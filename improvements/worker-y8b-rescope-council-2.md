# E1 RE-SCOPE decision: Council Member 2 verdict

Council Member 2, independent of Council Members 1 and 3. Paper only. No Zen driving, no executor launches, no live browser use. All times Asia/Ho_Chi_Minh, 2026-11-21.

## Timing log

- 19:54:57: task start. Read the judge ruling, the reconciliation, the frozen v2.1 design.
- 19:55-19:56: verified the v2.2 fix in the working tree with my own checks (see section 2), and read the laptop proof log read-only via ssh-laptop.sh.
- 19:56-20:05: verdict written.

## 1. What is binding, and what is not re-debated

The independent judge ruling (improvements/worker-y8b-judge-void.md, commit 7275171) is BINDING. I do not re-litigate VOID vs FAIL. The facts I take from it:

- A1: FAIL (incomplete). A2: FAIL (incomplete). Both count. Zero task steps ran in either.
- Arm A budget exhausted (2 of 2 starts). No A3 under v2.1. Second crash of any kind ends the arm as BLOCKED. Arm A stands BLOCKED.
- No-clean-win clause TRIGGERED (A2 was an infra retry). This holds independently of the VOID/FAIL call.
- Executors exonerated. The failure is a deterministic defect in the frozen instrument (the shell-quoting trap), proven by the judge independently.
- The v2.1 comparison is OVER. Arm A BLOCKED, B never ran. No comparative verdict can be drawn from A.
- A future A attempt would need a versioned re-freeze (v2.2 or later) and a fresh budget decision by the coordinator and council. The ruling does not authorize one.
- Replication trigger engaged ("either arm flagged or invalid").

The reconciliation file (improvements/worker-y8b-reconciliation.md, commit 3cfea4d) I read for context only, not as authority. Its Q3 void position, its "max 2 VALID starts" budget, its replication rename to (B2, A4), and its no-clean-win scope were all conditional on a judge ruling VOID. The judge ruled FAIL. Those terms are therefore dead with the void, not live premises for this decision. Any option below that quietly reuses them is the void by another name, and I treat it as such.

Design text I rely on (frozen v2.1, commit 695efea):

- "Max 2 starts per arm. A second start, if any, is labelled A2 or B2 in every table and every verdict sentence. It never silently replaces A1 or B1."
- "Second crash of any kind ends the arm as BLOCKED."
- "If either arm needed an infra retry or any recovery-ladder intervention, no clean win or loss is claimed on either criterion."
- "Never compare one measured arm against nothing." (pre-start INFRA-BLOCKED rule; the judge, section 5, reads it as barring any comparative verdict from a lone B run.)
- "Any change after this freeze requires a new version number and a re-freeze note, never a silent edit."
- Replication trigger: "A second pair (B2, A2, swapped order) is run before any comparative verdict beyond pilot language if ANY of these holds: ... either arm is flagged or invalid; ..." and "The second pair runs only in a fresh handover window, not by extending a window that has already closed."

## 2. The v2.2 fix: verified by my own checks, not taken on trust

I verified the working-tree fix independently on the VM, and the live proof read-only on the laptop. This verification covers the instrument only. It authorizes nothing about budgets or comparisons.

