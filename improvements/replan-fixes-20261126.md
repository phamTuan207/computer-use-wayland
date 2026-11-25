# R3-L3 Re-plan Fix Record, Worker A (documents and state evidence)

Date: 2026-11-26. Role: FIX WORKER A for the R3-L3 re-plan. This file implements the document-side fixes F1, F2, F5, F6, F7, F8, F9, F10, F11 (evidence only), and F12 from the redteam verdict (replan-redteam-20261126.md, sections 1 to 4). It does not commit, does not edit the coordinator state file, does not resume the run, and messages nobody. The re-plan coordinator writes state at synthesis from the verified values below and commits centrally.

Standing rules restated for every brief that follows from this record. Ponytail for all code work: smallest complete change, reuse what exists before writing, standard library and platform before new dependencies, no unrequested abstraction or for-later code, one small test for non-trivial logic, never cut validation, security, error handling, or accessibility. Skill at ~/workspace/custom-skills/ponytail/SKILL.md. ydotool is banned. Restate the ban in every brief. Never assume it. Event-log duty and user-path fields: see F10. English only. No long dashes anywhere in this file.

Ground truth read in full for this record: replan-redteam-20261126.md, replan-council1-redistribution-20261126.md, replan-council3-operations-20261126.md, skill-scout REGISTRY.md, lauren-tan-user-testing-20261126.md, R3-L3-grades.jsonl, R3-L3-reruns.jsonl, thu-tu-chay.txt, du-phong.txt, r3-l3-coordinator-state.json (read only), r3-l3-heartbeat.log, and the approved mid-run re-plan r3-l3-replan-midrun-20261125.md. Live checks run by this worker are timed in F8, F9, and F11 with wall-clock Asia/Ho_Chi_Minh plus elapsed time.

## F1. Corrected numbers from the ledgers

### F1.1 Two independent counts, matched

Count 1 (this worker, by hand from the files). R3-L3-grades.jsonl: 29 rows, made of 21 PASS, 4 INVALID, 3 FAIL, 1 TEST. R3-L3-reruns.jsonl: 3 rows, all PASS (R3-001, R3-002, R3-003). Rule-A counted total: 21 plus 3 equals 24 PASS, 0 FAIL. The 21 PASS rows include the 3 backup PASS rows DP-06, DP-02, DP-07 and the R3-025 fresh PASS. INVALID rows: R3-011 (backup DP-06), R3-022 (backup DP-02), R3-024 (backup DP-07), R3-026 (no replacement, dropped). Last graded: R3-025 fresh PASS.

Count 2 (script count, python3 json parse of every line, run 2026-11-26 about 05:43 Asia/Ho_Chi_Minh, elapsed under 1 second). Same result: grades 29 rows (PASS 21, INVALID 4, FAIL 3, TEST 1), re-runs 3 rows (PASS 3). The script also extracted the frozen order from thu-tu-chay.txt (55 tokens), subtracted the 28 distinct graded task IDs (25 frozen positions plus 3 DP backups), and got 30 remaining frozen positions. Both counts match. The heartbeat tail agrees (last line: graded 31, pass 24, fail 3, invalid 4, rule-A 24 PASS and 0 FAIL).

### F1.2 Corrected numbers table

| Quantity | Corrected value | Source |
| --- | --- | --- |
| Banked rule-A PASS | 24 | 21 PASS rows plus 3 re-run PASS rows |
| Banked rule-A FAIL | 0 | 3 original FAIL rows all superseded by PASS re-runs |
| INVALID events used | 4 of 5 | R3-011, R3-022, R3-024, R3-026 |
| Medium (trung binh) invalids | 3, over per-group cap 2 by 1 | R3-011, R3-024, R3-026 (see F11) |
| Hard (kho) invalids | 1 of 2 | R3-022 (see F11) |
| Invalid slots left | 1 (the next event is number 5, the cap) | 5 minus 4 |
| Remaining original-set positions | 30 | 55 frozen minus 25 graded positions |
| Remaining with task 56 | 31 tasks to run and score | 30 plus task 56 |
| Valid original set after R3-026 drop | 54 | 55 minus 1 dropped |
| Bar, original set (N minus 2) | 52 of 54 | Coordinator decision, F2 |
| Need, original set | 28 more PASS from 30 | 52 minus 24 banked |
| Slack, original set | 2 fails | 30 minus 28 |
| Valid with task 56 | 55 | 54 plus task 56 |
| Bar with task 56 (N minus 2) | 53 of 55 | Coordinator decision, F2 |
| Need with task 56 | 29 more PASS from 31 | 53 minus 24 banked |
| Slack with task 56 | 2 fails | 31 minus 29 |
| Superseded bars (closure, both ways) | 53 of 55 original, 54 of 56 with task 56 | Stated as superseded by the drop, never hidden |
| Backups left | DP-05 only, very hard tier | DP-03 at position 34, DP-06, DP-02, DP-07 used |

Remaining 30 in frozen order: R3-027, R3-028, R3-029, R3-035, R3-036, R3-037, R3-045, R3-046, DP-03, R3-049, R3-055, R3-067, R3-072, R3-074, R3-075, R3-076, R3-078, R3-079, R3-082, R3-083, R3-085, R3-086, R3-088, R3-089, R3-093, R3-094, R3-096, R3-098, R3-099, R3-100. Plus task 56 last.

Cascade figures (corrected). If R3-028, R3-036, and R3-046 all grade INVALID on the proven timeanddate shared cause: cap events add 0 (already counted once for R3-011), each task drops with no backup. Valid original set: 54 minus 3 equals 51. Bar N minus 2 equals 49 of 51. Need: 49 minus 24 equals 25 more PASS from 27 remaining valid positions (30 minus 3), slack 2. With task 56: valid 52, bar 50 of 52, need 26 from 29, slack 2. The B-F4 trigger at valid 53 is crossed on the first of these drops (54 to 53). Each drop recomputes N minus 2 and notifies via parent. The invented council-1 floor (pause and ask below valid 50) is replaced by the redteam guardrail: at valid 50, the coordinator pauses releases and reconvenes council plus redteam under the delegated gate, with no owner escalation unless the team cannot agree. If rule-A fails reach 3, the bar is unreachable under any drop scenario; the coordinator notifies via parent and the team decides continue-for-data or stop, recorded before further drives. Continuing past an unreachable bar is not pre-authorized.

### F1.3 Every stale council-1 and council-3 line

Council-1, file replan-council1-redistribution-20261126.md:

| Location | Stale value | Corrected value |
| --- | --- | --- |
| Section 2, heartbeat bullet | graded 29, pass 23, fail 3, invalid 3; rule-A 23 PASS and 0 FAIL; 3 invalids R3-011, R3-022, R3-024 | Ledger rows 29 grades (21 PASS, 4 INVALID, 3 FAIL, 1 TEST) plus 3 re-run PASS; rule-A 24 PASS and 0 FAIL; 4 invalids including R3-026 dropped |
| Section 2, in-flight bullet (R3-026) | Pair A scoring in progress; R3-026 is INVALID candidate number 4 | R3-026 graded INVALID, decided 2026-11-26T04:48:26+07:00, scorers A1 Mochi 70cd99d1 and A2 582ecc45, no replacement, dropped (du-phong.txt last line) |
| Section 2, in-flight bullet (R3-025) | Fresh drive running, deadline about 05:09, one ledger row to come | R3-025 fresh graded PASS (A1 plus A2 PASS), ledger row filed, in-flight complete, unscored queue empty |
| Section 2, bar-math bullet | Need 30 of 32 remaining original positions counting in-flight, slack 2; with task 56 need 31 of 33 | Need 28 more PASS from 30 remaining original positions, slack 2; with task 56 need 29 from 31, slack 2 (bars 52 of 54 and 53 of 55) |
| Section 2, invalid-budget bullet | 3 of 5 used; medium 2 of 2 at cap; hard 1 of 2 | 4 of 5 used; medium 3 over cap 2; hard 1 of 2; one slot left |
| Section 3, tiebreaker reserve paragraph | No tiebreaker has been needed in the 29 graded tasks to date | False. Two tiebreakers already used (see F6): R3-021 in the grades ledger and R3-002 in the re-runs ledger, each scorer1 PASS, scorer2 FAIL, scorer3 PASS |
| Section 3, INVALID analyses paragraph | R3-026 cause and cap ruling (in-flight scoring, analysis still open) | R3-026 analysis DONE (see F5). The 2 WU is charged as completed, not open work |
| Section 7, R3-026 cap impact | Cap impact if graded INVALID: total 4 of 5, medium 3 over cap 2 | Confirmed as graded. Wording changes from conditional to fact; numbers hold |
| Section 7, bar-math impact | Passes banked 23; remaining valid positions R3-025 fresh plus 30 equals 31; need 29 more PASS; with task 56 need 30 from 32 | Banked 24; remaining 30; need 28 from 30; with task 56 need 29 from 31. Bars 52 of 54 and 53 of 55 hold |
| Section 7, cascade paragraph | If all 3 drop after R3-026: need 26 more PASS from 28; with task 56 need 27 from 29 | Need 25 from 27; with task 56 need 26 from 29 (valid 51 and 52, bars 49 and 50) |
| Section 8, Phase 0 | Finish R3-026 scoring and R3-025 fresh drive, seal, score, one ledger row | Done. Phase 0 is complete at the pause point; nothing remains in flight |
| Section 11, step 6 | Record recomputed bars on resume approval | Bars to record are 52 of 54 and 53 of 55 beside superseded 53 of 55 and 54 of 56. Recording the section 7 stale need figures would write wrong bars |

