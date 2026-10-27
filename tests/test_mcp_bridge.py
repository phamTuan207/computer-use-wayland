"""GUI-free unit tests for scripts/mcp_bridge.py.

The bridge is exercised only through its existing seams:
- module import after manipulating os.environ (executable resolution),
- main() driven with in-memory stdin/stdout doubles (MCP framing),
- tool_call() status/finish/validation paths with fake Popen stand-ins.

No real driver is spawned, the installed CLI is never launched, no network,
and the real stdin/stdout main loop is never started (fake BytesIO only).
All temporary files and pipes are owned by the tests via addCleanup.
"""
import importlib.util
import io
import itertools
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import types
import unittest
from pathlib import Path
from unittest import mock

TREE_ROOT = Path(__file__).resolve().parent.parent
BRIDGE_PATH = TREE_ROOT / "scripts" / "mcp_bridge.py"
sys.path.insert(0, str(TREE_ROOT / "scripts"))
import mcp_bridge_transport as transport

_name_counter = itertools.count()


def load_bridge(env_overrides=None):
    """Import a fresh copy of the bridge module under a controlled environment."""
    with mock.patch.dict(os.environ):
        os.environ.pop("CU_EXECUTABLE", None)
        for key, value in (env_overrides or {}).items():
            os.environ[key] = value
        spec = importlib.util.spec_from_file_location(
            "mcp_bridge_under_test_%d" % next(_name_counter), str(BRIDGE_PATH))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


class FakeProc:
    """Minimal Popen stand-in owned by the test; no real process anywhere."""

    def __init__(self, returncode=0, alive=False):
        self.stdin = io.StringIO()
        self.stdout = io.StringIO()
        self.stderr = None
        self._returncode = returncode
        self._alive = alive
        self.wait_calls = []

    def poll(self):
        return None if self._alive else self._returncode

    def wait(self, timeout=None):
        self.wait_calls.append(timeout)
        self._alive = False
        return self._returncode


class ExplodingTeardownProc:
    """Delegates I/O and poll to a real child but explodes on reaping, so
    close_session records a cleanup failure with an UNKNOWN child status."""

    def __init__(self, inner):
        self._inner = inner
        self.stdin = inner.stdin
        self.stdout = inner.stdout
        self.stderr = inner.stderr

    def poll(self):
        return self._inner.poll()

    def wait(self, timeout=None):
        raise RuntimeError("reap exploded")

    def terminate(self):
        raise RuntimeError("term exploded")

    def kill(self):
        raise RuntimeError("kill exploded")


class BridgeTestCase(unittest.TestCase):
    """Fresh module per test plus restore of its mutable globals."""

    MUTABLE = ("proc", "session_ended", "session_log", "stderr_log",
               "last_command", "LOG_DIR", "driver_reader", "request_count",
               "STARTUP_TIMEOUT", "REQUEST_TIMEOUT",
               "REAP_WAIT", "TERMINATE_WAIT", "FAIL_DRAIN_WAIT", "FAIL_TERMINATE_WAIT")

    def setUp(self):
        self.bridge = load_bridge()
        snapshot = {name: getattr(self.bridge, name) for name in self.MUTABLE}

        def restore():
            for name, value in snapshot.items():
                setattr(self.bridge, name, value)

        self.addCleanup(restore)
        self.tmp = Path(tempfile.mkdtemp(prefix="mcp-bridge-tests-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.bridge.LOG_DIR = self.tmp

    def patch_child_spawn(self, module, child_code, wrap=None):
        """Route module's Popen to a real local `python3 -c` child.

        The bridge still builds its own pipes and stderr log; the child is a
        plain python process owned by the test (killed/reaped in cleanup).
        The original Popen is captured before patching because module.subprocess
        IS the global subprocess module. `wrap` optionally replaces the child
        object the bridge sees (e.g. a teardown-exploding proxy) while the
        test's holder keeps the real child for cleanup.
        """
        holder = {}
        original_popen = subprocess.Popen

        def fake_popen(cmd, **kwargs):
            real = original_popen([sys.executable, "-c", child_code],
                                  stdin=kwargs["stdin"],
                                  stdout=kwargs["stdout"],
                                  stderr=kwargs["stderr"],
                                  bufsize=0)
            holder["child"] = real
            return wrap(real) if wrap is not None else real

        env_patcher = mock.patch.object(module, "gui_environment",
                                        return_value={"PATH": "/usr/bin"})
        popen_patcher = mock.patch.object(module.subprocess, "Popen",
                                          side_effect=fake_popen)
        env_patcher.start()
        popen_patcher.start()
        self.addCleanup(env_patcher.stop)
        self.addCleanup(popen_patcher.stop)

        def cleanup_child():
            # Fixture teardown (registered at ownership acquisition): close
            # the bridge's owned handles (child stdio + private stderr log)
            # BEFORE the child is killed/reaped and before globals are
            # restored — so no unclosed FileIO is left for GC.
            module.REAP_WAIT = 0.5
            module.TERMINATE_WAIT = 0.5
            try:
                module.close_session()
            except Exception:
                pass
            child = holder.get("child")
            if child is None:
                return
            try:
                if child.poll() is None:
                    child.kill()
                child.wait(timeout=5)
            except Exception:
                pass
            for stream in (child.stdin, child.stdout, getattr(child, "stderr", None)):
                try:
                    if stream and not stream.closed:
                        stream.close()
                except Exception:
                    pass

        self.addCleanup(cleanup_child)
        return holder

    def shorten_waits(self, module):
        module.REAP_WAIT = 0.3
        module.TERMINATE_WAIT = 0.3
        module.FAIL_DRAIN_WAIT = 0.3
        module.FAIL_TERMINATE_WAIT = 0.3

    def run_bridge_main(self, messages):
        """Drive main() with owned in-memory stdin/stdout; never the real loop."""
        stdin_buf = io.BytesIO(b"".join(
            json.dumps(message).encode("utf-8") + b"\n" for message in messages))
        stdout_buf = io.BytesIO()
        fake_stdin = types.SimpleNamespace(buffer=stdin_buf)
        fake_stdout = types.SimpleNamespace(buffer=stdout_buf)
        with mock.patch.object(sys, "stdin", fake_stdin), \
                mock.patch.object(sys, "stdout", fake_stdout):
            self.bridge.main()
        return [json.loads(line)
                for line in stdout_buf.getvalue().splitlines() if line.strip()]


class ExecutableResolutionTests(BridgeTestCase):
    def test_env_override_wins(self):
        fake_dir = Path(tempfile.mkdtemp(prefix="fake-cu-"))
        self.addCleanup(shutil.rmtree, fake_dir, True)
        fake_exec = fake_dir / "cu-fake"
        fake_exec.write_text("#!/bin/sh\nexit 0\n")
        fake_exec.chmod(0o755)
        module = load_bridge({"CU_EXECUTABLE": str(fake_exec)})
        self.assertEqual(module.CU, str(fake_exec))

    def test_default_resolves_to_sibling_cu_py(self):
        expected = os.path.join(
            os.path.dirname(os.path.abspath(str(BRIDGE_PATH))), "cu.py")
        self.assertEqual(self.bridge.CU, expected)

    def test_default_sibling_exists_in_tree(self):
        self.assertTrue(os.path.isfile(self.bridge.CU),
                        "default CU must point at the real sibling cu.py")

    def test_bridge_file_keeps_shebang_and_exec_bit(self):
        mode = stat.S_IMODE(os.stat(BRIDGE_PATH).st_mode)
        self.assertTrue(mode & stat.S_IXUSR,
                        "scripts/mcp_bridge.py must stay executable")
        with open(BRIDGE_PATH, "rb") as stream:
            self.assertTrue(stream.readline().startswith(b"#!"),
                            "shebang must be preserved")


class McpProtocolTests(BridgeTestCase):
    def test_initialize_echoes_protocol_and_server_info(self):
        responses = self.run_bridge_main([
            {"jsonrpc": "2.0", "id": 1, "method": "initialize",
             "params": {"protocolVersion": "2025-06-18"}},
        ])
        self.assertEqual(len(responses), 1)
        self.assertEqual(responses[0]["jsonrpc"], "2.0")
        self.assertEqual(responses[0]["id"], 1)
        result = responses[0]["result"]
        self.assertEqual(result["protocolVersion"], "2025-06-18")
        self.assertEqual(result["serverInfo"]["name"], "computer-use-session")
        self.assertEqual(result["serverInfo"]["version"], "1.0.0")
        self.assertEqual(result["capabilities"], {"tools": {}})

    def test_initialize_default_protocol_version(self):
        responses = self.run_bridge_main([
            {"jsonrpc": "2.0", "id": 7, "method": "initialize", "params": {}},
        ])
        self.assertEqual(responses[0]["result"]["protocolVersion"], "2024-11-05")

    def test_tools_list_structure(self):
        responses = self.run_bridge_main([
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        ])
        tools = responses[0]["result"]["tools"]
        self.assertEqual(len(tools), 1)
        tool = tools[0]
        self.assertEqual(tool["name"], "computer_use_session")
        description = tool["description"]
        self.assertTrue(description.strip())
        for token in ("computer-use session", "request", "finish", "image_policy"):
            self.assertIn(token, description)
        schema = tool["inputSchema"]
        self.assertEqual(schema["type"], "object")
        self.assertEqual(schema["properties"]["operation"]["enum"],
                         ["start", "request", "finish", "status"])
        self.assertEqual(schema["required"], ["operation"])
        self.assertEqual(schema["properties"]["image_policy"]["enum"],
                         ["auto", "always"])

    def test_ping_and_notifications(self):
        responses = self.run_bridge_main([
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 3, "method": "ping"},
            {"jsonrpc": "2.0", "method": "notifications/cancelled"},
        ])
        self.assertEqual(len(responses), 1)
        self.assertEqual(responses[0]["id"], 3)
        self.assertEqual(responses[0]["result"], {})

    def test_unknown_method_returns_error(self):
        responses = self.run_bridge_main([
            {"jsonrpc": "2.0", "id": 4, "method": "does/not/exist"},
        ])
        self.assertEqual(responses[0]["id"], 4)
        self.assertEqual(responses[0]["error"]["code"], -32000)
        self.assertIn("unknown method", responses[0]["error"]["message"])

    def test_tools_call_status_through_mcp_layer(self):
        responses = self.run_bridge_main([
            {"jsonrpc": "2.0", "id": 5, "method": "tools/call",
             "params": {"arguments": {"operation": "status"}}},
        ])
        result = responses[0]["result"]
        self.assertNotIn("isError", result)
        self.assertEqual(result["content"][0]["type"], "text")
        payload = json.loads(result["content"][0]["text"])
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["session_active"])


