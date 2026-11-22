# Batch 13 council 3: review of the batch 13 task 2 (b1) spec review

## 0. Verdict: AGREE with AMEND, with one material correction

The task 2 report (docs/batch13-task2-b1-spec-review-20261122.md,
commit f5e36e7, verdict AMEND) is sound in its main findings and its
verdict stands. I re-read every cited line first-hand, recomputed
every number from the run JSONs with scripts, and re-verified the
25 PNGs against the manifest. All four HIGH findings (F1, F2, F3,
F4) hold, all medium and low findings hold, and the section 2.1
line citations and section 2.2 numbers check out except for the
two one-line slips the review itself already lists in F9.

One material correction, C1, changes what the fix pass must do.
The review's F2 first note says the run JSONs carry p9 as null in
every JSON. That is false. Every run JSON names its PNG path in
p9, and p9 was already non-null at the spec base. The fix pass
must NOT write the sentence the review prescribes there. The main
F2 finding (all 25 PNGs are now in the repo) is unaffected.

Two minor corrections, C2 and C3, tighten the review's proposed
F3 wording and F4 derivation. Two further gaps, C6 and C7, were
found in the review's F5 and F10 item (f): the hover_click drift
has a second facet the review misses, and the F10 item (f)
whitelist-sync test cannot pass while that drift is unfixed. I
verified C6 and C7 first-hand from the code after reading
council 1's report (912d631), which landed on main during this
review and notes the same two points; the verification below is
my own. A cosmetic log-ordering slip, C4, and a scope note, C5,
complete the list. None of them changes the AMEND verdict. No
shared code was changed by this council review. Report only.

## 1. Scope and method

- Report reviewed: docs/batch13-task2-b1-spec-review-20261122.md,
  607 lines, commit f5e36e7 on origin/main.
- Spec under review: docs/batch12-task2-b1-landing-spec-20261122.md,
  571 lines, commits 55405a5 and fix pass 20f3b99.
- Review HEAD: origin/todolist-push 8c6553a. The report was written
  against 3167c76 and states the diff to 8c6553a is empty for the
  reviewed files. I verified that diff myself: empty, 0 lines.
  The batch 13 brief text names a6dfa3b as the branch HEAD at
  brief-writing time; I checked with ls-remote that the branch
  HEAD is 8c6553a, and a6dfa3b is an ancestor of 8c6553a, so the
  findings stated against 8c6553a stand.
- Code read first-hand, read-only, from origin/todolist-push at
  8c6553a with `git show` (the branch was never checked out and
  never modified): scripts/cdp.mjs (641 lines),
  scripts/code_exec.py (1297 lines), scripts/cu.py (3465 lines),
  scripts/dom_asserts.py (227 lines), scripts/dom_act.py
  (866 lines), scripts/s2_flip_live.py (812 lines),
  scripts/element_ref.py (293 lines), scripts/action_result.py
  (103 lines), tests/test_s2_flip_wiring.py (244 lines),
  tests/cdp_validation.mjs (133 lines),
  tests/test_step5_p1p5.py (561 lines), tests/test_dom_act.py
  (605 lines).
- Evidence read first-hand from the same HEAD:
  improvements/s2-flip-b1-runs/run-1..5.json and
  run-2..5-aborted.json, improvements/s2-flip-reopen-runs/
  run-1..5.json, improvements/s2-flip-runs/run-1..5.json,
  improvements/s2-flip-b1-runs/c5-focusenter.mjs,
  improvements/s2-flip-p9-manifest.md,
  improvements/worker-click5-input-fix-log.md,
  improvements/worker-click5-s2-reopen-log.md,
  improvements/worker-click4-s2-flip-log.md.
- Every number in this report was recomputed from the run JSONs
  with a script, not copied from the report or the logs. Every
  line citation was checked with grep or direct read at HEAD
  8c6553a.
- Rules kept: no personal information anywhere, no long dashes,
  no ydotool, real numbers only, all verified first-hand.

## 2. Verdicts per finding

### F1 (HIGH, stale): AGREE

