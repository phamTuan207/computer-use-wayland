# Independent Judge ruling: E1 arm A starts A1 and A2 (VOID or FAIL)

Judge: independent judge subagent (Judge-V), deciding alone from the evidence, with no knowledge of any other verdict. I did not read the council or redteam files or any reconciliation file. I worked paper only: no Zen driving, no executor launches, no live browser use, no live Marionette evals. The live leg of the evidence is the coordinator's recorded reproduction in out.log; I verified the shell, JSON, and JS layers myself on the VM, and read the laptop evidence files read-only.

Design applied: E1 comparison design FROZEN v2.1, commit 695efea, file improvements/worker-y8-e1-comparison-design.md. The design file in the working tree is unmodified from 695efea (md5 e1909423ee987b355783f22c7d804494, verified). Brief and driver-reference citations below are to their 695efea versions, which are the frozen v2.1 instrument the executors were briefed with. See the disclosure in section 6: the working tree now holds uncommitted post-hoc edits to those files. This ruling uses only the frozen versions.

## 1. Verdicts

- **A1: FAIL (incomplete).** Not VOID. The start counts. It is arm A's first observation, recorded as FAIL (incomplete): zero task steps run, final verification never reached.
- **A2: FAIL (incomplete).** Not VOID. The start counts. It is arm A's second observation, reported alongside A1, never a replacement. Identical failure at the identical step.
- **Start budget: exhausted.** Arm A used 2 of 2 starts (A1, A2). No reset is available under the design's text (section 5).
- **Next A start label: none exists.** There is no A3 under v2.1. "Second crash of any kind ends the arm as BLOCKED" applies: A1 plus A2 are two crashes. Arm A stands BLOCKED.
- **No-clean-win clause: TRIGGERED, yes.** Arm A needed an infra retry (A2), so no clean win or loss is claimed on either criterion. This holds independently of the VOID/FAIL call, and is doubly secured by arm A ending BLOCKED with no valid observation.
- **Executors exonerated.** Both executors followed the frozen briefs exactly. The failure is a defect in the frozen instrument, not executor error, not browser health, not the fixture, and not a driver death. No burden is attributable to either executor beyond the single error incident each that the instrument itself caused (section 4).

## 2. Design sentences relied on (exact quotes, design file line numbers)

All quotes are from improvements/worker-y8-e1-comparison-design.md at 695efea.

(a) Line 99: "Max 2 starts per arm. A second start, if any, is labelled A2 or B2 in every table and every verdict sentence. It never silently replaces A1 or B1."

(b) Line 101: "Post-start INVALID (crash, DRIVER DEAD, mid-run hidden body, or any stop after the executor's first driver command): the first started run IS the arm's result for accuracy. If the executor never reaches final verification, the arm is recorded as FAIL (incomplete), with the partial step reached, the failed checks so far, and the crash or timeout evidence. A re-run, if the coordinator judges it worth doing, is a second observation (A2/B2) reported alongside A1/B1, never a replacement. No accuracy or speed win may be claimed from a second observation alone; a win requires the first observations to support it, or requires both observations to agree."

(c) Line 102: "DRIVER DEAD: two consecutive step.sh failures of any kind (timeout or immediate error, including "fifo missing"), not only timeouts. Before declaring DRIVER DEAD, the coordinator must check the driver process is alive, the geckodriver process is alive, and port 4451 answers, and must log those three checks. If the driver is alive, the event is a timeout, not a death, and the arm continues or fails on its own evidence."

(d) Line 103: "MID-RUN HIDDEN BODY: if the executor tab goes hidden mid-run (executor reports body hidden on its own tab, or two consecutive type/click steps fail and a diagnose on the executor tab shows hidden), the executor stops, the coordinator diagnoses the executor tab and classifies it, and the arm is INVALID (INFRA), not a FAIL. It is re-run once from scratch under the single retry budget. The partial run is logged, never counted."

(e) Line 106: "Second crash of any kind ends the arm as BLOCKED. Before any re-run, inventory Zen tabs and close only the crashed run's tab (or record that it is already gone)."

