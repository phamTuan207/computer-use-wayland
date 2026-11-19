"""Warm-browser manager tests; non-live, no real browser, no network.

Run with unittest discover: python3 -m unittest discover -s tests -p 'test_*.py'
or directly: python3 tests/test_warm_browser.py

CDP is stubbed twice: an in-process HTTP server implements
/json/version, /json/list and /json/close, and an in-process
WebSocket server answers the browser-level calls
(Target.createBrowserContext / createTarget / disposeBrowserContext)
and the page-level calls (Page.enable, Page.navigate,
Runtime.evaluate) with per-connection storage, so the isolation
probe can be exercised end to end. The state file is redirected to
a temp dir, so no real HOME state is touched.

What is NOT tested here: a real Chromium. That is the laptop live
probe (scripts/warm_browser.py CLI against a test Chromium on a
separate port with its own profile), reported in
improvements/live-test-log.md.
"""
import base64
import hashlib
import io
import json
import os
import re
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import warm_browser  # noqa: E402

WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def _ws_frame(payload, opcode=1):
    header = bytearray([0x80 | opcode])
    length = len(payload)
    if length < 126:
        header.append(length)
    elif length < 65536:
        header.append(126)
        header += struct.pack(">H", length)
    else:
        header.append(127)
        header += struct.pack(">Q", length)
    return bytes(header) + payload


def _ws_read_frame(conn):
    def exact(count):
        data = b""
        while len(data) < count:
            chunk = conn.recv(count - len(data))
            if not chunk:
                raise ConnectionError("ws closed")
            data += chunk
        return data

    first, second = exact(2)
    opcode = first & 0x0F
    length = second & 0x7F
    if length == 126:
        length = struct.unpack(">H", exact(2))[0]
    elif length == 127:
        length = struct.unpack(">Q", exact(8))[0]
    mask = exact(4) if second & 0x80 else None
    payload = exact(length)
    if mask:
        payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
    return opcode, payload


class _StubState:
    def __init__(self):
        self.targets = {}  # target id -> dict
        self.contexts = {}  # browser context id -> set of target ids
        self.next_ctx = 1
        self.next_target = 1
        self.lock = threading.Lock()


class _WSStubServer:
    """Holder for the stub WS socket plus its control handles."""

    def __init__(self, sock, port):
        self.sock = sock
        self.port = port
        self.stop_event = threading.Event()
        self.thread = None

    def close(self):
        self.stop_event.set()
        try:
            self.sock.close()
        except OSError:
            pass


