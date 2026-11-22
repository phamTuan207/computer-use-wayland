# Batch 12 council 3: task 3 CB-8 audit review

- Date: 2026-11-22, 13:35 +07.
- Reviewer: council 3, independent of the task 3 auditor.
- Report reviewed: docs/batch12-task3-cb8-audit-20261122.md, commit 73a759e on main, 169 lines.
- Brief: batch 12 task 3 from Muse, commit 26ebe40, coord/clone1.md. Audit the 2 new DONE claims (a) S2 flip reopen PASS (5/5 runs, 10/10 messages, median 28.6s) and (b) (b1) 5/5 on Chromium (set_value + focus + CDP Enter). For each claim: is the evidence complete, verdict UPHELD or REVOKED, and what is missing named specifically. Do not invent evidence.
- Method: this council re-checked the report first-hand, read-only, from branch todolist-push at HEAD 4305dcb. Nothing on todolist-push was modified. Every number below was recomputed from the raw JSONs and logs by this council, not copied from the report.

## Brief coverage

| Brief requirement | Covered |
|---|---|
| Claim (a) audited: evidence complete or not, verdict, missing named specifically | Yes. Numbers verified correct, evidence incomplete, verdict REVOKED, 10 P9 PNG paths named exactly |
| Claim (b) audited: evidence complete or not, verdict, missing named specifically | Yes. Numbers verified correct, evidence incomplete, verdict REVOKED, 5 P9 PNG paths named exactly |
| No evidence invented | Yes. The report states it does not assume the screenshots, and names only files it checked for |
| Stay on the 2 claims only | Yes. No other claim is judged |

## Claim (a) numbers, re-verified by this council

- Walls in ms: run 1 29020.4, run 2 27799.1, run 3 28112.6, run 4 28898.1, run 5 28560.9. Sorted: 27799.1, 28112.6, 28560.9, 28898.1, 29020.4. Median 28560.9 ms, 28.6 s. The report is correct.
- Outcome sent in 10 of 10 browser halves. CB-1 input_sent, target_received, verified all True in 10 of 10. V12 found True at attempts 1 in 10 of 10, items Brave 43, 45, 47, 49, 51 and Chromium 54, 56, 58, 60, 62.
- Program elapsed ms: Brave 140.5, 137.5, 144.9, 140.8, 141.2. Chromium 113.0, 106.6, 107.1, 99.4, 104.2. dom_act ms from the program logs: Brave 51, 46, 46, 43, 43. Chromium 12, 9, 9, 8, 10. All match the report.
- Model calls 0 in all 5 runs. dry_run False in all 5 runs. chromium_set_value True in all 5 runs. program_variant "brave=fill,chromium=set_value" in all 5 runs.
- Observe elements: Brave 72, 73, 75, 77, 79, not truncated, routing dom-chromium complete coverage every run. Chromium 80, truncated, routing_relaxed True every run, composer present every run.
- activate False in all 5 runs (top-level field). Chromium pre-send count 0, items 51, 54, 56, 58, 60. Delayed count exactly 1, items 54, 56, 58, 60, 62. No double-send.
- The reopen log run table matches the JSONs exactly on every checked field (wall, program elapsed, dom_act ms, V12 items, observe elements). Median wall in the log, 28560.9 ms, matches the recomputed median.

## Claim (a) missing evidence, re-verified by this council

- The 10 P9 PNG paths in the report are exactly the paths in the run JSONs (p9.brave.png and p9.chromium.png, runs 1 to 5, ok True each). Confirmed from the JSONs.
- git ls-tree at commit 1a3356d for improvements/s2-flip-reopen-runs lists only run-1..5.json. No PNG. Same at todolist-push HEAD 4305dcb.
- git rev-list --all --objects, grep p9, returns nothing. No P9 PNG object exists in any commit in the whole repo history. Confirmed.
- The reopen log section 8 says the PNGs were "to be committed with this log". Confirmed at lines 333-336 of the log at 1a3356d. They were not committed.
- P9 is a scoring condition, not a nicety. The reopen log section 0 states verbatim: "P9: one final screenshot per run, reviewed before scoring (B1 condition: any DOM-vs-render mismatch FAILS the run)". Confirmed. The report's REVOKED verdict for claim (a) therefore rests on a real rule and a real absence, not on an interpretation.

## Claim (b) numbers, re-verified by this council

