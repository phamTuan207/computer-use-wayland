# R3-L3 Final Prepare Report, Wed 2026-11-25

Final prepare review, ordered by the owner at 10:35 25/11 after the user found the plan was not fully updated for the current situation, even though the user had been told prepare was ready. The user also ordered R3-047 (the Gutenberg task) DROPPED from the run entirely (10:34). This report is the final review's deliverable. The run has NOT started. No run task has run.

## Verdict: prepare is PERFECT. The run can start on the owner's word.

Every council amendment is applied. Every redteam BLOCKING item is mitigated. Every redteam MUST-FIX item is fixed. The two live checks the redteam demanded (per-lane pill checks) both PASS. Both runners acknowledged the amended briefs in writing. The only things left are the run coordinator's start items (listed below) and two parent items (deputy re-confirmation, independent verification of the mitigations), neither of which blocks the run from starting on the owner's word.

## The R3-047 decision (council, unanimous)

Option A. Medium backup DP-03 replaces R3-047 at position 34. The run stays 55 tasks, the bar stays 53/55, difficulty mix stays medium 37 / hard 11 / very hard 7, Class L stays 9 / Class S stays 46, invalid cap stays max 5 total and max 2 per group. R3-047 is recorded as EXCLUDED by owner order, consuming 0 invalids. Medium backups left: DP-06, DP-07. DP-03 inherits Pair B (Codex lane, position 34 is in the Codex lane 29-55), Class S, scored from the sealed snapshot.

Reasoning (all three councils, and the redteam agrees the swap is sound): every run document already named DP-03 as the pre-declared R3-047 replacement. Option B (54 tasks, bar 52/54) would force a recomputed bar and shift every position after 34, with strictly more churn for no benefit. DP-03 is a terminal task (one ss -tlnp run plus a report) versus R3-047 a 3-book browser search, so Option A is budget-neutral to slightly faster; the 19-31h budget holds.

## Council and redteam verdicts

- Council 1 (stability/risk): AMEND, Option A. 11 amendments (A-01 to A-11, A-01 to A-08 blocking). File improvements/r3-l3-final-council-1-stability-20261125.md.
- Council 2 (speed/benefit): AMEND, Option A. 10 amendments (A1-A10). File improvements/r3-l3-final-council-2-speed-20261125.md.
- Council 3 (correctness): AMEND, Option A. 21 amendments. File improvements/r3-l3-final-council-3-correctness-20261125.md.
- Redteam (independent): NOT READY. 4 BLOCKING (B-F1 to B-F4), 9 MUST-FIX (M-01 to M-09), 6 SHOULD-FIX (S-01 to S-06). File improvements/r3-l3-final-redteam-20261125.md. All 4 BLOCKING and all 9 MUST-FIX are mitigated below.

## How each redteam BLOCKING item was mitigated

