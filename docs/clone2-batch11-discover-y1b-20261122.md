# Batch 11 task 3: independent full discover at the current todolist-push tip + Y1b regression check

Work window: 2026-11-22 01:51 to 02:20 UTC (08:51 to 09:20 +07). Tip used:
65a2df6, 2026-11-22 01:49:16Z, "docs: COORD-CLICK-4 log start, batch 11 + 3 workers spawned,
Codex launch deferred to after P3". Worktree: ~/workspace/tools/batch11-t3/wt-current
(detached HEAD at 65a2df6). The gitignored build artifacts native/wtype and
native/keyboard-protocol.c/.h were copied in from the main checkout before running.
Without them a full discover at the same tip gives 3 failures and 240 errors (vs
1 failure and 5 errors with them), measured by me in
~/workspace/tools/batch11-t3/discover-noart.log; an independent council re-run
measured 150 errors + 2 failures under heavier parallel load, so the exact error
count is load-sensitive and the robust claim is hundreds of errors, spread across
the wtype-dependent modules (test_keyboard_preflight, test_type_verification,
test_click2_redteam, test_fast_observe, test_click3_redteam2, test_pointer_safety),
not just the RT2 suite. The 23 test_wtype_native tests never run without the
artifacts (setUpClass error, 0 tests run). No code or test was edited; this task
is verification only.

## Verdict

The suite is nearly green. From tests/, both runners agree exactly: Ran 1974 tests,
FAILED (failures=1, errors=5, skipped=17). From the repo root the same tip gives
Ran 1981 tests, FAILED (failures=1, errors=2, skipped=17); the 3 extra errors are
working-directory artifacts of running from tests/, not real failures. The Y1b
regression is GONE: all 8 problems found at 17fdb9b are fixed at the current tip,
7 by the RPC code change fd63a7d and 1 by the TESTREPAIR-D test amendment 29083cd.
All 5 formerly defective RT2 proof tests pass at this tip (RT2 Ran 51 tests, OK).
The 6 remaining problems from tests/ are all pre-existing environmentals, none a
production regression, none AMEND4, none Y1b.

## 1. Full discover numbers

Headline run, system python3 from tests/, PYTHONPATH=../scripts:. (the runner the
AMEND4 log uses), wall 01:51:53Z to 01:54:55Z:

- Ran 1974 tests in 180.748s, FAILED (failures=1, errors=5, skipped=17), exit 1.
  Log: ~/workspace/tools/batch11-t3/discover-current.log.

Every run at the current tip and at 17fdb9b, all re-run by me in my own worktrees:

| Run | Tip | Invocation | Ran | Fail | Err | Skip | Seconds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| system, from tests/ | 65a2df6 | system python3, PYTHONPATH=../scripts:. | 1974 | 1 | 5 | 17 | 180.748 |
| venv, from tests/ | 65a2df6 | venv python, PYTHONPATH=dist-packages:../scripts:. | 1974 | 1 | 5 | 17 | 177.142 |
| venv, from root | 65a2df6 | venv python, PYTHONPATH=dist-packages, -s tests | 1981 | 1 | 2 | 17 | 191.528 |
| system, from tests/ | 17fdb9b | system python3, PYTHONPATH=../scripts:. | 1927 | 11 | 9 | 17 | 357.478 |
| venv, from tests/ | 17fdb9b | venv python, PYTHONPATH=dist-packages:../scripts:. | 1927 | 11 | 9 | 17 | 184.508 |
| venv, from root | 17fdb9b | venv python, PYTHONPATH=dist-packages, -s tests | 1934 | 10 | 6 | 17 | 180.964 |

The two from-tests runs at the current tip have IDENTICAL problem sets (diff of the
sorted FAIL/ERROR lists is empty). The system run at 17fdb9b took 357.478 s, about
twice the other runs; no cause is established beyond parallel load on the shared VM
(sibling batch 11 subagents were running suites at the same time) plus the
test_cli_exit_codes failure present in that run. Timing is reported as measured.

