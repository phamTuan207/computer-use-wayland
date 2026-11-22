# Batch 13 council 2: review of task 1 P2-AMEND-FIX verification

## Verdict: AGREE with PASS, with two qualifications

The task 1 report (docs/batch13-task1-p2-amend-fix-verify-20261122.md,
commit e018ae0, verdict PASS) is correct. I re-ran its four checks
first-hand against the real code and tests, and all four confirm. Two
qualifications, neither of which changes the verdict:

1. My clean root discover gives failures=2, not failures=1. The extra
   failure is a boot-time artifact of a VM restart during my session,
   not a code defect and not an error in the task 1 report. See Check 4.
2. Two minor citation imprecisions (assert line numbers, one timestamp).
   Substance is correct in both cases. See Check 2 and Check 4.

No AMEND is needed. No fix work is needed.

## Scope and method

- Report branch: main. Code read read-only from branch todolist-push
  at HEAD 3167c76, in clean detached git worktrees. todolist-push was
  never modified and nothing was pushed to it.
- Ancestry verified with git merge-base: ce399c7 (tests), 507a50b
  (fix), and 03d99bc (worker log) are all ancestors of 3167c76.
- Times below are Asia/Ho_Chi_Minh (+07) on 2026-11-22, unless marked
  UTC.
- A runtime restart during this session wiped /tmp, deleting my first
  worktrees and their logs. I recreated the worktrees under
  ~/workspace/c2-t1-wt (3167c76), ~/workspace/c2-t1-wt-prefx (ce399c7),
  and ~/workspace/c2-t1-wt-base (ce399c7^), rebuilt the wtype helper,
  and redid the affected runs clean. Results already observed before
  the restart (P2 suite, failing-first, A1/A2 calls, related suites)
  were re-verified where cheap and are reported with the numbers
  observed in this session.
- No live Zen run was done: there is no laptop path available to this
  agent here. Same limitation as the task 1 report.
- No personal information in this report. No long dashes anywhere.

## Check 1: P2 suite re-run, worker claims 97 tests OK

AGREE.

- Fresh checkout first: from tests/ in the worktree,
  `PYTHONPATH=../scripts:. python3 -m unittest test_p2_element_ref`
  gave `Ran 97 tests`, `FAILED (errors=21)`, all 21 errors
  `RuntimeError: private wtype helper is missing: .../native/wtype`.
  This is the documented fresh-checkout state: docs/testing.md says a
  fresh checkout fails with exactly 21 such errors until the wtype
  helper is built. The task 1 report discloses that it built the
  helper first, so this is not a gap in its method.
- After building wtype with the docs/testing.md commands only,
  native/wtype is 35984 bytes, the same size the task 1 report and
  the docs record. Then the suite gave `Ran 97 tests in 0.157s`, `OK`,
  and on repeat `Ran 97 tests in 0.207s`, `OK`.
- Loader count confirms the total independently: 97 tests across 9
  classes with exactly the per-class counts the task 1 report lists
  (ElementRefTests 21, ScreenScopeLegalityTests 18, ZenBackendTests 14,
  ScreenPointFormTests 11, ValidatorFixTests 11,
  CodeExecPlanValidationTests 9, NoPointerDelegateTests 8,
  ValidatorLimitationTests 3, BackendRangeTests 2).
- The 86 baseline is confirmed too: loader count of
  test_p2_element_ref at ce399c7^ is 86, so 86 + 11 = 97, matching
  the task 1 report exactly. Method-definition counts agree as well:
  70 test methods at ce399c7^, 81 at ce399c7, a delta of 11.
- Failing-first confirmed in the ce399c7 worktree: `Ran 11 tests in
  0.005s`, `FAILED (failures=7)`. The 7 failures are exactly the ones
  the task 1 report names:
  test_main_path_type_reports_no_pointer_delegate,
  test_main_path_move_reports_no_pointer_delegate,
  test_reground_click_reports_no_pointer_delegate,
  test_reground_fill_reports_no_pointer_delegate,
  test_wait_reports_no_input_sent,
  test_assert_reports_no_input_sent,
  test_assert_mismatch_still_fails_without_input_sent. After the fix
  the same 11 tests give `Ran 11 tests`, `OK`.

