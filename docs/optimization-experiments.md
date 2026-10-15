# Measured results and limitations

Every figure here comes from a specific run against a specific owned fixture, and
each section states its own scope. None of it is a general claim about speed,
success rates, other applications or billed model tokens. Raw reports are kept
outside this repository.

> **Round 5 supersedes R4 CDP numerical attribution.**
> The R4 CDP candidate ran a private prototype hash, not the shipped commit
> hash; R5 reran both comparisons against committed artifacts with frozen
> provenance. See [docs/round5.md](round5.md) and
> `docs/benchmarks/r5_cdp_aggregate.json`. R4 tables below are kept intact as
> historical data. R5 paint refused the 40 ms sleep reduction with a measured
> delayed-60 failure (see round5.md §A). R5 a11y skeleton/drill skips PNGs but
> saves little JSON intrinsically: result JSON grows +1958 bytes
> (867 → 2825 median) while whole-task median moves 1.5% only — no billed-token
> claim follows.

## Current comparison set

The browser A/B below compares the current batch route against the same route
with `act --no-after`. Both use `set_value`, which is focus-independent; an
earlier exploration used `fill` for the batch route and is not the same
configuration, so those older numbers are not comparable with the current set and
are not repeated here.

## MUSE2 assertion polling interval

Root local verification of the private run against an owned live Chromium fixture
on Hyprland 0.56.2 verified 1,440 successful tasks:
24 blocks across six delay/control workloads and two task routes, with 60
samples per variant per cell. The baseline used a 50 ms CDP assertion poll;
the candidate changed only that interval to 10 ms. Blocks ran B,A,A,B. Each
task used the same fixture and sequence; an independent HTTP POST check
verified the saved text. These were real browser measurements, not mocked
benchmark runs. Session startup, discovery and model inference are outside
these timings.

| Delay | Controls | Route | Baseline median / p95 ms | Candidate median / p95 ms | Median reduction | Result JSON bytes |
|---:|---:|---|---:|---:|---:|---:|
| 0 | 0 | task-scoped | 63.742 / 67.811 | 30.502 / 32.577 | 52.15% (33.240 ms) | 381 → 381 |
| 0 | 0 | task-after-scoped | 64.260 / 67.740 | 31.275 / 33.773 | 51.33% (32.985 ms) | 679 → 679 |
| 0 | 1000 | task-scoped | 71.509 / 74.232 | 36.227 / 38.725 | 49.34% (35.282 ms) | 381 → 381 |
| 0 | 1000 | task-after-scoped | 72.691 / 75.763 | 37.922 / 40.195 | 47.83% (34.769 ms) | 679 → 679 |

All four zero-delay cells exceed the predeclared 10% and 5 ms median-win
thresholds. Across the other eight cells (delays 50 and 250 ms), median changes
range from a 0.877% reduction to a 0.905% increase. No cell exceeded the 15%
median-regression limit; the whole-task p95 bound passed in all cells, as did
the independent result and cleanup checks. No result-byte median increased.
The harness did not request screenshots and the raw schema has no PNG byte
field, so PNG output is absent rather than directly measured. Result sizes are
JSON bytes, not billed tokens. These fixtures do not measure LLM inference,
billed tokens, session startup or discovery.

Separate false-assert profiling runs recorded candidate Node CPU use of
63.181, 72.534 and 67.158 ms at controls=0, and 69.377, 60.244 and 61.565 ms
at controls=1000. The maximum, 72.534 ms, is Node CPU in the action loop, not
Chrome CPU or whole-machine usage. These six profiling runs are separate from
the acceptance samples and show the increased polling work.

Reproduction uses the original source basis at `f5d305e` with only the CDP
poll interval changed from 50 to 10 ms. Supply a baseline CLI prepared from
that source and the candidate `scripts/cu.py`; save each report outside the
repository. Run the routes and workloads sequentially:

