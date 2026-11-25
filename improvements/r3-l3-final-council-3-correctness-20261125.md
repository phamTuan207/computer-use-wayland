# R3-L3 Final Council 3 (Correctness) Verdict, 25/11 2026

## Standing rules

- NO OpenRouter. Never try it, never propose it. FCC's built-in OpenRouter-free backend is allowed per the owner's 25/11 decision; the ban covers only Opencode.
- NO em dash or en dash in any file. Commas, periods, or short hyphens only.
- NO personal info on GitHub (no name, address, email, phone, schedules, photos, accounts, passwords, tokens). The R3-029 password must NOT appear in any file.
- Never assume an agent's capabilities. Check or ASK THE AGENT DIRECTLY in its own chat. Every brief must state the delivery path explicitly.
- Clone1 and clone2 have NO Tailscale or SSH. Repo and web work only. Do NOT give them machine tasks.
- CDP-first observation: CLI and API first, then DOM, screenshot and vision last.
- Never close or navigate any window or tab the owner opened. Never close the 4 agents' windows in ws3.
- The pill MUST be visible on ANY agent control. Pill text is always plain "Computer use active."
- Do NOT edit MEMORY.md. Observations go to ~/memory/2026-11-25.md.
- Do NOT start the run. Do NOT run any run task.

## Verdict: AMEND

Council 3 (correctness), final review, 25/11 2026, about 10:40 +07. I read in full, live: the worktree re-plan, the stale re-plan copy, the 565-line execution plan, the prepare report, the state file, thu-tu-chay.txt, du-phong.txt, the exception list, the deputy declaration, rung3-ci/manifest-gate.py, ledger-schema.json, evidence-requirements.json, both L3 lane briefs, and the live cron list.

Nothing here is structurally wrong, so this is not REJECT. But task 1 must NOT start as the files stand, so this is not APPLY. The defects are all document-sync defects, each fixable before task 1, plus one owned decision (R3-047) that changes the run order. The single most dangerous live defect is that thu-tu-chay.txt, the canonical run order, still lists R3-047 at position 34 after the owner dropped it. The second is that the FCC L3 lane brief still carries a blanket NO OpenRouter line while FCC runs on its built-in backend under the owner's 09:23 allowance. The third is that two copies of the re-plan disagree and the deputy read the wrong one.

## Decision owned by Council 3: R3-047, Option A

DECISION: Option A. Medium backup DP-03 replaces R3-047 at position 34. The run stays 55 tasks and the bar stays 53/55.

Why A, not B. Every run document already names DP-03 as the exact replacement for R3-047 if Gutenberg stays down ("if still down, declare R3-047 INVALID plus the medium backup DP-03"). The owner order of 25/11 10:34 executes that pre-declared path early instead of waiting for the position-34 re-check. Option A keeps the designed 55-task run, the designed 53/55 bar, and every count in every document. Option B would force a recomputed 52/54 bar, a 54-task run no document was written for, medium 37 to 36, Class S 46 to 45, a rewritten ledger-completeness rule, and it would strand DP-03 unused while changing counts in the re-plan, the execution plan, thu-tu-chay.txt, du-phong.txt, the exception list, and the state file. Option B is legal (the owner decision exists, and execution plan line 131 permits recomputation by owner decision), but it is strictly more churn for no benefit.

Exact numbers under Option A:

- Run tasks: 55. Pass bar: 53/55, unchanged.
- Difficulty mix: medium 37, hard 11, very hard 7, unchanged (DP-03 is medium, like R3-047).
- Class L: 9. Class S: 46, unchanged (DP-03 is Class S, like R3-047).
- Invalid cap: max 5 total, max 2 per difficulty group, unchanged.
- Pre-run medium invalid candidates: only the R3-011, R3-028, R3-036, R3-046 shared-cause group, which counts as 1 invalid if a shared cause is proven (R3-011 per-event ruling). R3-047 is GONE, not an invalid. It consumes no invalid slot, no group slot, and no backup slot beyond its own replacement.
- Medium backups: DP-03 is CONSUMED as the position-34 replacement. Record it as used in du-phong.txt at decision time, before task 1. Remaining medium backups, in order: DP-06, then DP-07.
- Backup-depth check: the remaining medium depth is 2, and the medium group cap is 2, so the remaining backups exactly cover the maximum medium invalids the cap permits before a run stop. No shortfall is possible within the cap. If a third medium invalid were somehow declared, the run stops per the cap and the owner decides (G-40), it does not improvise.
- Ordering subtlety: because DP-03 is recorded as used before task 1, a medium invalid at positions 11, 24, or 27 (before position 34) takes DP-06, not DP-03. The coordinator must not reassign DP-03 to an earlier invalid.
- DP-03 inherits Pair B (Codex lane, position 34 is in the Codex lane, positions 29-55), Class S, scored from the sealed snapshot. No scorer or pair changes.
- Manifest gate: NO code change. Verified live, evidence-requirements.json has 61 keys (55 run tasks plus 5 backups plus the _comment key), including both DP-03 and R3-047. manifest-gate.py looks up requirements by task ID, so DP-03 at position 34 passes with no edit and the unused R3-047 entry is harmless. Ledger schema task_id pattern DP-0[123567] already admits DP-03. Record this verification in the run log as part of the G-32 pass.

