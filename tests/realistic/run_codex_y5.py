#!/usr/bin/env python3
"""Live Zen runner: codex-y5 test-01..10 (Worker Y13, 21/11/2026).

Runs tests/realistic/codex-y5/test-01..10 against the LIVE Zen on the
laptop via geckodriver --connect-existing (Marionette 2828), reusing
the proven driver from tests/realistic/run_live.py (Worker P) and the
harness from tests/realistic/run_agy_y2.py (Worker Y9).

LINEAGE AND FROZEN BASE. This file is self-contained except for the
run_live import (WD, Runner, diagnose_body, start_server). The park,
bootstrap, recheck, open_fixture, preflight, and main are COPIES of
run_agy_y2.py adapted to codex-y5 paths and Y13 ports; the diagnose
ladder and helpers are COPIES of run_agyq2.py at 1e3901c. Every
council-1/2/3 + redteam fix from the Y13 v2 plan is implemented in
the shipped bytes (see improvements/worker-y13-codex-y5-live-plan.md
v2, adjudication section). FROZEN BASE: run_live.py is shipped ONLY
from commit 1e3901c (md5 84fa106c253d5e7f16daccf2ce3f14a5), the Y4d
live-proven base. Evidence corrected (plan v2, redteam M1): the base
has ONE 10/10 live run on these bytes (Y4d run 2; run 1 was 8/10),
not "10/10 twice". It is deliberately NOT taken from HEAD: HEAD's
run_live.py changed in 91d3cd2 (Y11 live-metrics wiring, +415/-66),
unit-verified only, not live-proven. The runner refuses to launch
unless every shipped file matches codex-y5-manifest.json (launch-time
manifest check, with the Y9 diff2 B1 fix: _manifest_entries enforces
a dict manifest, exactly EXPECTED_MANIFEST_FILES entries, each a
unique path contained in the ship dir with a 32-hex md5; a duplicated
entry can no longer disguise a dropped file). The frozen ship is
recorded in codex-y5/SHIPPED.md; later VM edits do not affect the run.

RULES (from the v2 plan, all enforced in code below):
- One fresh WebDriver session per test, always deleted in finally.
  Sessions exit parked on a sacrificial about:blank tab (Y13WD park):
  DELETE /session closes the throwaway, never a keeper test tab and
  never a user tab. Park reliance is CONDITIONAL on Y9's live result:
  if Y9 still prints "shared tab gone, rebootstrap" every test, the
  park failed live and the rebootstrap fallback becomes primary.
- ONE shared test tab for the whole suite (bootstrap_tab, fresh
  tab only, up to 3 attempts). No handle scanning: only REGISTERED
  handles are ever switched to. User tabs are never navigated,
  typed into, or clicked.
- End states verified by reading the DOM directly through a 1:1
  port of check.mjs verifyTest (JS executed via Marionette eval,
  top-level return, testId via arguments[0]). The fixtures' verify
  hooks are NEVER used as oracles (none exist in this suite). The
  integrity guard runs the SAME ported verify on the untouched
  fixture before steps; a pass there is a suite defect, never a
  pass; a guard error/timeout is guard-inconclusive, never a
  proceed. None/non-dict verify results are verify FAILURES.
- Intermediate text verifies use txt() (eval textContent, trimmed),
  exact compare everywhere. norm() step list is EMPTY, frozen
  pre-run; any mid-run need for norm() is a checker finding.
- FLAGGED: a pass only after the tz-hidden removal ran AND the
  post-remove snapshot proves the class is gone, accumulated across
  attempts. Clean headline counts clean only. Exit 0 iff clean +
  flagged == total.
- ABORT: infra_blocked counts hidden-body-unrecoverable only;
  session-creation failures use the separate wd_failures counter
  (own two-consecutive abort; only a failure to CREATE the session
  counts). infra_blocked resets on any pass and on any non-INFRA
  failure, EXCEPT fixture-unavailable and guard outcomes, which
  leave the streak unchanged (fail-safe: a fixture failure between
  two INFRA tests does not hide the streak); first INFRA counts, a
  successful re-run resets it to 0, a second INFRA increments again.
  A 30 s WD HTTP timeout is INFRA (match wording "timed out" /
  TimeoutError / URLError, with the type name included); a wait_for
  timeout is a live failure.
- A re-run is allowed ONLY for a test proven infra-blocked, max ONE
  per test, immediately after the failed attempt, logged with the
  attempt field; attempt-1 summary printed before the re-run.
  Checker-bug path: the test fails, the checker is fixed, and a
  fresh FULL suite run is required; no single-test re-run after a
  checker fix.
- Mid-test hidden body: on ANY step failure, main runs diagnose_body
  once before classifying; only TZ_STUCK_V1 / OTHER_HIDDEN
  reclassifies to INFRA. FIXTURE_FAILURE splits: a positively proven
  no-body document (no eval_error, a snapshot with hasBody false and
  readyState complete, no snapshot with a body) is fixture-unavailable;
  a diagnose transport error (eval_error present, or no snapshots)
  is INFRA. UNKNOWN stays a live failure. A wall-cap trip (WallCapExceeded)
  is a live failure directly, classified before diagnose, never INFRA,
  never re-run.
- Per-test wall cap at each test's spec Maximum allowable latency
  (01: 360s, 02: 330s, 03: 360s, 04: 360s, 05: 390s, 06: 420s,
  07: 360s, 08: 360s, 09: 360s, 10: 390s). A pass over its cap is a
  failure.
- Step-count audit: the runner must emit exactly the frozen
  primitive count per test (see STEP_COUNTS); main() verifies the
  JSONL primitive count per test and FAILS a passing test if short.
- test-04 step 22 is a known weak check (passes on a fresh load);
  it is driven as written and the final report must NOT cite it as
  evidence that reverse cleared anything.
- test-10 reload steps use the navigation-tolerant reload helper:
  a click that raises after the navigation is success-then-wait,
  proven by the post-reload status text, never by message matching.

Usage (on the laptop, from /tmp/worker-y13-server). LAUNCH VIA
launch_y13.py (council A F4): it performs the launch-time checks
(go order asserted, handover token fresh, runner-quiet process
check, predecessor ports free, no live geckodriver with a live
parent) and then execs the runner under flock -w 60. Do NOT
launch the runner directly; the direct command below is the
equivalent only for reference.
  cd /tmp/worker-y13-server && Y13_GO=1 python3 launch_y13.py all \\
  > /tmp/worker-y13-stdout.log 2>&1
  Y13_GO=1 python3 launch_y13.py 01 02
  python3 run_codex_y5.py --verify-manifest
Output: one JSON summary line per test on stdout, a suite JSON line,
per-step JSONL at LIVE_LOG (with attempt fields), per-test
screenshots in /tmp/worker-y13-shots/.
"""
import os
import sys

# Y13g B1/B2: script-form-only guard + pre-import scan, before ANY
# other import. Only sys and os are imported here: sys is builtin
# and os is pre-loaded at interpreter startup, so neither can be
# shadowed by a planted file in the ship dir. Everything else
# (json, re, pathlib, ...) is imported AFTER the scan passes.
_SHIP_DIR = os.path.dirname(os.path.abspath(__file__))
_ENTRY_PYC_NAMES = (
    "run_codex_y5." + sys.implementation.cache_tag + ".pyc",
    "launch_y13." + sys.implementation.cache_tag + ".pyc",
)


def _entry_pyc_paths():
    cache = os.path.join(_SHIP_DIR, "__pycache__")
    return [os.path.join(cache, n) for n in _ENTRY_PYC_NAMES]


# Script-form-only (Y13g B1 item 3): refuse at the very top when
# loaded as a module or via -m (__spec__ is not None). A -m/import
# writes the entry .pyc during get_code, before this module
# executes; the guard deletes the two entry .pyc paths (best
# effort) so a -m probe does not brick the ship, then exits 2 with
# a clear message. NOTE: this guard cannot protect a FORGED entry
# .pyc invoked via -m/import (the forged bytecode IS the running
# code); the control for that lives in the launcher, which verifies
# the entry .pyc out-of-process before exec and never invokes
# -m/import on an unverified ship. -m and bare imports are
# unsupported invocation forms; the live launch path is always the
# launcher execing this file as a script.
if globals().get("__spec__") is not None:
    for _p in _entry_pyc_paths():
        try:
            os.unlink(_p)
        except OSError:
            pass
    print("run as a script (python3 run_codex_y5.py), not with -m "
          "and not via import", file=sys.stderr, flush=True)
    sys.exit(2)


def _json_str(s):
    # Minimal JSON string escaper: the scan runs before `json` is
    # imported, so it cannot use json.dumps (B2).
    out = []
    for ch in s:
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        elif ord(ch) < 0x20:
            out.append("\\u%04x" % ord(ch))
        else:
            out.append(ch)
    return '"' + "".join(out) + '"'


_SHIP_PY = {"run_codex_y5.py", "launch_y13.py", "run_live.py"}


def _refuse_tampered_ship():
    # Y13g B2: pre-import scan using ONLY os.path (never pathlib,
    # never json). Refuses any .pyc, any symlink, and any .py file
    # that is not one of the three ship entry points: a planted
    # re.py / json.py / functools.py would otherwise execute at
    # import time, before main() can run _verify_manifest (B2,
    # 9/15 stdlib names proven). The scan runs at module top,
    # before ANY ship import. No exemptions: the blind _ENTRY_PYC
    # exemption is removed (B1 item 1); the -m guard above deletes
    # a legitimate self-cache before it can brick a later run.
    # sys.dont_write_bytecode stops this process writing .pyc
    # itself, so a clean ship stays clean through the run.
    found = []  # (relative path, kind)
    for _root, _dirs, _files in os.walk(_SHIP_DIR, followlinks=False):
        _rel_root = os.path.relpath(_root, _SHIP_DIR)
        if _rel_root == ".":
            _rel_root = ""
        for _name in _dirs:
            _rel = (_rel_root + "/" + _name) if _rel_root else _name
            if os.path.islink(os.path.join(_root, _name)):
                found.append((_rel, "symlink"))
        for _name in _files:
            _rel = (_rel_root + "/" + _name) if _rel_root else _name
            _full = os.path.join(_root, _name)
            if os.path.islink(_full):
                found.append((_rel, "symlink"))
            elif _name.endswith(".pyc"):
                found.append((_rel, "pyc"))
            elif _name.endswith(".py") and _rel not in _SHIP_PY:
                found.append((_rel, "planted-py"))
    if found:
        _kinds = sorted({k for _, k in found})
        _kind = _kinds[0] if len(_kinds) == 1 else "mixed"
        _files = ", ".join(_json_str(p) for p, _ in sorted(found))
        print('{"refused": true, "kind": ' + _json_str(_kind)
              + ', "files": [' + _files + '], "manifest_ok": false}',
              flush=True)
        sys.exit(2)


_refuse_tampered_ship()

sys.dont_write_bytecode = True

import base64
import glob
import hashlib
import json
import re
import socket
import subprocess
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, _SHIP_DIR)

from run_live import (  # noqa: E402
    EL_KEY, WD, Runner, diagnose_body,
    start_server as _rl_start_server,
)

# Env-driven ports (read by run_live at import; the launcher sets
# them): LIVE_SERVER_PORT 8771, WD_PORT 4452, MARIONETTE_PORT 2828.
SERVER_PORT = int(os.environ.get("LIVE_SERVER_PORT", "8771"))
WD_PORT = int(os.environ.get("WD_PORT", "4452"))
LOG_PATH = Path(os.environ.get("LIVE_LOG", "/tmp/worker-y13-live.jsonl"))
SHOTS_DIR = Path("/tmp/worker-y13-shots")
GECKO_LOG = Path(f"/tmp/geckodriver-{WD_PORT}.log")
SUITE_DIR = "codex-y5"
FIRST_FIXTURE = "test-01-git-workflow.html"

# Registry of known test-tab handles (C2 F6): only these handles are
# ever switched to during tab discovery. Unknown handles are user
# tabs and must not be focused to read their URL. Pre-existing
# fixture tabs from earlier probes are NOT reused; the runner creates
# a fresh tab instead. This set is also the cleanup set: every tab in
# it is returned to about:blank at suite end.
_TEST_TABS = set()

# Timestamped handover token: written by the launcher at run start,
# re-checked before every test. Requires the env var AND a fresh
# token; a bare env var is never enough.
HANDOVER_FILE = Path("/tmp/worker-y13-handover.json")
HANDOVER_MAX_AGE_S = 4 * 3600

# Tracked item pairing the tz-hidden removal step (RT H3 / Y4b
# design): the removal is legitimate only with this item open.
TRACKED_ITEM = "improvements/transparent-zen-defect-tracked-item.md"

# Current attempt number, for the attempt field on every log record
# (Redteam A11). Set by main() before each attempt.
_CURRENT_ATTEMPT = {"n": 1}

# Fingerprint of the handover token file as first seen in this run
# (Redteam re-review N5): the token file must not change mid-run.
# A rewritten token (fresh asserted_at) would otherwise extend a run
# past the handover. Cross-launch reuse is prevented procedurally:
# the launcher writes a fresh token on every launch and flock
# prevents concurrent runs.
_HANDOVER_FP = {"fp": None}

# Marionette calls across ALL Y13WD sessions in this process
# (bootstrap, test attempts, rechecks; the suite-end cleanup session
# runs after the suite JSON is printed, so it is excluded).
_TOTAL_WD_CALLS = {"n": 0}

# Park-invariant warnings, recorded structurally (Y13f L6): every
# time _park_before_exit finds a registered test tab wrongly sitting
# in opened_tabs, one dict is appended here and the suite JSON
# carries the whole list. A stdout WARNING alone leaves no trace
# a parser can find.
_PARK_WARNINGS = []

# Launch-time manifest (Redteam re-review B3 + Y9 diff2 B1 fix):
# expected md5s for every shipped file, generated mechanically from
# the committed bytes. The runner refuses to run on any mismatch.
MANIFEST_NAME = "codex-y5-manifest.json"

# Pinned manifest size: the suite ships exactly this many files; a
# manifest listing fewer would silently skip checks. 26 = runner +
# run_live + 10 specs + simulate + check + README + check-dashes +
# 10 fixtures. SHIPPED.md is not listed (it is generated at ship
# time; its own md5 is recorded in the suite JSON via _read_shipped,
# not self-checked).
EXPECTED_MANIFEST_FILES = 27


class InfraError(RuntimeError):
    """Marker for a deliberate INFRA raise (Y13f L1): Y13Runner.step
    re-raises these unwrapped (isinstance, not a substring test on
    the message), and main() classifies them before the diagnose
    block. A plain error whose message merely mentions "INFRA:"
    stays wrapped as a step failure."""


class FixtureUnavailableError(RuntimeError):
    """Marker for a deliberate FIXTURE-UNAVAILABLE raise (Y13f L1):
    same unwrapped handling as InfraError, own outcome."""


class WallCapExceeded(RuntimeError):
    """Marker for a per-test wall-cap trip (Y13f M1): main()
    classifies it as a live failure BEFORE the diagnose block, so a
    hidden tab at trip time can never reclassify it to INFRA and
    it never spends a re-run slot (attempt 2 would trip instantly
    on cumulative time)."""


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def _ppid_of(pid):
    """Parent pid from /proc/<pid>/stat, parsed after the last ")",
    because the comm field (in parentheses) may contain spaces and
    shift every index of a blind split (C3 F7). Returns None when
    unreadable."""
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
        rest = stat[stat.rfind(")") + 2:]
        return int(rest.split()[1])
    except Exception:
        return None