Council-3, file replan-council3-operations-20261126.md:

| Location | Stale value | Corrected value |
| --- | --- | --- |
| Verdict summary point 3 | Invalid budget may reach 4 of 5 when R3-026 is graded | Invalid budget is 4 of 5. R3-026 graded INVALID and dropped |
| Section 3.0, run state | 23 PASS, 3 INVALID (each replaced by a backup PASS); rule-A 23 PASS, 0 FAIL; invalid budget 3 of 5; medium 2 of 2 at cap | 24 rule-A PASS (21 PASS rows plus 3 re-run PASS), 4 INVALID (3 replaced, R3-026 dropped with no replacement), 0 rule-A FAIL; budget 4 of 5; medium 3 over cap 2 |
| Section 3.0, in-flight paragraph | R3-026 INVALID candidate in Pair A scoring; if INVALID, count becomes 4 of 5; R3-025 fresh drive in flight, deadline about 05:09 | Both complete. R3-026 INVALID filed; R3-025 fresh PASS filed; unscored queue empty; pause point reached |
| Section 3.0, bar line | Bar 53 of 55 original, 54 of 56 with task 56 | Superseded by the drop. Current bars 52 of 54 and 53 of 55; original bars reported at closure as superseded |
| Section 3.1, R3-026 watch item | Position 22, scoring now; if INVALID, invalids become 4 of 5 and owner notified; backup follows difficulty group and DP-05 only if group matches | Scored INVALID, dropped, no backup (medium, no medium backup remains; DP-05 is very hard and does not replace it). Notification point already incurred (see F2) |
| Section 3.3, Phase 0 | R3-025 fresh drive completes; R3-026 Pair A scoring completes | Done. Phase 0 closed at the pause point |
| Section 3.5, invalid budget risk | Budget is 3 of 5 now, possibly 4 of 5 after R3-026 | Budget is 4 of 5. One slot left. Medium cap already breached |
| Section 3.5, owner-notification summary | Invalid 4 fires if R3-026 grades INVALID | Invalid 4 already incurred and recorded. Remaining points listed in F2 |
| Section 4, open items | R3-026 grade and the invalid-4 notification if it lands | Closed. Grade filed, drop recorded in du-phong.txt |

Lines that hold and must be kept: council-1 Pair A and Pair B fixed tables and counts (mochi 15, clone2 15, clone1 7, fresh 25, total 62), Class L remaining 9 including task 56, DP-05 reserved for very hard only, no retroactive change to filed scoring outcomes, task 56 last with both-ways closure. Council-3 watch-item handling for R3-028, R3-036, R3-046 shared-cause counting, R3-079 coupled reset, R3-089 fixture, and R3-100 port (hardened in F12).

## F2. Gate decision record

These decisions are recorded here under the delegated team gate. They are not re-litigated in this record. The coordinator writes them into the state file at synthesis with timestamps, before R3-027 releases.

### F2.1 Resume gate

The resume gate is the delegated team gate set by the owner at 04:53 on 2026-11-26: council plus redteam unanimously agree tools are sufficient (including the Cloudflare fix proven live) and the plan is good enough. The coordinator issues the resume word when that agreement exists. No owner approval is required to resume, and no draft line may require owner approval to resume. Every line in council-1 sections 1, 8 (Phase 3), 10 (items 1 and 2), and 11 (step 5), and in council-3 verdict summary point 4, section 3.3 (Phases 2 and 3), section 3.5, and section 4, that makes resume, ratio pinning, or installs wait for explicit owner approval is superseded by this record. The council-3 internal contradiction (summary says installs run only after the owner gate, section 3.3 orders Phase 2 installs before Phase 3 owner approval) is resolved the same way: installs and proofs run under the team gate in F9 order, and the team gate decides resume. Owner notification points (F2.4) remain notifications. They are not approval gates and they do not block the team gate, except where a point is also a team stop condition (valid-50 reconvene, bar unreachable, invalid event 6).

### F2.2 Ratio reading decision

Decision: clone1 weight 50, mochi weight 85, clone2 weight 100, mei weight 100, total weight 335. Reason: the plain reading of the owner order. The order says clone1 gets 50 percent fewer tasks than the other three, and mochi gets 15 percent fewer than clone2 and mei. The full-share members named in the order are clone2 and mei, so half of a full share is 50 against 100. The alternative reading (half of the average of the other three, 47.5) is rejected because it makes clone1 half of a blended figure that includes mochi at 85, which the order never names as a share unit.

Applied to the Four-Muse pool of 90 WU (pool definition in council-1 sections 3 and 4, kept): ideal quotas are clone2 26.87 WU, mei 26.87 WU, mochi 22.84 WU, clone1 13.43 WU. Assigned quotas are clone2 27, mei 27, mochi 23, clone1 13. Every assigned quota is within one whole unit of its ideal (largest gap: clone1, 0.43 WU). Checks: mochi 23 divided by 27 equals 85.2 percent (target 85). Clone1 13 divided by 27 equals 48.1 percent (target 50, gap 0.43 WU, whole-unit rounding). The coordinator tracks actual WU and rebalances at each milestone (after every 8 graded tasks) by moving the next prep or review unit to the person furthest below target. No person is assigned a half task to hit a decimal.

Task-count equivalent, shown beside WU because the owner order says tasks. Scoring assignments (tasks scored): mochi 15, clone2 15, clone1 7, fresh 25, mei 0, total 62. Tasks touched in the post-resume pool (scoring plus prep plus review audits plus activated INVALID analysis slots, from the F5 table): mei 27 touches at 27 WU (12 prep, 9 review, 6 analysis slots, 0 scoring), clone2 27 touches at 27 WU (15 scoring, 6 prep, 2 review, 4 analysis slots), mochi 23 touches at 23 WU (15 scoring, 4 prep, 4 review), clone1 13 touches at 13 WU (7 scoring, 3 prep, 1 review, 2 analysis slots). One WU equals one touch in this design except tiebreakers (2 WU, standby pool). The divergence the redteam flagged is real and is stated plainly: mei reaches a full share with zero scored tasks because she is disqualified from scoring (list and key author). The ratios govern the movable WU pool. They do not govern raw scored-task counts, and closure reports both figures so the owner can see the full picture. The 90 and 56 pool split is kept with this derivation recorded: fresh sessions hold 25 scoring assignments for parallelism, independence, and context limits (council-1 section 4 reasons, kept), the standby pool holds 6 tiebreaker WU, the coordinator holds 6 live-only prep units (SSH required, the four Muses have no SSH) and 19 review units (VM-local audits before the repo pull, ledger write, closure units). The remaining 90 WU is the Four-Muse pool the ratios govern.

### F2.3 Cap decision

