# Batch 12 council 2: task 2 (b1) landing spec review

Review of docs/batch12-task2-b1-landing-spec-20261122.md (commit
55405a5 on main, 491 lines). Base: branch todolist-push, HEAD
4305dcb. This review checks the reasoning and the recommendation,
not just the numbers. Every claim below cites the spec section
plus the file and line it was checked against.

Method. Read the spec in full. Read scripts/cdp.mjs,
scripts/code_exec.py, scripts/cu.py, scripts/dom_asserts.py,
scripts/s2_flip_live.py, scripts/dom_act.py, and
tests/test_s2_flip_wiring.py from todolist-push. Read
improvements/worker-click4-s2-flip-log.md,
improvements/worker-click5-input-fix-log.md (sections 7.1 to
7.3), and improvements/worker-click5-s2-reopen-log.md (sections
0, 1, 3, 4, 5, 6) from todolist-push. Verified every measured
number first-hand from improvements/s2-flip-b1-runs/run-1..5.json
and improvements/s2-flip-reopen-runs/run-1..5.json. Ran the
wiring suite in a temp worktree of todolist-push at 4305dcb:
python3 -m unittest tests.test_s2_flip_wiring -v, 12 tests, OK,
0.057 s. No change was made to todolist-push.

## Overall verdict: NEEDS CHANGE before landing starts

The design is sound and the measurements are exact, but the
spec must not land as written. One finding is a correctness
blocker: the send-requires-focus rule in section 5, as
specified, breaks two working send paths (F1). The option A
recommendation stands as a judgment call, but two of its three
stated reasons for rejecting option B are incorrect (F2, F3)
and the strongest argument for A is missing (F4). The rest are
citation corrections and test-list additions (F5 to F9).

## Section 0: what (b1) is, and the measured results. STANDS.

Every number verifies first-hand from the run JSONs:

- (b1) walls 18477.4, 20592.9, 18839.7, 18738.7, 19094.0.
  Sorted: 18477.4, 18738.7, 18839.7, 19094.0, 20592.9.
  Median 18839.7 ms. Program elapsed 91.575 to 106.622 ms.
  Focus Enter 17 to 23 ms. Pre-send count 0, delayed count 1,
  model calls 0, CB-1 all three True, completed 2, V12
  attempt 1, all 5 runs.
- Reopen walls 29020.4, 27799.1, 28112.6, 28898.1, 28560.9.
  Sorted: 27799.1, 28112.6, 28560.9, 28898.1, 29020.4.
  Median 28560.9 ms. Chromium program elapsed 99.412 to
  113.005 ms. Focus Enter 21 to 25 ms. Pre-send count 0,
  delayed count 1, model calls 0, CB-1 all three True,
  completed 2, V12 attempt 1, all 10 sends. Brave completed 3,
  strict gate every run; Chromium relaxed gate every run.
