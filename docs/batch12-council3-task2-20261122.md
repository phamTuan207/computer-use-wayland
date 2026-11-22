# Batch 12 council 3: task 2 (b1) landing spec review

Status: review only. No code changed by this file. The spec under review
is docs/batch12-task2-b1-landing-spec-20261122.md, commit 55405a5 on
main, 491 lines. Brief: batch 12 task 2 from coordinator Muse, commit
26ebe40, coord/clone1.md. Base checked: branch todolist-push, HEAD
4305dcb. Every claim below was checked first-hand against the code on
todolist-push and the run JSONs on todolist-push. Line counts are from
wc -l.

## Verdict: COMPLETE on brief coverage, with 8 corrections

The spec answers every item the brief asked for. It is a design doc
only and changes no code: commit 55405a5 adds one file, 491
insertions, 0 deletions. The corrections below do not remove any
section. One is substantive (E1, a wrong error string attributed to
fill). Five are wrong line-range citations (E2 to E6). Two are
trivial off-by-one imprecisions (E7, E8). The fix pass must apply
E1 to E6 before the spec is treated as the landing reference.

## 1. Brief coverage checklist

Each required item, with the spec section that answers it.

1. Where the focus action goes, cdp.mjs or a set_value focus
   field. Section 3. PASS. Both options are laid out, option A
   (standalone focus action in cdp.mjs) is recommended, option B
   (focus boolean field on set_value) is rejected with reasons
   (CB-1 accounting ambiguity, cannot express focus alone).
   The coordinator must still pick one; the spec states this
   plainly in section 10 item 3.
2. Which API. Sections 3, 4, 5. PASS. New `focus` action type,
   resolved through pageState by ref or selector, e.focus() in
   page context, activeElement proof, no scroll, no mouse, no
   key. File-by-file edit list covers cdp.mjs, code_exec.py,
   cu.py, dom_asserts.py, s2_flip_live.py, and the wiring
   tests.
3. Preconditions, pre-send count guard. Section 6. PASS. Guard
   runs in send_browser before the program, count above 0
   aborts with already-sent. The spec states it stays
   harness-side, depends on /tmp/c5-count.mjs, and gives the
   measured numbers (pre-send count 0 in all 5 b1 runs and
   all 5 reopen runs).
4. Post-verification, delayed count. Section 7. PASS. Delayed
   count after a 10 second sleep, V12, P9, CB-1 for the landed
   program, plus the known 2750.1 ms median residual artifact
   left as is.
5. Which tests, unit plus wiring plus live dry run. Section 8.
   PASS. 7 unit tests in the tests/cdp_validation.mjs style,
   4 wiring tests in tests/test_s2_flip_wiring.py, live dry
   run with the exact command and pass conditions, including
   the reopen dry run 0 baseline for comparison.
6. Landing order, tests first, code after, sync laptop, re-run
   5 runs. Section 9. PASS. 7 steps in order, tests and code
   in separate commits so the failing-first proof survives,
   laptop sync verification, dry run 0 gate, 5 live re-runs
   with run JSONs to improvements/s2-flip-land-runs/run-1..5.json.
7. What is still missing before it can land. Section 10. PASS.
   9 items, stated plainly: /tmp/c5-focusenter.mjs not in the
   repo, /tmp/c5-count.mjs not in the repo, coordinator
   decision pending, no tests yet, no live proof of landed
   code, laptop not synced, relay restart unknown, 80-element
   cap forces the relaxed gate, mouse stall unsolved, Brave
   uniform decision open.
8. Design doc only, no code change. PASS. Commit 55405a5
   touches only docs/batch12-task2-b1-landing-spec-20261122.md.

## 2. Numbers re-verified first-hand from the run JSONs

Recomputed from improvements/s2-flip-reopen-runs/run-1..5.json
and improvements/s2-flip-b1-runs/run-1..5.json on todolist-push.
All match the spec section 0.

- Reopen median wall: 28560.9 ms. Walls: 29020.4, 27799.1,
  28112.6, 28898.1, 28560.9. Median 28560.9. Matches.
