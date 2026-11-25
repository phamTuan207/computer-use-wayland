# Final R3-L3 Prepare Review, Council 1 (Stability / Risk)

- Role: Council 1, stability and risk lens.
- Date: Wed 2026-11-25, review written 10:41-10:55 +07.
- Reviewer: Council 1 subagent (final review, depth 2).
- Scope: final prepare review ordered by the owner 25/11 10:35, including the owner order 25/11 10:34 to DROP R3-047 from the run entirely.
- Files read in full and verified live (not from summary): the worktree re-plan, the root re-plan, the execution plan, the prepare report, the coordinator state file, thu-tu-chay.txt, du-phong.txt, the exception list, the deputy declaration. Live checks done in this review: diff of the two re-plan copies, cron.status for r3l3-agents-watch and r3l3-gutenberg-fixture-watch, cron.list, cron.view of the agents-watch body, curl of gutenberg.org (twice), SSH find of the R3-089 fixture on the laptop, deputy dry-run record, worktree git status.
- I did NOT edit the re-plan, the state file, or any run doc. I did NOT commit. I did NOT start the run. I did NOT run any run task.

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

## Verdict: AMEND

The run is fundamentally ready. All gates G-23 to G-49 were closed in Phase 0 and I re-verified the load-bearing facts live (see Evidence). There is no fatal flaw and no reason to reject or to re-run prepare. But APPLY is not safe yet, because the owner order to drop R3-047 has not been implemented anywhere, the two copies of the re-plan disagree on safety-critical lines, the canonical copy still carries stale not-ready items, and two watchdog verifications are not yet closed. All of the amendments below are small, pre-run, and cheap. None changes the run design. Task 1 must not release until amendments A-01 to A-08 are done and recorded.

## Vote on the R3-047 question: Option A (DP-03 replaces R3-047 at position 34)

I vote Option A. The run stays 55 tasks, the bar stays 53/55, position 34 stays in the Codex lane under Pair B.

Reasoning, from risk:

1. DP-03 is a like-for-like replacement. R3-047 is Class S (exception list, Class S list includes R3-047) and DP-03 is Class S (exception list, Backups section: DP-03, DP-05, DP-06, DP-07 are Class S). Both are medium, Tier B. Position 34 is in the Codex lane (positions 29-55), so DP-03 inherits Pair B, exactly as R3-047 would have. No class change, no lane change, no pair change, no count change.
2. The backup arithmetic holds after consuming DP-03. Medium backups left are DP-06 and DP-07 (du-phong.txt, medium order 2 and 3). The only remaining medium invalid candidates are the R3-011, R3-028, R3-036, R3-046 shared-cause group, which counts as 1 invalid if the shared cause is proven (R3-011 ruling, execution plan section 6 and du-phong.txt). If the shared cause is NOT proven, the group counts per task, but the run STOPS at the 3rd medium invalid (F-17, re-plan G-46: at most 2 medium invalids before the run stops), so at most 2 medium backups can ever be consumed before a stop. Two remaining backups are exactly enough. Option B's extra backup only matters in a scenario the stop rule already forbids.
3. The G-46 warning in the prepare report (if timeanddate consumes all 3 medium backups before position 34, a later R3-047 invalid has no backup left) becomes moot under Option A, because R3-047 is already replaced before the run.
4. DP-03 is ready to run as a task. Its key is frozen, N equals 5 measured 2026-11-23 (du-phong.txt), it was never run as a task in R3-L2 (in R3-L2 the R3-009 gate passed, so no medium backup was used; DP-01 was the backup used for the R3-047 invalid then, not DP-03), its snapshot dir exists (state file note: 60 empty R3-xxx-L3 and DP-xx-L3 dirs), and the pre-reset content check already covers it (rung3-ci/evidence-requirements.json, 61 keys including the 5 backups).
5. Option B has strictly more churn for near-zero benefit. It changes the task count (55 to 54), the bar (53/55 to 52/54), and shifts every position after 34 by one (R3-049 49 to 48, R3-089 49 to 48, R3-100 55 to 54, Codex lane 29-55 to 29-54). Every position-anchored milestone (before position 34, 43, 49, 55) must shift, plus the ledger row count, the evidence-requirements keys (61 to 60), and the checkpoint math. Each stale "55" or "position 49" left behind is a live mid-run trap. The bar table makes Option B legitimate (execution plan line 131: "54 valid needs 52"), but legitimacy is not the question. Churn risk is, and Option B has more of it.
6. Option A is the closest execution of the existing plan. The plan already said, for position 34, if Gutenberg is still down, declare R3-047 INVALID plus DP-03 (worktree re-plan section 9, line 258). The owner order only makes that decision early and unconditional. The one difference: because the drop is an owner order before the run, R3-047 must be recorded as EXCLUDED by owner order, consuming 0 invalids against the cap (max 5 total, max 2 per group), not as a mid-run INVALID. See amendment A-01.

