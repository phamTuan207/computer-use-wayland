# Round 5 evidence

Status: A/B rebutted with concrete correctness evidence; C/D/G/H done within
the measured and verification scopes below; E2–E6 done, E1 and L7/R3-2
accepted with reasons; F blocked only on the human decision.

Portable sanitized aggregates (recomputed from completed raw runs, not prior prose):

- `docs/benchmarks/r5_cdp_aggregate.json` — C: 2 comparisons x 24 blocks, 960 measured + 96 warmups.
- `docs/benchmarks/r5_a11y_aggregate.json` — H: 6 blocks x 5, 30 measured, 0 warmups.
- `docs/benchmarks/r5_paint_aggregate.json` — A: 6 blocks, 41 measured of planned 144.

Raw files stay private in `R5/`; SHA-256 hashes embedded. Methods use exact
`scripts/check-perf-evidence.py` `median_p95` / `paired_ci95` (seed 0, 10000).
CPU unmeasured → UNVERIFIED everywhere. CDP PNG absent → UNVERIFIED, never 0.

## A — retain 80 ms (rebutted by measured counterexample)

41 measured rows, planned 144. No later rounds. 5 successful 8-sample blocks
(40 rows) + first failed 40 ms delay-60 row (1 row). Evidence:
`r5_paint_aggregate.json`, raw `R5/paint-live-reduction/`, sources
`R5/paint-prepared/manifest.json`, prior `R5/paint-cache/old-evidence-audit.json`.

- Delay 60 + sleep 80 ms: 8/8 green (correctness pass only; no performance
  success claim from this pilot alone).
- Delay 60 + sleep 40 ms: 0/1 gate failure. After RGB red `[251,0,0]` vs late
  reference green `[0,251,0]`; `click_count` 1, `core_tool_completed` 1.
  No performance claim from the failed candidate.
- Sleep 80 retained. Never claim all 144 ran.
- Prior zero-30 counterexample is real (`old-evidence-audit.json` reopens
  retained PNGs); old independent probe PNG is missing (numeric RGB survives),
  stated explicitly.

Whole-task time includes observe + act + independent result verification; the late
validation probe and evidence copy are outside that timer. PNG and JSON below
count only the timed core; separate probe bytes remain in the aggregate. The
failed row is a correctness counterexample, not a speed improvement.

| Paint delay / sleep ms | n / correct | Whole median / P95 ms | Core PNG median bytes | Core reply JSON median bytes |
|---|---:|---:|---:|---:|
| 0 / 80 | 8 / 8 | 427.373 / 438.345 | 83871.5 | 590 |
| 0 / 40 | 8 / 8 | 383.205 / 392.011 | 83820 | 589 |
| 30 / 80 | 8 / 8 | 423.038 / 434.579 | 83847.5 | 590 |
| 30 / 40 | 8 / 8 | 383.348 / 387.544 | 83826.5 | 589 |
| 60 / 80 | 8 / 8 | 425.056 / 433.539 | 83854 | 590 |
| 60 / 40 | 1 / 0 | 396.998 / 396.998 | 83742 | 589 |

The failed 40 ms row completed one click, yet its returned after-image remained
red. Public unchanged synthetic-fixture PNGs: [before](benchmarks/r5_paint_images/before.png),
[returned after](benchmarks/r5_paint_images/after.png),
[late reference](benchmarks/r5_paint_images/reference.png). Pixel `(41,223)`
is red/red/green; hashes and byte sizes are embedded in the paint aggregate.
The retained late reference is green; all three PNG hashes/pixels were
reopened independently (`R5/A-independent-final.json`).

`--settle-ms` currently governs observe-only pixel stability (120 ms unchanged),
not causal completion of the preceding action. Stable old pixels can pass a
stability test before delayed paint. Wiring it into act would change that
contract and still need a presentation fence; no API/plugin change was made.
80 ms is retained as the current heuristic, not a guarantee for arbitrary delays.
`act --no-after` already avoids the sleep when an independent app-result check
suffices.

