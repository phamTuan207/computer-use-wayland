Agent clone2 setup complete.
gh authenticated, repo cloned, branch main, working tree clean.
Ready for tasks via GitHub.

## Batch 2 status, 2026-11-21 afternoon

Received from the coordinator through the user, 6 tasks. Status at the start of this batch:

1. PR 1 handling: in progress. Latest main merged into this branch, the add/add conflict in this file was the only conflict and is resolved in the merge commit. PR summary updated on GitHub. Not merged by clone2, ready for the coordinator to review and merge.
2. Desktop control research, Vercel agent-desktop, linux-use, kde-desktop-mcp, CUA Hyprland native: done, doc docs/research/2026-11-21-desktop-control-landscape.md. Two of the four were installed and run here with timing, agent-desktop 1.3.1 and desktop-mcp v0.17.0, both fail fast at the missing AT-SPI bus on this headless VM, staged errors recorded in the doc section 6. In-session behaviour of all four is UNVERIFIED here and needs the laptop session.
3. AT-SPI research and a button click prototype without screenshots: done, doc docs/research/2026-11-21-atspi-desktop-control.md, prototype tests/atspi_prototype.py. Selftest passed on this machine, 2026-11-21T09:29:45Z, all steps ok, press verified by state read back. Live desktop mode UNVERIFIED here, headless VM, no pyatspi, no session bus, no display, recorded in the prototype log output. Needs a graphical session on the laptop, run command is in the doc section 6.
4. Ten realistic tests, code editing, file management, terminal and editor, error handling, reading docs: done, suite in tests/realistic_clone2 with README and run_all.py runner. Measured on this machine, 2026-11-21, wall clock 2026-11-21T09:34:21Z to 09:34:22Z, suite total elapsed 1.0483 s, result 10/10 PASS. First run was 8/10, the two failures were bugs in clone2 test code, a reject key mapping in test08 and a trailing chunk rule in test09, both fixed and re-run green. Per test elapsed: test01 0.0812 s, test02 0.0809 s, test03 0.0033 s, test04 0.0016 s, test05 0.0767 s, test06 0.1332 s, test07 0.0033 s, test08 0.0013 s, test09 0.067 s, test10 0.0016 s.
5. Selenium on real Zen, full preparation package: done, script tests/selenium_zen_live.py with launch and attach modes, JSONL timed log, built in tab safety rules, and procedure doc docs/research/2026-11-21-selenium-zen-live-procedure.md with a laptop checklist. Verified here on Firefox 160.0.1 stand-in, 2026-11-21: launch mode 12/12 steps ok, total 8.0402 s, attach mode 13/13 steps ok, total 4.4301 s, browser alive after, only own tabs closed. Batch 1 script re-verified the same day, 10/10 steps ok, total 5.1791 s. Zen itself UNVERIFIED until the laptop run.
6. Speed comparison table for all Zen control methods: pending.

Updates are appended to this section as each task finishes, with commit ids and measured results. No personal information in this file.

# Report: controlling Firefox and Zen through the DOM

Date of work: 2026-11-21, local time Asia/Saigon. All times in the test logs are UTC wall clock as printed by the test script, with elapsed seconds from a monotonic clock for every step.

This report is generic. It contains no personal information, no real names, no email addresses, no accounts, no tokens.

## 0. Verdict first

No method in this report can attach to a browser that was started normally, with no remote control flag. Every attach method needs the browser to have been launched with a flag that opens a remote protocol:

- Marionette, for Selenium plus geckodriver attach: launch with -marionette.
- WebDriver BiDi, for zenpilot, zen-mcp and this repo's own Zen wrapper: launch with --remote-debugging-port.
- Playwright: no attach to a user started Firefox or Zen at all, in any mode found. Launch only.

Central finding, measured here: Selenium plus geckodriver with --connect-existing does attach to a running Firefox, does list tabs, read the DOM, type, click and verify a DOM change, open and close a second tab, and the browser stays alive after the session is deleted. Full timed log in section 3. Zen attach through the same path is reported working by third party projects and is not an official Zen guarantee. It was not measured here because no Zen binary exists on this machine, see section 1.

## 1. Environment on this machine, measured

- Operating system: Linux x86_64, headless virtual machine, no Wayland display and no X display in this session.
- Preinstalled at start: Python 3.12.3, Node v24.22.1, a Chromium build for the agent browser. No Firefox, no Zen, no geckodriver, no Selenium, no Playwright.
- Downloaded for the test, into a tools folder outside the repo: official Firefox tarball, 86.7 MB, and geckodriver v0.37.1 linux64, 2.3 MB. Download wall clock 2026-11-20T20:19:35Z to 20:19:41Z, total elapsed 6.771 s, geckodriver 1.831 s, Firefox 4.926 s.
- Versions measured after extraction: Mozilla Firefox 160.0.1, geckodriver 0.37.1, Selenium Python 4.53.0 in a local virtual environment. The Firefox binary has no missing shared libraries on this machine, ldd reported 0 not found entries.
- Zen: not installed and not downloadable as a simple Linux tarball in this session, so no Zen binary was run here. Every Zen specific claim below is labelled documentary or reported, and the repo's own earlier Zen verification is summarised in section 7.

