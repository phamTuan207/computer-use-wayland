# R3-L3 Deputy Coordinator Declaration (FRESH)

- Deputy session ID: 8397cff5-3099-4735-93fb-34415db38a3c
- Date and time read: 2026-11-25 09:34 +07 (Asia/Ho_Chi_Minh)
- Role: deputy coordinator for run code R3-L3 (rung 3, run code R3-L3)

## What this replaces

This declaration REPLACES the stale declaration of 2026-11-24 17:24:46 +07 (deputy session 028399b1). That session is gone, and its declaration listed the rejected tiebreaker B 9d613f19 (3/4, NOT APPROVED). I am a fresh deputy. The current tiebreaker B is TB-B2 df4defcc.

## What I read

I read the following files in full before writing this declaration:

- /home/hatch/workspace/r3-l3-replan-final-20261124.md (FINAL re-plan, commit 81919c0c, the operative plan)
- /home/hatch/workspace/r3-l3-execution-plan-20261124.md (565 lines, stamped SUPERSEDED ON IDS by Phase 0 gate G-32; canonical sources are the state file, thu-tu-chay.txt, and the re-plan)
- /home/hatch/workspace/r3l3-run-wt/rung3-run-log/r3-l3-coordinator-state.json (CURRENT state file, last updated 2026-11-25T09:15:00+07:00)

## Current state (re-confirmed, timestamp after the last state-file update)

- Run code: R3-L3. Status: PHASE 0 - PREPARATION, RUN NOT STARTED.
- Current position: 0. Completed positions: 0. No task has started. No task has been graded. Pass count 0, fail count 0, invalid count 0.
- Run order: FCC lane positions 1-28, R3-001 to R3-037. Codex lane positions 29-55, R3-040 to R3-100. Task 1 is R3-001 (FCC lane).
- Runners: FCC via tmux session r3-fcc-runner-L3 on the laptop (pane PID 22399, fcc-claude 2.1.332, recreated 2026-11-25 09:00:18 after the laptop reboot, lane brief acknowledged in writing 09:06). Codex via `codex exec` (0.172.0, non-interactive, one invocation per task from /home/james, no interactive session because the TUI stalls in tmux).
- Scorers (canonical, from the state file): Pair A scorer 1 Mochi (session 70cd99d1-ecef-4d02-9f42-714d7e86ab85), Pair A scorer 2 dc7e0d0d-24b2-4d94-9729-f106d21eff16, Pair B scorer 1B 4e2f52d4-f3f7-41ad-a302-78f0aee91895, Pair B scorer 2B 2e3ae678-2a82-496e-b301-7ac090356fb3, Pair A tiebreaker TB-A 97290681-d2ce-4230-9869-13c1c68df5d1, Pair B tiebreaker TB-B2 df4defcc-050b-47c0-8609-cb2932e36207. TB-B2 independent sign-off DONE (G-33, 4/4 re-graded from scratch).
- Class L: 9 tasks (R3-001, R3-055, R3-074, R3-075, R3-089, R3-096, R3-078, R3-079, R3-088). Class S: 46 tasks.
- Backups: medium DP-03, DP-06, DP-07 in that order. Hard DP-02 only (Class L). Very hard DP-05 only. DP-01 is RETIRED and is never assigned.
- Frozen hashes: H1 9b9d900, H2 5fac0eb. Key JSON sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8. Keys md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60. List sha256 c1d9a220fa9a5fe57f509cd386c2b28ad466aaecdfb053ad35b5723c697d29ec. todolist-push tip 81919c0c.
- Pass bar: 53/55. Invalid cap: max 5 total, max 2 per difficulty group.
- R3-029 runner is FCC, position 25 (corrected in Phase 0 25/11; the re-plan section 6 previously named Codex in error). The R3-029 credential goes in the FCC task brief only, never in a file.
- Messaging chain PASS (G-23): speed daemon alive on the VM, read.py ok=true for mei (25 items) and mochi (34 items), daemon resilience proven.
- R3-089 fixture healthy (G-39): 6 files log-01..06 within 7 days. Pill live test PROVEN (G-44, BiDi drive with pill visible).
- Coordinator: Phase 0 coordinator 68a84d25-2e88-48b1-b2ee-9911e2a4191c. The run coordinator will be named at task 1; I take over from the coordinator state file if that coordinator dies.
- State file path I will read to resume: /home/hatch/workspace/r3l3-run-wt/rung3-run-log/r3-l3-coordinator-state.json. The worktree is /home/hatch/workspace/r3l3-run-wt/, branch todolist-push.

## Takeover fencing (re-plan section 7)

I take over ONLY under the fencing rules: I verify the coordinator is DEAD (via the parent plus state-file mtime), not merely silent. I write a takeover record before issuing any order. Workers obey only the coordinator_active id. The old coordinator stops writing the moment it is no longer active. If the coordinator is alive but unreachable, I restore the channel instead of taking over. The wake chain is: cron alerts the parent, the parent messages me to take over (the parent is the only party that can reach a standby subagent session).

## Dry run (G-38)

Done 2026-11-25 09:32-09:34 +07. Record: rung3-run-log/r3-l3-deputy-dry-run-20261125.md. Result: PASS. Laptop reachable via SSH, FCC tmux session alive, fcc-server healthy, Zen BiDi 9222 and Marionette 2828 listening, Chromium 9223 and Brave 9224 CDP live, codex-cli 0.172.0 present, speed daemon alive, read.py ok=true for mei and mochi, R3-089 fixture healthy. Subagent workers (scorers, tiebreakers) are reached via the parent by design (G-42 wake chain); I have no direct channel to another subagent session, and I do not claim one.

## Standby commitment

I will NOT start any task on my own. I will NOT message the user directly. I will only act as coordinator if the coordinator is confirmed unavailable or if the parent agent directs me to take over. If told to take over, I will first re-read the coordinator state file at the path above and resume coordination from the recorded position. If told to stand down, I will end.
