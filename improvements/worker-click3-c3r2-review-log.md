# CLICK3-C3R2 review log: council review round 2 of the AMEND3 surgical fix pass

Worker: CLICK3-C3R2 (council reviewer 3, round 2; independent, did not
write AMEND2 or AMEND3). Coordinator: COORD-CLICK-2. Owner: Pham Tuan
(repo-facing name). Branch: todolist-push. Task start: 05:08 +07
22/11/2026. All times wall-clock Asia/Ho_Chi_Minh on this VM plus
elapsed from task start. Standing rules: full access, no em dash
(U+2014) or en dash (U+2013) anywhere including quoted window titles,
never ydotool, no personal info in repo files, log everything, review
only (no code or test edits).

Angle: this review reads the fixes for what they do LIVE, not for what
they do in tests, and judges whether the 2-vision benchmark can now be
built on the fixed code. Code mechanics were already covered by the
diff assessment (commit 910e471); this review traces live paths,
false-fail shapes, and benchmark readiness, and it re-verifies the R7
step-8 item from the live-behavior side.

HEAD note: work started at 9bcfb04 as briefed. During this review HEAD
moved to d086856 (fd3d8ed coord3 log preservation, d086856 R7 review).
`git diff 9bcfb04..HEAD --stat` is log-only (2 files, both under
improvements/), no change to scripts/ or tests/, so the code under
review is unchanged. The R7 review log was read in full and is
addressed in the step-8 section below.

## Verdict: AMEND

The AMEND3 fixes are sound where they land, and nothing that worked
before is broken on the live factor-1 path: every new failure mode is
a loud refusal, never a wrong click or a false pass, and the affected
suites pass (375 tests OK on independent re-run, full discover 1855
tests with 0 failures). But the review finds one real regression
introduced by step 5, one half-finished fix in step 6 whose live
effect on typing flows is zero, and two design-doc gaps that must
close before the benchmark worker builds on the design. All five gaps
are small and precisely located; none needs a redesign. Fix list:

- G1 (code, benchmark-gating): scripts/zen_dom.py viewport_origin
  lines 604-616, window_size=None fallback divides CSS-px outer size
  by the factor. One-line fix plus a test (see gap list).
- G2 (code, benchmark-gating unless live-confirmed otherwise):
  scripts/zen_dom.py hit_check line 660, focus_check line 693,
  arm_typed_flag line 833, harvest line 905: no shadow pierce or
  iframe walk where step 6 added it to field_value/verify_typed.
  Same find() helper fix, plus an honest-shim R7 test (see gap list).
- G3 (design doc, benchmark-gating): benchmark target browsers
  ambiguous: coord-log addendum says one Zen instance, two tabs,
  while the owner benchmark definition and the live lane put clone1
  and clone2 in Brave + Chrome windows on ws2, and the CDP half is
  still an open item. One explicit decision line (see gap list).
- G4 (design doc): coord-log design text still promises V4 caret
  position (lines 61, 85) although B18 drops V4 out of scope.
  One-line correction (see gap list).
- G5 (code, follow-up, not benchmark-gating): scripts/cu.py
  BrowserAdapter.act near line 2600 and the CLI act path near line
  2906 wire dom_hooks but do not forward type_x_ranges, so R3a stays
  open on those two production paths. Parity fix (see gap list).

## Sources read in full

- improvements/worker-click3-amend3-log.md (HEAD 9bcfb04): steps 1-7
  and 9 done, R1/R3a/R10 closed in substance, full discover 1855
  tests 0 failures.
- improvements/worker-click3-rt-synth.md (commit dd45231): 34-entry
  checklist A1-A13 + B1-B21, gating order, C12 probe mapping.
- improvements/worker-click3-diff-assess.md (commit 910e471): verdict
  KEEP MOST, 1 regression, 3 weak RT tests, handoff steps 1-9.
- improvements/worker-click2-c12probe-log.md (commit cd89597): verdict
  WINDOW-RELATIVE, absolute origin (2749, 922), window (2509, 914) +
  mozInner (240, 8), DPR 1, scale 1, zoom 100 percent.
- improvements/worker-click3-baseline-a-log.md (commit 8457997):
  corrected baseline, discriminator runs on a normal window, 3/3 X
  landed, median act-now 5299ms for the 6-action batch.
- improvements/worker-click3-r7-review-log.md (commit d086856, landed
  during this review): verdict CONFIRMED on the R7 fixture.
