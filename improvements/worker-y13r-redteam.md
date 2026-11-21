# Redteam: Worker Y13 fixed runner diff (cb26d1d)

- Reviewer: Worker Y13r redteam (independent Muse reviewer)
- Date: 2026-11-21, work 20:19 to 20:33 +07 (about 14 min wall)
- Repo: ~/workspace/computer-use-wayland, branch todolist-push
- Commit under review: cb26d1d "Y13: adjudicate Council A + redteam re-review (BLOCK -> fixed); launcher + manifest regen"
- Parent (last reviewed state): bd89b62
- Scope: ONLY the diff cb26d1d^..cb26d1d. No code or test file was modified. This paper is the only file written.
- Method: every claimed hole reproduced mechanically on the VM (script + output below) or marked UNPROVEN. Original Council A / redteam findings against the old bytes were not re-litigated; only what cb26d1d added or changed was attacked.
- Sources read first: improvements/worker-y13-rereview-council-a.md, improvements/worker-y13-rereview-redteam.md, improvements/worker-y13-codex-y5-live-log.md (re-review + final gates sections).
- Probe scripts (scratch, not in repo): /tmp/y13r-b/t1_probe.py, t1b_probe.py, t3_probe.py, t3b_probe.py, t45_probe.py, forge_pyc.py, forge_pyc2.py. Staged ship copies: /tmp/y13r-b/ship-test, ship-a, ship-b, ship-c, ship-c2, ship-pyc, ship-sy, ship-sy2, ship-sy3. Synthetic marker repo: /tmp/y13r-b/marker-repo. The staged handover token /tmp/worker-y13-handover.json was backed up before the T2 probes and restored byte-identical after (md5 a44f3cda7c7a5e6a83c2e661bc6e62bb before and after).
- Note on fleet state: MEMORY.md was updated during this review (Y9b finished 10/10 PASS). That does not change any finding below; the T1 hole is about the launch form, not about Y9 being live right now.

## Verdict: BLOCK

Two independent BLOCKERS, each reproduced mechanically:

1. H1: the new M1 allowlist can be bypassed through its own `__pycache__` carve-out. Attacker bytecode for run_live.py executes while `--verify-manifest` reports manifest_ok true, exit 0. The manifest gate is the load-bearing ship-integrity check; it now passes a ship that runs code the manifest never saw.
2. H2+H3: the queue gate is blind to the exact rivals it was built to exclude. The process regex misses every bare-relative `run_*.py` launch (the documented launch form for Y9, Y4d, Y14, and Y13 itself), and it cannot see Y6c's nested run at all (name shape `run-nested-pill.py`). The Y6c marker check additionally false-accepts "harness complete" wording, body-line matches, and stale markers from any earlier run. Per plan v2 S3, for Y6c the process check + marker + go order are load-bearing because Y6c uses no TCP ports, so two of the three legs are weak at once.

Do not drive live until H1, H2, H3 are fixed and re-verified mechanically (forged-pyc refusal, bare-relative + Y6c-pill process refusal, strict marker tests).

## HIGH

### H1. Forged `__pycache__` bytecode executes past the new allowlist (manifest_ok true, exit 0)

