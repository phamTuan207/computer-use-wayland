# CLICK3-R3C1 review log: round-3 council review of the AMEND4 fix pass

Worker CLICK3-R3C1, round-3 council reviewer 1 for the AMEND4 fix pass.
Owner: the owner (call the user the owner in repo-facing text, never "dang").
Work in `~/workspace/computer-use-wayland`, branch `todolist-push`.
Independent review: no coordination with the other round-3 reviewers.
Review start: 07:00 22/11/2026 Asia/Ho_Chi_Minh.
HEAD reviewed: 8008662 (`click3-codex-discuss`, full hash
800866256724e65404e58cf763a3b37fe038ca2c).
Base: f0ddd41 (round-2 redteam BLOCK, 13 breaking findings F1-F13,
15 failing proof tests, 17 tests in `tests/test_click3_redteam2.py`).
All times below are Asia/Ho_Chi_Minh unless noted. Elapsed at log
write: about 40 minutes.

## Standing rules honored

- Full access. NO em dash (U+2014) or en dash (U+2013) anywhere in this
  log or in any file I touched. NEVER ydotool. NO personal info in repo
  files (owner name the owner only). Log everything with wall-clock +
  elapsed.
- Commit with an EXPLICIT pathspec immediately after staging, never
  plain `git commit`, never `git add -A`. Verify every push with
  `git ls-remote`.
- Do NOT edit the redteam proof tests or the R7 fixture. Do NOT weaken
  any test. Verified below: `git diff f0ddd41..8008662` is 0 lines for
  both `tests/test_click3_redteam2.py` and `tests/test_click2_redteam.py`.
- No self-healing (05:56): this is a review, not my own work. Where a
  proof test is defective I prove the defect independently and name the
  repair; I do not fix the production code and I do not edit the test.
- First principles (06:01): for each item I asked whether the piece of
  design should exist at all, and judged patch vs rewrite on that basis.
- Evidence with every claim (Lauren Tan standard): test command,
  output, commit hash, time log.

## HEAD drift and a contaminated first discover run

- The task said HEAD f0ddd41, but the branch had moved; I reviewed the
  HEAD at review start, 8008662, which contains all 12 AMEND4 items
  (cc964b2, c1ea773, 62b740e, 72120aa, b44a5ea, 49081aa, af0fa87,
  44c15bb, e912ad4, 8d75135, cbab398, plus follow-up 0668327).
- At 07:09 the branch moved again under me: local HEAD is now 3f1b951
  (Y1b fix 1e, unpushed; origin at 6f54a4e), and another worker is
  actively editing in this same checkout: `git status` shows uncommitted
  modifications to scripts/code_exec.py, scripts/codemode.py,
  scripts/cu.py, scripts/first_action.py, scripts/zen_dom.py, file
  times 07:06 to 07:08. I touched none of those files. All evidence in
  this log is therefore anchored to 8008662, not to the moved HEAD.
- My first full-discover run in the main checkout started about 07:06
  and ran while those files were being modified mid-run, so its result
  is CONTAMINATED and I discard it. I re-ran the whole verification
  battery in a clean worktree at 8008662
  (`/tmp/click3-r3c1-head`, `git status` empty, `native/wtype` copied
  in because it is a gitignored build artifact, `.gitignore:13`).
  Every number in the per-item sections below was re-confirmed in that
  clean worktree at 07:09, except where a section says the run was in a
  stated older worktree (base, item-12 old code).

## Baseline and HEAD, failing-first (RT2 suite)

- Base worktree `/tmp/click3-r3c1-base` at f0ddd41 (native/wtype copied
  in, same gitignored artifact reason; without it the DesktopPreflight
  tests error with `private wtype helper is missing`, which is a
  worktree artifact gap, not a finding):
  `python3 tests/test_click3_redteam2.py`, 07:00, Ran 49 tests,
  FAILED (failures=15). The 15 failures are exactly the 15 proof tests;
  the 2 redteam controls pass. This matches the AMEND4 log baseline.
- HEAD worktree at 8008662, clean, 07:09:
  `python3 tests/test_click3_redteam2.py`, Ran 49 tests,
  FAILED (failures=4, errors=1). The 5 still failing are exactly the 5
  the AMEND4 worker claimed defective:
  test_typed_flag_forgeable_by_page_script (F6),
  test_region_fallback_readmits_raw_mozinner (F2, now ERROR not FAIL),
  test_stale_window_origin_accepted_silently (F3),
  test_band_stacked_fields_low_click_with_x_range_must_not_verify (F4),
  test_band_wrong_field_unwired_path_reports_ok (F5 behavior).
  The other 10 failing-first proof tests now pass, plus the 2 controls:
  F1, F5 source test, F7 node, F7 python, F8, F9, F10, F11, F12, F13.
