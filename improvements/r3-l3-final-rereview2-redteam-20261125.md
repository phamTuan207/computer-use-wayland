# R3-L3 Final Prepare RE-REVIEW ROUND 2, Redteam Verdict, Wed 2026-11-25

Fresh redteam, re-review round 2. I am independent of round 1 and of all three councils. I verified everything myself from the committed files at HEAD 590be03c on branch todolist-push, worktree ~/workspace/r3l3-run-wt. I did not trust the coordinator's summary or this brief. I did not edit any run file. I did not commit. I did not start the run. I did not run any run task.

## Verdict: NOT READY

The run must NOT start yet. Most of the round-1 fixes are real and verified (N-01, N-02, N-04, N-05, C2 B-1, C3 superseded note, C3 ONLY sentence, C1 A-09, G-32 re-run, fresh lane-brief acks). But the round-1 BLOCKING item B-F2 is only half fixed. The fresh deputy declaration itself is good: session 6f9f3647, timestamp 2026-11-25 11:43:12 +07, after the last state-file edit (11:33:08), naming the corrected facts and certifying the FINAL committed worktree re-plan. What is NOT fixed is the propagation: NOT ONE operative file names the new deputy. Every pointer in the re-plan, the state file, and thu-tu-chay.txt still names the old session 8397cff5 and its 09:34 declaration, and the new declaration itself says that 09:34 declaration does NOT satisfy G-24. The re-plan section 10 G-24 box is checked [x] with a justification that is false as written. The takeover identity is therefore wrong in every file the coordinator will read. Two MUST-FIX items and three SHOULD-FIX items also remain, listed below. All fixes are small and mechanical.

## Standing rules

- NO OpenRouter. Never try it, never propose it. FCC's built-in OpenRouter-free backend is allowed per the owner's 25/11 decision. The ban covers only Opencode.
- NO em dash (U+2014) or en dash (U+2013) in any file. Use commas, periods, or short hyphens only.
- NO personal info on GitHub (no name, address, email, phone, schedules, photos, accounts, passwords, tokens). The R3-029 password must NOT appear in any file. I found no password value in any file I read, only pointers.
- Never assume an agent's capabilities. Check or ASK THE AGENT DIRECTLY in its own chat.
- Clone1 and clone2 have NO Tailscale or SSH. Repo and web work only. Do NOT give them machine tasks.
- CDP-first observation: CLI and API first, then DOM, screenshot and vision last.
- Never close or navigate any window or tab the owner opened. Never close the 4 agents' windows in ws3.
- The pill MUST be visible on ANY agent control. Pill text is always plain "Computer use active."
- Do NOT edit MEMORY.md. Observations go to ~/memory/2026-11-25.md.
- Do NOT start the run. Do NOT run any run task.

## Live checks I ran myself

- git log and ls-remote: HEAD is 590be03c, origin/todolist-push is 590be03c. The round-1 fix commit is 4289e277, the deputy re-confirmation commit is 590be03c (changes ONLY rung3-run-log/r3-l3-deputy-declaration.md, 28 insertions, 18 deletions).
- Hashes recomputed by me: thu-tu-chay.txt f739f22e137af0f307f4f814bcb0246110a724342cbc08b7c705a6110cd8a9ac, du-phong.txt 0cf06dda18cb32a47c99f5d5a4be67d8a8d5541d58c072f0f8e8df5c982f5619. Both match the state file note exactly.
- Order line: 55 tokens, token 34 is DP-03, R3-047 absent, no duplicates. State file parses as JSON, 27 notes, last_updated 2026-11-25T11:33:08+07:00.
- Lane brief hashes match the acks-round1 laptop hashes exactly: FCC 690d408e9de25904f7e9a625c689902d848cd6aaab1734d2155525c54ccaee19, Codex fea1b9c62d48390ee117c7c0c05f196b323d8b6de83672092579c798baa93f5d. The acked briefs are byte-identical to the committed worktree briefs.
- Cron live: r3l3-agents-watch enabled, last success 11:46:34 +07, a run in flight at check time. cron.list shows all 6 r3l3 watches enabled, mei-mochi-15m-watchdog DISABLED, no Gutenberg watch present at all.
- Laptop live via SSH (read-only hyprctl workspaces): workspace 1 holds 1 window (Zen, "Chat - Muse - Zen Browser"), workspace 3 holds 4 windows (the 4 agents), special:herdrdrop holds 1. There is NO workspace 2. Zen is still on ws1, which is the correct pre-start state (the move is a coordinator start item only).
- Move command verified against the Hyprland wiki dispatchers page: `hl.dsp.window.move({ window?, workspace, follow? })` is "Move a window to a workspace", and the migration guide maps `movetoworkspace, 3` to `hl.dsp.window.move({ workspace = 3 })`. The re-plan command `hyprctl dispatch "hl.dsp.window.move({ workspace = 2 })"` is the real documented form.
- No em or en dashes in any of the 10 operative files I checked (python code-point check, 0 hits).

