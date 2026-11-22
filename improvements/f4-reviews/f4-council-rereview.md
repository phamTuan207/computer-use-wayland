# F4 council re-review (independent, second pass)

- Commit reviewed: `98308f3` (`98308f31cdc000874d76bf944f1c97f8b83c8c33`)
- Branch: `todolist-push`, repo `~/workspace/computer-use-wayland`
- Parent commit: `4777441` (mochi B2-6 work)
- Reviewer role: independent council re-reviewer. I did not write this code.
- Previous redteam verdict: DO NOT LAND (2 blocking issues, proven with failing tests).
- Date of review: 2026-11-23
- Working tree at review time: clean except pre-existing untracked files unrelated to this commit (`git status` showed only `M tests/realistic/clone1-batch3/results.json` and unrelated untracked `improvements/*.md` files; no staged or modified files from this commit).

## Overall verdict: LAND

Both redteam blocking issues are genuinely closed, not papered over. The new tests are sensitive to the bugs they claim to cover (verified by tracing the code paths they exercise, see below). All 423 related tests pass when run by me. Live evidence from f4diag run 12 matches the claimed numbers. One real defect remains, found by this review: the new `last_refresh_settle` can go stale across batches (and on refresh failure), the same staleness class this commit fixes for `viewport_settle`. It is evidence-only, does not affect typing correctness, and has a two-line fix. I record it as a required follow-up, not a landing blocker, because the redteam treated this exact severity class (stale settle evidence) as a note, not a blocker, and the real F4 path is unaffected. Two further minor notes are recorded below.

## Blocking 1: element_text gate (redteam 9858d9a) - PASS

### What the redteam proved
The `element_text` fallback in `_verify` was unconditional, so an assert could false-pass on a field: an input's `textContent` is always `''`, and a textarea's `textContent` is its default value, not its live value.

### What the fix does
`scripts/zen_dom.py`, `ZenSession.element_text`: returns `None` when `('value' in e) || e.isContentEditable`, before reading `textContent`. The fallback in `scripts/zen_backend.py` `_verify` is unchanged and now only ever receives text for a plain element (a sent bubble div). The fake in `tests/test_p2_element_ref.py` mirrors the gate (`selector in self.fields` returns `None`).

### Why it closes the issue
- The gate is placed at the only read site, so every caller of `element_text` is covered, not just `_verify`. There is no other path that can read a field's text as if it were its value.
- The new test `test_assert_on_a_field_never_passes_by_text` covers both halves of the redteam proof: an input holding `'hello'` asserted empty fails, and a textarea with default `'hello'` but live value `'goodbye'` asserted `'hello'` fails. Both return basis `dom-value`.
- Sensitivity check (by code-path trace, not by reverting): without the gate, the textarea case would reach `element_text`, which would return `'hello'` from `self.texts`, and `_verify` would return `True`. The test would fail. The test is real, not vacuous.
- The positive path is preserved: a plain bubble div is not in `self.fields`, so `element_text` still returns its text, and the f4diag run 12 assert step verified with basis `dom-value`.

### Minor note (not blocking): the gate is slightly over-broad
`'value' in e` is true for more than form fields. A `<button>` has a `value` property, as do `<option>` and `<li value>`. Before this commit, an assert on a button's visible label could pass through the `element_text` fallback; now it returns `None` and the assert fails. `field_value` and `verify_typed` already treat buttons the same way (they read `e.value`, the value attribute, not the label), so this only removes a fallback path, and no in-repo program or test asserts on a button label. Recommended follow-up: narrow the gate to value-bearing form controls (input, textarea, select) plus contenteditable, instead of the `'value' in e` heuristic. Do not block landing on this.

## Blocking 2: batch IME scope skipped for compose batches (redteam ccb0f1e) - PASS

### What the redteam proved
A batch holding a compose type entered the batch-level literal scope, which holds fcitx5 inactive for the whole batch, while a compose group's `literal_keyboard(env, False)` is a no-op that never reactivates it. The compose type ran with the IME inactive, Telex composition could not happen, and the batch still reported ok.

### What the fix does
`scripts/cu.py`, `desktop_act`: new `has_compose_type` predicate, structurally mirroring `has_literal_type` (dict group or list group, `type == 'type'` and `ime == 'compose'`). The batch scope is now entered only when `has_literal_type and not has_compose_type`. A mixed batch falls back to per-group IME management, the pre-ccb0f1e behavior.

