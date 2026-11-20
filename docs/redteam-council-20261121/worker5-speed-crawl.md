# Redteam Worker 5: Fast Browser Automation and Computer-Use Speed Crawl

- Worker: Redteam Worker 5
- Task: crawl latest real-time docs on fast browser automation and computer-use speed optimization
- Access date: 21/11/2026
- Start wall-clock: 2026-11-21 03:32:47 Asia/Ho_Chi_Minh
- Crawl phase end: 2026-11-21 03:33:36 Asia/Ho_Chi_Minh
- Report written: 2026-11-21 03:34 Asia/Ho_Chi_Minh (approx, same session)
- Elapsed for search and verification: under 2 minutes of wall time for the search calls themselves, plus report writing. Note: the searches returned results dated up to Nov 2026, including pages crawled 20/11/2026, so this is current as of the task date.
- Todo list checked: ~/workspace/zen-error-fix-todolist-20261121.md, Phase 1.1 already covers Puppeteer BiDi, firefox-mcp, Selenium plus geckodriver, zenpilot slash zen-mcp, and Playwright moz-firefox. Recommendations in section 9 are deliberately limited to things NOT in that list.
- Rule compliance: no em dashes or en dashes used in this file, only commas, periods, and short hyphens. Every claim cites a live URL plus access date. Unverified claims are marked UNVERIFIED.

## TL;DR verdict

1. For Zen specifically, DOM plus WebDriver BiDi is the best available control path right now. It is not close. Screenshot plus mouse is the fallback, not the primary.
2. The state of the art in late 2026 is NOT pure DOM and NOT pure screenshot. It is hybrid: programmatic plus semantic (accessibility tree) plus visual, with batched actions, diff-only observation, and a stale-layout guard before every input. Microsoft Hybrid Computer Use (HCU) is the clearest published version of this, with controlled head-to-head numbers against a screenshot-only driver.
3. AT-SPI on Linux is real, fast, and directly relevant to the desktop side, but it does NOT replace BiDi inside Zen. Firefox web content is best reached through BiDi or the browser accessibility tree, not through desktop AT-SPI alone. The fastest desktop tools in Nov 2026 (Vercel agent-desktop, linux-use, kde-desktop-mcp, CUA driver on Hyprland) all use AT-SPI, and all still keep screenshots as a verification fallback.
4. The single biggest speed lever for this team is not a faster click. It is fewer model turns: batch up to 64 actions per call, return only a diff after each batch, and stop re-screenshotting after every single action. That directly attacks the 87.8 percent think-observe-think loop cost in the todo list.
5. WebMCP is the fastest interface measured anywhere in 2026, but it is unusable for this team today: it is a Chrome origin trial, not a Firefox or Zen feature, and the trial was due to expire 17/11/2026. Watch it, do not build on it.

## 1. WebDriver BiDi: state as of 21/11/2026

### 1.1 Spec and Firefox status

- WebDriver BiDi is a W3C Working Draft, latest snapshot 1 June 2026, edited by James Graham (Mozilla), Alex Rudenko (Google), Maksim Sadym (Google). Source: https://github.com/kalebteccom/browxai/blob/HEAD/docs/rfcs/references/01-webdriver-bidi-standards.md, accessed 21/11/2026. Research date on that page is 2026-06-13.
- Firefox is all-in on BiDi. CDP was deprecated in Firefox 129 (Aug 2024) and completely removed in Firefox 141 (released 22 July 2025). The `--remote-debugging-port` flag now serves only a WebDriver BiDi WebSocket. Source: same browxai standards doc, accessed 21/11/2026.
- Firefox allows a remote agent on any profile with loopback-only plus allowlist gates, unlike Chrome 136 plus (May 2025) which blocks `--remote-debugging-port` on the default user profile. Source: same browxai standards doc, accessed 21/11/2026.
- Mozilla BiDi milestones, from https://wiki.mozilla.org/WebDriver/RemoteProtocol/WebDriver_BiDi, accessed 21/11/2026:
  - Milestone 17, completed 26 Sep 2025: emulation features, network response bodies.
  - Milestone 18, completed 4 Jan 2026: touch, device screen dimensions, locale emulation, network request body collection.
  - Milestone 19, completed 29 Mar 2026: CSP bypass, user context configuration on window.open, widget-level touch, foundational for controlling Firefox via MCP servers.
  - Milestone 20, completed 28 Jun 2026: screen recording start and stop commands, CSP disable, element scrolling, download tracking.
  - Milestone 21, completed 27 Sep 2026: streaming support (screencasting, network responses), WebSocket events, worker support, element scrolling action, console logging and download events.
  - Milestone 22, in development at last crawl: streaming, WebSocket events, worker support, widget-level touch.
- Capability gaps still open in June 2026, from the browxai standards doc: WebAuthn virtual authenticators, accessibility tree, coverage and profiling, screencast (in flight, Firefox M20 targets screen-recording commands), virtual time and clock, deep device emulation. BiDi is better than CDP at cross-browser preload scripts plus sandboxes plus channels, spec-defined input, user contexts, standardized auth and request interception phases, and a multi-connection session model.
- Implication for Zen: the accessibility tree is NOT yet a BiDi module. If the team wants the in-page accessibility tree, it must get it via script evaluation (for example `script.evaluate` returning an ARIA snapshot) or via the browser accessibility tree through AT-SPI, not via a native BiDi accessibility command. This gap matters and is not in the todo list.

### 1.2 Puppeteer plus BiDi

- Puppeteer documents WebDriver BiDi as the protocol for Firefox launch, while CDP remains the default for Chrome connections. Puppeteer 25.12.0 reference, checked 3 Oct 2026. Source: http://umatechnology.org/puppeteer-connect-options-explained-attach-to-an-existing-browser/, accessed 21/11/2026.
- `puppeteer.connect()` attaches to an already running browser via `browserWSEndpoint` or `browserURL`. For Firefox BiDi the endpoint form is `ws://127.0.0.1:9222/session` with protocol `webDriverBiDi`. A Mozilla bug report proves this works: Marionette session plus a second harness communicating via BiDi, `puppeteer.connect({browserWSEndpoint: 'ws://127.0.0.1:9222/session', protocol: 'webDriverBiDi'})`. Source: https://bugzilla.mozilla.org/show_bug.cgi?id=1943416, accessed 21/11/2026, status RESOLVED FIXED.
- Firefox allows a single BiDi session. A second session fails. Source: https://crates.io/crates/bidi-lite, accessed 21/11/2026. This is a hard constraint for the team: five tools cannot hold five simultaneous BiDi sessions on one Zen instance. See recommendation R10.

### 1.3 Playwright plus BiDi

- Playwright exposes `moz-firefox`, `moz-firefox-beta`, `moz-firefox-nightly` channels that drive stock Firefox over BiDi (experimental). Playwright MCP exposed them via `--browser moz-firefox` in microsoft/playwright pull request 41126, merged 2026-06-08, released in playwright-mcp v0.0.76. Source: https://github.com/kalebteccom/browxai/blob/HEAD/docs/rfcs/references/02-ecosystem-and-appium.md, accessed 21/11/2026, research date 2026-06-13.
- Playwright over BiDi targets unpatched, vanilla Firefox. Mozilla meta-bug 1917540, Support WebDriver BiDi in Playwright: 26 dependent bugs resolved, 11 open as of late May 2026. Playwright BiDi test pass rate cited as Firefox 1,469 out of 3,877 (38 percent) in that June 2026 doc, substantially improved since, but the tracking issue microsoft/playwright 32577 remains open as of June 2026. Source: same browxai ecosystem doc, accessed 21/11/2026.
- Verdict: Playwright BiDi is a real but not yet default path. The todo list item 1.1.5 (confirm Playwright moz-firefox cannot attach to a running Zen, launch-only) is consistent with this: BiDi launch works, attach to an existing profile is the hard part. UNVERIFIED as of this crawl whether Playwright 1.60 plus (May 2026) added attach; the team test in 1.1.5 is still the right experiment.

