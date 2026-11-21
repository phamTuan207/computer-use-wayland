# Council Member 1 verdict: E1 v2.2 (shell-quoting trap) - Worker Y8b council

Role: Council Member 1. Debate on paper only. No Zen driving, no executor launches, no live browser use. Evidence was read from the repo and from the laptop via short read-only calls (ssh-laptop.sh cat/grep), plus a local syntax check on the VM (node, no browser).

Timing: task received 19:33:05 +07, 2026-11-21. Evidence gathered 19:33-19:38. Verdict written 19:38-19:44. Commit and push follow.

## Evidence base

- Design v2.1 frozen: improvements/worker-y8-e1-comparison-design.md (commit 695efea). Key rules cited: max 2 starts per arm; post-start first run IS the arm result; DRIVER DEAD needs the three liveness checks (driver alive means timeout, not death); replication pair named (B2, A2); "never compare one measured arm against nothing"; no-clean-win clause for an arm that needed an infra retry.
- Execution log: improvements/worker-y8-e1-execution-log.md (commit ad64bc6), entries 19:17:04 to 19:32:17.
- Briefs: worker-y8-executor-a-brief.md line 25, worker-y8-executor-a2-brief.md line 25, worker-y8-executor-b-brief.md line 25 (diagnose JS in each).
- Driver reference: worker-y8-driver-reference.md lines 9 and 13 (click_js example with single quotes; click policy).
- Preflight: worker-y8-preflight.py lines 37, 45, 54-55 (DIAGNOSE_JS, transition concat, REMOVE_TZ_JS); step() function uses subprocess list argv, no shell.
- Plan: /tmp/e1/plan-test-05.md on the laptop, copied to the VM and verified md5 a7b5646b2bf081386bb7bcea0563ad5a, identical to the frozen value.
- Laptop evidence: /tmp/e1/events-a.jsonl and events-a2.jsonl (exact executor shell commands), /tmp/e1/out.log (command results in order), /tmp/e1/repro-quote.sh (coordinator A/B reproduction).
- Sweep (this council, on the verified plan copy): 64 JSON commands found; 24 js values contain a single quote; exactly 2 js values contain a double quote (plan steps 21 and 55); every other single quote in the file sits inside a backtick JSON command except the line 3 prose pair '<json>'.
- Node syntax check (this council, VM, no browser): naive single-to-double conversion of the step 21 js fails with "missing ) after argument list"; the escaped-inner-double form parses OK; the unquoted-CSS-value form parses OK.

## Q1: Is the shell-quoting mechanism proven as the root cause of both A1 and A2? GO

Yes, proven. The chain has five links, each cited:

1. The briefs hand the executor a diagnose JS containing document.querySelector('#contacts-count') with single quotes (A brief line 25, A2 brief line 25, B brief line 25).
2. Both executors passed the JSON to step.sh single-quoted, the natural method the briefs and the driver reference teach (step.sh '<json>'). The exact commands are in the event streams: events-a.jsonl shows A1's eval command with querySelector('#contacts-count') inside the single-quoted JSON, twice; events-a2.jsonl shows the identical command from A2, twice (wrapped in a sed/tee pipe, which does not change the quoting of the step.sh argument). Shell semantics do the rest: the quote before #contacts-count ends the quoted string, so the driver receives querySelector(#contacts-count) with the quotes stripped, which is a JS SyntaxError.
3. out.log matches that mechanism exactly, in order: A1 new_session ok, new_tab ok, then HTTP 500 in 2 ms and HTTP 500 in 4 ms; A2 new_session ok, new_tab ok, then HTTP 500 in 3 ms and HTTP 500 in 3 ms. A syntax error answers in milliseconds; a timeout or a sick browser does not.
4. Controlled reproduction on A2's own tab (repro-quote.sh, out.log tail): the executor's exact quoting returns a third HTTP 500, and the identical JS with double quotes for the selector returns "6". Same tab, same minute, only the quoting differs. This falsifies the coordinator's 19:22 "transient tab mid-state" guess and explains why A2 repeated A1 identically.
5. The contrast with pre-flight is predicted by the mechanism, not an anomaly: preflight.py calls step.sh through subprocess list argv (no shell), so its single-quoted JS survives; the coordinator's own diagnosis used double quotes and returned the full VISIBLE snapshot with countText "6". The instrument worked; the brief's JS as pasted through a shell did not.

