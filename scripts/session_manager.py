#!/usr/bin/env python3
"""Single-session manager for BiDi and Marionette. Stdlib only.

Background: the BiDi and Marionette session limit is shared. One leaked
session blocks everything, and only restarting Zen clears it. Marionette
accepts one client at a time, so two owners racing to open a session can
leave one session open with no owner to close it.

This module makes one rule enforceable in code:

- At most one session owner runs at a time, enforced by a file lock.
- Every session is closed in a finally block, through
  ``SessionManager.session()``, which always calls the session close
  method (``delete()``, ``end()``, ``disconnect()`` or ``close()``,
  first one found, in that order) even when the work raises.
- Every session open and close is logged with wall-clock time.
- A hung session is detected and reaped: a recorded session whose
  owner process is dead, or whose lock is free while its last activity
  is older than the stale timeout, is stale. Reaping clears the state
  so a new owner can start. The browser process is killed only when
  the caller asks for it and only when the recorded pid cmdline
  contains the recorded dedicated profile path, the same safety rule
  as ``scripts/zen_cli.py``. The manager never kills a real user Zen.

Fit with the existing repo code:

- ``scripts/zen_cli.py`` opens one ``BidiSession`` per command and
  closes it in ``finally`` with ``session.end()``. Wrap that pattern
  with ``SessionManager.session(kind="bidi", opener=...)`` to add the
  single-owner lock and the open/close log. The manager calls
  ``end()`` for a ``BidiSession`` because it has no ``delete()``.
- ``tests/puppeteer_bidi.mjs`` already disconnects in ``finally``.
  The same rule applies on the Node side: one owner, disconnect in
  finally, log open and close. This module is the Python side of
  that rule, and its tests prove the lock and the finally behaviour
  without a browser.

Real-browser behaviour (connecting to a live Zen, Marionette session
delete over the wire, killing a hung dedicated Zen) is UNVERIFIED on
this machine because no Firefox or Zen binary exists here. The tests
use fake sessions and a fake browser process record, and they prove
the lock, the finally close, and the hung detection, not the browser
side.
"""

import datetime
import fcntl
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_DIR = (Path.home() / ".local" / "share" / "agent-computer-use"
               / "session-manager")
DEFAULT_STALE_TIMEOUT_S = 300
DEFAULT_LOCK_TIMEOUT_S = 30


class SessionBusy(RuntimeError):
    """Another owner holds the session lock."""


def _utc_now():
    return datetime.datetime.now(tz=datetime.timezone.utc)


def _iso_now():
    return _utc_now().isoformat()


def _unix_now():
    return int(_utc_now().timestamp())


def _pid_alive(pid):
    """True when a process with this pid exists."""
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _cmdline_contains(pid, needle):
    """True when the pid cmdline contains the needle string."""
    if not needle:
        return False
    try:
        raw = Path("/proc/%d/cmdline" % pid).read_bytes()
    except OSError:
        return False
    return needle in raw.decode("utf-8", errors="replace")


