# Batch 12 council 2: review of task 3 CB-8 audit

- Date: 2026-11-22, 13:30 +07.
- Reviewer: clone1 council 2, independent of the task 3 auditor.
- Report reviewed: docs/batch12-task3-cb8-audit-20261122.md, commit 73a759e on main, 169 lines.
- Method: every factual premise re-checked first-hand, read-only, from branch todolist-push at HEAD 4305dcb, plus the batch 12 task 1 report (428 lines, still uncommitted in the working tree, read for reconciliation) and the batch 12 task 2 landing spec (docs/batch12-task2-b1-landing-spec-20261122.md, commit 55405a5, 491 lines). Nothing on todolist-push was modified. No em dash or en dash anywhere in this file. No personal info.
- Verdict scale: STANDS means the finding follows from the rule and the evidence as cited. NEEDS CHANGE means the reasoning or the stated consequence is wrong and must be fixed in the report.

## Verdict summary

| Finding | Verdict |
|---|---|
| F1. Numbers in claim (a) and claim (b) are correct | STANDS |
| F2. The 15 P9 PNGs are missing from the repo | STANDS |
| F3. CB-8 rule applied, both claims REVOKED | STANDS |
| F4. P9 is a scoring condition, consequence not overstated | STANDS |
| F5. p9.ok True proves capture only, not review | STANDS |
| F6. Log prose is the claim, not evidence for it | STANDS |
| F7. Repair path: 15 PNGs at exact paths, re-audit only the PNGs | STANDS |
| F8. Gating consequence (a): EXPAND approval should wait | STANDS |
| F9. Gating consequence (b): landing waits, or records the gap as open | STANDS, and live |
| F10. Relaxed routing is a qualification, not a gap | STANDS |
| F11. (b1) aborts are disclosed, not hidden | STANDS |
| F12. Focus-enter helper named as secondary gap only | STANDS |
| F13. Method note and task 1 reconciliation | STANDS |

Overall: the audit STANDS as written. Both REVOKED verdicts follow from the CB-8 rule and the evidence. No finding needs change.

## F1. Numbers in claim (a) and claim (b) are correct. STANDS.

Recomputed from the raw JSONs on todolist-push, all 5 runs of each series:

- Reopen walls in ms: 29020.4, 27799.1, 28112.6, 28898.1, 28560.9. Sorted: 27799.1, 28112.6, 28560.9, 28898.1, 29020.4. Median 28560.9 ms, which is 28.6 s. Matches the audit exactly.
- (b1) walls in ms: 18477.4, 20592.9, 18839.7, 18738.7, 19094.0. Sorted: 18477.4, 18738.7, 18839.7, 19094.0, 20592.9. Median 18839.7 ms, which is 18.8 s. Matches the audit exactly.
- Reopen program elapsed: Brave 140.5, 137.5, 144.9, 140.8, 141.2 ms; Chromium 113.0, 106.6, 107.1, 99.4, 104.2 ms. dom_act: Brave 51, 46, 46, 43, 43 ms; Chromium 12, 9, 9, 8, 10 ms. All match the audit.
- (b1) program elapsed: 97.7, 106.6, 91.6, 102.8, 104.6 ms. Range 91.575 to 106.622 ms, which is 91.6 to 106.6 ms. Matches the audit.
- Focus Enter: reopen Chromium 25, 21, 23, 25, 23 ms; (b1) 23, 23, 17, 18, 20 ms. Matches the audit.
- V12 found True attempt 1, CB-1 all three True, in all 10 reopen sends and all 5 (b1) sends. V12 items match the audit in every run checked (reopen Brave 43 to 51, Chromium 54 to 62; (b1) 44 to 52).
- Chromium pre-send count 0 and delayed count exactly 1 in every run of both series. Reopen pre items 51, 54, 56, 58, 60; delayed items 54, 56, 58, 60, 62. Matches the audit exactly.
- Observe elements: Brave 72, 73, 75, 77, 79, truncated False; Chromium 80, truncated True, routing_relaxed True, composer present, every run. Brave routing run 1 reads "complete coverage: 72 elements, not truncated", fell_through empty. Strict routing on Brave confirmed.
- Model calls 0, dry_run False, in all 10 run JSONs. program_variant "brave=fill,chromium=set_value" and chromium_set_value True in all 5 reopen runs; program_variant "set_value" in all 5 (b1) runs. activate False in all 10 run JSONs. All match the audit.
- The reopen log run table matches the JSONs on every field spot-checked (run 1 and run 5, both browsers: wall, program elapsed, dom_act ms, V12 items, CB-1, pre and delayed counts).
- The batch 12 task 2 spec independently recomputed the same medians, elapsed ranges, Enter ranges, pre and delayed counts. The batch 12 task 1 report independently recomputed the same walls, sorted list, median 28560.9 ms, per-send 10/10 and per-run 5/5. Three independent recomputations agree. The numbers are not the problem, as the audit says.

