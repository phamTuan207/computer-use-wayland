# CLICK3-AMEND3 log: surgical re-dispatch of AMEND2

Worker: CLICK3-AMEND3 (fix worker). Coordinator: COORD-CLICK-2.
Owner: the owner (repo-facing name). Branch: todolist-push.
Task start: 04:56 +07 22/11/2026 (task stamp; first measured wall
clock on this VM 04:46 +07, VM clock runs about 10 min behind the
coordinator stamp; all times below are measured wall-clock
Asia/Ho_Chi_Minh on this VM plus elapsed from task receipt).
Standing rules: full access, no em dash (U+2014) or en dash
(U+2013) anywhere including quoted window titles, never ydotool,
no personal info in repo files, log everything.

Sources read first, in order:
- improvements/worker-click3-diff-assess.md (commit 910e471):
  verdict KEEP MOST, 1 regression (cdp.mjs set_value), 3 weak RT
  tests (R1, R3a, R10), handoff steps 1-9.
- improvements/worker-click3-rt-synth.md (commit dd45231): 34
  entries A1-A13 + B1-B21.
- improvements/worker-click2-c12probe-log.md (commit cd89597):
  verdict WINDOW-RELATIVE, absolute origin (2749, 922) on probe
  geometry, window (2509, 914) + mozInner (240, 8).

Scope decisions (recorded up front):
- Step 8 (independent R7 re-verification) NOT done by this worker:
  a fresh reviewer does it after landing. This worker does not
  grade its own fixture edit.
- tests/test_click2_redteam.py: only the R1 test rewrite ordered by
  handoff step 2 is touched in that file. The R7 shadow fixture
  edit and the R3a/R10 redteam tests are left exactly as AMEND2
  left them, pending fresh re-verification. The new R3a and R10
  failing-first tests live in tests/test_type_verification.py and
  tests/test_zen_dom.py instead.
- C12 AT-SPI cross-check: DROPPED as specified. Probe run 3 proves
  Zen is not on the AT-SPI bus (bus works, 6 apps listed, Zen PID
  496121 not registered) and run 2 proves chrome-context eval is
  blocked (HTTP 500, needs a Zen restart, which must not be done).
  Substitute cross-check, already in the code: the dimension
  closure + window/monitor containment checks in
  zen_dom.check_viewport_geometry, validated by the probe with grim
  pixel-edge measurement of the urlbar pill. No live laptop driving
  by this worker; no new AT-SPI attempt.
- RT-SYNTH remaining CODE items audit (see the end of this log):
  B18 V4 caret position is the only CODE item not covered by steps
  1-7 or already done; it is listed out of scope with reasons.
  B11 Mantis is explicitly deferred in the coord-log addendum;
  B13 one-vs-two Zen instances is settled there (one Zen instance,
  two tabs); B8/B9/B10/B15 design gaps are settled in the addendum;
  B20 numbering is confirmed in the amend log; B21 is accepted
  with no action. All other A/B CODE items were verified done by
  the assessment (R2/R4/R5/R6/R7/R8/R11/R12/R13 in substance, plus
  B1 wiring, B2 size-mismatch None, B3 click-only anchors, B4
  off-line false-fail documented, B5 clean CLI failure, B6
  trailing-whitespace normalization, B7 relay band test, B16
  per-group bands, B17 terminal-None DOM pass, B19 MAP relabel,
  B14 one-shot harvest).

## Time log

- 04:46 +00m task received; branch todolist-push, HEAD 910e471 at
  receipt (moved to 807ba6e during this task, an unrelated skill
  commit by another worker; the AMEND2 tree is unchanged: 24 files,
  +2496/-304). Assessment, RT-synth checklist, C12 probe log read
  in full. Baseline: test_cdp_snapshot 2 tests, FAILED (failures=1),
  the regression reproduces exactly as assessed.
- 04:50 +04m AMEND2 tree committed verbatim in 11 small groups,
  each pushed and verified with git ls-remote: 2a25e7a zen_dom,
  7d09c0f dom_act, 35d42fb cu, 32e6e8f fastpath, ea6d163 cdp.mjs,
  449a3de zen_cli + first_action, f2eb90b 9223 defaults (3 files),
  d720814 zen_dom/dom_act/fastpath tests, b02b4f1 type-verification
  and 4 more test files, 6b1284d redteam + browser-start + endpoint
  tests + cdp validation, c01d4a2 amend-log + coord-log addenda.
  Working tree clean except 4 untracked other-worker files, left
  untouched. HEAD c01d4a2.
- 04:52 +06m Step 1 done: cdp.mjs set_value captures oldValue
  before the setter write and dispatches input/change only when the
  value changed; setter write and read-back stay unconditional.
  test_cdp_snapshot 2/2 OK. Committed e5c1c47, pushed, ls-remote
  verified. Full discover started 04:52 to confirm 0 failures
  (assessor baseline: 1850 tests, 1 failure + 4 pre-existing errors
  + 17 skipped).
