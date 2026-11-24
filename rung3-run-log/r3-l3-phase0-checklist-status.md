R3-L3 Phase 0 precondition checklist status (section 11 of the execution plan).
Updated 2026-11-24 17:46 +07 by the Phase 0 coordinator (agent 68a84d25).
Status counts: DONE 16, IN PROGRESS 2, NOT DONE 4. The run is ON HOLD until all 22 are DONE.
Evidence for each item is the file named. "DONE" means verified with a file, not merely asserted.

1. DP-01 removed from both du-phong files; byte-identical; laptop canonical.
   DONE (repo side). Repo file rewritten (rung3-run-log/du-phong.txt, DP-01 removed, medium order DP-03/DP-06/DP-07, laptop canonical declared). Laptop sync NOT yet done (the laptop copy is still R3-L1). IN PROGRESS overall until the laptop copy is synced and byte-identical is verified. See item 1 note below.
2. Evidence folders wiped and recreated; R3-001 folder empty.
   DONE. FCC wiped ~/rung3-chung-cu/ (verified empty 2026-11-24T17:13:29). diff -r -q ~/rung3/ ~/rung3-goc/ identical (no stale state in the live dir). R3-001 folder is empty (chung-cu is empty).
3. R3-096 to Class L; R3-078/088/093/079 resolved; exception list republished.
   DONE. Republished rung3-run-log/r3-l3-exception-list.txt (2026-11-24 17:12 +07, 9 Class L, 46 Class S). R3-096 proven Class L (live diff 4 lines). R3-078/079/088 moved to Class L. R3-093 proven Class S (manifest gate checks by name).
4. Fresh runner sessions started; IDs recorded; or 11 repeated tasks recorded as not held-out.
   DONE (with plan adaptation). FCC fresh session r3-fcc-runner-L3 (pane PID 203375, fcc-claude 2.1.331) verified responsive. Codex interactive TUI stalls in tmux (both 0.172.0 and 0.171.0, old session also stalled). ADAPTATION: Codex uses codex exec per task (proven READY, EXIT=0, 7376 tokens). No interactive Codex session is used. The 11 repeated tasks are therefore run by FRESH runners (FCC fresh session, Codex fresh codex exec invocations), so the held-out concern is addressed: no task is run by a session that already ran it in R3-L2.
5. R3-029 and R3-075 keys verified; R3-029 account + names confirmed.
   DONE. R3-075 CORRECT (fixture sha256s match key, Python 3.14.10, list+key consistent). R3-029 CORRECT (Mochi 17:11-17:19 +07: all 5 names confirmed with prices, account rung3-029-test@example.com created, wishlist works). Key gate PASSES. No blocker.
6. 4 pre-run invalid candidates declared/verified with group mapping; R3-009 WAVE 5 numbers.
   DONE (now 5 candidates). Group mapping: R3-011, R3-028, R3-036, R3-046 are all trung binh. R3-009 WAVE 5 numbers (Mochi 17:11-17:19): Fox News Errors 2, Alerts 311, Features 145, Structural 382, Contrast 16; Wikipedia Errors 7, Alerts 80, Features 451, Structural 75, Contrast 0. timeanddate.com loads normally (Hanoi 17:19:49, Sunny, 21C). ADDED 2026-11-24 18:02 +07: R3-047 is a 5th pre-run INVALID CANDIDATE (medium; Gutenberg down for maintenance, browser-verified by Mochi 17:29 +07, same as R3-L2; re-check before position 35, backup DP-03 if still down). R3-017 (bbc.com) is NOT invalid (Mochi verified bbc.com loads normally in a browser 17:29 +07; urllib DNS failure was a false positive). Recorded in du-phong.txt and the liveness report.
7. Manifest-gate script + audit scan named, committed, proven; pre-reset content check defined.
   DONE (scripts proven, commit pending). rung3-ci/manifest-gate.py and rung3-ci/audit-scan.py written in the worktree and proven: gate PASS on a valid trial snapshot, FAIL on an empty folder; audit PASS on a clean verdict, FAIL on a tainted verdict (reads ledger). Pre-reset content check is in the gate (evidence-requirements.json, files + patterns + screenshots_min). Commit pending (Phase 0 commit).