## What I verified correct (no change needed)

- State file hashes, verified live by sha256sum: thu-tu-chay.txt eaffee95e281efa1b9611efe09f0b60ee1f1424dc5747b275530763e5234bdba and du-phong.txt a57b488f15850413b02918df31db6c985f19e67f7a50fd5899ef121a531a5779 both match the state file notes exactly.
- Freeze hashes match across the state file, thu-tu-chay.txt header, and the deputy declaration: H1 9b9d900, H2 5fac0eb, key JSON 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, keys.md 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60, list c1d9a220fa9a5fe57f509cd386c2b28ad466aaecdfb053ad35b5723c697d29ec, todolist-push tip 81919c0c.
- Scorer IDs match the canonical set in the state file, thu-tu-chay.txt, and the deputy declaration: 1B 4e2f52d4, 2B 2e3ae678, TB-A 97290681, TB-B2 df4defcc, Pair A scorer 2 dc7e0d0d, Mochi 70cd99d1-ecef-4d02-9f42-714d7e86ab85.
- Class L list matches the exception list exactly, 9 tasks: R3-001, R3-055, R3-074, R3-075, R3-089, R3-096, R3-078, R3-079, R3-088.
- R3-029 runner is FCC, position 25, correctly recorded in the state file notes, the worktree re-plan section 6 line 218, and the deputy declaration.
- The Gutenberg watch cron is genuinely gone: live cron.list at 25/11 10:40 shows no r3l3-gutenberg-fixture-watch, enabled or disabled. The other run watches are present and enabled (r3l3-agents-watch, r3l3-coordinator-liveness-watch, r3l3-ledger-push-watch, r3l3-runner-process-watch, r3l3-timeout-watch, r3l3-zen-laptop-health). mei-mochi-15m-watchdog is disabled, as intended.
- The stale re-plan copy's two defects are exactly as briefed: line 200 says "The runner (Codex, position 25) receives the password", and line 225 says the chain is broken on "15 minutes OR ... 30 minutes". The worktree copy has both fixed (FCC at line 218, AND in section 8).
- The pass-bar table is real: execution plan line 131 says "54 valid needs 52, 53 needs 51". The worktree re-plan section 9 repeats it. Option A does not invoke it.

## Amendments (each must be done before task 1)

