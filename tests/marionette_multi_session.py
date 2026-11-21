#!/usr/bin/env python3
"""Raw Marionette protocol test: prove the one-session rule.

Talks to Firefox directly over a TCP socket using the Marionette
wire protocol (length-prefixed JSON). No Selenium, no geckodriver.

Sequence:
  1. Start Firefox headless with -marionette on a chosen port (set
     through the marionette.port preference in a user.js) and a
     throwaway profile.
  2. Connection A: handshake, then NewSession (attempt A1).
  3. Connection A: NewSession again while A1 is active (A2, A3).
  4. Connection B: a second simultaneous TCP connection while A is
     connected and A1 is active (B1), then a retry while A4 is
     active (B2). A second client may not even get a handshake.
  5. Connection A: DeleteSession, then NewSession again (A4) to show
     a new session is allowed once the old one is gone.
  6. Probe B once more while A is still connected but holds no
     session (B-mid), to separate the connection limit from the
     session limit. Then connection A disconnects entirely; only
     then is a fresh connection B accepted, and its NewSession
     (B3) is tried.
  7. Cleanup: delete any live session, close sockets, terminate
     Firefox, verify the process is gone and the port is closed.

Every request and response is logged to stdout as one JSON object
per line (JSONL), with UTC timestamps and per-attempt elapsed time.

Usage: python3 tests/marionette_multi_session.py [port]
Default port: 3849.
"""

import json
import socket
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

FIREFOX = Path.home() / "workspace" / "tools" / "firefox" / "firefox"
DEFAULT_PORT = 3849
SOCKET_TIMEOUT = 15.0


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def log(event, **fields):
    record = {"ts": now_iso(), "event": event}
    record.update(fields)
    print(json.dumps(record), flush=True)


class MarionetteConn:
    """One TCP connection speaking the Marionette wire protocol."""

    def __init__(self, name, host, port):
        self.name = name
        self.sock = socket.create_connection((host, port), timeout=SOCKET_TIMEOUT)
        self.sock.settimeout(SOCKET_TIMEOUT)
        self.buf = b""
        self.msgid = 0

    def _read_message(self):
        # Frame format: <decimal length> ":" <json payload>
        while True:
            colon = self.buf.find(b":")
            if colon > 0 and self.buf[:colon].isdigit():
                length = int(self.buf[:colon])
                if len(self.buf) >= colon + 1 + length:
                    payload = self.buf[colon + 1 : colon + 1 + length]
                    self.buf = self.buf[colon + 1 + length :]
                    return json.loads(payload.decode("utf-8"))
            chunk = self.sock.recv(65536)
            if not chunk:
                raise ConnectionError(f"conn {self.name}: server closed connection")
            self.buf += chunk

    def read_handshake(self):
        start = time.perf_counter()
        hs = self._read_message()
        elapsed = time.perf_counter() - start
        log("handshake", conn=self.name, elapsed_s=round(elapsed, 4), payload=hs)
        return hs

    def try_handshake(self):
        """Return the handshake dict, or None if the server closed the
        connection without sending one (what Firefox 160 does to a
        second simultaneous client)."""
        start = time.perf_counter()
        try:
            hs = self._read_message()
        except (ConnectionError, socket.timeout, OSError) as exc:
            elapsed = time.perf_counter() - start
            log("handshake_failed", conn=self.name,
                elapsed_s=round(elapsed, 4), detail=repr(exc))
            return None
        elapsed = time.perf_counter() - start
        log("handshake", conn=self.name, elapsed_s=round(elapsed, 4), payload=hs)
        return hs

    def command(self, attempt, name, params=None):
        self.msgid += 1
        msg = [0, self.msgid, name, params or {}]
        wire = json.dumps(msg).encode("utf-8")
        framed = str(len(wire)).encode("ascii") + b":" + wire
        log("send", conn=self.name, attempt=attempt, command=name,
            msgid=self.msgid, params=params or {})
        start = time.perf_counter()
        self.sock.sendall(framed)
        resp = self._read_message()
        elapsed = time.perf_counter() - start
        # Response shape: [1, msgid, error-or-null, result-or-null]
        error = resp[2] if len(resp) > 2 else None
        result = resp[3] if len(resp) > 3 else None
        outcome = "error" if error else "ok"
        slim_error = None
        if error:
            slim_error = {
                "error": error.get("error"),
                "message": error.get("message"),
                "stacktrace_present": bool(error.get("stacktrace")),
            }
        slim_result = None
        if result is not None:
            slim_result = result
            if isinstance(result, dict) and "capabilities" in result:
                slim_result = {
                    "sessionId": result.get("sessionId"),
                    "capabilities_keys": sorted(result.get("capabilities", {}).keys()),
                    "browserName": result.get("capabilities", {}).get("browserName"),
                    "browserVersion": result.get("capabilities", {}).get("browserVersion"),
                }
        log("recv", conn=self.name, attempt=attempt, command=name,
            elapsed_s=round(elapsed, 4), outcome=outcome,
            error=slim_error, result=slim_result)
        return {"outcome": outcome, "error": error, "result": result,
                "elapsed_s": elapsed}

    def close(self):
        try:
            self.sock.close()
        except OSError:
            pass


