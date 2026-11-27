# Worker W council position paper C: measurement and experiments

- Worker: W-Council-C (measurement councillor, Worker W structure team)
- Date: 2026-11-21. Written 17:52 Asia/Ho_Chi_Minh.
- Branch: todolist-push, repo computer-use-wayland.
- Status: PROPOSAL ONLY. No structural change is implemented by this paper. No code, no harness change, no test change is made here. Every experiment below is proposed for the parent coordinator to approve and assign to an independent runner.
- Sources: every external claim cites a source plus access date. Internal numbers are labeled INTERNAL. Unknown is UNVERIFIED. No em dash or en dash is used anywhere in this file, per standing rule.

## 0. The question this paper answers

The owner priority is performance when Muses control the user's machine. The single most valuable first step must be a concrete performance lever, not an org chart change. The crawls agree on the lever but do not prove it on our stack:

- Structures crawl (improvements/worker-w-crawl-structures-20261121.md, accessed 2026-11-21): "No source found in this crawl that measures 'one observation yields many actions' as a standalone intervention with an A/B wall-time number on a desktop GUI task. HCU and Qwen-UI-Agent are the closest published evidence, via batching and step counts. This is a gap worth a direct experiment on our own test cases."
- Bottlenecks crawl (improvements/worker-w-crawl-bottlenecks-20261121.md, accessed 2026-11-21): "No crawled source today gives a measured think-vs-observe-vs-act split of wall time for a computer-use loop. Our 87.8% figure is INTERNAL and stands alone."
- Clip (improvements/worker-w-crawl-clip-20261121.md, accessed 2026-11-21): Lauren Tan's rule, "done means nothing without runnable verification evidence", and "a repeated mistake becomes a deterministic rule, not a reminder". Applied to us: a speedup claim means nothing without a timed run on a frozen test, verified by an independent runner.

So the job of this paper is narrow: define the one experiment that closes the gap, define the metrics every run reports from now on, rank what to try first, and define how we stop fooling ourselves.

## 1. Our measured baseline (INTERNAL, 2026-11-21)

These are our own numbers, not literature claims. They are the baseline every experiment below is measured against.

| Number | Value | Source |
|---|---|---|
| Hand-driven t01, wall time | about 7 min, 12 tool calls, about 35 s per agent step | tests/realistic/RUN-REPORT-20261121.md, 2026-11-21 |
| Same t01, scripted machine time | 2,678 ms | tests/realistic/RUN-REPORT-20261121.md, 2026-11-21 |
| Hand vs scripted ratio | about 157x | Bottlenecks crawl, INTERNAL, accessed 2026-11-21 |
| Think-observe-think share of task time | 87.8% | 10x review finding, INTERNAL, cited in both crawls, 2026-11-21 |
| clone1 t01-t10, scripted | 10/10 PASS in 59,111 ms | tests/realistic/RUN-REPORT-20261121.md, 2026-11-21 |
| agy-q | 4/5 in 20.5 s | Task brief, INTERNAL, 2026-11-21 |
| fcc-k fixed | 10/10 in 28.6 s | Task brief, INTERNAL, 2026-11-21 |
| Full suite | 1,523 tests, 0 failures, 119.9 s | Task brief, INTERNAL, 2026-11-21 |
| fcc K2 | died twice with zero output | Task brief, INTERNAL, 2026-11-21 |
| agy Q2 first run | timed out at 10 min at 4/10 tests | Task brief, INTERNAL, 2026-11-21 |
| clone1 batch 2+3 | done in about 20 min, quality questioned | Task brief, INTERNAL, 2026-11-21 |
| clone2 | stalled 70+ min once | Task brief, INTERNAL, 2026-11-21 |
| Coordinator #2 stall | flagged 04:14, killed 04:36 | Task brief, INTERNAL, 2026-11-21 |

Three baseline facts that change the experiment design, all from RUN-REPORT-20261121.md:

1. clone1 tests are 5-7 steps each, not 15-40. They are too short to show think-time differences. They are controls, not the measurement set.
2. fcc-k tests are 16-26 steps each and are the right size, but their fixtures are defective: f01 has a spec bug (uppercase formulas, fixture keys are lowercase, diagnostic with lowercase PASSES), f02-f05 have fixture gaps, f06-f08 and f10 are BLOCKED on dead buttons or missing UI, and every fcc-k `__fcckVerify()` checker self-simulates the intended flow and then checks its own simulated state. A checker that writes its own expected state is not a checker. The offline 10/10 proves the fixtures' JS works, not that an agent can complete the tasks.
3. Extrapolation in the run report (estimate, NOT measured): f01 has 70 scripted steps, at about 35 s per agent step that is about 40 min hand-driven. Long cases are expensive to run by hand. The experiment must budget for that instead of pretending runs are cheap.

Consequence: no batching experiment is valid until the fcc-k fixtures are fixed and their checkers are replaced by DOM assertions. That fix is a precondition, not part of the experiment. If the fixtures are not fixed first, the experiment measures fixture defects, not the lever.

## 2. Experiment 1: one observation, many actions (the gap-closer)

This is the experiment the structures crawl says does not exist in the literature. It is the first thing we run, because it attacks the 87.8% directly and because every other lever (tree observation, code-exec) is confounded with it unless it is measured alone.

### 2.1 Hypothesis (falsifiable)

Batching independent actions into one model turn, executed from a single observation, reduces median wall time per task by at least 30% with no drop in pass rate and no increase in recovery steps, compared with the current one-action-per-observation loop on the same frozen test cases.

### 2.2 Test cases (frozen before the first run)

Use only cases whose fixtures are fixed and whose checkers read the DOM directly. Freeze the case list, the fixture versions, and the checker code in one commit before any run, and record the commit hash in every run report. No case may be edited between baseline and treatment runs.

Primary measurement set (long, fcc-k, after fixture fixes):

- f01 spreadsheet formula (70 scripted steps, the longest case, the strongest signal)
- f03 calendar conflicts (fixture gap fixed, event rendered in grid, state on window, not top-level let)
- f04 research notes (typing UI present, facts checkable from DOM)
- f09 copy format convert (source has 4 rows as specced, target input present)

Control set (short, clone1, already passing):

- t03 long form (14 fields, empty-submit errors)
- t10 login plus upload plus download (end to end, report file correct)

Excluded until fixed: f06, f07, f08, f10 (BLOCKED, dead buttons or no UI), f02, f05 (fixture gaps not yet closed). Excluding them is a scope decision recorded here, not a silent drop. If a fix lands mid-experiment, the case joins the NEXT experiment, never the running one.

### 2.3 Baseline method (A) vs new method (B)

Method A, baseline, current loop:

- One model turn produces one action.
- One fresh screenshot observation per action.
- Verification is a DOM read at the end of the task.

Method B, treatment, one observation many actions:

- One model turn produces a batch of independent actions (all actions whose preconditions are already visible in the current observation, no action that depends on the result of another action in the same batch).
- The batch executes without a fresh observation between actions.
- One verification observation (DOM read, plus one screenshot only if the DOM check is ambiguous) at the end of the batch, and a full screenshot plus DOM read at the end of the task.
- On any batch failure, the runner stops, takes one observation, and replans from the observed state. The failed batch and the recovery steps are logged as recovery cost, not hidden.

What B does NOT change, so the comparison is clean: same model, same harness, same fixtures, same checkers, same laptop, same Zen session shape, same settle rules (1 s after navigation, 0.5 s after switch, from RUN-REPORT-20261121.md). The ONLY difference is batching. Tree-first observation and code-exec substitution are separate experiments (sections 4.2 and 4.3) and are NOT mixed into B.

### 2.4 What to measure (per run, per case)

Every run records, in the run log JSONL (schema in section 3):

