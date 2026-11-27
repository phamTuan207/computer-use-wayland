#!/usr/bin/env python3
"""Single-drive lock hardening tests for rdp_client.py (I20 substitute).

Covers: holder identity record (pid + process start time) and its
parsing (incl. the legacy bare-pid form), liveness classification
(alive / dead / pid-reused), contention error naming a live holder,
contention with a stale record (flock held by another fd while the
recorded pid is dead), stale file content never wedging acquisition
(flock is kernel-released on holder death), lock released when
attach fails after acquisition, O_CLOEXEC on the lock fd, symlink
refusal, and the replaced-inode check.

Run: python3 -m unittest test_lock -v
No browser needed. ydotool is banned (not used).
"""
import fcntl
import os
import subprocess
import sys
import tempfile
import unittest

from rdp_client import (RDPClient, RDPError, Scope, _holder_alive,
                        _lock_path_is_fd, _lock_record,
                        _parse_lock_record, _proc_start_time)
from test_scope_unittest import FakeRDPTransport, TAB_A


def make_client(lock_file, transport=None):
    return RDPClient(0, transport=transport or FakeRDPTransport(),
                     scope=Scope(tab_ids=[TAB_A]), lock_file=lock_file)


class LockRecordTest(unittest.TestCase):
    def test_record_round_trip(self):
        rec = _parse_lock_record(_lock_record())
        self.assertEqual(rec["pid"], os.getpid())
        self.assertEqual(rec["start"], _proc_start_time(os.getpid()))

    def test_legacy_bare_pid_parses(self):
        self.assertEqual(_parse_lock_record("4242\n"),
                         {"pid": 4242, "start": None})

    def test_garbage_parses_to_none(self):
        self.assertIsNone(_parse_lock_record(""))
        self.assertIsNone(_parse_lock_record("not a record"))
        self.assertIsNone(_parse_lock_record("pid=abc"))

    def test_holder_alive_self(self):
        self.assertIs(_holder_alive(_parse_lock_record(_lock_record())),
                      True)

    def test_holder_dead_pid(self):
        # A reaped child pid is dead; pid reuse inside the test window
        # is not a realistic flake source at this scale.
        proc = subprocess.Popen([sys.executable, "-c", "pass"])
        proc.wait()
        rec = {"pid": proc.pid, "start": None}
        self.assertIs(_holder_alive(rec), False)

    def test_holder_pid_reused_is_stale(self):
        # Same live pid, wrong start time: a different incarnation.
        rec = {"pid": os.getpid(), "start": "1"}
        self.assertIs(_holder_alive(rec), False)


class LockAcquireTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "drive.lock")

    def test_contention_names_live_holder(self):
        c1 = make_client(self.path)
        try:
            with self.assertRaises(RDPError) as cm:
                make_client(self.path)
            msg = str(cm.exception)
            self.assertIn("LOCK REFUSED", msg)
            self.assertIn(f"by pid {os.getpid()}", msg)
            self.assertIn("process alive", msg)
        finally:
            c1.close()

    def test_stale_record_contention_says_not_running(self):
        # Flock held by a bare fd; file content names a dead pid.
        proc = subprocess.Popen([sys.executable, "-c", "pass"])
        proc.wait()
        fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            os.write(fd, f"pid={proc.pid} start=- at=x\n".encode())
            with self.assertRaises(RDPError) as cm:
                make_client(self.path)
            msg = str(cm.exception)
            self.assertIn("LOCK REFUSED", msg)
            self.assertIn("is not running", msg)
            self.assertIn("stale record", msg)
        finally:
            os.close(fd)

    def test_stale_file_content_does_not_wedge(self):
        # Leftover file naming a dead holder, no flock held: the
        # kernel released the flock at holder death, so acquisition
        # succeeds and overwrites the record.
        proc = subprocess.Popen([sys.executable, "-c", "pass"])
        proc.wait()
        with open(self.path, "w") as f:
            f.write(f"pid={proc.pid} start=- at=x\n")
        c = make_client(self.path)
        try:
            with open(self.path) as f:
                rec = _parse_lock_record(f.read())
            self.assertEqual(rec["pid"], os.getpid())
        finally:
            c.close()

    def test_lock_released_when_attach_fails(self):
        # Transport whose greeting read fails: __init__ raises after
        # the lock was taken; the fence must not stay wedged.
        class DeadTransport:
            def settimeout(self, _t):
                pass

            def close(self):
                pass

            def recv(self, _n):
                return b""

            def sendall(self, _data):
                pass

        with self.assertRaises(Exception):
            make_client(self.path, transport=DeadTransport())
        c = make_client(self.path)  # would raise LOCK REFUSED if wedged
        c.close()

    def test_lock_fd_is_cloexec(self):
        c = make_client(self.path)
        try:
            flags = fcntl.fcntl(c._lock_fd, fcntl.F_GETFD)
            self.assertTrue(flags & fcntl.FD_CLOEXEC)
        finally:
            c.close()

    def test_symlink_lock_file_refused(self):
        target = os.path.join(self.dir, "target")
        with open(target, "w") as f:
            f.write("x")
        os.symlink(target, self.path)
        with self.assertRaises(RDPError) as cm:
            make_client(self.path)
        self.assertIn("cannot open lock file", str(cm.exception))

    def test_replaced_inode_detected(self):
        fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o600)
        try:
            self.assertTrue(_lock_path_is_fd(self.path, fd))
            os.unlink(self.path)
            with open(self.path, "w") as f:
                f.write("new inode")
            self.assertFalse(_lock_path_is_fd(self.path, fd))
        finally:
            os.close(fd)

    def test_release_allows_reacquire(self):
        c1 = make_client(self.path)
        c1.close()
        c2 = make_client(self.path)
        c2.close()


if __name__ == "__main__":
    unittest.main()