- The reopen log recommends EXPAND (section 6) and records the
  landing as an open item (section 0: "durable landing of the
  (b1) shape in cdp.mjs (a focus action, or set_value focusing
  the field) with tests"). The flip log section 6 records the
  original Chromium failure as CDP timeout
  Input.dispatchMouseEvent, completed 0, 5003 ms, 0 of 5 sends
  verified. All citations in section 0 check out.

Note for the record: the reopen log section 0 already frames
both options neutrally ("a focus action, or set_value focusing
the field"), so the spec's pick of A is a genuine decision
this review must judge, not something inherited from the log.

## Section 1: where (b1) lives today. STANDS.

- set_value is landed at scripts/cdp.mjs:473 to 533, with no
  e.focus() call anywhere in cdp.mjs (grep returns nothing).
  The read-back as the type_check assert is correctly cited
  to scripts/dom_asserts.py:26 to 29.
- The focus plus Enter helper is laptop-only
  (/tmp/c5-focusenter.mjs), called from
  scripts/s2_flip_live.py:497 to 519 (focus_enter) and
  referenced by the constant at line 76. Verified.
- build_program_set_value is scripts/s2_flip_live.py:129 to
  167, emitting set_value plus a value assert, 2 actions, no
  key, no focus. Verified. The flags at lines 780 to 795 and
  variant_for at lines 189 to 205 check out.
- The count guard helper /tmp/c5-count.mjs is correctly
  described as harness-side and not part of the send method.

## Section 2: why focus is required. STANDS, one off-by-one.

- The T1 to T4 probe results match the input-fix log section
  7.2 exactly: T1 0 bubbles (Enter without focus does not
  send), T2 1 bubble (focus then Enter), T3 1 bubble
  (JS-dispatched Enter, untrusted, live React behavior
  untested), T4 still 1 bubble (retry on an empty composer
  cannot re-send).
- The D-B1 probe matches input-fix log section 7.1:
  dispatchKeyEvent answers in 2 ms on the stuck tab while
  dispatchMouseEvent times out.
- key dispatches keyDown plus keyUp with text '\r' for Enter:
  scripts/cdp.mjs:390 to 412, text assignment at line 410.
  Verified.
- fill starts with click(a) and click dispatches mouseMoved,
  mousePressed, mouseReleased: scripts/cdp.mjs:534 to 541 and
  292 to 313. Verified.
- The P5 gate citation (scripts/code_exec.py:922 to 940) is
  correct: the comment block starts at 922 and the
  require_asserts call is at 936.
- Correction: the fill focus proof is at scripts/cdp.mjs:537,
  not 536. Line 536 is `await click(a);`. Line 537 is the
  activeElement check. Fix the citation (F5).

## Section 3: design decision, option A over option B. NEEDS CHANGE.

The recommendation of A stands as a judgment call, but the
justification as written does not hold. Three problems.

F2. Reason (a) is incorrect. The spec says B "makes the CB-1
accounting ambiguous: input_sent would depend on a flag inside
set_value instead of on a counted action." That is wrong.
With B the program is [set_value(focus:true), key Enter,
assert], and input_sent would be completed >= 2, still a
counted action number. A focus failure inside set_value
throws (the branch returns ok:false and cdp.mjs throws), so
completed stays 0 and input_sent stays False. Completed >= 2
proves the set_value step (including its focus sub-step) and
the Enter both ran, exactly as completed >= 3 proves the
three steps under A. What B actually loses is per-step
granularity: the completed count cannot distinguish a focus
failure from a value failure inside set_value (the error
string can, the count cannot). Restate reason (a) as a
granularity point, not as CB-1 ambiguity.

F3. The cost comparison is misleading. The spec counts A as
"4 files to touch (cdp.mjs, code_exec.py, cu.py,
dom_asserts.py)" and B as "1 file (cdp.mjs) plus a test".
Both counts omit the files both options must touch:
scripts/s2_flip_live.py (builder rewrite plus CB-1 remap)
and the tests. The honest comparison is A touches 6 files
(the 4 mirrors plus the harness plus tests) and B touches 4
(cdp.mjs plus dom_asserts.py for the P5 rule plus the harness
plus tests). The real delta is the 2 mirror files
(code_exec.py, cu.py). The spec's conclusion, "which is the
same total work as option A spread across fewer files", is
false. B is genuinely less code; A costs 2 extra mirror
updates, not zero extra work and not equal work.

F4. The strongest argument for A is missing. The measured
(b1) shape is three separate steps: a 2-action program plus
the focus_enter helper returning {ok, focus, enter}. Landing
focus as its own action preserves those measured step
boundaries one to one, so the landed completed count (4)
maps directly onto the measured evidence (program completed 2
plus helper ok). With B the step shape changes and the
mapping from measured to landed is indirect. Add this
fidelity argument. With it, plus the genuine testability
point (focus testable alone, including the zero-Input-methods
assertion) and the reusability point, A is justified. Without
it, the section leans on reasons (a) and (c), which are
incorrect, and reason (b), which is speculative: no current
program needs focus without a value write.

Minor counter-consideration the spec does not acknowledge:
under A the focus branch duplicates set_value's
unavailable-field checks (disabled, readOnly, aria-disabled,
inert, scripts/cdp.mjs:478) in a second branch. That is a
small maintenance duplication. Note it; it does not change
the recommendation.

## Section 4: the landed focus action. STANDS, two fixes.

- Semantics steps 1 to 5 are coherent and replicate the
  helper: resolve through pageState (scripts/cdp.mjs:157 to
  167), reject unavailable fields, call e.focus(), verify
  document.activeElement === e, return ok, count toward
  completed (scripts/cdp.mjs:546).
- F6. Step 4 claims the error text is "the same wording fill
  uses (scripts/cdp.mjs:537)". It is not. Fill's error text
  at line 537 is 'field is not editable or did not gain
  focus'. The proposed 'field did not gain focus' is a
  substring, not the same wording. Either use fill's exact
  text or drop the sameness claim.
- The no-scroll note is sound: set_value already requires
  the field visible and hit-testable (scripts/cdp.mjs:502,
  not 503 to 510, see F5), and the composer is visible by
  construction in the S2 class.
- The shadow-root walk is correctly deferred as a follow-up,
  but it then appears nowhere in section 10's missing list.
  Add it there (F9).

## Section 5: file-by-file edit list. NEEDS CHANGE.

F1. BLOCKER. The send-requires-focus rule as specified
breaks two working send paths. The spec says: "a send key
(Enter after set_value, per _is_send_key, lines 100 to 113)
with no preceding focus action in the same batch raises
DomAssertError." But _is_send_key does not mean "Enter after
set_value". It returns True for Enter after 'type', 'fill',
or 'set_value' (scripts/dom_asserts.py:96 to 115, the type
list at line 113). Two existing send paths are send keys
under that definition and have no preceding `focus` action:

1. The Brave fill program [fill, key Enter, assert]
   (scripts/s2_flip_live.py:89 to 127). Fill focuses the
   composer internally via its mouse click
   (scripts/cdp.mjs:534 to 541), but there is no action of
   type 'focus' in the batch. The existing test
   test_program_actions_satisfy_p5_requires runs
   require_asserts on exactly this program and expects True
   (tests/test_s2_flip_wiring.py). A literal implementation
   of the spec's rule fails that test and breaks the Brave
   variant the spec explicitly keeps on fill.
2. The desktop send chain [click, type, key Enter]
   (scripts/dom_act.py:708 to 712, focus_type). The click
   establishes focus, but again there is no 'focus' action.
   That chain passes through require_asserts at
   scripts/dom_act.py:748 with available focus_check True.
   A literal implementation of the rule breaks every desktop
   focus_type send with enter=True, including the V12 bench
   send path.

Fix: scope the rule to sends whose nearest preceding value
action in the same batch is set_value, or equivalently treat
fill, click, confirm_click, hover_click, and type as
focus-establishing actions. State the scope in the spec; do
not cite _is_send_key as if it already means "Enter after
set_value". Add the two regression tests (F7).

The rest of the edit list verifies exact, line for line:

- cdp.mjs whitelist line 434 and element-action list line
  435: exact. Adding 'focus' to both is correct and complete
  for the dispatch side.
- code_exec.py allowed set line 217 and element_actions line
  218: exact. No new field validation is needed: focus takes
  no payload beyond ref or selector, and the P2 binding check
  covers the batch. Verified that code_exec.py has no other
  action-type list (only lines 217, 218, and the text check
  at 251).
- cu.py browser allowed set line 1299 and browser
  element-action check line 1341: exact. Verified cu.py has
  no other browser action list (the text check at 1309 does
  not apply to focus, which takes no text).
- dom_asserts.py: adding a 'focus' entry is correct, and no
  change to _api_dom_act is needed, because it already passes
  available focus_check True (scripts/code_exec.py:936 to
  938) with the comment that focus_check is available by
  construction. The spec does not say this; it should, so
  the landing engineer does not go looking for a caller
  change that is not needed.
- s2_flip_live.py: replace build_program_set_value (lines
  129 to 167), remove focus_enter (lines 497 to 519) and
  LAPTOP_FOCUSENTER (line 76), keep the flags (lines 780 to
  795) and variant_for (lines 189 to 205). All exact. The
  "do not add a value assert after the Enter" warning is
  correct: the composer is empty once sent. The CB-1 remap
  values are correct (input_sent = completed >= 3,
  target_received = completed >= 1, verified = V12 found),
  matching the existing convention in send_browser where
  target_received means the value landed (completed >= 1)
  and verified means the bubble was found.
- The "no change to set_value, key, or fill" statement is
  correct for the ranges cited (cdp.mjs:473 to 533, 390 to
  412, 534 to 541).

F5. Wrong line citations to fix in section 5 (and the
sections that repeat them):

- send_browser CB-1 is scripts/s2_flip_live.py:569 to 585,
  not 615 to 625. Lines 615 to 625 are inside seed_scratch
  and close_scratch. The set_value mapping is at 569 to 578
  (input_sent from the helper ok, target_received completed
  >= 1) and the fill mapping at 580 to 585.
- V12 is scripts/s2_flip_live.py:316 (def v12_check), not
  390 to 415. Lines 390 to 415 are inside run(), the routing
  decision code.
- P9 is scripts/s2_flip_live.py:340 (def p9_capture), not
  417 to 435. Lines 417 to 435 are also inside run().
- dom_asserts.py click entry is lines 48 to 50, not 42 to
  45. Lines 42 to 45 are the comment block above ASSERTS.
- dom_asserts.py fill entry is lines 63 to 65, not 62 to 64.
- dom_asserts.py set_value entry is lines 66 to 68, not 65
  to 68.
- cdp.mjs stale-snapshot check is line 470, not 467.
- cdp.mjs set_value visible check is line 502, not 503 to
  510.
- cdp.mjs read-back checks are lines 518 and 528. The cited
  range 516 to 522 covers the first and misses the second.
- cdp.mjs fill activeElement check is line 537, not 536
  (section 2). Line 536 is `await click(a);`.
- cdp.mjs unavailable-field check is line 478 alone, not
  476 to 478.

None of these changes the design; all of them matter in a
landing spec whose value is precise file plus line guidance.
Fix every citation before landing starts.

## Section 6: pre-send count guard stays harness-side. STANDS.

- The guard runs in send_browser at
  scripts/s2_flip_live.py:539 to 543 (count_check, abort with
  outcome already-sent when count is above 0). Verified.
- The count helper is at lines 478 to 495 (LAPTOP_COUNT use
  at 486). Verified.
- Not moving the guard into cdp.mjs is the right call: there
  is no count action type (whitelist at cdp.mjs:434), and a
  read-only count action would need its own P5 treatment.
- The measured numbers check out: pre-send count 0 in all 5
  (b1) runs and all 5 reopen runs, verified from the JSONs.

## Section 7: post-verification. STANDS.

- Delayed count at scripts/s2_flip_live.py:691 to 704.
  Verified. Delayed count exactly 1 in all 5 (b1) runs and
  all 5 reopen runs, verified from the JSONs.
- V12 found attempt 1 in all 10 reopen sends, verified from
  the JSONs. P9 PASS 10 of 10, verified from the reopen log
  section 5.
- The residual note is correct: median residual 2750.1 ms in
  the reopen phase split (sorted residuals 2708.9, 2743.1,
  2750.1, 2827.3, 2914.5), explained in the reopen log
  section 4 as the unspanned pre-send count-check SSH call.
  Leaving it as is, and not changing the phase split, is
  right.

## Section 8: tests to write. NEEDS CHANGE (additions only).

- The failing-first list is sound and complete for the focus
  action itself: unsupported before landing, ref resolution,
  e.focus() plus activeElement check, zero Input methods,
  disabled and readOnly rejection, missing ref, both ref and
  selector, Enter regression guard, set_value still does not
  focus. Each maps to a real check in the code (cdp.mjs:434
  to 436, 157 to 167, 478, 390 to 412).
- The baseline claim checks out: the wiring file is 12 of 12
  today, verified by running it (12 tests, OK), and the
  reopen log records "tests 12/12 pass (was 11/11)" for the
  split-variant test. The dry run 0 baseline checks out from
  the reopen log section 3: PASS, wall 30123.9 ms, Chromium
  elapsed 85.8 ms, completed 2. (There is no run-0.json on
  todolist-push; the numbers come from the log, which the
  spec cites correctly.)
- F7. Add two regression tests for the scoped rule: [fill,
  key Enter, assert] still passes require_asserts, and the
  desktop focus_type chain [click, type, key Enter] still
  passes require_asserts. Without them the F1 breakage has no
  guard in the spec's own test list. The existing test
  test_program_actions_satisfy_p5_requires already covers the
  fill program, but the spec must name it as a must-not-break
  test, not leave it implicit.
- F7 continued. The landed dry-run pass condition needs an
  elapsed bound. "Must match it except completed 4 instead
  of 2" cannot hold for elapsed: the landed 4-action program
  adds a focus step (measured 17 to 25 ms in the helper) and
  a key step (about 2 ms) to the 85.8 ms baseline, so expect
  about 105 to 115 ms, not 85.8 ms. State the bound, or the
  dry run will look like a mismatch on its first run.

## Section 9: landing order. STANDS, one addition.

- Tests first and failing-first, separate commits for tests
  and code, VM test run, laptop sync with a relay-restart
  check, dry run 0, 5 live re-runs with the reopen timing
  rules (including avoiding clone2-watch holds), run JSONs
  to improvements/s2-flip-land-runs/run-1..5.json, P9 before
  scoring, verification log that confirms or revises EXPAND
  from the numbers. Sound and complete.
- F8. Step 3 says "plus the full discover for the touched
  modules". Name the dom_act tests explicitly
  (tests/test_step5_p1p5.py and the dom_act suite): the rule
  change touches require_asserts, which dom_act.py also calls
  (line 748). The F1 regression must be caught on the VM
  before any laptop sync.

## Section 10: still missing. NEEDS CHANGE (one addition).

Items 1 to 9 all check out against the code and the logs:

1. /tmp/c5-focusenter.mjs is not in the repo (only
   referenced as LAPTOP_FOCUSENTER in s2_flip_live.py).
   Reconstruction basis is input-fix log section 7.3.
2. /tmp/c5-count.mjs is not in the repo. Both guards depend
   on it being present on the laptop.
3. The coordinator decision is pending; that is the point of
   this council round.
4. No focus tests exist yet. Verified: no focus test in the
   wiring file or in tests/cdp_validation.mjs.
5. No live proof of landed code exists. All 15 measured
   sends (5 b1 plus 10 reopen) ran through /tmp helpers.
6. Laptop sync and relay restart are genuinely unknown from
   this side. Stated honestly.
7. The 80-element cap (cdp.mjs:83) still forces the relaxed
   gate: all 5 reopen Chromium runs ran relaxed, verified
   from the JSONs.
8. The mouse stall is unsolved. Verified against reopen log
   section 6, caveat 2.
9. The Brave decision is pending. The landing keeps Brave on
   fill, which sends 5 of 5 in both the flip and the reopen.

F9. Add a tenth item: the shadow-root activeElement walk
from section 4. The focus check is a direct equality check;
if a future target lives in a shadow root, the check must
walk shadowRoot.activeElement the way the harvest does
(cdp.mjs:250). Section 4 calls it a follow-up; section 10
must list it or it is untracked.

## Section 11: acceptance criteria. STANDS, with the F7 addition.

- All tests pass, dry run 0 passes, 5 re-runs at 10 of 10
  sends with pre-send count 0 and delayed count 1, model
  calls 0, median wall comparable to 28.6 s, no /tmp helper
  call left in the Chromium send path, verification log
  written. Sound. Add the landed dry-run elapsed bound from
  F7 (about 105 to 115 ms, completed 4) so "comparable" is
  testable.

## Findings list

- F1 BLOCKER, section 5: send-requires-focus rule breaks
  the Brave fill program and the desktop focus_type chain.
  Scope it to set_value-preceded sends.
- F2, section 3: reason (a) is incorrect; B keeps CB-1
  sound, it only loses per-step granularity. Restate.
- F3, section 3: cost comparison is misleading; honest
  delta is 2 mirror files, not "same total work".
- F4, section 3: add the fidelity-to-measured-shape
  argument for A. Recommendation stands with it.
- F5, sections 2, 4, 5: eleven wrong line citations
  (CB-1, V12, P9, click, fill, set_value entries, stale
  check, visible check, read-back, fill focus check,
  unavailable check). Fix all.
- F6, section 4: "same wording fill uses" is wrong; use
  fill's exact text or drop the claim.
- F7, section 8: add the two regression tests and the
  landed dry-run elapsed bound (about 105 to 115 ms).
- F8, section 9: name the dom_act tests in step 3.
- F9, section 10: add the shadow-root walk as item 10.
- F10, section 3: note the duplicated unavailable-field
  checks under A as a small cost.

## Council 2 verdict

NEEDS CHANGE. Fix F1 before anything else: without the
scoping, the landing as specified breaks the Brave half
that sends 5 of 5 and the desktop send path the V12 bench
uses. Fix F2, F3, and F4 so the option A decision rests on
true reasons. Fix F5 so the landing engineer is sent to the
right lines. Add F7, F8, and F9. The measurements are exact,
the design is sound, and option A is the right pick once
its justification is corrected. After the fixes, the spec
can go to landing with the coordinator's option pick.
