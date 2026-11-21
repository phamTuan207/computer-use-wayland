# Council Member 1 re-review: Worker Y9 agy-y2 live-run runner (harness correctness only)

- Reviewer: Council Member 1 (scope: harness correctness only)
- Date: 2026-11-21
- Reviewed: `tests/realistic/run_agy_y2.py` as committed in a82bb41 (2517 lines, read from `git show a82bb41:tests/realistic/run_agy_y2.py`), checked against `improvements/worker-y9-agy-y2-live-plan.md` (plan v2), `improvements/worker-y9-step-mapping.md` (670 lines), `improvements/worker-y9-council-1.md`, `improvements/worker-y9-council-2.md`, `improvements/worker-y9-council-3.md`, `improvements/worker-y9-redteam.md`, `tests/realistic/agy-y2/check.mjs`, `tests/realistic/agy-y2/simulate.mjs`, the 10 spec files, and the fixtures cited below
- Method: read-only code review. No Zen driving, no browser, no live tests, no commits. Line numbers below are lines of the committed runner unless stated otherwise. Two mechanical checks were run: a check-by-check diff of the ported verify against check.mjs (88 checks), and `node --check` on the runtime value of the ported JS.
- Verdict: **GO WITH FIXES**

## Why GO WITH FIXES, in one paragraph

The runner the first round demanded now exists in code, and almost every fix the first round demanded is really in it, verified line by line below: the 10 drivers follow the mapping tables, the ported verify is a faithful 88 of 88 transcription, M11 and M12 are implemented, the flagged-pass rule, the abort rule, the 8 second ladder, the fresh-tab-only bootstrap, the integrity guard, the mid-test hidden-body rule, the one re-run rule, the JSONL rotation, the per-test screenshots, and the exit rule are all present. The fixes required before live driving are small and enumerated as F1 to F8. The largest one is not in the runner file at all: the runner cannot even be imported against the run_live.py committed at a82bb41, because that file has no diagnose_body and its goto, refresh, and new_tab reject the allow_hidden keyword the runner passes everywhere. The fixes the runner depends on landed later, in 1e3901c, which is on the branch now, so the run is shippable, but only from a named base with recorded md5s and a laptop-side import smoke test (F2). The other code fixes are a missing check() override that leaves every intermediate check out of the JSONL (F1), a post-removal fixture-failure hole (F3), two classification gaps (F4, F5), a misdefined stall metric (F6), a dropped attempt-1 summary plus two doc errors (F7), and two minor items (F8).

## Mechanical checks (run, not assumed)

- Ported verify diff: extracted every `check(...)` call from check.mjs verifyTest and from the runner `_VERIFY_JS` (lines 584 to 840) and compared normalized condition plus message. Result: 88 checks in check.mjs, 88 in the port, 0 differences, 0 missing, 0 extra. Counts per test: 01: 8, 02: 11, 03: 11, 04: 7, 05: 12, 06: 9, 07: 8, 08: 8, 09: 6, 10: 8. The two read-but-never-asserted values are read in both (terminalOutput in the 01 block, selectedCount in the 07 block) and asserted in neither, matching check.mjs exactly. The commit message says 87 assertions; the true count is 88. Trivial, see F7.
- JS syntax: extracted the runtime value of `_VERIFY_JS` (after Python string parsing, so the `join('\n')` escape is the value Marionette would receive) and ran `node --check` on it. Result: parses OK. The feared Python-escape breakage does not exist: the file carries `\\n` in source, which parses to backslash plus n, which is the correct JS newline escape.
- The runner itself parses clean (`ast.parse` OK).
- Fixture spot check for the test-01 scoping fix: `fixtures/test-01-tmux-session.html` line 196 sets `pane.className = 'pane'`, so `_active_pane_type` (line 967) and `_active_pane_click_send` (line 987) using `closest('.pane')` resolve. The duplicate-id scoping is sound, not luck.

## Q1. Do the 10 drivers follow simulate.mjs step for step, per the mapping tables?

