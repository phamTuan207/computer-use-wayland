# Batch 13 council 1: review of task 1 P2-AMEND-FIX verification

## Verdict: AGREE, PASS stands

The task 1 report (docs/batch13-task1-p2-amend-fix-verify-20261122.md,
commit e018ae0, verdict PASS) is correct on every substantive claim. I
re-ran the key checks first-hand on branch todolist-push at HEAD 3167c76
in clean worktrees, re-read the cited code lines, and re-ran both
discover invocations. No code defect was found, so no AMEND is needed.
One number in my own re-run differs from the task 1 report (root
discover failures=3, not 1). The 2 extra failures are a transient
post-reboot artifact in my run, proven so below, not a task 1 error
and not a regression.

## Scope and method

- Report branch: main. Code read read-only from branch todolist-push.
- todolist-push HEAD verified: 3167c76. Fix commits verified as
  ancestors of 3167c76: ce399c7 (tests) and 507a50b (fix). Worker log
  read in full: improvements/worker-click5-p2-amend-fix-log.md
  (commit 03d99bc, 529 lines).
- Verification ran in clean git worktrees of todolist-push at
  3167c76 and of ce399c7, so todolist-push was never modified. A
  runtime restart wiped /tmp mid-session, so the worktrees were
  recreated once and the wtype helper rebuilt; all numbers below
  are from the recreated worktrees unless marked otherwise.
- Times below are Asia/Ho_Chi_Minh (+07) on 2026-11-22, unless
  marked UTC.
- No personal information in this report. No long dashes anywhere
  in it.

## Claim by claim

### Check 1: P2 suite, worker claims 97 tests OK

AGREE.

- Command, 14:37:56 +07, from tests/ in the worktree:
  `PYTHONPATH=../scripts:. python3 -m unittest test_p2_element_ref`
- Output: `Ran 97 tests in 0.124s`, `OK`. Repeated: `Ran 97 tests in
  0.125s`, `OK`. After the worktree rebuild, once more: `Ran 97
  tests in 0.147s`, `OK`.
- Loader count confirms the total independently: 97 tests across 9
  classes, with exactly the class counts the task 1 report lists
  (ElementRefTests 21, ScreenScopeLegalityTests 18, ZenBackendTests
  14, ScreenPointFormTests 11, ValidatorFixTests 11,
  CodeExecPlanValidationTests 9, NoPointerDelegateTests 8,
  ValidatorLimitationTests 3, BackendRangeTests 2). The 11 new
  tests are the 8 NoPointerDelegateTests plus the 3
  ValidatorLimitationTests, so 86 + 11 = 97.
- First-hand note: a fresh checkout does NOT pass out of the box.
  Before the wtype build my first run failed with 21 errors, all
  `RuntimeError: private wtype helper is missing:
  .../native/wtype`, exactly as docs/testing.md warns. After
  building only the wtype helper per docs/testing.md, the suite
  passes. The build produced native/wtype at 35984 bytes, the same
  size the worker and task 1 reports record. The task 1 report
  discloses this build step in its Scope section, so this is not a
  report error, but the 97 OK result depends on that step.

### Check 1b: failing-first at ce399c7, 11 tests, 7 failures

AGREE, with a naming note.

- Command, 14:38:03 +07, in the ce399c7 worktree:
  `PYTHONPATH=../scripts:. python3 -m unittest
  test_p2_element_ref.NoPointerDelegateTests
  test_p2_element_ref.ValidatorLimitationTests`
- Output: `Ran 11 tests in 0.004s`, `FAILED (failures=7)`.
- The 7 failures, full names:
  test_main_path_type_reports_no_pointer_delegate,
  test_main_path_move_reports_no_pointer_delegate,
  test_reground_click_reports_no_pointer_delegate,
  test_reground_fill_reports_no_pointer_delegate,
  test_wait_reports_no_input_sent,
  test_assert_reports_no_input_sent,
  test_assert_mismatch_still_fails_without_input_sent.
