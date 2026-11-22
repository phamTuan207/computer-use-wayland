# Batch 13 task 2: review of the (b1) landing spec for feasibility

## 0. Verdict: AMEND

The spec is not ready to land as written. The design decision (option A,
standalone focus action) is sound, and nearly every line citation and
measured number in the spec verified first-hand against the code at the
review HEAD. But four things must change before landing:

1. Section 10 item 1 is false at the review HEAD: the focusenter helper
   source is now in the repo (commit 3ef8f55).
2. Section 10 item 11 is false at the review HEAD: all 25 P9 PNGs are
   now in the repo (commit 3ef8f55), and I verified all 25 against the
   manifest myself.
3. The section 5 send-requires-focus rule is unsound as worded: it
   lists `type` as a focus-establishing action, but `type` does not
   establish focus. A `[type, key Enter, assert]` batch with no click
   would pass the rule yet fail silently the same way
   `[set_value, key Enter]` does.
4. The section 8 and section 11 dry-run elapsed expectation (about
   105 to 115 ms) is wrong. The 17 to 25 ms figure is the Enter time,
   not the focus time, and it is a live measurement, while the dry run
   runs on scratch tabs where Enter measured 2 ms. The corrected
   dry-run expectation is about 90 to 100 ms.

Fix those four, plus the smaller items F5 to F10 below, and the spec can
land. No shared code was changed by this review. Report only.

## 1. Scope and method

- Spec reviewed: docs/batch12-task2-b1-landing-spec-20261122.md on
  origin/main, 571 lines, including its fix pass commit 20f3b99.
- Spec base: branch todolist-push, HEAD 4305dcb (stated in the spec).
- Review HEAD: origin/todolist-push 3167c76. The branch moved during
  this review to 8c6553a; I re-checked the diff between 3167c76 and
  8c6553a for every file listed below and it is empty, so all findings
  hold at 8c6553a as well.
- Code read first-hand, read-only, from origin/todolist-push with
  `git show` (the branch was never checked out and never modified):
  scripts/cdp.mjs (641 lines), scripts/code_exec.py (1297 lines),
  scripts/cu.py (3465 lines), scripts/dom_asserts.py (227 lines),
  scripts/dom_act.py (866 lines), scripts/s2_flip_live.py (812 lines),
  scripts/element_ref.py (293 lines), tests/test_s2_flip_wiring.py
  (244 lines), tests/cdp_validation.mjs (133 lines),
  tests/test_step5_p1p5.py, scripts/action_result.py.
- Evidence read first-hand from the same branch:
  improvements/s2-flip-b1-runs/run-1..5.json and run-2..5-aborted.json,
  improvements/s2-flip-reopen-runs/run-1..5.json,
  improvements/s2-flip-runs/run-1..5.json,
  improvements/s2-flip-b1-runs/c5-focusenter.mjs,
  improvements/s2-flip-p9-manifest.md,
  improvements/worker-click5-input-fix-log.md (commit 4bd6292),
  improvements/worker-click5-s2-reopen-log.md (commit 1a3356d),
  improvements/worker-click4-s2-flip-log.md.
- Every number in section 2 was recomputed from the run JSONs with a
  script, not copied from the logs. Every line citation in section 2
  was checked with grep or direct read at HEAD 3167c76.
- Rules kept: no personal information anywhere, no long dashes,
  no ydotool, real numbers only, all verified first-hand.

## 2. What checked out

### 2.1 Line citations (all exact at HEAD 3167c76)

- cdp.mjs:83 to 84, max_elements 1..80 check. Line 84 is the range
  check. Correct.
- cdp.mjs:157 to 167, pageState. Starts line 157, ends line 167.
  Correct.
- cdp.mjs:250 to 251, shadow-root activeElement walk in harvest.
  Correct.
- cdp.mjs:292 to 314, click. The three dispatchMouseEvent calls are
  on lines 311 to 313. The spec says 292 to 313, which covers the
  calls but not the closing brace on line 314. Trivial slip, see F9.
- cdp.mjs:390 to 412, key. The text '\r' for Enter is line 410.
  Correct.
