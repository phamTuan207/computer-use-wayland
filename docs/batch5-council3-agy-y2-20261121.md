# Batch 5 council 3: independent verification of task 6 (agy-y2)

- Council: batch 5 council 3, independent of the task 6 agent
- Date: 2026-11-21, session 21:09 to 21:13 +07
- Local HEAD at check time: f006137
- Task agent commit on main: 2c0a4dc ("clone1: batch 5 task 6 agy-y2 independent verify, 10/10 live Firefox")

## Verdict: CONFIRMED

The task agent's headline claim (simulate 10/10, live Firefox 10/10 on the
30a72e5 code) is confirmed by first-hand file reads this session, by
arithmetic recomputation, and by an exact per-test match against clone2's
independent live run (commit 80c548a). One limit applies and is stated
plainly below: my own fresh simulate and live re-runs were blocked by the
closed write window this session, so the run outputs themselves are
second-hand evidence, while everything checkable by reading files was
checked first-hand.

## 1. Code identity: CONFIRMED

- `git log --oneline origin/todolist-push -- tests/realistic/agy-y2/` returns
  exactly one commit: 30a72e5 ("Y2: 10 new hard realistic tests agy-y2").
  It is the only commit on that branch touching the suite.
- `git branch -r --contains 30a72e5` returns origin/todolist-push.
- origin/todolist-push tip is beebe50 ("Y8 E1: log v2.1 md5s + pre-flight
  wait until 19:05:40"), verified by rev-parse.
- Both Y7 commits are ancestors of beebe50, verified by merge-base:
  9a74a70 ("Y7: verify Y2 agy-y2 fixes, 10/10 simulate PASS, test-09
  proven non-vacuous, no code fix needed") and a07fd27 ("Y7: redteam
  NO BLOCK, record test-07 skip hole + test-09 bypass + method gaps
  as follow-ups").
- The agent's run copy in /tmp/agy-y2-verify/tests/realistic/agy-y2 is
  byte-identical to 30a72e5: all 25 files compared with
  `git show 30a72e5:<path> | diff -`, zero differences. The code the
  agent ran is exactly 30a72e5.

## 2. Evidence files: present, internally consistent

/tmp/agy-y2-verify/ survived (not wiped). Files and mtimes:
live_results.json (12:08), live_steps.jsonl (12:08), simulate-all.json
(12:01), simulate-all.err (12:00, 0 bytes), run_live.py (12:03),
tests/ (the 30a72e5 copy). Mtimes match the run window the coordinator
recorded (simulate 12:00:54Z to 12:01:03Z, live 12:06:28Z to 12:08:50Z).

Simulate (simulate-all.json), recomputed by me:
- allPassed true, count 10, every test passed true, failures [] every
  test, untouchedFailedAsExpected true every test.
- Per-test ms in file order 10,01,02,03,04,05,06,07,08,09: 724, 630,
  506, 477, 626, 587, 561, 990, 490, 661. In test order 01 to 10 that
  is 630, 506, 477, 626, 587, 561, 990, 490, 661, 724, exactly the
  numbers in the coordinator's report. Sum 6252 ms. (The file lists
  test 10 first because JS orders the integer-like key "10" before
  the non-canonical keys "01" to "09". Cosmetic, not an error.)

Live (live_results.json, cross-checked line by line against
live_steps.jsonl, identical):
- passed 10, count 10, every test PASS, step_error null, failures []
  every test.
- Total actions 179. My sum of the per-test actions
  (16+17+15+18+26+18+22+16+19+12) is 179. Confirmed.
- Total checks 88, all passed: 8/8, 11/11, 11/11, 7/7, 12/12, 9/9,
  8/8, 8/8, 6/6, 8/8. My sum is 88. Confirmed 88/88.
- Per-test seconds match the coordinator's report exactly: 20.094,
  9.570, 10.376, 15.787, 13.514, 17.503, 17.196, 6.903, 9.071, 4.890.
- total_elapsed_s is 140.821 while the per-test sum is 124.904. The
  gap of 15.917 s is explained, not an error: run_live.py computes
  per-test elapsed before driver.quit(), which runs in the finally
  block, so about 1.59 s of quit time per test lands in the main
  total only. 10 quits at about 1.59 s each is 15.9 s.
- Guard failures per test: 8, 10, 9, 4, 12, 7, 6, 7, 6, 8. All above
  zero, so the untouched-fixture guard held on every test.

## 3. Method (run_live.py): sound

Read in full this session. The live runner:
- Extracts verifyTest mechanically from check.mjs at runtime and adds
  only an assertion counter, so the live verdict uses the same
  checker as simulate, not a hand copy.
- Runs the guard first: verify must FAIL on the untouched fixture,
  else the test aborts as ABORT-GUARD. Guard failures of 4 to 12 per
  test prove every test is non-vacuous on the live path too.
- Uses real Selenium interactions (click, send_keys typing, Select
  for dropdowns), one fresh Firefox driver per test, and follows
  simulate.mjs action for action (same selectors, same order).
- Records mid-run notes for test 07 (delete/restore), test 09
  (delete path) and test 10 (watch override). These notes are what
  the Y7 follow-up assessment rests on; see section 5.

## 4. Cross-check against clone2's independent live run: exact match

Clone2's report (commit 80c548a,
docs/research/2026-11-21-agy-y2-live-firefox-run.md) used the same
suite content (commit 30a72e5) and the same ported-checker method.
Per-test actions, checks passed, and guard failures match the task
agent's numbers exactly on all 10 tests (for example test 05: 26
actions, 12/12, guard 12 in both; test 09: 19 actions, 6/6, guard 6
in both). Totals match: 179 actions, 88/88. Only the wall time
differs (clone2 68.838 s, task agent 140.821 s), which the
coordinator attributes to load average 7.18 during the task agent's
run, with other batch 5 agents running in parallel. That is plausible
and the per-test times are all longer by a similar factor, not
suspicious in one place. The coordinator's claim that the numbers
match clone2's exactly is confirmed by my own read of both sources.

