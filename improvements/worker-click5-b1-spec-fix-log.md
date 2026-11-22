# Worker log: C5-B1-SPEC-FIX, fix the (b1) landing spec per batch 13 task 2 review

- Worker: C5-B1-SPEC-FIX, reporting to COORD-CLICK-5 only. Independent fix pass. I did not write the (b1) landing spec and I did not review it.
- Task: apply every finding F1 to F13 from docs/batch13-task2-b1-spec-review-20261122.md (verdict AMEND) to docs/batch12-task2-b1-landing-spec-20261122.md.
- Spec commits on main: 3962400 (F1 to F10) and eab0228 (F2 follow-up, all 25 P9 frames pixel-viewed by the CB-8 re-audit). Both pushed to origin/main and verified with git ls-remote.
- Branches: spec edited in ~/workspace/cu-jpegq90-land on main; this log committed on todolist-push in ~/workspace/computer-use-wayland.
- No live runs, no browser work, no code changes. Doc fix only.
- No em dash or en dash anywhere in this file.

## Time log (wall-clock Asia/Ho_Chi_Minh)

- 15:24 +07 (T+0 min): task received. Fetched origin/main and origin/todolist-push in both work trees.
- 15:24 to 15:26 +07 (T+0 to 2 min): read the spec (571 lines) and the review in full.
- 15:25 +07 (T+1 min): verified commit 3ef8f55 on todolist-push (28 files: 25 P9 PNGs, manifest, focusenter helper, log). Read the committed helper (42 lines, 2478 bytes, sha256 94ee467ed3067e044491ad19153c24b73d574a8106a5367db454c0e47e1a695f) and the manifest in full.
- 15:25 to 15:26 +07 (T+1 to 2 min): extracted code, run JSONs, and logs from origin/todolist-push at HEAD 704a218 with git archive to /tmp/b1fix for read-only checking. Recomputed all F4 numbers from the run JSONs with a script. Verified every line citation used below with grep or direct read.
- 15:26 +07 (T+2 min): confirmed the reviewed files are unchanged between review HEAD 3167c76 and todolist-push HEAD 704a218 (git diff --quiet, empty).
- 15:26 to 15:28 +07 (T+2 to 4 min): applied the F1 to F10 edits to the spec. Checked the file for em/en dash (0 of each) and for stale phrases (none left).
- 15:28 +07 (T+4 min): committed the spec fix as 3962400 on main, pushed, verified with git ls-remote (39624009b4bd33d08724cdd2799cbd01a30503ec).
- 15:28 to 15:29 +07 (T+4 to 5 min): while writing this log, found the CB-8 re-audit commit 84cc31f on todolist-push (landed 15:26 to 15:27 +07, after the review): it viewed all 25 P9 PNGs itself. The F2 text in 3962400 ("hash-level only for 23 of the 25 frames; 2 frames pixel-viewed") was already stale at current HEAD, so I corrected it in the spec (section 7 and section 10 item 11) before this log was committed. See the F2 follow-up entry below.
- 15:29 +07 (T+5 min): committed the F2 follow-up as eab0228 on main, pushed, verified with git ls-remote (eab02280d0647df2899466a875ef587390ac176c). Wrote this log.
- Total elapsed about 6 minutes. No 15-minute stall at any point.

## Verification commands and outputs (Lauren Tan standard)

