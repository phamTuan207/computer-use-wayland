# Round-3 council review of the AMEND4 fix pass (worker CLICK3-R3C2)

Worker CLICK3-R3C2, round-3 council reviewer 2 for the AMEND4 fix pass,
subagent of the parent orchestrator. Owner: the owner (called the owner
in repo-facing text, never "dang"). Work in
`~/workspace/computer-use-wayland`, branch `todolist-push`.
HEAD reviewed: 8008662
(`click3-codex-discuss`, Codex discussion position).
Base reviewed against: f0ddd41 (round-2 redteam BLOCK, 13 findings
F1-F13, 15 failing proof tests).
Task start: 06:59 22/11/2026 Asia/Ho_Chi_Minh. All times below are
Asia/Ho_Chi_Minh unless noted. Elapsed: start 06:59 to log commit,
see the commit time.

## Standing rules honored

- Independent review: no coordination with the other round-3
  reviewers, everything questioned, nothing taken from the AMEND4
  worker's log on trust. Every claim below carries its own command,
  output, commit hash, and time (Lauren Tan standard).
- NO em dash (U+2014) or en dash (U+2013) anywhere in this log.
  NEVER ydotool. NO personal info in repo files (owner name the owner only).
- Do NOT edit `tests/test_click3_redteam2.py` or the R7 fixture
  (`tests/test_click2_redteam.py`). Do NOT weaken any test. The
  defective proof tests are named with exact repairs in this log;
  the repair itself is owed by the adjudication lane, not done here.
- Small commits, explicit pathspec immediately after staging, never
  plain `git commit`, never `git add -A`. Push verified with
  `git ls-remote`.
- Log with wall-clock Asia/Ho_Chi_Minh plus elapsed time.
- No self-healing (05:56): this is a review, not my own work.

## Method

- `git fetch origin` at 06:59: branch already up to date with
  `origin/todolist-push` at 8008662, no rebase needed.
- Two clean worktrees, both given the gitignored build artifact
  `native/wtype` copied from the main checkout (the artifact is
  required by `cu._wtype_executable`; without it the 32 inherited
  DesktopPreflight harness tests error with "private wtype helper
  is missing", which is what my first base run showed before the
  copy: Ran 49, failures=14, errors=41):
  - `/tmp/r3c2-base` at f0ddd41 (base, redteam BLOCK).
  - `/tmp/r3c2-head` at 8008662 (HEAD reviewed).
  - `/tmp/r3c2-swap` at 8008662, used only for the item-12
    failing-first swap (old `scripts/first_action.py` from
    cbab398^ dropped in, tests run, file restored by checkout).
- `git diff 0668327..HEAD -- scripts tests` is EMPTY: no production
  or test change landed after the item-4 follow-up 0668327, so HEAD
  8008662 is code-identical to 0668327 for everything under review.
  The commits between them are discussion positions and logs only.
- `git diff f0ddd41..HEAD -- tests/test_click3_redteam2.py
  tests/test_click2_redteam.py` is EMPTY (0 lines): the redteam
  proof tests and the frozen R7 fixture are untouched by the pass.
  No test was weakened or edited by the fix worker.
- `git diff f0ddd41..0668327` contains 0 em dashes and 0 en dashes.
- The AMEND4 worker's log is committed at 6f54a4e (716 lines,
  including the Final verification section). My first read of the
  working-tree copy showed only the first 588 lines because of
  output truncation; the committed version was read in full
  afterwards (lines 560-716) and is cited below where it agrees
  with my independent runs.

## Baseline and HEAD: the 15 proof tests

Base worktree, 07:01: `cd /tmp/r3c2-base/tests &&
python3 test_click3_redteam2.py` gives Ran 49 tests, FAILED
(failures=15). The 15 are exactly the redteam proof tests; the 2
band controls pass and the 32 inherited harness tests pass. This
reproduces the AMEND4 log baseline exactly.

HEAD worktree, 07:01: `cd /tmp/r3c2-head/tests &&
python3 test_click3_redteam2.py` gives Ran 49 tests, FAILED
(failures=4, errors=1). The 5 non-passing tests are:

- FAIL test_band_stacked_fields_low_click_with_x_range_must_not_verify
  (F4, item 3)
- FAIL test_band_wrong_field_unwired_path_reports_ok
  (F5 behavior, item 4)
- ERROR test_region_fallback_readmits_raw_mozinner (F2, items 5-6)
- FAIL test_stale_window_origin_accepted_silently (F3, items 5-6)
- FAIL test_typed_flag_forgeable_by_page_script (F6, item 7)

10 of 15 now pass: F1, F5-source, F7-node, F7-python, F8, F9, F10,
F11, F12, F13. This matches the AMEND4 log Final verification
exactly (same 5 non-passing, same 10 passing). My per-item
verification below confirms each of the 5 is a defective proof
test, not a code miss, and confirms each of the 10 passes is a
real fix, failing at base.

## Item 1. GEOMETRY (F9/F10) - GO, patch

Commit cc964b2 (06:12). `scripts/dom_act.py`, `scripts/zen_dom.py`,
`tests/test_zen_dom.py`.

