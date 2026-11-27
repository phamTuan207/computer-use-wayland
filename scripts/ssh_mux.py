#!/usr/bin/env python3
"""SPEED Step 0: persistent SSH multiplexing to the owner laptop (S0).

FINAL direction e05fc58, S0 row, on PROBE-S0 corrected numbers
(90eb8be): fresh SSH mean 4.667s (n=10), multiplexed mean 1.339s
(n=18), 3.49x, saving 3.328s per connection. The 460x claim and the
0.01s multiplexing figure are DEAD: 0.01s was a failed-fast connection
(rc=255, master down), never a live mux sample (best live sample 0.753s).

Hard requirements, all measured (PROBE-S0, idle tests 06:53-06:58
22/11/2026, soak A/B):

(a) Start the master with setsid/nohup WITHOUT -f. An explicitly
    started `ssh -M -f -N` master REFUSES every mux session
    ("Master refused session request: Permission denied") and dies on
    its own within 1-2 min (reproduced 2/2). Never use `ssh -f` here.
(b) ControlMaster=auto on clients, so a dead master self-heals: the
    next client falls back to one slow (~4.3s) but correct fresh
    connect and becomes the new master. No hard failure on death.
(c) Per-use liveness check plus restart-on-death. ensure_master()
    runs `-O check` before use and restarts a dead master; master
    death is the normal path, not an exception.
(d) ServerAliveInterval=15 on the master. Without it a master dies
    inside 90 s idle (idle test A: t90 5.582s, t300 4.861s, pid
    churned twice); with it the same master survives 300 s idle
    (idle test B: t90 1.172s, t300 0.883s, same pid 21189).
(e) Per-socket watchdog, not global: a half-dead master can hang
    rather than fail cleanly, and ControlPersist=600 can leave a
    stale master holding a dead Tailscale route. watchdog() checks
    THIS socket only.
(f) Log master death: every death and restart goes to the JSONL log
    with wall-clock Asia/Ho_Chi_Minh time.

Residual cost (PROBE-S0 F3): about 1.2-1.3s per session remains even
over a healthy master. It is per-SESSION server-side setup (sshd fork
plus session negotiation plus Tailscale proxy round trips), not shell
startup and not the mux layer (check-only is 0.06s). Three commands in
one session cost the same as one. Batching into one session is free;
every NEW session costs about 1.3s no matter what it runs. S0 caps at
about 3.3s saved per connection. Nothing here removes the residual.

Fallback contract: fresh SSH stays as the documented fallback AND the
recovery path (A5 MODIFY). run() retries ONCE on a connection-level
failure only (rc 255, or "Control socket" / "Master refused" in
stderr). A remote command failure (any other rc, including a remote
nonzero exit) is never retried: retrying a command that may already
have run is not safe.

Usage (library):
    from ssh_mux import SshMux
    mux = SshMux()
    result = mux.run(["echo", "ALIVE"])  # dict: rc, stdout, stderr,
        # secs, via ("mux" | "fresh-fallback" | "fresh"), master_pid,
        # restarted (bool)
    mux.ensure_master()  # liveness check + restart-on-death
    mux.watchdog()       # single-shot per-socket check + restart

Usage (CLI):
    python3 scripts/ssh_mux.py ensure   # start master if dead, print status
    python3 scripts/ssh_mux.py check    # liveness only, exit 0 alive / 1 dead
    python3 scripts/ssh_mux.py run -- <remote command...>
    python3 scripts/ssh_mux.py stop     # -O exit the master
    python3 scripts/ssh_mux.py watchdog # single-shot check + restart, for cron
    scripts/ssh-laptop-mux.sh <remote command...>  # shell drop-in

State lives under ~/.cache/agent-computer-use/ssh-mux/ (state.json with
the last known master pid, ssh-mux.jsonl with every death/restart/call
that asked for it). The control socket is /tmp/cm-s0-%r@%h:%p: its own
socket, never a probe socket (/tmp/cm-probe-*, /tmp/cm-soakb-*).
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone

# Laptop SSH target (user@host). Set CU_LAPTOP_SSH in the environment;
# no default is baked in so the repo carries no personal host info.
HOST = os.environ.get("CU_LAPTOP_SSH", "")
PROXY = f"python3 {Path.home()}/workspace/tailscale-proxy.py %h %p"
KEY = str(Path.home() / ".ssh" / "id_ed25519")
CONTROL_PATH = "/tmp/cm-s0-%r@%h:%p"
CONTROL_PERSIST = "600"
SERVER_ALIVE_INTERVAL = "15"
SERVER_ALIVE_COUNT_MAX = "3"
CONNECT_TIMEOUT = "25"

# Base options, identical to ~/workspace/ssh-laptop.sh, plus the mux
# options. The order matches ssh-laptop.sh so a diff stays readable.
BASE_OPTS = [
    "-o", "BatchMode=yes",
    "-o", f"ConnectTimeout={CONNECT_TIMEOUT}",
    "-o", "StrictHostKeyChecking=accept-new",
    "-o", "IdentitiesOnly=yes",
    "-o", f"ProxyCommand={PROXY}",
    "-i", KEY,
]
MUX_OPTS = [
    "-o", "ControlMaster=auto",
    "-o", f"ControlPath={CONTROL_PATH}",
    "-o", f"ControlPersist={CONTROL_PERSIST}",
    "-o", f"ServerAliveInterval={SERVER_ALIVE_INTERVAL}",
    "-o", f"ServerAliveCountMax={SERVER_ALIVE_COUNT_MAX}",
]

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("Asia/Ho_Chi_Minh")
except Exception:  # pragma: no cover - minimal env without tzdata
    TZ = timezone.utc


def hcm_now():
    return datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S %Z")


def _state_dir():
    return Path.home() / ".cache" / "agent-computer-use" / "ssh-mux"


class SshMux:
    """One multiplexed SSH channel to the owner laptop."""

    def __init__(self, host=HOST, state_dir=None, runner=None,
                 clock=time.monotonic):
        if not host:
            raise ValueError(
                "CU_LAPTOP_SSH is not set; set it to user@host for the "
                "laptop (e.g. CU_LAPTOP_SSH=user@host python3 "
                "scripts/ssh_mux.py ...)")
        self.host = host
        self.state_dir = Path(state_dir) if state_dir else _state_dir()
        self.log_path = self.state_dir / "ssh-mux.jsonl"
        self.state_path = self.state_dir / "state.json"
        self._runner = runner or subprocess.run
        self._clock = clock

    # -- logging ----------------------------------------------------
    def _log(self, event, **fields):
        row = {"event": event, "wall": hcm_now()}
        row.update(fields)
        try:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            line = (json.dumps(row, sort_keys=True, ensure_ascii=False,
                               allow_nan=False) + "\n").encode("utf-8")
            fd = os.open(str(self.log_path),
                         os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
            try:
                os.fchmod(fd, 0o600)
                os.write(fd, line)
            finally:
                os.close(fd)
        except Exception as exc:  # logging never breaks the call
            print(f"[ssh-mux] log failed: {exc}", file=sys.stderr)

    def _read_state(self):
        try:
            return json.loads(self.state_path.read_text())
        except (OSError, ValueError):
            return {}

    def _write_state(self, **fields):
        try:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            state = self._read_state()
            state.update(fields)
            self.state_path.write_text(
                json.dumps(state, sort_keys=True) + "\n")
            try:
                os.chmod(self.state_path, 0o600)
            except OSError:
                pass
        except Exception as exc:  # state is advisory, never fatal
            print(f"[ssh-mux] state write failed: {exc}", file=sys.stderr)

    # -- command construction ---------------------------------------
    def client_argv(self, remote_cmd):
        """Mux client argv: ControlMaster=auto, same socket as master."""
        return (["ssh"] + BASE_OPTS + MUX_OPTS + [self.host]
                + list(remote_cmd))

    def master_argv(self):
        """Master argv. NOTE: no -f flag. ssh -f masters refuse mux
        sessions on this path (PROBE-S0 F1). The caller starts this
        with setsid/nohup and disowns it; see start_master()."""
        return (["ssh"] + BASE_OPTS
                + ["-o", "ControlMaster=yes",
                   "-o", f"ControlPath={CONTROL_PATH}",
                   "-o", f"ControlPersist={CONTROL_PERSIST}",
                   "-o", f"ServerAliveInterval={SERVER_ALIVE_INTERVAL}",
                   "-o", f"ServerAliveCountMax={SERVER_ALIVE_COUNT_MAX}",
                   "-N", self.host])

    def check_argv(self):
        return (["ssh"] + BASE_OPTS
                + ["-o", f"ControlPath={CONTROL_PATH}",
                   "-O", "check", self.host])

    def exit_argv(self):
        return (["ssh"] + BASE_OPTS
                + ["-o", f"ControlPath={CONTROL_PATH}",
                   "-O", "exit", self.host])

    # -- liveness ----------------------------------------------------
    def check_master(self, timeout=30):
        """Return (alive, pid_or_None, rc). Liveness is judged by the
        -O check return code, never by speed: a slow check on a live
        master is still alive, and a fast failure is still dead."""
        try:
            proc = self._runner(self.check_argv(), capture_output=True,
                                text=True, timeout=timeout)
        except (OSError, subprocess.SubprocessError):
            return False, None, None
        pid = None
        text = (proc.stderr or "") + (proc.stdout or "")
        for token in text.replace("(", " ").replace(")", " ").split():
            if token.startswith("pid="):
                try:
                    pid = int(token[4:])
                except ValueError:
                    pid = None
                break
        return proc.returncode == 0, pid, proc.returncode

    def start_master(self, wait_s=30):
        """Start the master detached: setsid nohup, no -f, stdin from
        /dev/null, disowned. Then poll -O check until it answers or
        the wait runs out. Returns (started, pid_or_None)."""
        log_path = self.state_dir / "master.log"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        with open(log_path, "ab") as log:
            proc = subprocess.Popen(
                ["setsid", "nohup"] + self.master_argv(),
                stdin=subprocess.DEVNULL, stdout=log, stderr=log,
                start_new_session=False, close_fds=True)
            # setsid already detaches; no wait, no communicate.
            proc.poll()
        deadline = self._clock() + wait_s
        while self._clock() < deadline:
            alive, pid, _rc = self.check_master(timeout=10)
            if alive:
                self._write_state(master_pid=pid,
                                  master_started_wall=hcm_now())
                return True, pid
            time.sleep(1)
        return False, None

    def ensure_master(self):
        """Per-use liveness check plus restart-on-death.

        Returns {"alive": bool, "pid": int|None, "restarted": bool,
        "death_logged": bool}. A dead master is logged (previous pid
        from state, check rc) before the restart starts, so the death
        is on record even if the restart then fails."""
        alive, pid, rc = self.check_master()
        if alive:
            self._write_state(master_pid=pid,
                              master_last_seen_wall=hcm_now())
            return {"alive": True, "pid": pid, "restarted": False,
                    "death_logged": False}
        prev = self._read_state().get("master_pid")
        self._log("master_death", previous_pid=prev, check_rc=rc,
                  socket=CONTROL_PATH)
        started, new_pid = self.start_master()
        if started:
            self._log("master_restart", previous_pid=prev,
                      new_pid=new_pid)
        else:
            self._log("master_restart_failed", previous_pid=prev)
        return {"alive": started, "pid": new_pid, "restarted": True,
                "death_logged": True}

    def stop_master(self):
        """-O exit. Returns True when the master is gone afterwards."""
        try:
            self._runner(self.exit_argv(), capture_output=True,
                         text=True, timeout=30)
        except (OSError, subprocess.SubprocessError):
            pass
        alive, _pid, _rc = self.check_master(timeout=10)
        if not alive:
            self._log("master_stop")
            return True
        return False

    # -- running commands -------------------------------------------
    @staticmethod
    def _is_connection_failure(proc):
        """Connection-level failure only, judged by stderr markers.
        A bare rc of 255 is NOT enough: ssh passes a remote exit
        status of 255 through unchanged, so treating rc 255 alone as
        a connection failure would retry a command that already ran.
        The markers below are the ssh-side failures PROBE-S0 saw
        (master down: "Control socket connect: No such file or
        directory"; master refusing: "Master refused session
        request"). A remote nonzero exit never carries them and is
        never retried."""
        err = (proc.stderr or "").lower()
        return ("control socket" in err
                or "master refused" in err
                or "connection refused" in err
                or "connection timed out" in err
                or "connection reset" in err
                or "no route to host" in err
                or "ssh: connect" in err)

    def run(self, remote_cmd, timeout=120, retry_on_death=True):
        """Run one remote command over the mux master.

        Ensures the master first (liveness + restart-on-death), then
        runs the command and times it. On a connection-level failure
        restarts the master once and retries once. Returns a dict with
        rc, stdout, stderr, secs, via ("mux", "fresh-fallback", or
        "fresh"), master_pid, and restarted. via "fresh-fallback"
        means the master was dead and this call paid a fresh-connect
        cost (about 4.5s) while ControlMaster=auto created the new
        master; "fresh" means the retry also went fresh. secs is
        wall time from the caller, perf_counter, and includes the
        ensure step."""
        t0 = self._clock()
        ensured = self.ensure_master()
        via = "mux"
        if ensured["restarted"]:
            via = "fresh-fallback"
        restarted = ensured["restarted"]
        proc = self._runner(self.client_argv(remote_cmd),
                            capture_output=True, text=True, timeout=timeout)
        secs = round(self._clock() - t0, 3)
        if (retry_on_death and self._is_connection_failure(proc)
                and proc.returncode != 0):
            self._log("connection_failure_retry", rc=proc.returncode,
                      stderr=(proc.stderr or "")[:200])
            ensured = self.ensure_master()
            restarted = True
            t1 = self._clock()
            proc = self._runner(self.client_argv(remote_cmd),
                                capture_output=True, text=True,
                                timeout=timeout)
            secs = round(self._clock() - t0, 3)
            _ = t1
            via = "fresh-fallback" if ensured["restarted"] else via
        _alive, pid, _rc = self.check_master(timeout=10)
        return {"rc": proc.returncode, "stdout": proc.stdout,
                "stderr": proc.stderr, "secs": secs, "via": via,
                "master_pid": pid, "restarted": restarted}

    def watchdog(self):
        """Single-shot per-socket watchdog (for cron, every 5 min).

        Checks this socket's master and restarts it when dead, so a
        master that died idle is back before the next use pays a fresh
        connect. Returns the ensure_master() dict. Log rows:
        master_death / master_restart(_failed), same as ensure."""
        return self.ensure_master()


def _parse_remote(argv):
    if "--" in argv:
        return argv[argv.index("--") + 1:]
    return argv


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="S0 persistent SSH multiplexing to the owner laptop.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ensure", help="start the master if dead, print status")
    sub.add_parser("check", help="liveness only (exit 0 alive, 1 dead)")
    sub.add_parser("stop", help="stop the master with -O exit")
    sub.add_parser("watchdog", help="single-shot per-socket check+restart")
    p_run = sub.add_parser("run", help="run a remote command over mux")
    p_run.add_argument("remote", nargs=argparse.REMAINDER,
                       help="remote command after --")
    args = parser.parse_args(argv)
    mux = SshMux()
    if args.cmd == "ensure":
        status = mux.ensure_master()
        print(json.dumps({"wall": hcm_now(), **status},
                         sort_keys=True))
        return 0 if status["alive"] else 1
    if args.cmd == "check":
        alive, pid, rc = mux.check_master()
        print(json.dumps({"wall": hcm_now(), "alive": alive,
                          "pid": pid, "check_rc": rc}, sort_keys=True))
        return 0 if alive else 1
    if args.cmd == "stop":
        ok = mux.stop_master()
        print(json.dumps({"wall": hcm_now(), "stopped": ok},
                         sort_keys=True))
        return 0 if ok else 1
    if args.cmd == "watchdog":
        status = mux.watchdog()
        print(json.dumps({"wall": hcm_now(), **status},
                         sort_keys=True))
        return 0 if status["alive"] else 1
    if args.cmd == "run":
        remote = _parse_remote(args.remote)
        if not remote:
            parser.error("run needs a remote command after --")
        result = mux.run(remote)
        print(json.dumps({"wall": hcm_now(), **result}, sort_keys=True))
        return result["rc"]
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
