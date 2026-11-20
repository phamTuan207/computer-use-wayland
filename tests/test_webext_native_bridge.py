"""Tests for the WebExtension native messaging bridge. No browser needed.

Run directly: python3 tests/test_webext_native_bridge.py
(Explicit-run convention, like tests/test_zen_cli.py.)

A fake extension stands in for Firefox/Zen: it speaks the same framed
native messaging protocol on the host's stdin/stdout, and a TCP client
stands in for the agent. This proves the host framing, the relay, the
1 MB outbound limit, and bad-input survival. It does NOT prove that
Firefox or Zen accepts the extension, which is only verifiable on the
laptop with a real browser (see README.md in this folder, section
"Verification status").
"""

import json
import os
import socket
import struct
import subprocess
import sys
import threading
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "tests" / "webext-native-bridge"
HOST = BRIDGE / "host" / "cu_bridge_host.py"

sys.path.insert(0, str(BRIDGE / "host"))
import cu_bridge_host  # noqa: E402


def free_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def tcp_request(port, request, timeout=10.0):
    started = time.monotonic()
    with socket.create_connection(("127.0.0.1", port), timeout=timeout) as sock:
        sock.sendall((json.dumps(request) + "\n").encode("utf-8"))
        data = b""
        while not data.endswith(b"\n"):
            chunk = sock.recv(65536)
            if not chunk:
                break
            data += chunk
    elapsed_ms = (time.monotonic() - started) * 1000
    return json.loads(data.decode("utf-8")), elapsed_ms


class FakeExtension(threading.Thread):
    """Acts as the browser side of the native messaging channel."""

    def __init__(self, out_stream, in_stream):
        super().__init__(daemon=True)
        self.out_stream = out_stream  # host stdout: frames host sends us
        self.in_stream = in_stream  # host stdin: frames we send the host
        self.received = []
        self.write_lock = threading.Lock()
        self.stop = threading.Event()

    def run(self):
        try:
            while not self.stop.is_set():
                message = cu_bridge_host.read_message(self.out_stream)
                if message is None:
                    break
                if not isinstance(message, dict):
                    continue
                if "ok" in message:
                    continue  # reply to the background's own ping, ignore
                self.received.append(message)
                reply = {
                    "id": message.get("id"),
                    "ok": True,
                    "result": {"echo_op": message.get("op")},
                    "elapsed_ms": 1,
                }
                with self.write_lock:
                    self.in_stream.write(cu_bridge_host.encode_message(reply))
                    self.in_stream.flush()
        except (OSError, ValueError, EOFError):
            pass

    def send_raw(self, raw_bytes):
        with self.write_lock:
            self.in_stream.write(raw_bytes)
            self.in_stream.flush()