## Round-1 item verification (what round 1 demanded, what I found)

- B-F2 deputy re-confirmation: PARTLY FIXED. The declaration file is fresh and correct (see R2-B1). The propagation is NOT done: zero operative files name 6f9f3647.
- N-01 Zen ws2: FIXED. Move documented as a coordinator start item in re-plan section 0A line 18 with the exact command (verified real, see above), the do-not-release-task-1 condition, and the F-04(e) guard in both briefs (FCC section 9, Codex section 11). Fresh acks name the guard (FCC 11:36 plus 11:39 follow-up, Codex 11:37:33).
- N-02 grim/finish lines: FIXED. In both briefs (FCC section 9, Codex section 11): grim after release, finish at the end of each task.
- N-03 scorer addendum: PARTLY FIXED. Line 11 fixed (DP-06, DP-07), line 5 tip fixed (81919c0c, prepare baseline) and 577 lines. But "authoritative" was NOT removed (see R2-M2).
- N-04 bar pattern: FIXED. Re-plan G-46 line 137 now records "valid N needs N-2 (55 needs 53, 54 needs 52, 53 needs 51, 52 needs 50, and so on, per execution plan line 131)".
- N-05 worktree re-plan path: FIXED. Both briefs line 5 cite ~/workspace/r3l3-run-wt/improvements/r3-l3-replan-final-20261124.md as the ONLY operative plan.
- N-06 TB-B2 sign-off timestamp: PARTLY FIXED. Timestamp added (committed 2026-11-25 09:20:08 +07 in b061f87c). Verifier session id still not recorded (see R2-S1).
- C2 B-1 checkpoint trigger: FIXED. time-budget.md and thu-tu-chay.txt line 90 now match re-plan section 9 line 269: pause ONLY if revised run-complete exceeds 31h OR a per-class mean exceeds its estimate by more than 25 percent with at least 3 graded tasks of that class; 22-31h continues with a recorded estimate; 3-hour wall-clock fallback added. Hash re-recorded (f739f22e, recomputed by me, matches).
- C3 superseded note: FIXED. State file note re-added with a SUPERSEDED marker pointing at the drop note, kept for history, "do NOT act on it". 27 notes total.
- C3 ONLY sentence: FIXED. thu-tu-chay.txt line 84 now ends "Day la NHOM DUY NHAT con lai co the INVALID truoc khi chay o nhom trung binh (R3-047 da loai bo, khong tinh)".
- C1 A-09 Codex carve-out: FIXED. Codex brief line 97 now carries "(The OpenRouter ban applies ONLY to Opencode; it does not restrict Codex's own backend.)". Codex ack item 4 names it in writing.
- G-32 re-run: FIXED. Hashes, order tokens, brief hashes, and tip stamps all agree across the operative files (see live checks above).
- B-F4 backup exhaustion decision: NOT BLOCKING, per the task brief. The pre-declared table is genuine: execution plan line 131 reads "54 valid needs 52, 53 needs 51, and so on", re-plan Phase 3 line 273 and G-46 line 137 record the same. Drop counts as 0 invalids and the 4-task scenario (53 valid, bar 51/53, notify not stop) are consistent across re-plan G-46, du-phong.txt, scorer addendum lines 46-48, and the state file.

## BLOCKING items

### R2-B1. BLOCKING. B-F2 is half fixed: the new deputy exists only in its own declaration file; every operative pointer still names the superseded deputy

Evidence, all read live by me:

