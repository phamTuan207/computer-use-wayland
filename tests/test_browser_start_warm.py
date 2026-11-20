"""browser_start warm-browser adoption tests; no real browser, no network.

browser_start() now warms through scripts/warm_browser.py: a live
endpoint owned by us (recorded pid verified) gets a fresh browser
context per start, so a task's cookies/localStorage cannot leak into
the next task; a foreign endpoint is reused exactly as before; a dead
endpoint cold-launches through the hardened legacy path and the new
process is registered with the warm module. The module's own stub-CDP
tests prove the isolation primitive; these tests prove the adoption
seam in cu.py:

  (a) the warm path is used when the warm browser is healthy;
  (b) each start gets a fresh context, the previous start's context is
      closed, and a marker set in one start's context is absent in the
      next start's context (end to end through the real warm_browser
      module against the stub CDP servers from test_warm_browser);
  (c) cold fallback engages when warm is unavailable (cold launch with
      register, foreign endpoint reuse, warm-module import failure,
      warm-context failure degrading to the pre-adoption result).

The stub CDP servers are reused from test_warm_browser; the "our pid"
for the end-to-end test is a sleep process whose argv[0] is faked to a
Chromium command line, which is exactly what warm_browser._pid_is_ours
checks in /proc.
"""
import io
import json
import pathlib
import socket
import subprocess
import sys
import tempfile
import threading
import types
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

import cu  # noqa: E402
import warm_browser  # noqa: E402
import test_warm_browser as wb_tests  # noqa: E402


