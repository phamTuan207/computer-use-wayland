# CLICK3-R3RT log: round-3 redteam review of the AMEND4 fix pass

Worker: CLICK3-R3RT (redteam, round 3). Coordinator: COORD-CLICK-3.
Owner: the owner (repo-facing name). Branch: todolist-push.
Task start: 06:59 +07 22/11/2026 Asia/Ho_Chi_Minh. HEAD reviewed:
8008662 (click3-codex-discuss). All times below are wall-clock
Asia/Ho_Chi_Minh on this VM plus elapsed from task receipt.
Standing rules: full access, no em dash (U+2014) or en dash (U+2013)
anywhere, never ydotool, no personal info in repo files, log
everything. Independent and adversarial: I did not write AMEND4,
I attack it. I edited no production code and no proof test; I only
ADDED this log. Evidence with every claim (Lauren Tan standard:
test command, output, commit hash, time log).

## Verdict: NO BLOCK. 9 GO, 3 AMEND.

Per-item verdicts (detail below): item 1 GO, item 2 GO, item 3 GO,
item 4 GO, items 5-6 GO, item 7 AMEND (pre-lock forge, proven in
node), item 8 AMEND (maxlength pre-check still raw length, proven
in node), item 9 GO, item 10 GO, item 11 GO, item 12 AMEND
(scope-less window meta discards a correct window-scope after,
proven in Python; mismatch and screen-input branches untested).
No fix introduces a regression: full discover on clean HEAD is
recorded in the Final verification section; the 288 tests across
the seven AMEND4-touched suites pass. The 5 still-failing RT2
proof tests are all independently confirmed DEFECTIVE as written
(F2, F3, F4, F5-behavior, F6); the other 10 pass. No fix weakens a
test or the R7 fixture: the RT2 proof file is byte-identical to
f0ddd41 (0 diff), the frozen test_click2_redteam file is untouched
by AMEND4, and every fixture change I checked preserves the
asserted values (see items 5-6 and 7).

## Method and HEAD discipline

- Baseline first: `python3 tests/test_click3_redteam2.py` from
  `tests/` with `PYTHONPATH=../scripts:.` on the working tree:
  Ran 49 tests, FAILED (failures=4, errors=1). The 5 non-passing
  tests are exactly F2 (error), F3, F4, F5-behavior, F6 (fail).
- Hazard found mid-review (07:06-07:09 +07): the working tree
  carries UNCOMMITTED changes by another live worker (step-0
  CB-7/CB-10: dispatch_ms, first_pointer_ms, capture params) in
  scripts/cu.py, scripts/first_action.py, scripts/zen_dom.py,
  scripts/code_exec.py, scripts/codemode.py,
  scripts/sync-installed.py. Its in-progress first_action.py
  REPLACES `def _scope_after` with `def _dispatch_ms`, leaving
  the _scope_after docstring orphaned under _capture_params, so
  the working tree currently has NO _scope_after at all (my
  `hasattr` probe returned False, and the line-875 call site
  would NameError into after_error). That is the other worker's
  in-progress edit, NOT an AMEND4 defect, and I touched none of
  it. All verdicts below are against committed HEAD 8008662,
  verified in a clean worktree at /tmp/r3rt-head (HEAD
  800866256724e65404e58cf763a3b37fe038ca2c, status clean) with
  the gitignored native/wtype and native/pointer binaries copied
  in (without them the harness errors with 'private wtype helper
  is missing', 42 errors; that is a worktree artifact gap, not a
  code failure). Clean-HEAD RT2 run reproduces the working-tree
  run exactly: Ran 49, failures=4, errors=1, same 5 tests.
- Each fix was read as a diff, each defective-test claim was
  re-proven independently (not taken from the AMEND4 log), and
  each new residual was proven by executing the real code
  (node for the JS fixes, Python for the Python fixes).

## Time log

- 06:59 +00m task received; HEAD 8008662; AMEND4 log (588
  lines) and RTR2 log (F1-F13) read in full; 12 AMEND4 commits
  listed (cc964b2, c1ea773, 62b740e, 72120aa, b44a5ea, 49081aa,
  af0fa87, 44c15bb, e912ad4, 8d75135, cbab398, 0668327).
- 07:01 +02m RT2 run on working tree: 49 tests, failures=4,
  errors=1 (F2 error; F3, F4, F5-behavior, F6 fail).
- 07:02-07:05 +03-06m items 1, 8, 10, 11 read and checked
  (geometry diff, cdp.mjs diff, snapshot test, design doc).