- The new declaration is good on its own terms. rung3-run-log/r3-l3-deputy-declaration.md line 2: deputy session 6f9f3647-b92a-4b19-bdcd-6b6d88cafb9e. Line 3: date and time read 2026-11-25 11:43:12 +07. That is AFTER the state file last_updated 2026-11-25T11:33:08+07:00 (state file line 45), so the timestamp ordering satisfies G-24 as of now. It names the corrected facts with exact quotes (R3-029 runner FCC position 25; chain-broken AND; R3-047 dropped, DP-03 at position 34; backup order DP-06, DP-07 remaining) and certifies the FINAL committed worktree re-plan at 4289e277, 363 lines (wc -l confirms 363).
- But 6f9f3647 appears in NO operative file. Grep over the re-plan, state file, thu-tu-chay.txt, du-phong.txt, scorer addendum, both lane briefs, and time-budget.md returns zero hits for 6f9f3647. The ONLY file naming the current deputy is the declaration itself.
- Every pointer still names the old session 8397cff5 and its 09:34 declaration:
  - Re-plan line 14: "deputy re-confirmation and dry run closed 09:34, commit 3a2f45aa".
  - Re-plan line 23: "Deputy is fresh (25/11 09:34): new deputy declaration written (session 8397cff5)... the parent messages deputy 8397cff5 for that re-confirmation."
  - Re-plan line 25: "The deputy field is already updated to 8397cff5." The task-1 start checklist on the same line (create coordinator_active and epoch, receive the R3-029 password, verify the 4 watchdogs) does NOT include updating the deputy field.
  - Re-plan line 75 (roster): "Deputy coordinator (session 8397cff5, fresh declaration 09:34 25/11; the state file field is updated to 8397cff5...)".
  - Re-plan line 115 (G-24): "(CLOSED 25/11 09:34: fresh deputy declaration, session 8397cff5, timestamp after the last state-file update 09:15.)"
  - Re-plan line 283 (section 10 todolist): "[x] G-24: deputy re-confirmed the CURRENT state file in writing, with a new timestamp after the last state-file update (fresh declaration 09:34, session 8397cff5). The deputy re-confirms the FINAL committed re-plan before task 1 (parent messages deputy 8397cff5)."
  - Re-plan line 361 (section 11, What remains): "the parent messages deputy 8397cff5 for that re-confirmation (G-24)."
  - State file line 28 (deputy field): "8397cff5-3099-4735-93fb-34415db38a3c (declaration at ~/workspace/r3-l3-deputy-declaration.md, fresh declaration 2026-11-25 09:34 +07, dry run PASS 09:32-09:34, G-24 and G-38 CLOSED, on STANDBY)".
  - State file lines 76 and 78 (notes): "confirm the deputy re-read the FINAL committed re-plan (parent messages deputy 8397cff5)" and "Deputy re-confirmation is a PARENT action (parent messages deputy 8397cff5)".
  - thu-tu-chay.txt line 38: "Pho dieu phoi vien (deputy): session ID 8397cff5-3099-4735-93fb-34415db38a3c... (ban khai moi 2026-11-25 09:34 +07, dry run PASS 09:32-09:34, G-24 va G-38 da dong)."
- The new declaration itself disqualifies the old one. Declaration line 9: "The 09:34 declaration therefore does NOT satisfy G-24." So the re-plan line 283 [x] box, which cites the 09:34 declaration as the satisfaction of G-24, is false as written. A checked gate box whose justification is disqualified by the very declaration that replaces it cannot stand.
- The declaration's own "Deputy field note" (line 44) admits the state file still names 8397cff5 and asserts "The run coordinator updates that field when starting task 1." But NO committed file instructs the coordinator to do that: the start checklist (re-plan line 25) has no such item, and the state file notes tell the reader the parent messages 8397cff5. The coordinator reading the re-plan would conclude the deputy field is already correct. The update will most likely never happen, and the run would proceed with the state file naming a superseded deputy for all 55 tasks.
- Two-deputy ambiguity: nothing stands down the old session 8397cff5. I could not verify from the VM whether that session is still alive (the parent verifies deputy liveness hourly per G-42, but the files say to verify 8397cff5). If it is alive, two sessions hold deputy declarations and only the newer one is valid, while every file points at the older one. If it is dead, every file points at a dead session.
- Why this blocks: the deputy is the takeover fencing for a dead coordinator (re-plan section 7, G-24, G-42). If the coordinator dies mid-run, the takeover lookup runs off the state file and the re-plan, both of which name 8397cff5. A takeover that messages a superseded or dead session is a failed takeover, and orphaned workers with no coordinator is the exact failure mode section 7 exists to prevent. The run can proceed fine while the coordinator lives, but the prepare is not perfect and the G-24 gate box is false as written, which is the same class round 1 graded BLOCKING (RB-1, amendments 14 and 21).