class FakeCDP:
    """Loopback HTTP endpoint answering /json/version; no browser behind it."""

    def __init__(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                body = b"{}" if self.path.startswith("/json/version") else b"[]"
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
        self.server.server_close()
        return False

    @property
    def url(self):
        return "http://127.0.0.1:%d" % self.port


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


class FakeWarm:
    """Stand-in warm_browser module with canned, recorded behaviour."""

    def __init__(self, ensure=None, contexts=None, profile="/tmp/warm-profile"):
        self.calls = []
        self.ensure_result = ensure if ensure is not None else {
            "ok": True, "endpoint": "http://127.0.0.1:9222",
            "reused": True, "pid": 1234, "launch_ms": None, "health": {}}
        self.contexts = list(contexts) if contexts is not None else []
        self.profile = profile
        self.next_target = 0
        self.closed = []
        self.registered = []
        self.raise_on_context = None

    def ensure_warm(self, endpoint=None, state_dir=None, env=None):
        self.calls.append(("ensure_warm", endpoint, state_dir))
        result = dict(self.ensure_result)
        result["endpoint"] = endpoint
        return result

    def new_task_context(self, task_id, url=None, endpoint=None,
                         state_dir=None, env=None):
        self.calls.append(("new_task_context", task_id, endpoint, state_dir))
        if self.raise_on_context is not None:
            raise self.raise_on_context
        self.next_target += 1
        return {"ok": True, "task_id": task_id,
                "target_id": "target-%d" % self.next_target,
                "browser_context_id": "ctx-%d" % self.next_target,
                "url": url or "about:blank", "context_ms": 25.0,
                "ensure_ms": 5.0, "total_ms": 30.0, "endpoint": endpoint}

    def close_task_context(self, task_id=None, target_id=None,
                           endpoint=None, state_dir=None):
        self.calls.append(("close_task_context", task_id, endpoint))
        self.closed.append(task_id)
        return {"ok": True, "closed": "browser_context:x", "task_id": task_id}

    def status(self, endpoint=None, state_dir=None):
        self.calls.append(("status", endpoint, state_dir))
        return {"ok": True, "endpoint": endpoint, "health": {"ok": True},
                "recorded_pid": self.ensure_result.get("pid"),
                "recorded_profile": self.profile,
                "contexts": list(self.contexts)}

    def register(self, endpoint, pid, profile, state_dir=None):
        self.calls.append(("register", endpoint, pid, profile, state_dir))
        self.registered.append((endpoint, pid, profile))
        return {"ok": True, "endpoint": endpoint, "pid": pid,
                "profile": profile}


def make_fake_module(fake):
    module = types.ModuleType("warm_browser")
    module.ensure_warm = fake.ensure_warm
    module.new_task_context = fake.new_task_context
    module.close_task_context = fake.close_task_context
    module.status = fake.status
    module.register = fake.register
    module.PROFILE_DIRNAME = "warm-browser-profile"
    module.WarmBrowserError = warm_browser.WarmBrowserError
    return module


class BrowserStartWarmTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name)
        self._state_patch = mock.patch.object(cu, "STATE", self.tmp)
        self._state_patch.start()
        self.addCleanup(self._state_patch.stop)

    def start_with_fake(self, fake, endpoint="http://127.0.0.1:9222"):
        """browser_start with the fake warm module and a live probe."""
        module = make_fake_module(fake)
        with mock.patch.dict(sys.modules, {"warm_browser": module}), \
                mock.patch("urllib.request.urlopen",
                           return_value=io.StringIO("{}")):
            return cu.browser_start({}, endpoint)

    def test_warm_path_used_when_warm_browser_healthy(self):
        """(a) Healthy warm browser: start reuses it and returns a fresh
        context target; no cold launch is ever attempted."""
        fake = FakeWarm(profile=str(self.tmp / "warm-browser-profile"))
        with mock.patch.object(cu.subprocess, "Popen",
                               side_effect=AssertionError("must not launch")):
            result = self.start_with_fake(fake)
        self.assertTrue(result["ok"])
        self.assertTrue(result["warm"])
        self.assertTrue(result["reused"])
        self.assertEqual(result["pid"], 1234)
        self.assertEqual(result["target_id"], "target-1")
        self.assertEqual(result["browser_context_id"], "ctx-1")
        self.assertTrue(result["task_id"].startswith("browser-start-"))
        self.assertEqual(result["profile"],
                         str(self.tmp / "warm-browser-profile"))
        kinds = [c[0] for c in fake.calls]
        self.assertIn("ensure_warm", kinds)
        self.assertIn("new_task_context", kinds)
        self.assertNotIn("register", kinds)
        self.assertNotIn("close_task_context", kinds,
                         "no prior context exists on the first start")
        _, _, state_dir = fake.calls[0]
        self.assertEqual(state_dir, self.tmp)

    def test_second_start_gets_fresh_context_and_closes_prior(self):
        """(b, seam level) Two starts yield distinct contexts and the
        second start closes the first start's context."""
        fake = FakeWarm()
        first = self.start_with_fake(fake)
        fake.contexts = [{"task_id": first["task_id"],
                          "target_id": first["target_id"],
                          "browser_context_id": first["browser_context_id"]}]
        second = self.start_with_fake(fake)
        self.assertNotEqual(first["task_id"], second["task_id"])
        self.assertNotEqual(first["target_id"], second["target_id"])
        self.assertNotEqual(first["browser_context_id"],
                            second["browser_context_id"])
        self.assertIn(first["task_id"], fake.closed)

    def test_cold_launch_registers_then_creates_fresh_context(self):
        """(c) Dead endpoint: the hardened legacy launch runs, the new
        process is registered with the warm module, and the start still
        returns a fresh context from it."""
        fake = FakeWarm()
        cold = {"ok": True, "endpoint": "http://127.0.0.1:9222",
                "reused": False, "pid": 4242,
                "profile": str(self.tmp / "browser-profile")}
        module = make_fake_module(fake)
        with mock.patch.dict(sys.modules, {"warm_browser": module}), \
                mock.patch("urllib.request.urlopen",
                           side_effect=OSError("offline")), \
                mock.patch.object(cu, "_browser_start_cold",
                                  return_value=cold) as launch:
            result = cu.browser_start({}, "http://127.0.0.1:9222")
        launch.assert_called_once()
        self.assertEqual(launch.call_args.args[3], 9222)
        self.assertFalse(launch.call_args.kwargs.get("probe_alive", True),
                         "the caller already probed; no second probe")
        self.assertEqual(fake.registered,
                         [("http://127.0.0.1:9222", 4242,
                           str(self.tmp / "browser-profile"))])
        self.assertTrue(result["ok"])
        self.assertTrue(result["warm"])
        self.assertFalse(result["reused"])
        self.assertEqual(result["pid"], 4242)
        self.assertEqual(result["profile"], str(self.tmp / "browser-profile"))
        self.assertEqual(result["target_id"], "target-1")

    def test_foreign_endpoint_reused_exactly_as_before(self):
        """(c) An endpoint we do not own (pid None: someone else's browser
        or a test stub) is reused with the legacy shape, no fresh context
        is forced on it, and new_task_context is never called."""
        fake = FakeWarm(ensure={"ok": True, "reused": True, "pid": None,
                                "launch_ms": None, "health": {}})
        result = self.start_with_fake(fake)
        self.assertEqual(result, {"ok": True,
                                  "endpoint": "http://127.0.0.1:9222",
                                  "reused": True})
        kinds = [c[0] for c in fake.calls]
        self.assertNotIn("new_task_context", kinds)
        self.assertNotIn("close_task_context", kinds)
        self.assertNotIn("register", kinds)

    def test_context_failure_degrades_to_pre_adoption_result(self):
        """(c) When the browser IS ours but context creation fails, the
        start hands back the working browser exactly as before the
        adoption instead of failing a start the old code returned."""
        fake = FakeWarm()
        fake.raise_on_context = warm_browser.WarmBrowserError(
            "warm browser cold-start fallback failed after retry: boom")
        result = self.start_with_fake(fake)
        self.assertEqual(result, {"ok": True,
                                  "endpoint": "http://127.0.0.1:9222",
                                  "reused": True})
        cold = {"ok": True, "endpoint": "http://127.0.0.1:9222",
                "reused": False, "pid": 4242,
                "profile": str(self.tmp / "browser-profile")}
        module = make_fake_module(fake)
        with mock.patch.dict(sys.modules, {"warm_browser": module}), \
                mock.patch("urllib.request.urlopen",
                           side_effect=OSError("offline")), \
                mock.patch.object(cu, "_browser_start_cold",
                                  return_value=cold):
            result = cu.browser_start({}, "http://127.0.0.1:9222")
        self.assertEqual(result, cold)

    def test_missing_warm_module_falls_back_to_legacy_cold_path(self):
        """(c) A checkout without scripts/warm_browser.py still starts a
        browser exactly as before: reuse answers, dead ports raise."""
        with mock.patch.dict(sys.modules, {"warm_browser": None}):
            with FakeCDP() as cdp:
                result = cu.browser_start({}, cdp.url)
            self.assertEqual(result, {"ok": True, "endpoint": cdp.url,
                                      "reused": True})
            dead = free_port()
            with mock.patch.object(cu.subprocess, "Popen",
                                  side_effect=OSError("no browser")) as spawn:
                with self.assertRaisesRegex(OSError, "no browser"):
                    cu.browser_start({}, "http://127.0.0.1:%d" % dead)
            argv = spawn.call_args.args[0]
            self.assertIn("--remote-debugging-port=%d" % dead, argv)


