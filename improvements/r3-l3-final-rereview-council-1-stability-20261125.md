# Final R3-L3 Prepare RE-REVIEW, Council 1 (Stability / Risk)

- Role: Council 1, stability and risk lens, FRESH reviewer (not the author of the original Council 1 verdict).
- Date: Wed 2026-11-25, review written 11:21-11:35 +07.
- Scope: re-review of the fixes for the final prepare review (owner order 25/11 10:35, R3-047 dropped 10:34). I verified the committed files myself at HEAD d4df3aa1 on branch todolist-push in ~/workspace/r3l3-run-wt (working tree clean, remote tip matches via ls-remote). I did NOT trust the coordinator's prepare report. I did NOT edit any run doc. I did NOT commit. I did NOT start the run. I did NOT run any run task.
- Live checks done in this review: cron.list (all watches), cron.status for all 6 run watches, sha256 recomputation of thu-tu-chay.txt and du-phong.txt, token count of the order line, JSON parse of the state file, grep sweeps for R3-047, em/en dashes, and the R3-029 password value (pointer mentions only, no value found).

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

Two blocking items remain: RB-1, the deputy re-confirmation (A-02), and RB-2, a stale DP-03 backup listing in the scorer addendum (B-F1 fix incomplete). The deputy has NOT confirmed it read the FINAL committed re-plan, and its standing declaration still cites the superseded root copy as "the operative plan". The re-plan itself lists the deputy confirmation as remaining before task 1 (line 361). Task 1 must not release until both items are closed. Everything else in my scope is verified, including all of A-01, A-03, A-04, A-05, A-07, A-08, A-11, the B-F4 decision, the G-34 watch set, the F-04 pill workaround, the R3-089 fixture, and the R3-047 sweep. Two non-blocking SHOULD gaps remain (A-09, A-10). Once RB-1 and RB-2 land, my verdict flips to AGREE.

## Per-amendment verification (A-01 to A-11)

### A-01 (BLOCKING, R3-047 drop as Option A): VERIFIED

- Order line: rung3-run-log/thu-tu-chay.txt line 8, 55 tokens counted by script, token 34 is DP-03, token 49 is R3-089, token 25 is R3-029, R3-047 absent from the order. Bar stays 53/55 (line 6).
- du-phong.txt line 10: DP-03 marked USED before task 1 for R3-047, runs at position 34, Pair B. Lines 12 and 14: DP-06 and DP-07 renumbered medium order 1 and 2. Line 35: R3-047 DROP paragraph, 0 invalids, no Gutenberg re-check. Line 44: used-capacity entry.
- Exception list lines 43-44: DP-03 in the Class S enumeration in place of R3-047, with the owner-order note. Line 66: DP-03, DP-05, DP-06, DP-07 are Class S. Line 68: count stays 9 of 55 Class L, 46 Class S.
- Re-plan section 0A line 22 and G-46 line 137: drop recorded, 0 invalids, council 3/3 unanimous.
- Codex lane brief line 13: task list has DP-03 at position 34, R3-047 does not run. Line 50: pre-milestone reminder, no Gutenberg check.
- State file: backups_used is ["DP-03"] (line 2), drop note at line 68, final-review note at line 76. Hashes recomputed by me match the state file note exactly: thu-tu-chay.txt bf3e75507cb4eaa05f1c3e846fd75f74004a84492f396c04a0dec126fb2e9e85, du-phong.txt 0cf06dda18cb32a47c99f5d5a4be67d8a8d5541d58c072f0f8e8df5c982f5619.
- G-32 zero-mismatch claim holds on the fields I re-checked: tip 81919c0c in thu-tu line 2, du-phong line 2, and state file freeze; FCC pane PID 22399 and fcc-claude 2.1.332 in thu-tu line 16 and the state file; Mochi target A25AA6F0370A00A174BC5304A333417D in thu-tu line 25; deputy 8397cff5 in thu-tu line 38 and state file line 28.

