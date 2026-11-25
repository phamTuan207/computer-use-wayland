# Final R3-L3 Prepare RE-REVIEW ROUND 3, Council 1 (Stability / Risk)

- Role: Council 1, stability and risk lens, FRESH reviewer for round 3 (not the round 1 or round 2 reviewer, not the author of any earlier verdict, not the deputy).
- Date: Wed 2026-11-25, review written 12:00-12:05 +07.
- Scope: round 3 re-review of the round-2 fixes for the FINAL R3-L3 prepare (owner order 25/11 11:19, unanimous bar). Stability and risk only. I verified the committed files myself at HEAD 82a9f49e on branch todolist-push in ~/workspace/r3l3-run-wt (working tree clean, remote tip matches via ls-remote). I did NOT trust the brief, the deputy, or the round 2 verdicts. I did NOT edit any run doc. I did NOT commit. I did NOT start the run. I did NOT run any run task.
- Live checks done in this review: git log and ls-remote (tip 82a9f49e), full git diff b26a34c5..82a9f49e (all 9 files), grep sweeps for all three deputy session ids across the worktree, sha256 recomputation of thu-tu-chay.txt and du-phong.txt, JSON parse of the state file, token count of the order line, em/en dash sweep of the 9 changed files (zero hits), password-pointer check, cron.list plus cron.status for all 6 run watches, read-only hyprctl workspaces via ssh-laptop.sh (Zen on ws1, no ws2, ws3 has 4 windows; nothing moved, nothing navigated).

## Standing rules (restated)

- NO OpenRouter. Never try it, never propose it. FCC's built-in OpenRouter-free backend is allowed per the owner's 25/11 decision; the ban covers only Opencode.
- NO em dash (U+2014) or en dash (U+2013) in any file. Use commas, periods, or short hyphens only.
- NO personal info on GitHub (no name, address, email, phone, schedules, photos, accounts, passwords, tokens). The R3-029 password must NOT appear in any file.
- Never assume an agent's capabilities. Check or ASK THE AGENT DIRECTLY in its own chat. Every brief must state the delivery path explicitly.
- Clone1 and clone2 have NO Tailscale or SSH. Repo and web work only. Do NOT give them machine tasks.
- CDP-first observation: CLI and API first, then DOM, screenshot and vision last.
- Never close or navigate any window or tab the owner opened. Never close the 4 agents' windows in ws3.
- The pill MUST be visible on ANY agent control. Pill text is always plain "Computer use active."
- Do NOT edit MEMORY.md. Observations go to ~/memory/2026-11-25.md.
- Do NOT start the run. Do NOT run any run task.

## Verdict: AGREE

All round 2 items in my scope are fixed in the committed files, verified by me from scratch, including the single shared blocking issue (deputy identity) and all three round 2 Council 1 items (RB-1, NB-1, NB-2). No new stability risk was introduced by the round 2 fixes. Task 1 may release on the owner's word.

## The self-service concern: verified independently, not taken on trust

The deputy (session f41d8a84) updated the pointers to itself and then certified the result. That is self-service, so I re-derived every claim from the raw files and the git history myself:

- I ran my own grep sweeps for f41d8a84, 8397cff5, and 6f9f3647 across the whole worktree, read the full lines, and classified each hit as live pointer vs superseded/historical (item 1 below).
- I recomputed both G-32 hashes and the order-line tokens myself (item 9).
- I compared the declaration timestamp against the state file last_updated AND the state file mtime AND the commit time, and confirmed no commit and no state edit follows the declaration (item 2).
- I read the full state-file diff to confirm the final state edit changed no worker list, so the dry-run re-run's contact-path table still covers the current worker set (item 3).
- The propagation is real, not asserted. The self-service pattern that failed in round 2 (a deputy certifying from its own file only) does not recur here: every operative pointer now names f41d8a84.

## Verified items (numbered, each with file + line + evidence)

### 1. Deputy identity propagation is COMPLETE (round 2 C1 RB-1 and redteam R2-B1: FIXED)

New deputy f41d8a84-3a3d-45d2-bb28-62a75fb98930 is the live deputy in every operative pointer, verified by my own grep:

- improvements/r3-l3-replan-final-20261124.md lines 14, 23, 25, 75, 115, 129, 283, 290, 361. Line 23: "Deputy is fresh (25/11 round-2 fix): new deputy declaration written (session f41d8a84-3a3d-45d2-bb28-62a75fb98930)... Session 8397cff5 is SUPERSEDED and holds no deputy authority; session 6f9f3647 is superseded by this deputy." Line 75 (roster): "Deputy coordinator (session f41d8a84-3a3d-45d2-bb28-62a75fb98930, fresh declaration 25/11 round-2 fix...)". Line 115 (G-24 box): cites the round-2 fix declaration by f41d8a84 and records both 8397cff5 and 6f9f3647 as superseded. Line 283 (G-24 checkbox): "fresh declaration by session f41d8a84-3a3d-45d2-bb28-62a75fb98930, written after the final state-file edit of the round-2 fix... Session 8397cff5 is SUPERSEDED and holds no deputy authority." Line 361: "the parent messages deputy f41d8a84-3a3d-45d2-bb28-62a75fb98930 for that re-confirmation (G-24)... the 11:43:12 declaration by 6f9f3647 is superseded by the round-2 fix declaration by f41d8a84-3a3d-45d2-bb28-62a75fb98930, which satisfies G-24."
- rung3-run-log/r3-l3-coordinator-state.json line 28 (deputy field): "f41d8a84-3a3d-45d2-bb28-62a75fb98930 (declaration at ~/workspace/r3-l3-deputy-declaration.md, fresh declaration 2026-11-25, written after the final state-file edit of the round-2 fix, dry run PASS 11:53 +07 in own session, G-24 and G-38 CLOSED, on STANDBY). Session 8397cff5 SUPERSEDED, holds no deputy authority; session 6f9f3647 superseded by this deputy." State notes lines 76 and 78 (FINAL PREPARE REVIEW note and RE-REVIEW ROUND 1 note) now say "parent messages deputy f41d8a84-3a3d-45d2-bb28-62a75fb98930". New note line 79 records the round-2 fix and the supersession.
- rung3-run-log/thu-tu-chay.txt line 38: "Pho dieu phoi vien (deputy): session ID f41d8a84-3a3d-45d2-bb28-62a75fb98930... Session 8397cff5 SUPERSEDED, khong con quyen pho; session 6f9f3647 bi pho moi thay the."
- rung3-run-log/r3-l3-deputy-declaration.md line 3: deputy session f41d8a84-3a3d-45d2-bb28-62a75fb98930. Line 9 replaces both prior declarations (6f9f3647 11:43:12 and 8397cff5 09:34). Line 46 ("Deputy field note"): "No operative file names 8397cff5 or 6f9f3647 as the live deputy; every remaining mention of those sessions is marked superseded or historical." I verified this claim against my grep: every remaining 8397cff5 hit in an operative file is in superseded or historical context (re-plan lines 14, 23, 115, 283, 361; state field and notes; thu-tu line 38; dry-run record line 4, which is the historical 09:32-09:34 record header, superseded by the re-run section). The only other files naming 8397cff5 are the historical final-review verdicts (improvements/r3-l3-final-council-*.md), which are records, not operative docs. The lane briefs name no deputy at all (grep zero hits for all three ids), so no stale pointer hides there.
- Start checklist verify line: re-plan line 25 now ends "...verify the 4 per-agent internal watchdogs within 30 minutes of the start order (G-50); VERIFY the state file deputy field reads f41d8a84-3a3d-45d2-bb28-62a75fb98930 before releasing task 1." This is the checklist entry round 2 C1 RB-1 required. The deferred-update pattern is gone: the field is updated NOW, and the checklist verifies it rather than performing it.
- Commit 82a9f49e ("R3-L3 round-2 fix: deputy identity propagated to f41d8a84, G-38 re-run PASS, R2-M2/C2 O-1/R2-S1/R2-S2/R2-S3 fixed, G-32 zero mismatches"), 9 files changed, tip verified by ls-remote (origin/todolist-push = 82a9f49e), working tree clean.

### 2. Confirmation timestamp ordering holds (G-24: SATISFIED)

