# Worker CLICK2-C2 log (Council Member 2, independent review of the amend diff + combined design)

Branch: todolist-push. Task start 2026-11-22 02:50 +07 (t+0m). VM only (code + tests).
No live laptop driving, no browser tasks, never ydotool. No em dash (U+2014) or
en dash (U+2013) anywhere in any file written by this worker. All times
wall-clock Asia/Ho_Chi_Minh + elapsed from task start. I did NOT read the
other round-2 council/redteam logs (worker-click2-c1/c3/rt-review-log.md);
this verdict is independent. First-round C1/RT logs were read only to
reconstruct the 12-item spec the amend implements.

## 2026-11-22 02:50 +07 (t+0m) Start, spec reconstruction

The 12 consolidated items: C1 items 1-3 (1: test_session_continuation
regression repair; 2: widen G28 refusal to pointer-only batches; 3:
type_verified None on the terminal-None after-skip path) + RT R1-R9
(R1 type-verification false-pass; R2 pointer-only substitution; R3 envelope
drops type_verified/error_code; R4 refusal remedy cannot type; R5 zen_dom
malformed responses escape raw; R6 failed tab restore swallowed; R7 full
scan burns one timeout per handle on a wedged session; R8 tab_at handle-order
claim unverified; R9 docstring overclaims G28 refusal). Item 12 in the
original list (verify caret by fresh observe before typing) was REPLACED by
the owner corrections (02:00/02:02): DOM-first grounding + cheap
verification, no slow observe cycles, bar numbers (observes per task,
actions per observation, accuracy >= 90%).

Repo HEAD at start: 88f93f3 (coord2 synthesis). Amend tip: 4b7d6ac.
Diff scope e4082ff..4b7d6ac, code only: 12 files, +1632/-116
(scripts/cu.py, dom_act.py, fastpath.py, first_action.py, zen_dom.py;
tests test_dom_act, test_first_action, test_keyboard_preflight,
test_pick4_fastpath, test_session_continuation, test_type_verification,
test_zen_dom). The full-range diff stat also sweeps in unrelated log/doc
files from other workers on the shared branch; the amend code diff is the
12 files above.

## 2026-11-22 02:52 +07 (t+2m) Diff read, cu.py + first_action.py + fastpath.py

- cu.py: _input_line_changed (band, full width, anchor y +/- 12px,
  threshold 50, min 3 px/channel), _load_after_image, _run_check,
  _FocusUnverified, focus_check/type_check hooks in desktop_act,
  type_anchor/focus_click tracking, band-or-DOM verification block,
  terminal-None path sets type_verified None. JPEG max error 39 is
  sourced in-repo (cu.py:858-859, measured q90 4:4:4 vs 80 at 4:2:0),
  so threshold 50 sits above encoding noise on a real measurement.
- first_action.py: run() now refuses EVERY batch on a rejected given
  observation (was key/type only); loud_substitution_refusal splits the
  remedy by has_keyboard (screen-coordinates remedy only for
  pointer-only); envelope gains type_verified + error_code on both
  paths (session + fallback).
- fastpath.py: dom_rect_to_image_point via calibration_e2 chain
  (screen = viewport origin + rect center; image = inverse of
  image_point), fail-closed outside the image; point_in_rect hit test.

## 2026-11-22 02:55 +07 (t+5m) Diff read, zen_dom.py + dom_act.py + test diffs

- zen_dom.py: _wd converts JSON decode failures, http.client.HTTPException,
  and responses without a "value" member (R5); _try_restore/_verify_selected
  surface failed restores (R6); full scan stops after the first transport
  failure (R7, wedge); tab_at docstring downgraded to handle-list index
  (creation order, not visual tab order) and the switch is verified (R8);
  range check now precedes current_handle() (R10 minor fixed as a side
  effect). New DOM helpers: viewport_origin (mozInnerScreenX/Y),
  locate_point, hit_check (elementFromPoint), focus_check
  (document.activeElement), field_value, verify_typed (exact equality).
- dom_act.py (new, 129 lines): ground_input / ground_many / focus_type.
  Grounding is locate + viewport_origin + hit_check (3 DOM calls), then
  one desktop_act batch (click + type + Enter) with focus_check and
  type_check closures wired. No production caller exists yet (see F1).
- Test diffs: test_type_verification gains the R1 demo test, band pass
  test, focus gate tests, DOM check tests, no-extra-observes test;
  test_first_action gains the refusal flip (pointer-only refused), R4
  remedy split, R3 envelope tests; test_session_continuation changes
  only the mock post hash to '1111'; test_keyboard_preflight harness
  gains after_image (text pixels on the anchor line).

