# Batch 13 redteam: task 2 report (b1 spec review)

## 0. Verdict: BROKEN, narrowly scoped

The report under attack is docs/batch13-task2-b1-spec-review-20261122.md,
commit f5e36e7, verdict AMEND. I attacked it first-hand against the code
and evidence on origin/todolist-push at 8c6553a (the review HEAD was
3167c76; the diff between 3167c76 and 8c6553a for every reviewed file is
empty, verified below).

The AMEND verdict stands, and the cores of F1, F3, and F4 stand. But the
report is BROKEN as a fix-pass guide: F2 contains a false evidence claim
(R1 below) that drives a backwards fix-pass instruction. If the fix pass
follows that instruction, it writes a false sentence into the spec. The
report must be corrected on R1 before the fix pass relies on it. No
re-review of the whole report is needed: everything else I checked holds,
listed in section 3.

## 1. Breaking findings

### R1 (HIGH): F2 note, "p9 as null in every JSON", is false

What the report says (F2, fix-pass notes): "the run JSONs still carry p9
as null in every JSON, so the PNG paths come from the audit repair-list
filename convention, as the manifest records; the spec should say that
instead of implying the JSONs name the PNGs."

What is true: p9 is not null in any run JSON. I read all 19 JSONs
first-hand at 8c6553a: the 15 run JSONs and the 4 aborted JSONs all carry
p9 as an object naming the PNG path. Examples:

- improvements/s2-flip-b1-runs/run-1.json: p9 is {"chromium": {"ok": true,
  "png": "improvements/s2-flip-b1-runs/p9-run1-chromium.png",
  "wall_ms": 3637.2}}.
- improvements/s2-flip-reopen-runs/run-1.json: p9 names both
  p9-run1-brave.png and p9-run1-chromium.png.
- improvements/s2-flip-runs/run-1.json: p9 names both
  p9-run1-brave.png and p9-run1-chromium.png.
- The 4 aborted JSONs also carry p9 objects naming their PNGs.

I checked the same field at the review HEAD 3167c76 with git show:
run-1.json there also carries the p9 object, so the claim is false at
the review HEAD too. I checked the first commit that introduced
run-1.json (4bd6292): p9 was an object naming the PNG path from the
start. It was never null. All 25 JSON p9 entries name files that exist
in the repo, verified by path lookup, zero missing.

