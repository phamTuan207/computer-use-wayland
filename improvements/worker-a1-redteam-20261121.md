# A1 narrow pilot plan: redteam attack (2026-11-21)

- Target: improvements/worker-a1-pilot-plan.md (DRAFT, 2026-11-21, Worker A1)
- Spec checked: improvements/working-structure-redesign-20261121.md sections 6 and 9 (commit fb00973, owner approved 2026-11-21 18:17)
- Design checked: improvements/a1-code-exec-dom-design.md (2026-11-19)
- Measurement checked: improvements/speed-proto-pick4-summary.md (2026-11-19)
- Redteam: independent attack worker. No live arm has run. No speedup is claimed here.
- Method: every load-bearing number re-checked against its cited source file in the repo. Anything I could not verify is labeled UNVERIFIED, not stated as fact.
- Verdict up front: the design as written does NOT survive. 7 attacks KILL it as written (A1, A2, A3, A4, A5, A8, B1). All 7 are fixable with specific amendments, none requires abandoning the pilot. The fixes must land BEFORE any live arm runs, because 4 of the 7 (A1, A2, A3, A5) are unfixable after the fact: once the runs exist, no re-analysis can remove off-clock authorship, order learning, expectancy, or hidden in-program recovery from the numbers.

## 0. What the plan gets right (so the attacks stay honest)

- The question is correctly narrowed to one lever (batching per observation), and Case A holds the DOM interaction path constant across arms, which is the only clean comparison in the plan.
- The GO bar is pre-registered and conjunctive (all conditions, both cases), and section 10 states the pilot does not prove Zen transfer.
- The preflight two-layer gate exists at all, which most designs skip.
- The plan itself flags its own open questions 1-5; attacks A6, A7, and B2 below are sharper versions of questions 1, 2, and 5, not new discoveries.

## 1. FALSE GO attacks (code-exec wins on paper but not in reality)

### A1. The Case B program can be authored off-clock, and the Case A program already exists in the repo (HIGH, KILLS as written)