## B — per-act caching + invalidate-on-failure (rebutted for this design)

Unsafe; see `R5/paint-cache/report.md`. Guard reads can go stale across
input/wait/IME boundaries; a cached guard cannot see the change that should
invalidate it. The production-guard mock counterexample was executed independently:
a monitor scale change from 1 to 2 after preparatory motion is refused by a fresh
guard (0 button commands), while cached monitors permit button down/up. This is a
correctness counterexample, not a live compositor timing measurement. Raw proof:
`R5/B-independent-final/{stdout.json,stderr.log,exit.json}`. Caching only within
one guard adds no saving because each query is already issued once; event-based
caching needs an authoritative ordered state/fence that is not available here.

## C — CDP scoped-vs-after (measured)

Rerun numbers, not transferred. Prototype `39d79e…` differs from shipped
`ed98b12` only in 2 length-error wordings ("characters" → "UTF-16 code units",
`R5/C-provenance.json`, `R5/C-prototype-vs-shipped.patch`). All R5 numbers are
fresh runs of committed artifacts pinned in `R5/C-frozen-trees.json`
(A blocks = `before`, B blocks = comparison artifact).

Pooled (60+60 per cell), whole-task ms. All 8 cells gate PASS under the fixed
gate (≥1 ms AND ≥3%, every round gain > 0, paired-block CI lower > 0, pooled
and per-round P95 regression ≤ 5%):

| comparison | controls | mode | A med / p95 | B med / p95 | gain ms (%) | CI95 | gate |
|---|---|---|---|---|---|---|---|
| shipped-r4 | 0 | task-scoped | 31.040 / 33.088 | 26.272 / 31.782 | 4.768 (15.36%) | [3.026, 5.543] | pass |
| shipped-r4 | 0 | task-after-scoped | 30.654 / 34.660 | 26.213 / 32.010 | 4.441 (14.49%) | [2.490, 5.336] | pass |
| shipped-r4 | 1000 | task-scoped | 37.327 / 39.511 | 31.498 / 35.943 | 5.829 (15.62%) | [5.444, 6.687] | pass |
| shipped-r4 | 1000 | task-after-scoped | 37.693 / 40.749 | 32.938 / 36.805 | 4.755 (12.61%) | [3.131, 5.499] | pass |
| final-r5 | 0 | task-scoped | 31.061 / 32.903 | 26.260 / 31.716 | 4.801 (15.46%) | [3.272, 5.603] | pass |
| final-r5 | 0 | task-after-scoped | 30.817 / 34.523 | 25.938 / 31.512 | 4.879 (15.83%) | [3.716, 5.349] | pass |
| final-r5 | 1000 | task-scoped | 36.397 / 39.411 | 31.751 / 37.104 | 4.647 (12.77%) | [3.667, 5.775] | pass |
| final-r5 | 1000 | task-after-scoped | 37.983 / 41.844 | 33.639 / 37.615 | 4.344 (11.44%) | [3.905, 4.963] | pass |

Each cell has unchanged JSON medians: 381 bytes for scoped, 679 for after-scoped;
no PNG was requested. CPU/task and billed model-token effects are UNVERIFIED.
`final-r5` names the committed CDP revision `c65d13b`, whose `cdp.mjs` remains
byte-identical in the final tree. Its full runtime (including pre-skeleton CLI)
is pinned in the aggregate; these timings are not silently attributed to every
later CLI revision. H has its own committed runtime pin.

The checker now verifies all nine source blobs against local Git, exact block
runtime/source equality, 960 measured +96 warmup rows, per-round JSON bytes,
medians/P95, seeded block CI and gates. Explicit checks remain active under
`python3 -O`; corruption tests cover valid-looking false hashes and commits.

## D — CDP worker portability (done, machine-scoped)

