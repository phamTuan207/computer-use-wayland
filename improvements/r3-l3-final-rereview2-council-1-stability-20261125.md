# Final R3-L3 Prepare RE-REVIEW ROUND 2, Council 1 (Stability / Risk)

- Role: Council 1, stability and risk lens, FRESH reviewer for round 2 (not the round 1 reviewer, not the author of the original Council 1 verdict).
- Date: Wed 2026-11-25, review written 11:45-12:05 +07.
- Scope: round 2 re-review of the fixes for the round 1 re-review (owner order 25/11 11:19, unanimous bar). I verified the committed files myself at HEAD 590be03c on branch todolist-push in ~/workspace/r3l3-run-wt (working tree clean, remote tip matches via ls-remote). I did NOT trust the coordinator's summaries or the round 1 verdicts. I did NOT edit any run doc. I did NOT commit. I did NOT start the run. I did NOT run any run task.
- Live checks done in this review: git log and ls-remote (tip 590be03c), wc -l line counts, token count of the order line, sha256 recomputation of thu-tu-chay.txt and du-phong.txt, JSON parse of the state file, grep sweeps for both deputy session ids, em/en dash sweep of 7 key files (zero hits), cron.list plus cron.status for all 6 run watches, read-only hyprctl workspaces via ssh-laptop.sh (Zen on ws1, no ws2, ws3 has 4 windows; nothing moved, nothing navigated).

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

## Verdict: DISAGREE

One blocking item remains: RB-1, the fresh deputy id 6f9f3647 appears in exactly one file (its own declaration), while the operative re-plan, the state file, and the run order still name the superseded deputy 8397cff5 as the live deputy, and no G-32 pass has run since the deputy commit 590be03c. The deputy re-confirmation itself is genuine and satisfies G-24 on substance (see verification below), but the round 1 fix landed the new deputy without carrying the deputy id through the docs, which is the same stale-id failure mode the final redteam already ruled blocking once (B-F3: update the deputy field NOW, not at task 1). Everything else in my scope is verified, including all other round 1 items (RB-2, B-1, N-01, N-02, N-04, N-05, N-06), the takeover fencing, the Zen move guard, full watchdog coverage, and all failure modes. Two non-blocking SHOULD items remain (NB-1, NB-2). Once RB-1 lands, my verdict flips to AGREE.

## What the deputy re-confirmation genuinely proves (G-24 substance: VERIFIED)

- Fresh deputy session 6f9f3647-b92a-4b19-bdcd-6b6d88cafb9e, declaration timestamp 2026-11-25 11:43:12 +07, committed in 590be03c (verified via ls-remote, origin/todolist-push now equals 590be03c).
- Timestamp ordering holds: state file last_updated is 2026-11-25T11:33:08+07:00 (file mtime 04:33:15 UTC), declaration 11:43:12 +07 is after it. The declaration explicitly states it was written after the last state-file edit.
- It certifies the FINAL committed worktree re-plan (improvements/r3-l3-replan-final-20261124.md, commit 4289e277, 363 lines measured by me with wc -l), not the superseded root copy. The re-plan content is identical between 4289e277 and 590be03c (git diff shows only the declaration file changed), so the certification still covers the current committed re-plan.
- It names the corrected facts with exact quotes: R3-029 runner FCC at position 25 (re-plan section 6), the chain-broken AND rule (re-plan section 8 and the section 5 watchdog table), R3-047 DROPPED with DP-03 at position 34, run 55 tasks with bar 53/55, execution plan 577 lines (measured by me with wc -l), remaining medium backups DP-06 then DP-07, DP-01 retired.
- Order line verified by me: thu-tu-chay.txt line 8 has 55 tokens, token 25 is R3-029, token 34 is DP-03, token 49 is R3-089, R3-047 absent from the order.
- Hashes recomputed by me match the state file note exactly: thu-tu-chay.txt f739f22e137af0f307f4f814bcb0246110a724342cbc08b7c705a6110cd8a9ac, du-phong.txt 0cf06dda18cb32a47c99f5d5a4be67d8a8d5541d58c072f0f8e8df5c982f5619.
- No em dash or en dash in the declaration or in the 6 other key files I swept. No R3-029 password value in any file I read (pointer mentions only).

## Round 1 item status (verified in the files)

### RB-1 (round 1 Council 1: deputy re-confirmation): FIXED on substance, NEW residual stale-id defect (see RB-1 below)