### 1.4 Selenium plus BiDi

- Selenium latest stable cited as 4.50.0 (30 Sep 2026). Selenium 4.29.0 fully removed CDP support for Firefox in Feb 2025. Source: https://cloudqa.io/selenium-4-0-released-whats-new/, accessed 21/11/2026, last updated Oct 2026.
- Selenium 4.40 and 4.41 added screen and network emulation via BiDi. Selenium 4.47 added Safari BiDi (Technology Preview). Selenium 4.50 and 4.51 and 4.52 added web extension install via BiDi. Source: https://seleniumdecoded.com/learn/modern-selenium/whats-new-in-selenium-4/, accessed 21/11/2026.
- Selenium exposes BiDi at two levels: high-level APIs (`driver.script()`, `driver.network()`) and low-level modules mirroring the spec (`browsingContext`, `network`, `script`, `log`, `input`, `storage`, `emulation`, `webExtension`, `speculation`). Since 4.46 the low-level layer is generated from one shared schema. Source: https://seleniumdecoded.com/learn/modern-selenium/webdriver-bidi/, accessed 21/11/2026.
- Firefox BiDi status in Selenium 4.52: yes, stable, Firefox only bidirectional protocol since CDP removal. Source: same Selenium Decoded BiDi page, accessed 21/11/2026.

### 1.5 Lightweight BiDi clients (not in todo list)

- `bidi-lite`, a Rust crate: lightweight async low-overhead WebDriver BiDi client focused on Firefox, plus a minimal Firefox Remote Debugging Protocol (RDP) client for JS debugging. Validated against Firefox 157.0.1. Start Firefox with `firefox --no-remote --profile "$HOME/bidi-lite-profile" --remote-debugging-port=9222`. Source: https://crates.io/crates/bidi-lite, accessed 21/11/2026.
- Why it matters: if Puppeteer or Selenium overhead ever shows up in timing, a raw WebSocket BiDi client in Rust or Node removes a whole layer. Test only if the Phase 1.1 timings show client overhead, not browser overhead.

## 2. Firefox automation best practices, 2025-2026

- Mozilla official MCP server is now named `@mozilla/firefox-devtools-mcp`, repo https://github.com/mozilla/firefox-devtools-mcp, accessed 21/11/2026. It controls Firefox through WebDriver BiDi via Selenium WebDriver. Version 0.10.7 was checked in an isolated container on 16 Nov 2026 per https://hostedmcp.org/servers/mozilla/firefox-devtools-mcp, accessed 21/11/2026.
- Connect-existing mode requires BOTH flags, because the MCP uses both WebDriver Classic (Marionette) and BiDi: `firefox --marionette --remote-debugging-port`, then `npx @mozilla/firefox-devtools-mcp --connect-existing --marionette-port 2828`. If Firefox is started with only `--marionette`, the MCP fails to connect. Source: https://github.com/mozilla/firefox-devtools-mcp, accessed 21/11/2026.
- Security warning from the same repo: do not leave Marionette enabled during normal browsing. It sets `navigator.webdriver = true` and changes other browser fingerprint signals. The Zen fork doc repeats this warning. Source: https://github.com/mozilla/firefox-devtools-mcp and https://glama.ai/mcp/servers/simon-ami/zen-devtools-mcp, both accessed 21/11/2026.
- Zen-specific forks found in this crawl (not all in the todo list):
  - `zenpilot`, PyPI 0.2.0, 16 Oct 2026: MCP server driving a running Zen over BiDi, no extension, no HTTP server. Tested on macOS with Zen 1.23.2b (Firefox 157). One session at a time, releases BiDi session after 2 minutes idle. Refs point to BiDi `sharedId` node references, not CSS selectors. Source: https://pypi.org/project/zenpilot/0.2.0/, accessed 21/11/2026.
  - `claude-for-zen` (ilhamnadhif): MCP server, Zen over BiDi at `ws://127.0.0.1:9333`, Node 20 plus, macOS, Linux, Windows. Source: http://glama.ai/mcp/servers/ilhamnadhif/claude-for-zen, accessed 21/11/2026.
  - `zen-devtools-mcp` (simon-ami): Zen-first fork of Mozilla firefox-devtools-mcp, via Selenium WebDriver. `--connect-existing` plus `--marionette-port 2828`. Notes BiDi-dependent features (console events, network events) are NOT available in connect-existing mode. Source: https://glama.ai/mcp/servers/simon-ami/zen-devtools-mcp, accessed 21/11/2026.
  - `zen-mcp` (sh6drack): first MCP server for Zen, 20 tools, direct WebSocket BiDi, no Selenium, no Playwright, no driver. Known limits: no file upload or drag-and-drop (BiDi spec limitation), zombie sessions only cleared by restarting Zen. Last commit 2026-05-16, version 1.2.1, 27 stars. Source: https://glama.ai/mcp/servers/sh6drack/zen-mcp/tree and https://mcpdirectory.fyi/us/global/online/zen-mcp, accessed 21/11/2026.
- Foxhand (formerly WebMCP Controller): Firefox add-on plus native messaging host, drives the real Firefox profile, tabs, bookmarks, history, logged-in sessions. Localhost only, 256-bit bearer token, port 8901. No Marionette, no remote debugging port. Source: https://mcpservers.org/servers/hamb1y/foxhand, accessed 21/11/2026. This is a genuinely different attach path from BiDi and is NOT in the todo list. See R11.

## 3. AT-SPI and accessibility tree control on Linux Wayland

### 3.1 Direct answer to task question (a)

Yes, AT-SPI is faster than screenshots for reading and acting on UI structure, by orders of magnitude on the read path, and it removes coordinate guessing entirely. But it is not a drop-in replacement for screenshots: it cannot see canvas, it cannot see pixels-only state, and on Wayland synthetic input is the weak point in several tools. The winning pattern in every Nov 2026 tool is AT-SPI first, screenshot only to verify.

### 3.2 Evidence