- 07:05-07:09 +06-10m items 2, 3, 4 read; F4/F5 defect proofs
  re-derived from the test sources; dirty-tree hazard found
  (uncommitted step-0 edits, _scope_after missing in tree).
- 07:10 +11m clean worktree /tmp/r3rt-head at 8008662 created;
  RT2 re-run there (after copying native binaries): same 49,
  failures=4, errors=1. Pre-lock proof re-run against HEAD
  zen_dom JS: forge succeeds (see item 7).
- 07:11-07:13 +12-14m item 12 scope-less probe on HEAD
  first_action: Case A returns screen-1 (see item 12).
  Item-12 failing-first verified on worktree /tmp/r3rt-old at
  cbab398^: all 4 new tests fail on pre-fix code.
- 07:13-07:15 +14-16m item-8 maxlength proof in node (real
  cdp.mjs template): raw-length pre-check refuses a set the
  engine would accept (see item 8). Targeted suites on clean
  HEAD: 288 tests OK.
- 07:15 +16m full discover running in clean worktree (see
  Final verification); this log written.
- 07:19-07:30 +20-31m discover triage: run 1 (1864 tests,
  31 failures, 468 errors) vs AMEND4 log claim (1855, 0, 4);
  baseline worktree blocked by git EPERM flap; proved the
  mass errors are stdlib tempfile EPERM flap (live flag
  tests, mkdtemp flapping, 73 modules); sampled
  test_first_action / session / cdp_snapshot errors are
  tempdir setUp failures; test_chained_ops fails at f0ddd41
  too (pre-existing); test_host_exits passes on re-run
  (flaky). Log finalized for commit.
- 07:31-07:45 +32-46m commit blocked by the same EPERM flap
  (35 attempts total: 6 + 8 + 20-attempt loop + 1 probe,
  all "unable to write loose object file"); addendum
  added per COORD-CLICK-3 update (closeout facts verified
  against worker-amend4-closeout-log.md); Commit record
  corrected to NOT YET COMMITTED with landing command;
  branch moved to 5dcf2b3, reviewed HEAD 8008662 still an
  ancestor. Report delivered with the file on disk.

## Item 1. GEOMETRY (cc964b2, F9/F10) - GO

- The fix is correct. check_viewport_geometry now requires
  factor (raises instead of silently assuming 1), checks
  exactness (absolute == window + moz*factor within 0.5 px),
  and checks containment in screen px (window + size*factor).
  viewport_origin and ground_many_one_shot pass size as-is in
  both branches with factor passed explicitly. The "size as-is"
  premise is production-true: window_bounds comes from
  Hyprland logical size (cu.py:960 builds the window meta from
  bounds(), validate_coordinate_metadata calls window_bounds
  "integer logical dimensions"), and Hyprland logical px equal
  CSS px numerically, so the amend3 divide-by-factor was the
  unit mixing F9 caught. F9 and F10 RT2 tests pass.
- The factor-2 test rewrite is NOT a weakening: it changes the
  input to the new contract ([1863, 1176] logical instead of
  [3726, 2352] screen px) and keeps the same expected origin
  [2989, 930] plus the refusal case ([1500, 1000] raises).
- Notes, not verdict-changers: (a) the exactness check has no
  test that exercises it with factor supplied: the F10 RT2
  test calls check_viewport_geometry WITHOUT factor, so it
  passes via the fail-closed factor requirement, not via
  exactness; both production callers compute absolute from the
  same formula the check verifies, so exactness is
  defense-in-depth for a caller that forgets the factor. A
  test passing factor=2 with the factor-forgotten origin
  (2749, 922) and expecting refusal would pin it. (b)
  ground_many_one_shot silently defaults factor to 1 when
  harvest omits both screen_pixels_per_css_pixel and
  device_pixel_ratio (`raw.get('device_pixel_ratio', 1)`):
  the same silent-factor-1 pattern item 1 removes from the
  validator, one level up; unreachable in practice
  (devicePixelRatio is always a number in browsers).

## Item 2. GATE TRAVERSAL (c1ea773, F8/F11/F12/F13) - GO

- Shared _FIND_JS (pierce + framesOf + find, depth cap 5,
  frames detected by contentWindow presence, cross-origin
  fail-closed) is used by locate, hit_check, focus_check,
  field_value, verify_typed, arm_typed_flag, sent_bubble_contains
  (recursive leaf collection) and harvest (find per selector,
  framePoint hit, deepActive focus). All four RT2 iframe tests
  pass (F8 arm in iframe, F11 harvest, F12 nested iframe,
  F13 iframe in shadow root), running the real captured JS in
  node. No production caller of locate_point exists outside
  tests, so no live path was missed.
