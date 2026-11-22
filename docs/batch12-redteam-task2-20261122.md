# Batch 12 redteam task 2: (b1) landing spec review

Status: independent redteam. The spec under review is
docs/batch12-task2-b1-landing-spec-20261122.md, commit 55405a5
on main, 491 lines. Base checked: branch todolist-push, HEAD
4305dcb, read-only. Every number below was recomputed from the
run JSONs on todolist-push, every code citation was checked
against the actual file at that HEAD, and the wiring tests
were run first-hand in a throwaway worktree at 4305dcb (12
tests, all OK, 0.050s). Line numbers starting with "spec line"
refer to the spec file; all other line numbers refer to
todolist-push files.

## Verdict: BROKEN

1 breaking finding, 11 minor findings. The breaking finding
is a design gap in the proposed P5 rule: as written, the
send-requires-focus rule would reject the working fill
program, breaking the Brave half the spec says must keep
working. The spec must scope that rule before anyone lands
from it. The minor findings are wrong line or section
citations and one wrong error-string attribution; none of
them changes a measured number, but they would mislead the
implementer on exact lines and strings.

## Breaking findings

### B1. The send-requires-focus rule as specified rejects the fill program (spec line 221)

Spec section 5 says: "Add a send-requires-focus rule to
require_asserts: a send key (Enter after set_value, per
_is_send_key, lines 100 to 113) with no preceding focus
action in the same batch raises DomAssertError."

What is wrong: the rule sentence is unscoped. It says "a
send key ... with no preceding focus action", and the
authority it cites, _is_send_key (scripts/dom_asserts.py:96
to 114), defines a send key as Enter appearing after a
type, fill, or set_value action in the same batch. The
parenthetical "(Enter after set_value...)" hints at a
set_value-only scope, but the cited definition covers fill
too, and the rule sentence does not state the scope.

Evidence: the existing fill program is [fill, key Enter,
assert] (scripts/s2_flip_live.py, build_program, lines 107
to 127). It contains a send key and no focus action. The
existing test test_program_actions_satisfy_p5_requires
(tests/test_s2_flip_wiring.py:176 to 187) asserts that
exact program PASSES require_asserts. Under the rule as
written, that program raises DomAssertError, so that test
fails after the rule lands.

