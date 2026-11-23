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
  0. Module-top bootstrap (before ANY other import): script-form
     only (a -m/import exits 2 after deleting the entry .pyc
     files), a full-allowlist pre-import scan (R1: any file not
     a manifest path, any symlink, any unexpected dir refuses;
     a planted .so/.py would otherwise execute at import time),
     a PYTHONSAFEPATH enforcement (refuse without -P), and a
     PYTHONPATH refusal (refuse when PYTHONPATH is set and
     non-empty: -P does not clear PYTHONPATH, and a planted
     stdlib .py in a PYTHONPATH dir would execute at import).
     Entry .pyc files are EXEMPT from this scan only (they go
     to check 4, which adjudicates them); the runner's scan has
     no such exemption (it imports run_live). Run as
     `python3 -P -E launch_y13.py` so the ship dir is never added
     to sys.path from the environment AND all PYTHON* env vars
     are ignored at interpreter startup (-E): without -E, the
     interpreter itself imports warnings/re/functools/collections
     at startup, so a PYTHONPATH plant of one of those names
     executes before any module-top code runs (live-proved
     2026-11-22). The module-top refusal is defense-in-depth
     for an invocation without -E.
  1. Y13_GO=1 in the environment. The operator (Y13) sets this
     only after (a) the exact Y6c completion marker is confirmed
     on todolist-push and (b) Muse's fresh go order at run time.
  2. Y6c completion-marker check, REQUIRED (--repo <path> or
     Y13_REPO). It fetches origin and requires a todolist-push
     commit matching the exact marker (subject ^Y6c.*(nested|
     Wayland).*(run.*(DONE|complete)|verdict.*(REPRODUCED|NOT
     REPRODUCED|DONE|complete)), no "harness" in the subject,
     touching an improvements/worker-y6c-*.md file), NEWER than
     the newest abort marker (^Y6c.*(ABORT|abort)) BY GIT LOG
     --first-parent ORDER (first-parent branch position, not
     committer date: a forged old date no longer outranks a
     newer abort, and a side-branch marker never counts;
     markers must land as first-parent commits). The origin
     remote must be the known repo remote (an attacker fork
     refuses).
     The marker is a COORDINATION SIGNAL among pushers, not
     authentication: it orders completions vs aborts, it does
     not prove who pushed. No repo path refuses: the operator's
     Y13_GO assertion alone is not a marker check.
  3. Ship-manifest check: the ship manifest md5 must equal the
     committed manifest md5 from origin/todolist-push (a stale
     but self-consistent ship refuses; the in-runner pin is
     self-referential, so this git comparison is the gate). It
     also refuses any planted file or directory in the ship dir
     (any file/dir not in the manifest set, any non-entry .pyc,
     any symlink) and any missing allowlist file.
     Entry .pyc files are exempt here: check 4 adjudicates them.
  4. Entry-.pyc out-of-process check: for each entry .py
     (run_codex_y5.py, run_live.py, launch_y13.py), if a cached
     .pyc exists, compile the .py fresh in a separate
     `python3 -P -E` subprocess and compare the marshalled code
     objects; refuse on mismatch (a forged entry .pyc), and
     delete ONLY the entry .pyc files that match (a legitimate
     self-cache from a -m/import probe is removed so it cannot
     brick the run). This check RUNS (R2): the module-top scan
     and check 3 both exempt entry .pyc files so they reach it.
     A forged entry .pyc invoked via -m/import executes (the
     forged bytecode IS the running code), so no legitimate flow
     ever invokes -m/import on an unverified ship; this check is
     the control.
  5. Full-allowlist ship scan: every file must be a manifest
     path with a matching md5 (plus the manifest itself and
     SHIPPED.md); refuse any symlink, any .pyc at any depth
     (any entry .pyc remaining here means check 4 refused it
     or it appeared after check 4, so this is the backstop),
     any planted .py, and any non-prefix directory. An EMPTY
     __pycache__ dir is allowed (leftover from a probe whose
     .pyc files check 4 deleted).
  6. Handover token /tmp/worker-y13-handover.json: the launcher
     WRITES a fresh per-run token after the go order + marker
     pass AND after the ship passes its integrity checks
     (check_manifest, _check_entry_pyc, _scan_ship), never at
     prep time, and then checks it exists, is fresh (< 4 h)
     and names its basis. (The runner's preflight re-checks it.)
  7. Runner-quiet process check: no python process executing a
     run_*.py / run-nested* / hand_drive_e1.py script, other than
     this launcher's own ancestry. The check parses argv for
     real (wrappers incl. time/watch/xargs/ionice/chrt/numactl/
     systemd-run/unshare/su/runuser/prlimit/setarch/firejail/
     bwrap and a generic path-like unknown-wrapper rule, python
     flags and their values, -m by last dotted segment with
     pdb/pudb/trace special cases, -c by first-word semantics
     plus the exec-sink check with argv/env smuggling, all
     commands in a -c string, renamed/extensionless/symlinked
     copies by md5 against the manifest), so bare-relative, -m,
     flag-with-value, flock -c, and shell -c launches are
     caught, and a mere path mention (md5sum /abs/run_foo.py,
     echo/grep of a runner name, python -c 'import run_codex_y5')
     is not.
     A "codex" process whose cmdline mentions the E1 driver, a
     geckodriver, a browser profile path, or Marionette REFUSES;
     a plain codex process is a WARNING only (the warning
     matches the codex executable basename, not a raw
     substring).
  8. Predecessor ports free by TCP connect: Y9 8769/4449,
     Y8b 8767/4451, Y4d 8768/4448, and the 8770/4450 pair from
     Y14's gate range. Own ports 8771/4452 free too (a second Y13
     instance would hold them).
  9. No live geckodriver with a live parent (read
     /tmp/geckodriver-*.pid; a live geckodriver whose parent is
     alive means another driver session is running). Orphans
     (parent == 1) are warned only; the runner's preflight
     sweeps them.
  10. flock -w 60 on ~/.cache/agent-computer-use/zen_dom.lock,
     then exec `python3 -P -E run_codex_y5.py <args>` with the ship env
     set (server 8771, WD 4452, JSONL /tmp/worker-y13-live.jsonl,
     LIVE_OWNER_AWAY=1, PYTHONDONTWRITEBYTECODE=1 so the ship
     never writes .pyc, PYTHONSAFEPATH=1 so the ship dir is never
     added to sys.path from the environment, and
     PYTHONPATH/PYTHONHOME/PYTHONSTARTUP scrubbed from the exec
     env so a planted stdlib module cannot execute at import in
     the runner; -E makes the child ignore all PYTHON* vars even
     if the scrub is bypassed). The launcher exits with the
     runner's exit code.

Usage (on the laptop, from /tmp/worker-y13-server). Run with -P -E:
  Y13_GO=1 python3 -P -E launch_y13.py --repo ~/workspace/computer-use-wayland all
  Y13_GO=1 python3 -P -E launch_y13.py --repo ~/workspace/computer-use-wayland 01 02
  Default runner arg: all. --ship-dir DIR (or Y13_SHIP_DIR) points
  the launcher at a different ship dir; the default is the dir
  holding this file when it holds run_codex_y5.py + the manifest,
  else /tmp/worker-y13-server. --ship-dir takes its value as the
  NEXT arg, space-separated only (--ship-dir DIR, never
  --ship-dir=DIR); the value must be an existing directory.
