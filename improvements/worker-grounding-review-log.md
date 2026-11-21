# Worker GROUNDING-REVIEW log: independent first-principles review of perception/grounding

Task start 06:03 +07, 22/11/2026. Wall clock Asia/Ho_Chi_Minh + elapsed throughout.
Repo: ~/workspace/computer-use-wayland, branch todolist-push, HEAD c4b0d38 at start.
Role: independent review. I did not coordinate with other workers, did not follow the current method, questioned everything. No self-diagnosis issue here: this is a review of the pipeline, not of my own work.

## 0. Verdict first

Screenshot plus vision is the WRONG perception for web content, and the repo already knows it. The DOM already knows where every element is, to the sub-pixel, in about 0.03 s. Vision re-derives that same information from a lossy JPEG with a 58.6% first-try hit rate. Every grounding failure in the record is a vision failure, never a coordinate failure: pointer error 0.5-0.9 px, 29/29 clicks executed, 0 refusals, 17/29 first-try hits (calibration E2, live laptop, Phase 2.1).

The breakthrough layer already exists in this repo. It is not the default path. The live tasks still route through screenshots because of integration gaps, not capability gaps. The three gaps that matter:

1. The clone chats live in Brave, and Brave runs with no debugging port on its default profile, so the CDP DOM path cannot reach them (scripts/cdp.mjs harvest comment). This is the single highest-leverage blocker.
2. The action interface only speaks image coordinates, so even exact DOM rects are degraded back into the lossy image frame before they can be clicked (scripts/dom_act.py ground_many_one_shot returns image points via fastpath.dom_rect_to_image_point).
3. act-now always captures its after-image screen-scoped by construction (first_action.py hardcoded observe_screen), so reusing any after-image for a key/type step always fails (independent investigation 5f5a2fd, confirmed from source).

My recommendation, plainly: rewrite the action interface and the Brave launch path. The DOM layers themselves do not need rewriting. Demote screenshots to a last-resort fallback for canvas, games, video, and Zen's own chrome UI. Make DOM/a11y the default perception, element-ref addressing the default action form, and DOM-assert the default verification. Details and evidence below.

## 1. What I verified, with file and line evidence

### 1.1 Vision is the only error source, measured

- Calibration E2, live laptop screen, Phase 2.1 (documented in memory files, proactivity hidden files 1795237364036 and 1795240963795, and memory/people/luna-6.md): pointer and coordinate math exact, 29/29 real clicks executed with only 0.5-0.9 px pointer error and 0 refusals, but first-try hit rate only 17/29 (58.6%). Every miss was vision grounding error, a frame error of about 1.10x on the x-axis. The "screen ratio 1.55x" story is refuted, the screen is 1920x1200 at scale 1. Fix direction recorded there: take coordinates from DOM rects or correct the frame, never guess pixels from screenshots.
- G30, error file ~/workspace/cf26-upload/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md lines 302-310: 3 act-now batches reported ok/completed but the message never entered the thread. The 50 px offset hypothesis was refuted by a 3-point probe (clicks exact 0-1 px). The TYPE-on-contenteditable hypothesis was refuted (same wtype path types fine once the input is really focused). Proven root cause: vision-grounding, Muse clicked (250,1037), 64 px above the real field (field y 1101-1164, center (306,1132)); CL1-MSG2 clicked (300,1026), 75 px too high. Codex re-grounded from a fresh observe, clicked (300,1132) dead center, saw the caret, typed, Enter sent at once.
- G31 (not yet in the error file, grep finds no G31 entry, gap for the error-file phase): Muse's eyeball read of the input was (307,1085), 45 px too high, same failure mode as G30, caught before clicking by the visual grounding tool, which gave the authoritative point. Source: ~/workspace/cl2msg-direct-log.md and the parent brief.
- The vision model call itself is the unmeasured dominant cost. Capture is 15-30 ms (cu.py observe, grim). The model read that locates the target is seconds and is not timed anywhere in the repo. The repo optimizes capture (ms) while the locate step (seconds) sits outside its measurement. The 10x loop cannot optimize what it does not measure.

### 1.2 DOM grounding, measured by clone2 (batch 7 task 2, council and redteam corrected)

Source: docs/clone2-dom-grounding-20261122.md on origin/main (commits 455b6e8, 3fd6986; not present on todolist-push working tree, read via git show origin/main). Measured on headless Firefox 160.0.1 as the Zen stand-in, fixture tests/dom_grounding_fixture.html, 66 interactive elements, bench tests/dom_grounding_bench.py:

