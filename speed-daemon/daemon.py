#!/usr/bin/env python3
"""speed-daemon: warm persistent sender daemon (Method 2, speed-test 2026-11-23).

Keeps warm on this VM so each send is ONE IPC call:
  (a) warm Python process (this daemon; no per-send interpreter startup),
  (b) warm SSH ControlMaster to the laptop (S0 mux, scripts/ssh-laptop-mux.sh;
      first call creates the master ~3.3s, later calls reuse it ~0.7-0.9s),
  (c) ONE batched SSH session per send: the laptop-side
      /tmp/daemon-one-send.sh does pill acquire+verify, the CDP send
      (node /tmp/daemon-send.mjs: pre-count guard, set_value, focus, Enter,
      V12 poll), pill release+verify, all inside that single session.

DESIGN NOTE - why no warm CDP websocket from the VM (spec item b):
  Tested 2026-11-23 ~06:54 +07: CONNECT via the runtime tunnel proxy (port
  3130) to 100.70.92.52:22 returns HTTP 200, but CONNECT to
  100.70.92.52:9223 and :9224 returns an empty reply (proxy closes it).
  `ss` on the laptop confirms why: Chromium/Brave listen on 127.0.0.1:9223
  and 127.0.0.1:9224 ONLY (loopback-bound). Nothing listens on the tailnet
  IP, so no VM-side socket can ever reach CDP directly. CDP therefore runs
  ON the laptop (node, loopback) inside the one batched SSH session.
  The daemon still bypasses the session guardian: it never runs cu.py
  session-driver, so Method 1's "another automation session is active"
  collision cannot happen; sends are serialised by a lock anyway.

Protocol (Unix socket, newline-delimited JSON):
  {"cmd": "ping"}   -> {"ok": true, "daemon": "speed-daemon", ...}
  {"cmd": "status"} -> uptime, sends served, master state, last error
  {"cmd": "send", "recipient": "mei"|"mochi", "message": str, "run": int}
    -> {"ok": bool, "outcome": "sent"|"already-sent"|"failed-unverified"|
        "aborted-pill-lost"|"error", "recipient", "run",
        "wall_start_hcm", "wall_end_hcm", "elapsed_s",
        "ipc_ms": ms from IPC receipt to SSH start,
        "ssh_ms": ms of the single SSH session,
        "node": <daemon-send.mjs JSON incl. its timings>,
        "pill": {acquired, verified, released, release_verified},
        "error": str|null}

Safety:
  - Pill is fail-closed (enforced laptop-side in daemon-one-send.sh):
    no verified pill, no send. Release is always attempted; the holder is
    pid-keyed by a laptop sleeper, so the overlay daemon prunes it if this
    process dies mid-send.
  - Sends are serialised by a lock (one at a time); a second concurrent
    request waits instead of colliding.
  - Never closes/navigates any tab; only Runtime.evaluate + key Enter on
    the named target id. Never touches Zen, Zalo, Teams, music, or the
    fixture server on port 8768.
  - Retry: on SSH transport failure (rc 255) the send is retried ONCE
    (mux self-heals by creating a fresh master). A retry is safe because
    daemon-send.mjs counts bubbles first: if the first attempt actually
    sent, the retry reports already-sent instead of double-sending.
  - If /tmp/daemon-send.mjs is missing on the laptop, the daemon re-pushes
    it (and daemon-one-send.sh) once and retries the send once.

Restart / survival:
  - daemon.sh start|stop|restart|status (one-command restart).
  - watchdog.py (cron, every minute) pings the socket and restarts the
    daemon if it does not answer. After a VM replacement, run:
        ~/workspace/speed-daemon/daemon.sh start
    (cron must be re-installed after a replacement too; see README.md).
"""
import json
import os
import shlex
import signal
import socket
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Asia/Ho_Chi_Minh")
except Exception:
    TZ = timezone.utc

