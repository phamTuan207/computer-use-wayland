# Council Voice 3 verdict: Worker F3 Marionette slot recurrence

Verdict: AMEND

Reviewer: Council Voice 3 (next step + restart decision).
Scope: Worker F3 log `improvements/worker-f3-marionette-slot-log.md` and error file `~/workspace/cf26-upload/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md` entries J3 (updated), J22, J23, J24.
Branch: todolist-push. Note on HEAD: the task brief cited HEAD 6fb966f. At review time HEAD is 3b37df1. Git log confirms 6fb966f is F3's commit "log recurrence + zombie diagnosis + fix attempts (22:57-23:02)". The log content reviewed matches that commit. No defect in F3's work, recorded only.
Owner: referred to here as the owner, per repo-facing rule. No personal info in this file.

## Summary

F3's next step, report the recurrence to Muse and await direction for a restart, is the right step. The evidence is sufficient for Muse to authorize the second restart now, with conditions. The AMEND corrections below are required before or with that authorization: a pre-restart baseline check, a post-restart verification list, a ban on repeating the cleanup method that likely re-wedged the slot, a downgrade of the zombie-cause claim from proven to hypothesis, and a report to the owner now framed as FYI only, with no decision asked of the user.

## 1. Next step judgment

"Report to Muse and await direction" is correct, and F3 should NOT have restarted already.

- The brief reserves the restart decision to Muse: restart is the last resort and needs Muse's explicit direction. F3 obeyed it. Log verification status 23:02 states the restart is the proven fix awaiting direction and was NOT done on F3's own.
- The 22:25 authorization covered a restart when the browser was unusable. Log 22:25-22:27 records the owner redirect as Zen unusable, restore it. The situation now is different: the browser is usable. BiDi works (22:58:05, 15 tabs listed; 22:58:17, YouTube activated) and the UI works (23:00:03, Welcome tab clicked in 28ms, page rendered). Only Marionette session creation is broken. The old authorization does not clearly cover this narrower case, so F3 was right to stop and escalate rather than self-authorize.
- F3 also stopped correctly after the X-click miss. Log 23:01:53 records the X-click closing the wrong tab (a sacrificial blank) because sidebar rows had shifted, and UI-close attempts were stopped for rising misclick risk near real tabs. That is good judgment, not a gap.

## 2. Restart authorization: what is proven, what is unproven, risks

### Proven

- P1. The slot re-wedged and is not transient. Four POST /session failures with the same HTTP 500, browserElement is null, at 22:56:12, 22:56:31, 23:00:24, 23:02:04. Log event table and verification status 23:02.
- P2. BiDi and the browser UI still work. Evidence in section 1 above.
- P3. A dead tab element exists. Three-way evidence: BiDi tree 22:58:05 lists 15 contexts with no example.com; sidebar observe 22:59:13 shows an "Example Domain" row selected with a page rendered; click on that row 23:01:10 falls back to the neighboring "New Tab" instead of selecting it. The UI list and the BiDi list disagree, which is the zombie signature.
- P4. Three non-restart fixes failed. BiDi activate YouTube 22:58:17, mouse click on Welcome 23:00:03, UI X-close attempt 23:01:53. Retries after each still failed (23:00:24 after the click, 23:02:04 after the X attempt).
- P5. A Zen restart fixed the same error once. pkill -TERM 22:36:24, relaunch via zen-ai 22:36:48 (new PID 426338), session created in 0.1s at 22:37:32, 67 tabs listed. Elapsed from kill to working session: about 68 seconds.
- P6. The first restart's cost is known and small: one tab lost (the LMS login page opened about 22:26, never flushed to sessionstore) and 39 fixture tabs resurrected because sessionstore 22:04 predated the pass-1 cleanup. Log 22:38:32 and verification status 23:02.

### Unproven