Local Node v26.7.0 baseline green proof: `R5/cdp/before.json` (+ stdout/stderr)
and `R5/cdp/vm-delete-proof.json`. Reviewer environment unverified; no claim
the reviewer's older/different Node was green. Reload-delete now runs inside
the vm context, removing the host/context delete dependency. Full diff/after-exits
in `R5/cdp/`. R4 “no blocker” came from genuine local green logs
(`R4/final-root-checks-accepted/`); the reviewer’s red run exposed a portability
gap in that claim. A fresh run of exact starting HEAD `53b77ee` passed locally;
it does not retroactively prove every historical pushed-tree state. The exact
reviewer-environment cause remains UNVERIFIED, rather than assumed to be Node.
The final pushed-tree verification contract is now explicit in §G.

## E — reviewer points

- E1: bounded 5 s accepted, no replay. Ping RTT does not close the race
  (disconnect can follow the reply); no second liveness mechanism added.
- E2: tabs retains a healthy transport; next observe/act still re-lists and
  matches exact target + loopback URL + key.
- E3: checker bare asserts → explicit `require()` (separate worker;
  protected `tests/session_quiet_live.py` unchanged).
- E4: wording fixed — failed transports cannot be reused.
- E5: the old fresh-CDP-per-request description now explicitly says pre-R4
  in `optimization-experiments.md`.
- E6: crop guidance now says “identify a reliable crop” in `skill/SKILL.md`.
- L7/R3-2: deliberate cleanup defenses preserved, see
  `R5/paint-cache/report.md` (`restore_needed`, `ProcessLookupError`,
  `primary is not restore_error`). The flag distinguishes interruption before
  deactivation from a partial deactivation requiring restore; `ProcessLookupError`
  handles a process disappearing, distinct from a missing executable. The exception
  identity check is a cheap defensive formatting guard, not proven dead here.

## F — scope

**Blocked only on the human decision:** N4 optional `ime_restore_failed` result
flag and H5 build-glass dirty-tree policy. No other known blocker remains for
those proposals. Neither was implemented. H2, plugin build/load paths, ABI pins
and Vietnamese IME behavior are unchanged. The new a11y entry points are the
explicitly authorized H scope.

## G — verification contract

After the final push, root runs the full unittest suite, all five Node suites,
and the evidence checker with normal and optimized Python on that exact pushed
HEAD. The authoritative machine-local record is `R5/pushed-verification/`: it
records the actual remote HEAD, environment, commands, exits, skip reasons and
before/after tracked-file hashes. Its `DONE.json` exists only if every check
passes. Builder reports alone do not establish this result.

## H — a11y skeleton/drill (honest outcome)

Real GTK3 owned fixture only. 30 measured rows (3 rounds x 2 routes x 5), no
warmups. Every row `ok`, `pid_ok`, `clicks` 1, cleanup
`{children_reaped, focus_preserved}` true. Screenshot route: `png_count` 2 per
row, `drill_calls` 0. Semantic route: skeleton (5 elements, truncated) +
bounded drill + act + redrill with same snapshot (`drill_calls` 2,
`redrill` true, `png_count` 0). Semantic redrill can worsen latency — reported
per-row, not hidden (e.g. R1 screenshot med 383.85 ms vs semantic med
383.84 ms on this fixture; routes compared by medians/p95 in the aggregate,
not by a single row). A11y tree already bounded (≤80 elements), so little
intrinsic JSON saving; benefit is PNG skip. No model-token-percentage
marketing. First failed attempt `R5/H-live-attempt01/R1-semantic.json`
(selector `pushbutton` vs actual `button`, 1 failed row, no input on failure)
is preserved as FAILED in the aggregate, not silently excluded.

Measured pooled outcome (15 tasks per route):

