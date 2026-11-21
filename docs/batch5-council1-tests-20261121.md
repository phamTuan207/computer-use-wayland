# Batch 5 council 1 (tests) verification, 2026-11-21

Council run 2026-11-21 about 14:10 to 14:20 UTC. Repo local HEAD
f006137. All numbers below are from my own runs and reads this
session, or are marked as read back from preserved files.

## Task 1 (Shayxo contract): CONFIRMED

- Ran `python3 -m unittest tests.test_glass_shayxo_contract` twice.
  Run 1: 17 tests, 0 failures, 0.029 s suite, 0.165 s wall.
  Run 2: 17 tests, 0 failures, 0.027 s suite, 0.109 s wall.
- Source of truth checked: native/hyprglass-local-optics.lua line 14
  has blur_strength = 0.15. The test asserts 0.15 in three places
  (lines 195, 207, 260, 345) and pad 12.75
  (test_legacy_pad_is_12_75_pixels, line 267, assertAlmostEqual
  12.75). The agent's claim of 17/17 twice holds exactly.

## Task 2 (AT-SPI self-contained session probe): PARTIALLY CONFIRMED

Deliverables exist and are correct:

- tests/run_atspi_session.sh, 250 lines, bash -n syntax OK.
- docs/research/2026-11-21-atspi-session-probe.md, 174 lines.
- Both files: 0 em dash, 0 en dash characters.
- Script uses dbus-launch (not dbus-run-session), exports
  GNOME_ACCESSIBILITY=1 and GTK_MODULES=gail:atk-bridge, activates
  the registry before Firefox starts, logs one JSON line per stage
  with wall clock and elapsed ms, cleans up on exit. All of this
  matches the doc's recipe section.
- The two bugs the doc says were fixed are in the code:
  tests/atspi_probe.py has find_documents (line 152) and
  find_in_document (line 187), and a dismiss mode (line 565).
- All prerequisites are present on this machine right now: Xvfb,
  dbus-launch, gdbus, python3, /usr/libexec/at-spi-bus-launcher,
  pyatspi import works.

Live re-run BLOCKED, not run by me:

- Firefox 160.0.1 at /tmp/firefox segfaults on startup. My own
  headless screenshot test at 14:10 UTC: exit 11, no screenshot
  file produced, fresh minidump 25e2afe9-737d-33c5-b32f-6e5fdb414e0c
  (240664 bytes) written to the profile minidumps dir. Host memory
  at the time: 146M free, 609M available. This matches the Y10
  retry log exactly (10 failed attempts 12:37 to 14:07 UTC).
- Per the task brief I stopped there and did not run the wrapper
  script, because it needs a working Firefox. Nothing about the
  live probe is claimed here from my own run.

Evidence gap in the task 2 deliverable, not a fabrication:

- The doc reports runs 3 to 6 at 12:04 to 12:05 UTC (run 3 total
  19212 ms, 125 nodes, click ok, type fail Bug 2087495). No raw log
  of those runs is preserved on disk (no atspi-session-run*.log
  found under ~/workspace or /tmp). The numbers rest on the doc
  alone. The timing is consistent (12:04 to 12:05 UTC is before
  Firefox broke at about 12:29 UTC), and council 3 independently
  reproduced the same recipe in batch 4, so I do not dispute the
  runs, but I cannot re-verify them from a log file.

## Task 5 (20 tests batch 2 + batch 3 on real Firefox): CONFIRMED, with 2 corrections

I re-read all 7 result files in ~/workspace/b5t5-results/ field by
field. Counts, walls and per-test times match the doc exactly:

- batch2 run1: 5 passed, 5 failed, wall 236231 ms. Fails: t04, t06,
  t08, t09, t10.
- batch2 run2: 10/10, wall 65122 ms. Per-test ms match the doc
  (5556, 11052, 4766, 6760, 5923, 7898, 5118, 5968, 5842, 6228).
- batch2 run3: 10/10, wall 63700 ms. Per-test ms match the doc
  (5048, 11403, 5265, 6528, 5603, 7831, 5734, 5033, 5258, 5958).
- batch3 run1: 1/9, wall 61256 ms. Only t07 passed.
- batch3 run2: 5/5, wall 83356 ms. Fails: t03, t04, t05, t09, t10.
- batch3 run3: 8/2, wall 61131 ms. Fails: t05, t10. t09 passed
  (8707 ms), as the doc says.
- batch3 run4: 10/10, wall 56623 ms. Per-test ms match the doc
  (5225, 4697, 5033, 5071, 5589, 5199, 5766, 5273, 7269, 7489).

Failure-cause diagnoses check out against the recorded stdout:

- batch2 run1: t06 "all 7 messages should show again" and "edited
  text missing", t08 "electronics should show 3 products" and
  "catalog should show 8 again" fit the fill('') not clearing bug;
  t10 "paid orders in range should be 3, revenue $187.97 got
  $49.98" fits the mangled ISO date; t09 timeout on the signal
  line; t04 "todo should be 3 after clearing filter" is also the
  fill('') clear bug. The doc names t06, t08, t10 and t09 but not
  t04. Minor omission, same root cause.
- batch3 run1: t01 and t05 "page.$$eval is not a function", t09
  "Timeout waiting for page event". Shim gaps, as stated.
- batch3 run2: t03, t05, t10 "page.$ is not a function", t09
  "detail window did not prefill Alpha". Shim gaps, as stated.
- batch3 run3: t05 crumbs and empty state wrong inside Archive
  (dblclick navigation never fired, as stated); t10 "now playing
  after clicking Night Drive: got Morning Light - The Demos, want
  Night Drive - The Demos", positionMinAfterNext 0. Matches the doc
  exactly, including the second t10 race being different from the
  exact-0 race.