- Frozen files: `git diff f0ddd41..8008662 -- tests/test_click3_redteam2.py`
  is 0 lines; same for `tests/test_click2_redteam.py`. No em dash or en
  dash in the AMEND4 diffs (`git diff f0ddd41..8008662 -- scripts/ tests/`
  grep counts 0 and 0).

## Item 1. GEOMETRY (F9/F10) - GO, commit cc964b2

- Failing-first: both proof tests fail at base, pass at HEAD.
  F9 test_viewport_origin_factor2_small_window_false_refusal: ok.
  F10 test_geometry_check_accepts_factor_forgotten_origin: ok.
- What I checked in the diff: `check_viewport_geometry` gains
  `factor=None`, required, raises ZenDomError when absent or invalid;
  closure in CSS px with the size as-is; exactness check
  `absolute == window + moz*factor` within 0.5 px; containment in
  screen px (`window + size*factor`); `viewport_origin` passes size
  as-is in BOTH branches (given Hyprland logical size and the None
  outerWidth/Height fallback, both already CSS px numerically) and
  passes `factor=factor`. The second caller in `dom_act.py:359`
  (`ground_many_one_shot`) also passes size as-is with `factor=factor`.
- Suite: `python3 -m unittest test_zen_dom test_dom_act` in the clean
  worktree, Ran 60 tests, OK.
- Patch vs rewrite: PATCH, keep. The geometry chain (Hyprland origin +
  mozInner times factor) is correct; the defect was unit mixing in the
  validator and the size branch, not the design. The only removal is
  the silent factor-1 default, which is the F10 hole. No rewrite
  candidate.

## Item 2. GATE TRAVERSAL (F8/F11/F12/F13) - GO, commit c1ea773

- Failing-first: all 4 proof tests fail at base, pass at HEAD.
  F8 test_arm_typed_flag_misses_iframe_targets: ok.
  F11 test_harvest_misses_iframe_targets: ok.
  F12 test_field_value_misses_nested_iframe: ok.
  F13 test_field_value_misses_iframe_in_shadow_root: ok.
- What I checked in the diff: one shared `_FIND_JS` (pierce + framesOf
  + find, depth cap 5, frames detected by `contentWindow` presence,
  never tagName, cross-origin fail-closed via try/catch) used by
  locate, hit_check, focus_check, field_value, verify_typed,
  arm_typed_flag, sent_bubble_contains, harvest, with `_DEEP_ACTIVE_JS`
  and `_FRAME_POINT_JS` alongside. The new `TestFaithfulShadowShim`
  (2 node tests) passes in the clean worktree; the frozen R7 test
  (unfaithful shim) still passes inside the 131-test run below.
- Suite: `python3 -m unittest test_zen_dom test_dom_act
  test_click2_redteam`, Ran 131 tests, OK.
- Patch vs rewrite: PATCH, keep. The find/pierce/traverse shape is the
  right design; it was applied inconsistently (some helpers pierced
  shadow roots, none traversed frames). Unifying on one shared helper
  removes the inconsistency without a new architecture. No rewrite
  candidate.

## Item 3. R3a BAND ANCHORING (F4) - AMEND, commit 62b740e

- Failing test: test_band_stacked_fields_low_click_with_x_range_must_not_verify.
  It still fails at HEAD, exactly as at base.
- The production fix is SOUND. `_input_line_changed` gains `y_range`
  (band y is the field y-range when given, else anchor plus/minus 12);
  `grounded_y_range` mirrors `grounded_x_range`; `type_y_ranges`
  threads through `desktop_act` and `focus_type`. The fix's own tests
  pass in the clean worktree (`test_type_verification` +
  `test_dom_act`, Ran 80 tests, OK), including the desktop_act level
  test where stacked lower-field pixels report ok False with
  error_code type_unverified, and the positive control still verifies.
