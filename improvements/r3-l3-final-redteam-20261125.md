# R3-L3 Final Redteam Verdict, Wed 2026-11-25

Independent redteam, final prepare review. Ordered by the owner at 10:35 25/11, with the order that R3-047 is DROPPED from the run entirely. I verified everything myself from the files. I did not trust the prepare report, the councils, or any summary. I did not edit the re-plan, the state file, or any run doc. I did not commit. I did not start the run. I did not run any run task.

## Standing rules

- NO OpenRouter. Never try it, never propose it. FCC's built-in OpenRouter-free backend is allowed per the owner's 25/11 decision. The ban covers only Opencode.
- NO em dash (U+2014) or en dash (U+2013) in any file. Use commas, periods, or short hyphens only.
- NO personal info on GitHub (no name, address, email, phone, schedules, photos, accounts, passwords, tokens). The R3-029 password must NOT appear in any file.
- Never assume an agent's capabilities. Check or ASK THE AGENT DIRECTLY in its own chat. Every brief must state the delivery path explicitly.
- Clone1 and clone2 have NO Tailscale or SSH. Repo and web work only. Do NOT give them machine tasks.
- CDP-first observation: CLI and API first, then DOM, screenshot and vision last.
- Never close or navigate any window or tab the owner opened. Never close the 4 agents' windows in ws3.
- The pill MUST be visible on ANY agent control. Pill text is always plain "Computer use active."
- Do NOT edit MEMORY.md. Observations go to ~/memory/2026-11-25.md.
- Do NOT start the run. Do NOT run any run task.

## Verdict: NOT READY

The run must NOT start. The owner's order to drop R3-047 has not been executed in ANY run document, so every operative doc still tells the coordinator to run R3-047 at position 34 against a dead Gutenberg. On top of that, there are still two disagreeing FINAL re-plans, and the deputy certified the stale one as operative. Four BLOCKING items below must be mitigated before task 1. The MUST-FIX items must also be fixed or explicitly accepted by the owner in writing before task 1.

Note: the final council meeting today already flagged two of these problems itself (final-council-1-stability-20261125.md line 54: the deputy read the stale copy; final-council-3-correctness-20261125.md line 68: section 11 is stale and contradicts section 0A). They are still unfixed at the time of this verdict, which is why the verdict is NOT READY rather than a note.

## BLOCKING

### B-F1. The R3-047 drop exists nowhere except the owner's order. Every operative doc still runs R3-047.

What breaks: thu-tu-chay.txt is declared canonical for the run order (re-plan G-32, execution plan stamp). It still lists R3-047 at position 34 in a 55-token order line with no DP-03 anywhere. The coordinator follows that file, so at position 34 it will run R3-047, a medium task against gutenberg.org, which was still DOWN at 09:15 25/11 (curl 503 twice, second day). The run then improvises a mid-run invalid plus backup under time pressure, exactly the failure the pre-run drop was meant to avoid. The swap itself is sound (see Verified OK), only its execution is missing.

Every leftover reference, all verified by grep:

- rung3-run-log/thu-tu-chay.txt line 8: order line still contains R3-047 at position 34 (verified by token count: 55 tokens, token 34 is R3-047, DP-03 absent). Line 83: R3-047 ruling still says "Kiem tra lai gutenberg.org bang trinh duyet ngay truoc khi R3-047 chay (vi tri 34). Neu van bao tri, tuyen bo INVALID va dung DP-03. Neu da mo lai, chay binh thuong." That is a re-check plan, not a drop.
- rung3-run-log/du-phong.txt lines 37-43: R3-047 paragraph still says re-check before position 34 and use DP-03 if still down, run normally if back. DP-03 is still listed as unused medium backup 1 (order DP-03/DP-06/DP-07). Line 19 still says DP-01 was used for R3-047 INVALID in R3-L2, which is history, fine, but the live paragraph contradicts the drop.
- rung3-run-log/r3-l3-exception-list.txt line 43: R3-047 is still listed as a Class S run task. The count line ("9 of 55 Class L, 46 Class S") only stays true if DP-03 replaces R3-047 one for one in Class S, and no doc records that replacement.
- improvements/r3-l3-lane-brief-codex-L3-20261125.md line 13: Codex lane task list still includes R3-047. Line 50: pre-milestone reminder still says Gutenberg re-checked in a browser right before position 34 (R3-047). Codex already acknowledged this brief in writing (G-30, 09:06), so the ack covers a brief that contains a dropped task.
- rung3-run-log/scorer-briefs/rung3-scorer-brief-R3-L3-addendum.md lines 46-48: invalid candidates list and "R3-047 re-check: the coordinator re-checks gutenberg.org in a browser right before R3-047 runs". Pair B scorers will expect R3-047 evidence.
- improvements/r3-l3-replan-final-20261124.md (worktree copy) line 20: section 0A still says "R3-047 (position 34) leans invalid; Mochi re-checks Gutenberg in a real browser right before position 34; if still down, INVALID plus the medium backup DP-03." Line 258: "Before position 34 (R3-047): re-check Gutenberg in a browser right before position 34." Line 289 and line 309: G-46 checklist and pre-milestone reminders still carry the Gutenberg re-check. The 0A update worker was cancelled before finishing, and this is the unfinished part.
- rung3-run-log/r3-l3-coordinator-state.json line 66: note still says "R3-047 is a 5th pre-run INVALID CANDIDATE... Re-check Gutenberg in a browser right before position 34; if still down, declare INVALID and use DP-03. If back, run R3-047 normally."

