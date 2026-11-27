# Council Member 1 (performance) verdict: A1 narrow pilot plan

- Date: 2026-11-21
- Role: Council Member 1, performance only. Worker A1 (Muse) is the pilot worker.
- Status: COUNCIL VERDICT on the DRAFT pilot plan. The pilot does not run as written.
- Overall verdict: AMEND. All six design points below are AMEND, none is GO as written, none is BLOCK. Every point is fixable before the freeze, and no point kills the pilot. The pilot proceeds only after Worker A1 synthesizes these amendments into the frozen plan.
- Owner direction applied: best quality, not speed. The approved working-structure redesign proposal is followed as Lauren Tan advises. That means the pilot is judged on whether it produces a trustworthy number, not on whether it runs fast.
- Sources read (all on branch todolist-push, repo computer-use-wayland):
  - improvements/worker-a1-pilot-plan.md (DRAFT pilot plan, sections 1 to 5 and 11 are the performance scope)
  - improvements/working-structure-redesign-20261121.md section 6 (approved pilot spec, commit fb00973)
  - improvements/a1-code-exec-dom-design.md (Pick 1 / D1 design, 2026-11-19)
  - improvements/speed-proto-pick4-summary.md section 4 (before/after table)
- Rules applied: no fabrication, unknown stays UNVERIFIED, no em dash or en dash anywhere in this file, never ydotool, no personal info in this file or its commit.

## Verdict table

| Design point | Verdict | One line |
|---|---|---|
| 1. The two cases (Pick 4 one-action task, f01 26-step spreadsheet) | AMEND | Keep the pair, it is the right floor plus ceiling shape, but Pick 4 must not veto f01 on wall time. |
| 2. n=3 per arm with a 30 percent median-wall bar | AMEND | Keep n=3 and 30 percent as a pilot screen, but add a 2-of-3 rule, a dispersion rule, and an INCONCLUSIVE outcome. |
| 3. The 3-program-call cap for Case B | AMEND | Replace 3 planned calls with 2 planned plus 1 recovery for Case B, 1 planned plus 1 recovery for Case A, with split points frozen before the first run. |
| 4. STEP-first alternation | AMEND | STEP-first is not conservative, it is favourable to the hypothesis. Counterbalance the start arm across the two cases. |
| 5. Chromium/CDP isolation instead of Zen | AMEND | Keep Chromium for the pilot, isolation is correct, but add a mandatory Zen transfer probe between a Chromium GO and Exp1. |
| 6. Think-before-first-program-call measurement | AMEND | Measure think before EACH program call, define the window precisely, exclude finish think from wall, and make total composition think a GO condition. |

## 1. Cases: Pick 4 plus f01

Verdict: AMEND.

### The question

Are the two cases the right pair to test the batching lever, or is one of them a foregone conclusion?

### Evidence

- Case A (Pick 4): one action, click "Show result", verify #result contains "pick4-ok". Fixture md5 91b2f92945c167306a13ae32977a9bf3, 719 bytes. The D1 program in the design file is about 900 chars. D1 on Chromium was SUCCESS with 0 browser screenshots, core DOM loop (observe plus act) about 21s of think, but total D1 wall 293.401s.
- Case B (f01): 26 spec steps, 40+ low-level click/type/read actions, 71 steps in Worker U's scripted DOM run (tests/realistic/live-run-u-20261121.jsonl, f01 PASS 3,604 ms). It has a mid-task diagnosis step (wrong COUNT formula returning text, fix to COUNTA, confirm E5=1864000, E6=621333, E7=3).
- Pick 1 (the prior win this pilot extends): mean wall 37.54s to 17.59s, minus 53 percent, think minus 56 percent, calls 5 to 2, 4/4 SUCCESS. The design file warns for the sibling D1 measurement: "n=1 per arm, do not quote a precise speedup factor."
- Pick 4 clean pair (P2+P3): mean wall 43.733s to 41.744s, minus 1.989s, minus 5 percent. The raw mean minus 53 percent was inflated by incidentals (see point 2).

### Reasoning

The pair is the right shape: a floor case and a ceiling case. Pick 4 tests whether batching works at all on the smallest deterministic task. f01 tests whether batching survives length, branching, and a mid-task diagnosis, which is exactly what batching claims to absorb locally. Neither case alone would be enough.