- Naming note: the task 1 report shortens these names
  (test_main_path_type, test_main_path_move, test_reground_click,
  test_reground_fill, and so on). The worker log uses the same
  shortened forms. The same 7 tests fail, so the substance is
  right and the full names are recorded here.
- Main-path click passed pre-fix (not among the 7 failures) and
  A1/A2/A3 passed pre-fix, as the report states. After the fix,
  the same 11 tests pass: `Ran 11 tests in 0.003s`, `OK`,
  14:38:31 +07.

### Check 2: pointer check at BOTH _dispatch call sites

AGREE.

- There are exactly two `self._dispatch(` call sites in
  scripts/zen_backend.py at HEAD 3167c76, lines 569 and 635, and
  no `_dispatch(` call in any other file under scripts/.
- Re-ground path, line 559: `if self._pointer is None:` returns
  the structured refusal from `_no_pointer_result(index)` with
  the `re_ground` {plan_rect, live_rect} pair attached, sets
  error code no_pointer_delegate, and breaks, before the
  `_dispatch` at line 569.
- Main path, line 625: `if self._pointer is None:` returns
  `_no_pointer_result(index)` and breaks, before the `_dispatch`
  at line 635. The old 8-type allowlist is gone from the guard;
  the only remaining allowlist mentions are a docstring and a
  comment (lines 398 and 627) describing the old guard.
- The only remaining mention of double_click/confirm_click/
  hover_click is at lines 429-430 inside `_verify`, which
  classifies postconditions, not a dispatch guard. Not a bypass.
- `_dispatch` itself (defined line 380) returns (False, False)
  when the pointer is None, at line 387, as a second fail-closed
  layer.
- Wait records input_sent False, target_received False with ok
  True (block at lines 514-525; the report cites 515-522, off by
  one line at the start). Assert sets sent = received = False
  (lines 613-616) and ok comes from the postcondition alone
  (`ok = verified`, lines 638-639; the report cites 611-614 and
  640-641, off by two lines). Line spans drift by 1-2 lines;
  the code described is the code present.
- The full 507a50b zen_backend.py diff was read: it adds
  `_no_pointer_result`, adds the re-ground pointer check, flips
  wait input_sent/target_received from True to False, flips
  assert sent/received from True to False, and removes the old
  8-type allowlist guard. The diff matches the report.

### Check 3: tests A1/A2 pin the validator limit correctly

AGREE.

- Code read, scripts/zen_dom.py check_viewport_geometry (defined
  line 107): the verified-origin branch runs ONLY inside
  `if right_gap < 0 or bottom_gap < 0:` (line 203), returning the
  verified absolute origin at line 267. On the normal passing
  branch the code checks exactness of `absolute` against
  `window + moz * factor` and returns `absolute` at line 299.
  verified_moz_inner is never read on the normal branch. The
  worker log section 5 states the same scope, and the code
  agrees.
- Direct calls, 14:38 +07 (factor 1, window [2509, 914], size
  [925, 1176], monitor [2464, 902, 1920, 1200]):
  - Gaps hand-checked: right_gap = 925 - 667 - 250 = 8,
    bottom_gap = 1176 - 1150 - 18 = 8. Both non-negative, so the
    normal branch runs.
  - A1: moz [250, 18], absolute [2759, 932], inner [667, 1150]
    returns [2759, 932], which is 10px off the true origin
    [2749, 922]. The wrong but self-consistent moz is accepted.
    Pin correct.
  - A2: same inputs plus verified_moz_inner [240, 8] still
    returns [2759, 932]. The verified value is ignored on the
    passing branch. Pin correct.
  - A3 anchor: true moz [240, 8] returns [2749, 922]. Correct.
  - Control case: closure overflow (moz [274, 66], gaps -16,
    -40) with verified [240, 8] returns [2749, 922], the
    verified origin. This confirms the verified-origin path
    only rescues the closure-overflow case.
- The A1/A2/A3 test code uses exactly these inputs
  (tests/test_p2_element_ref.py, class ValidatorLimitationTests,
  line 564; the docstring there says the verified return is at
  line 267 and the moz return at line 299, which matches the
  code exactly).