- improvements/worker-coord-click2-log.md: combined design (lines
  61, 85), open items, review round, AMEND2 design addendum (line
  220 onward).
- Diff per amend3 commit: e5c1c47 (step 1), 0367ec9 (step 2), 0356389
  (step 3), d7b1579 (step 4), 4110e72 (step 5), 2dcd5d8 (step 6),
  5d49e51 (step 7). Code traced live: scripts/zen_dom.py
  viewport_origin, locate, hit_check, focus_check, field_value,
  verify_typed, arm_typed_flag, typed_flag, sent_bubble_contains,
  harvest, check_viewport_geometry; scripts/dom_act.py ground_input,
  ground_many_one_shot, grounded_x_range, dom_hooks, focus_type;
  scripts/cu.py _input_line_changed, desktop_act verification block,
  BrowserAdapter.act, CLI act path; scripts/first_action.py fallback
  wiring; scripts/cdp.mjs operations and set_value.

## Per-fix live trace (what changes LIVE, not just in tests)

### Step 1, cdp.mjs set_value (e5c1c47): SOUND

Live change: the native setter write and the read-back verification
stay unconditional (the R2 fix), but the synthetic input/change
events now fire only when the value actually changed (oldValue
captured before the setter write). This restores the snapshot
contract (tests/cdp_snapshot.mjs: unchanged text fires no synthetic
notifications) and removes the one AMEND2 regression. Independent
re-run: test_cdp_snapshot 2/2 OK.

Live caveats, neither a fix demand: first, the "changed" test
compares DOM value only, so a React-controlled input whose DOM value
already equals the text but whose framework state is stale gets no
event and still reports ok:true. That is the pre-AMEND2 contract,
not a new risk, and the CDP path is not the Zen benchmark path.
Second, the synthetic events are untrusted by construction (the
programmatic path), so a page that only listens for trusted input
ignores them; again pre-existing design, unchanged by this step.

### Step 2, fastpath dom_rect_to_image_point fallback removal (0367ec9): SOUND

Live change: a wrong origin, a stale observation, or a moved window
now raises ValueError instead of being silently rescued by the
window-relative retry. All four call sites convert it to a clean
refusal: dom_act ground_input lines 147 and 159 (ValueError to
DomActError), ground_many_one_shot line 312 (same), zen_dom
locate_point line 654 (ValueError to ZenDomError). No caller lets it
escape as a traceback. The R1 test now goes through
viewport_origin output (2749, 922) and asserts the raw pair (240, 8)
raises, so the test proves the chain instead of the net. This is the
correct fail-closed shape, and it is the only step whose live effect
is a pure narrowing: cases that used to return a possibly wrong
point now refuse loudly.

### Step 3, narrowed verification band (0356389): SOUND on the paths that supply it

Live change: desktop_act gains type_x_ranges, one image-px (x0, x1)
pair per type group, and _input_line_changed crops the band to that
range instead of the full image width. dom_act focus_type supplies
it from grounded_x_range (rect width times factor times image px
per screen px, centered on the rect center), and first_action
fallback lines 599-613 supply it the same way. The R3a attack (real
text in a different field on the same line) is closed in substance
on those two paths: the 12-pixel wrong-field failing-first tests
pass.

Layering, verified in the desktop_act verification block: when the
DOM type check passes, verified is True with basis dom-value and the
band is never consulted, so the x_range only matters in the fallback
case (DOM check failed or absent). That is the correct order: the
sufficient check first, the narrowed necessary check second.

Live caveats: first, grounded_x_range assumes the image spans the
whole region (half width uses image width over region width); with a
cropped observation the half width is wrong by the crop over region
ratio, and text at the field edge could fall outside the range. The
benchmark uses full-window observes, so this does not bite there,
but the assumption should be recorded next to the function. Second,
when x1 is less than or equal to x0 the band returns False rather
than None (no fallback to the whole-frame hash); a zero-width rect
would false-fail the band, but hit_check already requires width, so
this is unreachable in practice. Third, two production paths do NOT
supply ranges (see G5): on those the band stays full-width and R3a
stays open in the fallback case.

### Step 4, verify_typed consults the V11 typed flag (d7b1579): SOUND, false-fail audit below