- linux-use, by Javi Mosch, open-source CLI, MIT. Agent-first GUI control via AT-SPI, no screenshots, no mouse movement. Author benchmark: 28 interactive elements walked in 48 milliseconds, output as structured JSON with role, name, center coordinates, and action. Actions invoke the widget accessible action directly, no window focus, no mouse move, works even while the target window is occluded. `watch` streams AT-SPI events as newline-delimited JSON instead of polling. Caveats, from the project coverage: full automation only on X11 today, Wayland accessibility paths work but synthetic input does not, tested manually on one setup (Ubuntu 22.04.3, GNOME 42.9, X11, x86-64), six GTK 3 and 4 apps plus some Qt 5 menus, Electron, Flutter, Java untested, no automated test suite, v0.7.1. Chromium and Edge need `--force-renderer-accessibility`. Sources: https://www.techbytes.app/posts/linux-use-agent-first-gui-control-for-linux/ and https://ainews.leverageai.com.au/case/linux-use-accessibility-agent-control, both accessed 21/11/2026.
- Vercel agent-desktop, 1.0.0 on 27 Oct 2026 with Linux support, 1.0.2 on 30 Oct 2026, announced 31 Oct 2026. Rust CLI plus C library, Apache-2.0, 25,734 stars and 1,928 forks as read 20/11/2026 on GitHub (verified by direct page open in this crawl). Reads AX on macOS, UI Automation on Windows, AT-SPI on Linux. Returns JSON snapshot with stable refs such as `@s8f3k2p9:e8`, agent clicks or types by ref, no screenshots, no pixel matching. Headless by default: ref actions use the accessibility API without moving the pointer or taking focus. Global `--headed` flag allows physical input. Skeleton snapshot: Slack skeleton about 3.6 KB versus about 17.3 KB for the full tree, a 78 to 96 percent token saving on dense Electron apps (per dev.to summary of repo measurements). Linux needs a graphical session with `at-spi2-core`, mouse input needs X11 and `--headed`, Wayland clipboard needs `wl-clipboard`. 61 command names, 57 operational. MCP via `agent-desktop mcp`. Sources: https://github.com/vercel-labs/agent-desktop (opened directly 21/11/2026), https://dev.to/piekwerk/vercel-agent-desktop-computer-use-for-coding-agents-through-the-accessibility-tree-5fap, https://www.aighten.com/en/blog/vercel-agent-desktop-computer-use-accessibility-tree, all accessed 21/11/2026.
- kde-desktop-mcp (ahmetadakli): screenshot-free desktop control MCP for KDE Plasma Wayland, Hyprland, and Windows. Reads through AT-SPI over D-Bus, acts via AT-SPI actions and EditableText. Talks to AT-SPI over D-Bus directly, without libatspi, pipelines requests: all attributes of an element and every level of the tree are requested at once, so time is bound by app response speed rather than round-trip latency. On Hyprland the active window is matched to its AT-SPI app by pid. Hyprland commands go over the Hyprland socket instead of `hyprctl` processes. Screenshot fallback via grim. Source: https://glama.ai/mcp/servers/ahmetadakli/kde-desktop-mcp, accessed 21/11/2026.
- kwin-mcp, PyPI 0.3.0: MCP server for KDE Plasma 6 Wayland. No screenshots required for interaction, AT-SPI2 tree gives roles, names, coordinates, states, available actions. Isolated KWin virtual sessions. Note: KDE only, not Hyprland. Source: https://pypi.org/project/kwin-mcp/0.3.0/, accessed 21/11/2026.
- CUA driver (trycua, cua.ai), Linux backend published 18 June 2026, release 0.5.7. Uses AT-SPI 2 over D-Bus for the accessibility tree, XTEST for input synthesis, painted agent cursor separate from the physical pointer. Supported backend X11 and XWayland, native Wayland still in preview behind an opt-in flag. Tested on Debian 12, Ubuntu 22.04 and 24.04, Rocky 9, Fedora 41. Source: https://cua.ai/blog/inside-linux-computer-use, accessed 21/11/2026.
- CUA driver on Hyprland: 25 Sep 2026 product note, compositor-native background computer use on Hyprland (Omarchy). As of 2026-10-05 the latest cua-driver-rs release is v0.33.4, adding multi-monitor Hyprland support. Source: https://www.rl-list.com/vendors/cua, accessed 21/11/2026. This is directly relevant because the user runs Omarchy plus Hyprland. UNVERIFIED by this worker whether v0.33.4 works on the user laptop; it is a test candidate, not a proven fact.
- CUA driver performance note, from the Hermes docs that embed cua-driver: background mode accessibility-routed events take about 5 to 20 ms on macOS, about 3 to 10 ms on Windows UIA, about 5 to 15 ms on Linux AT-SPI, versus direct HID posting. Source: https://docs.gormes.ai/upstream-hermes/user-guide/features/tools/computer-use/, accessed 21/11/2026. These are doc claims, not an independent benchmark.
- Microsoft Hybrid Computer Use, platform support table (verified by direct GitHub open 21/11/2026): Linux X11 provider is Python embedded in the binary, AT-SPI2, X11, XTest, evaluated on OSWorld 1.0 and 2.0 and WeaveBench. macOS Swift AXUIElement, Windows C# UI Automation. Source: https://github.com/microsoft/Hybrid-Computer-Use, accessed 21/11/2026.

### 3.3 Wayland caveats that matter for this team

- Native Wayland synthetic input is the recurring weak point. linux-use: Wayland synthetic input broken. agent-desktop Linux: mouse input needs X11 and `--headed`. CUA Linux: native Wayland in preview, X11 and XWayland supported.
- The Hyprland-native workarounds that avoid ydotool and uinput are: `zwlr_virtual_pointer_v1` for pointer, `zwp_virtual_keyboard_v1` via wtype for typing, Hyprland socket for window management. hypruse documents exactly this stack. Source: https://pypi.org/project/hypruse/0.6.0/, accessed 21/11/2026.
- Firefox and Zen on Wayland: the browser itself exposes its internal accessibility tree to AT-SPI when accessibility is enabled, but the reliable programmatic path for web content remains BiDi plus script evaluation, not desktop AT-SPI. Do not assume desktop AT-SPI gives clean web element refs inside Zen without testing. UNVERIFIED: whether Zen exposes its web content tree over AT-SPI with the same fidelity as Firefox. Test it before designing around it.

## 4. GUI agent speed and accuracy research, 2025-2026

### 4.1 The hybrid result: Microsoft Hybrid Computer Use

- Paper: Hybrid Computer Use: A Unified Programmatic, Semantic, and Visual Interface for General Agents, arXiv 2610.41432, repo created 2026-10-08, MIT. Verified by direct GitHub open 21/11/2026 at https://github.com/microsoft/Hybrid-Computer-Use.
- Design: one MCP server, two tools `AX` and `GUI`, plus the agent own shell and file tools. `AX` reads a compact accessibility tree with short refs (`a1`, `w1`, `r12`), runs up to 64 actions in one call with waits, returns a diff. `GUI` takes screenshots, zooms into dense regions, sends batched pointer and keyboard input. Before sending any input, HCU checks the live target of every `AX` action and the live window layout of every `GUI` coordinate. An action planned on a desktop that has since changed is rejected, not sent.
- Controlled results, same model, same harness, same step budget, baseline CUA Driver:
  - OSWorld 2.0 (108 tasks), Linux, GPT-6 Astra: HCU 72.37 percent partial vs CUA Driver 68.82 percent, cost about the same.
  - OSWorld 1.0 (360 tasks), Linux, GPT-5.4: HCU 70.13 percent vs 62.47 percent, cost minus 59.1 percent.
  - Windows Agent Arena (111 tasks), Windows, GPT-5.4: HCU 80.86 percent vs 71.89 percent, cost minus 50.6 percent.
  - MacAgentBench UI subset (28 tasks), macOS, GPT-5.4: HCU 25 out of 28 vs 24 out of 28, cost minus 51.4 percent.
  - WeaveBench (114 tasks), Linux, GPT-5.4: HCU 53.25 percent vs 46.37 percent, cost minus 46.3 percent.
  - OSWorld 2.0 with Claude Opus 5: HCU 35.19 percent binary, highest of all full-set systems, at 20.3 percent lower cost than the official GUI loop.
  - Across four frontier models on OSWorld 1.0: HCU raises mean score by 6.48 points with 17 percent fewer steps and 30 percent lower cost.
- Timed example in the README: same LibreOffice Calc task, pure GUI 6 model turns and about 41 seconds, CUA Driver 11 turns and about 74 seconds, HCU 4 turns (three AX calls and one GUI zoom) and about 27 seconds.
- Why this matters most for this team: it is the only source found in this crawl with a controlled, same-harness comparison showing both higher success and lower cost from batching plus diffs plus a stale-layout guard. Those three mechanisms map exactly onto the todo list failures: G13 think-observe-think loop, H3 and I1 View vs Remove misclicks, I2 Discard vs Continue, I3 mouse sitting still on Add to Contest.

### 4.2 Grounding models and benchmarks