class WarmRegisterTests(unittest.TestCase):
    """register() records a foreign-launched process for later reuse."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.state_dir = pathlib.Path(tmp.name)

    def test_register_records_pid_and_profile(self):
        result = warm_browser.register(
            "http://127.0.0.1:9222", 4242, "/tmp/warm-profile",
            state_dir=self.state_dir)
        self.assertTrue(result["ok"])
        state = warm_browser._read_state(self.state_dir)
        self.assertEqual(state["pid"], 4242)
        self.assertEqual(state["profile"], "/tmp/warm-profile")
        self.assertEqual(state["endpoint"], "http://127.0.0.1:9222")
        self.assertEqual(oct((self.state_dir / "warm-browser.json")
                             .stat().st_mode & 0o777), "0o600")

    def test_register_preserves_recorded_contexts(self):
        warm_browser._write_state(self.state_dir, {
            "endpoint": "http://127.0.0.1:9222", "pid": 111,
            "profile": "/tmp/old",
            "contexts": [{"task_id": "browser-start-abc"}]})
        warm_browser.register("http://127.0.0.1:9222", 4242, "/tmp/new",
                              state_dir=self.state_dir)
        state = warm_browser._read_state(self.state_dir)
        self.assertEqual(state["pid"], 4242)
        self.assertEqual(state["contexts"],
                         [{"task_id": "browser-start-abc"}])

    def test_register_rejects_bad_input(self):
        with self.assertRaises(warm_browser.WarmBrowserError):
            warm_browser.register("http://127.0.0.1:9222", 0, "/tmp/p",
                                  state_dir=self.state_dir)
        with self.assertRaises(warm_browser.WarmBrowserError):
            warm_browser.register("http://example.com:9222", 4242, "/tmp/p",
                                  state_dir=self.state_dir)
        with self.assertRaises(warm_browser.WarmBrowserError):
            warm_browser.register("http://127.0.0.1:9222", 4242, "",
                                  state_dir=self.state_dir)


class BrowserStartWarmEndToEndTests(unittest.TestCase):
    """(b, end to end) Real warm_browser module against the stub CDP
    servers: two browser_start calls, marker cookie + localStorage set
    in the first start's context, absent in the second's."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.tmp = pathlib.Path(tmp.name)
        self.state_dir = self.tmp / "state"
        self.state_dir.mkdir()
        self.stub = wb_tests._StubState()
        self.ws = wb_tests._make_ws_server(self.stub)
        self.http = wb_tests._make_http_server(self.stub, self.ws.port)
        self.endpoint = ("http://127.0.0.1:%d"
                         % self.http.server_address[1])
        self._state_patch = mock.patch.object(cu, "STATE", self.state_dir)
        self._state_patch.start()
        self.addCleanup(self._state_patch.stop)
        # Fake "our" Chromium pid: a sleep whose argv[0] is a Chromium
        # command line with our profile, which _pid_is_ours checks.
        self.profile = self.state_dir / "warm-browser-profile"
        self.proc = subprocess.Popen(
            ["chromium --user-data-dir=%s" % self.profile, "30"],
            executable="/bin/sleep",
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.addCleanup(self._kill_proc)
        warm_browser._write_state(self.state_dir, {
            "endpoint": self.endpoint, "pid": self.proc.pid,
            "profile": str(self.profile), "contexts": []})

    def _kill_proc(self):
        try:
            self.proc.terminate()
            self.proc.wait(timeout=3)
        except Exception:
            try:
                self.proc.kill()
            except Exception:
                pass

    def tearDown(self):
        self.http.shutdown()
        self.http.server_close()
        self.ws.stop_event.set()
        self.ws.close()

    def _client(self, target_id):
        return warm_browser._WSClient(
            warm_browser._target_ws_url(self.endpoint, target_id))

    def test_marker_in_first_context_absent_in_second(self):
        first = cu.browser_start({}, self.endpoint)
        self.assertTrue(first.get("warm"))
        self.assertEqual(first["target_id"], "target-1")
        marker = "wb-adoption-probe"
        set_expr = (
            "(()=>{document.cookie='%s=%s; path=/';"
            "try{localStorage.setItem('%s','%s');}catch(_){}"
            "return document.cookie;})()"
            % (warm_browser.ISOLATION_COOKIE_NAME, marker,
               warm_browser.ISOLATION_STORAGE_KEY, marker))
        get_storage = (
            "(()=>{try{return localStorage.getItem('%s');}catch(_){return null;}})()"
            % warm_browser.ISOLATION_STORAGE_KEY)
        # The stub keeps storage per WebSocket connection, so the set and
        # the read-back in the first context share one connection, exactly
        # like warm_browser.verify_isolation does.
        ws_first = self._client(first["target_id"])
        try:
            seen_cookie = warm_browser._evaluate(ws_first, set_expr)
            seen_storage = warm_browser._evaluate(ws_first, get_storage)
        finally:
            ws_first.close()
        self.assertIn(marker, seen_cookie)
        self.assertEqual(seen_storage, marker)
        second = cu.browser_start({}, self.endpoint)
        self.assertNotEqual(first["target_id"], second["target_id"])
        self.assertNotEqual(first["browser_context_id"],
                            second["browser_context_id"])
        self.assertEqual(len(self.stub.targets), 1,
                         "the first start's context was closed")
        ws_second = self._client(second["target_id"])
        try:
            other_cookie = warm_browser._evaluate(ws_second,
                                                  "document.cookie")
            other_storage = warm_browser._evaluate(ws_second, get_storage)
        finally:
            ws_second.close()
        self.assertNotIn(marker, other_cookie or "")
        self.assertNotEqual(other_storage, marker)
        self.assertIsNone(other_storage)


if __name__ == "__main__":
    unittest.main()