## 2. Comparison at a glance

| Method | Protocol to the browser | Attach to a running browser | List tabs | Read DOM | Click and type | Run own JavaScript | Speed evidence | Stability | Needs building |
|---|---|---|---|---|---|---|---|---|---|
| Selenium plus geckodriver, --connect-existing | WebDriver HTTP to geckodriver, then Marionette | Yes, if launched with -marionette | Yes, window_handles | Yes, page_source, find_element, execute_script | Yes | Yes | Measured here, section 3. Session create about 2.8 s, single DOM steps 0.03 to 0.27 s | Most mature stack here. One session only | No |
| Selenium plus geckodriver, launch mode | Same as above | No, it launches its own | Yes | Yes | Yes | Yes | Not measured here | Mature, best for repeatable scripted tests | No |
| zenpilot, beSaif/zenpilot | MCP over stdio to the agent, WebDriver BiDi to Zen | Yes, it opens Zen with remote control, or reopens it with the port | Yes, list_tabs | Partial, ref outline and readable text, no raw selector DOM, no own JavaScript | Yes, trusted BiDi input events | No, deliberately blocked | No published benchmark found | Alpha, mainly macOS tested, Linux tried on one NixOS Wayland setup | No |
| zen-mcp, sh6drack/zen-mcp | MCP over stdio, WebDriver BiDi over WebSocket | Yes, if Zen was started with --remote-debugging-port 9222 | Yes, zen_list_pages | Yes, snapshot with selectors, page text, form fields | Yes, zen_click, zen_fill, zen_fill_form | Yes, zen_evaluate | No published benchmark found | Small project, quiet since mid 2026, BiDi limits documented | No |
| zen-mcp, DoubleBobCat/zen-mcp | MCP to a Go bridge to a browser extension | Yes, through its extension and bridge | Yes, as part of 46 tools | Yes, through extension APIs | Yes | Yes, through extension | No published benchmark found | Very early, 4 commits at check time | No |
| Playwright, classic Firefox | Patched Firefox build, Juggler protocol over a pipe | No | Yes, in its own browser | Yes | Yes | Yes | Not measured here | Mature for its own browser builds, not for Zen | No |
| Playwright, moz-firefox BiDi channels | WebDriver BiDi, stock Firefox launched by Playwright | No, launch only in the evidence found | Yes, in its own launched browser | Yes | Yes | Yes | Experimental | Experimental support, test harness and MCP exposure | No |
| This repo, scripts/zen_cli.py | WebDriver BiDi over loopback WebSocket, stdlib Python | Only to a dedicated session it started itself, never to a daily session with no port | Yes, by index | Title, URL and visible text only, full DOM goes through browser observe and act | Not in this wrapper | script.evaluate is used internally for titles and text | Verified on Zen 1.24.2b on 2026-11-18, see section 7 | Repo owned, narrow and predictable | Already built |
| Chromium CDP, this repo scripts/cdp.mjs | Chrome DevTools Protocol | Only to Chromium, not relevant to Zen except as a contrast | Yes | Yes | Yes | Yes | Used by the repo Chromium harness | Mature for Chromium, Firefox removed CDP in version 141 | Already built |

Reading of the table: for maximum DOM control of Zen today, the BiDi tools and Selenium attach are the real candidates. Playwright is not a candidate for attach. The repo wrapper is the only one already integrated here, and it deliberately does not do DOM interaction yet.

## 3. Selenium plus geckodriver, --connect-existing

### 3.1 How it works

Documented facts, sources in section 10.

- --connect-existing tells geckodriver to connect to an existing Firefox instance and not start a new one. The existing instance must have Marionette enabled.
- Marionette is the remote protocol that lets out of process programs control Gecko based browsers. Outside the Mozilla tree, Marionette is used by geckodriver to implement WebDriver. Geckodriver is a proxy and translator: WebDriver HTTP in, Marionette over a TCP socket out. A Selenium call therefore has two hops.
- Enable Marionette at launch with the -marionette flag, single dash or double dash are equivalent. Do not rely on the old marionette.enabled preference as a startup trigger, Mozilla removed it as a trigger and the command line flag or the MOZ_MARIONETTE environment variable is the documented path. A Zen fork project still documents the preference, treat that as unverified for a given Zen build.
- Default Marionette address is 127.0.0.1 port 2828. The marionette.port profile preference defaults to 2828. If a profile sets a different port, geckodriver will not guess it, pass --marionette-port with the correct value.
- The WebDriver HTTP port is a different port. Geckodriver --port defaults to 4444. Do not confuse 4444 with 2828.
- Profile flags are Firefox flags, separate from geckodriver: -profile PATH or -P NAME, plus -no-remote or --new-instance to stop the launch being handed to an already running instance with a different profile.
- --remote-debugging-port is not needed for a pure WebDriver Classic plus Marionette attach. That flag opens the Remote Agent for WebDriver BiDi. Tools that use both Classic and BiDi, such as Mozilla firefox-devtools-mcp, need both flags. Selenium Classic alone needs only -marionette.

Minimal sequence:

1. Start the browser with Marionette and a chosen profile: firefox -marionette -no-remote -profile /path/to/test-profile URL, or the same with the zen binary.
2. Start geckodriver with --connect-existing --marionette-port 2828, plus --port for its WebDriver server.
3. Create one WebDriver session against that geckodriver.

### 3.2 Selenium Python patterns

Firefox attach is not the Chrome pattern. Chrome uses a debuggerAddress pointing at a DevTools port. Firefox Options moz:debuggerAddress is a boolean capability in Selenium source, not a Marionette host and port. Blog code that copies the Chrome recipe into moz:firefoxOptions is mixing two mechanisms.

Pattern A, Selenium starts geckodriver, flags through a Service object:

```python
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

service = Service(
    executable_path="/path/to/geckodriver",
    service_args=["--connect-existing", "--marionette-port", "2828"],
    log_output="/tmp/geckodriver.log",
)
driver = webdriver.Firefox(service=service, options=Options())
```

Pattern B, start geckodriver yourself, then use Remote. This is the pattern used by the test in this repo, because the two ports and the geckodriver start time stay visible and measurable:

```bash
geckodriver --connect-existing --marionette-host 127.0.0.1 --marionette-port 2828 --port 4444
```

```python
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

driver = webdriver.Remote(
    command_executor="http://127.0.0.1:4444", options=Options())
```

Notes: in connect-existing mode geckodriver does not launch a browser, so a binary location in Options is not what creates the attach. Python has no connect_existing helper argument, the raw geckodriver flags are the API. Java does have a builder helper, Python does not. Modern Selenium 4 uses the base service URL without a /wd/hub suffix.

### 3.3 What works after attach

Standard WebDriver Classic, unchanged by how the session was obtained:

- Tabs: driver.window_handles, switch with driver.switch_to.window(handle), read driver.title and driver.current_url per tab. There is no separate tabs API in Classic.
- DOM: driver.page_source, driver.find_element and find_elements with By.ID, By.CSS_SELECTOR, By.XPATH, element.text, element.get_attribute, and driver.execute_script for targeted returns such as element counts or outerHTML.
- Interaction: element.click(), element.send_keys(), element.clear(), element.submit(). Click timing is affected by the Marionette navigate after click check, enabled by default with a 50 ms wait window in the preferences documentation.
- Navigation and tabs: driver.get(url), back, forward, refresh, driver.switch_to.new_window("tab") in Selenium 4, driver.close(), driver.quit() to delete the session.
- Limits inside the session: navigation to about: pages and moz-extension:// pages is reported refused on Firefox family browsers, so browser internal pages and extension popup pages cannot be driven this way. Default context is content. Driving the browser chrome UI needs the system access path added in newer Firefox and geckodriver, and is out of scope for a DOM test.

### 3.4 Local test, measured here

Code: tests/selenium_connect_existing.py, fixture tests/fixtures/selenium_attach_fixture.html. The script launches Firefox headless with -marionette and a temporary profile in its self contained mode, starts geckodriver with --connect-existing, attaches with Pattern B, runs the task, deletes the session, and checks the browser is still alive. Every step records wall clock start and end and elapsed seconds.

Task steps in both runs: launch browser, start geckodriver, create session, list tabs, read DOM, type into the fixture input, click the fixture button and verify the output text became the typed text with a prefix, open a second tab to https://example.com/, read its title, close it and return, delete the session, verify the browser process and the Marionette port are still alive.

Run 1, wall clock 2026-11-20T20:21:04.340Z to 20:21:13.584Z, total elapsed 9.2447 s, exit code 0, all steps ok:

| Step | Elapsed s | Result |
|---|---|---|
| launch_browser_with_marionette | 3.8285 | Marionette port 2828 open, temporary profile |
| start_geckodriver_connect_existing | 0.1499 | Status endpoint ready |
| create_session | 2.8927 | Session created, browserName firefox, browserVersion 160.0.1 |
| list_tabs | 0.1371 | 1 tab, title Selenium Attach Fixture, local fixture URL |
| read_dom | 0.1265 | Title and heading read, page_source 700 chars, 16 elements, readyState complete |
| type_into_input | 0.1798 | Typed text read back exactly |
| click_and_verify_dom_change | 0.0855 | Output text matched the expected clicked value |
| open_second_tab_read_and_close | 1.7262 | 2 handles, second tab title Example Domain, closed back to 1 handle |
| delete_session | 0.0162 | Session deleted |
| browser_still_alive_after_session_delete | 0.0014 | Browser process running, Marionette port still open |

Run 2, wall clock 2026-11-20T20:21:22.090Z to 20:21:27.038Z, total elapsed 4.9837 s, exit code 0, all steps ok:

| Step | Elapsed s | Result |
|---|---|---|
| launch_browser_with_marionette | 0.7118 | Marionette port open |
| start_geckodriver_connect_existing | 0.0473 | Status endpoint ready |
| create_session | 2.7904 | Session created, same browser version |
| list_tabs | 0.0299 | 1 tab, same fixture |
| read_dom | 0.2685 | Same DOM values as run 1 |
| type_into_input | 0.1190 | Typed text read back exactly |
| click_and_verify_dom_change | 0.0894 | Output text matched |
| open_second_tab_read_and_close | 0.8420 | Example Domain, handles 1 to 2 to 1 |
| delete_session | 0.0482 | Session deleted |
| browser_still_alive_after_session_delete | 0.0002 | Browser still running, port still open |