Decision: drop R3-026, recompute to N minus 2, notify via parent, do not stop. Bars: 52 of 54 original set, 53 of 55 with task 56, slack 2 fails in both countings. Banked: 24 PASS rule-A. Need: 28 more PASS from 30 remaining original positions, 29 from 31 with task 56. Medium invalid count 3 is over the per-group cap of 2, stated plainly. Total invalid count 4 of 5, one slot left. Closure counts both ways: recomputed bars (52 of 54, 53 of 55) beside the superseded bars (53 of 55, 54 of 56). Original FAIL rows and the rule-A supersede stay exactly as filed. Guardrails: the next invalid event is number 5, the cap; any sixth event needs a new recorded team decision before further releases. R3-028, R3-036, R3-046 shared-cause drops add zero cap events only with browser evidence per task plus scorer-2 confirmation; each drop recomputes N minus 2 and notifies. At valid 50 the coordinator pauses releases and reconvenes council plus redteam under the delegated gate. If rule-A fails reach 3, the bar is unreachable; the coordinator notifies via parent and the team decides continue-for-data or stop before further drives. DP-05 stays reserved for very hard invalids only. Cross-site Cloudflare blocks are not merged into one event.

### F2.4 Owner notification points (notify via parent, do not wait for approval)

1. Invalid event 5 (cap reached). Any sixth event needs a new recorded team decision before further releases.
2. Each further drop (valid count falls, bar recomputes), including each shared-cause drop among R3-028, R3-036, R3-046, and the B-F4 crossing at valid 53.
3. R3-029 password timing: the parent re-verifies the credential with the owner before position 25 arrives (F7 flow). The coordinator notifies the parent as the position approaches.
4. Task 56 pin and essential ambiguity: if pinned or essential state cannot be determined from the preserved sessionstore, ask the owner to confirm before position 56. Do not guess the setup.
5. Valid-50 reconvene trigger: at valid 50, releases pause and council plus redteam reconvene. The owner is notified that the trigger fired; the team decides under the delegated gate unless it cannot agree.
6. Bar unreachable (3 rule-A fails), DP-05 use or exhaustion, and shared-cause proof filed for R3-028, R3-036, R3-046 (with proof file path), as in council-1 section 7 and council-3 section 3.5.

Already incurred and recorded, not pending: invalid 4 (R3-026, medium breach, drop, recomputed bars), invalids 3 and earlier, and the resume-gate delegation itself.

## F5. Per-task prep, INVALID analysis, and review tables

### F5.1 How to read the table

Scoring pairs are council-1 section 5, unchanged. Prep owner is the one person who runs the pre-run check for that task (1 WU). INVALID analyst pair is lead plus second checker; the pair acts only if the task grades INVALID. Review auditor is the one person who audits the verdict pair for that task (1 WU). Coordinator-live prep means the coordinator or a Muse driving subagent with SSH runs the live fixture check; the four Muses have no SSH and cannot take these units. Fresh means a fresh independent session spawned per task under the existing brief plus declaration pattern.

Hard disjointness rule, checked per row below: no scorer preps, analyzes, or reviews key content for a task they score. Two further separations hold per row: the review auditor is never the prep owner for that task, and for the three named INVALID candidates (R3-028, R3-036, R3-046) the review auditor is never a member of the analyst pair. For on-call pairs on other tasks, the pair is standby only; if an on-call analysis activates, the review auditor for that task swaps to the coordinator before the audit, and the swap is recorded. Prep-to-analysis continuity is allowed for non-scorers (the prep liveness knowledge is the point of the analysis) and never touches scoring, because prep owners and analysts below never score the tasks they prep or analyze.

### F5.2 The 31-task table

| Task | Scorers (1 plus 2) | Prep owner | INVALID analyst pair (lead plus second) | Review auditor |
| --- | --- | --- | --- | --- |
| R3-027 | Mochi plus Clone2 | Mei | Mei plus Clone1 (on-call) | Coordinator |
| R3-028 | Mochi plus Fresh | Mei | Mei plus Clone2 (named) | Coordinator |
| R3-029 | Mochi plus Clone2 | Mei | Mei plus Clone1 (on-call) | Coordinator |
| R3-035 | Mochi plus Clone2 | Mei | Mei plus Clone1 (on-call) | Coordinator |
| R3-036 | Mochi plus Fresh | Mei | Clone2 plus Mei (named) | Coordinator |
| R3-037 | Mochi plus Clone1 | Mei | Mei plus Clone2 (on-call) | Clone2 |
| R3-045 | Clone2 plus Fresh | Mei | Mei plus Clone1 (on-call) | Mochi |
| R3-046 | Fresh plus Fresh | Mei | Clone2 plus Mei (named) | Clone1 |
| DP-03 | Clone2 plus Fresh | Mei | Mei plus Clone1 (on-call) | Mochi |
| R3-049 | Mochi plus Fresh | Clone2 | Mei plus Clone2 (on-call) | Mei |
| R3-055 | Mochi plus Clone2 | Coordinator-live | Mei plus Clone1 (on-call) | Mei |
| R3-067 | Mochi plus Fresh | Clone2 | Mei plus Clone2 (on-call) | Mei |
| R3-072 | Fresh plus Clone1 | Mei | Mei plus Clone2 (on-call) | Mochi |
| R3-074 | Clone2 plus Fresh | Coordinator-live | Mei plus Clone1 (on-call) | Mei |
| R3-075 | Mochi plus Clone2 | Coordinator-live | Mei plus Clone1 (on-call) | Mei |
| R3-076 | Fresh plus Clone1 | Mei | Mei plus Clone2 (on-call) | Mochi |
| R3-078 | Clone2 plus Fresh | Mei | Mei plus Clone1 (on-call) | Coordinator |
| R3-079 | Fresh plus Clone2 | Mochi | Mei plus Clone1 (on-call) | Mei |
| R3-082 | Clone1 plus Fresh | Clone2 | Mei plus Clone2 (on-call) | Coordinator |
| R3-083 | Fresh plus Clone1 | Clone2 | Mei plus Clone2 (on-call) | Coordinator |
| R3-085 | Mochi plus Fresh | Clone2 | Mei plus Clone2 (on-call) | Coordinator |
| R3-086 | Fresh plus Fresh | Mochi | Mei plus Clone2 (on-call) | Clone2 |
| R3-088 | Clone2 plus Fresh | Mochi | Mei plus Clone1 (on-call) | Coordinator |
| R3-089 | Mochi plus Clone2 | Coordinator-live | Mei plus Clone1 (on-call) | Mei |
| R3-093 | Fresh plus Clone1 | Clone2 | Mei plus Clone2 (on-call) | Coordinator |
| R3-094 | Clone1 plus Fresh | Mochi | Mei plus Clone2 (on-call) | Coordinator |
| R3-096 | Mochi plus Fresh | Coordinator-live | Mei plus Clone2 (on-call) | Mei |
| R3-098 | Fresh plus Clone2 | Clone1 | Mei plus Clone1 (on-call) | Coordinator |
| R3-099 | Clone2 plus Fresh | Clone1 | Mei plus Clone1 (on-call) | Coordinator |
| R3-100 | Mochi plus Fresh | Clone1 | Mei plus Clone2 (on-call) | Coordinator |
| Task 56 | Mochi plus Clone2 | Coordinator-live | Mei plus Clone1 (on-call) | Mei |

Counts from the table. Prep: mei 12, clone2 6, mochi 4, clone1 3, coordinator-live 6. Total 31. Review audits: mei 9, mochi 4, clone2 2, clone1 1, coordinator 15. Total 31 audits, plus 4 coordinator closure units equals the council-1 review pool of 35 (coordinator total 19). Scoring: mochi 15, clone2 15, clone1 7, fresh 25. Total 62. All three count sets match council-1 section 4.

Disjointness proof, spot checks the coordinator re-runs on every row before release. R3-028: scorers Mochi and Fresh; prep Mei, analysts Mei and Clone2, reviewer Coordinator. No overlap. R3-036: scorers Mochi and Fresh; prep Mei, analysts Clone2 and Mei, reviewer Coordinator. No overlap. R3-046: scorers Fresh and Fresh; prep Mei, analysts Clone2 and Mei, reviewer Clone1. No overlap. R3-055: scorers Mochi and Clone2; prep Coordinator-live, reviewer Mei. No overlap. Task 56: scorers Mochi and Clone2; prep Coordinator-live, reviewer Mei, VM-local grading path in F8. No overlap. Mochi preps only R3-079, R3-086, R3-088, R3-094, none of which she scores. Clone2 preps only R3-049, R3-067, R3-082, R3-083, R3-085, R3-093, none of which he scores. Clone1 preps only R3-098, R3-099, R3-100, none of which he scores (R3-098 scorer 2 is Clone2, R3-099 scorer 1 is Clone2, R3-100 scorer 1 is Mochi). Mei scores zero, so her 12 prep units and 9 review units cannot clash with scoring. Any later reassignment re-runs this check before release, and the check result is recorded in the state file.

