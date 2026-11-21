# CLICK3-C1R2 review log: council review (round 2) of the AMEND3 fix pass

Worker: CLICK3-C1R2 (council reviewer 1, round 2, independent: did not
write AMEND2 or AMEND3). Coordinator: COORD-CLICK-2.
Owner: Pham Tuan (repo-facing name). Branch: todolist-push.
Range reviewed: amend tip 4b7d6ac to HEAD 9bcfb04 (AMEND2 verbatim
commits 2a25e7a..c01d4a2, AMEND3 fix commits e5c1c47, 0367ec9, 0356389,
d7b1579, 4110e72, 2dcd5d8, 5d49e51, log 9bcfb04). Two unrelated commits
sit inside the range and were not reviewed as AMEND3 work: 807ba6e
(skill-update log, other worker) and 8457997 (coord2 baseline-A log,
doc-only, 1 file). HEAD moved under this review to fd3d8ed (coord3
doc-only commit, +36 lines to improvements/worker-click2-amend2-log.md,
no code or test change); all test runs below are valid for 9bcfb04 code.
Task start: 05:08 +07 22/11/2026. All times wall-clock Asia/Ho_Chi_Minh
+ elapsed from task receipt. Standing rules: full access, no em dash
(U+2014) or en dash (U+2013) anywhere including quoted window titles,
never ydotool, no personal info in repo files, review only (no code or
test edits). No 15-minute stall occurred at any point.

## Verdict: AMEND

Six of the seven AMEND3 fixes are verified correct with real
failing-first evidence (steps 1, 2, 3, 4, 6, 7), R1/R3a/R10 are closed
in substance, the R7 fixture edit is re-verified by this reviewer, and
the full discover is 1855 tests with 0 failures. But step 5 is wrong
in both branches: the division by the factor falsely refuses valid
geometry at factor 2, for the input production actually supplies as
well as for the no-size fallback, and its test locks in a premise the
pipeline itself contradicts. That is a proven false refusal introduced
by the fix, so this pass cannot be stamped GO as-is. The fix is small
and precisely specified in G1 below. This is AMEND, not BLOCK: at the
measured factor 1 the step-5 code is a proven no-op, and the 2-vision
benchmark runs at factor 1 against a top-document Messenger composer,
so no benchmark path is affected by G1-G4. G1 must be fixed before
landing; G2-G4 are minor residuals to fix in the same round.

## Time log

- 05:08 +00m task received; branch todolist-push, HEAD 9bcfb04.
  Sources read in full: worker-click3-rt-synth.md (dd45231),
  worker-click3-diff-assess.md (910e471), worker-click3-amend3-log.md
  (9bcfb04), worker-click2-c12probe-log.md (cd89597).
- 05:10 +02m diff stat checked; AMEND2 verbatim confirmed (see below).
  Steps 1-7 diffs read commit by commit.
- 05:12 +04m step-5 concern found on reading: the None branch divides
  an already-CSS-px outer size. Proved empirically with the fake
  (valid probe geometry raises at factor 2, window_size None).
  Given-size branch checked against the pipeline unit convention
  (cu.py:731, monitor_box, grim -s 1); production-realistic input
  [1863, 1176] at factor 2 raises at HEAD, passes pre-step-5.
  Hyprland layout-pixel model confirmed by web search (the Hyprland
  tree uses global layout pixels).
- 05:15 +07m step 8 (R7) re-verification done in node: old
  strict-equality JS returns False on the corrected fixture, new
  shadow-walk JS returns True. Step 8 CLOSED by this reviewer.
- 05:17 +09m HEAD targeted run: the 6 new tests + 2 snapshot tests,
  8/8 OK.
- 05:18 +10m fail-before worktrees: step 2 R1 fails before
  (ValueError not raised), step 3 R3a fails before (errors=2,
  TypeError), substance check on old code (12 wrong-field px True,
  3 px False).
