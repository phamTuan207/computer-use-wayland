"""Chromium wrapper tests; non-live, no real browser, no network.

Run with unittest discover: python3 -m unittest discover -s tests -p 'test_*.py'
or directly: python3 tests/test_chromium_cli.py

Tab commands run against an in-process stub CDP HTTP server (threaded,
loopback only) that implements /json/version, /json/list, /json/new,
/json/activate and /json/close. Profile commands run against a synthetic
Chromium profile built in a temp dir (History sqlite with urls and
downloads tables, Bookmarks JSON). The wrapper state file is redirected
to a temp path, so no real HOME state is touched.

What is NOT tested here: a real Chromium. That is the laptop live test
(see improvements/speed-cli-chromium.md), which runs the same commands
against the agent-managed Chromium on the laptop.
"""
import contextlib
import datetime
import io
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
from unittest import mock
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import chromium_cli  # noqa: E402


def chrome_epoch(moment):
    """datetime (UTC) to Chrome epoch microseconds since 1601-01-01."""
    base = datetime.datetime(1601, 1, 1, tzinfo=datetime.timezone.utc)
    delta = moment - base
    return int(delta.total_seconds() * 1_000_000)


class StubCdpHandler(BaseHTTPRequestHandler):
    """Minimal CDP HTTP surface with mutable tab state."""
    tabs = []
    protocol = "HTTP/1.1"

    def log_message(self, *args):
        pass

    def _send_json(self, payload, code=200):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_empty(self, code=200):
        # Real Chromium answers /json/activate and /json/close with an
        # empty 200 body, not JSON. The stub does the same, so the
        # wrapper must treat an empty 2xx as success.
        self.send_response(code)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        if self.path == "/json/version":
            self._send_json({"Browser": "Chromium/157.0.8103.38",
                             "Protocol-Version": "1.3",
                             "webSocketDebuggerUrl":
                                 "ws://127.0.0.1/devtools/browser/stub"})
            return
        if self.path == "/json/list":
            self._send_json(list(type(self).tabs))
            return
        parts = self.path.strip("/").split("/")
        if len(parts) == 3 and parts[0] == "json" and parts[1] in (
                "activate", "close"):
            tab_id = parts[2]
            known = [t for t in type(self).tabs if t["id"] == tab_id]
            if not known:
                self._send_json({"error": "no such target"}, code=404)
                return
            if parts[1] == "close":
                type(self).tabs = [t for t in type(self).tabs
                                   if t["id"] != tab_id]
            self._send_empty()
            return
        self._send_json({"error": "not found"}, code=404)

    def do_PUT(self):
        parsed = urlparse(self.path)
        if parsed.path == "/json/new":
            url = parse_qs(parsed.query).get("url", [""])[0]
            tab = {"id": "NEW1", "title": "", "url": url, "type": "page",
                   "webSocketDebuggerUrl": "ws://127.0.0.1/devtools/page/NEW1"}
            type(self).tabs.append(tab)
            self._send_json(tab)
            return
        self._send_json({"error": "not found"}, code=404)


class ChromiumCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), StubCdpHandler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever,
                                      daemon=True)
        cls.thread.start()
        cls.endpoint = "http://127.0.0.1:%d" % cls.port

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        # Fixture opt-out for the pill gate (W-PILLCDP): the stub server
        # runs on this machine with no compositor, so the write-command
        # tests run with the gate off. The dedicated pill tests below
        # re-enable it with patch.dict and a mocked hold.
        self._orig_pill = os.environ.get("CU_CDP_PILL")
        os.environ["CU_CDP_PILL"] = "0"
        StubCdpHandler.tabs = [
            {"id": "AAA", "title": "First Tab",
             "url": "https://example.com/one", "type": "page"},
            {"id": "BBB", "title": "Second Tab",
             "url": "https://example.com/two", "type": "page"},
            {"id": "SW1", "title": "Worker",
             "url": "https://example.com/sw.js", "type": "service_worker"},
        ]
        self.tmp = Path(tempfile.mkdtemp(prefix="chromium-cli-test-"))
        self.state_path = self.tmp / "state.json"
        self._orig_state = chromium_cli.STATE_PATH
        chromium_cli.STATE_PATH = self.state_path

    def tearDown(self):
        chromium_cli.STATE_PATH = self._orig_state
        if self._orig_pill is None:
            os.environ.pop("CU_CDP_PILL", None)
        else:
            os.environ["CU_CDP_PILL"] = self._orig_pill
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_write_commands_hold_pill_read_commands_do_not(self):
        """W-PILLCDP: open/activate/close hold the pill, tabs/status do not."""
        holder = mock.MagicMock()
        with mock.patch.dict(os.environ, {"CU_CDP_PILL": ""}), \
                mock.patch.object(chromium_cli, "_pill_hold", holder), \
                mock.patch.object(chromium_cli, "navigate_tab_via_ws",
                                  return_value=None):
            code, opened = self.run_cli(
                ["--endpoint", self.endpoint, "open", "https://example.com"])
            self.assertEqual(code, 0)
            self.assertEqual(holder.call_count, 1)
            code, _ = self.run_cli(
                ["--endpoint", self.endpoint, "activate", "BBB"])
            self.assertEqual(code, 0)
            self.assertEqual(holder.call_count, 2)
            code, _ = self.run_cli(
                ["--endpoint", self.endpoint, "close", "BBB"])
            self.assertEqual(code, 0)
            self.assertEqual(holder.call_count, 3)
            code, _ = self.run_cli(["--endpoint", self.endpoint, "tabs"])
            self.assertEqual(code, 0)
            code, _ = self.run_cli(["--endpoint", self.endpoint, "status"])
            self.assertEqual(code, 0)
            self.assertEqual(holder.call_count, 3,
                             "read commands must not hold the pill")

    def test_pill_failure_refuses_open_before_any_tab_created(self):
        """W-PILLCDP, fail closed: a pill hold failure refuses the write
        before the tab is created."""
        @contextlib.contextmanager
        def _boom():
            raise RuntimeError("overlay daemon exited")
            yield

        with mock.patch.dict(os.environ, {"CU_CDP_PILL": ""}), \
                mock.patch.object(chromium_cli, "_pill_hold", _boom):
            code, out = self.run_cli(
                ["--endpoint", self.endpoint, "open", "https://example.com"])
        self.assertEqual(code, 1)
        self.assertFalse(out["ok"])
        self.assertIn("overlay daemon exited", out["error"])
        self.assertEqual([t["id"] for t in StubCdpHandler.tabs],
                         ["AAA", "BBB", "SW1"],
                         "refused open must not create a tab")

    def run_cli(self, argv):
        """Run main(argv) capturing stdout; returns (exit_code, parsed)."""
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = chromium_cli.main(argv)
        return code, json.loads(buf.getvalue())

    def make_profile(self, with_bookmarks=True, nested=False):
        """Synthetic profile dir with History and optional Bookmarks."""
        profile = self.tmp / "profile"
        target = profile / "Default" if nested else profile
        target.mkdir(parents=True)
        db_path = target / "History"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE urls (url TEXT, title TEXT,"
                     " visit_count INTEGER, last_visit_time INTEGER)")
        conn.execute("CREATE TABLE downloads (target_path TEXT,"
                     " tab_url TEXT, start_time INTEGER, state INTEGER,"
                     " total_bytes INTEGER, received_bytes INTEGER)")
        t_new = chrome_epoch(datetime.datetime(
            2026, 11, 18, 15, 23, tzinfo=datetime.timezone.utc))
        t_old = chrome_epoch(datetime.datetime(
            2026, 11, 4, 9, 0, tzinfo=datetime.timezone.utc))
        conn.execute("INSERT INTO urls VALUES (?,?,?,?)",
                     ("https://example.com/new", "New Page", 3, t_new))
        conn.execute("INSERT INTO urls VALUES (?,?,?,?)",
                     ("https://example.com/old", "Old Page", 1, t_old))
        conn.execute("INSERT INTO downloads VALUES (?,?,?,?,?,?)",
                     ("/home/testuser/Downloads/report.pdf",
                      "https://example.com/report.pdf", t_new, 1, 1234, 1234))
        conn.execute("INSERT INTO downloads VALUES (?,?,?,?,?,?)",
                     ("/home/testuser/Downloads/partial.bin",
                      "https://example.com/partial.bin", t_old, 0, 9999, 100))
        conn.commit()
        conn.close()
        if with_bookmarks:
            bookmarks = {
                "roots": {
                    "bookmark_bar": {
                        "type": "folder", "name": "Bookmarks bar",
                        "children": [
                            {"type": "url", "name": "Example",
                             "url": "https://example.com/",
                             "date_added": str(t_new)},
                            {"type": "folder", "name": "Work",
                             "children": [
                                 {"type": "url", "name": "Docs",
                                  "url": "https://example.com/docs",
                                  "date_added": str(t_old)}]}]},
                    "other": {"type": "folder", "name": "Other",
                              "children": []},
                    "synced": {"type": "folder", "name": "Mobile",
                               "children": []}}}
            (target / "Bookmarks").write_text(json.dumps(bookmarks))
        return profile

    def test_tabs_lists_only_pages(self):
        code, out = self.run_cli(["--endpoint", self.endpoint, "tabs"])
        self.assertEqual(code, 0)
        self.assertTrue(out["ok"])
        self.assertEqual([t["id"] for t in out["tabs"]], ["AAA", "BBB"])

    def test_open_activate_current_close_roundtrip(self):
        # The stub HTTP server speaks no WebSocket, so the navigate step
        # is faked here; the real WebSocket client is covered by
        # WsClientTests below, and by the laptop live test.
        calls = []

        def fake_navigate(tab, url):
            calls.append((tab["id"], url))
            return None

        with mock.patch.object(chromium_cli, "navigate_tab_via_ws",
                               side_effect=fake_navigate):
            code, opened = self.run_cli(
                ["--endpoint", self.endpoint, "open", "https://example.com"])
        self.assertEqual(code, 0)
        self.assertTrue(opened["ok"])
        self.assertEqual(opened["tab"]["id"], "NEW1")
        self.assertEqual(opened["tab"]["url"], "https://example.com")
        self.assertEqual(calls, [("NEW1", "https://example.com")])
        code, current = self.run_cli(["--endpoint", self.endpoint, "current"])
        self.assertEqual(code, 0)
        self.assertEqual(current["tab"]["id"], "NEW1")
        code, activated = self.run_cli(
            ["--endpoint", self.endpoint, "activate", "BBB"])
        self.assertEqual(code, 0)
        self.assertEqual(activated["tab"]["title"], "Second Tab")
        code, current = self.run_cli(["--endpoint", self.endpoint, "current"])
        self.assertEqual(current["tab"]["id"], "BBB")
        code, closed = self.run_cli(
            ["--endpoint", self.endpoint, "close", "BBB"])
        self.assertEqual(code, 0)
        self.assertTrue(closed["ok"])
        code, current = self.run_cli(["--endpoint", self.endpoint, "current"])
        self.assertEqual(code, 1)
        # Closing the tracked tab clears the state, so current reports
        # no tracked tab rather than a closed tab.
        self.assertIn("no tab tracked", current["error"])
        code, out = self.run_cli(["--endpoint", self.endpoint, "tabs"])
        self.assertEqual([t["id"] for t in out["tabs"]], ["AAA", "NEW1"])

    def test_current_with_no_tracked_tab_fails(self):
        code, out = self.run_cli(["--endpoint", self.endpoint, "current"])
        self.assertEqual(code, 1)
        self.assertIn("no tab tracked", out["error"])

    def test_open_fails_loudly_when_navigation_fails(self):
        def boom(tab, url):
            raise RuntimeError("CDP WebSocket closed")

        with mock.patch.object(chromium_cli, "navigate_tab_via_ws",
                               side_effect=boom):
            code, out = self.run_cli(
                ["--endpoint", self.endpoint, "open", "https://example.com"])
        self.assertEqual(code, 1)
        self.assertFalse(out["ok"])
        self.assertIn("navigation failed", out["error"])
        self.assertIn("NEW1", out["error"])

    def test_open_rejects_non_http_url(self):
        code, out = self.run_cli(
            ["--endpoint", self.endpoint, "open", "file:///etc/passwd"])
        self.assertEqual(code, 1)
        self.assertFalse(out["ok"])

    def test_endpoint_must_be_loopback(self):
        code, out = self.run_cli(
            ["--endpoint", "http://example.com:9222", "tabs"])
        self.assertEqual(code, 1)
        self.assertIn("loopback", out["error"])

    def test_status_unreachable_endpoint(self):
        code, out = self.run_cli(
            ["--endpoint", "http://127.0.0.1:1", "status"])
        self.assertEqual(code, 0)
        self.assertTrue(out["ok"])
        self.assertFalse(out["reachable"])

    def test_status_reachable_stub(self):
        code, out = self.run_cli(["--endpoint", self.endpoint, "status"])
        self.assertEqual(code, 0)
        self.assertTrue(out["reachable"])
        self.assertIn("Chromium", out["browser"])
        self.assertEqual(out["protocol_version"], "1.3")

    def test_history_reads_synthetic_profile_newest_first(self):
        profile = self.make_profile()
        code, out = self.run_cli(
            ["--profile", str(profile), "history", "--limit", "10"])
        self.assertEqual(code, 0)
        self.assertEqual(len(out["visits"]), 2)
        self.assertEqual(out["visits"][0]["url"], "https://example.com/new")
        self.assertEqual(out["visits"][0]["last_visit"],
                         "2026-11-18T15:23:00+00:00")
        self.assertEqual(out["visits"][0]["visit_count"], 3)
        self.assertEqual(out["visits"][1]["url"], "https://example.com/old")

    def test_history_resolves_user_data_dir_layout(self):
        profile = self.make_profile(nested=True)
        code, out = self.run_cli(["--profile", str(profile), "history"])
        self.assertEqual(code, 0)
        self.assertEqual(len(out["visits"]), 2)

    def test_history_missing_file_fails(self):
        code, out = self.run_cli(
            ["--profile", str(self.tmp / "empty"), "history"])
        self.assertEqual(code, 1)
        self.assertIn("no History file", out["error"])

    def test_bookmarks_flattens_folders(self):
        profile = self.make_profile()
        code, out = self.run_cli(["--profile", str(profile), "bookmarks"])
        self.assertEqual(code, 0)
        self.assertEqual(len(out["bookmarks"]), 2)
        by_name = {b["name"]: b for b in out["bookmarks"]}
        self.assertEqual(by_name["Example"]["folder"], "Bookmarks bar")
        self.assertEqual(by_name["Docs"]["folder"], "Work")
        self.assertEqual(by_name["Docs"]["url"], "https://example.com/docs")

    def test_bookmarks_missing_file_returns_empty_list(self):
        profile = self.make_profile(with_bookmarks=False)
        code, out = self.run_cli(["--profile", str(profile), "bookmarks"])
        self.assertEqual(code, 0)
        self.assertEqual(out["bookmarks"], [])
        self.assertIn("no Bookmarks file", out["note"])

    def test_downloads_states(self):
        profile = self.make_profile()
        code, out = self.run_cli(["--profile", str(profile), "downloads"])
        self.assertEqual(code, 0)
        self.assertEqual(len(out["downloads"]), 2)
        self.assertEqual(out["downloads"][0]["state"], "complete")
        self.assertEqual(out["downloads"][0]["total_bytes"], 1234)
        self.assertEqual(out["downloads"][1]["state"], "in_progress")

    def test_limit_validation(self):
        profile = self.make_profile()
        code, out = self.run_cli(
            ["--profile", str(profile), "history", "--limit", "0"])
        self.assertEqual(code, 1)
        self.assertIn("limit", out["error"])