### F5.3 INVALID analyst totals fixed

Unit definition, corrected so table and text agree: one INVALID analysis equals 2 WU of pair effort, split lead 1 WU (cause proof draft: browser evidence review, difficulty group check, backup mapping, cap accounting) plus second 1 WU (independent check of the same proof). Six analyses equal 12 WU. Assignments:

| Analysis | Lead (1 WU) | Second (1 WU) | State |
| --- | --- | --- | --- |
| R3-026 | Mei | Clone2 | DONE (F5.4) |
| R3-028 | Mei | Clone2 | Open, named candidate |
| R3-036 | Clone2 | Mei | Open, named candidate |
| R3-046 | Clone2 | Mei | Open, named candidate |
| Unplanned A | Mei | Clone1 | Reserve |
| Unplanned B | Clone1 | Mei | Reserve |

Totals: mei 6 slots (6 WU), clone2 4 slots (4 WU), clone1 2 slots (2 WU). This matches the council-1 section 4 table exactly. Council-1 section 7 text (mei lead plus clone2 second on four named tasks, mei 4 and clone2 4 before unplanned work) is corrected: on the four named tasks the split is mei lead on R3-026 and R3-028, clone2 lead on R3-036 and R3-046, with the other as second each time. If R3-028, R3-036, and R3-046 share one proven cause, the cause proof is written once and confirmed twice; WU still counts per task for cap accounting, and the shared proof file path is recorded so the work is not triple written. Each extra analysis beyond the two unplanned slots is 2 WU charged to mei lead plus clone2 or clone1 second, excluding scorers of that task, and quotas rebalance at the next milestone. Cause proof standard is browser evidence (screenshot, Ray ID where present, wait log) plus scorer-2 confirmation. Curl 403 alone is never proof.

### F5.4 R3-026 analysis disposition: DONE

Evidence from du-phong.txt, last line: R3-026 to NO REPLACEMENT (invalid: Cloudflare bot check on coolors.co; no medium backup remains, DP-06 and DP-07 used, DP-03 is position 34 in the frozen 55; task drops from denominator; scorers A1 Mochi 70cd99d1, A2 582ecc45; decided 2026-11-26T04:48:26+07:00). The grades ledger row for R3-026 records the same: bot-check page, Ray ID in ket-qua.txt, no palette generated, medium invalid count 3 over the per-group cap of 2, backup_task null. The cause, difficulty group (medium, list line 452, do kho trung binh), backup mapping (none, drop), and cap accounting are all recorded. The analysis is done. Its 2 WU (mei 1 plus clone2 1) is charged as completed work inside the 90 WU pool, not as open work. Open analyses remaining: R3-028, R3-036, R3-046, plus 2 unplanned slots. Mei tranche 1 is corrected accordingly: R3-026 analysis lead is complete, not a tranche-1 assignment.

### F5.5 Mei tally source and dead session supervision removed

Mei does not read ledgers or snapshots (council-1 section 5, kept). Her tally therefore comes from coordinator reports only. Source, named: the coordinator milestone report filed at rung3-run-log/ after every 8 graded tasks (WU actuals, invalid counters, bar reachability), plus the per-task report file rows the coordinator publishes. Mei tallies from those reports. She does not open R3-L3-grades.jsonl, R3-L3-reruns.jsonl, or any snapshot. If a coordinator report is missing a figure mei needs, she asks the coordinator; she does not read the ledger herself.

Supervision of scorer-2 session dc7e0d0d is removed. That session is a completed calibration session that cannot resume, as the state file records (calibration sessions dc7e0d0d, 4e2f52d4, 2e3ae678 completed and cannot resume; run sessions are fresh spawns). Replacement: none. No supervision line is needed, because run scorer-2 sessions are fresh spawns briefed identically per task and audited by the coordinator before any ledger write. Council-1 section 4 tranche 1 and section 5 lines naming dc7e0d0d supervision are deleted by this record.

### F5.6 Quota honesty: in-flight scoring and calibration

Ratios apply to post-resume assignments (the 31-task pool above). Total-run load differs, stated plainly. In-flight scoring already done at the pause: mochi scored R3-025 fresh (scorer 1) and R3-026 (scorer 1, daemon run 231). Those are 2 scoring tasks outside the 31-task pool. They count as load for scheduling and are reported in closure load figures, but they do not change the post-resume quotas (mochi 23 WU post-resume, 25 scoring-plus-pool touches across the whole run when the 2 in-flight scorings are added). Calibration work for clone1 and clone2 (F6) is a gate, not quota credit, for both candidates; the verifier work is also outside the pool. Closure reports three load views: post-resume WU against targets, in-flight scorings, and calibration attempts. No view is hidden inside another.

## F6. Held-out calibration with a calibrated verifier

### F6.1 Why the old set is retired

The council-1 calibration set (R3-041 PASS, R3-002 FAIL, R3-003 FAIL, R3-067 PASS) is retired for clone1 and clone2. Every verdict is on file in the repo (calibration grade files and ledger rows), so 4 of 4 on it proves reading, not judgment. R3-067 is also a future run task at position 37 with its run snapshot still to be driven; calibrating on it exposes its key before the run. The old set stays valid as history for TB-A, 1B, 2B, and TB-B2. It is not reused for new candidates.

### F6.2 New held-out set: sealing procedure (no qualifying unsealed set exists)

This worker checked for already-graded snapshots whose grade files are absent from the repo. None qualify: every graded task in this run has a ledger row and verdict files on file, and every calibration case has a grade file on file. The sealing procedure therefore applies.

Procedure. The verifier (F6.3) selects 4 cases from already-graded snapshots of this run, excluding every future run task and its key (no R3-027 to R3-100 remaining task, no DP-03, no task 56, and in particular no R3-067). Eligible pool: graded PASS snapshots, graded FAIL snapshots (original R3-001, R3-002, R3-003 originals and their re-runs), and graded INVALID snapshots (R3-011, R3-022, R3-024, R3-026), so the set can include at least one PASS, one FAIL, and one INVALID judgment. The verifier writes the 4 verdicts, snapshot hashes, and key-section hashes into one sealed verdict file held outside candidate-readable paths (verifier workspace only, never committed to todolist-push before calibration closes). Candidates receive an allowlist per case: the sealed snapshot files for that case plus the frozen key section for that task only. No grade-file access, no ledger access, no other-scorer verdict, no live evidence dir. The coordinator enforces the allowlist and records file hashes in each candidate grade file, same as real scoring. Candidates grade blind, 4 cases each, one verdict json plus one grade markdown per case, with independence declarations. Pass bar: 4 of 4 agreement with the sealed verdicts. One re-calibration on a second sealed set is allowed during the pause. A candidate under 4 of 4 twice does not grade real tasks; fresh sessions fill that quota and ratios rebalance at the next milestone, recorded in the state file.

Contamination guard: any case whose snapshot a candidate already scored, prepped, or analyzed in this run is excluded for that candidate. Clone1 and clone2 have no run scoring history yet, but the coordinator checks the prep and analysis logs before sealing. The sealed file is opened only after both candidates file all 4 grades. The verifier sign-off (F6.3) names cases, hashes, and agreement per candidate.

### F6.3 Verifier