## Check 2: pointer check at BOTH _dispatch call sites

AGREE, with a minor line-number drift noted below.

- There are exactly two `self._dispatch(` call sites in
  scripts/zen_backend.py at HEAD 3167c76: lines 569 and 635. Both are
  guarded by a `self._pointer is None` check immediately before the
  call: re-ground guard at line 559 (with the re_ground plan_rect and
  live_rect pair and error code no_pointer_delegate), main-path guard
  at line 625.
- `_dispatch` itself (line 387) returns (False, False) when the
  pointer is None, as a second fail-closed layer.
- The old 8-type allowlist is gone as code: the word allowlist
  appears only in a docstring and a comment (lines 398, 627). The
  only remaining mention of double_click, confirm_click, or
  hover_click is at lines 429-430 inside `_verify`, which classifies
  postconditions, not a dispatch guard.
- The 507a50b diff to scripts/zen_backend.py adds exactly 2
  `_pointer is None` guard sites, matching the two call sites.
- Wait and assert confirmed in code: wait sleeps only, then records
  input_sent False, target_received False, ok True (lines 514-522).
  Assert sets sent = received = False (line 619) and ok comes from
  the postcondition alone (`ok = verified`, line 639).
- Minor drift: the task 1 report cites the assert lines as 611-614
  and 640-641. The actual assignment lines are 619 and 639. The
  substance is correct, the line numbers are off by a few lines.

## Check 3: tests A1/A2 pin the validator limit correctly

AGREE.

- Code read, scripts/zen_dom.py check_viewport_geometry (line 107):
  the verified-origin branch runs only inside
  `if right_gap < 0 or bottom_gap < 0:` (closure overflow), returning
  the verified absolute origin at line 267. On the normal passing
  branch the code returns `absolute` at line 299, which is the
  moz-computed origin, and never reads verified_moz_inner.
- Direct calls, with the task 1 inputs (factor 1, window [2509, 914],
  size [925, 1176], inner [667, 1150], monitor
  [2464, 902, 1920, 1200]):
  - A1: moz [250, 18], absolute [2759, 932] returns [2759, 932].
    Gaps hand-checked: right_gap = 925 - 667 - 250 = 8, bottom_gap =
    1176 - 1150 - 18 = 8. Both non-negative, so the normal branch
    runs and the wrong but self-consistent moz is accepted.
  - A2: same inputs plus verified_moz_inner [240, 8] still returns
    [2759, 932]. The verified value is ignored on the passing branch.
  - A3 anchor: true moz [240, 8] returns [2749, 922]. Correct.
  - Control case: closure overflow (moz [274, 66], gaps -16, -40)
    with verified [240, 8] returns [2749, 922], the verified origin.
- The ValidatorLimitationTests docstring says these tests PIN the
  known limitation, they do not fix it, and the code agrees. No
  change to the validator itself was in either fix commit.

## Check 4: discover claim, worker reports Ran 2131, errors=1, skipped=17, failures=0

AGREE WITH QUALIFICATION. Counts confirm except one extra failure,
explained below as an environment artifact, not a code reason.

### Root discover, my clean re-run

- Command, from the repo root of the worktree:
  `PYTHONPATH=scripts:. python3 -m unittest discover -s tests -p
  'test_*.py'`, with the wtype helper already built and no other
  test process running in parallel.
- Output: `Ran 2131 tests in 309.452s`, `FAILED (failures=2, errors=5,
  skipped=17)`. Log: ~/workspace/c2-t1-discover-root-clean.log.
- The 5 errors match the task 1 report exactly, and I traced each
  cause in the log:
  1. test_cursor_file setUpClass, 1 error: g++ rejects -std=c++26.
  2. test_bench_manifest, 3 errors: FileNotFoundError
     `/home/hatch/workspace/tools/firefox/firefox`. The binary does
     not exist on this VM now (verified with ls).
  3. test_tc02_controller, 1 error: `tesseract is unavailable;
     refusing to assume text presence`. tesseract is not installed
     now: /usr/bin/tesseract does not exist and `which tesseract`
     finds nothing.
