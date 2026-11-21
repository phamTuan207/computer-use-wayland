# CLICK3-RT-SYNTH: consolidated fix checklist from the CLICK2 review round

Worker: CLICK3-RT-SYNTH (independent Muse reviewer). Coordinator: COORD-CLICK-2.
Owner: Pham Tuan (repo-facing name).
Branch: todolist-push. Task start 04:33 +07 22/11/2026. All times wall-clock
Asia/Ho_Chi_Minh + elapsed from task start.

Sources read (all on todolist-push):
- RT: improvements/worker-click2-rt-log.md, commit 175d3ef, verdict BLOCK,
  13 findings R1-R13, 23 proof tests (22 fail, 1 fix-direction pass).
- C1: improvements/worker-click2-c1-review-log.md, commit 25ebf10, verdict AMEND, F1-F6.
- C2: improvements/worker-click2-c2-review-log.md, commit e7b4a52, verdict AMEND, F1-F6 + D1-D6.
- C3: improvements/worker-click2-c3-review-log.md, commit 9424bae, verdict AMEND, fixes 1-5.
- AMEND: improvements/worker-click-amend-log.md, CLICK-AMEND 12/12 items, 8 commits, HEAD 4b7d6ac.
- C12 probe: improvements/worker-click2-c12probe-log.md, commit cd89597,
  verdict WINDOW-RELATIVE (live, 1 real click).

Scope: the amend diff under review is the code range 16c4196..90b7026 (12 files,
+1632/-116), rebased inside e4082ff..4b7d6ac. All file:line references below are
at the amend tip 4b7d6ac unless stated otherwise. This worker did NOT edit any
code. This worker did NOT re-run the suites; counts below are the sources' own
measured numbers, quoted with their source.

Working-tree note (observed 04:40 +07, not mine, not touched): the checkout
holds uncommitted modifications in 24 files (scripts/cu.py, dom_act.py,
fastpath.py, first_action.py, zen_dom.py, zen_cli.py, cdp.mjs and tests),
i.e. AMEND2 work already in progress by another worker. This checklist is
grounded in the review-round sources at the amend tip, not in that
uncommitted tree. Line numbers below may already have shifted in the tree.
The coordinator should confirm whether the uncommitted tree already covers
any entry here before assigning it.

## How to read this file

- Each entry has: ID, source(s), severity, one-paragraph description, exact
  file/function to change, required fix in concrete terms, and C12-probe
  status (whether the probe verdict resolves it, changes it, or leaves it).
- Severity uses the sources' own words: BLOCK (must not land until fixed),
  GATING (must be fixed before the 2-vision benchmark relies on it),
  AMEND (fix before the benchmark relies on it / design-doc level).
- "Needs code" means the C12 probe verdict does not remove the work; the
  probe only ever answers the empirical mozInnerScreen question.
- Cross-references: entries that are the same defect seen by two reviewers
  are merged into one entry with all sources listed; the merge map is in
  section H so nothing is lost.

## A. Redteam findings R1-R13 (RT log, commit 175d3ef)

### A1. R1 - Conversion drops the window origin (BLOCK)

- Source: RT R1. Also C1 F2, C2 F2, C3 fix 2 and C12 adjudication (c).
- Description: scripts/zen_dom.py viewport_origin() returns
  window.mozInnerScreenX/Y and documents it as the viewport origin in screen
  coordinates, while the repo's own live calibration
  (docs/calibration-e2-report.md) says mozInnerScreenX/Y in this Zen build
  are WINDOW-relative (240, 8) and the truth table adds the window origin
  (2509, 914) for screen px. No window-origin term exists anywhere in
  dom_act, fastpath, or zen_dom, and the amend's own tests fake the origin
  as [2533, 914], which equals neither the measured (240, 8) nor the true
  screen origin (2749, 922). On the measured geometry ground_input raises
  DomActError instead of clicking (RT proof test: screen (546.0, 1140.5)
  maps to image (-1264.4, 145.8)).
- File/function: scripts/zen_dom.py:367-383 viewport_origin();
  scripts/fastpath.py:152-167 dom_rect_to_screen_point() (origin + center,
  no window term); scripts/dom_act.py ground_input() (no window-origin read).
- Required fix: make viewport_origin() return Hyprland window origin +
  mozInnerScreenX/Y (or the verified screen value), record the hypothesis
  with the snapshot, and correct the test fakes to the measured values
  (window-relative origin (240, 8), window origin (2509, 914), true screen
  origin (2749, 922)). Rewrite the 7 accuracy cases in
  tests/test_pick4_fastpath.py and tests/test_dom_act.py to true
  viewport-relative rects + window-relative origin + window origin.
- C12-probe status: CHANGED, not moot. The probe PROVES the empirical
  question live (mozInnerScreenX=240, mozInnerScreenY=8, measured 4 times;
  absolute reading is geometrically impossible, off-monitor; window-relative
  reading closes exactly, 240+1615+8=1863 and 8+1160+8=1176; one real click
  at candidate B (2628.5, 973.5) focused the urlbar and selected the URL).
  So the "resolve empirically" half of R1 is DONE and the fix direction is
  now known. The CODE half still needs doing: viewport_origin() is still
  wrong as written at the amend tip, and the tests are still circular.

### A2. R2 - Prefill false-ok: verify_typed is equality only (BLOCK)

- Source: RT R2. Also C3 review item 4 context; cdp.mjs half is RT R11.
- Description: verify_typed() checks field value equals expected with no
  before-value and no change required, so a pre-filled input passes with
  zero keystrokes. RT proof: pre-fill the input with the expected text,
  stub the type step, run focus_type, result ok True, type_verified True,
  typed []. The same hole exists in cdp.mjs set_value as an early return
  (ok:true when the value already equals the text).
- File/function: scripts/zen_dom.py:444-451 verify_typed();
  scripts/dom_act.py:105-108 type_check closure; scripts/cdp.mjs set_value
  early return (see A11).
- Required fix: capture the before-value at ground time; require before !=
  expected AND after == expected (V17 expectation-first). Apply the same
  fix in cdp.mjs set_value: remove the early return or require a real set.
  Add the RT proof test (prefilled input + stubbed type must not verify).
- C12-probe status: NEEDS CODE. The probe does not touch verification.

### A3. R3 - Input-line band false-passes three ways, and ok still follows it (BLOCK)

