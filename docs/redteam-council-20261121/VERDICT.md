# REDTEAM COUNCIL VERDICT - Zen automation + error-fix campaign
# Date: 21/11/2026, council ran 03:32-03:41 Asia/Ho_Chi_Minh
# Workers: 5, all completed, no blockers over 15 min
# Sources: worker1-bidi-verification.md, worker2-todolist-redteam.md, worker3-coordinate-redteam.md, worker4-overlay-flicker-redteam.md, worker5-speed-crawl.md
# Rule: no fabrication, every claim cited or marked UNVERIFIED. No em/en dashes.

## 0. Council verdict in one paragraph

DOM-first is the right direction but oversold, the todo list is already stale, and the story told about why clicks miss is wrong on the numbers. BiDi is confirmed real and the best available path for Zen, with Puppeteer connect, Selenium connect-existing, and Playwright launch-only all verified against live sources. But BiDi cannot attach to an already-running Zen, it fixes only browser clicks (not file picker, native dialogs, or other apps), it cannot see shadow DOM or iframes, and el.click() bypasses the hover state the Browse button needs. The click misses fit a vision grounding misread, not a screen-ratio error: live monitor is 1920x1200 scale 1, and the observed offsets are 22-33 percent below what the 1.55x ratio story predicts. The overlay flicker remains unexplained. Static audit found no normal 10 Hz pill command source, but has not identified a live cause; GTK, compositor, plugin, and client behavior remain unverified. The todo list needs a Phase 0 calibration-first experiment, pre-registered pass criteria, a go/no-go date, session management, bot-detection and upload tests, and a rewritten Phase 5. The fastest path forward is hybrid: DOM locate plus real mouse click, batched actions, diff-only observation, stale-layout guard, AT-SPI for desktop apps.

## 1. Verified facts (live sources, 21/11/2026)

### 1.1 BiDi and Firefox automation (Worker 1)
- CDP removed in Firefox 141 (released 22 July 2025, not June 2025). BiDi is the replacement. Sources: MDN, Bugzilla 1882096, Firefox Source Docs.
- Puppeteer BiDi connect CONFIRMED: Bugzilla 1943416 contains the exact puppeteer.connect({browserWSEndpoint: 'ws://127.0.0.1:9222/session', protocol: 'webDriverBiDi'}) test, plus pptr.dev 25.18.1 docs. Caveat: proven against Firefox/Marionette, not live-tested on Zen itself.
- Selenium --connect-existing CONFIRMED via Firefox Source Docs geckodriver Flags: existing instance must have Marionette enabled (--marionette, default port 2828).
- Playwright connectOverCDP Chromium-only CONFIRMED via official Playwright docs. moz-firefox is launch-only, no attach path found. Playwright browser.bind() (v1.59) binds a Playwright-launched browser only, does not change the attach conclusion.
- Mozilla firefox-mcp rename CONFIRMED: repo mozilla/firefox-mcp, npm @mozilla/firefox-mcp, old @mozilla/firefox-devtools-mcp still works as alias. Stars 589, commits 440, releases 45. --connect-existing needs both --marionette and --remote-debugging-port, idle timeout 1800s, confirmed verbatim from README.
- Current versions: Firefox 160.0.1 (17/11), Zen 1.24.3b on Firefox 160.0.1 (18/11), Playwright 1.65.1 (13/11), Puppeteer 25.18.1, Selenium 4.53 (17/11), W3C BiDi Draft Standard 13/11/2026.
- zenpilot latest on PyPI is 0.7.0 (18/11/2026), not 0.2.1. Linux tried on NixOS Wayland. zenpilot cannot run its own JavaScript and cannot touch cookies, passwords or downloads, with a fresh logged-out default profile.
- zen-mcp (sh6drack) is stale: v1.2.1, last commit 16/05/2026.
- Firefox 129 was August 2024, not May 2024. Firefox 141 was 22 July 2025, not June 2025. The prior research report has 2 wrong dates and 1 badly outdated version.