- One-shot all 66 rects: Marionette pooled median 0.030 s (9 samples, range 0.0085-0.096); BiDi run medians 0.006-0.054 s. Rect agreement BiDi vs Marionette max delta 5.7e-14 px, effectively zero. One-shot vs per-element max delta 0.0 px exactly.
- Per-element rects: 1.63 s median total, 54x slower than one shot. The naive loop is the trap.
- Screenshot PNG 1280x814: 0.037 s pooled median, capture only, no locate step. The capture is cheap; the locate is the cost, and the screenshot path pays a model call for it every time.
- 5 pointer clicks from one snapshot: 1.49 s total median, all 5 landed, 3 runs of the click step.
- 5 DOM clicks (.click() in one evaluate): 0.0022-0.0053 s total. DOM clicks skip the input pipeline.
- Verify by one DOM read: 0.002-0.015 s.
- Accessibility snapshot (Selenium 4.53, 2026-11-17): whole page first 0.045-0.147 s, repeats 0.019-0.070 s, 83 nodes; one element 0.013-0.023 s. Computed from DOM (WAI-ARIA, html-aam, accname), not the browser's own tree. No coordinates in the Python binding, so geometry still comes from the DOM rect.
- Session start is NOT free: BiDi session.new 1.51-2.77 s on a fresh browser, 0.014 s warm; Marionette attach 2.65-4.12 s. The BiDi win is in rect reads and DOM clicks, not in session start.
- Hard constraint, proved in all four runs: Firefox 160 allows exactly one active remote session per browser instance, across protocols. A Marionette session blocks a BiDi session with "Maximum number of active sessions". Never design a flow that needs both at once on one browser.
- CDP is dead on Firefox and Zen: removed in Firefox 141, /json endpoints return 404. Do not build on it for Zen. (Chrome/Brave still speak CDP; that is the clone-chat path, section 1.5.)

### 1.3 The DOM layer already exists on todolist-push

- scripts/zen_dom.py harvest() (lines 905-976): one evaluate returns rects for every selector, plus moz_inner, devicePixelRatio, screenPixelsPerCSSPixel, zoom, inner/outer size, hit and focused flags. Shadow-DOM piercing included. Docstring states the measured win (66 rects 0.019 s Marionette vs 16 ms per element, 55x slower).
- scripts/dom_act.py ground_many_one_shot() (lines 240-331): one evaluate for the whole inventory, zero observes, fails fast before any click when any selector is missing, uncovered, or maps outside the image. GroundPoints class (lines 208-239) live re-validates on read.
- scripts/dom_act.py focus_type() (lines 425-491): focus_check and type_check hooks, cheap DOM reads, no screenshot.
- scripts/fastpath.py dom_rect_to_screen_point() (lines 152-180): exact screen point from a DOM rect center plus absolute viewport origin plus scale factor. Docstring: "No screenshot is read: the DOM rect is ground truth, so the point is right the first time."
- scripts/cu.py desktop_act() (lines 1619+): focus_check runs before every type group, type_check runs after execution. The code already knows pixel verification is weak: the _input_line_changed docstring (lines 1023-1076) states plainly that a True there is necessary, not sufficient, proof the text landed, and "the DOM value check is the sufficient check". The hooks are optional. That optionality is the defect.
- scripts/cu.py act subcommand (line 2717): --dom-selector wires the DOM value hooks into the batch instead of the pixel band. Exists, not the default.
- scripts/cu.py browser subcommand (line 2723) and a11y subcommand (line 2728): the CDP and AT-SPI paths are first-class CLI, not hidden helpers.
- docs/zen-dom-control-comparison.md (measured live on the laptop 21/11, 5 tools): zen-mcp 1.2.3 WORKS, read DOM 3-5 ms, click 2-3 ms, fill 7 ms, JS evaluate 2 ms, fastest of all tools on live Zen. Selenium + geckodriver read DOM 14 ms, click 66 ms verified (headless only). Puppeteer BiDi click FAILED. Playwright moz-firefox BROKEN.

### 1.4 The image-coordinate degradation (the central architectural smell)