(f) Line 109: "If either arm needed an infra retry or any recovery-ladder intervention, no clean win or loss is claimed on either criterion. The result is reported as an observed difference, confounded by browser health, with the pre-flight evidence attached."

(g) Line 100: "Pre-start INFRA-BLOCKED (pre-flight diagnose fails before the executor issues its first driver command, zero executor steps attempted): the arm does not start."

(h) Line 93 (executor-tab diagnose): "If the executor tab is hidden, the executor stops immediately, records INFRA-SUSPECT with the read values, and the arm is INVALID (INFRA), not a FAIL."

(i) Line 104: "FIXTURE_FAILURE (pre-flight exit 3, fixture HTTP error, or missing #contacts-count): neither INFRA-BLOCKED nor a FAIL. It stops the run. The coordinator re-verifies the fixture file and the HTTP server, fixes or restores them, then re-runs pre-flight from scratch. It does not consume the INFRA retry."

(j) Line 13: "Any change after this freeze requires a new version number and a re-freeze note, never a silent edit."

## 3. Evidence chain

### 3.1 The coordinator's root-cause claim is verified, not taken on trust

Claim: the briefs' diagnose JS contains document.querySelector('#contacts-count') with single quotes; the executors passed the JSON to step.sh single-quoted at the shell; the shell stripped the quotes; Marionette received a JS SyntaxError and returned HTTP 500.

I verified each link myself:

1. **Frozen briefs contain the single-quoted selector and no quoting guidance.** At 695efea, brief A line 25 and brief A2 line 25 and brief B line 29 give the exact diagnose JS with `document.querySelector('#contacts-count')`. At 695efea, the word "single-quote" occurs 0 times in brief A and 0 times in the driver reference, so the frozen instrument gave the executors no quoting guidance. Frozen md5s match the execution log: brief A 2741a1a1de8b34e9ca2371d725432438, brief B 7345f969d5de7516ca40a3505a204829, driver reference 4775a5710724bea3b64393be16522fdc. The driver reference (frozen) line 7 states the invocation form: `/tmp/e1/step.sh '<json>'`.
2. **The executors used exactly that form.** Laptop /tmp/e1/events-a.jsonl lines 22-23 (item_10, diagnose) and 26-27 (item_12, retry), and /tmp/e1/events-a2.jsonl lines 26-29 (items 12 and 13), show the step.sh calls with the single-quoted JSON containing `'#contacts-count'`. Both executors read only the allowed files (spec, fixture, driver reference); A2 read zero forbidden paths (grep for run-a-report, events-a.jsonl, out.log in events-a2.jsonl returns 0).
3. **VM shell reproduction (my own test, 19:47 +07).** I ran the brief's exact command through `bash -lc` against a stub step.sh that records $1. Result: ARG_COUNT=1, and $1 is valid JSON whose js field contains `querySelector(#contacts-count)` with the quotes stripped. The `#` is literal because it sits mid-word (the single-quoted portion and the following unquoted characters form one shell word), so the JSON stays intact while the JS loses its quotes. `python3 json.loads` on the received $1 parses cleanly, cmd is "eval", the unquoted selector is present, the quoted selector is absent.
4. **VM JS check (my own test, 19:47 +07).** `node --check` on the mangled JS exits 1 with SyntaxError; on the corrected JS (quotes restored) exits 0. A script that fails to parse is rejected by Marionette as HTTP 500.
5. **The double-quote variant survives the same shell path (my own test, 19:48 +07).** Passing the identical eval with `\"#contacts-count\"` in the JSON through the same single-quoted shell invocation delivers js containing `querySelector("#contacts-count")` intact. This is the same contrast as the coordinator's live reproduction.
6. **The 500s in out.log match a Marionette script rejection, not a transport failure.** Laptop /tmp/e1/out.log lines 8-9 (A1, 2 ms and 4 ms) and lines 22-23 (A2, 3 ms and 3 ms) read `{"ok": false, "error": "HTTP Error 500: Internal Server Error"}`. In laptop /tmp/e1/hand_drive_e1.py, that exact string is produced only by the `except` handler around the Marionette POST (urllib HTTPError); a malformed JSON line would instead print `{"ok": false, "error": "bad json: ..."}`. So the JSON arrived intact and Marionette rejected the script. The 2-4 ms timing is consistent with parse-time rejection, not with a browser execution or a timeout.
7. **The coordinator's live reproduction is in out.log, lines 24-25.** On A2's tab, the executor's exact quoting returns HTTP 500 (3 ms); the identical JS with double quotes returns "6" (2 ms). This is the coordinator's recorded live leg, and it agrees exactly with my independent VM reproduction at every link.
8. **A2's own report records the mangled argument.** Laptop /tmp/e1/run-a2-report.md, final line, records `ARGV1_was:` with the received JSON containing `querySelector(#contacts-count)`, quotes stripped. This is the executor's own record, independent of the coordinator.
9. **Why pre-flight passed.** Laptop /tmp/e1/worker-y8-preflight.py calls step.sh via `subprocess.run([STEP, json.dumps(cmd)], ...)` with a list argv and no shell, so its quotes survive; and the coordinator's own diagnosis used double quotes. Pre-flight and the executors therefore tested different code paths. Pre-flight A #3 and pre-flight A2 both returned VISIBLE with countText "6" (preflight-a.json and preflight-a2.json, verdict VISIBLE, no intervention). The instrument was never validated end to end through the executor's shell path.