What would falsify it: (a) the fixed double-quoted diagnose JS, run through the executor's exact shell path, still returns HTTP 500 on a live tab; (b) a capture of the exact bytes the driver received showing the quotes intact while the 500 still occurs; (c) a single-quoted diagnose JS passed through the shell ever returning a snapshot, which would mean the shell did not strip the quotes; (d) a competing cause that also explains the A/B contrast in the reproduction, for example a Marionette fault tied to those exact tabs at those exact minutes, which the same-tab A/B already rules out. One honest gap: the exact bytes the driver received were not captured (no FIFO tap is cited), so the proof is a controlled same-tab A/B plus shell semantics plus the event-log command text. That is proof at the level this experiment needs, and Q4-1 is the test that would falsify it live before A3.

## Q2: Is the v2.2 fix correct and complete? AMEND

Direction is right; the proposal as written is incomplete in three places and wrong in one. Do not apply it as a mechanical single-to-double swap.

(a) Diagnose JS in the briefs and preflight: correct. Each brief's diagnose JS has exactly one single-quoted string ('#contacts-count') and no inner double quotes, so single-to-double is safe there. Preflight conversion is uniformity, not a fix: preflight already works through argv, but its DIAGNOSE_JS (line 37), REMOVE_TZ_JS (lines 54-55, 'tz-hidden' and '--zen-logo-path'), and the transition concat (line 45, ' ' strings) must all be converted together, or two dialects of the same diagnose JS will exist again, which is how this bug hid.

(b) Quoting rule in the driver reference: the rule must be stated in the strong form, and the reference's own example must be fixed. Strong form: the JSON argument is passed in single quotes at the shell, so the JSON text must contain NO single-quote character anywhere, in any field (js, css, text, url, el). Write every JS string literal with double quotes. The click_js example on line 9 currently teaches document.querySelector('...'), which is the trap itself; change it to double quotes. Add the symptom (an eval that looks right returning HTTP 500 in a few ms) and the recovery (inspect the JSON passed; if it holds a single quote, re-issue once with double-quoted JS strings). A blind identical retry of a deterministic syntax failure cannot succeed; A1 and A2 proved that twice.

(c) Convert the plan; do NOT let the B executor convert at runtime. Three reasons. First, the B brief forbids improvisation ("execute ONLY the plan", "do not improve the plan"); runtime conversion turns the executor into a second deliberator and breaks the treatment, and a failed conversion would be unclassifiable (plan defect or executor error?). Second, runtime conversion is error-prone live with no diff proof: the executor would have to spot all 24 single-quoted JS strings, including the two both-quote cases below, and get the JSON escaping right under time pressure. Third, a frozen converted plan with a version bump and an md5 re-freeze is the design's own procedure (as v2.1 did for the return prefix) and preserves judge auditability. Runtime conversion also breaks the replication condition "same plan file (same md5)".

(d) The naive conversion breaks steps 21 and 55. This is the one place the proposal as written is wrong. The sweep proves exactly 2 of the 64 JSON commands contain a double quote inside their js, both the .meta-line[style*="italic"] selector (plan steps 21 and 55). Naive replacement yields querySelector(".meta-line[style*="italic"]"), which node rejects as "missing ) after argument list". The correct converted form keeps the exact selector by escaping the inner doubles in the JS: querySelector(".meta-line[style*=\"italic\"]") (parses OK in the node check). The alternative, unquoted CSS value [style*=italic], also parses OK but changes the selector text, so it needs a live proof that it selects the same node; prefer the escaped form because it preserves the exact selector. Further, "diff proof (only quote characters change)" is NOT sufficient: the broken naive form also changes only quote characters. The proof must be semantic: parse all 64 JSON commands from the converted file, syntax-check every js value, assert zero single quotes in any JSON text, and prove the two hard evals live (Q4-2). The conversion must also be scoped to JSON command strings only: a global replace would corrupt the line 3 prose pair '<json>' in the documented invocation.

