Verdict: AGREE

# Final Prepare RE-REVIEW ROUND 2, Council 2 (Speed / Benefit), R3-L3, 25/11/2026

- Council: Council 2, speed and benefit lens, fresh reviewer, independent of round 1. This council did NOT write the original Council 2 verdict and did NOT write the round-1 re-review verdict. It verified the committed files itself and did NOT trust the coordinator's summary.
- Date: 2026-11-25, about 11:50 +07.
- Worktree: ~/workspace/r3l3-run-wt, HEAD 590be03c, git status clean, no uncommitted changes. Origin todolist-push verified via ls-remote = 590be03c.
- Files read in full and verified live: improvements/r3-l3-replan-final-20261124.md (worktree copy, operative, 363 lines), rung3-run-log/r3-l3-time-budget.md (49 lines), rung3-run-log/thu-tu-chay.txt (90 lines), rung3-run-log/r3-l3-coordinator-state.json, rung3-run-log/du-phong.txt, rung3-run-log/r3-l3-deputy-declaration.md, improvements/r3-l3-final-rereview-council-2-speed-20261125.md (round-1 Council 2 verdict, DISAGREE, single blocker B-1), improvements/r3-l3-final-rereview-council-1-stability-20261125.md, improvements/r3-l3-final-rereview-council-3-correctness-20261125.md, improvements/r3-l3-final-rereview-redteam-20261125.md, improvements/r3-l3-lane-brief-acks-round1-20261125.md, improvements/r3-l3-lane-brief-fcc-L3-20261125.md, improvements/r3-l3-lane-brief-codex-L3-20261125.md, rung3-run-log/scorer-briefs/rung3-scorer-brief-R3-L3-addendum.md, ~/workspace/r3-l3-execution-plan-20261124.md (577 lines, budget lines only).
- Live checks done by this council: git log (tip 590be03c, parent 4289e277, parent d4df3aa1), git ls-remote origin todolist-push = 590be03c, git show 4289e277 diff for time-budget.md and thu-tu-chay.txt, sha256sum of thu-tu-chay.txt (f739f22e137af0f307f4f814bcb0246110a724342cbc08b7c705a6110cd8a9ac) matching state file line 53, sha256sum of du-phong.txt (0cf06dda18cb32a47c99f5d5a4be67d8a8d5541d58c072f0f8e8df5c982f5619, unchanged), python token count of the thu-tu-chay.txt order line (55 tokens, token 34 is DP-03, R3-047 absent), grep for em dash and en dash in the three checkpoint files (0 in each).
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

Round 1 Council 2 had exactly one blocker, B-1: the checkpoint trigger was corrected in the re-plan only, while time-budget.md and thu-tu-chay.txt still carried the simplified overall-mean trigger that could fire a spurious pause on the biased early sample. That item is now VERIFIED FIXED in all three places, with identical trigger elements. The 19-31h budget holds after the DP-03 swap, the rolling-release and parallel-scoring design is intact, no round-1 fix introduced a new bottleneck, and the run can finish within budget with the corrected checkpoint. No round-1 speed item remains open. This council agrees.

## Numbered verification items

### 1. B-1 VERIFIED FIXED: the checkpoint trigger is now identical in all three places

The four required elements (per-class mean, at least 3 graded tasks of that class, 3-hour fallback, 22-31h continues) are present in each file:

- Worktree re-plan line 269: "The coordinator PAUSES and reports to the owner ONLY if the revised run-complete exceeds 31h (staffed ceiling) OR a per-class mean exceeds its estimate by more than 25 percent with at least 3 graded tasks of that class. A revised run-complete of 22-31h continues with a recorded estimate (no pause). The trigger does not fire on the biased early sample (R3-001 Class L serial plus R3-002 pilot) against a band the plan itself calls a lower bound. A 3-hour wall-clock fallback checkpoint is added (if the 3rd graded task has not landed by 3 hours after task 1, the coordinator reports to the owner)."
- rung3-run-log/r3-l3-time-budget.md lines 24-41: line 29-30, clause (b), "whether a per-class mean exceeds its estimate by more than 25 percent, with at least 3 graded tasks of that class"; lines 31-33, pause ONLY if the revised run-complete exceeds 31 hours OR a per-class mean exceeds its estimate by more than 25 percent with at least 3 graded tasks of that class; lines 35-36, "A revised run-complete of 22-31 hours continues with a recorded estimate (no pause)"; lines 39-41, "A 3-hour wall-clock fallback checkpoint is added: if the 3rd graded task has not landed by 3 hours after task 1, the coordinator reports to the owner." The old overall-mean clause and the 19-21h band are gone.
- rung3-run-log/thu-tu-chay.txt line 90: "Checkpoint sau task thu 3 duoc cham: dieu phoi vien TAM DUNG va bao chu so huu CHI NEU uoc tinh hoan thanh vuot 31h HOAC trung binh theo class vuot ke hoach hon 25% voi it nhat 3 task da cham cua class do; uoc tinh 22-31h thi chay tiep (ghi lai uoc tinh, khong tam dung); neu task thu 3 chua duoc cham sau 3 gio ke tu task 1 thi bao chu so huu. Xem rung3-run-log/r3-l3-time-budget.md." Same four elements in short form, still pointing at time-budget.md, which now carries the same trigger, so the pointer no longer resolves to a different rule.
- Commit evidence: git show 4289e277 shows the exact diff for both files (time-budget.md lines 24-41 rewritten, thu-tu-chay.txt line 90 rewritten). The hash discipline was followed: the edit changed the thu-tu-chay.txt sha256, and the state file line 53 records the new hash f739f22e137af0f307f4f814bcb0246110a724342cbc08b7c705a6110cd8a9ac, which this council recomputed live and matched. du-phong.txt hash 0cf06dda18cb32a47c99f5d5a4be67d8a8d5541d58c072f0f8e8df5c982f5619 is unchanged and also matches. Re-plan line 43 carries the same summary, so the plan and its two working references agree.
- Why the trap is closed: the trigger cannot fire on the first 3 graded tasks as an overall mean, because the per-class clause requires at least 3 graded tasks OF THAT CLASS, and the first 3 graded tasks cannot supply 3 of one class on the biased early sample (R3-001 Class L serial plus R3-002 pilot). A 22-31h revised estimate continues with a recorded estimate instead of pausing. The 3-hour fallback reports to the owner rather than pausing, so a slow start costs a report, not a run stop.

### 2. VERIFIED: the 19-31h budget still holds after dropping R3-047 and inserting DP-03

- The run is still 55 tasks, bar 53/55, class mix 9 Class L and 46 Class S, difficulty mix medium 37, hard 11, very hard 7, all unchanged (thu-tu-chay.txt lines 6 and 8, re-plan line 6, state file). DP-03 is a terminal task (one ss -tlnp run plus a report, thu-tu-chay.txt line 74: N = 5, n_min 3) versus R3-047 a 3-book browser search, so the swap is budget-neutral to slightly faster. No per-task minute estimate exists for either task in any file, so no larger saving is claimed. The 19-31h honest range appears identically in re-plan line 275, time-budget.md lines 4-7, and thu-tu-chay.txt line 90, all staffed for 31h and measured from task 1 start (re-plan line 105, line 275).
- The scorer addendum backup order now reads "Medium backups in order: DP-06, DP-07" with DP-03 marked USED at position 34 (addendum lines 11-13 and 46-48), so no mid-run backup assignment can stall on a consumed DP-03. The G-47 script check (unused, same difficulty, not DP-01) is the backstop, but the doc itself is now correct.
- The 4-task shared-cause scenario (R3-011/028/036/046) is a table lookup, valid 53, bar 51/53, notify not stop (re-plan G-46 line 137, du-phong.txt line 38, addendum lines 47-48). It adds no scoring delay and no run stop. Per the brief, this decision is not blocked on.