- The proof test is DEFECTIVE, proven independently, not on the
  AMEND4 log's word. I ran the symmetry probe in the clean worktree:
  pixels at y=110 and y=126, anchor 118, x_range (100, 300), no
  y_range: both verify (True, True). With y_range (100, 120): 110
  verifies, 126 does not. The test passes no y_range, and its two
  pixels are both 8 px from the anchor, so any symmetric band
  [118-h, 118+h] containing 110 needs h>=8 and then also contains 126,
  while h<8 excludes both. Only the field y-range (not passed) can
  distinguish them. Satisfying the test as written would need an
  arbitrary asymmetric band, which is not the specified fix and would
  be a different, unjustified design.
- Repair required: add `y_range=(100, 120)` to the F4 test call (the
  field rect the test comment itself states, y 100..120), then the test
  proves the fix instead of demanding the impossible. Production code
  needs no change.
- Patch vs rewrite: PATCH, keep. The band design is sound; only its y
  anchor was wrong (click point instead of field rect).

## Item 4. R3a WIRING (F5) - AMEND, commit 72120aa + follow-up 0668327

- Failing test: test_band_wrong_field_unwired_path_reports_ok.
  It still fails at HEAD, identically to base (Ran 1 test, FAILED in
  both worktrees).
- The production fix is SOUND. The source test
  test_codeexec_and_cli_act_paths_never_supply_x_ranges fails at base
  and passes at HEAD: `type_x_ranges` and `type_y_ranges` are now
  threaded through the CLI act path (explicit on the desktop_act call
  line), `CodeExecBackend.act` (best-effort grounding when dom_session
  + dom_selector are given), and the first_action fallback (y_range
  alongside the existing x_range). The claim that BrowserAdapter.act
  does not exist is correct: only a docstring mention in
  `dom_act.py:420`, fixed to `CodeExecBackend.act`.
- The behavior test is DEFECTIVE, proven independently. It calls
  `cu.desktop_act` DIRECTLY with click (15, 10), pixels x 0..11 at
  y=10, no ranges, no type_check, and expects ok False. The passing
  control test_click_type_text_in_input_line_verifies calls
  `desktop_act` directly the same way (click (10, 10), pixels at the
  left edge, no ranges) and expects ok True, and it passes in the clean
  worktree. What `desktop_act` can see in the two calls is
  structurally identical: click + type, no ranges, no type_check,
  after-image pixels on the anchor line at the left edge, which is
  exactly the documented empty-field contract (text lands at the left
  edge). No implementation can satisfy both. The "or" branch (band-only
  unverified when no ranges are supplied) would break that control, so
  refusing to implement it is correct.
- Repair required: route the behavior test through a wired path
  (CodeExecBackend.act, the CLI act path, or the first_action fallback
  with a grounded field) or supply the ranges to the direct call, so it
  tests the wiring instead of bypassing it. Production code needs no
  change.
- Follow-up 0668327 verified: the session `act_boundary` fakes in
  test_session_continuation.py and test_session_policy.py now accept
  `**extra` and forward it to the real `desktop_act`; assertions
  unchanged. `python3 -m unittest test_session_continuation
  test_session_policy` in the clean worktree, Ran 28 tests, OK. This
  is a stale-fake fix mirroring the production interface, not a test
  weakening.
- Patch vs rewrite: PATCH, keep. The ranges already existed at the
  focus_type layer and only needed threading to the three call sites.

## Items 5-6. R1 REGION FALLBACK (F2) + STALE ORIGIN (F3) - AMEND, commit b44a5ea

- Failing tests: test_region_fallback_readmits_raw_mozinner (now ERROR,
  DomActError refusal, where base FAILed) and
  test_stale_window_origin_accepted_silently (still FAIL, same
  assertion text, dist 1271.4044399796628 not less than 10).
- The production fix is SOUND. `_window_origin` requires
  `window_bounds` (raises DomActError, region fallback removed);
  `ZenSession.live_window_origin` re-reads hyprctl clients/activewindow
  and returns None (never raises) when hyprctl is unavailable;
  `_check_window_not_moved` refuses on mismatch and skips when live is
  None; wired into `ground_input` and `ground_many_one_shot`. The
  fix's own tests pass (`test_dom_act` + `test_zen_dom` +
  `test_click2_redteam`, Ran 131 tests, OK): refusal without
  window_bounds, stale-origin refusal (live [2600, 914] vs meta
  [2533, 914]), matching live origin passes with the same point.
- F2 is DEFECTIVE, proven independently. The test meta carries no
  window_bounds, no window address, and no live source on the VM, so
  the true origin [2749, 922] is not derivable from that meta; only a
  live hyprctl re-read could supply it, and none exists on the VM. The
  specified fix is to REFUSE, and the code now refuses with DomActError
  (`meta needs window_bounds for the window origin`), but the test has
  no assertRaises, so it errors instead of passing.