But Pick 4 is close to a foregone conclusion in one direction and not a fair wall test in the other:

- Foregone on core think: the CODE arm needs about 1 program call against a STEP arm of about 9 model turns (windows, observe, navigate act, observe, tabs, DOM observe, DOM act click, DOM assert, close, per the draft plan section 3). Core think has to fall. A CODE win on Pick 4 core think proves almost nothing about f01.
- Not foregone on wall: D1 wall was 293.401s while its core DOM loop was about 21s. The rest was navigation think, close think, and finish think of 139.2s (see point 6). Program-composition think for P3/P4 was about 18s versus P2 8.59s (design file section 7), which eats a large share of the saving on a 1-action task. So Pick 4 wall can fail the 30 percent bar for reasons that have nothing to do with the batching lever.
- f01 is not foregone either way. Its program must cover 26 spec steps plus branching plus asserts inside the 8192 char cap and the 3-call cap, and its composition think scales with program length in a way Pick 4 cannot predict. Whether f01 fits in the caps at all is UNVERIFIED until a draft program is counted (see point 3).
- The draft GO rule (section 5) requires the 30 percent median wall cut on BOTH cases. That makes Pick 4, the weaker wall test, a veto over f01, the real test. A Pick 4 wall miss caused by finish think or navigation overhead would kill a genuine f01 win. That coupling is backwards.

### Exact amendment

Replace draft plan section 5 with the following per-case GO rule, and add it to section 2:

> GO requires, on Case B (f01): median wall time (CODE) down at least 30 percent versus median wall time (STEP), pass rate (CODE) equal or better than pass rate (STEP), and recovery steps (CODE) not higher than recovery steps (STEP). Case A (Pick 4) is a feasibility gate, not a wall gate: it requires pass rate (CODE) equal or better than pass rate (STEP) and recovery steps (CODE) not higher than recovery steps (STEP), and its median wall time is reported as a diagnostic only. If Case B passes all three of its conditions and Case A passes its feasibility gate, the verdict is GO. If Case B fails any condition, the verdict is NO-GO regardless of Case A. If Case A fails its feasibility gate, the verdict is NO-GO regardless of Case B, because the lever does not work at all. A partial outcome is reported per case in all cases.

Also add to section 2: "If the f01 fixture is fixed after the freeze (the redesign proposal section 6 notes fixture fix work for f01, f03, f04, f09 running in parallel on disjoint cases), the freeze is broken: the fixture checksum is re-verified and the freeze is re-recorded before the first live run. No live run starts on a fixture whose checksum differs from the frozen value."

### Dissent considered

- Dissent: keep the symmetric both-cases 30 percent rule, because symmetry is simpler and a lever that cannot win on the easy case should not be trusted on the hard case. Rejected: the easy case is not easy on wall time, it is easy only on core think, and its wall is dominated by overhead common to both arms (navigation, close, finish). Symmetry here tests overhead, not the lever.
- Dissent: drop Pick 4 and run f01 only. Rejected: Pick 4 is the only case with a proven DOM path (D1, 0 browser screenshots) and a frozen fixture in the repo. It is a cheap smoke test that the harness works before the long case runs. Keep it, demote its wall gate.

## 2. n=3 per arm and the 30 percent median bar

Verdict: AMEND.

### The question

Is n=3 per arm with a 30 percent median-wall bar meaningful, or is wall-time noise on this harness going to swamp it?

### Evidence

- Pick 4 arm 1 run 2 walls: P1 281.494s, P2 43.609s, P3 43.857s, P4 312.513s. Mean 170.368s. Same arm, same harness, a 7x spread between the fastest and slowest task.
- Pick 4 arm 2 walls: P1 114.219s, P2 42.323s, P3 41.164s, P4 121.943s. Mean 79.912s. A 3x spread inside the arm.
- Clean pair P2+P3 mean: 43.733s to 41.744s, minus 5 percent. Raw mean over all four tasks: minus 53 percent. The headline depends entirely on which runs count.
- Identified inflation sources in Pick 4: arm 1 P1 first kitty launch failed, windows-retry think 110.7s, first act stale-refused (observation older than 90s); arm 1 P4 extra od-verify and byte-check acts (think 112.7s before od-verify, 69.7s before byte-check), 5 observes; arm 1 P3 gap includes a failed first start (broker held) and a 120s logged wait; D1 finish think 139.2s.
- Pick 4 arm 1 run 1 was 0/4, all BLOCKED by broker contention (parallel workers held the single-owner broker). The pilot plan mitigates this with broker SOLO and one run at a time (section 4), which is the right mitigation, but contention is only one of the four inflation sources above.
- The 30 percent bar sits between the clean minus 5 percent and the inflated minus 53 percent. A 30 percent median delta can therefore be produced by incidentals alone, as P1 minus 59 percent and P4 minus 61 percent were.

