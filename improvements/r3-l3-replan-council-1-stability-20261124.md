# Council 1 vote: stability / risk lens on the R3-L3 re-planned roadmap (draft 2026-11-24)

- Voter: Council Member 1 (stability / risk).
- Vote: AMEND.
- Date: 2026-11-24. Work started 21:36 Asia/Ho_Chi_Minh.
- Draft judged: ~/workspace/r3-l3-replan-draft-20261124.md (11 sections).
- Sources read in full before voting: the execution plan (565 lines), the crawler research (commit f9e20bd), the complaints audit (commit 5a1d705, 132 incidents), the readiness check (commit 73b49a5, 21 PASS / 3 FAIL / 3 PARTIAL), the Codex runner input (10 risks + 10 preventions), the coordinator state file rung3-run-log/r3-l3-coordinator-state.json (last updated 2026-11-24T20:02:00+07:00), the deputy declaration ~/workspace/r3-l3-deputy-declaration.md (2026-11-24 17:24:46 +07), and the live cron list (checked 2026-11-24 ~21:40 +07).
- No long dash or en dash in this file. Commas, periods, short hyphens only.

## Verdict in one paragraph

The draft is a real improvement on the execution plan and it correctly targets the two new failure modes. F-01 (orphan workers) and F-02 (silent reporting chain) name the right mechanisms, the watchdog plan is explicit instead of living only in memory, and the gates G-23 to G-30 close real holes found tonight. But the draft is not safe to apply as-is. Its deputy-takeover rule has no fencing against split-brain, its coordinator-liveness trigger will false-positive on every long task, its G-23 gate can go green while the send path is still unproven, and three of its load-bearing claims are stale or unverified against the state file. Every objection below is fixable before task 1 with the concrete fix named. None of them requires rethinking the run. That is why the vote is AMEND, not REJECT.

## What is sound (no change needed)

- F-01 worker self-stop at the task boundary. Correct: a worker that cannot reach the coordinator must finish the current task, preserve evidence, and not start the next one. This is the only rule that bounds orphan work without any coordinator at all.
- F-02 delivery verification by re-reading, never by send receipt. Correct and directly learned from tonight (daemon "sent, verified" coexisting with "delivery not confirmed" for about 4 hours) and from the 20 Oct chat receipt that never appeared in the transcript.
- The 15-minute poke condition (last sent newer than last seen reply, silence over 15 minutes, no poke in the last 15 minutes, never while the read path is broken). Correct; it is the fix for the false poke tonight.
- G-28 (credential in the run coordinator brief only, verified by reading the brief) and G-29 (gitleaks private-ip scrub or written acceptance with a scrub date). Correct in shape. See amendment M-10 for the draft's own handling slip.
- Adopting all 10 Codex preventions in full, including the durable trace per codex exec invocation, the manifest gate as a mandatory checkpoint, and the pre-milestone reminders. Correct.
- F-21 / Z8 naming the run-tab unload risk. Correct to name it. See amendment M-08: the protection itself is not yet verifiable as written.
- The checkpoint after the 3rd graded task with a pause-and-report decision rule. Correct; it is the only honest answer to the R3-L2 observed rate contradicting the baseline.

## Objections and required amendments

### M-01 (blocking). Deputy takeover has no fencing: a live-but-unreachable coordinator plus a deputy takeover equals two coordinators

- Problem: F-01(c) and section 7 let the deputy take over after 15 minutes of coordinator silence. Silence is not death. Tonight the daemon died and the supervisor died with it; a coordinator can be alive, working, and unreachable for 15 minutes because the messaging channel is down, not because the coordinator is dead. If the deputy takes over while the old coordinator is alive, there are two coordinators issuing orders, writing ledger rows, and performing resets. The draft has no fencing token, no state-file lock, no rule that the old coordinator must stop writing, and no rule for which coordinator the workers obey. This is the single most dangerous gap in the draft.
- Fix (add to section 7 and G-25): (a) the deputy must verify the coordinator is dead, not merely silent, before taking over: check the coordinator session/process liveness through the parent plus the state file mtime, and record the evidence in the state file; (b) the deputy writes a takeover record (timestamp, evidence, new active coordinator id) into the state file BEFORE issuing any order; (c) workers obey only the coordinator id named in the state file field `coordinator_active`; (d) the old coordinator must check that field before every ledger write and every state update, and must stop writing the moment it is no longer the active coordinator; (e) if the coordinator is alive but unreachable, the deputy does NOT take over, it restores the channel instead. Only one side may order stop or continue at any time (Codex prevention 3).