- `git show --stat 3ef8f55`: 28 files, including improvements/s2-flip-b1-runs/c5-focusenter.mjs (42 lines) and 25 P9 PNGs plus improvements/s2-flip-p9-manifest.md. Confirms F1 and F2 evidence commit.
- `git show origin/todolist-push:improvements/s2-flip-b1-runs/c5-focusenter.mjs | sha256sum`: 94ee467ed3067e044491ad19153c24b73d574a8106a5367db454c0e47e1a695f, 42 lines, 2478 bytes. Matches the manifest exactly.
- Run JSON recompute (script over the extracted JSONs, fields browsers.chromium.program.elapsed_ms, browsers.chromium.focus_enter.enter.ms, browsers.chromium.cb1.completed, browsers.chromium.pre_count.count, top-level delayed_count.chromium.count, browsers.chromium.v12.attempts, browsers.chromium.v12.elapsed_ms): (b1) elapsed 91.575 to 106.622 ms, enter.ms 17, 18, 20, 23, 23; reopen elapsed 99.412 to 113.005 ms, enter.ms 21, 23, 23, 25, 25; walls median 18839.7 ms (b1) and 28560.9 ms (reopen); pre_count 0 and delayed_count 1 in all 10 runs; V12 attempts 1, elapsed_ms 2 to 4 ms; aborted walls 12365.3, 14372.5, 12652.1, 13734.2 ms. All match the spec section 0.
- p9 field check: 24 run JSONs (5 a1, 5 (b1), 4 aborted, 10 reopen, 5 flip), 34 p9 entries, zero null. Each p9 entry is a dict with ok true, a png path, and wall_ms. Confirms the review F2 note 1: the manifest auditor note saying p9 is null is wrong.
- `git ls-tree -r --name-only origin/todolist-push | grep -c "c5-count"`: 0. Confirms F12 item 2 stands.
- `git ls-tree -r --name-only origin/todolist-push | grep "\.png$"`: 25 manifest PNGs in the three s2-flip dirs, plus 5 unrelated PNGs (benchmark paint images, fixtures). The 5 a1 PNGs are named by their run JSONs but are not in the repo.
- `grep -c hover_click scripts/cu.py`: 0. Confirms F5.
- `git diff --quiet 3167c76 origin/todolist-push -- <reviewed files>`: empty, so all findings hold at the verification HEAD 704a218. Re-checked after the branch moved to 0b59d9f: `git diff --quiet 704a218 0b59d9f -- <reviewed files>` is also empty, so the verification holds at 0b59d9f as well.
- Spec file checks after editing: em dash 0, en dash 0; no remaining "105 to 115", "nearest preceding value action", "must sit between", or "mirror already exists" wording. The two remaining "laptop-only helper" hits are the /tmp/c5-count.mjs helper, which is still laptop-only (F12 item 2 stands).
- Spec diff: 3962400 changed 1 file, 290 insertions, 69 deletions; eab0228 changed 1 file, 20 insertions, 14 deletions.

## Per-finding record

### F1 (HIGH, stale): section 10 item 1, focusenter helper now in repo

- What changed: section 10 item 1 rewritten from open to CLOSED. Section 1 item 2 reworded from "a laptop-only helper" to committed evidence. Section 4 intro now cites the committed file as the reconstruction basis instead of the log description alone. Section 0 notes the helper source is committed but the shape is still not landed code.
- Exact new wording (section 10 item 1): "CLOSED by the fix pass (review F1). The /tmp/c5-focusenter.mjs source IS in the repo: improvements/s2-flip-b1-runs/c5-focusenter.mjs, commit 3ef8f55, 42 lines, 2478 bytes, sha256 94ee467ed3067e044491ad19153c24b73d574a8106a5367db454c0e47e1a695f. Its semantics match the input-fix log section 7.3 description: Runtime.evaluate focus on textarea[aria-label="Message"], assert it is document.activeElement, then Input.dispatchKeyEvent keyDown plus keyUp Enter, zero mouse events, returns {ok, focus, enter}."
- Source: improvements/s2-flip-b1-runs/c5-focusenter.mjs at commit 3ef8f55, read first-hand (42 lines, 2478 bytes, sha256 above, matching the manifest row exactly). The "if the laptop file is gone" recovery clause is recorded as moot for focusenter.

### F2 (HIGH, stale): section 10 item 11, P9 PNGs now in repo

