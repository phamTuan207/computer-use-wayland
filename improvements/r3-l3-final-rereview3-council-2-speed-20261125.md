Verdict: AGREE

# Final Prepare RE-REVIEW ROUND 3, Council 2 (Speed / Benefit), R3-L3, 25/11/2026

- Council: Council 2, speed and benefit lens, fresh reviewer, independent of rounds 1 and 2. This council did NOT write the round-1 or round-2 Council 2 verdicts. It verified the committed files itself and did NOT trust the coordinator's summary or the brief alone.
- Date: 2026-11-25, about 12:00 +07.
- Worktree: ~/workspace/r3l3-run-wt, HEAD 82a9f49e, git status clean, no uncommitted changes. Origin todolist-push verified live via ls-remote = 82a9f49ec707da9d47a490d7135e44d4bcefc8a3.
- Files read in full and verified live: improvements/r3-l3-replan-final-20261124.md (worktree copy, operative, 363 lines), rung3-run-log/r3-l3-time-budget.md (49 lines), rung3-run-log/thu-tu-chay.txt (90 lines), rung3-run-log/r3-l3-coordinator-state.json (125 lines), rung3-run-log/r3-l3-exception-list.txt, rung3-run-log/du-phong.txt, rung3-run-log/r3-l3-deputy-dry-run-20261125.md, rung3-run-log/scorer-briefs/rung3-scorer-brief-R3-L3-addendum.md (backup order lines only), improvements/r3-l3-final-rereview2-council-2-speed-20261125.md (round-2 Council 2 verdict, AGREE with observation O-1), improvements/r3-l3-final-rereview2-redteam-20261125.md (round-2 redteam verdict, headings and R2-M1/R2-M2/R2-S1/S2/S3 only), ~/workspace/r3-l3-execution-plan-20261124.md (budget lines only).
- Live checks done by this council: git log (tip 82a9f49e, parent b26a34c5), git ls-remote origin todolist-push = 82a9f49e, git show 82a9f49e diff for time-budget.md (the O-1 fix, one line), python token count of the thu-tu-chay.txt order line (55 tokens, token 25 R3-029, token 34 DP-03, token 49 R3-089, R3-047 absent, 0 duplicates), sha256sum of thu-tu-chay.txt (a759ad21266743beea94e7e22bf962c3a380aa2efadee86d0461f9bf8ae2395d) and du-phong.txt (7d17b9b73584bfcafe0c238bc328859c011a263232df748ade7e098fe2889290) matching the state file round-2-fix note, grep for em dash and en dash in the three checkpoint files (0 in each).
- This council did NOT edit any run doc. It did NOT commit. It did NOT start the run. It did NOT run any run task. It did NOT message any agent.

## Standing rules (restated)

- NO OpenRouter. Never try it, never propose it. FCC's built-in OpenRouter-free backend is allowed per the owner's 25/11 decision; the ban covers only Opencode.
- NO em dash (U+2014) or en dash (U+2013) in any file. Commas, periods, or short hyphens only.
- NO personal info on GitHub (no name, address, email, phone, schedules, photos, accounts, passwords, tokens). The R3-029 password must NOT appear in any file.
- Never assume an agent's capabilities. Check or ASK THE AGENT DIRECTLY in its own chat.
- Clone1 and clone2 have NO Tailscale/SSH. Repo and web work only. Do NOT give them machine tasks.
- CDP-first observation: CLI/API first, then DOM, screenshot/vision last.
- Never close or navigate any window/tab the owner opened. Never close the 4 agents' windows in ws3.
- The pill MUST be visible on ANY agent control. Pill text is always plain "Computer use active."
- Do NOT edit MEMORY.md. Observations go to ~/memory/2026-11-25.md.
- Do NOT start the run. Do NOT run any run task.

## Verdict detail

Round 2 Council 2 voted AGREE with exactly one observation, O-1: the pause-release default differed between the re-plan (line 269, default continue if the owner is unreachable within 30 minutes) and time-budget.md (line 33, "The run continues ONLY on the owner's decision", no default). That item is now VERIFIED FIXED in commit 82a9f49e. The checkpoint trigger is identical in substance in all three places, the 19-31h budget holds after the DP-03 swap, the rolling-release and parallel-scoring design is intact, no round-2 fix introduced a new bottleneck, and no round-2 speed item remains open. This council agrees.

## Numbered verification items

### 1. O-1 VERIFIED FIXED: the pause-release default is now aligned between re-plan line 269 and time-budget.md