| Route | Whole median / P95 ms | JSON wire median bytes | PNG median bytes | Captures/task |
|---|---:|---:|---:|---:|
| screenshot | 384.789 / 420.205 | 867 | 60261 | 2 |
| semantic | 379.016 / 393.036 | 2825 | 0 | 0 |

The semantic route skipped 30 captures on 15 tasks, saved a median 60,261 PNG
bytes/task, added 1,958 JSON wire bytes/task, and reduced median whole-task time
by just 5.773 ms (1.50%). This is a small owned GTK3 form, not evidence that every
app or a model-driven task is faster. A11y JSON was already bounded to ≤80
elements: the benefit is indirect PNG skipping, not a large intrinsic JSON
reduction. Billed tokens and general-app effects remain UNVERIFIED. The advertised
percentage token-reduction claim is not used.

## Fan-out and accountability (who did what)

This followup runs in the SAME session as the publication work
(`ses_ec0427e26ffeKfbqNaKCpUZ0pq`, batch `R5-fixed-publication-session`;
original publication batch `R5-post-live-parallel`). No new or forked session.
All benchmark processes have ended; no GUI or timing work remains.

### Native precision agents (model inherited, exact ID UNVERIFIED)

No native agent exact model is available: each was requested inherited with no
override, actual UNVERIFIED. Do not invent model IDs.

- `/root/r5_a11y` — bounded skeleton + drill traversal in `scripts/a11y.py`
  plus offline tests. Report: `R5/a11y/report.md` (27 run / 27 pass: 19
  existing + 8 skeleton). Followups: `R5/a11y-independent-review.md`,
  `R5/a11y-final-review.md`, `R5/H-independent-final.json`.
- `/root/r5_cdp` — D portability, E1/E2/E4 in `scripts/cdp.mjs` +
  `tests/cdp_worker.mjs`. Report: `R5/cdp/report.md` (5/5 Node suites exit 0
  locally on Node v26.7.0; reviewer-environment failure not reproduced here).
  Followups: independent a11y source review `R5/a11y-independent-review.md`;
  checker provenance implementation/testing `R5/checker-provenance/report.md`.
- `/root/r5_paint_cache` — A/B/E evidence review, old zero-sleep audit,
  L7/R3-2 defenses. Report: `R5/paint-cache/report.md` (+
  `old-evidence-audit.json`; executable counterexample subsequently passed in
  `R5/B-independent-final/`).
  Followups: `R5/A-harness-review.md`, `R5/A-independent-final-report.md`,
  `R5/A-publication-review.md` and the executed B counterexample.
  H preparation repair belongs to `/root/r5_a11y`: `R5/H-harness-review.md`
  (real GTK geometry, actual re-drill/PID/freeze contracts),
  `R5/H-harness-contracts.log`, `R5/H-ready-plan.json`.
  OpenCode `live-prep/report.md` A27-block/216-task + contract38 claims are
  superseded by these precision reports where noted.

### OpenCode invocations (requested = actual, medium, verified read-only)

Requested `opencode/muse-spark-1.3-contributor-free#medium` on all sessions;
actual uniform per session: `id=muse-spark-1.3-contributor-free`,
`providerID=opencode`, `variant=medium` (read-only DB model metadata; no reasoning
or credentials read). Each invocation folder preserves `prompt.txt`,
`invocation.json`, `opencode.stdout.jsonl`, `opencode.stderr`, and
`opencode-exit.json` in addition to its report:

- Checker (E3 `require()` repair): prompt `R5/checker/prompt.txt`, batch
  `1: parallel native precision workers`. Outcome: valid artifacts exit 0
  normal and `-O`; corrupt artifacts fail both modes. Report
  `R5/checker/report.md`; raw `opencode.stdout.jsonl`, exit rc 0.
- Live-prep (C/A/H drivers, mock contracts, prep only — no live): prompt
  `R5/live-prep/prompt.txt`, batch
  `1: parallel checker and native precision; prep only`. Report
  `R5/live-prep/report.md` + `DONE`.