### Reasoning

With n=3, the median is a single middle run. It has no confidence interval and no protection against a middle run that happens to be the inflated one. If two of three runs in an arm are inflated, the median is inflated. The draft plan has no dispersion rule, no rule for what counts as an inflated run, and only two outcomes (GO or NO-GO), so a noisy pilot is forced into a confident verdict it has not earned.

That said, n=3 is the right size for a pilot. Council C Exp1 was 44 runs; the redesign correctly cut it to a pilot first. Raising n now would spend the pilot budget on precision the pilot does not need. The fix is not more runs, it is rules that stop a noisy n=3 from producing a false GO or a false NO-GO.

The 30 percent bar itself is a reasonable pilot screen: it is well above the clean-pair minus 5 percent (so a terminal-task-style null does not pass) and well below the Pick 1 minus 53 percent (so it does not demand the inflated number). Keep the bar, add the rules around it.

### Exact amendment

Add to draft plan section 5, after the existing three GO conditions:

> 4. At least 2 of the 3 CODE runs in a case are individually at least 20 percent below the STEP median wall for that case. A median that passes only because of one fast run does not pass.
> 5. Dispersion: for each arm-case cell of 3 runs, report (max minus min) divided by the median. If that ratio exceeds 50 percent in any cell, the verdict for that case is INCONCLUSIVE, not GO and not NO-GO, regardless of the median. Report all 12 runs, including failures, timeouts, and kills, with no run silently dropped.
> 6. Inflated runs are flagged, not deleted. A run is flagged if it contains any of: session death and restart, broker contention, a stale-snapshot refusal, or an extra verification act not in the runbook. Flagged runs stay in the median. If 2 or more runs in one arm-case cell are flagged, the verdict for that case is INCONCLUSIVE, not GO.
> 7. INCONCLUSIVE is a third outcome. On INCONCLUSIVE, Worker A1 reports the noise source plainly and the pilot is re-run after the noise source is fixed, it is not re-run unchanged hoping for a cleaner draw.

### Dissent considered

- Dissent: raise n to 5 per arm so the median is stabler. Rejected for the pilot: 20 runs instead of 12 spends pilot budget on precision before the design is proven runnable, and n=5 still has no dispersion rule. If the pilot goes INCONCLUSIVE on dispersion, the re-run is the place to revisit n.
- Dissent: drop the 30 percent bar to 20 percent because the clean-pair evidence suggests real lever effects may be small. Rejected: the clean pair measured a different lever (Pick 4 fast path on terminal tasks, minus 5 percent), not code-exec batching. Lowering the bar on that evidence would let a null pass. Keep 30 percent for the pilot.

## 3. The 3-program-call cap for Case B

Verdict: AMEND.

### The question

Is the 3-program-call cap for Case B honest, or does it let the CODE arm smuggle extra model turns through program splits?

### Evidence

- Draft plan section 3: each program at most 8192 chars (interpreter MAX_PROGRAM_CHARS, hard cap), at most 3 program calls per run, program char count and call count reported per run. More than 3 calls is recorded as a design miss, not worked around by editing the cap.
- Design file section 2: a dom_act call takes a list of 1 to 32 action dicts, and a program may chain several dom_act calls. A program can also loop, branch, re-observe, and retry locally at 0 model calls.
- Design file section 3: the D1 program is about 900 chars for 1 click plus navigation plus asserts.
- Design file section 7: program-composition think grows with program length (P3/P4 think-before-code-exec about 18s versus P2 8.59s).
- STEP arm for Case B is 26 spec steps, one model turn per action, so about 26 or more model turns.

### Reasoning

Three program calls is still far fewer than 26 step turns, so the cap does not erase the lever. And wall time already prices extra turns: each extra program call costs its own composition think, so splitting does not hide cost from the headline metric. In that sense the cap as written is not dishonest about wall time.

