# Worker Y14 redteam 2 verdict: AMEND

Redteam 2, code review only. No Zen driving, no laptop touch, no live run.
Reviewed `tests/realistic/run_batch3.py` (1993 lines, commit c7199ee, branch
todolist-push) end to end against `improvements/worker-y14-batch3-live-plan.md`
and all 10 `check.mjs` files in `/tmp/y14-stage/clone1-batch3` (staged from
main ed78e83), plus the cited sources `run_live.py`, `run_agyq2.py`,
`run_fcck.py`, the probe pages `run_batch3_probe.html` /
`run_batch3_probe_popup.html`, and the t05/t09/t10 fixtures.

Verdict: AMEND. The runner is faithful to the check suite and the first
redteam's D1-D5 fixes are real in the code (see Verified below). No
false-pass path was found and no hole will certainly fire live. But H1 is
a genuine bug with a two line fix, and H2 leaves a council rule
unimplemented. Fix H1-H5 before the slot, then re-run `py_compile` and an
import check. No live re-verification is needed for these fixes: all five
are small, reviewable, and on paths that are either rare (H1, H3) or
fail-closed (H2, H4, H5). Do NOT run live until H1 is fixed: it corrupts
t09 on exactly the hidden-body path the ladder exists to recover from.

## Verified correct (do not re-litigate)

- D1 PUA codes: `KEY_ARROW_RIGHT = "\uE014"`, `KEY_ARROW_DOWN = "\uE015"`
  (`run_batch3.py` L94-95), with Enter E007, Home E011, Left E012, Up E013
  (L90-93). Matches the W3C table. Preflight (i) asserts the recorded
  `e.key` strings are exactly `ArrowRight` and `ArrowDown` (L1641-1648).
- D2 relative handle counts: `handles_before` captured at t09 start
  (L1250), two-popups assert is `n == handles_before + 2` (L1376-1377),
  final assert is `n == handles_before` (L1399-1400). No absolute 3/1
  count remains anywhere in the runner.
- D3 sampler: preflight (vii) proves `return new Promise(...)` returns 42
  (L1745-1749) plus the bare-IIFE control returning null (L1751-1754).
  `sample_position_min` (L1426) raises on a None or non-numeric result,
  never defaults to 0. Thresholds match check.mjs exactly:
  `min_after <= 2 and min_after < pos_before` (L1477-1479), advance
  `>= 2` after a 350 ms sleep (L1483-1487), seek read 85-100 immediately
  after the 50 percent pointer click (L1514-1520), volume 50/0/30 checked
  immediately (L1495-1508).
- D4 popup tabs: `ensure_visible(..., allow_swap=False)` at the t09 popup
  require-visible point (L1271), in `reload_visible` (L371), and in
  preflight (viii) (L1773). Main tabs only reload the fixture on swap.
- D5 window.open proof: preflight (viii) clicks `#probe-popup-btn`,
  waits for a new handle, switches, asserts visible, reads `#popup-title`,
  closes, switches back, asserts the handle count returns to baseline
  (L1760-1788). The probe page opens `run_batch3_probe_popup.html` with
  `width=500,height=400` features, the same shape as the t09 popups, and
  that popup page provides `#popup-title` with text `probe popup`.
- Probe URL bug: preflight opens `/run_batch3_probe.html` (L1597-1598),
  and the probe page provides every element preflight touches:
  `#probe-input`, `#probe-range`, `#probe-pad`, `#probe-list`,
  `#probe-filter`, `#probe-items`, `#probe-popup-btn`.
- /actions payloads: key source with explicit keyDown/keyUp pairs batched
  max 10 per call (L136-186), pointer source with `pointerType: mouse`,
  `origin: viewport`, integer-rounded coords, button 0 (L188-210),
  dblclick as move/down/up/pause 50 ms/down/up in one call (L231-262).
  DELETE /actions is best effort, `{}` body first then body None, never
  raises (L112-126).
- Helpers verbatim: `select_option`, `clear_search`, `append_text` in
  `run_batch3.py` (L55-88) are byte-identical in body to `run_fcck.py`
  (L39-70). `ensure_visible` signature and `(ok, swapped)` return match
  `run_agyq2.py` (L351); all call sites pass the label and `allow_swap`
  correctly.
