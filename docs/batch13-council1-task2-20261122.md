# Batch 13 council 1: review of the task 2 (b1) spec review

## 0. Verdict: AMEND stands, with one correction

I reviewed the task 2 report
docs/batch13-task2-b1-spec-review-20261122.md (commit f5e36e7,
verdict AMEND) first-hand against the real code on branch
todolist-push at HEAD 8c6553a and against the run JSONs, logs,
and manifest on the same branch. I agree with its verdict and
with every finding F1 to F13 in substance, except for one
error and two small gaps listed below.

The one error, C1, is in F2 note 1: the run JSONs do not carry
p9 as null. All 15 run JSONs carry p9 as a dict naming the PNG
paths, so the fix pass must not apply that note's
recommendation. The main F2 finding (all 25 P9 PNGs are in the
repo) is correct and unaffected.

The gaps, C2 and C3, concern the hover_click drift: the drift
also sits in the cu.py element-action check list, which F5 does
not mention, and the F10 item (f) whitelist-sync test as
specified cannot pass while that drift is unfixed. C4 is a
clarification on the F4 derivation premise, not a correction:
the corrected ranges still stand.

No shared code was changed by this review. Report only.

## 1. Scope and method

- Report reviewed: docs/batch13-task2-b1-spec-review-20261122.md
  on origin/main, commit f5e36e7, 7 sections.
- Spec reviewed by that report:
  docs/batch12-task2-b1-landing-spec-20261122.md, 571 lines,
  including its fix pass commit 20f3b99.
- Review HEAD: origin/todolist-push 8c6553a. The task 2 report
  reviewed at 3167c76 and stated the diff to 8c6553a is empty
  for the reviewed files. I confirmed that directly: git diff
  3167c76 8c6553a touches only
  improvements/worker-click5-step8-log.md, scripts/first_action.py,
  scripts/session_driver.py, scripts/session_remote.py, and
  tests/test_first_action.py, tests/test_session_driver.py,
  tests/test_session_remote.py, tests/test_visual_delivery.py.
  None of the files the task 2 report reviewed changed, so all
  of its findings hold at 8c6553a as well.
- Code read first-hand, read-only, from origin/todolist-push
  with git show (the branch was never checked out and never
  modified): scripts/cdp.mjs (641 lines), scripts/code_exec.py
  (1297 lines), scripts/cu.py (3465 lines),
  scripts/dom_asserts.py (227 lines), scripts/dom_act.py
  (866 lines), scripts/s2_flip_live.py (812 lines),
  scripts/element_ref.py (293 lines),
  tests/test_s2_flip_wiring.py (244 lines),
  tests/cdp_validation.mjs (133 lines),
  tests/test_step5_p1p5.py, scripts/action_result.py,
  improvements/s2-flip-b1-runs/c5-focusenter.mjs (42 lines),
  improvements/s2-flip-p9-manifest.md (64 lines).
- Evidence read first-hand from the same branch:
  improvements/s2-flip-b1-runs/run-1..5.json and
  run-2..5-aborted.json, improvements/s2-flip-reopen-runs/run-1..5.json,
  improvements/s2-flip-runs/run-1..5.json,
  improvements/worker-click5-input-fix-log.md (commit 4bd6292),
  improvements/worker-click5-s2-reopen-log.md (commit 1a3356d),
  improvements/worker-click4-s2-flip-log.md.
- Every number in the task 2 report section 2.2 was recomputed
  from the run JSONs with a script, not copied from the report.
  Every line citation in its section 2.1 was re-checked with
  grep or direct read at HEAD 8c6553a.
- Rules kept: no personal information anywhere, no long dashes,
  no ydotool, real numbers only, all verified first-hand.

## 2. Verdict per finding

### F1 (HIGH, stale): AGREE

