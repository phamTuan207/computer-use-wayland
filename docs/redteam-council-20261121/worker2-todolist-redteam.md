# Redteam Worker 2: adversarial review of the Zen error-fix todo list

- Worker: Redteam Worker 2
- Date: 2026-11-21
- Start: 03:32:47 Asia/Ho_Chi_Minh
- Report written: about 03:36 Asia/Ho_Chi_Minh, elapsed about 4 minutes
- Target file: ~/workspace/zen-error-fix-todolist-20261121.md
- Source error file: ~/workspace/cf26-upload/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md (parts A to I)
- Method: read the todo list in full, read the error file in full, read the coordinate-accuracy note, read the already-existing BiDi research and test-results files, checked BiDi and Zen claims against public sources dated 2026. No live browser work was done. No claim below is invented. Where evidence is missing, that is stated as missing.

## Executive verdict

The todo list is a thorough catalogue of errors, but as a plan it is weaker than it looks. Three findings dominate everything else.

1. The todo list is already stale. Phase 1 is half executed. A test-results file exists at ~/workspace/zen-automation-test-results-20261121.md, timestamped 02:56 to 03:25 on 21/11/2026, and it already answers two of the five Phase 1 tools: Playwright is confirmed dead for Zen, zen-mcp 1.2.3 WORKS, zenpilot 0.7.0 WORKS. The todo list still shows all of 1.1.1 to 1.1.5 unchecked, with no link to that results file. A plan that does not know its own first phase is half done will duplicate work and will mislead anyone who picks it up.
2. The DOM-first assumption is directionally right for web pages and badly oversold as a cure for the whole error list. DOM control bypasses one specific failure, the screenshot-to-screen coordinate transform, but the evidence in the error file points to at least four other independent failure sources that DOM does not touch: model think time, fabrication, blocker reporting, and the overlay flicker whose cause is explicitly unknown. The 10x speed claim has no pre-registered baseline and contradicts the project's own prior measurement, which found think time is about 94 percent of wall time.
3. There is no fallback, no go/no-go criteria, and no ordering logic. If all five tools fail, the list has no next step. If calibration alone fixes most clicks, the list still does BiDi first. The single BiDi session, the Zen restart precondition, the navigator.webdriver bot-detection risk, and the file-upload gap are all absent from the list. Each of these can kill the plan on its own.

Overall: Phase 1 is sound in intent but stale and under-specified. Phase 2 is the strongest phase in content but mis-ordered. Phase 3 is mostly a checklist of already-known fixes with weak verification. Phase 4 is a dumping ground, not a phase. Phase 5 has no pass criteria and therefore cannot pass or fail.

## 1. Challenge to the DOM-first assumption

### 1.1 What DOM actually fixes, and what the evidence says the real problem is

The error file gives a precise, measured clue. From the coordinate-accuracy note (computer-use-wayland/improvements/muse-coordinate-accuracy-20261120.md): observation image 1200x757, window 1863x1176, scale 0.644. The ratio 1863/1200 is 1.5525 and 1176/757 is 1.553. Clicks aimed at View landed on Remove and Rejudge, consistently to the RIGHT of the aimed point: x=940 did nothing, x=850 and 837 hit Rejudge, x=825 and 805 hit Remove. That is a systematic, directional, repeatable offset, not random grounding noise. A systematic offset of this shape is exactly what a wrong coordinate transform produces, and it is exactly what a calibration fix would correct.

The user said the root cause at 19:27 on 20/11 (I6): the Muses do not understand the screen they are driving, its ratio, scale, or geometry, so computed coordinates do not match the real screen. That is a calibration claim, not a DOM claim. DOM is one way to route around it. Calibration is the direct fix for it. The todo list treats DOM as the fix and calibration as item 2.1.1, buried inside Phase 2 after Phase 1. That ordering assumes the answer before testing it.

### 1.2 The click-miss evidence does not uniquely support DOM-first

H3 in the error file lists four suspected causes, and all four are still unproven: (1) unknown screen ratio and scale factor, (2) observation coordinates not matching real screen coordinates, (3) visual grounding measuring pixels wrong, (4) observation crop or resize shifting coordinates. DOM-first only addresses causes 2, 3, and 4, and only for web page content. It does nothing for cause 1 as a general property of the machine, because the machine still has a scale the agent does not know, and every non-browser click still depends on it.

Three further facts weaken the DOM-first inference:

- I7: agents running directly on the laptop are fast and accurate, while Muse on the VM and Sia both miss often. If the visual grounding model were the problem, on-laptop agents using the same class of model would miss at a similar rate. The difference points at the VM-to-laptop path (screenshot capture, resize, transport over Tailscale and SSH, coordinate transform), not at the browser. DOM from the VM still crosses that same network path for its control channel, and the todo list never says where the BiDi client runs, on the VM or on the laptop.
- I8: no test ever measured hit rate separately. Misses were buried inside retries, and a task still counted as pass if the agent eventually clicked the right thing. So there is no baseline hit rate, no baseline wall time per click, and no measurement that isolates grounding error from think time from retry loops. A comparison in 1.2.2 between DOM and screenshot/mouse, run against an uncalibrated screenshot baseline, will flatter DOM by an unknown amount. It compares a fixed method against a broken baseline.
- G13 and the Pick 4 prior art: the 10x review says the think-observe-think loop is 87.8 percent of task time, and the Pick 4 summary (computer-use-wayland/improvements/speed-proto-pick4-summary.md) records a baseline anchor of think 34.2s of 36.4s wall, 94 percent, with the explicit note that only model-think cuts can move the total and grounding aids only win if the model skips its own vision re-grounding. Pick 4 Arm 2, the fast path, moved mean wall from 170.4s to 79.9s but the clean pair barely moved, 43.7s to 41.7s, about 5 percent. Faster actions alone cannot produce 10x when actions are a small slice of wall time. The todo list never engages with this measurement. It asserts 10x as a goal in Phase 1 and E3 without a model of where the time goes.