"""

import os
import sys

# Y13g B1/B2: script-form-only guard + pre-import scan, before ANY
# other import. Only sys and os are imported here: sys is builtin
# and os is pre-loaded at interpreter startup, so neither can be
# shadowed by a planted file in the ship dir. Everything else
# (hashlib, json, re, socket, subprocess, time) is imported AFTER
# the scan passes. Same bootstrap as run_codex_y5.py.


# Provisional ship dir for the __spec__ guard (C1-F2): the guard
# must run BEFORE _derive_ship_dir (which reads sys.argv and may
# exit), so it uses the dir holding this file; the real SHIP_DIR
# is derived after the guard. For a -m/import probe the file's
# dir IS the ship dir (the .pyc sits next to the file), so the
# provisional dir is the right one for the guard's cleanup.
_SHIP_DIR = os.path.dirname(os.path.abspath(__file__))
_ENTRY_STEMS = ("run_codex_y5", "launch_y13", "run_live")


def _entry_pyc_paths():
    # All cache-tag variants of the entry .pyc files, via
    # os.walk (recursive) and ANY implementation tag, not just
    # the current one. The cache dir must be a REAL directory
    # inside the ship dir (realpath check): a symlinked
    # __pycache__ returns [] here, so the guard never deletes a
    # file OUTSIDE the ship (C2-4); the scan below refuses the
    # symlinked dir instead.
    cache = os.path.join(_SHIP_DIR, "__pycache__")
    out = []
    try:
        if os.path.realpath(cache) != os.path.join(
                os.path.realpath(_SHIP_DIR), "__pycache__"):
            return out
    except OSError:
        return out
    for _root, _dirs, _files in os.walk(cache, followlinks=False):
        for _name in _files:
            for _stem in _ENTRY_STEMS:
                if (_name.startswith(_stem + ".")
                        and _name.endswith(".pyc")):
                    out.append(os.path.join(_root, _name))
    return out


def _prune_empty_cache_dirs():
    # F6: after the guard deletes entry .pyc files, prune the
    # empty dirs it emptied (bottom-up rmdir), so a nested
    # __pycache__ dir left empty by the guard does not linger.
    # Nested dirs only: the top-level __pycache__ stays in
    # place (it is exempt when empty). Gated on the same
    # realpath check as _entry_pyc_paths: a symlinked cache dir
    # is never pruned.
    try:
        _cache = os.path.join(_SHIP_DIR, "__pycache__")
        if os.path.realpath(_cache) != os.path.join(
                os.path.realpath(_SHIP_DIR), "__pycache__"):
            return
    except OSError:
        return
    for _root, _dirs, _files in os.walk(_cache, topdown=False,
                                        followlinks=False):
        if _root == _cache:
            continue
        try:
            if not os.listdir(_root):
                os.rmdir(_root)
        except OSError:
            pass


# Script-form-only (Y13g B1 item 3, same guard as the runner):
# refuse at the very top when loaded as a module or via -m
# (__spec__ is not None). A -m/import writes the entry .pyc
# during get_code; the guard deletes the entry .pyc files
# (recursive, every cache-tag variant, best effort) so a -m
# probe does not brick the ship, then exits 2.
# A forged entry .pyc invoked via -m/import still executes (the
# forged bytecode IS the running code); the control for that is
# _check_entry_pyc below, which verifies the entry .pyc
# out-of-process before exec. -m and bare imports are unsupported
# invocation forms; the live launch path is always this file run
# as a script, which execs the runner as a script. This guard
# runs BEFORE _derive_ship_dir (C1-F2), against the provisional
# _SHIP_DIR above.
if globals().get("__spec__") is not None:
    for _p in _entry_pyc_paths():
        try:
            os.unlink(_p)
        except OSError:
            pass
    # F6: prune the empty dirs the guard just emptied.
    _prune_empty_cache_dirs()
    print("run as a script (python3 launch_y13.py), not with -m "
          "and not via import", file=sys.stderr, flush=True)
    sys.exit(2)


def _derive_ship_dir():
    """Y13g Amend 4: the ship dir comes from --ship-dir, then
    Y13_SHIP_DIR, then the dir holding this file if it holds
    run_codex_y5.py + the manifest, else the hardcoded fallback
    (the probes' ship dir, /tmp/worker-y13-server). The launcher
    only ever checks the ship dir it derived; probes stage a
    tampered ship at a temp path and point --ship-dir at it.
    --ship-dir takes its value as the NEXT arg, space-separated
    only; the value must be a non-empty existing directory (a
    dangling --ship-dir used to silently eat the next arg, e.g.
    `--ship-dir all` made SHIP_DIR="all"). The file-dir branch
    refuses a repo-tree path: if this file lives inside a git
    checkout (a .git within 3 parents), it is the repo source
    tree, not a staged ship; cd to the ship dir or pass
    --ship-dir (C3-1). The = forms (--ship-dir=DIR, --repo=DIR)
    are refused up front: the exact-token parsing below (and
    main's --repo parsing) silently ignores them, so a = form
    would launch against the wrong dir or repo."""
    _args = sys.argv[1:]
    # C3-1: refuse the = forms first, before any other parsing.
    for _t in _args:
        if _t.startswith("--ship-dir=") or _t.startswith("--repo="):
            print("[launch_y13] REFUSED: use the space-separated "
                  f"form {_t.split('=', 1)[0]} DIR, not {_t!r}",
                  file=sys.stderr, flush=True)
            sys.exit(2)
    if "--ship-dir" in _args:
        _i = _args.index("--ship-dir")
        if _i + 1 >= len(_args):
            print("[launch_y13] REFUSED: --ship-dir needs a value "
                  "(space-separated, an existing directory)",
                  file=sys.stderr, flush=True)
            sys.exit(2)
        _v = _args[_i + 1]
        if not _v or not os.path.isdir(_v):
            print("[launch_y13] REFUSED: --ship-dir value "
                  f"{_v!r} is not an existing directory",
                  file=sys.stderr, flush=True)
            sys.exit(2)
        return _v
    _env = os.environ.get("Y13_SHIP_DIR")
    if _env:
        if not os.path.isdir(_env):
            print("[launch_y13] REFUSED: Y13_SHIP_DIR value "
                  f"{_env!r} is not an existing directory",
                  file=sys.stderr, flush=True)
            sys.exit(2)
        return _env
    _here = os.path.dirname(os.path.abspath(__file__))
    _p = _here
    for _ in range(4):
        if os.path.isdir(os.path.join(_p, ".git")):
            print("[launch_y13] REFUSED: this looks like the repo "
                  "tree, not a staged ship; cd to the ship dir or "
                  "pass --ship-dir", file=sys.stderr, flush=True)
            sys.exit(2)
        _parent = os.path.dirname(_p)
        if _parent == _p:
            break
        _p = _parent
    if (os.path.isfile(os.path.join(_here, "run_codex_y5.py"))
            and os.path.isfile(os.path.join(
                _here, "codex-y5-manifest.json"))):
        return _here
    return "/tmp/worker-y13-server"


SHIP_DIR = _derive_ship_dir()
_SHIP_DIR = SHIP_DIR


# Y13g R1 (C2-1): enforce PYTHONSAFEPATH, same as the runner.
# -P is not optional: without it sys.path[0] is the ship dir
# and a planted stdlib .so/.py executes at import time (a
# planted hashlib.so executed at the launcher's post-scan
# `import hashlib` under the bare form). The guard above already
# ran, so a -m probe still gets its script-form message and its
# .pyc deleted; a bare DIRECT invocation refuses here.
if not sys.flags.safe_path:
    print("run with python3 -P -E (PYTHONSAFEPATH=1, PYTHON* env "
          "ignored): the bare form is refused, a planted file "
          "could execute at import",
          file=sys.stderr, flush=True)
    sys.exit(2)


# Y13g R3 (F2): refuse a poisoned PYTHONPATH at the module top.
# -P removes sys.path[0] only; it does NOT clear PYTHONPATH, so
# a planted stdlib .py in a PYTHONPATH dir executes at the first
# post-scan import (a planted shlex.py proved it in the runner
# under -P, rc 0, manifest_ok true). PYTHONPATH must be unset or
# empty to run. (Residual, documented: without -E, PYTHONHOME and
# sitecustomize.py fire at interpreter startup, before any
# module-top code runs, and so do PYTHONPATH plants of the names
# the interpreter itself imports at startup (warnings, re,
# functools, collections, live-proved 2026-11-22), so no
# in-process check can close that channel; invoke with -E as
# documented, which makes the interpreter ignore all PYTHON*
# vars. The launcher also scrubs PYTHONPATH/PYTHONHOME/
# PYTHONSTARTUP from the exec env it passes to the runner, and
# from the _check_entry_pyc fresh-compile subprocess env.)
if os.environ.get("PYTHONPATH"):
    print("run with PYTHONPATH unset or empty (or with -E, which "
          "ignores PYTHONPATH): -P does not clear PYTHONPATH, "
          "and a planted stdlib module in a PYTHONPATH dir would "
          "execute at import",
          file=sys.stderr, flush=True)
    sys.exit(2)


_SHIP_FILES = {
    # Y13g R1 (C2-1): the FULL allowlist: the manifest's 27 rel
    # paths PLUS the manifest itself and SHIPPED.md (29 files in
    # a staged ship). Identical set to the runner's _SHIP_FILES;
    # if a ship file is ever added or removed, update this set
    # in BOTH entry points AND regen the manifest.
    "run_codex_y5.py", "launch_y13.py", "run_live.py",
    "codex-y5-manifest.json",
    "codex-y5/SHIPPED.md",
    "codex-y5/test-01-git-workflow.md",
    "codex-y5/test-02-music-player.md",
    "codex-y5/test-03-password-vault.md",
    "codex-y5/test-04-maps-directions.md",
    "codex-y5/test-05-calendar-recurring.md",
    "codex-y5/test-06-video-editor.md",
    "codex-y5/test-07-chat-search.md",
    "codex-y5/test-08-spreadsheet-pivot.md",
    "codex-y5/test-09-file-search-tag.md",
    "codex-y5/test-10-extension-settings.md",
    "codex-y5/simulate.mjs",
    "codex-y5/check.mjs",
    "codex-y5/README.md",
    "codex-y5/check-dashes.py",
    "codex-y5/fixtures/test-01-git-workflow.html",
    "codex-y5/fixtures/test-02-music-player.html",
    "codex-y5/fixtures/test-03-password-vault.html",
    "codex-y5/fixtures/test-04-maps-directions.html",
    "codex-y5/fixtures/test-05-calendar-recurring.html",
    "codex-y5/fixtures/test-06-video-editor.html",
    "codex-y5/fixtures/test-07-chat-search.html",
    "codex-y5/fixtures/test-08-spreadsheet-pivot.html",
    "codex-y5/fixtures/test-09-file-search-tag.html",
    "codex-y5/fixtures/test-10-extension-settings.html",
}
_SHIP_DIRS = {"codex-y5", "codex-y5/fixtures"}
# The LAUNCHER scan exempts a top-level __pycache__ entry-stem
# .pyc (any tag): _check_entry_pyc adjudicates it (verify +
# delete if legitimate, refuse if forged) before exec. The
# launcher never imports ship modules, so the exemption is safe
# here. The RUNNER sets this False (it imports run_live).
_EXEMPT_ENTRY_PYC_FROM_SCAN = True


def _is_entry_pyc_rel(rel):
    # True for a top-level __pycache__ entry-stem .pyc, any tag.
    if not rel.startswith("__pycache__/"):
        return False
    _name = rel[len("__pycache__/"):]
    if "/" in _name:
        return False
    return any(_name.startswith(_s + ".") and _name.endswith(".pyc")
               for _s in _ENTRY_STEMS)


def _is_exempt_cache_dir(rel, full):
    # A top-level __pycache__ dir is allowed (not refused as an
    # unexpected dir) ONLY when every entry in it is an entry
    # .pyc (or it is empty). The FILES inside are still handled
    # by the file loop below (exempted for _check_entry_pyc).
    if rel != "__pycache__":
        return False
    try:
        _names = os.listdir(full)
    except OSError:
        return False
    for _n in _names:
        if not any(_n.startswith(_s + ".") and _n.endswith(".pyc")
                   for _s in _ENTRY_STEMS):
            return False
    return True


def _refuse_tampered_ship():
    # Y13g R1 (C2-1): full-allowlist pre-import scan using ONLY
    # os.path. Refuses ANY file whose rel path is not a manifest
    # path in _SHIP_FILES (a planted .so/.py/.txt would otherwise
    # execute at import time, before any check runs), ANY
    # symlink, and ANY directory that is not a manifest parent
    # dir (except the exempted top-level __pycache__ above).
    # Entry .pyc files are exempt from THIS scan only: they go
    # to _check_entry_pyc (check 4), which verifies them
    # out-of-process before exec (R2). Recovery hint (C3-4):
    # the message names the fix (delete the named files and
    # directories, or re-stage).
    found = []
    # C2-4: every allowlist file must exist as a regular file. A
    # symlink is NOT flagged here (the walk below flags it as
    # "symlink"); only a genuinely absent path, or a non-file
    # non-symlink in its place, is "missing-file".
    for _rel in sorted(_SHIP_FILES):
        _full = os.path.join(_SHIP_DIR, _rel)
        if not os.path.isfile(_full) and not os.path.islink(_full):
            found.append((_rel, "missing-file"))
    for _root, _dirs, _files in os.walk(_SHIP_DIR, followlinks=False):
        _rel_root = os.path.relpath(_root, _SHIP_DIR)
        if _rel_root == ".":
            _rel_root = ""
        for _name in _dirs:
            _rel = (_rel_root + "/" + _name) if _rel_root else _name
            _full = os.path.join(_root, _name)
            if os.path.islink(_full):
                found.append((_rel, "symlink"))
            elif (_rel not in _SHIP_DIRS
                    and not _is_exempt_cache_dir(_rel, _full)):
                found.append((_rel, "unexpected-dir"))
        for _name in _files:
            _rel = (_rel_root + "/" + _name) if _rel_root else _name
            _full = os.path.join(_root, _name)
            if os.path.islink(_full):
                found.append((_rel, "symlink"))
            elif _rel not in _SHIP_FILES:
                if (_EXEMPT_ENTRY_PYC_FROM_SCAN
                        and _is_entry_pyc_rel(_rel)):
                    continue
                elif _name.endswith(".pyc"):
                    found.append((_rel, "pyc"))
                elif _name.endswith(".py"):
                    found.append((_rel, "planted-py"))
                else:
                    found.append((_rel, "unexpected-file"))
    if found:
        _kinds = sorted({k for _, k in found})
        _kind = _kinds[0] if len(_kinds) == 1 else "mixed"
        _files = ", ".join(sorted(p for p, _ in found))
        print(f"[launch_y13] REFUSED: tampered ship dir {_SHIP_DIR}: "
              f"{_kind}: {_files}. Fix: delete the named files and "
              "directories, or re-stage the ship with the regen "
              "script", file=sys.stderr, flush=True)
        sys.exit(2)


_refuse_tampered_ship()

sys.dont_write_bytecode = True

import hashlib
import json
import re
import shlex
import socket
import subprocess
import time

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
# Y13g Amend 1: the git remote the marker check trusts. Read from
# the real checkout at fix time (git remote get-url origin).
KNOWN_REMOTE_URL = "https://github.com/phamTuan207/computer-use-wayland.git"


def _script_basename_is_runner(name):
    """True if a cmdline token's basename is a test-runner script
    (Y13f H2/H3, kept by Y13g B3). run_*.py covers Y9/Y13/Y14/Y4d;
    run-nested* covers Y6c's nested run (run-nested-pill.py,
    run-nested-wayland[.sh]: a hyphen, not run_, so the old run_
    pattern was blind to it); hand_drive_e1.py is E1's driver.
    Generic on purpose: in this project every run_*.py is a
    runner, and the check is fail-closed. A renamed copy is NOT
    caught here; it is caught by the md5 leg in
    _token_is_runner_script."""
    if name == "hand_drive_e1.py":
        return True
    if name.startswith("run-nested"):
        return True
    return name.startswith("run_") and name.endswith(".py")


def _is_python_token(tok):
    base = tok.rsplit("/", 1)[-1]
    return (base in ("python", "python3", "pypy", "pypy3")
            or base.startswith("python3.") or base.startswith("python2.")
            or base.startswith("pypy3."))


# Y13g B3 (C2 AMEND 3/4, redteam B3; R3 round 2; R3 round 3):
# the Y13f tokenizer used a prev-token heuristic and missed -m
# forms, flag-with-value forms, renamed/extensionless/symlinked
# copies, and -c exec forms. This block parses the command the
# way a shell + python would: wrappers first (env/nohup/setsid/
# timeout/flock/bash -c, plus nice/stdbuf/taskset/sudo/uv run,
# time/watch/xargs/ionice/chrt/numactl/systemd-run/unshare/su/
# runuser/prlimit/setarch/firejail/bwrap, exec -a, and a generic
# path-like unknown-wrapper rule), then a real python argv parse
# (flags and their values skipped, bundled short flags, -m by
# last dotted segment with pdb/pudb/trace special cases,
# python3 - as stdin, python3 -- - as stdin, first positional
# is the script candidate), then identity by name OR by md5
# against the manifest. -c strings go through the exec-sink
# check (exec(, eval(, os.system(, os.popen(, os.exec/spawn,
# subprocess.* incl. getoutput/getstatusoutput, runpy.run_path(,
# pty.spawn(, pdb.run() plus a .py path md5 check, with
# __import__/from-import/alias normalization and sys.argv[N] /
# os.environ[...] smuggling resolved against the enclosing
# python's effective sys.argv and environ). All commands in a
# -c string are scanned, not just the first. A mere path mention
# (md5sum, cat, git) never matches: only a token in an execution
# position is examined. Keep in sync with run_codex_y5.py
# (identical block, AST-verified); _SHIP_DIR is the ship dir in
# both files.
_RUNNER_MODULE_NAMES = (
    "run_codex_y5", "run_live", "run_agyq2", "run_batch3",
    "run_agy_y2", "run-nested-pill", "hand_drive_e1",
)
_RUNNER_MANIFEST_PATHS = ("run_codex_y5.py", "launch_y13.py", "run_live.py")
_RUNNER_MD5S = None


def _shlex_tokens(s):
    """Split a -c command string on shell words (shlex, whitespace
    fallback), then split each token on ;, &, | (C2-3: a separator
    glued mid-token, 'python3 run_codex_y5.py;echo done', is the
    same command as a spaced one; shlex keeps it glued). The
    separators are KEPT as their own tokens (;, &, |, &&, ||) so
    _command_executes_runner can scan EVERY command in the string,
    not just the first (F3(f): a runner as the second command, or
    after a pipe, counts). A ';' inside a QUOTED string is split
    too (fail-closed: a quoted separator is rare, and the name leg
    still needs a runner token to match). shlex is imported at the
    module top (before the sys.path insert), never lazily here, so
    a planted shlex cannot load (C2-1)."""
    try:
        parts = shlex.split(s)
    except Exception:
        parts = s.split()
    out = []
    for p in parts:
        for _piece in re.split(r"(&&|\|\||[;&|])", p):
            if _piece:
                out.append(_piece)
    return out


def _runner_md5s():
    """md5s of the known runner .py files, from the ship manifest
    (cached). An unreadable manifest yields an empty set: the md5
    leg is then off, but the name leg still catches every named
    form, and the launcher's check_manifest refuses a bad
    manifest before exec."""
    global _RUNNER_MD5S
    if _RUNNER_MD5S is not None:
        return _RUNNER_MD5S
    md5s = set()
    try:
        import json
        with open(os.path.join(_SHIP_DIR,
                               "codex-y5-manifest.json"),
                  "rb") as f:
            man = json.load(f)
        for entry in man.get("files", []):
            if (isinstance(entry, dict)
                    and entry.get("path") in _RUNNER_MANIFEST_PATHS
                    and entry.get("md5")):
                md5s.add(entry["md5"])
    except Exception:
        pass
    _RUNNER_MD5S = md5s
    return md5s


def _path_is_runner_copy(tok, cwd=None):
    """True if the token resolves (symlinks followed, relative
    against cwd) to a file whose md5 is a known runner md5
    (redteam B3(4)). A renamed, extensionless, or symlinked copy
    of a runner is caught here, name-independently. An
    unresolvable or unreadable path is NOT a copy: the file being
    executed exists on disk in every real case, so an unresolvable
    path is a race or a namespace we cannot read, not a runner.
    A FIFO is NOT a copy either (isfile False; a FIFO streaming
    runner bytes cannot be md5'd without blocking). Files over
    10 MB are not read (the runners are ~200 KB; a bigger file
    is not a runner copy). The ports + flock backstop still
    applies. A renamed .sh copy is NOT in the md5 set (the set
    holds only the 3 .py runner md5s from this ship's manifest);
    that gap is documented, not closed (C2-10)."""
    import hashlib
    path = tok
    if not os.path.isabs(path):
        path = os.path.join(cwd or os.getcwd(), path)
    try:
        real = os.path.realpath(path)
        if not os.path.isfile(real):
            return False
        if os.path.getsize(real) > 10 * 1024 * 1024:
            return False
        with open(real, "rb") as f:
            digest = hashlib.md5(f.read()).hexdigest()
    except OSError:
        return False
    return digest in _runner_md5s()


def _token_is_runner_script(tok, cwd=None):
    """True if a script-candidate token executes a runner: by
    generic runner name, by bare module name (extensionless form:
    python3 run_codex_y5), or by md5 (renamed/extensionless/
    symlinked copy)."""
    base = tok.rsplit("/", 1)[-1]
    if _script_basename_is_runner(base):
        return True
    stem = base[:-3] if base.endswith(".py") else base
    if stem in _RUNNER_MODULE_NAMES:
        return True
    return _path_is_runner_copy(tok, cwd)


def _c_code_executes_runner(code, cwd=None, argv=None, environ=None):
    """True if a python -c code string executes a runner. First
    the code is parsed as a shell command (a nested 'python3
    run_codex_y5.py', e.g. via a -c inside -c, is caught by the
    same recursive parse). Then the exec-sink case: a -c string
    that hands code to exec(, eval(, os.system(, a subprocess.*
    call, runpy.run_path(, an os.exec/spawn call, os.popen(,
    pty.spawn(, or pdb.run( executes whatever it names, so a
    runner script basename in the code, or a quoted .py path
    that resolves to a runner copy (md5), counts. A bare
    'import run_codex_y5' is NOT an execution (an import runs
    the script-form guard and exits 2, never the suite), and
    neither is runpy.run_module (same guard) nor a mere mention
    such as print('run_codex_y5.py') (no sink). The code is
    NORMALIZED before the sink check: __import__('X').Y( becomes
    X.Y(, `from X import Y` makes a bare Y( count as X.Y(, and
    `import X as A` rewrites A. as X. (F3(c): from-import, alias,
    and __import__ forms are live evasions.) argv/env smuggling
    (F3(b)): when a sink is present, a path that comes from
    sys.argv[N] or os.environ[...] / os.getenv(... counts when
    the argv/env value is a runner script. argv is the enclosing
    python's effective sys.argv (['-c', arg1, ...], so sys.argv[N]
    is argv[N]); environ is the process environ dict. When
    argv/environ is None (unknown, e.g. an unreadable
    /proc/PID/environ), an unresolvable reference is treated as a
    runner (fail-closed). When environ is a dict without the key,
    the reference would raise KeyError in the real program, so it
    does not count. LIMIT (documented): a -c string that builds
    the runner name by string concatenation so NO single literal
    is a full runner path (exec(open('run_codex_'+'y5.py').read()))
    is not caught unless one literal is the full name; the ports
    + flock backstop applies."""
    inner = _shlex_tokens(code)
    if inner and _command_executes_runner(inner, cwd, environ):
        return True
    _code = code
    # __import__('X').Y( -> X.Y( (any quote style, spaces allowed).
    _code = re.sub(r"__import__\(\s*['\"]([A-Za-z0-9_.]+)['\"]\s*\)",
                   r"\1", _code)
    # `from X import Y [, Z ...] [as A]` -> a bare Y( counts as X.Y(.
    for _m in re.finditer(r"from\s+([A-Za-z0-9_.]+)\s+import\s+"
                         r"([^;\n]+)", _code):
        _mod = _m.group(1)
        _names = _m.group(2)
        _alias = None
        _am = re.search(r"\bas\s+([A-Za-z_][A-Za-z0-9_]*)\s*$", _names)
        if _am:
            _alias = _am.group(1)
            _names = _names[:_am.start()]
        for _part in _names.split(","):
            _part = _part.strip()
            if not _part:
                continue
            _pm = re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s+as\s+"
                           r"([A-Za-z_][A-Za-z0-9_]*)", _part)
            if _pm:
                _name, _call = _pm.group(1), _pm.group(2)
            elif _alias:
                _name, _call = _part, _alias
            else:
                _name = _call = _part
            if not re.match(r"[A-Za-z_][A-Za-z0-9_]*$", _call or ""):
                continue
            _code = re.sub(r"\b" + re.escape(_call) + r"\(",
                           _mod + "." + _name + "(", _code)
    # `import X as A` -> rewrite A. as X. (word-boundary aware).
    for _m in re.finditer(r"import\s+([A-Za-z0-9_.]+)\s+as\s+"
                         r"([A-Za-z_][A-Za-z0-9_]*)", _code):
        _mod, _alias = _m.group(1), _m.group(2)
        _code = re.sub(r"\b" + re.escape(_alias) + r"\.",
                       _mod + ".", _code)
    _SINKS = ("exec(", "eval(", "os.system(", "os.popen(",
              "os.execl(", "os.execle(", "os.execlp(", "os.execlpe(",
              "os.execv(", "os.execve(", "os.execvp(", "os.execvpe(",
              "os.posix_spawn(", "os.posix_spawnp(",
              "os.spawnl(", "os.spawnle(", "os.spawnlp(",
              "os.spawnlpe(", "os.spawnv(", "os.spawnve(",
              "os.spawnvp(", "os.spawnvpe(",
              "subprocess.call(", "subprocess.run(",
              "subprocess.Popen(", "subprocess.check_output(",
              "subprocess.check_call(", "subprocess.getoutput(",
              "subprocess.getstatusoutput(", "runpy.run_path(",
              "pty.spawn(", "pdb.run(")
    if not any(_s in _code for _s in _SINKS):
        return False
    for m in re.finditer(r"run_[A-Za-z0-9_.\-]*\.py|"
                         r"run-nested[A-Za-z0-9_.\-]*|"
                         r"hand_drive_e1\.py", _code):
        if _script_basename_is_runner(m.group(0)):
            return True
    for m in re.finditer(r"['\"]([^'\"]+\.py)['\"]", _code):
        if _path_is_runner_copy(m.group(1), cwd):
            return True
    # argv/env smuggling: a sink whose path comes from sys.argv[N]
    # or os.environ[...] / os.getenv(... counts when the value is
    # a runner script (or the value is unknown: fail-closed).
    for _m in re.finditer(r"sys\.argv\[(-?\d+)\]", _code):
        _n = int(_m.group(1))
        if argv is None:
            return True
        if _n >= 0:
            _val = argv[_n] if _n < len(argv) else None
        else:
            _val = argv[_n] if -_n <= len(argv) else None
        if _val is not None and _token_is_runner_script(_val, cwd):
            return True
    for _m in re.finditer(r"os\.environ\[\s*['\"]([^'\"]+)['\"]\s*\]",
                          _code):
        _key = _m.group(1)
        if environ is None:
            return True
        if _key in environ and _token_is_runner_script(
                environ[_key], cwd):
            return True
    for _m in re.finditer(r"os\.(?:getenv|environ\.get)\(\s*"
                         r"['\"]([^'\"]+)['\"]", _code):
        _key = _m.group(1)
        if environ is None:
            return True
        if _key in environ and _token_is_runner_script(
                environ[_key], cwd):
            return True
    return False


def _m_module_is_runner(mod, args, start, cwd=None):
    """True if a -m module argument executes a runner. A known
    runner module (by last dotted segment) counts. `pdb` and
    `pudb` count when a following arg is a runner script: a
    debugger runs its script with __spec__ None, so the -m
    guard does NOT fire (C2-3, proved live for pdb). `trace`
    counts the same way (trace runs the named script), EXCEPT
    in --module mode: --module / -m in the trace args means the
    module is IMPORTED, so the guard fires (safe). trace's value
    flags (--ignore-module, --ignore-dir, --coverdir, --file,
    -f, -C) skip their following value; a bare '-' is skipped.
    runpy/cProfile/profile are NOT counted: they set __spec__,
    so the guard kills those forms before the suite runs (-m
    profile is live-proved: guard fires, rc 0, no manifest_ok).
    -m unittest and -m timeit are NOT counted either (timeit
    exec crashes with NameError in the exec namespace,
    live-proved, rc 1, no run). A .py -m argument is an invalid
    form and cannot execute."""
    if mod.endswith(".py"):
        return False
    last = mod.rsplit(".", 1)[-1]
    if last in _RUNNER_MODULE_NAMES:
        return True
    if last in ("pdb", "pudb"):
        _skip = False
        for _t in args[start:]:
            if _skip:
                _skip = False
                continue
            if _t == "-c":
                _skip = True
                continue
            if _t.startswith("-"):
                continue
            if _token_is_runner_script(_t, cwd):
                return True
        return False
    if last == "trace":
        # --module mode imports the module (guard fires); any
        # --module / -m token, or a short-flag bundle containing
        # 'm', means module mode. (A -f value of literally "-m"
        # would be misread; that form is vanishingly exotic.)
        for _t in args[start:]:
            if _t in ("--module", "-m"):
                return False
            if _t.startswith("-") and not _t.startswith("--") \
                    and "m" in _t[1:]:
                return False
        _skip = False
        for _t in args[start:]:
            if _skip:
                _skip = False
                continue
            if _t in ("--ignore-module", "--ignore-dir",
                      "--coverdir", "--file", "-f", "-C"):
                _skip = True
                continue
            if _t.startswith("-"):
                continue
            if _token_is_runner_script(_t, cwd):
                return True
        return False
    return False


_PY_NO_VALUE = frozenset("bBdeEhiIOqSsuv")


def _python_executes_runner(args, cwd=None, environ=None):
    """Real python argv parse (C2 AMEND 3, R3). Skips interpreter
    flags and their values (-u -B -E -s -v -W <val> -X <val> -O
    -c <code> -m <mod>, -- separator, bundled short flags such as
    -uW, -Bc, -um, -Bum, and attached values such as -Wignore,
    -Xdev, -c..., -m...); the first positional is the script
    candidate. A -m module is a runner when its LAST dotted
    segment is a known runner module (pkg.run_codex_y5 counts;
    run_codex_y5.py as a -m argument is an invalid form and
    cannot execute), or when it is pdb/pudb/trace with a runner
    script following. `python3 -` (stdin) is treated as a
    possible runner (fail-closed: piped runner bytes execute),
    and so is `python3 -- -` (F3(a): the post--- position is
    still a script position). A -c string receives the enclosing
    python's effective sys.argv (['-c', arg1, ...]) and environ
    so it can resolve sys.argv[N] / os.environ[...] smuggling
    (F3(b)); environ None means unknown (fail-closed)."""
    i = 0
    n = len(args)
    while i < n:
        tok = args[i]
        if tok == "--":
            i += 1
            break
        if tok == "-c":
            if i + 1 >= n:
                return False
            return _c_code_executes_runner(
                args[i + 1], cwd, ["-c"] + list(args[i + 2:]),
                environ)
        if tok == "-m":
            if i + 1 >= n:
                return False
            return _m_module_is_runner(args[i + 1], args, i + 2, cwd)
        if tok in ("-W", "-X"):
            i += 2
            continue
        if tok.startswith("--check-hash-based-pycs"):
            i += 1 if "=" in tok else 2
            continue
        if tok.startswith("--"):
            i += 1
            continue
        if tok.startswith("-") and len(tok) > 1:
            # Short-flag token: a run of no-value flags, then
            # optionally ONE value flag (c/m/W/X) whose value is
            # the rest of this token or the next token (C1-F3,
            # C2-3: -uc, -Bc, -um, -Bum, -uW, -uX, -iuW). A pure
            # no-value bundle (-uB) or an unknown flag (-Z, -P)
            # is the whole token as flags, never a script.
            chars = tok[1:]
            j = 0
            while j < len(chars) and chars[j] in _PY_NO_VALUE:
                j += 1
            if j < len(chars) and chars[j] in "WXcm":
                flag = chars[j]
                rest = chars[j + 1:]
                if flag == "c":
                    if rest:
                        return _c_code_executes_runner(
                            rest, cwd, ["-c"] + list(args[i + 1:]),
                            environ)
                    if i + 1 >= n:
                        return False
                    return _c_code_executes_runner(
                        args[i + 1], cwd,
                        ["-c"] + list(args[i + 2:]), environ)
                if flag == "m":
                    mod = rest if rest else (
                        args[i + 1] if i + 1 < n else None)
                    if mod is None:
                        return False
                    _start = i + 1 if rest else i + 2
                    return _m_module_is_runner(mod, args, _start, cwd)
                # W/X: the value is the rest, or the next token;
                # skip it and keep parsing for the script.
                i += 1 if rest else 2
                continue
            i += 1
            continue
        if tok == "-":
            return True
        return _token_is_runner_script(tok, cwd)
    if i < n:
        # Post--- position: a '-' here is still stdin (a possible
        # runner), not a flag (F3(a)).
        if args[i] == "-":
            return True
        return _token_is_runner_script(args[i], cwd)
    return False


def _is_timeout_dur(t):
    # timeout durations accept a unit suffix and decimals: 60,
    # 60s, 1m, 1.5m, 90. (C2-3: "60s"/"1m" were misread as the
    # command.) Hex durations are accepted too (0x10, 0x10s),
    # and "inf" (GNU timeout's infinite duration). "1h30m" is
    # NOT a valid timeout duration (timeout takes one number
    # with one suffix), so it is not a duration here.
    if t == "inf":
        return True
    if t and t[-1] in "smhd":
        t = t[:-1]
    if not t:
        return False
    if t[:2] in ("0x", "0X"):
        return len(t) > 2 and all(
            c in "0123456789abcdefABCDEF" for c in t[2:])
    return t.replace(".", "", 1).isdigit()


def _command_executes_runner(tokens, cwd=None, environ=None):
    """Recursive shell-ish parse: strips wrappers (env VAR=1
    (and -S <cmd>), nohup, setsid, exec [-a name] [-l] [-c],
    command, timeout <dur>, flock <flags> <lock> [-c <cmd>],
    bash/sh -c <cmd> or <script>, and the command wrappers
    nice, stdbuf, taskset, sudo, uv run, time, watch, xargs,
    ionice, chrt, numactl, systemd-run, unshare, su, runuser,
    prlimit, setarch, firejail, bwrap, each with its flags and
    values skipped), then a python token hands off to
    _python_executes_runner, and any other token reaching this
    point is argv[0] of the command and is checked as a shebang
    exec (./run_codex_y5.py). A path-like argv[0] that is not a
    known wrapper, python, or shell, followed by a python token,
    a -c string, or a runner script token, is a renamed
    interpreter / shell / unknown wrapper around that command
    (F3(e)). Only a token in an execution position is ever
    examined, so 'echo python3 run_codex_y5.py' and 'grep
    python3 ...' do NOT match, while 'exec python3
    run_codex_y5.py' does. Commands separated by ;, &, |, &&,
    || are ALL checked (F3(f)): a runner as the second command,
    or after a pipe, counts. environ is the process environ
    dict (or None when unknown) for -c argv/env smuggling."""
    # Multi-command: split on ;, &, |, &&, || and check EVERY
    # command (F3(f)). _shlex_tokens keeps the separators as
    # tokens; a plain argv list has none, so the split is a
    # no-op there. Each slice is re-checked recursively.
    _seps = (";", "&", "|", "&&", "||")
    if any(_t in _seps for _t in tokens):
        i = 0
        n = len(tokens)
        while i < n:
            while i < n and tokens[i] in _seps:
                i += 1
            if i >= n:
                return False
            j = i
            while j < n and tokens[j] not in _seps:
                j += 1
            if _command_executes_runner(tokens[i:j], cwd, environ):
                return True
            i = j
        return False
    # Known non-executing basenames (F3(e)): hashing or reading a
    # runner file is not executing it, so a path-like argv[0]
    # with one of these basenames never triggers the generic
    # wrapper rule below.
    _NO_EXEC = frozenset((
        "md5sum", "sha1sum", "sha256sum", "sha512sum", "sha384sum",
        "sha224sum", "b2sum", "cksum", "cat", "grep", "egrep",
        "fgrep", "wc", "head", "tail", "less", "more", "ls",
        "sort", "uniq", "cut", "awk", "sed", "tr", "stat", "file"))
    i = 0
    n = len(tokens)
    while i < n:
        tok = tokens[i]
        base = tok.rsplit("/", 1)[-1]
        if base == "env":
            i += 1
            while i < n:
                t = tokens[i]
                if t in ("-S", "--split-string") and i + 1 < n:
                    # env -S "VAR=1 python3 run_codex_y5.py":
                    # the value is a command string, parsed
                    # recursively.
                    return _command_executes_runner(
                        _shlex_tokens(tokens[i + 1]), cwd, environ)
                if t.startswith("--split-string="):
                    return _command_executes_runner(
                        _shlex_tokens(t.split("=", 1)[1]),
                        cwd, environ)
                if t.startswith("-S") and len(t) > 2:
                    return _command_executes_runner(
                        _shlex_tokens(t[2:]), cwd, environ)
                if t.startswith("-"):
                    if t == "-u" and i + 1 < n:
                        i += 2
                        continue
                    i += 1
                    continue
                if "=" in t:
                    i += 1
                    continue
                break
            continue
        if base in ("nohup", "setsid", "command"):
            i += 1
            if base == "command" and i < n and \
                    tokens[i] in ("-v", "-V"):
                # `command -v NAME` only prints the path; it
                # never executes NAME.
                return False
            while i < n and tokens[i].startswith("-"):
                i += 1
            continue
        if base == "exec":
            # exec [-cl] [-a name] [command]: -a takes a value,
            # -l/-c are bare flags (C2-3: `exec -a` misread the
            # name as the command).
            i += 1
            while i < n:
                t = tokens[i]
                if t == "-a" and i + 1 < n:
                    i += 2
                    continue
                if t.startswith("-"):
                    i += 1
                    continue
                break
            continue
        if base in ("nice", "stdbuf", "taskset", "sudo", "uv"):
            # Command wrappers (C2-3/redteam F3): each executes
            # the command that follows its flags and values.
            i += 1
            _value_flags = {
                "nice": ("-n", "--adjustment"),
                "stdbuf": ("-o", "-e", "-i", "--output",
                           "--error", "--input"),
                "taskset": ("-c", "--cpu-list"),
                "sudo": ("-u", "--user", "-g", "--group"),
                "uv": ("-p", "--python", "--with", "--group",
                       "--extra"),
            }[base]
            while i < n:
                t = tokens[i]
                if base == "uv" and t == "run":
                    i += 1
                    continue
                if t in _value_flags and i + 1 < n:
                    i += 2
                    continue
                if t.startswith("-"):
                    i += 1
                    continue
                if base == "sudo" and "=" in t:
                    # sudo VAR=1 python3 ...: VAR= assignments
                    # after sudo are env, not the command.
                    i += 1
                    continue
                break
            # taskset takes a bare CPU mask (hex/number) before
            # the command; it is not the command.
            if base == "taskset" and i < n:
                _t = tokens[i]
                _m = _t[2:] if _t.startswith("0x") else _t
                if _m.replace(",", "").replace("-", "").isdigit():
                    i += 1
            continue
        if base in ("time", "watch", "xargs", "ionice", "numactl",
                    "systemd-run", "unshare", "prlimit", "firejail"):
            # More command wrappers (F3(e), redteam FRESH): each
            # executes the command that follows its flags and
            # values. Value flags take a separate next token;
            # attached values (-n1, --interleave=all) and bare
            # flags are skipped by the "-" check.
            i += 1
            _value_flags = {
                "time": ("-f", "--format", "-o", "--output"),
                "watch": ("-n", "--interval"),
                "xargs": ("-I", "--replace", "-n", "--max-args",
                          "-P", "--max-procs", "-s", "--max-chars",
                          "-L", "--max-lines", "-d", "--delimiter",
                          "-a", "--arg-file", "-E", "--eof"),
                "ionice": ("-c", "--class", "-n", "--classdata",
                           "-p", "--pid"),
                "numactl": ("--cpunodebind", "--physcpubind",
                            "--interleave", "--preferred",
                            "--membind", "--cpubind", "--file",
                            "--length", "--offset", "--shmmode",
                            "--touch", "-m", "-i", "-p", "-C",
                            "-N"),
                "systemd-run": ("--unit", "--description",
                                "--slice", "--property", "--uid",
                                "--gid", "--nice",
                                "--working-directory",
                                "--service-type",
                                "--timer-property", "--on-active",
                                "--on-boot", "--on-startup",
                                "--on-unit-active",
                                "--on-unit-inactive", "--setenv"),
                "unshare": ("--map-user", "--map-group",
                            "--setgroups"),
                "prlimit": ("--nproc", "--as", "--cpu", "--fsize",
                            "--nofile", "--rss", "--rttime",
                            "--rtprio", "--sigpending", "--stack",
                            "--core", "--data", "--locks",
                            "--memlock", "--msgqueue", "--nice",
                            "-p", "--pid"),
                "firejail": ("--profile",),
            }[base]
            while i < n:
                t = tokens[i]
                if t in _value_flags and i + 1 < n:
                    i += 2
                    continue
                if t.startswith("-"):
                    i += 1
                    continue
                break
            continue
        if base == "bwrap":
            # bwrap: --bind/--ro-bind/--dev-bind/--symlink/
            # --setenv take TWO following args; --dir/--tmpfs/
            # --proc/--dev/--chdir/--hostname/--uid/--gid/
            # --unsetenv take one. Other --flags are bare.
            i += 1
            _two = ("--bind", "--ro-bind", "--dev-bind",
                    "--symlink", "--setenv")
            _one = ("--dir", "--tmpfs", "--proc", "--dev",
                    "--chdir", "--hostname", "--uid", "--gid",
                    "--unsetenv")
            while i < n:
                t = tokens[i]
                if t in _two and i + 2 < n:
                    i += 3
                    continue
                if t in _one and i + 1 < n:
                    i += 2
                    continue
                if t.startswith("-"):
                    i += 1
                    continue
                break
            continue
        if base == "su":
            # su [user] [-c cmd]: -c takes a command string
            # (parsed recursively), wherever it appears; the
            # first bare token is the user, not the command.
            i += 1
            _seen_user = False
            while i < n:
                t = tokens[i]
                if t == "-c" and i + 1 < n:
                    return _command_executes_runner(
                        _shlex_tokens(tokens[i + 1]), cwd, environ)
                if t in ("-s", "--shell", "-g", "--group",
                         "-G") and i + 1 < n:
                    i += 2
                    continue
                if t.startswith("-"):
                    i += 1
                    continue
                if not _seen_user:
                    _seen_user = True
                    i += 1
                    continue
                break
            continue
        if base == "runuser":
            # runuser -u user [-c cmd] command: the user comes
            # via -u, so the first bare token IS the command.
            i += 1
            while i < n:
                t = tokens[i]
                if t == "-c" and i + 1 < n:
                    return _command_executes_runner(
                        _shlex_tokens(tokens[i + 1]), cwd, environ)
                if t in ("-u", "--user", "-g", "--group",
                         "-s", "--shell") and i + 1 < n:
                    i += 2
                    continue
                if t.startswith("-"):
                    i += 1
                    continue
                break
            continue
        if base == "setarch":
            # setarch [options] personality command: skip flags,
            # then one bare token (the personality/arch), then
            # the command.
            i += 1
            while i < n and tokens[i].startswith("-"):
                i += 1
            if i < n:
                i += 1
            continue
        if base == "chrt":
            # chrt [flags] priority command: skip flags, then
            # one bare numeric priority, then the command.
            i += 1
            while i < n:
                t = tokens[i]
                if t in ("-p", "--pid") and i + 1 < n:
                    i += 2
                    continue
                if t.startswith("-"):
                    i += 1
                    continue
                break
            if i < n and tokens[i].isdigit():
                i += 1
            continue
        if base == "timeout":
            i += 1
            while i < n:
                t = tokens[i]
                if t in ("-k", "--kill-after", "-s", "--signal"):
                    i += 2
                    continue
                if t.startswith("-") or _is_timeout_dur(t):
                    i += 1
                    continue
                break
            continue
        if base == "flock":
            i += 1
            while i < n:
                t = tokens[i]
                if t == "-c":
                    if i + 1 >= n:
                        return False
                    return _command_executes_runner(
                        _shlex_tokens(tokens[i + 1]), cwd, environ)
                if t in ("-w", "--timeout", "-E",
                         "--conflict-exit-code"):
                    i += 2
                    continue
                if t.startswith("-"):
                    i += 1
                    continue
                break
            if i >= n:
                return False
            i += 1
            if i >= n:
                return False
            if tokens[i] == "-c":
                if i + 1 >= n:
                    return False
                return _command_executes_runner(
                    _shlex_tokens(tokens[i + 1]), cwd, environ)
            return _command_executes_runner(tokens[i:], cwd, environ)
        if base in ("bash", "sh", "zsh", "dash"):
            j = i + 1
            while j < n:
                if tokens[j] == "-c" and j + 1 < n:
                    return _command_executes_runner(
                        _shlex_tokens(tokens[j + 1]), cwd, environ)
                if tokens[j].startswith("-"):
                    j += 1
                    continue
                return _token_is_runner_script(tokens[j], cwd)
            return False
        if _is_python_token(tok):
            return _python_executes_runner(tokens[i + 1:], cwd,
                                           environ)
        # Renamed interpreter / shell / unknown wrapper (F3(e)):
        # a path-like argv[0] (contains '/') that is not a known
        # wrapper, python, or shell, followed by a python token,
        # a -c string, or a runner script token, is a wrapper
        # around that command. A bare-word unknown wrapper (no
        # slash) is NOT treated this way: a bare-word generic
        # rule would break 'bash -c echo mention' (False).
        if "/" in tok and base not in _NO_EXEC:
            _rest = tokens[i + 1:]
            if _rest:
                _first = _rest[0]
                if _is_python_token(_first):
                    return _python_executes_runner(
                        _rest[1:], cwd, environ)
                if _first == "-c" and len(_rest) > 1:
                    return _command_executes_runner(
                        _shlex_tokens(_rest[1]), cwd, environ)
                if _token_is_runner_script(_first, cwd):
                    return True
        return _token_is_runner_script(tok, cwd)
    return False


def _argv_tokens(cmdline):
    """Split a /proc cmdline (NUL-separated) into argv tokens.
    (Y13g B3: the Y13f version expanded -c arguments inline,
    which conflated 'echo python3 run_codex_y5.py' with a real
    execution; -c strings are now parsed recursively by
    _command_executes_runner instead.)"""
    return [t for t in cmdline.split("\x00") if t]


def _is_runner_cmdline(cmdline, cwd=None, environ=None):
    """True if the cmdline EXECUTES a runner script (Y13g B3).

    Parses the command like a shell + python would (see
    _command_executes_runner): wrappers, real python argv parse,
    -m by last dotted segment (plus pdb/pudb/trace), -c by
    first-word semantics plus the exec-sink check (with argv/env
    smuggling resolved against the enclosing python's effective
    sys.argv and environ), renamed/extensionless/symlinked
    copies by md5 against the manifest. A mere path mention
    (md5sum /abs/run_foo.py, echo/grep of a runner name, python
    -c 'import run_codex_y5') never matches. cwd (the process's
    /proc/<pid>/cwd) resolves relative script paths for the md5
    leg; without it, relative paths resolve against this
    process's cwd. environ (the process's /proc/<pid>/environ
    as a dict, or None when unknown) resolves os.environ[...]
    references in -c code; None is fail-closed. Keep in sync
    with run_codex_y5.py (identical block)."""
    return _command_executes_runner(_argv_tokens(cmdline), cwd,
                                    environ)


def _is_codex_process(cmdline):
    """True if the cmdline EXECUTES a codex binary (C2-6): the
    first non-wrapper token's basename is 'codex', or it is a
    token ending in '/codex' in that execution position. A bare
    'codex' token elsewhere (grep codex, echo codex), a path
    merely containing a codex directory
    (/path/codex/run_codex_y5.py), and a codex path that is an
    ARGUMENT (ls /usr/bin/codex, grep /usr/bin/codex) do NOT
    count. Wrapper tokens (env VAR=1, sudo, nice, timeout, and
    the other wrappers _command_executes_runner strips) are
    skipped with their flags/values, so 'env codex --help'
    counts. Used by the launcher's WARNING branch only; the
    refuse branch keeps the fail-closed substring rule
    (C2 AMEND 6). Kept in both files so the shared block stays
    identical."""
    parts = _argv_tokens(cmdline)
    if not parts:
        return False
    # Strip leading wrapper tokens (with flag/value skipping),
    # mirroring _command_executes_runner, to find the first
    # non-wrapper token (the executed command).
    _wrappers = ("env", "nohup", "setsid", "exec", "command",
                 "nice", "stdbuf", "taskset", "sudo", "uv",
                 "timeout", "flock", "time", "watch", "xargs",
                 "ionice", "chrt", "numactl", "systemd-run",
                 "unshare", "su", "runuser", "prlimit", "setarch",
                 "firejail", "bwrap")
    _value_flags = {
        "env": ("-u",), "sudo": ("-u", "--user", "-g", "--group"),
        "nice": ("-n", "--adjustment"),
        "stdbuf": ("-o", "-e", "-i", "--output", "--error",
                   "--input"),
        "taskset": ("-c", "--cpu-list"),
        "uv": ("-p", "--python", "--with", "--group", "--extra"),
        "timeout": ("-k", "--kill-after", "-s", "--signal"),
        "flock": ("-w", "--timeout", "-E",
                  "--conflict-exit-code"),
        "time": ("-f", "--format", "-o", "--output"),
        "watch": ("-n", "--interval"),
        "xargs": ("-I", "--replace", "-n", "--max-args", "-P",
                  "--max-procs", "-s", "--max-chars", "-L",
                  "--max-lines", "-d", "--delimiter", "-a",
                  "--arg-file", "-E", "--eof"),
        "ionice": ("-c", "--class", "-n", "--classdata", "-p",
                   "--pid"),
        "numactl": ("--cpunodebind", "--physcpubind",
                    "--interleave", "--preferred", "--membind",
                    "--cpubind", "--file", "--length", "--offset",
                    "--shmmode", "--touch", "-m", "-i", "-p",
                    "-C", "-N"),
        "systemd-run": ("--unit", "--description", "--slice",
                        "--property", "--uid", "--gid", "--nice",
                        "--working-directory", "--service-type",
                        "--timer-property", "--on-active",
                        "--on-boot", "--on-startup",
                        "--on-unit-active", "--on-unit-inactive",
                        "--setenv"),
        "unshare": ("--map-user", "--map-group", "--setgroups"),
        "prlimit": ("--nproc", "--as", "--cpu", "--fsize",
                    "--nofile", "--rss", "--rttime", "--rtprio",
                    "--sigpending", "--stack", "--core", "--data",
                    "--locks", "--memlock", "--msgqueue",
                    "--nice", "-p", "--pid"),
        "firejail": ("--profile",),
        "su": ("-s", "--shell", "-g", "--group", "-G"),
        "runuser": ("-u", "--user", "-g", "--group", "-s",
                    "--shell"),
    }
    i = 0
    n = len(parts)
    while i < n:
        _base = parts[i].rsplit("/", 1)[-1]
        if _base not in _wrappers:
            break
        i += 1
        if _base == "uv":
            while i < n and parts[i] == "run":
                i += 1
        if _base == "flock":
            # flock's lock file is a bare token after the flags.
            while i < n:
                _t = parts[i]
                if _t == "-c":
                    # -c <cmd>: the command is the -c string;
                    # re-check it as a cmdline.
                    if i + 1 >= n:
                        return False
                    return _is_codex_process(
                        "\x00".join(_shlex_tokens(parts[i + 1])))
                if _t in _value_flags.get("flock", ()) and \
                        i + 1 < n:
                    i += 2
                    continue
                if _t.startswith("-"):
                    i += 1
                    continue
                break
            if i < n:
                i += 1
            continue
        if _base in ("su", "runuser"):
            # su's first bare token is the user; runuser's user
            # comes via -u, so its first bare token is the
            # command. Both stop stripping here.
            if _base == "su":
                while i < n:
                    _t = parts[i]
                    if _t == "-c":
                        # -c <cmd>: the command is the -c string.
                        if i + 1 >= n:
                            return False
                        return _is_codex_process(
                            "\x00".join(_shlex_tokens(parts[i + 1])))
                    if _t in _value_flags.get("su", ()) and \
                            i + 1 < n:
                        i += 2
                        continue
                    if _t.startswith("-"):
                        i += 1
                        continue
                    break
                if i < n:
                    i += 1
            continue
        if _base in ("setarch", "chrt"):
            while i < n and parts[i].startswith("-"):
                i += 1
            if _base == "setarch" and i < n:
                i += 1
            elif _base == "chrt" and i < n and \
                    parts[i].isdigit():
                i += 1
            continue
        if _base == "bwrap":
            _two = ("--bind", "--ro-bind", "--dev-bind",
                    "--symlink", "--setenv")
            _one = ("--dir", "--tmpfs", "--proc", "--dev",
                    "--chdir", "--hostname", "--uid", "--gid",
                    "--unsetenv")
            while i < n:
                _t = parts[i]
                if _t in _two and i + 2 < n:
                    i += 3
                    continue
                if _t in _one and i + 1 < n:
                    i += 2
                    continue
                if _t.startswith("-"):
                    i += 1
                    continue
                break
            continue
        if _base == "env":
            while i < n:
                _t = parts[i]
                if _t in ("-S", "--split-string") and i + 1 < n:
                    # env -S <cmd>: the command is the -S string.
                    return _is_codex_process(
                        "\x00".join(_shlex_tokens(parts[i + 1])))
                if _t.startswith("--split-string="):
                    return _is_codex_process(
                        "\x00".join(_shlex_tokens(
                            _t.split("=", 1)[1])))
                if _t.startswith("-S") and len(_t) > 2:
                    return _is_codex_process(
                        "\x00".join(_shlex_tokens(_t[2:])))
                if _t.startswith("-"):
                    if _t == "-u" and i + 1 < n:
                        i += 2
                        continue
                    i += 1
                    continue
                if "=" in _t:
                    i += 1
                    continue
                break
            continue
        # Generic wrapper: skip flags/values, then the command.
        while i < n:
            _t = parts[i]
            if _t in _value_flags.get(_base, ()) and i + 1 < n:
                i += 2
                continue
            if _t.startswith("-"):
                i += 1
                continue
            break
        if _base == "taskset" and i < n:
            _t = parts[i]
            _m = _t[2:] if _t.startswith("0x") else _t
            if _m.replace(",", "").replace("-", "").isdigit():
                i += 1
        if _base == "timeout" and i < n and \
                _is_timeout_dur(parts[i]):
            i += 1
    if i >= n:
        return False
    _first = parts[i]
    return _first.rsplit("/", 1)[-1].lower() == "codex" or \
        _first.lower().endswith("/codex")


# Codex executor processes that must REFUSE, not just warn (Y13f,
# council 3 fix 2): a codex CLI whose cmdline mentions the E1
# driver, a geckodriver, a browser profile path, or Marionette is
# driving (or about to drive) a browser. A plain "codex" match with
# none of these is warning-only (a Codex CLI may be doing
# unrelated work). Keep in sync with run_codex_y5.py.
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


def _environ(pid):
    """The process environ as a dict (NUL-separated KEY=VALUE),
    or None when unreadable (another user, a zombie). F3(b):
    _is_runner_cmdline resolves os.environ[...] / os.getenv(...)
    references in -c code against this; None is fail-closed."""
    try:
        with open(f"/proc/{pid}/environ", "rb") as f:
            raw = f.read()
    except OSError:
        return None
    env = {}
    for item in raw.split(b"\x00"):
        if not item or b"=" not in item:
            continue
        _k, _v = item.split(b"=", 1)
        env[_k.decode("utf-8", "replace")] = \
            _v.decode("utf-8", "replace")
    return env


def check_go():
    if os.environ.get("Y13_GO") != "1":
        _fail("Y13_GO is not 1: no recorded go order. Set Y13_GO=1 "
              "only after the exact Y6c completion marker is "
              "confirmed on todolist-push and Muse gave a fresh go "
              "order at run time.")


def write_token():
    """Write a fresh per-run handover token (C3-10). The plan and
    the runner's comment both say the launcher writes it at run
    start; no code did (the launcher only read it, so the token
    was a hand-written file). Written AFTER check_go +
    check_marker + the ship integrity checks (check_manifest,
    _check_entry_pyc, _scan_ship) pass, so the token names a
    real go order on a verified ship, never a prep-time stale
    one or a failed ship. Shape: {"asserted_at_unix": <unix
    seconds>, "basis": "Y13 go order (Y13_GO=1) + Y6c marker
    confirmed"}. The runner fingerprints it at first sight and
    refuses if it changes mid-run."""
    tok = {"asserted_at_unix": time.time(),
           "basis": "Y13 go order (Y13_GO=1) + Y6c marker confirmed"}
    try:
        with open(TOKEN_PATH, "w", encoding="utf-8") as f:
            json.dump(tok, f)
    except OSError as exc:
        _fail(f"cannot write handover token {TOKEN_PATH}: {exc}")
    print(f"[launch_y13] handover token written "
          f"(basis: {tok['basis']})", flush=True)


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
        try:
            cwd = os.readlink(f"/proc/{pid}/cwd")
        except OSError:
            cwd = None
        if _is_runner_cmdline(cmd, cwd, _environ(pid)):
            offenders.append((pid, flat))
        elif "codex" in cmd.lower() and any(
                m in cmd.lower() for m in CODEX_REFUSE_MARKERS):
            # Y13f codex rule: a codex executor driving a browser
            # refuses (the between-arms E1 case is exactly what
            # this check exists for). The refuse branch keeps the
            # fail-closed substring rule (C2 AMEND 6).
            offenders.append((pid, flat))
        elif _is_codex_process(cmd):
            # Y13g Amend 2: the warning matches the codex
            # executable basename (a path component or argv[0]
            # basename of "codex"), not a raw substring.
            codex_hits.append((pid, flat))
    for pid, cmd in codex_hits:
        print(f"[launch_y13] WARNING: codex process running "
              f"(pid {pid}): {cmd}", flush=True)
    if offenders:
        detail = "; ".join(f"pid {p}: {c}" for p, c in offenders)
        _fail(f"live slot busy, runner process running: {detail}")


def _normalize_remote_url(url):
    """Normalize a git remote URL for the pin comparison (C2-6):
    strip ALL trailing "/" (a URL may carry more than one),
    strip an optional trailing ".git" (case-folded: ".GIT"
    counts), case-fold the scheme and host, and accept the SSH
    forms git@github.com:owner/repo(.git)? AND
    ssh://git@github.com/owner/repo(.git)? as the same repo as
    the pinned https URL. A different host, owner, or repo name
    still refuses; http (not https) still refuses."""
    u = url.strip()
    while u.endswith("/"):
        u = u[:-1]
    if u.lower().endswith(".git"):
        u = u[:-4]
    if u.startswith("ssh://"):
        # ssh://git@github.com/owner/repo -> https://github.com/owner/repo
        _rest = u[len("ssh://"):]
        if "@" in _rest:
            _rest = _rest.split("@", 1)[1]
        _host, _, _path = _rest.partition("/")
        return "https://" + _host.lower() + "/" + _path
    if u.startswith("git@"):
        try:
            _host, _path = u[4:].split(":", 1)
        except ValueError:
            return u
        return "https://" + _host.lower() + "/" + _path
    if "://" in u:
        _scheme, _rest = u.split("://", 1)
        _host, _, _path = _rest.partition("/")
        return _scheme.lower() + "://" + _host.lower() + "/" + _path
    return u


def _check_remote(repo):
    """Y13g Amend 1: pin the git remote. The marker check fetches
    from origin; a repo whose origin points at an attacker fork
    would let a forged marker pass (A5 case 6). Refuse unless
    origin is the known repo remote (equivalent spellings of the
    same repo accepted: SSH form (scp-like and ssh://), trailing
    slashes, optional .git, host case). The marker is a
    coordination signal among pushers, not authentication: it
    orders completions vs aborts, it does not prove who pushed."""
    try:
        remote = subprocess.run(
            ["git", "-C", repo, "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        _fail(f"git remote get-url origin failed to run in {repo}: "
              f"{exc}")
    if remote.returncode != 0:
        _fail(f"git remote get-url origin failed in {repo}: "
              f"{remote.stderr.strip()[:200]}")
    url = remote.stdout.strip()
    if _normalize_remote_url(url) != _normalize_remote_url(
            KNOWN_REMOTE_URL):
        _fail(f"git remote origin is {url}, not the known repo "
              f"{KNOWN_REMOTE_URL}; refusing (attacker fork?)")


def check_marker(repo):
    """Y13f H3: verify the exact Y6c completion (or abort) marker
    on todolist-push. --repo is REQUIRED (main() refuses without
    one): the old operator-assertion fallback let the documented
    launch path skip the marker check entirely.

    Matching is against SUBJECTS only: git log --format=%H%x09%s,
    regex applied in Python. The old --grep form matched body
    lines too (a body line "Y6c nested run DONE" under subject
    "Fix flake" passed). Subjects containing "harness" are prep,
    never completion. Freshness/ordering (Y13g C2 AMEND 5(a)):
    completions and aborts are ordered by BRANCH POSITION in
    `git log --first-parent origin/todolist-push` order
    (first-parent position, newest first), NOT by committer
    date: a forged old date no longer outranks a newer abort
    (A5 case 3), and a marker that arrives via a merge is
    silently ignored (side-branch markers never count), so
    markers must land as first-parent commits on todolist-push.
    The newest completion must appear BEFORE (newer than) the
    newest abort in that order; an abort newer than the newest
    completion refuses (a stale completion from an earlier
    finished Y6c run must not satisfy the gate forever)."""
    if not repo:
        _fail("--repo is required: the Y6c marker check cannot run "
              "without a repo (set --repo or Y13_REPO)")
    if not os.path.isdir(os.path.join(repo, ".git")):
        _fail(f"--repo {repo} is not a git checkout")
    _check_remote(repo)
    try:
        fetch = subprocess.run(
            ["git", "-C", repo, "fetch", "origin", "todolist-push"],
            capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        _fail(f"git fetch failed to run in {repo}: {exc}")
    if fetch.returncode != 0:
        _fail(f"git fetch failed in {repo}: "
              f"{fetch.stderr.strip()[:200]}")
    try:
        log = subprocess.run(
            ["git", "-C", repo, "log", "origin/todolist-push",
             "--first-parent", "--topo-order",
             "--format=%H%x09%s", "--",
             "improvements/worker-y6c-*.md"],
            capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as exc:
        _fail(f"git log failed to run in {repo}: {exc}")
    if log.returncode != 0:
        _fail(f"git log failed in {repo}: "
              f"{log.stderr.strip()[:200]}")
    newest_completion = None
    newest_abort = None
    for idx, line in enumerate(log.stdout.splitlines()):
        parts = line.split("\x09", 1)
        if len(parts) != 2:
            continue
        commit, subject = parts
        if ABORT_RE.search(subject):
            if newest_abort is None:
                newest_abort = (idx, commit, subject)
        elif ("harness" not in subject.lower()
                and MARKER_RE.search(subject)):
            if newest_completion is None:
                newest_completion = (idx, commit, subject)
    if newest_completion is None:
        _fail("no Y6c completion marker on todolist-push "
              "(checked subjects on the exact marker pattern)")
    if newest_abort is not None and newest_abort[0] < newest_completion[0]:
        _fail(f"Y6c abort {newest_abort[1][:7]} "
              f"({newest_abort[2]}) is newer than the newest "
              f"completion {newest_completion[1][:7]}; refusing")
    print(f"[launch_y13] Y6c completion marker found: "
          f"{newest_completion[1]} ({newest_completion[2]})",
          flush=True)


def check_manifest(repo):
    """Y13f M1 (stale-ship half): compare the ship manifest md5
    against the committed manifest from git. The in-runner pin was
    declined as self-referential, so this comparison -- outside the
    ship, against git -- is the launch-time gate that refuses a
    stale but self-consistent ship (older runner + older manifest
    + older fixtures, which --verify-manifest alone accepts).
    Runs after check_marker, so origin/todolist-push is fresh.
    Y13g B2(3): also refuses any planted file in the ship dir (a
    top-level .py not in the manifest, any non-entry .pyc, any
    symlink). Entry .pyc files are exempt here: _check_entry_pyc
    adjudicates them (R2). Y13g Amend 1: the remote is pinned
    (see _check_remote). Y13g R3 (F7): the walk flags ANY file
    or directory not in the manifest set (the same allowlist
    _scan_ship uses: manifest paths + the manifest itself +
    SHIPPED.md, and their parent dirs + the top-level
    __pycache__), so a file named __pycache__, a directory
    named like a .pyc, or a nested .py also refuses here.
    Y13g R3 (C2-4): every allowlist file must exist as a
    regular file; a missing one refuses."""
    _check_remote(repo)
    ship_manifest = os.path.join(SHIP_DIR, "codex-y5-manifest.json")
    try:
        with open(ship_manifest, "rb") as f:
            ship_bytes = f.read()
    except OSError as exc:
        _fail(f"ship manifest unreadable: {exc}")
    try:
        ship_man = json.loads(ship_bytes.decode("utf-8"))
        manifest_paths = {e["path"] for e in ship_man["files"]}
    except Exception as exc:
        _fail(f"ship manifest unparsable: {exc}")
    _allowed_files = manifest_paths | {"codex-y5-manifest.json",
                                       "codex-y5/SHIPPED.md"}
    _allowed_dirs = {os.path.dirname(p) for p in _allowed_files
                     if os.path.dirname(p)}
    # C2-4: every allowlist file must exist as a regular file. A
    # symlink is NOT failed here (the walk below fails it as a
    # symlink); only a genuinely absent path, or a non-file
    # non-symlink in its place, is "missing".
    for _rel in sorted(_allowed_files):
        _full = os.path.join(SHIP_DIR, _rel)
        if not os.path.isfile(_full) and not os.path.islink(_full):
            _fail(f"missing ship file: {_rel}. Fix: re-stage the "
                  "ship with the regen script")
    for root, dirs, files in os.walk(SHIP_DIR, followlinks=False):
        rel_root = os.path.relpath(root, SHIP_DIR)
        if rel_root == ".":
            rel_root = ""
        for name in list(dirs):
            rel = f"{rel_root}/{name}" if rel_root else name
            full = os.path.join(root, name)
            if os.path.islink(full):
                _fail(f"planted symlink dir in ship: {rel}. Fix: "
                      "delete the named file, or re-stage the ship")
            if rel not in _allowed_dirs and not _is_exempt_cache_dir(
                    rel, full):
                _fail(f"unexpected directory in ship: {rel}. Fix: "
                      "delete the named file, or re-stage the ship")
        for name in files:
            rel = f"{rel_root}/{name}" if rel_root else name
            full = os.path.join(root, name)
            if os.path.islink(full):
                _fail(f"planted symlink in ship: {rel}. Fix: "
                      "delete the named file, or re-stage the ship")
            if name.endswith(".pyc"):
                # Entry .pyc files go to _check_entry_pyc (R2);
                # any other .pyc refuses here. (F1: the exemption
                # is live: _is_entry_pyc_rel already requires the
                # __pycache__/ prefix and no subdir, so no
                # rel_root test is needed here.)
                if _is_entry_pyc_rel(rel):
                    continue
                _fail(f"planted bytecode in ship: {rel}. Fix: "
                      "delete the file, or re-stage the ship")
            if rel not in _allowed_files:
                if not rel_root and name.endswith(".py"):
                    _fail(f"planted top-level .py in ship: {rel}. "
                          "Fix: delete the named file, or re-stage "
                          "the ship")
                _fail(f"unexpected file in ship: {rel}. Fix: "
                      "delete the named file, or re-stage the ship")
    ship_md5 = hashlib.md5(ship_bytes).hexdigest()
    try:
        show = subprocess.run(
            ["git", "-C", repo, "show",
             "origin/todolist-push:tests/realistic/codex-y5-manifest.json"],
            capture_output=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as exc:
        _fail(f"git show of the committed manifest failed to run: "
              f"{exc}")
    if show.returncode != 0:
        _fail("git show of the committed manifest failed: "
              f"{show.stderr.decode('utf-8', 'replace').strip()[:200]}")
    committed_md5 = hashlib.md5(show.stdout).hexdigest()
    if ship_md5 != committed_md5:
        _fail(f"ship manifest md5 {ship_md5} != committed manifest "
              f"md5 {committed_md5} (stale ship: commit + push the "
              f"manifest first, then re-stage from the committed "
              f"bytes with the regen script --stage)")
    print(f"[launch_y13] ship manifest md5 matches committed "
          f"({ship_md5})", flush=True)


def _ship_manifest_entries():
    """{path: md5} from the ship manifest, or None if unreadable.
    Used by _scan_ship; the launcher refuses a bad manifest in
    check_manifest first, so None here means the manifest broke
    after that check (fail closed in the caller)."""
    try:
        with open(os.path.join(SHIP_DIR, "codex-y5-manifest.json"),
                  "rb") as f:
            man = json.load(f)
        return {e["path"]: e["md5"] for e in man["files"]
                if isinstance(e, dict) and e.get("path")
                and e.get("md5")}
    except Exception:
        return None


def _check_entry_pyc():
    """Y13g B1(4)/B4(2): out-of-process entry-.pyc check. For each
    entry .py (run_codex_y5.py, run_live.py, launch_y13.py), if a
    cached .pyc exists in __pycache__ (any cache tag), compile the
    .py fresh in a separate `python3 -P` subprocess and compare
    the marshalled code objects against the cached .pyc; refuse
    on mismatch (a forged entry .pyc), and delete ONLY the entry
    .pyc files that match. A legitimate self-cache from a
    -m/import probe is removed so it cannot brick the run; a
    forged one refuses before exec, so the forged bytecode never
    runs. Runs BEFORE _scan_ship, so a legitimate entry .pyc is
    already gone when the scan refuses any remaining .pyc.
    Y13g R3 (verifier defect 2): the cache dir must be a REAL
    directory inside the ship (realpath check, mirroring
    _entry_pyc_paths): a symlinked __pycache__ is treated as
    absent, so this function never deletes a file OUTSIDE the
    ship; the module-top scan refuses the symlinked dir instead.
    Y13g R3 (F5): the fresh compile uses the CACHED code
    object's co_filename (passed as a second argv), because
    co_filename is part of the marshalled code: a .pyc compiled
    with a relative path spelling mismatches a fresh compile
    that uses the absolute path. Y13g R3 (F2): the subprocess
    env scrubs PYTHONPATH/PYTHONHOME/PYTHONSTARTUP, so a
    poisoned operator env cannot reach the fresh compile."""
    import marshal
    # Defect 2: one realpath check at the top. A symlinked
    # cache dir is treated as absent (return early, delete
    # nothing); the scan refuses the symlinked dir.
    try:
        _cache = os.path.join(SHIP_DIR, "__pycache__")
        if os.path.realpath(_cache) != os.path.join(
                os.path.realpath(SHIP_DIR), "__pycache__"):
            return
    except OSError:
        return
    # F2: scrub the poisoned-env channels from the fresh-compile
    # subprocess env (PYTHONPATH/PYTHONHOME/PYTHONSTARTUP).
    _env = dict(os.environ)
    for _k in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP"):
        _env.pop(_k, None)
    for name in ("run_codex_y5.py", "run_live.py", "launch_y13.py"):
        src = os.path.join(SHIP_DIR, name)
        if not os.path.isfile(src):
            continue
        stem = name[:-3]
        cache_dir = os.path.join(SHIP_DIR, "__pycache__")
        try:
            cached_names = [n for n in os.listdir(cache_dir)
                            if n.startswith(stem + ".")
                            and n.endswith(".pyc")]
        except OSError:
            continue
        for cached_name in sorted(cached_names):
            cached_path = os.path.join(cache_dir, cached_name)
            try:
                with open(cached_path, "rb") as f:
                    cached = f.read()
            except OSError as exc:
                _fail(f"entry .pyc unreadable: {cached_path}: {exc}")
            if len(cached) <= 16:
                _fail(f"entry .pyc truncated: {cached_path}")
            try:
                cached_code = marshal.loads(cached[16:])
            except Exception as exc:
                _fail(f"entry .pyc unmarshallable: {cached_path}: {exc}")
            # F5: compile the fresh reference with the CACHED
            # co_filename (co_filename is part of the marshalled
            # code). A forged .pyc may carry a non-str or NUL
            # co_filename, or a non-code payload; that is a bad
            # .pyc, refuse cleanly instead of crashing.
            _co_filename = getattr(cached_code, "co_filename", None)
            if not isinstance(_co_filename, str) or \
                    "\x00" in _co_filename:
                _fail(f"entry .pyc has a bad co_filename: "
                      f"{cached_path}")
            # Fresh compile in a separate python3 -P subprocess:
            # -P keeps the ship dir off sys.path, and compile()
            # writes no .pyc. The code object is marshalled to
            # stdout as hex; the marshalled forms are compared (a
            # re-dump normalizes any header difference). The
            # subprocess env is scrubbed (F2).
            code = ("import marshal, sys; src = open(sys.argv[1], "
                    "'rb').read(); sys.stdout.write(marshal.dumps("
                    "compile(src, sys.argv[2], 'exec')).hex())")
            try:
                proc = subprocess.run(
                    ["python3", "-P", "-E", "-c", code, src, _co_filename],
                    capture_output=True, text=True, timeout=60,
                    env=_env)
            except (OSError, subprocess.TimeoutExpired) as exc:
                _fail(f"fresh compile of {src} failed to run: {exc}")
            if proc.returncode != 0:
                _fail(f"fresh compile of {src} failed: "
                      f"{proc.stderr.strip()[:200]}")
            try:
                fresh_code = marshal.loads(
                    bytes.fromhex(proc.stdout.strip()))
            except Exception as exc:
                _fail(f"fresh compile output unparsable for {src}: {exc}")
            if marshal.dumps(cached_code) != marshal.dumps(fresh_code):
                _fail(f"entry .pyc mismatch (forged?): {cached_path} "
                      f"does not match a fresh compile of {src}; "
                      f"re-stage the ship")
            try:
                os.unlink(cached_path)
            except OSError as exc:
                _fail(f"cannot delete verified entry .pyc "
                      f"{cached_path}: {exc}")
            print(f"[launch_y13] verified + removed entry .pyc "
                  f"{cached_name}", flush=True)


def _scan_ship():
    """Y13g C2 AMEND 1(a): full-allowlist scan of the ship dir
    before exec. Every file must be a manifest path with a
    matching md5 (plus the manifest itself and SHIPPED.md, which
    are not manifest entries); refuse any symlink (file or dir),
    any .pyc at any depth, any planted .py, and any directory
    that is not a prefix of a manifest path. An EMPTY __pycache__
    dir is allowed (leftover from a -m/import probe whose .pyc
    files _check_entry_pyc just deleted); a __pycache__ holding
    any file refuses. Runs after _check_entry_pyc, so a
    legitimate entry .pyc is already gone and any remaining .pyc
    is forged or foreign."""
    entries = _ship_manifest_entries()
    if entries is None:
        _fail("ship manifest unreadable for the allowlist scan")
    allowed = set(entries)
    allowed.add("codex-y5-manifest.json")
    allowed.add("codex-y5/SHIPPED.md")
    prefixes = {""}
    for rel in entries:
        parts = rel.split("/")
        for i in range(1, len(parts)):
            prefixes.add("/".join(parts[:i]))
    # C2-4: every allowlist file must exist as a regular file. A
    # symlink is NOT failed here (the walk below fails it as a
    # symlink); only a genuinely absent path, or a non-file
    # non-symlink in its place, is "missing".
    for _rel in sorted(allowed):
        _full = os.path.join(SHIP_DIR, _rel)
        if not os.path.isfile(_full) and not os.path.islink(_full):
            _fail(f"missing ship file: {_rel}. Fix: re-stage the "
                  "ship with the regen script")
    for root, dirs, files in os.walk(SHIP_DIR, followlinks=False):
        rel_root = os.path.relpath(root, SHIP_DIR)
        if rel_root == ".":
            rel_root = ""
        for name in list(dirs):
            rel = f"{rel_root}/{name}" if rel_root else name
            full = os.path.join(root, name)
            if os.path.islink(full):
                _fail(f"symlink dir in ship: {rel}. Fix: delete "
                      "the named file, or re-stage the ship")
            if rel == "__pycache__" and not rel_root:
                try:
                    contents = os.listdir(full)
                except OSError:
                    contents = None
                if contents == []:
                    continue
                _fail(f"__pycache__ in ship holds files: {contents}. "
                      "Fix: delete the named file, or re-stage "
                      "the ship")
            if rel not in prefixes:
                _fail(f"unexpected directory in ship: {rel}. Fix: "
                      "delete the named file, or re-stage the ship")
        for name in files:
            rel = f"{rel_root}/{name}" if rel_root else name
            full = os.path.join(root, name)
            if os.path.islink(full):
                _fail(f"symlink in ship: {rel}. Fix: delete the "
                      "named file, or re-stage the ship")
            if name.endswith(".pyc"):
                _fail(f"bytecode in ship: {rel}. Fix: delete the "
                      "named file, or re-stage the ship")
            if rel not in allowed:
                _fail(f"unexpected file in ship: {rel}. Fix: delete "
                      "the named file, or re-stage the ship")
            if rel in entries:
                try:
                    with open(full, "rb") as f:
                        digest = hashlib.md5(f.read()).hexdigest()
                except OSError as exc:
                    _fail(f"ship file unreadable: {rel}: {exc}. "
                          "Fix: delete the named file, or re-stage "
                          "the ship")
                if digest != entries[rel]:
                    _fail(f"ship file md5 mismatch: {rel} "
                          f"(stale or edited ship; if you edited a "
                          f"ship file, commit + push the manifest "
                          f"first, then re-stage)")
    print("[launch_y13] ship allowlist scan passed "
          f"({len(entries)} manifest files)", flush=True)


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
              f"launcher from the ship dir, or point --ship-dir "
              f"(or Y13_SHIP_DIR) at the ship dir")
    args = list(argv[1:])
    repo = os.environ.get("Y13_REPO")
    if "--repo" in args:
        i = args.index("--repo")
        if i + 1 >= len(args):
            _fail("--repo needs a path argument")
        repo = args[i + 1]
        del args[i:i + 2]
    if "--ship-dir" in args:
        # SHIP_DIR was already derived from this flag at module
        # top; strip it here so the runner never sees it as a
        # test selector.
        i = args.index("--ship-dir")
        if i + 1 >= len(args):
            _fail("--ship-dir needs a path argument")
        del args[i:i + 2]
    check_go()
    check_marker(repo)
    check_manifest(repo)
    _check_entry_pyc()
    _scan_ship()
    # C3-8: the handover token is written AFTER the ship passes
    # its integrity checks, immediately before check_token()
    # reads it back; a token is never written for a ship that
    # fails a check.
    write_token()
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
        # Y13g B2: PYTHONSAFEPATH=1 (-P) keeps the ship dir off
        # sys.path, but it does NOT clear PYTHONPATH, so the
        # launcher scrubs PYTHONPATH/PYTHONHOME/PYTHONSTARTUP
        # from the exec env (F2): a planted stdlib .py in a
        # PYTHONPATH dir would otherwise execute at import time
        # in the runner. (The launcher also refuses a non-empty
        # PYTHONPATH at its own module top.) The exec argv adds
        # -E, so the child ignores all PYTHON* vars even if the
        # scrub is bypassed: without -E, a PYTHONPATH plant of
        # a startup-imported name (warnings, functools,
        # collections) would execute in the child at interpreter
        # startup, before its module-top refusal runs.
        "PYTHONSAFEPATH": "1",
    })
    for _k in ("PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP"):
        env.pop(_k, None)
    args = args or ["all"]
    cmd = ["flock", "-w", "60", LOCK_PATH,
           "python3", "-P", "-E", "run_codex_y5.py"] + args
    try:
        proc = subprocess.run(cmd, cwd=SHIP_DIR, env=env)
    except (OSError, subprocess.TimeoutExpired) as exc:
        _fail(f"runner exec failed to run: {exc}")
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv))