- GTA1, GUI Test-time Scaling Agent, Salesforce AI Research, 2025-07-09, arXiv 2507.05791. Test-time scaling (sample multiple action proposals, judge picks best) plus RL grounding model. GTA1-7B: 50.1 percent ScreenSpot-Pro, 92.4 percent ScreenSpot-V2, 67.7 percent OSWorld-G. With planner plus test-time scaling: 45.2 percent task success on OSWorld. Source: https://arxiv.org/html/2507.05791v1, accessed 21/11/2026.
- Jedi and OSWorld-G, Scaling Computer-Use Grounding via User Interface Decomposition and Synthesis, NeurIPS 2025 Datasets and Benchmarks spotlight, accepted 2025-11-25. OSWorld-G has 564 samples. Jedi dataset has 4 million examples. Jedi-7B: 91.7 percent ScreenSpot-v2, 39.5 percent ScreenSpot-Pro, 54.1 percent OSWorld-G. Improved grounding lifts OSWorld agentic performance from 23 percent to 51 percent. Source: https://osworld-grounding.github.io, accessed 21/11/2026.
- D2Snap, Beyond Pixels: Exploring DOM Downsampling for LLM-Based Web Agents, arXiv 2508.04412. Raw DOM snapshots exceed 128k context in 42 percent of cases; D2Snap-downsampled DOM snapshots all fit at mean 16.5 percent context utilisation. GPT-4o agent on Online-Mind2Web: D2Snap 73 percent success vs 67 percent grounded GUI snapshot baseline (plus 5.8 points, 95 percent CI minus 13.6 to plus 26.0, McNemar p equals 0.47, so not statistically significant, but no deficit beyond 11 points one-sided). Grounding text alone 62 percent. Source: https://arxiv.org/pdf/2508.04412v3, accessed 21/11/2026.
- ScreenSpot-Pro grounding accuracy, compiled from multiple sources accessed 21/11/2026:
  - GPT-4o alone: 0.8 to 0.9 percent.
  - OS-Atlas-7B: 18.9 percent at paper publication.
  - OmniParser V2 plus GPT-4o: 39.5 to 39.6 percent.
  - UI-TARS-72B: 38.1 percent. UI-TARS-1.5-7B: 61.6 percent per ByteDance blog, about 42 to 49 percent in third-party reproductions (regime difference, see caveats).
  - Jedi-7B: 39.5 percent. GTA1-7B: 50.1 percent.
  - GUI-Owl-1.5: 72.9 percent single-shot, 80.3 percent two-stage crop, self-reported, arXiv 2602.16855, verify before adopting.
  - Zoom-refine with no training: takes OS-Atlas-7B from 18.9 percent to 48.1 percent with ScreenSeekeR agentic framework.
  - Sources: https://github.com/tomsalphaclawbot/openclaw-vnc-control/blob/HEAD/docs/CLICK_ACCURACY_RESEARCH.md, https://ruoqijin.com/blog/mac-auto-bridge-cloud-ocr, https://github.com/temm1e-labs/temm1e/blob/HEAD/tems_lab/gaze/RESEARCH_PAPER.md, all accessed 21/11/2026. Treat vendor and self-reported numbers as self-reported, not independently replicated.
- OmniParser V2 latency: 0.6 seconds per frame on A100, 0.8 seconds per frame on RTX 4090, per Microsoft model card summary. Source: https://ruoqijin.com/blog/mac-auto-bridge-cloud-ocr, accessed 21/11/2026. License warning from same source: `icon_detect` inherits YOLOv8 AGPL-3.0, closed-source commercial use restricted, `icon_caption` is MIT.
- Why your AI Agent keeps misclicking, Tongyi-MAI MobileWorld blog, accessed 21/11/2026: Set-of-Mark paradigm yields remarkably poor results across frontier models on refined OSWorld-G, every model fails to reach even a 30-point threshold in that setting, using OmniParser V2 SoM. The gap between reported grounding numbers and deployment hides in coordinate system, image resize, and zoom-in tool. Source: https://github.com/tongyi-mai/mobileworld/blob/HEAD/site/blog_posts/Why%20your%20AI%20Agent%20keeps%20misclicking.md, accessed 21/11/2026. Lesson: do not trust a single grounding number without its exact resize, crop, and coordinate recipe.

### 4.3 OSWorld state of the art

- OSWorld-Verified (369 short tasks, cleaned): top published result 90.19 percent (Intelligence Indeed agent, 25 July 2026, 100 steps), above the 72.36 percent human baseline measured by the benchmark authors. Best general model alone: claude-fable-5 at 85.96 percent. Source: http://benchmarkingagents.com/osworld/, accessed 21/11/2026, read 18 Nov 2026 on that page.
- OSWorld 2.0 (108 long workflows, released 26 Jun 2026, median 1.6 hours per task for a skilled person): best full-task completion 44.44 percent as of 15 Oct 2026, Salesforce Darwinx agent running Claude Opus 4.8, and 44.3 percent binary for Claude Opus 5 max with batch tool, 17 Sep 2026, partial 77.67 percent. Sources: https://fintekcafe.com/computer-use-agents-design-guide/ and https://www.canagentswork.com/benchmarks/osworld-2/, both accessed 21/11/2026.
- Caveat from Epoch AI review, cited in the Fintekcafe guide: about 15 percent of OSWorld tasks can be completed using only a terminal, about 30 percent let an agent substitute terminal commands and Python scripting for much of the graphical work, about 10 percent had serious errors. Short tasks flatter agents. Long workflows are where the gap opens.
- Implication: short-task benchmarks do not prove the Polygon upload workflow is solved. The team should benchmark on its own long tasks (Polygon upload end to end), not on OSWorld alone.

## 5. New MCP servers for browser control, 2025-2026

- Playwright MCP Server: 39,301 stars, 7,526,421 npm downloads in a typical week, 25 tools, accessibility-snapshot approach, commit 2 days before the Glama comparison. Source: https://glama.ai/mcp/best/browser-automation, accessed 21/11/2026.
- Chrome DevTools MCP, official Google: 37,700 stars, 34 tools, WebMCP debugging support in Chrome 149 plus. Source: https://chatforest.com/reviews/browser-extension-mcp-servers/, accessed 21/11/2026.
- firefox-devtools-mcp, official Mozilla: 131 stars at time of that review, now at version 0.10.7. Source: same Chatforest review and https://hostedmcp.org/servers/mozilla/firefox-devtools-mcp, accessed 21/11/2026.
- browser-control-mcp, crates.io 0.15.0-beta.25, BETA: controls and debugs real browsers, breakpoints, pause on load, call frames, evaluation in a paused frame, stepping, script search, on Chrome (CDP) and Firefox (BiDi plus Firefox RDP), plus navigation, DOM, input, screenshots, console and network capture. Successor of chrome-debug-mcp. Validated Firefox 159.0 (Linux, snap) and Chrome 156.0.8078.47. Measured 2026-11-08 against Playwright MCP 0.0.84 and chrome-devtools-mcp 1.12.0. Source: https://crates.io/crates/browser-control-mcp/0.15.0-beta.25, accessed 21/11/2026.
- Browser Harness (browser-use.com), matched eval 14 Oct 2026, 100 public tasks from BU Bench V2.1: median input tokens 2.1M vs Playwright MCP 4.4M vs Chrome DevTools MCP 6.7M vs agent-browser 3.3M. Median tool calls: Browser Harness 42, Playwright MCP 57, Chrome DevTools MCP 67.5, agent-browser 45. Median agent cost: 0.042 dollars vs 0.066 vs 0.097 vs 0.056 dollars. Nobody won on score: paired differences within plus or minus 6.6 points. Runs in the Chrome you already have open, logged in. Source: https://browser-use.com/posts/best-mcp-servers-to-control-a-browser, accessed 21/11/2026. Caveat: vendor-published by Browser Use, which makes Browser Harness. Treat token and cost numbers as vendor-measured, not independent.
- agent-browser (Vercel Labs), v0.42.0 from 10 Nov 2026: Rust CLI, CDP, `--auto-connect` attaches to running Chrome, `--profile Default` reuses Chrome login state, encrypted auth vault, snapshot with `@eN` refs. Source: https://explainx.ai/skills/vercel-labs/agent-browser/agent-browser and https://www.alterhunt.com/tools/agent-browser, accessed 21/11/2026. Chrome only, not Firefox, so it is a pattern reference for Zen, not a direct Zen tool.
- SeleniumBase MCP: 24 tools, persistent Pure CDP Mode browser, attempts CAPTCHA solving, for anti-bot scraping. Source: https://glama.ai/mcp/best/browser-automation, accessed 21/11/2026.
- Blueprint MCP: controls real browser (Chrome, Firefox, Opera) through a browser extension, npm `@railsblueprint/blueprint-mcp`. Source: https://www.awesome-mcp.com/servers/blueprint-mcp, accessed 21/11/2026.
- Foxhand: see section 2. Firefox add-on plus native messaging host, localhost 8901, bearer token.
- hypruse and hyprland-mcp and kde-desktop-mcp: see sections 3 and 6.