## F2. The 15 P9 PNGs are missing from the repo. STANDS.

Three checks, all first-hand:

- git ls-tree at commit 1a3356d for improvements/s2-flip-reopen-runs lists only run-1..5.json. No PNG.
- git ls-tree at todolist-push HEAD 4305dcb for improvements/s2-flip-reopen-runs lists only run-1..5.json, and for improvements/s2-flip-b1-runs lists only run-1..5.json and run-2..5-aborted.json. No PNG.
- git rev-list --all --objects, grep p9, returns nothing. No P9 PNG object exists in any commit visible in this clone.
- The JSONs reference exactly the paths the audit lists. Sampled run-1.json and run-5.json of both series: p9.png is improvements/s2-flip-reopen-runs/p9-runN-brave.png and p9-runN-chromium.png, and improvements/s2-flip-b1-runs/p9-runN-chromium.png, with p9.ok True in each.
- Both logs promise the PNGs and do not deliver them. Reopen log section 8: "Re-open run JSONs + P9 PNGs: improvements/s2-flip-reopen-runs/run-1..5.json plus p9-runN-brave.png and p9-runN-chromium.png (to be committed with this log)". Input-fix log lines 511 and 514: the (a1) and (b1) run JSONs plus P9 PNGs "(to be committed with this log)".
- Independent corroboration: the batch 12 task 1 report, section 9 item A, found the same gap by a different method (GitHub API directory listing and recursive tree at 4305dcb, zero p9-run matches) and calls it a material gap.
- Log line counts cited in the audit are correct at the cited commits: reopen log 346 lines at 1a3356d, input-fix log 523 lines at 4bd6292. (HEAD counts are 347 and 525 because later commits added lines; the audit cited the commits it read.)

## F3. CB-8 rule applied, both claims REVOKED. STANDS.

- The rule as the audit states it matches the coordinator brief for this task (coord/clone1.md, batch 12 task 3: DONE must have concrete evidence, test command, output, commit hash, time log, otherwise revoked) and the standing rule in improvements/worker-click3-final-direction-log.md, CB-8 row: DONE means a specific named evidence exists, and any proposal whose DONE basis is a fixture-only proof gets its DONE revoked until live evidence exists.
- The audit applies the rule to the PASS verdict itself, not to the measured numbers. That is the correct scope: the numbers are verified and stay verified; what is revoked is the DONE/PASS standing, which rests on a render check no reviewer can repeat from the repo.
- Precedent is directly on point. Batch 10 task 3 applied the same rule and revoked (a) S2 Pick 1 and (c) DOM-grounding for the same pattern, prose claims with raw records absent from the repo, and councils 1, 2, 3 and redteam agreed and the coordinator accepted it. This audit follows that precedent exactly.
- The audit is careful about scope in the right places: the relaxed routing gate and the activate False field are treated as disclosed qualifications, not gaps, and the dry run 0 JSON in /tmp is correctly excluded because the dry run is not part of either claim. The verdicts are narrow, as the audit says: only the render evidence is missing, and only that is what the revocation turns on.

## F4. P9 is a scoring condition, consequence not overstated. STANDS.

This is the finding the council was asked to test hardest, because the final-direction log calls P9 "unscored human evidence". The apparent tension resolves in favor of the audit. The final-direction log, rung 2, says in full: "One final screenshot is kept as unscored human evidence (P9); it must not feed the score. HARD CONDITION (F2, section 2 item (b)): the final screenshot must be reviewed before a run scores as passed, and any DOM-vs-render mismatch FAILS the run."