Live change: whenever before is given, verify_typed now requires a
recorded trusted input event (typed_flag) in addition to value
equality. A pre-filled value and a JS-set value on an empty field
both fail without one. The fakes were fixed in the same step: the
old fake treated any value change since arming as typed, which made
it blind to the R10 attack; the new fake returns True only on a
recorded trusted event, matching the real window.__agentCuTyped
flag.

False-fail audit (the question this step lives or dies on: does a
legitimate typed value ever arrive with no trusted input event?):

- Real keystrokes via the native keyboard path: trusted input events
  fire. Pass.
- Mid-text edits (click mid-text, type to insert): trusted input
  events fire; caret position is irrelevant to the flag. Pass. This
  is why the B18 V4 caret decision is correct (see decisions).
- IME composition (Vietnamese Telex through fcitx5/ibus): input
  events fire with isTrusted true during composition and at commit;
  the arm listener checks only isTrusted, not isComposing. Pass.
- Paste (Ctrl+V): trusted input event, inputType insertFromPaste.
  Pass.
- Browser autofill: fires trusted input events in Chrome and
  Firefox. Pass.
- Masked or controlled inputs that preventDefault on keydown and set
  el.value programmatically: NO trusted input event fires, so a
  correctly delivered value false-fails. Real pattern, but the
  Messenger composer (contenteditable, React) does not do this, and
  no benchmark target does. Recorded as a known limitation, not a
  fix demand.
- React re-render replacing the field node between arm and type: the
  listener sits on the old node, so the flag stays clear. The
  Messenger composer node is stable across keystrokes. Caveat only.
- Full navigation between arm and verify: window.__agentCuTyped is
  wiped, flag reads False. A navigation invalidates the field
  anyway, so the refusal is correct, if for the wrong reason.
- The flag is keyed by selector string; two fields sharing one
  selector share one flag entry. locate, field_value, and verify all
  use first match, so this is consistent, not divergent.
- Minor: arm_typed_flag listeners and MutationObservers accumulate
  and are never removed or disconnected; repeated focus_type calls
  on one selector stack listeners that all set the same flag.
  Harmless to correctness, a small leak to note.
- Minor: dom_hooks ignores arm_typed_flag's False return (element
  missing, e.g. an iframe target). Typing proceeds and verify then
  fails at the flag with the generic reason "field value does not
  hold the typed text" instead of "flag never armed". Diagnostics
  only.
- Threat-model note: the flag lives on window.__agentCuTyped,
  writable by page JS, so a page that knows the flag name could
  forge it. The R10 attacker in scope is a page script setting
  el.value, not one that knows the flag name. The flag is a tripwire
  against programmatic sets, not a security boundary; the docstring
  should say so in one line.

Callers checked: the only before-giving callers are typed-input
flows (dom_act dom_hooks type_check via _verify, plus the CLI and
session paths that build the same hooks). No read-only verification
caller passes before, so no legitimate read is newly failed. cdp.mjs
set_value is the programmatic path and is unaffected, as the amend3
log states.

### Step 5, viewport geometry unit conversion (4110e72): PARTIAL, contains G1

Live change: viewport_origin divides the Hyprland screen-px window
size by the factor before check_viewport_geometry, so the dimension
closure is a CSS-px check at factors other than 1. The explicit-size
path is correct: at factor 2, window (2509, 914) size (3726, 2352)
gives absolute origin (2989, 930), and impossible CSS geometry is
refused. The factor-2 test proves both.

But the window_size=None fallback path is broken by this step, proven
independently (script /tmp/c3r2-step5.py, FakeWdSession with the real
ZenSession.viewport_origin):

- Explicit size [3726, 2352] at factor 2: [2989, 930]. Correct.
- No window size (None) at factor 2: ZenDomError, "dimension closure
  fails: mozInner [240, 8] + inner [1615, 1160] exceeds window size
  [931.5, 588.0] (gaps -923.5, -580.0)". The fallback size is outer
  CSS px (1863, 1176), halved by the unconditional division.
- Factor 1, no window size (control): [2749, 922]. Correct.

