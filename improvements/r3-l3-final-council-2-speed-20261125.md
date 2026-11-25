# Final Council 2 (Speed / Benefit) Verdict, R3-L3 Prepare Review, 25/11/2026

- Council: Council 2, speed and benefit lens.
- Date: 2026-11-25, about 10:40 +07.
- Scope: final pre-run review only. This council did NOT edit the re-plan, the state file, or any run doc. It did NOT commit. It did NOT start the run. It did NOT run any run task.
- Files read in full and verified live: worktree re-plan `~/workspace/r3l3-run-wt/improvements/r3-l3-replan-final-20261124.md` (with uncommitted 0A changes), root re-plan `~/workspace/r3-l3-replan-final-20261124.md`, execution plan `~/workspace/r3-l3-execution-plan-20261124.md` (565 lines), prepare report `~/workspace/r3l3-run-wt/improvements/r3-l3-prepare-report-20261125.md`, state file `~/workspace/r3l3-run-wt/rung3-run-log/r3-l3-coordinator-state.json`, `thu-tu-chay.txt`, `du-phong.txt`, `r3-l3-exception-list.txt`, deputy declaration `~/workspace/r3-l3-deputy-declaration.md`, time budget `~/workspace/r3l3-run-wt/rung3-run-log/r3-l3-time-budget.md`, task list `~/workspace/r3l3-run-wt/docs/rung3-list-100-tasks.md` (R3-047 and DP-03 entries), and `cron.list` (live, including disabled jobs).
- Live checks done by this council: `curl` to gutenberg.org returned 503 twice (still down, second day); `cron.list` confirms r3l3-agents-watch enabled at 5 min, mei-mochi-15m-watchdog disabled, r3l3-gutenberg-fixture-watch absent entirely; `sha256sum` confirms thu-tu-chay.txt eaffee95e281efa1b9611efe09f0b60ee1f1424dc5747b275530763e5234bdba and du-phong.txt a57b488f15850413b02918df31db6c985f19e67f7a50fd5899ef121a531a5779, matching the state file.

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

## Verdict: AMEND

The plan is sound and the 19-31h budget holds under the R3-047 drop. The run should NOT be delayed for a rewrite, and it should NOT start until the amendments below are applied, because three of them are stale-document traps that would cost real time mid-run: a spurious checkpoint pause (A4), a dead deputy and dead FCC pane in the canonical run-order file (A2, A3), and two copies of the re-plan that disagree on who runs R3-029 (A5). All ten amendments are small, pre-task-1, and owned by the parent or the run coordinator. None changes the run design.

## Vote on the R3-047 question: Option A (DP-03 replaces R3-047 at position 34)

### Why Option A wins on speed

