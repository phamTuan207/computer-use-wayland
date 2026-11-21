# Council CLICK2-C1 review log

Branch: todolist-push. Task: independent review of the amend diff and the combined design. Work on the VM only (code + tests). No live laptop driving, no browser tasks, never ydotool. No em dash (U+2014) or en dash (U+2013) anywhere in any file written by this worker. All times wall-clock Asia/Ho_Chi_Minh + elapsed from task start 02:52 +07.

## 2026-11-22 02:52 +07 (t+0m) Start

Read first, in order: coord-click2 synthesis log, amend log, fix log, all five crawl logs, clone2 bench doc (origin/main docs/clone2-dom-grounding-20261122.md, read via git show). Also read C1, C2, RT logs to pin down the consolidated 12 items (C1 items 1-3 + RT R1-R9), and the C3 log is on the read list if time allows after the code checks.

Scope note found at once: the task names the amend diff as e4082ff..4b7d6ac, but that range includes 30+ unrelated commits (crawls, ZT-C, batch7 corrections, coord logs) because the amend commits were rebased on top of a moved branch. The actual amend code is e704187..90b7026, parent 16c4196. The code review below is on 16c4196..90b7026 (12 files, +1632/-116), and the e4082ff..4b7d6ac range is checked only for scope and hygiene. The e4082ff..16c4196 span touches no scripts/ or tests/ files (verified by git diff --stat), so the two ranges agree on code content.

Consolidated 12 items as pinned down:
- C1-1: repair test_session_continuation regression (typed refusal then refresh).
- C1-2: widen G28 loud refusal to pointer-only batches.
- C1-3: set type_verified None on the terminal_address-None after-skip path.
- R1: redesign type verification to check typed text or input region, not whole-frame hash; correct fix-log Stage A claim; add click+type test with frame changed by click only.
- R2: surface pointer-only substitution top-level (fallback_reason or equivalent).
- R3: copy type_verified and error_code into act-now envelope on both paths.
- R4: reword refusal message so screen-coords remedy is not offered on key/type path.
- R5: convert JSON decode + HTTPException escapes in zen_dom _wd to ZenDomError (or correct docstring).
- R6: surface tab restore failures instead of swallowing them.
- R7: stop full tab scan after first hang (or scan budget).
- R8: verify switched tab in tab_at, or downgrade handle-order claim.
- R9: scope G28 docstrings to key/type batches (moot if C1-2 widening lands, since the docstring then becomes true as written).
- Item 12 in the amend log's own numbering is the owner-corrected grounding-verification item (DOM-first grounding + cheap verification, no slow observe cycles), which replaces the original "verify caret by fresh observe before typing" shape. This review checks it as the 12th item under that replacement reading, and flags the numbering ambiguity below.

## 2026-11-22 02:54 +07 (t+2m) Independent test runs (amend state)

No scripts/ or tests/ file changed between 4b7d6ac and HEAD e65b280 (only coord/baseline log commits), so runs at this checkout are the amend-state results. All from tests/ with stdlib unittest.

7 named suites: test_first_action 61 OK, test_type_verification 47 OK, test_zen_dom 25 OK, test_dom_act 10 OK, test_pick4_fastpath 28 OK, test_session_continuation 10 OK, test_keyboard_preflight 32 OK. Total 213, all OK.

13-suite run (the 10 fix-log suites plus session_continuation, dom_act, pick4_fastpath): 315 tests OK in 4.012s. Matches the amend log count exactly (315; its 5.173s is a timing difference, not a count difference).

Fail-before, worktree /tmp/click2-c1-base at e4082ff, new test files + scripts/dom_act.py + native/wtype copied in, old source untouched. Results match the amend log exactly: test_first_action 3 failures + 2 errors, test_type_verification 1 failure + 7 errors, test_zen_dom 6 failures + 9 errors, test_dom_act 9 errors of 10, test_pick4_fastpath 5 errors, test_keyboard_preflight OK, test_session_continuation OK. Every new suite fails before and passes after, so the tests do discriminate the new code.

## Item-by-item check (12 items)