- Re-plan line 269 ends: "The checkpoint decision is pre-authorized before task 1: the owner picks continue, stop, or add scorers, with a default if unreachable within 30 minutes (default: continue, record the estimate, and re-check at the next milestone)."
- Time-budget.md line 33 now reads: "The run continues on the owner's decision; if the owner is unreachable within 30 minutes, the default is continue, record the estimate, and re-check at the next milestone (re-plan line 269, pre-authorized before task 1)."
- Commit evidence: git show 82a9f49e shows the exact one-line diff in time-budget.md, replacing "The run continues ONLY on the owner's decision." with the aligned sentence above. The old fail-closed wording is gone from the file (grep for "ONLY on the owner's decision" returns nothing in time-budget.md).
- The two wordings are now the same rule in the same words: owner decides; unreachable within 30 minutes means continue, record the estimate, re-check at the next milestone. No pause can now hang indefinitely on an unreachable owner, and no coordinator faces two contradictory release rules.

### 2. VERIFIED: the checkpoint trigger is identical in substance in all three places

- The four required elements (pause ONLY if revised run-complete exceeds 31h OR a per-class mean exceeds its estimate by more than 25 percent with at least 3 graded tasks of that class; 22-31h continues with a recorded estimate; 3-hour wall-clock fallback; trigger does not fire on the biased early sample) are present in each file:
- Worktree re-plan line 269: full paragraph, all four elements, ending with the pre-authorized default verified in item 1. Re-plan line 43 carries the same summary.
- Time-budget.md lines 24-41: lines 29-33, pause ONLY if the revised run-complete exceeds 31 hours OR a per-class mean exceeds its estimate by more than 25 percent with at least 3 graded tasks of that class, plus the aligned release default; lines 35-36, "A revised run-complete of 22-31 hours continues with a recorded estimate (no pause)"; lines 39-41, 3-hour fallback, "if the 3rd graded task has not landed by 3 hours after task 1, the coordinator reports to the owner"; lines 37-38, the trigger does not fire on the biased early sample.
- Thu-tu-chay.txt line 90: "Checkpoint sau task thu 3 duoc cham: dieu phoi vien TAM DUNG va bao chu so huu CHI NEU uoc tinh hoan thanh vuot 31h HOAC trung binh theo class vuot ke hoach hon 25% voi it nhat 3 task da cham cua class do; uoc tinh 22-31h thi chay tiep (ghi lai uoc tinh, khong tam dung); neu task thu 3 chua duoc cham sau 3 gio ke tu task 1 thi bao chu so huu. Xem rung3-run-log/r3-l3-time-budget.md." Same four elements in short form.
- Precision note, stated plainly: the 30-minute unreachable-owner default is NOT repeated verbatim in thu-tu-chay.txt line 90. It is carried in the two authoritative places (re-plan line 269, time-budget.md line 33), and thu-tu-chay.txt line 90 ends by pointing at time-budget.md ("Xem rung3-run-log/r3-l3-time-budget.md"), which now carries the same rule. The trigger itself (what fires the pause) is identical in all three; the release default is aligned where the rule lives and reachable from thu-tu-chay.txt through that pointer. Round 2 accepted this short-form-plus-pointer shape for the trigger, and the same shape now holds for the release default. This council does not treat the missing verbatim repeat in thu-tu-chay.txt as a defect, because adding it would change the thu-tu-chay.txt sha256 and force another G-32 hash refresh for zero rule change.

### 3. VERIFIED: the 19-31h budget still holds after the DP-03 swap (55 tasks, bar 53/55, 9 Class L / 46 Class S)

