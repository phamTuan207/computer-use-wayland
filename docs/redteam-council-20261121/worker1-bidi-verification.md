# Redteam Worker 1: Verification of Firefox automation research against live sources

- Worker: Redteam Worker 1
- Task: verify `~/workspace/firefox-automation-research-20261121.md` (29 KB, 447 lines, 19 sources, all accessed 21/11/2026) against live sources as of 21/11/2026
- Verification date: 21/11/2026
- Work log (Asia/Ho_Chi_Minh): started 03:32:51, searches 03:32-03:33, direct page reads (PyPI zenpilot, GitHub mozilla/firefox-mcp, pptr.dev/webdriver-bidi) 03:33, follow-up searches 03:33-03:34, report written 03:34. Total elapsed about 2 minutes of tool time. No blocker, no stuck period over 15 minutes.
- Method: `browser.search` and `browser.open` on official docs only where possible (Mozilla MDN and Firefox Source Docs, W3C, Playwright, Puppeteer pptr.dev, Selenium selenium.dev, GitHub, PyPI, Bugzilla). No live browser test was run, so no claim in this report is based on running code on the user's machine. Anything I could not find in a live source is marked UNVERIFIED, not assumed.
- Language note: no em dashes or en dashes are used in this file, only commas, periods and short hyphens, per the task rule.

## 0. Bottom line verdict

The core thesis of the prior report SURVIVES verification: Firefox removed CDP in Firefox 141, WebDriver BiDi is the replacement, Puppeteer can connect over BiDi, Selenium and geckodriver can connect to a running Firefox with `--marionette`, Mozilla firefox-mcp needs both flags, Playwright `connectOverCDP` is Chromium-only, and there is no way to attach a debug port to a Firefox or Zen that was started without the flags on the stable channel.

But the report is already stale in several places after only hours or days, and it has two wrong dates and one badly outdated version. The most important corrections:

1. zenpilot is NOT 0.2.1. Latest on PyPI is 0.7.0, published 18/11/2026. The report's version is five releases behind.
2. Firefox 129 was August 2024, not May 2024. Firefox 141 was released 22 July 2025, not June 2025.
3. Current versions moved since the report: Firefox 160.0.1 (17/11/2026), Zen 1.24.3b on Firefox 160.0.1 (18/11/2026), Playwright 1.65.1 (13/11/2026), Puppeteer 25.18.1 (17/11/2026, this one the report already had right), Selenium 4.53 (17/11/2026, report said 4.52).
4. The report's golden rule ("no attach to a running Firefox without restart") still holds on stable, but there is now an emerging Nightly-only experimental exception: dynamic start via `remote.experimental.dynamicstart.enabled` and the Remote Control panel, with container isolation landing in Firefox 160. This was not in the report and must be tracked, not assumed to work on Zen stable.
5. zenpilot's own limits are stricter than the report implies. BiDi in general can read cookies and run script, but zenpilot itself cannot run its own JavaScript and cannot touch cookies, passwords or downloads, and its default profile is a fresh logged-out `zenpilot` profile. The report blurred BiDi capability with zenpilot capability.
6. zen-mcp (sh6drack) is stale: v1.2.1, last commit 16/05/2026, no update in about 6 months.

## 1. Current versions as of 21/11/2026

| Component | Prior report said | Live source says on 21/11/2026 | Verdict |
|---|---|---|---|
| Firefox stable | 157-160, Nov 2026 | 160.0.1, first offered 17/11/2026. Firefox 160.0 was 10/11/2026. ESR 153.7.0 (10/11/2026) and ESR 115.45.0 | CONFIRMED, now precise |
| Firefox Beta / Nightly | not stated | Beta 161.0b5 (18/11/2026), Nightly 163.0a1 (19/11/2026) | New info |
| Zen Browser | 1.23.2b, Firefox 157 (via zenpilot test) | 1.24.3b, published 18/11/2026, on Firefox 160.0.1. 1.24.2b was on Firefox 159.0.1, 1.24b (28-29/10/2026) on Firefox 159.0 | OUTDATED in report |
| Playwright | 1.62 (cited via Firm86, 31/08/2026); 1.60 for moz-firefox | 1.65.1, published 13/11/2026 (1.65.0 on 05/11/2026). Bundled browsers: Chromium 159.0.8154.6, Firefox 159.0, WebKit 27.2 | OUTDATED in report |
| Puppeteer | 25.18.1 (pptr.dev), 25.16.0 with Firefox 158.0.1 | 25.18.1 (17/11/2026) is latest per pptr.dev changelog. 25.17.0 (10/11/2026) rolled to Firefox 159.0. 25.16.0 was 22/10/2026 | CONFIRMED for latest, Firefox roll claim OUTDATED by one release |
| Selenium | 4.52 latest, 4.29+ BiDi | 4.53.0 released 17/11/2026 (selenium.dev blog, 17/11/2026). 4.52.0 was 29/10/2026 | OUTDATED in report, by 4 days |
| W3C WebDriver BiDi spec | Working Draft snapshot 01/06/2026 | W3C standards page lists WebDriver BiDi as Draft Standard, 13/11/2026. Publication history shows Working Drafts on 13, 12, 11, 10, 9, 6, 3 Nov 2026 and 08/10/2026 | OUTDATED in report, spec is actively updated, status wording changed |
| geckodriver | not versioned in report | Not re-verified to a version number in this session (see UNVERIFIED list) | UNVERIFIED |

Sources: Firefox 160.0.1 release notes, https://www.firefox.com/en-US/firefox/160.0.1/releasenotes/ ; Wikipedia Firefox page, stable 160.0.1 on 17/11/2026, https://en.wikipedia.org/wiki/Firefox ; Playwright 1.65.1, https://www.gitwatchman.com/track/microsoft/playwright and https://dirtystatic.com/articles/playwright-1-65-bun-runner-browser-automation-updates/ ; Puppeteer changelog, https://pptr.dev/CHANGELOG ; Selenium 4.53 blog, https://www.selenium.dev/blog/2026/selenium-4-53-released/ ; W3C BiDi history, https://www.w3.org/standards/history/webdriver-bidi/ ; Zen 1.24.3b, https://www.linuxcompatible.org/story/zen-browser-1243b-release-security-fixes-chatgpt-crash-fixes/ and https://www.free-codecs.com/download/zen-browser.htm . All accessed 21/11/2026.