### 1.2 New developments since the prior research (Worker 1)
- Nightly dynamic BiDi start: experimental pref remote.experimental.dynamicstart.enabled plus Remote Control panel can switch BiDi on at runtime on Nightly, container-isolated in Firefox 160 (bugs 2072964, 2081128). Golden rule (restart needed) still holds on stable. Top item to live-test next.
- Official Selenium MCP server: @selenium/mcp started in Selenium 4.53, repo SeleniumHQ/mcp, Chrome-first for now.
- New extension MCP candidates: FoxMCP 1.7.0, Foxhand 0.5.9, FF MCP Bridge 1.0.2 (15/11), Agent Browse, plus navigera --attach firefox (experimental) and agent-browser Firefox attach merged in November.

### 1.3 Speed and state of the art (Worker 5)
- For Zen, DOM plus BiDi is the best available path, not close. Screenshot plus mouse is the fallback.
- State of the art in late 2026 is hybrid, not pure DOM or pure screenshot: programmatic plus semantic (accessibility tree) plus visual, with batched actions, diff-only observation, stale-layout guard. Microsoft Hybrid Computer Use is the clearest published version (repo created 8 Oct 2026, MIT): up to 64 actions per AX call, diff-only returns, stale-layout guard. OSWorld 1.0 70.13% vs 62.47%, cost minus 59.1%; Windows Agent Arena 80.86% vs 71.89%, cost minus 50.6%. Calc task: HCU 4 turns about 27s vs pure GUI 6 turns about 41s vs CUA Driver 11 turns about 74s.
- AT-SPI on Linux is real and fast for desktop apps, but does NOT replace BiDi inside Zen. linux-use walks 28 elements in 48 ms; CUA docs claim 5 to 15 ms per Linux AT-SPI event. Vercel agent-desktop 1.0.0 (27 Oct 2026, Linux via AT-SPI), 1.0.2 (30 Oct 2026), 25,734 stars verified live. Wayland synthetic input is the weak point in linux-use, agent-desktop, and CUA alike.
- DOM vs screenshot: viewport-scoped tree beat a screenshot on 5 of 6 pages (Python docs 229 tokens vs 1,365), while full tree cost 2.8 to 14.5x one screenshot (dev.to, measured 17 Nov 2026). D2Snap downsampled DOM 73% vs 67% grounded screenshot on Mind2Web. WindTunnel WebMCP 96 to 98% solved, 3 to 5x faster, 3 to 8x cheaper, but Chrome-only, trial expired 17/11/2026, Mozilla neutral, WebKit opposes, so unusable for Zen.
- Grounding: GPT-4o alone 0.8% ScreenSpot-Pro; OmniParser V2 plus GPT-4o 39.6%; GTA1-7B 50.1%; Jedi-7B 39.5%; OSWorld-Verified top 90.19% (Jul 2026) vs OSWorld 2.0 best 44.3 to 44.44% (Sep/Oct 2026).
- Firefox allows only one BiDi session. Accessibility tree is still a missing BiDi module. Mozilla milestones M19 (29 Mar 2026), M20 (28 Jun 2026, screen recording, element scrolling), M21 (27 Sep 2026).

### 1.4 Todo list state (Worker 2)
- Phase 1 is half executed and the list does not know it. ~/workspace/zen-automation-test-results-20261121.md (02:56-03:25 on 21/11) already answers two of five tools: Playwright confirmed dead for Zen (launch also fails with Zen-specific "openWindow() not supported in Zen"), zen-mcp 1.2.3 WORKS (ops 2-20ms), zenpilot 0.7.0 WORKS (click 439ms, type 478ms). Puppeteer, Selenium, firefox-mcp results still pending in that file.

## 2. Challenged assumptions (the council's adversarial findings)

### 2.1 The "screen ratio" story for click misses is WRONG on the numbers (Worker 3, strongest finding)
- I1 clicks at image-x 805/825 hit Remove, 837/850 hit Rejudge. The ratio story (model multiplies by window width 1863 instead of image width 1200, a 1.55x error) predicts clicks near x=1196 for a true View at about 770. Observed values are 22-33 percent below that.
- The misses are small (tens of px) and confined to small adjacent links, which fits a vision grounding misread, not a frame error.
- Live monitor measured: 1920x1200, scale 1, transform 0. Logical equals physical pixels. A 1863-wide window could not have fit on 20/11 under any scale above 1, so monitor scale was 1 during the incident too. There is no monitor scale factor to mis-handle. Do not build the fix on the screen ratio story.
- The audited pipeline (cu.py, the on-laptop driver) is exact: grim capture in logical pixels, LANCZOS resize to max-width with exact inverse mapping in image_point, pointer move via native binary with live 3px cursorpos verification that refuses the click on a miss. The OS pointer is exonerated for I1/I2: if a click lands on Remove, the mapped point itself was over Remove. Error enters at stage 3 (model reads the image) or stage 4 (model supplies coords in the wrong frame), never stage 5. The 0.644 factor is purely the screenshot downscale, and it only matters by shrinking targets to 64 percent, amplifying grounding error on adjacent links.
- The misses happened on the VM Muse driver, whose code is not in this repo. That explains I7 (on-laptop agents accurate, VM Muses miss): same screen, same buttons, different drivers. Driver B's screenshot frame could not be audited here. Open item for the parent.