- F3 is DEFECTIVE, proven independently on two grounds. First, the
  assertions contradict each other: the test asserts
  `viewport_origin([100, 100], [1863, 1176]) == [340, 108]` AND that
  the mapped point is within 10 px of the true point (1527.5, 1027.25).
  I recomputed in the clean worktree: [340, 108] maps to
  (323.0, 620.25), distance 1271.4 from the true point, so no return
  value satisfies both assertions. Second, the test calls
  `viewport_origin` directly, so a ground-time re-read cannot affect
  it; the staleness check lives in `dom_act.ground_input`, not in
  `viewport_origin`. A raise would also error the test (no assertRaises).
- Repair required: F2 assertRaises DomActError for the refusal (or
  supply window_bounds plus a live origin and assert the true point);
  F3 restructure to call `ground_input` with a stale live origin and
  assertRaises DomActError, dropping the contradictory pair of
  assertions. Production code needs no change.
- Residual, noted not blocking: `ZenSession.locate_point` reads
  window_bounds directly (now refuses without them, good for F2) but
  does not call the staleness check. It has no production callers in
  scripts/ (only tests), so the gap is latent, not a live bypass. Worth
  a follow-up only if `locate_point` gains a production caller.
- Patch vs rewrite: PATCH with a removal, keep. The region fallback is
  removed outright (it re-admitted the raw mozInner pair, the R1 hole);
  the live re-read is a new check, not a new architecture.

## Item 7. R10 FLAG REDESIGN (F6/F7) - AMEND, commit 49081aa

- Failing test: test_typed_flag_forgeable_by_page_script. It still
  fails at HEAD (node TypeError, see below), where base failed on the
  flag assertion.
- The production fix is SOUND and is the one genuine REDESIGN in the
  pass, correctly judged. The window property `window.__agentCuTyped`
  is removed entirely; `arm_typed_flag` records the field value at each
  trusted input event in a listener closure and exposes it through a
  locked getter on the element (Object.defineProperty, non-configurable,
  no setter); `typed_flag` returns True only when the last-trusted value
  equals the current value. F7 node and F7 python pass at HEAD
  (test_typed_flag_sticky_across_js_set_value: ok,
  test_typed_flag_sticky_python_level: ok); F8
  (test_arm_typed_flag_misses_iframe_targets) still passes; the new
  node regression test_typed_flag_not_forgeable_via_window_property
  passes in the clean worktree.
- F6 is DEFECTIVE in two ways, proven independently with a node probe
  in the clean worktree. (1) Its forge line
  `window.__agentCuTyped['#msg-input'] = true;` throws
  `TypeError: Cannot set properties of undefined (setting '#msg-input')`
  because the arm no longer creates `window.__agentCuTyped`; the test
  errors before any assertion runs. With the forge guarded in try/catch
  (the repaired shape), the probe returns armed True, flag False, so the
  substantive flag assertion PASSES under the fix. (2) Its value
  assertion `assertNotEqual(out['value'], 'hello')` can never pass:
  the probe returns value 'hello' because the verify JS is a plain
  value read by design (Python `verify_typed` in zen_dom.py:913-936
  returns {value, editable} from the field, and consults the flag only
  when `before` is not None, keeping the before=None equality-only
  contract for pre-filled fields). F7's own assertion proves the two
  tests disagree: F7 asserts `not(flag and value == 'hello')` and passes
  with value 'hello' and flag False, while F6 demands value != 'hello'.
- Repair required: guard the forge line (or pre-create the property) and
  replace the value assertion with the F7-shaped assertion
  (not(flag and value == 'hello')). Production code needs no change.
- Residual, honestly recorded in the AMEND4 log and accepted here: a
  page that pre-defines the locked property name with a non-configurable
  forged getter before arming would defeat the check; that requires
  knowing the property name and running before the arm, outside the R10
  attacker model (a page script setting the value). Not a verdict driver.
- Patch vs rewrite: REDESIGN, keep. Any writable window state is
  forgeable by construction, so no hardening of the old property could
  close R10. The decoy-property idea (keep a window property so the
  forge line does not throw) was considered and rejected in the AMEND4
  log, correctly: it would keep a piece that should not exist purely to
  accommodate a defective test line.