- What changed: section 10 item 11 rewritten from open to CLOSED. Section 7 P9 bullet extended with the committed evidence. Section 9 step 7 now requires the landing verification log to repeat the flip-PNG warning.
- Exact new numbers (section 10 item 11): 5 (b1) Chromium PNGs (1,210,605 bytes), 10 reopen PNGs (2,354,937 bytes), 10 original flip PNGs (2,740,488 bytes), 6,306,030 bytes total; run JSONs name the PNGs directly through the p9 field, 34 entries across all 24 run JSONs in the s2-flip-* directories, zero null; manifest paths agree with JSON paths on all 25 rows.
- Source: commit 3ef8f55 (28 files) and improvements/s2-flip-p9-manifest.md, read first-hand; p9 field verified first-hand in all 24 run JSONs (5 a1, 5 (b1), 4 aborted, 10 reopen, 5 flip). The manifest auditor note saying the run JSONs carry p9 as null is recorded in the spec as wrong and must not be repeated. The spec does NOT say the PNG paths come from the audit repair-list filename convention.
- F2 follow-up (found during this fix pass, after commit 3962400): the review's fix-pass record said 2 frames were pixel-viewed and 23 hash-verified only. That was already stale at todolist-push HEAD 0b59d9f. The CB-8 re-audit worker viewed all 25 PNGs itself at 15:25 to 15:26 +07 on 22 November 2026 (commit 84cc31f, improvements/worker-click5-cb8-reaudit-log.md), each frame matching its manifest row and its JSON message, and reinstated both revoked claims. I corrected section 7 and section 10 item 11 in commit eab0228 to state all 25 frames were pixel-viewed by that independent re-audit. The 5 original flip Chromium PNGs show no test bubble in all five frames (same earlier scroll position), which agrees with their JSON outcome failed-unverified; they must not be cited as send evidence. Precision note kept: the 5 a1 PNGs are named by their run JSONs but are not in the repo; they are not part of the 25 manifest rows.

### F3 (HIGH, design): section 5 lists `type` as focus-establishing, it is not

- What changed: the send-requires-focus rule in section 5 rewritten. The old wording ("nearest preceding value action is set_value", "fill, click, confirm_click, hover_click, and type are focus-establishing actions") is gone. The new rule: a send key (per _is_send_key, scripts/dom_asserts.py lines 96 to 114) with no preceding focus-establishing action in the same batch raises DomAssertError. "Preceding" means before the send key in the same batch. "Focus-establishing" is defined through the ASSERTS table: any action whose ASSERTS entry is focus_check (click, double_click, confirm_click, hover_click, scripts/dom_asserts.py lines 48 to 59), plus the new focus action (focus_check), plus fill as an explicit exception.
- Exact new wording on fill: "Fill is the one action the table definition alone would wrongly exclude: its ASSERTS entry is type_check (dom_asserts.py lines 63 to 65), but it focuses through its internal click (scripts/cdp.mjs:535, await click(a), then the activeElement check on line 536), so a literal ASSERTS-only wording would wrongly reject [fill, key Enter] and break the existing passing shape [fill, key Enter, assert]."
- Outcomes now pinned in the spec: [set_value, key Enter] raises; [click, type, key Enter] passes; [double_click, type, key Enter] passes; [fill, key Enter] passes; [type, key Enter] raises; [set_value, focus, key Enter] passes. The spec now states `type` establishes no focus (in dom_act.py focus_type, lines 664 to 712, the click establishes focus and the chain at lines 708 to 712 is [click, type, key Enter]) and there is no `type` action at all in cdp.mjs (whitelist line 434).
- Sources verified first-hand: scripts/dom_asserts.py lines 48 to 59 (click 48, double_click 51, confirm_click 54, hover_click 57, all focus_check), lines 60 to 68 (type, fill, set_value all type_check); scripts/cdp.mjs line 434 (whitelist, no type) and lines 534 to 537 (fill: await click(a), activeElement check, error wording); scripts/dom_act.py lines 664 to 712 (focus_type docstring and chain); scripts/cu.py lines 2048 to 2054 (double_click does two presses).

### F4 (HIGH, acceptance criterion): section 8 and section 11 dry-run elapsed wrong

