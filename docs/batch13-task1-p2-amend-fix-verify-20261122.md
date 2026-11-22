# Batch 13 task 1: independent verification of P2-AMEND-FIX (step 7)

## Verdict: PASS

The step 7 fix is verified. All four assigned checks were run first-hand on
branch todolist-push at HEAD 3167c76. The P2 suite passes with 97 tests, the
pointer check exists at both _dispatch call sites, tests A1/A2 pin the
validator limit correctly, and the discover totals match the worker claim
(Ran 2131, skipped 17) with the error and failure delta fully explained by
two environment binaries that are currently missing on this VM, not by any
code defect. No fix work is needed, so no AMEND.

## Scope and method

- Report branch: main. Code read read-only from branch todolist-push.
- todolist-push HEAD verified: 3167c76. Fix commits verified on the branch:
  ce399c7 (tests) and 507a50b (fix), both ancestors of 3167c76.
- Full diffs of both commits read. Worker log read in full:
  improvements/worker-click5-p2-amend-fix-log.md (commit 03d99bc).
- Verification ran in a clean git worktree of todolist-push at 3167c76, so
  todolist-push was never modified. The wtype helper was built inside the
  worktree only (gitignored build artifact). Worktree status after all runs:
  clean apart from gitignored build artifacts.
- Times below are Asia/Ho_Chi_Minh (+07) on 2026-11-22, unless marked UTC.
- No personal information in this report. No long dashes anywhere in it.

## Check 1: P2 suite re-run, worker claims 97 tests OK

CONFIRMED.

- Command, 14:21:27 +07, from tests/ in the worktree:
  `PYTHONPATH=../scripts:. python3 -m unittest test_p2_element_ref`
- Output: `Ran 97 tests in 0.148s`, `OK`. Repeated: `Ran 97 tests in
  0.198s`, `OK`.
- Loader count confirms the total independently: 97 tests across 9 classes
  (ElementRefTests 21, ScreenScopeLegalityTests 18, ZenBackendTests 14,
  ScreenPointFormTests 11, ValidatorFixTests 11, CodeExecPlanValidationTests
  9, NoPointerDelegateTests 8, ValidatorLimitationTests 3,
  BackendRangeTests 2). The 11 new tests are the 8 NoPointerDelegateTests
  plus the 3 ValidatorLimitationTests, so 86 + 11 = 97 matches the worker
  claim exactly.
- Failing-first also confirmed, in a second worktree at ce399c7 (new tests,
  pre-fix code), 14:22 +07: `Ran 11 tests in 0.004s`, `FAILED
  (failures=7)`. The 7 failures are exactly the predicted ones:
  test_main_path_type, test_main_path_move, test_reground_click,
  test_reground_fill, test_wait_reports_no_input_sent,
  test_assert_reports_no_input_sent,
  test_assert_mismatch_still_fails_without_input_sent. Main-path click
  passed pre-fix (old allowlist covered it) and A1/A2/A3 passed pre-fix
  (they pin, not fix). After the fix all 11 pass (11 ok, 14:35 +07).

## Check 2: pointer check at BOTH _dispatch call sites

CONFIRMED. There are exactly two `self._dispatch(` call sites in
scripts/zen_backend.py at HEAD 3167c76, and both are guarded by a
`self._pointer is None` check immediately before the call:

- Re-ground path, line 559: `if self._pointer is None:` returns the
  structured refusal from `_no_pointer_result(index)` with the `re_ground`
  {plan_rect, live_rect} pair attached, sets error code
  no_pointer_delegate, and breaks, before the `_dispatch` at line 569.
- Main path, line 625: `if self._pointer is None:` returns
  `_no_pointer_result(index)` and breaks, before the `_dispatch` at
  line 635. The old 8-type allowlist (click, double_click, confirm_click,
  hover_click, fill, set_value, key, scroll) is gone from the guard. The
  only remaining mention of double_click/confirm_click/hover_click is at
  lines 429-430 inside `_verify`, which classifies postconditions, not a
  dispatch guard, so it is not a bypass.
- `_dispatch` itself (line 387) still returns (False, False) when the
  pointer is None, as a second fail-closed layer.
- Wait and assert confirmed in code: wait records input_sent False,
  target_received False with ok True (lines 515-522); assert sets sent =
  received = False and ok comes from the postcondition alone (`ok =
  verified`, lines 611-614 and 640-641).

## Check 3: tests A1/A2 pin the validator limit correctly

CONFIRMED, by code read and by direct calls.

- Code read, scripts/zen_dom.py check_viewport_geometry (line 107): the
  verified-origin branch runs ONLY inside `if right_gap < 0 or
  bottom_gap < 0:` (closure overflow), returning the verified absolute
  origin. On the normal passing branch the code skips that block entirely,
  checks exactness of `absolute` against `window + moz * factor`, and
  returns `absolute`, which IS the moz-computed origin. verified_moz_inner
  is never read on the normal branch. The worker log section 5 states the
  same scope, and the code agrees.