The focusenter helper is in the repo at
improvements/s2-flip-b1-runs/c5-focusenter.mjs, committed in
3ef8f55. I read it first-hand at 8c6553a: 2478 bytes, 42 lines,
sha256
94ee467ed3067e044491ad19153c24b73d574a8106a5367db454c0e47e1a695f,
matching the manifest row and the review exactly. Its semantics
match the input-fix log section 7.3 description: Runtime.evaluate
focus on textarea[aria-label="Message"], assert it is
document.activeElement, then Input.dispatchKeyEvent keyDown plus
keyUp Enter, zero mouse events, returns {ok, focus, enter}.
Spec section 10 item 1 and section 1 item 2 ("a laptop-only
helper") are stale as the review says. The reopen log section 8
line listing laptop helpers "not in the repo" is stale for
focusenter in the same way.

### F2 (HIGH, stale): AGREE on the finding, DISAGREE on note 1

Main finding: all 25 P9 PNGs are on todolist-push, committed in
3ef8f55 alongside improvements/s2-flip-p9-manifest.md. I verified
all 25 independently against the manifest with a section-aware
script (sha256, byte size, PNG magic): 25 of 25 match, zero
mismatches. Byte totals per directory are 1,210,605 for the 5
(b1) PNGs, 2,354,937 for the 10 reopen PNGs, and 2,740,488 for
the 10 original flip PNGs, 6,306,030 total, exactly as the
review states. Spec section 10 item 11 is stale as the review
says.

Note 1 is wrong, see C1. Note 2 (the 5 original flip Chromium
PNGs show no test bubble, agreeing with outcome
failed-unverified) is taken from the manifest's "What the frame
shows" column; neither the review nor this council viewed the
PNG pixels, see C5.

### F3 (HIGH, design): AGREE, with a wording correction, see C2

In dom_act.py focus_type (lines 664 to 712) the chain built at
lines 708 to 712 is [click, type, key Enter], and the docstring
says "Click an input, type, and verify". The click establishes
focus; the type step types into the field the click already
focused and performs no focus of its own. In cdp.mjs there is
no `type` action at all: the whitelist at line 434 is
['click','confirm_click','hover_click','fill','set_value','key',
'scroll','wait','assert']. The spec's section 5 list of
focus-establishing actions wrongly includes `type`, so a batch
[type, key Enter, assert] with no click would pass the spec's
rule yet fail silently the same way [set_value, key Enter]
does. No such batch exists today (focus_type always includes
the click), so the hole is latent, not live, as the review
says. The review's corrected rule is right in substance; its
exempt list omits double_click, see C2.

### F4 (HIGH, acceptance criterion): AGREE

Both errors confirmed first-hand.

(a) The 17 to 25 ms figure is the Enter time, not the focus
time. In the committed helper the timer t0 wraps only the two
dispatchKeyEvent calls, and out.enter.ms is measured around
those calls only. The run JSONs report enter.ms 17 to 23 ms
for the (b1) runs and 21 to 25 ms for the reopen runs. The
focus evaluate was never timed separately.

(b) The 17 to 25 ms figures are live measurements, while the
dry run runs on scratch tabs, where Enter measured 2 ms
(input-fix log section 7.4: "focus_enter ok True (focused
TEXTAREA, Enter 2ms)"; the D-B1 probe in section 7.1 also
measured 2 ms, keyDown plus keyUp Shift).

Corrected ranges check arithmetically. Dry run: baseline
85.8 ms (reopen log section 3) plus focus about 2 to 3 ms
(the flip log section 5 run 1 records each V12 evaluate at
2 to 3 ms) plus Enter on scratch about 2 ms plus assert
polling about 0 to 10 ms (assertAction polls every 10 ms,
cdp.mjs:415 to 427) gives 89.8 to 100.8 ms, so "about 90 to
100 ms" is fair. Live re-runs: (b1) program elapsed 91.575
to 106.622 ms plus focus about 2 to 3 ms plus live Enter 17
to 25 ms plus assert polling about 0 to 10 ms gives 110.6 to
144.6 ms, so "about 110 to 145 ms" is fair. One precision
note, see C3. The spec section 8 and section 11 figures of
105 to 115 ms are wrong as the review says.