Before step 5 the no-bounds path passed the CSS outer size straight
to the check and held the closure at any factor (loose, but passing);
after step 5 it refuses at any factor other than 1. That is a
regression for that path, introduced by this step. Reachability:
ground_input (dom_act.py line 113) passes window_size None whenever
meta has no window_bounds; production observes carry window_bounds
(cu.py observe builds it, code_exec.py:505 carries it), so the live
laptop at factor 1 never trips it. But the benchmark script builds
its own meta, and any future caller with a hand-built meta at factor
other than 1 trips it. The fix is one line (see G1), and
ground_many_one_shot already implements the correct shape ("outer is
already CSS px and is used as-is when no window size was given").

The containment half is fine: comparing a screen-px absolute origin
against a CSS-px window rect is conservative at factor over 1 (it
can only refuse, never accept a wrong origin) for any real sidebar
geometry (refusal needs mozInner over half the window width at
factor 2; the measured sidebar is 240 CSS px against 1863). The
monitor-box containment uses screen px consistently. No action here.

### Step 6, iframe traversal in field_value and verify_typed (2dcd5d8): PARTIAL, contains G2

Live change: both methods now use the same find() helper as locate
(shadow pierce, then same-origin iframe traversal with cross-origin
try/catch), so an iframe target reads and verifies, and a
cross-origin target fails closed (None / False, never a wrong pass).
The traversal code itself is correct, including the try/catch around
contentWindow.document access.

But the live effect on typing flows is zero, because the guards that
run before and around typing still cannot see shadow or iframe
targets at all. Proven independently (script /tmp/c3r2-extract.py
extracts the real JS from scripts/zen_dom.py at HEAD; script
/tmp/c3r2-node-proof.js runs it in node under honest shims):

- Extracted focus_check JS contains "pierce": False; contains
  "querySelector": True. Same for hit_check.
- Control (top-document input, focused): focus_check True,
  hit_check True. The harness is valid.
- Honest shadow (input inside a shadow root, focused; top-document
  querySelector honestly returns null): focus_check False, hit_check
  False.
- Honest iframe (input inside a same-origin iframe, focused;
  querySelector honestly returns null): focus_check False, hit_check
  False.

In a real browser, document.querySelector cannot return an element
hidden inside a shadow root or an iframe; that is standard DOM
behavior, and the probe log itself records the same shape for
browser chrome (run 1, all 4 urlbar selectors null). So for a shadow
or iframe target the flow fails in this order: locate finds the rect
(pierces, traverses), then ground_input refuses at hit_check (plain
querySelector returns null, returns False), so focus_check is never
reached; even if it were, focus_check would also return False for
the same reason; and arm_typed_flag pierces shadow roots but has no
iframe walk, so an iframe target never gets its flag armed (returns
False, ignored by dom_hooks) and would fail at the flag even if the
focus gate were fixed. harvest (VISION 1) pierces shadow roots but
has no iframe traversal either, so an iframe target comes back null
and ground_many_one_shot raises before any click. sent_bubble_contains
reads top-document leaf elements only, so a thread inside an iframe
or shadow tree would also miss the V12 gate.

Net: step 6 fixed the two methods that are NOT on the critical path
for typing, while hit_check, focus_check, arm_typed_flag, harvest,
and sent_bubble_contains still cannot see the same targets. R9 is
therefore still open in substance for typing flows, although the
tests pass. The fix is mechanical (see G2). For the likely benchmark
target (Messenger composer, a top-document React contenteditable)
none of this bites, which is why this is AMEND and not BLOCK, but
the benchmark must either fix it or confirm live that its targets
are top-document (see G2).

### Step 7, duplicate import os in zen_cli (5d49e51): SOUND

One line deleted, py_compile OK, one import os remains. No live
effect of any kind.

## Step 8 re-verification (R7 shadow fixture): fixture CONFIRMED, scope boundary DISPUTED

The R7 review (commit d086856, landed during this review) verifies
the fixture correction and the old-code failure, and I agree with
both halves on their evidence: the corrected fixture models a
focused input inside a shadow root (document.activeElement is the
host, host.shadowRoot.activeElement is the inner input), the
original fixture failed even the new code (their control proves it),
and the old strict-equality code fails the corrected fixture 3/3.
The AMEND2 edit was a genuine fixture correction, not a weakening.

I dispute the review's scope boundary, with evidence. It states the
shim having querySelector return the inner input directly "is fine
for THIS test, because it isolates focus_check only: focus_check is
called with an already located element, and piercing belongs to
locate()". That is not what the production code does: focus_check's
own JS performs its own lookup, `const e=document.querySelector(%s)`,
and returns False when that lookup returns null. It does not receive
an already located element; it receives a selector string. The test
therefore proves only the activeElement WALK half of focus_check;
it shims away the lookup half of the very function under test. My
honest-shim node run (above) shows the real JS returns False for a
focused shadow input and for a focused iframe input when
querySelector behaves honestly, while the control (top-document
input) returns True. The existing test passes while the live
behavior it claims to cover still fails.

Consequence: step 8 is NOT closed by the existing test. It closes
when hit_check and focus_check use the same find() helper as locate
(G2) and the node test models querySelector honestly (return null
for a shadow-hidden selector, or exercise the helper directly). The
R7 reviewer and I agree on the fixture; we disagree on what the test
proves, and the node evidence decides that question.

## The two recorded decisions

### AT-SPI cross-check dropped: AGREE

The probe settles this with live evidence, not opinion: run 3 proves
Zen is not on the AT-SPI bus (bus works, 6 apps listed, Zen PID
496121 not registered, accessibility never activated at its 17:37
startup); run 2 proves chrome-context eval is blocked (HTTP 500,
needs a Zen restart, which must not be done). There is no AT-SPI
check to keep. The substitute (dimension closure plus window and
monitor containment in check_viewport_geometry) is validated by the
probe's grim pixel-edge measurement of the urlbar pill. Live
consequence: the geometry check is now the only cross-check, so its
correctness at factors other than 1 rests on step 5, which is why
G1 matters. No live path loses a check it actually had, because
AT-SPI never worked against this Zen. The design addendum records
the drop; the code docstring in viewport_origin records it too.

### B18 V4 caret position out of scope: AGREE on substance, doc stale (G4)

The reasoning is correct: a page script can set el.value and then
set selectionStart to the end in one extra line, defeating any caret
check, while a synthetic input event is untrusted and cannot forge
the V11 flag (short of a page that knows the flag name, see the
step-4 note). A caret check therefore adds no discrimination beyond
the flag for the R10 attack. Requiring caret-at-end would also
false-fail legitimate flows (click mid-text to edit, IME
composition), so dropping V4 REDUCES false-fail risk; the live
consequence of the decision is positive. The only gap is that the
design text still promises V4 (see G4).

## Benchmark readiness: NOT YET, two gating items plus two one-line fixes

RT-SYNTH gating order (section F): design-doc gaps close before the
benchmark worker builds on the design. Measured against that order:

Settled already (verified in the addendum and the code): C12 window
origin plus DPR/zoom term (A1/A13, probe-verified); verification
wiring and ok-True holes (B1, A2/A3/A4, closed in substance on the
DOM paths by AMEND2 plus AMEND3 steps 3-4); send ordering and
exactly-once (A5/A6, Enter split plus V12 bubble gate plus intent
ledger in dom_act focus_type); stale DOM guard as code (A7/B10,
ground_input re-ground plus GroundPoints live re-validation);
one-shot bulk harvest (B14, zen_dom harvest plus cdp.mjs harvest);
VISION 1 terminology (B12, harvest not screenshot); one Zen
instance two tabs (B13, addendum); step-6 owner (B15, parent
orchestrator); Mantis deferred with reasons (B11); MAP-accuracy
relabel (B19); numbering accepted (B20/B21). The 2-vision shape
itself is implementable from the code as it stands for the Zen path:
ground_many_one_shot (VISION 1) plus focus_type with enter True
(scripted send, no vision) plus sent_bubble_contains (VISION 2,
outcome scoring: both messages landed).

Not settled, and gating:

- G1 (one-line code fix): the step-5 no-bounds fallback. The
  benchmark script builds its own meta; it must not trip a factor
  refusal on a legitimate geometry.
- G2 (fix or live-confirm): the R9 typing-path gap. Either extend
  the guards with the find() helper, or confirm live that the
  Messenger composer and send button are top-document (which also
  closes the RT "live confirmation owed" item for R9) and record
  iframe/shadow typing as an explicit scope cut.
- G3 (one decision line): the benchmark target browsers. The
  addendum says "one Zen instance, two tabs for the two clone
  windows", but the owner benchmark definition (02:05) says clone1
  plus clone2 on ws2 with a switch to ws2, and the live lane shows
  the clones in a Brave window and a Chrome window on ws2 (CL2-MSG
  live proof 03:49 drove the clone2 Chrome window; baseline-a drove
  a fresh Brave window on ws2). If the benchmark drives those real
  windows, its DOM path is CDP, not Marionette, and the CDP half is
  still an open item by the addendum's own words ("the CDP harvest
  runs against the agent-managed Chromium, not Brave, until the
  remote-debugging-port custom profile/relaunch question is
  resolved"; A11 Brave default-profile CDP conflict unverified live;
  no CDP equivalent of focus_type, intent ledger, or V12 gate exists
  in cdp.mjs, whose operations are tabs, observe, act, harvest
  only). If instead the benchmark drives two Zen tabs as a
  controlled stand-in, that scope cut must be stated, because the
  acceptance test then does not cover the real clone windows. Either
  answer is acceptable; the ambiguity is not, because the two
  targets need different code paths and the benchmark worker cannot
  build until the target is named.