What must change (exact fix, in this order; the order matters because of the G-24 timestamp rule):

1. Update the deputy identity to 6f9f3647-b92a-4b19-bdcd-6b6d88cafb9e, declaration 2026-11-25 11:43:12 +07, in: re-plan lines 14, 23, 75, 115, 283, 361; state file line 28 (deputy field) and lines 76, 78 (replace "parent messages deputy 8397cff5" with 6f9f3647); thu-tu-chay.txt line 38. ADD to the re-plan line 25 task-1 start checklist: "update the state file deputy field to 6f9f3647" is NOT needed if the field is fixed now; instead add a start-checklist line that the coordinator VERIFIES the deputy field reads 6f9f3647 before releasing task 1. Record that session 8397cff5 is superseded and holds no deputy authority (stand it down or record it as ended).
2. Those edits move the state file last_updated AFTER 11:43:12, so the 11:43:12 declaration would then predate the last state edit and stop satisfying G-24. Therefore, AFTER all pointer edits are committed, the deputy (6f9f3647) must re-confirm AGAIN with a new timestamp after the last edit, certifying the NEW committed re-plan (new commit hash), and that re-confirmation must be committed with NO further state-file edits before task 1. (Task-1 start edits are post-gate and do not retroactively break G-24.)
3. Re-run G-32 after the edits (thu-tu-chay.txt and the state file change, so their hashes change) and record zero mismatches.
4. Do NOT fix this by editing the declaration alone again. The declaration is already correct. The pointers are wrong.

## MUST-FIX items

### R2-M1. MUST-FIX. The new deputy did NOT re-run the G-38 dry run (it says so itself)

- Declaration lines 52-53: "The dry run was done by the previous deputy session 8397cff5 on 2026-11-25 09:32-09:34 +07... I have not re-run a dry run in this session; this declaration is a re-confirmation of the plan and state, not a new dry run."
- The dry-run record (rung3-run-log/r3-l3-deputy-dry-run-20261125.md) is thorough for the previous deputy: SSH via ssh-laptop.sh, FCC tmux has-session, fcc-server curl, codex exec present, Zen BiDi 9222 and Marionette 2828 listening, CDP 9223 and 9224 live, daemon status, read.py ok=true for mei and mochi. But G-38 requires the deputy (the role holder) to confirm the contact path, and the role holder changed. The new deputy's own SSH contact path to the laptop is unproven for THIS session.
- Why not BLOCKING: the environment facts the dry run proved (laptop reachable, services alive) are properties of the VM and laptop, not of the session, and the new deputy demonstrably ran git log and wc -l on the VM; the parent-to-new-deputy wake path is proven by the declaration itself (the parent reached 6f9f3647 to obtain it). The residual risk is narrow: the new session's SSH key and proxy path. A 5-minute check closes it.
- What must change: the new deputy (6f9f3647) runs the contact-path check in its own session (SSH via ~/workspace/ssh-laptop.sh, tmux has-session r3-fcc-runner-L3, state file read plus JSON parse, git log tip) and appends a dated PASS line to the dry-run record (or a declaration addendum). Update the re-plan G-38 box to name session 6f9f3647 and the new date instead of only 09:32-09:34. If it cannot reach the laptop, reassign the deputy per G-38 before task 1.

### R2-M2. MUST-FIX. Scorer addendum line 5 still calls the execution plan "authoritative", contradicting its own stamp