### 1.3 DOM does not fix the biggest non-click errors

- Overlay flicker (H1, I9, I10): cause explicitly unknown as of 02:30 on 21/11. The source report records that the screenshot-volume explanation was retracted. Given the reported 10-30 second observation cadence and no captures during the idle interval, normal capture cadence alone does not account for continuous 10 Hz flicker; those conditions were not independently measured in this review. DOM control does not touch the pill render loop. Nothing in Phase 1 investigates it. Item 2.2.1 correctly says the cause is unverified, but Phase 1 proceeds as if the browser-control change were the priority anyway.
- Slow decisions (H2, I13, I14, I15, I16): the error file concludes slowness came mostly from miss, re-observe, and re-click loops, but there is no per-step think-time log at all. DOM removes some re-observe cycles, but the model still has to read a DOM snapshot, decide, and issue the next call. The test results show zen-mcp click at 2 to 3ms and zenpilot click at 439ms, but those are tool-call times, not decision times. No end-to-end wall time on a real task has been measured for either tool. Item 1.3.2 promises that measurement only after integration, which is too late to justify the choice.
- Fabrication (I17 to I26, A7, A8): inventing rules, misattributing rules to Hieu, guessing that a blocking error is only a warning. These are model-behavior and process failures. DOM gives the model truer observations, which may reduce some guessing, but it cannot stop a model from asserting an unverified claim. Phase 2.4 lists the fixes correctly, but nothing in Phase 1 helps them, and the todo list's framing implies the tooling phase comes first.
- Blocker reporting, monitoring, killing stuck agents (A4, A5, A6, I27 to I30, G15 to G17): process and watchdog failures. DOM is irrelevant to all of them.
- The file-picker blocker (I27, 70 minutes stuck, 15:37 to 16:47): the single most expensive incident in the whole error file. DOM is weakest exactly here. See section 3.4.

### 1.4 What DOM cannot reach at all

DOM control, by definition, only reaches web page content. The error list contains many failures outside any DOM:

- Native file-picker dialog (GTK dialog, OS level). BiDi cannot click inside it. The only DOM-side answer is input.setFiles, which bypasses the dialog rather than driving it.
- Browser-native dialogs and the Zen chrome itself: tabs, address bar, the Zen-specific Ctrl+N versus Ctrl+T inversion (C3, I32, I33), the delete-working-copy dialog (I2, I19).
- Desktop apps, the image viewer (G5, imv-wayland), terminal work, and window geometry (G2, Hyprland tiling).
- The overlay pill itself, which is a separate overlay process, not a web page.

A plan that calls itself "Zen maximally controllable" while only covering page DOM is misnamed. It should be called "page-DOM control", with the non-DOM surface explicitly listed as out of scope and still needing the screenshot and mouse path. The todo list never draws that boundary, so a reader will assume DOM replaces computer-use. It does not. It replaces one layer of it.

## 2. Risks of the BiDi approach

Each risk below is grounded in a named source. None of them appears in the todo list.

### 2.1 The restart precondition, and the false claim that no restart was needed

The golden rule from the research file (firefox-automation-research-20261121.md, section 4.7) and from multiple public sources: there is no way to attach a debug port to a Firefox or Zen instance that was launched without the flag. Relaunching the binary against a running instance hands off and exits silently, opening no port. Verified against Firefox 153.0.3. The firefox-mcp README states the same: if Firefox is already running with the same profile, the command only opens a new window in that instance and the flags are ignored.

The test-results file shows what this cost in practice: at 02:56 on 21/11 the BiDi port was not up, Zen had been running since 02:18 before the .desktop flags were added at about 02:55, and the coordinator killed Zen (TERM then KILL) and relaunched it with a stolen Wayland environment at 02:58. That is a real restart of the user's live browser, with the user's tabs and sessions at stake, done in the middle of the night. It worked, and session restore kept the tabs, but the todo list never records this as a step, a risk, or a rollback plan.

Worse, the test-results file then claims "Neither needed any Zen restart, profile change, or extension." That is false as written. The tools themselves did not restart Zen, but a restart was a precondition performed minutes earlier by the coordinator. The todo list repeats the same blind spot at 1.3.3, which says the .desktop update "da xong (02:55 21/11), verify lai sau reboot" with no definition of what verification means, no check that the flags survive a Zen update, and no rollback if the flags break Zen launch. If a future Zen update rewrites or ignores the .desktop file, BiDi silently stops working and every dependent workflow fails at once, with no diagnostic in the plan.