- wall time per case, start to verified end state, in ms
- tool calls per case (counted from the transcript, not estimated)
- observations per case, split by type (screenshot vs DOM/tree read)
- actions per observation (mean and max per case)
- pass or fail, verified by the DOM checker, never by the agent's own claim
- recovery steps per case (steps spent fixing a failed batch or a wrong action)
- stall minutes per case (minutes with no progress marker, see section 3)
- tokens per case (input and output separately, see section 3.6 for the collection caveat)

### 2.5 Pass threshold and go/no-go rule

Pre-registered before the first run. No threshold may be moved after seeing results.

GO (adopt batching as the default loop) only if ALL of these hold on the primary set:

1. Median wall time per case in B is at least 30% lower than median wall time in A, computed per case then averaged across the 4 primary cases.
2. Pass rate in B is equal to or better than in A on the same cases (no case that passed in A fails in B).
3. Median recovery steps per case in B is not higher than in A.
4. Actions per observation in B reaches at least 2.5 mean on the primary set (if the agent cannot actually batch, the wall-time win, if any, came from something else and the experiment is inconclusive, not a pass).

NO-GO if any one of the four fails. A NO-GO means batching is not adopted, and the run report says so plainly. A partial win (for example faster on f01 only) is reported as a partial win with per-case numbers, and the decision is NO-GO for default adoption, with an optional follow-up experiment scoped to the winning case type only.

### 2.6 How many runs

- Primary set (f01, f03, f04, f09): 3 runs per method per case. That is 12 baseline runs and 12 treatment runs. f01 at about 40 min hand-driven per run is the cost driver; 6 runs of f01 is about 4 hours of agent time, which must be scheduled, not squeezed into one sitting.
- Control set (t03, t10): 5 runs per method per case. Short cases are cheap and give a tighter median.
- Total: 24 primary runs plus 20 control runs, 44 runs.
- Runs alternate A, B, A, B per case to cancel time-of-day and machine-load drift. Never run all of A first and all of B second.
- If a run is invalidated (fixture flake, Zen restart, SSH drop, watchdog kill), it is logged as INVALID with the reason and re-run once. Two invalidations of the same case-method pair stop that pair and the report says the pair is UNMEASURED, not silently replaced by a good run.

### 2.7 Who runs it