- Declaration rung3-run-log/r3-l3-deputy-declaration.md line 4: "Date and time read: 2026-11-25 11:59:05 +07 (Asia/Ho_Chi_Minh)."
- State file rung3-run-log/r3-l3-coordinator-state.json last_updated: 2026-11-25T11:56:17+07:00. Declaration 11:59:05 is 2m48s after it.
- Cross-checked on a second measure: state file mtime 11:58:29 +07, declaration file mtime 11:59:12 +07, commit 82a9f49e at 11:59:40 +07. The declaration postdates the last state-file write on either measure. No state-file edit followed the declaration: no commit after 82a9f49e exists, git status is clean, and the committed state file is byte-identical to disk.
- The declaration states it read the FINAL committed worktree re-plan "as it stands after my round-2 fixes, 363 lines measured with wc -l" (my wc -l confirms 363), the execution plan 577 lines (my wc -l confirms 577), the state file at last_updated 11:56:17 with 28 notes (my JSON parse confirms 28 notes), and the run order (55 tokens, DP-03 at position 34, R3-047 absent; my token count confirms, item 9). It quotes the corrected facts verbatim: R3-029 FCC position 25, chain-broken AND rule, R3-047 dropped with DP-03 at position 34, bar 53/55, remaining medium backups DP-06, DP-07, DP-01 retired.

### 3. G-38 dry run genuinely re-run by f41d8a84 in its own session (round 2 C1 NB-1 and redteam R2-M1: FIXED)

- rung3-run-log/r3-l3-deputy-dry-run-20261125.md, appended section "Re-run by the round-2 fix deputy (G-38, R2-M1)": "Date and time: 2026-11-25 11:53:43-11:53:49 +07. Deputy: f41d8a84-3a3d-45d2-bb28-62a75fb98930. Result: PASS. Contact-path check run in this deputy's own session: SSH via ~/workspace/ssh-laptop.sh OK (hostname omarchy, laptop clock 11:53:48 +07); tmux has-session r3-fcc-runner-L3 OK (session alive); state file read plus JSON parse OK (last_updated 2026-11-25T11:33:08+07:00, status PHASE 0, RUN NOT STARTED, position 0); git log tip b26a34c5, working tree clean."
- This is a dated PASS line for the new session, not the old deputy's record. The 09:32-09:34 full contact-path table (previous deputy 8397cff5) is retained as the procedure record and explicitly re-confirmed as such.
- One sequencing nuance, checked and closed: the re-run read the state file at last_updated 11:33:08, and the final state edit landed at 11:56:17, after the re-run. I read the full state-file diff b26a34c5..82a9f49e: the final edit changed only the deputy field, the freeze tip qualifier, last_updated, and notes. The runners, scorers, and tiebreaker sections are untouched, so the worker set the re-run listed is identical to the current worker set. The contact-path verification stands. The deputy then re-read the state file for the declaration at 11:59:05 (last_updated 11:56:17).
- Re-plan G-38 box (line 129) and section 7 line 237 now name the re-run: "RE-RUN 25/11 11:53 +07 by the round-2 fix deputy f41d8a84-3a3d-45d2-bb28-62a75fb98930, PASS."

### 4. Scorer addendum "authoritative" word deleted (redteam R2-M2: FIXED)

- rung3-run-log/scorer-briefs/rung3-scorer-brief-R3-L3-addendum.md line 5 now reads: "Branch: todolist-push, tip 81919c0c (prepare baseline). Execution plan: ~/workspace/r3-l3-execution-plan-20261124.md (577 lines)." The word "authoritative" is gone. This matches the execution plan's own line 3 stamp (SUPERSEDED ON IDS, canonical sources the state file, thu-tu-chay.txt, and the FINAL re-plan). Line 11 still reads "Medium backups in order: DP-06, DP-07." DP-03 is not listed as available.

### 5. Pause-release default aligned (round 2 C2 O-1: FIXED)

- rung3-run-log/r3-l3-time-budget.md lines 31-38 now read: "The run continues on the owner's decision; if the owner is unreachable within 30 minutes, the default is continue, record the estimate, and re-check at the next milestone (re-plan line 269, pre-authorized before task 1)."
- Re-plan line 269 carries the same default in full: "The checkpoint decision is pre-authorized before task 1: the owner picks continue, stop, or add scorers, with a default if unreachable within 30 minutes (default: continue, record the estimate, and re-check at the next milestone)." The two files agree; the previous contradiction is gone.

### 6. TB-B2 verifier session id recorded as a limitation (redteam R2-S1: FIXED per the redteam fallback)