def _make_ws_server(state, host="127.0.0.1", port=0):
    """Minimal WS server for browser-level and page-level CDP calls."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(16)
    server = _WSStubServer(sock, sock.getsockname()[1])
    stop = server.stop_event

    def handle(conn):
        storage = {"cookie": "", "ls": None}
        try:
            request = b""
            while b"\r\n\r\n" not in request:
                chunk = conn.recv(4096)
                if not chunk:
                    return
                request += chunk
            head, _, _ = request.partition(b"\r\n\r\n")
            lines = head.decode("latin1").split("\r\n")
            path = lines[0].split(" ")[1]
            key = None
            for line in lines[1:]:
                if line.lower().startswith("sec-websocket-key:"):
                    key = line.split(":", 1)[1].strip()
            accept = base64.b64encode(
                hashlib.sha1((key + WS_GUID).encode("ascii")).digest()
            ).decode("ascii")
            conn.sendall(
                ("HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\n"
                 "Connection: Upgrade\r\nSec-WebSocket-Accept: %s\r\n\r\n"
                 % accept).encode("ascii"))
            is_browser = path.startswith("/devtools/browser/")
            target_id = path.rsplit("/", 1)[-1] if not is_browser else None
            while not stop.is_set():
                try:
                    opcode, payload = _ws_read_frame(conn)
                except (ConnectionError, OSError):
                    return
                if opcode == 9:
                    conn.sendall(_ws_frame(payload, opcode=10))
                    continue
                if opcode == 8:
                    return
                if opcode != 1:
                    continue
                try:
                    message = json.loads(payload.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
                call_id = message.get("id")
                method = message.get("method")
                params = message.get("params", {})
                result = {}
                if method == "Target.createBrowserContext":
                    with state.lock:
                        ctx = "ctx-%d" % state.next_ctx
                        state.next_ctx += 1
                        state.contexts[ctx] = set()
                    result = {"browserContextId": ctx}
                elif method == "Target.createTarget":
                    ctx = params.get("browserContextId")
                    with state.lock:
                        tid = "target-%d" % state.next_target
                        state.next_target += 1
                        state.targets[tid] = {
                            "id": tid, "type": "page",
                            "url": params.get("url", "about:blank"),
                            "webSocketDebuggerUrl":
                                "ws://127.0.0.1:%d/devtools/page/%s"
                                % (server.port, tid),
                            "browserContextId": ctx}
                        if ctx:
                            state.contexts.setdefault(ctx, set()).add(tid)
                    result = {"targetId": tid}
                elif method == "Target.disposeBrowserContext":
                    ctx = params.get("browserContextId")
                    with state.lock:
                        for tid in state.contexts.pop(ctx, set()):
                            state.targets.pop(tid, None)
                    result = {}
                elif method == "Page.enable":
                    result = {}
                elif method == "Page.navigate":
                    result = {"frameId": "frame-1"}
                elif method == "Runtime.evaluate":
                    expr = params.get("expression", "")
                    if "localStorage.setItem" in expr:
                        found = re.search(
                            r"localStorage\.setItem\('([^']+)','([^']+)'\)",
                            expr)
                        cookie = re.search(
                            r"document\.cookie='([^=]+)=([^;]+);", expr)
                        if found:
                            storage["ls"] = found.group(2)
                        if cookie:
                            storage["cookie"] = "%s=%s" % (
                                cookie.group(1), cookie.group(2))
                        result = {"result": {"type": "string",
                                             "value": storage["cookie"]}}
                    elif expr.strip() == "document.cookie":
                        result = {"result": {"type": "string",
                                             "value": storage["cookie"]}}
                    elif "localStorage.getItem" in expr:
                        result = {"result": {"type": "string",
                                             "value": storage["ls"]}}
                    else:
                        result = {"result": {"type": "undefined"}}
                else:
                    result = {"error": {"code": -32601,
                                        "message": "unknown method " + str(method)}}
                if "error" in result:
                    reply = {"id": call_id, "error": result["error"]}
                else:
                    reply = {"id": call_id, "result": result}
                conn.sendall(_ws_frame(json.dumps(reply).encode("utf-8")))
                if method == "Page.navigate":
                    conn.sendall(_ws_frame(json.dumps(
                        {"method": "Page.loadEventFired",
                         "params": {"timestamp": 0}}).encode("utf-8")))
        except OSError:
            return
        finally:
            try:
                conn.close()
            except OSError:
                pass

    def serve():
        while not stop.is_set():
            try:
                sock.settimeout(0.2)
                conn, _ = sock.accept()
            except socket.timeout:
                continue
            except OSError:
                return
            threading.Thread(target=handle, args=(conn,),
                             daemon=True).start()

    thread = threading.Thread(target=serve, daemon=True)
    thread.start()
    server.thread = thread
    return server


def _make_http_server(state, ws_port, host="127.0.0.1", port=0):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, payload, code=200):
            body = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path == "/json/version":
                self._send({"Browser": "Stub/1.0",
                            "webSocketDebuggerUrl":
                                "ws://127.0.0.1:%d/devtools/browser/stub"
                                % ws_port})
            elif self.path == "/json/list":
                with state.lock:
                    self._send(list(state.targets.values()))
            elif self.path.startswith("/json/close/"):
                target_id = self.path.rsplit("/", 1)[-1]
                with state.lock:
                    state.targets.pop(target_id, None)
                self._send({})
            else:
                self._send({"error": "not found"}, code=404)

        def do_PUT(self):
            self._send({"error": "unused in tests"}, code=404)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer((host, port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


class WarmBrowserTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.state_dir = Path(self.tmp.name) / "state"
        self.state_dir.mkdir()
        self.stub = _StubState()
        self.ws = _make_ws_server(self.stub)
        self.http = _make_http_server(self.stub, self.ws.port)
        self.endpoint = "http://127.0.0.1:%d" % self.http.server_address[1]

    def tearDown(self):
        self.http.shutdown()
        self.http.server_close()
        self.ws.stop_event.set()
        self.ws.close()
        self.tmp.cleanup()

    def test_validate_endpoint_rejects_non_loopback(self):
        for bad in ("https://127.0.0.1:9222", "http://example.com:9222",
                    "http://192.168.1.1:9222", "ftp://127.0.0.1:21",
                    "http://127.0.0.1:99999", "http://127.0.0.1:notaport"):
            with self.assertRaises(warm_browser.WarmBrowserError, msg=bad):
                warm_browser.validate_endpoint(bad)

    def test_health_ok_and_unreachable(self):
        probe = warm_browser.health(self.endpoint)
        self.assertTrue(probe["ok"])
        self.assertEqual(probe["version"], "Stub/1.0")
        self.assertEqual(probe["target_count"], 0)
        dead = warm_browser.health("http://127.0.0.1:1")
        self.assertFalse(dead["ok"])
        self.assertIsNotNone(dead["error"])

    def test_ensure_warm_reuses_healthy_endpoint_without_launching(self):
        with mock.patch.object(warm_browser, "_launch_chromium") as launch:
            launch.side_effect = AssertionError("must not cold-launch")
            result = warm_browser.ensure_warm(endpoint=self.endpoint,
                                              state_dir=self.state_dir)
        self.assertTrue(result["ok"])
        self.assertTrue(result["reused"])
        self.assertIsNone(result["pid"])
        self.assertIsNone(result["launch_ms"])

    def test_ensure_warm_launches_when_unhealthy_and_records_state(self):
        dead = "http://127.0.0.1:1"
        calls = {"health": 0}

        def fake_health(endpoint):
            calls["health"] += 1
            return {"ok": calls["health"] > 1, "endpoint": endpoint,
                    "version": "Stub/1.0", "target_count": 0, "error": None}

        with mock.patch.object(warm_browser, "_launch_chromium",
                               return_value=(4242, 12.5)) as launch, \
                mock.patch.object(warm_browser, "health",
                                  side_effect=fake_health):
            result = warm_browser.ensure_warm(endpoint=dead,
                                              state_dir=self.state_dir)
        launch.assert_called_once()
        self.assertFalse(result["reused"])
        self.assertEqual(result["pid"], 4242)
        self.assertEqual(result["launch_ms"], 12.5)
        state = warm_browser._read_state(self.state_dir)
        self.assertEqual(state["pid"], 4242)
        self.assertEqual(oct(
            (self.state_dir / "warm-browser.json").stat().st_mode & 0o777),
            "0o600")

    def test_new_task_context_creates_distinct_fresh_contexts(self):
        first = warm_browser.new_task_context(
            "task-a", endpoint=self.endpoint, state_dir=self.state_dir)
        second = warm_browser.new_task_context(
            "task-b", endpoint=self.endpoint, state_dir=self.state_dir)
        self.assertTrue(first["warm"])
        self.assertNotEqual(first["target_id"], second["target_id"])
        self.assertNotEqual(first["browser_context_id"],
                            second["browser_context_id"])
        self.assertLess(first["total_ms"], 10000)
        state = warm_browser._read_state(self.state_dir)
        self.assertEqual(len(state["contexts"]), 2)

    def test_new_task_context_rejects_bad_url(self):
        with self.assertRaises(warm_browser.WarmBrowserError):
            warm_browser.new_task_context(
                "task-x", url="ftp://example.com/file",
                endpoint=self.endpoint, state_dir=self.state_dir)

    def test_close_task_context_disposes_and_clears_state(self):
        record = warm_browser.new_task_context(
            "task-a", endpoint=self.endpoint, state_dir=self.state_dir)
        self.assertEqual(len(self.stub.targets), 1)
        closed = warm_browser.close_task_context(
            task_id="task-a", endpoint=self.endpoint,
            state_dir=self.state_dir)
        self.assertTrue(closed["ok"])
        self.assertEqual(len(self.stub.targets), 0)
        self.assertEqual(
            warm_browser._read_state(self.state_dir).get("contexts"), [])

    def test_close_unknown_task_raises(self):
        with self.assertRaises(warm_browser.WarmBrowserError):
            warm_browser.close_task_context(
                task_id="no-such-task", endpoint=self.endpoint,
                state_dir=self.state_dir)

    def test_verify_isolation_proves_contexts_cannot_see_each_other(self):
        result = warm_browser.verify_isolation(
            endpoint=self.endpoint, state_dir=self.state_dir)
        self.assertTrue(result["ok"])
        self.assertTrue(result["a_sees_marker"])
        self.assertFalse(result["b_sees_marker"])
        self.assertTrue(result["isolated"])
        self.assertEqual(len(self.stub.targets), 0)
        self.assertEqual(
            warm_browser._read_state(self.state_dir).get("contexts"), [])

    def test_cold_fallback_retries_once_after_first_failure(self):
        real_create = warm_browser._create_context
        calls = {"n": 0}

        def flaky(endpoint, task_id, url, state_dir):
            calls["n"] += 1
            if calls["n"] == 1:
                raise warm_browser.WarmBrowserError("stale warm browser")
            return real_create(endpoint, task_id, url, state_dir)

        with mock.patch.object(warm_browser, "_create_context",
                               side_effect=flaky), \
                mock.patch.object(warm_browser, "_launch_chromium",
                                  return_value=(777, 9.9)) as launch, \
                mock.patch.object(warm_browser, "_pid_is_ours",
                                  return_value=False):
            record = warm_browser.new_task_context(
                "task-retry", endpoint=self.endpoint,
                state_dir=self.state_dir)
        self.assertEqual(calls["n"], 2)
        launch.assert_called_once()
        self.assertFalse(record["warm"])
        state = warm_browser._read_state(self.state_dir)
        self.assertEqual(state["pid"], 777)

    def test_stop_refuses_foreign_pid(self):
        own_pid = os.getpid()
        warm_browser._write_state(self.state_dir, {
            "endpoint": self.endpoint, "pid": own_pid,
            "profile": str(self.state_dir / "warm-browser-profile"),
            "contexts": []})
        result = warm_browser.stop(state_dir=self.state_dir)
        self.assertFalse(result["ok"])
        self.assertFalse(result["stopped"])
        self.assertTrue(os.path.exists("/proc/%d" % own_pid))

    def test_stop_without_pid_is_a_noop(self):
        result = warm_browser.stop(state_dir=self.state_dir)
        self.assertTrue(result["ok"])
        self.assertFalse(result["stopped"])

    def test_ws_client_call_and_event(self):
        browser_url = ("ws://127.0.0.1:%d/devtools/browser/stub"
                       % self.ws.port)
        client = warm_browser._WSClient(browser_url)
        try:
            created = client.call("Target.createBrowserContext", {})
            self.assertIn("browserContextId", created)
            with self.assertRaises(warm_browser.WarmBrowserError):
                client.call("Nope.unknownMethod", {})
        finally:
            client.close()

    def test_cli_health_prints_one_json_object(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = warm_browser.main(
                ["--endpoint", self.endpoint, "health"])
        self.assertEqual(code, 0)
        parsed = json.loads(buffer.getvalue())
        self.assertTrue(parsed["ok"])

    def test_cli_unknown_command_exits_nonzero(self):
        with self.assertRaises(SystemExit):
            warm_browser.main(["--endpoint", self.endpoint, "nope"])


if __name__ == "__main__":
    unittest.main()