### A-02 (BLOCKING, one canonical re-plan): NOT VERIFIED (partial, one bullet missing)

- Done: the worktree copy is canonical and committed (HEAD d4df3aa1, working tree clean, ls-remote tip d4df3aa1 on todolist-push). The root copy ~/workspace/r3-l3-replan-final-20261124.md is stamped SUPERSEDED in its first lines, names its own stale errors (R3-029 Codex, B-07 OR, old deputy 028399b1, re-enable the old watch), and names the worktree copy as operative.
- NOT done: the deputy re-confirmation. The deputy declaration rung3-run-log/r3-l3-deputy-declaration.md (last changed in commit 3a2f45aa, 09:34) still states it read "/home/hatch/workspace/r3-l3-replan-final-20261124.md (FINAL re-plan, commit 81919c0c, the operative plan)". That path is now the SUPERSEDED copy. No deputy confirmation of the FINAL committed worktree copy exists in any committed file, and no post-d4df3aa1 change to the declaration exists in git log. The re-plan itself admits this: section 0A line 23 and section 11 line 361 both say the deputy re-confirms before task 1 and the parent messages deputy 8397cff5 for it. The prepare report likewise lists it as a parent start item, not as done.
- Why this blocks: the deputy's written understanding still points at the copy that says R3-029 goes to Codex, the chain breaks on OR, and the old watchdog is re-enabled. The SUPERSEDED stamp mitigates a fresh read of that path, but the deputy has not confirmed the AND rule, the R3-029 FCC runner, or the agents-watch arrangement from the canonical copy, which is exactly what A-02 required. See Remaining blocking items.

### A-03 (BLOCKING, stale not-ready items in the canonical copy): VERIFIED

- Re-plan section 11 "What was NOT ready on 24/11": all six items struck and closed with evidence (Mei messaging G-23 PASS, Mochi lock reset passed G-31, Clone2 reset passed G-31, FCC ack 09:06 G-30, pill proven G-44, TB-B2 sign-off). Section 0A line 14 states section 0A governs sections 10 and 11 where they disagree.
- F-14(c) line 160: the mei-mochi 15-minute watchdog stays DISABLED, never re-enabled. The old contradiction is gone.
- Section 10 todolist: all Phase 0 gates [x] except the Section 11 confirmation step at line 306, which is [ ] PENDING and names this independent verification round as the closer. That is honest, not stale.

### A-04 (BLOCKING, section 5 watchdog row for the disabled Gutenberg watch): VERIFIED

- Re-plan line 205: the section 5 row is now "R3-089 fixture check (manual, no cron; the merged Gutenberg watch is REMOVED)", with the 2026-11-30 12:00 date guard, the 2026-12-01 08:59 expiry, and "Gutenberg is NOT monitored (R3-047 dropped, owner order 25/11 10:34; the Gutenberg fixture watch cron is removed)". No "on demand before position 34" language remains.

### A-05 (BLOCKING, pre-position-49 R3-089 check as a hard gate): VERIFIED

- Re-plan G-39 line 130 calls the pre-position-49 check "a hard gate before position 49". Section 9 milestone line 265: "Before position 49 (R3-089): the fixture refresh is verified (find -mtime -7 returns exactly 6). If the fixture is stale, refresh and verify before position 49 runs." The refresh doc confirmation procedure adds the stop rule: if the count is not 6, refresh, re-verify, and only then start R3-089; if the refresh cannot make the count 6, stop and report to the owner. No separate R3-089-only watch was created, which matches the original Council 1 judgement.

### A-06 (BLOCKING, per-agent internal watchdogs as hard gate G-50): VERIFIED as the bounded gate, with dissent recorded and accepted