def _hyprland_signature():
    """Return the live Hyprland instance signature, or None.

    Two sources, in order (Y4d, proven live 18:40 21/11; the
    environ-only version this replaces FAILED on this laptop):
    1. The environ of the live Hyprland process (pgrep -x Hyprland).
    2. The socket directory under $XDG_RUNTIME_DIR/hypr/ (Hyprland
       0.57 puts its instance dir there, named <signature>).
    UWSM-launched sessions do NOT carry HYPRLAND_INSTANCE_SIGNATURE
    in the compositor's own environ, so source 1 is often empty and
    the dir is the reliable source. Stale dirs from crashed nested
    sessions can linger, so each candidate is verified with a real
    AF_UNIX connect to its .socket.sock; only a dir whose socket
    answers is returned.
    """
    try:
        out = subprocess.run(["pgrep", "-x", "Hyprland"],
                             capture_output=True, text=True, timeout=5)
        pids = out.stdout.split()
    except Exception:
        pids = []
    for pid in pids:
        try:
            env = Path(f"/proc/{pid}/environ").read_bytes().split(b"\0")
            for kv in env:
                if kv.startswith(b"HYPRLAND_INSTANCE_SIGNATURE="):
                    return kv.split(b"=", 1)[1].decode()
        except Exception:
            continue
    runtime = os.environ.get("XDG_RUNTIME_DIR") or f"/run/user/{os.getuid()}"
    try:
        cands = [d for d in Path(runtime, "hypr").iterdir()
                 if d.is_dir() and (d / ".socket.sock").exists()]
    except Exception:
        return None
    if not cands:
        return None
    cands.sort(key=lambda d: (d / ".socket.sock").stat().st_mtime,
               reverse=True)
    for cand in cands:
        try:
            with socket.socket(socket.AF_UNIX,
                               socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect(str(cand / ".socket.sock"))
            return cand.name
        except Exception:
            continue
    return None


def _check_handover():
    """(ok, detail) for the owner-away assertion.

    Requires BOTH LIVE_OWNER_AWAY=1 AND a handover token file younger
    than HANDOVER_MAX_AGE_S, asserting the owner's handover with its
    basis and timestamp. Idle time is NOT independently verified (no
    reliable idle source on this machine); the token is an assertion
    by the launcher, recorded with basis + timestamp, and it is
    re-checked before every test, not just once in preflight.
    """
    if os.environ.get("LIVE_OWNER_AWAY") != "1":
        return False, "LIVE_OWNER_AWAY is not 1"
    try:
        raw = HANDOVER_FILE.read_bytes()
        tok = json.loads(raw)
    except Exception as exc:
        return False, f"handover file unreadable: {exc}"
    try:
        age = time.time() - float(tok["asserted_at_unix"])
    except Exception:
        return False, "handover file has no valid asserted_at_unix"
    if age < 0 or age > HANDOVER_MAX_AGE_S:
        return False, (f"handover token age {age:.0f}s outside "
                       f"0-{HANDOVER_MAX_AGE_S}s window")
    # Redteam M6: fingerprint the token CONTENT (sha256 of the file
    # bytes), not (asserted_at, mtime, size). A rewrite that
    # preserves mtime with identical asserted_at and size would pass
    # the old fingerprint; it cannot pass a content hash.
    fp = hashlib.sha256(raw).hexdigest()
    if _HANDOVER_FP["fp"] is None:
        _HANDOVER_FP["fp"] = fp
    elif fp != _HANDOVER_FP["fp"]:
        return False, "handover token changed mid-run; refusing"
    return True, (f"handover token age {age:.0f}s, "
                  f"basis: {tok.get('basis', '?')}")


def log_step(test, step, op, elapsed_ms, ok, detail=None, error=None):
    """Per-step JSONL record with the attempt field (Redteam A11).

    Same schema as run_live.log_step plus "attempt". The JSONL is
    rotated at launch (main), so one file holds exactly one run.
    """
    rec = {"ts": now_iso(), "test": test, "step": step, "op": op,
           "elapsed_ms": round(elapsed_ms, 1), "ok": ok,
           "detail": detail, "error": error,
           "attempt": _CURRENT_ATTEMPT["n"]}
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
    return rec


def _md5_of(path):
    try:
        return hashlib.md5(Path(path).read_bytes()).hexdigest()
    except Exception:
        return None


def _manifest_entries():
    """(entries, error) for the manifest, with all structural
    guards applied once and shared by both checks (Y9 diff2 B1 fix,
    commit 7e7996d, adopted verbatim).

    The manifest must be a dict, files a list of exactly
    EXPECTED_MANIFEST_FILES dict entries, each with a unique path
    contained in the ship dir and a 32-hex md5. The count pin
    alone counts entries, not files: a duplicated entry could
    disguise a dropped file (proven by the redteam: test-08
    dropped, test-07 duplicated, both checks passed), and a path
    escape could hide a file outside the ship dir. Returns
    (None, error) on any structural problem. The per-file md5
    comparison is NOT done here; callers do it against the
    returned (rel, want) pairs."""
    mpath = Path(__file__).with_name(MANIFEST_NAME)
    try:
        manifest = json.loads(mpath.read_text())
    except Exception as exc:
        return None, f"manifest unreadable: {exc}"
    if not isinstance(manifest, dict):
        return None, "manifest is not an object"
    files = manifest.get("files", [])
    if not isinstance(files, list):
        return None, "manifest files is not a list"
    if len(files) != EXPECTED_MANIFEST_FILES:
        return None, (f"manifest lists {len(files)} files, want "
                      f"{EXPECTED_MANIFEST_FILES}")
    base_dir = Path(__file__).resolve().parent
    seen = set()
    entries = []
    for entry in files:
        if not isinstance(entry, dict):
            return None, f"malformed manifest entry: {entry!r}"
        rel = entry.get("path")
        want = entry.get("md5")
        if (not isinstance(rel, str) or not isinstance(want, str)
                or len(want) != 32
                or any(c not in "0123456789abcdef" for c in want)):
            return None, f"malformed manifest entry: {entry!r}"
        full = (base_dir / rel).resolve()
        try:
            full.relative_to(base_dir)
        except ValueError:
            return None, f"manifest path escapes ship dir: {rel}"
        if full in seen:
            return None, f"duplicate manifest path: {rel}"
        seen.add(full)
        entries.append((rel, want))
    return entries, None


def _verify_manifest():
    """(ok, checked, mismatches, manifest_md5) for the launch-time
    manifest check (Redteam re-review B3 + Y9 diff2 B1).

    Every shipped file's md5 must match the manifest generated from
    the committed bytes. The manifest itself is a repo file; its own
    md5 is recorded in the suite JSON, not self-checked. Refuse the
    run on any mismatch: a stale or edited fixture must never run
    silently and pass, since the integrity guard only proves the
    verify FAILS on untouched bytes."""
    entries, err = _manifest_entries()
    if err is not None:
        return False, 0, [err], _md5_of(
            Path(__file__).with_name(MANIFEST_NAME))
    base_dir = Path(__file__).resolve().parent
    bad = []
    checked = 0
    for rel, want in entries:
        got = _md5_of(base_dir / rel)
        checked += 1
        if got != want:
            bad.append(f"{rel}: want {want}, got {got}")
    # Redteam M1: refuse unexpected files in the ship dir. The
    # entry check above only verifies listed files; a planted
    # live_metrics.py or a shadowing functools.py at top level
    # would otherwise pass (the runner inserts the ship dir at
    # sys.path[0], so a planted functools.py shadows the stdlib
    # for both this file and run_live.py). Allowlist: manifest
    # paths + the manifest itself + SHIPPED.md.
    # Y13g B1/B4: NO per-file entry-.pyc exemption anywhere. Any
    # .pyc file, at any depth, is a mismatch: a forged
    # __pycache__/run_live.cpython-312.pyc executes attacker
    # bytecode while the manifest check passes (proven by Y13r),
    # and a forged entry .pyc is no different. The pre-import scan
    # at module top refuses it even earlier, before run_live loads.
    # A legitimate entry .pyc CAN be self-created (a -m/import
    # probe writes it during get_code); the -m guard deletes it
    # before it can brick a later run, and the launcher verifies
    # it out-of-process and deletes it before exec.
    # Y13f M1: walk with os.walk (followlinks=False) and refuse any
    # symlink (file or dir) and any directory that is not a prefix
    # of a manifest path. The old rglob loop skipped every dir and
    # never descended into symlinked dirs, so a symlinked dir
    # (e.g. glob/ -> /tmp/evil) passed verify AND shadowed stdlib
    # imports. The manifest-md5 pin the redteam also asked for is
    # NOT in the runner: it is self-referential (the pin lives in
    # the runner, the runner is in the manifest, so changing the
    # pin changes the manifest md5). It is checked OUTSIDE the ship
    # instead: the launcher compares the ship manifest md5 against
    # the committed manifest from git when --repo is given.
    allowed = {rel for rel, _ in entries}
    allowed.add(MANIFEST_NAME)
    allowed.add(f"{SUITE_DIR}/SHIPPED.md")
    # Y13g B1/B4: a __pycache__ directory is exempt from the
    # "unexpected directory" refusal ONLY when it holds nothing but
    # the two entry .pyc files (0, 1, or 2). The files inside are
    # still refused as bytecode below (no per-file exemption), so
    # this exemption exists only to keep an empty __pycache__ left
    # by a probe from bricking verify.
    prefixes = {""}
    for rel, _ in entries:
        parts = rel.split("/")
        for i in range(1, len(parts)):
            prefixes.add("/".join(parts[:i]))
    for root, dirs, files in os.walk(base_dir, followlinks=False):
        rel_root = os.path.relpath(root, base_dir)
        if rel_root == ".":
            rel_root = ""
        for name in list(dirs):
            rel = f"{rel_root}/{name}" if rel_root else name
            full = os.path.join(root, name)
            if os.path.islink(full):
                bad.append(f"symlink in ship dir: {rel}")
                continue
            if rel == "__pycache__" and not rel_root:
                try:
                    _entries = os.listdir(full)
                except OSError:
                    _entries = None
                if (_entries is not None and all(
                        e in _ENTRY_PYC_NAMES
                        and os.path.isfile(os.path.join(full, e))
                        and not os.path.islink(os.path.join(full, e))
                        for e in _entries)):
                    continue
            if rel not in prefixes:
                bad.append(f"unexpected directory in ship dir: {rel}")
        for name in files:
            rel = f"{rel_root}/{name}" if rel_root else name
            full = os.path.join(root, name)
            if os.path.islink(full):
                bad.append(f"symlink in ship dir: {rel}")
                continue
            if name.endswith(".pyc") or "__pycache__" in rel.split("/"):
                bad.append(f"bytecode in ship dir: {rel}")
                continue
            if rel not in allowed:
                bad.append(f"unexpected file in ship dir: {rel}")
    return (not bad), checked, bad, _md5_of(
        Path(__file__).with_name(MANIFEST_NAME))


def _verify_served_files(base):
    """(ok, checked, mismatches) proving the HTTP server serves the
    manifest bytes (redteam diff F3). The reuse path in start_server
    probes only test-01 with a 200 check, which never proves the
    served root; a stale server on the port could serve old fixture
    bytes while the disk manifest passes. Fetch every manifest file
    over HTTP and compare md5s."""
    entries, err = _manifest_entries()
    if err is not None:
        return False, 0, [err]
    bad = []
    checked = 0
    for rel, want in entries:
        try:
            with urllib.request.urlopen(f"{base}/{rel}",
                                        timeout=5) as resp:
                data = resp.read()
            got = hashlib.md5(data).hexdigest()
        except Exception as exc:
            bad.append(f"{rel}: served fetch failed: {exc}")
            continue
        checked += 1
        if got != want:
            bad.append(f"{rel}: served {got}, want {want}")
    return (not bad), checked, bad


def select_option(d, css, value):
    """Set a <select> value and fire change."""
    return d.eval(
        "const el=document.querySelector(arguments[0]);"
        "el.value=arguments[1];"
        "el.dispatchEvent(new Event('change',{bubbles:true}));"
        "return el.value;", [css, value])


def txt(d, css):
    """Trimmed textContent of an element, or None.

    DELIBERATE difference from Y9's txt (untrimmed): check.mjs's
    text() trims, so the ported verify and the intermediate checks
    use the same semantics. Trim strips ends only; inner newlines
    survive, so exact multi-line compares (test-01 steps 4/22/26/34,
    test-02 steps 10/12/16/18/20, test-05 steps 21/23/25/26, test-06
    steps 12/15/19/21/24/26/27/28) still work. d.text (WebDriver
    rendered text) must NEVER be used for these: it collapses
    newlines and returns empty for hidden panels (council 2 F1/F2).
    """
    return d.eval(
        "const el=document.querySelector(arguments[0]);"
        "return el ? el.textContent.trim() : null;", [css])


def count(d, css):
    return d.eval(
        "return document.querySelectorAll(arguments[0]).length;", [css])


def has_class(d, css, cls):
    return d.eval(
        "const el=document.querySelector(arguments[0]);"
        "return el ? el.classList.contains(arguments[1]) : false;",
        [css, cls])


def is_checked(d, css):
    return d.eval(
        "const el=document.querySelector(arguments[0]);"
        "return el ? !!el.checked : false;", [css])


def norm(s):
    """Collapse all whitespace so multi-line renders compare sanely.

    FROZEN norm() list: EMPTY. txt() (trimmed textContent) handles
    every intermediate verify in this suite, so norm() is never
    called. Any mid-run need for norm() is a checker finding, not a
    pass-with-deviation (plan v2, C3 F6). Kept for parity with the
    Y4d/Y9 helper set only.
    """
    return " ".join((s or "").split())


class Y13WD(WD):
    """WD with a Marionette call counter, the Y9 park, and a
    screenshot helper (evidence leg)."""

    def __init__(self):
        super().__init__()
        self.wd_calls = 0

    def _wd(self, method, path, body=None):
        self.wd_calls += 1
        _TOTAL_WD_CALLS["n"] += 1
        return super()._wd(method, path, body)

    def _park_before_exit(self):
        """Park the session on a throwaway tab before DELETE /session
        (Y9WD verbatim, plus the Y13 v2 verification: the current
        handle must equal the throwaway after the switch, and no
        registered test tab may sit in opened_tabs).

        Y4d proved DELETE /session closes the session's current tab
        (the shared test tab died 20/20 at session exit). Parking on
        a keeper test tab would kill it; parking on a fresh
        sacrificial about:blank tab (kept OUT of opened_tabs so the
        base cleanup does not delete it first) makes the session
        delete close the throwaway instead. Opened test tabs are
        closed first, so the sacrificial tab is current when the
        session is deleted. If sacrificial creation fails, fall back
        to a registered test tab (council diff fix 2b): losing a
        test tab to the session delete is recoverable (rebootstrap);
        losing a user tab is not."""
        if getattr(self, "session", None) is None:
            return True
        # Y13 v2 (council A F5): a registered test tab must NEVER sit
        # in opened_tabs when the session is deleted, and the removal
        # MUST happen BEFORE the close loop below: the loop would
        # otherwise close a keeper test tab that was wrongly
        # registered as opened. A registered tab found here is a
        # bookkeeping bug; log it loudly. (Defense in depth;
        # bootstrap/open_fixture already keep them out, so this
        # normally removes nothing. Previously this loop sat AFTER
        # opened_tabs was reset to [], where it was dead code.)
        for handle in list(_TEST_TABS):
            if handle in getattr(self, "opened_tabs", []):
                print(f"[park] WARNING: registered test tab "
                      f"{handle[:8]} was in opened_tabs; removing "
                      f"(bookkeeping bug)", flush=True)
                # Y13f L6: record the invariant firing structurally,
                # not only on stdout, so the suite JSON shows it.
                _PARK_WARNINGS.append(
                    {"tab": handle[:8], "at": now_iso(),
                     "detail": "registered test tab in opened_tabs; "
                               "removed before the close loop"})
                try:
                    self.opened_tabs.remove(handle)
                except Exception:
                    pass
        for handle in list(getattr(self, "opened_tabs", [])):
            try:
                self.switch(handle)
                self._wd("DELETE", self._s("/window"), {})
            except Exception:
                pass
        try:
            self.opened_tabs = []
        except Exception:
            pass
        try:
            h = self.new_tab("about:blank", allow_hidden=True)
            try:
                self.opened_tabs.remove(h)
            except Exception:
                pass
            _TEST_TABS.add(h)
            self.switch(h)
            # Y13 v2: verify the current handle IS the throwaway
            # (GET /window). new_tab already verifies once, but the
            # switch above is a second move; never trust it blind.
            current = self._wd("GET", self._s("/window"))["value"]
            if current != h:
                print(f"[park] PARK-FAILED: current {current[:8]} != "
                      f"throwaway {h[:8]}", flush=True)
                return False
            return True
        except Exception:
            pass
        for handle in list(_TEST_TABS):
            try:
                self.switch(handle)
                return True
            except Exception:
                continue
        return False

    def __exit__(self, *exc):
        parked = False
        try:
            parked = self._park_before_exit()
        except Exception:
            parked = False
        if not parked and getattr(self, "session", None) is not None:
            # No safe current window: do NOT let DELETE /session run
            # on an uncontrolled window (redteam diff F1). Drop the
            # session reference so the base cleanup skips the DELETE
            # (it still terminates the geckodriver proc and closes
            # the log); the browser keeps its tabs, and the
            # preflight sweep can reclaim the driver slot.
            print("[park] could not park before exit; skipping "
                  "DELETE /session (session dropped, proc still "
                  "terminated by cleanup)", flush=True)
            self.session = None
        return super().__exit__(*exc)

    def screenshot(self, path):
        """End-state screenshot via the Marionette screenshot
        endpoint. Best effort: returns the path on success, None on
        any failure, never raises."""
        try:
            resp = self._wd("GET", self._s("/screenshot"))
            data = base64.b64decode(resp["value"])
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            Path(path).write_bytes(data)
            return str(path)
        except Exception as exc:
            print(f"[shot] screenshot failed: {exc}", flush=True)
            return None


class Y13Runner(Runner):
    """Runner with attempt-aware step logging and a gaps list."""

    def __init__(self, test_id, base_url):
        super().__init__(test_id, base_url)
        self.attempt = 1
        self.gaps = []
        # Ladder time in ms, accumulated by ensure_visible (C1
        # re-review F6 / C3 re-review F2): stall is time spent in
        # hidden-body recovery ladders, never whole-test elapsed.
        self.stall_ms = 0
        # Spec-primitive counter for the step-count audit (redteam
        # M4): incremented by step()/check() only while audit is
        # enabled (the driver body). open_fixture runs with audit
        # disabled, so harness steps never count as spec steps.
        self.spec_step_count = 0
        self.audit_enabled = False

    def _check_wall_cap(self, name):
        """Council A F7: enforce the per-test wall cap DURING the
        test, not only post-hoc in main(). The cap (spec Maximum
        allowable latency) counts from Runner creation, so session
        creation + open_fixture + every primitive count. A primitive
        that starts after the cap raises immediately, so the trip
        names the primitive in flight and its elapsed time. Runners
        without a cap (bootstrap, smoke) are unaffected. The raise
        is a WallCapExceeded, and main() classifies it as a live
        failure BEFORE the diagnose block (Y13f M1): a hidden tab at
        trip time can never reclassify it to INFRA, and it never
        spends a re-run slot (attempt 2 trips instantly on
        cumulative time)."""
        cap = WALL_CAPS.get(self.test)
        if cap is None:
            return
        elapsed = time.perf_counter() - self.t0
        if elapsed > cap:
            raise WallCapExceeded(
                f"wall cap exceeded: {elapsed:.0f}s > {cap}s at "
                f"primitive {name!r}")

    def check(self, name, cond, detail=""):
        """Base check plus a timed JSONL record with the attempt
        field (C1 re-review F1 / C3 re-review F5). Without this
        override the base Runner.check only prints, so every
        intermediate check (including the load-bearing pinned ones)
        left no JSONL record at all."""
        self._check_wall_cap(name)
        start = time.perf_counter()
        ok = super().check(name, cond, detail)
        ms = (time.perf_counter() - start) * 1000
        if self.audit_enabled:
            self.spec_step_count += 1
        # The JSONL write must never fail a check (redteam diff F5):
        # a logging I/O error is recorded on stdout, not raised.
        try:
            log_step(self.test, f"check: {name}", "check", ms, bool(ok),
                     detail if isinstance(detail, str) else json.dumps(
                         detail, ensure_ascii=False, default=str),
                     None if ok else f"check failed: {name}: {detail}")
        except Exception as exc:
            print(f"[{self.test}] check log failed (harmless): {exc}",
                  flush=True)
        return ok

    def step(self, name, op, fn):
        self._check_wall_cap(name)
        start = time.perf_counter()
        caught = None
        try:
            detail = fn()
            ok, error = True, None
        except Exception as exc:
            detail, ok, error = None, False, f"{type(exc).__name__}: {exc}"
            caught = exc
        ms = (time.perf_counter() - start) * 1000
        if self.audit_enabled:
            self.spec_step_count += 1
        log_step(self.test, name, op, ms, ok, detail, error)
        print(f"[{self.test}] {name} {'ok' if ok else 'FAIL'} "
              f"{ms:.0f}ms detail={detail} error={error}", flush=True)
        if not ok:
            self.failures.append(f"{name}: {error}")
            if isinstance(caught, (InfraError, FixtureUnavailableError,
                                   WallCapExceeded)):
                # Y13f L1: classify on the exception TYPE, not on a
                # substring of the wrapped message. The original
                # raise reaches main's handler directly. A plain
                # error whose message merely mentions "INFRA:" stays
                # wrapped as a step failure here (main's substring
                # matches remain only as defense in depth for
                # raises outside r.step).
                raise caught
            raise RuntimeError(f"step failed: {name}: {error}")
        return detail

    def gap(self, name, reason):
        """Record a spec step that cannot be performed (fixture gap),
        as a gap-probe log line only, never as r.step() success."""
        self.gaps.append(f"{name}: {reason}")
        log_step(self.test, f"SKIPPED (fixture gap): {name}",
                 "gap-probe", 0, True, reason)
        print(f"[{self.test}] SKIPPED {name}: {reason}", flush=True)

    def summary(self):
        s = super().summary()
        s["attempt"] = self.attempt
        s["gaps"] = self.gaps
        s["spec_step_count"] = self.spec_step_count
        return s


def _log_diag(r, diag, label, stage):
    """Record one hidden-body encounter: classification, htmlClass
    (tz-hidden present or not), rAF tick count, on the same tab at
    the same minute (wall-clock ts is in the JSONL record)."""
    snaps = diag.get("snapshots", [])
    last = snaps[-1] if snaps else {}
    raf_delta = None
    if (len(snaps) == 2 and isinstance(snaps[0], dict)
            and isinstance(snaps[1], dict)):
        t0, t1 = snaps[0].get("rafTicks"), snaps[1].get("rafTicks")
        if isinstance(t0, int) and isinstance(t1, int):
            raf_delta = t1 - t0
    detail = {
        "label": label, "stage": stage,
        "classification": diag["classification"],
        "htmlClass": last.get("htmlClass"),
        "tz_hidden": "tz-hidden" in (last.get("htmlClassList") or []),
        "bodyVis": last.get("bodyVis"),
        "bodyOpacity": last.get("bodyOpacity"),
        "rafTicks": last.get("rafTicks"),
        "rafDelta300ms": raf_delta,
        "url": last.get("url"),
    }
    r.details["hidden_body_encounters"] = \
        r.details.get("hidden_body_encounters", 0) + 1
    log_step(r.test, f"hidden-body: {diag['classification']} ({label})",
             "diagnose", 0, True, json.dumps(detail, ensure_ascii=False))
    print(f"[{r.test}] HIDDEN-BODY {diag['classification']} {label}: "
          f"htmlClass={detail['htmlClass']!r} "
          f"bodyVis={detail['bodyVis']} opacity={detail['bodyOpacity']} "
          f"rafTicks={detail['rafTicks']} rafDelta={raf_delta}",
          flush=True)
    return detail


def rebootstrap_tab(d, base, deadline=None):
    """Find or create a fresh visible test tab, using the live driver.

    Only REGISTERED test-tab handles are ever switched to (C2 F6):
    unknown handles are user tabs and must not be focused to read
    their URL. Each registered handle is diagnosed (guarded: a
    diagnose failure skips that tab, it never aborts the scan). Else
    create up to 3 new tabs via window/new, each verified; a new tab
    that opens hidden is closed (it is ours, we opened it) and the
    next is tried. A new tab whose diagnose raises after it left
    opened_tabs is closed explicitly and dropped from the registry
    (C2 F8). The new handle is kept out of opened_tabs so session
    cleanup never closes it. Raises RuntimeError when no visible tab
    is found, or when the deadline passes.
    """
    for h in list(_TEST_TABS):
        if deadline is not None and time.perf_counter() > deadline:
            raise RuntimeError("rebootstrap deadline exceeded")
        try:
            d.switch(h)
            diag = diagnose_body(d)
        except Exception:
            continue
        if diag["classification"] == "VISIBLE":
            print(f"rebootstrap: reusing visible test tab {h[:8]}",
                  flush=True)
            return h
    for _attempt in range(3):
        if deadline is not None and time.perf_counter() > deadline - 2.0:
            raise RuntimeError("rebootstrap deadline exceeded")
        h = d.new_tab("about:blank", allow_hidden=True)
        d.opened_tabs.remove(h)
        _TEST_TABS.add(h)
        try:
            diag = diagnose_body(d)
        except Exception as exc:
            print(f"rebootstrap: diagnose failed on new tab {h[:8]}: "
                  f"{exc}; closing it", flush=True)
            try:
                d.close_tab()
            except Exception:
                pass
            _TEST_TABS.discard(h)
            continue
        if diag["classification"] == "VISIBLE":
            print(f"rebootstrap: created visible tab {h[:8]}", flush=True)
            return h
        print(f"rebootstrap: new tab {h[:8]} hidden "
              f"({diag['classification']}), closing and retrying",
              flush=True)
        try:
            d.close_tab()
        except Exception:
            pass
        _TEST_TABS.discard(h)
    raise InfraError(
        "INFRA: rebootstrap: no visible test tab after 3 attempts")


def _proven_no_body(diag):
    """Redteam H4: split diagnose_body's FIXTURE_FAILURE into a
    genuine no-body document vs an eval transport failure (hung
    driver). Only a diagnose that POSITIVELY proves "document
    loaded, no body element" counts as a fixture failure: the
    diagnose carries NO eval_error, at least one snapshot has
    hasBody False AND readyState complete, and no snapshot has a
    body (contradictory samples mean instability, not proof).
    A transport error (eval_error present, or no snapshots at all)
    is NOT a proven no-body fixture; callers must treat it as
    INFRA. (Y13f M2: the eval_error check is load-bearing. A hung
    driver on the second sample leaves a genuine snap1 observation
    behind, but the fail-safe direction is INFRA, which earns a
    re-run, over fixture-unavailable, which loses it. The frozen
    base cannot be changed, so the split lives here in the caller,
    not in diagnose_body.)"""
    if diag.get("eval_error"):
        return False
    snaps = diag.get("snapshots") or []
    if not snaps:
        return False
    if any(isinstance(s, dict) and s.get("hasBody") for s in snaps):
        return False
    return any(isinstance(s, dict)
               and s.get("hasBody") is False
               and s.get("readyState") == "complete" for s in snaps)


def _ensure_visible_inner(d, r, label="test tab", allow_swap=True):
    """Diagnose-first recovery ladder (Y4b design). Body of
    ensure_visible; the wrapper accumulates ladder time into
    r.stall_ms on every call, including raises.

    Budget: 8.0 s wall per call, ENFORCED by deadline (C2 F5).
    Poll up to 2.0 s (about 3 samples: each hidden diagnose costs
    ~0.3 s + evals on top of the 0.25 s sleep), remove ~1.1 s,
    rebootstrap gets the remainder. Elapsed time against the budget
    is logged on every return path. The deadline is checked before
    each phase (poll diagnose, removal eval, new-tab attempt); the
    enforceable rule is INFRA when the remaining budget is below the
    next phase's known cost (new tab about 1.7-2.0 s, removal about
    1.1 s, diagnose about 0.5-0.7 s), never a new tab when the
    deadline is near. Per-test worst case is about 35-40 s
    (open_fixture calls this up to three times per test plus
    goto/refresh pairs; each call is bounded by its 8.0 s ladder).
    1. diagnose_body; VISIBLE -> (True, False).
    2. Poll 250 ms up to 2.0 s for the extension's own removal.
    3. If TZ_STUCK_V1 persists, remove tz-hidden exactly as
       Transparent Zen's removeLoadingScreen does (class + the
       --zen-logo-path inline property, single eval, test tab only,
       test origin only), logged as an intervention. The flag is set
       ONLY when the post-remove snapshot proves the class is gone
       (C2 F1). A test passing after a verified removal is a FLAGGED
       pass, counted separately, never folded silently into the
       headline number. The removal is legitimate only paired with
       the tracked item (see TRACKED_ITEM).
    4. Fall back to a fresh bootstrap tab (rebootstrap_tab), unless
       allow_swap is False.
    5. Still hidden -> (False, swapped); the caller raises
       INFRA: hidden-body, never a fixture failure. A FIXTURE_FAILURE
       diagnosis raises FIXTURE-UNAVAILABLE immediately, without
       burning tabs.
    REMOVED vs the old version: the switch-away step (it steals a user
    tab; Y4b correction 1) and the repaint step (V2 is dead). Never a
    real click as a recovery probe.
    Returns (ok, swapped).
    """
    t0 = time.perf_counter()
    deadline = t0 + 8.0

    def _elapsed():
        return time.perf_counter() - t0

    diag = diagnose_body(d)
    if diag["classification"] == "VISIBLE":
        print(f"[{r.test}] ensure_visible {label} visible in "
              f"{_elapsed():.1f}s / 8.0s", flush=True)
        return True, False
    if diag["classification"] == "FIXTURE_FAILURE":
        # Redteam H4: a transport error (hung driver) is INFRA,
        # not a fixture failure. Only a positively proven no-body
        # document raises FIXTURE-UNAVAILABLE.
        if _proven_no_body(diag):
            raise FixtureUnavailableError(
                f"FIXTURE-UNAVAILABLE: {label}: no body element")
        raise InfraError(
            f"INFRA: diagnose transport error, not a proven "
            f"no-body fixture: "
            f"{diag.get('eval_error', 'no snapshots')}")
    _log_diag(r, diag, label, "initial")
    poll_end = min(deadline - 3.0, t0 + 2.0)
    while time.perf_counter() < poll_end:
        time.sleep(0.25)
        diag = diagnose_body(d)
        if diag["classification"] == "VISIBLE":
            print(f"[{r.test}] ensure_visible {label} visible after "
                  f"poll in {_elapsed():.1f}s / 8.0s", flush=True)
            return True, False
        if diag["classification"] == "FIXTURE_FAILURE":
            if _proven_no_body(diag):
                raise FixtureUnavailableError(
                    f"FIXTURE-UNAVAILABLE: {label}: no body element")
            raise InfraError(
                f"INFRA: diagnose transport error, not a proven "
                f"no-body fixture: "
                f"{diag.get('eval_error', 'no snapshots')}")
    if diag["classification"] == "TZ_STUCK_V1":
        if time.perf_counter() > deadline - 1.1:
            print(f"[{r.test}] ensure_visible {label} deadline near "
                  f"({_elapsed():.1f}s / 8.0s), skipping removal",
                  flush=True)
            return False, False
        try:
            d.eval("document.documentElement.classList.remove('tz-hidden');"
                   "document.documentElement.style.removeProperty"
                   "('--zen-logo-path'); return 'removed';")
        except Exception as exc:
            raise InfraError(
                f"INFRA: tz-hidden removal eval failed: {exc}")
        time.sleep(0.5)
        diag = diagnose_body(d)
        if diag["classification"] == "VISIBLE":
            # Empty-snapshot guard (Redteam re-review N1): the
            # _DIAG_JS None bug taught that snapshots can be empty;
            # never index [-1] unguarded.
            snaps = diag.get("snapshots") or []
            last = snaps[-1] if snaps else {}
            removed = "tz-hidden" not in (
                last.get("htmlClassList") or [])
            if removed:
                r.details["tz_hidden_removed"] = True
            log_step(r.test, "remove tz-hidden (intervention)",
                     "intervention", 0, True,
                     json.dumps({"verified_removed": removed,
                                 "snapshot": last},
                                default=str))
            if removed:
                print(f"[{r.test}] INTERVENTION removed tz-hidden on "
                      f"{label} (verified); this test can only be a "
                      f"FLAGGED pass", flush=True)
            else:
                print(f"[{r.test}] removal eval ran on {label} but the "
                      f"class is still present; not flagged", flush=True)
            print(f"[{r.test}] ensure_visible {label} visible after "
                  f"removal in {_elapsed():.1f}s / 8.0s", flush=True)
            return True, False
        if diag["classification"] == "FIXTURE_FAILURE":
            # Post-removal fixture failure raises immediately (C1
            # re-review F3), same as the poll loop and the initial
            # diagnose do, instead of burning tabs on rebootstrap.
            # Redteam H4: same no-body vs transport split.
            if _proven_no_body(diag):
                raise FixtureUnavailableError(
                    f"FIXTURE-UNAVAILABLE: {label}: no body element")
            raise InfraError(
                f"INFRA: diagnose transport error, not a proven "
                f"no-body fixture: "
                f"{diag.get('eval_error', 'no snapshots')}")
        _log_diag(r, diag, label, "after-remove")
    if not allow_swap:
        print(f"[{r.test}] ensure_visible {label} still hidden after "
              f"{_elapsed():.1f}s / 8.0s, no swap allowed", flush=True)
        return False, False
    if time.perf_counter() > deadline - 2.0:
        print(f"[{r.test}] ensure_visible {label} deadline near "
              f"({_elapsed():.1f}s / 8.0s), skipping rebootstrap",
              flush=True)
        return False, False
    try:
        new_tab = rebootstrap_tab(d, r.base, deadline=deadline)
    except Exception as exc:
        print(f"[{r.test}] rebootstrap failed after {_elapsed():.1f}s / "
              f"8.0s: {exc}", flush=True)
        return False, False
    r.tab = new_tab
    d.switch(new_tab)
    diag = diagnose_body(d)
    if diag["classification"] == "VISIBLE":
        print(f"[{r.test}] ensure_visible {label} visible on new tab "
              f"in {_elapsed():.1f}s / 8.0s", flush=True)
        return True, True
    if diag["classification"] == "FIXTURE_FAILURE":
        # Y13f H4: the after-rebootstrap diagnose is a fourth
        # consumption point; split it exactly like the other three
        # sites instead of falling through to (False, True), which
        # misread a proven no-body fixture as INFRA after burning
        # extra tabs.
        if _proven_no_body(diag):
            raise FixtureUnavailableError(
                f"FIXTURE-UNAVAILABLE: {label}: no body element")
        raise InfraError(
            f"INFRA: diagnose transport error, not a proven "
            f"no-body fixture: "
            f"{diag.get('eval_error', 'no snapshots')}")
    _log_diag(r, diag, "rebootstrap tab", "after-rebootstrap")
    print(f"[{r.test}] ensure_visible {label} still hidden after "
          f"{_elapsed():.1f}s / 8.0s", flush=True)
    return False, True


def ensure_visible(d, r, label="test tab", allow_swap=True):
    """Public ladder entry point: runs _ensure_visible_inner and
    accumulates the ladder wall time into r.stall_ms on every call,
    including raises (C1 re-review F6 / C3 re-review F2). Stall is
    ladder time only, never whole-test elapsed."""
    t0 = time.perf_counter()
    try:
        return _ensure_visible_inner(d, r, label, allow_swap)
    finally:
        r.stall_ms = getattr(r, "stall_ms", 0) + \
            (time.perf_counter() - t0) * 1000


def _recheck_shared_tab(r, tab):
    """Re-diagnose the old shared tab after an INFRA failure: it may
    have cleared on its own, and its later state is evidence either
    way. Read-only diagnose, fresh session, never fails the run."""
    try:
        with Y13WD() as d:
            d.switch(tab)
            diag = diagnose_body(d)
            snaps = diag.get("snapshots") or []
            log_step(r.test, "recheck shared tab after INFRA", "diagnose",
                     0, True, json.dumps(
                         {"tab": tab[:8],
                          "classification": diag["classification"],
                          "snapshot": snaps[-1] if snaps else {}},
                         default=str))
            print(f"[{r.test}] RECHECK shared tab {tab[:8]}: "
                  f"{diag['classification']}", flush=True)
    except Exception as exc:
        print(f"[{r.test}] recheck shared tab failed (harmless): {exc}",
              flush=True)


# ---------------- ported verify (1:1 from check.mjs verifyTest) ----------------
# The JS below is transcribed from tests/realistic/codex-y5/check.mjs
# verifyTest, same selectors, same expected values, same messages,
# executed through Marionette eval instead of puppeteer evaluate.
# Note the \\n escapes: this is a Python string, so a JS "\n" inside
# a string literal must be written "\\n" here, or Python would turn
# it into a real newline and break the JS literal (Y9 convention).
_VERIFY_JS = '''
const testId = arguments[0];
const failures = [];
const state = {};
const text = (selector) => document.querySelector(selector)?.textContent?.trim();
const value = (selector) => document.querySelector(selector)?.value?.trim();
const check = (condition, message) => { if (!condition) failures.push(message); };
const equal = (selector, expected) => {
  const actual = text(selector);
  state[selector.slice(1)] = actual;
  check(actual === expected, `Expected ${selector} to be ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
};

if (testId === '01') {
  equal('#current-branch', 'feature/cleanup');
  equal('#worktree-status', 'Clean');
  equal('#commit-count', '4');
  equal('#conflict-count', '0');
  equal('#merge-status', 'Merge committed');
  equal('#latest-commit', 'Merge main after resolving config');
  const config = value('#file-config-editor');
  state.config = config;
  check(config === 'mode=preview\\nlog=compact', `Expected resolved config, got ${JSON.stringify(config)}`);
  const log = text('#git-log-list') || '';
  const expectedGitLog = 'Merge main after resolving config\\nUse compact logs\\nAdd preview mode\\nInitial commit';
  state.gitLog = log;
  check(log === expectedGitLog, `Expected Git history ${JSON.stringify(expectedGitLog)}, got ${JSON.stringify(log)}`);
  const terminalLog = text('#terminal-output');
  const expectedTerminalLog = '4 Merge main after resolving config\\n3 Use compact logs\\n2 Add preview mode\\n1 Initial commit';
  state.terminalLog = terminalLog;
  check(terminalLog === expectedTerminalLog, `Expected terminal log ${JSON.stringify(expectedTerminalLog)}, got ${JSON.stringify(terminalLog)}`);
} else if (testId === '02') {
  equal('#playlist-name', 'Morning Focus');
  equal('#playlist-count', '3');
  equal('#playlist-duration', '10:10');
  equal('#shuffle-status', 'Shuffle On');
  equal('#save-status', 'Playlist saved: Morning Focus (3 tracks, 10:10)');
  equal('#playlist-track-list', 'Quiet Circuit\\nPaper Planes\\nLow Tide');
} else if (testId === '03') {
  equal('#vault-status', 'Unlocked');
  equal('#vault-entry-count', '1');
  equal('#entry-title-display', 'Research Vault');
  equal('#entry-username-display', 'qa-operator');
  equal('#password-mask', '••••••••••••••');
  equal('#copy-status', 'Password copied');
  equal('#delete-status', 'Entry restored');
  const copied = value('#clipboard-buffer');
  state.copiedPassword = copied;
  check(copied === 'Cedar!9-Glass?', `Expected clipboard buffer to contain the generated password, got ${JSON.stringify(copied)}`);
} else if (testId === '04') {
  equal('#origin-selected', 'Workshop District');
  equal('#destination-selected', 'Harbor Square');
  equal('#selected-route-summary', 'North Loop | 14.2 km | 24 min | No tolls');
  equal('#saved-route-summary', 'Workshop District to Harbor Square | North Loop | 14.2 km | 24 min | No tolls');
  equal('#route-result-count', '1');
  equal('#avoid-tolls-status', 'Avoid tolls On');
} else if (testId === '05') {
  equal('#occurrence-count', '4');
  equal('#calendar-summary', '4 of 5 occurrences scheduled');
  equal('#title-1130', 'Design review prep');
  equal('#title-1123', 'Design review');
  equal('#title-1207', 'Design review');
  equal('#title-1214', 'Design review');
  equal('#series-location-summary', 'Room Cedar');
  equal('#delete-status', 'Deleted 2026-12-21');
  const occurrences = text('#occurrence-summary');
  const expectedOccurrences = '2026-11-23 | Design review | Room Cedar\\n2026-11-30 | Design review prep | Room Cedar\\n2026-12-07 | Design review | Room Cedar\\n2026-12-14 | Design review | Room Cedar';
  state.occurrences = occurrences;
  check(occurrences === expectedOccurrences, `Expected occurrence summary ${JSON.stringify(expectedOccurrences)}, got ${JSON.stringify(occurrences)}`);
} else if (testId === '06') {
  equal('#imported-clip-count', '3');
  equal('#timeline-clip-count', '3');
  equal('#timeline-duration', '19 sec');
  equal('#timeline-order', 'City B-roll (8 sec)\\nForest A-roll (5 sec)\\nForest A-roll (6 sec)');
  equal('#transition-summary', 'Cross Dissolve between City B-roll and Forest A-roll');
  equal('#export-resolution', '1920x1080');
  equal('#export-frame-rate', '30 fps');
  equal('#export-codec', 'H.264');
  equal('#export-filename', 'harbor-recap.mp4');
  equal('#export-status', 'Export complete: harbor-recap.mp4 (1920x1080, 30 fps, H.264)');
} else if (testId === '07') {
  equal('#search-result-count', '1');
  equal('#active-message-text', 'Release checklist is ready for review.');
  equal('#active-message-sender', 'Build Bot');
  equal('#active-message-date', '2026-10-12');
  equal('#star-status', 'Starred');
  equal('#forward-status', 'Forwarded to Release Room');
  equal('#forwarded-count', '1');
  equal('#active-room', 'Release Room');
} else if (testId === '08') {
  equal('#pivot-group-field', 'Category');
  equal('#pivot-value-field', 'Amount');
  equal('#pivot-aggregation', 'Sum');
  equal('#pivot-filter-region', 'South');
  equal('#pivot-row-count', '2');
  equal('#pivot-hardware-total', '900');
  equal('#pivot-software-total', '1400');
  equal('#pivot-grand-total', '2300');
  equal('#pivot-refresh-status', 'Pivot refreshed from 6 rows');
  const editedSource = value('#source-south-hardware');
  state['source-south-hardware'] = editedSource;
  check(editedSource === '900', `Expected #source-south-hardware value to be 900, got ${JSON.stringify(editedSource)}`);
} else if (testId === '09') {
  equal('#active-folder', 'Reviewed');
  equal('#active-tag-filter', 'Review');
  equal('#visible-file-count', '2');
  equal('#file-name-checklist', 'approved-release-checklist.md');
  equal('#file-name-plan', 'approved-release-plan.md');
  equal('#tag-checklist', 'Review');
  equal('#tag-plan', 'Review');
  equal('#file-location-checklist', 'Reviewed');
  equal('#file-location-plan', 'Reviewed');
  equal('#file-action-status', 'Moved 2 tagged files to Reviewed');
} else if (testId === '10') {
  equal('#extension-enabled-state', 'Enabled');
  equal('#site-calendar-permission', 'Ask');
  equal('#site-drive-permission', 'Ask');
  equal('#option-notify-state', 'On');
  equal('#option-auto-update-state', 'On');
  equal('#options-save-status', 'Defaults restored');
  equal('#extension-persistence-status', 'State restored after reload');
} else {
  failures.push(`Unknown test id: ${testId}`);
}
return {passed: failures.length === 0, failures, score: failures.length === 0 ? 1 : 0, state};
'''


def verify_test(d, test_id):
    """Run the ported check.mjs verifyTest for one test. Returns
    {"passed": bool, "failures": [...], "state": {...}, "score": 0/1}.
    A None/non-dict eval result is a verify FAILURE (fail closed,
    C3 G4): the ported verify must never silently pass on garbage.
    """
    try:
        res = d.eval(_VERIFY_JS, [test_id])
    except Exception as exc:
        return {"passed": False,
                "failures": [f"ported verify eval raised: "
                             f"{type(exc).__name__}: {exc}"],
                "state": {}, "score": 0, "eval_raised": True}
    if not isinstance(res, dict):
        return {"passed": False,
                "failures": [f"ported verify returned non-dict: {res!r}"],
                "state": {}, "score": 0, "eval_nondict": True}
    res.setdefault("failures", [])
    res.setdefault("state", {})
    res.setdefault("score", 0)
    res.setdefault("passed", False)
    return res


class IntegrityGuardError(RuntimeError):
    """The ported verify PASSED on the untouched fixture: the test
    cannot prove anything and is a suite defect, never a pass."""


class GuardInconclusiveError(RuntimeError):
    """The guard eval ERRORED or TIMED OUT on the untouched fixture:
    the test cannot be judged and must FAIL as guard-inconclusive.
    The suite continues; the test is NEVER driven (C3 G1)."""


def open_fixture(r, d, fname, test_id):
    """Load a fixture on the shared tab, then run the integrity
    guard through the SAME ported verify as the final verify.

    Shared visible test tab (r.tab), NOT window/new: new tabs
    intermittently open with body visibility:hidden. The tab is
    shared across tests; each test clears storage and reloads, so
    state stays isolated. The step-count audit is disabled for the
    whole of open_fixture (harness steps, not spec steps) and
    enabled on successful return.
    """
    r.audit_enabled = False
    url = r.base + f"/{SUITE_DIR}/fixtures/" + fname
    if r.tab not in d.handles():
        # The shared tab is gone (closed externally); get a fresh one.
        print(f"[{r.test}] shared tab gone, rebootstrap", flush=True)
        try:
            r.tab = rebootstrap_tab(d, r.base)
        except Exception as exc:
            raise InfraError(
                f"INFRA: shared tab gone, rebootstrap failed: {exc}")
    d.switch(r.tab)
    r.step("open fixture", "goto",
           lambda: d.goto(url, allow_hidden=True))
    r.step("clear storage + reload", "eval",
           lambda: (d.eval("localStorage.clear(); sessionStorage.clear();"
                           "return 'cleared';"),
                    d.refresh(allow_hidden=True)))
    ok, swapped = ensure_visible(d, r)
    if swapped:
        # The fixture is not loaded in the new tab yet; load it now.
        # A second swap is not attempted by the ladder itself.
        d.switch(r.tab)
        r.step("open fixture on rebootstrap tab", "goto",
               lambda: d.goto(url, allow_hidden=True))
        r.step("clear storage + reload on rebootstrap tab", "eval",
               lambda: (d.eval("localStorage.clear(); sessionStorage.clear();"
                               "return 'cleared';"),
                        d.refresh(allow_hidden=True)))
        ok, swapped2 = ensure_visible(d, r)
        if swapped2 or not ok:
            # One more fresh tab before finalising INFRA. A stall
            # that hides the rebootstrap fixture load is not a final
            # verdict until one more fresh tab has been tried.
            try:
                r.tab = rebootstrap_tab(
                    d, r.base, deadline=time.perf_counter() + 8.0)
            except Exception as exc:
                raise InfraError(
                    f"INFRA: hidden-body, final fresh tab failed: {exc}")
            d.switch(r.tab)
            r.step("open fixture on final tab", "goto",
                   lambda: d.goto(url, allow_hidden=True))
            r.step("clear storage + reload on final tab", "eval",
                   lambda: (d.eval("localStorage.clear(); "
                                   "sessionStorage.clear();"
                                   "return 'cleared';"),
                            d.refresh(allow_hidden=True)))
            ok, _swapped3 = ensure_visible(d, r, allow_swap=False)
            if not ok:
                raise InfraError(
                    "INFRA: hidden-body after final fresh tab; cannot "
                    "drive")
    if not ok:
        raise InfraError(
            "INFRA: hidden-body on test tab after recovery ladder; "
            "cannot drive (Marionette refuses clicks on "
            "visibility:hidden content)")
    # The check below is the real gate (Redteam re-review N14: the
    # old r.step("check body visible") logged ok True even when the
    # body was hidden, because Runner.step only fails on
    # exception and ignores a False return).
    r.check("body renders visible (no hidden-body incident)",
            d.visible("body"), "visible")
    # INTEGRITY GUARD (C2 F7, Redteam A6): the SAME ported verify
    # must FAIL on the untouched fixture. It runs after the fresh
    # load and before any action, per test, and is re-executed on
    # any re-run. The untouched failure list is recorded as
    # evidence. A pass on untouched aborts THIS test as a suite
    # defect (suite continues, no effect on infra_blocked). An
    # eval error/timeout aborts THIS test as guard-inconclusive
    # (suite continues, NEVER proceed).
    try:
        guard = verify_test(d, test_id)
    except Exception as exc:
        raise GuardInconclusiveError(
            f"GUARD-INCONCLUSIVE: verify raised on untouched fixture "
            f"for test {test_id}: {type(exc).__name__}: {exc}")
    if isinstance(guard, dict) and guard.get("eval_raised"):
        raise GuardInconclusiveError(
            f"GUARD-INCONCLUSIVE: verify eval raised on untouched "
            f"fixture for test {test_id}: {guard['failures']}")
    # Council A F6: a non-dict verify result does not prove the
    # guard either (the eval machinery returned garbage); it is
    # guard-inconclusive, never proceed.
    if isinstance(guard, dict) and guard.get("eval_nondict"):
        raise GuardInconclusiveError(
            f"GUARD-INCONCLUSIVE: verify returned non-dict on "
            f"untouched fixture for test {test_id}: "
            f"{guard['failures']}")
    r.details["integrity_guard"] = {
        "passed_on_untouched": guard["passed"],
        "untouched_failures": guard["failures"],
    }
    log_step(r.test, "integrity guard (untouched fixture)", "verify",
             0, not guard["passed"],
             json.dumps(guard["failures"], ensure_ascii=False))
    if guard["passed"]:
        raise IntegrityGuardError(
            f"INTEGRITY-GUARD: verify passed on untouched fixture "
            f"for test {test_id}; suite defect, not a pass")
    print(f"[{r.test}] integrity guard held "
          f"({len(guard['failures'])} expected failures on untouched)",
          flush=True)
    r.audit_enabled = True


def final_verify(r, d, test_id):
    """Final ported verify after driving. Failures are recorded as
    check failures (the test continues to its summary); a pass here
    plus zero step/check failures is required for PASS."""
    res = verify_test(d, test_id)
    r.details["final_verify"] = {
        "passed": res["passed"], "failures": res["failures"],
        "state": res["state"],
    }
    for f in res["failures"]:
        r.failures.append(f"final verify: {f}")
    print(f"[{r.test}] final verify "
          f"{'PASS' if res['passed'] else 'FAIL'}: {res['failures']}",
          flush=True)
    return res["passed"]


# ---------------- test drivers (spec step for step) ----------------
# Every primitive is named with its spec step number ("03 type ...").
# Step 1 of every spec is open_fixture (harness, not audited).
# Intermediate spec verifies are r.check() calls with txt() (exact,
# trimmed textContent); actions are r.step() calls. The full
# step-mapping table is in the v2 plan; the step-count audit freezes
# the primitive count per test in STEP_COUNTS below.

def run_01(r, d):
    open_fixture(r, d, "test-01-git-workflow.html", "01")
    r.check("02 branch starts main", txt(d, "#current-branch") == "main",
            txt(d, "#current-branch"))
    r.check("02 worktree starts clean",
            txt(d, "#worktree-status") == "Clean",
            txt(d, "#worktree-status"))
    r.check("02 commit count starts 1",
            txt(d, "#commit-count") == "1", txt(d, "#commit-count"))
    r.check("02 conflict count starts 0",
            txt(d, "#conflict-count") == "0", txt(d, "#conflict-count"))
    r.check("02 terminal ready",
            txt(d, "#terminal-output") == "Ready on branch main",
            txt(d, "#terminal-output"))
    r.step("03 type git command", "type",
           lambda: d.type_text("#terminal-command-input",
                               "git switch -c feature/cleanup"))
    r.step("03 run git command", "click",
           lambda: d.click("#btn-run-git-command"))
    r.check("03 branch is feature/cleanup",
            txt(d, "#current-branch") == "feature/cleanup",
            txt(d, "#current-branch"))
    r.check("04 terminal switched",
            txt(d, "#terminal-output")
            == "Switched to a new branch 'feature/cleanup'",
            txt(d, "#terminal-output"))
    r.check("04 branch list exact",
            txt(d, "#branch-list") == "main\nfeature/cleanup",
            txt(d, "#branch-list"))
    r.step("05 replace config editor", "type",
           lambda: d.type_text("#file-config-editor",
                               "mode=preview\nlog=verbose"))
    r.check("05 config value exact",
            d.value("#file-config-editor") == "mode=preview\nlog=verbose",
            d.value("#file-config-editor"))
    r.check("06 worktree modified",
            txt(d, "#worktree-status") == "Modified: config.txt",
            txt(d, "#worktree-status"))
    r.check("06 config value kept",
            d.value("#file-config-editor") == "mode=preview\nlog=verbose",
            d.value("#file-config-editor"))
    r.step("07 type git command", "type",
           lambda: d.type_text("#terminal-command-input",
                               "git add config.txt"))
    r.step("07 run git command", "click",
           lambda: d.click("#btn-run-git-command"))
    r.check("07 staged count 1",
            txt(d, "#staged-count") == "1", txt(d, "#staged-count"))
    r.check("08 terminal staged",
            txt(d, "#terminal-output") == "staged config.txt",
            txt(d, "#terminal-output"))
    r.check("08 staged count 1",
            txt(d, "#staged-count") == "1", txt(d, "#staged-count"))
    r.step("09 type git command", "type",
           lambda: d.type_text("#terminal-command-input",
                               'git commit -m "Add preview mode"'))
    r.step("09 run git command", "click",
           lambda: d.click("#btn-run-git-command"))
    r.check("09 latest commit Add preview mode",
            txt(d, "#latest-commit") == "Add preview mode",
            txt(d, "#latest-commit"))
    r.check("10 terminal committed",
            txt(d, "#terminal-output") == "committed: Add preview mode",
            txt(d, "#terminal-output"))
    r.check("10 commit count 2",
            txt(d, "#commit-count") == "2", txt(d, "#commit-count"))
    r.check("10 worktree clean",
            txt(d, "#worktree-status") == "Clean",
            txt(d, "#worktree-status"))
    r.step("11 type git command", "type",
           lambda: d.type_text("#terminal-command-input",
                               "git switch main"))
    r.step("11 run git command", "click",
           lambda: d.click("#btn-run-git-command"))
    r.check("11 branch is main",
            txt(d, "#current-branch") == "main",
            txt(d, "#current-branch"))
    r.check("12 terminal switched to main",
            txt(d, "#terminal-output") == "Switched to branch main",
            txt(d, "#terminal-output"))
    r.check("12 config is main version",
            d.value("#file-config-editor") == "mode=stable\nlog=verbose",
            d.value("#file-config-editor"))
    r.step("13 replace config editor", "type",
           lambda: d.type_text("#file-config-editor",
                               "mode=stable\nlog=compact"))
    r.check("13 config value exact",
            d.value("#file-config-editor") == "mode=stable\nlog=compact",
            d.value("#file-config-editor"))
    r.check("14 worktree modified",
            txt(d, "#worktree-status") == "Modified: config.txt",
            txt(d, "#worktree-status"))
    r.step("15 type git command", "type",
           lambda: d.type_text("#terminal-command-input",
                               "git add config.txt"))
    r.step("15 run git command", "click",
           lambda: d.click("#btn-run-git-command"))
    r.check("15 staged count 1",
            txt(d, "#staged-count") == "1", txt(d, "#staged-count"))
    r.check("16 terminal staged",
            txt(d, "#terminal-output") == "staged config.txt",
            txt(d, "#terminal-output"))
    r.check("16 staged count 1",
            txt(d, "#staged-count") == "1", txt(d, "#staged-count"))
    r.step("17 type git command", "type",
           lambda: d.type_text("#terminal-command-input",
                               'git commit -m "Use compact logs"'))
    r.step("17 run git command", "click",
           lambda: d.click("#btn-run-git-command"))
    r.check("17 latest commit Use compact logs",
            txt(d, "#latest-commit") == "Use compact logs",
            txt(d, "#latest-commit"))
    r.check("18 terminal committed",
            txt(d, "#terminal-output") == "committed: Use compact logs",
            txt(d, "#terminal-output"))
    r.check("18 commit count 3",
            txt(d, "#commit-count") == "3", txt(d, "#commit-count"))
    r.check("18 worktree clean",
            txt(d, "#worktree-status") == "Clean",
            txt(d, "#worktree-status"))
    r.step("19 type git command", "type",
           lambda: d.type_text("#terminal-command-input",
                               "git switch feature/cleanup"))
    r.step("19 run git command", "click",
           lambda: d.click("#btn-run-git-command"))
    r.check("19 branch is feature/cleanup",
            txt(d, "#current-branch") == "feature/cleanup",
            txt(d, "#current-branch"))
    r.check("20 terminal switched to feature",
            txt(d, "#terminal-output")
            == "Switched to branch feature/cleanup",
            txt(d, "#terminal-output"))
    r.check("20 config is feature version",
            d.value("#file-config-editor") == "mode=preview\nlog=verbose",
            d.value("#file-config-editor"))
    r.step("21 type git command", "type",
           lambda: d.type_text("#terminal-command-input", "git merge main"))
    r.step("21 run git command", "click",
           lambda: d.click("#btn-run-git-command"))
    r.check("21 merge status conflict",
            txt(d, "#merge-status") == "Conflict in config.txt",
            txt(d, "#merge-status"))
    r.check("22 terminal merge conflict exact",
            txt(d, "#terminal-output")
            == "Auto-merging config.txt\nCONFLICT in config.txt",
            txt(d, "#terminal-output"))
    r.check("22 conflict count 1",
            txt(d, "#conflict-count") == "1", txt(d, "#conflict-count"))
    r.check("22 merge status conflict",
            txt(d, "#merge-status") == "Conflict in config.txt",
            txt(d, "#merge-status"))
    r.step("23 mistake use incoming", "click",
           lambda: d.click("#btn-use-incoming"))
    r.check("23 config is incoming version",
            d.value("#file-config-editor") == "mode=stable\nlog=compact",
            d.value("#file-config-editor"))
    r.check("24 merge status resolved incoming",
            txt(d, "#merge-status") == "Resolved with incoming version",
            txt(d, "#merge-status"))
    r.check("24 conflict count 0",
            txt(d, "#conflict-count") == "0", txt(d, "#conflict-count"))
    r.step("25 recovery undo resolution", "click",
           lambda: d.click("#btn-undo-conflict-resolution"))
    r.check("25 merge status back to conflict",
            txt(d, "#merge-status") == "Conflict in config.txt",
            txt(d, "#merge-status"))
    r.check("26 conflict count 1",
            txt(d, "#conflict-count") == "1", txt(d, "#conflict-count"))
    r.check("26 conflict markers exact",
            txt(d, "#conflict-markers")
            == "<<<<<<< feature/cleanup\nmode=preview\n=======\nmode=stable\n>>>>>>> main",
            txt(d, "#conflict-markers"))
    r.step("27 use ours", "click", lambda: d.click("#btn-use-ours"))
    r.check("27 config resolved ours",
            d.value("#file-config-editor") == "mode=preview\nlog=compact",
            d.value("#file-config-editor"))
    r.check("28 merge status resolved",
            txt(d, "#merge-status") == "Conflict resolved",
            txt(d, "#merge-status"))
    r.check("28 conflict count 0",
            txt(d, "#conflict-count") == "0", txt(d, "#conflict-count"))
    r.check("28 staged count 1",
            txt(d, "#staged-count") == "1", txt(d, "#staged-count"))
    r.step("29 type git command", "type",
           lambda: d.type_text("#terminal-command-input",
                               'git commit -m "Merge main after resolving config"'))
    r.step("29 run git command", "click",
           lambda: d.click("#btn-run-git-command"))
    r.check("29 latest commit merge",
            txt(d, "#latest-commit")
            == "Merge main after resolving config",
            txt(d, "#latest-commit"))
    r.check("30 terminal committed merge",
            txt(d, "#terminal-output")
            == "committed: Merge main after resolving config",
            txt(d, "#terminal-output"))
    r.check("30 commit count 4",
            txt(d, "#commit-count") == "4", txt(d, "#commit-count"))
    r.check("30 worktree clean",
            txt(d, "#worktree-status") == "Clean",
            txt(d, "#worktree-status"))
    r.check("30 config resolved",
            d.value("#file-config-editor") == "mode=preview\nlog=compact",
            d.value("#file-config-editor"))
    r.step("31 type git command", "type",
           lambda: d.type_text("#terminal-command-input",
                               "git status --short"))
    r.step("31 run git command", "click",
           lambda: d.click("#btn-run-git-command"))
    r.check("31 terminal clean status",
            txt(d, "#terminal-output")
            == "working tree clean on feature/cleanup",
            txt(d, "#terminal-output"))
    r.check("32 terminal clean status exact",
            txt(d, "#terminal-output")
            == "working tree clean on feature/cleanup",
            txt(d, "#terminal-output"))
    r.step("33 type git command", "type",
           lambda: d.type_text("#terminal-command-input",
                               "git log --oneline"))
    r.step("33 run git command", "click",
           lambda: d.click("#btn-run-git-command"))
    r.check("33 terminal log exact",
            txt(d, "#terminal-output")
            == "4 Merge main after resolving config\n3 Use compact logs\n2 Add preview mode\n1 Initial commit",
            txt(d, "#terminal-output"))
    r.check("34 terminal log exact",
            txt(d, "#terminal-output")
            == "4 Merge main after resolving config\n3 Use compact logs\n2 Add preview mode\n1 Initial commit",
            txt(d, "#terminal-output"))
    r.check("34 git log list exact",
            txt(d, "#git-log-list")
            == "Merge main after resolving config\nUse compact logs\nAdd preview mode\nInitial commit",
            txt(d, "#git-log-list"))
    r.check("34 branch is feature/cleanup",
            txt(d, "#current-branch") == "feature/cleanup",
            txt(d, "#current-branch"))
    r.check("34 conflict count 0",
            txt(d, "#conflict-count") == "0", txt(d, "#conflict-count"))
    final_verify(r, d, "01")


def run_02(r, d):
    open_fixture(r, d, "test-02-music-player.html", "02")
    r.check("02 playlist name starts none",
            txt(d, "#playlist-name") == "No playlist selected",
            txt(d, "#playlist-name"))
    r.check("02 playlist count starts 0",
            txt(d, "#playlist-count") == "0", txt(d, "#playlist-count"))
    r.check("02 playlist duration starts 0:00",
            txt(d, "#playlist-duration") == "0:00",
            txt(d, "#playlist-duration"))
    r.check("02 track list starts empty",
            txt(d, "#playlist-track-list") == "No tracks",
            txt(d, "#playlist-track-list"))
    r.check("02 shuffle starts off",
            txt(d, "#shuffle-status") == "Shuffle Off",
            txt(d, "#shuffle-status"))
    r.check("02 save status starts not saved",
            txt(d, "#save-status") == "Not saved",
            txt(d, "#save-status"))
    r.step("03 type playlist name", "type",
           lambda: d.type_text("#playlist-name-input", "Morning Focus"))
    r.check("03 playlist name input value",
            d.value("#playlist-name-input") == "Morning Focus",
            d.value("#playlist-name-input"))
    r.step("04 create playlist", "click",
           lambda: d.click("#btn-create-playlist"))
    r.check("04 playlist name Morning Focus",
            txt(d, "#playlist-name") == "Morning Focus",
            txt(d, "#playlist-name"))
    r.step("05 add Low Tide", "click",
           lambda: d.click("#btn-add-track-low-tide"))
    r.check("05 playlist count 1",
            txt(d, "#playlist-count") == "1", txt(d, "#playlist-count"))
    r.check("06 playlist duration 3:20",
            txt(d, "#playlist-duration") == "3:20",
            txt(d, "#playlist-duration"))
    r.check("06 track list Low Tide",
            txt(d, "#playlist-track-list") == "Low Tide",
            txt(d, "#playlist-track-list"))
    r.step("07 add Paper Planes", "click",
           lambda: d.click("#btn-add-track-paper-planes"))
    r.check("07 playlist count 2",
            txt(d, "#playlist-count") == "2", txt(d, "#playlist-count"))
    r.step("08 add Quiet Circuit", "click",
           lambda: d.click("#btn-add-track-quiet-circuit"))
    r.check("08 playlist count 3",
            txt(d, "#playlist-count") == "3", txt(d, "#playlist-count"))
    r.step("09 add Night Shift", "click",
           lambda: d.click("#btn-add-track-night-shift"))
    r.check("09 playlist count 4",
            txt(d, "#playlist-count") == "4", txt(d, "#playlist-count"))
    r.check("10 playlist duration 14:00",
            txt(d, "#playlist-duration") == "14:00",
            txt(d, "#playlist-duration"))
    r.check("10 track list exact",
            txt(d, "#playlist-track-list")
            == "Low Tide\nPaper Planes\nQuiet Circuit\nNight Shift",
            txt(d, "#playlist-track-list"))
    r.step("11 move Paper Planes up", "click",
           lambda: d.click("#btn-move-paper-up"))
    first = r.step("11 read first playlist track", "text",
                   lambda: (txt(d, "#playlist-track-list") or "")
                   .split("\n")[0])
    r.check("11 first track is Paper Planes",
            first == "Paper Planes", first)
    r.check("12 track list exact",
            txt(d, "#playlist-track-list")
            == "Paper Planes\nLow Tide\nQuiet Circuit\nNight Shift",
            txt(d, "#playlist-track-list"))
    r.step("13 mistake remove Quiet Circuit", "click",
           lambda: d.click("#btn-remove-quiet-circuit"))
    r.check("13 playlist count 3",
            txt(d, "#playlist-count") == "3", txt(d, "#playlist-count"))
    r.check("14 action status removed",
            txt(d, "#playlist-action-status") == "Removed Quiet Circuit",
            txt(d, "#playlist-action-status"))
    r.check("14 playlist duration 11:15",
            txt(d, "#playlist-duration") == "11:15",
            txt(d, "#playlist-duration"))
    r.step("15 recovery undo removal", "click",
           lambda: d.click("#btn-undo-playlist-change"))
    r.check("15 playlist count 4",
            txt(d, "#playlist-count") == "4", txt(d, "#playlist-count"))
    r.check("16 action status undone",
            txt(d, "#playlist-action-status") == "Last removal undone",
            txt(d, "#playlist-action-status"))
    r.check("16 playlist duration 14:00",
            txt(d, "#playlist-duration") == "14:00",
            txt(d, "#playlist-duration"))
    r.check("16 track list exact",
            txt(d, "#playlist-track-list")
            == "Paper Planes\nLow Tide\nQuiet Circuit\nNight Shift",
            txt(d, "#playlist-track-list"))
    r.step("17 shuffle", "click", lambda: d.click("#btn-shuffle"))
    r.check("17 shuffle on",
            txt(d, "#shuffle-status") == "Shuffle On",
            txt(d, "#shuffle-status"))
    r.check("18 track list shuffled exact",
            txt(d, "#playlist-track-list")
            == "Night Shift\nQuiet Circuit\nPaper Planes\nLow Tide",
            txt(d, "#playlist-track-list"))
    r.step("19 remove Night Shift", "click",
           lambda: d.click("#btn-remove-night-shift"))
    r.check("19 playlist count 3",
            txt(d, "#playlist-count") == "3", txt(d, "#playlist-count"))
    r.check("19 playlist duration 10:10",
            txt(d, "#playlist-duration") == "10:10",
            txt(d, "#playlist-duration"))
    r.check("20 track list exact",
            txt(d, "#playlist-track-list")
            == "Quiet Circuit\nPaper Planes\nLow Tide",
            txt(d, "#playlist-track-list"))
    r.check("20 shuffle still on",
            txt(d, "#shuffle-status") == "Shuffle On",
            txt(d, "#shuffle-status"))
    r.step("21 save playlist", "click",
           lambda: d.click("#btn-save-playlist"))
    r.check("21 save status exact",
            txt(d, "#save-status")
            == "Playlist saved: Morning Focus (3 tracks, 10:10)",
            txt(d, "#save-status"))
    r.check("22 playlist name Morning Focus",
            txt(d, "#playlist-name") == "Morning Focus",
            txt(d, "#playlist-name"))
    r.check("22 playlist count 3",
            txt(d, "#playlist-count") == "3", txt(d, "#playlist-count"))
    r.check("22 save status exact",
            txt(d, "#save-status")
            == "Playlist saved: Morning Focus (3 tracks, 10:10)",
            txt(d, "#save-status"))
    final_verify(r, d, "02")


def run_03(r, d):
    open_fixture(r, d, "test-03-password-vault.html", "03")
    r.check("02 vault starts locked",
            txt(d, "#vault-status") == "Locked", txt(d, "#vault-status"))
    r.check("02 entry count starts 0",
            txt(d, "#vault-entry-count") == "0",
            txt(d, "#vault-entry-count"))
    r.check("02 entry title starts None",
            txt(d, "#entry-title-display") == "None",
            txt(d, "#entry-title-display"))
    r.check("02 delete status starts none",
            txt(d, "#delete-status") == "No deletion",
            txt(d, "#delete-status"))
    r.step("03 type master key", "type",
           lambda: d.type_text("#master-key-input", "vault-access-key"))
    r.check("03 master key value",
            d.value("#master-key-input") == "vault-access-key",
            d.value("#master-key-input"))
    r.step("04 unlock vault", "click",
           lambda: d.click("#btn-unlock-vault"))
    r.check("04 vault unlocked",
            txt(d, "#vault-status") == "Unlocked", txt(d, "#vault-status"))
    r.check("05 vault message unlocked",
            txt(d, "#vault-message") == "Vault unlocked",
            txt(d, "#vault-message"))
    r.check("05 entry count 0",
            txt(d, "#vault-entry-count") == "0",
            txt(d, "#vault-entry-count"))
    r.step("06 add entry", "click", lambda: d.click("#btn-add-entry"))
    r.check("06 entry editor visible", d.visible("#entry-editor"),
            "visible")
    r.step("07 type entry title", "type",
           lambda: d.type_text("#entry-title-input", "Research Portal"))
    r.check("07 entry title value",
            d.value("#entry-title-input") == "Research Portal",
            d.value("#entry-title-input"))
    r.step("08 type entry username", "type",
           lambda: d.type_text("#entry-username-input", "research-user"))
    r.check("08 entry username value",
            d.value("#entry-username-input") == "research-user",
            d.value("#entry-username-input"))
    r.step("09 generate password", "click",
           lambda: d.click("#btn-generate-password"))
    r.check("09 generated password value",
            d.value("#entry-password-input") == "Cedar!9-Glass?",
            d.value("#entry-password-input"))
    r.check("10 generated password exact",
            d.value("#entry-password-input") == "Cedar!9-Glass?",
            d.value("#entry-password-input"))
    r.step("11 save entry", "click", lambda: d.click("#btn-save-entry"))
    r.check("11 entry count 1",
            txt(d, "#vault-entry-count") == "1",
            txt(d, "#vault-entry-count"))
    r.check("12 entry title display Research Portal",
            txt(d, "#entry-title-display") == "Research Portal",
            txt(d, "#entry-title-display"))
    r.check("12 entry username display research-user",
            txt(d, "#entry-username-display") == "research-user",
            txt(d, "#entry-username-display"))
    r.check("12 password mask",
            txt(d, "#password-mask") == "••••••••••••••",
            txt(d, "#password-mask"))
    r.step("13 reveal password", "click",
           lambda: d.click("#btn-reveal-password"))
    r.check("13 password mask reveals generated",
            txt(d, "#password-mask") == "Cedar!9-Glass?",
            txt(d, "#password-mask"))
    r.check("14 password mask exact",
            txt(d, "#password-mask") == "Cedar!9-Glass?",
            txt(d, "#password-mask"))
    r.step("15 copy password", "click",
           lambda: d.click("#btn-copy-password"))
    r.check("15 copy status",
            txt(d, "#copy-status") == "Password copied",
            txt(d, "#copy-status"))
    r.check("16 clipboard buffer value",
            d.value("#clipboard-buffer") == "Cedar!9-Glass?",
            d.value("#clipboard-buffer"))
    r.check("16 copy status",
            txt(d, "#copy-status") == "Password copied",
            txt(d, "#copy-status"))
    r.step("17 edit entry", "click", lambda: d.click("#btn-edit-entry"))
    r.check("17 entry editor visible", d.visible("#entry-editor"),
            "visible")
    r.step("18 replace entry title", "type",
           lambda: d.type_text("#entry-title-input", "Research Vault"))
    r.check("18 entry title value",
            d.value("#entry-title-input") == "Research Vault",
            d.value("#entry-title-input"))
    r.step("19 replace entry username", "type",
           lambda: d.type_text("#entry-username-input", "qa-operator"))
    r.check("19 entry username value",
            d.value("#entry-username-input") == "qa-operator",
            d.value("#entry-username-input"))
    r.step("20 save entry", "click", lambda: d.click("#btn-save-entry"))
    r.check("20 entry title display Research Vault",
            txt(d, "#entry-title-display") == "Research Vault",
            txt(d, "#entry-title-display"))
    r.check("21 entry username display qa-operator",
            txt(d, "#entry-username-display") == "qa-operator",
            txt(d, "#entry-username-display"))
    r.check("21 password mask",
            txt(d, "#password-mask") == "••••••••••••••",
            txt(d, "#password-mask"))
    r.step("22 mistake delete entry", "click",
           lambda: d.click("#btn-delete-entry"))
    r.check("22 entry count 0",
            txt(d, "#vault-entry-count") == "0",
            txt(d, "#vault-entry-count"))
    r.check("23 delete status mistake",
            txt(d, "#delete-status") == "Entry deleted by mistake",
            txt(d, "#delete-status"))
    r.check("23 entry title display None",
            txt(d, "#entry-title-display") == "None",
            txt(d, "#entry-title-display"))
    r.step("24 recovery undo delete", "click",
           lambda: d.click("#btn-undo-delete"))
    r.check("24 entry count 1",
            txt(d, "#vault-entry-count") == "1",
            txt(d, "#vault-entry-count"))
    r.check("25 delete status restored",
            txt(d, "#delete-status") == "Entry restored",
            txt(d, "#delete-status"))
    r.check("25 entry title display Research Vault",
            txt(d, "#entry-title-display") == "Research Vault",
            txt(d, "#entry-title-display"))
    r.step("26 lock vault", "click", lambda: d.click("#btn-lock-vault"))
    r.check("26 vault locked",
            txt(d, "#vault-status") == "Locked", txt(d, "#vault-status"))
    r.check("26 entry title display None",
            txt(d, "#entry-title-display") == "None",
            txt(d, "#entry-title-display"))
    r.step("27 type master key", "type",
           lambda: d.type_text("#master-key-input", "vault-access-key"))
    r.check("27 master key value",
            d.value("#master-key-input") == "vault-access-key",
            d.value("#master-key-input"))
    r.step("28 unlock vault", "click",
           lambda: d.click("#btn-unlock-vault"))
    r.check("28 vault unlocked",
            txt(d, "#vault-status") == "Unlocked", txt(d, "#vault-status"))
    r.check("29 vault unlocked",
            txt(d, "#vault-status") == "Unlocked", txt(d, "#vault-status"))
    r.check("29 entry count 1",
            txt(d, "#vault-entry-count") == "1",
            txt(d, "#vault-entry-count"))
    r.check("29 entry title display Research Vault",
            txt(d, "#entry-title-display") == "Research Vault",
            txt(d, "#entry-title-display"))
    r.check("29 entry username display qa-operator",
            txt(d, "#entry-username-display") == "qa-operator",
            txt(d, "#entry-username-display"))
    r.check("29 password mask",
            txt(d, "#password-mask") == "••••••••••••••",
            txt(d, "#password-mask"))
    r.check("29 copy status",
            txt(d, "#copy-status") == "Password copied",
            txt(d, "#copy-status"))
    r.check("29 delete status restored",
            txt(d, "#delete-status") == "Entry restored",
            txt(d, "#delete-status"))
    final_verify(r, d, "03")


def run_04(r, d):
    open_fixture(r, d, "test-04-maps-directions.html", "04")
    r.check("02 origin starts None",
            txt(d, "#origin-selected") == "None",
            txt(d, "#origin-selected"))
    r.check("02 destination starts None",
            txt(d, "#destination-selected") == "None",
            txt(d, "#destination-selected"))
    r.check("02 route count starts 0",
            txt(d, "#route-result-count") == "0",
            txt(d, "#route-result-count"))
    r.check("02 selected route starts none",
            txt(d, "#selected-route-summary") == "No route selected",
            txt(d, "#selected-route-summary"))
    r.check("02 saved route starts none",
            txt(d, "#saved-route-summary") == "No saved route",
            txt(d, "#saved-route-summary"))
    r.check("02 origin suggestions start none",
            txt(d, "#origin-suggestions") == "No origin search",
            txt(d, "#origin-suggestions"))
    r.check("02 destination suggestions start none",
            txt(d, "#destination-suggestions") == "No destination search",
            txt(d, "#destination-suggestions"))
    r.step("03 type origin", "type",
           lambda: d.type_text("#origin-input", "Harbor Square"))
    r.check("03 origin input value",
            d.value("#origin-input") == "Harbor Square",
            d.value("#origin-input"))
    r.step("04 search origin", "click",
           lambda: d.click("#btn-search-origin"))
    r.check("04 origin suggestions Harbor Square",
            txt(d, "#origin-suggestions") == "Harbor Square",
            txt(d, "#origin-suggestions"))
    r.check("05 origin suggestions exact",
            txt(d, "#origin-suggestions") == "Harbor Square",
            txt(d, "#origin-suggestions"))
    r.check("05 pick origin button text",
            txt(d, "#btn-pick-origin-harbor-square") == "Harbor Square",
            txt(d, "#btn-pick-origin-harbor-square"))
    r.step("06 pick origin Harbor Square", "click",
           lambda: d.click("#btn-pick-origin-harbor-square"))
    r.check("06 origin selected Harbor Square",
            txt(d, "#origin-selected") == "Harbor Square",
            txt(d, "#origin-selected"))
    r.step("07 type destination", "type",
           lambda: d.type_text("#destination-input", "Workshop District"))
    r.check("07 destination input value",
            d.value("#destination-input") == "Workshop District",
            d.value("#destination-input"))
    r.step("08 search destination", "click",
           lambda: d.click("#btn-search-destination"))
    r.check("08 destination suggestions Workshop District",
            txt(d, "#destination-suggestions") == "Workshop District",
            txt(d, "#destination-suggestions"))
    r.check("09 destination suggestions exact",
            txt(d, "#destination-suggestions") == "Workshop District",
            txt(d, "#destination-suggestions"))
    r.check("09 pick destination button text",
            txt(d, "#btn-pick-destination-workshop-district")
            == "Workshop District",
            txt(d, "#btn-pick-destination-workshop-district"))
    r.step("10 pick destination Workshop District", "click",
           lambda: d.click("#btn-pick-destination-workshop-district"))
    r.check("10 destination selected Workshop District",
            txt(d, "#destination-selected") == "Workshop District",
            txt(d, "#destination-selected"))
    r.step("11 find routes", "click", lambda: d.click("#btn-find-routes"))
    r.check("11 route count 2",
            txt(d, "#route-result-count") == "2",
            txt(d, "#route-result-count"))
    r.check("12 north loop button Choose",
            txt(d, "#btn-select-north-loop") == "Choose",
            txt(d, "#btn-select-north-loop"))
    r.check("12 river express button Choose",
            txt(d, "#btn-select-river-express") == "Choose",
            txt(d, "#btn-select-river-express"))
    r.step("13 mistake select River Express", "click",
           lambda: d.click("#btn-select-river-express"))
    r.check("13 selected route River Express",
            txt(d, "#selected-route-summary")
            == "River Express | 12.8 km | 21 min | $2.50 toll",
            txt(d, "#selected-route-summary"))
    r.check("14 selected route exact",
            txt(d, "#selected-route-summary")
            == "River Express | 12.8 km | 21 min | $2.50 toll",
            txt(d, "#selected-route-summary"))
    r.step("15 recovery avoid tolls on", "click",
           lambda: d.click("#avoid-tolls-toggle"))
    r.check("15 avoid tolls on",
            txt(d, "#avoid-tolls-status") == "Avoid tolls On",
            txt(d, "#avoid-tolls-status"))
    r.check("16 route count 1",
            txt(d, "#route-result-count") == "1",
            txt(d, "#route-result-count"))
    r.check("16 selected route cleared",
            txt(d, "#selected-route-summary") == "No route selected",
            txt(d, "#selected-route-summary"))
    r.check("16 north loop button Choose",
            txt(d, "#btn-select-north-loop") == "Choose",
            txt(d, "#btn-select-north-loop"))
    r.step("17 select North Loop", "click",
           lambda: d.click("#btn-select-north-loop"))
    r.check("17 selected route North Loop",
            txt(d, "#selected-route-summary")
            == "North Loop | 14.2 km | 24 min | No tolls",
            txt(d, "#selected-route-summary"))
    r.check("18 selected route exact",
            txt(d, "#selected-route-summary")
            == "North Loop | 14.2 km | 24 min | No tolls",
            txt(d, "#selected-route-summary"))
    r.step("19 save route", "click", lambda: d.click("#btn-save-route"))
    r.check("19 saved route status",
            txt(d, "#saved-route-status") == "Route saved",
            txt(d, "#saved-route-status"))
    r.check("20 saved route summary",
            txt(d, "#saved-route-summary")
            == "Harbor Square to Workshop District | North Loop | "
               "14.2 km | 24 min | No tolls",
            txt(d, "#saved-route-summary"))
    r.step("21 reverse route", "click",
           lambda: d.click("#btn-reverse-route"))
    r.check("21 origin is Workshop District",
            txt(d, "#origin-selected") == "Workshop District",
            txt(d, "#origin-selected"))
    r.check("21 destination is Harbor Square",
            txt(d, "#destination-selected") == "Harbor Square",
            txt(d, "#destination-selected"))
    # Step 22 is the KNOWN WEAK CHECK: it passes on a fresh load
    # (same class as the 5 known weak checks in agy-y2). Driven as
    # written; the final report must NOT cite it as evidence that
    # reverse cleared anything.
    r.check("22 selected route cleared (weak check)",
            txt(d, "#selected-route-summary") == "No route selected",
            txt(d, "#selected-route-summary"))
    r.check("22 saved route cleared (weak check)",
            txt(d, "#saved-route-summary") == "No saved route",
            txt(d, "#saved-route-summary"))
    r.step("23 find routes", "click", lambda: d.click("#btn-find-routes"))
    r.check("23 route count 1",
            txt(d, "#route-result-count") == "1",
            txt(d, "#route-result-count"))
    r.check("24 avoid tolls still on",
            txt(d, "#avoid-tolls-status") == "Avoid tolls On",
            txt(d, "#avoid-tolls-status"))
    r.check("24 route count 1",
            txt(d, "#route-result-count") == "1",
            txt(d, "#route-result-count"))
    r.step("25 select North Loop", "click",
           lambda: d.click("#btn-select-north-loop"))
    r.check("25 selected route North Loop",
            txt(d, "#selected-route-summary")
            == "North Loop | 14.2 km | 24 min | No tolls",
            txt(d, "#selected-route-summary"))
    r.step("26 save route", "click", lambda: d.click("#btn-save-route"))
    r.check("26 saved route status",
            txt(d, "#saved-route-status") == "Route saved",
            txt(d, "#saved-route-status"))
    r.check("27 origin Workshop District",
            txt(d, "#origin-selected") == "Workshop District",
            txt(d, "#origin-selected"))
    r.check("27 destination Harbor Square",
            txt(d, "#destination-selected") == "Harbor Square",
            txt(d, "#destination-selected"))
    r.check("27 selected route North Loop",
            txt(d, "#selected-route-summary")
            == "North Loop | 14.2 km | 24 min | No tolls",
            txt(d, "#selected-route-summary"))
    r.check("27 saved route summary reversed",
            txt(d, "#saved-route-summary")
            == "Workshop District to Harbor Square | North Loop | "
               "14.2 km | 24 min | No tolls",
            txt(d, "#saved-route-summary"))
    final_verify(r, d, "04")


def run_05(r, d):
    open_fixture(r, d, "test-05-calendar-recurring.html", "05")
    r.check("02 occurrence count starts 0",
            txt(d, "#occurrence-count") == "0",
            txt(d, "#occurrence-count"))
    r.check("02 calendar summary starts none",
            txt(d, "#calendar-summary") == "No events",
            txt(d, "#calendar-summary"))
    r.check("02 delete status starts none",
            txt(d, "#delete-status") == "No occurrence deleted",
            txt(d, "#delete-status"))
    r.check("02 series location starts None",
            txt(d, "#series-location-summary") == "None",
            txt(d, "#series-location-summary"))
    r.step("03 type event title", "type",
           lambda: d.type_text("#event-title-input", "Design review"))
    r.check("03 event title value",
            d.value("#event-title-input") == "Design review",
            d.value("#event-title-input"))
    r.step("04 type start date", "type",
           lambda: d.type_text("#event-start-date", "2026-11-23"))
    r.check("04 start date value",
            d.value("#event-start-date") == "2026-11-23",
            d.value("#event-start-date"))
    r.step("05 type location", "type",
           lambda: d.type_text("#event-location-input", "Room Ash"))
    r.check("05 location value",
            d.value("#event-location-input") == "Room Ash",
            d.value("#event-location-input"))
    r.step("06 select weekly", "select",
           lambda: select_option(d, "#repeat-frequency", "weekly"))
    r.check("06 repeat frequency weekly",
            d.value("#repeat-frequency") == "weekly",
            d.value("#repeat-frequency"))
    r.step("07 replace occurrence limit", "type",
           lambda: d.type_text("#occurrence-limit", "5"))
    r.check("07 occurrence limit value",
            d.value("#occurrence-limit") == "5",
            d.value("#occurrence-limit"))
    r.step("08 create event", "click",
           lambda: d.click("#btn-create-event"))
    r.check("08 occurrence count 5",
            txt(d, "#occurrence-count") == "5",
            txt(d, "#occurrence-count"))
    r.check("09 calendar summary 5 of 5",
            txt(d, "#calendar-summary") == "5 of 5 occurrences scheduled",
            txt(d, "#calendar-summary"))
    r.check("09 create status",
            txt(d, "#create-status")
            == "Created weekly series: Design review (5 occurrences)",
            txt(d, "#create-status"))
    r.step("10 edit 1130 occurrence", "click",
           lambda: d.click("#btn-edit-1130"))
    r.check("10 edit date 2026-11-30",
            txt(d, "#edit-occurrence-date") == "2026-11-30",
            txt(d, "#edit-occurrence-date"))
    r.check("11 edit scope this",
            d.value("#edit-scope") == "this", d.value("#edit-scope"))
    r.check("11 edit title Design review",
            d.value("#edit-event-title") == "Design review",
            d.value("#edit-event-title"))
    r.step("12 replace edit title", "type",
           lambda: d.type_text("#edit-event-title", "Design review prep"))
    r.check("12 edit title value",
            d.value("#edit-event-title") == "Design review prep",
            d.value("#edit-event-title"))
    r.step("13 save event changes", "click",
           lambda: d.click("#btn-save-event-changes"))
    r.check("13 title 1130 prep",
            txt(d, "#title-1130") == "Design review prep",
            txt(d, "#title-1130"))
    r.check("14 occurrence count 5",
            txt(d, "#occurrence-count") == "5",
            txt(d, "#occurrence-count"))
    r.check("14 title 1130 prep",
            txt(d, "#title-1130") == "Design review prep",
            txt(d, "#title-1130"))
    r.check("14 title 1123 Design review",
            txt(d, "#title-1123") == "Design review",
            txt(d, "#title-1123"))
    r.step("15 edit 1123 occurrence", "click",
           lambda: d.click("#btn-edit-1123"))
    r.check("15 edit date 2026-11-23",
            txt(d, "#edit-occurrence-date") == "2026-11-23",
            txt(d, "#edit-occurrence-date"))
    r.step("16 select series scope", "select",
           lambda: select_option(d, "#edit-scope", "series"))
    r.check("16 edit scope series",
            d.value("#edit-scope") == "series", d.value("#edit-scope"))
    r.step("17 replace edit location", "type",
           lambda: d.type_text("#edit-event-location", "Room Cedar"))
    r.check("17 edit location value",
            d.value("#edit-event-location") == "Room Cedar",
            d.value("#edit-event-location"))
    r.step("18 save event changes", "click",
           lambda: d.click("#btn-save-event-changes"))
    r.check("18 series location Room Cedar",
            txt(d, "#series-location-summary") == "Room Cedar",
            txt(d, "#series-location-summary"))
    r.check("19 series location Room Cedar",
            txt(d, "#series-location-summary") == "Room Cedar",
            txt(d, "#series-location-summary"))
    r.check("19 title 1130 prep",
            txt(d, "#title-1130") == "Design review prep",
            txt(d, "#title-1130"))
    r.check("19 title 1207 Design review",
            txt(d, "#title-1207") == "Design review",
            txt(d, "#title-1207"))
    r.step("20 mistake delete 1207", "click",
           lambda: d.click("#btn-delete-1207"))
    r.check("20 occurrence count 4",
            txt(d, "#occurrence-count") == "4",
            txt(d, "#occurrence-count"))
    r.check("21 delete status 1207",
            txt(d, "#delete-status") == "Deleted 2026-12-07",
            txt(d, "#delete-status"))
    r.check("21 occurrence summary exact",
            txt(d, "#occurrence-summary")
            == "2026-11-23 | Design review | Room Cedar\n"
               "2026-11-30 | Design review prep | Room Cedar\n"
               "2026-12-14 | Design review | Room Cedar\n"
               "2026-12-21 | Design review | Room Cedar",
            txt(d, "#occurrence-summary"))
    r.step("22 recovery undo delete", "click",
           lambda: d.click("#btn-undo-calendar-delete"))
    r.check("22 occurrence count 5",
            txt(d, "#occurrence-count") == "5",
            txt(d, "#occurrence-count"))
    r.check("23 delete status restored",
            txt(d, "#delete-status") == "Last occurrence restored",
            txt(d, "#delete-status"))
    r.check("23 occurrence summary exact",
            txt(d, "#occurrence-summary")
            == "2026-11-23 | Design review | Room Cedar\n"
               "2026-11-30 | Design review prep | Room Cedar\n"
               "2026-12-07 | Design review | Room Cedar\n"
               "2026-12-14 | Design review | Room Cedar\n"
               "2026-12-21 | Design review | Room Cedar",
            txt(d, "#occurrence-summary"))
    r.step("24 delete 1221", "click", lambda: d.click("#btn-delete-1221"))
    r.check("24 occurrence count 4",
            txt(d, "#occurrence-count") == "4",
            txt(d, "#occurrence-count"))
    r.check("25 delete status 1221",
            txt(d, "#delete-status") == "Deleted 2026-12-21",
            txt(d, "#delete-status"))
    r.check("25 occurrence summary exact",
            txt(d, "#occurrence-summary")
            == "2026-11-23 | Design review | Room Cedar\n"
               "2026-11-30 | Design review prep | Room Cedar\n"
               "2026-12-07 | Design review | Room Cedar\n"
               "2026-12-14 | Design review | Room Cedar",
            txt(d, "#occurrence-summary"))
    r.check("26 calendar summary 4 of 5",
            txt(d, "#calendar-summary") == "4 of 5 occurrences scheduled",
            txt(d, "#calendar-summary"))
    r.check("26 occurrence summary exact",
            txt(d, "#occurrence-summary")
            == "2026-11-23 | Design review | Room Cedar\n"
               "2026-11-30 | Design review prep | Room Cedar\n"
               "2026-12-07 | Design review | Room Cedar\n"
               "2026-12-14 | Design review | Room Cedar",
            txt(d, "#occurrence-summary"))
    r.check("26 title 1130 prep",
            txt(d, "#title-1130") == "Design review prep",
            txt(d, "#title-1130"))
    r.check("26 title 1123 Design review",
            txt(d, "#title-1123") == "Design review",
            txt(d, "#title-1123"))
    r.check("26 title 1207 Design review",
            txt(d, "#title-1207") == "Design review",
            txt(d, "#title-1207"))
    r.check("26 title 1214 Design review",
            txt(d, "#title-1214") == "Design review",
            txt(d, "#title-1214"))
    r.check("26 series location Room Cedar",
            txt(d, "#series-location-summary") == "Room Cedar",
            txt(d, "#series-location-summary"))
    final_verify(r, d, "05")


def run_06(r, d):
    open_fixture(r, d, "test-06-video-editor.html", "06")
    r.check("02 imported count starts 0",
            txt(d, "#imported-clip-count") == "0",
            txt(d, "#imported-clip-count"))
    r.check("02 timeline count starts 0",
            txt(d, "#timeline-clip-count") == "0",
            txt(d, "#timeline-clip-count"))
    r.check("02 timeline duration starts 0 sec",
            txt(d, "#timeline-duration") == "0 sec",
            txt(d, "#timeline-duration"))
    r.check("02 timeline order starts empty",
            txt(d, "#timeline-order") == "Timeline is empty",
            txt(d, "#timeline-order"))
    r.check("02 export status starts not exported",
            txt(d, "#export-status") == "Not exported",
            txt(d, "#export-status"))
    r.step("03 open import modal", "click",
           lambda: d.click("#btn-open-import"))
    r.check("03 import modal visible", d.visible("#import-modal"),
            "visible")
    r.check("04 forest unchecked", not is_checked(d, "#chk-import-forest"),
            is_checked(d, "#chk-import-forest"))
    r.check("04 city unchecked", not is_checked(d, "#chk-import-city"),
            is_checked(d, "#chk-import-city"))
    r.check("04 score unchecked", not is_checked(d, "#chk-import-score"),
            is_checked(d, "#chk-import-score"))
    r.step("05 check import forest", "click",
           lambda: d.click("#chk-import-forest"))
    r.check("05 forest checked", is_checked(d, "#chk-import-forest"),
            is_checked(d, "#chk-import-forest"))
    r.step("06 check import city", "click",
           lambda: d.click("#chk-import-city"))
    r.check("06 city checked", is_checked(d, "#chk-import-city"),
            is_checked(d, "#chk-import-city"))
    r.step("07 check import score", "click",
           lambda: d.click("#chk-import-score"))
    r.check("07 score checked", is_checked(d, "#chk-import-score"),
            is_checked(d, "#chk-import-score"))
    r.step("08 import selected", "click",
           lambda: d.click("#btn-import-selected"))
    r.check("08 imported count 3",
            txt(d, "#imported-clip-count") == "3",
            txt(d, "#imported-clip-count"))
    r.check("09 media forest name",
            txt(d, "#media-name-forest") == "Forest A-roll (12 sec)",
            txt(d, "#media-name-forest"))
    r.check("09 media city name",
            txt(d, "#media-name-city") == "City B-roll (8 sec)",
            txt(d, "#media-name-city"))
    r.check("09 media score name",
            txt(d, "#media-name-score") == "Night Score (20 sec)",
            txt(d, "#media-name-score"))
    r.step("10 add forest", "click", lambda: d.click("#btn-add-forest"))
    r.check("10 timeline count 1",
            txt(d, "#timeline-clip-count") == "1",
            txt(d, "#timeline-clip-count"))
    r.step("11 add city", "click", lambda: d.click("#btn-add-city"))
    r.check("11 timeline count 2",
            txt(d, "#timeline-clip-count") == "2",
            txt(d, "#timeline-clip-count"))
    r.check("12 timeline duration 20 sec",
            txt(d, "#timeline-duration") == "20 sec",
            txt(d, "#timeline-duration"))
    r.check("12 timeline order exact",
            txt(d, "#timeline-order")
            == "Forest A-roll (12 sec)\nCity B-roll (8 sec)",
            txt(d, "#timeline-order"))
    # Step 13: the click is LOAD-BEARING (redteam M3): the split acts
    # on the SELECTED clip. Click first, then set the playhead.
    r.step("13 select forest clip", "click",
           lambda: d.click("#btn-select-forest"))
    r.step("13 set playhead 5", "type",
           lambda: d.type_text("#playhead-input", "5"))
    r.check("13 playhead value 5",
            d.value("#playhead-input") == "5",
            d.value("#playhead-input"))
    r.step("14 split selected", "click",
           lambda: d.click("#btn-split-selected"))
    r.check("14 timeline count 3",
            txt(d, "#timeline-clip-count") == "3",
            txt(d, "#timeline-clip-count"))
    r.check("15 timeline duration 20 sec",
            txt(d, "#timeline-duration") == "20 sec",
            txt(d, "#timeline-duration"))
    r.check("15 timeline order exact",
            txt(d, "#timeline-order")
            == "Forest A-roll (5 sec)\nForest A-roll (7 sec)\nCity B-roll (8 sec)",
            txt(d, "#timeline-order"))
    r.step("16 select forest tail", "click",
           lambda: d.click("#btn-select-forest-tail"))
    r.check("16 timeline selection forest",
            txt(d, "#timeline-selection") == "Selected Forest A-roll",
            txt(d, "#timeline-selection"))
    r.step("17 mistake trim 2", "type",
           lambda: d.type_text("#trim-duration-input", "2"))
    r.check("17 trim value 2",
            d.value("#trim-duration-input") == "2",
            d.value("#trim-duration-input"))
    r.step("18 apply trim", "click",
           lambda: d.click("#btn-apply-trim"))
    r.check("18 timeline duration 15 sec",
            txt(d, "#timeline-duration") == "15 sec",
            txt(d, "#timeline-duration"))
    r.check("19 timeline order exact",
            txt(d, "#timeline-order")
            == "Forest A-roll (5 sec)\nForest A-roll (2 sec)\nCity B-roll (8 sec)",
            txt(d, "#timeline-order"))
    r.step("20 recovery undo edit", "click",
           lambda: d.click("#btn-undo-edit"))
    r.check("20 timeline duration 20 sec",
            txt(d, "#timeline-duration") == "20 sec",
            txt(d, "#timeline-duration"))
    r.check("21 timeline order exact",
            txt(d, "#timeline-order")
            == "Forest A-roll (5 sec)\nForest A-roll (7 sec)\nCity B-roll (8 sec)",
            txt(d, "#timeline-order"))
    r.step("22 trim 6", "type",
           lambda: d.type_text("#trim-duration-input", "6"))
    r.check("22 trim value 6",
            d.value("#trim-duration-input") == "6",
            d.value("#trim-duration-input"))
    r.step("23 apply trim", "click",
           lambda: d.click("#btn-apply-trim"))
    r.check("23 timeline duration 19 sec",
            txt(d, "#timeline-duration") == "19 sec",
            txt(d, "#timeline-duration"))
    r.check("24 timeline order exact",
            txt(d, "#timeline-order")
            == "Forest A-roll (5 sec)\nForest A-roll (6 sec)\nCity B-roll (8 sec)",
            txt(d, "#timeline-order"))
    r.step("25 select city clip", "click",
           lambda: d.click("#btn-select-city"))
    r.check("25 timeline selection city",
            txt(d, "#timeline-selection") == "Selected City B-roll",
            txt(d, "#timeline-selection"))
    r.step("26 move selected left", "click",
           lambda: d.click("#btn-move-selected-left"))
    r.check("26 timeline order exact",
            txt(d, "#timeline-order")
            == "Forest A-roll (5 sec)\nCity B-roll (8 sec)\nForest A-roll (6 sec)",
            txt(d, "#timeline-order"))
    r.step("27 move selected left again", "click",
           lambda: d.click("#btn-move-selected-left"))
    r.check("27 timeline order exact",
            txt(d, "#timeline-order")
            == "City B-roll (8 sec)\nForest A-roll (5 sec)\nForest A-roll (6 sec)",
            txt(d, "#timeline-order"))
    r.check("28 timeline order exact",
            txt(d, "#timeline-order")
            == "City B-roll (8 sec)\nForest A-roll (5 sec)\nForest A-roll (6 sec)",
            txt(d, "#timeline-order"))
    r.check("28 timeline duration 19 sec",
            txt(d, "#timeline-duration") == "19 sec",
            txt(d, "#timeline-duration"))
    r.step("29 select Cross Dissolve", "select",
           lambda: select_option(d, "#transition-type", "Cross Dissolve"))
    r.check("29 transition type Cross Dissolve",
            d.value("#transition-type") == "Cross Dissolve",
            d.value("#transition-type"))
    r.step("30 add transition", "click",
           lambda: d.click("#btn-add-transition"))
    r.check("30 transition summary",
            txt(d, "#transition-summary")
            == "Cross Dissolve between City B-roll and Forest A-roll",
            txt(d, "#transition-summary"))
    r.step("31 select resolution", "select",
           lambda: select_option(d, "#export-resolution-select",
                                 "1920x1080"))
    r.check("31 resolution 1920x1080",
            d.value("#export-resolution-select") == "1920x1080",
            d.value("#export-resolution-select"))
    r.step("32 select frame rate", "select",
           lambda: select_option(d, "#export-frame-rate-select", "30 fps"))
    r.check("32 frame rate 30 fps",
            d.value("#export-frame-rate-select") == "30 fps",
            d.value("#export-frame-rate-select"))
    r.step("33 select codec", "select",
           lambda: select_option(d, "#export-codec-select", "H.264"))
    r.check("33 codec H.264",
            d.value("#export-codec-select") == "H.264",
            d.value("#export-codec-select"))
    r.step("34 type export filename", "type",
           lambda: d.type_text("#export-filename-input", "harbor-recap.mp4"))
    r.check("34 export filename value",
            d.value("#export-filename-input") == "harbor-recap.mp4",
            d.value("#export-filename-input"))
    r.step("35 export video", "click",
           lambda: d.click("#btn-export-video"))
    r.check("35 export status",
            txt(d, "#export-status")
            == "Export complete: harbor-recap.mp4 (1920x1080, 30 fps, H.264)",
            txt(d, "#export-status"))
    r.check("36 export resolution",
            txt(d, "#export-resolution") == "1920x1080",
            txt(d, "#export-resolution"))
    r.check("36 export frame rate",
            txt(d, "#export-frame-rate") == "30 fps",
            txt(d, "#export-frame-rate"))
    r.check("36 export codec",
            txt(d, "#export-codec") == "H.264",
            txt(d, "#export-codec"))
    r.check("36 export filename",
            txt(d, "#export-filename") == "harbor-recap.mp4",
            txt(d, "#export-filename"))
    r.check("36 export status",
            txt(d, "#export-status")
            == "Export complete: harbor-recap.mp4 (1920x1080, 30 fps, H.264)",
            txt(d, "#export-status"))
    final_verify(r, d, "06")


def run_07(r, d):
    open_fixture(r, d, "test-07-chat-search.html", "07")
    r.check("02 search count starts 0",
            txt(d, "#search-result-count") == "0",
            txt(d, "#search-result-count"))
    r.check("02 active message starts none",
            txt(d, "#active-message-text") == "No message selected",
            txt(d, "#active-message-text"))
    r.check("02 active room starts None",
            txt(d, "#active-room") == "None", txt(d, "#active-room"))
    r.step("03 type search query", "type",
           lambda: d.type_text("#search-query-input", "Release checklist"))
    r.check("03 search query value",
            d.value("#search-query-input") == "Release checklist",
            d.value("#search-query-input"))
    r.step("04 search messages", "click",
           lambda: d.click("#btn-search-messages"))
    r.check("04 search count 3",
            txt(d, "#search-result-count") == "3",
            txt(d, "#search-result-count"))
    r.check("05 filter summary 3 matching",
            txt(d, "#filter-summary") == "3 matching messages",
            txt(d, "#filter-summary"))
    r.check("05 open result m1 text",
            txt(d, "#btn-open-result-m1") == "Jump to result",
            txt(d, "#btn-open-result-m1"))
    r.check("05 open result m2 text",
            txt(d, "#btn-open-result-m2") == "Jump to result",
            txt(d, "#btn-open-result-m2"))
    r.step("06 mistake select Design Bot", "select",
           lambda: select_option(d, "#sender-filter", "Design Bot"))
    r.check("06 sender filter Design Bot",
            d.value("#sender-filter") == "Design Bot",
            d.value("#sender-filter"))
    r.step("07 apply filters", "click",
           lambda: d.click("#btn-apply-filters"))
    r.check("07 search count 1",
            txt(d, "#search-result-count") == "1",
            txt(d, "#search-result-count"))
    r.check("08 filter summary 1 matching",
            txt(d, "#filter-summary") == "1 matching message",
            txt(d, "#filter-summary"))
    r.check("08 open result m3 text",
            txt(d, "#btn-open-result-m3") == "Jump to result",
            txt(d, "#btn-open-result-m3"))
    r.step("09 recovery select Build Bot", "select",
           lambda: select_option(d, "#sender-filter", "Build Bot"))
    r.check("09 sender filter Build Bot",
            d.value("#sender-filter") == "Build Bot",
            d.value("#sender-filter"))
    r.step("10 apply filters", "click",
           lambda: d.click("#btn-apply-filters"))
    r.check("10 search count 2",
            txt(d, "#search-result-count") == "2",
            txt(d, "#search-result-count"))
    r.check("11 filter summary 2 matching",
            txt(d, "#filter-summary") == "2 matching messages",
            txt(d, "#filter-summary"))
    r.check("11 open result m1 text",
            txt(d, "#btn-open-result-m1") == "Jump to result",
            txt(d, "#btn-open-result-m1"))
    r.step("12 type from date", "type",
           lambda: d.type_text("#from-date-input", "2026-10-12"))
    r.check("12 from date value",
            d.value("#from-date-input") == "2026-10-12",
            d.value("#from-date-input"))
    r.step("13 type to date", "type",
           lambda: d.type_text("#to-date-input", "2026-10-12"))
    r.check("13 to date value",
            d.value("#to-date-input") == "2026-10-12",
            d.value("#to-date-input"))
    r.step("14 apply filters", "click",
           lambda: d.click("#btn-apply-filters"))
    r.check("14 search count 1",
            txt(d, "#search-result-count") == "1",
            txt(d, "#search-result-count"))
    r.check("15 filter summary 1 matching",
            txt(d, "#filter-summary") == "1 matching message",
            txt(d, "#filter-summary"))
    r.check("15 open result m1 text",
            txt(d, "#btn-open-result-m1") == "Jump to result",
            txt(d, "#btn-open-result-m1"))
    r.step("16 open result m1", "click",
           lambda: d.click("#btn-open-result-m1"))
    r.check("16 active message text",
            txt(d, "#active-message-text")
            == "Release checklist is ready for review.",
            txt(d, "#active-message-text"))
    r.check("17 active message sender Build Bot",
            txt(d, "#active-message-sender") == "Build Bot",
            txt(d, "#active-message-sender"))
    r.check("17 active message date 2026-10-12",
            txt(d, "#active-message-date") == "2026-10-12",
            txt(d, "#active-message-date"))
    r.check("17 active room Build Room",
            txt(d, "#active-room") == "Build Room", txt(d, "#active-room"))
    r.step("18 star message", "click",
           lambda: d.click("#btn-star-message"))
    r.check("18 star status Starred",
            txt(d, "#star-status") == "Starred", txt(d, "#star-status"))
    r.check("19 star status Starred",
            txt(d, "#star-status") == "Starred", txt(d, "#star-status"))
    r.step("20 forward message", "click",
           lambda: d.click("#btn-forward-message"))
    r.check("20 forward modal visible", d.visible("#forward-modal"),
            "visible")
    fwd_heading = r.step("20 read forward modal heading", "text",
                         lambda: d.eval(
                             "const h=document.querySelector"
                             "('#forward-modal h2');"
                             " return h ? h.textContent.trim() : null;"))
    r.check("20 forward modal heading",
            fwd_heading == "Forward message", fwd_heading)
    r.step("21 type forward room", "type",
           lambda: d.type_text("#forward-room-input", "Release Room"))
    r.check("21 forward room value",
            d.value("#forward-room-input") == "Release Room",
            d.value("#forward-room-input"))
    r.step("22 confirm forward", "click",
           lambda: d.click("#btn-confirm-forward"))
    r.check("22 forward status",
            txt(d, "#forward-status") == "Forwarded to Release Room",
            txt(d, "#forward-status"))
    r.check("23 search count 1",
            txt(d, "#search-result-count") == "1",
            txt(d, "#search-result-count"))
    r.check("23 active message text",
            txt(d, "#active-message-text")
            == "Release checklist is ready for review.",
            txt(d, "#active-message-text"))
    r.check("23 star status Starred",
            txt(d, "#star-status") == "Starred", txt(d, "#star-status"))
    r.check("23 forward status",
            txt(d, "#forward-status") == "Forwarded to Release Room",
            txt(d, "#forward-status"))
    r.check("23 forwarded count 1",
            txt(d, "#forwarded-count") == "1",
            txt(d, "#forwarded-count"))
    r.check("23 active room Release Room",
            txt(d, "#active-room") == "Release Room",
            txt(d, "#active-room"))
    final_verify(r, d, "07")


def run_08(r, d):
    open_fixture(r, d, "test-08-spreadsheet-pivot.html", "08")
    r.check("02 source row count 6",
            txt(d, "#source-row-count") == "6",
            txt(d, "#source-row-count"))
    r.check("02 pivot row count starts 0",
            txt(d, "#pivot-row-count") == "0", txt(d, "#pivot-row-count"))
    r.check("02 pivot status starts none",
            txt(d, "#pivot-status") == "No pivot table",
            txt(d, "#pivot-status"))
    r.check("02 hardware total starts -",
            txt(d, "#pivot-hardware-total") == "-",
            txt(d, "#pivot-hardware-total"))
    r.check("02 grand total starts -",
            txt(d, "#pivot-grand-total") == "-",
            txt(d, "#pivot-grand-total"))
    r.step("03 create pivot", "click",
           lambda: d.click("#btn-create-pivot"))
    r.check("03 pivot status created",
            txt(d, "#pivot-status") == "Pivot created from 6 rows",
            txt(d, "#pivot-status"))
    r.check("04 pivot status created",
            txt(d, "#pivot-status") == "Pivot created from 6 rows",
            txt(d, "#pivot-status"))
    r.check("04 pivot group field None",
            txt(d, "#pivot-group-field") == "None",
            txt(d, "#pivot-group-field"))
    r.check("04 pivot value field None",
            txt(d, "#pivot-value-field") == "None",
            txt(d, "#pivot-value-field"))
    r.step("05 select group Category", "select",
           lambda: select_option(d, "#pivot-group-select", "Category"))
    r.check("05 group select Category",
            d.value("#pivot-group-select") == "Category",
            d.value("#pivot-group-select"))
    r.check("06 group select Category",
            d.value("#pivot-group-select") == "Category",
            d.value("#pivot-group-select"))
    r.step("07 select value Amount", "select",
           lambda: select_option(d, "#pivot-value-select", "Amount"))
    r.check("07 value select Amount",
            d.value("#pivot-value-select") == "Amount",
            d.value("#pivot-value-select"))
    r.check("08 value select Amount",
            d.value("#pivot-value-select") == "Amount",
            d.value("#pivot-value-select"))
    r.step("09 mistake select Count", "select",
           lambda: select_option(d, "#pivot-aggregation-select", "Count"))
    r.check("09 aggregation select Count",
            d.value("#pivot-aggregation-select") == "Count",
            d.value("#pivot-aggregation-select"))
    r.step("10 refresh pivot", "click",
           lambda: d.click("#btn-refresh-pivot"))
    r.check("10 pivot status ready",
            txt(d, "#pivot-status") == "Pivot table ready",
            txt(d, "#pivot-status"))
    r.check("11 hardware total 3 (count)",
            txt(d, "#pivot-hardware-total") == "3",
            txt(d, "#pivot-hardware-total"))
    r.check("11 software total 3 (count)",
            txt(d, "#pivot-software-total") == "3",
            txt(d, "#pivot-software-total"))
    r.check("11 grand total 6 (count)",
            txt(d, "#pivot-grand-total") == "6",
            txt(d, "#pivot-grand-total"))
    r.step("12 recovery select Sum", "select",
           lambda: select_option(d, "#pivot-aggregation-select", "Sum"))
    r.check("12 aggregation select Sum",
            d.value("#pivot-aggregation-select") == "Sum",
            d.value("#pivot-aggregation-select"))
    r.step("13 refresh pivot", "click",
           lambda: d.click("#btn-refresh-pivot"))
    r.check("13 grand total 5200",
            txt(d, "#pivot-grand-total") == "5200",
            txt(d, "#pivot-grand-total"))
    r.check("14 pivot group field Category",
            txt(d, "#pivot-group-field") == "Category",
            txt(d, "#pivot-group-field"))
    r.check("14 pivot value field Amount",
            txt(d, "#pivot-value-field") == "Amount",
            txt(d, "#pivot-value-field"))
    r.check("14 pivot aggregation Sum",
            txt(d, "#pivot-aggregation") == "Sum",
            txt(d, "#pivot-aggregation"))
    r.check("14 hardware total 2300",
            txt(d, "#pivot-hardware-total") == "2300",
            txt(d, "#pivot-hardware-total"))
    r.check("14 software total 2900",
            txt(d, "#pivot-software-total") == "2900",
            txt(d, "#pivot-software-total"))
    r.check("14 grand total 5200",
            txt(d, "#pivot-grand-total") == "5200",
            txt(d, "#pivot-grand-total"))
    r.step("15 select filter South", "select",
           lambda: select_option(d, "#pivot-filter-select", "South"))
    r.check("15 filter select South",
            d.value("#pivot-filter-select") == "South",
            d.value("#pivot-filter-select"))
    r.step("16 refresh pivot", "click",
           lambda: d.click("#btn-refresh-pivot"))
    r.check("16 pivot filter region South",
            txt(d, "#pivot-filter-region") == "South",
            txt(d, "#pivot-filter-region"))
    r.check("17 hardware total 600",
            txt(d, "#pivot-hardware-total") == "600",
            txt(d, "#pivot-hardware-total"))
    r.check("17 software total 1400",
            txt(d, "#pivot-software-total") == "1400",
            txt(d, "#pivot-software-total"))
    r.check("17 grand total 2000",
            txt(d, "#pivot-grand-total") == "2000",
            txt(d, "#pivot-grand-total"))
    r.step("18 replace source south hardware", "type",
           lambda: d.type_text("#source-south-hardware", "900"))
    r.check("18 source south hardware 900",
            d.value("#source-south-hardware") == "900",
            d.value("#source-south-hardware"))
    r.check("19 source south hardware 900",
            d.value("#source-south-hardware") == "900",
            d.value("#source-south-hardware"))
    r.check("19 pivot hardware still 600 before refresh",
            txt(d, "#pivot-hardware-total") == "600",
            txt(d, "#pivot-hardware-total"))
    r.check("19 pivot grand still 2000 before refresh",
            txt(d, "#pivot-grand-total") == "2000",
            txt(d, "#pivot-grand-total"))
    r.step("20 refresh pivot", "click",
           lambda: d.click("#btn-refresh-pivot"))
    r.check("20 pivot hardware 900",
            txt(d, "#pivot-hardware-total") == "900",
            txt(d, "#pivot-hardware-total"))
    r.check("21 pivot group field Category",
            txt(d, "#pivot-group-field") == "Category",
            txt(d, "#pivot-group-field"))
    r.check("21 pivot value field Amount",
            txt(d, "#pivot-value-field") == "Amount",
            txt(d, "#pivot-value-field"))
    r.check("21 pivot aggregation Sum",
            txt(d, "#pivot-aggregation") == "Sum",
            txt(d, "#pivot-aggregation"))
    r.check("21 pivot filter region South",
            txt(d, "#pivot-filter-region") == "South",
            txt(d, "#pivot-filter-region"))
    r.check("21 pivot row count 2",
            txt(d, "#pivot-row-count") == "2", txt(d, "#pivot-row-count"))
    r.check("21 hardware total 900",
            txt(d, "#pivot-hardware-total") == "900",
            txt(d, "#pivot-hardware-total"))
    r.check("21 software total 1400",
            txt(d, "#pivot-software-total") == "1400",
            txt(d, "#pivot-software-total"))
    r.check("21 grand total 2300",
            txt(d, "#pivot-grand-total") == "2300",
            txt(d, "#pivot-grand-total"))
    r.check("21 refresh status",
            txt(d, "#pivot-refresh-status") == "Pivot refreshed from 6 rows",
            txt(d, "#pivot-refresh-status"))
    r.check("21 source south hardware 900",
            d.value("#source-south-hardware") == "900",
            d.value("#source-south-hardware"))
    final_verify(r, d, "08")


def run_09(r, d):
    open_fixture(r, d, "test-09-file-search-tag.html", "09")
    r.check("02 active folder starts Root",
            txt(d, "#active-folder") == "Root", txt(d, "#active-folder"))
    r.check("02 visible file count starts 6",
            txt(d, "#visible-file-count") == "6",
            txt(d, "#visible-file-count"))
    r.check("02 selected file count starts 0",
            txt(d, "#selected-file-count") == "0",
            txt(d, "#selected-file-count"))
    r.check("02 tag filter starts All",
            txt(d, "#active-tag-filter") == "All",
            txt(d, "#active-tag-filter"))
    r.step("03 type file search", "type",
           lambda: d.type_text("#file-search-input", "releases"))
    r.check("03 file search value",
            d.value("#file-search-input") == "releases",
            d.value("#file-search-input"))
    r.step("04 search files", "click",
           lambda: d.click("#btn-search-files"))
    r.check("04 visible file count 0",
            txt(d, "#visible-file-count") == "0",
            txt(d, "#visible-file-count"))
    r.check("05 file list no matching",
            txt(d, "#file-list") == "No matching files",
            txt(d, "#file-list"))
    r.check("05 visible file count 0",
            txt(d, "#visible-file-count") == "0",
            txt(d, "#visible-file-count"))
    r.step("06 recovery replace search", "type",
           lambda: d.type_text("#file-search-input", "release"))
    r.check("06 file search value",
            d.value("#file-search-input") == "release",
            d.value("#file-search-input"))
    r.step("07 search files", "click",
           lambda: d.click("#btn-search-files"))
    r.check("07 visible file count 3",
            txt(d, "#visible-file-count") == "3",
            txt(d, "#visible-file-count"))
    r.check("08 file name checklist",
            txt(d, "#file-name-checklist") == "release-checklist.md",
            txt(d, "#file-name-checklist"))
    r.check("08 file name plan",
            txt(d, "#file-name-plan") == "release-plan.md",
            txt(d, "#file-name-plan"))
    r.check("08 file name artwork",
            txt(d, "#file-name-artwork") == "release-artwork.png",
            txt(d, "#file-name-artwork"))
    # Checkboxes re-render the file list on change (council 2):
    # every click re-finds its element fresh (d.click does find).
    r.step("09 check checklist", "click",
           lambda: d.click("#check-file-checklist"))
    r.check("09 selected count 1",
            txt(d, "#selected-file-count") == "1",
            txt(d, "#selected-file-count"))
    r.step("10 check plan", "click", lambda: d.click("#check-file-plan"))
    r.check("10 selected count 2",
            txt(d, "#selected-file-count") == "2",
            txt(d, "#selected-file-count"))
    r.check("11 selected count 2",
            txt(d, "#selected-file-count") == "2",
            txt(d, "#selected-file-count"))
    r.step("12 open tag panel", "click",
           lambda: d.click("#btn-open-tag-panel"))
    r.check("12 tag panel visible", d.visible("#tag-panel"), "visible")
    r.step("13 type tag name", "type",
           lambda: d.type_text("#tag-name-input", "Review"))
    r.check("13 tag name value",
            d.value("#tag-name-input") == "Review",
            d.value("#tag-name-input"))
    r.step("14 apply tag", "click", lambda: d.click("#btn-apply-tag"))
    r.check("14 action status tagged",
            txt(d, "#file-action-status") == "Tagged 2 files with Review",
            txt(d, "#file-action-status"))
    r.check("15 tag checklist Review",
            txt(d, "#tag-checklist") == "Review", txt(d, "#tag-checklist"))
    r.check("15 tag plan Review",
            txt(d, "#tag-plan") == "Review", txt(d, "#tag-plan"))
    r.check("15 tag artwork none",
            txt(d, "#tag-artwork") == "No tag", txt(d, "#tag-artwork"))
    r.step("16 filter Review", "click",
           lambda: d.click("#btn-filter-review"))
    r.check("16 tag filter Review",
            txt(d, "#active-tag-filter") == "Review",
            txt(d, "#active-tag-filter"))
    r.check("17 visible file count 2",
            txt(d, "#visible-file-count") == "2",
            txt(d, "#visible-file-count"))
    r.check("17 file name checklist",
            txt(d, "#file-name-checklist") == "release-checklist.md",
            txt(d, "#file-name-checklist"))
    r.check("17 file name plan",
            txt(d, "#file-name-plan") == "release-plan.md",
            txt(d, "#file-name-plan"))
    r.step("18 select visible files", "click",
           lambda: d.click("#btn-select-visible-files"))
    r.check("18 selected count 2",
            txt(d, "#selected-file-count") == "2",
            txt(d, "#selected-file-count"))
    r.step("19 type rename prefix", "type",
           lambda: d.type_text("#rename-prefix-input", "approved-"))
    r.check("19 rename prefix value",
            d.value("#rename-prefix-input") == "approved-",
            d.value("#rename-prefix-input"))
    r.step("20 rename selected", "click",
           lambda: d.click("#btn-rename-selected"))
    r.check("20 file name checklist approved",
            txt(d, "#file-name-checklist")
            == "approved-release-checklist.md",
            txt(d, "#file-name-checklist"))
    r.check("21 file name plan approved",
            txt(d, "#file-name-plan") == "approved-release-plan.md",
            txt(d, "#file-name-plan"))
    r.check("21 tag filter Review",
            txt(d, "#active-tag-filter") == "Review",
            txt(d, "#active-tag-filter"))
    r.step("22 select move target Reviewed", "select",
           lambda: select_option(d, "#move-target-folder", "Reviewed"))
    r.check("22 move target Reviewed",
            d.value("#move-target-folder") == "Reviewed",
            d.value("#move-target-folder"))
    r.step("23 move selected", "click",
           lambda: d.click("#btn-move-selected"))
    r.check("23 active folder Reviewed",
            txt(d, "#active-folder") == "Reviewed",
            txt(d, "#active-folder"))
    r.check("24 active folder Reviewed",
            txt(d, "#active-folder") == "Reviewed",
            txt(d, "#active-folder"))
    r.check("24 tag filter Review",
            txt(d, "#active-tag-filter") == "Review",
            txt(d, "#active-tag-filter"))
    r.check("24 visible file count 2",
            txt(d, "#visible-file-count") == "2",
            txt(d, "#visible-file-count"))
    r.check("24 file name checklist approved",
            txt(d, "#file-name-checklist")
            == "approved-release-checklist.md",
            txt(d, "#file-name-checklist"))
    r.check("24 file name plan approved",
            txt(d, "#file-name-plan") == "approved-release-plan.md",
            txt(d, "#file-name-plan"))
    r.check("24 tag checklist Review",
            txt(d, "#tag-checklist") == "Review", txt(d, "#tag-checklist"))
    r.check("24 tag plan Review",
            txt(d, "#tag-plan") == "Review", txt(d, "#tag-plan"))
    r.check("24 location checklist Reviewed",
            txt(d, "#file-location-checklist") == "Reviewed",
            txt(d, "#file-location-checklist"))
    r.check("24 location plan Reviewed",
            txt(d, "#file-location-plan") == "Reviewed",
            txt(d, "#file-location-plan"))
    r.check("24 action status moved",
            txt(d, "#file-action-status")
            == "Moved 2 tagged files to Reviewed",
            txt(d, "#file-action-status"))
    final_verify(r, d, "09")


def _reload_settings(d, r, step):
    """Click #btn-reload-settings with navigation tolerance (RT M6):
    the click may raise after the navigation (stale element / dead
    object / document unloaded). Evidence-based tolerance: if the
    click raises, check whether the reload actually happened
    (wait_ready + the persistence status text within 10 s). If yes,
    treat as success-then-wait and log the tolerance; if no,
    re-raise as a step failure. Then run the ensure_visible ladder
    (a reload is a new document). A ladder failure raises plainly;
    main()'s diagnose-on-step-failure classifies it (hidden body
    reclassifies to INFRA, visible stays a live failure).
    Returns "reloaded" (or "reloaded (click raised, tolerance)").
    """
    raised = None
    # Council A F9 reload proof: set a window marker BEFORE the
    # click; a real navigation creates a fresh window object, so
    # the marker must be GONE after the reload. Without this, a
    # click that raises for a NON-navigation reason (button missing,
    # wrong page state) could pass the persistence wait_for below
    # on STALE text: step 26 runs after step 21 already set
    # "State restored after reload", so the text is already there
    # even if the second reload never happened. A surviving marker
    # is proof the reload did not land, and raises a step failure.
    d.eval("window.__y13_reload_probe = 'before-reload';"
           " return 'marker-set';")
    try:
        d.click("#btn-reload-settings")
    except Exception as exc:
        raised = exc
    d.wait_ready()
    time.sleep(1.0)
    ok, swapped = ensure_visible(d, r, "reloaded settings page")
    if swapped:
        # Council B F3: a swapped ladder leaves a fresh about:blank
        # tab with no fixture and no sessionStorage. The persistence
        # wait_for below would time out after 10 s on that empty tab
        # and a genuine tz-hidden incident would read as a live
        # failure. Raise INFRA before the wait_for. (InfraError is
        # re-raised unwrapped by r.step, so main() sees the marker
        # class directly; see the exception handler there.)
        raise InfraError(
            "INFRA: hidden-body after settings reload; ladder swapped "
            "to a fresh tab, fixture not loaded")
    if not ok:
        raise RuntimeError("reload: hidden-body after settings reload")
    # Y13f F9: wrap the marker typeof eval so a transport raise is
    # reported as a reload marker check failure (with context)
    # rather than propagating raw, and treat a None typeof result
    # as inconclusive rather than "survived": in real Marionette
    # typeof always yields a string, so None means the eval itself
    # misbehaved mid-navigation. Both are fail-closed (step fails,
    # no false pass).
    try:
        marker = d.eval("return typeof window.__y13_reload_probe;")
    except Exception as exc:
        raise RuntimeError(
            f"reload settings: marker check failed "
            f"({type(exc).__name__}: {exc}); reload unproven")
    if marker is None:
        raise RuntimeError(
            "reload settings: marker check inconclusive (typeof "
            "returned null); reload unproven")
    if marker != "undefined":
        if raised is not None:
            raise RuntimeError(
                f"reload settings: click raised "
                f"{type(raised).__name__}: {raised}; and the reload "
                f"did not land (marker survived)")
        raise RuntimeError(
            "reload settings: reload did not land (marker survived "
            "the click)")
    try:
        d.wait_for(
            "document.querySelector('#extension-persistence-status') && "
            "document.querySelector('#extension-persistence-status')"
            ".textContent.trim() === 'State restored after reload'",
            10, "#extension-persistence-status restored")
    except Exception as exc:
        if raised is not None:
            raise RuntimeError(
                f"reload settings: click raised "
                f"{type(raised).__name__}: {raised}; and the reload "
                f"did not land: {exc}")
        raise
    if raised is not None:
        print(f"[{r.test}] {step} reload click raised "
              f"{type(raised).__name__} but the reload landed "
              f"(tolerance applied)", flush=True)
        return "reloaded (click raised, tolerance)"
    return "reloaded"


def run_10(r, d):
    open_fixture(r, d, "test-10-extension-settings.html", "10")
    r.check("02 extension starts Disabled",
            txt(d, "#extension-enabled-state") == "Disabled",
            txt(d, "#extension-enabled-state"))
    r.check("02 calendar permission starts Ask",
            txt(d, "#site-calendar-permission") == "Ask",
            txt(d, "#site-calendar-permission"))
    r.check("02 drive permission starts Ask",
            txt(d, "#site-drive-permission") == "Ask",
            txt(d, "#site-drive-permission"))
    r.check("02 notify starts On",
            txt(d, "#option-notify-state") == "On",
            txt(d, "#option-notify-state"))
    r.check("02 auto-update starts On",
            txt(d, "#option-auto-update-state") == "On",
            txt(d, "#option-auto-update-state"))
    r.check("02 options save starts not saved",
            txt(d, "#options-save-status") == "Not saved",
            txt(d, "#options-save-status"))
    r.check("02 persistence starts not reloaded",
            txt(d, "#extension-persistence-status") == "Not reloaded",
            txt(d, "#extension-persistence-status"))
    r.step("03 toggle extension", "click",
           lambda: d.click("#btn-toggle-extension"))
    r.check("03 extension Enabled",
            txt(d, "#extension-enabled-state") == "Enabled",
            txt(d, "#extension-enabled-state"))
    r.check("04 extension Enabled",
            txt(d, "#extension-enabled-state") == "Enabled",
            txt(d, "#extension-enabled-state"))
    r.step("05 toggle extension", "click",
           lambda: d.click("#btn-toggle-extension"))
    r.check("05 extension Disabled",
            txt(d, "#extension-enabled-state") == "Disabled",
            txt(d, "#extension-enabled-state"))
    r.check("06 extension Disabled",
            txt(d, "#extension-enabled-state") == "Disabled",
            txt(d, "#extension-enabled-state"))
    r.step("07 toggle extension", "click",
           lambda: d.click("#btn-toggle-extension"))
    r.check("07 extension Enabled",
            txt(d, "#extension-enabled-state") == "Enabled",
            txt(d, "#extension-enabled-state"))
    r.step("08 open sites", "click", lambda: d.click("#btn-open-sites"))
    r.check("08 site access page visible",
            d.visible("#site-access-page"), "visible")
    r.step("09 mistake select Block calendar", "select",
           lambda: select_option(d, "#site-calendar-select", "Block"))
    r.check("09 calendar select Block",
            d.value("#site-calendar-select") == "Block",
            d.value("#site-calendar-select"))
    r.step("10 save site permissions", "click",
           lambda: d.click("#btn-save-site-permissions"))
    r.check("10 calendar permission Block",
            txt(d, "#site-calendar-permission") == "Block",
            txt(d, "#site-calendar-permission"))
    r.check("11 calendar permission Block",
            txt(d, "#site-calendar-permission") == "Block",
            txt(d, "#site-calendar-permission"))
    r.check("11 drive permission Ask",
            txt(d, "#site-drive-permission") == "Ask",
            txt(d, "#site-drive-permission"))
    r.step("12 recovery select Allow calendar", "select",
           lambda: select_option(d, "#site-calendar-select", "Allow"))
    r.check("12 calendar select Allow",
            d.value("#site-calendar-select") == "Allow",
            d.value("#site-calendar-select"))
    r.step("13 select Block drive", "select",
           lambda: select_option(d, "#site-drive-select", "Block"))
    r.check("13 drive select Block",
            d.value("#site-drive-select") == "Block",
            d.value("#site-drive-select"))
    r.step("14 save site permissions", "click",
           lambda: d.click("#btn-save-site-permissions"))
    r.check("14 calendar permission Allow",
            txt(d, "#site-calendar-permission") == "Allow",
            txt(d, "#site-calendar-permission"))
    r.check("14 drive permission Block",
            txt(d, "#site-drive-permission") == "Block",
            txt(d, "#site-drive-permission"))
    r.check("15 calendar permission Allow",
            txt(d, "#site-calendar-permission") == "Allow",
            txt(d, "#site-calendar-permission"))
    r.check("15 drive permission Block",
            txt(d, "#site-drive-permission") == "Block",
            txt(d, "#site-drive-permission"))
    r.step("16 open options", "click",
           lambda: d.click("#btn-open-options"))
    r.check("16 options page visible", d.visible("#options-page"),
            "visible")
    r.step("17 notify toggle off", "click",
           lambda: d.click("#option-notify-toggle"))
    r.check("17 notify Off",
            txt(d, "#option-notify-state") == "Off",
            txt(d, "#option-notify-state"))
    r.step("18 auto-update toggle off", "click",
           lambda: d.click("#option-auto-update-toggle"))
    r.check("18 auto-update Off",
            txt(d, "#option-auto-update-state") == "Off",
            txt(d, "#option-auto-update-state"))
    r.step("19 save options", "click",
           lambda: d.click("#btn-save-options"))
    r.check("19 options save status saved",
            txt(d, "#options-save-status") == "Options saved",
            txt(d, "#options-save-status"))
    r.check("20 notify Off",
            txt(d, "#option-notify-state") == "Off",
            txt(d, "#option-notify-state"))
    r.check("20 auto-update Off",
            txt(d, "#option-auto-update-state") == "Off",
            txt(d, "#option-auto-update-state"))
    r.check("20 options save status saved",
            txt(d, "#options-save-status") == "Options saved",
            txt(d, "#options-save-status"))
    r.step("21 reload settings", "click",
           lambda: _reload_settings(d, r, "21"))
    r.check("21 persistence restored",
            txt(d, "#extension-persistence-status")
            == "State restored after reload",
            txt(d, "#extension-persistence-status"))
    r.check("22 persistence restored",
            txt(d, "#extension-persistence-status")
            == "State restored after reload",
            txt(d, "#extension-persistence-status"))
    r.check("22 extension Enabled",
            txt(d, "#extension-enabled-state") == "Enabled",
            txt(d, "#extension-enabled-state"))
    r.check("22 calendar permission Allow",
            txt(d, "#site-calendar-permission") == "Allow",
            txt(d, "#site-calendar-permission"))
    r.check("22 drive permission Block",
            txt(d, "#site-drive-permission") == "Block",
            txt(d, "#site-drive-permission"))
    r.check("22 notify Off",
            txt(d, "#option-notify-state") == "Off",
            txt(d, "#option-notify-state"))
    r.check("22 auto-update Off",
            txt(d, "#option-auto-update-state") == "Off",
            txt(d, "#option-auto-update-state"))
    r.step("23 open options", "click",
           lambda: d.click("#btn-open-options"))
    r.check("23 options page visible", d.visible("#options-page"),
            "visible")
    r.step("24 reset defaults", "click",
           lambda: d.click("#btn-reset-defaults"))
    r.check("24 options save status defaults restored",
            txt(d, "#options-save-status") == "Defaults restored",
            txt(d, "#options-save-status"))
    r.check("25 extension Enabled",
            txt(d, "#extension-enabled-state") == "Enabled",
            txt(d, "#extension-enabled-state"))
    r.check("25 calendar permission Ask",
            txt(d, "#site-calendar-permission") == "Ask",
            txt(d, "#site-calendar-permission"))
    r.check("25 drive permission Ask",
            txt(d, "#site-drive-permission") == "Ask",
            txt(d, "#site-drive-permission"))
    r.check("25 notify On",
            txt(d, "#option-notify-state") == "On",
            txt(d, "#option-notify-state"))
    r.check("25 auto-update On",
            txt(d, "#option-auto-update-state") == "On",
            txt(d, "#option-auto-update-state"))
    r.step("26 reload settings", "click",
           lambda: _reload_settings(d, r, "26"))
    r.check("26 persistence restored",
            txt(d, "#extension-persistence-status")
            == "State restored after reload",
            txt(d, "#extension-persistence-status"))
    r.check("27 persistence restored",
            txt(d, "#extension-persistence-status")
            == "State restored after reload",
            txt(d, "#extension-persistence-status"))
    r.check("27 extension Enabled",
            txt(d, "#extension-enabled-state") == "Enabled",
            txt(d, "#extension-enabled-state"))
    r.check("27 calendar permission Ask",
            txt(d, "#site-calendar-permission") == "Ask",
            txt(d, "#site-calendar-permission"))
    r.check("27 drive permission Ask",
            txt(d, "#site-drive-permission") == "Ask",
            txt(d, "#site-drive-permission"))
    r.check("27 notify On",
            txt(d, "#option-notify-state") == "On",
            txt(d, "#option-notify-state"))
    r.check("27 auto-update On",
            txt(d, "#option-auto-update-state") == "On",
            txt(d, "#option-auto-update-state"))
    r.check("27 options save status defaults restored",
            txt(d, "#options-save-status") == "Defaults restored",
            txt(d, "#options-save-status"))
    final_verify(r, d, "10")


TESTS = {
    "01": run_01, "02": run_02, "03": run_03, "04": run_04,
    "05": run_05, "06": run_06, "07": run_07, "08": run_08,
    "09": run_09, "10": run_10,
}

FIXTURES = {
    "01": "test-01-git-workflow.html",
    "02": "test-02-music-player.html",
    "03": "test-03-password-vault.html",
    "04": "test-04-maps-directions.html",
    "05": "test-05-calendar-recurring.html",
    "06": "test-06-video-editor.html",
    "07": "test-07-chat-search.html",
    "08": "test-08-spreadsheet-pivot.html",
    "09": "test-09-file-search-tag.html",
    "10": "test-10-extension-settings.html",
}

# Frozen step-count audit table (redteam M4): the number of spec
# primitives (r.step + r.check calls while the audit is enabled)
# each driver must emit. Counted mechanically from the written
# drivers (grep r.step/r.check per run_NN) and verified against the
# spec step numbers (every spec step 2..N appears at least once per
# driver). A passing test with fewer primitives is a live failure:
# a driver that silently omits steps cannot pass.
STEP_COUNTS = {
    "01": 86, "02": 48, "03": 63, "04": 58, "05": 59,
    "06": 76, "07": 52, "08": 57, "09": 58, "10": 69,
}

# Per-test wall cap in seconds: each test's spec Maximum allowable
# latency. A pass over its cap is a live failure.
WALL_CAPS = {
    "01": 360, "02": 330, "03": 360, "04": 360, "05": 390,
    "06": 420, "07": 360, "08": 360, "09": 360, "10": 390,
}

# Ops counted by the step-count audit: the driver primitives only.
# Harness ops (goto, eval, verify, diagnose, intervention,
# gap-probe) are excluded, so open_fixture / guard / ladder records
# never count as spec steps.
AUDIT_OPS = {"click", "type", "wait", "select", "check", "text"}

# JSONL step names that are harness checks, never spec primitives.
# The body-visible gate in open_fixture logs op "check" while the
# audit is disabled, so it must be excluded here or every clean run
# counts one extra record (council B F1: jsonl_n = mem_n + 1).
_AUDIT_EXCLUDED_STEPS = {
    "check: body renders visible (no hidden-body incident)",
}


def _audit_count(tid, attempt):
    """Count JSONL primitive records for one test attempt."""
    n = 0
    try:
        with open(LOG_PATH) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                if (rec.get("test") == tid
                        and rec.get("attempt") == attempt
                        and rec.get("op") in AUDIT_OPS
                        and rec.get("step") not in _AUDIT_EXCLUDED_STEPS):
                    n += 1
    except Exception as exc:
        print(f"[audit] JSONL read failed for {tid} a{attempt}: {exc}",
              flush=True)
        return -1
    return n


# ---------------- server, bootstrap, preflight ----------------

def start_server():
    """Reuse a server already listening on our port, else start one.

    run_live.start_server only reuses when the clone1 fixture
    answers, so on this port it would try to bind 8771 twice and die
    with EADDRINUSE. Probe our own codex-y5 fixture first (Redteam
    A12: the copied agy-q2 probe is NOT reused verbatim)."""
    probe = (f"http://127.0.0.1:{SERVER_PORT}/{SUITE_DIR}/fixtures/"
             + FIRST_FIXTURE)
    try:
        with urllib.request.urlopen(probe, timeout=2) as resp:
            if resp.status == 200:
                print(f"reusing live server at http://127.0.0.1:{SERVER_PORT}",
                      flush=True)
                return None, f"http://127.0.0.1:{SERVER_PORT}"
    except Exception:
        pass
    try:
        return _rl_start_server()
    except OSError as exc:
        raise RuntimeError(
            f"could not start or reuse a server on port {SERVER_PORT} "
            f"(is a stale server holding the port with the wrong root?): {exc}"
        )


class BootstrapError(RuntimeError):
    """Bootstrap failed after all fresh-tab attempts. Carries the
    best-effort intervention info so main() can emit suite JSON."""

    def __init__(self, message, info):
        super().__init__(message)
        self.info = info


def bootstrap_tab(base):
    """Create ONE visible test tab, shared by all tests (DECIDED
    policy, Redteam A5): fresh-tab-only with bounded retries.

    Up to 3 fresh-tab attempts, each a new window/new tab plus the
    full ladder with allow_swap=False; a failed tab is closed and
    the next is tried. This differs from the Y4b reuse-first design
    DELIBERATELY: reuse-first requires scanning handles to find a
    visible fixture tab, which C2-F6 forbids, and Y8 also rejected
    the Y4 bootstrap (its evidence is n=1 confounded by time). The
    ladder's removal step deterministically fixes a tz-hidden tab,
    so a fresh tab opening hidden is recoverable, and the retries
    bound the residual risk.
    No handle scanning (C2 F6): pre-existing fixture tabs from
    earlier probes are NOT reused. The tab is kept out of
    opened_tabs so session cleanup never closes it (C1 R9), and
    registered in _TEST_TABS for the suite-end cleanup.
    Returns (handle, info) where info records any intervention on
    the shared tab (C2 F2: no intervention on the shared tab may be
    invisible). Raises BootstrapError after 3 failed attempts.
    """
    info = {"intervened": False, "tz_hidden_removed": False,
            "hidden_body_encounters": 0, "detail": "none",
            # Bootstrap ladder time (redteam diff F7): it is stall
            # time too, and main() folds it into the suite stall_ms.
            "stall_ms": 0}
    last_exc = None
    for attempt in range(1, 4):
        wd = Y13WD()
        h = None
        try:
            d = wd.__enter__()
        except Exception as exc:
            last_exc = exc
            print(f"bootstrap attempt {attempt}: session failed: {exc}",
                  flush=True)
            continue
        try:
            h = d.new_tab(base + f"/{SUITE_DIR}/fixtures/" + FIRST_FIXTURE,
                          allow_hidden=True)
            r = Y13Runner("bootstrap", base)
            r.tab = h
            ok, _swapped = ensure_visible(d, r, "new test tab",
                                          allow_swap=False)
            h = r.tab
            info["stall_ms"] = round(
                info["stall_ms"] + getattr(r, "stall_ms", 0), 1)
            if r.details.get("tz_hidden_removed"):
                info["tz_hidden_removed"] = True
                info["intervened"] = True
            info["hidden_body_encounters"] += r.details.get(
                "hidden_body_encounters", 0)
            if info["hidden_body_encounters"]:
                info["intervened"] = True
            if info["intervened"]:
                info["detail"] = (
                    f"attempt {attempt}: tz_hidden_removed="
                    f"{info['tz_hidden_removed']}, encounters="
                    f"{info['hidden_body_encounters']}")
                print(f"BOOTSTRAP INTERVENTION: {info}", flush=True)
            if not ok:
                raise RuntimeError(
                    "new test tab body hidden after recovery ladder")
            _TEST_TABS.add(h)
            if h in d.opened_tabs:
                d.opened_tabs.remove(h)
            print(f"created test tab {h[:8]} (attempt {attempt})",
                  flush=True)
            return h, info
        except Exception as exc:
            last_exc = exc
            print(f"bootstrap attempt {attempt} failed: {exc}", flush=True)
            try:
                d.close_tab()
            except Exception:
                pass
            if h is not None:
                _TEST_TABS.discard(h)
        finally:
            wd.__exit__()
    raise BootstrapError(
        f"INFRA: no visible test tab after 3 fresh-tab attempts: {last_exc}",
        info)


def _script_basename_is_runner(name):
    """True if a cmdline token's basename is a test-runner script
    (Y13f H2/H3). run_*.py covers Y9/Y13/Y14/Y4d; run-nested*
    covers Y6c's nested run (run-nested-pill.py, run-nested-wayland
    [.sh]: a hyphen, not run_, so the old run_ pattern was blind
    to it); hand_drive_e1.py is E1's driver."""
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
    bare-relative or wrapped launch is visible (Y13f H2). The -c
    argument itself is replaced by its words: the first word of a
    -c string is the command being run."""
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

    The old regex r"(^|/)run_[^/\\s]*\\.py" matched raw cmdline
    text and missed every bare-relative launch (the token sits
    after a NUL, not after "/" or string start) and every flock -c
    / shell -c form. It also false-positived on a mere path
    mention (md5sum /abs/run_foo.py). This version tokenizes argv
    and requires the script token to be argv[0] (shebang exec), to
    follow a python interpreter token (bare-relative, absolute,
    -u/-m flags, flock -c, shell -c), to be the first word of a -c
    string, or (for non-.py run-nested scripts only) to follow
    bash/sh. A path mention after md5sum/cat/git never matches.
    Keep in sync with launch_y13.py (identical logic) and with
    the note in the plan: Y14's run_batch3.py carries the same old
    pattern and must apply this same fix when it re-stages."""
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
# driving (or about to drive) a browser. A plain "codex" match with
# none of these is warning-only (a Codex CLI may be doing
# unrelated work). Keep in sync with launch_y13.py.
CODEX_REFUSE_MARKERS = ("hand_drive_e1", "geckodriver", ".config/zen",
                        "zen-bin", ".mozilla", "remote-debugging",
                        "marionette")


def preflight(base):
    """Fail-closed preflight (Y4b design). Raises RuntimeError on any
    failure; nothing proceeds to tab opening until it passes.

    Checks, in order: owner-away (explicit LIVE_OWNER_AWAY=1 AND a
    timestamped handover token, never inferred), Zen liveness (BiDi
    port 9222 + Marionette port 2828; the TCP connect proves the
    port listens, the session POST in WD.__enter__ is the real
    protocol probe), Hyprland IPC as a labeled SAFETY gate (not an
    incident detector), fixture server loopback, predecessor slot
    checks (Y9 server 8769 + WD 4449, Y8b server 8767 + WD 4451, Y4d
    server 8768 + WD 4448, and the 8770/4450 pair from Y14's gate
    range must be FREE; Y11b ports are not yet named by its plan, so the
    runner-quiet process check at launch time is the backstop for
    Y11b, and Y6c nested uses no TCP ports), stale-geckodriver sweep
    by PID file with parent check (kill only verified orphans),
    single-session lock check (zen_dom.lock must show an exclusive
    flock held by an ancestor of this process). Idle time is NOT
    independently verified (no reliable idle source on this machine);
    the handover token records the basis and timestamp instead.
    """
    ok, detail = _check_handover()
    if not ok:
        raise RuntimeError(f"PREFLIGHT: owner-away check failed: {detail}")
    print(f"PREFLIGHT: owner-away asserted ({detail}); idle time NOT "
          "independently verified", flush=True)
    # Zen liveness: the remote-debugging HTTP server on 9222 serves
    # its httpd.js root page (GET / -> 200). There is no /json/version
    # here: that is a Chrome DevTools path and 404s on Firefox/Zen.
    # The Marionette check below is a TCP connect only; the session
    # POST in WD.__enter__ is the real protocol probe.
    try:
        with urllib.request.urlopen("http://127.0.0.1:9222/",
                                    timeout=5) as resp:
            if resp.status != 200:
                raise RuntimeError("BiDi root endpoint not 200")
    except Exception as exc:
        raise RuntimeError(
            f"PREFLIGHT: Zen BiDi port 9222 unreachable: {exc}")
    try:
        s = socket.create_connection(("127.0.0.1", 2828), timeout=5)
        s.close()
    except Exception as exc:
        raise RuntimeError(
            f"PREFLIGHT: Marionette port 2828 unreachable: {exc}")
    # SAFETY gate (C3 F9): Hyprland IPC liveness. This is NOT an
    # incident detector (the IPC wedge is an unproven correlate for
    # the CSS value); it is a fail-closed safety gate: if the
    # compositor cannot answer, input/focus delivery is unverified
    # and driving is unsafe. Timeout-guarded, never a bare call.
    try:
        sig = _hyprland_signature()
        if not sig:
            raise RuntimeError("no Hyprland signature found")
        env = dict(os.environ)
        env["XDG_RUNTIME_DIR"] = "/run/user/1000"
        env["HYPRLAND_INSTANCE_SIGNATURE"] = sig
        subprocess.run(["hyprctl", "version"], env=env,
                       capture_output=True, timeout=10, check=True)
    except Exception as exc:
        raise RuntimeError(
            f"PREFLIGHT SAFETY: Hyprland IPC unresponsive: {exc}")
    try:
        with urllib.request.urlopen(
                base + f"/{SUITE_DIR}/fixtures/" + FIRST_FIXTURE,
                timeout=5) as resp:
            if resp.status != 200:
                raise RuntimeError("fixture probe not 200")
    except Exception as exc:
        raise RuntimeError(f"PREFLIGHT: fixture server check failed: {exc}")
    # Predecessor slot checks: Y9's server (8769) and driver (4449),
    # Y8b's server (8767) and driver (4451), Y4d's server (8768) and
    # driver (4448), and the 8770/4450 pair from Y14's gate range
    # must be FREE at launch. If any answers, that runner is still
    # alive and this run must not start.
    for port, who in ((8769, "Y9 server"), (4449, "Y9 geckodriver"),
                      (8767, "Y8b server"), (4451, "Y8b geckodriver"),
                      (8768, "Y4d server"), (4448, "Y4d geckodriver"),
                      (8770, "Y14-gate server"),
                      (4450, "Y14-gate geckodriver")):
        try:
            s = socket.create_connection(("127.0.0.1", port), timeout=2)
            s.close()
            raise RuntimeError(
                f"PREFLIGHT: {who} port {port} still answers; "
                "the live-driving slot is not free")
        except RuntimeError:
            raise
        except Exception:
            pass
    # Redteam H5: runner-quiet process check, in code, as defense
    # in depth behind the launcher's pre-flock check (launch_y13.py
    # does this before flock; preflight re-checks it after the lock
    # is held, in case a runner started in between). No run_*.py
    # process other than this process's own ancestry, and no
    # hand_drive_e1.py (E1's driver), may be running.
    _own = {os.getpid()}
    _pid = os.getpid()
    while _pid > 1:
        _ppid = _ppid_of(_pid)
        if _ppid is None or _ppid in _own:
            break
        _pid = _ppid
        _own.add(_pid)
    for _name in os.listdir("/proc"):
        if not _name.isdigit():
            continue
        _rpid = int(_name)
        if _rpid in _own:
            continue
        try:
            with open(f"/proc/{_rpid}/cmdline", "rb") as _f:
                _cmd = _f.read().decode("utf-8", "replace")
        except OSError:
            continue
        _flat = _cmd.replace(chr(0), " ").strip()
        if _is_runner_cmdline(_cmd):
            raise RuntimeError(
                f"PREFLIGHT: live slot busy, runner process running: "
                f"pid {_rpid}: {_flat}")
        # Y13f codex rule: a codex process driving a browser
        # refuses; a plain codex process only warns (see the
        # launcher, same rule). hand_drive_e1.py is already caught
        # above as a runner script.
        if "codex" in _cmd.lower() and any(
                m in _cmd.lower() for m in CODEX_REFUSE_MARKERS):
            raise RuntimeError(
                f"PREFLIGHT: live slot busy, codex executor driving "
                f"a browser: pid {_rpid}: {_flat}")
    for pid_path in glob.glob("/tmp/geckodriver-*.pid"):
        try:
            pid = int(Path(pid_path).read_text().strip())
        except Exception:
            print(f"preflight: unreadable PID file {pid_path}, "
                  "unlinking it", flush=True)
            try:
                os.unlink(pid_path)
            except Exception:
                pass
            continue
        try:
            os.kill(pid, 0)
            alive = True
        except (ProcessLookupError, PermissionError):
            alive = False
        if not alive:
            try:
                os.unlink(pid_path)
            except Exception:
                pass
            continue
        ppid = _ppid_of(pid)
        if ppid is None:
            # Unknown parentage: re-check liveness; if still alive,
            # REFUSE rather than kill a driver we cannot attribute
            # (C3 F3). Never kill on unknown parentage.
            try:
                os.kill(pid, 0)
                raise RuntimeError(
                    f"PREFLIGHT: geckodriver PID {pid} alive with "
                    "unreadable parent; refusing to kill or run")
            except ProcessLookupError:
                pass
            try:
                os.unlink(pid_path)
            except Exception:
                pass
            continue
        parent_alive = (ppid != 1 and os.path.exists(f"/proc/{ppid}"))
        if parent_alive:
            raise RuntimeError(
                f"PREFLIGHT: live geckodriver PID {pid} with live parent "
                f"{ppid}; another driver is active, refusing to run")
        # Re-verify the pid still names geckodriver BEFORE SIGTERM
        # too (Redteam re-review N11): the pid could have been
        # recycled between the liveness check and this kill.
        try:
            cmdline = Path(f"/proc/{pid}/cmdline").read_bytes()
        except Exception:
            cmdline = b""
        if b"geckodriver" not in cmdline:
            print(f"preflight: PID {pid} no longer geckodriver; "
                  "treating PID file as stale", flush=True)
            try:
                os.unlink(pid_path)
            except Exception:
                pass
            continue
        print(f"preflight: killing orphaned geckodriver PID {pid}",
              flush=True)
        try:
            os.kill(pid, 15)
            time.sleep(1)
            os.kill(pid, 0)
            # Re-verify the pid still names geckodriver before SIGKILL
            # (pid could have been recycled in that 1 s window).
            try:
                cmdline = Path(f"/proc/{pid}/cmdline").read_bytes()
            except Exception:
                cmdline = b""
            if b"geckodriver" not in cmdline:
                raise RuntimeError(
                    f"PREFLIGHT: PID {pid} no longer geckodriver; "
                    "refusing SIGKILL")
            os.kill(pid, 9)
        except ProcessLookupError:
            pass
        except Exception as exc:
            raise RuntimeError(
                f"PREFLIGHT: could not kill orphan {pid}: {exc}")
        try:
            os.unlink(pid_path)
        except Exception:
            pass
    lock_path = Path.home() / ".cache/agent-computer-use/zen_dom.lock"
    try:
        inode = lock_path.stat().st_ino
    except Exception as exc:
        raise RuntimeError(f"PREFLIGHT: lock file missing: {exc}")
    holders = []
    try:
        locks = Path("/proc/locks").read_text().splitlines()
    except Exception as exc:
        raise RuntimeError(f"PREFLIGHT: cannot read /proc/locks: {exc}")
    for line in locks:
        parts = line.split()
        # Lock type is POSIX (fcntl.lockf), FLOCK (flock(2)), or
        # OFDLCK. The launch holds the lock via flock(1), so the
        # entry is FLOCK; requiring POSIX alone fails every correct
        # launch (C3 F1, proven live).
        if (len(parts) < 6 or parts[1] not in ("POSIX", "FLOCK", "OFDLCK")
                or parts[3] != "WRITE"):
            continue
        try:
            ino = int(parts[5].rsplit(":", 1)[1])
        except (ValueError, IndexError):
            continue
        if ino == inode:
            holders.append(int(parts[4]))
    ancestors = {os.getpid()}
    pid = os.getpid()
    while pid > 1:
        ppid = _ppid_of(pid)
        if ppid is None or ppid in ancestors:
            break
        pid = ppid
        ancestors.add(pid)
    if not holders:
        raise RuntimeError("PREFLIGHT: no flock holder on zen_dom.lock; "
                           "run must be launched under flock")
    if not any(h in ancestors for h in holders):
        raise RuntimeError(
            f"PREFLIGHT: zen_dom.lock held by {holders}, not by an "
            "ancestor of this process")
    print("PREFLIGHT OK", flush=True)


def _copy_gecko_log(test_id, attempt):
    """Copy the geckodriver log to a per-test file, strictly before
    the next WD() starts (C1 R5). Logs copy success or failure;
    tolerates a missing log file (a failed __enter__ may leave
    none). Returns the destination path or None."""
    dest = Path(f"/tmp/worker-y13-gecko-{test_id}-a{attempt}.log")
    try:
        if not GECKO_LOG.exists():
            print(f"[gecko-log] no log to copy for {test_id} "
                  f"attempt {attempt} (missing, tolerated)", flush=True)
            return None
        dest.write_bytes(GECKO_LOG.read_bytes())
        print(f"[gecko-log] copied to {dest}", flush=True)
        return str(dest)
    except Exception as exc:
        print(f"[gecko-log] copy failed for {test_id} attempt {attempt}: "
              f"{exc}", flush=True)
        return None


def _read_shipped():
    """SHIPPED.md contents (file, md5, source commit), best effort.

    Lives in the suite dir (codex-y5/SHIPPED.md), NOT next to the
    runner: tests/realistic/SHIPPED.md already belongs to Y9's ship
    and must not be overwritten."""
    try:
        return (Path(__file__).parent / SUITE_DIR
                / "SHIPPED.md").read_text()
    except Exception:
        return None


def main():
    args = sys.argv[1:]
    if args == ["--verify-manifest"]:
        # Dry-run the manifest check without driving anything:
        # used by the laptop ship verification.
        ok, checked, bad, mmd5 = _verify_manifest()
        print(json.dumps({"manifest_ok": ok, "files_checked": checked,
                          "mismatches": bad, "manifest_md5": mmd5},
                         ensure_ascii=False), flush=True)
        return 0 if ok else 2
    selected = list(TESTS) if not args or args == ["all"] else args
    unknown = [a for a in selected if a not in TESTS]
    if unknown:
        print(f"unknown tests: {unknown}", file=sys.stderr)
        return 2
    _TOTAL_WD_CALLS["n"] = 0
    # Launch-time manifest check FIRST (Redteam re-review B3): the
    # shipped bytes must be the committed bytes, before any driving.
    manifest_ok, manifest_checked, manifest_bad, manifest_md5 = \
        _verify_manifest()
    if not manifest_ok:
        print(f"MANIFEST FAILED: {manifest_bad}", flush=True)
        print(json.dumps({"suite": "codex-y5", "manifest_failed": True,
                          "mismatches": manifest_bad,
                          "total": len(selected)}, ensure_ascii=False),
              flush=True)
        return 2
    print(f"MANIFEST OK ({manifest_checked} files, "
          f"manifest md5 {manifest_md5})", flush=True)
    # Rotate the JSONL at launch (Redteam A11): one file holds
    # exactly one run; the previous run is kept with a timestamp.
    if LOG_PATH.exists():
        prev = LOG_PATH.with_name(
            LOG_PATH.name + ".prev-"
            + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
        try:
            LOG_PATH.rename(prev)
            print(f"rotated previous JSONL to {prev}", flush=True)
        except Exception as exc:
            # Refuse, do not fail open (C3 re-review F9b): appending
            # into a stale log would mix two runs in one file.
            print(f"JSONL rotation failed, refusing to run: {exc}",
                  flush=True)
            print(json.dumps({"suite": "codex-y5",
                              "jsonl_rotation_failed": True,
                              "error": f"{type(exc).__name__}: {exc}",
                              "total": len(selected)}, ensure_ascii=False),
                  flush=True)
            return 2
    suite_t0 = time.perf_counter()
    # Redteam M7: a start_server failure used to escape main as an
    # uncaught traceback with no suite JSON. Wrap it in the same
    # structured-failure pattern as preflight.
    try:
        _, base = start_server()
    except Exception as exc:
        print(f"SERVER FAILED {type(exc).__name__}: {exc}", flush=True)
        print(json.dumps({"suite": "codex-y5", "server_failed": True,
                          "error": f"{type(exc).__name__}: {exc}",
                          "passed": 0, "flagged": 0, "failed": 0,
                          "hidden_body_encounters": 0,
                          "bootstrap_intervention": None, "gaps": [],
                          "total": len(selected)}, ensure_ascii=False),
              flush=True)
        return 2
    print(f"serving at {base}", flush=True)
    # Prove the server serves the manifest bytes (redteam diff F3):
    # the reuse probe only checks a 200, never the served root.
    served_ok, served_checked, served_bad = _verify_served_files(base)
    if not served_ok:
        print(f"SERVED FILES FAILED: {served_bad}", flush=True)
        print(json.dumps({"suite": "codex-y5",
                          "served_files_failed": True,
                          "mismatches": served_bad,
                          "total": len(selected)}, ensure_ascii=False),
              flush=True)
        return 2
    print(f"SERVED FILES OK ({served_checked} files over HTTP)",
          flush=True)
    try:
        preflight(base)
    except Exception as exc:
        print(f"PREFLIGHT FAILED {type(exc).__name__}: {exc}", flush=True)
        print(json.dumps({"suite": "codex-y5", "preflight_failed": True,
                          "error": f"{type(exc).__name__}: {exc}",
                          "passed": 0, "flagged": 0, "failed": 0,
                          "hidden_body_encounters": 0,
                          "bootstrap_intervention": None, "gaps": [],
                          "total": len(selected)}, ensure_ascii=False),
              flush=True)
        return 2
    # Pre-suite live-eval smoke test (C3 G4): the ported verify AND
    # diagnose_body must return well-formed values on a live fixture
    # before test 01 runs. This is the exact lesson from Y4d's
    # _DIAG_JS bug (a broken eval helper survived council review).
    # Only well-formedness is required here (a VISIBLE diagnosis is
    # NOT required: the ladder handles a hidden body at open_fixture).
    try:
        with Y13WD() as d:
            h = d.new_tab(base + f"/{SUITE_DIR}/fixtures/"
                          + FIRST_FIXTURE, allow_hidden=True)
            _TEST_TABS.add(h)
            if h in d.opened_tabs:
                d.opened_tabs.remove(h)
            diag = diagnose_body(d)
            if not isinstance(diag, dict) \
                    or "classification" not in diag:
                raise RuntimeError(
                    f"smoke: diagnose_body returned non-dict: {diag!r}")
            res = verify_test(d, "01")
            if not isinstance(res, dict) or "passed" not in res:
                raise RuntimeError(
                    f"smoke: ported verify returned non-dict: {res!r}")
            print(f"SMOKE OK: diagnose {diag['classification']}, "
                  f"ported verify returned dict "
                  f"(passed_on_untouched={res['passed']})", flush=True)
    except Exception as exc:
        print(f"SMOKE FAILED {type(exc).__name__}: {exc}", flush=True)
        print(json.dumps({"suite": "codex-y5", "smoke_failed": True,
                          "error": f"{type(exc).__name__}: {exc}",
                          "total": len(selected)}, ensure_ascii=False),
              flush=True)
        return 2
    try:
        tab, boot_info = bootstrap_tab(base)
    except BootstrapError as exc:
        print(f"BOOTSTRAP FAILED {type(exc).__name__}: {exc}", flush=True)
        print(json.dumps({"suite": "codex-y5", "bootstrap_failed": True,
                          "error": str(exc),
                          "bootstrap_intervention": exc.info,
                          "hidden_body_encounters": exc.info.get(
                              "hidden_body_encounters", 0),
                          "total": len(selected)}, ensure_ascii=False),
              flush=True)
        return 2
    bootstrap_tabs = [tab]
    results = []
    wd_failures = 0
    infra_blocked = 0
    aborted_handover = False
    stall_ms = 0
    # Cross-attempt evidence (C3 re-review F3): hidden-body
    # encounters and verified removals on a SUPERSEDED attempt 1
    # must survive in the suite total, not vanish with the summary.
    superseded = []
    hidden_encounters_all = 0
    tz_removed_any = False
    # Redteam M2: cumulative wall time per test across attempts
    # (ms). Attempt 2 does not get a fresh cap budget.
    cum_ms = {}
    for tid in selected:
        ok, detail = _check_handover()
        if not ok:
            print(f"HANDOVER EXPIRED before {tid}: {detail}; aborting run",
                  flush=True)
            aborted_handover = True
            break
        summary = None
        for attempt in (1, 2):
            _CURRENT_ATTEMPT["n"] = attempt
            # Council A F10: re-check the handover before EVERY
            # attempt, not only before each test. The token can
            # expire between attempt 1 and attempt 2; a re-run must
            # never drive without a live handover.
            ok, detail = _check_handover()
            if not ok:
                print(f"HANDOVER EXPIRED before {tid} attempt "
                      f"{attempt}: {detail}; aborting run", flush=True)
                aborted_handover = True
                break
            r = Y13Runner(tid, base)
            r.attempt = attempt
            attempt_t0 = r.t0
            if tid in cum_ms:
                # Redteam M2: offset t0 so the per-primitive
                # deadline check and the post-hoc cap check measure
                # CUMULATIVE time across attempts, not a fresh
                # budget per attempt. attempt_t0 (kept above) is
                # the un-offset start for the per-attempt elapsed.
                r.t0 = time.perf_counter() - cum_ms[tid] / 1000.0
            r.tab = tab
            try:
                wd = Y13WD()
                d = wd.__enter__()
            except Exception as exc:
                # Only a failure to CREATE the session counts toward
                # the abort threshold. A step failure inside a test
                # contains "/session/<id>/..." in its URL and must
                # never count here (that bug aborted the first Y4
                # run after 2 tests).
                r.failures.append(f"session: {type(exc).__name__}: {exc}")
                print(f"[{tid}] SESSION ERROR {type(exc).__name__}: {exc}",
                      flush=True)
                wd_failures += 1
                infra_blocked = 0
                _copy_gecko_log(tid, attempt)
                s = r.summary()
                s["flagged"] = False
                s["outcome"] = "session-creation-failure"
                s["reattempted_from_infra"] = False
                # Y13f L4: the cumulative key is new in cb26d1d and
                # appears on every normal per-test summary; a
                # session-failure summary without it breaks a
                # downstream parser expecting the key on every
                # per-test summary. No attempt 2 follows a session
                # failure, so this attempt's elapsed IS the
                # cumulative value (cum_ms is NOT updated here).
                s["cumulative_elapsed_ms"] = round(
                    (time.perf_counter() - attempt_t0) * 1000, 1)
                results.append(s)
                print(json.dumps(s, ensure_ascii=False), flush=True)
                if wd_failures >= 2:
                    print("two consecutive session-creation failures, "
                          "aborting run", flush=True)
                    summary = s
                    break
                summary = s
                break
            wd_failures = 0
            outcome = "pass"
            raised_infra = False
            guard_defect = False
            guard_inconclusive = False
            try:
                TESTS[tid](r, d)
            except IntegrityGuardError as exc:
                # Suite defect, not infra: no effect on the abort
                # counter, no re-run, suite continues (C2 F7 / C3 F6).
                guard_defect = True
                outcome = "guard-defect"
                r.failures.append(f"{type(exc).__name__}: {exc}")
                print(f"[{tid}] INTEGRITY GUARD: {exc}", flush=True)
            except GuardInconclusiveError as exc:
                # Guard eval error/timeout: FAIL the test as
                # guard-inconclusive; suite continues; NEVER proceed
                # to drive (C3 G1). No effect on infra_blocked.
                guard_inconclusive = True
                outcome = "guard-inconclusive"
                r.failures.append(f"{type(exc).__name__}: {exc}")
                print(f"[{tid}] GUARD INCONCLUSIVE: {exc}", flush=True)
            except Exception as exc:
                # Y13f F8: build msg WITH the type name, so the
                # TimeoutError/URLError clauses below match bare
                # raises too (str(exc) alone omits the type name,
                # which made those clauses dead outside r.step).
                msg = f"{type(exc).__name__}: {exc}"
                if isinstance(exc, WallCapExceeded):
                    # Y13f M1: a wall-cap trip is a live failure by
                    # construction (no WD call is outstanding
                    # between primitives). Classify it BEFORE the
                    # diagnose block: never diagnose-reclassify to
                    # INFRA, never spend a re-run slot on it
                    # (attempt 2 would trip instantly on
                    # cumulative time).
                    outcome = "failed"
                    r.failures.append(f"wall cap exceeded: {exc}")
                    print(f"[{tid}] WALL CAP EXCEEDED (primitive "
                          f"trip): {exc}", flush=True)
                elif isinstance(exc, InfraError):
                    # Y13f L1: marker class, classified on the type.
                    raised_infra = True
                    outcome = "infra-blocked"
                elif isinstance(exc, FixtureUnavailableError):
                    outcome = "fixture-unavailable"
                    r.failures.append(
                        f"fixture unavailable: {exc}")
                    print(f"[{tid}] FIXTURE-UNAVAILABLE: {exc}",
                          flush=True)
                elif msg.startswith("INFRA:") or ": INFRA:" in msg:
                    # Defense in depth for INFRA raises that arrive
                    # wrapped or as a plain RuntimeError (e.g. from
                    # the frozen base): the marker-class branch
                    # above is the primary path.
                    raised_infra = True
                    outcome = "infra-blocked"
                elif (msg.startswith("FIXTURE-UNAVAILABLE")
                        or ": FIXTURE-UNAVAILABLE" in msg):
                    # Redteam M3: match the substring too, like
                    # ": INFRA:": a FIXTURE-UNAVAILABLE raised inside
                    # an r.step lambda is wrapped as "step failed:
                    # ...: RuntimeError: FIXTURE-UNAVAILABLE: ...",
                    # which the startswith check alone misses.
                    # Own outcome (C1 re-review F4): a fixture that
                    # never renders a body is not a live test
                    # failure. Suite continues, no infra count,
                    # no re-run.
                    outcome = "fixture-unavailable"
                    r.failures.append(
                        f"fixture unavailable: {exc}")
                    print(f"[{tid}] FIXTURE-UNAVAILABLE: {exc}",
                          flush=True)
                else:
                    # Mid-test hidden-body rule (Redteam A10),
                    # narrowed (C3 re-review F4): only a PROVEN
                    # hidden body (TZ_STUCK_V1 / OTHER_HIDDEN) may
                    # reclassify to INFRA and earn a re-run.
                    # UNKNOWN stays a live failure (no re-run, no
                    # infra count). FIXTURE_FAILURE splits (redteam
                    # H4): a positively proven no-body document is
                    # fixture-unavailable; a diagnose transport
                    # error is INFRA.
                    diag = {}
                    try:
                        diag = diagnose_body(d)
                        cls = diag["classification"]
                    except Exception:
                        cls = "UNKNOWN"
                    if cls in ("TZ_STUCK_V1", "OTHER_HIDDEN"):
                        raised_infra = True
                        outcome = "infra-blocked"
                        r.failures.append(
                            f"reclassified INFRA: hidden-body mid-test "
                            f"({cls}) after step failure: {exc}")
                        print(f"[{tid}] MID-TEST HIDDEN BODY ({cls}); "
                              "reclassified INFRA", flush=True)
                    elif cls == "FIXTURE_FAILURE":
                        if _proven_no_body(diag):
                            outcome = "fixture-unavailable"
                            r.failures.append(
                                f"fixture unavailable mid-test "
                                f"({cls}) after step failure: {exc}")
                            print(f"[{tid}] FIXTURE-UNAVAILABLE mid-test "
                                  f"({cls})", flush=True)
                        else:
                            raised_infra = True
                            outcome = "infra-blocked"
                            r.failures.append(
                                f"reclassified INFRA: diagnose "
                                f"transport error, not a proven "
                                f"no-body fixture "
                                f"({diag.get('eval_error', 'no snapshots')}) "
                                f"after step failure: {exc}")
                            print(f"[{tid}] DIAGNOSE TRANSPORT ERROR; "
                                  f"reclassified INFRA", flush=True)
                    elif (("timed out" in msg.lower()
                           or "TimeoutError" in msg
                           or "URLError" in msg)
                            and "timeout waiting for" not in msg):
                        # Council A F8: match ONLY the pinned
                        # wording ("timed out", TimeoutError,
                        # URLError), not any "timeout" substring:
                        # a fixture-side message mentioning timeout
                        # must not be reclassified as INFRA.
                        # A WD HTTP timeout is INFRA (driver or
                        # browser hung) unless evidence shows a
                        # fixture cause. Evidence recorded: the
                        # exception type + message, and the fact the
                        # diagnose just answered VISIBLE, so the
                        # driver is alive but the step call hung.
                        # A wait_for timeout ("timeout waiting for
                        # ...") is a live failure. (C1 re-review F5:
                        # a genuine urlopen timeout surfaces as
                        # "timed out", which contains no "timeout"
                        # substring on its own.)
                        raised_infra = True
                        outcome = "infra-blocked"
                        r.failures.append(
                            f"reclassified INFRA: WD timeout "
                            f"({type(exc).__name__}: {exc}; diagnose "
                            f"answered {cls})")
                        print(f"[{tid}] WD TIMEOUT; reclassified INFRA",
                              flush=True)
                    else:
                        outcome = "failed"
                        r.failures.append(
                            f"runner: {type(exc).__name__}: {exc}")
                        print(f"[{tid}] RUNNER ERROR "
                              f"{type(exc).__name__}: {exc}", flush=True)
            finally:
                # End-state screenshot while the session is alive.
                # Switch to a known test tab first (Redteam re-review
                # B2): after a rebootstrap failure the current window
                # is uncontrolled, and the screenshot must never
                # capture a user tab as test evidence. If the switch
                # fails, SKIP the screenshot (council diff fix 2a)
                # instead of capturing an uncontrolled window.
                shot = None
                try:
                    if r.tab in d.handles():
                        d.switch(r.tab)
                    else:
                        h = d.new_tab("about:blank", allow_hidden=True)
                        d.opened_tabs.remove(h)
                        _TEST_TABS.add(h)
                    shot = d.screenshot(
                        str(SHOTS_DIR / f"{tid}-a{attempt}.png"))
                except Exception as exc:
                    print(f"[{tid}] pre-screenshot step failed; "
                          f"skipping screenshot: {exc}", flush=True)
                    shot = None
                if shot:
                    r.details["end_state_screenshot"] = shot
                wd.__exit__()
                _copy_gecko_log(tid, attempt)
            if raised_infra:
                _recheck_shared_tab(r, tab)
                infra_blocked += 1
            elif guard_defect or guard_inconclusive:
                pass  # no effect on the abort counter
            elif outcome == "fixture-unavailable":
                pass  # suite/fixture defect, not infra: no effect
            else:
                infra_blocked = 0
            # Redteam M4: a test whose checks failed still had
            # outcome "pass" (r.check failures do not raise, they
            # append to r.failures). Set the outcome here, before
            # the audit block, so the per-test JSON tells the truth.
            if outcome == "pass" and r.failures:
                outcome = "failed"
            # Wall-cap + step-count audit (Y13 v2, C3 V1 / RT M4):
            # only when the test would otherwise pass. A pass over
            # its spec max latency, or with fewer driven primitives
            # than the frozen table, is a live failure, never a
            # pass. The JSONL count and the in-memory counter must
            # agree; disagreement is itself an audit failure.
            if outcome == "pass" and not r.failures:
                elapsed_ms = (time.perf_counter() - r.t0) * 1000
                if elapsed_ms > WALL_CAPS[tid] * 1000:
                    outcome = "failed"
                    r.failures.append(
                        f"wall cap exceeded: {elapsed_ms:.0f}ms > "
                        f"{WALL_CAPS[tid] * 1000}ms")
                    print(f"[{tid}] WALL CAP EXCEEDED: "
                          f"{elapsed_ms:.0f}ms > "
                          f"{WALL_CAPS[tid] * 1000}ms", flush=True)
                else:
                    jsonl_n = _audit_count(tid, attempt)
                    mem_n = r.spec_step_count
                    if (jsonl_n != STEP_COUNTS[tid]
                            or mem_n != STEP_COUNTS[tid]):
                        outcome = "failed"
                        r.failures.append(
                            f"step-count audit: drove {mem_n} "
                            f"primitives (JSONL {jsonl_n}), want "
                            f"{STEP_COUNTS[tid]}")
                        print(f"[{tid}] STEP-COUNT AUDIT FAILED: "
                              f"memory {mem_n}, JSONL {jsonl_n}, want "
                              f"{STEP_COUNTS[tid]}", flush=True)
                    else:
                        print(f"[{tid}] wall cap + step-count audit OK "
                              f"({elapsed_ms:.0f}ms <= "
                              f"{WALL_CAPS[tid] * 1000}ms, "
                              f"{mem_n} primitives)", flush=True)
            summary = r.summary()
            summary["flagged"] = bool(r.details.get("tz_hidden_removed"))
            summary["outcome"] = outcome
            summary["reattempted_from_infra"] = (attempt == 2)
            # Redteam M2: cumulative wall accounting. The cap checks
            # (per-primitive + post-hoc) measure cumulative time via
            # the offset t0; the summary keeps elapsed_ms as THIS
            # attempt only (plan C3 F1: total_ms sums final attempts
            # only) and records the cumulative separately, so a
            # superseded attempt's time is visible per test.
            attempt_elapsed_ms = (time.perf_counter() - attempt_t0) * 1000
            cum_ms[tid] = cum_ms.get(tid, 0) + attempt_elapsed_ms
            summary["elapsed_ms"] = round(attempt_elapsed_ms, 1)
            summary["cumulative_elapsed_ms"] = round(cum_ms[tid], 1)
            # Ladder time only (C1 re-review F6 / C3 re-review F2),
            # accumulated across attempts, including recovered and
            # flagged tests. Cross-attempt hidden-body evidence
            # (C3 re-review F3).
            stall_ms += getattr(r, "stall_ms", 0)
            hidden_encounters_all += r.details.get(
                "hidden_body_encounters", 0)
            if r.details.get("tz_hidden_removed"):
                tz_removed_any = True
            if r.tab not in bootstrap_tabs:
                bootstrap_tabs.append(r.tab)
                tab = r.tab
            if outcome == "infra-blocked" and attempt == 1:
                # ONE re-run for a proven infra-blocked test,
                # immediately after the failed attempt. The first
                # INFRA still counts toward infra_blocked; a
                # successful re-run resets it (pass rule). The
                # superseded attempt-1 summary is printed before
                # re-running (C1 re-review F7 / C3 re-review F6),
                # so the INFRA failure text exists as a per-test
                # JSON summary and not only as JSONL step records.
                superseded.append(summary)
                print(json.dumps({**summary, "superseded": True},
                                 ensure_ascii=False), flush=True)
                print(f"[{tid}] infra-blocked on attempt 1; "
                      "re-running once", flush=True)
                continue
            results.append(summary)
            print(json.dumps(summary, ensure_ascii=False), flush=True)
            if raised_infra and infra_blocked >= 2:
                print("two consecutive INFRA-blocked tests, aborting run",
                      flush=True)
                break
            break
        if aborted_handover:
            break
        if summary is not None and summary.get("outcome") == \
                "session-creation-failure" and wd_failures >= 2:
            break
        if infra_blocked >= 2:
            break
    passed = sum(1 for s in results if s["pass"] and not s.get("flagged"))
    flagged = sum(1 for s in results if s["pass"] and s.get("flagged"))
    total_passed = passed + flagged
    # Cross-attempt total (C3 re-review F3): appended summaries plus
    # superseded attempt-1 encounters plus bootstrap encounters.
    hidden_encounters = hidden_encounters_all + boot_info.get(
        "hidden_body_encounters", 0)
    all_gaps = [g for s in results for g in s.get("gaps", [])]
    total_ms = sum(s["elapsed_ms"] for s in results)
    marker = (f"Y13 codex-y5 live complete: {passed} clean, {flagged} "
              f"flagged, {total_passed}/{len(results)} passed")
    suite = {"suite": "codex-y5", "passed": passed,
             "flagged": flagged, "total_passed": total_passed,
             "failed": len(results) - total_passed,
             # Separate count (redteam diff F4): a fixture-unavailable
             # outcome still counts in "failed" (the test did not
             # pass) and still exits 1, but it must be visible
             # separately, not conflated with live failures. The
             # infra streak is deliberately NOT reset by it (fail
             # safe, consistent with the guard-defect precedent).
             "fixture_unavailable": sum(
                 1 for s in results
                 if s.get("outcome") == "fixture-unavailable"),
             "guard_defect": sum(
                 1 for s in results
                 if s.get("outcome") == "guard-defect"),
             "guard_inconclusive": sum(
                 1 for s in results
                 if s.get("outcome") == "guard-inconclusive"),
             "total": len(results), "selected": len(selected),
             "total_ms": total_ms,
             "suite_wall_ms": round(
                 (time.perf_counter() - suite_t0) * 1000),
             "hidden_body_encounters": hidden_encounters,
             "tz_hidden_removed_any_attempt": tz_removed_any,
             "park_warnings": list(_PARK_WARNINGS),
             "superseded_attempts": superseded,
             "bootstrap_intervention": boot_info,
             "gaps": all_gaps,
             "tracked_item": TRACKED_ITEM,
             "manifest": {"file": MANIFEST_NAME, "md5": manifest_md5,
                          "files_checked": manifest_checked},
             "step_counts": STEP_COUNTS,
             "wall_caps_s": WALL_CAPS,
             "completion_marker": marker,
             "metrics": {"wall_ms": total_ms,
                         "marionette_calls": _TOTAL_WD_CALLS["n"],
                         "marionette_calls_scope":
                             "all Y13WD sessions before suite JSON "
                             "(bootstrap, test attempts, rechecks; "
                             "suite-end cleanup excluded)",
                         "tokens": "UNMEASURED",
                         "observation_cost": "UNMEASURED",
                         "vcr": False,
                         "stall_ms": round(
                             stall_ms + boot_info.get("stall_ms", 0),
                             1)},
             "md5": {"run_live.py": _md5_of(
                         Path(__file__).with_name("run_live.py")),
                     "run_codex_y5.py": _md5_of(__file__)},
             "shipped": _read_shipped()}
    print(json.dumps(suite, ensure_ascii=False), flush=True)
    # "passed" counts CLEAN passes only (C2 F3). A flagged pass is a
    # test that drove successfully only after the tz-hidden removal,
    # and it must never read as clean green.
    if flagged > 0 or boot_info.get("tz_hidden_removed"):
        print(f"SUITE FLAGGED: {flagged} flagged passes"
              + (" + bootstrap intervention" if boot_info.get(
                  "tz_hidden_removed") else "")
              + f"; browser unhealthy; see {TRACKED_ITEM}", flush=True)
    print(marker, flush=True)
    # Leave every shared test tab clean (about:blank) for the next runner.
    # Y13f L3: skip the cleanup entirely when the handover aborted.
    # The gate closed (the owner may be back), and driving the shared
    # browser to switch tabs after that is exactly what F10 forbids.
    # The partial suite JSON above already printed.
    if not aborted_handover:
        try:
            with Y13WD() as d:
                try:
                    d.switch(tab)
                    d.screenshot(str(SHOTS_DIR / "suite-end.png"))
                except Exception:
                    pass
                for t in set(bootstrap_tabs) | _TEST_TABS:
                    try:
                        d.switch(t)
                        d.goto("about:blank", allow_hidden=True)
                    except Exception as exc:
                        print(f"tab cleanup failed for {t[:8]} (harmless): {exc}",
                              flush=True)
                print("test tabs returned to about:blank", flush=True)
        except Exception as exc:
            print(f"tab cleanup failed (harmless): {exc}", flush=True)
    if aborted_handover:
        return 2
    return 0 if total_passed == len(results) and \
        len(results) == len(selected) else 1


if __name__ == "__main__":
    sys.exit(main())
