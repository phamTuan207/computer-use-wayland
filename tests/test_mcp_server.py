#!/usr/bin/env python3
"""Tests for scripts/mcp_server.py.

A minimal stdio JSON-RPC client spawns the real server process and
speaks MCP to it. No MCP client library is installed on this machine
(no `mcp` Python package, no MCP client binary), so this client is
the test harness, and the README says so.

Two server modes are tested:
- --fake: in-memory backend, full tool flow without a browser.
- real backend: session_start with no browser present must fail
  cleanly and fast, never hang and never claim success.

Each test prints one JSON line with wall-clock time and elapsed ms.
Run: python3 tests/test_mcp_server.py
"""
import base64
import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVER = ROOT / "scripts" / "mcp_server.py"


class JsonRpcClient:
    """Minimal newline delimited JSON-RPC client over stdio."""

    def __init__(self, argv, timeout_s=20):
        self.timeout_s = timeout_s
        self.stderr_file = tempfile.TemporaryFile(mode="w+")
        self.proc = subprocess.Popen(
            argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=self.stderr_file, text=True, bufsize=1)
        self.next_id = 1

    def send(self, message):
        self.proc.stdin.write(json.dumps(message) + "\n")
        self.proc.stdin.flush()

    def recv(self):
        import select
        ready, _, _ = select.select([self.proc.stdout], [],
                                    [], self.timeout_s)
        if not ready:
            raise TimeoutError("no MCP response within %ss"
                               % self.timeout_s)
        line = self.proc.stdout.readline()
        if not line:
            raise EOFError("server closed stdio")
        return json.loads(line)

    def request(self, method, params=None):
        ident = self.next_id
        self.next_id += 1
        message = {"jsonrpc": "2.0", "id": ident, "method": method}
        if params is not None:
            message["params"] = params
        self.send(message)
        reply = self.recv()
        assert reply.get("id") == ident, reply
        return reply

    def notify(self, method, params=None):
        message = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            message["params"] = params
        self.send(message)

    def call_tool(self, name, args):
        reply = self.request("tools/call",
                             {"name": name, "arguments": args})
        assert "error" not in reply, reply
        return reply["result"]

    def close(self):
        try:
            if self.proc.stdin and not self.proc.stdin.closed:
                self.proc.stdin.close()
        except BrokenPipeError:
            pass
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait()
        self.stderr_file.close()


def log_line(test, monotonic_started, **fields):
    elapsed_s = time.monotonic() - monotonic_started
    end_wall = time.time()
    record = {"test": test,
              "wall_clock_start": time.strftime(
                  "%Y-%m-%dT%H:%M:%SZ", time.gmtime(end_wall - elapsed_s)),
              "wall_clock_end": time.strftime(
                  "%Y-%m-%dT%H:%M:%SZ", time.gmtime(end_wall)),
              "elapsed_ms": round(elapsed_s * 1000, 1)}
    record.update(fields)
    print(json.dumps(record), flush=True)