## Evidence verified live in this review

- Gutenberg is still down. curl https://www.gutenberg.org/ returned HTTP 503 twice at about 10:41 25/11. The drop order is well founded; waiting for recovery is not a live option.
- R3-047 is position 34, R3-089 is position 49, R3-029 is position 25. Counted from the thu-tu-chay.txt order line (55 IDs). The order line still lists R3-047 at position 34; it has not been updated for the drop.
- R3-089 fixture is healthy, verified live on the laptop via SSH. find -mtime -7 returns exactly 6 (log-01 to log-06, mtime 2026-11-24 08:59:42; log-07 to log-12 dated 2026-11-15 08:59:42). The mtimes are consistent with a refresh on 25/11 08:59 using touch -d "1 day ago". In-window until 2026-12-01 08:59, so about 4.5 days of margin past a run ending about 26/11.
- r3l3-gutenberg-fixture-watch is DISABLED. cron.status 25/11 10:41: enabled false, last successful run 09:48:30, next run null. It will not run again.
- r3l3-agents-watch is ENABLED (5 min) and running. cron.status 25/11 10:41: enabled true, a run in flight, next run 10:42:58. But last_run_at and last_success_at are both null, so it has NO completed successful run on record yet. Its body (cron.view) matches the re-plan row: clone1 observation-only, dynamic target resolution via /json/list, 15-minute poke rule with delivery-first condition, serialized sends, ws3 do-not-touch, CDP and read.py first.
- mei-mochi-15m-watchdog is DISABLED (cron.list with include_disabled true). It stays disabled; the shared agents-watch replaces it.
- The two re-plan copies differ on 50 changed lines (diff). The dangerous differences, verified by line number:
  - Stale root copy line 200 names Codex as the R3-029 runner at position 25 (wrong). Worktree copy line 218 names FCC (correct; position 25 is in the FCC lane, positions 1-28).
  - Stale root copy line 225 defines the chain as broken on 15-minute unreachability OR a 30-minute missing report (the B-07 false-positive bug). Worktree copy line 243 uses AND (correct). Stale section 5 trigger (b) also lacks the AND heartbeat condition; worktree section 5 has it.
  - Stale root copy line 57 names deputy session 028399b1. Worktree copy line 71 names 8397cff5.
  - Stale root copy section 5 line 179 lists mei-mochi-15m-watchdog as the watch to re-enable for the run. Worktree copy line 195 lists r3l3-agents-watch and states mei-mochi stays DISABLED.
  - Stale root copy lines 324-326 list Mei messaging broken, Mochi locked until 02:38, Clone2 reset pending. All three are superseded (G-23 PASS, G-31 live checks).
- The deputy read the STALE copy. The deputy declaration states it read /home/hatch/workspace/r3-l3-replan-final-20261124.md and calls it "the operative plan". Its declaration still states the correct fresh facts (deputy 8397cff5, TB-B2 df4defcc, R3-029 FCC position 25, Class L 9), which it took from the state file, so the harm is bounded, but the deputy has not confirmed the AND rule or the agents-watch arrangement, which exist only in the worktree copy.
- The worktree copy itself still carries stale text. Its section 11 lines 342-346 still list Mei messaging STILL BROKEN, Mochi locked until 02:38, FCC not replied, pill unproven. The diff shows NO changes past stale line 243 (worktree line 243), so the header claim that section 10 and section 11 were updated did not land (the plan-update worker was cancelled before finishing, as briefed). Section 10's unchecked boxes (G-24, G-38, G-30 and others) are the 24/11 record, contradicting section 0A's "all gates done" unless read with the 0A override.
- The worktree re-plan has UNCOMMITTED changes. git status in ~/workspace/r3l3-run-wt shows M improvements/r3-l3-replan-final-20261124.md, HEAD 3a2f45aa.
- State file deputy field still records the old session. r3-l3-coordinator-state.json, deputy field: 028399b1-634c-4b37-84d1-6c8689c87ab8, declaration 2026-11-24 17:24:46 +07. Last updated 2026-11-25T09:15:00+07:00. thu-tu-chay.txt also still names deputy 028399b1.
- Deputy dry run is PASS and on file. rung3-run-log/r3-l3-deputy-dry-run-20261125.md, 09:32-09:34 25/11, deputy 8397cff5. Laptop reachable, FCC tmux alive, Zen BiDi 9222 and Marionette 2828 listening, Chromium 9223 and Brave 9224 CDP live, daemon alive, read.py ok for mei and mochi.
- FCC backend is recorded in the canonical copy in section 0A and in the section 1 FCC row ("Backend is its built-in free backend, allowed per owner decision 25/11; do not flag it as a violation"). The deputy dry-run record confirms the backend JSON (provider open_router, model open_router/openrouter/free) with the same allowance note. The stale root copy does NOT carry the carve-out.
- Execution plan line 131 confirms the bar table: "54 valid needs 52, 53 needs 51". The worktree re-plan section 9 carries the same table.

