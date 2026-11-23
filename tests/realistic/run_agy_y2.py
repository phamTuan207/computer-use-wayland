#!/usr/bin/env python3
"""Live Zen runner: agy-y2 test-01..10 (Worker Y9, 21/11/2026).

Runs tests/realistic/agy-y2/test-01..10 against the LIVE Zen on the
laptop via geckodriver --connect-existing (Marionette 2828), reusing
the proven driver from tests/realistic/run_live.py (Worker P) and the
harness pattern from tests/realistic/run_agyq2.py (Worker Y4).

LINEAGE AND FROZEN BASE. This file is self-contained except for the
run_live import (WD, Runner, diagnose_body, log_step, start_server).
The harness functions (ensure_visible, rebootstrap_tab,
bootstrap_tab, open_fixture, preflight) are COPIES of run_agyq2.py
adapted to agy-y2 paths and Y9 ports, with every Y4d council fix
implemented in the shipped bytes (see the fix table in the v2 plan,
improvements/worker-y9-agy-y2-live-plan.md). The shipped run_live.py
already contains the Council-1 diagnose fixes (second-sample eval
error keeps the snap1 classification; refresh() diagnoses like
goto()) and the C3-F4/F5/F6 orphan hardening (append-mode geckodriver
log, PID write and session POST inside try with cleanup, exception
proof terminate), verified by reading the shipped bytes. FROZEN BASE:
run_live.py is shipped ONLY from commit 1e3901c (md5
84fa106c253d5e7f16daccf2ce3f14a5), the Y4d live-proven base (10/10
twice). It is deliberately NOT taken from HEAD: HEAD's run_live.py
changed in 91d3cd2 (Y11 live-metrics wiring, +415/-66), which is
not live-proven, and the runner was written and reviewed against
the 1e3901c API. The runner refuses to launch unless every shipped
file matches agy-y2-manifest.json (launch-time manifest check,
Redteam re-review B3). The frozen ship is recorded in SHIPPED.md
next to this file; later VM edits do not affect the run.

RULES (from the v2 plan, all enforced in code below):
- One fresh WebDriver session per test, always deleted in finally.
  Sessions exit parked on a sacrificial about:blank tab (Y9WD park):
  DELETE /session closes the throwaway, never a keeper test tab and
  never a user tab (Redteam re-review B2). The shared test tab
  therefore survives session exit; if the live run still prints
  "shared tab gone, rebootstrap", that itself is a finding.
- ONE shared test tab for the whole suite (bootstrap_tab, fresh
  tab only, up to 3 attempts). No handle scanning: only REGISTERED
  handles are ever switched to. User tabs are never navigated,
  typed into, or clicked.
- End states verified by reading the DOM directly through a 1:1
  port of check.mjs verifyTest (JS executed via Marionette eval).
  The fixtures' verify hooks are NEVER used as oracles (none exist
  in this suite). The integrity guard runs the SAME ported verify on
  the untouched fixture before steps; a pass there is a suite
  defect, never a pass.
- FLAGGED: a pass only after the tz-hidden removal ran AND the
  post-remove snapshot proves the class is gone. Clean headline
  counts clean only. Exit 0 iff clean + flagged == total.
- ABORT: infra_blocked counts hidden-body-unrecoverable only;
  session-creation failures use the separate wd_failures counter
  (own two-consecutive abort). infra_blocked resets on any pass, on
  any non-INFRA failure. A 30 s WD HTTP timeout is INFRA; a
  wait_for timeout is a live failure.
- A re-run is allowed ONLY for a test proven infra-blocked, max ONE
  per test, immediately after the failed attempt, logged with the
  attempt field. A hidden body found mid-test (on any step failure)
  is INFRA, not a step failure.
- test-10 spec step 15 is SKIPPED (fixture gap: input display:none,
  no handler, simulator also skips it), never counted as driven.
- test-01 typing is scoped to the ACTIVE pane (element-from-element
  search inside the pane holding #pane-active-output).

Usage (on the laptop, from /tmp/worker-y9-server):
  cd /tmp/worker-y9-server && LIVE_SERVER_ROOT=/tmp/worker-y9-server \\
  LIVE_SERVER_PORT=8769 LIVE_LOG=/tmp/worker-y9-live.jsonl WD_PORT=4449 \\
  LIVE_OWNER_AWAY=1 flock -w 60 ~/.cache/agent-computer-use/zen_dom.lock \\
  -c "python3 run_agy_y2.py all > /tmp/worker-y9-stdout.log 2>&1"
  python3 run_agy_y2.py 01 02
Output: one JSON summary line per test on stdout, a suite JSON line,
per-step JSONL at LIVE_LOG (with attempt fields), per-test
screenshots in /tmp/worker-y9-shots/.
"""
import base64
import glob
import hashlib
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_live import (  # noqa: E402
    EL_KEY, WD, Runner, diagnose_body,
    start_server as _rl_start_server,
)

# Env-driven ports (read by run_live at import; the launcher sets
# them): LIVE_SERVER_PORT 8769, WD_PORT 4449, MARIONETTE_PORT 2828.
SERVER_PORT = int(os.environ.get("LIVE_SERVER_PORT", "8769"))
WD_PORT = int(os.environ.get("WD_PORT", "4449"))
LOG_PATH = Path(os.environ.get("LIVE_LOG", "/tmp/worker-y9-live.jsonl"))
SHOTS_DIR = Path("/tmp/worker-y9-shots")
GECKO_LOG = Path(f"/tmp/geckodriver-{WD_PORT}.log")
SUITE_DIR = "agy-y2"
FIRST_FIXTURE = "test-01-tmux-session.html"

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
HANDOVER_FILE = Path("/tmp/worker-y9-handover.json")
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

# Marionette calls across ALL Y9WD sessions in this process
# (bootstrap, test attempts, rechecks; the suite-end cleanup session
# runs after the suite JSON is printed, so it is excluded). This is
# the six-metrics marionette_calls value (C3 re-review F7).
_TOTAL_WD_CALLS = {"n": 0}

# Launch-time manifest (Redteam re-review B3): expected md5s for
# every shipped file, generated mechanically from the committed
# bytes. The runner refuses to run on any mismatch.
MANIFEST_NAME = "agy-y2-manifest.json"

# Pinned manifest size (redteam diff F2): the suite ships exactly
# this many files; a manifest listing fewer would silently skip
# checks. Update together with the manifest when the suite grows.
EXPECTED_MANIFEST_FILES = 26


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
        tok = json.loads(HANDOVER_FILE.read_text())
    except Exception as exc:
        return False, f"handover file unreadable: {exc}"
    try:
        age = time.time() - float(tok["asserted_at_unix"])
    except Exception:
        return False, "handover file has no valid asserted_at_unix"
    if age < 0 or age > HANDOVER_MAX_AGE_S:
        return False, (f"handover token age {age:.0f}s outside "
                       f"0-{HANDOVER_MAX_AGE_S}s window")
    try:
        st = HANDOVER_FILE.stat()
        fp = (float(tok["asserted_at_unix"]), st.st_mtime_ns, st.st_size)
    except Exception:
        return False, "handover file has no statable fingerprint"
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
    guards applied once and shared by both checks (redteam diff2
    B1).

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
    manifest check (Redteam re-review B3).

    Every shipped file's md5 must match the manifest generated from
    the committed bytes. The manifest itself is a repo file; its own
    md5 is recorded in the suite JSON, not self-checked. Refuse the
    run on any mismatch: a stale or edited fixture must never run
    silently and pass, since the integrity guard only proves the
    verify FAILS on untouched bytes."""
    mpath = Path(__file__).with_name(MANIFEST_NAME)
    entries, err = _manifest_entries()
    if err is not None:
        return False, 0, [err], _md5_of(mpath)
    base_dir = Path(__file__).resolve().parent
    bad = []
    checked = 0
    for rel, want in entries:
        got = _md5_of(base_dir / rel)
        checked += 1
        if got != want:
            bad.append(f"{rel}: want {want}, got {got}")
    return (not bad), checked, bad, _md5_of(mpath)


def _verify_served_files(base):
    """(ok, checked, mismatches) proving the HTTP server serves the
    manifest bytes (redteam diff F3). The reuse path in start_server
    probes only test-01 with a 200 check, which never proves the
    served root; a stale server on the port could serve old fixture
    bytes while the disk manifest passes. Fetch every manifest file
    over HTTP and compare md5s. The entry list comes from the same
    _manifest_entries() helper as the disk check (redteam diff2
    B1), so a duplicated or escaping entry cannot pass here while
    failing there."""
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


def _child_in(d, parent_css, child_css):
    """True iff an element matching child_css exists INSIDE the
    element matching parent_css (C2 re-review F3: id presence in
    the whole DOM does not prove containment)."""
    return bool(d.eval(
        "const p=document.querySelector(arguments[0]);"
        "return p ? !!p.querySelector(arguments[1]) : false;",
        [parent_css, child_css]))


def _child_txt(d, parent_css, child_css):
    """Text of the child element inside the parent element, or None
    (C2 re-review F3: same containment rule, for text checks)."""
    return d.eval(
        "const p=document.querySelector(arguments[0]);"
        "const c=p ? p.querySelector(arguments[1]) : null;"
        "return c ? c.textContent : null;", [parent_css, child_css])


def select_option(d, css, value):
    """Set a <select> value and fire change."""
    return d.eval(
        "const el=document.querySelector(arguments[0]);"
        "el.value=arguments[1];"
        "el.dispatchEvent(new Event('change',{bubbles:true}));"
        "return el.value;", [css, value])


def txt(d, css):
    return d.eval(
        "const el=document.querySelector(arguments[0]);"
        "return el ? el.textContent : null;", [css])


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
    """Collapse all whitespace so multi-line renders compare sanely."""
    return " ".join((s or "").split())


class Y9WD(WD):
    """WD with a Marionette call counter (six-metrics leg), a scoped
    element-from-element search (test-01 active-pane rule), and a
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
        (Redteam re-review B2). Returns True when the session is
        parked on a safe current window, False when no safe window
        could be established (the caller must then NOT let DELETE
        /session run on an uncontrolled window).

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

    def find_in(self, parent_el, css):
        """Find a child element inside a parent element (WebDriver
        element-from-element). Returns the child element id. Used to
        scope test-01 typing to the active pane only."""
        resp = self._wd("POST", self._s(f"/element/{parent_el}/element"),
                        {"using": "css selector", "value": css})
        return resp["value"][EL_KEY]

    def click_el(self, el):
        self._wd("POST", self._s(f"/element/{el}/click"), {})

    def type_in(self, el, text):
        self._wd("POST", self._s(f"/element/{el}/clear"), {})
        self._wd("POST", self._s(f"/element/{el}/value"), {"text": text})

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