But it is dishonest about what the lever is, in two ways:

- First, a planned split is a model turn. The lever under test is one observation yielding many actions. A program split is a fresh model turn with a fresh observation and fresh context. Three planned splits means the CODE arm is really 3 batched turns, not 1. The draft plan reports program-call count but does not distinguish a planned split from a recovery retry, so a CODE arm that needed 3 planned programs to cover 26 steps looks identical in the report to one that needed 1 planned program plus 2 recoveries. Those are different findings: the first says the char cap forces splits, the second says the program failed twice.
- Second, composition think is measured only before the first call (see point 6). Calls 2 and 3 each carry their own composition think, about 18s each at the P3/P4 reference scale, which is unmeasured as a separate field. A 3-split CODE arm could carry 54s of composition think that the headline think metric never attributes.
- The cap number itself is arbitrary. Nothing in the sources shows whether 26 spec steps fit in 1, 2, or 3 programs of 8192 chars. Linear scaling from D1 (about 900 chars for 1 click plus navigation) is UNVERIFIED. If f01 does not fit in 2 programs, a 2-call cap would test the char limit instead of batching. If it fits in 1, a 3-call cap is generous. The honest cap cannot be set from the sources; it must be set from a counted draft.

### Exact amendment

Replace the draft plan section 3 cap paragraph with:

> Caps (pre-registered): each program at most 8192 chars (the interpreter MAX_PROGRAM_CHARS, hard cap). Case A: at most 1 planned program call plus at most 1 recovery call. Case B: at most 2 planned program calls plus at most 1 recovery call. A recovery call is a program call issued only after a previous program returned ok false or a failed assert with completed 0 or no effect, and it counts as 1 recovery step against the section 5 recovery gate. Planned split points are frozen in the runbook before the first live run: which spec steps each planned program covers. No adaptive re-splitting mid-run except through the single recovery call. Program char count per call, program call count, and planned versus recovery label are reported per run. If a case needs more planned calls than the cap, that is recorded as a design miss, not worked around by editing the cap.
>
> Preflight char check (prep, before any live run): Worker A1 drafts the Case B planned programs without running them and counts chars. If the draft exceeds 2 times 8192 chars, the Case B cap reverts to 3 planned calls plus 1 recovery, and that reversion, with the draft char count, is frozen in the runbook before the first live run. The reversion is a char-limit finding, recorded as such, not a silent assumption.

### Dissent considered

- Dissent: keep 3 planned calls, because wall already prices extra turns and the char fit is UNVERIFIED, so 3 is the safe number. Rejected as the default, but kept as the fallback: the amendment keeps 3 available through the preflight char check, so the safe number is reachable only with counted evidence, not by assumption.
- Dissent: set the cap to 1 planned call for both cases, the purest test of one observation yielding many actions. Rejected: if f01 does not fit in 8192 chars, a 1-call cap makes the pilot impossible by construction and tests the char limit, not batching. The 2-planned cap plus the char-check fallback is the honest middle.

## 4. STEP-first alternation

Verdict: AMEND.

### The question

Is STEP-first alternation the right warmup protection, or should the start arm be randomized?

### Evidence

- Draft plan section 4: per case, run order is STEP, CODE, STEP, CODE, STEP, CODE. Stated reason: "Step first so any first-run warmup cost lands on the control arm, conservative against the hypothesis."
- Warmup and learning effects in the sources: first-run costs are documented (Pick 4 arm 1 run 1 was 0/4 BLOCKED on broker contention; P1 first kitty launch failed with 110.7s windows-retry think). Executor learning is not measured anywhere in the sources; whether the same executor learns the task from the first arm is UNVERIFIED, but the mechanism is plain: the executor that just did f01 step by step knows the fixture layout, the correct formulas, and the diagnosis before composing the CODE program.

### Reasoning

The stated reason is backwards. Landing the first-run warmup cost on the control arm makes STEP slower, which makes CODE look faster, which makes the 30 percent bar easier to pass. That is favourable to the hypothesis, not conservative against it. Conservative would be landing warmup on CODE. The draft plan's warmup protection points the wrong way.