Yes, with three deviations, one of which is the mapping table being wrong and the runner being right.

- test-01 (run_01, lines 1000 to 1089): all 35 mapping rows present in order. The uptime check is pinned at lines 1038 to 1040 (`#pane-active-output` contains `load average: 0.18, 0.22, 0.15`), with the comment that the final verify does not cover it. Typing and send are scoped to the active pane (lines 1032 to 1035) instead of the simulator bare duplicate ids (simulate.mjs lines 46 to 47); that is the decided Redteam A9 fix, and the fixture proves it. The overview check uses `d.visible("#session-overview")` (line 1078), which checks computed display plus rect, so it satisfies M3 (display block, not presence). One equivalence: mapping step 20 says clear-and-type for the window name, the runner uses `type_text` (line 1057); equivalent because run_live `type_text` clears first.
- test-02 (run_02, lines 1090 to 1191): all 35 rows plus the unnumbered apply action present in order. M11 is implemented: apply click at line 1180, then the toast active check at line 1183 and the toast text check at line 1185. The metered, known-panel, and summary checks are all present.
- test-03 (run_03, lines 1192 to 1267): all 33 rows in order. Dialog dims uses contains `750 x 1000` (line 1247), matching check.mjs, per M5.
- test-04 (run_04, lines 1268 to 1362): all 33 rows in order. M10 is implemented: the reopened draft subject is read with `d.value` and checked at lines 1330 to 1332. The empty-list check uses whitespace-normalized text (lines 1340 to 1342).
- test-05 (run_05, lines 1363 to 1445): all 35 rows in order. M12 is implemented: after the render click (line 1417) the runner waits for `#chart-title-controls` display not none (lines 1421 to 1426) before the title click and type (lines 1427 to 1432). The Bar select is kept with the M14 note that it is outcome-irrelevant (lines 1410 to 1413). Two small deviations: mapping step 22 says click then clear then type for the B4 correction, the runner types without the prior click (line 1400); the simulator does click first (simulate.mjs lines 204 to 206). Low risk, since the input exists and send-keys focuses it, but the mapping row is not followed literally. Mapping steps 31 and 22 say clear-and-type; the runner uses `type_text`, which clears first, so those are equivalences, not deviations.
- test-06 (run_06, lines 1446 to 1536): all 35 rows in order, including the screenshare modal wait (lines 1485 to 1490), the banner text plus visible checks, the rejoin panel check, and the mic/cam class checks.
- test-07 (run_07, lines 1537 to 1625): all 35 rows in order. The move set is exactly img1 to img3 (lines 1569 to 1571). The selected-5 check is present (line 1549). The skip-hole closers are present: row hidden plus trash 1 (lines 1591 to 1595) and trash 0 after restore (lines 1602 to 1603).
- test-08 (run_08, lines 1626 to 1709): all 35 rows in order. The row click uses the first td inside the row (lines 1664 to 1667), with the bubbling justification in the comment (fixture handler on the tr). See F8 for the missing scroll step on that one click.
- test-09 (run_09, lines 1710 to 1818): all 35 rows in order. Step 10 reads the body, asserts it equals `Milk, Eggs, Bread` (lines 1741 to 1744), then types the full text `Milk, Eggs, Bread, Apples` (lines 1745 to 1747). Step 33 reads the primary body and checks it contains the pinned value (lines 1806 to 1809). The step 7 save uses the rename branch by construction (comment at lines 1731 to 1734), and no save happens after the archived note is selected.
- test-10 (run_10, lines 1819 to 1928): all rows except step 15, which is recorded as a gap (lines 1853 to 1859) via `r.gap`, never as a driven step. The watch override uses `type_text` (line 1865); equivalent to the simulator type-only step since the field starts empty.
- MAPPING TABLE ERROR (runner correct, table wrong): mapping test-09 step 10 prescribes `d.type_text('#note-editor-body', ', Apples')`. With `type_text` clearing first, that would leave the body as just `, Apples`. The runner correctly types the full text instead, following plan D6. The table row must be fixed to match the runner (F7). The same class of slip does not recur elsewhere: every other `type_text` in the drivers types a complete value or types into a field that starts empty.