class Y9Runner(Runner):
    """Runner with attempt-aware step logging (Redteam A11) and a
    gaps list for skipped spec steps (test-10 step 15)."""

    def __init__(self, test_id, base_url):
        super().__init__(test_id, base_url)
        self.attempt = 1
        self.gaps = []
        # Ladder time in ms, accumulated by ensure_visible (C1
        # re-review F6 / C3 re-review F2): stall is time spent in
        # hidden-body recovery ladders, never whole-test elapsed.
        self.stall_ms = 0

    def check(self, name, cond, detail=""):
        """Base check plus a timed JSONL record with the attempt
        field (C1 re-review F1 / C3 re-review F5). Without this
        override the base Runner.check only prints, so every
        intermediate check (including the load-bearing pinned ones)
        left no JSONL record at all."""
        start = time.perf_counter()
        ok = super().check(name, cond, detail)
        ms = (time.perf_counter() - start) * 1000
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
        start = time.perf_counter()
        try:
            detail = fn()
            ok, error = True, None
        except Exception as exc:
            detail, ok, error = None, False, f"{type(exc).__name__}: {exc}"
        ms = (time.perf_counter() - start) * 1000
        log_step(self.test, name, op, ms, ok, detail, error)
        print(f"[{self.test}] {name} {'ok' if ok else 'FAIL'} "
              f"{ms:.0f}ms detail={detail} error={error}", flush=True)
        if not ok:
            self.failures.append(f"{name}: {error}")
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
    raise RuntimeError(
        "INFRA: rebootstrap: no visible test tab after 3 attempts")


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
        raise RuntimeError(
            f"FIXTURE-UNAVAILABLE: {label}: "
            f"{diag.get('eval_error', 'no body element')}")
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
            raise RuntimeError(
                f"FIXTURE-UNAVAILABLE: {label}: "
                f"{diag.get('eval_error', 'no body element')}")
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
            raise RuntimeError(
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
            raise RuntimeError(
                f"FIXTURE-UNAVAILABLE: {label}: "
                f"{diag.get('eval_error', 'no body element')}")
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
        with Y9WD() as d:
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
# The JS below is transcribed from tests/realistic/agy-y2/check.mjs
# verifyTest, same selectors, same expected values, same messages,
# executed through Marionette eval instead of puppeteer evaluate.
# Two values check.mjs reads but never asserts are kept read-only
# here too, by design (see the v2 plan): test-01 terminalOutput and
# test-07 selectedCount. They are covered by pinned intermediate
# checks instead (test-01 spec step 15, test-07 spec step 8), because
# a final-verify assertion on them would be unsound (later steps
# re-render the panes / reset the selection). The diff audit is in
# improvements/worker-y9-step-mapping.md section 4.
_VERIFY_JS = '''
const testId = arguments[0];
const failures = [];
const state = {};
function check(cond, msg) {
  if (!cond) failures.push(msg);
}
if (testId === '01') {
  const sessName = document.querySelector('#active-session-name')?.textContent?.trim();
  const statusInd = document.querySelector('#status-indicator')?.textContent?.trim();
  const winCount = document.querySelector('#window-count')?.textContent?.trim();
  const paneCount = document.querySelector('#pane-count')?.textContent?.trim();
  const tab0 = document.querySelector('#window-tab-0')?.textContent?.trim();
  const tab1 = document.querySelector('#window-tab-1')?.textContent?.trim();
  const savedMsg = document.querySelector('#saved-status-message')?.textContent?.trim();
  const isSavedVisible = document.querySelector('#saved-status-message')?.classList?.contains('visible');
  const terminalOutput = Array.from(document.querySelectorAll('.pane-content')).map(el => el.textContent || '').join('\\n');
  state.sessionName = sessName;
  state.status = statusInd;
  state.windowCount = winCount;
  state.paneCount = paneCount;
  state.savedMessage = savedMsg;
  check(sessName === 'deploy', `Expected active session 'deploy', got '${sessName}'`);
  check(statusInd && statusInd.includes('deploy: Attached'), `Expected status to contain 'deploy: Attached', got '${statusInd}'`);
  check(winCount === '2', `Expected window count 2, got '${winCount}'`);
  check(paneCount === '2', `Expected pane count 2, got '${paneCount}'`);
  check(tab0 && tab0.includes('0:bash'), `Expected tab 0 '0:bash', got '${tab0}'`);
  check(tab1 && tab1.includes('1:worker-logs'), `Expected tab 1 '1:worker-logs', got '${tab1}'`);
  check(isSavedVisible, 'Saved status message is not visible');
  check(savedMsg && savedMsg.includes('Session deploy saved with 2 windows'), `Saved message mismatch, got '${savedMsg}'`);
} else if (testId === '02') {
  const wifiStatus = document.querySelector('#wifi-toggle-status')?.textContent?.trim();
  const connectedSsid = document.querySelector('#connected-network-name')?.textContent?.trim();
  const connBadge = document.querySelector('#wifi-connection-badge')?.textContent?.trim();
  const cafeFree = document.querySelector('#item-cafefree');
  const btStatus = document.querySelector('#bt-toggle-status')?.textContent?.trim();
  const mxMaster = document.querySelector('#paired-item-mx-master');
  const summarySsid = document.querySelector('#summary-wifi-ssid')?.textContent?.trim();
  const summaryMetered = document.querySelector('#summary-wifi-metered')?.textContent?.trim();
  const summaryBt = document.querySelector('#summary-bt-device')?.textContent?.trim();
  const toast = document.querySelector('#settings-status-toast');
  const toastText = toast?.textContent?.trim();
  const isToastActive = toast?.classList?.contains('active');
  state.wifiStatus = wifiStatus;
  state.connectedSsid = connectedSsid;
  state.btStatus = btStatus;
  state.summaryMetered = summaryMetered;
  check(wifiStatus === 'Enabled', `Expected Wi-Fi 'Enabled', got '${wifiStatus}'`);
  check(connectedSsid === 'HomeFiber-5G', `Expected connected SSID 'HomeFiber-5G', got '${connectedSsid}'`);
  check(connBadge === 'Connected', `Expected connection badge 'Connected', got '${connBadge}'`);
  check(!cafeFree, 'Network CafeFree was not forgotten (still exists in DOM)');
  check(btStatus === 'Enabled', `Expected Bluetooth 'Enabled', got '${btStatus}'`);
  check(!!mxMaster && mxMaster.textContent.includes('MX Master 3S'), 'Device MX Master 3S not paired');
  check(summarySsid === 'HomeFiber-5G', `Expected summary SSID 'HomeFiber-5G', got '${summarySsid}'`);
  check(summaryMetered === 'Yes', `Expected summary metered 'Yes', got '${summaryMetered}'`);
  check(summaryBt === 'MX Master 3S', `Expected summary BT 'MX Master 3S', got '${summaryBt}'`);
  check(isToastActive, 'Settings toast notification is not active');
  check(toastText && toastText.includes('Network settings applied successfully'), `Toast mismatch, got '${toastText}'`);
} else if (testId === '03') {
  const filename = document.querySelector('#current-filename')?.textContent?.trim();
  const dimW = document.querySelector('#dim-width')?.textContent?.trim();
  const dimH = document.querySelector('#dim-height')?.textContent?.trim();
  const cropRatio = document.querySelector('#active-crop-ratio')?.textContent?.trim();
  const filterName = document.querySelector('#active-filter-name')?.textContent?.trim();
  const brightness = document.querySelector('#brightness-display')?.textContent?.trim();
  const rotation = document.querySelector('#rotation-angle')?.textContent?.trim();
  const banner = document.querySelector('#export-status-banner');
  const bannerText = banner?.textContent?.trim();
  const isBannerActive = banner?.classList?.contains('active');
  const formatDisplay = document.querySelector('#dialog-format-display')?.textContent?.trim();
  const dimsDisplay = document.querySelector('#dialog-dimensions-display')?.textContent?.trim();
  state.filename = filename;
  state.dimensions = `${dimW}x${dimH}`;
  state.filter = filterName;
  state.rotation = rotation;
  state.brightness = brightness;
  check(filename === 'sunset.jpg', `Expected file 'sunset.jpg', got '${filename}'`);
  check(cropRatio === '4:3', `Expected crop ratio '4:3', got '${cropRatio}'`);
  check(filterName === 'Vivid', `Expected filter 'Vivid', got '${filterName}'`);
  check(brightness === '0', `Expected brightness '0' (undone), got '${brightness}'`);
  check(rotation === '90 deg', `Expected rotation '90 deg', got '${rotation}'`);
  check(dimW === '750', `Expected width '750', got '${dimW}'`);
  check(dimH === '1000', `Expected height '1000', got '${dimH}'`);
  check(formatDisplay === 'PNG', `Expected format display 'PNG', got '${formatDisplay}'`);
  check(dimsDisplay && dimsDisplay.includes('750 x 1000'), `Expected dialog dims '750 x 1000', got '${dimsDisplay}'`);
  check(isBannerActive, 'Export banner is not active');
  check(bannerText && bannerText.includes('Image exported: sunset.png (750x1000, PNG)'), `Banner mismatch, got '${bannerText}'`);
} else if (testId === '04') {
  const sentCount = document.querySelector('#sent-folder-counter')?.textContent?.trim();
  const draftsCount = document.querySelector('#drafts-folder-counter')?.textContent?.trim();
  const sentRow = document.querySelector('#sent-row-1');
  const sentRowDisplay = sentRow ? window.getComputedStyle(sentRow).display : 'none';
  const toast = document.querySelector('#toast-alert');
  const toastText = toast?.textContent?.trim();
  const isToastVisible = toast?.classList?.contains('visible');
  state.sentCount = sentCount;
  state.draftsCount = draftsCount;
  state.sentRowDisplay = sentRowDisplay;
  check(sentCount === '13', `Expected Sent count 13, got '${sentCount}'`);
  check(draftsCount === '0', `Expected Drafts count 0, got '${draftsCount}'`);
  check(sentRow && sentRowDisplay !== 'none', 'Sent table row #sent-row-1 is not visible');
  check(sentRow && sentRow.textContent.includes('team@example.com'), 'Sent row missing recipient team@example.com');
  check(sentRow && sentRow.textContent.includes('Q4 report'), 'Sent row missing subject Q4 report');
  check(isToastVisible, 'Sent toast alert is not visible');
  check(toastText && toastText.includes('Email sent to team@example.com with attachment report.pdf'), `Toast mismatch, got '${toastText}'`);
} else if (testId === '05') {
  const a1 = document.querySelector('#cell-input-a1')?.value?.trim();
  const b1 = document.querySelector('#cell-input-b1')?.value?.trim();
  const a2 = document.querySelector('#cell-input-a2')?.value?.trim();
  const b2 = document.querySelector('#cell-input-b2')?.value?.trim();
  const a3 = document.querySelector('#cell-input-a3')?.value?.trim();
  const b3 = document.querySelector('#cell-input-b3')?.value?.trim();
  const a4 = document.querySelector('#cell-input-a4')?.value?.trim();
  const b4 = document.querySelector('#cell-input-b4')?.value?.trim();
  const valB5 = document.querySelector('#cell-value-b5')?.textContent?.trim();
  const valB6 = document.querySelector('#cell-value-b6')?.textContent?.trim();
  const chartSvg = document.querySelector('#sales-bar-svg');
  const chartTitle = document.querySelector('#chart-title-text')?.textContent?.trim();
  const toast = document.querySelector('#sheet-status-toast');
  const toastText = toast?.textContent?.trim();
  const isToastActive = toast?.classList?.contains('active');
  state.a1 = a1;
  state.b4 = b4;
  state.valB5 = valB5;
  state.valB6 = valB6;
  state.chartTitle = chartTitle;
  check(a1 === 'Month', `Expected A1 'Month', got '${a1}'`);
  check(b1 === 'Sales', `Expected B1 'Sales', got '${b1}'`);
  check(a2 === 'Jan' && b2 === '1200', `Expected Jan 1200, got '${a2} ${b2}'`);
  check(a3 === 'Feb' && b3 === '1500', `Expected Feb 1500, got '${a3} ${b3}'`);
  check(a4 === 'Mar', `Expected A4 'Mar', got '${a4}'`);
  check(b4 === '1800', `Expected B4 corrected to '1800', got '${b4}'`);
  check(valB5 === '4500', `Expected Total (B5) '4500', got '${valB5}'`);
  check(valB6 === '1500.00', `Expected Average (B6) '1500.00', got '${valB6}'`);
  check(!!chartSvg, 'Bar chart SVG #sales-bar-svg not found');
  check(chartTitle === 'Q1 Regional Sales', `Expected chart title 'Q1 Regional Sales', got '${chartTitle}'`);
  check(isToastActive, 'Sheet status toast is not active');
  check(toastText && toastText.includes('Sheet saved: Total=4500, Average=1500.00, Chart=Q1 Regional Sales'), `Toast mismatch, got '${toastText}'`);
} else if (testId === '06') {
  const room = document.querySelector('#room-name-display')?.textContent?.trim();
  const partCount = document.querySelector('#participant-count')?.textContent?.trim();
  const statusBadge = document.querySelector('#call-status-badge')?.textContent?.trim();
  const micStatus = document.querySelector('#mic-status-indicator')?.textContent?.trim();
  const camStatus = document.querySelector('#cam-status-indicator')?.textContent?.trim();
  const handStatus = document.querySelector('#hand-raise-indicator')?.textContent?.trim();
  const chatText = document.querySelector('#chat-message-list')?.textContent || '';
  const toast = document.querySelector('#call-summary-toast');
  const toastText = toast?.textContent?.trim();
  const isToastActive = toast?.classList?.contains('active');
  state.room = room;
  state.participants = partCount;
  state.status = statusBadge;
  state.mic = micStatus;
  state.cam = camStatus;
  check(room === 'Sprint Planning', `Expected room 'Sprint Planning', got '${room}'`);
  check(partCount === '4', `Expected 4 participants, got '${partCount}'`);
  check(statusBadge === 'Connected', `Expected call status 'Connected', got '${statusBadge}'`);
  check(micStatus === 'Unmuted', `Expected mic 'Unmuted', got '${micStatus}'`);
  check(camStatus === 'Camera On', `Expected camera 'Camera On', got '${camStatus}'`);
  check(handStatus === 'Hand Raised', `Expected hand 'Hand Raised', got '${handStatus}'`);
  check(chatText.includes('Ready for updates'), 'Chat message missing in chat list');
  check(isToastActive, 'Call summary toast is not active');
  check(toastText && toastText.includes('Meeting Sprint Planning: 4 participants, audio active, video active'), `Toast mismatch, got '${toastText}'`);
} else if (testId === '07') {
  const selectedCount = document.querySelector('#selected-files-count')?.textContent?.trim();
  const trashCount = document.querySelector('#trash-counter')?.textContent?.trim();
  const archiveCount = document.querySelector('#folder-count-archive')?.textContent?.trim();
  const name1 = document.querySelector('#file-name-img1')?.textContent?.trim();
  const name5 = document.querySelector('#file-name-img5')?.textContent?.trim();
  const row4 = document.querySelector('#file-row-img4');
  const isRow4Visible = row4 && !row4.classList.contains('hidden');
  const newFolderItem = document.querySelector('#folder-item-processed');
  const toast = document.querySelector('#inventory-summary-toast');
  const toastText = toast?.textContent?.trim();
  const isToastActive = toast?.classList?.contains('active');
  state.name1 = name1;
  state.name5 = name5;
  state.trash = trashCount;
  state.archive = archiveCount;
  check(name1 === 'photo-2026-01.jpg', `Expected file 1 'photo-2026-01.jpg', got '${name1}'`);
  check(name5 === 'photo-2026-05.jpg', `Expected file 5 'photo-2026-05.jpg', got '${name5}'`);
  check(archiveCount && archiveCount.includes('3 files'), `Expected Archive to have '3 files', got '${archiveCount}'`);
  check(trashCount === '0', `Expected Trash count '0', got '${trashCount}'`);
  check(isRow4Visible, 'File row img4 is not restored and visible');
  check(!!newFolderItem, 'Custom folder item #folder-item-processed not found');
  check(isToastActive, 'Inventory summary toast is not active');
  check(toastText && toastText.includes('Root: 5 files, Archive: 3 files, Trash: 0 files, Folder Processed created'), `Toast mismatch, got '${toastText}'`);
} else if (testId === '08') {
  const panel = document.querySelector('#devtools-panel');
  const isExpanded = panel?.classList?.contains('expanded');
  const logCount = document.querySelector('#console-log-count')?.textContent?.trim();
  const netVisible = document.querySelector('#network-visible-count')?.textContent?.trim();
  const logOutput = document.querySelector('#console-output-log')?.textContent || '';
  const checkoutRow = document.querySelector('#row-req-api-checkout');
  const isCheckoutVisible = checkoutRow && !checkoutRow.classList.contains('hidden');
  const stylesRow = document.querySelector('#row-req-styles');
  const isStylesHidden = stylesRow && stylesRow.classList.contains('hidden');
  const toast = document.querySelector('#devtools-toast-summary');
  const toastText = toast?.textContent?.trim();
  const isToastActive = toast?.classList?.contains('active');
  state.isExpanded = isExpanded;
  state.logCount = logCount;
  state.netVisible = netVisible;
  check(isExpanded, 'DevTools panel is not expanded');
  check(logCount === '1', `Expected console log count '1', got '${logCount}'`);
  check(netVisible === '3', `Expected visible network count '3', got '${netVisible}'`);
  check(logOutput.includes('ready'), 'Console log does not contain "ready"');
  check(isCheckoutVisible, 'Filtered row /api/v1/checkout is not visible');
  check(isStylesHidden, 'Unmatched row styles.css was not filtered out');
  check(isToastActive, 'DevTools summary toast is not active');
  check(toastText && toastText.includes('DevTools diagnostics: 1 logs, 3 filtered network rows, error 404 checked'), `Toast mismatch, got '${toastText}'`);
} else if (testId === '09') {
  const totalNotes = document.querySelector('#notes-total-counter')?.textContent?.trim();
  const titleShopping = document.querySelector('#note-item-title-shopping')?.textContent?.trim();
  const titleConflict = document.querySelector('#note-item-title-conflict')?.textContent?.trim();
  const archivedItem = document.querySelector('#note-item-archived-draft');
  const toast = document.querySelector('#sync-summary-toast');
  const toastText = toast?.textContent?.trim();
  const isToastActive = toast?.classList?.contains('active');
  state.totalNotes = totalNotes;
  state.titleShopping = titleShopping;
  state.titleConflict = titleConflict;
  check(totalNotes === '3', `Expected total notes '3', got '${totalNotes}'`);
  check(titleShopping === 'Shopping', `Expected note 'Shopping', got '${titleShopping}'`);
  check(titleConflict === 'Shopping - Phone Copy', `Expected note 'Shopping - Phone Copy', got '${titleConflict}'`);
  check(!archivedItem, 'Outdated note #note-item-archived-draft was not deleted');
  check(isToastActive, 'Sync summary toast is not active');
  check(toastText && toastText.includes('Sync completed: 3 notes active, Shopping and Shopping - Phone Copy verified'), `Toast mismatch, got '${toastText}'`);
} else if (testId === '10') {
  const fileName = document.querySelector('#active-file-name')?.textContent?.trim();
  const bpCount = document.querySelector('#breakpoint-count-indicator')?.textContent?.trim();
  const statusBadge = document.querySelector('#debug-state-badge')?.textContent?.trim();
  const watchTotal = document.querySelector('#watch-val-total')?.textContent?.trim();
  const watchGrand = document.querySelector('#watch-val-grand-total')?.textContent?.trim();
  const stackList = document.querySelector('#call-stack-list')?.textContent || '';
  const toast = document.querySelector('#debug-toast-summary');
  const toastText = toast?.textContent?.trim();
  const isToastActive = toast?.classList?.contains('active');
  state.file = fileName;
  state.breakpoints = bpCount;
  state.status = statusBadge;
  state.watchTotal = watchTotal;
  state.watchGrand = watchGrand;
  check(fileName === 'app.js', `Expected file 'app.js', got '${fileName}'`);
  check(bpCount === '2', `Expected 2 breakpoints, got '${bpCount}'`);
  check(statusBadge === 'Stopped', `Expected debug status 'Stopped', got '${statusBadge}'`);
  check(watchTotal === '250', `Expected watch total '250', got '${watchTotal}'`);
  check(watchGrand === '250', `Expected watch grandTotal '250', got '${watchGrand}'`);
  check(stackList.includes('renderSummary (line 16)'), 'Call stack missing renderSummary');
  check(isToastActive, 'Debug toast summary is not active');
  check(toastText && toastText.includes('Debug session complete: watched total=250, breakpoints=2, final line 16'), `Toast mismatch, got '${toastText}'`);
} else {
  failures.push(`Unknown test id: ${testId}`);
}
return {passed: failures.length === 0, failures, state};
'''


def verify_test(d, test_id):
    """Run the ported check.mjs verifyTest for one test. Returns
    {"passed": bool, "failures": [...], "state": {...}}."""
    return d.eval(_VERIFY_JS, [test_id])


class IntegrityGuardError(RuntimeError):
    """The ported verify PASSED on the untouched fixture: the test
    cannot prove anything and is a suite defect, never a pass."""


def open_fixture(r, d, fname, test_id):
    """Load a fixture on the shared tab, then run the integrity
    guard through the SAME ported verify as the final verify.

    Shared visible test tab (r.tab), NOT window/new: new tabs
    intermittently open with body visibility:hidden. The tab is
    shared across tests; each test clears storage and reloads, so
    state stays isolated.
    """
    url = r.base + f"/{SUITE_DIR}/fixtures/" + fname
    if r.tab not in d.handles():
        # The shared tab is gone (closed externally); get a fresh one.
        print(f"[{r.test}] shared tab gone, rebootstrap", flush=True)
        try:
            r.tab = rebootstrap_tab(d, r.base)
        except Exception as exc:
            raise RuntimeError(
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
                raise RuntimeError(
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
                raise RuntimeError(
                    "INFRA: hidden-body after final fresh tab; cannot "
                    "drive")
    if not ok:
        raise RuntimeError(
            "INFRA: hidden-body on test tab after recovery ladder; "
            "cannot drive (Marionette refuses clicks on "
            "visibility:hidden content)")
    # The check below is the real gate (Redteam re-review N14: the
    # old r.step("check body visible") logged ok True even when the
    # body was hidden, because Y9Runner.step only fails on
    # exception and ignores a False return).
    r.check("body renders visible (no hidden-body incident)",
            d.visible("body"), "visible")
    # INTEGRITY GUARD (C2 F7, Redteam A6): the SAME ported verify
    # must FAIL on the untouched fixture. It runs after the fresh
    # load and before any action, per test, and is re-executed on
    # any re-run. The untouched failure list is recorded as
    # evidence. A pass on untouched aborts THIS test as a suite
    # defect (suite continues, no effect on infra_blocked).
    guard = verify_test(d, test_id)
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


# ---------------- test drivers (simulate.mjs step for step) ----------------
# Every modal open is followed by a wait_for on its open/active
# selector (10 s). Intermediate spec verifies are r.check() calls.
# The full step-mapping table is in
# improvements/worker-y9-step-mapping.md.

def _active_pane_type(d, text):
    """Type into the terminal input of the ACTIVE pane only (Redteam
    A9). Only the active pane's content div carries id
    #pane-active-output (fixture lines 205-206); the input and send
    button ids repeat per pane. Scope by element-from-element search
    inside the pane holding #pane-active-output, then use real
    Marionette element clear/value/click on the child ids."""
    pane_id = d.eval(
        "const c = document.querySelector('#pane-active-output');"
        " if (!c) return null;"
        " return c.closest('.pane').id;")
    if not pane_id:
        raise RuntimeError("no active pane output found")
    d.scroll_into_view("#" + pane_id)
    parent = d.find("#" + pane_id)
    inp = d.find_in(parent, "#pane-terminal-input")
    d.type_in(inp, text)
    return pane_id


def _active_pane_click_send(d):
    pane_id = d.eval(
        "const c = document.querySelector('#pane-active-output');"
        " if (!c) return null;"
        " return c.closest('.pane').id;")
    if not pane_id:
        raise RuntimeError("no active pane output found")
    parent = d.find("#" + pane_id)
    btn = d.find_in(parent, "#btn-send-command")
    d.click_el(btn)
    return pane_id


def run_01(r, d):
    open_fixture(r, d, "test-01-tmux-session.html", "01")
    r.check("session count starts 0", txt(d, "#session-count") == "0",
            txt(d, "#session-count"))
    r.check("status no active session",
            txt(d, "#status-indicator") == "No Active Session",
            txt(d, "#status-indicator"))
    r.step("open new session modal", "click",
           lambda: d.click("#btn-new-session"))
    r.step("wait session modal open", "wait",
           lambda: d.wait_for(
               "document.querySelector('#session-modal') && "
               "document.querySelector('#session-modal').classList.contains('open')",
               10, "#session-modal.open"))
    r.step("type session name deploy", "type",
           lambda: d.type_text("#input-session-name", "deploy"))
    r.step("create session", "click", lambda: d.click("#btn-create-session"))
    r.check("active session deploy", txt(d, "#active-session-name") == "deploy",
            txt(d, "#active-session-name"))
    r.check("status attached",
            "deploy: Attached" in (txt(d, "#status-indicator") or ""),
            txt(d, "#status-indicator"))
    r.check("window count 1", txt(d, "#window-count") == "1",
            txt(d, "#window-count"))
    r.check("pane count 1", txt(d, "#pane-count") == "1",
            txt(d, "#pane-count"))
    r.step("split horizontal", "click",
           lambda: d.click("#btn-split-horizontal"))
    r.check("pane count 2", txt(d, "#pane-count") == "2",
            txt(d, "#pane-count"))
    r.check("pane 2 present and visible", d.visible("#pane-2"), "visible")
    r.step("type uptime (active pane)", "type",
           lambda: _active_pane_type(d, "uptime"))
    r.step("send command (active pane)", "click",
           lambda: _active_pane_click_send(d))
    # PINNED intermediate check (C2 F3): the ported final verify
    # does NOT cover the uptime output, so this check is load-bearing.
    out = r.step("read active pane output", "text",
                 lambda: txt(d, "#pane-active-output"))
    r.check("uptime output has load average",
            "load average: 0.18, 0.22, 0.15" in (out or ""), out)
    r.step("new window", "click", lambda: d.click("#btn-new-window"))
    r.check("window count 2", txt(d, "#window-count") == "2",
            txt(d, "#window-count"))
    r.step("open rename modal", "click",
           lambda: d.click("#btn-rename-window"))
    r.step("wait rename modal open", "wait",
           lambda: d.wait_for(
               "document.querySelector('#rename-window-modal') && "
               "document.querySelector('#rename-window-modal').classList.contains('open')",
               10, "#rename-window-modal.open"))
    r.step("type window name worker-logs", "type",
           lambda: d.type_text("#input-window-name", "worker-logs"))
    r.step("confirm rename", "click",
           lambda: d.click("#btn-confirm-rename"))
    r.check("window tab 1 renamed",
            "1:worker-logs" in (txt(d, "#window-tab-1") or ""),
            txt(d, "#window-tab-1"))
    r.step("split vertical", "click",
           lambda: d.click("#btn-split-vertical"))
    r.check("pane count 2 in window 1", txt(d, "#pane-count") == "2",
            txt(d, "#pane-count"))
    r.step("mistake: kill pane", "click", lambda: d.click("#btn-kill-pane"))
    r.check("pane count drops to 1", txt(d, "#pane-count") == "1",
            txt(d, "#pane-count"))
    r.check("alert says pane closed",
            "Pane 2 closed" in (txt(d, "#alert-banner") or ""),
            txt(d, "#alert-banner"))
    r.step("recovery: undo pane", "click", lambda: d.click("#btn-undo-pane"))
    r.check("pane count back to 2", txt(d, "#pane-count") == "2",
            txt(d, "#pane-count"))
    r.step("detach session", "click",
           lambda: d.click("#btn-detach-session"))
    r.check("status detached",
            "deploy: Detached" in (txt(d, "#status-indicator") or ""),
            txt(d, "#status-indicator"))
    r.check("session overview visible", d.visible("#session-overview"),
            "visible")
    r.check("session shows 2 windows",
            txt(d, "#session-windows-deploy") == "2 windows",
            txt(d, "#session-windows-deploy"))
    r.step("reattach deploy", "click", lambda: d.click("#btn-attach-deploy"))
    r.check("status attached again",
            "deploy: Attached" in (txt(d, "#status-indicator") or ""),
            txt(d, "#status-indicator"))
    r.step("save session state", "click",
           lambda: d.click("#btn-save-session-state"))
    r.check("saved message shown",
            "Session deploy saved with 2 windows" in
            (txt(d, "#saved-status-message") or ""),
            txt(d, "#saved-status-message"))
    final_verify(r, d, "01")


def run_02(r, d):
    open_fixture(r, d, "test-02-network-settings.html", "02")
    r.check("wifi disabled at start",
            txt(d, "#wifi-toggle-status") == "Disabled",
            txt(d, "#wifi-toggle-status"))
    r.check("not connected at start",
            txt(d, "#connected-network-name") == "Not Connected",
            txt(d, "#connected-network-name"))
    r.step("toggle wifi on", "click", lambda: d.click("#toggle-wifi"))
    r.check("wifi enabled", txt(d, "#wifi-toggle-status") == "Enabled",
            txt(d, "#wifi-toggle-status"))
    r.check("wifi content displayed", d.visible("#wifi-content"), "visible")
    r.step("connect HomeFiber-5G", "click",
           lambda: d.click("#network-row-homefiber"))
    r.step("wait wifi auth modal", "wait",
           lambda: d.wait_for(
               "document.querySelector('#wifi-auth-modal') && "
               "document.querySelector('#wifi-auth-modal').classList.contains('active')",
               10, "#wifi-auth-modal.active"))
    r.step("type wifi password", "type",
           lambda: d.type_text("#input-wifi-password", "HomeKey2026"))
    r.step("confirm wifi connect", "click",
           lambda: d.click("#btn-connect-wifi"))
    r.check("connected SSID",
            txt(d, "#connected-network-name") == "HomeFiber-5G",
            txt(d, "#connected-network-name"))
    r.check("connection badge",
            txt(d, "#wifi-connection-badge") == "Connected",
            txt(d, "#wifi-connection-badge"))
    r.step("manage known networks", "click",
           lambda: d.click("#btn-manage-known-networks"))
    r.check("known networks panel visible",
            d.visible("#known-networks-panel"), "visible")
    r.step("forget CafeFree", "click",
           lambda: d.click("#btn-forget-cafefree"))
    r.check("CafeFree removed from DOM", count(d, "#item-cafefree") == 0,
            count(d, "#item-cafefree"))
    r.step("switch to bluetooth tab", "click",
           lambda: d.click("#nav-tab-bluetooth"))
    r.check("bluetooth panel active",
            has_class(d, "#bluetooth-panel", "active"), "active")
    r.check("bluetooth enabled", txt(d, "#bt-toggle-status") == "Enabled",
            txt(d, "#bt-toggle-status"))
    r.step("scan bluetooth devices", "click",
           lambda: d.click("#btn-scan-bt-devices"))
    r.check("available list visible", d.visible("#available-bt-list"),
            "visible")
    r.check("MX Master listed in available list",
            _child_in(d, "#available-bt-list", "#bt-device-mx-master"),
            "present in #available-bt-list")
    r.step("pair MX Master", "click",
           lambda: d.click("#btn-pair-mx-master"))
    # Single eval, not two (redteam diff F8): the paired check used
    # to evaluate the same child text twice.
    paired_txt = _child_txt(d, "#paired-bt-list", "#paired-item-mx-master")
    r.check("MX Master paired in paired list",
            "Paired" in (paired_txt or ""), paired_txt)
    r.step("bluetooth off", "click", lambda: d.click("#toggle-bluetooth"))
    r.check("bluetooth disabled", txt(d, "#bt-toggle-status") == "Disabled",
            txt(d, "#bt-toggle-status"))
    r.step("bluetooth on again", "click",
           lambda: d.click("#toggle-bluetooth"))
    r.check("bluetooth enabled again",
            txt(d, "#bt-toggle-status") == "Enabled",
            txt(d, "#bt-toggle-status"))
    r.check("paired device persists in paired list",
            _child_in(d, "#paired-bt-list", "#paired-item-mx-master"),
            "present in #paired-bt-list")
    r.step("back to wifi tab", "click", lambda: d.click("#nav-tab-wifi"))
    r.step("open network properties", "click",
           lambda: d.click("#btn-network-properties"))
    r.step("wait properties panel", "wait",
           lambda: d.wait_for(
               "document.querySelector('#network-properties-panel') && "
               "document.querySelector('#network-properties-panel').classList.contains('active')",
               10, "#network-properties-panel.active"))
    r.step("enable metered", "click",
           lambda: d.click("#toggle-metered-connection"))
    r.check("metered indicator",
            txt(d, "#metered-status-indicator") == "Metered",
            txt(d, "#metered-status-indicator"))
    r.step("save wifi properties", "click",
           lambda: d.click("#btn-save-wifi-properties"))
    r.step("open status tab", "click", lambda: d.click("#nav-tab-status"))
    r.check("summary SSID",
            txt(d, "#summary-wifi-ssid") == "HomeFiber-5G",
            txt(d, "#summary-wifi-ssid"))
    r.check("summary metered", txt(d, "#summary-wifi-metered") == "Yes",
            txt(d, "#summary-wifi-metered"))
    r.check("summary bluetooth",
            txt(d, "#summary-bt-device") == "MX Master 3S",
            txt(d, "#summary-bt-device"))
    r.step("apply network settings", "click",
           lambda: d.click("#btn-apply-network-settings"))
    # M11: the apply toast is asserted only in check.mjs; check it
    # here as well as in the final verify.
    r.check("apply toast active",
            has_class(d, "#settings-status-toast", "active"), "active")
    r.check("apply toast text",
            "Network settings applied successfully" in
            (txt(d, "#settings-status-toast") or ""),
            txt(d, "#settings-status-toast"))
    final_verify(r, d, "02")


def run_03(r, d):
    open_fixture(r, d, "test-03-photo-editor.html", "03")
    r.check("editor ready",
            txt(d, "#editor-status-text") == "Ready. No file loaded.",
            txt(d, "#editor-status-text"))
    r.step("select sunset.jpg", "click",
           lambda: d.click("#file-item-sunset"))
    r.step("load photo", "click", lambda: d.click("#btn-load-photo"))
    r.check("filename sunset", txt(d, "#current-filename") == "sunset.jpg",
            txt(d, "#current-filename"))
    r.check("width 1200", txt(d, "#dim-width") == "1200",
            txt(d, "#dim-width"))
    r.check("height 900", txt(d, "#dim-height") == "900",
            txt(d, "#dim-height"))
    r.step("open crop tab", "click", lambda: d.click("#tool-tab-crop"))
    r.check("crop controls active", has_class(d, "#crop-controls", "active"),
            "active")
    r.step("choose 4:3 ratio", "click", lambda: d.click("#btn-ratio-4-3"))
    r.check("ratio 4:3", txt(d, "#active-crop-ratio") == "4:3",
            txt(d, "#active-crop-ratio"))
    r.step("apply crop", "click", lambda: d.click("#btn-apply-crop"))
    r.check("width 1000 after crop", txt(d, "#dim-width") == "1000",
            txt(d, "#dim-width"))
    r.check("height 750 after crop", txt(d, "#dim-height") == "750",
            txt(d, "#dim-height"))
    r.step("open filters tab", "click", lambda: d.click("#tool-tab-filters"))
    r.check("filters panel active", has_class(d, "#filters-panel", "active"),
            "active")
    r.step("apply Vivid filter", "click",
           lambda: d.click("#btn-filter-vivid"))
    r.check("filter Vivid", txt(d, "#active-filter-name") == "Vivid",
            txt(d, "#active-filter-name"))
    r.step("open adjust tab", "click", lambda: d.click("#tool-tab-adjust"))
    r.check("brightness 0", txt(d, "#brightness-display") == "0",
            txt(d, "#brightness-display"))
    r.step("brightness plus", "click",
           lambda: d.click("#btn-brightness-plus"))
    r.check("brightness 20", txt(d, "#brightness-display") == "20",
            txt(d, "#brightness-display"))
    r.step("mistake: undo brightness", "click",
           lambda: d.click("#btn-undo-adjust"))
    r.check("brightness back to 0", txt(d, "#brightness-display") == "0",
            txt(d, "#brightness-display"))
    r.step("open transform tab", "click",
           lambda: d.click("#tool-tab-transform"))
    r.step("rotate 90 cw", "click", lambda: d.click("#btn-rotate-90-cw"))
    r.check("rotation 90 deg", txt(d, "#rotation-angle") == "90 deg",
            txt(d, "#rotation-angle"))
    r.check("width 750 after rotate", txt(d, "#dim-width") == "750",
            txt(d, "#dim-width"))
    r.check("height 1000 after rotate", txt(d, "#dim-height") == "1000",
            txt(d, "#dim-height"))
    r.step("open export modal", "click",
           lambda: d.click("#btn-open-export"))
    r.step("wait export modal", "wait",
           lambda: d.wait_for(
               "document.querySelector('#export-modal') && "
               "document.querySelector('#export-modal').classList.contains('active')",
               10, "#export-modal.active"))
    r.step("select PNG format", "select",
           lambda: select_option(d, "#select-export-format", "PNG"))
    r.check("dialog format PNG",
            txt(d, "#dialog-format-display") == "PNG",
            txt(d, "#dialog-format-display"))
    r.check("dialog dims 750 x 1000 px",
            (txt(d, "#dialog-dimensions-display") or "").strip()
            == "750 x 1000 px",
            txt(d, "#dialog-dimensions-display"))
    r.step("confirm export", "click",
           lambda: d.click("#btn-confirm-export"))
    r.check("export banner",
            "Image exported: sunset.png (750x1000, PNG)" in
            (txt(d, "#export-status-banner") or ""),
            txt(d, "#export-status-banner"))
    final_verify(r, d, "03")


def run_04(r, d):
    open_fixture(r, d, "test-04-email-compose.html", "04")
    r.check("sent starts 12", txt(d, "#sent-folder-counter") == "12",
            txt(d, "#sent-folder-counter"))
    r.check("drafts start 0", txt(d, "#drafts-folder-counter") == "0",
            txt(d, "#drafts-folder-counter"))
    r.step("compose mail", "click", lambda: d.click("#btn-compose-mail"))
    r.step("wait compose pane open", "wait",
           lambda: d.wait_for(
               "document.querySelector('#compose-pane') && "
               "document.querySelector('#compose-pane').classList.contains('open')",
               10, "#compose-pane.open"))
    r.step("type recipient", "type",
           lambda: d.type_text("#input-recipient-to", "team@example.com"))
    r.step("add CC field", "click", lambda: d.click("#btn-add-cc"))
    r.check("CC group visible", d.visible("#cc-group"), "visible")
    r.step("type CC", "type",
           lambda: d.type_text("#input-recipient-cc", "audit@example.com"))
    r.step("type subject", "type",
           lambda: d.type_text("#input-mail-subject", "Q4 report"))
    r.step("type body", "type",
           lambda: d.type_text("#input-mail-body",
                               "Attached is the Q4 performance overview."))
    r.step("open attachment picker", "click",
           lambda: d.click("#btn-open-attachment-picker"))
    r.step("wait attachment picker", "wait",
           lambda: d.wait_for(
               "document.querySelector('#attachment-picker-modal') && "
               "document.querySelector('#attachment-picker-modal').classList.contains('active')",
               10, "#attachment-picker-modal.active"))
    r.step("choose report.pdf", "click",
           lambda: d.click("#file-option-report-pdf"))
    r.step("confirm attach", "click",
           lambda: d.click("#btn-confirm-attach-file"))
    r.check("attachment chip present in attached list",
            _child_in(d, "#attached-files-list",
                      "#attachment-chip-report"),
            "present in #attached-files-list")
    r.check("attachment counter 1",
            txt(d, "#attachment-counter") == "1",
            txt(d, "#attachment-counter"))
    r.step("save draft", "click", lambda: d.click("#btn-save-draft-mail"))
    r.check("drafts count 1", txt(d, "#drafts-folder-counter") == "1",
            txt(d, "#drafts-folder-counter"))
    r.step("close composer", "click",
           lambda: d.click("#btn-close-composer"))
    r.check("compose pane hidden",
            has_class(d, "#compose-pane", "hidden"), "hidden")
    r.step("open drafts folder", "click",
           lambda: d.click("#nav-folder-drafts"))
    r.step("reopen draft q4", "click",
           lambda: d.click("#draft-entry-q4"))
    r.step("wait compose pane open again", "wait",
           lambda: d.wait_for(
               "document.querySelector('#compose-pane') && "
               "document.querySelector('#compose-pane').classList.contains('open')",
               10, "#compose-pane.open"))
    r.check("subject restored",
            d.value("#input-mail-subject") == "Q4 report",
            d.value("#input-mail-subject"))
    r.step("mistake: remove attachment", "click",
           lambda: d.click("#btn-remove-attachment-report"))
    r.check("attachment counter 0",
            txt(d, "#attachment-counter") == "0",
            txt(d, "#attachment-counter"))
    r.check("attached list empty",
            norm(txt(d, "#attached-files-list")) == "",
            txt(d, "#attached-files-list"))
    r.step("reopen attachment picker", "click",
           lambda: d.click("#btn-open-attachment-picker"))
    r.step("wait attachment picker again", "wait",
           lambda: d.wait_for(
               "document.querySelector('#attachment-picker-modal') && "
               "document.querySelector('#attachment-picker-modal').classList.contains('active')",
               10, "#attachment-picker-modal.active"))
    r.step("choose report.pdf again", "click",
           lambda: d.click("#file-option-report-pdf"))
    r.step("confirm re-attach", "click",
           lambda: d.click("#btn-confirm-attach-file"))
    r.check("attachment counter 1 again",
            txt(d, "#attachment-counter") == "1",
            txt(d, "#attachment-counter"))
    r.check("attachment chip present again in attached list",
            _child_in(d, "#attached-files-list",
                      "#attachment-chip-report"),
            "present in #attached-files-list")
    r.step("send email", "click", lambda: d.click("#btn-dispatch-send"))
    r.check("compose pane hidden after send",
            has_class(d, "#compose-pane", "hidden"), "hidden")
    r.check("sent toast",
            "Email sent to team@example.com with attachment report.pdf" in
            (txt(d, "#toast-alert") or ""), txt(d, "#toast-alert"))
    r.check("sent count 13", txt(d, "#sent-folder-counter") == "13",
            txt(d, "#sent-folder-counter"))
    final_verify(r, d, "04")


def run_05(r, d):
    open_fixture(r, d, "test-05-spreadsheet-chart.html", "05")
    r.check("sheet name",
            txt(d, "#active-sheet-name") == "Sales Forecast",
            txt(d, "#active-sheet-name"))
    for sel, val in [("#cell-input-a1", "Month"), ("#cell-input-b1", "Sales"),
                     ("#cell-input-a2", "Jan"), ("#cell-input-b2", "1200"),
                     ("#cell-input-a3", "Feb"), ("#cell-input-b3", "1500"),
                     ("#cell-input-a4", "Mar")]:
        r.step(f"type {val} into {sel}", "type",
               lambda s=sel, v=val: d.type_text(s, v))
    r.step("mistake: type 9800 into B4", "type",
           lambda: d.type_text("#cell-input-b4", "9800"))
    r.check("B4 shows 9800", txt(d, "#cell-value-b4") == "9800",
            txt(d, "#cell-value-b4"))
    r.step("type Total into A5", "type",
           lambda: d.type_text("#cell-input-a5", "Total"))
    r.step("select cell B5", "click", lambda: d.click("#cell-input-b5"))
    r.step("type SUM formula", "type",
           lambda: d.type_text("#formula-bar-input", "=SUM(B2:B4)"))
    r.step("commit formula", "click",
           lambda: d.click("#btn-commit-formula"))
    r.check("B5 total 12500", txt(d, "#cell-value-b5") == "12500",
            txt(d, "#cell-value-b5"))
    r.step("type Average into A6", "type",
           lambda: d.type_text("#cell-input-a6", "Average"))
    r.step("select cell B6", "click", lambda: d.click("#cell-input-b6"))
    r.step("type AVERAGE formula", "type",
           lambda: d.type_text("#formula-bar-input", "=AVERAGE(B2:B4)"))
    r.step("commit formula 2", "click",
           lambda: d.click("#btn-commit-formula"))
    r.check("B6 average 4166.67", txt(d, "#cell-value-b6") == "4166.67",
            txt(d, "#cell-value-b6"))
    # Simulator clicks the input first (simulate.mjs lines 204-206);
    # the runner used to type without the prior click (C1 re-review
    # Q1). Click, then clear-and-type, literally.
    r.step("correct B4 to 1800", "type",
           lambda: (d.click("#cell-input-b4"),
                    d.type_text("#cell-input-b4", "1800")))
    r.step("recalculate sheet", "click",
           lambda: d.click("#btn-recalculate-sheet"))
    r.check("B5 total 4500", txt(d, "#cell-value-b5") == "4500",
            txt(d, "#cell-value-b5"))
    r.check("B6 average 1500.00", txt(d, "#cell-value-b6") == "1500.00",
            txt(d, "#cell-value-b6"))
    r.step("open chart modal", "click",
           lambda: d.click("#btn-insert-chart-modal"))
    r.step("wait chart modal", "wait",
           lambda: d.wait_for(
               "document.querySelector('#chart-modal') && "
               "document.querySelector('#chart-modal').classList.contains('active')",
               10, "#chart-modal.active"))
    # NOTE: the chart-type select has no onchange listener and the
    # render handler always draws the bar SVG, so this select is
    # outcome-irrelevant; kept for spec fidelity only.
    r.step("select Bar chart type", "select",
           lambda: select_option(d, "#select-chart-type", "Bar"))
    r.step("render chart", "click", lambda: d.click("#btn-render-chart"))
    r.check("bar chart SVG present in chart wrapper",
            _child_in(d, "#chart-wrapper", "#sales-bar-svg"),
            "present in #chart-wrapper")
    # M12: #chart-title-controls is display:none until the render
    # handler shows it; wait for it before the title steps.
    r.step("wait chart title controls visible", "wait",
           lambda: d.wait_for(
               "window.getComputedStyle(document.querySelector("
               "'#chart-title-controls')).display !== 'none'",
               10, "#chart-title-controls visible"))
    # ORDERING: #chart-title-controls is display:none until the
    # render-chart handler shows it, so the title steps run only now.
    r.step("click chart title input", "click",
           lambda: d.click("#input-chart-title"))
    r.step("type chart title", "type",
           lambda: d.type_text("#input-chart-title", "Q1 Regional Sales"))
    r.step("apply chart title", "click",
           lambda: d.click("#btn-apply-chart-title"))
    r.check("chart title set",
            txt(d, "#chart-title-text") == "Q1 Regional Sales",
            txt(d, "#chart-title-text"))
    r.step("save sheet", "click",
           lambda: d.click("#btn-save-sheet-state"))
    r.check("save toast",
            "Sheet saved: Total=4500, Average=1500.00, Chart=Q1 Regional Sales"
            in (txt(d, "#sheet-status-toast") or ""),
            txt(d, "#sheet-status-toast"))
    final_verify(r, d, "05")


def run_06(r, d):
    open_fixture(r, d, "test-06-video-call.html", "06")
    r.check("lobby at start", txt(d, "#call-status-badge") == "Lobby",
            txt(d, "#call-status-badge"))
    r.check("0 participants at start", txt(d, "#participant-count") == "0",
            txt(d, "#participant-count"))
    r.step("type meeting id", "type",
           lambda: d.type_text("#input-meeting-id", "Sprint Planning"))
    r.step("type display name", "type",
           lambda: d.type_text("#input-display-name", "Alex"))
    r.step("join meeting", "click", lambda: d.click("#btn-join-meeting"))
    r.check("connected", txt(d, "#call-status-badge") == "Connected",
            txt(d, "#call-status-badge"))
    r.check("4 participants", txt(d, "#participant-count") == "4",
            txt(d, "#participant-count"))
    r.check("room name",
            txt(d, "#room-name-display") == "Sprint Planning",
            txt(d, "#room-name-display"))
    r.step("mute mic", "click", lambda: d.click("#btn-toggle-mic"))
    r.check("mic muted", txt(d, "#mic-status-indicator") == "Muted",
            txt(d, "#mic-status-indicator"))
    r.check("mic muted class", has_class(d, "#mic-status-indicator", "muted"),
            "muted")
    r.step("unmute mic", "click", lambda: d.click("#btn-toggle-mic"))
    r.check("mic unmuted", txt(d, "#mic-status-indicator") == "Unmuted",
            txt(d, "#mic-status-indicator"))
    r.check("mic active class",
            has_class(d, "#mic-status-indicator", "active"), "active")
    r.step("camera off", "click", lambda: d.click("#btn-toggle-cam"))
    r.check("camera off", txt(d, "#cam-status-indicator") == "Camera Off",
            txt(d, "#cam-status-indicator"))
    r.check("camera off class", has_class(d, "#cam-status-indicator", "off"),
            "off")
    r.step("camera on", "click", lambda: d.click("#btn-toggle-cam"))
    r.check("camera on", txt(d, "#cam-status-indicator") == "Camera On",
            txt(d, "#cam-status-indicator"))
    r.check("camera active class",
            has_class(d, "#cam-status-indicator", "active"), "active")
    r.step("share screen", "click", lambda: d.click("#btn-share-screen"))
    r.step("wait screenshare modal", "wait",
           lambda: d.wait_for(
               "document.querySelector('#screenshare-modal') && "
               "document.querySelector('#screenshare-modal').classList.contains('active')",
               10, "#screenshare-modal.active"))
    r.step("choose desktop share", "click",
           lambda: d.click("#screen-option-desktop"))
    r.step("confirm screenshare", "click",
           lambda: d.click("#btn-confirm-screenshare"))
    r.check("share banner text",
            "Screen sharing active" in (txt(d, "#screen-share-banner") or ""),
            txt(d, "#screen-share-banner"))
    r.check("share banner visible", d.visible("#screen-share-banner"),
            "visible")
    r.step("stop screenshare", "click",
           lambda: d.click("#btn-stop-screenshare"))
    r.check("share banner hidden",
            has_class(d, "#screen-share-banner", "hidden"), "hidden")
    r.step("raise hand", "click", lambda: d.click("#btn-raise-hand"))
    r.check("hand raised class",
            has_class(d, "#hand-raise-indicator", "raised"), "raised")
    r.check("hand raised text",
            txt(d, "#hand-raise-indicator") == "Hand Raised",
            txt(d, "#hand-raise-indicator"))
    r.step("open chat", "click", lambda: d.click("#btn-open-chat"))
    r.check("chat sidebar open", has_class(d, "#chat-sidebar", "open"),
            "open")
    r.step("type chat message", "type",
           lambda: d.type_text("#input-chat-message", "Ready for updates"))
    r.step("send chat", "click", lambda: d.click("#btn-send-chat"))
    r.check("chat message recorded",
            "Ready for updates" in (txt(d, "#chat-message-list") or ""),
            txt(d, "#chat-message-list"))
    r.step("leave meeting", "click", lambda: d.click("#btn-leave-meeting"))
    r.check("disconnected", txt(d, "#call-status-badge") == "Disconnected",
            txt(d, "#call-status-badge"))
    r.check("rejoin prompt visible", d.visible("#rejoin-prompt-panel"),
            "visible")
    r.step("rejoin meeting", "click", lambda: d.click("#btn-rejoin-meeting"))
    r.check("connected again", txt(d, "#call-status-badge") == "Connected",
            txt(d, "#call-status-badge"))
    r.check("4 participants again", txt(d, "#participant-count") == "4",
            txt(d, "#participant-count"))
    r.step("save call summary", "click",
           lambda: d.click("#btn-save-call-summary"))
    r.check("summary toast",
            "Meeting Sprint Planning: 4 participants, audio active, video active"
            in (txt(d, "#call-summary-toast") or ""),
            txt(d, "#call-summary-toast"))
    final_verify(r, d, "06")


def run_07(r, d):
    open_fixture(r, d, "test-07-file-manager.html", "07")
    r.check("total files 8", txt(d, "#total-files-count") == "8",
            txt(d, "#total-files-count"))
    r.check("selected 0 at start", txt(d, "#selected-files-count") == "0",
            txt(d, "#selected-files-count"))
    for img in ("img1", "img2", "img3", "img4", "img5"):
        r.step(f"select {img}", "click",
               lambda i=img: d.click(f"#checkbox-file-{i}"))
    # PINNED intermediate check (C2 F4): the ported final verify
    # does NOT assert the selected count, so this check is the only
    # coverage of the 5-file selection.
    r.check("selected 5 files", txt(d, "#selected-files-count") == "5",
            txt(d, "#selected-files-count"))
    r.step("open bulk rename", "click",
           lambda: d.click("#btn-open-bulk-rename"))
    r.step("wait bulk rename modal", "wait",
           lambda: d.wait_for(
               "document.querySelector('#bulk-rename-modal') && "
               "document.querySelector('#bulk-rename-modal').classList.contains('active')",
               10, "#bulk-rename-modal.active"))
    r.step("type rename pattern", "type",
           lambda: d.type_text("#input-rename-pattern", "photo-2026-##"))
    r.step("apply bulk rename", "click",
           lambda: d.click("#btn-apply-bulk-rename"))
    r.check("file 1 renamed",
            txt(d, "#file-name-img1") == "photo-2026-01.jpg",
            txt(d, "#file-name-img1"))
    r.check("file 5 renamed",
            txt(d, "#file-name-img5") == "photo-2026-05.jpg",
            txt(d, "#file-name-img5"))
    # WARNING (Y7 doubt 3): the move set is EXACTLY img1-3. A Root 6
    # toast means the move set was wrong, not the fix.
    for img in ("img1", "img2", "img3"):
        r.step(f"select {img} for move", "click",
               lambda i=img: d.click(f"#checkbox-file-{i}"))
    r.step("open move dialog", "click",
           lambda: d.click("#btn-open-move-dialog"))
    r.step("wait move modal", "wait",
           lambda: d.wait_for(
               "document.querySelector('#move-modal') && "
               "document.querySelector('#move-modal').classList.contains('active')",
               10, "#move-modal.active"))
    r.step("pick Archive target", "click",
           lambda: d.click("#move-target-archive"))
    r.step("confirm move", "click", lambda: d.click("#btn-confirm-move"))
    r.check("archive has 3 files",
            "3 files" in (txt(d, "#folder-count-archive") or ""),
            txt(d, "#folder-count-archive"))
    r.step("mistake: delete img4", "click",
           lambda: d.click("#btn-delete-file-img4"))
    # HOLE-CLOSERS (C2 F4, Redteam A14): without these two checks,
    # skipping the delete+restore steps would still pass the final
    # verify, because the fixture has no restore marker.
    r.check("row img4 hidden after delete",
            has_class(d, "#file-row-img4", "hidden"), "hidden")
    r.check("trash counter 1", txt(d, "#trash-counter") == "1",
            txt(d, "#trash-counter"))
    r.step("open trash folder", "click",
           lambda: d.click("#nav-folder-trash"))
    r.check("trash table visible", d.visible("#trash-table"), "visible")
    r.check("trash row img4 present in trash table",
            _child_in(d, "#trash-table", "#trash-row-img4"),
            "present in #trash-table")
    r.step("restore img4", "click",
           lambda: d.click("#btn-restore-file-img4"))
    r.check("trash counter 0 after restore",
            txt(d, "#trash-counter") == "0", txt(d, "#trash-counter"))
    r.step("back to root folder", "click",
           lambda: d.click("#nav-folder-root"))
    r.step("open new folder modal", "click",
           lambda: d.click("#btn-new-folder"))
    r.step("wait new folder modal", "wait",
           lambda: d.wait_for(
               "document.querySelector('#new-folder-modal') && "
               "document.querySelector('#new-folder-modal').classList.contains('active')",
               10, "#new-folder-modal.active"))
    r.step("type folder name Processed", "type",
           lambda: d.type_text("#input-new-folder-name", "Processed"))
    r.step("confirm create folder", "click",
           lambda: d.click("#btn-confirm-create-folder"))
    r.step("generate inventory report", "click",
           lambda: d.click("#btn-generate-inventory-report"))
    r.check("inventory toast",
            "Root: 5 files, Archive: 3 files, Trash: 0 files, Folder Processed created"
            in (txt(d, "#inventory-summary-toast") or ""),
            txt(d, "#inventory-summary-toast"))
    final_verify(r, d, "07")


def run_08(r, d):
    open_fixture(r, d, "test-08-devtools.html", "08")
    r.check("panel collapsed at start",
            has_class(d, "#devtools-panel", "collapsed"), "collapsed")
    r.check("toggle says open",
            "Open DevTools" in (txt(d, "#devtools-toggle-btn") or ""),
            txt(d, "#devtools-toggle-btn"))
    r.step("open devtools", "click",
           lambda: d.click("#devtools-toggle-btn"))
    r.check("panel expanded", has_class(d, "#devtools-panel", "expanded"),
            "expanded")
    r.step("open console tab", "click", lambda: d.click("#tab-console"))
    r.check("console view visible", d.visible("#view-console"), "visible")
    r.check("log count 0", txt(d, "#console-log-count") == "0",
            txt(d, "#console-log-count"))
    r.step("type eval window.appVersion", "type",
           lambda: d.type_text("#input-console-eval", "window.appVersion"))
    r.step("evaluate", "click", lambda: d.click("#btn-eval-console"))
    r.check("output has version",
            "v2.4.1" in (txt(d, "#console-output-log") or ""),
            txt(d, "#console-output-log"))
    r.check("log count 1", txt(d, "#console-log-count") == "1",
            txt(d, "#console-log-count"))
    r.step("open network tab", "click", lambda: d.click("#tab-network"))
    r.check("network view visible", d.visible("#view-network"), "visible")
    r.check("network total 6", txt(d, "#network-total-count") == "6",
            txt(d, "#network-total-count"))
    r.step("type filter api", "type",
           lambda: d.type_text("#input-network-filter", "api"))
    r.step("apply filter", "click",
           lambda: d.click("#btn-apply-network-filter"))
    r.check("visible count 3", txt(d, "#network-visible-count") == "3",
            txt(d, "#network-visible-count"))
    r.check("users row visible", d.visible("#row-req-api-users"), "visible")
    r.check("checkout row visible", d.visible("#row-req-api-checkout"),
            "visible")
    # P rule: click <td> never <tr>. The fixture handler sits on the
    # tr itself (line 273), so a td click bubbles to it. Scroll the
    # row into view first: click_el does not scroll, while every
    # other click goes through d.click, which does (C1 re-review F8
    # / Redteam re-review N7).
    r.step("inspect checkout row (first td)", "click",
           lambda: (d.scroll_into_view("#row-req-api-checkout"),
                    d.click_el(d.find_in(
                        d.find("#row-req-api-checkout"), "td"))))
    r.check("detail pane open",
            has_class(d, "#request-detail-pane", "open"), "open")
    r.check("status 404",
            txt(d, "#detail-status-code") == "404 Not Found",
            txt(d, "#detail-status-code"))
    r.step("open response tab", "click",
           lambda: d.click("#tab-detail-response"))
    r.check("response body",
            "endpoint deprecated" in (txt(d, "#detail-response-body") or ""),
            txt(d, "#detail-response-body"))
    r.step("close detail pane", "click",
           lambda: d.click("#btn-close-detail"))
    r.check("detail pane closed",
            has_class(d, "#request-detail-pane", "closed"), "closed")
    r.step("back to console tab", "click", lambda: d.click("#tab-console"))
    r.check("console view visible again", d.visible("#view-console"),
            "visible")
    r.step("mistake: clear console", "click",
           lambda: d.click("#btn-clear-console"))
    r.check("log count 0 after clear",
            txt(d, "#console-log-count") == "0",
            txt(d, "#console-log-count"))
    r.check("output empty after clear",
            norm(txt(d, "#console-output-log")) == "",
            txt(d, "#console-output-log"))
    r.step("type eval console.log ready", "type",
           lambda: d.type_text("#input-console-eval", "console.log('ready')"))
    r.step("evaluate again", "click", lambda: d.click("#btn-eval-console"))
    r.check("log count 1 again", txt(d, "#console-log-count") == "1",
            txt(d, "#console-log-count"))
    r.step("back to network tab", "click", lambda: d.click("#tab-network"))
    r.check("visible count still 3",
            txt(d, "#network-visible-count") == "3",
            txt(d, "#network-visible-count"))
    r.step("save devtools report", "click",
           lambda: d.click("#btn-save-devtools-report"))
    r.check("summary toast",
            "DevTools diagnostics: 1 logs, 3 filtered network rows, error 404 checked"
            in (txt(d, "#devtools-toast-summary") or ""),
            txt(d, "#devtools-toast-summary"))
    final_verify(r, d, "08")


def run_09(r, d):
    open_fixture(r, d, "test-09-notes-sync.html", "09")
    r.check("total notes 2 at start",
            txt(d, "#notes-total-counter") == "2",
            txt(d, "#notes-total-counter"))
    r.check("sync status",
            "Synchronized" in (txt(d, "#sync-status-indicator") or ""),
            txt(d, "#sync-status-indicator"))
    r.step("create new note", "click",
           lambda: d.click("#btn-create-new-note"))
    r.check("new title untitled",
            d.value("#note-editor-title") == "Untitled Note",
            d.value("#note-editor-title"))
    r.step("type title Shopping", "type",
           lambda: d.type_text("#note-editor-title", "Shopping"))
    r.step("type body Milk Eggs Bread", "type",
           lambda: d.type_text("#note-editor-body", "Milk, Eggs, Bread"))
    # This save MUST use the rename branch: title 'Shopping' with a
    # generated active id creates the 'shopping' key. The precise
    # rule is: never save titled 'Shopping' while the ARCHIVED note
    # is active. No save happens after the archived note is selected.
    r.step("save initial note", "click",
           lambda: d.click("#btn-save-note-edit"))
    r.check("total notes 3", txt(d, "#notes-total-counter") == "3",
            txt(d, "#notes-total-counter"))
    r.check("shopping title present",
            txt(d, "#note-item-title-shopping") == "Shopping",
            txt(d, "#note-item-title-shopping"))
    r.step("switch to device A", "click", lambda: d.click("#tab-device-a"))
    # Step 10 APPENDS ", Apples": type_text clears first, so read
    # the current value, ASSERT it, then type the full text.
    cur = r.step("read current body", "value",
                 lambda: d.value("#note-editor-body"))
    r.check("body is Milk Eggs Bread before append",
            cur == "Milk, Eggs, Bread", cur)
    r.step("type full body with Apples", "type",
           lambda: d.type_text("#note-editor-body",
                               "Milk, Eggs, Bread, Apples"))
    r.step("stage device A", "click",
           lambda: d.click("#btn-stage-device-a"))
    r.check("device A draft ready",
            "Draft ready: Laptop" in (txt(d, "#device-a-status") or ""),
            txt(d, "#device-a-status"))
    r.step("switch to device B", "click", lambda: d.click("#tab-device-b"))
    r.step("type conflicting body", "type",
           lambda: d.type_text("#note-editor-body",
                               "Milk, Eggs, Bread, Bananas, Orange Juice"))
    r.step("stage device B", "click",
           lambda: d.click("#btn-stage-device-b"))
    r.check("device B draft ready",
            "Draft ready: Phone" in (txt(d, "#device-b-status") or ""),
            txt(d, "#device-b-status"))
    r.step("trigger cloud sync", "click",
           lambda: d.click("#btn-trigger-cloud-sync"))
    r.step("wait conflict modal", "wait",
           lambda: d.wait_for(
               "document.querySelector('#conflict-resolution-modal') && "
               "document.querySelector('#conflict-resolution-modal').classList.contains('active')",
               10, "#conflict-resolution-modal.active"))
    r.check("conflict modal active",
            has_class(d, "#conflict-resolution-modal", "active"), "active")
    r.check("conflict banner",
            "Sync conflict detected for note Shopping" in
            (txt(d, "#conflict-detected-banner") or ""),
            txt(d, "#conflict-detected-banner"))
    r.step("resolve keep both", "click",
           lambda: d.click("#btn-resolve-keep-both"))
    r.check("conflict modal closed",
            has_class(d, "#conflict-resolution-modal", "closed"), "closed")
    r.check("total notes 4", txt(d, "#notes-total-counter") == "4",
            txt(d, "#notes-total-counter"))
    r.check("conflict copy present", count(d, "#note-item-conflict-copy") == 1,
            count(d, "#note-item-conflict-copy"))
    r.step("open conflict copy", "click",
           lambda: d.click("#note-item-conflict-copy"))
    r.check("editor title is conflict copy",
            "Shopping (Conflict Copy)" in
            (d.value("#note-editor-title") or ""),
            d.value("#note-editor-title"))
    r.step("rename to Phone Copy", "type",
           lambda: d.type_text("#note-editor-title", "Shopping - Phone Copy"))
    r.step("save renamed copy", "click",
           lambda: d.click("#btn-save-note-edit"))
    r.check("conflict title renamed",
            txt(d, "#note-item-title-conflict") == "Shopping - Phone Copy",
            txt(d, "#note-item-title-conflict"))
    r.step("select archived draft", "click",
           lambda: d.click("#note-item-archived-draft"))
    r.step("delete archived draft", "click",
           lambda: d.click("#btn-delete-active-note"))
    r.check("total notes 3 again", txt(d, "#notes-total-counter") == "3",
            txt(d, "#notes-total-counter"))
    r.step("view primary note", "click",
           lambda: d.click("#note-item-title-shopping"))
    # PINNED step 33 (C2 F4): the only check that catches the
    # rename-branch bypass off-spec.
    body = r.step("read primary body", "value",
                  lambda: d.value("#note-editor-body"))
    r.check("primary body has Apples",
            "Milk, Eggs, Bread, Apples" in (body or ""), body)
    r.step("finalize sync report", "click",
           lambda: d.click("#btn-finalize-sync-report"))
    r.check("sync toast",
            "Sync completed: 3 notes active, Shopping and Shopping - Phone Copy verified"
            in (txt(d, "#sync-summary-toast") or ""),
            txt(d, "#sync-summary-toast"))
    final_verify(r, d, "09")


def run_10(r, d):
    open_fixture(r, d, "test-10-ide-debug.html", "10")
    r.check("debugger inactive",
            txt(d, "#debug-state-badge") == "Inactive",
            txt(d, "#debug-state-badge"))
    r.check("no file at start", txt(d, "#active-file-name") == "None",
            txt(d, "#active-file-name"))
    r.step("open app.js", "click", lambda: d.click("#file-item-app-js"))
    r.check("active file app.js", txt(d, "#active-file-name") == "app.js",
            txt(d, "#active-file-name"))
    r.check("code editor visible", d.visible("#code-editor"), "visible")
    r.step("breakpoint line 12", "click",
           lambda: d.click("#gutter-line-12"))
    r.check("line 12 has breakpoint",
            has_class(d, "#gutter-line-12", "has-breakpoint"),
            "has-breakpoint")
    r.check("breakpoint count 1",
            txt(d, "#breakpoint-count-indicator") == "1",
            txt(d, "#breakpoint-count-indicator"))
    r.step("start debugger", "click",
           lambda: d.click("#btn-start-debugger"))
    r.check("debugger paused", txt(d, "#debug-state-badge") == "Paused",
            txt(d, "#debug-state-badge"))
    r.check("stack has calculateSum line 12",
            "calculateSum (line 12)" in (txt(d, "#call-stack-list") or ""),
            txt(d, "#call-stack-list"))
    r.step("step over 1", "click", lambda: d.click("#btn-step-over"))
    r.check("paused line 13", txt(d, "#current-paused-line") == "Line 13",
            txt(d, "#current-paused-line"))
    r.step("step over 2", "click", lambda: d.click("#btn-step-over"))
    r.check("paused line 14", txt(d, "#current-paused-line") == "Line 14",
            txt(d, "#current-paused-line"))
    r.check("watch total 120", txt(d, "#watch-val-total") == "120",
            txt(d, "#watch-val-total"))
    # Spec step 15 (click #input-edit-watch-total) is SKIPPED: the
    # fixture has that input display:none with no handler that
    # unhides it, and the simulator skips it too. A click_js on it
    # would be a no-op recorded as success, which the evidence
    # contract forbids. Recorded as a gap, never as a driven step.
    r.gap("step 15 click #input-edit-watch-total",
          "fixture gap: input display:none, no handler, simulator also skips it")
    r.step("open edit watch modal", "click",
           lambda: d.click("#btn-open-edit-watch"))
    r.step("wait edit watch modal", "wait",
           lambda: d.wait_for(
               "document.querySelector('#edit-watch-modal') && "
               "document.querySelector('#edit-watch-modal').classList.contains('active')",
               10, "#edit-watch-modal.active"))
    r.step("type override 250", "type",
           lambda: d.type_text("#input-watch-override-value", "250"))
    r.step("confirm watch override", "click",
           lambda: d.click("#btn-confirm-watch-override"))
    r.check("watch total 250", txt(d, "#watch-val-total") == "250",
            txt(d, "#watch-val-total"))
    r.step("breakpoint line 16", "click",
           lambda: d.click("#gutter-line-16"))
    r.check("line 16 has breakpoint",
            has_class(d, "#gutter-line-16", "has-breakpoint"),
            "has-breakpoint")
    r.check("breakpoint count 2",
            txt(d, "#breakpoint-count-indicator") == "2",
            txt(d, "#breakpoint-count-indicator"))
    r.step("continue debugger", "click",
           lambda: d.click("#btn-continue-debugger"))
    r.check("paused line 16", txt(d, "#current-paused-line") == "Line 16",
            txt(d, "#current-paused-line"))
    r.check("stack has renderSummary line 16",
            "renderSummary (line 16)" in (txt(d, "#call-stack-list") or ""),
            txt(d, "#call-stack-list"))
    r.check("watch grand total 250",
            txt(d, "#watch-val-grand-total") == "250",
            txt(d, "#watch-val-grand-total"))
    r.step("stop debugger", "click",
           lambda: d.click("#btn-stop-debugger"))
    r.check("debugger stopped", txt(d, "#debug-state-badge") == "Stopped",
            txt(d, "#debug-state-badge"))
    r.check("paused line none",
            txt(d, "#current-paused-line") == "None",
            txt(d, "#current-paused-line"))
    r.step("save debug session", "click",
           lambda: d.click("#btn-save-debug-session"))
    r.check("debug toast",
            "Debug session complete: watched total=250, breakpoints=2, final line 16"
            in (txt(d, "#debug-toast-summary") or ""),
            txt(d, "#debug-toast-summary"))
    final_verify(r, d, "10")


TESTS = {
    "01": run_01, "02": run_02, "03": run_03, "04": run_04,
    "05": run_05, "06": run_06, "07": run_07, "08": run_08,
    "09": run_09, "10": run_10,
}

FIXTURES = {
    "01": "test-01-tmux-session.html",
    "02": "test-02-network-settings.html",
    "03": "test-03-photo-editor.html",
    "04": "test-04-email-compose.html",
    "05": "test-05-spreadsheet-chart.html",
    "06": "test-06-video-call.html",
    "07": "test-07-file-manager.html",
    "08": "test-08-devtools.html",
    "09": "test-09-notes-sync.html",
    "10": "test-10-ide-debug.html",
}


# ---------------- server, bootstrap, preflight ----------------

def start_server():
    """Reuse a server already listening on our port, else start one.

    run_live.start_server only reuses when the clone1 fixture
    answers, so on this port it would try to bind 8769 twice and die
    with EADDRINUSE. Probe our own agy-y2 fixture first (Redteam
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
        wd = Y9WD()
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
            r = Y9Runner("bootstrap", base)
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


def preflight(base):
    """Fail-closed preflight (Y4b design). Raises RuntimeError on any
    failure; nothing proceeds to tab opening until it passes.

    Checks, in order: owner-away (explicit LIVE_OWNER_AWAY=1 AND a
    timestamped handover token, never inferred), Zen liveness (BiDi
    port 9222 + Marionette port 2828; the TCP connect proves the
    port listens, the session POST in WD.__enter__ is the real
    protocol probe), Hyprland IPC as a labeled SAFETY gate (not an
    incident detector), fixture server loopback, Y8 slot checks (Y8
    ports 4451 and 8767 must be FREE), stale-geckodriver sweep by
    PID file with parent check (kill only verified orphans),
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
    # Y8 slot checks (C3 F4): Y8's server (8767) and driver (4451)
    # must be FREE at launch. If either answers, Y8 is still alive
    # and this run must not start.
    for port, who in ((8767, "Y8 server"), (4451, "Y8 geckodriver")):
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
        if ppid is None:
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
    dest = Path(f"/tmp/worker-y9-gecko-{test_id}-a{attempt}.log")
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
    """SHIPPED.md contents (file, md5, source commit), best effort."""
    try:
        return Path(__file__).with_name("SHIPPED.md").read_text()
    except Exception:
        return None


def main():
    args = sys.argv[1:]
    if args == ["--verify-manifest"]:
        # Dry-run the B3 manifest check without driving anything:
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
        print(json.dumps({"suite": "agy-y2", "manifest_failed": True,
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
            print(json.dumps({"suite": "agy-y2",
                              "jsonl_rotation_failed": True,
                              "error": f"{type(exc).__name__}: {exc}",
                              "total": len(selected)}, ensure_ascii=False),
                  flush=True)
            return 2
    suite_t0 = time.perf_counter()
    _, base = start_server()
    print(f"serving at {base}", flush=True)
    # Prove the server serves the manifest bytes (redteam diff F3):
    # the reuse probe only checks a 200, never the served root.
    served_ok, served_checked, served_bad = _verify_served_files(base)
    if not served_ok:
        print(f"SERVED FILES FAILED: {served_bad}", flush=True)
        print(json.dumps({"suite": "agy-y2",
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
        print(json.dumps({"suite": "agy-y2", "preflight_failed": True,
                          "error": f"{type(exc).__name__}: {exc}",
                          "passed": 0, "flagged": 0, "failed": 0,
                          "hidden_body_encounters": 0,
                          "bootstrap_intervention": None, "gaps": [],
                          "total": len(selected)}, ensure_ascii=False),
              flush=True)
        return 2
    try:
        tab, boot_info = bootstrap_tab(base)
    except BootstrapError as exc:
        print(f"BOOTSTRAP FAILED {type(exc).__name__}: {exc}", flush=True)
        print(json.dumps({"suite": "agy-y2", "bootstrap_failed": True,
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
            r = Y9Runner(tid, base)
            r.attempt = attempt
            r.tab = tab
            try:
                wd = Y9WD()
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
            try:
                TESTS[tid](r, d)
            except IntegrityGuardError as exc:
                # Suite defect, not infra: no effect on the abort
                # counter, no re-run, suite continues (C2 F7 / C3 F6).
                guard_defect = True
                outcome = "guard-defect"
                r.failures.append(f"{type(exc).__name__}: {exc}")
                print(f"[{tid}] INTEGRITY GUARD: {exc}", flush=True)
            except Exception as exc:
                msg = str(exc)
                if msg.startswith("INFRA:"):
                    raised_infra = True
                    outcome = "infra-blocked"
                elif msg.startswith("FIXTURE-UNAVAILABLE"):
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
                    # FIXTURE_FAILURE and UNKNOWN stay live
                    # failures (no re-run, no infra count).
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
                        outcome = "fixture-unavailable"
                        r.failures.append(
                            f"fixture unavailable mid-test "
                            f"({cls}) after step failure: {exc}")
                        print(f"[{tid}] FIXTURE-UNAVAILABLE mid-test "
                              f"({cls})", flush=True)
                    elif (("timed out" in msg.lower()
                           or "timeout" in msg.lower())
                            and "timeout waiting for" not in msg):
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
                        d.switch(h)
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
            elif guard_defect:
                pass  # no effect on the abort counter
            elif outcome == "fixture-unavailable":
                pass  # suite/fixture defect, not infra: no effect
            else:
                infra_blocked = 0
            summary = r.summary()
            summary["flagged"] = bool(r.details.get("tz_hidden_removed"))
            summary["outcome"] = outcome
            summary["reattempted_from_infra"] = (attempt == 2)
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
    suite = {"suite": "agy-y2", "passed": passed,
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
             "total": len(results), "selected": len(selected),
             "total_ms": total_ms,
             "suite_wall_ms": round(
                 (time.perf_counter() - suite_t0) * 1000),
             "hidden_body_encounters": hidden_encounters,
             "tz_hidden_removed_any_attempt": tz_removed_any,
             "superseded_attempts": superseded,
             "bootstrap_intervention": boot_info,
             "gaps": all_gaps,
             "tracked_item": TRACKED_ITEM,
             "manifest": {"file": MANIFEST_NAME, "md5": manifest_md5,
                          "files_checked": manifest_checked},
             "metrics": {"wall_ms": total_ms,
                         "marionette_calls": _TOTAL_WD_CALLS["n"],
                         "marionette_calls_scope":
                             "all Y9WD sessions before suite JSON "
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
                     "run_agy_y2.py": _md5_of(__file__)},
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
    # Leave every shared test tab clean (about:blank) for the next runner.
    try:
        with Y9WD() as d:
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