Verifier path, in order of preference. First choice: TB-A (session 97290681, calibration 4 of 4, APPROVED, independent verifier confirmed) or TB-B2 (session df4defcc, calibration 4 of 4, APPROVED), each with sign-off on file: TB-B2 independent sign-off at improvements/r3-l3-tbb2-signoff-20261125.md (verifier re-graded all 4 cases from scratch, agreement 4 of 4, G-33 signed off; the earlier coordinator-only gap note in the state file is superseded by that sign-off). Calibration grade files on disk, verified by this worker 2026-11-26: ~/workspace/r3-l3-calibration-1B.md, r3-l3-calibration-2B.md, r3-l3-calibration-TBA.md, r3-l3-calibration-TBB2.md, r3-l3-calibration-VERIFICATION.md. Because calibration sessions cannot resume, the verifier runs as a fresh spawn briefed as TB-A or TB-B2 with the same brief plus addendum, spawned on demand with the new session ID recorded. If neither TB-A nor TB-B2 lineage is available, the verifier must itself calibrate 4 of 4 on a separate sealed set (built by the coordinator under F6.2, disjoint from the candidate set) before verifying anyone. An uncalibrated fresh session never verifies. The verifier is never mei, never mochi, never the coordinator alone, and never the candidate. The verifier re-grades all 4 candidate cases from scratch and signs off in a file naming cases, hashes, and agreement.

### F6.4 Tiebreaker history corrected and reserve re-based

Corrected history. Council-1 section 3 (no tiebreaker needed in 29 graded tasks) is false. Script recount of scorer verdicts across grades plus re-runs (2026-11-26, this worker) found exactly 2 disagreements, each resolved by a third scorer: R3-021 (grades ledger: scorer1 PASS, scorer2 FAIL, scorer3 PASS, final PASS) and R3-002 re-run (re-runs ledger: scorer1 PASS, scorer2 FAIL, scorer3 PASS, final PASS). At least 2 tiebreakers have already been used. All other 30 graded rows (29 grades plus 3 re-runs, minus the TEST row and minus these 2) show scorer agreement.

Re-based reserve. Observed disagreement rate: 2 in 31 graded tasks (about 6.5 percent). For 31 remaining tasks, expected disagreements: about 2. Reserve of 3 tiebreakers (6 WU, standby pool TB-A and TB-B2) covers the expectation plus one spare and is kept. If the reserve is exhausted, fresh tiebreaker sessions absorb overflow under the same calibration gate (4 of 4, independent verification) before grading, and the coordinator records the overrun. Ratios are not re-litigated per tiebreaker. The tiebreaker must not have scored, prepped, or analyzed the task. The tiebreaker grade is final, and the ledger records all three verdicts.

## F7. Driving lanes settled in one table

### F7.1 Evidence hierarchy and the decision

Hierarchy applied: owner-approved re-plan (r3-l3-replan-midrun-20261125.md, epoch 7, 2026-11-25) first, then state-file corrections, then council drafts, with the frozen order file thu-tu-chay.txt governing order and positions. The approved re-plan section 2 assigns positions 4 to 28 as Muse 22 plus FCC 3, naming FCC tasks explicitly (R3-014 position 13, R3-027 position 23, R3-037 position 28) and Muse tasks explicitly, including R3-028 (position 24), R3-029 (position 25, Claude-run, credential parent-held), R3-035 (position 26), and R3-036 (position 27). Section 2.3 keeps positions 32 to 55 on Codex (24 tasks). Council-1 section 6 matches the approved re-plan for the remaining tasks. Council-3 section 3.1 (R3-029 on the FCC lane) and the Phase 0 state note (R3-029 runner corrected to FCC, correcting a re-plan draft that named Codex) both predate or misread the approved split: the approved re-plan names neither FCC nor Codex for R3-029, it names Muse. Under the hierarchy, Muse drives R3-029. The frozen order file lane lines (FCC positions 1 to 28, Codex positions 29 to 55) describe the pre-re-plan freeze and are superseded for runner assignment by the approved re-plan; order, keys, and positions in that file stay frozen.

Position number resolved: R3-027 is frozen position 23. Script count of the 55-token order line (2026-11-26, this worker): R3-027 index 23, R3-028 index 24, R3-029 index 25, R3-035 index 26, R3-036 index 27, R3-037 index 28. The parent figure of 24 for R3-027 is wrong (24 is R3-028). The redteam figure of 23 is correct. Council-3 section 3.0 positions (R3-027 at 23, R3-028 at 24, R3-029 at 25) hold.

### F7.2 Lane table for all 31 remaining tasks

Driving is non-movable. One driver at a time on shared Zen on ws2. Backpressure max 2 unscored per runner lane. Class L runner waits for both verdicts before reset. Class S runner proceeds after the snapshot gate. Timeout for every drive: 30 minutes, over 30 minutes is FAIL, never graded from partial evidence, kill by exact recorded PID only. Pill rule for every drive: the pill must show on any agent control by any method; acquire before driving, release after, verify with grim, end each session with finish. Pill text is plain: Computer use active. Raw CDP is read-only until a pill-on-CDP mechanism exists; live browser writes go through the computer-use session so the pill shows. Lane brief version: the L3 lane briefs re-issued and acknowledged in writing by FCC (09:06) and Codex (state file, G-26 and G-30), plus the Muse runner lane brief from the approved re-plan section 3 (fresh independent subagent per task, lane brief plus task only, SSH via ~/workspace/ssh-laptop.sh, detached long jobs, evidence to the laptop evidence dir, coordinator seals and gates). Every runner brief also carries the F10 fields, the F12 guards for its task, the ponytail rule text (council-3 section 1.6 verbatim) for code tasks, the ydotool ban, and the tab rules (never close or navigate owner-opened tabs; open a new tab beside owner tabs; runner closes its own task tabs at drive end).

| Lane | Tasks | Count | Method |
| --- | --- | --- | --- |
| FCC | R3-027, R3-037 | 2 | tmux r3-fcc-runner-L3 (pane PID 22399 at last check), easiest tasks only, no coaching on key values. R3-014 already graded, so 2 of the approved 3 remain |
| Muse subagents | R3-028, R3-029, R3-035, R3-036, plus task 56 default | 4 plus 1 | Fresh independent Muse subagent per task, SSH via ~/workspace/ssh-laptop.sh, Zen via computer-use with pill visible, lane brief plus task only |
| Codex | R3-045, R3-046, DP-03, R3-049, R3-055, R3-067, R3-072, R3-074, R3-075, R3-076, R3-078, R3-079, R3-082, R3-083, R3-085, R3-086, R3-088, R3-089, R3-093, R3-094, R3-096, R3-098, R3-099, R3-100 | 24 | codex exec per task from /home/james, -m gpt-6-luna --sandbox danger-full-access --skip-git-repo-check, Hyprland env exported in every launch |

Explicit decisions for the four contested tasks. R3-028 (position 24): Muse subagent. Reason: approved re-plan assigns it to Muse; it is a named INVALID candidate, and the genuine-runner rule from the re-plan (FCC fabrication history on R3-001, R3-002, R3-003) keeps evidence-critical tasks off FCC. R3-029 (position 25): Muse subagent. Reason: approved re-plan section 2.2 names it Claude-run with the credential parent-held; council-3 FCC naming is superseded (F7.1). Password flow in F7.3. R3-035 (position 26): Muse subagent. Reason: approved re-plan Muse list, same genuine-runner rule. R3-036 (position 27): Muse subagent. Reason: approved re-plan Muse list; named INVALID candidate, same rule as R3-028. No lane change is made by this record beyond confirming the approved split; the change relative to the frozen order file was already made by the approved re-plan, and the receiving lane brief, timeout, and pill rules above cover every moved task.

Task 56 runner: Muse fresh independent subagent by default. Codex is the approved alternative if the Muse runner fails twice on task 56. Opencode cannot run task 56 or any remaining task (F9). Order: frozen order R3-027 onward, no reordering mid-run. Task 56 last, after R3-100, Class L, leave restored tabs live, coordinator verifies against the live tab list plus sessionstore before scoring closes. No reset exists for task 56. Runner briefs are re-issued with this lane table and acknowledged before R3-027 releases; the state file lane table must match this table at synthesis.

### F7.3 R3-029 password flow for the Muse lane

Restated for the chosen lane (Muse subagent runner), no exceptions. The test-account credential is held by the parent. It goes in the R3-029 task brief at release time only. It never goes in any file, state file, ledger, log, commit, snapshot, or evidence dir. The parent re-verifies the credential with the owner before position 25 arrives. Epoch 9 (the run coordinator) notifies the parent as the position approaches, at position 24 release at the latest, earlier if pause timing makes the approach uncertain. If the credential is not confirmed by release time, R3-029 is held and the coordinator reports to the parent. The runner never guesses, never reuses another credential, and never asks the owner directly. After the task, the brief copy holding the credential is destroyed, and the destruction is logged without the value (log line names the task, the destruction time, and the method; never the credential). The key itself was verified correct before the run (all 5 product names with prices, wishlist works); this record repeats no credential value and no account identifier beyond what the frozen files already carry.

