# Batch 8 council 3: fail-before and neighbor regression reproduction

Council: independent re-run of the fail-before and neighbor regression
results in `docs/clone1-amend-verify-20261122.md`. Work done read-only in
the two worktrees `~/workspace/b8t2/base` at `e4082ff` (pre-fix) and
`~/workspace/b8t2/amend` at `4b7d6ac` (post-fix). Neither worktree was
modified: the base worktree already contained the task 2 agent's copied
test files, and I verified all 8 copied files are byte-identical to the
amend versions before running anything (`diff -q` MATCH on
`scripts/dom_act.py` and `tests/test_dom_act.py`,
`test_first_action.py`, `test_keyboard_preflight.py`,
`test_pick4_fastpath.py`, `test_session_continuation.py`,
`test_type_verification.py`, `test_zen_dom.py`). Base `git status` after
my runs is unchanged from before (6 modified test files, 2 untracked
new files); amend is clean. Run 2026-11-21 22:03-22:06 UTC. Method:
`python3 -m unittest <suite>` from each worktree's `tests/` directory.
Python 3.12.3. The suites use fakes, no live browser.

## 1. Fail-before at base (e4082ff): REPRODUCED exactly

New tests (amend versions) run against old code. Every count matches
the task 2 report exactly; times differ only by load variance.

| Suite | Tests | My result | Report | My time | Report time |
|---|---|---|---|---|---|
| test_first_action | 61 | FAILED, failures 3, errors 2 | 3, 2 | 0.610s | 0.604s |
| test_type_verification | 47 | FAILED, failures 1, errors 7 | 1, 7 | 0.281s | 0.313s |
| test_zen_dom | 25 | FAILED, failures 6, errors 9 | 6, 9 | 0.023s | 0.017s |
| test_dom_act | 10 | FAILED, errors 9 | 9 | 0.008s | 0.004s |
| test_pick4_fastpath | 28 | FAILED, errors 5 | 5 | 0.089s | 0.078s |
| test_session_continuation | 10 | OK | OK | 0.307s | 0.265s |
| test_keyboard_preflight | 32 | OK | OK | 0.120s | 0.112s |

Key failure names seen, all matching the report's list:

- R1 demo: `test_click_type_frame_changed_by_click_only_fails`
  (test_type_verification, FAIL).
- Item 2 flip: `test_stale_given_observation_pointer_only_refused`
  (test_first_action, FAIL).
- Item 7: `test_stale_given_observation_refusal_key_type_offers_window_only`
  (test_first_action, FAIL).
- Item 6: `test_session_type_verified_and_error_code_surfaced_in_envelope`
  and `test_fallback_type_verified_and_error_code_surfaced_in_envelope`
  (test_first_action, both ERROR).
- Item 8: `test_non_json_response_becomes_zen_dom_error` (ERROR) and
  `test_response_without_value_becomes_zen_dom_error` (FAIL).
- Item 9: `test_failed_restore_is_raised_not_swallowed` (FAIL) and
  `test_failed_restore_after_scan_is_raised` (FAIL).
- Item 10: `test_hung_handle_stops_scan_and_raises_wedge` (FAIL) and
  `test_raw_timeout_per_handle_stops_scan` (FAIL).
- Item 11: `test_switch_not_taking_effect_raises` (FAIL).
- Item 12: `test_viewport_origin_returns_moz_inner_screen`,
  `test_locate_point_is_rect_center_in_image`,
  `test_hit_check_passes_uncovered_fails_covered`,
  `test_focus_check_reads_active_element`,
  `test_field_value_and_verify_typed`,
  `test_grounding_accuracy_across_cases` (test_zen_dom and
  test_pick4_fastpath), `test_g30_dom_point_hits_and_old_eye_point_misses`
  (all ERROR).

Per-suite FAIL/ERROR name counts also match exactly: first_action 3 FAIL
+ 2 ERROR, type_verification 1 FAIL + 7 ERROR, zen_dom 6 FAIL + 9 ERROR,
dom_act 0 FAIL + 9 ERROR, pick4_fastpath 0 FAIL + 5 ERROR. Full logs in
`~/workspace/b8t2/c3-logs/base-*.log`.

## 2. Neighbor regression set, both trees: NO REGRESSION

12 modules: test_core, test_codemode, test_session_driver,
test_session_policy, test_session_continuation, test_phase3_c1,
test_phase3_c2, test_phase3_cleanup, test_json_limits,
test_observation_contract, test_act_diagnostics, test_fast_observe.

| Tree | Tests | Result | Time | Report time |
|---|---|---|---|---|
| base (e4082ff) | 209 | FAILED, failures 2 | 7.683s | 7.690s |
| amend (4b7d6ac) | 209 | FAILED, failures 2 | 7.651s | 8.037s |

Both failures are the same pre-existing test, identical on both trees:

- `test_core.SecureObservationFiles.test_private_mode_under_any_umask_in_isolated_child`
  (umask `0`)
- `test_core.SecureObservationFiles.test_private_mode_under_any_umask_in_isolated_child`
  (umask `0o777`)

Same test, same 2 subcases, same failure on base and amend. The diff
adds no new failure. Full logs in
`~/workspace/b8t2/c3-logs/base-neighbor.log` and
`~/workspace/b8t2/c3-logs/amend-neighbor.log`.

## 3. Amend pass confirmation

All 6 suites re-run at the amend worktree, all pass:

| Suite | Tests | Result | My time | Report time |
|---|---|---|---|---|
| test_first_action | 61 | OK | 0.587s | 0.629s |
| test_type_verification | 47 | OK | 0.413s | 0.424s |
| test_zen_dom | 25 | OK | 0.008s | 0.005s |
| test_dom_act | 10 | OK | 0.001s | 0.001s |
| test_pick4_fastpath | 28 | OK | 0.073s | 0.074s |
| test_session_continuation | 10 | OK | 0.226s | 0.242s |

Total 181 tests OK in 1.308s (report: 1.385s). Full logs in
`~/workspace/b8t2/c3-logs/amend-*.log`.

## 4. Verdict

- Fail-before: REPRODUCED. Every failure/error count and every key
  failure name in the task 2 report matches my independent re-run at
  base. The new tests do catch the bugs they guard.
- Neighbor regression: NO REGRESSION. The only 2 failures are the
  pre-existing test_core umask failures, identical on base and amend.
- Amend pass: CONFIRMED. All 6 suites pass at amend.

## 5. What could not be checked

- Live browser proof. These suites use fakes; no Zen or Brave ran on
  this VM. The live accuracy proof is owed by the 2-vision benchmark
  worker on the laptop, same as the task 2 report states.
- Full test discover was not re-run here either. The 6 suites, the
  12-module neighbor set, and the task 2 report's 13-suite run cover
  the regression surface flagged for this diff.