- Direct calls, 14:21 +07 (factor 1, window [2509, 914], size [925, 1176],
  monitor [2464, 902, 1920, 1200]):
  - Gaps hand-checked: right_gap = 925 - 667 - 250 = 8, bottom_gap =
    1176 - 1150 - 18 = 8. Both non-negative, so the normal branch runs.
  - A1: moz [250, 18], absolute [2759, 932], inner [667, 1150] returns
    [2759, 932], which is 10px off the true origin [2749, 922]. The wrong
    but self-consistent moz is accepted. Pin correct.
  - A2: same inputs plus verified_moz_inner [240, 8] still returns
    [2759, 932]. The verified value is ignored on the passing branch. Pin
    correct.
  - A3 anchor: true moz [240, 8] returns [2749, 922]. Correct.
  - Control case: closure overflow (moz [274, 66], gaps -16, -40) with
    verified [240, 8] returns [2749, 922], the verified origin. This
    confirms the verified-origin path only rescues the closure-overflow
    case, exactly as the worker log claims.
- A1/A2 pin the limitation, they do not fix it. The tests say so in their
  docstring, and the code agrees. No change to the validator itself was in
  either fix commit, which is correct for a pin.

## Check 4: discover claim, worker reports Ran 2131, errors=1, skipped=17, failures=0

COUNTS CONFIRMED, ERROR AND FAILURE NUMBERS DIFFER FOR AN ENVIRONMENT
REASON, NOT A CODE REASON. No hidden regression found.

### Root discover, my re-run

- Command, started 14:21:33 +07, from the repo root of the worktree:
  `PYTHONPATH=scripts:. python3 -m unittest discover -s tests -p
  'test_*.py'`
- Output, finished 14:24:22 +07: `Ran 2131 tests in 175.507s`, `FAILED
  (failures=1, errors=5, skipped=17)`. Log: /tmp/batch13-t1-discover-root.log.