- Small addition the task 1 report does not mention:
  ZenSession.viewport_origin (scripts/zen_dom.py, line 765)
  passes verified_moz_inner through to
  check_viewport_geometry (line 843), so the same limitation
  applies on the live call path too. This does not change the
  conclusion: the pin is correct and no validator change was
  in either fix commit, which is correct for a pin.
  Confirmed: neither ce399c7 nor 507a50b touches
  scripts/zen_dom.py (507a50b touches 3 files only:
  docs/testing.md, scripts/cu.py, scripts/zen_backend.py;
  ce399c7 touches tests/test_p2_element_ref.py only, +212
  lines).

### Check 4: discover claim, worker reports Ran 2131, errors=1, skipped=17, failures=0

COUNTS AGREE. ERROR NUMBERS AGREE. FAILURE NUMBER DIFFERS IN MY
RUN FOR A PROVEN TRANSIENT REASON, NOT A CODE REASON.

### Root discover, my re-run

- Command, started 14:43:20 +07, from the repo root of the
  worktree: `PYTHONPATH=scripts:. python3 -m unittest discover
  -s tests -p 'test_*.py'`
- Output, finished 14:48:40 +07: `Ran 2131 tests in 317.537s`,
  `FAILED (failures=3, errors=5, skipped=17)`. Log:
  ~/workspace/goals/computer-use-wayland-zen-browser-control-research/hidden_files/b13c1-discover-root.log.