What must happen before task 1: execute the swap in all six places above (thu-tu order line R3-047 to DP-03 at position 34; du-phong mark DP-03 USED for R3-047 and strike it from the available medium order; exception list replace R3-047 with DP-03 in Class S; Codex brief re-issued or amended in writing with a fresh Codex ack; scorer addendum amended; re-plan 0A and section 9 rewritten to DROP, not re-check). Then recompute both sha256 hashes, re-record them in the state file, re-run G-32, and record whether the drop counts as invalid 1 in the medium group (see B-F4). The frozen key file needs no change (DP-03 key is already frozen, see Verified OK). The evidence-requirements.json R3-047 entry may stay as a dead entry, but the manifest gate must be proven against DP-03, which it is (DP-03 spec exists there).

### B-F2. Two FINAL re-plans disagree, and the deputy certified the stale one as operative. The owner decisions of 25/11 live only in uncommitted changes.

What breaks: there is no single operative re-plan. The worktree copy (improvements/r3-l3-replan-final-20261124.md) has section 0A and the fixes. The root copy (~/workspace/r3-l3-replan-final-20261124.md) is stale. The deputy declaration (~/workspace/r3-l3-deputy-declaration.md) states it read the root copy and calls it "the operative plan, commit 81919c0c". That citation is false: 81919c0c is the todolist-push tip in the worktree repo, and the root file is outside that repo. The deputy therefore confirmed a plan that says, in its text:

- ~/workspace/r3-l3-replan-final-20261124.md line 200: the R3-029 password goes to Codex at position 25. The worktree copy line 218 says FCC. Position 25 is in the FCC lane (positions 1-28). If the run coordinator reads the stale copy, the credential goes to the wrong runner, and Codex (which never runs position 25) holds a credential it must never hold, while FCC arrives at position 25 without it. The FCC lane brief (line 44) correctly says the credential comes in the FCC task brief only, so the two sources contradict each other.
- ~/workspace/r3-l3-replan-final-20261124.md line 225: chain-broken definition still has the OR ("unreachable for 15 minutes OR if no per-task report appears for 30 minutes"). The worktree copy line 243 has the AND fix. If the coordinator or the liveness watch follows the stale copy, a normal long task with no per-task report for 30 minutes counts as a broken chain and can trigger a false takeover alert. The live coordinator-liveness-watch cron body does use AND (verified by reading the cron), so the live enforcement matches the worktree copy, but the document the deputy certified says OR.
- ~/workspace/r3-l3-replan-final-20261124.md roster row: deputy is session 028399b1. The fresh deputy is 8397cff5. Workers reading the stale roster expect the old deputy.
- ~/workspace/r3-l3-replan-final-20261124.md section 5: the old mei-mochi-15m-watchdog is to be re-enabled for the run. The worktree copy says it stays DISABLED and r3l3-agents-watch replaces it. cron.list confirms DISABLED for mei-mochi-15m-watchdog and ENABLED for r3l3-agents-watch. A coordinator following the stale copy re-enables a watch the owner ordered to stay disabled, double-covering mei and mochi with two poking watches.