## Fact-by-fact assessment

1. R3-047 drop: Option A, see vote above. The drop must be recorded as an owner-ordered exclusion consuming 0 invalids, not as a mid-run INVALID.
2. Gutenberg watch removal and R3-089: removing the continuous watch is SAFE, and NO separate R3-089-only watch is needed. The fixture is verified live (exactly 6 files in window, in-window until 2026-12-01 08:59, run ends about 26/11). The mtimes are fixed values, not a live service, so there is nothing for a continuous watch to catch that the pre-position-49 check would miss; that check runs the same find command at the only moment it matters. The residual risk is only that the section 5 cron row still describes the disabled cron as live (amendment A-04) and that the pre-position-49 check is treated as optional (amendment A-05 makes it a hard gate).
3. Shared agents watchdog: coverage is sufficient IN DESIGN (all 4 agents, clone1 observation-only which is correct given its tokens, 5-minute cadence, delivery-first poke rule, serialized sends, CDP and read.py first) and verified live as enabled and running, but NOT yet proven in operation (no successful run on record). Amendment A-07 closes that gap before task 1. The old mei-mochi-15m-watchdog staying DISABLED is correct and verified live.
4. Per-agent internal watchdogs: NOT yet verified (being set up by a separate worker; clone1 and clone2 already had theirs, mei and mochi are being instructed). It is safe to start ONLY if verification before task 1 is a HARD gate, not a best effort. The shared watch sees only the top-level tab; only the internal watchdog sees a Muse's own subagents. Amendment A-06 makes it gate G-50: written confirmation from each of the 4 before task 1 releases, else the run waits and re-checks every 30 minutes. It must NOT be downgraded to verification during the run.
5. Two copies disagree: HIGH risk, live-proven (the deputy already read the stale one). The stale copy contains the R3-029 Codex error, the B-07 OR bug, the dead deputy id, the re-enable-the-old-watchdog instruction, and three superseded blockers. Any worker reading it could hand the R3-029 password to the wrong lane, trigger a false takeover on a normal long task, message the dead deputy, or re-enable a watchdog the owner ordered to stay disabled. Amendment A-02 reconciles to one canonical copy and re-syncs the deputy. Amendment A-03 fixes the canonical copy's own stale section 11.
6. Deputy field stale in the state file: LOW risk, acceptable with amendment A-08. The parent holds the fresh deputy id independently via the 09:34 declaration, so the wake chain (cron alerts parent, parent messages deputy) still reaches 8397cff5. But two canonical docs naming a dead deputy is the same stale-id failure mode G-32 already fixed 10 instances of. Update both the state file and thu-tu-chay.txt at task 1, before releasing task 1, atomically, with read-back verification. Note: the update is a state change after the deputy's 09:34 confirmation, but the changed field is the deputy's own id, which its declaration already asserts, so no fresh full re-confirmation is needed; a one-line confirmation after the update suffices.
7. FCC backend: recorded clearly enough IN THE CANONICAL COPY (section 0A, section 1 FCC row, dry-run record), and the owner decision 25/11 09:23 closes the prepare report's open finding. It is NOT recorded clearly enough in the stale root copy, which is the same A-02 problem. Amendment A-09 adds the one-line check that the lane briefs carry the sentence, so no runner or scorer re-flags the backend mid-run.
8. Workspace arrangement: recorded in worktree re-plan section 0A (owner 25/11 08:54) and in the agents-watch body (verified via cron.view), and corroborated by the prepare report laptop state. Amendment A-10 carries it into the run coordinator's brief explicitly, so the coordinator has it in its own brief and not only in the re-plan.

