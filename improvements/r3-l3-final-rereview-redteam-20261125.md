# R3-L3 Final Prepare RE-REVIEW, Redteam Verdict, Wed 2026-11-25

Fresh redteam, re-review round. I am not the author of the original redteam verdict. I verified everything myself from the committed files at HEAD d4df3aa1 on branch todolist-push, worktree ~/workspace/r3l3-run-wt. I did not trust the coordinator's summary. I did not edit any run file. I did not commit. I did not start the run. I did not run any run task. I ran the check scripts myself (hashes, G-32, ledger cross-check with my own trial rows, resume.py, validate-ledger.py, cron list and status, SSH read-only checks on the laptop for Zen workspace, file sync, and the R3-089 fixture).

## Verdict: NOT READY

The run must NOT start yet. Most of the fixes are real and verified (B-F1, B-F3, M-01, M-02, M-03, M-05 mechanism, M-06, M-07, M-08, all six SHOULD-FIX items). But two things block task 1. First, B-F2 is not mitigated: the deputy has not re-confirmed in writing that it read the worktree copy, and by the re-plan's own G-24 rule its 09:34 declaration cannot satisfy the current state file (last updated 10:55:25). Second, the fixes introduced a new blocking contradiction: both lane briefs order drives on ws2, the pill report's own Finding 3 forbids exactly that instruction for the Codex lane, and live on the laptop there is no workspace 2 at all, Zen is on ws1. A third must-fix also blocks the G-32 claim: the scorer addendum still lists DP-03 as the first available medium backup. All three fixes are small and mechanical, listed exactly below. Fix them, re-ack the briefs, get the deputy line, then re-verify.

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

## BLOCKING items

### B-F1. R3-047 drop executed in all six places: MITIGATED

I recomputed the order and the hashes myself.

- thu-tu-chay.txt line 8: order line has 55 tokens, token 34 is DP-03, R3-047 absent. Line 83: R3-047 ruling rewritten to DROP, 0 invalids, no Gutenberg re-check, no Gutenberg monitoring.
- du-phong.txt line 10: DP-03 marked USED pre-run for R3-047, no longer in the available table. Line 17: the false DP-01 note corrected. Line 35: R3-047 DROP paragraph. Line 44: used-capacity entry, medium backups left DP-06, DP-07.
- r3-l3-exception-list.txt line 44: DP-03 replaces R3-047 in Class S, counts unchanged 9 Class L, 46 Class S.
- Lane brief Codex line 13: DP-03 at position 34. Line 50: pre-milestone reminder says DP-03 at position 34, no Gutenberg check, no Gutenberg monitoring.
- Scorer addendum lines 46-48: R3-047 not a candidate, DROP, 0 invalids, DP-03 at position 34, no Gutenberg check.
- Re-plan section 0A line 22: DROP, 0 invalids, DP-03 at position 34. Section 9 line 263: before position 34 (DP-03), no Gutenberg check.
- State file line 68: R3-047 DROP note, 0 invalids, DP-03 at position 34.
- Hashes recomputed by me: thu-tu-chay.txt bf3e75507cb4eaa05f1c3e846fd75f74004a84492f396c04a0dec126fb2e9e85, du-phong.txt 0cf06dda18cb32a47c99f5d5a4be67d8a8d5541d58c072f0f8e8df5c982f5619. Both match the state file line 53. The 09:15 hashes (eaffee95, a57b488f) are correctly superseded there.
- Residual, not B-F1: the scorer addendum header and backup order lines are still stale (see N-03). The six B-F1 places themselves are done.

### B-F2. Worktree re-plan is the only operative plan: NOT MITIGATED

The stamp half is done. The deputy half is not.