## Q2. Are the first-round fixes really in the committed code?

Almost all of them are. Each item below names the code that proves it, or the gap.

### Bootstrap, fresh-tab-only with bounded retries: PRESENT

- `bootstrap_tab` (lines 1964 to 2043) tries up to 3 fresh tabs (`range(1, 4)`), each a `window/new` tab plus the full ladder with `allow_swap=False`, closes a failed tab and discards it from the registry, and raises `BootstrapError` after 3 failures. No handle scanning anywhere in it. The bootstrap handle is removed from `opened_tabs` before the session exits (lines 2034 to 2036, C1 R9). The intervention info dict defaults to no intervention (lines 1972 to 1974) and is returned with the handle.
- `rebootstrap_tab` (lines 366 to 423) is create-only: it iterates only `_TEST_TABS` (registered handles), diagnoses each under a guard that skips on failure (lines 376 to 382), and otherwise creates new tabs (lines 385 to 420). No `handles()` scan for discovery. New handles are removed from `opened_tabs` (line 390) and dropped from the registry plus closed explicitly when their diagnose raises (lines 396 to 405, C2 F8).

### Attempt fields: PRESENT for steps, ABSENT for checks (F1)

- Y9 `log_step` (lines 180 to 194) adds `"attempt": _CURRENT_ATTEMPT["n"]` to every record. `Y9Runner.step` (lines 300 to 315) uses it. `Y9Runner.summary` (lines 324 to 330) adds `attempt` and `gaps`. `main` sets `_CURRENT_ATTEMPT` before each attempt (line 2324) and `r.attempt` (line 2325).
- Gap: `Y9Runner` does NOT override `check()`. The inherited `Runner.check` (run_live.py lines 584 to 590, both at a82bb41 and at HEAD) only prints and appends failures; it never calls any `log_step`. Every `r.check()` in all 10 drivers therefore leaves no JSONL record at all, with no attempt field and no elapsed time. The four load-bearing intermediate checks (test-01 uptime, test-07 selected-5, test-07 hole closers, test-09 step 33) exist only as stdout prints. Stdout is captured to the stdout log, so the evidence is not lost entirely, but the JSONL cannot attribute checks to an attempt, which is exactly what Redteam A11 required the attempt field for. Fix F1.

### JSONL rotation: PRESENT

- `main` renames an existing JSONL to `.prev-<UTC timestamp>` at launch (lines 2277 to 2293), logs the rotation, and only appends if the rename itself fails. One file holds exactly one run under the normal path.

### Per-test screenshots: PRESENT

- The `finally` block in `main` screenshots to `/tmp/worker-y9-shots/{tid}-a{attempt}.png` while the session is alive (line 2413), stores the path in `r.details`, and a suite-end screenshot is taken in the cleanup session (line 2497). The screenshot helper (lines 276 to 290) is best effort and never raises.

### Integrity guard placement: PRESENT

- `open_fixture` (lines 853 to 943) runs the guard after the fresh load and before any action (lines 923 to 940), through the SAME `verify_test` used by `final_verify` (lines 944 to 966). The untouched failure list is recorded in `r.details["integrity_guard"]` and in the JSONL (lines 927 to 934). A pass on untouched raises `IntegrityGuardError` (line 936), which `main` catches as a suite defect (lines 2362 to 2370): failed, flagged False, suite continues, no effect on `infra_blocked`. The guard re-runs on any re-run because `open_fixture` runs per attempt.

### Mid-test hidden-body diagnose: PRESENT

- On any step failure, `main` diagnoses before classifying (lines 2376 to 2405): a non-VISIBLE classification reclassifies the failure to INFRA with a recorded reason. `refresh` diagnoses like `goto` in the current base (run_live.py line 478), so the Redteam A10 refresh gap is closed at the base level. The base level only holds for the post-1e3901c run_live.py; see F2.

