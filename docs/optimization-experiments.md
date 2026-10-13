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
application correctness or focus safety. This prototype experiment did not test
the stock backend; the later installed diagnostics below tested that separately.

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

## Browser `act --no-after` A/B on the source fixture

Measured A/B of the opt-in `browser act --no-after` flag against the same batch
route without it. `tests/browser_task_benchmark.py` drives an inert real
Chromium fixture from the source tree: `set_value`, `click` on Save, then a
final `assert` on the status text. Both routes send one request with the same
actions and the same payload length; only the flag differs. The payload carries
a per-run nonce plus the sample index and mode, so a stale field left by the
previous route or sample can never satisfy the assertion. `max_elements` stayed
at 8. `--controls` adds inert inputs so the after-snapshot pays real DOM
enumeration cost; `max_elements` unchanged.

3 blocks x 30 pairs = 90 samples per route per controls value, AB/BA alternated
by pair within each block; controls order was flipped in the middle block. 360 measured tasks plus 12
unmeasured warm-ups, all exact, independent server POST verification on every
task, cleanup clean. The worker is warm, but every request gets a fresh CDP
connection. The timed span is the worker task request **plus** the independent
app verification; compile, setup and the initial observe sit outside the timer.
Result bytes are `len(json.dumps(result, ensure_ascii=False).encode(UTF-8))`.
No live LLM or API billing was measured — these are bytes, not tokens.

Declared criteria: no regression when candidate median <= baseline median +
max(10%, 10 ms); p95 <= baseline p95 + max(10%, 5 ms); speed win only at median
reduction >= 10% **and** >= 5 ms; output reduction >= 50% of median re-encoded
result bytes, which is accepted **separately** from any speed win.

| Controls | Baseline median / p95 ms | Candidate median / p95 ms | Median cut | Bytes cut |
|---|---:|---:|---:|---:|
| 0 | 38.458 / 84.282 | 37.440 / 84.861 | 2.647% (1.018 ms) | 79.360% |
| 1000 | 76.814 / 100.788 | 55.870 / 91.350 | 27.267% (20.945 ms) | 91.676% |

**Speed win: only at controls 1000.** Both conditions hold there (27.267% and
20.945 ms) and the p95 improves in all three blocks. At controls 0 the median
reduction is 2.647% / 1.018 ms, far below both thresholds, so
`speed_win = false`. No regression and the p95 bound both pass at both values,
and the output gate passes at both.

**Small-page p95 variability, disclosed.** At controls 0 the aggregate p95
barely moves (84.282 -> 84.861 ms) while the per-block numbers swing widely
(blocks numbered 0..2): block 0 84.282 -> 84.861 ms, block 1 86.908 -> 85.720 ms,
block 2 **48.372 -> 80.253 ms** — 31.881 ms worse. The small-page tail is not a
consistent improvement and must not be read as one; block 2 is the clearest case
where the candidate's p95 is far worse than the baseline's. At controls 1000 all
three blocks improve on both median and p95 (100.788 -> 90.051, 100.762 ->
88.603, 103.064 -> 92.835 ms).

Method note: the earlier `fill`-based batch figures above are **historic**. The
current `batch` mode uses `set_value` so both batch routes are focus-independent;
it is therefore not the same backend as that historical comparison, and the two
tables are not directly comparable.

Startup smoke failures before the fixture-readiness fix are excluded from these
figures; readiness is now established before any input is sent.

Output reduction is accepted as a separate opt-in criterion: at controls 0 the
median result drops 344 -> 71 bytes and at controls 1000 853 -> 71 bytes, both
well past the 50% gate, with no speed win claimed at controls 0. Not installed
or verified in the installed tree at the time of this measurement.

Reproduce one block per command; repeat three blocks with distinct report names
and alternate the controls order (reports stay outside any public repo):

```bash
python3 tests/browser_task_benchmark.py --report /private/report.json --controls 0 \
  --modes batch batch-no-after --samples 30
python3 tests/browser_task_benchmark.py --report /private/report.json --controls 1000 \
  --modes batch batch-no-after --samples 30
```

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

## Installed keyboard diagnostics

Follow-up on 2026-10-13 used the installed CLI/session and installed input code,
stock wtype 0.4-2, temporary Chromium profiles and synthetic fixture values.
No production profile or compositor plugin was changed.

The desktop string `Tạo báo cáo nháp — 3 mục` produced
`Tạo báo cáo nháp — 3 c` both at delay_ms=45 and delay_ms=0 (one trial each).
Application events recorded key `ụ`, physical code `Backspace`, followed by a
trusted `deleteContentBackward` input event. ASCII `abcdefghijklmnop`, `mục`,
`Tiếng Việt` and a leading-dash version of the full sentence matched in one trial
each; `abcdefghijklmục` also failed. These seven diagnostic trials demonstrate a
keymap-dependent correctness bug, not a Unicode-wide failure rate or an IME fix.
This matches the mechanism described in
[wtype's control-key collision proposal](https://github.com/atx/wtype/pull/77).
That proposal was not installed or validated here. Slower typing is not a fix.

A separate fault injection used two inert GTK windows on an unused workspace.
During a 481-character stock typing action, focus was deliberately moved to the
second fixture. The target received 44 characters and the other fixture 436;
the action eventually returned a failure. This single trial establishes that
between-group focus guards do not bind ongoing keyboard input to its target.
It does not establish the missing character's cause, a leakage-rate distribution,
or any repair. Both fixtures were closed and the previous workspace/focus restored.

For the practical browser route, a new installed `fill`/`click`/result-assert smoke
ran three measured warm tasks with exact Vietnamese-plus-emoji fixture values.
All passed the independent application callback check; median 72.904 ms,
nearest-rank p95 76.919 ms. This is smoke, not another speed comparison, and does
not prove desktop keyboard safety or identical behavior in other applications.

A private copy of the same harness then used the exact failing demo sentence
instead of its usual payload. All three measured warm DOM tasks matched the full
sentence via the independent callback, with cleanup successful. These are output
checks, not evidence that the desktop keyboard bug has been repaired.

## Browser field assignment with routing faults

`set_value` is a browser-only alternative for ordinary text inputs and
textareas. It resolves one snapshot reference or one unique selector, does not
click or change focus, uses the element's native value setter, dispatches
synthetic `input` and `change` events, then checks that the same connected
element still contains the requested value. These events are not trusted
keyboard input; pages that require trusted events need a different route.
Always verify the app's own result with a following `assert` or another
independent check. A matching DOM value alone does not prove an app accepted it.

`tests/browser_field_live.py` ran against an isolated Chromium profile and a
loopback-only fixture using the source tree. The fixture reproduced both a
wrong-field write and a false `fill` success after focus changed; the new setter
left the decoy untouched and its Save/result assertion matched the requested
Vietnamese text. The run also verified that its input event was synthetic. This
was one live correctness run per case, not a speed benchmark or a claim about
arbitrary web apps. The test owns its disposable profile and restores focus and
workspace when possible.

Keyboard input still has an unresolved focus race. During investigation,
terminating stock `wtype` while Ctrl was held did not let the owned GTK fixture
confirm that Ctrl had been released. Upstream `wtype` does not install a signal
cleanup handler, and the issue is reported in [wtype #66](https://github.com/atx/wtype/issues/66).
The in-flight focus-stop patch was therefore withdrawn before installation;
between-group focus checks remain the only production protection. Do not claim
that a long native typing action is target-bound or safe against focus changes.
The next keyboard change needs a signal-safe input helper and live verification
of key release before it can be accepted.