## 2. Claim by claim verification

### 2.1 Firefox removed CDP in Firefox 141, June 2025

Verdict: CONFIRMED in substance, WRONG month.

- MDN Firefox 141 release notes: "Removed the experimental CDP (Chrome DevTools Protocol) implementation from Firefox. With it we also removed the support for the `remote.active-protocols` preference." Bug 1882096. Source: https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/141
- Bugzilla bug 1882096: RESOLVED FIXED, 141 Branch. Source: https://bugzilla.mozilla.org/show_bug.cgi?id=1882096
- Firefox Source Docs, Remote protocol preferences: "`remote.active-protocols` ... With the end of the CDP support, WebDriver BiDi is the only available protocol, and the preference was removed in Firefox 141." Source: https://firefox-source-docs.mozilla.org/remote/Prefs.html
- Date correction: multiple secondary sources agree Firefox 141 was released 22 July 2025, not June 2025. The June date in the report confuses the development start (development on 141 started 26 May 2025, per bug 1882096 discussion) with the release date. Source for 22 July 2025: browxai RFC 01, https://github.com/kalebteccom/browxai/blob/HEAD/docs/rfcs/references/01-webdriver-bidi-standards.md , which cites fxdx.dev and MDN.
- The `/json/*` returning HTTP 404 claim was not re-tested live here, but it is consistent with the exzilcalanza article (verified live on Firefox Developer Edition 153) and with CDP removal. Mark as CONFIRMED via secondary source, not live-tested by me.

### 2.2 CDP deprecated in Firefox 129, May 2024

Verdict: CONFIRMED in substance, WRONG month.

- Correct date is August 2024. Firefox 129 was released 6 August 2024, and the production-ready BiDi announcement (Chrome blog, Matthias Rohmer) was 7 August 2024, covering Firefox 129 and Puppeteer 23. Source: browxai RFC 01 (same URL as above) and https://blog.crawlex.net/blog/webdriver-bidi-selenium/ , both accessed 21/11/2026.
- The report's table says "Firefox 129 (thang 5/2024)". May 2024 is wrong. This matters because the report elsewhere also says Puppeteer BiDi GA with Fx 129 (Aug 2024), which is the correct date, so the report contradicts itself on this point.

### 2.3 WebDriver BiDi is the replacement, present in current Firefox and Zen

Verdict: CONFIRMED.

- W3C WebDriver BiDi, editors James Graham (Mozilla), Alex Rudenko (Google), Maksim Sadym (Google), Browser Testing and Tools Working Group. Latest snapshot listed as Draft Standard 13/11/2026 (see section 1). Source: https://www.w3.org/standards/history/webdriver-bidi/
- Firefox Source Docs, Remote Protocols: "Firefox supports several remote protocols... Marionette, WebDriver BiDi." Source: https://firefox-source-docs.mozilla.org/remote/index.html
- Firefox 160 developer release notes list BiDi changes: machine-readable CDDL for all Firefox BiDi vendor extensions (`moz:` commands, events, parameters, capabilities, bug 2057588), `script.message` context fix (bug 2079905), Set-Cookie fix, network events performance change (bug 2075175), `script.evaluate` and `script.callFunction` no longer clearing user activation when called with `userActivation: false` (bug 2084107). Source: https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/160
- The report's claim that BiDi is the only two-way protocol in Firefox since CDP removal is consistent with all sources above.
- The report's list of BiDi gaps (WebAuthn virtual authenticators, accessibility tree, coverage and profiling, screencast, virtual time, deep device emulation) is consistent with browxai RFC 01 (June 2026) and with the Puppeteer BiDi unsupported list (see 2.5). No live source found in this session contradicts it, but I did not re-verify each gap individually against Firefox 160 source docs. Mark gaps as CONFIRMED via secondary sources, with that caveat.

### 2.4 Playwright cannot attach to a running Firefox or Zen, connectOverCDP is Chromium-only, moz-firefox is launch-only

Verdict: CONFIRMED, with two updates.