## F8. PII push gate verified or replaced

### F8.1 Scanner check on the VM (live, timed)

Check run 2026-11-26 about 05:43 Asia/Ho_Chi_Minh, elapsed under 1 second: command -v gitleaks returns nothing (exit 1, gitleaks not on PATH). gitleaks version fails (command not found). command -v trufflehog also returns nothing. Python 3.12.3 is present. Git 2.43.0 is present. Graphify is present at ~/.local/bin/graphify (version 0.9.120, F9). Conclusion: the council-1 PII gate names a tool that is not installed. A gate that names an unverified tool is not a gate, so the gate is replaced below. No install was run by this worker.

Replacement scanner, specified with version and run method: local PII scan script pii-scan.py, version 1, Python standard library only (ponytail: no new dependency for a grep-class job), owned by the coordinator, run on the VM before every snapshot push. What it checks, deterministically, on every file in the snapshot dir: password and token patterns (key names matching password, token, secret, api key, bearer, session, cookie, plus high-entropy strings over 20 characters), email addresses, phone numbers, and owner tab URLs (any http or https URL whose host is a mail, calendar, drive, or docs service, plus any URL with account path segments). Output: one line per hit with file path and line number, exit code 1 on any hit, exit code 0 only when clean. The coordinator also runs the manual checklist (passwords, tokens, personal emails, owner tab URLs beyond what the task requires) beside the script. A failed scan stops the push. The snapshot does not move by chat.

If the team later wants gitleaks itself, the exact install route to verify (not assumed, not run here) is: download the pinned release binary from the gitleaks GitHub releases page, verify its published sha256, place it at ~/.local/bin/gitleaks, then verify with command -v gitleaks and gitleaks version, and file both outputs. Until that verification exists, briefs name pii-scan.py version 1, never gitleaks.

### F8.2 Explicit pathspec git commands for snapshot pushes

Never git add -A. Never a bare git commit (it sweeps any staged file, including another worker file). Add and commit atomically with an explicit pathspec, then verify by ls-remote. Templates (coordinator fills the task ID; run from the worktree root):

    git add -- rung3-run-log/rung3-snapshots/R3-xxx-L3/
    git diff --cached --stat
    git commit -m "snapshot R3-xxx-L3" -- rung3-run-log/rung3-snapshots/R3-xxx-L3/
    git push origin HEAD:todolist-push
    git ls-remote origin todolist-push

The diff --cached check must show only the intended snapshot files before the commit runs. Ledger pushes use the same shape with the ledger pathspec (rung3-run-log/R3-L3-grades.jsonl, and rung3-run-log/R3-L3-reruns.jsonl when re-runs change). Verdict branches keep exactly two files per scorer (verdict json plus grade markdown) under the branch name form in council-1 section 5. The PII scan (F8.1) runs before the add step, and its output is filed with the snapshot record.

Test required before resume (redteam F8 verify): one already-scored snapshot goes through the full path (seal, scan, pathspec add, commit, push, ls-remote, scorer pull, verdict branch, coordinator audit) with scanner output filed. This worker did not run the test push (no commit authority); the coordinator runs it during Phase 2 readiness and logs the result via log-event.sh.

### F8.3 Task 56 VM-local default restated

Task 56 tab URLs are owner data. The task 56 snapshot stays VM-local by default. It is not pushed with full URLs unless the owner approves (notification point F2.4 item 4 covers ambiguity; a push decision is separate and explicit). Scorers for task 56 (Mochi plus Clone2, F5 table) grade from the VM-local snapshot plus the coordinator live verification note, with URLs redacted to host plus path pattern where the key allows. If redaction would break grading, the coordinator asks the owner before pushing. Default is no push of task 56 URLs. This restriction must appear in council-3 operations (section 3.2 currently lists the restore set without it) and verbatim in both task 56 scorer briefs before position 56 arrives. This record deliberately does not reproduce the restore URLs; the sessionstore on the laptop is the source of truth, and any list in a brief stays VM-local.

R3-029 credential rule, restated with the gate: the test-account password never enters the snapshot, the evidence dir, or any file (F7.3). The PII scan is a backstop, not a substitute for that rule.

## F9. Skill-scout dispositions, pinned versions, and proofs

Registry source: ~/workspace/skill-scout/REGISTRY.md (read in full). One line per item: adopt, defer with reason, or reject. Nothing installs from this record; installs run under the team gate in council-3 sections 1.2 and 2.1 order, each with check-before-installing repeated at install time, one CLI at a time, timed and logged, registry entry updated the same day with version, state proof, behavior proof result, revert command, and log path (owner rule 04:57: a skill counts as equipped only after proven live use with that staff member).

| Item | Disposition | Reason and next step |
| --- | --- | --- |
| 1. codex-plugin-cc for FCC, review gate OFF | Defer to post-run | Highest leverage in the registry, but it adds a marketplace fetch and a Codex-from-FCC review path mid-pause while FCC drives only 2 remaining tasks. The run does not need it. Post-run: marketplace add, install, setup, gate OFF, test /codex:review --background on one real diff against independent_review output. Confirm the LICENSE file before vendoring |
| 2. webapp-testing plus skill-creator (single folders) | Defer to post-run | Useful for frontend-kit verification and for the scout team itself, but no remaining run task depends on them. Post-run: copy single folders only, pip install playwright plus playwright install for webapp-testing, test on a frontend-kit fixture; run the skill-creator eval on one existing custom skill before trusting it |
| 3. caveman skill-only for FCC plus VM | Defer to post-run | Cheap and reversible, and Codex plus opencode already carry the family, but output-style changes mid-run risk scorer and runner format drift for zero run benefit. The proxy and Auto router stay deferred for a measured A/B. Post-run: skill-only install, never the proxy without its own gate |
| 4. Context7 for Codex (API key owner: parent) | Defer to post-run | Needs one free API key created by the parent (scout does not create accounts). No remaining task needs version-specific docs badly enough to add an MCP or CLI surface mid-pause. Post-run: Codex first in CLI plus Skills mode, measure retries and tokens on held-out tasks, then FCC. Never for mochi scoring |
| 5. Ponytail for FCC: skill folder versus plugin | Adopt skill folder for the run; plugin deferred post-run | Registry proposes copying the skill folder to ~/.claude/skills (low risk, no marketplace fetch, no tmux refresh). Council-3 chose the plugin route without comparing. For 2 remaining FCC tasks, the skill folder at instruction tier plus the verbatim rule text in every brief (council-3 section 1.6) is sufficient and safer. The plugin (lifecycle hooks, levels, subagent injection) is post-run, with the marketplace command-accept stop rule and sha256 record from council-3 section 1.2 if it is ever installed |
| 6. last30days 4.6.0 blocked update | Defer; VM stays on 4.5.0 | The cloned upstream content failed a runtime execution-risk check and must not be copied or installed without owner approval. Parent decides the update path post-run (for example npx skills add, or approve the clone copy). FCC carries last30days at an unread version; record that version at the next FCC check. One install method per machine (marketplace and npx copies do not dedupe) |
| 7. Later list: superpowers A/B on Codex | Defer to post-run | One-harness A/B only (Codex, one held-out task with and without, tokens plus review quality). Overlap and friction risk with ponytail smallest-change rule. No FCC or VM rollout until the A/B passes |
| 8. Later list: Serena, GPL tool-use only | Defer to post-run | Bounded Codex test only (one language server, one held-out refactor) against the graphify plus grep plus edit baseline. License split (SolidLSP MIT, Serena app GPL-3.0-or-later): tool use is fine, never vendor or link its code into computer-use-wayland. Council plus redteam gate before wider rollout. Reject the paid JetBrains backend |
| 9. Later list: Chrome DevTools MCP slim | Defer to post-run | Codex-only trial with --slim --no-usage-statistics --no-performance-crux on one real frontend debug task against the vision path. Confirm the LICENSE file before install. Chrome-only: does not fix the Zen Cloudflare problem |
| 10. Later list: wshobson 2 plugins for FCC | Defer to post-run | developer-essentials plus security-scanning for FCC only, one PR review through each against current FCC output. Reject bulk install (context bloat, duplicates existing code-review and tdd skills) |
| 11. Later list: agnix | Defer to post-run | Read-only trial over ~/workspace/custom-skills/ plus laptop skill dirs; adopt as a pre-commit-style check only if it catches real breakage. Reject full agentsys (duplicates governance skills) |
| 12. Later list: Semgrep retry | Defer to post-run | VM install failed 3 attempts on proxy timeouts (not a tool defect). Retry on the laptop post-run with parent approval, write 3 starter rules (ydotool ban, PII patterns, banned imports), measure false positives. Complements the F8 scanner; does not replace it mid-run |
| 13. Later list: last30days for Codex | Defer to post-run | Install via npx skills add so Codex research tasks match brief quality. No remaining Codex run task is a research task, so no run dependency. Post-run with the F9 item 6 update decision |