### One-re-run-only-for-proven-infra: PRESENT

- The attempt loop is `(1, 2)` (line 2323). Only `outcome == "infra-blocked"` on attempt 1 continues to attempt 2 (lines 2434 to 2439). The summary carries `reattempted_from_infra` (line 2430). The first INFRA still counts toward `infra_blocked` (line 2421), and a successful re-run resets it (line 2426).

### Exit 0 iff clean plus flagged equals total: PRESENT

- `passed` counts clean only (line 2454), `flagged` counts passing flagged tests (line 2455), and the exit is `0 if total_passed == len(results) and len(results) == len(selected) else 1` (lines 2512 to 2514). No hardcoded 10. Guard defects, live failures, and early aborts all fail the exit test. The bootstrap-failure path returns 2 with suite JSON (lines 2299 to 2308).

### Flagged-pass rule (C2 F1, C2 O1, C3 F3, C1 R6): PRESENT

- The flag is set only after the post-remove snapshot proves the class is gone (lines 505 to 511: `removed = "tz-hidden" not in snapshots[-1] htmlClassList`, flag set only if removed). The removal eval also clears `--zen-logo-path` (lines 495 to 498). The intervention is logged with the verified flag and the snapshot (lines 512 to 524). `bootstrap_intervention` is propagated with schema `{"intervened", "tz_hidden_removed", "hidden_body_encounters", "detail"}` (lines 1972 to 1974, 2424 to 2426 in bootstrap; suite JSON lines 2460 to 2462), including on the bootstrap-failure path (lines 2301 to 2307), and bootstrap encounters are added to the suite total (line 2458). Every per-test summary carries `flagged`, including the session-failure path (line 2344). A flagged test still requires all PASS conditions, since `flagged` is only counted when `s["pass"]` is true (line 2455).

### Abort rule (C2 F4, C3 F2, C1 R7): PRESENT

- Session failures use only the separate `wd_failures` counter with its own two-consecutive abort (lines 2340 to 2357), reset to 0 after a successful session creation (line 2359). `infra_blocked` resets on pass, on non-INFRA failure, and on non-INFRA runner failure (lines 2421 to 2426). INFRA is matched with `startswith("INFRA:")` (line 2371), stricter than the old substring match. The two counters are kept distinct.

### 8 second ladder budget with phase gates (C2 F5, C1 R10): PRESENT, with one hole (F3)

- Deadline `t0 + 8.0` (line 461). Poll capped by `poll_end = min(deadline - 3.0, t0 + 2.0)` (line 476). Removal skipped when less than 1.1 seconds remain (line 489). Rebootstrap skipped when less than 2.0 seconds remain (line 528). Elapsed time against the budget is printed on every return path, including the VISIBLE early return (lines 466 to 470). The poll cadence docstring says about 3 samples in 2 seconds (lines 430 to 433).
- Hole (F3): after the removal eval, if the new diagnose is FIXTURE_FAILURE, the code falls through to `_log_diag` and then to rebootstrap (lines 525 to 540) instead of raising FIXTURE-UNAVAILABLE immediately. The poll loop and the initial diagnose do raise on FIXTURE_FAILURE (lines 472 and 485); the post-removal path is the one place that does not. A fixture with no body would burn tabs before failing.

### Preflight C3 F1, F3, F7, F8, F9 (C1 R2, R3): PRESENT in the runner copy

- F1: lock types accepted are POSIX, FLOCK, OFDLCK (line 2210), with the comment recording why POSIX-only fails a correct flock launch.
- F3: ppid None refuses instead of killing (lines 2146 to 2160), re-checking liveness first.
- F7: ppid parsed after the last `)` in `_ppid_of` (lines 120 to 131); the ancestor set starts with `os.getpid()` (line 2219).
- F8: unreadable PID files are unlinked and logged (lines 2126 to 2135).
- F9: Hyprland IPC is a labeled SAFETY gate with a 10 second timeout, never a bare call (lines 2092 to 2101), and the handover check logs that idle time was NOT independently verified (lines 2064 to 2067). Y8 slot checks are present: ports 8767 and 4451 must be free (lines 2113 to 2124). The preflight probe is the agy-y2 fixture `test-01-tmux-session.html` (lines 2103 to 2110). `start_server` probes the agy-y2 fixture first (lines 1929 to 1948).