- Playwright official docs (via search results and the Playwright Ruby client mirror of the same API text): "Connecting over the Chrome DevTools Protocol is only supported for Chromium-based browsers." Source: https://playwright.dev/mcp/configuration/browser-extension (Connecting to Browsers page, lists only Chrome, Edge, Electron and cloud Chromium for CDP endpoint) and the BrowserType API text mirrored at https://github.com/YusukeIwaki/playwright-ruby-client/blob/HEAD/documentation/docs/api/browser_type.md
- Playwright `connect()` only attaches to a browser created by `launchServer`, not to a user-opened browser. This is consistent with the official docs text found in this session.
- moz-firefox channels: browxai RFC 02 (June 2026) confirms channel names `moz-firefox`, `moz-firefox-beta`, `moz-firefox-nightly`, driving stock Firefox over BiDi, exposed via Playwright MCP `--browser moz-firefox` in PR 41126, merged 08/06/2026, released in playwright-mcp v0.0.76. Source: https://github.com/kalebteccom/browxai/blob/HEAD/docs/rfcs/references/02-ecosystem-and-appium.md . No live source found in this session showing a Playwright attach-to-running-Firefox path. The report's "launch-only" conclusion still stands.
- Update 1: Playwright is now 1.65.1, not 1.62. The bundled Firefox in 1.65 is 159.0, not 150.0.2 (that was 1.60). The report's version anchor is stale.
- Update 2, NEW in Playwright: `browser.bind()` was added in v1.59 (per playwright.dev Browser API page, https://playwright.dev/docs/api/class-browser) and was highlighted in the November 2026 Playwright update. It makes a Playwright-launched browser available for playwright-cli, @playwright/mcp and other clients to connect to, via a named pipe or WebSocket endpoint. This does NOT change the attach conclusion: `bind()` binds a browser Playwright itself launched, it does not attach Playwright to a user-opened Zen. Do not cite `bind()` as a fix for the Zen attach problem. The report did not mention `bind()`, which is fine, but any follow-up work should not confuse the two.
- The report's claim that Playwright drives stock Firefox via Juggler with a patched build is consistent with secondary sources in this session (remote-browser.dev, The Testing Academy, both verified against Playwright 1.62). Note: one secondary source (remote-browser.dev, "CDP Firefox") incorrectly says Playwright Firefox uses Marionette under the hood. That is wrong. Playwright Firefox uses Juggler, its own protocol, not Marionette. The prior report got this right and the secondary source got it wrong.

### 2.5 Puppeteer CAN connect via webDriverBiDi, bug 1943416

Verdict: CONFIRMED, strongly. This is the best-evidenced claim in the report.

- Bugzilla bug 1943416, "Investigate Communicating with a Marionette session via BiDi", RESOLVED FIXED. The bug text includes the exact Puppeteer test the report cites, verbatim:
  ```
  var browser = await puppeteer.connect(
      {
          browserWSEndpoint: 'ws://127.0.0.1:9222/session',
          protocol: 'webDriverBiDi'
      }
  );
  var page = await browser.newPage();
  await page.goto('https://www.example.com')
  ```
  Source: https://bugzilla.mozilla.org/show_bug.cgi?id=1943416 , accessed 21/11/2026.
- Puppeteer official docs, pptr.dev/webdriver-bidi, version 25.18.1 (read directly 21/11/2026): "Puppeteer supports WebDriver BiDi automation with Chrome and Firefox. When launching Firefox with Puppeteer, the WebDriver BiDi Protocol is enabled by default. When launching Chrome, CDP is still used by default since not all CDP features are supported by WebDriver BiDi yet." Source: https://pptr.dev/webdriver-bidi
- The CDP error message is confirmed: puppeteer.guide, "Connecting to Firefox using CDP is no longer supported", created 21/05/2026, updated 16/09/2026. Fix shown is launch with `protocol: 'webDriverBiDi'` or connect to the BiDi endpoint with that protocol. Source: https://puppeteer.guide/errors/firefox-cdp-connection-unsupported/
- Independent third-party confirmation: TestingBot Puppeteer docs show `puppeteer.connect({browserWSEndpoint: ..., protocol: 'webDriverBiDi'})` for Firefox, with the note "Firefox has no CDP: Puppeteer drives it over WebDriver BiDi". Source: https://testingbot.com/support/web-automate/puppeteer
- Puppeteer BiDi unsupported list, read directly from pptr.dev on 21/11/2026, confirms and extends the report's gap list: no Accessibility, no Coverage, no Tracing, no `Page.createCDPSession()`, no drag and drop (`Input.drag`, `Input.dragAndDrop`, `Input.dragOver`, `Input.drop`), no `Page.screencast()`, no `Page.metrics()`, no `HTTPResponse.buffer()` / `text()` / `content()`, no `Page.emulateNetworkConditions()`, no `Page.setOfflineMode()`, various emulations missing. Fully supported: `Page.evaluate()`, locators, click and type, keyboard, mouse (except drag), screenshots (clip, encoding, fullPage only), PDF (limited params), request interception, `Page.cookies()`, `Page.setCookie()`, `Page.setGeolocation()`, `Page.setUserAgent()`. This is a correction to the report's shorter gap list: file upload via `ElementHandle.uploadFile` IS listed as fully supported over BiDi in Puppeteer, while the report (via zen-mcp) said no file upload. The difference is Puppeteer-level support versus BiDi-spec-level support versus a specific MCP server's limits. Do not conflate the three.
- Caveat: bug 1943416 proves connect works against a Marionette-started Firefox session with a BiDi endpoint at `ws://127.0.0.1:9222/session`. It does not by itself prove connect works against Zen specifically, or against a Zen started only with `--remote-debugging-port` and no `--marionette`. The report's Zen extrapolation is reasonable (Zen is a Firefox fork, same Remote Agent) but was not live-tested on Zen in this session. Mark Zen-specific connect as CONFIRMED in principle, UNVERIFIED by a live Zen run.

### 2.6 Selenium and geckodriver CAN connect via --connect-existing with --marionette

Verdict: CONFIRMED for the flag and the requirement, with a version update.

- Firefox Source Docs, geckodriver Flags, read via search 21/11/2026: "`--connect-existing`: Connect geckodriver to an existing Firefox instance. This means geckodriver will abstain from the default of starting a new Firefox session. The existing Firefox instance must have Marionette enabled. To enable the remote protocol in Firefox, you can pass the `--marionette` flag. Unless the `marionette.port` preference has been user-set, Marionette will listen on port 2828. So when using `--connect-existing` it is likely you will also have to use `--marionette-port` to set the correct port." Source: https://firefox-source-docs.mozilla.org/testing/geckodriver/Flags.html
- The same text is mirrored in the geckodriver README and in Appium geckodriver docs (which add that `appium:noReset` adds `--connect-existing`).
- Selenium version correction: latest is 4.53.0 (17/11/2026), not 4.52. Source: https://www.selenium.dev/blog/2026/selenium-4-53-released/
- Selenium 4.53 highlights: accessibility snapshots in Python and JavaScript (`driver.accessibility_snapshot()`, `getAccessibilitySnapshot()`), in both Classic and BiDi sessions, and a new Selenium MCP server (see section 4). Docker Selenium 4.53.0-20261120 ships Firefox 160.0.1.
- The report's claims "Selenium 4.29+ dropped CDP for Firefox" and "Selenium 4.50 removed old profile-extension methods" are consistent with sources found: Selenium blog (Feb 2025) via crawlex, and seleniumdecoded FAQ, https://seleniumdecoded.com/faq/ ("Firefox CDP support was removed in Selenium 4.29", "Selenium 4.50 removed the deprecated Firefox profile extension and certificate methods"). CONFIRMED via secondary sources.
- The report's claim "Selenium 4.35+ allows session reuse via session ID plus command executor URL" was NOT verified in this session. Mark UNVERIFIED. Do not rely on it without a direct source.

### 2.7 Mozilla firefox-mcp needs --marionette and --remote-debugging-port

Verdict: CONFIRMED, including the rename the report claimed.

- The GitHub URL https://github.com/mozilla/firefox-devtools-mcp now resolves to mozilla/firefox-mcp. The page title on 20/11/2026 crawl is "GitHub - mozilla/firefox-mcp". README says: "Repository: https://github.com/mozilla/firefox-mcp. Also published as `@mozilla/firefox-devtools-mcp` for existing setups." and "Use `npx @mozilla/firefox-mcp@latest`". So the report's rename claim is CORRECT, and the old name still works as an alias. Source: https://github.com/mozilla/firefox-mcp , read directly 21/11/2026.
- Repo metadata on that page matches the report exactly: 589 stars, 440 commits, 45 releases, created 2025-10-08. This suggests the report's crawl (20/11/2026 19:19 UTC) is still current.
- Connect-existing, read directly from the README on 21/11/2026:
  ```
  firefox --marionette --remote-debugging-port
  npx @mozilla/firefox-mcp --connect-existing --marionette-port 2828
  ```
  "Both flags are required because the MCP uses both WebDriver Classic (`--marionette`) and WebDriver BiDi (`--remote-debugging-port`). If Firefox is only started with `--marionette`, the MCP server fails to connect and asks you to restart Firefox with both flags."
  "If Firefox is already running with the same profile, the command above only opens a new window in that instance: the flags are ignored, so neither Marionette nor the Remote Agent starts."
  Dedicated profile workaround is documented with `firefox -CreateProfile firefox-mcp` then `firefox -P firefox-mcp --marionette --remote-debugging-port`.
  Warning: "Do not leave Marionette enabled during normal browsing. It sets `navigator.webdriver = true` and changes other browser fingerprint signals, which can trigger bot detection on sites protected by Cloudflare, Akamai, etc."
  Idle timeout: `--idle-timeout`, default 1800 seconds, "Firefox accepts one client at a time, so other clients can only connect once it is released."
- All of the above CONFIRMS the report's section 4.4 word for word in substance. The report's npm command `npx @mozilla/firefox-mcp --connect-existing` is correct under the new name; the old name `npx @mozilla/firefox-devtools-mcp` also still works per the README.
- New detail not in the report: the README now documents Firefox for Android mode (`--android-device`, wipes app data), `--tool-preset` values slim / basic (default) / developer / mozilla / all, and that the `bidi`, `prefs`, `privileged` and `launch` modules require the Mozilla-internal build and are skipped in the public package. The report's tool list (list_pages, select_page, navigate_page, take_snapshot, click_by_uid, fill_by_uid, evaluate_script, list_network_requests, list_console_messages, screenshot_page, list_downloads, set_download_behavior) is consistent with the README's "Try it with MCP Inspector" section.

### 2.8 zenpilot and zen-mcp

Verdict: PARTLY CONFIRMED, MAJOR VERSION ERROR for zenpilot, STALE for zen-mcp.

zenpilot:
- Latest on PyPI is 0.7.0, uploaded 18/11/2026 (63.8 kB sdist, 68.8 kB wheel). Source: https://pypi.org/project/zenpilot/ , read directly 21/11/2026 (page crawled 20/11/2026 20:33 UTC).
- Release history found in search: 0.2.0 (16/10/2026), 0.2.1 (cited in report, no date confirmed here), 0.5.0 (28/10/2026), 0.5.1 (28/10/2026), 0.6.0 (08/11/2026), 0.7.0 (18/11/2026). The report's "PyPI 0.2.1" is five releases behind and three weeks old. OUTDATED.
- Core mechanism CONFIRMED: "It talks to Zen over WebDriver BiDi, which Firefox (and so Zen) exposes when started with `--remote-debugging-port`. There is no browser extension, HTTP server or native messaging host." One BiDi session at a time, released after 2 minutes idle. Source: same PyPI page.
- Linux support, CORRECTION to the report: the current PyPI text says "Alpha. Built and tested on macOS with Zen 1.23. Linux support is newer: it's been tried on NixOS (Wayland) with Zen 1.23." and "You need a Mac with Zen in `/Applications`, or Linux with Zen installed (on `PATH`, in `/opt/zen`, `~/.local/share/zen` or as the Flatpak)." The report said "currently only tested on macOS, need to test on Linux/Omarchy". That was true for 0.2.1, but 0.7.0 has at least been tried on NixOS Wayland. Linux is still newer and less tested, and Omarchy specifically is still untested as far as any source I found shows. Mark as PARTLY OUTDATED.
- zenpilot limits, CORRECTION to the report's implication: the current PyPI text says "It can attach files to upload, but only from folders you list in `upload_dirs`. It can't touch cookies, passwords or downloads, and it can't run its own JavaScript." The report said "BiDi can read cookies and run script in your logged-in sites" in the zenpilot paragraph. That is true of BiDi as a protocol, not of zenpilot as a product. zenpilot deliberately does not expose script execution or cookie access. Do not promise those via zenpilot.
- zenpilot default profile, CORRECTION: "Which profile? `zenpilot` is a fresh profile that isn't logged in to anything. Pick your own profile if you want Claude to use sites you're logged into." and "Reopen Zen? If Zen is already open without remote control, zenpilot offers to restart it." The report did not mention the fresh-profile default. This matters for the user's goal: zenpilot out of the box does NOT drive the logged-in daily profile unless the user picks it in setup.
- zenpilot allowlist: Claude only works on sites the user allows, with Don't Allow / Allow for 12 Hours / Always Allow. Remote control is open while Zen runs this way, other local apps could connect too, some sites may treat the session as a bot. Source: same PyPI page.

zen-mcp (sh6drack):
- v1.2.1, 20 tools, WebDriver BiDi over WebSocket, no Selenium or Playwright. Last commit 16/05/2026. Multiple directories list it as updated 6 months ago, stars 27-28, forks 6. Source: https://mcpdirectory.fyi/us/global/online/zen-mcp and https://mcpskull.com/browser-automation/zen , accessed 21/11/2026.
- The report gave no version and no freshness date for zen-mcp. Verdict: the project appears STALE, no release in about 6 months. It still works in principle (BiDi protocol has not changed incompatibly), but do not present it as actively maintained. Its "no file upload / drag-and-drop" limit is consistent with the BiDi spec gap, not a zen-mcp bug.
- Note name collision: there is a separate `@spaxe-dev/zen-mcp` (0.5.0, 01/11/2026, "agent harness for Zen Browser") and a separate "zen-mcp" that is a Docker-first Playwright MCP server. These are NOT sh6drack/zen-mcp. The report did not distinguish them. Mark as a naming hazard for follow-up work.

zen-devtools-mcp (simon-ami fork, mentioned in the report):
- UNVERIFIED in this session. I did not open its repo or Glama page directly, and no search result in this session gave its current version or last update. Do not cite it as current without a fresh check.

### 2.9 WebExtension plus native messaging, Inari MCP, mcp-browser-bridge

Verdict: CONFIRMED for Inari, PARTLY VERIFIED for the rest.

- Inari MCP for Firefox: listed on addons.mozilla.org since 14/10/2026, numbered from 0.1.0, Firefox 142 or later, extension plus native host plus MCP server, fork of ClaudeCodeBrowser, approval for every action, no script execution, no logging. Source: https://glama.ai/mcp/servers/elys0912/InariMCP and https://addons.mozilla.org/en-US/firefox/addon/inari-mcp-for-firefox/ , accessed 21/11/2026. The AMO page references a privacy policy at `InariMCP/blob/v0.2.0/docs/PRIVACY.md`, which implies a 0.2.0 exists, newer than the 0.1.0 the report cited. Mark version as PARTLY OUTDATED, mechanism as CONFIRMED.
- The report's claim "Zen accepts the unsigned zip locally" was NOT re-verified in this session. Mark UNVERIFIED. Do not rely on it for a Zen install plan without a live test.
- mcp-browser-bridge and Claudezilla: not re-checked in this session. Mark UNVERIFIED for current status.

### 2.10 The golden rule: no attach to a running Firefox without restart

Verdict: CONFIRMED for stable and release, with an emerging Nightly exception (see section 4).

- cdp-toolkit commit 4cd3907, quoted in the report: "Firefox is launched, never attached to... verified against Firefox 153.0.3" and "relaunching the binary against a running instance hands off and exits silently, opening no port". This commit text was found again in search on 21/11/2026. Source: https://github.com/sblattj/cdp-toolkit/commit/4cd3907cd8fd770c5c638eead91b3cf26676fd4d
- Mozilla firefox-mcp README (see 2.7) confirms the same handoff behavior for the same profile.
- Bugzilla bug 1754738 (closed WONTFIX) confirms the design: remote protocols require a command line argument at startup, "When that's not done the appropriate components won't be enabled at all." Source: https://bugzilla.mozilla.org/1754738
- Exception: see section 4, dynamic start on Nightly. The golden rule needs a Nightly footnote now, it is no longer unconditional across all channels.

### 2.11 Other dated claims in the report

- "Firefox 145 (2026) added `emulation.setUserAgentOverride`, `browsingContext.downloadEnd`": UNVERIFIED in this session. I did not open the Firefox 145 release notes. Do not cite without checking.
- "Firefox 160.0 release ~10/11/2026": CONFIRMED, 10/11/2026 for 160.0, 17/11/2026 for 160.0.1.
- "Safari has no BiDi as of Safari 27 beta, 08/06/2026": NOT re-verified in this session. Selenium 4.47 notes say Safari BiDi support is in Technology Preview since 4.47, and irurueta (Oct 2026) says Safari gained BiDi in the Ruby binding for Safari Technology Preview in 4.47. The report's Safari claim may be outdated. Mark UNVERIFIED, likely stale.
- "One BiDi session at a time": CONFIRMED via firefox-mcp README (idle timeout 1800s, "Firefox accepts one client at a time") and zenpilot PyPI (one session, release after 2 minutes idle).
- "WebDriver Classic and BiDi refuse navigate to `moz-extension://` and `about:` pages": UNVERIFIED in this session. I did not find a direct source for this in the searches run. Do not treat as verified.
- "`navigator.webdriver` is true when a Marionette/BiDi session is active": PARTLY VERIFIED. firefox-mcp README confirms it for Marionette ("It sets `navigator.webdriver = true`"). The BiDi-only case (no Marionette, only `--remote-debugging-port`) was NOT separately verified in this session. The report itself flagged this as needing a live test on Zen. That flag still stands.
- "Zen does not create a new window via BiDi, tab opens in current window": UNVERIFIED in this session.
- "firefox-cdp, ~700 lines Python, MIT, 19 unit tests": CONFIRMED in substance via exzilcalanza.info, https://exzilcalanza.info/firefox-cdp-webdriver-bidi/ , which says "~700-line Python adapter", MIT, github.com/Zek21/firefox-cdp. The "19 unit tests" count was not re-verified. Mark that count UNVERIFIED.

## 3. Community signals cited in the report, re-checked

- vercel-labs/agent-browser PR 2227 (26/10/2026, "feat(firefox): attach to a running Firefox over WebDriver BiDi") and PR 2205 (23/10/2026, launch Firefox over BiDi): PARTLY VERIFIED. GitHub contribution activity for November 2026 lists "feat(firefox): attach to a running Firefox over WebDriver BiDi" among 10 merged PRs in vercel-labs/agent-browser, plus launch, snapshots, dashboard and network control PRs. Source: https://github.com/ctate (contribution activity). I did NOT open PR 2227 itself in this session, so the PR number 2227 and the 26/10/2026 date are UNVERIFIED by direct read. The feature itself (attach to running Firefox over BiDi) is confirmed as merged work in November 2026.
- developing-today/code PR 6146 and dezren39/darwin-nix PR 1515 (05/11/2026): NOT re-checked in this session. UNVERIFIED.
- w3c/webdriver-bidi issue 1188 (28/10/2026, "Authenticate WebDriver BiDi client connections"): NOT found in the searches run in this session. The search for issue 1188 returned unrelated Bugzilla and W3C results, not the issue itself. Mark UNVERIFIED for current status. The security concern itself (any local process can connect to the BiDi WebSocket, loopback only, no auth) is consistent with all BiDi sources and with the firefox-mcp and zenpilot warnings, but the issue number and date were not confirmed here.
- aresstack/playwright4j PRs (24-25/10/2026): NOT re-checked. UNVERIFIED.
- phnx-labs/agi-cli, a NEW signal not in the report: "feat(browser): drive Firefox over WebDriver BiDi with native profile", which says "Firefox 129+ dropped CDP" and "agents launch it headless with a debug port (or attach to a running one, failing loud when a portless Firefox already holds the profile)". Note: this commit text itself says "Firefox 129 removed the Chrome DevTools Protocol", which is wrong in the same way as the report's May date confusion. CDP was deprecated in 129, removed in 141. This is a reminder that secondary sources repeat the 129/141 confusion. Source: https://github.com/phnx-labs/agi-cli/commit/887363950e8820e5aba4767190f0ab09157884d9

## 4. NEW developments since the report (21/11/2026)

These were not in the prior report, or were only hinted at. All accessed 21/11/2026.

### 4.1 Firefox Nightly dynamic start, the most important new item

- A fork README (Majdoddin/firefox-devtools-mcp) states: "The flags are one way to get both listening: a Nightly where both were switched on at runtime from its Remote Control panel (experimental, shown once the pref `remote.experimental.dynamicstart.enabled` is true) connects the same way." Source: https://github.com/Majdoddin/firefox-devtools-mcp
- Mozilla Bugzilla bug 2081128, fixed in Firefox 160, is about BiDi sessions restricted to a dedicated container (`remote-control-container`), behind the hidden pref `remote.experimental.dynamicstart.container-isolation-enabled`. It says "Bug 2072964 restricts WebDriver BiDi sessions to the dedicated container". Source: https://bugzilla.mozilla.org/show_bug.cgi?id=2081128
- Implication: Mozilla is building a path to start BiDi at runtime, without relaunch, but it is experimental, Nightly-only as far as any source here shows, and container-isolated (the session is restricted to a dedicated user context, and `browser.createUserContext`, `browser.removeUserContext` and `browser.close` are rejected for such sessions). This does NOT yet overturn the golden rule for Zen stable. It is the single most important thing to live-test next, on Firefox Nightly, not on the user's daily Zen.
- Related: Firefox Enterprise 160.0 release notes say "DisableDeveloperTools can now disable remote automation (WebDriver BiDi and Marionette) without a restart." Source: https://www-dev.springfield.moz.works/en-US/firefox/enterprise/160.0/releasenotes/ . That is the reverse direction (disabling without restart), but it shows Mozilla is actively changing the restart assumptions around remote automation in Firefox 160.

### 4.2 Selenium MCP server, new official project

- Selenium 4.53 (17/11/2026) started an official MCP server for coding agents, now in its own repo SeleniumHQ/mcp, npm `@selenium/mcp`. Source: https://www.selenium.dev/blog/2026/selenium-4-53-released/ and https://github.com/SeleniumHQ/selenium/releases
- Status: v0/v1 in progress, Chrome headless by default over stdio, one browser per server, depends on `getAccessibilitySnapshot()` which first ships in selenium-webdriver 4.53.0. It is Chrome-first in its current docs, not Firefox-first. Do not present it as a Firefox or Zen solution yet. It is relevant as a new official MCP path to watch, and as a possible future BiDi client.

### 4.3 zenpilot 0.7.0, with Linux support

- See 2.8. 0.7.0 on 18/11/2026, Linux tried on NixOS Wayland. The report's "test on Linux" gap is now partly closed, but Omarchy is still untested in any source found.

### 4.4 New Firefox and Zen extension MCP servers (not in the report)

These all use the WebExtension plus native messaging pattern, which is the report's "no restart" path. They are new or newly visible since the report's sources, and they change the "which extension MCP to try" choice:

- FoxMCP (ThinkerYzu/foxmcp), v1.7.0 on PyPI and GitHub, extension plus Python server, `uvx foxmcp --stdio`, works in the user's real Firefox with tabs, logins, bookmarks, history and containers. AMO serves 1.6.0 while 1.7.0 awaits review. Last commit 4 days before the MCPpedia check. Source: https://mcppedia.org/s/io-github-thinkeryzu-foxmcp
- Foxhand (hamb1y, formerly WebMCP Controller), v0.5.9, extension plus native messaging helper, MCP on localhost, install via a one-line shell or PowerShell script. Source: https://glama.ai/mcp/servers/hamb1y/foxhand
- FF MCP Bridge, AMO v1.0.2, updated 15/11/2026, "Lets an AI agent control Firefox through a local MCP server (tabs, DOM, input, JS, storage, cookies, console, network)". Source: https://addons.mozilla.org/en-US/firefox/addon/ff-mcp-bridge/
- Agent Browse (store name for "browse for Firefox", sankalpmukim/browse-for-firefox), extension plus local relay over native messaging, no network port, MIT. Source: https://addons.mozilla.org/en-US/firefox/addon/agent-browse/
- Browser for AI Agent, AMO, extension plus native messaging host, supports WebMCP page-provided tools. Source: https://addons.mozilla.org/en-US/firefox/addon/browser-for-ai-agent/
- None of these were live-tested here. They are listed as candidates to evaluate, not as verified recommendations. Their Zen compatibility specifically (versus Firefox) was not verified in this session.

### 4.5 Other new tools

- navigera changelog: "`--attach firefox` (experimental): a running Firefox started with `firefox --remote-debugging-port` is worked in over WebDriver BiDi and left running. navigera finds it by the file its remote agent keeps in the profile (`WebDriverBiDiServer.json`), then on port 9222". Also BiDi `route` and `unroute` (experimental). Source: https://andrey-usa.github.io/navigera/project/changelog.html
- Lightpanda, 19/11/2026: a headless browser written in Zig for AI agents, exposes a CDP server, WebDriver BiDi and a native MCP server. Not Firefox, but a new BiDi-speaking browser to watch. Source: https://gtmstacker.com/registry/
- Majdoddin/firefox-devtools-mcp fork, the `__ffllm` kit: privileged primitives to discover, introspect and hot-patch a running Firefox, chrome and content processes, no rebuild, no restart, submitted as bug 2062803, developed against Firefox Nightly 155. This is a fork, not upstream, and the published npm packages do not carry the kit. Source: https://github.com/Majdoddin/firefox-devtools-mcp
- agent-browser (Vercel Labs) Firefox attach work, see section 3. The project itself was released publicly around 08/11/2026 and gained about 53k stars by mid-November. Its Firefox support is BiDi-based and includes attach to a running Firefox. This is a credible new CLI-first option for the user's goal, alongside Puppeteer.

## 5. Errors and stale items in the prior report, consolidated

| # | Prior report claim | Correction | Severity |
|---|---|---|---|
| 1 | Firefox 129, May 2024 | August 2024 (6 Aug 2024 release, 7 Aug 2024 BiDi GA announcement) | Date error, medium. The report contradicts itself, elsewhere saying Aug 2024 correctly. |
| 2 | Firefox 141, June 2025 | 22 July 2025 | Date error, medium. June was dev start, not release. |
| 3 | zenpilot PyPI 0.2.1, Zen 1.23.2b, Firefox 157, macOS only | 0.7.0 on 18/11/2026, Linux tried on NixOS Wayland, Zen now 1.24.3b on Firefox 160.0.1 | Version error, high. Five releases behind. |
| 4 | Playwright 1.62 current | 1.65.1 on 13/11/2026, bundled Firefox 159.0 | Stale, medium. |
| 5 | Puppeteer 25.16.0 with Firefox 158.0.1 | 25.18.1 latest (report had this right elsewhere), 25.17.0 rolled Firefox 159.0 | Stale, low. Latest version itself was correct. |
| 6 | Selenium 4.52 latest | 4.53.0 on 17/11/2026 | Stale, medium. 4 days out of date at verification time. |
| 7 | W3C BiDi snapshot 01/06/2026 | Draft Standard 13/11/2026, with Working Drafts published on 13, 12, 11, 10, 9, 6, 3 Nov 2026 | Stale, low. Spec is actively updated. |
| 8 | Firefox current 157-160 | 160.0.1 (17/11/2026), Zen 1.24.3b on 160.0.1 (18/11/2026) | Stale, low. Range was right, precision was missing. |
| 9 | zenpilot paragraph implies cookies and script via zenpilot | zenpilot cannot run its own JavaScript, cannot touch cookies, passwords or downloads, default profile is fresh and logged out | Misleading, high. BiDi capability was blurred with zenpilot capability. |
| 10 | No mention of Nightly dynamic start | Experimental dynamic start exists on Nightly (`remote.experimental.dynamicstart.enabled`), container-isolated in Firefox 160 | Missing development, high for future work. Golden rule needs a Nightly footnote. |
| 11 | No mention of Selenium MCP, new extension MCPs, navigera Firefox attach, agent-browser Firefox attach as merged | See section 4. All are November 2026 developments | Missing developments, medium. |
| 12 | zen-mcp presented without version or freshness | sh6drack/zen-mcp v1.2.1, last commit 16/05/2026, stale about 6 months | Missing freshness, medium. |
| 13 | Firefox 145 BiDi additions, Selenium 4.35 session reuse, Zen no-new-window, `about:` navigate refusal, BiDi-only `navigator.webdriver`, Safari no BiDi | None verified in this session (see UNVERIFIED list) | Unverified, low to medium. Do not cite as verified. |

## 6. UNVERIFIED list (could not confirm in this session, do not cite as verified)

- zen-devtools-mcp (simon-ami fork): current version, last update, whether it still works.
- mcp-browser-bridge (Drima-code) and Claudezilla: current status.
- Report claim: Firefox 145 added `emulation.setUserAgentOverride` and `browsingContext.downloadEnd`.
- Report claim: Selenium 4.35+ session reuse via session ID plus command executor URL.
- Report claim: Zen does not create a new window via BiDi, new tab opens in current window.
- Report claim: WebDriver Classic and BiDi refuse navigate to `moz-extension://` and `about:` pages.
- Report claim: `navigator.webdriver` is true in BiDi-only mode (no Marionette). Confirmed for Marionette, not separately for BiDi-only.
- Report claim: Zen accepts unsigned extension zip locally.
- Report claim: "Zen 1.23.2b = Firefox 157" as a zenpilot test target. The 1.23.2b number itself was not confirmed against Zen release notes here, only the PyPI text "Tested on macOS with Zen 1.23.2b (Firefox 157)" in an older PyPI snapshot.
- w3c/webdriver-bidi issue 1188 (28/10/2026): existence, number and current status.
- vercel-labs/agent-browser PR number 2227 and date 26/10/2026: the attach feature is confirmed as merged November 2026 work, the PR number and date were not opened directly.
- developing-today/code PR 6146, dezren39/darwin-nix PR 1515, aresstack/playwright4j PRs: not re-checked.
- Safari BiDi status as of November 2026: the report's "no BiDi as of Safari 27 beta" may be stale given Selenium 4.47 Safari Technology Preview BiDi notes.
- geckodriver latest version number.
- Any claim that requires running code on Zen on the user's machine (Puppeteer connect to Zen, firefox-mcp connect to Zen, zenpilot on Omarchy Linux). All Zen-specific attach claims are reasonable extrapolations from Firefox, not live Zen tests.

## 7. What still stands for the user's goal

The actionable conclusion of the prior report is unchanged by this verification:

- The fastest path is still Puppeteer `connect()` over BiDi to a Zen started with `--remote-debugging-port`, as proven by Mozilla bug 1943416 and documented at pptr.dev. That is the lightest client, no driver binary needed.
- The ready-made MCP path is still Mozilla firefox-mcp with `--connect-existing`, requiring both `--marionette` and `--remote-debugging-port`, with the dedicated-profile workaround for daily browsing. The rename to `@mozilla/firefox-mcp` is confirmed, and the old name still works.
- The no-restart path is still WebExtension plus native messaging (Inari confirmed on AMO, plus the new FoxMCP, Foxhand, FF MCP Bridge and Agent Browse candidates in section 4.4). This is the only path that works on a Zen that is already running without flags.
- Playwright still cannot attach to a running Zen. `browser.bind()` does not change this.
- The next test to run, before any build decision, is the Nightly dynamic-start experiment (section 4.1). If it works on Nightly, it may eventually remove the restart requirement on stable, but it is not a stable-channel solution today.

## 8. Sources

All accessed 21/11/2026, unless a crawl date is noted in the text.

1. MDN, Firefox 141 release notes: https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/141
2. Bugzilla bug 1882096 (Remove CDP support): https://bugzilla.mozilla.org/show_bug.cgi?id=1882096
3. Firefox Source Docs, Remote protocol preferences: https://firefox-source-docs.mozilla.org/remote/Prefs.html
4. Firefox Source Docs, Remote Protocols index: https://firefox-source-docs.mozilla.org/remote/index.html
5. Firefox Source Docs, geckodriver Flags: https://firefox-source-docs.mozilla.org/testing/geckodriver/Flags.html
6. MDN, Firefox 160 release notes: https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/160
7. Firefox 160.0.1 release notes: https://www.firefox.com/en-US/firefox/160.0.1/releasenotes/
8. Wikipedia, Firefox (stable 160.0.1, 17/11/2026): https://en.wikipedia.org/wiki/Firefox
9. W3C, WebDriver BiDi publication history: https://www.w3.org/standards/history/webdriver-bidi/
10. browxai RFC 01, WebDriver BiDi standards (June 2026): https://github.com/kalebteccom/browxai/blob/HEAD/docs/rfcs/references/01-webdriver-bidi-standards.md
11. browxai RFC 02, ecosystem and Appium (June 2026): https://github.com/kalebteccom/browxai/blob/HEAD/docs/rfcs/references/02-ecosystem-and-appium.md
12. exzilcalanza.info, Driving Firefox Without CDP: https://exzilcalanza.info/firefox-cdp-webdriver-bidi/
13. Bugzilla bug 1943416 (Marionette session via BiDi, Puppeteer connect): https://bugzilla.mozilla.org/show_bug.cgi?id=1943416
14. Puppeteer, WebDriver BiDi support, v25.18.1: https://pptr.dev/webdriver-bidi
15. Puppeteer changelog: https://pptr.dev/CHANGELOG
16. puppeteer.guide, Connecting to Firefox using CDP is no longer supported: https://puppeteer.guide/errors/firefox-cdp-connection-unsupported/
17. TestingBot, Puppeteer Testing in the Cloud: https://testingbot.com/support/web-automate/puppeteer
18. Playwright, Browser API (browser.bind, added v1.59): https://playwright.dev/docs/api/class-browser
19. Playwright, Connecting to Browsers: https://playwright.dev/mcp/configuration/browser-extension
20. Playwright 1.65.1 release notes (via GitWatchman): https://www.gitwatchman.com/track/microsoft/playwright
21. Playwright 1.65 overview: https://dirtystatic.com/articles/playwright-1-65-bun-runner-browser-automation-updates/
22. Selenium 4.53 released: https://www.selenium.dev/blog/2026/selenium-4-53-released/
23. Selenium decoded FAQ (4.52, 4.29 CDP removal, 4.50 profile methods): https://seleniumdecoded.com/faq/
24. irurueta, Selenium WebDriver BiDi (4.51.0, Oct 2026): https://www.irurueta.com/web/e2e-testing/selenium/webdriver-bidi.html
25. GitHub, mozilla/firefox-mcp (formerly firefox-devtools-mcp): https://github.com/mozilla/firefox-mcp
26. PyPI, zenpilot 0.7.0: https://pypi.org/project/zenpilot/
27. MCP Directory, sh6drack/zen-mcp v1.2.1: https://mcpdirectory.fyi/us/global/online/zen-mcp
28. Glama, Inari MCP for Firefox: https://glama.ai/mcp/servers/elys0912/InariMCP
29. AMO, Inari MCP for Firefox: https://addons.mozilla.org/en-US/firefox/addon/inari-mcp-for-firefox/
30. AMO, FF MCP Bridge: https://addons.mozilla.org/en-US/firefox/addon/ff-mcp-bridge/
31. AMO, Agent Browse: https://addons.mozilla.org/en-US/firefox/addon/agent-browse/
32. Glama, Foxhand: https://glama.ai/mcp/servers/hamb1y/foxhand
33. MCPpedia, FoxMCP: https://mcppedia.org/s/io-github-thinkeryzu-foxmcp
34. navigera changelog (attach firefox): https://andrey-usa.github.io/navigera/project/changelog.html
35. cdp-toolkit commit 4cd3907 (Firefox launched, never attached): https://github.com/sblattj/cdp-toolkit/commit/4cd3907cd8fd770c5c638eead91b3cf26676fd4d
36. Bugzilla bug 2081128 (BiDi container restriction, Firefox 160): https://bugzilla.mozilla.org/show_bug.cgi?id=2081128
37. Bugzilla bug 1754738 (WebDriver components in release builds, WONTFIX): https://bugzilla.mozilla.org/1754738
38. GitHub, Majdoddin/firefox-devtools-mcp (__ffllm kit, dynamic start note): https://github.com/Majdoddin/firefox-devtools-mcp
39. Firefox Enterprise 160.0 release notes: https://www-dev.springfield.moz.works/en-US/firefox/enterprise/160.0/releasenotes/
40. crawlex blog, Selenium BiDi migration (Firefox 129, 7 Aug 2024): https://blog.crawlex.net/blog/webdriver-bidi-selenium/
41. Zen 1.24.3b release: https://www.linuxcompatible.org/story/zen-browser-1243b-release-security-fixes-chatgpt-crash-fixes/
42. phnx-labs/agi-cli, Firefox BiDi commit: https://github.com/phnx-labs/agi-cli/commit/887363950e8820e5aba4767190f0ab09157884d9
