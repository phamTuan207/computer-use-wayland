# Batch 6 task 3: re-verify of Y15 D1 fix + full clone1-batch3 suite

Re-ran the FULL clone1-batch3 suite on this machine with Y15's D1
fix, on Chromium and on real Firefox, plus my own t10 mutation
probes against the D1 checker. All numbers below are from my own
runs this session, read back from the saved result files.

## Code under test

- Repo HEAD at run time: ab90611 ("clone1: batch 6 task 1 partial
  noted, follow-up spawned"). D1 commit 1d23532 ("t10-music-player:
  assert exact-zero reset and clock liveness on Next paths") IS an
  ancestor of HEAD. The t10 check's last change is 1d23532, so the
  D1 version ran in every run below.
- Check hashes (git hash-object, recorded because council 1 found
  batch 5 runs did not record them):
  - t10 check.mjs: 3b1757cedbda0163c321eed882de44a3a1ed1d6e
  - t10 fixture.html: b09bcbf547bc33ec8dd089abc44bbf4fbf825392
  - t09 check.mjs: 565f4ddc6170dcc4b67709e5f5fc77710d4c4df9
  - t05 check.mjs: 67e94ed5cb0f498899fb23cadce070e331abee63
- D1 closes the hole Y12 probe P2 found: the old checker accepted
  a nextTrack resetting position to 1 because the sampler tolerance
  was min <= 2. D1 adds exact-zero reads after every playing Next,
  frozen exact-zero checks after paused Nexts, three-point
  advancing checks after the plain and shuffle Nexts, and two-point
  resume reads after every frozen resume. Y12's verdict on the
  merged suite (ed78e83) was "SOUND WITH NOTED DEFECTS".

## Chromium (Playwright, cache build 1254): 10/10 twice

playwright-core 1.55.0 installed once into
~/workspace/b6t3-scratch (2 s). Runs 18:39:56Z and 18:41:01Z.

| Run | Passed | Wall ms |
|-----|--------|---------|
| 1 | 10/10 | 36367 |
| 2 | 10/10 | 36122 |

Run 1 per-test ms: t01 5965, t02 1939, t03 1927, t04 1749,
t05 2526, t06 2066, t07 2705, t08 1946, t09 4032, t10 11445.
Run 2 per-test ms: t01 2836, t02 2977, t03 1834, t04 2376,
t05 5008, t06 3239, t07 2305, t08 2010, t09 3052, t10 10461.
Run 1 results saved to /tmp/b6t3-run1-results.json; run 2 is the
results.json that was in the tree before my Firefox runs (restored
afterwards, tree clean).

t10 run 2 details (all D1 reads correct): exact-zero reads 0 on
every Next path (playing, paused, shuffle playing, shuffle paused,
playing wrap, frozen wrap); sampler mins 0; advancing gains 3-4
ticks per 350 ms window (8 then 12); resume reads 3 then 7;
seek 90.

## Firefox: recovered, then 10/10 three times

### Firefox was down, then back

/tmp/firefox was gone (VM restart wiped /tmp). I re-downloaded
Firefox 160.0.1 from
https://ftp.mozilla.org/pub/firefox/releases/160.0.1/linux-x86_64/en-US/firefox-160.0.1.tar.xz,
90,943,956 bytes exactly. First headless screenshot failed only
because the profile dir did not exist yet ("Could not find profile
folder"); with the dir created it started at once, exit 0,
screenshot 5,763 bytes, at 18:42:04Z with 1060M available. The
90-minute segfault window of 21/11 is over: host memory is back
(available 899M-1818M during my runs, free 130M-718M).

The install now lives at ~/workspace/firefox-160.0.1 (moved out of
/tmp, see the disk section below) with a symlink at /tmp/firefox
so the old path still works.

### The BiDi shim had to be rebuilt from scratch

No copy of batch 5's lib/firefox_bidi.mjs survives on disk (full
workspace search, 160 s, found only doc mentions). I rebuilt it
from the method in docs/clone1-batch5-firefox-20261121.md and
~/workspace/b5t5-results-y10/README.md: puppeteer-core 24.43.1
from ~/workspace/b5t5-scratch over WebDriver BiDi, fresh Firefox
per check (own port, own profile), Playwright-API surface
(click, fill, textContent, getAttribute, inputValue, isVisible,
isChecked, check, uncheck, selectOption, reload, evaluate,
$$eval, $eval, $, locator with nth and chaining, keyboard,
mouse, waitForEvent page/close, context.pages). The shim was
TEMPORARY: it lived in
tests/realistic/clone1-batch3/lib/firefox_bidi.mjs plus a
FIREFOX_BIDI branch in lib/browser.mjs, and both were reverted
after the runs (browser.mjs restored byte-identical from the copy
saved before editing, shim deleted, results.json restored to the
committed content). Do NOT commit the shim; it is not in this
report's file list.

Shim smoke test first (~/workspace/b6t3-scratch/smoke.mjs):
launch 4,884 ms, goto 190 ms, click 134 ms, counter 0 to 1,
fill 'bidi-test' read back, PASS.

Emulations, disclosed honestly (same as batch 5, plus two of my
own): dblclick dispatches a dblclick event explicitly (Puppeteer
clickCount 2 fires none on Firefox BiDi); fill uses the native
value setter plus one input/change event; locator clicks resolve
the element in-page and click its center with a real pointer
click; Puppeteer "closed" errors are rethrown with Playwright's
wording ("Target page, context or browser has been closed") so
the t09 clickAndClose tolerance works; click() retries up to 3
times on "Node is detached from document" (Playwright retries a
click when the element is detached mid-action; added after run 3,
see below).

### /tmp was 100% full: the root cause of run 1

Full Firefox run 1 went 6/10 (t05, t07, t08, t09 fail). The
diagnosis was not the tests: /tmp was 100% full (512M used,
0 avail). Firefox stderr showed "No space left on device"
(os error 28), "database or disk is full", "Could not write to
.../sessionCheckpoints.json.tmp: NS_ERROR_FILE_NO_DEVICE_SPACE",
and every sqlite file in the profile was 0 bytes. localStorage
threw NS_ERROR_FAILURE and sessionStorage also failed at first,
so the t07/t08 fixtures died at their localStorage line before
attaching any listeners (editor stayed "", save button dead).
The full /tmp was: /tmp/firefox 331M (mine, just downloaded),
the tarball 87M (mine), and 90M of ff-b6-diag* profiles from
other batch 6 agents (NOT touched). Fix, using only my own
files: deleted the tarball, moved /tmp/firefox to
~/workspace/firefox-160.0.1, left a symlink at /tmp/firefox,
deleted my stale profiles. /tmp went to 111M free (79%). After
that, t07 editor initial read '2 + 3', run gave 'Result: 40',
t08 save gave toast 'Settings saved.' with 'demo-settings' in
localStorage. All four run-1 failures were this disk-full
environment, not the suite.

### Full Firefox runs

| Run | Passed | Wall ms | Note |
|-----|--------|---------|------|
| 1 | 6/10 | 55942 | /tmp 100% full; t05, t07, t08, t09 fail |
| 2 | 10/10 | 60522 | after disk fix + 2 shim fixes |
| 3 | 8/10 | 60466 | t09 waitForLoadState hole, t10 detached-node race |
| 4 | 10/10 | 62095 | after the 2 fixes below |
| 5 | 10/10 | 58393 | |

Run 2 per-test ms: t01 5487, t02 4616, t03 5078, t04 4487,
t05 4965, t06 4848, t07 5538, t08 4767, t09 7159, t10 13539.
Run 4 per-test ms: t01 4802, t02 4805, t03 5182, t04 4999,
t05 5371, t06 5391, t07 5672, t08 4581, t09 8064, t10 13212.
Run 5 per-test ms: t01 4666, t02 4238, t03 4765, t04 4525,
t05 4892, t06 4957, t07 4925, t08 4568, t09 7679, t10 13166.
Firefox is about 1.7x slower than Chromium wall clock (58-62 s
vs 36 s), mostly one fresh Firefox launch per check plus slower
BiDi round trips.

Evidence: ~/workspace/b6t3-results/batch3-firefox-run1.json
through run5.json (one per run).

### Two shim bugs found and fixed during the runs

1. t05 `treeBtn.textContent is not a function` (run 1): the
   check calls .textContent() on the ElementHandle returned by
   page.$, and my shim's $ returned only boundingBox(). Fixed by
   adding textContent(), getAttribute(), inputValue() to the $
   handle.
2. Page registry double-count (found while debugging t09): my
   newPage() pushed a wrapper AND the targetcreated handler
   pushed a second wrapper for the same tab, so context.pages()
   counted the main page twice (2 before any popup). Fixed with
   a one-wrapper-per-raw-page map: newPage() polls for the
   handler's wrapper instead of pushing its own, and the initial
   about:blank tab is tracked but excluded from pages(), so
   pages() counts only real pages (1 main + popups), matching
   Playwright. Verified in isolation: 1 page before the click,
   2 after one popup, waitForEvent resolves.
3. t09 run 3, "detail window did not prefill Alpha v2 on
   reopen": my waitForLoadState polled readyState, but a fresh
   popup starts at about:blank whose readyState is already
   'complete', so it returned before detail.html even started
   loading and the prefill read hit the blank page. Fixed by
   waiting for the URL to leave about:blank first. t09
   standalone then passed 2/2 (7,691 ms, 7,266 ms).
4. t10 run 3, "Node is detached from document": Puppeteer's
   click holds an element handle; the fixture rebuilds the whole
   playlist (innerHTML) every 100 ms while playing, so a timer
   tick between the query and the click detaches the node. Fixed
   in the shim with the bounded detached-retry above. The
   wrong-target variant of the same race (standalone run 3 below)
   throws no error, so no retry can catch it; that one is the
   fixture race, not the shim.

### t09 standalone on Firefox: 2/2 PASS

7,691 ms and 7,266 ms, 0 failures. Saved as
t09-firefox-standalone-run1.json and run2.json. This is the
first live proof of the Y10 t09 version on Firefox: the
postMessage-then-close race, the 5 s verify polling, the cancel
dwell, and the two-popups-open count (3 pages) all pass on real
Firefox. The batch 5 Y10 followup never got here (Firefox
segfaulted before t09 could run).

### t10 standalone on Firefox: 2/3 PASS

- Run 1: PASS, 13,130 ms. Run 2: PASS, 16,926 ms.
- Run 3: FAIL, 13,121 ms, one failure: "now playing after
  clicking Night Drive: got 'Morning Light - The Demos', want
  'Night Drive - The Demos'". Every D1 detail in run 3 is
  correct (all exact-zero reads 0, all sampler mins 0, all
  advancing gains 3-4 ticks, all resume reads 3 then 7), so the
  D1 checks all passed; the failure is the last playlist click.
  This is the same race batch 5 task 5 documented in its run 3:
  the fixture rebuilds the playlist every 100 ms while playing,
  and the slower BiDi click can straddle a rebuild so mousedown
  and mouseup land on different nodes and the click event never
  reaches the track. It is a pre-existing fixture race, not a D1
  defect, and it exists on Chromium too in principle (the BiDi
  click is just slower, so the window is wider). Saved as
  t10-firefox-standalone-run2.json and run3.json (run 1 was
  printed to stdout, not saved to a file).

### Firefox-only failures: none in the app

Every Firefox failure across all runs was diagnosed to the disk
being full, a shim gap, or the playlist-click race. No app
behavior failed only on Firefox. t10 on Firefox is flaky in the
same way as on Chromium for the same timing reason, not a
Firefox defect.

## My own t10 mutation probes (Chromium, D1 checker)

Method: copied the whole suite tree four times into
~/workspace/b6t3-scratch (control-suite, m1/m2/m3-suite),
mutated ONLY the nextTrack function in the t10 fixture of each
copy with ~/workspace/b6t3-scratch/mutate.py, ran the D1
check.mjs standalone against each copy. All three mutations are
my own, not Y10's or Y12's.

- Control (unmutated copy): PASS, exit 0, 12,609 ms. The
  harness itself is sound.
- M1, nextTrack resets position to 1 instead of 0 (the Y12 P2
  hole, all three position = 0 lines in nextTrack changed to 1):
  FAIL, exit 1, 11,549 ms, 6 failures, one per Next path:
  "position not exactly 0 after next while playing: 1",
  "... while paused: 1", "... after shuffle next while
  playing: 1", "... after shuffle next while paused: 1",
  "... after playing wrap next while playing: 1",
  "... after wrap next while paused: 1". The sampler mins were
  1, inside the old min <= 2 tolerance: the old checker would
  have passed this. D1 catches it on every path. EXPECTED FAIL,
  GOT FAIL.
- M2, nextTrack stops the timer (stopTimer() as its first
  statement; a Next that kills the clock): FAIL, exit 1,
  10,871 ms, 6 failures: "position did not gain after next
  while playing: 0 to 0", "position after next while playing
  out of range 2-11: 0", "position did not gain again after
  next while playing: 0 to 0", and the same three for the
  shuffle Next. The exact-zero reads and sampler mins still
  pass (position is 0); only the three-point advancing checks
  catch it, on both the plain and shuffle paths. EXPECTED FAIL,
  GOT FAIL.
- M3, nextTrack resets position only when paused (position = 0
  changed to "if (!playing) position = 0" in nextTrack):
  FAIL, exit 1, 12,380 ms, 8 failures: "position not exactly 0
  after next while playing: 12", "position not reset after
  next: min observed 12 after 12", "position after next while
  playing out of range 2-11: 20", the same three for the shuffle
  Next (reads 90, 90, 99, after the seek set position to 90),
  and "position not exactly 0 after playing wrap next while
  playing: 7" plus its sampler failure. All frozen (paused)
  paths pass, exactly the defect's shape: the reset works
  paused and is skipped while playing. EXPECTED FAIL, GOT FAIL.

Verdict on the probes: 3/3 mutations caught, each by the D1
check written for it (exact-zero for M1/M3, advancing for M2).
The D1 checker is mutation-proven for these three defects on
Chromium.

## Verdict

- D1 t10 checker: SOUND. It passes the correct fixture on
  Chromium 10/10 twice and on Firefox 10/10 three times, and it
  fails all three of my mutation probes with the exact failure
  messages for each defect. Y12's "SOUND WITH NOTED DEFECTS" on
  the merged suite stands for the suite as a whole; for t10
  specifically, D1 closes the noted P2 hole (proven by M1).
- Full batch-3 suite with D1: 10/10 on Chromium (36 s) and
  10/10 on Firefox in 3 of 5 full runs (58-62 s). The two
  non-10/10 Firefox runs are fully explained: run 1 was a full
  /tmp disk (environment, fixed by moving Firefox out of /tmp),
  run 3 was two shim bugs I found and fixed (waitForLoadState
  about:blank hole, detached-node click) plus the pre-existing
  playlist-click race. No suite defect remains unaccounted for.
- Y10 t09/t10 on Firefox, which batch 5 left BLOCKED: t09 is
  now proven 2/2 standalone plus 10/10 in three full runs; t10
  is proven 2/3 standalone plus 10/10 in three full runs, with
  the one standalone failure being the known playlist-click
  race, not a D1 failure. The BLOCKED label for the Y10 Firefox
  rerun no longer applies.

## Still open / not verified

- The t10 final playlist-click race (fixture rebuilds the whole
  playlist every 100 ms while playing; a slow BiDi click can
  straddle a rebuild) is pre-existing and unfixed. It failed 1
  of 3 t10 standalones and 0 of 5 full runs on Firefox. On
  Chromium the same race exists in principle but the faster
  click makes it rarer. Fixing it means changing the fixture
  (e.g. not rebuilding the list on every tick) or the checker
  (e.g. pause before the final playlist click), which is a
  suite change, not a verification change, so I did not make it.
- The click detached-retry in the shim fixes only the variant
  that throws; the wrong-target variant throws nothing and can
  still fail a run. Same race as above.
- Everything on real Zen is still UNVERIFIED (Firefox 160.0.1
  only, headless, X11-less BiDi). The BiDi shim's dblclick and
  locator-center clicks are synthetic event dispatches or
  coordinate clicks, not real pointer drags; dragTo was not
  needed for batch 3.
- /tmp is 79% full again (111M free) with 90M of ff-b6-diag*
  profiles from other batch 6 agents. If another agent's
  Firefox hits the same localStorage failure, check /tmp first:
  Firefox stderr "No space left on device" is the tell.

## Evidence

- This report: docs/clone1-batch3-reverify-20261121.md
- Chromium run 1: /tmp/b6t3-run1-results.json (10/10, 36,367 ms)
- Chromium run 2: 10/10, 36,122 ms, numbers from the live run
  output recorded in this report; no separate file was saved for
  run 2 (only run 1's file exists). results.json in the tree was
  restored to the committed content after the Firefox runs, so
  the tree holds no run output from this task.
- Firefox full runs 1-5:
  ~/workspace/b6t3-results/batch3-firefox-run1.json (6/10),
  run2.json (10/10), run3.json (8/10), run4.json (10/10),
  run5.json (10/10)
- t09 standalone: ~/workspace/b6t3-results/t09-firefox-standalone-run1.json
  and run2.json (2/2 PASS)
- t10 standalone: ~/workspace/b6t3-results/t10-firefox-standalone-run2.json
  (PASS) and run3.json (FAIL, Night Drive race); run 1 passed
  on stdout, not saved to a file
- Mutation probes: ~/workspace/b6t3-scratch/control-suite,
  m1-suite, m2-suite, m3-suite (whole suite copies, only the
  t10 fixture nextTrack mutated), ~/workspace/b6t3-scratch/mutate.py
- Shim smoke + debug scripts: ~/workspace/b6t3-scratch/smoke.mjs,
  debug-t07-t08.mjs, debug-click.mjs, debug-ls.mjs, debug-ls2.mjs,
  debug-ls3.mjs, debug-ls4.mjs, debug-t09.mjs, and
  ff-stderr.log (the "No space left on device" evidence)
- Scratch installs: ~/workspace/b6t3-scratch (playwright-core
  1.55.0), ~/workspace/firefox-160.0.1 (browser, symlink at
  /tmp/firefox)

## Completion check (2026-11-22 02:21 +07, separate checker, original agent silent)

Verified from the saved files, no full re-run: all 5 Firefox run
JSONs match the report exactly (run1 6/10, 55,942 ms; run2 10/10,
60,522 ms; run3 8/10, 60,466 ms; run4 10/10, 62,095 ms; run5 10/10,
58,393 ms; per-test ms and the run1/run3 failure messages match).
Chromium run 1 file /tmp/b6t3-run1-results.json matches (10/10,
36,367 ms, per-test ms match). t09 standalones 2/2 PASS (7,691 ms,
7,266 ms). t10 standalone run2 PASS 16,926 ms with the D1 details
as reported; run3 FAIL only on the Night Drive race, all D1 reads
correct. All four check hashes match; t10 check last change is
1d23532, which is an ancestor of HEAD. The m1/m2/m3 fixtures contain
exactly the described nextTrack mutations; the control suite is
byte-identical to the committed tree; the shim is gone and the
batch3 tree is clean. Re-ran the M1 probe once as a single check:
exit 1, 6 failures with the exact messages in this report, sampler
mins 1, wall 13,909 ms, saved to
~/workspace/b6t3-results/m1-probe-recheck.json. ff-stderr.log holds
the "No space left on device" evidence; the Firefox install at
~/workspace/firefox-160.0.1 exists, but the /tmp/firefox symlink is
gone after a later /tmp wipe (environment, not a report error).
Not verifiable from files: Chromium run 2, t10 standalone run 1,
and the M2/M3 probe outputs were never saved (the report discloses
this); their numbers rest on the report record only.

Final verdict: DONE. D1 t10 checker SOUND, suite 10/10 Chromium
twice and 10/10 Firefox 3 of 5 runs, 3/3 mutation probes caught.