Findings from the two runs:

- Attach works exactly as documented on stock Firefox. No workaround was needed.
- Session creation is the slowest single step in both runs, about 2.8 s, far slower than any DOM step. Any agent loop that creates a session per command will pay this every time. Keep one session alive and reuse it.
- Single DOM steps are fast on a local page: list tabs 0.03 to 0.14 s, read DOM 0.13 to 0.27 s, type 0.12 to 0.18 s, click plus verify 0.09 s.
- The second tab step includes a real network load of example.com, 0.84 to 1.73 s, so it is a network number, not a protocol number.
- Browser launch time varied, 3.83 s cold against 0.71 s in the second run, measured as time until the Marionette port opened. Treat launch numbers as machine and cache dependent.
- driver.quit() in this mode deleted only the session. The pre existing browser stayed alive and Marionette stayed open, in both runs. This matches the fix that landed for Firefox 91, and it is now verified on Firefox 160.0.1 here. It still needs the same check on the exact Zen build used on the target machine.
- Session identifiers, process identifiers and absolute local paths were recorded in the raw local log and are deliberately not reproduced in this report. The script prints them locally when run.

How to reproduce:

```bash
python3 -m venv /path/to/venv
/path/to/venv/bin/pip install selenium
/path/to/venv/bin/python tests/selenium_connect_existing.py \
    --geckodriver /path/to/geckodriver \
    --launch-firefox --firefox-binary /path/to/firefox \
    --headless --log-json /tmp/selenium_attach_log.json
```

Pure attach mode is the same command without --launch-firefox and --firefox-binary, with the browser already running with -marionette.

### 3.5 Limits, failures and risks for Selenium attach

- One session only. Marionette allows one WebDriver session at a time. A second attach while a session is active has historically hung for about 60 s and then failed with an unhelpful error, because the client got no greeting and kept retrying. A fix to fail fast with a clear error is described in the Mozilla bugs in section 10. Design rule: one owner per browser, and always delete the session in a finally block.
- Killing the client or geckodriver without deleting the session leaves the browser locked. A Mozilla tool had to fix exactly this, its cleanup now sends the session delete first. A hard killed test here would need a browser restart before the next attach.
- Version pairing matters. The Mozilla support table pairs geckodriver releases with a minimum Firefox and a Selenium minimum. Current rows, geckodriver 0.34 to 0.37.1, need Selenium 3.11 or later and Firefox 115 ESR or later, with no stated maximum. Older geckodriver rows are capped, for example 0.33 supports Firefox up to 120. For Zen, the number that matters is the Firefox base version of that Zen build, not the Zen version number.
- Zen specific, reported not official: a Zen first fork of Mozilla firefox-devtools-mcp documents attach as start Zen with --marionette, then run its tool with --connect-existing --marionette-port 2828, and states that its BiDi dependent features, console and network events, are not available in connect-existing mode while other features work. A separate third party harness reports that passing a profile through the moz:profile capability breaks session creation on Zen with geckodriver 0.36, error Invalid byte 45, offset 52, and that it uses a geckodriver owned temporary profile instead. Neither report is a Zen project guarantee.
- Zen binary discovery: in launch mode geckodriver looks for a binary named firefox by default, a Zen binary will not be found without an explicit binary path. In connect-existing mode no binary is launched, so this should not block attach.
- Side effects on a personal profile, reported by the Zen fork tool: Marionette recommended automation preferences can leave signon.autofillForms and signon.rememberSignons set to false after a session, which stopped saved password suggestions for its users, and the tool suggests setting remote.prefs.recommended to false before using Marionette on a personal profile. Separately, Marionette sets navigator.webdriver to true, which can trigger bot detection. Rules that follow: use a dedicated profile for attach tests by default, use a logged in profile only when the task needs it, and restore preferences after.
- Security: Marionette and geckodriver listen on loopback by default. Keep them on 127.0.0.1. Anything local can drive a browser that was left with Marionette open, including its logged in sessions.
- Geckodriver exit code 64 in old Selenium code was caused by passing service_args to webdriver.Firefox directly after that API was deprecated. Use a Service object, pass both --connect-existing and --marionette-port, and capture the geckodriver log or the failure is opaque.

## 4. zenpilot, beSaif/zenpilot

Identity: a single project with this name, on GitHub and on PyPI. Described by its author as letting an agent use Zen Browser with no extension, only on sites the user allows. Status alpha. At check time: created 2026-10-16, 61 commits, 15 releases, latest release v0.7.0 with PyPI files uploaded 2026-11-18, 11 stars, 4 forks, MIT.

Protocol: it is itself an MCP server, one Python process speaking MCP over stdio to the agent client. To the browser it speaks WebDriver BiDi, which Firefox and therefore Zen expose when started with --remote-debugging-port. No browser extension, no HTTP server, no native messaging host, not CDP, not Marionette directly. Input goes through BiDi input.performActions, so pages see trusted events, event.isTrusted is true. Element references are BiDi sharedId node references, not CSS selectors, and they reach into open shadow roots and iframes through their own browsing contexts.