- The total (2131) and skip count (17) match the task 1 report
  exactly.
- No commit between 507a50b and 3167c76 touched
  scripts/bench_manifest.py, scripts/tc02_controller.py,
  tests/test_bench_manifest.py, or tests/test_tc02_controller.py
  (verified with git log, empty result). None of the 5 errors is a
  step 7 regression.

### The extra failure: failures=2, not failures=1

- Failure 1 is the task 1 failure:
  test_tc02_controller.Tc02MenuBarTests.
  test_typed_text_check_fails_when_fragment_is_absent, expecting
  '20:30' in the reason but getting the tesseract-unavailable
  reason. A direct consequence of the missing binary.
- Failure 2 is new in my run:
  test_act_diagnostics.ActDiagnostics.
  test_preflight_refusal_raises_before_any_diagnostics_query. It
  expects a PreflightRefusal matching `observation older than 120s`
  but got `capture_started_monotonic is invalid; observe again`.
- Root cause, verified first-hand: the test builds a meta with
  capture_started_monotonic set to time.monotonic() at call time
  (via cu._capture_identity in base_meta), then subtracts 121
  (OBSERVATION_MAX_AGE + 1). scripts/cu.py _valid_capture_identity
  rejects a value <= 0 as invalid before it ever reaches the age
  check. So the test only produces the expected `older than 120s`
  refusal when the machine has been up for more than 121 seconds.
  The runtime restart during this session reset time.monotonic(),
  and test_act_diagnostics runs early in discover order, so the
  test ran while uptime was still under 121 seconds.
- Proof it is the restart, not the code: re-running that single
  test now, with time.monotonic() at 451.2 seconds, gives `Ran 1
  test`, `OK`. The task 1 verifier ran on a long-uptime VM, so it
  saw failures=1. My failures=2 is the same suite on a freshly
  restarted VM.
- Implication for the coordinator: the task 1 discover numbers
  (failures=1) hold on a long-uptime VM only. On a freshly restarted
  VM the same suite shows failures=2 for this timing reason. No
  code change is needed for the fix, but the test is fragile: it
  assumes uptime over 121 seconds, and any future discover run
  started within 2 minutes of a restart will fail it again.

### My first discover attempt, and why it does not count

- My first root discover attempt gave `Ran 2131`, `FAILED
  (failures=1, errors=110, skipped=17)`. That number is my own
  contamination, not evidence against the task 1 report: the run
  started before I built wtype (105 of the 110 errors are
  `private wtype helper is missing`), and I ran other test
  processes in the same worktree in parallel. The clean re-run
  above supersedes it. Its log was lost in the /tmp wipe.

### Skip identities

- Confirmed directly, with the correct invocation from the repo
  root: test_menu_bar_ocr_requires_file_and_edit_on_fixture_images
  now skips (`tesseract is required by the menu-bar check`), while
  test_missing_tesseract_is_unverifiable now RUNS and passes
  (`ok`). That is the exact identity swap the task 1 report
  describes, caused by tesseract now being missing.
- Note: running either test standalone from tests/ with
  PYTHONPATH=../scripts:. fails at import with `No module named
  'scripts'`, because test_tc02_controller.py does
  `from scripts import tc02_controller` and needs the repo root on
  the path. That import error is my invocation mistake, not a test
  defect, and it is why the tests must be run from the repo root
  or with the root on PYTHONPATH.

### Worker log cross-check

- The worker log exists at 03d99bc
  (improvements/worker-click5-p2-amend-fix-log.md, 529 lines) and
  records the discover at 13:08:46 +07 as Ran 2131, errors=1,
  skipped=17, failures=0, with tesseract installed at that time.
  The task 1 report's reading of the worker numbers is correct.