### WD orphan hardening and log copy (C3 F4, F5, F6; C1 R4, R5): PRESENT in the runner, CONDITIONAL on the base (F2)

- The log copy exists with the right placement: `_copy_gecko_log` (lines 2237 to 2256) copies to `/tmp/worker-y9-gecko-{test}-a{attempt}.log`, logs success or failure, tolerates a missing file, and is called after each WD exit in the `finally` block (line 2418) and on the session-creation-failure path (line 2342), strictly before the next `WD()` starts, including before the suite-end cleanup session.
- The orphan hardening itself lives in run_live.py, not in this file. It is present in the run_live.py at HEAD (commit 1e3901c): append-mode log open (line 283), PID write plus session POST inside try with cleanup on any failure (lines 298 to 322), exception-proof terminate in `_cleanup` (lines 360 to 380), and the C1 diagnose fixes (second-sample error keeps the snap1 classification, run_live.py lines 232 to 240; refresh diagnoses like goto, line 478). It is ABSENT from the run_live.py committed at a82bb41, which has no diagnose_body at all, no geckodriver log file, no PID file, and no allow_hidden keyword on goto, refresh, or new_tab. See F2.

### Per-test independence (C2 F5): PRESENT

- Each test runs inside the per-test try/except in `main` (lines 2358 to 2405). `open_fixture` reloads the fixture with storage cleared per test (lines 875 to 883). A live step failure fails that test and the runner continues; only two-consecutive-INFRA aborts the suite (lines 2440 to 2444).

### Slot marker, launch, ship layout, evidence (C3 F4, F5, F6; Redteam A4, A12): PRESENT in plan and runner, except the freeze

- The launch command has `cd` to the shipped dir and `flock -w 60` (plan section 5; runner docstring lines 55 to 61). Stdout is redirected to a named log file. The shipped layout and the agy-y2 probe are specified. The six metrics are reported in the suite JSON (lines 2463 to 2471): wall time, Marionette call count, tokens UNMEASURED, observation cost UNMEASURED, VCR False, stall time. See F6 for the stall definition problem.
- NOT satisfied yet: no SHIPPED.md exists in the repo (checked: neither `improvements/SHIPPED.md` nor `tests/realistic/SHIPPED.md` exists), and no md5 list is recorded anywhere in the commit. The runner records md5s at run time in the suite JSON (lines 2472 to 2476) but never compares the shipped run_live.py against any expected value, so C1 R12 runtime verification is record-only. See F2.

## Q3. Is the ported verify a faithful transcription of check.mjs verifyTest?

Yes. Mechanical diff: 88 of 88 checks identical in selector, expected value, and message, in the same order per test (see the mechanical checks section). The two read-but-never-asserted values are preserved as read-only. The unknown-test branch is preserved. The runtime JS parses clean. Two trivial notes, both non-blocking:

- The port drops check.mjs `score` field (`failures.length === 0 ? 1 : 0`) from the returned object. The runner never reads `score`, so this is harmless, but the "1:1" claim is exact only for the assertions, not the return shape.
- check.mjs returns `passed` from `failures.length === 0`; the port does the same.

## Q4. New defects the first round missed

### N1. The runner cannot run against its own commit base (F2, the largest item)