- Per-test translations t01-t10: checked line by line against all 10
  `check.mjs` files. Every assert is present, none weakened, no
  reordering that changes a fixture state machine. Spot checks that
  matter most: t05 sort sequence size-desc/name/size-asc/name with the
  first-item assert after each, typed cancel, empty rename (error shown,
  dialog stays open), real rename with novel name `field-notes-7.txt`,
  delete confirm-no keeps 5 then confirm-yes, move out and back, folder
  rename with padded `  Old Files 2026  ` and tree-button text assert;
  t09 prefills (Alpha, Alpha v2), status `Renamed alpha to Alpha v2.`,
  cancel dwell 500 ms with no verify (L1365), two-popups with the detail
  handle saved explicitly; t08 final toggle guard via isChecked
  (L1233-1237); t07 dirty-class asserts; t03 existence/class asserts
  (camera-off class, screen tile present via visible and absent via null
  eval, Cara the same); t04 `#empty` visible on no-match; t06 `#form-day`
  label. The only differences are details-only, as the plan states:
  t01 historyLines counts non-empty lines vs the check regex, and the t10
  supplementary D1 diagnostic is recorded in details only, never as a
  pass/fail check.
- Preflight (ii), (iii), (iv), (v), (vi): range 50/0/70 with the full
  70-key batch (L1650-1666); scrolled pointer probe with a 3 px tolerance
  (L1668-1688); dblclick on the re-rendering probe list asserting exactly
  1 (L1690-1697); empty-clear probe setting `CLEAR_FIRES_INPUT` and then
  proving `type_empty` restores 4 (L1699-1715); raw fallback proven on a
  text input and a range input (L1717-1738).
- Hidden-body wiring: `ensure_visible` reused, never reinvented; swapped
  tabs appended to `opened_tabs` so session cleanup closes them (L332-334,
  L363-365); flagged passes via `r.details["tz_hidden_removed"]` set by
  `ensure_visible` itself; circuit breaker aborts after 2 consecutive
  INFRA (L1933-1972); one INFRA-only retry (L1957-1967).
- Launch gate and mechanics: env names match `run_live.py`
  (`LIVE_SERVER_ROOT`, `LIVE_SERVER_PORT`, `LIVE_LOG`, `LIVE_RUN_ID`,
  `WD_PORT`); ports 8771/4452; `zen-bin` is the real Zen process name
  (confirmed in repo logs); Marionette 2828 TCP check; one session per
  test, always deleted in `finally` via `WD.__exit__`; `LiveMetrics`
  constructed exactly as `run_live.main()` does, including
  `default_metrics_path(LOG_PATH)`, `make_run_id`, and `live_log`.
  `py_compile` passes.

## H1 (AMEND): open_test returns a stale tab handle on the swap path

File: `tests/realistic/run_batch3.py`, `open_test` L317-352.

Evidence: `tab` is assigned from `d.new_tab(url, ...)` at L324-325. On a
swap, `ensure_visible` sets `r.tab` to the new tab (`run_agyq2.py` L459:
`r.tab = new_tab`) and the driver switches there (L336). `open_test`
then returns `tab` at L352, the OLD handle, not `r.tab`.

Blast radius: t09 does `main_tab = open_test(r, d, url)` (L1245).
`click_and_close` then does `d.switch(main_tab)` (L1289) and the
two-popup step does the same (L1370). On the swap path the driver lands
on the old hidden tab. The rename postMessage went to the NEW tab, so
`poll_effect` on the old tab never sees the effect, the check fails, and
the next Marionette click on hidden content raises. Result: t09
false-FAILs on a swap the ladder otherwise recovered. Preflight (viii)
has the same staleness (`tab = open_test(...)` L1601, `d.switch(tab)`
L1783), low impact there because only the handle-count check follows.