```sh
report_dir=$(mktemp -d)
baseline_cli=PATH_TO_BASELINE_CLI
for controls in 0 1000; do
  for delay in 0 50 250; do
    for block in B1 A1 A2 B2; do
      case "$block" in
        B1|B2) cli=$baseline_cli ;;
        A1|A2) cli=scripts/cu.py ;;
      esac
      python3 tests/browser_task_benchmark.py \
        --report "$report_dir/controls${controls}-delay${delay}-${block}.json" \
        --cli "$cli" --samples 30 --controls "$controls" --delay "$delay" \
        --modes task-scoped task-after-scoped || exit
    done
  done
done
```

The audited rows and recomputation are published in
[docs/benchmarks/muse2_assertion_poll_aggregate.json](benchmarks/muse2_assertion_poll_aggregate.json),
verifiable with `python3 scripts/check-perf-evidence.py`. Provenance: local owned
live Chromium fixture runs, reviewed measurements — not a third-party
independence claim. The poll-interval change itself is R3 work; R4 adds only
packaging and verification, no new gain. Round4 ran its own FINAL measured
isolation experiment below; the R3 poll gain stays R3 and is not re-claimed
there. The 24 blocks span 6 delay/control workloads and 2 task
routes in B,A,A,B order with 60 samples per variant per cell; these are repeats
under that order, not 1,440 distinct scenarios. No runtime or model-wide
performance claim follows from this fixture.

## Round4 FINAL (R4 FINAL): measured isolation experiment

FINAL balanced experiment, not pending and not sequential: 66 blocks,
870 measured rows plus 54 warmups (924 rows total), every row `ok` with
cleanup confirmed. Desktop: 36 blocks x 10 samples, 360 measured + 0 warmup,
owned inert GTK click fixture, rounds R1 ABBA / R2 BAAB / R3 ABBA.
CDP normal: 24 blocks x 20 samples (10 per mode), 480 measured + 48 warmup,
owned live Chromium fixture, same round order. CDP image: 6 blocks x 5
samples, 30 measured + 6 warmup, descriptive only. Rows and recomputation are
published in
[docs/benchmarks/r4_isolation_aggregate.json](benchmarks/r4_isolation_aggregate.json),
verifiable with `python3 scripts/check-perf-evidence.py`. Independent means
root local verification, not an external third party. Session startup,
discovery and model inference are outside all timings below.

Fixed thresholds (set before measurement): every normal cell needs
all 3 round gains positive, the seeded chronological paired-block CI95
(6 pairs per normal cell, 3 for image, 10000 draws, seed 0) above zero, and
candidate p95 within baseline p95 x 1.05. Root conservatively enforces
this cap on each round as well as pooled data; the initial pooled-only
acceptance of the desktop candidate was withdrawn, not rounded to pass. CDP normal cells additionally need pooled gain >= 1 ms and >= 3%.
The image cell is exploratory with no gate. The aggregate includes median
and total JSON/PNG bytes for each variant in each round; image JSON embeds
base64, so those two byte metrics overlap and must not be added.

Desktop guard cell `exp1 guard-crop-noafter-click` (candidate: skip the outer
guard when the group has no mouse modifier; fresh `execute_group` guard and
modifier pre-guard kept; sleep unchanged):

Cell reached FINAL gate: REJECT. Before median/p95 162.919 / 188.858 ms,
after 161.374 / 184.528 ms, gain 1.545 ms (0.95%), CI95 [0.181, 3.569] ms.
Per-round gains all positive (R1 +1.277, R2 +2.074, R3 +2.818 ms) but R3
round p95 regresses +5.02% (176.577 -> 185.439 ms), over the 5% cap.
JSON 335 -> 335 bytes, PNG 4192 -> 4192 bytes. Result-bytes/4 may be quoted
only as an explicitly naive heuristic; visual and billed tokens stay
UNVERIFIED. The guard optimization is NOT LANDED; the original outer guard remains.
Four behavioral regression tests are retained. No desktop engine speed win
is claimed.