- C1-1 session_continuation regression: DONE. tests/test_session_continuation.py post hash is now '1111', distinct from the fresh observation, mirroring the sibling test and the preflight harness. Suite passes 10/10, including the previously failing typed-refusal test.
- C1-2 G28 widening to pointer-only: DONE. scripts/first_action.py run() now refuses for EVERY batch when rejected is not None; the has_keyboard gate is gone. Test test_stale_given_observation_pointer_only_refused (tests/test_first_action.py:620) asserts refusal, code 1, path 'refused', session never attempted.
- C1-3 type_verified None on terminal_address-None path: DONE. scripts/cu.py terminal-None branch now sets type_verified None plus a skip note, matching the after_capture=False branch.
- R1 type verification redesign: PARTIAL (see F1/F3). The whole-frame hash is replaced by the input-line band (scripts/cu.py:1018 _input_line_changed, band full width, anchor y plus/minus 12, threshold 50) plus optional focus_check/type_check hooks, and the fix-log Stage A claim is corrected in improvements/worker-click-fix-log.md. The click+type test with a frame changed by the click only exists (tests/test_type_verification.py:95) and passes. But the sufficient check (DOM value) is not wired into any production path, and the band still false-passes one live shape (F3).
- R2 pointer substitution top-level flag: DONE, in the stronger form. Pointer batches no longer proceed at all, so there is no proceed path left to flag; fallback_reason is set on the refusal path (scripts/first_action.py:474-486). The docstring overclaim is gone with the exception itself.
- R3 envelope type_verified + error_code: DONE on both paths. scripts/first_action.py:543 (session path) and :597 (fallback path) copy both fields, None when absent. Tests test_session_type_verified_and_error_code_surfaced_in_envelope and test_session_without_verification_fields_reports_none pass.
- R4 refusal remedy: DONE. loud_substitution_refusal(rejected, has_keyboard) offers the screen-coordinates remedy only for pointer-only batches; the key/type test (tests/test_first_action.py:659) asserts 'omit --observation' is absent.
- R5 zen_dom _wd escapes: DONE. scripts/zen_dom.py _wd now catches ValueError (covers JSONDecodeError) and http.client.HTTPException, and raises ZenDomError when the parsed response lacks a "value" member. Tests test_non_json_response_becomes_zen_dom_error, test_bad_status_line_becomes_zen_dom_error, test_response_without_value_becomes_zen_dom_error all pass.
- R6 restore failures: DONE. _try_restore returns the error and every caller raises it instead of swallowing (scripts/zen_dom.py:227-240, tab_at and list_tabs paths). Tests test_failed_restore_is_raised_not_swallowed and test_failed_restore_after_scan_is_raised pass.
- R7 scan budget: DONE. list_tabs stops after the first transport failure and raises a wedge error (scripts/zen_dom.py:271-340, wedge at :317-328); non-transport per-handle errors still record and continue. Tests test_hung_handle_stops_scan_and_raises_wedge and test_raw_timeout_per_handle_stops_scan pass.
- R8 tab_at verification: DONE. The handle-order claim is downgraded to handle-list index (creation order, not visual tab order) in the docstring and CLI help, and _verify_selected checks the current handle equals the requested handle after switching. Test test_switch_not_taking_effect_raises passes. Note: the verification is handle equality, not a title/URL cross-check; the title/URL read already existed via _read_current_tab, so the combination satisfies the "verify or downgrade" requirement.
- R9 G28 docstrings: DONE, moot by widening. The module docstring now says the run "refuses loudly instead, for any batch" (scripts/first_action.py:56-61), which is true as written once C1-2 lands.
- Item 12 (owner replacement: DOM-first grounding + cheap verification, no slow observe cycles): PARTIAL (see F1/F2). The DOM-first path is built and tested (scripts/dom_act.py, scripts/zen_dom.py viewport_origin/focus_check/field_value/verify_typed/hit_check, scripts/fastpath.py dom_rect_to_image_point), and it adds zero observes in the dom_act flow. But the conversion layer does not satisfy C12 (F2), and the cheap verification hooks are not wired into the production path (F1).

## Bar numbers check (owner corrections)

- Observes per task: 3 (1 preflight fresh + 1 after-capture + 1 settle re-capture), proven by tests/test_type_verification.py:195 test_click_type_enter_uses_no_extra_observes, which asserts observe_calls == ['fresh', 'persist', 'persist']. The amend adds zero observes in desktop_act; DOM evals are not observes. ACCEPTED as measured, with the caveat that the count comes from the fake harness, not a live run.
- Actions per observation: 3 (click, type, Enter) from 1 observation in the batch test; ground_many grounds 2 inputs from 1 meta in 6 DOM calls (tests/test_dom_act.py). ACCEPTED as measured.
- Accuracy: 7/7 = 100% synthetic in DomRectMappingTests, bar >= 90%. NOT ACCEPTED as grounding accuracy: the 7 cases test the linear map given a correct viewport origin, and the truth rect in _hit is built from that same origin (tests/test_pick4_fastpath.py:482-560), so the test is circular on the load-bearing step, origin acquisition. Live grounding accuracy is still owed by the 2-vision benchmark. The number is a map-accuracy number, not a grounding-accuracy number, and must be labeled as such.
- Live wall time vs Codex 2.5 min: OWED, not claimed. The amend log states this honestly.