- `from run_live import (... diagnose_body ...)` (lines 78 to 82) raises ImportError against the run_live.py committed at a82bb41, which defines no diagnose_body.
- `d.goto(url, allow_hidden=True)`, `d.refresh(allow_hidden=True)`, and `d.new_tab(url, allow_hidden=True)` (open_fixture lines 876 to 912, bootstrap line 1997, rebootstrap line 389, cleanup line 2503) raise TypeError against that base, whose goto, refresh, and new_tab take no allow_hidden keyword.
- The failure is loud, not silent: the run dies at import or at the first fixture load. It is fixed by shipping the post-1e3901c run_live.py, which has all three. But nothing in commit a82bb41 pins that base, and the plan claim "already FIXED in the shipped run_live.py (verified by reading)" was verified against a moving working tree, which is the exact failure mode Council 1 R4 and Redteam A2 warned about. The gate must be a ship-time check, not a claim.

### N2. Checks never reach the JSONL (F1)

- Covered in Q2 above. `Y9Runner` overrides `step` but not `check`, and base `Runner.check` never logs. This is the only evidence-contract hole in the runner file itself.

### N3. FIXTURE-UNAVAILABLE has no outcome (F4)

- `ensure_visible` raises `FIXTURE-UNAVAILABLE` (lines 472 and 485), but `main` has no branch for it. The except chain tests `startswith("INFRA:")` (line 2371), then diagnoses, then tests the timeout wording, and otherwise records the test as a live `failed` outcome (lines 2403 to 2408). A fixture that never renders a body would be reported as a live test failure, which misstates the finding. It needs its own outcome, recorded distinctly from a live failure and from INFRA.

### N4. The WD-timeout match misses the real wording (F5)

- Lines 2392 to 2393 test `"timeout waiting for" not in msg and "timeout" in msg.lower()`. A genuine 30 second urlopen timeout surfaces as `timed out` (URLError or TimeoutError), which does not contain the substring `timeout`, so the branch never fires for it. The branch is partly rescued by the diagnose path above it: a hung driver makes diagnose raise, giving classification UNKNOWN, which is reclassified INFRA (lines 2382 to 2391). But the timeout branch as written is near dead code and misleads a reader about what it catches.

### N5. stall_ms measures the wrong thing (F6)

- Line 2422 adds the whole test `elapsed_ms` to `stall_ms` for infra-blocked attempts. The plan defines stall as time spent in hidden-body recovery ladders, from ensure_visible timings. Whole-test elapsed overstates it. Either accumulate ensure_visible elapsed time, or correct the plan definition.

### N6. Attempt-1 summary is dropped on re-run (F7)

- When attempt 1 is infra-blocked, the summary built at lines 2428 to 2432 is discarded by the `continue` at line 2438; only the attempt 2 summary is appended and printed. The JSONL holds the attempt-1 steps, but the attempt-1 summary (failures, details, elapsed) has no stdout record. Print it before continuing.

### N7. Per-test worst-case bound is understated (F7)

- The plan says the per-test worst case is about 20 seconds. `open_fixture` can call `ensure_visible` up to three times (8 seconds each) plus a rebootstrap of up to 8 seconds plus three goto and refresh pairs. The honest bound is about 35 to 40 seconds. Diagnostic only, but a 30 second test would otherwise read as a hang.

### N8. Two small letter-of-the-fix gaps (F8)

- `rebootstrap_tab` raises a bare `RuntimeError("rebootstrap: no visible test tab after 3 attempts")` (line 421), not an INFRA-prefixed error as C2 F9 requires. Every caller wraps it (ensure_visible returns False and the caller raises INFRA; open_fixture wraps it as INFRA), so the effect is achieved, but the letter is unmet.
- The test-08 td click (lines 1664 to 1667) uses `click_el`, which does not scroll into view, while every other click goes through `d.click`, which does. If the filtered row sits outside the viewport, the Marionette click can fail for scroll reasons. Scroll first.

### N9. Dead code, no behavior impact

- `clear_input` (lines 211 to 218) is defined and never called. `_rl_log_step` is imported (line 79) and never used. Harmless; remove or leave.

## Required fixes (all before any live driving)