- cdp.mjs:434, action whitelist. Correct.
- cdp.mjs:435 to 437, element-action list (exactly one of ref or
  selector). Correct.
- cdp.mjs:467 to 470, stale-snapshot check on every action in the
  dispatch loop. Correct.
- cdp.mjs:473 to 533, set_value branch. Correct.
- cdp.mjs:478, unavailable-field checks with error 'field
  unavailable'. Correct.
- cdp.mjs:501 to 502, set_value visible and hit-testable check.
  Correct.
- cdp.mjs:517 to 518 and 528, the read-back check, repeated.
  Correct.
- cdp.mjs:534 to 541, fill. ActiveElement check line 536, error
  wording 'field is not editable or did not gain focus' line 537.
  Correct.
- cdp.mjs:546, completed increment. Correct. The assert action also
  increments completed, so a fully successful 4-action program
  reports completed 4. The spec's dry-run expectation of completed 4
  is consistent with the code.
- cdp.mjs contains no e.focus() call anywhere. The only occurrences
  of "focus" are a comment, harvest `focused:` fields, and the fill
  error string. The spec section 1 item 1 claim is correct.
- code_exec.py:217, allowed set. Line 218, element_actions. Correct.
- code_exec.py:277 to 284, P2 scope plus observation_id binding check.
  Correct.
- code_exec.py:922 to 940, P5 gate in _api_dom_act. The
  require_asserts call is lines 936 to 939, not 936 to 938 as the
  spec says; it closes on line 939 with 'sent_bubble': False. Trivial
  slip, see F9. The call does pass available focus_check True,
  type_check True, sent_bubble False. Correct in substance.
- cu.py:1299, browser allowed set. Line 1341, browser element-action
  check (ref and selector mutually exclusive, non-empty strings).
  Correct.
- dom_asserts.py:26 to 29, fill and set_value map to type_check,
  enforced inside cdp.mjs. Correct.
- dom_asserts.py:48 to 50, click entry. Lines 63 to 65, fill entry.
  Lines 66 to 68, set_value entry. Correct.
- dom_asserts.py:96 to 114, _is_send_key. It covers Enter after type,
  fill, or set_value. Correct.
- dom_asserts.py require_asserts fails closed on unknown action types
  (an entry of None adds an 'unknown action' message) and has the
  trailing-assert rule (a trailing assert action satisfies the
  sent_bubble requirement). Correct.
- dom_act.py:708 to 712, focus_type chain [click, type, key Enter].
  Line 748, require_asserts gate. Correct.
- s2_flip_live.py:76 LAPTOP_FOCUSENTER, 77 LAPTOP_COUNT, 84
  BUBBLE_ASSERT_SELECTOR, 89 to 126 build_program, 117 to 121 the
  trailing bubble assert with timeout_ms 3000, 129 to 161
  build_program_set_value (set_value plus a value assert, 2 actions,
  no key, no focus), 189 to 195 variant_for, 316 to 338 v12_check
  (10 second poll), 340 to 356 p9_capture, 478 to 495 count_check,
  497 to 519 focus_enter, 539 to 543 pre-send guard, 568 to 588 CB-1
  (set_value branch 568 to 578, fill branch 579 to 585, verified set
  at 588), 691 to 704 delayed count (10 second sleep, recount),
  780 to 795 the --set-value and --chromium-set-value flags. All
  correct.
- tests/test_s2_flip_wiring.py has 12 test methods. The named tests
  exist as described: test_set_value_program_carries_p2_stamps_and_
  passes_p5 (2 scope stamps, 2 observation_id stamps, require_asserts
  with available focus_check True, type_check True, sent_bubble
  False), test_program_actions_satisfy_p5_requires ([fill, key Enter,
  assert] passes), test_chromium_set_value_splits_variants_per_browser.
  The spec section 8 claim "it is 12 of 12 today" matches the reopen
  log section 1 (line 115: "tests 12/12 pass (was 11/11)") and
  section 8.
- tests/cdp_validation.mjs extracts production functions with vm and
  runs the whole adapter with a fake CDP transport. The spec section 8
  description of the pattern is correct, with one gap, see F10.