class InactiveSessionTests(BridgeTestCase):
    def test_status_without_session_reports_inactive(self):
        result = self.bridge.tool_call({"operation": "status"})
        self.assertTrue(result["ok"])
        self.assertFalse(result["session_active"])
        self.assertIsNone(result["session_ended"])
        self.assertIsNone(result["log"])

    def test_finish_without_session_reports_inactive(self):
        result = self.bridge.tool_call({"operation": "finish"})
        self.assertEqual(result, {"ok": True, "session": "inactive",
                                  "already_finished": True, "session_ended": None})
        self.assertIsNone(self.bridge.proc)

    def test_request_without_session_raises(self):
        with self.assertRaises(RuntimeError) as caught:
            self.bridge.tool_call({"operation": "request", "args": ["status"]})
        self.assertIn("no live computer-use session", str(caught.exception))

    def test_status_after_driver_exit(self):
        dead = FakeProc(returncode=3)
        self.bridge.proc = dead
        stderr_log = open(self.tmp / "fake.stderr.log", "w+b")
        self.addCleanup(stderr_log.close)
        stderr_log.write(b"boom\n")
        stderr_log.flush()
        self.bridge.stderr_log = stderr_log
        self.bridge.session_log = self.tmp / "fake.session.log"
        result = self.bridge.tool_call({"operation": "status"})
        self.assertFalse(result["session_active"])
        ended = result["session_ended"]
        self.assertEqual(ended["reason"], "driver exited between requests")
        self.assertEqual(ended["exit_code"], 3)
        self.assertEqual(ended["stderr"], "boom\n")
        self.assertEqual(ended["log"], str(self.tmp / "fake.session.log"))
        self.assertIsNone(self.bridge.proc)
        self.assertTrue(stderr_log.closed)

    def test_finish_after_driver_exit(self):
        dead = FakeProc(returncode=7)
        self.bridge.proc = dead
        result = self.bridge.tool_call({"operation": "finish"})
        self.assertTrue(result["ok"])
        self.assertEqual(result["session"], "inactive")
        self.assertTrue(result["already_finished"])
        self.assertEqual(result["session_ended"]["reason"],
                         "driver exited before finish")
        self.assertEqual(result["session_ended"]["exit_code"], 7)
        self.assertIsNone(self.bridge.proc)


class StartAndValidationTests(BridgeTestCase):
    def make_fake_exec(self):
        fake_dir = Path(tempfile.mkdtemp(prefix="fake-cu-"))
        self.addCleanup(shutil.rmtree, fake_dir, True)
        fake_exec = fake_dir / "cu-fake"
        fake_exec.write_text("#!/bin/sh\nexit 0\n")
        fake_exec.chmod(0o755)
        return fake_exec

    def test_start_uses_resolved_executable(self):
        fake_exec = self.make_fake_exec()
        module = load_bridge({"CU_EXECUTABLE": str(fake_exec)})
        module.LOG_DIR = self.tmp
        read_fd, write_fd = os.pipe()
        os.write(write_fd, b'{"driver": "ready"}\n')
        os.close(write_fd)
        # The transport reads raw bytes: the fixture must be a raw binary
        # stream (what Popen(bufsize=0) would hand the bridge), not text.
        read_file = os.fdopen(read_fd, "rb", buffering=0)
        self.addCleanup(read_file.close)
        fake = FakeProc(returncode=0, alive=True)
        fake.stdout = read_file
        captured = {}

        def fake_popen(cmd, **kwargs):
            captured["cmd"] = cmd
            captured["env"] = kwargs.get("env")
            return fake

        with mock.patch.object(module, "gui_environment",
                               return_value={"PATH": "/usr/bin"}), \
                mock.patch.object(module.subprocess, "Popen",
                                  side_effect=fake_popen):
            result = module.tool_call({"operation": "start"})
        self.addCleanup(module.close_session)
        self.assertTrue(result["ok"])
        self.assertEqual(result["driver"], "ready")
        self.assertEqual(captured["cmd"],
                         [str(fake_exec), "session", "--", str(fake_exec),
                          "session-driver"])
        self.assertEqual(captured["env"], {"PATH": "/usr/bin"})
        self.assertIs(module.proc, fake)

    def test_start_while_active_raises_without_spawning(self):
        alive = FakeProc(returncode=0, alive=True)
        self.bridge.proc = alive
        with self.assertRaises(RuntimeError) as caught:
            self.bridge.tool_call({"operation": "start"})
        self.assertIn("already active", str(caught.exception))
        self.assertIs(self.bridge.proc, alive)
        self.assertEqual(alive.wait_calls, [])

    def test_start_failure_cleans_up_temp_logs(self):
        with mock.patch.object(self.bridge, "gui_environment",
                               side_effect=RuntimeError("no live GUI in test")):
            with self.assertRaises(RuntimeError):
                self.bridge.tool_call({"operation": "start"})
        self.assertIsNone(self.bridge.proc)
        self.assertIsNone(self.bridge.stderr_log)
        self.assertTrue(list(self.tmp.glob("session-*.log")))
        self.assertTrue(list(self.tmp.glob("session-*.stderr.log")))

    def test_request_rejects_bad_arguments(self):
        for bad_args in ([], "observe", [123], ["act", 5]):
            with self.assertRaises(ValueError):
                self.bridge.tool_call({"operation": "request", "args": bad_args})
        for arguments in ({"operation": "request", "args": ["status"], "stdin": 5},
                          {"operation": "request", "args": ["status"],
                           "image_policy": "never"},
                          {"operation": "request", "args": ["reboot"]},
                          {"operation": "explode"}):
            with self.assertRaises(ValueError):
                self.bridge.tool_call(arguments)

    def test_image_paths_finds_png_only(self):
        value = {"result": {"image": "/tmp/a.png",
                            "screens": [{"image": "/tmp/b.png"},
                                        {"image": "/tmp/c.jpg"}]},
                 "session_ended": {"log": "/tmp/log.txt"}}
        self.assertEqual(sorted(self.bridge.image_paths(value)),
                         ["/tmp/a.png", "/tmp/b.png"])


# --- Child programs (real `python3 -c` sources) -----------------------------
# Each speaks the driver's JSON-lines protocol; after the handshake they
# behave differently so each test can force one specific transport failure.

CHILD_EXIT_BEFORE_HANDSHAKE = "import sys\nsys.exit(5)"

CHILD_HANDSHAKE_SLEEP = "import time\ntime.sleep(120)"

CHILD_HANDSHAKE_GARBAGE = (
    "import sys\n"
    "sys.stdout.write('this is not json\\n')\n"
    "sys.stdout.flush()\n"
)

CHILD_HANDSHAKE_NON_OBJECT = (
    "import sys\n"
    "sys.stdout.write('[1, 2]\\n')\n"
    "sys.stdout.flush()\n"
)

CHILD_MALFORMED_RESPONSE = (
    "import sys\n"
    "sys.stdout.write('{\"driver\": \"ready\"}\\n')\n"
    "sys.stdout.flush()\n"
    "sys.stdin.readline()\n"
    "sys.stdout.write('this is not json\\n')\n"
    "sys.stdout.flush()\n"
)

CHILD_NON_OBJECT_RESPONSE = (
    "import sys\n"
    "sys.stdout.write('{\"driver\": \"ready\"}\\n')\n"
    "sys.stdout.flush()\n"
    "sys.stdin.readline()\n"
    "sys.stdout.write('[1, 2]\\n')\n"
    "sys.stdout.flush()\n"
)

CHILD_SILENT_EXIT = (
    "import sys\n"
    "sys.stdout.write('{\"driver\": \"ready\"}\\n')\n"
    "sys.stdout.flush()\n"
    "sys.stdin.readline()\n"
)

CHILD_EOF_MIDLINE = (
    "import sys\n"
    "sys.stdout.write('{\"driver\": \"ready\"}\\n')\n"
    "sys.stdout.flush()\n"
    "sys.stdin.readline()\n"
    "sys.stdout.write('{\"returnc')\n"
    "sys.stdout.flush()\n"
)

CHILD_STALL_PARTIAL = (
    "import sys, time\n"
    "sys.stdout.write('{\"driver\": \"ready\"}\\n')\n"
    "sys.stdout.flush()\n"
    "sys.stdin.readline()\n"
    "sys.stdout.write('{\"retu')\n"
    "sys.stdout.flush()\n"
    "time.sleep(120)\n"
)

CHILD_ECHO = (
    "import json, sys\n"
    "out = sys.stdout\n"
    "out.write(json.dumps({'driver': 'ready'}) + '\\n')\n"
    "out.flush()\n"
    "for line in sys.stdin:\n"
    "    request = json.loads(line)\n"
    "    if request.get('args') == ['finish']:\n"
    "        out.write(json.dumps({'ok': True, 'driver': 'finished'}) + '\\n')\n"
    "        out.flush()\n"
    "        break\n"
    "    out.write(json.dumps({'returncode': 0, 'result': "
    "{'echo': request.get('stdin', '')}, 'session_continues': True}) + '\\n')\n"
    "    out.flush()\n"
)

CHILD_STALL = (
    "import sys, time\n"
    "sys.stdout.write('{\"driver\": \"ready\"}\\n')\n"
    "sys.stdout.flush()\n"
    "time.sleep(120)\n"
)

CHILD_DIE_AFTER_READY = (
    "import sys\n"
    "sys.stdout.write('{\"driver\": \"ready\"}\\n')\n"
    "sys.stdout.flush()\n"
    "sys.exit(4)\n"
)