- The 09:34 declaration by 8397cff5 certifying the superseded root copy is replaced by the 11:43:12 declaration by fresh deputy 6f9f3647 certifying the FINAL committed worktree re-plan. That is what RB-1 asked for.
- Residual defect: the new deputy id was not carried through the docs. See Remaining blocking items.

### RB-2 (round 1 Council 1: scorer addendum line 11): FIXED

- rung3-run-log/scorer-briefs/rung3-scorer-brief-R3-L3-addendum.md line 11 now reads "Medium backups in order: DP-06, DP-07." DP-03 is no longer listed as available, consistent with lines 46-48 of the same file and du-phong.txt line 10 (DP-03 USED).
- Line 5 now reads "Branch: todolist-push, tip 81919c0c (prepare baseline). Execution plan: ~/workspace/r3-l3-execution-plan-20261124.md (577 lines, authoritative)." Tip 81919c0c is the frozen prepare baseline by the accepted convention (round 1 Council 3), and 577 lines is correct. One leftover word, "authoritative", is NB-2 below, not part of RB-2.

### B-1 (round 1 Council 2: checkpoint trigger): FIXED

- Re-plan line 269 carries the full corrected trigger (pause ONLY if revised run-complete exceeds 31h OR a per-class mean exceeds its estimate by more than 25 percent with at least 3 graded tasks of that class; 22-31h continues with a recorded estimate; 3-hour wall-clock fallback).
- rung3-run-log/r3-l3-time-budget.md lines 31-38 now carry the same full trigger (pause clause, continue clause, 3-hour fallback).
- rung3-run-log/thu-tu-chay.txt line 90 carries the trigger in short form with the pointer to time-budget.md.
- The thu-tu sha256 changed by the edit and was re-recorded in the state file (f739f22e, verified by my recomputation).

### N-01 (round 1 redteam: Zen on ws1, no move step): FIXED

- Re-plan section 0A line 18 documents the move as a coordinator start item: focus Zen, then hyprctl dispatch "hl.dsp.window.move({ workspace = 2 })", then focus ws2, verify with hyprctl workspaces, do NOT release task 1 if Zen is not on ws2, and do NOT move Zen before the run starts.
- Verified live by me (read-only hyprctl workspaces via ssh-laptop.sh, nothing moved): workspaces are 1, special:herdrdrop, 3. No ws2 exists. Zen ("Chat, Muse, Zen Browser") is on ws1. ws3 has 4 windows (the 4 agents), untouched. The move step is still needed at start and is correctly not done yet.
- F-04(e) guard is in the re-plan (section 3) and in both lane briefs (FCC brief line 74, Codex brief line 92): confirm Zen visible on ws2 before driving, do NOT switch workspaces blindly, report to the coordinator and wait.

### N-02 (round 1 redteam: grim/finish lines in both lane briefs): FIXED

- FCC brief line 74 and Codex brief line 92 both carry: verify the pill is actually gone with a grim screenshot after release, not only with status; end the computer-use session (finish) at the end of each task.
- Fresh acks name these lines: FCC 11:36 +07 with follow-up 11:39, Codex 11:37:33 +07 (report improvements/r3-l3-lane-brief-acks-round1-20261125.md, both verified by me as naming all re-issue changes, no-start confirmed).

### N-04 (round 1 redteam: bar pattern in G-46): FIXED

- Re-plan G-46 line 137 records the pattern: valid N needs N-2 (55 needs 53, 54 needs 52, 53 needs 51, 52 needs 50, and so on, per execution plan line 131). The 4-task scenario (valid 53, bar 51/53, notify not stop) is recorded in the same line.

### N-05 (round 1 redteam: lane briefs cite the worktree re-plan path): FIXED

- FCC brief line 5 and Codex brief line 5 both cite ~/workspace/r3l3-run-wt/improvements/r3-l3-replan-final-20261124.md as the ONLY operative plan, with the root copy marked SUPERSEDED.

### N-06 (round 1 redteam: TB-B2 sign-off timestamp): FIXED

- improvements/r3-l3-tbb2-signoff-20261125.md line 4: "Verified: 2026-11-25 Asia/Ho_Chi_Minh. Committed 2026-11-25 09:20:08 +07 in b061f87c (R3-L3 Phase 0 prepare complete)."

### A-09 (round 1 Council 1: Codex brief OpenRouter carve-out): FIXED

- Codex brief line 97 now reads: "NO OpenRouter. Never try it, never propose it. No banned model routes of any kind. (The OpenRouter ban applies ONLY to Opencode; it does not restrict Codex's own backend.)" Codex ack 11:37:33 names it in full.