HERE = Path(__file__).resolve().parent
REPO_SCRIPTS = Path.home() / "workspace" / "computer-use-wayland" / "scripts"
MUX_SSH = str(REPO_SCRIPTS / "ssh-laptop-mux.sh")
SSH_LAPTOP = str(Path.home() / "workspace" / "ssh-laptop.sh")
SOCK_PATH = HERE / "daemon.sock"
PID_FILE = HERE / "daemon.pid"
LOG_FILE = HERE / "daemon.log"
SEND_MJS = HERE / "daemon-send.mjs"
ONE_SEND_SH = HERE / "daemon-one-send.sh"

RECIPIENTS = {
    "mei": {"endpoint": "http://127.0.0.1:9224", "target": "709E2AE0F1CE0F9C9B57536626782E2D"},
    "mochi": {"endpoint": "http://127.0.0.1:9223", "target": "A25AA6F0370A00A174BC5304A333417D"},
}
HEARTBEAT_SECONDS = 60
SSH_TIMEOUT = 90


def hcm_now():
    return datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S %Z")


def log(event, **fields):
    rec = {"ts_hcm": hcm_now(), "event": event}
    rec.update(fields)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError:
        pass


class Daemon:
    def __init__(self):
        self.started = time.monotonic()
        self.started_hcm = hcm_now()
        self.lock = threading.Lock()
        self.sends = 0
        self.failures = 0
        self.last_error = None
        self.master_ok = None
        self.master_restarts = 0
        self._stop = threading.Event()

    # -- SSH helpers -----------------------------------------------------
    def ssh(self, remote_cmd, timeout=SSH_TIMEOUT):
        """One mux SSH call. Returns (rc, stdout, stderr, wall_ms)."""
        t = time.monotonic()
        p = subprocess.run([MUX_SSH, remote_cmd], capture_output=True,
                           text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr, (time.monotonic() - t) * 1000.0

    def push_laptop_files(self):
        """(Re)install the two laptop-side scripts via SSH stdin."""
        ok = True
        for local, remote in ((SEND_MJS, "/tmp/daemon-send.mjs"),
                              (ONE_SEND_SH, "/tmp/daemon-one-send.sh")):
            try:
                with open(local, "rb") as f:
                    data = f.read()
                p = subprocess.run([SSH_LAPTOP, "cat > %s" % remote],
                                   input=data, capture_output=True, timeout=60)
                if p.returncode != 0:
                    ok = False
                    log("push_failed", remote=remote, rc=p.returncode,
                        stderr=p.stderr.decode(errors="replace")[:300])
            except Exception as exc:
                ok = False
                log("push_failed", remote=remote, error=str(exc)[:300])
        if ok:
            log("laptop_files_pushed")
        return ok

    def ensure_laptop_files(self):
        rc, out, _err, _ms = self.ssh(
            "ls -l /tmp/daemon-send.mjs /tmp/daemon-one-send.sh 2>&1")
        if rc != 0 or "daemon-send.mjs" not in out or "daemon-one-send.sh" not in out:
            log("laptop_files_missing", ls_out=out[:300])
            return self.push_laptop_files()
        return True

    def ensure_master(self):
        """Warm the SSH master; one call creates it (~3.3s), later calls ~0.8s."""
        try:
            rc, _out, _err, ms = self.ssh("true", timeout=60)
            self.master_ok = (rc == 0)
            log("master_ensure", rc=rc, ms=round(ms, 1))
            return rc == 0
        except Exception as exc:
            self.master_ok = False
            log("master_ensure_failed", error=str(exc)[:200])
            return False

    def heartbeat_loop(self):
        while not self._stop.wait(HEARTBEAT_SECONDS):
            try:
                rc, _o, _e, ms = self.ssh("true", timeout=60)
                was_ok = self.master_ok
                self.master_ok = (rc == 0)
                if rc != 0:
                    self.master_restarts += 1
                    log("heartbeat_master_dead", rc=rc, ms=round(ms, 1))
                elif was_ok is False:
                    log("heartbeat_master_recovered", ms=round(ms, 1))
            except Exception as exc:
                self.master_ok = False
                self.master_restarts += 1
                log("heartbeat_failed", error=str(exc)[:200])

    # -- send ------------------------------------------------------------
    def do_send(self, recipient, message, run):
        t_recv = time.monotonic()
        wall_start = hcm_now()
        cfg = RECIPIENTS[recipient]
        remote = "bash /tmp/daemon-one-send.sh %s %s %s" % (
            shlex.quote(cfg["endpoint"]), shlex.quote(cfg["target"]),
            shlex.quote(message))
        result = None
        ssh_ms = 0.0
        attempts = 0
        while attempts < 2:
            attempts += 1
            t_ssh = time.monotonic()
            try:
                rc, out, err, wall_ms = self.ssh(remote)
            except subprocess.TimeoutExpired:
                rc, out, err, wall_ms = -1, "", "ssh timeout", SSH_TIMEOUT * 1000.0
            ssh_ms += wall_ms
            ipc_ms = (t_ssh - t_recv) * 1000.0
            if rc == 255 and attempts == 1:
                # Transport failure: mux self-heals (fresh master), retry once.
                log("send_ssh_255_retry", recipient=recipient, run=run)
                continue
            result = self._parse_send_out(out, rc, err)
            if result.get("stage") == "preflight" and "missing on laptop" in str(result.get("error", "")) and attempts == 1:
                log("send_laptop_file_missing_repush", recipient=recipient, run=run)
                if self.push_laptop_files():
                    continue
            break
        if result is None:
            result = {"ok": False, "outcome": "error",
                      "error": "ssh failed twice (rc 255, master did not recover)"}
        wall_end = hcm_now()
        elapsed = time.monotonic() - t_recv
        self.sends += 1
        if not result.get("ok"):
            self.failures += 1
            self.last_error = str(result.get("error"))[:300]
        resp = {
            "ok": bool(result.get("ok")),
            "outcome": result.get("outcome", "error"),
            "recipient": recipient, "run": run,
            "wall_start_hcm": wall_start, "wall_end_hcm": wall_end,
            "elapsed_s": round(elapsed, 3),
            "ipc_ms": round(ipc_ms, 1),
            "ssh_ms": round(ssh_ms, 1),
            "ssh_attempts": attempts,
            "node": {k: v for k, v in result.items()
                     if k in ("ground", "pre_count", "set", "focus", "v12",
                              "ms_total", "timings")},
            "pill": result.get("pill"),
            "error": result.get("error"),
        }
        log("send", recipient=recipient, run=run, outcome=resp["outcome"],
            elapsed_s=resp["elapsed_s"], ipc_ms=resp["ipc_ms"],
            ssh_ms=resp["ssh_ms"], attempts=attempts)
        return resp

    @staticmethod
    def _parse_send_out(out, rc, err):
        for line in reversed(out.strip().splitlines()):
            line = line.strip()
            if line.startswith("{"):
                try:
                    return json.loads(line)
                except ValueError:
                    continue
        return {"ok": False, "outcome": "error",
                "error": "no JSON from laptop one-send (rc=%d): %s" % (
                    rc, (out + err).strip()[-300:])}

    # -- server ----------------------------------------------------------
    def handle(self, req):
        cmd = req.get("cmd")
        if cmd == "ping":
            return {"ok": True, "daemon": "speed-daemon", "ts_hcm": hcm_now()}
        if cmd == "status":
            return {"ok": True, "daemon": "speed-daemon",
                    "started_hcm": self.started_hcm,
                    "uptime_s": round(time.monotonic() - self.started, 1),
                    "sends": self.sends, "failures": self.failures,
                    "master_ok": self.master_ok,
                    "master_restarts": self.master_restarts,
                    "last_error": self.last_error}
        if cmd == "send":
            recipient = req.get("recipient")
            message = req.get("message")
            run = req.get("run")
            if recipient not in RECIPIENTS:
                return {"ok": False, "outcome": "error",
                        "error": "unknown recipient %r" % (recipient,)}
            if not isinstance(message, str) or not message:
                return {"ok": False, "outcome": "error",
                        "error": "message must be a non-empty string"}
            if not isinstance(run, int):
                return {"ok": False, "outcome": "error",
                        "error": "run must be an int"}
            with self.lock:
                return self.do_send(recipient, message, run)
        return {"ok": False, "error": "unknown cmd %r" % (cmd,)}

    def _on_signal(self, signum, _frame):
        # R15 instrumentation: record WHY the daemon exits. SIGTERM is
        # what daemon.sh stop / every restarter sends; without this the
        # finally below never runs and the death leaves no record.
        # SIGKILL and VM death cannot be caught: no exit line for those
        # means "vanished", never "did not die" (see README blind spot).
        log("daemon_exit", reason=signal.Signals(signum).name,
            pid=os.getpid())
        self._stop.set()

    def serve(self):
        signal.signal(signal.SIGTERM, self._on_signal)
        signal.signal(signal.SIGINT, self._on_signal)
        # R15 instrumentation: double-start contention line. serve()
        # unlinks the socket file before bind, so a sequential second
        # start steals the socket instead of failing bind (the two
        # historical tracebacks were unlink/bind races). Detect the
        # contention here: if a live daemon already answers on the
        # existing socket, record it. Behavior unchanged: unlink and
        # bind proceed exactly as before.
        if SOCK_PATH.exists():
            try:
                probe = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                probe.settimeout(2)
                probe.connect(str(SOCK_PATH))
                probe.sendall(b'{"cmd": "ping"}\n')
                if probe.recv(4096):
                    log("daemon_bind_failed", pid=os.getpid(),
                        sock=str(SOCK_PATH),
                        error="double-start: live daemon already "
                              "answering on socket")
                probe.close()
            except OSError:
                pass
        PID_FILE.write_text(str(os.getpid()))
        try:
            SOCK_PATH.unlink()
        except FileNotFoundError:
            pass
        log("daemon_start", pid=os.getpid(),
            restarter=os.environ.get("DAEMON_RESTARTER", "direct/unknown"))
        self.ensure_laptop_files()
        self.ensure_master()
        threading.Thread(target=self.heartbeat_loop, daemon=True).start()
        srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            srv.bind(str(SOCK_PATH))
        except OSError as exc:
            # R15 instrumentation: double-start contention line. A
            # second daemon starting while one is live lands here.
            log("daemon_bind_failed", pid=os.getpid(),
                sock=str(SOCK_PATH), error=str(exc)[:200])
            raise
        srv.listen(16)
        srv.settimeout(1.0)
        log("daemon_listening", sock=str(SOCK_PATH))
        try:
            while not self._stop.is_set():
                try:
                    conn, _ = srv.accept()
                except socket.timeout:
                    continue
                threading.Thread(target=self._serve_conn, args=(conn,),
                                 daemon=True).start()
        finally:
            srv.close()
            try:
                SOCK_PATH.unlink()
            except FileNotFoundError:
                pass
            PID_FILE.unlink(missing_ok=True)
            log("daemon_stop")

    def _serve_conn(self, conn):
        try:
            buf = b""
            while not buf.endswith(b"\n"):
                chunk = conn.recv(65536)
                if not chunk:
                    break
                buf += chunk
                if len(buf) > 1_000_000:
                    break
            if not buf.strip():
                return
            req = json.loads(buf.decode("utf-8"))
            resp = self.handle(req)
            conn.sendall((json.dumps(resp, ensure_ascii=False) + "\n").encode("utf-8"))
        except Exception as exc:
            try:
                conn.sendall((json.dumps(
                    {"ok": False, "error": "daemon error: %s" % str(exc)[:300]})
                    + "\n").encode("utf-8"))
            except OSError:
                pass
        finally:
            conn.close()


if __name__ == "__main__":
    Daemon().serve()
