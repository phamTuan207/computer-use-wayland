# Council vote, Council Member 2 (speed / benefit lens): R3-L3 re-planned roadmap

- Date: 2026-11-24, 21:38 +07. Written the night before the run (25/11).
- Member: Council 2, speed / benefit lens.
- Vote: AMEND.
- Draft under vote: ~/workspace/r3-l3-replan-draft-20261124.md (11 sections).
- Sources read in full before voting: the draft; the execution plan ~/workspace/r3-l3-execution-plan-20261124.md (565 lines); the crawler research improvements/r3-l3-multiagent-coordination-research-20261124.md (commit f9e20bd); the complaints audit improvements/r3-l3-complaints-audit-20261124.md (commit 5a1d705, 132 incidents); the readiness check improvements/r3-l3-readiness-check-20261124.md (commit 73b49a5, 21 PASS / 3 FAIL / 3 PARTIAL); Codex runner input ~/workspace/codex-meeting-input-20261124.md (10 risks + 10 preventions); Clone1 key finding (run tab unload under memory pressure, adopted as F-21 / Z8).
- No long dash or en dash in this file. Commas, periods, short hyphens only.
- No credential value in this file. The R3-029 password lives in the run coordinator brief only, never in the repo.

## 1. What the draft gets right on speed and benefit (kept, no change)

1. The honest budget is kept: 19-31h, staffed for 31h, no promise of a 20h finish. The draft does not shrink the range to pay for its new preventions. Correct.
2. The 30-minute per-task timeout is kept and enforced. This is the single biggest speed win in the whole package: it is what stops another R3-040 4h05. Keep it exactly as written.
3. The backpressure cap is right: max 2 unscored tasks per runner, pause that runner only (the other lane continues) when lag exceeds 30 minutes. It bounds the Phase 2 scoring drain to at most 4 tasks and keeps the drain inside its 2h deadline. Do not raise it (drain blows out) and do not lower it to 1 (runners idle waiting on scoring, the decoupling saving evaporates).
4. G-23 gates the run on the messaging chain being proven working. Starting without it caused the 79-minute stall and the 4h silent scorer in the audit. The gate costs start delay, but a run with a dead reporting chain is slower than a delayed start. Keep it.
5. G-30 correctly makes the FCC meeting input non-blocking: note and proceed if it does not arrive. The FCC lane brief already carries the plan.
6. Two lanes stay the cap. The research (section 14) and the team's own measured parallelism (1.21-1.82x) both say 2 runners. A third runner would need a third scorer pair and is not costed anywhere. Keep 2.
7. The 10-minute heartbeat cadence is right. Detection within 15 minutes needs a cadence under 15 minutes, and 10 minutes gives margin. The problem is not the cadence, it is the channel and the ack rule (amendment A1).
8. The checkpoint after the 3rd graded task is kept in concept. Measuring replaces the assumption that the R3-L2 rate (about 1.5h per task) contradicts. The problem is the pause trigger, not the checkpoint (amendment A3).
9. Codex prevention 10 (checkpoint + backpressure) and prevention 6 (manifest gate as a mandatory checkpoint) are adopted. Both are cheap and load-bearing. Keep them.

## 2. The arithmetic the draft does not do (why AMEND, not APPLY)

The draft adds real coordinator serial work on top of a coordinator that the base plan already names as the bottleneck (F-24: 55 manifest gates about 2 min each is 1.8h, 110 grade audits about 5 min each is about 9h, 55 ledger appends, 9 Tier A runs). The added work is nowhere costed against the 19-31h budget:

- Heartbeat acks: 6 workers with an outstanding task, every 10 minutes, is 36 heartbeats per hour. Over a 25h run that is about 900 heartbeats, each requiring a written ack from the coordinator (section 8: "the coordinator acknowledges receipt in writing"). At even 30 seconds of coordinator attention each, that is about 7.5h of ack work, on top of the 9h of audits and 1.8h of gates. At 1 minute each it is 15h. The draft's budget does not include a single minute of it.
- Watchdog creation: 3 new crons (coordinator-liveness-watch, reporting-chain-watch, daemon-liveness-watch) plus re-enabling 1 and extending 2, all before task 1. Phase 0 was already 2-4h of focused coordinator work. The new crons add roughly 60-90 minutes of setup and verification to Phase 0, and each new cron is a new failure surface that can cry wolf (audit F-13: a watchdog that cries wolf teaches everyone to ignore it).
- State file updates after every task, PID recording before every launch, Zen RSS polling, per-graded-task reports to the parent: each is small alone, together they are a steady tax on the one serial worker in the run.

None of this kills the run. All of it is fixable with concrete changes below. That is why the vote is AMEND and not REJECT.

## 3. Amendments (each required before task 1)

### A1. Heartbeat channel and ack rule (most serious cost item)

- Problem: section 8 requires a written coordinator ack for every 10-minute heartbeat from every worker. About 900 written acks over the run, uncosted, on the serial bottleneck worker. The ack also travels over the same daemon channel whose failure it is meant to detect, so a flaky ack path alone can look like a broken chain.
- Fix: heartbeats go to a shared append-only heartbeat log file, not as individual daemon or chat messages. One JSONL line per heartbeat: wall-clock time, worker, task ID, status, evidence path. Newline-checked before append, parse-verified after, same discipline as the ledger (F-06). The coordinator's watchdog reads that one file to detect silence. The coordinator acks in batch, once per 30 minutes per worker, in a single short message, or implicitly through its next task instruction. A missing batch ack alone never marks the chain broken. The chain is broken only when the coordinator is unreachable for 15 minutes (F-01d) or no per-task report arrives for 30 minutes (F-02c). Daemon and chat messages are reserved for start, finish, blocked, and escalation.
- Effect: detection stays inside 15 minutes, the about 900 written acks become about 50 batched acks, and the watchdog has one file to check instead of a message stream.
- This mirrors the verdict pattern the run already uses: scorers send verdicts by file to the coordinator only, never by chat.

### A2. Heartbeat scope

- Problem: section 5 and section 8 say "every worker" heartbeats every 10 minutes. Standby tiebreakers have no task, researchers have no task, Mei is review-only. Heartbeats from idle agents are pure noise on the coordinator's queue.
- Fix: only a worker with an outstanding task heartbeats every 10 minutes. Standby tiebreakers, researchers, and Mei heartbeat on state change or once per hour, whichever comes first. The 15-minute silence rule applies only to a worker with an outstanding task.

### A3. Checkpoint pause trigger (most serious objection)

- Problem: section 9 keeps the base plan rule: pause and report to the owner if the revised run-complete is outside 19-21h OR the mean cycle time exceeds the estimate by more than 25 percent. Two defects. First, the plan itself states 19-21h is a lower bound, not a forecast, and the honest range is 19-31h. Pausing the whole run because the revised estimate is 22-31h means pausing a run that is inside its staffed budget, costing wall time and an owner decision for no benefit. Second, the early sample is biased slow by construction: the first 3 graded tasks include R3-001 (Class L serial, the slowest scoring shape in Pair A) and R3-002 (the Tier A decoupling pilot, with a serial snapshot verification before the runner proceeds to task 3). The base plan warns about this bias and the draft repeats the warning without fixing the trigger, so the pause will very likely fire spuriously on the first checkpoint and stall a run that is actually on plan.
- Fix: recompute per lane AND per class (Class S cycle against the Class S estimate, Class L cycle against the Class L estimate, never a blended mean). Pause and report to the owner ONLY if the revised run-complete exceeds 31h (the staffed ceiling) OR a per-class mean cycle exceeds its estimate by more than 25 percent with at least 3 graded tasks of that class. If the revised run-complete is 22-31h, continue and record the revised estimate in writing. No pause, no owner decision.
- Also add a wall-clock fallback checkpoint: if fewer than 3 tasks are graded by 3h of wall time since task 1, run the checkpoint then. The 3rd-graded-task trigger alone lets a slow start hide for hours (the R3-L2 rate was about 1.5h per task; after 3h with zero grades, something is already wrong).