- File + line: tests/realistic/run_codex_y5.py, `_verify_manifest` allowlist, line 406: `if rel.startswith("__pycache__/"): continue`. This skip is NEW in cb26d1d (part of the M1 fix).
- What was supposed to happen: redteam M1 asked that a planted file in the ship dir be refused, because the runner inserts the ship dir at sys.path[0] and a planted .py shadows stdlib. The fix refuses planted top-level .py files, but it skips `__pycache__/` entirely.
- The hole: CPython loads `__pycache__/run_live.cpython-312.pyc` instead of compiling `run_live.py` whenever the pyc header (magic, flags, mtime, source size) matches the source file's stat. mtime and size are public (readable from the source file), so an attacker who can write one file into the ship dir can forge a valid header for arbitrary bytecode. The manifest check only md5s .py sources, never the .pyc, and the allowlist skips the whole `__pycache__/` tree, so the forged bytecode is invisible to the gate and executes at import time.
- Reproduction (20:30 +07, 0.2 s): staged a copy of the real ship at /tmp/y13r-b/ship-pyc, forged `__pycache__/run_live.cpython-312.pyc` from the REAL run_live.py source plus a marker print (header mtime/size taken from the real source file's stat), then ran the gate:
  - Output line 1: `POISON-MARKER: attacker bytecode executed instead of run_live.py`
  - Output line 2: `{"manifest_ok": true, "files_checked": 27, "mismatches": [], "manifest_md5": "d3e71259dd7a5de3fab663534724428c"}`
  - Exit code: 0
  - A first attempt with a wrong header (missing the 4-byte flags field, 12-byte header) was correctly rejected by CPython and recompiled from source, which confirms the acceptance above is header validation passing, not a broken loader. Control import of a minimal payload (no real module names) also printed the marker, then failed only on the missing import names, which is expected.
- Why this matters: the attacker needs write access to the ship dir, but that is exactly the M1 threat model (a planted file surviving in /tmp/worker-y13-server). Modifying run_live.py itself IS caught by md5; the forged .pyc is the only route that changes executed code without changing any md5'd file. The skip exists because the runner's own import of run_live creates `__pycache__/run_live.cpython-312.pyc` before main() runs the check, so the check cannot simply refuse all .pyc files without also handling its own import.
- Concrete fix (tests/realistic/run_codex_y5.py, `_verify_manifest` + module top + tests/realistic/launch_y13.py env):
  - (a) Set `sys.dont_write_bytecode = True` at the very top of run_codex_y5.py, before the `from run_live import ...` line, and set `PYTHONDONTWRITEBYTECODE=1` in the launcher env, so no .pyc is ever written by this ship.
  - (b) Delete `__pycache__/` at ship time, and change line 406 from skip to refuse: any file under `__pycache__/` is a mismatch. Re-verify mechanically with the forge script above: the forged pyc must refuse with exit 2 and the marker must never print.
  - Alternative if (a) is refused: in `_verify_manifest`, recompile each manifest .py source and compare the marshalled code object against the cached .pyc instead of trusting the header.

### H2. Process-check regex misses the bare-relative launch form (Y9, Y4d, Y14, Y13 itself)

- File + line: tests/realistic/launch_y13.py line 72 `RUNNER_PATTERNS` first pattern `r"(^|/)run_[^/\s]*\.py"`, and the identical literal in tests/realistic/run_codex_y5.py line 3496 (preflight). Both are NEW in cb26d1d.
- The hole: /proc cmdlines are NUL-separated (`python3\0run_agy_y2.py\0all`). The pattern requires `run_` to sit at string start or right after `/`. In the bare-relative form it sits after a NUL byte, so there is no match. The `flock -c "..."` wrapper form is missed the same way (`python3 run_agy_y2.py` inside the -c string has a space before `run_`). The hand_drive_e1.py substring pattern is NOT affected (substring match works across separators).
- Reproduction (20:25 +07, 1.0 s), live processes scanned with the REAL imported patterns from launch_y13.py:
  - Unit, raw cmdlines: bare-relative Y9 `python3\0run_agy_y2.py\0all` match=False; bare-relative Y13 self match=False; bare-relative Y14 match=False; absolute path match=True; relative subdir `tests/realistic/run_agyq2.py` match=True; `./run_agy_y2.py` match=True; flock wrapper `flock\0-w\060\0...\0-c\0python3 run_agy_y2.py all` match=False; bare-relative E1 match=True; unrelated python match=False.
  - Live: dummy Y9 runner spawned bare-relative from its ship dir (pid 128910) MISSED; dummy Y14 runner spawned bare-relative (pid 128911) MISSED; same dummy spawned by absolute path (pid 128912) CAUGHT. Preflight literal extracted from run_codex_y5.py is byte-identical to the launcher pattern, so the preflight check misses the same forms.
- Why this matters: the bare-relative form IS the documented launch form. Y9 plan: `cd /tmp/worker-y9-server && ... flock -w 60 ... -c "python3 run_agy_y2.py all > ..."` (improvements/worker-y9-agy-y2-live-plan.md line 65). Y4d: `flock -w 1800 ... -c "cd /tmp/worker-y4-server && ... python3 run_agyq2.py all ..."` (improvements/worker-y4-run-log.md line 49). Y14: `python3 run_batch3.py all` (tests/realistic/run_batch3.py lines 33-35). Y13 itself: launch_y13.py execs `["flock", "-w", "60", LOCK, "python3", "run_codex_y5.py"]` with cwd=SHIP_DIR, bare-relative.
- What still catches a bare-relative rival (mitigations, verified by reading, not assumed): launcher own/predecessor port checks (Y9 8769/4449, Y8b 8767/4451, own 8771/4452) catch a rival whose server is bound; Y14 shares Y13's ports 8771/4452 (run_batch3.py lines 33, 1906-1907), so a live Y14 is caught by the own-ports check; the flock backstop (launcher takes flock -w 60 after the checks) makes a lock-holding rival fail loudly after a 60 s wait instead of launching silently; the geckodriver sweep catches a rival with a live geckodriver + live parent. The hole is the window the process check was built for: a rival alive but not yet bound / between arms / not holding the lock. For Y6c there is no port backstop at all (see H3).
- Concrete fix (launch_y13.py line 72 + run_codex_y5.py line 3496, same change in both): match the NUL/space-separated form, e.g. pattern `r"(^|[/\s\x00])run_[^/\s\x00]*\.py"` applied to the raw cmdline, or split the cmdline on NUL and match each argv token with `(^|/)run_[^/]*\.py$` plus a scan of the flock -c argument. Re-verify with the T1 probe: all three bare-relative dummies plus the flock-wrapper cmdline must be CAUGHT, unrelated python must stay uncaught.

### H3. The Y6c queue gate is blind twice over: process check cannot see the nested run, marker check false-accepts

- Files: launch_y13.py lines 69-73 (MARKER_RE, ABORT_RE), 161-190 (check_marker); run_codex_y5.py line 3496 (preflight pattern, same as H2).
- Part A, process check blind to Y6c (20:32 +07, 0.7 s): Y6c's nested run is `python3 run-nested-pill.py` (improvements/worker-y6b-nested-wayland-log.md line 25: `setsid nohup python3 run-nested-pill.py`), launched by `run-nested-wayland.sh`. The pattern needs the literal `run_` (underscore). `run-nested-pill.py` has a hyphen after `run`, so it never matches, bare-relative or absolute. Live probe: dummy pill spawned bare-relative (pid 139602) MISSED, absolute-path (pid 139603) MISSED. The nested Hyprland, mpv, and grim processes are not python `run_*.py` either. Plan v2 S3 states explicitly: "Y6c nested uses no TCP ports, so for Y6c the process check + marker + go order are load-bearing". The process leg contributes nothing for Y6c.
- Part B, marker false accepts (20:31 +07, synthetic repo, exact launcher `git log` commands): the launcher runs `git log origin/todolist-push --format=%H -E --grep=<pattern> -- improvements/worker-y6c-*.md`. Results on 8 synthetic commits:
  - Intended accepts, correct: `Y6c nested run DONE` matched completion; `Y6c: Wayland-nested verdict REPRODUCED` matched completion; `Y6c nested run ABORTED` matched abort only.
  - False accept 1: `Y6c nested harness complete, run starts now` MATCHED the completion pattern. A harness-ready commit (run not started) opens the gate.
  - False accept 2: subject `Fix flake` with BODY line `Y6c nested run DONE` MATCHED the completion pattern. `git log --grep` matches any line of the message, so the `^` anchor binds to a body line, not to the message start, despite the docstring saying "message ^Y6c...".
  - False accept 3 (staleness): the check takes ANY matching commit anywhere on todolist-push history, with no recency or ordering condition. A completion marker from an earlier finished Y6c run satisfies the gate forever, including after Y6c starts a new run or aborts one. Completion is also tried before abort, so once any historical completion commit exists the abort branch is unreachable.
  - Correct rejects (fail-closed, good): `Y6c nested run done` (lowercase) no match; `Fix Y6c nested run complete` (mid-message) no match; `Y6c nested run COMPLETE` (uppercase) no match.
- Concrete fix (launch_y13.py check_marker + MARKER_RE):
  - (a) Match against the SUBJECT only: fetch `git log --format=%H%x09%s` and apply the regex in Python to the subject field, not via `--grep`.
  - (b) Tighten the wording so prep is not completion: require a run token, e.g. `^Y6c.*nested.*run.*(DONE|complete|verdict|REPRODUCED)` and explicitly reject subjects containing `harness`.
  - (c) Add a freshness/ordering rule: the completion commit must be newer than the last abort commit on the branch (compare commit dates), or must fall inside the current queue window; if an abort commit is newer than the newest completion commit, refuse.
  - (d) Add the Y6c process names to the runner patterns: `run-nested-pill\.py` and `run-nested-wayland` (or a `y6-nested` / `run-nested` pattern). Re-verify with the T1b pill probe (both forms CAUGHT) and the marker repo (false accepts 1-3 all refuse, intended accepts still pass).

## MEDIUM

### M1. Wall-cap trip is NOT classified as the docstring claims: it can be reclassified INFRA and re-run

- File + line: tests/realistic/run_codex_y5.py `_check_wall_cap` lines 636-660 (docstring: "The raise is a plain RuntimeError, so main() classifies it as a live failure, never INFRA"); main() else-branch lines 3924-3941 (diagnose reclassification).
- The hole: `_check_wall_cap` raises a bare RuntimeError with message `wall cap exceeded: ...`, which carries no INFRA/FIXTURE/timeout marker, so the DIRECT classification is a live failure. But main() then runs diagnose_body on ANY step failure, and if the diagnosis is TZ_STUCK_V1 or OTHER_HIDDEN it reclassifies the SAME error to infra-blocked and earns a re-run. The docstring claim "never INFRA" is false whenever the tab happens to be hidden at trip time. The V1 trip rule the fix was supposed to implement (INFRA only if a WD call is outstanding or the browser is unresponsive, else live failure) is not implemented at all; classification is by tab-hidden state instead. Consequence: an over-cap test is reported infra-blocked (not failed), consumes a re-run that can never pass (attempt 2 offsets t0 by cumulative time, so its first primitive trips at once, proven in T4.5), and counts toward the two-consecutive-INFRA suite abort.
- Reproduction (20:28 +07, 0.3 s), real module import, fake Y13Runner with t0 400 s in the past (cap 360 s for test 01):
  - T4.1 direct step(): raw `RuntimeError: wall cap exceeded: 400s > 360s at primitive '99 cap trip'`, NOT wrapped as "step failed", failures list empty (the r.failures bypass the lead named is real on the direct path).
  - T4.2 direct check(): same raw raise.
  - T4.3 nested (cap trips inside a check() called from a step fn): wrapped as `step failed: 99 nested trip: RuntimeError: wall cap exceeded...` AND failures appended. So the bypass holds only on the direct path.
  - T4.4 classification predicate on the message: infra=False, fixture=False, wd-timeout=False, so live failure direct, but the diagnose branch at lines 3924-3941 can flip it to INFRA.
  - T4.5 attempt 2 with cumulative 400 s over the 360 s cap: first primitive raises at once.
- Concrete fix: tag the trip (a `WallCapExceeded` exception subclass, or a `WALL-CAP:` message prefix) and handle it in main() BEFORE the diagnose block: classify as live failure directly, never diagnose-reclassify, never re-run. Correct the docstring. Keep the cumulative attempt-2 trip (by design), but do not spend the re-run slot on it.

### M2. `_proven_no_body` ignores eval_error, contradicting its own docstring

- File + line: tests/realistic/run_codex_y5.py `_proven_no_body` lines 818-838. Docstring: "A transport error (eval_error present, or no snapshots at all) is NOT a proven no-body fixture". The code never reads `eval_error`.
- The hole: the state the docstring rules out is reachable through the REAL diagnose code. In run_live.py `_diagnose_body_impl`, if the first sample proves a no-body complete document and the SECOND sample eval then raises (hung driver on re-sample), it returns `{"classification": "FIXTURE_FAILURE", "snapshots": [snap1], "eval_error": "TimeoutError: ..."}`. `_proven_no_body` returns True on that diag, so the caller raises FIXTURE-UNAVAILABLE instead of INFRA. A hung driver mid-test is then reported as a bad fixture, earns no re-run, and does not count toward the infra streak. That is exactly the misattribution the H4 split was built to prevent.
- Reproduction (20:28 +07): synthetic cases all behaved as specified except 5c; then a fake driver (first eval returns no-body complete snapshot, second eval raises TimeoutError) run through the REAL `_diagnose_body_impl` returned classification FIXTURE_FAILURE with eval_error set and 1 snapshot, and `_proven_no_body` on that diag returned True.
- Concrete fix: in `_proven_no_body`, return False when `diag.get("eval_error")` is present (per the docstring), or at minimum when the error came from a sample eval. Also change `not s.get("hasBody")` to `s.get("hasBody") is False` (see L2). Re-verify with the T5 probe, case 5c must return False.

## LOW

### L1. Launcher `check_token` crashes with an uncaught traceback instead of refusing with exit 2

- File + line: tests/realistic/launch_y13.py `check_token` lines 118-135, line 126 `age = time.time() - float(tok.get("asserted_at_unix", 0))`.
- Reproduction (20:25 +07, real launcher binary, Y13_GO=1, token file doctored then restored byte-identical):
  - JSON list `["x"]`: `AttributeError: 'list' object has no attribute 'get'`, exit 1 (traceback).
  - JSON string `"hello"`: `AttributeError: 'str' object has no attribute 'get'`, exit 1.
  - `{"asserted_at_unix": "abc", "basis": "t"}`: `ValueError: could not convert string to float: 'abc'`, exit 1.
  - `{"basis": "t"}` (missing asserted_at_unix): correctly REFUSED with exit 2 (age huge, stale message).
- Impact: fail-closed (exit 1 still blocks the launch), but it violates the launcher's own contract ("any failure refuses with exit 2, never waits silently") and a downstream parser keying on exit 2 / "REFUSED" misreads a crash as an unknown failure. Note the RUNNER's `_check_handover` (run_codex_y5.py lines 251-280) wraps the float() in try/except and returns False, so only the launcher crashes.
- Concrete fix (launch_y13.py line 126): require `isinstance(tok, dict)` first, and wrap the float conversion in try/except, both routing to `_fail(...)`. Mirror the runner's handling.

### L2. `_proven_no_body` treats a missing hasBody key as proof of no-body

- File + line: run_codex_y5.py line 818-838, `not s.get("hasBody")` is True when the key is absent (None).
- Reproduction (20:28 +07): synthetic diag `{"snapshots": [{"readyState": "complete"}]}` (no hasBody key) returns True.
- Impact: none reachable today, because `_DIAG_JS` in run_live.py always sets `hasBody: !!b`, so a real snapshot always carries the key. The predicate is still wrong on its face: None is not False, and a future diagnose change emitting key-less snapshots would manufacture fixture-unavailable proofs. Fix with M2: use `s.get("hasBody") is False`.

### L3. F10 abort still drives the browser (suite-end tab cleanup) after the handover gate closed

- File + line: run_codex_y5.py lines 4120-4121 (break out), 4199-4215 (suite JSON print + tab cleanup), 4215-4216 (`if aborted_handover: return 2`).
- Verified: main() DOES return 2 on aborted_handover (it does not fall through to the 0/1 exit), and the partial suite JSON is printed first (total < selected, so a parser can tell it is partial). But before returning 2 it opens a fresh Y13WD() session and drives the shared browser (switch tabs, goto about:blank, screenshot) in the cleanup block. The F10 fix's own rationale is "a re-run must never drive without a live handover"; the cleanup drives after that gate closed. If the handover expired because the owner returned, the cleanup switches tabs in the owner's live browser.
- Concrete fix: skip the Y13WD cleanup block when `aborted_handover` is set (or gate it on a fresh `_check_handover()` pass). The partial suite JSON print can stay.

### L4. Session-creation-failure summaries lack `cumulative_elapsed_ms`

- File + line: run_codex_y5.py lines 3855-3870 (session-failure branch builds `s = r.summary()` and sets flagged/outcome/reattempted, then `break`s) vs lines 4082-4085 (cum_ms update + `summary["cumulative_elapsed_ms"]`, reached only on the normal path).
- Impact: the `cumulative_elapsed_ms` key is NEW in cb26d1d (M2 fix) and appears on every normal per-test summary but not on session-creation-failure summaries. A downstream parser expecting the key on every per-test summary breaks on exactly the failure path that most needs the timing. Fix: set `s["cumulative_elapsed_ms"]` (attempt elapsed, or 0) in the session-failure branch too.

### L5. Allowlist blind spot: non-manifest file inside an outside-pointing symlinked dir is invisible (exit 0)

- File + line: run_codex_y5.py `_verify_manifest` allowlist, `base_dir.rglob("*")` (Path.rglob does not descend into symlinked dirs).
- Reproduction (20:32 +07): staged ship with `codex-y5/extras` symlinked to /tmp/y13r-b/evilout containing planted.py: `--verify-manifest` returned manifest_ok true, exit 0. A symlinked FILE at a manifest path is refused separately by the path-containment check (`manifest path escapes ship dir`, proven in the sy3 case), and a symlinked dir REPLACING a manifest dir is refused the same way (proven in the c2 case).
- Impact: nil as far as this reviewer can establish. Nothing imports or serves a non-manifest file from such a directory (the runner imports run_live from the ship top; the HTTP server serves only manifest files, checked by `_verify_served_files`). Noted as a blind spot, not a live bypass. Fix if the allowlist is ever hardened: walk with `os.walk(followlinks=True)` and refuse any file whose resolved path is outside the ship dir or not in the allowlist.

### L6. Park F5 fix deviates from Council A's specified fix (warn + continue instead of fail)

- File + line: run_codex_y5.py `_park_before_exit` lines 536-550 (new removal loop before the close loop).
- Council A F5 specified: at the top, if a registered tab is in opened_tabs, print PARK-FAILED loudly and return False (do not close it, do not proceed). The cb26d1d fix instead prints a `[park] WARNING`, removes the handle, and proceeds with the close loop and session delete. The actual tab-deletion bug IS fixed (the removal now happens before the close loop, where it was previously dead code after the reset), so this is a deviation, not a live hole. But a bookkeeping bug is now silently repaired mid-park with only a stdout warning and no structured trace (nothing in JSON/JSONL records that the invariant fired).
- Concrete fix: record the event in `r.details` / the suite JSON (or implement the specified return False). At minimum keep the warning text.

### L7. Launcher + preflight do not check Y4d ports 8768/4448 (or 8770/4450)

- Files: launch_y13.py PREDECESSOR_PORTS = (8769, 4449, 8767, 4451); run_codex_y5.py preflight predecessor check (same two pairs, per Council A verified-clean).
- The fleet's newer standard is wider: Y14's launch gate checks predecessor ports 8767-8770/4448-4451 (run_batch3.py line 1949), which includes Y4d 8768/4448. Y13's plan S3 names only Y9/Y8b, so the launcher matches its plan; this is a gap against the newer sibling gate, not a plan deviation. Mitigated by flock (Y4d launches under flock) and by H2's fix (a Y4d process check that works would catch it regardless of ports). Fix: add 8768, 4448, 8770, 4450 to both port lists.

## Killed leads (tested, no hole)

- T1 (partial): absolute-path, relative-subdir, and `./` launches ARE caught by the regex. Only bare-relative and flock -c forms are missed (H2).
- T2 (partial): missing asserted_at_unix refuses correctly with exit 2. Only non-dict JSON and non-numeric asserted_at_unix crash (L1).
- T3 ancestry loop: deep fork chain (depth 14, 20:27 +07) terminates in 0.00 s with the full 18-pid set; orphan reparented to pid 1 terminates with size 1; absolute-path runner as descendant is FLAGGED (correct, descendants are not excluded); absolute-path runner as ancestor is EXCLUDED (correct). No termination or exclusion defect.
- T5a/5d/5e/5f: canonical proof returns True; empty snapshots + eval_error returns False (INFRA, confirmed); not-complete returns False; contradictory snapshots return False. All correct.
- T6 reload marker: ordering is marker-set, click, wait_ready, 1.0 s settle, ensure_visible ladder, THEN marker check (run_codex_y5.py _reload_settings lines 2918-2990), so the check runs after the new realm is ready, not before. Fixture grep over tests/realistic/codex-y5/ finds no `__y13_reload_probe` string, so no name collision. A raising marker-check eval propagates out of _reload_settings uncaught and fails the step closed (no false pass). Residual risk is a false FAILURE on a slow navigation (marker eval hitting the old realm), which is fail-closed and UNPROVEN without live driving.
- T7a: nested `codex-y5/__pycache__/x.pyc` is REFUSED with exit 2 (20:29 +07), and correctly so: no legitimate nested `__pycache__` can appear, because the only .py under codex-y5/ is check-dashes.py, a standalone script never imported by the runner or launcher.
- T7b: top-level planted `evil.py` REFUSED with exit 2 (20:29 +07).
- T7c: tampered manifest-listed file (same name, different bytes) caught by md5, exit 2 (20:29 +07).
- T7 symlink file at a manifest path: refused via path containment (`manifest path escapes ship dir`, 20:32 +07).
- T8 cumulative cap: the cum_ms update (lines 4082-4085) runs BEFORE the infra-blocked `continue` (line 4098), so an infra re-run measures cumulative time; the session-creation-failure path `break`s out of the attempt loop on both branches (lines 3867-3870), so no attempt 2 exists and no fresh budget is granted there. No hole. Only L4 (missing key on that path) remains.
- T9 (partial): abort commit matches ABORT_RE only; lowercase `done`, mid-message `Fix Y6c ...`, and uppercase `COMPLETE` are all correctly rejected. Only the three false accepts in H3 are holes.
- T10: EXPECTED_MANIFEST_FILES 27 equals the manifest's 27 entries; staged `--verify-manifest` on the real ship exits 0 with manifest md5 d3e71259dd7a5de3fab663534724428c, matching the commit message; ports 8771/4452 match the plan (lines 194-195, 406); M7 server_failed JSON keys are IDENTICAL to the preflight_failed JSON keys (10 keys each, same set, extracted mechanically from the source); handover path and 4 h TTL are identical in launcher and runner (/tmp/worker-y13-handover.json); F10 returns 2 (see L3 for the cleanup caveat).
- Spot checks on other new lines: F8 timeout narrowing implements exactly the pinned wording; M3 substring match covers the wrapped form; M4 outcome fix sits before the audit block; M6 sha256 fingerprint is computed on the raw file bytes; the park removal loop now runs before the close loop (L6 deviation aside).

## Out of scope notes (not counted as findings)

- The jsonl_rotation_failed and served_files_failed structured JSONs have only 4 keys (missing passed/flagged/failed/hidden_body_encounters/bootstrap_intervention/gaps), unlike the 10-key preflight/server_failed shapes. Both predate cb26d1d and were not changed by it, so they are not re-litigated here. Flagging for the parent only: if a downstream parser requires the 10-key shape on every structured failure, those two older paths will break it too.
- No live driving was done (no Zen, no laptop access from this VM for driving). The T4/T5/T7/T9 reproductions use the real module code with fake drivers or staged ships, which is sufficient for the claims made.

## Required fixes before any live driving (in order)

1. H1: stop trusting `__pycache__` (dont_write_bytecode + refuse any .pyc at verify time); re-run the forge script and require exit 2 with no marker printed.
2. H2: fix the process regex in BOTH files to match NUL/space-separated bare-relative forms and the flock -c form; re-run the T1 probe (all bare-relative dummies CAUGHT).
3. H3: add Y6c process names to the patterns; match the marker against subjects only, tighten the wording, add a freshness/ordering rule; re-run the T1b pill probe and the marker repo cases.
4. M1: tag wall-cap trips and classify them before diagnose, never re-run; fix the docstring.
5. M2 + L2: `_proven_no_body` returns False on eval_error and requires `hasBody is False`.
6. L1, L3, L4, L6, L7 as specified above.
7. Re-run the full mechanical set: staged `--verify-manifest` exit 0 on the clean ship, forged-pyc refusal, negative manifest cases, T1/T1b/T3/T4/T5 probes, marker repo cases.
