# Run report: 10 realistic tests, 2026-11-21

Run date: 2026-11-21, 09:30:11Z to 09:30:52Z (UTC).
Runner: node tests/realistic/clone1/run_all.mjs, exit 0.
Result: 10 passed, 0 failed. Wall clock 41534 ms.

## Environment check first: no Firefox on this machine

Checked before the run, 2026-11-21 about 09:30Z:

- `which firefox firefox-esr zen zen-browser`: nothing found.
- `/usr/lib/firefox*`, `/opt/firefox*`, `~/.mozilla`: none exist.
- No Flatpak or snap Firefox/Zen found.
- Playwright Chromium 1254 is cached under ~/.cache/ms-playwright.
- playwright-core 1.55.0 was reused from /tmp/realistic-b2-scratch,
  installed there by a sibling batch 2 agent. The original
  /tmp/realistic-scratch install from the first batch is gone.
- Machine at run time: Node v24.22.1, Python 3.12.3, 4 CPUs, 7.9 GB RAM.
  Load average was 7.68 at 09:31:33Z, so the machine was busy with
  parallel work. That is the likely reason this run took 41.5 s wall
  clock while the same suite took 16.0 s on 2026-11-21 at 08:26Z.

Because there is no Firefox, the assignment's real-Firefox run with
the WebExtension bridge could not be done. Nothing about Firefox was
faked. The tests ran on Playwright Chromium 1254 headless, and the
bridge was exercised only through its node harness on a fake DOM and
its Python host tests. See UNVERIFIED below.

## Per-test results

Times are real, from results.json. runner_ms includes browser launch
and the child process. check_ms is the time inside check.mjs.
No test was edited to make it pass.

| test | pass | runner_ms | check_ms | started_at (UTC) |
| --- | --- | --- | --- | --- |
| t01-upload-single | pass | 5365 | 5256 | 2026-11-21T09:30:11.231Z |
| t02-upload-multi-error | pass | 2323 | 2224 | 2026-11-21T09:30:16.586Z |
| t03-long-form | pass | 2225 | 2102 | 2026-11-21T09:30:18.933Z |
| t04-long-form-draft | pass | 5112 | 4928 | 2026-11-21T09:30:21.217Z |
| t05-multi-tab | pass | 5051 | 4783 | 2026-11-21T09:30:26.348Z |
| t06-popup-dialog | pass | 5999 | 5602 | 2026-11-21T09:30:31.528Z |
| t07-download-check | pass | 3632 | 3363 | 2026-11-21T09:30:37.462Z |
| t08-login-auth | pass | 4718 | 4119 | 2026-11-21T09:30:41.418Z |
| t09-upload-metadata | pass | 3448 | 3102 | 2026-11-21T09:30:45.832Z |
| t10-login-upload-download | pass | 3624 | 3215 | 2026-11-21T09:30:49.322Z |

What each test confirmed, from its recorded details:

- t01: uploaded t01-statement.txt, 38 bytes, checksum 258f5a4f,
  confirmation text matched.
- t02: 3 files uploaded, the 100 KB file failed the 64 KB limit,
  final result lists only the two valid files.
- t03: empty submit showed 4 required-field errors, then the 14-field
  form created the problem with difficulty medium.
- t04: conditional interactive fields appeared, draft restored from
  localStorage after reload, problem created as interactive.
- t05: 5 tabs, detail tab title edited to "Edited Title Two", list tab
  showed the new title after refresh.
- t06: alert accepted, confirm dismissed as cancelled, prompt returned
  "Reviewer", modal note saved, popup window posted back
  "Popup Tester".
- t07: downloaded CSV has 6 lines, header id,input,expected, checksum
  ed70e477.
- t08: short code rejected with length error, valid demo code logged
  in, review action worked, session survived reload, logout hid the
  protected page.
- t09: empty form and .png file rejected, valid .txt created problem
  P-1042.
- t10: login, upload of a 4-case file, judge verdict PASS, downloaded
  report contents verified.

## Errors observed

None. Every test reported failures [], and stderr was empty for all
10 tests. No click miss, no stale observation, no timeout, no slow
step was recorded in this run. Per-step wall-clock times are not
instrumented by the existing check scripts, which only record
per-test times, so no per-step numbers are given here. None were
invented.

## Bridge checks run alongside

- node tests/webext-native-bridge/content_node_test.mjs:
  16 checks, 0 failures, exit 0, 09:31:09.633Z to 09:31:09.692Z
  (59 ms). Covers snapshot, click, type, scroll, hover, select,
  upload, waitFor, evaluate, and error cases on a fake DOM.
- python3 tests/test_webext_native_bridge.py: 16 tests, OK,
  12.212 s, finished 09:31:22Z. Covers host relay, new-op forwarding,
  status counters, and install check/uninstall/policies/sign round
  trips against a temp HOME.

Both are host-side or fake-DOM checks only. They do not prove the
bridge works inside a real browser.

## UNVERIFIED, exact blocker

- All 10 flows on a real Firefox and on Zen. No Firefox or Zen binary
  exists on this machine, so every browser run here is Playwright
  Chromium 1254.
- The WebExtension bridge on a real browser: extension load, native
  connect, all 10 ops against a real tab with per-op timing,
  install.py and --check on the laptop, the signed permanent install
  path, and the policies force-install path.
- Per-op timings on Zen, and any comparison of Chromium timings here
  with Zen timings. Run the same checks against Zen on the laptop
  before quoting any Zen timing.

## Files

- tests/realistic/clone1/results.json (rewritten by this run)
- tests/realistic/clone1/RUN-LOG-20261121.jsonl (one JSON object per
  line: run header, environment, each test, bridge checks, summary)