class FakeBackendTest(unittest.TestCase):
    def setUp(self):
        self.client = JsonRpcClient(
            [sys.executable, str(SERVER), "--fake"])
        self.started = time.monotonic()
        reply = self.client.request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "0.1.0"}})
        self.assertEqual(reply["result"]["serverInfo"]["name"],
                         "computer-use-mcp")
        self.client.notify("notifications/initialized")

    def tearDown(self):
        self.client.close()

    def test_ping(self):
        reply = self.client.request("ping")
        self.assertEqual(reply["result"], {})
        log_line("ping", self.started)

    def test_tools_list(self):
        reply = self.client.request("tools/list")
        names = [t["name"] for t in reply["result"]["tools"]]
        self.assertEqual(names, [
            "session_start", "session_status", "session_finish",
            "locate", "click", "type", "screenshot", "overlay"])
        for tool in reply["result"]["tools"]:
            self.assertIn("description", tool)
            self.assertIn("inputSchema", tool)
        log_line("tools_list", self.started, tools=len(names))

    def test_session_lifecycle(self):
        result = self.client.call_tool("session_start", {})
        self.assertTrue(result["content"][0]["text"])
        body = json.loads(result["content"][0]["text"])
        self.assertTrue(body["ok"])
        self.assertEqual(body["session_id"], "fake-1")
        status = json.loads(self.client.call_tool(
            "session_status", {})["content"][0]["text"])
        self.assertTrue(status["session_active"])
        again = self.client.call_tool("session_start", {})
        self.assertTrue(again.get("isError"))
        done = json.loads(self.client.call_tool(
            "session_finish", {})["content"][0]["text"])
        self.assertTrue(done["ok"])
        status = json.loads(self.client.call_tool(
            "session_status", {})["content"][0]["text"])
        self.assertFalse(status["session_active"])
        twice = json.loads(self.client.call_tool(
            "session_finish", {})["content"][0]["text"])
        self.assertTrue(twice.get("already_finished"))
        log_line("session_lifecycle", self.started)

    def test_locate_found_and_missing(self):
        self.client.call_tool("session_start", {})
        found = json.loads(self.client.call_tool(
            "locate", {"selector": "#count-btn"})["content"][0]["text"])
        self.assertTrue(found["ok"])
        self.assertEqual(found["rect"]["center_x"], 140)
        self.assertEqual(found["rect"]["center_y"], 65)
        missing = self.client.call_tool(
            "locate", {"selector": "#nope"})
        self.assertTrue(missing.get("isError"))
        log_line("locate", self.started)

    def test_click_increments_counter(self):
        self.client.call_tool("session_start", {})
        first = json.loads(self.client.call_tool(
            "click", {"selector": "#count-btn"})["content"][0]["text"])
        self.assertTrue(first["ok"])
        self.assertEqual(first["counter"], 1)
        self.assertEqual(first["clicked_at"], {"x": 140, "y": 65})
        second = json.loads(self.client.call_tool(
            "click", {"selector": "#count-btn"})["content"][0]["text"])
        self.assertEqual(second["counter"], 2)
        log_line("click", self.started, counter=2)

    def test_type_sets_value(self):
        self.client.call_tool("session_start", {})
        result = json.loads(self.client.call_tool(
            "type", {"selector": "#name", "text": "Ada"})["content"][0]["text"])
        self.assertTrue(result["ok"])
        self.assertEqual(result["before"], "")
        self.assertEqual(result["after"], "Ada")
        log_line("type", self.started)

    def test_screenshot_is_png(self):
        self.client.call_tool("session_start", {})
        result = self.client.call_tool("screenshot", {})
        self.assertFalse(result.get("isError"))
        images = [c for c in result["content"] if c["type"] == "image"]
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]["mimeType"], "image/png")
        raw = base64.b64decode(images[0]["data"])
        self.assertTrue(raw.startswith(b"\x89PNG"))
        log_line("screenshot", self.started, image_bytes=len(raw))

    def test_overlay_acquire_release(self):
        self.client.call_tool("session_start", {})
        acquired = json.loads(self.client.call_tool(
            "overlay", {"action": "acquire", "agent": "test",
                        "method": "mcp"})["content"][0]["text"])
        self.assertTrue(acquired["ok"])
        self.assertIn("test", acquired["holders"])
        status = json.loads(self.client.call_tool(
            "overlay", {"action": "status"})["content"][0]["text"])
        self.assertIn("test", status["holders"])
        released = json.loads(self.client.call_tool(
            "overlay", {"action": "release", "agent": "test",
                        "method": "mcp"})["content"][0]["text"])
        self.assertTrue(released["was_present"])
        self.assertNotIn("test", released["holders"])
        log_line("overlay", self.started)

    def test_no_session_errors(self):
        result = self.client.call_tool(
            "locate", {"selector": "#count-btn"})
        self.assertTrue(result.get("isError"))
        body = json.loads(result["content"][0]["text"])
        self.assertIn("no live session", body["error"])
        log_line("no_session_error", self.started)

    def test_bad_arguments(self):
        self.client.call_tool("session_start", {})
        no_selector = self.client.call_tool("click", {})
        self.assertTrue(no_selector.get("isError"))
        no_text = self.client.call_tool(
            "type", {"selector": "#name"})
        self.assertTrue(no_text.get("isError"))
        bad_action = self.client.call_tool(
            "overlay", {"action": "explode"})
        self.assertTrue(bad_action.get("isError"))
        unknown = self.client.call_tool("teleport", {})
        self.assertTrue(unknown.get("isError"))
        log_line("bad_arguments", self.started)

    def test_unknown_method(self):
        reply = self.client.request("resources/list")
        self.assertIn("error", reply)
        self.assertEqual(reply["error"]["code"], -32601)
        log_line("unknown_method", self.started)


class RealBackendNoBrowserTest(unittest.TestCase):
    def test_session_start_fails_clean_without_browser(self):
        started = time.monotonic()
        client = JsonRpcClient([sys.executable, str(SERVER)],
                               timeout_s=30)
        try:
            client.request("initialize", {
                "protocolVersion": "2024-11-05", "capabilities": {},
                "clientInfo": {"name": "test-client",
                               "version": "0.1.0"}})
            client.notify("notifications/initialized")
            result = client.call_tool(
                "session_start", {"timeout_s": 2})
            self.assertTrue(result.get("isError"))
            body = json.loads(result["content"][0]["text"])
            self.assertIn("could not start Zen session", body["error"])
        finally:
            client.close()
        elapsed = time.monotonic() - started
        self.assertLess(elapsed, 20,
                        "session_start must fail fast, not hang")
        log_line("real_backend_no_browser", started,
                 elapsed_s=round(elapsed, 2))


if __name__ == "__main__":
    unittest.main(verbosity=2)