### 2.2 Measured numbers (all recomputed from the run JSONs)

- (b1), 5 runs: 5 of 5 sends verified, outcomes sent. Median wall
  18839.7 ms. Program elapsed 91.575 to 106.622 ms. Helper enter.ms
  17 to 23 ms. Pre-send count 0 in all 5. Delayed count exactly 1 in
  all 5. Model calls 0. Completed 2 in all 5. All match the spec
  section 0.
- (b1) aborted first attempts: runs 2 to 5, outcome aborted-routing,
  walls 12365.3, 14372.5, 12652.1, 13734.2 ms. The spec section 0
  qualification ("5 of 5 completed runs, not 5 of 5 attempts") is
  correct, and the aborted JSONs exist as run-N-aborted.json.
- Reopen, 5 runs: 10 of 10 sends verified, outcomes sent on both
  browsers. Median wall 28560.9 ms. Chromium program elapsed 99.412
  to 113.005 ms. Helper enter.ms 21 to 25 ms. Pre-send count 0 in
  all 5. Delayed count exactly 1 in all 5. Model calls 0. V12
  attempts 1 in all 10 sends (field name `attempts`). All 5 Chromium
  runs ran relaxed (routing_relaxed True, observe truncated True, 80
  elements). All match the spec sections 0, 6, 7, and 10 item 7.
- Reopen phase split residual: 2708.9, 2827.3, 2743.1, 2750.1, 2914.5
  ms across runs 1 to 5. Median 2750.1 ms. The spec section 7 figure
  is correct. The count_check helper appends no span (verified in
  code), while focus_enter does append a span. The spec section 7
  artifact note is correct.
- Original flip, Chromium: 0 of 5 sends, outcome failed-unverified
  in all 5. The dom_act log lines read "dom_act ok False completed 0
  ms 5003" in runs 1, 3, 4, 5 and "ms 5002" in run 2. The flip log
  section 5 names the cause as "CDP timeout: Input.dispatchMouseEvent"
  in each run. The spec section 0 numbers are correct.
- D-B1 probe: Input.dispatchKeyEvent answers in 2 ms on the stuck
  tab (input-fix log section 7.1). The probe used Shift, not Enter;
  the spec section 2 states it as a dispatchKeyEvent result, which is
  accurate.
- Scratch mechanism probe T1 to T4 (input-fix log section 7.2):
  T1 0 bubbles with focus on BODY, T2 1 bubble after evaluate
  focus() plus CDP Enter, T3 1 bubble with JS-dispatched Enter and no
  focus (untrusted event, live React behavior untested), T4 still 1
  bubble on a second CDP Enter into the empty composer. The spec
  section 2 summary is accurate.
- Reopen dry run 0 baseline (reopen log section 3): PASS, wall
  30123.9 ms, Chromium elapsed 85.8 ms, completed 2. Correct as cited
  from the log. Note it is log-only evidence, see F13.
- Reopen log section 6 recommends EXPAND. Reopen log section 5
  records P9 PASS 10 of 10. Both citations in the spec sections 0
  and 7 are correct.

### 2.3 Design checks that hold

- The landed 4-action program [set_value, focus, key Enter, assert]
  passes require_asserts only if the focus entry is added to ASSERTS:
  without it, `focus` is an unknown action type and require_asserts
  raises before any CDP request. The spec section 5 edit list covers
  this dependency.
- Adding `focus` to code_exec.py allowed and element_actions is
  sufficient for validation: _validate_dom_actions then applies the
  exactly-one ref-or-selector check and the ref-in-snapshot check
  automatically, and element_ref.validate_action_binding (lines 146
  to 164) is type-agnostic (it checks observation_id and scope only).
  The spec section 5 claim "no new field validation is needed" is
  correct.
- The CB-1 mapping proposed in section 5 is sound: input_sent =
  completed >= 3 means set_value, focus, and Enter all ran;
  target_received = completed >= 1 means the set_value read-back
  passed (a failed set_value throws before completed increments).
  The old mapping description (helper result for input_sent,
  completed >= 1 for target_received) matches the code at lines 574
  to 575.
