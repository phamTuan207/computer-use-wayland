# Council Member 3 verdict: E1 RE-SCOPE after the binding judge ruling (Worker Y8b council)

Role: Council Member 3 for the E1 re-scope decision. Debate on paper only. No Zen driving, no executor launches, no live browser use. Independent of Council Members 1 and 2; this conclusion is my own. I did not read any other re-scope council verdict (none existed in the repo when I wrote this). I read the judge ruling, the v2.1 design, the reconciliation of the earlier round, and the working-tree v2.2 files, and I ran my own checks on the fix.

Timing: task received 2026-11-21 19:54:36 +07. Evidence gathered 19:54-19:58. Verdict written 19:57-19:58. No ydotool used. No em dash or en dash in this file.

## 1. What is settled and not re-debated

The independent judge ruling (improvements/worker-y8b-judge-void.md, commit 7275171) is BINDING. I do not re-litigate VOID vs FAIL. The settled facts I rely on:

- A1: FAIL (incomplete). A2: FAIL (incomplete). Each counts as a start; zero task steps ran in either.
- Arm A start budget under v2.1 is exhausted (2 of 2). No A3 exists under v2.1. Arm A stands BLOCKED.
- The no-clean-win clause is TRIGGERED for v2.1.
- Executors exonerated: both followed the frozen briefs exactly; the failure is a deterministic defect in the frozen instrument (the shell-quoting trap), proven by the judge independently.
- The v2.1 comparison is OVER: arm A BLOCKED, B never ran, no comparative verdict can be drawn.
- A future A attempt would need a versioned re-freeze (v2.2 or later) under design sentence (j) and a fresh budget decision by the coordinator and council. The ruling does not authorize one. This council is the body that can make that decision, or decline it.

Design sentences I rely on (improvements/worker-y8-e1-comparison-design.md, commit 695efea, md5 e1909423ee987b355783f22c7d804494, verified unmodified):

- Line 99: "Max 2 starts per arm. A second start, if any, is labelled A2 or B2 in every table and every verdict sentence. It never silently replaces A1 or B1."
- Line 100: pre-start INFRA-BLOCKED abort rule, ending "Never compare one measured arm against nothing."
- Line 101: post-start rule, "the first started run IS the arm's result for accuracy. If the executor never reaches final verification, the arm is recorded as FAIL (incomplete)..."
- Line 106: "Second crash of any kind ends the arm as BLOCKED."
- Line 109: "If either arm needed an infra retry or any recovery-ladder intervention, no clean win or loss is claimed on either criterion."
- Line 13: "Any change after this freeze requires a new version number and a re-freeze note, never a silent edit."
- Line 139: replication trigger. A second pair (B2, A2, swapped order) runs before any comparative verdict beyond pilot language if ANY of the listed conditions holds, including "either arm is flagged or invalid".
- Line 23: "Live queue after Y8: Y9 runs the agy-y2 suite live, after E1."
- Execution log line 39: Y9 polls for the Y8 completion marker (commit regex ^Y8 E1: .*execution complete + "E1 EXECUTION COMPLETE" log line + direct Y4d marker, already satisfied).

## 2. My independent verification of the v2.2 fix

I did not take the fix claims on trust. My own checks, run on the working tree and the laptop (read-only):