## 2026-11-22 02:53 +07 (t+3m) Independent test re-runs (amend code, HEAD 88f93f3)

- 7 named suites (test_first_action, test_type_verification,
  test_zen_dom, test_dom_act, test_pick4_fastpath,
  test_session_continuation, test_keyboard_preflight): 213 tests OK
  in 2.829s.
- Full 13-suite set (the 7 above + test_fast_observe,
  test_act_diagnostics, test_guard_boundaries, test_pointer_safety,
  test_focus, test_observation_contract): 315 tests OK in 4.613s.
  Matches the amend log claim (315 tests, about 5.2s).

## 2026-11-22 02:56 +07 (t+6m) Fail-before, own worktree at e4082ff

Worktree /tmp/c2-failbefore at e4082ff, new test files + scripts/dom_act.py
+ native/wtype copied in (removed afterwards with git worktree remove):
- test_type_verification: FAILED, failures=1, errors=7. Matches amend log.
- test_dom_act: FAILED, errors=9 of 10. Matches amend log.
- test_pick4_fastpath: FAILED, errors=5. Matches amend log.
- test_first_action: FAILED, failures=3, errors=2. Matches amend log.
- test_zen_dom: FAILED, failures=6, errors=9. Matches amend log.
On the amend code all five suites pass. Fail-before is independently
reproduced, not trusted from the log.

## 2026-11-22 02:57 +07 (t+7m) R1 probe: can a click-only frame change still false-pass?

Probed the real cu._input_line_changed on 901x1176 white frames
(the G30 geometry), anchor y = click y, band +/- 12px:
- P1 caret-only on the anchor line (correct click at (300,1132), black
  1px caret column, zero text delivered): True. FALSE PASS.
- P2 focus-ring line on the anchor line: True. FALSE PASS.
- P3 missed click at y=1037, no pixel change on that line: False.
  The band correctly fails the incident shape ONLY when the missed
  click is pixel-silent on its line (assumed, never measured live).
- P4 missed click + light-grey (220) full-width line on the anchor:
  False (diff 35 < threshold 50). A darker ring would pass.
- P5 unrelated pixels on the anchor line (incoming message bubble):
  True. FALSE PASS.
- P6 text lands in the field at y=1132 but the anchor is the missed
  click y=1037: False. FALSE FAIL direction (band is anchored to the
  click, not the field).
- P7 hover-state change on the anchor line (type_anchor tracks
  move/hover): True. FALSE PASS.
Conclusion: the band narrows the e4082ff whole-frame check to one line,
but it does NOT close the false pass. The click's own visual feedback
(caret, focus ring) sits on the anchor line by construction, so the
correct-click-but-no-text shape still verifies. The amend log and code
comments admit the band is "necessary, not sufficient" and name the DOM
value check as the sufficient check, but no live caller wires it:
grep over scripts/ shows first_action.py:581, cu.py:2470 and cu.py:2759
all call desktop_act without focus_check/type_check, and dom_act.py
has no production caller (only tests). The sufficient check exists as
an opt-in library, not on any live path. The R1 demo test
(test_click_type_frame_changed_by_click_only_fails) sets after_image
to the pixel-identical pre-batch image, so it proves the band ignores
a hash-only change, not a click-caused pixel change on the line; it
cannot distinguish the band from any pixel diff. See required fix F1.

## 2026-11-22 02:58 +07 (t+8m) C12 adjudication: conversion layer

What the amend builds: dom_rect_to_image_point (fastpath.py) =
screen = viewport origin + rect center, then the inverse of
cu.image_point (verified the linear maps are exact inverses from
cu.py:995-1000). Fail-closed outside the image. Synthetic 7/7.
What C12 requires on top: Hyprland window geometry + DPR +
viewport origin, AT-SPI cross-check.
- No Hyprland geometry term anywhere in the amend; no DPR term
  (window.devicePixelRatio is never read); no AT-SPI cross-check
  (scripts/a11y.py exists but is never called from this path).
- The core assumption is contradicted by the repo's own calibration
  report: docs/calibration-e2-report.md:21 says mozInnerScreenX/Y
  in this Zen build are WINDOW-relative (240, 8), not absolute screen
  coords, and screen px needs the window origin (2509, 914) added.
  The amend treats mozInnerScreenX/Y as the absolute screen origin.
  If the report is right, dom_rect_to_image_point fails closed
  (ValueError, point outside image) on every live Zen call: loud, so
  no mis-click, but the DOM-first path is dead on arrival.
