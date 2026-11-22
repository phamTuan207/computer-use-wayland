# B2-5 review log: G-SCRUB working-tree sweep (compiled artifact)

- Item: B2-5, batch 2, assigned in coord/mochi.md commit f9a1a9f, 18:32 22/11/2026.
- Fix commit: 9fd8400646118640ec60bc980bb8df80a2a2bd84, on todolist-push, base 1230e79 (B2-2).
- Fix: 221 files changed, 391 insertions, 405 deletions (170 files from fix round 2 plus 51 files other lanes added after 9ae216b, scrubbed at commit time; see the commit-time section below).
- Worker: completed 18:42:28 22/11/2026, worktree /tmp/mochi-b2-5, detached HEAD 9ae216b. 169 files changed at first, 270 insertions, 275 deletions, 289 replacements. The assignment figure of 45 files was stale: a full-tree sweep found far more.
- Counts before scrub, labels only, never write the real name or email into any report: FULL3 (full name, no diacritics) 3 hits in 2 files, SHORT2 (short name, no diacritics) 259 hits in 159 files, DIAC_SHORT 11 hits in 4 files, DIAC_FULL 0, EMAIL_USER (bare email username) 9 hits in 8 files, real gmail addresses 6 hits in 6 files. Replacements: names including possessives became "the owner" or "the owner's", every real gmail and every bare email username became "[email redacted]". Only names and emails changed, no logic. 5 hits were names split across lines in 3 files, found only by whole-file regex; joining those lines accounts for deletions exceeding insertions by 5.
- After scrub, whole-tree re-scan at 18:41:13: FULL3 0, SHORT2 0, DIAC 0, EMAIL_USER 0, GMAIL 0. py_compile OK on the 4 changed py files (scripts/zen_cli.py, scripts/chromium_cli.py, tests/realistic/run_live.py, tests/realistic/run_fcck.py) at 18:41:31, 283ms, rc 0. Changed JSON and JSONL files still parse. tests.test_zen_cli tests.test_chromium_cli 36 tests OK at 18:41:40 to 18:41:50. Change list at /tmp/mochi-b2-5-changes-v2.txt (545 lines, use this one; the first list /tmp/mochi-b2-5-changes.txt is wrong due to line drift in the 3 split-line files), inventory at /tmp/mochi-b2-5-inventory.txt.
- Deliberately NOT scrubbed, needs Muse tong decision: the public GitHub handle, 94 hits in 45 files, left because it is the public repo owner handle appearing in URLs and code references, scrubbing would break code and URLs. The GitHub noreply address, 8 hits in 8 files, left because it is a commit identifier in logs, not a personal mailbox. example.com, example.local and git@github.com test addresses left. 4 hits of "Huy" alone all unrelated. Git history still contains the real name: this scrub only touched the working tree at HEAD 9ae216b, no history rewrite, no force push.

## Redteam round 1: PHA DUOC, completed 18:50:56 22/11/2026