- U1. The zombie cause. J3 and J22 state as fact that closing a BiDi-navigated tab with Marionette DELETE leaves the zombie. The log itself at 22:56 labels this a hypothesis, "to be proven by BiDi diagnosis + a click/activate test". The supporting evidence is strong (the Example Domain tab was the only BiDi-navigated tab among the 3 tabs close3 closed at 22:56:01; Bug 1342723 says removeTab sets linkedBrowser to null; the source at driver.sys.mjs lines 4616, 4640, 2707 shows one null browser kills newSession). Strong is not proven. The DELETE-to-removeTab path is not source-proven. See correction C5.
- U2. What a second restart will restore. The task brief asserts the current 14 real tabs would restore from the latest sessionstore flush. That is unproven. The log at 22:36:24 records that sessionstore was NOT rewritten on clean exit (recovery.jsonlz4 still 22:04). No flush time after 22:36 is recorded in the log. The restore set could include the 39 fixture tabs again, or could miss tabs opened since the last flush. See correction C2.
- U3. That a second restart clears this zombie. Inferred with high confidence, not directly proven. The first restart cleared the first zombie by rebuilding the tabbrowser fresh, and the mechanism is identical, but this zombie was created by a different path (close3 DELETE) than the first (suspected pass-1 teardown). The post-restart verification list in section 4 must confirm it.
- U4. The trigger of the first wedge (22:03 to 22:06 change). Log root-cause section states it is still unproven. Not blocking for the restart decision.

### Risks of a second restart

- R1. Fixture resurrection. If the latest flush predates the 22:54 cleanup, the 39 fixture tabs come back and cleanup must be redone. Mitigated by C4.
- R2. Loss of tabs opened since the last flush. Precedent: the LMS login page in the first restart. Mitigated by C2 baseline, which names what is at stake.
- R3. Zen fails to relaunch. Low: the 22:36 relaunch worked first try, ports 2828 and 9222 listening.
- R4. The restart-cleanup loop. This is the largest risk. If fixtures resurrect and F3 re-runs cleanup_full with Marionette DELETE, the same wedge can recur a third time. The loop breaks only if the procedure change in log open item 4 is enforced. Mitigated by C4.
- R5. Zombie survives the restart. Low, per U3 reasoning, but must be verified, not assumed. Mitigated by V5.

### Non-restart fixes: none remains with a real chance

Exhausted and failed: BiDi activate a real tab, mouse click on a real tab, UI X-close on the zombie row. Each is logged with time and outcome (section 2, P4).

One untried attempt exists but I rule it out: a fresh-observe, immediate X retry on the zombie row. Against it: the click on the zombie row at 23:01:10 proved the row's handler is dead (Zen fell back to the neighbor tab), so the X on the same dead element is likely also dead; and the 23:01:53 misclick already demonstrated the misclick risk near real tabs. The proven restart costs about 68 seconds. A low-chance X gamble with misclick risk is worse than the restart. Do not retry the X-close. See C7.

Two other ideas have no chance and are recorded so they are not re-proposed: BiDi close cannot target the zombie because it has no browsing context and does not appear in the BiDi tree; opening a new window cannot help because newSession enumerates every window and every tab (driver.sys.mjs line 2707), so the zombie is hit regardless.

## 3. Escalation judgment

Muse should report this recurrence to the owner now, in main chat, as FYI only, with no decision asked of the user. Do not wait until morning.

- For reporting now: the 23:01 instruction in the log says big errors, blockers, and things needing the user's decision get reported at once, not next morning, even though the user is asleep since about 22:27. This recurrence is a big blocker: it gates the Y13 and Y14 live runs, which need the Marionette slot. Waiting until morning would hide an overnight stall and violate the standing report-blockers-early rule (error file A5).
- For FYI only, no decision asked: no owner decision is needed tonight. Restart authorization is Muse's call under the brief, and the procedure change is internal. A message that asks the user to decide would wake the user for a decision the user delegated. The message must state plainly: slot re-wedged at 22:56:12, restart authorized by Muse, outcome to follow in the morning report, no action needed from the user.
- If the restart fails or Zen does not relaunch, that becomes a new fact for the morning report, and still needs no owner action overnight unless Muse finds a step only the user can do.

## 4. Post-restart verification steps (exact, in order)

Run these before any cleanup or live run. Log each with wall-clock time.

