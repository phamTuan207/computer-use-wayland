# Independent redteam: R3-L3 re-planned roadmap (draft 2026-11-24)

- Redteam: independent, did not write the draft, does not share the council's assumptions.
- Draft judged: ~/workspace/r3-l3-replan-draft-20261124.md (11 sections, 50843 bytes).
- Date: 2026-11-24. Work started 21:36 Asia/Ho_Chi_Minh, ended 21:58 Asia/Ho_Chi_Minh. Elapsed about 22 minutes.
- Sources read in full before writing: the draft; the execution plan ~/workspace/r3-l3-execution-plan-20261124.md (565 lines); the crawler research improvements/r3-l3-multiagent-coordination-research-20261124.md (commit f9e20bd); the complaints audit improvements/r3-l3-complaints-audit-20261124.md (commit 5a1d705, 132 incidents); the readiness check improvements/r3-l3-readiness-check-20261124.md (commit 73b49a5, 21 PASS / 3 FAIL / 3 PARTIAL); Codex runner input ~/workspace/codex-meeting-input-20261124.md (10 risks + 10 preventions); Clone1 meeting input improvements/r3-l3-clone1-meeting-input-20261124.md (commit 86dd55a8); the coordinator state file rung3-run-log/r3-l3-coordinator-state.json (last updated 2026-11-24T20:02:00+07:00); the deputy declaration ~/workspace/r3-l3-deputy-declaration.md (2026-11-24 17:24:46 +07); the timeout procedure rung3-run-log/r3-l3-timeout-watch.md; the backup file rung3-run-log/du-phong.txt; the Phase 0 checklist status rung3-run-log/r3-l3-phase0-checklist-status.md; the calibration verification report ~/workspace/r3-l3-calibration-VERIFICATION.md; Council 1 vote improvements/r3-l3-replan-council-1-stability-20261124.md (commit 0823c184, AMEND, 14 amendments); Council 2 vote improvements/r3-l3-replan-council-2-speed-20261124.md (commit 6fa22a1d, AMEND, 8 amendments); Council 3 vote improvements/r3-l3-replan-council-3-correctness-20261124.md (commit c1d39fef, AMEND, 28 objections, read after the first draft of this report and folded in as M-16 to M-19 and S-14 to S-19).
- Live checks done by this redteam (not taken from any other file): cron.list at 21:43 +07 (mei-mochi-15m-watchdog disabled; tonight-coordinator-stall-watch, tonight-clone1-progress-watch, tonight-worker-process-watch, tonight-zen-laptop-health-watch enabled; coordinator-liveness-watch, reporting-chain-watch, daemon-liveness-watch absent); grep of the calibration verification report for df4defcc (0 hits); read of the state file tail (TB-B2 verification-gap correction at 20:02 present); evidence-requirements.json at rung3-ci/ covers all 55 task IDs plus 5 backups (61 keys); R3-040-retry-s1 still present in ~/workspace/rung3-snapshots/ (62 entries).
- No long dash or en dash in this file. Commas, periods, short hyphens only.
- No credential value in this file. The R3-029 credential lives in the run coordinator brief only, never in the repo. No account email in this file. No personal info.

## Verdict: NOT READY

10 BLOCKING, 19 MUST-FIX, 19 SHOULD-FIX. The run must not start until every BLOCKING item is fixed. The draft is a real improvement on the execution plan: F-01 and F-02 name the right failure modes, the watchdog plan is explicit, G-23 gates the run on the messaging chain, and all 10 Codex preventions are adopted. But the draft's answers to the two new failure modes do not work as specified, two of its gates cannot be evaluated as written, and one of its verdict rules contradicts the operative procedure file. Council 1, Council 2, and Council 3 all voted AMEND; this redteam independently confirmed 8 of Council 1's blocking items and the core of Council 2's amendments, confirmed 10 of Council 3's objections, and adds 2 new BLOCKING items (B-01, B-10) plus 9 new MUST-FIX items the councils did not raise. AMEND and NOT READY are consistent: fix first, then start.

## How to read the ranks

- BLOCKING: the run must not start until fixed. Either a correctness failure (a wrong verdict can lock silently), a split-brain risk (two coordinators), or a gate that cannot be evaluated (so readiness cannot be known).
- MUST-FIX: fix before task 1 or the run is at real risk. The failure is recoverable but costs hours, a stall, or a re-run.
- SHOULD-FIX: fix if cheap, else record as an accepted risk with an owner and a date.
- Items marked (confirm) were found independently by this redteam and also appear in a council vote; the convergence is noted, the verification here is my own. Items marked (new) were not raised by either council.

## BLOCKING

### B-01 (new). The timeout verdict rule contradicts the operative procedure file

- Failure scenario: a task hits the 30-minute timeout with a complete-looking deliverable in the evidence folder. The execution plan (section 3) and the draft (section 9) both say "Over 30 minutes is FAIL, stop, log." The timeout procedure file rung3-run-log/r3-l3-timeout-watch.md (precondition 8, marked DONE) says the opposite: "The timeout itself is not a verdict; the grade comes from the evidence (PASS/FAIL/INVALID per the key)", and "If the evidence is enough to check against the key, grade PASS or FAIL." The same file, step 5, says to run the manifest gate on the timed-out snapshot and "If the gate FAILS (missing required files), the task is graded from whatever is in the snapshot", which also contradicts the manifest-gate failure branch (gate FAIL means no reset, re-collect, re-run; 3 failures then pause). The scorers are never told the gate failed, so they can PASS a task from evidence the gate already judged untrustworthy.
- Why the draft does not prevent it: the draft repeats the plan's rule and never mentions that the precondition-8 file says the opposite. Both rules cannot be true. Whichever one the coordinator follows at 03:00, the other file calls it wrong, and the 53/55 tally depends on the choice.
- Fix: the council picks one rule before task 1 and edits the other file to match, then re-verifies precondition 8. Proposed: over 30 minutes is FAIL, stop, log (the plan and draft rule), and a timed-out task with a failed gate is FAIL (incomplete), never graded from partial evidence. A timed-out task with a passed gate is still FAIL on timeout, with the evidence kept for the record. Record the chosen rule in the timeout file and in the draft.

### B-02 (confirm Council 1 M-01). Deputy takeover has no fencing: a live-but-unreachable coordinator plus a deputy takeover equals two coordinators

- Failure scenario: the daemon dies again mid-run (it died twice tonight). The coordinator is alive, working, and unreachable for 15 minutes because the channel is down, not because it is dead. The deputy takes over under F-01(c) and section 7. Now two coordinators issue orders, write ledger rows, and perform resets. The draft has no fencing token, no state-file lock, no rule that the old coordinator must stop writing, and no rule for which coordinator the workers obey.
- Why the draft does not prevent it: F-01(c) triggers on 15 minutes of silence, and silence is not death. Nothing in the draft distinguishes the two.
- Fix: (a) the deputy must verify the coordinator is dead, not merely silent, before taking over: check coordinator session/process liveness through the parent plus the state file mtime, and record the evidence in the state file; (b) the deputy writes a takeover record (timestamp, evidence, new active coordinator id) into the state file BEFORE issuing any order; (c) workers obey only the coordinator id named in the state file field `coordinator_active`; (d) the old coordinator must check that field before every ledger write and every state update, and must stop writing the moment it is no longer the active coordinator; (e) if the coordinator is alive but unreachable, the deputy does NOT take over, it restores the channel instead. Only one side may order stop or continue at any time. The concrete fencing mechanism already exists in Clone1's input section 2.2 and was not adopted: a coordinator epoch integer in the heartbeat file, incremented by the deputy on takeover, with workers accepting only assignments carrying the current epoch. Adopt it.