Remaining single-quote traps, inventoried:
- click_js: 7 plan commands (steps 6, 20, 23, 29, 31, 34, 47) all carry single-quoted selectors; covered by the plan conversion, plus the driver reference example fix above.
- text/value/css fields: already double-quoted JSON with no single quotes in this task; the strong-form rule covers all fields anyway, because any single quote anywhere in the JSON breaks the shell split.
- type text values: no apostrophes in this task (Frank, Sinatra, frank.s@example.com, +1-555-0106, Vocal Architect, +1-555-9999, Kim); verified by the sweep.
- Plan prose apostrophes: none found outside JSON commands except the line 3 '<json>' pair.
- JS containing both quote types: only steps 21 and 55, handled above.
- A-composed JS is the biggest residual trap. The A brief step 7 gives the fixed final-read list in prose, not exact JSON, so A3 will compose its David, Spam Bot, and Frank evals live. One single-quoted selector there 500s the same way. Mitigations, both required: put the quoting rule plus a worked double-quoted DOM-read example in the A3 brief itself, not only in the driver reference; and give the A3 brief exact double-quoted JSON for the fixed final-read evals. The list is already frozen and identical for both arms, so exact commands add no deliberation content.
- Executor shell pipelines: A2 piped step.sh through sed/tee with its own quoting tricks. It worked, but every extra quoting layer is new trap surface. Rule: keep the step.sh call bare and log raw output; do not re-quote through sed.
- DRIVER DEAD labelling is misaligned and v2.2 must fix it. The briefs say two consecutive failures of any kind mean DRIVER DEAD; the design requires the coordinator's three liveness checks first and says driver-alive means timeout, not death. A1 and A2 declared DRIVER DEAD while the driver, geckodriver, and port 4451 were all alive, so those declarations were false under the design's own rule. Change the briefs: after two consecutive failures the executor stops and records STOPPED (DRIVER SUSPECT, coordinator to classify); it never labels DRIVER DEAD itself.

## Q3: Are A1/A2 void as instrument artifacts, budget reset, next A start A3, or is arm A exhausted? AMEND

Substance: GO for voiding. Text: AMEND, because the design needs four written amendments before the freeze.

Void A1 and A2 as instrument artifacts, reset the retry budget, label the next A start A3. Reasons:

1. Zero task steps ran in either attempt. No task measurement exists to lose, so voiding discards no data.
2. The cause sits in the frozen instrument, not in the executors, the browser, or the fixture: the brief's exact JS, delivered through the only invocation method the briefs authorize, cannot succeed as written. Both executors followed the brief exactly, and the defect hits both arms identically.
3. Design precedent already exists: the v2.1 note records that the failed 18:55:40 pre-flight consumed no retry budget because no classification was made, and the 19:06 driver death was treated as an infra fault, not an arm retry. The same principle applies here: a gate whose own JS is unexecutable is an instrument failure, not an arm outcome. The executor-tab diagnose is a gate by design (proceed only if VISIBLE; hidden means INVALID, not FAIL); a gate broken by its own wording cannot produce a FAIL.
4. The FAIL (incomplete) labels rest on a false premise: the design's DRIVER DEAD rule was not satisfied, because the driver was alive on all three liveness checks.
5. Exhaustion would kill the experiment over a deterministic, understood, fixable defect affecting both arms identically, and would violate "never compare one measured arm against nothing" in substance: B would have 500ed identically before the fix, so the comparison would be nothing against nothing.

The counter-reading, answered: "max 2 starts" and "post-start first run IS the result" were written for failures of the execution or the browser, presuming a valid instrument. They cannot sensibly consume budget on a command that cannot succeed as written. Restate the cap as max 2 VALID starts per arm; voided instrument-artifact starts do not count.