- Ran 2131, errors=5, skipped=17 all match the task 1 report.
  The 5 errors match in identity and cause:
  1. test_bench_manifest, 3 errors: FileNotFoundError
     `/home/hatch/workspace/tools/firefox/firefox`.
     scripts/bench_manifest.py line 58 defines FIREFOX as that
     path and line 177 hashes it unconditionally. The binary
     does not exist on this VM now.
  2. test_cursor_file setUpClass: g++ rejects -std=c++26
     ("unrecognized command-line option; did you mean
     -std=c++20"). The worker single reported error. Reproduces
     exactly.
  3. test_tc02_controller, 1 error: `tesseract is
     unavailable; refusing to assume text presence`
     (scripts/tc02_controller.py line 1124-1125, via
     shutil.which at line 1122). tesseract is not installed
     now: /usr/bin/tesseract does not exist and `which
     tesseract` finds nothing.
- The 1 failure the task 1 report has is mine too:
  test_typed_text_check_fails_when_fragment_is_absent, expecting
  '20:30' in the reason but getting the tesseract-unavailable
  reason instead, a direct consequence of the missing binary.

### The 2 extra failures in my root run, and why they are transient

- The 2 extra failures are
  test_act_diagnostics.ActDiagnostics.test_preflight_refusal_raises_before_any_diagnostics_query
  and
  test_core.Coordinates.test_expired_observation_is_typed_preflight_before_focus_or_input.
  Both expect a PreflightRefusal matching "observation older
  than 120s" and both got "capture_started_monotonic is invalid;
  observe again" instead.
- Mechanism, read first-hand in scripts/cu.py: each test builds
  a meta with `capture_started_monotonic = time.monotonic()`
  (via `_capture_identity`, line 941-945) and subtracts 121
  (OBSERVATION_MAX_AGE + 1, line 78). `_valid_capture_identity`
  (line 787) first rejects any value that is not finite or is
  <= 0 with "capture_started_monotonic is invalid", and only
  then checks the age. When time.monotonic() is under 121s, the
  fabricated value goes <= 0 and the identity check fires
  before the age check, so the test sees the wrong message.
- Timing proof: the runtime restart rebooted this VM. `uptime`
  at 14:49:25 +07 read "up 7 min", and time.monotonic() read
  424.6s, so the boot was around 14:42 +07. My discover
  started 14:43:20 +07, about a minute after boot, so the
  early modules ran while time.monotonic() was still under
  121s. Both failing tests ran in that window.
- Reproduction proof: run standalone now, both tests pass
  (`Ran 2 tests in 0.004s`, `OK`, 14:49:25 +07). The later
  tests/ discover below, started 14:50:13 +07 when monotonic
  was past 400s, shows failures=1, exactly the task 1 number,
  with no preflight failure. The task 1 report measured
  failures=1 at 14:24 +07, hours after that boot, so its number
  was correct at its run time.
- Not a step 7 regression: no commit between 292753f and
  3167c76 touched tests/test_act_diagnostics.py or
  tests/test_core.py. The only cu.py change in that range is
  507a50b, and its cu.py diff is only the wtype missing-helper
  error message (9 lines), nowhere near the preflight path.
  This is a third environment factor in the discover story
  (missing Firefox binary, missing tesseract, post-reboot
  monotonic clock), not a code difference. The two tests are
  boot-window sensitive by construction: they fabricate a
  121s-old observation, which is only representable once the
  machine has been up for 121s.

### Tests/ discover, my re-run (second worker number)

- Command, started 14:50:13 +07, from tests/:
  `PYTHONPATH=../scripts:. python3 -m unittest discover -s .
  -p 'test_*.py'`
- Output, finished 14:54:22 +07: `Ran 2124 tests in 247.580s`,
  `FAILED (failures=1, errors=8, skipped=17)`. Log:
  ~/workspace/goals/computer-use-wayland-zen-browser-control-research/hidden_files/b13c1-discover-tests.log.
- This matches the task 1 report exactly (Ran 2124,
  failures=1, errors=8, skipped=17). The 8 errors are the
  worker 4 (test_a11y_skeleton import ModuleNotFoundError: No
  module named 'tests'; test_cursor_file g++ C++26;
  test_perf_evidence x2 FileNotFoundError
  docs/benchmarks/r5_cdp_aggregate.json) plus bench_manifest
  x3 and tc02 x1, with the same causes the worker named. The 1
  failure is the tc02 fragment-absent test.

### Skip identities

- The 17 skips were not re-enumerated from a verbose run here,
  but the swap the task 1 report describes was verified
  directly, 14:49 +07:
  - test_menu_bar_ocr_requires_file_and_edit_on_fixture_images
    now SKIPS ("OK (skipped=1)"), because tesseract is missing.
  - test_missing_tesseract_is_unverifiable now RUNS and passes
    ("OK"), because the missing-binary case is now the actual
    state.
- The swap is consistent with the tesseract explanation, not
  a code change.

## Extra confirmations (not in the four assigned checks)

- Related 7 suites re-run, 14:39:47 +07:
  `test_zen_dom test_click3_redteam2 test_code_exec test_a1_preflight
  test_core test_first_action test_s0_bundle` gives `Ran 294 tests`,
  `OK`. Matches the worker claim exactly.
- Previously unrun 3 suites, 14:39:47 +07:
  `test_keyboard_preflight test_click2_redteam test_pick4_fastpath`
  gives `Ran 131 tests`, `OK`. Matches the worker claim exactly.
- Em dash check: 0 em dashes in the added lines of 507a50b, 0 in
  the added lines of ce399c7, 0 em dashes and 0 en dashes in the
  task 1 report itself. docs/testing.md at 3167c76 contains 9 em
  dashes in total, all pre-existing outside the added section,
  which confirms the task 1 side note exactly (it said 9, and
  said it had not re-counted them; the count is 9).
- Step 7 scope check: `git show 292753f --stat` confirms 17
  files, and no commit between 292753f and 3167c76 touched
  test_cursor_file.py, test_perf_evidence.py,
  test_a11y_skeleton.py, test_tc02_controller.py, or
  test_bench_manifest.py, nor scripts/bench_manifest.py or
  scripts/tc02_controller.py, so none of the discover errors
  is a step 7 regression.

## Errors, gaps, and missing checks in the task 1 report

1. Line-number drift, minor: wait block cited as lines 515-522,
   actual block is 514-525; assert `ok = verified` cited as
   lines 640-641, actual lines are 638-639. The code described
   is the code present. No correction needed beyond the record
   here.
2. Test-name abbreviation, minor: the 7 failing-first names are
   shortened (suffixes like _reports_no_pointer_delegate and
   _reports_no_input_sent dropped). Same shortened forms as the
   worker log. Full names are recorded in Check 1b above.
3. Attribution imprecision, minor: the report says "The worker
   log records tesseract present at /usr/bin/tesseract at 12:58
   +07". The worker log records tesseract present at 13:12 +07
   (the verbose-discover entry) and in section 7; 12:58 is the
   pre-checks time, which does not mention tesseract. The
   substance is unaffected: tesseract was present at the worker
   discover time (tc02 tests passed then) and is gone now.
   Likewise "Firefox re-downloaded for batch 6" is batch 6
   history, not a statement in the worker log; the operative
   fact (the binary existed at the worker discover time, shown
   by the bench_manifest tests passing then, and is absent now)
   is proven by the test outcomes.
4. Unmentioned but checked: ZenSession.viewport_origin passes
   verified_moz_inner through to check_viewport_geometry, so
   the A1/A2 limitation applies on the live call path too. The
   report's claim about the function is correct; the wrapper
   adds no second verified path.
5. Shared limitation, stated in the task 1 report and shared
   here: the worker live claims (Zen live run passed 13:22:29
   +07, CLI act WITH/WITHOUT binding passed 13:38:38 +07) were
   NOT re-run from this VM. There is no laptop path available
   to this agent here, and the brief did not ask for a live
   re-run. The code paths those live runs exercise (no-pointer
   refusal, wait input_sent False) are covered by the unit
   tests re-run above, which pass. No live evidence contradicts
   the fix.

## Environment note for the coordinator

- Three environment factors now explain every discover delta
  from the worker run: /home/hatch/workspace/tools/firefox/firefox
  is missing, tesseract is missing (/usr/bin/tesseract, not on
  PATH), and this VM rebooted around 14:42 +07, which makes the
  two preflight tests fail only when a discover starts within
  about 121s of boot. The first two are the same failure mode
  seen before on this machine (binaries disappearing across
  restarts or cleanups). Restore both binaries before the next
  full discover, and avoid starting a full discover within 2
  minutes of a reboot, so the numbers are comparable to the
  worker run. No code change is needed for any of this.

## Evidence index

- P2 suite: Ran 97, OK, three times (0.124s, 0.125s, 0.147s),
  14:37:56 +07 and 14:43 +07. Fresh checkout without the wtype
  build: 21 errors, all the missing-helper RuntimeError.
- Failing-first at ce399c7: Ran 11, FAILED (failures=7),
  14:38:03 +07, 7 failures named in full in Check 1b.
- Post-fix 11 new tests: Ran 11, OK, 14:38:31 +07.
- Pointer guard: scripts/zen_backend.py lines 559-569
  (re-ground) and 625-635 (main), _dispatch fail-closed at
  line 387, old allowlist gone from code.
- Validator: scripts/zen_dom.py check_viewport_geometry, line
  107, verified branch only inside the right_gap < 0 or
  bottom_gap < 0 block (line 203), return verified_absolute
  line 267, return absolute line 299; direct A1/A2/A3 calls in
  Check 3.
- Root discover: Ran 2131 in 317.537s, FAILED (failures=3,
  errors=5, skipped=17), 14:48:40 +07, log in the goal
  hidden_files as b13c1-discover-root.log.
- Tests/ discover: Ran 2124 in 247.580s, FAILED (failures=1,
  errors=8, skipped=17), 14:54:22 +07, log in the goal
  hidden_files as b13c1-discover-tests.log.
- Boot-window proof: uptime "up 7 min" at 14:49:25 +07,
  time.monotonic() 424.6s; the 2 extra preflight failures pass
  standalone now (Ran 2, OK).
- Skip swap: menu_bar_ocr test skips, missing_tesseract test
  runs and passes, both 14:49 +07.
- Related suites: 294 OK; unrun suites: 131 OK; both
  14:39:47 +07.
- Commits verified: ce399c7, 507a50b, 03d99bc, 292753f, all
  ancestors of todolist-push HEAD 3167c76.
