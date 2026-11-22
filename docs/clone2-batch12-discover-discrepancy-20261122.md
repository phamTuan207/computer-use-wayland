# Batch 12 task 1: discover count discrepancy 1974/1/5/17 vs 0/4, investigated and fixed

Work window: 2026-11-22 03:51 to 04:05 UTC (10:51 to 11:05 +07). Assignment:
coord/clone2.md, commit 0521d6c, batch 12 task 1. Runner throughout: system
python3 from tests/, `PYTHONPATH=../scripts:. python3 -m unittest discover
-s . -p "test_*.py"`, the same command the step-1 close-out used. Worktree:
~/workspace/tools/batch12-t1/wt-current. Logs preserved in
~/workspace/tools/batch12-t1/ (discover-current.log,
discover-current-fixed.log, fakebin/tesseract stub).

## 0. Answer up front

The 1 failure is `test_typed_text_check_fails_when_fragment_is_absent`
(tests/test_tc02_controller.py, Tc02MenuBarTests). The 5th error is
`test_typed_text_check_passes_when_fragment_is_visible` (same class). Both
are the tc02 tesseract pair: two tests that mock the tesseract invocation
but forget the `shutil.which('tesseract')` gate in front of it, so they fail
deterministically on any machine without tesseract on PATH. This machine has
no tesseract. The step-1 close-out machine did have it, which is the whole
0/4 vs 1/5 difference. The defect is REAL (non-hermetic tests), not a flake,
and it is FIXED here, test-only, by mocking `shutil.which` the way this same
test file already does elsewhere. After the fix the full discover at the
current tip is Ran 2024, 0 failures, 4 errors, skipped 17, the same shape
as the close-out.

## 1. The 6 problems at 65a2df6 (batch 11 task 3) and at 3724f52 (this run)

Batch 11 task 3 (report docs/clone2-batch11-discover-y1b-20261122.md, commit
53ce420) measured at tip 65a2df6: Ran 1974 tests in 180.748 s, FAILED
(failures=1, errors=5, skipped=17). I re-ran at the current tip 3724f52
(C5-B5-VERIFY, fetched 03:52 UTC): Ran 2024 tests in 176.606 s, FAILED
(failures=1, errors=5, skipped=17), exit 1, log
discover-current.log. The test count grew 1974 to 2024, exactly the 50
added `def test_` methods between the two tips (`git diff -U0 65a2df6
3724f52 -- 'tests/test_*.py'` counts 50 added test methods; biggest
contributors are the new S2 flip wiring tests and step-5 tests). The problem
set is IDENTICAL at both tips, in the same log order:

1. ERROR test_a11y_skeleton (unittest.loader._FailedTest): ImportError,
   ModuleNotFoundError: No module named 'tests'. Laptop-only import shape.
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
  Lines 1123 to 1125: if it is None, raise Escalate with reason
  'tesseract is unavailable; refusing to assume text presence'. Only after
  that gate does line 1149 call `subprocess.run([tesseract, ...])`.
- `_assert_typed_text_visible`, line 1174, calls `_ocr_text` and raises
  Escalate when the fragment is absent.

Test code, tests/test_tc02_controller.py, lines 640 to 671:

- `test_typed_text_check_passes_when_fragment_is_visible` (line 640)
  patches only `tc02_controller.subprocess.run` with a canned
  CompletedProcess returning 'note at 20:30.\n'.
- `test_typed_text_check_fails_when_fragment_is_absent` (line 657) patches
  only `tc02_controller.subprocess.run` with a canned CompletedProcess
  returning 'empty document\n', then asserts '20:30' is in the Escalate
  reason.

Neither test patches `shutil.which`. On a machine without tesseract, the
gate fires before the mocked `subprocess.run` is ever reached: the passes
test errors with the Escalate, and the fails test fails its assertIn
because the reason is the tesseract-unavailable string instead of the
fragment-absent string. The tests were written this way from the start
(commit 5a03991 added them; the which-gate arrived with 58704a2); the
defect is as old as the tests.

Proof, all on this VM (no tesseract: `which tesseract` finds nothing,
`find / -name 'tesseract*'` finds nothing, no tesseract entry in
/var/log/dpkg.log):

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
  tests, OK. The which-gate is the sole cause.
- The third test in the class,
  `test_typed_text_check_skips_plans_without_a_time_fragment` (line 676),
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
  file. A code change cannot explain the difference.