- R7 faithful-shim re-run verified failing-first: the PRE-item-2
  focus_check JS (from c1ea773^:scripts/zen_dom.py, no find())
  run in node against the faithful shim returns false; the new
  code returns True (TestFaithfulShadowShim, 2 node tests, in
  the 288-test OK run). The frozen R7 test still passes.
- Note, not a verdict-changer: _FRAME_POINT_JS subtracts the
  iframe border-box origin (r.left/r.top) but not the iframe
  border width when walking the frame chain, so a bordered
  iframe shifts the elementFromPoint probe by the border
  (typically 0-2 px). A 2 px error only flips a hit test for
  a target at an edge; the center-hit check is robust to it.

## Item 3. R3a BAND ANCHORING (62b740e, F4) - GO

- _input_line_changed gained y_range (band y = field y-range
  when given, else anchor+-12); grounded_y_range mirrors
  grounded_x_range; type_y_ranges threaded through
  desktop_act and focus_type. The two new tests are real pins:
  a unit test (stacked pixels at y=18 with y_range=(4,16)
  must not verify, and must verify without y_range, proving
  the hole) and a desktop_act-level test (ok False,
  type_unverified, with a positive control that still
  verifies). Both pass in the 288-test run.
- F4 RT2 test CONFIRMED DEFECTIVE (independent symmetry
  proof). The test calls _input_line_changed(old, new, 118,
  x_range=(100, 300)) with pixels at y=126 and expects False,
  while its control expects True for pixels at y=110. Both
  are 8 px from anchor 118 and no y_range is passed. Any
  symmetric band [118-h, 118+h] containing 110 needs h>=8 and
  then also contains 126; h<8 excludes both. Only the field's
  y-range (not passed) can distinguish them, so no
  implementation of the y_range contract can pass this test
  as written. The test needs y_range=(100, 120) added to be
  sound. Adjudication owed, as the AMEND4 log says.

## Item 4. R3a WIRING (72120aa + 0668327, F5) - GO

- type_x_ranges AND type_y_ranges are threaded through all
  three paths: CLI act (explicit on the desktop_act call
  line), CodeExecBackend.act (best-effort grounding when
  dom_session + dom_selector are given), first_action fallback
  (y_range alongside existing x_range). The F5 source test
  passes. The BrowserAdapter.act naming slip is fixed
  (docstring now says CodeExecBackend.act; no such class
  exists). The item-4 follow-up (0668327) is a stale-fake
  fix, not a weakening: the live() act_boundary fakes in
  test_session_continuation.py and test_session_policy.py now
  accept **extra and forward it to the real desktop_act;
  assertions unchanged; the 17 TypeErrors it fixed are gone
  (both suites pass in the 288-test run).
- F5 behavior test CONFIRMED DEFECTIVE (independent proof).
  It calls cu.desktop_act DIRECTLY with click (15,10) +
  type, pixels x 0..11 at y=10, no ranges, and expects ok
  False. Threading cannot affect a direct call. Worse, its
  expectation contradicts the existing control test
  test_click_type_text_in_input_line_verifies (click (10,10),
  pixels x 12..17 at the line's left edge, no ranges, expects
  ok True via band): both are "text at the line's left edge,
  away from the click point", the documented empty-field
  shape. Both cannot pass. The AMEND4 decision to implement
  threading and NOT the "or" branch (band-only unverified
  when no ranges supplied) is correct: the "or" branch would
  break that control and the empty-field contract.
- Residual, not a verdict-changer: the three wired paths
  supply a ONE-element ranges list (single dom_selector), so
  in a multi-field batch (click field A, type, click field B,
  type) group 2+ pads to None and keeps the full-width /
  click-anchored band. Before AMEND4 every group was
  full-width; now group 1 is narrowed. Improvement, not a
  break; per-group grounding is a follow-up, not F5.

## Items 5-6. R1 REGION FALLBACK + STALE ORIGIN (b44a5ea, F2/F3) - GO

