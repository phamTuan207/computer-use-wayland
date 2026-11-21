# Council Member 2 verdict: Worker Y9 agy-y2 live-run plan (test fidelity only)

- Reviewer: Council Member 2 (test fidelity scope only)
- Plan under review: improvements/worker-y9-agy-y2-live-plan.md (commit 6f20fb5 on todolist-push)
- Suite under review: tests/realistic/agy-y2/ (commit 30a72e5), Y7 verification improvements/worker-y7-fix-log.md (commit a07fd27)
- Date: 2026-11-21

## Verdict: APPROVE WITH FIXES

The plan's structure is sound and most per-test notes are faithful, but the executable core of the plan (the runner and the ported verifier) does not exist yet, so fidelity cannot be fully proven from the plan text alone, and one spec step is papered over with a no-op. All fixes below are required BEFORE any live driving, except Fix 8 items, which may be fixed in the plan text at the same time. Fix 1 is a hard launch gate.

## What was checked and found correct

1. test-07 move set: plan line 48 states the move set is EXACTLY img1-3 (spec test-07-file-manager.md lines 38-40, steps 15-17) and Root 5 is correct. Confirmed against check.mjs line 240 ('Root: 5 files') and spec line 58 (step 35). The Root 6 diagnostic (img4 in the moved set) matches the Y7 redteam finding recorded in improvements/worker-y7-fix-log.md line 46.
2. test-09 direction B: plan line 50 uses #note-item-archived-draft for spec step 29 (spec test-09-notes-sync.md line 52), consistent with simulate.mjs line 364, check.mjs line 285, fixture line 66 (static HTML) and fixture line 142 (renderList ternary). The prohibition on the save handler rename branch is correct: fixture lines 182-191 delete the active key when the title is exactly 'Shopping' and the active id is not 'shopping'.
3. test-09 step 10 append handling: plan line 50 (read current value, type the full text, never append via type_text) is correct because run_live.py type_text lines 396-401 clears the element before typing, while simulate.mjs line 343 relies on puppeteer type append semantics. Step 14 (clear then type full body) matches simulate.mjs, which $eval-clears before typing.
4. test-09 step 33 as bypass mitigation: correct in principle. The rename-branch bypass passes all six final checker assertions (check.mjs lines 282-287 contain no body check), and only the spec step 33 body check (spec test-09-notes-sync.md line 56) can catch it. See Fix 4 for what is still missing.
5. test-02 mistake step: plan line 43 is correct that the spec has no explicit mistake step. Spec test-02-network-settings.md has no "Simulate mistake" step, and simulate.mjs has none either. The Bluetooth off/on plus persistence check (spec steps 21-25) is the closest analogue. The plan's "plays that role" wording is interpretive but harmless because it also says "Follow as written".
6. test-03 and test-05 select handling: JS value plus change event is equivalent to puppeteer page.select in simulate.mjs. test-05 B4 correction (click, clear, type 1800) matches the simulator $eval clear. test-05 formula bar typing is safe because type_text clears first (run_live.py lines 396-401).
7. test-08 row click: clicking the first td inside #row-req-api-checkout is equivalent to clicking the tr, because the fixture attaches the handler to the tr itself (fixtures/test-08-devtools.html line 273) and a td click bubbles to it. See Fix 8 for the missing justification note.
8. Thresholds (plan lines 18, 20, 21): PASS as zero step failures AND zero check failures AND final verify 0 failures AND integrity guard held is strict and sound. FLAGGED kept separate from the clean headline count is sound. Exit 0 iff clean plus flagged equals 10 is sound. The no-silent-re-run rule (re-run only for a test proven infra-blocked, logged as a re-run, never as a first pass) is sound. See Fix 6 for the one internal contradiction in the INFRA counter.

## Findings

### F1 (major): the runner and the ported verifier do not exist, so the central fidelity claim is unauditable

- Plan line 12 claims each test is verified by "a 1:1 port of check.mjs verifyTest (same selectors, same expected values, including test-07 'Root: 5 files')", and plan line 41 claims "All 10 tests follow simulate.mjs step for step (selectors and order)".
- tests/realistic/run_agy_y2.py does not exist in the repo (ls confirms only run_live.py and run_agyq2.py are present). There is no transcription to diff against the specs, simulate.mjs, or check.mjs.
- Consequence: every finding below that says "covered by an intermediate r.check()" is conditional on code that has not been written. The plan's repeated defense "my run follows the spec exactly" (plan lines 14, 48) is an assumption, not a control, until the runner exists and is audited.

### F2 (major): test-10 step 15 is replaced with a JS click that cannot fail and does nothing

