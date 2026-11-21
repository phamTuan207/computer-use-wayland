# CLICK-CRAWL-VERIFY log

Worker: CLICK-CRAWL-VERIFY (research crawler for COORD-CLICK)
Repo: ~/workspace/computer-use-wayland, branch todolist-push
Start: 2026-11-22 02:05:24 +07 (Asia/Ho_Chi_Minh)
Finish: 2026-11-22 02:21 +07 (approx, elapsed about 16 min incl. last30days sweep)
Scope: crawling + candidate list ONLY. No live driving, no browser tasks, no implementation, no live tests. Never ydotool.

## Goal bar (judge every candidate against exactly this)

One vision (one observation) drives as many actions as possible, total task time reduced as much as possible, accuracy 90% or above. One vision, max actions, minimal total time, accuracy >= 90%.

Owner updates received during this crawl (MEMORY.md, 02:05 and 02:06 +07):
- Benchmark 2-vision is the acceptance test for the COORD-CLICK fix: VISION 1 locates ALL input boxes + buttons for clone1 + clone2 on ws2, then one script/workflow (no vision) clicks and sends for both, then VISION 2 checks both messages sent. Whole process uses only 2 visions.
- 1 vision = max work: every vision must be exploited to the maximum (all coordinates, all buttons, all state from one image). Verify by cheap non-vision means wherever possible.
- Benchmark runs AFTER improvements look good, not before. Order: research + improve first, then run the benchmark to prove it.

## Context: the defect this crawl must fix

Fix diff e4082ff added type verification via a whole-frame pixel hash. Redteam proved it false-passes on the incident shape: any click in the batch sets the hash, so click+type with type stubbed reports ok True, type_verified True, zero text delivered. The required fix is to verify the typed text or the input region, not the whole-frame hash, and to do it cheaply (no full observe). Our stack: Python, Hyprland/Wayland, Zen/Brave via Marionette/CDP/AT-SPI, wtype, grim.

## Method

Scrapling 0.5.1, venv ~/workspace/scrapling-trial-venv, PLAIN Fetcher only. StealthyFetcher NOT used (blocked by the VM proxy). Plain Fetcher worked on every source tried: 13 fetches, all HTTP 200, zero proxy failures, so no browser.search fallback fetches were needed for page reads (browser.search was used only for discovery). Fetch script: ~/workspace/scrapling-verify-fetch.py (outside the repo, scratch only).

Fetches (all 200, times in seconds):
- developer.mozilla.org/en-US/docs/Web/API/Document/activeElement (1.0s, 152734 bytes)
- developer.mozilla.org/en-US/docs/Web/API/Document/elementFromPoint (3.6s, 151989 bytes)
- developer.mozilla.org/en-US/docs/Web/API/Document/caretPositionFromPoint (3.4s, 165422 bytes)
- developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/selectionStart (1.4s, 140728 bytes)
- developer.mozilla.org/en-US/docs/Web/API/Selection (1.4s, 131699 bytes)
- playwright.dev/docs/actionability (1.9s, 52998 bytes)
- chromedevtools.github.io/devtools-protocol/tot/DOM/ (1.1s, method list incl. getContentQuads, getBoxModel, getNodeForLocation, focus)
- chromedevtools.github.io/devtools-protocol/tot/Runtime/ (1.5s, method list incl. Runtime.evaluate, callFunctionOn)
- arxiv.org/abs/2510.27266 HyperClick (5.1s)
- arxiv.org/abs/2506.03143 GUI-Actor (2.0s)
- github.com/emersion/grim (9.9s, README: region screenshot via -g)
- github.com/agent-sh/computer-use-linux (2.1s, README)
- github.com/nguy-n-th-huy/browzy/blob/HEAD/plans/reports/browser-use-click-260911-2354-action-execution.md (4.4s)

Discovery searches (browser.search): DOM verification, elementFromPoint hit testing, Playwright actionability, OSWorld grounding failures, AT-SPI focus/caret, region hash / phash, GUI-agent verifier + confidence, Marionette active_element, MutationObserver + contenteditable, pyatspi Text interface, crop-only OCR.

Date accessed for all sources: 2026-11-22.

## Candidates

### V1. DOM input value readback (exact string compare)

What it is: after wtype types into an input/textarea, read the value back through the browser, not through pixels. One CDP Runtime.evaluate call (Brave) or Marionette execute_script / element property call (Zen/Firefox) returning document.activeElement.value or the target element value, then compare exactly against the expected string. This is the direct replacement for the whole-frame hash: the check answers "is the text in the box", which is the claim type_verified makes.

Source: Playwright docs, Auto-waiting, https://playwright.dev/docs/actionability (accessed 2026-11-22). Playwright's own fill examples verify the final input value after typing. Also: Selenium type_test.html, https://chromium.googlesource.com/external/github.com/SeleniumHQ/selenium/+/refs/tags/selenium-4.15.2-python/javascript/atoms/test/type_test.html (types a value, then checks the textbox has the correct value afterwards). Also: Firefox Marionette intro, https://firefox-source-docs.mozilla.org/remote/marionette/Intro.html (Marionette "can be used to return information about the state of the browser which can then be used to validate that the action was performed correctly").

Goal mapping: cheap verification (one evaluate round trip, no screenshot, no vision). Kills the e4082ff false pass outright: a stubbed type leaves value empty, compare fails. Accuracy >= 90% without extra observes.

Applicability to our stack: in the type step, after wtype, run one Runtime.evaluate (CDP, Brave) or Marionette execute_script (Zen) returning the focused element value. Compare to expected; mismatch means retry type or re-click then type. Cost is one local socket round trip, milliseconds, versus a full grim + vision observe cycle.

Measured numbers: none reported by these sources for latency; Playwright treats value readback as a plain state read that "answers immediately" (no waiting).

Verdict: promising. Rank 1. This is the required fix.

### V2. contenteditable text readback (innerText + caret offset)

What it is: the incident shape is a contenteditable box (Muse web app message input in Brave), which has no .value. Read it back with el.innerText or el.textContent plus window.getSelection() caret offset inside the element. PromptSnippets' contenteditable adapter does exactly this: getElementValue via innerText, selection via the Selection and Range APIs. GhostType's getCaretCharacterOffsetWithin builds a Range from the selection, clones it to the element start, and returns the string length as the caret offset.

Source: ContentEditable Support, https://deepwiki.com/taterboom/PromptSnippets/7.2-contenteditable-support (accessed 2026-11-22). Ghost Text Engine, https://deepwiki.com/mdrazak2001/GhostType/3-ghost-text-engine-(content.js) (accessed 2026-11-22). MDN Selection, https://developer.mozilla.org/en-US/docs/Web/API/Selection (fetched 200, accessed 2026-11-22).

Goal mapping: cheap verification for the exact box type that failed in the incident. Same single evaluate call as V1, just a different property. Without this, V1 alone leaves contenteditable boxes unverified.

Applicability: one Runtime.evaluate returning {text: el.innerText, caret: caretOffsetWithin(el), focused: document.activeElement === el} for the contenteditable input. Compare text to expected (normalize trailing newline / zero-width chars, which rich editors insert). Note the CODE-CLICK finding that the real input rect was 64-75px below the clicked point: V2 catches that shape too, because text lands nowhere when the click misses the box.