- G4 (one-line doc fix): V4 still promised in the design text.

Baseline numbers, assessed: the corrected baseline (8457997) is a
valid wall-time "before" comparator, not a validation of the new
path. Median act-now 5299ms for a 6-action click plus type batch on
pre-amend code, 3/3 X landed, normal Brave window, zero G28
fallbacks, order-to-overlay 326 to 333ms. It measures the OLD pixel
grounding path (no DOM calls, type_verified absent from every
envelope), so it says nothing about DOM harvest speed or the new
verification overhead; the post-amend re-run and the benchmark
itself are what measure those. It does carry one runbook lesson the
benchmark must keep: field focus and selection state at batch start
changes what typing does (Run 1 appended "about:blankX" while Runs
2 and 3 replaced with "X" alone), so each benchmark run must start
from a known composer state (empty, unfocused), exactly as the
baseline re-run procedure already notes. The crash-dialog Block
dismissal and Restore-bubble dismissal in the baseline setup also
show fresh-window setup is non-trivial; the benchmark runbook must
include it or use existing windows.

## Gap list (every remaining gap, with file, function, and fix)

- G1: scripts/zen_dom.py viewport_origin (lines 549-617), fallback
  branch lines 604-616. At factor other than 1 with window_size
  None, the CSS-px outer size is divided by the factor and the
  dimension closure refuses legitimate geometry (proven: factor 2,
  ZenDomError, gaps -923.5 and -580.0). Fix: only divide when
  window_size was explicitly given; when it is None use outer as-is,
  mirroring dom_act.ground_many_one_shot. Add a factor-2 no-bounds
  test next to the existing factor-2 test. Benchmark-gating.