Crop guidance (same baseline engine, equal after-semantics compared only):
existing crop feature, newly documented default — not a new backend
algorithm. `exp2 crop-after`: full-after 411.219 / 456.618 ms becomes
crop-after 291.779 / 317.556 ms, gain 119.439 ms (29.05%),
CI95 [115.876, 141.829] ms, gate PASS. PNG paired bytes 83332 -> 8384,
JSON 579 -> 606. `exp2 crop-noafter`: full-noafter 242.143 / 281.786 ms
becomes crop-noafter 164.010 / 192.711 ms, gain 78.133 ms (32.27%),
CI95 [74.434, 96.016] ms, gate PASS. PNG 41692 -> 4192, JSON 322 -> 335.
Per-round gains positive in all 6 rounds. Begin with a bounded crop when app
window, semantics or geometry determine a reliable one; full view is the
explicit fallback when they do not.

CDP one-slot worker transport (candidate reuses one slot only for a fresh
validated same target; standalone commands stay isolated; no snapshot cache,
no replay, terminal failures stop). All four normal cells reached FINAL
gate: PASS. PNG is absent (null, UNVERIFIED, never 0); JSON unchanged.
(R4 CDP numbers only: the candidate measured here was a private prototype
hash, not the shipped commit — R5 reruns against committed artifacts
supersede this numerical attribution. See [docs/round5.md](round5.md).)

- `cdp C0 task-scoped`: 31.296 / 33.025 ms becomes 25.809 / 31.671 ms,
  gain 5.488 ms (17.53%), CI95 [3.791, 6.541] ms. Rounds +3.982 / +5.017 / +6.806 ms.
- `cdp C0 task-after-scoped`: 31.873 / 34.552 ms becomes 26.213 / 32.454 ms,
  gain 5.660 ms (17.76%), CI95 [3.537, 6.509] ms. Rounds +5.911 / +5.071 / +5.828 ms.
- `cdp C1000 task-scoped`: 37.091 / 39.117 ms becomes 31.615 / 36.938 ms,
  gain 5.476 ms (14.76%), CI95 [4.336, 5.537] ms. Rounds +5.802 / +5.710 / +4.007 ms.
- `cdp C1000 task-after-scoped`: 38.702 / 41.236 ms becomes 33.194 / 38.709 ms,
  gain 5.508 ms (14.23%), CI95 [4.416, 5.819] ms. Rounds +5.625 / +5.940 / +4.459 ms.

CDP image cell (exploratory, no gate, no speed claim): 364.949 / 382.627 ms
vs 371.489 / 384.107 ms, gain -6.540 ms (-1.79%),
CI95 [-7.865, 12.824] ms crossing zero. Round gains -7.451 / +12.824 / -7.865 ms.
Actual per-row PNG bytes with dimensions are published (before+after pairs,
e.g. medians 31963 vs 31950 bytes); image result JSON embeds base64 PNG data,
so JSON and PNG byte metrics overlap — never add them and never divide image
JSON by 4 to claim real model tokens. CPU per task UNVERIFIED throughout.

Rejected and NOT LANDED: sleep-80ms removal/reduction (R5 measured a real
40 ms delayed-60 failure — after stays red while the late reference turns
green — so the existing sleep is retained; see [docs/round5.md](round5.md)
§A) and query caching
across safety boundaries (fresh guards retained). Non-perf CLI/a11y/ABI
diagnostic changes carry correctness-test evidence only; their timings are
UNVERIFIED, so no speed is inferred from tests. No universal application
gain and no billed-token claim follow from any cell above.

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
after-snapshot is whole page again unless `--after-scope` is explicit, and every action, focus and cancellation
guard is unchanged. It is not an input, security or privacy boundary.

Measured on the owned Chromium fixture, 3 blocks x 30 pairs = 90 samples per
route at each controls value, AB/BA alternated, warm worker with the pre-R4 fresh CDP
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

## Scoped successful after-snapshots

`browser act --after-scope SELECTOR` returns the next snapshot from one panel
after a successful action. Unlike `--no-after`, it supplies new refs for the next
step. The option is explicit for each act; failures keep a whole-page diagnostic.
If the requested root is unavailable after success, `after_unavailable` requires
a fresh observe before more input. It does not restrict where actions can target.

