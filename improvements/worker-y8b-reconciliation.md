# E1 v2.2 reconciliation: council 1/2/3 + redteam verdicts (Worker Y8b)

Coordinator adjudication, by evidence, not vote count. All times Asia/Ho_Chi_Minh, 2026-11-21.

## Verdicts received

| Member | File | Commit | Q1 | Q2 | Q3 | Q4 | Q5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Council 1 | worker-y8b-council-1.md | c1b285a | GO | AMEND | AMEND (substance GO) | AMEND | AMEND (conditional GO) |
| Council 2 | worker-y8b-council-2.md | 4849fec | GO | AMEND | GO with conditions | AMEND | AMEND (conditional GO) |
| Council 3 | worker-y8b-council-3.md | 8888f22 | GO | AMEND | GO | AMEND | AMEND (conditional GO) |
| Redteam | worker-y8b-redteam.md | 8d0fe98 | mechanism stands (S1 refuted) | SUSTAINED (fix does not close trap) | SUSTAINED (void is a rewrite) | SUSTAINED | BLOCK |

Convergence is genuine, not copied: each member produced independent checks (C1 node syntax check; C2 shell test quotetest.sh + programmatic plan census; C3 shell stub + JSON + node checks; redteam R1 stub replay + R2/R3/R4 plan extraction). All four independently found the same two defects in the proposal as written: the JSON-escaping omission and the steps 21/55 italic selectors.

Timing: council called 19:32:17. Verdicts written 19:38-19:52. Reconciliation written 19:44-19:55.

## Q1: quoting mechanism proven as root cause of A1 and A2. ADJUDICATED: GO (unanimous, 4/4)

The mechanism is proven. The chain, as established by all four:

1. The briefs hand the executor diagnose JS containing document.querySelector('#contacts-count') with single quotes (A/A2/B briefs line 25, step 3).
2. Both executors passed the JSON to step.sh single-quoted at the shell (exact commands in events-a.jsonl items 10/12 and events-a2.jsonl items 12/13). Shell semantics strip the inner quotes, so the driver receives querySelector(#contacts-count), a JS SyntaxError.
3. out.log matches: new_session ok, new_tab ok, then HTTP 500 in 2-4 ms twice per attempt. A syntax error answers in milliseconds; a timeout or dead driver does not.
4. Controlled live A/B on A2's own tab (repro-quote.sh): executor's exact quoting returns HTTP 500, identical JS with double quotes returns "6". Same tab, same minute, only quoting differs.
5. Pre-flight succeeds only because preflight.py calls step.sh via subprocess list argv (no shell). The coordinator's own double-quoted diagnosis returned the full VISIBLE snapshot with countText "6".
6. Independent shell-layer proof: C3's stub received exactly querySelector(#contacts-count); C2's quotetest.sh showed the mangled $1 is still valid JSON carrying broken JS; redteam R1 replayed both executors' exact commands through a stub and got the same mangling.

Honest gaps recorded (do not break the verdict): the exact bytes the driver received were never captured (no FIFO tap); the Marionette 500 error body was never captured (hand_drive_e1.py truncates to str(e)[:300]; geckodriver logs to DEVNULL). The live full-diagnose proof (Q4 gate 1) is the test that would falsify the mechanism before A3.

## Q2: v2.2 fix correct and complete. ADJUDICATED: AMEND (unanimous, 4/4)

Direction right; the proposal as written is wrong in two places and incomplete in the rest. Do not apply it as specified.

### Adopted exact transform (all four agree on substance)

- Inside a JSON string value in the briefs and the plan, a JS single-quoted string '...' becomes \"...\" in the FILE TEXT (backslash-doublequote). The shell single-quoted word passes the backslash through literally; json.loads decodes \" to "; the JS engine receives "...". Bare " without the backslash is INVALID JSON (proven: json.loads fails, Expecting ',' delimiter). The v2.2 text must state the \" form, never bare "single to double quotes".
- Steps 21 and 55 (Frank notes reads, .meta-line[style*="italic"]) are special: the escaped transform alone still breaks them, because the inner " terminates the JS string (node: SyntaxError, missing ) after argument list). Adopted form, content-preserving: JS-escape the inner quotes, so the decoded JS is ".meta-line[style*=\"italic\"]". In file text that is \".meta-line[style*=\\\"italic\\\"]\". The unquoted-CSS alternative ([style*=italic]) is rejected: it changes the selector text and would need its own live proof.
- The plan conversion is JSON-aware only: parse each command with json.loads, rewrite the string literals in the decoded JS, re-serialize with json.dumps. Never a text replace, never a global sed. A global replace corrupts the line 3 prose pair '<json>' and the naive swap breaks 24 of 64 commands (redteam R2: naive swap parses 40/64; JSON-aware re-parses 64/64, R3).
- Diff proof must be semantic, not "only quote characters change": decode old and new JSON commands and show the decoded JS values are identical except for quote style, keys/order/values/step count (58) unchanged. The correct transform adds backslashes, so the naive diff claim is false for every converted line and doubly false for steps 21/55.
- Both plan copies converted identically (repo improvements/worker-x-e1-plan-test-05.md and laptop /tmp/e1/plan-test-05.md), new md5 frozen in the v2.2 note.

### Corrected counts (all four agree; the log and the v2.1 note were wrong)

Plan: 64 JSON commands total; 19 evals (not 21), 7 click_js; 26 JS-bearing commands, 24 carrying the trap (2 quoteless: localStorage.clear eval and return window.__agyVerify() eval); 10 of 19 evals start with return, all 19 contain a return. The v2.1 note sentence "all 21 of its evals start with return" is wrong twice over. The v2.2 note uses the corrected counts. (C2 counts 79 JS string literals, C3 counts 78; the fix-phase sweep establishes the exact number programmatically and records it.)

### Remaining traps, adopted mitigations

- Driver reference: the quoting rule sits next to the eval line, in strong form (JSON is passed single-quoted to step.sh; JS strings inside it MUST use double quotes, written as \" in the JSON text; a single quote anywhere inside the JSON ends the shell quoting, is stripped, and reaches Marionette as a JS SyntaxError reported as HTTP 500 in a few ms while the driver stack is alive; symptom and recovery stated; one correct and one incorrect example). The click_js example (currently document.querySelector('...')) is fixed to the \" form. It currently teaches the trap.
- Prose that must NOT be converted: plan line 3 '<json>', briefs line 17 '<json>', driver reference line 7 '<json>', A2 brief line 13 "attempt's", preflight.py docstring/comment apostrophes (lines 7, 14, 145). The sweep scopes to decoded "js" values only; a whole-file grep is the wrong sweep.
- Preflight.py: converted for uniformity (all JS single quotes to double quotes; Python triple-quoted string, plain character swap, no backslash). All three council members support this; redteam calls it theater because argv is shell-free. Adjudication: convert, but record explicitly that preflight does NOT test the shell path and its conversion is not proof of the fix. The shell-path proof (Q4) is the proof. Re-verified by a fresh pre-flight run before A3.
- A-composed JS is the biggest residual trap. Adopted, layered: (a) the A3 brief carries EXACT double-quoted JSON for the fixed final-read evals (David favorite, Spam Bot absence, Frank DOM) and the localStorage eval, since the list is frozen and identical for both arms, so exact commands add no deliberation content (C1, redteam gate 5 first option); (b) the quoting rule plus a worked double-quoted DOM-read example sits in the A3 brief itself, not only in the driver reference; (c) post-run audit of A3's event stream for ' bytes inside js values (C2 Q4 item 8). For A's other spec-step evals, the rule is the mitigation and the residual risk is accepted in writing; after the fix, a quoting slip by the executor is an executor error, not an instrument defect.
- DRIVER DEAD labelling is misaligned and v2.2 fixes it (C1, redteam S6.2): the briefs' "two consecutive failures of any kind mean DRIVER DEAD" contradicts the design, which requires the coordinator's three liveness checks first. A1/A2 declared DRIVER DEAD while the driver, geckodriver, and port 4451 were all alive, so those declarations were false under the design's own rule. Changed in the briefs: after two consecutive failures the executor stops and records STOPPED (DRIVER SUSPECT, coordinator to classify); it never labels DRIVER DEAD itself. The coordinator's classification checklist (C3 Q4 item 3h) is added to the design: before accepting any DRIVER DEAD declaration, inspect the failed command's JS in the events file for single quotes (the quoting trap) and record the check. This is the one-minute check that would have caught the trap at A1 without a council round.
- Type text / find css / new_tab url vectors (redteam S2f): no apostrophes exist in this task's typed values or plan type texts (verified by C2 census: zero single quotes in text/css/url/el fields; spec possessives are prose only). The strong-form rule covers all fields anyway. Executor-typed values for A are covered by the rule plus the post-run audit.
- Shell double-quote wrapping is forbidden (redteam S2e): exactly one form, single-quoted shell argument, JS double quotes escaped as \", never \', never shell double-quote wrapping (which would make $ and backticks live). The rule states this.
- A2 brief is NOT edited: it is a historical artifact of a voided run. Fix the base A brief and the B brief, create a new A3 brief. Leave the A2 brief byte-identical as the record of what A2 was ordered to do (C3 Q2 item 6).

### Runtime conversion by the B executor: rejected (unanimous)

It violates the B brief ("execute ONLY that plan", "do not fix the plan"), puts 26 conversions under executor discretion with no diff proof, forces the executor to convert through the same trap it is avoiding, and breaks the same-md5 replication condition. The plan is fixed once, in the open, with proof.

### Deferred, not adopted in v2.2

- Transport hardening (step.sh reading JSON from stdin or a file): considered and rejected for v2.2 by C1 (unproven through codex's bash -lc wrapping, while the payload fix was proven live) and recorded as future work by C2. Redteam gate 6 demands one of three options (transport change, shell-path preflight, or pre-launch shell-parse gate). Adjudication: the v2.2 control IS option (c), the pre-launch shell-parse gate, implemented as Q4 gates 1-3 below (live shell-path proof of the fixed commands plus a full static sweep of every command). A full live run of every converted eval on a scratch tab is not adopted: it would execute task mutations on a shared-origin tab, and the static sweep (json.loads + node parse of every js value) plus sampled live proof covers the same risk. Transport hardening stays future work.
- Marionette error-body capture in hand_drive_e1.py (redteam S1 caveat, gate 7 second half): deferred to future work. Reason: the driver is frozen and working, the running driver process holds the old code, and a driver edit would force an infra restart for a diagnostic nicety. The coordinator DRIVER DEAD checklist above is the substitute classifier. The gap (500 bodies never captured) stays recorded.

## Q3: A1/A2 void, budget reset, next A start A3. ADJUDICATED: CONDITIONAL, pending a binding independent judge ruling

### The council position (3/3 for voiding, with conditions)

- Zero task steps ran in either attempt, so voiding discards no data. The cause is a deterministic defect in the frozen instrument, identical for both arms, proven by a controlled live A/B repro. Both executors followed the brief exactly. The executor-tab diagnose is a gate by design; a gate broken by its own wording cannot produce a FAIL.
- Precedent in the same run: the v2.1 pre-flight failure consumed no budget because no classification was made; the 19:06 driver death was treated as an infra fault, not an arm retry. The same principle applies one step later.
- The design's post-start rule was written for genuine run events (crash, DRIVER DEAD, mid-run hidden body) presupposing a runnable instrument. It cannot sensibly consume budget on a command that cannot succeed as written. Exhaustion would kill the experiment over a fixable defect affecting both arms identically and would violate "never compare one measured arm against nothing" in substance: B would have 500ed identically before the fix.
- Bounded void test (C2, four parts; C3 narrow rule, four conditions): a start is void ONLY when (i) the failure occurs before the first task step, (ii) the root cause is proven to be a defect in the frozen instrument, not an executor choice, (iii) the defect is deterministic and reproducible on demand, (iv) the voided attempts stay in the record with their labels, and the fix is applied identically to both arms before any further start. Any future void failing any part is not a void, it is a FAIL. Exactly one void per arm per experiment, ever.

### The redteam objection (BLOCK), and how it is answered

Redteam S4 is sustained as a real objection: the frozen text, read literally, says A1 is FAIL (incomplete), A2 is the second observation, and the arm is BLOCKED; there is no void clause for post-start failures; the void is an amendment after the failures it would erase; and the pattern so far is four consecutive non-counting failures (pre-flight 1, pre-flight 2, A1, A2) with zero counting failures. The beneficiary of the void is the coordinator's own experiment. That objection cannot be answered by the coordinator alone, because the coordinator wrote the briefs that contained the trap.

Adjudication: the void is NOT decided by the coordinator or by this council alone. It is decided by an independent judge (Judge-V, spawned 19:44), ruling from arm-stripped evidence on the question VOID vs FAIL, with no knowledge of the council's conclusions and no access to the council or redteam verdict files. The judge's VOID/FAIL ruling is binding. If the judge rules VOID, the void stands under the bounded test above. If the judge rules FAIL, arm A is exhausted per the frozen text and the comparison is re-scoped (council reconvenes; no A3).

This adopts redteam gate 1. It is the only gate that removes the self-dealing hazard, and it is cheap (one paper round).

### Terms that apply IF the judge rules VOID

- A1 and A2 stay in the record, labelled VOID (instrument artifact), with full evidence attached (events-a.jsonl, events-a2.jsonl, out.log 500 ranges, repro-quote.sh, wall times, token counts). Log annotation, not rewrite: the original FAIL lines stay visible. The 19:22 "transient tab mid-state" diagnosis is superseded by the reproduction; the annotation says so.
- Budget: max 2 VALID starts per arm (C1/C3 formulation). A3 is the first valid A start; A4 is available only as a genuine second valid start under the frozen retry rules. This is adopted over redteam guard 4 ("A3 only, no A4") for two reasons: the cap's purpose is bounding re-rolls of a working instrument, and A1/A2 were not rolls of a working instrument; and the replication pair (below) needs A4 to exist as a label. The one-void-ever rule plus the 2-valid-start cap bounds the total: arm A can never exceed 2 valid starts, the same as B. The redteam dissent on this point is recorded here.
- Voided-start wall time is EXCLUDED from A's execution total (C3): A1 coordinator wall 151 s and A2 wall are reported separately, not counted. The design's "failed-attempt wall time counts toward the arm's total" was written for genuine retries; applying it here would bake the coordinator's instrument bug into A's total. The exclusion is frozen here, before A3 runs, not chosen after.
- Replication pair renamed to (B2, A4) (C1): start labels are per-arm sequential counters of all starts, voided or not, and labels are never reused. C2's alternative (A3 doing double duty as both first observation and second-pair run) is rejected as confusing.
- Replication trigger is evaluated on the valid pilot pair (A3, B1) under the frozen conditions. Redteam holds the trigger stays tripped because "either arm flagged or invalid" already holds; adjudication: that condition is evaluated on the valid pair's runs, not on voided attempts, which are instrument artifacts and not arm observations. The redteam dissent is recorded here and disclosed to the final judge.
- No-clean-win clause: the void does NOT auto-trigger the clause (C1/C2/C3). The clause was written for browser-health confounds during measured runs; the void is an instrument fix before any measurement. BUT the pilot pair runs under a disclosed history (two voided starts, a mid-experiment instrument fix, a plan edit, roughly an hour elapsed, an infra restart, an unexplained holder death), and the final judge decides whether any win is clean with that disclosure in front of it. Redteam's position (permanent downgrade: "observed difference, confounded by browser health" even if A3 and B run clean) is NOT adopted as a pre-judgment, because pre-judging the clean-win question would itself be coordinator overreach over the judge's remit. The redteam's downgrade argument is recorded in full here and goes to the final judge with the disclosure. This is the adjudicated middle: the clause is not triggered by fiat, and it is not cleared by fiat either.

## Q4: what else must change before any executor runs. ADJUDICATED: gates below, all required

No executor runs until every gate passes and the v2.2 re-freeze is committed.

1. Live shell-path proof of the FULL fixed diagnose JS, byte-identical to the A3 and B briefs, through the executor's exact invocation (single-quoted step.sh call via bash -lc as codex wraps it), on a fresh live tab. Expected: full VISIBLE snapshot with countText "6". The existing repro proved only a short count read.
2. Same-path live proof of converted plan commands before B runs: plan step 4 eval (widest eval), plan step 31 click_js followed by step 32 eval (starActive true, cardFavorite true), the steps 21/55 italic-selector eval (expected {"ok": true} with result null, NOT a 500; Frank does not exist yet on a fresh tab, so null proves the JS parses and runs), and plan step 56 eval (return window.__agyVerify()). All on a sacrificial tab, closed and session deleted afterwards, outputs saved to /tmp/e1/v22-proof-<name>.log.
3. Mechanical sweep, run on the FINAL frozen files, output logged: every JSON command in the plan (64) parses with json.loads; every decoded "js" value parses (node new Function, parses without executing); zero single quotes inside any decoded "js" value across the fixed briefs, driver reference examples, and plan; converted plan prose byte-identical except the JSON js strings (line 3 pair untouched); prose exceptions listed (plan line 3, briefs line 17, driver reference line 7, A2 line 13, preflight.py lines 7/14/145).
4. A3 brief created and frozen with md5 recorded: new file improvements/worker-y8-executor-a3-brief.md, derived from the fixed A brief, with fixed diagnose JS in the \" form, quoting rule plus worked example inline, exact final-read JSON plus localStorage JSON, HTTP 500 re-check rule, STOPPED (DRIVER SUSPECT) wording, report run-a3-report.md, bans on A1/A2 artifacts (run-a-report.md, run-a2-report.md, events-a.jsonl, events-a2.jsonl, out.log).
5. Driver reference fixed: strong-form quoting rule next to the eval line, click_js example in double quotes, symptom plus recovery, return rule kept, single-form prescription (single-quoted shell argument, never shell double-quote wrapping).
6. Preflight.py converted (all single-quoted JS strings, plain swap) and re-proven by a fresh pre-flight pass before A3 (saved to /tmp/e1/preflight-a3.json). Recorded: preflight argv path does not test the shell path.
7. Design v2.2 re-freeze note carrying: the root cause in one paragraph, the exact fix with the corrected counts, the Q3 void rule and wall-time exclusion, the replication rename, the no-clean-win scope, the new frozen md5s (plan, briefs A/A3/B, driver reference, preflight, step.sh), and the pre-launch proof outputs by filename.
8. Log annotation entries for A1/A2 VOID (once the judge rules), out.log archived per attempt before A3 (the reproduction 500 and "6" lines currently contaminate the A2/A3 boundary; session-boundary counting needs a clean archive), and /tmp/e1/repro-quote.sh committed to the repo under improvements/ as the root-cause evidence artifact.
9. Frozen md5 re-verification of all inputs before A3, as the design already requires before each arm.
10. Residual risk stated in the log: the 19:06 FIFO-holder death is still unproven. The driver has been alive since 19:08 and verified repeatedly, so it is not a blocker, but if it recurs before A3, stop and diagnose rather than pushing through.
11. Post-run audit of A3's event stream for ' bytes inside js values, recorded in the A3 report (C2 Q4 item 8). After the fix, a quoting slip is an executor error.

## Q5: verdict on the v2.2 re-freeze + A3. ADJUDICATED: CONDITIONAL GO

Do not re-freeze or launch A3 on the v2.2 proposal as written. GO the moment: (a) the independent judge rules VOID on A1/A2, (b) the Q2 amendments above are applied, (c) the Q4 gates pass, and (d) the v2.2 re-freeze note is committed. No executor runs before that commit. If any pre-launch probe returns HTTP 500, fails JSON parsing, or fails JS parsing, stop: do not fix forward live, return to council with the failing output.

## Correction to the pre-compaction record

The pre-compaction prep claimed a plan conversion was "proven on a copy (/tmp/plan-converted.md)". That claim is NOT trusted: all four verdicts prove the mechanical form it describes breaks 24/64 commands and steps 21/55 specifically. /tmp/plan-converted.md will be verified against the Q4 sweep before use and discarded if it fails; the conversion is re-done JSON-aware with proof regardless.

## Dissent register (for the final judge)

- Redteam gate 4 (A3 only, no A4): not adopted; reason in Q3 terms above. Dissent recorded.
- Redteam permanent no-clean-win downgrade: not adopted as pre-judgment; the argument goes to the final judge with the disclosure. Dissent recorded.
- Redteam "replication trigger stays tripped": not adopted; trigger evaluated on (A3, B1). Dissent recorded.
- Redteam gate 7 second half (Marionette error-body capture in hand_drive_e1.py): deferred to future work; checklist substitutes. Recorded.
- Transport hardening: deferred to future work by C1/C2/C3; the shell-parse gate is the v2.2 control. Recorded.

## Next steps, in order

1. Judge-V rules on A1/A2 (VOID vs FAIL), binding. Spawned 19:44.
2. Apply the v2.2 fix per Q2 (briefs, driver reference, preflight, plan conversion JSON-aware, A3 brief).
3. Run the Q4 pre-launch proof (live shell-path probes + sweep), save outputs.
4. Write the v2.2 re-freeze note, commit, push, transfer files to /tmp/e1/, verify md5s.
5. Fresh pre-flight, launch A3.