ground_many_one_shot returns IMAGE points, not screen points: it calls fastpath.dom_rect_to_image_point (fastpath.py lines 195-243), which takes the exact screen point from dom_rect_to_screen_point and maps it BACK into image coordinates (screen minus region origin, times image size over region size) so desktop_act can click it. desktop_act only speaks image coordinates: every click goes through cu.image_point (cu.py lines 1000-1005), image px to global px via the region origin.

So the pipeline is: exact DOM rect (CSS px) -> exact screen point -> lossy image point -> back to screen point at click time. The round trip through the image frame exists only because the action interface demands an observation image. The Pointer itself takes screen coordinates (cu.py Pointer class lines 1426+, command uses normalized 0-1,000,000 screen coordinates, verified against cursorpos with a 3 px tolerance). The image frame is pure overhead for grounded actions: it adds a conversion, a failure mode (point outside the image = refusal), and a stale-observation coupling, and buys nothing.

The coordinate-frame tower that only exists to serve the screenshot path: image px -> region origin -> window bounds -> monitor box -> screen px -> CSS px (factor). Each conversion is a proven bug site: F2b-1 (region vs monitor_box origin), C12 (window-relative vs absolute origin, mozInnerScreenX/Y are window-relative in this Zen build, probe 03:36), amend3 step 5 (viewport geometry unit mixing), G28 (screen scope refuses key/type, cu.py:1649), the after-image scope trap (section 1.6). First principles: a tower with five frames and five historical bugs is not a tower to patch, it is a tower to delete. The DOM path needs exactly one conversion (CSS px to screen px, one factor) and it already exists.

### 1.5 The Brave gap (why live tasks still use screenshots)

scripts/cdp.mjs (616 lines) is a complete DOM-first driver for Chromium: observe (snapshot of interactive elements with refs, roles, names, values, disabled, offscreen, no screenshot unless --image), harvest (one-shot rects plus Accessibility.getFullAXTree plus DOM.getBoxModel cross-check), act (click, confirm_click, hover_click, fill, set_value, key, scroll, wait, assert) by ref or selector, with stale-snapshot guards (90 s, URL check), hit tests, hover-state verification, fill read-back verification, assert polling. no_after mode skips the after-snapshot when the final action is an assert: verification by DOM assert, not by screenshot. It is wired into cu.py browser() (line 2208) and scripts/browser_worker.py (persistent Node worker, never retries input).

The harvest comment in cdp.mjs states the open item plainly: the remote-debugging-port needs a custom profile/relaunch vs the already-logged-in Brave (Brave holds no debugging port on its default profile), so this operation runs against the agent-managed Chromium, not Brave, until that is resolved.

The clone chats live in Brave on ws2. The live messaging tasks (CL1-MSG, CL1-MSG2, CL2-MSG, CL1-SWEEP) all used the screenshot path on Brave because the CDP path cannot reach Brave today. The capability exists; the launch does not. Chrome and Brave accept --remote-debugging-port at launch on the existing profile, so login persists and tabs restore; the running instance must be closed first because a second launch forwards to the existing instance and the flag is ignored. That relaunch is the single highest-leverage change in this review. It was not attempted here because clone1 is mid-batch-8 and killing its Brave window would disrupt it. Proposed as a controlled experiment in section 3, step 3.

### 1.6 The after-image scope trap (independently proven, not mine)

Independent investigation 5f5a2fd (worker CL1SWEEP-FAIL-INVEST, log improvements/worker-cl1sweep-fail-invest-log.md): the 05:49 CL1-SWEEP Enter failure. My parent's diagnosis (used a full-screen after-image as the observation) was confirmed but incomplete. Root cause one level deeper, proven from source: first_action.py always captures the envelope after-image with cu.observe_screen (line 656, max_width 1920), regardless of input scope, and overwrites desktop_act's scope-matching after-capture (cu.py:2083-2091). So every act-now after-image is screen-scoped by construction, and reusing ANY of them for a key/type step will ALWAYS fail. Consistency proof: CL2-MSG's after-image f2bdb0d34ead is also scope screen; the trap existed then and just did not bite. The proposed fix (scope-matching after-capture, or return both after and after_screen; move the scope check before the overlay attempt) is a rewrite of first_action.py's capture, not a procedure patch. I endorse it and add: the trap exists because the observation is treated as a capability (its scope gates which actions are legal) instead of as data. A screenshot should never be a capability token.

### 1.7 Where screenshots are legitimately the only perception

