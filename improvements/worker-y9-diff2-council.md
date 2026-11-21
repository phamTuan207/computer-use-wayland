# Diff2 re-review: Worker Y9 agy-y2 runner fix diff 9d95f74 (council)

- Reviewer: Council diff2 re-reviewer (Y9 fix diff only)
- Date: 2026-11-21
- Reviewed diff: `git show 9d95f74` for `tests/realistic/run_agy_y2.py` (189 changed lines), `improvements/worker-y9-agy-y2-live-plan.md`, `improvements/worker-y9-agy-y2-live-log.md`. Parent is bab8d8a, not 2357a91 as the brief stated; the runner at the actual parent is still 2865 lines, so the count claims below are unaffected.
- Checked against: `improvements/worker-y9-diffreview-council.md` (fixes 1 and 2), `improvements/worker-y9-diffreview-redteam.md` (F1-F8), `tests/realistic/agy-y2-manifest.json` (uncommitted, regenerated), the shipped base `git show 1e3901c:tests/realistic/run_live.py`, and `tests/realistic/agy-y2/check.mjs`.
- Method: read-only code review, no Zen driving, no browser, no live tests, no commits. Every claim below carries a file plus line citation. Mechanical checks run by me on the VM, not assumed.
- Verdict: **GO WITH FIXES** (1 required fix, small, listed at the end; 2 nits)

## Mechanical checks I ran

- Line counts: `git show 9d95f74:tests/realistic/run_agy_y2.py | wc -l` is 2982; `git show 9d95f74^:tests/realistic/run_agy_y2.py | wc -l` is 2865. Both match the paperwork (see item 1).
- Manifest (uncommitted working tree): 26 files; runner entry md5 7d1abf2b2f995f748915be3641b8ed87 matches the working tree runner md5; manifest file md5 e1f4fe20d75d33ac507895dfb06a51f3. Both match the values in the task brief.
- Runner parses: `python3 -m py_compile tests/realistic/run_agy_y2.py` OK.
- No em dash, no en dash, and no banned input-automation tool string in the runner, the plan, or the log (grep, 0 hits).
- Ported verify untouched by this diff (no hunk touches `_VERIFY_JS`): the ported JS holds 89 raw `check(` matches including the `function check(` definition, so 88 real calls; `check.mjs` holds 89 raw including its definition, so 88 real calls. Counts match, as the task requires.

## Checklist

### 1. Council fix 1: line counts. PASS

- Plan `improvements/worker-y9-agy-y2-live-plan.md` line 167 says 2865 lines at 9564304; plan line 204 says 2982 lines after these fixes; log `improvements/worker-y9-agy-y2-live-log.md` line 56 says 2865 lines at 9564304 and 2982 lines after the diff-review fixes; log line 218 says 2517 to 2865 lines at 9564304. All four agree with the measured counts (2865 at the parent, 2982 at 9d95f74).
- The two remaining "2853" strings (plan line 181, log line 323) are inside correction narratives quoting the old wrong number in order to record its correction, not live claims. Same treatment the council diff review applied to the earlier log lines.
- Log line 56 cites "see addendum 6"; Addendum 6 exists at log line 313 ("Diff re-review verdicts in, merged fix list applied").

### 2. Council fix 2a: end-state screenshot skipped when the pre-screenshot switch fails. PASS

- `tests/realistic/run_agy_y2.py` lines 2827-2843: `shot = None` is set before the try; the try switches to `r.tab` if it is in `d.handles()`, else creates a sacrificial tab, registers it, and switches to it, then screenshots. Any exception in that block prints "pre-screenshot switch failed; skipping screenshot" and leaves `shot = None`, so lines 2844-2845 record no screenshot. The screenshot can no longer run on an uncontrolled current window through this path.
- Nit, not a fail: the except message says "switch failed" even when it is the `d.screenshot` call itself that raises. Behavior is correct (skip); only the wording is imprecise.

### 3. Council fix 2b / redteam F1: park fallback and DELETE skip. PASS

