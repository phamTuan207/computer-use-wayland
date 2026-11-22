# Batch 13 council 2: review of the batch 13 task 2 (b1) spec review

## 0. Verdict: AMEND STANDS, with one material correction and three minor notes

I re-verified the task 2 report
(docs/batch13-task2-b1-spec-review-20261122.md, commit f5e36e7,
verdict AMEND) first-hand against the code at todolist-push HEAD
8c6553a and the cited commits. The AMEND verdict stands: F1 and F2
are real staleness, F3 is a real design hole, F4 is a real
acceptance-criterion error, and F5 to F10 are real. But the report
contains one material error of its own, and the fix pass must not
apply it:

- C-2 (MEDIUM): the F2 note claiming "the run JSONs still carry p9
  as null in every JSON" is false. All 19 run JSONs carry a
  non-null p9 object naming the PNG paths, since commit 4bd6292,
  before the spec base. The F2 fix instruction is inverted and
  must be reversed: the spec fix should say the JSONs name the
  PNGs, not that the paths come from the audit repair-list
  filename convention.

The three minor notes are C-1 (the report's own section 2.1 has a
range slip of the same class it flagged in F9, on key()), C-3 (the
F3 fix list omits double_click), and C-4 (the F4 derivation does
not subtract the removed value assert, which does not change the
ranges). None of the four changes the AMEND verdict. No shared
code was changed by this council. Report only.

## 1. Scope and method

- Report reviewed: docs/batch13-task2-b1-spec-review-20261122.md,
  commit f5e36e7, 607 lines.
- Spec reviewed by task 2: docs/batch12-task2-b1-landing-spec-
  20261122.md on origin/main, 571 lines, including fix pass
  commit 20f3b99.
- Review HEAD: origin/todolist-push 8c6553a. I checked the diff
  between 3167c76 (task 2 review HEAD) and 8c6553a for every file
  listed below: empty. I also checked the diff between the spec
  base 4305dcb and 3167c76 for those files: empty. All findings
  hold at 8c6553a.
- Code read first-hand, read-only, from origin/todolist-push with
  `git show` (the branch was never checked out and never
  modified): scripts/cdp.mjs (641 lines), scripts/code_exec.py
  (1297 lines), scripts/cu.py (3465 lines), scripts/dom_asserts.py
  (227 lines), scripts/dom_act.py (866 lines),
  scripts/s2_flip_live.py (812 lines), scripts/element_ref.py
  (293 lines), scripts/action_result.py,
  tests/test_s2_flip_wiring.py (244 lines),
  tests/cdp_validation.mjs (133 lines), tests/test_step5_p1p5.py,
  tests/test_dom_act.py.
- Evidence read first-hand from the same branch:
  improvements/s2-flip-b1-runs/run-1..5.json and
  run-2..5-aborted.json, improvements/s2-flip-reopen-runs/
  run-1..5.json, improvements/s2-flip-runs/run-1..5.json,
  improvements/s2-flip-b1-runs/c5-focusenter.mjs,
  improvements/s2-flip-p9-manifest.md,
  improvements/worker-click5-input-fix-log.md (commit 4bd6292),
  improvements/worker-click5-s2-reopen-log.md (commit 1a3356d),
  improvements/worker-click4-s2-flip-log.md.
- Every number in section 2 was recomputed from the run JSONs
  with a script, not copied from the logs. Every line citation in
  section 2 was checked with grep or direct read at HEAD 8c6553a.
- The 25 P9 PNGs were verified by sha256, byte size, and PNG
  magic, and 2 of the 25 frames were viewed directly to check
  the manifest content rows.
- Rules kept: no personal information anywhere, no long dashes,
  no ydotool, real numbers only, all verified first-hand.

## 2. Verdict per finding

### F1 (HIGH, stale): AGREE