- Failing-first: both RT2 geometry tests fail at base
  (`test_viewport_origin_factor2_small_window_false_refusal`,
  `test_geometry_check_accepts_factor_forgotten_origin`) and pass
  at HEAD (absent from the HEAD failure list, 07:01 run).
- Fix verified from source: `check_viewport_geometry` gains a
  required `factor` (absent raises `ZenDomError`, closing the
  silent factor-1 default); closure in CSS px, exactness check
  `absolute == window + moz*factor` within 0.5 px; containment in
  screen px; `viewport_origin` passes size as-is in BOTH branches
  with `factor=factor`.
- Full file at HEAD, 07:05: `python3 -m unittest test_zen_dom`
  gives Ran 41 tests, OK. Frozen R7 suite `test_click2_redteam`
  gives Ran 71 tests, OK.
- Patch-vs-rewrite: PATCH, agree. The geometry chain (Hyprland
  origin + mozInner times factor) is correct; the defect was unit
  mixing in the validator and the size branch, not the design. The
  only removal is the silent factor-1 default, which is the F10
  hole. First principles satisfied: the fix removes the thing that
  should not exist (the silent default) instead of hardening it.
- Note, recorded honestly: the F10 refusal comes from the
  fail-closed factor requirement, not from containment alone; the
  F10 inputs are self-consistent at factor 1, so no pure
  consistency check can refuse them. The worker's log states
  this plainly and I confirm it from the test shape.

## Item 2. GATE TRAVERSAL (F8/F11/F12/F13) - GO, patch

Commit c1ea773 (06:19). `scripts/zen_dom.py`,
`tests/test_zen_dom.py`.

- Failing-first: all 4 RT2 traversal tests fail at base
  (`test_arm_typed_flag_misses_iframe_targets`,
  `test_field_value_misses_nested_iframe`,
  `test_field_value_misses_iframe_in_shadow_root`,
  `test_harvest_misses_iframe_targets`) and pass at HEAD.
- Faithful-shim R7 re-run, independently re-verified: I copied the
  HEAD `tests/test_zen_dom.py` into the base worktree and ran
  `TestFaithfulShadowShim` against the OLD `scripts/zen_dom.py`
  at 07:04: Ran 2 tests, FAILED (failures=2). The old code returns
  False on the faithful shim; the new code returns True (both
  tests pass at HEAD, in the 41-test `test_zen_dom` OK run). The
  base tree was restored clean afterwards (`git status` empty).
  This closes the C3 step-8 scope dispute with failing-first
  evidence, as claimed.
- New tests at HEAD, 07:03:
  `test_focus_check_faithful_shadow_shim` and
  `test_hit_check_faithful_shadow_shim`, both pass (part of the
  10-test targeted run, OK).
- Patch-vs-rewrite: PATCH, agree. One shared `find()` with frame
  plus shadow recursion replaces inconsistent per-helper traversal.
  No new architecture, and the inconsistency (some helpers pierced
  shadow roots, none traversed frames) is exactly what the shared
  helper removes.
- Residual, not a blocker: the shared JS is shaped around the
  test-fake dispatch (it must contain no marker substring the
  fakes dispatch on, e.g. activeElement, elementFromPoint). That
  is a test-harness coupling: production JS avoids strings because
  of how the fakes route. It works, but a future fake change can
  silently re-route production JS. Worth a comment in the code;
  it does not change the verdict.

## Item 3. BAND Y ANCHORING (F4) - AMEND, patch (test repair owed)

Commit 62b740e (06:22). `scripts/cu.py`, `scripts/dom_act.py`,
`tests/test_dom_act.py`, `tests/test_type_verification.py`.

- Failing test: `test_band_stacked_fields_low_click_with_x_range_must_not_verify`
  (RT2 F4). Still FAIL at HEAD, 07:01.
- The code fix is verified correct. New contract tests pass at
  HEAD, 07:03 (targeted run, 10 tests OK):
  `test_band_wrong_field_with_rect_range_must_not_verify`
  (stacked field with y_range must not verify) and
  `test_grounded_y_range_is_field_y_in_image_px` (G30:
  [1101.0, 1164.0]). At base, `y_range` occurs 0 times in
  `scripts/cu.py` (HEAD: 25), so the contract did not exist
  before the fix: failing-first for the mechanism.
