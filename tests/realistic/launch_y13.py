#!/usr/bin/env python3
"""Launch the Y13 codex-y5 live run under the live slot, with the
launch-time checks from plan v2 S3 wired into code (council A F4).

The runner's own preflight checks ports and geckodriver orphans,
but it runs AFTER flock is held, so it cannot enforce the
runner-quiet process check BEFORE the lock, and it cannot assert
the go order. This launcher does both, then execs the runner
under `flock -w 60`.

Checks, in order (any failure refuses with exit 2, never waits
silently):
  1. Y13_GO=1 in the environment. The operator (Y13) sets this
     only after (a) the exact Y6c completion marker is confirmed
     on todolist-push and (b) Muse's fresh go order at run time.
  2. Y6c completion-marker check, ONLY when a repo is given
     (--repo <path> or Y13_REPO). It fetches origin and requires a
     todolist-push commit matching the exact marker (message
     ^Y6c.*(nested|Wayland).*(complete|DONE|verdict|REPRODUCED|
     NOT REPRODUCED) touching an improvements/worker-y6c-*.md
     file), or an abort marker (^Y6c.*(ABORT|abort)). Without a
     repo path the check is skipped and the operator's Y13_GO
     assertion stands (the marker is verified by the operator via
     git before launching); with a repo path it is enforced here
     and its output is recorded in the launch log.
  3. Handover token /tmp/worker-y13-handover.json exists, is
     fresh (< 4 h) and names its basis. (The runner's preflight
     re-checks it.)
  4. Runner-quiet process check: no python process whose cmdline
     matches run_*.py or hand_drive_e1.py, other than this
     launcher's own ancestry. A "codex" cmdline match is a
     WARNING only (a Codex CLI may be doing unrelated work; the
     E1 driver is hand_drive_e1.py, which is covered).
  5. Predecessor ports free by TCP connect: Y9 8769/4449,
     Y8b 8767/4451. Own ports 8771/4452 free too (a second Y13
     instance would hold them).
  6. No live geckodriver with a live parent (read
     /tmp/geckodriver-*.pid; a live geckodriver whose parent is
     alive means another driver session is running). Orphans
     (parent == 1) are warned only; the runner's preflight
     sweeps them.
  7. flock -w 60 on ~/.cache/agent-computer-use/zen_dom.lock,
     then exec `python3 run_codex_y5.py <args>` with the ship env
     set (server 8771, WD 4452, JSONL /tmp/worker-y13-live.jsonl,
     LIVE_OWNER_AWAY=1). The launcher exits with the runner's
     exit code.

Usage (on the laptop, from /tmp/worker-y13-server):
  Y13_GO=1 python3 launch_y13.py [runner args...]
  Y13_GO=1 python3 launch_y13.py --repo ~/computer-use-wayland all
  Default runner arg: all.
"""

import json
import os
import re
import socket
import subprocess
import sys
import time

SHIP_DIR = "/tmp/worker-y13-server"
TOKEN_PATH = "/tmp/worker-y13-handover.json"
LOCK_PATH = os.path.expanduser(
    "~/.cache/agent-computer-use/zen_dom.lock")
TOKEN_TTL_S = 4 * 3600
PREDECESSOR_PORTS = (8769, 4449, 8767, 4451)
OWN_PORTS = (8771, 4452)
MARKER_RE = (r"^Y6c.*(nested|Wayland).*(complete|DONE|verdict|"
             r"REPRODUCED|NOT REPRODUCED)")
ABORT_RE = r"^Y6c.*(ABORT|abort)"
RUNNER_PATTERNS = (re.compile(r"(^|/)run_[^/\s]*\.py"),
                   re.compile(r"hand_drive_e1\.py"))


def _fail(msg):
    print(f"[launch_y13] REFUSED: {msg}", flush=True)
    sys.exit(2)


def _own_ancestry():
    """Pids of this process and every ancestor, from /proc."""
    pids = {os.getpid()}
    pid = os.getpid()
    while True:
        try:
            with open(f"/proc/{pid}/stat", "rb") as f:
                stat = f.read()
        except OSError:
            break
        try:
            ppid = int(stat[stat.rfind(b")") + 2:].split()[1])
        except (IndexError, ValueError):
            break
        if ppid <= 1 or ppid in pids:
            break
        pids.add(ppid)
        pid = ppid
    return pids


def _cmdline(pid):
    try:
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            return f.read().decode("utf-8", "replace")
    except OSError:
        return ""


def check_go():
    if os.environ.get("Y13_GO") != "1":
        _fail("Y13_GO is not 1: no recorded go order. Set Y13_GO=1 "
              "only after the exact Y6c completion marker is "
              "confirmed on todolist-push and Muse gave a fresh go "
              "order at run time.")


def check_token():
    try:
        with open(TOKEN_PATH, "r", encoding="utf-8") as f:
            tok = json.load(f)
    except OSError as exc:
        _fail(f"handover token missing/unreadable: {TOKEN_PATH}: {exc}")
    except json.JSONDecodeError as exc:
        _fail(f"handover token is not valid JSON: {exc}")
    age = time.time() - float(tok.get("asserted_at_unix", 0))
    if age < 0 or age > TOKEN_TTL_S:
        _fail(f"handover token is stale/aged {age:.0f}s "
              f"(TTL {TOKEN_TTL_S}s)")
    if not tok.get("basis"):
        _fail("handover token names no basis")
    print(f"[launch_y13] handover token OK, age {age:.0f}s, "
          f"basis: {tok['basis']}", flush=True)