## Item 8. SET_VALUE SANITIZATION (F1) - GO, commit af0fa87

- Failing-first: the F1 test fails at base and passes at HEAD
  (test_set_value_newline_text_fails_verification: ok in the clean
  worktree, Ran 1 test, OK).
- What I checked in the diff: both read-back checks in the set_value
  template now compare `e.value` against the SANITIZED form (INPUT:
  strip CR then LF via String.fromCharCode(13)/(10); TEXTAREA:
  CRLF to LF then CR to LF). The change detection (`e.value !==
  oldValue`) is unchanged and correct as-is because `e.value` is already
  the sanitized value after assignment. The char-code form avoids the
  backslash-doubling trap the AMEND4 log records from its first edit.
- Suite: `node cdp_snapshot.mjs` passes (prints "all cdp snapshot,
  redaction, fill, payload, no_after and scope regressions pass");
  `python3 -m unittest test_cdp_snapshot` in the clean worktree,
  Ran 2 tests, OK.
- Caveat, not a verdict driver: live-browser confirmation of the fixed
  template is still owed (no browser on the VM). The proof test runs the
  REAL template against a spec-faithful fake DOM, and the rule is the
  HTML Standard value sanitization algorithm. The bug itself was live
  confirmed in Chromium 130 headless (fcc driver commits 614f4b6,
  f4dcfa3).
- Patch vs rewrite: PATCH, keep. The set_value template (native-setter
  write + read-back + change-only events) is the right design; only the
  compared value was wrong.

## Item 9. SUPPLY-CHAIN TESTS (C2 A3) - GO, commit 44c15bb

- Tests only, no production code changed. Three tests pin the R3a range
  supply chain end to end: test_grounded_x_range_is_field_x_in_image_px
  (G30 field, [86.0, 526.0], None when the meta cannot map the rect),
  test_focus_type_forwards_grounded_ranges_to_act_fn (a recording
  wrapper proves the kwargs arrive, [[86.0, 526.0]] and
  [[1101.0, 1164.0]]), and the first_action ranges test (window-scope
  observation + groundable field supplies both ranges; the screen-scope
  fallback test is unchanged and still supplies no ranges).
- Suite: `python3 -m unittest test_dom_act test_first_action
  test_zen_dom test_type_verification test_click2_redteam` in the clean
  worktree, Ran 260 tests, OK.
- Patch vs rewrite: TESTS, keep. They pin the wiring from items 3-4 so
  a silent drop is caught. Nothing to rewrite.

## Item 10. SNAPSHOT EVENT TEST (C1 G4) - GO, commit e912ad4

- Test only. The mirror case is added to `tests/cdp_snapshot.mjs`
  right after the unchanged-text assertion: set_value from 'hello' to
  'world' lands the value and fires input then change, in that order.
  The suite used to assert only the zero-event side, so a template
  that never dispatched would have passed.
- Suite: `node cdp_snapshot.mjs` passes (see item 8); `python3 -m
  unittest test_cdp_snapshot`, Ran 2 tests, OK.
- Flake noted, not a verdict driver: one direct `node
  cdp_snapshot.mjs` run during this review exited 1 on a hover
  assertion at line 704 (expected /hover state did not visibly change/,
  got 'could not establish a stable non-hover state'), after the
  snapshot/fill section had already printed pass. Two re-runs exited 0.
  The hover section is timing-dependent and unrelated to items 8/10.
- Patch vs rewrite: TEST, keep. The production dispatch is proven by
  the pin, not changed.

## Item 11. DESIGN-DOC FIXES (C3 G3/G4) - GO, commit 8d75135

- Doc only. (a) Benchmark target recorded in the AMEND2 addendum of
  `improvements/worker-coord-click2-log.md`: clone1 Brave + clone2
  Chrome on ws2 per the owner definition (02:05); the "one Zen
  instance, two tabs" tab-switch protocol line is marked SUPERSEDED
  and kept visible, history not rewritten. (b) The V4 caret promise is
  removed from the design text: the line 61 bundle and step 4
  ("V1+V2+V3+V4+V11" becomes "V1+V2+V3+V11"), with a note that B18
  drops the caret signal (forgeable by page JS, false-fails mid-text
  edits and IME composition; the trusted-input flag is the
  discriminator). Verified by grep: only one "V4" mention remains in
  the doc, inside the drop note itself.
- Patch vs rewrite: REMOVE, keep. The V4 caret signal should not exist
  as a verification promise; the tab-switch protocol is superseded, not
  patched, because the benchmark target changed.

## Item 12. CL1-SWEEP ACT-NOW ENVELOPE (after-scope fix) - GO, commit cbab398

- Failing-first, verified independently: in a worktree at cbab398^
  (5f30908) with the new `tests/test_first_action.py` copied over, all
  4 new tests FAIL (Ran 68 tests, FAILED failures=4). At HEAD, all 4
  pass and `python3 -m unittest test_first_action` is Ran 68 tests, OK
  in the clean worktree. The 4 tests:
  test_session_after_is_scope_matching_not_screen,
  test_fallback_after_is_scope_matching_not_screen,
  test_after_without_result_after_captures_fresh_window,
  test_screen_observation_key_batch_refused_before_overlay.
- What I checked in the diff: the envelope now carries BOTH captures.
  `after` is scope-matching (chainable), preferring the action
  result's after (desktop_act already captures in the input scope, so
  zero extra captures) and otherwise taking a fresh capture in the
  input observation's scope via `_scope_after` (window observation
  re-observes its window; screen-scope input reuses the screen capture,
  which IS its scope-matching after). `after_screen` is the
  full-monitor capture for verification only, documented non-chainable.
  The scope check runs BEFORE the overlay attempt: a key/type batch
  given a screen-scope observation is refused (path 'refused', session
  never attempted, overlay never acquired), saving the 998 ms the
  CL1-SWEEP Enter failure wasted. The `meta` passed to `_scope_after`
  is the input observation meta from `_fresh_observation`, confirmed by
  reading run(). A meta with no scope field is not refused here (older
  observations predate the scope field; the session preflight still
  guards them).
