# Council Member 1 verdict: Worker Y11 think-time instrumentation design

- Role: Council Member 1, debating one question: what counts as think time, and is the proposed think boundary honest or vacuous?
- Work log (wall-clock Asia/Ho_Chi_Minh): task received 2026-11-21 18:52:40. Files read 18:52 to 18:54 (worker-y3-fcc-verification.md lines 233 and 253 area, scripts/timing.py full, tests/realistic/run_live.py Runner.step and WD, tests/realistic/hand_drive.py full, tests/test_timing.py full). Grep verification 18:54 (zero production imports of TimingLogger confirmed; 208 r.step() calls in run_live.py). Verdict written 18:55. Total elapsed about 3 minutes.
- Rules observed: no ydotool, no em dash or en dash anywhere in this file, no personal info, no git commands, no pushes.

## Verdict: AMEND

The design is fixable, but as proposed it is unshippable for its stated purpose, which is closing H2. Amendment 1 below is non-negotiable. If Y11 keeps think_s = 0 rows for scripted steps and counts them as H2 evidence, this verdict flips to BLOCK, because that is exactly the failure Y3 documented: an instrument that exists on paper while the headline goal stays unmeasured.

## The single weakest point

Think time is defined into existence. Runner.step wraps fn, calls act() immediately, and the interval from think_step entry to act() is microseconds of Python function-call overhead, not a decision. The design then labels that interval "think_s ~ 0" and the step duration "act_s". Nothing about the agent's thinking was observed. The same file that would close H2, run_live.py, already states in its own docstring that per-step wall time is DOM-driver machine time, NOT agent think time. Relabelling the same duration as think 0 plus act N does not change what was measured. 208 r.step() calls in run_live.py would emit 208 fabricated zeros, and TimingLogger.summary() would report think_median_s near 0.000 as a headline number. That is worse than the current state, where H2 is openly unmeasured. It replaces an honest gap with a dishonest zero.

A second fabrication rides along with it, and it is just as bad. _ThinkStep.__enter__ in scripts/timing.py calls self.logger.note_model_call() unconditionally. Wrapping 208 scripted steps would therefore log model_calls = 208 for a run in which zero model calls happened. pace() would then compute actions_per_call from fake calls. The design manufactures both headline numbers at once.

## Q1. Is think_s ~ 0 for scripted steps honest evidence or vacuous wiring?

Vacuous wiring. Evidence, from the files:

- run_live.py Runner.step times fn() with time.perf_counter and logs elapsed_ms as machine time. The docstring says this is the floor under any agent run, not agent think time. The proposed design keeps fn() identical and only adds a think_step wrapper plus an immediate act() call. No new observation is introduced anywhere in the chain.
- timing.py _ThinkStep.__exit__ computes think_s as act_start minus think_start. If act() is called immediately after entry, think_s is the time to execute two Python statements. That measures the harness, not the agent.
- A scripted run has no decision at all: the decision was pre-written by the test author days earlier. There is no think event in the run to measure. Recording 0 for a non-event is not a measurement, it is a placeholder that a later reader will mistake for a measurement, because summary() aggregates think_s into think_median_s and think_max_s with no source filter.

What would make it honest:

- Scripted steps record think_s as null, not 0, with think_source = "scripted", and act_s = the step duration. Null says "no think event exists here". Zero says "thinking took no time", which is false: the thinking happened in the test author's head, outside the run.
- summary() must compute think medians over agent-source steps only, and report null when there are none. A scripted run's summary must not contain a think_median_s at all.
- H2 stays open until a real agent-driven run produces think rows. Scripted rows alone never close H2, no matter how many of them exist.

## Q2. Where does the think boundary belong: Runner.step, the WD action methods, or the caller?

The boundary belongs where the first action is issued, which is the caller for agent runners and the WD action methods as the enforcement point for scripted and driver runs. It does not belong in Runner.step.

- Runner.step cannot know when a decision ends. It only knows when fn() starts. If Runner.step calls act() immediately before fn(), the split is tautological (see Q1). If Runner.step never calls act(), the timing.py default fires: __exit__ counts the whole step as think (timing.py docstring: "If never called, the whole step counts as think time, which is honest: a step that never acts was all thinking"). That default is wrong in the opposite direction for this harness. A scripted wait_for polling step with a 10 second timeout would log 10 seconds of "think". A download poll step would log think time while the machine waits for a file. The default is only honest for a step that is pure decision, and most steps in run_live.py are not.
- The WD action methods (click, type_text, eval, set_file, click_js, alert_accept, and the rest) are the choke point where execution actually starts, and WD is shared across run_live.py, run_agyq2.py, run_agy_y2.py, run_fcck.py, run_agyq.py, and the probe scripts. Putting the act() mark inside the WD methods gives every runner the same boundary. Putting it in Runner.step covers only run_live.py Runner users and leaves direct WD users (probes, diag scripts) with nothing.
- But WD alone is not enough for agent runners. For a future agent runner, think_step must open when the observation is delivered to the agent, and act() must be called by the agent loop when it issues its first action after a model call. WD can mark act start as a fallback (first WD call inside a step), but the agent loop owns the boundary, because only the loop knows when the model call returned and the decision was made.