- rung3-run-log/scorer-briefs/rung3-scorer-brief-R3-L3-addendum.md line 5: "Branch: todolist-push, tip 81919c0c (prepare baseline). Execution plan: ~/workspace/r3-l3-execution-plan-20261124.md (577 lines, authoritative)."
- Round-1 redteam N-03 explicitly required three sub-fixes on this line: tip to 81919c0c, 577 lines, remove "authoritative". The 4289e277 diff shows the first two landed (fa72d87 to 81919c0c, 565 to 577) and the third did NOT land. The word is still there.
- The execution plan's own line 3 stamp reads "SUPERSEDED ON IDS... The canonical sources are the state file, thu-tu-chay.txt, and the FINAL re-plan... Do not use the IDs, counts, or tip in this file". Its title line even says "(Authoritative)" while the stamp supersedes its IDs. Calling it "authoritative" in the addendum contradicts the stamp and tells a scorer to trust a doc the plan itself says not to trust for IDs.
- Why not BLOCKING: the addendum's operative values are all correct now (line 11: DP-06, DP-07; lines 46-48: drop, 0 invalids, DP-03 at position 34), and G-47 script-checks backup assignment against du-phong.txt, so a scorer cannot actually assign DP-03. The risk is confusion, not a wrong assignment.
- What must change: delete the one word "authoritative" from addendum line 5 (one-word edit), then re-run G-32.

## SHOULD-FIX items

### R2-S1. SHOULD-FIX. TB-B2 sign-off timestamp added, verifier session id still unrecorded

- improvements/r3-l3-tbb2-signoff-20261125.md now reads "Verified: 2026-11-25 Asia/Ho_Chi_Minh. Committed 2026-11-25 09:20:08 +07 in b061f87c" (timestamp half of N-06 fixed). The verifier line now reads "Verifier session id: not recorded in the prepare phase (the verifier was an independent subagent...)". The file is identified by its commit b061f87c instead.
- This is honest and auditable rather than silently missing, so it does not block. Fix if the session id is recoverable from the prepare-phase records; otherwise accept commit-identification and close N-06 as a recorded limitation.

### R2-S2. SHOULD-FIX. The new declaration itself carries two stale pointers

- Declaration "What I read" section: "origin/todolist-push = 4289e277". That was true when the deputy wrote it at 11:43:12, but committing the declaration itself (590be03c, 11:43:44) moved the tip to 590be03c. The re-plan content is unchanged between 4289e277 and 590be03c (only the declaration file changed), so the certification of the re-plan content holds; only the origin pointer is stale. Fix by phrasing it as "origin/todolist-push = 4289e277 at time of reading" in the next declaration revision. Do not write a new declaration for this alone.
- Declaration "Current state" runners paragraph: "lane brief acknowledged in writing 09:06". That ack predates the round-1 brief re-issue. The current acks are FCC 11:36 +07 with follow-up 11:39, Codex 11:37:33 +07 (acks-round1 report). The declaration was written at 11:43:12, after both fresh acks, and still cites 09:06. Fix by updating the timestamp to 11:36/11:39 in the next declaration revision.

### R2-S3. SHOULD-FIX. Tip 81919c0c is stamped bare in three files, qualified in only one

- thu-tu-chay.txt line 2, du-phong.txt line 2, and state file freeze line 36 all stamp "tip 81919c0c" with no qualifier. The addendum line 5 stamps it as "tip 81919c0c (prepare baseline)". The live tip is 590be03c. Round-1 Council 2 and Council 3 accepted this as the prepare-baseline convention, and all four files agree with each other, which is what G-32 checks, so this is not a defect. Add the "(prepare baseline)" qualifier to the three bare stamps for consistency so a future G-32 pass does not re-flag them.

## Verified fixed (round-1 items closed, with evidence)

- N-01 Zen ws2: move step, command, guard, and do-not-release condition all in place; command verified real against the Hyprland wiki; live machine state is the correct pre-start state (Zen ws1, no ws2, 4 agents ws3).
- N-02 grim/finish: in both briefs, acked in writing by both runners.
- N-04 bar pattern: G-46 line 137 records the N-2 pattern through 52 needs 50.
- N-05 worktree path: both briefs line 5.
- C2 B-1 checkpoint: time-budget.md, thu-tu-chay.txt line 90, and re-plan line 269 all carry the identical corrected trigger.
- C3 superseded note: re-added with SUPERSEDED marker, 27 notes.
- C3 ONLY sentence: thu-tu-chay.txt line 84.
- C1 A-09 Codex carve-out: Codex brief line 97, acked (Codex ack item 4).
- G-32: hashes recomputed by me match; order tokens verified; brief hashes match the laptop acks exactly.
- Fresh lane-brief acks: FCC 11:36 +07 with 11:39 follow-up, Codex 11:37:33 +07, both naming every re-issue change and confirming no start until assigned (acks-round1 report).
- R3-047 drop: order line 55 tokens with DP-03 at position 34, no live R3-047 task in any operative file (see sweep below).

