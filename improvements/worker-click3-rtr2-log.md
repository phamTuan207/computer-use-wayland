# CLICK3-RTR2 log: redteam round 2 against the AMEND3 fix pass

Worker: CLICK3-RTR2 (redteam, round 2). Coordinator: COORD-CLICK-2.
Owner: Pham Tuan (repo-facing name). Branch: todolist-push.
Task start: 05:08 +07 22/11/2026 (coordinator stamp; first measured
wall clock on this VM 05:08 +07, Asia/Ho_Chi_Minh). All times below
are measured wall-clock Asia/Ho_Chi_Minh on this VM plus elapsed
from task receipt.
Standing rules: full access, no em dash (U+2014) or en dash
(U+2013) anywhere including quoted window titles, never ydotool,
no personal info in repo files, log everything. No live laptop
driving, no browser tasks. I did not write AMEND2 or AMEND3; this
is an independent adversarial pass.

Sources read first, in full:
- improvements/worker-click3-amend3-log.md (HEAD 9bcfb04): steps
  1-7 and 9 done, R1/R3a/R10 claimed closed in substance.
- improvements/worker-click3-diff-assess.md (commit 910e471):
  KEEP MOST, 1 regression, 3 weak RT tests, handoff steps 1-9.
- improvements/worker-click3-rt-synth.md (commit dd45231):
  34-entry checklist A1-A13 + B1-B21.
- improvements/worker-click2-rt-log.md (commit 175d3ef): round-1
  redteam, 13 findings R1-R13.

Method: for each of the six assigned attacks I wrote a proof test
that asserts the REQUIRED behavior, so a failing test IS the
finding. Real production JS is executed, not re-implemented: the
zen_dom helper scripts are captured verbatim from the methods and
run in node against shimmed DOMs (the round-1 node-shim pattern),
and the cdp.mjs set_value template is extracted verbatim from the
file and run against a spec-faithful fake DOM. Python-level tests
run the real functions against the repo's own fakes. I edited no
production code; I only ADDED tests/test_click3_redteam2.py.

## Verdict: BLOCK

13 breaking findings (F1-F13), 5 high, 5 medium, 3 low-medium.
Every AMEND3 step re-attacked breaks somewhere: the set_value
delta is sound for plain strings but fails on engine-sanitized
text (F1); R1 is closed for the literal raw-pair call but
re-enters through the region fallback (F2) and through stale
window origins (F3); the R3a band is narrowed in x only, so a
low click still verifies stacked fields (F4) and the unwired
paths still run full-width (F5); the R10 flag is forgeable (F6),
sticky (F7), and never reaches iframe targets (F8); the geometry
check refuses valid factor-2 geometry (F9) and accepts a
factor-forgotten origin (F10); the iframe extension is one level
deep (F12), misses iframes in shadow roots (F13), and never
reaches the one-shot harvest (F11). Do not treat R1/R3a/R10 as
closed. Fix list per finding is in the Findings section.

## Time log

- 05:08 +00m task received; branch todolist-push, HEAD 9bcfb04
  (moved under this worker to a861201, an unrelated review
  time-log correction by another worker; the AMEND3 tree is
  unchanged). The four source logs read in full.
- 05:08-05:18 +00-10m the fixed code read: scripts/cdp.mjs
  set_value (oldValue capture, conditional dispatch),
  scripts/zen_dom.py viewport_origin / check_viewport_geometry /
  verify_typed / field_value / arm_typed_flag / typed_flag /
  harvest, scripts/fastpath.py dom_rect_to_image_point /
  dom_rect_to_screen_point, scripts/dom_act.py ground_input /
  ground_many_one_shot / grounded_x_range / focus_type / dom_hooks,
  scripts/cu.py _input_line_changed / desktop_act band / CLI act /
  CodeExecBackend.act, scripts/first_action.py fallback wiring.
  Two facts established by reading: cu.observe_screen metas carry
  NO window_bounds (region only), so the _window_origin region
  fallback is live for screen-scope observations; the set_value
  template extracts cleanly (2692 chars, no inner backticks).
- 05:18-05:22 +10-14m attack design; HTML sanitization rule
  confirmed by search (single-line input value sanitization
  strips newlines; textarea normalizes CR/CRLF to LF; browsers
  return normalized \n from textarea.value).
- 05:22-05:25 +14-17m proof tests written:
  tests/test_click3_redteam2.py, 17 redteam tests.