Measured numbers: PromptSnippets uses 20ms settle waits around selection changes. No accuracy numbers reported.

Verdict: promising. Rank 2. V1 + V2 together cover every text box we type into.

### V3. Focus verification via document.activeElement (walk shadow roots)

What it is: read document.activeElement and check it IS the intended input before typing, and still is it after clicking. MDN: activeElement returns the element receiving keyboard events, usually the focused element. The Chromium omnibox test patch shows the correct form for modern pages: walk shadowRoot.activeElement down, because the focused element inside a shadow tree or iframe otherwise reports as the host. If activeElement is body, nothing has focus and typing goes nowhere.

Source: MDN Document.activeElement, https://developer.mozilla.org/en-US/docs/Web/API/Document/activeElement (fetched 200, accessed 2026-11-22). Chromium commit 7eaef9cf8999e3d242d58001e6903e36f3187cb0, https://chromium.googlesource.com/chromium/src/+/7eaef9cf8999e3d242d58001e6903e36f3187cb0%5E%21/ (focus verification refactor: "if (el && el.ownerDocument.hasFocus()) { active = el.ownerDocument.activeElement; while (active?.shadowRoot?.activeElement) { active = active.shadowRoot.activeElement; } is_focused = (active === el); }").

Goal mapping: cheap verification, catches false ok. A click that missed the box leaves focus on body or the wrong element; typing then silently goes nowhere, which is exactly the incident shape. One field in the same evaluate call as V1/V2, zero extra round trips.

Applicability: fold into the V1/V2 evaluate call: return activeElement tag/id/class + whether it equals the target. If focus is wrong, re-click (or element.focus()) before typing, do not type blind.

Measured numbers: none.

Verdict: promising. Rank 4 (bundled free with V1/V2).

### V4. Caret position check (selectionStart / getSelection focusOffset)

What it is: after typing N chars at the end of a field, the caret must be at offset len(before)+N. For input/textarea, read selectionStart/selectionEnd (MDN: when nothing is selected both equal the caret position; applies to text, search, url, tel, password). For contenteditable, read getSelection().focusOffset plus the focus node, or the GhostType character-offset method. Caret in the wrong place (0, or in another node) proves the keys went elsewhere even if some text exists somewhere.

Source: MDN HTMLInputElement.selectionStart, https://developer.mozilla.org/en-US/docs/Web/API/HTMLInputElement/selectionStart (fetched 200, accessed 2026-11-22). MDN Selection, https://developer.mozilla.org/en-US/docs/Web/API/Selection (fetched 200). MDN Document.caretPositionFromPoint, https://developer.mozilla.org/en-US/docs/Web/API/Document/caretPositionFromPoint (fetched 200; returns node + character offset for a point, Baseline 2025, new since Dec 2025, so do not rely on it in older browsers; caretRangeFromPoint is the fallback).

Goal mapping: cheap verification, catches wrong grounding and stale points. Caret offset is a single number that distinguishes "typed into the right box" from "typed into the wrong box" and "typed nowhere". Same evaluate call as V1/V2/V3.

Applicability: same Runtime.evaluate / execute_script as V1, return caret offset, assert it equals expected length. For contenteditable, use the Range-clone offset method from GhostType, not focusOffset alone (focusOffset is relative to its node, not the whole box).

Measured numbers: none.

Verdict: promising. Rank 3.

### V5. elementFromPoint hit test (pre-click occlusion check + post-click identity check)

What it is: document.elementFromPoint(x, y) returns the topmost element at viewport coordinates, ignoring pointer-events:none elements. Before clicking, call it at the planned point and check the returned element is the target or a descendant of it; if a modal, banner, or sibling is on top, the click would land there instead. After clicking, check activeElement (V3). Playwright's "Receives Events" actionability check is this same idea built into every click. browser-use does the equivalent as an occlusion check before CDP mouse dispatch, with a JS-click fallback when blocked.

Source: MDN Document.elementFromPoint, https://developer.mozilla.org/en-US/docs/Web/API/Document/elementFromPoint (fetched 200, accessed 2026-11-22). Playwright Auto-waiting, https://playwright.dev/docs/actionability (fetched 200). browser-use click report, https://github.com/nguy-n-th-huy/browzy/blob/HEAD/plans/reports/browser-use-click-260911-2354-action-execution.md (fetched 200; "if no geometry can be obtained at all, or if the occlusion check says the point is blocked, browser-use falls back to a JS click"). Reticle Moli experiment, https://www.reticle.sh/signal/2026-10-25-moli-headless-browser-mock-layout-visibility (accessed 2026-11-22; elementFromPoint at the Pay button centre returns the modal in Chromium, the button in a mock-layout browser: the call is the sharp detector for "something covers the target").

Goal mapping: cheap verification AND catching wrong grounding before acting. One evaluate call, no screenshot. Prevents the misclick instead of detecting it afterwards.

Applicability: in the click step, before dispatching mouse events, evaluate elementFromPoint at the planned point (viewport coords, so convert from screen coords using the window position). If the hit element is not the target, re-ground from the same vision data (try another candidate point inside the target rect) or abort to re-observe. Also usable post-click as a stale-point check.

Measured numbers: Reticle table: 4 checks, Chromium vs mock-layout browser; elementFromPoint row is the one that exposes the false pass. No latency numbers.

Verdict: promising. Rank 6.

### V6. CDP live geometry re-resolution at click time (kill stale points)

What it is: never click coordinates cached from serialization time. browser-use recomputes coordinates at click time from live element geometry, trying CDP DOM.getContentQuads, then DOM.getBoxModel, then JS getBoundingClientRect, and CDP itself validates/rejects a stale backend_node_id. Its report also notes the failure mode: the model index resolves from a cached selector map, and staleness only surfaces as a downstream CDP error. DOM.getNodeForLocation is the CDP-native hit test equivalent of V5.

Source: browser-use click report, https://github.com/nguy-n-th-huy/browzy/blob/HEAD/plans/reports/browser-use-click-260911-2354-action-execution.md (fetched 200). CDP DOM domain, https://chromedevtools.github.io/devtools-protocol/tot/DOM/ (fetched 200; method list includes getContentQuads, getBoxModel, getNodeForLocation, focus, scrollIntoViewIfNeeded).

Goal mapping: catches stale points, which is one of the required redteam break attempts. Cheap (CDP round trips, no vision). Accuracy >= 90% needs fresh geometry when the page moved between vision and click.

Applicability: in our click path (Brave/CDP), resolve the target element once from vision, then re-query its quads immediately before dispatching Input.dispatchMouseEvent, and click the live centre. For Zen/Marionette, the equivalent is re-reading getBoundingClientRect via execute_script right before the click.

Measured numbers: none reported.

Verdict: promising. Rank 10. Needed for the stale-point redteam case, but secondary to V1-V5 for the type false-ok.

### V7. Playwright-style actionability gate + trial mode (pre-action discipline)