CHILD_MISMATCH = (
    "import json, sys\n"
    "sys.stdout.write('{\"driver\": \"ready\"}\\n')\n"
    "sys.stdout.flush()\n"
    "sys.stdin.readline()\n"
    "response = {'returncode': 3, 'result': {'ok': False},\n"
    "            'session_continues': False,\n"
    "            'session_ended': {'exit_code': 3, 'reason': 'command failed'}}\n"
    "sys.stdout.write(json.dumps(response) + '\\n')\n"
    "sys.stdout.flush()\n"
    "sys.exit(7)\n"
)

CHILD_STDERR_DEATH = (
    "import sys\n"
    "sys.stdout.write('{\"driver\": \"ready\"}\\n')\n"
    "sys.stdout.flush()\n"
    "sys.stdin.readline()\n"
    "sys.stderr.write('child boom\\n')\n"
    "sys.stdout.write('{\"returnc')\n"
    "sys.stdout.flush()\n"
    "sys.exit(9)\n"
)

# Receipt child (C4): appends one 'request-N' line to $MCP_TEST_RECEIPT each
# time it actually READS a request line, so a hidden resend inside the
# transport would show up as an extra receipt. It answers with a partial
# response and keeps consuming (never completing) so resends are receipted.
CHILD_COUNTING_PARTIAL = (
    "import os, sys, time\n"
    "receipt = os.environ['MCP_TEST_RECEIPT']\n"
    "count = 0\n"
    "def note():\n"
    "    global count\n"
    "    count += 1\n"
    "    with open(receipt, 'a', encoding='utf-8') as f:\n"
    "        f.write('request-%d\\n' % count)\n"
    "sys.stdout.write('{\"driver\": \"ready\"}\\n')\n"
    "sys.stdout.flush()\n"
    "note()\n"
    "sys.stdin.readline()\n"
    "note()\n"
    "sys.stdout.write('{\"retu')\n"
    "sys.stdout.flush()\n"
    "while True:\n"
    "    if not sys.stdin.readline():\n"
    "        break\n"
    "    note()\n"
    "time.sleep(120)\n"
)

CHILD_ACK_EXIT = (
    "import json, sys\n"
    "sys.stdout.write('{\"driver\": \"ready\"}\\n')\n"
    "sys.stdout.flush()\n"
    "for line in sys.stdin:\n"
    "    request = json.loads(line)\n"
    "    if request.get('args') == ['finish']:\n"
    "        sys.stdout.write(json.dumps({'ok': True, 'driver': 'finished'}) + '\\n')\n"
    "        sys.stdout.flush()\n"
    "        sys.exit(17)\n"
    "    sys.stdout.write('{\"returncode\": 0, \"result\": {}}\\n')\n"
    "    sys.stdout.flush()\n"
)

CHILD_ACK_STALL = (
    "import json, sys, time\n"
    "sys.stdout.write('{\"driver\": \"ready\"}\\n')\n"
    "sys.stdout.flush()\n"
    "for line in sys.stdin:\n"
    "    request = json.loads(line)\n"
    "    if request.get('args') == ['finish']:\n"
    "        sys.stdout.write(json.dumps({'ok': True, 'driver': 'finished'}) + '\\n')\n"
    "        sys.stdout.flush()\n"
    "        time.sleep(120)\n"
    "    sys.stdout.write('{\"returncode\": 0, \"result\": {}}\\n')\n"
    "    sys.stdout.flush()\n"
)

CHILD_MISMATCH_NO_DETAIL = (
    "import json, sys\n"
    "sys.stdout.write('{\"driver\": \"ready\"}\\n')\n"
    "sys.stdout.flush()\n"
    "sys.stdin.readline()\n"
    "# A valid fatal envelope without session_ended.exit_code: the bridge's\n"
    "# legacy exit_code must fall back to the response's returncode.\n"
    "sys.stdout.write(json.dumps({'returncode': 3, 'result': {'ok': False},\n"
    " 'session_continues': False,\n"
    " 'session_ended': {'reason': 'command failed'}}) + '\\n')\n"
    "sys.stdout.flush()\n"
    "sys.exit(7)\n"
)

# E1: the driver OWNS the continuation decision. These children speak the
# real driver envelope: a top-level boolean `session_continues` per command
# response, plus `session_ended` on fatal commands. The bridge must consume
# THAT decision and never the legacy `recoverable` flag inside result.
CHILD_REFUSAL_CONTINUE = (
    "import json, sys\n"
    "REFUSED = [False]\n"
    "sys.stdout.write('{\"driver\": \"ready\"}\\n')\n"
    "sys.stdout.flush()\n"
    "for line in sys.stdin:\n"
    "    request = json.loads(line)\n"
    "    if request.get('args') == ['finish']:\n"
    "        sys.stdout.write(json.dumps({'ok': True, 'driver': 'finished'}) + '\\n')\n"
    "        sys.stdout.flush()\n"
    "        break\n"
    "    if not REFUSED[0]:\n"
    "        REFUSED[0] = True\n"
    "        sys.stdout.write(json.dumps({'returncode': 1, 'result': "
    "{'ok': False, 'completed': 0, 'recoverable': True, 'error': 'wait ms must be 0..2000'},"
    " 'session_continues': True}) + '\\n')\n"
    "    else:\n"
    "        sys.stdout.write(json.dumps({'returncode': 0, 'result': "
    "{'ok': True, 'echo': 'after-refusal'}, 'session_continues': True}) + '\\n')\n"
    "    sys.stdout.flush()\n"
)

CHILD_FORGED_RECOVERABLE = (
    "import json, sys\n"
    "sys.stdout.write('{\"driver\": \"ready\"}\\n')\n"
    "sys.stdout.flush()\n"
    "sys.stdin.readline()\n"
    "sys.stdout.write(json.dumps({'returncode': 1, 'result': "
    "{'ok': False, 'recoverable': True, 'error': 'forged refusal'}}) + '\\n')\n"
    "sys.stdout.flush()\n"
    "sys.exit(5)\n"
)

CHILD_FATAL_ENVELOPE = (
    "import json, sys\n"
    "sys.stdout.write('{\"driver\": \"ready\"}\\n')\n"
    "sys.stdout.flush()\n"
    "sys.stdin.readline()\n"
    "sys.stdout.write(json.dumps({'returncode': 1, 'result': {'ok': False},"
    " 'session_continues': False,"
    " 'session_ended': {'reason': 'final capture failed: boom', 'exit_code': 1}}) + '\\n')\n"
    "sys.stdout.flush()\n"
    "sys.exit(6)\n"
)

CHILD_INVALID_CONTINUATION = (
    "import json, sys\n"
    "sys.stdout.write('{\"driver\": \"ready\"}\\n')\n"
    "sys.stdout.flush()\n"
    "sys.stdin.readline()\n"
    "sys.stdout.write(json.dumps({'returncode': 1, 'result': "
    "{'ok': False, 'recoverable': True, 'error': 'lying body'},"
    " 'session_continues': 'yes'}) + '\\n')\n"
    "sys.stdout.flush()\n"
    "sys.exit(8)\n"
)

# R06 envelope validation: each child answers EVERY request with one specific
# malformed envelope and keeps reading, so a hidden replay would get another
# answer instead of an ended session.
CHILD_EMPTY_ENVELOPE = (
    "import sys\n"
    "sys.stdout.write('{\"driver\": \"ready\"}\\n')\n"
    "sys.stdout.flush()\n"
    "for line in sys.stdin:\n"
    "    sys.stdout.write('{}\\n')\n"
    "    sys.stdout.flush()\n"
)

CHILD_BOOL_RETURNCODE = (
    "import json, sys\n"
    "sys.stdout.write('{\"driver\": \"ready\"}\\n')\n"
    "sys.stdout.flush()\n"
    "for line in sys.stdin:\n"
    "    sys.stdout.write(json.dumps({'returncode': True, 'result': {},"
    " 'session_continues': True}) + '\\n')\n"
    "    sys.stdout.flush()\n"
)

CHILD_STRING_CONTINUATION = (
    "import json, sys\n"
    "sys.stdout.write('{\"driver\": \"ready\"}\\n')\n"
    "sys.stdout.flush()\n"
    "for line in sys.stdin:\n"
    "    sys.stdout.write(json.dumps({'returncode': 0, 'result': {},"
    " 'session_continues': 'yes'}) + '\\n')\n"
    "    sys.stdout.flush()\n"
)

CHILD_CONTRADICTORY_SUCCESS = (
    "import json, sys\n"
    "sys.stdout.write('{\"driver\": \"ready\"}\\n')\n"
    "sys.stdout.flush()\n"
    "for line in sys.stdin:\n"
    "    sys.stdout.write(json.dumps({'returncode': 0, 'result': {},"
    " 'session_continues': False}) + '\\n')\n"
    "    sys.stdout.flush()\n"
)

# Receipt variant of CHILD_EMPTY_ENVELOPE: appends one 'request-N' line to
# $MCP_TEST_RECEIPT per line actually read, so a hidden resend after the
# protocol failure would show up as request-3.
CHILD_COUNTING_EMPTY = (
    "import os, sys\n"
    "receipt = os.environ['MCP_TEST_RECEIPT']\n"
    "count = 0\n"
    "def note():\n"
    "    global count\n"
    "    count += 1\n"
    "    with open(receipt, 'a', encoding='utf-8') as f:\n"
    "        f.write('request-%d\\n' % count)\n"
    "sys.stdout.write('{\"driver\": \"ready\"}\\n')\n"
    "sys.stdout.flush()\n"
    "note()\n"
    "for line in sys.stdin:\n"
    "    note()\n"
    "    sys.stdout.write('{}\\n')\n"
    "    sys.stdout.flush()\n"
)

