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
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVER = ROOT / "scripts" / "mcp_server.py"

sys.path.insert(0, str(ROOT / "scripts"))
import mcp_server
import session_manager
import zen_dom


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

    def test_type_textarea(self):
        self.client.call_tool("session_start", {})
        first = json.loads(self.client.call_tool(
            "type", {"selector": "#notes", "text": "hello notes"})
            ["content"][0]["text"])
        self.assertTrue(first["ok"])
        self.assertEqual(first["before"], "")
        self.assertEqual(first["after"], "hello notes")
        second = json.loads(self.client.call_tool(
            "type", {"selector": "#notes", "text": "again"})
            ["content"][0]["text"])
        self.assertEqual(second["before"], "hello notes")
        self.assertEqual(second["after"], "again")
        log_line("type_textarea", self.started)

    def test_type_contenteditable(self):
        self.client.call_tool("session_start", {})
        result = json.loads(self.client.call_tool(
            "type", {"selector": "#editor", "text": "edited text"})
            ["content"][0]["text"])
        self.assertTrue(result["ok"])
        self.assertEqual(result["before"], "")
        self.assertEqual(result["after"], "edited text")
        log_line("type_contenteditable", self.started)

    def test_initialize_bad_protocol_version(self):
        reply = self.client.request("initialize", {
            "protocolVersion": "1900-01-01", "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "0.1.0"}})
        self.assertIn("error", reply)
        self.assertEqual(reply["error"]["code"], -32602)
        self.assertIn("unsupported protocol version",
                      reply["error"]["message"])
        # The server keeps serving after a rejected initialize.
        ping = self.client.request("ping")
        self.assertEqual(ping["result"], {})
        # A real newer protocol version negotiates and is echoed back.
        ok = self.client.request("initialize", {
            "protocolVersion": "2025-03-26", "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "0.1.0"}})
        self.assertEqual(ok["result"]["protocolVersion"], "2025-03-26")
        self.assertEqual(ok["result"]["serverInfo"]["name"],
                         "computer-use-mcp")
        log_line("initialize_bad_version", self.started)

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


class OversizedLineTest(unittest.TestCase):
    def test_oversized_line_returns_error_and_keeps_serving(self):
        started = time.monotonic()
        proc = subprocess.Popen(
            [sys.executable, str(SERVER), "--fake"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL)
        try:
            big = (b'{"jsonrpc": "2.0", "id": 99, "method": "ping"}'
                   + b" " * (8 * 1024 * 1024) + b"\n")
            proc.stdin.write(big)
            proc.stdin.flush()
            reply = json.loads(proc.stdout.readline())
            self.assertIn("error", reply)
            self.assertEqual(reply["error"]["code"], -32700)
            self.assertIn("maximum size", reply["error"]["message"])
            self.assertIsNone(reply["id"])
            # The server is still alive: a normal ping gets a reply.
            proc.stdin.write(
                b'{"jsonrpc": "2.0", "id": 1, "method": "ping"}\n')
            proc.stdin.flush()
            reply = json.loads(proc.stdout.readline())
            self.assertEqual(reply["id"], 1)
            self.assertEqual(reply["result"], {})
            self.assertIsNone(proc.poll(), "server must stay alive")
        finally:
            try:
                proc.stdin.close()
            except BrokenPipeError:
                pass
            proc.wait(timeout=10)
        self.assertEqual(proc.returncode, 0,
                         "server must exit cleanly on EOF")
        log_line("oversized_line", started)


class SessionStartRollbackTest(unittest.TestCase):
    def test_record_open_failure_rolls_back(self):
        started = time.monotonic()
        tmp = tempfile.TemporaryDirectory()
        manager = session_manager.SessionManager(directory=tmp.name)
        backend = mcp_server.ZenBackend.__new__(mcp_server.ZenBackend)
        backend.manager = manager
        backend.zen = None
        backend.session_id = None
        closed = []

        class FakeZen:
            session = "zen-1"

            def __init__(self, *args, **kwargs):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *exc):
                closed.append(True)
                return False

        real_zen = zen_dom.ZenSession
        zen_dom.ZenSession = FakeZen
        try:
            original_record_open = manager.record_open

            def boom(*args, **kwargs):
                raise RuntimeError("disk full")

            manager.record_open = boom
            with self.assertRaises(mcp_server.ToolError):
                backend.session_start({})
            self.assertIsNone(backend.zen)
            self.assertIsNone(backend.session_id)
            self.assertTrue(closed,
                            "failed start must close the Zen session")
            self.assertTrue(manager.try_lock(),
                            "manager lock must be released")
            self.assertIsNone(manager._read_state(),
                              "no open session may be recorded")
            # The slot is not leaked: a second start with record_open
            # restored succeeds.
            manager.record_open = original_record_open
            started_ok = backend.session_start({})
            self.assertTrue(started_ok["ok"])
            self.assertEqual(backend.session_id, "zen-1")
            self.assertIsNotNone(manager._read_state())
            done = backend.session_finish({})
            self.assertTrue(done["ok"])
            self.assertIsNone(manager._read_state())
        finally:
            zen_dom.ZenSession = real_zen
            tmp.cleanup()
        log_line("record_open_rollback", started)


class BadImageTest(unittest.TestCase):
    def test_bad_base64_screenshot_returns_error_result(self):
        started = time.monotonic()

        class BadBackend(mcp_server.FakeBackend):
            def screenshot(self, args):
                return {"ok": True,
                        "image_base64": "!!!not-base64!!!",
                        "mime_type": "image/png"}

        server = mcp_server.Server(BadBackend())
        reply = server.handle(
            {"jsonrpc": "2.0", "id": 7, "method": "tools/call",
             "params": {"name": "screenshot", "arguments": {}}})
        self.assertTrue(reply.get("isError"))
        body = json.loads(reply["content"][0]["text"])
        self.assertIn("invalid base64", body["error"])
        # The server keeps serving after the bad payload.
        again = server.handle(
            {"jsonrpc": "2.0", "id": 8, "method": "tools/call",
             "params": {"name": "session_status", "arguments": {}}})
        self.assertNotIn("error", again)
        log_line("bad_base64_screenshot", started)


_TYPE_FIXTURE = """<!doctype html><html><body>
<input id="name" value="">
<textarea id="notes"></textarea>
<div id="editor" contenteditable="true">start</div>
<script>
window.__events = [];
for (const id of ['name', 'notes', 'editor']) {
  const el = document.getElementById(id);
  el.addEventListener('input', () => window.__events.push(id + ':input'));
  el.addEventListener('change', () => window.__events.push(id + ':change'));
}
</script>
</body></html>
"""

_TYPE_DRIVER = """
const fs = require('fs');
const path = require('path');
const { chromium } = require(process.env.PLAYWRIGHT_CORE_PATH);
function chromiumPath() {
  if (process.env.CHROMIUM_PATH && fs.existsSync(process.env.CHROMIUM_PATH)) {
    return process.env.CHROMIUM_PATH;
  }
  const cached = path.join(process.env.HOME || '',
    '.cache/ms-playwright/chromium-1254/chrome-linux64/chrome');
  if (fs.existsSync(cached)) return cached;
  return undefined;
}
(async () => {
  const js = fs.readFileSync(process.argv[2], 'utf8');
  const fixture = process.argv[3];
  const browser = await chromium.launch({
    executablePath: chromiumPath(), args: ['--no-sandbox'] });
  try {
    const page = await browser.newPage();
    await page.goto('file://' + fixture);
    const out = {};
    for (const [sel, text] of [['#name', 'Ada'],
                               ['#notes', 'hello notes'],
                               ['#editor', 'edited text']]) {
      out[sel] = await page.evaluate((args) => {
        const fn = new Function('arguments', args.js);
        return fn([args.selector, args.text]);
      }, { js, selector: sel, text });
    }
    out.events = await page.evaluate(() => window.__events);
    console.log(JSON.stringify(out));
  } finally {
    await browser.close();
  }
})().catch((e) => { console.error(e); process.exit(1); });
"""


def _find_playwright_core():
    candidates = []
    env = os.environ.get("PLAYWRIGHT_CORE_PATH")
    if env:
        candidates.append(env)
    candidates.append("/tmp/realistic-b2-scratch/node_modules/playwright-core")
    for path in candidates:
        if path and os.path.isdir(path):
            return path
    return None


@unittest.skipUnless(_find_playwright_core(),
                     "playwright-core not installed on this machine")
class RealDomTypeTest(unittest.TestCase):
    def test_type_js_on_real_dom(self):
        started = time.monotonic()
        tmp = tempfile.TemporaryDirectory()
        js_path = os.path.join(tmp.name, "type_js.txt")
        fixture_path = os.path.join(tmp.name, "fixture.html")
        driver_path = os.path.join(tmp.name, "driver.cjs")
        with open(js_path, "w", encoding="utf-8") as handle:
            handle.write(mcp_server.TYPE_JS)
        with open(fixture_path, "w", encoding="utf-8") as handle:
            handle.write(_TYPE_FIXTURE)
        with open(driver_path, "w", encoding="utf-8") as handle:
            handle.write(_TYPE_DRIVER)
        env = dict(os.environ)
        env["PLAYWRIGHT_CORE_PATH"] = _find_playwright_core()
        proc = subprocess.run(
            ["node", driver_path, js_path, fixture_path],
            capture_output=True, text=True, timeout=120, env=env)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = json.loads(proc.stdout.strip().splitlines()[-1])
        self.assertTrue(out["#name"]["found"])
        self.assertEqual(out["#name"]["before"], "")
        self.assertEqual(out["#name"]["after"], "Ada")
        self.assertTrue(out["#notes"]["found"])
        self.assertEqual(out["#notes"]["after"], "hello notes")
        self.assertTrue(out["#editor"]["found"])
        self.assertEqual(out["#editor"]["before"], "start")
        self.assertEqual(out["#editor"]["after"], "edited text")
        self.assertEqual(out["events"],
                         ["name:input", "name:change",
                          "notes:input", "notes:change",
                          "editor:input", "editor:change"])
        tmp.cleanup()
        log_line("type_js_real_dom", started)


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