- 05:25-05:26 +17-18m first run: 49 tests (17 redteam + 32
  inherited DesktopPreflight harness tests), 11 failures,
  3 errors. The 3 errors were test bugs, not findings: the
  captured JS was JSON-encoded instead of embedded raw (a
  string, never executed), _capture_js passed one arg to
  verify_typed which needs (selector, expected), and
  test_zen_dom loads its own zen_dom copy via importlib so a
  ZenDomError raised through FakeWdSession is that copy's
  class, not this file's zen_dom.ZenDomError. Two assertions
  were also inverted (they asserted the buggy behavior): the
  factor-2 false-accept test and the factor-2 false-refusal
  test. All fixed in the test file only.
- 05:26-05:27 +18-19m final run: 49 tests, 15 failures, 0
  errors. The 15 failing tests are the 15 breaking proofs
  (sticky flag has two proofs, node + Python). The 2 passing
  redteam tests are controls (text inside the target field
  still verifies; text below the band does not). The 32
  inherited harness tests pass. Set_value controls verified
  separately (the test fails at its first assert, so its
  controls never executed in the run): same-text ok true with
  zero events, whitespace-only change ok true with
  input+change events.
- 05:27-05:28 +19-20m neighbor suites re-run with only the new
  test file added: test_click2_redteam, test_zen_dom,
  test_dom_act, test_pick4_fastpath, test_type_verification,
  test_first_action, test_cdp_snapshot: 274 tests, OK. No
  production code touched.
- 05:28-05:30 +20-22m this log written; dash check 0 em/en
  dashes in both files; commit with explicit pathspecs; push
  verified with git ls-remote (see the coordinator copy of
  this log for the hash). No 15-minute stall occurred.

## Test results (exact commands)

- python3 tests/test_click3_redteam2.py (from the tests dir,
  PYTHONPATH=../scripts:.): Ran 49 tests, FAILED (failures=15).
  15 failing redteam tests, 0 errors, 2 passing redteam
  controls, 32 passing inherited DesktopPreflight harness
  tests. The 49 count matches the round-1 shape (its file also
  runs the inherited harness tests); the redteam count is 17.
- Neighbor suites, same invocation:
  python3 -m unittest test_click2_redteam test_zen_dom
  test_dom_act test_pick4_fastpath test_type_verification
  test_first_action test_cdp_snapshot: Ran 274 tests, OK.
- node v24.22.1 used for the production-JS proofs.

## Findings

Severity: HIGH means the AMEND3 claim is false on a live
production path; MEDIUM means false on a reachable path or a
fail-closed functional break; LOW-MEDIUM means a real hole with
a narrow trigger or fail-closed incompleteness.

### F1 (MEDIUM, BROKEN): set_value can never set newline text
- Attack (1). File: scripts/cdp.mjs, set_value branch.
- Proof: test_set_value_newline_text_fails_verification.
  The REAL set_value template extracted from scripts/cdp.mjs,
  run in node against a spec-faithful fake DOM (input strips
  newlines, textarea normalizes CR/CRLF to LF per the HTML
  Standard). Textarea, set 'a\r\nb' on an empty field:
  ok false, error 'value verification failed', events [],
  value 'a\nb'. Input text, set 'a\nb': ok false, value 'ab'.
  Input text, value 'hello', set 'hello\n': ok false, events
  [], value 'hello'. The set lands (normalized) and the call
  still fails: the read-back compares e.value against the
  UNSANITIZED text, which the engine can never hold.
- Why the AMEND3 delta misses it: the delta only conditions
  the event dispatch on oldValue; the read-back
  (e.value !== text) is the AMEND2 R2 code it kept verbatim,
  and no sanitization is modeled anywhere in the comparison.
- Fix required: normalize the comparison, compare e.value
  against the sanitized form of text (strip newlines for
  single-line inputs, CRLF/CR to LF for textareas), and use
  the sanitized length in the maxLength pre-check. A set whose
  sanitized form already holds must report ok true.
- Caveat, stated plainly: no live browser exists on this VM,
  so the engine half of this proof is the documented HTML
  Standard rule, not a live observation. The JS-logic half
  (the real template failing given that rule) is executed
  proof. A live-browser confirmation is still owed before
  landing the fix.
- SURVIVES (same test, controls, observed separately because
  the test fails at its first assert): same text 'same' on a
  field holding 'same' reports ok true with zero events; a
  whitespace-only change 'hello' to 'hello ' reports ok true
  with input+change events. The AMEND3 delta is sound for
  plain strings. The existing cdp_snapshot suite independently
  covers the same-text case.

### F2 (HIGH, BROKEN): region fallback re-admits the raw mozInner pair
- Attack (2), R1. Files: scripts/dom_act.py _window_origin,
  scripts/zen_dom.py viewport_origin.