### 2.2 One BiDi session at a time, and zombie sessions

Firefox allows one BiDi session at a time. Sources: the bidi-lite docs (a second session fails with "Session already started"), zenpilot docs (one session at a time, released after 2 minutes idle), claude-for-zen docs (one session per browser, needs a session broker), and the research file. The session outlives the connection: dropping the client closes the socket but does not end the session, and Firefox keeps refusing new sessions until the browser restarts unless the client ends it cleanly. The zen-mcp docs say a zombie session is only cleared by restarting Zen.

This is a single point of failure with three concrete consequences the todo list ignores:

- Concurrent workers cannot each hold a BiDi session. The test-results file already records the symptom: other workers were driving Zen concurrently, the active tab changed on its own between runs, and context IDs regenerated on every new BiDi session. The todo list's Phase 1 runs five workers in parallel against one browser with one session slot and no coordination protocol. That is a race, not a test plan.
- A crashed or killed client locks every other agent out until Zen restarts. There is no session-broker item, no session-cleanup item, and no watchdog item for BiDi session health. The existing watchdog (G16, G17) watches computer-use processes, not BiDi sessions.
- The multi-agent deliberation idea (E1, item 3.4.1) conflicts directly with the single-session limit. Many agents deliberating is fine, but only one can drive, and the handoff between drivers needs a session broker. The todo list never reconciles E1 with the BiDi constraint.

### 2.3 navigator.webdriver and bot detection

The research file flags this explicitly and honestly: navigator.webdriver reports true while a Marionette or BiDi session is active, Mozilla warns Marionette can trigger bot detection at Cloudflare and Akamai, and this was not verified separately for BiDi-only mode on Zen. It needs testing on the real machine before use on a site with bot checks. The todo list has no such test item. This matters because the real tasks are Polygon and Codeforces, and I36 already records the live possibility of a Cloudflare box on Codeforces. If BiDi trips bot detection on the exact sites the whole project exists to drive, the DOM-first plan fails at the point of use, and the failure will look like a login or access problem, not a tooling problem. The plan should have a named item: check navigator.webdriver under BiDi-only mode, test Polygon and Codeforces with a BiDi session active, and record the result before committing to BiDi as the primary path.

### 2.4 Profile mutation from enabling remote debugging

zenpilot documents that before Zen starts with remote debugging it always sets remote.prefs.recommended to false in the profile user.js, because without it Firefox's remote agent rewrites about 40 prefs for test automation and Zen writes them into the profile, where they stay. That is a persistent mutation of the user's daily-driver profile, made by a tool the todo list treats as a candidate. The todo list has no item to audit which prefs change, no item to back up the profile before enabling the flags, and no item to restore prefs if the tool is abandoned. Given the standing rule that personal data never leaves the laptop and the profile holds logins and sessions, this is a gap, not a detail.

### 2.5 Zen is a fork, and its BiDi behavior already differs from Firefox

The strongest evidence is already in the test-results file, and it cuts against the assumption that Firefox documentation transfers cleanly to Zen. Playwright's moz-firefox launch did handshake successfully, but every page-creation path failed with the same Zen-specific error: "browsingContext.create: unsupported operation, Message: openWindow() not supported in Zen". The research file had predicted launch would work. It did not, for a Zen-specific reason. That is a live demonstration that Zen diverges from Firefox in its BiDi implementation, and it was discovered by testing, not by reading Firefox docs.

Consequences: every Firefox BiDi claim in the todo list needs Zen-specific verification, including Puppeteer connect, Selenium connect-existing, and firefox-mcp connect-existing, none of which have reported results yet. Zen updates ship on Zen's schedule, and a Zen update can change BiDi behavior without any change in Firefox. The todo list has no item for pinning or recording the Zen version under test (the tests ran on Zen 1.24.2b, Firefox 160.0), no item for re-testing after a Zen update, and no item for what happens if a Zen update breaks the chosen tool. The plan treats BiDi as a stable platform. It is a W3C Working Draft, snapshot 1 June 2026, with modules still missing (accessibility tree, coverage and profiling, screencast in flight, WebAuthn virtual authenticators). Mozilla is actively changing it.

### 2.6 Security: no authentication on the BiDi socket

The research file and the browxai RFC both state it plainly: any local process can connect to the BiDi WebSocket, there is no encryption or auth on the socket, loopback only, and W3C issue 1188 (28 October 2026) is discussing adding authentication precisely because agentic browsing now uses real profiles with cookies, saved credentials, and payment data. The todo list proposes leaving a permanent BiDi port open on the user's daily browser, with the user's logged-in Polygon, Gmail, and Codeforces sessions, and never mentions this. At minimum the plan needs an item: bind loopback only, document who can connect, consider the zenpilot allowlist model, and decide whether the port stays open when no agent is working or is only enabled per session.

### 2.7 The file-upload gap, the exact place the project bled most