- 04:55 +09m Full discover after step 1: Ran 1850 tests, FAILED
  (errors=4, skipped=17). 0 failures, exactly the step-1 target.
  The 4 errors are the pre-existing set (a11y skeleton import,
  cursor_file g++ -std=c++26, perf_evidence x2 missing benchmark
  JSON). Step 1 CLOSED.
- 04:56 +10m Step 2: rewrote test_raw_moz_inner_screen_origin_must_
  land failing-first (ran 04:56, FAILED: ValueError not raised, the
  fallback rescued the raw pair), then deleted the fallback in
  dom_rect_to_image_point and updated its docstring. R1 suite 3/3,
  fastpath 28/28, dom_act 13/13. Committed 0367ec9, pushed,
  ls-remote verified. Note: HEAD moved under this worker to 8457997
  (coord2 baseline commit, unrelated); the push stayed fast-forward.
  Step 2 CLOSED, R1 now proven through viewport_origin, not the net.
- 04:58 +12m Step 3: wrote the R3a failing-first tests first (ran
  04:56, FAILED errors=2: desktop_act got unexpected keyword
  type_x_ranges; substance check on the old code: 12 wrong-field
  pixels returned True from the full-width band), then implemented:
  _input_line_changed gains x_range, desktop_act gains
  type_x_ranges, dom_act.grounded_x_range computes the image-px
  range from the grounded rect, focus_type passes it through act_fn,
  first_action grounds best-effort after open_dom_hooks and passes
  it. min_pixels 4 and per-group anchors kept. test_type_verification
  59/59 (57 + 2 new), dom_act 13/13, first_action 63/63, redteam
  71/71. Committed 0356389, pushed, ls-remote verified. Step 3
  CLOSED, R3a closed in substance. Follow-up noted, not done: the
  cu CLI act path and CodeExecBackend.act do not yet supply ranges
  (they still get the DOM value check, the sufficient check; the
  band is only their fallback).
- 04:59 +13m Step 4: wrote the R10 failing-first test first (ran
  04:58, FAILED: typed_flag True and verify_typed True on a JS-set
  empty field), then implemented: verify_typed consults the V11
  typed flag whenever before is given, not only in the prefill case;
  FakeDomSession.verify_typed mirrors it; both fakes' typed_flag now
  model the trusted-event flag faithfully (True only on a recorded
  trusted input event; a bare value change leaves it clear). The
  earlier value-change fallback is what made the fakes blind to the
  JS-set attack. Prefill case kept as-is. test_zen_dom 36/36 (35 +
  1 new), dom_act 13/13, redteam 71/71. Committed d7b1579, pushed,
  ls-remote verified. Step 4 CLOSED, R10 closed in substance.
- 05:00 +14m Step 5: wrote the factor-2 test failing-first (ran
  05:00, FAILED: ZenDomError not raised for impossible CSS geometry
  at factor 2), then implemented: viewport_origin converts the
  Hyprland screen-px window size to CSS px before
  check_viewport_geometry, ground_many_one_shot does the same for
  its direct check call (outer stays as-is when no window size is
  given, it is already CSS px), docstring states the contract.
  test_zen_dom 37/37 (36 + 1 new), dom_act 13/13, redteam 71/71.
  Committed 4110e72, pushed, ls-remote verified. Step 5 CLOSED.
  Note: the containment check now compares a screen absolute origin
  against a CSS-px window rect, which is conservative at factor > 1
  (it can only refuse, never accept a wrong origin); the viewport
  origin sits mozInner * factor from the window origin, well inside
  that rect for any real sidebar geometry. This follows the
  assessment's prescribed fix literally.
- 05:02 +16m Step 6: fail-before evidence is the pre-fix source
  (0 occurrences of contentWindow in field_value/verify_typed at
  HEAD before this step; locate already had it), then implemented:
  both methods now use the same find() helper (shadow pierce, then
  same-origin iframe traversal with cross-origin try/catch), so an
  iframe target reads and verifies, and a cross-origin target fails
  closed. The test fake learned the find() selector shape (its
  extraction missed the new helper and returned None until the
  pattern was added; caught by the existing field_value test, fixed
  in the same step). test_zen_dom 38/38 (37 + 1 new), dom_act 13/13,
  redteam 71/71. Committed 2dcd5d8, pushed, ls-remote verified.
  Step 6 CLOSED. Note: focus_check still uses a top-document
  querySelector (no pierce, no iframe walk); the handoff names only
  field_value and verify_typed, so it is left as-is and recorded
  here as a known gap, not silently fixed.
- 05:02 +16m Step 7: deleted the duplicate import os in zen_cli.py
  (kept line 92, deleted line 96); py_compile OK, one import os
  remains. Committed 5d49e51, pushed, ls-remote verified. Step 7
  CLOSED.