- Spec test-10-ide-debug.md step 15 clicks #input-edit-watch-total. simulate.mjs lines 372-400 skip this step entirely (no occurrence of input-edit-watch-total in simulate.mjs).
- The fixture defines the input as display:none (fixtures/test-10-ide-debug.html line 114) and attaches no handler to it anywhere in the fixture. A pointer click cannot work on it, which the plan correctly states (plan line 51).
- The plan's remedy, click_js (el.click()), is a no-op that always succeeds: JS click on a hidden input with no handler has no observable effect. run_live.py click_js lines 392-394 just evals element.click(). Counting it as an executed step toward PASS is false fidelity. The plan's note "The checker does not test it" is true (check.mjs test-10 block, lines 289 onward, never references the input) but irrelevant: the checker not testing a step does not make the step performed.

### F3 (medium): test-01 step 15 is underspecified and is asserted nowhere else

- Spec test-01-tmux-session.md line 40 (step 15) requires #pane-active-output to contain "load average: 0.18, 0.22, 0.15" (fixture line 226 produces that string).
- simulate.mjs line 46 only types 'uptime' and clicks send; it never verifies the output. check.mjs line 51 computes terminalOutput from .pane-content but lines 59-66 never assert anything about it. So the final verify does NOT cover step 15 at all.
- Plan line 42 says only "Verify uptime text per spec step 15", with no selector and no expected string. The only coverage of the uptime execution therefore rests on an r.check() whose selector and expected value are not pinned in the plan.
- Plan line 42 also asserts Marionette find returns "the first match (the active pane)". First match in document order is the checkable claim; "the active pane" is not established by any cited fixture evidence. If the first match were the wrong pane, the test would still pass because nothing asserts the output.

### F4 (medium): the test-07 skip hole is handled by assertion, not by a pinned control