class FakeCdpWsServer:
    """One-connection CDP WebSocket server for the WS client tests.

    Answers Page.enable with {}, Page.navigate with a frame result and
    then a Page.loadEventFired event. Records every method seen.
    """

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(1)
        self.port = self.sock.getsockname()[1]
        self.methods = []
        self.thread = threading.Thread(target=self._serve, daemon=True)

    def start(self):
        self.thread.start()

    def stop(self):
        try:
            self.sock.close()
        except OSError:
            pass

    def _recv_exact(self, conn, count):
        chunks = []
        while sum(len(c) for c in chunks) < count:
            chunk = conn.recv(count - sum(len(c) for c in chunks))
            if not chunk:
                raise RuntimeError("client closed")
            chunks.append(chunk)
        return b"".join(chunks)

    def _send_text(self, conn, text):
        data = text.encode()
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

    def _serve(self):
        import base64
        import hashlib
        try:
            conn, _ = self.sock.accept()
        except OSError:
            return
        with conn:
            conn.settimeout(10)
            buf = b""
            while b"\r\n\r\n" not in buf:
                chunk = conn.recv(4096)
                if not chunk:
                    return
                buf += chunk
            head = buf.split(b"\r\n\r\n", 1)[0].decode()
            key = [line.split(": ", 1)[1] for line in head.split("\r\n")
                   if line.lower().startswith("sec-websocket-key:")][0]
            accept = base64.b64encode(hashlib.sha1(
                (key + chromium_cli.WS_GUID).encode()).digest()).decode()
            conn.sendall(("HTTP/1.1 101 Switching Protocols\r\n"
                          "Upgrade: websocket\r\nConnection: Upgrade\r\n"
                          "Sec-WebSocket-Accept: %s\r\n\r\n" % accept).encode())
            while True:
                try:
                    first, second = self._recv_exact(conn, 2)
                except (RuntimeError, OSError):
                    return
                opcode = first & 0x0F
                if opcode == 0x8:
                    return
                length = second & 0x7F
                if length == 126:
                    length = struct.unpack(
                        ">H", self._recv_exact(conn, 2))[0]
                elif length == 127:
                    length = struct.unpack(
                        ">Q", self._recv_exact(conn, 8))[0]
                mask = self._recv_exact(conn, 4)
                payload = bytes(b ^ mask[i % 4] for i, b in
                                enumerate(self._recv_exact(conn, length)))
                frame = json.loads(payload.decode())
                method = frame.get("method", "")
                self.methods.append(method)
                if method == "Page.enable":
                    self._send_text(conn, json.dumps(
                        {"id": frame["id"], "result": {}}))
                elif method == "Page.navigate":
                    self._send_text(conn, json.dumps(
                        {"id": frame["id"], "result": {
                            "frameId": "F1", "loaderId": "L1"}}))
                    self._send_text(conn, json.dumps(
                        {"method": "Page.loadEventFired",
                         "params": {"timestamp": 1}}))
                else:
                    self._send_text(conn, json.dumps(
                        {"id": frame.get("id"), "result": {}}))


