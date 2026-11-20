# Zen automation test results - 21/11/2026

Coordinator log. Wall-clock Asia/Ho_Chi_Minh. Task: test which tools can control the
running Zen browser via DOM (not screenshots/mouse), which work, which are broken,
and whether anything needs to be built ourselves.

## Setup log

- 02:56 +07: Task received. Zen BiDi port 9222 NOT up (curl EXIT 7, connection refused).
  Zen was running since 02:18 (before the .desktop flags were added at ~02:55).
  Chromium port 9223 also not up (Chromium not running).
- 02:57 +07: Killed Zen (TERM then KILL). First relaunch attempt died with the SSH
  session (no DISPLAY env in SSH session).
- 02:58 +07: Relaunched Zen with stolen Wayland env
  (XDG_RUNTIME_DIR=/run/user/1000, WAYLAND_DISPLAY=wayland-1,
  HYPRLAND_INSTANCE_SIGNATURE from /run/user/1000/hypr/).
- 02:59 +07: BiDi server UP. curl http://127.0.0.1:9222/json/version returns HTTP 404
  (EXPECTED for Firefox: no CDP, BiDi HTTP server is listening).
  WebDriverBiDiServer.json exists:
  /home/james/.config/zen/ae59l0ak.Default (release)/WebDriverBiDiServer.json
  with {"ws_host": "127.0.0.1", "ws_port": 9222}.
  BiDi WebSocket endpoint: ws://127.0.0.1:9222/session.