1. thu-tu-chay.txt, line 8 (run order line): replace R3-047 with DP-03 at position 34. The order line must read 55 IDs with DP-03 in the position-34 slot. Recompute and record the new sha256 in the state file after the edit.
2. thu-tu-chay.txt, line 2: "Branch todolist-push tip ccd83e5" is stale. Change to 81919c0c.
3. thu-tu-chay.txt, FCC runner row: "pane PID 203375, fcc-claude 2.1.331, created 2026-11-24 17:18:33" is stale. Change to pane PID 22399, fcc-claude 2.1.332, recreated 2026-11-25 09:00:18 (prepare report G-32, state file 09:15 note).
4. thu-tu-chay.txt, Mochi scorer row: target A67A718D5E236F894F9863F48834743C is stale. The prepare report G-23 records A25AA6F0370A00A174BC5304A333417D. Correct it, and have the run coordinator re-verify it live from the CDP list at task 1 before trusting it.
5. thu-tu-chay.txt, deputy row (line 38): session 028399b1, declaration 2026-11-24 17:24:46, is stale. Change to session 8397cff5, fresh declaration 2026-11-25 09:34.
6. thu-tu-chay.txt, R3-047 ruling (line 83): rewrite. R3-047 was DROPPED by owner order 25/11 10:34, not declared invalid. DP-03 runs at position 34. There is no Gutenberg re-check before position 34. Also update the R3-089 note in the same rulings block: "Moc hien tai: 2026-11-22 19:20" is stale; the fixture was refreshed 25/11 08:59, find -mtime -7 returns exactly 6, in-window until 2026-12-01, so the 2026-11-29 19:20 hard deadline is moot (prepare report G-39). Also add one line to the R3-011, R3-028, R3-036, R3-046 ruling: they are now the ONLY pre-run medium invalid candidates, one shared-cause group.
7. du-phong.txt, line 3: tip ccd83e5 is stale. Change to 81919c0c.
8. du-phong.txt, "Cap da dung" section: record DP-03 as USED at decision time (position-34 replacement for dropped R3-047, owner order 25/11 10:34). Remaining medium order is DP-06, then DP-07.
9. du-phong.txt, line 19: "DP-01 ... va da dung cho R3-047 INVALID" is false on both halves. DP-01 was never used, and R3-047 was never declared invalid; it was dropped by owner order. Rewrite the sentence to say DP-01 is retired and was never assigned in R3-L3.
10. du-phong.txt, R3-047 paragraph (lines 37-43, "ung vien INVALID truoc khi chay thu 5"): rewrite to dropped status. R3-047 is gone, not a candidate, not an invalid. Keep the Gutenberg maintenance fact as history only.
11. du-phong.txt, R3-011, R3-028, R3-036, R3-046 paragraph: add that they are now the only pre-run medium invalid candidates and count as 1 invalid under the per-event ruling if a shared cause is proven.
12. r3-l3-exception-list.txt, Class S list (line 43): remove R3-047 from the enumeration and put DP-03 in its place at position 34. The COUNT line ("9 of 55 run tasks are Class L") stays correct and unchanged. Add a short note at the top: R3-047 dropped by owner order 25/11 10:34, replaced at position 34 by DP-03, Class S. No Class L change.
13. State file (r3-l3-coordinator-state.json): update the deputy field to 8397cff5-3099-4735-93fb-34415db38a3c at task 1, as already planned. Append a new note entry recording the owner drop of R3-047, DP-03 at position 34, DP-03 marked used, and medium backups remaining DP-06 and DP-07. Do NOT delete the old "R3-047 is a 5th pre-run INVALID CANDIDATE" note; notes are append-only history, so supersede it with the new entry. The old "todolist-push tip is now 28e2ce0" note and the old "pane PID 203375, fcc-claude 2.1.331" note are stale history superseded by the 09:15 entry and the freeze field; leave them in place, but the run coordinator must not read them as current values. Advance last_updated when the deputy field is written.
14. Re-plan canonicalization (blocking): the worktree copy (~/workspace/r3l3-run-wt/improvements/r3-l3-replan-final-20261124.md) is canonical. Sync the other copy (~/workspace/r3-l3-replan-final-20261124.md) FROM it, byte for byte, so only one text exists. The stale copy currently differs in at least: section 6 line 200 (Codex for R3-029, should be FCC), section 8 line 225 (chain-broken OR, should be AND), the section 0 summary line 24 (OR, should be AND), the section 5 watchdog table (mei-mochi-15m-watchdog row, should be r3l3-agents-watch), no section 0A at all, section 1 deputy 028399b1, and a stale section 11. After syncing, the deputy (8397cff5) re-reads the canonical copy and confirms in writing that the two deltas (R3-029 runner FCC, B-07 AND) do not change its declaration. This matters because the deputy declaration currently cites the STALE copy path as "the operative plan", which is evidence the deputy read the wrong copy.
15. Worktree re-plan, section 11 ("What is NOT ready for tomorrow"): stale and contradicts section 0A. It still lists Mei messaging broken, Mochi locked until 02:38, Clone2 reset, FCC not replied, pill unproven, and TB-B2 sign-off pending. All six closed on 25/11 morning (G-23 PASS, G-31, G-30, G-44 PROVEN, G-33 CLOSED). Rewrite section 11 to the 25/11 state, or stamp it "superseded by section 0A".
16. Worktree re-plan, Gutenberg references: section 0A bullet (line 20), section 5 watch table (line 200), section 9 milestone "Before position 34 (R3-047)" (line 258), section 10 todolist "Gutenberg before position 34" (line 309), and G-46 (line 133) must all be updated to the drop: no Gutenberg watch, no position-34 re-check, DP-03 runs at position 34, G-46 disposition table covers only R3-011, R3-028, R3-036, R3-046. The section 5 watch row for R3-047-Gutenberg-watch plus R3-089-fixture-watch must be deleted or marked removed 25/11; the R3-089 half is covered by amendment 17.
17. R3-089 watch: NO replacement R3-089-only watch is needed. The fixture was refreshed 08:59 25/11 and stays in-window until 2026-12-01, while the run ends 26/11 even at the 31h staffed ceiling. The pre-position-49 coordinator check (find -mtime -7 returns exactly 6, re-plan section 9) is sufficient as the guard, provided it stays a hard check before position 49 runs and the refresh is recorded in the run log. Do not create a new cron for a check that is already a named milestone.
18. Codex L3 lane brief (improvements/r3-l3-lane-brief-codex-L3-20261125.md): line 13 task list still includes R3-047; replace it with DP-03. Line 50 pre-milestone reminder still says Gutenberg is re-checked before position 34 and R3-047 goes invalid plus DP-03; replace with DP-03 runs at position 34, no re-check. Re-issue the brief and get Codex to acknowledge the one-line amendment in writing before task 1 (G-26 and G-30), or record the amendment as acknowledged in the run log.
19. FCC L3 lane brief (improvements/r3-l3-lane-brief-fcc-L3-20261125.md, line 79): the blanket "NO OpenRouter. Never try it, never propose it. No banned model routes of any kind." contradicts the owner decision of 25/11 09:23. Add the carve-out in the brief itself: "FCC MAY use its built-in OpenRouter-free backend (owner decision 25/11 09:23). The OpenRouter ban applies ONLY to Opencode." The re-plan records the decision clearly enough in section 0A and the FCC roster row, but the brief is the document the runner obeys, and as written it risks FCC refusing its own backend or a false flag mid-run. Re-issue or amend with FCC ack before task 1.
20. After amendments 1-19, re-run the G-32 mechanical consistency pass across all run documents (zero mismatches), recompute and record the new thu-tu-chay.txt and du-phong.txt sha256 values in the state file, re-sync the laptop copies byte-identical, and re-verify the todolist-push tip. Note du-phong.txt line 6 claims the laptop copy is canonical and the repo copy is the mirror; pick exactly one sync direction, record it, and do not leave two divergent copies again.
21. After any material state-file change from these amendments, the deputy re-confirms in writing with a timestamp after the last state-file update, so G-24 stays satisfied. A confirmation older than the last material state change does not count.