### A4. Merge the watchdogs (three new crons become one)

- Problem: section 5 lists 9 watchdogs, including 3 new crons that watch the same failure through different lenses. Coordinator-liveness-watch (coordinator silent 15 min) and reporting-chain-watch (no per-task report 30 min) are two views of one chain. Daemon-liveness-watch (daemon socket) and zen-laptop-health-watch (ports 9222/9223/9224/2828) are two views of one laptop. Each new cron is Phase 0 setup time and a false-positive surface.
- Fix: merge coordinator-liveness-watch and reporting-chain-watch into one 5-minute cron that checks both conditions (coordinator reported in the last 15 min AND parent received a per-task report in the last 30 min) and sends one alert. Merge daemon-liveness-watch into zen-laptop-health-watch: one 15-minute cron checking ports 9222, 9223, 9224, 2828, the daemon socket, and Zen RSS (for Z8, see A6). Net before task 1: 1 new cron (merged liveness/chain), re-enable mei-mochi-15m-watchdog, extend the 2 existing tonight crons. Drop the separate daemon-liveness-watch and reporting-chain-watch rows from section 5.
- Effect: Phase 0 watchdog setup drops from roughly 60-90 minutes to roughly 30 minutes, and alerts come from one place per failure instead of two.

### A5. Coordinator bottleneck: mechanical audit plus pre-authorized relief

- Problem: F-24 names the coordinator as the bottleneck and the only mitigation is "report measured times at the checkpoint, the owner decides whether to add a second coordinator". By the checkpoint the bottleneck has already cost hours, and the decision itself costs a pause. The 110 audits at about 5 minutes each (about 9h) assume manual audit, but the readiness check proves audit-scan.py already exists and correctly passes a clean verdict and fails a verdict that reads the ledger.
- Fix: the forbidden-read audit is mechanical. The coordinator runs audit-scan.py and files its output; the manual 5-minute review per grade applies only to the verdict content, not to the read check. Phase 0 pre-authorizes an audit-only second coordinator with a numeric trigger written before task 1: if measured coordinator serial time per graded task exceeds 12 minutes at the checkpoint, or the manifest-plus-gate queue backs up past 2 tasks, the audit-only coordinator starts automatically, no fresh owner decision, no pause. The owner pre-approves the trigger now, in Phase 0. The ledger writer never changes: still only the coordinator writes the ledger.
- Effect: the 9h audit estimate falls, and the bottleneck has a pre-approved escape hatch instead of a mid-run pause.

### A6. G-27 concrete verification (Z8)

- Problem: section 2 says the coordinator verifies "the unload protection from the council prefs is effective, or the tab is pinned, or the memory headroom is sufficient". The readiness check proved the first option is not verifiable: browser.tabs.unloadOnLowMemory is absent from prefs.js because the pref does not exist in this build, so it is a no-op. Accepting "prefs effective" as a pass would pass a gate that proves nothing, and an unloaded run tab mid-run costs a full task re-run.
- Fix: G-27 passes only on verifiable facts: the run tab is PINNED (checkable) and the RSS headroom is recorded (17 GB available at probe time; the 8 GB RSS threshold triggers the Z3 restart point). The RSS poll rides on the merged 15-minute health watch from A4, not a separate coordinator poll. Do not list "council prefs effective" as an accepted verification.

### A7. G-29 downgrade: gitleaks private-ip finding leaves the pre-run gates

- Problem: G-29 makes the historical gitleaks private-ip finding (a private network address in a worklog error message, commit 2ee670a7) a pre-run gate. The readiness check itself says it is low severity, not a credential, and does not block the run. A gate that can be satisfied by a written acceptance sentence is gate theater, and a scrub commit before task 1 is Phase 0 work with zero run benefit.
- Fix: move G-29 out of the pre-run gates to post-run cleanup. Record the written acceptance now (known historical finding, scrub date set after the run closes). Task 1 must not wait on it.