Required amendments in the v2.2 text:
- Log annotation, not rewrite: append correction entries to the execution log reclassifying A1 and A2 as VOID (instrument artifact), keeping the original FAIL lines visible.
- A3 is the first VALID A observation. The "second observation" restrictions (no win claimed from a second observation alone) attach to the voided A1/A2, not to A3.
- Replication pair rename. The design names the second pair (B2, A2), but A2 is already used by the voided attempt. Rename the pair to (B2, A4) under the general rule that start labels are per-arm sequential counters of all starts, voided or not, and labels are never reused.
- No-clean-win clause scope. The clause ("if either arm needed an infra retry, no clean win or loss is claimed") was written for browser-health confounds. A voided instrument artifact does not trigger it, but that must be written explicitly in v2.2, not assumed. If either VALID arm later needs a genuine infra retry or recovery-ladder intervention, the clause triggers then.
- The replication trigger is evaluated on the valid pair (A3, B1), not on voided attempts. The A2 brief is superseded; A3 needs its own brief file (report run-a3-report.md, ban on A1/A2 artifacts added to the A2 ban list).

## Q4: What else must change before any executor runs again? AMEND

All of the following are gates. No executor runs until they pass.

1. Live shell-path proof of the fixed full diagnose JS, byte-identical to the A3 and B briefs, through the executor's exact invocation (single-quoted step.sh call via bash -lc as codex wraps it), on a fresh live tab, requiring a full VISIBLE snapshot with countText "6". The existing reproduction proved only a short count read, not the full diagnose text.
2. Same shell-path live proof for the two hard plan evals (steps 21 and 55, escaped-inner-double form) returning the Frank notes value, plus one converted click_js, before B runs. The plan proof belongs before the re-freeze; the click_js proof belongs before B.
3. Sweep with output logged: zero single quotes inside any JSON command in the plan and in briefs A3 and B, and in the driver reference examples; all 64 plan JSON commands parse; every js value passes a JS syntax check; converted plan prose byte-identical except the JSON js strings (line 3 pair untouched).
4. A3 brief created and frozen with md5 recorded: fixed diagnose JS, quoting rule plus worked example, exact final-read JSON, HTTP 500 re-check rule, DRIVER SUSPECT wording, report run-a3-report.md, A1/A2 artifact ban.
5. Driver reference fixed: strong-form quoting rule, click_js example in double quotes, symptom plus recovery, return rule kept.
6. Preflight.py converted (all single-quoted JS strings) and re-proven by a fresh pre-flight pass before A3.
7. Design v2.2 re-freeze note carrying: the voiding, the cap restatement, A3 as first valid observation, the replication rename, the no-clean-win scope, and the new frozen md5s (plan, briefs A3 and B, driver reference, preflight, step.sh).
8. Log annotation entries for A1/A2 VOID, and out.log archived per attempt before A3. The reproduction 500 and "6" lines currently sit in out.log between the A2 and A3 ranges; session-boundary counting needs a clean archive.
9. Frozen md5 re-verification of all inputs before A3, as the design already requires before each arm.
10. Residual risk stated in the log: the 19:06 FIFO-holder death is still unproven. The driver has been alive since 19:08 and verified repeatedly, so it is not a blocker, but if it recurs before A3, stop and diagnose rather than pushing through.

## Q5: Verdict on the v2.2 re-freeze + A3. AMEND (conditional GO)

Do not re-freeze or launch A3 on the v2.2 proposal as written: the naive conversion breaks plan steps 21 and 55, the replication pair name collides with the used A2 label, and the DRIVER DEAD labelling is unaligned with the design. This is AMEND, not BLOCK: the fix direction is right, the root cause is proven, and the work to make it airtight is bounded and specified above. GO the moment the Q2 amendments are applied, the Q3 text amendments are written into v2.2, and the Q4 proofs (items 1 to 3 at minimum, items 4 to 9 attached) pass. No executor runs before that.

Per-question verdicts: Q1 GO, Q2 AMEND, Q3 AMEND, Q4 AMEND, Q5 AMEND (conditional GO).

## Notes for the reconciler

- The strongest alternative considered and rejected: fixing the transport instead of the payload (for example step.sh reading JSON from stdin or a file, which would let single quotes survive). It would preserve the plan md5 and protect A-composed JS, but it is an unproven invocation idiom through codex's bash -lc wrapping, while the payload fix was proven live by the reproduction returning "6" through the exact shell path. Record transport hardening as a future improvement for the next experiment, not as part of v2.2.
- The "transient" diagnosis of A1 at 19:22 is superseded by the reproduction; the log should say so in the annotation entry, since a future reader will otherwise trust the earlier line.
- No personal information is in this verdict. No em dash or en dash is used in this file.