### B-03 (confirm Council 1 M-03). G-23 can go green while the send path is still unproven, and without the supervisor alive

- Failure scenario: the fixer restarts the daemon, Chromium comes back, read.py returns ok=true for mochi. G-23 goes green. But reads prove the read path only. Tonight the send probe crashed with ECONNREFUSED while reads worked for mei, and the readiness check states explicitly that a real send is still unproven until the coordinator's next real message goes through. The daemon died with its supervisor, and nothing in G-23 requires the supervisor alive, so the daemon can die silently again the same way.
- Why the draft does not prevent it: G-23 checks daemon status, Chromium running, and read.py ok=true. None of those proves a send.
- Fix: rewrite G-23 so it passes only when (a) daemon.sh status shows the daemon alive AND the supervisor process is alive (both PIDs recorded in the run log); (b) a SEND to mochi is proven with delivery confirmed by re-reading the thread (the coordinator's first real message counts, but the gate must not be marked green until that send plus re-read succeeds; if a test message is needed, use one agreed test message and record it); (c) read.py returns ok=true for mochi, and for mei or a named fallback. Add a daemon resilience proof: kill the daemon, confirm the supervisor restarts it and read.py works within 5 minutes. A restart alone, without (a) and (b), does not pass G-23.

### B-04 (confirm Council 1 M-04). TB-B2 is presented as approved, but its approval is coordinator-only, not independent

- Failure scenario: Pair B disagrees on a task, or a key dispute is raised, and TB-B2 (df4defcc) breaks the tie. Its verdict is final for that task. If its calibration was never independently verified, the tiebreak rests on the coordinator's own check, which is the party whose work the tiebreaker is meant to check.
- Why the draft does not prevent it: the draft roster lists TB-B2 with no caveat. My own checks: the state file tail carries a CORRECTION recorded 2026-11-24T20:02:00+07:00 stating TB-B2's 4/4 approval rests on the coordinator's own check, NOT on independent verification, and the independent verification report was verified 17:27, before the TB-B2 calibration (17:31), covers only the first candidate 9d613f19 (3/4, NOT APPROVED), and never mentions df4defcc. My grep of the verification report for df4defcc returned 0 hits. Execution plan precondition 10 requires Pair B declarations and calibration verified by someone other than the coordinator before task 1. The draft does not mention this gap at all, while the Phase 0 status file item 10 still says TB-B2 was "APPROVED" without the caveat.
- Fix: before task 1, either an independent verifier signs the TB-B2 calibration (grade file ~/workspace/r3-l3-calibration-TBB2.md), or the gap is recorded as an accepted limitation with an owner decision, in the same pattern as execution plan objection 43 (TB-B2 acts only on disagreement, so the risk is bounded, but it must be declared, not silently presented as fully approved). Add the caveat to the section 1 roster and to the Phase 0 checklist.

### B-05 (confirm Council 1 M-05). The deputy confirmation in G-24 is stale: it predates the TB-B2 change and the state file update

- Failure scenario: the coordinator dies mid-run and the deputy resumes from the state file. The deputy last read the state file at 17:24:46, when tiebreaker B was 9d613f19, the candidate later NOT APPROVED (3/4). The deputy has never confirmed the current state file, which lists TB-B2 df4defcc and the 20:02 verification-gap correction.
- Why the draft does not prevent it: G-24 states as a present fact that the deputy "has read it and confirmed". My own checks: the deputy declaration is timestamped 2026-11-24 17:24:46 +07 and lists tiebreaker B as 9d613f19; the state file was last updated 2026-11-24T20:02:00+07:00. G-24 as a present fact is false for the current state file.
- Fix: the deputy must re-read the CURRENT state file and re-confirm in writing before task 1, with a new timestamp after the last state-file update. G-24 must name the confirmation artifact (declaration file plus timestamp, or a confirmation line appended to the state file). A confirmation older than the last material state change does not satisfy G-24.

### B-06 (confirm Council 1 M-07). Heartbeats depend on the daemon, which is the component that died tonight

- Failure scenario: the daemon dies mid-run with its supervisor, as it did tonight, unnoticed for about 2 hours. Every heartbeat and every ack fails at once, because sections 7 and 8 name no channel other than the daemon. The draft's own rule (a heartbeat with no ack is a broken chain) then reads as a total chain failure with no fallback, and every worker stops at its next task boundary while nobody can report the stall, because the reporting path is the dead daemon.
- Why the draft does not prevent it: the heartbeat design rides on the single component whose failure it is meant to detect. The fallback channel is also untested: the Phase 0 status file item 18 admits the speed-lean fallback was "not yet test-sent".
- Fix: define two heartbeat channels. Primary: daemon message. Fallback: file-based heartbeat (worker appends one JSONL line per heartbeat, wall-clock time, worker, task ID, status, evidence path, into a heartbeat log file; newline-checked before append, parse-verified after, same discipline as the ledger). The coordinator's watchdog reads that one file to detect silence. Rule: a heartbeat with no ack after 10 minutes (one retry) switches to the fallback channel; a worker that cannot reach the coordinator on either channel for 15 minutes stops at the task boundary. Test-send the speed-lean fallback before task 1 and record the result. Add the fallback to sections 7 and 8 and to F-01/F-02. (This is the same fix as Council 2 A1, applied to the heartbeat channel rather than only to the ack load.)

### B-07 (confirm Council 1 M-02). The coordinator-liveness trigger and the reporting-chain trigger will false-positive on normal long tasks

- Failure scenario: a single task legitimately runs up to 30 minutes by the timeout rule, and R3-L2 observed about 1.5 hours per task of wall time. A 30-minute gap with no graded task is normal mid-task, not a broken chain. Section 5 triggers coordinator-liveness-watch on no coordinator report in the last 15 minutes while tasks are running, and reporting-chain-watch on no per-task report for 30 minutes. Both watches will fire constantly, teach everyone to ignore them, and, combined with B-02, risk a spurious deputy takeover on a healthy run.
- Why the draft does not prevent it: the triggers are defined on graded-task reports, but grading is not the coordinator's heartbeat.
- Fix: define a coordinator heartbeat that is independent of grading: every 10 minutes the coordinator writes a heartbeat (timestamp, next task per lane, unscored queue depth) into the state file and reports it to the parent. The coordinator-liveness-watch triggers only on a missing heartbeat (15 minutes), never on a missing per-task report. The reporting-chain-watch triggers only on no heartbeat AND no per-task report for 30 minutes. Add the heartbeat emission to the coordinator's duties and to the checkpoint measurement.

### B-08 (confirm Council 1 M-06). "Record the PID BEFORE launching" is unimplementable for codex exec, and the deputy's contact path is unproven

- Failure scenario: the coordinator launches a codex exec invocation for a task. G-25 and F-01(a) require the PID recorded BEFORE launching. A codex exec PID exists only after launch, so the rule cannot be followed for the Codex lane, and the coordinator either violates its own gate or records a PID that does not exist. Separately, on takeover the deputy is supposed to "contact every live worker by PID/session", but nothing verifies the deputy has a working path to the laptop (SSH) or to the tmux sessions. The deputy is a subagent session; its laptop reach was never proven.
- Why the draft does not prevent it: the rule is written for a process model that does not match the Codex lane, and the takeover path was never dry-run.
- Fix: change the rule to record launcher session plus task id before launch, and the worker PID immediately after launch, before any task work starts, verified by ps. Add a pre-task-1 dry-run gate: the deputy lists every live worker from the state file and confirms the contact path (SSH/tmux/session) for each, and the result is recorded in the run log. If the deputy cannot reach the laptop, the takeover procedure is unproven and must be fixed or the deputy role reassigned to a session with SSH before task 1.

### B-09 (confirm Council 1 M-08). G-27 / Z8 has no pass/fail criterion, and the Marionette fallback is unproven

- Failure scenario: the coordinator marks G-27 green because "the memory headroom is sufficient" (17 GB available at probe time) while the run tab has no actual unload protection. Nineteen hours later Zen RSS grows, the tab unloads during a long idle gap, and a Class L live re-read finds nothing there. Or a BiDi session zombies mid-run (F-17) and the fallback control path, Marionette, is the one the readiness check found hanging on newSession (PARTIAL, cause unproven).
- Why the draft does not prevent it: F-21 lets the coordinator verify "the unload protection is effective, or the tab is pinned, or the memory headroom is sufficient", and none of those has a threshold. The readiness check found browser.tabs.unloadOnLowMemory absent from prefs.js (the pref does not exist in this build, so the council pref line is a no-op), and Z5 states pinned tabs are only deprioritized by the unloader, not exempt. So there is no verified protection to check, and G-27 cannot be marked green or red as written. Clone1's own input (section 1.1) is more honest than the draft: it says the choice between unloader-off (unbounded memory growth toward OOM) and unloader-on (the run tab itself can unload) must be made explicitly, and names zen.tab-unloader.excluded-urls as the only reliable Zen-side lever. The draft names no such lever.
- Fix: make G-27 concrete before task 1: record the about:unloads baseline (Z4) plus Zen RSS plus available RAM, with stated thresholds (proposed: run tab pinned AND available RAM above a stated floor AND Zen RSS below 8 GB); polling stays as written (RSS over 8 GB triggers the Z3 restart). If no unload protection can be verified, record Z8 as an accepted risk with the mitigation being RSS polling plus re-run on unload, not as a verified protection. Record the Marionette PARTIAL as an accepted risk with owner and date: BiDi primary, Marionette fallback unproven, response to a zombie BiDi session is the Z3 restart, not Marionette.

### B-10 (new). G-26 is unevaluable: the lane and scorer briefs were issued before the re-plan, and nothing verifies workers know the new rules

- Failure scenario: the FCC runner, the Codex runner, and the scorers were briefed on the execution plan earlier in the day. Tonight the re-plan adds rules they have never seen: the 10-minute heartbeat plus ack, the stop-at-task-boundary rule, the durable trace per codex exec invocation, the pill-before-drive rule, the explicit-pathspec git rule. Task 1 starts. A worker that cannot reach the coordinator keeps running silently, because it was never told to stop. That is F-01's only sound leg (worker self-stop, which Council 1 confirmed as correct) failing for the most banal reason: nobody told the worker.
- Why the draft does not prevent it: G-26 says "every worker knows the 10-minute heartbeat + ack rule" with no verification method. A gate that cannot be verified is not a gate, the same defect as B-09. The draft also says "The FCC lane brief already carries the plan" (G-30), but the plan changed tonight, so the brief carries the old plan.
- Fix: re-issue both lane briefs and the scorer briefs carrying the re-plan rules (heartbeat plus ack, stop at the task boundary, durable trace, pill before drive, explicit-pathspec git, no banned model routes, no personal data in repo text) and collect a written acknowledgement from each worker before task 1. G-26 passes only on the acks, not on the coordinator asserting that every worker knows.

## MUST-FIX

### M-01 (new). The per-graded-task report to the parent has no defined medium, and a cron cannot read chat

- Failure scenario: the coordinator "sends a per-graded-task report to the parent (Muse) as each ledger row lands" (F-02(b), section 8). The reporting-chain-watch is a cron that checks "has the parent received a per-task report in the last 30 minutes". A cron cannot read the parent's chat. If the report travels by chat message, the watch has nothing to grep, so it can never fire and never clear. If the report travels by subagent final message, it arrives once at the end, not per task.
- Why the draft does not prevent it: the draft never says the report is a file write. The watch assumes an observable artifact that the reporting step never produces.
- Fix: per-task reports are appended to a named run-log file with timestamps (task ID, verdict, pair, tiebreaker if any, invalid or backup if any, elapsed time). The reporting-chain-watch greps that file. The coordinator's chat message to the parent, if any, is a copy of the file line, not the record itself.

### M-02 (new). The deputy wake path does not exist, and deputy liveness is unwatched

- Failure scenario: the coordinator-liveness-watch fires at 03:00. The draft says "the deputy is alerted" and "the deputy takes over". A cron cannot message a subagent session. The deputy is a standby session that has sat idle since 17:24; nothing polls it, nothing wakes it, and nothing checks whether that session still exists at hour 20 of a 31-hour run. The takeover never happens, and the workers sit stopped at task boundaries with no coordinator.
- Why the draft does not prevent it: section 5 names the deputy as the escalation target for a cron alert, but no mechanism connects a cron to a subagent session, and no watch covers the deputy itself. This is distinct from B-02 (fencing once the deputy acts) and B-08 (the deputy's contact path to workers): this is the path that wakes the deputy at all.
- Fix: name the chain explicitly: cron alerts the parent, the parent messages the deputy to take over (the parent is the only party that can reach a standby subagent session). Add a deputy-liveness check: the deputy confirms standby in the state file every hour; if the deputy session ends, the parent names a new deputy before task 1, or the run pauses until one is named. Record the wake chain in section 7.

### M-03 (new). The timeout watcher has no timer mechanism, and the kill command is unsafe

- Failure scenario: the timeout procedure says "The coordinator checks the runner session and the evidence folder at 15 minutes (midpoint) and at 30 minutes (deadline)." The coordinator is a subagent session; it does not poll on a schedule by itself. With no cron or timer process named, the 15-minute and 30-minute checks happen only if the coordinator happens to look, which is how R3-040 ran 4h05 in R3-L2 under a rule that already existed. At the deadline, the kill procedure for Codex says "kill it with pkill -f 'codex exec' (or kill the PID recorded at launch)". pkill -f matches any process whose command line contains that string, including a newer codex exec invocation if the old one already exited and the next task started, or any monitoring command that mentions it. A blind pkill can kill the wrong task.
- Why the draft does not prevent it: the draft repeats "timeout enforced" without naming the timer, and inherits the pkill line from the precondition-8 file without checking it.
- Fix: name the timer: a 5-minute cron (or a named watcher process) reads task_start from the state file, alerts at 15 minutes, and kills at 30 minutes. Kill by exact recorded PID only, never by pkill -f. The PID recorded immediately after launch (see B-08) is the only kill target. Record the timer's cron id in the run log before task 1.

### M-04 (new). FCC runner agent responsiveness is unproven; G-30 lets task 1 start on a silent runner

- Failure scenario: FCC was messaged at 21:24 for meeting input and had not replied at draft time. G-30 says the run proceeds anyway because "the FCC lane brief already carries the plan". Task 1 is R3-001 in the FCC lane. The readiness check verified the tmux session r3-fcc-runner-L3 exists and its pane shows an idle READY prompt from 17:20, but a prompt is not an agent response; the agent behind the session may be gone. Task 1 is released to a runner that never answers, and the run burns its first 30 minutes on a timeout.
- Why the draft does not prevent it: G-30 exempts FCC from the draft's own 15-minute silence rule, and no gate checks that the runner AGENT (as opposed to its session) is responsive before task 1.
- Fix: a live ping before task 1: FCC acknowledges the task-1 brief (and Codex acknowledges its lane brief) in writing. If FCC does not answer, the coordinator respawns the FCC runner session and re-pings. A tmux READY prompt does not satisfy this gate. If FCC's meeting input arrives mid-run, the coordinator triages it within 1 hour and records the disposition.

### M-05 (new). Tier A checker scripts are unverified, and the correlated failure has no independent re-run

- Failure scenario: the coordinator runs each Tier A checker once and hands the identical output to both scorers (F-19). If the checker is wrong (wrong file, stale fixture, misread key), both scorers receive the same wrong input, verify it against the same snapshot the checker read, agree, and lock a wrong verdict. No tiebreaker is called, because agreement produces no dispute. The failure is silent by construction: the only trigger for a second look is disagreement, and a correlated failure produces agreement.
- Why the draft does not prevent it: F-19's "verification" is circular (scorers check the checker output against the snapshot the checker already read), and it records the input hash, which detects nothing unless someone re-runs the checker, which nobody does. The readiness check compiled all rung3-ci scripts and proved manifest-gate and audit-scan on trial data, but it did not locate or trial-run the Tier A checker scripts. The draft says "If the checker script cannot be located, Decision D cannot be executed", but no one has recorded that the scripts were located.
- Fix: locate each Tier A checker script and trial-run it against a trial snapshot before task 1, and record the outputs. The coordinator independently re-runs the checker for the first Tier A task in each lane and compares outputs; a mismatch blocks grading until investigated. That is 2 extra runs for 9 Tier A tasks, and it is the only independent check on the single-run design.

### M-06 (confirm Council 2 A3, plus a new availability half). The checkpoint pause trigger fires on a healthy run, and the owner may be unreachable when it fires

- Failure scenario: the checkpoint fires after the 3rd graded task. The early sample is biased slow by construction: R3-001 is Class L serial (the slowest scoring shape in Pair A) and R3-002 is the Tier A decoupling pilot (serial snapshot verification before the runner proceeds to task 3). The base plan warns about this bias and the draft repeats the warning without fixing the trigger. The revised run-complete lands at 22-31 hours, inside the staffed budget, and the draft's rule pauses the whole run for an owner decision anyway. If that happens overnight, the owner is asleep or in morning class, and the run sits paused for hours waiting for a decision that was never pre-authorized.
- Why the draft does not prevent it: the trigger uses the 19-21 hour band, which the plan itself calls a lower bound, not a forecast, against a blended mean that mixes Class L and Class S cycles.
- Fix: recompute per lane AND per class (Class S cycle against the Class S estimate, Class L cycle against the Class L estimate, never a blended mean). Pause and report to the owner ONLY if the revised run-complete exceeds 31 hours (the staffed ceiling) OR a per-class mean cycle exceeds its estimate by more than 25 percent with at least 3 graded tasks of that class. If the revised run-complete is 22-31 hours, continue and record the revised estimate in writing. Add a wall-clock fallback checkpoint: if fewer than 3 tasks are graded by 3 hours of wall time since task 1, run the checkpoint then. Pre-authorize the checkpoint decision before task 1: the owner picks continue, stop, or add scorers, with a default if unreachable within 30 minutes, so a pause never waits on a sleeping owner.

### M-07 (new). Clone1's full input: the draft adopted 1 of 11 risks and gives no disposition for the rest

- Failure scenario: Clone1's meeting input (commit 86dd55a8) lists 11 risks with concrete preventions. The draft adopted one (the run-tab unload finding, F-21/Z8) and never mentions the other 10. Three are load-bearing. (a) A frozen Zen window is invisible to a heartbeat (Clone1 section 1.2, Zen issue 16706): after a resize the window stops rendering and freezes on the last frame while BiDi and Marionette still answer, so every draft watchdog reports the run healthy while the window is dead. Detection needs screenshot-hash comparison after an action that should change the page. (b) A stale profile lock makes every relaunch fail silently (Clone1 section 1.4, issue 16694): a crashed Zen leaves .parentlock and the lock symlink held, and every later launch fails with no window. The draft's Z3 restart verifies no zen-bin processes and free ports, then relaunches, with no lock check, so a stale lock produces a relaunch loop: ports stay down, the watch alerts, the coordinator relaunches, it fails again. (c) Epoch fencing (Clone1 section 2.2) is the concrete fix for B-02 and was not adopted.
- Why the draft does not prevent it: the draft treats Clone1's input as a single finding (F-21) and defers the rest to "folded into the re-plan before task 1", but the council is voting now, so the vote covers a draft that has not disposed of the input.
- Fix: a disposition table for all Clone1 items before task 1 (adopt, or reject with a reason). Adopt at minimum: screenshot-hash detection after state-changing actions for the freeze case; the stale-lock sequence in Z3 (kill all zen processes, verify pgrep empty, remove .parentlock and lock from the run profile only, then relaunch; never delete a lock while a process is alive; never recover with safe mode); and the coordinator epoch fencing from B-02. Note the item the draft must reject with a reason rather than ignore: per-lane browser profiles (Clone1 section 1.9) conflicts with the single-driver hard constraint, so the mitigation is the Z3 restart pausing both lanes, recorded as a decision.

### M-08 (confirm Council 2 A1 and Council 1 M-14). The heartbeat ack load is uncosted, about 900 written acks on the serial bottleneck

- Failure scenario: 6 workers with an outstanding task, every 10 minutes, is 36 heartbeats per hour. Over a 25-hour run that is about 900 heartbeats, each requiring a written ack from the coordinator (section 8). At 30 seconds of coordinator attention each, that is about 7.5 hours of ack work, on top of the 9 hours of audits and 1.8 hours of gates in F-24. At 1 minute each it is 15 hours. The draft's budget includes none of it, and the ack travels over the same daemon channel whose failure it is meant to detect, so a flaky ack path alone can look like a broken chain.
- Why the draft does not prevent it: F-24 counts gates, audits, appends, and Tier A runs, but not the new heartbeat ack load or the per-task parent reports.
- Fix: the file-based heartbeat log from B-06, with batched acks (once per 30 minutes per worker, in a single short message, or implicit through the next task instruction). A missing batch ack alone never marks the chain broken. Add ack latency to the checkpoint measurement: if ack latency exceeds 10 minutes, the heartbeat interval is the bottleneck and the coordinator reports it.

### M-09 (new). The F-07 git rule is backwards and internally contradictory

- Failure scenario: the coordinator stages the ledger row (git add -- rung3-run-log/R3-L3-grades.jsonl) and then runs a bare git commit. Between the add and the commit, Clone1 stages a research file in the same worktree. The bare commit sweeps Clone1's staged file into the coordinator's commit. That is exactly the 22/11 incident (a plain commit swept another worker's staged-but-uncommitted file) which F-07 claims to prevent. The draft also contradicts itself: F-07 says "Only the coordinator commits to the run-log branch during the run", while section 1 and section 5 let Clone1 commit research to todolist-push during the run, so the race is live by the draft's own rules.
- Why the draft does not prevent it: the draft bans `git commit -- <paths>` and mandates the bare commit. That is backwards: a commit with an explicit pathspec records only the named paths and cannot sweep another worker's staged file, while a bare commit records everything staged. The draft also contradicts the standing lesson (2026-11-22: always commit with an explicit pathspec AND immediately after staging). The draft inherited the ban from the execution plan objection 7 answer without checking it.
- Fix: commit with an explicit pathspec on the commit as well (`git commit -m <message> -- <paths>`), or verify `git status --porcelain` shows only intended files immediately before committing and abort if anything else is staged. Freeze all non-coordinator commits to todolist-push during the run (Clone1 research lands after the run, or on a separate branch), and correct the standing lesson if the council disagrees with it, rather than leaving two contradictory rules.

### M-10 (new). Precondition 6 disposition is missing: 5 pre-run invalid candidates are still open in du-phong.txt

- Failure scenario: R3-011, R3-028, R3-036, R3-046, and R3-047 are pre-run invalid candidates, all medium (trung binh), still listed as candidates ("ung vien") in du-phong.txt with none used. The Phase 0 status file marks precondition 6 DONE ("declared/verified with group mapping"), but the file itself records no disposition for the first four, only that timeanddate.com loads and Mochi's re-confirmation was pending. The draft never states their disposition. The cap math matters: the cap is max 5 total and max 2 per difficulty group, so at most 2 of these 5 medium candidates can ever be declared invalid. If a 3rd medium candidate turns invalid mid-run, the run stops at the 3rd-in-a-group rule.
- Why the draft does not prevent it: the draft carries no disposition table, so the council votes without knowing whether the run starts with 0, 2, or 5 invalids already booked against a cap of 5.
- Fix: publish a disposition table before task 1 (each candidate: invalid, valid, or pending with its re-check point). If any is still pending, name the re-check point and the backup it would consume. Record the group-cap consequence in the table: at most 2 medium invalids before the run stops.

### M-11 (confirm Council 1 M-11, independently verified). The watchdog creation gate and meta-watch are missing; 3 run watchdogs do not exist

- Failure scenario: the draft lists 9 watchdogs, 3 of them as "new cron (create before task 1)" with no ids and no verification step. They can be believed created while not running, the same class as audit item B10.6 (a cron believed removed but still live). There is also no meta-watch: if a run watchdog cron itself dies, nobody notices, repeating B10.1.
- Why the draft does not prevent it: my own cron.list at 21:43 +07 shows coordinator-liveness-watch, reporting-chain-watch, and daemon-liveness-watch absent entirely, mei-mochi-15m-watchdog disabled, and the 4 tonight watches enabled. The draft's todolist checkbox "Watchdogs created and enabled" has no verification method.
- Fix: a gate before task 1: every run watchdog is listed via cron.list with its id and a successful last run, recorded in the run log with its cron id (verify after creation, per the B10.6 lesson). Add a meta-watch: the parent checks each run watchdog's last-run timestamp hourly; a watchdog with no successful run in twice its interval raises an alert. Fix the runner-process-watch check: the Codex lane uses codex exec per task, not a daemon, so "Codex daemon is alive" is the wrong check; change it to "no stale codex exec process beyond the task timeout, plus FCC tmux session alive". Add a tonight-watchdog transition table (which tonight watches are disabled, which are extended for the run).

### M-12 (confirm Council 1 M-13). The correlated-outage maximum wait has no value

- Failure scenario: both lanes block on the same external cause (a site down, a 429, a bot check). F-23 says the coordinator pauses both lanes and waits, with the maximum wait "set in Phase 0". No value is proposed anywhere in the draft. An unbounded wait is the exact failure F-23 names, and the execution plan already flags the outage as unbounded until the value is written.
- Why the draft does not prevent it: the section 10 checklist carries the item ("Correlated-outage maximum wait written") without a value, so the gate can be checked off with the value still blank.
- Fix: set a concrete value before task 1 (proposed: 60 minutes, then escalate to the owner). The coordinator may change the value with a reason recorded in the run log, but task 1 must not start with the value blank. Also define the backup-exhaustion rule: a correlated event that invalidates more tasks than the remaining backups of that difficulty leaves the run short, and the coordinator escalates to the owner rather than improvising.

### M-13 (confirm Council 1 M-12). The mechanical consistency pass is missing as a gate

- Failure scenario: the execution plan still carries stale session ids (Pair A tiebreaker 6e844611, Pair B 2890a5de and b8c9b7b8, tiebreaker B 3f3aca86) that contradict the draft and the state file (TB-A 97290681, 1B 4e2f52d4, 2B 2e3ae678, TB-B2 df4defcc). A coordinator reading the execution plan calls the wrong tiebreaker; a scorer reading the wrong brief scores the wrong lane. This is the same defect class as audit A14 (an addendum listing retired scorer session IDs while other files listed new ones).
- Why the draft does not prevent it: the complaints audit Part C item 12 requires one mechanical consistency pass before task 1 (session ids, backup ids, file patterns, counts, positions across all run documents), failing the gate on any mismatch. The draft has no such gate.
- Fix: add the consistency pass as a pre-task-1 gate: one grep pass across all run documents with zero mismatches, recorded in the run log. Either correct the execution plan ids or declare the state file plus thu-tu-chay.txt canonical and stamp the plan as superseded on ids. Until the pass runs, the draft roster is the current claim, not the verified source.

### M-14 (new). The pill procedure is unproven on the actual drive path

- Failure scenario: the runners drive Zen over BiDi for 55 tasks. The draft asserts every live drive "must acquire the pill before driving", but no pill mechanism for BiDi or raw-protocol drives is proven to exist. The complaints audit B2.6 records that a message went in with no pill because it was sent over a raw protocol call, and that raw protocol is read-only until a pill-on-protocol mechanism exists. The draft's rule is therefore unenforceable on the exact path the run uses, and the run will drive without a pill, repeating the 19:53-20:22 violation that F-04 is meant to prevent.
- Why the draft does not prevent it: F-04(b) states the requirement as if the procedure existed. No readiness item proves the pill on BiDi, and the readiness check did not test it.
- Fix: a live test drive over BiDi with the pill visible, verified by screenshot, before task 1. If no pill mechanism exists for BiDi drives, record it as an accepted deviation with the owner's decision (the standing rule is that the pill MUST show on ANY agent control), rather than letting the run silently violate it.

### M-15 (new). The 22 preconditions' DONE marks are stale (18:20) and at least one is already falsified

- Failure scenario: the Phase 0 status file marks all 22 preconditions DONE at 18:20 +07. The readiness check at 21:21-21:38 found the messaging chain FAIL (daemon dead, Chromium down, stale scorer target) after that mark, so a DONE mark from 18:20 does not cover tonight's regression. Precondition 18's DONE also rests on a fallback that was never test-sent (see B-06). The draft's section 10 todolist re-lists "All 22 preconditions green, each verified with a named file" as a checkbox with no re-verification step, so the council can check it off by citing the 18:20 marks.
- Why the draft does not prevent it: the draft adds gates G-23 to G-30 without a status roll-up of the base 22, and without requiring a fresh verification pass.
- Fix: a final verification pass as a named gate with a fresh timestamp after 21:38 (re-run the readiness checks in one pass, confirm no regressions), owned by the parent, before task 1. The draft's checkbox must cite the fresh pass, not the 18:20 marks. The Phase 0 status file itself already says this pass is remaining ("Final verification pass: every tool works, every environment ready, re-run the checks in one pass, confirm no regressions, then report to the parent"); the draft must carry it as a gate instead of leaving it as a note.

### M-16 (confirm Council 3 A9). Standby-as-fallback-scorer leaves the pair without a tiebreaker

- Failure scenario: Mochi is unavailable, so TB-A (97290681) takes over as scorer 1 for Pair A, following the draft's fallback rule. The pair's scorers then disagree on a task. There is no one to call: TB-A is now scorer 1 and cannot tiebreak its own verdict. The pair has no dispute resolution for the rest of the lane (28 tasks), exactly when it is already degraded. The same holds for Pair B if TB-B2 becomes scorer 1.
- Why the draft does not prevent it: section 1 makes the standby the fallback scorer 1 for its pair but names no replacement tiebreaker.
- Fix: name the tiebreaker of last resort for a pair whose standby is acting as scorer 1 (for example the other pair's standby, or escalation of the disagreement to the council or the owner) and record it in the roster. The fallback must never consume the pair's only tiebreaker without a named replacement.

### M-17 (confirm Council 3 A11). The Codex retry rule contradicts the no-blind-retry rule

- Failure scenario: a codex exec invocation fails mid-task after partially driving the task (a form filled, a file written, a page changed). Section 1 says "If a codex exec invocation fails, the coordinator retries it once, then escalates", with no state check. The retry drives the same actions a second time on a partially completed task. Codex prevention 5 and F-11 forbid blind retry for exactly this reason: a partial run can drive the same action twice.
- Why the draft does not prevent it: the draft adopts Codex prevention 5 in full in section 4 and then states the opposite rule in section 1.
- Fix: retry only after checking the evidence dir and runner state (no partial drive already recorded), per F-11. If a partial drive is recorded, the coordinator re-runs the task from the start on a clean fixture, never by resuming the failed invocation.

### M-18 (confirm Council 3 A7). Section 9 mixes position numbers with task numbers

- Failure scenario: section 9 says "Pre-milestone reminders before positions 34 (Gutenberg), 49 (R3-089 fixture), 79 (coupled-task reset), 100 (port check)". Only 55 positions exist. 79 and 100 are task numbers, not positions (R3-079 is position 43 per the exception list; R3-100 is position 55). A coordinator following section 9 literally waits for position 79, which never comes, and misses the R3-079 coupled-task reset check and the R3-100 port check.
- Why the draft does not prevent it: the section 10 todolist says it correctly ("Before R3-079", "Before R3-100"), so the same file states the milestone two ways and the execution text is the wrong one.
- Fix: rewrite section 9 as before position 34 (R3-047 Gutenberg), before position 49 (R3-089 fixture), before R3-079 (position 43, coupled-task reset), before R3-100 (position 55, port check). Every milestone in the draft must carry both its position and its task ID.

### M-19 (confirm Council 3 A20). The F-12 manual ID update repeats the wrong-fix trap

- Failure scenario: Chromium restarts mid-run and target IDs change. F-12 says "until then, the coordinator updates the IDs after every browser restart and verifies with read.py". The manual update is exactly what produced tonight's wrong mei fix (pointing mei at clone1's tab, F0857EB317D3027975B6F70658AB666A, verified by direct CDP read). The draft's interim procedure IS the failure mode it warns about: a human copies an ID from a list, and the list is stale.
- Why the draft does not prevent it: F-12 names the manual update as the fallback without requiring the check that caught the error (verifying the tab's TITLE and CONTENT against the intended recipient).
- Fix: every manual ID update must verify tab TITLE and CONTENT match the intended recipient before use, the same check that exposed the wrong fix. Until the daemon resolves targets dynamically from /json/list at use time, the manual update is a high-risk step and the verification is mandatory, not advisory. Prefer the code fix (dynamic resolution) before task 1 over relying on the manual step all run.

## SHOULD-FIX

### S-01 (new). Ledger rows have no mechanical cross-check against the verdict files

- Failure scenario: the coordinator transcribes scorer verdicts into ledger rows by hand. A swapped PASS/FAIL, a wrong task ID, or a wrong pair in one row silently corrupts the 53/55 tally, and the row looks valid to every later check because validate-ledger.py checks schema, not agreement with the verdict files.
- Why the draft does not prevent it: no step compares a ledger row to the verdict files it came from.
- Fix: a script diffs each ledger row against its verdict files (task ID, verdict, pair) before each push, or the rows are generated from the verdict files instead of typed. Cheap, and it is the only check on the tally itself.

### S-02 (new). R3-040-retry-s1, a stale R3-L2 directory, still sits in the snapshot tree

- Failure scenario: a scorer (most plausibly Mochi, browsing files) opens R3-040-retry-s1 instead of R3-040-L3 and grades stale R3-L2 evidence. The verdict locks on the wrong run. My live check confirms the directory still exists in ~/workspace/rung3-snapshots/ (62 entries), and the state file records it was "left untouched".
- Why the draft does not prevent it: the draft never mentions it. The snapshot naming rule (-L3 suffix) prevents collision for new snapshots, but it does not remove the one stale directory that already breaks the pattern.
- Fix: quarantine or remove R3-040-retry-s1 before task 1, and record the removal in the run log.

### S-03 (new). Mochi's prior-knowledge bias on the 11 repeated tasks has no mitigation beyond a recorded limitation

- Failure scenario: Mochi re-scores 11 tasks she already scored in R3-L2, knowing the prior verdicts, and she also reviewed the R3-L3 build and saw key contents. If she and scorer 2 agree on a repeated task, the agreement looks like independence but may be memory. The draft's check (scorer 2 plus tiebreaker) only fires on disagreement, so agreement caused by prior knowledge is invisible.
- Why the draft does not prevent it: execution plan precondition 22 records the exposure as a limitation and does not mitigate it.
- Fix: the tiebreaker blind-scores a sample of the repeated tasks (proposed: 3 of the 11) as a bias check, and the result is recorded. If the sample diverges from Mochi's verdicts, widen the sample.

### S-04 (new). Inter-pair drift: the n=3 comparison is meaningless, and there is no re-score rule for locked verdicts

- Failure scenario: Pair A and Pair B grade different tasks, so "inter-pair agreement" cannot be computed by comparing verdicts on the same tasks. The draft compares within-pair agreement rates on 3 graded tasks each, where a single disagreement flips the outcome, and the pairs grade different difficulty mixes, so a difference may reflect task mix, not drift. If drift is found at task 10, ten verdicts are already locked and the draft has no rule for revisiting them.
- Why the draft does not prevent it: F-20 defines the trigger but not the measurement and not the response.
- Fix: use the first 5 graded tasks per pair (or a rate rule with a minimum sample), separate the comparison by difficulty, and define the drift response: the tiebreaker re-scores the affected pair's earlier tasks, or the drift is recorded as a limitation with the affected tasks named.

### S-05 (new). Backup assignment has no second check

- Failure scenario: the coordinator assigns a backup by hand at an invalid decision. A slip assigns DP-01 (retired, failed in R3-L2), a backup of the wrong difficulty, or a backup already used. The task runs, the evidence is graded, and only later does someone notice the backup was never live. That is the DP-01 defect from the execution plan, recurring through a manual step instead of a stale file.
- Why the draft does not prevent it: the files were fixed, but the assignment step itself has no verification.
- Fix: script-check the assignment before the backup runs (unused, same difficulty, not DP-01, order matches du-phong.txt) and record the check in the run log.

### S-06 (confirm Council 1 M-09). The mei fallback in G-23 is undefined

- Failure scenario: mei is declared unavailable with a fallback of "repo/PR channel" and no file path, monitor, or latency. An INVALID proposal sits in a channel nobody watches, which is a silent stall by another name.
- Why the draft does not prevent it: G-23 allows the declaration without defining the fallback.
- Fix: state the fallback explicitly. The existing invalid procedure (execution plan section 6: scorer 1 proposes with evidence, scorer 2 confirms blind, tiebreaker on dispute, coordinator countersigns) already covers INVALID proposals without mei, so the fallback is: mei's review is skipped and the scorer-led procedure stands, with the coordinator checking for scorer proposals every 15 minutes during the run. Name the confirming scorer per lane (Pair A scorer 2 for FCC-lane tasks, Pair B scorer 2 for Codex-lane tasks), and state that a Mei proposal is an additional input, not a replacement: scorer 1 keeps its proposal right. If a repo/PR channel is meant instead, name the file path, who monitors it, and the check interval before task 1.

### S-07 (confirm Council 2 A7). G-29 is gate theater

- Failure scenario: the gitleaks private-ip finding (a private network address in a worklog error message, commit 2ee670a7) is a pre-run gate that can be satisfied by a written acceptance sentence, while a scrub commit before task 1 is Phase 0 work with zero run benefit. The readiness check itself says it is low severity, not a credential, and does not block the run. A scrub in a new commit also does not remove the address from history, so the gate's "scrubbed" branch does not even do what it claims.
- Why the draft does not prevent it: G-29 offers "scrubbed in a new commit OR explicitly accepted in writing", and the acceptance branch needs no scrub date to be meaningful.
- Fix: move G-29 out of the pre-run gates to post-run cleanup. Record the written acceptance now (known historical finding, scrub date set after the run closes). History rewrite remains a separate owner decision on a shared branch.

### S-08 (new). The coordinator state file has no atomic-write rule

- Failure scenario: the coordinator dies mid-write and the state file is torn (partial JSON). The deputy resumes from a file that does not parse, or parses with a stale position, and re-runs a task that already ran or skips a task that never ran. F-06's atomic rule covers the JSONL ledger only, not the state file.
- Why the draft does not prevent it: G-24 and G-25 require the state file to exist and be current, but nothing constrains how it is written.
- Fix: write temp file then rename; the deputy verifies the file parses and its mtime is sane before trusting it, and falls back to the ledger tip plus the run log if it does not.

### S-09 (new). The Z3 restart has no stuck-holder fallback

- Failure scenario: Zen RSS passes 8 GB, or a BiDi session zombies, and the Z3 restart point is reached. The restart requires the current BiDi holder to end its session cleanly. The holder is the stuck runner, so it cannot. Kill -9 is banned (a second consecutive unclean start shows the session-restore prompt and blocks automation). The procedure deadlocks: it cannot restart without the holder, and the holder cannot comply.
- Why the draft does not prevent it: Z3 lists the clean path only.
- Fix: define the fallback (kill the holder process, accept the restore prompt on the next start, dismiss it via a defined step, verify tabs restored) or record the stuck-holder case as a run-stop with escalation to the owner.

### S-10 (new). The F-03 memory-job guard has no owner, deadline, or verification

- Failure scenario: the hourly memory job demoted the R3-029 decision twice today, and the draft itself notes it "will be demoted again at 22:43 tonight". Prevention (b) says owner decisions are append-only for automated jobs, but names no one to enforce it, no deadline, and no check. The same job already deleted the R3-040 retry decision line. The draft's fix is a rule with no process behind it, the exact class the complaints audit names as the root cause of the 79-minute stall.
- Why the draft does not prevent it: the draft removes reliance on MEMORY.md for the password only; other run-critical decisions still live there with no guard.
- Fix: name the owner and the verification (check at 22:43 that the decision survives, or remove all reliance on MEMORY.md for run-critical decisions by carrying them in the briefs and the state file).

### S-11 (new). The R3-089 refresh owner and date are unassigned, and the 29/11 deadline is after the run ends

- Failure scenario: the draft's todolist carries "R3-089 fixture refresh owner + date assigned" as a checkbox, not a fact. The Phase 0 status file says the owner is the run coordinator and the refresh happens "the day before R3-089 runs", with no date. The hard deadline 2026-11-29 19:20 is after the run ends (19-31 hours from 25/11), so it cannot guard a run that finishes on 26/11. If position 49 arrives and the fixture is stale, R3-089 cannot run and the run stalls at position 49.
- Why the draft does not prevent it: the real deadline (the day before position 49) depends on run pace and was never computed.
- Fix: assign the owner and date now, or refresh in Phase 0 and verify find -mtime -7 returns exactly 6, which removes the mid-run dependency (a refresh on 25/11 still leaves the 6 recent files inside the 7-day window on 26/11).

### S-12 (confirm Council 1 M-10). The draft itself breaks its own credential and personal-info rules

- Failure scenario: draft section 6 reproduces the R3-029 credential value in plaintext outside the run coordinator brief, contradicting its own handling rule (brief only, never in a repo file). The draft roster also carries an account email address for agy. Both would reach the repo if the draft is committed as written.
- Why the draft does not prevent it: the draft states the rule and violates it in the same file.
- Fix: the final plan must reference the credential by pointer only (account name, position 25, "in the run coordinator's brief"), with the value removed. Remove the account email from the roster in any committed version; name the account by role only. This vote file contains neither value.

### S-13 (new). Clone1's search-lag and window-counting items have no disposition

- Failure scenario: a runner types into the urlbar, the UI freezes while the process stays alive (Clone1 section 1.6, issue 16710), and the coordinator kills Zen on a timeout, losing state and creating a false crash. Separately, a harness step that counts windows miscounts when openPreferences opens a separate settings dialog window (Clone1 section 1.5).
- Why the draft does not prevent it: neither item is mentioned.
- Fix: fold both into the Clone1 disposition table from M-07: wait 60 seconds before killing on a slow response, never type a search into the urlbar (navigate by URL instead), and verify the run tab by URL read from BiDi or Marionette, never by window position or clipboard.

### S-14 (confirm Council 3 A15). Backpressure wording drift

- Failure scenario: section 9 says "if the lag exceeds 30 minutes, pause that runner". That reads as lag alone triggering a pause. The base plan pauses when the runner has 2 unscored tasks AND the oldest lag exceeds 30 minutes. A runner with 1 unscored task and a 31-minute scoring lag gets paused under the draft's wording, stalling a lane the base plan would keep running.
- Why the draft does not prevent it: the conjunction was dropped in the rewrite.
- Fix: restore the conjunction verbatim (2 unscored tasks AND oldest lag over 30 minutes).

### S-15 (confirm Council 3 A16). Pass-bar recomputation narrowed

- Failure scenario: the valid count shrinks mid-run (a task excluded, a backup exhausted). Section 9 Phase 3 says the bar is recomputed only by an owner decision before task 1 if the valid count shrank. The base plan Phase 3 step 4 recomputes per table (54 valid needs 52, 53 needs 51) and records it in the ledger, with an owner decision required only if the shrink was not pre-declared. Under the draft's wording, a pre-declared shrink that changes the bar has no defined path during the run.
- Why the draft does not prevent it: the draft narrowed the rule in the rewrite.
- Fix: restore the table plus the pre-declared-shrink distinction.

### S-16 (confirm Council 3 A21). Roster count is wrong

- Failure scenario: section 1 says the draft "names the full 9-person team". The roster table lists 14 rows (coordinator, 2 runners, 4 scorers, 2 tiebreakers, Mei, Clone1, Clone2, Opencode, agy). A roster whose own count is wrong invites the reader to assume 5 members do not exist, or that 9 is the team and the rest are not counted for coverage.
- Why the draft does not prevent it: the count was carried over from the execution plan's 9 sessions without updating it for the expanded roster.
- Fix: correct the count to 14 named members (or state 9 sessions plus 5 support members) and say which members are on the critical path and which are support only.

### S-17 (confirm Council 3 A23). Re-enabling a watchdog the owner disabled, without citing approval

- Failure scenario: the owner ordered the mei-mochi 15-minute watchdog disabled tonight. The draft asserts it is re-enabled for the run (F-14(c), section 5) without citing owner approval for the re-enable. If the owner disabled it for a reason that still holds, the re-enable disobeys an owner order; if the reason was pre-run-only, nobody recorded that.
- Why the draft does not prevent it: the draft treats the re-enable as its own decision.
- Fix: record owner confirmation for the re-enable (or note that run-start approval covers it) before task 1.

### S-18 (confirm Council 3 A24). The P1-H todolist item is undefined in the draft

- Failure scenario: section 10 says "P1-H pref reverted after the run (council condition)". P1-H is defined nowhere in the draft. A todolist item nobody can execute is either skipped silently or done wrong.
- Why the draft does not prevent it: the item references a decision from another document without naming it.
- Fix: define P1-H in the draft (which pref, what value, reverted to what) or remove the item.

### S-19 (confirm Council 3 A27). The section 11 decision rule is ambiguous

- Failure scenario: the council votes and a member votes REJECT with an objection. The rule says "A REJECT blocks only if its objection is not concretely mitigated", but nobody is named to judge whether the mitigation is concrete. The council judges its own mitigation, which is the same party that wrote the draft.
- Why the draft does not prevent it: the rule names no judge.
- Fix: name the judge (proposed: the redteam confirms whether its own objections are mitigated; the parent confirms for council objections) and record the judgement in writing before task 1.

## What the draft gets right (kept, no change)

- F-01 worker self-stop at the task boundary. Correct: a worker that cannot reach the coordinator must finish the current task, preserve evidence, and not start the next one. This is the only rule that bounds orphan work without any coordinator at all, and it is the floor under B-02, B-06, and B-10.
- F-02 delivery verification by re-reading, never by send receipt. Correct and directly learned from tonight.
- The 15-minute poke condition (last sent newer than last seen reply, silence over 15 minutes, no poke in the last 15 minutes, never while the read path is broken). Correct.
- Adopting all 10 Codex preventions in full, including the durable trace per codex exec invocation, the manifest gate as a mandatory checkpoint, and the pre-milestone reminders. Correct.
- The honest budget is kept: 19-31 hours, staffed for 31 hours, no promise of a 20-hour finish. The draft does not shrink the range to pay for its new preventions.
- The pre-reset content check is machine-readable: rung3-ci/evidence-requirements.json covers all 55 task IDs plus the 5 backups (verified by this redteam), so the check is not a human parse.
- The 30-minute per-task timeout is kept. This is the single biggest speed win in the package, provided B-01 resolves which verdict a timeout produces.

## Single most likely way this run still breaks

The messaging chain dies again mid-run. Chromium died twice tonight with no root cause found (no crash dump, no OOM, no kill signal), the daemon died with its supervisor and went unnoticed for about 2 hours, and the run's only defense is a 15-minute poll plus a manual coordinator relaunch, while Mochi is scorer 1 for the entire FCC lane and every heartbeat, ack, and per-task report rides the same dead channel. The second most likely break is a split-brain deputy takeover (B-02) if the daemon outage recurs and the deputy mistakes an alive-but-unreachable coordinator for a dead one. The third is a silent wrong verdict: a Tier A checker error (M-05) or a timeout-rule disagreement (B-01) locking a wrong PASS/FAIL with no dispute to trigger a second look.

## Council vote (redteam)

| Member | Lens | Vote | Objections / amendments |
|---|---|---|---|
| Redteam | Independent break-it | NOT READY | 10 BLOCKING (B-01 to B-10), 19 MUST-FIX (M-01 to M-19), 19 SHOULD-FIX (S-01 to S-19) above. The run must not start until every BLOCKING item is fixed. Each BLOCKING item has a concrete fix named. |

Decision rule (draft section 11): majority (2 of 3) APPLY = council APPLY. This redteam vote is NOT READY, not a council APPLY. The redteam's objections must each be answered (fix, accept with owner + date, or reject with a reason) before task 1.

## Work log

- Started 21:36 Asia/Ho_Chi_Minh, 2026-11-24. Ended 21:58 Asia/Ho_Chi_Minh. Elapsed about 22 minutes.
- Read the draft, the execution plan, the crawler research, the complaints audit, the readiness check, the Codex input, the Clone1 input, the coordinator state file, the deputy declaration, the timeout procedure, the backup file, the Phase 0 checklist status, the calibration verification report, and all three council votes in full. Council 3 (commit c1d39fef, AMEND, 28 objections) landed during this review and was read and folded in as M-16 to M-19 and S-14 to S-19.
- Live checks: cron.list at 21:43 +07; grep of the verification report for df4defcc (0 hits); read of the state file tail (TB-B2 correction at 20:02 present); evidence-requirements.json coverage (61 keys, all 55 task IDs); R3-040-retry-s1 still present in the snapshot tree.
- No browser work was needed. No agent capability was assumed; session ids, watchdog existence, and file coverage were verified against live records, not taken from the draft's claims.
- No credential value and no account email appear in this file. The R3-029 credential is referenced by pointer only.
