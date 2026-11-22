# CLICK3-C2R2 review log: council round 2 on the AMEND3 surgical fix pass

Worker: CLICK3-C2R2 (council reviewer 2, independent; did not write
AMEND2 or AMEND3; focus: test quality and the verification chain, not
fix mechanics). Coordinator: COORD-CLICK-2. Owner: the owner
(repo-facing name). Branch: todolist-push, HEAD 9bcfb04 at review.
Task start: 05:08 +07 22/11/2026. All times wall-clock Asia/Ho_Chi_Minh
+ elapsed from task receipt. Standing rules: full access, no em dash
(U+2014) or en dash (U+2013) anywhere including quoted window titles,
never ydotool, no personal info in repo files, log everything.
Review only: no code or tests edited by this worker.

Sources read first, in full:
- improvements/worker-click3-rt-synth.md (34-entry checklist, dd45231).
- improvements/worker-click3-diff-assess.md (910e471).
- improvements/worker-click3-amend3-log.md (HEAD 9bcfb04).
- improvements/worker-click2-c12probe-log.md (C12 verdict
  WINDOW-RELATIVE).

## Time log

- 05:08 +00m task received; branch todolist-push, HEAD 9bcfb04
  confirmed; git status clean except 4 untracked other-worker files,
  left untouched.
- 05:08-05:10 +00-02m all four sources read in full; amend3 code diff
  (c01d4a2..9bcfb04, scripts + tests, 11 files, +399/-121) read in full.
- 05:09 +01m full discover started in background (pid 24473).
- 05:10 +02m grounded_x_range math checked by direct call: correct.
- 05:10-05:11 +02-03m node probes with faithful shims: focus_check
  fails shadow-nested and iframe-nested inputs; field_value and
  verify_typed traverse same-origin iframes and fail closed
  cross-origin.
- 05:11 +03m targeted re-run: 8 tests OK (R1, factor-2, R10, iframe,
  R3a x2, cdp_snapshot x2).
- 05:11 +03m fail-before in temp worktree at c01d4a2 (new test files
  copied onto pre-amend3 code): 6/6 new tests fail. Worktree removed.
- 05:12 +04m affected suites re-run: 373 tests, all OK; cdp_validation
  3 ok lines.
- 05:15 +07m full discover finished: Ran 1855 tests in 218.193s,
  FAILED (errors=4, skipped=17), 0 failures. The 4 errors are the
  pre-existing set (see below).
- 05:15 +07m R7 independent re-verification (step 8): old
  strict-equality code returns False on the corrected fixture, new
  code returns True; R7ShadowTests 3/3 OK.
- 05:16 +08m range composition and hygiene checks (dashes, ydotool,
  diff-check) done; review written.
- No 15-minute stall occurred at any point.

## What the reviewed range actually is

The task names the range 4b7d6ac..9bcfb04: 40 files, +7044/-317. Most
of that is NOT amend3. Its composition:
- 4b7d6ac..c01d4a2 (AMEND2 verbatim groups + logs): 38 files,
  +6376/-303.
- c01d4a2..9bcfb04 (amend3 fixes + logs): 13 files, of which the fix
  delta in scripts + tests is 11 files, +399/-121. The other two
  files are the amend3 log itself and one unrelated docs-only commit
  (8457997, coord baseline log, 128 lines, no code).
- This review covers the amend3 fix delta in full, and the AMEND2
  content only through the diff-assess verdict (KEEP MOST) plus my own
  re-runs. Limit, stated plainly: I did not re-verify AMEND2
  byte-for-byte against its original uncommitted tree (that tree no
  longer exists uncommitted); the group commits match the
  diff-assess file list and counts, and my re-runs confirm the
  resulting tree behaves as assessed.

## Per-fix verdicts: does the new test attack the substance?

The round-1 failure mode was a test that passes while the finding
survives. I re-ran every new failing-first test myself, and I ran
all 6 of them against pre-amend3 code in a temp worktree to confirm
they fail before the fix. Result: 6/6 fail before, 6/6 pass after.
The substance verdicts below are per fix, not per test file.

### Step 1, cdp.mjs set_value (regression): SUBSTANTIVE, PASS

The fix captures oldValue before the native-setter write and
dispatches input/change only when the value changed; setter write
and read-back stay unconditional, so the R2 fix is preserved. My
re-run: `python3 -m unittest test_cdp_snapshot` from the tests dir,
Ran 2 tests, OK. The regression DIFF-ASSESS proved by fail-before
(passes on HEAD, fails on the AMEND2 tree) is gone. No weakness
found in this step.

### Step 2, R1 fallback deletion + test rewrite: SUBSTANTIVE, PASS

