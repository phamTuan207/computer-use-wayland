# CLICK3-DIFF-ASSESS: verdict on AMEND2's uncommitted work

Worker: CLICK3-DIFF-ASSESS (independent reviewer). Coordinator: COORD-CLICK-2.
Owner: the owner. Branch: todolist-push. Base at task start: da60024.
Note: HEAD moved under me during assessment to dd45231 (CLICK3-RT-SYNTH,
a doc-only commit adding improvements/worker-click3-rt-synth.md, 1 file).
The uncommitted diff is unchanged: 24 files, +2496/-304, same as at start.
No commit made by this worker except this report file itself (explicit
pathspec, verified with git ls-remote; see the end of this log).
No live laptop driving, no browser work, never ydotool. No em dash or
en dash anywhere in this file. All times wall-clock Asia/Ho_Chi_Minh.

## Time log (elapsed from task start 04:33 +07)

- 04:33 +00m task received; branch todolist-push, HEAD da60024, 24 files
  modified uncommitted (+2496/-304).
- 04:34 +01m probe log (cd89597), amend log (CLICK-AMEND 12/12), RT log
  (13 findings R1-R13), AMEND2 log read. Full diff (3780 lines) read.
- 04:40 +07m syntax check: all 11 changed .py files py_compile OK,
  cdp.mjs node --check OK. 0 em/en dashes in the diff, no ydotool use,
  git diff --check clean.
- 04:42 +09m test runs: RT suite 71/71 OK; 10 neighbor suites all OK;
  cdp_validation.mjs OK.
- 04:44 +11m targeted probes: R3a wrong-field band still passes with
  real text; R10 JS-set value on an empty field still verifies.
- 04:46 +13m full discover: 1850 tests, 1 failure + 4 errors + 17 skipped.
- 04:52 +19m fail-before check in a temp worktree at HEAD: the 1 failure
  is a genuine AMEND2 regression (passes on HEAD, fails on the AMEND2
  tree). Worktree removed.
- 04:55 +22m report written, committed (explicit pathspec), push verified.

## Overall verdict: KEEP MOST, fix 4 files surgically, redo nothing

About 90% of AMEND2's work survives verbatim. Zero files need a wholesale
redo. The C12 window-relative fix is implemented correctly at the
zen_dom.py level (the core of the task), R2/R4/R5/R6/R7/R8/R9/R11/R12/R13
are fixed in substance, and all 23 RT proof tests now pass (71/71 in
tests/test_click2_redteam.py, was 21 failures + 1 error).

But the verdict is NOT a clean GO, for four concrete reasons:

1. ONE REAL REGRESSION: AMEND2's cdp.mjs set_value change breaks the
   pre-existing contract in tests/cdp_snapshot.mjs:193. Full discover
   is 1850 tests with 1 failure, and that failure is this regression,
   proven by fail-before (passes on HEAD dd45231, fails on the AMEND2
   tree). See "Regression" below.