Setup:

1. Requirements: macOS with Zen in /Applications, or Linux with Zen on PATH, in /opt/zen, in a local share zen folder, or as the Flatpak. If Zen is not found, set the ZENPILOT_ZEN environment variable to the start command. Linux dialogs use zenity or kdialog plus notify-send. There is no Claude Desktop app on Linux, so Linux use is through a code agent client.
2. Desktop app path: download the .mcpb file from the latest release and open it.
3. Code client path: uv tool install zenpilot, then zenpilot setup. Setup asks which Zen profile to use and which sites the agent may visit, registers the server with the agent clients it finds, and opens Zen. It can create a separate logged out profile, or use an existing profile after a dialog offering to reopen Zen with remote debugging. Setup writes preferences into the profile user.js.
4. Day to day commands: zenpilot setup, zenpilot allow, zenpilot launch, zenpilot doctor, zenpilot report, zenpilot log. Allowlist entries are added with zenpilot allow followed by a site name. Settings live in a config file under the user config folder, audit log is a jsonl file under the user local state folder.

Tools: the list grew by version. The documented 0.2.0 set has 11 tools: list_tabs, new_tab, switch_tab, close_tab, navigate, read_page, click, type, scroll, screenshot, get_text. read_page returns an indented outline of visible interactive elements and text with short references, capped at about 12k characters. get_text returns readable text, default maximum 8000 characters in that version. Later releases add reading console errors and network requests with responses, har_export, find a control by name, dropdown picking, hover, press_key, wait_for, handle_dialog, resize_window, and network routing tools.

Hard limits, documented by the project:

- It cannot run its own JavaScript, and it cannot touch cookies, passwords or downloads. There are no tools for arbitrary JavaScript, storage, clipboard or downloads.
- Allowlist only. A read_only setting makes it look but not click or type.
- Only http and https pages plus about:blank in the documented safety rules. No new windows over BiDi, new tabs open in the current window. Drag and drop is given as an example failure.
- One BiDi session at a time is a Firefox limit, not just this tool. The tool releases the session after 2 minutes idle, references and tab ids expire on release, and a hard kill can leave a stuck session that needs a Zen restart. There is no selected tab API in BiDi, so the active tab is inferred from focus and visibility.
- Restored tabs are lazy in Zen, a restored tab is only seen once opened.
- Warning from the project itself: while Zen runs with remote control open, other local applications can also reach it.
- Platform status: built and tested on macOS with Zen 1.23. Linux support is newer, stated as tried on NixOS, Wayland, with Zen 1.23.

Testability verdict: list tabs yes, click and type yes with trusted events, read DOM only in the mediated outline and text form, execute script no. This is a supervised agent driver for a real profile, not a programmable test driver.

Setup test on this machine: not run, because there is no Zen binary here and no agent client configuration to register against. The setup steps above are documentary, from the project README and PyPI pages, not a local verification.

## 5. zen-mcp, three different projects with one name

The name zen-mcp is ambiguous. Any instruction that just says zen-mcp, with no owner, is underspecified.

### 5.1 sh6drack/zen-mcp, the BiDi one

Identity: described as the first MCP server for Zen Browser, 20 tools, no Selenium, no Playwright, just WebSocket. At check time: created 2026-02-27, 8 commits, 1 release, 28 stars, 6 forks, MIT. A registry listing gives version 1.2.1 and a last commit date of 2026-05-16, about six months before this check. Treat it as dormant until the repo shows new commits.

Protocol: agent client over MCP stdio to the server, then WebDriver BiDi directly over WebSocket to Zen. No driver process, no extension. Form filling uses native value setters with input and change event dispatch, so React, Vue and Angular forms are claimed to work correctly.

Setup:

1. Start Zen with remote debugging. The README example is macOS only: the Zen application binary with --remote-debugging-port 9222. No Linux or Wayland launch instructions were found in the README fetched.
2. Install: npm install -g zen-mcp, or clone the repo and npm install, then point the client at node with the server file path.
3. Register the server in the agent client MCP configuration under the name zen-browser, command zen-mcp. Requirements: Zen Browser and Node.js 20 or higher. Configuration: environment variable ZEN_DEBUG_PORT, default 9222.
4. Documented test: node test-e2e.mjs, described as 21 tests, needs Zen running.

Tools, all 20, grouped by the project:

- Browse: zen_navigate, zen_list_pages, zen_select_page, zen_new_tab, zen_close_tab.
- See: zen_snapshot, page structure with selectors, filterable to all, interactive or form, zen_screenshot, zen_get_page_text for title, URL and text, zen_get_form_fields.
- Interact: zen_click, zen_fill, zen_select_option, zen_check, zen_press_key, zen_fill_form, zen_scroll.
- Utility: zen_evaluate, run JavaScript in the page, zen_wait, zen_wait_for, zen_reconnect.