The fallback is deleted from dom_rect_to_image_point (fail closed,
raises ValueError) and the R1 test now goes through the real
zen_dom.viewport_origin code (FakeWdSession runs the inherited real
method, it does not reimplement it): window (2509, 914) + mozInner
(240, 8) = (2749, 922), point (351.7, 734.4), and the raw pair
(240, 8) must raise. My re-run: the test passes. Fail-before: it
FAILS on pre-amend3 code (the fallback rescued the raw pair). This
is the substance: the test now proves the corrected chain, not the
net. Caveat, accepted: the test still runs against a fake session,
not live Zen; the live leg is the C12 probe itself (one real click
at candidate B, focus confirmed), which this test encodes exactly.
No live driving was done by this reviewer, and none was needed for
this step.

### Step 3, R3a band x-range: SUBSTANTIVE ON THE CONSUMPTION SIDE, UNPROVEN ON THE SUPPLY SIDE, AMEND

Consumption side, verified: the two new tests attack the substance.
12 changed pixels in another field on the same line, outside the
target x-range, must not verify (old full-width band returned True
for exactly this shape, proven by DIFF-ASSESS); the same pixels
inside the range must verify. My re-run: both pass. The
desktop_act-level test asserts ok False with error_code
type_unverified for the wrong-field shape and ok True for the
in-range control. Fail-before: both ERROR on pre-amend3 code (the
old functions take no x_range parameter). The band narrowing itself
is real code, correctly implemented: _input_line_changed crops to
(x0, y0, x1, y1) when a range is given, clamps to the image, returns
False on an empty range and None on an unparseable one, and the
desktop_act pairing pads a short ranges list with None (full width)
rather than misaligning groups.

Supply side, NOT proven by any test: no test asserts that
focus_type forwards the computed range to act_fn (the test FakeAct
swallows type_x_ranges in **kw and ignores it), no test pins
grounded_x_range output, and no test asserts first_action supplies
ranges. A focus_type that computed the range and dropped it, or a
grounded_x_range that always returned None, would pass every suite
today. I checked the math myself by direct call (probe geometry:
rect width 440 CSS px, point [351.7, 734.4], meta 1200x757 over
region [2509, 914, 1863, 1176] gives [209.99, 493.41], exactly
point +/- half width in image px), so the computation is correct as
written; it is the absence of a test pinning it that is the gap.
See fix A3 below. This gap is also why the two unsupplied call
paths (gap G2) stay silent: nothing anywhere asserts ranges arrive.

### Step 4, R10 typed flag whenever before is given: SUBSTANTIVE, PASS

The new test is the exact attack DIFF-ASSESS used: field starts
empty, a page script sets the expected text with no keystrokes,
before='' must NOT verify; then a trusted input event on the same
shape DOES verify. My re-run: passes. Fail-before: FAILS on
pre-amend3 code (old code consulted the flag only when
before == expected). Both fakes (test_zen_dom FakeWdSession,
test_dom_act FakeDomSession) now model the flag faithfully: True
only on a recorded trusted input event, a bare value change leaves
it clear. That fake correction matters: the old fake shape (any
value change since arming counts as typed) made the fake blind to
exactly this attack, the same failure mode as round 1. Recorded
contract change, accepted: verify_typed now requires the flag
whenever before is given, so a caller that passes before without
arming gets False even for genuinely typed text. That matches
handoff step 4 exactly, dom_act always arms via dom_hooks, and
cdp.mjs set_value (the programmatic path) is unaffected.

### Step 5, factor-2 geometry: SUBSTANTIVE, PASS

The test asserts the absolute origin [2989, 930] at factor 2
(window [2509, 914], screen-px size [3726, 2352], mozInner
(240, 8)) and asserts refusal of impossible CSS geometry
([3000, 2000] screen px = [1500, 1000] CSS px, closure
240 + 1615 = 1855 > 1500). My re-run: passes. Fail-before: FAILS
on pre-amend3 code (the old check compared against the screen-px
size and let the impossible geometry through). The test
discriminates the fix. The disclosed conservatism (containment
compares a screen absolute origin against a CSS-px window rect, so
at factor > 1 it can only refuse, never accept a wrong origin) is
real but bounded: the origin sits mozInner * factor from the window
origin, well inside that rect for any real sidebar geometry. The
code and the log both disclose it. Accepted as written.

### Step 6, iframe traversal in field_value and verify_typed: SUBSTANTIVE FOR THE TWO METHODS, HALF-USABLE ON THE REAL PATH, AMEND