- Root copy ~/workspace/r3-l3-replan-final-20261124.md line 1: stamped SUPERSEDED 2026-11-25, names the worktree copy as operative, lists the four stale facts. Stamp verified present.
- Worktree copy improvements/r3-l3-replan-final-20261124.md has section 0A (lines 12-25) and the three corrected facts: R3-029 runner FCC (section 6, line 223, and 0A line 21), chain-broken AND (lines 42, 201, 248), deputy 8397cff5 (roster line 75, 0A line 23).
- BUT the deputy has NOT re-confirmed in writing that it read the worktree copy. The live declaration ~/workspace/r3-l3-deputy-declaration.md still says, line 15: it read /home/hatch/workspace/r3-l3-replan-final-20261124.md (the root copy) as "the operative plan". Line 16: execution plan "565 lines". Line 17: state file "last updated 2026-11-25T09:15:00+07:00". Line 27: "Backups: medium DP-03, DP-06, DP-07 in that order" (DP-03 is used, not available). All four facts are wrong now.
- Decisive, by the plan's own rule: re-plan line 115 (G-24) says the deputy "must re-read the CURRENT state file and re-confirm in writing before task 1, with a new timestamp after the last state-file update" and "A confirmation older than the last material state change does not satisfy G-24." The state file last_updated is 2026-11-25T10:55:25+07:00 (state file line 45). The declaration timestamp is 09:34 (declaration line 4). 09:34 predates 10:55:25, and the 10:55 update was material (deputy field changed, run order changed to DP-03, hashes changed). So the 09:34 declaration does NOT satisfy G-24 for the current state file, and the section 10 box "[x] G-24: deputy re-confirmed the CURRENT state file in writing, with a new timestamp after the last state-file update (fresh declaration 09:34...)" (re-plan line 283) is false as written.
- The executed fix also deviates from what the councils ordered: Council 3 amendment 14 required syncing the root copy FROM the worktree copy byte for byte and then the deputy re-reading the canonical copy and confirming in writing; Council 1 amendment 91 required the deputy to write a one-line confirmation covering the B-07 AND rule, the R3-029 FCC runner, and the r3l3-agents-watch arrangement. What happened instead: stamp, plus deferral to a "parent start item". A stamp plus a promise is not the written confirmation B-F2 required.
- What must change: the parent messages deputy 8397cff5; the deputy re-reads the worktree copy (improvements/r3-l3-replan-final-20261124.md) and the current state file, and writes a confirmation (new declaration lines or a confirmation line appended to the state file) with a timestamp after 10:55:25, naming the three corrected facts (R3-029 runner FCC, chain-broken AND, deputy 8397cff5, agents-watch replaces the old watch) and the corrected backup order (DP-06, DP-07, DP-03 used). Then the section 10 G-24 box becomes true.

### B-F3. State file deputy field: MITIGATED

- State file line 28: deputy is 8397cff5-3099-4735-93fb-34415db38a3c, fresh declaration 2026-11-25 09:34, dry run PASS 09:32-09:34, G-24 and G-38 CLOSED, on STANDBY. Updated NOW, not deferred to task 1.
- The file parses as JSON (verified with python3 -m json.tool, JSON-OK).
- coordinator_active and epoch do not exist in the state file yet, which is correct: creation at task 1 is on the start checklist in re-plan 0A line 25 and in section 7 ("At task 1, the run coordinator creates these fields first (coordinator_active set to its own id, epoch 1) before releasing task 1").
- Residual, folded into B-F2: the declaration the deputy field points to is stale (see B-F2). The field value itself is right.

### B-F4. Backup exhaustion decision: MITIGATED, with one residual gap (see N-04)

- (a) Drop counts as 0 invalids: recorded in re-plan G-46 line 137, du-phong.txt, scorer addendum line 47, state file invalid_by_group trung_binh 0 and invalid_count 0 (state file lines 42-44). Council 3/3 unanimous, recorded in writing.
- (b) Four-task scenario: recorded in re-plan G-46 line 137, du-phong.txt, scorer addendum line 47: if all 4 shared-cause tasks go invalid, DP-06 and DP-07 replace 2, 2 drop, valid 53, bar recomputes to 51/53, coordinator NOTIFIES the owner (G-40) but does NOT stop.
- Bar reachable: 51/53 is 96.2 percent, the same ratio as 53/55. The run can pass.
- Attack on the "pre-declared table" claim: I checked the parent commit. The table "54 valid needs 52, 53 needs 51 (Council 3 A16, redteam S-15)" was already in the re-plan at commit b061f87c (line 250 there, line 273 now). So applying it is not a new decision invented in this review. The council decision under the user's 23/11 full-autonomy mandate is defensible for (a) and (b): the owner ordered the drop and the run staying 55 tasks at bar 53/55, which directly implies the drop is not an invalid, and (b) applies a rule that predates this review. Note for the parent: the owner has not personally signed (a) or (b); surface the decision in the start message so the user can overrule it.
- Is there a scenario where the bar becomes unreachable? The bar as a ratio is always reachable while valid tasks remain. The gap is narrower: the table has no entry for 52 valid (see N-04). The plan does not deadlock there (Phase 3 line 273: an owner decision is required if the shrink was not pre-declared), but the coordinator would be running toward an undefined bar until closure. That is a SHOULD-level gap, not a B-F4 failure.

