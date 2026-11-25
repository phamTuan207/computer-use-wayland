Verdict: DISAGREE

# Final Prepare RE-REVIEW, Council 2 (Speed / Benefit), R3-L3, 25/11/2026

- Council: Council 2, speed and benefit lens, fresh reviewer. This council did NOT write the original Council 2 verdict and did NOT write the prepare report. It verified the committed files itself and did NOT trust the coordinator's summary.
- Date: 2026-11-25, about 11:30 +07.
- Worktree: ~/workspace/r3l3-run-wt, detached HEAD d4df3aa1, git status clean, no uncommitted changes. Commit d4df3aa1 verified on the worktree HEAD.
- Files read in full and verified live: improvements/r3-l3-final-council-2-speed-20261125.md (original Council 2 verdict, amendments A1-A10), improvements/r3-l3-final-redteam-20261125.md (original redteam verdict), improvements/r3-l3-final-prepare-report-20261125.md (coordinator's claim of what was fixed), rung3-run-log/thu-tu-chay.txt, rung3-run-log/du-phong.txt, rung3-run-log/r3-l3-exception-list.txt, rung3-run-log/r3-l3-coordinator-state.json, rung3-run-log/r3-l3-time-budget.md, improvements/r3-l3-replan-final-20261124.md (worktree copy, operative), improvements/r3-l3-lane-brief-fcc-L3-20261125.md, improvements/r3-l3-lane-brief-codex-L3-20261125.md, improvements/r3-l3-pill-path-check-20261125.md, improvements/r3-l3-lane-brief-acks-20261125.md, rung3-run-log/scorer-briefs/rung3-scorer-brief-R3-L3-addendum.md, rung3-ci/evidence-requirements.json, ~/workspace/r3-l3-replan-final-20261124.md (root copy, first lines).
- Live checks done by this council: sha256sum of thu-tu-chay.txt (bf3e75507cb4eaa05f1c3e846fd75f74004a84492f396c04a0dec126fb2e9e85) and du-phong.txt (0cf06dda18cb32a47c99f5d5a4be67d8a8d5541d58c072f0f8e8df5c982f5619), both matching the state file; token count of the thu-tu-chay.txt order line (55 tokens, token 34 is DP-03, R3-047 absent); cron.list live (6 r3l3-* watches enabled, mei-mochi-15m-watchdog disabled, no gutenberg watch present); python count of em dash and en dash in all ten checked files (0 in each).
- This council did NOT edit any run doc. It did NOT commit. It did NOT start the run. It did NOT run any run task. It did NOT message any agent.

## Standing rules (restated)

- NO OpenRouter. Never try it, never propose it. FCC's built-in OpenRouter-free backend is allowed per the owner's 25/11 decision; the ban covers only Opencode.
- NO em dash (U+2014) or en dash (U+2013) in any file. Commas, periods, or short hyphens only.
- NO personal info on GitHub (no name, address, email, phone, schedules, photos, accounts, passwords, tokens). The R3-029 password must NOT appear in any file.
- Never assume an agent's capabilities. Check or ASK THE AGENT DIRECTLY in its own chat. Every brief must state the delivery path explicitly.
- Clone1 and clone2 have NO Tailscale/SSH. Repo and web work only. Do NOT give them machine tasks.
- CDP-first observation: CLI/API first, then DOM, screenshot/vision last.
- Never close or navigate any window/tab the owner opened. Never close the 4 agents' windows in ws3.
- The pill MUST be visible on ANY agent control. Pill text is always plain "Computer use active."
- Do NOT edit MEMORY.md. Observations go to ~/memory/2026-11-25.md.
- Do NOT start the run. Do NOT run any run task.

## Verdict detail

Nine of the ten original Council 2 amendments are verified as fixed in the committed files. One is only half fixed: A4, the checkpoint trigger alignment. The re-plan carries the full corrected trigger, but the two files the coordinator consults at checkpoint time (rung3-run-log/r3-l3-time-budget.md and rung3-run-log/thu-tu-chay.txt) still carry a simplified trigger that can fire a spurious pause on the biased early sample, which is exactly the trap A4 was written to close. The prepare report overstates this fix ("checkpoint trigger corrected to 19-31h"); the band was corrected, the per-class condition and the 3-hour fallback were not. The fix is two short edits plus a re-hash, about 10 minutes of coordinator work, and it must land before task 1. Until it does, prepare is not perfect, and this council cannot agree under the unanimity bar.

## Per-amendment verification

### A1. R3-047 drop as Option A, pre-decided and pre-checked: VERIFIED

- thu-tu-chay.txt line 8: order line is 55 tokens, token 34 is DP-03, R3-047 is absent from the order line. Line 6 still reads 55 tasks and pass bar 53/55. Line 83: R3-047 ruling rewritten to DROP by owner order 25/11 10:34, 0 invalids, DP-03 replaces at position 34, no Gutenberg re-check, no Gutenberg monitoring.
- du-phong.txt line 10: DP-03 marked USED before task 1 for R3-047, Tier B medium, N = 5, runs at position 34, Pair B. Lines 12 and 14: DP-06 and DP-07 renumbered to medium order 1 and 2. Line 35: R3-047 DROP paragraph, 0 invalids. Line 44: used-capacity entry records the drop as 0 invalids with DP-06 and DP-07 remaining.
- r3-l3-exception-list.txt lines 43-44: DP-03 listed in Class S in place of R3-047, with the replacement noted. Line 66: DP-03, DP-05, DP-06, DP-07 are Class S. Counts unchanged: 9 Class L, 46 Class S.
- r3-l3-coordinator-state.json lines 2-3: backups_used is ["DP-03"]. Line 42: invalid_by_group trung_binh is 0. Line 68: note records the drop as 0 invalids, DP-03 medium, Class S, Pair B, position 34.
- Worktree re-plan line 22 (section 0A) and line 263 (section 9 milestone "Before position 34 (DP-03)") and G-46 line 137: all say DROP, not re-check. The Gutenberg re-check step for position 34 is gone.
- Hashes: sha256sum of thu-tu-chay.txt is bf3e75507cb4eaa05f1c3e846fd75f74004a84492f396c04a0dec126fb2e9e85 and of du-phong.txt is 0cf06dda18cb32a47c99f5d5a4be67d8a8d5541d58c072f0f8e8df5c982f5619, both matching state file line 53. G-47 backup assignment is recorded PASS in the state file notes.
- Budget: 55 tasks, bar 53/55, class mix 9 Class L and 46 Class S, difficulty mix medium 37, hard 11, very hard 7, all unchanged. DP-03 is a terminal task (one ss -tlnp run plus a report, thu-tu-chay.txt line 74: N = 5, n_min 3) versus R3-047 a 3-book browser search, so the swap is budget-neutral to slightly faster. No per-task minute estimate exists for either task in any file, so no larger saving is claimed. The 19-31h budget holds unchanged.

### A2. Fix the two stale lines in the canonical run-order file, then re-hash and re-run G-32: VERIFIED

- thu-tu-chay.txt line 16: FCC pane PID 22399, fcc-claude 2.1.332, created 2026-11-25 09:00:18, matching the state file runners.fcc field. The stale 203375 and 2.1.331 values are gone.
- thu-tu-chay.txt line 38: deputy session 8397cff5-3099-4735-93fb-34415db38a3c, declaration 2026-11-25 09:34, dry run PASS 09:32-09:34. The stale 028399b1 value is gone.
- thu-tu-chay.txt line 25: Mochi target A25AA6F0370A00A174BC5304A333417D, matching the live target verified by G-23.
- thu-tu-chay.txt line 2: tip stamp 81919c0c, matching state file freeze.todolist_push_tip. Note: the live todolist-push tip has since advanced (fffda9da per the prepare report); 81919c0c is the prepare baseline, which is the established convention, not a defect.
- Hashes recomputed and recorded in the state file (line 53), verified by this council with sha256sum. The four fields above match between thu-tu-chay.txt and the state file, so the G-32 zero-mismatch claim is confirmed for the fields this council re-checked.

### A3. Update the state-file deputy field BEFORE task 1, with a fresh deputy re-confirmation: VERIFIED (file part)

- r3-l3-coordinator-state.json line 28: deputy field reads 8397cff5-3099-4735-93fb-34415db38a3c, fresh declaration 2026-11-25 09:34 +07, dry run PASS 09:32-09:34, G-24 and G-38 CLOSED, on STANDBY. The update was done before task 1, not deferred to task 1. JSON parses (verified with python json.tool).
- The deputy re-confirmation of the FINAL committed re-plan remains a parent start item (prepare report, parent start items), not a file defect. The run must not start until the parent messages deputy 8397cff5 and receives that re-confirmation. See the open start items below.

### A4. Align the checkpoint trigger in the two stale files to the corrected re-plan trigger: NOT VERIFIED

- The corrected trigger exists in the worktree re-plan line 269: pause ONLY if the revised run-complete exceeds 31h OR a per-class mean exceeds its estimate by more than 25 percent with at least 3 graded tasks of that class; a revised run-complete of 22-31h continues with a recorded estimate; a 3-hour wall-clock fallback checkpoint is added.
- rung3-run-log/r3-l3-time-budget.md lines 31-34: "If the revised run-complete estimate is OUTSIDE 19-31 hours (i.e. the run will take longer than 31 hours at the current pace) OR the mean cycle time exceeds the plan estimate by more than 25 percent, the coordinator PAUSES the run." The 19-21h band is fixed (now 19-31h), but the clause still uses the OVERALL mean cycle time of just 3 graded tasks, with NO per-class condition and NO at-least-3-graded-tasks-of-that-class floor. Lines 37-38 do say a 19-31h estimate continues, so the estimate half is fixed. The 3-hour wall-clock fallback appears NOWHERE in this file (grep for "3-hour" and "wall-clock": zero hits).
- rung3-run-log/thu-tu-chay.txt line 90: "Checkpoint sau task thu 3 duoc cham: neu uoc tinh hoan thanh vuot 31h hoac thoi gian chu ky trung binh vuot ke hoach hon 25%, dieu phoi vien TAM DUNG va bao chu so huu; chay tiep chi khi chu so huu quyet dinh. Xem rung3-run-log/r3-l3-time-budget.md." Same simplified trigger: overall mean, no per-class floor, no 22-31h continues clause, no 3-hour fallback. It also explicitly defers to time-budget.md, so the coordinator's working reference at checkpoint time is the simplified trigger, not re-plan line 269.
- Why this is blocking, not a wording nit: the first 3 graded tasks are the biased early sample the re-plan itself names (R3-001 Class L serial plus R3-002 pilot). The overall-mean clause in time-budget.md lines 31-34 can fire on that sample alone, while re-plan line 269 forbids firing until a per-class mean exceeds its estimate with at least 3 graded tasks of that class. The two docs the coordinator reads disagree with the operative plan at the exact moment the pause decision is made. A spurious pause here costs an owner-decision wait in the middle of the run. This is the same trap A4 called "the single most likely spurious pause in the run." The prepare report's claim that the trigger is "corrected to 19-31h" describes only the band half of the fix.
- What must change: see blocking item B-1 below.

### A5. Make the worktree re-plan the single canonical copy; stamp the stale root copy SUPERSEDED: VERIFIED

- ~/workspace/r3-l3-replan-final-20261124.md line 1: stamped SUPERSEDED 2026-11-25, names the worktree copy as the only operative plan, and lists the four stale facts (R3-029 runner Codex, B-07 OR, deputy 028399b1, mei-mochi re-enable) as corrected in the worktree copy.
- Worktree re-plan is committed: git show HEAD d4df3aa1 includes improvements/r3-l3-replan-final-20261124.md (157 changed lines), git status is clean, git diff HEAD is empty. The 25/11 owner decisions in section 0A are on the branch, not only in a dirty worktree.
- Worktree re-plan line 160, F-14(c): the mei-mochi 15-minute watchdog stays DISABLED for the run, never re-enabled, and the shared r3l3-agents-watch replaces it. The prepare report's start item 6 also says never re-enable it. The stale re-enable lines are gone.
- Worktree re-plan line 223: R3-029 runner is FCC, position 25. Line 248: chain-broken definition is AND. Both match the live state.

### A6. Update the watchdog table for the removed Gutenberg watch and record the new 6-watch set: VERIFIED

- Worktree re-plan line 205 (section 5): the merged Gutenberg watch row is replaced with a manual R3-089 fixture check before position 49, with the 2026-11-30 12:00 date guard. Gutenberg is NOT monitored.
- Worktree re-plan line 130 (G-39): fixture refreshed 25/11 08:59, in-window until 2026-12-01 08:59, pre-position-49 check is a hard gate, date guard 2026-11-30 12:00.
- Live cron.list checked by this council: 6 r3l3-* watches enabled (r3l3-agents-watch 5m, r3l3-coordinator-liveness-watch 5m, r3l3-ledger-push-watch 1h, r3l3-runner-process-watch 15m, r3l3-timeout-watch 5m, r3l3-zen-laptop-health 15m). mei-mochi-15m-watchdog is DISABLED. No r3l3-gutenberg-fixture-watch exists in the list at all. This matches the G-34 6/6 record in the prepare report.

### A7. Bound the per-agent internal watchdog gate; do not let it delay task 1 without limit: VERIFIED

- Worktree re-plan line 21 (section 0A), line 138 (G-50), and line 215 (section 5): all three state the bounded gate identically. The run coordinator verifies all 4 per-agent internal 10-minute watchdogs within 30 minutes of the start order; if any is missing at 30 minutes, the run starts anyway with the shared r3l3-agents-watch covering, and the missing one is recorded and set up mid-run. Council 1's dissent (wanted a hard gate) is recorded in G-50 line 138.
- Speed and risk tradeoff: this is the right tradeoff. The gate is verify-within-30-minutes, not wait-30-minutes, so if all 4 verify quickly the run starts at once with no forced delay. The worst case is a single pre-task-1 slip of at most 30 minutes, and only if a watchdog is missing. The shared r3l3-agents-watch is live (verified enabled at 5 minutes in cron.list) and covers silence detection, and the internal watchdogs are redundant with it (final redteam M-04), not load-bearing. An unbounded wait for two setup confirmations would have been worse than the bounded gate.
- State file line 76 records G-50 as a run coordinator start item. The prepare report start item 3 repeats it.

### A8. State the run-tab workspace explicitly: VERIFIED

- Worktree re-plan line 18: "The Zen run tab lives in ws2, never ws3. Never move, close, navigate, or disturb the 4 agents' windows in ws3." The gap between the ws3-only-agents rule and the run-tab rule is closed.

### A9. Commit the uncommitted operative-plan changes before task 1: VERIFIED

- HEAD is d4df3aa1, git status --porcelain is empty, git diff HEAD is empty. git show HEAD includes the worktree re-plan (157 changed lines) plus all 23 other files in the final prepare review. The operative plan is on branch todolist-push, not only in a dirty worktree.

### A10. Pre-position the DP-03 evidence and scoring path so position 34 is a normal task: VERIFIED

- Codex lane brief line 13: task list includes DP-03 at position 34, with the note that DP-03 replaces the dropped R3-047 by owner order 25/11 10:34 and R3-047 does not run. Line 50: pre-milestone reminder carries DP-03 at position 34 with no Gutenberg check.
- Exception list lines 43-44 and 66: DP-03 is Class S, scored from the sealed snapshot, decoupled, no live re-read.
- rung3-ci/evidence-requirements.json: 61 keys, DP-03 spec exists (files ss-output.txt and bao-cao.txt, screenshots_min 1), so the manifest gate works for DP-03 as written.
- thu-tu-chay.txt line 74: DP-03 fixture ruling records N = 5 (n_min 3), measured 2026-11-23 19:20, 9 ports found. Scorer addendum line 48: DP-03 at position 34, medium, Class S, Pair B, scored from its sealed snapshot, no Gutenberg check. Position 34 needs zero decision time when it arrives.

## Remaining blocking items

### B-1. A4 remainder: the checkpoint trigger is still simplified in time-budget.md and thu-tu-chay.txt (BLOCKING)

- Files and lines:
  - rung3-run-log/r3-l3-time-budget.md, lines 31-34 (pause clause) and lines 37-38 (continue clause). Missing: the per-class mean condition with at least 3 graded tasks of that class, and the 3-hour wall-clock fallback.
  - rung3-run-log/thu-tu-chay.txt, line 90 (tail checkpoint paragraph). Missing: the per-class mean condition with at least 3 graded tasks of that class, the 22-31h continues clause, and the 3-hour wall-clock fallback. It also defers to time-budget.md, which carries the same simplified trigger.
  - Correct reference: worktree re-plan line 269, which has the full corrected trigger.
- What must change (two short edits, then re-hash):
  1. In time-budget.md lines 31-38, replace the pause clause with the re-plan line 269 wording: pause ONLY if the revised run-complete exceeds 31h OR a per-class mean exceeds its estimate by more than 25 percent with at least 3 graded tasks of that class; a revised run-complete of 22-31h continues with a recorded estimate; add the 3-hour wall-clock fallback (if the 3rd graded task has not landed by 3 hours after task 1, the coordinator reports to the owner).
  2. In thu-tu-chay.txt line 90, replace the tail paragraph with the same corrected trigger in short form, keeping the pointer to time-budget.md.
  3. Recompute the thu-tu-chay.txt sha256 (the edit changes it), re-record it in the state file, and re-run the G-32 grep pass to zero mismatches, per the S-01 hash discipline. Time-budget.md has no recorded hash, so no hash update is needed for it.
- Cost of the fix: about 10 minutes of coordinator work, no run-design change, no bar change, no position change. Cost of leaving it: a spurious checkpoint pause on the biased early sample, which waits on an owner decision mid-run.

## Open start items (not blocking, must still happen before task 1)

- Deputy re-confirmation: the parent messages deputy 8397cff5 to re-confirm it read the FINAL committed re-plan (worktree copy, improvements/r3-l3-replan-final-20261124.md) before task 1. The deputy field update itself is done (A3); this is the re-confirmation step after it.
- Zen on ws2: the coordinator confirms Zen is on ws2 and visible before releasing task 1 (prepare report start item 4). This matters because the pill path check attempt 2 proved a ws2 drive instruction fails when Zen sits on ws1. The lane briefs say "Drives run on ws2" (FCC brief line 74, Codex brief line 92), which is correct only if Zen is actually on ws2. Re-plan F-04(e) already covers the drive-where-visible rule: each lane confirms Zen is visible on its drive workspace before driving and reports to the coordinator instead of switching workspaces blindly if it is not.

## Answers to the review questions

- DP-03 swap: budget-neutral to slightly faster than keeping R3-047. The run stays 55 tasks, bar 53/55, 19-31h budget holds. DP-03 is a terminal task (one ss -tlnp run plus a report) versus R3-047 a 3-book browser search. No per-task minute estimate exists for either task, so the honest claim stops at budget-neutral to slightly faster.
- G-50 bounded internal-watchdog gate: the right speed and risk tradeoff. Verify-within-30-minutes, not wait-30-minutes, so there is no forced delay. Worst case is one pre-task-1 slip of at most 30 minutes, only if a watchdog is missing, with the shared agents-watch covering. Live cron.list confirms r3l3-agents-watch is enabled at 5 minutes.
- Per-lane pill checks: both PASS in improvements/r3-l3-pill-path-check-20261125.md (FCC 10:54-10:57, Codex 11:12-11:14 on attempt 3). They add no delay to the run start because they are already done. The stuck-pill workaround (verify the pill is actually gone with a grim after release, finish each lane's computer-use session at the end of each task) is workable without slowing the lanes: one grim plus one finish per task costs seconds, and the single-session latch rule in re-plan F-04(d) prevents a repeat of the FCC leftover session blocking Codex attempt 1.
- 4-task shared-cause scenario: the bar recompute to 51/53 is recorded in du-phong.txt line 38, re-plan G-46 line 137, scorer addendum line 47, and state file line 76. It is fast to apply mid-run: it is a table lookup (valid 53, bar 51/53) plus an owner notification under G-40, with no run stop. It creates no scoring delay.
- Lane briefs: both are the amended versions. FCC brief section 9 (pill mechanism, line 74) and section 10 (OpenRouter carve-out, line 79). Codex brief line 13 (DP-03 at position 34) and section 11 (pill mechanism, line 92). Both runners re-acknowledged in writing (improvements/r3-l3-lane-brief-acks-20261125.md, FCC 11:05, Codex 11:07:34), each naming both amendments and confirming no start until assigned. The only remaining ambiguity is the ws2 drive condition noted above, which F-04(e) and start item 4 already cover.
- R3-089 fixture: the manual pre-position-49 check is in the re-plan (line 130 G-39, line 205 section 5, line 265 section 9 milestone) and does not block the run. It is a check before position 49, not a gate on task 1, with a 2026-11-30 12:00 date guard and a seconds-long touch refresh if stale. Fixture is in-window until 2026-12-01 08:59.

## Reasoning

The coordinator's summary was checked against the committed files, not trusted. Nine amendments hold up under that check, with file and line evidence above. The tenth, A4, does not: the prepare report claims the checkpoint trigger is corrected, but only the band half of the correction landed in the two files the coordinator will actually read at checkpoint time. The re-plan is correct, but the re-plan is not the file the coordinator consults at the checkpoint; thu-tu-chay.txt line 90 points at time-budget.md, and both carry the simplified trigger. A doc disagreement at the pause decision is not a cosmetic issue: it is the exact failure mode the original Council 2 flagged as the most likely spurious pause, and the fix costs about 10 minutes. Under the unanimity bar, one half-fixed amendment is enough to withhold agreement. Fix B-1, re-hash, re-run G-32, and this council's verdict flips to AGREE with no further review needed from the speed lens.

## What this council did NOT verify

- It did not message any agent, so per-agent internal watchdog existence (mei, mochi, clone1, clone2) is not independently confirmed by this council. The G-50 gate is the check for that, and it runs at start.
- It did not re-run the G-35 live checks (Zen, BiDi, FCC tmux, daemon) from this VM. The pill path check report and the prepare report's G-34 evidence were verified as files, and the cron states were verified live by this council via cron.list.
- The R3-029 password appears in no file this council read (grep over the run docs returns only pointer language and the test account address rung3-029-test@example.com, no credential value). Zero em dashes and zero en dashes in all ten files checked.