## Scope checks (1) to (6)

### (1) Deputy re-confirmation vs G-24: SUBSTANCE VERIFIED, consistency broken (RB-1)

- See the G-24 section above. The declaration is genuine, correctly timestamped, and names the corrected facts.
- The break is not in the declaration but around it: the operative docs still name the old deputy. See RB-1.

### (2) Deputy takeover fencing: SOUND, except the deputy-field cross-check names the wrong deputy (RB-1)

- Re-plan section 7: coordinator epoch starting at 1, incremented only on takeover; workers accept only assignments carrying the current epoch; deputy verifies the coordinator is DEAD via the parent plus state-file mtime (no heartbeat for 15 minutes AND no state-file write for 15 minutes), not merely silent; alive-but-unreachable means restore the channel (restart daemon, restart supervisor, verify read.py within 5 minutes), not take over; deputy writes a takeover record into the state file BEFORE issuing any order (coordinator_active set to its own id, epoch incremented, timestamp, reason); workers obey only coordinator_active; old coordinator checks coordinator_active before every ledger write and stops the moment it is no longer active.
- The declaration repeats the fencing correctly, including the AND condition for death and the takeover-record-before-any-order rule.
- The state file correctly has no coordinator_active or epoch field yet (grep finds only a mention inside the final-review note text); both are created by the run coordinator at task 1 before releasing task 1 (re-plan section 0A line 25 and section 7 line 234).
- Residual: the fencing's written cross-check (the state file deputy field, and the re-plan's instruction to message the deputy) names 8397cff5, not the live deputy 6f9f3647. See RB-1.

### (3) Zen-to-ws2 move step: VERIFIED

- See N-01 above. Documented in the re-plan, guarded in both briefs, acked by both runners, live state confirmed by me. The do-not-release-task-1 condition is explicit.

### (4) Watchdog coverage: VERIFIED LIVE, no gaps

- cron.list plus cron.status checked by me at about 11:47 +07. All 6 run watches enabled with 0 consecutive failures and a successful last run inside their interval: r3l3-agents-watch 11:46:34 (5 min), r3l3-coordinator-liveness-watch 11:43:10 (5 min), r3l3-zen-laptop-health 11:43:51 (15 min), r3l3-runner-process-watch 11:43:10 (15 min), r3l3-timeout-watch 11:43:07 (5 min), r3l3-ledger-push-watch 10:48:17 (1 h).
- mei-mochi-15m-watchdog is DISABLED in cron.list. No Gutenberg watch exists in cron.list. All 4 tonight-only watches are DISABLED. pr-head-watch stays enabled (not a run watch).
- Per-agent internal 10-minute watchdogs: all 4 confirmed running at 10:44 +07 (memory log ~/memory/2026-11-25.md lines 428-432 and 540-543: clone1 last run 10:29, clone2 cycle 10:31 OK, mei trial 10:37 with first scheduled run 10:47, mochi running from 10:44). The G-50 bounded gate (verify within 30 minutes of the start order, run starts anyway with the shared watch covering) still applies at start.
- Daemon plus supervisor resilience: folded into the zen-laptop-health watch (daemon socket and supervisor alive checks), with the G-23 kill-and-restart proof on file and the fallback doc rung3-run-log/r3-l3-daemon-fallback.md.

### (5) Failure modes: COVERED

- Coordinator death: F-02 and section 7 fencing, plus F-01 worker self-stop at the task boundary as the floor.
- Deputy takeover: section 7 fencing plus G-38 dry run (PASS 09:32-09:34) plus G-42 wake chain (cron alerts the parent, the parent messages the deputy, the parent is the only party that can reach a standby subagent session).
- Correlated outage: F-23 and G-40, maximum wait 60 minutes then escalate to the owner, backup-exhaustion rule defined, no improvisation.
- Daemon death: G-23 resilience proof, zen-laptop-health fold, fallback doc, file-based heartbeat fallback in section 8 (heartbeats ride the shared JSONL log, not the daemon).
- Zen crash: F-05 and F-21 (pinned tab, RSS polling, 8 GB threshold armed for the Z3 restart, about:unloads baseline), Clone1 risk 4 stale-lock sequence adopted, Marionette PARTIAL recorded as an accepted risk with BiDi primary and Z3 restart as the response.
- Runner stall: F-15 and G-43 (5-minute timeout watcher, alert at 15 minutes, kill at 30 minutes by exact recorded PID only, never pkill -f), G-37 timeout rule resolved (over 30 minutes is FAIL, stop, log, never graded from partial evidence).
- Timeout rule: G-37, recorded in the timeout file and the re-plan, consistent across both.

