# F4 fix chain: independent council review

Reviewer: independent council reviewer (did not write this code).
Repo: `~/workspace/computer-use-wayland`, branch `todolist-push`.
Date: 2026-11-23.
Commits reviewed: 71ad538, 6e150f1, f51ca30, ccb0f1e, 1bf574c, 66c34f8, 9858d9a, f1cb4d5.
Method: read the full diff of each commit plus the changed code in context
(`scripts/zen_pointer.py`, `scripts/zen_backend.py`, `scripts/zen_dom.py`,
`scripts/cu.py`, `improvements/c5-zenproof-runs/zen-tab.py`); re-read the live
evidence file `/tmp/c5-zenproof-f4diag/run-f4diag.json` directly instead of
trusting the summary; re-ran the test suites myself.

## Live evidence check (read from the run JSON, not from the brief)

f4diag run 11, `/tmp/c5-zenproof-f4diag/run-f4diag.json`, confirmed as stated,
with two precision corrections:

- Program: `ok` true, `completed` 4/4, `error` null.
- Per-action bases: action 0 set_value verified `dom-value`; action 1 focus
  completed with `act_ok` true, 1/1, but its verify basis is
  `no-dom-postcondition:focus`, i.e. it passed at dispatch level, not by a DOM
  postcondition. The brief's "focus ok" is true but should not be read as a
  DOM verification.
- Action 2 Enter verified `sent-bubble`; action 3 assert verified `dom-value`.
- Delayed bubbles: count 1, exact message `ZEN-DELEGATE-F4DIAG-TEST`.
- `settle`: reads 2, stable true, elapsed 135.694 ms. See the note under
  66c34f8: this is the post-type refresh settle, not the begin_batch settle,
  because the refresh overwrites `last_settle`.
- `viewport_settle`: reads 3, settled `[240, 8]`, elapsed 207.3 ms.
- Cleanup: `ok` true, count 20 to 19, current restored to `Chat - Muse`.
- Action 0 dispatch IME trace shows `before` state `1`: the input method was
  already inactive when the set_value click ran, which is direct live proof
  that the batch-level deactivation in ccb0f1e happened before the click and
  the per-group keyboard switched nothing.

## Per-fix verdicts

### 1. 71ad538, begin_batch settles the observation: PASS

Addresses the proven root cause, not the symptom. f4diag run 3 showed the
batch meta was a mid-transition frame (old_vs_new mean 3.609 against a 3.0
preflight threshold) and no retry could help because the stored meta itself
was the bad frame. Re-observing until two consecutive frames agree (mean abs
pixel diff at most 0.5) replaces the bad frame at the source, in the one place
every batch flows through.

- Minimal and correctly placed: the old single observe became `_observe`,
  the settle loop is a separate `_settle_observation`, and the preflight
  stays the gatekeeper.
- Budget expiry is handled well: latest meta is used, `stable` False is
  recorded, and dispatch can still proceed or be refused by preflight.
  Fail-open with evidence is the right call here.
- `_mean_diff` returns inf on unreadable images or size mismatch, so a
  broken comparison burns the budget instead of passing a bad frame. Bounded
  at 2.0 s, poll 0.1 s, so worst case is about 20 extra screenshots.
- Notes, non-blocking: (a) a page that legitimately animates forever (video,
  spinner) never settles, so every batch on it pays the full 2.0 s; the 0.5
  threshold has no animation exemption. (b) Every batch now costs at least 2
  screenshots even when the first frame was already stable. Both are
  acceptable costs for the reliability gained, but they are real latency
  costs and should be measured if batch volume grows.

### 2. 6e150f1, settle before reactivating fcitx5 after literal typing: PASS WITH NOTE

The reasoning is sound (wtype exits when keys are sent, not delivered, so an
immediate restore lets in-flight keys land after reactivation and get
Telex-composed). The code is correctly placed: the 0.3 s sleep sits in the
`finally` of `literal_keyboard`, after the type and before `switch('-o')`,
only when a restore is actually needed (`original == '2'`).

- But as a standalone fix it FAILED live: f4diag run 6 still doubled. The
  verdict is therefore not "this fixed the doubling" but "this is a correct
  piece of the combination that eventually worked". It survives inside the
  batch-level scope, where it now runs once per batch instead of once per
  type group, which is the right granularity.
- Note: 0.3 s is an unmeasured magic number. Nothing in the evidence proves
  300 ms is sufficient on a loaded compositor; it is a guess that happened to
  hold on the runs so far. If doubling ever recurs under load, this constant
  is the first suspect. The sleep also uses plain `time.sleep`, not the
  cancelable wait, so a cancel during it is delayed up to 0.3 s. Trivial.

### 3. f51ca30, settle after deactivating fcitx5, before typing: PASS WITH NOTE