- Proof: test_region_fallback_readmits_raw_mozinner. A meta
  with no window_bounds (the exact shape cu.observe_screen
  builds: region [0, 0, 3840, 2160], monitor_box, no
  window_bounds) goes through ground_input; _window_origin
  falls back to the region origin [0, 0]; viewport_origin
  returns [240, 8], the raw mozInner pair as the absolute
  origin, with no error; the ground point is (273.0, 570.25)
  while the true point is (1527.5, 1027.25), about 1335 image
  px off, no error raised. The containment check passes
  because the "window" is now the whole monitor.
- This is the literal R1 old bug, re-entering through a
  documented fallback ("window_bounds, else its region") on
  a live production meta shape.
- Fix required: refuse when window_bounds is absent (require
  it; never fall back to the region origin), or re-read the
  live Hyprland window origin at ground time and refuse on
  mismatch. At minimum, ground_input must reject a
  screen-scope meta (scope 'screen') instead of grounding
  against it.

### F3 (MEDIUM, BROKEN): stale window origin accepted silently
- Attack (2), R1. Files: scripts/zen_dom.py viewport_origin /
  check_viewport_geometry, scripts/dom_act.py ground_input.
- Proof: test_stale_window_origin_accepted_silently. The
  window moved from (2509, 914) to (100, 100) after the
  observation; viewport_origin([100, 100], [1863, 1176])
  returns [340, 108] with no error (closure and containment
  both pass: the stale origin is internally consistent and
  still on-monitor); on a screen-scope meta the wrong point
  (323.0, 620.25) lands inside the image while the true point
  is (1527.5, 1027.25), 1271 image px away, no error raised.
  The chain never re-reads the window origin live: no hyprctl
  call exists anywhere in the chain, and the HCU guard
  re-reads the rect but not the origin.
- Fix required: re-read the Hyprland window origin live at
  ground time (hyprctl activewindow) and refuse when it
  differs from the meta's window_bounds, or record the window
  origin with the observation and refuse grounding when the
  observation is stale.

### F4 (HIGH, BROKEN): stacked fields sharing the x-range
- Attack (3), R3a. File: scripts/cu.py _input_line_changed.
- Proof: test_band_stacked_fields_low_click_with_x_range_must_
  not_verify. Upper field A spans y 100..120, click at y 118
  (near its bottom edge); lower field B spans y 124..144 and
  shares x-range (100, 300). 12 changed pixels in B at y 126
  return True from _input_line_changed with x_range=(100,
  300). The band is narrowed in x only; the y window is still
  anchor_y +- 12 around the CLICK point, not the field rect.
  Controls pass: the same pixels inside A verify (True), and
  pixels below the band at y 140 do not (False).
- Fix required: anchor the band y on the grounded field rect
  (its y-range mapped to image px), not on the click point;
  or intersect the band with the rect's y-range. The click
  point is an arbitrary point inside the field, not the text
  line.

### F5 (HIGH, BROKEN): unwired paths still run the full-width band
- Attack (3), R3a. Files: scripts/cu.py CodeExecBackend.act
  and the CLI act branch; scripts/dom_act.py focus_type is
  the only wired caller besides first_action.