- _window_origin requires window_bounds (raises DomActError,
  no region fallback); locate_point same. live_window_origin
  (hyprctl clients -j by address, else activewindow -j,
  None on any failure, never raises) plus
  _check_window_not_moved wired into ground_input and
  ground_many_one_shot (refuse on mismatch, skip when live
  origin is None). New tests pin refusal without
  window_bounds, stale-origin refusal (live [2600,914] vs
  meta [2533,914]), and matching-origin pass with the same
  point/origin. All pass.
- Fixture changes preserve semantics: G30_META, _meta() and
  the 7 map-accuracy case metas gained window_bounds EQUAL
  to their region (their regions ARE the windows), so the
  asserted points are unchanged; the region-fallback path
  they used to exercise no longer exists, and the
  no-window_bounds case is covered by the new refusal test.
- F2 RT2 test CONFIRMED DEFECTIVE. It asserts ground_input
  RETURNS a ground with viewport_origin != [240,8] and point
  within 10 px of the true point (1527.5, 1027.25) from a
  meta with no window_bounds. The true origin [2749,922] is
  not derivable from that meta; only a live hyprctl re-read
  could supply it, and none exists on the VM (the test's
  FakeWdSession has no live_window_origin). No implementation
  can pass it as written; the required behavior is refusal,
  and the test has no assertRaises, so it errors with the
  refusal DomActError. That error IS the fix working.
- F3 RT2 test CONFIRMED DEFECTIVE. It calls viewport_origin
  directly and asserts BOTH stale == [340,108] AND the mapped
  point within 10 px of the true point. [340,108] maps to
  (323.0, 620.25) while the true point is (1527.5, 1027.25),
  1271 image px away (confirmed in the failure output:
  "1271.4044399796628 not less than 10"). No return value
  satisfies both assertions, and a ground-time re-read cannot
  affect a direct viewport_origin call. Adjudication owed.
- Residuals, not verdict-changers: (a) the staleness check
  compares ORIGIN only, not size; a resize without a move
  leaves a stale window_size in the closure check, which
  false-refuses (fail-closed) when the window grew and is
  harmless to the point when it shrank (the point uses
  origin + live mozInner, not size). (b) The check fails
  OPEN when the live re-read returns None (hyprctl failure,
  timeout, window not found): a move plus a simultaneous
  hyprctl failure is accepted silently. (c) locate_point has
  no staleness check, but it has no production callers
  (tests only), so F3 is closed on the live paths.

## Item 7. R10 FLAG REDESIGN (49081aa, F6/F7) - AMEND

- What is fixed: window.__agentCuTyped is gone. arm records
  the field value at each trusted input event in a listener
  closure, exposed via a locked getter (defineProperty,
  non-configurable, no setter) on the element; typed_flag
  returns True only when last-trusted equals current value.
  F7 node and F7 python pass; F8 still passes; the new node
  regression test (whole-property window forge, flag False)
  passes. The fakes model the new contract faithfully and
  STRICTER (record-at-set, compare-to-current), not weaker.
- F6 RT2 test CONFIRMED DEFECTIVE in two ways. (1) Its forge
  line `window.__agentCuTyped['#msg-input'] = true;` throws
  (TypeError: Cannot set properties of undefined) because the
  arm no longer creates window.__agentCuTyped; the forgery
  attempt itself throws before the assertions run, so the
  test fails as an assertion error from the node driver, not
  from a forged flag. The flag assertion would pass if the
  forge line were guarded (proven by AMEND4's own node test:
  armed true, flag false). (2) Its value assertion
  `assertNotEqual(out['value'], 'hello')` conflates the field
  value with the verify outcome: out['value'] is the verify
  JS result {value, editable} and the field's value IS
  'hello' (the page script set it), so the assertion can
  never pass for any implementation that reads the field
  value; making the JS lie about the value would break the
  before=None equality-only contract for pre-filled fields.
  The sibling F7 test asserts the correct conjunction
  (flag False AND value == hello is False) and passes.
- BLOCKING-CLASS RESIDUAL (new finding, same class as F6):
  the re-arm path trusts ANY pre-existing non-configurable
  getter under the property name:
  `if(desc && desc.get && desc.configurable===false) return
  true;` A hostile page that pre-locks the name BEFORE the
  arm, with a getter returning the live value, defeats the
  check completely. PROOF (real captured arm/typed_flag JS
  from HEAD zen_dom, node, /tmp/r3rt_prelock.js):
  pre-locked getter returning __el.value, then arm, then a
  page script sets value 'hello' with zero trusted input
  events: {"armed":true,"flag":true,"value":"hello"}. Control
  (no pre-lock, same forge): {"armed":true,"flag":false}.
  The property name is in the shipped source, and the page
  loads before the agent arms, so the timing requirement is
  satisfiable by any page that wants to defeat the flag. The
  fix narrows the forge window (before-arm only, vs the old
  any-time one-liner) but does not eliminate it. Required
  hardening: do not trust a pre-existing descriptor; use a
  per-arm unpredictable property name (token generated in
  Python, stored on the session, typed_flag reads the same
  name) or fail closed on re-arm unless the getter is proven
  to be the arm's own. Named failing test (to be added in
  tests/test_zen_dom.py):
  test_typed_flag_not_forgeable_via_prelocked_getter (arm
  after a pre-locked live-value getter must return False or
  typed_flag must return False after a zero-event JS set).