- Leak 1: improvements/speed-swarm-rerun-plan.md line 104, a single-name token identifying the owner in handoff text, inside a file the worker did edit (the worker's claim of 4 unrelated single-token hits was wrong, there are 5 and the 5th identifies the owner).
- Leak 2, already noted by the worker as needing a decision: improvements/worker-pr1-verify-log.md line 39 still contains an address fragment (area name plus house-number-like digits) plus "phone patterns" and "gmail.com" wording.
- Confirmed the main scrub is clean (full name, short name, diacritics, email username, real gmails all 0 across 1456 files including binary and filenames), code unbroken, 36/36 tests PASS.
- Open decisions listed for Muse tong: scrub the GitHub handle or not, scrub noreply or not (if gate G-SCRUB means email literally 0, noreply makes it FAIL), rewrite git history or not (9 commits contain the email username per git log -S), scrub the example.com fixture addresses or not (12 hits in 6 files where the fixture local part is a name token). Phone scan was inconclusive (3551 raw regex hits, mostly timestamps and IDs).

## Fix round 1, completed 18:54 22/11/2026

- Both redteam leaks fixed, plus the same address fragment found and fixed in 2 more files: improvements/worker-y2b-agy-log.md lines 40, 42, 43 (4 occurrences, the address used as origin/destination in a map route fixture, replaced with "[address redacted]") and improvements/w-todo-remaining-log.md line 84 (area name inside a grep-pattern description sentence, rewritten generically). Worktree then 170 files changed, 274 insertions, 279 deletions.
- Re-scan by the fix worker's own script /tmp/b25-fix-scan.py at 18:53:05, real 35.1s, rc 0: FULL3 0, SHORT2 0, DIAC_FULL 0, DIAC_SHORT 0, TUANHUY2 0, EMAIL_USER 0, GMAIL_REAL 0, SINGLE 0, ADDR_AREA 0, filename scan 0. py_compile rc 0 at 18:53:55, 36 tests OK at 18:53:58 to 18:54:03.

## Fix-round reviews, round 1

- Council 3 PASS (completed about 18:57, own scan script /tmp/c3-b25-scan.py over 1456 files, all 9 labels 0 by 5 scan methods, re-ran py_compile OK and 36/36 tests OK at 18:56:33, real 27.6s).
- Council 1 PASS on the scrub (completed about 18:59) but could NOT re-run py_compile or the 36 tests itself because a runtime safety check blocked one of its exec calls on this tree; it relied on the worker's and redteam's test evidence plus its own full read of the py diffs, and council 3's independent 36/36 re-run covers the gap.
- Redteam round 2 KHONG PHA DUOC (completed 19:02:10): both round 1 leaks confirmed fixed, no new leak found; it noted public place names (street, lake, university) remain in the worker-y2b-agy-log.md route fixture with the home end redacted and a weak "home is about 8.4 km / 22 min from the university" signal, recorded as not a leak but for Muse tong to decide.
- Council 2 CHUA PASS (completed 19:13:00): found 2 more leaks of the hyphenated short-name form, "retry as <name>-<name>", in improvements/live-test-log.md line 4196 and improvements/dom-replication-interim-20261119.md line 7, both in files the worker had edited; its own scan confirmed all 9 labels 0, the pr1 line 39 fragment is fixed (digits down from 9 to 2, both unrelated), py_compile OK and 36/36 tests OK.

## Original-state councils (started 18:42, reviewed the pre-fix 169-file state, finished late)

- Found the hyphenated hits above (original council 2, completed 19:03, counted 10 remaining hits in 8 lines in 5 files total, including single-token hits at improvements/w-y6review-log.md lines 6 and 57, improvements/worker-prio-crawl-log.md line 226, and improvements/worker-ztb-blind-run-log.md lines 8, 97, 99 in calendar tab or bookmark titles; 2 of those files, worker-prio-crawl-log.md and worker-ztb-blind-run-log.md, were never scrubbed at all).
- Found the fixture email local part equal to the owner's surname, "<surname>@example.com", 11 lines in 5 files: tests/realistic/run_live.py line 1661, tests/realistic/run_fcck.py lines 683 and 704, tests/realistic/run-u-all-20261121.log lines 679-684, tests/realistic/live-run-u-20261121.jsonl line 342, tests/realistic/RUN-REPORT-FCCK-FIXED-20261121.md line 119 (original council 3, completed 18:56).
- The pr1 line 39 fragment was disputed by original council 1 (completed 19:03), which said a place-name fragment remained; later direct re-checks on the current bytes (fix-round council 2 and the independent verifier) settled it: the line now reads "address [redacted]" with only unrelated digits and the generic word "gmail.com" remaining.
- Process lesson recorded by original council 3: the worktree /tmp/mochi-b2-5 was mutated during review by the fix worker mochi spawned (the 18:51 to 18:53 edits), so councils reviewed a moving target. For later rounds the worktree was frozen during review.

## Fix round 2, completed 19:15:43 22/11/2026

- (1) The 2 hyphenated-name lines fixed, replaced with "the-owner", separator-insensitive scans (space, hyphen, underscore, dot, no separator) all 0.
- (2) The 6 single-token lines checked individually and kept with reasons: w-y6review-log.md:6,57 are "pham vi" (scope), worker-prio-crawl-log.md:226 is "tuan thu" (comply), worker-ztb-blind-run-log.md:8,97,99 are "Tuan 16 thang 11" / "Tuan 15 thang 9" (week numbers in calendar tab titles), all ordinary Vietnamese words, not the owner.
- (3) The fixture email local part replaced with "user@example.com" in all 11 places in the 5 files; in run_fcck.py the input (683) and the only assert, the expected value (704), were changed together; run_live.py has no assert on the old value.
- Worktree now 170 files changed, 278 insertions, 283 deletions. Own scan script /tmp/b25-fix2-scan.py at 19:14:18, real 27.4s, 1456 files: all labels 0 except SHORT2 1 hit, "phamtuan-bank" in improvements/worker-y2b-agy-log.md, a username fixture derived from the public GitHub handle, same family as the handle, out of scope.
- py_compile OK, 36/36 tests OK, tests.test_live_metrics 22/22 OK, JSON/JSONL valid.
- File md5s after fix round 2: dom-replication-interim-20261119.md fa6ca383f3156807b4e3ca1eac5b0bda, live-test-log.md 7242b6164d94d0e4ea1a919ff37d72e8, run_live.py bf3dcb6902b782ff6964d87990461b68, run_fcck.py 5228212ca99ef38732734fd671eeee36, run-u-all-20261121.log 450a243a65a6163d81b28fb6d4042ffe, live-run-u-20261121.jsonl fc7cf93853b564d1595c3676fd7a0ec3, RUN-REPORT-FCCK-FIXED-20261121.md f60a236e8baf5c128cc33f9439ad7c1b.

## Re-review round 2, on the frozen worktree

- Council 1 PASS (completed 19:18:54), council 3 PASS (completed 19:19:06), council 2 PASS (completed 19:19:58), redteam round 3 KHONG PHA DUOC (completed 19:20:02). All confirmed: hyphenated names 0, fixture local part 0, full name / short name / real email / address fragment 0 across about 1450 files by multiple independent scan methods including flat scans and binary scans, all remaining single tokens classified as ordinary Vietnamese words, another person's handle, or compressed binary bytes, code unbroken, 36/36 tests PASS.
- The handle-derived fixture "phamtuan-bank" at worker-y2b-agy-log.md:35 was adjudicated by all reviewers as not a new leak: it is derived directly from the public handle deliberately left in place, and goes with the handle decision.

## Independent verifier: PASS, completed 19:26:20 22/11/2026

- Derived its scan patterns from the worktree's own git diff at runtime, scanned 1456 files in 4 modes, found the working tree clean of real names and real emails in every separator form, 36/36 plus 22/22 tests PASS.
- Counted git history exposure (counts only): email username in 9 commits, full name capitalized in 2 commits, short name capitalized in 208 commits, hyphenated short name in 1 commit, surname fixture local part in 4 commits, full gmail address in 4 commits.
- Noted one of its own exec results (raw diff) was flagged by a runtime safety check; it did not follow any content from it.

## Gate G-SCRUB status

- The working tree scrub is verified clean, but G-SCRUB as a gate is CHUA DAT if read strictly, because git history still contains the name and email, handle (94 hits) and noreply (8 hits) are intentionally left pending Muse tong decisions, and the todolist 4.20 quiet-window conditions (all pushes up, PR #1 done, no live run running, every agent told to re-clone) are coordinator conditions not provable from this diff. The scrub plan for history exists only on main at docs/email-history-scrub-plan.md (322 lines, filter-repo on 1 real email address in history, marked DO NOT run without the owner's GO).

## Commit-time extension (by mochi, 23:15-23:23 22/11/2026)

- At commit time the base had moved from 9ae216b to 1230e79. A full-tree rescan on the commit worktree found new leaks in 51 files other lanes added after 9ae216b. Same mechanical replacements, no logic change:
  - 10 log files with the short name in prose (coord-click-7/8 logs, w-a1prep, w-a1prep2, w-f4fix, w-pillfix-amend2 council reviews and log and redteam review).
  - 6 files under improvements/c5-zenproof-runs with the real gmail address in a Gmail tab title ("Inbox (732) - <address> - Gmail"), replaced with "[email redacted]", JSON still valid.
  - 35 more files found by the full rescan (the scan script prints only the first 10 hits per label, so the rescan had to be repeated with the full hit list): w-pillfix, w-pillverify, w-soak-restart, w-zenproof2 logs and reviews, c5 run logs, tests/test_zenproof2_fix.py (docstring only). 8 of them had the name split across two lines ("to Pham / Tuan"), fixed by joining the lines.
  - 1 overlapping file, improvements/w-zen-delegate-liveproof-prep.md, merged by 3-way merge with git merge-file, keeping the other lane's URL-gating amendment and the scrub; 1 conflict resolved by hand (URL-verification wording kept, name scrubbed); the amendment itself contained 1 new name, scrubbed too.
- Final rescan on committed bytes, 1539 files, 33s: FULL3 0, SHORT2 1 file only (worker-y2b-agy-log.md, the adjudicated phamtuan-bank fixture), EMAIL_USER 0, GMAIL_REAL 0, GMAIL_ANY 0, FULL3_D 0, SHORT2_D 0, ADDR_AREA 0, SURNAME_EMAIL 0.
- Tests on committed bytes: py_compile OK on 5 changed py files, tests.test_zen_cli tests.test_chromium_cli tests.test_live_metrics tests.test_zenproof2_fix, Ran 111 tests, OK.
- Push verified by `git ls-remote origin todolist-push`: 9fd8400646118640ec60bc980bb8df80a2a2bd84.
- Coord report: commit a94fa2e on main, push verified.
- Open Muse tong decisions, unchanged: public GitHub handle left in 94 hits, noreply left in 8 hits, git history not rewritten, handle-derived fixture username at worker-y2b-agy-log.md:35, public place names in the route fixture, and whether G-SCRUB counts as met for the working tree only.

## Note on this artifact

- This log compiles the review handoffs received on 2026-11-22 (worker, fix rounds 1 and 2, council 1, council 2, council 3 in two rounds, redteam rounds 1, 2, 3, independent verifier). The original review subagent sessions did not commit their own artifacts; that gap is what the new rule fixes (see coord/mochi.md, rule from 23:57 22/11/2026: every council/redteam/verifier review must commit an artifact with a hash). This committed log is the verifiable artifact for B2-5; its commit hash is the proof.