- `Y9WD._park_before_exit`, lines 425-471: returns True when the session is parked, False when no safe window could be established. Sacrificial `new_tab("about:blank")` is created at line 456, removed from `opened_tabs`, added to `_TEST_TABS` at line 461, and switched to at line 462. If that fails, the loop at lines 466-470 switches to a registered test tab from `_TEST_TABS` and returns True. If none is switchable, line 471 returns False. If there is no session at all, line 444-445 returns True.
- `Y9WD.__exit__`, lines 474-493: on `parked` False with a live session, lines 483-491 print the skip notice and set `self.session = None` before `super().__exit__()`. Base cleanup therefore skips DELETE /session.
- Base cleanup still terminates the proc and closes the log in that path: verified against the shipped base `git show 1e3901c:tests/realistic/run_live.py`, `_cleanup` lines 333-349. The `if self.session is not None:` block guards only the opened-tabs DELETE loop and the DELETE /session call; the proc terminate/wait/kill, the gecko log close, and the PID unlink run unconditionally after it. The commit message claim holds.
- Residual, accepted: dropping the session leaves the browser process alive with its tabs intact, and the comment (lines 487-490) says the preflight sweep can reclaim the driver slot. Preflight re-reads `/proc/<pid>/cmdline` before SIGTERM, so a stale driver PID is handled there. No user tab is closed by this path.

### 4. Redteam F2: manifest pinned, non-hex/null refused, entry loop guarded. PASS with one residual (Required fix 1)

- `EXPECTED_MANIFEST_FILES = 26`, lines 146-149.
- `_verify_manifest`, lines 278-317: line 297-299 refuses when `len(files) != 26`; the per-entry loop at lines 300-316 is wrapped in try/except; a non-string, non-32-char, or non-hex `md5` (including null) is recorded as a malformed entry and refused at lines 305-312, so the old null-md5 plus missing-file pass (None == None) is closed; a missing file gives `_md5_of` None, which never equals a 32-hex want.
- Residual: the top-level shape is unguarded. Line 297, `files = manifest.get("files", [])`, sits outside the try that only covers reading and parsing the manifest. A manifest whose JSON parses to a non-dict (for example a JSON list) raises AttributeError out of `_verify_manifest`, escaping `main()` with a traceback and no suite JSON. I confirmed the crash by simulating it (`json.loads('[1, 2]').get` raises AttributeError). The two stated F2(c) examples (rel None, non-dict entry) are fixed; the top-level case is the same class of hole one line further out. Required fix 1 below.

### 5. Redteam F3: served bytes verified over HTTP, main refuses on mismatch. PASS

- `_verify_served_files`, lines 323-351: reads the manifest next to the runner, fetches every listed file over HTTP at `f"{base}/{rel}"` with a 5 s timeout, compares md5s, returns ok, checked, mismatches.
- URL correctness: the server root is `SERVER_ROOT` from the shipped base (`run_live.py` line 50, `LIVE_SERVER_ROOT`, default `/tmp/worker-p-server`; the runner docstring line 66 launches with `/tmp/worker-y9-server`). The ship dir holds `run_agy_y2.py`, `run_live.py`, and `agy-y2/` at its top level, exactly the layout the manifest paths describe relative to the runner parent dir. So `f"{base}/{rel}"` hits the same layout the disk check verifies: `agy-y2/fixtures/test-01-tmux-session.html` serves from the ship `agy-y2/fixtures/` dir, and `run_agy_y2.py` serves from the ship top level. The base from `start_server` has no trailing slash, so no double slash. The fetch URL is correct.
- `main`, lines 2649-2661: the served check runs right after `start_server`, before preflight and before any driving. On failure it prints SERVED FILES FAILED plus a JSON line with `served_files_failed` and returns 2. A stale server on the port serving old fixture bytes can no longer pass the disk check silently.
- Observation, not a fail: `_verify_served_files` does not apply the F2 guards (no count pin, no hex validation), but any malformed entry still fails closed here (a null rel fetches a 404, a null want never equals a hex md5), so no hole follows from that.

### 6. Redteam F4: fixture-unavailable counted separately, still failed, still exit 1. PASS

- Suite JSON, lines 2917-2919: `"fixture_unavailable"` counts results whose outcome is `fixture-unavailable`.
- It still counts in failed: `"failed": len(results) - total_passed` at line 2912, and a fixture-unavailable summary has pass False, so it is inside failed. Exit rule at lines 2977-2978 returns 0 only when `total_passed == len(results)` and all selected tests ran, so a fixture-unavailable outcome still exits 1.
- Infra streak deliberately not reset: lines 2853-2856, `elif outcome == "fixture-unavailable": pass`, with the fail-safe rationale documented in the suite JSON comment (lines 2913-2916) and in the plan addendum. This is the documented resolution of redteam F4 (count separately, document the streak rule), not the reset alternative. Accepted as specified.

