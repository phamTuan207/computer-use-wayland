"""Repo-owned Zen CLI wrapper; non-live, no Zen needed.

Run directly: python3 tests/test_zen_cli.py
(Not picked up by `python3 -m unittest discover -s tests -p 'test_*.py'`
discovery of live tests; it follows the repo's explicit-run convention
for wrapper tests instead.)

Covers, against a fake HOME and a fake BiDi server on loopback:
- --help advertises --json (the cli-anything runner probes for it);
- status / session stop with no session recorded;
- tabs / open / history fail clearly with no session or bad input;
- session start refuses a profile inside ~/.config/zen;
- history recent + search against a fixture places.sqlite;
- tabs / current / page / close against a fake BiDi server that
  answers session.new, getTree, script.evaluate, navigate, activate,
  close and session.end with canned JSON.

The fake server speaks the same minimal WebSocket framing as the
wrapper: HTTP upgrade, masked client frames, unmasked server frames.
It proves the stdlib WebSocket client and the BiDi call loop work;
it does not prove Zen answers, which the live test on the laptop does.
"""
import base64
import hashlib
import json
import os
import socket
import sqlite3
import struct
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "scripts" / "zen_cli.py"

WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def read_exact(reader, count):
    """Read exactly count bytes from a buffered reader."""
    data = reader.read(count)
    if data is None or len(data) < count:
        raise RuntimeError("short read")
    return data


