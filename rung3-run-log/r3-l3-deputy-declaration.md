# R3-L3 Deputy Coordinator Declaration (FRESH, RE-CONFIRMATION, ROUND-2 FIX)

- Deputy session ID: f41d8a84-3a3d-45d2-bb28-62a75fb98930
- Date and time read: 2026-11-25 11:59:05 +07 (Asia/Ho_Chi_Minh)
- Role: deputy coordinator for run code R3-L3 (rung 3, run code R3-L3)

## What this replaces

This declaration REPLACES the declaration of 2026-11-25 11:43:12 +07 (deputy session 6f9f3647-b92a-4b19-bdcd-6b6d88cafb9e, commit 590be03c) AND the declaration of 2026-11-25 09:34 +07 (deputy session 8397cff5-3099-4735-93fb-34415db38a3c). Session 8397cff5 is SUPERSEDED and holds no deputy authority. Session 6f9f3647 is superseded by me: its declaration was correct (it certified the FINAL committed worktree re-plan with the corrected facts), but it completed and its identity was never propagated past its own file, so the re-plan, the state file, and the run order still named 8397cff5. I am the new deputy, and in this same round-2 fix I updated ALL deputy pointers to my own session id before writing this declaration. This declaration is written after the final state-file edit of the round-2 fix (state file last_updated 2026-11-25T11:56:17+07:00), so it satisfies G-24.

## What I read

I read the following files in full before writing this declaration, verifying each live:

- ~/workspace/r3l3-run-wt/improvements/r3-l3-replan-final-20261124.md (FINAL committed worktree re-plan as it stands after my round-2 fixes, 363 lines measured with wc -l; origin/todolist-push = b26a34c5 at time of reading).
- ~/workspace/r3-l3-execution-plan-20261124.md (the execution plan, 577 lines, measured with wc -l; stamped SUPERSEDED ON IDS by Phase 0 gate G-32, canonical sources are the state file, thu-tu-chay.txt, and the worktree re-plan).
- ~/workspace/r3l3-run-wt/rung3-run-log/r3-l3-coordinator-state.json (CURRENT state file, last_updated 2026-11-25T11:56:17+07:00, verified live, parses as JSON, 28 notes).
- ~/workspace/r3l3-run-wt/rung3-run-log/r3-l3-deputy-declaration.md (the previous deputy's 11:43:12 declaration, to see what it certified and what is now superseded).
- ~/workspace/r3l3-run-wt/rung3-run-log/thu-tu-chay.txt (the run order; verified live: 55 tokens in the order line, DP-03 at position 34, R3-047 absent, token 25 is R3-029, token 49 is R3-089, 0 duplicates; sha256 a759ad21266743beea94e7e22bf962c3a380aa2efadee86d0461f9bf8ae2395d).
- ~/workspace/r3l3-run-wt/rung3-run-log/du-phong.txt (sha256 7d17b9b73584bfcafe0c238bc328859c011a263232df748ade7e098fe2889290, laptop copy re-synced byte-identical).
- ~/workspace/r3l3-run-wt/rung3-run-log/r3-l3-deputy-dry-run-20261125.md (dry-run record, including my own re-run PASS line 11:53 +07).

## Corrected facts, verified live from the files

- R3-029 runner is FCC, position 25. Re-plan section 6, exact wording: "The runner (FCC, position 25) receives the password in its task brief only, never in a repo file and never in a chat message to a third party. (Corrected 25/11 Phase 0: position 25 is in the FCC lane, positions 1-28; the re-plan previously named Codex here in error.)" The credential goes in the FCC task brief only, never in a file.
- Chain-broken AND rule, re-plan section 8, exact wording: "Chain-broken definition: the chain is broken if a worker is unreachable for 15 minutes AND no per-task report appears for 30 minutes while a task is outstanding. A missing report alone, with a live heartbeat, is normal for a long task and does not break the chain. A missing ack does NOT define a broken chain (acks are batched, so a missing ack is normal)." The same AND condition is the reporting-chain trigger in the section 5 watchdog table: "(b) No per-task report for 30 minutes while a task is outstanding AND no coordinator heartbeat for 15 minutes (reporting-chain alert)." A missing report alone, with a live heartbeat, does NOT trigger a takeover.
- R3-047 is DROPPED from the run entirely. Re-plan section 0A, exact wording: "R3-047 DROPPED (owner order, 25/11 10:34): R3-047 is OUT of the run entirely. It does NOT run, is NOT an invalid, consumes 0 invalids (council 3/3 unanimous). Medium backup DP-03 replaces it at position 34 (Option A; run stays 55 tasks, bar stays 53/55, difficulty mix and Class L/S counts unchanged)." Verified in thu-tu-chay.txt: DP-03 is at position 34, R3-047 does not appear in the order. The run is 55 tasks, pass bar 53/55.
- Line counts, measured live with wc -l after my edits: worktree re-plan 363 lines; execution plan 577 lines.
- Backup order: medium DP-03, DP-06, DP-07 in that order; hard DP-02 only; very hard DP-05 only. DP-01 is RETIRED and is never assigned. Execution plan line 327, exact wording: "When a task is declared invalid, the coordinator assigns the first unused backup of the same difficulty, in the fixed order in du-phong.txt (medium: DP-03, DP-06, DP-07; hard: DP-02 only; very hard: DP-05 only). DP-01 is retired and is never assigned." DP-03 is already used (position 34, replacing R3-047), so the remaining medium backups are DP-06, DP-07, in that order (du-phong.txt: "Du phong trung binh con lai: DP-06, DP-07.").

## Current state (re-confirmed, timestamp after the last state-file update)

- Run code: R3-L3. Status: PHASE 0 - PREPARATION, RUN NOT STARTED.
- Current position: 0. Completed positions: 0. No task has started. No task has been graded. Pass count 0, fail count 0, invalid count 0.
- Run order: FCC lane positions 1-28, R3-001 to R3-037. Codex lane positions 29-55, R3-040 to R3-100. Task 1 is R3-001 (FCC lane).
- Runners: FCC via tmux session r3-fcc-runner-L3 on the laptop (pane PID 22399, fcc-claude 2.1.332, recreated 2026-11-25 09:00:18 after the laptop reboot, lane brief acknowledged in writing FCC 11:36 +07 with follow-up 11:39, Codex 11:37:33 +07, per the round-1 acks report). Codex via `codex exec` (0.172.0, non-interactive, one invocation per task from /home/james, no interactive session because the TUI stalls in tmux).
- Scorers (canonical, from the state file): Pair A scorer 1 Mochi (session 70cd99d1-ecef-4d02-9f42-714d7e86ab85), Pair A scorer 2 dc7e0d0d-24b2-4d94-9729-f106d21eff16, Pair B scorer 1B 4e2f52d4-f3f7-41ad-a302-78f0aee91895, Pair B scorer 2B 2e3ae678-2a82-496e-b301-7ac090356fb3, Pair A tiebreaker TB-A 97290681-d2ce-4230-9869-13c1c68df5d1, Pair B tiebreaker TB-B2 df4defcc-050b-47c0-8609-cb2932e36207. TB-B2 independent sign-off DONE (G-33, 4/4 re-graded from scratch).
- Class L: 9 tasks (R3-001, R3-055, R3-074, R3-075, R3-089, R3-096, R3-078, R3-079, R3-088). Class S: 46 tasks.
- Frozen hashes (from the state file): H1 9b9d900, H2 5fac0eb. Key JSON sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8. Keys md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60. List sha256 c1d9a220fa9a5fe57f509cd386c2b28ad466aaecdfb053ad35b5723c697d29ec. todolist-push tip 81919c0c (prepare baseline).
- Pass bar: 53/55. Invalid cap: max 5 total, max 2 per difficulty group.
- Coordinator: Phase 0 coordinator 68a84d25-2e88-48b1-b2ee-9911e2a4191c. The run coordinator will be named at task 1; I take over from the coordinator state file if that coordinator dies, under the fencing rules below.
- State file path I will read to resume: /home/hatch/workspace/r3l3-run-wt/rung3-run-log/r3-l3-coordinator-state.json. The worktree is /home/hatch/workspace/r3l3-run-wt/, branch todolist-push.

## Deputy field note

The state file's deputy field now names my session f41d8a84-3a3d-45d2-bb28-62a75fb98930 (round-2 fix, this declaration). The re-plan, the state file, and thu-tu-chay.txt line 38 all name me as the live deputy. No operative file names 8397cff5 or 6f9f3647 as the live deputy; every remaining mention of those sessions is marked superseded or historical. I did not edit the state file after writing this declaration: the state file last_updated (2026-11-25T11:56:17+07:00) is before this declaration timestamp (2026-11-25 11:59:05 +07).

## Takeover fencing (re-plan section 7)

I take over ONLY under the fencing rules: I verify the coordinator is DEAD (via the parent plus state-file mtime: no heartbeat for 15 minutes AND the state file has not been written for 15 minutes), not merely silent. I write a takeover record into the state file BEFORE issuing any order (coordinator_active set to my id, epoch incremented, timestamp, reason). Workers obey only the coordinator id named in the state file field coordinator_active. The old coordinator stops writing the moment it is no longer active. If the coordinator is alive but unreachable, I do NOT take over; I restore the channel instead (restart the daemon, restart the supervisor, verify read.py works within 5 minutes, then confirm the coordinator is reachable). The wake chain is: cron alerts the parent, the parent messages me to take over (the parent is the only party that can reach a standby subagent session).

## Dry run (G-38)

The dry run was re-run by me in my own session on 2026-11-25 11:53:43-11:53:49 +07. Record: rung3-run-log/r3-l3-deputy-dry-run-20261125.md (appended re-run section). Result: PASS. SSH via ~/workspace/ssh-laptop.sh OK (hostname omarchy, laptop clock 11:53:48 +07); tmux has-session r3-fcc-runner-L3 OK (session alive); state file read plus JSON parse OK (last_updated 2026-11-25T11:33:08+07:00 at time of read, status PHASE 0, RUN NOT STARTED, position 0); git log tip b26a34c5, working tree clean. The 09:32-09:34 dry run by the previous deputy 8397cff5 remains the full contact-path table; my re-run proves this session itself can reach the laptop and read the state file.

## Standby and fencing commitment

I am on STANDBY. I will NOT start any task on my own. I will NOT message the user directly. I will NOT write to the ledger. I will NOT issue run orders while on standby. I will only act as coordinator if the coordinator is confirmed unavailable under the fencing rules above, or if the parent agent directs me to take over. If told to take over, I will first re-read the coordinator state file at the path above and resume coordination from the recorded position. If told to stand down, I will end.