Why it matters: fill focuses internally. The fill branch
checks document.activeElement === e after the click
(scripts/cdp.mjs:536) and throws 'field is not editable or
did not gain focus' (scripts/cdp.mjs:537). Fill satisfies
focus by construction and must be exempt, or the rule must
apply only when the batch's value action is set_value. The
spec never states either. Implemented literally, the rule
breaks the Brave fill path, which the spec elsewhere says
must keep working ("Brave keeps fill", section 5; "Brave
unchanged", section 8), and it falsifies section 8's claim
that "The full wiring file still passes 12 of 12 after the
swap".

Required fix: state the scope in section 5, in one
sentence, for example: the rule applies only to a send key
whose preceding value action in the same batch is
set_value; a fill action satisfies the focus requirement by
construction (cdp.mjs:536 to 537). Add a test that [fill,
key Enter, assert] still passes require_asserts after the
rule lands, next to the proposed test that [set_value, key
Enter, assert] without focus raises.

## Minor findings

### M1. Wrong line citations for V12 and P9 (spec lines 309, 312)

Spec section 7 says V12 is at "scripts/s2_flip_live.py:390
to 415" and P9 is at "scripts/s2_flip_live.py:417 to 435".

Correct values: v12_check is scripts/s2_flip_live.py:316
to 338. p9_capture is scripts/s2_flip_live.py:340 to 356.
Lines 390 to 415 are the observe and broker call plus the
relaxed-gate comment; lines 417 to 435 are the observe span
append and the relaxed-gate routing block. The claims
themselves are true (V12 polls up to V12_TIMEOUT_MS, 10000
ms, for a [data-message-item]; P9 captures after the scored
wall), only the citations point at the wrong code.

### M2. Wrong line citation for send_browser CB-1 (spec line 245)

Spec section 5 says: "Update send_browser CB-1 for the
set_value variant (lines 615 to 625)".

Correct value: the CB-1 block is scripts/s2_flip_live.py:568
to 588 (set_value branch 568 to 578, fill branch 579 to
585, verified set at 588). Lines 615 to 625 are the tail of
seed_scratch, close_scratch, and `def run`. The spec's
description of the old mapping is correct (input_sent =
focus_enter ok at line 574, target_received = completed >= 1
at line 575), and the proposed new mapping (input_sent =
completed >= 3, target_received = completed >= 1) is
coherent for the 4-action program. Only the citation is
wrong.

### M3. Wrong section citation for the residual (spec line 324)

Spec section 7 says the 2750.1 ms median residual is in
"improvements/worker-click5-s2-reopen-log.md, section 4".

Correct value: the reopen log has no section 4. Its
sections are 0, 1, 2, 3, 5, 6, 7, 8. The residual figure
sits in the run table under section 3 (lines 180 to 219).
The number itself is correct: residuals from the 5 reopen
run JSONs are 2708.9, 2827.3, 2743.1, 2750.1, 2914.5 ms,
median 2750.1 ms.

### M4. Wrong error-string attribution (spec line 171)

Spec section 4, item 4 says: "On failure throw 'field did
not gain focus', the same wording fill uses
(scripts/cdp.mjs:537)."

Correct value: fill's wording at scripts/cdp.mjs:537 is
'field is not editable or did not gain focus'. The string
'field did not gain focus' appears nowhere in cdp.mjs. The
proposed string is fine as a new wording, but it is not
fill's wording. Either correct the attribution or adopt
fill's exact string.

### M5. dom_asserts.py ASSERTS entry citations are off (spec lines 129, 219, 226)

Spec says the click entry is "lines 42 to 45", the fill
entry is "lines 62 to 64", and the set_value entry is
"lines 65 to 68" (section 3 line 129 and section 5 lines
219, 226).

Correct values: click entry scripts/dom_asserts.py:48 to
50; fill entry 63 to 65; set_value entry 66 to 68. Lines 42
to 45 are the comment header above ASSERTS; line 62 is the
tail of the 'type' entry; line 65 is the tail of the 'fill'
entry. The entries exist and the spec's descriptions of
them are right; the numbers are off by 1 to 6 lines each.

### M6. set_value visibility citation points at a comment (spec line 178)

Spec section 4 says: "set_value already requires the field
to be visible and hit-testable (scripts/cdp.mjs:503 to
510)."

Correct value: the visibility and hit-test check is
scripts/cdp.mjs:501 to 502. Lines 503 to 510 are the "No
prefill early return" comment block. The claim is true;
the citation points at the wrong lines.

### M7. Incomplete enumeration of the unavailable-field checks (spec line 168)

Spec section 4, item 2 lists "disabled, readOnly,
aria-disabled, inert (scripts/cdp.mjs:476 to 478)".

Correct value: the set_value branch check at
scripts/cdp.mjs:478 is `e.disabled || e.matches(':disabled')
|| e.readOnly || e.getAttribute('aria-disabled') === 'true'
|| e.closest('[inert]')`, five conditions. The spec omits
the CSS :disabled pseudo-class, which covers
fieldset-disabled descendants. An implementer copying the
spec's list would drop that check. The line range 476 to
478 itself is acceptable (resolve at 476, type check at
477, availability check at 478).

### M8. The 5003 ms figure is misattributed to flip log section 6 (spec line 19)

Spec section 0 says: "(CDP timeout
Input.dispatchMouseEvent, 5003 ms, 0 of 5 sends;
improvements/worker-click4-s2-flip-log.md, section 6)."

Correct value: 5003 ms is the dom_act ms from the per-run
log lines in flip log section 5 (runs 1, 3, 4, 5 show "ms
5003"; run 2 shows "ms 5002", verified from
improvements/s2-flip-runs/run-1..5.json program log lines).
Section 6's table records program elapsed_ms 5102.6 to
5106.3 ms, not 5003. The stall fact and the 0 of 5 are
right; the section 6 attribution for the 5003 figure is
wrong, and the single figure glosses over run 2's 5002 ms.

### M9. s2_flip_live.py function ranges run past the function end (spec lines 232, 235, 251)

Spec cites build_program_set_value as "lines 129 to 167",
variant_for as "lines 189 to 205", and build_program's
trailing assert as "lines 107 to 127".

Correct values: build_program_set_value is lines 129 to
161 (lines 162 to 167 are blank lines plus message_for);
variant_for is lines 189 to 195; build_program starts at
line 89, so 107 to 127 is only its tail. Each range starts
at the right place and the functions exist there; the
ranges overstate the end by 6 to 10 lines. Low risk, fix
for precision.

### M10. P2 binding citation is truncated (spec line 122)

Spec section 3 cites "the P2 scope plus observation_id
binding (scripts/code_exec.py:206 to 280)".

Correct value: the binding loop is
scripts/code_exec.py:277 to 284. The cited range ends at
280, mid-statement (line 280 is
`element_ref.validate_action_binding(`). The check starts
inside the cited range but the range cuts it off. The
function _validate_dom_actions spans lines 205 to about
285.

### M11. Unsubstantiated cost equivalence in the option B rejection (spec line 149)

Spec section 3 says of option B: "The field would also
need its own preflight validation (focus must be a boolean,
default false) and its own P5 rule, which is the same total
work as option A spread across fewer files."

What is wrong: "the same total work" is asserted, not
shown. Option A, by the spec's own section 5, touches 4
files plus the validation mirror in 3 of them and adds a
new P5 rule; option B touches cdp.mjs plus a test plus a
P5 rule. No evidence is given that the totals are equal.
The coordinator's A-versus-B choice rests partly on this
claim, so it should be justified with a concrete count or
softened to a judgment. The other two reasons against B,
bundled effects with ambiguous CB-1 accounting, and no
focus-without-value, are sound and stand.