- Order line verified live by python token count: 55 tokens, token 25 R3-029, token 34 DP-03, token 49 R3-089, R3-047 absent, 0 duplicates. Thu-tu-chay.txt lines 6 and 8: 55 tasks, medium 37, hard 11, very hard 7, pass bar 53/55. State file: class_l_count 9, class_s_count 46, backups_used DP-03, current_position 0, run NOT started.
- Class mix confirmed against the exception list: 9 Class L (R3-001, R3-055, R3-074, R3-075, R3-089, R3-096, R3-078, R3-079, R3-088) and 46 Class S, with DP-03 listed as Class S like R3-047 (exception list lines 43-44 and 66). The swap changes no class count, because DP-03 is Class S and R3-047 was Class S.
- DP-03 is a terminal task (one ss command plus a report, thu-tu-chay.txt line 74: N = 5, minimum 3) versus R3-047 a 3-book browser search, so the swap is budget-neutral to slightly faster. No per-task minute estimate exists for either task in any file, so no larger saving is claimed.
- The 19-31h honest range appears identically in re-plan line 6, re-plan line 275, time-budget.md lines 4-7, and thu-tu-chay.txt line 90, all staffed for 31h and measured from task 1 start (re-plan lines 105 and 275). The budget arithmetic is unchanged: 55 tasks at about 21 minutes mean cycle time is 19h, at about 34 minutes is 31h (time-budget.md lines 10-13), with up to 3 timeouts at 30 minutes each already inside the 31h figure (lines 19-21). Execution plan lines 540 and 562 agree (19-31h, staffed for 31h).
- The 4-task shared-cause scenario (R3-011/028/036/046) is a table lookup, valid 53, bar 51/53, notify not stop (re-plan G-46 line 137, du-phong.txt line 38, addendum lines 47-48). It adds no scoring delay and no run stop. Per the brief, this decision is not blocked on.
- The scorer addendum backup order now reads "Medium backups in order: DP-06, DP-07" with DP-03 marked USED at position 34 (addendum line 11), so no mid-run backup assignment can stall on a consumed DP-03.

### 4. VERIFIED: the rolling-release and parallel-scoring design still holds

- Two lanes, two scorer pairs: FCC positions 1-28 with Pair A (Mochi scorer 1, dc7e0d0d scorer 2, TB-A tiebreaker), Codex positions 29-55 with Pair B (1B, 2B, TB-B2), in thu-tu-chay.txt lines 16-31 and the state file scorers block. No lane or pair changed in the round-2 fix (git show 82a9f49e touches no lane or pair assignment).
- Rolling release: re-plan line 259, Phase 1, "rolling release (the next task starts as soon as its evidence is locked, score in parallel behind it)"; thu-tu-chay.txt lines 48-54, decoupled handover, manifest gate then reset, scoring async from the sealed snapshot, Class L score-before-reset as the only exception (9 tasks).
- Backpressure: re-plan line 259, "pause a runner when it has 2 unscored tasks AND the oldest lag exceeds 30 minutes (the conjunction is restored; lag alone does not pause)"; thu-tu-chay.txt line 54, max 2 unscored tasks per runner, pause if scoring lags over 30 minutes; re-plan line 314 checklist, "Backpressure enforced (2 unscored AND oldest lag over 30 minutes)". The two wordings agree in substance: the cap plus the 30-minute lag condition.
- G-50 bounded internal-watchdog gate (re-plan lines 21, 138, 215, 308): verify all 4 per-agent internal 10-minute watchdogs within 30 minutes of the start order; if any is missing at 30 minutes, the run starts anyway with the shared r3l3-agents-watch covering. This is verify-within-30-minutes, not wait-30-minutes, so there is no forced delay when all 4 verify quickly, and the worst case is a single pre-task-1 slip of at most 30 minutes, only if a watchdog is missing. No round-2 fix touched this gate.
- Interleaving rule unchanged (re-plan line 259): a scorer driving live for a Class L task pauses the other lane's runner. This is the only cross-lane serialization, and it applies to at most 9 tasks.

### 5. VERIFIED: no speed benefit was lost and no new bottleneck was introduced by the round-2 fixes

- The round-2 fix commit 82a9f49e touches 9 files, 48 insertions, 35 deletions. In speed terms the only behavioral change is the one-line O-1 fix in time-budget.md (item 1), which changes only the pause-release decision rule, read once at the 3rd graded task. It adds no per-task cost and removes a potential indefinite wait.
- The other round-2 fix changes are identity propagation and record corrections with no run-time cost: deputy id f41d8a84 propagated to the re-plan, state file deputy field, thu-tu-chay.txt line 38, and the deputy declaration; the word "authoritative" removed from the scorer addendum line 5 (R2-M2); the "(prepare baseline)" qualifier added to tip 81919c0c in thu-tu-chay.txt line 2 and du-phong.txt (R2-S3); the TB-B2 sign-off note (R2-S1) and the declaration pointer wording (R2-S2).
- The G-38 dry run was re-run by the new deputy itself in its own session, PASS 11:53 +07 (deputy-dry-run record, tail section: SSH via ssh-laptop.sh OK, tmux r3-fcc-runner-L3 alive, state file parse OK, git log tip b26a34c5). This proves the takeover path in the new deputy's own session, so a coordinator death mid-run does not stall on an unproven deputy. That closes round-2 redteam R2-M1, which is speed-relevant only as a stall risk, and it is closed.
- G-32 hash refresh is consistent: the state file round-2-fix note records thu-tu-chay.txt sha256 a759ad21 and du-phong.txt sha256 7d17b9b7, both recomputed live by this council and matched. No stale-hash pause can fire at the manifest gate.
- No new gate, no new ack round, no new wait was added by the round-2 fixes. Task 1 is not gated on any further round-2 item in the speed lens.