- improvements/r3-l3-tbb2-signoff-20261125.md, appended "Round-2 fix note (R2-S1, 2026-11-25)": "The verifier session id was searched in the prepare records (memory log ~/memory/2026-11-25.md, the prepare report, this sign-off file) and is NOT recoverable... Commit-identification is accepted instead: this sign-off is identified by commit b061f87c, committed 2026-11-25 09:20:08 +07. N-06 is closed as a recorded limitation, per the round-2 redteam fallback (fix if recoverable, otherwise accept commit-identification)." This is exactly the fallback the redteam prescribed. Honest and auditable, not silently missing.

### 7. Declaration stale pointers fixed (redteam R2-S2: FIXED)

- Declaration line 15 phrases the tip as at-time-of-reading: "origin/todolist-push = b26a34c5 at time of reading." (Committing the declaration itself moved the tip to 82a9f49e; the at-time-of-reading phrasing is what R2-S2 prescribed, and the deputy authored the 82a9f49e changes itself before writing the declaration, so the certification covers the committed content.)
- Declaration runners paragraph cites the fresh lane-brief acks: "lane brief acknowledged in writing FCC 11:36 +07 with follow-up 11:39, Codex 11:37:33 +07, per the round-1 acks report." The stale 09:06 citation is gone.

### 8. Tip qualifier added in all three places (redteam R2-S3: FIXED)

- rung3-run-log/thu-tu-chay.txt line 2: "Branch todolist-push tip 81919c0c (prepare baseline)."
- rung3-run-log/du-phong.txt line 2: "Branch todolist-push tip 81919c0c (prepare baseline)."
- State file freeze field: "todolist_push_tip": "81919c0c (prepare baseline)" (verified in the state diff and by JSON parse).
- All four stamps (including addendum line 5) now agree, which is what G-32 checks.

### 9. G-32 re-run to zero mismatches (round 2 C1 RB-1 step 2: DONE)

- Recomputed by me live: thu-tu-chay.txt sha256 a759ad21266743beea94e7e22bf962c3a380aa2efadee86d0461f9bf8ae2395d; du-phong.txt sha256 7d17b9b73584bfcafe0c238bc328859c011a263232df748ade7e098fe2889290. Both match the state file round-2 fix note exactly. The 11:33 hashes (f739f22e, 0cf06dda) are recorded as superseded in the same note.
- Order line verified by me: thu-tu-chay.txt line 8 has 55 tokens, token 25 is R3-029, token 34 is DP-03, token 49 is R3-089, R3-047 absent from the order, 0 duplicates. R3-047 appears only in the note line 83 ("DA LOAI BO KHOI RUN... KHONG chay, KHONG phai INVALID, KHONG tinh vao muc tran (0 invalid). DP-03 thay the o vi tri 34") and in the DP-03 note line 74. State file parses as JSON, status "PHASE 0 - PREPARATION, RUN NOT STARTED", position 0, pass 0, fail 0, invalid 0, no coordinator_active or epoch field yet (correct pre-start; both are created by the run coordinator at task 1).
- Re-plan is 363 lines, execution plan 577 lines by my wc -l, matching the declaration.

### 10. Deputy takeover fencing is SOUND and unchanged

- I read the full re-plan diff b26a34c5..82a9f49e: 8 hunks, all deputy-identity only (lines 14, 23, 25, 75, 115, 129, 237, 283, 290, 361). Section 7 fencing is untouched except the G-38 line noting the re-run (item 3). The fencing still reads: coordinator epoch starting at 1, incremented only on takeover; workers accept only assignments carrying the current epoch; deputy verifies the coordinator is DEAD via the parent plus state-file mtime (no heartbeat for 15 minutes AND no state-file write for 15 minutes), not merely silent; alive-but-unreachable means restore the channel (restart daemon, restart supervisor, verify read.py within 5 minutes), not take over; deputy writes a takeover record into the state file BEFORE issuing any order (coordinator_active set to its own id, epoch incremented, timestamp, reason); workers obey only coordinator_active; old coordinator checks coordinator_active before every ledger write and stops the moment it is no longer active.
- The declaration repeats the fencing correctly, including the AND condition for death and the takeover-record-before-any-order rule, and commits to standby (no task starts, no direct messages to the owner, no ledger writes, no run orders while on standby).
- The written cross-check that round 2 found broken (state deputy field, re-plan instruction to message the deputy) now names f41d8a84 everywhere (item 1). The two-deputy ambiguity is resolved in the files: 8397cff5 is recorded superseded with no authority in the re-plan, the state file, thu-tu-chay.txt, and the declaration. Whether the old session is actually ended is a parent-side G-42 liveness matter; no file directs anyone to it anymore.