## Hygiene and scope (checked on 16c4196..90b7026, scripts + tests)

- Em dash U+2014: 0. En dash U+2013: 0. Same counts on the full e4082ff..4b7d6ac range.
- ydotool: 1 occurrence, the words "No ydotool" in tests/test_dom_act.py module docstring, a mention, not usage.
- PII: none in added lines (no email, address, phone, name).
- image_point (scripts/cu.py:995) and move: appear only as unchanged context lines in the diff; no added line touches them. Confirmed by diff -U0 grep.
- Y13g: no Y13g file in the diff; no _check_entry_pyc change.
- Scope note: the task names e4082ff..4b7d6ac, but that range holds 30+ unrelated commits (crawls, ZT-C, batch7 corrections, coord logs) because the amend was rebased onto a moved branch. The code review above is on the real amend range 16c4196..90b7026; the e4082ff..16c4196 span touches no scripts/ or tests/ file, so the code content is the same either way.

## C12 adjudication (c): NOT SATISFIED

The amend's dom_rect_to_image_point (scripts/fastpath.py:169) implements only the linear map: screen = viewport_origin + rect center, then image = (screen - region origin) * image_size / region size. The doma11y C12 requirement is: Hyprland window geometry + devicePixelRatio + viewport origin, cross-checked against AT-SPI screen extents. The amend meets one of those four parts and fails the other three, and the one part it claims is contradicted by live in-repo evidence:

1. Viewport origin semantics are wrong for this Zen build. scripts/zen_dom.py:367-380 viewport_origin() returns [window.mozInnerScreenX, window.mozInnerScreenY] and documents it as "the viewport origin in screen coordinates (CSS px)". docs/calibration-e2-report.md:21, measured live on the laptop 2026-11-21, says mozInnerScreenX/Y in this Zen build are WINDOW-relative (240, 8), not absolute screen coords, and the truth table must add the window origin (2509, 914) for screen px. Using the window-relative pair as a screen origin misplaces every point by the window offset. The tests hide this: tests/test_zen_dom.py:418-428 and tests/test_pick4_fastpath.py:482-560 both assume the origin IS the absolute window origin [2533, 914].
2. Marionette may not return the value at all. improvements/worker-ztb-blind-run-log.md:10 records eval "window.mozInnerScreenX + ..." returned null via Marionette eval, and that worker switched to observe-image content-area offset + DOM rect instead. viewport_origin() raises ZenDomError on a non-numeric return, which fails closed (safe) but means the DOM-first flow cannot run live over Marionette until the origin source is proven. No live Marionette probe of viewport_origin exists in this diff.
3. No DPR or monitor scale. dom_rect_to_image_point never reads window.devicePixelRatio and never uses meta monitor_scale (the meta carries it; scripts/cu.py:990). On this machine scale is 1 and dpr is 1 (E2 setup), so the live impact today is nil, but the C12 requirement as written is unmet and the code will be wrong by the scale factor on any scaled display.
4. No AT-SPI cross-check. No cross-check against AT-SPI screen extents exists in scripts/dom_act.py, scripts/fastpath.py, or scripts/zen_dom.py (grep: no atspi reference in the new code). The C12 cross-check is the cheapest accuracy proof before any live benchmark, and it is entirely absent.
5. No Hyprland window-geometry path. The window origin is never read from hyprctl clients (scripts/hypr_cmd.py already parses it); the conversion has no fallback origin source.

Net: the conversion layer is a correct linear map with an unproven, likely wrong origin input. A further build is still open: origin = Hyprland window origin + mozInnerScreenX/Y (window-relative), times DPR/monitor_scale, with an AT-SPI cross-check that stops the run on disagreement, plus a live Marionette probe proving viewport_origin returns numbers on real Zen. Until then the DOM-first flow is likely to fail closed live (ValueError "outside the observed image" from scripts/fastpath.py:169, or ZenDomError from viewport_origin), not to click wrong, which is safe but non-functional.

## Combined design review (b)

