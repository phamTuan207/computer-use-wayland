# Task experiments

These experiments separate scripted application outcomes from protocol mocks,
image fixtures and model/tool latency. No model API was called. Test reports
contain timing samples and synthetic task metadata; no real application titles,
identifiers, profile contents or desktop screenshots belong in public results.

## GTK task baseline

`tests/optimization_live.py` owns one automation session and an unused workspace.
Its GTK fixture resets before each task and publishes the actual entry contents,
click count, scroll offset and draggable rectangle position. Typing checks exact
Unicode codepoints; drag must begin inside the rectangle and reach its expected
position. The scroll task checks direction, not a portable pixel distance.
Cleanup preserves cancellation and verifies workspace restoration before marking
the report successful. Failed samples remain in the report.

A staging runtime used current source scripts and the installed native helpers
and accepted local indicator/cursor profile. This was not installed acceptance.
The initial setup attempt failed before opening a fixture because its workspace
command used obsolete syntax. The harness now uses the machine's Lua dispatch
and verifies the actual workspace transition.

Three successful samples per task, at 1920x1200, scale 1, transform 0:

| Task | Median ms | p95 ms |
|---|---:|---:|
| Type 32 characters | 410.646 | 423.797 |
| Type 481 characters | 2376.693 | 2389.538 |
| Ctrl+A and replace text | 298.272 | 307.586 |
| Click and verify count | 286.805 | 288.276 |
| Scroll and verify positive offset | 300.264 | 301.501 |
| Drag and verify position | 411.233 | 418.034 |

These are smoke baselines, below the sample count required to retain a speed
optimization. Timing includes the resident CLI action, safety preflight, default
final capture and an independent fixture-state check; the initial observation
and fixture reset occur before timing. It excludes model reasoning/tool overhead.

## Rejected keyboard prototype

A private project-local prototype mapped literal BMP text to printable physical
key positions, reserved a trailing VoidSymbol and limited each helper invocation
to 32 codepoints. The first candidate retained the stock 2 ms press/release pacing
and used a parent guard and a 5 second keyboard-action deadline. The system wtype,
source input path and installed input path were not changed.

Three GTK samples per payload produced medians of 412.711 ms for 32 characters
and 2478.192 ms for 481 characters. Both payloads matched exactly in the ordinary
fixture. This did not demonstrate a speedup.

An isolated fault test deliberately focused a second inert GTK window during
typing. The target received 40 characters and the other window received 24 before
the next guard stopped the batch. The candidate failed the safety gate and was
removed from the staging runtime. The unpaced candidate was not live-tested or
enabled. Parser/keymap checks and a corrected stdin signal bug do not establish
application correctness or focus safety. This experiment did not test whether
the stock backend has the same focus behavior.

Further keyboard work requires reviewing how input is bound to its intended
target while focus can change. Smaller sleeps or faster ACKs do not establish
that guarantee. No compositor plugin replacement, independent seat or system
keyboard installation was attempted.

## Browser recipe comparison

`tests/browser_task_benchmark.py` compares existing API recipes on an inert
Chromium profile and loopback page. Both routes fill the same Unicode payload,
click Save and assert the specific result. The split route uses four requests:
fill, click, a fixed 80 ms wait, then assert. The batch route uses one request
containing fill, click and assert. Both use the existing session-owned Node worker
and fresh CDP connections; this is not a new backend optimization.

The page changes its state after a configured delay and independently reports
the exact submitted text to the fixture server. Every measured task must pass
that check. No screenshot freshness or physical keyboard behavior is inferred
from DOM results. Warm runs perform an unmeasured task per route first, alternate
AB/BA order and retain raw timings, request counts and result byte counts. Cold
runs require one task and one route in each fresh session/profile.

Acceptance thresholds were set before measurement: three blocks of 30 warm
samples per route, median task improvement at least 10% and 5 ms, p95 regression
no greater than max(5%, 2 ms), and ten cold sessions per route with no median
regression greater than max(10%, 10 ms). All measured tasks must be correct;
never-ready conditions must fail rather than claim success. Percentiles use
nearest rank, `ceil(.95*n)-1` in a zero-indexed sorted array.