- What changed: the section 8 elapsed paragraph rewritten with the corrected derivation; the dry-run criterion changed from about 105 to 115 ms to about 90 to 100 ms; a live re-run criterion of about 110 to 145 ms added to section 9 step 6 and to section 11.
- Exact new numbers and derivation (section 8): baseline 85.8 ms (reopen log section 3) plus focus evaluate about 2 to 3 ms (one Runtime.evaluate) plus Enter on scratch about 2 ms plus trailing bubble assert polling about 0 to 10 ms minus the dropped value assert about 2 to 3 ms, which is 86.8 to 98.8 ms, stated as about 90 to 100 ms.
- Exact new numbers and derivation (section 9 step 6, live): live (b1) program elapsed 91.575 to 106.622 ms plus focus about 2 to 3 ms plus live Enter 17 to 25 ms plus assert polling about 0 to 10 ms minus the dropped value assert about 2 to 3 ms, which is 107.6 to 142.6 ms, stated as about 110 to 145 ms.
- What was wrong, stated in the spec: the 17 to 25 ms figure is the ENTER time, not the focus time (field browsers.chromium.focus_enter.enter.ms: 17 to 23 ms for the (b1) runs, 21 to 25 ms for the reopen runs, measured around the two dispatchKeyEvent calls only; the focus evaluate was never timed separately), and it is a LIVE measurement while the dry run runs on scratch tabs, where Enter measured 2 ms (input-fix log section 7.4: "focus_enter ok True (focused TEXTAREA, Enter 2ms)").
- Sources for every corrected number: browsers.chromium.program.elapsed_ms (91.575 to 106.622 ms (b1), 99.412 to 113.005 ms reopen); browsers.chromium.focus_enter.enter.ms (17 to 23 ms (b1), 21 to 25 ms reopen); assertAction polls every 10 ms, scripts/cdp.mjs lines 415 to 426, returns on first passing poll line 422; value-assert evaluate about 2 to 3 ms (flip log records Runtime.evaluate at 1 to 3 ms and V12 elapsed at 2 to 3 ms); set_value internal verification scripts/cdp.mjs lines 517 to 518, repeated at 528. Caveat recorded: the 0 to 10 ms component assumes the bubble is present at the first poll; no cited measurement bounds post-Enter bubble render latency on a scratch tab, so the landing must measure it (one Runtime.evaluate loop after the Enter) or widen the dry-run range.
- Section 0 labels also corrected to prevent the same misreading: "helper Enter 17 to 23 ms (field browsers.chromium.focus_enter.enter.ms)" and "helper Enter 21 to 25 ms (field browsers.chromium.focus_enter.enter.ms)", with program elapsed cited to browsers.chromium.program.elapsed_ms.

### F5 (MEDIUM): section 3 mirror claim false for hover_click

- What changed: the sentence "the mirror already exists for every other action type" is gone. Section 3 now records the hover_click drift as a known pre-existing drift, not something this landing fixes, and requires the landing to verify the three whitelists agree for focus instead of assuming the pattern.
- Exact new wording: "hover_click is in the cdp.mjs whitelist (line 434) and in the code_exec.py allowed set (line 217), but it is NOT in the cu.py browser allowed set (line 1299) and NOT in the cu.py browser element-action check (line 1341); a grep for hover_click across cu.py returns zero matches."
- Source: grep -c hover_click scripts/cu.py returned 0; scripts/cdp.mjs line 434 and scripts/code_exec.py line 217 both list hover_click; scripts/cu.py line 1299 (browser allowed set: click, confirm_click, fill, set_value, key, scroll, wait, assert) and line 1341 (element-action check list) both lack it.

### F6 (MEDIUM): section 4 frames design additions as replication of the helper

- What changed: section 4 intro now cites the committed helper as the basis, cross-checked against the log description, and labels steps 2, 4, and 5 as design additions, one sentence each. The intro also states what the helper actually does.
- Exact new wording: step 2 "Design addition borrowed from the set_value branch, not helper behavior."; step 4 "Design addition borrowed from fill, not helper behavior: the helper throws 'composer did not gain focus' instead."; step 5 "Design addition: a deliberate narrowing of the helper's {ok, focus, enter} shape to the focus step alone, since the Enter becomes a separate key action in the landed program."; intro: "if the textarea is missing it returns {focused: false, error: 'no-textarea'}; on focus failure it throws 'composer did not gain focus'; it performs no unavailable-field checks."
- Source: committed helper read first-hand (improvements/s2-flip-b1-runs/c5-focusenter.mjs, lines: missing textarea returns {focused: false, error: 'no-textarea'}; focus failure throws 'composer did not gain focus'); set_value unavailable-field checks scripts/cdp.mjs line 478; fill error wording scripts/cdp.mjs line 537.