- Proof: test_band_wrong_field_unwired_path_reports_ok and
  test_codeexec_and_cli_act_paths_never_supply_x_ranges. A
  click (15, 10) + type batch with 12 wrong-field pixels at
  x 0..11, no type_check, no type_x_ranges, reports ok True,
  type_verified True, basis input-line-band. The source test
  pins the call sites: CodeExecBackend.act builds no
  type_x_ranges at all, and the CLI act branch never puts one
  into act_kwargs. The AMEND3 log admits this ("the cu CLI
  act path and CodeExecBackend.act do not yet supply ranges")
  but still claims R3a "closed in substance": it is closed
  only on the focus_type/first_action paths, not on the
  code-exec and CLI paths, which are production paths.
- Fix required: thread type_x_ranges through both paths
  (ground the rect in open_dom_hooks / CodeExecBackend.act
  the way first_action does), or make a band-only result
  report type_verified False whenever no x-range was
  supplied, so the full-width band can never verify alone.

### F6 (HIGH, BROKEN): the V11 typed flag is forgeable by page JS
- Attack (4), R10. File: scripts/zen_dom.py arm_typed_flag /
  typed_flag.
- Proof: test_typed_flag_forgeable_by_page_script. The REAL
  arm/typed_flag/verify JS run in node against a shimmed DOM.
  After arming, a page script runs
  window.__agentCuTyped['#msg-input'] = true and sets the
  value to 'hello' with zero input events; typed_flag returns
  true and verify returns 'hello', so the real Python
  verify_typed would return True. The amend log's defense
  ("isTrusted cannot be forged by page JS") is true of
  events and false of the flag: the flag is a plain property
  on window, writable in one line.
- Fix required: do not keep the flag as a plain window
  property. Record, in the input listener's closure, the
  field value at each trusted input event (last-trusted
  value); verify requires value == last-trusted value. A
  closure variable is unreachable from page JS, which
  defeats both the forge and the sticky flag (F7) at once.

### F7 (HIGH, BROKEN): the typed flag is sticky across JS-set values
- Attack (4), R10. File: scripts/zen_dom.py verify_typed /
  typed_flag.
- Proof: test_typed_flag_sticky_across_js_set_value (node,
  real JS) and test_typed_flag_sticky_python_level (real
  Python verify_typed, FakeWdSession). One real keystroke
  (value 'h', one trusted input event) sets the flag; a page
  script then replaces the whole value with 'hello' and no
  further event; verify_typed('hello', before='') returns
  True. The flag proves an input event happened at some
  point, not that THIS value came from input events.
- Fix required: same as F6, record the value at the last
  trusted input event in the listener closure and require
  the verified value to equal it. A boolean flag can never
  express which value the typing produced.

### F8 (MEDIUM, BROKEN): arm_typed_flag never reaches iframe targets
- Attack (4) + (6), R10 + step 6. File:
  scripts/zen_dom.py arm_typed_flag.
- Proof: test_arm_typed_flag_misses_iframe_targets. The REAL
  arm JS run in node against a same-origin iframe target:
  arm returns false, no listener is installed, and a real
  trusted input event inside the iframe leaves the flag
  clear, while the REAL field_value JS returns 'hello' from
  the same iframe. The value IS readable from the iframe,
  but the typed path can never verify it: step 6's "an iframe
  target reads and verifies" is false for the typed path.
- Fix required: give arm_typed_flag the same find() helper
  (shadow pierce + same-origin iframe traversal) as
  field_value/verify_typed. Note the known gap the AMEND3 log
  already records (focus_check is top-document only) compounds
  this: an iframe field cannot pass the focus gate either.

### F9 (MEDIUM, BROKEN): valid factor-2 geometry refused
- Attack (5), geometry. File: scripts/zen_dom.py
  viewport_origin / check_viewport_geometry.
- Proof: test_viewport_origin_factor2_small_window_false_
  refusal. Factor 2, window (100, 100) screen px 800x600,
  mozInner CSS (240, 8), inner CSS (152, 284), outer CSS
  (400, 300): a consistent geometry (sidebar 240 CSS px =
  480 screen px, viewport 304 screen px, gaps 8 CSS px).
  viewport_origin raises ZenDomError: absolute [580, 116]
  "falls outside the window rect [100, 100] size [400.0,
  300.0]". The absolute origin is 480 screen px into an 800
  screen px window, inside; the check compares it against a
  CSS-px rect. The AMEND3 log admits the mix ("conservative
  at factor > 1") but a conservative check that refuses valid
  geometry is a false refusal, not safety: at factor 2 any
  Zen window narrower than about 960 screen px with a 240 CSS
  px sidebar refuses to ground at all.
- Fix required: do the containment check in consistent units:
  compare the screen-px absolute origin against window_origin
  + the SCREEN-px window size, or compare the CSS-px origin
  (mozInner) against the CSS-px window rect. Never compare
  screen px against CSS px.

### F10 (LOW-MEDIUM, BROKEN): validator accepts a factor-forgotten origin
- Attack (5), geometry. File: scripts/zen_dom.py
  check_viewport_geometry.
- Proof: test_geometry_check_accepts_factor_forgotten_origin.
  At factor 2 the true absolute origin is (2989, 930); the
  factor-forgotten (2749, 922) is 240 screen px off, yet
  check_viewport_geometry returns it without raising (closure
  and containment both pass on the CSS-px rect). The AMEND3
  log's claim that the mixed-unit check "can only refuse,
  never accept a wrong origin" is false.
- Fix required: same consistent-unit fix as F9. No production
  caller passes a factor-forgotten origin today, so this is a
  validator weakness, not a live wrong click; severity is
  lower than F9 for that reason.

### F11 (MEDIUM, BROKEN): harvest never traverses iframes
- Attack (6), iframe. File: scripts/zen_dom.py harvest.
- Proof: test_harvest_misses_iframe_targets. The REAL harvest
  JS run in node against a same-origin iframe target returns
  items['#msg-input'] null, while locate() finds the same
  target. harvest() pierces shadow roots in the top document
  only and has no frame loop at all. The VISION 1 one-shot
  grounding therefore disagrees with per-element grounding
  about iframe targets, on the exact path the 2-vision
  benchmark uses for both clone inputs.
- Fix required: give harvest the same frame loop as locate
  (same-origin traversal, cross-origin fails closed per
  item, never silently dropped).

### F12 (LOW-MEDIUM, BROKEN): field_value reads only one iframe level
- Attack (6), iframe. File: scripts/zen_dom.py field_value /
  verify_typed (find helper).
- Proof: test_field_value_misses_nested_iframe. The REAL
  field_value JS run in node against a target inside an
  iframe inside an iframe returns null: pierce() inside the
  first frame document never looks for frames of its own.
  Fail-closed, but the "same-origin frames" claim covers
  only one level.
- Fix required: recurse find() into frame documents (with a
  depth cap and the same cross-origin try/catch).

### F13 (LOW-MEDIUM, BROKEN): field_value misses iframes in shadow roots
- Attack (6), iframe. File: scripts/zen_dom.py field_value /
  verify_typed (find helper).
- Proof: test_field_value_misses_iframe_in_shadow_root. The
  REAL field_value JS run in node against an iframe inside a
  shadow root returns null: the frame loop uses
  document.querySelectorAll('iframe'), which sees light-DOM
  iframes only, and pierce() recurses into shadow roots but
  never into iframes.
- Fix required: in pierce, also recurse into iframes found
  under each root (or collect frames with a shadow-piercing
  walk), so a frame nested in a shadow tree is reached.

## What survives (attacks that failed)

- The AMEND3 set_value delta is sound for plain strings:
  same text fires no events, a real whitespace change fires
  input+change (F1 controls).
- The R1 literal bypass is closed in production code: no
  caller passes a raw mozInner pair to dom_rect_to_image_point
  or dom_rect_to_screen_point; all three image-point callers
  go through viewport_origin output or the inline absolute in
  ground_many_one_shot, which adds the window origin (grep
  verified). The breaks are the fallback (F2) and staleness
  (F3), not a direct raw-pair call.
- The R3a narrowed band works when ranges are supplied and
  the click is central: the AMEND3 12-pixel wrong-field test
  still passes, and my controls pass (text inside the target
  field verifies; text below the band does not).
- Cross-origin iframes fail closed: the try/catch around
  contentWindow.document access holds, and the existing test
  covers it. No wrong-DOCUMENT value read was found: locate,
  field_value, and verify_typed share the same top-first find
  order, so the iframe breaks are nulls (fail-closed
  incompleteness) and the arm asymmetry (F8), not wrong values.
- Paste, IME commit, and drag-drop text dispatch trusted
  input events by design, so the flag correctly treats them
  as user input; they are not R10 breaks. Whether Firefox
  autofill fires a trusted input event is UNCONFIRMED (needs
  a live browser; none exists on this VM) and is NOT claimed
  as a finding here.

## Test-authoring notes (traps for the next worker)

- The captured zen_dom JS must be embedded RAW in the node
  driver, not JSON-encoded: a JSON string never executes.
  My first run had this bug in three tests.
- _capture_js must pass verify_typed its (selector,
  expected) args; one arg raises TypeError before any
  evaluate call.
- test_zen_dom loads its own zen_dom copy via importlib, so a
  ZenDomError raised through FakeWdSession is that copy's
  class, not the importing file's zen_dom.ZenDomError.
  assertRaises on such calls must use the copy that raised
  (or catch Exception and fail with the message).
- A redteam test must assert the REQUIRED behavior: two of my
  geometry assertions were written inverted (asserting the
  buggy behavior happens) and had to be flipped before the
  run counted them as findings.
- The 49-test count includes 32 inherited DesktopPreflight
  harness tests (the round-1 file has the same shape); the
  redteam count is 17 (15 failing, 2 passing controls).

## Commit record

Proof tests: tests/test_click3_redteam2.py (new file, 17 tests).
This log: improvements/worker-click3-rtr2-log.md (this file).
Both staged and committed with explicit pathspecs, push
verified with git ls-remote (see the coordinator copy of this
log for the hash). No production code touched: the only change
in the tree is these two files. The 4 other untracked files in
the tree (other workers' files) were left untouched. No em
dash or en dash in either file (checked by grep before
commit). No ydotool (one mention of the ban in the test file
docstring only). No personal info (owner name Pham Tuan only,
as instructed for repo-facing text).