### 3. VERIFIED: the rolling-release and parallel-scoring design still holds

- Two lanes, two scorer pairs: FCC positions 1-28 with Pair A (Mochi scorer 1, dc7e0d0d scorer 2, TB-A tiebreaker), Codex positions 29-55 with Pair B (1B, 2B, TB-B2), in thu-tu-chay.txt lines 16-31 and the addendum lines 8-9. No lane or pair changed in the round-1 fixes.
- Rolling release: re-plan line 259, Phase 1, "rolling release (the next task starts as soon as its evidence is locked, score in parallel behind it)"; thu-tu-chay.txt lines 48-54, decoupled handover, manifest gate then reset, scoring async from the sealed snapshot, Class L score-before-reset as the only exception (9 tasks).
- Backpressure: thu-tu-chay.txt line 54, max 2 unscored tasks per runner, pause if scoring lags over 30 minutes; re-plan line 259, the conjunction is restored (pause a runner when it has 2 unscored tasks AND the oldest lag exceeds 30 minutes; lag alone does not pause). The two wordings agree in substance: the cap plus the 30-minute lag condition.
- G-50 bounded internal-watchdog gate (re-plan line 21 section 0A, line 138, line 215): verify all 4 per-agent internal 10-minute watchdogs within 30 minutes of the start order; if any is missing at 30 minutes, the run starts anyway with the shared r3l3-agents-watch covering. This is verify-within-30-minutes, not wait-30-minutes, so there is no forced delay when all 4 verify quickly, and the worst case is a single pre-task-1 slip of at most 30 minutes, only if a watchdog is missing. No round-1 fix touched this gate.

### 4. VERIFIED: no speed benefit was lost and no new bottleneck was introduced by the round-1 fixes

- The checkpoint fix itself adds no per-task cost: it changes only the pause decision rule, read once at the 3rd graded task.
- Zen move to ws2 (redteam N-01) is a one-time coordinator start item (re-plan section 0A, line 18: "The Zen run tab lives in ws2, never ws3"; the move command and the verify-before-task-1 guard are documented as a coordinator start item, Zen is NOT moved before the run starts). It costs minutes once, before task 1, and it removes the known failure where a ws2 drive instruction fails while Zen sits on ws1.
- Grim/finish lines in both lane briefs (redteam N-02, FCC brief line 74, Codex brief line 92): one grim screenshot plus one finish per task, seconds per task, and they prevent the stuck-pill and leftover-session stalls that cost far more (the FCC leftover session blocked Codex attempt 1 in the pill path check).
- Fresh lane-brief acks are in (acks-round1 file): FCC 11:36 +07 with follow-up confirmation 11:39, Codex 11:37:33 +07, each naming all three re-issued amendments and confirming no start until assigned. No re-ack round is outstanding, so task 1 is not gated on another ack cycle.
- The Codex OpenRouter carve-out parenthetical (Council 1 A-09, Codex brief line 97) and the FCC carve-out remove a false-violation flag that could otherwise have paused a lane mid-run. The ban still covers only Opencode, per the owner's 25/11 decision.
- TB-B2 sign-off timestamp (N-06) and the bar pattern in G-46 (N-04) are record corrections with no run-time cost.

### 5. VERIFIED: the run can still finish within the budget with the corrected checkpoint

- The checkpoint is the only early warning that the run will overrun (time-budget.md lines 42-44, mandatory, never skipped). With the corrected trigger, the earliest it can pause the run is on a genuine overrun signal: a revised run-complete over 31h, or a per-class mean over its estimate by more than 25 percent with at least 3 graded tasks of that class. Neither can fire on the biased early sample. A 22-31h revised estimate continues with a recorded estimate, so the run does not lose its staffed 31h headroom to a spurious pause. The 3-hour fallback is a report, not a pause, so a slow start does not stop the run either.
- The budget arithmetic is unchanged from round 1: 55 tasks at about 21 minutes mean cycle time is 19h, at about 34 minutes is 31h (time-budget.md lines 10-13), with up to 3 timeouts at 30 minutes each already inside the 31h figure (lines 19-21). The coordinator serial load (manifest gates, audits, ledger) is counted in the plan (execution plan line 471, re-plan F-24 line 170), with an audit-only second coordinator pre-authorized on a numeric trigger (more than 12 minutes serial time per graded task, or the manifest-plus-gate queue past 2 tasks), so a coordinator bottleneck has a pre-authorized relief valve instead of a mid-run decision delay.