- Zen's own chrome UI (sidebar, urlbar, tabs, settings): AT-SPI cannot see Zen (C12 probe, live). scripts/zen_cli.py has no chrome-context support (grep for chrome/set_context returns nothing). Marionette chrome context (set_context("chrome")) is the untested DOM path for Zen chrome; until it is proven, screenshots are the only perception for Zen's own UI. Keep them there, and say so explicitly, instead of pretending the screenshot path is general.
- Canvas, games, video: no DOM, no tree. Screenshots are the fallback by definition.
- One final human-visible outcome check: the 2-vision benchmark's VISION 2 is a look at the two threads. That look is for the human, not for the machine: the script scores by outcome in the thread DOM (V12 sent-bubble gate), never by point-in-box.

### 1.8 The benchmark already embodies the breakthrough design

tests/two_vision_bench.py on origin/main (868 lines, batch 8 task 1, BUILD ONLY, no live run yet): VISION 1 is a DOM harvest, NOT a screenshot (docstring states this explicitly, gap D5). The agent's two vision calls are (1) read the numbered inventory text to pick the two message inputs, (2) look at the two threads once at the end to confirm both bubbles. The script itself never reads a screenshot to locate anything. HCU-style live guard re-checks the target's live geometry, stop-at-first-failure, exactly-once intents, V12 sent-bubble gate after each message, scoring by OUTCOME (message in the thread DOM), never point-in-box. Transport Marionette only (one-session constraint). Open items recorded in its TODOs: Brave CDP box model and AX tree (Chromium path only); no BiDi/Marionette handover protocol under the one-session constraint (D1); a production V11 MutationObserver flag for the Messenger page (the fixture counts input events, a real page needs a real observer armed before typing). The benchmark is the proof vehicle for this review's proposal, not a separate thing.

## 2. First-principles weaknesses of the current perception pipeline

W1. Vision re-derives structured information lossily. A screenshot is a lossy projection (JPEG q90, 901x1176) of a structured tree. Reading it back with a model is an inverse problem with a measured 58.6% first-try hit rate and 45-75 px eyeball errors. The DOM is the source of truth and hands over the same numbers exactly in 0.03 s. Any pipeline that prefers the projection over the source is wrong by construction, not by tuning.

W2. Actions are addressed by pixels in an image, not by elements. The interface forces every action through the five-frame tower (section 1.4). A click that misses by 64 px (G30) is not a aiming error, it is an addressing error: the action was addressed to a point in a picture, and the picture was read wrong.

W3. Verification by pixels is admitted insufficient by the code itself (cu.py _input_line_changed docstring). A pixel band can pass when text lands in a different field on the same line, and a caret blink can change the band. Verification by DOM state (field value, activeElement, sent bubble in thread DOM) is sufficient and 100-1000x cheaper (0.002-0.015 s vs a re-screenshot plus a model read). A pipeline that verifies by the weaker signal when the stronger one is available is wrong by construction.

W4. Observation is a capability token, not data. desktop_act refuses key/type on screen observations (cu.py:1649), and act-now's after-image is screen-scoped by construction (section 1.6), so the chain breaks exactly when a task needs to type. The observation's scope gates legality. First principles: an observation should describe the world, never authorize the next action. The scope check should not exist in this form; the executor should take the target window and the action and do it.

W5. Two perception stacks, no routing rule. The DOM stack (Zen Marionette/BiDi, Chromium CDP, AT-SPI) and the screenshot stack (grim + model) coexist with no rule for which one a task uses. Live tasks pick the screenshot path by default because it is the only path that works on Brave, not because it is the right path. A system with two perception stacks and no router will always drift to the worse one, because the worse one works everywhere and the better one needs setup.

W6. The session model is unhandled. One remote session per Firefox instance, no BiDi/Marionette handover protocol (bench TODO D1). Any design that needs grounding on BiDi and real input on Marionette for the same browser has no defined sequence. This will bite the first live task that needs both.

W7. The dominant cost is unmeasured. Capture 0.03 s, DOM rects 0.03 s, DOM clicks 0.001 s, pointer clicks 0.30 s, DOM verify 0.002-0.015 s, all measured. The vision model read, seconds per call, is timed nowhere in the repo. The 10x loop is optimizing the measured milliseconds while the unmeasured seconds dominate total wall time. Measure it or the loop is blind.

W8. Staleness is handled by re-observation, not by refs. A screenshot is stale the moment the page mutates, and the fix today is another screenshot. The DOM path has refs with staleness guards (cdp.mjs 90 s + URL check, snapshot id; GroundPoints live re-validation). Staleness should be detected by the ref, not by taking another picture.