### (6) Stability risk introduced by the round 1 fixes: ONE, the deputy-id staleness (RB-1)

- The round 1 file fixes themselves (checkpoint trigger, addendum lines, Zen move, grim/finish, worktree path, carve-out, bar pattern, TB-B2 timestamp) are all verified correct in the files and introduce no new risk.
- The one new risk is from the deputy commit 590be03c itself: it changed the live deputy without updating any other doc. See RB-1.

## B-F4 decision: SOUND, do not block

- The drop counts as 0 invalids and the 4-task scenario (valid 53, bar 51/53, notify not stop) follow the pre-declared table (re-plan G-46 line 137, section 9 Phase 3 line 273, du-phong.txt, scorer addendum lines 47-48, state file). The arithmetic checks (55 minus 2 dropped is 53 valid, 53 valid needs 51). This was decided by the team under full autonomy and the bar table was genuinely pre-declared. I do not block on it.

## Remaining blocking items (1)

### RB-1. Stale deputy id across the operative docs after the fresh deputy declaration

- Live deputy: 6f9f3647-b92a-4b19-bdcd-6b6d88cafb9e, declaration 2026-11-25 11:43:12 +07, commit 590be03c.
- Evidence of staleness (grep, all verified by me in the committed tree):
  - The new id 6f9f3647 appears in exactly ONE file: rung3-run-log/r3-l3-deputy-declaration.md line 3. It appears nowhere else in the worktree.
  - The old id 8397cff5 is still named as the live deputy in the re-plan at lines 14, 23, 25, 75, 115, 283, and 361. Line 23 says "Deputy is fresh (25/11 09:34): new deputy declaration written (session 8397cff5)". Line 361 says "the parent messages deputy 8397cff5 for that re-confirmation (G-24)" and "The 09:34 declaration certifies the superseded root copy and does NOT satisfy G-24", which no longer describes the current state (the 11:43 declaration does satisfy G-24).
  - State file rung3-run-log/r3-l3-coordinator-state.json line 28, deputy field: "8397cff5-3099-4735-93fb-34415db38a3c (declaration at ~/workspace/r3-l3-deputy-declaration.md, fresh declaration 2026-11-25 09:34 +07, dry run PASS 09:32-09:34, G-24 and G-38 CLOSED, on STANDBY)".
  - rung3-run-log/thu-tu-chay.txt line 38: deputy session 8397cff5, fresh declaration 09:34 +07.
- No G-32 pass has run since the deputy commit: the last G-32 note in the state file is the 11:33 entry (before 590be03c at 11:43), and git log shows 590be03c changed only the declaration file. The "G-32 zero mismatches" claim from commit 4289e277 therefore does not cover the deputy id, which now mismatches across 4 files.
- The update the declaration relies on is not on any checklist: the declaration says "The run coordinator updates that field when starting task 1", but the coordinator start checklist (re-plan section 0A line 25) lists only coordinator_active and epoch creation, password receipt, and G-50 verification. It does NOT list updating the deputy field. A memory-log note (~/memory/2026-11-25.md line 354) mentions the update, but the operative plan the coordinator reads does not.
- Why this blocks: this is the exact failure mode the final redteam already ruled blocking in B-F3 (state file naming a dead deputy while the live deputy is someone else, with the fix "update the deputy field NOW, not at task 1"), and the team accepted that remedy then (prepare report: deputy field updated to 8397cff5 NOW, with a parse check). The round 1 fix repeated the deferred-update pattern for the new deputy. If the run coordinator forgets the unlisted update, the state file (the machine-readable source of truth the deputy, the coordinator, and the watches read) names a deputy session that is no longer the deputy for the whole run, and the re-plan's written instruction tells the parent to message 8397cff5, a session whose liveness no one has verified since 09:34. The takeover fencing itself keys on coordinator_active, so a takeover by a parent who knows the fresh id still works, but the written cross-check the fencing depends on points at the wrong session, and G-32 (zero mismatches across all run documents) is violated with no re-run.
- What must change (about 10 minutes, no run-design change):
  1. Update the deputy id to 6f9f3647-b92a-4b19-bdcd-6b6d88cafb9e NOW, not at task 1, in: the re-plan (lines 14, 23, 25, 75, 115, 283, 361; replace the 8397cff5 and 09:34 references with 6f9f3647, 11:43:12, and commit 590be03c, and correct line 361 to record that the 11:43 declaration satisfies G-24); the state file deputy field (line 28, atomic write per G-48, parse check, note recording the edit, advance last_updated); thu-tu-chay.txt line 38 (then recompute the thu-tu sha256, re-record it in the state file, and re-sync the laptop copy per the hash discipline).
  2. Re-run G-32 across all run documents to zero mismatches and record it, covering the deputy id in every file.
  3. Deputy 6f9f3647 writes a one-line confirmation timestamped AFTER the state-file edit in step 1. This sequencing is mandatory: round 1 Council 3 ruled that if the state file changes after a deputy confirmation, the deputy must re-confirm again, so the field update must come first and the confirmation second. One line suffices because the changed field is the deputy's own id, which its declaration already asserts (round 1 Council 1 A-08 precedent).
  4. Commit and verify via ls-remote.