## 6. Hyprland IPC capabilities

- Hyprland exposes a complete IPC surface: `hyprctl -j` for state (monitors, workspaces, clients, active window), `hyprctl dispatch` for focus, move, close, resize, fullscreen, floating, `hyprctl keyword` and `getoption` for runtime config, `hyprctl --batch` to bundle several commands into a single request (avoids visible stutter from many rapid calls), `hyprctl eval` and `hyprctl repl` for Lua API (`hl.dispatch`, `hl.config`). Source: https://linuxcommandlibrary.com/man/hyprctl, accessed 21/11/2026.
- Note for this team: the todo list already records that string-dispatcher `hyprctl dispatch <string>` is broken on Hyprland 0.57.2 Lua config and the working form is `hl.dsp` object form. The man page summary above is generic; the Lua breakage is a local 0.57.2 fact from the team history, not contradicted by the man page.
- hypruse, PyPI 0.6.0: Computer use for Hyprland, MCP server, native hands on Wayland desktop. `desktop` returns the real window and workspace tree (addresses, classes, titles, geometry) in one call. Screenshots of a monitor, an exact window crop, or a zoomed region, with geometry and scale metadata to map any pixel back to a clickable coordinate. Native input: clicks and scrolls over Wayland wire (`zwlr_virtual_pointer_v1`), typing via wtype virtual keyboard with proper XKB keymap, unicode-safe. No ydotool, no uinput, no portals. Cursor positioning via `hyprctl dispatch movecursor` (global logical coordinates), sidestepping multi-monitor bugs of absolute virtual-pointer motion (Hyprland issue 6749). Source: https://pypi.org/project/hypruse/0.6.0/, accessed 21/11/2026.
- hyprland-mcp (keanehatescoding): MCP server over `hyprctl` and `hyprctl -j`, shells out to grim and slurp and notify-send. Tools: list, focus, close, kill, move, resize, floating, fullscreen, pin, workspaces, monitors, config, screenshots, launcher, tags, groups, cursor, hyprpaper, hypridle, hyprlock, plus escape hatches `hyprland_dispatch` and `hyprctl_raw`. Must run inside the Hyprland session or with `HYPRLAND_INSTANCE_SIGNATURE` forwarded. Source: https://glama.ai/mcp/servers/keanehatescoding/hyprland-mcp, accessed 21/11/2026.
- kde-desktop-mcp on Hyprland: Hyprland commands go over the Hyprland socket instead of `hyprctl` processes, which is faster than spawning a process per command. Source: https://glama.ai/mcp/servers/ahmetadakli/kde-desktop-mcp, accessed 21/11/2026. This is a concrete optimisation the team repo can copy: talk to the Hyprland socket directly instead of shelling to `hyprctl` per action.

## 7. DOM vs screenshot: benchmark numbers

No single independent benchmark settles DOM vs screenshot once and for all. The numbers below come from different methods, different tasks, and some vendor sources. Read the caveats with the numbers.

### 7.1 Head-to-head: WebMCP vs DOM vs screenshot (WindTunnel)

- WindTunnel, preprint 4 Aug 2026, nekuda, https://webmcp.com/windtunnel-paper.pdf, accessed 21/11/2026. 49 tasks across 8 self-hosted open-source web apps, 7 agent implementations, 3 attempts per task, 1,029 agent runs, about 103 dollars cost. Outcome scored by app state, not by a judge.
- Headline from the paper abstract: WebMCP agents solved 96 to 98 percent of tasks, compared to 80 to 90 percent for screenshot and structure-based agents, while costing 3 to 8 times less, processing 3 to 9 times fewer tokens, and finishing 3 to 5 times faster. Longest journeys cost gap about 12 times.
- WindTunnel v1.4 leaderboard detail, from the claims-and-maturity review accessed 21/11/2026: Native Sonnet 5 on WebMCP at 0.009 dollars per task median against 0.210 dollars for DOM plus vision. 6.8 seconds median agent time against 29.3 seconds. 5,172 median tokens against 64,424 tokens. Eight configurations tied at 48 out of 49 tasks solved.
- Same-model comparison in v1.4, from https://ipv6.velacore.au/what-is-webmcp/, accessed 21/11/2026: Sonnet 5.5, WebMCP 4.2 seconds median, 0.00353 dollars, 147 of 147 successful attempts, vs computer use 19.7 seconds, 0.031641 dollars, 140 of 147.
- Caveats, mandatory: publisher nekuda sells agentic-commerce infrastructure and benefits commercially if WebMCP adoption rises. Not peer reviewed, not independently replicated. Self-hosted benchmark sites, not production traffic. WebMCP agent can only do what the site tools expose; on one checkout task a gap in tool coverage let the slower screenshot agents win. Source for caveats: https://github.com/agricidaniel/web-mcp/blob/HEAD/skills/webmcp/references/claims-and-maturity.md, accessed 21/11/2026, facts verified against primary sources 2026-09-05.
- WebMCP availability: Draft Community Group Report at W3C Web Machine Learning Community Group, dated 2026-09-04, not a W3C Standard, not on the Standards Track. Not enabled by default in any browser. Chrome origin trial versions 149 to 156, Edge separate trial expiring 2026-11-17, Microsoft stating the feature may never be enabled beyond the trial. Google shipping target Chrome 157. WebKit formally opposes, Mozilla neutral. Sources: same claims-and-maturity doc and https://dplouffe.ca/2026/10/10/webmcp-browser-agent-tools/, both accessed 21/11/2026.
- Bottom line: WebMCP is the fastest measured interface, but it is not available on Zen or Firefox, and the Chrome trial expired 17/11/2026. Do not build the Zen plan on it.

### 7.2 DOM vs screenshot token and latency math

- Karate Labs, DOM vs Screenshot AI Testing, https://karatelabs.io/blog/dom-vs-screenshot-ai-testing, accessed 21/11/2026. Vendor source (Karate sells a DOM-based agent), treat as vendor math, not independent:
  - One 1920x1080 screenshot: roughly 1,500 to 3,000 LLM input tokens. Structured DOM extract of the same page: typically 300 to 800 tokens. Claimed 5 times difference minimum per page view.
  - Screenshot-based: about 1.5 to 3 seconds per step. DOM-based: about 0.3 to 0.8 seconds per step. Over a 100-step test: screenshot 2 to 5 minutes, DOM 30 to 80 seconds.
  - Cost example: 100 tests, 20 page views each, 10 runs per day, 20,000 page views per day, Claude Sonnet: screenshot about 40M tokens per day, about 120 dollars per day, about 3,600 dollars per month. DOM about 10M tokens per day, about 30 dollars per day, about 900 dollars per month.
- Independent dev.to measurement, Pixels vs the Accessibility Tree, measured 17 Nov 2026, 1280x800 viewport, Playwright `aria_snapshot()`, https://dev.to/neeraj_sharma_757fbb49aa7/pixels-vs-the-accessibility-tree-i-measured-what-a-web-page-costs-an-ai-agent-67-lines-of-python-2hn8, accessed 21/11/2026:
  - Screenshot: 1,365 tokens (Anthropic estimate width times height divided by 750).
  - Full tree cost 2.8 to 14.5 times one screenshot. Hacker News full tree 9,905 tokens vs scrolling the whole page as screenshots 2,730 tokens. Stripe pricing full tree 19,737 tokens vs 40,950 tokens as 30 screenshots.
  - Viewport tree (only interactive elements visible now): beat a single screenshot on 5 of 6 pages. Python docs 229 tokens vs 1,365 screenshot, a 6 times saving. Hacker News viewport tree 1,516 tokens vs 1,365 screenshot, the one loss, because 167 links fit in one viewport.
  - Lesson: full tree is NOT automatically cheaper. Viewport-scoped tree is the best default for acting. This is a concrete design rule the team can adopt immediately.
