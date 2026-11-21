# Council Member 1 verdict: E1 RE-SCOPE (Worker Y8b)

Council Member 1, independent. Paper only. No Zen driving, no executor launches, no live browser use. I did not read the Council 2 or Council 3 re-scope verdicts or any redteam re-scope file. This verdict is my own.

The independent judge's ruling is BINDING and I do not re-debate it. I accept: A1 FAIL (incomplete), A2 FAIL (incomplete), arm A BLOCKED, budget exhausted, no A3 under v2.1, no-clean-win clause TRIGGERED, executors exonerated, the failure a deterministic defect in the frozen instrument. The v2.1 comparison is OVER. The question before this council is only what happens next.

## 1. Timing log (Asia/Ho_Chi_Minh, wall clock)

- 19:54:36: task received.
- 19:54:55: work start. Elapsed 0:00:19.
- 19:55-19:57: read the judge ruling (improvements/worker-y8b-judge-void.md, commit 7275171) and the reconciliation (improvements/worker-y8b-reconciliation.md, commit 3cfea4d, context only, not authority) in full.
- 19:57-19:58: read the frozen v2.1 design (git show 695efea) and the Y9 slot marker text (worker-y9-agy-y2-live-plan.md section 5, via grep); read the execution log tail.
- 19:58: independently verified the v2.2 fix on the working tree and the laptop proof log (read-only ssh-laptop.sh cat). See section 2.
- 19:58-19:59: verdict written. Elapsed at write about 0:04.

## 2. What I verified myself (not taken on trust)

The v2.2 fix is done and proven. I checked it independently rather than trusting the task brief or the log.