The two methods now use the same find() helper as locate()
(shadow pierce, then same-origin iframe traversal with
cross-origin try/catch). My own node probes, running the REAL
captured JS against faithful shims (not the repo fakes):
- same-origin iframe input: field_value returns "hello",
  verify_typed returns the value object (verifies).
- cross-origin iframe (contentWindow.document access throws):
  field_value returns null, verify_typed returns null (fails
  closed, never a wrong pass).
The new test asserts contentWindow in both scripts and reads the
value. Fail-before: FAILS on pre-amend3 code. The two methods are
closed in substance.

But the real call path is half-usable, because the gate that runs
before every type group, focus_check, still cannot see these
targets (gap G1 below). A same-origin iframe input that locate()
grounds and field_value can now read still cannot be typed into
through dom_act.focus_type: focus_check returns False and the batch
refuses before any keystroke. That is fail-closed, not a
false-pass, but step 6 does not deliver a working typed-input path
for iframe targets until focus_check is fixed with it.

### Step 7, duplicate import os: TRIVIAL, PASS

One `import os` deleted from scripts/zen_cli.py (kept line 92,
deleted line 96). Verified: exactly one `import os` remains, and
every suite that imports zen_cli passes (full discover green).

## My independent re-runs (exact commands, outputs, counts)

All run on HEAD 9bcfb04, from the tests dir unless stated, with
PYTHONPATH=../scripts:. except where noted.

- Targeted new tests + snapshot regression (8 tests):
  `python3 -m unittest
  test_click2_redteam.R1ConversionTests.test_raw_moz_inner_screen_origin_must_land
  test_zen_dom.TestDomHelpers.test_viewport_origin_factor_two_geometry
  test_zen_dom.TestDomHelpers.test_verify_typed_js_set_without_keystrokes_must_not_verify
  test_zen_dom.TestDomHelpers.test_field_value_and_verify_typed_traverse_iframes
  test_type_verification.TypeVerification.test_band_wrong_field_with_rect_range_must_not_verify
  test_type_verification.TypeVerification.test_band_wrong_field_with_rect_range_reports_not_ok
  test_cdp_snapshot`
  Result: Ran 8 tests, OK (4.436s).
- Affected suites (amend3 step 9 set), each `python3 -m unittest <suite>`:
  test_click2_redteam 71/71 OK; test_dom_act 13/13 OK; test_zen_dom
  38/38 OK; test_pick4_fastpath 28/28 OK; test_type_verification
  59/59 OK; test_first_action 63/63 OK; test_keyboard_preflight
  32/32 OK; test_session_continuation 11/11 OK; test_fast_observe
  40/40 OK; test_browser_start_warm 11/11 OK;
  test_endpoint_retention 7/7 OK. Total 373, all OK. These match
  the amend3 log counts exactly.
- `node tests/cdp_validation.mjs` from the repo root: 3 ok lines
  (key preflight, adapter preflight, harvest). (Note: run from the
  tests dir it fails on the path; the repo-root invocation is the
  correct one.)
- Full discover: `PYTHONPATH=../scripts:. python3 -m unittest
  discover -p 'test_*.py'` from the tests dir, background pid 24473.
  Result: Ran 1855 tests in 218.193s, FAILED (errors=4, skipped=17),
  0 failures. The amend3 claim (1855 tests, 0 failures, 4
  pre-existing errors, 17 skipped) is CONFIRMED by my own run.
  The 4 errors are exactly the pre-existing set:
  test_a11y_skeleton import error, test_cursor_file setUpClass
  (g++ rejects -std=c++26), test_perf_evidence x2
  (FileNotFoundError docs/benchmarks/r5_cdp_aggregate.json).
- Fail-before (temp worktree at c01d4a2, the 4 new test files copied
  onto pre-amend3 code, same 6 tests): Ran 6 tests, FAILED
  (failures=4, errors=2). Breakdown: R1 FAIL, factor-2 FAIL, R10
  FAIL, iframe FAIL, R3a unit test ERROR, R3a desktop_act test
  ERROR (old functions take no x_range parameter). All 6 new tests
  fail before the fix and pass after it. Worktree removed after.
- Hygiene: `git diff --check c01d4a2..9bcfb04 -- scripts tests`
  clean; no U+2014 or U+2013 and no ydotool in the amend3 scripts +
  tests diff (checked by grep).

## My own probes (evidence for the gaps)

### P1. focus_check cannot pass for shadow-nested or iframe-nested inputs in a real browser