The research file states there is no file upload or drag-and-drop via BiDi (zen-mcp docs), and zenpilot has an upload tool only from folders listed in upload_dirs, empty by default, and it was not tested. The BiDi spec does define input.setFiles (MDN documents it), so a correct client can set files on an input element without opening the picker, but that is not the same as the tools under test supporting it. The live evidence is discouraging: Mozilla bug 2083461, opened 27 days before this review and fixed 19 days ago, reports that firefox-mcp upload_file_by_uid returned success while setting no file, files.length stayed 0, no change event fired. The regression came from a change in how the tool sent input, and the fix was to migrate to input.setFiles. A tool that reports success while doing nothing is the worst failure mode for this project, because it feeds the fabrication pattern (A7, A8, I22) rather than fixing it.

The file picker was the 70-minute blocker (I27) and the Browse-button hover fix (B9, I21, G21) is a real-mouse phenomenon. A DOM click that bypasses hover state might work, or might not trigger the same code path, and the todo list asserts "Sua: click bang DOM" for I2, I3, I4, I5, and 2.1.2 to 2.1.6 without a single test of a DOM click against the Polygon Browse button, the file input, or a native dialog. The plan must test input.setFiles and the real Polygon upload flow before claiming DOM fixes the upload path. If it cannot, the screenshot and mouse path must remain for uploads, and the plan must say so.

### 2.8 Tooling immaturity and silent success

Two of the five tools are young and lightly maintained. zenpilot is explicitly alpha, tested on macOS with Zen 1.23.2b, and the test run used 0.7.0, far newer than the 0.2.1 in the research report. zen-mcp is a community project (sh6drack). The firefox-mcp regression above shows even Mozilla's official tool ships silent-success bugs. The todo list has no item for pinning tool versions, no item for checking maintenance status, and no item for what happens when an upstream tool changes behavior. The test results already show version drift inside a single day: research cited zenpilot 0.2.1, tests ran 0.7.0.

## 3. What could fail in Phase 1, and the missing fallback

### 3.1 Phase 1 as written has no decision procedure

Items 1.1.1 to 1.1.5 list five tools and four verbs each (list tabs, read DOM, click, type) plus timing. But there is no pre-registered pass threshold: how fast is fast enough, what hit rate counts as accurate, how many consecutive runs count as stable, what failure disqualifies a tool. Item 1.2.1 says to summarize WORKS, PARTIAL, or BROKEN, but gives no definition of those words. Item 1.2.2 asks how many times faster DOM is, but there is no baseline wall time for the same task done the old way, and no named real task to run both ways. Item 1.2.4 says to pick the best tool, but does not say who decides, by when, or what happens on a tie.

Without thresholds, the phase cannot fail. Any result can be declared good enough. That is the same measurement hole as I8: tests that only record pass or fail, with no hit-rate metric, hide the real problem.

### 3.2 The five-way test is already partially obsolete

As of the test-results file (03:25 on 21/11):

- 1.1.5 Playwright: DONE, confirmed dead, and more dead than predicted (launch also cannot drive Zen). The todo list should mark it done and stop spending effort on it.
- 1.1.4 zenpilot and zen-mcp: DONE, both WORKS, with timings. zen-mcp is fastest (ops 2 to 20ms, arbitrary JS, no safety model). zenpilot is slower (click 439ms, type 478ms, first read 1026ms) but safer (allowlist, audit log, no arbitrary JS). The choice between them is a speed-versus-safety tradeoff the todo list never frames.
- 1.1.1 Puppeteer, 1.1.2 firefox-mcp, 1.1.3 Selenium: results still pending in the file ("Worker results (pending - filled in as workers report back)"). Clone1 delivered Puppeteer BiDi test code on GitHub (commit 1ef0816), but no run result is recorded.

So Phase 1 is two-fifths complete and the todo list does not reflect it. The remaining risk is concentrated in the three unreported tools, and the plan has no deadline for them.

### 3.3 Dependencies on other agents with no owner and no deadline

- 1.1.3 depends on clone2 delivering Selenium code "khi no nop len GitHub". No date, no owner, no fallback if it never arrives.
- 1.1.4 depends on opencode testing zenpilot and zen-mcp. The results file shows the work was actually done directly via SSH from the VM, not via opencode, with the note "Depth 2 cannot spawn subagents, and direct shell was the fastest path with zero tokens burned. No opencode tokens were used at all." The method deviated from the plan, and the plan has no way to record that.
- 1.1.5 depended on fcc testing Playwright. The results file shows it was also run directly via SSH exec as the owner, not via fcc, "same commands, same account".

A phase whose execution method is "whoever is available runs it somehow" is not a test protocol. Each tool needs one owner, one deadline, and one named machine and profile.

### 3.4 The concurrent-test confound

The test-results file records that other workers were driving Zen concurrently, the active tab changed on its own between runs (YouTube at 03:21:33, httpbin at 03:22:00), and BiDi context IDs regenerated on every new session. Tab order stayed stable, and the tester used new tabs only and restored state, but the runs were not isolated. A click test that runs while another worker switches tabs is not a clean measurement. The todo list has no isolation rule: one driver at a time, no concurrent Zen driving during a timed test, and a named baseline tab set. Given the single BiDi session limit, this is not optional.

### 3.5 The missing fallback

There is no fallback anywhere in Phase 1. Item 1.2.3 asks for a breakthrough direction "neu co", which is an invitation, not a fallback. The concrete fallback options the research file already identified are not in the todo list:

- WebExtension plus native messaging (Inari MCP, mcp-browser-bridge, or a small custom extension). This is the only path that attaches to a running Zen without restart and without flags, and it was documented in the research file (section 4.6). It is limited to page-level DOM and cannot touch browser UI or the file picker, but for Polygon and Codeforces page work it is sufficient. It should be the named fallback if BiDi attach fails or if the restart is unacceptable.
- Keep the calibrated screenshot and mouse path as the fallback and as the permanent path for non-DOM surfaces. The todo list treats the old path as something to replace, not as a fallback to preserve.
- A minimal raw-BiDi client (the firefox-cdp adapter pattern, about 700 lines of Python, MIT) as the build-it-ourselves fallback if all five tools fail. The research file documents it. The todo list does not mention it.

A phase with no fallback and no go/no-go date will drift. The correction is simple: add a decision date, a named fallback (extension bridge first, calibrated mouse path second), and a rule that if no tool passes the pre-registered thresholds by that date, the fallback is adopted and Phase 1 closes.

## 4. Ordering: calibration before, independent of, or after BiDi

The ordering is wrong, and the evidence for saying so is the project's own data.

### 4.1 Calibration is cheap, independent, and fixes the non-browser surface too

Calibration means: record the exact resolution, Hyprland scale, and monitor geometry; verify the image-to-screen coordinate transform end to end with a known target; measure the systematic offset; and encode the correction so every screenshot-based click uses it. The coordinate note already gives the numbers to start from (image 1200x757, window 1863x1176, scale 0.644, clicks landing right). This is a measurement task, not a rewrite. It can be done in parallel with BiDi testing, it does not depend on BiDi, and it fixes clicks everywhere DOM cannot reach: desktop apps, dialogs, the file picker, Zen chrome, and the image viewer.

The todo list puts it at 2.1.1, after all of Phase 1. That means Phase 1's comparison (1.2.2) is run with a known-broken baseline, Phase 1's tool choice is made before knowing whether the cheaper fix works, and the team may invest in BiDi integration (1.3.1) to solve a problem calibration already solved.

### 4.2 Could calibration alone solve 80 percent?

The honest answer is: unknown, and the todo list is structured so it will stay unknown. The 80 percent figure is a hypothesis, not a measurement, because hit rate was never measured (I8). But the shape of the evidence favors calibration strongly:

- The offset is systematic and directional (always right), which is the signature of a transform error, not of random model error.
- The on-laptop agents are accurate with the same class of model, which points at the path, not the model.
- The user named calibration as the top priority (I6, 19:27), and the coordinate note calls it the most important fix.

The correct experiment is cheap and should come first: measure hit rate on a fixed set of real targets before and after calibration, with no BiDi involved. If hit rate goes from the observed pattern (multiple misses per target, e.g. four aimed clicks at View all missing) to near-first-try, then BiDi becomes an optimization for speed, not a rescue for accuracy, and the integration decision changes completely. If calibration does not fix it, then the grounding model or the screenshot pipeline is implicated, and DOM-first gains real support. Either way, the experiment is the thing that decides. The todo list never runs it as a standalone experiment.

### 4.3 The corrected order

1. Calibrate and measure hit rate on held-out real targets (Polygon pages, not example.com). This is a half-day measurement task.
2. Run the BiDi tool tests in parallel or immediately after, with the calibrated baseline as the comparator, so 1.2.2 measures DOM against a fair baseline instead of a broken one.
3. Only then choose and integrate.

The todo list does 2, then 1, then 3, which guarantees the comparison is biased and the choice is made on incomplete information.

## 5. Alternatives not in the todo list

The todo list's Phase 1 tests five tools that are all the same idea: BiDi clients. It never tests the other families, even though the project's own prior work and the research file name them.

### 5.1 Accessibility tree (AT-SPI)

AT-SPI is the Linux accessibility stack. It gives structured names, roles, states, and bounding boxes for UI elements, without vision. The project already tried it: Pick 4 (speed-proto-pick4-summary.md) ran an a11y probe and fast-path arms. The results were mixed and are directly relevant, but the todo list never mentions them:

- Direct cu.py a11y observe on Nautilus returned 3 elements with extents, but a11y ground failed both times with "cannot tell whether extents are screen or window relative; use vision".
- For Zen, kitty, and other apps, a11y observe failed with "exact app PID required; use a11y apps", which the report calls a probe PID-lookup artifact (hyprctl window PID is not the AT-SPI app PID), not a verdict on those apps.
- Through the broker, a11y calls returned unsupported_command. The broker does not implement a11y commands at all.

So AT-SPI is not a drop-in replacement, but it is a live lead with known blockers (broker support, coordinate-frame ambiguity, PID lookup), and it has one decisive advantage over BiDi: it covers desktop apps and native dialogs, not just web pages. It deserves a named item, even if the verdict is "tried, blocked at broker, revisit after BiDi". Its absence means the team may rediscover Pick 4's findings from scratch.

Public tooling in this family (tine-cli, Touchpoint, bad-ass-mcp) also exists, but the honest note is that they are young, mostly GNOME-targeted or generic, and none is proven on Hyprland and Zen. They should be listed as investigated and not adopted, not silently omitted.

