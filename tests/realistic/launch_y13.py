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
     and a PYTHONSAFEPATH enforcement (refuse without -P).
     Entry .pyc files are EXEMPT from this scan only (they go
     to check 4, which adjudicates them); the runner's scan has
     no such exemption (it imports run_live). Run as
     `python3 -P launch_y13.py` so the ship dir is never added
     to sys.path from the environment.
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
     ORDER (branch position, not committer date: a forged old
     date no longer outranks a newer abort). The origin remote
     must be the known repo remote (an attacker fork refuses).
     The marker is a COORDINATION SIGNAL among pushers, not
     authentication: it orders completions vs aborts, it does
     not prove who pushed. No repo path refuses: the operator's
     Y13_GO assertion alone is not a marker check.
  3. Ship-manifest check: the ship manifest md5 must equal the
     committed manifest md5 from origin/todolist-push (a stale
     but self-consistent ship refuses; the in-runner pin is
     self-referential, so this git comparison is the gate). It
     also refuses any planted file in the ship dir (a top-level
     .py not in the manifest, any non-entry .pyc, any symlink).
     Entry .pyc files are exempt here: check 4 adjudicates them.
  4. Entry-.pyc out-of-process check: for each entry .py
     (run_codex_y5.py, run_live.py, launch_y13.py), if a cached
     .pyc exists, compile the .py fresh in a separate
     `python3 -P` subprocess and compare the marshalled code
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
  6. Handover token /tmp/worker-y13-handover.json exists, is
     fresh (< 4 h) and names its basis. (The runner's preflight
     re-checks it.)
  7. Runner-quiet process check: no python process executing a
     run_*.py / run-nested* / hand_drive_e1.py script, other than
     this launcher's own ancestry. The check parses argv for
     real (wrappers, python flags and their values, -m by last
     dotted segment, -c by first-word semantics plus exec(,
     renamed/extensionless/symlinked copies by md5 against the
     manifest), so bare-relative, -m, flag-with-value,
     flock -c, and shell -c launches are caught, and a mere path
     mention (md5sum /abs/run_foo.py, echo/grep of a runner
     name, python -c 'import run_codex_y5') is not.
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
     then exec `python3 -P run_codex_y5.py <args>` with the ship env
     set (server 8771, WD 4452, JSONL /tmp/worker-y13-live.jsonl,
     LIVE_OWNER_AWAY=1, PYTHONDONTWRITEBYTECODE=1 so the ship
     never writes .pyc, PYTHONSAFEPATH=1 so the ship dir is never
     added to sys.path from the environment). The launcher exits
     with the runner's exit code.

Usage (on the laptop, from /tmp/worker-y13-server). Run with -P:
  Y13_GO=1 python3 -P launch_y13.py --repo /home/james/workspace/computer-use-wayland all
  Y13_GO=1 python3 -P launch_y13.py --repo /home/james/workspace/computer-use-wayland 01 02
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
    --ship-dir (C3-1)."""
    _args = sys.argv[1:]
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
# as a script, which execs the runner as a script.
if globals().get("__spec__") is not None:
    for _p in _entry_pyc_paths():
        try:
            os.unlink(_p)
        except OSError:
            pass
    print("run as a script (python3 launch_y13.py), not with -m "
          "and not via import", file=sys.stderr, flush=True)
    sys.exit(2)


# Y13g R1 (C2-1): enforce PYTHONSAFEPATH, same as the runner.
# -P is not optional: without it sys.path[0] is the ship dir
# and a planted stdlib .so/.py executes at import time (a
# planted hashlib.so executed at the launcher's post-scan
# `import hashlib` under the bare form). The guard above already
# ran, so a -m probe still gets its script-form message and its
# .pyc deleted; a bare DIRECT invocation refuses here.
if not sys.flags.safe_path:
    print("run with python3 -P (PYTHONSAFEPATH=1): the bare form "
          "is refused, a planted file could execute at import",
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
    # out-of-process before exec (R2). Recovery hint (C3-5):
    # the message names the fix (delete the files, or re-stage).
    found = []
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
              f"{_kind}: {_files}. Fix: delete the named files, or "
              "re-stage the ship with the regen script",
              file=sys.stderr, flush=True)
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


# Y13g B3 (C2 AMEND 3/4, redteam B3; R3 round 2): the Y13f
# tokenizer used a prev-token heuristic and missed -m forms,
# flag-with-value forms, renamed/extensionless/symlinked copies,
# and -c exec forms. This block parses the command the way a
# shell + python would: wrappers first (env/nohup/setsid/timeout/
# flock/bash -c, plus nice/stdbuf/taskset/sudo/uv run, exec -a),
# then a real python argv parse (flags and their values skipped,
# bundled short flags, -m by last dotted segment with a pdb
# special case, python3 - as stdin, first positional is the
# script candidate), then identity by name OR by md5 against the
# manifest. -c strings go through the exec-sink check (exec(,
# eval(, os.system(, subprocess.*, runpy.run_path() plus a .py
# path md5 check). A mere path mention (md5sum, cat, git) never
# matches: only a token in an execution position is examined.
# Keep in sync with run_codex_y5.py (identical block,
# AST-verified); _SHIP_DIR is the ship dir in both files.
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
    same command as a spaced one; shlex keeps it glued). A ';'
    inside a QUOTED string is split too (fail-closed: a quoted
    separator is rare, and the name leg still needs a runner
    token to match). shlex is imported at the module top (before
    the sys.path insert), never lazily here, so a planted shlex
    cannot load (C2-1)."""
    try:
        parts = shlex.split(s)
    except Exception:
        parts = s.split()
    out = []
    for p in parts:
        for _piece in re.split(r"[;&|]", p):
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


def _c_code_executes_runner(code, cwd=None):
    """True if a python -c code string executes a runner. First
    the code is parsed as a shell command (a nested 'python3
    run_codex_y5.py', e.g. via a -c inside -c, is caught by the
    same recursive parse). Then the exec-sink case: a -c string
    that hands code to exec(, eval(, os.system(, a subprocess.*
    call, or runpy.run_path( executes whatever it names, so a
    runner script basename in the code, or a quoted .py path
    that resolves to a runner copy (md5), counts. A bare
    'import run_codex_y5' is NOT an execution (an import runs
    the script-form guard and exits 2, never the suite), and
    neither is runpy.run_module (same guard) nor a mere mention
    such as print('run_codex_y5.py') (no sink). LIMIT
    (documented): a -c string that builds the runner name by
    string concatenation so NO single literal is a full runner
    path (exec(open('run_codex_'+'y5.py').read())) is not caught
    unless one literal is the full name; the ports + flock
    backstop applies."""
    inner = _shlex_tokens(code)
    if inner and _command_executes_runner(inner, cwd):
        return True
    _SINKS = ("exec(", "eval(", "os.system(",
              "subprocess.call(", "subprocess.run(",
              "subprocess.Popen(", "subprocess.check_output(",
              "subprocess.check_call(", "runpy.run_path(")
    if not any(_s in code for _s in _SINKS):
        return False
    for m in re.finditer(r"run_[A-Za-z0-9_.\-]*\.py|"
                         r"run-nested[A-Za-z0-9_.\-]*|"
                         r"hand_drive_e1\.py", code):
        if _script_basename_is_runner(m.group(0)):
            return True
    for m in re.finditer(r"['\"]([^'\"]+\.py)['\"]", code):
        if _path_is_runner_copy(m.group(1), cwd):
            return True
    return False


def _m_module_is_runner(mod, args, start, cwd=None):
    """True if a -m module argument executes a runner. A known
    runner module (by last dotted segment) counts. `pdb` counts
    when a following arg is a runner script: pdb runs its script
    with __spec__ None, so the -m guard does NOT fire (C2-3,
    proved live). runpy/cProfile are NOT counted: both set
    __spec__, so the guard kills those forms before the suite
    runs (C2-3 corrected rows). A .py -m argument is an invalid
    form and cannot execute."""
    if mod.endswith(".py"):
        return False
    last = mod.rsplit(".", 1)[-1]
    if last in _RUNNER_MODULE_NAMES:
        return True
    if last == "pdb":
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
    return False


_PY_NO_VALUE = frozenset("bBdeEhiIOqSsuv")


def _python_executes_runner(args, cwd=None):
    """Real python argv parse (C2 AMEND 3, R3). Skips interpreter
    flags and their values (-u -B -E -s -v -W <val> -X <val> -O
    -c <code> -m <mod>, -- separator, bundled short flags such as
    -uW, -Bc, -um, -Bum, and attached values such as -Wignore,
    -Xdev, -c..., -m...); the first positional is the script
    candidate. A -m module is a runner when its LAST dotted
    segment is a known runner module (pkg.run_codex_y5 counts;
    run_codex_y5.py as a -m argument is an invalid form and
    cannot execute), or when it is pdb with a runner script
    following. `python3 -` (stdin) is treated as a possible
    runner (fail-closed: piped runner bytes execute)."""
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
            return _c_code_executes_runner(args[i + 1], cwd)
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
                        return _c_code_executes_runner(rest, cwd)
                    if i + 1 >= n:
                        return False
                    return _c_code_executes_runner(args[i + 1], cwd)
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
        return _token_is_runner_script(args[i], cwd)
    return False


def _is_timeout_dur(t):
    # timeout durations accept a unit suffix and decimals: 60,
    # 60s, 1m, 1.5m, 90. (C2-3: "60s"/"1m" were misread as the
    # command.)
    if t and t[-1] in "smhd":
        t = t[:-1]
    return bool(t) and t.replace(".", "", 1).isdigit()


def _command_executes_runner(tokens, cwd=None):
    """Recursive shell-ish parse: strips wrappers (env VAR=1,
    nohup, setsid, exec [-a name] [-l] [-c], command, timeout
    <dur>, flock <flags> <lock> [-c <cmd>], bash/sh -c <cmd> or
    <script>, and the command wrappers nice, stdbuf, taskset,
    sudo, uv run, each with its flags and values skipped), then
    a python token hands off to _python_executes_runner, and any
    other token reaching this point is argv[0] of the command
    and is checked as a shebang exec (./run_codex_y5.py).
    Only a token in an execution position is ever examined, so
    'echo python3 run_codex_y5.py' and 'grep python3 ...' do
    NOT match, while 'exec python3 run_codex_y5.py' does."""
    i = 0
    n = len(tokens)
    while i < n:
        tok = tokens[i]
        base = tok.rsplit("/", 1)[-1]
        if base == "env":
            i += 1
            while i < n:
                t = tokens[i]
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
                break
            # taskset takes a bare CPU mask (hex/number) before
            # the command; it is not the command.
            if base == "taskset" and i < n:
                _t = tokens[i]
                _m = _t[2:] if _t.startswith("0x") else _t
                if _m.replace(",", "").replace("-", "").isdigit():
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
                        _shlex_tokens(tokens[i + 1]), cwd)
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
                    _shlex_tokens(tokens[i + 1]), cwd)
            return _command_executes_runner(tokens[i:], cwd)
        if base in ("bash", "sh", "zsh", "dash"):
            j = i + 1
            while j < n:
                if tokens[j] == "-c" and j + 1 < n:
                    return _command_executes_runner(
                        _shlex_tokens(tokens[j + 1]), cwd)
                if tokens[j].startswith("-"):
                    j += 1
                    continue
                return _token_is_runner_script(tokens[j], cwd)
            return False
        if _is_python_token(tok):
            return _python_executes_runner(tokens[i + 1:], cwd)
        return _token_is_runner_script(tok, cwd)
    return False