def check_runner_quiet():
    own = _own_ancestry()
    offenders = []
    codex_hits = []
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        pid = int(name)
        if pid in own:
            continue
        cmd = _cmdline(pid)
        if not cmd:
            continue
        if any(p.search(cmd) for p in RUNNER_PATTERNS):
            offenders.append((pid, cmd.replace("\x00", " ").strip()))
        elif "codex" in cmd.lower():
            codex_hits.append((pid, cmd.replace("\x00", " ").strip()))
    for pid, cmd in codex_hits:
        print(f"[launch_y13] WARNING: codex process running "
              f"(pid {pid}): {cmd}", flush=True)
    if offenders:
        detail = "; ".join(f"pid {p}: {c}" for p, c in offenders)
        _fail(f"live slot busy, runner process running: {detail}")


def check_marker(repo):
    """Redteam H5: verify the exact Y6c completion (or abort)
    marker on todolist-push, when a repo path is given. Skipped
    (with a printed note) when no repo is given: the operator
    verifies the marker via git and asserts it with Y13_GO."""
    if not repo:
        print("[launch_y13] no --repo given; Y6c marker verified "
              "by the operator (Y13_GO assertion)", flush=True)
        return
    if not os.path.isdir(os.path.join(repo, ".git")):
        _fail(f"--repo {repo} is not a git checkout")
    fetch = subprocess.run(
        ["git", "-C", repo, "fetch", "origin", "todolist-push"],
        capture_output=True, text=True, timeout=120)
    if fetch.returncode != 0:
        _fail(f"git fetch failed in {repo}: "
              f"{fetch.stderr.strip()[:200]}")
    for label, pattern in (("completion", MARKER_RE),
                           ("abort", ABORT_RE)):
        log = subprocess.run(
            ["git", "-C", repo, "log", "origin/todolist-push",
             "--format=%H", "-E", f"--grep={pattern}", "--",
             "improvements/worker-y6c-*.md"],
            capture_output=True, text=True, timeout=60)
        if log.returncode != 0:
            _fail(f"git log failed in {repo}: "
                  f"{log.stderr.strip()[:200]}")
        hits = [h for h in log.stdout.split() if h]
        if hits:
            print(f"[launch_y13] Y6c {label} marker found: "
                  f"{hits[0]}", flush=True)
            return
    _fail("no Y6c completion/abort marker on todolist-push "
          "(checked git log with the exact marker patterns)")


def check_ports():
    for port in PREDECESSOR_PORTS:
        try:
            with socket.create_connection(("127.0.0.1", port),
                                          timeout=2) as s:
                s.close()
        except OSError:
            continue
        _fail(f"predecessor port {port} answers (another runner is "
              f"live or a stale server is up)")
    # Redteam H5: own ports must be free too; a second Y13
    # instance would hold 8771 (server) and 4452 (geckodriver).
    for port in OWN_PORTS:
        try:
            with socket.create_connection(("127.0.0.1", port),
                                          timeout=2) as s:
                s.close()
        except OSError:
            continue
        _fail(f"own port {port} answers (another Y13 instance is "
              f"live or a stale server is up)")


def _ppid_of(pid):
    try:
        with open(f"/proc/{pid}/stat", "rb") as f:
            stat = f.read()
    except OSError:
        return None
    try:
        return int(stat[stat.rfind(b")") + 2:].split()[1])
    except (IndexError, ValueError):
        return None


def check_geckodriver():
    import glob
    for pid_file in sorted(glob.glob("/tmp/geckodriver-*.pid")):
        try:
            pid = int(open(pid_file, "r").read().strip())
        except (OSError, ValueError):
            continue
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            continue
        except PermissionError:
            pass
        cmd = _cmdline(pid)
        if "geckodriver" not in cmd:
            continue
        ppid = _ppid_of(pid)
        if ppid is None:
            _fail(f"geckodriver {pid} alive but its ppid is "
                  f"unreadable (fail closed)")
        if ppid == 1:
            print(f"[launch_y13] WARNING: orphan geckodriver {pid} "
                  f"(parent 1); preflight will sweep it", flush=True)
            continue
        try:
            os.kill(ppid, 0)
            parent_alive = True
        except ProcessLookupError:
            parent_alive = False
        except PermissionError:
            parent_alive = True
        if parent_alive:
            _fail(f"live geckodriver {pid} with live parent "
                  f"{ppid} (another driver session is running)")


def main(argv):
    if not os.path.isfile(os.path.join(SHIP_DIR,
                                       "run_codex_y5.py")):
        _fail(f"run_codex_y5.py not found in {SHIP_DIR}; run this "
              f"launcher from the ship dir")
    args = list(argv[1:])
    repo = os.environ.get("Y13_REPO")
    if "--repo" in args:
        i = args.index("--repo")
        if i + 1 >= len(args):
            _fail("--repo needs a path argument")
        repo = args[i + 1]
        del args[i:i + 2]
    check_go()
    check_marker(repo)
    check_token()
    check_runner_quiet()
    check_ports()
    check_geckodriver()
    print("[launch_y13] launch checks passed; taking flock",
          flush=True)
    env = dict(os.environ)
    env.update({
        "LIVE_SERVER_ROOT": SHIP_DIR,
        "LIVE_SERVER_PORT": "8771",
        "LIVE_LOG": "/tmp/worker-y13-live.jsonl",
        "WD_PORT": "4452",
        "LIVE_OWNER_AWAY": "1",
    })
    args = args or ["all"]
    cmd = ["flock", "-w", "60", LOCK_PATH,
           "python3", "run_codex_y5.py"] + args
    proc = subprocess.run(cmd, cwd=SHIP_DIR, env=env)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv))