### 5.2 Hyprland IPC for window positions

hyprctl already gives exact window positions, sizes, and monitor geometry. The geometry fix (G2) used exactly this: floating plus resize to exactly 901x1176 at [2990,914], 0px deviation. That is a proven, working, non-vision source of ground truth for window geometry, and it is already in the codebase. The todo list never proposes using hyprctl output as the calibration source for the screenshot transform, even though it is the most direct way to verify what the screenshot claims about window position. A calibration item that does not mention hyprctl is missing its best instrument.

### 5.3 Fixing the screenshot pipeline instead of replacing it

The screenshot path has at least three named suspects (H3): crop, resize, and scale. The observation image is 1200x757 while the window is 1863x1176. Something resizes by a factor of about 1.55, and the click transform has to invert that exactly. The todo list never asks for an audit of that pipeline: who resizes, with what algorithm, is the aspect ratio preserved, is there a crop offset, is the scale factor recorded in the observation metadata. A pipeline audit is a small, high-leverage item. If the resize is lossy or the scale is rounded (0.644 is a rounded number), no amount of model improvement will fix clicks, and DOM will look better than it is simply because it skips the pipeline. The plan should audit the pipeline before abandoning it, because the pipeline is still needed for every non-DOM surface.

### 5.4 Native Wayland protocols and the extension bridge

Native Wayland protocols are correctly not a practical path: Wayland deliberately does not let one client read another client's surfaces or inject input, which is why the project uses a relay, a pill overlay, and grim screenshots. The todo list is right not to propose Wayland protocol work, but it should say so in one line, so nobody re-proposes it.

The extension bridge (section 3.5 above) is the practical alternative the list omits. It is the only no-restart attach, and Zen accepts unsigned local extensions, per the research file. It should be tested as a candidate in Phase 1, not left as a footnote in the research file.

### 5.5 The missing middle: DOM snapshot plus verified mouse click

There is a hybrid the list never considers: use DOM to find the element and get its exact bounding box, then click it with the real mouse through the existing computer-use path, using the calibrated transform. That hybrid fixes the grounding problem (the model no longer guesses from a screenshot) while keeping real input events, which is exactly what the Browse hover-state fix needs (B9: the button must darken under a real hover before a real click registers). A pure DOM click via input.performActions may or may not reproduce hover state, and a JS element.click() certainly does not. The hybrid is testable in an afternoon and it de-risks the BiDi bet. It should be an item.

## 6. What the todo list is missing

### 6.1 Placeholders instead of items

- 2.5.8: "I28-I30: (doc them trong file LOI-COMPUTER-USE-TU-LICH-SU-CHAT, phan 5)". That is not an item. I28 is the failure to monitor the .cpp and NB2 fix and start problem 3, I29 is the inability to stop an agent after a pause order, I30 is the overnight non-reporting. Each needs its own fix, and I29 in particular (no kill switch for a delegated agent) is a safety gap.
- 2.6.6: "I32-I40: Chi thi sai cho worker, hanh dong truoc GO (doc them trong file chat)". That is nine distinct errors (wrong Ctrl+L instruction, Ctrl+T confusion, wrong order versus Hieu, acting before GO, false readiness without a live login check, forgetting the workflow, asking the user to click, cross-channel reminder, buried disclosure of self-written solutions) compressed into one placeholder. None of them has a fix in the list.
- Phase 4, item 4.6: "User decisions con no" lists six decisions (H1-BASE recovery, Step 3 go/no-go, save-dialog fix Part B, ~/backups about 99 GiB, Omarchy restore steps) with no owner and no date. These are not Phase 4 work, they are open decisions that block other work.

### 6.2 Error categories with no coverage

- No security item (section 2.6 above).
- No BiDi session management item: broker, cleanup, zombie-session recovery, watchdog for session health.
- No version-pinning item: Zen version, tool versions, re-test after Zen update.
- No navigator.webdriver and bot-detection test item (section 2.3).
- No profile backup and pref-audit item (section 2.4).
- No definition of done for the overlay flicker: 2.2.1 to 2.2.5 list investigation steps, but there is no criterion for "fixed" (flicker rate measured how, over how long, with what tool) and no owner for the investigation.
- No item for the H1 correction: the LOI file's Part H says the flicker happened while Codex was driving, but I9 shows the opposite, Codex driving was normal and Muse driving flickered. The todo list's 2.2.1 gets it right, but there is no item to correct H1 in the source file, so the error file stays wrong.
- No item for I25 (claiming to see images during a voice call, miscounting 2 versus 11) beyond the generic fabrication items, and no item for the counting and vision-reliability problem it exposes.
- No item for G25 and G26. The LOI file jumps from G24 to G27. Either two items were lost in numbering or the source file has a gap. The todo list copies the gap silently instead of flagging it.
- No item for the test-methodology fix as a first-class deliverable: hit-rate measurement, held-out test sets, and the G14 anti-memorization rule applied to Phase 1 itself. Phase 1 tests on example.com and httpbin, which are toy sites with no login, no file upload, no Cloudflare, and no Polygon dialogs. That violates the project's own held-out principle (G14) in the very phase that is supposed to choose the tool.

