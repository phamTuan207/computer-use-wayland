# F4 fix chain redteam review

Independent reviewer. I did not write this code. I tried to break it.

Scope: repo `~/workspace/computer-use-wayland`, branch `todolist-push`.
Commits attacked: `71ad538`, `ccb0f1e`, `66c34f8`, `9858d9a`, `f1cb4d5`.

## Verdict: DO NOT LAND as-is

Two blocking issues, both proven with failing tests (see Probes).
Both fixes are small and described under each issue. Everything else
is notes or survived.

Blocking issues first:

1. **9858d9a, element_text fallback: assert can now FALSE-PASS on
   fields.** The fallback is unconditional after `verify_typed` and
   `field_value` fail, but `textContent` is not the value for elements
   that have a value property. Two concrete repros, both failing
   tests in `/tmp/f4_redteam_probes.py`:
   - An input holding `"hello"` has `textContent` `""`. Asserting
     the field is empty (`text: ""`) now returns True. A real
     "field was cleared" check passes when the clear failed.
   - A textarea whose default text is `"hello"` and whose current
     value is `"goodbye"` (after typing) has `textContent`
     `"hello"`. Asserting `"hello"` now returns True. `textContent`
     is the default value, not the live value.
   The same shape applies to a select (textContent is all options
   concatenated, not the selected value). A false pass in a
   verification primitive is worse than a false failure: it reports
   success on a wrong state. Fix: gate the fallback to elements
   with no value property (check `'value' in e` and
   `isContentEditable` in the JS, or only fall back when
   `field_value` returned null AND the element is not an input,
   textarea, select, or contenteditable). The intended case (plain
   div bubble, no value property) keeps working; the control probe
   for it passes.

2. **ccb0f1e, batch-level IME: a mixed literal + compose batch now
   mistypes the compose text silently.** `has_literal_type` is true
   when ANY group holds a literal type, so the batch scope holds
   fcitx5 inactive for the whole batch. A compose group enters
   `literal_keyboard(env, False)`, which is a no-op and never
   reactivates, so the compose type runs with the IME inactive and
   Telex composition cannot happen. Failing test: batch
   `[click, type 'a', type 'b' (ime compose)]` with fcitx5 starting
   active records the IME state at each typing call as `['1',
   '1']`; the correct states are `['1', '2']`. The batch still
   reports ok True, so the wrong text lands with no error. Before
   this commit each group had its own scope and the compose group
   ran with the IME active. Trigger is narrow in production (the
   Zen delegate never emits compose; only direct `desktop_act`
   callers mix modes, and `exact_live.py` uses compose-only
   batches), but it is a silent wrong-output regression in a
   previously correct path. Fix: either do not enter the
   batch-level scope when the batch also holds a compose type
   (fall back to per-group scopes for mixed batches), or make a
   compose group's scope re-activate the IME for its duration.

## Per-fix attack log

### 71ad538, begin_batch settle (SURVIVED, with notes)

Attacks tried:

- Slow fade, consecutive-agreement does not bound total drift.
  A linear fade with per-step diff under 0.5 declares stable on
  the first pair while the frame is still mid-fade. Benign here:
  a cross-fade does not move geometry, grounding is DOM-rect
  based (not vision), and the preflight compares the meta against
  a near-contemporaneous screenshot, so a mid-fade meta passes
  preflight with a small diff instead of tripping it. The settle
  only needs to avoid the refusal case (meta mid-fade vs settled
  screen, mean 3.6), and it does that.
- Screen that never settles (video, spinner, clock). The loop
  burns the full 2.0s budget every batch, reports stable False,
  and the preflight refuses as before. Same refusal outcome as
  pre-fix, plus a 2s latency penalty per batch. Not a correctness
  break.
- Window resize between observations. `_mean_diff` returns inf
  on size mismatch, so the settle never converges and burns the
  whole budget on every batch during a resize animation. Latency
  only; preflight refuses anyway on geometry change.
- Budget overshoot. The budget is checked only after each
  observe plus compare, so slow observes can push a batch well
  past 2.0s. Latency only.
- Mid-transient plateau (two agreeing frames mid-transition).
  Possible in principle (two-stage animation with a pause), but
  the preflight is the backstop: worst case is a refused batch,
  never wrong input.
- `_observe` raising mid-settle propagates out of `begin_batch`
  and refuses the batch. Same as pre-fix (one observe then), only
  more chances to hit a transient screenshot failure. No new
  failure class.

No failing test found for this commit. The settle does its job
for the observed failure (tab-switch ghost, mean 3.6).

### ccb0f1e, batch-level literal_keyboard (BROKEN, see blocking 2)

Attacks that SURVIVED:

- Batch with NO literal type. `has_literal_type` is false, no
  batch scope is entered, the IME is untouched. Verified by
  reading the gate and by the existing trace tests.
- Literal type in a LATER group. The scope spans the whole batch
  from before the first action, so a later type is covered. The
  field is focused while inactive regardless of group order.
- Deactivate failure. `enter_context` is inside the try, so a
  failure is a batch error (ok False, completed 0), and the
  empty stack close is a no-op. Verified in code.