## Amendments (numbered, concrete)

### A-01 (BLOCKING): Implement the R3-047 drop as Option A

- Worktree re-plan, section 0A: replace the Gutenberg bullet (line 20) with the owner drop order (25/11 10:34) and the Option A decision: position 34 runs DP-03 (medium, Class S, Pair B, Codex lane) in place of R3-047; R3-047 is EXCLUDED by owner order and consumes 0 invalids.
- Worktree re-plan, section 9, line 258: replace the "Before position 34 (R3-047)" milestone with "Position 34 runs DP-03 in place of R3-047; no Gutenberg re-check."
- Worktree re-plan, section 2, G-46 (line 133): update the disposition. R3-047 is DROPPED, not pending. Medium invalid candidates are now only the R3-011, R3-028, R3-036, R3-046 shared-cause group (1 event if the shared cause is proven).
- rung3-run-log/thu-tu-chay.txt, order line: replace R3-047 with DP-03 at position 34. Task count stays 55, bar stays 53/55, all other positions unchanged.
- rung3-run-log/du-phong.txt: record DP-03 used as the replacement for R3-047 (owner order 25/11 10:34). Remaining medium backups are DP-06 and DP-07.
- rung3-run-log/r3-l3-exception-list.txt: remove R3-047 from the Class S list. DP-03 is already listed as Class S in the Backups section; counts stay Class L 9, Class S 46.
- State file: update the thu-tu-chay.txt and du-phong.txt hashes and add a note recording the replacement. Counts are unchanged.
- Codex lane brief: position 34 is DP-03 (N equals 5, Tier B, Class S, decoupled snapshot scoring). FCC lane brief is unaffected.
- After all edits, re-run G-32 (mechanical consistency, zero mismatches) and G-47 (backup assignment check) and record both in the run log.

### A-02 (BLOCKING): Reconcile the two re-plan copies into one canonical copy

- Declare the worktree copy (~/workspace/r3l3-run-wt/improvements/r3-l3-replan-final-20261124.md) canonical, in writing, in the run log.
- Overwrite the root copy (~/workspace/r3-l3-replan-final-20261124.md) with the canonical content, or replace it with a pointer file stating it is superseded and naming the canonical path. No stale copy may remain readable as the operative plan.
- The deputy (8397cff5) re-reads the canonical copy and writes a one-line confirmation that its understanding matches, covering the B-07 AND rule, the R3-029 FCC runner, and the r3l3-agents-watch arrangement.
- The run coordinator's brief names the canonical path explicitly. No brief may cite the root path.
- Commit the worktree re-plan (currently uncommitted, git status M) with an explicit pathspec on both add and commit, and verify via ls-remote, before task 1.

### A-03 (BLOCKING): Fix the stale not-ready items in the canonical copy

- Worktree re-plan, section 11, lines 342-346: strike and update each item with its closure evidence. Mei messaging: CLOSED, G-23 PASS, targets verified 09:20 25/11. Mochi locked: CLOSED, G-31 live check, reset 02:38 passed. Clone2 reset: CLOSED, G-31 live check. FCC not replied: CLOSED, written ack 09:06 (G-30 DONE). Pill unproven: CLOSED, G-44 live BiDi drive 09:01:48-09:01:52 with pill visible.
- Worktree re-plan, section 0A: add one sentence stating sections 10 and 11 below are the 24/11 record, and where they disagree with this section or the prepare report, this section governs.

### A-04 (BLOCKING): Fix the section 5 watchdog row for the disabled Gutenberg watch

- Worktree re-plan, section 5, the merged "R3-047-Gutenberg-watch + R3-089-fixture-watch" row (line 200): replace it with "r3l3-gutenberg-fixture-watch DISABLED (cron.status 25/11 10:41: enabled false, last success 09:48:30). No continuous Gutenberg watch (R3-047 dropped). No continuous R3-089 watch; the pre-position-49 check in section 9 is the guard." Remove the "on demand before position 34" language.

### A-05 (BLOCKING): Make the pre-position-49 R3-089 check a hard gate

- Worktree re-plan, section 9: elevate the "Before position 49 (R3-089)" milestone to a hard gate. The coordinator runs find -mtime -7 on ~/rung3/nd09-logs, expects exactly 6, and records the output in the run log before position 49 runs. Position 49 does not run until the check passes. If the count is not 6, refresh per the documented touch commands (touch -d "1 day ago" log-01..06, "10 days ago" log-07..12) and re-verify before position 49 runs.
- No separate R3-089-only watch is created. The fixture is verified live in this review (exactly 6 files in window until 2026-12-01 08:59, run ends about 26/11).