- Once RB-1 lands, my verdict flips to AGREE. Task 1 must not release until it lands.

## Remaining non-blocking items (2)

### NB-1. Fresh deputy has not re-proven G-38 laptop reachability for its own session

- File: rung3-run-log/r3-l3-deputy-dry-run-20261125.md, 09:32-09:34 +07, deputy 8397cff5. The dry run proved SSH, tmux, Zen BiDi/Marionette, CDP ports, daemon, and the mei/mochi messaging chain for the OLD deputy session.
- The fresh deputy 6f9f3647 states in its declaration that it has not re-run a dry run. Parent-to-deputy contact is proven by the declaration itself (the parent messaged it and it responded), but deputy-to-laptop reachability (SSH/tmux) for this session is assumed, not proven, and the standing rule is never to assume an agent's capabilities.
- Non-blocking because the dry run proved the procedure and the environment path 2 hours ago, and the new session runs on the same VM with the same tooling (I ran ssh-laptop.sh successfully from this VM during this review). But it is cheap to close.
- What must change: before task 1, deputy 6f9f3647 runs ssh-laptop.sh plus a tmux has-session check for r3-fcc-runner-L3 and records one line in the run log (or in an addendum to its declaration). If it cannot reach the laptop, the deputy role is reassigned per re-plan section 7.

### NB-2. Scorer addendum line 5 still calls the execution plan "authoritative"

- File: rung3-run-log/scorer-briefs/rung3-scorer-brief-R3-L3-addendum.md line 5: "Execution plan: ~/workspace/r3-l3-execution-plan-20261124.md (577 lines, authoritative)." The execution plan's own stamp says SUPERSEDED ON IDS, with canonical sources the state file, thu-tu-chay.txt, and the FINAL re-plan. "Authoritative" contradicts that stamp.
- Non-blocking: no operational impact, the addendum's other lines cite the canonical sources, and the tip and line count are now correct. Delete the one word when the RB-1 fix lands.

## Reasoning

The round 1 fixes are real and I verified them in the committed files, not from any summary: the checkpoint trigger matches across all three files, the addendum lines are fixed, the Zen move is documented and guarded and its live state matches, both briefs carry the grim/finish lines and the worktree path, the Codex carve-out is on line 97, the bar pattern is in G-46, the TB-B2 timestamp is on file, both runners re-acked in writing, all 6 watches show fresh successful runs live, and the order line counts 55 with DP-03 at token 34. The deputy re-confirmation is genuine: fresh session, timestamp after the last state edit, correct facts, correct committed re-plan.

I still say DISAGREE, because the unanimity bar the owner set requires prepare to be perfect, and the fix for round 1's RB-1 introduced a new defect of the same class it fixed: a stale deputy identity in the operative plan, the state file, and the run order, with no G-32 pass since the change and no checklist entry for the update the declaration relies on. The final redteam already ruled this exact pattern blocking once and prescribed updating now, not at task 1. It closes in minutes with the four steps above, and then my verdict is AGREE.

## What this review did not do

- No edits to the re-plan, state file, or any run doc. No commits. No run start. No run task executed.
- I did not re-run the G-35 live checks (Zen, BiDi, FCC tmux, daemon) beyond the read-only hyprctl workspaces check and the cron statuses above, and I did not message any agent. The per-agent internal watchdog confirmations I cite come from the memory log at ~/memory/2026-11-25.md lines 428-432 and 540-543, and the G-50 start verification still applies.
- I did not independently verify the pill-path-check screenshots pixel by pixel; I verified the report file exists, the F-04 text records both PASS results with times, and the lane briefs name the exact acquire and release commands.
