# Redteam CLICK2-RT log

Branch: todolist-push. Task: break the amend diff e4082ff..4b7d6ac and the
combined design in improvements/worker-coord-click2-log.md, with proof.
Work on the VM only (code + tests). No live laptop driving, no browser
tasks, never ydotool. No em dash (U+2014) or en dash (U+2013) anywhere.
All times wall-clock Asia/Ho_Chi_Minh, elapsed from task start 02:50 +07.

## 02:50 +07 (t+0m) Start

Read first: coord-click2 log (synthesis + combined design + open items),
click-amend log (12/12 items, 315 tests), click-crawl-verify log (V1-V20
+ redteam notes), clone2 bench docs/clone2-dom-grounding-20261122.md on
origin/main. Diff under attack: e4082ff..4b7d6ac, code files scripts/cu.py,
scripts/dom_act.py, scripts/fastpath.py, scripts/first_action.py,
scripts/zen_dom.py. Did NOT read any council member logs (C1/C2/C3);
verdict below is independent.

## 02:52 +07 (t+2m) First pass over the diff

What the amend does, in one paragraph: cu.desktop_act gains an input
line band check (_input_line_changed, full image width, anchor y +-12px)
plus optional focus_check/type_check hooks; zen_dom gains viewport_origin
(mozInnerScreenX/Y), hit_check (elementFromPoint), focus_check
(activeElement strict equality), field_value (textContent or value),
verify_typed (equality only); fastpath gains dom_rect_to_image_point
(screen = origin + rect center, then inverse of cu.image_point);
dom_act grounds from the live DOM, clicks + types + Enters in one batch,
verifies via the hooks. first_action widens the G28 refusal to every
batch and copies type_verified/error_code into the envelope.

What jumped out before any test was written (all confirmed by tests
below, not just asserted here):

1. Conversion: zen_dom.viewport_origin returns mozInnerScreenX/Y and
   calls it "viewport origin in screen coordinates", with NO window
   origin term anywhere in dom_act, fastpath, or zen_dom. The repo's own
   live calibration (docs/calibration-e2-report.md, measured on the
   laptop Zen 21/11) says mozInnerScreenX/Y in this Zen build are
   WINDOW-relative (240, 8), not absolute screen coords, and the truth
   table is window-relative CSS px with the window origin (2509, 914)
   added for screen px. The amend's own tests fake the origin as
   [2533, 914] (tests/test_zen_dom.py dom_origin, tests/test_dom_act.py
   origin default), which equals neither the measured (240, 8) nor the
   true screen origin (2749, 922). The "7/7 grounding accuracy, 100%"
   bar number is measured against a fake that contradicts the repo's own
   live measurement.
2. verify_typed is equality only: no before-value, no change required.
   A pre-filled input passes with zero keystrokes. cdp.mjs set_value
   has the same hole as an early return (ok:true when value already
   equals text).
3. The band is full-width: text in ANY field on the same line passes,
   a 3px caret blink passes, a resize passes (size mismatch returns
   True outright). Without a type_check hook the batch still reports
   ok True on all three.
4. ok True with type_verified None: after_capture=False and the
   terminal-address-None path both return ok True with no verification
   at all. The existing tests assert this as intended behavior.
5. Ordering: type_check runs AFTER the whole batch including Enter, so
   a sent message (input cleared by the send) FAILS verify_typed. The
   amend's own FakeAct never models Enter clearing the field, so its
   enter=True happy-path test passes vacuously. A successful send
   reports type_unverified, and the prescribed retry re-sends: the
   double-send is driven by the false failure, not just by a lost
   result. No V12 sent-bubble check exists anywhere in dom_act.
6. Stale DOM: ground_input reads locate, origin, hit_check as three
   separate evaluates; hit_check re-reads its own rect, so the hit
   verdict and the clicked point come from different snapshots. Nothing
   re-resolves between ground and click, and ground_many points are
   never re-validated before use. The HCU live guard in the combined
   design (step 3) is design text only; no code implements it.
7. hit_check passes any descendant (e.contains(hit)), including an
   interactive child button sitting at the rect center.
8. Shadow DOM / iframe: locate, focus_check, field_value all use
   document.querySelector only; focus_check is strict activeElement===e
   with no shadowRoot walk (V3 explicitly requires the walk).
