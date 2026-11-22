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
  clean apart from gitignored build artifacts. Note for a reader
  reproducing Check 1: a fresh checkout without that build fails the P2
  suite with 21 errors, all `RuntimeError: private wtype helper is
  missing`, exactly as docs/testing.md documents (lines 15-23), so the
  97 OK result below depends on that documented build step first.
- Times below are Asia/Ho_Chi_Minh (+07) on 2026-11-22, unless marked UTC.
- No personal information in this report. No long dashes anywhere in it.

## Check 1: P2 suite re-run, worker claims 97 tests OK

CONFIRMED.

- Command, 14:21:27 +07, from tests/ in the worktree, after the wtype
  helper build described in Scope and method (a bare checkout fails this
  command with 21 missing-helper errors first):
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
  (failures=7)`. The 7 failures are exactly the predicted ones, full
  names as defined in tests/test_p2_element_ref.py at HEAD 3167c76:
  test_main_path_type_reports_no_pointer_delegate (line 452),
  test_main_path_move_reports_no_pointer_delegate (line 467),
  test_reground_click_reports_no_pointer_delegate (line 482),
  test_reground_fill_reports_no_pointer_delegate (line 500),
  test_wait_reports_no_input_sent (line 517),
  test_assert_reports_no_input_sent (line 532),
  test_assert_mismatch_still_fails_without_input_sent (line 548).
  Main-path click passed pre-fix (old allowlist covered it) and A1/A2/A3
  passed pre-fix (they pin, not fix). After the fix all 11 pass
  (11 ok, 14:35 +07).

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
  target_received False with ok True (lines 514-524; input_sent False at
  line 520, target_received False at line 521, ok True at line 524);
  assert sets sent = received = False at line 618 (branch lines 613-618)
  and ok comes from the postcondition alone (`ok = verified`, line 639).

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
- The same limitation applies on the live call path too:
  ZenSession.viewport_origin (scripts/zen_dom.py, defined line 764)
  passes verified_moz_inner through to check_viewport_geometry
  (line 843), so it inherits the A1/A2 limitation and adds no second
  verified path.

## Check 4: discover claim, worker reports Ran 2131, errors=1, skipped=17, failures=0

COUNTS CONFIRMED, ERROR AND FAILURE NUMBERS DIFFER FOR AN ENVIRONMENT
REASON, NOT A CODE REASON. No hidden regression found. The failures=1
number below holds on a long-uptime VM only; see the boot-time flake
note at the end of this check.

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
  - The worker log records tesseract present at /usr/bin/tesseract in its
    13:12 +07 verbose-discover entry (line 104 of the log at 03d99bc),
    not at 12:58 +07 (that entry is about native/wtype existing). The
    log does not record any Firefox re-download: it records
    /usr/bin/firefox as NOT existing (line 105), and mentions Firefox
    only twice. The tools/firefox binary still existed at the worker
    discover time (13:08 +07), shown by test_bench_manifest passing
    then (worker root discover errors=1, only the g++ error), and both
    binaries are gone now (14:26 +07). When and how they vanished is
    not established from any log available here.
  - The test count (2131) and skip count (17) match the worker claim
    exactly, which they would not if the code under test had changed.

### Boot-time flake note (added in the batch 13 fix pass)

- Later independent re-runs of the same root discover by the three
  council reviewers and the redteam, all on VMs that had rebooted
  minutes earlier, showed failures=2 or failures=3 instead of this
  report's failures=1, with the same errors=5 and skipped=17. The
  extra failures are a pre-existing boot-time flake, not a step 7
  regression, and not an error in this report's run, which measured
  failures=1 hours after boot.
- Mechanism, verified first-hand in the code at todolist-push HEAD
  3167c76: test_act_diagnostics
  test_preflight_refusal_raises_before_any_diagnostics_query
  (tests/test_act_diagnostics.py line 331) and test_core
  test_expired_observation_is_typed_preflight_before_focus_or_input
  (tests/test_core.py line 77) each subtract age =
  OBSERVATION_MAX_AGE + 1 (121) from capture_started_monotonic, which
  is time.monotonic() at fixture build (scripts/cu.py
  _capture_identity, lines 941-945). _valid_capture_identity
  (scripts/cu.py, line 787) rejects any value at or below 0 with
  "capture_started_monotonic is invalid; observe again" (lines
  793-795) before it ever reaches the age check (lines 798-800), so
  while time.monotonic() is under 121s the tests see the wrong
  message instead of the expected "observation older than 120s"
  refusal. Both tests pass standalone once the monotonic clock is
  past 121s (reviewers verified at monotonic 431.2s, 451.2s, and
  past 440s).
- Whether a fresh-boot run shows failures=2 or failures=3 depends on
  how much of the run elapses before the monotonic clock passes 121s:
  test_act_diagnostics runs near the start of discover order, so it
  fails on any discover started within about 2 minutes of a boot;
  test_core runs later, so it fails only when the run starts even
  closer to boot (council 1, discover started about 1 minute after
  boot, saw both; councils 2 and 3 and the redteam saw only the
  act_diagnostics one).
- Not a step 7 regression: no commit between 292753f and 3167c76
  touched tests/test_act_diagnostics.py or tests/test_core.py
  (verified with git log, 0 commits), and the only cu.py change in
  that range, 507a50b, touches only the wtype error message, nowhere
  near the preflight path.
- Advice for future verifiers: start a full discover more than about
  2 minutes after a boot, or expect failures=2 from this one test
  (failures=3 if the run starts within about 1 minute of boot) and do
  not mistake it for a regression.

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
  (/usr/bin/tesseract, not on PATH). Tesseract was present at the worker
  discover time (13:08 +07, recorded in the worker log 13:12 entry) and
  the tools/firefox binary existed then too (test_bench_manifest passed
  at the worker run); both are gone now (14:26 +07). This is the
  same failure mode seen before on this machine (binaries disappearing
  across restarts or cleanups). Restore both before the next full
  discover, so the numbers are comparable to the worker run. No code
  change is needed for this.
- Also, start a full discover more than about 2 minutes after a boot:
  a discover started sooner shows one or two extra failures from the
  boot-time flake in Check 4 (test_act_diagnostics, and test_core if
  the run starts within about 1 minute of boot).

## Evidence index

- P2 suite: Ran 97, OK, twice (0.148s, 0.198s), 14:21 +07.
- Failing-first at ce399c7: Ran 11, FAILED (failures=7), 14:22 +07, 7
  failures named in full in Check 1.
- Pointer guard: scripts/zen_backend.py lines 559-569 (re-ground) and
  625-635 (main), _dispatch fail-closed at line 387. Wait lines 514-524
  (ok True at 524); assert sent = received = False at line 618,
  ok = verified at line 639.
- Validator: scripts/zen_dom.py check_viewport_geometry, verified branch
  only inside the right_gap < 0 or bottom_gap < 0 block; direct A1/A2/A3
  calls in Check 3. ZenSession.viewport_origin (line 764) passes
  verified_moz_inner through (line 843), same limitation, no second
  verified path.
- Root discover: Ran 2131 in 175.507s, FAILED (failures=1, errors=5,
  skipped=17), 14:24:22 +07. Log /tmp/batch13-t1-discover-root.log was
  swept from /tmp during the batch 13 review session and no longer
  exists; the same totals are in the reviewers' logs kept under the
  goal hidden_files dir: b13c1-discover-root.log (failures=3, fresh
  boot), b13c3-discover-root-v.log (failures=2, fresh boot), and
  batch13-redteam-task1/discover-root.log (failures=2, fresh boot).
  Failures=1 holds on a long-uptime VM only; see the boot-time flake
  note in Check 4.
- Tests/ discover: Ran 2124 in 176.605s, FAILED (failures=1, errors=8,
  skipped=17), 14:29:49 +07. Log /tmp/batch13-t1-discover-tests.log was
  also swept; the same totals are in b13c1-discover-tests.log,
  b13c3-discover-tests.log, and
  batch13-redteam-task1/discover-tests-v.log under the goal
  hidden_files dir.
- Verbose root discover: Ran 2131 in 177.629s, FAILED (failures=1,
  errors=5, skipped=17), 14:34:03 +07. Log
  /tmp/batch13-t1-discover-root-v.log was also swept; see the
  reviewers' logs above.
- Related suites: 294 OK; unrun suites: 131 OK; both 14:26 +07.
- Commits verified: ce399c7, 507a50b, 03d99bc, all ancestors of
  todolist-push HEAD 3167c76.

## Fix pass (batch 13, 14:57 +07, 2026-11-22)

- This report was corrected in place by the batch 13 fix agent, per
  council 1 (395f357), council 2 (61eaba5), council 3 (3992f8f), and
  redteam (2b09b10). Verdict PASS stands; no code was changed.
- Corrections applied, each verified first-hand against todolist-push
  at 3167c76 and the worker log at 03d99bc before applying:
  1. Check 1: the 7 failing-first failure names are now given in full,
     with test file line numbers; the wtype build precondition is now
     stated in Scope and method and in Check 1 (bare checkout fails
     with 21 missing-helper errors first).
  2. Check 2: wait cited as lines 514-524 (was 515-522), assert
     sent = received = False at line 618 in branch 613-618 (was
     611-614), ok = verified at line 639 (was 640-641).
  3. Check 3: added the ZenSession.viewport_origin note (defined line
     764, passes verified_moz_inner through at line 843), so the A1/A2
     limitation applies on the live call path too, with no second
     verified path.
  4. Check 4: tesseract-present note corrected to the worker log 13:12
     entry (was 12:58); the "Firefox re-downloaded for batch 6" claim
     removed, it does not appear in the worker log (the log records
     /usr/bin/firefox as NOT existing); the tools/firefox binary
     existing at worker time now rests on test_bench_manifest passing
     then. Added the boot-time flake note: failures=1 holds on a
     long-uptime VM only, fresh-boot runs show failures=2 or 3 from
     the 121s subtraction in test_act_diagnostics and test_core.
  5. Environment note: same attribution correction, plus the advice to
     start a full discover more than about 2 minutes after a boot.
  6. Evidence index: the three cited /tmp logs were swept and no
     longer exist; the reviewers' surviving logs under the goal
     hidden_files dir are now cited instead.
- Reviewer corrections NOT applied, with reasons:
  1. Council 2's assert line 619: the assignment is at line 618
     (verified by grep), so 619 was not used; line 618 is cited.
  2. Council 2's wait range 514-522: ok True is at line 524, outside
     that range, so it was not used; lines 514-524 are cited.
  3. Council 1's assert lines 613-616 and ok lines 638-639: the
     assignment is at line 618 and ok = verified is at line 639 only
     (line 638 is the second `if action_type == 'assert':`), so the
     tighter lines 613-618 and 639 are cited.