class WsClientTests(unittest.TestCase):
    def test_navigate_waits_for_load_event(self):
        server = FakeCdpWsServer()
        server.start()
        try:
            chromium_cli.navigate_tab_via_ws(
                {"webSocketDebuggerUrl":
                 "ws://127.0.0.1:%d/devtools/page/NEW1" % server.port},
                "https://example.com")
        finally:
            server.stop()
        self.assertEqual(server.methods, ["Page.enable", "Page.navigate"])

    def test_ws_connect_rejects_non_loopback(self):
        with self.assertRaises(ValueError):
            chromium_cli.ws_connect("ws://example.com:9222/devtools/page/X")

    def test_ws_connect_refuses_closed_port(self):
        with self.assertRaises((RuntimeError, OSError)):
            chromium_cli.ws_connect("ws://127.0.0.1:1/devtools/page/X")


class CuCliWiringTests(unittest.TestCase):
    """`computer-use cli` exposes chromium through the shared CLI."""

    def run_cu(self, argv):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "cu.py"), *argv],
            capture_output=True, text=True, timeout=60)
        return proc.returncode, json.loads(proc.stdout)

    def test_cli_list_includes_chromium(self):
        code, out = self.run_cu(["cli", "list"])
        self.assertEqual(code, 0)
        names = [app["name"] for app in out["apps"]]
        self.assertIn("chromium", names)
        self.assertEqual(len(names), 15)

    def test_cli_info_chromium_is_repo_owned(self):
        code, out = self.run_cu(["cli", "info", "chromium"])
        self.assertEqual(code, 0)
        self.assertTrue(out["skill_vendored"])
        self.assertIn("scripts/chromium_cli.py", out["install"])

    def test_cli_run_chromium_status_envelope(self):
        code, out = self.run_cu(
            ["cli", "run", "chromium", "--", "--endpoint",
             "http://127.0.0.1:1", "status"])
        self.assertEqual(code, 0)
        self.assertTrue(out["ok"])
        self.assertFalse(out["result"]["reachable"])
        self.assertEqual(out["result"]["command"], "status")


if __name__ == "__main__":
    unittest.main()