- The section 5 claim that dropping the separate value assert is safe
  holds: set_value verifies the value internally (cdp.mjs:517 to 518,
  repeated at 528) and throws 'value verification failed' on mismatch.
- The section 3 option B accounting note is correct: under B the
  program would be [set_value, key Enter, assert], so input_sent =
  completed >= 2 stays a counted action number. The loss is
  granularity, not accounting ambiguity, as the spec says.
- The section 9 step 3 test list is complete for the touched modules:
  tests/test_step5_p1p5.py and tests/test_dom_act.py both exist, and
  require_asserts has only two production callers (code_exec.py:936
  and dom_act.py:748). Adding the focus ASSERTS entry does not break
  the AssertSetTests in test_step5_p1p5.py: none of their chains
  contains a focus action, and they assert exact required sets only
  for those chains. action_result.py only re-exports
  DOM_ASSERT_EXCEPTIONS and is unaffected.

## 3. Findings: where the spec is wrong or incomplete

### F1 (HIGH, stale): section 10 item 1, the focusenter helper is now in the repo

What the spec says (section 10 item 1): "The /tmp/c5-focusenter.mjs
source is not in the repo. It lives only on the laptop. Its exact
semantics must be recovered before the focus action is written."

What is true at HEAD 3167c76: the helper source IS in the repo at
improvements/s2-flip-b1-runs/c5-focusenter.mjs, committed in 3ef8f55
("C5-P9-EVIDENCE: commit 25 P9 screenshots plus manifest and
focusenter helper", 28 files). I read it first-hand: 2478 bytes, 42
lines, sha256
94ee467ed3067e044491ad19153c24b73d574a8106a5367db454c0e47e1a695f,
matching the manifest row exactly. Its semantics match the input-fix
log section 7.3 description the spec cites: Runtime.evaluate focus
on textarea[aria-label="Message"], assert it is document.activeElement,
then Input.dispatchKeyEvent keyDown plus keyUp Enter, zero mouse
events, returns {ok, focus, enter}.

Fix: strike section 10 item 1 and reword it as closed. Section 4
should cite the committed file as the reconstruction basis instead of
the log description alone, and the "if the laptop file is gone"
recovery clause is now moot for focusenter. The same staleness affects
section 1 item 2, which calls it "a laptop-only helper": the file is
still at /tmp on the laptop, but it is no longer laptop-only. The
reopen log section 8 line listing laptop helpers "not in the repo"
is stale in the same way for focusenter; that is the log's text, not
the spec's, but the spec inherits the wording.

### F2 (HIGH, stale): section 10 item 11, the P9 PNGs are now in the repo

What the spec says (section 10 item 11): "The 10 reopen P9 PNGs (5
runs x 2 browsers, promised in improvements/worker-click5-s2-reopen-
log.md, section 8) and the 5 (b1) P9 PNGs are not on todolist-push.
Section 7 asserts P9 PASS 10 of 10 in the reopen from the log's prose
descriptions, but no reviewer can re-check the render from the repo."

What is true at HEAD 3167c76: all 25 P9 PNGs are on todolist-push,
committed in 3ef8f55 alongside improvements/s2-flip-p9-manifest.md:
5 (b1) Chromium PNGs (1,210,605 bytes), 10 reopen PNGs (2,354,937
bytes), 10 original flip PNGs (2,740,488 bytes), 6,306,030 bytes
total. I verified all 25 independently against the manifest with a
section-aware script: sha256, byte size, and PNG magic all match on
25 of 25 rows, zero mismatches. The section 7 "P9 PASS 10 of 10" claim
is now backed by committed render evidence, not only by log prose.

Fix: strike section 10 item 11. Two notes for the fix pass. First,
the run JSONs still carry p9 as null in every JSON, so the PNG paths
come from the audit repair-list filename convention, as the manifest
records; the spec should say that instead of implying the JSONs name
the PNGs. Second, the 5 original flip Chromium PNGs show NO test
bubble, which agrees with their JSON outcome failed-unverified; they
must not be cited as send evidence, as the manifest states. The spec
never mentions the flip PNGs, so no spec text is wrong on that point,
but the landing verification log should repeat the warning.

