# AMEND4 fix pass log (worker CLICK3-AMEND4)

Worker CLICK3-AMEND4, subagent of the parent orchestrator. Owner: the owner
(call the user the owner in repo-facing text, never "dang"). Work in
`~/workspace/computer-use-wayland`, branch `todolist-push`.
Task start: 05:30 22/11/2026 Asia/Ho_Chi_Minh. Log committed last, after
all 12 items. All times below are Asia/Ho_Chi_Minh unless noted.
Commit timestamps are converted from the UTC author dates stored in git
(+07). Elapsed: start 05:30 to log commit ~06:55, about 85 minutes.

## Standing rules honored

- Full access. NO em dash (U+2014) or en dash (U+2013) anywhere, including
  quoted window titles. NEVER ydotool. NO personal info in repo files
  (owner name the owner only). Log everything with wall-clock + elapsed.
- Small commits, one fix per commit, explicit pathspec immediately after
  staging, never plain `git commit`, never `git add -A`. Push after each
  commit, verify with `git ls-remote`; on non-fast-forward, fetch + rebase
  and retry, never force-push. Other workers' files untouched.
- Do NOT edit `tests/test_click3_redteam2.py` or
  `tests/test_click2_redteam.py` (acceptance tests; may only ADD tests).
  Do NOT weaken any test: a proof test whose expectation is wrong is left
  failing for adjudication, with the evidence in this log.
- Failing-first: each fix's proof test must fail before and pass after
  (where the test is sound).
- End state: full discover 0 failures (4 pre-existing errors allowed) and
  all 15 RT proof tests passing; exact commands and counts recorded below.
- If stuck 15 min with no progress, say so in the final report. Report to
  the coordinator, never to the user directly.

## Owner directions received during this pass

- 05:56, NO SELF-HEALING (stronger than the 03:58 rule): when Muse fails,
  Muse does NOT self-diagnose or self-fix, even for small in-task errors.
  Hand the log and all evidence to other workers to MEET, research,
  propose and fix, to avoid bias. Reason: if Muse is wrong, how can it
  point out where it is wrong itself. This applies to the whole lane,
  including direct runs by Muse tong (the parent dispatched an
  independent worker to re-investigate its own 05:49 CL1-SWEEP Enter
  failure). Recorded here. If my work turns up a failure by Muse, I
  investigate it independently and propose the fix myself; I do not hand
  it back to Muse to self-diagnose. Item 12 is that independent
  investigation, and its finding goes further than the parent's own
  diagnosis (see item 12).
- 06:00:16, ADD ITEM 12 (CL1-SWEEP Enter failure, log
  `improvements/worker-cl1sweep-fail-invest-log.md`, commit 5f5a2fd). The
  parent's own diagnosis was CONFIRMED but INCOMPLETE. Deeper root cause,
  proven from source: act-now ALWAYS captures its envelope `after` image
  with `cu.observe_screen` (first_action.py hardcoded, max_width 1920),
  regardless of input scope, and overwrites desktop_act's scope-matching
  after-capture (cu.py:2083-2091). EVERY act-now after-image is
  screen-scoped by construction; reusing ANY of them for a key/type step
  will ALWAYS fail. Proof: CL2-MSG's after-image f2bdb0d34ead is also
  scope=screen; the trap existed then and just did not bite.
- 06:01, FIRST PRINCIPLES THINKING (standing rule): some things should NOT
  exist at all, or should be COMPLETELY DIFFERENT, or were WRONG FROM THE
  START. If needed, REWRITE. Applied to this pass, not just patching: for
  each of the 12 items I questioned whether the piece of design should
  exist at all. Every patch-vs-remove-vs-redesign decision with its
  evidence is recorded under its item below. The round-3 council judges
  patch vs rewrite. This continues the 10x rule.
- 06:02, INDEPENDENT BREAKTHROUGH SWARM (context only): 4 independent
  workers dispatched (CODEX-BREAKTHROUGH, ARCH-REVIEW, GROUNDING-REVIEW,
  SPEED-REVIEW); their commits landed on this branch (arch-review
  074c1d7, grounding-review d1fc4e9, speed-review a4ecb49).
- 06:07, PRAGMATIC (standing rule): cost does not matter (token, time,
  rewrite effort). The decision criterion for every proposal is the
  accuracy and speed of the final result.
- 06:09, TWO TRACKS: the discussion team is deciding the direction; my
  track (track 2) CONTINUES but SLOWER and more gradually to save tokens.
  Concretely: work item by item, commit after each item, do not spawn
  extra sub-workers, do not run expensive re-runs more than the brief
  requires, do not expand scope.
- 06:32-06:34, received via MEMORY.md during this pass (final direction
  round; feasibility rule; Lauren Tan evidence standard): the discussion
  team settles ONE direction last, every direction needs live feasibility
  evidence from the laptop, and every claim needs real measured numbers
  (command + output + commit hash + time log). These do not change the
  AMEND4 fix list: my track continues per the 06:09 two-tracks order, and
  my verification already follows the evidence standard (real commands,
  outputs, commit hashes, and time logs are recorded below; live-browser
  confirmation that this VM cannot provide is recorded as still owed,
  not claimed).

## HEAD drift

