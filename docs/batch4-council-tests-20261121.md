# Batch 4 council verification: realistic tests, batch 2 and 3

Council member 1, independent re-run. I did not trust any number in
coord/clone1.md or any agent report. Every number below comes from a
run I did myself in this session, 2026-11-21, on this machine.

## Environment and method

- Repo HEAD beffa19, working tree clean except an unrelated council
  file (docs/batch4-council-audits-20261121.md, not mine).
- Node v24.22.1, Playwright Chromium 1254 from
  ~/.cache/ms-playwright/chromium-1254/chrome-linux64/chrome.
- playwright-core 1.55.0, installed fresh by me into
  /tmp/council-b4-scratch, because /tmp/realistic-b2-scratch named
  in the task no longer exists (scratch under /tmp is wiped between
  runs). Env var PLAYWRIGHT_CORE_PATH pointed at that install for
  every run below.
- Each suite ran twice in full. Each of the 3 flaky tests ran
  standalone 3 times. I did not modify any test file or fixture.
- Raw evidence kept in ~/workspace/council-b4/: per-run results.json
  copies, runner logs, standalone logs, step-mapping.txt.

## Incident during the runs: /tmp full

- /tmp is a 512M tmpfs. During the batch3 run 1, it hit 100% full.
  Largest occupants: /tmp/firefox 331M (the AT-SPI Firefox install),
  /tmp/firefox-160.0.1.tar.xz 87M (installer tarball),
  /tmp/scan 76M.
- Batch3 run 1 itself exited 0, but its stdout log file was 0 bytes
  and the results.json copy to /tmp failed. I recovered run 1 numbers
  by reading the live repo results.json immediately after the run,
  before run 2 overwrote it. Those numbers are in the table below.
- I freed space by deleting only /tmp/firefox-160.0.1.tar.xz, the
  re-downloadable installer tarball. The extracted Firefox at
  /tmp/firefox was left untouched. I did not delete /tmp/scan or any
  other agent scratch.
- Later, the repo results.json files were back to their committed
  content (clone1 09:30:11Z 10/10, batch2 09:46:53Z 9/10, batch3
  09:41:30Z 8/10). Someone or something restored them after my runs.
  My run outputs survive in the ~/workspace/council-b4/ copies
  listed above.

## Suite 1: tests/realistic/clone1 (batch 2 task 1)

Run 1, started 2026-11-21T11:24:59Z, wall 22151 ms, 10 passed,
0 failed, exit 0.

| test | pass | elapsed ms |
|---|---|---|
| t01-upload-single | pass | 4804 |
| t02-upload-multi-error | pass | 2096 |
| t03-long-form | pass | 2472 |
| t04-long-form-draft | pass | 2039 |
| t05-multi-tab | pass | 2131 |
| t06-popup-dialog | pass | 1890 |
| t07-download-check | pass | 1545 |
| t08-login-auth | pass | 1854 |
| t09-upload-metadata | pass | 1589 |
| t10-login-upload-download | pass | 1720 |

Run 2, started 2026-11-21T11:25:21Z, wall 17218 ms, 10 passed,
0 failed, exit 0.

| test | pass | elapsed ms |
|---|---|---|
| t01-upload-single | pass | 2120 |
| t02-upload-multi-error | pass | 1507 |
| t03-long-form | pass | 1416 |
| t04-long-form-draft | pass | 1549 |
| t05-multi-tab | pass | 1925 |
| t06-popup-dialog | pass | 2904 |
| t07-download-check | pass | 1516 |
| t08-login-auth | pass | 1484 |
| t09-upload-metadata | pass | 1363 |
| t10-login-upload-download | pass | 1423 |

No failures in either run. No failure message to record.

## Suite 2: tests/realistic/clone1-batch2

Run 1, started 2026-11-21T11:25:40Z, wall 32210 ms, 10 passed,
0 failed, exit 0.

| test | pass | elapsed ms |
|---|---|---|
| t01-pdf-form | pass | 2055 |
| t02-video-player | pass | 7946 |
| t03-keyboard-nav | pass | 1445 |
| t04-kanban-drag | pass | 4044 |
| t05-canvas-draw | pass | 2962 |
| t06-chat-app | pass | 4648 |
| t07-map-directions | pass | 2285 |
| t08-cart-checkout | pass | 2265 |
| t09-diff-review | pass | 2573 |
| t10-dashboard | pass | 1977 |