W9. The "one vision" goal is misnamed in a useful way. The benchmark's VISION 1 is a DOM harvest and its VISION 2 is a human look. The machine never locates from pixels in that design. The goal bar (one vision drives max actions, accuracy >=90%, minimal total wall time) is already achievable by the DOM design and unachievable by the screenshot design at 58.6% first-try accuracy. The goal does not need a better vision model; it needs vision to stop being the locator.

## 3. The breakthrough proposal, concretely

P1. Make DOM/a11y the default perception, with an explicit router. Rule, in order: web page in Zen -> Marionette/BiDi harvest + a11y snapshot; web page in Chromium -> CDP observe/harvest; native app with AT-SPI -> a11y tree; else -> screenshot. Encode the router in code (a single function that returns the perception source for a target), not in convention or in worker briefs. Screenshots become the last branch, not the first.

P2. Rewrite the action interface: element-ref addressing. Actions address (ref or selector) plus a live rect re-read at execution time; the executor computes the screen point once from the live rect (fastpath.dom_rect_to_screen_point already does this exactly) and clicks via Pointer. Add a screen-point action form to desktop_act (or a grounded batch form that takes selector to screen point) so grounded actions never touch image coordinates. Delete dom_rect_to_image_point from the live path (keep it for tests and legacy). This deletes the five-frame tower for grounded actions and with it F2b-1, C12, amend3-step-5 class bugs. This is the rewrite the owner authorized on 06:01 (first principles: if the design was wrong from the start, rewrite it).

P3. Fix the Brave gap: controlled relaunch experiment. In a quiet window (clone1 between batches, never mid-batch): close Brave, relaunch with --remote-debugging-port=9223 on its existing profile, verify /json/list shows the Muse tab and the login intact, run cdp.mjs observe and harvest against it, run one fill plus assert on a scratch input, verify. If it works, the clone chats move off screenshots entirely and the live messaging tasks become CDP tasks. If Brave refuses the port on its default profile, fall back to: run the clones' chats in the agent-managed Chromium (login once, session persists in its profile) and drive them by CDP. Either way, the outcome is the same: no more screenshots for chat tasks. Do not run this experiment while clone1 is mid-batch; coordinate the window with the coordinator.

P4. Fix the after-image scope defect in code (investigator 5f5a2fd): make the act-now after-capture match the input observation's scope, or copy desktop_act's scope-matching result['after'] into the envelope; best shape return BOTH after (scope-matching, chainable) and after_screen (full monitor, verification only, documented non-chainable). Move the scope check before the overlay attempt. Add a regression test for after-scope matching. And delete the scope-as-capability rule: the executor should not refuse key/type based on the observation's scope.

P5. Make DOM verification mandatory, delete pixel verification as a success criterion. focus_check and type_check become required (not optional hooks) for any batch containing a type action; the CDP path already verifies fill by read-back and assert by polling. Keep the pixel band only as a diagnostic, never as a pass signal. The V12 sent-bubble gate in the benchmark is the model: outcome in the DOM, not pixels.

P6. Measure the vision call. Log vision-call latency in the harness (observation to located target, seconds). Until that number is in the logs, every speed claim about the screenshot path is incomplete. This is a harness change, not a model change.

P7. Define the session handover protocol (bench TODO D1): one protocol per browser instance per task phase, with an explicit sequence (ground and plan on BiDi, hand over to a fresh Marionette session for real input, or stay on one protocol). Write it down before the first live task needs both.

P8. Zen chrome UI: test Marionette chrome context (set_context("chrome")) as the DOM path for Zen's own UI. If it works, the last screenshot-only surface falls. If it is blocked without a restart (C12 note), keep screenshots ONLY for chrome UI and record that boundary explicitly. AT-SPI cannot see Zen, so that path is closed; do not spend more time on it.

P9. Keep one screenshot, for the human. VISION 2 in the benchmark (a look at the two threads at the end) stays, because the owner wants to see the result. The machine scores by DOM; the screenshot is evidence for the human, not perception for the machine. That is the correct division: screenshots are a human evidence channel, not a machine perception channel.

