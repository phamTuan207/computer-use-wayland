# Batch 12 council 1: review of task 2 (b1) landing spec

Reviewer: council 1. Reviewed file:
docs/batch12-task2-b1-landing-spec-20261122.md, commit 55405a5
on main, 491 lines. Base: branch todolist-push, tip 4305dcb
(verified: git log 4305dcb..origin/todolist-push is empty, so
4305dcb is the tip; the spec header base is correct).

Method: every number recomputed first-hand from the run JSONs on
todolist-push; every file-plus-line citation checked with grep -n
and sed against files extracted from origin/todolist-push into
/tmp/c12c1; the wiring tests run first-hand from a git-archive
copy of todolist-push scripts plus tests. Commands and outputs
are quoted under each claim. Read-only on todolist-push; no
change to it.

## Verdict: AMEND

The numbers are all correct. The design follows from the evidence.
But 10 file-plus-line citations are wrong, including three that
point at the wrong functions entirely (V12, P9, CB-1), which are
the exact functions the landing edits. The spec must be corrected
on those 10 points before the landing implementer uses it as a
map. The corrections are listed in part B, items R1 to R10.
Nothing in the numbers or the design is refuted.

## Part A. Numbers, all CONFIRMED

A1. (b1) Chromium-only, 5 of 5 sends verified, median wall
18839.7 ms. Command: python3 over /tmp/b1-1..5.json (git show
origin/todolist-push:improvements/s2-flip-b1-runs/run-1..5.json).
Output walls: 18477.4, 20592.9, 18839.7, 18738.7, 19094.0.
Sorted: 18477.4, 18738.7, 18839.7, 19094.0, 20592.9. Median
18839.7. Outcomes all sent, cb1 all three True, V12 found
attempt 1, program completed 2, api_calls 2, program_variant
set_value, dry_run False, model_calls 0, all 5 runs. CONFIRMED.

A2. (b1) program elapsed 91.575 to 106.622 ms. Same command.
Output elapsed_ms: 97.656, 106.622, 91.575, 102.811, 104.563.
Min 91.575, max 106.622. CONFIRMED.

A3. (b1) focus Enter 17 to 23 ms. Same command. Output
focus_enter enter ms: 23, 23, 17, 18, 20. Min 17, max 23.
CONFIRMED.

A4. (b1) pre-send count 0, delayed count 1, model calls 0,
all 5 runs. Same command. Output pre_count count 0 in all 5;
delayed_count chromium count 1 in all 5; model_calls 0 in
all 5. CONFIRMED.

A5. Reopen, 10 of 10 sends verified, 5 of 5 runs, median wall
28560.9 ms. Command: python3 over /tmp/ro-1..5.json (git show
origin/todolist-push:improvements/s2-flip-reopen-runs/run-1..5.json).
Output walls: 29020.4, 27799.1, 28112.6, 28898.1, 28560.9.
Sorted: 27799.1, 28112.6, 28560.9, 28898.1, 29020.4. Median
28560.9. Outcomes: 10 sent. CONFIRMED.

A6. Reopen Chromium program elapsed 99.412 to 113.005 ms.
Same command. Output: 113.005, 106.613, 107.077, 99.412,
104.164. Min 99.412, max 113.005. CONFIRMED.

A7. Reopen Chromium focus Enter 21 to 25 ms. Same command.
Output: 25, 21, 23, 25, 23. Min 21, max 25. CONFIRMED.

A8. Reopen pre-send count 0, delayed count 1, model calls 0,
all 5 runs. Same command. Output pre 0 in all 5; delayed
chromium count 1 in all 5; model_calls 0 in all 5. CONFIRMED.

A9. Reopen V12 found attempt 1 in all 10 sends, CB-1 all
three True in all 10. Same command. Output v12 attempts all
1; cb1 all True, 10 of 10. CONFIRMED.

A10. Reopen P9 ok True in all 10 captures. Same command.
Output p9 brave ok True and chromium ok True in all 5 runs.
The human PASS 10 of 10 is in the reopen log, section 5,
quoted in part B. CONFIRMED.