# A finish answered with a REGULAR command envelope instead of the finish
# acknowledgement shape: not a recognized finish response.
CHILD_FINISH_REGULAR_ENVELOPE = (
    "import json, sys\n"
    "sys.stdout.write('{\"driver\": \"ready\"}\\n')\n"
    "sys.stdout.flush()\n"
    "for line in sys.stdin:\n"
    "    sys.stdout.write(json.dumps({'returncode': 0, 'result': {},"
    " 'session_continues': True}) + '\\n')\n"
    "    sys.stdout.flush()\n"
)


def wait_until(predicate, timeout=5.0):
    limit = time.monotonic() + timeout
    while time.monotonic() < limit:
        if predicate():
            return True
        time.sleep(0.01)
    return predicate()


class StartFailureTests(BridgeTestCase):
    """B1.6 + P2: startup failure paths close all owned handles, surface the
    origin (transport cause preserved as __cause__) and carry the FINALIZED
    session_ended details (child exit status, bounded stderr tail, log
    paths, cleanup) in the raised message."""

    def assert_start_failure_payload(self, exc):
        """Parse the finalized end record carried by a failed start."""
        prefix = "could not start session: "
        self.assertTrue(str(exc).startswith(prefix),
                        "failed start must carry the formatted end record")
        return json.loads(str(exc)[len(prefix):])

    def finish_start_failure_asserts(self, exc, cause_type=None, child=None):
        ended = self.assert_start_failure_payload(exc)
        if cause_type is not None:
            self.assertIsInstance(exc.__cause__, cause_type)
        if child is not None:
            self.assertIsNotNone(child.poll(), "failed child must be reaped")
            self.assertEqual(ended.get("child_exit_code"), child.poll())
            self.assertIsNone(self.bridge.proc)
            self.assertIsNone(self.bridge.stderr_log)
            self.assertIsNone(self.bridge.driver_reader)
        self.assertTrue(isinstance(ended.get("cleanup"), dict),
                        "cleanup outcome must be finalized in the record")
        self.assertTrue(ended.get("log"), "log path must be present")
        self.assertIsInstance(ended.get("stderr"), str)
        return ended

    def test_popen_failure_closes_handles_and_surfaces_original_cause(self):
        with mock.patch.object(self.bridge, "gui_environment",
                               return_value={"PATH": "/usr/bin"}), \
                mock.patch.object(self.bridge.subprocess, "Popen",
                                  side_effect=OSError("exec boom")):
            with self.assertRaises(OSError) as caught:
                self.bridge.tool_call({"operation": "start"})
        self.assertEqual(str(caught.exception), "exec boom")
        self.assertIsNone(self.bridge.proc)
        self.assertIsNone(self.bridge.stderr_log)
        self.assertIsNone(self.bridge.driver_reader)
        self.assertEqual(self.bridge.session_ended["reason"],
                         "driver process could not be started: exec boom")

    def test_missing_executable_surfaces_filenotfound(self):
        original_popen = subprocess.Popen

        def real_popen(cmd, **kwargs):
            return original_popen(["/nonexistent/cu-missing"],
                                  stdin=kwargs["stdin"],
                                  stdout=kwargs["stdout"],
                                  stderr=kwargs["stderr"],
                                  bufsize=0)
        with mock.patch.object(self.bridge, "gui_environment",
                               return_value={"PATH": "/usr/bin"}), \
                mock.patch.object(self.bridge.subprocess, "Popen",
                                  side_effect=real_popen):
            with self.assertRaises(FileNotFoundError):
                self.bridge.tool_call({"operation": "start"})
        self.assertIsNone(self.bridge.proc)
        self.assertIsNone(self.bridge.stderr_log)
        self.assertIsNone(self.bridge.driver_reader)

    def test_child_exit_before_handshake_surfaces_stream_closed(self):
        holder = self.patch_child_spawn(self.bridge, CHILD_EXIT_BEFORE_HANDSHAKE)
        with self.assertRaises(RuntimeError) as caught:
            self.bridge.tool_call({"operation": "start"})
        self.finish_start_failure_asserts(
            caught.exception, transport.StreamClosedError, holder["child"])
        child = holder["child"]
        self.assertEqual(child.poll(), 5)
        self.assertTrue(self.bridge.session_ended["reason"]
                        .startswith("could not start session"))

    def test_failed_start_jsonrpc_carries_causal_child_details(self):
        # P2 reproduction: a child that refuses startup exits 5 and prints a
        # causal diagnostic on its private stderr; the main JSONRPC layer
        # previously returned only the raw transport message, hiding the
        # cause, exit code and stderr from the failed-start response.
        child_code = ("import sys\n"
                      "sys.stderr.write('guardian refused: cancellation latch active\\n')\n"
                      "sys.exit(5)")
        holder = self.patch_child_spawn(self.bridge, child_code)
        responses = self.run_bridge_main([
            {"jsonrpc": "2.0", "id": 11, "method": "tools/call",
             "params": {"arguments": {"operation": "start"}}},
        ])
        self.assertEqual(responses[0]["id"], 11)
        self.assertIn("error", responses[0], "failed start must be an error")
        error = responses[0]["error"]
        self.assertEqual(error["code"], -32000)
        ended = self.finish_start_failure_asserts(
            RuntimeError(error["message"]), child=holder["child"])
        self.assertIn("guardian refused: cancellation latch active",
                      ended["stderr"], "causal stderr tail must be surfaced")
        self.assertEqual(ended["child_exit_code"], 5)
        self.assertEqual(ended["cleanup"]["child_exit_code"], 5)
        self.assertFalse(ended["cleanup"]["ok"],
                         "nonzero child status is not a clean teardown")

    def test_failed_start_status_and_finish_keep_the_record(self):
        child_code = ("import sys\n"
                      "sys.stderr.write('guardian refused: latch\\n')\n"
                      "sys.exit(5)")
        holder = self.patch_child_spawn(self.bridge, child_code)
        with self.assertRaises(RuntimeError):
            self.bridge.tool_call({"operation": "start"})
        child = holder["child"]
        self.assertIsNotNone(child.poll())
        status = self.bridge.tool_call({"operation": "status"})
        self.assertFalse(status["session_active"])
        ended = status["session_ended"]
        self.assertTrue(ended["reason"].startswith("could not start session"))
        self.assertEqual(ended["child_exit_code"], 5)
        self.assertTrue(ended["cleanup"])
        self.assertEqual(ended["stderr"], "guardian refused: latch\n")
        self.assertTrue(ended["log"])
        finish = self.bridge.tool_call({"operation": "finish"})
        self.assertEqual(finish, {"ok": True, "session": "inactive",
                                  "already_finished": True,
                                  "session_ended": ended})
        # A new start attempt is allowed: the failure never latches the
        # bridge itself.
        self.bridge.session_ended = None

    def test_handshake_timeout_surfaces_original_cause(self):
        self.shorten_waits(self.bridge)
        self.bridge.STARTUP_TIMEOUT = 0.4
        holder = self.patch_child_spawn(self.bridge, CHILD_HANDSHAKE_SLEEP)
        with self.assertRaises(RuntimeError) as caught:
            self.bridge.tool_call({"operation": "start"})
        ended = self.finish_start_failure_asserts(
            caught.exception, transport.ResponseTimeoutError, holder["child"])
        self.assertIn("session startup timed out", ended.get("reason", ""))
        self.assertTrue(ended.get("cleanup", {}).get("escalated"),
                        "stalled child must be escalated to SIGTERM")

    def test_timeout_start_surfaces_late_sigterm_stderr(self):
        # P2 late stderr: a child that is never ready, whose SIGTERM handler
        # writes its real cleanup diagnostic and exits 9 during teardown.
        # The failed-start record must refresh the stderr tail AFTER the reap:
        # marker present, real exit 9, primary timeout reason + cause kept.
        child_code = ("import signal,time,sys\n"
                      "def h(_s,_f):\n"
                      "    sys.stderr.write('guardian cleanup failed\\n');sys.stderr.flush()\n"
                      "    time.sleep(0.2);sys.exit(9)\n"
                      "signal.signal(signal.SIGTERM,h)\n"
                      "time.sleep(120)\n")
        holder = self.patch_child_spawn(self.bridge, child_code)
        self.shorten_waits(self.bridge)
        self.bridge.STARTUP_TIMEOUT = 0.4
        with self.assertRaises(RuntimeError) as caught:
            self.bridge.tool_call({"operation": "start"})
        ended = self.finish_start_failure_asserts(
            caught.exception, transport.ResponseTimeoutError, holder["child"])
        self.assertIn("session startup timed out", ended.get("reason", ""))
        self.assertIn("guardian cleanup failed", ended.get("stderr", ""))
        self.assertEqual(ended.get("child_exit_code"), 9)
        self.assertTrue(ended.get("cleanup", {}).get("escalated"))

    def test_timeout_start_jsonrpc_carries_late_stderr_and_exit(self):
        child_code = ("import signal,time,sys\n"
                      "def h(_s,_f):\n"
                      "    sys.stderr.write('guardian cleanup failed\\n');sys.stderr.flush()\n"
                      "    time.sleep(0.2);sys.exit(9)\n"
                      "signal.signal(signal.SIGTERM,h)\n"
                      "time.sleep(120)\n")
        holder = self.patch_child_spawn(self.bridge, child_code)
        self.shorten_waits(self.bridge)
        self.bridge.STARTUP_TIMEOUT = 0.4
        responses = self.run_bridge_main([
            {"jsonrpc": "2.0", "id": 12, "method": "tools/call",
             "params": {"arguments": {"operation": "start"}}},
        ])
        self.assertIn("error", responses[0])
        ended = self.finish_start_failure_asserts(
            RuntimeError(responses[0]["error"]["message"]),
            child=holder["child"])
        self.assertIn("session startup timed out", ended.get("reason", ""))
        self.assertIn("guardian cleanup failed", ended.get("stderr", ""))
        self.assertEqual(ended.get("child_exit_code"), 9)
        self.assertTrue(ended.get("log"), "log path must be present")

    def test_handshake_garbage_surfaces_original_cause(self):
        holder = self.patch_child_spawn(self.bridge, CHILD_HANDSHAKE_GARBAGE)
        with self.assertRaises(RuntimeError) as caught:
            self.bridge.tool_call({"operation": "start"})
        self.assertIn("not valid JSON", str(caught.exception))
        ended = self.finish_start_failure_asserts(
            caught.exception, transport.MessageError, holder["child"])
        self.assertIn("not valid JSON", ended.get("reason", ""))

    def test_handshake_non_object_surfaces_original_cause(self):
        holder = self.patch_child_spawn(self.bridge, CHILD_HANDSHAKE_NON_OBJECT)
        with self.assertRaises(RuntimeError) as caught:
            self.bridge.tool_call({"operation": "start"})
        self.assertIn("not a JSON object", str(caught.exception))
        self.finish_start_failure_asserts(
            caught.exception, transport.MessageError, holder["child"])

    def test_bad_handshake_payload_retains_payload_cause(self):
        # P2: a bad handshake payload is a failed start too; the original
        # payload must stay in the surfaced details (bounded), not be lost.
        holder = self.patch_child_spawn(
            self.bridge, "print('{\"note\":\"no driver ready here\"}')")
        with self.assertRaises(RuntimeError) as caught:
            self.bridge.tool_call({"operation": "start"})
        ended = self.finish_start_failure_asserts(
            caught.exception, None, holder["child"])
        payload = json.loads(ended["handshake"])
        self.assertEqual(payload, {"note": "no driver ready here"})

    def test_handshake_read_failure_surfaces_original_cause(self):
        class ExplodingStream:
            def __init__(self):
                self.closed = False

            def fileno(self):
                raise io.UnsupportedOperation("not a real stream")

            def read(self, size):
                raise OSError("pipe exploded")

            def close(self):
                self.closed = True

        exploding = ExplodingStream()
        fake = FakeProc(returncode=0, alive=True)
        fake.stdout = exploding
        with mock.patch.object(self.bridge, "gui_environment",
                               return_value={"PATH": "/usr/bin"}), \
                mock.patch.object(self.bridge.subprocess, "Popen",
                                  return_value=fake):
            with self.assertRaises(RuntimeError) as caught:
                self.bridge.tool_call({"operation": "start"})
        self.assertIn("pipe exploded", str(caught.exception))
        self.assertIsInstance(caught.exception.__cause__, OSError)
        self.assertIsNone(self.bridge.proc)
        self.assertTrue(exploding.closed, "owned stdout must be closed once")
        ended = self.assert_start_failure_payload(caught.exception)
        self.assertIn("pipe exploded", ended.get("reason", ""))
        self.assertTrue(ended.get("log"))


