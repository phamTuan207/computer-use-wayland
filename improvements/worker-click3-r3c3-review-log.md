# CLICK3-R3C3 log: round-3 council review of the AMEND4 fix pass

Worker: CLICK3-R3C3 (council reviewer 3, round 3). Coordinator: COORD-CLICK-3.
Owner: the owner (repo-facing name). Branch: todolist-push.
Task start: 06:59 +07 22/11/2026 Asia/Ho_Chi_Minh (first measured wall
clock on this VM 06:59:58). All times below are Asia/Ho_Chi_Minh wall
clock plus elapsed from task receipt. HEAD reviewed: 8008662
(click3-codex-discuss). Base: f0ddd41 (RTR2, 13 findings F1-F13, 15
failing proof tests). Standing rules: full access, no em dash (U+2014)
or en dash (U+2013) anywhere, never ydotool, no personal info in repo
files, log everything with wall-clock + elapsed. I did not write
AMEND4; this is an independent review. I edited no production code and
no proof test; the only file I write is this log.

## Method

Failing-first per item, independently re-derived, not trusted from the
AMEND4 log: the 15 RT2 proof tests run at base (worktree
/tmp/r3c3-base at f0ddd41, with the ignored native/wtype helper copied
in so the harness behaves the same) and at HEAD, plus each item's own
new tests run at HEAD and against the pre-fix tree (HEAD test files
copied into a pre-fix worktree where the test did not exist at base).
Defective-test claims were re-proven with my own checks, not taken
from the driver's word: an F4 symmetry script, a guarded-forge node
run for F6, and reading the contradicting control test for F5.

## Baseline and HEAD, RT2 proof tests (exact commands)

- Base, /tmp/r3c3-base/tests, PYTHONPATH=../scripts:.
  `python3 test_click3_redteam2.py`: Ran 49 tests in 3.907s, FAILED
  (failures=15). The 15 failures are exactly the RT2 proof tests; 2
  redteam controls pass; 32 inherited DesktopPreflight harness tests
  pass. This matches the RTR2 log's baseline exactly.
- HEAD, tests/, same command: Ran 49 tests in 4.053s, FAILED
  (failures=4, errors=1). Still failing at HEAD, all judged defective
  by the driver and re-verified defective below:
  - FAIL test_band_stacked_fields_low_click_with_x_range_must_not_verify (F4, item 3)
  - FAIL test_band_wrong_field_unwired_path_reports_ok (F5 behavior, item 4)
  - FAIL test_stale_window_origin_accepted_silently (F3, items 5-6)
  - ERROR test_region_fallback_readmits_raw_mozinner (F2, items 5-6)
  - FAIL test_typed_flag_forgeable_by_page_script (F6, item 7)
- Fixed at HEAD (fail at base, pass at HEAD): F1 set_value newline,
  F9 factor-2 false refusal, F10 factor-forgotten origin, F11 harvest
  iframe, F12 nested iframe, F13 iframe in shadow root, F7 sticky
  node, F7 sticky python, F8 arm in iframe, F5 source test
  (codeexec/CLI supply x_ranges). 10 of 15.
- Proof test file untouched: `git diff f0ddd41..HEAD -- tests/test_click3_redteam2.py`
  is empty. Frozen test_click2_redteam.py also untouched. No test
  weakened: the only removed assert line in any test diff is the old
  factor-2 geometry expectation, rewritten production-realistically
  (same expected origin [2989, 930], size input changed from screen-px
  [3726, 2352] to Hyprland-logical [1863, 1176], plus a None-branch
  case and a [1500, 1000] refusal case); the only other removed lines
  are fake-signature lines from the follow-up. No em dash or en dash
  in the whole AMEND4 diff (scripts + tests + design doc): 0 and 0.

## Item 1. GEOMETRY (F9/F10), cc964b2 - GO, patch

- Failing-first: both F9/F10 fail at base, pass at HEAD (in the 49-test runs above).
- Independent checks: `check_viewport_geometry(..., factor=None)`
  raises ZenDomError ("viewport factor is required"); with factor=2
  the true origin [2989, 930] is returned. Consistent units confirmed
  in code: closure in CSS px, containment in screen px
  (absolute vs window + size*factor).
- Patch, not rewrite (agree with driver): the geometry chain
  (Hyprland origin + mozInner * factor) is correct; only the validator
  mixed units and the size branch divided. The only removal is the
  silent factor-1 default, which is the F10 hole.
- F10 note, confirmed: the F10 inputs are self-consistent at factor 1,
  so no pure consistency check can refuse them; the refusal comes from
  the fail-closed factor requirement. Sound.

## Item 2. GATE TRAVERSAL (F8/F11/F12/F13), c1ea773 - GO, patch