9. No MutationObserver anywhere (V11 unimplemented): a JS-set value
   passes verify_typed with zero keystrokes.
10. CDP default: cu.BROWSER_ENDPOINT is http://127.0.0.1:9222, which
    is Zen's BiDi port; cdp.mjs fetches /json/list from it (404 on
    Firefox 141+, clone2 proved) and browser_start probes /json/version
    there, treating live Zen as dead.
11. Session slot: zen_cli.py (BiDi) takes no ZEN_DOM_LOCK, so nothing
    stops a BiDi session opening while a ZenSession (Marionette) holds
    the one Firefox session slot. The combined design never names which
    tool switches tabs between clone1 and clone2.
12. No DPR/zoom term anywhere, and no DPR/zoom recorded with any
    snapshot. MDN: mozInnerScreenX/Y are CSS px, affected by zoom;
    physical px need screenPixelsPerCSSPixel. At the single measured
    config (DPR 1, scale 1, zoom 100%) the factor is 1 and invisible.

## 03:05 +07 (t+15m) Proof tests written

tests/test_click2_redteam.py: 16 tests, each asserting the REQUIRED
behavior, so each fails (or errors) on the current code. That is the
point: a failing test here is the finding, with the command and output
below. A few fix-direction tests pass to show the arithmetic of the fix.
Run: python3 tests/test_click2_redteam.py

## 03:12 +07 (t+22m) Test run (proof)

Command: python3 tests/test_click2_redteam.py
Result: Ran 71 tests in about 1s, FAILED (failures=21, errors=1).
Of the 71, 49 are inherited harness tests from DesktopPreflight, all
passing (the harness is intact). Of my 23 redteam tests, 22 fail or
error exactly as designed (each asserts required behavior), and 1
passes: test_window_origin_added_lands, the fix-direction arithmetic
for R1. Neighbor suites still pass with only a test file added:
test_type_verification OK, test_dom_act OK, test_zen_dom OK,
test_pick4_fastpath OK.

Headline outputs (full text in the test run above):

- R1: ValueError: DOM rect center maps outside the observed image:
  screen (546.0, 1140.5) maps to image (-1264.4, 145.8) of 1200x757.
  That is mozInnerScreen (240, 8) + rect center, on the calibration
  window (2509, 914, 1863x1176). The corrected origin (2749, 922)
  lands at (351.7, 734.4), inside the image.
- R3 desktop: wrong-field pixels on the anchor line verified the type:
  ok True, type_verified True, basis input-line-band.
- R4: after_capture=False type batch: ok True, type_verified None,
  type_verification "skipped: after_capture is False, no fresh frame
  to compare".
- R5: sent message failed verification: ok False, completed 3,
  type_verified False, error_code type_unverified, after the message
  provably sent (sent == ['hello']).
- R6: retry sent the message twice: ['hello', 'hello'].
- R8 node run of the REAL hit_check JS: True with a BUTTON at the
  rect center.
- R9 node run of the REAL focus_check JS: False for a focused input
  inside a shadow root (activeElement is the host).

One test-authoring note, recorded because it is a trap for the next
worker: test_keyboard_preflight loads cu via importlib spec (its own
module object) and patches THAT object. A plain `import cu` in the
redteam file loaded a second copy, whose real focus() raised on the
fixture address. Fixed by importing cu from test_keyboard_preflight,
the same way test_type_verification does.

## Findings

BLOCK means the amend must not land until fixed. AMEND means fix
before the 2-vision benchmark relies on it. Every finding has the
exact attack, the file:line, the observed behavior, and the fix.

