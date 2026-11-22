# F4 redteam re-review: commit 98308f3

- Commit attacked: `98308f3` (on branch `todolist-push`, on top of mochi B2-6 `4777441`)
- Reviewer: independent redteam, did not write this code
- Date: 2026-11-23
- Probe file: `/tmp/f4_rereview_probes.py` (24 probes, 24 passed, 0 failed)
- Verdict: **LAND**, with 3 non-blocking issues below

## Verdict and bar

The previous redteam blocked on two issues: a false-pass assert on fields
and a silent wrong IME state on mixed batches. Both are genuinely fixed
and re-proven below, including harder variants than the shipped tests
(click-first mixed batch, compose-first order, compose nested in a list
group with a key). I tried to break every fix and found no remaining
false pass, no silent wrong output, and no crash. What I did find is
evidence mislabeling (stale settle fields), a spurious error flag on a
successful close, and a fake/real divergence plus an over-broad gate.
None of them changes an action outcome, so none blocks landing. They
should be fixed as follow-ups, because two of them are the same
staleness class the commit itself fixed for one field and left for two
others.

## Blocking 1 re-attack: element_text gate (SURVIVED)

Re-ran the previous redteam's probes against the fixed code, plus a
bubble control:

- B1a: input holding `hello`, assert empty: verified False, basis
  `dom-value`. FAILS as required.
- B1b: textarea default `hello`, live value `goodbye`, assert `hello`:
  verified False, basis `dom-value`. FAILS as required.
- B1c: sent bubble div, assert `hello`: verified True, basis
  `dom-value`. Control still PASSES.

Why the gate is coherent, not just patched: `field_value` in
`scripts/zen_dom.py` uses the exact same predicate
(`'value' in e ? e.value : null`, plus the contenteditable branch).
`element_text` now returns text exactly when `field_value` would
return None and the element is not contenteditable. The two functions
cannot disagree about whether an element is value-bearing. I could
not find any value-bearing element the gate misses: `input`,
`textarea`, `select`, `button`, `option` all have a `value` IDL
attribute; a custom element with a `value` property is caught by the
`in` operator (own plus prototype chain); closed shadow roots and
cross-origin iframes fail closed (find returns null).

Attacks that did NOT break it:

- A `select` whose textContent is all options concatenated: gate
  returns None, correct.
- A contenteditable child (isContentEditable is inherited): gate
  returns None; the assert path verifies it through `verify_typed`
  first, which handles contenteditables.
- A custom element storing its value only as an attribute with no
  IDL property: `'value' in e` is False, so text is read, but
  `field_value` also returns null there, so the text fallback is the
  only signal and is the displayed text. Not a hole.

## Blocking 2 re-attack: batch IME scope vs compose (SURVIVED)

Re-ran the mixed-batch probe against the fixed code, with variants:

- B2a: `[click, type 'a', type 'b' compose]` types with IME state
  `['1', '2']`, ok True, exactly 6 trace entries (two per-group
  triples, no batch triple). The click-first shape matters because the
  batch scope used to deactivate before the focusing click; with the
  fix the literal group still deactivates before its own typing.
- B2b: compose FIRST, then literal: states `['2', '1']`. Order
  independent, as claimed: each group enters and exits its own IME
  context, the compose group's `literal_keyboard(env, False)` is a
  no-op and the literal group's deactivates fresh.
- B2c: compose nested in a list group with a key
  (`[key 'x', type 'b' compose, type 'a' literal]`): states
  `['2', '1']`. `has_compose_type` catches the compose type inside
  the list group, as its list branch intends. I also checked
  `keyboard_groups`: a list group cannot hold both a literal and a
  compose type (it splits on mode change), so the per-group `exact`
  computation cannot see a mixed group; the dict branch covers
  dash-prefixed types that bypass grouping.
- B4 (attack killed by existing code): I tried a type with
  `ime=None`, where the per-group code treats any non-literal ime as
  compose-like but the batch gate only recognises `ime == 'compose'`.
  `validate_actions` (`scripts/cu.py:1318`) rejects any ime outside
  `('literal', 'compose')` with `ime must be literal or compose`
  before `desktop_act` runs, so the hole is unreachable through the
  real entry point. The batch gate matches the validated domain
  exactly.

## Notes re-attack

### Refresh separation and key refresh (SURVIVED, with a cost note)