- Root-cause check: the AMEND4 log's deeper cause (first_action.py
  hardcoded observe_screen for the envelope after, overwriting
  desktop_act's scope-matching after-capture at cu.py:2083-2091) is
  consistent with the diff, which removes exactly that overwrite; the
  CL2-MSG after-image being scope=screen predates the failure, so the
  trap existed before it bit.
- Patch vs rewrite: REDESIGN of the envelope contract, keep. The
  after-capture was defective by construction (always screen-scoped).
  The "both" shape is justified over scope-matching-only because the
  verification use of the screen capture is real and the scope-matching
  after costs zero extra captures; removing `after` was considered and
  rejected for the same reason. `after_screen` is a new field with no
  existing consumer, so nothing can chain the wrong field by accident.

## Full regression (clean worktree at 8008662)

- Targeted suites, all in the clean worktree at 8008662:
  RT2 Ran 49, FAILED (failures=4, errors=1), the 5 defective tests only.
  test_zen_dom + test_dom_act + test_first_action +
  test_type_verification + test_click2_redteam: Ran 260 tests, OK.
  test_session_continuation + test_session_policy: Ran 28 tests, OK.
  test_cdp_snapshot: Ran 2 tests, OK.
  test_first_action alone: Ran 68 tests, OK.
  test_zen_dom alone: Ran 41 tests, OK.
- Full discover: PENDING (running in the clean worktree at log write;
  the contaminated main-checkout run is discarded, see HEAD drift).

## Verdicts (per item)

- Item 1 (F9/F10): GO. Patch, keep.
- Item 2 (F8/F11/F12/F13): GO. Patch, keep.
- Item 3 (F4): AMEND. Failing test:
  test_band_stacked_fields_low_click_with_x_range_must_not_verify.
  Fix is sound; the proof test is defective (no y_range passed;
  symmetric band cannot distinguish y=110 from y=126). Repair: add
  y_range=(100, 120) to the test call.
- Item 4 (F5): AMEND. Failing test:
  test_band_wrong_field_unwired_path_reports_ok. Fix is sound (source
  test passes); the behavior test is defective (direct desktop_act call
  indistinguishable from the passing control
  test_click_type_text_in_input_line_verifies). Repair: route the test
  through a wired path or supply the ranges.
- Items 5-6 (F2/F3): AMEND. Failing tests:
  test_region_fallback_readmits_raw_mozinner and
  test_stale_window_origin_accepted_silently. Fix is sound; F2 is
  defective (true origin underivable from the meta; correct behavior is
  refusal, test has no assertRaises) and F3 is defective (contradictory
  assertions, 1271.4 px apart, and viewport_origin called directly).
  Repair: assertRaises DomActError restructures for both.