Generators never run their own tests. The baseline and treatment runs are executed by an independent runner who did not write the batching method, using the frozen cases and the pre-registered thresholds. A second independent checker (or the same runner's DOM checker, never the agent under test) verifies each end state. This is the standing rule, restated because it is the load-bearing anti-self-grading control.

## 3. Metrics tracked on every run from now on

Six metrics, no more, no fewer, until an experiment justifies adding one. Every realistic-test run report must carry all six, per case and as a run total. A run report missing a metric says UNMEASURED for it, never a guessed number.

### 3.1 Wall time per task (headline metric)

- Definition: milliseconds from the first action of the task to the verified end state (DOM checker pass), including all thinking, all observations, all recovery, and all settle sleeps. Excludes fixture setup before the first action and teardown after verification.
- Collection: the runner logs a wall-clock timestamp (Asia/Ho_Chi_Minh) at task start and at verification, plus a monotonic elapsed timer per step. The existing per-step JSONL log (`/tmp/worker-p-live.jsonl` pattern in RUN-REPORT-20261121.md) is the collection point; add start and verify timestamps to it. Do not use the agent's self-reported duration.
- Why headline: METR (see section 5) shows felt speed and measured speed diverge by about 40 points. Wall time is the only number that cannot be felt into existence.

### 3.2 Tool calls per task

- Definition: count of tool calls the agent issued for the task, from the session transcript, including failed calls and retries. One batched turn that emits 4 tool calls counts as 4.
- Collection: counted from the transcript or the runner log after the run, by a script, not by the agent counting its own calls. Report the count alongside the median wall time, so a wall-time win bought by more calls is visible.
- Target direction: down, but only together with wall time. Fewer calls with the same wall time is a null result, not a win.

### 3.3 Tokens per task (input and output separately)

- Definition: input tokens and output tokens consumed by the task, as reported by the model session. Input includes re-sent context, which is the dominant cost (see below).
- Collection: read from the session usage record after the run. Caveat, stated plainly: if the session does not expose a per-task token count, report tokens as UNMEASURED for that run and use tool calls as the cost proxy. Never estimate tokens as calls times a constant; that fabricates a number. The background fact that motivates tracking it is measured elsewhere: a typical 50-turn session burns about 1,000,000 input tokens and 40,000 output tokens, a 25:1 ratio, and re-sent context is about 62% of the bill at production teams audited in 2026 (tokenade.net, Claude Code token usage statistics 2026, about 2026-10-16, accessed 2026-11-21, compiled, mixed verification, Uber figure secondhand and UNVERIFIED here). Our own loop re-reads context on every tool call, so input tokens, not output, are where batching should save money.
- Target direction: input tokens down per task. If wall time falls but input tokens rise, the lever is a speed-for-cost trade, and the report must say so.

### 3.4 Observation cost (per observation, by type)

- Definition: for each observation, its type (screenshot, DOM read, ARIA/tree read, or combined) plus its wall time in ms and its token cost where known. Reported as a per-case total and as a mean per observation, split by type.
- Collection: the runner logs every observation with type, start timestamp, and end timestamp. Screenshot encoding alone costs about 0.8 s per shot (olliebot docs, Specialized Computer Use Models Research, date UNVERIFIED, accessed 2026-11-21, secondhand table, verify before quoting externally), and a pruned ARIA snapshot is claimed at about 320 tokens vs a full-HD PNG vision loop at about 2,400+ tokens (SyndiPath, 2026-11-08, accessed 2026-11-21, vendor blog, measurement claim, exact multipliers UNVERIFIED until we measure them on our own stack). Our own numbers replace both claims once Experiment 2 runs. Until then, both are cited as claims, not facts.
- Target direction: fewer observations per task, and cheaper observations per action. Observation cost is the diagnostic that tells us whether a wall-time win came from batching (fewer observations) or from something else.

### 3.5 Verification cost (separate from production cost)

- Definition: wall time plus tool calls plus tokens spent verifying the end state, counted separately from the time spent producing it. Includes DOM checks, screenshot checks, independent-runner re-runs, and human review minutes where a human reviews.
- Collection: the runner logs verification as its own timed phase with its own start and end timestamps. Human review minutes are logged by the reviewer, not estimated after the fact.
- Why separate: verification is a budgeted stage, not a free check. The Verification Complexity Ratio (VCR, time to verify divided by time to produce) framing comes from AWS Builder, "When Human-in-the-Loop Becomes Theater", 2026-05-29, accessed 2026-11-21, anecdotal field observation, thresholds are pragmatic cutoffs from three deployments, not theory. VCR under 0.5 means human review is fine, 0.5 to 1.0 is on the edge, at or above 1.0 the review is theater: a 200-line change produced in 15 seconds approved in 20 seconds means nothing real was verified. Our version of the rule: if verification costs as much as production, the check is theater, and the run report must show the ratio. Also count review minutes in cost per task (qa.tech, "The Full AI Cost of Shipping a Feature", figures checked 2026-11-16, accessed 2026-11-21, vendor figures plus surveys): token spend on generation is the only stage with a clear invoice line, the other three stages (generate, review, verify in the running product, watch in production) have no public benchmark for what they should cost, so we measure them ourselves instead of assuming they are free.

### 3.6 Stall minutes (progress, not liveness)

- Definition: minutes in a run during which no progress marker advances. Progress markers are steps completed, artifacts written, or checker states changed. Process-alive, heartbeat-OK, or token-consumed do NOT count as progress.
- Collection: the watchdog (separate process, polls every 5 min, acts after 15 silent min, reports to Muse not to the coordinator, per standing rule) logs last-progress timestamps from the run log. Stall minutes per case equal wall time minus time covered by progress markers. The pattern matches the published guidance: a walking-dead agent passes every liveness check while producing no durable progress, and detection requires a progress signal, not a heartbeat (baeseokjae.github.io, "Agent Walking-Dead State Detection", about 2026-09-23, accessed 2026-11-21, practitioner guide citing a real preprint scan of 6,549 repos with 68 infinite-loop failures confirmed across 47 projects, secondhand count). Our own history justifies it: clone2 stalled 70+ min once, fcc K2 died twice with zero output, agy Q2 timed out at 10 min at 4/10, coordinator #2 was flagged at 04:14 and killed at 04:36 (INTERNAL, 2026-11-21). A stall that is not measured is a stall that repeats.
- Target direction: zero stall minutes on a completed run. Any run with stall minutes above 0 reports them, and a run killed by the watchdog reports its stall minutes up to the kill, not zero.

### 3.7 Run-log schema (minimum fields, one JSON object per step)

Every realistic-test run appends to a JSONL log with these fields per step, so the six metrics are computed by script, not by hand:

- run_id, case_id, method (A or B), run_index, agent (who ran it), started_at (wall clock Asia/Ho_Chi_Minh), step_index, step_type (think, observe, act, verify, recover), observation_type (screenshot, dom, aria, none), action_count (actions in this turn), machine_ms, wall_ms, tokens_in (or null), tokens_out (or null), progress_marker (true or false), note.

A run whose log is missing is an UNMEASURED run, and its result does not enter any median.

## 4. Ranked list: what to try first, second, third

Ranked by evidence strength and by how directly each attacks the 87.8%. Each is a falsifiable experiment with a pre-registered go/no-go rule. No experiment starts until the previous one's go/no-go is recorded, unless the parent explicitly orders parallel runs on disjoint cases with separate runners.

### 4.1 FIRST: one observation, many actions (batching)

- What: section 2 in full. Batch independent actions per turn, one observation per batch, verify at batch end and task end.
- Why first: it is the gap the crawls name, it attacks the 87.8% at its root (fewer loop iterations), and the published support, while indirect, is the strongest of the three. Batching evidence: LLMCompiler-style DAG scheduling measured 1.8x latency reduction on HotpotQA and up to 3.7x on parallelizable workflows, up to 6x cost reduction from fewer LLM inference calls (Zylos, 2026-04-26, accessed 2026-11-21, measured, cited ICML 2024 numbers, OLDER). Production multi-agent pipelines: 36-50% wall-clock reduction from fan-out and fan-in (same source). Qwen-UI-Agent: more than 40% of action outputs executed in batches, 58.4% and 21.7% fewer steps per task than MiniMax M3 and Qwen 3.7 Plus respectively (blog summary 2026-07-31, accessed 2026-11-21, OUTSIDE WINDOW, kept for batching numbers only). HCU: accessibility tools execute actions in batches and report effects as AX diffs, so the model needs fewer round trips; highest Partial and Binary scores on OSWorld 2.0, 72.37% Partial with GPT-6 Astra (arXiv 2610.41432v1, October 2026, accessed 2026-11-21, MEASURED). None of these is a standalone A/B of batching alone on a desktop GUI task, which is exactly why our experiment matters.
- Cost: 44 runs (section 2.6), dominated by 6 f01 runs at about 40 min each.
- Go rule: section 2.5, all four conditions. GO means batching becomes the default loop and the runner guide is updated to a deterministic rule (Lauren Tan's rule: a repeated pattern becomes a rule, not a reminder).
- No-go rule: any one of the four conditions fails. NO-GO means batching is not adopted, the report records the per-case numbers, and we move to Experiment 2 without re-litigating Experiment 1.

### 4.2 SECOND: tree-first observation, screenshot only for verification and recovery

- What: change the observation, not the action count. Method A observes by screenshot every iteration. Method B observes by DOM or ARIA tree every iteration, and takes a screenshot only for end-of-task verification and for recovery when the tree and the task state disagree. Batching stays at the Experiment 1 outcome: if Experiment 1 went GO, B includes batching; if it went NO-GO, B uses one action per turn so the observation change is measured alone. Never change two levers in one experiment.
- Hypothesis: tree-first observation reduces median wall time per task by at least 20% with no drop in pass rate, compared with screenshot-every-iteration on the same frozen cases.
- Test cases: same frozen set as Experiment 1 (f01, f03, f04, f09 primary; t03, t10 control), same run counts (3 per method per primary case, 5 per method per control case), same alternation, same invalidation rule.
- What to measure: the six metrics in section 3, with observation cost (section 3.4) as the diagnostic. The prediction is that observation cost per task falls sharply while actions per observation stays flat, which is how we know the win came from the observation and not from batching.
- Go rule: GO only if median wall time falls at least 20% AND pass rate is equal or better AND median recovery steps do not rise. NO-GO otherwise. The 20% bar is lower than batching's 30% because the published multipliers are weaker evidence: ARIA about 320 tokens vs vision 2,400+ tokens and 0.4-0.9 s vs 2.8-5.5 s per action (SyndiPath, 2026-11-08, vendor blog, UNVERIFIED multipliers), DOM 15 s vs vision 75 s on the same task (olliebot docs, date UNVERIFIED, secondhand table), and the same-model harness gap of 3.0x median, 38.2 s vs 12.7 s (PureTensor, 2026-09-26, accessed 2026-11-21, MEASURED live bake-off, 39 tasks, one run each, top four setups cannot be separated on this sample). MobiBench supports hybrid input over screenshot-only: GPT-4.1 scored 27.17% task success on tree, 4.72% on screenshot only, 31.50% hybrid (508 tasks, 66 apps, arXiv 2512.12634, accessed 2026-11-21, MEASURED). The honest reading is that tree-first should help, but the exact size is unknown until we measure it, so the bar is set at a level a real effect should clear and a placebo should not.
- Risk to watch: tree-only observation can miss visual state (a popup that exists in the DOM but is not visible, a layout shift). That is why screenshots stay for verification and recovery, and why any pass-rate drop is an automatic NO-GO even if wall time falls.

### 4.3 THIRD: code-exec and CLI substitution for GUI steps

- What: replace GUI steps with code or CLI wherever the step can be done that way, and measure the agent loop against the scripted floor. Method A is the winning loop from Experiments 1 and 2 (or the baseline if both went NO-GO). Method B is the same loop, except steps that have a code or CLI equivalent are executed as one code-exec call instead of a sequence of GUI actions. The scripted floor is already known for the control set: t01 scripted is 2,678 ms vs about 7 min hand-driven, a 157x gap (INTERNAL). The experiment asks how much of that gap code-exec closes on the agent loop, not whether scripted code is faster (it is, that is already proven).
- Hypothesis: code-exec substitution reduces median wall time per task by at least 25% on cases with at least 5 substitutable steps, with no drop in pass rate.
- Test cases: f01 (formula entry and verification are DOM operations, many steps substitutable), t03 long form (14 fields, typing via DOM instead of clicking each field), t10 (upload plus download plus report, file operations via CLI where the fixture allows). f03, f04, f09 join only if they have at least 5 substitutable steps each; otherwise they are reported as not applicable for this experiment, not forced in. Same run counts as Experiments 1 and 2 for the cases that qualify.
- What to measure: the six metrics in section 3, plus a seventh diagnostic for this experiment only: substitutable-step share (steps replaced by code-exec divided by total steps). If the share is under 30%, a wall-time win cannot be attributed to substitution and the experiment is inconclusive.
- Go rule: GO only if median wall time falls at least 25% on qualifying cases AND pass rate is equal or better AND recovery steps do not rise AND substitutable-step share is at least 30%. NO-GO otherwise.
- Evidence it leans on: scripted selectors under 50 ms per step vs 800-2,500 ms per step for vision GUI agents, a 16x-50x per-step gap (UI-TARS Desktop writeup, about 2026-10-18, accessed 2026-11-21, measurement claim, secondhand table, numbers not independently verified). OpenBot research notes: "Speed comes from collapsing the loop. The biggest lever is not a faster model, it is replacing N screenshot-to-click round trips with one code call that performs many actions" (last updated 2026-09-16, accessed 2026-11-21, benchmark numbers measured, lever ranking is the author's synthesis, not a controlled experiment). Our own standing rule already says CLI first, then code-exec, then vision; this experiment measures how much that rule is worth on our cases instead of assuming it.
- Boundary: code-exec substitution is a measurement experiment, not a license to bypass the UI under test. A step is substitutable only when the fixture exposes the same operation the user performs (typing a field, submitting a form, reading a value). Reaching into fixture internals to set the expected end state directly is fabrication of a pass, not substitution, and any run that does it is invalid.

### 4.4 Backlog (not ranked for now, listed so they are not forgotten)

- Step cap plus early stop: reliability collapses within about 16 steps (Mittal, "How Fast Do Agents Rot?", about 2026-09, accessed 2026-11-21, MEASURED, n=10,664 trajectories, near-perfect to near zero within 16 steps, degradation driven by step count not context length). A loop that cannot finish in 16 steps should replan or escalate instead of grinding on. This becomes an experiment only after Experiments 1-3, because batching changes the step count and would confound it.
- Context compaction discipline: bounding the context window steepened decay in the same study (logit slope -0.69 vs -0.44), so compaction is not a free win. Measure before adopting.
- Parallel lanes: expect 1.5x, not Nx. Stackness measured effective parallelism 1.21 overall, 1.46 in the busiest window, 1.82 in a six-agent 106-task run, about 0.3x the agent cap, across 364 timed runs (2026-11-11, accessed 2026-11-21, MEASURED, single repo and developer caveat). Two lanes is the honest default. This is an org question, not a loop question, so it waits until the loop is measured.

## 5. How to avoid fooling ourselves

### 5.1 The METR lesson: felt speed is not measured speed

METR randomized controlled trial, Becker et al., July 2025, re-analysis arXiv October 2026, CACM summary 2026-11-09, all accessed 2026-11-21, MEASURED, the strongest evidence in the bottlenecks crawl: 16 experienced open-source developers, 246 real issues, Cursor Pro with Claude 3.5 and 3.7. Tasks took 19% longer with AI (95% CI +2% to +39%). Developers predicted a 24% speedup beforehand and still believed they were 20% faster afterward. The perception gap is about 40 points. Re-analysis: slowdown of 19% or 24% depending on estimand (34% unadjusted), AI helped on somewhere between 3% and 82% of issues. METR February 2026 follow-up (57 developers, 143 repos, 800+ tasks) estimated an 18% speedup for returning developers (CI 38% faster to 9% slower) and 4% for new ones, but METR itself calls the signal unreliable due to selection bias (30-50% avoided submitting tasks they expected AI to speed up, pay dropped $150 to $50 per hour). Scope: experienced maintainers in their own large codebases, early-2025 tools. Do not generalize to all developers or current tools, but do not dismiss it either.

Our rule from it: wall time (section 3.1) is the only speed claim that counts. Any sentence of the form "it felt faster" is recorded as perception, never as evidence, and is kept in a separate line of the run report from the timed numbers. If a runner reports feeling faster while the timer says slower, the timer wins and the report says so.

### 5.2 Verification theater

Section 3.5 states the VCR rule. Two more concrete controls:

- The agent under test never verifies its own work. Verification is by DOM checker or independent runner, never by the agent saying "done". This is Lauren Tan's rule from the clip, and it is also the standing rule that generators never run their own tests.
- A run report must show verification cost next to production cost. If verification took longer than production, the report flags VCR at or above 1.0 and the pass is treated as expensive, not free.

### 5.3 Self-grading and reviewer approval

- Agent reviewer approval is not evidence. Swarm-tax experiment (programmingtheloop.com, 2026-10-26, accessed 2026-11-21, MEASURED, 144 runs, pre-registered hypotheses): every time an agent reviewer approved a change, the change failed hidden tests, 24 of 24 approvals. One agent passed 56.8% of hidden tests, planner-coder-reviewer team passed 25.7%. Giving every team member the task file raised the team to 54.1%. Our controls: every worker reads the ORIGINAL brief, never a coordinator summary; every pass is checked against hidden acceptance tests (the DOM checker), not against a reviewer's approval.
- The 2,124-run sub-agent benchmark (read via news summary, aicoder.com, about 2026-11-20, accessed 2026-11-21, numbers as reported by the study author, underlying study not read): enabling sub-agents dropped Claude Code's solve rate from 83% to 59% and latency rose from 17.5 to 27.8 minutes, token consumption inflated 1.41x to 3.31x. Treat as reported, not independently verified. It reinforces the same point: more agents and more review do not by themselves mean better results.

### 5.4 Pre-registration and frozen cases

- Thresholds, case lists, fixture versions, and checker code are frozen and committed before the first run of each experiment. The commit hash goes in every run report.
- All runs are reported, including failures, invalidations, timeouts, and watchdog kills. A median computed from only the successful runs is fabrication by selection. The fcc K2 zero-output deaths and the agy Q2 10-minute timeout are reported in the baseline for exactly this reason; they are data, not embarrassment to hide.
- No threshold moves after seeing results. If a threshold was wrong, the experiment is re-run as a new pre-registered experiment with the corrected threshold, and the old one stays NO-GO.

### 5.5 Handoff loss

- Handoffs lose information mostly through repeated compression, not through changing agents (zicq.com summary of handoff paper, about 2026-11-17, accessed 2026-11-21, MEASURED experiment, secondhand summary, 70-82% recovery figure reported not independently verified): a chain of eight agents inheriting a 300-character note reaches only the learning level a persistent agent reaches after about four lives. Rewriting each note from the complete record instead of from the previous note recovers 70-82% of the lost learning at the same budget.
- Our rule: every experiment handoff (brief, run report, go/no-go) is written from the full run log, not from the previous summary. A coordinator summary is never the source for the next worker's brief; the original brief and the raw log are.

### 5.6 What this paper does NOT claim

- Our 87.8% think-observe-think share is INTERNAL only. No crawled source confirms the split. It stands as our number until an experiment measures the split directly (a time-motion split of think vs observe vs act per step, which is a follow-up measurement, not part of Experiments 1-3).
- The SyndiPath multipliers (7.5x tokens, 4x latency), the olliebot 15 s vs 75 s pair, and the tokenade Uber figure are UNVERIFIED secondhand claims. They motivate experiments; they are not facts in our reports.
- The Lauren Tan numbers (3,000 PRs in a month, team 11,000 PRs at about 0.5% revert rate) are self-reported by SpaceX (xAI), a vendor selling Grok Bot, and the talk ends with a pitch for Grok Bot. Treat as the team's own claim, not an audited fact (clip file, accessed 2026-11-21). The method transfers; the headline output does not, without the token budget and model strength the clip's own comment thread flags.

## 6. Recommended order of work (for the parent coordinator)

1. Fix the fcc-k fixtures and replace `__fcckVerify()` self-simulation with DOM assertions (precondition, not an experiment). Record the fixing commit.
2. Freeze the Experiment 1 case list and thresholds, assign an independent runner, run the 44 runs alternating A and B.
3. Record the go/no-go for Experiment 1. If GO, update the runner guide to a deterministic rule. If NO-GO, record the per-case numbers and move on.
4. Run Experiment 2 (tree-first observation) with the batching outcome held fixed.
5. Run Experiment 3 (code-exec substitution) on qualifying cases only.
6. After all three, re-measure the 87.8% split directly with a time-motion log, and only then update the headline number.

## Work log (Asia/Ho_Chi_Minh, wall clock plus elapsed)

- 17:51, T+0min: task received. Read the three crawl files (clip, structures, bottlenecks).
- 17:52, T+1min: read tests/realistic/RUN-REPORT-20261121.md and listed the realistic test directory, confirmed branch todolist-push.
- 17:52-18:10, T+1-19min: wrote this paper, committed, pushed.

## Files

- This paper: improvements/worker-w-council-c-measurement-20261121.md (repo computer-use-wayland, branch todolist-push)