A11. Reopen median residual 2750.1 ms. Same command. Output
residuals: 2708.9, 2827.3, 2743.1, 2750.1, 2914.5. Sorted:
2708.9, 2743.1, 2750.1, 2827.3, 2914.5. Median 2750.1.
CONFIRMED. (The log section citation for this number is
wrong, see R9.)

A12. Reopen dry run 0 baseline: PASS, wall 30123.9 ms,
Chromium elapsed 85.8 ms, completed 2. Source: reopen log,
section 3, lines 150 to 167: "Result: PASS, 13:03:51-13:04:38
+07. Wall 30123.9ms ... Chromium: variant set_value, program
ok True, completed 2, elapsed 85.8ms, CB-1 all three True,
V12 found attempt 1, items 2, pre_count 0, delayed_count
chromium 1". CONFIRMED.

A13. Wiring tests 12 of 12 pass today. Command: git archive
origin/todolist-push scripts, plus tests/test_s2_flip_wiring.py,
then python3 -m unittest tests.test_s2_flip_wiring -v in
/tmp/c12c1/run. Output: "Ran 12 tests in 0.057s, OK". The
12 test methods counted with grep -c "def test_" = 12.
CONFIRMED. The reopen log section 1 also records "tests
12/12 pass (was 11/11)".

A14. Flip baseline: CDP timeout Input.dispatchMouseEvent,
5003 ms, Chromium 0 of 5 sends. Source: flip log, section 6,
5-run table lines 581 to 585, and run sections lines 139,
447, 487, 527, 544, 558. CONFIRMED.

A15. Reopen runs 13:05 to 13:09. Source: reopen log run
table, times 13:05:09 to 13:09:12. CONFIRMED.

A16. All 5 reopen Chromium runs ran relaxed (truncated
inventory, composer present). Command: same as A5. Output
routing_relaxed True in all 5 Chromium results. CONFIRMED.

## Part B. Citations

### CONFIRMED citations

- cdp.mjs:473 to 533, set_value branch with native-setter
  write, sanitized read-back, input and change events. sed
  473 to 545 shows the branch starts 473 and fill starts
  534. No e.focus() call anywhere in cdp.mjs: grep -n
  "e.focus()" returns nothing. CONFIRMED.
- cdp.mjs:157 to 167, pageState (ref or selector, stale
  snapshot, element missing). CONFIRMED.
- cdp.mjs:250 to 251, shadowRoot.activeElement walk in
  harvest. CONFIRMED.
- cdp.mjs:292 to 313, click dispatches mouseMoved,
  mousePressed, mouseReleased. CONFIRMED.
- cdp.mjs:390 to 412, key dispatches keyDown plus keyUp;
  line 410, grep -n "params.text='\\r'" returns 410.
  CONFIRMED.
- cdp.mjs:434, action whitelist, grep -n shows the
  whitelist line at 434. Line 435, element-action list.
  CONFIRMED.
- cdp.mjs:476 to 478, unavailable checks (disabled,
  readOnly, aria-disabled, inert). grep -n shows the
  'field unavailable' check at 478. CONFIRMED.
- cdp.mjs:534 to 541, fill starts with click(a) at 535,
  activeElement check at 536, error at 537, key at 541.
  CONFIRMED.
- cdp.mjs:516 to 522, value read-back. grep -n shows
  setter.call at 517 and the first read-back check at 518.
  CONFIRMED.
- code_exec.py:217, allowed set; line 218, element_actions.
  grep -n returns 217 and 218 exactly. CONFIRMED.
- code_exec.py:922 to 940, P5 gate. grep -n shows the P5
  comment at 922 and dom_asserts.require_asserts at 936 to
  940. CONFIRMED.
- code_exec.py:206 to 280, P2 binding. Function def at 205,
  binding call element_ref.validate_action_binding at 280.
  Range covers the function through the binding call.
  CONFIRMED, with the def one line above the cited start.
- cu.py:1299, browser allowed set. The browser branch of
  the allowed set is line 1299. Line 1341, ref and selector
  mutually exclusive check. Both grep verified. CONFIRMED.
- dom_asserts.py:26 to 29, type_check read-back docstring.
  grep -n returns line 26. CONFIRMED.