class FakeBidiServer:
    """A canned WebDriver BiDi server on an ephemeral loopback port."""

    def __init__(self, contexts, title="Fake Title"):
        self.contexts = contexts
        self.title = title
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", 0))
        self.port = self.sock.getsockname()[1]
        self.sock.listen(5)
        self.sock.settimeout(10)
        self.thread = None
        self.calls = []
        self.stop_event = threading.Event()

    def __enter__(self):
        self.thread = threading.Thread(target=self._serve, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.stop_event.set()
        try:
            self.sock.close()
        except OSError:
            pass
        return False

    def _send_frame(self, conn, payload):
        data = payload.encode("utf-8")
        header = bytearray([0x81])
        if len(data) < 126:
            header.append(len(data))
        elif len(data) < 65536:
            header.append(126)
            header.extend(struct.pack(">H", len(data)))
        else:
            header.append(127)
            header.extend(struct.pack(">Q", len(data)))
        conn.sendall(bytes(header) + data)

    def _recv_frame(self, reader):
        first = read_exact(reader, 2)
        opcode = first[0] & 0x0F
        length = first[1] & 0x7F
        if length == 126:
            length = struct.unpack(">H", read_exact(reader, 2))[0]
        elif length == 127:
            length = struct.unpack(">Q", read_exact(reader, 8))[0]
        mask = read_exact(reader, 4) if first[1] & 0x80 else None
        payload = read_exact(reader, length) if length else b""
        if mask is not None:
            payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        return opcode, payload

    def _reply(self, conn, call_id, result):
        self._send_frame(conn, json.dumps(
            {"id": call_id, "type": "success", "result": result}))

    def _serve(self):
        """Accept sequential connections until stopped."""
        while not self.stop_event.is_set():
            try:
                conn, _ = self.sock.accept()
            except socket.timeout:
                continue
            except OSError:
                return
            self._handle(conn)

    def _handle(self, conn):
        try:
            conn.settimeout(10)
            reader = conn.makefile("rb")
            request = b""
            while b"\r\n\r\n" not in request:
                chunk = conn.recv(4096)
                if not chunk:
                    return
                request += chunk
            key = None
            for line in request.decode("latin-1").split("\r\n"):
                if line.lower().startswith("sec-websocket-key:"):
                    key = line.split(":", 1)[1].strip()
            accept = base64.b64encode(hashlib.sha1(
                (key + WS_GUID).encode("ascii")).digest()).decode("ascii")
            conn.sendall((
                "HTTP/1.1 101 Switching Protocols\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                "Sec-WebSocket-Accept: %s\r\n\r\n" % accept).encode("ascii"))
            while True:
                try:
                    opcode, payload = self._recv_frame(reader)
                except (RuntimeError, OSError):
                    return
                if opcode == 0x8:
                    return
                if opcode != 0x1:
                    continue
                try:
                    message = json.loads(payload.decode("utf-8"))
                except json.JSONDecodeError:
                    continue
                self.calls.append(message.get("method"))
                method = message.get("method")
                call_id = message.get("id")
                params = message.get("params", {})
                if method == "session.new":
                    self._reply(conn, call_id, {
                        "sessionId": "fake-session",
                        "capabilities": {
                            "browserName": "zen",
                            "browserVersion": "1.24.2b",
                            "moz:profile": "/tmp/fake-zen-profile"}})
                elif method == "session.end":
                    self._reply(conn, call_id, {})
                elif method == "browsingContext.getTree":
                    self._reply(conn, call_id, {
                        "contexts": self.contexts})
                elif method == "script.evaluate":
                    expression = params.get("expression", "")
                    if "window.open" in expression:
                        result = {"type": "string", "value": "opened"}
                    elif "document.body" in expression:
                        result = {"type": "object", "value": [
                            ["title", {"type": "string",
                                      "value": self.title}],
                            ["url", {"type": "string",
                                    "value": "https://example.com/"}],
                            ["text", {"type": "string",
                                     "value": "hello fake page"}]]}
                    else:
                        result = {"type": "string", "value": self.title}
                    self._reply(conn, call_id, {
                        "realm": "fake-realm", "type": "success",
                        "result": result})
                elif method in ("browsingContext.navigate",
                                "browsingContext.activate",
                                "browsingContext.close"):
                    self._reply(conn, call_id, {})
                else:
                    self._send_frame(conn, json.dumps(
                        {"id": call_id, "type": "error",
                         "error": "unknown command",
                         "message": method}))
        finally:
            try:
                conn.close()
            except OSError:
                pass


def two_contexts():
    """Two top-level contexts: a blank tab and example.com."""
    return [
        {"context": "ctx-blank", "url": "about:blank",
         "originalOpener": None, "parent": None},
        {"context": "ctx-page", "url": "https://example.com/",
         "originalOpener": None, "parent": None},
    ]


class ZenCliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name) / "home"
        self.home.mkdir()
        self.env = dict(os.environ)
        self.env["HOME"] = str(self.home)
        self.env["PATH"] = os.environ.get("PATH", "")

    def unused_loopback_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return sock.getsockname()[1]

    def tearDown(self):
        self.tmp.cleanup()

    def run_wrapper(self, *args, extra_path=None):
        """Run the wrapper with the fake HOME; return (code, parsed)."""
        env = dict(self.env)
        if extra_path:
            env["PATH"] = extra_path + os.pathsep + env["PATH"]
        result = subprocess.run(
            [sys.executable, str(WRAPPER), *args],
            capture_output=True, text=True, timeout=30, env=env)
        try:
            parsed = json.loads(result.stdout)
        except json.JSONDecodeError:
            parsed = None
        return result.returncode, result.stdout, parsed

    def write_state(self, **fields):
        """Write a fake dedicated-session state file."""
        state_dir = self.home / ".local" / "share" / "agent-computer-use"
        state_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        payload = {"port": 9222, "profile": "/tmp/fake-zen-profile",
                   "pid": 12345, "ws_url": "ws://127.0.0.1:9222/session"}
        payload.update(fields)
        (state_dir / "zen-cli-state.json").write_text(json.dumps(payload))

    def make_profile(self, visits):
        """A fixture real profile with places.sqlite + profiles.ini."""
        profile_dir = self.home / ".config" / "zen" / "abc.default-release"
        profile_dir.mkdir(parents=True)
        db_path = profile_dir / "places.sqlite"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE moz_places (id INTEGER PRIMARY KEY,"
                     " url TEXT, title TEXT, visit_count INTEGER)")
        conn.execute("CREATE TABLE moz_historyvisits (id INTEGER PRIMARY"
                     " KEY, place_id INTEGER, visit_date INTEGER)")
        for index, (url, title, count, date) in enumerate(visits, start=1):
            conn.execute("INSERT INTO moz_places VALUES (?, ?, ?, ?)",
                         (index, url, title, count))
            conn.execute("INSERT INTO moz_historyvisits VALUES (?, ?, ?)",
                         (index, index, date))
        conn.commit()
        conn.close()
        (self.home / ".config" / "zen" / "profiles.ini").write_text(
            "[Profile0]\nName=Default\nDefault=1\n"
            "Path=abc.default-release\n")
        return profile_dir

    def test_help_mentions_json(self):
        code, out, _ = self.run_wrapper("--help")
        self.assertEqual(code, 0)
        self.assertIn("--json", out)

    def test_status_no_session(self):
        port = self.unused_loopback_port()
        code, _, parsed = self.run_wrapper("--port", str(port), "status")
        self.assertEqual(code, 0)
        self.assertTrue(parsed["ok"])
        self.assertFalse(parsed["session_up"])
        self.assertEqual(parsed["port"], port)

    def test_session_stop_no_state(self):
        code, _, parsed = self.run_wrapper("session", "stop")
        self.assertEqual(code, 0)
        self.assertTrue(parsed["ok"])
        self.assertFalse(parsed["running"])

    def test_tabs_no_session(self):
        port = self.unused_loopback_port()
        code, _, parsed = self.run_wrapper("--port", str(port), "tabs")
        self.assertEqual(code, 1)
        self.assertFalse(parsed["ok"])
        self.assertIn("session start", parsed["error"])

    def test_open_rejects_non_http(self):
        code, _, parsed = self.run_wrapper("open", "ftp://example.com")
        self.assertEqual(code, 1)
        self.assertIn("http(s)", parsed["error"])

    def test_history_no_profile(self):
        code, _, parsed = self.run_wrapper("history")
        self.assertEqual(code, 1)
        self.assertIn("no Zen profile", parsed["error"])

    def test_session_start_refuses_real_profile(self):
        bindir = Path(self.tmp.name) / "bin"
        bindir.mkdir()
        stub = bindir / "zen-browser"
        stub.write_text("#!/bin/sh\nexit 0\n")
        stub.chmod(0o755)
        real = self.home / ".config" / "zen" / "evil.default-release"
        real.mkdir(parents=True)
        code, _, parsed = self.run_wrapper(
            "session", "start", "--profile", str(real),
            extra_path=str(bindir))
        self.assertEqual(code, 1)
        self.assertIn("refusing profile", parsed["error"])

    def test_history_recent_and_search(self):
        self.make_profile([
            ("https://github.com/a", "GitHub A", 5, 1795000000000000),
            ("https://example.com/", "Example Domain", 2, 1794000000000000),
            ("https://github.com/b", "GitHub B", 3, 1793000000000000),
        ])
        code, _, parsed = self.run_wrapper("history", "--limit", "2")
        self.assertEqual(code, 0)
        self.assertTrue(parsed["ok"])
        self.assertEqual(len(parsed["visits"]), 2)
        self.assertEqual(parsed["visits"][0]["url"], "https://github.com/a")
        self.assertEqual(parsed["visits"][0]["visit_count"], 5)
        code, _, parsed = self.run_wrapper("history", "github")
        self.assertEqual(code, 0)
        self.assertEqual(len(parsed["visits"]), 2)
        self.assertTrue(all("github" in v["url"]
                            for v in parsed["visits"]))
        code, _, parsed = self.run_wrapper("history", "zzz-no-match")
        self.assertEqual(code, 0)
        self.assertEqual(parsed["visits"], [])

    def test_status_via_fake_bidi(self):
        with FakeBidiServer(two_contexts()) as server:
            code, _, parsed = self.run_wrapper(
                "--port", str(server.port), "status")
        self.assertEqual(code, 0)
        self.assertTrue(parsed["ok"])
        self.assertTrue(parsed["session_up"])
        self.assertEqual(parsed["browser"], "zen")
        self.assertEqual(parsed["browser_version"], "1.24.2b")
        self.assertEqual(parsed["session_profile"], "/tmp/fake-zen-profile")

    def test_history_prefers_install_default_over_decoy_default1(self):
        """Regression: on the laptop the Install default and the
        Default=1 profile disagree, and the Default=1 one has no
        places.sqlite. History must use the Install default."""
        real = self.make_profile([
            ("https://example.com/", "Example Domain", 2, 1794000000000000),
        ])
        decoy = self.home / ".config" / "zen" / "decoy-profile.Default Profile"
        decoy.mkdir(parents=True)
        # The fixture profile dir is named abc.default-release, so point
        # the ini at the real fixture dir, with a decoy Default=1 profile
        # that has no places.sqlite, mirroring the laptop layout.
        (self.home / ".config" / "zen" / "profiles.ini").write_text(
            "[Profile0]\nName=Default (release)\nIsRelative=1\n"
            "Path=%s\n\n"
            "[Install15B76BAA26BA15E7]\n"
            "Default=%s\nLocked=1\n\n"
            "[Profile1]\nName=Default Profile\nIsRelative=1\n"
            "Path=decoy-profile.Default Profile\nDefault=1\n"
            % (real.name, real.name))
        code, _, parsed = self.run_wrapper("history", "--limit", "5")
        self.assertEqual(code, 0)
        self.assertTrue(parsed["ok"])
        self.assertEqual(parsed["profile"], str(real))
        self.assertEqual(len(parsed["visits"]), 1)
        self.assertEqual(parsed["visits"][0]["url"], "https://example.com/")

    def test_tabs_via_fake_bidi(self):
        with FakeBidiServer(two_contexts()) as server:
            code, _, parsed = self.run_wrapper(
                "--port", str(server.port), "tabs")
        self.assertEqual(code, 0)
        self.assertTrue(parsed["ok"])
        self.assertEqual(len(parsed["tabs"]), 2)
        page = next(t for t in parsed["tabs"] if t["index"] == 1)
        self.assertEqual(page["url"], "https://example.com/")
        self.assertEqual(page["title"], "Fake Title")
        self.assertNotIn("context", parsed["tabs"][0],
                         "tabs must not expose BiDi context ids: they "
                         "change on every new BiDi session")
        self.assertIn("browsingContext.getTree", server.calls)
        self.assertIn("script.evaluate", server.calls)

    def test_tab_index_rejects_context_id(self):
        with FakeBidiServer(two_contexts()) as server:
            code, _, parsed = self.run_wrapper(
                "--port", str(server.port), "close", "ctx-page")
        self.assertEqual(code, 1)
        self.assertIn("index from `tabs`", parsed["error"])

    def test_page_and_current_via_fake_bidi(self):
        with FakeBidiServer(two_contexts()) as server:
            code, _, parsed = self.run_wrapper(
                "--port", str(server.port), "page", "--tab", "1")
            self.assertEqual(code, 0)
            self.assertEqual(parsed["title"], "Fake Title")
            self.assertEqual(parsed["url"], "https://example.com/")
            self.assertEqual(parsed["text"], "hello fake page")
            code, _, parsed = self.run_wrapper(
                "--port", str(server.port), "current")
            self.assertEqual(code, 0)
            self.assertFalse(parsed["tracked"])
            self.assertEqual(parsed["tab"]["index"], 1)
        self.write_state(port=9222, tab_index=1,
                         tab_url="https://example.com/")
        with FakeBidiServer(two_contexts()) as server:
            code, _, parsed = self.run_wrapper(
                "--port", str(server.port), "current")
            self.assertEqual(code, 0)
            self.assertTrue(parsed["tracked"])
            self.assertEqual(parsed["tab"]["index"], 1)

    def test_close_last_tab_refused(self):
        one = [dict(two_contexts()[1])]
        with FakeBidiServer(one) as server:
            code, _, parsed = self.run_wrapper(
                "--port", str(server.port), "close", "0")
        self.assertEqual(code, 1)
        self.assertIn("last remaining tab", parsed["error"])
        self.assertNotIn("browsingContext.close", server.calls)

    def test_close_one_of_two_via_fake_bidi(self):
        with FakeBidiServer(two_contexts()) as server:
            code, _, parsed = self.run_wrapper(
                "--port", str(server.port), "close", "0")
        self.assertEqual(code, 0)
        self.assertTrue(parsed["ok"])
        self.assertEqual(parsed["index"], 0)
        self.assertIn("browsingContext.close", server.calls)


if __name__ == "__main__":
    unittest.main()