- Source: RT R3. Also C1 F1/F3, C2 F1 (probes P1/P2/P5/P7), C3 fix 1
  (caret-only probe: 3-pixel caret mark, ok True, type_verified True,
  basis input-line-band).
- Description: _input_line_changed() uses a full-width band (anchor y
  +-12px), so text in ANY field on the same line passes, a 3px caret blink
  or focus ring passes, and a frame resize passes (size mismatch returns
  True outright). Without a type_check hook the batch still reports ok True
  on all three. The result note itself says the band is "necessary, not
  sufficient", yet ok True follows it. All three councils independently
  reproduced the caret-only false pass on the real predicate.
- File/function: scripts/cu.py:1018-1045 _input_line_changed();
  scripts/cu.py:2053-2080 (band True sets type_verified True, ok stays True).
- Required fix: the band must never be the sole basis for ok. Without a DOM
  value check, a has_type batch reports type_verified False (or ok False),
  not ok True. Narrow the band to the target rect (not full width), and
  make size mismatch return None (unverifiable), not True (see A16 for the
  size-mismatch half). Acceptance test: click + stubbed type with a
  caret-only after image must report ok False, type_verified False,
  error_code type_unverified.
- C12-probe status: NEEDS CODE. The probe does not touch the band.

### A4. R4 - ok True with type_verified None (BLOCK)

- Source: RT R4. Also C3 fix 4 (the mirror case: a passing DOM check is
  discarded on the same path).
- Description: two paths return ok True with no verification at all:
  after_capture=False (ok True, type_verified None, "skipped: after_capture
  is False, no fresh frame to compare") and the terminal-address-None path
  (after_skipped, type_verified None, ok stays True). The existing test
  test_type_batch_after_capture_false_skips_verification asserts ok True,
  so the hole is baked into the suite as intended behavior.
- File/function: scripts/cu.py:1958-1975 (after_capture=False branch);
  scripts/cu.py:1998-2007 (terminal None path).
- Required fix: a has_type batch with no verification at all must not
  report ok; set ok False (or outcome_uncertain True with ok False) and
  keep type_verified None as the reason. Update the existing test to the
  new contract. On the terminal-None path, consult type_dom_verified the
  way the after_capture=False branch does, so a DOM-verified type still
  reports type_verified True with basis dom-value (C3 fix 4).
- C12-probe status: NEEDS CODE. The probe does not touch these paths.

### A5. R5 - Verify-after-Enter ordering: a successful send fails (BLOCK)

- Source: RT R5. Also C1 F5(d), C2 D4 context.
- Description: type_check runs AFTER the whole batch including Enter, so a
  sent message (input cleared by the send) FAILS verify_typed. RT proof:
  sent == ['hello'] (the message did send) but result ok False,
  type_verified False, error_code type_unverified. The amend's own FakeAct
  never models Enter clearing the field, so its enter=True happy-path test
  passes vacuously. No V12 sent-bubble check exists anywhere in dom_act.
- File/function: scripts/cu.py:1914-1920 (type_check runs after execution,
  after Enter already dispatched); scripts/dom_act.py:86-95 (Enter appended
  to the same batch as type, type_check after).
- Required fix: verify the typed text BEFORE Enter (field holds expected
  text, caret at end), then Enter, then verify the SEND by the sent bubble
  (V12, thread DOM), never by re-reading the cleared field. Fix the FakeAct
  to model Enter clearing the field so the happy-path test is not vacuous.
- C12-probe status: NEEDS CODE. The probe does not touch ordering.

### A6. R6 - Double-send: no exactly-once mechanism (BLOCK)

- Source: RT R6. Also C1 F5(c), C2 D4, C3 design gap (intent ledger missing).
- Description: focus_type has no sent-bubble pre-check, no dedup token, no
  before-send state read, so retrying after a partial send (first attempt
  executed, result lost; or the R5 false-failure after a real send)
  re-sends the message. RT proof: sent == ['hello', 'hello'] after two
  identical calls. V12 exists nowhere in dom_act. All three councils agree
  exactly-once is asserted in the design, not mechanized.
- File/function: scripts/dom_act.py:78-129 focus_type().
- Required fix: before sending, read the thread DOM for the exact text
  bubble (V12); send only if absent. Order the flow as A5 requires
  (verify text, then Enter, then verify bubble), and make retry check the
  bubble first. Specify the retry/ledger rule in the design doc before
  implementation: intent + sent-bubble check, dedupe by text plus
  timestamp. If the V12 finish gate fails on render lag, a retry must
  still not double-send.
- C12-probe status: NEEDS CODE. The probe does not touch send semantics.

### A7. R7 - Stale DOM: hit and point come from different snapshots; no live guard (AMEND)

- Source: RT R7. Also C1 F5 (guard unspecified), C2 D2, C3 design gap
  (per-action guard, not per-batch).
- Description: ground_input reads locate, origin, hit_check as three
  separate evaluates, and hit_check re-reads its own rect, so the hit
  verdict and the clicked point come from different snapshots. Nothing
  re-resolves between ground and click, and ground_many points are never
  re-validated before use. RT proof: ground point (306.0, 1132.5) is outside
  the live rect (y 800..863) while hit passed; stored clone2 point
  (306.0, 1031.5) is outside the live rect (y 700..763). The combined
  design's step-3 HCU live guard is design text only; no code implements it.
- File/function: scripts/dom_act.py:38-62 ground_input();
  scripts/dom_act.py:64-76 ground_many();
  scripts/zen_dom.py:405-421 hit_check().
- Required fix: re-resolve the rect immediately before each click and
  require the stored point to still hit the live rect (V6); re-ground each
  input at its own send time, never click a ground_many point from before
  the previous send. Build the guard as a per-action check (focus gate
  before EVERY type group, hit re-check before the second click), not a
  per-batch one, and name its owner and location (dom_act, or a wrapper
  around desktop_act). Implement the guard, do not just document it.
- C12-probe status: NEEDS CODE. The probe does not touch staleness.

### A8. R8 - hit_check passes any descendant, including an interactive child (AMEND)

- Source: RT R8. Also noted in C3 (same clause in cdp.mjs set_value).
- Description: hit_check passes when the elementFromPoint hit is any
  descendant (e.contains(hit)), including an interactive child button
  sitting at the rect center (clear-text / emoji / send affordance inside
  the composer). RT proof: node execution of the REAL hit_check JS returns
  True with a BUTTON at the rect center. The click would activate the child
  instead of focusing the field. A hit on a border child node passes
  identically.
- File/function: scripts/zen_dom.py:405-421 hit_check()
  (e===hit||e.contains(hit)); same clause in scripts/cdp.mjs set_value.
- Required fix: require e===hit, or allow descendants only when the
  descendant is not itself interactive (not BUTTON, A, INPUT, or
  [role=button]) and document which case each selector relies on. Fix the
  same clause in cdp.mjs set_value.
- C12-probe status: NEEDS CODE. The probe does not touch hit testing.
  (Live confirmation owed on the laptop: whether the real Messenger
  composer center hits a child control.)

### A9. R9 - Shadow DOM and iframe inputs unreachable; shadow focus false-negatives (AMEND)

- Source: RT R9. Also C1 F5 context (doma11y open item 6: cross-origin
  iframes unreachable from parent JS).
- Description: locate, focus_check, and field_value all use
  document.querySelector only, and focus_check is strict
  activeElement===e with no shadowRoot walk (V3 explicitly requires the
  walk). RT proof: node execution of the REAL focus_check JS returns False
  for a focused input inside a shadow root (activeElement is the host);
  no 'shadowRoot', 'contentWindow', or 'frames' appears in the code.
- File/function: scripts/zen_dom.py:347-361 locate();
  scripts/zen_dom.py:423-434 focus_check();
  scripts/zen_dom.py:436-442 field_value().
- Required fix: walk shadowRoot.activeElement down (the Chromium pattern in
  the crawl log), pierce open shadow roots in locate/field_value, and
  traverse same-origin frames. For cross-origin iframes refuse loudly
  naming the target class instead of silently dropping it from the "every
  input" harvest. The design must state which fallback applies (vision or
  BiDi browsing-context calls) for cross-origin frame content.