### F7 (MEDIUM): helper Enter params never compared with landed key params

- What changed: a "Note on the Enter wire params (helper versus landed key)" added to section 4. The landing must record the decision: either justify the two differences as harmless, or decide whether key() needs a `code` field for Enter. Do not change key() silently inside the landing without recording the decision.
- Exact new wording: "The helper sends code: 'Enter' on both keyDown and keyUp, and text: '\r' on keyDown only (its keyUp carries no text). The landed key() never sends a `code` field for any key; it sends key, modifiers, windowsVirtualKeyCode, and nativeVirtualKeyCode only (scripts/cdp.mjs:402), and it sends the same params object, including text '\r', for both keyDown and keyUp (lines 411 to 412). Both differences are probably harmless: the composer keys off e.key, and browsers ignore text on keyUp."
- Source: committed helper lines (keyDown carries code 'Enter' and text '\r'; keyUp carries code 'Enter', no text); scripts/cdp.mjs line 402 (params object, no code field), line 410 (text '\r' for Enter), lines 411 to 412 (same params object for keyDown and keyUp).

### F8 (LOW): section 5 "must sit between set_value and key in the chain"

- What changed: softened to a style suggestion. Exact new wording: "Keep the branches in action-list order for readability, with the focus branch between set_value and key; that is a style suggestion, not a requirement, because the dispatch chain is an else-if over distinct action types (lines 471 to 545), so branch position is irrelevant to execution order and the action list order decides."
- Source: scripts/cdp.mjs lines 471 to 545 (dispatch chain).

### F9 (LOW): two one-line citation slips

- What changed: scripts/code_exec.py:936 to 938 corrected to 936 to 939 (the require_asserts call closes on line 939 with 'sent_bubble': False). Scripts/cdp.mjs:292 to 313 corrected to 292 to 314 (click closes on line 314; the three dispatchMouseEvent calls are on lines 311 to 313).
- Additional correction carried from the review's own fix-pass record (report section 8.1 item 7): key() range corrected from 390 to 412 to 390 to 414 in both places the spec cites it (section 2 and section 5). The function closes on line 414; the for loop closes on line 413. AssertAction cited as scripts/cdp.mjs lines 415 to 426 in the new F4 derivation (closes on line 426, per the review fix-pass record section 8.3).
- Source: direct reads of scripts/code_exec.py lines 936 to 940 and scripts/cdp.mjs lines 390 to 427 at todolist-push HEAD 704a218.

### F10 (MEDIUM): missing test steps in section 8