The real focus_check JS (captured with the repo's own _capture_js
helper) contains no pierce and no contentWindow: it starts with
`const e=document.querySelector("#msg-input")` and returns False
when e is null. In a real browser document.querySelector does NOT
pierce shadow roots, so for a shadow-nested input e is null and the
shadowRoot.activeElement walk below it is unreachable dead code:
the walk only matters when e is shadow-nested, which is exactly
the case querySelector cannot find. I ran the real JS under node
against faithful shims:
- shadow-nested (querySelector returns null, host shadowRoot
  activeElement is the focused inner input): focus_check = false.
- iframe-nested (querySelector returns null, input inside a
  same-origin iframe document): focus_check = false.
- top-document control (querySelector returns the focused input):
  focus_check = true.
So focus_check fails closed for exactly the targets step 6
unblocked. This is the round-1 failure mode recurring: the redteam
test test_focus_check_shadow_host_false_negative passes only
because its shim stubs document.querySelector to return the inner
element directly, which a real browser never does for a
shadow-nested element. The test proves the activeElement walk, not
the end-to-end focus_check for shadow targets.

### P2. R7 re-verification (amend3 step 8, fresh reviewer job)

Done by this reviewer, independently. On the corrected fixture
(host carries shadowRoot with the inner input as activeElement):
old strict-equality focus_check JS returns false, new code returns
true. R7ShadowTests: Ran 3 tests, OK. The walk half of R7 is
confirmed: the fixture models a focused input inside a shadow root
and the old code fails it. The lookup half is NOT confirmed by
that fixture (see P1): the fixture is unfaithful on the lookup,
so the R7 claim stays half-proven until the shim is fixed.

### P3. grounded_x_range math is correct as written

Direct call with probe geometry gives [209.99, 493.41], exactly
point +/- half the rect width in image px. The computation is
right; what is missing is a test pinning it (see fix A3).

## Recorded gaps: verdict, plainly

### G1. focus_check still uses a top-document querySelector: NOT ACCEPTABLE TO LEAVE AS-IS

It does not undermine the R3a closure (different mechanism: the
band is about the x-range, focus_check is about the focus gate).
It DOES undermine the R9 / step-6 closure on real call paths: an
iframe-nested or shadow-nested input that locate() grounds and
field_value()/verify_typed() can now read still cannot be typed
into through the DOM-first flow, because the focus gate runs
before every type group and returns False for it. The failure is
fail-closed (the batch refuses, nothing wrong is typed or clicked),
so this is not a false-pass and not a BLOCK. But the amend3 log
records it as a known gap while the R9 shadow claim still reads as
closed, and the redteam test that supposedly proves the shadow
walk passes only through an unfaithful shim. That is the exact
defect class this council round exists to catch. Fix A1 below.

### G2. cu CLI act path and CodeExecBackend.act do not supply type_x_ranges: NOT ACCEPTABLE TO LEAVE UNQUALIFIED

Verified in code: scripts/cu.py CodeExecBackend.act (line ~2587)
wires focus_check/type_check via dom_hooks but never computes or
passes type_x_ranges; the CLI act branch (line ~2890) opens the DOM
hooks via open_dom_hooks and likewise never grounds the rect or
passes ranges. Only dom_act.focus_type and first_action supply
them. Consequence, stated plainly: on those two paths the band
stays full-width, so R3a survives there whenever no DOM session is
present (the band is then the sole basis and ok True still follows
it, exactly the RT R3 shape). When a DOM session IS present, the
DOM value check is the sufficient check and the band does not
decide, so the amend3 log's justification ("they still get the DOM
value check") is true only in that case, not in general. The
2-vision benchmark path (dom_act / first_action) is covered, so
this does not block the benchmark; but the unqualified amend3 claim
"R3a closed in substance" is not true for all production call
paths. The fix is small and mirrors first_action exactly (fix A2
below). Leaving it means the next council round re-finds it.

### G3. Supply-side test gap (part of step 3): NOT ACCEPTABLE TO LEAVE

No test asserts focus_type forwards the computed range, no test
pins grounded_x_range, no test asserts first_action supplies
ranges. The R3a closure on the covered paths rests on untested
wiring. Fix A3 below.

## Accepted, no action

- B18 V4 caret position (unbuilt): the amend3 reasoning is sound.
  A caret offset adds no discrimination beyond the V11
  trusted-input-event flag that step 4 now enforces (a page script
  can set el.value and then set selectionStart in one extra line,
  while isTrusted cannot be forged by page JS), and requiring
  caret-at-end would false-fail legitimate mid-text edits and IME
  composition. V4 stays a UX signal, not a verification signal.
- B11 Mantis numbering: explicitly deferred in the coord-log
  addendum; a design deferral, not code this worker should build.
- Step 5 containment conservatism at factor > 1: disclosed in code
  and log, can only refuse, bounded. Accepted.