## 5. Y7 follow-ups: CONFIRMED as resolved for this run, gaps still open

I read the Y7 redteam doc (a07fd27) and the checker at 30a72e5
myself. The coordinator's framing is accurate on both items: the
mid-run evidence neutralizes the follow-up for this run, and both
remain valid follow-ups for Y2 to fix in the checker and fixture.

Test 07 trash restore (redteam attack 1f, the skip hole):
- The hole is real and still open in the checker. The test 07 branch
  of check.mjs (lines 215 to 240) has 8 checks, all final-state only:
  names, archive "3 files", trash "0", row img4 visible, folder
  Processed, toast active, toast text "Root: 5 files, Archive: 3
  files, Trash: 0 files, Folder Processed created". No restore
  marker is read. Skipping spec steps 23 to 29 (delete and restore)
  still passes all 8 checks, exactly as the redteam proved.
- The live run nevertheless proves THIS run did delete and restore.
  Mid-run notes in live_results.json test 07: after delete, trash
  "1" and img4 hidden true; after restore, trash "0" and img4
  hidden false. A run that skipped delete/restore could not produce
  those intermediate values. The run is honest; the checker gap
  stays open for a future runner.

Test 09 delete path (redteam attack 2c, the bypass):
- The hole is real and still open in the checker. The test 09 branch
  of check.mjs (lines 269 to 287) has 6 checks: total "3", both
  titles, archived item absent, toast active, toast text. There is
  no assertion on the editor title after delete, so the off-spec
  bypass (save the archived note with title "Shopping", never
  clicking delete) would still pass the checker, exactly as the
  redteam proved.
- The live run nevertheless proves THIS run used the real delete
  path. Mid-run notes in live_results.json test 09:
  after_delete_editor_title "Personal Tasks", after_delete_total
  "3", shopping_body "Milk, Eggs, Bread, Apples". The delete button
  was clicked (run_live.py test 09 steps), the editor fell back to
  the Personal Tasks note as the redteam predicted, and the Shopping
  body kept its full content. The run is honest; the checker gap
  stays open. The suggested hardening (assert editor title is
  "Personal Tasks" after delete) is still unapplied.

Neither gap blocks the 10/10 result, because both are about what a
future skipping or bypassing runner could get away with, not about
what this run did. The mid-run notes are the evidence that this run
did neither.

## 6. What I could NOT re-run this session (honest limit)

The write window is closed this session. Content writes fail with
EPERM everywhere I tried (tar extraction to /tmp and to home,
npm, echo to a file in /tmp and in home). Only metadata operations
succeed (mkdir, touch of an empty file, symlink). /tmp is 77 percent
full (392M used, 121M free), so this is the permission block, not
disk space.

- Own simulate.mjs --all: BLOCKED. The agent's copy resolves
  puppeteer-core through a symlink I created at /tmp/node_modules
  (removed afterwards), but both Chromium binaries fail to launch:
  /opt/meta-chromium/chrome refuses with "Hatch WebGL domain policy
  is required for browser startup", and the Playwright chromium-1254
  binary fails with an empty launch error (exit 3 from simulate).
  Direct --dump-dom on the Playwright binary exits 133
  (Trace/breakpoint trap) with 0 bytes output, the known closed
  window signature. The agent ran simulate at 12:00 when the window
  was open; it is closed now.
- Own live Firefox run: NOT ATTEMPTED, per the task rule. The
  screenshot gate test failed: first attempt printed "Could not
  find profile folder" and produced no PNG; second attempt with an
  explicit profile printed a crashreporter minidump failure and a
  Gtk "cannot open display" warning, and produced no PNG. Firefox
  did not start cleanly, so I stopped and did no live run.
- Selenium 4.53.0 (claimed in the coordinator's report): NOT
  VERIFIED by me. The selenium module is not importable in system
  python3 and no venv carrying it was found; the agent's venv is
  gone. This is second-hand only.
- The coordinator also reports a first full live run crashing at
  test 02 (geckodriver connection refused at load 8.23, test 01
  passed in 18.908 s). No log of that crashed run survives in
  /tmp/agy-y2-verify, so I cannot confirm it independently. It is
  reported as a failure, not a success, and the final clean run is
  what the evidence files show.

Because of this limit, the simulate and live run outputs are
second-hand evidence in this report. Everything else above is
first-hand: file reads, diffs, arithmetic, and cross-reads of the
two independent live reports.

## 7. Anything the task agent got wrong

Nothing material. Three small notes, none of which change the
verdict:

- The 140.821 s total versus the 124.904 s per-test sum looks like a
  mismatch at first glance; it is fully explained by driver.quit()
  time (section 2). The agent did not misreport.
- The coordinator's report says the live run was "1 lần chạy duy
  nhất cả 10 test" for the final clean run, after a crashed first
  attempt and per-test re-runs of 02 to 10. The evidence files only
  hold the final clean run. That is fine, but a reader should know
  the 10/10 is the second full run, not the first attempt.
- Selenium 4.53.0 and the load-average explanation for the slower
  wall time are the agent's words, not independently re-measured
  by me.

## 8. UNVERIFIED (stays open)

- Zen. Only Firefox 160.0.1 headless was used, same Gecko stack,
  but no run on the user's Zen. The live run on Zen under the Y9
  plan is still owed, as the coordinator already notes.
- The two checker gaps in section 5 (test 07 restore marker,
  test 09 post-delete editor title assertion) are still open
  follow-ups for Y2.