### F3 (HIGH, design): section 5 lists `type` as a focus-establishing action, it is not

What the spec says (section 5): "The scope is set_value-preceded
sends only: fill, click, confirm_click, hover_click, and type are
focus-establishing actions." The proposed rule therefore raises only
when the send key's nearest preceding value action is set_value.

What the code says: in dom_act.py focus_type (lines 664 to 712), the
CLICK establishes focus, not the type. The docstring says "Click an
input, type, and verify", and the chain built at lines 708 to 712 is
[click, type, key Enter]. The type step types into the field the click
already focused; it performs no focus of its own. In cdp.mjs there is
no `type` action at all (whitelist line 434), so the claim is vacuous
on the code-exec path as well.

Consequence: a batch [type, key Enter, assert] with no preceding click
would pass the spec's rule (nearest preceding value action is type)
yet fail silently in exactly the way the rule exists to prevent: the
type would go to whatever happens to be focused, and the Enter would
go to BODY. No such batch exists today (focus_type always includes the
click), so the hole is latent, not live, but the rule as specified
would bless the unsafe shape if one is ever written.

Fix: reword the section 5 rule to exempt only batches containing an
actual focus-establishing action before the send key (click,
confirm_click, hover_click, fill, or the new focus), regardless of
which value action precedes the key. Define "preceding" explicitly as
"before the send key in the same batch"; a focus action after the send
key must not satisfy it. Under this wording [set_value, key Enter]
raises, [click, type, key Enter] passes (the click is the
focus-establishing action), [fill, key Enter] passes (fill focuses
internally through its click, cdp.mjs:534 to 537), [type, key Enter]
raises, and [set_value, focus, key Enter] passes. Add the
corresponding test, see F10 item (e).

### F4 (HIGH, acceptance criterion): section 8 and section 11 dry-run elapsed is wrong

What the spec says (section 8): "The landed dry run must match it
except completed 4 instead of 2, and Chromium elapsed about 105 to
115 ms instead of 85.8 ms: the landed 4-action program adds a focus
step (measured 17 to 25 ms in the helper) and a key step (about 2 ms)
to the 85.8 ms baseline." Section 11 repeats "Chromium elapsed about
105 to 115 ms" as an acceptance criterion.

Two errors in the derivation, both verified first-hand:

(a) The 17 to 25 ms figure is the ENTER time, not the focus time.
In the run JSONs the helper reports enter.ms of 17 to 23 ms for the
(b1) runs and 21 to 25 ms for the reopen runs, measured around the two
dispatchKeyEvent calls only. The focus evaluate was never timed
separately; the helper does not record it. The spec adds the Enter
time as if it were the focus cost, then adds a separate "key step
(about 2 ms)".

(b) The 17 to 25 ms figures are LIVE measurements, while the dry run
runs on scratch tabs, where Enter measured 2 ms (input-fix log
section 7.4: "focus_enter ok True (focused TEXTAREA, Enter 2ms)";
the D-B1 probe in section 7.1 also measured 2 ms). The spec applies
live timings to a scratch-tab run.

Corrected derivation, from the same sources: dry-run baseline 85.8 ms
(reopen log section 3) plus one focus evaluate (one Runtime.evaluate;
the flip log section 5 run 1 records each V12 evaluate at 2 to 3 ms,
so about 2 to 3 ms, assuming the focus plus activeElement check is
one combined evaluate) plus Enter on scratch (about 2 ms) plus the
trailing bubble assert polling (assertAction polls every 10 ms,
cdp.mjs:415 to 427, so about 0 to 10 ms). Corrected dry-run
expectation: about 90 to 100 ms, not 105 to 115 ms. As written, the
pass condition would likely fail on a healthy dry run (a false
failure) or train the landing team to expect live timings on scratch.

For the live re-runs the corrected expectation is different again:
live (b1) program elapsed 91.575 to 106.622 ms plus focus about 2 to
3 ms plus live Enter 17 to 25 ms plus assert polling about 0 to 10 ms,
so about 110 to 145 ms. The spec gives no live elapsed expectation at
all; section 9 step 6 should state one, using the live components
above.