Separately, `git status` in ~/workspace/r3l3-run-wt shows the worktree re-plan as Modified and uncommitted. Every 25/11 owner decision in section 0A (FCC backend 09:23, shared agents-watch 10:31, per-agent internal watchdogs 10:31-10:32) lives ONLY in those uncommitted changes, except the FCC backend decision, which is also recorded in the committed deputy dry-run record (commit 3a2f45aa). If the worktree is reset or the coordinator reads the committed tree, the decisions vanish and the FCC backend looks like a ban violation again.

What must happen before task 1: commit the worktree re-plan with section 0A; stamp the root copy SUPERSEDED in its first lines (or delete it, and record the deletion); the deputy re-confirms in writing that it read the worktree copy (path improvements/r3-l3-replan-final-20261124.md) and lists the three corrected facts (R3-029 runner FCC, chain-broken AND, deputy 8397cff5). The parent must confirm the committed tree contains the 0A decisions.

### B-F3. The state file still names the dead deputy. The takeover fencing points at a session that no longer exists.

What breaks: rung3-run-log/r3-l3-coordinator-state.json line 26, field "deputy", still reads "028399b1-634c-4b37-84d1-6c8689c87ab8 (declaration at ~/workspace/r3-l3-deputy-declaration.md, read plan+state 2026-11-24 17:24:46 +07, on STANDBY)". The fresh deputy is 8397cff5 (declaration 09:34 25/11, dry run PASS 09:32-09:34). The state file is the machine-readable source of truth the deputy, the coordinator, and the watches read. Section 7 fencing says the deputy writes a takeover record into the state file (coordinator_active set to the deputy's id) and workers obey only the coordinator id named in the state file. If the run coordinator forgets the "update at task 1" step, then at takeover time the deputy (8397cff5) writes coordinator_active = 8397cff5 while the state file's deputy field still names 028399b1, so a worker checking "is this the deputy" against the state file rejects the real deputy, and the parent's wake message names a deputy the state file does not recognize. The deputy dry-run record itself documents that the deputy has no direct channel to subagent workers, so the wake chain already depends entirely on the parent; a wrong deputy id in the state file removes the one written cross-check the parent has. There is no reason to defer this to task 1: it is a one-field edit now, plus a parse check.

What must happen before task 1: update the deputy field to 8397cff5-3099-4735-93fb-34415db38a3c now, not at task 1; verify the state file still parses as JSON; record the edit in the state file notes with a timestamp. Also note the state file currently has no coordinator_active field and no epoch field at all (verified by grep: zero hits). That is acceptable before task 1 only if the run coordinator creates both at task 1 with epoch starting at 1, as section 7 requires. Put that creation on the coordinator's start checklist in writing.

### B-F4. After DP-03 is consumed pre-run, the shared-cause medium group has 2 backups left for 4 tasks, and the cap math contradicts itself.

What breaks: the shared-cause medium group is R3-011 (pos 11), R3-028 (pos 24), R3-036 (pos 27), R3-046 (pos 33), all medium, all timeanddate. The du-phong.txt R3-011 ruling says one proven shared cause counts as 1 invalid for BOTH the total cap (5) and the group cap (2). The same file also says each affected task still leaves the sample and still uses the backup rule. After the R3-047 drop consumes DP-03, the remaining medium backups are DP-06 and DP-07 only. If the shared cause fires, 4 tasks leave the sample but only 2 backups exist, so the run is 2 tasks short. The plan simultaneously says the run continues (cap counts 1 event, under the cap of 2) and cannot complete (2 unfilled slots). G-40 says escalate to the owner rather than improvise, but no pre-decided outcome exists, so the escalation burns run hours on a question that was fully foreseeable before task 1. The pass bar is also undefined in that state: 55 tasks minus 4 invalid plus 2 backups is 53 graded tasks, and 53/55 as written is unreachable if 2 slots stay empty.

Two sub-questions must also be decided and recorded in the state file before task 1, because they change the cap arithmetic:

- Does the owner-ordered R3-047 drop count as invalid 1 in the medium group (invalid_count 1, trung_binh 1)? If yes, only 1 more medium invalid is allowed before the run stops (F-17: a 3rd medium invalid stops the run; the drop plus 2 more would be 3). If no, record that an owner exclusion is not an invalid, with the owner's words. Right now the state file says invalid_count 0 and trung_binh 0, which answers neither.
- If the shared cause fires, is the outcome stop, accept a short run with a recomputed bar, or something else? The execution plan line 37 allows the bar to change only by an owner decision before task 1 if a task is excluded with a recomputed bar. That decision must be made now, not mid-run.

What must happen before task 1: the owner decides and the decision is written into the state file and the re-plan: (a) whether the R3-047 drop counts toward the medium cap, (b) the exact outcome if the shared-cause group fires after DP-03 is consumed. Without (a) and (b), the run can enter a state its own rules cannot resolve.

## MUST-FIX

### M-01. G-32 "DONE (fixed)" is false. The canonical run-order file still contradicts the state file on three fields.

The prepare report (line 30 area, G-32 row) claims 10 mismatches fixed, including "FCC pane PID 203375 -> 22399 (version 2.1.332)" and "Mochi full session id recorded". I read thu-tu-chay.txt and the state file side by side. The fixes did not land in thu-tu-chay.txt:

- thu-tu-chay.txt line 2: "Branch todolist-push tip ccd83e5." The state file freeze.todolist_push_tip is 81919c0c, and the execution-plan stamp (line 3 of both copies) also says tip 81919c0c. du-phong.txt line 2 also still says tip ccd83e5.
- thu-tu-chay.txt line 16: FCC pane PID 203375, fcc-claude 2.1.331, created 2026-11-24 17:18:33. The state file runners.fcc says pane_pid 22399, version 2.1.332, recreated 2026-11-25 09:00:18. The deputy dry-run record agrees with the state file (pane 22399, 2.1.332).
- thu-tu-chay.txt line 25: Mochi target A67A718D5E236F894F9863F48834743C. G-23 verified the live Mochi target as A25AA6F0370A00A174BC5304A333417D (Chromium 9223). F-12 forbids hardcoded target IDs and requires resolving from /json/list, but thu-tu-chay.txt hardcodes a stale one, and a coordinator that trusts the canonical file will message the wrong target.

G-32's own rule declares the state file plus thu-tu-chay.txt canonical. A canonical file that contradicts the state file on the tip, the runner pane, and a scorer target is not a pass. Re-run G-32 after the B-F1 swap, fix thu-tu-chay.txt itself (not just the state file), and record the grep pass in the run log with zero mismatches.

### M-02. The worktree re-plan is internally inconsistent. The cancelled plan-update worker left section 10 and section 11 stale.

- Line 155, F-14(c): "The mei-mochi 15-minute watchdog re-enable for the run is recorded with owner confirmation (the owner disabled it tonight; run-start approval covers the re-enable, recorded in section 5)." This directly contradicts section 0A line 18 and the section 5 row, which say the old watch stays DISABLED and r3l3-agents-watch replaces it, and contradicts cron.list, where mei-mochi-15m-watchdog is DISABLED. A coordinator reading F-14 re-enables a watch the owner ordered disabled.
- Section 10 todolist: zero checked boxes (verified by grep: 0 hits for "[x]"). Every gate G-23 to G-49 is still shown as "[ ]" even though Phase 0 closed them. The diff header claims the Phase 0 todolist was updated; it was not.
- Section 11, lines 341 and following, "What is NOT ready for tomorrow": still lists Mei messaging STILL BROKEN (line 342), Mochi locked until 02:38 Wed 25/11, Clone2 reset at 02:38, FCC not replied, pill unproven, TB-B2 unsigned. All six are superseded by 25/11 morning events (G-23 PASS, resets passed, FCC ack 09:06, G-44 test, G-33 claim). A coordinator using section 11 as its start checklist blocks the run on ghosts.
- Section 5, line 200: the watchdog table still lists the "R3-047-Gutenberg-watch + R3-089-fixture-watch (merged, one cron)" row. That cron does not exist in cron.list at all (not disabled, absent). See M-08.

Fix: finish the cancelled worker's update (sections 5, 10, 11, F-14). The section 0A disclaimer ("where this section says otherwise, this section is the current state") does not cover unchecked boxes or a stale not-ready list, so it does not cure these.

### M-03. G-42 "redteam confirmation DONE, 10/10 BLOCKING mitigated" overstates the redteam's own written record.

The prepare report line 30 says redteam confirmation is DONE with 10/10 BLOCKING mitigated, and line 69 says "Fresh reviewer grepped the file: no OR trigger remains. Redteam re-confirmed B-07 MITIGATED." The redteam's own confirmation file (improvements/r3-l3-redteam-confirmation-20261125.md line 12 and line 82) says the opposite: "9 of 10 BLOCKING objections are mitigated at plan level. 1 is only partially mitigated: B-07" and "**NOT CONFIRMED.**" No second redteam confirmation artifact exists in improvements/. The "fresh reviewer" is unnamed, has no file and no signature, and under the re-plan's own decision rule (section 0: "The judge is: the redteam confirms whether its own objections are mitigated") a non-redteam reviewer cannot close B-07.

My own verification as the final redteam: B-07 IS mitigated in the worktree copy. The chain-broken definition is AND in all three places (line 38 summary, section 5 trigger (b), line 243 section 8), and the remaining " OR " hits in that file (lines 126 and 264) are the G-39 alternative and the checkpoint trigger, both legitimate ORs, not chain-broken triggers. The live coordinator-liveness-watch cron body also uses AND for trigger (b). B-07 is NOT mitigated in the stale root copy, which still has the OR at line 225. So I, the final redteam, confirm B-07 MITIGATED in the worktree copy only. That confirmation needs to be accepted by the parent in writing and recorded, and the stale copy problem must be fixed per B-F2, before G-42 can honestly read DONE.

### M-04. Per-agent internal watchdogs are unverified. "The run coordinator verifies all 4 before task 1" is a hope, not a gate.

The worktree re-plan lines 19 and 210 say each of the 4 Muses runs its own internal 10-minute watchdog, that clone1 and clone2 already had them, that mei and mochi are being instructed to create theirs, and that the run coordinator verifies all 4 are running before task 1. I found no evidence artifact for any of the four: no file, no cron id, no timestamp, no confirmation message on record. "Clone1 and clone2 already had them" is an uncited claim. Mei and mochi are "being instructed" by a separate worker with no confirmation on file. There is no acceptance criterion: what counts as "running" (a reply saying yes, a log line, a heartbeat)? There is no named file the coordinator checks. These watchdogs live inside the agents' own accounts, so I cannot verify them from the VM, and neither can the run coordinator except by asking each agent and trusting the reply.

The good news: they are redundant, not load-bearing. The shared r3l3-agents-watch is live and verified (cron.list ENABLED, 5 min; cron.status last successful run 10:42:48 +07, with a run in flight at the time of this review). Its body checks all 4 agents, pokes mei and mochi via the daemon one at a time, pokes clone2 via CDP, and is observation-only for clone1. Silence detection does not depend on the internal watchdogs.

Fix before task 1: either produce a named confirmation artifact per agent (who confirmed, when, how), or downgrade the internal watchdogs to an accepted limitation in writing ("unverified, redundant with r3l3-agents-watch") with the owner's decision. Do not let task 1 start on an unverified "the coordinator will check" with no defined check.

### M-05. The pill procedure is a rule without a mechanism in the lane briefs. G-44 "PROVEN" was a 4-second blank-tab demo, not a drive on either runner's path.

The prepare report G-44 row says PROVEN, with evidence files improvements/g44-during-tight.jpg and improvements/g44-bidi-pill-test.mjs. Both files exist (verified). The test was a live BiDi drive 09:01:48-09:01:52 in ws2 only, 4 seconds, one blank tab created, read, screenshotted, closed. The prepare report's own caveat says the mechanism is MANUAL and zen_dom.py has zero pill references, and every BiDi worker must use the acquire and release wrapper.

I grepped both lane briefs. Neither names the mechanism: no script path, no overlay command, no wrapper name, no g44 reference. Both say only "The 'Computer use active' pill MUST show on ANY live drive, before you drive. Re-acquire it proactively before any segment expected to exceed about 8 minutes. Log each acquire and expire with wall-clock time." (FCC brief lines 73-74, Codex brief lines 91-92.) A runner cannot execute "re-acquire" from that text. Worse, the same briefs say "Live drives go through a computer-use session (pill shows). Raw drive paths without the pill are read-only until a pill mechanism exists for them." The runners' drives are not read-only; they must drive. So the briefs simultaneously demand live drives and forbid raw drives without a pill, without giving the pill mechanism for those drives. The 4-second blank-tab demo proves the overlay exists, not that the FCC tmux lane or the Codex exec lane can acquire it on a real task drive.

Fix before task 1: name the exact acquire and release mechanism (script path and command) in both lane briefs, and run one live pill check on each runner's actual drive path (FCC lane and Codex lane), verified by screenshot, before task 1. If that cannot be done, record it as an accepted deviation with the owner's decision, as G-44 itself allows, rather than letting the run silently violate the standing pill rule on every live drive.

### M-06. The ledger cross-check "pair" check does not exist. Its position logic is wrong for every task it would check.

G-49 claims the script "diffs each ledger row against its verdict files (task ID, verdict, pair)". I read rung3-ci/ledger-cross-check.py in full. It defines PAIR_A_POSITIONS, PAIR_B_POSITIONS, task_position(), and pair_for_position(), but main() never calls task_position() or pair_for_position(). The pair is never checked. The functions are dead code. And task_position() is wrong by construction: it returns the task NUMBER (int of the digits in R3-xxx), not the run position. R3-029 would map to 29, Pair B; its real position is 25, Pair A. R3-047 maps to 47, Pair B, which happens to be right for the old order and wrong in general. For DP-03, the regex ^R3-(\d{3})$ returns None, so a DP-03 row has no position and no pair at all.

The script does work for what it actually does: run from the worktree it printed "OK: 0 verdict file(s) cross-checked, 1 test row(s) skipped, 0 errors", and validate-ledger.py with the explicit L3 path printed "PASS: ledger valid: 1 row(s), 0 errors". So the task ID and verdict checks are real. The pair claim is fiction.

Fix before task 1: either wire the pair check to the run order in thu-tu-chay.txt (position of the task id in the order line, 1-28 Pair A, 29-55 Pair B, DP tasks inherit the replaced task's pair per F-18) and prove it with a DP-03 trial row, or drop the pair claim from G-49 and the prepare report. Do not present a check that does not run.

### M-07. Two CI scripts and the run-log README still point at the R3-L1 ledger.

- rung3-ci/resume.py line 58: load_graded() reads R3-L1-grades.jsonl. Its own docstring line 6 also names the L1 file. The L3 ledger is R3-L3-grades.jsonl. Both files currently hold only one test row, so the 23/11 dry run looked fine (ORDER 55, GRADED 0, NEXT R3-001). Mid-run, resume.py status and next will always report GRADED 0 and NEXT R3-001, because it never reads the L3 ledger. If the coordinator restarts mid-run and uses resume.py to find the next task, it re-runs from the start.
- rung3-ci/validate-ledger.py line 123: default path is R3-L1-grades.jsonl. Run without arguments mid-run it validates the wrong ledger and reports PASS on a file that never changes.
- rung3-run-log/README.md line 3: "Append-only ledger: R3-L1-grades.jsonl". Stale doc.

Fix before task 1: point both scripts at R3-L3-grades.jsonl (one line each), fix the README, and re-run the G-35 checks with explicit L3 paths. This is a copy-paste leftover from R3-L1, and it is exactly the kind of silent wrong-file bug the redteam exists to catch.

### M-08. R3-089 fixture: no monitoring remains, and the docs still carry the old expiry.

Verified by cron.list: r3l3-gutenberg-fixture-watch is absent entirely, not disabled. The prepare report line 50 still lists it as ENABLED with last run 09:16:34, which is stale. The cron that also watched the R3-089 fixture is gone with it. I read the r3l3-zen-laptop-health cron body in full: it checks Zen, ports 9222/2828/9223/9224/8082, Zen RSS, daemon and supervisor, and the FCC tmux session. It does not check fixture mtimes at all. No other cron checks them. The only remaining guard is the manual pre-milestone reminder in re-plan section 9 and the refresh doc rung3-run-log/r3-l3-r3-089-refresh.md, which names the run coordinator as owner with a day-before-position-49 refresh.

Two docs are stale on the dates: the refresh doc still says CURRENT FIXTURE STATE verified 2026-11-24 17:07 with log-01..06 mtime 2026-11-22 19:20 and HARD EXPIRY 2026-11-29 19:20, and thu-tu-chay.txt line 76 still says the hard deadline is 2026-11-29 19:20. The fixture was refreshed 08:59 25/11 (prepare report G-39), so the real expiry is 2026-12-01. The honest risk: within the planned 19-31h window the run ends 26-27/11, inside the window, so this cannot bite on plan. It bites only if the run slips past 2026-12-01, which needs a multi-day overrun, and the fix then is a seconds-long touch refresh before position 49, which has no external dependency. So this is MUST-FIX, not BLOCKING: update the refresh doc to the 25/11 08:59 state and the 2026-12-01 expiry, fix the thu-tu-chay.txt line 76 deadline, replace the dead section 5 cron row (line 200) with the named manual check, and put the pre-49 refresh on the run coordinator's start brief in writing.

### M-09. G-33 TB-B2 sign-off: the named evidence file contradicts the closure claim.

G-33 requires an independent verifier to sign the TB-B2 calibration (grade file ~/workspace/r3-l3-calibration-TBB2.md) before task 1, or the gap recorded as an accepted limitation with an owner decision. The prepare report G-33 row says CLOSED, "Independent verifier re-graded all four calibration cases from scratch and SIGNED OFF, 4/4 agreement". The grade file itself says otherwise: its coordinator note (added 2026-11-24 20:02) says "TB-B2 (df4defcc) 4/4 approval rests on the coordinator's own check, NOT on independent verification." The independent verification report (~/workspace/r3-l3-calibration-VERIFICATION.md) contains zero mentions of df4defcc (verified by grep). No signed independent artifact for TB-B2 is named anywhere: no file, no verifier session id, no timestamp. The final council files mention df4defcc only as an id, not as a sign-off.

TB-B2 acts only on disagreement, so the risk is bounded (the plan's own objection-43 pattern), which is why this is MUST-FIX and not BLOCKING. Fix before task 1: either append the independent verifier's signature, session id, and timestamp to the grade file itself, or record the gap as an accepted limitation with the owner's decision, as G-33 allows. Do not leave the gate's named evidence file contradicting its closure.

## SHOULD-FIX

### S-01. Hashes must be re-recorded after the B-F1 swap.

Verified now and matching: sha256 of thu-tu-chay.txt is eaffee95e281efa1b9611efe09f0b60ee1f1424dc5747b275530763e5234bdba, and of du-phong.txt is a57b488f15850413b02918df31db6c985f19e67f7a50fd5899ef121a531a5779. Both match the state file notes. This item is currently fine. It becomes false the moment the swap is executed, so re-record the new hashes in the state file as part of B-F1 and re-verify with sha256sum. Do not let the swap land without the hash update, or G-32 fails again the same day.

### S-02. Deputy hourly standby confirmation has no mechanism.

Section 7 and G-42 say the deputy confirms standby in the state file every hour. No cron prompts the deputy hourly, the deputy is a standby subagent with no self-trigger, and the state file has no standby entries. Either arm an hourly prompt or drop the hourly claim from section 7 and G-42. Related to B-F3 but separate: even with the right deputy id, the hourly confirmation cannot happen as written.

### S-03. G-34 "6/6" needs re-verification with the new watchdog composition.

The prepare report G-34 row says 6/6 succeeded, but its table counted r3l3-gutenberg-fixture-watch (now absent) and did not count r3l3-agents-watch. The live enabled set is still 6 r3l3-* crons (agents-watch, coordinator-liveness-watch, ledger-push-watch, runner-process-watch, timeout-watch, zen-laptop-health), verified by cron.list. Re-run G-34 against the new composition and record the six ids with their last successful runs before task 1. The meta-watch (parent checks each watchdog hourly) is also unrecorded as an armed mechanism; name who runs it.

### S-04. Liveness config still lists gutenberg.org under R3-047.

rung3-ci/liveness-config.json services list includes {"task": "R3-047", "url": "https://www.gutenberg.org/"}. Liveness checks are pre-run, so this is harmless now, but a mid-run liveness re-check would flag R3-047 as a live failure. Annotate or remove it as part of the B-F1 swap. Do not run a mid-run liveness check against a dropped task.

### S-05. Citation drift: the execution plan is 577 lines, not 565.

Both copies of ~/workspace/r3-l3-execution-plan-20261124.md are 577 lines by wc, and both carry the SUPERSEDED ON IDS stamp (line 3) naming the state file, thu-tu-chay.txt, and the FINAL re-plan as canonical. The re-plan sources line says 565 lines. Trivial, but G-32 is supposed to be a zero-mismatch pass, so fix the citation when the re-plan is next edited. Also, verify-list.py hardcodes EXPECTED_TOTAL = 55 against the frozen list doc; that is correct for the frozen list and must not be edited to match the run order. Leave the frozen list alone.

### S-06. The FCC backend decision needs its committed record.

The decision itself is sound and recorded in the worktree re-plan 0A, the FCC roster row, and the committed deputy dry-run record (which quotes the fcc-server response {"status":"ok","provider":"open_router","model":"open_router/openrouter/free"} and the owner decision). The prepare report predates the decision and frames the backend as an open question for the owner to decide, which is now stale but harmless. No separate action beyond B-F2 (commit the re-plan). Do not let a future worker re-flag the FCC backend: the committed re-plan must carry the 09:23 decision in its own words.

## Verified OK (things I checked that hold)

- Hashes match the state file (see S-01).
- DP-03 key exists in the frozen key file: docs/rung3-answer-keys.json, allocated section, DP-03 n 5, n_min 3. R3-047 key also exists there (3 books), so the frozen key needs no change for the swap.
- DP-03 is Class S (exception list line 66: "DP-03, DP-05, DP-06, DP-07 are Class S"), medium difficulty (du-phong.txt, Tier B, backup order 1), and position 34 is in the Codex lane (positions 29-55), Pair B. F-18 says the backup inherits the replaced task's pair, so DP-03 inherits Pair B correctly. Difficulty counts (37 medium, 11 hard, 7 very hard) are unchanged by the swap because both tasks are medium. The swap is sound; only its execution is missing.
- The manifest gate does not assume 55 tasks: manifest-gate.py is a per-task lookup against evidence-requirements.json, which has a DP-03 spec (files ss-output.txt and bao-cao.txt, screenshots_min 1). The gate works for DP-03 as written. The ledger schema task_id pattern DP-0[123567] already includes DP-03. resume.py load_order accepts DP tokens (regex R3-[0-9]{3} or DP-[0-9]{2}). No CI script breaks on DP-03 in the order, except the pair logic in M-06 and the L1 ledger paths in M-07.
- B-07 substance is fixed in the worktree copy (see M-03). The live liveness cron enforces AND.
- R3-029 runner is FCC in the worktree copy (line 218) and in the FCC lane brief (line 44: credential comes in the FCC task brief only). The R3-029 password appears in no file I read.
- The shared agents-watch is live: cron.list ENABLED at 5 min, cron.status last successful run 10:42:48 +07. Its body matches section 0A (clone1 observation-only, clone2 via CDP, mei and mochi via daemon one at a time, never concurrent). The old mei-mochi-15m-watchdog is DISABLED, matching section 0A. There is no gap in mei and mochi silence detection from the shared watch itself; the gap is only the unverified internal watchdogs (M-04).
- The deputy dry-run record exists (rung3-run-log/r3-l3-deputy-dry-run-20261125.md, PASS 09:32-09:34) and honestly documents its one gap: the deputy has no direct channel to subagent workers, by design under the G-42 wake chain.
- The G-44 evidence files exist (g44-bidi-pill-test.mjs and g44-during-tight.jpg). The demo itself is real; the gap is the missing mechanism in the briefs (M-05).

## What I did not verify

- I did not re-grade TB-B2 myself and did not independently re-run the G-35 live checks (Zen, BiDi, FCC tmux, daemon) from this VM. I verified the cron states, the dry-run record, and the files named above. The G-35 pass cited in the prepare report is 09:15-09:25 25/11; the agents-watch last success at 10:42:48 is my own freshest live check.
- I did not message any agent. Per-agent internal watchdog status (M-04) can only be settled by asking the agents directly, which is for the parent or the run coordinator, not for this redteam.

## Bottom line

NOT READY. The single biggest fact: the owner's 10:35 order to drop R3-047 has not reached a single operative document, and the run order file that the coordinator must follow still runs R3-047 at position 34. Execute the swap (B-F1), fix the two-plan problem and the deputy field (B-F2, B-F3), get the owner's decision on the backup-exhaustion contradiction (B-F4), then clear the MUST-FIX list. The plan is close, and the swap itself is sound, but starting now would run a dropped task and improvise the most foreseeable failure mid-run.