### 2.2 DOM-first is directionally right but oversold (Worker 2)
- The click-miss evidence is a systematic rightward offset, which is the signature of a coordinate-transform error, and the user named calibration as the root cause (I6, 19:27). DOM routes around it; calibration fixes it directly, including for every non-DOM surface.
- DOM cannot fix the overlay flicker (cause explicitly unknown), fabrication, blocker reporting, or think time.
- The 10x claim contradicts the project's own Pick 4 measurement: think time is about 94% of wall time, and the fast path moved the clean task pair only 43.7s to 41.7s (about 5%).

### 2.3 BiDi is a partial fix, not 100 percent (Worker 3)
- Rects are layout-engine ground truth, and BiDi input.performActions deletes the window-origin, chrome-offset, and DPR conversions. But: rect center fails for rotated/skewed elements (Mozilla Bug 1496683, needs getBoxQuads), querySelectorAll cannot see shadow DOM or iframes (cdp.mjs counts frames but cannot click inside them), wrapped inline links can have centers in gaps, sticky headers can cover after scrollIntoView, the model can still pick the wrong ref, and el.click() bypasses hover behavior the Browse button needs.
- Biggest practical blocker: BiDi cannot attach to the already-running Zen. Mozilla's own MCP docs and cdp-toolkit (verified on Firefox 153.0.3) say flags are ignored on a running instance; clone1's Bug 1943416 attach claim conflicts with those sources and is unverified on Zen. Restarting Zen or a separate profile both cost the logged-in session; only the unverified WebExtension bridge reaches live tabs.

### 2.4 The overlay flicker cause remains unknown (Worker 4 evidence review)
- Static inspection found no normal 10 Hz command source in the audited repo paths. The capture fence can hide and show the pill around each screenshot. At the reported rate of one observe per 10-30 seconds, ordinary capture cadence does not explain continuous 10 Hz flicker during the reported idle interval. The cadence and idle condition are source-reported, not measured in this run.
- The earlier claim blaming too many screenshots was unsupported and was retracted. This static check is consistent with that correction but does not prove a live cause, exclude unobserved retries, or localize the flicker to the compositor/plugin. Runtime counters and a matched live reproduction are still required.
- H-A through H-G remain unranked hypotheses. The old after-paint behavior was a concrete code issue and has been changed, but no live before/after flicker measurement proves it was causal. The backdrop, duplicate-instance, client-request, crash, shader, and refresh-rate explanations are likewise unverified.
- The three incident reports are consistent with presentation-path failures but do not prove a shared cause. Runtime counters have been added; only a live before/after measurement can show whether the changes affect flicker. No live flicker was reproduced, so the reported rate remains unmeasured.


### 2.5 Todo list flaws (Worker 2)
- Phase 1: risky and stale. Sound intent, but no thresholds, baseline, isolation, owners, deadlines, or fallback.
- Phase 2: sound in content, flawed in ordering. Calibration (2.1.1) sits after Phase 1 instead of before it; 2.5.8 and 2.6.6 are placeholders, not items (I28-I30 and I32-I40 compressed into two lines).
- Phase 3: sound as a checklist, risky as a plan. No verification step for any item; 3.4.1 multi-agent deliberation conflicts with the single BiDi session limit.
- Phase 4: flawed. A dumping ground of six unrelated leftovers with no owner or date.
- Phase 5: flawed. No named task, baseline, pass criteria, held-out set, or independent checker, repeating the I8/G14 measurement error.
- H1 in the source error file is wrong (flicker was during Muse driving, Codex driving was normal, per I9) with no item to correct it; the G24 to G27 numbering gap is copied silently; the test sites (example.com, httpbin) violate the project's own held-out principle (G14).