The focusenter helper is in the repo at
improvements/s2-flip-b1-runs/c5-focusenter.mjs, committed in
3ef8f55 ("C5-P9-EVIDENCE: commit 25 P9 screenshots plus
manifest and focusenter helper", 28 files). I read it
first-hand: 2478 bytes, 42 lines, sha256
94ee467ed3067e044491ad19153c24b73d574a8106a5367db454c0e47e1a695f,
matching the manifest row and the task 2 report exactly. Its
semantics match the input-fix log section 7.3 description: it
focuses textarea[aria-label="Message"], asserts
document.activeElement, then sends dispatchKeyEvent keyDown
plus keyUp Enter, zero mouse events, returns {ok, focus, enter}.
The spec section 10 item 1 and section 1 item 2 ("a
laptop-only helper") are stale, and the reopen log section 8
line listing laptop helpers "not in the repo" is stale in the
same way for focusenter. All as the task 2 report states.

### F2 (HIGH, stale): AGREE on the finding, DISAGREE on note 1

All 25 P9 PNGs are on todolist-push, committed in 3ef8f55. I
verified all 25 independently against the manifest with a
section-aware script (full path, sha256, byte size, PNG magic):
25 of 25 match, zero mismatches. Subtotals from git ls-tree:
5 (b1) Chromium PNGs 1,210,605 bytes, 10 reopen PNGs
2,354,937 bytes, 10 original flip PNGs 2,740,488 bytes,
6,306,030 bytes total. All match the task 2 report and the
manifest exactly. The section 7 "P9 PASS 10 of 10" claim is now
backed by committed render evidence.

Note 2 stands: the manifest states the 5 original flip
Chromium PNGs show no test bubble, which agrees with their
JSON outcome failed-unverified, and they must not be cited as
send evidence. The spec never mentions the flip PNGs.

Note 1 is wrong, see C1 in section 3.

### F3 (HIGH, design): AGREE

The spec section 5 lists `type` as a focus-establishing action.
It is not. In dom_act.py focus_type (lines 664 to 712) the
chain built at lines 708 to 712 is [click, type, key Enter],
and the docstring says "Click an input, type, and verify". The
click establishes focus; the type step types into the field the
click already focused and performs no focus of its own. In
cdp.mjs there is no `type` action at all: the whitelist at
line 434 is click, confirm_click, hover_click, fill, set_value,
key, scroll, wait, assert. The task 2 report's consequence
holds: a batch [type, key Enter, assert] with no preceding
click would pass the spec's rule yet fail silently the same way
[set_value, key Enter] does. No such batch exists today
(focus_type always includes the click), so the hole is latent,
not live. The proposed rewording (exempt only batches with an
actual focus-establishing action before the send key) and the
worked examples are correct.

### F4 (HIGH, acceptance criterion): AGREE

The spec section 8 and section 11 dry-run elapsed expectation
(about 105 to 115 ms) is wrong, for the two reasons the task 2
report gives, both verified first-hand:

(a) The 17 to 25 ms figure is the Enter time, not the focus
time. In the helper source the timer t0 is set immediately
before the keyDown dispatch and enter.ms is read immediately
after the keyUp dispatch, so it covers only the two
dispatchKeyEvent calls. The focus evaluate is never timed
separately; the helper records no focus timing. The recomputed
JSON values are enter.ms 17 to 23 ms for the (b1) runs and
21 to 25 ms for the reopen runs, matching the task 2 report.

(b) The 17 to 25 ms figures are live measurements, while the
dry run runs on scratch tabs, where Enter measured 2 ms
(input-fix log section 7.4: "focus_enter ok True (focused
TEXTAREA, Enter 2ms)"; the D-B1 probe in section 7.1 also
measured 2 ms, using Shift, not Enter, as the task 2 report
correctly notes).

Corrected arithmetic, re-derived: dry-run baseline 85.8 ms
(reopen log section 3) plus focus evaluate about 2 to 3 ms
(flip log section 5 run 1: "each evaluate 2-3ms") plus Enter
on scratch about 2 ms plus assert polling about 0 to 10 ms
(assertAction polls every 10 ms, cdp.mjs line 426) gives about
90 to 100 ms. Live: (b1) program elapsed 91.575 to 106.622 ms
plus focus about 2 to 3 ms plus live Enter 17 to 25 ms plus
assert polling about 0 to 10 ms gives about 110 to 145 ms.
Both ranges match the task 2 report. One premise is unstated,
see C4, but the ranges still stand.

### F5 (MEDIUM): AGREE, with one added facet

hover_click is in the cdp.mjs whitelist (line 434) and in the
code_exec.py allowed set (line 217), but a grep for hover_click
across cu.py at HEAD 8c6553a returns zero matches, and the
browser allowed set at cu.py line 1299 is click,
confirm_click, fill, set_value, key, scroll, wait, assert.
The three-way mirror drifts today on one action type, as the
task 2 report states. The spec section 3 cost argument
("the mirror already exists for every other action type") is
therefore false. The spec section 5 edit list does name all
three files, so no edit is missing. Added facet, see C2: the
drift also sits in the cu.py element-action check list at
line 1341, which the task 2 report does not mention.

### F6 (MEDIUM): AGREE

The helper, read first-hand, returns {focused: false, error:
'no-textarea'} when the textarea is missing and throws
'composer did not gain focus' on focus failure. It performs
no unavailable-field checks. Spec section 4 step 2 (disabled,
:disabled, readOnly, aria-disabled, inert, error 'field
unavailable') is borrowed from the set_value branch
(cdp.mjs line 478), step 4 (error wording 'field is not
editable or did not gain focus') is borrowed from fill
(cdp.mjs line 537), and step 5 ("Return ok") is a deliberate
narrowing of the helper's {ok, focus, enter} shape. None of
the three is a replication of the helper, as the task 2 report
states.

### F7 (MEDIUM): AGREE

Verified first-hand from the committed helper and from
cdp.mjs lines 390 to 412. (a) The helper sends code: 'Enter'
on both keyDown and keyUp. The landed key() never sends a
`code` field for any key; it sends key, modifiers,
windowsVirtualKeyCode, and nativeVirtualKeyCode only.
(b) The helper sends text: '\r' on keyDown only; its keyUp
carries no text. The landed key() sends the same params object,
including text '\r' (line 410), for both keyDown and keyUp
(lines 411 to 412). Both differences are probably harmless, as
the task 2 report says, but the landing must record them
rather than change key() silently.

### F8 (LOW): AGREE

The dispatch chain in cdp.mjs is an else-if over distinct
action types (lines 471 to 545), so branch position is
irrelevant to execution order; the action list order decides.
"It must sit between set_value and key in the chain" is
misleading as a requirement and should be softened to a style
suggestion. No behavior is at stake.

### F9 (LOW): AGREE

Both one-line slips verified. The code_exec.py require_asserts
call spans lines 936 to 939; it closes on line 939 with
'sent_bubble': False, not 936 to 938 as the spec says. The
cdp.mjs click function starts at line 292 and closes on line
314; the three dispatchMouseEvent calls are on lines 311 to
313, inside the spec's cited range, so only the closing brace
falls outside.

### F10 (MEDIUM): AGREE, all seven items verified missing

(a) No test covers the focus-failure throw ('field is not
editable or did not gain focus' when activeElement is not e
after focus). The spec section 8 unit tests cover the
unavailable-field error only. Verified by reading the spec
section 8 list and grepping the test files: test_s2_flip_wiring.py
has 4 mentions of "focus", all of them the focus_check
available flag or a comment, and no focus-action test exists.

(b) No selector-resolution focus test exists; the spec section 8
list resolves a ref only.

(c) The existing
test_program_without_trailing_assert_would_fail_p5 covers the
fill shape only ([fill, key Enter] without assert, lines 189
to 197 of tests/test_s2_flip_wiring.py). No test covers the
landed shape [set_value, focus, key Enter] without the
trailing assert.

(d) The spec's failing-first anchor covers only the cdp.mjs
rejection ('unsupported action'). No anchor covers the
dom_asserts change (landed program must fail require_asserts
before the focus entry lands, unknown action type, and pass
after).

(e) The corrected F3 rule has no test: [type, key Enter,
assert] with no click must raise DomAssertError, and [click,
type, key Enter, assert] must pass.

(f) No whitelist-sync test exists. The drift in F5 is real,
so such a test would fail today on hover_click; see C3.

(g) The cdp_validation.mjs key-function trick slices the
source between 'async function key(' and 'async function
assertAction(' (line 6 of tests/cdp_validation.mjs). That
does not apply to focus, because the focus branch lives inline
in the handle() dispatch loop (cdp.mjs lines 471 to 545), not
in a standalone function. The focus unit tests need the
whole-adapter vm run with a fake page, like the existing
harvest test's fake page (tests/cdp_validation.mjs lines 51
to 104, vm.createContext with a fake page).

### F11 (NOTE, confirmed no gap): AGREE

element_ref.validate_action_binding (lines 146 to 164) is
type-agnostic: it checks observation_id and scope only.
action_result.py only re-exports DOM_ASSERT_EXCEPTIONS
(line 33: DOM_ASSERT_EXCEPTIONS =
dom_asserts.DOM_ASSERT_EXCEPTIONS). The AssertSetTests chains
in tests/test_step5_p1p5.py contain no focus action (SEND chain
is [click, type, key Enter], lines 121 to 123; the exception
chain is scroll, hover, move, wait, drag), and they assert
exact required sets only for those chains, so the new ASSERTS
entry cannot change them. require_asserts has only two
production callers (code_exec.py line 936 and dom_act.py
line 748). No fourth file is missing from the spec section 5
edit list.

### F12 (NOTE, stands): AGREE

- Item 2 stands: a tree listing grep for c5-count returns
  zero matches in the whole todolist-push tree. The pre-send
  guard and delayed count still depend on the laptop file.
- Items 3 to 6 stand: no commit on main picks option A or B
  (the batch 13 assignment, commit e03e288, assigns the review
  and picks nothing); no focus tests exist yet; no live proof
  of landed code exists (cdp.mjs has no focus action); the
  laptop tree sync and relay-restart question are still
  unverified.
- Item 7 stands: the 80-element cap is cdp.mjs lines 83 to
  84, and all 5 reopen Chromium runs ran relaxed (routing
  reason "relaxed gate: truncated inventory (80 elements),
  send target covered", verified from the JSONs).
- Items 8, 9, 10 stand: the mouse stall is unsolved; the
  Brave decision is open; the shadow-root activeElement walk
  is a follow-up.

### F13 (NOTE): AGREE

The dry-run baseline (wall 30123.9 ms, Chromium elapsed
85.8 ms, completed 2) is cited to the reopen log section 3,
which is honest, but no run-0 JSON exists in the repo: a tree
listing of improvements/s2-flip-reopen-runs/ shows only
run-1..5.json plus the P9 PNGs. The baseline rests on log
prose only. One sentence in section 8 should say so.

## 3. Errors in the task 2 report

### C1 (MEDIUM): F2 note 1 is wrong, the run JSONs do name the PNG paths

What the task 2 report says (F2, second note): "the run JSONs
still carry p9 as null in every JSON, so the PNG paths come
from the audit repair-list filename convention, as the manifest
records; the spec should say that instead of implying the JSONs
name the PNGs."

What is true at HEAD 8c6553a, verified first-hand in all 15
run JSONs: p9 is a dict naming the PNG paths, not null. Examples:

- improvements/s2-flip-b1-runs/run-1.json, at 3167c76 and at
  8c6553a: p9.chromium.png =
  'improvements/s2-flip-b1-runs/p9-run1-chromium.png', ok True,
  wall_ms 3637.2.
- improvements/s2-flip-reopen-runs/run-1.json: p9.brave.png =
  'improvements/s2-flip-reopen-runs/p9-run1-brave.png' and
  p9.chromium.png =
  'improvements/s2-flip-reopen-runs/p9-run1-chromium.png'.
- improvements/s2-flip-runs/run-1.json: p9.brave.png and
  p9.chromium.png both present with the same path convention.

The p9 field was populated in the original log commits
(4bd6292 for the (b1) JSONs, 1a3356d for the reopen JSONs), so
it was already a dict at the task 2 review HEAD 3167c76, not
something that changed afterwards. The manifest's auditor note
("the run JSONs carry p9 as null, so they do not name the PNG
paths") carries the same error; the task 2 report trusted the
manifest prose on this point instead of re-checking the JSONs
it had already read for its numbers. The manifest paths match
the JSON paths exactly for all 25 rows, which my section-aware
verification in section 2 of this report confirms.

Fix: do not apply the F2 note 1 recommendation to the spec.
The spec should not be told to say the PNG paths come from the
repair-list convention, because the JSONs do name them. The fix
pass should instead correct the manifest's auditor note, or
leave the manifest alone and simply not repeat the claim. The
main F2 finding is unaffected: all 25 PNGs are in the repo and
verified.

## 4. Gaps and observations

### C2 (LOW): F5 misses the second facet of the hover_click drift

The task 2 report records the drift in the allowed sets only.
The same drift sits in the element-action check lists:
cdp.mjs line 435 lists click, confirm_click, hover_click,
fill, set_value, assert; code_exec.py line 218 lists the same
six; but cu.py line 1341 lists click, confirm_click, fill,
set_value, assert, with no hover_click. So cu.py drifts from
the other two mirrors in two places (line 1299 and line 1341),
not one. The spec section 5 edit list is still complete: it
names line 1341 for focus. The fix pass should record both
facets when it acknowledges the drift.

### C3 (LOW): F10 item (f) as specified cannot pass while the drift is unfixed

A test asserting the three browser whitelists (cdp.mjs line
434, code_exec.py line 217, cu.py line 1299) contain the same
set fails today on hover_click, because cu.py line 1299 lacks
it. The task 2 report says in F5 that the drift is "a known
pre-existing drift, not something this landing fixes", while
F10 item (f) says the test "locks in the F5 fix and catches
future drift". Those two directions conflict until the fix pass
picks one: either add hover_click to cu.py (both line 1299 and
line 1341, see C2) as part of the landing, or scope the
F10 item (f) test to the landed set plus the recorded drift.
The fix pass must state which it chose. This does not change
the AMEND verdict.

### C4 (NOTE): F4 derivation premise is unstated, ranges still stand

The 0 to 10 ms assert component in the corrected F4
derivation is the incremental bubble-assert latency over the
value assert, which passes on its first poll because set_value
already verified the value internally (cdp.mjs lines 517 to
518, repeated at 528). The task 2 report does not state that
premise, so a reader could take the 0 to 10 ms as an additive
assert cost on top of a baseline that already contains an
assert poll. Either way the corrected ranges still bracket the
true expectation: without the component the dry run is about
90 to 91 ms and the live re-run about 110 to 135 ms; with it
they are about 90 to 100 ms and about 110 to 145 ms, as the
task 2 report states. No change to the corrected criteria is
needed. One sentence stating the premise is enough.

## 5. Recommendation for the fix pass

Apply F1 and F2 first, as the task 2 report says, but do not
apply the F2 note 1 recommendation: the run JSONs do name the
PNG paths (C1). Then fix F3 (reword the section 5 rule and add
the F10 item (e) test) and F4 (rewrite the section 8 elapsed
paragraph and the section 11 criterion, add the live elapsed
expectation of about 110 to 145 ms to section 9 step 6, and
state the C4 premise in one sentence). Then apply F5, F6, F7,
F8, F9, and F10, recording both facets of the hover_click
drift (C2) and resolving the F10 item (f) scoping question
(C3) explicitly. The design decision (option A) needs no
rework, and the bulk of the spec verified clean, so the fix
pass is small. After the fix pass, the spec can land without a
second full review, provided the fix pass re-checks F3 and F4
against the code. The AMEND verdict stands.

## 6. Verification log

Times are Asia/Ho_Chi_Minh, 22 November 2026. Work ran about
14:35 to 14:45 +07. No live runs, no browser work, no shared
code changed. Read-only git show and git grep against
origin/todolist-push, plus local scripts over the extracted
JSONs.

- 14:35: fetched origin/main and origin/todolist-push. Local
  main at f5e36e7 (the task 2 report). todolist-push at
  8c6553a, matching the brief note.
- 14:36: read the task 2 report and the spec (571 lines) in
  full. Extracted scripts/cdp.mjs, scripts/code_exec.py,
  scripts/cu.py, scripts/dom_asserts.py, scripts/dom_act.py,
  scripts/s2_flip_live.py, scripts/element_ref.py,
  tests/test_s2_flip_wiring.py, tests/cdp_validation.mjs,
  tests/test_step5_p1p5.py, scripts/action_result.py,
  improvements/s2-flip-b1-runs/c5-focusenter.mjs, and
  improvements/s2-flip-p9-manifest.md from origin/todolist-push
  to /tmp for read-only checking.
- 14:37: verified F1 (helper 2478 bytes, 42 lines, sha256
  match) and F2 (25 of 25 PNGs verified against the manifest,
  section-aware, sha256 plus byte size plus PNG magic).
- 14:38: found C1: all 15 run JSONs carry p9 as a dict naming
  the PNG paths, at both 3167c76 and 8c6553a, populated since
  commits 4bd6292 and 1a3356d. The task 2 report F2 note 1
  claim of p9 null is wrong.
- 14:39 to 14:42: recomputed all section 2.2 numbers from the
  15 run JSONs plus 4 aborted JSONs with a script. All match
  the task 2 report: (b1) median wall 18839.7 ms, program
  elapsed 91.575 to 106.622 ms, helper enter.ms 17 to 23 ms,
  completed 2, pre-send count 0, delayed count 1, model calls
  0, all 5 runs; aborted walls 12365.3, 14372.5, 12652.1,
  13734.2 ms; reopen median wall 28560.9 ms, Chromium program
  elapsed 99.412 to 113.005 ms, helper enter.ms 21 to 25 ms,
  V12 attempts 1 in all 10 sends, all 5 Chromium runs relaxed
  with 80 elements truncated, phase split residuals 2708.9,
  2827.3, 2743.1, 2750.1, 2914.5 ms, median 2750.1 ms; flip
  Chromium dom_act "ok False completed 0 ms 5003" in runs 1,
  3, 4, 5 and "ms 5002" in run 2, with "CDP timeout:
  Input.dispatchMouseEvent" in the program log of runs 2 to 5.
- 14:42 to 14:44: verified every line citation in section 2.1
  with grep and direct reads. All exact except the two
  one-line slips in F9. Verified F3, F5, F6, F7, F8, F10, F11,
  F12, F13 first-hand. Found C2 (cu.py line 1341 also lacks
  hover_click) and C3 (F10 item (f) cannot pass as specified
  while the drift stands).
- 14:45: wrote this report to
  docs/batch13-council1-task2-20261122.md, committed only that
  file, pushed to origin/main.

## 7. What this review did not do

- No shared code was changed. No edits to coord/clone1.md or
  coord/clone2.md. The untracked 0-byte test-w.txt was left
  alone.
- No live runs and no browser work. The corrected elapsed
  ranges in F4 are estimates from the existing measurements,
  stated as ranges with their components, not as new
  measurements.
- No redteam or fix pass. Those follow under the batch 13
  brief.