What it is: before every action, check visible, stable (same position for two animation frames), enabled, editable (for fill), receives events, not inert. Retry until all pass or timeout. Playwright also offers trial:true, which runs all checks without acting, and warns that force:true "can make a test pass that exercises nothing" and that force-click "can pass while testing nothing". Our equivalent of force:true is exactly the e4082ff failure mode: skipping the check and reporting ok.

Source: Playwright Auto-waiting, https://playwright.dev/docs/actionability (fetched 200, accessed 2026-11-22). Tutorial restatement, https://www.devtutorials.ai/learn/playwright/core-test-writing/actions-and-auto-waiting (accessed 2026-11-22; check table incl. "Receives events: nothing covers it, so the click lands on it" and "After the click, Playwright checks that the box really changed. If not, the action fails").

Goal mapping: cheap verification before acting, catches wrong grounding. Most checks are DOM reads; the stable check needs two frames, which is the only non-trivial cost. Also gives us the trial pattern: run checks, do not act, report which check failed.

Applicability: implement as a pre-click/pre-type gate using V5 (receives events), getBoundingClientRect size (visible), disabled/readonly attributes (enabled/editable), and a two-sample rect compare (stable). Forbid any force/bypass flag in our own code path; if a check fails, the action must not report ok.

Measured numbers: none (Playwright default action timeout 30s; our gate needs a much smaller budget, to be set by testing).

Verdict: promising. Rank 11. Mostly a packaging of V3/V5/V6 plus stability; adopt the discipline, not the library.

### V8. Input-region pixel hash / cropped grim capture (repair of the whole-frame hash)

What it is: hash ONLY the input element rect, not the whole frame. grim supports region capture natively: grim -g "x,y wxh". Compare the region hash before vs after typing. A change in the input rect is necessary evidence that something happened in the box; a whole-frame change is not (any click anywhere sets it, which is the proven false pass). The watchman project notes incremental grid hashing (hash each cell of a 16x16 grid, re-hash only changed cells) is 10-50x faster than whole-screen hashing for typical desktop use.

Source: grim README, https://github.com/emersion/grim (fetched 200, accessed 2026-11-22; "Screenshoot a region: grim -g \"10,20 300x400\""). Smart capture doc, https://github.com/coldaine/the-watchman/blob/HEAD/docs/unified/smart_capture.md (accessed 2026-11-22; phash/dhash/pixel algorithms, "Hash only changed regions", "Benefit: 10-50x faster diffing for typical desktop usage").

Goal mapping: cheap verification, fixes the exact defect (whole-frame hash) at minimum cost. A grim -g crop of one input box is a tiny capture, no vision model call.

Applicability: replace the e4082ff whole-frame hash with: capture input rect before type, capture same rect after type, require hash change. BUT this alone is still not sufficient, and redteam must be told: a click that focuses the box changes the region (caret blink, focus ring) with zero text typed, so region-hash-change can still false-pass. It must be paired with V1/V2 (content compare). Use it as the visual fallback where DOM is blind (canvas inputs, native apps), not as the primary type check.

Measured numbers: watchman claims 10-50x faster for incremental grid hashing (planned feature, not measured in that doc, treat as claim not proof). No latency numbers for grim -g.

Verdict: promising, but only as a pair with V1/V2. Rank 7.

### V9. Perceptual hash (phash/dhash) with calibrated threshold on the input crop

What it is: phash/dhash summarize image structure in a few dozen bits, compared by Hamming distance; robust to JPEG noise and one-pixel shifts, unlike exact pixel equality. WiFry switched its frame hash from raw SHA-256 to dHash on a center-cropped frame: JPEG noise gives Hamming distance 0-2, real screen changes give 15+, threshold 6, hash_size 12 (144-bit), 10% edge crop to ignore clock/status bar. SearchByVideo measured the same library (ImageHash 4.3.2): JPEG re-save at quality 30 moves 0 bits, a caption bar over 18% moves 4-12 bits, a centre crop to 60% moves 20-32 bits of 64 (near random).

Source: WiFry commit, https://github.com/lstepnio/wifry/commit/82086fa66e35802a4aad4d1f7556d1b6073b24c8 (accessed 2026-11-22). Visual drift guide, https://simpleprog.com/topics/web-scraping/layout-drift-detection (accessed 2026-11-22; "calibrate the threshold: screenshot the same unchanged page several times, note the largest distance, set the threshold comfortably above that"). Phash test, https://searchbyvideo.net/blog/how-to-find-a-video (accessed 2026-11-22; measured table above).

Goal mapping: cheap verification where exact pixels are too brittle (blinking caret, anti-aliasing). Weaker than V8 exact-region compare for our case, because typing changes many pixels and we want an exact verdict, not a similarity score.

Applicability: only if exact region compare proves too noisy in live testing (caret blink toggling the hash). Then use dHash on the input crop with a calibrated threshold, and still pair with V1/V2. Do not use phash on the whole frame: that is e4082ff with a fuzzier threshold.

Measured numbers: WiFry dHash noise 0-2 vs real change 15+, threshold 6. SearchByVideo: JPEG 0 bits, caption bar 4-12, crop 20-32 of 64. ImageHash phash is 64-bit; phash compare is microseconds (watchman doc).

Verdict: maybe. Rank 15. Fallback only, weaker than V1/V8.

### V10. AT-SPI Text interface readback + text-changed events (event-driven, zero polling)

What it is: AT-SPI2 exposes org.a11y.atspi.Text on focused elements: get_text(start, end), get_character_count(), get_caret_offset(), plus events object:text-changed:insert (carries start_pos, length, and the inserted text string itself) and object:text-caret-moved. Listening for text-changed:insert before typing gives event-driven proof that the exact string landed, with no polling and no screenshot. openwhispr's linux-text-monitor.py does exactly this in Python via gi.repository.Atspi, including a --probe-editable mode that finds the FOCUSED element in the ACTIVE window of a target pid and checks it is writable.

Source: Text change detection research, https://github.com/masonrhodesdev/wayland-voice-dictation/blob/HEAD/docs/research-text-change-detection-wayland.md (accessed 2026-11-22; Text interface table, event table, plus a 2026-07-03 validation addendum). Atspi.Text API, https://lazka.github.io/pgi-docs/Atspi-2.0/classes/Text.html (accessed 2026-11-22; get_caret_offset, get_text, get_offset_at_point, get_character_extents). openwhispr linux-text-monitor.py, https://www.armgit.com/armgit/openwhispr/blob/main/resources/linux-text-monitor.py (accessed 2026-11-22).

Goal mapping: cheap verification, event-driven (cheapest possible: the app tells us the text changed). Catches false ok for native/GTK/Qt apps where there is no DOM.

Applicability: for Zen/Firefox and GTK apps, query the focused accessible (Atspi.StateType.FOCUSED) and read get_text + get_caret_offset after typing; better, subscribe to text-changed:insert and assert the inserted string equals the typed text. Caveats from the validation addendum, must be respected: Chromium never implemented AT-SPI EditableText, so for Brave/Chrome this path is read-only at best and the DOM path (V1/V2) wins; and libatspi gives an unresponsive peer 15s to answer, so every call needs a hard timeout (openwhispr uses PROBE_ATSPI_CALL_TIMEOUT_MS = 500). Also the focused-element search must be scoped to the ACTIVE window of the target pid, or a stale FOCUSED state in another app false-passes.