### F5 (MEDIUM, hover_click drift): AGREE

A grep for hover_click across cu.py at 8c6553a returns zero
matches. The cu.py browser allowed set at line 1299 is
{'click','confirm_click','fill','set_value','key','scroll',
'wait','assert'}, with no hover_click. hover_click is present
in the cdp.mjs whitelist (line 434) and in the code_exec.py
allowed set (line 217). The three-way mirror already drifts
today on one action type, as the review says. The drift is
confined to the cu.py whitelist: dom_asserts.py:57 does carry
a hover_click ASSERTS entry (focus_check), so the assert
table is not part of the drift. But the review records only
one facet of the drift: the same gap sits in the
element-action check lists too, see C6.

### F6 (MEDIUM, design additions mislabeled): AGREE

Read first-hand from the committed helper: if the textarea
is missing it returns {focused: false, error: 'no-textarea'};
on focus failure it throws 'composer did not gain focus'. It
performs no unavailable-field checks (no disabled,
:disabled, readOnly, aria-disabled, or inert check). Spec
section 4 step 2 (the unavailable-field checks) is borrowed
from the set_value branch (cdp.mjs:478), and step 4 (error
wording 'field is not editable or did not gain focus') is
borrowed from fill (cdp.mjs:537). Both borrowings are sound
design choices, and step 5 ("Return ok") is a deliberate
narrowing of the helper's {ok, focus, enter} shape, but none
of the three is a replication of the helper, as the review
says.

### F7 (MEDIUM, Enter params differ): AGREE

Verified first-hand from the committed helper and from
cdp.mjs lines 390 to 412. (a) The helper sends code: 'Enter'
on both keyDown and keyUp. The landed key() never sends a
`code` field for any key; it sends key, modifiers,
windowsVirtualKeyCode, and nativeVirtualKeyCode only.
(b) The helper sends text: '\r' on keyDown only; its keyUp
carries no text. The landed key() builds one params object,
including text '\r' for Enter, and spreads the same object
into both keyDown and keyUp. Both differences are probably
harmless, as the review says, but the spec should record
them and decide whether key() needs a `code` field for
Enter, not change key() silently inside the landing.

### F8 (LOW, branch position): AGREE

The dispatch chain in cdp.mjs is an else-if over distinct
action types (lines 471 to 545); the for loop iterates
request.actions in order, so branch position is irrelevant
to execution order. "It must sit between set_value and key
in the chain" is misleading as a requirement and should be
softened to a style suggestion, as the review says.

### F9 (LOW, citation slips): AGREE

Both slips confirmed. The _api_dom_act require_asserts call
in code_exec.py spans lines 936 to 939; it closes on line
939 with 'sent_bubble': False, not 936 to 938 as the spec
says. The click function in cdp.mjs spans lines 292 to 314;
it closes on line 314, not 313, and the three
dispatchMouseEvent calls are on lines 311 to 313, inside
the spec's cited range.

### F10 (MEDIUM, missing tests): AGREE on all items (a) to (g)