This fires only when a hidden-body swap happens inside `open_test`
(0 in 20 in Y4d's rerun), and it fails loudly, never silently passes.
It is still a real bug in the one function every test funnels through,
and it directly contradicts the ladder's purpose.

Exact fix: after the swap branch in `open_test`, before `return tab`,
add `tab = r.tab`. Or change L352 to `return r.tab if swapped else tab`.
Do the same audit in `reload_visible` (L355-374): it returns no handle,
so it needs no fix, but add a comment saying so.

## H2 (AMEND): hung /actions and session death are never classified INFRA

Files: `tests/realistic/run_batch3.py`, `_actions_post` L106-110,
`_is_infra` L1807-1810, `run_one` L1812-1823.

Evidence: `_actions_post` docstring says "A 30 s `_wd` timeout raises
RuntimeError and the caller treats it as INFRA". No caller does.
`press_keys`, `pointer_click_at`, and `dblclick_el` let the timeout
propagate. `run_live.py` `WD._wd` raises `TimeoutError`/`URLError` (or a
`RuntimeError` without the word INFRA) on a 30 s urlopen timeout, and
`run_one` records it as `RUNNER ERROR: TimeoutError: ...`. `_is_infra`
only matches the substrings `INFRA` and `PREFLIGHT FAIL`, so the test
gets no retry and the circuit breaker never counts it. The same gap
covers a mid-test session death (for example `invalid session id` or a
connection error) and `FIXTURE-UNAVAILABLE` raised by `ensure_visible`
(`run_agyq2.py` L371-374, L393-396), which also lacks the INFRA
substring. The plan (Council 1 A7 and the run-mechanics section)
requires hung-Actions to be INFRA with a fresh session for the next
test, and the retry rule to cover session death.

Consequence is bounded: each test already gets a fresh session, so a
hung session cannot wedge the suite. What is lost is the promised retry
and the breaker count, so one transient infra event costs a test its
pass instead of a retry.

Exact fix (smallest): in `_actions_post`, catch the timeout and raise
`RuntimeError("INFRA: /actions POST timed out")`. And in `run_one`,
classify transport and session errors as INFRA, for example by
matching `TimeoutError`, `URLError`, `invalid session id`, `no such
window`, and `FIXTURE-UNAVAILABLE` in the recorded failure string and
prefixing it with `INFRA: ` before `_is_infra` runs. Either half alone
fixes the Actions case; do both so session death is covered too.

## H3 (AMEND, minor): open_test skips the final fresh tab the plan requires

File: `tests/realistic/run_batch3.py`, `open_test` L343-347.

Evidence: on `swapped2 or not ok` the code raises `RuntimeError("INFRA:
hidden-body after rebootstrap; cannot drive")` immediately. The plan
requires one final fresh tab before finalising INFRA, and
`run_agyq2.py` `open_fixture` (L525-551) implements it: a third
`rebootstrap_tab` plus goto, clear, refresh, and `ensure_visible` with
`allow_swap=False`. The `open_test` docstring (L317-322) even claims
"(one final fresh tab before finalising INFRA)", which the code does
not do.

Exact fix: mirror the `open_fixture` final-tab block inside `open_test`
before raising, or correct the docstring and record the deviation. The
first option is a copy of about 15 lines and keeps the plan true.

## H4 (AMEND, minor): no ensure_visible after switch-backs

Files: `tests/realistic/run_batch3.py`, `click_and_close` L1289,
two-popup step L1370 and L1387, preflight (viii) L1783.

Evidence: the plan requires `ensure_visible` "after every switch
(including both switches in the t09 two-popup step, not only switch-back
to main)". The runner calls it at popup require-visible points but
never after `d.switch(main_tab)`, `d.switch(detail_popup)`, or the
preflight switch-back. A body re-hidden on switch-back would surface as
loud Marionette click failures (a false-fail, not a silent pass),
because every subsequent step clicks or types. The gap is therefore
robustness, not correctness.

Exact fix: after each of those three switches, add
`ensure_visible(d, r, allow_swap=False)` and raise INFRA if it returns
not-ok. Do not reload the fixture there: a switch-back target already
holds the fixture.

## H5 (AMEND, minor): launch gate omits two plan A4 checks

File: `tests/realistic/run_batch3.py`, `launch_gate` L1827-1898.

Evidence: the plan requires the predecessor ports 8767/8768/8769/8770
and 4448/4449/4450/4451 to be free or owned by no live runner, and the
server port to be free "or proven to serve /tmp/y14-server". The gate
checks only 8771 and 4452 free (L1860-1870) plus a `pgrep -f` sweep for
known runner scripts (L1876-1896). The sweep covers a live runner on
another port, so the practical gap is small. The gate also never checks
that `LIVE_SERVER_ROOT` exists and holds the suite: a missing
`/tmp/y14-server` is only caught at the first test failure (loud 404
via FIXTURE-UNAVAILABLE, not silent).

Exact fix: add a loop over the eight predecessor ports failing closed
on a bind failure, and add `os.path.isdir(os.environ["LIVE_SERVER_ROOT"])`
plus a probe that `/clone1-batch3/t01-terminal/fixture.html` exists
under it, before any Zen driving.

## Minor items (fix with H1-H5, no separate gate)

- M1: preflight (vi) sends the raw Enter to `#probe-input` (L1722)
  without clicking or focusing it first. Focus sits on `#probe-filter`
  from step (v). The proof relies on Marionette element/value focusing
  the element implicitly. If it does not, the raw-text check fails and
  preflight aborts fail-closed, but the abort would be spurious. Fix:
  add `d.click("#probe-input")` before the raw send at L1722, matching
  the explicit click already done for the raw range test at L1730.
- M2: the t10 min-in-3-5 rule is not in the code. The plan says a min of
  3-5 with a sampler start gap over 200 ms is INFRA/timing with one
  retry, not a fixture failure. The code only has the plain check at
  L1477-1479. The gap is derivable post-hoc from the step log
  timestamps, so this is an analysis rule for the report, not a code
  defect. If t10 fails with min 3-5, check the log gap before calling
  it a fixture failure, and record the gap in the report either way.

## Surviving doubts (not holes)

- Y15 precondition: this runner translates the ed78e83 checker
  (`min <= 2`) plus the supplementary D1 diagnostic (L1581-1590). The
  plan says Y15 will fix D1 on main BEFORE Y14 runs live, which changes
  the suite under test. This AMEND is conditional on the staged suite
  still being ed78e83 at slot time. At slot time, re-verify the staging
  md5s against the then-current main HEAD; if Y15 has landed, re-stage,
  update the t10 translation to Y15's checker, and drop or keep the D1
  probe only as a duplicate diagnostic.
- The t10 sampler start gap (click return to first sample) is unmeasured
  until live. Loopback round trips should keep it well under 200 ms, but
  if t10 fails with min 3-5, see M2.
- `open_popup` takes the first new handle (`L1263-1274`). If a user tab
  opened at the same moment, the runner could grab the wrong handle.
  The machine is handed over, so this is unlikely, but the two-popups
  assert would catch it loudly.
- The t10 seek click uses `pointer_click_at` without a prior
  scroll-into-view or elementFromPoint check (unlike `click_nth` and
  `dblclick_el`). The bar sits above the fold at 1863x1176, so this is
  low risk; a covered bar would false-fail, not false-pass.
- Shipping: `run_batch3.py` inserts its own directory on `sys.path` and
  imports `run_live` and `run_agyq2`, which in turn import
  `live_metrics` from `scripts/` or its own directory. Ship all four
  files together to the laptop and verify the import on the laptop
  before the slot. If the import fails, metrics silently degrade to off
  (one stderr line) and the run proceeds unmeasured; the post-preflight
  metrics-file print only reports, it does not fail.
- `Runner` defines no `self.tab` default. Audit found every `r.tab`
  read in `run_batch3.py` sits on a path where `ensure_visible` has
  already set it, so there is no AttributeError risk. No change needed.
- The circuit breaker counts final test outcomes (post-retry), not
  per-attempt INFRA events. Two tests that each fail INFRA once and
  pass on retry will not trip it. That reading of "2 consecutive INFRA
  failures" is defensible; a Zen that fails once per test and recovers
  is not wedged.

## Method

Read `run_batch3.py` fully (L1-1993), read all 10 `check.mjs` files and
compared each assert to the runner, read the t05/t09/t10 fixtures
(including detail.html and prefs.html), read `run_batch3_probe.html`
and `run_batch3_probe_popup.html`, verified the reused code in
`run_live.py` (WD, Runner.step/check, start_server, LiveMetrics
construction), `run_agyq2.py` (`ensure_visible`, `rebootstrap_tab`,
`open_fixture`), and `run_fcck.py` (helpers byte-compared), and ran
`py_compile` (passes). No browser use, no live run, no laptop access.