- Evidence: the plan (section 3) says the Case A program is "the D1 program from the design file section 3, adapted only for the frozen fixture path". That program is printed in full in improvements/a1-code-exec-dom-design.md section 3. The executor does not compose it live; it copies it and changes a path. For Case B, no draft program exists, but nothing in the plan forbids the executor from writing, testing, and debugging the program BEFORE the timed window starts, or forbids Worker A1 from putting a draft program in the runbook (which does not exist yet, see A8). The timed window is "task start (session start submit) to verified end state" (section 3), so any think spent composing the program before session start is invisible to every metric. The plan measures "think-before-first-program-call" only inside the run.
- Why it is fatal: the pilot claims to test "one observation yields many actions" as a live model loop. A pre-written program tested against a frozen fixture is a script, not a loop. A script beating a live loop proves nothing about the loop; it proves scripts are fast, which was never in doubt (Worker U's scripted f01 run took 3,604 ms, see N2). The entire wall saving could be off-clock authorship.
- It also breaks the comparison asymmetrically: the STEP arm cannot pre-compose anything, because each of its steps needs a live observation. Only CODE gets a free prep phase.
- Amendment (required): (a) the runbook must contain NO program text, no pseudocode, and no ref lists; (b) the executor must compose each program live inside the timed run, with the session started BEFORE any program text is written; (c) the executor's transcript must show the program's first draft appearing after session start; (d) Worker A1 must state in the runbook that any program text written before session start voids the run. A weaker version (allow a draft but time the drafting) does not fix it, because drafting time outside the run is still unmeasured.

### A2. Fixed order STEP-first plus same-executor, same-task pairing hands CODE a learning effect (HIGH, KILLS as written)

- Evidence: plan section 4 fixes the order per case as STEP, CODE, STEP, CODE, STEP, CODE, and section 3 uses ONE executor for both arms. The plan's justification is that "any first-run warmup cost lands on the control arm, conservative against the hypothesis".
- Why the justification is wrong: warmup is not the only order effect, and it is not the largest one. The executor that just ran STEP on Case B has already learned the fixture's non-obvious interaction model (cells are selected by BUTTONS, typed values go through the #typed input plus "type" and "Enter" buttons, direct td clicks select nothing; see A4), the exact formula strings, the COUNT trap, and the expected end state. The CODE run then re-uses that learning. The same holds for Case A (fixture layout, button ref, expected string). Learning helps the second arm on every pair, and the second arm is always CODE. Browser and server warm caches point the same way (second run reuses a warm Chromium profile and a warm HTTP server).
- The "conservative" claim only covers first-run warmup, which is small, and ignores within-pair learning, which is large. The bias points directly at a false GO.
- Amendment (required): randomize the start arm per pair (coin flip per case, recorded in the sealed manifest before the pair runs), so learning effects split across arms instead of always favoring CODE. If the coordinator insists on a fixed order for operational simplicity, the pilot must use TWO executors (one per arm, each seeing only its own arm) instead of one executor doing both. Either fix works; the current fixed-order-plus-one-executor combination does not.

### A3. The executor cannot be blinded: it knows the hypothesis and can read the plan (HIGH, KILLS as written)

- Evidence: plan section 9 requires the executor to be "briefed from the runbook only, no knowledge of the pilot's numbers or the hypothesis direction beyond the arm procedure". But the runbook does not exist (A8), the plan itself sits in the repo at improvements/worker-a1-pilot-plan.md, and the executor is a Muse subagent with repo access. Nothing prevents it from reading the plan, the design file, or this redteam report. Worse, the arm procedures themselves reveal the hypothesis: an executor told to run a "code-exec program" arm and a "step-by-step" arm knows which one is supposed to win.
- Why it matters: expectancy effects are the classic false-GO engine. An executor that believes CODE should win will compose the program carefully, retry patiently inside the program, and on STEP will follow the spec woodenly, re-observe after every step, and never reuse an address or skip a redundant observe (contrast Pick 4 arm 2 P2, which skipped the windows call by reusing an address and was faster for it). A single executor running both arms can also, without meaning to, try harder on the arm it finds interesting.
- Amendment (required): split the executor role. Two executors, each briefed ONLY on its own arm's procedure, each told its arm is the one under test, neither given the plan, the design file, or the other arm's brief. If two executors are operationally impossible, the minimum is: the runbook each executor receives must not name the other arm, must not state the hypothesis direction, and must not cite the pilot's numbers; and the executor's repo access during runs must exclude improvements/ (enforced by the spawn brief, verified by the transcript showing no reads of the plan). The current section 9 sentence asserts blindness without any mechanism. An assertion is not a control.

### A4. Case B: the STEP interaction path is unspecified, and the fixture punishes the obvious path (HIGH, KILLS as written)

- Evidence: plan section 3 specifies the STEP arm for Case A precisely (windows, observe, navigate, observe, tabs, DOM observe, DOM act click, DOM assert, close). For Case B it says only "the 26 spec steps, one model turn per action, re-observing after each batch of edits as the spec requires". It never says whether STEP Case B uses DOM observe/act per step or desktop screenshots plus mouse clicks.
- Why it matters: the f01 fixture's interaction model is a trap for the obvious path. Cells are plain td elements with NO click handler (tests/realistic/fcc-k/fixtures/test-01-spreadsheet.html lines 43-52). Clicking a td directly selects nothing; Worker U's scripted run records exactly this as "TRAP: click td#a2 directly" followed by "check td click selected nothing: False". The working path is: click a BUTTON labeled A2/B2/... to select the cell, fill the #typed input, click the "type" button, click the "Enter" button to evaluate. That is 4 DOM actions per cell value, about 80 actions for the whole task (see A9).
- If STEP Case B uses mouse clicks on cells (the literal reading of spec steps like "Click cell A2 and type 2026-11-16"), it hits the trap on the first data row and fails or burns recovery steps discovering the button dance. If CODE Case B uses DOM refs to click the buttons, it bypasses the trap entirely. The arms would then differ in TWO levers (batching AND interaction path), and a CODE win would prove DOM-refs beat mouse clicks, not that batching beats step-by-step. The plan's section 1 promise ("Nothing else changes between arms: same fixture, same browser, same task, same executor, same checker") would be false for the hard case.
- Amendment (required): freeze in the runbook, before any run, that STEP Case B uses dom_observe/dom_act per step with the same refs the CODE program uses (click button by ref, fill #typed by ref, click type/Enter by ref), one model turn per action. The spec's "click cell" language must be translated to the button path explicitly, identically for both arms. If the coordinator instead wants STEP to use mouse clicks, that is a different experiment (batching AND modality) and the GO bar must be re-registered as such.

### A5. Recovery steps are invisible inside a program, so GO condition 3 is biased toward CODE by construction (HIGH, KILLS condition 3 as written)

- Evidence: plan section 5 condition 3 requires "Recovery steps (CODE) not higher than recovery steps (STEP)". Section 8 lists recovery steps as a per-run field "computed by script from the run log, never self-reported", but the plan never defines what counts as a recovery step (re-observe? retry click? re-submitted program? in-program branch taken?).
- Why it is fatal: a STEP retry is a visible model tool call in the log. A CODE retry is invisible: the design file section 4 shows the program re-observing and re-issuing a click on failure with zero model calls ("The branch-and-retry above costs 0 model calls. That is the whole point of A1"). The program can retry 5 times, re-observe 3 times, and take the fix-the-formula branch, and the run log still shows 1 program call and 0 recovery steps. Comparing visible STEP recoveries against invisible CODE recoveries is not a comparison; CODE wins condition 3 automatically, even on a run where the program thrashed internally.
- Amendment (required): define recovery operationally BEFORE any run, and count it the same way in both arms: (a) in the CODE arm, every in-program retry, re-observe, and branch-to-fix counts as one recovery step, extracted from the program's returned trace/output (the program must return its retry count; a program that swallows its retries fails the run); (b) in the STEP arm, every repeated action after a failed or refused action counts as one. If the harness cannot surface in-program retries, condition 3 must be dropped as a GO condition and replaced with end-state correctness plus wall only, stated plainly. What cannot be done is to keep condition 3 as written, because it is a free pass for CODE.

### A6. The blinded checker can infer the arm from the run log (MEDIUM, fixable)

- Evidence: plan section 6 says the checker "reads ONLY the run directory" and "does not know the arm", and section 8 says the checker outputs PASS/FAIL plus the six metrics plus per-run fields "from the DOM dump and the timed log", including "program calls (CODE arm), program chars (CODE arm)".
- Why it matters: any run log containing a program call, program chars, or a code-exec op is CODE; any log with 40+ observe/act turns is STEP. Tool-call counts alone separate the arms (CODE about 2-5 calls, STEP about 40+). The op sequence, elapsed pattern, and per-run fields all leak the arm. A script checker has no expectancy bias, so leaking the arm does not bias a purely DOM-based PASS/FAIL. But the plan has the same script computing recovery steps, refusals, and metrics from the timed log (see A5), and any future human review of checker output inherits the leak. The blinding claim is also overstated in a second way: the sealed manifest is a plain file (runs/manifest-sealed.jsonl) that anyone with repo access can read; "the checker never opens it" is an honor rule, not an enforcement.
- Amendment: (a) split the checker into two stages: stage 1 reads ONLY the DOM dump and outputs PASS/FAIL; stage 2 (run after unblinding, by Worker A1) computes metrics from the timed log; (b) remove program-call/program-char fields from the run log the checker sees, or move them to the sealed manifest; (c) state plainly that the manifest seal is honor-system and that the actual blinding guarantee is "the PASS/FAIL function takes no arm input", verified by code review of check_run.py.

### A7. n=3, median of 3, and no rule for flakes, voids, or blocked starts (HIGH, fixable only with a re-registered run rule)

- Evidence: plan section 4 sets n=3 per arm per case; section 5 takes the median. No section defines what counts as a run, what happens on a broker-blocked start, a harness flake, or a session death, or whether a failed run is retried, voided, or counted.
- Why it matters: Pick 4 arm-1 run 1 went 0/4 on broker contention alone (summary section 2, run 1). Pick 1 P3/P4 attempt 1 failed identically on a harness flake (screen-changed preflight refusal, global mean 3.56 vs threshold 3.0) and only passed on retry with the identical program. With n=3, one flake run IS the median if it lands in the middle, and one blocked start counted as a fail flips pass rate by 33 points (2/3 vs 3/3). The plan's "report ALL runs" principle (from the redesign) is cited nowhere in the pilot plan, so an executor that quietly retries a blocked start has no rule telling it not to.
- Amendment (required before any run): (a) define VOID vs FAIL in the runbook: broker-blocked start, session death before first task action, and harness preflight flake with zero task effects are VOID (re-run, recorded as void with evidence); a wrong end state or an exceeded program budget is FAIL (counted); (b) cap voids per arm per case at 1, and if voids exceed the cap the case is inconclusive, not GO; (c) report the range (min/max) alongside every median, so a median built on one flake is visible. If n=3 stays, the verdict must be labeled "pilot signal, n=3" in every downstream citation, and Exp1 must re-confirm with a larger n before any land decision.

### A8. Three load-bearing artifacts referenced by the plan do not exist, and the plan itself is uncommitted (HIGH, KILLS as written)

- Evidence: plan section 3 cites tests/realistic/a1-pilot/runbook.md; section 6 cites tests/realistic/a1-pilot/check_run.py; section 8 cites tests/realistic/a1-pilot/run-log-schema.md. On 2026-11-21 I listed tests/realistic/a1-pilot/ and found only fixtures/README.md and fixtures/pick4-fixture.html. All three cited paths return "No such file". The plan file itself is untracked (git status shows ?? improvements/worker-a1-pilot-plan.md), as is the whole tests/realistic/a1-pilot/ directory.
- Why it matters: the runbook is the instrument that controls executor variance (A3), the interaction path (A4), and the void/fail rule (A7). The checker is the instrument that decides PASS/FAIL (A6). The schema is the instrument that defines the metrics (A5). A plan whose three instruments do not exist cannot be executed as written; any run done now would improvise all three under time pressure, which is exactly how questioned fast results are produced. It also violates the standing rule "small commits push as you go": the design under debate is not on the branch for the council to read.
- Amendment (required): write all three artifacts, have them reviewed by someone other than Worker A1 (see C1), commit the plan plus the artifacts plus this redteam report, and push before any live arm. No live arm starts until the runbook, checker, and schema are frozen on todolist-push.

### A9. The 3-program cap and the 8192-char cap are untested for Case B, and Case B needs about 80 DOM actions (HIGH, fixable)

- Evidence: plan section 3 caps each program at 8192 chars (verified: scripts/code_exec.py line 92, MAX_PROGRAM_CHARS = 8192) and at most 3 program calls per run. The design file says the D1 program is "about 900 chars". No draft Case B program exists and no char estimate is given anywhere.
- Why it matters: from the fixture's interaction model (A4), each of the roughly 20 cell values needs select-button click plus fill #typed plus type-button click plus Enter-button click, about 4 actions per value, plus 3 formula reads, a diagnosis branch, a COUNTA fix, and final reads. That is about 80 dom_act actions. One dom_act call takes at most 32 actions (design file section 2), so the program needs at least 3 dom_act calls inside it. Each action dict is roughly 30-100 chars; 80 actions plus ref-lookup code (find each of about 25 buttons by name in the snapshot) plus branching plausibly totals 4,000-8,000 chars, right against the 8192 cap. This is an estimate, not a measurement; the honest statement is that nobody knows whether it fits.
- If it does not fit, the executor must split across program calls, and each split is a fresh model turn with fresh think and a fresh observation. The 3-call cap then stops measuring batching and starts measuring the cap. Worse, if the executor discovers the overflow mid-run, the run fails for a cap reason, not a lever reason, and under A7's missing void rule that failure would count against CODE.
- Amendment (required): draft the Case B program NOW, on the VM with no browser, measure its exact char count, and publish it with the plan. If it fits in 8192 with margin (at least 15 percent headroom), keep the cap. If it busts the cap, re-register: either raise the cap with a stated reason (and say why the new cap is principled, not fitted to the program) or split Case B into two registered sub-programs. Do not discover the answer during a timed run.

### A10. A Chromium GO gates Zen work, and the DOM lever is confounded with the batching lever on the transfer path (MEDIUM, fixable)

- Evidence: plan section 3 uses managed Chromium via CDP, explicitly NOT Zen, and section 10 states the pilot "does not prove batching wins on Zen". But section 6 of the redesign (the approved spec) says on GO, "run Council C Exp1 as the confirmatory run, then Exp2", with no Zen-transfer condition anywhere in the chain.
- Why it matters: the user's actual goal is Muses driving THE USER'S Zen. On Chromium, both arms use DOM ops (Case A) or at least a DOM-capable path; on Zen there is no CDP DOM path, there is a documented hidden-body incident (21/11 17:52) and a BiDi click false-ok mode. If CODE's win on Chromium comes mostly from DOM ops being instant and screenshot-free (a read-path win, not a batching win), the win evaporates on Zen where every observation is a screenshot and every click is a real mouse move. The pilot would then produce a GO that launches Exp1/Exp2 on a lever that does not transfer.
- Amendment: add a transfer condition to the GO: a pilot GO authorizes Exp1 design work only, and Exp1 RUNS start only after a Zen-transfer probe (one Case A-shaped task on Zen, both arms, reported plainly even if it fails). Alternatively, keep the Chromium GO but rename the verdict in every downstream citation to "Chromium-only pilot GO", never a bare GO. The plan already says this in section 10; the gap is that the redesign's section 6 GO chain does not carry the qualifier forward.

## 2. FALSE NO-GO attacks (batching really helps but the pilot says no)

### B1. The 30 percent bar is unreachable on Case A given D1's own wall decomposition (HIGH, KILLS the bar as written)

- Evidence: D1 (summary section 3) took 293.401s wall. Its think splits sum to about 290s: browser-start 5.9, windows 16.4, tabs 6.9, desktop-observe 7.8, navigate-act 21.5, browser-observe 7.5, browser-act 13.2, close-observe 45.8, close-act 14.7, windows-after-close 11.2, finish 139.2. The "core DOM loop" the pilot is testing (browser-observe plus browser-act) is 20.7s, about 7 percent of the wall. The summary itself says "The 139.2s finish think is executor overhead, not Pick 4."
- Why it is fatal to the bar: the plan's wall window is "task start to verified end state" with no rule excluding finish-confirmation think and no bound on it. If the pilot executor reproduces anything like D1's finish behavior, both arms carry 100s+ of fixed overhead (browser start, navigation, close, finish) that batching cannot touch. Cutting the 20.7s DOM loop to zero saves 7 percent of a 293s wall. To clear a 30 percent median wall cut on Case A, CODE would need to save about 88s, four times the entire DOM loop, which means the win would have to come from navigation, close, and finish turns, not from batching. A pilot that cannot pass even when the lever works perfectly is a false-NO-GO machine.
- Note the asymmetry: this does not make Case A easy to pass; it makes it nearly impossible to pass for the reason the pilot claims to test. The honest reading of D1 is that finish think dominates and must be controlled before any wall bar is meaningful.
- Amendment (required): either (a) define wall as task start to verified end state EXCLUDING finish-confirmation think (the Pick 1 re-measure used "wall excl. dwell" and excluded finish-confirmation think; adopt that definition explicitly), and bound finish to one confirmation turn in the runbook; or (b) set per-case bars from a measured decomposition: run a dry-run STEP Case A once, decompose its wall, and set the Case A bar to a fraction of the batchable portion, not of the total wall. Do not keep a 30 percent of total wall bar on a case where the batchable portion is 7 percent.

### B2. n=3 with unknown variance and a 30 percent bar has unknown power, and no variance data exists to justify it (HIGH, fixable)

- Evidence: plan section 4 (n=3) and section 5 (30 percent bar). No pilot variance data exists anywhere: Pick 4's clean pair differed by 5 percent while its raw mean differed by 53 percent, both on n=1 per task per arm with different tasks; the same arm's walls ranged from 43.6s to 312.5s across tasks (summary section 2). Within-task, across-run variance for these exact cases is UNMEASURED.
- Why it matters: with unknown variance, a 30 percent median difference on n=3 can be noise in either direction (see A7 for the false-GO side). On the false-NO-GO side specifically: if the STEP arm happens to draw a fast run (executor reuses an address, skips a redundant observe, as Pick 4 arm 2 P2 did) and CODE draws one slow run (a stale-snapshot retry, a preflight flake), the median misses 30 percent even if batching truly saves 40 percent on a typical run. The plan's own open question 1 asks exactly this ("does the small n make the 30 percent bar meaningless on noisy wall times?") and the plan answers it nowhere.
- Amendment: before freezing the bar, run a variance probe: repeat STEP Case A 3 times and STEP Case B once, with the runbook, and report the spread. If the spread exceeds about 15 percent of the median, either raise n to 5 per arm per case or lower the bar to a value the probe shows is distinguishable from noise, and re-register the new numbers. Running the full pilot to discover its own power is backwards.

### B3. The program cap can starve Case B and produce a NO-GO for cap reasons, not lever reasons (MEDIUM, fixable, same evidence as A9)

- Evidence: same as A9 (8192 chars, 3 calls, about 80 actions, no draft program).
- False-NO-GO mechanism: if the Case B program busts 8192 chars, the executor splits it. Each split adds a model turn and a fresh observation, so the measured CODE wall includes 3 full composition thinks instead of 1. If the split program also risks the 30s default / 60s max program wall budget (design file section 5: API-call budget 32, wall-clock budget default 30s max 60s), a slow Case B program can be killed mid-run by the budget. Either failure reads as "batching did not help on the hard case" when the true statement is "the program did not fit the harness".
- Amendment: same as A9 (draft and measure now). Additionally, state in the runbook what happens if a program hits the wall budget mid-run (FAIL, not VOID, unless the budget itself is the thing under test, in which case re-register). And record program wall-budget headroom per run.

### B4. The preflight gate can kill the pilot for an adapter bug instead of a lever result (MEDIUM, fixable)

- Evidence: plan section 7 layer 2 says "If any probe shows a partial effect, the pilot does NOT proceed; that is a NO-GO by safety, reported plainly." Layer 1 is a FakeDomBackend unit test of the interpreter mirror; layer 2 is one probe per ref-taking action type against the real fixture.
- Why it matters: a partial effect on a probe proves the ADAPTER preflight (cdp.mjs) or its interpreter mirror is wrong, not that batching is a bad lever. The correct response to a broken safety invariant is to fix the adapter and re-probe, not to NO-GO the lever. The plan as written conflates two verdicts: "the batching lever fails" and "the harness has a safety bug". There is also a false-trigger risk: a probe can fail for unrelated reasons (fixture not loaded, snapshot expired at 90s, browser not started, wrong ref namespace) and be misread as a safety NO-GO. The plan lists no probe-failure triage (distinguish "partial DOM effect observed" from "probe setup failed").
- Amendment: rewrite section 7 so a probe failure triggers STOP, FIX THE ADAPTER, RE-PROBE, and only a partial effect that survives a fix attempt, or a partial effect the owner explicitly accepts as unfixable, becomes a safety NO-GO. Add a triage checklist: confirm fixture loaded, snapshot fresh, browser up, ref namespace correct, before any probe result is recorded. Also note the coverage gap: the design file's preflight covers click/fill/set_value/assert by ref; the Case B program also needs key/Enter handling and fill on #typed, so the probe list must name every action type the Case B program actually uses, not "every action type used" in the abstract.

### B5. One executor's program-composition skill decides Case B (MEDIUM, fixable by labeling, not by redesign)

- Evidence: plan section 3, one fresh executor for both arms. The design file section 7 notes program-composition think grows with program length (P3/P4 about 18s vs P2 8.59s; see N4 for why that comparison is shaky).
- Why it matters: composing an 80-action program with ref lookups and a diagnosis branch is a skill. If the single executor is bad at it (slow composition, buggy first draft, snapshot expiry from dawdling), CODE loses Case B for executor reasons. If the executor is unusually good at it, CODE wins for executor reasons. With one executor there is no way to tell which happened. This is a pilot limitation, not a design error, but the plan never states it as one.
- Amendment: state the limitation in section 10 ("single-executor result; composition skill is a confound"), and require the verdict report to include the executor's program-draft count and composition think per run, so a NO-GO driven by composition can be recognized as such. A second executor replication belongs in Exp1, not in the pilot, but the pilot must not be cited later as if executor variance were controlled.

### B6. Snapshot 90s expiry and the program wall budget can kill a legitimate Case B program (MEDIUM, fixable)

- Evidence: design file section 5 and 7: snapshot bindings expire after 90s (cdp.mjs line 160, snapshot older than 90s throws), program wall budget default 30s max 60s. The Case B program chains dom_act calls, each returning a fresh after snapshot, so chaining resets expiry in the normal path.
- Why it matters anyway: the program ALSO does desktop navigation first (windows, observe, Ctrl+L nav act, observe) before its first dom_observe, and any desktop-side delay (a stale-act refusal, a focus retry, the Pick 1 first-act flake) eats wall budget before the DOM work starts. If the program's total in-program time approaches 60s, the budget kills it mid-task. Whether 80 DOM actions plus navigation fits in 60s is UNVERIFIED; adapter round trips are milliseconds each, so it probably fits, but "probably" is not a pre-registered fact. The plan never states the program wall budget the pilot will use (default 30s or max 60s), so the executor cannot know its envelope.
- Amendment: freeze the program wall budget in the runbook (recommend max 60s for Case B, default 30s for Case A, stated explicitly), and require the dry-run program draft (A9) to report its in-program elapsed so the headroom is measured, not assumed.

## 3. Number cross-check (every load-bearing number vs its source)

### N1. Pick 1 wall 37.54s to 17.59s, minus 53 percent: VERIFIED, with four caveats that shrink it

- Source: improvements/speed-proto-pick1-p34remeasure.md, "Mean P1-P4 wall: baseline 37.54 -> Pick1 17.59 (-53%). Mean think: baseline 35.41 -> Pick1 15.43 (-56%). Model calls 5 -> 2-4 per task." The design file line 5 repeats the same figures.
- Caveat 1 (dwell excluded): P3/P4 Pick 1 walls are "excl. dwell". P3 strict wall was 295.22s (274.51s dwell), P4 strict wall 98.62s (78.04s dwell). The reported mean uses retry-only walls with diagnosis time subtracted. That is defensible for comparing task time, but it means the minus 53 percent is a sanitized mean, not a raw mean.
- Caveat 2 (attempt 1 failed): both P3 and P4 attempt 1 failed identically on the screen-changed preflight flake and only passed on retry with the identical program. The minus 53 percent counts the retries, not the attempts.
- Caveat 3 (n=1, heterogeneous tasks): the mean is across 4 DIFFERENT terminal tasks (P1-P4), each run once per arm. It is not 4 replicates of one task. A mean across heterogeneous tasks with n=1 each has no variance estimate.
- Caveat 4 ("calls 5 to 2" is a range, not a mean): the remeasure says "Model calls 5 -> 2-4 per task" (P3 5->4, P4 5->3). The design file's "calls 5 to 2" quotes the best case as if it were the uniform result. The plan itself does not quote the calls figure, but the redesign section 6 does ("calls 5 to 2"), and the plan inherits the motivation.
- The design file's own warning applies: section 9, "n=1 per arm, do not quote a precise speedup factor." The plan honors this in section 10. The redesign's section 6 motivation ("the only proposal with our own measured win (Pick 1: wall minus 53%...)") does not carry the warning with the number.

### N2. f01: 26 spec steps, 40+ actions, 71 scripted steps, PASS 3,604 ms: VERIFIED with two corrections

- 26 spec steps: VERIFIED by counting steps 1-26 in tests/realistic/fcc-k/test-01-spreadsheet-formula.md. Expected end state E5=1864000, E6=621333, E7=3: VERIFIED in the same file.
- 40+ low-level actions: VERIFIED as a quote from the spec file itself ("Per-step wall time for each click/type/read (40+ actions)").
- 71 scripted steps: VERIFIED by count (71 rows with test f01 in tests/realistic/live-run-u-20261121.jsonl, all ok true).
- 3,604 ms: VERIFIED, but the plan cites the WRONG source. The jsonl contains no 3,604 figure: the sum of f01 elapsed_ms is 2,960.7 ms and the first-to-last timestamp span is 1,329 ms. The 3,604 ms figure lives in tests/realistic/run-u-all-20261121.log ("RESULT {test f01, pass true, ... elapsed_ms 3604}", started 09:56:14.950492, finished 09:56:18.554317). Fix the citation to the log, not the jsonl.
- Correction: the 71 steps are NOT 71 spec steps. They include non-spec ops (a "TRAP: click td#a2 directly" step, diagnostic reads, and the 4-op per cell button dance). The scripted run is also a machine floor (scripted DOM, 3.6s), not a model baseline; citing it next to the 26 spec steps invites the reader to compare the CODE arm against 3.6s, which no model loop can touch. State plainly that 3,604 ms is the scripted floor, not a target.

### N3. D1 about 21s core DOM loop: VERIFIED as think, not wall; "time-to-verified about 82s" UNVERIFIED

- 21s: VERIFIED as think. Summary section 3: browser-observe think 7.5s plus browser-act think 13.2s equals 20.7s, described as "Core DOM loop (observe plus act) is about 21s of think." Correct.
- BUT it is think, not wall. D1 total wall was 293.401s (summary section 3). Any reader who takes "21s" as the D1 task time is wrong by 14x. The plan says "D1 about 21s core DOM loop" without the word think; add it.
- "Time-to-verified about 82s" (design file section 9): UNVERIFIED. No derivation appears in the summary or the design file. The partial sum of think up to the browser-act step is 79.2s (5.9 + 16.4 + 6.9 + 7.8 + 21.5 + 7.5 + 13.2), which is close to 82s but is not a derivation, and think is not wall. Do not quote 82s until someone shows the arithmetic.
- D1 has no arm-1 baseline: VERIFIED (summary section 4, "D1: no arm1 baseline exists ... It proves DOM-first works with 0 browser screenshots; it does not prove a think-time saving"). The plan states this correctly in section 10.

### N4. "Program-composition think about 18s vs P2 8.59s": UNVERIFIED and apples-to-oranges

- Source: design file section 7, repeated in plan section 3 ("program-composition think was about 18s vs P2 8.59s").
- The 8.59s is P2's TOTAL think (remeasure file: "P2 10.18 / 8.59", wall/think). The "about 18s" matches P3/P4 TOTAL think (17.99s and 17.74s), not a measured think-before-code-exec component. No source anywhere breaks out think-before-first-program-call for P3/P4. The comparison pits a component (or a mislabeled total) against a total from a different task.
- The plan's metric (think-before-first-program-call per run) is the right fix for this: measure the component directly in the pilot instead of inheriting a broken comparison. But the plan must stop citing "18s vs 8.59s" as a fact. Label it UNVERIFIED and delete it from the plan's motivation.

### N5. Pick 4 fixture md5 91b2f92945c167306a13ae32977a9bf3, 719 bytes: VERIFIED

- I ran md5sum on tests/realistic/a1-pilot/fixtures/pick4-fixture.html: 91b2f92945c167306a13ae32977a9bf3, 719 bytes. Matches the plan and the fixtures README. The README's provenance note (laptop /tmp copy lost, VM copy is the survivor) is consistent with the file's presence only under tests/realistic/a1-pilot/ and its untracked git status.

### N6. 87.8 percent loop share: UNVERIFIED (admitted by the spec itself)

- The plan does not quote it directly, but the redesign section 6 motivates the pilot with "it directly attacks the loop that is 87.8% of task time". Redesign section 9 admits the figure "has no time-motion confirmation" and "no crawled source gives a think-vs-observe-vs-act split". The pilot's six metrics are designed to measure it. Until then, every ranking that rests on 87.8 percent is an assumption, and the pilot plan should not inherit the number as a premise. Note it as UNVERIFIED in the plan's section 10.

### N7. G1 blocked at two layers; arm-1 run 1 0/4 on broker contention; clean pair minus 5 percent: VERIFIED

- G1: summary section 3, broker returns unsupported_command for a11y commands AND direct cu.py a11y ground fails its coord-frame check. Two layers, correct.
- Arm-1 run 1 0/4: summary section 2, run 1, all BLOCKED on broker contention (Pick 1 and Pick 2 workers held the single-owner broker). Correct.
- Clean pair minus 5 percent: summary section 4, P2+P3 mean 43.733s to 41.744s, minus 1.989s, minus 5 percent. Correct, and it is the only honest Pick 4 delta. The raw mean delta (minus 53 percent) is incidental executor variance, as the summary itself says.

### N8. f01 fixture "already in the repo, unchanged": UNVERIFIED as stated (no pin)

- The plan gives no checksum and no commit pin for the f01 fixture. The fixture was fixed after the original 0/10 run (commit cbbb748, "fix(fcc-k): DOM-only checkers + missing UI for f01-f03", which made formulas case-insensitive: evalFormula uppercases the formula and lowercases refs), and Worker U's live run passed after that fix. "Unchanged" since when is undefined. The plan must pin the fixture by commit hash plus md5, the same way it pins the Pick 4 fixture, or a later fixture fix silently changes the task under the pilot.
- Related: the f01 spec bug described in tests/realistic/RUN-REPORT-20261121.md (uppercase formulas threw #ERR because cell keys were lowercase) is FIXED in the committed fixture (lines 61-62 uppercase the formula and lowercase the refs), and Worker U typed uppercase =C2*D2 successfully. The spec as written now works. This is good news, but the plan never states the fix or its commit, so a reader of the RUN-REPORT would wrongly conclude Case B is broken as specced.

## 4. Contradictions between the plan and the standing rules

### C1. Generator-runner separation: Worker A1 authors the plan, the runbook, the checker, the checker self-test, AND unblinds (HIGH, KILLS the verdict's independence as written)

- Standing rule (redesign section 5.3, approved): "The generator never runs its own tests. Only a different agent's runner evidence counts, for landed changes." Worker A1 is not the generator of code-exec itself (that was Luna 6 Max), but Worker A1 IS the generator of every pilot instrument: the plan, the runbook (to be written), the checker check_run.py (to be written), the run-log schema (to be written), and the checker self-test (section 9). Section 6 then has Worker A1 do the unblinding ("done by Worker A1, not the checker, not the executor") and, by the task brief, synthesize the verdict.
- The person who writes the checker must not be the person who verifies the checker, and the person who writes the runbook must not be the person who judges whether the runs followed it. A checker self-tested by its own author is self-grading, the exact failure the evidence contract exists to prevent (Worker A2's 9 ticked checkboxes, commit b876ee1, never touched the todo file).
- Amendment: (a) the checker must be reviewed and self-tested by an INDEPENDENT worker (not A1, not the executor) against known-good and known-bad run directories that the reviewer creates from REAL runs, not hand-written files; (b) the unblinding and verdict synthesis must be done by Muse (coordinator) or a different worker, not A1; (c) A1's role after the instruments freeze is evidence packager only.

### C2. Evidence contract: the "known-good / known-bad" checker self-test has no provenance (MEDIUM, fixable)

- Plan section 9 requires the checker to be "verified against a known-good and a known-bad run directory (checker self-test)" but never says who creates those directories or how. If they are hand-written (a DOM dump typed by hand, a log fabricated to look like a run), the self-test is fabricated evidence: it proves the checker reads the files it was told to read, not that it judges real runs.
- Amendment: both directories must come from real runs (a real PASS run and a real FAIL run, e.g., a run with a deliberately wrong end state), with their full logs and commands preserved. Hand-written run directories are forbidden as self-test input.

### C3. Kill on first stall flag: the pilot has no stall rule at all (MEDIUM, fixable)

- Standing rule: kill on the FIRST stall flag; progress markers every 15 min; watchdog polls every 5 min and reports to Muse directly. The pilot plan (12 sequential runs, one executor, broker SOLO) contains no stall rule, no progress markers for pilot runs, no watchdog assignment, and no kill record procedure. If the executor stalls mid-pilot (the documented failure mode: coordinator #2 flagged 04:14, killed 04:36; clone2 stalled 70+ min), the plan has no answer except the executor's own silence.
- Amendment: add one paragraph to section 9: pilot runs carry progress markers (one per run start, per program submission, per 15 min of wall); the watchdog watches the executor; first stall flag kills the run (recorded as VOID with cause, see A7) and Muse re-spawns. No pilot run may proceed without a named watchdog.

### C4. Realistic tests: Case A is a 1-action synthetic fixture holding veto power over the verdict (MEDIUM, fixable by re-weighting, not by dropping Case A)

- Standing rule: realistic complex tests (15-40 steps), timed and logged. Case A is 1 action on a synthetic fixture built for Pick 4. The redesign resolved the selection-bias contradiction (section 4.8) by pairing it with f01, a hard case with 70 scripted steps. That pairing is correct, but the GO bar (section 5) requires BOTH cases to pass, so the synthetic 1-action case holds veto power: a NO-GO on Case A alone kills the pilot even if f01 (the realistic case) passes by a wide margin. Combined with B1 (the 30 percent bar is near-unreachable on Case A for structural reasons), the synthetic case is the most likely single cause of a false NO-GO.
- Amendment: keep Case A as a diagnostic (it is the cleanest batching comparison), but remove its veto: GO requires f01 to pass all three conditions AND Case A to pass pass-rate and recovery conditions, with Case A's wall condition reported as a diagnostic, not a gate. Or keep the veto but fix B1 first so the veto is at least attainable. One of the two must change; keeping both is stacking two independent false-NO-GO mechanisms on the same case.

### C5. No fabrication: the "sealed" manifest is honor-system, and run-id assignment is unspecified (LOW, fixable)

- Plan section 6: run-id is "a random 8-hex string assigned at run start" and the manifest is "sealed" in runs/manifest-sealed.jsonl "which the checker never opens". No mechanism seals anything: it is a plain file, the executor knows its own run-id and arm, and anyone running the checker can read the manifest first. The plan also never says WHO assigns the run-id or HOW the manifest is written (by the executor? by Worker A1? by a script?).
- Amendment: state plainly that the seal is procedural (checker code takes a run directory path and never reads the manifest; verified by code review), assign run-ids from a script run by Worker A1 before each run (not by the executor), and log the assignment. Do not call it "sealed" without that sentence; the word overclaims the mechanism.

### C6. Small commits push as you go: the plan and its fixtures are uncommitted (LOW, fixable immediately)

- The plan file and the whole tests/realistic/a1-pilot/ directory are untracked on todolist-push (verified by git status). The council is being asked to debate a design that is not on the branch.
- Amendment: commit and push the plan, the fixtures README, and this redteam report now. The missing artifacts (A8) follow as their own commits when written.

### C7. Pre-registration: the held-out choice is made AFTER the verdict (HIGH, covered in H2 below)

- Standing rule (Council C, surviving): pre-register thresholds before runs; freeze cases before the first run. The plan freezes the pilot cases and thresholds, which is correct, but section 2 freezes the held-out task AFTER the pilot verdict ("Muse picks it after the pilot verdict from the pool..."). Choosing the confirmatory task after seeing the result is the same error one level up: the choice can be steered, consciously or not, toward a task shape where the GO arm looks good.
- Amendment: see H2.

## 5. Held-out phase attack (can it really be independent and uncontaminated?)

### H1. Half the held-out pool does not exist (HIGH, KILLS the pool as written)

- Evidence: plan section 2 defines the pool as {agy-q2 test-06..test-10, clone1-batch3 t-series}. I searched the repo: "clone1-batch3 t-series" appears NOWHERE except the plan itself. There is no directory, no file, no coord entry, and no log defining a clone1-batch3 t-series (coord/clone1.md contains no "batch3" match). The pool as written is half undefined.
- Amendment: either define clone1-batch3 t-series precisely (paths, test IDs, fixture checksums) and commit that definition, or drop it from the pool and state the pool is agy-q2 test-06..test-10 only. An undefined pool member is a free choice disguised as a constraint.

### H2. Selection after the verdict by the party that knows the numbers (HIGH, KILLS the selection as written)

- Evidence: plan section 2, "Muse picks it after the pilot verdict from the pool... The choice is written down before the runner starts."
- Writing the choice down before the RUN is not pre-registration; pre-registration is writing it down before the VERDICT. Muse (coordinator) will know the pilot's numbers, which case passed, and by how much. Picking after that, Muse can steer toward a task shape that flatters the GO arm (for example, a form-fill task if CODE won on f01, or a short task if CODE won only on Case A). The runner "not knowing the pilot's numbers" does not fix this, because the bias enters at selection, not at execution.
- Amendment: pre-register the choice NOW, before any pilot run: draw one task from the (defined, see H1) pool by a recorded random draw, seal it in the manifest, and open it only after the pilot verdict. If the coordinator wants a judgment-based pick instead of a random draw, the pick must still be written and sealed before the first pilot run, with the reason recorded.

### H3. Runner independence is asserted, not enforced (HIGH, fixable)

- Evidence: plan section 2, "run by an INDEPENDENT runner (never the pilot executor)" and "The runner does not know the pilot's numbers."
- The runner is a Muse subagent spawned by the same coordinator, with the same repo access as the executor. It can read the plan, the pilot results, and this redteam report. "Never the pilot executor" is the only enforcement, and it controls identity, not knowledge. There is also no rule against the runner being the same MODEL with the same habits as the executor, or against the runner discussing the pilot with the coordinator before the run.
- Amendment: (a) the runner's brief must contain only the task spec and the GO-arm procedure, with no pilot numbers, no plan reference, and no mention of the pilot verdict; (b) the runner's transcript must be checked for reads of improvements/worker-a1-pilot-plan.md and the pilot run directories, and any such read voids the held-out run; (c) the runner must be a different agent instance from the executor AND from Worker A1. Identity separation plus a transcript check is enforceable; the current sentence is not.

### H4. The held-out run has no control arm and n=1, so it cannot confirm the speedup (MEDIUM, fixable by labeling)

- Evidence: plan section 2, the held-out task runs "using the GO-arm method only".
- A single GO-arm-only run that passes proves the method works once on a new task. It does not prove the 30 percent wall saving, because there is no STEP arm on the held-out task to compare against. A single run that fails proves even less: it could be a fixture defect (see H5), a runner error, or a genuinely hard task. The held-out phase as designed can only produce weak evidence in either direction, but its placement ("phase 2", after the verdict) invites it to be cited as confirmation.
- Amendment: either run BOTH arms on the held-out task (n=1 each, labeled exploratory, not confirmatory), or label the held-out run in the plan as "feasibility check only, not a speedup confirmation" and forbid citing it as confirmation of the 30 percent claim in Exp1's motivation.

### H5. The agy-q2 pool was validated by simulation only, never live (MEDIUM, fixable)

- Evidence: improvements/worker-q2-agy-log.md lines 96-98: "Executed node tests/realistic/agy-q2/simulate.mjs --all: all 10 tests passed (10/10, summary: all simulated, allPassed: true)." No live run of any agy-q2 test is recorded. The fcc-k precedent is direct: the same simulation pattern passed offline while the live runs went 0/10 as specced (RUN-REPORT-20261121.md), all fixture/spec defects, and the offline pass "proves the fixtures' JS works, not that an agent can complete the tasks."
- A held-out task drawn from this pool can fail on fixture defects that simulation cannot see (missing UI, unreadable state, dead buttons), and that failure would be misread as a verdict on the GO arm.
- Amendment: before the held-out draw is sealed (H2), live-run each pool candidate once with the scripted runner (not the GO arm, not the executor) and keep only candidates that pass live as specced. A pool candidate that fails live is a fixture bug to fix, not a held-out task.

### H6. The exclusion rule is necessary but not sufficient (LOW, fixable)

- Evidence: plan section 2 excludes "any test used in deliberation or pilot prep". Deliberation used f01, f03, f04, f09 and Pick 4 (redesign section 4.8); the pool does not overlap those, so the rule works as far as it goes.
- It does not go far enough: it excludes tests USED, not tests SEEN. The executor, the runner, and Worker A1 have all seen the agy-q2 specs (they are in the repo), and the GO-arm procedure could have been tuned against them in prep without any of them being "used". True held-out status for an agent with repo access is nearly impossible; the honest mitigation is H2 (sealed random draw) plus H3 (transcript check), not the exclusion sentence alone.
- Amendment: add the sealed draw and the transcript check, and state in the plan that held-out status here means "not used in pilot prep and not selected after the verdict", not "never seen by any agent".

## 6. What must change before any live arm (checklist for Worker A1 synthesis)

1. Write the runbook, the checker, and the run-log schema; get them reviewed by someone other than A1; commit and push all four documents plus this report. (A8, C1, C6)
2. Draft the Case B program now, measure its chars, and publish the count. Re-register the cap if it busts 8192. (A9, B3, B6)
3. Fix the run order: randomize the start arm per pair, or split into two executors briefed on one arm each, with no plan access. (A2, A3)
4. Forbid off-clock program authorship: no program text in the runbook, session starts before any program is written. (A1)
5. Freeze the STEP Case B interaction path to DOM observe/act per step with the same refs as CODE. (A4)
6. Define recovery operationally and count in-program retries, or drop condition 3 as a gate. (A5)
7. Fix the wall definition: exclude finish-confirmation think, bound finish to one turn, and re-derive the Case A bar from the batchable portion (or remove Case A's wall veto). (B1, C4)
8. Run the variance probe and re-register n and the bar from measured spread. (B2, A7)
9. Rewrite the preflight gate as stop-fix-reprobe, with a triage checklist and the full action-type list. (B4)
10. Seal the held-out draw BEFORE the first pilot run, from a defined pool whose candidates pass live. (H1, H2, H5)
11. Assign the watchdog and the stall rule to the pilot; define VOID vs FAIL with a void cap. (C3, A7)
12. Correct the citations: 3,604 ms to the run-u-all log, delete "18s vs 8.59s", add "think" to the 21s figure, pin the f01 fixture by commit plus md5, label 87.8 percent UNVERIFIED. (N2, N4, N3, N8, N6)

## Sources (all accessed 2026-11-21, all in repo, branch todolist-push unless noted)

- improvements/worker-a1-pilot-plan.md (DRAFT, untracked at time of writing)
- improvements/working-structure-redesign-20261121.md, sections 6 and 9 (commit fb00973)
- improvements/a1-code-exec-dom-design.md (2026-11-19)
- improvements/speed-proto-pick4-summary.md (2026-11-19)
- improvements/speed-proto-pick1-p34remeasure.md (2026-11-19)
- tests/realistic/fcc-k/test-01-spreadsheet-formula.md (26 steps, expected end state)
- tests/realistic/fcc-k/fixtures/test-01-spreadsheet.html (interaction model, lines 33-66; fixture fix at commit cbbb748)
- tests/realistic/live-run-u-20261121.jsonl (f01: 71 rows, all ok; sum elapsed 2,960.7 ms; span 1,329 ms)
- tests/realistic/run-u-all-20261121.log (f01 RESULT elapsed_ms 3604; serving at http://127.0.0.1:8767)
- tests/realistic/RUN-REPORT-20261121.md (f01 spec bug; simulated checkers prove JS works, not agent completability)
- tests/realistic/a1-pilot/fixtures/pick4-fixture.html (md5 91b2f92945c167306a13ae32977a9bf3, 719 bytes, verified by md5sum)
- tests/realistic/a1-pilot/fixtures/README.md (provenance)
- tests/realistic/agy-q2/test-06-file-converter.md through test-10-markdown-editor.md (pool members that exist)
- improvements/worker-q2-agy-log.md lines 96-98 (agy-q2 validated by simulation only, 10/10 simulated)
- scripts/code_exec.py line 92 (MAX_PROGRAM_CHARS = 8192), scripts/cdp.mjs line 160 (snapshot older than 90s)
- git status on 2026-11-21: plan file and tests/realistic/a1-pilot/ untracked; runbook.md, check_run.py, run-log-schema.md do not exist (ls confirmed)
- Repo search on 2026-11-21: "clone1-batch3 t-series" appears only in the pilot plan; no files, no coord entry