- Restore failure. The `finally` close records
  `ime_restore_failed`, keeps the batch error if there is one,
  and never masks a primary error. The per-group re-entry sees
  state '1', skips the switch and both settles, and records
  'unchanged' / 'not_requeried'. The trace test asserts the
  interleaving (batch triple around group triples).
- Preflight runs before the try, so a refused batch never
  touches the IME.
- Signal during typing. The inner scope restores handlers to the
  outer handler and the outer scope still restores the IME.

Attack that BROKE it: mixed literal + compose batch (blocking
issue 2 above). Failing test `test_compose_type_sees_active_ime`
in `/tmp/f4_redteam_probes.py`.

### 66c34f8, post-type meta refresh (SURVIVED functionally, 2 notes)

Attacks that SURVIVED:

- Refresh failure. The `except Exception: pass` keeps the stale
  meta and the preflight stays the gatekeeper. The action that
  already succeeded is not failed. Verified in code.
- Window address change. `_window_address` is fixed at
  `begin_batch`. The Zen Hyprland window address does not change
  on tab switches inside Zen; if the window is gone, `_observe`
  raises and is swallowed as above.
- Click-only dispatch does not refresh, by design, and the
  existing test asserts it.
- Refresh runs before the backend `_verify`, so it only costs
  latency, never verification correctness.

Notes (not blocking):

- N1. The refresh OVERWRITES `last_settle`, so the dom_act
  result `settle` no longer says whether the batch STARTED
  stable once a type ran. Failing test
  `test_last_settle_still_describes_batch_start_after_type`:
  begin_batch settles stable, the type refresh runs its own
  unstable settle, and `last_settle['stable']` is then False for
  a batch that started stable. The 71ad538 commit message defines
  `last_settle` as the begin_batch outcome, and the evidence now
  contradicts that definition after any type. Diagnostic-only.
  Fix: keep the begin settle under its own key and record the
  refresh settle separately.
- N2. The refresh triggers ONLY on type. A key dispatch that
  changes the screen does not refresh, which is the same failure
  class this commit fixed for type. Failing test
  `test_screen_changing_key_refreshes_meta`: after an Enter that
  sends the bubble (`sent_bubbles` grows), observe count stays
  2 and the meta is still the pre-Enter frame. A program shaped
  `[fill, key Enter, click ...]` would hit a preflight
  'screen changed' refusal on the click in real `desktop_act`
  (the fake backend has no preflight, so the refusal itself was
  not reproduced in unit tests). Same for a click that navigates
  or opens a menu. Fix: refresh after any dispatch that can
  mutate the screen, or at least after key dispatches.

### 9858d9a, assert by rendered text (BROKEN, see blocking 1)

Attacks that SURVIVED:

- Fallback runs only after `verify_typed` AND `field_value`
  fail, so there is no extra DOM read on the pass path.
  Performance question from the brief: no, the extra evaluate
  happens only on the failure path.
- A mismatched bubble still fails (existing test asserts it).
- Cross-origin iframe target returns null from `element_text`
  and the assert fails, never silently passes.
- `field_value` contract is unchanged for other callers.

Attack that BROKE it: unconditional fallback on elements with a
value property (blocking issue 1 above). Failing tests
`test_assert_empty_on_nonempty_input_must_fail` and
`test_assert_default_text_on_changed_textarea_must_fail`.

One more note: a bubble div containing nested elements (a time
span, a second line) has `textContent` with that extra text, so
an exact-equality assert fails even though the message is
there. That is a false negative limitation of exact matching,
not a false pass, and the fixture bubble is a plain div, so it
does not bite the live program. Worth knowing before reusing
this assert shape on real chat UIs.

### f1cb4d5, cmd_close fallback window (SURVIVED in the live shape, 2 residual holes)