- "Unscored" means the screenshot contributes no points to the score. It does not mean the review is optional.
- The hard condition makes the review a precondition for a run scoring as passed, and a mismatch fails the run. That is a scoring condition in the gate sense, which is exactly how the audit uses the term.
- The reopen log section 0 states the same procedure for this measurement: "P9: one final screenshot per run, reviewed before scoring (B1 condition: any DOM-vs-render mismatch FAILS the run)."
- The audit does not claim P9 feeds the score. It claims only that a PASS verdict whose render check cannot be checked by any reviewer does not meet CB-8. That follows: V12 and CB-1 both read the DOM, neither checks rendering, and P9 is the only render check in the procedure.
- The consequence is therefore not overstated. A missing P9 review blocks a PASS verdict under the procedure the workers themselves wrote, and it blocks a DONE claim under CB-8.

## F5. p9.ok True proves capture only, not review. STANDS.

- p9.ok is a machine field set by the harness when the capture call returns ok. Sampled JSONs show p9.ok True with a png path and a wall_ms for the capture. Nothing in that field records that a human opened the image.
- The audit is right to treat it as proof that the capture call succeeded, and as no proof at all that any reviewer read the image. The two are different facts, and only the second is what the hard condition requires.

## F6. Log prose is the claim, not evidence for it. STANDS.

- Reopen log section 5 claims "P9 PASS 10/10" with one prose description per run. Input-fix log section 7.5 claims "P9 PASS all 5 runs". Both describe what the worker says it saw.
- Prose describing a review is the claim that a review happened. It cannot substitute for the artifact the review was of, because no independent reviewer can re-perform the review from prose. This is the same reasoning batch 10 task 3 applied, and it is correct here.

## F7. Repair path: 15 PNGs at exact paths, re-audit only the PNGs. STANDS.

- Committing the 10 reopen PNGs and the 5 (b1) PNGs at exactly the paths the JSONs reference is the right repair: it makes the p9.png pointers resolve, so any reviewer can open the exact files the procedure required.
- Re-audit scoped to the PNGs only is sound. The run JSONs are committed and content-addressed by git, and the numeric checks are already recorded first-hand in this audit with three-way agreement (audit, task 1, task 2 spec). Nothing in the numeric layer needs redoing.
- Repair item 3 is correct and important: if the laptop PNG files are gone, re-capture equivalent shots and label them as re-captures, and do not rewrite the logs to pretend the originals were committed.
- Repair item 4 is correct as a secondary item: commit the focus-enter helper code or record its exact hash, so the Enter mechanism is reviewable from the branch.
- Minor strengthening note, not a change: the re-audit should confirm the bubble text in each PNG matches that run's message (the audit says "confirm each claimed bubble is visible with an empty composer", which already implies the right bubble; matching the message text makes the check explicit). The re-audit should also note the run 5 Chromium case, where R1 has scrolled off the top, so the expected visible set is R2 to R5, as the log already records.

## F8. Gating consequence (a): EXPAND approval should wait. STANDS.

- Commit 4305dcb records "EXPAND approved in principle" on the strength of this PASS. Verified: the commit message reads "docs: COORD-CLICK-5 log, S2-REOPEN verified 5/5 median 28.6s, EXPAND approved in principle, clone1 batch 12 queued", and improvements/worker-click5-coord-log.md line 1054 reads "C5-S2-REOPEN verified: class completes 5/5, median 28.6s; EXPAND approved in principle, sequenced after landing; clone1 batch 12 queued (13:14-13:22 +07)".
- The audit says EXPAND should wait until the 10 PNGs are committed and the claim is re-audited. That is consistent with the recorded posture: the approval is "in principle" and "sequenced after landing", not an executed expansion. Waiting for the render evidence before the expansion proceeds is the correct reading, and the audit does not overclaim beyond it.

## F9. Gating consequence (b): landing waits, or records the gap as open. STANDS, and live.