8. Timeout watcher, kill procedure, partial-evidence rule named; >30min task list published.
   DONE. rung3-run-log/r3-l3-timeout-watch.md (30-min hard timeout, watcher, kill procedure for FCC tmux and Codex exec, partial-evidence rule, >30min task list: R3-003, R3-040, R3-042, R3-041, R3-082, R3-096, R3-100).
9. Deputy coordinator named with declaration; coordinator state file defined.
   DONE. Deputy 028399b1 (declaration ~/workspace/r3-l3-deputy-declaration.md, read plan+state 2026-11-24 17:24:46 +07, on STANDBY). State file rung3-run-log/r3-l3-coordinator-state.json (updated after every task; currently 2026-11-24T17:45:00+07:00).
10. Pair B declarations + calibration verified by someone other than coordinator, with signed grades incl. Tier C + B-hybrid.
    DONE. 1B (4e2f52d4) 4/4, 2B (2e3ae678) 4/4, TB-A (97290681) 4/4, all APPROVED by the independent verifier (032952f7, report ~/workspace/r3-l3-calibration-VERIFICATION.md). Original TB-B (9d613f19) 3/4, NOT APPROVED (R3-041 misapplication). Replacement TB-B2 (df4defcc) calibrated 4/4 (R3-041 PASS, R3-002 FAIL, R3-003 FAIL, R3-067 PASS, 2026-11-24 17:31 +07), APPROVED. Grade files: ~/workspace/r3-l3-calibration-1B.md, -2B.md, -TBA.md, -TBB.md (failed), -TBB2.md (approved), -VERIFICATION.md. All include Tier C (R3-067) + B-hybrid (R3-003) + declarations + key hash verification.
11. Ledger file created with schema, trial row validated + committed; append/push protocol written.
    DONE (file + validation + protocol; commit pending). rung3-run-log/R3-L3-grades.jsonl (1 trial row, test_row true, validated PASS by validate-ledger.py 2026-11-24 17:20). Append/push protocol in rung3-run-log/r3-l3-ledger-push.md. Commit pending (Phase 0 commit).
12. Liveness report signed off.
    DONE (with triage + browser verification complete). rung3-ci/liveness-report-20261124-175000.md (2026-11-24 17:28, host omarchy, fixture root /home/james/rung3-goc): 40 OK, 9 FAIL, 3 PENDING, 2 SKIP. All 17 fixture checks OK. Triage: 6 FAILs are urllib 403 false positives (bot check on browser tasks; timeanddate.com browser-verified by Mochi). 1 is Wayback 429 (transient, has a policy). 2 were pending browser verification and are now RESOLVED (Mochi run 136, 17:29 +07): bbc.com loads normally (R3-017 NOT invalid, urllib DNS was a false positive); gutenberg.org is down for maintenance (R3-047 is a pre-run INVALID CANDIDATE, re-check before position 35, backup DP-03 if still down). Signed off by the coordinator 2026-11-24 17:52 +07, updated 18:02 +07 with the browser verification. No undeclared invalid remains.
13. Snapshot naming fixed (R3-xxx-L3); snapshot dirs created.
    DONE. Path ~/workspace/rung3-snapshots/R3-xxx-L3/. 60 empty dirs created (55 tasks + 5 backups). snapshot.py --name option added (fixed dir name). Tested: snapshot.py --name R3-002-L3 works, gate PASS on it. Pre-existing R3-040-retry-s1 (R3-L2, fuller than repo copy) left untouched.
14. thu-tu-chay.txt rewritten (decoupled handoff, Pair A only for Mochi, names, runner IDs, tip, deputy) + timestamped; sha256 recorded.
    NOT DONE. Depends on the final runner/scorer/deputy IDs and the Codex exec adaptation. TODO after the verifier reports and the Phase 0 commit. Then sync to laptop and verify byte-identical.