- The AMEND4 log records this residual honestly but places
  it "outside the R10 attacker model"; a page script that
  pre-locks is a page script setting the value, which IS the
  R10 model, so I do not accept the exclusion. AMEND, not
  BLOCK: F6/F7 as proven are closed, and the fix is a strict
  improvement over the window property.

## Item 8. SET_VALUE SANITIZATION (af0fa87, F1) - AMEND

- What is fixed: both read-back checks in scripts/cdp.mjs
  compare e.value against the SANITIZED form (input strips
  CR/LF, textarea normalizes CRLF/CR to LF, via
  String.fromCharCode so the template needs no backslash
  doubling). F1 passes (textarea CRLF lands as LF, input
  newline lands stripped, unchanged text fires no events,
  whitespace change fires input+change). `node
  cdp_snapshot.mjs` passes.
- RESIDUAL (second half of the RTR2 F1 fix requirement,
  left untouched as "out of scope" in the AMEND4 log): the
  maxLength pre-check still measures the RAW text:
  `if(e.maxLength>=0&&${text}.length>e.maxLength) return
  {ok:false,error:'value exceeds maxlength'}`. PROOF (real
  set_value template extracted from scripts/cdp.mjs, node,
  spec-faithful fake DOM, /tmp/r3rt_maxlen.py): textarea
  maxLength 5, text 'ab\r\ncd' (raw 6, sanitized 'ab\ncd'
  5 chars, which the engine would accept): {"ok":false,
  "error":"value exceeds maxlength","events":[],"value":""}.
  Input maxLength 4, text 'ab\ncd' (raw 5, sanitized 'abcd'
  4): same refusal. The pre-check refuses a set the engine
  would accept, on the exact newline text F1 is about.
  Required fix: compare sanitized.length in the pre-check
  (one line; the sanitized value is already computed). Named
  failing test (to be added to the F1 test class in
  tests/test_click3_redteam2.py by adjudication, or to
  tests/cdp_snapshot.mjs):
  test_set_value_maxlength_uses_sanitized_length. AMEND, not
  BLOCK: fail-closed false refusal, narrow trigger
  (maxLength set AND newline text AND length within the
  newline count of the limit); the main F1 read-back finding
  is fixed. Live-browser confirmation of the sanitization
  rule itself is still owed (no browser on this VM), as the
  AMEND4 log states.

## Item 9. SUPPLY-CHAIN TESTS (44c15bb, C2 A3) - GO