- G1: three keys cost 2 observes each (8 total after a 2-observe
  begin), no loop. The refresh is once per dispatch, bounded by
  `SETTLE_BUDGET_S` (2s); `_observe` / `_settle_observation` never
  call back into `__call__`, so there is no recursion and no runaway
  when a key opens a new window or a dialog.
- G2: refresh failure on a key: the action still returns ok True and
  `last_refresh_error` is set to the exception type. Recorded, never
  swallowed.
- E0: the (b1) program takes 6 observes (2 begin + 2 post-type + 2
  post-key), matching the two updated tests; begin settle is
  untouched by the refresh (identity check in the shipped test, and
  my probe).
- Cost note (not blocking): EVERY key refreshes, including no-op
  keys (arrows, modifiers, Tab). A key-heavy batch pays 2+ observes
  plus a settle loop per key, and an unstable screen burns the full
  2s settle budget per key. Also, by design, the refresh absorbs a
  navigation the key caused, so the next action's preflight no longer
  refuses it as 'screen changed'. That is the same class as the
  pre-existing type refresh, not a new failure mode.

### Viewport clear (SURVIVED, with a minor ordering wart)

- E1b/E2c: a click batch surfaces its own fresh viewport settle
  (reads 3, [240, 8]), not a planted stale sentinel (reads 99); a
  key-only batch surfaces no viewport settle at all. The fix works.
- The task's same-batch question is answered by ordering: the clear
  runs at the very start of `dom_act`, before `_bound_snapshot`,
  before the window-move `dom_observe`, and `dom_observe` never
  calls `viewport_origin` (it calls `harvest`, `_zen_window_bounds`,
  `_window` only), so there is no same-batch settle for the clear to
  erase.
- H1 (minor wart, proven): the clear runs BEFORE `_bound_snapshot`
  validation, so a `dom_act` call that fails fast on an unbound or
  stale snapshot still wipes the previous batch's viewport settle.
  Evidence loss on an error path. Move the clear after the binding
  check.

### Non-blocking issue 1: the staleness fix covers 1 of 3 fields

Proven with probes E1, E2, E2b (same backend, three batches in a row):

- E1: a click-only second batch surfaces a STALE `refresh_settle`
  from batch 1, although no type or key ran in batch 2.
- E2: an assert-only third batch surfaces a STALE begin `settle`
  from batch 2 (read-only batches skip `begin_batch`, and nothing
  clears `last_settle`).
- E2b: the same assert-only batch also surfaces the STALE
  `refresh_settle` from batch 1.

The commit fixed this exact staleness class for `viewport_settle`
(clear at `dom_act` start) but left `last_settle`,
`last_refresh_settle`, and `last_refresh_error` uncleared:
`begin_batch` only overwrites `last_settle` when input is needed,
and nothing anywhere clears the refresh fields. The `refresh_settle`
instance is introduced by this very commit. Severity is low: I
grepped and nothing outside `zen_backend.py` / `zen_pointer.py`
consumes these fields, so no decision is made on the stale values;
it is run-evidence misattribution. The shipped test
(`test_key_only_batch_surfaces_no_stale_viewport_settle`) checks only
`viewport_settle`, so it is blind to the other two. Fix: clear all
three pointer fields at `dom_act` start (or in `begin_batch` plus a
read-only path), mirroring the viewport clear.

### Non-blocking issue 2: cmd_close only-tab reports scan_error on success

Proven with probe F1, using a realistic fake whose `list_tabs`
raises `ZenDomError('Browsing context has been discarded')` when no
tabs remain, matching the real session (real `list_tabs` calls
`current_handle()`, a GET /window, before the scan loop; with zero
tabs that read fails, which is the fix's own premise for skipping
the verification reads):

- F1: only-tab close returns `ok True, count_after 0`, the close is
  NOT masked, but the result also carries `scan_error True`,
  `current_title ''`, `current_url ''`.
- F1c: the shipped fake's `list_tabs` never raises on empty tabs,
  so the shipped test sees `original_missing True` instead and
  asserts neither flag. The test is blind to the real outcome.

The close itself is correct and `ok` is not masked, so this does
not block. But `scan_error` is documented as "a scan failure is an
error, not ambiguity", and here the scan fails by design: there is
no window left and nothing to restore to. A reader or future
consumer that gates on `scan_error` will misread a full success as
a partial failure. Fix: skip `_restore_original` (or pass it a flag)
when the fallback is None, since there is nothing to restore to.