Conclusion on cause: proven. The failure is a deterministic defect in the frozen instrument (brief JS plus invocation form), not executor error, not browser health, not the fixture, not the driver.

### 3.2 What each executor actually did

- A1 (laptop /tmp/e1/run-a-report.md; out.log lines 6-9): 4 driver commands, new_session ok (5ee1bf71, 4 ms), new_tab ok (f340da5e, 1101 ms), diagnose eval HTTP 500 (2 ms), diagnose retry HTTP 500 (4 ms). No task step ran. Final evidence: "Visibility diagnosis did not return JSON. Visibility is UNVERIFIED. No contact task steps were run." Coordinator wall 151 s (19:17:04 to 19:19:35, execution log line 50).
- A2 (laptop /tmp/e1/run-a2-report.md; out.log lines 20-23): 4 driver commands, new_session ok (a18e76dc, 5 ms), new_tab ok (c63f8986, 1128 ms), diagnose eval HTTP 500 (3 ms), diagnose retry HTTP 500 (3 ms). No task step ran. Final evidence: none; "Final fixed-read list: not run because DRIVER DEAD occurred before the visibility gate passed."
- A2 was a lawful second observation: fresh codex process, pre-flight A2 VISIBLE (19:24:48), brief A2 md5 858705772c5562a78ffc14a2d0035234 matches the repo, zero forbidden-path reads. The coordinator judged the re-run worth doing (execution log line 52), which sentence (b) permits.

### 3.3 The rival classifications are excluded by the evidence

- **Not a driver death.** Sentence (c) requires the three liveness checks before accepting DRIVER DEAD. The coordinator logged them at 19:22:40 (execution log line 50): driver PID 274644 ALIVE, geckodriver PID 274657 ALIVE, port 4451 LISTEN. Per sentence (c), "the event is a timeout, not a death, and the arm continues or fails on its own evidence." The executors had already stopped as their briefs required, so the arm fails on its own evidence. The executors' "DRIVER DEAD" label was procedurally correct under the frozen briefs, but the design reclassifies the event. Either way the outcome is failure, not voiding.
- **Not a hidden body.** The coordinator's diagnosis on A1's own tab (out.log lines 10-12, 19:23:17) returned the full snapshot, VISIBLE, countText "6", readyState complete, fixture URL. Pre-flights A #3 and A2 were VISIBLE. Sentences (h) and (d) both trigger only on a hidden tab; the tab was visible.
- **Not a fixture failure.** Fixture HTTP 200 throughout; countText "6" present in every successful diagnose. Sentence (i) does not trigger.
- **Not pre-start.** Both executors issued driver commands (new_session and new_tab succeeded) before the failing evals. Sentence (g) requires "zero executor steps attempted"; it does not apply. Both pre-flights passed in any case.
- **The plan carries the same trap.** Laptop /tmp/e1/plan-test-05.md (md5 a7b5646b2bf081386bb7bcea0563ad5a, verified, matches the frozen value) contains 45 occurrences of `querySelector('#` and 6 of `querySelector('.`, across 21 eval lines and 11 click_js lines. A B executor passing those commands single-quoted through the shell would meet the same 500s. This corroborates that the defect is systemic to the frozen instrument, and it is why no B start may run on the frozen v2.1 files without a versioned re-freeze under sentence (j).