### Why it closes the issue
- The new test `test_mixed_literal_and_compose_batch_skips_batch_ime_scope` is exact: with fake fcitx5 state starting at `'2'`, the literal type sees state `'1'` at typing time and the compose type sees `'2'`, and the trace has exactly 6 entries (two per-group triples, no batch triple). Without the fix the batch scope would add a third triple (9 entries) and the compose type would type with state `'1'`. The test would fail. It is real, not vacuous.
- The real F4 path is unaffected: the Zen delegate never emits compose, so all-literal batches still enter the batch scope. Live evidence confirms this: f4diag run 12 action 0 shows 6 trace entries (batch triple plus group triple), i.e. the batch scope still engaged on the real path.
- Placement is minimal: one predicate plus one condition change, with the comment explaining why.

### Residual risk (not blocking): literal types in a mixed batch focus while IME is active
Skipping the batch scope re-exposes, for mixed batches only, the exact failure mode ccb0f1e was written to fix: the focus click before a literal type now happens with fcitx5 active, and only the per-group `literal_keyboard` deactivates around the keystrokes. The mitigating factor is the 300 ms deactivate settle (`IME_DEACTIVATE_SETTLE_S`), whose documented purpose is to let deactivation propagate to the already-focused field's text-input connection before the first keystroke. There is no live evidence of doubling in a mixed batch, and no in-repo caller emits mixed batches except the test. Recommended follow-up: if mixed batches ever become a real path, switch IME state at group boundaries including before each literal group's anchor click, instead of reverting to per-group scope. Do not block landing on this.

## Note fixes (redteam 66c34f8, f1cb4d5)

### Refresh settle separated from begin settle, refresh failure recorded - PARTIAL (one real defect, evidence-only)

What was done:
- `scripts/zen_pointer.py`: new `last_refresh_settle` and `last_refresh_error` on the delegate. The post-type/key refresh now writes the settle to `last_refresh_settle` (never overwriting `last_settle`, the BEGIN settle) and clears `last_refresh_error` on success or records the exception type name on failure.
- `scripts/zen_backend.py`: `dom_act` surfaces both as top-level `refresh_settle` and `refresh_error`.
- Key dispatches now refresh too, same as types: the (b1) program now takes 6 observes (2 begin plus 2 post-type plus 2 post-key). Two tests updated to 6 and a new assertion pins `last_settle` identity across the refresh.

Why the within-batch part is correct: the updated `test_meta_refreshes_after_a_type` asserts `last_settle` is the identical object after the refresh and that `last_refresh_settle` is stable with `last_refresh_error` None. A key dispatch adds 2 more observes and refreshes again. The refresh failure path cannot fail the already-successful action, which is the right call.

Defect found by this review: `last_refresh_settle` and `last_refresh_error` are only initialized in `__init__` and are never reset by `begin_batch`. A later batch that dispatches no type or key therefore surfaces the previous batch's `refresh_settle` in its `dom_act` result. I proved this with a probe against the test harness (`/tmp/probe_refresh_stale.py`): after a fill, `last_refresh_settle` was `{'reads': 2, 'stable': True, 'elapsed_ms': 1.418}`; after a second `begin_batch` with no further type/key, it was still that same dict. This is the same staleness class this commit fixes for `viewport_settle` (clear at `dom_act` start). The same defect also appears on refresh failure: the `except` branch sets `last_refresh_error` but leaves the previous successful `last_refresh_settle` in place, so a result can show a stale successful settle next to an error.

Fix (required follow-up, two lines): reset both fields in `begin_batch` (next to `self.last_settle = settle`), and clear `last_refresh_settle` in the refresh `except` branch before recording the error. Evidence-only, no typing-correctness impact, and f4diag run 12 is a single batch so its evidence is unaffected. Not a landing blocker.

### cmd_close fallback guard and only-tab skip - PASS

What was done (`improvements/c5-zenproof-runs/zen-tab.py`):
- The original-URL fallback now applies the same `candidate != scratch_full` guard the loop path already had, so the fallback can never resolve to the tab being deleted.
- When the scratch tab is the only tab, the verification reads are skipped (`after = []`); the DELETE success is the verification, since no live window remains to read from.