- batch2 run1 t10 details show csvLines 9, which supports the doc's
  claim that the CSV export itself worked on Firefox.

Correction 1, the doc is wrong on one sentence:

- The doc says "No newer fix for t09 or t10 batch3 has landed on
  main or todolist-push after b629e11. The batch-4 version was run."
  That sentence is wrong about main at the time the doc was
  committed (12:25 UTC): commit ed78e83, "Y10: reconcile
  clone1-batch3 t05/t09/t10 fixes into one set", landed on main at
  12:19:42 UTC, about 5 minutes before the doc commit, and it
  changes t09 check.mjs (cancel case drops the verify callback for
  a 500 ms dwell, because the old verify proved nothing) and t10
  check.mjs (adds a "position must advance after next" check, so a
  stopped timer is caught). Both are real behavioral changes.
- Which check version the Firefox runs actually executed cannot be
  proven from the 7 JSONs: they record no check-file hash, and the
  Y10 changes leave no fingerprint in the recorded details. The
  agent states it ran the batch-4 version, and the Y10 followup
  treats the Y10 t09/t10 Firefox run as still pending, which is
  consistent with that. Note batch3 run4 started 12:21:45 UTC,
  after ed78e83 landed, so the ambiguity is real. The fix is to
  record the check-file hash in future result files, and to run the
  Y10 t09/t10 checks on Firefox when Firefox works again. This is
  an evidence gap, not a fabrication.

Correction 2, unpreserved standalone claims:

- The doc says "Standalone confirmations: t10 3/3 pass, t05 1/1
  pass." No JSONs for those standalone runs exist in
  ~/workspace/b5t5-results/ (only the 7 run files). I could not
  verify them from preserved evidence.

## Y10 followup evidence (t09/t10 Firefox part): CONFIRMED BLOCKED

Re-read ~/workspace/b5t5-results-y10/:

- t05 standalone on Firefox 3/3 pass: run1 6145 ms, run2 5925 ms,
  run3 5058 ms, all with finalHome ["budget.csv",
  "field-notes-7.txt", "Old Files 2026", "video.mp4"]. The novel
  names prove the Y10 checker ran. Plus one smoke pass 6800 ms
  noted in the README.
- t09 standalone 3/3 fail, all the same environment error, not a
  test failure: "could not connect to Firefox BiDi on port 19586 /
  19520 / 19338", each after a 30 s connect timeout (elapsed 30340,
  30284, 30285 ms).
- t10 standalone and the full batch3 run: NOT RUN. No JSONs exist
  for them, as the README says.
- ff-retry-log.txt: 10 attempts 12:37 to 14:07 UTC, all failed,
  minidump IDs listed. The last one, 22ee9d81, is on disk at
  /tmp/ff-retry-profile/minidumps/ (231120 bytes, timestamp 14:07).
  My own 14:10 UTC test adds an 11th failure with a fresh minidump.
- Verdict: the Y10 t09/t10 Firefox part is BLOCKED, not run.
  The README states this plainly and the files back it up.

## t05 fix (08f36d2 + Y10 ed78e83): CONFIRMED in code

- Fixture: rename dialog exists (#rename-input, #rename-save,
  #rename-cancel, #rename-error). The save handler takes the new
  name from the input value and rejects an empty name. The old
  hardcoded mapping (notes.txt to meeting-notes.txt, Archive to
  Old files) is gone: grep for meeting-notes and "Old files" in
  the t05 directory returns nothing.
- Check: fills check-chosen novel names (field-notes-7.txt,
  "  Old Files 2026  " with surrounding spaces to test trim,
  budget2.csv for the cancel case), checks the prefill, checks
  Cancel leaves the name, checks an empty name is rejected with
  the error shown and the dialog still open.
- Committed results.json at HEAD: t05 pass true, 2983 ms,
  finalHome with the novel names.
- Firefox evidence: Y10 t05 3/3 pass above.
- My own Chromium standalone re-run: BLOCKED by the environment,
  not by the test. Two attempts at 14:10 UTC both died at browser
  launch: "browserType.launch: Target page, context or browser has
  been closed", Chromium pid killed with SIGTRAP before any page
  loaded. Host memory was 146M free / 609M available on the first
  attempt, 385M free / 848M available on the second. The test
  itself never ran, so this is not a t05 failure and not a t05
  pass. Re-run it when host memory pressure eases.

## Environment note for the coordinator

- Shell writes fail with EPERM intermittently in this session
  (git status hit "Operation not permitted" on .git/index.lock).
  This report was written with the file tool, as instructed.
  The Y10 README notes the same EPERM window for most of
  12:37 to 14:08 UTC.
- Firefox 160.0.1 is unusable on this machine right now
  (segfault, exit 11, since about 12:29 UTC) and Chromium
  launch also died twice (SIGTRAP). Any live-browser claim made
  after 12:29 UTC today needs a fresh browser test, not a quote
  of earlier numbers.

## Verdicts summary

- Task 1 Shayxo: CONFIRMED. 17/17 twice by my own runs.
- Task 2 AT-SPI probe: PARTIALLY CONFIRMED. Script and doc are
  correct and all prerequisites are present, but the live re-run
  is blocked by the Firefox segfault, and the doc's run numbers
  have no preserved raw log.
- Task 5 Firefox 20/20: CONFIRMED, with the "no newer fix landed"
  sentence corrected (ed78e83 did land before the doc commit) and
  the standalone t10 3/3 and t05 1/1 claims noted as unpreserved.
- Y10 t09/t10 Firefox: CONFIRMED BLOCKED, not run.
- t05 fix: CONFIRMED in code and in the Y10 Firefox 3/3 runs.
  My Chromium re-run was blocked by the environment.
