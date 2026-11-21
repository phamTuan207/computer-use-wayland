# E1 RE-SCOPE reconciliation: council 1/2/3 + redteam after the binding judge ruling (Worker Y8b)

Coordinator adjudication, by evidence, not vote count. All times Asia/Ho_Chi_Minh, 2026-11-21.

## Verdicts received

| Member | File | Commit | (a) B alone | (b) Fresh comparison | (c) Abort | Recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| Council 1 | worker-y8b-rescope-council-1.md | ee71271 | AMEND (conditional GO) | AMEND (deferred, not tonight) | BLOCK | (a) |
| Council 2 | worker-y8b-rescope-council-2.md | 7bc789d | AMEND (conditional GO, 7 terms) | BLOCK | GO (fallback) | (a) |
| Council 3 | worker-y8b-rescope-council-3.md | 43300ca + 6d55e65 | AMEND (acceptable fallback) | GO (9 terms) | GO (fallback) | (b) |
| Redteam | worker-y8b-rescope-redteam.md | e5241bb | AMEND | BLOCK | GO (recommended) | (c) |

The judge's ruling (7275171) is binding and was not re-debated by any member. A1 FAIL (incomplete), A2 FAIL (incomplete), arm A BLOCKED, no-clean-win TRIGGERED, executors exonerated. The v2.1 comparison is OVER.

## Adjudication

### Option (b), fresh comparison with a new A budget: NOT AUTHORIZED tonight

Two BLOCKs (Council 2, redteam) against one GO (Council 3) and one deferred (Council 1). The BLOCK arguments are the stronger reading of the record:

- The judge's sentence lists necessary conditions and expressly withholds authorization ("this ruling does not authorize one"). It does not say the council MAY grant a fresh budget; the design contains no budget-grant mechanism ("Max 2 starts per arm" is a cap, not a power to re-issue starts). Reading the sentence as permission inverts it (redteam).
- The win rule keys on first observations FAIL/FAIL, which support nothing; a third observation cannot ground a win under the frozen text. No-clean-win is already TRIGGERED as a historical fact, so the best outcome (b) can ever reach is "observed difference, confounded by browser health", the same ceiling (a) reaches with one slot (C2, redteam).
- Label discipline fails: A3 reads as continuation of the same arm; the replication pair (B2, A2) has A2 spent (label reuse forbidden); the same-md5 replication condition fails by construction (plan md5 changed); running A then B again violates the ABBA order prescription (redteam).
- Precedent: if a BLOCKED arm's budget can be reset by council vote after a binding adverse ruling, BLOCKED is advisory and the ruling was theater (redteam). Council 1, sympathetic to (b) in principle, does not authorize it tonight either (sequencing: B validation first; queue: Y9 4-hour timeout; cost: a 4-run, 2-window program, not a 2-run comparison).

Council 3's defense is recorded and respected (the judge assigned the fresh-budget decision to coordinator and council; v2.1 CLOSED as a separate experiment with FAILs kept; the new budget is symmetric at max 2 per arm; the ceiling is conceded). It does not overcome the two BLOCKs tonight, because the authorization the judge's sentence withholds cannot be supplied by the same body that ran the experiment without the design containing the power to grant it. A future NEW experiment (new design doc, new labels, new pre-registration, win criteria re-derived, no-clean-win evaluated afresh, E1's FAILs cited as prior work not data) is NOT blocked in principle; its terms are recorded below for a future proposal. Nothing under (b) is authorized tonight.

### Option (a), B runs alone under v2.2 as a single-arm observation: GO, on the binding terms below

No member BLOCKs (a). Two council members recommend it; one accepts it as fallback; redteam rates it AMEND (gates, not BLOCK). The finding is real and otherwise unobtainable: the only end-to-end test of the 58-step plan bundle and of the v2.2 instrument (the 6 probes prove sampled commands, not the full run; the italic selectors with Frank present are unproven). Cost is one live slot. It does not foreclose a future new experiment (a future comparison re-runs BOTH arms fresh).

The redteam's sharpest objection to (a) is adopted as a binding constraint, not dismissed: a B PASS satisfies the frozen accuracy-win disjunct (B passes and A fails) while the triggered no-clean-win clause forbids claiming it, with no judge scheduled to adjudicate the conflict, so the number will be misread as a verdict. The answer is the fencing in the terms below (pre-registered forbidden sentences, the report's first paragraph, the B1-v2.2 label, no pairing with any future A run) PLUS an independent judge scheduled for B1-v2.2 (Council 2 term 5: PASS/FAIL read from out.log by the independent judge from the fixed final-read list, never from an executor claim). The judge adjudicates B1-v2.2's PASS/FAIL and burden; it adjudicates no comparative verdict, because none is claimable.

