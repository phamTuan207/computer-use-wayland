# Batch 6 redteam: hostile review of the three batch 6 reports

Reviewer: batch 6 redteam, independent subagent. Method: read all three
reports in full, then recomputed every checkable number from the repo,
the branch tip e4082ff, and the files on disk. Line counts by wc -l.
No report was taken on trust. No coord file edited, nothing committed
or pushed.

Reports reviewed:
- docs/clone1-evidence-audit-full-20261121.md (task 2)
- docs/clone1-zen-ordinary-user-run-20261121.md (task 1, PARTIAL)
- docs/clone1-batch3-reverify-20261121.md (task 3, verdict SOUND)

Totals: 12 wrong facts, 8 unverified claims stated as done, 2 real
bugs, 6 minor. The verdicts themselves mostly survive: the 13
violations are real, D1 is SOUND, and the Firefox runs check out
exactly. The damage is in the evidence accounting, the timestamps,
and one report that is already stale.

## Wrong facts

### W1. All three line counts quoted for the reports are off by +1 (again)
wc -l gives 377 for the evidence audit, 243 for the ZT report, 372
for the batch 3 re-verify. The brief quoted 378 / 244 / 373, and the
original task 1 report at 3323170 is 189 lines, not 190. This is the
same systematic error as batch 4 and batch 5 (counting newline + 1).
Coord already corrects task 3 to 372 (coord line 1997, "brief noi
373") but still says 378 for task 2 (line 1712) and 244 for task 1
(line 1834). The reports themselves do not state their own line
counts, so the error lives in the parent's claims and in coord, not
in the report text.

### W2. Evidence audit census: 4 of 8 pattern counts do not reproduce
Claimed (report, Census): done 603, complet 1146, verified 2479,
passed 420. Measured by me with git grep -c on e4082ff,
improvements/*.md, case-sensitive: done 582, complet 1120,
verified 2237, passed 403. Case-insensitive: 1061, 1247, 2758, 455.
All files under improvements/: 660, 1311, 2257, 428. Word-boundary:
556, 0, 2011, 381. No obvious grep variant reproduces any of the
four claimed numbers. The other census numbers are exact: PASS 1428,
10/10 172, ALL PASS 25, all tests 2, /tmp/ lines 1664 in 227 files,
laptop 1675 (exact only case-insensitively), strong-claim union 1011
(recomputed exactly). So the census table is half wrong, half right,
and the wrong half cannot be explained by a case-sensitivity choice.

### W3. Evidence audit hash classification does not add up
Claimed: 390 cited hashes, 363 resolve, 27 do not; the 27 are
classified as 1 genuine this-repo commit + "about 20" external-repo
commits + "6 false positives". Counting the items the audit itself
names: external list has 16 items (03a57c4, 34f5195, 784fee3,
30528aa, 355c03b35c2f94006c567a1e4f52f180218de148, 4c72cd4,
eb4a0ea, 4e7b769, 5841c24, a05e0dc, a4144b3, a827562, f5e1fb56,
88f681a, d71be3a7b3f93b534a2823fd68cabd7ac2a02359, 99e8e15),
false-positive list has 8 items (11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947,
1794947807, 750c8dae, 8fb75ccd, 99f30ca, 5cb507b6, 674441ea, c1a2b3c).
1 + 16 + 8 = 25, not 27. Two unresolvable hashes are unaccounted
for, and the prose counts ("about 20", "6") do not match the named
items (16, 8). Spot checks confirm the substance: 84b88bb and
87cd34f do resolve; 03a57c4, 34f5195, 30528aa do not; 700144a does
not (V12). But the classification as written is internally
inconsistent, so the 27 total itself is not fully accounted for.

### W4. Evidence audit header end time is impossible
Header says "work 01:40 to 02:30 +07". The task 2 agent completed
at 01:45:21 +07 (runtime completion record) and its commit
581736e landed 01:45:30 +07. Work cannot have run to 02:30. The
end time is wrong by 45 minutes. Same pattern as W5.

### W5. Task 1 report timestamps after 02:00 are impossible, and the timeout order is inverted
The report header says the session ran "01:38 to 02:05 +07", the
TLS fix was "verified 02:03 +07", and the approval timeout was
"02:04 +07". The first task 1 agent completed at 01:57:52 +07
(runtime completion record) and its report file was committed as
3323170 at 01:58:07 +07. Events claimed at 02:03, 02:04 and 02:05
are 5 to 8 minutes after the agent stopped. The timeout event
itself is real (the runtime record shows userConfirmationRequired
timed_out for that agent), but the 02:04 timestamp cannot be
right. The ordering is also inverted: the follow-up's "second"
timeout at 02:01:44 predates the first agent's claimed "first"
timeout at 02:04. The true order is unknown; the first agent's
timeout happened at some time at or before 01:57. The early
timestamps in the report are consistent with real time (the
ZT-00 pre-fix JSON's own wallStart07 is 01:43:58, matching the
report), so the drift starts somewhere after 01:57, not at the
beginning.

### W6. Task 1 ZT-00: a 10-second span next to a 17,960 ms duration
The report says the gate run was "(01:43:58 to 01:44:08 +07,
17,960 ms)". The pre-fix JSON confirms wallStart07 01:43:58,
wallEnd07 01:44:08, elapsedMs 17,960. The wall span is 10,000 ms;
the elapsed figure is 17,960 ms. The step elapsed values sum to
about 10,591 ms, consistent with the 10 s span. About 7.4 s of
launch and setup time is inside elapsedMs but outside the quoted
wall span, with no explanation. The two numbers as presented do
not agree with each other.

### W7. Task 3 report: Chromium run 2 start time is wrong
"Runs 18:39:56Z and 18:41:01Z." The saved run 2 output
(control-suite/results.json, see W9) says started_at
18:40:35.594Z, finished_at 18:41:11.716Z, wall 36,122 ms. 18:41:01Z
is neither the start nor the end. Wrong by 26 s from the start.
Run 1's stated start (18:39:56Z) cannot be checked: its file is
gone (see U3).

### W8. Task 3 completion-check section: M1 recheck wall is wrong
"wall 13,909 ms". The saved file m1-probe-recheck.json says
elapsed_ms 13,648, pass false, 6 failures with the exact messages
quoted. Wrong by 261 ms. The failures and sampler mins (1) in the
file match the report exactly; only the wall number is wrong.

### W9. Task 3 report: "no separate file was saved for run 2" is false
Evidence section: "Chromium run 2: 10/10, 36,122 ms, numbers from
the live run output recorded in this report; no separate file was
saved for run 2 (only run 1's file exists)." False. The run 2
output exists in four identical copies on disk:
control-suite/results.json, m1-suite/results.json,
m2-suite/results.json, m3-suite/results.json (all started
18:40:35.594Z, wall 36,122 ms, 10/10, per-test ms matching run 2
exactly, including t10 10,461 ms with the D1 details quoted in
the report). The suites were copied after run 2, so the file
survived inside them. The completion-check section repeats the
error ("Chromium run 2... never saved"). The error cuts in the
report's favor in one sense: run 2 IS verifiable from disk, and
its numbers check out exactly. But the claim as written is wrong.

### W10. Task 3 completion-check section: "control suite is byte-identical to the committed tree" is false
control-suite/results.json differs from the committed
results.json: the suite copy is the run 2 output (started
18:40:35Z, wall 36,122 ms), the committed file is the Y10 run
(started 12:18:46Z, wall 25,024 ms). The code and fixture files
in the control suite are identical to the committed tree; the
results.json is not. The claim as written, without qualification,
is false.

### W11. Task 3 report contradicts itself on run 2
Body: "run 2 is the results.json that was in the tree before my
Firefox runs (restored afterwards, tree clean)." Evidence
section: "no separate file was saved for run 2". Both cannot be
true. The file-exists version is correct (see W9).

### W12. Coord repeats the run 2 error
Coord line 2047: "chi M2/M3 va Chromium run 2 khong co file luu
(bao cao da khai)". Wrong for Chromium run 2 (see W9). The M2/M3
part is correct (their probe outputs were never saved, see U4).

## Unverified claims stated as done

### U1. Task 1: the second F-B6-03 reproduction log is gone
The report cites /tmp/diag-followup.log (847 bytes) as the log
for the second Wikipedia timeout (02:01:44). The file no longer
exists (later /tmp wipe). The second reproduction can no longer
be checked from disk; only the report's word remains. Same for
the first agent's diag logs /tmp/diag2.log, diag3.log, diag4.log.

### U2. Task 1: the Firefox-start screenshot evidence is gone
"screenshot /tmp/ff-b6-test.png 5,763 bytes, no minidump" is
cited as proof Firefox starts. The file is gone (later /tmp
wipe). The 5,763-byte figure is now unverifiable from disk.
Consistent, not proof: task 3's screenshot at 18:42:04Z is also
5,763 bytes.

### U3. Task 3: Chromium run 1 has no surviving file
/tmp/b6t3-run1-results.json is gone (wiped). Run 1's 10/10,
36,367 ms and per-test ms now rest on the report record only.
Its per-test values sum to 36,300 ms against a 36,367 ms wall
(67 ms overhead), which is internally consistent, but there is
no file to check them against.

### U4. Task 3: three of the four mutation-probe runs were never saved
t10 standalone run 1 (PASS, 13,130 ms) was printed to stdout
only. The M2 probe (FAIL, 10,871 ms, 6 failures) and M3 probe
(FAIL, 12,380 ms, 8 failures) outputs were never saved, and
neither was the control probe (PASS, 12,609 ms). Only M1 was
re-run and saved (m1-probe-recheck.json, verified: 6 failures,
exact messages, sampler mins 1). So the "3/3 mutations caught"
verdict rests on one saved re-run plus the report's record for
M2, M3 and the control. The mutations themselves are verified
exactly as described in the suite copies (see Survived), which
supports the verdict, but the run outputs for M2/M3/control are
second-hand.

### U5. Task 1: memory readings have no preserved log
"free 144M / available 469M at 01:39", "free 545M / available
2098M at 01:58", "free 142M / available 1157M at 02:01" are
stated as verified this session, but no log file preserves any
of them. They cannot be re-checked.

### U6. Task 2: "39 headline claims read in full" has no artifact
The audit says 39 headline claims were read with a verdict and
1011 strong-claim lines were "saved during the audit and
triaged". The 1011 union recomputes exactly (see Survived), but
no saved triage file is named or located, so the 39-claim triage
itself cannot be re-checked.

### U7. Task 1 report is already stale (most important forward item)
The report (last edited 02:12) says no scenario ran. Since then
a follow-up agent (spawned by the 02:40 watchdog) has run ZT-00
again at 02:40:13 and produced ZT-01.json through ZT-08.json
(02:40-03:12). ZT-00.json on disk no longer holds the run the
report describes; the old run is preserved in
ZT-00-pre-fix.json. The new ZT-00 run shows the adapted gate
passing the BiDi goto (example.com, title "Example Domain") but
failing on Ctrl+W close (closedBy "none", tab count stayed 1)
and on title-set-restored. None of this is in the report, and
the report's "no scenario ran" verdict is no longer current.
The parent needs a report update, not a re-verification.

### U8. Task 3: "t10 flaky on Chromium the same way" is an inference, not an observation
The report says the playlist-click race "exists on Chromium too
in principle (the BiDi click is just slower, so the window is
wider)". No Chromium failure from this race was observed in this
task (Chromium runs were 10/10 twice). The inference is
reasonable, but it is stated as a near-fact with no Chromium-side
evidence behind it.

## Real bugs

### B1. Runner closeActiveTab returns "none" on a single-tab session (new, missed by the reports)
The 02:40 ZT-00 run (see U7) shows step 7-ctrl-w-close FAIL
with closedBy "none", before 1, after 1. The runner code does
have the fallback the report describes (Ctrl+W, wait 800 ms,
then page.close(), wait 400 ms), but on a single-tab session
BOTH mechanisms failed to reduce the tab count: Ctrl+W did
nothing (headless has no chrome to close), and page.close() on
the only tab did not drop browser.pages() below 1. The report's
framing ("falls back to BiDi page.close()") implies the fallback
rescues the close; in practice it returned "none" and the run
verdict went FAIL on the close and restore steps. Any scenario
that ends by closing its only tab will hit this. The fix is a
runner change (for example, do not require the tab count to
drop when closing the last tab, or close the browser instead),
which is outside this review's scope, but the reports never
flag it.

### B2. a1_unblind.py line 226: unguarded median still crashes the exact B3a scenario (confirmed, credit to task 2)
Task 2 reported this as V6 and I confirmed it by reading the
code at e4082ff: `code_wall_med = median(code_walls)` sits
inside the `if len(code_thinks) == 3 and len(step_gaps) == 3:`
branch with no guard on code_walls, and median() itself (line
41) is just sorted() with no guard. In the exact B3a scenario
(CODE wall UNMEASURED, thinks numeric) the branch is entered
and sorted() on mixed str/int raises TypeError. The think
lists are isinstance-filtered (lines 216-219) and the
dispersion, timeout-median and robustness blocks all guard
with isinstance, but the line 226 wall median was missed.
Verified by code reading only, no execution. This is a real bug
in the audited code, correctly found by task 2, not a report
error. It is listed here because it is the most significant
real bug in the batch, and the fix task 2 recommends (guard
line 226 the same way) is the right one.

## Minor

### M1. "Firefox about 1.7x slower than Chromium" overstates slightly
Firefox full-run walls 55,942-62,095 ms vs Chromium 36,122-36,367
ms: ratios 1.54, 1.66, 1.66, 1.71, 1.61, mean about 1.64.
"About 1.6x" would be accurate; "about 1.7x" is the top of the
range, not the middle.

### M2. V4 summary mislabels 1359 as the baseline
The audit's V4 parenthetical says "(1359 baseline, +20 from 10
det_finish + 10 from another worker's file, 1350 final)". The
doc says baseline is 1339: after-changes 1359 = 1339 + 20, final
1350 = 1339 + 11 (the other worker's file absent from the clean
worktree). The arithmetic the audit endorses is right; the
label "1359 baseline" is wrong.

### M3. V1 "5 places" understates the citation count
13 lines on the branch cite "MEMORY.md 22:57" (measured), and
the H3 acceptance appears in more places than the 5 the audit
lists (for example opt-council-m2-verdict.md lines 71 and 108
also cite it, for the VMFIX cause). The violation itself stands;
the count of places is incomplete.

### M4. Runner comment repeats the wrong timestamp
~/workspace/b6t1/zt_run.mjs comments cite the TLS fix as
"verified 02:03 +07" (see W5). The timestamp is wrong in the
code comment as well as in the report.

### M5. Completion check overstates the disclosure on M2/M3
The completion-check section says the M2/M3 probe outputs "were
never saved (the report discloses this)". The report never
states that in so many words; its evidence section merely omits
M2/M3 result files while listing the suite copies and mutate.py.
Omission is weaker than disclosure, and the checker overstated
it. (The M2/M3 outputs are in fact unsaved; only the wording of
the disclosure claim is wrong.)

### M6. prepProfileCerts runs -A even when -N fails, and never checks the CA file exists
If certutil -N fails, the code still runs -A (which will also
fail without a DB), and the ok flag is computed only at the end.
The runner's claimed "writes BLOCKED and exits 2" behavior
depends on the downstream ok check, which was not verified in
this review. Cosmetic robustness gap, not a wrong result: the
02:40 run's certPrep came back nCode 0, aCode 0, ok true.

## What survived the hunt (verified correct)

### Evidence audit (task 2)
- Scope: 484 files, 10,287,241 bytes at e4082ff, exact. live-test-log
  4229 lines, PASS 113 lines, exact.
- Census exact where it matters: PASS 1428, 10/10 172, ALL PASS 25,
  all tests 2, /tmp/ lines 1664 in 227 files, laptop 1675
  (case-insensitive), strong-claim union 1011 (recomputed exactly).
- FREEZE.md 12 sha256 hashes; A1 plan 1072 lines; FCCK per-test
  times sum to 28,613 ms, plus 4,118 = 32,731 ms, exact.
- Y8b chain exact: worker-y8b-out-b1-v2.2.log 59 lines, 59
  "ok": true, 0 "ok": false; plan md5
  63415e9b6cd63dc2185ca23242180424; design md5 verified by
  hashing the file at 695efea (e1909423ee987b355783f22c7d804494);
  executor wall 522 s, coordinator wall 543 s.
- V1 confirmed: MEMORY.md does not exist on the branch; the H3
  acceptance is cited only to MEMORY.md 22:57 (13 citing lines).
- V2 confirmed: all 9 arm logs absent; f3-evidence holds 14
  files; full.log 59 lines, 0 arm mentions.
- V3 confirmed: test-scores.md, test-cases.md,
  test-execution-report.md, typing-fix-multipage-report.md and
  stress.log have 0 hits on the branch; c9b96a7 exists. Note:
  15 end-state.json files do exist, but they are A1 pilot case
  fixtures (tests/realistic/a1-pilot/checker-selftest/cases/Txx/),
  not the judge's state.json files, so they do not contradict V3.
- V5 confirmed: 16 case dirs (T01-T10, T11a, T11b, T13-T16), no
  T12, total = 17 hardcoded at run_matrix.py line 147.
- V6 confirmed by code reading (see B2).
- V7, V8, V11, V13: local-only evidence pattern confirmed;
  V13 arithmetic recomputed exact (93.96, -53.1, -56.4, +379.2,
  +414.3 percent).
- V9 confirmed: RUN-REPORT-20261121.md line 19 says "Final full
  run: 9/20 in 59,111 ms".
- V10 confirmed: diff ed78e83..1d23532 is check.mjs +213/-27 and
  README.md +87/+10; check.mjs 167 to 353 lines; the log's 240
  and 97 are diffstat changed-line totals, misread as insertions.
- V12 confirmed: 700144a is not a valid object name; no
  step3-stream-prep branch exists.
- Hash spot checks: 84b88bb and 87cd34f resolve; 03a57c4,
  34f5195, 30528aa do not (external, as classified).

### ZT report (task 1)
- Firefox tarball 90,943,956 bytes, --version prints 160.0.1.
- ZT source file at e4082ff is revision v2 (22:34 21/11).
- prepProfileCerts exists in the runner (line 109), called at
  line 902 after writeUserJs (901) and before launchFirefox
  (915); node --check passes; the CA file exists.
- ZT-00 pre-fix JSON matches the report's old-run description
  exactly: wallStart 01:43:58, elapsed 17,960 ms, verdict
  BLOCKED, steps as described.
- Ctrl+L finding: proved in the old run (step 4, page stayed
  about:blank).
- TLS root cause and certutil fix: corroborated by the follow-up
  re-test and by the 02:40 run's certPrep ok true plus
  example.com title PASS.

### Batch 3 re-verify (task 3)
- All four check hashes match exactly (t10 check
  3b1757cedbda0163c321eed882de44a3a1ed1d6e, t10 fixture
  b09bcbf547bc33ec8dd089abc44bbf4fbf825392, t09 check
  565f4ddc6170dcc4b67709e5f5fc77710d4c4df9, t05 check
  67e94ed5cb0f498899fb23cadce070e331abee63). t10 check last
  change is 1d23532, an ancestor of ab90611.
- Firefox run JSONs match the report exactly: run1 6/10
  (55,942 ms; t05 textContent, t07/t08 localStorage, t09
  waitForEvent timeout), run2 10/10 (60,522 ms, per-test ms
  exact), run3 8/10 (60,466 ms; t09 prefill, t10 detached
  node), run4 10/10 (62,095 ms, per-test ms exact), run5 10/10
  (58,393 ms, per-test ms exact).
- Standalones match: t09 2/2 PASS (7,691 ms, 7,266 ms); t10
  run2 PASS 16,926 ms with D1 details 8 then 12, resume 3 then
  7, seek 90; run3 FAIL 13,121 ms on the Night Drive race only,
  all D1 reads correct.
- M1 recheck file matches the report except the wall (see W8):
  6 failures with the exact messages, sampler mins 1.
- Mutations exactly as described: M1 changes all three
  `position = 0;` to `position = 1;` in nextTrack; M2 inserts
  stopTimer() as the first statement of nextTrack; M3 changes
  all three to `if (!playing) position = 0;`. Only the fixture
  differs in each mutated suite.
- Old checker (ed78e83) has 0 exact-zero checks and its sampler
  fails only when min > 2, so M1 (sampler mins 1) would have
  passed it. The report's "old checker would have passed this"
  claim is correct. The D1 checker has 8 exact-zero checks plus
  the three-point advancing checks, all read in the current code.
- ff-stderr.log holds the "No space left on device" evidence
  (os error 28, glean state-file write failures).
- Shim deleted: full ~/workspace find returns no
  firefox_bidi.mjs. Tree clean except untracked test-w.txt.
  The /tmp/firefox symlink is gone, as the report discloses.

## Bottom line
- The 13 violations stand. The D1 SOUND verdict stands. The
  Firefox 10/10 runs stand.
- What does not stand: the census counts for done/complet/
  verified/passed, the hash-classification arithmetic, the
  session timestamps in the task 1 and task 2 reports, the
  Chromium run 2 evidence accounting (the file exists; the
  report and the completion check both say it does not), and
  the task 1 report's currency (follow-up 2 has run ZT-00
  through ZT-08 since it was written).
- The single most useful next step is a task 1 report update
  from the ZT-00..ZT-08 result files now on disk, including
  the Ctrl+W finding (B1). The second is to stop quoting line
  counts from memory: every count in this review was taken
  from wc -l, and the +1 error has now bitten three batches
  in a row.