R1 (BLOCK) Conversion drops the window origin.
Attack: ground a field with the measured laptop Zen geometry
(calibration-e2-report.md: window at (2509, 914), mozInnerScreenX/Y
window-relative (240, 8), observation 1200x757 over region
(2509, 914, 1863, 1176)).
File:line: scripts/zen_dom.py:367-383 viewport_origin (returns
mozInnerScreenX/Y as "screen coordinates"), scripts/fastpath.py:152-167
dom_rect_to_screen_point (origin + center, no window term), no window
origin read anywhere in dom_act, fastpath, or zen_dom.
Observed: test_raw_moz_inner_screen_origin_must_land errors with
ValueError, screen (546.0, 1140.5) maps to image (-1264.4, 145.8).
On the measured geometry ground_input always raises DomActError
instead of clicking. The amend's tests hide this by faking the origin
as [2533, 914] (tests/test_zen_dom.py dom_origin, tests/test_dom_act.py
origin default), which equals neither the measured (240, 8) nor the
true screen origin (2749, 922). Two repo sources also disagree with
each other (calibration_e2.py:17 says truth screen = mozInnerScreen +
rect center; the calibration report note says mozInnerScreen is
window-relative and the window origin must be added); the amend picked
one side without resolving the contradiction. MDN (accessed 2026-11-22)
says mozInnerScreenX/Y are CSS px, affected by zoom, and physical px
need screenPixelsPerCSSPixel, which feeds R13.
Fix: resolve empirically on the laptop (read mozInnerScreenX/Y plus
hyprctl window origin plus a known rect, click-test which hypothesis
lands), then make viewport_origin return window origin + mozInnerScreen
(or the verified screen value) and record the hypothesis with the
snapshot. Correct the fakes to the measured values.

R2 (BLOCK) Prefill false-ok: verify_typed is equality only.
Attack: pre-fill the input with the expected text, stub the type step
(zero keystrokes), run focus_type.
File:line: scripts/zen_dom.py:444-451 verify_typed (field_value ==
expected, no before-value, no change required), scripts/dom_act.py:105-108
type_check closure.
Observed: test_prefilled_input_stubbed_type_must_not_verify FAILS:
result ok True, type_verified True, typed [].
Fix: capture the before-value at ground time; require before !=
expected and after == expected (V17 expectation-first). Same fix in
cdp.mjs set_value, which returns {ok:true} when value already equals
text (see R11).

R3 (BLOCK) Input-line band false-passes three ways, and ok still
follows it.
Attack: (a) text in a different field on the same horizontal line;
(b) a 3px caret blink / focus ring with zero text; (c) a frame resize
between pre-batch and after-capture.
File:line: scripts/cu.py:1018-1045 _input_line_changed (full-width band,
anchor y +-12px; size mismatch returns True outright),
scripts/cu.py:2053-2080 (band True sets type_verified True and ok stays
True).
Observed: test_band_wrong_field_same_line_must_not_verify,
test_band_caret_blink_only_must_not_verify, test_band_resize_must_not_verify
all FAIL (function returns True); the desktop-level tests FAIL with
ok True, type_verified True, basis input-line-band, on wrong-field
pixels and on caret-only pixels. The note text in the result itself
says the band is "necessary, not sufficient", yet ok True follows it.
Fix: the band must never be the sole basis for ok. Without a DOM value
check, a has_type batch reports type_verified False (or ok False), not
ok True. Narrow the band to the target rect (not full width), and make
size mismatch return None (unverifiable), not True.

R4 (BLOCK) ok True with type_verified None.
Attack: type with after_capture=False and no type_check; and type with
expected_terminal_window='none'.
File:line: scripts/cu.py:1958-1975 (after_capture=False branch sets
ok True, type_verified None), scripts/cu.py:1998-2007 (terminal None
path sets after_skipped, type_verified None, ok stays True).
Observed: both tests FAIL with ok True and type_verified None. The
existing test test_type_batch_after_capture_false_skips_verification
asserts ok True, so the hole is baked into the suite as intended.
Fix: a has_type batch with no verification at all must not report ok;
set ok False (or outcome_uncertain True with ok False) and keep
type_verified None as the reason. Update the existing test to the new
contract.

R5 (BLOCK) Verify-after-Enter ordering: a successful send fails.
Attack: type, then Enter in the same batch, with type_check reading the
field after the batch. A real send clears the input.
File:line: scripts/cu.py:1914-1920 (type_check runs after execution,
after Enter already dispatched), scripts/dom_act.py:86-95 (Enter
appended to the same batch as type, type_check after).
Observed: test_successful_send_must_not_fail_verification FAILS:
sent == ['hello'] (the message did send) but result ok False,
type_verified False, error_code type_unverified. The amend's own
FakeAct never models Enter clearing the field, so its enter=True
happy-path test passes vacuously.
Fix: verify the typed text BEFORE Enter (field holds expected text,
caret at end), then Enter, then verify the SEND by the sent bubble
(V12, thread DOM), never by re-reading the cleared field.