- G2: scripts/zen_dom.py hit_check (line 660), focus_check (line
  693), arm_typed_flag (line 833), harvest (line 905), plus
  sent_bubble_contains (line 888, top-document leaf elements only).
  All use plain top-document querySelector or querySelectorAll with
  no shadow pierce (hit_check, focus_check) or no iframe walk
  (arm_typed_flag, harvest, sent_bubble_contains), while locate,
  field_value, and verify_typed use the find() helper. Proven live
  in code: honest-shim node run returns False for focused shadow and
  iframe inputs (control True). Fix: give hit_check and focus_check
  the same find() helper, returning the element with its owner
  document; run elementFromPoint in the owner document for frames
  and walk activeElement down through iframe documents as well as
  shadow roots; give arm_typed_flag and harvest the same iframe
  walk; extend sent_bubble_contains the same way or record it as
  top-document only. Fix the R7 node test shim to model querySelector
  honestly (return null for a shadow-hidden selector) so the test
  proves the live path. Alternative close: live-confirm the
  Messenger composer and send button are top-document and record
  iframe/shadow typing as an explicit scope cut. Benchmark-gating
  unless the live confirmation closes it.
- G3: improvements/worker-coord-click2-log.md (combined design and
  AMEND2 addendum) plus the benchmark runbook. Name the benchmark
  target browsers explicitly: two Zen tabs (addendum settlement) or
  the real clone1 Brave plus clone2 Chrome windows on ws2 (owner
  02:05 definition, live lane). If Zen tabs, state the scope cut (the
  acceptance test does not cover the real clone windows). If the real
  windows, the CDP half must close first (Brave default-profile CDP
  conflict verified live; CDP harvest against Brave; CDP equivalents
  of focus_type, intent ledger, and V12 gate, or an explicit
  statement of what verifies sends on that path). Benchmark-gating:
  no benchmark build until this line is written.