Pinned versions. Ponytail: 5.3.3 (verified by this worker 2026-11-26 in ~/workspace/ponytail-repo/.claude-plugin/plugin.json, name ponytail, version 5.3.3; six skills present). Any laptop install records the installed version exactly and must match 5.3.3 or record why it differs. Graphify: graphifyy 0.9.120 to match the VM (verified: ~/.local/bin/graphify --version prints graphify 0.9.120). Laptop install command pins the version: uv tool install graphifyy==0.9.120. An unpinned install that lands a different version is a stop-and-record, not a pass. File-transfer method for any VM-to-laptop copy (the FCC skills fallback): base64 chunk transfer with muse.write, or scp verified by hash readback, specified in the install brief. Never assumed, given the intermittent exec-write failures on record.

Codex ponytail exec-mode proof, specified. The run invokes Codex exactly as: codex exec -m gpt-6-luna --sandbox danger-full-access --skip-git-repo-check, one invocation per task from /home/james, with XDG_RUNTIME_DIR, WAYLAND_DISPLAY, DBUS_SESSION_BUS_ADDRESS, and HYPRLAND_INSTANCE_SIGNATURE exported in every launch. The proof runs through that shape, in a scratch directory, with the council-3 date-picker task (add a date picker to a tiny page that already has an Input component). Activation evidence expected in exec output: the result reuses the existing Input with a native date type in a handful of lines, adds no dependency, and the reply ends with what was skipped and any risk; plus one $ponytail:ponytail-review invocation on the scratch diff answering in ponytail review format. An interactive-thread-only proof does not count. Fallback ruling: if SessionStart hooks do not fire in exec mode, skill-tier is sufficient for the run (the bare skill file at ~/.codex/skills/ponytail/SKILL.md, 3492 bytes, plus verbatim rule text in briefs), the plugin is deferred post-run, and the registry records the exec evidence. The same exec-mode question applies to the graphify platform skill for Codex: proof through codex exec shape or file-read fallback, recorded either way.

Graphify laptop checkout path, verified read-only. Short SSH calls via ~/workspace/ssh-laptop.sh on 2026-11-26 about 05:44 Asia/Ho_Chi_Minh, elapsed about 4 seconds each, no laptop file changed. Two checkouts exist: /home/james/computer-use-wayland at HEAD 58c419f527803a14cef49ec259f6ead5f9317f82, and /home/james/workspace/computer-use-wayland at HEAD 9ac4dcdaeb66b55fc0a3edbe70c085e9ff63563b. Both point at the same origin repo. The VM reference graph was built from commit f58e341df93222d20fd0d5e756546884e6a69877 at ~/workspace/cu-graphify (7903 nodes, 16640 edges, 430 communities). Neither laptop HEAD matches the VM build commit, so counts will differ and the VM numbers are a sanity range only. Implementer instruction: build the laptop graph in the checkout the laptop agents actually work in, record git rev-parse HEAD before the build, and state which of the two paths was chosen and why. If neither path is reachable at install time, the exact verification command is: git -C <candidate path> rev-parse HEAD plus git -C <candidate path> remote get-url origin, run over ~/workspace/ssh-laptop.sh as a short call. Do not copy the VM graph.json to the laptop as the working graph (council-3 ruling, kept).

Two exact graphify proof queries, with expected files (verified by this worker against the VM graph 2026-11-26, each about 3 to 6 seconds). Query 1, explain: graphify explain "ZenSession" --graph graphify-out/graph.json. Expected: node ZenSession, source scripts/zen_dom.py L67, with real neighbors including ._wd(), .evaluate(), .locate(), .list_tabs(), .verify(). Query 2, path: graphify path "scripts_mcp_server_zenbackend_session_start" "scripts_zen_dom_zensession" --graph graphify-out/graph.json. Expected: shortest path 1 hop, .session_start() calls ZenSession (scripts/mcp_server.py L168 to scripts/zen_dom.py). Cross-check one answer by hand: open scripts/zen_dom.py and confirm class ZenSession at L67. Pass needs both queries plus the hand check. Fail is node not found, empty neighbors, no path, or neighbors absent from the checkout.

Opencode: INSTALLED, unverified. Ponytail is directory-loaded (plugin file, six skills, six commands, mode file full), so opencode plugin list is not evidence either way. Live model proof waits until the owner picks an opencode provider model (opencode/ prefix only, never NVIDIA, Groq, or OpenRouter). No run task depends on opencode. Clone1, clone2, mei, mochi ponytail state: UNKNOWN until each answers directly in its own chat. Never guess. Every code brief to those accounts restates the ponytail rule text verbatim (council-3 section 1.6) and asks the account to confirm skill availability before starting; the answer is recorded in the registry under that staff member. If the account cannot load the skill, the brief text itself is the ruleset for that task and the reviewer checks the diff against it.

## F10. Brief field spec: event-log duty and user-path fields

Paste the two blocks below into every brief template, unchanged. A brief without them is incomplete.

Event-log duty line (every coordinator and worker brief):

    Event-log duty: log key events (decisions, test results, fix milestones, revert actions, invalid rulings, gate results) via ~/workspace/agent-event-log/log-event.sh to the master log on the laptop at ~/agent-event-log/events.log, and keep state notes and per-task reports complete for the 15-minute harvest.

User-path fields (every test brief, filled per test):

    User-path test: enter via search/homepage and click through like a normal user; no deep links, no direct commands, no internal setters; evidence shows entry, path, action, and resulting state.
    User entry point for this test: <search query, homepage, or in-app start screen, named>
    Forbidden shortcuts for this test: <deep links, direct commands, internal setters, test-only endpoints, direct navigation A/B, named for this test>

For a surface that is not user-facing (code discipline proofs such as ponytail and graphify behavior proofs), the brief carries instead one line naming the real entry point, for example: Surface is not user-facing. Real entry point: codex exec -m gpt-6-luna --sandbox danger-full-access --skip-git-repo-check from /home/james (the exact invocation the run uses). Equipping evidence records the entry point used.

Coordinator spot-check rule: the coordinator spot-checks the next three briefs per lane after this record lands. Any brief missing the event-log line or the user-path fields (or the not-user-facing line with the real entry named) is returned incomplete, unread for user-facing claims. End-state-only evidence for a user-facing claim is returned unread, like a bare done. The check itself is logged via log-event.sh.

## F11. Counter repair evidence and full-file parse (evidence only)

This worker does not write the state file. Values below are for the coordinator to write at synthesis via temp file then rename.

Invalids by group, recounted from the ledger plus the frozen list difficulty lines. R3-011: trung binh (list line 373, do kho trung binh), backup DP-06 (Tier B trung binh). R3-022: kho (list line 431, do kho kho), backup DP-02 (Tier A kho). R3-024: trung binh (list line 438, do kho trung binh; also moved from kho to trung binh in round 3, list line 89), backup DP-07 (Tier B trung binh). R3-026: trung binh (list line 452, do kho trung binh), no backup. Totals: trung_binh 3, kho 1, rat_kho 0, de 0, total 4. Corrected invalid_by_group values for the coordinator to write: {"de": 0, "kho": 1, "rat_kho": 0, "trung_binh": 3}. The state file currently reads all zeros and contradicts the ledger; every future cap check reads from a broken counter until this lands. After writing, verify by independent recount from the ledger and record state last_updated after the fix.