- No live validation exists: the 7/7 accuracy is synthetic with fake
  sessions; clone2's bench validated rect agreement across protocols,
  not rect-to-screen conversion; the G30 live case (Codex clicking
  (300,1132)) used an image point from a fresh observe, not a DOM rect.
- One ZT-B line must NOT be read as evidence against the amend:
  "mozInnerScreenX returned null via Marionette eval" is explained in
  the same log (line 15) by the eval omitting `return`; the amend's
  viewport_origin includes an explicit `return`, so that finding does
  not apply. The window-relative finding above is the live issue.
Adjudication: PARTIAL. The amend builds the conversion function shape
but does not satisfy C12: a further build is still open (live probe
of mozInnerScreen against hyprctl window origin, window-origin/DPR
terms, AT-SPI cross-check). See required fix F2.

## 2026-11-22 02:59 +07 (t+9m) 12-item checklist (verified from the diff + runs)

- C1-1 session_continuation regression: FIXED, test passes in the 315
  run. Repair is the C1-prescribed fixture change (mock post hash
  '1111'). Note (F6): TYPE_AFTER_REFRESH is a type-only batch, so the
  test passes via the whole-frame-hash fallback and never runs the band.
- C1-2 G28 widening to pointer-only: FIXED. run() refuses every batch
  on a rejected given observation; pointer-only test flipped; module
  docstring now says "for any batch". No-observation default unaffected
  (rejected is None there).
- C1-3 type_verified None on terminal-None after-skip: FIXED in cu.py.
- R1 type-verification false-pass: PARTIAL, see F1/F3. The D2 harness
  shape is closed; the live pixel confound is not.
- R2 pointer-only substitution: FIXED, stronger than the RT minimum
  (refusal, not just a top-level flag).
- R3 envelope drops type_verified/error_code: FIXED on both paths
  (session + fallback), fields always present.
- R4 refusal remedy cannot type: FIXED, remedy split by has_keyboard.
- R5 malformed zen_dom responses escape raw: FIXED (JSON decode,
  HTTPException, missing "value" all become ZenDomError; the raise
  inside _wd is not re-caught because ZenDomError is not in the
  except tuple). Tests cover all three shapes.
- R6 failed tab restore swallowed: FIXED in tab_at and full scan
  (raise, never swallow). Tests cover it.
- R7 scan burns one timeout per handle: FIXED (stops after the first
  transport failure, raises the wedge). Side effect (F4): the `list`
  CLI subcommand now dies with a traceback on a wedged session.
- R8 tab_at handle-order claim: FIXED (docstring downgraded to
  handle-list index; switch verified via _verify_selected). Tests
  cover the switch-not-taking-effect shape.