- Same pacing, zero design change. R3-047 and DP-03 are both medium and both Class S. The exception list names R3-047 in the Class S list, and its backups paragraph names DP-03, DP-05, DP-06, DP-07 as Class S. The class mix stays 9 Class L and 46 Class S, the task count stays 55, the bar stays 53/55, and the Codex lane keeps position 34 in its lane (positions 29-55). Nothing downstream moves.
- DP-03 is, if anything, faster than R3-047. R3-047 (list file line 540) is a browser task: open gutenberg.org, search 3 books, record author, year, public-domain status and 3 formats per book, 3 detail-page screenshots, ket-qua.txt. DP-03 (list file line 730) is a terminal task: run `ss -tlnp` once, save output, write a 5-row report, one screenshot. No site navigation, no multi-page search. No file gives a per-task minute estimate for either task, so the honest claim is only that the swap is budget-neutral to slightly favorable, not that it saves a measured amount.
- Option B costs more than it saves. Dropping to 54 tasks saves one mean cycle on paper (about 21-34 min at the budget means in the time-budget file), but the doc churn eats it: thu-tu-chay.txt 55-ID line plus counts plus sha256 plus tip, state file class counts (Class S 46 to 45) plus hashes, exception list (remove R3-047 from the Class S list), du-phong.txt, re-plan section 9 bar table (54 valid needs 52), manifest-gate evidence-requirements.json (61 keys to 60), resume.py dry run, and a full G-32 mechanical-consistency re-run. That is about 30-60 min of pre-task-1 coordinator serial time plus re-verification risk, for a saving that is smaller than the churn. Option A needs only the normal invalid-handling path that already exists (G-47 script check, du-phong.txt entry, run-order substitution).
- Option A keeps the pre-declared bar. Option B recomputes the bar to 52/54 under a table that is pre-declared (execution plan Phase 3 step 4, re-plan section 9), so it is legal, but it spends a second bar change on a run whose bar has already been a source of confusion, and it leaves the run with 3 medium backups for 4 timeanddate candidates while Option A leaves 2. That difference is real but small: the 4 timeanddate tasks (R3-011, R3-028, R3-036, R3-046) share one event, so they count as 1 event invalid against the caps, but each still consumes a backup slot (key file lines 23-24: 3 medium backups for 4 tasks, the 4th drops out of the sample with no backup). Under Option A, if all 4 go invalid, 2 get backups and 2 drop, valid count 53, bar recomputes to 51 by the pre-declared table. Under Option B the same outcome is 53 valid with 3 replaced and 1 dropped. The end bar is the same either way; Option A just gets there with less churn.

### Budget recompute

- The honest budget is 19-31h, staffed for 31h, measured from task 1. The time-budget file gives the means: about 21 min per task at 19h, about 34 min per task at 31h.
- Option A: 55 tasks, same class mix, same means. 19-31h holds unchanged. The DP-03-for-R3-047 swap does not move either bound, because both tasks sit in the same class and difficulty cell and no per-task estimate exists for either.
- Option B: 54 tasks x 21-34 min = about 18.6-30.6h of run time, but the pre-run churn (30-60 min) is paid before task 1, so the wall-clock start slips by more than the run-time saving. Net slower in practice, plus a fresh mismatch risk across 7 files.
- Gutenberg is still down (this council curled gutenberg.org twice, 503 both times), so the drop itself is correct and is not a speed question. The owner order of 25/11 10:34 settles it.

### Checkpoint

- The R3-047 change does NOT affect the checkpoint. The checkpoint fires after the 3rd graded task, which lands in the first FCC-lane tasks, long before position 34. DP-03 is Codex lane, position 34. Both R3-047 and DP-03 are Class S medium, so even the per-class mean composition is unchanged. The corrected trigger (re-plan section 9, worktree copy line 264: pause only if revised run-complete exceeds 31h, or a per-class mean exceeds its estimate by more than 25 percent with at least 3 graded tasks of that class; 22-31h continues with a recorded estimate; 3-hour wall-clock fallback) is unaffected by either option. See A4 for the stale copies of this trigger that DO need fixing.

### The R3-047 drop and the invalid cap (must be recorded)

- The owner-ordered pre-run drop must be recorded as a pre-run exclusion that does NOT count toward the invalid cap (max 5 total, max 2 per medium group). It is decided before task 1 with a replacement already named, exactly like the 45 tasks excluded during list building, not a mid-run invalid. If it counted, the medium group would sit at 1 of 2 before task 1, and 2 timeanddate invalids would stop the run under F-17. That would be a speed and correctness trap. Record the decision in du-phong.txt, in the state file (invalid_by_group trung_binh stays 0, with a note), and in re-plan G-46. Do NOT edit the frozen key file: its line about DP-01 ("da het vi R3-047 INVALID") is stale wording in a frozen file; the run docs carry the clarification instead.

## Findings per review question