Alternation also confounds order with arm in a second way: CODE always runs immediately after a STEP run of the same case. The single executor (draft plan section 3, same model, same harness, to minimize executor variance) has just completed the task stepwise before composing the CODE program. Its composition think is therefore not fresh think; it is informed think. The same confound runs the other way on later runs (STEP run 3 benefits from CODE run 2), but the first CODE run is the one that matters most for the composition-think comparison, and it is always the informed one.

Randomization per case is the textbook answer, but with only 2 cases it does not guarantee balance: two independent coin flips land on the same start arm 50 percent of the time. Counterbalancing guarantees balance: one case starts STEP, the other starts CODE, so warmup and first-run learning land on each arm exactly once across the pilot.

### Exact amendment

Replace draft plan section 4 run-order paragraph with:

> Run order is counterbalanced across cases, not STEP-first on both. Case A starts STEP, Case B starts CODE (assignment frozen in the runbook before the first run), then arms alternate within each case: Case A runs STEP, CODE, STEP, CODE, STEP, CODE; Case B runs CODE, STEP, CODE, STEP, CODE, STEP. The first run of each case is reported separately as the least-contaminated comparison, because only the first run in a case has no prior exposure to that case by the same executor. The draft plan's claim that STEP-first is conservative is withdrawn: landing warmup on the control arm favours the hypothesis, it does not protect against it. Executor learning across runs in a case is a known confound of the single-executor design and is disclosed in the pilot report; it is not assumed away.

### Dissent considered

- Dissent: randomize the start arm per case, the standard method. Rejected at this n: with 2 cases, randomization leaves a 50 percent chance of the same start arm on both cases, which is no balance at all. Counterbalancing is deterministic balance. Randomization becomes the right choice only when the pilot grows to more cases.
- Dissent: use separate executors per arm to remove learning entirely. Rejected for the pilot: it doubles executor variance, which the draft plan correctly chose to minimize with one executor, and it doubles briefing cost. Keep one executor, counterbalance, disclose.

## 5. Chromium/CDP isolation instead of Zen

Verdict: AMEND.

### The question

Is Chromium/CDP (not Zen) the right isolation for this pilot, or does it make the result irrelevant to the user's goal (Muses driving THE USER'S Zen)?

### Evidence for Chromium