- 05:19 +11m fail-before worktrees: step 4 R10 fails before (True is
  not false), step 5 factor-2 fails before (ZenDomError not raised),
  step 6 iframe fails before (contentWindow.document not found in
  the old field_value script; the 2 contentWindow occurrences in old
  zen_dom.py are locate's lines 463-464 only).
- 05:20 +12m step-1 fail-before at c01d4a2: test_cdp_snapshot FAILED
  (failures=1); 2/2 OK at HEAD. Full discover started.
- 05:21 +13m affected suites 373/373 OK; node cdp_validation.mjs
  3 ok lines. Temp worktrees removed.
- 05:24 +16m full discover run 1: Ran 1855 tests, FAILED (errors=4,
  skipped=17), 0 failures. Re-ran to file for the exact count line.
- 05:28 +20m full discover run 2 (to /tmp/discover-c1r2.log):
  Ran 1855 tests in 228.459s, FAILED (errors=4, skipped=17).
  The 4 errors are the pre-existing set (see Test evidence).
- 05:29 +21m review written; commit follows with an explicit
  pathspec for this file only.

## Scope check: AMEND2 committed verbatim

`git diff --stat 910e471..c01d4a2` is 25 files, +2618/-304. Removing
the one unrelated file that landed in between (the skill-update log,
122 lines, commit 807ba6e, another worker) leaves exactly the assessed
uncommitted tree: 24 files, +2496/-304. Per-file counts match the
assessment: zen_dom.py 569 changed (+522/-47), dom_act.py 474,
cu.py 288, fastpath.py 103, cdp.mjs 94, test_click2_redteam.py 9
(the single R7 fixture edit). AMEND2 was committed verbatim as
claimed. The AMEND3-only diff (c01d4a2..9bcfb04, excluding the
unrelated baseline-a log) is 12 files, +647/-121.

## Step 1: cdp.mjs set_value regression, VERIFIED

Fix (e5c1c47): capture oldValue before the native-setter write,
dispatch input/change only when e.value !== oldValue; setter write
and both read-backs stay unconditional, so the R2 fix is preserved.
Fail-before: temp worktree at c01d4a2, `python3 -m unittest
test_cdp_snapshot` from tests: Ran 2 tests, FAILED (failures=1),
the assessed regression reproducing exactly. Pass-after at HEAD:
2/2 OK. The snapshot contract (tests/cdp_snapshot.mjs:192-193,
unchanged text fires zero events) holds, and the changed-value case
(lines 160-171, set_value writes the value, ok true) still passes.
Minor coverage note, filed as G4: no assertion checks the events
FIRE on a changed value, so a future edit dropping the dispatch
would still pass this suite; the changed side is verified only by
reading the code. Code review confirms the dispatch is present and
correctly gated.

## Step 2: R1 fallback removal, VERIFIED

Fix (0367ec9): the fallback retry in dom_rect_to_image_point is
deleted (15 lines of code plus the docstring paragraph); the function
now raises when the absolute reading maps outside the image. The
docstring records why the net was removed. Fail-before: temp
worktree at 8457997 with HEAD's tests/test_click2_redteam.py copied
in, the rewritten test fails with "AssertionError: ValueError not
raised", the fallback rescuing the raw pair exactly as the assessment
proved. Pass-after at HEAD: the test goes through
zen_dom.viewport_origin output [2749, 922] on probe geometry, asserts
the point (351.7, 734.4), and asserts the raw pair [240, 8] raises.
R1 is now proven through the corrected chain, not the net. No other
caller relied on the fallback (grep shows no other rescue path).

## Step 3: R3a band narrowing, VERIFIED

Fix (0356389): _input_line_changed gains x_range (clamped to the
image, invalid range returns None, empty range returns False);
desktop_act gains type_x_ranges, one pair per type group, padded
with None for groups without a range (those keep the full-width
band, as documented); dom_act.grounded_x_range computes the image-px
range from the grounded rect (CSS width x factor x image/screen,
centered on the image point, dimensionally correct); focus_type
passes it through act_fn; first_action grounds best-effort after
open_dom_hooks and passes [x_range], never failing the batch when
grounding is unavailable. Fail-before: temp worktree at 0367ec9
with HEAD's tests/test_type_verification.py copied in, the two new
tests fail with errors=2 ("TypeError: desktop_act() got an
unexpected keyword argument 'type_x_ranges'"), as the log records.
Substance check on the old code (same worktree): 12 changed pixels
in another field on the anchor line returns True from the full-width
band, while 3 pixels returns False, confirming the RT fixture was
under min_pixels 4 and the finding was open in substance. Pass-after
at HEAD: test_type_verification 59/59, including both new tests
(wrong-field pixels outside the range do not verify at the band level
and at the desktop_act level with ok False / type_unverified; the
same pixels inside the range still verify). min_pixels 4 and the
per-group anchors are untouched. Residual, filed as G2: the cu CLI
act path and CodeExecBackend.act do not supply ranges (see below).

## Step 4: R10 flag consultation, VERIFIED

Fix (d7b1579): ZenSession.verify_typed now requires the V11 typed
flag whenever before is given, not only in the prefill case; the
docstring is updated to match. Both fakes were corrected to model
the trusted-event flag faithfully (True only on a recorded trusted
input event; the old shape treated any value change since arming as
typed, which made the fakes blind to the JS-set attack). The real
mechanism is sound: arm_typed_flag installs
`e.addEventListener('input', function(ev){ if(ev.isTrusted)
window.__agentCuTyped[sel]=true; })` (zen_dom.py:866-868), so a page
script setting el.value and dispatching synthetic input events
leaves the flag clear. Fail-before: temp worktree at 0356389 with
HEAD's tests/test_zen_dom.py copied in, the new test fails with
"AssertionError: True is not false", the old code verifying the
JS-set empty-field value. Pass-after at HEAD: the new test passes,
including the positive control (a real trusted event on the same
shape verifies). The prefill case is kept as-is (the existing
before='hello' test still passes). R10 is closed in substance: a
value that appears with no trusted input event fails whenever a
before-value is given. before None keeps the old equality-only shape
for callers that never type, as the handoff specified.

## Step 5: geometry unit mixing, NOT VERIFIED, see G1

What was done (4110e72): viewport_origin divides window_size by the
factor before check_viewport_geometry, and ground_many_one_shot does
the same for its direct check call; a factor-2 test was added. The
test as written passes at HEAD: explicit size [3726, 2352] at factor
2 returns [2989, 930], and size [3000, 2000] raises. But the fix is
wrong in both branches, and the test bakes in the wrong premise
(full proof in G1). The ground_many_one_shot half is correct as
written (it uses outer as-is when no window size is given, with a
comment stating exactly the rule viewport_origin violates), which
shows the worker knew the distinction and applied it in one place
only. The containment conservatism the log notes (screen absolute
origin compared against a CSS-px window rect) is real but
conservative-only, and is not the defect: the defect is the closure
check refusing valid geometry.

## Step 6: iframe traversal, VERIFIED (with residual, see G3)

Fix (2dcd5d8): field_value and verify_typed now use the same find()
helper as locate (shadow pierce, then same-origin iframe traversal,
cross-origin access inside try/catch, failing closed). Fail-before:
temp worktree at 4110e72 with HEAD's tests/test_zen_dom.py copied
in, the new test fails with "'contentWindow.document' not found in
..." the old field_value script; grep confirms 0 occurrences of
contentWindow in field_value/verify_typed before the fix (the 2
occurrences in old zen_dom.py are locate's lines 463-464). Pass-after
at HEAD: the test passes for both methods. The test is a
script-shape assertion (a stubbed evaluate returning canned values),
not a behavioral test against a real iframe DOM; it proves the
production code sends the traversal, consistent with how locate's
traversal is tested in this suite, and the cross-origin fail-closed
behavior follows from the try/catch in the sent JS. Residual, filed
as G3: focus_check, hit_check, and arm_typed_flag still look the
target up in the top document only, so shadow/iframe targets still
fail closed at the gates.

## Step 7: duplicate import, VERIFIED

Fix (5d49e51): one `import os` deleted from scripts/zen_cli.py
(was lines 92 and 96); one remains at line 92; py_compile OK
(re-checked by this reviewer). Cosmetic, exact.

## Step 8: R7 re-verification (done by this reviewer), CLOSED

The AMEND3 log left step 8 to a fresh reviewer; this reviewer did
it. The corrected fixture in
tests/test_click2_redteam.py::test_focus_check_shadow_host_false_negative
genuinely models a focused input inside a shadow root: __inner is an
INPUT, __host is a DIV with shadowRoot.activeElement = __inner, and
document.activeElement = __host, while querySelector returns __inner.
Independent node check (old focus_check JS extracted from 4b7d6ac,
new JS from HEAD, same corrected shim): old strict-equality code
returns False, new shadow-walk code returns True. The AMEND2 fixture
edit is a justified correction, not a weakening: the old fixture
(host without shadowRoot) did not model what its docstring described,
and the old code still fails the corrected fixture. The class name
R7ShadowTests is a pre-existing misnomer (the content is R9 shadow
focus, not R7 stale DOM); harmless, not a gap. Step 8 CLOSED.

## Decision 1: AT-SPI cross-check dropped, AGREE

The probe proves the AT-SPI half cannot run on this Zen: run 3, the
bus works and lists 6 apps but Zen PID 496121 is not registered
(accessibility never activated at its 17:37 startup); run 2,
chrome-context eval via geckodriver moz/context is HTTP 500 and
needs MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 plus a Zen restart, which
must not be done. No new AT-SPI attempt was made by AMEND3, correctly.
The substitute (dimension closure + window/monitor containment in
check_viewport_geometry, validated by the probe with grim pixel-edge
measurement of the urlbar pill) catches the known failure modes: an
absolute reading off-monitor, and impossible closure. Caveat, recorded
not as an objection: the substitute is not a fully independent
instrument, since both checks derive from the same JS reads plus
Hyprland geometry; but the independent instrument for the empirical
question was the probe's own grim measurement, and no second live
instrument exists for this Zen. Re-prescribing AT-SPI would be
prescribing something proven not to run. AGREE with the drop.

## Decision 2: B18 V4 caret position out of scope, AGREE

The reasons given are sound. selectionStart/selectionEnd are
settable by page JS in one extra line, so a caret-at-end check adds
no discrimination against the JS-set attacker: the same script that
sets el.value can set the caret to the end, while isTrusted cannot
be forged by page JS (synthetic events are untrusted). Requiring
caret-at-end would also false-fail legitimate flows (click mid-text
to edit, IME composition). RT R10 / checklist A10 asked for flag
plus value plus caret, but the caret half is satisfied in substance
by the flag: the flag is the discriminator, the value is the content,
and the caret is a UX signal, not a verification signal. The log's
placement note (if a caller ever needs the caret for another reason,
the helper belongs in zen_dom next to field_value, bundled in the
same evaluate) is right. AGREE with out of scope.

## Remaining gaps (AMEND list)

### G1 (must fix, blocks landing): step-5 division is wrong in both branches

File/function: scripts/zen_dom.py viewport_origin (lines 604-616);
test: tests/test_zen_dom.py
test_viewport_origin_factor_two_geometry.

(a) None branch. When window_size is not given, size falls back to
[raw[7], raw[8]] = window.outerWidth/outerHeight, which are CSS px
by definition. Step 5 divides them by the factor. Proof, run by this
reviewer with the FakeWdSession (probe geometry, dom_factor 2,
window_size None): HEAD raises "dimension closure fails: mozInner
[240, 8] + inner [1615, 1160] exceeds window size [931.5, 588.0]".
Valid geometry, false refusal. The branch is reachable in
production: ground_input (dom_act.py:135-144) passes window_size
None whenever the meta has a region but no window_bounds, and
_viewport_origin falls back to region in that case.

(b) Given-size branch. window_size comes from meta window_bounds,
which is Hyprland client at+size (cu.py bounds(), line 582). Hyprland
reports client geometry in global layout (logical) pixels, and the
repo's own code says so: cu.py:731, "window_bounds must use integer
logical dimensions"; monitor_box() divides physical monitor size by
scale (cu.py:549-552); the observe comment at cu.py:944, "grim -s 1
uses logical layout pixels". Logical px equal CSS px numerically
when devicePixelRatio equals monitor scale, so no division is needed
or correct. Proof, same fake at factor 2: production-realistic input
[1863, 1176] raises at HEAD ("exceeds window size [931.5, 588.0]"),
while pre-step-5 code (worktree at d7b1579) returned [2989, 930]
for the same input. The test's [3726, 2352] input is physical-px
shaped and is not what production supplies; the test therefore locks
in the wrong premise, and its raises-half ([3000, 2000] must raise)
is wrong under the pipeline convention too (a 3000-logical-px window
closes fine: 240 + 1615 + 8 = 1863 <= 3000).

Fix required: in viewport_origin, pass the size as-is in both
branches (window_size when given, else [raw[7], raw[8]]); drop the
division and correct the size_css comment to state both sources are
already CSS px. Rewrite the factor-2 test to production-realistic
inputs: viewport_origin([2509, 914], [1863, 1176]) at factor 2
returns [2989, 930] per the existing absolute formula, and
viewport_origin([2509, 914], [1500, 1000]) at factor 2 raises (the
window genuinely cannot contain mozInner + inner). Add the
None-branch case: viewport_origin([2509, 914]) at factor 2 with
probe geometry returns [2989, 930]. Note, out of this fix's scope:
the absolute formula itself (window_origin + mozInner * factor)
mixes a logical origin with a physical offset at factor != 1, which
is a pre-existing AMEND2 question, not something step 5 was asked
to settle; it needs live factor-2 evidence before any claim either
way. The check must not refuse valid geometry regardless of that
open question. At factor 1 (the measured setup and the benchmark)
the division is exact and changes nothing, which is why this is
AMEND and not BLOCK.

### G2 (minor): R3a ranges not wired into the cu CLI act path or CodeExecBackend.act

File/function: scripts/cu.py, CLI act path (~2894-2927) and
CodeExecBackend.act (~2588-2605). Both wire focus_check/type_check
via open_dom_hooks/dom_hooks but never pass type_x_ranges, so the
band stays full-width there. When --dom-selector is given the DOM
check is the sufficient check and the band is secondary, but without
it the band is the only check and R3a stays open on those paths.
Fix required: after open_dom_hooks succeeds, ground best-effort
(dom_act.ground_input, then grounded_x_range) and set
act_kwargs['type_x_ranges'] = [x_range] when a range comes back,
in the same try/except best-effort shape first_action.py already
uses; same in CodeExecBackend.act (it has meta). Note:
desktop_act pads missing ranges with None, so in a multi-type-group
batch only the groups with a supplied range are narrowed; callers
should supply one range per group where they can.

### G3 (minor): focus_check, hit_check, arm_typed_flag still top-document only

File/function: scripts/zen_dom.py focus_check (~693), hit_check
(~660), arm_typed_flag (~833). focus_check and hit_check look the
target up with plain document.querySelector (no pierce, no iframe
walk); arm_typed_flag uses pierce (shadow) but no iframe walk. So a
shadow/iframe target that locate/field_value/verify_typed now support
still fails closed at the gates: ground_input refuses at hit_check
(e is null), the focus gate refuses at focus_check, and arm returns
False so verify_typed with before fails. All fail-closed, never a
wrong pass, and the benchmark target (Messenger composer,
top-document contenteditable) is unaffected, but R9 is not fully
closed for shadow/iframe targets. The AMEND3 log discloses
focus_check only; hit_check and arm were not mentioned. Fix
required: reuse the find() helper (pierce + same-origin iframe
traversal) for the element lookup in focus_check and arm_typed_flag;
for hit_check, elementFromPoint from the top document returns the
iframe element itself for iframe targets, so the hit comparison
needs frame-aware handling, and at minimum the limitation must be
documented loudly if it is not fixed in this round.

### G4 (minor, test only): no changed-value event assertion in the snapshot suite

File: tests/cdp_snapshot.mjs. The suite asserts zero events on
unchanged text (line 193) but nothing asserts the two events fire
on a changed value; the harness already records events on
node.events (line 46). Fix required: one assertion in the changed
value set_value case (around line 168) that the target recorded
input + change events. No production change. (The live side is
covered by tests/browser_field_live.py:146, which is not part of
the unit suite run here.)

## Test evidence (run by this reviewer, all at HEAD 9bcfb04 code)

- New tests + snapshot, targeted: `PYTHONPATH=../scripts:.
  python3 -m unittest test_click2_redteam.R1ConversionTests.
  test_raw_moz_inner_screen_origin_must_land
  test_type_verification.TypeVerification.
  test_band_wrong_field_with_rect_range_must_not_verify
  test_type_verification.TypeVerification.
  test_band_wrong_field_with_rect_range_reports_not_ok
  test_zen_dom.TestDomHelpers.
  test_verify_typed_js_set_without_keystrokes_must_not_verify
  test_zen_dom.TestDomHelpers.
  test_viewport_origin_factor_two_geometry
  test_zen_dom.TestDomHelpers.
  test_field_value_and_verify_typed_traverse_iframes
  test_cdp_snapshot`: Ran 8 tests, OK.
- Fail-before, each in a temp worktree at the fix's parent commit
  with the HEAD test file copied in (worktrees removed after):
  step 1 at c01d4a2, test_cdp_snapshot FAILED (failures=1); step 2
  at 8457997, R1 test FAILED (ValueError not raised); step 3 at
  0367ec9, R3a tests FAILED (errors=2, TypeError unexpected keyword),
  plus the substance check (old full-width band returns True for 12
  wrong-field px, False for 3 px); step 4 at 0356389, R10 test FAILED
  (True is not false); step 5 at d7b1579, factor-2 test FAILED
  (ZenDomError not raised); step 6 at 4110e72, iframe test FAILED
  (contentWindow.document not found in the old field_value script).
  All six fail before and pass after, for the substantive reason in
  each case, not a harness artifact.
- Affected suites: `python3 -m unittest test_click2_redteam
  test_dom_act test_zen_dom test_pick4_fastpath test_type_verification
  test_first_action test_keyboard_preflight test_session_continuation
  test_fast_observe test_browser_start_warm test_endpoint_retention`:
  Ran 373 tests, OK (matches the AMEND3 log's 373 total).
- Node: `node cdp_validation.mjs` from tests: 3 ok lines (key
  preflight, adapter preflight, harvest).
- Full discover (run twice by this reviewer):
  `PYTHONPATH=../scripts:. python3 -m unittest discover -p
  'test_*.py'`: Ran 1855 tests in 228.459s, FAILED (errors=4,
  skipped=17), 0 failures. The 4 errors are the pre-existing set
  named by the assessment (test_a11y_skeleton import,
  test_cursor_file setUpClass g++ rejects -std=c++26,
  test_perf_evidence x2 missing benchmark JSON). Confirms the AMEND3
  log's 1855/0-failures claim exactly.
- Step-5 counter-proofs (FakeWdSession, probe geometry,
  dom_factor 2): HEAD viewport_origin([2509, 914], [1863, 1176])
  raises (closure sees [931.5, 588.0]); pre-step-5 worktree returns
  [2989, 930]; HEAD viewport_origin([2509, 914]) with window_size
  None raises (closure sees [931.5, 588.0]).

## Hygiene checks

- Em/en dash: 0 added lines with U+2014 or U+2013 in the AMEND3
  code+tests+log diff (checked in Python over the full diff), and 0
  in improvements/worker-click3-amend3-log.md.
- ydotool: the only mentions in the AMEND3 diff are in the log's
  standing-rules text ("never ydotool", "No ydotool"); no use in
  code or tests. This reviewer used wtype-free node/python checks
  only; no live laptop driving, no browser work.
- Personal info: no emails, addresses, phones, or credentials in the
  AMEND3 diff; only the owner name Pham Tuan and the already-published
  Zen PID 496121 from the probe log.
- Untracked files from other workers were left untouched; this
  review commits only its own file (explicit pathspec below).

## Commit record

Report file: improvements/worker-click3-c1r2-review-log.md (this
file). Staged and committed with an explicit pathspec; push verified
with git ls-remote (see the coordinator copy of this log for the
hash; this worker's final report to the coordinator carries it).