Warning, verified live: a venv run WITHOUT system dist-packages on PYTHONPATH
collects only 1844 tests with 257 errors (ModuleNotFoundError: No module named
'PIL', 253 occurrences in the log) and is not a usable measurement. Log
discover-venv.log. Always put /usr/lib/python3/dist-packages on PYTHONPATH for
the venv runner.

## 2. The 6 remaining problems (from tests/)

All 6 are pre-existing environmentals, documented in earlier reports, with the
exact traces below from discover-current.log:

1. ERROR test_a11y_skeleton (unittest.loader._FailedTest): ImportError, failed to
   import test module, ModuleNotFoundError: No module named 'tests'. Laptop-only:
   the module imports the 'tests' package, which only resolves when the repo root
   is on sys.path. From the repo root this module imports and its 8 tests run.
2. ERROR setUpClass (test_cursor_file.CursorFileTests): harness compile failed,
   g++: error: unrecognized command-line option ‘-std=c++26’; did you mean
   ‘-std=c++20’? (exact characters as in the log, curly single quotes). The VM has
   g++ 13.3.0. Known, unchanged since batch 5.
3. ERROR test_valid_normal (test_perf_evidence.EvidenceChecks): the check script
   raises FileNotFoundError: docs/benchmarks/r5_cdp_aggregate.json. The file EXISTS
   in the worktree; the path is relative to the current directory, so it only
   resolves from the repo root. From the root this test passes. CWD artifact, not
   missing evidence.
4. ERROR test_valid_optimized (test_perf_evidence.EvidenceChecks): same cause as 3.
5. ERROR test_typed_text_check_passes_when_fragment_is_visible
   (test_tc02_controller.Tc02MenuBarTests): scripts.tc02_controller.Escalate:
   tesseract is unavailable; refusing to assume text presence. `which tesseract`
   finds nothing on this VM. Known environmental.
6. FAIL test_typed_text_check_fails_when_fragment_is_absent
   (test_tc02_controller.Tc02MenuBarTests): AssertionError: '20:30' not found in
   'tesseract is unavailable; refusing to assume text presence'. Same cause as 5.

From the repo root (venv, -s tests) problems 1, 3 and 4 disappear and only 3 remain:
the cursor_file setUpClass error and the tc02 pair. Nothing else in the suite fails.

## 3. Y1b answer: GONE

At tip 17fdb9b, batch 10 task 2 found 8 NEW problems in test_code_exec (4 failures,
3 errors) and test_codemode (1 failure), the executor recording zero backend calls,
consistent with the Y1b forked-child change 17fdb9b. I reproduced all 8 myself in a
second worktree (wt-y1b) at 17fdb9b, then traced them forward commit by commit:

| Tip | test_code_exec (55 tests) | test_codemode (26 tests) |
| --- | --- | --- |
| 17fdb9b, Y1b fix 2a/2b plain fork | FAILED (failures=4, errors=3), 11.957 s | FAILED (failures=1), 0.568 s |
| fd63a7d, Y1b fix 2a/2b (RPC) | OK, 12.323 s | FAILED (failures=1), 0.506 s |
| 29083cd, TESTREPAIR-D | OK, 12.429 s | OK, 0.666 s |
| 65a2df6, current tip | OK, 12.228 s | OK, 0.463 s |

The 8 problems decompose exactly:

- 7 fixed by the code change fd63a7d (2026-11-22 00:54:40Z, "Y1b fix 2a/2b (RPC):
  API calls run in the parent, snippet in a forked child"). Its commit body states
  the cause plainly: "The plain fork design broke 8 of the 81 executor tests:
  backend calls recorded in the child's FakeBackend copy were invisible to the
  parent, and observations/DOM snapshots mutated in the child were lost across
  runs." The fix is a socketpair RPC (_fork_api_session, _ApiChannel): the snippet
  runs in the forked child, every API call is marshalled to the parent, which
  executes it against the real backend and session state; the wall is still
  enforced by the parent killing the child at wall_seconds.
- 1 fixed by the test amendment 29083cd (2026-11-22 01:09:08Z, "TESTREPAIR-D:
  amend codemode builtins-pin test to capture via a temp file (exec now runs in
  the forked child); assertions unchanged in strength"). At fd63a7d the remaining
  failure is test_execute_namespace_pins_safe_builtins, AssertionError: 0 != 1;
  the test patches builtins.exec in-process, which a fork invalidates, exactly as
  fd63a7d's commit body says ("The codemode mock-exec pin test stays open").
  TESTREPAIR-D changes the capture mechanism to a temp file; the assertion
  strength is unchanged (verified by reading the diff: 38 insertions, 13
  deletions, all in tests/test_codemode.py).

At the current tip, test_code_exec and test_codemode are both fully green, standalone
and inside the full discover (zero entries in the discover problem lists). The Y1b
regression is gone, not merely reduced. No new problem replaced it in either file.

## 4. The 5 defective RT2 tests: all pass at this tip

RT2 standalone at the current tip, system python3 from tests/:
Ran 51 tests in 1.194 s, OK, exit 0. Log: rt2.log. All 5 formerly defective tests
pass by name:

- F2 test_region_fallback_readmits_raw_mozinner ... ok
- F3 test_stale_window_origin_accepted_silently ... ok
- F4 test_band_stacked_fields_low_click_with_x_range_must_not_verify ... ok
- F5-behavior test_band_wrong_field_unwired_path_reports_ok ... ok
- F6 test_typed_flag_forgeable_by_page_script ... ok

The suite grew from 49 to 51 tests. The 2 new methods, verified by diff between
17fdb9b and 65a2df6: test_stale_window_origin_refused_at_ground_time (the F3 split,
TESTREPAIR-B) and test_set_value_maxlength_uses_sanitized_length (TESTREPAIR-C8).

Important attribution: these 5 tests pass at this tip because the coordinator's
TESTREPAIR-B commit 43b27a1 ("repair the 5 defective RT2 proof tests (F2
assertRaises, F3 split, F4 y_range, F5 wired-path rewrite, F6 guarded forge +
value fix)") already landed them on todolist-push. Batch 11 task 1 is doing the
same repair in parallel on main; this run predates and is independent of that
work. Do NOT credit batch 11 task 1 for these passes on todolist-push.

Cross-check: the TESTREPAIR log's final verification (improvements/
worker-click3-testrepair-log.md, first committed in 77c72be on 2026-11-22 01:11:46Z;
its FINAL VERIFICATION section is headed "HEAD 29083cd") claims RT2 Ran 51 OK,
test_first_action Ran 71 OK, test_zen_dom Ran 42 OK, test_codemode Ran 26 OK. My
independent runs match all four exactly (RT2 51 OK, codemode 26 OK; first_action 71
and zen_dom 42 test counts confirmed by grep on the current tree).

## 5. Count reconciliation with the two prior measurements

Prior measurements, reconciled here against my re-runs at 17fdb9b and the redteam's
independent re-runs at 48c6aee and 0668327 (logs in
~/workspace/tools/batch11-t3-redteam/):

- Batch 10 task 2 at tip 48c6aee (venv, from root): 1927 tests, 20 failures,
  5 errors, 17 skipped, suite red as landed. With the stale doubles probe-fixed:
  1927 tests, 5 failures, 3 errors.
- Batch 10 task 2 fix pass at tip 17fdb9b (venv, from root): 1934 tests, 10
  failures, 6 errors, 17 skipped. 16 problems: 5 RT2 + tc02 pair + cursor_file
  error + 8 Y1b.
- DOT 9 task 1 post-fix (system, from tests/, tip 0668327): 1920 tests, 5 failures,
  6 errors, 17 skipped, matching the AMEND4 log's final counts exactly.
- This run at tip 65a2df6 (system and venv, from tests/): 1974 tests, 1 failure,
  5 errors, 17 skipped. From root: 1981 tests, 1 failure, 2 errors, 17 skipped.

Reconciliation, verified by re-running:

(a) The 16 problems at 17fdb9b are the stable reproducible core: 5 RT2 + tc02 pair +
cursor_file error + 8 Y1b. They decompose to zero at the current tip except the
3 pre-existing environmentals: 5 RT2 fixed by TESTREPAIR-B, 8 Y1b fixed by fd63a7d
plus TESTREPAIR-D, leaving the tc02 pair and the cursor_file error. The 3 extra
errors in my from-tests runs (a11y skeleton + 2 perf_evidence) are working-directory
artifacts (section 2), not new failures. Qualification: the 17fdb9b counts are
flake-sensitive. Independent re-runs at that tip see 16 to 20 problems: my root run
16, council 2's root re-run 17 (extra ime_cleanup flake, section 6), the redteam's
root re-run 18 (extra cdp_snapshot + cursor_session flakes), the redteam's system
re-run 19 problems with 10 failures (the cli_exit_codes flake absent there), my own
from-tests runs 20 (the 16 stable problems + the 3 working-directory errors + 1
flake each). Every extra entry is a load flake that decomposes to zero at the
current tip; the 16 stable problems are identical in every run.

(b) The historical "7-test runner gap" is a WORKING-DIRECTORY effect, not a runner
effect. Proof, by reproduction: at 17fdb9b the venv run from the repo root gives
1934 tests, 10 failures, 6 errors, 17 skipped, reproducing batch 10 task 2's numbers
exactly for the stable 16-problem core, including the identical problem list.
Qualification: the reproduction is exact for the stable core, not for the flake
margin. Council 2's independent root re-run at the same tip gave 1934/11/6/17
(one extra failure, the ime_cleanup flake) and the redteam's gave 1934/11/7/17
(two extra problems, the cdp_snapshot failure and the cursor_session error), so
the 17fdb9b root counts vary by +-1 failure and +0 to 1 error across re-runs. The
same tip run from tests/ gives 1927 tests, 11 failures, 9 errors, 17 skipped, in
BOTH runners (my system and venv runs agree exactly). Mechanism, verified: from
the root, test_a11y_skeleton imports successfully and its 8 tests run (from tests/
it is 1 import-error entry, +7 tests), and test_perf_evidence's relative path
docs/benchmarks/r5_cdp_aggregate.json resolves (its 2 tests pass instead of
erroring, -2 errors). 8 - 1 = +7 tests, -3 errors, exactly the observed gap. At the
current tip the same mechanism gives 1981 from root vs 1974 from tests/, again
exactly +7. Both runners agree at each working directory, so there is no runner
difference left to explain. The redteam also re-ran the two older tips: at 0668327
it reproduced 1920/5/6/17 exactly (the DOT 9 post-fix numbers), and at 48c6aee
1920/20/8/17 (failures 20 match batch 10 task 2's as-landed 20 exactly; errors 8
vs 5 differ by exactly the 3 laptop-only errors, from-tests vs from-root).

(c) The 47-test growth from 17fdb9b to 65a2df6 is exactly the 47 test methods added
between the tips (verified by git diff, 47 added, 0 removed, all 47 present in the
current discover logs): new files test_s0_bundle.py (29 methods) and
test_ssh_mux.py (12 methods), RT2 +2, test_first_action +3 (68 to 71), and
test_zen_dom +1 (41 to 42). test_click2_redteam (23 to 23) and test_browser_image
(9 to 9) added no test method; their diffs only add a helper, call sites, and
assertions inside existing tests. 29 + 12 + 2 + 3 + 1 = 47. From-tests:
1927 + 47 = 1974. From-root: 1934 + 47 = 1981. Both exact.

## 6. Flakes seen in passing

The failure counts at 17fdb9b and at the current tip are flake-sensitive under
parallel load on this shared VM. Every flake below appeared in exactly one run
each (unless noted) and passes standalone or in other full runs at the same tip.
None is a regression; none survives at the current tip as a failure.

- FAIL unittest.case.FunctionTestCase (test_cli_exit_codes): in my system run at
  17fdb9b and in council 1's independent full discover at the current tip. The
  guardian-leftover flake already flagged in batch 10 task 2. Absent in the
  redteam's system re-run at 17fdb9b and in my three runs at the current tip.
- FAIL test_partial_driver_json_marks_outcome_unknown
  (test_session_remote.SessionRemoteIntegration): in my venv from-tests run at
  17fdb9b only.
- FAIL test_exception_restores_ime_and_handlers
  (test_ime_cleanup.ImeCleanup): in council 2's root re-run at 17fdb9b only.
  Trace: the test expects 'caught ValueError' but got 'caught RuntimeError /
  fcitx5 state change timed out', a load-induced timeout pre-empting the test's
  own exception.
- FAIL test_snapshot_and_fill_contracts (test_cdp_snapshot.Snapshot): in the
  redteam's root re-run at 17fdb9b and in council 1's full discover at the current
  tip (hover-state node assertion).
- ERROR test_unproven_release_retains_snapshot_then_recover
  (test_cursor_session.Lifecycle): in the redteam's root re-run at 17fdb9b only.
- FAIL test_production_timeout_matrix (test_ime_cleanup.ImeCleanup), 3 scenarios
  (hang-deactivate-query, hang-restore-flag, hang-restore-query): in council 1's
  full discover at the current tip only.

Disclosure: council 1's independent full discover at the current tip gave
1974/6/5/17, not 1974/1/5/17: the 5 extra failures are the cdp_snapshot, 3x
ime_cleanup timeout-matrix, and cli_exit_codes flakes above, all passing standalone
at the same tip. The report's headline 1974/1/5/17 rests on my two agreeing runs
(system and venv from tests/, identical problem sets) plus the redteam's two
agreeing runs at the same tip (1974/1/5/17 in both runners, 1981/1/2/17 from root).
Neither flake failure above appears in my runs at the current tip as a failure,
nor in the redteam's runs at the current tip; council 1's independent run at the
same tip did see 5 of them as failures (see the disclosure above), all passing
standalone. A reader grepping for the test names will also find passing occurrences
in the current-tip logs. No conclusion is drawn about any flake beyond intermittency.

## 7. Logs preserved

All under ~/workspace/tools/batch11-t3/ (not /tmp, which gets wiped):

- discover-current.log: full discover, system runner, tip 65a2df6, 1974/1/5/17.
- discover-venv2.log: full discover, venv runner from tests/, tip 65a2df6, 1974/1/5/17.
- discover-current-venv-root.log: full discover, venv runner from root, tip 65a2df6,
  1981/1/2/17.
- discover-venv.log: BROKEN venv invocation without dist-packages on PYTHONPATH,
  1844 tests, 3 failures, 257 errors; kept as a warning, do not use.
- discover-17fdb9b-system.log: full discover, system runner, tip 17fdb9b, 1927/11/9/17.
- discover-17fdb9b-venv-v.log: full discover, venv runner from tests/, tip 17fdb9b,
  1927/11/9/17.
- discover-17fdb9b-venv-root.log: full discover, venv runner from root, tip 17fdb9b,
  1934/10/6/17, reproducing batch 10 task 2 exactly for the stable core.
- code_exec.log, codemode.log, rt2.log: standalone runs at the current tip, all OK.
- discover-noart.log: full discover WITHOUT the gitignored build artifacts, tip
  65a2df6, 1974 tests, 3 failures, 240 errors, 17 skipped (see the header note).
- noart-modules.log: targeted run of the 5 wtype-dependent modules without artifacts
  at 65a2df6, 215 tests, 191 errors.
- wt-current: worktree at 65a2df6. wt-y1b: worktree used for the 17fdb9b / fd63a7d /
  29083cd Y1b trace (left at 17fdb9b). wt-noart: worktree used for the no-artifact
  runs (left at 65a2df6).