Fix: rewrite the section 8 elapsed paragraph with the corrected
derivation, set the dry-run criterion to about 90 to 100 ms, add the
live re-run criterion of about 110 to 145 ms to section 9 step 6,
and fix the section 11 criterion to match the dry-run figure.

### F5 (MEDIUM): section 3 "the mirror already exists for every other action type" is false for hover_click

What the spec says (section 3, option A cost): "The 4 mirror files
are a one-time validation-mirror update, and the mirror already exists
for every other action type."

What the code says: hover_click is in the cdp.mjs whitelist (line
434) and in the code_exec.py allowed set (line 217), but it is NOT in
the cu.py browser allowed set (line 1299: click, confirm_click, fill,
set_value, key, scroll, wait, assert). A grep for hover_click across
cu.py at HEAD 3167c76 returns zero matches. The three-way mirror
already drifts today on one action type.

Consequence: the section 3 cost argument overstates how routine the
mirror update is, and the landing cannot assume the three whitelists
agree by construction. The spec section 5 edit list does name all
three files, so no edit is missing, but the landing must verify the
three whitelists agree for focus instead of assuming the pattern.

Fix: acknowledge the hover_click drift in section 3 (and record it as
a known pre-existing drift, not something this landing fixes), and add
a test asserting the three browser whitelists contain the same set,
see F10 item (f).

### F6 (MEDIUM): section 4 frames design additions as replication of the helper

What the spec says (section 4 intro): the focus action replicates
/tmp/c5-focusenter.mjs as documented in the input-fix log section 7.3.