- Plan md5 63415e9b6cd63dc2185ca23242180424, matches the task brief. My own extraction of the backticked JSON commands: 64 parsed with json.loads, 0 failures; 26 JS-bearing; 19 evals, 7 click_js; 0 single quotes inside any decoded js value; node new Function parses all 26 js values, 0 failures.
- Brief A md5 b34bbfa0e419dcd8cec10e06a4575d16, brief B md5 054527b88eea3d6a6b18d19787b8177d, driver reference md5 dde7ad584d22ac28d0573404e5d5cabb, preflight.py md5 5bfaebccace04e1c7e75c5cc5a837d22, A3 brief md5 813bcebae435ddfc5b0b1c23de1c3807. All match the task brief.
- Grep: zero occurrences of querySelector(' in briefs A, A3, B, the driver reference, and the plan.
- STOPPED (DRIVER SUSPECT) wording present in the A and A3 briefs; the executor no longer labels DRIVER DEAD itself.
- Laptop /tmp/e1/v22-proof.log (read-only): full diagnose VISIBLE with countText 6; step 4 count 6; step 31 click_js ok plus step 32 starActive true; italic eval returned ok with nulls (not a 500); step 56 eval returned the verifier JSON (failures expected on a sacrificial tab where the task was not performed). /tmp/e1/plan-test-05.md md5 matches the repo file. Fresh pre-flight A3 exists (/tmp/e1/preflight-a3.json, 19:53:15, VISIBLE, countText 6).

Conclusion: the quoting trap is closed in the instrument as written. The fix is real, and it is the same fix for both arms. What the fix does NOT do: it does not un-FAIL A1/A2, it does not un-trigger no-clean-win, it does not create an A budget, and it does not repair the v2.1 comparison. A fixed instrument and a live comparison are different things, and only the first is proven here.

## 3. Per-option verdicts

### (a) B runs alone under v2.2 as a single-arm observation, no comparison claimed

Verdict: AMEND (conditional GO, on the terms in section 4).

For: the deliberated plan has never been executed live. The deliberation phase cost 642 s sunk plus about 463k input tokens, and its product is a 58-step plan whose 64 commands are now proven to parse and whose sampled steps are proven to run, but whose full run is untested. A B1 run answers a real, narrow question: does the deliberated-plan bundle execute end to end on test-05, and with what burden and plan defects? That is a prerequisite finding for any future use of the plan, and it is the natural completion of the Q4 live proof already spent. Cost is one live slot and one executor run (spec puts this task at 150 s expected, 260 s maximum), which is small against the sunk deliberation cost and against leaving the plan wholly untested. The judge does not forbid B running; it forbids a comparative verdict from a lone B run ("should B run" is contemplated, and the bar is on the verdict, not the run). The fix is proven, so B1 would test the fixed instrument, not re-run the trap.

Against: a lone B datum invites misuse. Future readers will be tempted to compare B1 against the spec's 150-260 s expectation, or against A1/A2's burden (1 error incident each, from the instrument, with zero task steps), or to headline a B result. None of those comparisons is valid, and the fencing in section 4 must carry that weight in every table and every verdict sentence. B1's wall time without an A comparator cannot answer the E1 question, and cannot even support the break-even calculation, which needs A execution time that does not exist. B1 also goes stale: if a fresh A ever runs later, pairing it with B1 means pairing across windows, which the design requires to be disclosed and which weakens the pairing.

Balance: the misuse hazard is real but fenceable in writing, and the judge's own bar already supplies the fence. The plan-executability finding is real and cheap. The hazard does not outweigh the finding, provided the terms in section 4 are binding, not advisory. If any term cannot be met, this option becomes BLOCK, not GO with the term dropped.

### (b) A fresh comparison under v2.2 with a NEW A budget

Verdict: BLOCK.

Reasons, in order of weight:

1. It is the void by another name. The reconciliation's void terms (A3 as first valid start, 2 valid starts, old attempts kept in the record) granted exactly what (b) grants: a fresh A budget after the fix. The judge denied the void under the frozen text, in a ruling created precisely because the coordinator cannot void its own failures alone. Re-granting the same budget by council vote, with FAIL labels retained as a fig leaf, does not change the substance: the FAILs would no longer constrain anything, and the arm the judge declared BLOCKED would be un-blocked by the same body that ran the experiment. That is the self-dealing hazard the judge was created to remove, repeated one round later.

2. The labels are incoherent. Under the frozen text, "Max 2 starts per arm" and "Second crash of any kind ends the arm as BLOCKED" have already fired for A. A fresh budget means arm A would hold 4 starts in total (A1, A2 FAIL under v2.1, plus A3, A4 under v2.2) while B holds 2. To make that coherent the council would have to rewrite the cap after the outcome is known, which is a design rewrite after the fact, not a fresh decision under the design.

3. The comparison it would buy cannot answer the question. No-clean-win is already TRIGGERED, permanently, for E1. A fresh comparison could at best report "an observed difference, confounded by browser health" on either criterion, never a win or a loss. The headline purpose of E1 (does deliberation win on speed or accuracy) is already unachievable in this experiment. Spending two live slots plus Y9 delay for a comparison whose best possible verdict is a confounded observed difference is a bad trade, and it would still carry the full disclosure burden (two FAILs, a mid-experiment instrument fix, a plan edit, elapsed time, an infra restart).

4. Precedent. If an arm that fails twice on an instrument defect gets a fresh budget after a fix, the start budget and the BLOCKED rule stop binding. Every future arm failure becomes re-arguable on the same ground. The judge's ruling exists to stop exactly that slide.

What (b) is NOT: I do not block a genuinely NEW experiment in principle. A future proposal with new labels (not A3/A4 continuing E1), a new design version, its own council, its own budget, and a stated decision value that survives no-clean-win (that is, explicitly seeking only an observed difference, never a win) could be considered on its own merits, later, not in this verdict. What I block is authorizing a fresh A budget NOW as a continuation of E1. The distinction matters: continuation inherits E1's triggered clauses; a new experiment does not inherit them, but it also does not inherit E1's deliberation data without its own justification. No such proposal is before this council, so nothing is authorized here.

### (c) Abort the experiment entirely: report A BLOCKED plus the instrument defect; B never runs

Verdict: GO (valid fallback, not recommended).

For: cleanest respect for the binding ruling. The v2.1 comparison is over; the experiment's unit is the pair, not the arm; the design authorized a comparison, not a standalone B observation. Aborting avoids the misuse hazard of (a) entirely, frees the live slot for Y9 at once, and still leaves a substantive finding: the instrument defect is proven, the pre-flight gap is identified (pre-flight uses subprocess argv with no shell, so it structurally cannot exhibit the shell-path trap), the DRIVER DEAD labelling is fixed, and the v2.2 fix is proven live on a sacrificial tab. That is a real methodological result, not an empty abort.

Against: it wastes the plan validation. The deliberation product (58-step plan, 642 s sunk) is left wholly unexecuted, and the question "does the deliberated plan even run?" stays unanswered when one executor run could answer it. The abort also discards the live-proof investment already made (the Q4 probes proved sampled steps, not the full run).

Balance: (c) is lawful and clean, and I would take it over (b) without hesitation. I rank it below (a) only because the cost of B1 is one slot and the finding it buys (plan executability, burden, defects) is the one piece of E1 data that is still obtainable without violating any binding rule.

## 4. Recommended option: (a), with exact binding terms

Run B1 alone under v2.2 as a single-arm observation. No comparison is claimed, now or later, from E1 data. Terms are binding; breach of any term voids the GO and the run must stop and return to council.

1. Re-freeze first. A v2.2 re-freeze note is written and committed BEFORE any executor runs, carrying: the root cause in one paragraph; the exact fix with corrected counts (64 commands, 19 evals, 7 click_js, 26 JS-bearing, 0 single quotes in js); the new frozen md5s (plan 63415e9b6cd63dc2185ca23242180424, brief A b34bbfa0e419dcd8cec10e06a4575d16, brief B 054527b88eea3d6a6b18d19787b8177d, driver reference dde7ad584d22ac28d0573404e5d5cabb, preflight.py 5bfaebccace04e1c7e75c5cc5a837d22, step.sh unchanged); the re-scope decision in one paragraph (A BLOCKED under v2.1, B1 single-arm observation under v2.2, no comparison claimed); and the pre-launch proof outputs by filename (v22-proof.log, preflight-a3.json). No executor runs before that commit. The A3 brief (813bcebae435ddfc5b0b1c23de1c3807) is NOT used and stays unlaunched; its existence does not imply an A budget.
2. Labels. The B run is labelled B1, the first B start under v2.2. A1 and A2 stay labelled FAIL (incomplete) under v2.1, in every table and every verdict sentence. No label is reused, and no B1 result is ever relabelled as part of a pair.
3. B budget. B keeps the frozen budget rules intact: max 2 starts. If B1 stops post-start without reaching final verification, B1 IS B's result (FAIL incomplete), and a second observation B2, if the coordinator judges it worth doing, is reported alongside B1, never as a replacement. A second crash of any kind ends B as BLOCKED. No void logic is imported into B. If B1 hits the quoting trap again, that is reported as a v2.2 instrument failure, not voided.
4. Pre-flight and hygiene. Fresh pre-flight B before launch (saved to /tmp/e1/preflight-b.json), md5 re-verification of all frozen inputs before B starts, infra restart between the proof phase and B1, out.log archived as out-b.log before any later infra start, B1 report run-b-report.md, event stream events-b.jsonl audited for single-quote bytes inside js values.
5. Verdict language, fenced. The B1 report and any verdict sentence may say only: "B1 observed: PASS/FAIL, wall X, burden Y, plan defects Z, on test-05, this run, single arm only." PASS/FAIL is read from out.log by the independent judge from the fixed final-read list, never from an executor claim. Forbidden in every table and verdict sentence: any total-speed claim (the 642 s sunk cost is recorded separately and never added to a total-speed verdict, because there is no A total to compare against); any execution-only speed win; any accuracy win, loss, or draw; any comparison of B1 wall time against the spec's 150-260 s expectation; any comparison of B1 burden against A1/A2 burden; any headline containing "deliberation wins" or "deliberation loses"; any "pilot verdict" language. The report states in its first paragraph that B1 is not comparable to A1/A2 (different instrument versions, A never ran a task step) and that no comparative verdict can ever be drawn from E1 data.
6. No-clean-win stays TRIGGERED. It is recorded as triggered for E1, and it is irrelevant to a single-arm observation, which claims no win at all. It is not cleared, not re-evaluated, and not used to upgrade B1 into a clean result.
7. Y9 release (see section 6). B1 completing does not satisfy the original two-arm marker; the closure marker in section 6 releases Y9 instead.

## 5. The replication trigger: what it forces

The judge states the replication trigger is engaged ("either arm flagged or invalid"). Under the design, the trigger's consequence is: a second pair (B2, A2, swapped order) is run BEFORE any comparative verdict beyond pilot language. It does NOT force a second pair to be run regardless, and it does NOT force B to run or not run. Its operative consequence here is a bar, not a mandate:

- No comparative verdict beyond pilot language may ever be claimed from E1 data, because the trigger is engaged and the second pair that could discharge it cannot be constituted (A is BLOCKED, no A2 label exists under v2.1, and this verdict BLOCKs a fresh A budget).
- The trigger is therefore recorded as ENGAGED and UNSATISFIED, permanently, for E1. That status is itself the reason no comparative verdict is claimable, and it stays in the record even after B1 runs: B1 is a single-arm observation, not a pair, so it neither satisfies nor re-evaluates the trigger.
- The reconciliation's position (trigger evaluated on a valid pair A3/B1) is dead with the void. It is not adopted here. The redteam position (trigger stays tripped) is adopted as to the fact: it stays tripped, and the consequence is the permanent bar above, not a mandate to manufacture a pair.

## 6. The Y9 slot marker: what releases Y9 instead

The original marker (execution log line 39: a commit matching ^Y8 E1:.*execution complete plus an "E1 EXECUTION COMPLETE" log line naming both arms' results) cannot be satisfied as written: arm A has no valid result, only two FAILs, and under option (c) B would have no result at all. Y9 must not wait for a marker that can never arrive, and the coordinator must not fake it by writing a two-arm completion line.

Replacement marker, exact. The coordinator writes a closure commit and a closure log line, and Y9 treats EITHER the original marker OR the closure marker as release:

- If (a) runs: commit message "Y8 E1: execution complete (A BLOCKED under v2.1, B1 single-arm observation under v2.2, no comparison claimed)". Log line in improvements/worker-y8-e1-execution-log.md: "E1 EXECUTION COMPLETE: arm A BLOCKED (A1 FAIL incomplete, A2 FAIL incomplete), arm B B1 <PASS/FAIL, wall, burden>, no comparative verdict, replication trigger ENGAGED and UNSATISFIED."
- If (c) were taken instead: commit message "Y8 E1: execution closed, experiment aborted (A BLOCKED, B never ran)". Log line: "E1 EXECUTION CLOSED: aborted, arm A BLOCKED (A1 FAIL incomplete, A2 FAIL incomplete), arm B never ran, finding instrument defect (shell-quoting trap), no comparative verdict."
- Y9's poll is updated to accept the closure marker as release. The slot is free the moment the closure commit lands on origin/todolist-push, verified by git ls-remote. Y9 must not wait for the original two-arm line.

## 7. What would change my mind

- On (a) to (c): if the live slot cost is higher than stated (Y9 time-critical, or the handover window closing before B1 can finish with its review), or if the v2.2 re-freeze note cannot be committed cleanly, or if fresh pre-flight B fails, I switch to (c). A failed pre-flight B is a stop, not a fix-forward.
- On (a) to BLOCK: if B1 returns HTTP 500s on the fixed commands, the v2.2 fix is falsified live and B1 stops; the finding becomes "v2.2 fix incomplete", and no further B start is authorized by this verdict.
- On (b) to GO: nothing in this record changes it. Only a separate, future proposal for a genuinely new experiment (new labels, new design version, own council, own budget, explicitly seeking only an observed difference) could reopen the question, and it would need its own authorization, not this verdict. The judge's denial of the void plus the already-triggered no-clean-win clause together close (b) as a continuation of E1.
- On the fix itself: my verification is static plus sampled live proof. If the B1 event audit finds single-quote bytes inside any js value, or if B1's diagnose step 500s, the fix claim is falsified and the B1 result is reported as an instrument failure under term 3, not as a B executor failure.

## 8. Anticipated attacks, answered

- "B1 alone is half a comparison and will be misread as one." Answered by term 5: the fencing is in the report's first paragraph and in every verdict sentence, and the judge's own bar ("never compare one measured arm against nothing") is cited there. A reader who misreads past that fencing is misreading, not following the report. The alternative, (c), avoids the hazard by discarding the finding; I judge the finding worth the fencing.
- "The v2.2 fix was proven on a sacrificial tab, so B1 adds nothing." The probes proved sampled commands (diagnose, step 4, steps 31/32, step 55, step 56). They did not prove the full 58-step run, the modal flows, the save flow, or the final verification sequence. B1 proves the run, not the samples.
- "One live slot for a datum with no comparator is waste." The datum is plan executability, burden, and defects, which is the deliverable the 642 s deliberation bought. The slot cost is one executor run against a sunk deliberation cost an order of magnitude larger in time and tokens.
- "Authorizing B1 now prejudges the future new-experiment question." It does not. B1 is labelled a single-arm observation under v2.2, never part of a pair. A future new experiment would need its own council to decide whether B1 can serve as its B observation (across windows, with disclosure) or whether B must re-run. This verdict decides neither.

## 9. Verdict summary

- (a) B alone under v2.2, no comparison: AMEND (conditional GO on the seven binding terms in section 4).
- (b) Fresh comparison under v2.2 with a new A budget: BLOCK. It is the void by another name, its labels are incoherent, its best verdict is a confounded observed difference, and it destroys the budget precedent.
- (c) Abort entirely: GO as a valid fallback, not recommended. Clean, lawful, but discards the one obtainable finding.
- Recommended: (a) on the terms in section 4. Replication trigger ENGAGED and UNSATISFIED permanently for E1. Y9 is released by the closure marker in section 6, not by the original two-arm marker.