## 4. Why VOID fails under the design's text

VOID would require a design provision whose trigger conditions are satisfied. I tested each one against the verified facts:

- Pre-start INFRA-BLOCKED (g): trigger false, executors issued driver commands.
- Executor-tab diagnose INVALID (h): trigger false, tab visible.
- Mid-run hidden body INVALID, "logged, never counted" (d): trigger false on both prongs (failures were evals, not type/click; the executor-tab diagnose showed VISIBLE, not hidden).
- Fixture failure, "does not consume the INFRA retry" (i): trigger false, fixture fine.
- No other sentence in the design voids a started run. In particular, there is no sentence that voids a post-start stop because its cause was the instrument, and no sentence that resets a start budget.

Against that, the post-start rule (b) applies by its plain catch-all: "any stop after the executor's first driver command". Both A1 and A2 stopped after their first driver command. The sentence then directs the consequence without exception for cause: "the first started run IS the arm's result for accuracy. If the executor never reaches final verification, the arm is recorded as FAIL (incomplete), with the partial step reached, the failed checks so far, and the crash or timeout evidence." Neither executor reached final verification. So each is FAIL (incomplete), with partial step reached: the diagnose step (step 1 precheck); failed checks so far: none; evidence: two HTTP 500s each.

Two further points confirm this reading. First, sentence (e) counts crashes "of any kind", expressly regardless of cause; the quoting cause does not exempt the second crash. Second, the design's harshness here is deliberate and consistent: the v2.1 re-freeze note shows the design's own remedy for an instrument bug is to fix and re-freeze BEFORE arms run (that is what happened for the bare-IIFE bug, caught pre-start, which consumed no budget). The quoting bug is the same kind of bug in the same diagnose step, but it was first detectable only post-start, because the pre-flight path structurally cannot exhibit it (subprocess argv, no shell). That is a gap in the design's gate, and it is unfortunate, but the design's text assigns post-start stops to FAIL, and this judge's mandate is to apply the design's own text, not to repair the design. The repair path the design provides is a versioned re-freeze under sentence (j) before any further arm runs.

Burden note, for the record: under the design's category table, one {"ok": false} result plus all recovery it triggered is ONE error incident. Each arm therefore carries one error incident (the first 500 plus its retry), zero check failures, zero misclicks. No executor error is attributable to either executor, because each followed the frozen brief exactly and the command could not have succeeded as written.

## 5. Budget, label, and no-clean-win

- **Budget:** "Max 2 starts per arm" (a). A1 and A2 are the two starts. The budget is exhausted. No sentence authorizes a reset, and the coordinator's log floats "retry budget reset" only as an open question, not as a design rule. A ruling of VOID plus reset would invent a rule the design does not contain.
- **Next label:** none. Sentence (e), "Second crash of any kind ends the arm as BLOCKED", applies: A1 and A2 are two crashes. Arm A stands BLOCKED. There is no A3 under v2.1. Any future A attempt would need a versioned re-freeze (v2.2 or later) under sentence (j) and a fresh budget decision by the coordinator and council; this ruling does not authorize one.
- **No-clean-win:** TRIGGERED. Sentence (f) triggers when "either arm needed an infra retry". A2 was a retry granted after an infra-suspect DRIVER DEAD stop, under the single retry budget (execution log line 52, which itself records "because A needed an infra retry, no clean win/loss is claimed"). No clean win or loss is claimed on either criterion. Independently, arm A ending BLOCKED with no valid observation also bars any clean win or loss.
- **Comparison status:** arm A stands BLOCKED with two FAIL (incomplete) observations at zero task steps. No comparative verdict can be drawn from A. The design's "Never compare one measured arm against nothing" bars any comparative verdict from a lone B run, should B run. The replication trigger ("either arm is flagged or invalid") is engaged, since A1 and A2 fall under the design's "Post-start INVALID" heading.