Limits, documented by the project: Firefox WebDriver BiDi is still maturing, some advanced BiDi commands available in Chrome may not be available. Zombie sessions can only be cleared by restarting Zen. No file upload and no drag and drop, a BiDi limitation. Reliability features claimed: auto reconnect with exponential backoff, connection retry 3 attempts, clean shutdown on SIGINT and SIGTERM.

Testability verdict: list tabs yes, read DOM yes in snapshot form with selectors plus page text and form fields, and raw DOM is reachable through zen_evaluate, click and type yes, execute script yes. Of the two BiDi MCP tools, this is the one that fits a programmable DOM test, at the cost of dormant maintenance.

### 5.2 DoubleBobCat/zen-mcp, the extension and Go bridge one

A different project with the same repo name. It exposes Zen automation through a local bridge and a Zen extension, offers MCP over WebSocket and over streamable HTTP on localhost port 9222, and lists 46 callable tools, 43 core and 3 diagnostic, with workspace management as a special feature. Architecture: external MCP client to Go bridge to Firefox and Zen extension backend to Zen Browser APIs. At check time: created 2026-10-06, 4 commits, 3 stars, 1 release, GPL-3.0 only. This design does not have the BiDi limits of 5.1, but it depends on an extension staying installed and compatible with Zen updates, and it is the least proven of the three.

### 5.3 Not a browser project at all

The best known Zen MCP in general search is a multi model coding server that was formerly called Zen MCP and is now renamed. Its tools, chat, planner, consensus, code review and similar, have nothing to do with Zen Browser. Config copied from that project will not drive a browser. A similarly named devtools project for Zen also exists, a Zen first fork of Mozilla Firefox DevTools MCP that uses Selenium WebDriver, and should not be conflated with 5.1 or 5.2 either.

Setup test on this machine: not run for any zen-mcp variant, for the same reason as section 4, no Zen binary here. Setup steps are documentary.

## 6. Playwright with Firefox, attach or launch only

Verdict: attach to an already running Firefox or Zen, no. Launch a new Firefox controlled by Playwright, yes. Connect to a browser that Playwright itself launched as a server, yes, and that is not attach to a user browser.

How Playwright controls Firefox, documented:

- Classic Playwright Firefox does not use stock Firefox WebDriver, Marionette or CDP. It uses a Playwright specific patched Firefox build and the Juggler protocol over a pipe. The Playwright browsers page says its Firefox version matches a recent Firefox Stable build, and that Playwright does not work with the branded version of Firefox since it relies on patches.
- Launch documentation warns that Playwright only works with the bundled Chromium, Firefox or WebKit builds, and using another executable path is at your own risk. Zen is neither the branded Firefox nor the patched build, so the warning applies twice.
- firefox is the browser name and variant for that patched stable build. firefox-beta is a variant name for the beta line of the same Playwright build family. Neither is a way to select an installed Firefox or Zen binary. The branded channel list in the launch API, chrome, chrome-beta, msedge and similar, contains no Firefox entry.

What moz-firefox actually is, a correction to the assumption in the task:

- moz-firefox is a real name in Playwright, but it is not a classic Juggler launch channel. It is the WebDriver BiDi Firefox channel family. Evidence: the Playwright BiDi test readme runs tests with a project pattern moz-firefox-* and passes a custom Firefox binary path with an environment variable, with an example using a stock Firefox beta. A Playwright change renamed bidi-firefox-stable to the moz-firefox channel. Playwright MCP release notes later added support for moz-firefox BiDi channels in its browser option.
- Inference from that evidence: moz-firefox, and by pattern its beta and nightly siblings, mean launching stock unpatched Firefox through WebDriver BiDi on an experimental basis. The documented workflow is still a launch workflow, a binary path is supplied and Playwright starts the browser. No attach to a running browser is documented for this channel.

Connect APIs, documented:

- browserType.connect attaches Playwright to an existing browser instance created via launchServer. The endpoint comes from that server, and the connecting Playwright version must match the launching version. It is not a generic attach to any running browser.
- connect_over_cdp is Chromium only, stated directly in the docs: connecting over the Chrome DevTools Protocol is only supported for Chromium based browsers. The example uses the chromium object, not firefox.
- A GitHub issue from 2022, number 12044, asks exactly this question for Firefox over the Juggler protocol. The reporter tried starting Firefox with a juggler argument and a remote debugging port, then tried to connect, and reported that it fails and that they are unable to start driving the browser, while launchServer did create a usable endpoint. No later documentation found changes the connect definition above.
- Firefox has no CDP endpoint to give such a call in current versions. Mozilla removed CDP support from the Remote Agent, resolved fixed for the Firefox 141 branch, keeping CDP only on the 128 ESR branch. A remote debugging port on a current Firefox or Zen serves WebDriver BiDi, not CDP.

Persistent context and a profile that is already open, documented:

- launch_persistent_context is a launch method, it launches a browser that uses the storage at a user data directory. It is not an attach method.
- Browsers do not allow launching multiple instances with the same user data directory, and a Gecko profile is locked with OS file locking while in use. A second instance with the same profile fails with a profile in use error, and the user facing message is that Firefox is already running but not responding.
- Conclusion: if Zen is open on a profile, Playwright cannot open that same profile. What breaks is the launch itself, before any DOM work.