### Non-blocking issue 3: fake/real divergence and the over-broad gate

- A4a/A4b/A4c (proven in the fake): the fake's gate is
  `selector in self.fields`, while the real gate is `'value' in e`
  plus `isContentEditable`. A button, a select, or a contenteditable
  div that is not in `self.fields` returns its text in the fake and
  the assert PASSES, while the real `element_text` returns None and
  the same assert FAILS. The fake also never models the
  contenteditable half of the gate at all.
- The real gate is over-broad in the other direction, grounded in
  the HTML standard (WHATWG, MDN): `button`, `option`, `li`, `data`,
  `meter`, `progress`, `param` all define a `value` IDL attribute,
  so `'value' in e` is true for them, yet their textContent is
  meaningful and independent of their value. The spec says a button
  is "labeled by its contents" while its value is "for the purposes
  of form submission" (empty string when no value attribute). So an
  assert on a button's visible label, which passed before this
  commit via the text fallback, now fails. Same for an option label
  when a value attribute is present, and for `li value` ordinals.
- Why this does not block: the failure direction is loud (the assert
  fails, the batch stops) rather than a silent false pass, and no
  real program in the repo asserts button or option labels (asserts
  target fields and sent bubbles). The precise gate would be
  tag-based (input, textarea, select, contenteditable), but that is
  a refinement, not a correctness fix for the reported blocking
  issue. The fake should be fixed to mirror the real gate
  (value-bearing selectors plus contenteditables return None),
  otherwise the suite cannot catch regressions in this area.

## Test numbers measured by this reviewer

Four suites touched by the commit, run by me on 2026-11-23:

- `tests.test_keyboard_preflight`: 33 tests, OK
- `tests.test_p2_element_ref`: 101 tests, OK
- `tests.test_zen_pointer`: 31 tests, OK
- `tests.test_zenproof2_fix`: 53 tests, OK
- Total for the four touched suites: 218/218 OK
- Wider related set run by me (16 suites: test_zen_dom,
  test_zen_cli, test_c5_zenproof_p15, test_dom_act,
  test_type_verification, test_input_validation, test_ime_cleanup,
  test_core, test_first_action, test_session_driver,
  test_act_diagnostics, test_focus, test_click2_redteam,
  test_click3_redteam2, test_pick4_fastpath, test_cancel_l1):
  579/579 pass. One import error appeared in the combined run
  (`test_type_verification` fails to import as `tests.*` because it
  does `from test_keyboard_preflight import ...`); run standalone
  from `tests/` it passes 63/63, so the error is an invocation path
  artifact, not a failure in this commit.
- The commit message claims 423/423 "related suites". I could not
  reproduce that exact set: the four touched files total 218 and my
  wider 16-suite set totals 579, so 423 refers to some other
  selection the commit does not name. Every suite I ran passes, so
  this is an unverified count, not a failing suite.
- My independent probes: 24/24 passed (`/tmp/f4_rereview_probes.py`)

## Live evidence checked

`~/workspace/f4diag-run12.log` matches the cited numbers: `dom_act
ok True completed 4`, `settle` reads 4 stable True, `refresh_settle`
reads 2 stable True, `viewport_settle` reads 3 settled [240, 8],
`refresh_error` absent (None), bubble sent, cleanup ok True
(`original_restored` True, `count_restored` True, `pill_release`
ok True).

## Follow-ups (non-blocking, in priority order)

1. Clear `last_settle`, `last_refresh_settle`, and
   `last_refresh_error` per batch the same way `dom_act` now clears
   the viewport settle, and extend the stale-settle test to cover
   all three fields on a read-only batch.
2. Skip `_restore_original` in `cmd_close` when the fallback is
   None (scratch was the only tab), so a successful close does not
   carry `scan_error True`; extend the only-tab test to assert the
   absence of `scan_error`, using a fake whose `list_tabs` raises
   when no tabs remain.
3. Make the fake `element_text` mirror the real gate (value-bearing
   selectors and contenteditables return None) and consider a
   tag-based gate so button and option labels stay assertable.
4. Move the viewport-settle clear in `dom_act` to after the
   `_bound_snapshot` check, so a failed call does not destroy the
   previous batch's evidence.