class BridgeTestCase(unittest.TestCase):
    def setUp(self):
        self.port = free_port()
        env = dict(os.environ)
        env["CU_BRIDGE_PORT"] = str(self.port)
        env["CU_BRIDGE_TIMEOUT_S"] = "5"
        self.proc = subprocess.Popen(
            [sys.executable, str(HOST)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        self.stderr_lines = []
        self.stderr_thread = threading.Thread(target=self._drain_stderr, daemon=True)
        self.stderr_thread.start()
        self.fake = FakeExtension(self.proc.stdout, self.proc.stdin)
        self.fake.start()
        self._wait_for_listening()

    def _drain_stderr(self):
        try:
            for line in self.proc.stderr:
                self.stderr_lines.append(line.decode("utf-8", "replace"))
        except (OSError, ValueError):
            pass

    def _wait_for_listening(self, timeout=10.0):
        deadline = time.monotonic() + timeout
        needle = f"listening on 127.0.0.1:{self.port}"
        while time.monotonic() < deadline:
            if any(needle in line for line in self.stderr_lines):
                return
            if self.proc.poll() is not None:
                break
            time.sleep(0.05)
        self.assertTrue(
            any(needle in line for line in self.stderr_lines),
            f"host did not start listening; stderr={self.stderr_lines}",
        )

    def tearDown(self):
        self.fake.stop.set()
        if self.proc.poll() is None:
            try:
                self.proc.stdin.close()
            except (BrokenPipeError, OSError):
                pass
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=5)
        for stream in (self.proc.stdout, self.proc.stderr):
            try:
                stream.close()
            except (OSError, ValueError):
                pass

    def test_full_relay_agent_to_fake_extension(self):
        started_wall = time.time()
        reply, elapsed_ms = tcp_request(
            self.port, {"id": 7, "op": "snapshot", "tabId": 3}
        )
        self.assertTrue(reply["ok"], reply)
        self.assertEqual(reply["id"], 7)
        self.assertEqual(reply["result"]["echo_op"], "snapshot")
        self.assertIn("host_elapsed_ms", reply)
        self.assertGreaterEqual(elapsed_ms, 0)
        self.assertLess(elapsed_ms, 5000)
        forwarded = [m for m in self.fake.received if m.get("id") == 7]
        self.assertEqual(len(forwarded), 1)
        self.assertEqual(forwarded[0]["op"], "snapshot")
        self.assertEqual(forwarded[0]["tabId"], 3)
        wall = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started_wall))
        print(f"\nrelay wall-clock: {wall} elapsed_ms: {elapsed_ms:.1f}")

    def test_host_ping_answered_locally(self):
        before = len(self.fake.received)
        reply, _elapsed = tcp_request(self.port, {"id": 8, "op": "host.ping"})
        self.assertTrue(reply["ok"], reply)
        self.assertTrue(reply["result"]["pong"])
        self.assertEqual(len(self.fake.received), before)

    def test_host_status_answered_locally(self):
        reply, _elapsed = tcp_request(self.port, {"id": 9, "op": "host.status"})
        self.assertTrue(reply["ok"], reply)
        self.assertEqual(reply["result"]["host"], "computer_use_bridge")

    def test_oversize_request_rejected_without_forwarding(self):
        before = len(self.fake.received)
        big_text = "x" * (2 * 1024 * 1024)
        reply, _elapsed = tcp_request(
            self.port, {"id": 10, "op": "type", "tabId": 1, "text": big_text}
        )
        self.assertFalse(reply["ok"], reply)
        self.assertIn("too large", reply["error"])
        self.assertEqual(len(self.fake.received), before)

    def test_bad_frame_from_browser_survived(self):
        self.fake.send_raw(struct.pack("<I", 5) + b"notjs")
        time.sleep(0.3)
        reply, _elapsed = tcp_request(self.port, {"id": 11, "op": "host.ping"})
        self.assertTrue(reply["ok"], reply)

    def test_request_without_id_rejected(self):
        reply, _elapsed = tcp_request(self.port, {"op": "host.ping"})
        self.assertFalse(reply["ok"], reply)

    def test_manifests_valid(self):
        ext_manifest = json.loads((BRIDGE / "extension" / "manifest.json").read_text())
        self.assertEqual(ext_manifest["manifest_version"], 2)
        self.assertIn("nativeMessaging", ext_manifest["permissions"])
        self.assertEqual(
            ext_manifest["browser_specific_settings"]["gecko"]["id"],
            "cu-bridge@example.local",
        )
        self.assertIn("background.js", ext_manifest["background"]["scripts"])
        template = json.loads(
            (BRIDGE / "host" / "computer_use_bridge.json.template").read_text()
        )
        self.assertEqual(template["name"], "computer_use_bridge")
        self.assertEqual(template["type"], "stdio")
        self.assertEqual(template["allowed_extensions"], ["cu-bridge@example.local"])

    def test_no_long_dashes_or_forbidden_text(self):
        for path in sorted(BRIDGE.rglob("*")):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            self.assertNotIn("\u2014", text, f"em dash in {path}")
            self.assertNotIn("\u2013", text, f"en dash in {path}")

    def test_host_exits_when_browser_closes_stdin(self):
        env = dict(os.environ)
        env["CU_BRIDGE_PORT"] = str(free_port())
        proc = subprocess.Popen(
            [sys.executable, str(HOST)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        try:
            proc.stdin.close()
            code = proc.wait(timeout=5)
            self.assertEqual(code, 0)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait(timeout=5)
            for stream in (proc.stdout, proc.stderr):
                try:
                    stream.close()
                except (OSError, ValueError):
                    pass


if __name__ == "__main__":
    unittest.main(verbosity=2)