Same shape as 6e150f1 on the other side of the type, and the same verdict:
sound mechanism, correctly placed (after the `after_switch` record, before
the `yield`, only when a switch actually happened), but it also FAILED live
as a standalone fix (runs 4-7 still doubled with both settles in place),
because the real root cause was where the deactivation happened, not how
long after it the keys were sent. It is retained as defense in depth inside
the batch-level scope. The 0.3 s value carries the same unmeasured-constant
caveat as 6e150f1.

### 4. ccb0f1e, deactivate the input method for the whole batch, before the click: PASS WITH NOTE

This is the fix that actually killed the doubling, and the diagnosis is
convincing: fcitx5-remote reported the deactivate succeeding while the
already-focused field's text-input connection kept composing, so keys reached
the app directly AND through fcitx5. Moving the deactivation before the
focus click attacks that root cause directly. Live run 8 confirms it
(set_value verified, field holds exactly the message, input_events 24).

- Structure is correct: `ExitStack.enter_context` inside the `try`, so a
  deactivate failure is caught as a batch error; `close()` in the `finally`,
  so the input method is always restored; a restore failure sets
  `ime_restore_failed` and an error without masking a pre-existing batch
  error or un-counting groups that already ran. The updated test
  (`test_restore_failure_at_batch_end_keeps_count`, completed 2, not 1) pins
  exactly this semantic, and it is the right semantic.
- The trace test update (groups + 1 triples, batch triple nesting around the
  group triples) matches the new nesting and is asserted phase by phase.
- NEEDS NOTE, one real regression risk: a batch mixing a literal type with a
  `compose` type now types the compose text with the input method inactive.
  The per-group path for compose enters `literal_keyboard(env, False)`,
  which is a no-op and cannot reactivate anything while the batch scope
  holds the IME off (see `cu.py` lines 2114-2120 and 2178). Before this
  commit, the compose group ran after the literal group's restore, with the
  IME active. This is a narrow case (one batch rarely mixes literal and
  compose types), but it is a genuine behavior change with no test covering
  it. Recommend a test for a mixed batch, or a guard that skips the
  batch-level scope when a compose type is present. Non-blocking for landing
  the F4 chain, but it should be a follow-up item, not forgotten.

### 5. 1bf574c, surface the desktop_act IME trace on last_dispatch: PASS

Purely additive: three fields (`ime_state_trace`, `ime_restore_failed`,
`wtype_stderr`) copied from the desktop_act result onto `last_dispatch`.
No behavior change, no new failure mode (missing keys read as None). It is
also the evidence that made the doubling diagnosable at all, and the live
run 11 trace is what proves ccb0f1e worked. Nothing to object to.

### 6. 66c34f8, refresh the batch meta after a type: PASS WITH NOTES

Addresses the run 8 failure precisely: the type puts text on screen, the
batch meta predates it, so the next dispatch's preflight refuses as "screen
changed". Re-observing and settling after a successful type dispatch fixes
the stale meta at the source. Scoping is right: only after a successful
dispatch, only when the dispatch included a `type` item, click-only
dispatches do not refresh. A refresh failure is swallowed and the action
that already succeeded is not failed, with the stale meta and preflight left
as gatekeeper. Correct.

- Note 1, evidence integrity: the refresh overwrites `self.last_settle`,
  so the `settle` field on the dom_act result no longer reports the
  begin_batch settle. The run 11 value I verified (reads 2, stable true) is
  the post-type refresh settle. A begin_batch that burned its whole budget
  (`stable` False) would be silently masked by a later successful refresh.
  Recommend keeping the two settles separate (e.g. `last_settle` for begin,
  a `last_refresh_settle` for the refresh, both surfaced), so run evidence
  can no longer conflate them.
- Note 2: the refresh failure is a bare `except Exception: pass` with no
  record anywhere. A failing refresh is indistinguishable in the evidence
  from a refresh that never ran. At minimum log it or record
  `last_refresh_settle` with a failure marker.
- Note 3: the refresh only helps the NEXT dispatch, not a later group inside
  the same desktop_act batch. A batch whose type group is followed by a
  click group in the same call could still trip the preflight. The (b1)
  program dispatches per action, so this did not bite live, but the fix is
  dispatch-scoped while the staleness is batch-scoped.
- Note 4: every successful type now pays a second observe plus settle, up
  to 2.0 s when the screen keeps changing (e.g. live autocomplete). The
  (b1) program went from 2 observes to 4. Acceptable, but it doubles the
  screenshot cost of every type.

### 7. 9858d9a, assert on a sent bubble verifies by rendered text: PASS WITH NOTE

The root cause is exactly as stated: the assert target is a plain div with
no value property, so `verify_typed` and `field_value` could never verify
it, and the trailing assert could never pass (run 9: 3/4 with the bubble
present and correct). The fix is minimal and well scoped: `element_text`
reads trimmed `textContent` with the same shadow-root and iframe piercing as
`field_value`, and `_verify` falls back to it only in the `assert` branch,
only after the two value checks fail, comparing trimmed text. A missing
element returns None and fails; a mismatched bubble still fails (pinned by
the new test). `field_value`'s contract is untouched for other callers.