- Failing-first: all 4 fail at base, pass at HEAD (in the 49-test runs above).
- Shared helper confirmed in code: `_FIND_JS` (pierce + framesOf +
  find, depth cap 5, frames detected by contentWindow presence,
  cross-origin fail-closed) is used by locate, hit_check, focus_check,
  field_value, verify_typed, arm_typed_flag, typed_flag,
  sent_bubble_contains and harvest (zen_dom.py lines 580, 833, 869,
  890, 914, 969, 1012, 1036, 1076).
- R7 faithful-shim re-run: `test_zen_dom.TestFaithfulShadowShim` (2
  tests) passes at HEAD; with HEAD's test file copied into the base
  worktree, all 3 targeted tests (2 shim + the item-7 flag test) FAIL
  on the old code (Ran 3 tests, FAILED failures=3). The old code fails
  the faithful shim; the new code passes it. The frozen R7 test
  (unfaithful shim) still passes (in the suite runs below).
- Patch, not rewrite (agree with driver): the find/pierce/traverse
  shape is right; it was applied inconsistently. Unifying on one
  shared helper removes the inconsistency without a new architecture.

## Item 3. R3a BAND ANCHORING (F4), 62b740e - AMEND (test repair), patch

- Failing test: test_band_stacked_fields_low_click_with_x_range_must_not_verify.
- The FIX is proven and sound. Driver's own new tests fail at base and
  pass at HEAD: test_band_stacked_field_with_y_range_must_not_verify
  and test_band_stacked_field_with_y_range_reports_not_ok error on the
  base tree (Ran 2 tests, FAILED errors=2) and pass at HEAD; the
  grounded_y_range unit test errors at base and passes at HEAD. My own
  symmetry check (/tmp/r3c3-f4-check.py, run 07:02):
  `_input_line_changed` with no y_range returns True for pixels at
  y=126 AND at y=110; with y_range=(100, 120) it returns False for
  y=126 and True for y=110. The y_range contract works when supplied.
- The RT2 TEST is defective, independently confirmed. It calls
  `_input_line_changed(old, new, 118, x_range=(100, 300))` with
  pixels at y=126 and no y_range; the control uses y=110. Both are 8px
  from anchor 118, so any symmetric band [118-h, 118+h] containing 110
  needs h>=8 and then also contains 126; h<8 excludes both. Only the
  field's y-range (not passed) can distinguish them. No code change can
  make this test pass without breaking its own control.
- Repair required (test repair, for adjudication; I do not edit proof
  tests): add y_range=(100, 120) to the test call, as the driver
  proposes. Then the test asserts the fixed contract instead of an
  impossible one.
- Patch, not rewrite (agree with driver): the band design is sound;
  only its y anchor was wrong (click point instead of field rect).

## Item 4. R3a WIRING (F5), 72120aa - AMEND (test repair), patch

- Failing test: test_band_wrong_field_unwired_path_reports_ok (behavior test).
- The FIX is proven and real, not a string cheat. The F5 source test
  fails at base (CodeExecBackend.act never supplies type_x_ranges) and
  passes at HEAD. I read CodeExecBackend.act at HEAD: it genuinely
  grounds the field via dom_act.ground_input and threads
  type_x_ranges/type_y_ranges to desktop_act (best-effort, guarded by
  try/except), and the CLI act line passes both ranges. The ranges
  only exist when dom_session + dom_selector are given; without a
  session the path still runs the full-width band, which is the
  residual the behavior test attacks.
- The BEHAVIOR TEST is defective, independently confirmed. It calls
  cu.desktop_act directly (click (15,10), pixels x 0..11 at y=10, no
  ranges, no type_check) and expects ok False. The control test
  test_click_type_text_in_input_line_verifies (test_type_verification.py:120)
  calls desktop_act directly with the same shape (click (10,10) +
  type, no ranges, no type_check, text at the left of the line) and
  expects ok True, type_verified True, basis input-line-band. The two
  tests demand opposite outcomes on indistinguishable inputs: pixels
  at the left edge of the clicked line are exactly what legitimate
  empty-field typing produces. Threading cannot affect a direct call.
- The driver's decision is correct: implement threading, do NOT
  implement the "or" branch (band-only unverified when no ranges
  supplied), because it breaks the control test and the documented
  empty-field contract.
- Repair required (test repair, for adjudication): rewrite the behavior
  test to go through a wired path (CodeExecBackend.act with
  dom_session/dom_selector, or the CLI act path) where ranges are
  supplied and wrong-field pixels must not verify, or drop the
  direct-call expectation. The direct-call expectation contradicts the
  control test and cannot stand.
- Patch, not rewrite (agree with driver): the ranges existed at the
  focus_type layer and only needed threading to the three call sites.
- Note: BrowserAdapter.act does not exist (only a docstring mention);
  the driver fixed the docstring to CodeExecBackend.act. Confirmed by
  grep; no production effect.