- R9 docstring overclaims G28: FIXED (docstrings now say "for any
  batch", matching the widened behavior).
- Item 12 (replaced, DOM-first + cheap verification + bar numbers):
  BUILT as code (zen_dom helpers, fastpath mapping, dom_act
  orchestrator). Bar numbers measured in tests: observes per task
  unchanged at 3 (preflight fresh + after + settle re-capture,
  asserted by test_click_type_enter_uses_no_extra_observes); actions
  per observation 3 (click + type + Enter from 1 observation);
  synthetic grounding accuracy 7/7 = 100% (bar >= 90%). Live proof
  (2-vision benchmark, wall time vs Codex 2.5 min) is still owed,
  as the amend log itself states. The DOM path has no live caller
  (F1) and the conversion is unvalidated live (F2).
- Hygiene: 0 em dashes and 0 en dashes in the code diff
  (scripts + tests); ydotool appears once as the words "No ydotool"
  in a dom_act.py docstring, not usage; no personal info in the diff;
  no changed line alters image_point, move, or _check_entry_pyc
  (verified with a git diff -U0 changed-lines scan; image_point is
  mentioned only in comments/docstrings as the inverse map).

## 2026-11-22 03:00 +07 (t+10m) Review (b): the combined design

Sound parts: the browser split is correct (CDP for Brave only, Marionette
for Zen; CDP is dead on Zen per clone2). The one-session constraint is
respected by the per-browser choice. HCU guard + plan-once + stop at
first failure compose with the V1-V6 cheap verification bundle.
Outcome scoring (M1) as the acceptance metric is right.
Gaps and conflicts, all in the unbuilt design (none blocks the amend
itself, but D1/D3/D4 must be settled before the benchmark worker builds):
- D1 One-session sequencing unspecified. If the benchmark wants BiDi
  rect reads (fastest per clone2, 0.006-0.011s) AND Marionette real
  clicks on the same Zen instance, the sessions must be sequenced
  (close one before opening the other) and the cold session.new cost
  (1.5-2.8s) budgeted. The design names Marionette for the Zen harvest,
  which avoids the handover but gives up BiDi speed; either way the
  choice and its cost must be written down.
- D2 The HCU guard has no owner or location: which component re-checks
  live geometry/focus before each input (dom_act? a wrapper around
  desktop_act?), per action or per batch? As written the guard is a
  citation, not a component.
- D3 Mantis numbering on live Messenger: Mantis is Chromium-only, so
  the numbering/diff format must be ported to the Marionette harvest,
  and ref stability on a mutating chat page is unaddressed (messages
  stream in; positional refs shift; a stable key such as a selector
  or node id is needed). The vendor numbers (29-47% fewer tokens
  etc.) were measured on public sites with other models and must not
  be carried as expected gains for Messenger/Zen.
- D4 Exactly-once sends are asserted, not mechanized: if the V12
  finish gate fails on render lag, a retry double-sends. The mechanism
  is owed (check the sent bubble before any retry; dedupe by text
  plus timestamp).
- D5 "VISION 1" is a DOM harvest, not a screenshot: the benchmark's
  "2 visions" are really 1 DOM read + 1 screenshot check. The
  terminology should say so, or the count misleads.
- D6 Two windows (clone1 + clone2) in one Zen instance vs two
  instances is unspecified; one Marionette session covers both tabs
  only if they share an instance.

## 2026-11-22 03:01 +07 (t+11m) VERDICT: AMEND

Not BLOCK: nothing in the diff fails silently live; every new failure
mode is loud, and the 315-test suite passes with fail-before proven.
Not GO: R1 is not closed on any live path, and the C12 conversion
rests on an assumption the repo's own calibration report contradicts.

Required fixes (file:line evidence in the log above):
- F1 (GATING, R1 residual): wire the DOM value check into the live
  browser-type path. (a) Add regression tests where the after image
  differs from the pre-batch image ONLY by a caret column / focus
  ring on the anchor line, expecting ok False with error_code
  type_unverified; these fail on the current amend code (probes P1/P2
  above). (b) Route browser type batches through dom_act.focus_type
  (or pass ZenSession focus/type closures from first_action/act into
  desktop_act) so those tests pass; until wired, downgrade the R1
  claim in the amend log from "the incident shape now fails" to
  "narrowed to the input line; correct-click/no-text still
  false-passes without the DOM check". Verify: caret-only test fails
  before, passes after; 315-test suite still OK.
- F2 (GATING, C12): resolve the mozInnerScreen contradiction
  empirically. One live probe on the laptop (Zen): read
  mozInnerScreenX/Y via the amend's viewport_origin, read the window
  origin via hyprctl clients, click a known rect center via dom_act,
  and record whether the point lands; add the window-origin term if
  the value is window-relative, and a DPR term (read
  window.devicePixelRatio; assert scale==1 on the target monitor if
  the term is omitted). Until the probe lands, C12 stays OPEN and
  dom_rect_to_image_point must not be cited as satisfying C12.
  Verify: probe log + a test pinning the agreed conversion.
- F3 (band hygiene): (a) _input_line_changed returns True on size
  mismatch (scripts/cu.py:1038-1039): a resize between frames verifies
  any type batch; return None instead so it falls back to the hash
  with the note. (b) type_anchor tracks move/hover/drag-to; restrict
  it to click/double_click (probe P7: hover state false-passes).
  (c) Document the off-line-click false-fail (probe P6: text lands
  off the anchor line) and cover it with a test; the DOM check (F1)
  is the fix. Verify: unit tests for (a), (b), and the off-line shape.
- F4 (zen_dom CLI): the `list` subcommand (scripts/zen_dom.py:503-504)
  has no error handling, so after R7 a wedged session dies with a
  traceback instead of printing JSON error entries. Catch ZenDomError
  in main and print a JSON error object with exit code 1. Verify:
  wedged-session CLI test.
- F5 (verify_typed brittleness): verify_typed uses exact equality
  against the field value (scripts/zen_dom.py: verify_typed); for
  contenteditable, textContent can carry a trailing newline/whitespace
  or pre-existing text, which false-fails. Compare stripped/ends-with
  or document the exact-empty-field precondition. Verify: test with a
  trailing newline in the field value.
- F6 (coverage note, may be accepted as a note): the relay tests pass
  via the whole-frame-hash fallback (type-only batches, no anchor),
  so they never exercise the band. Add one relay-level click+type
  test with distinct after-image pixels so the band path is covered
  above the unit level, or record the gap in the amend log.
