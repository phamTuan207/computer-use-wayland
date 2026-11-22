# Batch 12 task 1: discover count discrepancy 1974/1/5/17 vs 0/4, investigated and fixed

Work window: 2026-11-22 03:51 to 04:01 UTC (10:51 to 11:01 +07); fix pass
04:21 to 04:27 UTC. Assignment: coord/clone2.md, commit 0521d6c, batch 12
task 1. Runner throughout: system python3 from tests/,
`PYTHONPATH=../scripts:. python3 -m unittest discover -s . -p "test_*.py"`,
the same command the step-1 close-out used. Worktree:
~/workspace/tools/batch12-t1/wt-current. The worktree had the gitignored
native build artifacts copied in from the main checkout before the runs
(native/wtype, native/keyboard-protocol.c/.h); a bare worktree without them
gives hundreds of errors instead of the numbers here (council 2 and the
redteam both reproduced the 239-error bare-worktree result). Logs preserved
in ~/workspace/tools/batch12-t1/ (discover-current.log,
discover-current-fixed.log, discover-current-fixed2.log,
standalone-tc02.log, fakebin/tesseract stub).

## 0. Answer up front

The 1 failure is `test_typed_text_check_fails_when_fragment_is_absent`
(tests/test_tc02_controller.py, Tc02MenuBarTests). The 5th error is
`test_typed_text_check_passes_when_fragment_is_visible` (same class). Both
are the tc02 tesseract pair: two tests that mock the tesseract invocation
but forget the `shutil.which('tesseract')` gate in front of it, so they fail
deterministically on any machine without tesseract on PATH. This machine has
no tesseract. The step-1 close-out machine must have had tesseract (or a
same-named executable) on PATH, which is the whole 0/4 vs 1/5 difference.
The defect is REAL (non-hermetic tests), not a flake, and it is FIXED here,
test-only, by mocking `shutil.which` the way this same test file already
does elsewhere, plus one new test covering the gate itself. After the fix
the full discover at the current todolist-push tip is Ran 2025, 0 failures,
4 errors, skipped 17, the same shape as the close-out. Load caveat: the
redteam's independent re-run at the same tip gave 2 load-flake failures in
test_cursor_session (8 s wait_for deadline, passing standalone), so 0
failures is the measured result of the runs here, not a guarantee under
load; see section 5.

## 1. The 6 problems at 65a2df6 (batch 11 task 3) and at 3724f52 (this run)

Batch 11 task 3 (report docs/clone2-batch11-discover-y1b-20261122.md, commit
53ce420) measured at tip 65a2df6: Ran 1974 tests in 180.748 s, FAILED
(failures=1, errors=5, skipped=17). I re-ran at the current todolist-push
tip 3724f52 (C5-B5-VERIFY, fetched 03:52 UTC): Ran 2024 tests in 176.606 s, FAILED
(failures=1, errors=5, skipped=17), exit 1, log
discover-current.log. The test count grew 1974 to 2024, exactly the 50
added `def test_` methods between the two tips (`git diff -U0 65a2df6
3724f52 -- 'tests/test_*.py'` counts 50 added test methods; biggest
contributors are the new S2 flip wiring tests and step-5 tests). The problem
set is IDENTICAL at both tips, in the same log order:

1. ERROR test_a11y_skeleton (unittest.loader._FailedTest): ImportError,
   ModuleNotFoundError: No module named 'tests'. CWD-dependent import shape.
2. ERROR setUpClass (test_cursor_file.CursorFileTests): harness compile
   failed, g++ 13.3.0 does not recognize '-std=c++26'.
3. ERROR test_valid_normal (test_perf_evidence.EvidenceChecks):
   FileNotFoundError docs/benchmarks/r5_cdp_aggregate.json (relative path,
   resolves only from the repo root).
4. ERROR test_valid_optimized (test_perf_evidence.EvidenceChecks): same
   cause as 3.
5. ERROR test_typed_text_check_passes_when_fragment_is_visible
   (test_tc02_controller.Tc02MenuBarTests): scripts.tc02_controller.Escalate:
   tesseract is unavailable; refusing to assume text presence.