Control probe PASSES: with a fake that models the live
Marionette behavior (after DELETE closes the current window,
every `_wd` call fails with 'Browsing context has been
discarded' until a POST /window selects a live window), closing
a scratch tab with an owner tab present succeeds, count 3 to 2,
scratch gone. The fix works in the live shape, consistent with
f4diag run 11 (cleanup ok True, count 20 to 19).

Residual holes, both demonstrated with the same discarded-
context fake:

- H1. Scratch tab is the ONLY tab. `fallback` is None (no
  non-scratch handle exists), no POST runs, and the
  verification read `after = _handles(z)` raises
  `ZenDomError: Browsing context has been discarded` at
  `zen-tab.py` line 580 even though the DELETE succeeded. The
  exact spurious error this commit was meant to kill survives
  when there is no fallback window. Not live in the runner
  (the fixture run always has the owner tab alongside), but the
  function contract does not require 2+ tabs. Fix: when
  `fallback` is None, do not let the verification read raise
  away a successful close; return ok with a flag such as
  `context_discarded_no_fallback` instead.
- H2. The original-entry path has no scratch exclusion. The
  loop path guards `h != scratch_full`, but the
  `_find_in_scan(entries, original_url)` path does not. When
  `original_url` matches the scratch tab itself, `fallback` IS
  the tab about to be deleted, the post-DELETE POST selects a
  dead handle, and the verification read raises. Trigger needs
  a caller passing a URL that matches the scratch tab, so this
  is a hardening gap, not a live bug. Fix: skip the fallback
  when it equals `scratch_full`.

Related test gap: NO existing test models the discarded
browsing context at all (the repo `FakeSession` answers reads
happily with current None), so the central mechanism of this
commit was unproven by the suite until my control probe above.
The one updated test
(`test_restore_original_scan_error_flagged_not_ambiguous`, now
expecting `current_url == OWNER_URL`) only checks the
post-DELETE current tab, not the discarded-context recovery.

### f1cb4d5, viewport_settle surfacing (SURVIVED as a field, STALE value in 3 shapes)

`dom_act` surfaces `session.last_viewport_settle`, but that
attribute is session-global and is only written by
`viewport_origin`. `dom_observe` does not call it, and
`_screen_point` (the only `viewport_origin` caller inside
`dom_act`) is skipped for key actions, skipped for
wait/assert actions, and never reached when the batch breaks
on revalidation before any dispatch. Failing test
`test_key_only_batch_does_not_surface_stale_settle`: a key-only
batch surfaces a previous batch's settle record (`reads 3,
settled_moz [240, 8]`) although this batch never called
`viewport_origin`. Diagnostic-only, but the commit's claim
("run evidence says whether the viewport origin was settled
when the batch grounded its points") is false for key-only
batches, read-only batches, and early-break batches. Also,
when a verified origin is used, `last_viewport_settle` stays
None and the key is absent, which is at least honest. Fix:
snapshot the value at `dom_act` entry and surface it only if
`viewport_origin` ran during this batch (or reset it at batch
start when the batch will ground points).

## Test numbers measured by me

- Claimed suite: 417/417 across 11 suites. Reproduced exactly:
  `python3 -m unittest tests.test_zen_pointer tests.test_zen_dom
  tests.test_p2_element_ref tests.test_code_exec
  tests.test_zenproof2_fix tests.test_dom_act tests.test_zen_cli
  tests.test_a1_preflight tests.test_keyboard_preflight
  tests.test_ime_cleanup tests.test_core` -> `Ran 417 tests in
  42.107s, OK`.
- My probes: `/tmp/f4_redteam_probes.py`, 10 tests, 0.6s.
  2 controls pass, 8 demonstrate defects (6 FAIL, 2 ERROR):
  - FAIL `test_assert_empty_on_nonempty_input_must_fail`
    (9858d9a false pass, input)
  - FAIL `test_assert_default_text_on_changed_textarea_must_fail`
    (9858d9a false pass, textarea)
  - ok `test_assert_on_bubble_still_passes` (control, intended
    9858d9a case works)
  - ok `test_multi_tab_close_succeeds_with_discarded_context`
    (control, f1cb4d5 works in the live shape)
  - ERROR `test_single_tab_close_reports_success` (f1cb4d5 H1,
    raises ZenDomError at the post-DELETE handles read)
  - ERROR `test_fallback_never_resolves_to_scratch_itself`
    (f1cb4d5 H2, raises at the same read)
  - FAIL `test_screen_changing_key_refreshes_meta` (66c34f8 N2,
    observe count stays 2 after a screen-changing Enter)
  - FAIL `test_compose_type_sees_active_ime` (ccb0f1e blocking 2,
    states `['1', '1']`, expected `['1', '2']`)
  - FAIL `test_last_settle_still_describes_batch_start_after_type`
    (66c34f8 N1, refresh overwrites the begin settle)
  - FAIL `test_key_only_batch_does_not_surface_stale_settle`
    (f1cb4d5 viewport staleness)
- Live evidence checked: `~/workspace/f4diag-run11.log` shows
  `completed 4` (twice), `count_before 20` / `count_after 19`,
  17 `ok true`, `stable true`. Consistent with the task's claim
  (program ok True, 4/4, bubble sent, cleanup ok True). The live
  run does not cover the blocking issues: its asserts are on a
  bubble div and a field value, and its batches hold no compose
  type.

## Notes on the two blocking fixes

- For 9858d9a, the smallest correct gate is inside the
  `element_text` JS or in `_verify`: fall back to rendered text
  only when the element has no `value` property and is not
  contenteditable. That keeps the bubble case and closes both
  false-pass repros.
- For ccb0f1e, the smallest correct scope is: enter the
  batch-level scope only for batches with no compose type; mixed
  batches keep the old per-group scopes. Alternatively the
  compose group's scope re-activates. Either way, add the mixed
  batch test (my probe) to `test_keyboard_preflight.py`.

## What I did not do

- Committed nothing. The probe file is scratch at
  `/tmp/f4_redteam_probes.py` (not in the repo); it imports the
  repo's own test fakes. The repo working tree is untouched
  except for this review file.
- No live browser work: the preflight-refusal consequence of N2
  was reasoned from the real `desktop_act` preflight, not
  reproduced live, because the unit fakes have no preflight.
  The delegate-level staleness behind it is proven by the probe.
