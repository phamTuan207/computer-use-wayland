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
  2. Y6c completion-marker check, REQUIRED (--repo <path> or
     Y13_REPO). It fetches origin and requires a todolist-push
     commit matching the exact marker (subject ^Y6c.*(nested|
     Wayland).*(run.*(DONE|complete)|verdict.*(REPRODUCED|NOT
     REPRODUCED|DONE|complete)), no "harness" in the subject,
     touching an improvements/worker-y6c-*.md file), NEWER than
     the newest abort marker (^Y6c.*(ABORT|abort)); an abort newer
     than the newest completion refuses. No repo path refuses:
     the operator's Y13_GO assertion alone is not a marker check.
  3. Ship-manifest check: the ship manifest md5 must equal the
     committed manifest md5 from origin/todolist-push (a stale
     but self-consistent ship refuses; the in-runner pin is
     self-referential, so this git comparison is the gate).
  4. Handover token /tmp/worker-y13-handover.json exists, is
     fresh (< 4 h) and names its basis. (The runner's preflight
     re-checks it.)
  5. Runner-quiet process check: no python process executing a
     run_*.py / run-nested* / hand_drive_e1.py script, other than
     this launcher's own ancestry. The check tokenizes argv, so
     bare-relative, flock -c, and shell -c launches are caught,
     and a mere path mention (md5sum /abs/run_foo.py) is not.
     A "codex" process whose cmdline mentions the E1 driver, a
     geckodriver, a browser profile path, or Marionette REFUSES;
     a plain codex process is a WARNING only.
  6. Predecessor ports free by TCP connect: Y9 8769/4449,
     Y8b 8767/4451, Y4d 8768/4448, and the 8770/4450 pair from
     Y14's gate range. Own ports 8771/4452 free too (a second Y13
     instance would hold them).
  7. No live geckodriver with a live parent (read
     /tmp/geckodriver-*.pid; a live geckodriver whose parent is
     alive means another driver session is running). Orphans
     (parent == 1) are warned only; the runner's preflight
     sweeps them.
  8. flock -w 60 on ~/.cache/agent-computer-use/zen_dom.lock,
     then exec `python3 run_codex_y5.py <args>` with the ship env
     set (server 8771, WD 4452, JSONL /tmp/worker-y13-live.jsonl,
     LIVE_OWNER_AWAY=1, PYTHONDONTWRITEBYTECODE=1 so the ship
     never writes .pyc). The launcher exits with the runner's
     exit code.

Usage (on the laptop, from /tmp/worker-y13-server):
  Y13_GO=1 python3 launch_y13.py --repo ~/computer-use-wayland all
  Y13_GO=1 python3 launch_y13.py --repo ~/computer-use-wayland 01 02
  Default runner arg: all.