Measured numbers: 15s libatspi default per unresponsive peer; 500ms probe timeout in openwhispr; no accuracy numbers.

Verdict: promising for native/GTK/Firefox, skip for Chromium. Rank 9.

### V11. MutationObserver / input-event flag (event-driven DOM verification)

What it is: install a MutationObserver (characterData + subtree) or an input-event listener on the target element BEFORE typing, then check the flag/records afterwards. The observer fires only if the DOM actually changed, so a stubbed type that dispatches nothing leaves zero records. PromptSnippets uses MutationObserver exactly this way: if event simulation did not trigger a change (detected via MutationObserver), fall back to direct DOM manipulation. thewebdev.info shows both forms: input event listener on a contenteditable div, and MutationObserver with characterData:true, subtree:true reading mutationRecords[0].target.data.

Source: ContentEditable Support, https://deepwiki.com/taterboom/PromptSnippets/7.2-contenteditable-support (accessed 2026-11-22; two-phase set: event simulation, then direct manipulation if MutationObserver shows no change). How to listen for contenteditable changes, https://thewebdev.info/2021/03/03/how-to-listen-for-changes-to-html-elements-with-the-contenteditable-attribute-with-javascript/ (accessed 2026-11-22). MDN Selection / Selection API via the same fetch set.

Goal mapping: cheap verification, zero polling, catches false ok. The observer is armed in the same evaluate call that finds the element, and read in the same evaluate call that does V1/V2, so it adds no round trips. It also catches the case where keys reached the wrong element: the observed target shows no mutations.

Applicability: before wtype, evaluate a snippet that attaches a MutationObserver + input listener to the target, stashing a window-level flag (e.g. counts + last inserted text). After typing, read the flag in the V1/V2 evaluate call. If flag is empty, type did not land even if some other check looks fine. Works for contenteditable (MutationObserver) and plain inputs (input event). Note: wtype keys are real key events, so a real type fires real input events; a stubbed type fires none.

Measured numbers: PromptSnippets 20ms settle waits. No accuracy numbers.

Verdict: promising. Rank 5. Best event-driven complement to V1/V2.

### V12. State-grounded verification / independent finish gate (verify the artifact, not the pixels)

What it is: verify the persisted result, not the screenshot and not the action return code. StateAct (2026) grounds actions and verification in program state (files, databases, app backends) and adds an independent Finish Gate: a separate process that, when the agent calls finish, reads the artifact directly (e.g. reads the file for the formula, queries the calendar store). Verification is objective state change, not the agent's own report. For our Messenger shape: after Enter, query the thread DOM (or the sent-bubble list) for the exact sent text, instead of trusting the click+type ok.

Source: StateAct, https://staging.alphaxiv.org/abs/2607.22798 (accessed 2026-11-22; submitted 24 Jul 2026; "an independent finish gate double-checks the saved result for structural failures, e.g. output that is missing, unsaved, or written to the wrong path"; "verify the persisted artifacts"). OSWorld summary, https://beancount.io/bean-labs/research-logs/2026/06/15/osworld-benchmarking-multimodal-agents-real-computer-environments (accessed 2026-11-22; OSWorld uses programmatic evaluation scripts that check actual system state after execution, no string-matching heuristics, no LLM-as-judge).

Goal mapping: cheap verification at task level, catches false ok end to end. This is the VISION 2 step of the 2-vision benchmark done cheaply via DOM: one evaluate call listing sent bubbles, instead of a second vision pass, or as a pre-check before spending VISION 2.

Applicability: after a send action, evaluate the thread DOM for a bubble containing the exact sent text (and, for Messenger, the sent marker). If absent, the send failed even if click+type both reported ok. Same pattern generalizes: after any action, read the state the action was supposed to change.

Measured numbers: StateAct on OSWorld 2.0 lifts Claude Opus 4.8 from 20.6% to 26.9% binary success and 54.8% to 61.6% partial success, at about 9x lower cost per task than screenshot-only driving; GUI subagent is only 1.1% of main-agent steps; code-only variant reaches only 45.9% partial, below the screenshot baseline 54.8%.

Verdict: promising. Rank 8. This is the task-level check; V1/V2 are the step-level checks. Both are needed.

### V13. Grounding verifier + calibrated confidence (GUI-Actor verifier, HyperClick SCRL)

What it is: propose several candidate action regions in one forward pass, then run a separate verifier to pick the most plausible one, with a confidence threshold and abstention below it. GUI-Actor's verifier is finetuned from UI-TARS-2B-SFT, takes a pool of K=20 candidates, threshold gamma 0.95 on ScreenSpot-Pro and 0.8 on ScreenSpot/v2. HyperClick trains the model to output a click prediction plus an explicit confidence estimate, with a correctness reward and a confidence-alignment reward (Brier score), so confidence matches actual accuracy and the agent can abstain when unsure. Both papers report the same diagnosis: models are overconfident relative to their real accuracy.

Source: GUI-Actor, https://arxiv.org/abs/2506.03143 (fetched 200, accessed 2026-11-22; also https://arxiv.org/pdf/2506.03143). HyperClick, https://arxiv.org/abs/2510.27266 (fetched 200, accessed 2026-11-22; "models exhibit a higher confidence in their answers than in the accuracy that they actually achieve").

Goal mapping: accuracy >= 90% without extra observes, by spending the one vision better (K candidates from one pass, verifier picks). This is the model-side version of the goal bar. Directly relevant as a pattern, not as code to import.

Applicability: we cannot train a verifier, but we can copy the pattern cheaply: from ONE vision, keep the top-K candidate points for each target instead of one point; score each candidate with DOM checks (V5 elementFromPoint, V3 focus, V6 live geometry); pick the best-scoring candidate; abstain (re-observe) if no candidate passes a threshold. That turns a single vision into a verified multi-candidate grounding step with no extra vision cost. The confidence number must come from a check (hit test pass/fail), not from the model's self-report, because HyperClick proves self-reported confidence is miscalibrated.

Measured numbers: GUI-Actor-7B + Verifier: ScreenSpot-v2 89.7 (vs 88.3 without verifier); ScreenSpot-Pro 44.6 with Qwen2.5-VL backbone vs UI-TARS-72B 38.1; verifier finetunes only the ~100M action head with the backbone frozen. HyperClick: state of the art on seven benchmarks with better-calibrated confidence (no single headline number in the abstract; do not quote one).

Verdict: maybe as a model, promising as a pattern. Rank 13. The DOM-scored top-K translation is cheap and worth testing; training a verifier is out of scope.

### V14. Auto-retrying DOM assertion with bounded polling (expect / waitForFunction pattern)

What it is: assert on the state you need, and let the assertion retry until it holds or a short timeout ends, instead of sleeping a fixed time or reading state once. Playwright's expect(locator).toHaveText / toBeFocused / toHaveValue auto-retry; its plain state reads (isVisible, textContent) answer immediately and must not be used to wait. The same idea as a CDP waitForFunction poll on a DOM predicate. The tutorial warns: assert on the content you need rather than only on the URL, because the URL can change before the page renders.

