# Batch 13 council 3: review of task 1 P2-AMEND-FIX verification

## Verdict: AGREE with PASS

The task 1 report (docs/batch13-task1-p2-amend-fix-verify-20261122.md,
commit e018ae0, verdict PASS) is correct in substance. I re-ran its four
checks first-hand against the real code and the real test runs. Every
number the report claims reproduces, except one: my root discover shows
failures=2, not failures=1. The extra failure is a pre-existing
boot-time flake in an unrelated test, not a step 7 regression, so the
PASS verdict stands. No AMEND to the fix is needed. Two minor
imprecisions in the report (line ranges, one attribution) are listed
below; neither changes any conclusion.

## Scope and method

- Report branch: main. Code read read-only from branch todolist-push.
- todolist-push HEAD verified: 3167c76. Fix commits verified as
  ancestors: ce399c7 (tests) and 507a50b (fix).
- Full diffs of both fix commits read. Worker log read:
  improvements/worker-click5-p2-amend-fix-log.md (commit 03d99bc).
- Verification ran in clean git worktrees of todolist-push at 3167c76
  (~/workspace/b13c3-wt) and at ce399c7 (~/workspace/b13c3-wt-ce), so
  todolist-push was never modified. The wtype helper was built inside
  the main worktree only (gitignored build artifact, 35984 bytes).
- The VM restarted during this review (about 14:35 to 14:42 +07): it
  wiped the first /tmp worktrees and the first root discover run, which
  had no confirmed result. All work below was redone after the restart
  in worktrees under ~/workspace, with discover logs written to the
  goal hidden_files dir so they survive a restart.
- Times below are Asia/Ho_Chi_Minh (+07) on 2026-11-22.
- No personal information in this report. No long dashes anywhere in it.

## Check 1: P2 suite, worker claims 97 tests OK

AGREE.

- Command, 14:43 +07, from tests/ in the worktree:
  `PYTHONPATH=../scripts:. python3 -m unittest test_p2_element_ref`
- Output: `Ran 97 tests in 0.711s`, `OK`. Repeated: `Ran 97 tests in
  0.224s`, `OK`.
- Loader count confirms the total independently: 97 tests across 9
  classes (ElementRefTests 21, ScreenScopeLegalityTests 18,
  ZenBackendTests 14, ScreenPointFormTests 11, ValidatorFixTests 11,
  CodeExecPlanValidationTests 9, NoPointerDelegateTests 8,
  ValidatorLimitationTests 3, BackendRangeTests 2). Exact match with
  the report.
- The 11 new tests are exactly the methods added by ce399c7 (8
  NoPointerDelegateTests plus 3 ValidatorLimitationTests, confirmed
  from the diff). At the parent of ce399c7 the suite has Ran 86 tests,
  so 86 + 11 = 97, as the report claims. (The parent run shows 21
  wtype errors only, because that worktree has no built helper.)
- Failing-first, in the ce399c7 worktree, 14:43 +07: `Ran 11 tests`,
  `FAILED (failures=7)`. The 7 failures are exactly the predicted
  ones: test_main_path_type_reports_no_pointer_delegate,
  test_main_path_move_reports_no_pointer_delegate,
  test_reground_click_reports_no_pointer_delegate,
  test_reground_fill_reports_no_pointer_delegate,
  test_wait_reports_no_input_sent,
  test_assert_reports_no_input_sent,
  test_assert_mismatch_still_fails_without_input_sent. Main-path click
  passed pre-fix (old allowlist covered it). After the fix all 11 pass
  (`Ran 11 tests`, `OK`, 14:43 +07).
- Note for future verifiers: a fresh checkout without the built wtype
  helper fails the P2 suite with 21 errors, all `RuntimeError: private
  wtype helper is missing`. I reproduced that too, before building the
  helper. The report discloses this build step, and it is required.

## Check 2: pointer check at BOTH _dispatch call sites

AGREE in substance, with a minor line-range correction below.

- There are exactly two `self._dispatch(` call sites in
  scripts/zen_backend.py at HEAD 3167c76: lines 569 and 635. Both are
  guarded by a `self._pointer is None` check immediately before the
  call: line 559 (re-ground path, with the re_ground {plan_rect,
  live_rect} pair and error code no_pointer_delegate) and line 625
  (main path). The old 8-type allowlist is gone from the guard; the
  507a50b diff shows it removed and replaced by the unconditional
  check. The only remaining mention of double_click/confirm_click/
  hover_click is at lines 429-430 inside `_verify`, which classifies
  postconditions, not a dispatch guard.
- `_dispatch` itself still returns (False, False) when the pointer is
  None (check at line 387), as a second fail-closed layer.