Run 2, started 2026-11-21T11:26:12Z, wall 34697 ms, 10 passed,
0 failed, exit 0.

| test | pass | elapsed ms |
|---|---|---|
| t01-pdf-form | pass | 2110 |
| t02-video-player | pass | 8241 |
| t03-keyboard-nav | pass | 1830 |
| t04-kanban-drag | pass | 4534 |
| t05-canvas-draw | pass | 3428 |
| t06-chat-app | pass | 5116 |
| t07-map-directions | pass | 1949 |
| t08-cart-checkout | pass | 2490 |
| t09-diff-review | pass | 2938 |
| t10-dashboard | pass | 2048 |

No failures in either run. The earlier t10 "download.path: canceled"
failure was NOT reproduced in my runs.

## Suite 3: tests/realistic/clone1-batch3

Run 1, started 2026-11-21T11:26:49Z, wall 52967 ms, 10 passed,
0 failed, exit 0. Numbers read from the live repo results.json
(see the /tmp incident above).

| test | pass | elapsed ms |
|---|---|---|
| t01-terminal | pass | 5428 |
| t02-spreadsheet | pass | 4041 |
| t03-video-call | pass | 3765 |
| t04-email-client | pass | 3504 |
| t05-file-manager | pass | 5668 |
| t06-calendar | pass | 3204 |
| t07-code-editor | pass | 5709 |
| t08-settings-panel | pass | 4401 |
| t09-multi-window | pass | 8418 |
| t10-music-player | pass | 8781 |

Run 2, started 2026-11-21T11:27:59Z, wall 42198 ms, 9 passed,
1 failed, exit 1.

| test | pass | elapsed ms |
|---|---|---|
| t01-terminal | pass | 2339 |
| t02-spreadsheet | pass | 3812 |
| t03-video-call | pass | 2288 |
| t04-email-client | pass | 3132 |
| t05-file-manager | pass | 2493 |
| t06-calendar | pass | 3989 |
| t07-code-editor | pass | 4534 |
| t08-settings-panel | pass | 3597 |
| t09-multi-window | pass | 6204 |
| t10-music-player | FAIL | 9799 |

Exact failure message, t10-music-player run 2: "position not reset
after next". That is the same message the coordinator saw in a
second re-run on 2026-11-21.

## Standalone runs of the 3 flaky tests, 3 times each

All 9 standalone runs passed. Times are elapsed ms per run.

Batch3 t09-multi-window, 2026-11-21T11:28:48Z to 11:29:04Z:
pass 4784, pass 5095, pass 5470. Final titles in all 3 runs:
Alpha Final, Beta, Gamma v2.

Batch3 t10-music-player, 2026-11-21T11:29:04Z to 11:29:18Z:
pass 5157, pass 4920, pass 3727. Details in all 3 runs:
positionAfter700ms 7, positionAfterSeek 90.

Batch2 t10-dashboard, 2026-11-21T11:29:18Z to 11:29:25Z:
pass 1784, pass 2328, pass 2019. Details in all 3 runs: csvLines 9,
all 40 steps listed in the result.

## Flakiness verdicts

- Batch3 t10-music-player: FLAKY, confirmed. Failed 1 of 2 full
  runs in my session ("position not reset after next"), passed 3 of
  3 standalone. Likely mechanism, read from the checker: after
  clicking Next, the checker asserts the position is 0, but the
  fixture position advances on a timer, so under full-suite load
  the assertion can run after the position has already moved past
  0. The test is timing-sensitive, not logic-broken. Do not quote
  batch3 as a stable 10/10.
- Batch3 t09-multi-window: STABLE in my session. Passed 2 of 2 full
  runs and 3 of 3 standalone. The earlier "Target page has been
  closed" failure is gone after the clickAndClose fix in check.mjs.
  The earlier "main window missing dark class after prefs dark"
  failure was NOT reproduced in my runs.
- Batch2 t10-dashboard: STABLE in my session. Passed 2 of 2 full
  runs and 3 of 3 standalone. The earlier "download.path: canceled"
  failure was NOT reproduced in my runs.
- All other 27 tests: passed every full run (2 of 2 each). No other
  flakiness observed in this session.

## README step counts vs checkers, all 30 tests

- Batch2, all 10 tests: EXACT match. README header count equals the
  bullet count equals the step() call count in check.mjs: t01 36,
  t02 35, t03 35, t04 36, t05 36, t06 40, t07 27, t08 40, t09 24,
  t10 40. All inside 15-40.