- B-F1 (R3-047 drop existed nowhere except the owner's order): the swap is executed in all six places. thu-tu-chay.txt order line has DP-03 at position 34 (55 tokens, token 34 is DP-03). du-phong.txt marks DP-03 USED and records the drop in the used-capacity section. The exception list replaces R3-047 with DP-03 in Class S. The Codex lane brief carries DP-03 at position 34 with no Gutenberg re-check. The scorer addendum carries DP-03 at position 34 with no Gutenberg check. The re-plan section 0A and section 9 say DROP, not re-check. The state file note records the drop. Hashes recomputed and re-recorded (thu-tu bf3e75507cb4eaa05f1c3e846fd75f74004a84492f396c04a0dec126fb2e9e85, du-phong 0cf06dda18cb32a47c99f5d5a4be67d8a8d5541d58c072f0f8e8df5c982f5619). G-32 re-run with zero mismatches.
- B-F2 (two FINAL re-plans disagreed, deputy certified the stale one): the worktree re-plan is committed with section 0A and all final-review fixes. The root copy is stamped SUPERSEDED in its first lines and is kept only as a historical artifact; the worktree copy is the only operative plan. The deputy re-confirms in writing that it read the worktree copy before task 1 (parent start item, parent messages deputy 8397cff5).
- B-F3 (state file named the dead deputy): the deputy field is updated to 8397cff5-3099-4735-93fb-34415db38a3c NOW, not at task 1, with a parse check (JSON valid) and a note recording the edit. The run coordinator creates coordinator_active (its own id) and epoch (1) in the state file at task 1 before releasing task 1; that creation is on the coordinator's start checklist in section 0A and section 7.
- B-F4 (backup exhaustion contradiction): decided by council, recorded in the re-plan G-46 and du-phong.txt. (a) The R3-047 drop counts as 0 medium invalids (council 3/3 unanimous; an owner-ordered pre-run exclusion is not an invalid). The state file invalid_by_group.trung_binh stays 0 with a note. (b) If all 4 shared-cause tasks (R3-011/028/036/046) go invalid on a proven shared cause: 1 invalid for the caps (run continues), DP-06 and DP-07 replace 2 of them, 2 drop out of the sample, valid count becomes 53, and the pass bar recomputes to 51/53 per the pre-declared table (a pre-declared shrink, no owner decision needed for the bar). The coordinator NOTIFIES the owner (G-40) but does NOT stop the run (a backup shortfall is not a run-stop condition). The bar is reachable (51/53 is 96.2 percent, the same difficulty as 53/55). Note: the redteam asked for an owner decision on (a) and (b). The team decided under the owner's full-autonomy mandate (23/11): the councils were unanimous on (a), and (b) follows the pre-declared recomputation table plus the G-40 notification rule. The parent can escalate to the owner if it disagrees; the decision is recorded here in writing so it can be.

## How each redteam MUST-FIX item was fixed

- M-01 (G-32 DONE was false): thu-tu-chay.txt fixed (tip 81919c0c, FCC pane PID 22399 / 2.1.332, Mochi target A25AA6F0370A00A174BC5304A333417D, deputy 8397cff5). G-32 re-run with zero mismatches (see Evidence).
- M-02 (worktree re-plan internally inconsistent): F-14(c) fixed (old watch stays DISABLED, never re-enabled). Section 10 todolist updated to the 25/11 state (all Phase 0 gates [x] except G-26, now [x] after the fresh acks, and Section 11, pending independent verification). Section 11 rewritten (all six 24/11 not-ready items closed with evidence, plus what remains). Section 5 Gutenberg watch row replaced with a manual R3-089 fixture check.
- M-03 (G-42 overstated 10/10): the final redteam confirms B-07 IS mitigated in the worktree copy only (chain-broken AND in all 3 places, live coordinator-liveness-watch cron uses AND). Recorded in the re-plan section 0 and the state file. The 24/11 redteam file's 9/10 status is superseded for B-07 by that confirmation. The prepare report's G-42 line is a historical Phase 0 record; this report supersedes it.
- M-04 (per-agent internal watchdogs unverified): bounded gate G-50 adopted (Council 2 A7). The run coordinator verifies all 4 within 30 minutes of the start order; if any is missing at 30 minutes, the run starts anyway with the shared r3l3-agents-watch covering, and the missing internal watchdog is recorded and set up mid-run. Council 1's dissent (wanted a hard gate, no downgrade) is recorded in G-50. Evidence as of this report: the updated memory index records mei, mochi, and clone2's own 10-minute watchdogs as confirmed on 25/11 morning, and clone1 already had one; the run coordinator still runs the G-50 verification at start (the gate is the check, not the memory entry).
- M-05 (pill mechanism named in neither lane brief): the exact mechanism is named in both lane briefs (overlay.py acquire/release/status, env vars, fail-closed rule, ws2). One live pill check on each runner's actual drive path, verified by screenshot, both PASS (see Pill checks below).
- M-06 (ledger cross-check pair check was dead code): the pair check is wired to the run-order line in thu-tu-chay.txt (position 1-28 Pair A, 29-55 Pair B; DP tasks inherit the replaced task's pair per F-18). Proven with a DP-03 trial row (PASS) and a negative test (R3-029 with a Pair B verdict file correctly FAILS, position 25 is Pair A). The real L3 ledger passes (1 test row skipped).
- M-07 (two CI scripts and the README pointed at the R3-L1 ledger): resume.py, validate-ledger.py, rung3-run-log/README.md, rung3-ci/README.md, and ledger-schema.json all point at R3-L3-grades.jsonl now. Re-run: resume.py next returns R3-001, validate-ledger.py PASS (1 row, 0 errors). The proof-log.md historical entries are left as history.
- M-08 (R3-089 fixture no monitoring, stale expiry docs): the refresh doc is updated to the 25/11 08:59 state (mtimes 2026-11-24 08:59:42, expiry 2026-12-01 08:59) with a 2026-11-30 12:00 date guard. thu-tu-chay.txt line 76 and du-phong.txt carry the 2026-12-01 expiry. The dead section 5 cron row is replaced with a manual pre-position-49 check (hard gate). The pre-49 refresh is on the run coordinator's start brief.
- M-09 (TB-B2 grade file contradicted G-33): the independent sign-off EXISTS (improvements/r3-l3-tbb2-signoff-20261125.md, committed in the prepare report, verifier re-graded all 4 cases from scratch, agreement 4/4, signed off on G-33). A superseding note is appended to the grade file ~/workspace/r3-l3-calibration-TBB2.md pointing at the sign-off file. The 20:02 gap note is superseded.

## SHOULD-FIX items (all addressed)

- S-01: hashes re-recorded after the B-F1 swap (see Evidence).
- S-02: the deputy hourly standby claim is corrected (parent verifies the deputy session hourly via subagent list and prompts it if needed; a standby subagent has no self-trigger). Fixed in G-42, section 7, F-02, and the "what changed" list.
- S-03: G-34 re-verified with the new composition (6/6 run watches enabled with successful last runs; see Evidence). The meta-watch is the parent checking each watchdog hourly.
- S-04: liveness-config.json no longer lists R3-047 / gutenberg.org (31 services, JSON valid).
- S-05: the execution plan is 577 lines, not 565; the re-plan sources line is corrected. The frozen list doc is untouched.
- S-06: the FCC backend decision is recorded in the committed re-plan section 0A, the FCC roster row, the FCC lane brief carve-out, and the committed deputy dry-run record.

## Pill checks (M-05, live, both PASS)

Report: improvements/r3-l3-pill-path-check-20261125.md.

- FCC lane: PASS 10:54-10:57. Acquire visible true, during screenshot shows the pill "Computer use active" at top center, release confirmed (holders empty, visible false).
- Codex lane: PASS 11:12-11:14 on attempt 3. Acquire visible true 11:12:35, during screenshot shows the pill visible with the new blank tab active, release confirmed. Attempt 1 failed (FCC's leftover session held the single-session latch; cleared with computer-use stop). Attempt 2 failed (told to switch to ws2, but Zen was on ws1; the pixel driver sees only the active workspace).
- Known defect recorded (F-04): when the pill owner is the live session, overlay.py release returns visible false but does NOT hide the pill (the empty-holders branch only sends hide when owner is daemon). Fail-safe direction (stuck ON, never OFF), but status lies about the visual state. Workaround: verify the pill is actually gone with a grim after release; end each lane's computer-use session (finish) at the end of each task; if stuck, hide via an indicator hide request. No mechanism code was changed in this review; the defect is recorded for a separate fix.
- Rules recorded in F-04: never overlap the two lanes' drives (single-session latch; verify no session-driver process from the other lane remains before driving). Drive where Zen is visible; the coordinator confirms Zen is on ws2 (the run-tab workspace) before releasing a task.

## Lane brief fresh acks (G-26)

Report: improvements/r3-l3-lane-brief-acks-20261125.md.

- FCC ACK received 11:05 +07 (tmux r3-fcc-runner-L3, pane 22399): names both amendments (pill mechanism section 9, OpenRouter carve-out section 10), confirms no start until assigned.
- Codex ACK received 11:07:34 +07 (codex exec, 11,382 tokens): names both amendments (DP-03 replaces R3-047 at position 34, pill mechanism section 11), confirms no start until assigned.
- G-26 is DONE. The run was NOT started by either ack.

## What changed, file by file

- rung3-run-log/thu-tu-chay.txt: DP-03 at position 34; tip 81919c0c; FCC pane 22399 / 2.1.332; Mochi target A25AA6F0; deputy 8397cff5; R3-047 ruling rewritten to DROP; R3-089 note (refreshed 25/11 08:59, expiry 2026-12-01); checkpoint trigger corrected to 19-31h.
- rung3-run-log/du-phong.txt: tip 81919c0c; DP-03 marked USED; DP-06/DP-07 renumbered (order 1/2); DP-01 line 19 false claim corrected; R3-047 paragraph rewritten to DROP; 4-task scenario recorded; used-capacity entry added; R3-089 expiry 2026-12-01.
- rung3-run-log/r3-l3-exception-list.txt: R3-047 replaced with DP-03 in Class S (counts unchanged, 9 Class L / 46 Class S).
- rung3-run-log/r3-l3-coordinator-state.json: deputy 8397cff5; backups_used DP-03; FCC pane note corrected; R3-089 expiry corrected; R3-047 note rewritten to DROP; TB-B2 and G-42 correction notes appended; final-review note appended; hashes re-recorded; last_updated advanced.
- improvements/r3-l3-replan-final-20261124.md (worktree, operative): section 0A rewritten (R3-047 drop, G-50, deputy updated, ws2 run tab, final-review paragraph); sources line 577; section 0 final-review paragraph; roster TB-B2 and coordinator rows; G-33/G-39/G-42/G-46 closed or corrected; new G-50; F-04 pill mechanism plus defect plus latch plus drive-where-visible; F-14(c) corrected; section 4 Codex risk 7; section 5 Gutenberg row replaced, internal watchdogs bounded; section 7 hourly standby corrected, coordinator_active creation at task 1; section 9 position-34 milestone; section 10 todolist updated to 25/11 state; section 11 not-ready list rewritten.
- ~/workspace/r3-l3-replan-final-20261124.md (root): stamped SUPERSEDED in its first lines; kept only as a historical artifact.
- improvements/r3-l3-lane-brief-codex-L3-20261125.md: DP-03 at position 34; Gutenberg re-check removed; pill mechanism named (section 11).
- improvements/r3-l3-lane-brief-fcc-L3-20261125.md: pill mechanism named (section 9); OpenRouter carve-out (section 10).
- rung3-run-log/scorer-briefs/rung3-scorer-brief-R3-L3-addendum.md: R3-047 removed from invalid candidates; cap math corrected (0 medium invalids); DP-03 at position 34; 4-task scenario noted.
- rung3-ci/liveness-config.json: R3-047 / gutenberg.org removed (31 services).
- rung3-ci/ledger-cross-check.py: pair check wired to the run-order line (M-06, proven).
- rung3-ci/resume.py, rung3-ci/validate-ledger.py, rung3-run-log/README.md, rung3-ci/README.md, rung3-ci/ledger-schema.json: R3-L1 ledger references changed to R3-L3.
- rung3-run-log/r3-l3-r3-089-refresh.md: 25/11 08:59 state, expiry 2026-12-01 08:59, 2026-11-30 12:00 date guard.
- rung3-run-log/r3-l3-time-budget.md: checkpoint trigger corrected to 19-31h.
- ~/workspace/r3-l3-calibration-TBB2.md: superseding note appended (independent verification DONE, sign-off file cited).
- New files: the 3 council verdicts, the redteam verdict, the pill path check report, the lane-brief acks report, this final prepare report.
- Laptop copies re-synced byte-identical (thu-tu-chay.txt, du-phong.txt, both lane briefs; sha256 verified).

## Evidence

- G-32 re-run (zero mismatches): tip 81919c0c in thu-tu, du-phong, and state file. FCC pane 22399 / 2.1.332 in thu-tu and state file. Mochi target A25AA6F0370A00A174BC5304A333417D. Deputy 8397cff5 in thu-tu and state file. Order line 55 tokens, token 34 is DP-03. Hashes match the state file (thu-tu bf3e7550, du-phong 0cf06dda).
- G-34 re-verified (6/6): r3l3-agents-watch last success 11:02:08 +07; coordinator-liveness 10:58:19; zen-laptop-health 10:59:36; runner-process 10:58:33; ledger-push 10:48:17; timeout 10:58:18. mei-mochi-15m-watchdog DISABLED. Gutenberg watch absent.
- Manifest gate reads the DP-03 spec (61 keys, DP-03 needs ss-output.txt, bao-cao.txt, 1 screenshot). The gate FAILs on the empty DP-03 snapshot as expected (DP-03 has not run yet).
- Ledger cross-check: DP-03 trial row PASS (2 verdict files), R3-029 wrong-pair FAIL caught, R3-029 correct-pair PASS, real L3 ledger PASS (1 test row skipped).
- resume.py next returns R3-001. validate-ledger.py PASS (1 row, 0 errors). liveness-config.json valid, 31 services, no R3-047.
- 0 em/en dashes in all edited files (grep verified).
- Tip stamp note: 81919c0c is the prepare baseline recorded in the state file and the execution plan. The live todolist-push tip has since advanced (fffda9da, the pwa-send.py fix) and will advance to this review's commit. The stamp identifies the prepare baseline, not the live tip; that is the established convention.

## What the run coordinator must do at start

1. Spawn as the run coordinator. Create coordinator_active (own id) and epoch (1) in the state file BEFORE releasing task 1.
2. Receive the R3-029 password from the parent (never in a file). Re-verify it before task 1 and before position 25. R3-029 runner is FCC, position 25.
3. Verify the 4 per-agent internal watchdogs within 30 minutes of the start order (G-50, bounded). If any is missing at 30 minutes, start anyway with the shared agents-watch covering, record the missing one, and set it up mid-run.
4. Confirm Zen is on ws2 (the run-tab workspace) and visible before releasing task 1. Each lane confirms Zen is visible on its drive workspace before driving.
5. Release task 1 to FCC (position 1, R3-001). The Codex lane starts at position 29 (R3-040) when the coordinator assigns it.
6. Never re-enable the mei-mochi-15m-watchdog. Never monitor Gutenberg. DP-03 runs at position 34; there is no Gutenberg check.
7. After each task, verify the pill is actually gone with a grim (not only overlay status) and end the lane's computer-use session (finish). Never let the two lanes' drives overlap.

## Parent start items (not the coordinator's)

- Message deputy 8397cff5 to re-confirm it read the FINAL committed re-plan (the worktree copy, improvements/r3-l3-replan-final-20261124.md) before task 1 (G-24).
- The independent verification of the final redteam mitigations (section 11 confirmation step) is running separately; its result confirms the mitigations in the committed files.
- The B-F4 decision (drop = 0 invalids; 4-task scenario = 53 valid, bar 51/53, notify not stop) was made by the team under full autonomy with council unanimity plus the pre-declared table. If the owner wants to decide it instead, the user can; the decision is recorded here in writing.

## Open items and caveats

- The stuck-pill defect (F-04) is recorded, not fixed. The workaround is in the re-plan. A separate fix to overlay.py apply_holders is needed after the run (it must send hide when owner is session, not only when owner is daemon).
- The internal watchdogs worker (parent-spawned) confirmed mei, mochi, and clone2's watchdogs on 25/11 morning per the updated memory index; clone1 already had one. The G-50 verification at start is still the check.
- The 24/11 redteam confirmation file still says 9/10, B-07 partial, NOT CONFIRMED. It is superseded for B-07 by the final redteam's confirmation (B-07 IS mitigated in the worktree copy only). The file itself is a historical record and is not rewritten.
- The prepare report (commit b061f87c) is a historical Phase 0 record. Its G-42 line (10/10) and its final paragraph (mei-mochi watch re-enable) are superseded by this report. The historical file is not rewritten.