Source-tree Chromium fixture, one block of 30 AB/BA pairs at each page size.
Both routes begin with the same scoped observe, then use the same
`set_value`/Save/result-assert sequence; the candidate scopes only the successful
after-snapshot. The timed span covers observe, ref selection, act and independent
server POST verification, with a warm worker and, in this pre-R4 experiment, a fresh CDP connection per
request. Setup and model time are excluded. Bytes are re-encoded observe plus
act JSON, not billed tokens. All 120 measured tasks and four warm-ups matched
the independent app state; cleanup succeeded.

| Extra controls | Full after median / p95 ms | Scoped after median / p95 ms | Median result bytes |
|---|---:|---:|---:|
| 0 | 64.732 / 67.385 | 65.699 / 67.758 | 663 -> 679 |
| 1000 | 75.146 / 77.883 | 72.406 / 74.981 | 7363 -> 679 |

The large fixture returns **90.78% fewer bytes**. Its 2.740 ms / 3.65% median
time reduction does not meet the existing speed-win threshold (at least 10% and
5 ms); the small page is 0.967 ms slower and adds 16 bytes. Use the option when
irrelevant page controls dominate the result. These runs do not establish lower
LLM token billing or lower end-to-end model task time.

```sh
report_dir=$(mktemp -d)
python3 tests/browser_task_benchmark.py --report "$report_dir/after.json" \
  --modes task-after-full task-after-scoped --samples 30 --controls 1000
```

## Desktop final-capture comparison

The existing desktop `act --no-after` route skips the successful final screenshot.
It retains the fresh pre-input capture, focus/geometry/cancellation checks and
execution-error diagnostics. Use it when an independent application result check
confirms the outcome and no next screenshot is needed; event-level `ok` is not
that evidence.

Measured with the **installed CLI** against an owned inert GTK click fixture:
four sequential A/B/B/A blocks, 30 samples each, A with the default final capture
and B with `--no-after`. Every reset had a nonce and every task independently
verified exactly one click. All 120 tasks and cleanup passed. First samples were
retained. No keyboard typing, account activity, network or plugin activation.

`whole_task_ms` spans fresh observe, Python action construction, the harness
checkpoint write/fsync, act and independent app verification. Session/setup and
model time are excluded. Historical `total_ms` still measures act plus verifier.
Bytes are re-encoded observe plus act JSON; PNG contents and transport framing
are excluded, and no model-token billing was measured.

| Route | Samples | Whole-task median / p95 ms | Median result bytes |
|---|---:|---:|---:|
| Default after | 60 | 403.891 / 424.519 | 579 |
| No after | 60 | 234.762 / 249.736 | 322 |

The fixture's median time drops **169.129 ms / 41.88%**, meeting the existing
10% + 5 ms speed-win criterion with a lower p95. Per-block whole-task median/p95:
A1 402.875/413.327, B1 234.164/247.589, B2 235.001/250.521, A2 410.050/426.543 ms.
Output falls 44.39%, which **does not** meet the separate 50% output gate. This
is a tool-driven fixture task, not an end-to-end LLM task or a guarantee for other
applications or image sizes.

```sh
report_dir=$(mktemp -d)
python3 tests/optimization_live.py --cli PATH_TO_INSTALLED_CU \
  --report "$report_dir/full.json" --samples 30 --cases click
python3 tests/optimization_live.py --cli PATH_TO_INSTALLED_CU \
  --report "$report_dir/skip.json" --samples 30 --cases click --no-after
```

For the four-block comparison, repeat in full/skip/skip/full order with a fresh
report path for each block. Summarize `whole_task_ms` and `result_bytes` from the
rows; the existing console summary reports historical act-plus-verifier time.

## Cropped desktop observation, once the area is known

`observe --crop X Y W H` narrows the captured region. Begin with a bounded crop
when the app window, semantics or geometry determine one: the crop must contain
the target **and** the context you need to confirm you aimed at it. Inspect the
returned cropped image before choosing input coordinates; the crop changes the
image and its scale, not the window's logic. Expand or re-observe when the
target or its context is absent. A full view is the explicit fallback only when
no reliable crop can be determined. Never crop past an unseen menu or popup
change — an unknown menu or popup is exactly where a blind crop hides the thing
you needed — and never guess action coordinates. After any geometry, focus
or screen change, observe again rather than reusing coordinates. No runtime CLI
default or API changes: this is instruction guidance only.

