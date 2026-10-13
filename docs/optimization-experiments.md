# Measured results and limitations

Every figure here comes from a specific run against a specific owned fixture, and
each section states its own scope. None of it is a general claim about speed,
success rates, other applications or billed model tokens. Raw reports are kept
outside this repository.

## Current comparison set

The browser A/B below compares the current batch route against the same route
with `act --no-after`. Both use `set_value`, which is focus-independent; an
earlier exploration used `fill` for the batch route and is not the same
configuration, so those older numbers are not comparable with the current set and
are not repeated here.

## Browser `act --no-after` A/B on the source fixture

Measured against an inert real Chromium fixture driven from the source tree.
`set_value`, `click` on Save, then a final `assert` on the status text. Both
routes send one request with the same action sequence and equal-length Unicode
values; the candidate adds the flag. The payload carries a per-run nonce plus the sample index and
mode, so a stale field left by the previous route or sample can never satisfy the
assertion. `max_elements` stayed at 8. `--controls` adds inert inputs so the
after-snapshot pays real DOM enumeration cost; `max_elements` unchanged.

3 blocks x 30 pairs = 90 samples per route per controls value, AB/BA alternated
by pair within each block; controls order was flipped in the middle block. 360 measured tasks plus 12
unmeasured warm-ups, all exact, with independent server POST verification on
every task and clean cleanup. The worker is warm, but every request gets a fresh
CDP connection. The timed span is the worker task request **plus** the
independent app verification; startup, setup and the initial observe sit outside
the timer. Result bytes are
`len(json.dumps(result, ensure_ascii=False).encode(UTF-8))`. No live LLM or API
billing was measured — these are bytes, not tokens.

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

Startup smoke failures that happened before the fixture-readiness fix are
excluded from these figures; readiness is now established before any input is
sent.

Output reduction is accepted as a separate opt-in criterion: at controls 0 the
median result drops 344 -> 71 bytes and at controls 1000 853 -> 71 bytes, both
well past the 50% gate, with no speed win claimed at controls 0. These are source
measurements; they are not a claim about every website or page size.

## Reproduce

Run from the repository root, writing reports outside the public repository and
to a fresh path per run:

```sh
report_dir=$(mktemp -d)
python3 tests/browser_task_benchmark.py --report "$report_dir/small.json" \
  --modes batch batch-no-after --samples 30 --controls 0
python3 tests/browser_task_benchmark.py --report "$report_dir/large.json" \
  --modes batch batch-no-after --samples 30 --controls 1000
```

The benchmark owns its own session, so run it outside an existing one. To drive
an installed CLI instead of the source tree, pass `--cli PATH_TO_INSTALLED_CU`.

The scoped route is measured by the same harness with the paired task modes:

```sh
python3 tests/browser_task_benchmark.py --report "$report_dir/scope.json" \
  --modes task-full task-scoped --samples 30 --controls 1000
```

`tests/control_benchmark.py` is a separate read-only comparison helper for
capture and worker latency; `--target` points it at an inert fixture tab and it
performs no input.

## Scoped observation

`browser observe --scope SELECTOR` filters the observe enumeration to the
interactive descendants of exactly one top-document root, plus that root when it
is itself interactive. The scope is not retained between reads; an `act`
after-snapshot is whole page again, and every action, focus and cancellation
guard is unchanged. It is not an input, security or privacy boundary.

Measured on the owned Chromium fixture, 3 blocks x 30 pairs = 90 samples per
route at each controls value, AB/BA alternated, warm worker with a fresh CDP
connection per request. Both routes use `max_elements: 80`, exactly two requests
(one observe, one act with `no_after`), equal-length, unique Unicode payloads, refs resolved
from the returned observation, and the timer covers the observe, ref selection,
the act, the final assert and the independent POST verification. Setup and model
time are excluded. Bytes are re-encoded JSON for observe plus act — not
transport bytes and not billed tokens. 360 measured tasks plus 12 warm-ups, no
correctness failure, cleanup clean.

| Controls | Full median / p95 ms | Scoped median / p95 ms | Median cut | Bytes |
|---|---:|---:|---:|---:|
| 0 | 65.045 / 67.030 | 64.292 / 66.918 | 1.160% (0.753 ms) | 365 -> 381, **4.38% more** |
| 1000 | 73.153 / 76.146 | 70.643 / 74.650 | 3.430% (2.510 ms) | 7065 -> 381, **94.61% fewer** |