6. FAIL test_typed_text_check_fails_when_fragment_is_absent
   (test_tc02_controller.Tc02MenuBarTests): AssertionError: '20:30' not
   found in 'tesseract is unavailable; refusing to assume text presence'.

So the 1 failure is problem 6 and the 5th error is problem 5. Both are the
tc02 pair; problems 1 to 4 are the same four errors the close-out reported.

## 2. Mechanism: the tests mock the call but not the gate

Production code, scripts/tc02_controller.py:

- `_ocr_text`, line 1110. Line 1122: `tesseract = shutil.which('tesseract')`.
  Lines 1123 to 1125: if it is falsy, raise Escalate with reason
  'tesseract is unavailable; refusing to assume text presence'. Only after
  that gate does line 1145 call `subprocess.run([tesseract, ...])`.
- `_assert_typed_text_visible`, line 1174, calls `_ocr_text` and raises
  Escalate when the fragment is absent.

Test code, tests/test_tc02_controller.py, lines 640 to 670 (pre-fix
numbering):

- `test_typed_text_check_passes_when_fragment_is_visible` (line 640)
  patches only `tc02_controller.subprocess.run` with a canned
  CompletedProcess returning 'note at 20:30.\n'.
- `test_typed_text_check_fails_when_fragment_is_absent` (line 655) patches
  only `tc02_controller.subprocess.run` with a canned CompletedProcess
  returning 'empty document\n', then asserts '20:30' is in the Escalate
  reason.

Neither test patches `shutil.which`. On a machine without tesseract, the
gate fires before the mocked `subprocess.run` is ever reached: the passes
test errors with the Escalate, and the fails test fails its assertIn
because the reason is the tesseract-unavailable string instead of the
fragment-absent string. The tests were written this way from the start
(commit 5a03991 added them, and the which-gate was already in the exercised
path then, added by 5a03991 itself in `_assert_typed_text_visible`;
58704a2 later consolidated the two gates into `_ocr_text`); the defect is
as old as the tests.

Proof, all on this VM (no tesseract: `which tesseract` finds nothing,
`find / -name 'tesseract*'` found nothing when checked before the fakebin
stub below was created, the stub now exists at
~/workspace/tools/batch12-t1/fakebin/tesseract so that command today finds
it, no tesseract entry in /var/log/dpkg.log):

- Standalone, 3 runs: `PYTHONPATH=..:. python3 -m unittest
  test_tc02_controller.Tc02MenuBarTests.test_typed_text_check_passes_when_fragment_is_visible
  test_tc02_controller.Tc02MenuBarTests.test_typed_text_check_fails_when_fragment_is_absent`
  gives FAILED (failures=1, errors=1) all 3 times. Deterministic, not a
  flake. (First attempt used PYTHONPATH=../scripts:. and errored on import,
  ModuleNotFoundError: No module named 'scripts'; the correct standalone
  path is PYTHONPATH=..:. from tests/.)
- Stub experiment: a stub executable named `tesseract` placed in
  ~/workspace/tools/batch12-t1/fakebin/ (never executed; the tests still
  mock subprocess.run), prepended to PATH, makes both tests pass: Ran 2
  tests, OK. The which-gate is the sole cause. The standalone runs and the
  stub experiment are preserved in ~/workspace/tools/batch12-t1/
  standalone-tc02.log (fix-pass re-runs of the fixed tests; the pre-fix
  stub experiment was reproduced independently by council 1, 2, 3 and the
  redteam).
- The third test in the class,
  `test_typed_text_check_skips_plans_without_a_time_fragment` (line 672),
  does not reach the gate (no time fragment, early return) and is
  unaffected.

## 3. Reconciliation with the step-1 close-out: 0 failures, 4 errors at 36364b1

