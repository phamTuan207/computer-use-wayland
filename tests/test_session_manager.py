#!/usr/bin/env python3
"""Tests for scripts/session_manager.py. Stdlib only, no browser needed.

Every test uses a fake session object and a temporary state directory,
so no real Zen session is touched. Each test logs its wall-clock start
and end plus elapsed milliseconds. Run: python3 -m unittest
tests.test_session_manager -v  (from the repo root), or
python3 tests/test_session_manager.py.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from session_manager import SessionBusy, SessionManager  # noqa: E402


def _wall():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class FakeSession:
    """A stand-in for a BiDi or Marionette session object."""

    def __init__(self, session_id="fake-session-1", close_name="delete"):
        self.session_id = session_id
        self.close_calls = []
        self._close_name = close_name

    def delete(self):
        if self._close_name == "delete":
            self.close_calls.append("delete")

    def end(self):
        if self._close_name == "end":
            self.close_calls.append("end")

    def disconnect(self):
        if self._close_name == "disconnect":
            self.close_calls.append("disconnect")


class FakeBidiSession:
    """Mimics scripts/zen_cli.py BidiSession: only end() exists."""

    def __init__(self, session_id="fake-bidi-1"):
        self.session_id = session_id
        self.close_calls = []

    def end(self):
        self.close_calls.append("end")


class SessionManagerTest(unittest.TestCase):
    def setUp(self):
        self._started = time.monotonic()
        self.tmp = tempfile.TemporaryDirectory()
        self.manager = SessionManager(
            directory=Path(self.tmp.name), stale_timeout_s=60)
        print("test %s wall_clock_start %s"
              % (self._testMethodName, _wall()))

    def tearDown(self):
        elapsed_ms = round((time.monotonic() - self._started) * 1000)
        print("test %s wall_clock_end %s elapsed_ms %d"
              % (self._testMethodName, _wall(), elapsed_ms))
        self.tmp.cleanup()

    def test_only_one_owner_at_a_time(self):
        """A second process cannot take the lock while it is held."""
        holder = SessionManager(directory=Path(self.tmp.name),
                                stale_timeout_s=60)
        holder.acquire(timeout_s=5)
        try:
            code = (
                "import sys; sys.path.insert(0, 'scripts');"
                "from session_manager import SessionManager, SessionBusy;"
                "m = SessionManager(directory=%r);"
                "m.acquire(timeout_s=1)"
                % self.tmp.name)
            started = time.monotonic()
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True, text=True, timeout=30)
            elapsed_ms = round((time.monotonic() - started) * 1000)
            print("second owner attempt elapsed_ms %d exit %d"
                  % (elapsed_ms, result.returncode))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SessionBusy", result.stderr)
            self.assertGreaterEqual(elapsed_ms, 900)
        finally:
            holder.release()
        after = SessionManager(directory=Path(self.tmp.name),
                               stale_timeout_s=60)
        after.acquire(timeout_s=5)
        after.release()

    def test_session_always_closed_when_work_raises(self):
        """The session close runs even when the work raises."""
        fake = FakeSession()
        with self.assertRaises(RuntimeError):
            with self.manager.session(kind="bidi",
                                      opener=lambda: fake):
                raise RuntimeError("work failed")
        self.assertEqual(fake.close_calls, ["delete"])
        self.assertIsNone(self.manager._read_state())
        self.assertTrue(self.manager.try_lock())
        log = (Path(self.tmp.name) / "session-manager.log").read_text()
        events = [json.loads(line)["event"] for line in log.splitlines()]
        self.assertIn("session_open", events)
        self.assertIn("session_close", events)

    def test_session_closed_on_success(self):
        """Normal exit closes the session and releases the lock."""
        fake = FakeSession()
        with self.manager.session(kind="marionette",
                                  opener=lambda: fake) as session:
            self.assertIs(session, fake)
            self.assertIsNotNone(self.manager._read_state())
        self.assertEqual(fake.close_calls, ["delete"])
        self.assertIsNone(self.manager._read_state())
        self.assertTrue(self.manager.try_lock())

    def test_bidi_session_closed_with_end(self):
        """A zen_cli style session (only end()) is closed with end()."""
        fake = FakeBidiSession()
        with self.manager.session(kind="bidi", opener=lambda: fake):
            pass
        self.assertEqual(fake.close_calls, ["end"])

    def test_hung_session_detected_and_reaped(self):
        """A record with a dead owner pid and old activity is hung."""
        dead_pid = 999999
        self.assertFalse(os.path.exists("/proc/%d" % dead_pid))
        state = {
            "session_id": "hung-1",
            "kind": "bidi",
            "port": 9222,
            "owner_pid": dead_pid,
            "browser_pid": None,
            "profile": None,
            "opened_wall_clock": _wall(),
            "opened_unix": int(time.time()) - 600,
            "last_activity_unix": int(time.time()) - 600,
        }
        (Path(self.tmp.name) / "session.json").write_text(
            json.dumps(state))
        started = time.monotonic()
        hung = self.manager.detect_hung()
        elapsed_ms = round((time.monotonic() - started) * 1000)
        print("detect_hung elapsed_ms %d" % elapsed_ms)
        self.assertIsNotNone(hung)
        self.assertEqual(hung["hung_reason"], "owner_pid_dead")
        result = self.manager.reap_hung()
        self.assertTrue(result["hung"])
        self.assertEqual(result["session_id"], "hung-1")
        self.assertIsNone(self.manager._read_state())
        self.assertIsNone(self.manager.detect_hung())

    def test_live_session_is_not_hung(self):
        """A record owned by a live process is never flagged hung."""
        self.manager.record_open("live-1", "bidi", port=9222)
        self.assertIsNone(self.manager.detect_hung())
        self.manager.record_close("live-1")

    def test_stale_activity_without_owner_is_hung(self):
        """Old activity plus a free lock counts as hung when the
        owner pid field is missing."""
        state = {
            "session_id": "stale-1",
            "kind": "marionette",
            "port": 2828,
            "owner_pid": None,
            "browser_pid": None,
            "profile": None,
            "opened_wall_clock": _wall(),
            "opened_unix": int(time.time()) - 900,
            "last_activity_unix": int(time.time()) - 900,
        }
        (Path(self.tmp.name) / "session.json").write_text(
            json.dumps(state))
        hung = self.manager.detect_hung()
        self.assertIsNotNone(hung)
        self.assertEqual(hung["hung_reason"], "stale_activity")

    def test_log_lines_carry_wall_clock(self):
        """Every log line is JSON with a wall-clock timestamp."""
        self.manager.record_open("log-1", "bidi", port=9222)
        self.manager.record_close("log-1")
        lines = (Path(self.tmp.name) / "session-manager.log") \
            .read_text().splitlines()
        self.assertGreaterEqual(len(lines), 2)
        for line in lines:
            entry = json.loads(line)
            self.assertIn("wall_clock", entry)
            self.assertIn("event", entry)

    def test_cli_status_and_check(self):
        """The CLI reports status and exits 1 on a hung session."""
        script = Path(__file__).resolve().parent.parent \
            / "scripts" / "session_manager.py"
        started = time.monotonic()
        status = subprocess.run(
            [sys.executable, str(script), "--dir", self.tmp.name,
             "status"], capture_output=True, text=True, timeout=30)
        elapsed_ms = round((time.monotonic() - started) * 1000)
        print("cli status elapsed_ms %d" % elapsed_ms)
        self.assertEqual(status.returncode, 0)
        self.assertIn("lock_free", status.stdout)
        state = {
            "session_id": "cli-hung-1",
            "kind": "bidi",
            "port": 9222,
            "owner_pid": 999999,
            "browser_pid": None,
            "profile": None,
            "opened_wall_clock": _wall(),
            "opened_unix": int(time.time()) - 600,
            "last_activity_unix": int(time.time()) - 600,
        }
        (Path(self.tmp.name) / "session.json").write_text(
            json.dumps(state))
        check = subprocess.run(
            [sys.executable, str(script), "--dir", self.tmp.name,
             "check"], capture_output=True, text=True, timeout=30)
        self.assertEqual(check.returncode, 1)
        self.assertIn("owner_pid_dead", check.stdout)
        reap = subprocess.run(
            [sys.executable, str(script), "--dir", self.tmp.name,
             "reap"], capture_output=True, text=True, timeout=30)
        self.assertEqual(reap.returncode, 0)
        self.assertIn('"hung": true', reap.stdout)
        self.assertIsNone(self.manager._read_state())


if __name__ == "__main__":
    unittest.main(verbosity=2)