- The audit says the (b1) landing should wait for the 5 PNGs plus re-audit, or land with the missing P9 evidence recorded as an open item against it.
- Checked against the landing spec as committed (55405a5, 491 lines): section 7 asserts "P9 PASS 10 of 10 in the reopen" as an established fact, and section 10 ("What is still missing before it can land") lists 8 items, including the missing /tmp helpers, but does not list the missing P9 PNGs for the reopen or (b1) measurements.
- So the "land with the gap recorded as open" branch is currently NOT satisfied by the spec. The "wait" branch is the operative one. The audit's consequence is not hypothetical; the spec leans on a P9 PASS whose evidence is not in the repo.
- The spec's own section 9 step 7 is consistent with the audit: "The reopen EXPAND recommendation stands only if the 5 re-runs match the reopen numbers." The spec already conditions the recommendation on re-runs. The audit adds the prior condition, that the reopen numbers themselves must first be fully evidenced.

## F10. Relaxed routing is a qualification, not a gap. STANDS.

- The Chromium half ran under the disclosed relaxed routing gate in all 5 reopen runs: truncated 80-element inventory, composer covered, routing_relaxed True per run, reason recorded in each JSON ("relaxed gate: truncated inventory (80 elements), send target covered").
- The (b1) run 1 passed under the strict gate, and the send mechanism is identical across runs; the relaxation touches only the routing gate, not the send path. The audit is right to treat this as a disclosed qualification on the PASS, not hidden evidence and not a reason to revoke.

## F11. (b1) aborts are disclosed, not hidden. STANDS.

- Runs 2 to 5 each had a first attempt with outcome aborted-routing, error "router fell through to screenshot: fail-closed fallback: no backend returned complete coverage". Verified in run-2-aborted.json (same shape for runs 3 to 5, all preserved).
- The input-fix log discloses the aborts in the time log, in section 7.5, and in the commit record, and states nothing was sent in the aborted attempts. The 5/5 figure counts the 5 scored runs, and the aborts are on the record. The audit is right that this is not a gap.

## F12. Focus-enter helper named as secondary gap only. STANDS.

- /tmp/c5-focusenter.mjs is not in the repo. Verified: no focusenter file in the todolist-push tree, only references in scripts/s2_flip_live.py (LAPTOP_FOCUSENTER at line 76, docstrings at lines 138 and 500).
- The audit correctly treats this as secondary, not the reason for the verdict: the helper's behavior is recorded per run in the JSONs (focus_enter ok True, enter ms) and its contract is documented in the harness docstrings (Runtime.evaluate focus plus Input.dispatchKeyEvent Enter, zero mouse events). The mechanism description is confirmed from the docstrings, and the input-fix log section 7.1 confirms Input.dispatchKeyEvent answers in 2 ms on the stuck tab while Input.dispatchMouseEvent stalls.
- The outcome evidence is complete; the code itself is not reviewable from the branch, and that stays an open item for the landing work, as the audit says.

## F13. Method note and task 1 reconciliation. STANDS.

- The audit states the batch 12 task 1 verification report was not on main when it ran, and that no numbers were reused from it. That was true when the audit ran, and the task 1 report is still not on main: it exists as an uncommitted 428-line file in the working tree.
- Reconciliation, now possible: task 1 independently confirms every number the audit recomputed (walls, sorted list, median 28560.9 ms, per-send 10/10, per-run 5/5, phase split medians) and independently confirms the P9 gap (section 9 item A, "P9 screenshots are MISSING from the branch. Material gap.", found by GitHub API). Task 1 CONFIRMED the numeric claims and listed the gap; it did not apply CB-8, which was task 3's job. There is no conflict between the two reports.
- Task 1 also records two minor open notes the audit does not mention: V12 textLen is systematically +4 over the message length, and the residual range wording cites run 1 values. Neither touches any verdict in the audit, and neither is in the audit's scope. Noted here for the record, not a change to the audit.
- The audit's statement that the 12/12 wiring tests claim was not re-verified is honest scoping, not a gap in the audit's own verdicts, which rest on the committed artifacts, as CB-8 asks.

## Notes for the fix pass

- None of the findings above requires a change to the audit report. The two amplifications a fix pass could add, without changing any verdict, are: (1) state explicitly in F4 terms that "unscored" in the final-direction log means P9 contributes no points to the score, while the hard condition still makes its review a precondition for PASS, so future readers do not re-raise the apparent tension; (2) record that the task 2 spec section 10 does not list the missing PNGs, so the "wait" branch of the (b1) gating consequence is the operative one until the spec is amended or the PNGs land.
