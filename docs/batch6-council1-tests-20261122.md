# Batch 6 council 1: independent test verification of task 3

Council run 2026-11-22 03:09-03:13 +07 (20:09-20:13Z). Repo HEAD
6c4afef at run time. I re-ran the suite and the mutation probes
myself and read the evidence files; nothing below is copied from
the task 3 report without checking it.

## Verdict

AGREE on every material claim in
docs/clone1-batch3-reverify-20261121.md. D1 t10 checker SOUND,
full suite 10/10 on Chromium, Firefox 3 of 5 full runs 10/10
with the two failures explained, 3/3 mutation probes caught.
No material error found. Four minor notes at the end, none of
them changes a verdict.

## 1. My own full Chromium run: 10/10

Command: PLAYWRIGHT_CORE_PATH set to
~/workspace/b6t3-scratch/node_modules/playwright-core,
node tests/realistic/clone1-batch3/run_all.mjs.
2026-11-21T20:11:06Z to 20:11:43Z, wall 37,276 ms, exit 0.
results.json copied to ~/workspace/b6c1-results/chromium-run1.json,
then restored to the committed content; tree clean after
(only untracked test-w.txt).

Per-test ms, my run: t01 4259, t02 4005, t03 2777, t04 1980,
t05 2649, t06 2454, t07 2605, t08 2049, t09 3344, t10 11143.
The report's two runs were 36,367 ms and 36,122 ms. Mine is in
the same range; 10/10 reproduces.

## 2. My own mutation probes: 3/3 caught, control passes

Ran each suite copy's t10 check.mjs standalone on Chromium,
same PLAYWRIGHT_CORE_PATH. Outputs saved to
~/workspace/b6c1-results/probe-control.json,
probe-m1.json, probe-m2.json, probe-m3.json.

- Control (unmutated copy): PASS, exit 0, 15,144 ms.
  positionAfterPlayingNext 0, min 0, advancing 8 then 12.
  The harness is sound. (Report: 12,609 ms; same verdict,
  mine slower under load.)
- M1 (nextTrack resets to 1): FAIL, exit 1, 11,298 ms,
  6 failures, exact messages as reported, one per Next path:
  "position not exactly 0 after next while playing: 1",
  "... while paused: 1", "... after shuffle next while
  playing: 1", "... after shuffle next while paused: 1",
  "... after playing wrap next while playing: 1",
  "... after wrap next while paused: 1".
  Sampler min 1, inside the old min <= 2 tolerance: the old
  checker would have passed this. (Report: 11,549 ms,
  same 6 messages.)
- M2 (nextTrack stops the timer): FAIL, exit 1, 11,277 ms,
  6 failures, exact messages as reported:
  "position did not gain after next while playing: 0 to 0",
  "position after next while playing out of range 2-11: 0",
  "position did not gain again after next while playing: 0 to 0",
  and the same three for the shuffle Next. Exact-zero reads
  and sampler mins still pass (position is 0); only the
  advancing checks catch it. (Report: 10,871 ms, same 6.)
- M3 (reset only when paused): FAIL, exit 1, 12,112 ms,
  8 failures, same paths and messages as reported:
  exact-zero 12 on the playing Next, sampler min 12,
  out of range 21; shuffle exact-zero 91, min 91,
  out of range 99; wrap exact-zero 7, sampler min 7.
  All frozen (paused) paths pass. (Report: 12,380 ms,
  8 failures; its live timer values were 20 and 90 where
  mine are 21 and 91. See minor note 2.)

Mutation fixtures verified by diff against the committed
fixture: M1 changes exactly the three "position = 0;" lines
to "position = 1;", M2 adds exactly one "stopTimer();" line
inside nextTrack, M3 changes exactly the three lines to
"if (!playing) position = 0;". mutate.py does exactly what
it says. The control suite is byte-identical to the committed
tree (diff -r, excluding results.json).

## 3. D1 code read

Commit 1d23532 is an ancestor of HEAD. The t10 check's last
change is 1d23532. I read the diff: it adds the in-page
exact-zero read (click and read in the same in-page task),
the sampleMin helper, the three-point advancing checks
(gain of at least 2 ticks across each of two 350 ms sleeps,
absolute 2-11 bound on the middle read), frozen exact-zero
checks, and two-point resume reads. This matches the report's
description of D1 exactly.

Check hashes (git hash-object) all match the report:
t10 check.mjs 3b1757cedbda0163c321eed882de44a3a1ed1d6e,
t10 fixture.html b09bcbf547bc33ec8dd089abc44bbf4fbf825392,
t09 check.mjs 565f4ddc6170dcc4b67709e5f5fc77710d4c4df9,
t05 check.mjs 67e94ed5cb0f498899fb23cadce070e331abee63.

t09 in the tree is the Y10 version: clickAndClose with 5 s
verify polling (line 74) and the 500 ms cancel dwell
(line 132). t05 in the tree is the Y10 checker: it fills the
novel name "field-notes-7.txt" (line 103).