- Y7 doubt 1 (plan line 48): skipping spec steps 23-29 (delete plus restore) still passes all 8 final checks (check.mjs lines 233-240: names, Archive 3, Trash 0, row4 visible, folder Processed, toast active and text). The fixture has no restore marker. The plan acknowledges this.
- The hole-closers are the intermediate checks at spec step 24 (test-07-file-manager.md line 47: #file-row-img4 hidden and #trash-counter "1") and spec step 28 (line 51: #trash-counter "0"). The plan never names them. Its generic line 41 ("intermediate spec verifies as r.check() calls") does not pin which checks close this hole, and the runner that would implement them does not exist (F1).
- Same pattern for test-09 step 33: the plan names the step but does not pin the expected value "Milk, Eggs, Bread, Apples" (spec test-09-notes-sync.md line 56) in the plan text.

### F5 (medium): Y7 doubt 4 is dismissed without proof

- Plan line 14 says simulate --all aborting on the first crash "does not apply (each test runs independently)".
- simulate.mjs lines 457-466 run the --all loop with no per-test try/except, so a throw aborts all remaining tests and main().catch at line 474 exits 3. That gap is real.
- The live equivalent is unproven: run_live.py Runner.step lines 448-462 raises RuntimeError on any step failure, so unless run_agy_y2.py wraps each test in try/except with a fresh-fixture reset, a live step failure aborts the suite exactly the same way. The plan also states all 10 tests share one tab (plan Sec 3), which makes the per-test reset behavior load-bearing, yet the plan never states what happens after a mid-test step failure: does the runner reset the tab and continue to the next test, or abort?

### F6 (medium): the INFRA counter contradicts itself, and the 30 s hang has no classification

- Plan line 20 lists session-creation failure as INFRA-blocked, but the same line says the consecutive counter "resets to 0 on any pass and on the session-failure path" (repeated in Sec 3). A dead driver would therefore produce 10 consecutive session failures with no abort, which defeats the purpose of the two-consecutive abort rule for the most catastrophic infra mode.
- Plan line 22 says a Marionette call hanging past its 30 s timeout "fails that test", with no classification. The 30 s figure is the WD HTTP timeout (run_live.py line 278, urlopen timeout=30). A WD timeout is presumptively infra (driver or browser hung), not a live test failure. As written, a hung call would be recorded as a live failure (a finding, no re-run allowed under plan line 21) instead of an infra-blocked test eligible for a proven-infra re-run.

### F7 (minor): integrity guard is correctly specified in outcome but under-pinned in procedure

- Plan line 18 correctly requires the guard (verify FAILS on the untouched fixture before steps; a pass on untouched aborts that test as a suite defect, never a pass). This matches simulate.mjs, which throws an integrity error on an untouched pass.
- Missing pins: (a) the guard must run through the SAME ported verify code path as the final verify, not a second implementation that could drift; (b) it must run after the fresh fixture load and before any action, per test; (c) the untouched failure list must be recorded as evidence; (d) any re-run must re-execute the guard; (e) "abort that test" is ambiguous about whether the suite continues to the next test or stops.

### F8 (minor): small inaccuracies and missing justifications

- Plan line 50, test-09 step 10: the plan says to read the current value and type the full text, but never requires asserting the read value equals "Milk, Eggs, Bread" before typing. If the read returned empty, the run would type only ", Apples" and fail late at step 33.
- Plan line 49, test-08: the td-click deviation cites only "the P rule" with no fixture evidence. The equivalence holds by bubbling (fixture line 273), but the justification should be recorded in the plan.
- Plan line 53 claims "grep: zero __verify / __agyVerify / __fcckVerify in the suite". The claim is literally false for the suite tree: tests/realistic/agy-y2/README.md line 19 mentions window.__verify in prose ("window.__verify is strictly forbidden"). The substantive point stands (no hooks in fixtures, simulate.mjs, or check.mjs), but the claim must be corrected to that scope.
- Plan line 20 defines FLAGGED as "a pass where the intervention ran" without stating explicitly that a flagged test still requires all PASS conditions (zero step, check, and verify failures). Implied by the word "pass", should be explicit.
- Plan line 22 quotes headless timing as "240-411 ms/test" while the Y7 log records "247-393ms" (improvements/worker-y7-fix-log.md line 36). Diagnostic only, but the plan should quote the measured range or drop the numbers.

## Required fixes (numbered)

1. LAUNCH GATE, hard: write tests/realistic/run_agy_y2.py first, then audit before any live driving. (a) Produce a step-mapping table: every spec step for all 10 tests mapped to the runner call and to the simulate.mjs line that performs the same action. (b) Diff the ported verifyTest against check.mjs selector by selector and expected value by expected value, including test-07 'Root: 5 files' (check.mjs line 240) and all 6 test-09 assertions (check.mjs lines 282-287). (c) Freeze md5s of run_agy_y2.py, run_live.py, and the suite in the run log before launch. No live driving until this audit is recorded and passes. The plan must state this gate explicitly; the current ship step (plan Sec 5) records md5s but does not require the audit.
2. test-10 step 15: do NOT count the click_js call as executing spec step 15. Mark the step NOT PERFORMABLE in the runner (log it as a gap-probe only, never as r.step() success), exclude it from the test-10 step list, and record it as a known spec/fixture gap in the final report: input is display:none with no handler (fixture line 114). Do not let a test-10 PASS imply step 15 was performed.
3. test-01 step 15: pin the intermediate check in the plan: selector #pane-active-output, expected substring "load average: 0.18, 0.22, 0.15" (spec line 40, fixture line 226). State explicitly that the ported final verify does NOT cover this step (check.mjs line 51 computes terminalOutput but lines 59-66 never assert it), so this r.check() is load-bearing. Soften "(the active pane)" in plan line 42 to "first match in document order, same as puppeteer" unless fixture evidence for "active pane" is cited.
4. test-07 skip hole and test-09 step 33: name the hole-closing checks explicitly as required, PASS-gating r.check() calls: test-07 spec step 24 (trash-counter "1" and #file-row-img4 hidden) and step 28 (trash-counter "0"); test-09 spec step 33 with the pinned expected value "Milk, Eggs, Bread, Apples". State that the final verify alone cannot detect skipping test-07 steps 23-29.
5. Per-test independence: require the runner to wrap each test in try/except with a fresh-fixture reset (goto plus clear storage plus reload) before the next test, and state the abort behavior in the plan: a live step failure fails that test and the runner continues to the next test; only the Sec 2 two-consecutive-INFRA rule aborts the suite. Remove or qualify the plan line 14 claim that doubt 4 "does not apply" until this is implemented.
6. INFRA counter and hang classification: (a) session-creation failures must increment the consecutive INFRA counter (or, if the Y4d council intent is kept, add a separate cap: 2 consecutive session failures abort the suite). (b) Classify a 30 s WD timeout (run_live.py line 278) as INFRA-blocked unless evidence shows a fixture cause, so it is eligible for a proven-infra re-run instead of being recorded as a live failure.
7. Integrity guard procedure: pin in the plan that the guard uses the same ported verify code path as the final verify, runs after fresh load and before any action per test, records the untouched failure list as evidence, is re-executed on any re-run, and that "abort that test" means the test is failed as a suite defect and the suite continues (or the suite stops, pick one and state it).
8. Minor corrections in the plan text: (a) test-09 step 10: assert the read value equals "Milk, Eggs, Bread" before typing the full text. (b) test-08: record the bubbling justification (fixture line 273, handler on the tr). (c) Correct the __verify claim to "zero in fixtures, simulate.mjs, and check.mjs; the sole mention is the README.md line 19 prose prohibition". (d) State explicitly that a FLAGGED test still requires all PASS conditions. (e) Correct the headless timing range to 247-393ms per the Y7 log, or drop the numbers.

## Notes (not fixes)

- The plan's Sec 3 inheritance of Y4d council fixes (Council 3 F1-F9, Council 2 F1-F9) by reference is acceptable for this review, since the frozen md5s at ship time are the control. This review does not re-audit those fixes.
- The queue and slot-polling design (Sec 5) is outside test-fidelity scope and was not reviewed here.
- No em dash or en dash appears in this verdict file.