The task said HEAD f0ddd41, but other workers pushed since; I work on the
current HEAD. f0ddd41 is an ancestor of HEAD. HEAD moved repeatedly during
this pass (a4ecb49 at 06:10, then 14fc139, 6cb3f95, 2b0c73c, 9d23834,
7b1006a, 2864be4, a1a672d, 5f30908 at successive pushes); every one of my
pushes was a fast-forward from the then-current HEAD, verified with
`git ls-remote`. No force-push, no rebase of other workers' work.

## Baseline (05:30)

- `python3 test_click3_redteam2.py` from `tests/` with
  `PYTHONPATH=../scripts:.`: Ran 49 tests, FAILED (failures=15). The 15
  failures are the RT2 proof tests; 2 redteam controls pass; 32 inherited
  DesktopPreflight harness tests pass.
- Full discover baseline from council re-runs: 1855 tests, 0 failures,
  4 pre-existing errors, 17 skipped. The 4 pre-existing errors:
  test_a11y_skeleton import, test_cursor_file setUpClass (g++ rejects
  -std=c++26), test_perf_evidence x2 (missing benchmark JSON).
- Environment: no `hyprctl` on this VM, no `/run/user/1000/hypr/`, no
  browser on the VM, no pytest (use `python3 -m unittest`), node is
  available.

## Sources read in full

1. `improvements/worker-click3-rtr2-log.md` + `tests/test_click3_redteam2.py`
   (round-2 redteam, 13 findings F1-F13, 15 failing proof tests, f0ddd41).
2. `improvements/worker-click3-c1r2-review-log.md` (1057750),
   `improvements/worker-click3-c2r2-review-log.md` (4419b5f),
   `improvements/worker-click3-c3r2-review-log.md` (7e93128).
3. `improvements/worker-click3-rt-synth.md` (34-entry checklist),
   `improvements/worker-click3-amend3-log.md` (9bcfb04).
4. Production code: `scripts/zen_dom.py`, `scripts/dom_act.py`,
   `scripts/cu.py`, `scripts/first_action.py`, `scripts/cdp.mjs`,
   `scripts/fastpath.py`.
5. Tests: `tests/test_zen_dom.py`, `tests/test_dom_act.py`,
   `tests/test_type_verification.py`, `tests/test_keyboard_preflight.py`,
   `tests/cdp_snapshot.mjs`, `tests/test_click2_redteam.py` (frozen, read
   only), `tests/test_first_action.py`.
6. Design doc: `improvements/worker-coord-click2-log.md`.
7. Item 12: `improvements/worker-cl1sweep-fail-invest-log.md` (5f5a2fd).

## Item 1. GEOMETRY (C1 G1 + C3 G1 + RT F9/F10) - DONE, cc964b2, 06:12

- `check_viewport_geometry` gained `factor=None` (keyword, after
  monitor_box); factor absent raises `ZenDomError` (a validator that
  silently assumes factor 1 is the F10 hole). Closure in CSS px (moz +
  inner vs size as-is); exactness check `absolute == window + moz*factor`
  within 0.5 px (catches the factor-forgotten origin); containment in
  screen px (`absolute` vs `window + size*factor`); monitor containment
  in screen px (unchanged).
- `viewport_origin` passes size as-is in BOTH branches (given size is
  Hyprland logical px = CSS px numerically; None fallback is CSS-px
  outerWidth/Height) and passes `factor=factor`. `ground_many_one_shot`
  in `dom_act.py` same (size as-is, factor passed).
- Factor-2 test in `tests/test_zen_dom.py` rewritten production-realistically:
  `[1863, 1176]` returns `[2989, 930]`; `[1500, 1000]` raises; plus the
  None-branch case returns `[2989, 930]`.
- Failing-first confirmed: both F9/F10 failed before, pass after.
- First principles: PATCH, not redesign. The geometry chain itself
  (Hyprland origin + mozInner * factor) is correct; the defect was unit
  mixing in the validator and the size branch, not the design. The only
  removal is the silent factor-1 default, which is the F10 hole.
- F10 design note: the F10 inputs are self-consistent at factor 1
  (closure gaps 1.5 and 8; containment passes), so no pure consistency
  check can refuse them; the refusal comes from the fail-closed factor
  requirement, not from containment alone. The containment fix
  (consistent units) is what makes the production path correct (F9).
- Verified: 53 tests (GeometryTests + test_zen_dom + test_dom_act) OK;
  frozen test_click2_redteam 71 OK.

## Item 2. GATE TRAVERSAL (C2 A1 + C3 G2 + C1 G3 + RT F8/F11/F12/F13) - DONE, c1ea773, 06:19

- Shared JS constants in `scripts/zen_dom.py`: `_FIND_JS` (pierce +
  framesOf + find, depth cap 5; frames detected by `contentWindow`
  presence, never tagName, since RT2 shims give frame objects no tagName;
  cross-origin fail-closed via try/catch), `_DEEP_ACTIVE_JS`
  (activeElement walk through shadow roots AND iframes),
  `_FRAME_POINT_JS` (owner-document elementFromPoint with frame-chain
  offset walk).
- `locate`, `hit_check`, `focus_check`, `field_value`, `verify_typed`,
  `arm_typed_flag` (find, old flag semantics kept), `sent_bubble_contains`
  (recursive leaf collection across shadow roots and same-origin frames
  via framesOf), `harvest` (find per selector, framePoint hit, deepActive
  focus) all use the shared helper.