- C12-probe status: NEEDS CODE. The probe does not touch shadow DOM.
  (Live confirmation owed: shadow/iframe structure of the real target DOM.)

### A10. R10 - Synthetic JS-set value passes verification; V11 unimplemented (AMEND)

- Source: RT R10. Also C1 F5(e), C3 step 4 (V11 unbuilt).
- Description: a page script can set el.value (or textContent) to the
  expected text and dispatch synthetic input events with zero keystrokes,
  and verify_typed passes it. No MutationObserver exists anywhere in cu.py,
  dom_act.py, or zen_dom.py. The verification channel (Marionette evaluate)
  is the same channel the page's own JS writes through, so the check cannot
  distinguish typed text from JS-set text.
- File/function: scripts/zen_dom.py:444-451 verify_typed();
  (new) scripts/zen_dom.py verification helpers; scripts/dom_act.py focus_type().
- Required fix: arm a MutationObserver / input-event flag on the target
  BEFORE typing (V11), require the flag plus the value plus the caret
  offset (V4, see A33), and record before-value (A2). A value that appears
  with no input events and no keystrokes must fail. Bundle V1+V2+V3+V4+V11
  into one evaluate per step where feasible instead of 5 separate calls.
- C12-probe status: NEEDS CODE. The probe does not touch V11.

### A11. R11 - CDP default endpoint is Zen's BiDi port; Chromium path has the prefill hole (AMEND)

- Source: RT R11. Also C3 design gap (Brave default-profile conflict).
- Description: cu.BROWSER_ENDPOINT defaults to http://127.0.0.1:9222, which
  is Zen's BiDi port; cdp.mjs fetches /json/list from it (404 on Firefox
  141+, clone2 proved) and browser_start probes /json/version there,
  treating live Zen as dead and then cold-launching Chromium onto the port
  Zen already holds. The combined design TEXT routes CDP to Brave/Chrome
  only (correct); the assumption lives in the code defaults, not the design
  text. cdp.mjs set_value also has the prefill early return (see A2).
- File/function: scripts/cu.py:35 BROWSER_ENDPOINT;
  scripts/cdp.mjs:119-128 (/json/list fetch); scripts/cu.py:2121
  (browser_start /json/version probe); scripts/cdp.mjs set_value.
- Required fix: default the CDP endpoint to the Chromium/Brave port, never
  9222; probe BiDi (session.new) when the target is Zen; remove the
  set_value early return or require a real set (A2 fix). Note the
  dependency: doma11y open item 4 says Brave refuses
  --remote-debugging-port on the default user data directory and it cannot
  be enabled on an already-running browser, which conflicts with driving
  the already-logged-in Brave; verify the live Linux behavior before
  building the CDP half on it.
- C12-probe status: NEEDS CODE. The probe confirms CDP 9222 is LISTEN on
  the laptop and Marionette 2828 is LISTEN, but does not fix the default.

### A12. R12 - Session-slot wedge: the BiDi client takes no lock (AMEND)

- Source: RT R12. Also C2 D1, C3 BiDi/Marionette sequencing gap.
- Description: zen_dom.py takes a file lock ZEN_DOM_LOCK for its one
  WebDriver session, but zen_cli.py (BiDi) takes no lock, so nothing stops
  a BiDi session opening while a ZenSession (Marionette) holds the one
  Firefox session slot. Clone2 measured the Firefox cap on all runs:
  "Maximum number of active sessions". The combined design never names
  which tool switches tabs between clone1 and clone2.
- File/function: scripts/zen_dom.py:109-141 (ZEN_DOM_LOCK, one WebDriver
  session, always deleted); scripts/zen_cli.py:456-458 (session.new, no
  flock, no ZEN_DOM_LOCK anywhere in the file).
- Required fix: make zen_cli take the same ZEN_DOM_LOCK (or share one
  session manager), and name the tab-switch protocol in the benchmark
  runbook: Marionette only while a ZenSession is held; BiDi only after it
  exits. Specify the session lifecycle (open, use, close, leak handling)
  and the handover sequence (close Marionette, open BiDi, close BiDi,
  reopen Marionette, with a leak guard); budget the cold session.new cost
  (1.5-2.8s, 0.014s warm) if the benchmark wants BiDi rect reads AND
  Marionette real clicks on the same Zen instance.