Step 1 (VISION 1 inventory, one-shot bulk DOM harvest, Mantis numbered text, C12 layer + AT-SPI cross-check): SOUND in shape, HALF-BUILT. The amend builds per-selector grounding, not one-shot bulk harvest: scripts/dom_act.py:64-72 ground_many calls ground_input per selector, 3 evals each (locate + viewport_origin + hit_check), re-reading the origin every time. Clone2 measured one-shot 66 rects in 0.019s Marionette / 0.006-0.011s BiDi versus 16ms per element (55x slower), so the amend's shape is the slow shape clone2 warned against. For 2 inputs it is fine; for "every input + button of both clones" it is not the bulk harvest the design claims. Brave CDP DOM domain + AX tree (C2/C3) is unbuilt: scripts/cdp.mjs contains no getBoxModel, getContentQuads, or getFullAXTree. Mantis numbering is a formatting layer, not yet built, and its vendor numbers (29-47% fewer tokens, 29-37% fewer calls, about a third less time) are vendor-run with disclosed caveats (short-task comparison across builds, tasks swapped, two long iframe/tab tasks excluded); Mantis is Chromium-side, so on Zen it is a format to copy, not a tool to run. Ref stability on a mutating live Messenger thread (new bubbles, typing indicators) is unproven; diff-only updates assume stable refs, which a live chat thread does not guarantee.

Step 2 (plan-once program): SOUND. Matches the in-repo Pick1 shape and the multiaction rank 4 candidate. No conflict, provided the inventory it plans from is complete; a wrong inventory fails the whole program, which is why step 3's guard matters.

Step 3 (guarded execution, HCU-style live guard, stop at first failure, exactly-once per send): SOUND in principle, NOT WIRED. The guard pieces exist (hit_check before click in dom_act, focus_check before type in desktop_act) but only in the dom_act flow; the default desktop_act path used by act-now has no guard at all and no production caller passes the hooks (see F1). Exactly-once intent per send has no implementation: no intent ledger, no dedup, no send marker. A guard abort mid-batch followed by a retry can double-send. The design must specify the retry/ledger rule before implementation, not after.

Step 4 (cheap verification in-run, V1+V2+V3+V4+V11 in one evaluate, V5 hit test, V12 finish gate): PARTLY SOUND. V1/V2/V3/V4/V11 in one evaluate is the right bundle and the amend's zen_dom helpers cover V1-V4 individually, but they are separate evaluate calls (5 calls per focus_type), not one bundled call, and V11 (MutationObserver/input-event flag) is not built anywhere. V12 finish gate (sent bubble in thread DOM) is not built: verify_typed reads the field, which is empty after a send, so the finish gate needs a different check (thread DOM bubble list) that does not exist yet.

Step 5 (VISION 2 outcome scoring per M1): SOUND. Outcome scoring (both messages landed) is the right acceptance metric, and the grounding crawl's M1 correction (point-in-box under-counts correct clicks) is correctly applied. No conflict.

Step 6 (loop hygiene: prompt caching, diff-gated re-observation, downscale, context editing, low effort, adaptive waiting): UNOWNED. None of these live in this repo's code; they are agent-loop behaviors with no file, no owner, and no measurement in the design. Listing them as design steps without an owner is a gap, not a plan.

Conflicts and gaps summary for (b):
- CDP for Brave vs dead on Zen: handled correctly in the design (per-browser path), but only the Zen half is built; the Brave half (CDP DOM + AX) is missing, so the design as a whole is not implementable today for the Brave side.
- BiDi vs Marionette handover under the one-session constraint: the design uses Marionette only for Zen, which avoids the conflict, but it never specifies the session lifecycle (open, use, close, leak handling). Clone2 proved one active session per browser and that a leak blocks all remote control until restart. Any future step that needs BiDi (e.g. locateNodes with an accessibility locator, which the doma11y appendix resolved as existing) needs a specified handover: close Marionette, open BiDi, close BiDi, reopen Marionette, with a leak guard. Unspecified.
- HCU guard feasibility on our stack: feasible (cheap evals exist, measured 0.005-0.015s for a DOM read by clone2), but the guard is not wired into the default path, so feasibility is proven for the mechanism and unproven for the deployment.
- Mantis numbering on live Messenger pages: unproven (see step 1); Chromium-only tool, vendor numbers, mutating-thread ref stability open. Also doma11y open item 6 stands: cross-origin iframes are unreachable from parent JS, so any Messenger content in a cross-origin frame falls back to vision or BiDi browsing-context calls, and the design does not say which.

## Required fixes (AMEND)