- The C12 AT-SPI cross-check drop: correct as specified. Probe run
  3 proves Zen is not on the AT-SPI bus and run 2 proves
  chrome-context eval is blocked without a Zen restart that must
  not be done. The dimension-closure + containment substitute is
  validated by the probe's grim pixel-edge measurement. No new
  AT-SPI attempt is owed.
- RT-SYNTH items verified done by the assessment and untouched by
  amend3 (R2/R4/R5/R6/R7/R8/R11/R12/R13 in substance, B1 wiring, B2
  size-mismatch None, B3 click-only anchors, B4 off-line false-fail
  documented, B5 clean CLI failure, B6 trailing-whitespace
  normalization, B7 relay band test, B16 per-group bands, B17
  terminal-None DOM pass, B19 MAP relabel, B14 one-shot harvest):
  no new evidence against any of them was found in this review.
  My re-runs confirm their suites green.

## Verdict: AMEND

The seven amend3 fixes are real and their new tests attack the
substance: 6/6 new tests fail before and pass after, the full
discover claim is confirmed by my own run (1855 tests, 0 failures,
4 pre-existing errors, 17 skipped), and the step-1 regression is
gone. But two recorded gaps are not acceptable to leave, and one
unrecorded test gap hides them:

### Fix A1. focus_check must use the same find() helper (scripts/zen_dom.py focus_check, ~line 693)

Reuse the pierce + same-origin iframe traversal already built for
field_value/verify_typed in step 6 (shadow pierce, then iframe
walk with cross-origin try/catch), so the focus gate can see the
same targets locate() grounds. Then fix the redteam node test
(tests/test_click2_redteam.py
test_focus_check_shadow_host_false_negative) to use a faithful
shim: document.querySelector returns null for the shadow-nested
input (and the host for a host selector), so the test proves the
lookup plus the walk, not the walk alone. Add an iframe-nested
focus_check node test with the same faithful shape (top
querySelector null, input inside a same-origin iframe document,
focused: must return True; cross-origin: must return False).
Failing-first: the new tests must fail on the current code (P1
proves they will: false today) and pass after the fix.

### Fix A2. Supply type_x_ranges on the two unsupplied call paths

- scripts/cu.py CLI act branch (~line 2890): after open_dom_hooks
  succeeds, best-effort ground_input(dom_session, meta, selector)
  + grounded_x_range, pass type_x_ranges=[x_range] in act_kwargs;
  on any exception keep the full-width band exactly as before
  (mirror first_action.py lines ~602-615, including the
  never-fail-the-batch except).
- scripts/cu.py CodeExecBackend.act (~line 2587): same, using the
  dom_session + dom_selector + meta already in scope; when no
  dom_session is present there is nothing to ground from, so the
  full-width band stays and the envelope must keep recording that
  basis (it already does via type_verified_basis).
Both are best-effort: grounding never fails the batch.

### Fix A3. Pin the R3a supply chain with tests

- tests/test_dom_act.py: a focus_type test whose FakeAct captures
  kwargs and asserts type_x_ranges equals the grounded_x_range of
  the fake session field (not None, and equal to the range computed
  from the ground evidence). Today the FakeAct ignores the kwarg,
  so this test must be written to fail if focus_type drops it.
- tests/test_dom_act.py or tests/test_type_verification.py: a
  grounded_x_range unit test on the probe geometry (rect width 440
  CSS px, point [351.7, 734.4], meta 1200x757 over [2509, 914,
  1863, 1176] gives [209.99, 493.41]) plus the None-meta case
  returns None.
- tests/test_first_action.py: a test asserting the fallback batch
  passes type_x_ranges when the DOM hooks open with a grounded
  rect (or at least that the kwarg reaches desktop_act).
After A1-A3, re-run the step-9 set (373 tests) + full discover and
record the counts; the counts must stay 1855 + new tests, 0
failures, same 4 pre-existing errors.

No other fix is required. In particular, do NOT redo AMEND2, do NOT
rebuild the R1/R3a/R10 tests (they are substantive as written), and
do NOT revive the AT-SPI cross-check.

## Commit record

Review file: improvements/worker-click3-c2r2-review-log.md (this
file). Staged and committed with an explicit pathspec; push verified
with git ls-remote (hash in the coordinator copy of this log; this
worker's final report carries it). No other file touched. The 4
untracked other-worker files were left untouched. Temp worktree
/tmp/c2r2-before was removed after the fail-before check. No em
dash or en dash in this file (checked by grep before commit). No
ydotool. No personal info (owner name the owner only, as instructed
for repo-facing text).