## Checked, not findings

- R3-047 / Gutenberg sweep across all 10 operative files: every R3-047 mention is a DROP record (owner order 25/11 10:34, 0 invalids, DP-03 at position 34, no Gutenberg re-check, no Gutenberg monitoring). No file treats R3-047 as a live task. The only Gutenberg hits in the state file are historical: line 66 is a 24/11 liveness triage note whose "conditional on bbc/gutenberg browser verification before task 1" condition is mooted by the later owner DROP order, and the superseded note explicitly says "Do NOT re-check Gutenberg". No live Gutenberg dependency exists. The Gutenberg fixture watch cron is absent from cron.list entirely.
- Bar and invalid math consistent everywhere: 55 tasks, bar 53/55, invalid cap max 5 total and max 2 per group, invalid_count 0, invalid_by_group all 0, backups_used ["DP-03"], 4-task scenario 53 valid with bar 51/53, pattern N-2.
- Backup order consistent: du-phong.txt medium order DP-06 then DP-07 (DP-03 USED), addendum line 11 DP-06, DP-07, re-plan G-46, state file notes. Hard DP-02 only, very hard DP-05 only, DP-01 retired, in all four places.
- Cron set verified live: 6 r3l3 watches enabled (agents, coordinator-liveness, zen-laptop-health, runner-process, ledger-push, timeout), mei-mochi-15m-watchdog DISABLED, agents-watch last success 11:46:34 +07.
- Root re-plan copy still stamped SUPERSEDED in its first lines, naming the worktree copy as operative. Execution plan line 3 stamp SUPERSEDED ON IDS, canonical sources named.
- R3-029: runner FCC position 25 in re-plan section 6, declaration, and thu-tu-chay.txt (token 25 is R3-029). Password appears by pointer only in every file I read; no credential value seen.
- No em or en dashes in the 10 operative files. No personal info in any file I read.
- Worktree state: HEAD 590be03c, origin matches via ls-remote. One untracked file is present (improvements/r3-l3-final-rereview2-council-2-speed-20261125.md, another round-2 reviewer's in-progress file). I did not read it, to stay independent.

## What I did not verify

- The 4 per-agent internal 10-minute watchdogs: no direct channel from this VM, same limitation as round 1. The G-50 bounded gate (verify within 30 minutes of the start order) is the check for that, and it runs at start.
- Whether old deputy session 8397cff5 is still alive: the parent verifies deputy liveness hourly per G-42. I could not check subagent liveness from this session. This matters for R2-B1: if it is alive, two deputy sessions exist; if dead, the files point at a dead session. Either way the pointers must be fixed.
- The live FCC tmux pane and Codex exec path beyond the acks report (pane 22399, acks 11:36 and 11:37:33 as reported with exact ack text quoted in the acks-round1 report). The worktree brief hashes match the laptop hashes in that report exactly, which I verified.
- The pill-path-check screenshots pixel by pixel. The report file, the F-04 text, and the brief commands were verified as files; the per-lane PASS results (FCC 10:54-10:57, Codex 11:12-11:14 attempt 3) are as reported.

## Reasoning

The round-1 fixes are mostly real. I independently re-ran the hashes, the order-token count, the brief-hash match against the laptop acks, the cron states, and the laptop Zen workspace check, and they hold. The checkpoint trigger, the ONLY sentence, the superseded note, the bar pattern, the carve-out, the grim and finish lines, the worktree paths, and the fresh acks are all verified in the files, not from the coordinator's summary. The Zen move command is real per the Hyprland wiki, and the live machine is in the correct pre-start state.

The verdict is NOT READY because the one BLOCKING item from round 1 was fixed in exactly one file and in no other. A deputy re-confirmation that lives only in its own declaration, while the re-plan, the state file, and the run-order file all name a different session whose declaration the new one disqualifies, is not a closed loop. The G-24 gate box is checked with a justification the new declaration itself says does not satisfy G-24. The takeover is the run's protection against a dead coordinator, and its identity must be right in the files the coordinator reads, not only in the deputy's own file. The fix is small (pointer updates in 9 places, then one more deputy re-confirmation after the last edit, then a G-32 re-run), plus a 5-minute dry-run re-check by the new deputy and a one-word deletion in the addendum. Do that, commit it, and re-verify those points only. Then the run can start.