- Second dev.to measurement, Accessibility tree vs screenshots, https://dev.to/siropkin/accessibility-tree-vs-screenshots-the-token-math-behind-my-browser-agent-3fk9, accessed 21/11/2026:
  - Same page: accessibility tree 2.4 KB text, 1000px JPEG 16 KB. Tree tokenised near 840 tokens, image about 950 tokens, near parity on a light page. Savings live elsewhere: text runs on any model tier, screenshot needs a vision tier. Refs survive re-renders, pixel coordinates do not. Scoped snap of one story row: 147 bytes, about 50 tokens. A screenshot is all or nothing, a tree is queryable.
  - LinkedIn feed: 2,911 DOM elements, 784 divs, tree had zero divs and 121 buttons, every one with an accessible name.
  - Canvas is invisible to the tree. Excalidraw, Figma, anything that draws: tree sees a rectangle. If the target is a canvas, pixels are required.
  - Some state only lives in pixels. Tree for structure, pixels for verification.
- Browser Harness matched eval, 14 Oct 2026, see section 5: Browser Harness 2.1M median input tokens and 42 tool calls per task vs Playwright MCP 4.4M and 57 calls vs Chrome DevTools MCP 6.7M and 67.5 calls. Source: https://browser-use.com/posts/best-mcp-servers-to-control-a-browser, accessed 21/11/2026. Vendor-measured, see caveat in section 5.
- D2Snap, see section 4.2: downsampled DOM 73 percent vs grounded screenshot 67 percent on Mind2Web with GPT-4o, all downsampled DOM fits in context vs 42 percent of raw DOM exceeding 128k. Source: https://arxiv.org/pdf/2508.04412v3, accessed 21/11/2026.
- HCU Calc timing, see section 4.1: HCU 4 turns and about 27 seconds vs pure GUI 6 turns and about 41 seconds vs CUA Driver 11 turns and about 74 seconds. Source: https://github.com/microsoft/Hybrid-Computer-Use, accessed 21/11/2026.

### 7.3 What the numbers do NOT prove

- No source found in this crawl gives a clean, independent, same-task, same-model, DOM-vs-screenshot wall-time benchmark on Firefox or Zen specifically. The Karate numbers are vendor math. The WindTunnel numbers are vendor-run and WebMCP-centric. The dev.to numbers are token counts on six pages, not task success. The HCU numbers are the strongest controlled comparison found, and they compare hybrid vs screenshot-only driver, not pure DOM vs pure screenshot.
- The team Phase 1.2.2 item (measure DOM vs screenshot on its own tasks) is therefore still necessary. Do not quote Karate 5 times or WindTunnel 5 times as if they were measured on Zen.

## 8. State of the art for fast and accurate GUI control, right now

Ranked by evidence in this crawl, for the team constraints (Zen on Hyprland, Omarchy, Linux, logged-in tabs, Polygon upload tasks):

1. Hybrid is the state of the art. Programmatic first (API, CLI, file, DOM), semantic second (accessibility tree with stable refs), visual third (screenshot only to verify or to handle canvas and pixels-only state). Batch actions, return diffs, guard against stale layout. Evidence: HCU, agent-desktop, agent-browser, CUA driver all converge on this shape in Oct and Nov 2026.
2. DOM plus BiDi is the best available for Zen web content. No other protocol reaches logged-in Zen tabs with the same fidelity. Evidence: BiDi milestones M19 to M21, Puppeteer connect proof, zenpilot, claude-for-zen, zen-devtools-mcp, all BiDi-based.
3. AT-SPI is the best available for desktop apps outside the browser, and the fastest read path measured (28 elements in 48 ms, linux-use; 5 to 15 ms per accessibility-routed event, CUA docs). It is not a Zen replacement.
4. Screenshot-only grounding has improved enormously (ScreenSpot-Pro from 18.9 percent OS-Atlas-7B at publication to 50 to 73 percent for newer models, OSWorld-Verified top 90.19 percent), but it is still the slowest and most brittle channel, and it is where the team misclicks live. Use it as verification, not as the primary actuator.
5. WebMCP would beat all of the above where a site exposes tools, but it does not exist on Zen or Firefox. It is a watch item, not a plan.

## 9. Concrete recommendations NOT already in the todo list

Priority order is by expected impact on the todo list failures, not by novelty. Each item names what to test, what success looks like, and what it fixes.

### R1. Test Microsoft Hybrid Computer Use as the reference architecture, do not just read it

- What: clone https://github.com/microsoft/Hybrid-Computer-Use, build the Linux binary, run it on the laptop against a real Polygon upload task and a LibreOffice Calc task, measure turns, wall time, cost, and misclicks vs the current screenshot loop.
- Why not in todo: todo covers five browser tools, not HCU. HCU is the only controlled hybrid benchmark found.
- Success: fewer model turns and a lower misclick rate on the same task, with the AX diff and stale-layout guard visibly preventing a wrong click.
- Fixes: G13 (87.8 percent loop), H3 and I1, I2, I3 misclicks.
- Risk: HCU Linux provider is X11, not native Wayland. Test whether it works under XWayland on Hyprland before committing.

### R2. Test Vercel agent-desktop for desktop-side control

- What: `npm install -g agent-desktop`, run `agent-desktop snapshot --app <app> -i --compact`, click by ref, test on a non-browser app first, then test whether it can see Zen window structure.
- Why not in todo: todo is browser-only. agent-desktop is the highest-traction AT-SPI tool of Nov 2026 (25,734 stars, 1.0.2 on 30 Oct 2026).
- Success: a desktop task completes with zero screenshots and zero coordinate guesses.
- Fixes: desktop-side clicks, window management, verification without screenshots.
- Risk: Linux mouse input needs X11 and `--headed`. Headless ref actions should work, headed mouse may not on native Wayland. Test both.

### R3. Test linux-use and kde-desktop-mcp for Hyprland AT-SPI reads

- What: run linux-use `apps` and tree walk on the laptop, measure milliseconds for a real app tree, test `act` on a button by ref, test `watch` event streaming vs polling. Separately test kde-desktop-mcp Hyprland backend, which pipelines AT-SPI over D-Bus and talks to the Hyprland socket directly.
- Why not in todo: todo has no AT-SPI tool test.
- Success: tree walk under 100 ms for a typical app, act succeeds without focus change or mouse move.
- Fixes: fast observation, no coordinate drift, event-driven waits instead of screenshot polling.
- Risk: linux-use Wayland synthetic input is broken per its own docs. Read path may work, act path may not on native Wayland. Report read and act separately, do not conflate them.

### R4. Test CUA driver Hyprland compositor-native build

- What: test cua-driver-rs v0.33.4 or later, multi-monitor Hyprland support, compositor-native synthetic cursor, background operation while the user keeps their own pointer.
- Why not in todo: todo does not mention CUA driver at all.
- Success: agent acts on a background window while the user pointer stays put, no focus steal, no overlay flicker from screenshot capture.
- Fixes: H1 and I9 to I12 overlay flicker hypothesis (pill redraw vs screenshot capture conflict), plus background operation.
- Risk: CUA Linux native Wayland was preview in June 2026. Hyprland support is dated Sep and Oct 2026. UNVERIFIED on this laptop. Test, do not assume.

### R5. Batch actions and return diffs only (copy the HCU contract)