What breaks if nobody calls act():

- Every step becomes think_s = total, act_s = 0. summary() then reports think_median_s equal to the total-time median, which is machine time mislabelled as think.
- Any step over 60 seconds flags slow_think, including waits, polls, and downloads. The SLOW_THINK flag becomes noise, and a real slow decision drowns in false positives.
- The pace ratio is unaffected by act(), but the per-step slow_think flag and the pace() "slow_think" key (see Q5) both fire for reasons that have nothing to do with thinking.

Additional problem the design must address: the step taxonomy in run_live.py mixes observation steps and action steps. "read confirmation" (text), "read rows" (text), "check td click selected nothing" (eval), and "wait confirmation" (wait_for) are observation or polling, not actions. A read is input to the next decision, not execution of the current one. A wait is machine polling. Neither is cleanly think or act. The design needs an op-kind tag on each step and a rule: wait and poll steps are act (machine time) or excluded from think aggregates, never counted as think. Without that rule, the think/act split is applied to steps where the split has no meaning.

## Q3. For hand_drive, is the inter-command arrival gap a fair definition of think time?

No, not as a definition of think time. It is a fair definition of one thing only: an upper bound on think time at the harness boundary, contaminated by at least three other components. Evidence from hand_drive.py:

- The docstring says "The AGENT types each command by hand and times its own thinking between commands". Typing JSON by hand is part of the gap. Typing speed, typos, corrections, and paste delays all land inside the measured interval. A slow typist looks like a slow thinker.
- The gap runs from the previous result print to command N's arrival on stdin. Between those two points sit: the agent reading the result (real think), the agent's own scheduling latency (a separate process or subagent waking up, tool-call overhead, model queueing when the agent waits for a model call between commands), and the human operator's typing time. The harness cannot separate these from its side of the pipe. Model queueing is not thinking, scheduling latency is not thinking, typing is not thinking.
- The first command has no previous result, so its gap is undefined. The design must record it as null, not as zero and not as time since driver start.
- Multi-command decisions split one decision across two gaps. A find followed by a click is one decision (where is the button, click it) executed as two commands. The gap between the find result and the click arrival is think for the click, but the gap between the click result and the next find arrival is think for the next decision. The boundary between "thinking about this command" and "thinking about the next command" is not observable from arrival times alone. An agent can also decide while the previous command is still executing (pipelining), in which case the arrival gap undercounts think.

How to separate, if at all:

- Record three timestamps per command: result printed (t_print), command bytes fully received (t_arrive), command execution start and end (t_exec). Report boundary_gap_s = t_arrive minus t_print, labelled exactly that, never labelled think_s. It is an upper bound on think, not think.
- To claim real think time, the driver must self-report: the agent includes a decided_at timestamp (when it finished deciding, before it started typing) or a model_calls count in each JSON command. Then think_s = decided_at minus t_print, and typing_s = t_arrive minus decided_at. Without a self-reported decided_at, the harness cannot split typing from thinking, and must not pretend it can.
- Log the operator kind per session (human-typed vs agent-driven). A human-typed hand-drive session has zero model calls and its gap is mostly typing. An agent-driven session has model calls and its gap is mostly think plus queueing. Mixing the two in one aggregate is meaningless.

## Q4. Who calls note_model_call() in each run shape, and what does actions_per_call mean when the count is 0 or undefined?