What the helper actually does (read first-hand from the committed
file): if the textarea is missing it returns {focused: false, error:
'no-textarea'}; on focus failure it throws 'composer did not gain
focus'. It performs NO unavailable-field checks. Section 4 step 2
(disabled, :disabled, readOnly, aria-disabled, inert, error 'field
unavailable') is borrowed from the set_value branch (cdp.mjs:478),
and section 4 step 4 (error wording 'field is not editable or did not
gain focus') is borrowed from fill (cdp.mjs:537). Both borrowings are
sound design choices, and step 5 ("Return ok") is a deliberate
narrowing of the helper's {ok, focus, enter} shape, but none of the
three is a replication of the helper.

Fix: label steps 2, 4, and 5 as design additions borrowed from
set_value and fill, not as helper behavior. One sentence each is
enough.

### F7 (MEDIUM): the spec never compares the helper Enter params with the landed key params

Verified first-hand from the committed helper and from cdp.mjs
lines 390 to 412:

(a) The helper sends code: 'Enter' on both keyDown and keyUp. The
landed key() never sends a `code` field for any key; it sends key,
modifiers, windowsVirtualKeyCode, and nativeVirtualKeyCode only.
(b) The helper sends text: '\r' on keyDown only; its keyUp carries no
text. The landed key() sends the same params object, including text
'\r', for both keyDown and keyUp.

Both differences are probably harmless: the composer keys off e.key,
and browsers ignore text on keyUp. But the section 3 fidelity argument
("preserves those measured step boundaries one to one") is step-level
only, and the landing would silently change the wire params of the
measured Enter. The spec should record the two differences and either
justify them or decide whether key() needs a `code` field for Enter.
Add as a section 4 note or a section 10 open item. Do not change key()
silently inside the landing without recording the decision.

### F8 (LOW): section 5 "must sit between set_value and key in the chain"

The dispatch chain in cdp.mjs is an else-if over distinct action
types (lines 471 to 545), so branch position is irrelevant to
execution order; the action list order decides. "It must sit between
set_value and key" is misleading as a requirement. Soften it to a
style suggestion (keep the branches in action-list order for
readability). No behavior is at stake.

### F9 (LOW): two one-line citation slips

- Section 5 cites the _api_dom_act require_asserts call as
  code_exec.py:936 to 938. The call spans lines 936 to 939; it closes
  on line 939 with 'sent_bubble': False.
- Section 2 cites the click function as cdp.mjs:292 to 313. The
  function closes on line 314; the three dispatchMouseEvent calls are
  on lines 311 to 313, inside the cited range, so the substantive
  claim is true and only the closing brace falls outside.
Fix both ranges in place.

### F10 (MEDIUM): missing test steps in section 8

The section 8 lists are good and mostly complete. These are missing:

(a) Focus failure path: a focus where the evaluate returns
activeElement !== e must throw 'field is not editable or did not gain
focus' (the section 4 step 4 wording). The listed tests cover the
unavailable-field error only, not the focus-failure error.
(b) Focus via selector: the listed tests resolve a ref only. The spec
says "exactly one of ref or selector" (section 4 step 1); add a
selector-resolution focus test.
(c) Missing trailing assert on the landed shape: [set_value, focus,
key Enter] without the trailing assert must fail P5. The existing
test_program_without_trailing_assert_would_fail_p5 covers the fill
shape only, not the landed shape.
(d) Failing-first anchor for the dom_asserts change: the landed
4-action program must fail require_asserts BEFORE the focus entry
lands (unknown action type), and pass after. The spec's failing-first
anchor covers only the cdp.mjs rejection ('unsupported action').
(e) The corrected rule from F3: [type, key Enter, assert] with no
click must raise DomAssertError under the corrected rule, and [click,
type, key Enter, assert] must pass.
(f) Whitelist sync: a test asserting the three browser whitelists
(cdp.mjs line 434, code_exec.py line 217, cu.py line 1299) contain the
same set. This locks in the F5 fix and catches future drift.
(g) One clarification for the unit-test paragraph: the existing
cdp_validation.mjs key-function trick slices the source between
'async function key(' and 'async function assertAction(', which does
not apply to focus, because the focus branch lives inline in the
handle() dispatch loop, not in a standalone function. The focus unit
tests need the whole-adapter vm run with a fake page carrying
globalThis.__agentCu, refs, and an activeElement stub, like the
existing harvest test's fake page. Name that pattern explicitly so
the test author does not try to slice a function that does not exist.

### F11 (NOTE, confirmed no gap): the section 5 file list is complete

I checked the three places a new action type could need a change
beyond the spec's list. element_ref.validate_action_binding (lines 146
to 164) is type-agnostic. action_result.py only re-exports
DOM_ASSERT_EXCEPTIONS (line 33). test_step5_p1p5.py AssertSetTests
chains contain no focus action, so the new ASSERTS entry cannot change
their exact required-set assertions. No fourth file is missing from
the section 5 edit list.

### F12 (NOTE, stands): section 10 items 2 to 10, except 1 and 11

- Item 2 stands: /tmp/c5-count.mjs is still not in the repo. I checked
  with a tree listing grep for c5-count, zero matches. The pre-send
  guard and delayed count still depend on the laptop file.
- Items 3 to 6 stand: the coordinator has not picked option A or B in
  any commit I read; no focus tests exist yet; no live proof of landed
  code exists; the laptop tree sync and relay-restart question are
  still unverified.
- Item 7 stands: the 80-element cap is cdp.mjs:83 to 84, and all 5
  reopen Chromium runs ran relaxed (verified from the JSONs).
- Items 8, 9, 10 stand: the mouse stall is unsolved; the Brave
  decision is open; the shadow-root activeElement walk is a follow-up.

### F13 (NOTE): the dry-run baseline is log-only evidence

The section 8 baseline (wall 30123.9 ms, Chromium elapsed 85.8 ms,
completed 2) is cited to the reopen log section 3, which is honest,
but no run-0 JSON exists in the repo: a tree listing of
improvements/s2-flip-reopen-runs/ shows only run-1..5.json plus the
P9 PNGs. The landing team cannot recompute the baseline from a JSON.
One sentence in section 8 should say the baseline rests on log prose
only.

## 4. Missing test steps, consolidated

Add to section 8, in addition to F10 items (a) to (g):

- A negative test that a program of [set_value, focus, key Enter,
  assert] where the focus step is placed AFTER the Enter raises
  DomAssertError under the corrected F3 rule (focus must precede the
  send key). This pins the "preceding" definition.
- A test that the landed program builder emits the focus action with
  a ref (not a selector) and that the ref is the same composer ref as
  the set_value action, so a wrong-ref focus cannot silently focus
  another element.
- In the live dry run, record the focus step's own timing separately
  (one Runtime.evaluate) so the F4 derivation can be checked against
  a real number instead of the 2 to 3 ms estimate. The current
  program elapsed_ms covers the whole program; the focus cost inside
  it is not separately visible.

## 5. Recommendation for the fix pass

Apply F1 and F2 first: they are pure staleness from the evidence
landing in commit 3ef8f55 after the spec base 4305dcb, and they change
two section 10 items from open to closed. Then fix F3 (reword the
section 5 rule and add the F10 item (e) test) and F4 (rewrite the
section 8 elapsed paragraph and the section 11 criterion, and add the
live elapsed expectation to section 9 step 6). Then apply F5, F6, F7,
F8, F9, and F10. Re-verify the two stale items against the branch at
fix-pass time, because the branch keeps moving: the review HEAD was
3167c76 and the branch moved to 8c6553a during this review, with no
change to the reviewed files. The design decision (option A) needs no
rework, and the bulk of the spec verified clean, so the fix pass is
small. After the fix pass, the spec can land without a second full
review, provided the fix pass re-checks F3 and F4 against the code.

## 6. Verification log

Times are Asia/Ho_Chi_Minh, 22 November 2026. Work ran about 14:20
to 14:33 +07. No live runs, no browser work, no shared code changed.
Read-only `git show` and `git grep` against origin/todolist-push, plus
local scripts over the extracted JSONs.

- 14:20: fetched origin/main and origin/todolist-push. Local main at
  e03e288 (batch 13 assignment). todolist-push at 3167c76, matching
  the brief note.
- 14:21: read the spec (571 lines) in full. Extracted scripts/cdp.mjs,
  scripts/code_exec.py, scripts/cu.py, scripts/dom_asserts.py,
  scripts/s2_flip_live.py, scripts/dom_act.py,
  tests/test_s2_flip_wiring.py, tests/cdp_validation.mjs from
  origin/todolist-push to /tmp for read-only checking. Diff between
  the spec base 4305dcb and 3167c76 for those files is empty, so every
  cited line number still holds.
- 14:23: found commit 3ef8f55 (28 files: 25 P9 PNGs, manifest,
  focusenter helper, log) and correction commit b7d9fad after the spec
  base. Read the committed focusenter helper and manifest in full.
  This produced F1 and F2.
- 14:25 to 14:30: verified every line citation in section 2.1 with
  grep and direct reads. All exact except the two one-line slips in
  F9.
- 14:30: recomputed all section 2.2 numbers from the 15 run JSONs
  plus 4 aborted JSONs with a script. All match the spec except the
  F4 derivation, which misattributes the Enter time and mixes live
  with scratch timings.
- 14:33: verified the 25 PNGs against the manifest section by section
  (sha256, byte size, PNG magic). First attempt used a naive filename
  match and mismatched 15 rows because the same filenames repeat
  across the three sections; the section-aware rerun verified 25 of
  25, zero mismatches. The naive run's mismatches were a script bug,
  not a repo problem; the corrected run is the result reported here.
- 14:35: checked the remaining callers (require_asserts, assert_for,
  assert_coverage, DOM_ASSERT_EXCEPTIONS, validate_actions) and the
  hover_click drift in cu.py. Produced F3, F5, F10, F11.
- 14:31: confirmed the branch moved to 8c6553a during this review;
  the diff for all reviewed files between 3167c76 and 8c6553a is empty.
- 14:33: wrote this report to
  docs/batch13-task2-b1-spec-review-20261122.md, committed only that
  file, pushed to origin/main.

## 7. What this review did not do

- No shared code was changed. No edits to coord/clone1.md or
  coord/clone2.md. The untracked 0-byte test-w.txt was left alone.
- No live runs and no browser work. The corrected elapsed ranges in
  F4 are estimates from the existing measurements, stated as ranges
  with their components, not as new measurements.
- No council, redteam, or fix pass. Those follow under the batch 13
  brief.