def _argv_tokens(cmdline):
    """Split a /proc cmdline (NUL-separated) into argv tokens.
    (Y13g B3: the Y13f version expanded -c arguments inline,
    which conflated 'echo python3 run_codex_y5.py' with a real
    execution; -c strings are now parsed recursively by
    _command_executes_runner instead.)"""
    return [t for t in cmdline.split("\x00") if t]


def _is_runner_cmdline(cmdline, cwd=None):
    """True if the cmdline EXECUTES a runner script (Y13g B3).

    Parses the command like a shell + python would (see
    _command_executes_runner): wrappers, real python argv parse,
    -m by last dotted segment (plus pdb), -c by first-word
    semantics plus the exec-sink check, renamed/extensionless/
    symlinked copies by md5 against the manifest. A mere path
    mention (md5sum /abs/run_foo.py, echo/grep of a runner
    name, python -c 'import run_codex_y5') never matches.
    cwd (the process's /proc/<pid>/cwd) resolves relative
    script paths for the md5 leg; without it, relative paths
    resolve against this process's cwd. Keep in sync with
    run_codex_y5.py (identical block)."""
    return _command_executes_runner(_argv_tokens(cmdline), cwd)


def _is_codex_process(cmdline):
    """True if the cmdline names a codex executable: argv[0]'s
    basename is 'codex', or some token is a path ENDING in
    '/codex' (an execution position, C2-5). A bare 'codex' token
    elsewhere (grep codex, echo codex) and a path merely
    containing a codex directory (/path/codex/run_codex_y5.py)
    do NOT count. Used by the launcher's WARNING branch only;
    the refuse branch keeps the fail-closed substring rule
    (C2 AMEND 6). Kept in both files so the shared block stays
    identical."""
    parts = _argv_tokens(cmdline)
    if not parts:
        return False
    if parts[0].rsplit("/", 1)[-1].lower() == "codex":
        return True
    for tok in parts[1:]:
        if tok.lower().endswith("/codex"):
            return True
    return False


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
        try:
            cwd = os.readlink(f"/proc/{pid}/cwd")
        except OSError:
            cwd = None
        if _is_runner_cmdline(cmd, cwd):
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


