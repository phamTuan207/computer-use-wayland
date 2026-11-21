# Batch 8 council 1: independent re-run of the 6 suites, 2026-11-22

Council 1 re-ran the 6 suites from the batch 8 task 2 report
(docs/clone1-amend-verify-20261122.md) on the amend worktree
`~/workspace/b8t2/amend` at `4b7d6ac` (clean tree, verified with
`git rev-parse HEAD` and `git status --short`, no output). Method:
`python3 -m unittest <suite>` in the worktree `tests/` directory.
Run 2026-11-21 22:04-22:05 UTC (05:04-05:05 +07). The suites use
fakes, no live browser. Memory at run time: 131 MB free, 381 MB
available. No coord edit, no commit, no push.

## 1. The 6 suites

| Suite | Tests | Result | My time | Report time | Verdict |
|---|---|---|---|---|---|
| test_first_action | 61 | OK | 0.594s | 0.629s | CONFIRMED |
| test_type_verification | 47 | OK | 0.473s | 0.424s | CONFIRMED |
| test_zen_dom | 25 | OK | 0.007s | 0.005s | CONFIRMED |
| test_dom_act | 10 | OK | 0.001s | 0.001s | CONFIRMED |
| test_pick4_fastpath | 28 | OK | 0.087s | 0.074s | CONFIRMED |
| test_session_continuation | 10 | OK | 0.327s | 0.242s | CONFIRMED |
| Total 6 suites | 181 | OK | 1.489s | 1.385s | CONFIRMED |

Test counts match the report exactly in all 6 suites (61, 47, 25,
10, 28, 10, total 181). Times are the per-suite times reported by
unittest itself. My summed time is 1.489s against the report's
1.385s, a 7.5% difference, all in the direction of slower runs
except test_first_action (0.594s against 0.629s, faster). This is
load variance on a tight machine, not a discrepancy: the counts
are exact and every suite passes. Note: my wall-clock computation
failed because `bc` is not installed on this machine; I used
unittest's own reported times instead, which are the figures
comparable with the report.

## 2. The 13-suite set

The 6 suites above plus test_keyboard_preflight, test_fast_observe,
test_act_diagnostics, test_guard_boundaries, test_pointer_safety,
test_focus, test_observation_contract, run in one unittest
invocation: 315 tests OK in 2.273s. The report says 315 tests OK in
2.239s. Count matches exactly; time differs by 0.034s (1.5%),
load variance. Verdict: CONFIRMED.

## 3. Verdict

All 6 suites CONFIRMED, 13-suite set CONFIRMED. The task 2
report's suite numbers reproduce exactly in count and pass status
on an independent re-run. No error to fix in the suite section of
the report.

## 4. What I could not check

- Live browser proof. These suites use fakes; no Zen or Brave ran
  here. Same limit as the task 2 report states.
- Fail-before at the base worktree and the 12-module neighbor
  regression set: those are council 3's lane, not re-checked here.
- The 12 fix items and the C12 evaluation: council 2's lane, not
  re-checked here.