- 03:00 +07: Tailscale on VM dropped ("stopped sending network configuration.
  Reconnecting") for ~2 min. SSH failed with exit 255. Recovered ~03:02 +07,
  tailscale status Connected, SSH OK. Zen still running (11 zen-bin processes),
  BiDi port still 404 (up).
- 03:03 +07: Node v26.13.1, npm 11.20.0, Python 3.14.10 on laptop. No puppeteer
  cache yet. Global npm: eas-cli, npm only.
- 03:04 +07: Fanned out 5 parallel workers (one per tool):
  - A: Puppeteer via BiDi
  - B: Selenium + geckodriver
  - C: Mozilla firefox-mcp
  - D: zenpilot/zen-mcp
  - E: Playwright moz-firefox (confirm cannot attach)

## Muse direct testing log (03:24 +07 onwards)

### 03:24:29 +07 - Muse starts direct testing (user order: Muse tests, not Codex)
- User: Muse must proactively test, Codex only fixes errors in the error file.
- User: Muse's errors take priority (sections G, H, I). First principles thinking.
- User: breakthrough mindset, ready to rewrite whole repo if needed.
- User: start testing, measuring, logging everything with all agents including Muse.
- Zen still running with --remote-debugging-port=9222 --marionette (PID 28990, since 02:57).
- BiDi HTTP server responds on port 9222.
- Clone1 already delivered on GitHub (commit 1ef0816): Puppeteer BiDi test, firefox-mcp research, WebExtension bridge prototype, DOM control comparison.
- Coordinator b72f1f5a running (Codex fixing errors, opencode testing zenpilot, fcc testing Playwright).
- Watchdog cron watchdog-zen-20m active, checks every 20 min, reports directly to Muse.
- Clone1 and clone2 work on their own machines only, no SSH to laptop. They submit via GitHub, Muse runs their code on the laptop.
  - B: Selenium + geckodriver (--connect-existing)
  - C: Mozilla firefox-mcp (--connect-existing)
  - D: zenpilot / zen-mcp
  - E: Playwright moz-firefox channel (confirm cannot attach)

## Worker results

(pending - filled in as workers report back)

## Worker C - Playwright moz-firefox (fcc)

Tested 03:19-03:25 +07, 21/11/2026. Method note: ran directly via SSH exec as james on the laptop (not via fcc), same commands, same account. Playwright 1.65.1, Node v26.13.1, npm 11.20.0. Test dir on laptop: /tmp/pw-moz-c (scripts test-attach.js, test-launch.js, test-launch2.js, test-juggler.js, test-final.js plus logs). Zen binary /opt/zen-browser-bin/zen-bin, running Zen main PID 28990 with --remote-debugging-port=9222 --marionette, BiDi endpoint ws://127.0.0.1:9222/session. No existing Zen tab was ever touched: every test instance used a fresh temp profile, and main Zen PID 28990 was alive with BiDi still up (HTTP 404 on /json/version, expected) before and after every test.

### 1. Attach to the RUNNING Zen: FAILED on all three Playwright paths

- 1a, 03:21:29 +07, chromium.connectOverCDP("http://127.0.0.1:9222"): FAILED in 13 ms. Exact error: "browserType.connectOverCDP: Unexpected status 404 when connecting to http://127.0.0.1:9222/json/version/. This does not look like a DevTools server, try connecting via ws://."
- 1b, 03:21:29 +07, firefox.connect({ wsEndpoint: "ws://127.0.0.1:9222/session", timeout: 15000 }): FAILED, timeout after 15,022 ms. Exact error: "browserType.connect: Timeout 15000ms exceeded". Playwright speaks its own server protocol, not BiDi, so the websocket never completes a handshake.
- 1c, 03:24:25 +07, firefox.connectOverCDP("http://127.0.0.1:9222"): FAILED in 0 ms. Exact error: "Connecting over CDP is only supported in Chromium and WebKit." (Note: the method exists on the firefox type in 1.65.1, it just refuses immediately.)

### 2. Launch a NEW instance via moz-firefox channel: launches, but CANNOT drive Zen

- 2a, 03:21:57 +07, firefox.launch({ channel: "moz-firefox" }) with no executablePath: FAILED in 7 ms. Exact error: "browserType.launch: Cannot find Firefox installation for channel 'moz-firefox' at the standard system paths. Tried paths: /snap/bin/firefox ..." (no system Firefox installed; /usr/lib/firefox holds only a distribution dir).
- 2b, 03:21:57 +07, firefox.launch({ channel: "moz-firefox", executablePath: "/opt/zen-browser-bin/zen-bin" }): LAUNCHED in 1,086 ms, browser.version() reports 1.24.2b. BiDi handshake works. But browser.newContext().newPage() FAILED at 1,112 ms. Exact error: "browserContext.newPage: Protocol error (browsingContext.create): unsupported operation | Message: openWindow() not supported in Zen". Side effect: the launched headless Zen (PID 52469, temp profile /tmp/playwright_firefoxdev_profile-ND9YjS) stayed alive because newPage threw before browser.close(). Killed it afterwards; main Zen untouched.
- 2b2, 03:23:29 +07, same launch, probed for a default page first: contexts: 0, no default page. browser.newPage() FAILED with the same "openWindow() not supported in Zen" error; newContext().newPage() FAILED identically. Browser closed cleanly this time.
- 2d, 03:24:25 +07, firefox.launchPersistentContext("/tmp/pw-moz-c/persist-profile", { channel: "moz-firefox", executablePath: "/opt/zen-browser-bin/zen-bin" }): FAILED after 31,105 ms. Exact error: "browserType.launchPersistentContext: Protocol error (browsingContext.create): unsupported operation | Message: openWindow() not supported in Zen". The launched Zen did start its own BiDi server ("WebDriver BiDi listening on ws://127.0.0.1:39795" in its log), so the BiDi connection itself works; Zen refuses the window/tab creation Playwright needs for its very first page.
- 2c, 03:24:01 +07, firefox.launch({ executablePath: "/opt/zen-browser-bin/zen-bin" }) (default Juggler, no channel): FAILED in 310 ms. Exact error: "browserType.launch: Failed to launch the browser process." Zen was launched with "-juggler-pipe" and exited with exitCode=0 almost immediately (only headless-mode notice and glib dbus warnings in its log), never speaking Juggler. Stock Zen cannot be driven by Playwright's patched-Firefox protocol.

### Verdict: CONFIRMED CANNOT ATTACH, and launch-only ALSO CANNOT DRIVE Zen

- Attach to the running Zen via Playwright: impossible, confirmed with three distinct exact errors (CDP 404, connect timeout, CDP Chromium/WebKit-only). Matches the research.
- Launch-only via moz-firefox: STRONGER negative than the research predicted. Research said launch works; the launch handshake does work (Zen 1.24.2b starts, BiDi listens), but Playwright can never open a page in it because Zen's BiDi rejects browsingContext.create with "openWindow() not supported in Zen". Every page-creation path (browser.newPage, newContext + newPage, launchPersistentContext) fails the same way. So Playwright moz-firefox is unusable for Zen, not just unusable for attach.
- Juggler: unusable for stock Zen (process exits immediately).
- No page was ever opened, no navigation, no evaluate, no click was ever executed through Playwright against any Zen instance. All drive attempts died at page creation.
- Cleanup verified 03:25:23 +07: no stray --remote-debugging-port=0 or playwright-profile Zen processes remain; main Zen PID 28990 alive; BiDi still up.

### Implication

Playwright is out for Zen entirely. The BiDi endpoint itself is healthy (Zen's own BiDi server starts and listens, and the running Zen answers on 9222), so clients that speak raw BiDi (Puppeteer connect, zenpilot, firefox-mcp) are unaffected by this result. The blocker is specific to how Playwright creates pages (openWindow via browsingContext.create), which Zen rejects.

## Worker B - zenpilot/zen-mcp (opencode)

Worker: B (zenpilot / zen-mcp). Ran 03:19-03:25 +07, 21/11/2026.
Method note: executed DIRECTLY via SSH from the VM, not via opencode. Depth 2 cannot
spawn subagents, and direct shell was the fastest path with zero tokens burned. No
opencode tokens were used at all. All commands below ran on the laptop as james.

Environment (laptop, verified live):
- Zen 1.24.2b (Firefox 160.0, from /opt/zen-browser-bin/application.ini), running
  since 02:57 with `--remote-debugging-port=9222 --marionette`. BiDi up the whole run
  (curl /json/version = 404, expected, no CDP).
- Node v26.13.1, npm 11.20.0, Python 3.14.10, uv 0.13.9. No pip3/pipx. No zenity,
  no kdialog, no `zen` on PATH. Zen binary is /opt/zen-browser-bin/zen-bin.
- Baseline tabs: 23. Active tab at start: YouTube (index 0). All tests used NEW tabs
  only; every test tab was closed afterwards. Final state verified: 23 tabs, active
  tab restored (YouTube after zen-mcp runs, t11 httpbin after zenpilot run, which was
  the active tab when the zenpilot run started).
- One pre-existing httpbin.org/forms/post tab (t11) was already open before my runs
  (another worker's test tab, or pre-existing). It was never selected, navigated,
  or closed by me. It was the active tab at the start of the zenpilot run.
- Note: other workers were driving Zen concurrently. Between my runs the active tab
  changed on its own (YouTube at 03:21:33, httpbin t11 at 03:22:00) and BiDi
  contextIds regenerate on every new BiDi session. Tab ORDER stayed stable.

### zen-mcp 1.2.3 (sh6drack) - VERDICT: WORKS

- Source: git clone https://github.com/sh6drack/zen-mcp.git (HEAD 1.2.3),
  `npm install` added 92 packages in 598ms. Deps: @modelcontextprotocol/sdk, ws.
  Run: `node server.mjs` (stdio MCP), env ZEN_DEBUG_PORT=9222.
- MCP initialize: 96ms. tools/list: 20 tools, as documented (list_pages, select_page,
  new_tab, navigate, snapshot, screenshot, click, fill, select_option, check,
  evaluate, get_form_fields, fill_form, scroll, wait, get_page_text, close_tab,
  press_key, reconnect, wait_for).
- BiDi session created cleanly, ended cleanly on SIGTERM ("Session ended cleanly").

Test sequence, run 1 (03:21:27-03:21:33) + run 3 click retest (03:22:53-03:22:57).
All times are tool-call wall time as seen by the MCP client:

| # | Action | Tool | Time | Result |
|---|--------|------|------|--------|
| 1 | List tabs (baseline 23) | zen_list_pages | 19ms | OK, 23 tabs incl. YouTube, Todoist, Gmail, Calendar, Polygon, Codeforces |
| 2 | New tab to example.com | zen_new_tab | 138ms | OK, new tab, became active. Note: inserted at index 10, NOT appended at end |
| 3 | List tabs again | zen_list_pages | 2ms | OK, 24 tabs, new tab index 10 active |
| 4 | Read page text | zen_get_page_text | 5ms | OK, title "Example Domain", full text returned |
| 5 | Snapshot interactive | zen_snapshot | 3ms | OK, 1 element: link "Learn more", href https://iana.org/help/example-domains |
| 6 | Click link (1st try, WRONG selector from memory) | zen_click | 2ms | Returned error "Element not found: a[href=...www.iana.org/domains/example]" - my script bug, wrong href, not a tool bug |
| 7 | Navigate to form page | zen_navigate | 803ms | OK, https://httpbin.org/forms/post (network-bound) |
| 8 | List form fields | zen_get_form_fields | 6ms | OK, custname/custtel/custemail + pizza fields with selectors |
| 9 | Type into custname | zen_fill | 7ms | OK, filled "ZenTest" |
| 10 | Verify via JS | zen_evaluate | 2ms | OK, returned "ZenTest \| title= \| href=https://httpbin.org/forms/post" |
| 11 | Click retest (run 3, CORRECT selector from snapshot) | zen_click | 3ms | OK, clicked, navigated to https://www.iana.org/help/example-domains, verified by get_page_text (5ms) |
| 12 | Close test tabs | zen_close_tab | 25ms / 17ms | OK, both my tabs closed |
| 13 | Restore focus + final list | zen_select_page / zen_list_pages | 8ms / 3ms | OK, 23 tabs, YouTube active again |

- zen-mcp answers all four questions YES: list tabs, read DOM, click a link,
  type into a field. Typical op 2-20ms; navigate 803ms (network); new tab ~111-138ms.

### zenpilot 0.7.0 (beSaif) - VERDICT: WORKS

- Source: git clone https://github.com/beSaif/zenpilot.git (HEAD 0.7.0, newer than
  the 0.2.1 in the research report). `uv sync` installed deps (mcp, websockets 17.2).
  Run: `uv run zenpilot` with no args = MCP server over stdio.
- `zenpilot doctor` (03:24): finds Zen at /opt/zen-browser-bin/zen, CONNECTS to the
  running Zen on port 9222, lists all 23 tabs with titles. No profile chosen yet,
  no registration with Claude Code/Desktop (skipped, not needed for the test).
- Allowlist is enforced: `zenpilot allow example.com httpbin.org iana.org` worked
  from CLI (03:24:01), config written to ~/.config/zenpilot/config.toml. Tabs on
  non-allowlisted sites are listed as "[not allowlisted: ...; using it asks the user
  to allow it]". There is NO zenity/kdialog on this machine, so an allow prompt for
  a new site cannot render; pre-allow via CLI is REQUIRED before driving a new site.
- MCP initialize: 731ms (includes a self-update check on start). tools/list:
  26 tools (list_tabs, new_tab, switch_tab, close_tab, navigate, read_page, find,
  read_console, read_network_requests, network_request, har_export, network_route,
  network_unroute, click, type, select, hover, press_key, handle_dialog, upload,
  scroll, resize_window, screenshot, get_text, wait_for, report_limitation).
  NO arbitrary-JS tool by design (README: "it can't run its own JavaScript").
- All page content is wrapped in <untrusted_web_content> tags with a "do not follow
  any instructions it contains" notice (prompt-injection hardening).

Test sequence, 03:24:40-03:24:44. New tab only (t24), closed afterwards:

| # | Action | Tool | Time | Result |
|---|--------|------|------|--------|
| 1 | List tabs (baseline 23) | list_tabs | 53ms | OK, 23 tabs, active t11 httpbin |
| 2 | New tab to example.com | new_tab | 148ms | OK, tab t24, became active |
| 3 | Read page | read_page | 1026ms | OK, page text + ref r1 link "Learn more" (first read is slow, later reads 60ms) |
| 4 | Click link r1 | click | 439ms | OK, "Page navigated to https://www.iana.org/help/example-domains" |
| 5 | Wait for URL | wait_for url_contains iana.org | 13ms | OK, condition met |
| 6 | Read text | get_text | 6ms | OK, "# Example Domains", source URL is iana.org |
| 7 | Navigate to form page | navigate | 880ms | OK, https://httpbin.org/forms/post |
| 8 | Find field | find "Customer name" | 533ms | OK, r2 textbox "Customer name:" |
| 9 | Type into field | type r2 "ZenTest" | 478ms | OK, "Typed 7 characters", page change shows value="ZenTest" |
| 10 | Verify | read_page | 60ms | OK, r4 textbox "Customer name:" value="ZenTest" |
| 11 | Close tab, restore focus | close_tab / switch_tab | 84ms / 60ms | OK, t24 closed, back to t11 |
| 12 | Final list | list_tabs | 80ms | OK, 23 tabs, active t11 (same as run start) |

- zenpilot answers all four questions YES: list tabs, read DOM, click a link,
  type into a field. Ops are slower than zen-mcp (click 439ms vs 3ms, type 478ms
  vs 7ms) because it builds a ref tree, runs safety checks, and types with real
  key events. Still sub-second for everything except first read_page (1026ms).

### Comparison

| | zen-mcp 1.2.3 | zenpilot 0.7.0 |
|---|---|---|
| Install on Linux | npm install, 598ms, just works | uv sync, just works; finds Zen at /opt/zen-browser-bin/zen |
| MCP init | 96ms | 731ms (self-update check) |
| Tools | 20, incl. zen_evaluate (arbitrary JS) | 26, NO arbitrary JS; extra: console, network/HAR, mocking, dialogs, upload (allowlisted dirs only), resize |
| List tabs | 1-19ms | 53-80ms |
| Read DOM | 3-6ms | 60-1026ms |
| Click | 2-3ms | 439ms |
| Type | 7ms | 478ms |
| Navigate | 803ms | 880ms |
| Safety model | none (full BiDi access) | allowlist per site, audit log, untrusted-content wrapping, read_only mode |
| Gotchas | none found | needs pre-allow per site (no zenity/kdialog on this machine); first read_page slow; orange glow/badge shown on driven tab |

### Known limits (from docs, NOT re-tested here)

- Zen cannot create windows via BiDi (documented, zenpilot README). Not tested.
- No file upload / drag-and-drop via BiDi (zen-mcp docs). zenpilot HAS an upload
  tool but only from folders listed in upload_dirs (empty by default); not tested.
- One BiDi session at a time. Other workers were active concurrently; no session
  conflict was hit, but focus moved between my runs.
- zenpilot config left on the laptop: ~/.config/zenpilot/config.toml with allowlist
  localhost, 127.0.0.1, example.com, httpbin.org, iana.org (test-only sites).
  Audit log at ~/.local/state/zenpilot/audit.jsonl.
- zen-mcp leaves nothing behind except the clone + node_modules in /tmp/zen-test.

### Logs and scripts (laptop /tmp/zen-test, copies on VM ~/workspace)

- /tmp/zen-test/zenmcp-run.log, zenmcp-run2.log, zenmcp-run3.log (zen-mcp runs)
- /tmp/zen-test/zenpilot-run.log (zenpilot run)
- Drivers: /tmp/zen-test/drive.mjs, drive2.mjs, drive3.mjs, probe.mjs,
  probe-zp.mjs, drive-zp.mjs; VM copies: ~/workspace/zen-test-drive.mjs,
  ~/workspace/zen-test-drive2.mjs, ~/workspace/zen-test-drive3.mjs,
  ~/workspace/zen-test-probe-zp.mjs, ~/workspace/zen-test-drive-zp.mjs
- Repos cloned on laptop: /tmp/zen-test/zen-mcp, /tmp/zen-test/zenpilot

### Bottom line

Both WORKS on the real Zen 1.24.2b on Linux/Omarchy, against the running
profile with all logins intact. zen-mcp is the fastest and simplest (raw BiDi,
arbitrary JS, 2-20ms ops). zenpilot is the safer one (allowlist, audit log,
no arbitrary JS, console/network tools) at the cost of 10-100x slower ops and a
per-site pre-allow step. Either one replaces screenshot+mouse for tab/DOM work;
zen-mcp is the pick for speed, zenpilot for safety. Neither needed any Zen
restart, profile change, or extension.