class SessionManager:
    """Owns the single BiDi/Marionette session slot on this machine."""

    def __init__(self, directory=None, stale_timeout_s=None,
                 log_path=None):
        self.directory = Path(directory) if directory else DEFAULT_DIR
        self.directory.mkdir(parents=True, exist_ok=True)
        self.lock_path = self.directory / "owner.lock"
        self.state_path = self.directory / "session.json"
        self.log_path = (Path(log_path) if log_path
                         else self.directory / "session-manager.log")
        self.stale_timeout_s = (DEFAULT_STALE_TIMEOUT_S
                                if stale_timeout_s is None
                                else stale_timeout_s)
        self._lock_fd = None

    # -- logging ---------------------------------------------------------

    def log(self, event, **fields):
        """Append one JSON log line with wall-clock time."""
        entry = {"event": event, "wall_clock": _iso_now()}
        entry.update(fields)
        line = json.dumps(entry, ensure_ascii=False)
        with open(self.log_path, "a", encoding="utf-8") as handle:
            handle.write(line + "\n")
        return entry

    # -- state file ------------------------------------------------------

    def _read_state(self):
        try:
            data = json.loads(self.state_path.read_text())
        except (OSError, json.JSONDecodeError):
            return None
        return data if isinstance(data, dict) else None

    def _write_state(self, payload):
        payload = dict(payload)
        payload["updated_unix"] = _unix_now()
        tmp = self.state_path.with_suffix(".tmp")
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            with os.fdopen(fd, "w") as handle:
                json.dump(payload, handle)
        except BaseException:
            try:
                os.close(fd)
            except OSError:
                pass
            raise
        os.replace(tmp, self.state_path)
        return payload

    def _clear_state(self):
        try:
            self.state_path.unlink()
        except OSError:
            pass

    # -- lock ------------------------------------------------------------

    def acquire(self, timeout_s=DEFAULT_LOCK_TIMEOUT_S):
        """Take the single-owner lock, or raise SessionBusy.

        Blocks up to timeout_s seconds, polling every 50 ms. The lock
        is released by the kernel when the owner process dies, so a
        dead owner never holds the slot forever.
        """
        started = time.monotonic()
        fd = os.open(self.lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                self._lock_fd = fd
                self.log("lock_acquired", pid=os.getpid(),
                         waited_ms=round(
                             (time.monotonic() - started) * 1000))
                return self
            except BlockingIOError:
                if time.monotonic() - started >= timeout_s:
                    os.close(fd)
                    raise SessionBusy(
                        "session slot is held by another owner; "
                        "waited %.1fs" % timeout_s) from None
                time.sleep(0.05)

    def release(self):
        """Release the lock. Never raises."""
        if self._lock_fd is None:
            return
        try:
            fcntl.flock(self._lock_fd, fcntl.LOCK_UN)
        except OSError:
            pass
        try:
            os.close(self._lock_fd)
        except OSError:
            pass
        self._lock_fd = None
        self.log("lock_released", pid=os.getpid())

    def try_lock(self):
        """True when the lock is currently free, else False."""
        fd = os.open(self.lock_path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(fd, fcntl.LOCK_UN)
            return True
        except BlockingIOError:
            return False
        finally:
            os.close(fd)

    # -- session record --------------------------------------------------

    def record_open(self, session_id, kind, port=None, browser_pid=None,
                    profile=None):
        """Record a newly opened session and log it."""
        payload = {
            "session_id": session_id,
            "kind": kind,
            "port": port,
            "owner_pid": os.getpid(),
            "browser_pid": browser_pid,
            "profile": profile,
            "opened_wall_clock": _iso_now(),
            "opened_unix": _unix_now(),
            "last_activity_unix": _unix_now(),
        }
        self._write_state(payload)
        self.log("session_open", session_id=session_id, kind=kind,
                 port=port, owner_pid=os.getpid(),
                 browser_pid=browser_pid)
        return payload

    def heartbeat(self):
        """Refresh last activity for the recorded session."""
        state = self._read_state()
        if state is None:
            return None
        state["last_activity_unix"] = _unix_now()
        return self._write_state(state)

    def record_close(self, session_id=None, reason="done"):
        """Clear the session record and log the close."""
        state = self._read_state()
        closed_id = session_id or (state or {}).get("session_id")
        self._clear_state()
        self.log("session_close", session_id=closed_id, reason=reason,
                 owner_pid=os.getpid())
        return closed_id

    # -- close a session object ------------------------------------------

    @staticmethod
    def close_session(session):
        """Close a session object. Never raises.

        Tries, in order: delete(), end(), disconnect(), close().
        Returns the name of the method called, or None when the
        object has no close method. zen_cli BidiSession has end(),
        a raw BiDi or Marionette session has delete(), a Puppeteer
        browser object would use disconnect().
        """
        for name in ("delete", "end", "disconnect", "close"):
            method = getattr(session, name, None)
            if callable(method):
                try:
                    method()
                except Exception:
                    pass
                return name
        return None

    def session(self, kind, opener, timeout_s=DEFAULT_LOCK_TIMEOUT_S):
        """Context manager: one owner, one session, always closed.

        Acquires the lock, calls opener() to build the session,
        records the open, yields the session, then in a finally block
        closes the session, clears the record, and releases the lock.
        The close runs even when the work inside raises.
        """
        return _ManagedSession(self, kind, opener, timeout_s)

    # -- hung detection and reaping --------------------------------------

    def detect_hung(self):
        """Return the hung session record, or None when healthy.

        A recorded session is hung when the lock is free (no live
        owner holds it) and either the owner process is dead or the
        last activity is older than the stale timeout. A live owner
        holding the lock is never hung, however old its session is.
        """
        state = self._read_state()
        if state is None:
            return None
        if not self.try_lock():
            return None
        owner_pid = state.get("owner_pid")
        last = state.get("last_activity_unix") or 0
        age_s = _unix_now() - last
        if _pid_alive(owner_pid):
            return None
        if owner_pid is not None and not _pid_alive(owner_pid):
            return dict(state, hung_reason="owner_pid_dead",
                        age_s=age_s)
        if age_s > self.stale_timeout_s:
            return dict(state, hung_reason="stale_activity",
                        age_s=age_s)
        return None

    def reap_hung(self, kill_browser=False):
        """Clear a hung session record. Returns a result dict.

        With kill_browser=True, also kills the recorded browser pid,
        but only when its cmdline contains the recorded dedicated
        profile path. A real user Zen is never killed: its cmdline
        does not contain a dedicated profile path.
        """
        hung = self.detect_hung()
        if hung is None:
            return {"ok": True, "hung": False}
        browser_pid = hung.get("browser_pid")
        profile = hung.get("profile")
        killed = False
        if kill_browser and isinstance(browser_pid, int):
            if _cmdline_contains(browser_pid, profile or ""):
                try:
                    os.kill(browser_pid, signal.SIGTERM)
                    killed = True
                except OSError:
                    killed = False
        self._clear_state()
        self.log("session_reaped", session_id=hung.get("session_id"),
                 kind=hung.get("kind"),
                 hung_reason=hung.get("hung_reason"),
                 age_s=hung.get("age_s"),
                 browser_killed=killed)
        return {"ok": True, "hung": True,
                "session_id": hung.get("session_id"),
                "kind": hung.get("kind"),
                "hung_reason": hung.get("hung_reason"),
                "age_s": hung.get("age_s"),
                "browser_killed": killed}

    def status(self):
        """Current slot status as a dict."""
        state = self._read_state()
        hung = self.detect_hung()
        return {
            "lock_free": self.try_lock(),
            "session_recorded": state is not None,
            "session": state,
            "hung": hung is not None,
            "hung_reason": (hung or {}).get("hung_reason"),
            "directory": str(self.directory),
        }


class _ManagedSession:
    """Context manager returned by SessionManager.session()."""

    def __init__(self, manager, kind, opener, timeout_s):
        self.manager = manager
        self.kind = kind
        self.opener = opener
        self.timeout_s = timeout_s
        self.session = None
        self.session_id = None

    def __enter__(self):
        self.manager.acquire(timeout_s=self.timeout_s)
        try:
            self.session = self.opener()
        except BaseException:
            self.manager.release()
            raise
        session_id = getattr(self.session, "session_id", None)
        self.session_id = session_id if session_id else "unknown"
        self.manager.record_open(self.session_id, self.kind)
        return self.session

    def __exit__(self, *exc):
        close_method = None
        if self.session is not None:
            close_method = self.manager.close_session(self.session)
        self.manager.record_close(self.session_id,
                                  reason="error" if exc[0] else "done")
        self.manager.log("session_close_method",
                         session_id=self.session_id,
                         method=close_method)
        self.manager.release()
        return False


def build_parser():
    import argparse
    parser = argparse.ArgumentParser(
        description="Single-session manager for BiDi and Marionette.")
    parser.add_argument("--dir", default=None,
                        help="state directory (default: "
                             "~/.local/share/agent-computer-use/"
                             "session-manager)")
    parser.add_argument("--stale-timeout-s", type=int, default=None,
                        help="seconds of inactivity before a session "
                             "counts as hung (default 300)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="show lock and session status")
    sub.add_parser("check", help="exit 1 when a hung session exists")
    reap = sub.add_parser("reap", help="clear a hung session record")
    reap.add_argument("--kill-browser", action="store_true",
                      help="also kill the recorded browser pid, only "
                           "when its cmdline contains the recorded "
                           "dedicated profile path")
    return parser


def main(argv):
    parser = build_parser()
    args = parser.parse_args(argv)
    manager = SessionManager(
        directory=args.dir,
        stale_timeout_s=args.stale_timeout_s)
    if args.command == "status":
        print(json.dumps(manager.status(), ensure_ascii=False))
        return 0
    if args.command == "check":
        hung = manager.detect_hung()
        print(json.dumps({"hung": hung is not None,
                          "hung_reason": (hung or {}).get("hung_reason"),
                          "session_id": (hung or {}).get("session_id")},
                         ensure_ascii=False))
        return 1 if hung is not None else 0
    if args.command == "reap":
        print(json.dumps(manager.reap_hung(
            kill_browser=args.kill_browser), ensure_ascii=False))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