### 11. Zen-to-ws2 move step and F-04(e) guard are CORRECT

- Re-plan section 0A line 18 documents the move as a coordinator start item: focus Zen, then hyprctl dispatch "hl.dsp.window.move({ workspace = 2 })", then hyprctl dispatch "hl.dsp.focus({ workspace = 2 })", verify with hyprctl workspaces that Zen is on ws2 before releasing task 1; "if Zen is not on ws2, do NOT release task 1, report to the parent. Zen is NOT moved before the run starts (the owner uses ws1); the move is a coordinator start item only."
- Verified live by me (read-only hyprctl workspaces via ssh-laptop.sh, nothing moved, nothing navigated): workspaces are 1, special:herdrdrop, 3. No ws2 exists. Zen ("Chat, Muse, Zen Browser") is on ws1 (1 window). ws3 has 4 windows (the 4 agents), untouched. The move step is still needed at start and is correctly not done yet.
- F-04(e) guard is in both lane briefs, read in full by me: FCC brief line 74 and Codex brief line 92 both carry the complete guard text: verify the pill is actually gone with a grim screenshot after release, not only with status; end the computer-use session (finish) at the end of each task; drives run on ws2; before driving, confirm Zen is visible on ws2; if Zen is not visible on ws2, do NOT switch workspaces blindly; report to the coordinator and wait. (Note: the brief lines do not carry the literal label "F-04(e)"; the guard text itself is present in full. The label lives in the re-plan G-26 box, line 284.)

### 12. Watchdog coverage is COMPLETE with no gaps (verified live)

- cron.list plus cron.status checked by me at about 12:03 +07. All 6 run watches enabled with 0 consecutive failures and a successful last run inside their interval: r3l3-agents-watch 11:59:59 (5 min, one run in flight at check time), r3l3-coordinator-liveness-watch 12:03:16 (5 min), r3l3-zen-laptop-health 11:59:17 (15 min), r3l3-runner-process-watch 11:59:23 (15 min), r3l3-timeout-watch 12:03:07 (5 min), r3l3-ledger-push-watch 11:48:32 (1 h).
- mei-mochi-15m-watchdog is DISABLED in cron.list. No Gutenberg watch exists in cron.list. All 4 tonight-only watches are DISABLED. pr-head-watch stays enabled (not a run watch).
- Per-agent internal 10-minute watchdogs: all 4 confirmed running at 10:44 +07 (memory log ~/memory/2026-11-25.md lines 541-543 and 602-610: clone1 last run 10:29, clone2 cycle 10:31 OK, mei trial 10:37 with first scheduled run 10:47, mochi running from 10:44; agents-watch run log 11:48 confirms all 4 healthy, clone2 watchdog 11:38 fine). The G-50 bounded gate (verify within 30 minutes of the start order, run starts anyway with the shared watch covering) still applies at start.
- Daemon plus supervisor resilience: folded into the zen-laptop-health watch (daemon socket and supervisor alive checks), with the G-23 kill-and-restart proof on file and the fallback doc rung3-run-log/r3-l3-daemon-fallback.md.

### 13. Failure modes are COVERED

- Coordinator death: F-02 and section 7 fencing, plus F-01 worker self-stop at the task boundary as the floor.
- Deputy takeover: section 7 fencing plus G-38 dry run (PASS 09:32-09:34, re-run PASS 11:53 by the live deputy) plus G-42 wake chain (cron alerts the parent, the parent messages the deputy, the parent is the only party that can reach a standby subagent session).
- Correlated outage: F-23 and G-40, maximum wait 60 minutes then escalate to the owner, backup-exhaustion rule defined, no improvisation.
- Daemon death: G-23 resilience proof, zen-laptop-health fold, fallback doc, file-based heartbeat fallback in section 8 (heartbeats ride the shared JSONL log, not the daemon).
- Zen crash: F-05 and F-21 (pinned tab, RSS polling, 8 GB threshold armed for the Z3 restart, about:unloads baseline), Clone1 risk 4 stale-lock sequence adopted, Marionette PARTIAL recorded as an accepted risk with BiDi primary and Z3 restart as the response.
- Runner stall: F-15 and G-43 (5-minute timeout watcher, alert at 15 minutes, kill at 30 minutes by exact recorded PID only, never pkill -f), G-37 timeout rule resolved (over 30 minutes is FAIL, stop, log, never graded from partial evidence).
- None of these texts changed in the round-2 fix (the 9-file diff touches none of them), so no failure-mode coverage was lost or altered.