- b1 median wall: 18839.7 ms. Walls: 18477.4, 20592.9,
  18839.7, 18738.7, 19094.0. Median 18839.7. Matches.
- Reopen Chromium program elapsed: 113.005, 106.613, 107.077,
  99.412, 104.164. Range 99.412 to 113.005. Matches.
- b1 Chromium program elapsed: 97.656, 106.622, 91.575,
  102.811, 104.563. Range 91.575 to 106.622. Matches.
- Reopen Chromium focus Enter ms: 25, 21, 23, 25, 23. Range
  21 to 25. Matches.
- b1 Chromium focus Enter ms: 23, 23, 17, 18, 20. Range 17
  to 23. Matches.
- Pre-send count 0 in all 5 b1 runs and all 5 reopen runs.
  Delayed count 1 in all 10. Model calls 0 in all 10.
  V12 found attempt 1 in all 10 sends. CB-1 all three True
  in all 10 sends. Matches.
- Reopen Chromium routing_relaxed True in all 5 runs,
  observe 80 elements truncated. Matches section 10 item 7.
- Reopen phase split residual: 2708.9, 2827.3, 2743.1,
  2750.1, 2914.5. Median 2750.1. Matches section 7.
- Reopen dry run 0 (reopen log section 3): PASS, wall
  30123.9 ms, Chromium elapsed 85.8 ms, completed 2.
  Matches section 8.

Log claims re-verified: reopen log section 6 recommends
EXPAND and caveat 2 states the mouse stall is unsolved with
step 9 as the target; caveat 4 states the durable landing is
still open. Input-fix log section 7.1: dispatchKeyEvent
answers in 2 ms on the stuck tab. Section 7.2: T1 0 bubbles,
T2 1 bubble, T3 1 bubble (b2, untrusted, live React
untested), T4 still 1 bubble. Section 7.3: focusenter is
Runtime.evaluate focus on textarea[aria-label="Message"],
assert activeElement, dispatchKeyEvent keyDown plus keyUp
Enter, return {ok, focus, enter}. All match the spec
section 2.

## 3. Citations confirmed correct

Spot-checked against todolist-push HEAD 4305dcb. The spec base
HEAD 4305dcb differs from the brief's 212e0ad only by one doc
commit (improvements/worker-click5-coord-log.md, 101
insertions), so no code citation is affected.

- cdp.mjs:434 whitelist, :435 element-action list, :473
  set_value branch start, :476 to :478 unavailable checks,
  :501 to :502 visibility check (see E6 for the wrong range
  the spec cites), :516 to :522 read-back, :534 to :541 fill,
  :536 activeElement check, :546 completed counter. No
  e.focus() call anywhere in cdp.mjs. Confirmed.
- cdp.mjs:157 to :167 pageState, :250 to :251 shadow root
  activeElement walk, :292 to :313 click with mouseMoved,
  mousePressed, mouseReleased, :83 max_elements 1..80.
  Confirmed.
- code_exec.py:206 to :280 P2 binding, :217 allowed set,
  :218 element_actions, :922 to :940 P5 gate with available
  focus_check True, type_check True, sent_bubble False.
  Confirmed.
- cu.py:1299 browser allowed set, :1341 browser
  element-action check. Confirmed.
- dom_asserts.py:26 to :29 type_check comment, :42 to :45
  click entry, :62 to :64 fill entry, :65 to :68 set_value
  entry, :100 to :113 _is_send_key. Confirmed.
- s2_flip_live.py:76 LAPTOP_FOCUSENTER, :77 LAPTOP_COUNT,
  :129 build_program_set_value start (see E4 for the end),
  :539 to :543 pre-send guard, :691 to :704 delayed count,
  :780 to :795 flags. Confirmed.
- tests/test_s2_flip_wiring.py has 12 tests, including
  test_set_value_program_carries_p2_stamps_and_passes_p5
  (2 scope stamps, 2 observation_id stamps, require_asserts
  with available focus_check True, type_check True,
  sent_bubble False) and
  test_chromium_set_value_splits_variants_per_browser.
  Confirmed. Reopen log lines 113 to 115 record wiring
  tests 12/12 pass.