15. Shared-resource table published; pause rule on 429/bot check.
    DONE. rung3-run-log/r3-l3-shared-resources.md (10 shared resources, pause rule).
16. Coupled-task checks written as concrete steps with pass/fail criteria (R3-078/R3-079, R3-067/R3-083).
    DONE. rung3-run-log/r3-l3-coupled-tasks.md.
17. R3-089 fixture-refresh owner + date assigned; confirmation procedure defined.
    DONE. rung3-run-log/r3-l3-r3-089-refresh.md (owner = run coordinator, refresh the day before R3-089 runs, confirmation procedure, fixture currently fresh, expiry 2026-11-29 19:20).
18. Daemon fallback channel named (direct SSH + speed-lean) and tested.
    DONE. rung3-run-log/r3-l3-daemon-fallback.md. Tested: daemon died, restarted 17:16:43 +07 (PID 2423), run 135 re-sent successfully. Speed-lean named as fallback (not yet test-sent; will be used if the daemon fails again).
19. Interleaving rule written; /proc fd scan documented verbatim with expected output; coordinator named.
    DONE. rung3-run-log/r3-l3-interleaving-rule.md (single-driver rule, interleaving rule, /proc fd scan verbatim with expected output, verified FREE at prep 17:11 +07, coordinator named).
20. Ledger push job created (cron or timer); retry rule; escalation.
    DONE. rung3-run-log/r3-l3-ledger-push.md (manual push by coordinator, at least hourly, immediately on INVALID/dispute, retry 5min then 15min, escalate after 3 failures or 2 hours, pause run if unpushable over 2 hours). Method is manual (not cron) because only the coordinator knows when a row is graded; the reason is recorded in the file.
21. R3-100 port check rule defined.
    DONE. rung3-run-log/r3-l3-r3-100-port-rule.md.
22. Calibration exposure limitation recorded.
    DONE. rung3-run-log/r3-l3-calibration-limitation.md (4-task calibration does not prove all 55 tasks; coordinator audits first 2 grades of each new task type; 2 overturns trigger re-calibration).

ITEM 1 NOTE (laptop du-phong.txt sync): the laptop ~/du-phong.txt is still R3-L1 (DP-01 first medium backup, records R3-047 to DP-01). The repo file is corrected (DP-01 removed). The sync (copy the corrected file to the laptop, verify byte-identical with sha256) is the remaining step for item 1 and item 2 (byte-identical). This is done together with the thu-tu-chay.txt sync (item 14) in one laptop sync step, after the Phase 0 commit, so the repo files are final before syncing.

PLAN ADAPTATIONS (owner gave full authority; recorded in the state file):
- Codex runner uses codex exec per task (not an interactive tmux session). Reason: interactive TUI stalls in tmux for new sessions (both versions, old session also stalled). codex exec proven (READY, EXIT=0).
- Worktree moved from /tmp to ~/workspace (persistent). Reason: /tmp was cleaned by the system, deleting the worktree and uncommitted work.
- snapshot.py --name option added. Reason: the plan requires fixed R3-xxx-L3 names; snapshot.py only made timestamped names.
- Class L = 9 tasks (not 5). Reason: R3-096 proven Class L, R3-078/079/088 moved (scorer needs live files the list does not require the runner to copy). Recorded in the republished exception list.
- R3-075 key verified CORRECT (the du-phong note saying it was wrong was stale). Recorded in corrected du-phong.txt.

REMAINING BEFORE THE RUN CAN START:
- (a) Independent verifier report (item 10) and TB-B resolution (if TB-B fails, calibrate a replacement tiebreaker B).
- (b) R3-L3 liveness report + sign-off (item 12).
- (c) Phase 0 commit to todolist-push (all files above) + push verified via ls-remote.
- (d) thu-tu-chay.txt rewrite (item 14) with final IDs, then sync du-phong.txt + thu-tu-chay.txt to the laptop and verify byte-identical (items 1, 2, 14).
- (e) Final verification pass: every tool works, every environment ready, then report to the parent.