- What: change the agent loop so one model call can send up to N actions (start with 8, test up to 64 like HCU) with in-call waits, and the observation after a batch is a compact diff (what changed, which refs are stale), not a full screenshot plus full tree.
- Why not in todo: todo 2.1.9 says one observation for many actions, but does not specify batching inside one call or diff-only returns. This is the mechanism that makes 2.1.9 real.
- Success: model turns per Polygon task drop by at least half, wall time drops measurably, with no rise in misclicks.
- Fixes: G13, G22 (3 to 6 operations taking 5 minutes), I16 (9 minutes for 6 model calls).

### R6. Use viewport-scoped accessibility snapshots, never full-tree dumps by default

- What: snapshot only interactive elements in the current viewport, with short refs, like Playwright `aria_snapshot()` scoped to viewport. Full tree only on explicit drill-down (`--root <ref>` in agent-desktop terms, or a scoped BiDi query).
- Why not in todo: todo says use DOM, not how to scope it.
- Evidence: viewport tree beat a screenshot on 5 of 6 pages (229 tokens vs 1,365 on Python docs), while full tree cost 2.8 to 14.5 times one screenshot. Source: dev.to measurement 17 Nov 2026, section 7.2.
- Success: observation tokens per step drop, model decisions get faster, no loss in element coverage for the visible task.
- Fixes: H2 and I13 slow decisions, token cost, context overflow on long pages.

### R7. Add a stale-layout guard before every input (copy HCU)

- What: before sending any click or type, re-check the live target ref and the live window layout. If the target moved, changed, or the layout shifted since planning, reject the action, return a fresh snapshot, and re-plan. Never send a click planned on a stale observation.
- Why not in todo: todo fixes individual misclicks (H3, I1, I2, I3) one by one, but has no general guard.
- Success: zero clicks land on the wrong button after a layout shift in held-out tests. The guard fires visibly in logs when it saves a misclick.
- Fixes: H3, I1, I2, I3, I4, I5, I7, and the whole misclick class at once.

### R8. Add coarse-to-fine zoom for small targets

- What: for any target smaller than a threshold, or any click that missed, re-capture a zoomed region around the estimated point (hypruse `zoom`, HCU `GUI zoom`), then click from the zoomed coordinates. Log the zoom step.
- Why not in todo: todo does not mention zoom-refine.
- Evidence: zoom-refine takes OS-Atlas-7B from 18.9 percent to 48.1 percent on ScreenSpot-Pro with no training. Source: Tem Gaze research paper, March 2026, https://github.com/temm1e-labs/temm1e/blob/HEAD/tems_lab/gaze/RESEARCH_PAPER.md, accessed 21/11/2026. Also HCU uses GUI zoom as its visual verification step.
- Success: hit rate on small buttons (Browse, Add to Contest, View vs Remove) rises measurably.
- Fixes: I1, I3, I7, B9 and I21 Browse hover trick (zoom may reveal the hover state).

### R9. Subscribe to BiDi events instead of polling with screenshots

- What: use BiDi `session.subscribe` for `browsingContext.load`, `browsingContext.domContentLoaded`, `log.entryAdded`, `network.responseCompleted`, and related events. Wait for the event, do not screenshot-poll for page readiness. Use the M21 element scrolling action instead of mouse wheel guessing.
- Why not in todo: todo tests BiDi commands, not event-driven waiting.
- Success: no more observation-expired errors (I41 to I43, C1, C2) from acting on a stale screenshot after navigation, and no wasted screenshot polls while a page loads.
- Fixes: C1, C2, I41 to I43, G2.8 observation expiry.

### R10. Build a single BiDi session manager; do not run five BiDi tools at once

- What: one process owns the single Firefox BiDi session, multiplexes tool calls, releases after idle (zenpilot uses 2 minutes idle). All other tools talk to that manager, not directly to Zen.
- Why not in todo: todo tests five tools in parallel (1.1.1 to 1.1.5) with no session plan.
- Evidence: Firefox allows a single BiDi session, second session fails. Source: https://crates.io/crates/bidi-lite, accessed 21/11/2026. zenpilot releases after 2 minutes idle so multiple Claude sessions can take turns. Source: https://pypi.org/project/zenpilot/0.2.0/, accessed 21/11/2026.
- Success: no session conflicts, no zombie sessions requiring a Zen restart (zen-mcp known limit).
- Fixes: G1 stale-code and session rot class, zen-mcp zombie session limit.

### R11. Test the Firefox extension plus native messaging attach path (Foxhand) as a BiDi fallback

- What: install Foxhand add-on plus helper, test driving the real Zen profile without Marionette and without `--remote-debugging-port`.
- Why not in todo: todo is BiDi, Selenium, Playwright, zenpilot only. No extension path.
- Advantage: no `navigator.webdriver = true` fingerprint change (Marionette warning, section 2), no BiDi single-session limit, works on the real profile with logins.
- Risk: extension runs inside the browser, different trust model. Test on a throwaway task first. UNVERIFIED whether Foxhand works on Zen specifically (it targets Firefox); test it.

### R12. Test D2Snap DOM downsampling on long Polygon pages

- What: implement or port D2Snap downsampling (preserve actionability, drop non-actionable DOM), test on long Polygon pages where raw DOM would blow context.
- Why not in todo: todo says use DOM, not how to fit long pages in context.
- Evidence: D2Snap 73 percent vs 67 percent grounded snapshot on Mind2Web, all downsampled DOM fits at 16.5 percent mean context vs 42 percent of raw DOM exceeding 128k. Source: https://arxiv.org/pdf/2508.04412v3, accessed 21/11/2026.
- Success: long pages stay actionable without screenshot fallback.
- Fixes: long-page tasks, context overflow, slow decisions on dense pages.

### R13. Talk to the Hyprland socket directly; stop spawning hyprctl per action

- What: replace per-action `hyprctl` process spawns with a persistent Hyprland socket connection, and use `hyprctl --batch` where a socket client is not yet ready.
- Why not in todo: todo uses hyprctl as-is.
- Evidence: kde-desktop-mcp sends Hyprland commands over the socket instead of `hyprctl` processes. hyprctl man page says issuing many calls in quick succession can cause visible stutter, use `--batch` to bundle several commands into a single request. Sources: https://glama.ai/mcp/servers/ahmetadakli/kde-desktop-mcp and https://linuxcommandlibrary.com/man/hyprctl, both accessed 21/11/2026.
- Success: window operations get faster and stop stuttering the desktop.
- Fixes: overlay flicker and stutter hypotheses, window focus and resize speed.

### R14. Keep a grounding model only as a fallback for canvas and non-DOM targets

- What: test OmniParser V2 plus a local model, or UI-TARS-1.5, or Jedi-7B, on the laptop RTX 4050, ONLY for targets DOM and AT-SPI cannot see (canvas, custom widgets, image buttons). Do not route normal clicks through it.
- Why not in todo: todo is DOM-first, with no defined fallback for non-DOM targets.
- Evidence: OmniParser V2 plus GPT-4o 39.6 percent ScreenSpot-Pro vs GPT-4o alone 0.8 percent, 0.6 seconds per frame on A100, 0.8 seconds on RTX 4090. Jedi-7B 39.5 percent ScreenSpot-Pro. UI-TARS-1.5-7B 61.6 percent per ByteDance blog, 42 to 49 percent third-party. Sources in section 4.2.
- Risk: local inference on RTX 4050 may be slower than the A100 and 4090 numbers. Measure on the laptop, do not assume. License: OmniParser `icon_detect` is AGPL-3.0, check before any redistribution.
- Success: canvas targets become clickable without slowing down normal DOM clicks.

### R15. Test bidi-lite (Rust) if Node client overhead shows up in Phase 1.1 timings

- What: if Puppeteer or Selenium timings show client-side overhead, test bidi-lite raw WebSocket BiDi client, validated on Firefox 157.0.1.
- Why not in todo: todo tests only Node and Python clients.
- Source: https://crates.io/crates/bidi-lite, accessed 21/11/2026.
- Success: same BiDi commands, lower client latency, no Node dependency in the hot path.

### R16. Test browser-control-mcp for debugging, not for driving