- C12-probe status: NEEDS CODE. The probe used one Marionette session at a
  time with DELETE in finally (slot free after every run), which models the
  discipline required but does not implement the lock.

### A13. R13 - No DPR or zoom term, and none recorded (AMEND)

- Source: RT R13. Also C1 F2, C2 F2, C3 fix 2 (DPR half of the C12 build).
- Description: no devicePixelRatio or screenPixelsPerCSSPixel term exists
  in fastpath.py, zen_dom.py, or dom_act.py, and no snapshot records DPR or
  zoom. MDN: mozInnerScreenX/Y are CSS px, affected by zoom; physical px
  need screenPixelsPerCSSPixel. At the single measured config (DPR 1,
  scale 1, zoom 100%) the factor is 1 and invisible, which is why the
  "proven chain" looks proven. Arithmetic: at scale 2 a rect center 306 CSS
  px from the viewport origin is 612 screen px away; the code maps 306 and
  lands about 306 screen px off.
- File/function: scripts/fastpath.py:152-167 dom_rect_to_screen_point();
  scripts/zen_dom.py:367-383 viewport_origin().
- Required fix: read window.devicePixelRatio (and visualViewport scale /
  fullZoom) with every snapshot, apply screenPixelsPerCSSPixel in the
  conversion, record DPR/zoom with the snapshot, and refuse or re-ground
  when the recorded factor changes.
- C12-probe status: CHANGED (bounded), not moot. The probe measured DPR=1,
  monitor scale=1, zoom 100% live on the target Zen, so at the measured
  config the missing term changes nothing today. The code term is still
  required for any scaled display or zoomed page; the probe only bounds the
  current impact, it does not supply the term.

## B. Council items (C1 F1-F6, C2 F1-F6 + D1-D6, C3 fixes 1-5)

Items already merged into section A are listed with their merge target and
not repeated. Only the council-only items get full entries here.

### B1. Wire the DOM verification hooks into the production path (GATING)

- Source: C1 F1, C2 F1, C3 fix 1 (all three councils, same gating item).
- Merges: C1 F3 (band false-pass shape, "the fix is F1"), C2 F1(a) (caret
  tests), C3 fix 1 (caret test). Related to A2/A3/A4 (the defects it closes).
- Description: the focus_check/type_check hooks exist in
  scripts/cu.py:1570 desktop_act, but no production caller passes them
  (scripts/cu.py:2470, :2759, scripts/first_action.py:581 all call
  desktop_act without hooks; only tests and scripts/dom_act.py focus_type
  do). scripts/dom_act.py has no production caller (grep finds no importer
  outside its own test). The sufficient DOM value check therefore exists as
  an opt-in library, not on any live path, so the live path still verifies
  with a necessary-not-sufficient signal, exactly the defect class R1 gated
  on, narrowed but not closed. The amend's own R1 demo test uses a
  pixel-identical after image and does not cover the caret case.
- File/function: scripts/cu.py:1570 desktop_act() (hooks);
  scripts/first_action.py:581 (fallback caller); scripts/cu.py:2470
  (session path), :2759 (CLI act); scripts/dom_act.py focus_type().
- Required fix, in order: (a) first_action/session driver passes
  zen_dom-based focus_check/type_check closures when the batch targets a
  known DOM field (or routes browser type batches through
  dom_act.focus_type), with the session closed or reused under the
  one-session rule (A12); (b) failing that, change desktop_act so a type
  batch without a DOM hook is labeled band-only in the envelope
  (type_verified_basis already says input-line-band; the envelope must
  carry that basis too, via the R3 copy, so no consumer reads
  type_verified as text-delivered). Acceptance test (all three councils
  agree on its shape): click + stubbed type with an after image differing
  from the pre-batch image ONLY by a caret column / focus ring on the
  anchor line must report ok False with error_code type_unverified. Until
  wired, downgrade the R1 claim in the amend log from "the incident shape
  now fails" to "narrowed to the input line; correct-click/no-text still
  false-passes without the DOM check". Alternative fix path (C3 only):
  make the band sufficient without DOM by requiring the band change to
  exceed a caret-scale baseline (count changed pixels against the
  caret-only shape, or require text-shaped change on the line). The
  coordinator decides: wiring the DOM check is the councils' preferred
  order; the caret-baseline is the fallback, not a second fix to do as well.
- C12-probe status: NEEDS CODE. The probe does not touch hook wiring.

### B2. Size-mismatch fail-open in _input_line_changed (AMEND)

- Source: C1 F4, C2 F3(a). (The RT half is A3.)
- Description: when old.size != new.size, _input_line_changed returns True,
  so a resize between frames verifies any type batch. Incomparable images
  are treated as a pass.
- File/function: scripts/cu.py:1038-1039 _input_line_changed().
- Required fix: return None (unverifiable, falling back to the labeled
  frame-hash path) instead of True. Verify with a unit test: two
  different-sized images, band returns None.
- C12-probe status: NEEDS CODE.

### B3. type_anchor tracks move/hover; restrict to click/double_click (AMEND)

- Source: C2 F3(b). (C2 probe P7: hover-state change on the anchor line
  false-passes.)
- Description: type_anchor tracks move/hover/drag-to, so a hover-state
  pixel change on the anchor line verifies a type batch that delivered no
  text.
- File/function: scripts/cu.py type_anchor tracking (desktop_act).
- Required fix: restrict type_anchor to click/double_click targets only.
  Verify with a unit test for the hover shape (P7).
- C12-probe status: NEEDS CODE.

### B4. Off-line-click false-fail: document it and cover it with a test (AMEND)

- Source: C2 F3(c). (C2 probe P6: text lands in the field at y=1132 but the
  anchor is the missed click y=1037, band returns False.)
- Description: the band is anchored to the click, not the field, so text
  that lands off the anchor line false-fails. The DOM check (B1) is the
  fix; the band alone cannot distinguish this shape from a real failure.
- File/function: scripts/cu.py _input_line_changed() + type_anchor.
- Required fix: document the off-line-click false-fail shape and cover it
  with a test; the DOM check from B1 is the fix for it.
- C12-probe status: NEEDS CODE.

### B5. zen_dom `list` CLI dies with a traceback on a wedged session (AMEND)

- Source: C2 F4. (Side effect of the R7 scan-stop fix, which all councils
  agree is otherwise DONE.)