class ResponseFramingTests(BridgeTestCase):
    """B1.4/B1.5 through the bridge request path with real owned children."""

    def request_failure(self, module, child_code, timeout=None):
        holder = self.patch_child_spawn(module, child_code)
        module.tool_call({"operation": "start"})
        if timeout is not None:
            module.REQUEST_TIMEOUT = timeout
            self.shorten_waits(module)
        with self.assertRaises(RuntimeError) as caught:
            module.tool_call({"operation": "request", "args": ["status"]})
        return caught.exception, holder["child"]

    def test_malformed_json_response_ends_session_truthfully(self):
        error, child = self.request_failure(self.bridge, CHILD_MALFORMED_RESPONSE)
        self.assertIn("not valid JSON", str(error))
        self.assertEqual(self.bridge.request_count, 1)
        self.assertIsNotNone(child.poll(), "child must be reaped")
        self.assertIsNone(self.bridge.proc)
        self.assertIsNone(self.bridge.stderr_log)
        self.assertIn("not valid JSON", self.bridge.session_ended["reason"])

    def test_non_object_response_ends_session_truthfully(self):
        error, child = self.request_failure(self.bridge, CHILD_NON_OBJECT_RESPONSE)
        self.assertIn("not a JSON object", str(error))
        self.assertEqual(self.bridge.request_count, 1)
        self.assertIsNotNone(child.poll())
        self.assertIsNone(self.bridge.proc)
        self.assertIn("not a JSON object", self.bridge.session_ended["reason"])

    def test_eof_before_response_ends_session(self):
        error, child = self.request_failure(self.bridge, CHILD_SILENT_EXIT)
        self.assertIn("closed before a complete line", str(error))
        self.assertEqual(self.bridge.request_count, 1)
        self.assertIsNotNone(child.poll())
        self.assertIsNone(self.bridge.proc)

    def test_eof_midline_ends_session(self):
        error, child = self.request_failure(self.bridge, CHILD_EOF_MIDLINE)
        self.assertIn("mid-line", str(error))
        self.assertEqual(self.bridge.request_count, 1)
        self.assertIsNotNone(child.poll())
        self.assertIsNone(self.bridge.proc)
        self.assertEqual(self.bridge.session_ended["child_exit_code"], 0)

    def test_partial_line_then_stall_hits_request_deadline(self):
        error, child = self.request_failure(self.bridge, CHILD_STALL_PARTIAL,
                                            timeout=0.6)
        self.assertIn("no complete line", str(error))
        self.assertEqual(self.bridge.request_count, 1)
        self.assertIsNotNone(child.poll(), "stalled child must be reaped")
        self.assertIsNone(self.bridge.proc)
        self.assertIsNone(self.bridge.stderr_log)


class SessionCleanupTests(BridgeTestCase):
    """B1.1: stream ownership — the bridge closes each borrowed stream
    exactly once, through the object, at teardown."""

    def test_close_session_closes_each_stream_exactly_once(self):
        class CloseCounting:
            def __init__(self, inner):
                self.inner = inner
                self.close_calls = 0

            def read(self, size):
                return self.inner.read(size)

            def write(self, data):
                return self.inner.write(data)

            def flush(self):
                return self.inner.flush()

            def fileno(self):
                return self.inner.fileno()

            @property
            def closed(self):
                return self.inner.closed

            def close(self):
                self.close_calls += 1
                self.inner.close()

        stdin = CloseCounting(io.StringIO())
        stdout = CloseCounting(ScriptedBytesStream(b'{"a": 1}\n'))
        fake = FakeProc(returncode=0, alive=True)
        fake.stdin = stdin
        fake.stdout = stdout
        self.bridge.proc = fake
        self.bridge.driver_reader = transport.LineReader(stdout, timeout=5.0)
        self.bridge.close_session()
        self.bridge.close_session()  # teardown is idempotent
        self.assertEqual(stdin.close_calls, 1)
        self.assertEqual(stdout.close_calls, 1)
        self.assertIsNone(self.bridge.proc)
        self.assertIsNone(self.bridge.driver_reader)

    def test_reader_borrows_bridge_stream_until_teardown(self):
        # The reader retains the live stdout object across requests; the
        # bridge closes it exactly once at teardown, never the reader.
        read_fd, write_fd = os.pipe()
        stdout = os.fdopen(read_fd, "rb", buffering=0)
        self.addCleanup(stdout.close)
        os.write(write_fd, b'{"returncode": 0, "result": {"ok": true},'
                          b' "session_continues": true}\n')
        os.close(write_fd)
        fake = FakeProc(returncode=0, alive=True)
        fake.stdout = stdout
        fake.stdin = io.BytesIO()  # the bridge writes raw bytes to the driver
        self.bridge.proc = fake
        self.bridge.driver_reader = transport.LineReader(stdout, timeout=5.0)
        result = self.bridge.tool_call({"operation": "request",
                                        "args": ["status"]})
        self.assertEqual(result["result"], {"ok": True})
        borrowed = self.bridge.driver_reader.stream
        self.assertIs(borrowed, stdout)
        self.assertFalse(borrowed.closed)
        self.bridge.close_session()
        self.assertTrue(borrowed.closed)


class BoundedRequestTests(BridgeTestCase):
    """B2.1/B2.2/B2.3: bounded writes, 8 MiB pre-write validation, one send
    attempt per command."""

    def make_active_fake_session(self):
        fake = FakeProc(returncode=0, alive=True)
        fake.stdin = io.BytesIO()
        fake.stdout = ScriptedBytesStream(b'')
        self.bridge.proc = fake
        self.bridge.driver_reader = transport.LineReader(fake.stdout, timeout=5.0)
        return fake

    def test_oversize_request_refused_before_writing(self):
        fake = self.make_active_fake_session()
        data = "x" * (8 * 1024 * 1024)  # payload will exceed the 8 MiB line
        with self.assertRaises(ValueError) as caught:
            self.bridge.tool_call({"operation": "request", "args": ["status"],
                                   "stdin": data})
        self.assertIn("8 MiB", str(caught.exception))
        # Nothing was written, nothing is uncertain: session stays usable.
        self.assertEqual(self.bridge.request_count, 0)
        self.assertEqual(fake.stdin.getvalue(), b"")
        self.assertFalse(fake.stdin.closed)
        self.assertIs(self.bridge.proc, fake)
        self.assertIsNotNone(self.bridge.driver_reader)

    def test_request_at_exact_limit_is_written(self):
        holder = self.patch_child_spawn(self.bridge, CHILD_ECHO)
        self.bridge.tool_call({"operation": "start"})
        base = json.dumps({"args": ["status"], "stdin": "", "image_policy": "auto"},
                          ensure_ascii=False)
        filler = self.bridge.REQUEST_LINE_LIMIT - len(base.encode("utf-8")) - 1
        data = "x" * filler  # serialized request line lands exactly on 8 MiB
        result = self.bridge.tool_call({"operation": "request", "args": ["status"],
                                        "stdin": data})
        self.assertEqual(result["returncode"], 0)
        self.assertEqual(result["result"]["echo"], data)
        self.assertEqual(self.bridge.request_count, 1)
        # The session survives a request at exactly the limit.
        self.assertIsNone(holder["child"].poll())
        self.assertIsNotNone(self.bridge.proc)

    def test_stalled_child_write_hits_deadline(self):
        receipt = self.tmp / "receipt.log"
        receipt.touch()  # owned temp artifact for the child's read receipts
        with mock.patch.dict(os.environ, {"MCP_TEST_RECEIPT": str(receipt)}):
            holder = self.patch_child_spawn(self.bridge, CHILD_STALL)
            self.bridge.tool_call({"operation": "start"})
            self.bridge.REQUEST_TIMEOUT = 0.6
            self.shorten_waits(self.bridge)
            with self.assertRaises(RuntimeError) as caught:
                self.bridge.tool_call({"operation": "request", "args": ["status"],
                                       "stdin": "x" * 200000})
        self.assertIn("bytes sent", str(caught.exception))
        self.assertEqual(self.bridge.request_count, 1)
        self.assertIsNotNone(holder["child"].poll(), "stalled child must be reaped")
        self.assertIsNone(self.bridge.proc)
        self.assertIsNone(self.bridge.stderr_log)
        # The stalled child never READ a single request line: the write never
        # completed, so no request was received at all.
        self.assertEqual(receipt.read_text(encoding="utf-8"), "")

    def test_partial_output_receipts_exactly_one_request(self):
        receipt = self.tmp / "receipt.log"
        with mock.patch.dict(os.environ, {"MCP_TEST_RECEIPT": str(receipt)}):
            holder = self.patch_child_spawn(self.bridge, CHILD_COUNTING_PARTIAL)
            self.bridge.tool_call({"operation": "start"})
            self.bridge.REQUEST_TIMEOUT = 0.6
            self.shorten_waits(self.bridge)
            with self.assertRaises(RuntimeError):
                self.bridge.tool_call({"operation": "request", "args": ["status"]})
        # request-1 is the handshake accounting line; exactly ONE driver
        # request (request-2) was received — a resend inside the transport
        # would have produced request-3 in the receipt.
        self.assertEqual(receipt.read_text(encoding="utf-8").splitlines(),
                         ["request-1", "request-2"])
        self.assertEqual(self.bridge.request_count, 1)
        self.assertIsNotNone(holder["child"].poll())
        self.assertIsNone(self.bridge.proc)