- Wait records input_sent False, target_received False with ok True
  (block at lines 514-524; the ok True line is 524). Assert sets sent
  = received = False (line 618) and ok comes from the postcondition
  alone (`ok = verified`, line 639).
- Correction: the report cites assert as "lines 611-614 and 640-641"
  and wait as "lines 515-522". The real lines are 613-618 for the
  assert branch (sent = received = False at 618), 639 for
  `ok = verified`, and 524 for wait ok True. Substance is correct;
  the cited ranges are a few lines short.

## Check 3: tests A1/A2 pin the validator limit correctly

AGREE.

- Code read, scripts/zen_dom.py check_viewport_geometry: the
  verified-origin branch runs ONLY inside `if right_gap < 0 or
  bottom_gap < 0:` (line 203), returning the verified absolute origin
  at line 267. On the normal passing branch the code returns
  `absolute` at line 299, which IS the moz-computed origin.
  verified_moz_inner is never read on the normal branch. The
  ValidatorLimitationTests docstring says the same, and the code
  agrees.
- Direct calls, 14:43 +07 (factor 1, window [2509, 914], size
  [925, 1176], monitor [2464, 902, 1920, 1200]):
  - Gaps hand-checked: right_gap = 925 - 667 - 250 = 8, bottom_gap =
    1176 - 1150 - 18 = 8. Both non-negative, so the normal branch runs.
  - A1: moz [250, 18], absolute [2759, 932], inner [667, 1150]
    returns [2759, 932], 10px off the true origin [2749, 922]. Pin
    correct.
  - A2: same inputs plus verified_moz_inner [240, 8] still returns
    [2759, 932]. The verified value is ignored on the passing branch.
    Pin correct.
  - A3 anchor: true moz [240, 8] returns [2749, 922]. Correct.
  - Control case: closure overflow (moz [274, 66], gaps -16, -40)
    with verified [240, 8] returns [2749, 922], the verified origin.
    The verified-origin path only rescues the closure-overflow case.
- No change to the validator itself was in either fix commit, which is
  correct for a pin.

## Check 4: discover claim, worker reports Ran 2131, errors=1, skipped=17, failures=0

AGREE with one correction: my root discover shows failures=2, not
failures=1. The extra failure is explained below and is not a code
regression. All other numbers match.

### Root discover, my re-run (verbose)

- Command, started 14:43 +07, from the repo root of the worktree:
  `PYTHONPATH=scripts:. python3 -m unittest discover -s tests -p
  'test_*.py' -v`
- Output, finished 14:49 +07: `Ran 2131 tests in 316.504s`, `FAILED
  (failures=2, errors=5, skipped=17)`. Log:
  ~/workspace/goals/computer-use-wayland-zen-browser-control-research/hidden_files/b13c3-discover-root-v.log
- The 5 errors match the report exactly:
  1. test_cursor_file setUpClass: `RuntimeError: harness compile
     failed: g++: error: unrecognized command-line option
     '-std=c++26'; did you mean '-std=c++20'?`
  2. test_bench_manifest, 3 errors: `FileNotFoundError: [Errno 2] No
     such file or directory:
     '/home/hatch/workspace/tools/firefox/firefox'`. The builder
     hashes that path unconditionally (scripts/bench_manifest.py
     line 177, FIREFOX constant at line 58). The binary does not
     exist on this VM now (verified with ls, 14:43 +07).
  3. test_tc02_controller, 1 error: `tesseract is unavailable;
     refusing to assume text presence` (scripts/tc02_controller.py
     line 1124, via shutil.which). tesseract is not installed now:
     /usr/bin/tesseract does not exist and `which tesseract` finds
     nothing (verified 14:43 +07).
- The 2 failures:
  1. test_tc02_controller fragment-absent test: `assertIn('20:30',
     reason)` fails because the reason is the tesseract-unavailable
     message instead. Same as the report, direct consequence of the
     missing binary.
  2. NEW in my run: test_act_diagnostics
     test_preflight_refusal_raises_before_any_diagnostics_query. It
     expects PreflightRefusal matching "observation older than 120s"
     but got "capture_started_monotonic is invalid; observe again".
     This is a boot-time flake, not a step 7 regression; see the
     finding below.
- Why the environment explanation still holds:
  - No commit between 507a50b and 3167c76 touched
    scripts/bench_manifest.py, scripts/tc02_controller.py,
    tests/test_bench_manifest.py, or tests/test_tc02_controller.py
    (verified with git log, empty result).
  - The test count (2131) and skip count (17) match the worker claim
    exactly.

