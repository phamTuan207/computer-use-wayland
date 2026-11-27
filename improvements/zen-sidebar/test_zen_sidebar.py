#!/usr/bin/env python3
"""Small tests for zen_sessions.py and zen_live.py.

Run: python3 -m unittest test_zen_sidebar -v   (needs the lz4 package)
No real Zen profile is touched: the offline editor runs against a
synthetic zen-sessions fixture in a temp dir, and the Marionette
client runs against an in-process fake server.
"""

import copy
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import zen_live
import zen_sessions as zs

STATE = {
    "lastCollected": 0,
    "splitViewData": {},
    "spaces": [
        {"uuid": "ws-1", "name": "One", "containerTabId": 0},
        {"uuid": "ws-2", "name": "Two", "containerTabId": 0},
    ],
    "folders": [
        {"id": "fld-1", "name": "F", "collapsed": False, "workspaceId": "ws-1",
         "prevSiblingInfo": None, "emptyTabIds": ["sync-empty"]},
    ],
    "groups": [{"id": "fld-1", "name": "F", "color": "", "collapsed": False}],
    "tabs": [
        {"zenSyncId": "sync-ess", "pinned": True, "zenEssential": True,
         "zenWorkspace": None, "entries": [{"url": "https://ess.example/"}], "index": 1},
        {"zenSyncId": "sync-empty", "pinned": True, "zenEssential": False,
         "zenWorkspace": "ws-1", "groupId": "fld-1", "zenIsEmpty": True,
         "entries": [{"url": "about:blank"}], "index": 1},
        {"zenSyncId": "sync-pin", "pinned": True, "zenEssential": False,
         "zenWorkspace": "ws-1", "entries": [{"url": "https://pin.example/"}], "index": 1},
        {"zenSyncId": "sync-pin2", "pinned": True, "zenEssential": False,
         "zenWorkspace": "ws-1", "entries": [{"url": "https://pin2.example/"}], "index": 1},
        {"zenSyncId": "sync-open", "pinned": False, "zenEssential": False,
         "zenWorkspace": "ws-1", "entries": [{"url": "https://open.example/"}], "index": 1},
    ],
}