class FinishSemanticsTests(BridgeTestCase):
    """B2.5: finish is a successful no-op only for an already inactive/dead
    session (retaining its details) or a completed clean finish; an active
    finish failure stays an error and never erases a failure record."""

    def test_clean_finish_twice(self):
        holder = self.patch_child_spawn(self.bridge, CHILD_ECHO)
        self.bridge.tool_call({"operation": "start"})
        first = self.bridge.tool_call({"operation": "request", "args": ["status"]})
        self.assertEqual(first["returncode"], 0)
        finish = self.bridge.tool_call({"operation": "finish"})
        self.assertTrue(finish["ok"])
        self.assertEqual(finish["driver"], "finished")
        again = self.bridge.tool_call({"operation": "finish"})
        self.assertEqual(again, {"ok": True, "session": "inactive",
                                 "already_finished": True, "session_ended": None})
        self.assertIsNone(self.bridge.proc)
        self.assertIsNone(self.bridge.session_ended)
        self.assertIsNotNone(holder["child"].poll(), "child must be reaped")

    def test_ack_then_nonzero_child_exit_is_not_a_clean_finish(self):
        holder = self.patch_child_spawn(self.bridge, CHILD_ACK_EXIT)
        self.bridge.tool_call({"operation": "start"})
        result = self.bridge.tool_call({"operation": "finish"})
        # The driver ACKed, but the reaped child exited 17: the finish must
        # NOT be a success, and BOTH facts stay visible.
        self.assertFalse(result["ok"])
        self.assertEqual(result["driver"], "finished")  # ACK kept visible
        self.assertEqual(result["returncode"], 17)      # real child exit status
        self.assertEqual(result["cleanup"]["child_exit_code"], 17)
        self.assertFalse(result["cleanup"]["ok"])
        self.assertTrue(result["cleanup"]["errors"] == [])
        self.assertFalse(result["cleanup"]["escalated"])
        ended = result.get("session_ended")
        self.assertIsNotNone(ended)
        self.assertEqual(ended["child_exit_code"], 17)
        self.assertIsNone(self.bridge.proc)
        self.assertIsNotNone(holder["child"].poll())

    def test_ack_then_cleanup_failure_is_not_a_clean_finish(self):
        holder = self.patch_child_spawn(self.bridge, CHILD_ACK_STALL)
        self.bridge.tool_call({"operation": "start"})
        real_child = holder["child"]

        class ExplodingTeardownProc:
            """Delegates I/O to the real child but explodes on reaping."""

            def __init__(self, inner):
                self._inner = inner
                self.stdin = inner.stdin
                self.stdout = inner.stdout
                self.stderr = inner.stderr

            def poll(self):
                return self._inner.poll()

            def wait(self, timeout=None):
                raise RuntimeError("reap exploded")

            def terminate(self):
                raise RuntimeError("term exploded")

            def kill(self):
                raise RuntimeError("kill exploded")

        self.bridge.proc = ExplodingTeardownProc(real_child)
        result = self.bridge.tool_call({"operation": "finish"})
        # ACK visible AND cleanup failure visible; neither masks the other.
        self.assertFalse(result["ok"])
        self.assertEqual(result["driver"], "finished")
        cleanup = result["cleanup"]
        self.assertFalse(cleanup["ok"])
        self.assertTrue(cleanup["escalated"])
        self.assertTrue(any("term exploded" in err for err in cleanup["errors"]),
                        cleanup["errors"])
        ended = result["session_ended"]
        self.assertIn("teardown did not confirm clean", ended["reason"])
        self.assertIsNone(self.bridge.proc)
        # The real child survives the broken proxy teardown; the fixture
        # cleanup below still kills and reaps it.
        try:
            if real_child.poll() is None:
                real_child.kill()
            real_child.wait(timeout=5)
        except Exception:
            pass

    def test_active_finish_timeout_stays_error(self):
        holder = self.patch_child_spawn(self.bridge, CHILD_STALL)
        self.bridge.tool_call({"operation": "start"})
        self.bridge.REQUEST_TIMEOUT = 0.5
        self.shorten_waits(self.bridge)
        with self.assertRaises(RuntimeError) as caught:
            self.bridge.tool_call({"operation": "finish"})
        self.assertIn("no complete line", str(caught.exception))
        # The failure path made the session inactive, but the finish result
        # must remain an error, not a converted success.
        self.assertIsNone(self.bridge.proc)
        self.assertEqual(self.bridge.request_count, 1)
        self.assertIsNotNone(holder["child"].poll())

    def test_finish_when_driver_already_dead_is_inactive_success(self):
        holder = self.patch_child_spawn(self.bridge, CHILD_DIE_AFTER_READY)
        self.bridge.tool_call({"operation": "start"})
        child = holder["child"]
        self.assertTrue(wait_until(lambda: child.poll() is not None),
                        "child should exit right after the handshake")
        result = self.bridge.tool_call({"operation": "finish"})
        self.assertTrue(result["ok"])
        self.assertEqual(result["session"], "inactive")
        self.assertTrue(result["already_finished"])
        ended = result["session_ended"]
        self.assertEqual(ended["reason"], "driver exited before finish")
        self.assertEqual(ended["exit_code"], 4)
        self.assertEqual(ended["child_exit_code"], 4)
        self.assertIsNone(self.bridge.proc)

    def test_finish_when_driver_dies_between_checks_is_inactive_success(self):
        # poll() flips to a real exit code only after the first call, so the
        # driver dies between finish's liveness check and session_call's.
        flaky = FakeProc(returncode=2, alive=True)
        flaky.stdin = io.BytesIO()
        flaky.stdout = ScriptedBytesStream(b'')
        calls = {"n": 0}

        def poll_then_die():
            calls["n"] += 1
            return 2 if calls["n"] > 1 else None

        flaky.poll = poll_then_die
        self.bridge.proc = flaky
        self.bridge.driver_reader = transport.LineReader(flaky.stdout, timeout=5.0)
        result = self.bridge.tool_call({"operation": "finish"})
        self.assertTrue(result["ok"])
        self.assertTrue(result["already_finished"])
        ended = result["session_ended"]
        self.assertEqual(ended["reason"], "driver exited between requests")
        self.assertEqual(ended["exit_code"], 2)
        self.assertIsNone(self.bridge.proc)

    def test_repeated_finish_keeps_failure_record(self):
        holder = self.patch_child_spawn(self.bridge, CHILD_STDERR_DEATH)
        self.bridge.tool_call({"operation": "start"})
        self.shorten_waits(self.bridge)
        with self.assertRaises(RuntimeError):
            self.bridge.tool_call({"operation": "request", "args": ["status"]})
        record = self.bridge.session_ended
        self.assertIsNotNone(record)
        result = self.bridge.tool_call({"operation": "finish"})
        self.assertTrue(result["ok"])
        self.assertTrue(result["already_finished"])
        # The repeated finish returned the PRECEDING failure record untouched.
        self.assertIs(result["session_ended"], record)
        self.assertEqual(record["reason"], self.bridge.session_ended["reason"])