- The adopted gate is bounded, not the hard gate my predecessor demanded. Re-plan G-50 line 138: the coordinator verifies all 4 within 30 minutes of the start order; if any is missing at 30 minutes, the run starts anyway with the shared r3l3-agents-watch covering, and the missing one is recorded and set up mid-run. The Council 1 dissent is recorded in the same line: "Council 1 wanted a hard gate (all 4 verified before task 1, no downgrade); the bounded gate is adopted because the designed monitoring already detects stalls at the level that matters."
- I accept the bounded gate on stability grounds, and I do not treat the downgrade as a blocker, for three reasons. First, the internal watchdogs are redundant, not load-bearing: the shared r3l3-agents-watch is live and I verified its last successful run at 11:20:13 +07 today with 0 consecutive failures, and the timeout watch (last success 11:18:07) plus the coordinator heartbeat and per-task reports catch a late verdict independently. The only coverage unique to an internal watchdog is a Muse's own subagent stalling while its top-level tab stays alive, and that failure mode costs delay, not silent corruption, because the verdict still has to land. Second, the G-50 check is real work at start, not a formality: the coordinator still verifies all 4 within 30 minutes and records the result. Third, the evidence base for the 4 watchdogs existing is now on file: ~/memory/2026-11-25.md line 428 records all 4 confirmed at 10:44 +07, with lines 540-543 giving per-agent timestamps (clone1 last run 10:29, clone2 cycle 10:31 OK, mei trial 10:37 with first scheduled run 10:47, mochi running from 10:44). The residual risk is a subagent-level stall going unnoticed until a verdict is late; I accept it.

### A-07 (BLOCKING, first successful agents-watch run before task 1): VERIFIED, live, by me

- cron.status at about 11:21 +07: r3l3-agents-watch enabled, last run 11:20:13, last success 11:20:13, status succeeded. The original gap (last_success_at null at 10:41) is closed.
- Full G-34 set, all enabled with successful last runs: agents-watch 11:20:13, coordinator-liveness 11:18:18, zen-laptop-health 11:14:28, runner-process 11:14:04, ledger-push 10:48:17, timeout 11:18:07. mei-mochi-15m-watchdog is DISABLED in cron.list. The Gutenberg watch is absent from cron.list entirely, not merely disabled. This is fresher and stronger than the prepare report's claimed times.

### A-08 (BLOCKING, deputy field at task 1): VERIFIED

- State file line 28: deputy is 8397cff5-3099-4735-93fb-34415db38a3c, with the fresh declaration 09:34 and dry run PASS 09:32-09:34 cited. The file parses as JSON (loaded by script in this review). invalid_by_group trung_binh is 0 (line 42), consistent with the drop counting as 0 invalids.
- thu-tu-chay.txt line 38: deputy 8397cff5, fresh declaration 09:34. The stale 028399b1 appears nowhere in thu-tu-chay.txt or the state file deputy field.
- coordinator_active and epoch creation at task 1 is on the start checklist: re-plan section 0A line 25, section 7 line 234 ("At task 1, the run coordinator creates these fields first (coordinator_active set to its own id, epoch 1) before releasing task 1"), and state file final note line 76. The state file correctly has no coordinator_active or epoch field yet, since the run coordinator has not been spawned.
- Note: no separate one-line deputy confirmation after the 10:55 state-file update is on file. I do not treat this as a gap, because the 09:34 declaration already asserts the same deputy id 8397cff5 that was written into the field, so the substance is covered. The missing confirmation that matters is the A-02 re-read of the final committed re-plan, not this one.

### A-09 (SHOULD, FCC backend carve-out in both lane briefs): NOT VERIFIED (partial, non-blocking)

- FCC lane brief line 79 carries the carve-out with the owner decision 25/11 09:23, and the FCC ack names it (acks report, FCC 11:05). The re-plan section 0A line 19 and the FCC roster row also carry it.
- Codex lane brief line 97 carries only "NO OpenRouter. Never try it, never propose it." It does NOT carry the required sentence "FCC MAY use its built-in OpenRouter-free backend; the OpenRouter ban covers Opencode only (owner decision 25/11 09:23)". The Codex ack names only DP-03 and the pill mechanism, not the carve-out. The prepare report does not claim the Codex brief carries it.
- Non-blocking because it is a SHOULD, and the risk is low: Codex has no visibility into FCC's backend and cannot re-flag what it cannot see, while the re-plan, the FCC brief, and the FCC ack all record the carve-out. See Remaining non-blocking items for the fix.