### 6. VERIFIED: the run can still finish within the budget with the corrected checkpoint

- The checkpoint is the only early warning that the run will overrun (time-budget.md lines 42-44, mandatory, never skipped). With the corrected trigger, the earliest it can pause the run is on a genuine overrun signal: a revised run-complete over 31h, or a per-class mean over its estimate by more than 25 percent with at least 3 graded tasks of that class. Neither can fire on the biased early sample. A 22-31h revised estimate continues with a recorded estimate, so the run does not lose its staffed 31h headroom to a spurious pause. The 3-hour fallback is a report, not a pause, so a slow start does not stop the run either. With O-1 fixed, a pause that does fire now has a bounded release: continue by default if the owner is unreachable within 30 minutes.
- The coordinator serial load (manifest gates, audits, ledger) is counted in the plan (re-plan F-24 line 170), with an audit-only second coordinator pre-authorized on a numeric trigger (more than 12 minutes serial time per graded task, or the manifest-plus-gate queue past 2 tasks), so a coordinator bottleneck has a pre-authorized relief valve instead of a mid-run decision delay.

## Non-blocking observation (does NOT affect the verdict)

### O-1 (round 3, wording asymmetry, no rule difference)

- Thu-tu-chay.txt line 54 states the backpressure cap (max 2 unscored per runner) and the 30-minute lag pause in two sentences, without restating the AND conjunction in one sentence the way re-plan line 259 does ("2 unscored tasks AND the oldest lag exceeds 30 minutes"). The substance agrees (cap plus lag condition, same numbers, same pause), and round 2 accepted the same two wordings. Rewriting thu-tu-chay.txt line 54 to restate the conjunction would change its sha256 and force another G-32 hash refresh for zero rule change. Suggested only as a future edit if thu-tu-chay.txt is touched for another reason, not required before task 1.

## Answers to the review questions

- Checkpoint trigger identical in all three places: yes, in substance, all four elements, item 2 above, with the precision note that the release default lives verbatim in re-plan line 269 and time-budget.md line 33 and is reached from thu-tu-chay.txt line 90 through its pointer to time-budget.md.
- Pause-release default aligned between re-plan line 269 and time-budget.md: yes, item 1 above, verified by the 82a9f49e diff, one line, old fail-closed wording gone.
- Round-2 Council 2 observation O-1 actually fixed: yes, item 1 above, file and line evidence, no round-2 speed item remains open.
- 19-31h budget holds after the DP-03 swap: yes, item 3 above, budget-neutral to slightly faster, 55 tasks, bar 53/55, 9 Class L / 46 Class S.
- Rolling release and parallel scoring hold: yes, item 4 above, two lanes, two scorer pairs, backpressure cap max 2 unscored per runner with pause on lag over 30 minutes.
- No speed benefit lost, no new bottleneck: yes, item 5 above, the round-2 fixes cost nothing per task and remove a potential indefinite pause and an unproven-deputy stall risk.
- Run can finish within budget with the corrected checkpoint: yes, item 6 above.

## What this council did NOT verify

- It did not independently re-verify the non-speed round-2 items R2-M2, R2-S1, R2-S2, R2-S3 word by word; those belong to Council 1, Council 3, and the redteam. It verified only their speed touchpoints: the addendum backup order (DP-06, DP-07, DP-03 USED, line 11) and the G-38 dry-run re-run PASS 11:53 (R2-M1), which is speed-relevant as a stall risk.
- It did not message any agent, so per-agent internal watchdog existence (mei, mochi, clone1, clone2) is not independently confirmed by this council. The G-50 gate is the check for that, and it runs at start.
- It did not re-run live cron.list or the G-35 live checks (Zen, BiDi, FCC tmux, daemon) from this VM. The pill path check report, the prepare report's G-34 evidence, and the lane-brief acks were verified as files in round 2, and the hashes and git state were verified live by this council in round 3.
- The R3-029 password value appears in no file this council read. Zero em dashes and zero en dashes in the three checkpoint files checked.
- Items outside the speed lens (deputy identity in full, scorer addendum wording, TB-B2 sign-off session id, tip qualifiers) are noted only where they touch speed; their own verdicts are for their councils.