### 6.3 Single points of failure

- One BiDi session (section 2.2).
- One browser profile with all logins, mutated by remote-debug prefs, with no backup item.
- One .desktop file carrying the flags, with no verification after reboot or update.
- One chosen tool (1.2.4 picks a single winner) with no fallback tool named.
- One person (Muse) as the tester for 1.1.1, with no independent verification of the results. The test-results file already shows why this matters: the "neither needed any Zen restart" claim is wrong, and the concurrent-driving confound was not controlled.

## 7. Verdicts per phase

### Phase 1, Zen automation testing: RISKY, and stale

Sound in intent: testing five tools on the real Zen with timing is the right experiment. Risky in execution: no thresholds, no baseline, no isolation, no owner per tool, no deadline, no fallback, and the results file already answers two tools while the list still shows them open. The Playwright result is stronger than predicted and should close 1.1.5 immediately. The zen-mcp versus zenpilot choice is a speed-versus-safety tradeoff the list never frames. The three pending tools need a deadline and a fallback (extension bridge, then calibrated mouse path). The phase also needs a pre-registered rule: one driver at a time, no concurrent Zen driving during timed tests.

### Phase 2, fix Muse errors: SOUND in content, FLAWED in ordering

This is the strongest phase. The error catalogue is faithful to the source file, the priority order inside 2.1 (click misses first) matches the user's stated priority, and 2.2.1 correctly refuses to assert an unverified cause for the flicker. The flaws are: calibration (2.1.1) sits after Phase 1 instead of before it; several fixes assert "Sua: click bang DOM" for cases where DOM clicking is unproven (Browse hover state, native dialogs, file upload); and 2.5.8 and 2.6.6 are placeholders, not items. The phase also has no measurement definitions: no hit-rate target, no think-time logging format, no flicker-rate measurement method. Without those, "fixed" is unverifiable.

### Phase 3, fix Codex and system errors: SOUND as a checklist, RISKY as a plan