- 05:03 +17m Step 9 (step 8 is the fresh reviewer's job, not this
  worker's): full affected set re-run, all OK: test_click2_redteam
  71/71, test_dom_act 13/13, test_zen_dom 38/38, test_pick4_fastpath
  28/28, test_type_verification 59/59, test_first_action 63/63,
  test_keyboard_preflight 32/32, test_session_continuation 11/11,
  test_fast_observe 40/40, test_browser_start_warm 11/11,
  test_endpoint_retention 7/7 (373 tests total), node
  tests/cdp_validation.mjs 3 ok lines (key preflight, adapter
  preflight, harvest). Full discover started 05:03, result below.
- 05:06 +20m Full discover after all fixes: Ran 1855 tests
  (1850 + 5 new), FAILED (errors=4, skipped=17). 0 failures. The 4
  errors are the pre-existing set, unchanged. Step 9 DONE. R1, R3a,
  and R10 are claimed CLOSED only now, after their new failing-first
  tests pass (steps 2-4 above).

## RT-SYNTH remaining CODE items audit (task item a)

Checked every A/B entry against the assessment verdict and the
code as landed. DONE already (verified by the assessment, kept
verbatim): A1 window origin, A13 DPR/zoom term, A2 prefill,
A3 R3b/R3c, A4 ok-True holes, A5 Enter ordering, A6 exactly-once,
A7 stale DOM/HCU guard, A8 interactive-child hit, A9 shadow walk
(iframe half closed by step 6), A10 V11 mechanism (substance
closed by step 4), A11 CDP endpoint, A12 session lock, B1 DOM hook
wiring, B2 size-mismatch None, B3 click-only anchors, B4 off-line
false-fail documented, B5 clean CLI failure, B6 contenteditable
whitespace, B7 relay band test, B14 one-shot harvest, B16
per-group bands, B17 terminal-None DOM pass, B19 MAP relabel.
Design/doc entries settled in the coord-log addendum: B8 combined
gaps, B9 one-session sequencing (Marionette only while held, BiDi
after exit), B10 HCU owner (dom_act), B12 VISION 1 terminology,
B13 one Zen instance two tabs, B15 step-6 owner (parent
orchestrator). B20 numbering confirmed in the amend log. B21
accepted with no action.
OUT OF SCOPE, with reasons:
- B18 V4 caret position (unbuilt). Not implemented. A caret offset
  adds no discrimination beyond the V11 trusted-input-event flag
  that step 4 now enforces: a page script can set el.value and then
  set selectionStart to the end in one extra line, defeating any
  caret check, while isTrusted cannot be forged by page JS
  (synthetic events are untrusted). Requiring caret-at-end would
  also false-fail legitimate flows (click mid-text to edit, IME
  composition). V4 is a UX signal at best, not a verification
  signal; R10 is closed in substance by the flag. If a caller ever
  needs the caret for another reason, the helper belongs in
  zen_dom next to field_value, bundled in the same evaluate.
- B11 Mantis numbering: explicitly deferred in the coord-log
  addendum (vendor numbers do not transfer to Messenger React, ref
  stability unproven). A design deferral, not code this worker
  should build.
- Focus_check iframe/shadow query (noted in step 6): the handoff
  names only field_value and verify_typed. Left as-is, recorded as
  a known gap.
- cu CLI act path and CodeExecBackend.act do not yet supply
  type_x_ranges (noted in step 3). They still get the DOM value
  check, the sufficient check.

## C12 cross-check decision (task item b)

The AT-SPI half of the C12 build cannot run on this Zen and is
dropped as specified: probe run 3 proves Zen is not on the AT-SPI
bus, probe run 2 proves chrome-context eval is blocked without a
Zen restart (which must not be done). No new AT-SPI attempt was
made and no live laptop driving was done by this worker. The
substitute cross-check is the one already in the code and validated
by the probe with grim pixel-edge measurement: dimension closure
plus window/monitor containment in check_viewport_geometry.

## Commit record (all pushes verified with git ls-remote)

AMEND2 verbatim groups: 2a25e7a zen_dom, 7d09c0f dom_act, 35d42fb
cu, 32e6e8f fastpath, ea6d163 cdp.mjs, 449a3de zen_cli +
first_action, f2eb90b 9223 defaults, d720814 zen_dom/dom_act/
fastpath tests, b02b4f1 type-verification + 4 test files, 6b1284d
redteam + browser-start + endpoint tests + cdp validation,
c01d4a2 amend-log + coord-log addenda.
Amend3 fixes: e5c1c47 step 1, 0367ec9 step 2, 0356389 step 3,
d7b1579 step 4, 4110e72 step 5, 2dcd5d8 step 6, 5d49e51 step 7.
This log: committed last, explicit pathspec, push verified.
HEAD at finish: see the coordinator copy of this log for the hash
(this worker's final report carries it).
No 15-minute stall occurred at any point. No em dash or en dash in
this file (checked by grep before commit). No ydotool. No personal
info (owner name the owner only, as instructed for repo-facing
text).

## AMEND2 commits (verbatim, grouped, before the fixes)

The 24 uncommitted AMEND2 files are committed first in small
groups, verbatim as assessed, so each fix commit below shows
exactly its own delta. One fix per commit, explicit pathspec
immediately after staging, never plain git commit, never git
add -A. Push after each commit, verified with git ls-remote.
The 4 untracked files in the tree are other workers' files and are
left untouched.