- `find` defaults `root=document, depth=0`; call sites use one-arg
  `find(sel)` so the FakeWdSession selector regex (`find("...")`) keeps
  working.
- Fake-routing constraint learned: `_FIND_JS` must contain no marker
  substring the test fakes dispatch on (no activeElement,
  elementFromPoint, textContent, getBoundingClientRect, mozInnerScreenX);
  deepActive/framePoint live apart because they DO contain one and belong
  only in scripts whose fake branch already expects it. The sent_bubble
  `%` formatting needed parens around the whole concatenation (`%` binds
  tighter than `+`).
- R7 faithful-shim re-run: added `TestFaithfulShadowShim` (2 node tests)
  in `tests/test_zen_dom.py` (querySelector returns null for the
  shadow-nested input; host reachable only via querySelectorAll('*') +
  shadowRoot). Verified the old code returns False on the faithful shim
  (node one-liner) and the new code returns True. The frozen R7 test
  (unfaithful shim) still passes. This closes the C3 step-8 scope dispute.
- First principles: PATCH, not redesign. The find/pierce/traverse shape
  is the right design; it was applied inconsistently (some helpers pierced
  shadow roots, none traversed frames). Unifying on one shared helper
  removes the inconsistency without a new architecture.
- Verified: 130 tests (F8/F11/F12/F13 + test_zen_dom + test_dom_act +
  test_click2_redteam) OK.

## Item 3. R3a BAND ANCHORING (RT F4) - DONE, 62b740e, 06:22

- `_input_line_changed` gained `y_range=None` (band y = field y-range
  when given, else anchor+-12); `grounded_y_range` in `dom_act.py`
  mirroring `grounded_x_range` (height axis); `type_y_ranges` threaded
  through `desktop_act` and `focus_type`. The CLI/CodeExec/first_action
  y-threading was done in item 4 (same call sites as x).
- My tests: 2 band tests in `tests/test_type_verification.py` (stacked
  field with y_range must not verify at desktop_act level; unit test
  with/without y_range) + `grounded_y_range` unit test in
  `tests/test_dom_act.py` (G30: [1101.0, 1164.0]; None meta returns None).
- First principles: PATCH. The band design (read the anchor line in the
  after-capture) is sound; the defect is the band's y anchor (click
  point instead of field rect). Anchoring both axes on the grounded rect
  fixes it without a new verification channel.
- **F4 RT2 test judged DEFECTIVE, left failing**: symmetry proof. The test
  calls `_input_line_changed(old, new, 118, x_range=(100, 300))` with
  pixels at y=126; the control uses y=110. Both are 8px from anchor 118,
  no y_range passed. Any symmetric band [118-h, 118+h] containing 110
  needs h>=8, then also contains 126; h<8 excludes both. Only the
  field's y-range (not passed) can distinguish them. My y_range contract
  is proven by my own tests. The RT2 test needs `y_range=(100, 120)`
  added to be sound; adjudication owed.

## Item 4. R3a WIRING (C2 A2 + C1 G2 + C3 G5 + RT F5) - DONE, 72120aa, 06:23

- Threaded `type_x_ranges` AND `type_y_ranges` through the CLI act path
  (explicit on the desktop_act call line,
  `result=desktop_act(env,read_json_file(args.observation),actions,type_x_ranges=type_ranges,type_y_ranges=type_y_ranges,**act_kwargs)`,
  because the source test slices that one line), `CodeExecBackend.act`
  (best-effort grounding when dom_session + dom_selector are given,
  mirroring first_action.py:599-613), and the first_action fallback
  (y_range added alongside existing x_range).
- **BrowserAdapter.act does NOT exist** (only a docstring mention in
  `dom_act.py:420`); fixed that docstring to `CodeExecBackend.act` and
  noted the naming slip.
- F5 source test passes.
- First principles: PATCH. The wiring is the fix the councils specified;
  the ranges already existed at the focus_type layer and only needed
  threading to the three call sites. No redesign: the band is the
  verification channel, the ranges narrow it.