- Description: after the R7 fix, the `list` subcommand has no error
  handling, so a wedged session dies with a traceback instead of printing
  JSON error entries.
- File/function: scripts/zen_dom.py:503-504 (`list` CLI subcommand, main).
- Required fix: catch ZenDomError in main and print a JSON error object
  with exit code 1. Verify with a wedged-session CLI test.
- C12-probe status: NEEDS CODE.

### B6. verify_typed exact-equality brittleness for contenteditable (AMEND)

- Source: C2 F5.
- Description: verify_typed uses exact equality against the field value,
  but for contenteditable, textContent can carry a trailing newline or
  whitespace or pre-existing text, which false-fails a correctly typed
  message.
- File/function: scripts/zen_dom.py verify_typed().
- Required fix: compare stripped/ends-with, or document the exact-empty-
  field precondition. Verify with a test carrying a trailing newline in
  the field value.
- C12-probe status: NEEDS CODE.

### B7. Relay tests never exercise the band (coverage note, AMEND)

- Source: C2 F6. (C1 notes the same shape for TYPE_AFTER_REFRESH: a
  type-only batch passes via the whole-frame-hash fallback and never runs
  the band.)
- Description: the relay tests pass via the whole-frame-hash fallback
  (type-only batches, no anchor), so they never exercise the band path
  above the unit level.
- File/function: tests/test_session_continuation.py (relay-level tests);
  scripts/cu.py desktop_act() band path.
- Required fix: add one relay-level click+type test with distinct
  after-image pixels so the band path is covered above the unit level, or
  record the gap in the amend log.
- C12-probe status: NEEDS CODE (test work, not probe work).

### B8. Combined-design gaps: specify before implementation (AMEND, design doc)

- Source: C1 F5 (a)-(g). Overlaps C2 D1-D6 and C3 design gaps; each
  sub-item maps to its owner entry below.
- Description: the combined design lists steps with no owner, no file, and
  no measurement. C1 requires each gap to be settled in the design doc
  (owner + file named, or explicitly deferred with reasons) before the
  benchmark worker builds on it.
- Sub-items and their owner entries:
  - (a) One-shot bulk harvest (doma11y C1) as a single evaluate returning
    all rects, replacing ground_many's 3N evals: see B13.
  - (b) Brave CDP DOM.getBoxModel + Accessibility.getFullAXTree in
    scripts/cdp.mjs, or an explicit scope cut to Zen-only with the Brave
    path deferred: see B14.
  - (c) Exactly-once send ledger (intent + sent-bubble check): see A6.
  - (d) V12 sent-bubble finish gate as a thread-DOM read: see A5/A6.
  - (e) V11 MutationObserver/input-event flag bundled into the one-evaluate
    verification call: see A10.
  - (f) BiDi/Marionette session handover protocol under the one-session
    constraint: see A12 and B9.
  - (g) An owner for step-6 loop hygiene, or drop step 6 from the design:
    see B15.
- C12-probe status: NEEDS DOC + CODE. The probe settles none of these
  except by narrowing (a): the probe's Marionette reads are cheap and
  repeatable, which supports the bulk-harvest cost case, but does not build
  it.

### B9. One-session sequencing unspecified (AMEND, design decision)

- Source: C2 D1. Also A12, C3 BiDi/Marionette gap.
- Description: if the benchmark wants BiDi rect reads (fastest per clone2,
  0.006-0.011s) AND Marionette real clicks on the same Zen instance, the
  sessions must be sequenced (close one before opening the other) and the
  cold session.new cost (1.5-2.8s) budgeted. The design names Marionette
  for the Zen harvest, which avoids the handover but gives up BiDi speed;
  either way the choice and its cost must be written down.
- File/function: design doc (improvements/worker-coord-click2-log.md
  combined design); scripts/zen_cli.py + scripts/zen_dom.py session
  lifecycle.
- Required fix: write down the choice (Marionette-only harvest, or
  sequenced BiDi+Marionette) with its session cost, in the design doc and
  the benchmark runbook.
- C12-probe status: NEEDS DOC. The probe ran Marionette-only with strict
  DELETE-after-use, which is consistent with the Marionette-only choice.

### B10. HCU guard has no owner or location (AMEND, design decision)

- Source: C2 D2. Owner entry is A7; this is the design-doc half.
- Description: which component re-checks live geometry/focus before each
  input (dom_act? a wrapper around desktop_act?), per action or per batch?
  As written the guard is a citation, not a component.
- Required fix: name the owner component and the per-action placement in
  the design doc; the code fix is A7.
- C12-probe status: NEEDS DOC + CODE (see A7).

### B11. Mantis numbering on live Messenger: unproven port (AMEND, design/build)

- Source: C2 D3. Also C1 step-1 review, C3 design gap (numbering layer).
- Description: Mantis is Chromium-only, so the numbering/diff format must
  be ported to the Marionette harvest, and ref stability on a mutating chat
  page is unaddressed (messages stream in; positional refs shift; a stable
  key such as a selector or node id is needed). The vendor numbers (29-47%
  fewer tokens, 29-37% fewer calls, about a third less time) were measured
  on public sites with other models and must not be carried as expected
  gains for Messenger/Zen. The harvest returns selectors, not stable refs;
  refs must be minted per snapshot and remapped per call, and Messenger is
  React plus contenteditable with a dynamic DOM, so ref stability across
  re-reads is unproven.
- File/function: new numbering layer (no file yet); scripts/dom_act.py
  ground_many() (returns selectors today).
- Required fix: build the numbering layer as a port (not an import), mint
  stable refs per snapshot, and prove ref stability live on Messenger
  before quoting any vendor gain.
- C12-probe status: NEEDS CODE. The probe does not touch numbering.

### B12. "VISION 1" is a DOM harvest, not a screenshot (AMEND, terminology)

- Source: C2 D5.
- Description: the benchmark's "2 visions" are really 1 DOM read + 1
  screenshot check. The terminology as written misleads the count.
- File/function: design doc / benchmark runbook terminology.
- Required fix: say so in the runbook ("1 DOM read + 1 screenshot check"),
  or rename the steps so the count does not mislead.
- C12-probe status: MOOT AS A CODE FIX (doc wording only), and the probe
  itself is the example: its verdict came from Marionette reads plus grim
  screenshots, not from two visions.