The close-out is commit 4ac9320 on todolist-push ("C4 step-1 closeout,
item-12 4/4 PASS, Codex-lane landed, discover 1974 0 failures, Y1b 8
gone"), section 4 of improvements/worker-click4-step1-closeout-log.md. It
ran the same command from tests/ in a clean worktree at HEAD 36364b1
(launched 08:50:43 +07, finished about 08:54:54 +07): Ran 1974 tests in
248.397 s, FAILED (errors=4, skipped=17), 0 failures. Its 4 errors are
exactly problems 1 to 4 above, and it states "No FAIL lines in the log
(grep for ^FAIL: returns nothing)".

The difference is exactly the tc02 pair, and it is environmental, not a
code difference:

- Code identity: `git diff 36364b1 65a2df6 -- tests/test_tc02_controller.py
  scripts/tc02_controller.py` is EMPTY. The tests and the controller are
  byte-identical at both tips. No commit between the tips touched either
  file. A code change cannot explain the difference. Stronger still, the
  whole-tree `git diff 36364b1 65a2df6` is exactly one file,
  improvements/worker-click4-coord-log.md, 90 insertions, so no code, plan,
  or fixture change of any kind can explain the difference (redteam).
- Determinism (section 2): on a tesseract-less machine the pair fails
  every time; with tesseract on PATH it passes every time. The close-out's
  0-failure result therefore REQUIRES tesseract (or a same-named
  executable) on its machine's PATH at run time.
- This machine has none (section 2), and the close-out's own log
  (/tmp/click4-discover.log) and the other worker's log it mentions
  (/tmp/step5-baseline-discover.log) are absent from this VM, which is
  consistent with the close-out having run on a different machine (the
  coordinator's worker VM or the laptop). This VM itself booted at about
  02:47 UTC (uptime 1:10 at 03:57 UTC), after the close-out ran, so its
  /tmp cannot hold the close-out logs either way.
- The close-out log records no hostname and no `which tesseract` output,
  so the identity of its machine is UNVERIFIED from the repo record. What
  is verified is the mechanism: the only way these two tests pass is
  tesseract on PATH, and the only way they fail is tesseract absent, given
  identical code and the observed environment. No other explanation fits
  code identity plus determinism.

Note the runs overlapped in time (close-out 01:50:43 to 01:54:54 UTC,
batch 11 task 3 ran 01:51:53Z to 01:54:55Z by its own report's wall
window), which rules out "tesseract was installed then removed between
the runs" as well: the two runs were concurrent on different machines,
and the wall-time gap (248.397 s vs 180.748 s) is VM contention, as the
close-out itself notes.

## 4. The fix (test-only, on main)

Both tests now also patch `tc02_controller.shutil.which`, alongside the
existing `subprocess.run` patch, but with an argument-sensitive fake
instead of a blanket return value (fix pass, redteam finding 1): a helper
`_which_with_tesseract`, tests/test_tc02_controller.py line 632, returns
'/usr/bin/tesseract' only when the name is 'tesseract' and delegates to
the real `shutil.which` otherwise. Diff (tests/test_tc02_controller.py,
final form, 3 hunks):

- `test_typed_text_check_passes_when_fragment_is_visible`, with-block
  lines 663 to 666: the `with patch.object(tc02_controller.subprocess,
  'run', ...)` gains a second context, `patch.object(
  tc02_controller.shutil, 'which', side_effect=_which_with_tesseract)`.
- `test_typed_text_check_fails_when_fragment_is_absent`, with-block lines
  680 to 683: the same second context added.
- New test `test_typed_text_check_escalates_when_tesseract_is_absent`,
  def line 688: patches `which` to return None and asserts
  `_assert_typed_text_visible` raises Escalate with 'tesseract is
  unavailable' in the reason (fix pass, redteam finding 2). The gate now
  has direct coverage instead of being covered only accidentally by the
  pair failing on tesseract-less machines.

This follows the file's own established pattern: line 457 already patches
`tc02_controller.shutil.which` with return_value='/usr/bin/code' for the
window-launch test, and lines 869 and 895 do the same with
return_value='/usr/bin/tesseract'. No production code changed. The mocked
path is never executed (subprocess.run is still mocked); it only satisfies
the gate. The third tc02 test and the skipUnless-guarded
`test_menu_bar_ocr_requires_file_and_edit_on_fixture_images` are untouched
and still behave as before.

Failing-first evidence on main, before the fix: the 2 tests give FAILED
(failures=1, errors=1). After the fix, on main:

- The 3 tests (pair plus gate test), 3 runs: OK, OK, OK.
- Whole module, system python3: Ran 47 tests in about 0.2 s, OK
  (skipped=1, the properly guarded menu-bar OCR test).
- Whole module, venv python ~/workspace/tools/venv/bin/python with
  dist-packages on PYTHONPATH: Ran 47 tests, OK (skipped=1). py_compile
  OK. Standalone evidence preserved in
  ~/workspace/tools/batch12-t1/standalone-tc02.log.

Mutation checks, run in the worktree (scratch, production file restored
afterwards): (A) changing scripts/tc02_controller.py:1122 from
`shutil.which('tesseract')` to `shutil.which('tesseract-ocr')` makes the
2 fixed tests fail (errors=2), so the argument-sensitive mock catches a
binary-name regression; with the first fix-pass form (blanket
return_value) they still passed. (B) hardcoding the gate to
`'/usr/bin/tesseract'` (bypassing which) makes the new gate test fail
(errors=1), so the gate test is sensitive to the gate.

Full-discover verification at the current tip 3724f52 with the final fix
applied in the worktree (file verified identical to the fixed main file by
diff): Ran 2025 tests in 176.354 s, FAILED (errors=4, skipped=17),
0 failures, exit 1, log discover-current-fixed2.log. The 4 remaining errors
are exactly problems 1 to 4 above; the tc02 pair is gone and the new gate
test passes. That is the same shape as the close-out (0 failures, 4
errors), now reproduced on this VM. (An earlier fixed run, log
discover-current-fixed.log, gave 2024/0/4/17 before the gate test was
added; the count grew by exactly that 1 test.)

## 5. Verdicts

- The 1 failure (`test_typed_text_check_fails_when_fragment_is_absent`):
  REAL test defect, FIXED. Non-hermetic test, deterministic on
  tesseract-less machines.
- The 5th error (`test_typed_text_check_passes_when_fragment_is_visible`):
  REAL test defect, same cause, FIXED with the same change.
- The gate itself: now directly covered by the new
  `test_typed_text_check_escalates_when_tesseract_is_absent`, mutation
  proven in both directions (section 4).
- The other 4 errors (a11y skeleton import, cursor_file g++ -std=c++26,
  perf_evidence x2): pre-existing environmentals, unchanged, NOT fixed
  here. They are out of this task's scope and already documented in
  earlier reports (batch 5 crawl, batch 10 task 2, batch 11 task 3). The
  a11y and perf_evidence errors disappear from the repo root; the
  cursor_file error is a g++ 13.3.0 limitation.
- Flake verdict: neither tc02 problem is a flake. Both reproduce 3/3
  standalone and in every full discover on this VM, with a proven
  mechanism and a stub experiment isolating the single cause.
- Load caveat on "0 failures": the redteam's independent re-run at the
  same tip with the fix gave Ran 2024 in 266.010 s, FAILED (failures=2,
  errors=4, skipped=17). The tc02 pair is gone and the 4 errors match, but
  test_cursor_session.Lifecycle.test_refusal_and_exception_end_session
  fails in 2 subTests with 'condition did not settle within test deadline'
  (the wait_for deadline is 8 s, tests/test_cursor_session.py:407-413);
  standalone the same test passes 3/3 in about 3.9 s each. The 266 s run
  against the report's 176 to 198 s runs is a timing-sensitive test failing
  under concurrent VM load, unrelated to tc02. The 0-failure headline is
  the measured result of the runs in section 4, not a guarantee under
  load, and the 8 s deadline is a known-fragile spot if the suite is
  re-run under load.
- Count growth 1974 to 2024 between 65a2df6 and 3724f52 is exactly 50
  added test methods, not a runner difference; the fix pass adds 1 more
  (the gate test), taking the suite to 2025.

## 6. Open items

- The fix lives on main only. todolist-push still carries the defective
  tests (its tip moved to 4e3b42d during this task; the tc02 files are
  unchanged between 3724f52 and 4e3b42d, so the fix applies cleanly).
  Porting to todolist-push is the coordinator's decision, not mine.
- The close-out machine's identity is UNVERIFIED (section 3). If the
  coordinator wants it pinned, the close-out worker would need to record
  hostname and `which tesseract` output.
- The 4 remaining errors are still open environmentals for the
  coordinator to disposition (install tesseract on this VM, or accept the
  tc02 pair as environmental and skip it where tesseract is absent; note
  the third test in the class is already properly skip-guarded, so
  skipping the pair the same way would also be a defensible fix, but
  mocking which is stronger because it tests the logic instead of
  skipping it).

## 7. Council + redteam + fix pass

Report commit 067745d, fix commit c7bc697. Council 1 ISSUES (1 factual,
4 minor), council 2 ISSUES (3 corrections, 4 minor nits), council 3
ISSUES (7 corrections, 6 minor nits), redteam ISSUES (minor only, 4
findings). Every correction was applied and verified against primary
sources, except three that were checked and REJECTED with evidence:

- Council 1 correction 2 and council 2 nit 4 ("the defect dates to
  58704a2, the tests were correct as written") are WRONG. `git show
  5a03991 -- scripts/tc02_controller.py` adds a which-gate in
  `_assert_typed_text_visible` (diff line 60, `+
  tesseract = shutil.which('tesseract')`, the gate at line 1078 of the
  5a03991 file), in the same commit that added the tests. The tests were
  never correct as written on a tesseract-less machine. 58704a2 only
  consolidated the two pre-existing gates into `_ocr_text`. Council 3's
  wording (section 2) is the correct one.
- Council 3 correction 4 ("lines 838 and 864") cites the pre-fix tip
  file; the report's "lines 842 and 868" were the numbers in the fixed
  file at report time, verified by grep then. After the fix pass the same
  two sites are at lines 869 and 895 (section 4), which is what the
  report now says.

Applied in the fix pass: line 1149 to 1145 for the subprocess.run call;
provenance wording (council 3); pre-fix test line numbers 640/655/672
and range 640-670 in section 2; fix hunk ranges 651-654 and 668-671 in
the first fix form, now 663-666 and 680-683 in the final form; step-5 log
attribution (only /tmp/click4-discover.log is the close-out's own);
batch 11 run times from its own report's wall window (01:51:53Z to
01:54:55Z); "Laptop-only" to "CWD-dependent"; "if it is None" to "if it
is falsy"; "current tip" to "current todolist-push tip"; section 0 hedge
to "must have had"; find-claim qualified (stub created after the check);
venv path named (~/workspace/tools/venv/bin/python); work window end
corrected to 04:01 UTC; whole-tree diff (one file, 90 insertions) added
to section 3; native-artifact copy step documented in the header; "only
way they fail" scoped; standalone evidence preserved in
standalone-tc02.log; module time stated as about 0.2 s.

Redteam findings, all applied: (1) the mock is now argument-sensitive
(`_which_with_tesseract`, line 632), mutation-proven: renaming the
binary to 'tesseract-ocr' now fails both tests; (2) the gate now has a
dedicated test (`test_typed_text_check_escalates_when_tesseract_is_absent`),
mutation-proven: bypassing the gate fails it; (3) the native-artifact
copy step is documented; (4) the load caveat on "0 failures" is in
sections 0 and 5, with the redteam's 2024/2/4/17 re-run numbers and the
8 s wait_for deadline cited.

Fix-pass commits: test change (side_effect helper plus gate test) and
this report update, each its own small commit, pushed. The core verdict
is unchanged by any of this: the 1 failure and the 5th error are the
tc02 tesseract pair, a real non-hermetic-test defect, fixed test-only.