Source: Playwright Auto-waiting, https://playwright.dev/docs/actionability (fetched 200; auto-retrying assertions list incl. toBeFocused, toHaveText, toHaveValue, toHaveJSProperty). Tutorial, https://learn.sharadhaai.com/agentic-playwright/level-1-foundations/06-actions-and-auto-waiting/ (accessed 2026-11-22; "Assertions wait too, which is how you wait for a business condition rather than a technical one").

Goal mapping: cheap verification, catches slow-to-land typing (composition, IME, React state) without a full observe. A 200-500ms bounded poll on a DOM predicate is far cheaper than a vision cycle.

Applicability: wrap V1/V2 in a short poll: evaluate the predicate every ~50ms up to a small budget (e.g. 1s), succeed on first match, fail loudly after. This handles the case where wtype keys are still being processed (composition, Vietnamese IME) when the first read happens. Never poll a screenshot; poll the DOM value.

Measured numbers: none.

Verdict: promising. Rank 12. A wrapper around V1/V2, not a standalone check.

### V15. OCR on the input-region crop only (tesseract PSM 7, DOM-unavailable fallback)

What it is: crop the input rect (grim -g) and OCR only that crop with tesseract set for a single text line (PSM 7), then compare the recognized text to the expected string. Cropping removes full-screen noise and makes PSM 7 the right mode; the tuning doc warns PSM 3 on a cropped region is a silent accuracy loss (returns empty from a perfectly readable image, no warning, no lowered confidence), and PSM 6 on a real page interleaves columns. Use only where DOM readback is impossible (canvas-rendered inputs, native apps without AT-SPI text).

Source: Tesseract tuning, https://github.com/mamonet/ocr-pipeline-optimizer/blob/HEAD/docs/tesseract-tuning.md (accessed 2026-11-22; PSM table: 7 = single text line, "a cropped line: table cells, form fields"; "PSM 3 on a cropped region ... can return an empty string from a perfectly readable image"). OCR API doc, https://sstar.us/apis/ocr-tesseract-text-extraction-batch-layout-boxes/ (accessed 2026-11-22; /ocr/region crops a pixel rectangle and OCRs only that area; clean-render English extracted exactly, confidence about 93).

Goal mapping: cheap verification relative to full-screen OCR (tiny crop, single line), catches false ok where DOM is blind. But strictly worse than V1/V2 where DOM exists: OCR can misread and is slower than a string compare.

Applicability: fallback only. grim -g input rect, tesseract --psm 7, compare normalized text. Do not use PSM 3 on crops. Note the failure mode: OCR returning empty is silent, so empty OCR must mean FAIL, never "no text typed, try again later" ambiguity; pair with V8 region hash change.

Measured numbers: control-set English extracted exactly, confidence about 93 (sstar doc). No latency numbers.

Verdict: maybe. Rank 14. Fallback only.

### V16. Independent second channel rule (governing principle, not a check)

What it is: never trust an action's own return code. Every "ok" must be corroborated by an independent channel that the action itself cannot set. The e4082ff bug is the textbook violation: the type step reported its own success using a signal (whole-frame hash) that the click step could set. OSWorld's error analysis found over 75% of 550 agent failures are mouse click inaccuracies, not reasoning failures (best model 12.24% vs human 72.36%), which is why the check must be independent of the guess. Reticle's Moli experiment shows the same trap one level down: a mock-geometry browser returns plausible, wrong geometry, so a check built on that geometry passes a broken layout; the check must use the real layout path. browser-use's stale-index failure shows the same shape: the cached map says ok, only a live CDP error surfaces the truth.

Source: OSWorld summary, https://beancount.io/bean-labs/research-logs/2026/06/15/osworld-benchmarking-multimodal-agents-real-computer-environments (accessed 2026-11-22; "Error analysis of 550 failures: over 75% are mouse click inaccuracies"). Reticle Moli, https://www.reticle.sh/signal/2026-10-25-moli-headless-browser-mock-layout-visibility (accessed 2026-11-22; "On a mock-geometry browser, the answer is computed from the mock, so a broken layout passes the check"). browser-use click report (fetched 200; stale index "failure surfaces only as a downstream CDP error").

Goal mapping: this is the rule that makes V1-V15 work. Any verification whose signal the action under test can produce is not verification. The DOM value (V1) is independent of wtype's return code; the MutationObserver flag (V11) is independent of the click; the sent-bubble check (V12) is independent of the type.

Applicability: code-review rule for the fix: for each step, name the check channel and confirm the step cannot set it. Redteam must try to break each method by producing the check signal without the effect (e.g. set the hash without typing, focus the box without typing, type into the wrong box).

Measured numbers: OSWorld 12.24% vs 72.36% human; 75% of failures are grounding.

Verdict: governing principle. Rank 0, applies to all. Enforce in review, not a runtime check by itself.

## Extra supporting pattern (not a separate candidate)

