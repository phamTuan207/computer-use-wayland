# Phase 2.3, 2.4, 2.5 fixes - slow decisions, fabrication, no reporting

Date: 2026-11-21. Worker D. Sources: the 20/11 CF26 upload session
(A4-A8, G15-G18, G22, H2, I13-I30). Each item below names the code that
enforces it, so the rule is not a prompt line an agent can skip. It is a
function that returns a verdict, a report, or a refusal.

## 2.3 Slow decisions

- 2.3.1 (H2/I13) Think time is measured per step, split from act time.
  `scripts/timing.py`: `TimingLogger.think_step(name)` records think
  seconds (observation received to first action) and act seconds
  separately. A step over 60 s of think time is flagged `slow_think`.
  Shorter prompts and split decisions are the remedy to try first when
  the log shows think-dominated steps; the log, not a feeling, decides.
- 2.3.2 (I14) Step timeout is 3.5 min (210 s). `scripts/step_watchdog.py`:
  `StepWatchdog` reports STUCK the moment a step passes 210 s with no
  progress. No waiting for 5 min. The user set this on 20/11 at 18:06.
- 2.3.3 (I15) Progress heartbeat every 5 min (300 s). The same watchdog
  emits a HEARTBEAT report when 5 min pass with no progress line.
  Silence longer than 5 min is itself the failure.
- 2.3.4 (G22) Timing/logging is ALWAYS ON. `TimingLogger` has no off
  switch. A 3-6 operation task has a 300 s wall budget; `summary()`
  reports `over_small_task_budget` so versions compare on numbers.
- 2.3.5 (I16) Pace check: actions per model call. Under 1.0 means
  thinking, not doing (6 calls in 9 min, almost no clicks). `pace()`
  flags it. A live worker that is alive but not progressing is stuck,
  not busy.

## 2.4 Fabrication, wrong diagnosis

- 2.4.1-2.4.9 live in `scripts/claim_check.py`. One rule covers them
  all: a claim is assertable only with a named source and an access
  date. Anything else is answered with "I don't know" plus what would
  settle it. `ClaimCheck.assert_or_admit()` is the function to call
  before any factual sentence goes to the user or to a worker.
- 2.4.1 (A7/I17): "same browser required" was invented. Tripwire list
  blocks that shape without a verified source.
- 2.4.2 (I18): a rule's origin is recorded (`origin` field). A rule
  Muse wrote is never attributed to Hieu or to a tutorial.
- 2.4.3 (I19): a technical-sounding explanation for a miss ("native
  dialog", "separate window") is fabrication when the truth is "I
  aimed wrong and I don't know why it missed". Say that instead.
- 2.4.4 (I22): a subagent's diagnosis is relayed as "subagent X claims
  Y, unverified" until the screen or the primary source confirms it.
  `verify()` refuses an empty source.
- 2.4.5 (I23): follow the tutorial exactly. No invented step, no cut
  step, no reordered step. A step with no source in the tutorial is
  not a step.
- 2.4.6 (I24): read the tooltip before characterising an error.
  "Enumerated incorrectly" says "Package can not be built": a blocker,
  not a warning. Guessing severity is fabrication.
- 2.4.7 (I25): never claim to see an image the current channel cannot
  show. During a voice call there is no new image; only images already
  received exist, named explicitly. Counts are re-counted from the
  image actually in front of you.
- 2.4.8 (I26): research before suggesting. `check_tool_suggestion()`
  refuses a tool suggestion with no capability evidence (tool, target,
  proof it can drive that target). Zen is Firefox; Firefox has no CDP;
  Playwright cannot attach to a logged-in Zen tab.
- 2.4.9 (A8): every claim carries source + access date. That is the
  `Claim` record, not a style preference.

## 2.5 No blocker reporting, no monitoring, no killing

- 2.5.1 (A4/I28): `TaskChainMonitor` in `scripts/task_chain.py` polls
  the dependency and starts the next task the moment it finishes, then
  notifies. The check runs on schedule (every 5 min); it never waits
  for the user to ask.
- 2.5.2 (A5/I27): step stuck past 3.5 min reports immediately
  (`StepWatchdog`); worker with no progress past 15 min reports as
  stalled (`WorkerStall`). Retry silently is the failure.
- 2.5.3 (A6): a stuck agent is KILLED IMMEDIATELY, no asking first,
  and the user is told. `kill_stuck_agent()` does that for registered
  agents (idle past 15 min). Asking first is how a 73-hour silence
  happened.
- 2.5.4 (G16): the watchdog reports DIRECTLY to Muse.
  `DirectReporter` writes every report to a file the parent reads
  directly, plus stdout. It never routes through a coordinator: when
  the coordinator is the stuck part, a routed stall flag goes silent
  with it.
- 2.5.5 (G17): `watch_until_done()` polls every 5 min and reports
  completion at once. A dedicated watcher owns one job.
- 2.5.6 (G15): `launch_detached()` launches long-running processes
  fully detached (setsid semantics, stdin from /dev/null, output to a
  log file). The launcher verifies the process is alive, then ends its
  turn. An attached launch never completes and its final report never
  arrives. Restate this in EVERY worker brief that launches a
  long-running process.
- 2.5.7 (G18): Track 2 is PAUSED. `Track2Gate` (`docs/track2-gate.json`)
  refuses to run until the gate file records a unanimous council GO
  AND a unanimous redteam GO, each with a date. No self-judged stop,
  no silent resume.
- I28: same as 2.5.1 (monitor + notify on completion).
- I29: a pause order stops already-dispatched agents. `AgentRegistry`
  records every dispatched agent before it starts, so `pause_all()`
  has a handle on each one and reports which ones could not be
  stopped. A pause is not complete while any outcome is unresolved.
- I30: overnight results are queued in `PendingReport` and delivered
  whole at the morning check. The queue is a file, not memory, so a
  restart cannot lose the report.

## Worker-brief checklist (copy into every brief)

1. Timing is on: `TimingLogger` for the run, JSONL path named in the brief.
2. Watchdog is on: step timeout 210 s, heartbeat 300 s, worker stall 900 s.
3. Reports go to `DirectReporter`, never through another agent.
4. Claims carry source + date, or the answer is "I don't know".
5. Long-running processes launch with `launch_detached()` only.
6. Every dispatched agent is registered before it starts.
7. Track 2 stays PAUSED unless the gate file says GO.