class CleanupTruthTests(BridgeTestCase):
    """B2.3/B2.4: terminate+reap on uncertain outcomes, command code vs child
    code distinction, original reason surviving cleanup failures."""

    def test_cleanup_failure_keeps_original_reason(self):
        class RebelProc(FakeProc):
            def terminate(self):
                raise RuntimeError("term exploded")

            def kill(self):
                raise RuntimeError("kill exploded")

            def wait(self, timeout=None):
                raise RuntimeError("reap exploded")

        fake = RebelProc(returncode=0, alive=True)
        fake.stdin = io.BytesIO()
        fake.stdout = ScriptedBytesStream(b'')  # immediate EOF
        self.bridge.proc = fake
        self.bridge.driver_reader = transport.LineReader(fake.stdout, timeout=5.0)
        with self.assertRaises(RuntimeError) as caught:
            self.bridge.tool_call({"operation": "request", "args": ["status"]})
        message = str(caught.exception)
        self.assertIn("closed before a complete line", message)
        # Both facts survive: the primary reason AND the secondary cleanup
        # errors — neither masks the other.
        self.assertIn("term exploded", message)
        self.assertEqual(self.bridge.request_count, 1)
        self.assertTrue(fake.stdin.closed)
        self.assertTrue(fake.stdout.closed)
        self.assertIsNone(self.bridge.proc)

    def test_command_code_differs_from_child_exit_code(self):
        holder = self.patch_child_spawn(self.bridge, CHILD_MISMATCH)
        self.bridge.tool_call({"operation": "start"})
        result = self.bridge.tool_call({"operation": "request", "args": ["status"]})
        ended = result["session_ended"]
        self.assertEqual(result["returncode"], 3)
        self.assertEqual(ended["exit_code"], 3)          # legacy: command code
        self.assertEqual(ended["command_exit_code"], 3)  # driver-reported
        self.assertEqual(ended["child_exit_code"], 7)    # reaped child status
        self.assertNotEqual(ended["exit_code"], ended["child_exit_code"])
        self.assertIsNotNone(holder["child"].poll())
        self.assertEqual(holder["child"].poll(), 7)
        self.assertIsNone(self.bridge.proc)

    def test_command_code_falls_back_to_returncode_without_detail(self):
        # The driver reported no session_ended.exit_code: the legacy field
        # must fall back to the response's returncode (command code 3), and
        # stay distinct from the reaped child's own exit status (7).
        holder = self.patch_child_spawn(self.bridge, CHILD_MISMATCH_NO_DETAIL)
        self.bridge.tool_call({"operation": "start"})
        result = self.bridge.tool_call({"operation": "request", "args": ["status"]})
        ended = result["session_ended"]
        self.assertEqual(result["returncode"], 3)
        self.assertEqual(ended["exit_code"], 3)
        self.assertEqual(ended["command_exit_code"], 3)
        self.assertEqual(ended["child_exit_code"], 7)
        self.assertNotEqual(ended["exit_code"], ended["child_exit_code"])
        self.assertIsNone(self.bridge.proc)

    def test_last_end_log_matches_response(self):
        holder = self.patch_child_spawn(self.bridge, CHILD_MISMATCH)
        self.bridge.tool_call({"operation": "start"})
        result = self.bridge.tool_call({"operation": "request", "args": ["status"]})
        ended = result["session_ended"]
        log_path = Path(ended["log"])
        events = [json.loads(line)
                  for line in log_path.read_text(encoding="utf-8").splitlines()
                  if line.strip()]
        end_events = [event["session_ended"] for event in events
                      if "session_ended" in event]
        self.assertTrue(end_events, "session log must contain end events")
        last = end_events[-1]
        # The FINAL appended record matches the response exactly: primary
        # reason, command code, real child status and cleanup outcome.
        self.assertEqual(last["reason"], ended["reason"])
        self.assertEqual(last["exit_code"], ended["exit_code"])
        self.assertEqual(last["command_exit_code"], ended["command_exit_code"])
        self.assertEqual(last["child_exit_code"], ended["child_exit_code"])
        self.assertEqual(last.get("cleanup", {}).get("child_exit_code"), 7)

    def test_failure_metadata_retained_after_closure(self):
        holder = self.patch_child_spawn(self.bridge, CHILD_STDERR_DEATH)
        self.bridge.tool_call({"operation": "start"})
        self.shorten_waits(self.bridge)
        with self.assertRaises(RuntimeError):
            self.bridge.tool_call({"operation": "request", "args": ["status"]})
        ended = self.bridge.session_ended
        self.assertIn("mid-line", ended["reason"])
        self.assertIn("child boom", ended["stderr"])
        self.assertEqual(ended["child_exit_code"], 9)
        self.assertTrue(Path(ended["log"]).exists())
        self.assertEqual(self.bridge.request_count, 1)
        # A later status still reports the same record.
        status = self.bridge.tool_call({"operation": "status"})
        self.assertEqual(status["session_ended"]["reason"], ended["reason"])
        self.assertIn("child boom", status["session_ended"]["stderr"])


class ContinuationEnvelopeTests(BridgeTestCase):
    """E1: the bridge consumes the DRIVER's top-level `session_continues`
    decision for failed commands; backend `recoverable` flags and missing
    metadata never keep a session alive (fail-closed)."""

    def test_driver_continuation_keeps_session_after_failed_command(self):
        holder = self.patch_child_spawn(self.bridge, CHILD_REFUSAL_CONTINUE)
        self.bridge.tool_call({"operation": "start"})
        refused = self.bridge.tool_call({"operation": "request",
                                         "args": ["act"], "stdin": "[]"})
        # The refusal envelope passes through with the driver's decision.
        self.assertEqual(refused["returncode"], 1)
        self.assertIs(refused["session_continues"], True)
        self.assertTrue(refused["result"]["recoverable"],
                        "legacy body field stays visible, never decisive")
        # The session is still alive: the next command really runs.
        followup = self.bridge.tool_call({"operation": "request",
                                          "args": ["status"]})
        self.assertEqual(followup["returncode"], 0)
        self.assertEqual(followup["result"]["echo"], "after-refusal")
        self.assertIsNone(self.bridge.session_ended)
        self.assertIsNone(holder["child"].poll(), "child must survive a refusal")
        # A clean finish still works after a continued refusal.
        finish = self.bridge.tool_call({"operation": "finish"})
        self.assertTrue(finish["ok"])
        self.assertEqual(self.bridge.request_count, 3)
        self.assertIsNotNone(holder["child"].poll())

    def test_forged_backend_recoverable_without_metadata_ends_session(self):
        holder = self.patch_child_spawn(self.bridge, CHILD_FORGED_RECOVERABLE)
        self.bridge.tool_call({"operation": "start"})
        # R06: missing response metadata is a protocol failure — the envelope
        # cannot be trusted at all, so neither the forged flag nor its body
        # supplies the reason. Fail-closed, reaped, never replayed.
        with self.assertRaises(RuntimeError) as caught:
            self.bridge.tool_call({"operation": "request", "args": ["act"],
                                   "stdin": "[]"})
        message = str(caught.exception)
        self.assertIn("computer-use session ended", message)
        self.assertIn("boolean session_continues", message)
        self.assertNotIn("forged refusal", message,
                         "an untrusted envelope must not supply the reason")
        self.assertEqual(self.bridge.request_count, 1)
        self.assertIsNotNone(holder["child"].poll(), "child must be reaped")
        self.assertIsNone(self.bridge.proc)
        self.assertIn("boolean session_continues",
                      self.bridge.session_ended["reason"])

    def test_invalid_continuation_type_ends_session_fail_closed(self):
        holder = self.patch_child_spawn(self.bridge, CHILD_INVALID_CONTINUATION)
        self.bridge.tool_call({"operation": "start"})
        # R06: a non-boolean session_continues is a protocol failure, not a
        # command result — the whole envelope is untrusted.
        with self.assertRaises(RuntimeError) as caught:
            self.bridge.tool_call({"operation": "request", "args": ["act"],
                                   "stdin": "[]"})
        message = str(caught.exception)
        self.assertIn("computer-use session ended", message)
        self.assertIn("boolean session_continues", message)
        self.assertNotIn("lying body", message,
                         "an untrusted envelope must not supply the reason")
        self.assertEqual(self.bridge.request_count, 1)
        self.assertIsNotNone(holder["child"].poll())
        self.assertIsNone(self.bridge.proc)

    def test_driver_fatal_envelope_fields_are_surfaced(self):
        holder = self.patch_child_spawn(self.bridge, CHILD_FATAL_ENVELOPE)
        self.bridge.tool_call({"operation": "start"})
        result = self.bridge.tool_call({"operation": "request", "args": ["act"],
                                        "stdin": "[]"})
        self.assertEqual(result["returncode"], 1)
        ended = result["session_ended"]
        self.assertEqual(ended["reason"], "final capture failed: boom")
        self.assertEqual(ended["exit_code"], 1, "driver command exit code")
        self.assertEqual(ended["command_exit_code"], 1)
        self.assertEqual(ended["child_exit_code"], 6, "real child status kept distinct")
        self.assertEqual(ended["last_command"], "act")
        self.assertIsNotNone(holder["child"].poll())
        self.assertIsNone(self.bridge.proc)


class McpMainFramingTests(BridgeTestCase):
    """R06 fixes exercised through the ACTUAL main() JSON-RPC framing:
    initialize plus tools/call lines are fed through main()'s stdin/stdout
    while the driver is a real local child speaking the JSON-lines protocol."""

    def run_main_calls(self, calls):
        """Feed initialize + one tools/call per entry through main()."""
        messages = [{"jsonrpc": "2.0", "id": 1, "method": "initialize",
                     "params": {"protocolVersion": "2024-11-05"}}]
        for index, arguments in enumerate(calls, start=2):
            messages.append({"jsonrpc": "2.0", "id": index,
                             "method": "tools/call",
                             "params": {"arguments": arguments}})
        stdin_buf = io.BytesIO(b"".join(
            json.dumps(message).encode("utf-8") + b"\n" for message in messages))
        stdout_buf = io.BytesIO()
        fake_stdin = types.SimpleNamespace(buffer=stdin_buf)
        fake_stdout = types.SimpleNamespace(buffer=stdout_buf)
        with mock.patch.object(sys, "stdin", fake_stdin), \
                mock.patch.object(sys, "stdout", fake_stdout):
            self.bridge.main()
        return [json.loads(line)
                for line in stdout_buf.getvalue().splitlines() if line.strip()]

    def payload(self, response):
        return json.loads(response["result"]["content"][0]["text"])