- Item 7 (F6/F7): AMEND. Failing test:
  test_typed_flag_forgeable_by_page_script. Fix is sound (redesign;
  F7 node + python pass, F8 still passes); F6 is defective two ways
  (forge line throws TypeError; value assertion can never pass and
  contradicts F7). Repair: guard the forge line, replace the value
  assertion with the F7-shaped assertion.
- Item 8 (F1): GO. Patch, keep. Live-browser confirmation of the fixed
  template still owed, not a verdict driver.
- Item 9 (C2 A3): GO. Tests, keep.
- Item 10 (C1 G4): GO. Test, keep.
- Item 11 (C3 G3/G4): GO. Doc remove, keep.
- Item 12 (CL1-SWEEP): GO. Redesign, keep.
- Totals: GO 7 (items 1, 2, 8, 9, 10, 11, 12), AMEND 5 (items 3, 4, 5,
  6, 7), BLOCK 0. No item needs a rewrite instead of its patch or
  redesign; the two redesigns (items 7 and 12) are the correct shape
  and stay.

## Defective-test findings (summary for the repair limb)

- F4 test_band_stacked_fields_low_click_with_x_range_must_not_verify:
  defective, symmetry proof in the item 3 section.
- F5 test_band_wrong_field_unwired_path_reports_ok: defective,
  indistinguishable-from-control proof in the item 4 section.
- F2 test_region_fallback_readmits_raw_mozinner: defective,
  underivable-true-origin proof in the items 5-6 section.
- F3 test_stale_window_origin_accepted_silently: defective,
  contradictory-assertions proof in the items 5-6 section.
- F6 test_typed_flag_forgeable_by_page_script: defective in two ways,
  node-probe proof in the item 7 section.
- All five defects were verified independently in the clean worktree,
  not taken from the AMEND4 log on trust. None of the five blocks its
  production fix: in each case the fix is proven sound by its own tests
  plus my independent probes, and the repair is to the test, not to the
  production code. No test was edited or weakened by this review.

## Open questions for COORD-CLICK-3

- Who owns the test-repair limb (FRT B5): the round-3 council, the
  redteam, or a repair worker? The five repairs above are specified
  precisely enough to hand to a repair worker, but the repairs touch
  the frozen proof-test file, so they need an explicit owner and a
  re-verification run after.
- Live-browser confirmation still owed for item 8 (fixed set_value
  template in a real browser) and for items 5-6 (live hyprctl re-read
  on the laptop, since the VM has no hyprctl and the check skips
  there). Neither blocks the GO/AMEND verdicts above, which rest on
  the VM proof tests, but both should be scheduled before the AMEND4
  close-out is declared fully live-proven.
- The branch moved during this review (8008662 reviewed, HEAD now
  3f1b951 with another worker editing in the same checkout). If the
  council wants this review re-anchored to the newer HEAD, say so; the
  AMEND4 files themselves are unchanged between 8008662 and 3f1b951
  except for the Y1b commit touching code_exec/codemode, which is
  outside the AMEND4 scope.

## Log commit

- (To be filled when committed: commit hash of this file, after
  `git ls-remote` verification. The hash is reported in the completion
  message to COORD-CLICK-3.)

## Addendum (07:33 22/11/2026, update from COORD-CLICK-3 via CLOSEOUT-VERIFY, landed 07:31)

Added as an addendum, not a rewrite. None of the five points below
changes a per-item verdict. Sources: the close-out log
`improvements/worker-amend4-closeout-log.md` sections 5-8, plus my own
re-runs in the clean worktree at 8008662 noted under each point.

1. CORRECTION, Codex "15/15" is qualified, not 15/15 proof tests.
   Codex's own log says "The 15 non-contradictory RT proof tests
   passed": Ran 15 tests, OK. The 15 named tests are 13 proofs + 2
   controls (F4 stacked-fields, the 2 controls, F5-behavior wrong-field,
   codeexec/CLI ranges, geometry x2, R10 flag x3, iframe arm, iframe
   reads x3, set_value newline). F2 and F3 are EXCLUDED by Codex as
   "non-contradictory" (its word), and they fail or error on BOTH lanes
   (Codex full discover: failures include F3, errors include F2). Do
   not cite Codex as passing 15/15 proof tests. My log never made that
   claim (it cites only VM-lane numbers), so no verdict of mine needs
   correcting; this records the correction for the council record.