Why it is correct: both changes are minimal and in the right place. The two new tests are sensitive: `test_close_fallback_never_targets_the_scratch_tab` records post-DELETE window-select handles and asserts the scratch handle is absent and the owner handle is present; `test_close_only_tab_skips_verification_reads` asserts `ok` with `count_before` 1 and `count_after` 0 and an empty tab list. `_restore_original` is still called in the only-tab path and the test passes, so the restore path tolerates having no live window. One judgment call to note: `count_after` 0 is reported from the DELETE rather than observed, which is honest given there is nothing left to observe.

### Stale viewport settle cleared at dom_act start - PASS

What was done:
- `scripts/zen_backend.py`: `dom_act` clears `session.last_viewport_settle` at its start, so a batch that never calls `viewport_origin` (key-only, read-only, early-break) surfaces nothing stale.
- `tests/test_p2_element_ref.py`: the fake's `viewport_origin` now records the settle on `last_viewport_settle`, like the real session.
- New test `test_key_only_batch_surfaces_no_stale_viewport_settle`: a stale settle (`reads` 99) is planted, a key-only batch runs, and the result contains no `viewport_settle` key. The existing test was updated to plant the stale value and still expect the fresh settle (`reads` 3, `[240, 8]`, 201.5 ms).

Why it is correct: the clear is placed before any dispatch, and the comment's claim holds: `dom_observe` never calls `viewport_origin`, so clearing in `dom_act` loses nothing from the observe phase. The test is sensitive: without the clear, the planted `reads` 99 settle would surface.

## Test numbers measured by me (not the author's)

Command: `python3 -m unittest tests.test_zen_pointer tests.test_zen_dom tests.test_p2_element_ref tests.test_code_exec tests.test_zenproof2_fix tests.test_dom_act tests.test_zen_cli tests.test_a1_preflight tests.test_keyboard_preflight tests.test_ime_cleanup tests.test_core`

Result: Ran 423 tests in 42.963s, OK. This matches the author's claimed 423/423 (was 417/417, 6 new).

Per-suite counts, each run separately by me (all OK):
- test_zen_pointer: 31
- test_zen_dom: 49
- test_p2_element_ref: 101
- test_code_exec: 60
- test_zenproof2_fix: 53
- test_dom_act: 19
- test_zen_cli: 15
- test_a1_preflight: 7
- test_keyboard_preflight: 33
- test_ime_cleanup: 16
- test_core: 39
- Total: 423

New tests added by this commit (6): `test_assert_on_a_field_never_passes_by_text`, `test_mixed_literal_and_compose_batch_skips_batch_ime_scope`, `test_key_only_batch_surfaces_no_stale_viewport_settle`, `test_close_only_tab_skips_verification_reads`, `test_close_fallback_never_targets_the_scratch_tab`, plus the extended refresh assertions in `test_meta_refreshes_after_a_type` and the updated observe counts (4 to 6) in two (b1) tests.

## Live evidence check (f4diag run 12)

I read `/tmp/c5-zenproof-f4diag/run-f4diag.json` and `~/workspace/f4diag-run12.log` myself. All claimed numbers check out:
- program ok True, completed 4/4, error None
- action 0 set_value verified, basis dom-value; action 1 focus, no DOM postcondition, ok True; action 2 Enter verified, basis sent-bubble; action 3 assert verified, basis dom-value
- delayed bubbles: 1, exact message `ZEN-DELEGATE-F4DIAG-TEST`
- settle: 4 reads, stable True, 616.292 ms (the BEGIN settle)
- refresh_settle: 2 reads, stable True, 130.971 ms; refresh_error absent (None)
- viewport_settle: 3 reads, settled_moz [240, 8], 207.6 ms
- cleanup ok True, tabs_before 19, tabs_after 19, original restored True
- action 0 IME trace has 6 entries (batch scope plus group scope), confirming the batch scope still engages on the all-literal real path.

## Required follow-ups (not landing blockers)

1. Reset `last_refresh_settle` and `last_refresh_error` in `begin_batch`, and clear `last_refresh_settle` on refresh failure. The refresh evidence can otherwise describe a previous batch, the same staleness class this commit fixes for viewport settle.
2. Consider narrowing the `element_text` gate from `'value' in e` to value-bearing form controls (input, textarea, select) plus contenteditable, so asserts on button or option labels keep working.
3. If mixed literal/compose batches ever become a real path, switch IME state at group boundaries including before each literal group's anchor click, rather than relying on per-group scope alone.

## Verdict restated

LAND `98308f3`. Both blocking issues are closed with correct, minimal, well-placed fixes and sensitive tests. The remaining defect is evidence-only with a specified two-line fix, to be done as follow-up.