class McpIsErrorFramingTests(McpMainFramingTests):
    """R06 fix 1: a failing tool result must be framed with isError:true in
    the MCP tools/call response, while an inactive/repeated finish stays a
    successful no-op even when historical death details remain in its
    payload."""

    def test_finish_cleanup_failure_is_error_result(self):
        self.patch_child_spawn(self.bridge, CHILD_ACK_EXIT)
        responses = self.run_main_calls([
            {"operation": "start"},
            {"operation": "finish"},
        ])
        self.assertNotIn("isError", responses[1]["result"], "start is a success")
        self.assertNotIn("error", responses[1])
        finish = responses[2]["result"]
        self.assertIs(finish.get("isError"), True,
                      "a finish that did not confirm clean is an error result")
        payload = self.payload(responses[2])
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["returncode"], 17)
        self.assertEqual(payload["cleanup"]["child_exit_code"], 17)

    def test_finish_cleanup_failure_with_unknown_exit_is_error_result(self):
        # THE reported defect: ok:false from a cleanup failure whose child
        # status stays UNKNOWN sets no returncode, so main() used to frame
        # the failure as a SUCCESSFUL tool call. The teardown proxy explodes
        # from spawn time (start never waits; finish's reap does).
        holder = self.patch_child_spawn(self.bridge, CHILD_ACK_STALL,
                                        wrap=ExplodingTeardownProc)
        responses = self.run_main_calls([
            {"operation": "start"},
            {"operation": "finish"},
        ])
        real_child = holder["child"]
        self.assertNotIn("error", responses[1], "start must succeed")
        finish = responses[2]["result"]
        self.assertIs(finish.get("isError"), True,
                      "cleanup failure with unknown exit must be an error result")
        payload = self.payload(responses[2])
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["driver"], "finished")  # ACK stays visible
        self.assertNotIn("returncode", payload, "child status is unknown")
        self.assertFalse(payload["cleanup"]["ok"])
        self.assertTrue(payload["cleanup"]["escalated"])
        self.assertIsNone(self.bridge.proc)
        # The proxy blocked the bridge's teardown, so the real child must be
        # stopped here before the fixture cleanup runs.
        try:
            if real_child.poll() is None:
                real_child.kill()
            real_child.wait(timeout=5)
        except Exception:
            pass

    def test_request_failure_is_error_result(self):
        self.patch_child_spawn(self.bridge, CHILD_MISMATCH)
        responses = self.run_main_calls([
            {"operation": "start"},
            {"operation": "request", "args": ["status"]},
        ])
        self.assertNotIn("error", responses[2],
                         "a failed command is a result with isError, not a JSON-RPC error")
        request = responses[2]["result"]
        self.assertIs(request.get("isError"), True)
        payload = self.payload(responses[2])
        self.assertEqual(payload["returncode"], 3)
        self.assertEqual(payload["session_ended"]["reason"], "command failed")

    def test_inactive_and_repeated_finish_stay_successful_no_ops(self):
        # A dead session with historical death details: finish (and its
        # repeat) must remain successful no-ops — isError stays absent even
        # though the payload carries the death record and a failed cleanup.
        dead = FakeProc(returncode=4)
        self.bridge.proc = dead
        self.bridge.session_log = self.tmp / "already-ended.log"
        responses = self.run_main_calls([
            {"operation": "finish"},
            {"operation": "finish"},
        ])
        for index in (1, 2):
            self.assertNotIn("isError", responses[index]["result"])
            self.assertNotIn("error", responses[index])
        first = self.payload(responses[1])
        self.assertTrue(first["ok"])
        self.assertTrue(first["already_finished"])
        self.assertEqual(first["session_ended"]["reason"],
                         "driver exited before finish")
        again = self.payload(responses[2])
        self.assertTrue(again["ok"])
        self.assertTrue(again["already_finished"])
        self.assertEqual(again["session_ended"]["reason"],
                         "driver exited before finish")

    def test_clean_start_request_finish_has_no_isError(self):
        self.patch_child_spawn(self.bridge, CHILD_ECHO)
        responses = self.run_main_calls([
            {"operation": "start"},
            {"operation": "request", "args": ["status"]},
            {"operation": "finish"},
        ])
        for index in (1, 2, 3):
            self.assertNotIn("isError", responses[index]["result"])
            self.assertNotIn("error", responses[index])
        self.assertEqual(self.payload(responses[2])["result"]["echo"], "")
        self.assertTrue(self.payload(responses[3])["ok"])


class McpEnvelopeValidationTests(McpMainFramingTests):
    """R06 fix 2: a JSON object is not automatically a valid driver envelope.
    Regular commands require an integer returncode (not bool) and a boolean
    session_continues; missing/wrong-type/contradictory metadata is a
    protocol failure that closes and reaps the session, preserves the reason
    and never replays the request. The finish ACK and the startup-ready
    handshake are separate recognized shapes."""

    def assert_protocol_failure(self, response, fragment):
        self.assertIn("error", response,
                      "malformed envelope must be a JSON-RPC error, not a result")
        self.assertEqual(response["error"]["code"], -32000)
        self.assertIn("computer-use session ended", response["error"]["message"])
        self.assertIn(fragment, response["error"]["message"])

    def test_empty_envelope_is_protocol_failure(self):
        self.patch_child_spawn(self.bridge, CHILD_EMPTY_ENVELOPE)
        responses = self.run_main_calls([
            {"operation": "start"},
            {"operation": "request", "args": ["status"]},
            {"operation": "request", "args": ["status"]},
        ])
        self.assertNotIn("error", responses[1], "start must succeed")
        self.assert_protocol_failure(responses[2], "integer command returncode")
        # The session is over: the follow-up request cannot run either.
        self.assert_protocol_failure(responses[3], "computer-use session ended")
        self.assertEqual(self.bridge.request_count, 1,
                         "exactly one request per command; no replay")
        self.assertIsNone(self.bridge.proc)
        self.assertIn("integer command returncode",
                      self.bridge.session_ended["reason"])

    def test_boolean_returncode_is_protocol_failure(self):
        self.patch_child_spawn(self.bridge, CHILD_BOOL_RETURNCODE)
        responses = self.run_main_calls([
            {"operation": "start"},
            {"operation": "request", "args": ["status"]},
        ])
        self.assert_protocol_failure(responses[2], "integer command returncode")
        self.assertEqual(self.bridge.request_count, 1)
        self.assertIsNotNone(self.bridge.session_ended)
        self.assertIsNone(self.bridge.proc)

    def test_string_continuation_is_protocol_failure(self):
        # returncode 0 with a string session_continues used to pass as a
        # SUCCESS (the missing-metadata default); it must end the session.
        self.patch_child_spawn(self.bridge, CHILD_STRING_CONTINUATION)
        responses = self.run_main_calls([
            {"operation": "start"},
            {"operation": "request", "args": ["status"]},
        ])
        self.assert_protocol_failure(responses[2], "boolean session_continues")
        self.assertEqual(self.bridge.request_count, 1)
        self.assertIn("boolean session_continues",
                      self.bridge.session_ended["reason"])

    def test_contradictory_success_is_protocol_failure(self):
        self.patch_child_spawn(self.bridge, CHILD_CONTRADICTORY_SUCCESS)
        responses = self.run_main_calls([
            {"operation": "start"},
            {"operation": "request", "args": ["status"]},
        ])
        self.assert_protocol_failure(responses[2], "contradictory")
        self.assertEqual(self.bridge.request_count, 1)
        self.assertIsNone(self.bridge.proc)

    def test_protocol_failure_replays_nothing(self):
        receipt = self.tmp / "receipt.log"
        receipt.touch()
        with mock.patch.dict(os.environ, {"MCP_TEST_RECEIPT": str(receipt)}):
            self.patch_child_spawn(self.bridge, CHILD_COUNTING_EMPTY)
            self.run_main_calls([
                {"operation": "start"},
                {"operation": "request", "args": ["status"]},
            ])
        # request-1 is the handshake accounting line; exactly ONE driver
        # request (request-2) was received — a resend after the protocol
        # failure would have produced request-3.
        self.assertEqual(receipt.read_text(encoding="utf-8").splitlines(),
                         ["request-1", "request-2"])
        self.assertEqual(self.bridge.request_count, 1)

    def test_finish_regular_envelope_is_protocol_failure(self):
        self.patch_child_spawn(self.bridge, CHILD_FINISH_REGULAR_ENVELOPE)
        responses = self.run_main_calls([
            {"operation": "start"},
            {"operation": "finish"},
        ])
        self.assert_protocol_failure(responses[2], "finish acknowledgement")
        self.assertIsNone(self.bridge.proc)

    def test_fatal_envelope_is_a_result_with_preserved_reason(self):
        self.patch_child_spawn(self.bridge, CHILD_FATAL_ENVELOPE)
        responses = self.run_main_calls([
            {"operation": "start"},
            {"operation": "request", "args": ["act"], "stdin": "[]"},
        ])
        self.assertNotIn("error", responses[2],
                         "a valid fatal envelope is a tool result, not a protocol error")
        self.assertIs(responses[2]["result"].get("isError"), True)
        payload = self.payload(responses[2])
        self.assertEqual(payload["returncode"], 1)
        self.assertIs(payload["session_continues"], False)
        self.assertEqual(payload["session_ended"]["reason"],
                         "final capture failed: boom")
        self.assertIsNone(self.bridge.proc)

    def test_recoverable_command_keeps_session_alive(self):
        self.patch_child_spawn(self.bridge, CHILD_REFUSAL_CONTINUE)
        responses = self.run_main_calls([
            {"operation": "start"},
            {"operation": "request", "args": ["act"], "stdin": "[]"},
            {"operation": "request", "args": ["status"]},
            {"operation": "finish"},
        ])
        refused = responses[2]["result"]
        self.assertIs(refused.get("isError"), True,
                      "the command failed even though the session continues")
        payload = self.payload(responses[2])
        self.assertEqual(payload["returncode"], 1)
        self.assertIs(payload["session_continues"], True)
        followup = responses[3]["result"]
        self.assertNotIn("isError", followup)
        self.assertEqual(self.payload(responses[3])["result"]["echo"],
                         "after-refusal")
        self.assertNotIn("isError", responses[4]["result"])
        self.assertTrue(self.payload(responses[4])["ok"])
        self.assertEqual(self.bridge.request_count, 3)


class ScriptedBytesStream:
    """Raw binary stream double that yields one chunk then EOF."""

    def __init__(self, chunk):
        self.chunk = chunk
        self.closed = False

    def fileno(self):
        raise io.UnsupportedOperation("not a real stream")

    def read(self, size):
        chunk, self.chunk = self.chunk, b""
        return chunk

    def close(self):
        self.closed = True


if __name__ == "__main__":
    unittest.main()