## 4. Firefox 3/5 claim, verified from the result files

All five files exist in ~/workspace/b6t3-results/ and match
the report's table exactly (counts, walls, per-test ms,
failure messages). I read every file, not just the headers.

- run1: 6/10, wall 55,942 ms. Failures exactly as reported:
  t05 "treeBtn.textContent is not a function", t07 and t08
  localStorage failures (editor "", toast "", nothing
  persisted), t09 "waitForEvent page timeout".
- run2: 10/10, wall 60,522 ms. Per-test ms match the report
  to the millisecond (t01 5487, t02 4616, t03 5078, t04 4487,
  t05 4965, t06 4848, t07 5538, t08 4767, t09 7159, t10 13539).
- run3: 8/10, wall 60,466 ms. Failures exactly as reported:
  t09 "detail window did not prefill Alpha v2 on reopen",
  t10 "Node is detached from document".
- run4: 10/10, wall 62,095 ms. Per-test ms match the report
  exactly (t01 4802 through t10 13212).
- run5: 10/10, wall 58,393 ms. Per-test ms match the report
  exactly (t01 4666 through t10 13166).

Standalones: t09 run1 PASS 7,691 ms, run2 PASS 7,266 ms;
t10 run2 PASS 16,926 ms with all D1 details correct
(exact-zero reads 0, sampler mins 0, advancing 8 then 12,
resume 3 then 7, seek 90); t10 run3 FAIL 13,121 ms with the
single failure "now playing after clicking Night Drive: got
'Morning Light - The Demos', want 'Night Drive - The Demos'",
all D1 reads correct. All match the report.
m1-probe-recheck.json: FAIL, 6 failures, exact messages as
reported. See minor note 1 for its elapsed ms.

The run-1 disk-full diagnosis is supported by
~/workspace/b6t3-scratch/ff-stderr.log, which contains 3
occurrences of "No space left on device" (Os code 28,
StorageFull).

## 5. Environment check

Firefox 160.0.1 at ~/workspace/firefox still starts at
council time: headless screenshot test exit 0, screenshot
5,763 bytes, --version prints 160.0.1, no minidump. (The
5,763-byte screenshot size matches the task 3 agent's.)
/tmp/firefox is gone again (another /tmp wipe since the
task 3 runs); /tmp is 1% used now, 511M free. Memory at
council time: free 366M, available 1776M.

## Minor notes (do not change any verdict)

1. m1-probe-recheck.json has internal elapsed_ms 13,648,
   while the report's completion-check section says
   "wall 13,909 ms" for the same re-run. 261 ms gap,
   unexplained. Most likely the checker's external stopwatch
   versus the JSON's internal elapsed (process spawn
   overhead). The 6 failure messages match exactly, so the
   re-run itself is confirmed.
2. M3 live timer values differ by one tick between my run
   (advancing 21, shuffle min 91) and the report's run
   (20, 90). These are live 100 ms timer reads, not
   constants, so a one-tick difference is expected. Failure
   shapes are identical (8 failures, same paths).
3. The Chromium run 1 evidence file /tmp/b6t3-run1-results.json
   no longer exists (another /tmp wipe after the 02:21
   completion check). The report's "10/10 twice" Chromium
   claim now rests on the report record plus my fresh
   independent 10/10 run above, which reproduces it.
4. The task 3 report is 372 lines by wc -l (the batch 6
   assignment brief said 373; the usual plus-one count).
   The report itself states no line count, so this is not
   a report error.

## Limits of this verification

- I did not re-run anything on Firefox: the BiDi shim was
  deleted after the task 3 runs (as the report says), and
  rebuilding it is out of council scope. The Firefox numbers
  above are verified from the saved result files only.
  I re-ran the suite and all four probes on Chromium myself.
- I ran each probe once and the suite once; the agent ran
  each probe once and the suite twice on Chromium.
- Everything on real Zen is still UNVERIFIED, as the report
  states. The t10 playlist-click race (fixture rebuilds the
  playlist every 100 ms while playing) remains open and
  unfixed, also as the report states.

## Evidence

- My Chromium run: ~/workspace/b6c1-results/chromium-run1.json
  (10/10, wall 37,276 ms) and chromium-run1.txt (full output)
- My probe outputs: ~/workspace/b6c1-results/probe-control.json
  (PASS, 15,144 ms), probe-m1.json (FAIL, 11,298 ms),
  probe-m2.json (FAIL, 11,277 ms), probe-m3.json
  (FAIL, 12,112 ms)
- Firefox files read: ~/workspace/b6t3-results/
  batch3-firefox-run1.json through run5.json,
  t09-firefox-standalone-run1.json and run2.json,
  t10-firefox-standalone-run2.json and run3.json,
  m1-probe-recheck.json