Source of the error: the report copied the manifest's wrong auditor note
without checking it. improvements/s2-flip-p9-manifest.md says "the run
JSONs carry p9 as null, so they do not name the PNG paths." That note is
itself wrong, and the report repeats it as verified fact ("as the
manifest records") while elsewhere claiming the run JSONs were recomputed
from a script. The p9 field sits in the same JSONs the report says it
recomputed.

Consequence: the recommended fix-pass wording is backwards. The JSONs DO
name the PNGs, so the spec must NOT be told to say the paths come from
the repair-list convention. The F2 core finding is unaffected: all 25
PNGs are in the repo (re-verified 25 of 25 in section 3), so section 10
item 11 is still struck. Only the note is wrong, but it is attached to a
HIGH finding and written as an instruction, so it breaks the report as a
fix-pass guide.

Fix: strike the p9-null note from F2 and replace it with the true
statement: every run JSON carries p9 naming its PNG path. The manifest's
auditor note carries the same error and should be corrected alongside,
since the fix pass may read the manifest.

### R2 (MINOR, F3 fix list incomplete): double_click is missing from the corrected focus-establishing list

What the report proposes (F3 fix): exempt only batches containing a
focus-establishing action before the send key, listing "click,
confirm_click, hover_click, fill, or the new focus".

What the code says: double_click is also focus-establishing. It carries
a focus_check entry in ASSERTS (scripts/dom_asserts.py, lines 51 to 53:
"target is document.activeElement after the double click, before any
keystroke"), it is in the desktop allowed set (scripts/cu.py, line 1297),
and in the desktop path it moves to the point and presses the left button
twice (scripts/cu.py, lines 2048 to 2054), which is a real click that
focuses. A batch [double_click, type, key Enter] would be wrongly
rejected by the report's corrected rule, even though the double_click did
focus the field.

Scope: no such batch exists today (focus_type uses a single click,
scripts/dom_act.py, lines 708 to 712), and the spec's own list omits
double_click too, so the report inherits the omission rather than
inventing it. The F3 diagnosis itself stands. Fix: add double_click to
the list, or define the exemption through the focus_check assert instead
of an action list.

### R3 (MINOR, F4 assert component unmeasured): the 0 to 10 ms bubble-assert bound assumes the bubble is present at the first poll

What the report says (F4 corrected derivation): the trailing bubble
assert adds "about 0 to 10 ms" because assertAction polls every 10 ms
(scripts/cdp.mjs, lines 415 to 427, setTimeout 10 ms).

What is missing: no cited measurement bounds how long the bubble takes
to appear after the Enter. The assert cost is the bubble render latency
after Enter, not the poll interval: if the bubble is present at the first
poll the cost is about one evaluate (2 to 3 ms), but if React needs 30
ms to render the new bubble, the assert costs about 30 ms. The V12
elapsed_ms figures (2 to 4 ms in the (b1) run JSONs) do not bound this:
V12 runs after the focus_enter helper returns, about 1.3 s after the
Enter, when the bubble has long been rendered. The report labels the F4
figures as estimates in its section 7, so this is a weakness, not a
falsehood. The dry-run range "about 90 to 100 ms" could false-fail if
the bubble takes longer than about 10 ms to render on a scratch tab.

Fix: the fix pass should measure the post-Enter bubble latency on a
scratch tab (one Runtime.evaluate loop after the Enter) or widen the
dry-run range to cover it. The report's section 4 already asks for the
focus step's own timing to be recorded separately; add the bubble
latency to that ask.

### R4 (TRIVIAL): verification log entries out of order

Section 6 lists the 14:31 entry ("confirmed the branch moved to
8c6553a") after the 14:35 entries. The times themselves are consistent:
8c6553a was committed at 14:26:55 +07 (git show 8c6553a), inside the
stated 14:20 to 14:33 work window, and the report commit f5e36e7 is at
14:34:23 +07. Only the listing order is off. No content is affected.

## 2. What the attack verified as correct

### 2.1 Line citations

I re-checked the section 2.1 citations with grep and direct reads at
8c6553a. All exact except the two F9 slips, which are real:

- cdp.mjs:83 to 84 (max_elements 1..80), 157 to 167 (pageState),
  250 to 251 (shadow-root activeElement walk), 390 to 412 (key, text
  '\r' line 410), 434 (whitelist, no 'type' action), 435 to 437
  (element-action list), 467 to 470 (stale-snapshot check), 473 to 533
  (set_value branch), 478 ('field unavailable'), 501 to 502 (visible
  and hit-testable check), 517 to 518 and 528 (read-back check),
  534 to 541 (fill, ActiveElement check line 536, error wording line
  537), 546 (completed increment, after the assert branch, so assert
  increments completed too). No e.focus() call anywhere in cdp.mjs;
  "focus" occurs 4 times (a comment, harvest focused fields, the fill
  error string).
- code_exec.py:217 (allowed set), 218 (element_actions), 277 to 284
  (P2 binding check), 922 to 940 (P5 gate), require_asserts call lines
  936 to 939, closing line 939 with 'sent_bubble': False.
- cu.py:1299 (browser allowed set, no hover_click), 1341 (browser
  element-action check, mutual exclusion plus non-empty strings).
- dom_asserts.py:26 to 29 (fill and set_value map to type_check),
  48 to 50 (click entry), 51 to 53 (double_click entry), 63 to 65
  (fill entry), 66 to 68 (set_value entry), 96 to 114 (_is_send_key,
  covers Enter after type, fill, or set_value). require_asserts fails
  closed on unknown action types and has the trailing-assert rule.
- dom_act.py:664 to 712 (focus_type, docstring "Click an input, type,
  and verify", chain [click, type, key Enter] lines 708 to 712), 748
  (require_asserts gate).
- s2_flip_live.py:76, 77, 84, 89 to 126, 117 to 121, 129 to 161,
  189 to 195, 316 to 338, 340 to 356, 478 to 495, 497 to 519, 539 to
  543, 568 to 588, 691 to 704, 780 to 795. All boundaries exact.
  count_check appends no span; focus_enter appends a span.
- tests/test_s2_flip_wiring.py: 12 test methods, counted. The named
  tests exist as described. test_program_without_trailing_assert_
  would_fail_p5 covers the fill shape only.
- tests/cdp_validation.mjs slices the source between 'async function
  key(' and 'async function assertAction(', confirmed by direct read.

### 2.2 Recomputed numbers

Recomputed from the 15 run JSONs plus 4 aborted JSONs with a script.
All match the report:

- (b1), 5 runs: 5 of 5 sent, median wall 18839.7 ms, program elapsed
  91.575 to 106.622 ms, helper enter.ms 17 to 23 ms, pre-send count 0,
  delayed count 1, model calls 0, completed 2, all 5 runs.
- (b1) aborted, runs 2 to 5: outcome aborted-routing under
  browsers.chromium.outcome, walls 12365.3, 14372.5, 12652.1,
  13734.2 ms.
- Reopen, 5 runs: 10 of 10 sent, median wall 28560.9 ms, Chromium
  program elapsed 99.412 to 113.005 ms, helper enter.ms 21 to 25 ms,
  pre-send count 0, delayed count 1, model calls 0, V12 attempts 1 in
  all 10 sends, all 5 Chromium runs relaxed (routing_relaxed True,
  observe truncated True, 80 elements).
- Reopen phase split residual: 2708.9, 2827.3, 2743.1, 2750.1,
  2914.5 ms, median 2750.1 ms, from the run JSONs.
- Original flip, Chromium: 0 of 5 sends, outcome failed-unverified in
  all 5, program log "dom_act ok False completed 0 ms 5003" in runs
  1, 3, 4, 5 and "ms 5002" in run 2.
- Input-fix log 7.1 (D-B1 dispatchKeyEvent Shift answers in 2 ms),
  7.2 (T1 0 bubbles, T2 1 bubble, T3 1 bubble untrusted, T4 still
  1 bubble), 7.4 ("focus_enter ok True (focused TEXTAREA, Enter
  2ms)"), flip log section 5 run 1 ("each evaluate 2-3ms"): all quoted
  accurately.
- Reopen log section 3 dry run 0: PASS, wall 30123.9 ms, Chromium
  elapsed 85.8 ms, completed 2. Log-only evidence, no run-0 JSON in
  the repo tree. Reopen log section 1 line 115 and section 8 line 330
  both record wiring tests 12/12 pass.

### 2.3 Findings F1 to F13

- F1 stands: c5-focusenter.mjs is in the repo at
  improvements/s2-flip-b1-runs/c5-focusenter.mjs, commit 3ef8f55 (28
  files). I verified 2478 bytes, 42 lines, sha256
  94ee467ed3067e044491ad19153c24b73d574a8106a5367db454c0e47e1a695f,
  matching the manifest row exactly.
- F2 core stands: all 25 P9 PNGs verified independently against the
  manifest, section-aware (sha256, byte size, PNG magic), 25 of 25,
  zero mismatches. Totals: (b1) 1,210,605 bytes, reopen 2,354,937
  bytes, original flip 2,740,488 bytes, total 6,306,030 bytes. Only
  the p9-null note is wrong, see R1.
- F3 stands: the click establishes focus in focus_type, not the type;
  there is no 'type' action in cdp.mjs; 'type' has a type_check ASSERTS
  entry (dom_asserts.py, lines 60 to 62), so [type, key Enter, assert]
  would pass require_asserts under the spec's rule. Fill does click
  first (cdp.mjs, line 535, await click(a)), so the report's claim
  that fill focuses through its click is correct.
- F4 stands in substance: the spec's 105 to 115 ms dry-run figure
  misattributes the helper enter.ms (17 to 25 ms, live) as the focus
  cost and mixes live with scratch timings. The report's corrected
  dry-run range (85.8 plus focus 2 to 3 plus Enter on scratch 2 plus
  assert polling 0 to 10, about 90 to 100 ms) and live range (91.575
  to 106.622 plus focus 2 to 3 plus live Enter 17 to 25 plus assert
  polling 0 to 10, about 110 to 145 ms) check out arithmetically
  against the program shapes: the baseline programs are [set_value,
  assert] with no key in the program, so the Enter is genuinely added,
  not double counted. The assert component is the one unmeasured
  piece, see R3.
- F5 stands: hover_click appears 0 times in cu.py, but is in the
  cdp.mjs whitelist (line 434), the code_exec.py allowed set (line
  217), and dom_asserts.py (lines 54 to 56).
- F6 stands: the helper returns {focused: false, error: 'no-textarea'}
  when the textarea is missing, throws 'composer did not gain focus'
  on focus failure, and performs no unavailable-field checks.
- F7 stands: the helper sends code 'Enter' on both keyDown and keyUp
  and text '\r' on keyDown only; key() never sends a code field and
  sends the same params object, including text '\r', for both keyDown
  and keyUp (cdp.mjs, lines 390 to 412).
- F8 stands: the dispatch chain is an else-if over distinct action
  types (cdp.mjs, lines 471 to 545).
- F9 stands: both one-line slips are real (code_exec.py:936 to 939,
  cdp.mjs click closes line 314).
- F10 stands: all seven items check out against the code and the
  tests, including (c) the trailing-assert test covering the fill
  shape only and (g) the cdp_validation.mjs slice pattern.
- F11 stands: element_ref.validate_action_binding (lines 146 to 164)
  is type-agnostic; action_result.py line 33 only re-exports
  DOM_ASSERT_EXCEPTIONS; require_asserts has only two production
  callers (code_exec.py:936 and dom_act.py:748); no AssertSetTests
  chain in test_step5_p1p5.py contains a focus action.
- F12 stands: c5-count.mjs is not in the repo (zero files match in
  the tree); the batch 13 assignment commit e03e288 picks neither
  option A nor option B; no focus-action tests exist in the tests;
  all 5 reopen Chromium runs ran relaxed.
- F13 stands: no run-0 JSON exists in improvements/s2-flip-reopen-
  runs on todolist-push.

### 2.4 Method and history claims

- Diff 3167c76 to 8c6553a for every reviewed file is empty, verified
  with git diff. Diff 4305dcb to 3167c76 for the reviewed files holds
  only the 27 evidence files (25 PNGs, manifest, focusenter helper);
  no code file changed, so every cited line number still holds.
- Commit 3ef8f55 holds 28 files with the stated message. Correction
  commit b7d9fad exists. Spec base 4305dcb exists. Spec fix pass
  20f3b99 exists.
- Report commit f5e36e7 holds only the report file (607 insertions,
  1 file). The report holds no long dashes (grep count 0) and no
  personal information.
- The review's "15 mismatches" naive-run anecdote is arithmetically
  consistent: 15 filenames repeat across the three manifest sections
  (5 Chromium names in all 3 sections, 5 Brave names in 2 sections).
- 8c6553a was committed at 14:26:55 +07, inside the review's stated
  14:20 to 14:33 work window.

## 3. Recommendation

Correct R1 in the report (strike the p9-null note, state that every run
JSON names its PNG path through p9), correct the manifest's auditor note
the same way, and fold R2 and R3 into the fix-pass instructions. Then
the AMEND verdict and the fix pass can proceed as the report directs.
No second full review is needed: the attack found one false claim and
two minor gaps, and everything else in the report verified first-hand.

## 4. Verification log

Times are Asia/Ho_Chi_Minh, 22 November 2026. Work ran about 14:36 to
14:58 +07. No live runs, no browser work, no shared code changed.
Read-only git show, git archive, and git grep against
origin/todolist-push at 8c6553a, plus local scripts over the extracted
JSONs and PNGs. The extraction first went to /tmp, which was wiped
mid-task by the environment, so it was redone under ~/.redteam13 and
all checks were run there. No shared repo file was modified except this
report.

- 14:36: fetched origin. Local main at f5e36e7. todolist-push at
  8c6553a. Diff 3167c76 to 8c6553a for reviewed files is empty.
- 14:37: read the task 2 report (607 lines) and the (b1) spec (571
  lines) in full. Extracted the code, logs, run JSONs, and PNGs from
  origin/todolist-push.
- 14:40: recomputed all section 2.2 numbers from the 19 JSONs. All
  match, except the p9 field: every JSON carries p9 as an object, not
  null. This produced R1.
- 14:44: verified the 25 PNGs against the manifest section-aware
  (sha256, size, PNG magic): 25 of 25. Verified the focusenter
  helper bytes, lines, and sha256. Verified p9 was an object from the
  first commit of run-1.json (4bd6292).
- 14:48: verified every line citation in section 2.1, the F3 code
  readings in dom_act.py and dom_asserts.py, the F4 sources in the
  logs, and the F5 to F13 evidence. Found R2 (double_click) and R3
  (assert polling assumption).
- 14:55: verified the method claims (diffs, commit contents, dash
  count, commit times). Wrote this report, committed only this file,
  pushed to origin/main.

## 5. What this redteam did not do

- No shared code was changed. No edits to coord/clone1.md or
  coord/clone2.md. The untracked 0-byte test-w.txt was left alone.
- No live runs and no browser work. No PNG pixel was viewed: the PNG
  verification covers sha256, byte size, and PNG magic against the
  manifest, and the manifest's "what the frame shows" column was not
  re-checked by viewing frames.
- No council, fix pass, or second review. Those follow under the
  batch 13 brief.