- Minor imprecision: the task 1 report ties the tesseract-present
  note to 12:58 +07, but the 12:58 entry in the worker log is
  about native/wtype existing at pre-check time. The
  tesseract-present note sits under the 13:12 verbose-discover
  entry. The substance (tesseract present at worker discover time,
  gone now) is confirmed.

### Extra confirmations (not in the four assigned checks)

- Related 7 suites re-run:
  `test_zen_dom test_click3_redteam2 test_code_exec test_a1_preflight
  test_core test_first_action test_s0_bundle` gives `Ran 294 tests`,
  `OK`. Matches the task 1 report exactly.
- Previously unrun 3 suites: `test_keyboard_preflight
  test_click2_redteam test_pick4_fastpath` gives `Ran 131 tests`,
  `OK`. Matches the task 1 report exactly.
- Em dash check on the fix commits: 0 em dashes in the added lines
  of docs/testing.md in 507a50b, 0 in the zen_backend.py and cu.py
  diffs, 0 in the ce399c7 test diff.
- Step 7 scope check: `git show 292753f --stat` confirms 17 files,
  and no commit between 292753f and 3167c76 touched
  test_cursor_file.py, test_perf_evidence.py, test_a11y_skeleton.py,
  test_tc02_controller.py, or test_bench_manifest.py, so none of the
  discover errors is a step 7 regression.

## Errors, gaps, and missing checks in the task 1 report

1. Discover failure count: the task 1 report's failures=1 is correct
   for its long-uptime VM, but it does not warn that a freshly
   restarted VM shows failures=2 because of the uptime-sensitive
   test_act_diagnostics test. Gap in robustness of the reported
   number, not an error in the verification. No action needed for
   the fix.
2. Two minor citation imprecisions: assert line numbers (cited
   611-614 and 640-641, actual 619 and 639) and the tesseract
   timestamp (cited 12:58, the note sits under the 13:12 entry).
   Neither affects any verdict.
3. Not re-run here: the tests/ discover (Ran 2124, errors=8 per the
   task 1 report). The root discover above already covers the same
   modules and confirms every environment error item, so the
   marginal value was low. The live Zen and CLI runs were not
   re-run either: no laptop path is available to this agent here.
   Same live limitation as the task 1 report.
4. The P2 `97 OK` result is conditional on the documented wtype
   build step first. A fresh checkout without it fails with 21
   errors. The task 1 report discloses the build, so this is a
   note for the coordinator, not a finding against the report.

## Evidence index

- P2 suite: Ran 97, OK, twice (0.157s, 0.207s). Fresh checkout
  without wtype: Ran 97, FAILED (errors=21, all wtype-missing).
  wtype built: 35984 bytes.
- Loader counts: 97 at 3167c76, 86 at ce399c7^, 11 new test methods
  (70 to 81 by method count).
- Failing-first at ce399c7: Ran 11, FAILED (failures=7), 7 failures
  named in Check 1. After fix: Ran 11, OK.
- Pointer guard: scripts/zen_backend.py lines 559-569 (re-ground)
  and 625-635 (main), _dispatch fail-closed at line 387. Wait at
  lines 514-522, assert sent = received = False at line 619,
  ok = verified at line 639.
- Validator: scripts/zen_dom.py check_viewport_geometry, verified
  branch only inside the right_gap < 0 or bottom_gap < 0 block;
  returns at lines 267 (verified) and 299 (absolute). Direct
  A1/A2/A3/control calls in Check 3.
- Root discover (clean): Ran 2131 in 309.452s, FAILED (failures=2,
  errors=5, skipped=17). Log:
  ~/workspace/c2-t1-discover-root-clean.log.
- Extra failure: test_act_diagnostics.ActDiagnostics.
  test_preflight_refusal_raises_before_any_diagnostics_query.
  Standalone re-run now: Ran 1 test, OK (time.monotonic 451.2s).
- Skip swap: menu-bar test skipped, missing-tesseract test ok.
- Related suites: 294 OK; unrun suites: 131 OK.
- Commits verified: ce399c7, 507a50b, 03d99bc, 292753f, all
  ancestors of todolist-push HEAD 3167c76. Task 1 report:
  e018ae0.