- Note 1, narrow false-pass edge: for a `textarea`, `textContent` is the
  default value, not the live value. An assert on a textarea whose default
  text equals the expected text could pass through this fallback even when
  the live value differs. Inputs are safe (empty `textContent`), divs are
  the intended target. Recommend restricting the fallback to
  non-input, non-textarea elements, or checking the tag before falling back.
- Note 2, cosmetic: the basis label stays `dom-value` even when the
  verification was by rendered text. Misleading in run evidence; a
  `dom-text` basis would be honest and cheap.
- Note 3: every failed assert now costs one extra CDP evaluate. Negligible.

### 8. f1cb4d5, cmd_close fallback window after DELETE; surface viewport settle: PASS

The cmd_close fix addresses the real cause of the spurious error: DELETE
discards the session's browsing context, so the next read fails even though
the close succeeded. Resolving the fallback (original tab, else any
non-scratch tab) BEFORE the DELETE and selecting it right after is the
correct ordering, and the post-DELETE select is best-effort with the
verification read kept as the real check. A DELETE failure still propagates
instead of being papered over, which is correct. The updated test
(scan-error case now finds the current tab is already the original) pins
the new behavior. Live run 11 cleanup confirms it end to end (20 to 19,
current back to Chat - Muse).

- Note: when the original-tab lookup fails, the fallback loop picks the
  FIRST non-scratch handle, which may be an `about:blank` tab rather than
  anything meaningful. That is acceptable for a browsing-context anchor
  (it only needs a live window, not the right tab), but the choice is
  arbitrary and worth one comment line.
- The viewport settle surfacing is additive and correct: `getattr` with an
  `isinstance` dict check, key omitted when the session never settled. No
  behavior change.

## Test numbers measured by this reviewer (not the author's)

Four suites named in the brief, run together:

- `tests.test_zen_pointer tests.test_zen_dom tests.test_p2_element_ref tests.test_zenproof2_fix`: 229 tests, OK, 10.7 s.

All 11 suites named across the commit messages, run together in one
invocation (the author's 417 claim):

- `tests.test_zen_pointer tests.test_zen_dom tests.test_p2_element_ref tests.test_code_exec tests.test_zenproof2_fix tests.test_dom_act tests.test_zen_cli tests.test_a1_preflight tests.test_keyboard_preflight tests.test_ime_cleanup tests.test_core`: 417 tests, OK, 41.6 s.

Per-suite counts from individual runs: test_zen_pointer 29, test_zen_dom 49,
test_p2_element_ref 100, test_code_exec 60, test_zenproof2_fix 51,
test_dom_act 19, test_zen_cli 15, test_a1_preflight 7,
test_keyboard_preflight 32, test_ime_cleanup 16, test_core 39. Sum: 417.

One discrepancy found, pre-existing and NOT caused by the F4 chain:
`test_zen_dom` run STANDALONE fails 4 tests (45/49) with
`ModuleNotFoundError: No module named 'test_click3_redteam2'` in
`test_typed_flag_not_forgeable_via_prelocked_getter`,
`test_typed_flag_not_forgeable_via_window_property`,
`test_focus_check_faithful_shadow_shim`, and
`test_hit_check_faithful_shadow_shim`. The tests import a sibling test
module that only resolves when the tests directory is on `sys.path`, which
happens in multi-suite invocations but not standalone. The last touch to
those files was the F2 commit db21dd7, not any F4 commit, and the failing
tests are about typed-flag and shadow shims, unrelated to F4. So the 417/417
claim reproduces, but only in the combined invocation order; the suite has
an order-dependent import wart that should be fixed separately (add the
tests directory to `sys.path` in the test setup, or use a package-relative
import). I did not fix it: it is out of scope for this review, and I commit
nothing.

## Overall verdict: LAND WITH NOTES

The chain is proven, not just plausible: run 11 completes 4/4 live with the
exact bubble, the doubling is gone, the stale-meta refusal is gone, the
trailing assert passes, and cleanup restores the owner tab. I reproduced
417/417 in the combined invocation myself. Every fix addresses a stated root
cause demonstrated by a numbered f4diag run, and the two IME settles that
failed standalone are honestly retained as defense in depth rather than
claimed as fixes.

Notes to carry as follow-ups, none blocking the land:

1. Mixed literal + compose batch: the batch-level IME scope breaks compose
   typing in the same batch (ccb0f1e). Add a test or a guard.
2. `last_settle` is overwritten by the post-type refresh, so run evidence
   conflates the begin settle with the refresh settle (66c34f8). Keep them
   separate.
3. Refresh failures are swallowed silently (66c34f8). Record them.
4. `element_text` fallback can false-pass on a textarea default value
   (9858d9a). Restrict by tag, and label the basis `dom-text`.
5. The 0.3 s IME settle constants are unmeasured (6e150f1, f51ca30). If
   doubling recurs under load, they are the first suspects.
6. `test_zen_dom` standalone fails 4 pre-existing import errors
   (order-dependent `sys.path` wart, F2 era). Fix separately; it is not an
   F4 regression.