## Items 5-6. R1 REGION FALLBACK (F2) + STALE ORIGIN (F3), b44a5ea - AMEND (test repair), patch

- Failing tests: test_region_fallback_readmits_raw_mozinner (F2, errors
  at HEAD) and test_stale_window_origin_accepted_silently (F3, fails at HEAD).
- The FIXES are proven. Driver's own tests pass at HEAD (Ran 6 tests
  OK, run 07:04, including the item-3 y_range tests):
  test_ground_input_refuses_meta_without_window_bounds,
  test_ground_input_refuses_stale_window_origin,
  test_ground_input_accepts_matching_live_origin. _window_origin
  requires window_bounds (raises DomActError, no region fallback);
  live_window_origin (hyprctl clients/activewindow, returns None when
  hyprctl is unavailable, never raises) plus _check_window_not_moved
  are wired into ground_input and ground_many_one_shot.
- F2 TEST is defective, independently confirmed. At HEAD it errors with
  exactly the fix's intended refusal: DomActError "meta needs
  window_bounds for the window origin (mozInnerScreen is
  window-relative); a screen-scope observation has no window to ground
  against, re-observe the window" (dom_act.py:67, via ground_input:182).
  The test has no assertRaises, so the refusal surfaces as an error.
  And the test's demand (a successful ground with the point within
  10px of the true point (1527.5, 1027.25)) is impossible from its meta
  ({image_size:[1920,1080], region:[0,0,3840,2160], monitor_box}):
  the true origin [2749,922] is not derivable from that meta; only a
  live hyprctl re-read could supply it, and none exists on the VM.
  The redteam's own fix requirement is to REFUSE, so the correct
  behavior makes this test error by construction.
- F3 TEST is defective, independently confirmed. It asserts
  viewport_origin([100,100],[1863,1176]) == [340,108] AND that the
  mapped point is within 10px of the true point. At HEAD
  viewport_origin still returns [340,108] (the first assert passes;
  the failure is "1271.4044399796628 not less than 10"). No return
  value satisfies both assertions: [340,108] maps 1271px away, any
  other value fails the equality assert, a raise errors the test (no
  assertRaises). It also calls viewport_origin directly, so a
  ground-time re-read cannot affect it.
- Repair required (test repair, for adjudication): F2 should
  assertRaises DomActError on ground_input with the bounds-less meta.
  F3 should be rewritten to assert the ground-time refusal (ground_input
  with a live origin that differs from the meta) instead of asserting
  on viewport_origin directly.
- Residual, recorded honestly: the live hyprctl re-read path has no
  live proof on this VM (no hyprctl here); only the fake-driven refusal
  is proven. On the laptop hyprctl exists so the check runs there.
  When the live origin is None the check is skipped and grounding
  proceeds on the meta's origin; if hyprctl ever fails on the laptop,
  a stale origin would pass silently. That is a coverage gap, not a
  blocker for this item: the refusal contract the redteam demanded is
  what the tests prove, and it is proven.
- Patch, with a removal (agree with driver): the region fallback is
  removed outright (it re-admitted the raw mozInner pair, the R1 hole);
  the live re-read is added as a check, not a new architecture.

## Item 7. R10 FLAG REDESIGN (F6/F7), 49081aa - AMEND (test repair), REDESIGN

- Failing test: test_typed_flag_forgeable_by_page_script (F6).
- F7 is fixed: F7 node and F7 python tests fail at base, pass at HEAD.
  The driver's new node test test_typed_flag_not_forgeable_via_window_property
  passes at HEAD and FAILS on the base tree (in the 3-test run above).
- F6 TEST is defective in two ways, independently confirmed:
  1. Its forge line `window.__agentCuTyped['#msg-input'] = true;`
     throws TypeError: Cannot set properties of undefined (setting
     '#msg-input') at HEAD, because the arm no longer creates
     window.__agentCuTyped (the arm JS contains __agentCuTyped only
     as a substring of the element-level '__agentCuTypedValue'). The
     test fails in _run_node before reaching any assertion (run 07:02).
     The line assumes the old surface; with the surface removed, the
     forgery attempt itself throws.
  2. Its value assertion `assertNotEqual(out['value'], 'hello')`
     conflates the field value with the verify outcome. out['value']
     is the verify JS result's value, a plain read of the field, and
     the page script did set the field to 'hello', so the assertion
     can never pass regardless of the flag redesign.
- My guarded-forge check (/tmp/r3c3-f6-check.py, run 07:02) proves the
  substantive assertion IS fixed: with the forge line wrapped in
  try/catch, the run returns {armed: True, flag: False, value:
  'hello'}. The flag assertion (assertFalse flag) WOULD pass; only the
  value assertion cannot.
- Repair required (test repair, for adjudication): guard the forge line
  (try/catch) and drop or fix the value assertion (the verify JS is a
  plain value read by design; the flag is what must be False). A decoy
  window property to make the unguarded forge line not throw was
  considered by the driver and rightly REJECTED: it would keep a piece
  that should not exist purely to accommodate a defective test line.