Measured with the **installed CLI** against the same owned inert GTK click
fixture: four sequential A/B/B/A blocks, 30 samples each, both with `act --no-after`, A a
full-window observe and B one padded 8 px crop around the fixture button. Every
reset had a nonce, every task independently verified exactly one click, and all
120 tasks and cleanup passed. First samples were retained. No keyboard typing,
account activity, network or plugin activation. The runtime hash was identical on
both routes; no runtime code changed.

`whole_task_ms` again spans fresh observe, action construction, the checkpoint
write/fsync, act and independent verification, so the crop derivation is inside
the measured span. Session/setup and model time are excluded.
The fixture supplies target geometry; discovering the area and inspecting an initial
full view are outside this span. This measures a known-area task, not a new task
whose target must first be discovered.

| Metric | Default | Crop | Change |
|---|---:|---:|---:|
| `total_ms` median | 122.053 | 86.537 | −29.1% |
| `response_ms` median | 121.960 | 86.476 | −29.1% |
| `execution_ms` median | 29.000 | 29.000 | unchanged |
| `whole_task_ms` median | 241.788 | 155.062 | **−86.726 ms / 35.869%** |
| `whole_task_ms` p95 | 279.196 | 164.236 | −41.2% |
| PNG bytes median | 117,138.5 | 5,633.0 | −95.191% |
| `result_bytes` | 322 | 335 | **+4.037%** |

Per-block whole-task median/p95 in ms: A1 239.432/259.959, B1 155.242/164.703,
B2 154.953/163.948, A2 249.542/286.066. Disclosures: A1 ran the original HEAD
harness, A2 the new harness at the same default, which adds the PNG statistics
*outside* the timer; the PNG baseline comes from A2's 30 samples only, while every
other aggregate is 60 samples per route. An extra A0 baseline run was retained
separately and is not part of the declared ABBA. The checkpoint write/fsync is
inside the measured span. Both gates — the 10% + 5 ms speed win and a lower p95 —
passed.

Read this honestly: PNG bytes are **not** billed model tokens, and the result JSON
grows 4.037% because the explicit crop metadata is carried in the response. The 35.869% is the fixture's whole-task wall clock, not a claim about
total LLM task time, other applications or other image sizes. Docs-only impact on
agent task tokens is UNVERIFIED until controlled measurement: a JSON-bytes/4
heuristic may be quoted only when clearly labelled as a heuristic, and any PNG
visual-token saving is UNVERIFIED.

The sequential full-vs-crop baseline variants below were superseded by the
R4 FINAL balanced experiment above; no causal gain is published from them.

```sh
report_dir=$(mktemp -d)
python3 tests/optimization_live.py --cli PATH_TO_INSTALLED_CU \
  --report "$report_dir/full.json" --samples 30 --cases click --no-after
python3 tests/optimization_live.py --cli PATH_TO_INSTALLED_CU \
  --report "$report_dir/crop.json" --samples 30 --cases click --no-after --crop-button
```

`--crop-button` is a harness option that only exists for this comparison; it
derives the crop from the fixture's own layout. A real agent chooses its own
rectangle. For the four-block comparison, repeat in full/crop/crop/full order
with a fresh report path for each block.

## Compact window discovery

`windows --class CLASS --no-titles` filters a single client-list read by exact
class and omits the title field. It returns every matching window; it does not
focus or select one. The default output is unchanged.

An offline fixture fed 100 synthetic clients through the real CLI formatter,
with one matching class. The JSON output was 12,178 bytes by default, 9,188 with
`--no-titles`, and 95 with both flags. Each route made exactly one mocked clients
call. These figures describe selected output size, not compositor latency,
real-world window counts or billed tokens. A separate real, read-only compositor
smoke confirmed exact filtering and title-key omission; it performed no input.