### A8. Phase 0 cost note

- Problem: the draft adds gates G-23 to G-30 to a Phase 0 that was already 2-4h, without stating the added time.
- Fix: with A4 applied, the added Phase 0 work is about 30 minutes (messaging-chain verification, state file, PID procedure, one new cron, G-27 pin check). The coordinator records the added Phase 0 time in the run log. Without A4 it is 60-90 minutes, which is a further reason A4 is required.

## 4. Considered and deliberately NOT added (speed lens)

- Capture-recapture batch check (research section 7): after each batch of about 10 scored tasks, compute the overlap between the two pairs' blocking findings and re-pass a batch on low overlap. Not adopted for this run. It would add re-scoring passes to the critical path for a benefit that is unproven in this run's shape, and the two-pair structure already gives the divergence signal through the tiebreaker and the inter-pair drift check (F-20). Revisit after the run, not during it.
- Third runner (PR #68): not adopted. Undecided by the owner, uncosted, and it would need a third scorer pair. Two lanes stay.
- Raising the backpressure cap above 2: not adopted. It would let runners pile up unscored work and push the scoring drain past its 2h deadline.
- Lowering the heartbeat cadence below 10 minutes: not adopted. 10 minutes already gives detection inside 15 minutes; faster heartbeats add coordinator load for no detection gain.

## 5. Objections answered (none dismissed without an answer)

- O1. "The draft adds prevention without costing it." Answered by A1, A4, A5, A8: the ack load is removed, the crons are merged, the audit is mechanized, the added Phase 0 time is stated.
- O2. "The checkpoint will pause a healthy run." Answered by A3: the trigger moves to the 31h staffed ceiling with per-class separation and a 3-task minimum per class, plus a wall-clock fallback checkpoint.
- O3. "Nine watchdogs is triple coverage of the same failures." Answered by A4: merged to one new cron plus re-enable plus extensions.
- O4. "The coordinator bottleneck has no relief until after it has already cost hours." Answered by A5: mechanical audit plus a pre-authorized numeric trigger.
- O5. "G-27 can pass on a pref the readiness check proved is a no-op." Answered by A6: pin plus recorded RSS headroom only.
- O6. "A low-severity historical finding is a pre-run gate." Answered by A7: moved to post-run cleanup with written acceptance now.
- O7. "Heartbeat acks travel over the channel whose failure they detect." Answered by A1: heartbeats move to a shared log file, acks are batched, chain-broken is defined by unreachability and missing reports, not by a missing ack.

## 6. Verdict

- Vote: AMEND. The draft is good as a base: it keeps the honest 19-31h budget, the 30-minute timeout, the backpressure cap of 2, the messaging-chain gate, and all 10 Codex preventions. None of the amendments above changes the run shape, the lanes, the pass bar, or any hard constraint. Each amendment is a concrete fix with a named location in the draft. Apply A1 to A8, then the draft is ready for task 1.
- Single most serious objection: A3, the checkpoint pause trigger. As written it will very likely fire spuriously on the biased early sample (R3-001 Class L serial plus the R3-002 pilot) against a 19-21h band the plan itself calls a lower bound, and pausing the whole run for an owner decision while the run is inside its staffed 19-31h budget is the most expensive failure this draft can produce before a single task is graded.
- What would change this vote to REJECT: if the checkpoint trigger in A3 is kept as written AND the heartbeat ack rule in A1 is kept as written together, because the run would then both stall spuriously at its first checkpoint and carry about 900 uncosted written acks on its serial bottleneck. Either one alone is amendable; both together are not.

## 7. Log

- Started reading sources: 2026-11-24 21:36 +07.
- Vote file written: 2026-11-24 21:38 +07.
- Elapsed reading and voting: about 2 minutes for the read of the draft and the execution plan sections relevant to speed, plus the research, audit, readiness check, and Codex input read before that in the same session.
- Delivery: committed to todolist-push at improvements/r3-l3-replan-council-2-speed-20261124.md, verified with git ls-remote.