### 7. Redteam F5: check() JSONL write cannot fail a check. PASS

- `Y9Runner.check`, lines 545-568: `super().check` runs first at line 553, then the `log_step` call at lines 557-563 is wrapped in try/except, and a logging I/O error is printed at lines 564-566 ("check log failed (harmless)") and never raised. The original `ok` is returned at line 568. A disk-full JSONL can no longer turn a passing check into a test failure.

### 8. Redteam F7: bootstrap stall folded in, screenshot fallback tab registered. PASS

- Bootstrap stall: `bootstrap_tab` info dict gains `"stall_ms": 0` at lines 2298-2301; each attempt folds its runner stall at lines 2331-2332 (`info["stall_ms"] + getattr(r, "stall_ms", 0)`). Suite JSON folds it in at lines 2955-2957 (`stall_ms + boot_info.get("stall_ms", 0)`).
- Screenshot fallback tab: the finally-screenshot sacrificial tab is added to `_TEST_TABS` at line 2835, and the suite-end cleanup at lines 2965-2974 blanks every tab in `set(bootstrap_tabs) | _TEST_TABS`. The orphan-tab leak is closed for this path. The park sacrificial tab is likewise registered at line 461.
- Observation, not a demanded fix: the bootstrap fold at lines 2331-2332 runs only after `ensure_visible` returns. If `ensure_visible` itself raises on a failed bootstrap attempt, that attempt ladder time is lost from `info["stall_ms"]`. Metric undercount only, on an attempt that already failed; the success path and the not-ok path both fold correctly.

### 9. Redteam F8: socket context manager, run_02 single eval, run_live md5 path. PASS

- (a) Hyprland socket: lines 207-212 use `with socket.socket(...) as s:`, so the socket is closed on both the connect-success and connect-failure paths. The fd leak is closed.
- (b) run_02 paired check: lines 1440-1447 evaluate `_child_txt` once into `paired_txt` and use it for both the condition and the detail. The double-eval disagreement is gone.
- (c) Suite md5 record: lines 2951-2954 build the run_live.py path with `Path(__file__).with_name("run_live.py")`. A rename can no longer silently mislabel the runner md5 as the run_live md5.

### 10. Port verify untouched except the run_02 single-eval change. PASS

- The diff contains no hunk touching `_VERIFY_JS` or any driver step order. The only driver-line change is the run_02 paired check (item 9b), which is the required F8 change and is semantics-preserving (same child text, same "Paired" condition, evaluated once instead of twice).
- The exit rule (lines 2977-2978), the infra-only re-run rule, the two-consecutive-INFRA abort, and the counter resets are untouched. No other file in the runner changed beyond the hunks listed in items 2-9.
- The plan and log diffs are paperwork only: line-count corrections plus the new addendum recording this fix round. No code behavior rides in them.

## Required fixes (apply before any live driving)

1. Guard the manifest top-level shape in `_verify_manifest` (`tests/realistic/run_agy_y2.py`, line 297). A manifest whose JSON parses to a non-dict raises AttributeError out of the function and escapes `main()` with no suite JSON, which is exactly the crash F2(c) demanded be turned into a refusal. Add, before line 297, a check such as: if the parsed manifest is not a dict, return `(False, 0, ["manifest is not an object"], None)`. One guard, re-verify by reading the diff; no new live test needed.

## Nits (no fix demanded before launch)

- Plan line 180 says "19:2x on 21/11" where the log Addendum 6 (line 313) says 19:26 +07. Fill in the exact time so the two records agree.
- The finally-screenshot except message (lines 2840-2842) says "pre-screenshot switch failed" even when the screenshot call itself raises. Behavior is correct (skip); only the wording overclaims the cause.

## Verdict restated

GO WITH FIXES. Every claimed fix is present and correct in the diff with the citations above: counts, screenshot skip, park fallback with DELETE skip and intact proc/log cleanup, manifest pin and entry guards, served-bytes HTTP verification with a correct fetch URL, separate fixture-unavailable count with exit 1 preserved, wrapped check logging, bootstrap stall folding with fallback-tab registration, and all three F8 items. The port is still 88 of 88 and nothing else in the runner changed. Apply required fix 1 (one guard in `_verify_manifest`), then the runner is cleared for the live run.