Workarounds, and what they really are:

- Copy the profile after closing the browser, then launch the copy with Playwright. Mozilla backup guidance states the precondition plainly, close Firefox first and then copy the profile folder. Copying while the browser runs risks locked files and incomplete database data, and the copy diverges from the live profile from that moment.
- Close the browser, then launch Playwright Firefox with the original profile path. This reuses the profile only as a new launch, it is not concurrent control, and Playwright may write its own preferences into that profile.
- Remote debugging port plus a direct BiDi or Marionette client, outside Playwright. That is sections 3, 4, 5 and 7, not a Playwright feature.
- Playwright server attach: launch with launchServer first, keep it running, then connect from another Playwright process. Works for Firefox in principle because it is the Playwright protocol. It still requires that Playwright launched the browser.

Local test on this machine: not run. Installing Playwright would download its own patched Firefox, which by the documentation above cannot be Zen and cannot attach, so a local run would only re-prove launch mode, which is not the question. The evidence for the verdict is documentary and specific, docs lines and issue 12044, listed in section 10.

## 7. What this repo already has, and what it already proved

This matters for the comparison, because two of the methods above are not greenfield here.

- scripts/zen_cli.py, a repo owned Zen wrapper, stdlib Python, talks to Zen over WebDriver BiDi on a loopback WebSocket, and reads the Zen profile read only for history. Its skill file is skill/cli-anything/zen.md.
- Verified in this repo on 2026-11-18 against Zen 1.24.2b, on a dedicated headless instance with a fresh profile, not against a daily session: launching Zen headless with --remote-debugging-port=9222 listens on 127.0.0.1:9222 and logs that WebDriver BiDi is listening, the WebSocket is at path /session, session.new returns browserName zen and the Zen version, browsingContext.getTree lists tabs, browsingContext.navigate plus script.evaluate returns the page title and URL, and a new tab is opened with window.open from an existing tab because browsingContext.createContext is an unknown command in that build.
- Also verified there: BiDi context ids are not stable across sessions, three sequential sessions returned three different id sets for the same tabs while tab order and URLs stayed identical, so the wrapper addresses tabs by index and never prints a context id. Any new BiDi tool built here must keep that rule.
- Also verified there: a normally started daily Zen has no remote debugging port listening, nothing on 9222, 2828 or 6000 in that check, so no tool can attach to it. Only read only history and an opt in remoting flag that opens a new tab touch that session, and the second was not run in that verification.
- The wrapper deliberately does not do DOM interaction. It lists, opens, activates, navigates and closes tabs, and reads title, URL and visible text. Click, fill and element reads are left to the browser observe and act path in the main harness.
- For Chromium the repo has the opposite situation, a mature CDP path: scripts/cdp.mjs, scripts/warm_browser.py with a persistent warm Chromium and a fresh context per task, and scripts/code_exec.py and improvements/a1-code-exec-dom-design.md for DOM program execution. That path has no Firefox equivalent because Firefox removed CDP, see section 6.
- Gap summary: the repo has BiDi tab control for a dedicated Zen, CDP DOM control for Chromium, and now, with this report, a measured Selenium Marionette attach test for Firefox. It has no BiDi DOM interaction layer for Zen yet, no click or fill over BiDi input actions in the Zen wrapper, and no Zen equivalent of the Chromium warm browser pattern.

## 8. Speed, stability, errors, and what to build

Speed, only where there is evidence:

- Measured here, Selenium attach on Firefox: session create about 2.8 s, DOM steps 0.03 to 0.27 s on a local page, second tab with a network load 0.84 to 1.73 s. No other method has a local number from this machine.
- No head to head benchmark against Selenium was found in the zenpilot or zen-mcp documentation. Any claim that BiDi is faster would be invented if stated as fact.
- Inference, labelled as such: a direct BiDi WebSocket path removes the geckodriver HTTP hop and the Selenium client hop, and the BiDi tools return compact snapshots, an outline in zenpilot and a filtered snapshot in zen-mcp, instead of repeated find_element round trips. That plausibly reduces per step latency in an agent loop. In the other direction, a scripted test with known selectors has no MCP stdio hop and no model facing serialisation, so Selenium may be as fast or faster for fixed tests. The deciding test is a timed run of the same task, navigate, snapshot, click, fill, on the same Zen build, through both paths. That test needs a Zen binary on the test machine and is the first item in section 9.

Stability, summary:

- Selenium plus geckodriver is the most stable and predictable option for repeatable tests today, a long maintained Mozilla and Selenium stack, with headless and CI patterns. Its weak point for this project is the attach story for a daily profile, one session, profile side effects, and the session create cost.
- The BiDi tools inherit Firefox BiDi maturity risk, documented by both projects, zombie sessions, missing upload and drag and drop, plus their own small project risk. zenpilot is active and very new, zen-mcp by sh6drack is dormant, the extension variant is very early.
- Playwright is stable inside its own browser builds and irrelevant for Zen attach.

Errors to expect, consolidated:

- Attach refused or a long hang: browser not started with the needed flag, wrong port, or a session already held by another client. Check the launch flags, check the port, check for a stale session, restart the browser if a session is stuck.
- Profile in use: a second launch against a profile that a running browser holds. Close the browser or use a different profile.
- Session create failure with a profile capability on Zen, reported. Use a driver owned temporary profile or a profile given at browser launch, not through the capability.
- Unknown command over BiDi on Zen, verified in this repo for browsingContext.createContext. Fall back to window.open and re-list tabs.
- Stale element or stale context references after navigation or after a session is released. Re-list tabs by index, re-find elements, never reuse BiDi context ids or zenpilot references across sessions.
- Bot detection and changed browser signals while a remote protocol is enabled, including navigator.webdriver under Marionette. Do not browse normally with remote control left on.

Recommendation for the stated goal, controlling Zen through the DOM as much as possible:

1. Short term, use what is already proven in this repo for a dedicated Zen: BiDi over a loopback port, tabs by index, script.evaluate for DOM reads. Extend scripts/zen_cli.py with DOM interaction, click and fill through BiDi input actions and script.evaluate, keeping the dedicated profile and dedicated session rules it already enforces. That is a build task on a verified base, not a new dependency.
2. In parallel, evaluate sh6drack/zen-mcp on the target machine as the fastest route to selector snapshots and JavaScript evaluation in Zen, accepting dormant maintenance, and zenpilot where a supervised, allowlisted, no JavaScript driver is the safer fit for a real profile.
3. Use Selenium plus geckodriver, the test in tests/, for scripted, repeatable Firefox and Zen regression tests, launched or attached with -marionette and a dedicated profile. This is the measured, working baseline from this report.
4. Do not plan any Playwright attach work for Zen. Use Playwright only where its own Firefox build is acceptable as the test browser.
5. Any plan that needs the daily, already open Zen must start from the hard fact in section 0: that Zen has to be relaunched with a remote flag first, with a profile decision made explicitly, dedicated by default, daily only with consent and with preferences restored after.

## 9. Next tasks proposed, not done in this report

- Run the deciding timed comparison on a machine with Zen: same task through the repo BiDi wrapper extended with evaluate, through sh6drack/zen-mcp, and through tests/selenium_connect_existing.py against Zen launched with -marionette. Record wall clock and elapsed per step, full logs, same pages, same Zen build, and state the Zen and Firefox base versions.
- Run tests/selenium_connect_existing.py against Zen itself, not only Firefox, and record whether Marionette opens on port 2828, whether session creation works without a profile capability, and whether the browser stays alive after session delete, on that Zen build.
- Add click and fill to the repo Zen wrapper over BiDi, with the tab by index rule and a timed live test against a local fixture page like the Selenium fixture in tests/fixtures/.
- Decide the session ownership rule for the team, one driver per browser at a time, with a written release step, because both Marionette and BiDi are single session protocols.

## 10. Sources

Selenium and geckodriver:

- https://firefox-source-docs.mozilla.org/testing/geckodriver/Flags.html
- https://firefox-source-docs.mozilla.org/remote/marionette/index.html
- https://firefox-source-docs.mozilla.org/testing/marionette/Prefs.html
- https://firefox-source-docs.mozilla.org/browser/CommandLineParameters.html
- https://firefox-source-docs.mozilla.org/testing/geckodriver/Support.html
- https://firefox-source-docs.mozilla.org/testing/geckodriver/Building.html
- https://firefox-source-docs.mozilla.org/testing/geckodriver/Profiles.html
- https://github.com/mozilla/geckodriver/issues/1980
- https://bugzilla.mozilla.org/show_bug.cgi?id=2085827
- https://bugzilla.mozilla.org/show_bug.cgi?id=2081625
- https://bugzilla.mozilla.org/show_bug.cgi?id=1713782
- https://github.com/mozilla/firefox-devtools-mcp
- https://github.com/simon-ami/zen-devtools-mcp
- https://www.selenium.dev/selenium/docs/api/py/selenium_webdriver_firefox/selenium.webdriver.firefox.webdriver.html

zenpilot and zen-mcp:

- https://github.com/beSaif/zenpilot
- https://pypi.org/project/zenpilot/
- https://github.com/sh6drack/zen-mcp
- https://github.com/DoubleBobCat/zen-mcp
- https://github.com/zen-browser/desktop
- https://firefox-source-docs.mozilla.org/remote/index.html

Playwright:

- https://playwright.dev/docs/browsers
- https://playwright.dev/docs/api/class-browsertype
- https://playwright.dev/python/docs/api/class-browsertype
- https://github.com/microsoft/playwright/issues/12044
- https://github.com/microsoft/playwright/issues/28533
- https://github.com/microsoft/playwright/blob/main/tests/bidi/README.md
- https://bugzilla.mozilla.org/show_bug.cgi?id=1882096
- https://firefox-source-docs.mozilla.org/toolkit/profile/index.html
- https://support.mozilla.org/en-US/kb/firefox-already-running-not-responding

In this repo:

- scripts/zen_cli.py
- skill/cli-anything/zen.md
- scripts/cdp.mjs
- scripts/warm_browser.py
- tests/selenium_connect_existing.py
- tests/fixtures/selenium_attach_fixture.html