### M-02 (blocking). The coordinator-liveness trigger and the reporting-chain trigger will false-positive on normal long tasks

- Problem: section 5 triggers coordinator-liveness-watch on "no coordinator report in the last 15 min while tasks are running" and reporting-chain-watch on "no per-task report for 30 min while tasks are running". A single task legitimately runs up to 30 minutes by the timeout rule, and R3-L2 observed about 1.5 hours per task of wall time. A 30-minute gap with no graded task is normal mid-task, not a broken chain. Both watches will fire constantly, teach everyone to ignore them, and risk a spurious deputy takeover under M-01.
- Fix: define a coordinator heartbeat that is independent of grading: every 10 minutes the coordinator writes a heartbeat (timestamp, next task per lane, unscored queue depth) into the state file and reports it to the parent. The coordinator-liveness-watch triggers only on a missing heartbeat (15 min), never on a missing per-task report. The reporting-chain-watch triggers only on no heartbeat AND no per-task report for 30 minutes. Add the heartbeat emission to the coordinator's duties and to the checkpoint measurement (section 9, F-24).

### M-03 (blocking). G-23 can go green while the send path is still unproven, and without the supervisor alive

- Problem: G-23 requires the daemon running, Chromium running with the mochi tab, and read.py ok=true. Read proves the read path only. The readiness check states explicitly that a real send is still unproven until the coordinator's next real message goes through. Tonight the send probe crashed with ECONNREFUSED while reads worked for mei. A gate that checks reads only can pass with sends broken, which is exactly tonight's failure mode. G-23 also does not require the supervisor process alive; the readiness check fix 1 says to find why the supervisor died with the daemon, or the daemon can die silently again. Restarting the daemon without the supervisor alive repeats the failure.
- Fix (rewrite G-23): the gate passes only when (a) daemon.sh status shows the daemon alive AND the supervisor process is alive (both PIDs recorded in the run log); (b) a SEND to mochi is proven with delivery confirmed by re-reading the thread (the coordinator's first real message counts, but the gate must not be marked green until that send plus re-read succeeds; if a test message is needed, use one agreed test message and record it); (c) read.py returns ok=true for mochi, and for mei or a named fallback under M-09. Daemon restart alone, without (a) and (b), does not pass G-23.

### M-04 (blocking). TB-B2 is presented as approved, but its approval is coordinator-only, not independent

- Problem: the draft roster lists TB-B2 (df4defcc) as tiebreaker for Pair B with no caveat. The coordinator state file records a correction at 2026-11-24T20:02:00+07:00: TB-B2 calibrated 4/4, but that approval rests on the coordinator's own check, NOT on independent verification. The independent verification report covers only the first candidate 9d613f19 (3/4, NOT APPROVED) and never mentions df4defcc. Execution plan precondition 10 requires Pair B declarations and calibration verified by someone other than the coordinator before task 1. The draft does not mention this gap at all.
- Fix: before task 1, either an independent verifier signs the TB-B2 calibration (grade file ~/workspace/r3-l3-calibration-TBB2.md), or the gap is recorded as an accepted limitation with an owner decision, in the same pattern as execution plan objection 43 (TB-B2 acts only on disagreement, so the risk is bounded, but it must be declared, not silently presented as fully approved). Add the caveat to the section 1 roster and to the Phase 0 checklist.

### M-05 (blocking). The deputy confirmation in G-24 is stale: it predates the TB-B2 change and the state file update

- Problem: the deputy declaration is timestamped 2026-11-24 17:24:46 +07. It lists tiebreaker B as 9d613f19, the candidate later NOT APPROVED (3/4). TB-B2 (df4defcc) was approved at 17:31, the TB-B2 verification-gap correction was recorded at 20:02, and the state file was last updated 20:02. The deputy has not confirmed the current state file. G-24 as a past fact ("the deputy has read it and confirmed") is false for the current state file.
- Fix: the deputy must re-read the CURRENT state file and re-confirm in writing before task 1, with a new timestamp after the last state-file update. G-24 must name the confirmation artifact (declaration file plus timestamp, or a confirmation line appended to the state file). A confirmation older than the last material state change does not satisfy G-24.

### M-06 (blocking). "Record the PID BEFORE launching" is unimplementable for codex exec, and the deputy's contact path is unproven

- Problem: G-25 and F-01(a) require the coordinator to record every live worker PID before launching it. A codex exec PID exists only after launch; it cannot be recorded before. As written the rule cannot be followed for the Codex lane. Separately, the deputy is supposed to "contact every live worker by PID/session" on takeover, but nothing verifies the deputy has a working path to the laptop (SSH) or to the tmux sessions. The deputy is a subagent session; its laptop reach was never proven. An unproven takeover path is a paper prevention for the top new failure mode.
- Fix: change the rule to record launcher session plus task id before launch, and the worker PID immediately after launch, before any task work starts, verified by ps. Add a pre-task-1 dry-run gate: the deputy lists every live worker from the state file and confirms the contact path (SSH/tmux/session) for each, and the result is recorded in the run log. If the deputy cannot reach the laptop, the takeover procedure is unproven and must be fixed or the deputy role reassigned to a session with SSH before task 1.

### M-07 (blocking). Heartbeats depend on the daemon, which is the component that died tonight

- Problem: sections 7 and 8 route heartbeats and acks through the coordinator, but name no channel. The only named messaging channel is the daemon, which died tonight with its supervisor, unnoticed for about 2 hours. A heartbeat design that rides on the daemon inherits the daemon's failure mode: when the daemon dies, every heartbeat and every ack fails at once, and the draft's own rule (a heartbeat with no ack is a broken chain) then reads as a total chain failure with no fallback.
- Fix: define two heartbeat channels. Primary: daemon message. Fallback: file-based heartbeat (worker writes a heartbeat file with task id, status, evidence path, timestamp into the run-log dir; coordinator reads it). Rule: a heartbeat with no ack after 10 minutes (one retry) switches to the fallback channel; a worker that cannot reach the coordinator on either channel for 15 minutes stops at the task boundary. Add the fallback to sections 7 and 8 and to F-01/F-02.

### M-08 (blocking). G-27 / Z8 has no pass/fail criterion, and the Marionette fallback is unproven

- Problem: F-21 says the coordinator verifies "the unload protection is effective, or the tab is pinned, or the memory headroom is sufficient" before task 1. None of those has a threshold. The readiness check found browser.tabs.unloadOnLowMemory absent from prefs.js (the pref does not exist in this build, so the council pref line is a no-op), and Z5 states pinned tabs are only deprioritized by the unloader, not exempt. So there is no verified protection to check, and G-27 cannot be marked green or red as written. Separately, the readiness check lists Marionette newSession hanging as PARTIAL with cause unproven, and BiDi is the only working control path. If a BiDi session zombies (F-17), the fallback control path is unproven; the draft does not carry this as a gate or an accepted risk.
- Fix: make G-27 concrete before task 1: record the about:unloads baseline (Z4) plus Zen RSS plus available RAM, with stated thresholds (propose: run tab pinned AND available RAM above a stated floor AND Zen RSS below 8 GB); polling stays as written (RSS over 8 GB triggers the Z3 restart). If no unload protection can be verified, record Z8 as an accepted risk with the mitigation being RSS polling plus re-run on unload, not as a verified protection. Record the Marionette PARTIAL as an accepted risk with owner and date: BiDi primary, Marionette fallback unproven, response to a zombie BiDi session is the Z3 restart, not Marionette.

### M-09 (amendment). The mei fallback in G-23 is undefined

- Problem: G-23 allows mei to be "declared unavailable with a fallback (repo/PR channel) recorded". No file path, no monitor, no latency is named. An INVALID proposal that sits in a repo channel nobody watches is a silent stall by another name.
- Fix: state the fallback explicitly. The existing invalid procedure (execution plan section 6: scorer 1 proposes with evidence, scorer 2 confirms blind, tiebreaker on dispute, coordinator countersigns) already covers INVALID proposals without mei, so the fallback is: mei's review is skipped and the scorer-led procedure stands, with the coordinator checking for scorer proposals every 15 minutes during the run. If a repo/PR channel is meant instead, name the file path, who monitors it, and the check interval before task 1. Do not leave "repo/PR channel" as an undefined phrase in a gate.

### M-10 (amendment). The draft itself breaks its own credential and personal-info rules

- Problem: draft section 6 reproduces the R3-029 credential value in plaintext outside the run coordinator brief, contradicting its own handling rule (brief only, never in a repo file). The draft roster also carries an account email address for agy. Both must not reach any repo-committed version.
- Fix: the final plan must reference the credential by pointer only (account name, position 25, "in the run coordinator's brief"), with the value removed. Remove the account email from the roster in any committed version; name the account by role only. This vote file contains neither value.

### M-11 (amendment). The three new watchdogs do not exist yet and there is no watch on the watchers

- Problem: verified live against the scheduler at about 21:40 +07 on 2026-11-24: mei-mochi-15m-watchdog exists but is disabled; tonight-coordinator-stall-watch, tonight-clone1-progress-watch, tonight-zen-laptop-health-watch, tonight-worker-process-watch exist and are enabled; coordinator-liveness-watch, reporting-chain-watch, and daemon-liveness-watch do not exist at all. The draft lists them as "new cron (create before task 1)" with no ids and no verification step, so they can be believed created while not running (the same class as the audit item B10.6, a cron believed removed but still live). There is also no meta-watch: if a run watchdog cron itself dies, nobody notices, repeating B10.1 (the guard that watches the watchers runs on its own schedule).
- Fix: add a gate before task 1: every run watchdog is listed via cron.list with its id and a successful last run, recorded in the run log with its cron id. Add a meta-watch: the parent checks each run watchdog's last-run timestamp hourly; a watchdog with no successful run in twice its interval raises an alert. Also fix the runner-process-watch check: the Codex lane uses codex exec per task, not a daemon, so "Codex daemon is alive" is the wrong check; change it to "no stale codex exec process beyond the task timeout, plus FCC tmux session alive".

### M-12 (amendment). The mechanical consistency pass is missing as a gate

- Problem: the execution plan still carries stale session ids (Pair A tiebreaker 6e844611, Pair B 2890a5de / b8c9b7b8, tiebreaker B 3f3aca86) that contradict the draft and the state file (TB-A 97290681, 1B 4e2f52d4, 2B 2e3ae678, TB-B2 df4defcc). The complaints audit Part C item 12 requires one mechanical consistency pass before task 1 (session ids, backup ids, file patterns, counts, positions across all run documents), failing the gate on any mismatch. The draft has no such gate, so the roster cannot yet be trusted as the single source.
- Fix: add the consistency pass as a pre-task-1 gate: one grep pass across all run documents with zero mismatches, recorded in the run log. Either correct the execution plan ids or declare the state file plus thu-tu-chay.txt canonical and stamp the plan as superseded on ids. Until the pass runs, the draft roster is the current claim, not the verified source.

### M-13 (amendment). Correlated-outage maximum wait has no value

- Problem: F-23 and the section 10 checklist require the maximum wait to be written in Phase 0, but no value is proposed anywhere. An unbounded wait is the exact failure F-23 names.
- Fix: set a concrete value before task 1 (proposed: 60 minutes, then escalate to the owner). The coordinator may change the value with a reason recorded in the run log, but task 1 must not start with the value blank.

### M-14 (minor). Coordinator heartbeat/ack load is uncounted in F-24

- Problem: F-24 counts manifest gates, grade audits, ledger appends, and Tier A runs, but not the new heartbeat ack load (every worker every 10 minutes plus written acks) or the per-task parent reports. The coordinator is already the serial bottleneck; the new load makes the checkpoint measurement more important, not less.
- Fix: add heartbeat ack latency to the checkpoint measurement (coordinator records ack latency per worker; if ack latency exceeds 10 minutes, the heartbeat interval is the bottleneck and the coordinator reports it at the checkpoint). No separate gate needed.

## Answers to the brief questions

- Does the draft prevent the failure modes? Mostly. F-01 and F-02 name the right mechanisms and the Codex preventions are adopted in full. But M-01 (no fencing), M-06 (PID rule unimplementable, takeover path unproven), and M-07 (heartbeat rides the dead daemon) mean the two new failure modes are prevented on paper, not yet in a way that survives the exact conditions that caused them.
- Are the pre-run gates sufficient? No, as written. G-23 misses the send path and the supervisor (M-03), G-24 rests on a stale confirmation (M-05), G-25 rests on an impossible recording rule (M-06), and G-27 has no pass/fail criterion (M-08). The missing consistency-pass gate (M-12) and the missing watchdog-creation gate (M-11) are also required.
- Is the orphan-worker prevention (F-01) sound? Directionally yes, mechanically no. The worker self-stop rule is sound. The deputy takeover is not sound without fencing (M-01), a provable contact path (M-06), and a non-daemon heartbeat channel (M-07).
- Is the silent-reporting-chain prevention (F-02) sound? Directionally yes, mechanically no. Re-read verification and the poke condition are sound. The triggers false-positive on normal long tasks (M-02) and the heartbeat has no fallback channel (M-07).
- Are the watchdog triggers tight enough? The intervals (5-minute cron for a 15-minute silence) are tight enough. The triggers are not: the 30-minute per-task-report trigger misfires on normal tasks (M-02), three of the seven run watchdogs do not exist yet (M-11), and nothing watches the watchdogs.
- Single most likely way this run still breaks: the messaging chain dies again mid-run. Chromium died twice tonight with no root cause found (no crash dump, no OOM, no kill signal), the daemon died with its supervisor and went unnoticed for about 2 hours, and the run's only defense is a 15-minute poll plus a manual coordinator relaunch, while Mochi is scorer 1 for the entire FCC lane. The second most likely break is a split-brain deputy takeover (M-01) if the daemon outage recurs and the deputy mistakes an alive-but-unreachable coordinator for a dead one.

## Verification notes (what was checked live, not asserted)

- Cron list at about 21:40 +07 2026-11-24: mei-mochi-15m-watchdog disabled; tonight-coordinator-stall-watch, tonight-clone1-progress-watch, tonight-zen-laptop-health-watch, tonight-worker-process-watch enabled; coordinator-liveness-watch, reporting-chain-watch, daemon-liveness-watch absent.
- Deputy declaration 2026-11-24 17:24:46 +07 lists tiebreaker B as 9d613f19 (later NOT APPROVED 3/4); state file last updated 2026-11-24T20:02:00+07:00 lists TB-B2 df4defcc approved 17:31 and records the TB-B2 independent-verification gap at 20:02.
- Coordinator state file: 22-item checklist marked all DONE at 18:20 +07, but the readiness check at 21:21-21:38 +07 found the messaging chain FAIL after that mark, so a Phase 0 DONE mark from 18:20 does not cover tonight's regression. G-23 is the right response; M-03 makes it strong enough.
- Draft roster ids (TB-A 97290681, 1B 4e2f52d4, 2B 2e3ae678, TB-B2 df4defcc, deputy 028399b1) match the state file and thu-tu-chay.txt. The execution plan ids (6e844611, 3f3aca86, 2890a5de, b8c9b7b8) are stale. See M-12.

## Work log

- Started 21:36 Asia/Ho_Chi_Minh, 2026-11-24. Ended 21:39 Asia/Ho_Chi_Minh. Elapsed about 3 minutes for reading and voting; the underlying sources were read in full before voting.
- Read the draft, the execution plan, the crawler research, the complaints audit, the readiness check, the Codex input, the deputy declaration, and the coordinator state file; checked the live cron list; verified session ids across the state file, thu-tu-chay.txt, and the execution plan.
- No browser work was needed. No agent capability was assumed; session ids and watchdog existence were verified against live records (state file, cron list), not taken from the draft's claims.