- s2_flip_live.py:76, LAPTOP_FOCUSENTER; line 77,
  LAPTOP_COUNT. grep -n returns 76 and 77. CONFIRMED.
- s2_flip_live.py:129 to 167, build_program_set_value, 2
  actions, no key, no focus. sed 129 to 167 shows the whole
  function. CONFIRMED.
- s2_flip_live.py:107 to 127, trailing bubble assert in
  build_program. The assert action with
  BUBBLE_ASSERT_SELECTOR, text, timeout_ms 3000 sits at
  115 to 121, inside 107 to 127. CONFIRMED.
- s2_flip_live.py:478 to 495, count_check; 497 to 519,
  focus_enter. Both def to return, sed verified. CONFIRMED.
- s2_flip_live.py:539 to 543, pre-send guard (count above 0
  aborts with already-sent). sed 539 to 543 shows exactly
  that block. CONFIRMED.
- s2_flip_live.py:691 to 704, delayed count (sleep 10 at
  692, recount per set_value browser). CONFIRMED.
- s2_flip_live.py:780 to 795, flags. --set-value at 787,
  --chromium-set-value at 790, both inside the range.
  CONFIRMED.
- Input-fix log section 7.1, D-B1 dispatchKeyEvent answers
  in 2 ms; section 7.2, T1 0 bubbles, T2 1 bubble, T3 1
  bubble, T4 still 1 bubble (lines 324 to 332); section
  7.3, focusenter and count helper behavior (lines 340 to
  366). All CONFIRMED against the log text.
- Reopen log section 0, open item that durable landing is
  missing (lines 62 to 65); section 1, wiring 12/12
  (lines 113 to 115); section 3, dry run 0 and run table;
  section 5, P9 PASS 10/10; section 6, EXPAND
  recommendation and caveat 2 (mouse stall unsolved, step 9
  first target). All CONFIRMED.
- Input-fix log commit 4bd6292 and reopen log commit
  1a3356d are both ancestors of todolist-push (git
  merge-base --is-ancestor returns true for both).
  CONFIRMED.

### REFUTED citations, with corrections

R1. Section 4 item 4: "throw 'field did not gain focus',
the same wording fill uses (scripts/cdp.mjs:537)".
REFUTED. grep -n "did not gain focus" in cdp.mjs returns
only line 537: "throw new Error('field is not editable or
did not gain focus')". The string 'field did not gain
focus' does not exist anywhere in cdp.mjs. Correction:
the focus action should throw 'field is not editable or
did not gain focus' if it mirrors fill, or use a new
distinct string and say so plainly, not claim it is
fill's wording.

R2. Section 5, dom_asserts.py: "mirrors the click entry
(lines 42 to 45)". REFUTED. The click entry is lines 48
to 50: line 48 "'click': {'assert': 'focus_check',
'mandatory': True,", lines 49 to 50 the check text.
Correction: lines 48 to 50.

R3. Section 5, dom_asserts.py: "the fill entry (lines 62
to 64)". REFUTED. The fill entry is lines 63 to 65: line
63 "'fill': {'assert': 'type_check', 'mandatory': True,",
lines 64 to 65 the check text. Correction: lines 63 to 65.

R4. Section 5, dom_asserts.py: "No change to the
set_value entry (lines 65 to 68)". REFUTED by one line.
The set_value entry is lines 66 to 68: line 66
"'set_value': {'assert': 'type_check', 'mandatory':
True,", lines 67 to 68 the check text. Line 65 is the
last line of the fill entry. Correction: lines 66 to 68.
Same drift in section 3, which cites dom_asserts.py:65
to 68 for the set_value entry.

R5. Section 5, s2_flip_live.py: "variant_for (lines 189
to 205)". REFUTED. variant_for is lines 189 to 196: def
at 189, body through "return 'fill'" at 196. Lines 197
to 205 are def note and def ssh. Correction: lines 189
to 196.