(a) The spec section 8 lists a focus test for the
unavailable-field error only, not for the focus-failure
error wording from section 4 step 4. (b) The listed focus
test resolves a ref only; no selector-resolution focus test
is listed. (c) test_program_without_trailing_assert_would_
fail_p5 (tests/test_s2_flip_wiring.py:189) covers the fill
shape only, not the landed [set_value, focus, key Enter]
shape. (d) The spec's failing-first anchor covers only the
cdp.mjs rejection ('unsupported action'); no anchor covers
the dom_asserts change (the landed program failing
require_asserts before the focus entry lands). (e) Follows
F3; the corrected-rule tests are missing. (f) The whitelist
drift in F5 exists, so a whitelist-sync test is missing.
(g) tests/cdp_validation.mjs line 6 slices the source
between 'async function key(' and 'async function
assertAction('; the focus branch lives inline in the
handle() dispatch loop, not in a standalone function, so
that slicing pattern does not apply to focus, and the focus
unit tests need the whole-adapter vm run with a fake page,
as the review says. One caveat on item (f): the
whitelist-sync test as specified cannot pass while the F5
drift is unfixed, see C7.

### F11 (NOTE, file list complete): AGREE

element_ref.validate_action_binding (lines 146 to 164) is
type-agnostic: it checks observation_id and scope only.
action_result.py line 33 only re-exports
DOM_ASSERT_EXCEPTIONS. The AssertSetTests SEND chain in
tests/test_step5_p1p5.py (lines 121 to 123) is [click, type,
key Enter] and contains no focus action, so the new ASSERTS
entry cannot change their exact required-set assertions.
No fourth file is missing from the spec section 5 edit list.

### F12 (NOTE, items 2 to 10 stand): AGREE

Item 2 stands: /tmp/c5-count.mjs has zero matches anywhere
on todolist-push at 8c6553a. Items 3 to 6 stand: no commit on
origin/main and no text in coord/clone1.md picks option A or
B; no focus-action tests exist (test_dom_act.py tests
focus_check closures in the desktop flow, not a cdp `focus`
action); the cdp.mjs whitelist at line 434 has no `focus`
action, so no live proof of landed code exists; nothing in
the repo resolves the laptop tree sync or relay-restart
question. Item 7 stands: the 80-element cap is cdp.mjs:83
to 84, and all 5 reopen Chromium runs ran relaxed
(routing_relaxed True, observe truncated True, 80 elements,
verified from the JSONs). Items 8, 9, 10 stand: the mouse
stall is unsolved, the Brave decision is open, and the
shadow-root activeElement walk is a follow-up.

### F13 (NOTE, dry-run baseline is log-only): AGREE

No run-0 JSON exists in improvements/s2-flip-reopen-runs/
(or anywhere in the improvements tree): a tree listing
shows only run-1..5.json plus the P9 PNGs. The section 8
baseline (wall 30123.9 ms, Chromium elapsed 85.8 ms,
completed 2) rests on the reopen log section 3 prose only;
I verified those three numbers from the log text itself.
The landing team cannot recompute the baseline from a JSON.

## 3. Section 2 spot-checks: all verified

Section 2.1 line citations: I re-checked the full list.
All exact except the two one-line slips the review already
lists in F9. Samples verified first-hand: cdp.mjs:83 to 84
(max_elements 1..80), 157 to 167 (pageState), 250 to 251
(shadow-root activeElement walk), 390 to 412 (key, text
'\r' for Enter on line 410), 434 (whitelist), 435 to 437
(element-action list), 467 to 470 (stale-snapshot check),
473 to 533 (set_value), 478 ('field unavailable'), 501 to
502 (visible and hit-testable), 517 to 518 and 528
(read-back), 534 to 541 (fill, activeElement check line 536,
error wording line 537), 546 (completed increment).
cdp.mjs contains no e.focus() call; the only occurrences
of "focus" are a comment (line 183), harvest `focused:`
fields (lines 251, 261), and the fill error string (line
537). code_exec.py:217 and 218 (allowed and element_actions),
277 to 284 (P2 binding check), 922 to 940 (P5 gate).
cu.py:1299 (browser allowed set) and 1341 (browser
element-action check). dom_asserts.py:26 to 29 (fill and
set_value map to type_check), 48 to 50 (click entry), 63 to
65 (fill entry), 66 to 68 (set_value entry), 96 to 114
(_is_send_key covers Enter after type, fill, or set_value).
require_asserts fails closed on unknown action types and
has the trailing-assert rule; it has exactly two production
callers, code_exec.py:936 and dom_act.py:748 (verified by
grep across scripts/ and tests/). dom_act.py:708 to 712
(focus_type chain) and 748 (gate). s2_flip_live.py:76, 77,
84, 89 to 126, 117 to 121 (trailing bubble assert,
timeout_ms 3000), 129 to 161, 189 to 195, 316 to 338
(V12_TIMEOUT_MS 10000), 340 to 356, 478 to 495, 497 to 519,
539 to 543, 568 to 588 (set_value branch 568 to 578, fill
branch 579 to 585, verified set at 588), 691 to 704 (10
second sleep, recount), 780 to 795. The old CB-1 mapping
(helper result for input_sent, completed >= 1 for
target_received) matches the code at lines 574 to 575, and
the fill branch uses completed >= 2 at line 582.
tests/test_s2_flip_wiring.py has 12 test methods (verified
by count); the named tests exist as described, including
test_set_value_program_carries_p2_stamps_and_passes_p5
(2 scope stamps, 2 observation_id stamps, require_asserts
with available focus_check True, type_check True,
sent_bubble False) and test_program_actions_satisfy_p5_
requires ([fill, key Enter, assert] passes). The reopen log
section 1 line 115 reads "tests 12/12 pass (was 11/11)".

Section 2.2 numbers: I recomputed all of them from the 19
run JSONs (5 (b1), 4 aborted, 5 reopen, 5 flip). All match
the review exactly: (b1) median wall 18839.7 ms, program
elapsed 91.575 to 106.622 ms, enter.ms 17 to 23 ms,
pre-send count 0 in all 5, delayed count exactly 1 in all
5, model calls 0, completed 2 in all 5; aborted walls
12365.3, 14372.5, 12652.1, 13734.2 ms with outcome
aborted-routing; reopen median wall 28560.9 ms, Chromium
program elapsed 99.412 to 113.005 ms, enter.ms 21 to 25 ms,
V12 attempts 1 in all 10 sends, phase split residual
2708.9, 2827.3, 2743.1, 2750.1, 2914.5 ms with median
2750.1 ms; flip Chromium 0 of 5 sends, outcome
failed-unverified in all 5, dom_act log lines "dom_act ok
False completed 0 ms 5003" in runs 1, 3, 4, 5 and "ms 5002"
in run 2. The count_check helper appends no span (verified
in code; the only helper span append is focus-enter at
s2_flip_live.py:517). The D-B1 probe and the T1 to T4
scratch probe summaries match input-fix log sections 7.1
and 7.2 as read first-hand. The reopen dry run 0 baseline
matches reopen log section 3.

Section 2.3 design checks: all hold. Without a focus entry
in ASSERTS, require_asserts raises 'unknown action' before
any CDP request, so the landed 4-action program needs the
entry. Adding `focus` to code_exec.py allowed and
element_actions is sufficient: _validate_dom_actions then
applies the exactly-one ref-or-selector check and the
ref-in-snapshot check automatically. The CB-1 mapping
proposed in spec section 5 is sound: input_sent =
completed >= 3 means set_value, focus, and Enter all ran;
target_received = completed >= 1 means the set_value
read-back passed, since a failed set_value throws before
completed increments. Dropping the separate value assert is
safe: set_value verifies the value internally (cdp.mjs:517
to 518, repeated at 528) and throws 'value verification
failed' on mismatch. The section 3 option B accounting note
is correct. The section 9 step 3 test list is complete for
the touched modules: tests/test_step5_p1p5.py and
tests/test_dom_act.py both exist.

## 4. Errors, gaps, and missing issues in the review

### C1 (MATERIAL): F2 note 1, "p9 is null in every JSON", is false

What the review says (F2, first note for the fix pass):
"the run JSONs still carry p9 as null in every JSON, so the
PNG paths come from the audit repair-list filename
convention, as the manifest records; the spec should say
that instead of implying the JSONs name the PNGs."

What is true: every run JSON names its PNG path in p9. I
checked all 24 run JSONs in the three s2-flip-* run
directories (5 (b1), 4 aborted, 5 reopen, 5 flip, plus 5
a1): p9 is an object, never null, and its `png` field holds
the exact repo path, for example (b1) run-1.json carries
p9.chromium.png =
"improvements/s2-flip-b1-runs/p9-run1-chromium.png" and
reopen run-1.json carries p9.brave.png and
p9.chromium.png with the matching paths. I checked the same
field at the review HEAD 3167c76, at 8c6553a, and at the
spec base 4305dcb: p9 was already non-null at the spec
base, so it was never null at any point the review covers.
Commit 3ef8f55 touched zero run JSONs, so the evidence
commit did not add the field later. The manifest's auditor
note ("the run JSONs carry p9 as null, so they do not name
the PNG paths") is wrong on this point, and the review
repeated it without checking the JSONs.

Fix: the fix pass must NOT add the sentence the review
prescribes. The correct statement is the opposite: the run
JSONs name the PNG paths in p9, and the manifest paths
agree with them. The main F2 finding is unaffected.

### C2 (MINOR): the F3 corrected rule omits double_click

The review's corrected exempt list is "click,
confirm_click, hover_click, fill, or the new focus".
dom_asserts.py maps double_click to focus_check (lines 51
to 53), and cu.py includes double_click in the desktop
allowed set (line 1297: click, double_click, move, hover,
drag, scroll, type, key, wait). A desktop batch
[double_click, type, key Enter] focuses through the
double-click, passes require_asserts today, and would
wrongly raise under the review's wording because
double_click is not in its exempt list. No such batch
exists today, so this is latent, like the F3 hole itself.
Fix: add double_click to the exempt list, or scope the
rule explicitly to the CDP/browser vocabulary, where
double_click does not exist.

### C3 (MINOR): the F4 derivation omits the dropped value assert

The corrected dry-run and live ranges are built by adding
the focus cost, the Enter cost, and the bubble-assert
polling to the 2-action program elapsed. But the landed
4-action program drops the value assert that the 2-action
program carries (spec section 5: no separate value assert
is needed, the read-back lives inside set_value), and the
review never subtracts its cost. The value assert is an
assertAction poll that returns on its first evaluation when
the value matches, so the dropped cost is about 2 to 3 ms.
Subtracting it moves the dry-run range to about 87.8 to
100.3 ms and the live range to about 108.6 to 144.6 ms.
Both stated ranges ("about 90 to 100 ms" and "about 110
to 145 ms") still stand within their rounding. Note it in
the fix pass so the derivation is complete; no range
changes.

### C4 (COSMETIC): the review's section 6 verification log is out of order

The entries list 14:31 after 14:35, and the stated work
window "about 14:20 to 14:33" conflicts with a 14:35 entry
in the same log. Cosmetic only; it does not affect any
finding.

### C5 (SCOPE NOTE): the F2 PNG verification is hash-level, not pixel-level

The review verified the 25 PNGs against the manifest by
sha256, byte size, and PNG magic, and I did the same. That
proves the committed files are exactly the files the
manifest describes. It does not prove the manifest's "What
the frame shows" column (for example, that the 5 original
flip Chromium PNGs show no test bubble). Neither the review
nor this council viewed the PNG pixels. The manifest
records that every PNG was viewed in full before commit, so
the render claim rests on the manifest's viewing record
plus hash integrity. The fix pass and the landing log
should not overstate it as independent pixel verification.

### C6 (LOW): F5 misses the second facet of the hover_click drift

The review records the drift in the allowed sets only. The
same drift sits in the element-action check lists, verified
first-hand at 8c6553a: cdp.mjs line 435 lists click,
confirm_click, hover_click, fill, set_value, assert;
code_exec.py line 218 lists the same six; but cu.py line
1341 lists click, confirm_click, fill, set_value, assert,
with no hover_click. So cu.py drifts from the other two
mirrors in two places (line 1299 and line 1341), not one.
The spec section 5 edit list is still complete: it names
line 1341 for focus. The fix pass should record both
facets when it acknowledges the drift.

### C7 (LOW): F10 item (f) as specified cannot pass while the drift is unfixed

A test asserting the three browser whitelists (cdp.mjs line
434, code_exec.py line 217, cu.py line 1299) contain the
same set fails today on hover_click, because cu.py line
1299 lacks it, as verified in F5 above. The review says in
F5 that the drift is "a known pre-existing drift, not
something this landing fixes", while F10 item (f) says the
test "locks in the F5 fix and catches future drift". Those
two directions conflict until the fix pass picks one:
either add hover_click to cu.py (both line 1299 and line
1341, see C6) as part of the landing, or scope the F10
item (f) test to the landed set plus the recorded drift.
The fix pass must state which it chose. This does not
change the AMEND verdict.

### What the review did not miss

I checked for further gaps and found none of substance.
The review's method note (read-only `git show` and `git
grep` against origin/todolist-push, plus scripts over the
extracted JSONs) matches what it did. It did not re-run
the wiring tests itself; the "12 of 12 today" claim is
verified from the reopen log citation only. That is
consistent with its stated read-only method, not a gap.
The review's section 4 consolidated test additions (the
focus-after-Enter negative test, the same-ref builder test,
and recording the focus step's own timing in the live dry
run) are all sound and complete the F10 list.

## 5. Recommendation

Apply C1 first: strike the review's F2 note 1 and do not
let the fix pass write it into the spec; the JSONs name the
PNGs. Then apply the review's F1, F2 (main finding), F3,
and F4 fixes, with the C2 double_click addition to the F3
rule wording and the C3 value-assert note in the F4
derivation. Then apply F5, F6, F7, F8, F9, and F10, with
the C6 second drift facet recorded and the C7 choice made
explicit (either add hover_click to cu.py lines 1299 and
1341 as part of the landing, or scope the F10 item (f)
test to the landed set plus the recorded drift). After
the fix pass, the spec can land without a second full
review, provided the fix pass re-checks F3 and F4 against
the code and C1 against the JSONs.

## 6. Verification log

Times are Asia/Ho_Chi_Minh, 22 November 2026. Work ran
about 14:36 to 14:47 +07. No live runs, no browser work, no
shared code changed. Read-only `git show` and `git grep`
against origin/todolist-push, plus local scripts over the
extracted JSONs and PNG blobs.

- 14:36: fetched origin/main and origin/todolist-push.
  Local main at f5e36e7 (the task 2 report commit).
  todolist-push at 8c6553a, matching the brief note.
- 14:37: read the task 2 report (607 lines) and the spec
  (571 lines) in full. Extracted the 12 reviewed files from
  origin/todolist-push at 8c6553a to /tmp for read-only
  checking. Diff between 3167c76 and 8c6553a for those
  files is empty; diff between the spec base 4305dcb and
  3167c76 for those files is empty.
- 14:38: verified the focusenter helper (2478 bytes, 42
  lines, sha256 match) and the 25 PNGs against the manifest
  with a section-aware script: 25 of 25 match, zero
  mismatches, byte totals 1,210,605 plus 2,354,937 plus
  2,740,488, total 6,306,030.
- 14:39: recomputed all section 2.2 numbers from the 19
  run JSONs with a script. All match the review exactly.
  Found the p9 field is an object naming the PNG path in
  all 24 JSONs checked, and confirmed the same at 3167c76
  and at the spec base 4305dcb. This produced C1.
- 14:40 to 14:43: verified every line citation in section
  2.1 with grep and direct reads, and the section 2.3
  design checks (require_asserts callers, _validate_dom_
  actions, CB-1 mapping, AssertSetTests chains). All exact
  except the two F9 slips the review already lists. The
  double_click omission in the F3 wording produced C2; the
  dropped value assert produced C3.
- 14:44: checked the remaining F12 items (c5-count absent
  anywhere on the branch, no coordinator A/B pick in
  coord/clone1.md or the main log, no focus action in the
  cdp.mjs whitelist) and the F13 run-0 absence.
- 14:46: before committing, pulled origin/main and found
  council 1's report (912d631) had landed during this
  review. I read it and verified its C2 and C3 claims
  first-hand from the code (cu.py:1341 lacks hover_click
  while cdp.mjs:435 and code_exec.py:218 include it; the
  F10 item (f) test fails today on that drift), then added
  them as C6 and C7 above. Council 1 independently found
  the same C1 p9 error.
- 14:47: wrote this report to
  docs/batch13-council3-task2-20261122.md, committed only
  that file, pushed to origin/main.

## 7. What this council review did not do

- No shared code was changed. No edits to coord/clone1.md
  or coord/clone2.md. The untracked 0-byte test-w.txt was
  left alone.
- No live runs and no browser work. The corrected elapsed
  ranges in F4 were checked arithmetically against the
  existing measurements, not re-measured.
- No pixel-level review of the 25 P9 PNGs; verification was
  sha256, byte size, and PNG magic against the manifest,
  see C5.
- No redteam or fix pass. Those follow under the batch 13
  brief.