"""

import hashlib
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
PREDECESSOR_PORTS = (8769, 4449, 8767, 4451, 8768, 4448, 8770, 4450)
OWN_PORTS = (8771, 4452)
# Y13f H3: tightened marker. Completion needs a run token or a
# verdict token; a subject containing "harness" is prep, never
# completion. Matched against SUBJECTS only (see check_marker),
# never via git log --grep (which matches body lines too).
MARKER_RE = re.compile(
    r"^Y6c.*(nested|Wayland).*(run.*(DONE|complete)"
    r"|verdict.*(REPRODUCED|NOT REPRODUCED|DONE|complete))")
ABORT_RE = re.compile(r"^Y6c.*(ABORT|abort)")


def _script_basename_is_runner(name):
    """True if a cmdline token's basename is a test-runner script
    (Y13f H2/H3). run_*.py covers Y9/Y13/Y14/Y4d; run-nested*
    covers Y6c's nested run (run-nested-pill.py, run-nested-wayland
    [.sh]: a hyphen, not run_); hand_drive_e1.py is E1's driver.
    Keep in sync with run_codex_y5.py (identical logic)."""
    if name == "hand_drive_e1.py":
        return True
    if name.startswith("run-nested"):
        return True
    return name.startswith("run_") and name.endswith(".py")


def _is_python_token(tok):
    base = tok.rsplit("/", 1)[-1]
    return (base in ("python", "python3")
            or base.startswith("python3.") or base.startswith("python2."))


def _argv_tokens(cmdline):
    """Split a /proc cmdline (NUL-separated) into argv tokens, and
    split any shell -c / flock -c argument on whitespace, so a
    bare-relative or wrapped launch is visible (Y13f H2)."""
    parts = [t for t in cmdline.split("\x00") if t]
    tokens = []
    i = 0
    while i < len(parts):
        if parts[i] == "-c" and i + 1 < len(parts):
            tokens.append("-c")
            tokens.extend(parts[i + 1].split())
            i += 2
        else:
            tokens.append(parts[i])
            i += 1
    return tokens


def _is_runner_cmdline(cmdline):
    """True if the cmdline EXECUTES a runner script (Y13f H2).
    The script token must be argv[0] (shebang exec), follow a python
    interpreter token, be the first word of a -c string, follow a
    python flag (-u) with a python token earlier, or (for non-.py
    run-nested scripts only) follow bash/sh. A mere path mention
    (md5sum /abs/run_foo.py) never matches. Keep in sync with
    run_codex_y5.py."""
    tokens = _argv_tokens(cmdline)
    for i, tok in enumerate(tokens):
        base = tok.rsplit("/", 1)[-1]
        if not _script_basename_is_runner(base):
            continue
        if i == 0:
            return True
        prev = tokens[i - 1]
        prev_base = prev.rsplit("/", 1)[-1]
        if _is_python_token(prev):
            return True
        if prev == "-c":
            return True
        if prev.startswith("-") and any(
                _is_python_token(t) for t in tokens[:i]):
            return True
        if not base.endswith(".py") and prev_base in ("bash", "sh"):
            return True
    return False


# Codex executor processes that must REFUSE, not just warn (Y13f,
# council 3 fix 2): a codex CLI whose cmdline mentions the E1
# driver, a geckodriver, a browser profile path, or Marionette is
# driving (or about to drive) a browser. Keep in sync with
# run_codex_y5.py.
CODEX_REFUSE_MARKERS = ("hand_drive_e1", "geckodriver", ".config/zen",
                        "zen-bin", ".mozilla", "remote-debugging",
                        "marionette")


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
    # Y13f L1: a non-dict token (list/string) and a non-numeric
    # asserted_at_unix crashed with an uncaught traceback, exit 1,
    # instead of REFUSED exit 2. Mirror the runner's handling.
    if not isinstance(tok, dict):
        _fail("handover token is not a JSON object")
    try:
        age = time.time() - float(tok.get("asserted_at_unix", 0))
    except (TypeError, ValueError):
        _fail("handover token asserted_at_unix is not numeric")
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
        flat = cmd.replace("\x00", " ").strip()
        if _is_runner_cmdline(cmd):
            offenders.append((pid, flat))
        elif "codex" in cmd.lower() and any(
                m in cmd.lower() for m in CODEX_REFUSE_MARKERS):
            # Y13f codex rule: a codex executor driving a browser
            # refuses (the between-arms E1 case is exactly what
            # this check exists for).
            offenders.append((pid, flat))
        elif "codex" in cmd.lower():
            codex_hits.append((pid, flat))
    for pid, cmd in codex_hits:
        print(f"[launch_y13] WARNING: codex process running "
              f"(pid {pid}): {cmd}", flush=True)
    if offenders:
        detail = "; ".join(f"pid {p}: {c}" for p, c in offenders)
        _fail(f"live slot busy, runner process running: {detail}")


def check_marker(repo):
    """Y13f H3: verify the exact Y6c completion (or abort) marker
    on todolist-push. --repo is REQUIRED (main() refuses without
    one): the old operator-assertion fallback let the documented
    launch path skip the marker check entirely.

    Matching is against SUBJECTS only: git log --format=%H%x09%ct
    %x09%s, regex applied in Python. The old --grep form matched
    body lines too (a body line "Y6c nested run DONE" under subject
    "Fix flake" passed). Subjects containing "harness" are prep,
    never completion. Freshness/ordering: the newest completion
    must be NEWER than the newest abort; an abort newer than the
    newest completion refuses (a stale completion from an earlier
    finished Y6c run must not satisfy the gate forever)."""
    if not repo:
        _fail("--repo is required: the Y6c marker check cannot run "
              "without a repo (set --repo or Y13_REPO)")
    if not os.path.isdir(os.path.join(repo, ".git")):
        _fail(f"--repo {repo} is not a git checkout")
    fetch = subprocess.run(
        ["git", "-C", repo, "fetch", "origin", "todolist-push"],
        capture_output=True, text=True, timeout=120)
    if fetch.returncode != 0:
        _fail(f"git fetch failed in {repo}: "
              f"{fetch.stderr.strip()[:200]}")
    log = subprocess.run(
        ["git", "-C", repo, "log", "origin/todolist-push",
         "--format=%H%x09%ct%x09%s", "--",
         "improvements/worker-y6c-*.md"],
        capture_output=True, text=True, timeout=60)
    if log.returncode != 0:
        _fail(f"git log failed in {repo}: "
              f"{log.stderr.strip()[:200]}")
    newest_completion = None
    newest_abort = None
    for line in log.stdout.splitlines():
        parts = line.split("\x09", 2)
        if len(parts) != 3:
            continue
        commit, ctime, subject = parts
        try:
            ctime = int(ctime)
        except ValueError:
            continue
        if ABORT_RE.search(subject):
            if newest_abort is None or ctime > newest_abort[1]:
                newest_abort = (commit, ctime, subject)
        elif ("harness" not in subject.lower()
                and MARKER_RE.search(subject)):
            if newest_completion is None or ctime > newest_completion[1]:
                newest_completion = (commit, ctime, subject)
    if newest_completion is None:
        _fail("no Y6c completion marker on todolist-push "
              "(checked subjects on the exact marker pattern)")
    if newest_abort is not None and newest_abort[1] >= newest_completion[1]:
        _fail(f"Y6c abort {newest_abort[0][:7]} "
              f"({newest_abort[2]}) is newer than the newest "
              f"completion {newest_completion[0][:7]}; refusing")
    print(f"[launch_y13] Y6c completion marker found: "
          f"{newest_completion[0]} ({newest_completion[2]})",
          flush=True)


def check_manifest(repo):
    """Y13f M1 (stale-ship half): compare the ship manifest md5
    against the committed manifest from git. The in-runner pin was
    declined as self-referential, so this comparison -- outside the
    ship, against git -- is the launch-time gate that refuses a
    stale but self-consistent ship (older runner + older manifest
    + older fixtures, which --verify-manifest alone accepts).
    Runs after check_marker, so origin/todolist-push is fresh."""
    ship_manifest = os.path.join(SHIP_DIR, "codex-y5-manifest.json")
    try:
        with open(ship_manifest, "rb") as f:
            ship_md5 = hashlib.md5(f.read()).hexdigest()
    except OSError as exc:
        _fail(f"ship manifest unreadable: {exc}")
    show = subprocess.run(
        ["git", "-C", repo, "show",
         "origin/todolist-push:tests/realistic/codex-y5-manifest.json"],
        capture_output=True, timeout=60)
    if show.returncode != 0:
        _fail("git show of the committed manifest failed: "
              f"{show.stderr.decode('utf-8', 'replace').strip()[:200]}")
    committed_md5 = hashlib.md5(show.stdout).hexdigest()
    if ship_md5 != committed_md5:
        _fail(f"ship manifest md5 {ship_md5} != committed manifest "
              f"md5 {committed_md5} (stale ship; re-stage from the "
              f"committed bytes with the regen script --stage)")
    print(f"[launch_y13] ship manifest md5 matches committed "
          f"({ship_md5})", flush=True)


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
    check_manifest(repo)
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
        # Y13f H1: the runner sets sys.dont_write_bytecode before
        # importing run_live; this env var is the same guard for
        # any other python this exec chain spawns.
        "PYTHONDONTWRITEBYTECODE": "1",
    })
    args = args or ["all"]
    cmd = ["flock", "-w", "60", LOCK_PATH,
           "python3", "run_codex_y5.py"] + args
    proc = subprocess.run(cmd, cwd=SHIP_DIR, env=env)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv))