- Scripted runs: nobody. A scripted run makes zero model calls. The count must stay 0, and pace() must report actions_per_call as null. Today pace() does `calls = self.model_calls or 1`, which silently substitutes 1 for 0. A scripted run with 6 actions would report actions_per_call = 6.0, a fabricated number that looks like excellent pace. The `or 1` must go. When model_calls is 0, actions_per_call is undefined, not 0 and not actions divided by 1.
- Hand-drive: the harness cannot know. Only the driving agent knows how many model calls it made between commands, and a human operator makes none. The driver must self-report a model_calls delta per command (a field in the JSON command), or the run records model_calls as null. The harness must never infer model calls from command count: one command is not one model call, and one model call can produce several commands.
- Future agent runners: the agent loop calls note_model_call() once per model invocation, explicitly, before opening think_step. It also calls note_action() once per action issued. This is the only shape where actions_per_call has its intended I16 meaning: fewer than one action per model call over a window flags thinking without doing.
- The auto-call in _ThinkStep.__enter__ must be removed or made opt-in. As written it double counts for agent runners (loop calls it, then think_step calls it again) and fabricates calls for scripted runs. The unit test test_pace_flags_few_clicks_many_calls calls note_model_call() explicitly and passes either way, so removing the auto-call breaks no tested behaviour. The tests that use think_step (test_think_act_split_is_measured, test_slow_think_flagged_over_60s, test_summary_flags_small_task_over_5_min) never assert model_calls, so they are unaffected.
- actions_per_call when the count is 0 or undefined: null, with pace() also reporting slow_think (the ratio flag) as null, not False. Reporting False would claim "pace is fine" on evidence that does not exist.

## Q5. Is the SLOW_THINK 60s flag meaningful for scripted runs, or should it be suppressed when think_source is scripted?

It should be suppressed when think_source is scripted, and suppressed whenever think_s is null. For scripted runs the flag is meaningless in both directions:

- With the proposed immediate act() call, think_s is ~0, so the flag never fires. Its silence proves nothing and a reader will misread "0 slow steps" as "no slow thinking".
- With act() never called, the whole step counts as think, so any wait, poll, or download over 60 seconds fires the flag with no thinking involved. Its firing proves nothing either.

There is also a naming collision that will confuse every reader. timing.py uses "slow_think" for two different predicates: _finish_step sets row["slow_think"] when think_s is over SLOW_THINK_S (a per-step time flag), while pace() returns "slow_think": ratio smaller than MIN_ACTIONS_PER_CALL (a run-level pace flag). A run can have slow_think True from pace with zero slow steps, or slow steps with pace slow_think False. One of the two keys must be renamed, for example pace() returning "low_pace" instead of "slow_think". This is a small fix but it prevents exactly the kind of misreading this council exists to catch.

Note also that summary() computes think_median_s as sorted[mid], the upper median for even counts. That is a minor bias, not a blocker, but worth a comment in the code if Y11 touches summary() anyway.

## Exact amendments required (AMEND, not APPROVE)

1. Scripted steps record think_s = null, think_source = "scripted", act_s = step duration, slow_think = null. Never 0. This amendment is non-negotiable; without it the verdict is BLOCK.
2. Remove the unconditional note_model_call() from _ThinkStep.__enter__ in scripts/timing.py, or gate it behind an explicit parameter. Model calls are counted only by an explicit caller. Fix pace() so model_calls == 0 yields actions_per_call = null and the pace flag = null. Delete the `or 1` substitution.
3. Runner.step must NOT call act() immediately before fn(). act() is called by the issuer of the first action: the WD action methods mark act start as the fallback, and agent loops call act() explicitly when they issue their first action after a model call.
4. hand_drive.py metrics mode records t_print, t_arrive, and t_exec per command, reports boundary_gap_s (an upper bound, never think_s), records the first command gap as null, and requires a driver self-reported decided_at or per-command model_calls to claim real think time. Log operator kind (human vs agent) per session.
5. Suppress the SLOW_THINK flag when think_source is scripted or think_s is null. Rename pace()["slow_think"] to "low_pace" to end the collision with the per-step slow_think flag.
6. H2 stays OPEN until at least one real agent-driven run (hand-drive with an agent operator, or a future agent runner) produces think rows with think_source "agent" or "hand-drive-agent". Scripted rows alone never close H2. summary() computes think medians over agent-source steps only, and reports null when there are none.
7. Tag each step with its op kind, and exclude pure wait, poll, and download steps from think aggregates. A wait is machine polling, not thinking, and not acting either; the design must state the rule rather than letting the split silently absorb it.

## What the design gets right

- Wiring TimingLogger into Runner.step is the right plumbing direction: one shared choke point, one JSONL file, the same log_step path every runner already uses. The plumbing is not the problem. The labels attached to the numbers are.
- The hand-drive metrics mode is the right place for the first real think measurement, because hand_drive.py is the only existing shape where a real agent decision happens between harness events. It deserves to be the H2 evidence path, with the boundary_gap discipline in amendment 4.
- Keeping think_source on every row is the right instinct and the thing that saves this design from being vacuous: once rows carry their source, a reader can tell a measured think from a placeholder. Amendment 1 is just that instinct carried to its conclusion.