- What changed: a "Missing tests" block added to section 8, items (a) to (g) plus the review section 4 consolidated items.
- (a) Focus failure path: evaluate returns activeElement !== e, must throw 'field is not editable or did not gain focus' (section 4 step 4 wording).
- (b) Focus via selector, not only by ref.
- (c) [set_value, focus, key Enter] without the trailing assert must fail P5.
- (d) Failing-first anchor for the dom_asserts change: the landed 4-action program must fail require_asserts BEFORE the focus entry lands (unknown action type), and pass after.
- (e) Corrected F3 rule tests: [type, key Enter, assert] with no click must raise DomAssertError; [click, type, key Enter, assert] must pass; [set_value, focus, key Enter, assert] with focus placed AFTER the Enter must raise DomAssertError (pins "preceding").
- (f) Whitelist sync test: asserts the three browser whitelists (cdp.mjs line 434, code_exec.py line 217, cu.py line 1299) contain the same set. Scoping decision, made by this fix pass and stated in the spec: the test is scoped to the landed set plus the recorded drift. It asserts focus is in all three whitelists and the three sets are equal except for the known hover_click drift (cu.py lines 1299 and 1341 lack hover_click). Adding hover_click to cu.py is a follow-up, not part of this landing, so the test does not require it. Reason: the drift predates this landing, is unrelated to focus, and changing cu.py browser validation is out of landing scope.
- (g) Pattern clarification: focus unit tests need the whole-adapter vm run with a fake page carrying globalThis.__agentCu, refs, and an activeElement stub, like the existing harvest test's fake page in tests/cdp_validation.mjs. The key-function slicing trick (line 6, between 'async function key(' and 'async function assertAction(') does not apply to focus, because the focus branch lives inline in the handle() dispatch loop, not in a standalone function.
- Consolidated additions: the landed program builder emits the focus action with a ref (not a selector), the same composer ref as the set_value action; the live dry run records the focus step's own timing separately (one Runtime.evaluate) and the post-Enter bubble latency the same way (one Runtime.evaluate loop after the Enter).
- Source: tests/cdp_validation.mjs line 6 (slice pattern) and the harvest test fake page (vm.createContext with document stub and activeElement), read first-hand.

### F11 (NOTE, confirmed no gap): section 5 file list complete

- No change made. Confirmed in the log: element_ref.validate_action_binding is type-agnostic (lines 146 to 164), action_result.py only re-exports DOM_ASSERT_EXCEPTIONS (line 33), and the AssertSetTests chains in test_step5_p1p5.py contain no focus action. No fourth file is missing from the section 5 edit list. Verified by reading the review's section 2.3 check and the cited files; no spec text was wrong on this point.

### F12 (NOTE, stands): section 10 items 2 to 10, except 1 and 11

- No change made. Re-verified at todolist-push HEAD 0b59d9f: /tmp/c5-count.mjs is still not in the repo (`git ls-tree` grep for c5-count returns 0 matches), so item 2 stands. Items 3 to 6 stand (no coordinator decision on option A or B in any commit read; no focus tests exist yet; no live proof of landed code exists; laptop sync and relay restart still unverified). Item 7 stands (80-element cap scripts/cdp.mjs lines 83 to 84; all 5 reopen Chromium runs ran relaxed, verified from the JSONs: routing_relaxed True, observe truncated True, 80 elements). Items 8, 9, 10 stand (mouse stall unsolved; Brave decision open; shadow-root activeElement walk a follow-up).

### F13 (NOTE): dry-run baseline is log-only evidence

- What changed: one sentence added in section 8 next to the baseline: "That baseline rests on log prose only: no run-0 JSON exists in the repo (improvements/s2-flip-reopen-runs/ holds only run-1..5.json plus the P9 PNGs), so the landing team cannot recompute it from a JSON."
- Source: tree listing of improvements/s2-flip-reopen-runs/ on todolist-push (run-1..5.json plus 10 P9 PNGs, no run-0 JSON). Baseline figures themselves (wall 30123.9 ms, Chromium elapsed 85.8 ms, completed 2) verified against the reopen log section 3.

## Commit record

- Spec fix, main: commit 3962400, "C5-B1-SPEC-FIX: apply batch 13 task 2 review (F1-F10) to (b1) landing spec", 1 file changed (docs/batch12-task2-b1-landing-spec-20261122.md), 290 insertions, 69 deletions. Staged with explicit pathspec (git add docs/batch12-task2-b1-landing-spec-20261122.md), committed with explicit pathspec. Push: 52bcd90..3962400 main -> main at about 15:28 +07. Verified: git ls-remote origin main returned 39624009b4bd33d08724cdd2799cbd01a30503ec.
- Spec F2 follow-up, main: commit eab0228, "C5-B1-SPEC-FIX: F2 follow-up, all 25 P9 frames pixel-viewed by CB-8 re-audit 84cc31f", 1 file changed, 20 insertions, 14 deletions. Same staging discipline. Push: 3962400..eab0228 main -> main at about 15:29 +07. Verified: git ls-remote origin main returned eab02280d0647df2899466a875ef587390ac176c.
- This log, todolist-push: staged with explicit pathspec for this file only (improvements/worker-click5-b1-spec-fix-log.md). Unrelated working tree changes were NOT committed: pre-existing untracked improvements/* files belong to other workers and were left untouched.
- No personal information anywhere in the spec edits or this log. No em dash or en dash in the spec edits (checked: 0 of each) or in this log.