### Tests/ discover, my re-run (second worker number)

- Command, started 14:49 +07, from tests/:
  `PYTHONPATH=../scripts:. python3 -m unittest discover -s . -p
  'test_*.py'`
- Output, finished 14:54 +07: `Ran 2124 tests in 249.718s`, `FAILED
  (failures=1, errors=8, skipped=17)`. Log:
  ~/workspace/goals/computer-use-wayland-zen-browser-control-research/hidden_files/b13c3-discover-tests.log
- This matches the report's own re-run exactly (failures=1, errors=8,
  skipped=17). The 8 errors are the worker 4 (test_a11y_skeleton
  import, test_cursor_file g++ C++26, test_perf_evidence x2) plus
  bench_manifest x3 and tc02 visible x1. The 1 failure is the tc02
  fragment-absent test. No act_diagnostics failure here.

### Skip identities, verbose root discover

- Exactly 17 lines carry a skip reason: 12 cursor renderer missing
  (10 "cursor renderer missing" plus 2 "optional cursor renderer
  missing"), 3 Lua interpreter missing or unavailable, 1 hyprglass
  source not supplied, 1 tesseract. Same counts as the worker list
  (12 + 3 + 1 + 1 = 17), with the same identity swap the report
  describes: test_menu_bar_ocr_requires_file_and_edit_on_fixture_images
  now skips ("tesseract is required by the menu-bar check"), while
  test_missing_tesseract_is_unverifiable now RUNS and passes ("ok").
  Verified line by line from my verbose log.

## New finding: test_act_diagnostics fails only soon after boot (pre-existing flake)

- The test (tests/test_act_diagnostics.py, line 333) subtracts age =
  121 (OBSERVATION_MAX_AGE + 1) from capture_started_monotonic and
  expects the "observation older than 120s" refusal. But
  _valid_capture_identity (scripts/cu.py, line 795) first rejects any
  non-positive timestamp with "capture_started_monotonic is invalid".
  When the suite runs while time.monotonic() is under about 121 plus
  the test's offset into the run, the aged value goes to zero or
  below, and the validity check fires before the age check.
- Evidence this is boot timing, not code:
  - The VM restarted during this review. At 14:49 +07, /proc/uptime
    read 444.84s, so boot was about 14:42 +07. The verbose discover
    started about 14:43 +07 and test_act_diagnostics runs near the
    start (line 46 of the verbose log), when monotonic was roughly
    100 to 110s, so 108 minus 121 is negative. That matches the
    observed "is invalid" message exactly.
  - The same test passes standalone (`Ran 1 test`, `OK`) and
    in-module (`Ran 20 tests`, `OK`) at 14:49 +07, when monotonic
    was past 440s.
  - The tests/ discover, started later at 14:49 +07 when monotonic
    was past 460s, shows failures=1 with no act_diagnostics failure.
  - No commit between 292753f and 3167c76 touched
    tests/test_act_diagnostics.py (verified with git log, 0 commits),
    and scripts/cu.py was touched in that range only by 507a50b,
    which did not change _valid_capture_identity. So this cannot be
    a step 7 regression.
- Consequence for the coordinator: the "failures=1" root discover
  number is boot-state dependent. A discover started within about
  two minutes of a boot will show failures=2 instead. The report
  could not have seen this (its run was hours after boot), so this is
  a gap in the report, not an error in its run. A later step could
  harden the fixture (for example, age from a monotonic value that is
  guaranteed positive), but that is out of scope for this review and
  no fix is required for the P2-AMEND-FIX verdict.

## Extra confirmations (not in the four assigned checks, run for completeness)

- Related 7 suites re-run, 14:44 +07:
  `test_zen_dom test_click3_redteam2 test_code_exec test_a1_preflight
  test_core test_first_action test_s0_bundle` gives `Ran 294 tests`,
  `OK`. Matches the worker claim exactly.
- Previously unrun 3 suites, 14:44 +07: `test_keyboard_preflight
  test_click2_redteam test_pick4_fastpath` gives `Ran 131 tests`,
  `OK`. Matches the worker claim exactly.
- Em dash check on the fix commits: 0 em dashes in the added lines of
  507a50b (the 1 hit in the full `git show` output is a pre-existing
  context line, docs/testing.md line 12) and 0 in the ce399c7 test
  diff. docs/testing.md currently contains 9 pre-existing em dashes,
  matching the report's count.
- Step 7 scope check: `git show 292753f --stat` confirms 17 files,
  and no commit between 292753f and 3167c76 touched
  test_cursor_file.py, test_perf_evidence.py, test_a11y_skeleton.py,
  test_tc02_controller.py, or test_bench_manifest.py, so none of the
  discover errors is a step 7 regression.
- Worker log numbers verified against the worker log itself: tests/
  discover Ran 2124, errors=4, failures=0 at 13:05:25 +07; root
  discover Ran 2131, errors=1, failures=0 at 13:08:46 +07; the 4
  tests/ errors are the identities the report lists; the 17 skips are
  12 + 3 + 1 + 1 with test_missing_tesseract_is_unverifiable skipping
  because tesseract was installed at worker time.
- This report itself: 0 em dashes (checked with grep), no personal
  information (checked with grep for names and @).

## Minor corrections to the task 1 report

1. Check 2 line ranges: assert is lines 613-618 with sent = received
   = False at 618 and `ok = verified` at 639, not "611-614 and
   640-641". Wait ok True is at line 524, outside the cited
   "515-522". Substance is correct.
2. Attribution: the report says "The worker log records tesseract
   present at /usr/bin/tesseract at 12:58 +07 and Firefox
   re-downloaded for batch 6". The worker log records tesseract
   present at 12:58 and /usr/bin/firefox NOT existing; it does not
   record a Firefox re-download. The conclusion that the
   tools/firefox binary existed at 13:08 still follows, because
   test_bench_manifest passed then (worker root discover errors=1,
   only the g++ error), but the sentence over-attributes it to the
   worker log.
3. The report does not mention the act_diagnostics boot-time flake
   above. Its own run could not have seen it. Future verifiers
   should start a full discover more than about two minutes after a
   boot, or expect failures=2 from that one test.

## Limitation: live runs not re-run

- The worker live claims (Zen live run passed 13:22:29 +07 on the
  laptop, CLI act WITH/WITHOUT binding passed 13:38:38 +07) were NOT
  re-run from this VM in this session: there is no laptop path
  available to this agent here, and the brief did not ask for a live
  re-run. They rest on the worker log only, as the task 1 report
  already discloses. The code paths those live runs exercise
  (no-pointer refusal, wait input_sent False) are covered by the
  unit tests re-run above, which pass. No live evidence contradicts
  the fix.

## Environment note for the coordinator

- Two binaries the suite depends on are currently missing on this VM:
  /home/hatch/workspace/tools/firefox/firefox and tesseract
  (/usr/bin/tesseract, not on PATH). Both were present at the worker
  discover time (13:08 +07) and are gone now (14:43 +07). This is the
  same failure mode seen before on this machine (binaries disappearing
  across restarts or cleanups). Restore both before the next full
  discover, so the numbers are comparable to the worker run. No code
  change is needed for this.
- The VM restarted during this review, which also exposed the
  boot-time flake above. A discover started soon after a boot will
  show one extra failure in test_act_diagnostics.

## Evidence index

- P2 suite: Ran 97, OK, twice (0.711s, 0.224s), 14:43 +07.
- Pre-fix P2 total at ce399c7 parent: Ran 86 tests (21 wtype errors
  only), confirming 86 + 11 = 97.
- Failing-first at ce399c7: Ran 11, FAILED (failures=7), 14:43 +07, 7
  failures named in Check 1. Post-fix: Ran 11, OK.
- Pointer guard: scripts/zen_backend.py lines 559-569 (re-ground) and
  625-635 (main), _dispatch fail-closed at line 387, _verify
  classification at lines 429-430.
- Validator: scripts/zen_dom.py check_viewport_geometry, verified
  branch only inside the right_gap < 0 or bottom_gap < 0 block (line
  203, return verified at 267, return absolute at 299); direct A1/A2/
  A3/overflow calls in Check 3.
- Root discover (verbose): Ran 2131 in 316.504s, FAILED (failures=2,
  errors=5, skipped=17), 14:49 +07, log
  ~/workspace/goals/computer-use-wayland-zen-browser-control-research/hidden_files/b13c3-discover-root-v.log
- Tests/ discover: Ran 2124 in 249.718s, FAILED (failures=1,
  errors=8, skipped=17), 14:54 +07, log
  ~/workspace/goals/computer-use-wayland-zen-browser-control-research/hidden_files/b13c3-discover-tests.log
- Boot-time flake: test_act_diagnostics
  test_preflight_refusal_raises_before_any_diagnostics_query fails
  only when monotonic is under about 121s at fixture time; passes
  standalone and in-module at monotonic past 440s; 0 commits on the
  test file between 292753f and 3167c76.
- Related suites: 294 OK; unrun suites: 131 OK; both 14:44 +07.
- Commits verified: ce399c7, 507a50b, 03d99bc, 292753f, all ancestors
  of todolist-push HEAD 3167c76.