## MUST-FIX items

### M-01. G-32 zero mismatches: MITIGATED

My own G-32 re-run, file against file: tip 81919c0c in thu-tu-chay.txt line 2, du-phong.txt line 2, state file freeze line 36. FCC pane PID 22399, fcc-claude 2.1.332 in thu-tu-chay.txt line 16 and state file lines 58, 106, 110. Mochi target A25AA6F0370A00A174BC5304A333417D in thu-tu-chay.txt line 25. Deputy 8397cff5 in thu-tu-chay.txt line 38 and state file line 28. Hashes match (see B-F1). The only stale-value hit in the operative files is state file line 72, a 24/11 20:02 historical note describing the ccd83e5 update as history, not a current value. Note: the live branch tip is now d4df3aa1 while the files stamp 81919c0c as the prepare baseline (prepare report convention). The files agree with each other, which is what G-32 checks.

### M-02. Worktree re-plan internally consistent: MITIGATED

- F-14(c) re-plan line 160: the mei-mochi 15-minute watchdog stays DISABLED, never re-enabled, shared agents-watch replaces it. Corrected.
- Section 10 todolist: 28 boxes [x], the remaining [ ] are honestly pending (section 11 confirmation, during-run items, after-run items). Section 11 rewritten: all six 24/11 not-ready items closed with evidence, plus a "What remains" list naming the deputy re-confirmation and this independent verification.
- Section 5 Gutenberg watch row replaced with the manual R3-089 fixture check (re-plan line 205).
- Nits, not blocking: G-50 is marked [x] in section 10 (line 308) though its verification runs within 30 minutes of the start order; G-35 is marked [x] though this re-review is the verification it claims. The G-24 [x] box is false as written, see B-F2.

### M-03. G-42 overstated 10/10, B-07: MITIGATED in the worktree copy only

- Chain-broken AND in all 3 places in the worktree copy: line 42 (section 0 summary), line 201 (section 5 trigger b), line 248 (section 8 definition). The remaining OR hits are the checkpoint trigger (line 269) and backpressure (line 259), both legitimate ORs, not chain-broken triggers.
- Live cron verified by me: I read the coordinator-liveness-watch cron body file (r3l3-coordinator-liveness-watch__interval@5m.md). Trigger (b) reads "if no per-task report for 30 minutes AND no coordinator heartbeat for 15 minutes". AND confirmed live. Last success 11:23:15 +07.
- Recorded in re-plan line 38 and state file line 75 (correction note). The 24/11 redteam file's 9/10 status is superseded for B-07 by the final redteam's confirmation, as the re-plan says. The stale root copy still has OR, but it is stamped SUPERSEDED.

### M-04. Per-agent internal watchdogs: MITIGATED as a bounded gate