### B13. Two windows (clone1 + clone2) in one Zen instance vs two instances (AMEND, design decision)

- Source: C2 D6.
- Description: one Marionette session covers both tabs only if they share
  an instance. The design does not say whether clone1 and clone2 run as
  two tabs in one Zen instance or two instances.
- File/function: design doc / benchmark runbook; scripts/zen_dom.py tab
  handling (tab_at, list_tabs).
- Required fix: state the choice in the runbook before the benchmark.
- C12-probe status: NEEDS DOC. The probe ran on a single Zen instance
  (PID 496121) and does not decide the two-window shape.

### B14. One-shot bulk harvest vs per-element grounding (AMEND, build)

- Source: C1 step-1 review, C2 D1 context, C3 step-1 gap. (C1 F5(a) owner.)
- Description: the amend builds per-selector grounding, not one-shot bulk
  harvest: scripts/dom_act.py:64-72 ground_many calls ground_input per
  selector, 3 evals each (locate + viewport_origin + hit_check),
  re-reading the origin every time. Clone2 measured one-shot 66 rects in
  0.019s Marionette / 0.006-0.011s BiDi versus 16ms per element (55x
  slower), so the amend's shape is the slow shape clone2 warned against.
  For 2 inputs it is fine; for "every input + button of both clones" it is
  not the bulk harvest the design claims.
- File/function: scripts/dom_act.py:64-76 ground_many() (replace with a
  single-evaluate bulk harvest); scripts/zen_dom.py (one evaluate returning
  all rects).
- Required fix: implement the bulk harvest as a single evaluate returning
  all rects (doma11y C1), replacing ground_many's 3N evals. Brave CDP half
  (DOM.getBoxModel + Accessibility.getFullAXTree in scripts/cdp.mjs) is
  either built with it or explicitly deferred with a Zen-only scope cut
  (C1 F5(b)); note the A11 dependency (Brave default-profile CDP conflict)
  before building the CDP half.
- C12-probe status: NEEDS CODE.

### B15. Step-6 loop hygiene unowned (AMEND, design decision)

- Source: C1 F5(g), C2 step-6 note, C3 step-6 note.
- Description: prompt caching, diff-gated re-observation, downscale,
  context editing, low effort, adaptive waiting: none of these live in this
  repo's code; they are agent-loop behaviors with no file, no owner, and no
  measurement in the design. Listing them as design steps without an owner
  is a gap, not a plan. No council objects to them; all three note them as
  unbuilt.
- File/function: design doc (no code file).
- Required fix: name an owner for step 6, or drop step 6 from the design.
- C12-probe status: NEEDS DOC (or an explicit drop).

### B16. Per-type-group verification for multi-input batches (AMEND)

- Source: C3 fix 3. (C3 review item 4 sub-issue: the band anchors on the
  last pointer target before the FIRST type only, and the focus gate runs
  only before the first type group.)
- Description: in a two-input batch the second type has neither a band
  check on its own line nor a focus re-check, because the band anchors on
  the last pointer target before the first type only and the focus gate
  runs only before the first type group.
- File/function: scripts/cu.py desktop_act() (focus_checked once-only flag;
  band anchoring).
- Required fix: run the focus gate before EVERY type group (drop the
  focus_checked once-only flag or reset it per group) and anchor a band per
  type group (the last pointer target before that type), not only before
  the first type. Verify with a two-input click+type+click+type test where
  the second type is stubbed.
- C12-probe status: NEEDS CODE.

### B17. Preserve a passing DOM type check on the terminal-None path (AMEND, minor)

- Source: C3 fix 4. (Mirror of A4.)
- Description: when the DOM type check passed on the terminal-None path
  (type_dom_verified True), the branch still reports type_verified None,
  because the verification block only runs when 'after' is in the result
  and the after-capture is skipped there. The DOM pass is discarded. Not a
  false pass, a lost true pass. Polish, not blocking.
- File/function: scripts/cu.py terminal_address None branch.
- Required fix: consult type_dom_verified there the way the
  after_capture=False branch does, so a DOM-verified type reports
  type_verified True with basis dom-value. Fold into the A4 fix.
- C12-probe status: NEEDS CODE.

### B18. V4 caret position unbuilt (AMEND, build)

- Source: C3 step-4 review (V4 not implemented); C1 F5(e) (V4 in the
  one-evaluate bundle); RT R10 fix (caret offset required alongside V11).
- Description: step 4 claims V1+V2+V3+V4+V11 in one evaluate per step. The
  amend implements V1/V2/V3 (field value, innerText via field_value,
  activeElement via focus_check) but NOT V4 (caret position) and NOT V11
  (A10). V12 (A5/A6) is also unimplemented anywhere.
- File/function: scripts/zen_dom.py (new caret-position helper, same
  evaluate bundle as V1-V3/V11).
- Required fix: implement V4 (caret position / caret offset) and bundle it
  with V1+V2+V3+V11 into one evaluate per step where feasible.
- C12-probe status: NEEDS CODE.

### B19. Relabel the 7/7 accuracy number as map accuracy, not grounding accuracy (AMEND, label/test)

- Source: C1 bar-numbers check, C2 item-12 review, C3 owner-corrections
  review (all three agree).
- Description: the 7/7 = 100% synthetic accuracy in DomRectMappingTests is
  circular on the load-bearing step: the 7 cases test the linear map given
  a correct viewport origin, and the truth rect in _hit is built from that
  same origin (tests/test_pick4_fastpath.py:482-560), so the test is
  circular on origin acquisition. The number is a map-accuracy number, not
  a grounding-accuracy number, and must be labeled as such. Live grounding
  accuracy is still owed by the 2-vision benchmark. The bar numbers that
  ARE accepted as measured: observes per task 3 (1 preflight fresh + 1
  after-capture + 1 settle re-capture), actions per observation 3
  (click, type, Enter), both from the fake harness, not a live run.
- File/function: tests/test_pick4_fastpath.py:482-560;
  tests/test_dom_act.py; improvements/worker-click-amend-log.md (bar
  numbers section).
- Required fix: relabel 7/7 as map accuracy in the tests and the amend log,
  and drive the accuracy cases from a real origin acquisition (A1 fix).
  Do not quote the synthetic 7/7 as live accuracy anywhere.