- Walls in ms: run 1 18477.4, run 2 20592.9, run 3 18839.7, run 4 18738.7, run 5 19094.0. Sorted: 18477.4, 18738.7, 18839.7, 19094.0, 20592.9. Median 18839.7 ms, 18.8 s. The report is correct.
- Program elapsed ms: 97.656, 106.622, 91.575, 102.811, 104.563. Range 91.575 to 106.622 ms, 91.6 to 106.6 ms. The report is correct.
- dom_act ms: 8, 9, 8, 7, 8. focus_enter ok True, focused TEXTAREA, enter 23, 23, 17, 18, 20 ms. CB-1 all True in all 5. V12 found True attempt 1, items 44, 46, 48, 50, 52. Pre count 0, items 41, 44, 46, 48, 50. Delayed count 1, items 44, 46, 48, 50, 52. Messages C5-B1-R1 to R5-CHROMIUM-IGNORE-TEST, each exactly once.
- Model calls 0 in all 5 runs. dry_run False in all 5 runs. program_variant "set_value" in all 5 runs.
- Aborts: runs 2 to 5 each have outcome aborted-routing with error "router fell through to screenshot: fail-closed fallback: no backend returned complete coverage". Confirmed from the aborted JSONs. The aborts are disclosed in the input-fix log and the aborted JSONs are preserved. Not a gap.
- The (b1) shape is re-proven by the reopen Chromium halves: 5 of 5 sent with set_value, focus_enter ok True, enter 25, 21, 23, 25, 23 ms, CB-1 all True, V12 attempt 1, pre 0, delayed 1. Confirmed.

## Claim (b) missing evidence, re-verified by this council

- The 5 P9 PNG paths in the report are exactly the paths in the (b1) run JSONs (p9.chromium.png, runs 1 to 5, ok True each). Confirmed from the JSONs.
- git ls-tree at todolist-push HEAD 4305dcb for improvements/s2-flip-b1-runs lists only run-1..5.json and run-2..5-aborted.json. No PNG. Same rev-list grep p9 result as above: nothing.
- The input-fix log commit record says the (b1) run JSONs plus P9 PNGs were "to be committed with this log". Confirmed at lines 511-514 of the log at 4bd6292. They were not committed.
- Mechanism confirmed from repo code: scripts/s2_flip_live.py line 76 LAPTOP_FOCUSENTER = '/tmp/c5-focusenter.mjs', build_program_set_value at line 129, focus_enter at line 497 with docstring "Runs /tmp/c5-focusenter.mjs (Runtime.evaluate focus plus". Input-fix log section 7.1 line 288: "dispatchKeyEvent ANSWERS in 2ms on the stuck tab", line 308: the stall is mouse-specific. The report's mechanism description is correct.

## Evidence-base citations, checked

- Reopen log: 346 lines at commit 1a3356d, hash recorded in 212e0ad. Correct. At tip it is 347 lines because 212e0ad added 1 line recording its own hash.
- Input-fix log: 523 lines at commit 4bd6292, hash recorded in 030c227. Correct. At tip it is 525 lines because 030c227 added lines recording its own hash.
- Reopen log section 5 P9 review ("P9 PASS 10/10") and section 6 verdict confirmed. Input-fix log section 7.5 P9 review ("P9 PASS all 5 runs") confirmed.
- Commit 4305dcb records "EXPAND approved in principle": confirmed in the commit message and in improvements/worker-click5-coord-log.md line 1054.
- The (b1) scored runs landed in commit 4bd6292. The aborted JSONs were committed in be2371e, per the input-fix log line 122. Correct.
- The report has 0 em dashes and 0 en dashes, and no personal info. Confirmed by grep.

## Correction 1 (minor, citation only)

- The report cites the input-fix log commit record as "section 8" in two places: the evidence-base table and the claim (b) "What is missing" text.
- The commit record is section 9. Section 8 is "Verdict: (b1) WORKS, 5/5 verified". The section headers at commit 4bd6292 are: section 7.5 Live 5-run measurement, section 8 Verdict, section 9 Commit record.
- The quoted words are real and the substance is unaffected: the "to be committed with this log" text is in the section 9 commit record. Fix: change "section 8" to "section 9" in both places.
- The reopen log citations are correct: its commit record really is section 8.

## Note 1 (method, not a gap)

- The brief asked the audit to build on task 1 results and not redo the work from scratch. The auditor could not do that: the task 1 report (docs/batch12-task1-s2-reopen-verify-20261122.md) was not on main when the audit ran, and it is still not on main now. No batch 12 task 1 commit exists on main. The auditor disclosed this and recomputed every number from the raw JSONs. This council independently recomputed the same numbers and they all match. The deviation was forced by timing, disclosed, and the recomputation is stronger than reuse. No correction needed.

## Note 2 (unverified aside, immaterial)

- The report says "The dry run 0 JSON lives in /tmp and is not committed". The repo side is verified: no dry-run JSON exists in improvements/s2-flip-reopen-runs on todolist-push. The /tmp side cannot be checked from this VM. The report itself says the dry run is not part of either claim, so this aside does not touch either verdict. No correction needed.

## Verdict: COMPLETE

- Both claims are audited. Both verdicts are given (REVOKED, REVOKED). Missing evidence is named specifically (15 exact PNG paths). No evidence is invented. Every number the report states was re-verified first-hand by this council from the raw JSONs and logs, and all of them are correct.
- The report did its own first-hand checks and did not reuse task 1 numbers: the task 1 report was not on main when it ran, and is still not on main. The statement holds.
- One minor citation correction applies (Correction 1 above). It does not change either verdict or the gating consequences. The REVOKED verdicts stand: the measured numbers are correct, and the render evidence required by the scoring procedure is missing in both claims.