### A-10 (SHOULD, workspace arrangement in the run coordinator's brief): NOT VERIFIED (partial, non-blocking)

- The arrangement IS in the re-plan section 0A line 18 (ws3 holds ONLY the 4 agents; all other work on ws2; never move, close, navigate, or disturb the 4 agents' windows in ws3), and in the agents-watch body per the original Council 1 verification.
- It is NOT in a run coordinator's brief, because no coordinator brief file exists yet in the worktree (no file matching *coordinator-brief* found; the coordinator is spawned at start). This is a SHOULD, and the fix is a one-sentence addition to the spawn brief. See Remaining non-blocking items.

### A-11 (SHOULD, commit the final-review amendments before task 1): VERIFIED

- Commit d4df3aa1 on branch todolist-push contains all 24 changed files, including the re-plan, thu-tu-chay.txt, du-phong.txt, exception list, state file, both lane briefs, the scorer addendum, the refresh doc, and the CI fixes. ls-remote shows origin todolist-push at d4df3aa1. git status in the worktree is clean (no uncommitted changes).

## Redteam stability/risk items in my scope

### B-F4 (backup exhaustion decision): SOUND, bar reachable, no owner decision needed before task 1

- (a) The drop counts as 0 medium invalids: recorded in re-plan G-46 line 137, du-phong.txt line 38, state file line 76, and scorer addendum line 47. The state file invalid_by_group trung_binh stays 0 (line 42). This is sound: a pre-run owner-ordered exclusion is not a mid-run failure, and counting it as an invalid would burn 1 of the 2 medium-group slots for an event that is not a failure. Council 3/3 unanimous is recorded in each place.
- (b) The 4-task shared-cause scenario (R3-011/028/036/046): 1 invalid for the caps if the shared cause is proven, DP-06 and DP-07 replace 2, 2 drop out of the sample, valid count becomes 53, bar recomputes to 51/53, coordinator NOTIFIES the owner (G-40) but does NOT stop. Recorded in re-plan G-46 line 137, du-phong.txt line 38, state file line 76, scorer addendum lines 47-48. The arithmetic checks: 55 minus 2 dropped is 53 valid, and the pre-declared table says 53 valid needs 51 (execution plan line 131; re-plan section 9 Phase 3 line 273). 51/53 is 96.2 percent, the same difficulty as 53/55 at 96.4 percent, so the bar is reachable. The notify-not-stop rule is consistent with section 9, where run-stop conditions are owner decisions and a backup shortfall is not listed as one. The F-17 stop rule (a 3rd medium invalid stops the run) is also consistent, because the shared-cause group counts as 1 event, leaving 1 more medium invalid allowed before a stop.
- On the redteam's demand for an owner decision: the team decided under the user's full-autonomy mandate (23/11) with council unanimity, and the decision is recorded in writing in four places so the owner can overrule it. The bar recomputation follows the pre-declared table, and the re-plan line 273 states an owner decision is required only if the shrink was not pre-declared. This shrink is pre-declared. I judge no pre-start owner decision is needed. I recommend the parent still surface this decision to the owner at start, since the redteam explicitly asked for the user's decision; the prepare report already flags that the parent can escalate.

### G-34 (watch verification): VERIFIED

- See A-07. 6/6 enabled with successful last runs, verified live by me at about 11:21 +07. Gutenberg watch absent, mei-mochi watch DISABLED.

### Stuck-pill defect, F-04: WORKAROUND SUFFICIENT for the run, not a blocker

- The defect is recorded in re-plan F-04 line 150: when the pill owner is the live session, overlay.py release returns visible false but does NOT hide the pill (the empty-holders branch only sends hide when owner is daemon). Fail-safe direction: stuck ON, never OFF, so status lies about the visual state but the pill never disappears when it should show.
- The workaround is recorded in the same line: verify the pill is actually gone with a grim after release, end each lane's computer-use session with finish at the end of each task, never overlap the two lanes' drives (single-session latch), and hide via an indicator hide request if stuck. Both per-lane pill checks PASS with screenshots (FCC 10:54-10:57, Codex 11:12-11:14 on attempt 3, report improvements/r3-l3-pill-path-check-20261125.md). The latch failure mode already occurred once in testing (Codex attempt 1 failed on FCC's leftover session) and was caught and cleared with computer-use stop, which proves the detection works rather than proving the run will fail. No mechanism code was changed; the defect is recorded for a separate post-run fix. I accept this: the workaround is manual discipline, but it is written into the re-plan, both lane briefs name the exact acquire and release commands, and the failure mode is fail-safe. It is not a blocker.

### R3-089 fixture: VERIFIED

- Expiry 2026-12-01 08:59 in thu-tu-chay.txt line 76, du-phong.txt line 41, and refresh doc line 13. Date guard 2026-11-30 12:00 in refresh doc lines 25-26 and re-plan line 205. Manual pre-position-49 hard-gate check in re-plan line 130 (G-39), line 205 (section 5 row), and line 265 (section 9 milestone). Refresh doc lines 71 and 13-14 record the 25/11 08:59 refresh, count 6, expiry 2026-12-01 08:59. The run ends 26-27/11 on plan, inside the window.

### R3-047 drop sweep, no live task remains: VERIFIED

- Every R3-047 mention in the run docs is a DROP record, not a live task: re-plan lines 16, 22, 58, 137, 205, 263, 295; thu-tu line 83; du-phong lines 10, 17, 35, 44; exception list line 44 (parenthetical only); state file lines 53, 68, 76; scorer addendum lines 46-48; Codex brief lines 3, 13, 50. No live R3-047 task remains in any run doc. liveness-config.json contains no R3-047 or gutenberg.org entry. The R3-029 password value appears in no file I read (pointer mentions only).

## Remaining blocking items (2)

### RB-1. A-02: deputy re-confirmation of the FINAL committed re-plan is missing

- File: rung3-run-log/r3-l3-deputy-declaration.md (last changed commit 3a2f45aa, 09:34 25/11). Its "What I read" section still cites "/home/hatch/workspace/r3-l3-replan-final-20261124.md (FINAL re-plan, commit 81919c0c, the operative plan)", which is the root copy now stamped SUPERSEDED.
- What must change: the parent messages deputy 8397cff5 before task 1; the deputy reads the FINAL committed worktree copy (improvements/r3-l3-replan-final-20261124.md, commit d4df3aa1) and writes a one-line confirmation on file covering the three corrected facts (R3-029 runner is FCC at position 25, chain-broken is AND not OR, r3l3-agents-watch replaces the old mei-mochi watch which stays DISABLED). The re-plan requires this at section 0A line 23 and section 11 line 361.
- Closes in minutes. Task 1 must not release until that line is on file. Once it lands, my verdict flips to AGREE.

### RB-2. B-F1 fix incomplete: scorer addendum line 11 still lists DP-03 as an available medium backup

- File: rung3-run-log/scorer-briefs/rung3-scorer-brief-R3-L3-addendum.md line 11: "Medium backups in order: DP-03, DP-06, DP-07." DP-03 is consumed: it runs at position 34 (same file lines 46 and 48, du-phong.txt line 10, re-plan line 263). Line 11 contradicts lines 46 and 48 of the same file and the canonical backup record in du-phong.txt, where DP-03 is marked USED and the remaining medium order is DP-06 then DP-07.
- Why this blocks: B-F1 required the scorer addendum to be amended for the swap, and the prepare report claims G-32 re-ran with zero mismatches. This is a live contradiction in the backup order in a doc the scorers read. If a medium task goes invalid mid-run, a reader of line 11 expects DP-03 to be available when it already ran at position 34. The coordinator assigns backups from du-phong.txt (correct), so the practical risk is confusion and delay rather than a double assignment, but a self-contradictory backup order is exactly what G-32 was supposed to catch.
- What must change: one line. Rewrite line 11 to "Medium backups in order: DP-06, DP-07. DP-03 is used (runs at position 34 in place of the dropped R3-047)." While editing that file, also correct its stale stamps on line 5 (tip fa72d87, execution plan 565 lines; the plan is 577 lines and the tip has advanced past d4df3aa1) or delete the tip stamp. Re-run G-32 after the edit and record zero mismatches.
- Note: thu-tu-chay.txt line 84 lists the shared-cause group only as pre-run invalid candidates, without the shared-cause counting rule. That wording is Council 3's amendment, not mine, but the counting rule itself is recorded in the canonical docs (re-plan G-46 line 137, du-phong.txt line 38, scorer addendum line 47), so I do not raise it as my own item.

## Remaining non-blocking items (2)

### NB-1. A-09: Codex lane brief lacks the FCC backend carve-out sentence

- File: improvements/r3-l3-lane-brief-codex-L3-20261125.md line 97. It has only the ban. Add the exact sentence "FCC MAY use its built-in OpenRouter-free backend; the OpenRouter ban covers Opencode only (owner decision 25/11 09:23)". Because the Codex brief was already acknowledged at 11:07:34, the cheaper correct alternative is to record the carve-out in the run log and the coordinator's start checklist so no runner re-flags the backend mid-run, and leave the brief text unchanged. Either path closes it; it does not block task 1.

### NB-2. A-10: ws3 arrangement not yet in a coordinator brief

- The sentence exists in re-plan section 0A line 18. No coordinator brief file exists yet. The parent must put this sentence in the run coordinator's spawn brief verbatim: "Hyprland workspace 3 holds ONLY the 4 agents (clone1, clone2, mei, mochi); all other work happens on workspace 2; never move, close, navigate, or disturb the 4 agents' windows in ws3." This is a start item, not a blocker.

## Reasoning

The fixes are real and I verified them in the committed files, not from the coordinator's summary: the order line counts 55 with DP-03 at token 34, the hashes recompute exactly, the watches all show successful last runs live, the deputy field is 8397cff5 and parses, the R3-089 dates are consistent across four files, and no live R3-047 task remains anywhere. The B-F4 decision is arithmetically sound and follows the pre-declared bar table. The bounded G-50 gate is acceptable because the shared watch is live and the 4 internal watchdogs were confirmed at 10:44 with timestamps. The stuck-pill workaround is sufficient because the defect fails safe and both per-lane checks passed.

I still say DISAGREE, because the unanimity bar the owner set at 11:19 requires ALL council members and the redteam to agree the fixes are adequate and prepare is perfect, and two BLOCKING items are admittedly unfinished. The deputy certified the stale copy as operative, and nobody has yet obtained its confirmation of the final committed copy. The scorer addendum still lists a consumed backup as available, contradicting its own later lines and the canonical backup record. Both are small items, closable in minutes, but they are exactly the class of stale-plan hazard (wrong R3-029 runner, wrong OR rule, wrong watchdog, wrong backup order) that the original Council 1 and redteam both flagged as blocking, and I will not sign past them. The two SHOULD gaps do not block task 1. Once RB-1 and RB-2 land, prepare is perfect in my scope and my verdict is AGREE.

## What this review did not do

- No edits to the re-plan, state file, or any run doc. No commits. No run start. No run task executed.
- I did not re-run the G-35 live checks (Zen, BiDi, FCC tmux, daemon) from this VM, and I did not message any agent. The per-agent internal watchdog confirmations I cite come from the memory log at ~/memory/2026-11-25.md lines 428 and 540-543, and the G-50 start verification still applies.
- I did not independently verify the pill-path-check screenshots pixel by pixel; I verified the report file exists in commit d4df3aa1, the F-04 text records both PASS results with times, and the lane briefs name the exact acquire and release commands.