The redteam's second objection (B-only does not release Y9; Y9 keeps polling to its 4-hour timeout around 22:53) is answered by the amended marker below (Council 1 section 8 + Council 2 section 6, merged). Y9's polling is not unamendable: the Y9 plan's own abort rule already anticipates a non-completion release, and the coordinator is required to amend the Y9 plan in writing before Y8 closes (Council 1's mandatory step). The closure marker names both arms' FINAL states (A BLOCKED is a standing, B1-v2.2 is a result), which satisfies the marker's intent ("Y8 is done with the live slot and both arms are accounted for").

### Option (c), abort entirely: FALLBACK, not taken

Council 1 BLOCKs it as the recommendation; Council 2 and 3 accept it as fallback; redteam recommends it. It stays the fallback if (a)'s fencing cannot be held, the live slot is unavailable, fresh pre-flight B fails, or B1-v2.2 hits an HTTP 500 (fail-closed, return to council, which may then choose (c)).

## Binding terms for option (a) (breach of any term voids the GO)

1. Re-freeze first. A v2.2 re-freeze note is committed BEFORE any B launch, carrying: the v2.1 comparison is CLOSED (arm A BLOCKED, A1/A2 FAIL incomplete, judge 7275171, no comparative verdict, replication trigger engaged and undischarged for v2.1); the v2.2 files are frozen for a SINGLE-ARM B OBSERVATION ONLY, not a comparison; the new md5s (plan 63415e9b6cd63dc2185ca23242180424, brief A b34bbfa0e419dcd8cec10e06a4575d16, brief B 054527b88eea3d6a6b18d19787b8177d, driver reference dde7ad584d22ac28d0573404e5d5cabb, preflight.py 5bfaebccace04e1c7e75c5cc5a837d22, step.sh unchanged); the Q4 proof outputs by filename (v22-proof.log, preflight-a3.json, consolidated sweep); and the no-comparison fence below. The A3 brief (813bcebae435ddfc5b0b1c23de1c3807) is recorded as created and NOT used. No executor runs before that commit.
2. One B start only, labelled B1-v2.2 in every table and every verdict sentence, never bare B1 (the v2.1 B1 never ran, and the label must not be confused with it). Pre-start INFRA-BLOCKED: one pre-flight retry after at least 10 minutes per the design, then stop. Post-start crash: recorded as FAIL (incomplete), the observation ends, and there is NO B2 under this authorization. Any B2 needs a new council decision. Infra is restarted before B, out.log is archived per arm, and the v2.2 md5s are re-verified before launch.
3. Fresh pre-flight B before launch, saved to /tmp/e1/preflight-b.json. Md5 re-verification of all frozen inputs before B starts.
4. Verdict language is frozen to single-arm observation. The B report records: PASS/FAIL from the fixed final-read list read from out.log by the independent judge (never from the executor's claim), accuracy burden (check failures plus error incidents plus misclicks, with step numbers), plan deviations and PLAN DEFECTs by plan step number, execution wall on the primary clock, driver-command count, tool calls, tokens in and out, and pre-flight evidence. The FIRST lines of the B report state: single-arm observation under v2.2, no comparison, no deliberation win or loss claimed.
5. Forbidden comparisons, enumerated. No comparison of B's wall to A1/A2 walls (the 151 s coordinator wall with zero task steps is not an A time). No comparison of B's wall to the spec's 150 s expected or 260 s max as a win claim (those numbers may appear as context only, with the caveat that they are not a measured arm). No total-speed arithmetic (the 642 s sunk deliberation cost is recorded separately and never added to a total-speed verdict, because there is no A total to compare against). No accuracy comparison. No headline saying "deliberation wins" or "deliberation loses" in any form. No "pilot verdict" language. No pairing of this B run with any future A run: a future comparison re-runs BOTH arms fresh, under its own freeze and budget. Any sentence that violates this list is struck from the report before it is committed.
6. No-clean-win stays TRIGGERED. It is recorded as triggered for E1, and it is irrelevant to a single-arm observation, which claims no win at all. It is not cleared, not re-evaluated, and not used to upgrade B1-v2.2 into a clean result.
7. Replication trigger stays ENGAGED and UNSATISFIED for v2.1, permanently. This lone B run neither satisfies it nor clears it. It creates no pilot pair, and no comparative verdict may be drawn from it, now or later, by pairing it with anything.
8. Fail-closed. If any B command returns HTTP 500, or any command fails JSON or JS parsing, the executor stops immediately, the run is recorded as it stands, and the matter returns to council with the failing output. Do not fix forward live. A 500 on the fixed instrument would falsify the v2.2 proof, and that falsification is itself the finding.
9. Post-run audit. The B1-v2.2 event stream is audited for single-quote bytes inside js values, and the audit result is recorded in the B report. After the fix, a quoting slip by an executor is an executor error, not an instrument defect.
10. Y9 release by the amended marker below, immediately after the B observation completes, the closure line is committed, and infra is stopped and verified (INFRA_DOWN, ports 4451 and 8767 free, no foreign geckodriver). A log line alone does not free the slot.

## Y9 slot marker, amended (exact)

The original marker cannot be satisfied as written (it demands a log line naming both arms' results, and arm A has no valid result). The amended marker redefines "both arms' results" as "both arms' FINAL states". Y9 treats EITHER the original marker OR this amended marker as release. The coordinator amends the Y9 plan (improvements/worker-y9-agy-y2-live-plan.md, section 5) in writing before Y8 closes, redefining legs (a') and (b') from "both arms completed" to "both arms accounted for, comparison closed".

- Leg (a'): a commit on todolist-push after 4a78f7f matching the SAME regex ^Y8 E1: .*execution complete, for example "Y8 E1: B single-arm observation execution complete, v2.1 comparison closed". The message must not claim both arms completed.
- Leg (b'): a NEW line in improvements/worker-y8-e1-execution-log.md matching "E1 EXECUTION COMPLETE" that names both arms' FINAL states: arm A BLOCKED (A1 FAIL incomplete, A2 FAIL incomplete, judge 7275171) and arm B single-arm observation B1-v2.2 (PASS/FAIL, execution wall, burden), plus the literal words "no comparative verdict" and "live slot released to Y9".
- Leg (c): Y4d's completion verified DIRECTLY, unchanged (already satisfied by 1e3901c).
- Plus the existing abort-rule live checks at launch time (Y8 ports 4451 and 8767 free, no foreign geckodriver, flock) as the real safety gate. The git marker is the signal; the live checks are the proof the slot is actually free.
- If option (c) were taken instead, the same amended marker applies with "ABORTED" and "arm B never ran", and the abort commit message must NOT contain "execution complete" and the abort log line must NOT contain the literal string "E1 EXECUTION COMPLETE" (redteam risks 1-2: false-positive regex/grep hits).

## Deferred: terms for a future NEW experiment (not authorized)

If a fresh comparison is ever proposed, it is legitimate ONLY on all of these terms (Council 1 section 6, Council 2 section 3, redteam PREFERRED path, merged): new experiment, not a continuation (new design doc, new version, new pre-registration, new labels never reusing A1/A2/B1); old FAILs carried in every table and every verdict sentence with judge 7275171 cited; budget is NEW, not reset (the v2.1 budget is closed, exhausted; no sentence may say the budget was reset); ceiling conceded upfront (no clean win or loss ever, for this lineage; verdict language capped at "observed difference, confounded by browser health", pilot language only); replication pair mandatory before any comparative verdict beyond pilot language, in a fresh handover window; queue honored (Y9's 4-hour timeout respected). No executor runs under this path tonight.

## Dissent register

- Council 3's (b) GO: not adopted tonight, for the reasons above. Its terms are preserved in the deferred section.
- Redteam's (c) recommendation: not adopted as the primary path; (c) is the fallback. Its Y9 false-positive cautions (exact abort wording) are adopted for the abort path.
- Redteam's (b) BLOCK: adopted for tonight. Its PREFERRED path (new experiment) is preserved in the deferred section.

## Next steps, in order

1. Write the v2.2 re-freeze note (design file), commit the v2.2 files + reconciliation + Y9 plan amendment + log, push, verify.
2. Fresh pre-flight B, md5 re-verification, infra restart, launch B1-v2.2 (single start, brief B v2.2, converted plan).
3. Independent judge reads B1-v2.2 PASS/FAIL and burden from out.log (de-labeled evidence not needed: single arm; the judge scores the fixed final-read list only).
4. Final B report with the fencing in term 5, closure marker + infra stop, Y9 released.