- Live-worker (exclusive GUI execution): prompt `R5/live-worker/prompt.txt`,
  batch `2: exclusive GUI; all other CPU workers stopped`. Wrapper exit rc 0
  covers the harness driver only — NOT task outcomes. Detached actuals:
  C-shipped-r4 rc 0, C-final-r5 rc 0, H-attempt01 rc 1 (stopped per rule:
  R1-screenshot 5/5 ok, R1-semantic FAILED — expected role `push button`
  vs machine snapshot `button`, no input on failure), A never started
  (correct per stop rule). Report `R5/live-worker/report.md` +
  `summary.json` + `DONE.json`; per-command `*.result.json` + stdout/stderr.
- Root followup (not OpenCode): H-attempt02 rc 0 (30 rows), A-reduction rc 1
  (41 measured rows, stopped immediately). Results in `R5/live-followup/`.
- Publication + this followup: prompt `R5/publication/prompt.txt`, same
  session throughout; followup full prompt `R5/publication-followup01/prompt.txt`
  (handoff original `/tmp/r5-opencode-handoff.md`). Publication and fanout-audit
  ran concurrently in batch `R5-post-live-parallel`; the fixed-session followup
  ran sequentially in `R5-fixed-publication-session`. Reports `R5/publication/report.md`,
  `R5/publication/schema.json`, `R5/publication-followup01/` (+
  `aggregate-ready` marker for the native checker).
- Fanout-audit (accountability only, no public files touched): prompt
  `R5/fanout-audit/prompt.txt`. Report `R5/fanout-audit/fanout-report.md` +
  `manifest.json` + `commands.log` + `DONE`.

Qualitative split only (no token counts invented): OpenCode checker repaired
the checker + CLI tests; live-prep built reusable drivers; live-worker ran the
exclusive GUI blocks; publication sanitized and published evidence; fanout
audited accountability; native agents did precision repairs, evidence
recovery and rebuttals; root integrated, froze trees, gated exclusive runs
and ran followups. Root independently matched all 960+96 C rows and 48 raw
hashes, recomputed all eight cells, reviewed source safety, and integrated native
corrections for A core/probe bytes and H route/source metadata. Final pushed-tree
verification is recorded separately in §G. No frontier/cheap token split can be
measured from these records; bulk preparation/execution/publication was OpenCode,
precision code/safety/review and final verification were native/root.

### Corrections to the fan-out audit

- Protected `tests/session_quiet_live.py` SHA256 is still
  `aa5af4d1cf3ad53ca28681ea25edaa9b2191b40f0a936b6825d0e9d62a4f3c63`
  in the working tree, and it already differed from HEAD at R5 start —
  pre-existing dirt, not an R5 live change. A git blob object ID
  (`hash-object`) is not a SHA256; never compare the two or imply a live
  change from them.
- Current a11y work commits at `9d97431`; final verification is recorded after push as described in §G.
- Machine-local references: raw sidecars and runtime-freeze logs contain
  machine-local absolute paths; public aggregates strip them (short relative
  keys + hashes only). Handoff-relative links (`R5/...`) above resolve inside
  the private handoff, not the public repo.

### Session cleanup and diff

After the human corrected the handoff method, publication followup reused the
existing session using a file handoff; no additional session was created. Four
completed auxiliary R5 sessions (checker, live-prep, live-worker, fanout-audit)
were deleted at the human’s request. The publication session and prior user
sessions remain. Prompts, raw logs, report files and independently read model
metadata remain in `R5/`; cleanup evidence is `R5/session-cleanup/`.

The full committed R5 diff is `git diff 53b77ee..HEAD` (baseline is the last R4
push). Root also saves `R5/round5.patch` after the final commit. The protected
pre-existing `tests/session_quiet_live.py` worktree change is excluded from all
R5 commits. The local, ignored `CREW.md` now records the fixed-session handoff
preference; no installed directory was synchronized.