- md5s match the task brief exactly: plan 63415e9b6cd63dc2185ca23242180424, brief A b34bbfa0e419dcd8cec10e06a4575d16, brief A3 813bcebae435ddfc5b0b1c23de1c3807, brief B 054527b88eea3d6a6b18d19787b8177d, driver reference dde7ad584d22ac28d0573404e5d5cabb, preflight.py 5bfaebccace04e1c7e75c5cc5a837d22. Design md5 matches the frozen 695efea value.
- Command census (my script, JSON-object matching, not a loose backtick count): plan 64 cmd objects, all parse with json.loads; 26 js-bearing, 0 with a single quote inside any decoded js value, 0 node parse failures (new Function on every js value). Briefs A/A3/B and driver reference: 6 + 6 + 2 + 1 cmd objects, all parse, 0 single quotes in js, 0 node failures. Total 79 cmd objects across the five files, which is what the "79 JSON commands" figure counts. The plan file retains exactly 2 single-quote characters in its whole text, both the line 3 prose pair '<json>', which must not be converted.
- Wording verified in the files: the strong-form quoting rule (\" form, single-form prescription, symptom and recovery) is in the driver reference line 15 and the coordinator checklist is in line 24; STOPPED (DRIVER SUSPECT) wording is in briefs A, A3, and B; the A3 brief bans A1/A2 artifacts (run-a-report.md, events-a2.jsonl, and the rest).
- Live shell-path proof, read from the laptop /tmp/e1/v22-proof.log (md5 824fb5d38b0c71acfb72f90c9f35989f, 19:52): full diagnose VISIBLE with countText "6"; step 4 eval count 6 with all six card ids; step 31 click_js ok plus step 32 starActive true, cardFavorite true; step 55 italic-selector eval ok with nulls (Frank absent on a fresh tab, as expected, so null proves the JS parses and runs rather than 500ing); step 56 eval ok. All six probes passed on a sacrificial tab, session deleted afterwards.
- Fresh pre-flight A3, read from the laptop /tmp/e1/preflight-a3.json (started 19:53:15 +07): VISIBLE, countText "6".
- Laptop plan md5 matches the repo plan md5 (63415e9b...), so the deployed copy is the fixed copy.

Conclusion: the v2.2 fix is done and proven at the level the earlier council's Q4 gates demanded. The fix is a real precondition for any further arm run, and it is satisfied. What the fix does NOT prove: a full 58-step run end to end (only sampled probes), and the steps 21/55 italic selectors in a real Frank-present state (only probed as null-ok on a fresh tab). Those are residual risks a full run would retire, and they cut in favor of running a full arm rather than against it.

## 3. Per-option verdicts

### (a) B runs alone under v2.2 as a single-arm observation, no comparison claimed. AMEND

There is real value here, and I do not dismiss it: B's absolute wall time, error incidents, and burden on this task would be the only execution data E1 ever produces if A stays dead; and a full B run would retire the two residual risks in section 2 (end-to-end plan execution, italic selectors with Frank present). The design's "never compare one measured arm against nothing" is respected as long as no comparative sentence is ever written from it.

But (a) is dominated by (b) on value per live slot. The live slot is the scarce resource, Y9 is queued behind it, and a lone B run spends a slot for a datum that cannot answer the question the experiment was built to answer. It also creates a permanent policing burden: a measured B with a BLOCKED A invites exactly the comparison the design forbids, and every later reader must be warned off it. And the instrument-validation value of a full B run is real but partial: it validates B's plan path, not A's direct path, and the six-probe proof already validates the quoting fix itself.

AMEND terms, if (b) is rejected and (a) is chosen instead: label the run explicitly as an instrument-validation observation, never as an E1 arm result; report B's numbers as absolute values only, with the sentence "no comparison is drawn, arm A has no valid observation" in every table; run it under the v2.2 re-freeze (term 1 of section 4 applies in full); release Y9 by the closure marker in section 6, not by the completion marker. Under these terms (a) is acceptable. Without them it is BLOCK.

### (b) A fresh comparison under v2.2 with a NEW A budget. GO, with the terms in section 4

This is my recommendation. The comparison is the experiment's central question, the instrument that killed it is now fixed and proven on the shell path, and the judge's ruling itself names the legitimate route: a versioned re-freeze plus a fresh budget decision by the coordinator and council. The re-freeze is done; this council is that decision.

The attack this option must survive is the redteam's and the judge's: that a fresh budget is the void by another name, letting the coordinator buy extra starts after burning its budget on its own instrument bug. I answer it directly, because the answer is the difference between GO and BLOCK:

1. The void would rewrite the record inside the same experiment (FAIL to VOID, budget reset). Option (b) does not touch the record. A1 and A2 stay FAIL (incomplete) in every table and every verdict sentence; the v2.1 experiment is CLOSED as BLOCKED with no comparative verdict, and the no-clean-win clause stays triggered for v2.1 permanently. Nothing is erased, nothing is relabelled.
2. The authority is the one the judge named. The ruling says a future A attempt needs "a versioned re-freeze (v2.2 or later) under sentence (j) and a fresh budget decision by the coordinator and council; this ruling does not authorize one." It withholds authorization from itself and assigns it to the coordinator and council. A council decision that keeps the FAILs standing is an exercise of that assigned authority, not an evasion of the ruling.
3. The new budget is bounded and symmetric: max 2 starts per arm under v2.2, the same cap the design always imposed. Arm A gets no more starts under v2.2 than arm B gets, and no more than it would have had under v2.1.
4. The new comparison carries its history in the open: the v2.1 FAILs, the instrument defect, the mid-experiment fix, and the elapsed time are disclosed to the final judge, which decides clean-win status. The coordinator does not pre-judge that question either way.
5. The labels make the break visible. v2.2 A starts are A3 and A4, not a restarted A1. Any reader can see that two v2.1 starts failed before the v2.2 comparison began.

The honest limit of this defense: in substance, the coordinator does get a second chance at the comparison after its own bug burned the first chance. Transparency does not erase that fact; it is the reason the terms in section 4 are conditions, not decorations. If the council were a rubber stamp, the redteam's objection would stand. I am not a rubber stamp: the terms below are what make (b) legitimate, and breaching term 1 (no re-freeze before any executor runs) voids this authorization.

Cost: two live slots for the pilot pair (A3, then B1), plus a possible second pair (B2, A4) if the replication trigger fires on the v2.2 pair. That delays Y9 by roughly the length of those runs, not indefinitely, and section 6 bounds Y9's wait with a defined release on every path.

### (c) Abort the experiment entirely. GO as a fallback, NOT recommended

This is clean, honest, and costless in live slots: report A BLOCKED plus the instrument defect as the finding, B never runs, Y9 released at once by the closure marker. If the council judged the comparison not worth two to four live slots, or judged the self-dealing appearance incurable, (c) would be the right call and I would not fight it.

I do not recommend it, for two reasons. First, the question is answerable now: the instrument is fixed and proven on the exact path that failed, the executors are exonerated, and the only thing standing between the experiment and its answer is a budget decision the judge expressly left to the coordinator and council. Aborting treats a fixable instrument defect as if it were a fatal design flaw, and it is not. Second, the deliberation phase (8m 40s parallel max plus 122 s merge, a 58-step plan) was paid for to be executed and compared; aborting writes that investment off with zero execution data. The cost of (b) is bounded (two starts per arm, pilot language only, final judge over clean-win status); the cost of (c) is the whole comparison. A bounded, disclosed second attempt is worth more than a clean abort.

## 4. Recommended option: (b), with exact terms

1. Re-freeze first. No executor runs until a v2.2 re-freeze note is committed on todolist-push, carrying: the root cause in one paragraph; the exact fix with the corrected counts (64 plan cmd objects, 26 js-bearing, 24 carrying the trap, 2 quoteless; 79 cmd objects total across plan, briefs A/A3/B, and driver reference); the new frozen md5s (plan 63415e9b6cd63dc2185ca23242180424, brief A b34bbfa0e419dcd8cec10e06a4575d16, brief A3 813bcebae435ddfc5b0b1c23de1c3807, brief B 054527b88eea3d6a6b18d19787b8177d, driver reference dde7ad584d22ac28d0573404e5d5cabb, preflight.py 5bfaebccace04e1c7e75c5cc5a837d22); the Q4 proof outputs by filename (v22-proof.log, preflight-a3.json); and this re-scope decision, with the v2.1 closure stated in it. The A3 brief (813bceb...) already exists but is NOT to be used unless this council authorizes a fresh A budget. This verdict is that authorization, conditional on this term.
2. v2.1 is CLOSED. A1 and A2 stay FAIL (incomplete) under v2.1, arm A BLOCKED under v2.1, no comparative verdict from v2.1, no-clean-win triggered for v2.1 permanently, the shell-quoting trap reported as the v2.1 finding, executors exonerated. A1/A2 wall times are reported separately and excluded from every v2.2 arm total.
3. v2.2 is a NEW comparison, not a continuation. New budget: max 2 starts per arm under v2.2. Labels are per-arm sequential counters, never reused: A3 is the first v2.2 A start, A4 the second (whether its role is retry or replication, the role is stated in every report); B1 is the first v2.2 B start, B2 the second (replication only). The old FAILs are history, disclosed in every table, never data.
4. Run order and hygiene. A3 first, then B1, never concurrent. Infra restarted between arms, frozen inputs re-verified by md5 before EACH arm (the inter-arm gap already exceeds 60 minutes, so the design's re-verification and disclosure rule applies), fresh pre-flight per arm, single live runner throughout.
5. Replication. The trigger is evaluated on the v2.2 pilot pair (A3, B1) under the frozen conditions at design line 139. If any condition holds, the second pair (B2, A4) runs in a fresh handover window before any comparative verdict beyond pilot language, order B then A, same v2.2 briefs, same v2.2 plan md5, results reported as a second pair, never merged into a single average without showing both pairs separately. The v2.1 history alone does not force the second pair (see section 5), but it is disclosed to the final judge.
6. Clean-win status. The coordinator claims no clean win or loss for v2.2. Verdict language is pilot language only. The final judge decides clean-win status with the full disclosure attached (v2.1 FAILs, instrument fix, elapsed time, infra restarts). Default reporting is "observed difference".
7. Stop rules. If A3 fails post-start for a NEW instrument defect, stop: do not burn A4 on another fix, return to council for re-scope. If A3 and A4 both fail, arm A is BLOCKED under v2.2 and the comparison aborts with the closure marker in section 6. The same mirror rules apply to B. If any pre-launch probe returns HTTP 500, fails JSON parsing, or fails JS parsing, stop: do not fix forward live, return to council with the failing output.
8. Wall time. v2.2 arm totals count only v2.2 starts. Within v2.2, retry waiting time and failed-attempt wall time count toward the arm total, per the design. A1/A2 wall times never enter a v2.2 total.
9. Post-run audit. The A3 and B1 event streams are audited for single-quote bytes inside js values, and the audit result is recorded in each arm report. After the fix, a quoting slip by an executor is an executor error, not an instrument defect.

## 5. The replication trigger: does it force anything?

Yes and no, and the distinction matters.

Under v2.1, the trigger is engaged. The judge is right: A1 and A2 fall under the design's "Post-start INVALID" heading, so the condition "either arm is flagged or invalid" holds. But an engaged trigger forces a second pair only before a comparative verdict beyond pilot language, and v2.1 has no pilot pair at all (B never ran) and therefore no verdict for the trigger to attach to. So under v2.1 the trigger forces exactly one thing: no comparative verdict, which is already barred. It forces no run, no re-run, and no label.

Under v2.2, the trigger is evaluated afresh on the v2.2 pilot pair (A3, B1). The v2.1 engagement does not carry over as a trip of the new comparison's trigger, because the trigger conditions are written about the pilot pair of the comparison they belong to ("Stage 1 is the n=1 pilot (A1, B1)"), and the v2.2 pilot pair is (A3, B1). A1 and A2 are history, not members of that pair. This is the same reading the earlier reconciliation adopted, and I adopt it for the same reason: a trigger cannot demand replication of a pair that does not exist yet, and it cannot be tripped in advance by runs that belong to a closed experiment.

I record the redteam dissent on this point openly: the redteam holds the trigger stays tripped because "either arm flagged or invalid" already holds. If the final judge adopts the redteam reading, the consequence is bounded and known in advance: the second pair (B2, A4) runs before any comparative verdict beyond pilot language. That is a cost, not a contradiction, and it does not change my recommendation. What would change it is a design sentence, which I have not found, stating that a trigger engaged in one version carries into the next version. I searched the design for the trigger conditions and the version rule; the version rule (line 13) governs changes to the instrument, not the carry-over of trigger state.

One discipline follows from the history regardless of the reading: the trigger conditions on (A3, B1) are evaluated strictly. A close call on any condition (times within 2 minutes, burden difference of 1 or less, wall times within 20 percent, any flag) is treated as holding, not rounded away.

## 6. The Y9 slot marker: what releases Y9

The marker as written cannot be satisfied if B never runs or A stays BLOCKED, because it demands a log line naming both arms' results. The fix is to define the release on every path, in the execution log, before A3 launches, so Y9's wait is bounded and defined instead of open-ended.

Under my recommended option (b), the marker is satisfiable as written, and Y9 keeps polling for it: commit subject matching ^Y8 E1: .*execution complete, plus the log line "E1 EXECUTION COMPLETE" naming both v2.2 arms' results (A3/A4 and B1/B2 as they stand). The v2.2 completion satisfies it; no marker change is needed for the success path.

For every other path, Y9 is released by a closure marker instead, and Y9's polling rule must be amended in the execution log to accept either marker before A3 launches:

- Closure commit subject: "Y8 E1: execution closed (A BLOCKED, B <status>)", where <status> is "never ran" or "single-arm observation complete" as the case may be.
- Closure log line: "E1 EXECUTION CLOSED: arm A BLOCKED under v2.1 (A1 FAIL incomplete, A2 FAIL incomplete, shell-quoting trap, no-clean-win triggered); arm B <status>; no comparative verdict." For the v2.2 abort path, the same form with the v2.2 standings substituted.
- The amendment is recorded in the execution log as: "Y9 release: either the E1 EXECUTION COMPLETE marker (both v2.2 arms' results) or the E1 EXECUTION CLOSED marker (closure with each arm's standing). Y9 proceeds on the first marker of either form."

Under option (a), Y9 is released by the closure marker with B's status "single-arm observation complete". Under option (c), Y9 is released by the closure marker with B's status "never ran". In no case does Y9 wait on a marker that the chosen path cannot produce.

## 7. What would change my mind

- If the v2.2 re-freeze note is not committed before any executor runs, this authorization lapses and the recommendation falls to (c). Term 1 is a condition, not a preference.
- If a design sentence I missed forbids a fresh comparison reusing the same task, or states that trigger engagement carries across versions, I would switch to (c). I searched the design for the budget, void, invalid, retry, replication, and version provisions; the only void-like consequences are the ones the judge enumerated, and none of their triggers is satisfied here, which is why the fresh-decision route is the legitimate one.
- If the live slot is needed by Y9 urgently, or the handover window closes before the pilot pair can run, I would switch to (a) for a single B validation run or to (c), whichever fits the remaining window, because an unfinished pair strands Y9 behind a half-run comparison.
- If A3 fails post-start for a NEW instrument defect, the v2.2 instrument itself is suspect and I would stop the comparison rather than burn A4 on another fix (term 7 already says this).
- If the final judge rules that the v2.2 comparison cannot claim even pilot language without the second pair running unconditionally, I would accept that as a cost term (run B2/A4) rather than abandoning the comparison, because the cost is two more live slots, not a contradiction.

## 8. Timing log (Asia/Ho_Chi_Minh, wall clock)

- 19:54:36: task received.
- 19:54-19:57: located the repo (~/workspace/computer-use-wayland, branch todolist-push), read the judge ruling in full and the reconciliation.
- 19:57: read the design v2.1 (frozen 695efea md5 verified), the Y9 marker lines in the design and execution log, and the earlier council 1/2 files (prior Q1-Q5 round, not this re-scope round).
- 19:57: independent fix verification on the working tree: md5s, command census (64 plan cmd objects, 26 js-bearing, 0 single quotes, 0 node failures; 15 more across briefs and reference, 79 total), STOPPED (DRIVER SUSPECT) wording, A3 artifact bans.
- 19:57-19:58: laptop read-only checks via ssh-laptop.sh: /tmp/e1/v22-proof.log (all six probes passed), /tmp/e1/preflight-a3.json (VISIBLE, countText 6), laptop plan md5 matches repo.
- 19:57-19:58: verdict written.