- C12-probe status: CHANGED. The probe supplies the true origin
  acquisition the tests lack (window origin + window-relative mozInner),
  so the rewritten tests can now be driven from the probe's measured
  values. The relabel itself still needs doing.

### B20. Item-12 numbering clarification (log only)

- Source: C1 F6.
- Description: the amend log counts the owner-corrected grounding item as
  item 12, while the coord log counts C1 1-3 + RT R1-R9 as the 12. The two
  numberings must not be read against each other.
- File/function: improvements/worker-click-amend-log.md (AMEND2 note
  already added in the amend log: owner-corrected grounding item REPLACES
  the original item 12 shape; R9 covered by the widening at
  scripts/first_action.py:56-61).
- Required fix: one-line log confirmation that the amend log states which
  item the DOM-first work replaces and confirms R9 is covered by the
  widening. Verify the AMEND2 note already in the amend log says this; if
  it does, this entry is DONE, no further action.
- C12-probe status: MOOT (log wording only; the probe does not affect it).

### B21. G28 over-refusal on stale SCREEN observations (accepted, no action)

- Source: C3 G28 special attention (not a required fix).
- Description: blanket refusal refuses one legitimate case: a stale given
  SCREEN observation with screen-written pointer coordinates would have
  worked on the substituted screen capture, since both regions are the
  monitor box. The rejected dict carries no scope (only given_id, age_s,
  reason), so run() cannot tell that case apart. C3 judges blanket refusal
  correct anyway: the screen content is 100+ s old and may have changed,
  the session guard would likely refuse on screen change, and the cost of
  refusing is one re-observe round trip, which is the documented procedure.
  Key-only batches (Escape, Ctrl+Tab) are also refused on a stale
  observation, but they would fail on screen scope in desktop_act anyway,
  so that is a louder failure, not a new one. The no-observation default is
  unaffected (rejected is None).
- File/function: scripts/first_action.py run() (no change).
- Required fix: NONE REQUIRED. Optional refinement only: plumb scope
  through the rejection to preserve the legitimate SCREEN case. Record as
  accepted.
- C12-probe status: MOOT (no action; the probe does not affect it).

## C. Verified DONE by all three councils (no action)

The 12 consolidated round-1 items were each verified in code by C1, C2,
and C3 independently (315-test suite OK, fail-before reproduced in own
worktrees). Listing them here so this checklist is complete and no one
re-opens them.

- C1-1 session_continuation regression: FIXED (fixture hash '1111').
- C1-2 G28 widening to pointer-only batches: DONE (refuses every batch;
  has_keyboard gate gone). R9 satisfied by the widening itself.
- C1-3 type_verified None on the terminal-None path: DONE (but see A4/B17
  for the remaining ok-True and lost-DOM-pass halves on that path).
- R1 (round 1) whole-frame-hash redesign: PARTIAL, see A3/B1 (the band
  narrows it; the sufficient check is unwired). Not done.
- R2 (round 1) pointer substitution top-level flag: DONE, subsumed by the
  refusal (stronger form).
- R3 (round 1) envelope type_verified/error_code: DONE on both paths.
- R4 (round 1) refusal remedy split: DONE.
- R5 (round 1) zen_dom raw escapes: DONE (JSON decode, HTTPException,
  missing "value" all become ZenDomError).
- R6 (round 1) restore surfacing: DONE (raise, never swallow).
- R7 (round 1) scan budget: DONE (stops after first transport failure,
  raises wedge). Side effect: see B5.
- R8 (round 1) tab_at verification/downgrade: DONE (handle-list index
  claim; switch verified via _verify_selected).
- R9 (round 1) G28 docstrings: DONE, moot by widening.
- Side effect noted by C2: R10 minor (range check now precedes
  current_handle()) fixed as a side effect.
- Sound, needs no change (C3): G28 blanket refusal, session_continuation
  fixture repair, R3 envelope fields, R4 remedy split, R5 _wd conversion,
  R6 restore surfacing, R7 scan stop, R8 handle verification plus claim
  downgrade, R9 docstrings, 0-observes-added bar number, fail-before
  evidence for all five new suites.

## D. What the C12 probe verdict does to this list

Probe verdict (commit cd89597, live 03:36 +07 22/11, Zen PID 496121, ws1):
window.mozInnerScreenX/Y in this Zen build are WINDOW-RELATIVE, NOT absolute
screen coordinates. mozInnerScreenX=240, mozInnerScreenY=8, DPR=1, measured
4 times (03:23, 03:27, 03:30, 03:32). Absolute viewport origin is
(2509+240, 914+8) = (2749, 922). One real click at candidate B (2628.5,
973.5) focused the urlbar and selected the full URL text; candidate A
(120, 60) is off-monitor and was never clicked.

- MOOT (no code needed, question answered): NOTHING is fully moot. No
  finding is removed by the probe. The two entries marked MOOT above
  (B12 terminology, B20 numbering, B21 accepted over-refusal) are moot
  for reasons unrelated to the probe (doc wording / already accepted).
- CHANGED (fix direction now known, code still needed): A1 (R1: the
  empirical half is done; implement window origin + mozInnerScreen), A13
  (R13: DPR=1 bounds the current impact; the term is still required),
  B19 (7/7 relabel: the probe supplies the true origin values the
  rewritten tests need).
- CHANGED (a prescribed fix is partly unachievable as specified): the
  AT-SPI cross-check half of the C12 build (C1 F2, C2 F2, C3 fix 2, A1).
  The probe's run 3 proves AT-SPI cannot see Zen at all (bus works, 6
  apps listed, Zen PID 496121 not registered; accessibility never
  activated at its 17:37 startup), and run 2 proves chrome-context eval
  via geckodriver moz/context is BLOCKED (HTTP 500, needs
  MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1 plus a Zen restart, which must NOT be
  done). So the "cross-check against AT-SPI screen extents" as specified
  cannot run on this Zen. The fix must substitute another cross-check
  (e.g. grim pixel-edge measurement as the probe used, or hyprctl window
  geometry), or explicitly drop the cross-check with reasons. Do not keep
  prescribing AT-SPI as if it worked.
- CLARIFIED (not a change to the fix, but to the evidence): the ZT-B line
  "mozInnerScreenX returned null" is NOT evidence against the amend; C2
  and C3 both show it is explained by those evals omitting `return`, and
  the probe confirms Marionette returns mozInnerScreenX/Y fine (4 reads)
  when `return` is present. Also clarified: the urlbar is browser chrome,
  not page content (no content document.querySelector can see it; run 1,
  all 4 selectors null), so no fix may read chrome rects from the content
  DOM.