Items 3.1.1 to 3.1.8 and 3.2.1 to 3.2.13 are concrete, correct, and mostly already known. The risk is that they are listed as if listing them fixes them. Most are brief-writing and checklist items (put the lesson in every brief, follow Hieu's order, use the right extension, renumber tests). There is no verification step for any of them: no item that says "verify the next worker brief actually contains all 20 lessons" or "verify the next upload actually renumbers". Item 3.4.1 (multi-agent deliberation) is marked as an experiment with no hypothesis and no metric, and it conflicts with the single BiDi session limit. Item 3.4.3 (10x) is marked PAUSED with no resume condition beyond "after Zen", which is not a condition.

### Phase 4, outstanding items: FLAWED

This is not a phase. It is six unrelated leftovers (pill blur, cookie research, speed loop, Track 2, pill candidates, open user decisions) with no order, no owner, and no dates. Item 4.1 (increase pill blur) is a one-line user instruction from 02:15 on 21/11 that could be done in minutes, and it sits next to Track 2, which is paused pending a council decision. Mixing trivial and blocked items in one list guarantees the trivial ones wait for the blocked ones. Each item needs its own owner and date, or it needs to move to the phase it belongs to (pill blur belongs with 2.2, Track 2 stays paused with its gate stated).

### Phase 5, retest and report: FLAWED

Items 5.1 to 5.3 promise a retest on a real task, a before-and-after comparison, and a summary report, but name no task, no baseline, no pass criteria, and no held-out set. After G14 (anti-memorization) and I8 (no hit-rate measurement), a retest phase with no defined test set is a repeat of the original error. It also has no independence requirement: the same agent that built the fix should not be the one that declares it fixed. The phase needs a named real task (a Polygon upload of the same shape as the 20/11 incident, on held-out problems), a hit-rate target, a wall-time target, and an independent checker.

## 8. Concrete corrections

These are the minimum changes that would make the plan defensible. Each one is written so it can be pasted as a todo item.

1. Update Phase 1 to reflect reality: mark 1.1.4 and 1.1.5 done with links to ~/workspace/zen-automation-test-results-20261121.md, record Playwright as dead (including the Zen-specific openWindow rejection), and record zen-mcp and zenpilot as WORKS with their timings. Set a deadline for the three pending tools (Puppeteer, Selenium, firefox-mcp) and name one owner each.
2. Move calibration to the front: create a Phase 0 that records resolution, Hyprland scale, and monitor geometry, audits the screenshot resize pipeline, verifies the transform end to end with a known target, and measures hit rate on held-out Polygon targets before and after. Do this before the BiDi comparison in 1.2.2, so DOM is compared against a fair baseline.
3. Define Phase 1 pass criteria before running more tests: minimum hit rate on real targets, maximum per-action time, stability over a named number of consecutive runs, and a named real task for the end-to-end wall-time comparison. Record the old-path baseline on that same task first.
4. Add a fallback and a go/no-go date to Phase 1: if no tool passes by the date, adopt the WebExtension plus native-messaging bridge for page work and keep the calibrated mouse path for everything else. Name the fallback explicitly. Do not leave 1.2.3 as an open invitation.
5. Add a one-driver-at-a-time rule for all timed tests: no concurrent Zen driving during a test, a named baseline tab set, and restoration verified after each run.
6. Add a BiDi session-management item: a session broker or equivalent, clean session end on every exit path, zombie-session detection, and a watchdog check for BiDi session health. Test what happens when a client crashes mid-session.
7. Add a restart and rollback item: back up the Zen profile before enabling flags, record the exact .desktop change, verify the flags survive a reboot and a Zen update, and document the rollback (remove flags, restart, verify logins). Correct the false "no restart needed" claim in the test-results file.
8. Add a bot-detection test item: check navigator.webdriver under BiDi-only mode on Zen, and test Polygon and Codeforces with a BiDi session active, before committing to BiDi as the primary path. Record the result.
9. Add a profile-audit item: record which prefs the remote agent changes (including remote.prefs.recommended), and restore them if the tool is abandoned.
10. Add a security item: document that the BiDi socket has no auth, bind loopback only, decide whether the port stays open when idle, and prefer the allowlist model (zenpilot) or equivalent for the chosen tool.
11. Add a file-upload test item before any claim that DOM fixes uploads: test input.setFiles against the real Polygon file input, test the Browse button hover behavior under BiDi input.performActions, and record whether the native picker can be avoided or must still be driven by mouse. If it cannot, keep the mouse path for uploads and say so.
12. Add the hybrid item: DOM locates the element and returns its bounding box, the real mouse clicks it through the calibrated path. Test it against the Browse button specifically.
13. Expand 2.5.8 and 2.6.6 into real items, one per error (I28, I29, I30, I32 to I40), each with its own fix. Give I29 (cannot stop a delegated agent after a pause order) its own safety item.
14. Add a measurement item to Phase 2: define hit rate, define think-time logging format, define flicker-rate measurement, and require all three in every test from now on. Apply G14 to Phase 1 itself: the tool-choice tests must use held-out real tasks, not example.com and httpbin alone.
15. Split Phase 4: move pill blur to 2.2, move the speed loop and Track 2 to their own gated items with their resume conditions stated, and give each open user decision (4.6) an owner and a date.
16. Rewrite Phase 5 with a named real task, a hit-rate target, a wall-time target, a held-out problem set, and an independent checker who did not build the fix.
17. Correct H1 in the source error file: the flicker happened while Muse was driving directly, Codex driving was normal (I9). Add an item to fix the source file so the error record stops contradicting itself.
18. Flag the G24 to G27 numbering gap: check whether G25 and G26 exist or were lost, and record the answer.
19. Record versions: Zen 1.24.2b, Firefox 160.0, zen-mcp 1.2.3, zenpilot 0.7.0, and every tool version tested, in the todo list itself, with a re-test trigger on any Zen update.
20. Rename the goal honestly: "page-DOM control for Zen" plus "calibrated mouse path for everything DOM cannot reach". Do not let the plan imply DOM replaces computer-use.

## 9. What this review did not verify

- I did not run any BiDi tool myself, and I did not check the live BiDi port or the live Zen state. The test-results file is taken as reported, including its timings and its claim that Zen was running with the flags since 02:57.
- I did not verify the Puppeteer, Selenium, and firefox-mcp results, because none are recorded yet. Their absence is itself a finding, but it is not evidence they fail.
- I did not verify the zenpilot pref-mutation claim against the live profile, only against zenpilot's own documentation as returned by search.
- I did not verify whether navigator.webdriver is true under BiDi-only mode on this Zen build. The research file says it needs testing on the real machine, and this review agrees.
- I did not check whether the .desktop flags from 02:55 survive a reboot. Item 1.3.3 says to verify after reboot, and that verification has not been recorded anywhere I read.

## Sources used

- ~/workspace/zen-error-fix-todolist-20261121.md, read in full.
- ~/workspace/cf26-upload/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md, read in full (parts A to I, I1 to I46).
- ~/workspace/computer-use-wayland/improvements/muse-coordinate-accuracy-20261120.md, read in full.
- ~/workspace/firefox-automation-research-20261121.md, read in full.
- ~/workspace/zen-automation-test-results-20261121.md, read in full.
- ~/workspace/computer-use-wayland/improvements/speed-proto-pick4-summary.md, read in part (probe, Arm 1, Arm 2, G1 a11y grounding).
- Web search, 21/11/2026: Firefox WebDriver BiDi attach limits (cdp-toolkit commit 4cd3907, browxai RFC 01-webdriver-bidi-standards.md June 2026, gaze RESEARCH.md September 2026, bidi-lite docs); Mozilla firefox-mcp connect-existing requirements and the both-flags rule (github.com/mozilla/firefox-devtools-mcp); zen-devtools-mcp connect-existing limits; zenpilot 0.7.0 docs (PyPI, alpha status, remote.prefs.recommended, one session at a time, 2-minute idle release); claude-for-zen docs (RemoteAgent.startAtRuntime, experiment signing, session broker); Mozilla bug 2083461 (firefox-mcp upload_file_by_uid silent success, regression in 0.10.5, fix by migrating to input.setFiles); MDN input.setFiles reference; AT-SPI tooling (tine-cli, Touchpoint, bad-ass-mcp).