R6 (BLOCK) Double-send: no exactly-once mechanism.
Attack: retry focus_type after a partial send (first attempt executed,
result lost; or R5 false-failed after a real send).
File:line: scripts/dom_act.py:78-129 focus_type (no sent-bubble
pre-check, no dedup token, no before-send state read; V12 exists
nowhere in dom_act).
Observed: test_retry_after_partial_send_must_not_double_send FAILS:
sent == ['hello', 'hello'] after two identical calls.
Fix: before sending, read the thread DOM for the exact text bubble
(V12); send only if absent. Order the flow as R5 requires (verify
text, then Enter, then verify bubble), and make retry check the bubble
first.

R7 (AMEND) Stale DOM: hit and point come from different snapshots;
no live guard exists.
Attack: (a) element moves between locate and hit_check; (b) ground_many
grounds both clone inputs, then the first send shifts the layout.
File:line: scripts/dom_act.py:38-62 ground_input (three separate
evaluates; hit_check re-reads its own rect), scripts/dom_act.py:64-76
ground_many (points stored, never re-validated), scripts/zen_dom.py:405-421
hit_check (re-reads rect internally).
Observed: test_hit_passes_but_point_is_stale FAILS: ground point
(306.0, 1132.5) is outside the live rect (y 800..863) while hit passed.
test_ground_many_points_go_stale_across_sends FAILS: stored clone2
point (306.0, 1031.5) is outside the live rect (y 700..763). The
combined design's step-3 HCU live guard (re-check live geometry before
input) is design text only; grep finds no re-check in dom_act or cu.py.
Fix: re-resolve the rect immediately before each click and require the
stored point to still hit the live rect (V6); re-ground each input at
its own send time, never click a ground_many point from before the
previous send. Implement the guard, do not just document it.

R8 (AMEND) hit_check passes any descendant, including an interactive
child at the rect center.
Attack: the rect center is occupied by a child BUTTON (clear-text /
emoji / send affordance inside the composer). elementFromPoint returns
the child.
File:line: scripts/zen_dom.py:405-421 hit_check
(`e===hit||e.contains(hit)`), same clause in scripts/cdp.mjs set_value.
Observed: node execution of the REAL hit_check JS (extracted from
zen_dom.py, shimmed DOM) returns True with a BUTTON at the center.
The click would activate the child instead of focusing the field. The
task's border variant is the same clause: a hit on a border child node
passes identically.
Fix: require e===hit, or allow descendants only when the descendant is
not itself interactive (not BUTTON, A, INPUT, or [role=button]) and
document which case each selector relies on.

R9 (AMEND) Shadow DOM and iframe inputs are unreachable, and shadow
focus false-negatives.
Attack: (a) target inside a shadow root or an iframe; (b) input inside
a shadow root IS focused, but document.activeElement is the host.
File:line: scripts/zen_dom.py:347-361 locate, 423-434 focus_check
(strict activeElement===e, no shadowRoot walk), 436-442 field_value,
all document.querySelector only.
Observed: test_focus_check_walks_shadow_roots and
test_locate_pierces_shadow_roots_or_frames FAIL (no 'shadowRoot',
'contentWindow', or 'frames' in the code); node execution of the REAL
focus_check JS returns False for a focused shadow input. V3 explicitly
requires the shadow walk; the amend does not implement it.
Fix: walk shadowRoot.activeElement down (the Chromium pattern in the
crawl log), pierce open shadow roots in locate/field_value, and traverse
same-origin frames; for cross-origin iframes refuse loudly naming the
target class instead of silently dropping it from the "every input"
harvest.