The helper is in the repo. I read it first-hand at HEAD 8c6553a:
improvements/s2-flip-b1-runs/c5-focusenter.mjs, 2478 bytes, 42
lines, sha256
94ee467ed3067e044491ad19153c24b73d574a8106a5367db454c0e47e1a695f,
matching the manifest row exactly, committed in 3ef8f55
("C5-P9-EVIDENCE: commit 25 P9 screenshots plus manifest and
focusenter helper", 28 files changed). Its semantics match the
report: missing textarea returns {focused: false, error:
'no-textarea'}; focus failure throws 'composer did not gain
focus'; no unavailable-field checks; returns {ok, focus, enter}.
Section 10 item 1 and the section 1 item 2 "laptop-only helper"
wording are stale. The reopen log section 8 line listing laptop
helpers "not in the repo" is stale in the same way for
focusenter (it names /tmp/c5-focusenter.mjs among the laptop
helpers); it stays true for the other four files listed there.

### F2 (HIGH, stale): AGREE on the core, DISAGREE on the p9-null note

Core: AGREE. All 25 P9 PNGs are on todolist-push, committed in
3ef8f55. I verified all 25 independently against the manifest
with a section-aware script: sha256, byte size, and PNG magic
all match on 25 of 25 rows, zero mismatches. Subtotals check:
5 (b1) PNGs 1,210,605 bytes; 10 reopen PNGs 2,354,937 bytes; 10
original flip PNGs 2,740,488 bytes; total 6,306,030 bytes.
No extra PNG sits on disk beyond the 25 listed, none listed is
missing. I also viewed 2 frames directly: (b1) p9-run1-chromium.png
shows the test bubble C5-B1-R1-CHROMIUM-IGNORE-TEST with the
composer empty, and flip p9-run1-chromium.png shows no test
bubble at the earlier scroll position, both matching the
manifest content rows exactly. Section 10 item 11 is stale and
must be struck.

Note: DISAGREE, see C-2. The run JSONs do not carry p9 as null.
Every one of the 19 run JSONs (5 (b1) completed, 4 (b1)
aborted, 5 reopen, 5 flip) carries a non-null p9 object naming
the PNG path per browser, with ok true and a wall_ms. Example:
(b1) run-1.json p9 is {"chromium": {"ok": true, "png":
"improvements/s2-flip-b1-runs/p9-run1-chromium.png", "wall_ms":
3637.2}}. The field has been populated since commit 4bd6292,
which created run-1.json, before the spec base 4305dcb. The
manifest auditor note the report repeats is wrong in the same
way. The fix pass must not write the report's sentence about
the audit repair-list filename convention into the spec.

### F3 (HIGH, design): AGREE

The spec section 5 list is wrong about `type`. In dom_act.py
focus_type (lines 664 to 712), the docstring says "Click an
input, type, and verify", and the chain built at lines 708 to
712 is [click, type, key Enter]. The click establishes focus;
the type step types into the field the click already focused.
In dom_asserts.py the ASSERTS table maps 'type' to type_check
(lines 60 to 62), not to focus_check. In cdp.mjs there is no
`type` action at all: the whitelist at line 434 is
['click','confirm_click','hover_click','fill','set_value','key',
'scroll','wait','assert']. A batch [type, key Enter, assert]
with no preceding click would pass the spec rule yet fail
silently the same way [set_value, key Enter] does. No such
batch exists today (focus_type always includes the click), so
the hole is latent, not live. The proposed fix wording is
sound, with one gap, see C-3.

### F4 (HIGH, acceptance criterion): AGREE

Both errors verified first-hand:

(a) The 17 to 25 ms figure is the Enter time, not the focus
time. In the run JSONs the helper reports enter.ms of 17, 18,
20, 23, 23 ms for the (b1) runs and 21, 23, 23, 25, 25 ms for
the reopen runs. The helper source times only the two
dispatchKeyEvent calls (t0 before keyDown, ms after keyUp);
the focus evaluate is never timed separately. The helper total
focus_enter.ms (1244.8 to 1338.5 ms for (b1), 1310.5 to 1484.6
ms for reopen) is wall time including transport, not focus
time.

(b) The 17 to 25 ms figures are live measurements, while the
dry run runs on scratch tabs, where Enter measured 2 ms
(input-fix log section 7.4: "focus_enter ok True (focused
TEXTAREA, Enter 2ms)"; the D-B1 probe in section 7.1 also
measured 2 ms, on Shift, not Enter, as the report notes).