- F1. Override `check()` in `Y9Runner` so every intermediate check writes a JSONL record through the Y9 `log_step` (lines 180 to 194) with the attempt field, the check name, the condition result, and the detail. Keep the base behavior (append failure, print). Verify by running one test headlessly against a stub or by inspection that a check record with an attempt field appears in the JSONL.
- F2. Freeze the base before shipping. Ship run_live.py ONLY from commit 1e3901c or later (the version containing diagnose_body, allow_hidden on goto, refresh, and new_tab, the append-mode geckodriver log, and the PID write plus session POST inside try with cleanup). Write SHIPPED.md next to the shipped files with file, md5, and source commit for every shipped file. On the laptop, before launch, run `python3 -m py_compile run_live.py run_agy_y2.py` and `python3 -c "import run_agy_y2"` in the shipped dir; abort the launch if either fails. This closes the a82bb41-base incompatibility (ImportError on diagnose_body, TypeError on allow_hidden) and the missing md5 freeze.
- F3. In `ensure_visible`, after the removal eval, if the new diagnose is FIXTURE_FAILURE, raise FIXTURE-UNAVAILABLE immediately (same as the poll loop and the initial diagnose do), instead of falling through to `_log_diag` and rebootstrap.
- F4. In `main`, add an explicit branch for FIXTURE-UNAVAILABLE (its own outcome, recorded distinctly, suite continues, no effect on the infra counter unless the run decides otherwise). Do not let it fall through to the live `failed` outcome.
- F5. Fix the WD-timeout match at lines 2392 to 2393 to catch the real wording (`timed out`, TimeoutError, URLError) or remove the branch and record that the UNKNOWN diagnose path is the timeout classifier. As written it cannot fire on a genuine urlopen timeout.
- F6. Make `stall_ms` accumulate ensure_visible ladder time only (accumulate the elapsed time printed by ensure_visible), or correct the plan definition to whole-test elapsed for infra-blocked attempts. Pick one and make code and plan agree.
- F7. Print the attempt-1 summary to stdout before the re-run `continue` (line 2438). Fix the mapping table test-09 step 10 row to prescribe typing the full text `Milk, Eggs, Bread, Apples` (the runner is already correct). Correct the plan per-test worst-case bound from about 20 seconds to about 35 to 40 seconds. Correct the commit-message assertion count from 87 to 88.
- F8. Raise an INFRA-prefixed error from `rebootstrap_tab` (line 421) per C2 F9. In run_08, scroll the checkout row into view before the td click (lines 1664 to 1667).

## What was verified correct and should stay

- All 10 drivers follow the mapping tables step for step, with M11 (test-02 apply toast, lines 1181 to 1186) and M12 (test-05 chart-title wait, lines 1421 to 1426) implemented in code.
- The ported verify is 88 of 88 identical to check.mjs, and the runtime JS parses clean.
- The flagged-pass rule, the abort rule with two distinct counters, the fresh-tab-only bootstrap with bounded retries, the integrity guard with suite-defect handling, the mid-test hidden-body reclassification, the one-re-run rule, the JSONL rotation, the per-test screenshots, and the clean-only exit rule are all present in code with the line citations above.
- The preflight copy accepts FLOCK locks, refuses on unknown parentage, parses ppid after the last parenthesis, unlinks garbage PID files, gates on Hyprland IPC with a timeout, checks the Y8 ports, and probes the agy-y2 fixture.
- The test-10 step 15 gap is recorded as a gap and never counted as a driven step (lines 1853 to 1859, `r.gap` at lines 316 to 323, gaps list in the summary).
- The test-01 active-pane scoping is proven by the fixture (pane class at fixture line 196), not assumed.

## Scope limits of this re-review

- The runner was reviewed as code only. No live run was performed, so timing claims (8 second ladder, per-test wall time) and the live behavior of the Marionette calls are unverified beyond the code paths.
- The shipped run_live.py was verified by reading the working tree at HEAD (post-1e3901c). The freeze itself (SHIPPED.md, md5s, laptop smoke test) has not happened yet and is F2.
- The plan v2 text was checked only where it makes claims about the runner code. Slot polling cadence, the Y8 marker, and the handover token process were not re-verified live.