R6. Section 5, s2_flip_live.py: "Update send_browser
CB-1 for the set_value variant (lines 615 to 625)".
REFUTED. The set_value CB-1 mapping is lines 568 to 577:
line 568 "if variant == 'set_value':", line 572
out['focus_enter'], lines 573 to 577 the cb1 dict
(input_sent from focus_enter ok, target_received from
completed >= 1). Lines 615 to 625 are def seed_scratch
(601), def close_scratch (620), and def run (625).
Correction: lines 568 to 577. The old mapping substance
the spec describes is correct; only the location is wrong.

R7. Section 7, s2_flip_live.py: "Independent V12: fresh
DOM read over CDP, polls up to 10 seconds
(scripts/s2_flip_live.py:390 to 415)". REFUTED.
v12_check is lines 316 to 339: def at 316, docstring
"Independent V12: fresh DOM read over CDP, not the
program", V12_TIMEOUT_MS passed at 325. Lines 390 to 415
are inside route_browser (observe and routing code).
Correction: lines 316 to 339.

R8. Section 7, s2_flip_live.py: "P9 viewport capture
after the scored wall (scripts/s2_flip_live.py:417 to
435)". REFUTED. p9_capture is lines 340 to 356: def at
340, docstring "P9 viewport screenshot via direct CDP".
Lines 417 to 435 are inside route_browser (coverage and
relaxed-gate code). Correction: lines 340 to 356.

R9. Section 7: "the 2750.1 ms median residual in the
reopen phase split (improvements/worker-click5-s2-reopen-
log.md, section 4)". REFUTED as a section citation. The
reopen log has no "## 4" heading. Its headings are 0, 1,
2, 3, 5, 6, 7, 8. The residual line sits in the "### Run
table" subsection of section 3. Correction: section 3,
run table subsection. The number itself is confirmed, see
A11.

R10. Section 4 notes: "set_value already requires the
field to be visible and hit-testable (scripts/cdp.mjs:503
to 510)". REFUTED. The visibility check is lines 501 to
502: line 501 computes the rect and hit, line 502 is the
"if(!e.getClientRects().length||...)" check returning
'field is not visible'. Lines 503 to 510 are the "No
prefill early return" comment. Correction: lines 501 to
502.

### Minor imprecisions, not refuted

- Section 3, cdp.mjs:467, stale-snapshot check. Line 467
  is the dispatch loop header ("for(const a of
  request.actions){"); the actual stale-snapshot evaluate
  is line 470. The check is inside the loop that starts
  at 467, so cite 467 to 470.
- Section 10 item 7, cdp.mjs:83, max_elements 1..80. The
  default 80 is line 83; the 1..80 validation is line 84.
  Cite 83 to 84.
- Section 4 item 5, cdp.mjs:546 to 547, completed counter.
  The increment completed++ is line 546; line 547 is the
  connection error check. Cite line 546.
- Section 5, dom_asserts.py _is_send_key, lines 100 to
  113. The function def is line 96; the body runs 103 to
  114. Cite 96 to 114.
- Section 5, cdp.mjs fill "lines 534 to 541". The fill
  branch body is 534 to 540; line 541 starts the key
  branch on the same closing line. Acceptable as written.

## Part C. Omission, not a number error

The spec never mentions the 4 aborted first attempts in
the (b1) measurement: improvements/s2-flip-b1-runs/run-2
to run-5-aborted.json, each outcome aborted-routing, walls
12365.3, 14372.5, 12652.1, 13734.2 ms. The input-fix log
documents them (lines 404 to 407, 423, 513): first-attempt
routing aborts, nothing sent, same messages re-run. The
spec's "5 of 5" is therefore 5 of 5 completed runs, not 5
of 5 attempts. The numbers in the spec are still correct,
but the spec should say so in one line, so a reader does
not mistake 5/5 for 5 attempts with no aborts.

## Part D. What must change before landing use

Apply corrections R1 to R10 to the spec. The three that
matter most are R6, R7, R8: the landing edits CB-1, V12,
and P9-adjacent code, and the spec currently points the
implementer at the wrong functions for all three. R1
matters because the proposed error string does not exist
in the codebase. Add one line disclosing the 4 routing
aborts from part C. After those fixes, the spec is safe
to use as the landing map: every number in it is verified
from the run JSONs, and every other citation checks out.