## 6. Disclosure: working-tree state at ruling time

While I was judging, the working tree changed under me. My first reads (19:45 +07) captured the frozen v2.1 text. A later grep (about 19:52 +07) showed uncommitted modifications to improvements/worker-y8-executor-a-brief.md, improvements/worker-y8-executor-b-brief.md, improvements/worker-y8-driver-reference.md, and improvements/worker-y8-preflight.py, adding quoting guidance and changing the DRIVER DEAD rule, plus an untracked improvements/worker-y8-executor-a3-brief.md. I verified by git show that the 695efea versions are the frozen v2.1 text I relied on (brief A md5 2741a1a1de8b34e9ca2371d725432438, driver reference md5 4775a5710724bea3b64393be16522fdc, design md5 e1909423ee987b355783f22c7d804494, all matching). I did not read the uncommitted edits as authority, and I did not read the A3 brief, the council files, the redteam file, or any reconciliation file. This ruling judges A1 and A2 as run under the frozen v2.1 instrument, and the post-hoc edits change nothing about it.

## 7. What would falsify this ruling

- If a design sentence I missed voids a post-start stop whose cause is a proven instrument defect, or authorizes a start-budget reset, that sentence would overturn the FAIL and BLOCKED consequences. I searched the design for void, invalid, retry, and budget provisions; the only void-like consequences are sentences (d), (g), (h), and (i), and none of their triggers is satisfied here.
- If the executor tabs had in fact been hidden (not VISIBLE), sentence (h) or (d) would make the arm INVALID (INFRA), not FAIL. The evidence against this is the coordinator's full VISIBLE snapshot on A1's tab (out.log lines 10-12) and two VISIBLE pre-flights.
- If the driver or geckodriver had in fact been dead, the DRIVER DEAD classification would stand as a death rather than a timeout, but the post-start consequence would still be FAIL (incomplete) under sentence (b); only the cause label would change.
- If the executors had not followed the briefs (for example, if they had invented their own JS or used double quotes and still 500'd), the exoneration in section 1 would fail, though the FAIL consequence under sentence (b) would still stand. The event streams show exact compliance.
- If my VM shell reproduction were wrong (if the single quotes had survived the shell), the root-cause proof in section 3.1 would fail. It is reproducible: the stub test in /tmp/judge-void/stub-step.sh with the brief's exact command, plus node --check on the received JS.

## 8. Timing log (Asia/Ho_Chi_Minh, wall clock)

- 19:45:11: task start. Read the design, execution log, both A briefs, the B brief, the driver reference, and preflight.py in full.
- 19:45-19:46: verified laptop /tmp/e1 listing and md5s (plan a7b5646b2bf081386bb7bcea0563ad5a matches frozen; step.sh b4eaa8736a7db7b6ba7ab9188ab3364f).
- 19:46-19:47: read out.log (27 lines), repro-quote.sh, step.sh, hand_drive_e1.py, preflight-a.json, preflight-a2.json.
- 19:47: read events-a.jsonl and events-a2.jsonl diagnose commands (items 10, 12; items 12, 13).
- 19:47-19:48: VM verification. Shell stub test: quotes stripped, JSON intact, unquoted selector present. node --check: mangled JS SyntaxError exit 1, correct JS exit 0. Double-quote variant survives intact.
- 19:49: read run-a-report.md and run-a2-report.md (4 commands each, zero task steps).
- 19:49: verified the plan file carries the same trap (45 querySelector('#, 6 querySelector('., 21 eval lines, 11 click_js lines).
- 19:50: verified A2 read zero forbidden paths; both executors read only the 3 allowed files.
- 19:50: verified design sentences by grep with line numbers; verified frozen 695efea md5s and the absence of quoting guidance in the frozen briefs and driver reference; recorded the working-tree disclosure.
- 19:50: ruling written.