- The lever under test is batching, not Zen control (draft plan section 3). Zen has open failure modes that would confound the lever: the hidden-body incident at 17:52 on 21/11, and BiDi click reported ok but fired nothing (redesign proposal sources, docs/zen-dom-control-comparison.md).
- The DOM path is proven on Chromium: D1 SUCCESS, 0 browser screenshots, click by ref plus DOM assert, core DOM loop about 21s of think. No equivalent baseline exists on Zen.
- The code-exec DOM path (dom_start default endpoint http://127.0.0.1:9222, managed Chromium) is the path the design file built. Zen control goes through a different path (zen-mcp, single session per Zen, DOM read 3 to 5ms, vision grounding 17/29 = 58.6 percent).
- The pilot plan section 10 states plainly that the pilot does not prove batching wins on Zen.

### Evidence against Chromium

- The user's goal is Muses driving THE USER'S Zen: the user's sessions, the user's Gmail, the user's daily browser live there. A Chromium win does not transfer by itself. Transfer of desktop results to Zen is assumed, not shown, in the crawl (MobiBench transfer to desktop Zen is assumed, not shown, per the redesign proposal section 2).
- The costs that batching saves may differ by browser: DOM read cost, click reliability (BiDi false-ok forces extra verification on Zen), snapshot expiry behaviour, and finish overhead are all browser-specific. A CODE program that passes on Chromium could fail on Zen for reasons that have nothing to do with batching, or a wall win on Chromium could vanish on Zen if Zen verification costs more.
- The redesign proposal section 6 chains a pilot GO directly to Council C Exp1 as the confirmatory run, with no transfer step in between. A Chromium GO read that way licenses scale-up on a result that section 10 admits does not prove the Zen case.

### Reasoning

Both sides are right about different things. Chromium is right for internal validity: the pilot can actually run, and a difference between arms can be attributed to batching rather than to a Zen failure mode. Zen is right for external validity: the result only matters if it survives contact with the browser the owner actually uses. A pilot that picks one side and ignores the other is either unrunnable or irrelevant.

The fix is sequence, not substitution. Run the lever test where it is clean (Chromium), then run a transfer probe where it matters (Zen), before any scale-up. The transfer probe is diagnostic, not a second full pilot: one run per arm on Zen, Case A only, same fixture and task, same blinded checker. Its job is to catch a transfer failure (CODE fails on Zen, or CODE wall is worse than STEP on Zen) before Exp1 spends runs assuming transfer.

### Exact amendment

Add to draft plan section 10, after the existing "It does not prove batching wins on Zen" line:

> A Chromium GO does not authorize Exp1. Between a Chromium GO and Exp1, a Zen transfer probe runs: Case A only, 1 run per arm on Zen, same fixture and task, same blinded checker, no GO bar. The probe is diagnostic. If the CODE probe run fails, or its wall is worse than the STEP probe run wall, Exp1 is paused and the transfer failure is investigated and reported before any scale-up. Exp1 proceeds only after the probe is reported. The pilot report states Chromium-only in its title and in every claim: no wall-time claim in the pilot report names Zen.

### Dissent considered

- Dissent: run the pilot on Zen directly, because only Zen results matter and Chromium results are wasted runs. Rejected: the hidden-body incident happened the same day the pilot was drafted, and BiDi false-ok is an open failure mode. A Zen pilot that fails could fail on Zen, not on batching, and the pilot would have spent 12 runs learning nothing about the lever.
- Dissent: keep Chromium only, with the existing section 10 disclaimer, and let Exp1 handle Zen. Rejected: a disclaimer does not stop the GO-to-Exp1 chain in section 6 from being read as a licence to scale. The transfer probe is one run per arm, cheap insurance against a false scale-up.

## 6. Think-before-first-program-call measurement

Verdict: AMEND.

### The question

Is think-before-first-program-call measured well enough to catch a wall win bought by huge composition think?

### Evidence

- Draft plan section 3: think-before-first-program-call is measured per run (the P3/P4 lesson: program-composition think was about 18s versus P2 8.59s). Section 5: it is reported alongside wall time, so a wall win bought by huge composition think is visible, not hidden. Section 8: it is a per-run field.
- Design file section 7: same P3/P4 versus P2 numbers, guard is "measure think-before-code-exec on the D1 program and report it; if it eats the DOM saving, the verdict says so."
- D1 think splits (Pick 4 summary section 3): browser-start 5.9s, windows 16.4s, tabs 6.9s, desktop-observe 7.8s, navigate-act 21.5s, browser-observe 7.5s, browser-act 13.2s, close-observe 45.8s, close-act 14.7s, windows-after-close 11.2s, finish 139.2s. Sum about 290s against D1 wall 293.401s.
- Draft plan section 3 run window: task start (session start submit) to verified end state. D1 wall as reported includes finish think of 139.2s, which falls after the end state is verified. The window definition and the D1 measurement therefore disagree about whether finish think is inside wall.
- Draft plan section 8: tokens are BEST-EFFORT (report UNMEASURED if unavailable, never estimated) and observation cost is aspirational until the harness logs it. Think is therefore the only composition-cost signal the pilot actually has.

### Reasoning

No, as written it is not measured well enough, for four reasons:

- First, only the FIRST program call is measured. The cap allows 3 calls. Calls 2 and 3 each carry composition think (about 18s each at the P3/P4 reference scale), and none of it is attributed as a separate field. A CODE arm could buy its wall win with huge think on calls 2 and 3 while the reported first-call number looks small.
- Second, the window is undefined. "Think before first program call" could mean from task start, from session start, or from the end of the previous model turn. The executor may also do exploratory observes before composing the program; whether that think counts is unspecified. Two runners could compute different numbers from the same run.
- Third, it is reported, not gated. Section 5 GO conditions are wall, pass rate, and recovery only. A CODE win with composition think at 80 percent of wall still passes GO. Reporting makes the problem visible; it does not make the verdict catch it. The design file's own guard ("if it eats the DOM saving, the verdict says so") has no threshold, so "the verdict says so" is unenforceable.
- Fourth, finish think contaminates wall. D1 finish think was 139.2s, larger than every other think split combined and larger than the entire Pick 1 wall win (37.54s to 17.59s, a 19.95s saving). If finish think is inside the wall window, a 30 percent wall delta can be created or erased by executor finish verbosity alone. If it is outside, D1 wall should have been about 154s, not 293.401s. The pilot must pick one definition before the first run.

### Exact amendment

Replace the draft plan section 8 per-run field "think-before-first-program-call (CODE arm)" with the following, and add a fourth GO condition to section 5:

> Think-before-program-call is timed for EACH program call, not only the first. Definition: elapsed wall time from the end of the previous model turn (or from task start for the first call) to the submit timestamp of that program call, taken from the timed run log. The executor does no exploratory observe between the end of the previous turn and the program submit except the observes the program itself performs; any exploratory observe before a program call is logged as its own run-log line and its think counts toward that call. Report per run: think before each program call, the sum over all program calls (total composition think), and the largest single call. Report finish think separately: elapsed from verified end state to session finish. Wall time ends at verified end state (DOM assert pass), so finish think is OUTSIDE wall and is reported as a diagnostic only.
>
> GO condition 4 (both cases): total composition think (CODE, sum over all program calls) is less than STEP median total think for that case. Batching claims to cut think by cutting turns; if total think does not fall, the wall win was bought elsewhere and the verdict is NO-GO on the lever, even if wall passes. If total composition think exceeds 50 percent of CODE median wall, that is flagged in the report even when GO condition 4 passes.

### Dissent considered

- Dissent: keep first-call-only measurement, because the first call carries the bulk of composition think and later calls are small retries. Rejected: the cap allows 3 planned calls, and a planned split is a full composition, not a small retry. First-call-only measurement assumes what the pilot is supposed to test.
- Dissent: make composition think a diagnostic, not a GO condition, because wall is the headline and think is secondary. Rejected: wall includes service time (Pick 4 service was 0.887s to 7.099s per task) and observation time, both small next to think (the loop is 87.8 percent think by the internal 10x review figure, and Pick 4 gaps were 40s to 472s against service of about 1s to 7s). A wall win without a think win on this harness would be a service-time accident, not a batching win. The think gate is what ties the verdict to the lever.

## What stays unchanged

- n=3 per arm per case, 12 runs total. The pilot stays small.
- The 30 percent median wall bar for Case B. The bar stays.
- Chromium for the pilot runs. Isolation stays.
- One fresh executor for both arms, broker SOLO, one run at a time, fresh browser session and fresh fixture state between runs. The variance controls stay.
- The blinded checker, sealed manifest, and run-log JSONL schema. The anti-self-deception machinery stays. (Blinding itself is a question for the council member covering it, not for performance; this verdict takes no position on whether the checker can infer the arm from run-log shape.)
- The preflight safety gate (Layer 1 unit test plus Layer 2 live probe, bad ref mid-list, completed 0, zero DOM effects). Safety is not a performance question and is not weakened here.

## UNVERIFIED items this verdict depends on

- Whether the Case B program fits in 2 times 8192 chars. UNVERIFIED until the preflight char check counts a draft. The point 3 amendment is built around this gap.
- Whether the same executor learns the task from the first arm and composes the CODE program faster for it. UNVERIFIED, no measurement in the sources. The point 4 amendment discloses it and reports the first run separately rather than assuming it away.
- Whether batching transfers from Chromium to Zen. UNVERIFIED. The point 5 amendment adds the transfer probe rather than assuming transfer.
- Whether composition think for a 26-step program scales linearly from the D1 900-char program or the P3/P4 18s reference. UNVERIFIED. The point 6 amendment measures it per call instead of assuming a scale.
- Token counts and observation cost by type. UNMEASURED by the draft plan's own admission (best-effort and aspirational). This verdict does not rely on either.

## Sources

- improvements/worker-a1-pilot-plan.md, DRAFT, 2026-11-21 (sections 1 to 5, 11).
- improvements/working-structure-redesign-20261121.md, section 6, commit fb00973, accessed 2026-11-21.
- improvements/a1-code-exec-dom-design.md, 2026-11-19 (Pick 1 mean wall 37.54s to 17.59s, D1 core think 99.2s to 20.7s, D1 program about 900 chars, MAX_PROGRAM_CHARS 8192, dom_act 1 to 32 actions, P3/P4 think-before-code-exec about 18s versus P2 8.59s).
- improvements/speed-proto-pick4-summary.md, 2026-11-19 (section 4 before/after table; D1 wall 293.401s and think splits; clean pair minus 5 percent; P1 windows-retry think 110.7s; P4 extra verification think 112.7s and 69.7s; arm 1 run 1 0/4 BLOCKED).