- The RT2 F4 test is DEFECTIVE. Independent proof, from the
  production source, not from the worker's log:
  `_input_line_changed` without y_range uses y0 = anchor_y - 12,
  y1 = anchor_y + 12 + 1 (symmetric band, `scripts/cu.py`
  lines 1023-1085). The test calls it with anchor 118, pixels
  at y=126, no y_range; the control uses y=110. Both are 8 px
  from anchor 118. Any symmetric band containing 110 must also
  contain 126; any band excluding 126 must also exclude 110.
  Only the field's y-range (not passed) can distinguish them.
  The test therefore cannot pass under any implementation of the
  documented contract while the control
  (`test_band_text_inside_target_field_still_verifies`, y=110
  must verify) also passes. The docstring now states the limit
  plainly ("with no y_range the band is click-anchored, so text
  in a stacked field below the click line can still pass it").
- Required repair (exact): add `y_range=(100, 120)` to the F4
  test call (the upper field A spans y 100..120), keeping the
  pixels at y=126 and the control at y=110. Then re-run the RT2
  suite and confirm F4 passes with the control still passing.
  Repair lane: adjudication (I do not edit proof tests).
- Patch-vs-rewrite: PATCH, agree. The band design is sound; only
  its y anchor was wrong (click point instead of field rect).
  Anchoring both axes on the grounded rect fixes it without a
  new verification channel.

## Item 4. R3a WIRING (F5) - AMEND, patch (test repair owed)

Commit 72120aa (06:23) plus follow-up 0668327 (07:02).
`scripts/cu.py`, `scripts/dom_act.py`, `scripts/first_action.py`,
`tests/test_session_continuation.py`,
`tests/test_session_policy.py`.

- Failing test: `test_band_wrong_field_unwired_path_reports_ok`
  (RT2 F5 behavior). Still FAIL at HEAD, 07:01: result ok True,
  `type_verified` True via `input-line-band`, `type_verified_basis`
  `input-line-band`.
- The wiring fix is verified correct. The F5 source test
  (`test_codeexec_and_cli_act_paths_never_supply_x_ranges`)
  fails at base (`'type_x_ranges' not found in ... def act ...`,
  base run) and passes at HEAD. `type_x_ranges` and
  `type_y_ranges` are threaded through the CLI act path,
  `CodeExecBackend.act`, and the first_action fallback.
  `BrowserAdapter.act` does not exist (only a docstring mention,
  corrected to `CodeExecBackend.act`): confirmed by the commit
  and by the base source test output, which shows
  `CodeExecBackend.act` as the only act path.
- The F5 behavior test is DEFECTIVE. Independent proof, by
  mutual inconsistency with a control test, not by assertion:
  the behavior test calls `cu.desktop_act` DIRECTLY (click
  (15,10), pixels x 0..11 at y=10, no ranges, no type_check)
  and expects ok False. The control test
  `test_click_type_text_in_input_line_verifies`
  (`tests/test_type_verification.py` lines 120-132) calls
  `cu.desktop_act` DIRECTLY (click (10,10), pixels x 12..17 at
  y=10, no ranges, no type_check) and expects ok True via
  `input-line-band`. The two calls have the same shape; no
  threading change can affect either, because neither passes
  through a wired path. Implementing the task's "or" branch
  (band-only unverified when no ranges supplied) would flip the
  control to ok False. The worker's decision to implement only
  the threading branch is correct, and the behavior test as
  written is unimplementable without breaking the control.
  (Left-vs-right of the click is not a distinguishing feature:
  text typed into an empty field lands at the field's left edge,
  which is left of the click, exactly the F5 pixel shape; the
  band has no field geometry without ranges.)
- Required repair (exact): rewrite the behavior test to go
  through a WIRED path (CodeExecBackend.act with dom_session
  plus dom_selector, or the CLI act path) where ranges ARE
  supplied, with wrong-field pixels on the anchor line, and
  expect ok False with `error_code` `type_unverified`. The
  direct-call shape must keep verifying via the band, per the
  control. Repair lane: adjudication. Re-run the RT2 suite
  after the repair.
- Follow-up 0668327, verified: the item-4 change broke 17
  session tests (act_boundary fakes rejected the new kwargs
  with TypeError). The fix makes both fakes accept `**extra`
  and forward it to the real `desktop_act`. At HEAD, 07:03:
  `python3 -m unittest test_session_continuation
  test_session_policy` gives Ran 28 tests, OK. This is a
  stale-fake fix, not a weakening: assertions unchanged, the
  fake mirrors the production interface. Process note: an
  interface change that breaks 17 tests should have been
  caught by a full discover before the item-4 commit, not
  after; the worker did catch it in the final discover and
  fixed it, which is the correct order in the end.
- Patch-vs-rewrite: PATCH, agree. The ranges already existed at
  the focus_type layer and only needed threading to three call
  sites.

## Items 5-6. WINDOW_BOUNDS REFUSAL + LIVE RE-READ (F2/F3) - AMEND, patch with removal (test repair owed)

Commit b44a5ea (06:26). `scripts/dom_act.py`,
`scripts/zen_dom.py`, `tests/test_dom_act.py`,
`tests/test_zen_dom.py`.

- Failing tests: `test_region_fallback_readmits_raw_mozinner`
  (F2, ERROR at HEAD) and
  `test_stale_window_origin_accepted_silently` (F3, FAIL at HEAD).
- The code fix is verified correct. New tests pass at HEAD,
  07:03 (targeted run, 10 tests OK):
  `test_ground_input_refuses_meta_without_window_bounds`,
  `test_ground_input_refuses_stale_window_origin` (live
  [2600,914] vs meta [2533,914]), and
  `test_ground_input_accepts_matching_live_origin`. At base,
  `live_window_origin` occurs 0 times in `scripts/zen_dom.py`,
  and the base RT2 run shows F2 returning the raw mozInner pair
  `[240, 8]` as the origin with no error: failing-first for the
  mechanism.
- F2 is DEFECTIVE. Independent proof: at HEAD the test ERRORS
  with `dom_act.DomActError: meta needs window_bounds for the
  window origin (mozInnerScreen is window-relative); a
  screen-scope observation has no window to ground against,
  re-observe the window` (traceback from the 07:01 HEAD run).
  That refusal IS the specified fix; the test has no
  assertRaises and asserts a ground return. The true origin
  [2749,922] is not derivable from the given meta
  (`{image_size:[1920,1080], region:[0,0,3840,2160],
  monitor_box:[0,0,3840,2160]}`); only a live hyprctl re-read
  could supply it, and none exists on the VM. No return value
  can satisfy the test as written once the fix refuses.
- F3 is DEFECTIVE. Independent proof, numeric: at HEAD the
  test fails at line 243 on the distance assertion, AFTER the
  first assertion passes, so `viewport_origin([100,100],
  [1863,1176])` still returns [340,108]. I recomputed with the
  production `fastpath.dom_rect_to_image_point` (07:03):
  origin [340,108] maps the rect to (323.0, 620.25); the true
  origin [2749,922] maps it to (1527.5, 1027.25); distance
  1271.4 image px. The test demands BOTH `viewport_origin ==
  [340,108]` AND distance under 10. Only [2749,922] satisfies
  the distance, and it fails the equality. No return value
  satisfies both assertions. The test also calls
  `viewport_origin` directly, so no ground-time re-read can
  affect it.
- Required repairs (exact):
  - F2: change the test to assert the refusal, e.g.
    `assertRaises(DomActError)` around `ground_input` with the
    window_bounds-less meta. Repair lane: adjudication.
  - F3: split into two tests. (a) The direct `viewport_origin`
    call documents the stale value ([340,108]) and must NOT
    also demand the true point. (b) A ground-time test:
    `ground_input` with a stale meta plus a live origin that
    disagrees must refuse (this is already pinned by the new
    `test_ground_input_refuses_stale_window_origin`; the F3
    rewrite should assert that shape, not the contradictory
    pair). Repair lane: adjudication. Re-run the RT2 suite
    after both repairs.
- Patch-vs-rewrite: PATCH WITH A REMOVAL, agree. The region
  fallback is removed outright (it re-admitted the raw mozInner
  pair, the R1 hole); the live re-read is added as a check, not
  a new architecture. Fail-closed is the design and the patch
  implements it.
- Evidence limit, recorded: the live Hyprland re-read cannot be
  exercised on this VM (no hyprctl, no `/run/user/1000/hypr/`);
  it is proven by the FakeDomSession model plus the refusal
  paths. Live confirmation on the laptop is still owed.

## Item 7. R10 FLAG REDESIGN (F6/F7) - AMEND, redesign (test repair owed)

Commit 49081aa (06:34). `scripts/zen_dom.py`,
`tests/test_dom_act.py`, `tests/test_zen_dom.py`.

- Failing test: `test_typed_flag_forgeable_by_page_script`
  (RT2 F6). Still FAIL at HEAD, 07:01.
- The redesign is verified correct. F7 node
  (`test_typed_flag_sticky_across_js_set_value`) and F7 python
  (`test_typed_flag_sticky_python_level`) fail at base and pass
  at HEAD. The new node regression test
  `test_typed_flag_not_forgeable_via_window_property` passes at
  HEAD, 07:03 (targeted run, 10 tests OK): production arm and
  typed_flag JS under node, page forges the old window property,
  zero trusted input events, result `{"armed":true,"flag":false}`.
  The window property is gone; state lives in the arm's closure
  plus a locked getter with no setter
  (Object.defineProperty, non-configurable).
- F6 is DEFECTIVE in two ways. Both confirmed by my own
  independent repro, 07:03, reusing the test's own shim and
  capture helpers with the forge line wrapped in try/catch:
  output `{'armed': True, 'flag': False, 'value': 'hello',
  'forgeThrew': "Cannot set properties of undefined (setting
  '#msg-input')"}`.
  1. The forge line `window.__agentCuTyped['#msg-input'] =
     true;` throws TypeError because the arm no longer creates
     `window.__agentCuTyped`. The forgery attempt itself throws
     before the assertions run. With the line guarded, the flag
     assertion (`assertFalse(out['flag'])`) PASSES: flag is
     False. The substantive security property is fixed.
  2. The value assertion `assertNotEqual(out['value'], 'hello')`
     can never pass: `out['value']` is the field's value, and
     the page script set the field to 'hello', so the value IS
     'hello'. My repro confirms value == 'hello' while flag ==
     False. The assertion conflates the field value with the
     verify outcome.
- Required repair (exact): guard the forge line in try/catch
  (a forgery attempt that throws is itself evidence the surface
  is gone) and replace the value assertion with the actual
  security property: assert `out['value'] == 'hello'` AND
  `out['flag'] is False` (value set, flag clear). Repair lane:
  adjudication. Re-run the RT2 suite after the repair.
- Patch-vs-rewrite: REDESIGN, agree. Any writable window state
  is forgeable by construction, so no hardening of the window
  property could close R10; removing the surface and moving
  state to a closure plus locked getter is the correct call.
  The decoy window property (kept only so the defective F6
  forge line would not throw) was rightly rejected: it would
  keep a piece that should not exist to accommodate a defective
  test line.
- Residual, recorded honestly (from the worker's log, confirmed
  as a real limit): a page that pre-defines the locked property
  name with a non-configurable forged getter before arming
  would defeat the check. That requires knowing the property
  name and running before the arm, outside the R10 attacker
  model (a page script setting the value). F6/F7 as proven are
  closed. This residual does not change the verdict.

## Item 8. SET_VALUE SANITIZATION (F1) - GO, patch

Commit af0fa87 (06:38). `scripts/cdp.mjs` only.

- Failing-first: the F1 test
  (`test_set_value_newline_text_fails_verification`) fails at
  base and passes at HEAD. The failure message at base is the
  claimed one (CRLF text into a textarea failed although the
  field holds the normalized value).
- Fix verified from the diff: both read-back checks compare
  `e.value` against the SANITIZED form (input: strip CR and LF;
  textarea: CRLF and CR become LF), computed with
  `String.fromCharCode` so the template needs no backslash
  doubling when re-evaluated. Change detection and the maxlength
  pre-check are untouched, correctly out of scope.
- `node cdp_snapshot.mjs` passes at HEAD, 07:03 ("all cdp
  snapshot, redaction, fill, payload, no_after and scope
  regressions pass"). `test_cdp_snapshot.py` gives Ran 2 tests,
  OK.
- Patch-vs-rewrite: PATCH, agree. The set_value template (native
  setter write plus read-back plus change-only events) is the
  right design; only the compared value was wrong.
- Evidence limit, recorded: live-browser confirmation of the
  HTML Standard sanitization rule is still owed (no browser on
  this VM). The proof is the node-shim run of the REAL template
  against a spec-faithful fake DOM plus the standard citation.
  That is an evidence limit, not a code defect. GO with the
  caveat recorded.

## Item 9. SUPPLY-CHAIN TESTS (C2 A3) - GO, tests only

Commit 44c15bb (06:40). `tests/test_dom_act.py`,
`tests/test_first_action.py` only, no production change.

- All 3 new tests pass at HEAD, 07:03 (targeted runs):
  `test_grounded_x_range_is_field_x_in_image_px` (G30 field,
  [86.0, 526.0]),
  `test_focus_type_forwards_grounded_ranges_to_act_fn`
  (recording wrapper proves both ranges arrive:
  [[86.0, 526.0]] and [[1101.0, 1164.0]]),
  `test_fallback_with_window_observation_supplies_ranges`
  (first_action supplies both ranges on window scope).
- Failing-first, partial, stated honestly: at base,
  `focus_type` forwarded x_range only (base
  `scripts/dom_act.py` line 501: `type_x_ranges=type_ranges`,
  no y-range) and the first_action fallback supplied x_range
  only (item 4 added y_range alongside it), so the two
  forwarding tests would fail at base. The grounded_x_range
  unit test is a pure pin: `grounded_x_range` already existed
  at base (base line 185), so that one test would pass at base
  too. That is fine for a pin; the wiring it pins was the
  missing piece, proven failing at base by the F5 source test.
- The FakeZenSession gains the grounding methods ground_input
  needs (locate, viewport_origin, hit_check); the screen-scope
  fallback test is unchanged and still supplies no ranges.
- Patch-vs-rewrite: TESTS ONLY, agree. They pin the item 3-4
  wiring so a silent drop is caught. No production change to
  judge.

## Item 10. SNAPSHOT EVENT TEST (C1 G4) - GO, tests only

Commit e912ad4 (06:41). `tests/cdp_snapshot.mjs` only, 9 lines.

- The mirror case passes at HEAD, 07:03 (`node
  cdp_snapshot.mjs`: "all cdp snapshot, redaction, fill,
  payload, no_after and scope regressions pass"). Set_value from
  'hello' to 'world' lands the value and fires input then
  change, in that order. Before this item the suite asserted
  only the zero-event side, so a template that never dispatched
  would have passed.
- Patch-vs-rewrite: TESTS ONLY, agree. The production dispatch
  (item 8's template) is proven by the pin, not changed.

## Item 11. DESIGN-DOC FIXES (C3 G3/G4) - GO, remove

Commit 8d75135 (06:41).
`improvements/worker-coord-click2-log.md` only, docs.

- Verified by grep at HEAD, 07:03: the only remaining "V4"
  mention in the doc is inside the B18 drop note itself
  ("B18 drops the V4 caret signal: caret position is forgeable
  by page JS, the trusted-input flag is the discriminator; a
  caret-at-end check would false-fail mid-text edits and IME
  composition"). The "V4 caret position check" clause is gone
  from the line 61 bundle and step 4 now reads "V1+V2+V3+V11".
  The tab-switch protocol line is marked `**SUPERSEDED
  (2026-11-22, AMEND4 item 11)**` and kept visible (line 237);
  the benchmark target (clone1 Brave plus clone2 Chrome on ws2)
  is recorded.
- Patch-vs-rewrite: REMOVE, agree. The V4 caret signal should
  not exist as a verification promise (forgeable, and it
  false-fails legitimate edits); the trusted-input flag replaces
  it. The tab-switch protocol is superseded, not patched: the
  benchmark target changed, so the protocol built for the old
  target goes away.

## Item 12. ACT-NOW ENVELOPE (CL1-SWEEP) - GO, redesign

Commit cbab398 (06:46). `scripts/first_action.py`,
`tests/test_first_action.py`.

- Failing-first, independently verified by swap, 07:04: in the
  `/tmp/r3c2-swap` worktree I replaced `scripts/first_action.py`
  with the pre-item-12 version (cbab398^) and ran the 4 new
  tests: Ran 4 tests, FAILED (failures=4). With the new code
  the same 4 pass at HEAD, 07:03 (targeted run, 5 tests OK
  including the item-9 fallback test):
  `test_session_after_is_scope_matching_not_screen`,
  `test_fallback_after_is_scope_matching_not_screen`,
  `test_after_without_result_after_captures_fresh_window`,
  `test_screen_observation_key_batch_refused_before_overlay`.
- Full file at HEAD, 07:05: `python3 -m unittest
  test_first_action` gives Ran 68 tests, OK.
- Root cause confirmed from the commit and the code: act-now
  always captured its envelope `after` with `observe_screen`
  regardless of input scope, overwriting desktop_act's
  scope-matching after-capture, so EVERY act-now after-image
  was screen-scoped by construction and reusing one for a
  key/type step always failed. The envelope now carries BOTH
  `after` (scope-matching, chainable) and `after_screen`
  (full-monitor, verification only). The "documented
  non-chainable" claim is verified in the code itself
  (`scripts/first_action.py` lines 730-732: "'after_screen' is
  the full-monitor capture, for verification only, documented
  non-chainable: reusing a screen-scope after-image for a
  key/type step always fails (CL1-SWEEP)"). The scope check
  runs before the overlay attempt (the 998 ms CL1-SWEEP waste
  is removed for the refused shape).
- Patch-vs-rewrite: REDESIGN, agree. The after-capture was
  defective by construction (always screen-scoped). The
  both-fields shape is the right call over a one-line
  scope-matching patch: the verification use of the screen
  capture is real, and the scope-matching after costs zero
  extra captures (desktop_act already computes it). Removal
  of `after` was rightly rejected for the same reason.
- Note: item 12 is after-scope (CL1-SWEEP, not one of the 13
  redteam findings). It is the independent investigation the
  05:56 no-self-healing rule required, and its finding goes
  further than the parent's own diagnosis. That is exactly
  what the rule is for.

## Full-suite files at HEAD (per-file, 07:05)

- `test_zen_dom`: Ran 41 tests, OK.
- `test_dom_act`: Ran 19 tests, OK.
- `test_type_verification`: Ran 61 tests, OK.
- `test_first_action`: Ran 68 tests, OK.
- `test_session_continuation`: Ran 11 tests, OK.
- `test_session_policy`: Ran 17 tests, OK.
- `test_cdp_snapshot`: Ran 2 tests, OK.
- `test_click2_redteam` (frozen R7): Ran 71 tests, OK.

## Full discover at HEAD

### My run (no PYTHONPATH, 07:04-07:14)

Command (from `tests/`):

    python3 -m unittest discover -s .

Result: Ran 1897 tests in 613.410s, FAILED (failures=16, errors=11,
skipped=17). Log: `/tmp/r3c2-discover-head2.log` (worktree scratch,
not committed).

The 27 problems break down as follows:

- 5 RT2 adjudicated defectives (F2 error; F3, F4, F5-behavior, F6
  failures). Expected, see the item sections.
- 2 environmental tesseract (tc02_controller, 1 failure plus 1
  error: "tesseract is unavailable; refusing to assume text
  presence").
- 4 pre-existing errors (test_a11y_skeleton import,
  test_cursor_file setUpClass, test_perf_evidence x2).
- 16 extra, ALL environmental, none caused by AMEND4 code:
  - test_ime_cleanup, 8 failures: timing flakes under 5x
    concurrent load (613 s run vs the worker's 388 s solo
    run). Traceback shows the child timing out on fcitx5 state
    change ("caught RuntimeError, caught_msg fcitx5 state
    change timed out") instead of the expected ValueError.
  - test_core, 2 failures: the isolated child fails with
    "ModuleNotFoundError: No module named 'cu'". That is MY
    invocation difference: I ran discover without PYTHONPATH,
    while the worker's command sets
    `PYTHONPATH=../scripts:.`. The child inherits the env, so
    it cannot import `cu`. Not an AMEND4 failure.
  - test_cursor_session, 4 errors, and test_wtype_native
    setUpClass, 1 error: `tempfile.TemporaryDirectory` fails
    with `FileNotFoundError: No usable temporary directory`
    (see the EPERM storm below).
  - test_phase3_cleanup (FunctionTestCase test_cli_exit_codes),
    1 failure: "desktop NOT clean: session guardian still
    running: pid 42974". That pid is gone now; it was a
    transient leftover from a concurrent reviewer's run
    (cross-run contamination, not AMEND4).

Count reconciliation (proves the totals, not just the failures):
the loader counts 1928 tests at HEAD without running. My run
executed 1897 because two setUpClass failures kept their tests
unrun: 1928 - 8 (test_cursor_file, pre-existing) - 23
(test_wtype_native, tempfile EPERM) = 1897 exactly. The
worker's Ran 1920 is 1928 - 8 (cursor_file only; wtype_native
passed in the worker's clean run). The totals differ only by
which class-level setups failed, not by test content.

Base control (decisive): the same files fail WITHOUT AMEND4
code. Individual runs at base, 07:18: test_ime_cleanup Ran 14,
errors=10; test_core Ran 39, errors=37; test_cursor_session
Ran 36, errors=35. If base fails the same way, AMEND4 cannot
be the cause.

Corroboration, not evidence: another reviewer's full discover
on the dirty main-checkout tree finished Ran 1927, failures=7,
errors=4. Its list shows the same pattern (RT2 5, tesseract 2,
pre-existing 1, plus flakes: ime SIGTERM, cursor_session,
phase3). That tree has another worker's uncommitted script
modifications and a different invocation, so it is NOT
single-commit evidence and I do not use it as such. It only
corroborates that the extra failures vary run to run.

### EPERM storm: a clean full discover at fixed HEAD is still owed

Two attempts to run the exact worker command at fixed HEAD
8008662 in the clean worktree died to a transient sandbox
EPERM storm:

- Attempt 1 (~07:22, setsid nohup, log
  `/home/hatch/r3c2-discover-head3.log`): no process survived,
  0-byte log, no EXIT line.
- Attempt 2 (~07:32, plain background launch, pid 64367, same
  log path): alive at +20 s, gone by +60 s, 0-byte log, no EXIT
  line.

The storm is proven, not assumed. `tempfile.gettempdir()`
raises `FileNotFoundError: No usable temporary directory found`
in bad execs and works in good ones. Replicating
`_get_default_tempdir` step by step shows `os.open` with
`_bin_openflags` (which includes O_NOFOLLOW) failing with
`PermissionError [Errno 1] Operation not permitted`, while the
same open without O_NOFOLLOW succeeds; minutes later the
O_NOFOLLOW open succeeds in another exec. Even a shell `echo`
failed once with "write error: Operation not permitted". This
is the same EPERM class as the 2026-11-10 lesson (exec writes
failing with EPERM), recurring transiently. It comes and goes
per exec, so a later attempt may land in a good window.

Conclusion: NO failure in any full run (worker's 1920/5/6,
mine 1897/16/11, the other reviewer's 1927/7/4) implicates
AMEND4 production code beyond the 5 known defective proof
tests. But a clean full discover at a fixed HEAD is still
owed and must be run in a good window before close-out; the
numbers above are not a substitute for it.

## Verdict summary

- GO (7): item 1 geometry, item 2 traversal, item 8 set_value,
  item 9 supply-chain tests, item 10 snapshot test, item 11
  design docs, item 12 act-now envelope.
- AMEND (4 rows, 5 defective proof tests): item 3 (F4),
  item 4 (F5 behavior), items 5-6 (F2, F3), item 7 (F6).
  Every AMEND is a TEST repair, not a code rework: the code
  fix in each case is verified correct with failing-first
  evidence, and the named proof test cannot pass as written.
  Repair each test exactly as specified in its item section,
  re-run the RT2 suite, and the item becomes GO. No item is
  BLOCK: no fix is wrong, unsafe, or architecturally mistaken.
- BLOCK (0).
- Patch-vs-rewrite judgments: patch for items 1, 2, 3, 4, 8;
  patch with a removal for items 5-6 and item 11; redesign for
  items 7 and 12; tests only for items 9 and 10. I agree with
  the worker's own patch-vs-rewrite summary in the AMEND4 log
  (6f54a4e) on every item, with the independent evidence above
  as the basis, not the worker's say-so.
- Cross-check against the AMEND4 log Final verification: the
  worker's RT2 numbers (Ran 49, failures=4, errors=1; 10 of 15
  pass) reproduce exactly in my independent runs, and its
  defective-test proofs reproduce from source and from my own
  repros (F4 symmetry from the band code, F5 mutual
  inconsistency with the control, F2 refusal trace, F3 numeric
  1271.4 px, F6 guarded-forge repro). Where the worker's log
  and my runs differ, the difference is noted above (the
  item-9 grounded_x_range pin would pass at base; the item-4
  breakage should have been caught before commit). Nothing in
  the worker's log is contradicted.

## Open items for the adjudication lane (not mine to do)

1. Repair the 5 defective proof tests exactly as specified
   (F4 y_range, F5 wired-path rewrite, F2 assertRaises, F3
   split, F6 guarded forge plus flag-only value assertion),
   then re-run the RT2 suite and confirm 15 of 15 pass.
2. Live-browser confirmation still owed: F1 sanitization rule,
   F8/F9 live-DOM runs, items 5-6 live Hyprland re-read. All
   need the laptop; none can be done on this VM.
3. The 2 environmental tesseract failures (tc02_controller)
   are unrelated to AMEND4; installing the binary is out of
   this pass's scope.

## Process notes

- At 07:05 the main-checkout working tree showed modified
  scripts (`M scripts/code_exec.py codemode.py cu.py
  first_action.py sync-installed.py zen_dom.py`) from another
  worker's concurrent work. Those modifications are NOT mine
  and are NOT part of this review: my review is of committed
  HEAD 8008662, verified in clean pinned worktrees. My commit
  below touches ONLY this log file, explicit pathspec.
- Three other full-discover runs were concurrently active on
  this VM during my review (other reviewers). I started no
  additional full discover beyond my one HEAD run, and I killed
  nothing.
- Branch moved during review: HEAD was 8008662 when I started
  (06:59); by 07:33 local HEAD was 17fdb9b (Y1b fix by another
  worker) with origin at af0d0a2. This review covers 8008662
  only, as stated at the top; the Y1b commits are out of scope.
- LANDING BLOCKED (07:34-07:37): this log could not be
  committed yet. `git fetch origin` fails ("unable to write
  loose object file: Operation not permitted"), and `git add`
  fails the same way (8 attempts over 07:34-07:37). Diagnosis:
  the sandbox EPERM wave blocks O_RDWR file creation (proven:
  `os.open` with O_RDWR fails EPERM in `.git/objects`, `/tmp`,
  and `/home/hatch`, while O_WRONLY `touch` and python `open`
  in `'w'` mode succeed; the object store itself is fine and
  the disk has 100G free). Recovery: when the wave passes,
  run `git add improvements/worker-click3-r3c2-review-log.md`
  then `git commit -m "click3-r3c2: round-3 council review of
  AMEND4 fix pass (7 GO, 4 AMEND rows on 5 defective proof
  tests, 0 BLOCK; HEAD 8008662)" --
  improvements/worker-click3-r3c2-review-log.md`, then push
  and verify with `git ls-remote`. The file on disk is
  complete (763 lines, 0 em/en dashes); only the commit is
  owed.

## Addendum (07:33, parent update CLOSEOUT-VERIFY landed 07:31)

Added without rewriting the verdicts above, per the parent's
instruction. Facts from the parent's update, attributed to
CLOSEOUT-VERIFY (07:31), plus my answers to the live question
it raises.

1. CORRECTION, Codex RT claim: it was qualified, not 15/15.
   The Codex log says "The 15 non-contradictory RT proof tests
   passed": the 15 named tests are 13 proofs plus 2 controls,
   and F2 and F3 are EXCLUDED as "non-contradictory". F2 and F3
   fail or error on BOTH lanes. I do not cite Codex as passing
   15/15 proof tests anywhere in this log, and I will not.
2. DIVERGENCE, the live question for the defective-test repair
   decision: F4, F5, and F6 PASS on the Codex lane and FAIL on
   the VM lane (judged defective there). My answers, per test:
   - F5: the Codex pass does NOT change my repair decision; it
     confirms it. The Codex lane's stricter item-4 (the "or"
     branch: band-only result unverified without grounded
     ranges) BREAKS the pre-existing relay test
     `test_click_type_verifies_through_input_line_band`. That
     is the counterfactual the VM lane never had to run: the
     "or" branch buys the F5 behavior pass by breaking a
     pre-existing test. The VM lane deliberately rejected that
     branch and keeps the relay test passing. Repair decision
     stands: rewrite the behavior test to go through a WIRED
     path; do NOT implement the "or" branch.
   - F4 and F6: HOW Codex passes them is not in the material I
     reviewed (no Codex-lane diff in front of me), so I cannot
     verify the mechanism. My defect proofs are facts about
     the VM code-plus-test pair (F4 symmetry from the band
     code; F6 forge-line throw plus value conflation, both
     reproduced by my own runs). A Codex pass must come from a
     different production change or a test change. What would
     settle it: the Codex lane's exact diff for items 3 and 7,
     plus proof its F4 and F6 passes break no other test (the
     item-4 case proves a pass can hide a break). Until that
     evidence is on the table, my AMEND verdicts for items 3
     and 7 stand, with the divergence flagged open for
     adjudication. I do not overturn a proven defect on an
     unverified pass.
   - F2 and F3: both lanes agree they fail or error. That
     strengthens my AMEND verdicts for items 5-6: the tests
     are unfixable as written on either lane.
3. Codex-lane regression: its stricter item-4 breaks
   `test_click_type_verifies_through_input_line_band`. See the
   F5 answer above. The VM lane keeps that test passing.
4. Close-out corroboration: item-12 regression tests 4/4 PASS
   (three runs) and the RT set Ran 49, failures=4, errors=1,
   matching AMEND4's 6f54a4e exactly. That matches my
   independent HEAD runs exactly: my item-12 swap test (4 fail
   on old first_action.py, 4 pass on new code) and the RT suite
   Ran 49, failures=4, errors=1, run twice (direct script and
   module invocation with PYTHONPATH). Corroboration recorded.
5. Clean full discover: still owed at a fixed HEAD (the EPERM
   storm blocked it, see the discover section above). Mixed-tree
   numbers are not single-commit evidence. My log follows that
   rule: the other reviewer's 1927/7/4 run is cited only as
   corroboration, never as evidence for HEAD 8008662.

No verdict in this log changes on the update. The update
strengthens two of them (item 4, via the Codex regression as
counterfactual proof; items 5-6, via cross-lane agreement on
F2/F3) and leaves two open pending one piece of evidence (the
Codex diff for items 3 and 7).