- REDESIGN, not patch (agree with driver, and this is the correct
  call): any writable window state is forgeable by construction, so no
  hardening of it can close R10. The closure + locked getter
  (Object.defineProperty, no setter, non-configurable) moves the state
  where page JS cannot write it. The Python verify_typed logic stays
  as-is, which is right: the flag check lives in Python for
  before!=None, and the before=None equality-only contract must keep
  working for pre-filled fields.
- Residual, recorded honestly: a page that pre-defines the locked
  property name with a non-configurable forged getter before arming
  would defeat the check; that requires knowing the property name and
  running before the arm, outside the R10 attacker model. Named, not
  hidden; not a blocker.

## Item 8. SET_VALUE SANITIZATION (F1), af0fa87 - GO, patch

- Failing-first: the F1 test fails at base (textarea CRLF lands as LF
  but ok False, 'value verification failed') and passes at HEAD.
- The diff is exactly the fix: both read-back checks in the set_value
  template now compare e.value against the sanitized form (input:
  strip CR/LF; textarea: CRLF/CR to LF), computed with
  String.fromCharCode so the template needs no backslash doubling.
  The maxlength pre-check is untouched (out of F1 scope, as claimed).
- Patch, not rewrite (agree with driver): native-setter write +
  read-back + change-only events is the right design; only the compared
  value was wrong.
- Owed, not hidden: live-browser confirmation of the HTML
  sanitization rule is still owed (no browser on the VM); the
  node-shim proof runs the REAL template against a spec-faithful fake
  DOM, and the rule is the documented HTML Standard behavior. The
  redteam itself flagged this as a caveat. Not a blocker for the code.

## Item 9. SUPPLY-CHAIN TESTS (C2 A3), 44c15bb - GO, tests only

- 3 new tests, all pass at HEAD (targeted run 07:03, Ran 10 tests OK,
  includes these plus items 2/7/12 tests):
  test_grounded_x_range_is_field_x_in_image_px,
  test_focus_type_forwards_grounded_ranges_to_act_fn,
  test_fallback_with_window_observation_supplies_ranges. The
  focus_type test uses a recording wrapper proving the kwargs arrive,
  not just that a fake accepts them. The first_action test gains the
  grounding methods on FakeZenSession. No production code changed in
  this item. Tests pin the items 3-4 wiring so a silent drop is caught.
- Patch-vs-rewrite: not applicable, tests only.

## Item 10. SNAPSHOT EVENT TEST (C1 G4), e912ad4 - GO, test only

- `node tests/cdp_snapshot.mjs` passes at HEAD (run 07:03, "all cdp
  snapshot, redaction, fill, payload, no_after and scope regressions
  pass" tail). The new mirror case asserts set_value from 'hello' to
  'world' lands the value and fires input then change, in that order.
  Before, the suite asserted only the zero-event side, so a template
  that never dispatched would have passed. Test only; the production
  dispatch is item 8's template, proven by the pin.

## Item 11. DESIGN-DOC FIXES (C3 G3/G4), 8d75135 - GO, doc only

- Verified by grep in improvements/worker-coord-click2-log.md: the only
  remaining "V4" mention is inside the B18 drop note itself (line 61),
  which records that the caret signal is dropped because it is
  forgeable by page JS and would false-fail mid-text edits and IME
  composition. The tab-switch protocol line is marked "**SUPERSEDED
  (2026-11-22, AMEND4 item 11)**" and kept visible (line 237); a new
  bullet records the benchmark target "clone1 Brave + clone2 Chrome on
  ws2" (owner definition 02:05). History is not rewritten.
- REMOVE, not patch (agree with driver): the V4 caret signal should not
  exist as a verification promise; the trusted-input flag replaces it.
  The tab-switch protocol is superseded, not patched: the benchmark
  target changed, so the protocol built for the old target goes away.

## Item 12. ACT-NOW ENVELOPE (CL1-SWEEP), cbab398 - GO, REDESIGN

- 4 new tests pass at HEAD (targeted run 07:03) and ALL 4 FAIL on the
  pre-fix tree: worktree /tmp/r3c3-pre12 at cbab398^ (5f30908) with
  HEAD's test_first_action.py copied in, Ran 4 tests, FAILED
  (failures=4). Failing-first confirmed the driver's stash-based claim
  independently.
- The diff matches the design: _scope_after helper returns the action
  result's after when its scope matches the input observation's scope,
  else a fresh capture in the input scope (window re-observed via
  cu.observe); a screen-scope input reuses the screen capture, which IS
  its scope-matching after. The envelope carries BOTH after
  (scope-matching, chainable) and after_screen (verification only,
  non-chainable). The scope check runs BEFORE the overlay attempt: a
  key/type batch given a screen-scope observation is refused with path
  'refused', the session is never attempted, the overlay is never
  acquired (test 4 asserts sess.assert_not_called and holders == {}).
- REDESIGN, not a one-line patch (agree with driver): the envelope
  contract changes because the after-capture was defective by
  construction (always screen-scoped). The "both" shape is the right
  choice over only patching the capture or removing after: the
  verification use of the screen capture is real, removal would force
  an extra observe per verification and break the workflow, and the
  scope-matching after costs zero extra captures (desktop_act already
  computes it). Removal of after was considered and rejected on those
  grounds; I agree.
- The root-cause claim (act-now ALWAYS captured envelope after with
  cu.observe_screen regardless of scope, overwriting desktop_act's
  scope-matching capture at cu.py:2083-2091) is consistent with the
  diff shape and the 4 failing-first tests; the trap is fixed by the
  scope match, proven by the tests, not by re-reading the CL1-SWEEP
  images, which I did not re-verify. The CL2-MSG after-image
  scope=screen claim is taken from the invest log, not re-verified.

## Item 4 follow-up. Session act_boundary fakes, 0668327 - GO, test-double fix

- At the parent commit e05fc58 (worktree /tmp/r3c3-pre66, native/wtype
  copied in), test_session_continuation + test_session_policy: Ran 28
  tests, FAILED (failures=15, errors=2). A single test run shows the
  exact cause: 'live.<locals>.act_boundary() got an unexpected keyword
  argument type_x_ranges' (the TypeError surfaces inside assertion
  messages). At HEAD the same 28 tests pass (inside the 217-test suite
  run, OK). The fix (both fakes accept **extra and forward it to the
  real desktop_act) is a stale-fake fix, not a test weakening: the
  fake mirrors the production desktop_act interface, and the tests'
  assertions are unchanged (the only removed lines are the fixed
  signature lines). Attribution to item 4 is correct: only items 3-4
  touched scripts/cu.py since 14fc139.