class CodecTests(unittest.TestCase):
    def test_round_trip_and_bad_magic(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "zen-sessions.jsonlz4")
            zs.write_mozlz4_atomic(path, STATE)
            self.assertEqual(zs.read_mozlz4(path), STATE)
            bad = os.path.join(d, "bad.jsonlz4")
            with open(bad, "wb") as fh:
                fh.write(b"not a mozlz4 file at all........")
            with self.assertRaises(ValueError):
                zs.read_mozlz4(bad)

    def test_truncated_file_is_value_error(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "zen-sessions.jsonlz4")
            zs.write_mozlz4_atomic(path, STATE)
            data = open(path, "rb").read()
            with open(path, "wb") as fh:
                fh.write(data[:10])  # valid magic, truncated size field
            with self.assertRaises(ValueError):
                zs.read_mozlz4(path)
            with open(path, "wb") as fh:
                fh.write(data[:len(data) // 2])  # truncated LZ4 payload
            with self.assertRaises(ValueError):
                zs.read_mozlz4(path)


class ValidateTests(unittest.TestCase):
    def test_clean_fixture_passes(self):
        self.assertEqual(zs.validate(copy.deepcopy(STATE)), [])

    def test_dangling_references_caught(self):
        state = copy.deepcopy(STATE)
        state["tabs"][4]["groupId"] = "no-such-folder"
        state["tabs"][2]["zenWorkspace"] = "no-such-space"
        problems = zs.validate(state)
        self.assertEqual(len(problems), 2)

    def test_sibling_cycle_caught(self):
        state = copy.deepcopy(STATE)
        state["folders"].append(
            {"id": "fld-2", "name": "G", "collapsed": False, "workspaceId": "ws-1",
             "prevSiblingInfo": {"type": "group", "id": "fld-1"}, "emptyTabIds": []})
        state["folders"][0]["prevSiblingInfo"] = {"type": "group", "id": "fld-2"}
        problems = zs.validate(state)
        self.assertTrue(any("cycle" in p for p in problems), problems)

    def test_tab_folder_workspace_mismatch_caught(self):
        state = copy.deepcopy(STATE)
        state["tabs"][1]["zenWorkspace"] = "ws-2"  # folder fld-1 lives in ws-1
        problems = zs.validate(state)
        self.assertTrue(any("fld-1" in p for p in problems), problems)


class OpTests(unittest.TestCase):
    def setUp(self):
        self.state = copy.deepcopy(STATE)

    def test_move_workspace_and_essential_refusal(self):
        tab = zs.find_tab(self.state, url_part="open.example")
        zs.op_move_workspace(self.state, tab, "ws-2")
        self.assertEqual(tab["zenWorkspace"], "ws-2")
        ess = zs.find_tab(self.state, ident="sync-ess")
        with self.assertRaises(ValueError):
            zs.op_move_workspace(self.state, ess, "ws-1")

    def test_move_workspace_refused_for_foldered_tab(self):
        tab = zs.find_tab(self.state, ident="sync-empty")  # in fld-1 (ws-1)
        with self.assertRaises(ValueError):
            zs.op_move_workspace(self.state, tab, "ws-2")

    def test_move_folder_and_cross_workspace_refusal(self):
        tab = zs.find_tab(self.state, url_part="open.example")
        zs.op_move_folder(self.state, tab, "fld-1")
        self.assertEqual(tab["groupId"], "fld-1")
        other = zs.find_tab(self.state, url_part="pin.example")
        zs.op_move_workspace(self.state, other, "ws-2")
        with self.assertRaises(ValueError):
            zs.op_move_folder(self.state, other, "fld-1")

    def test_pin_moves_to_pinned_boundary_and_unpin_back(self):
        tab = zs.find_tab(self.state, url_part="open.example")
        zs.op_set_pinned(self.state, tab, True)
        ids = [t["zenSyncId"] for t in self.state["tabs"]]
        self.assertEqual(ids[-1], "sync-open")  # last of the pinned region
        self.assertEqual(zs.validate(self.state), [])
        zs.op_set_pinned(self.state, tab, False)
        ids = [t["zenSyncId"] for t in self.state["tabs"]]
        self.assertEqual(ids[-1], "sync-open")  # first of the unpinned region
        self.assertEqual(zs.validate(self.state), [])

    def test_unpin_essential_refused(self):
        ess = zs.find_tab(self.state, ident="sync-ess")
        with self.assertRaises(ValueError):
            zs.op_set_pinned(self.state, ess, False)

    def test_reorder_movable_pins_only(self):
        zs.op_reorder_pins(self.state, ["sync-pin2", "sync-pin"])
        ids = [t["zenSyncId"] for t in self.state["tabs"]]
        self.assertEqual(ids, ["sync-ess", "sync-empty", "sync-pin2", "sync-pin", "sync-open"])
        with self.assertRaises(ValueError):
            zs.op_reorder_pins(self.state, ["sync-pin"])  # incomplete set
        with self.assertRaises(ValueError):
            zs.op_reorder_pins(self.state, ["sync-ess", "sync-pin", "sync-pin2"])  # essential not movable


class CliTests(unittest.TestCase):
    def test_dry_run_then_apply(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as bd:
            path = os.path.join(d, "zen-sessions.jsonlz4")
            zs.write_mozlz4_atomic(path, STATE)
            before = open(path, "rb").read()
            rc = zs.main(["--profile", d, "move-workspace",
                          "--tab-url", "open.example", "--to", "ws-2"])
            self.assertEqual(rc, 0)
            self.assertEqual(open(path, "rb").read(), before)  # dry run wrote nothing
            rc = zs.main(["--profile", d, "--backup-dir", bd, "move-workspace",
                          "--tab-url", "open.example", "--to", "ws-2", "--apply"])
            self.assertEqual(rc, 0)
            tab = zs.find_tab(zs.read_mozlz4(path), url_part="open.example")
            self.assertEqual(tab["zenWorkspace"], "ws-2")
            stamps = os.listdir(bd)
            self.assertEqual(len(stamps), 1)
            backup_dir = os.path.join(bd, stamps[0])
            self.assertTrue(os.path.exists(os.path.join(backup_dir, "zen-sessions.jsonlz4")))
            manifest = json.load(open(os.path.join(backup_dir, "manifest.json")))
            self.assertIn("zen-sessions.jsonlz4", manifest["files"])

    def test_apply_restores_original_when_verification_fails(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as bd:
            path = os.path.join(d, "zen-sessions.jsonlz4")
            zs.write_mozlz4_atomic(path, STATE)
            before = open(path, "rb").read()
            orig = zs.read_mozlz4
            calls = {"n": 0}

            def tampering_read(p):
                calls["n"] += 1
                result = orig(p)
                if calls["n"] == 3:  # main load=1, backup check=2, post-write verify=3
                    return dict(result, tampered=True)
                return result

            zs.read_mozlz4 = tampering_read
            try:
                with self.assertRaises(SystemExit):
                    zs.main(["--profile", d, "--backup-dir", bd, "move-workspace",
                             "--tab-url", "open.example", "--to", "ws-2", "--apply"])
            finally:
                zs.read_mozlz4 = orig
            self.assertEqual(open(path, "rb").read(), before)


LOCK_HOLDER = """
import fcntl, sys, time
fd = open(sys.argv[1], "w")
fcntl.lockf(fd, fcntl.LOCK_EX)
open(sys.argv[2], "w").write("ready")
time.sleep(30)
"""


class LockTests(unittest.TestCase):
    def test_posix_lock_detected_and_apply_refused(self):
        with tempfile.TemporaryDirectory() as d:
            zs.write_mozlz4_atomic(os.path.join(d, "zen-sessions.jsonlz4"), STATE)
            lock_path = os.path.join(d, ".parentlock")
            open(lock_path, "w").close()
            self.assertFalse(zs._lock_is_held(lock_path))
            ready = os.path.join(d, "ready")
            child = subprocess.Popen([sys.executable, "-c", LOCK_HOLDER, lock_path, ready])
            try:
                for _ in range(100):
                    if os.path.exists(ready):
                        break
                    time.sleep(0.05)
                # Gecko holds the profile lock with POSIX fcntl locks, which
                # a flock-only probe cannot see; the probe must use lockf.
                self.assertTrue(zs._lock_is_held(lock_path))
                self.assertTrue(zs.zen_is_running(d))
                with self.assertRaises(SystemExit):
                    zs.main(["--profile", d, "move-workspace",
                             "--tab-url", "open.example", "--to", "ws-2", "--apply"])
            finally:
                child.terminate()
                child.wait()
            self.assertFalse(zs._lock_is_held(lock_path))


class JsPayloadTests(unittest.TestCase):
    def test_payloads_use_real_apis_and_guards(self):
        self.assertIn("gZenFolders.createFolder", zen_live.JS_CREATE_FOLDER)
        self.assertIn("addTabs", zen_live.JS_MOVE_FOLDER)
        self.assertIn("changeWorkspaceWithID", zen_live.JS_SWITCH_WORKSPACE)
        self.assertIn("changeFolderToSpace", zen_live.JS_MOVE_FOLDER_SPACE)
        self.assertIn("pinTab", zen_live.JS_PIN)
        self.assertIn("moveTabTo", zen_live.JS_MOVE_TAB)
        self.assertIn("moveTabToWorkspace", zen_live.JS_MOVE_WORKSPACE)
        self.assertIn('need("gZenWorkspaces")', zen_live.JS_LIST)
        for payload in (zen_live.JS_LIST, zen_live.JS_MOVE_WORKSPACE, zen_live.JS_CREATE_FOLDER):
            # Async completion is the callback Marionette appends as the
            # last script argument (marionetteScriptFinished is gone).
            self.assertIn("arguments[arguments.length - 1](v)", payload)
            self.assertNotIn("marionetteScriptFinished", payload)


class FakeMarionetteServer(threading.Thread):
    """Modes: normal | dribble (byte-chunked sends) | error | wrongid."""

    def __init__(self, mode="normal"):
        super().__init__(daemon=True)
        self.mode = mode
        self.listener = socket.socket()
        self.listener.bind(("127.0.0.1", 0))
        self.listener.listen(1)
        self.port = self.listener.getsockname()[1]
        self.commands = []

    def _send(self, conn, data):
        if self.mode == "dribble":
            for i in range(0, len(data), 7):
                conn.sendall(data[i:i + 7])
                time.sleep(0.001)
        else:
            conn.sendall(data)

    def run(self):
        conn, _ = self.listener.accept()
        # The real server sends the greeting as a length-prefixed frame.
        greeting = b'{"applicationType":"gecko","marionetteProtocol":3}'
        self._send(conn, str(len(greeting)).encode() + b":" + greeting)
        buf = b""
        while True:
            try:
                chunk = conn.recv(65536)
            except OSError:
                return
            if not chunk:
                return
            buf += chunk
            while b":" in buf:
                size_raw, _, rest = buf.partition(b":")
                size = int(size_raw)
                if len(rest) < size:
                    break
                msg = json.loads(rest[:size])
                buf = rest[size:]
                self.commands.append(msg[2])
                if self.mode == "error" and msg[2] == "WebDriver:ExecuteAsyncScript":
                    reply = [1, msg[1], {"error": "fake failure"}, None]
                elif self.mode == "wrongid":
                    reply = [1, msg[1] + 99, None, None]
                else:
                    # WebDriver wraps script results as {"value": ...};
                    # NewSession returns sessionId/capabilities unwrapped.
                    result = {"sessionId": "fake", "capabilities": {}} if msg[2] == "WebDriver:NewSession" else \
                        {"value": {"echoArgs": msg[3].get("args")}} if msg[2] == "WebDriver:ExecuteAsyncScript" else None
                    reply = [1, msg[1], None, result]
                payload = json.dumps(reply).encode()
                self._send(conn, str(len(payload)).encode() + b":" + payload)


class MarionetteClientTests(unittest.TestCase):
    def _client(self, mode="normal"):
        server = FakeMarionetteServer(mode)
        server.start()
        return zen_live.Marionette("127.0.0.1", server.port), server

    def test_handshake_and_execute(self):
        client, server = self._client()
        self.assertEqual(client.greeting["marionetteProtocol"], 3)
        client.new_session()
        client.set_context("chrome")
        result = client.execute_async("script body", ("a", 1))
        self.assertEqual(result["echoArgs"], ["a", 1])
        client.close()
        self.assertEqual(server.commands[:3],
                         ["WebDriver:NewSession", "Marionette:SetContext",
                          "WebDriver:ExecuteAsyncScript"])

    def test_split_frames_reassemble(self):
        client, _server = self._client("dribble")
        client.new_session()
        result = client.execute_async("script body", ("x",))
        self.assertEqual(result["echoArgs"], ["x"])
        client.close()

    def test_error_frame_raises(self):
        client, _server = self._client("error")
        client.new_session()
        with self.assertRaises(zen_live.MarionetteError):
            client.execute_async("script body", ())
        client.close()

    def test_wrong_response_id_raises(self):
        client, _server = self._client("wrongid")
        with self.assertRaises(zen_live.MarionetteError):
            client.new_session()
        client.sock.close()

    def test_run_op_list_needs_no_other_subcommand_args(self):
        # Regression (R17 D3): run_op must not dereference arguments
        # belonging to other subcommands; `list` defines none of them.
        import argparse
        client, server = self._client()
        result = zen_live.run_op(client, argparse.Namespace(cmd="list"))
        self.assertEqual(result, {"echoArgs": []})
        client.close()
        self.assertEqual(server.commands[:3],
                         ["WebDriver:NewSession", "Marionette:SetContext",
                          "WebDriver:ExecuteAsyncScript"])


class PreflightTests(unittest.TestCase):
    """M11c: synthetic env/port/profile cases for the launch
    pre-flight. No real Zen is touched."""

    def _free_port(self):
        probe = socket.socket()
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
        probe.close()
        return port

    def _dbus_socket(self, directory):
        path = os.path.join(directory, "bus")
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        listener.bind(path)
        listener.listen(1)
        self.addCleanup(listener.close)
        return "unix:path=" + path

    def _codes(self, result):
        return {c["name"]: c["code"] for c in result["checks"]}

    def test_all_pass(self):
        with tempfile.TemporaryDirectory() as d:
            env = {"MOZ_REMOTE_ALLOW_SYSTEM_ACCESS": "1",
                   "DBUS_SESSION_BUS_ADDRESS": self._dbus_socket(d)}
            result = zen_live.marionette_preflight(
                env=env, port=self._free_port(), profile=d)
            self.assertTrue(result["ok"], result)
            self.assertEqual(set(self._codes(result).values()), {"ok"})

    def test_missing_env_gate_fails_fast_named(self):
        with tempfile.TemporaryDirectory() as d:
            env = {"DBUS_SESSION_BUS_ADDRESS": self._dbus_socket(d)}
            result = zen_live.marionette_preflight(
                env=env, port=self._free_port(), profile=d)
            self.assertFalse(result["ok"])
            self.assertEqual(self._codes(result)["system_access_env"],
                             "missing_system_access_env")

    def test_missing_dbus_address_fails_named(self):
        env = {"MOZ_REMOTE_ALLOW_SYSTEM_ACCESS": "1"}
        result = zen_live.marionette_preflight(
            env=env, port=self._free_port())
        self.assertFalse(result["ok"])
        self.assertEqual(self._codes(result)["dbus_session_bus"],
                         "dbus_address_missing")

    def test_port_in_use_fails_named(self):
        with tempfile.TemporaryDirectory() as d:
            holder = socket.socket()
            holder.bind(("127.0.0.1", 0))
            holder.listen(1)
            self.addCleanup(holder.close)
            env = {"MOZ_REMOTE_ALLOW_SYSTEM_ACCESS": "1",
                   "DBUS_SESSION_BUS_ADDRESS": self._dbus_socket(d)}
            result = zen_live.marionette_preflight(
                env=env, port=holder.getsockname()[1], profile=d)
            self.assertFalse(result["ok"])
            self.assertEqual(self._codes(result)["port_free"], "port_in_use")

    def test_profile_in_real_home_refused(self):
        with tempfile.TemporaryDirectory() as d:
            env = {"MOZ_REMOTE_ALLOW_SYSTEM_ACCESS": "1",
                   "DBUS_SESSION_BUS_ADDRESS": self._dbus_socket(d)}
            real = os.path.join(os.path.expanduser("~"), ".config", "zen",
                                "throwaway")
            result = zen_live.marionette_preflight(
                env=env, port=self._free_port(), profile=real)
            self.assertFalse(result["ok"])
            self.assertEqual(self._codes(result)["profile_dir"],
                             "profile_in_real_home")

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            good = {"MOZ_REMOTE_ALLOW_SYSTEM_ACCESS": "1",
                    "DBUS_SESSION_BUS_ADDRESS": self._dbus_socket(d)}
            port = str(self._free_port())
            old = dict(os.environ)
            try:
                os.environ.clear()
                os.environ.update(good)
                self.assertEqual(
                    zen_live.main(["--port", port, "preflight",
                                   "--profile", d]), 0)
                del os.environ["MOZ_REMOTE_ALLOW_SYSTEM_ACCESS"]
                self.assertEqual(
                    zen_live.main(["--port", port, "preflight",
                                   "--profile", d]), 1)
            finally:
                os.environ.clear()
                os.environ.update(old)


if __name__ == "__main__":
    unittest.main()