### 14. No new stability risk introduced by the round-2 fixes

- The 9-file diff b26a34c5..82a9f49e is, in full: re-plan deputy-identity lines only; state file deputy field, tip qualifier, last_updated, and notes; thu-tu-chay.txt tip qualifier and deputy line; du-phong.txt tip qualifier; time-budget pause default; scorer addendum one-word deletion; tbb2 sign-off R2-S1 note; deputy declaration rewritten; dry-run record re-run section appended. Nothing touches the run order, the lane briefs, the failure-mode texts, the watchdog configuration, or the fencing rules (except the G-38 re-run note). No file outside these 9 changed.
- The B-F4 decision (drop counts as 0 invalids; 4-task scenario valid 53, bar 51/53, notify not stop) was decided by the team under full autonomy and the redteam confirmed the bar table was genuinely pre-declared. I do not block on it. The arithmetic checks (55 minus 2 dropped is 53 valid, 53 valid needs 51) and the pattern is recorded in re-plan G-46 line 137.
- R3-047 stays dropped by owner order 25/11 10:34, DP-03 at position 34, run 55 tasks, bar 53/55 (items 2 and 9).

### 15. Standing-rule hygiene in the round-2 fix

- Em/en dash sweep of all 9 changed files, by code point: 0 em dashes, 0 en dashes.
- R3-029 password: pointer-only references only in every file I read (re-plan section 6, state note, thu-tu-chay.txt line 81 "Mat khau tai khoan test trong Secure Vault, khong ghi o day", declaration). No password value appears in any file.
- FCC backend: the dry-run record notes fcc-server returns provider open_router via FCC's built-in backend, allowed per the owner's 25/11 decision; the ban covers Opencode only. No OpenRouter use is proposed anywhere in the round-2 fix.

## Observations (non-blocking, recorded for the record, none affects the verdict)

- O-1. The state file mtime (11:58:29 +07) is 2m12s after its internal last_updated (11:56:17). The declaration (11:59:05) postdates both, so the G-24 ordering holds on either measure. Most likely the atomic temp-file-plus-rename write landed at 11:58:29. Not a defect, noted only because I checked both measures.
- O-2. The declaration's tip pointer (b26a34c5 at time of reading) is now one commit behind the tip (82a9f49e) because committing the declaration itself moved the tip. This is the exact phrasing round 2 redteam R2-S2 prescribed, and the deputy authored the 82a9f49e changes before writing the declaration, so the certification covers the committed content. Not a defect.
- O-3. Whether old session 8397cff5 is actually ended (vs merely superseded on paper) is a parent-side G-42 liveness matter I cannot verify from the VM. No file directs anyone to it anymore, so an alive old session has no path into the run. Not a defect.
- O-4. The lane-brief guard lines do not carry the literal label "F-04(e)"; the full guard text is present (item 11). A future reader grepping for the label in the briefs will miss it. Cosmetic only; the re-plan G-26 box names it.

## What this review did not do

- No edits to the re-plan, state file, or any run doc. No commits. No run start. No run task executed.
- I did not re-run the G-35 live checks (Zen, BiDi, FCC tmux, daemon) beyond the read-only hyprctl workspaces check, the cron statuses above, and the dry-run record; nothing in the round-2 fix touches those systems, and the dry-run re-run re-proved SSH, tmux, and state-file reachability at 11:53. I did not message any agent. The per-agent internal watchdog confirmations I cite come from the memory log and the agents-watch run log at 11:48, and the G-50 start verification still applies.
- I did not independently verify the pill-path-check screenshots pixel by pixel; I verified the report file exists, the F-04 text records both PASS results with times, and the lane briefs name the exact acquire and release commands.