## Neighbor suites

- 07:03, tests/, PYTHONPATH=../scripts:. python3 -m unittest
  test_zen_dom test_dom_act test_type_verification test_first_action
  test_session_continuation test_session_policy: Ran 217 tests in
  11.500s, OK.
- Targeted new-test run 07:03: Ran 10 tests in 1.412s, OK (2 faithful
  shim, 1 flag non-forgeable, 2 item-9 dom_act, 1 item-9 first_action,
  4 item-12).
- Full discover, driver's final run (read from the AMEND4 log's Final
  verification section, 07:05, commit 6f54a4e): Ran 1920 tests in
  388.608s, FAILED (failures=5, errors=6, skipped=17). All 11 problems
  accounted for: 4 pre-existing errors (test_a11y_skeleton import,
  test_cursor_file setUpClass g++ -std=c++26, test_perf_evidence x2
  missing benchmark JSON), 5 RT2 adjudicated defectives (F2 error; F3,
  F4, F5-behavior, F6 failures), 2 environmental tc02_controller
  (missing tesseract binary). I checked the tesseract half myself:
  `which tesseract` returns nothing, and test_tc02_controller.py
  shells out to ['tesseract', ...] at lines 649/664/837, so the
  environmental attribution is consistent with the code (the failure
  mode itself was not live re-run here: standalone the module fails
  import for a path artifact, `from scripts import tc02_controller`
  needs an earlier discover module to put the repo root on sys.path).
  Zero failures in that run are caused by AMEND4 code: the only
  AMEND4-caused failures found (the 17 session tests) were fixed in
  0668327 and re-verified. The brief's end state (0 failures, 4
  pre-existing errors) is therefore NOT fully met: 5 failures remain,
  of which 4 are defective proof tests left for adjudication and 1 is
  environmental.