### A-06 (BLOCKING): Per-agent internal watchdogs are a hard gate before task 1 (new gate G-50)

- The run coordinator must hold written confirmation from EACH of clone1, clone2, mei, and mochi that its own internal 10-minute watchdog is running and checks (a) the repo for new assignments, (b) the owner's notification messages on the repo, (c) ALL of its own subagents, (d) its coordinator.
- Task 1 does NOT release until all 4 confirmations are in hand. If any is missing, the coordinator waits and re-checks every 30 minutes (same cadence as G-31). Do not downgrade this to verification during the run.
- Record the 4 confirmations in the run log with timestamps.

### A-07 (BLOCKING): Verify the first successful agents-watch run before task 1

- The run coordinator verifies r3l3-agents-watch has a completed successful run (cron.status last_success_at non-null) before task 1 and records it. Live at 10:41 the watch is enabled with a run in flight and next run 10:42:58, but last_success_at is null, so G-34 is not yet satisfied for this watch. This is expected to close within one 5-minute cycle.
- Re-run G-34 for the CURRENT watch set (r3l3-agents-watch, coordinator-liveness, zen-laptop-health, runner-process, ledger-push, timeout, plus mei-mochi-15m-watchdog confirmed DISABLED). The prepare report's G-34 "6/6 succeeded" covered the old set and does not cover the new agents-watch or the disabled Gutenberg watch.

### A-08 (BLOCKING): Update the deputy field at task 1, before releasing task 1

- State file (rung3-run-log/r3-l3-coordinator-state.json, deputy field): replace 028399b1-634c-4b37-84d1-6c8689c87ab8 with 8397cff5-3099-4735-93fb-34415db38a3c, via atomic write (temp file then rename, G-48), with read-back verification, recorded in the run log citing the 09:34 declaration.
- thu-tu-chay.txt, deputy line: replace 028399b1 with 8397cff5 at the same time, and update the state file hashes.
- The deputy appends a one-line confirmation after the update (the changed field is its own id, already asserted in its 09:34 declaration).

### A-09 (SHOULD): Carry the FCC backend carve-out into the lane briefs

- The run coordinator verifies the FCC lane brief and the Codex lane brief each carry the exact sentence "FCC MAY use its built-in OpenRouter-free backend; the OpenRouter ban covers Opencode only (owner decision 25/11 09:23)" before task 1, as part of the G-26 re-check.
- Record the owner decision as CLOSED in the run log, so the prepare report's open "Finding that needs an owner decision" (FCC backend) is not re-opened mid-run.

### A-10 (SHOULD): Carry the workspace arrangement into the run coordinator's brief

- The run coordinator's brief states explicitly, in its own text: Hyprland workspace 3 holds ONLY the 4 agents (clone1, clone2, mei, mochi); all other work happens on workspace 2; never move, close, navigate, or disturb the 4 agents' windows in ws3 (owner 25/11 08:54).

### A-11 (SHOULD): Commit the final-review amendments before task 1

- All amendments above that touch repo files (re-plan, thu-tu-chay.txt, du-phong.txt, exception list, state file, lane briefs) are committed with an explicit pathspec on both add and commit, immediately after staging, with git status --porcelain verified to show only intended files, and every push verified via ls-remote. Do not leave the canonical plan as an uncommitted working-tree edit at task 1.

## Risks accepted without amendment

- The deputy field update (A-08) happens at task 1 rather than now. Accepted because the parent holds the fresh deputy id independently via the 09:34 declaration, and the wake chain runs through the parent, not through the state file field.
- No continuous R3-089 watch (A-05). Accepted because the fixture is verified live with 4.5 days of margin and the pre-position-49 hard gate runs the same check at the only moment it matters.
- The stale root copy is overwritten rather than deleted (A-02). Accepted because a pointer file or an overwritten copy both remove the hazard, as long as no stale operative text remains at the root path.

## What this review did not do

- No edits to the re-plan, state file, or any run doc. No commits. No run start. No run task executed.
- The R3-089 fixture mtimes and the Gutenberg 503s were verified live from this VM (SSH to the laptop for the fixture, curl for Gutenberg). The per-agent internal watchdogs were NOT verified, because their setup is still in progress by a separate worker; that is amendment A-06, not a finding I could close here.
- The agents-watch first successful run was NOT observed, because its first run was still in flight at 10:41; that is amendment A-07.