Full-file JSONL parse, run 2026-11-26 about 05:43 Asia/Ho_Chi_Minh, elapsed under 1 second (python3, every line parsed, trailing-newline check on raw bytes). R3-L3-grades.jsonl: 29 lines, all parse, file ends with newline, no glued line. R3-L3-reruns.jsonl: 3 lines, all parse, ends with newline, no glued line. r3-l3-heartbeat.log: 108 lines by wc, ends with newline, 107 lines parse as single JSON objects, 1 line fails. Glued line found: heartbeat line 23 contains two JSON objects concatenated with no newline between them (first object ts 2026-11-25T17:42:23+07:00, epoch 6, graded 5; second object ts 2026-11-25T17:46:30+07:00, epoch 6, graded 6, R3-042 graded PASS). Parse error: Extra data at column 749. This is the pre-existing glued line the epoch 9 note mentions; the redteam tail check did not hit it because it sits early in the file. Disposition: the coordinator splits line 23 into its two objects at synthesis (or annotates it as two records) and re-runs the full parse; no heartbeat record is lost, both objects are intact and readable. Ledger append discipline from here: check the file ends with a newline before any append, parse-verify after every push.

## F12. Watch-item guard texts, verbatim for runner briefs

Copy each block into the named runner brief unchanged, before its position arrives. The coordinator verifies presence verbatim.

R3-100 kill guard (into the R3-100 runner brief and the coordinator pre-check):

    R3-100 port guard: before R3-100 starts, read the port number from the frozen key (docs/rung3-answer-keys.md, R3-100 section; the key is the source of truth, do not hard-code the number), list listening ports with ss -tlnp, and confirm the target port is in the state the key expects. Record the process name and full command line of anything holding the port before any kill. Kill only a process proven to be a leftover from a prior run task (recorded runner PID or evidence path from that task). Never kill a process whose owner cannot be shown to be a prior run task. After any kill, re-verify the port state. The runner records the port state at run time (ss output plus saved HTML) into the evidence folder. The scorer grades from the saved files only and never re-checks the live port. If the port is held by an unrelated process that cannot be killed, stop and report to the parent before starting.

R3-089 refresh ownership during the pause (into the R3-089 runner brief and the coordinator checklist):

    R3-089 fixture guard: the fixture holds 12 log files; the key expects find -mtime -7 to return exactly 6 (log-01 to log-06 within 7 days, log-07 to log-12 older). Hard expiry 2026-12-01 08:59 Asia/Ho_Chi_Minh. The run coordinator owns the refresh, during the pause and after resume alike. Refresh the day before R3-089 runs. Date guard: if the run has not reached R3-089 by 2026-11-30 12:00, refresh on 2026-11-30 anyway so the fixture stays valid through 2026-12-07. Refresh touches ~/rung3-goc/nd09-logs/ only (touch -d "1 day ago" for log-01 to log-06, touch -d "10 days ago" for log-07 to log-12), contents untouched. Record date, time, who, count, and new expiry in rung3-run-log/r3-l3-r3-089-refresh.md. Confirmation runs after the reset that precedes R3-089 and before the runner starts, on the live ~/rung3/nd09-logs/: count verified exactly 6. If the count is not 6 and a refresh cannot make it 6, stop and report to the parent. Do not run R3-089 on a broken fixture.

R3-079 pre-check inside the R3-079 brief itself (not only in the plan):

    R3-079 coupled reset pre-check, run before R3-079 starts and after R3-078 is scored and reset: (a) R3-078 snapshot gate PASS and R3-078 graded; (b) ls ~/rung3/d45-backup returns No such file and ls ~/rung3/d46-restored returns No such file; (c) the d46 fixture is intact in ~/rung3-goc/. If d45-backup still exists after the reset, the reset failed. Do NOT start R3-079. Report to the parent and fix the reset first. General rule for every task: before any task starts, diff -r -q ~/rung3/ ~/rung3-goc/ must be empty. After any task: snapshot, manifest gate, grade or queue the grade, reset, re-run the diff. The reset restores ~/rung3/ from ~/rung3-goc/ and clears the evidence dir for the task just run. The reset never touches ~/rung3-goc/. Both R3-078 and R3-079 are Class L: the runner waits for each grade before each reset.

## Verify checklist for the redteam reconvene

Run each line; record pass or fail with evidence path. No line needs owner approval.

F1. Recount R3-L3-grades.jsonl and R3-L3-reruns.jsonl from the files (counts by final_grade). Expect 21 PASS, 4 INVALID, 3 FAIL, 1 TEST plus 3 re-run PASS, rule-A 24 PASS and 0 FAIL. Confirm the corrected table (banked 24, invalid 4, remaining 30 plus task 56, need 28 and 29, cascade need 25 from 27) and grep council-1 and council-3 for the stale figures in F1.3; each must be superseded by this record. Log via log-event.sh.

F2. Read the state file after synthesis. Expect: ratio reading recorded (weights 100, 100, 85, 50, total 335, with reason), cap decision recorded (drop R3-026, bars 52 of 54 and 53 of 55, superseded bars stated), resume gate recorded as the delegated team gate, notification points listed. Grep all three council drafts and this record for any line requiring owner approval to resume. Expect zero live lines.

F5. Check every row of the F5.2 table: prep owner, analyst pair, and review auditor named for all 31 tasks; no scorer preps, analyzes, or reviews a task they score; reviewer never the prep owner; named-candidate reviewers outside the analyst pair. Confirm analyst totals (mei 6, clone2 4, clone1 2 WU) match the F5.3 table. Confirm R3-026 analysis marked done with du-phong.txt evidence. Confirm mei tally source names coordinator reports only, and no dc7e0d0d supervision line survives. Confirm the quota honesty note (ratios post-resume, in-flight and calibration load stated).

F6. Confirm the old calibration set is retired, the sealing procedure names the verifier-held file and the allowlist (snapshot plus key section only), no future run task key is in the set (no R3-067), and the verifier is TB-A or TB-B2 with sign-off on file (improvements/r3-l3-tbb2-signoff-20261125.md) or calibrated 4 of 4 on a separate sealed set. Confirm the tiebreaker history line (2 used: R3-021 and R3-002 re-run) and the re-based reserve (3 tiebreakers, 6 WU).

F7. Confirm one lane table for all 31 tasks matches the state file after synthesis, with R3-028, R3-029, R3-035, R3-036 each decided with reason, lane brief version, 30-minute timeout, and pill rule. Confirm the R3-029 password flow (parent holds, brief at release only, never in file, epoch 9 notifies parent as position 25 approaches, brief copy destroyed after, destruction logged without value). Confirm R3-027 recorded as frozen position 23.

F8. Run command -v gitleaks and the replacement scanner version check on the VM. Expect gitleaks absent and pii-scan.py version 1 named with its run method, or gitleaks present with version filed. Confirm explicit pathspec add and commit templates (never git add -A) and the test-push result filed with scanner output and ls-remote verification. Confirm task 56 VM-local default in operations text and in both task 56 scorer briefs.

F9. Confirm one disposition line per skill-scout item (F9 table, 13 lines). Confirm pinned versions (ponytail 5.3.3, graphifyy 0.9.120) and the Codex exec-mode proof specification with the skill-tier fallback ruling. Confirm the graphify laptop checkout path with git rev-parse HEAD recorded, and the two exact proof queries (ZenSession explain, session_start to ZenSession path) with expected files. Confirm opencode INSTALLED unverified with no run dependency, and clone1, clone2, mei, mochi ponytail UNKNOWN with verbatim rule text in briefs.

F10. Grep the next three briefs per lane for the event-log duty line and the user-path fields (or the not-user-facing line with the real entry named). Expect all present. Confirm the spot-check itself was logged via log-event.sh.

F11. Recount invalids by group from the ledger. Expect trung_binh 3, kho 1, rat_kho 0, de 0, total 4, matching the values the coordinator wrote. Re-run the full-file JSONL parse on grades, re-runs, and heartbeat with trailing-newline check. Expect grades and re-runs clean, heartbeat line 23 split or annotated with both objects intact.

F12. Grep the R3-079, R3-089, and R3-100 runner briefs for the F12 guard texts verbatim (process name plus command line recorded, kill only proven prior-task leftovers; 2026-11-30 12:00 guard stands, refresh goc only, contents untouched, count verified 6; R3-079 pre-check inside the brief itself). Expect all present before their positions arrive.

End of fix record.
