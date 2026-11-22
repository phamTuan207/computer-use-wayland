# Council round 3 review: AMEND4 fix pass (12 items)

Reviewer: clone2 (DOT 9 task 1, moved from clone1). Independent second
check: the coordinator runs a parallel council round 3 lane; I did not
read its output and did not copy any verdict. Every number below is from
my own runs on this machine, not from the AMEND4 log.

## Method

Worktrees under ~/workspace/tools/amend4-council3 (my own, separate from
the batch 10 task 2 agent's worktrees):

- wt-post at 0668327 (AMEND4 end state: item 12 cbab398 plus the item 4
  follow-up 0668327; the log commit 6f54a4e adds only the log file).
- wt-pre at 14fc139 (parent of the first AMEND4 commit cc964b2).
- wt-old12 at 0668327 with scripts/first_action.py replaced by the
  14fc139 version (item 12 failing-first check).
- wt-pre12fix at e05fc58 (parent of 0668327, contains items 1-12 but not
  the follow-up fix).

Environment: this VM, Python 3.12.3, node available, no hyprctl, no
browser. One setup gap, recorded honestly: fresh worktrees lack the
gitignored build artifacts native/wtype and native/keyboard-protocol.c/.h.
Without them the RT2 suite errors 42 times (wtype helper missing) and
the 23 test_wtype_native tests never run (setUpClass compile fails).
I copied the three files from the main checkout into my worktrees; with
them, every number below reproduces. This is a worktree setup gap, not
an AMEND4 defect.

## Headline numbers (mine)

RT proof tests (tests/test_click3_redteam2.py, from tests/,
PYTHONPATH=../scripts:. python3 -m unittest test_click3_redteam2):

- Pre-fix (wt-pre): Ran 49 tests, FAILED (failures=15). All 15 proof
  tests fail; the 2 redteam controls and 32 harness tests pass.
- Post-fix (wt-post): Ran 49 tests, FAILED (failures=4, errors=1).
  10 of 15 pass: F1, F5-source, F7-node, F7-python, F8, F9, F10, F11,
  F12, F13. The 5 that do not pass are F2 (error), F3, F4, F5-behavior,
  F6 (failures). Each is judged defective below, with my own proof.

Full discover (from tests/,
PYTHONPATH=../scripts:. python3 -m unittest discover -s . -p "test_*.py"):

- Pre-fix (wt-pre): Ran 1904 tests in 186.121s, FAILED (failures=16,
  errors=5, skipped=17). Failures: the 15 RT2 proof tests plus 1
  tc02 tesseract failure. Errors: 4 pre-existing (test_a11y_skeleton
  import, test_cursor_file setUpClass, test_perf_evidence x2) plus 1
  tc02 tesseract error.
- Post-fix (wt-post): Ran 1920 tests in 191.631s, FAILED (failures=5,
  errors=6, skipped=17). Failures: F3, F4, F5-behavior, F6, plus 1
  tc02 tesseract failure. Errors: the 4 pre-existing, plus F2, plus 1
  tc02 tesseract error.
- The log claims 1920 tests, failures=5, errors=6, skipped=17 in
  388.608s. The counts match mine exactly; the timing differs (faster
  here, same counts).
- Count note, 1920 vs 1927: this review's full discover collects 1920
  tests, matching the AMEND4 log exactly, while the independent batch
  10 task 2 re-verification measured 1927 at the same code state. The
  gap is the same systematic 7-test runner-collection difference
  already established: this review ran system python3 from tests/ with
  PYTHONPATH=../scripts:., the re-verification ran the venv python
  with -s tests and PYTHONPATH=/usr/lib/python3/dist-packages; the
  same 7 appears in the AMEND3 gap (1855 vs 1862). The failure counts
  agree (20 before the doubles fix, 5 after), so the gap is
  collection, not a counting error by either side.
- Net: 10 RT2 tests fixed; F2 moved from FAIL to ERROR (the refusal,
  by design); 16 new tests added by the pass, all passing; no
  regression anywhere (the post-fix problem set is a strict subset of
  the pre-fix set, modulo F2 changing category; the 2 tesseract
  environmentals appear identically in both runs).

## Per-item verdicts

### Item 1. GEOMETRY (F9/F10) - GO

Failing-first confirmed: both GeometryTests fail pre-fix (in the 15)
and pass post-fix (in the 10). The diff does what the log claims:
check_viewport_geometry gains factor=None and raises ZenDomError
without a positive factor; the exactness check (absolute == window +
moz*factor within 0.5 px) catches the factor-forgotten origin; the
containment check runs in screen px; viewport_origin and
ground_many_one_shot pass the window size as-is and pass factor
explicitly. The factor-2 test ([1863, 1176] returns [2989, 930];
[1500, 1000] raises) passes.

### Item 2. GATE TRAVERSAL (F8/F11/F12/F13) - GO

All four pass post-fix and fail pre-fix. The shared-JS constraint
holds: _FIND_JS (877 chars) contains none of the five marker
substrings (activeElement, elementFromPoint, textContent,
getBoundingClientRect, mozInnerScreenX), verified by direct import.
R7 faithful-shim, verified with my own node run (not the test's word
for it): on the faithful shim, pre-AMEND4 focus_check returns false
and hit_check returns false; post-AMEND4 both return true. The two
new TestFaithfulShadowShim tests pass. Frozen test_click2_redteam:
Ran 71 tests, OK.

### Item 3. BAND Y ANCHORING (F4) - GO for the fix; F4 test DEFECTIVE

The y_range contract is proven by the new tests, all passing
post-fix: test_band_stacked_field_with_y_range_must_not_verify,
test_band_stacked_field_with_y_range_reports_not_ok (both in
test_type_verification.py), and test_grounded_y_range_is_field_y_in_image_px
(G30: [1101.0, 1164.0]; None meta returns None). grounded_y_range
mirrors grounded_x_range in dom_act.py; type_y_ranges is threaded
through desktop_act and focus_type.

F4 (test_band_stacked_fields_low_click_with_x_range_must_not_verify)
is defective, proven independently. The test calls
cu._input_line_changed(old, new, 118, x_range=(100, 300)) with pixels
at y=126 and no y_range. Its own control requires pixels at y=110 to
verify. Both are 8 px from anchor 118, and the band without y_range
is symmetric anchor +- 12 (the function docstring states this limit
in plain words). No half value satisfies both assertions: half >= 8
is needed to include 110, half < 8 to exclude 126. The function
cannot distinguish the two pixels because it is never given the
field rect. The sound version of the test passes y_range=(100, 120).
Repair: add y_range=(100, 120) to the F4 call. No code change.

### Item 4. WIRING (F5) - GO for the fix; F5-behavior test DEFECTIVE

F5-source passes post-fix and fails pre-fix. The three call sites
verified by direct read: CLI act line 2986 passes
type_x_ranges=type_ranges and type_y_ranges=type_y_ranges;
CodeExecBackend.act line 2649 passes type_ranges; first_action
fallback lines 668 and 673 pass both ranges. BrowserAdapter.act does
not exist anywhere in scripts/ or tests/ (grep finds nothing); the
docstring fix to CodeExecBackend.act is correct.

F5-behavior (test_band_wrong_field_unwired_path_reports_ok) is
defective, proven independently. It calls cu.desktop_act DIRECTLY
(click (15,10), pixels x 0..11 at y=10, no ranges, no type_check)
and expects ok False. Threading ranges through CLI, CodeExec, and
first_action cannot affect a direct call. Pixels x 0..11 after a
click at x=15 are indistinguishable from legitimate empty-field
typing (text lands at the left edge, per _input_line_changed's own
docstring). The "or" branch (band-only unverified when no ranges are
supplied) would break the control test
test_click_type_text_in_input_line_verifies, which calls desktop_act
directly with no ranges and expects ok True via the band. I read that
control test and ran it: it passes post-fix. The worker was right not
to implement the "or" branch. Repair: rewrite the test to exercise a
wired path (supply ranges and assert they are honored), or assert at
the call-site level. No code change.

Dissent, recorded 2026-11-22: an independent re-verification (batch 10
task 2, docs/clone2-amend4-reverify-20261122.md) judged this same test
a TRUE negative, a design dispute between fail-closed (the test's
requirement) and best-effort (the implementation's choice). This review
disagrees at the desktop_act layer: the test calls cu.desktop_act
directly with no ranges, so no code fix can satisfy it without breaking
the passing control test test_click_type_text_in_input_line_verifies,
which calls desktop_act directly with no ranges and expects ok True
via the band. Adjudication must decide the fail-closed vs best-effort
question; this review does not settle it.

### Items 5-6. WINDOW BOUNDS + STALE ORIGIN (F2/F3) - GO for the fix; F2 and F3 DEFECTIVE

The fix is implemented and tested: _window_origin raises DomActError
without window_bounds (read in dom_act.py); _live_window_origin and
_check_window_not_moved are wired into ground_input and
ground_many_one_shot; locate_point also requires window_bounds. Three
new tests pass post-fix: test_ground_input_refuses_meta_without_window_bounds,
test_ground_input_refuses_stale_window_origin,
test_ground_input_accepts_matching_live_origin. ZenSession.live_window_origin
added in zen_dom.py (hyprctl clients -j by address, fallback
activewindow -j, returns None instead of raising).

F2 (test_region_fallback_readmits_raw_mozinner) is defective, proven
independently. It calls ground_input with a meta that has no
window_bounds and asserts a ground whose viewport_origin is not
[240, 8] AND whose point is within 10 px of the true point computed
with origin [2749, 922]. That origin is not derivable from the meta
(image_size [1920, 1080], region [0, 0, 3840, 2160], monitor_box
[0, 0, 3840, 2160]); only a live hyprctl re-read could supply it,
and the test's FakeWdSession has no live_window_origin method (grep
finds none in test_zen_dom.py), so no re-read is available. The
specified fix is to REFUSE, so the correct behavior errors the test,
which has no assertRaises. Repair: assert the refusal with
assertRaises(DomActError), or supply a live origin in the fake.
No code change.

F3 (test_stale_window_origin_accepted_silently) is defective, proven
independently. It asserts stale == [340, 108] AND that the point
mapped through that origin is within 10 px of the true point. The
mapped point is (323.0, 620.25); the true point is (1527.5, 1027.25);
the distance is 1271.4044399796628 px, confirmed in my run output.
No return value satisfies both assertions, because the point is
computed from the asserted origin. A raise would error the test (no
assertRaises). It also calls viewport_origin directly, so no
ground-time re-read can affect it, and the function cannot detect
staleness from its inputs (dom_origin [240, 8] is internally
consistent). Repair: rewrite to test the ground-time refusal (live
origin mismatch via ground_input), not a direct viewport_origin call.
No code change.

### Item 7. R10 FLAG REDESIGN (F6/F7) - GO for the fix; F6 DEFECTIVE

F7-node and F7-python pass post-fix and fail pre-fix. The redesign is in the diff and does what the log claims:
window.__agentCuTyped is gone; arm_typed_flag installs a listener
recording the field value at each trusted input event in a closure
variable, exposed through a locked getter (Object.defineProperty,
configurable false, no setter); typed_flag requires the recorded
value to equal the current value. The new node test
test_typed_flag_not_forgeable_via_window_property passes.

F6 (test_typed_flag_forgeable_by_page_script) is defective in two
ways, both proven independently by my own node run (same code as the
test, forge line guarded with try/catch):

1. The forge line `window.__agentCuTyped['#msg-input'] = true;`
   throws TypeError (Cannot set properties of undefined) because the
   arm no longer creates window.__agentCuTyped. My guarded run prints
   FORGE-THREW plus the result, so the test dies before its
   assertions run.
2. The value assertion assertNotEqual(out['value'], 'hello') can
   never pass: out['value'] is the verify JS result {value, editable},
   a plain value read (zen_dom.py verify_typed returns e.value), and
   the page script set the field value to 'hello'. My guarded run
   gives {"armed":true,"flag":false,"value":"hello"}.

The substantive flag assertion (assertFalse(out['flag'])) IS fixed:
flag is false with zero trusted input events. Repair: guard the forge
line and drop or replace the value assertion (assert the flag, not
the field value). No code change.

Disclosed residual, recorded honestly by the worker and confirmed as
real: a page that pre-defines the locked property name with a
non-configurable forged getter before arming would defeat the check.
That requires knowing the property name and running before the arm,
outside the R10 attacker model (a page script setting the value).
Not a verdict changer.

### Item 8. SET_VALUE SANITIZATION (F1) - GO

F1 fails pre-fix and passes post-fix (in the 15-failure list, then
in the 10 passing). The diff does what the log claims: both
read-back checks in the cdp.mjs set_value template now compare
e.value against the sanitized form (input strips CR/LF, textarea
normalizes CRLF and CR to LF), computed with String.fromCharCode so
no backslash doubling is needed. node cdp_snapshot.mjs passes ("all
cdp snapshot, redaction, fill, payload, no_after and scope
regressions pass"). Live browser confirmation of the HTML Standard
sanitization rule is still owed (no browser on this VM); the rule is
cited from the standard, not a live observation. Disclosed, not a
verdict changer.

### Item 9. SUPPLY-CHAIN TESTS - GO

All 3 new tests pass post-fix, and I read their bodies: they
genuinely pin the wiring, not just accept and ignore it.
test_grounded_x_range_is_field_x_in_image_px asserts the exact range
[86.0, 526.0] and None for an unmappable meta.
test_focus_type_forwards_grounded_ranges_to_act_fn uses a recording
wrapper and asserts the kwargs arrive as [[86.0, 526.0]] and
[[1101.0, 1164.0]]. test_fallback_with_window_observation_supplies_ranges
asserts first_action supplies both ranges on a window-scope
observation. No production code changed in this item, as claimed.

### Item 10. SNAPSHOT EVENT TEST - GO

The mirror assertion is in tests/cdp_snapshot.mjs (set_value from
'hello' to 'world' lands the value and fires input then change, in
that order). node cdp_snapshot.mjs passes. Test only, as claimed.

### Item 11. DESIGN-DOC FIXES - GO

Verified by grep on improvements/worker-coord-click2-log.md: exactly
1 "V4" mention remains in the whole doc, inside the B18 drop note
itself (line 61); step 4 reads "V1+V2+V3+V11". The tab-switch
protocol line is marked "**SUPERSEDED (2026-11-22, AMEND4 item 11)**"
(line 237) and kept visible; the benchmark target bullet records
clone1 Brave + clone2 Chrome on ws2 (line 242). No history rewritten.

### Item 12. ENVELOPE REDESIGN (CL1-SWEEP) - GO

The design is in the diff and does what the log claims: the envelope
now carries BOTH after (scope-matching, chainable) and after_screen
(verification only, non-chainable); _scope_after prefers the action
result's after when its scope matches, else takes a fresh capture in
the input observation's scope; a screen-scope input reuses the screen
capture. The scope check runs BEFORE the overlay attempt (a key/type
batch given a screen-scope observation is refused with path
'refused', before any session attempt or overlay acquire).

Failing-first confirmed with my own worktree (wt-old12): all 4 new
regression tests FAIL on the old first_action.py (failures=4) and
PASS on the new code (in the 68-test test_first_action run, OK):
test_session_after_is_scope_matching_not_screen,
test_fallback_after_is_scope_matching_not_screen,
test_after_without_result_after_captures_fresh_window,
test_screen_observation_key_batch_refused_before_overlay. The
pre-overlay refusal test asserts the session is never attempted and
the overlay is never acquired. Full test_first_action run: 68 tests
OK (including the item 9 ranges test).

### Item 4 follow-up. SESSION act_boundary FAKES (0668327) - GO

Verified independently: at e05fc58 (parent of 0668327, items 1-12
landed, follow-up not yet), test_session_continuation +
test_session_policy give Ran 28 tests, FAILED (failures=15,
errors=2), 17 problems, with the TypeError
"act_boundary() got an unexpected keyword argument 'type_x_ranges'"
visible in the failure traces. At 0668327 the same two modules give
Ran 28 tests, OK. The fix (both fakes accept **extra and forward it
to the real desktop_act) is a stale-fake fix, not a test weakening:
the assertions are unchanged. The log's claim that only the
AMEND4 commits touched scripts/cu.py since 14fc139 (items 3 and 4)
is consistent with the failure cause.

## The 5 defective proof tests: exact repairs needed (test-side only)

- F2 test_region_fallback_readmits_raw_mozinner: assert the refusal
  (assertRaises DomActError), or supply a live origin in the fake.
  The correct behavior errors this test as written.
- F3 test_stale_window_origin_accepted_silently: rewrite to test the
  ground-time refusal via ground_input with a live origin mismatch.
  The direct viewport_origin call with contradictory assertions
  cannot pass under any implementation.
- F4 test_band_stacked_fields_low_click_with_x_range_must_not_verify:
  add y_range=(100, 120) to the _input_line_changed call.
- F5-behavior test_band_wrong_field_unwired_path_reports_ok: rewrite
  to exercise a wired path (supply ranges), or assert at the
  call-site level. A direct desktop_act call with no ranges cannot be
  affected by range threading, and the "or" branch must not be
  implemented (it breaks the control test).
- F6 test_typed_flag_forgeable_by_page_script: guard the forge line
  (try/catch) and drop or replace the value assertion; keep the flag
  assertion, which is fixed.

## Overall verdict: AMEND (on the acceptance gate only)

Per-item verdicts: 12/12 GO. The code fixes are verified correct,
each with failing-first evidence, and the full discover shows no
regression.

The pass cannot close as 15/15: 5 RT proof tests still fail, and all
5 are proven defective as written (my own proofs above, not the
worker's claim alone). The AMEND4 worker was forbidden from editing
tests/test_click3_redteam2.py, so leaving them failing was the
instructed behavior; the rule is in the AMEND4 log,
improvements/worker-click3-amend4-log.md lines 20-22 ("Do NOT edit
tests/test_click3_redteam2.py or tests/test_click2_redteam.py
(acceptance tests; may only ADD tests). Do NOT weaken any test: a proof
test whose expectation is wrong is left failing for adjudication, with
the evidence in this log."). The repairs above are test-side only and no code
change is required. Until those 5 tests are repaired, the brief's end
state (0 failures, 4 pre-existing errors, 15/15 RT proof tests
passing) is not met.

Also outstanding, unrelated to the fixes: 1 failure + 1 error from the
environmental tesseract pair (tc02_controller, missing tesseract binary
on this VM, present identically pre and post); live-browser confirmation
still owed for the F1 sanitization rule and the 2-vision benchmark as a
whole; the item 7 pre-locked-property residual (outside the R10
attacker model).

Also outstanding, on the F5 finding itself: the CodeExec path remains
unwired by construction and the CLI path remains unwired without
--dom-selector, so the unwired path still verifies via the full-width /
click-anchored band by design. CodeExecBackend.act (cu.py:2615-2649)
sets type_ranges = None initially and only sets it when dom_session is
not None and dom_selector is not None; the code comment states the
code-exec allowlist does not expose ZenSession yet, so no code-exec
program can pass a session today and type_ranges is always None on
that path. CLI act (cu.py:2945-2986) grounds the ranges only when
--dom-selector is supplied; otherwise the batch keeps the full-width /
click-anchored band, per the code comment. The F5-behavior test
faithfully reproduces that production unwired path, and the repair
above (rewrite the test to exercise a wired path) means after repair
nothing tests the unwired path at all. The dissent is recorded in the
item 4 section: the independent re-verification judged F5 a true
negative, this review judges the test defective at the desktop_act
layer, and the fail-closed vs best-effort choice is left to
adjudication.

Patch vs remove vs redesign (the worker's summary, checked against
the diffs): patch items 1, 2, 3, 4, 8; patch with a removal items
5-6 and 11; redesign items 7 and 12; tests only items 9 and 10.
The characterization holds. The two redesigns are justified: the
window-property flag is forgeable by construction (any writable
window state), and the after-capture was screen-scoped by
construction (first_action.py hardcoded observe_screen).

## Evidence locations

- AMEND4 log: improvements/worker-click3-amend4-log.md (6f54a4e,
  716 lines), read in full.
- My worktrees: ~/workspace/tools/amend4-council3/wt-post (0668327),
  wt-pre (14fc139), wt-old12, wt-pre12fix (e05fc58).
- Logs: ~/workspace/tools/amend4-council3/rt2-post.log (49 tests,
  failures=4, errors=1, re-run in this fix pass),
  /tmp/discover-post2.log (1920 tests, failures=5, errors=6),
  /tmp/discover-pre.log (1904 tests, failures=16, errors=5),
  /tmp/cdp-post.log (node cdp_snapshot.mjs pass),
  ~/workspace/tools/amend4-council3/sess-pre12fix.log (28 tests,
  17 problems at e05fc58, re-run in this fix pass).