def wait_for_port(port, timeout=60.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            s = socket.create_connection(("127.0.0.1", port), timeout=2.0)
            s.close()
            return True
        except OSError:
            time.sleep(0.25)
    return False


def port_is_open(port):
    try:
        s = socket.create_connection(("127.0.0.1", port), timeout=2.0)
        s.close()
        return True
    except OSError:
        return False


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    results = []

    def record(attempt, conn_name, description, res):
        err = res["error"] or {}
        results.append({
            "attempt": attempt,
            "conn": conn_name,
            "description": description,
            "outcome": res["outcome"],
            "session_id": (res["result"] or {}).get("sessionId")
            if isinstance(res["result"], dict) else None,
            "error_name": err.get("error"),
            "error_message": err.get("message"),
            "elapsed_s": round(res["elapsed_s"], 4),
        })

    def record_raw(attempt, conn_name, description, outcome, elapsed,
                   error_name=None, error_message=None, session_id=None):
        results.append({
            "attempt": attempt,
            "conn": conn_name,
            "description": description,
            "outcome": outcome,
            "session_id": session_id,
            "error_name": error_name,
            "error_message": error_message,
            "elapsed_s": round(elapsed, 4),
        })

    profile = tempfile.mkdtemp(prefix="marionette-multi-session-")
    # The --marionette-port command line flag is ignored by Firefox
    # 160 (it still listens on the default 2828, verified in a debug
    # run). The supported way to pick the port is the marionette.port
    # preference, seeded here through user.js in the throwaway profile.
    user_js = Path(profile) / "user.js"
    user_js.write_text(f'user_pref("marionette.port", {port});\n',
                       encoding="utf-8")
    log("info", step="launch_firefox", binary=str(FIREFOX), port=port,
        profile=profile)
    launch_start = time.perf_counter()
    proc = subprocess.Popen(
        [str(FIREFOX), "-marionette",
         "-headless", "-no-remote", "-profile", profile],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        if not wait_for_port(port):
            log("fatal", step="wait_for_port", detail="port never opened")
            return 1
        log("info", step="port_open",
            elapsed_s=round(time.perf_counter() - launch_start, 4))

        caps = {"capabilities": {"alwaysMatch": {"browserName": "firefox"}}}

        # Connection A
        a = MarionetteConn("A", "127.0.0.1", port)
        a.read_handshake()

        r = a.command("A1", "WebDriver:NewSession", caps)
        record("A1", "A", "first NewSession on connection A", r)
        a_session_1 = (r["result"] or {}).get("sessionId")

        r = a.command("A2", "WebDriver:NewSession", caps)
        record("A2", "A", "second NewSession on same connection, A1 active", r)

        r = a.command("A3", "WebDriver:NewSession", caps)
        record("A3", "A", "third NewSession on same connection, A1 active", r)

        # Connection B, simultaneous, while A is connected and its
        # session is active. Firefox 160 closes a second connection
        # without a handshake (observed in an earlier run), so B is
        # handled as an expected-failure probe, not a hard error.
        b_session = None
        b = None
        t0 = time.perf_counter()
        try:
            b_probe = MarionetteConn("B", "127.0.0.1", port)
            hs = b_probe.try_handshake()
        except (ConnectionError, socket.timeout, OSError) as exc:
            hs = None
            log("handshake_failed", conn="B",
                elapsed_s=round(time.perf_counter() - t0, 4),
                detail=f"connect: {exc!r}")
            b_probe = None
        if hs is None:
            record_raw("B1", "B",
                       "second TCP connection while A connected, A1 active",
                       "connection closed by server, no handshake received",
                       time.perf_counter() - t0)
            if b_probe is not None:
                b_probe.close()
        else:
            b = b_probe
            r = b.command("B1", "WebDriver:NewSession", caps)
            record("B1", "B", "NewSession on second connection, A1 active", r)
            b_session = (r["result"] or {}).get("sessionId")

        # Delete A's session, then a new session must be allowed
        r = a.command("A-del-1", "WebDriver:DeleteSession")
        record("A-del-1", "A", "DeleteSession for A1", r)

        r = a.command("A4", "WebDriver:NewSession", caps)
        record("A4", "A", "NewSession on A after A1 was deleted", r)
        a_session_2 = (r["result"] or {}).get("sessionId")

        # B retries while A is still connected with A4 active
        if b is None:
            t0 = time.perf_counter()
            try:
                b_probe = MarionetteConn("B", "127.0.0.1", port)
                hs = b_probe.try_handshake()
            except (ConnectionError, socket.timeout, OSError) as exc:
                hs = None
                log("handshake_failed", conn="B",
                    elapsed_s=round(time.perf_counter() - t0, 4),
                    detail=f"connect: {exc!r}")
                b_probe = None
            if hs is None:
                record_raw("B2", "B",
                           "second TCP connection retry, A still connected, "
                           "A4 active",
                           "connection closed by server, no handshake received",
                           time.perf_counter() - t0)
                if b_probe is not None:
                    b_probe.close()
            else:
                b = b_probe
        if b is not None and b_session is None:
            r = b.command("B2", "WebDriver:NewSession", caps)
            record("B2", "B", "NewSession on second connection, A4 active", r)
            b_session = (r["result"] or {}).get("sessionId")

        # Cleanup A's second session, then disconnect A entirely.
        if a_session_2:
            r = a.command("A-del-2", "WebDriver:DeleteSession")
            record("A-del-2", "A", "DeleteSession for A4", r)

        # Probe: A is still connected but now holds no session. Is a
        # second connection refused because of the active session, or
        # because of the open connection itself?
        if b is None:
            t0 = time.perf_counter()
            try:
                b_probe = MarionetteConn("B", "127.0.0.1", port)
                hs = b_probe.try_handshake()
            except (ConnectionError, socket.timeout, OSError) as exc:
                hs = None
                log("handshake_failed", conn="B",
                    elapsed_s=round(time.perf_counter() - t0, 4),
                    detail=f"connect: {exc!r}")
                b_probe = None
            if hs is None:
                record_raw("B-mid", "B",
                           "second TCP connection, A still connected but "
                           "holding no session",
                           "connection closed by server, no handshake received",
                           time.perf_counter() - t0)
                if b_probe is not None:
                    b_probe.close()
            else:
                record_raw("B-mid", "B",
                           "second TCP connection, A still connected but "
                           "holding no session",
                           "handshake received", time.perf_counter() - t0)
                b = b_probe

        a.close()
        log("info", step="connection_a_closed")

        # Only now, with A disconnected, a fresh client B should be
        # accepted. Retry for up to about 5 seconds while the
        # listener recovers.
        if b is None:
            deadline = time.monotonic() + 5.0
            tries = 0
            while time.monotonic() < deadline and b is None:
                tries += 1
                try:
                    b_probe = MarionetteConn("B", "127.0.0.1", port)
                    hs = b_probe.try_handshake()
                except (ConnectionError, socket.timeout, OSError):
                    hs = None
                    b_probe = None
                if hs is None:
                    if b_probe is not None:
                        b_probe.close()
                    time.sleep(0.5)
                else:
                    b = b_probe
            log("info", step="connection_b_after_a_disconnect", tries=tries,
                accepted=b is not None)
        if b is not None and b_session is None:
            r = b.command("B3", "WebDriver:NewSession", caps)
            record("B3", "B", "NewSession on fresh connection after A "
                              "disconnected", r)
            b_session = (r["result"] or {}).get("sessionId")
        if b is not None and b_session:
            r = b.command("B-del", "WebDriver:DeleteSession")
            record("B-del", "B", "DeleteSession for B session (cleanup)", r)

        log("info", step="session_ids", a_first=a_session_1,
            a_after_delete=a_session_2, b=b_session)

        if b is not None:
            b.close()
    finally:
        log("info", step="terminate_firefox", pid=proc.pid)
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)
        alive = proc.poll() is None
        log("info", step="firefox_exited", pid=proc.pid,
            returncode=proc.returncode, still_alive=alive)
        time.sleep(0.5)
        log("info", step="port_after_exit", port=port,
            port_open=port_is_open(port))

    log("summary", results=results)
    print("\n==== RESULTS TABLE ====")
    for row in results:
        print(json.dumps(row))
    return 0


if __name__ == "__main__":
    sys.exit(main())