2. DIVERGENCE, F4/F5/F6: PASS on the Codex lane, FAIL on the VM lane
   (judged defective there). This is the live question for the
   defective-test repair decision. My VM-lane defect proofs stand as
   VM-lane evidence (item 3 symmetry probe, item 4
   indistinguishable-from-control proof, item 7 node probe, all
   re-confirmed in the clean worktree). The council must adjudicate:
   are the F4/F5/F6 VM-lane "defective" judgments right, or is the
   Codex implementation (which satisfies them unmodified) the correct
   fix? Note the asymmetry in point 3: the Codex F5 pass comes with a
   cost, so it is not clean evidence that the F5 proof test is sound
   as written.

3. CODEX-LANE REGRESSION, stricter item-4 breaks a pre-existing test.
   Codex's stricter item-4 breaks the relay test
   test_click_type_verifies_through_input_line_band (its log: "expects
   a band-only result to verify without grounded ranges. Item 4
   requires that result to be unverified"). The VM lane deliberately
   did NOT implement that "or" branch, because it breaks the control
   test test_click_type_text_in_input_line_verifies (proven in my item
   4 section), and the VM lane keeps the relay test passing. Verified
   on the VM lane: `python3 -m unittest test_session_continuation
   test_session_policy` in the clean worktree at 07:09, Ran 28 tests,
   OK (11 continuation + 17 policy tests, the relay test included).
   A 07:33 re-run of the relay test alone ERRORs, but the error is the
   EPERM storm, not a behavioral failure:
   tempfile.TemporaryDirectory raises FileNotFoundError "No usable
   temporary directory found in ['/tmp', '/var/tmp', '/usr/tmp', ...]",
   exactly the close-out log section 7 symptom. So the VM lane keeps
   the relay test passing and the Codex lane breaks it. Consequence for
   the repair decision: the F5 repair must NOT adopt the Codex "or"
   branch, since it breaks a pre-existing test; the repair stays
   test-side (route through a wired path or supply the ranges), as my
   item 4 verdict already says.

4. CLOSE-OUT CORROBORATION. Close-out verified item-12 regression
   tests 4/4 PASS (three runs) and the RT set Ran 49, failures=4,
   errors=1, matching AMEND4's 6f54a4e exactly. My clean-worktree runs
   agree: item-12 4/4 pass (test_first_action Ran 68, OK) and RT2 Ran
   49, failures=4, errors=1, at 07:09. No test weakened. The Codex
   lane is 11/12 (item 12 pending a resume launched 07:27:00), so the
   Codex lane is not complete until the resume lands or is abandoned;
   that does not affect the VM-lane verdicts.

5. CLEAN FULL DISCOVER STILL OWED. The EPERM storm (from about 07:19,
   still active at 07:33, confirmed by the tempfile failure in point 3
   and by close-out log section 7) blocks file writes intermittently;
   a clean full discover at a fixed HEAD was not obtained. Do not treat
   any mixed-tree number as single-commit evidence, and do not cite my
   discover numbers as such either: the 464s run (1885 tests, 20
   failures, 307 errors) and the 44-62s runs (1831 tests, 5 failures,
   931 errors) are storm/load artifacts, not AMEND4 regressions.
   Three facts support that reading. (a) The latest discover FAIL list
   is the 4 defective RT2 tests plus test_chained_ops_in_one_program
   (test_codemode), which fails IDENTICALLY at HEAD and at base
   (AssertionError 'error' != 'completed' at test_codemode.py:62), so
   it is pre-existing, not an AMEND4 regression. (b) The "120 != 0"
   assertion seen in the 464s run tail matches the close-out log's note
   that CPython exits 120 when flushing stdout/stderr to a redirected
   file fails under EPERM. (c) Concurrent discovers by other workers
   (r3rt-head, PROBE-DOMZEN) were running on the same small VM at the
   same time, and my tee/redirect log writes failed with EPERM in the
   same window. The targeted suites remain the evidence for the
   verdicts: RT2, session suites, zen_dom/dom_act/first_action/
   type_verification/click2 (260 OK), cdp_snapshot (2 OK).

Effect on verdicts: none. GO 7 (items 1, 2, 8, 9, 10, 11, 12), AMEND 5
(items 3, 4, 5, 6, 7), BLOCK 0, as in the verdicts section above.
Points 2 and 3 make the repair decision a council adjudication, not a
worker decision: the F4/F5/F6 repairs must be decided with the
Codex-lane divergence in view, and the F5 repair in particular must
not adopt the Codex "or" branch.