The corrected ranges check out arithmetically from the same
sources. Dry run: baseline 85.8 ms (reopen log section 3) plus
focus about 2 to 3 ms (flip log section 5 run 1: "each evaluate
2-3ms") plus Enter on scratch about 2 ms plus assert polling
about 0 to 10 ms (assertAction polls every 10 ms, cdp.mjs
lines 415 to 427) gives 89.8 to 100.8 ms, so about 90 to 100
ms is right. Live: (b1) program elapsed 91.575 to 106.622 ms
plus focus about 2 to 3 ms plus live Enter 17 to 25 ms plus
assert polling about 0 to 10 ms gives 110.575 to 144.622 ms,
so about 110 to 145 ms is right. The spec gives no live
elapsed expectation at all; section 9 step 6 should state one.
See C-4 for a small refinement that does not change the ranges.

### F5 (MEDIUM): AGREE

hover_click is in the cdp.mjs whitelist (line 434) and in the
code_exec.py allowed set (line 217), but it is NOT in the cu.py
browser allowed set (line 1299: click, confirm_click, fill,
set_value, key, scroll, wait, assert). A grep for hover_click
across cu.py at HEAD 8c6553a returns zero matches. The browser
element-action check at cu.py line 1341 also omits hover_click.
The three-way mirror already drifts today on one action type.
The spec section 5 edit list names all three files, so no edit
is missing, but the landing must verify the three whitelists
agree for focus instead of assuming the pattern.

### F6 (MEDIUM): AGREE

The helper, read first-hand, performs no unavailable-field
checks, throws 'composer did not gain focus' on focus failure
(not the fill wording 'field is not editable or did not gain
focus'), and returns {ok, focus, enter} (not a bare ok). Spec
section 4 step 2 (unavailable-field checks, borrowed from the
set_value branch, cdp.mjs line 478), step 4 (fill error wording,
cdp.mjs line 537), and step 5 (return ok) are design additions,
not helper replication. The section 4 intro wording
"replicating /tmp/c5-focusenter.mjs" must be qualified.

### F7 (MEDIUM): AGREE

Verified from the committed helper and cdp.mjs lines 390 to
414. (a) The helper sends code 'Enter' on both keyDown and
keyUp. The landed key() never sends a `code` field for any key;
its params are key, modifiers, windowsVirtualKeyCode, and
nativeVirtualKeyCode only. (b) The helper sends text '\r' on
keyDown only; its keyUp carries no text. The landed key() sets
params.text '\r' at line 410 and sends the same params object
for keyDown (line 411) and keyUp (line 412). Both differences
are probably harmless, as the report says, but the landing
must record the decision rather than change the wire params
silently.

### F8 (LOW): AGREE

The dispatch chain in cdp.mjs is an else-if over distinct
action types (lines 471 to 545). Branch position is irrelevant
to execution order; the action list order decides. "It must sit
between set_value and key in the chain" is misleading as a
requirement and should be softened to a style suggestion.

### F9 (LOW): AGREE

Both slips verified. The _api_dom_act require_asserts call in
code_exec.py spans lines 936 to 939; it closes on line 939 with
'sent_bubble': False. The click function in cdp.mjs spans lines
292 to 314; the three dispatchMouseEvent calls are on lines 311
to 313 and the closing brace is on line 314.

### F10 (MEDIUM): AGREE in substance

I checked each item against the spec and the code:

(a) Spec section 8 lists a focus test for the unavailable-field
error only, not for the focus-failure error wording from
section 4 step 4. Missing as stated.
(b) Spec section 8 says "focus resolves a ref through
pageState"; no selector-resolution focus test is listed.
Missing as stated.
(c) test_program_without_trailing_assert_would_fail_p5
(tests/test_s2_flip_wiring.py lines 189 to 198) uses the fill
shape only, not the landed [set_value, focus, key Enter]
shape. Missing as stated.
(d) require_asserts raises on unknown action types
(dom_asserts.py lines 185 to 227, an entry of None adds an
'unknown action' message), so a failing-first anchor for the
dom_asserts change is possible and is not in the spec.
Missing as stated.
(e) Follows from F3; the two test shapes named are the right
ones, see C-3 for the double_click gap.
(f) The three browser whitelists are cdp.mjs line 434,
code_exec.py line 217, and cu.py line 1299. A sync test is
possible and is not in the spec. Missing as stated.
(g) tests/cdp_validation.mjs line 6 slices the source between
'async function key(' and 'async function assertAction(', which
does not apply to focus, because the focus branch lives inline
in the handle() dispatch loop. The harvest test in the same
file uses a whole-adapter vm run with a fake page carrying
globalThis.__agentCu, refs, and an activeElement stub (lines 51
to 59, 83). The clarification is accurate.

### F11 (NOTE, confirmed no gap): AGREE

element_ref.validate_action_binding (lines 146 to 164) checks
observation_id and scope only and is type-agnostic.
action_result.py line 33 re-exports DOM_ASSERT_EXCEPTIONS (the
file also defines build_contract, which the new ASSERTS entry
does not touch). test_step5_p1p5.py contains zero matches for
'focus', so its AssertSetTests chains cannot change. No fourth
file is missing from the section 5 edit list.

### F12 (NOTE): AGREE, items 2 to 10 stand

- Item 2 stands: /tmp/c5-count.mjs is still not in the repo. A
  tree listing grep for c5-count returns zero matches.
- Items 3 to 6 stand: the coordinator has not picked option A
  or B in any commit I read (the batch 12 summary in
  coord/clone1.md recommends option A; a recommendation is not
  a decision); no focus-action test exists (the 'focus' matches
  in tests/test_s2_flip_wiring.py are one comment plus three
  focus_check availability maps, and in tests/cdp_validation.mjs
  they are the harvest test only); no live proof of landed code
  exists; the laptop tree sync and relay-restart question are
  still unverified.
- Item 7 stands: the 80-element cap is cdp.mjs lines 83 to 84,
  and all 5 reopen Chromium runs ran relaxed
  (routing_relaxed true, observe truncated true, 80 elements,
  verified from the JSONs).
- Items 8, 9, 10 stand: the mouse stall is unsolved; the Brave
  decision is open; the shadow-root activeElement walk is a
  follow-up.

### F13 (NOTE): AGREE, the dry-run baseline is log-only

No run-0 JSON exists in improvements/s2-flip-reopen-runs/ on
the branch: the directory holds only run-1..5.json plus the P9
PNGs. The baseline (wall 30123.9 ms, Chromium elapsed 85.8 ms,
completed 2) rests on reopen log section 3 prose only, and the
dry-run workdir was /tmp/s2-reopen-dry, so the JSON was never
in the repo. One sentence in section 8 should say so.

## 3. Council corrections: errors and gaps in the task 2 report

### C-1 (LOW, error in the report): key() is cdp.mjs 390 to 414, not 390 to 412

The report section 2.1 says "cdp.mjs:390 to 412, key. The text
'\r' for Enter is line 410. Correct." The function actually
spans lines 390 to 414: the for loop closes on line 413 and the
function closes on line 414, with async function assertAction
starting on line 415. The two dispatchKeyEvent calls are on
lines 411 and 412, inside the cited range, and the text '\r'
is on line 410, so the substantive claim is true and only the
closing braces fall outside. This is the same class of slip the
report flags in F9 against the spec, and the report's "all
exact" claim for section 2.1 is overstated by this one range.
Fix the range to 390 to 414. No spec text depends on it.

### C-2 (MEDIUM, error in the report): the run JSONs do NOT carry p9 as null

The F2 note says "the run JSONs still carry p9 as null in every
JSON, so the PNG paths come from the audit repair-list filename
convention, as the manifest records". That is false at the
review HEAD, false at the spec base, and false now. I checked
all 19 run JSONs on todolist-push HEAD 8c6553a: every one
carries a non-null p9 object naming the PNG path per browser,
with ok true and a wall_ms. (b1) run-1.json p9 is {"chromium":
{"ok": true, "png": "improvements/s2-flip-b1-runs/p9-run1-
chromium.png", "wall_ms": 3637.2}}. The reopen JSONs name both
browsers, for example reopen run-1.json names p9-run1-brave.png
and p9-run1-chromium.png. The aborted JSONs name the same PNGs
as their completed counterparts. The p9 field has been
populated since commit 4bd6292, which created run-1.json; I
confirmed the same non-null value at 3ef8f55^, at the spec base
4305dcb, and at the review HEAD 3167c76. The task 2 reviewer
repeated the manifest auditor note without checking the field.
Consequence: the F2 fix instruction is inverted. The fix pass
must NOT write into the spec that the paths come from the audit
repair-list convention; it should say the run JSONs name the
PNGs directly. The manifest auditor note is wrong in the same
way and should be corrected where it is cited, not repeated.
This does not change the F2 core (the PNGs are in the repo) or
the AMEND verdict.

### C-3 (LOW, gap in the F3 fix): the proposed list omits double_click

The F3 fix proposes exempting batches containing "click,
confirm_click, hover_click, fill, or the new focus" before the
send key. It omits double_click, which dom_asserts.py maps to
focus_check (lines 51 to 53) and which cu.py allows on the
desktop path. A desktop batch [double_click, type, key Enter]
establishes focus but would raise under the proposed wording.
Define "focus-establishing" through the ASSERTS table instead
(any action whose assert is focus_check) rather than a hardcoded
list, or add double_click to the list. Either way the rule
cannot drift from the table again.

### C-4 (LOW, refinement to F4): the derivation does not subtract the removed value assert

The corrected derivation adds focus (about 2 to 3 ms), Enter,
and assert polling to the 85.8 ms baseline, but the landed
4-action program drops the value assert the baseline program
carried. That assert is one Runtime.evaluate on success, about
2 to 3 ms, so the corrected ranges shift down by about that
much and the focus evaluate adds about the same back. Net
effect is about zero, and the ranges about 90 to 100 ms
dry-run and about 110 to 145 ms live still hold. No change to
the numbers is needed; record the wash so the fix pass does
not re-derive it as an error.

### C-5 (NOTE, gap closed in part): the task 2 report did not view any frame

The task 2 report verified the PNGs by sha256, byte size, and
PNG magic only. I spot-viewed 2 of the 25 frames directly: (b1)
p9-run1-chromium.png shows the test bubble with the composer
empty, and flip p9-run1-chromium.png shows no test bubble at
the earlier scroll position. Both match the manifest content
rows exactly, including the negative case. The other 23 frames
remain hash-verified only. No disagreement follows; the sample
supports the manifest.

## 4. What the fix pass must and must not do

Must do: strike spec section 10 items 1 and 11; reword the
section 5 send-requires-focus rule per F3 with the C-3
double_click fix; rewrite the section 8 elapsed paragraph and
the section 11 criterion per F4 (dry-run about 90 to 100 ms)
and add the live re-run criterion of about 110 to 145 ms to
section 9 step 6; apply F5, F6, F7, F8, F9, and F10; fix the
key() range to 390 to 414 if the spec cites it (C-1 is a report
error, not a spec error, so this is for the report record, not
the spec).

Must not do: do not apply the F2 note as written. Do not write
into the spec that the PNG paths come from the audit
repair-list filename convention, and do not write that the run
JSONs carry p9 as null. The JSONs name the PNGs directly.

After the fix pass, the spec can land without a second full
review, provided the fix pass re-checks F3 and F4 against the
code, as the task 2 report recommends.

## 5. Verification log

Times are Asia/Ho_Chi_Minh, 22 November 2026. Work ran about
14:37 to 14:47 +07. No live runs, no browser work, no shared
code changed. Read-only `git show`, `git grep`, and `git
archive` against origin/todolist-push, plus local scripts over
the extracted JSONs and PNGs. One early exec result carried an
execution-risk flag, but its content was only git log text; I
did read-only text inspection and ran no repo code.

- 14:37: fetched origin/main and origin/todolist-push. Local
  main at f5e36e7 (the task 2 report commit). todolist-push at
  8c6553a, matching the brief note.
- 14:38: read the task 2 report (607 lines) and the spec (571
  lines) in full. Extracted the 12 code and test files plus the
  3 logs, the focusenter helper, and the manifest from
  origin/todolist-push to /tmp for read-only checking.
- 14:39: verified the helper (2478 bytes, 42 lines, sha256
  match) and the 25 PNGs (sha256, size, PNG magic, 25 of 25,
  zero mismatches; subtotals 1,210,605, 2,354,937, 2,740,488;
  total 6,306,030). Found the p9-null note false: all 19 run
  JSONs carry non-null p9, populated since 4bd6292. Produced
  C-2.
- 14:40 to 14:44: recomputed all section 2.2 numbers from the
  15 run JSONs plus 4 aborted JSONs. All match the spec except
  the F4 derivation, which the report already flags. Verified
  every line citation in section 2.1 with grep and direct reads.
  Found the key() range slip (390 to 414, not 390 to 412).
  Produced C-1.
- 14:44: verified the hover_click drift, the F3 chain, the F7
  param differences, the F9 slips, the F10 test gaps, the F11
  file list, and the F12 and F13 notes. Found the double_click
  gap in the F3 fix. Produced C-3, C-4, C-5.
- 14:45: spot-viewed 2 PNG frames; both match the manifest
  content rows exactly.
- 14:46: confirmed the diffs 4305dcb to 3167c76 and 3167c76 to
  8c6553a are empty for all reviewed files, so every finding
  holds at 8c6553a.
- 14:47: wrote this report to
  docs/batch13-council2-task2-20261122.md, committed only that
  file, pushed to origin/main.

## 6. What this council did not do

- No shared code was changed. No edits to coord/clone1.md or
  coord/clone2.md. The untracked 0-byte test-w.txt was left
  alone.
- No live runs and no browser work. The corrected elapsed
  ranges in F4 are estimates from the existing measurements,
  stated as ranges with their components, not as new
  measurements.
- No redteam or fix pass. Those follow under the batch 13
  brief. This council did not read council 1's report; its
  verdicts are first-hand.