- Three tests, all real pins, all passing: grounded_x_range
  unit test (G30 field [86.0, 526.0], None on an unmappable
  meta); focus_type forwards grounded x- and y-ranges to the
  act_fn (a RECORDING wrapper proves the kwargs arrive with
  exact values [[86.0, 526.0]] and [[1101.0, 1164.0]], not
  just that a fake accepts them); first_action supplies both
  ranges to the fallback desktop_act on a window-scope
  observation (real dom_act.ground_input through the
  FakeZenSession's locate/viewport_origin/hit_check). No
  production code changed in this item, nothing to regress.

## Item 10. SNAPSHOT EVENT TEST (e912ad4, C1 G4) - GO

- Mirror case added to tests/cdp_snapshot.mjs: set_value
  from 'hello' to 'world' lands the value and fires input
  then change, in that order. The suite used to assert only
  the zero-event side, so a template that never dispatched
  would have passed; the new assertion fails on such a
  template by construction (events [] != ['input','change']).
  `node cdp_snapshot.mjs` passes.

## Item 11. DESIGN-DOC FIXES (8d75135, C3 G3/G4) - GO

- Benchmark target recorded (clone1 Brave + clone2 Chrome on
  ws2, owner definition 02:05); the one-Zen-two-tabs
  tab-switch protocol marked SUPERSEDED, history kept
  visible. V4 caret promise removed from line 61 bundle and
  step 4; the only remaining "V4" mention is inside the B18
  drop note itself (grep verified). No caret check exists in
  code (grep for selectionStart/selectionEnd/getSelection/
  caret offset across scripts/*.py and scripts/*.mjs: zero
  hits; the only "caret" mentions are band comments about
  caret-pixel noise), so dropping the doc promise removes the
  only caret-position claim and creates no doc/code mismatch.
  V2's "caret offset" phrase is doc language only, with no
  implementing code. The V4 rationale (forgeable, false-fails
  mid-text edits and IME) is sound.

## Item 12. ACT-NOW ENVELOPE (cbab398, CL1-SWEEP) - AMEND

- What is fixed and verified from source: the old hardcoded
  observe_screen envelope after is GONE (grep: only
  after_screen assignments remain); the envelope now carries
  BOTH after (scope-matching, chainable) and after_screen
  (verification-only). The session path's result['after']
  survives compaction: cu.py:3216 compacts non-verbose act
  output, and compact_result recurses into 'after' with the
  desktop whitelist that includes scope, window,
  window_bounds, region, image_size (verified by reading
  compact_result, cu.py:1506-1529). desktop_act's
  _after_capture is scope-matching by construction
  (observe_screen for screen scope, observe for window scope,
  cu.py:2218-2225). cu.observe's signature matches the
  _scope_after fresh-capture call (crop, max_width,
  activate=False). The pre-overlay scope refusal is real:
  a Return key batch given a screen-scope observation is
  refused before overlay acquire and session attempt, and
  the finally block prints the envelope on that path, so
  the refusal reaches the operator. Failing-first verified:
  all 4 new tests fail on pre-fix first_action.py (worktree
  /tmp/r3rt-old at cbab398^, new test file copied in: Ran 4
  tests, FAILED (failures=4)); all 4 pass on HEAD.
- RESIDUAL 1 (same trap class, proven): a scope-less window
  meta discards a correct window-scope result_after and
  returns the screen capture as the chainable after. PROOF
  (real _scope_after from HEAD first_action.py, Python):
  Case A scope-less window meta + window-scope result_after
  -> screen-1, zero observe calls (the correct after is
  dropped). Case B control (scoped window meta, same
  result_after) -> result-win. Case C (mismatched
  screen-scope result_after + window meta) -> win-after-1
  fresh capture, correct. The AMEND4 log's claim that "one
  with no scope field reuses the screen capture, which IS
  its scope-matching after" is FALSE for a scope-less WINDOW
  observation. Reachability is narrow (only observations
  written by a pre-scope build, still fresh within the 120 s
  window: _read_given_observation does not require a scope
  field, and desktop_act's preflight treats scope-less as
  window-scope, so a key/type batch CAN run on one), and
  the consequence is a LOUD pre-overlay refusal on the next
  chained act-now, not a wrong click. Required fix (one
  line): in _scope_after, treat a window-bearing meta with
  no scope as window scope (accept a window-scope
  result_after, else fresh-capture via cu.observe).
  Named failing test (to be added in
  tests/test_first_action.py):
  test_scope_after_prefers_result_after_for_scopeless_window_meta.
- RESIDUAL 2 (coverage): the scope-mismatch branch (Case C
  above, works) and the screen-scope input branch (after ==
  screen capture, no extra observe call) have NO regression
  test; the 4 landed tests cover matching session, matching
  fallback, no-after fresh capture, and pre-overlay refusal
  only. Named tests to add:
  test_scope_after_mismatched_result_after_recaptures_window
  and test_scope_after_screen_input_reuses_screen_without_recapture.
- AMEND, not BLOCK: for every observation the current code
  produces (scope always set), the trap is closed; the
  residual needs a legacy scope-less file and fails loud.

## Defective-test findings (FRT B5)

All five still-non-passing RT2 proof tests are defective as
written, each re-proven independently above: F2 (demands an
underivable true point, no assertRaises for the required
refusal), F3 (self-contradictory assertions on a direct
viewport_origin call), F4 (symmetry proof: no y_range passed,
both pixels 8 px from the anchor), F5-behavior (direct
desktop_act call no threading can affect; contradicts the
control test_click_type_text_in_input_line_verifies), F6
(forge line throws on the removed surface; value assertion
conflates the value read with the verdict). The F5 source
test passes. Adjudication owed on all five: each needs its
expectation repaired (assertRaises for F2; split F3 into a
refusal test at the ground_input level; add y_range to F4;
delete or re-scope the F5 behavior test to a wired path;
guard the F6 forge line and drop the value assertion), NOT
a production change to satisfy them as written. Do NOT edit
tests/test_click3_redteam2.py in a fix pass without that
adjudication; the file is byte-identical to f0ddd41.

## Regressions and test-weakening check

- tests/test_click3_redteam2.py: 0 diff f0ddd41..HEAD.
  tests/test_click2_redteam.py: untouched by AMEND4.
- No test assertion was weakened: the factor-2 geometry test
  rewrite changes the INPUT to the new contract with the same
  expected origin; the item-7 fakes got STRICTER; the
  session act_boundary fakes forward kwargs instead of
  rejecting them (assertions unchanged); fixture metas gained
  window_bounds equal to their regions (asserted values
  unchanged).
- Full discover on clean HEAD: see Final verification.
  Two stable non-RT2 failures in the discover are NOT
  AMEND4 regressions: test_chained_ops_in_one_program fails
  identically at baseline f0ddd41 (pre-existing), and
  test_host_exits_when_browser_closes_stdin passes on
  standalone re-run (flaky). Neighbor suites on clean HEAD: 288 tests OK
  (test_type_verification, test_dom_act, test_first_action,
  test_zen_dom, test_session_continuation, test_session_policy,
  test_click2_redteam).
- Dashes: AMEND4 introduced zero em/en dashes. The two
  dashes present at HEAD in AMEND4-touched files are
  pre-existing (also in f0ddd41): a quoted window title in
  worker-coord-click2-log.md:188 and a comment in
  test_session_continuation.py:504. No personal info in any
  AMEND4 commit content (checked for gmail, address, phone
  patterns; only the GitHub noreply author address, which is
  in every commit).

## Final verification

- RT2 proof tests, clean HEAD 8008662 (/tmp/r3rt-head,
  native binaries copied in): Ran 49 tests, FAILED
  (failures=4, errors=1): F2 error (refusal DomActError),
  F3/F4/F5-behavior/F6 fail. Same 5 tests as the working-tree
  run; the other 10 pass.
- Full discover, clean HEAD: three runs, all dominated by an
  ENVIRONMENTAL filesystem flap, not by code. Run 1 (07:19,
  tail only): Ran 1864 tests in 456.753s, FAILED (failures=31,
  errors=468, skipped=17). Run 2 (07:24, grep FAIL:/ERROR:):
  Ran 1831 tests in 56.701s, FAILED (failures=6, errors=931,
  skipped=17). Run 3 (07:28, count only): 936 FAIL/ERROR
  lines. Counts vary 2x between identical runs, so the
  discover is not a stable regression signal while the flap
  lasts. PROOF the errors are environmental: a sampled error
  (test_act_diagnostics setUp) fails in
  tempfile._get_default_tempdir, which probes each candidate
  dir by creating, writing and unlinking a test file; the
  stdlib source at /usr/lib/python3.12/tempfile.py:322-362
  shows that logic, and zero AMEND4 code is in the stack.
  Live flap demo (07:26): os.open(O_RDWR|O_CREAT|O_EXCL)
  fails EPERM in /tmp AND in ~/workspace while touch on the
  same paths succeeds; one minute later all flag
  combinations succeed; minutes later mkdtemp fails 5/5
  again. The same flap broke git fetch, git worktree add
  (loose-object / lock writes EPERM) and tar extraction
  during this review. Module-level analysis of run 2 (937
  lines, 73 modules): AMEND4-touched test_zen_dom 0,
  test_dom_act 0, test_type_verification 0,
  test_click2_redteam 0 errors; test_first_action 49,
  test_session_continuation 10, test_session_policy 15 errors
  are all tempdir setUp failures in suites that PASS in the
  288-test targeted run. Stable failures in run 2 (6): the
  4 defective RT2 tests, plus test_chained_ops_in_one_program
  (codemode) and test_host_exits_when_browser_closes_stdin
  (webext). test_host_exits PASSES on standalone re-run
  (flaky). test_chained_ops FAILS deterministically on HEAD
  AND on baseline f0ddd41 (/tmp/r3c2-base, 07:30), so it is
  PRE-EXISTING, not AMEND4-caused (codemode.py is not an
  AMEND4 file; the test runs repo_py_compile on zen_dom.py).
  Conclusion: no AMEND4-caused regression found. The AMEND4
  log's end-state claim (1855 tests, 0 failures, 4 errors)
  is NOT reproducible by plain `python3 -m unittest discover`
  on this VM, and the AMEND4 log references a "Final
  verification" section that was never written in that file;
  that is a log-accuracy gap, not a code finding.

## Addendum (COORD-CLICK-3 update, 07:32 +07, via CLOSEOUT-VERIFY)

Source: closeout log improvements/worker-amend4-closeout-log.md
(landed 07:31 +07). I verified each fact below against that
log by grep before writing this addendum (07:33 +07). No
verdict in this review changes; the addendum qualifies the
defective-test findings and corroborates two of them.

- (1) CORRECTION on the Codex lane RT claim. Codex's log
  says "The 15 non-contradictory RT proof tests passed": Ran
  15 tests, OK. The 15 named tests are 13 proofs + 2
  controls (F4 stacked-fields, the 2 controls, F5-behavior
  wrong-field, codeexec/CLI ranges, geometry x2, R10 flag x3,
  iframe arm, iframe reads x3, set_value newline). F2 and F3
  are EXCLUDED by Codex as "non-contradictory" and fail or
  error on BOTH lanes in full discover. Do not cite Codex as
  passing 15/15 proof tests. This log makes no such claim.
- (2) DIVERGENCE, live for the repair decision. F4, F5-behavior
  and F6 PASS on the Codex lane and FAIL on the VM lane
  (judged defective there). My F4 symmetry proof and F6
  forge-line/value-assertion findings are relative to the VM
  lane's contract as reviewed: a symmetric band, no "or"
  branch, and the window surface removed. The Codex lane
  passes these tests by changing the contract (mechanism for
  F4/F6 not read by me; F5's mechanism is the "or" branch,
  see (3)). A pass bought by changing the semantics is not
  evidence the tests as written are sound. The repair
  decision must settle the SEMANTICS first (band-only
  unverified without grounded ranges vs the empty-field/band
  contract), not chase green on either lane. That decision
  belongs to the council.
- (3) Codex-lane REGRESSION, confirming my item-4 note
  empirically. Codex full discover: Ran 1922 tests,
  FAILED (failures=2, errors=4, skipped=2). Failures: F3
  stale-origin + test_click_type_verifies_through_input_line_band
  (RelayBandVerification). Codex's own log attributes the
  relay break to its stricter item-4 ("expects a band-only
  result to verify without grounded ranges. Item 4 requires
  that result to be unverified"). The VM lane deliberately
  rejected that "or" branch and keeps the relay test passing.
  My item-4 GO stands on the VM lane as reviewed; the Codex
  lane's item-4 is a divergent implementation, not the one
  reviewed here.
- (4) Closeout independently verified item-12 regression
  tests 4/4 PASS (3 independent runs) and the RT proof set
  Ran 49, failures=4, errors=1, matching AMEND4's 6f54a4e
  Final verification exactly. Corroborates my item-12
  failing-first check and my RT baseline.
- (5) Clean full discover at a fixed HEAD is STILL OWED.
  Closeout's own fixed-worktree run at af0d0a2 was INVALID
  (497 errors, PermissionError EPERM on tempfile writes);
  its section 3e records NOT OBTAINED, and its section 7
  documents the EPERM storm. My Final verification numbers
  are likewise flap-dominated and must not be treated as
  single-commit evidence. The no-regression conclusion in
  this review rests on the targeted suites (288 tests OK) and
  the proven flap mechanism, not on the discover counts.

## Commit record

- This log: improvements/worker-click3-r3rt-review-log.md
  (this file, 33,702 bytes). NOT YET COMMITTED: the EPERM
  storm blocked every git object write, 35 failed attempts
  07:31-07:45 +07 ("fatal: unable to write loose object
  file: Operation not permitted"), including a 20-attempt
  retry loop 07:35-07:44. To land it once the storm clears,
  from the repo root, with an explicit pathspec only:
  git add improvements/worker-click3-r3rt-review-log.md
  then git commit -m "R3RT review: AMEND4 round-3 redteam,
  9 GO / 3 AMEND, no BLOCK (HEAD 8008662)" --
  improvements/worker-click3-r3rt-review-log.md, then push
  and verify with git ls-remote. No production code and no
  test touched. No em dash or en dash in this file (grep -c
  = 0, checked 07:34). No ydotool. No personal info (owner
  name the owner only). HEAD reviewed 8008662 is an ancestor
  of current HEAD 5dcf2b3 (verified 07:45).