- tests/cdp_validation.mjs extracts production functions
  with vm.runInNewContext. Confirmed.

## 4. Corrections the fix pass must apply

E1, substantive. Section 4 item 4 says: on failure throw
'field did not gain focus', the same wording fill uses
(scripts/cdp.mjs:537). Wrong. Fill at cdp.mjs:537 throws
'field is not editable or did not gain focus'. The spec
invents a shorter string and misattributes it to fill. Fix:
either use fill's exact string, 'field is not editable or
did not gain focus', or define 'field did not gain focus'
as a new distinct string and delete the claim that it is
the same wording fill uses. An implementer following the
spec as written would add a third error string while
believing it matches fill.

E2, citation. Section 7 cites V12 as
scripts/s2_flip_live.py:390 to 415 and P9 as :417 to 435.
Wrong. v12_check is lines 316 to 339, p9_capture is lines
340 to 357. Lines 390 to 435 sit inside route_browser.
The functional descriptions are correct (V12 fresh DOM
read, polls up to V12_TIMEOUT_MS which is 10000 ms; P9
viewport capture via direct CDP, PNG saved for human
review). Fix the two ranges only.

E3, citation. Section 5 cites send_browser CB-1 for the
set_value variant as lines 615 to 625. Wrong. The CB-1
block is lines 570 to 588: set_value branch 569 to 578
(input_sent from the helper result, target_received
completed >= 1), fill branch 580 to 585, verified set from
V12 at 588. Lines 615 to 625 sit inside close_scratch and
run, not CB-1. The old-mapping description in the spec is
correct. Fix the range to 570 to 588.

E4, citation. Sections 1 and 5 cite build_program_set_value
as lines 129 to 167. Wrong end. The function spans 129 to
163; message_for starts at 164. Fix to 129 to 163.

E5, citation. Sections 1 and 5 cite variant_for as lines
189 to 205. Wrong end. variant_for spans 189 to 196;
note() starts at 197. Fix to 189 to 196.

E6, citation. Section 4 note cites the set_value visible
and hit-testable requirement as scripts/cdp.mjs:503 to
510. Wrong. The check is lines 501 to 502 (rect and hit
computation at 501, 'field is not visible' return at 502).
Lines 503 to 510 are the "No prefill early return" comment.
The claim itself is true. Fix the range to 501 to 502.

E7, trivial. Section 2 cites the key function as
scripts/cdp.mjs:390 to 412. The function starts at 394;
lines 390 to 393 are the tail of click. The '\r' line 410
is correct. Fix to 394 to 412.

E8, trivial off-by-one. focus_enter is cited as 497 to 519;
it spans 497 to 520 (send_browser starts at 521).
count_check is cited as 478 to 495; it spans 478 to 496
(focus_enter starts at 497). Fix both ends.

## 5. Notes, not errors

N1. Section 4 says "Call e.focus() in page context" but
does not name the evaluate expression. The implementer can
infer it from the pageState machinery (section 3) and the
fill editable check pattern (elementExpression, cdp.mjs:536),
so this is adequate for a design doc. The fix pass may add
one sentence naming the expression shape; it is optional.

N2. Section 5 sets the landed CB-1 mapping to input_sent =
completed >= 3. This follows the existing convention (the
fill variant uses completed >= 2 for a 3-action program),
and verified = V12 found still dominates the verdict, so a
failed trailing assert cannot score a send. No change
needed.

N3. Section 3 rejects option B partly because a focus flag
inside set_value would make CB-1 accounting ambiguous.
That is a judgment call, not a fact, and the spec records
the coordinator must still pick. No change needed.

## 6. What the fix pass must do

Apply E1 to E6 in the spec, plus E7 and E8. Do not add or
remove any section. After the fix pass, the spec is the
landing reference: tests first, code after, laptop sync,
dry run 0, then 5 live re-runs per section 9.