- Determinism (section 2): on a tesseract-less machine the pair fails
  every time; with tesseract on PATH it passes every time. The close-out's
  0-failure result therefore REQUIRES tesseract (or a same-named
  executable) on its machine's PATH at run time.
- This machine has none (section 2), and the close-out's own log files
  (/tmp/click4-discover.log, /tmp/step5-baseline-discover.log) are absent
  from this VM, which is consistent with the close-out having run on a
  different machine (the coordinator's worker VM or the laptop). This VM
  itself booted at about 02:47 UTC (uptime 1:10 at 03:57 UTC), after the
  close-out ran, so its /tmp cannot hold the close-out logs either way.
- The close-out log records no hostname and no `which tesseract` output,
  so the identity of its machine is UNVERIFIED from the repo record. What
  is verified is the mechanism: the only way these two tests pass is
  tesseract on PATH, and the only way they fail is tesseract absent.
  No other explanation fits code identity plus determinism.

Note the runs overlapped in time (close-out 01:50:43 to 01:54:54 UTC,
batch 11 task 3 about 01:51:46 to 01:54:47 UTC by its log mtime and
180.748 s duration), which rules out "tesseract was installed then
removed between the runs" as well: the two runs were concurrent on
different machines, and the wall-time gap (248.397 s vs 180.748 s) is VM
contention, as the close-out itself notes.

## 4. The fix (test-only, on main)

Both tests now also patch `tc02_controller.shutil.which` to return
'/usr/bin/tesseract', alongside the existing `subprocess.run` patch.
Diff (tests/test_tc02_controller.py, 8 lines changed, 2 hunks):

- test_typed_text_check_passes_when_fragment_is_visible, lines 652 to 655:
  the `with patch.object(tc02_controller.subprocess, 'run', ...)` gains a
  second context, `patch.object(tc02_controller.shutil, 'which',
  return_value='/usr/bin/tesseract')`.
- test_typed_text_check_fails_when_fragment_is_absent, lines 669 to 672:
  the same second context added.

This follows the file's own established pattern: line 457 already patches
`tc02_controller.shutil.which` with return_value='/usr/bin/code' for the
window-launch test, and lines 842 and 868 do the same. No production code
changed. The mocked path is never executed (subprocess.run is still
mocked); it only satisfies the gate. The third tc02 test and the
skipUnless-guarded `test_menu_bar_ocr_requires_file_and_edit_on_fixture_images`
are untouched and still behave as before.

Failing-first evidence on main, before the fix: the 2 tests give FAILED
(failures=1, errors=1). After the fix, on main:

- The 2 tests, 3 runs: OK, OK, OK.
- Whole module, system python3: Ran 46 tests in 0.200 s, OK (skipped=1,
  the properly guarded menu-bar OCR test).
- Whole module, venv python with dist-packages on PYTHONPATH: Ran 46
  tests, OK (skipped=1). py_compile OK.

Full-discover verification at the current tip 3724f52 with the fix applied
in the worktree (same 8 lines, file verified identical to the fixed main
file by diff): Ran 2024 tests in 198.344 s, FAILED (errors=4, skipped=17),
0 failures, exit 1, log discover-current-fixed.log. The 4 remaining errors
are exactly problems 1 to 4 above; the tc02 pair is gone. That is the same
shape as the close-out (0 failures, 4 errors), now reproduced on this VM.

## 5. Verdicts

- The 1 failure (`test_typed_text_check_fails_when_fragment_is_absent`):
  REAL test defect, FIXED. Non-hermetic test, deterministic on
  tesseract-less machines.
- The 5th error (`test_typed_text_check_passes_when_fragment_is_visible`):
  REAL test defect, same cause, FIXED with the same change.
- The other 4 errors (a11y skeleton import, cursor_file g++ -std=c++26,
  perf_evidence x2): pre-existing environmentals, unchanged, NOT fixed
  here. They are out of this task's scope and already documented in
  earlier reports (batch 5 crawl, batch 10 task 2, batch 11 task 3). The
  a11y and perf_evidence errors disappear from the repo root; the
  cursor_file error is a g++ 13.3.0 limitation.
- Flake verdict: neither tc02 problem is a flake. Both reproduce 3/3
  standalone and in every full discover on this VM, with a proven
  mechanism and a stub experiment isolating the single cause.
- Count growth 1974 to 2024 between 65a2df6 and 3724f52 is exactly 50
  added test methods, not a runner difference.

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