- UNTOUCHED by the probe: A2, A3, A4, A5, A6, A7, A8, A9, A10, A11, A12,
  B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, B11, B13, B14, B15, B16, B17,
  B18. Every one of those still needs code, doc, or test work as specified.

## E. Consistency verdict: is the list internally consistent?

YES, with two items for the coordinator to decide, neither a contradiction.

1. Verdict-threshold difference, same facts: RT says BLOCK, C1/C2/C3 say
   AMEND. This is not a factual contradiction. All four agree R1 and C12
   are not closed on the live path and the caret false pass is real. They
   differ on the gate: RT blocks because R1-R6 include live-path failures
   (R1 raises instead of clicking; R5 fails a real send and R6 double-sends
   on retry; R2/R3/R4 false-pass), while the councils judge AMEND because
   nothing that worked before is broken, every new failure mode is loud
   (fail-closed, no wrong click), and the 315-test suite passes with
   fail-before proven. The checklist keeps RT's BLOCK severity on R1-R6
   and the councils' AMEND on the rest; the coordinator decides the gate.
2. Fix-path alternative, not a contradiction: C1 F1 / C2 F1 (wire the DOM
   check into the production path) versus C3 fix 1 option (b) (make the
   band sufficient without DOM via a caret-scale baseline). These are two
   ways to close the same caret false pass. The checklist records the
   councils' preferred order (wire the DOM check first; caret-baseline
   only as fallback). Do both only if the coordinator says so; doing the
   baseline INSTEAD of the wiring leaves A2/A4/A5 unfixed.
3. Checked and NOT contradictions:
   - RT R1 "resolve empirically" vs C1 F2 / C2 F2 / C3 fix 2 prescribing
     window origin + mozInnerScreen: same direction, all consistent with
     the E2 report, and the probe now proves it.
   - C1 F5(a) bulk harvest vs RT R7 "re-ground each input at its own send
     time": compatible (harvest once, re-validate before each click); the
     design must state both, see B8/B14.
   - RT R11 "default the CDP endpoint to the Chromium/Brave port" vs C3
     "Brave refuses --remote-debugging-port on the default user data
     directory": a dependency to verify live before building the CDP half,
     not a contradiction (see A11/B14).
   - C1 "R9 moot by widening" vs C2/C3 "R9 fixed": same conclusion.
   - C2 F3(c) off-line false-fail vs A3 band narrowing: same limitation
     seen from opposite sides; the DOM check (B1) is the fix for both.
   - C3 "G28 blanket refusal is correct" (B21) vs RT R4 "ok True with
     type_verified None": different paths (refusal path vs
     verification-skipped path); no conflict.
   - C1/C2/C3 all agree the 7/7 number is circular; no reviewer defends
     it as live accuracy.
4. One numbering trap, already flagged by C1 F6 and the amend log's AMEND2
   note: "item 12" means two different things in the amend log
   (owner-corrected grounding item) and the coord log (C1 1-3 + RT R1-R9).
   This checklist uses the coord numbering for round-1 items and the RT
   R-numbering for round-2 findings, and never uses bare "item 12".

## F. Counts and acceptance

- Entries: 13 redteam (A1-A13) + 21 council/design entries (B1-B21) =
  34 entries. Merged duplicates: C1 F2 / C2 F2 / C3 fix 2 into A1; C1 F3 /
  C2 F1(a) / C3 fix 1 into B1; C1 F4 / C2 F3(a) into B2; C2 D4 / C1 F5(c)
  into A6; C2 D2 / C1 F5 into A7/B10; C1 F5(e) / C3 step 4 into A10/B18;
  C3 fix 4 into A4/B17; C1 F5(a) / C3 step 1 into B14.
- Gating order (this worker's read of the sources, coordinator decides):
  first A1 + A13 (conversion, probe now gives the formula), then B1 + A3
  + A2 + A4 (verification wiring and ok-True holes), then A5 + A6 (send
  ordering and exactly-once), then A7-A12 + B2-B7 + B16-B18 (stale DOM,
  hit, shadow, V11, CDP, lock, hygiene), then B8-B15 (design doc gaps)
  before the benchmark worker builds on the design.
- Acceptance for the whole list: tests/test_click2_redteam.py all 23 pass
  (RT verdict condition), plus the caret-only test (B1), the
  window-relative-origin test (A1), the size-mismatch None test (B2), the
  two-input stubbed-second-type test (B16), the wedged-session CLI test
  (B5), the trailing-newline verify_typed test (B6), and a live Zen probe
  confirming R1 (A1) before any benchmark claim. The 2-vision benchmark
  with outcome scoring (both messages landed) and live wall time vs the
  Codex 2.5 min mark remains owed after the fixes, as all sources state.
- Live confirmation still owed on the laptop (RT log): R1 (done by the
  C12 probe, see section D), R8 (real Messenger composer center), R9
  (shadow/iframe structure of the real target DOM), and the 2-vision
  benchmark as a whole. The combined design's step-3 guard, step-1 bulk
  harvest, and V12 finish gate are design text only and were reviewed as
  text, not as code, because the code does not contain them.
- No em dash (U+2014) or en dash (U+2013) in this file (checked by grep
  before commit). No ydotool. No personal info (no real names beyond the
  owner name Pham Tuan as instructed for repo-facing text, no emails,
  addresses, phones, schedules, photos, accounts, passwords, tokens).

## G. Time log (wall-clock +07, elapsed from task start 04:33)

- 04:33 +00m task received, branch todolist-push confirmed, HEAD da60024.
- 04:34 +01m all six source commits verified present (175d3ef, 25ebf10,
  e7b4a52, 9424bae, 4b7d6ac, cd89597).
- 04:34-04:36 +01-03m all six logs read in full (RT, C12 probe, C1, C2,
  C3, amend).
- 04:37 +04m code cross-checks (grep): key functions located; observed
  uncommitted AMEND2 work in the working tree (24 files), recorded in the
  header note, not touched.
- 04:36-04:38 +03-05m checklist written (sections A-G).
- No 15-minute stall occurred at any point.