def _check_remote(repo):
    """Y13g Amend 1: pin the git remote. The marker check fetches
    from origin; a repo whose origin points at an attacker fork
    would let a forged marker pass (A5 case 6). Refuse unless
    origin is the known repo remote. The marker is a
    coordination signal among pushers, not authentication: it
    orders completions vs aborts, it does not prove who pushed."""
    remote = subprocess.run(
        ["git", "-C", repo, "remote", "get-url", "origin"],
        capture_output=True, text=True, timeout=30)
    if remote.returncode != 0:
        _fail(f"git remote get-url origin failed in {repo}: "
              f"{remote.stderr.strip()[:200]}")
    url = remote.stdout.strip()
    if url != KNOWN_REMOTE_URL:
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
    `git log origin/todolist-push` order (newest first), NOT by
    committer date: a forged old date no longer outranks a newer
    abort (A5 case 3). The newest completion must appear BEFORE
    (newer than) the newest abort in that order; an abort newer
    than the newest completion refuses (a stale completion from
    an earlier finished Y6c run must not satisfy the gate
    forever)."""
    if not repo:
        _fail("--repo is required: the Y6c marker check cannot run "
              "without a repo (set --repo or Y13_REPO)")
    if not os.path.isdir(os.path.join(repo, ".git")):
        _fail(f"--repo {repo} is not a git checkout")
    _check_remote(repo)
    fetch = subprocess.run(
        ["git", "-C", repo, "fetch", "origin", "todolist-push"],
        capture_output=True, text=True, timeout=120)
    if fetch.returncode != 0:
        _fail(f"git fetch failed in {repo}: "
              f"{fetch.stderr.strip()[:200]}")
    log = subprocess.run(
        ["git", "-C", repo, "log", "origin/todolist-push",
         "--format=%H%x09%s", "--",
         "improvements/worker-y6c-*.md"],
        capture_output=True, text=True, timeout=60)
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
    top-level .py not in the manifest, any .pyc, any symlink).
    Y13g Amend 1: the remote is pinned (see _check_remote)."""
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
    for root, dirs, files in os.walk(SHIP_DIR, followlinks=False):
        rel_root = os.path.relpath(root, SHIP_DIR)
        if rel_root == ".":
            rel_root = ""
        for name in list(dirs):
            if os.path.islink(os.path.join(root, name)):
                rel = f"{rel_root}/{name}" if rel_root else name
                _fail(f"planted symlink dir in ship: {rel}")
        for name in files:
            rel = f"{rel_root}/{name}" if rel_root else name
            full = os.path.join(root, name)
            if os.path.islink(full):
                _fail(f"planted symlink in ship: {rel}")
            if name.endswith(".pyc"):
                _fail(f"planted bytecode in ship: {rel}")
            if (not rel_root and name.endswith(".py")
                    and rel not in manifest_paths):
                _fail(f"planted top-level .py in ship: {rel}")
    ship_md5 = hashlib.md5(ship_bytes).hexdigest()
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
    already gone when the scan refuses any remaining .pyc."""
    import marshal
    for name in ("run_codex_y5.py", "run_live.py", "launch_y13.py"):
        src = os.path.join(SHIP_DIR, name)
        if not os.path.isfile(src):
            continue
        stem = name[:-3]
        cache_dir = os.path.join(SHIP_DIR, "__pycache__")
        try:
            cached_names = [n for n in os.listdir(cache_dir)
                            if n.startswith(stem + ".cpython-")
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
            # Fresh compile in a separate python3 -P subprocess:
            # -P keeps the ship dir off sys.path, and compile()
            # writes no .pyc. The code object is marshalled to
            # stdout as hex; the marshalled forms are compared (a
            # re-dump normalizes any header difference).
            code = ("import marshal, sys; src = open(sys.argv[1], "
                    "'rb').read(); sys.stdout.write(marshal.dumps("
                    "compile(src, sys.argv[1], 'exec')).hex())")
            proc = subprocess.run(
                ["python3", "-P", "-c", code, src],
                capture_output=True, text=True, timeout=60)
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
    for root, dirs, files in os.walk(SHIP_DIR, followlinks=False):
        rel_root = os.path.relpath(root, SHIP_DIR)
        if rel_root == ".":
            rel_root = ""
        for name in list(dirs):
            rel = f"{rel_root}/{name}" if rel_root else name
            full = os.path.join(root, name)
            if os.path.islink(full):
                _fail(f"symlink dir in ship: {rel}")
            if rel == "__pycache__" and not rel_root:
                try:
                    contents = os.listdir(full)
                except OSError:
                    contents = None
                if contents == []:
                    continue
                _fail(f"__pycache__ in ship holds files: {contents}")
            if rel not in prefixes:
                _fail(f"unexpected directory in ship: {rel}")
        for name in files:
            rel = f"{rel_root}/{name}" if rel_root else name
            full = os.path.join(root, name)
            if os.path.islink(full):
                _fail(f"symlink in ship: {rel}")
            if name.endswith(".pyc"):
                _fail(f"bytecode in ship: {rel}")
            if rel not in allowed:
                _fail(f"unexpected file in ship: {rel}")
            if rel in entries:
                try:
                    with open(full, "rb") as f:
                        digest = hashlib.md5(f.read()).hexdigest()
                except OSError as exc:
                    _fail(f"ship file unreadable: {rel}: {exc}")
                if digest != entries[rel]:
                    _fail(f"ship file md5 mismatch: {rel} "
                          f"(stale or edited ship; re-stage)")
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
              f"launcher from the ship dir")
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
        # sys.path, so a planted stdlib .py cannot execute at
        # import time in the runner.
        "PYTHONSAFEPATH": "1",
    })
    args = args or ["all"]
    cmd = ["flock", "-w", "60", LOCK_PATH,
           "python3", "-P", "run_codex_y5.py"] + args
    proc = subprocess.run(cmd, cwd=SHIP_DIR, env=env)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv))