- Gate G-50 is written (re-plan 0A line 21, line 138, section 5 line 215): the run coordinator verifies all 4 within 30 minutes of the start order; if any is missing at 30 minutes, the run starts anyway with the shared agents-watch covering, and the missing one is recorded and set up mid-run. Council 1 dissent (wanted a hard gate) is recorded at line 138.
- I could not verify the 4 internal watchdogs from the VM (they live inside the agents' own accounts, no direct channel), and neither can the run coordinator except by asking each agent. That is the design, and the gate is the check.
- The shared r3l3-agents-watch is live and verified by me: ENABLED, 5 min, last success 11:20:13 +07, a run in flight at check time. Silence detection does not depend on the internal watchdogs.

### M-05. Pill mechanism in lane briefs: MITIGATED in letter, new defect in substance (see N-01, N-02)

- Mechanism named in both briefs with exact commands: FCC brief line 74, Codex brief line 92 (overlay.py acquire/release/status, agent, method, pid, env vars, fail-closed on visible true, ws2).
- Per-lane live checks PASS per improvements/r3-l3-pill-path-check-20261125.md: FCC 10:54-10:57, Codex attempt 3 11:12-11:14, pill visible in during screenshots, release confirmed.
- Both acks name the mechanism (acks report: FCC 11:05, Codex 11:07:34).
- BUT the ws2 instruction in those same brief lines contradicts the pill report's own Finding 3 and the live machine state (N-01), and the stuck-pill workaround is not in the briefs at all (N-02). M-05 as originally written (name the mechanism, run one live check per lane) is done. The new defects ride on the fix itself and are listed below as new items.

### M-06. Ledger cross-check pair check: MITIGATED, proven by me

- I read rung3-ci/ledger-cross-check.py in full. main() now calls task_position() and pair_for_position(), wired to the run-order line in thu-tu-chay.txt (load_order). task_position() returns the run position, not the task number (docstring names R3-029 position 25, Pair A). DP tasks in the order line inherit their position (DP-03 is position 34); mid-run replacements use DP_REPLACEMENT_POSITION.
- My own runs in /tmp (worktree untouched): DP-03 trial row with Pair B verdict files PASS (2 files checked, 0 errors). R3-029 with Pair B verdict files correctly FAILS (suffix B2 is Pair B but position 25 is Pair A). R3-029 with Pair A verdict files PASS. Real L3 ledger PASS (0 checked, 1 test row skipped, 0 errors).

### M-07. CI scripts and README point at R3-L1 ledger: MITIGATED

- Zero R3-L1 references in resume.py, validate-ledger.py, ledger-schema.json, rung3-run-log/README.md, rung3-ci/README.md (grep, no hits). All point at R3-L3-grades.jsonl.
- My runs: resume.py status returns ORDER 55, GRADED 0, REMAINING 55, NEXT R3-001. validate-ledger.py PASS (1 row, 0 errors) with both the explicit L3 path and the default path.

### M-08. R3-089 fixture monitoring and expiry: MITIGATED

- Refresh doc rung3-run-log/r3-l3-r3-089-refresh.md updated: verified 2026-11-25 08:59, log-01..06 mtime 2026-11-24 08:59:42, hard expiry 2026-12-01 08:59, date guard "if the run has not reached R3-089 by 2026-11-30 12:00, refresh on 2026-11-30".
- thu-tu-chay.txt line 76: hard deadline 2026-12-01 08:59. du-phong.txt: R3-089 expiry 2026-12-01.
- Section 5 Gutenberg row replaced with the manual pre-position-49 check, hard gate (re-plan line 205).
- Live check by me via SSH on the laptop: find -mtime -7 in ~/rung3-goc/nd09-logs returns 6 right now. The fixture is in window.

### M-09. TB-B2 sign-off: MITIGATED on substance, provenance gap noted (see N-06)

- Sign-off file exists: improvements/r3-l3-tbb2-signoff-20261125.md. Independent re-grade from snapshots plus frozen key only, key sha256 verified by the verifier (5059f6c4... match YES), case by case with pixel-level measurements, agreement 4/4 (R3-041 PASS, R3-002 FAIL, R3-003 FAIL, R3-067 PASS), signed statement for gate G-33.
- Grade file ~/workspace/r3-l3-calibration-TBB2.md has the superseding note appended, citing the sign-off file and closing the 20:02 gap note.
- Gap: no verifier session id and no precise timestamp anywhere. The sign-off says only "Verified: 2026-11-25" and signs as "independent verifier for the R3-L3 run". No session id appears in any worktree file for this verification (the 1B/2B/TB-A verifier was session 032952f7; the TB-B2 verifier is unnamed). Substance is strong and reproducible, so this is a SHOULD-level provenance fix, not a blocker.

## SHOULD-FIX items

### S-01. Hashes re-recorded: DONE

State file line 53 records the new hashes; my recomputation matches (see B-F1).

### S-02. Deputy hourly standby: DONE

Corrected in G-42 (re-plan line 133) and section 7 (line 236): the parent verifies the deputy session hourly via subagent list and prompts it if needed; a standby subagent has no self-trigger, so there is no hourly self-confirmation entry. Section 10 G-42 box records the correction.

### S-03. G-34 re-verified with new composition: DONE, verified live by me

cron.list plus cron.status, checked 25/11 about 11:26 +07. Six r3l3 watches ENABLED with successful last runs: r3l3-agents-watch 11:20:13 (run in flight at check), r3l3-coordinator-liveness-watch 11:23:15, r3l3-zen-laptop-health 11:14:28, r3l3-runner-process-watch 11:14:04, r3l3-ledger-push-watch 10:48:17, r3l3-timeout-watch 11:23:09. mei-mochi-15m-watchdog DISABLED. r3l3-gutenberg-fixture-watch absent entirely. Meta-watch is the parent checking each watchdog hourly (G-34, re-plan line 125).

### S-04. Liveness config R3-047: DONE

rung3-ci/liveness-config.json has 31 services, valid JSON, no R3-047, no gutenberg.org.

### S-05. Execution plan line count: DONE

Worktree re-plan sources line says 577 lines. wc confirms ~/workspace/r3-l3-execution-plan-20261124.md is 577 lines. The root copy still says 565, but it is stamped SUPERSEDED. The frozen list doc is untouched.

### S-06. FCC backend decision recorded: DONE

Recorded in re-plan 0A (owner decision 25/11 09:23), the FCC roster row, the FCC lane brief section 10 carve-out (owner decision 25/11 09:23, fcc-server provider open_router, model open_router/openrouter/free), and the committed deputy dry-run record.

## NEW items found by this re-review

### N-01. BLOCKING. The briefs order drives on ws2. The pill report forbids that order for the Codex lane, and ws2 does not exist.

- The instruction: Codex brief line 92 and FCC brief line 74 both say "Drives run on ws2." Re-plan F-04(a) line 150 says the same. Re-plan 0A line 18 says "The Zen run tab lives in ws2, never ws3."
- The evidence against it: improvements/r3-l3-pill-path-check-20261125.md line 60, Finding 3: "Workspace 2 first is BiDi-only. The Codex session-driver lane must drive where Zen is visible (workspace 1) or use observe --window ADDRESS --focus. Do not instruct the Codex lane to switch to workspace 2 before driving." Attempt 2 (11:08) failed with exactly this cause, pill report line 41: "window is not visible on its monitor; switch workspace yourself or use observe --window ADDRESS --focus. Cause: my prompt told Codex to switch to workspace 2 first (the G-44 procedure, which was proven for BiDi). The pixel session driver can only see a window on the active workspace, and Zen lives on workspace 1."
- The live state, verified by me via SSH (hyprctl workspaces, about 11:28 +07): there is NO workspace 2. The workspaces are 1 (1 window: Zen, class zen, title "Chat - Muse - Zen Browser", workspace 1), special:herdrdrop, and 3 (4 windows, the 4 agents). The active workspace is 1. So the plan's assumed start state (Zen on ws2) is false right now, and no move step is documented anywhere in the committed files (no hyprctl movetoworkspace command, no "move Zen to ws2" line in any start checklist; the prepare report start item 4 says only "Confirm Zen is on ws2", which is a check, not a move).
- The guard that would save it is not in the runners' docs: re-plan F-04(e) line 150 says each lane confirms Zen is visible on its drive workspace before driving and reports to the coordinator instead of switching workspaces blindly. Neither lane brief carries that guard. The Codex runner's acked doc therefore contains the instruction that failed live 40 minutes before the ack, with no guard in the same doc.
- What must change before task 1: (1) either move the Zen run tab to ws2 before task 1 with a documented command and verify with hyprctl clients, or correct the plan and both briefs to drive where Zen is visible (ws1) and drop the ws2 order; (2) put the F-04(e) visibility guard into both lane briefs in the runners' own words (drive where Zen is visible; if Zen is not visible on your workspace, report to the coordinator, do not switch workspaces blindly); (3) re-issue the amended brief(s) and get fresh written acks under G-26. Do not start with a brief that tells the Codex lane to do the thing that already failed.

### N-02. MUST-FIX (fix in the same brief re-issue as N-01). The stuck-pill workaround never reaches the actors who must execute it.

- The defect is real and proven: pill-path-check report, FCC caveat 1. After FCC released, overlay status said visible false while three grims (10:57, 10:59, 11:01) showed the pill still at top center. Root cause in overlay.py apply_holders: the empty-holders branch sends hide only when owner is daemon, not when owner is session. Fail-safe direction (stuck ON, never OFF), but status lies about the visual state. Cleared manually at 11:03:16 with an indicator hide request.
- The workaround exists in the right place in prose: re-plan F-04(c) line 150 (verify the pill is actually gone with a grim after release, end each lane's computer-use session with finish at the end of each task, hide via an indicator hide request if stuck) and prepare report start item 7.
- It is missing where it must be executed: neither lane brief mentions grim, stuck, or finishing the computer-use session (grep: zero hits in either brief except generic "finish the task"). Section 10 "During the run" list has no grim check, no finish-session check, no latch check. The runners release the pill; the coordinator is never told in its during-run list to grim-verify after each task.
- The failure already happened once in the checks: FCC left its computer-use session running after the test (session driver PID 157786, plus Zen's quick-switcher dialog left open), and that leftover session blocked Codex attempt 1 with the session-guardian error (pill report line 33).
- Verdict on the defect itself: the workaround in content is sufficient, and the failure mode fails safe (the latch error stops the lane cleanly, no wrong drive happens, the pill stuck ON never hides a drive). So N-02 is not independently blocking. It must be fixed in the same re-issue as N-01: add the grim-after-release plus finish-session lines to both briefs and one line to the section 10 during-run list, then re-ack. A workaround that lives only in prose will be forgotten by task 3 of 55.

### N-03. MUST-FIX. The scorer addendum still lists DP-03 as the first available medium backup, plus stale tip and plan citation.

- rung3-run-log/scorer-briefs/rung3-scorer-brief-R3-L3-addendum.md line 5: "Branch: todolist-push, tip fa72d87. Execution plan: ~/workspace/r3-l3-execution-plan-20261124.md (565 lines, authoritative)." Tip fa72d87 is stale (prepare baseline 81919c0c). 565 is wrong (577). "Authoritative" contradicts the execution plan's own line 3 stamp (SUPERSEDED ON IDS, canonical sources are the state file, thu-tu-chay.txt, and the FINAL re-plan).
- Addendum line 11: "Medium backups in order: DP-03, DP-06, DP-07." DP-03 is USED pre-run. This directly contradicts du-phong.txt line 10 (DP-03 USED, no longer available) and line 13-14 (medium order 1/2 is DP-06/DP-07).
- The d4df3aa1 diff for this file changed only the 3 Invalid-section lines (46-48). These header lines predate the review and were never fixed, so the G-32 "zero mismatches" claim is false for this operative doc. G-32 evidently did not cover the addendum header.
- Operational risk is bounded: G-47 script-checks backup assignment against du-phong.txt (unused, same difficulty, not DP-01), so DP-03 would be rejected as already used. But an operative scorer doc that names a used backup first is exactly the class of contradiction G-32 exists to catch.
- What must change: line 5 tip to 81919c0c (or drop the tip), 577 lines, remove "authoritative"; line 11 to "Medium backups in order: DP-06, DP-07 (DP-03 USED pre-run for R3-047)".

### N-04. SHOULD-FIX. The bar table has no entry for 52 valid.

- Re-plan Phase 3 line 273: "54 valid needs 52, 53 needs 51". Scenario: shared cause fires (1 invalid, 2 drop, valid 53) AND one more medium invalid occurs (no medium backup left, valid 52). Two independent medium-invalid events, one of them the known timeanddate shared cause. The fallback exists (Phase 3: an owner decision is required if the shrink was not pre-declared), so the plan does not deadlock, but the coordinator would run toward an undefined bar until closure. Fix: extend the table by the evident rule (52 needs 50) or record that any shrink beyond 53 triggers an owner decision before continuing.

### N-05. SHOULD-FIX. Both lane briefs cite the superseded root re-plan as their source.

- FCC brief line 5 and Codex brief line 5: "Source of the rules in this brief: the R3-L3 re-plan ~/workspace/r3-l3-replan-final-20261124.md". That path is the root copy, stamped SUPERSEDED. Its first line redirects the reader to the worktree copy, so a reader is warned, not silently misled. Fix in the N-01 re-issue: point at improvements/r3-l3-replan-final-20261124.md in the worktree.

### N-06. SHOULD-FIX. TB-B2 sign-off has no verifier session id or timestamp.

- See M-09. Append the verifier session id and a precise timestamp to improvements/r3-l3-tbb2-signoff-20261125.md (or to the grade-file note). One line.

## Notes and non-issues (checked, not blocking)

- Single-session latch (task item c): the rule IS written clearly enough. Codex brief line 51 and FCC brief line 45 both carry the session rule (one driver at a time, session free only by /proc fd scan for cursor.lock, guardian or session-busy error means STOP and report at once, do not retry blindly). F-04(d) adds the remedy (computer-use stop). Attempt 1 proved the latch fails safe (Codex stopped, sent no actions).
- Laptop file sync verified by me via SSH sha256: thu-tu-chay.txt bf3e7550 and du-phong.txt 0cf06dda on /home/james match the worktree exactly; both lane briefs match too (FCC 0e174282, Codex cf73edfd). The "byte-identical" claim holds.
- Lane task lists match thu-tu-chay.txt exactly (FCC 28 tasks positions 1-28, Codex 27 tasks positions 29-55 including DP-03), verified programmatically.
- No em or en dashes in any file changed in d4df3aa1 (grep, zero hits). No R3-029 password value in any file (only pointers: parent-held, task brief only, re-verify before task 1 and before position 25).
- Historical files still carry old R3-047 re-check language: rung3-run-log/r3-l3-phase0-checklist-status.md lines 17, 29, 57; rung3-ci/liveness-report-20261124-175000.md lines 105-106, 120-121; evidence-requirements.json R3-047 dead entry; rung3-snapshots/R3-047-s1. All are dated 24/11 records, none is referenced by the operative docs, and the original redteam already allowed the evidence-requirements entry to stay. Do not treat them as current. No action.
- Minor id inconsistency, no operative impact: the addendum line 10 says the original TB-B was 3f3aca86, while the deputy declaration says the rejected tiebreaker B was 9d613f19. Both are unused. Possibly two successive rejected candidates. Not a verdict driver.
- What I did not verify: the 4 per-agent internal watchdogs (no direct channel from this VM, see M-04); the live FCC tmux pane and Codex exec path beyond the acks report (pane 22399 and the 11:05/11:07:34 acks are as reported, with exact ack text quoted in the acks report); the deputy session's liveness (the parent verifies it hourly per G-42). I verified the cron states, the files, the hashes, the scripts, the laptop Zen workspace, the laptop file sync, and the R3-089 fixture count myself.

## Reasoning

The coordinator's fixes are mostly real. I independently re-ran the hashes, the G-32 comparison, the ledger pair proof with my own trial rows, the resume and validate scripts, the cron states, and the laptop checks, and they hold. The R3-047 swap is executed in all six places, the deputy field is correct, the B-07 AND is live in the cron body, the R3-089 fixture is in window on the laptop right now, and the bar table for the four-task scenario was genuinely pre-declared in b061f87c, which makes the council's B-F4 decision defensible under full autonomy.

The verdict is NOT READY because the remaining defects are the same class the original redteam voted NOT READY for: required actions unexecuted, and a fix that contradicts its own evidence. B-F2's deputy re-confirmation is not a start formality, it is the written cross-check the takeover fencing depends on, and the plan's own G-24 rule disqualifies the 09:34 declaration for the 10:55 state file. N-01 is worse than a typo: the acked Codex brief orders the exact workspace switch that failed live in attempt 2, while the machine it will run on has no ws2 and Zen on ws1. N-03 shows the G-32 pass did not cover an operative doc. None of these needs a council or a redesign. The deputy writes one confirmation, the Zen move gets one documented command, two briefs get three added lines plus a re-ack, the addendum gets two corrected lines. Do that, commit it, and re-verify those four points only. Then the run can start.