Rewrite assessment, plainly: P2 (action interface) and P3 (Brave launch) are substantial rewrites and are the ones that change the outcome. P1, P5, P6 are mostly rewiring existing code. P4 is a focused fix in first_action.py plus a test. The DOM layers (zen_dom, dom_act, cdp.mjs, a11y) do NOT need rewriting; they need to become the default instead of the opt-in. The total rewrite is of the routing and the action interface, not of the perception engines. If the team only does one thing, do P3: it moves the live tasks off screenshots and everything else follows.

## 4. What I did not verify (honest limits)

- I did not re-run the DOM bench live. The repo venv and the Firefox/geckodriver tools clone2 used are not present in this session (no .venv, no pytest, ~/workspace/tools empty on this listing). All bench numbers above are clone2's, council and redteam corrected, cited with their source. My independent contribution is the code-level derivation: I read cu.py, first_action.py, cdp.mjs, zen_dom.py, dom_act.py, fastpath.py, a11y.py, the benchmark script, the error file, and the Zen DOM comparison doc, and traced the exact failure paths. The structural claims (image-frame degradation, scope-as-capability, five-frame tower) are proven from the code itself, not from the bench.
- I did not test the Brave relaunch (section 3, P3). It would kill clone1's Brave window mid-batch-8. It is proposed as a controlled experiment, not claimed as done.
- AT-SPI live numbers are unverified on this VM (no daemons, no pyatspi), same as clone2's report. The linux-use 48 ms figure is author-reported, not measured here.
- G31 is not yet in the error file (grep finds no G31 entry). The facts are in ~/workspace/cl2msg-direct-log.md and the parent brief. The error-file phase should add it.
- Zen chrome-context Marionette access is untested (P8). The C12 note says chrome-context eval is blocked without a Zen restart; I did not re-probe it.

## 5. Evidence index

- Calibration E2: memory files (proactivity hidden files 1795237364036, 1795240963795), memory/people/luna-6.md. 17/29 first-hit, 0.5-0.9 px pointer error, 29/29 executed, 0 refusals.
- G30: ~/workspace/cf26-upload/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md lines 302-310. G28 lines 293-296, G29 lines 297-301.
- Clone2 DOM numbers: docs/clone2-dom-grounding-20261122.md on origin/main (455b6e8, 3fd6986).
- Zen DOM comparison: docs/zen-dom-control-comparison.md, live laptop 21/11, zen-mcp 3-5 ms DOM read, 2-3 ms click.
- Harvest: scripts/zen_dom.py lines 905-976. One-shot grounding: scripts/dom_act.py lines 240-331. Screen point: scripts/fastpath.py lines 152-180, image point lines 195-243. Image point conversion: scripts/cu.py lines 1000-1005. Desktop act: scripts/cu.py lines 1619+. Scope refusal: scripts/cu.py line 1649. Pixel band admission: scripts/cu.py lines 1023-1076. After-capture: scripts/first_action.py line 656, scripts/cu.py lines 2083-2091 (per investigator 5f5a2fd). CDP driver: scripts/cdp.mjs, wired at scripts/cu.py line 2208 and scripts/browser_worker.py. Browser/a11y CLI: scripts/cu.py lines 2717-2728. Benchmark: tests/two_vision_bench.py on origin/main, 868 lines.
- After-image scope investigation: improvements/worker-cl1sweep-fail-invest-log.md, commit 5f5a2fd.

## 6. Log of this review

- 06:03 +07 (T+0s): task received, repo on todolist-push HEAD c4b0d38, started reading.
- 06:03-06:05 +07: read zen_dom.py harvest, cu.py observe/desktop_act/image_point, first_action.py after-capture, dom_act.py ground_many_one_shot, fastpath.py conversions, a11y.py, cdp.mjs (full), two_vision_bench.py docstring and gates, G28/G29/G30 in the error file, clone2 DOM report (origin/main), Zen DOM comparison doc. Confirmed the 17/29 calibration from memory files.
- 06:05 +07 (T+2m): attempted a live re-run of the DOM bench, environment absent (no .venv, no pytest, no tools dir). Recorded as an honest limit, did not claim numbers I did not measure.
- 06:05 +07: wrote this log, committing with explicit pathspec, verifying with git ls-remote.

Verdict restated: screenshots are a human evidence channel, not a machine perception channel. The machine should perceive through DOM and accessibility trees, act by element ref, and verify by DOM assert. The code for that already exists; the work is to make it the default, rewrite the action interface that forces exact answers through the lossy image frame, and fix the Brave launch so the live tasks can use it.