1. R3-047 drop: vote Option A, reasoning above. DP-03 has no separate time estimate in any file; its task shape is faster than R3-047, so it does not change the budget.
2. Budget: 19-31h holds under Option A. See recompute above.
3. Checkpoint: unaffected. Position 34 is after the checkpoint; both tasks are Class S medium.
4. Shared agents watchdog: r3l3-agents-watch (5 min, enabled, verified live in cron.list) adds no coordinator serial time. It is a cron worker job doing read-only CDP/read.py checks, and it pokes only on a trigger (silence over 15 min on a pending message, last sent newer than last seen reply, no poke in the last 15 min). The only coordinator cost is handling a real alert, which is the point of the watch. The old mei-mochi-15m-watchdog is verified DISABLED in cron.list. Keep the setup. See A5 and A6 for the stale text that still says the old watch gets re-enabled.
5. Per-agent internal watchdogs: NOT yet verified, and the re-plan section 5 line "The run coordinator verifies all 4 are running before task 1" makes them a hard pre-task-1 gate with an unbounded wait. Clone1 and clone2 already had theirs; only mei and mochi are pending. A bounded wait is worth it (they catch subagent-level stalls inside each agent's account, which the shared watch cannot see), an unbounded wait is not. See A7.
6. Gutenberg watch removal: verified live, the cron r3l3-gutenberg-fixture-watch is absent from cron.list entirely, not just disabled. The removal saves one trivial hourly run (curl plus find) and adds no schedule risk, because the R3-089 fixture was refreshed 08:59 on 25/11 and is in-window until 2026-12-01 (prepare report G-39), the run should finish about 26/11, and the section 9 pre-position-49 point check replaces the continuous watch. Gutenberg polling is moot now that R3-047 is dropped. See A6 for the stale section 5 row and the date guard.
7. Workspace arrangement: ws3 holds ONLY the 4 agents, all other work on ws2 (owner 25/11 08:54). This helps run speed: no focus steal, no accidental navigation of agent windows, no live-runner tab switching in front of the owner. The G-44 pill test ran in ws2 only. Cost is zero to the run. See A8 for the one missing sentence (the Zen run tab lives in ws2, never ws3).

## Amendments (numbered, each with file and line or section)

### A1. Apply the R3-047 drop as Option A, pre-decided and pre-checked, before task 1

- Files:
  - `~/workspace/r3l3-run-wt/rung3-run-log/du-phong.txt`, section "Cap da dung": record "R3-047 DROPPED by owner order 25/11 10:34 (Gutenberg 503, verified live by this council), replaced by DP-03 at position 34, Pair B, Class S, medium". Record that the drop does NOT count toward the invalid cap.
  - `~/workspace/r3l3-run-wt/rung3-run-log/thu-tu-chay.txt`, the single 55-ID run-order line: replace R3-047 with DP-03 at position 34. Update the file header counts only if they change (they do not: still 55 tasks, still 37 medium). Recompute the sha256 and update the header line and the state file.
  - `~/workspace/r3l3-run-wt/rung3-run-log/r3-l3-exception-list.txt`, Class S list: replace R3-047 with DP-03 (the count stays 46 Class S, 9 Class L). DP-03 is already named Class S in the backups paragraph, so this is a substitution, not a reclassification.
  - `~/workspace/r3l3-run-wt/rung3-run-log/r3-l3-coordinator-state.json`: set backups_used to ["DP-03"], keep invalid_by_group trung_binh at 0, add a note that the owner-ordered pre-run exclusion does not count toward the invalid cap.
  - Worktree re-plan section 9 milestone "Before position 34" and G-46: change R3-047 from PENDING (leans invalid, re-check before position 34) to DROPPED by owner order, replaced by DP-03. Delete the Gutenberg re-check step for position 34; it is moot.
- Also run the G-47 script check for the DP-03 assignment BEFORE task 1 (unused, same difficulty, not DP-01, order matches du-phong.txt) and record it, so position 34 needs zero decision time when it arrives.

### A2. Fix the two stale lines in the canonical run-order file, then re-hash and re-run G-32

- File: `~/workspace/r3l3-run-wt/rung3-run-log/thu-tu-chay.txt`.
- Line 16 still says FCC pane PID 203375, fcc-claude 2.1.331, created 2026-11-24 17:18:33. The live values (state file, deputy declaration, prepare report G-30) are pane PID 22399, fcc-claude 2.1.332, recreated 2026-11-25 09:00:18 after the laptop reboot. The prepare report claims G-32 fixed this ("FCC pane PID 203375 -> 22399"), but the file still carries the old values, so G-32 fixed the hashes, not these lines.
- Line 38 still says deputy session 028399b1, declaration 2026-11-24 17:24:46. The live deputy is 8397cff5, declaration 2026-11-25 09:34.
- Speed cost if unfixed: the run coordinator reading the canonical file at task 1 pings a dead pane PID and messages a dead deputy session, then spends a respawn and re-confirmation cycle. Fix both lines, recompute the sha256 (currently eaffee95e281efa1b9611efe09f0b60ee1f1424dc5747b275530763e5234bdba), update the state file note, and re-run the G-32 grep pass to zero mismatches.

### A3. Update the state-file deputy field BEFORE task 1, with a fresh deputy re-confirmation in the same step

- File: `~/workspace/r3l3-run-wt/rung3-run-log/r3-l3-coordinator-state.json`, deputy field still records 028399b1.
- The worktree re-plan section 0A says the run coordinator updates it "at task 1", but that update would post-date the deputy's 09:34 confirmation, which breaks G-24's own rule (a confirmation older than the last material state change does not satisfy G-24). Do the update before task 1 and have the deputy re-confirm after it, so task 1 is not delayed by a re-confirmation round trip. Alternatively, amend G-24 to exempt a deputy-field-only update, but the pre-task-1 update plus re-confirmation is cleaner and costs about 2 minutes.

### A4. Align the checkpoint trigger in the two stale files to the corrected re-plan trigger

- Files:
  - `~/workspace/r3l3-run-wt/rung3-run-log/r3-l3-time-budget.md`, lines 31-37: still says pause if the revised run-complete is outside 19-21h. Replace with the corrected trigger from worktree re-plan section 9 (line 264): pause only if revised run-complete exceeds 31h, or a per-class mean exceeds its estimate by more than 25 percent with at least 3 graded tasks of that class; 22-31h continues with a recorded estimate; 3-hour wall-clock fallback checkpoint stays.
  - `~/workspace/r3l3-run-wt/rung3-run-log/thu-tu-chay.txt`, tail paragraph: still says "neu uoc tinh hoan thanh vuot 19-21h ... TAM DUNG". Replace with the same corrected trigger.
- Speed cost if unfixed: a revised estimate of 22-31h is the expected outcome under the honest budget, and the stale trigger would pause the run and wait on an owner decision for a case the corrected plan explicitly says continues. That is the single most likely spurious pause in the run.

### A5. Make the worktree re-plan the single canonical copy; stamp the stale root copy SUPERSEDED

- File to stamp or remove: `~/workspace/r3-l3-replan-final-20261124.md`. It still says the R3-029 runner is Codex at line 200 ("The runner (Codex, position 25)"), still has the B-07 OR in the chain-broken definition at line 225 ("unreachable for 15 minutes OR if no per-task report appears"), still carries the mei-mochi re-enable language in section 5, and still lists the superseded not-ready items in section 11 (mei messaging broken, Mochi locked, Clone2 reset, FCC no reply, pill unproven, TB-B2 unsigned). The deputy declaration cites this root copy as "the operative plan", which proves the stale copy is being treated as operative by at least one member.
- The worktree copy has all of these fixed (R3-029 runner FCC, chain-broken AND at line 243, agents-watch row in section 5, section 0A current situation). Stamp the root copy SUPERSEDED on every page or delete it, and point all briefs at the worktree copy.
- Also fix the two leftover re-enable lines that contradict the owner 10:31 decision: worktree re-plan F-14(c) (still says the mei-mochi re-enable "is recorded with owner confirmation") and the prepare report final paragraph ("The run coordinator enables mei-mochi-15m-watchdog at run start"). Both must say the old watch stays DISABLED and r3l3-agents-watch replaces it. If the coordinator follows the prepare-report line at start, two crons would poke mei and mochi.

### A6. Update the watchdog table for the removed Gutenberg watch and record the new 6-watch set

- File: worktree re-plan section 5. The merged "R3-047-Gutenberg-watch + R3-089-fixture-watch" row still lists a live 60-min cron. That cron is removed (verified absent from cron.list). Change the row to REMOVED: Gutenberg polling moot (R3-047 dropped, A1), R3-089 fixture covered by the section 9 pre-position-49 point check (find -mtime -7 returns exactly 6).
- Add a date guard to the section 9 R3-089 milestone: if position 49 has not been reached by 30/11 12:00, the coordinator re-verifies the fixture before position 49 runs. The fixture is good to 2026-12-01, so this guard only bites if the run stalls badly, and it costs one find command.
- Update the G-34 record to the actual enabled set, verified by this council in cron.list: r3l3-agents-watch, r3l3-coordinator-liveness-watch, r3l3-zen-laptop-health, r3l3-runner-process-watch, r3l3-ledger-push-watch, r3l3-timeout-watch (6 enabled). mei-mochi-15m-watchdog disabled. Gutenberg watch removed.

### A7. Bound the per-agent internal watchdog gate; do not let it delay task 1 without limit

- File: worktree re-plan section 5, paragraph "Per-agent internal watchdogs". Change "The run coordinator verifies all 4 are running before task 1" to a bounded gate: verify-or-record-missing within 30 minutes of the owner start order; the run starts at the end of that window with the shared r3l3-agents-watch covering, and the mei/mochi internal watchdogs may land mid-run. Clone1 and clone2 already had theirs, so only mei and mochi are pending, and mochi's matters most because she is scorer 1 Pair A. An unbounded wait for two setup confirmations is not worth it; a 30-minute bounded wait is.

### A8. State the run-tab workspace explicitly

- File: worktree re-plan section 0A, workspace arrangement bullet. Add one sentence: the Zen run tab lives in ws2, never ws3, and no drive happens in ws3. This closes the gap between the ws3-only-agents rule and the run-tab rule, and it matches the G-44 pill test, which ran in ws2 only.

### A9. Commit the uncommitted operative-plan changes before task 1

- File: `~/workspace/r3l3-run-wt/improvements/r3-l3-replan-final-20261124.md`. `git status` shows it modified and uncommitted (30 insertions, 12 deletions: section 0A plus the section 1, section 5, and section 11 updates). The operative plan must be on the branch, not only in a dirty worktree, before task 1. Commit with an explicit pathspec on both add and commit, verify `git status --porcelain` shows only intended files, and verify via ls-remote. This council does not commit; the parent or the run coordinator does.

### A10. Pre-position the DP-03 evidence and scoring path so position 34 is a normal task

- Files: worktree re-plan section 9 and the lane briefs. DP-03 runs in the Codex lane at position 34 and inherits Pair B. Confirm in the Codex lane brief before task 1 that DP-03 is Class S (score from sealed snapshot, decoupled, no live re-read), that its manifest-gate requirements are in evidence-requirements.json (it already is, as one of the 5 backups in the 61 keys), and that the DP-03 fixture check (at least 3 TCP ports with visible process names, N=5 per the key) is done by the coordinator before position 34. This is the same pre-milestone pattern as the R3-089 and R3-079 checks, and it keeps position 34 at the normal Class S pace instead of a decision pause.

## What this council did NOT find

- No speed case for rejecting the plan. The 19-31h budget, the rolling two-lane design, the decoupled scoring, and the backpressure conjunction all survive the R3-047 drop unchanged.
- No watchdog overhead problem. The shared agents-watch is read-only work done by a cron job, not coordinator serial time.
- No workspace-arrangement problem. ws3-only-agents helps speed and costs nothing.
- The checkpoint trigger, the stale run-order lines, and the two-copy re-plan divergence are the only time traps found, and all three are fixed by A2, A4, and A5 before task 1.