2. THREE RT TESTS PASS WITHOUT FIXING THE FINDING: R1, R3a, R10. Each
   passes because of a fixture or a fallback, not because the attack is
   closed. I proved each with a direct experiment (see "Passing tests
   that do not prove the fix").
3. TWO PARTIAL files (cu.py, fastpath.py) need small surgical changes,
   plus one cosmetic fix in zen_cli.py and one latent unit-mixing flaw
   in check_viewport_geometry at scale factors other than 1.
4. AMEND2 edited a redteam proof-test fixture itself
   (tests/test_click2_redteam.py, R7 shadow host). The edit is justified
   as a fixture correction, but an implementer editing the test that
   grades it weakens independence; the re-dispatch worker must have a
   fresh reviewer re-verify that test, not the same worker.

Per-file verdicts follow. KEEP means take verbatim. PARTIAL means keep
the file and apply the listed surgical fix. REDO means rewrite; none.

## Per-file verdicts

### scripts/zen_dom.py: KEEP (569 lines changed, +522/-47)

The C12 fix is correct per the probe log (commit cd89597, verdict
WINDOW-RELATIVE): viewport_origin(window_origin, window_size,
monitor_box) now REQUIRES the Hyprland window origin, computes
absolute = window_origin + mozInner * factor, and verifies it with
check_viewport_geometry (dimension closure mozInner + inner + gap ==
outer, gaps >= 0; absolute origin inside the window rect and inside
the monitor box when given). Probe geometry is asserted in tests:
window (2509, 914) + mozInner (240, 8) = (2749, 922), and the
off-window geometry is refused. display_metrics/scale_factor record
DPR, screenPixelsPerCSSPixel, zoom with every read (R13). hit_check
refuses interactive descendants (R8). locate/field_value/verify_typed/
harvest pierce open shadow roots; focus_check walks shadowRoot
activeElement (R9, shadow part). verify_typed(selector, expected,
before) enforces the prefill rule when before == expected (R2) and
normalizes trailing whitespace for contenteditable (item E).
arm_typed_flag/typed_flag install the V11 trusted-input-event flag plus
a MutationObserver (R10, mechanism present). sent_bubble_contains is
the V12 leaf-element exact-match gate (R5/R6). harvest is the one-shot
bulk grounding (item Q). The list CLI now fails with one JSON error
object and exit 1 instead of a traceback (item D).

Caveats (do not change the verdict, fix in re-dispatch):
- R10 is only half closed: verify_typed consults the typed flag ONLY
  when before == expected (the prefill case). A JS-set value on a field
  that did NOT already hold the text still verifies. Proven below.
- R9 iframe piercing exists in locate() only; field_value() and
  verify_typed() pierce shadow roots but do not traverse same-origin
  iframes. A target inside an iframe grounds but its value read returns
  None (verify fails closed, never a wrong pass; still an incomplete R9).
- check_viewport_geometry mixes units at factor != 1: window_size comes
  from meta window_bounds (screen px) while mozInner and inner_size are
  CSS px, and the containment check compares an absolute screen origin
  against window origin + a CSS-px size. At the measured factor 1 this
  is exact and harmless; at monitor scale 2 the checks are loose and
  mis-scaled. Fix by converting window size to CSS px (divide by the
  factor) inside viewport_origin before calling the check.

### scripts/fastpath.py: PARTIAL (103 lines changed)

The corrected chain is right: dom_rect_to_screen_point takes the
ABSOLUTE origin plus a scale_factor (screenPixelsPerCSSPixel, fallback
devicePixelRatio), and dom_rect_to_image_point maps through the inverse
of cu.image_point. The 7 map-accuracy cases are relabeled MAP accuracy
with true viewport-relative inputs, and the probe geometry is case 1.

The problem is the fallback safety net added to
dom_rect_to_image_point: when the absolute reading maps outside the
observed image, it retries treating the passed origin as
window-relative (window origin from meta window_bounds, else region,
plus the passed origin times the factor). This silently rescues the
exact old-bug call: passing raw mozInner (240, 8) as the origin returns
the CORRECT point (351.7, 734.4), identical to the correct absolute
origin (2749, 922). I verified this directly (see "Passing tests" 1).
Consequences: (a) the RT R1 test passes via the net, not via the fixed
call chain, so it no longer proves the chain is fixed; (b) a wrong
origin that happens to land inside via the net is used with no warning,
so the function is no longer fail-closed for wrong-origin callers; (c)
when the absolute reading misses because the window moved (stale
observation), the net can return a point computed from a doubly-counted
origin instead of refusing. The docstring admits the residual case but
the masking is the defect. Fix: delete the fallback, restore fail-closed
raising, and rewrite the R1 RT test to go through
zen_dom.viewport_origin output (the corrected chain) instead of passing
the raw pair.

### scripts/dom_act.py: KEEP (474 lines changed, +430/-44)

ground_input re-locates after hit_check and re-grounds once on move,
refusing on a second move (R7 HCU guard as code). GroundPoints
re-validates the live rect on every [] access (R7, ground_many).
ground_many_one_shot uses the one-shot harvest when the session has it.
dom_hooks captures the before-value and arms the V11 flag before any
keystroke, and _verify passes before through (R2/R10 plumbing).
focus_type splits Enter into its own batch AFTER type_check, so a
successful send is no longer failed by its own Enter clearing the
field (R5), then verifies the send with the V12 sent-bubble gate and
records (selector, text) in a per-session intent ledger; a retry after
a failed V12 gate or a lost result returns the recorded success without
re-pressing Enter (R6). typed_text_of and open_dom_hooks are the item A
production wiring. The module docstring states the C12 conversion and
the VISION-1-as-harvest reading correctly.

Caveats: GroundPoints .get() and other dict methods bypass the live
guard (documented in the class docstring; callers must use [] access).
When the session lacks sent_bubble_contains, focus_type accepts the
Enter batch without V12 verification and records the intent anyway
(basis "dom-value+enter-accepted"); the real ZenSession exposes the
gate, so this only bites stub sessions. Both are acceptable as written.

### scripts/cu.py: PARTIAL (288 lines changed, +214/-74)

R4 is fixed in substance: a has_type batch with no passing DOM check
and no after-capture frame now reports ok False with error_code
type_unverified, in both the after_capture=False branch and the
terminal-None branch; a passing DOM check preserves the pass in the
terminal-None branch (item G). _input_line_changed now returns None
(not True) on size mismatch and uses min_pixels 4, so a 3px caret blink
or focus ring alone no longer verifies (R3b/R3c, item C).
_type_group_anchors gives one band per type group, anchored only on
click/double_click (move, hover, drag never set an anchor; item C), and
the focus gate runs before EVERY type group (item A). browser_start
refuses to cold-launch Chromium onto a port held by a non-CDP service
(Zen BiDi answering 404 on /json/version) instead of misreading the 404
as "no live endpoint" (R11). BROWSER_ENDPOINT is now 9223 (R11).
--dom-selector wires the DOM hooks into the CLI act path, and
CodeExecBackend.act wires them when a DOM session is supplied (item A).

The problem is R3a, wrong-field-on-the-same-line: the band is still
full image width, so real text landing in a DIFFERENT field on the same
line still verifies the type. Proven directly: 12 changed pixels in
another field on the anchor line returns True from
_input_line_changed. The RT test passes only because its fixture is
3 pixels, under the new min_pixels 4. The amend log's own note still
says the band is "necessary, not sufficient", yet ok True still follows
it when no DOM check is present. Fix: narrow the band to the target
field's horizontal range. desktop_act only knows the click point, so
the re-dispatch worker should pass the grounded rect into desktop_act
(a new optional parameter, supplied by dom_act/first_action) and read
the band over that rect's x-range; until then, add a real-text
wrong-field test (12+ pixels) that currently fails and must pass after
the fix.

### scripts/cdp.mjs: PARTIAL (94 lines changed)

HIT_USABLE (RT R8) is applied in click, hoverClick, and set_value; the
harvest operation is new (one evaluate plus Accessibility.getFullAXTree
plus DOM.getBoxModel cross-check, item Q); the set_value prefill early
return is removed (R2/N). BUT the removal introduced the one real
regression in this diff (see "Regression"): set_value now dispatches
synthetic input/change events even when the value was already equal.
Fix surgically (do not revert the R2 fix): capture the old value before
the native-setter write and dispatch the two events only when the value
actually changed. The setter write and the read-back verification stay
unconditional, so the R2 behavior is preserved and the snapshot
contract is restored.

### scripts/zen_cli.py: KEEP, one cosmetic fix

BidiSession takes the shared ZEN_DOM_LOCK (same path and env var as
zen_dom.ZenSession) on construction with LOCK_NB, refusing instead of
wedging the single Firefox session slot, and releases it in end()
(R12). The tab-switch protocol is documented in the coord-log addendum
(Marionette only while a ZenSession is held, BiDi only after it exits).
Cosmetic defect: `import os` appears twice (lines 92 and 96 in the
working tree). Delete one.

### scripts/first_action.py: KEEP

--dom-selector wires the DOM hooks into the fallback batch (item A),
best-effort with the reason recorded in the envelope
(dom_hooks/dom_hooks_error). No other behavior changed.

### scripts/chromium_cli.py, scripts/session_driver.py, scripts/warm_browser.py: KEEP

Each changes only the CDP default from 9222 to 9223 (R11), with the
comment stating 9222 is Zen's BiDi port. Consistent with cu.py and the
tests. Trivial and correct.

### tests/test_click2_redteam.py: PARTIAL (flag, not a code verdict)

AMEND2 changed one redteam proof-test fixture: in the R7 shadow test,
the host now carries shadowRoot with the inner input as its
activeElement. The old fixture did not model what its own docstring
described (an input focused inside its shadow root), so the change is
justified as a fixture correction, and the old strict-equality code
still fails the corrected fixture. But the implementer edited the test
that grades its own work. The re-dispatch must NOT let the same worker
grade this: a fresh reviewer re-verifies the R7 tests independently.
Also note the three weak fixtures (R1 raw pair, R3a 3px, R10 prefilled
field) that pass without closing the finding; the re-dispatch worker
rewrites those three tests to the substantive attacks (see handoff).

### tests/test_dom_act.py, tests/test_zen_dom.py, tests/test_pick4_fastpath.py: KEEP

FakeDomSession now models the window-relative mozInner pair (default
[0, 0]), the V11 flag, and the harvest; the 7 cases are relabeled MAP
accuracy with true viewport-relative inputs and the probe geometry as
case 1, with an explicit never-quote-as-live-accuracy note (item S).
V12 tests cover send-verified, failed-gate-then-retry-skips, and the
already-sent ledger. zen_dom fake dispatches on the new marker
comments and covers viewport_origin probe geometry, the
requires-window-origin refusal, off-window geometry refusal, trailing
whitespace, prefill-needs-flag, display metrics, harvest, sent bubbles,
arm/typed flag, and the clean CLI failure (item D). All pass.

### tests/test_type_verification.py, tests/test_first_action.py, tests/test_session_continuation.py, tests/test_browser_start_warm.py, tests/test_endpoint_retention.py, tests/test_fast_observe.py, tests/test_keyboard_preflight.py: KEEP

R4 contract change (ok False when unverified, type_unverified), caret/
focus-ring/hover-only after-images fail, per-group band tests (second
type stubbed fails on its own line, both landed verifies), terminal-None
DOM-pass preserved, relay-level band verification test (item F),
non-CDP 404 refuses cold launch, endpoint 9223 defaults, --dom-selector
fallback wiring with a real fake Zen session. All pass. Note two
pre-existing tests were adapted to the new R4 contract by passing a
passing type_check (test_fast_observe, test_keyboard_preflight); that is
the correct adaptation, not a weakening.

### tests/cdp_validation.mjs: KEEP

Harvest test added (one evaluate, AX tree, box model, all asserted from
production JS run in a vm page). Passes.

### improvements/worker-click-amend-log.md, improvements/worker-coord-click2-log.md: KEEP

AMEND2 appended an item-R numbering note to the amend log and a design
addendum to the coord log (item B finalized from the probe, tab-switch
protocol, HCU guard as code, exactly-once mechanized, one-shot harvest,
VISION 1 as harvest, Mantis explicitly deferred with reason, step-6
owner assigned to the parent orchestrator, items R and S). The addendum
matches the code as written, including the honest open item that the CDP
harvest runs against the agent-managed Chromium, not Brave. No personal
info, no em/en dashes.

### AMEND2's own log (untracked improvements/worker-click2-amend2-log.md): note

It contains only the start section (task receipt, fix list A-S mapping).
AMEND2 was cancelled before writing its run log, so no test numbers or
decisions are recorded there. This assessment supplies the missing
record; the re-dispatch worker should not treat the A-S list as proven
done, only as intended.

## Regression: cdp.mjs set_value breaks the snapshot contract

Full discover on the AMEND2 tree: 1850 tests, FAILED (failures=1,
errors=4, skipped=17). The 1 failure is
test_cdp_snapshot.Snapshot.test_snapshot_and_fill_contracts.

Failure text (from /tmp/click3-discover.log):
AssertionError at tests/cdp_snapshot.mjs:193:47, expected [] but got
[{trusted: false, type: 'input'}, {trusted: false, type: 'change'}].
The contract under test (tests/cdp_snapshot.mjs, comment "unchanged
text does not fire synthetic notifications"): set_value on a field
whose value already equals the text must fire zero events.

Cause: AMEND2 removed the prefill early return, so set_value now always
runs the native setter and then unconditionally dispatches InputEvent
'input' and Event 'change' (scripts/cdp.mjs, set_value branch). The
setter write is the R2 fix and must stay; the unconditional event
dispatch is the regression.

Fail-before proof: temp worktree at HEAD dd45231 (pre-AMEND2 code),
command `PYTHONPATH=../scripts:. python3 -m unittest test_cdp_snapshot -v`
run from the tests dir: Ran 2 tests, OK. Same command on the AMEND2
working tree: Ran 2 tests, FAILED (failures=1). Worktree removed after.

The 4 discover errors are pre-existing and untouched by this diff
(test_a11y_skeleton import error, test_cursor_file setUpClass g++
rejects -std=c++26, test_perf_evidence x2 FileNotFoundError
docs/benchmarks/r5_cdp_aggregate.json); the amend log recorded the same
4 on the pre-amend code. The 2 test_core umask failures the amend log
recorded do NOT reproduce in this run (environment difference, not a
code change). 17 skipped, same as before.

## Passing tests that do not prove the fix

1. R1 (conversion): test_raw_moz_inner_screen_origin_must_land passes
   the raw pair [240, 8] as the origin to dom_rect_to_image_point and
   asserts the point lands inside the image. Direct check on the AMEND2
   code: dom_rect_to_screen_point(rect, [240, 8]) = [546.0, 1140.5]
   (the old wrong map, off-monitor), but dom_rect_to_image_point with
   the same inputs returns [351.69, 734.15], identical to the correct
   absolute origin [2749, 922]. The fallback rescues the wrong call.
   The test proves the net, not the chain. The chain itself IS fixed
   (viewport_origin tests pass with the probe geometry), but this test
   must be rewritten to go through viewport_origin.
2. R3a (wrong-field band): test_band_wrong_field_same_line_must_not_verify
   and its desktop sibling use 3 changed pixels, under the new
   min_pixels 4. Direct check: 12 changed pixels in another field on
   the anchor line returns True from _input_line_changed. Real text in
   the wrong field still verifies. The finding is open in substance.
3. R10 (JS-set value): test_js_set_value_without_keystrokes_must_not_verify
   uses a prefilled field (value already 'hello'), so it passes via the
   R2 prefill rule. Direct check with the real ZenSession.verify_typed
   logic (test_zen_dom FakeWdSession): field empty before, JS sets
   'hello', no typed event, before='' returns True; before=None returns
   True. Only before='hello' (prefill) returns False. The V11 flag
   exists and is armed, but verify_typed never consults it when the
   value changed from something else. The finding is open in substance
   for the empty-field attack.

## Test results (exact commands, all on the AMEND2 working tree)

- python3 tests/test_click2_redteam.py: Ran 71 tests, OK (was 21
  failures + 1 error on the amend code; all 23 RT proof tests pass).
- python3 tests/test_dom_act.py: Ran 13 tests, OK.
- python3 tests/test_zen_dom.py: Ran 35 tests, OK.
- python3 tests/test_pick4_fastpath.py: Ran 28 tests, OK.
- python3 tests/test_type_verification.py: Ran 57 tests, OK.
- python3 tests/test_first_action.py: Ran 63 tests, OK.
- python3 tests/test_keyboard_preflight.py: Ran 32 tests, OK.
- python3 tests/test_session_continuation.py: Ran 11 tests, OK.
- python3 tests/test_fast_observe.py: Ran 40 tests, OK.
- python3 tests/test_browser_start_warm.py: Ran 11 tests, OK.
- python3 tests/test_endpoint_retention.py: Ran 7 tests, OK.
- node tests/cdp_validation.mjs: 3 ok lines (key preflight, adapter
  preflight, harvest). OK.
- Full discover, from the tests dir:
  PYTHONPATH=../scripts:. python3 -m unittest discover -p 'test_*.py':
  Ran 1850 tests in 200.295s, FAILED (failures=1, errors=4, skipped=17).
  The 1 failure is the cdp_snapshot regression above; the 4 errors are
  the pre-existing set.
- Syntax: python3 -m py_compile on each changed .py (11 files) OK;
  node --check scripts/cdp.mjs OK. git diff --check clean. 0 em/en
  dashes in the whole diff. No ydotool anywhere in the diff (only
  mentions of the ban in existing comments).

## RT finding status (R1-R13)

- R1 conversion: FIXED at the zen_dom level (viewport_origin + geometry
  check + probe-geometry tests). PARTIAL at the fastpath level (the
  fallback masks wrong-origin calls; RT test passes via the net).
- R2 prefill: FIXED (before-value rule in verify_typed + dom_hooks).
- R3 band: PARTIAL. R3b/R3c fixed (min_pixels 4, size mismatch None).
  R3a open in substance (full-width band still verifies real text in
  another field on the same line).
- R4 unverified ok: FIXED (ok False, type_unverified, both branches).
- R5 verify-after-Enter: FIXED (type_check before Enter, Enter as its
  own batch, V12 bubble gate after).
- R6 double-send: FIXED (per-session intent ledger + pre-send V12
  bubble read).
- R7 stale DOM: FIXED (re-locate + re-ground in ground_input,
  GroundPoints live re-validation on [] access).
- R8 interactive child: FIXED (zen_dom hit_check and cdp.mjs HIT_USABLE).
- R9 shadow/iframe: MOSTLY FIXED. Shadow walk and piercing in place;
  iframe traversal exists in locate() only, not in field_value() or
  verify_typed().
- R10 JS-set value: PARTIAL. V11 flag + MutationObserver armed; flag
  consulted only in the prefill case. Empty-field JS-set still verifies.
- R11 CDP endpoint: FIXED (9223 default everywhere, 404 refusal,
  set_value prefill early return removed, subject to the regression fix).
- R12 session-slot lock: FIXED (zen_cli takes ZEN_DOM_LOCK).
- R13 DPR/zoom: FIXED (metrics recorded, factor applied in the chain).

Items A-S from the AMEND2 brief: A, B, C, D, E, F, G, H, I, J, K, N, O,
P, Q, R, S are implemented as described (Q's Mantis deferral and step-6
owner are documented decisions, not code). L is partial (iframe value
reads), M is partial (flag not consulted on value change). The AMEND2
log's A-S list is an intent list only; this assessment is the evidence.

## Handoff for the re-dispatch worker (in order, do not re-do the rest)

1. Fix the cdp_snapshot regression FIRST (scripts/cdp.mjs set_value):
   capture the old value before the native-setter write; dispatch the
   synthetic input/change events only when the value actually changed.
   Keep the setter write and the read-back verification unconditional
   (the R2 fix stays). Then run `python3 -m unittest test_cdp_snapshot`
   from the tests dir: must be 2/2 OK. Then re-run the full discover:
   must be 0 failures (only the 4 pre-existing errors + 17 skipped).
2. Delete the fastpath fallback in dom_rect_to_image_point (restore
   fail-closed raising). Rewrite test_raw_moz_inner_screen_origin_must_land
   to go through zen_dom.viewport_origin output (absolute origin
   [2749, 922] on the probe geometry) instead of passing the raw pair.
   The corrected chain is already proven by the test_zen_dom probe
   geometry tests; this step removes the mask, not the fix.
3. Close R3a in substance: pass the grounded rect into desktop_act (new
   optional parameter, supplied by dom_act/first_action) and read the
   input-line band over that rect's x-range instead of the full image
   width. Add a failing-first test with 12+ changed pixels in another
   field on the same line; it must fail before the fix and pass after.
   Keep min_pixels 4 and the per-group anchors.
4. Close R10 in substance: in ZenSession.verify_typed, consult the
   typed flag whenever before is given and the value changed (before !=
   expected), not only when before == expected. A value that appears
   with no trusted input event must fail. Add a failing-first test:
   empty field, JS sets the expected text, no keystrokes, before=''
   must NOT verify. Keep the prefill case as is. Note: this changes the
   verify_typed contract for callers that set values programmatically;
   dom_act's type_check is a typed-input check, so requiring the flag
   there is correct; cdp.mjs set_value is the programmatic path and is
   unaffected.
5. Fix the check_viewport_geometry unit mixing: convert window_size to
   CSS px (divide by the factor) inside viewport_origin before the
   check, so the closure and containment hold at scale factors other
   than 1. Add a factor-2 geometry test.
6. Extend locate's iframe traversal to field_value() and verify_typed()
   (same-origin frames), or document loudly that iframe targets verify
   fail-closed. Small.
7. Delete the duplicate `import os` in scripts/zen_cli.py (lines 92/96).
8. Independent re-verification: a FRESH reviewer (not the re-dispatch
   worker) re-runs the R7 shadow tests and confirms the corrected
   fixture models a focused input inside a shadow root and that the old
   strict-equality code fails it. The re-dispatch worker must not grade
   its own fixture edit.
9. Re-run the full affected set (the 11 suites above + cdp_validation.mjs
   + full discover) and record the exact commands and counts in the
   re-dispatch log. Do not claim the R1/R3a/R10 findings closed until
   the new failing-first tests in steps 2-4 pass.

## What to keep verbatim (do not touch)

Everything else: zen_dom.py viewport_origin/geometry/harvest/V12,
dom_act.py ground/HCU/ledger/Enter split, cu.py R4/per-group bands/404
refusal/--dom-selector, zen_cli.py lock, first_action.py wiring, the
9223 defaults, the MAP-accuracy relabeling, the V12 and per-group band
tests, the coord-log design addendum. The re-dispatch is surgical
(steps 1-8 above), not a rewrite of AMEND2.

## Commit record

Report file: improvements/worker-click3-diff-assess.md (this file).
Staged and committed with an explicit pathspec; push verified with
git ls-remote (see the coordinator's copy of this log for the hash;
this worker's final report to the coordinator carries it).