## Places still saying "5 pre-run INVALID candidates" or "at most 2 medium invalids"

- "At most 2 medium invalids" is the GROUP CAP, and it stays correct. It is not the candidate count. Do not delete it; the candidate count is what changes.
- State file note: "R3-047 is a 5th pre-run INVALID CANDIDATE" (supersede per amendment 13, do not delete).
- du-phong.txt lines 37-43: "ung vien INVALID truoc khi chay thu 5" (rewrite per amendment 10).
- thu-tu-chay.txt line 83: R3-047 invalid ruling (rewrite per amendment 6).
- Prepare report G-46: "all 5 candidates medium, all PENDING" (historical Phase 0 record; do not edit the report, record the supersession in the run log).
- Exception list line 43: R3-047 in the Class S enumeration (amendment 12).
- Execution plan line 501 (objection 42): "four pre-run invalid candidates (R3-011, R3-028, R3-036, R3-046)" is now correct again. The execution plan is stamped superseded on IDs, so no edit; noted here for the record.
- After the drop, the correct statement everywhere is: 4 pre-run invalid candidates in 1 shared-cause group, counting as 1 invalid if the shared cause is proven.

## State file inconsistencies found (beyond the known deputy field)

- Deputy field still 028399b1; fresh deputy is 8397cff5 (amendment 13).
- R3-047 candidate note superseded by the owner drop (amendment 13).
- Stale history notes remain: "todolist-push tip is now 28e2ce0" and "FCC fresh session (pane PID 203375, fcc-claude 2.1.331)". Both are superseded by the 09:15 note and the freeze field. History, not errors, but a reader must not take them as current.
- last_updated is 2026-11-25T09:15:00+07:00, which predates the deputy declaration (09:34). G-24 was satisfied because the declaration came after the last state update, but any state edit from these amendments advances last_updated and triggers a fresh deputy re-confirmation (amendment 21).
- Everything else in the state file checks out: hashes verified live, scorer IDs canonical, Class L list exact, freeze hashes consistent, R3-029 note correct, coordinator field correctly names the Phase 0 coordinator (the run coordinator is named at task 1).

## FCC backend question (fact 8)

Recorded clearly enough in the re-plan? Partly. The worktree re-plan section 0A states the owner decision of 25/11 09:23 plainly, and the FCC roster row repeats the allowance. But the stale re-plan copy has none of it, and the FCC L3 lane brief (line 79) still carries the blanket ban with no carve-out. The prepare report's "Finding that needs an owner decision" section is now superseded by the 09:23 decision; it is a historical report, so leave it, but the run log should record that the decision closed it. Amendment 19 fixes the live gap.

## Bottom line for the parent

Apply amendments 1-21, then task 1 can start. The highest-risk items if skipped are amendment 1 (R3-047 still in the run order), amendment 14 (two re-plans disagree and the deputy read the wrong one), amendment 19 (FCC brief bans the backend FCC uses), and amendment 5 (deputy still stale in thu-tu-chay.txt). None of these needs the owner except the R3-047 decision, which the owner already made; Council 3 owns the Option A choice recorded above.