Measured on the host's isolated Chromium fixture: three blocks per delay,
90 warm samples per route and delay (900 measured tasks total), all exact
application results correct. Every block passed the thresholds above.

| Fixture delay ms | Split median / p95 ms | Batch median / p95 ms |
|---|---:|---:|
| 0 | 109.312 / 114.351 | 70.940 / 78.784 |
| 16 | 109.768 / 115.002 | 71.879 / 76.887 |
| 50 | 110.378 / 117.780 | 73.124 / 79.492 |
| 100 | 162.515 / 168.550 | 123.857 / 129.593 |
| 250 | 316.988 / 322.370 | 277.182 / 283.127 |

Ten fresh sessions per route also produced correct results. Complete-session
median was 1717.609 ms split and 1717.673 ms batch: no meaningful cold-session
speedup. First-task medians were 314.643 and 275.270 ms respectively; startup
still dominates the complete session. At zero delay, requests fell from four to
one and median result bytes from 1373 to 344. These are bytes, not billed tokens.

Never-ready fixtures failed both routes with cleanup successful. Initial negative
runs stopped during their warm-up; the cold reproduction command below checks a
measured failure without warm-up. Reports now checkpoint outside timing using
atomic replacement, retain unsuccessful status until cleanup completes, and
preserve the last complete checkpoint if writing fails. This report-only change
followed the full timing run and is covered by focused tests and final live smoke.
The retained improvement is guidance to batch known actions with a specific
result assertion. It is not evidence that every website is faster or that DOM
fill is equivalent to trusted physical keyboard input.

## Reproduce

Run the live harnesses sequentially, outside an existing automation session.
They temporarily own the foreground, create disposable fixtures, preserve the
selected engine's session profile and restore focus/workspace when appropriate.
Choose an engine whose approved local indicator/cursor configuration is present.
Each `--cli` determines the runtime root for the fixture and adapter as well as
the session guardian. Use a fresh private report file for each run.

```sh
python3 tests/optimization_live.py --cli /path/to/runtime/scripts/cu.py --samples 3 --report /private/gtk.json
python3 tests/browser_task_benchmark.py --cli /path/to/runtime/scripts/cu.py --samples 30 --delay 50 --report /private/browser.json
python3 tests/browser_task_benchmark.py --cli /path/to/runtime/scripts/cu.py --cold --samples 1 --modes batch --report /private/cold.json
python3 tests/browser_task_benchmark.py --cli /path/to/runtime/scripts/cu.py --cold --samples 1 --modes batch --delay -1 --report /private/never-ready.json
```

The never-ready run is expected to exit unsuccessfully and retain a failed task
row. It must not retry the click. Baseline and candidate comparisons require the
same fixture, runtime, display settings, payload and host load. Repeat three
blocks and ten cold sessions per route rather than treating one command as a
complete comparison. `tests/control_benchmark.py --raw-samples` also reports
nearest-rank p95 for its read-only command and image benchmarks; its synthetic
images are not live desktop measurements.

## Final validation

The final source unittest suite ran 284 tests in 24.139 seconds: no failures,
one optional skip. Capture/adapter regressions and the no-magnifier check passed.
These include mocks, synthetic images and protocol fixtures, separate from live
application checks. A second read-only reviewer checked the atomic checkpoints
and privacy boundaries; the reviewer did not independently recompute raw timings.

Only nine reviewed test/documentation files were synced to the installed tree,
with backups and matching hashes. Runtime scripts, native binaries, approved
indicator/cursor profiles and compositor plugin were unchanged. Installed smoke
used the actual installed executable and matching installed drivers: one GTK
sample for each of six tasks, three browser samples per route at 50 ms delay,
and one never-ready cold task per route. Positive tasks passed; negative tasks
failed as expected; all reported cleanup successful. All 17 focused installed
tests passed. This is installed smoke plus focused tests, not full installed-tree
parity or a second full performance comparison.