- **F5 behavior test judged DEFECTIVE, left failing**: it calls
  `cu.desktop_act` DIRECTLY (click (15,10), pixels x 0..11 at y=10, no
  ranges, no type_check) and expects ok False. Threading cannot affect a
  direct call. Pixels x 0..11 after a click at x=15 are indistinguishable
  from legitimate empty-field typing (text lands at the left edge, per
  `_input_line_changed`'s own docstring). The task's "or" branch
  (band-only unverified when no ranges supplied) would break the control
  test `test_click_type_text_in_input_line_verifies` (expects ok True via
  band, no ranges). Verified: 156 tests, only the F5 behavior test fails.
- Decision recorded: implement the threading branch (correct fix); do NOT
  implement the "or" branch (band-only unverified), because it breaks
  `test_click_type_text_in_input_line_verifies` and the documented
  empty-field contract.

## Item 5. R1 REGION FALLBACK (RT F2) + Item 6. R1 STALE ORIGIN (RT F3) - DONE, b44a5ea, 06:26

- `_window_origin` in `dom_act.py` requires `window_bounds` (raises
  `DomActError` when absent, no region fallback). `ZenSession.live_window_origin(address=None)`
  added in `zen_dom.py` (hyprctl clients -j by address, fallback
  activewindow -j; returns None when hyprctl unavailable / window not
  found / unparsable, never raises). `dom_act` helper `_live_window_origin`
  + `_check_window_not_moved` wired into `ground_input` and
  `ground_many_one_shot` (refuse on mismatch, skip check when live origin
  is None). `locate_point` also requires `window_bounds` now (same F2 hole).
- Fixtures updated to production shape: `G30_META` in
  `tests/test_dom_act.py` and `_meta()` in `tests/test_zen_dom.py` gained
  `window_bounds` (region values unchanged); the 7 map-accuracy case metas
  gained `window_bounds` equal to their region (their regions ARE the
  windows).
- FakeDomSession gained `live_origin` param + `live_window_origin()`
  method (None = cannot re-read, skip check). My tests: refusal without
  window_bounds; stale-origin refusal (live [2600,914] vs meta
  [2533,914]); matching live origin passes with the same point/origin.
- First principles: PATCH, with a removal. The region fallback is removed
  outright (it re-admitted the raw mozInner pair, the R1 hole); the live
  re-read is added (a new check, not a new architecture). The fail-closed
  shape (refuse when the evidence is absent or stale) is the design, and
  the patch implements it.
- Verified: 128 tests (test_dom_act + test_zen_dom + test_click2_redteam) OK.
- **F2 judged DEFECTIVE**: test asserts `ground_input` returns a ground
  with `viewport_origin != [240,8]` and point within 10px of true
  (1527.5, 1027.25) from a meta with no `window_bounds`
  (`{image_size:[1920,1080], region:[0,0,3840,2160], monitor_box:[0,0,3840,2160]}`).
  The true origin [2749,922] is not derivable from that meta; only a live
  hyprctl re-read could supply it, and none exists on the VM. The task's
  fix is to REFUSE, so the correct behavior makes the test error (it now
  errors with the refusal DomActError; it has no assertRaises). Left for
  adjudication.
- **F3 judged DEFECTIVE**: test asserts
  `viewport_origin([100,100],[1863,1176]) == [340,108]` AND that the mapped
  point is within 10px of the true point, but `[340,108]` maps to
  (323.0, 620.25) while the true point is (1527.5, 1027.25), about 1271
  image px away (confirmed in the failure output:
  "1271.4044399796628 not less than 10"). No return value satisfies both
  assertions; a raise would error the test (no assertRaises). It also calls
  `viewport_origin` directly, so a ground-time re-read cannot affect it.
  Left for adjudication.

## Item 7. R10 FLAG REDESIGN (RT F6/F7, HIGH) - DONE, 49081aa, 06:34

- Failing-first confirmed: all 3 R10FlagTests fail before the fix.
- Design (REDESIGN, not patch: the window property is the forgeable
  surface, so it is removed, not hardened): remove
  `window.__agentCuTyped` entirely. `arm_typed_flag` installs a listener
  recording the field value at each trusted input event in a closure
  variable, exposed through a locked getter on the element via
  `Object.defineProperty(e, '__agentCuTypedValue', {get, configurable:false,
  enumerable:false})` (no setter, so page JS cannot write it;
  non-configurable, so it cannot redefine/delete it). Arm returns False
  if defineProperty throws (page pre-locked the name). Re-arm: if a
  non-configurable descriptor already exists, return True (the earlier
  arm's listener+getter are still live). The MutationObserver diagnostic
  is kept, stored on the element via a locked property instead of the
  window.
- `typed_flag(selector)`: find element (pierce + iframe traversal), read
  locked getter, return True only when last-trusted value is non-null AND
  equals the current value (same trailing-whitespace normalization as
  `verify_typed` for contenteditable). This satisfies both RT2 node tests:
  forge (no event, flag False) and sticky (last-trusted 'h' vs current
  'hello', flag False).
- Python `verify_typed` logic stays as-is (calls `typed_flag` when
  `before` is not None); the two-evaluate shape is acceptable because both
  reads must agree.
- Fakes updated to the same contract: `tests/test_zen_dom.py`
  FakeWdSession `_typed` becomes a dict subclass whose `__setitem__` with
  value True records the field's current value at set time (simulating "a
  trusted event fired now"), using a _MISSING sentinel for "no event";
  `_typed_flag` compares recorded vs current value.
  `tests/test_dom_act.py` FakeDomSession `note_typed` records the current
  field value; `typed_flag` compares recorded vs current. Existing tests
  that set `_typed=True` while the field holds the expected value keep
  passing (recorded value equals current); the RT2 python sticky test
  (value 'h' at set time, then 'hello') correctly fails.
- New node regression test in `tests/test_zen_dom.py`
  (`test_typed_flag_not_forgeable_via_window_property`): the production
  arm/typed_flag JS runs under node against the redteam top-document shim;
  a page script forges the old window property (whole-property assignment;
  the arm creates no window property, so the subscript form would throw)
  and sets the value, with zero trusted input events. Result:
  `{"armed":true,"flag":false}`. The flag is not forgeable via the window
  property.
- First principles: REDESIGN. The window property is removed, not
  hardened: any writable window state is forgeable by construction, so no
  hardening of it can close R10. The closure + locked getter moves the
  state to a place the page cannot write (the arm's closure, reachable
  only through a getter with no setter). A decoy window property (created
  only so the redteam F6 forge line would not throw) was considered and
  REJECTED: it would keep a piece that should not exist, purely to
  accommodate a defective test line.
- Residual, recorded honestly: a page that pre-defines the locked property
  name with a non-configurable forged getter before arming would defeat
  the check; that requires knowing the property name and running before
  the arm, outside the R10 attacker model (a page script setting the
  value). F6/F7 as proven are closed.
- **F6 judged DEFECTIVE in two ways, left failing**:
  1. Its forge line `window.__agentCuTyped['#msg-input'] = true;` throws
     (`TypeError: Cannot set properties of undefined`) because the arm no
     longer creates `window.__agentCuTyped`. The line assumes the old
     surface; with the surface removed, the forgery attempt itself throws
     before the assertions run. The flag assertion would pass if the forge
     line were guarded (proven by my own node test above:
     armed true, flag false).
  2. Its value assertion `assertNotEqual(out['value'], 'hello')` conflates
     the field value with the verify outcome. `out['value']` is `__v.value`
     where `__v` is the verify JS result `{value, editable}`; the field's
     value IS 'hello' (the page script set it), so the assertion can never
     pass regardless of the flag redesign. The verify JS is a plain value
     read by design (the flag check lives in Python for before!=None, and
     the before=None equality-only contract must keep working for
     pre-filled fields); making the JS enforce the flag would break that
     contract. The substantive flag assertion (`assertFalse(out['flag'])`)
     IS fixable and IS fixed.
- Verified: 132 tests (R10FlagTests + test_zen_dom + test_dom_act +
  test_click2_redteam), only F6 fails (the two defects above). F7 node and
  F7 python pass. F8 (arm in iframe + trusted dispatch + flag True)
  still passes.

## Item 8. SET_VALUE SANITIZATION (RT F1) - DONE, af0fa87, 06:38

- Failing-first confirmed: the F1 test fails before (`CRLF text into a
  textarea failed although the field holds the normalized value:
  {'ok': False, 'error': 'value verification failed', 'events': [],
  'value': 'a\\nb'}`) and passes after.
- Fix in `scripts/cdp.mjs` set_value template: both read-back checks now
  compare `e.value` against the SANITIZED form, computed with
  `String.fromCharCode` (input: strip CR and LF; textarea: CRLF and CR
  become LF). The change detection (`e.value !== oldValue`) is unchanged:
  `e.value` is already the sanitized value after assignment, and
  `oldValue` is the previous sanitized value, so the comparison is
  correct as-is. The return stays `{ok:true}`; the maxlength pre-check
  is untouched (out of the F1 scope).
- HTML Standard rule cited (live confirmation still owed, no browser on
  the VM): the value sanitization algorithm. For `input`, the algorithm
  strips newlines (U+000A LF and U+000D CR are removed from the value).
  For `textarea`, the algorithm normalizes CRLF and CR to LF. The
  read-back must compare against the sanitized form, or a set that
  landed (normalized) still reports "value verification failed". Live
  confirmation of the sanitization rule in a real browser is still owed;
  the node-shim proof runs the REAL template against a spec-faithful
  fake DOM (the F1 test's own design), and the rule is the documented
  HTML Standard behavior, not a live observation.
- Implementation lesson, recorded honestly: my first edit used regex
  literals with doubled backslashes inside the template, and a comment
  that mentioned the escape sequences. The heredoc/Python escaping chain
  mangled the backslashes: the comment ended up containing a literal CR
  character, which the template literal normalized to LF when the
  template was re-evaluated, breaking the comment across lines and
  producing a SyntaxError in the generated source (`", not literal"`).
  The fix was to avoid backslash escapes entirely (char codes via
  `String.fromCharCode(13)` / `(10)` / `(13,10)`), so the template needs
  no backslash doubling when it is re-evaluated. The regex form would
  have needed exactly two backslashes in the file; the escaping chain
  through JSON, shell heredoc, and Python string made that unreliable,
  so the char-code form is the robust choice.
- First principles: PATCH. The set_value template is the right design
  (native-setter write + read-back + change-only events); only the
  compared value was wrong (unsanitized instead of sanitized).
- Verified: F1 passes (textarea CRLF lands as LF, input newline lands
  stripped, unchanged text fires no events, whitespace change fires
  input plus change). `node cdp_snapshot.mjs` passes ("all cdp snapshot,
  redaction, fill, payload, no_after and scope regressions pass") and
  `test_cdp_snapshot.py` 2 tests OK.

## Item 9. SUPPLY-CHAIN TESTS (C2 A3) - DONE, 44c15bb, 06:40

- Three tests pin the R3a range supply chain end to end:
  1. `grounded_x_range` unit test in `tests/test_dom_act.py` (G30 field,
     [86.0, 526.0], None when the meta cannot map the rect), mirroring
     the y-range test from item 3.
  2. `focus_type` forwards the grounded x-range and y-range to the
     act_fn in `tests/test_dom_act.py` (a recording wrapper proves the
     kwargs arrive, `[[86.0, 526.0]]` and `[[1101.0, 1164.0]]`, not just
     that a fake accepts and ignores them).
  3. `first_action` supplies both ranges to the fallback desktop_act in
     `tests/test_first_action.py` (window-scope observation + groundable
     field; the FakeZenSession gains the grounding methods ground_input
     needs: locate, viewport_origin, hit_check). The screen-scope
     fallback test is unchanged and still supplies no ranges.
- First principles: these are TESTS, not a redesign; they pin the wiring
  from items 3-4 so a silent drop is caught. No production code changed
  in this item.
- Verified: all 3 new tests pass; 256 tests (test_dom_act +
  test_first_action + test_zen_dom + test_type_verification +
  test_click2_redteam) OK.

## Item 10. SNAPSHOT EVENT TEST (C1 G4) - DONE, e912ad4, 06:41

- Added the mirror case to `tests/cdp_snapshot.mjs`, right after the
  existing unchanged-text assertion: set_value from 'hello' to 'world'
  lands the value and fires input then change, in that order
  (`deepEqual(events.map(type), ['input','change'])`). The suite used to
  assert only the zero-event side (unchanged text), so a template that
  never dispatched would have passed.
- First principles: TEST only; the production dispatch (item 8's template
  already dispatches on change) is proven by the pin, not changed.
- Verified: `node cdp_snapshot.mjs` passes ("all cdp snapshot, redaction,
  fill, payload, no_after and scope regressions pass").

## Item 11. DESIGN-DOC FIXES (C3 G3/G4) - DONE, 8d75135, 06:41

- (a) Benchmark target recorded in the AMEND2 addendum of
  `improvements/worker-coord-click2-log.md`: clone1 Brave + clone2 Chrome
  on ws2 per the owner definition (02:05). The "one Zen instance, two
  tabs" tab-switch protocol line is marked
  `**SUPERSEDED (2026-11-22, AMEND4 item 11)**` and kept visible;
  history is not rewritten. A new bullet records the benchmark target and
  that each clone runs its own browser on ws2, so no tab-switch protocol
  is needed.
- (b) The V4 caret promise is removed from the design text: line 61 bundle
  (the "V4 caret position check" clause dropped) and step 4
  ("V1+V2+V3+V4+V11" becomes "V1+V2+V3+V11"), with a note that B18 drops
  the caret signal: caret position is forgeable by page JS, the
  trusted-input flag is the discriminator, and a caret-at-end check would
  false-fail mid-text edits and IME composition. V2 (contenteditable
  innerText readback) is untouched; only the V4 clause is removed. The
  only remaining "V4" mention in the doc is inside the B18 drop note
  itself.
- First principles: REMOVE. The V4 caret signal should not exist as a
  verification promise (forgeable, and it false-fails legitimate edits);
  the trusted-input flag replaces it as the discriminator. The tab-switch
  protocol is superseded, not patched: the benchmark target changed, so
  the protocol built for the old target goes away.
- Verified: grep confirms no V4 promise remains (only the drop note).

## Item 12. CL1-SWEEP ENTER FAILURE (act-now envelope redesign) - DONE, cbab398, 06:46

- Independent investigation (per the 05:56 no-self-healing rule; the
  parent's own diagnosis was CONFIRMED but INCOMPLETE). Deeper root cause,
  proven from source: act-now ALWAYS captures its envelope `after` image
  with `cu.observe_screen` (`first_action.py` hardcoded, max_width 1920)
  regardless of input scope, and overwrites desktop_act's scope-matching
  after-capture (`cu.py:2083-2091`, where `_after_capture` returns
  `observe_screen` for screen scope and `observe` for window scope).
  EVERY act-now after-image is screen-scoped by construction; reusing ANY
  of them for a key/type step will ALWAYS fail. Proof: CL2-MSG's
  after-image `f2bdb0d34ead` is also scope=screen; the trap existed then
  and just did not bite.
- Evidence re-derived: action file `~/workspace/cl1sweep-enter1.json`
  (`[{"keys":["Return"],"type":"key"}]`); observation `8716a28d6388.json`
  scope screen, image_size [1920,1200], region [2464,902,1920,1200],
  max_width 1920, no window field; retry observation `0b78b458b8f3.json`
  scope window, window 0x55705383d420, image_size [901,1176], region
  [2533,914,901,1176], max_width 960; images cl1sweep-obs4.jpg (draft
  unsent) and cl1sweep-obs5.jpg (blue bubble 5:49 AM, sent). G28 preflight
  refusal at `cu.py` desktop_act line 1649 (screen scope + key/type).
- Open verification resolved during implementation: the session stdout
  envelope DOES carry `result['after']` (confirmed from source: the CLI
  act path prints the desktop_act result at `cu.py:3101`, compacted at
  `:3100` via `compact_result`, which keeps `after` with its `scope`,
  `window`, `window_bounds`, `region`, and `image_size` fields intact).
  So on the session path the scope-matching after comes from the session
  result; on the fallback path from the direct result; when neither has
  one, a fresh capture is taken in the input observation's scope.
- Design (REDESIGN, not a one-line patch; first principles applied):
  the envelope contract changes. It now returns BOTH `after`
  (scope-matching, chainable: the next act-now may reuse it as its
  observation) and `after_screen` (full-monitor verification only,
  documented non-chainable). `after` prefers the action result's after
  (desktop_act already captures in the input scope, so this costs no
  extra capture); when that is absent, a non-dict, or scoped differently,
  a fresh capture is taken in the input observation's scope (a window
  observation re-observes its window via `cu.observe`). A screen-scope
  input needs no extra capture: the screen capture IS its scope-matching
  after. Removal of `after` from the envelope was considered and
  REJECTED: the verification use is real (operators read the after-image
  to confirm the result), removal would force an extra observe call per
  verification and break the existing workflow, and the trap is fixed by
  the scope match at zero extra captures (desktop_act already computes
  the scope-matching after). The "both" design is fastest and most
  accurate, which is the owner's pragmatic criterion (06:07).
- Also moved: the scope check runs BEFORE the overlay attempt. A key/type
  batch given a screen-scope observation is refused before the overlay is
  acquired and before any session attempt (the CL1-SWEEP Enter failure
  wasted 998ms on both before the desktop_act scope preflight refused).
  A rejected given observation is left to the G28 loud-refusal flow (which
  names the substitute capture); a meta with no scope field is not refused
  here (older observations predate the scope field, and the session
  preflight still guards them). The no-observation key/type case is
  unchanged (it still refuses inside desktop_act, pre-existing behavior,
  out of this item's scope).
- Regression tests in `tests/test_first_action.py` (4, all failing-first:
  on the old `first_action.py` all 4 fail, verified by stashing the
  production change and re-running; on the new code all 4 pass):
  1. Session path: the session result's window-scope after is copied to
     the envelope `after` (id 'sess-after-1'); `after_screen` is the
     screen capture (id 'a1b2c3d4e5f6').
  2. Fallback path: the direct desktop_act result's window-scope after
     is copied (id 'after-1'); `after_screen` is the screen capture.
  3. No result after: the envelope `after` is captured fresh in the
     input window scope (id 'win-after-1' from `cu.observe`).
  4. Pre-overlay scope refusal: a Return key batch given a screen-scope
     observation is refused (path 'refused', error names screen
     observations), the session is never attempted
     (`sess.assert_not_called()`), and the overlay is never acquired
     (`fake_overlay.holders == {}`).
- Fake updates in `tests/test_first_action.py`: FakeCu.observe_screen meta
  gains `'scope': 'screen'`; FakeCu gains an `observe` method (window
  capture, id 'win-after-1'); FakeCu.desktop_act `after` becomes a
  scope-matching dict (production-faithful: desktop_act's after-capture
  matches the input observation's scope). No existing test asserts the
  envelope `after` value, so no existing test changes meaning.
- First principles: REDESIGN of the envelope contract (the after-capture
  was defective by construction: always screen-scoped). The alternative
  of only patching the capture to match scope was considered; the "both"
  shape was chosen because the verification use of the screen capture is
  real and the scope-matching after costs zero extra captures.
- Verified: 68 tests in test_first_action OK (including the 4 new ones
  and the item-9 ranges test).

## Item 4 follow-up. Session act_boundary fakes forward desktop_act kwargs - DONE, 0668327, 07:02

- Found by the final full discover (see Final verification): 17
  session_continuation / session_policy tests failed with
  `live.<locals>.act_boundary() got an unexpected keyword argument
  'type_x_ranges'`. Root cause: my item-4 CLI change forwards
  `type_x_ranges` / `type_y_ranges` to `desktop_act`, but the `live()`
  `act_boundary` fakes in `tests/test_session_policy.py` and
  `tests/test_session_continuation.py` had a fixed signature
  `(env, meta, actions, after_capture, observation_path,
  expected_terminal_window)` and rejected the new kwargs. The production
  `desktop_act` accepts them; only the test doubles were stale.
- Fix: both fakes now accept `**extra` and forward it to the real
  `desktop_act`. The tests' assertions are unchanged. This is a
  stale-fake fix, not a test weakening: the fake mirrors the production
  `desktop_act` interface, and forwarding future kwargs keeps it from
  breaking again on the next interface addition.
- How it was proven to be mine (not pre-existing): the three files pass
  28/29 on the pre-AMEND4 worktree (commit 14fc139, the parent of my
  first AMEND4 commit), with only the tc02 module failing to load there;
  on current code they had 17 failures, all with the same TypeError.
  Only my commits touched `scripts/cu.py` since 14fc139 (items 3 and 4).
  A minimal repro (the KillEnvelope completed-capture-error scenario)
  printed the exact TypeError before the fix and passes after it.
- Verified: `test_session_continuation` + `test_session_policy`, Ran 28
  tests, OK.

## Final verification (07:05 22/11/2026)

### RT proof tests (the 15)

Command (from `tests/`, twice, same result):

    PYTHONPATH=../scripts:. python3 -m unittest test_click3_redteam2

Result: Ran 49 tests, FAILED (failures=4, errors=1). 10 of 15 pass:
F1, F5-source, F7-node, F7-python, F8, F9, F10, F11, F12, F13.
The 5 that do not pass are the adjudicated defectives, each with its
proof in its item section above:

- ERROR test_region_fallback_readmits_raw_mozinner (F2): the correct
  behavior is a refusal DomActError; the test has no assertRaises.
- FAIL test_stale_window_origin_accepted_silently (F3): contradictory
  assertions (1271 image px apart); no return value satisfies both.
- FAIL test_band_stacked_fields_low_click_with_x_range_must_not_verify
  (F4): symmetry proof; no y_range passed, so no band can distinguish
  the two pixels.
- FAIL test_band_wrong_field_unwired_path_reports_ok (F5 behavior):
  direct desktop_act call; threading cannot affect it; the "or" branch
  would break the control test.
- FAIL test_typed_flag_forgeable_by_page_script (F6): the forge line
  assumes the removed window property (throws TypeError) and the value
  assertion conflates the field value with the verify outcome; the
  substantive flag assertion is fixed (proven by my own node test:
  armed true, flag false).

### Full discover

Command (from `tests/`):

    PYTHONPATH=../scripts:. python3 -m unittest discover -s . -p "test_*.py"

First run (before the item-4 follow-up fix): Ran 1920 tests in 234.840s,
FAILED (failures=20, errors=8, skipped=17). The 17 session failures
were caused by my item-4 change (see Item 4 follow-up); the fix
resolved all 17.
Final run (after the follow-up fix): Ran 1920 tests in 388.608s,
FAILED (failures=5, errors=6, skipped=17). The 11 remaining problems:

- 4 pre-existing errors (the allowed baseline): test_a11y_skeleton
  import, test_cursor_file setUpClass (g++ rejects -std=c++26),
  test_perf_evidence x2 (missing benchmark JSON).
- 5 RT2 adjudicated defectives (F2 error; F3, F4, F5-behavior, F6
  failures), listed above.
- 2 environmental (tc02_controller, missing tesseract binary on this
  VM: `which tesseract` returns nothing; the tests raise
  "tesseract is unavailable; refusing to assume text presence").
  These are unrelated to AMEND4 (they test the tc02 controller's OCR
  path) and fail identically with or without my changes; installing a
  system package is out of this pass's scope.

The brief's end state (0 failures, 4 pre-existing errors) is therefore
NOT fully met: 5 failures remain, of which 4 are defective proof tests
left for adjudication and 1 is environmental (tesseract). The 6 errors
are the 4 allowed pre-existing plus F2 (defective) plus 1 environmental
(tesseract). No failure in the final run is caused by AMEND4 code: the
only AMEND4-caused failures found (the 17 session tests) were fixed in
0668327 and re-verified.

### New tests added by this pass (13)

- Item 2: 2 TestFaithfulShadowShim node tests (test_zen_dom.py).
- Item 3: 2 band tests (test_type_verification.py) + 1 grounded_y_range
  unit test (test_dom_act.py).
- Item 7: 1 node forge test (test_zen_dom.py).
- Item 9: 1 grounded_x_range unit test + 1 focus_type forwarding test
  (test_dom_act.py) + 1 first_action ranges test
  (test_first_action.py).
- Item 12: 4 regression tests (test_first_action.py).
- Item 10: 1 changed-value event assertion (cdp_snapshot.mjs, run via
  node, not counted in the unittest discover total).

### Live confirmation still owed

- F1 sanitization rule (HTML Standard value sanitization algorithm):
  cited from the standard; live browser confirmation owed (no browser
  on the VM).
- The 2-vision benchmark as a whole, and the F1/F8/F9 live-DOM runs:
  owed from the redteam round, unchanged by this pass (VM has no
  browser; the laptop re-run is the parent's lane).

### Note on the final direction (received 06:58, during close-out)

The final direction landed (commit e05fc58): 40 proposals, ADOPT 19,
MODIFY 20, CLOSED 1 (P8), REJECT 0. Step 1 is the AMEND4 close-out
(12/12 landed, plus tests, Codex-lane confirmation, and fixing broken
tests). This pass delivers exactly that: 12/12 items landed, the broken
session tests found by the final discover fixed in 0668327, and the
remaining gaps (5 defective proof tests for adjudication, 2
environmental tesseract failures, live-browser confirmation owed)
recorded here for the round-3 council.

## Commits (all on todolist-push, pushed, ls-remote verified)

- cc964b2 (06:12): item 1 geometry (F9/F10).
- c1ea773 (06:19): item 2 gate traversal (F8/F11/F12/F13) + faithful-shim
  R7 tests.
- 62b740e (06:22): item 3 band y anchoring (F4 defective, symmetry proof).
- 72120aa (06:23): item 4 wiring (F5 source passes; F5 behavior defective).
- b44a5ea (06:26): items 5-6 window_bounds refusal + live re-read (F2/F3
  defective).
- 49081aa (06:34): item 7 R10 flag redesign (F6/F7; F6 defective in two
  ways).
- af0fa87 (06:38): item 8 set_value sanitization (F1).
- 44c15bb (06:40): item 9 supply-chain tests (C2 A3).
- e912ad4 (06:41): item 10 snapshot event test (C1 G4).
- 8d75135 (06:41): item 11 design-doc fixes (C3 G3/G4).
- cbab398 (06:46): item 12 act-now envelope redesign (CL1-SWEEP).
- 0668327 (07:02): item 4 follow-up, session act_boundary fakes forward
  desktop_act kwargs (17 session tests fixed).
- This log, committed last.

## Patch vs remove vs redesign (summary for the round-3 council)

- Patch: items 1, 2, 3, 4, 8 (the design is right; a value, a branch, or
  a wiring is wrong).
- Patch with a removal: items 5-6 (the region fallback is removed; the
  live re-read is added), item 11 (V4 caret promise removed; tab-switch
  protocol superseded).
- Redesign: item 7 (the window-property flag is removed and replaced by
  a closure + locked getter), item 12 (the envelope after-capture
  contract is redesigned to carry both a scope-matching after and a
  verification-only after_screen).
- Tests only: items 9, 10.