Neither size meets the predeclared speed-win rule (median reduction >=10% and
>=5 ms with bounded p95); both pass the no-regression gate. Large-page p95
improves in all three blocks (75.415 -> 74.571, 76.304 -> 74.650,
76.146 -> 74.655 ms). Small-page medians vary; block 2 worsens from 63.174
to 63.966 ms. Its extra `scoped: true` field also adds 16 bytes.

The opt-in release passes the large-page output gate (>=50% fewer bytes).
Use it to reduce irrelevant observation context; these measurements do not
establish billed-token savings, model-time savings or a speed win. Default
whole-page observation is unchanged.

## Installed keyboard diagnostics

Follow-up runs used the installed CLI/session and installed input code, stock
`wtype` 0.4-2, temporary Chromium profiles and synthetic fixture values. No
production profile or compositor plugin was changed.

The desktop string `Tạo báo cáo nháp — 3 mục` produced
`Tạo báo cáo nháp — 3 c` at both delay settings tested (one trial each).
Application events recorded key `ụ`, physical code `Backspace`, followed by a
trusted `deleteContentBackward` input event. ASCII `abcdefghijklmnop`, `mục`,
`Tiếng Việt` and a leading-dash version of the full sentence matched in one trial
each; `abcdefghijklmục` also failed. These diagnostic trials demonstrate a
keymap-dependent correctness bug, not a Unicode-wide failure rate or an IME fix.
This matches the mechanism described in
[wtype's control-key collision proposal](https://github.com/atx/wtype/pull/77).
That proposal was not installed or validated here. Slower typing is not a fix.

A separate fault injection used two inert GTK windows on an unused workspace.
During a 481-character stock typing action, focus was deliberately moved to the
second fixture. The target received 44 characters and the other fixture 436; the
action eventually returned a failure. This single trial establishes that
between-group focus guards do not bind ongoing keyboard input to its target. It
does not establish the missing character's cause, a leakage-rate distribution, or
any repair.

For the practical browser route, an installed `fill`/`click`/result-assert smoke
ran three measured warm tasks with exact Vietnamese-plus-emoji fixture values.
All passed the independent application callback check; median 72.904 ms,
nearest-rank p95 76.919 ms. This is smoke, not another speed comparison, and does
not prove desktop keyboard safety or identical behaviour in other applications.

A separate copy of the same harness used the exact failing demo sentence instead
of its usual payload. All three measured warm DOM tasks matched the full sentence
via the independent callback, with cleanup successful. These are output checks,
not evidence that the desktop keyboard bug has been repaired.

## Browser field assignment with routing faults

`set_value` is a browser-only alternative for ordinary text inputs and textareas.
It resolves one snapshot reference or one unique selector, does not click or
change focus, uses the element's native value setter, dispatches synthetic
`input` and `change` events, then checks that the same connected element still
contains the requested value. These events are not trusted keyboard input; pages
that require trusted events need a different route. Always verify the app's own
result with a following `assert` or another independent check. A matching DOM
value alone does not prove an app accepted it.

`tests/browser_field_live.py` ran against an isolated Chromium profile and a
loopback-only fixture using the source tree. The fixture reproduced both a
wrong-field write and a false `fill` success after focus changed; the setter left
the decoy untouched and its Save/result assertion matched the requested
Vietnamese text. The run also verified that its input event was synthetic. This
was one live correctness run per case, not a speed benchmark or a claim about
arbitrary web apps. The test owns its disposable profile and restores focus and
workspace when possible.

Keyboard input still has an unresolved focus race: during investigation,
terminating stock `wtype` while Ctrl was held did not let the owned GTK fixture
confirm that Ctrl had been released. Upstream `wtype` does not install a signal
cleanup handler, and the issue is reported in
[wtype #66](https://github.com/atx/wtype/issues/66). Do not claim that a long
native typing action is target-bound or safe against focus changes.

## Related

- [liquid-glass.md](liquid-glass.md) — optional compositor backend
- [testing.md](testing.md) — running the checks