## Skill entrypoint size

The main `skill/SKILL.md` was reduced from 8,267 to 5,845 UTF-8 bytes and from
1,113 to 828 words (about 29% fewer bytes). Detailed schemas stay in the selected
backend reference, so routine use need not load every backend. These are file
counts from `wc -w -c`, not measured model tokens, billing or task duration.

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

## Closed CDP transport response

An ABBA mock-protocol run (four blocks, three samples per block, including each
block's first sample) compared the old installed adapter with the reviewed
source adapter. Medians changed: total 10,007.440→1.342 ms, response
10,007.396→1.331 ms, action execution 5,001→0 ms, whole task
10,007.440→1.342 ms, and result JSON 222→210 bytes; whole-task p95 changed
10,028.243→19.605 ms. The fixture uses Node's real clock/timers and includes
VM fixture setup. It exercises a closed WebSocket during an assert-only action:
this is closed-transport failure latency, not normal successful browser work.
The response clock spans fixture/VM setup, observe and act response; execution is the
act result's own timer, and whole/total include the protocol input/state check.
The independent check covers only the simulated peer, not DOM or app state. It
uses a simulated WebSocket/CDP peer, not Chrome, and makes no LLM or billed
token claim. The WebSocket standard describes `send()`'s state behavior at
[WHATWG WebSockets §3.1](https://websockets.spec.whatwg.org/#dom-websocket-send).

The 5 s timeout for an open but unresponsive socket remains; there is no retry,
and input ordering is unchanged. Reproduce four ABBA blocks by running three
samples for each command, in this order; the baseline path is the archived old
adapter, while the candidate path is the reviewed source:

```sh
node tests/cdp_worker.mjs --close-bench PATH_TO_BASELINE_CDP
node tests/cdp_worker.mjs --close-bench scripts/cdp.mjs
node tests/cdp_worker.mjs --close-bench scripts/cdp.mjs
node tests/cdp_worker.mjs --close-bench PATH_TO_BASELINE_CDP
```

Each invocation emits three samples and uses the native 5 s timeout unchanged.

A separate paired headless Chromium smoke closed its owned tab by timer during a
1,000 ms wait plus assert; both routes completed one action and marked the
after-state unavailable. Total/whole time changed 11,073.930→1,065.077 ms and
result JSON 233→229 bytes. This single pair validates real close handling, not
statistical throughput or LLM performance; it is separate from mock results.

## Historical evidence (MUSE1, not Round4 validation)

Earlier runs against owned live fixtures recorded 180 measured task executions —
120 Chromium plus 30 GTK full-window and 30 GTK crop — with 4 warmups, all
successful with cleanup confirmed. Separately, 11 installed unit-test module
executions totalled 98 run / 98 pass / 0 failed, each with exit code 0. These
are execution counts, not distinct test IDs; the 180 are live-fixture runs
(real Chromium/GTK fixtures, not mocks) while the 98 are unit mocks/offline
tests. The source basis predates Round4, so this is historical evidence, not
validation of the current HEAD. Rows and per-module counts are published in
[docs/benchmarks/muse1_historical_aggregate.json](benchmarks/muse1_historical_aggregate.json),
verifiable with `python3 scripts/check-perf-evidence.py`; no private-only
citation is needed.

## Already-deliberate behaviors (no code change)

The following were verified as already implemented at the cited source; they
are documented here without reverting or changing code:

- **L2 address case**: window-address comparison is case-insensitive
  (`scripts/cu.py` `same_window_address`, used by all callers).
- **L3 read-only query allowlist**: Hyprland queries pass a fixed-name
  allowlist on both the socket and CLI paths; refusal carries bounded query
  detail, not a fixed string.
- **L4 browser `start`/`tabs --image` rejection**: refused before environment
  or dispatch.
- **L5 missing controller fails closed**: an own-UID fcitx5 daemon without the
  helper refuses rather than proceeding.

## Related

- [liquid-glass.md](liquid-glass.md) — optional compositor backend
- [testing.md](testing.md) — running the checks