- V1. POST /session creates in under about 5 seconds (first restart: 0.1s). Log the session id and time.
- V2. Tab list by URL shows the 14 real tabs: YouTube, Reddit, Todoist, Gmail, Calendar, Muse, PCCV CF26, Free Claude Code Admin, Welcome, Polygon, codeforces, chunkbase, duck.ai, BytePlus. Count fixture tabs separately. Expect 0 unless sessionstore resurrected them; if any resurrected, list them by title and do not proceed to cleanup until C4 is applied.
- V3. BiDi navigate a sacrificial tab to example.com and confirm title "Example Domain". Same test as the 22:40 PASS.
- V4. Mouse click on a real tab row (Welcome) and confirm selection plus content rendered. Log ms and miss. First restart baseline: 29ms, 1.0px miss.
- V5. Confirm no zombie row: the sidebar tab list matches the BiDi context list, and no "Example Domain" row remains.
- V6. Only after V1 to V5 pass, declare the slot fixed and unblock Y13/Y14. Log the declaration with time.

## 5. Corrections required (the AMEND list)

- C1. Muse authorizes the second restart now, not held to morning, using the same method as 22:36 (pkill -TERM, relaunch via the zen-ai wrapper, detached). Evidence P1 to P5 meets the threshold. Delay only blocks Y13/Y14 overnight with no benefit.
- C2. Before the restart, capture the baseline: a BiDi tab list with URLs (expected: 14 real tabs plus 1 zombie element visible only in the sidebar) and the recovery.jsonlz4 mtime, logged with wall-clock time. This closes U2 before the restart changes the state.
- C3. After the restart, run V1 to V6 in order before any cleanup or live run.
- C4. If fixture tabs resurrect, do NOT re-run cleanup_full or close3 with Marionette DELETE. Close resurrected tabs via the UI or via BiDi close only, per log open item 4. Never close a BiDi-navigated tab with Marionette DELETE. Accept 1 leftover sacrificial blank, per J24.
- C5. Downgrade the zombie-cause claim in J3 and J22 from proven to hypothesis, with the supporting evidence listed (only BiDi-navigated tab among close3's 3; Bug 1342723; driver.sys.mjs lines 4616, 4640, 2707). Keep the procedure change in C4 as a precaution, not as a proven root cause, until the DELETE-to-removeTab path is source-proven.
- C6. Report the recurrence to the owner now in main chat as FYI only, per section 3. No decision asked, no action needed from the user.
- C7. Do not retry the X-close on the zombie row. Ruled out in section 2 with reasons.

## 6. Findings list

- F1. Recurrence proven, non-transient. Evidence: 4 failures, 22:56:12, 22:56:31, 23:00:24, 23:02:04, same HTTP 500. Log event table, verification status 23:02, J22.
- F2. First restart is a proven fix for the same error. Evidence: kill 22:36:24, relaunch 22:36:48 PID 426338, session 0.1s 22:37:32, 67 tabs. Log event table, J3.
- F3. Zombie identified with three-way evidence. Evidence: BiDi 22:58:05 (no example.com among 15 contexts), sidebar 22:59:13 (Example Domain row present), click 23:01:10 (falls back to neighbor). Log event table, J22.
- F4. Non-restart fixes exhausted. Evidence: BiDi activate 22:58:17, mouse click Welcome 23:00:03 (28ms), X-click 23:01:53 (closed wrong tab, sacrificial blank). Log event table, J22.
- F5. F3 correctly did not restart alone. Evidence: brief reserves restart to Muse; 22:25 authorization covered an unusable browser; browser is usable now (BiDi plus UI). Log 22:25-22:27, verification status 23:02.
- F6. Zombie-cause claim is overstated in J3 and J22. Evidence: log 22:56 labels it a hypothesis "to be proven"; J3 and J22 state it as fact. Correction C5.
- F7. Restore set for a second restart is unknown. Evidence: log 22:36:24 records recovery.jsonlz4 still 22:04 after clean exit, not rewritten. The brief's assertion that the 14 real tabs would restore is unproven. Correction C2.
- F8. Restart-cleanup loop is the largest risk. Evidence: first restart resurrected 39 fixture tabs (log 22:38:32); cleanup redo at 22:54-22:56 preceded the re-wedge at 22:56:12. Correction C4 breaks the loop.
- F9. The X-close retry is the only untried non-restart attempt and should not be tried. Evidence: row handler dead per 23:01:10 click fallback; misclick demonstrated 23:01:53; restart costs about 68 seconds. Correction C7.
- F10. Escalation now as FYI is required by the 23:01 instruction and gates Y13/Y14, but no owner decision is needed. Evidence: log 23:01 line, error file A5. Correction C6.