- Clone1, all 10 tests: match by reading. READMEs list 5, 7, 6, 7,
  6, 6, 5, 6, 5, 6 numbered steps, and each step maps to an action
  in the checker. Two cases needed a closer look and both check out:
  t04 step 2 selects type batch, which is the fixture default, and
  the checker asserts the interactive fields are hidden for batch
  before selecting interactive; t05 uses list and detail page
  variables instead of page, and t07 and t10 handle downloads with
  waitForEvent('download'), which my first grep pattern missed.
- Batch3, all 10 tests: match by reading. READMEs list 20, 19, 19,
  19, 20, 17, 17, 16, 12, 20 numbered steps, and each step maps to
  an action in the checker. Two cases needed a closer look: t02 uses
  set and expect helpers (21 set calls, 19 expect calls for 19
  steps); t06 uses an addEvent helper called 3 times plus the inline
  Team sync fill, covering all 4 event-creation steps.
- No README step count mismatch found in any of the 30 tests.

## Fixtures offline, all 30 tests

- Grep over every fixture.html, check.mjs, and .vtt in all three
  suites for external URLs (http/https src, href, fetch, import,
  url()). Total hits: 7, all benign.
- 4 hits are the SVG namespace string http://www.w3.org/2000/svg
  in batch2 t07-map-directions/fixture.html. That is a namespace
  identifier, not a fetch.
- 3 hits are http://127.0.0.1:${port} in lib/server.mjs of each
  suite. That is the local loopback test server, not external.
- 0 non-local src or href attributes in any fixture HTML. No CDN,
  no external fetch, no external import in any fixture or checker.
- All fixtures are offline. The t02 video clip in batch2 is a local
  mp4 generated with ffmpeg.

## Discrepancies vs the batch 2/3 report (coord/clone1.md)

- Clone1 suite: report says 10/10, wall 41534 ms. My runs: 10/10
  twice, wall 22151 ms and 17218 ms. Pass count agrees. My walls are
  faster; the report run happened under heavier parallel load
  (load average 7.68 at the time). No discrepancy in outcome.
- Batch2 suite: agent report says 10/10 twice, wall 35265 ms and
  32079 ms. My runs: 10/10 twice, wall 32210 ms and 34697 ms.
  Agrees. The coordinator's separate re-run saw 9/10 once with
  t10 "download.path: canceled"; I did not reproduce that, which
  supports it being a load-timing flake rather than a stable defect.
- Batch3 suite: agent report says 10/10, wall 27033 ms. My run 1:
  10/10, wall 52967 ms (much slower, machine load). My run 2: 9/10,
  t10 failed with "position not reset after next". The coordinator's
  re-runs also saw 9/10 and 8/10 with t09 and t10 failures. The
  agent's 10/10 claim does not hold as a stable result. The honest
  statement is: batch3 passes 10/10 when the machine is quiet and
  t10 is timing-lucky, and fails t10 intermittently under load.
- The batch3 agent's per-test numbers (t01 3686, t02 1932, t03 2033,
  t04 2428, t05 2227, t06 2570, t07 2601, t08 1911, t09 3239,
  t10 4396 ms) are all lower than my run 1 numbers. That is
  consistent with load differences, not with fabricated numbers.
  My run 1 per-test times are roughly 1.5x to 2.5x the agent's,
  which matches a loaded machine.
- No test outcome in the batch 2/3 report was contradicted by my
  runs except the implied stability of batch3 10/10. No test that
  the report says passes was found to be deterministically broken.

## Overall verdict

- 29 of 30 tests are stable: they passed every full run I did
  (2 of 2 each) and, where tested standalone, 3 of 3.
- 1 test, batch3 t10-music-player, is flaky under full-suite load:
  1 failure in 2 full runs, 0 failures in 3 standalone runs.
  Fix the timing assertion (position reset after Next) before
  quoting batch3 as 10/10.
- Step counts match the checkers for all 30 tests. All fixtures
  are offline. No test file or fixture was modified by me.
- The suites are real tests that drive real DOM state with real
  input. They are not self-graded: the checkers assert DOM state,
  downloads, and file contents, and they do fail when the fixture
  misbehaves (t10 proved that in run 2).

## UNVERIFIED

- All runs here are Playwright Chromium 1254. The same 30 tests on
  Firefox or Zen are unverified by me. That is out of scope for
  this task.
- I did not verify the batch 5 Firefox run of these suites. That is
  a separate task.