R10 (AMEND) Synthetic JS-set value passes verification; V11 is
unimplemented.
Attack: a page script sets el.value (or textContent) to the expected
text and dispatches synthetic input events; zero keystrokes.
File:line: scripts/zen_dom.py:444-451 verify_typed; grep finds no
'MutationObserver' in cu.py, dom_act.py, or zen_dom.py.
Observed: test_js_set_value_without_keystrokes_must_not_verify FAILS on
both the source assertion (no MutationObserver) and the behavior
(ok True, typed []). The verification channel (Marionette evaluate)
is the same channel the page's own JS writes through, so the check
cannot distinguish typed text from JS-set text.
Fix: arm a MutationObserver / input-event flag on the target BEFORE
typing (V11), require the flag plus the value plus the caret offset
(V4), and record before-value (R2). A value that appears with no input
events and no keystrokes must fail.

R11 (AMEND) CDP default endpoint is Zen's BiDi port; Chromium path
has the same prefill hole.
Attack: call the CDP browser path with the default endpoint against the
live Zen; and set_value a field that already holds the text.
File:line: scripts/cu.py:35 BROWSER_ENDPOINT =
'http://127.0.0.1:9222' (Zen's --remote-debugging-port, BiDi only since
Firefox 141); scripts/cdp.mjs:119-128 (fetches /json/list from the
endpoint; /json returns 404 on Firefox 141+, clone2 proved);
scripts/cu.py:2121 (browser_start probes /json/version there and reads
the 404 as "no live endpoint", then cold-launches Chromium onto the
port Zen already holds); scripts/cdp.mjs set_value early return
`if(e.value===...)return {ok:true}`.
Observed: test_default_cdp_endpoint_is_not_zen_bidi_port and
test_cdp_set_value_prefill_early_return FAIL. Note the combined design
TEXT routes CDP to Brave/Chrome only (correct); the assumption lives
in the code defaults, not in the design text.
Fix: default the CDP endpoint to the Chromium/Brave port, never 9222;
probe BiDi (session.new) when the target is Zen; remove the set_value
early return or require a real set (R2 fix).

R12 (AMEND) Session-slot wedge: the BiDi client takes no lock.
Attack: hold a ZenSession (Marionette) and open a zen_cli BiDi session
on the same Zen instance, e.g. to switch tabs between clone1 and clone2.
File:line: scripts/zen_dom.py:109-141 (file lock ZEN_DOM_LOCK, one
WebDriver session, always deleted); scripts/zen_cli.py:456-458
(session.new, no flock, no ZEN_DOM_LOCK anywhere in the file).
Observed: test_bidi_client_takes_the_single_session_lock FAILS
(no lock in zen_cli.py). Clone2 measured the Firefox cap on all runs:
"Maximum number of active sessions". The combined design never names
which tool switches tabs, so the wedge is one natural choice away.
Fix: make zen_cli take the same ZEN_DOM_LOCK (or share one session
manager), and name the tab-switch protocol in the benchmark runbook:
Marionette only while a ZenSession is held; BiDi only after it exits.

R13 (AMEND) No DPR or zoom term, and none recorded.
Attack: run the same conversion at monitor scale 2 or page zoom 125%.
File:line: scripts/fastpath.py:152-167 dom_rect_to_screen_point,
scripts/zen_dom.py:367-383 viewport_origin; grep finds no
'devicePixelRatio' or 'screenPixelsPerCSSPixel' in fastpath.py,
zen_dom.py, or dom_act.py, and no snapshot records DPR or zoom.
Observed: test_no_dpr_or_zoom_term_recorded FAILS. Arithmetic: at
scale 2 a rect center 306 CSS px from the viewport origin is 612
screen px away; the code maps 306 and lands about 306 screen px off.
At the single measured config (DPR 1, scale 1, zoom 100%) the factor
is 1 and invisible, which is why the "proven chain" looks proven.
Fix: read window.devicePixelRatio (and visualViewport scale / fullZoom)
with every snapshot, apply screenPixelsPerCSSPixel in the conversion,
and refuse or re-ground when the recorded factor changes.

## V16 verification-independence table

For each check, the channel and whether the step under test can set the
check signal itself. Any check the action can set is not verification.

- Band / frame hash (cu.py): pixels. Set by the click (caret, focus
  ring), by any animation, by resize. NOT independent. The result note
  admits it; ok still follows it.
- focus_check (zen_dom activeElement): DOM state over the same
  Marionette channel as grounding. Set by any JS el.focus() and by any
  click that focuses anything; reads in-page focus only, not OS focus
  (document.hasFocus is never checked), so keys can go to another
  window while the check passes.