- The 5 errors and 1 failure, all traced:
  1. test_cursor_file setUpClass: g++ rejects -std=c++26 ("unrecognized
     command-line option; did you mean -std=c++20"). This is the worker
     single reported error. Reproduces exactly.
  2. test_bench_manifest, 3 errors: FileNotFoundError
     `/home/hatch/workspace/tools/firefox/firefox`. The bench manifest
     builder hashes that Firefox binary path unconditionally
     (scripts/bench_manifest.py line 177). The binary does not exist on
     this VM now (verified with ls, 14:26 +07).
  3. test_tc02_controller, 1 error + 1 failure: `tesseract is
     unavailable; refusing to assume text presence`
     (scripts/tc02_controller.py line 1124, via shutil.which). tesseract
     is not installed now: /usr/bin/tesseract does not exist and `which
     tesseract` finds nothing (verified 14:26 +07). The FAIL is the
     fragment-absent test expecting '20:30' in the reason but getting the
     tesseract-unavailable reason instead, a direct consequence of the
     missing binary.
- Why this is environment drift, not a code difference:
  - No commit between 507a50b and 3167c76 touched
    scripts/bench_manifest.py, scripts/tc02_controller.py,
    tests/test_bench_manifest.py, or tests/test_tc02_controller.py
    (verified with git log, empty result).
  - The worker log records tesseract present at /usr/bin/tesseract at
    12:58 +07 and Firefox re-downloaded for batch 6, so both binaries
    existed at the worker discover time (13:08 +07) and are gone now
    (14:26 +07). When and how they vanished is not established from any
    log available here.
  - The test count (2131) and skip count (17) match the worker claim
    exactly, which they would not if the code under test had changed.

### Tests/ discover, my re-run (second worker number)

- Command, started 14:26:12 +07, from tests/:
  `PYTHONPATH=../scripts:. python3 -m unittest discover -s . -p
  'test_*.py'`
- Output, finished 14:29:49 +07: `Ran 2124 tests in 176.605s`, `FAILED
  (failures=1, errors=8, skipped=17)`. Log:
  /tmp/batch13-t1-discover-tests.log.
- The worker reported errors=4, failures=0 from tests/. My 8 errors are
  the worker 4 plus the same 5 environment items counted above minus the
  overlap: worker 4 are test_a11y_skeleton import (ModuleNotFoundError:
  No module named 'tests'), test_cursor_file g++ C++26, and
  test_perf_evidence x2 (FileNotFoundError
  docs/benchmarks/r5_cdp_aggregate.json, relative path resolved from
  tests/). All 4 reproduce exactly, with the same causes the worker
  named (invocation artifacts and toolchain). The extra 4 errors and 1
  failure are the bench_manifest x3 and tc02 x2 items above.

### Skip identities, verbose root discover

- Command, started 14:30:33 +07: same root discover with -v. Output,
  finished 14:34:03 +07: `Ran 2131 tests in 177.629s`, `FAILED
  (failures=1, errors=5, skipped=17)`. Log:
  /tmp/batch13-t1-discover-root-v.log. Exactly 17 lines carry a skip
  reason.
- The 17 skips: 12 cursor renderer missing, 3 Lua interpreter missing
  or unavailable, 1 hyprglass source not supplied, 1 tesseract. Same
  counts as the worker list (12 + 3 + 1 + 1 = 17), with one identity
  swap caused by tesseract now being missing:
  test_menu_bar_ocr_requires_file_and_edit_on_fixture_images now skips
  ("tesseract is required by the menu-bar check"), while
  test_missing_tesseract_is_unverifiable now RUNS and passes ("ok"),
  because the missing-binary case is now the actual state. That swap is
  consistent with the tesseract explanation, not a code change.

## Extra confirmations (not in the four assigned checks, run for completeness)

- Related 7 suites re-run, 14:26 +07:
  `test_zen_dom test_click3_redteam2 test_code_exec test_a1_preflight
  test_core test_first_action test_s0_bundle` gives `Ran 294 tests`,
  `OK`. Matches the worker claim exactly.
- Previously unrun 3 suites, 14:26 +07: `test_keyboard_preflight
  test_click2_redteam test_pick4_fastpath` gives `Ran 131 tests`, `OK`.
  Matches the worker claim exactly.
- wtype build guidance reproduced, 14:21:21 +07: the docs/testing.md
  commands build native/wtype at 35984 bytes, the same size the worker
  reported. `pkg-config gtk4-layer-shell-0 gtk4 wayland-client` fails
  with exit 1 ("Package gtk4-layer-shell-0 was not found"), confirming
  the full build.py stops at the indicator step on this VM as the docs
  say.
- Em dash check on the fix commits: 0 em dashes in the added lines of
  docs/testing.md in 507a50b, 0 in the zen_backend.py and cu.py diff, 0 in
  the ce399c7 test diff. The worker note that docs/testing.md contains 9
  pre-existing em dashes outside the added section was not re-counted
  line by line, but no added line introduces one.
- Step 7 scope check: `git show 292753f --stat` confirms 17 files, and
  no commit between 292753f and 3167c76 touched test_cursor_file.py,
  test_perf_evidence.py, test_a11y_skeleton.py, test_tc02_controller.py,
  or test_bench_manifest.py, so none of the discover errors is a step 7
  regression.

## Limitation: live runs not re-run

- The worker live claims (Zen live run passed 13:22:29 +07 on the laptop,
  CLI act WITH/WITHOUT binding passed 13:38:38 +07) were NOT re-run from
  this VM in this session: there is no laptop path available to this
  agent here, and the brief did not ask for a live re-run. They rest on
  the worker log only.
- The code paths those live runs exercise (no-pointer refusal, wait
  input_sent False) are covered by the unit tests re-run above, which
  pass. No live evidence contradicts the fix.

## Environment note for the coordinator

- Two binaries the suite depends on are currently missing on this VM:
  /home/hatch/workspace/tools/firefox/firefox and tesseract
  (/usr/bin/tesseract, not on PATH). Both were present at the worker
  discover time (13:08 +07) and are gone now (14:26 +07). This is the
  same failure mode seen before on this machine (binaries disappearing
  across restarts or cleanups). Restore both before the next full
  discover, so the numbers are comparable to the worker run. No code
  change is needed for this.

## Evidence index

- P2 suite: Ran 97, OK, twice (0.148s, 0.198s), 14:21 +07.
- Failing-first at ce399c7: Ran 11, FAILED (failures=7), 14:22 +07, 7
  failures named in Check 1.
- Pointer guard: scripts/zen_backend.py lines 559-569 (re-ground) and
  625-635 (main), _dispatch fail-closed at line 387.
- Validator: scripts/zen_dom.py check_viewport_geometry, verified branch
  only inside the right_gap < 0 or bottom_gap < 0 block; direct A1/A2/A3
  calls in Check 3.
- Root discover: Ran 2131 in 175.507s, FAILED (failures=1, errors=5,
  skipped=17), 14:24:22 +07, log /tmp/batch13-t1-discover-root.log.
- Tests/ discover: Ran 2124 in 176.605s, FAILED (failures=1, errors=8,
  skipped=17), 14:29:49 +07, log /tmp/batch13-t1-discover-tests.log.
- Verbose root discover: Ran 2131 in 177.629s, FAILED (failures=1,
  errors=5, skipped=17), 14:34:03 +07, log
  /tmp/batch13-t1-discover-root-v.log.
- Related suites: 294 OK; unrun suites: 131 OK; both 14:26 +07.
- Commits verified: ce399c7, 507a50b, 03d99bc, all ancestors of
  todolist-push HEAD 3167c76.