F1. Wire the DOM verification hooks into the production path, or prove the default path does not need them. The focus_check/type_check hooks exist in scripts/cu.py:1570 desktop_act but no production caller passes them (scripts/cu.py:2470, :2759, scripts/first_action.py:581 all call desktop_act without hooks; only tests/dom_act.py FakeAct and scripts/dom_act.py focus_type do). Fix options, in order: (a) first_action/session driver passes zen_dom-based focus_check/type_check closures when the batch targets a known DOM field, with the session closed or reused under the one-session rule; (b) failing that, change desktop_act so a type batch without a DOM hook is labeled band-only in the envelope (type_verified_basis already says input-line-band; the envelope must carry that basis too, via R3, so no consumer reads type_verified as text-delivered). Verify with: a test where the click lands on the field, the type is stubbed (wtype returns '', no text), and the after image differs only by caret/focus-ring pixels on the band; the batch must report ok False with error_code type_unverified. That test currently does not exist; test_click_type_frame_changed_by_click_only_fails uses a pixel-identical after image and does not cover the caret case.

F2. Fix the C12 conversion layer. In scripts/zen_dom.py viewport_origin() and scripts/fastpath.py dom_rect_to_image_point: origin must be Hyprland window origin + mozInnerScreenX/Y (window-relative per docs/calibration-e2-report.md:21), multiplied by DPR / monitor_scale from the meta (scripts/cu.py:990 carries monitor_scale), with an AT-SPI cross-check (scripts/a11y.py ground extents) that stops the run when the converted rect and the AT-SPI extents disagree by more than a few px. Prove viewport_origin returns numbers over live Marionette on real Zen (the ZT-B null result must be re-probed, not assumed away). Relabel the DomRectMappingTests 7/7 as map accuracy, or drive them from a real origin acquisition. Verify with: a live Zen probe (laptop lane) showing viewport_origin + rect center lands inside the element rect for at least 5 elements, plus a unit test where the origin is window-relative (240, 8) with a window origin (2509, 914) and the image point is correct.

F3. Close the band false-pass shape. A click that lands correctly on the field shows a caret/focus ring on the input line, so scripts/cu.py _input_line_changed returns True with zero text delivered. The code comment already admits this ("necessary, not sufficient"), but R1 required verifying the typed text. The fix is F1 (wire the DOM value check); the band alone must never be presented as closing R1. Add the caret-only test from F1 as the acceptance test.

F4. Correct the size-mismatch fail-open in scripts/cu.py:1038 _input_line_changed. When old.size != new.size it returns True (verified). Incomparable images must return None (unverifiable, falling back to the labeled frame-hash path) instead of True. Verify with a unit test: two different-sized images, band returns None.

F5. Specify the combined-design gaps before implementation: (a) one-shot bulk harvest (doma11y C1) as a single evaluate returning all rects, replacing ground_many's 3N evals; (b) Brave CDP DOM.getBoxModel + Accessibility.getFullAXTree in scripts/cdp.mjs, or an explicit scope cut to Zen-only with the Brave path deferred; (c) exactly-once send ledger (intent + sent-bubble check) so a retried batch cannot double-send; (d) V12 sent-bubble finish gate as a thread-DOM read; (e) V11 MutationObserver/input-event flag bundled into the one-evaluate verification call; (f) BiDi/Marionette session handover protocol under the one-session constraint; (g) an owner for step-6 loop hygiene, or drop step 6 from the design. Verify with: the design doc updated to name the owner and file for each, or the items explicitly deferred with reasons.

F6. Clarify the item-12 numbering. The amend log counts the owner-corrected grounding item as item 12, while the coord log counts C1 1-3 + RT R1-R9 as the 12. State in the amend log which item the DOM-first work replaces and confirm R9 is covered by the widening (it is: scripts/first_action.py:56-61). One-line log fix, no code.

## Verdict: AMEND

The amend is a strict improvement with no regression (315 tests OK, fail-before confirmed on all new suites, hygiene and scope clean, all 12 items have code addressing them), so this is not BLOCK. But it must not land as closing R1 and C12: the sufficient type check is unwired in production (F1/F3), and the conversion layer uses a viewport origin contradicted by live in-repo evidence with no DPR and no AT-SPI cross-check (F2). Fix F1-F4 in code with the stated verification tests, F5 in the design doc, F6 in the log, then re-run the 13-suite set plus the new caret-only and window-relative-origin tests and re-review. Live proof (2-vision benchmark, total wall time vs Codex 2.5 min, both messages sent) remains owed after the fixes, as the amend log already states. Context note: MEMORY.md updated 02:57 during this review, ZT-C DONE, ZT series complete, lane now free; the baseline and benchmark runs that were blocked on the lane can now be scheduled, but they are not part of this review.

## 2026-11-22 03:05 +07 (t+13m) Review done, committing

Log written to improvements/worker-click2-c1-review-log.md. Commit with explicit pathspec only, push, verify via git ls-remote.