- Plan (improvements/worker-x-e1-plan-test-05.md, working tree): 64 driver commands parse with json.loads, 64/64, 0 parse failures. 19 evals, 7 click_js, 6 click, 7 type. Zero single quotes in ANY field of any command. All 64 decoded js values parse with node (0 failures). Prose outside the JSON is byte-identical to v2.1 (JSON-masked prose diff 0). 79 JS string literals. New md5 63415e9b6cd63dc2185ca23242180424 matches the brief.
- The 24 commands whose decoded js changed are exactly the quote-style changes (single to double quotes). The 2 remaining text differences after quote normalization are steps 21 and 55, the italic selectors, in the adopted JS-escaped form (.meta-line[style*=\"italic\"]). The string VALUE is identical to v2.1; the live proof below confirms the selector parses and runs (ok, not 500).
- Briefs A (b34bbfa0e419dcd8cec10e06a4575d16), A3 (813bcebae435ddfc5b0b1c23de1c3807), B (054527b88eea3d6a6b18d19787b8177d), driver reference (dde7ad584d22ac28d0573404e5d5cabb), preflight.py (5bfaebccace04e1c7e75c5cc5a837d22): md5s match the brief. Backticked JSON objects in these files: A 6, A3 6, B 2, reference 1, all parse, 0 single quotes in any js value. The quoting rule and STOPPED (DRIVER SUSPECT) wording are present in each brief and in the reference.
- Laptop proof log (/tmp/e1/v22-proof.log, read 19:58): all 6 shell-path probes PASSED on a sacrificial tab. Full diagnose VISIBLE with countText "6" in 3 ms; step 4 count 6; step 31 click_js ok and step 32 starActive true with cardFavorite true; italic eval ok with nulls (Frank not yet present, which proves the JS parses and runs rather than 500ing); step 56 eval ok returning verifier JSON. Fresh pre-flight A3 (/tmp/e1/preflight-a3.json, 19:53:15): VISIBLE, exit 0, countText "6".
- Conclusion: the v2.2 instrument is proven through the executor's shell path, which is exactly the path v2.1 never validated. The fix is real. That does not change the judge's ruling, and it must not be used to change it. It changes only what a NEXT run may use.

## 3. Design sentences relied on (frozen v2.1, commit 695efea)

- Line 13: "Any change after this freeze requires a new version number and a re-freeze note, never a silent edit."
- Line 99: "Max 2 starts per arm. A second start, if any, is labelled A2 or B2 in every table and every verdict sentence. It never silently replaces A1 or B1."
- Line 100: "Never compare one measured arm against nothing." (Pre-start INFRA-BLOCKED paragraph; the sentence is the bar on any lone-arm comparative verdict.)
- Line 101: "Post-start INVALID (crash, DRIVER DEAD, mid-run hidden body, or any stop after the executor's first driver command): the first started run IS the arm's result for accuracy. If the executor never reaches final verification, the arm is recorded as FAIL (incomplete), with the partial step reached, the failed checks so far, and the crash or timeout evidence."
- Line 106: "Second crash of any kind ends the arm as BLOCKED."
- Line 109: "If either arm needed an infra retry or any recovery-ladder intervention, no clean win or loss is claimed on either criterion. The result is reported as an observed difference, confounded by browser health, with the pre-flight evidence attached."
- Lines 137-139 (replication trigger): "A second pair (B2, A2, swapped order) is run before any comparative verdict beyond pilot language if ANY of these holds: the arms split PASS/FAIL; total times differ by less than 2 min on the primary clock; accuracy burden difference is 1 or less; either arm is flagged or invalid; the coordinator's independent error count disagrees with either executor report by more than 2; execution wall times differ by less than 20 percent."
- Judge ruling, section 5: "Any future A attempt would need a versioned re-freeze (v2.2 or later) under sentence (j) and a fresh budget decision by the coordinator and council; this ruling does not authorize one." And: "The replication trigger ('either arm is flagged or invalid') is engaged, since A1 and A2 fall under the design's 'Post-start INVALID' heading."

Two facts follow from the design text that decide this verdict. First, a total-speed verdict needs an A total, and A has no total: A never ran a task step, so there is no A execution wall to put on either side of the headline formula. Second, an accuracy verdict needs two arms, and A is FAIL (incomplete) at zero steps: the design's own rule for both fail ("no accuracy win is awarded to either arm") plus "never compare one measured arm against nothing" bars any comparative verdict from a lone B run. Those bars are not inconveniences. They are the design working as written.

## 4. Per-option verdicts

### (a) B runs alone under v2.2 as a single-arm observation, no comparison claimed

Verdict: AMEND (conditional GO). The option is sound in substance and wrong if run as loosely described. It is worth one live slot, and only one, under the terms in section 5.

For: the v2.2 instrument is proven at the sampled-probe level but has never been validated end to end on a full 58-step, 64-command run. Only a full B run tests the plan bundle as a whole: whether the merged plan executes, what its burden is, and whether it carries non-quoting PLAN DEFECTs (a wrong expected value, a stale selector) that the sampled probes cannot see. That is genuine new information, and it is the only end-to-end test of the deliberation product available. The cost is one executor run plus infra restart and pre-flight, roughly one live slot, and it releases Y9 promptly. It does not foreclose option (b) later; a future comparison re-runs BOTH arms fresh, so tonight's B observation is not spent against a future A.

Against: a lone B datum cannot answer the experiment's question, and it invites exactly the misreading the design forbids. Readers will compare B's wall to the spec's 150 s expected and 260 s max, or to A1's 151 s coordinator wall (which was waiting time with zero task steps, not an A time), and claim a win. The fencing in section 5 is therefore load-bearing, not decoration. If the coordinator cannot hold it, this option collapses to BLOCK.

The amendments required: v2.2 re-freeze committed before any launch; one B start only, labelled B1-v2.2, never bare B1; frozen single-arm verdict language; the enumerated forbidden comparisons; no pairing of this B run with any future A run; immediate stop and return to council on any HTTP 500 or parse failure.

### (b) A fresh comparison under v2.2 with a NEW A budget

Verdict: AMEND (terms specified below, NOT authorized tonight; deferred to a fresh window and a fresh proposal).

For: the judge's own text contemplates this path ("a fresh budget decision by the coordinator and council"). The instrument defect is fixed and proven, so a fresh A would measure the arm, not the trap. The core question (does the deliberation bundle change speed or accuracy) is the reason the deliberation cost was sunk, and only a comparison can answer it, even in capped form.

Against, and why I do not authorize it tonight: first, the ceiling. The no-clean-win clause is already triggered for this lineage, so a fresh comparison can never claim a clean win or loss on either criterion. Its verdict language is capped at "observed difference, confounded by browser health", pilot language only. That is decision-relevant but it is not the verdict the experiment was built to produce. Second, the replication trigger is engaged and the history is flagged, so a fresh comparison is not a 2-run decision. A second pair is effectively mandatory before any comparative verdict beyond pilot language, and the design requires that pair to run in a fresh handover window, not by extending this one. Option (b) is therefore a 4-run, 2-window program, not a 2-run comparison. Third, sequencing: running the comparison before knowing whether B can even execute a full run puts the comparison before the validation that option (a) provides. If B fails on plan defects, the comparison question changes entirely (the plan, not the execution, is the weak link), and the fresh A runs would have been spent answering the wrong question. Fourth, the queue: Y9 has polled since 18:53 with a 4-hour timeout, and the live queue behind it (Y11 proof, Y6b) is waiting on this slot.

The amendments that would make (b) legitimate, if it is ever proposed: see section 6. In particular, the fresh experiment must be re-registered as a new experiment with new labels, the old FAILs must be carried in every table and every verdict sentence, the capped ceiling must be conceded upfront, and the replication pair must be committed as mandatory. Without all of that, (b) is the void by another name, and I would BLOCK it. With all of that, it is legitimate in principle but still not worth authorizing tonight for the sequencing and queue reasons above.

### (c) Abort the experiment entirely

Verdict: BLOCK.

For: it costs no further live slot and it releases Y9 immediately. The instrument-defect finding is already preserved in the record (judge 7275171 plus the reconciliation), so aborting loses no finding.

Against: it forfeits the only end-to-end test of the plan bundle and of the proven v2.2 instrument, for the price of one slot. The fix work is already done (the log records it was needed regardless of the void ruling); refusing to run anything on the proven instrument discards the value of that work and leaves the deliberation product (642 s sunk, about 463k tokens) with zero execution data. Aborting is the correct fallback only if option (a)'s fencing cannot be held or the live slot is unavailable. Neither is true now. BLOCK (c) as the recommendation, and keep it as the fallback.

## 5. Recommended option: (a), with exact terms

B runs alone under v2.2 as a single-arm observation, on these terms. Each term is a condition of the GO, not a suggestion.

1. Re-freeze first. A v2.2 re-freeze note is committed BEFORE any B launch. It records: the v2.1 comparison is CLOSED (arm A BLOCKED, A1/A2 FAIL incomplete, judge 7275171, no comparative verdict, replication trigger engaged and undischarged for v2.1); the v2.2 files are frozen for a SINGLE-ARM B OBSERVATION ONLY, not a comparison; the new md5s (plan 63415e9b6cd63dc2185ca23242180424, brief B 054527b88eea3d6a6b18d19787b8177d, driver reference dde7ad584d22ac28d0573404e5d5cabb, preflight 5bfaebccace04e1c7e75c5cc5a837d22); the Q4 gates passed, by filename (/tmp/e1/v22-proof.log, /tmp/e1/preflight-a3.json, the consolidated sweep); and the no-comparison fence below. The A3 brief (813bcebae435ddfc5b0b1c23de1c3807) is recorded as created and NOT used. No executor runs before that commit.
2. One B start only, labelled B1-v2.2 in every table and every verdict sentence, never bare B1 (the v2.1 B1 never ran, and the label must not be confused with it). Pre-start INFRA-BLOCKED: one pre-flight retry after at least 10 minutes per the design's pre-start rule, then stop. Post-start crash: recorded as FAIL (incomplete), the observation ends, and there is NO B2 under this authorization. Any B2 needs a new council decision. Infra is restarted before B, out.log is archived per arm, and the v2.2 md5s are re-verified before launch.
3. Verdict language is frozen to single-arm observation. The B report records: PASS/FAIL from the fixed final-read list read from out.log (never from the executor's claim), accuracy burden (check failures plus error incidents plus misclicks, with step numbers), plan deviations and PLAN DEFECTs by plan step number, execution wall on the primary clock, driver-command count, tool calls, tokens in and out, and pre-flight evidence. The FIRST lines of the B report state: single-arm observation under v2.2, no comparison, no deliberation win or loss claimed.
4. Forbidden comparisons, enumerated. No comparison of B's wall to A1/A2 walls (the 151 s coordinator wall with zero task steps is not an A time). No comparison of B's wall to the spec's 150 s expected or 260 s max as a win claim (those numbers may appear as context only, with the caveat that they are not a measured arm). No total-speed arithmetic (642 s sunk plus B execution, versus nothing). No accuracy comparison. No headline saying "deliberation wins" or "deliberation loses" in any form. No pairing of this B run with any future A run: a future comparison re-runs BOTH arms fresh, under its own freeze and budget. Any sentence that violates this list is struck from the report before it is committed.
5. The replication trigger stays engaged for v2.1. This lone B run neither satisfies it nor clears it. It creates no pilot pair, and no comparative verdict may be drawn from it, now or later, by pairing it with anything.
6. Fail-closed. If any B command returns HTTP 500, or any command fails JSON or JS parsing, the executor stops immediately, the run is recorded as it stands, and the matter returns to council with the failing output. Do not fix forward live. A 500 on the fixed instrument would falsify the v2.2 proof, and that falsification is itself the finding.
7. Y9 is released by the amended marker in section 8, immediately after the B observation completes and the closure line is committed.

## 6. Terms that would make (b) legitimate (deferred, not authorized)

If a fresh comparison is ever proposed, it is legitimate ONLY on all of these terms. I state them now so the proposal, if it comes, does not have to re-litigate them.

1. New experiment, not a continuation. It is registered as E1 v2.2 (or E1b), with its own design file version v2.2 and re-freeze note. New labels v2.2-A1 and v2.2-B1, never reusing A1, A2, or B1.
2. Old FAILs carried, never erased. A1 FAIL (incomplete) and A2 FAIL (incomplete) appear in every table and every verdict sentence of the fresh experiment, with judge 7275171 cited. The fresh experiment's verdict opens with its own history: first attempt BLOCKED on an instrument defect.
3. Budget is NEW, not reset. The v2.1 budget (max 2 starts per arm) is closed, exhausted. The fresh budget (max 2 starts per fresh arm) is a new budget for a new experiment. No sentence may say the budget was reset.
4. Ceiling conceded upfront. No clean win or loss is claimed on either criterion, ever, for this lineage. Verdict language is capped at "observed difference, confounded by browser health", pilot language only. This concession is the load-bearing difference from the void: the void would have erased the FAILs and restored a clean-win ceiling; this keeps the FAILs and gives up the ceiling permanently.
5. Replication pair mandatory. Because the trigger is engaged and the history is flagged, a second pair (v2.2-B2, v2.2-A2, swapped order) is REQUIRED before any comparative verdict beyond pilot language, and it runs only in a fresh handover window. The proposal must commit to the 4-run, 2-window program upfront, not to a 2-run comparison with the replication pair left vague.
6. Fresh handover window for the fresh pair. Not by extending the current window.
7. Queue honored. Y9's 4-hour timeout is respected. If the fresh pair cannot complete before it, the fresh pair does not start tonight.

Why this is not the void by another name: the void would have (i) relabeled A1/A2 as VOID instrument artifacts, (ii) reset the budget inside the same experiment, and (iii) restored the possibility of a clean win. The terms above do none of those three things. The remaining resemblance (A runs again after failing) is the same as any re-registered replication after a failed pilot, which is normal practice, not erasure. The redteam's strongest remaining objection is the selection effect (the instrument was debugged using the failures, so undiscovered defects may remain). That objection is valid and it is disclosed, not hidden, and it is exactly why the ceiling in term 4 is capped. If the coordinator will not accept term 4, then (b) is the void by another name and I BLOCK it.

## 7. The replication trigger: what it forces

The judge holds the trigger engaged because A1 and A2 fall under the design's "Post-start INVALID" heading. What that forces is a gate on VERDICTS, not an order to RUN.

For the v2.1 comparison, it forces that no comparative verdict beyond pilot language may be drawn from the v2.1 pilot without a second pair. Since the v2.1 pilot has no valid pair (A has no valid observation), the trigger can never be discharged inside v2.1. That is acceptable, because v2.1 draws no comparative verdict at all. The trigger does not force a B-only run (that creates no pair), it does not force a fresh comparison (that is a new experiment, not a replication of the v2.1 pilot), and it does not force Y9 to wait beyond the amended marker in section 8.

For any fresh experiment under option (b), the trigger is re-evaluated on the fresh pair's runs, with the flagged history disclosed. My terms in section 6 make the second pair mandatory in that case, because a fresh pair on this task will very likely meet at least one trigger condition (burden difference of 1 or less, execution walls within 20 percent, or a flagged run), and the history is flagged from the start. The trigger is therefore not a reason to run anything tonight. It is a reason no comparative verdict may be claimed tonight.

## 8. The Y9 slot marker: what Y9 should do instead

The marker as written cannot be satisfied. The Y9 plan (worker-y9-agy-y2-live-plan.md, section 5) requires ALL of: (a) a commit on todolist-push after 4a78f7f matching regex ^Y8 E1: .*execution complete; (b) a NEW line in improvements/worker-y8-e1-execution-log.md matching "E1 EXECUTION COMPLETE" that names both arm A and arm B results; (c) Y4d's completion verified DIRECTLY. Leg (b) as written assumes two completed arms. Arm A will never complete under v2.1. So Y9 must poll for an AMENDED marker, defined here exactly.

Amended marker (for the recommended option (a)):

- Leg (a'): a commit on todolist-push matching the SAME regex ^Y8 E1: .*execution complete, for example "Y8 E1: B single-arm observation execution complete, v2.1 comparison closed". The regex is satisfied by the words "execution complete". The message must not claim both arms completed.
- Leg (b'): a NEW line in improvements/worker-y8-e1-execution-log.md matching "E1 EXECUTION COMPLETE" that names both arms' FINAL states: arm A BLOCKED (A1 FAIL incomplete, A2 FAIL incomplete, judge 7275171) and arm B single-arm observation B1-v2.2 (PASS/FAIL, execution wall, burden), plus the literal words "no comparative verdict" and "live slot released to Y9". The marker's intent is "Y8 is done with the live slot and both arms are accounted for", not "both arms completed successfully". Naming A's final state (BLOCKED) plus B's observed result satisfies that intent.
- Leg (c): Y4d's completion verified DIRECTLY, unchanged.
- Plus the existing abort-rule live checks at launch time (Y8 ports 4451 and 8767 free, no foreign geckodriver, flock) as the real safety gate. The git marker is the signal; the live checks are the proof the slot is actually free.

One step is mandatory and must happen BEFORE Y8 closes: the coordinator must amend the Y9 plan in writing (a note in the Y9 live log or plan) redefining legs (a') and (b') from "both arms completed" to "both arms accounted for, comparison closed". If Y9's polling is literal and requires two completed arms, that written amendment is the only thing that prevents Y9 from waiting out its 4-hour timeout on a marker that can never arrive. Y9 should poll for the amended marker on its normal cadence, and on its timeout it reports to the parent instead of launching, as its plan already provides.

If option (c) were chosen instead, the same amended marker applies with "ABORTED" and "arm B never ran". The Y9 plan's abort rule already anticipates this: an ABORT marker frees the slot only after the launch-time live checks pass.

If option (b) were ever authorized, the marker is satisfied only after the fresh pair completes, naming v2.2-A1 and v2.2-B1 results in pilot language, with the replication pair recorded as outstanding. Y9 then runs before the replication pair, which needs a fresh window.

## 9. What would change my mind

- Option (a) to BLOCK: a B probe returns HTTP 500 (the v2.2 proof falsified); the coordinator cannot hold the fencing in section 5, term 4; or Y9's timeout is imminent and the slot is needed now. Any one of these flips (a) to BLOCK and (c) becomes the fallback.
- Option (a) to unconditional GO: nothing. The fencing is load-bearing, not optional. There is no version of (a) I endorse without it.
- Option (b) to GO tonight: written agreement from Y9 to wait past its timeout, plus a coordinator commitment in writing to the full 4-run, 2-window program with the capped ceiling in section 6, plus re-registration as a new experiment with new labels before any run. Even then I would still sequence (a) first, because a B plan-defect failure would reframe the comparison question.
- Option (c) to GO: the plan's executability is proven another way (so the B run has no information value), or the live slot becomes unavailable. Neither holds now.
- On the fix itself: if an independent check finds a single quote inside any decoded js value in the v2.2 files, or a JSON or node parse failure, my section 2 conclusion is wrong and every option that runs an executor (a and b) must stop until the fix is re-proven. My checks found none.

## 10. Summary of verdicts

- (a) B alone, single-arm observation, no comparison: AMEND, conditional GO on the terms in section 5. RECOMMENDED.
- (b) Fresh comparison under v2.2, new A budget: AMEND, terms in section 6, NOT authorized tonight. Deferred to a fresh window and a fresh proposal, after (a) completes and Y9 runs.
- (c) Abort entirely: BLOCK as the recommendation. Kept as the fallback if (a)'s fencing cannot be held or the slot is unavailable.
- Replication trigger: engaged for v2.1, undischarged, and undischargable inside v2.1. It gates comparative verdicts; it orders no run.
- Y9 marker: amended marker in section 8 (same commit regex, closure line naming both arms' final states with "no comparative verdict" and "live slot released to Y9", Y4d direct verification unchanged, launch-time live checks as the real gate). The coordinator must amend the Y9 plan in writing before Y8 closes.

Council Member 1. Verdict written 19:58-19:59, 2026-11-21, Asia/Ho_Chi_Minh.