- verify_typed (zen_dom field value): DOM state over the same
  Marionette channel. Set by page JS, autofill, React controlled
  inputs, and prefill (R2, R10). Independent of wtype's return code
  only; not independent of the page.
- hit_check (zen_dom elementFromPoint): DOM state over the same
  channel. Defeated by any layout change after the check (R7); passes
  descendants (R8).
- type_check closure (cu.py _run_check): caller-supplied. desktop_act
  trusts any truthy return; a stub lambda True passes and the result
  still says basis dom-value. The check is only as strong as the
  closure; dom_act supplies the real one, plain desktop_act callers
  are on their honor.
- Sent bubble (V12): not implemented anywhere in dom_act. This is the
  one check the type step cannot set (only Enter plus the app can), and
  it is the missing one.
- Grounding itself (locate + origin): same Marionette evaluate channel
  as every check above. A lying or stale DOM defeats grounding and all
  checks together; there is no cross-check against AT-SPI extents (C12
  cross-check unbuilt) and no second protocol corroboration.

## Checked and cleared (not findings)

- Rotation about the element center is NOT a break: for a symmetric
  rect the bbox center is the transformed center, so a rotated input's
  rect center stays on the element. The transform risk is clip-path
  and child occlusion, not rotation.
- clip-path: fails closed via hit_check (center clipped away returns
  another element, hit False, ground refuses). No wrong click.
- focus_check raising fails closed (test_focus_check_exception_fails_closed
  in the amend suite); the _FocusUnverified path stops before typing.
- first_action G28 widening (e10fef4, 90b7026): verified in the diff,
  refusal now covers every batch, and the pointer-only remedy is
  correctly gated on has_keyboard. The flip is sound.
- cdp.mjs fill (unlike set_value) does check focus after the click and
  value after insertText; its hole is the shared textContent read and
  the missing before-value, not a stub pass.
- No em/en dash in any file written here (grep clean). No ydotool.

## What was NOT tested live (owed, not claimed)

No browser binary exists on this VM (no firefox, no chromium), so no
live DOM run was possible; the node-shim runs execute the production
JS strings with a shimmed DOM, which proves the JS logic, not the live
page. Live confirmation is owed on the laptop for: R1 (which
mozInnerScreen semantics the real Zen has, and the click-test of both
hypotheses), R8 (whether the real Messenger composer center hits a
child control), R9 (shadow/iframe structure of the real target DOM),
and the 2-vision benchmark as a whole. The combined design's step-3
guard, step-1 bulk harvest, and V12 finish gate are design text only
and were reviewed as text, not as code, because the code does not
contain them.

## Verdict: BLOCK

Do not land e4082ff..4b7d6ac. The DOM-first direction is right and the
G28 widening is sound, but the Zen conversion as implemented cannot
produce a correct click on the repo's own measured laptop geometry
(R1 raises instead of clicking), a successful send fails verification
and its retry double-sends (R5, R6), and the two main verifications
false-pass on prefill and on band changes the type step never made
(R2, R3, R4). Fix R1, R2, R3, R4, R5, R6 first, then R7-R13, then
re-run tests/test_click2_redteam.py: all 23 must pass (the 1 currently
passing fix-direction test plus the 22 now failing), with the laptop
live run confirming R1 before any benchmark claim.

## 03:14 +07 (t+24m) Committed and pushed

Commit 175d3ef (explicit pathspec: tests/test_click2_redteam.py,
improvements/worker-click2-rt-log.md only). Pushed todolist-push,
ls-remote confirms origin at 175d3ef2720ebc530e6d7e7e6186674521333f2b.
No other files touched; the untracked files from other workers
(multi-agent-deliberation, muse-coordinate-accuracy,
worker-click-baseline2-log, worker-y14b-fix6-redteam) were left alone.
Verdict: BLOCK. 13 findings (R1-R6 blockers, R7-R13 amend-level),
23 proof tests, 22 fail or error on current code, 1 fix-direction
test passes, 49 inherited harness tests pass, neighbor suites
(test_type_verification, test_dom_act, test_zen_dom,
test_pick4_fastpath) all OK.