### 6. VERIFIED (start-gate note, speed scope only): the round-1 remaining blocker, the deputy re-confirmation, is closed

- Fresh deputy session 6f9f3647, declaration timestamp 2026-11-25 11:43:12 +07, commit 590be03c, verified via ls-remote: origin/todolist-push now = 590be03c. The declaration certifies the FINAL committed worktree re-plan 4289e277, R3-029 FCC position 25, the chain-broken AND rule, and R3-047 dropped with DP-03 at position 34. Its timestamp (11:43:12) is after the last state-file update (2026-11-25T11:33:08+07:00), so it satisfies G-24 ordering.
- The state file deputy field still names the previous session 8397cff5. This is documented and intentional: the declaration states the run coordinator updates that field when starting task 1, and the deputy does NOT edit the state file itself because editing would move last_updated after its confirmation timestamp and break the ordering it certifies. This is a start item, not a defect, and it costs no run time.

## Non-blocking observation (does NOT affect the verdict)

### O-1. Pause-release default differs between the re-plan and time-budget.md

- Re-plan line 269 ends the checkpoint paragraph with a pre-authorized default: if the owner is unreachable within 30 minutes, the default is continue, record the estimate, and re-check at the next milestone.
- Time-budget.md line 33 says "The run continues ONLY on the owner's decision," with no 30-minute default.
- The trigger itself (what fires the pause) is identical in both files, so this does not reopen B-1. The difference is only on the release path after a pause has fired. The time-budget version is the conservative one (fail-closed: a pause waits for the owner), and the owner is reachable by phone, so the worst case is a wait, not a wrong continuation. Suggested fix at the next edit, not required before task 1: add one line to time-budget.md aligning the release default with re-plan line 269, or delete the default from the re-plan if the owner prefers fail-closed. Either way, one line, no run-design change.

## Answers to the review questions

- Checkpoint trigger identical in all three places: yes, all four elements, item 1 above, with file and line evidence and the 4289e277 diff.
- 19-31h budget honest after the DP-03 swap: yes, item 2 above, budget-neutral to slightly faster.
- Rolling release and parallel scoring hold: yes, item 3 above, two lanes, two scorer pairs, backpressure cap max 2 unscored per runner with pause on lag over 30 minutes.
- No speed benefit lost, no new bottleneck: yes, item 4 above, the round-1 fixes cost seconds per task or minutes once before task 1, and they remove known stall modes.
- Run can finish within budget with the corrected checkpoint: yes, item 5 above, the trigger cannot fire spuriously on the early sample and the 22-31h band continues.

## What this council did NOT verify

- It did not message any agent, so per-agent internal watchdog existence (mei, mochi, clone1, clone2) is not independently confirmed by this council. The G-50 gate is the check for that, and it runs at start.
- It did not re-run live cron.list or the G-35 live checks (Zen, BiDi, FCC tmux, daemon) from this VM. The pill path check report, the prepare report's G-34 evidence, and the acks-round1 file were verified as files, and the hashes and git state were verified live by this council.
- The R3-029 password value appears in no file this council read. Zero em dashes and zero en dashes in the three checkpoint files checked.
- Items outside the speed lens (Council 1 RB-1/RB-2, Council 3 amendments, redteam N-01/N-03/N-04/N-05/N-06 in their own lenses) are noted only where they touch speed; their own verdicts are for their councils.