- Full discover, my run 1 (07:06-07:16, main tree): Ran 1927 tests in
  666.276s, FAILED (failures=13, errors=8, skipped=17). That is +7
  tests and +8 failures/+2 errors versus the driver's final run. The
  delta coincides exactly with post-07:05 tree churn, not AMEND4
  (AMEND4's last code commit 0668327, 07:02, is included in the
  driver's final run): Y1b baseline d7c0945 (07:04:40, Codex hardening,
  +23 lines test_code_exec.py, +52 test_codemode.py), Y1b fix 1e
  3f1b951 (07:05:52), PROBE-DOMZEN af0d0a2 (07:09:58), Y1b fix 2a/2b
  17fdb9b (07:14:20, 209 + 146 lines in code_exec.py/codemode.py), all
  landing during my run, plus uncommitted Y1b/PROBE edits entering the
  shared tree. One concrete mechanism verified by me: the uncommitted
  zen_dom.py edit adds a `return` prefix to the locate/hit_check/
  focus_check/field_value JS (from "(function(){" to "return
  (function(){"); the faithful-shim tests embed the captured script
  inside JSON.stringify(...), where a leading `return` is a JS syntax
  error, so both shim tests fail on the current dirty tree (reproduced
  07:23, node "Expression expected"). That is a post-review break by
  other workers' in-progress edit, NOT an AMEND4 defect at 8008662
  (the tests passed at 07:03 on the clean 8008662 tree), but the
  coordinator should know the shim tests are currently red on the
  shared tree and need a `_wrap_bare_return`-style fix in the test or
  a revert of the prefix. I could not name the other run-1 extras
  exactly: my rerun for names was contaminated by the sandbox EPERM
  flip below (566 errors), and the tree kept moving under me. None of
  the run-1 extras can be AMEND4 regressions on the evidence above:
  AMEND4 code is unchanged since the driver's clean final run, and
  every post-07:05 change is Y1b/probe/contract work.
- Sandbox EPERM flips (environment caveat, recorded for the
  coordinator): exec-shell child-process content writes flip between
  working and EPERM ("Operation not permitted", silent 0-byte files)
  on a seconds-to-minutes timescale in this session. Working at
  07:00-07:04 (all failing-first evidence) and 07:06-07:16 (run 1);
  EPERM at 07:17-07:26 (my detached rerun: 566 errors, unusable; `git
  fetch` "unpack-objects failed"; `git worktree add` and `git archive`
  writes fail; even shell-builtin printf fails at the worst moments).
  Working again briefly at 07:26:49 and 07:30:11, EPERM again by
  07:30:26. `muse.write`/`muse.edit` are unaffected (this log was
  written that way). Consequence: any test count taken while the
  sandbox is EPERM is garbage (file-writing tests fail spuriously);
  only run 1 and the driver's final run were taken in working windows.
  The flips also blocked building a pristine 8008662 worktree
  (`git worktree add` needs .git writes) for a clean re-run of the
  discover; the per-item verdicts do not depend on it (clean-tree
  measurements 07:00-07:06 stand).
- Shared-tree movement (caveat): HEAD moved 8008662 to 17fdb9b during
  this review (9 commits, 07:02-07:14 +07), and the working tree now
  carries uncommitted edits by other workers (732 insertions across
  scripts/code_exec.py, cu.py, first_action.py, sync-installed.py,
  zen_dom.py). I touched none of them. My verdicts are for HEAD
  8008662 as reviewed, measured on the clean tree at 07:00-07:06.

## Per-item verdicts (summary)

- Item 1 geometry (F9/F10): GO, patch.
- Item 2 gate traversal (F8/F11/F12/F13): GO, patch.
- Item 3 band anchoring (F4): AMEND, patch. Failing test:
  test_band_stacked_fields_low_click_with_x_range_must_not_verify.
  Repair: add y_range=(100, 120) to the test call.
- Item 4 wiring (F5): AMEND, patch. Failing test:
  test_band_wrong_field_unwired_path_reports_ok. Repair: rewrite the
  behavior test through a wired path or drop the direct-call
  expectation; it contradicts test_click_type_text_in_input_line_verifies.
- Items 5-6 R1 (F2/F3): AMEND, patch. Failing tests:
  test_region_fallback_readmits_raw_mozinner,
  test_stale_window_origin_accepted_silently. Repair: F2 assertRaises
  DomActError; F3 assert the ground-time refusal instead of
  viewport_origin directly.
- Item 7 flag redesign (F6/F7): AMEND, REDESIGN. Failing test:
  test_typed_flag_forgeable_by_page_script. Repair: guard the forge
  line and drop/fix the value assertion.
- Item 8 set_value (F1): GO, patch.
- Item 9 supply-chain tests (C2 A3): GO, tests only.
- Item 10 snapshot event test (C1 G4): GO, test only.
- Item 11 design-doc fixes (C3 G3/G4): GO, doc only (REMOVE for V4).
- Item 12 act-now envelope (CL1-SWEEP): GO, REDESIGN.
- Item 4 follow-up (0668327): GO, test-double fix.

## Overall verdict: AMEND (test-repair limb)

10 of 15 RT2 proof tests pass as written at HEAD; the other 5 fail
because the tests themselves are defective, and I re-proved each
defect independently (F4 symmetry, F5 contradicting control, F2
refusal-as-error plus underivable true point, F3 jointly
unsatisfiable assertions, F6 throwing forge line plus impossible
value assertion). In every one of the 5 cases the production fix is
independently proven by the driver's new tests plus my own checks.
This is not a BLOCK: there is no remaining production hole behind any
of the 5 failures that I can find. What is owed is test repair for
those 5 tests (repairs specified per item above), re-verification
after repair, plus the two live confirmations no VM can provide (F1
sanitization rule in a real browser; F3 hyprctl re-read on the
laptop). The FINAL direction's test-repair limb (e05fc58, "B5 stands
with test-repair limb") is the right frame for this.

## Time log

- 06:59 +00m task received; HEAD 8008662, branch todolist-push up to
  date with origin/todolist-push (fetch, no rebase needed).
- 07:00 +01m base worktree /tmp/r3c3-base at f0ddd41 created; HEAD
  RT2 run: 49 tests, failures=4, errors=1.
- 07:01 +02m base RT2 run first showed 41 harness errors (missing
  ignored native/wtype helper in the fresh worktree); copied it in,
  re-ran: 49 tests, failures=15, matching the RTR2 baseline exactly.
- 07:02 +03m F6 node failure read (forge line TypeError); F2 error
  read (DomActError refusal); F4 symmetry script and F6 guarded-forge
  script run, both confirming the defects.
- 07:03 +04m neighbor suites 217 tests OK; node cdp_snapshot.mjs
  passes; targeted 10 new tests OK; item-9 test names resolved.
- 07:04 +05m item-12 failing-first (4/4 fail on pre-fix tree) and
  pre66 session suites (15 failures + 2 errors, TypeError) confirmed;
  item-2/7 failing-first (3/3 fail on base) confirmed; item-3 own
  tests fail at base, pass at HEAD; item 5-6 driver tests pass at HEAD.
- 07:05 +06m item 11 grep verified; item 8 diff read; factor-required
  check (my first arg-order mistake corrected: factor is the 7th
  parameter, keyword form returns [2989, 930]).
- 07:06 +07m full discover started; dash scan 0/0; test-weakening
  review (only the factor-2 rewrite, a strengthening); item-2 shared
  helper and item-12 diff read.
- (discover result and commit time to be added before commit)

## Commit record

This log: improvements/worker-click3-r3c3-review-log.md (this file).
Committed with an explicit pathspec, push verified with git
ls-remote. No production code touched, no proof test touched, no
other worker file touched. Worktrees /tmp/r3c3-base, /tmp/r3c3-pre12,
/tmp/r3c3-pre66 are scratch in /tmp and will be removed. No em dash
or en dash in this file (checked before commit). No ydotool. No
personal info (owner name the owner only).

## Addendum (07:32 +07 22/11/2026, from COORD-CLICK-3 via CLOSEOUT-VERIFY, landed 07:31)

This addendum records five facts received after the review above was
written. Nothing above is rewritten; where a fact changes what the
review says, the change is stated here.

### 1. CORRECTION: Codex's RT claim was qualified, not 15/15 proof tests

Codex's log says "The 15 non-contradictory RT proof tests passed".
The 15 named tests are 13 proofs + 2 controls, and F2 and F3 are
EXCLUDED as "non-contradictory". F2/F3 fail or error on BOTH lanes.
Do not cite Codex as passing 15/15 proof tests. My review above does
not cite Codex on this point (it cites only VM-lane runs), so no
sentence above needs correction, but the qualified reading is recorded
here to prevent mis-citation. Arithmetic check, consistent with my
counts: 17 RT tests = 13 non-F2/F3 failing proofs (F1, F4, F5-behavior,
F5-source, F6, F7-node, F7-python, F8, F9, F10, F11, F12, F13) + 2
controls + F2 + F3. Codex passed the 15 non-contradictory ones; the VM
lane passed 10 of the 13 proofs (all except F4, F5-behavior, F6) plus
both controls.

### 2. Divergence: F4/F5/F6 PASS on the Codex lane, FAIL on the VM lane

This is the live question for the defective-test repair decision, and
my decision per test follows, with reasons. What the divergence
logically entails (no Codex-lane code inspected by me; these are
necessities, not guesses about its implementation):

- F4: the test requires _input_line_changed to return False for
  pixels at y=126 and True for pixels at y=110, both 8px from anchor
  118, with no y_range passed. My symmetry proof shows no SYMMETRIC
  band can do that. So a Codex-lane pass entails the band semantics
  changed (asymmetric or context-dependent), not just the test.
- F5-behavior: the test requires a direct desktop_act call with no
  ranges to report ok False, while the control
  test_click_type_text_in_input_line_verifies requires ok True on the
  same shape. A Codex-lane pass entails desktop_act's no-range
  behavior changed (the "or" branch: band-only unverified without
  grounded ranges).
- F6: the test requires out['value'] != 'hello' after a page script
  set the field to 'hello', and its forge line assumes the removed
  window property. A Codex-lane pass entails verify no longer returns
  the field's actual value when untyped (flag-gated verify JS), and
  the forge line no longer throws (a window property exists again, or
  the line was changed).

DECISION, per test (VM-lane repairs from the review above STAND):

- F4: KEEP the VM repair (add y_range=(100, 120) to the test call).
  Do not adopt an asymmetric band on the strength of the Codex pass
  alone: the mechanism is unnamed, and an asymmetric band has its own
  failure shape (a click near the TOP edge of a field, with text
  below the click line, would be refused). Request: the Codex lane
  must name its F4 mechanism and show the y=110 control still passing
  plus a top-edge-click case, before any adoption is considered.
- F5-behavior: KEEP the VM repair (rewrite the behavior test through
  a wired path) and REJECT the "or" branch. Point 3 below confirms
  the "or" branch breaks the pre-existing relay test. The Codex
  lane's F5 pass is bought by breaking a pre-existing contract, which
  is a regression trade, not a fix. Threading (the VM lane) preserves
  every pre-existing contract; the "or" branch breaks one.
- F6: KEEP the VM repair (guard the forge line, fix the value
  assertion) and REJECT flag-gated verify JS. Verify as a plain value
  read is the documented contract, and the before=None equality-only
  path must keep working for pre-filled fields; flag enforcement lives
  in Python for before!=None. If the Codex lane's F6 pass rests on
  flag-gated verify, it breaks that contract, and the pass should not
  be adopted without an adjudication that the contract itself should
  change.

### 3. Codex-lane regression (confirms the VM lane's item-4 choice)

The Codex lane's stricter item-4 BREAKS the pre-existing relay test
test_click_type_verifies_through_input_line_band (band-only result
unverified without grounded ranges). The VM lane deliberately rejected
that "or" branch and keeps the relay test passing. This is independent
confirmation, from the other lane's own outcome, that the "or" branch
is the wrong trade: it fixes one redteam proof test by breaking a
pre-existing test that encodes the documented empty-field contract.
My item-4 AMEND verdict stands, and the F5 repair stays a test repair,
not a production change.

### 4. Close-out verification (corroborates my RT measurements)

Close-out verified item-12 regression tests 4/4 PASS (three runs) and
the RT set Ran 49, failures=4, errors=1, matching AMEND4's 6f54a4e
exactly. This is independent corroboration of my own RT measurements
at HEAD 8008662 (49 tests, failures=4, errors=1, same five tests)
and in the pre66 worktree. My item-12 GO verdict and the five
defective-test findings are confirmed on two lanes plus close-out.

### 5. Clean full discover at a fixed HEAD is still owed

A clean full discover at a fixed HEAD is still owed (an EPERM storm
blocked it). Do not treat any mixed-tree number as single-commit
evidence. Applied to my own log: my run-1 number (1927 tests,
failures=13, errors=8) is a MIXED-TREE number (Y1b/probe commits and
uncommitted edits landed during the run) and must NOT be cited as
8008662's end state, nor as evidence about any single commit. The
driver's final run (1920 tests, failures=5, errors=6) is the closest
available fixed-head-adjacent number, but it too ran across the
07:04-07:05 commit window, so it is also not clean single-commit
evidence. The clean discover remains owed. My per-item verdicts do
not depend on any discover number: they rest on the clean-tree
per-item measurements at 07:00-07:06 (HEAD 8008662, tree verified
clean at 06:59) plus the failing-first worktree checks, all recorded
above.

### 6. Corroboration: DOMZEN-FIX (5dcf2b31) confirms the shim-test break

After this addendum was written, the branch moved to 5dcf2b31
("DOMZEN-FIX: return values from 7 zen_dom helpers, tolerate sppc
None in viewport_origin"). Its own message confirms the flag in the
discover section above: the `return` prefix (correct for real Zen,
where Geckodriver wraps execute scripts in a function body and bare
IIFEs returned None) breaks "9 node-harness tests that embed the
captured script as a JS expression", which "now fail with a
SyntaxError (a return statement is not an expression)". The DOMZEN
worker states the repair is test-side (wrap return-scripts) and
edited no test. This corroborates my finding (I reproduced the
failure for the 2 faithful-shim tests at 07:23) and widens it: the
RT2 node tests that embed captured scripts (F6, F7-node, F8-arm) are
among the 9 now failing with SyntaxError on the current tree, so a
fresh RT2 run on the current HEAD would show MORE than the 5
defective failures recorded at 8008662. That is a test-harness
repair owed on the current tree, not an AMEND4 verdict change: at
the reviewed HEAD 8008662 the tests embedded bare IIFEs and the 5
failures are the defective ones judged above. The coordinator should
route the wrap-return-scripts repair (the RT2 file already has a
_wrap_bare_return helper for typed_flag/harvest; the same treatment
is needed for the other captured scripts) before anyone re-runs the
RT set on the current HEAD and misreads the SyntaxErrors as new
findings.

### Addendum time log

- 07:32 +33m update received from COORD-CLICK-3 (CLOSEOUT-VERIFY
  facts, landed 07:31). Addendum written, no rewrite of the review
  above. Dash check run before commit (0 em/en dashes in this file).
- Commit of this log (explicit pathspec only) and push verification
  recorded in the Commit record below.