## 3. Risks (none in the todo list, all found by the council)

### 3.1 BiDi risks (Worker 2)
- Restart is a precondition, not optional: no debug port can be added to a running Zen; the coordinator already killed and relaunched Zen at 02:57-02:58 to add the flags, yet the results file claims "neither needed any Zen restart", which is false as written. No rollback or re-verification-after-update item exists.
- One BiDi session at a time; a crashed client leaves a zombie session cleared only by restarting Zen. Five parallel workers testing against one browser is a race, and the results file already records tabs changing on their own between runs.
- navigator.webdriver=true under BiDi/Marionette can trigger Cloudflare/Akamai bot detection; untested on Polygon/Codeforces, and the list has no test item for it.
- zenpilot sets remote.prefs.recommended=false because the remote agent rewrites about 40 prefs into the profile permanently. No profile backup or pref-audit item.
- Zen diverges from Firefox in BiDi (the Playwright openWindow rejection proves it); BiDi is a W3C Working Draft with modules still missing. No version pinning or re-test-on-update item.
- No auth on the BiDi socket (W3C issue 1188). No security item.
- File upload, the exact 70-minute blocker (I27), is where DOM is weakest: zen-mcp docs say no upload, zenpilot upload is untested and allowlist-gated, and Mozilla bug 2083461 shows firefox-mcp upload reporting success while setting no file. The list asserts "fix by DOM click" for five items without one upload test.

### 3.2 Non-browser apps untouched by BiDi (Worker 3)
- File picker (70-minute stall), native dialogs, terminal, VS Code, Zen chrome. The native equivalent already half-exists: a11y.py AT-SPI extents plus native click actions, gated behind CU_PICK4_FASTPATH=1, with a screen-vs-window ambiguity still unresolved. Hyprland IPC gives window geometry only, never button positions.

## 4. Recommended corrections to the todo list and approach

### 4.1 Immediate corrections (Worker 2, 20 concrete corrections in its report)
- Add Phase 0: calibration-first experiment BEFORE Phase 1. Known-point grid test (5 min, decisive), error-vector analysis. Do not build on the screen-ratio story until the grid test confirms or refutes it.
- Pre-register pass criteria for Phase 1: baseline wall time, hit-rate threshold, speed threshold, per-tool verdict rule.
- Set a go/no-go date for Phase 1, with the WebExtension plus native messaging bridge as fallback (the only no-restart attach, already documented in the research file but absent from the list).
- Add session management: single BiDi session manager, zombie session cleanup, no parallel workers against one browser.
- Add bot-detection test: navigator.webdriver=true on Polygon/Codeforces under BiDi.
- Add upload test: file upload via each tool, since DOM is weakest here and it was the 70-minute blocker.
- Add profile backup and pref-audit before zenpilot runs (it rewrites about 40 prefs permanently).
- Add version pinning and re-test-on-update items (Firefox, Zen, BiDi spec all move fast).
- Add BiDi socket security item (no auth, W3C issue 1188).
- Correct H1 in the source error file (flicker was Muse driving, not Codex). Fix the G24 to G27 numbering gap.
- Rewrite Phase 5: named task, baseline, pass criteria, held-out set (G14), independent checker.
- Expand placeholders 2.5.8 (I28-I30) and 2.6.6 (I32-I40) into real items.
- Link the todo list to the live results file; stop re-testing what is already answered (Playwright dead, zen-mcp works, zenpilot works).

### 4.2 Coordinate fixes, cheapest first (Worker 3)
- Known-point grid calibration test (5 min, decisive).
- Crop-zoom on small targets (already supported via --crop).
- Grid/ruler overlay.
- Hover-first plus verify-after-click on destructive targets.
- Hit-rate logging (I8: no hit rate was ever measured).
- Experiments E1-E8 in worker3 report: pipeline unit audit, known-point grid with error-vector analysis, downscale sensitivity (960/1200/1920), DOM-rect vs vision head-to-head on the real Polygon page, scale-1.25 robustness, Browse hover test, native dialog accuracy, ongoing hit-rate instrumentation with before/after measurement for any BiDi rollout.