agent-sh computer-use-linux (https://github.com/agent-sh/computer-use-linux, fetched 200; also https://pi.dev/packages/@agent-sh/computer-use-linux?name=sub+agents, accessed 2026-11-22): native Linux desktop control with semantic AT-SPI trees and "single-round-trip post-action verification" across GNOME, KDE, Hyprland, niri, COSMIC, i3, Sway, labwc and X11. Supports the V10/V12 direction: verification bundled into the same round trip as the action, using the accessibility tree instead of a second screenshot. No measured numbers quoted in the README. Worth reading its verification implementation as a reference when implementing V10, but do not copy its ydotool-adjacent input paths; our input stays wtype.

## Ranked list (most promising first)

0. V16 independent second channel rule (governing principle for all the rest)
1. V1 DOM input value readback, exact compare (the required fix for e4082ff)
2. V2 contenteditable innerText + caret offset (the incident shape: Muse web app input)
3. V4 caret position check (one number, distinguishes right box / wrong box / nowhere)
4. V3 activeElement focus check (shadow-root walk; free inside the V1 call)
5. V11 MutationObserver / input-event flag (event-driven, zero polling, zero extra round trips)
6. V5 elementFromPoint hit test (pre-click occlusion check, prevents the misclick)
7. V8 input-region hash via grim -g (visual fallback where DOM is blind; must pair with V1/V2)
8. V12 state-grounded finish gate (verify the sent bubble / artifact, the cheap VISION 2)
9. V10 AT-SPI Text readback + text-changed events (native/GTK/Firefox; skip for Chromium)
10. V6 CDP live geometry re-resolution (kills stale points)
11. V7 Playwright-style actionability gate + trial mode (discipline wrapper; forbid force/bypass)
12. V14 auto-retrying DOM assertion, bounded poll (handles IME/composition lag)
13. V13 grounding verifier + calibrated confidence, DOM-scored top-K pattern (cheap translation; do not train a model)
14. V15 crop-only OCR, tesseract PSM 7 (fallback only, DOM-unavailable surfaces)
15. V9 phash/dhash on the input crop (fallback only, weaker than V8 exact compare)

Recommended minimal set to test first (all in ONE evaluate call per step, no extra observes): V1 + V2 + V3 + V4 + V11 armed before typing, V5 before clicking, V12 after sending. That is the cheapest bundle that kills the proven false pass and the known redteam shapes (wrong grounding, stale points, false ok).

## Redteam notes (what must be tried live, after council review)

- V1: type into the WRONG input, then read the right input value (must fail); pre-fill the input with the expected text, then stub the type (must fail: compare against before-value, require change AND equality, not equality alone).
- V2: type into a contenteditable that strips formatting or inserts zero-width chars; check normalization does not false-pass on empty vs expected.
- V3/V4: click 64px above the input (the proven incident offset), confirm focus/caret show the miss; click a different chat thread input and type, confirm the check attributes text to the wrong box.
- V5: cover the input with a modal/banner, confirm the hit test blocks the click; use a point on the input border where elementFromPoint returns a child node, confirm descendant handling.
- V8: click inside the input rect without typing (caret blink / focus ring only) and confirm region-hash-change alone would false-pass, which is why it must pair with V1/V2.
- V11: dispatch synthetic input events without typing (must not count as typed text unless content also matches V1/V2).
- V10: try on Brave (expect EditableText gap) and on Zen/Firefox (expect it to work); leave an unresponsive AT-SPI peer in the tree and confirm the 500ms timeout holds.
- V12: send a message, then check for the bubble before it renders (timing), and check a bubble with the same text from an earlier message (must match the newest one, not any one).
- V9/V15: feed a crop with a blinking caret mid-blink and a crop with Vietnamese diacritics; record misread rates.

## Time log (wall-clock Asia/Ho_Chi_Minh, elapsed from 02:05:24)

- 02:05:24 +07, T+0s: task start. Repo fetch origin, branch todolist-push, HEAD 646cf71, remote in sync. Scrapling venv check: scrapling 0.5.1.
- 02:05:50 +07, T+26s: Scrapling plain Fetcher smoke test, MDN activeElement 200, 152734 bytes. Plain path works.
- 02:06:15 +07, T+51s: Scrapling batch 1 (elementFromPoint, activeElement, Playwright actionability) all 200. Discovery searches 1-2 done.
- 02:06:31 +07, T+67s: Scrapling batch 2 (caretPositionFromPoint, selectionStart, CDP DOM) all 200. Discovery searches 3-4 done.
- 02:07:02 +07, T+98s: Scrapling batch 3 (HyperClick abs, GUI-Actor abs, grim README) all 200. Discovery searches 5-6 done.
- 02:07:18 +07, T+114s: Scrapling batch 4 (browser-use report, CDP Runtime) all 200. Discovery searches 7-8 done.
- 02:07:31 +07, T+127s: Scrapling batch 5 (agent-sh README, MDN Selection) all 200. Crawl closed.
- 02:08-02:20 +07, T+3min to T+15min: log written. No StealthyFetcher used anywhere. No proxy failures anywhere. No live driving, no browser tasks, no implementation.

## last30days 30-day sweep (owner order 02:09 +07, parent follow-up task)

Owner order: the whole team uses last30days-skill (https://github.com/mvanhorn/last30days-skill) to crawl REAL data for the improvement research, across Reddit, X, YouTube, HN, Polymarket, GitHub, arXiv and the web in the last 30 days. HARD RULE: no old stale datasets, only fresh real data from the last 30 days. Every crawled claim carries its source and date. The skill is an additional source, not a replacement for the Scrapling work above.

### Skill install and first-run gate

- Skill already present on the VM as a repo checkout: ~/workspace/last30days-skill, skill spec at skills/last30days/SKILL.md, version 4.4.0, MIT license. Also found in earlier team work at ~/workspace/research_notes/muse-company-multi-account-20261121/last30days.
- `npx skills add mvanhorn/last30days-skill -g` hung TWICE with zero output (first run without -y killed after about 4 min, second run with -y killed after about 5.5 min). npm/npx appears stalled behind the VM proxy. The local checkout was used instead, which the skill accepts as a valid load point. The global -g copy was NOT installed; retry the npx command on a host with a working registry connection if the -g copy is wanted.
- First-run gate printed FIRST_RUN_DETECTED (no SETUP_COMPLETE in ~/.config/last30days/.env). Applied the skill's Skip path per the Research Continuation Override (topic already supplied, no browser-cookie consent from a subagent): wrote SETUP_COMPLETE=true and BROWSER_CONSENT=false to ~/.config/last30days/.env (mode 0600, appended, existing content preserved). No setup command run, no cookies read.
- Deferred onboarding note for the parent (skill rule: resume the ScrapeCreators offer after the findings): the Step 4 ScrapeCreators offer (10,000 free calls, TikTok/Instagram + YouTube comments + Reddit/YouTube backfill) was NOT presented, because a subagent cannot ask the user. If the owner wants it, present it in the main chat. No key was requested or stored.
- Runtime preflight: Python 3.12.3 at /usr/bin/python3.12. Save dir resolved to /tmp/l30d-verify (one-off, keeps research files out of the repo and out of the user's documents).
- Diagnose (--diagnose --include-research-backend): available_sources = reddit, hackernews, polymarket, github. X omitted (no cookie/API consent). YouTube omitted (yt-dlp not installed). TikTok/Instagram omitted (no ScrapeCreators key). gh CLI present and authed. Local backend.
- Step 0.55 resolution: Reddit r/AI_Agents, r/AgentsOfAI, r/LLMDevs, r/LocalLLaMA, r/AutoGPT (source: redditmaster 2026 agent-subreddit guide, crawled 21 Nov 2026). No X handle (generic concept, X inactive). No GitHub repo (concept, not a product). TikTok/IG creators skipped (not a creator topic). devto-tags ai,agents.
- Step 0.75 plan: intent factual, freshness balanced_recent (NOT evergreen_ok, to honor the 30-day rule), cluster none. 4 subqueries: primary GUI-agent verification (reddit, hackernews, polymarket, github), browser-use judge (github, hackernews, reddit), false-success self-report (reddit, hackernews, github), VeriGUI (github, hackernews).

### Engine run result (the skill ran, evidence is thin)

- Engine: python3.12 scripts/last30days.py, --emit=compact, --plan -, 150.4s. Follow-up cache ID cd1fff5cf8e64777b43349b87e289958. Saved raw: /tmp/l30d-verify/cheap-accurate-verification-methods-for-gui-computer-use-agents-raw-v3.md (Step 2.5 supplements appended to that file, 8 bullets).
- Counts: 35 items across 3 sources. Reddit 11 threads, HN 12 stories, dev.to 12 articles, Polymarket 0 markets, GitHub 0 results. Research quality 3/4 core sources, missing YouTube. Only 17 of 35 dated items from the last 7 days.
- Ranked clusters (2): "Is Coding with AI Actually Faster and Cheaper?" (dev.to, 18 Nov 2026) and "What I'm doing with my AI Agents as a normal person" (r/AI_Agents, 14 Nov 2026). Both are OFF-TOPIC for verification methods. The engine's own verdict: "Evidence is thin for this topic."
- Honest conclusion: in the last 30 days, Reddit/X-adjacent community chatter is about AI coding cost and everyday agent use, NOT about verification methods. The verification discussion lives in papers and release notes (see V17-V20 below, found by the date-focused web sweep), not in community threads. No community quote from the engine run is usable as evidence for any candidate; per the skill's nothing-solid floor, no engine comment is quoted as a finding.

### New candidates from the 30-day sweep

### V17. Expectation-first action-effect verification (VeriGUI TVAE pattern)

What it is: before acting, state the expected effect in DOM/state terms; after acting, check that exact effect and no other. VeriGUI (VeriGUI, Thinking-Verification-Action-Expectation) verifies each action outcome against predicted effects and recovers on mismatch, instead of assuming deterministic environment responses. Its diagnosis: VLM agents generate actions without verifying whether previous operations succeeded, which leads to undetected failures and repetitive ineffective behavior.

Source: arXiv 2604.05477, Zhang et al., "Don't Act Blindly: Robust GUI Automation via Action-Effect Verification and Self-Correction", https://arxiv.org/abs/2604.05477 (fetched 200 via Scrapling, accessed 2026-11-22; submitted 7 Apr 2026, ACL 2026 Main Conference).

Goal mapping: cheap verification, catches false ok. The cheap translation needs no model training: our V1/V2/V12 checks already read the effect, V17 adds the expectation (the exact string and box) written down BEFORE the action, so the check cannot be retrofitted to whatever happened. Accuracy >= 90% without extra observes, because the check is the same single evaluate call.

Applicability: in the type step, pass the expected (box, text) pair into the verify call; the verify returns pass only when value/text equals expected AND the before-value differed (kills the pre-filled false pass). Same for clicks: expected post-click state (focus element, URL, dialog) named before dispatch.

Measured numbers: execution timeouts caused by repeated ineffective actions account for 72.3% of all failures across 1,265 task executions (Liu et al., 2026, cited in the paper). No headline accuracy number in the abstract; do not quote one.

Verdict: promising as a pattern, training out of scope. Rank 8 (with V12).

### V18. Report-trace auditing / self-report leakage (freshest evidence on the exact failure mode)

What it is: an agent's confident success report must be audited against an independently recorded trace, with the self-report WITHHELD from the judge. The paper names our e4082ff shape precisely: a "dangerous misreport" is an unhedged success claim that the trace does not support as causal accomplishment. A controlled aware/blind intervention shows the self-report itself corrupts judging: withholding it improves trace-only dangerous-misreport recall by 43.4 percentage points (Qwen3.5-35B-A3B) and 13.3 points (DeepSeek-284B-A13B). The structured auditor separates claim interpretation from claim-blind trace analysis and applies deterministic rules to extracted evidence.

Source: arXiv 2610.29609, Zhu et al., "Who Verifies the Agent's Success Claim? Self-Report Leakage in GUI-Agent Completion Judging", https://arxiv.org/abs/2610.29609 (fetched 200 via Scrapling, accessed 2026-11-22; submitted 21 Oct 2026, accepted by ICSE 2027 Research Track).

Goal mapping: catches false ok, directly. This is V16 (independent second channel) proven with numbers: any judge that sees the agent's own ok is measurably worse at catching false ok. Our verify step must never receive the action step's ok flag as input.

Applicability: code rule for the fix: the verifier function takes only (expected effect, observed state), never the action's return value. Log the action claim and the trace evidence separately so redteam can audit them apart. The auditor's deterministic-rules idea maps to our exact string compare (V1/V2), not a model judgment.

Measured numbers: recall +43.4pp (Qwen3.5-35B) and +13.3pp (DeepSeek-284B) when the self-report is withheld; auditor F1 0.75-0.78 on the 465-record set and 0.77-0.81 on held-out Batch 2; under audit-stage gating it blocks 74-90% of dangerous misreports at 45-56% inspection load (16-19% of the full stream after triage).

Verdict: promising. Rank 0b (strengthens the V16 governing principle with fresh numbers).

### V19. Built-in run judge (browser-use 1.0.5, 14 Nov 2026)

What it is: every Agent.run() that took at least one step is now judged by the same model the agent uses. One extra request compares the run trace with the task and fills result.judgement with six fields: success, failure_reason, description, prompt_injection_detected, bot_block_or_captcha_detected, gotchas (up to five). The judge sees the trace, the last screenshots, and the final page (unless use_vision=False). The judge never changes the run's own result, and a malformed judge answer is not retried, so a run costs exactly one judge request.

Source: Browser Use 1.0.5 release notes via https://onlinelearningportal.website/browser-use-1-0-5-run-judge-python/ (accessed 2026-11-22; released 14 Nov 2026, PR #6398). Also: Browser Use November 2026 changelog, https://agentgid.com/agents/browser-use/changelog/ (accessed 2026-11-22; 1.0.0 to 1.0.7 in November, "AI judge to validate task completion").

Goal mapping: catches false ok at run level ("Browser agents fail in quiet ways. The run finishes, but the form was never submitted"). NOT cheap: it costs a model call per run, so it cannot be the per-step check. Its value for us is the pattern: judge the trace + final page, never the self-report (same lesson as V18).

Applicability: do not copy the model judge per step. Copy the shape at task level only: after a task, a deterministic trace audit (V12 sent-bubble check + V1/V2 logs) fills a judgement-like record. If a model judge is ever added, it must read the trace and final state, never the agent's ok flags.

Measured numbers: project tested on 13 real runs, each judged 3 times. Gotchas appeared on 15 of 15 verdicts where the site pushed back (up from 6 of 15), and on 2 of 24 verdicts for clean runs, with success verdicts unchanged.

Verdict: maybe. Rank 14 (model judge is not cheap; deterministic translation only).

### V20. Three-proof model (design doctrine, Sep 2026)

What it is: an action only counts as done once it has separately proven where it acted, who authorized it, and what actually changed. Observation must be fresh (a state read seconds ago can already be stale). Grounding must be exact: a target matching two plausible recipients is an ambiguity that stops the agent, not a silent choice. Completion is confirmed by the authoritative record, not an intermediate signal like a confirmation message a transaction can still roll back behind.

Source: Yash Sharma, "Browser Agents That Prove an Action Actually Happened", https://www.yashsharma.ai/writing/browser-computer-use-and-digital-action-engineering (accessed 2026-11-22; listed as updated 67 days ago, so about Sep 2026).

Goal mapping: catches false ok and wrong grounding, as doctrine. The "ambiguity stops, never silently chooses" rule is directly applicable to our one-vision multi-target step: if two inputs match, stop and re-observe rather than guessing.

Applicability: three rules for our code: (1) re-read state at action time (V6), (2) ambiguous target means abort to re-observe, (3) success means the authoritative record changed (V12), never a toast/confirmation message.

Measured numbers: SentinelBench (Jun 2026, 100 tasks): one model's overall score rose 0.68 to 0.75 while its score on tasks requiring an actual action reversed 0.60 to 0.50. WorkArena: cutting per-step latency from 65.7 to 30.2 seconds retained only 84% of task success.

Verdict: promising as doctrine. Rank 0c (reinforces V16/V12/V5).

### Updated ranked list (V17-V20 inserted)

0. V16 independent second channel rule (governing principle)
0b. V18 report-trace auditing (fresh numbers for V16: withhold the self-report from any judge)
0c. V20 three-proof model (doctrine: fresh observation, exact grounding, authoritative record)
1. V1 DOM input value readback, exact compare
2. V2 contenteditable innerText + caret offset
3. V4 caret position check
4. V3 activeElement focus check
5. V11 MutationObserver / input-event flag
6. V5 elementFromPoint hit test
7. V8 input-region hash via grim -g (pair with V1/V2)
8. V12 state-grounded finish gate, plus V17 expectation-first (name the expected effect before acting)
9. V10 AT-SPI Text readback + text-changed events (native/GTK/Firefox; skip for Chromium)
10. V6 CDP live geometry re-resolution
11. V7 Playwright-style actionability gate + trial mode
12. V14 auto-retrying DOM assertion, bounded poll
13. V13 grounding verifier + calibrated confidence, DOM-scored top-K pattern
14. V15 crop-only OCR, tesseract PSM 7 (fallback only)
15. V9 phash/dhash on the input crop (fallback only, weaker than V8)
16. V19 browser-use style run judge (model call, task level only, deterministic translation preferred)

Recommended minimal set, updated: V1 + V2 + V3 + V4 + V11 armed before typing, V5 before clicking, V17 expectation named before acting, V12 after sending. All in ONE evaluate call per step, no extra observes.

## Recency audit (owner hard rule: only fresh real data from the last 30 days)

Window: 2026-10-23 to 2026-11-22. Today is 2026-11-22. Every source below carries its date and its status. Older sources are kept ONLY as mechanism (how an API or pattern works) or benchmark numbers, never as fresh evidence that the method is currently used or discussed. The fresh-evidence core of this log is V17-V20 plus the engine run.

Within the 30-day window:
- last30days engine run, 22 Nov 2026: thin evidence, 2 off-topic clusters (see above).
- agent-sh computer-use-linux v0.7.59, published 20 Nov 2026: single-round-trip post-action verification.
- browser-use 1.0.5 judge, released 14 Nov 2026: run-level judge, 13 runs x3.
- SkillVeris computer-use guide, 12 Nov 2026: DOM/a11y supplement screenshots.
- KindaTechnical computer-use lesson, updated Nov 2026: a11y-tree pre-action verification.
- SearchByVideo phash test, run 9 Nov 2026: JPEG 0 bits, caption bar 4-12, crop 20-32 of 64.
- implbits phash vs SHA-256, about 1 Nov 2026 (listed 21 days ago): same method family.
- Reticle Moli experiment, 25 Oct 2026: elementFromPoint exposes mock geometry.
- redditmaster agent-subreddit guide, 2026, crawled 21 Nov 2026: used ONLY for subreddit resolution, not as evidence.

Marginally outside the window (flagged, kept for one stated reason):
- arXiv 2610.29609 self-report leakage, submitted 21 Oct 2026 (32 days before today, 1 day outside): the freshest peer-reviewed evidence on the exact false-ok failure mode, surfaced by the Nov 2026 sweep. Numbers only.

Older, kept as mechanism only (API behavior, patterns, or benchmark numbers, not current discussion):
- MDN Web API docs (activeElement, elementFromPoint, caretPositionFromPoint, selectionStart, Selection): timeless API reference, fetched 200 on 22 Nov 2026.
- Playwright actionability docs, CDP DOM/Runtime protocol, Marionette docs, Selenium type_test (4.15.2): timeless behavior specs.
- grim README (region capture -g), AT-SPI Text docs, pyatspi interface: timeless API/CLI behavior.
- StateAct, submitted 24 Jul 2026: finish-gate mechanism + OSWorld 2.0 numbers.
- GUI-Actor, submitted 3 Jun 2025: verifier pattern + benchmark numbers.
- HyperClick, submitted 31 Oct 2025, revised 27 May 2026: confidence calibration pattern + numbers.
- OSWorld summary (NeurIPS 2024 paper, Jun 2026 writeup): 12.24% vs 72.36%, 75% grounding failures.
- openclaw click-accuracy research, 15 Mar 2026: survey of grounding methods.
- VeriGUI (V17), submitted 7 Apr 2026: TVAE mechanism + 72.3% ineffective-action failure share.
- Yash Sharma three-proof model (V20), about Sep 2026: doctrine + SentinelBench/WorkArena numbers.
- browser-use click report (Browzy), commit dated 11 Sep 2026: CDP occlusion-check mechanism.
- WiFry dHash commit, watchman smart-capture doc (11 Nov 2025), simpleprog drift guide, tesseract tuning doc, sstar OCR doc, PromptSnippets/GhostType contenteditable docs, thewebdev.info MutationObserver article (2021), openwhispr linux-text-monitor, wayland-voice-dictation research (1 Apr 2026, validation addendum 3 Jul 2026), chrome-bridge clear commit: mechanism or code patterns only; the watchman 10-50x claim is explicitly flagged as an unmeasured plan, not a result.
- Chromium omnibox focus-verification patch (commit 7eaef9cf): mechanism (shadow-root activeElement walk), date not verified.

No source in this log is presented as fresh evidence when it is older than the window. No claim relies on a stale dataset for currency; currency claims rest only on the within-window items above.

## Supplement time log (wall-clock Asia/Ho_Chi_Minh, elapsed from 02:05:24)

- 02:09:52 +07, T+4min28s: log dash check (0 em, 0 en, 40985 bytes). First npx install attempt killed (hung, zero output, about 4 min).
- 02:12:21 +07, T+6min57s: Scrapling batch 5 done (arXiv 2610.29609 + 2604.05477, both 200). Date-focused searches returned VeriGUI, self-report leakage, browser-use 1.0.5 judge, three-proof model.
- 02:14:03 +07, T+8min39s: background find confirmed skill checkout already exists at ~/workspace/last30days-skill (v4.4.0). Second npx -y attempt still running with zero output.
- 02:16:26 +07, T+11min02s: first-run gate FIRST_RUN_DETECTED, Skip path applied (SETUP_COMPLETE=true + BROWSER_CONSENT=false, 0600). Python 3.12.3 confirmed.
- 02:16-02:18 +07, T+11-13min: skill docs read (SKILL.md, runtime.md, research-runbook.md, synthesis.md, setup-wizard.md, repo AGENTS.md). Diagnose: reddit, hackernews, polymarket, github. Save dir /tmp/l30d-verify. Plan written (4 subqueries, balanced_recent).
- 02:18-02:21 +07, T+13-16min: engine run, 150.4s, completed exit 0. Thin evidence, 2 off-topic clusters, GitHub 0, Polymarket 0.
- 02:21 +07, T+16min: Step 2.5 appendix written to saved raw file (8 bullets). This supplement (V17-V20, recency audit) written into the log. Second npx -y attempt killed (hung, zero output, about 5.5 min); local checkout stands as the install.

## Handoff

Deliverable is this file only. Next steps are NOT mine: council + redteam review of the ranked list, then live testing of the promising ones with live proof, redteam trying to break each method (wrong grounding, stale points, false ok reports). The 2-vision benchmark runs AFTER improvements look good, not before.