- What: test browser-control-mcp (BETA 0.15.0-beta.25, Firefox via BiDi plus RDP) for breakpoints, pause on load, call frames, and script search when a Polygon page misbehaves. Do not use it as the primary driver.
- Why not in todo: todo has no JS debugging tool.
- Source: https://crates.io/crates/browser-control-mcp/0.15.0-beta.25, accessed 21/11/2026.
- Success: a stuck page can be diagnosed (console, network, paused JS) without screenshots.

## 10. What NOT to do (traps found in this crawl)

- Do not build on WebMCP for Zen. It is Chrome-only, trial expired 17/11/2026, Mozilla neutral, WebKit opposes. Watch it, do not depend on it.
- Do not use full-tree dumps as the default observation. Full tree cost 2.8 to 14.5 times one screenshot in the 17 Nov 2026 measurement. Viewport-scoped is the default.
- Do not run five BiDi clients against one Zen at once. Firefox allows one BiDi session.
- Do not leave Marionette enabled during normal browsing. It sets `navigator.webdriver = true`.
- Do not quote vendor benchmark numbers as independent facts. WindTunnel (nekuda), Karate (DOM vendor), Browser Harness eval (Browser Use vendor) are all vendor-measured. HCU numbers are the strongest controlled comparison found, and even they are author-measured on their own harness.
- Do not assume AT-SPI act works on native Wayland just because AT-SPI read works. linux-use, agent-desktop, and CUA all flag Wayland input as limited or preview. Test read and act separately.
- Do not route normal clicks through a grounding model. OmniParser V2 is 0.6 to 0.8 seconds per frame, and its ScreenSpot-Pro accuracy is 39.6 percent, not 99 percent. DOM refs are exact; grounding is a fallback.

## 11. Gaps and UNVERIFIED claims

- UNVERIFIED: whether Zen exposes its web content accessibility tree over desktop AT-SPI with the same fidelity as Firefox. Needs a live test on the laptop.
- UNVERIFIED: whether CUA driver v0.33.4 Hyprland support works on the user laptop (Omarchy, Hyprland 0.57.2). Needs a live test.
- UNVERIFIED: whether Foxhand works on Zen specifically. It targets Firefox. Needs a live test.
- UNVERIFIED: whether Playwright 1.60 plus added attach-to-running-Firefox. The June 2026 docs say launch-only for moz-firefox channels. The todo 1.1.5 test is still the deciding experiment.
- UNVERIFIED: local grounding model latency on the laptop RTX 4050. A100 and RTX 4090 numbers do not transfer.
- UNVERIFIED: whether the HCU Linux X11 provider works under XWayland on Hyprland. Needs a live test.
- No independent, same-task, same-model DOM-vs-screenshot wall-time benchmark on Firefox or Zen was found in this crawl. Phase 1.2.2 must measure it locally.
- Search note: this crawl used public web search and direct page opens only. No live browser task was run (subagent cannot operate a live browser). Any claim that would need a live Zen session is marked UNVERIFIED above.

## 12. Sources (all accessed 21/11/2026)

- https://github.com/kalebteccom/browxai/blob/HEAD/docs/rfcs/references/01-webdriver-bidi-standards.md
- https://wiki.mozilla.org/WebDriver/RemoteProtocol/WebDriver_BiDi
- https://github.com/kalebteccom/browxai/blob/HEAD/docs/rfcs/references/02-ecosystem-and-appium.md
- https://crates.io/crates/bidi-lite
- https://bugzilla.mozilla.org/show_bug.cgi?id=1943416
- http://umatechnology.org/puppeteer-connect-options-explained-attach-to-an-existing-browser/
- https://cloudqa.io/selenium-4-0-released-whats-new/
- https://seleniumdecoded.com/learn/modern-selenium/whats-new-in-selenium-4/
- https://seleniumdecoded.com/learn/modern-selenium/webdriver-bidi/
- https://github.com/mozilla/firefox-devtools-mcp
- https://hostedmcp.org/servers/mozilla/firefox-devtools-mcp
- https://pypi.org/project/zenpilot/0.2.0/
- http://glama.ai/mcp/servers/ilhamnadhif/claude-for-zen
- https://glama.ai/mcp/servers/simon-ami/zen-devtools-mcp
- https://glama.ai/mcp/servers/sh6drack/zen-mcp/tree
- https://mcpdirectory.fyi/us/global/online/zen-mcp
- https://mcpservers.org/servers/hamb1y/foxhand
- https://www.techbytes.app/posts/linux-use-agent-first-gui-control-for-linux/
- https://ainews.leverageai.com.au/case/linux-use-accessibility-agent-control
- https://github.com/vercel-labs/agent-desktop
- https://dev.to/piekwerk/vercel-agent-desktop-computer-use-for-coding-agents-through-the-accessibility-tree-5fap
- https://www.aighten.com/en/blog/vercel-agent-desktop-computer-use-accessibility-tree
- https://glama.ai/mcp/servers/ahmetadakli/kde-desktop-mcp
- https://pypi.org/project/kwin-mcp/0.3.0/
- https://cua.ai/blog/inside-linux-computer-use
- https://www.rl-list.com/vendors/cua
- https://docs.gormes.ai/upstream-hermes/user-guide/features/tools/computer-use/
- https://github.com/microsoft/Hybrid-Computer-Use
- https://arxiv.org/html/2507.05791v1
- https://osworld-grounding.github.io
- https://arxiv.org/pdf/2508.04412v3
- https://github.com/tomsalphaclawbot/openclaw-vnc-control/blob/HEAD/docs/CLICK_ACCURACY_RESEARCH.md
- https://ruoqijin.com/blog/mac-auto-bridge-cloud-ocr
- https://github.com/temm1e-labs/temm1e/blob/HEAD/tems_lab/gaze/RESEARCH_PAPER.md
- https://github.com/tongyi-mai/mobileworld/blob/HEAD/site/blog_posts/Why%20your%20AI%20Agent%20keeps%20misclicking.md
- http://benchmarkingagents.com/osworld/
- https://fintekcafe.com/computer-use-agents-design-guide/
- https://www.canagentswork.com/benchmarks/osworld-2/
- https://glama.ai/mcp/best/browser-automation
- https://chatforest.com/reviews/browser-extension-mcp-servers/
- https://crates.io/crates/browser-control-mcp/0.15.0-beta.25
- https://browser-use.com/posts/best-mcp-servers-to-control-a-browser
- https://explainx.ai/skills/vercel-labs/agent-browser/agent-browser
- https://www.alterhunt.com/tools/agent-browser
- https://www.awesome-mcp.com/servers/blueprint-mcp
- https://webmcp.com/windtunnel-paper.pdf
- https://github.com/agricidaniel/web-mcp/blob/HEAD/skills/webmcp/references/claims-and-maturity.md
- https://ipv6.velacore.au/what-is-webmcp/
- https://dplouffe.ca/2026/10/10/webmcp-browser-agent-tools/
- https://karatelabs.io/blog/dom-vs-screenshot-ai-testing
- https://dev.to/siropkin/accessibility-tree-vs-screenshots-the-token-math-behind-my-browser-agent-3fk9
- https://dev.to/neeraj_sharma_757fbb49aa7/pixels-vs-the-accessibility-tree-i-measured-what-a-web-page-costs-an-ai-agent-67-lines-of-python-2hn8
- https://pypi.org/project/hypruse/0.6.0/
- https://glama.ai/mcp/servers/keanehatescoding/hyprland-mcp
- https://linuxcommandlibrary.com/man/hyprctl

## 13. Blockers

- None. No blocker lasted more than 15 minutes. All searches returned results. Two primary repos (Hybrid Computer Use, agent-desktop) were opened directly and verified.
- Limitation to report to parent: as a subagent I cannot operate a live browser, so no live Zen test was run. All UNVERIFIED items in section 11 need a live-browser agent to test on the laptop.