### 4.3 Overlay flicker experiments (Worker 4, E1-E8 in its report)
- E1 instrument the pill with timestamped logging, then A/B Muse vs Codex on the same page (decides storm vs repaint vs duplicate instance).
- E2 idle isolation: in a later live test, send no input or observations while measuring visible frames and indicator counters. Flicker without driver traffic would make capture activity insufficient as the sole explanation, not identify the render-layer cause.
- E3 unload hyprglass while the indicator runs.
- E4 check for duplicate indicator processes/layer surfaces during flicker.
- E5 measure the true rate and CPU.
- The conditional after-paint commit change and timestamped counters are already implemented. The remaining live work is to collect those counters during a measured flicker and separately assess presentation-feedback failure behavior.

### 4.4 New directions NOT in the todo list (Worker 5, 16 recommendations, top 5)
- R1 test Microsoft Hybrid Computer Use directly on Polygon (batched actions, diff-only observation, stale-layout guard).
- R2 test Vercel agent-desktop for desktop-side AT-SPI.
- R3 test linux-use and kde-desktop-mcp Hyprland AT-SPI reads.
- R4 test CUA driver Hyprland compositor-native v0.33.4.
- R5 batch actions plus diff-only observation to kill the 87.8% think-observe-think loop.
- Others: viewport-scoped snapshots, stale-layout guard, coarse-to-fine zoom, BiDi event subscription instead of screenshot polling, single BiDi session manager, Foxhand extension attach fallback, D2Snap, Hyprland socket instead of hyprctl spawns, grounding model only for canvas, bidi-lite Rust client, browser-control-mcp for JS debugging.

### 4.5 Research corrections (Worker 1)
- Fix the 2 wrong dates (Firefox 129 August 2024, Firefox 141 22 July 2025) and the zenpilot version (0.7.0, 18/11/2026) in the Firefox automation research file.
- Add Nightly dynamic BiDi start as a footnote and a live-test item.
- Add Selenium MCP server, FoxMCP, Foxhand, FF MCP Bridge, navigera, agent-browser as candidates to evaluate.

## 5. UNVERIFIED items (need live work, do not treat as fact)
- zen-devtools-mcp current status; mcp-browser-bridge/Claudezilla; Firefox 145 BiDi additions; Selenium 4.35 session reuse; Zen no-new-window claim; about: navigate refusal; BiDi-only navigator.webdriver; W3C issue 1188 current status; agent-browser PR 2227 number/date (feature confirmed merged, number not opened directly); all Zen-specific attach claims (no live Zen run in the redteam session).
- Whether Zen exposes web content over desktop AT-SPI; whether CUA Hyprland v0.33.4 works on the laptop; whether Foxhand works on Zen; whether Playwright added attach-to-running-Firefox; grounding latency on the RTX 4050; whether HCU X11 provider works under XWayland on Hyprland. No independent same-task DOM-vs-screenshot benchmark on Firefox/Zen was found, so Phase 1.2.2 must measure it locally.
- The VM Muse driver screenshot frame (the actual driver that missed) could not be audited; its code is not in the repo.
- The true overlay flicker rate ("about 10 per second") is the user's estimate, not a measurement. No live flicker was reproduced in the redteam session.

## 6. Council unanimous decision

The council agrees: DOM/BiDi is the right direction for browser control, but it is not a complete fix and not a 10x fix by itself. The work must proceed as: Phase 0 calibration-first experiment (5 min, decisive), then Phase 1 with pre-registered criteria and a go/no-go date, then hybrid control (DOM locate plus real mouse click, batched actions, diff-only observation), plus AT-SPI for desktop apps, plus the flicker experiments. The todo list must be corrected per section 4 before the next round of work. No further optimization is claimed until measured on a real task with hit rate logged.

## 7. Files
- ~/workspace/redteam-council-20261121/worker1-bidi-verification.md (316 lines)
- ~/workspace/redteam-council-20261121/worker2-todolist-redteam.md (302 lines)
- ~/workspace/redteam-council-20261121/worker3-coordinate-redteam.md (305 lines)
- ~/workspace/redteam-council-20261121/worker4-overlay-flicker-redteam.md (181 lines)
- ~/workspace/redteam-council-20261121/worker5-speed-crawl.md (416 lines)
- ~/workspace/redteam-council-20261121/VERDICT.md (this file)