## What verified clean

Numbers, recomputed first-hand from the run JSONs on
todolist-push:

- (b1) Chromium-only: 5 of 5 sent, walls 18477.4,
  18738.7, 18839.7, 19094.0, 20592.9 ms, median 18839.7
  ms. Program elapsed 91.575 to 106.622 ms. Focus Enter
  17 to 23 ms. Pre-send count 0, delayed count 1, model
  calls 0, all 5 runs. CB-1 all three True, completed 2,
  V12 attempt 1, all 5.
- S2 reopen, two browsers: 10 of 10 sent, walls 27799.1,
  28112.6, 28560.9, 28898.1, 29020.4 ms, median 28560.9
  ms. Chromium program elapsed 99.412 to 113.005 ms.
  Focus Enter 21 to 25 ms. Pre-send count 0, delayed
  count 1, model calls 0, all 5 runs. V12 attempt 1 in
  all 10 sends. All 5 reopen Chromium runs ran the relaxed
  routing gate (truncated inventory, 80 elements, composer
  present), per the run JSON routing reasons.
- Reopen dry run 0: PASS, wall 30123.9 ms, Chromium
  elapsed 85.8 ms, completed 2, per reopen log section 3.
- Residuals: reopen phase-split residuals median 2750.1
  ms, as in M3.
- P9 PASS 10 of 10 in the reopen, per reopen log section
  5 (all 10 screenshots reviewed before scoring).

Code and log citations that checked out exactly: base
HEAD 4305dcb; reopen log commit 1a3356d and input-fix log
commit 4bd6292; cdp.mjs lines 83 (max_elements 1..80),
157 to 167 (pageState), 250 to 251 (shadow-root walk),
292 to 313 (click, mouseMoved plus mousePressed plus
mouseReleased), 390 to 412 (key, text '\r' for Enter at
line 410), 434 (whitelist), 435 to 437 (element-action
list), 467 (stale-snapshot check), 473 to 533 (set_value),
534 to 541 (fill), 536 (activeElement check), 546 to 547
(completed); code_exec.py lines 217 (allowed set), 218
(element_actions), 922 to 940 (P5 gate); cu.py lines 1299
(browser allowed set) and 1341 (browser element-action
check); dom_asserts.py lines 26 to 29 (type_check doc),
100 to 113 (inside _is_send_key, 96 to 114), the
trailing-assert rule at 198 to 203 and 215 to 216, and
the fail-closed unknown-action rule at 207 to 211;
s2_flip_live.py lines 76 (LAPTOP_FOCUSENTER), 77
(LAPTOP_COUNT), 478 to 495 (count_check), 497 to 519
(focus_enter), 539 to 543 (already-sent guard), 691 to
704 (delayed count); the no-e.focus() claim (grep over
cdp.mjs returns nothing); the T1 to T4 probe results and
the D-B1 2 ms result (input-fix log sections 7.1, 7.2,
7.3); the focusenter helper semantics and the count
helper (input-fix log section 7.3); the reopen log
section 0 open item on durable landing; the reopen log
section 6 EXPAND recommendation and its caveats 1 to 4;
the wiring file has exactly 12 test methods, including
test_set_value_program_carries_p2_stamps_and_passes_p5
and test_chromium_set_value_splits_variants_per_browser.

Tests run first-hand: in a throwaway worktree at
todolist-push HEAD 4305dcb, `python3 -m unittest
tests.test_s2_flip_wiring -v` ran 12 tests, all OK, in
0.050s. `node tests/cdp_validation.mjs` passed (key
rejects modifiers only, adapter preflight, harvest).
Worktree removed after the run.

Design checks that hold: the landed 4-action program
[set_value, focus, key Enter, assert] passes
require_asserts with available focus_check True,
type_check True, sent_bubble False, because the trailing
assert satisfies sent_bubble; the proposed CB-1 mapping
(completed >= 3 for input_sent, completed >= 1 for
target_received) matches the 4-action shape; the value
read-back lives inside set_value, so no value assert
after the Enter is correct (the composer is empty after
the send); the focus action carrying the same
activeElement proof as fill, without the mouse, is the
right contract.

## Required fixes before landing from this spec

1. Fix B1: scope the send-requires-focus rule to
   set_value programs (or exempt fill by construction)
   and add the fill-still-passes test. Until this is
   fixed, the spec must not be used as the landing
   instruction.
2. Fix the wrong citations M1, M2, M3, M5, M6, M8, M9,
   M10 to the correct lines and sections named above.
3. Fix the error-string attribution M4 and the
   incomplete check list M7.
4. Justify or soften the cost claim M11.

After those fixes, the spec's numbers, design, and test
plan are sound, and the landing can proceed on option A.