- G4: improvements/worker-coord-click2-log.md design section lines
  61 and 85 ("V4 caret position check", "V1+V2+V3+V4+V11 in one
  evaluate call per step"). V4 is dropped by the B18 decision in
  this round. Fix: one-line correction in the design text stating
  V4 is out of scope with the reason (caret forgeable by page JS,
  flag is the discriminator, caret-at-end would false-fail mid-text
  edits and IME composition).
- G5: scripts/cu.py BrowserAdapter.act (near line 2600) and the CLI
  act path (near line 2906). Both wire dom_hooks but do not forward
  type_x_ranges, so the band stays full-width on those production
  paths and R3a stays open in the fallback case (DOM check failed,
  band passes on wrong-field text). Fix: ground the selector and
  forward the range exactly as scripts/first_action.py lines 599-613
  do. Follow-up, not benchmark-gating while the benchmark drives
  through focus_type or first_action, both of which supply ranges.

## Independent verification (this reviewer, read-only, no code or test edits)

- Affected suites re-run 05:20 +07: `PYTHONPATH=../scripts:. python3
  -m unittest test_click2_redteam test_dom_act test_zen_dom
  test_pick4_fastpath test_type_verification test_first_action
  test_keyboard_preflight test_session_continuation test_fast_observe
  test_browser_start_warm test_endpoint_retention test_cdp_snapshot`
  from the tests dir: Ran 375 tests in 12.583s, OK. Node
  tests/cdp_validation.mjs: 3 ok lines (key preflight, adapter
  preflight, harvest).
- Full discover re-run (background, 05:16-05:20 +07):
  `PYTHONPATH=../scripts:. python3 -m unittest discover -p
  'test_*.py'` from the tests dir: Ran 1855 tests in 233.292s,
  FAILED (errors=4, skipped=17). 0 failures. The 4 errors are the
  pre-existing set (test_a11y_skeleton import, test_cursor_file g++
  rejects -std=c++26, test_perf_evidence x2 missing benchmark JSON),
  identical to the amend3 log claim. This matches amend3 exactly
  (1855 tests, 0 failures).
- Node honest-shim proof of the real focus_check and hit_check JS
  (scripts /tmp/c3r2-extract.py, /tmp/c3r2-node-proof.js): control
  top-document focused input True/True; honest shadow False/False;
  honest iframe False/False. Source extraction confirms neither
  function contains "pierce".
- Step-5 proof (script /tmp/c3r2-step5.py, real
  ZenSession.viewport_origin via the test fake): explicit size at
  factor 2 gives [2989, 930]; no window size at factor 2 raises
  ZenDomError (closure gaps -923.5, -580.0); factor-1 control gives
  [2749, 922].
- Step-2 safety checked by grep: all four dom_rect_to_image_point
  call sites convert ValueError to DomActError or ZenDomError.
- Step-4 caller audit by grep: the only before-giving callers are
  typed-input flows (dom_hooks type_check); cdp.mjs set_value is a
  separate programmatic path and is unaffected.

## Time log (wall-clock +07, elapsed from task start 05:08)

- 05:08 +00m task received; branch todolist-push, HEAD 9bcfb04.
- 05:09-05:13 +01-05m sources read in full (amend3 log, rt-synth,
  diff-assess, C12 probe log, baseline-a log, coord log design and
  addendum).
- 05:13-05:16 +05-08m diff reviewed per amend3 commit (e5c1c47,
  0367ec9, 0356389, d7b1579, 4110e72, 2dcd5d8, 5d49e51) and code traced
  live (zen_dom, dom_act, cu.py verification block and act paths,
  first_action fallback, cdp.mjs operations).
- 05:16-05:20 +08-12m independent proofs run (node honest-shim,
  step-5 factor-2, affected suites 375 OK, full discover started in
  background).
- 05:20-05:22 +12-14m full discover result read (1855 tests, 0
  failures, 4 pre-existing errors); HEAD moved to d086856 during the
  review, verified log-only (git diff 9bcfb04..HEAD, 2 files); R7
  review log read in full; disagreement on its scope boundary
  recorded with evidence.
- No 15-minute stall occurred at any point. No em dash or en dash in
  this file (checked by grep before commit). No ydotool. No personal
  info (owner name Pham Tuan only, as instructed for repo-facing
  text).

## Commit record

Review log: improvements/worker-click3-c3r2-review-log.md (this
file). Staged and committed with an explicit pathspec; push verified
with git ls-remote (hash in the coordinator copy of this log; this
worker's final report to the coordinator carries it).
