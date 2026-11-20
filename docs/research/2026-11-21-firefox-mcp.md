# Mozilla firefox-mcp: setup, tools, and comparison with direct Puppeteer over WebDriver BiDi

Date: 2026-11-21. Repo HEAD at time of writing: 6f055e1 (per parent task).
Scope: Mozilla's official MCP server for Firefox only. Similarly named projects
(JediLuke/firefox-mcp-server, dh1011/firefox-mcp) are different software and are
not covered here except where noted in section 8.

## 1. What it is

Firefox MCP is a Model Context Protocol (MCP) server that lets AI agents use
Firefox. It has two main use cases, per its README: agentic browsing (reading
pages, filling forms, multi-step flows) and agent-assisted web development
(console, network requests, debugger, profiler).

It controls Firefox through WebDriver BiDi, via Selenium WebDriver. It works
with Claude Code, Claude Desktop, Cursor, Cline, and other MCP clients.

Sources:
- Repo: https://github.com/mozilla/firefox-mcp
- Release note, v0.11.0: https://discourse.mozilla.org/t/firefox-mcp-v0-11-0-released/150327
- Firefox Source Docs: https://firefox-source-docs.mozilla.org/ai-agent-tools/firefox-devtools-mcp.html

### 1.1 Rename history, and which package to install

The project was first published as Firefox DevTools MCP, repo
mozilla/firefox-devtools-mcp, npm package `@mozilla/firefox-devtools-mcp`.
On 2026-11-19 it was renamed to Firefox MCP, repo mozilla/firefox-mcp, npm
package `@mozilla/firefox-mcp`, version 0.11.0. The same build is still
published as `@mozilla/firefox-devtools-mcp`, so existing setups keep working.
The Mozilla-internal package is now `@mozilla/firefox-mcp-moz`. New setups
should use `@mozilla/firefox-mcp` and the MCP server key `firefox`, which
gives tool names like `mcp__firefox__navigate_page`.

Verified on this machine by `npm view`: `@mozilla/firefox-mcp` latest is
0.11.0 (checked 2026-11-20 20:17 UTC). The installed package.json in the
scratch folder confirms version 0.11.0, license MIT OR Apache-2.0, Node
engines `>=20.19.0`, main `dist/index.js`, bin `firefox-mcp`.

### 1.2 How it is built

Installed dependencies (from the installed package.json, read 2026-11-20):
- `@modelcontextprotocol/sdk` 1.29.0 (MCP protocol, stdio transport)
- `selenium-webdriver` 4.36.0 and `geckodriver` 6.0.2 (browser launch and
  WebDriver BiDi session)
- `ws` 8.21.0, `yargs` 17.7.2

Architecture: MCP client --stdio--> firefox-mcp server --Selenium/geckodriver-->
Firefox (WebDriver BiDi plus WebDriver Classic/Marionette for some operations).
This matters for the comparison in section 7: there are three processes and two
protocol hops between the agent and the page, where a direct Puppeteer BiDi
client has one WebSocket hop.

## 2. Requirements

Per the README:
- Node.js >= 20.19.0. This machine has Node v24.22.1 and npm 10.9.4, so the
  Node requirement is met.
- Firefox 100+ installed (auto-detected, or pass `--firefox-path`).
- A local Firefox installation is required. The README states it cannot run on
  cloud hosting services.

## 3. Setup guide

### 3.1 Fastest path: npx, no install step

```
npx @mozilla/firefox-mcp@latest
```

Use `@latest` for the newest release. Pre-1.0 versioning applies (versions
start at `0.x`).

### 3.2 Claude Code (CLI)

```
claude mcp add firefox npx @mozilla/firefox-mcp@latest
```

Headless with a viewport:

```
claude mcp add firefox npx @mozilla/firefox-mcp@latest -- --headless --viewport 1280x720
```

Or via environment variables:

```
claude mcp add firefox npx @mozilla/firefox-mcp@latest \
  --env START_URL=https://example.com \
  --env FIREFOX_HEADLESS=true
```

### 3.3 Codex (CLI)

```
codex mcp add firefox -- npx @mozilla/firefox-mcp@latest
```

Headless with a viewport:

```
codex mcp add firefox -- \
  npx @mozilla/firefox-mcp@latest -- --headless --viewport 1280x720
```

### 3.4 Generic MCP client (config file)

Claude Code `mcp_settings.json`:

```json
{
  "mcpServers": {
    "firefox": {
      "command": "npx",
      "args": ["-y", "@mozilla/firefox-mcp@latest", "--headless", "--viewport", "1280x720"],
      "env": {
        "START_URL": "about:blank"
      }
    }
  }
}
```

Codex `~/.codex/config.toml`:

```toml
[mcp_servers.firefox]
command = "npx"
args = ["-y", "@mozilla/firefox-mcp@latest", "--headless", "--viewport", "1280x720"]

[mcp_servers.firefox.env]
START_URL = "about:blank"
```

### 3.5 Local dev build (from source)

```
git clone https://github.com/mozilla/firefox-mcp.git
cd firefox-mcp
npm install
npm run build
npx @modelcontextprotocol/inspector node dist/index.js --headless --viewport 1280x720
```

There is also a helper script, `npm run setup`, which asks which client to
configure and writes the JSON to the right path. A Dockerfile and a
docker-compose file are included in the repo for container use.

### 3.6 MCP Inspector (no client needed)

```
npx @modelcontextprotocol/inspector npx @mozilla/firefox-mcp@latest --start-url https://example.com --headless
```

Then call tools such as `list_pages`, `select_page`, `navigate_page`,
`take_snapshot`, `click_by_uid`, `fill_by_uid`, `list_network_requests`,
`list_console_messages`, `screenshot_page`.

### 3.7 CLI options

Flags or environment variables (from the README):

- `--firefox-path`: absolute path to the Firefox binary. This is the hook for
  pointing the server at a Zen binary instead of stock Firefox (see section 6).
- `--headless` (`FIREFOX_HEADLESS=true`): run without UI.
- `--viewport 1280x720`: initial window size.
- `--profile-path`: use a specific Firefox profile. Firefox runs in a
  `firefox_mcp_profile` subfolder of that path, marked with a `.firefox-mcp`
  file. Pointing at a marked profile reuses it directly.
- `--firefox-arg`: extra Firefox arguments, repeatable.
- `--start-url` (`START_URL`): URL to open on start.
- `--accept-insecure-certs` (`ACCEPT_INSECURE_CERTS=true`).
- `--connect-existing` (`CONNECT_EXISTING=true`): attach to an already running
  Firefox instead of launching a new one.
- `--marionette-port` (`MARIONETTE_PORT`): Marionette port for
  connect-existing mode, default 2828.
- `--idle-timeout` (`IDLE_TIMEOUT`): seconds without tool calls after which a
  connect-existing session releases Firefox, default 1800. Firefox accepts one
  client at a time, so other clients can only connect once it is released. The
  next tool call reconnects and selects the tab that is active in Firefox at
  that moment.
- `--pref name=value`: set a Firefox preference at startup via
  `moz:firefoxOptions`, repeatable.
- `--tool-preset`: `slim`, `basic` (default), `developer`, `mozilla`, or `all`.
- `--tools`: explicit list of tool modules, overriding `--tool-preset`.
- `--android-device`, `--android-wipe-app-data`, `--android-package`: Firefox
  for Android mode. Warning: Android mode wipes all data of the target app
  before every session (tabs, history, bookmarks, passwords, cookies,
  settings). Use a build dedicated to automation.
- `--unrestricted-save-paths`: let `saveTo` write anywhere on disk instead of
  the default roots.
- `--log-file`: write MCP server logs to a file instead of stderr. Set
  `DEBUG=*` for verbose debug logs.

Useful preferences (`--pref`):
- `remote.prefs.recommended=false`: skip the automation RecommendedPreferences
  so the browser behaves closer to a regular Firefox instance.
- `remote.log.level=Trace`: verbose WebDriver protocol logs in Firefox.
- `app.update.disabledForTesting=false`: allow Firefox to auto-update (may
  interrupt a session; also needs `remote.prefs.recommended=false`).

### 3.8 Connect to an existing Firefox (your real session)

```
firefox --marionette --remote-debugging-port
npx @mozilla/firefox-mcp --connect-existing --marionette-port 2828
```

Both flags are required: the server uses WebDriver Classic (`--marionette`)
and WebDriver BiDi (`--remote-debugging-port`). If Firefox is started with
`--marionette` only, the server fails to connect and asks for a restart with
both flags. If Firefox is already running with the same profile, the command
only opens a new window in that instance and the flags are ignored.

Dedicated profile, so everyday Firefox keeps running without Marionette:

```
firefox -CreateProfile firefox-mcp
firefox -P firefox-mcp --marionette --remote-debugging-port
```

Warning from the README: do not leave Marionette enabled during normal
browsing. It sets `navigator.webdriver = true` and changes other browser
fingerprint signals, which can trigger bot detection on sites protected by
Cloudflare, Akamai, and similar services. Enable Marionette only when
automation is needed, then restart Firefox normally afterward, or run it in a
dedicated profile.

## 4. Tool inventory (public package)

Full reference: `docs/tools.md` in the upstream repo (generated from source).
Counts are per module; presets are cumulative and `basic` is the default.

| Module | Tools | slim | basic | developer | mozilla | all |
| --- | --- | --- | --- | --- | --- | --- |
| pages | 6 | yes | yes | yes | yes | yes |
| snapshot | 3 | yes | yes | yes | yes | yes |
| input | 8 | yes | yes | yes | yes | yes |
| network | 3 | no | no | yes | yes | yes |
| console | 2 | no | no | yes | yes | yes |
| screenshot | 2 | yes | yes | yes | yes | yes |
| print | 1 | no | yes | yes | yes | yes |
| downloads | 3 | no | yes | yes | yes | yes |
| utilities | 4 | no | yes | yes | yes | yes |
| management | 3 | no | yes | yes | yes | yes |
| launch (moz build) | 1 | no | no | no | yes | yes |
| webextension | 3 | no | yes | yes | yes | yes |
| profiler | 3 | no | no | yes | yes | yes |
| screencast | 2 | no | yes | yes | yes | yes |
| script | 1 | no | yes | yes | yes | yes |
| debugging | 6 | no | no | yes | yes | yes |
| prefs (privileged) | 2 | no | no | no | yes | yes |
| privileged (privileged) | 3 | no | no | no | yes | yes |
| bidi (moz build) | 1 | no | no | no | yes | yes |

### 4.1 Pages

`list_pages` (tabs: index, title, URL; selected tab marked),
`new_page` (open tab at URL, `wait` none/interactive/complete),
`navigate_page`, `select_page` (by index, URL, or title substring),
`close_page`, `get_page_text` (document.body.innerText, capped at 20000
chars inline by default, full text with `saveTo`).

### 4.2 Snapshot (DOM control core)

`take_snapshot`: DOM snapshot with stable UIDs. A UID stays valid across
snapshots until its element is removed or the page navigates. Output caps at
100 lines by default; scope with a CSS `selector` or dump the full tree with
`saveTo`. Options: `maxLines`, `includeAttributes`, `includeText`,
`maxDepth`, `includeAll`, `selector`, `saveTo`, `preview`.
`resolve_uid_to_selector`: resolve a UID to a CSS selector. Fails if the
element is gone. `clear_snapshot`: clear snapshot UIDs.

This UID model is the main difference from raw BiDi: the agent never handles
raw node ids or coordinates. It snapshots, then acts by UID.

### 4.3 Input

`click_by_uid` (plus `dblClick`), `hover_by_uid`, `fill_by_uid` (text input,
textarea, or select option), `drag_by_uid_to_uid` (HTML5 drag events),
`fill_form_by_uid` (many fields at once), `upload_file_by_uid`,
`press_key` (one key, optional modifiers, not for entering text),
`type_text` (key by key into the focused element, optional submit key; for
elements that only react to real typing, such as autocomplete fields and rich
text editors).

### 4.4 Network, console, screenshot, print, downloads, utilities, management

- Network: `list_network_requests` (always-on capture, filter by URL, method,
  status, resource type), `get_network_request` (details plus response body),
  `set_network_cache` (bypass cache, per tab or global; useful for
  performance measurement).
- Console: `list_console_messages` (filter by level, time, text, source),
  `clear_console_messages`.
- Screenshot: `screenshot_page` (viewport or full page), `screenshot_by_uid`.
- Print: `print_page` (PDF, landscape and background options).
- Downloads: `list_downloads`, `clear_downloads`, `set_download_behavior`
  (allow/deny/default, avoids the native save-file dialog).
- Utilities: `accept_dialog`, `dismiss_dialog`, `navigate_history`,
  `set_viewport_size`.
- Management: `get_firefox_output` (Firefox stdout/stderr including MOZ_LOG,
  warnings, crashes, stack traces), `get_firefox_info` (binary path,
  environment, output file location), `close_firefox_session`.

### 4.5 WebExtension, profiler, screencast, script, debugging

- WebExtension: `install_extension` (BiDi `webExtension.install`, from
  archive, base64, or unpacked path; temporary by default, permanent needs a
  signed extension), `uninstall_extension`, `list_extensions`.
- Profiler: `profiler_is_active`, `profiler_start` (presets: web-developer,
  firefox-platform, graphics, media, ml, networking, power, debug),
  `profiler_stop`.
- Screencast: `screencast_start`, `screencast_stop` (Firefox 154+).
- Script: `evaluate_script` (run a JS function in the page, return the
  result; `args` takes UIDs, including from iframes; `sandbox` option runs in
  an isolated realm sharing the page DOM; `timeout` default 5000 ms).
  The README advises preferring this for targeted reads (a value, text,
  computed style, whether an element exists) instead of a full snapshot, and
  using the UID interaction tools for clicking, typing, and filling.
- Debugging: `enable_debugger`, `list_scripts`, `get_script_source`,
  `set_logpoint`, `remove_logpoint`, `get_logpoint_results` (Firefox 153+).

### 4.6 What the public package does NOT include

The `prefs`, `privileged`, `launch`, and `bidi` modules require the
Mozilla-internal build (`@mozilla/firefox-mcp-moz`). The public package skips
them even if requested and logs a warning naming the modules it dropped.

- `send_bidi_command`: send a raw WebDriver BiDi command (for example
  `browsingContext.getTree`). This is the escape hatch for BiDi features no
  other tool covers. Not in the public package.
- `restart_firefox`: restart under a different binary, profile, environment,
  or prefs. Not in the public package.
- `get_firefox_prefs` / `set_firefox_prefs`: runtime pref access via a
  privileged API. Needs `MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1` and the internal
  build.
- `list_privileged_contexts`, `select_privileged_context`,
  `evaluate_privileged_script`: access to privileged ("chrome") browsing
  contexts. Needs `MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1` and the internal build.

Consequence for this repo: anything that needs raw BiDi commands or
chrome-context access cannot be done through the public npm package. It needs
either a direct BiDi client (see section 7) or the Mozilla-internal build,
which is not generally available to us.

### 4.7 Saving bulky output to disk

Several tools accept `saveTo`, which writes the result to a file instead of
returning it inline: `get_page_text`, `take_snapshot`,
`list_network_requests`, `get_network_request`, `list_console_messages`,
`screenshot_page`, `screenshot_by_uid`, `print_page`, `evaluate_script`,
`evaluate_privileged_script`, `send_bidi_command`. The response returns the
path and byte size, and the saved file always holds the full untruncated data.
By default, relative paths resolve against the current working directory and
absolute paths are only allowed within `~/.firefox-mcp`. Paths reaching a
Firefox profile, or files the server reads back, are refused. Start with
`--unrestricted-save-paths` to write anywhere. This is useful for keeping
agent context small: save the full snapshot, read only the needed part.

## 5. Security notes (from the upstream README and SECURITY.md)

- Use a dedicated Firefox profile. Never run the server against a regular
  profile: the agent has access to whatever the browser can reach, including
  cookies and saved sessions.
- Be cautious about which sites to visit. Pages can return content designed to
  manipulate the agent (prompt injection). Stick to sites you control or trust.
- Enable only the tool modules you need. The default `basic` preset already
  includes `evaluate_script`; `--tool-preset slim` drops it. Higher presets
  (`developer`, `mozilla`) expand what the agent can do further.
- Do not leave Marionette enabled during normal browsing (see section 3.8).
- Android mode wipes all app data before every session (see section 3.7).
- A CVE was reported against this project in April 2026 (CVE-2026-7064, OS
  command injection, CWE-78) according to a third-party review; the upstream
  fix status was not verified in this task. Treat the version pinned here
  (0.11.0) as the version to re-check against the upstream changelog before
  adopting.

## 6. Zen notes

Zen is a Firefox fork, so the same WebDriver BiDi and Marionette machinery
should in principle apply. Concretely:

- `--firefox-path` accepts any Firefox-compatible binary, so pointing it at a
  Zen binary is the documented way to try Zen with this server. UNVERIFIED:
  no Zen binary exists on this machine, so this was not tested.
- Connect-existing mode needs Firefox started with `--marionette` and
  `--remote-debugging-port`. Whether a Zen build accepts both flags the same
  way, and whether its BiDi implementation matches stock Firefox, is
  UNVERIFIED.
- The server launches its own Firefox by default in a dedicated
  `firefox_mcp_profile`. For the repo goal of controlling the user's real Zen
  session, connect-existing mode is the path to test, with the Marionette
  fingerprint caveat from section 3.8.
- Zen version skew matters: the server needs Firefox 100+, and newer tools
  need Firefox 153+ (debugging) or 154+ (screencast). The Zen version on the
  target machine must be checked against those floors. UNVERIFIED here.

## 7. Comparison: firefox-mcp vs direct Puppeteer over WebDriver BiDi

All speed numbers in this section are UNVERIFIED. No live browser run was
possible on this machine (see section 9). The comparison below is
architecture and documentation based. Measured Puppeteer numbers belong to the
sibling Puppeteer task.

| Axis | firefox-mcp (Mozilla, public npm) | Direct Puppeteer over BiDi |
| --- | --- | --- |
| Speed | Extra hops: MCP stdio JSON-RPC, plus Selenium, plus geckodriver, plus BiDi. Each tool call also pays for a snapshot round trip when the agent needs fresh UIDs. First run is slow: the README says Selenium sets up the BiDi session, and later runs are faster. Expected to be slower per action than a direct client, by an unmeasured amount. UNVERIFIED. | One WebSocket hop to the BiDi endpoint, no MCP layer, no Selenium, no geckodriver. Lowest per-action latency of the two. The agent drives the protocol directly, so it can batch and pipeline commands. UNVERIFIED numerically. |
| Stability | Maintained by Mozilla, 589 stars, 440 commits, 45 releases at the time of reading. Known failure modes from the README: Firefox not found (needs `--firefox-path`), first run slow, stale UIDs after navigation or element removal (fix: fresh snapshot), Windows 10 MCP error -32000 connection closed (workarounds: wrap with `cmd /c`, or use an absolute npx path). Marionette accepts one client at a time, with an 1800 s idle timeout. The server cannot run without a local Firefox. | Stability depends on the client you write: reconnect logic, session recovery, and BiDi version skew are yours to own. No MCP server to crash, but also no maintained server to absorb protocol changes. Firefox BiDi coverage is still growing, so some operations may be missing or behave differently across Firefox versions. UNVERIFIED on this machine. |
| DOM control depth | Deep for page content: snapshot UIDs, click, fill, hover, drag, type, press key, upload, `evaluate_script` for arbitrary JS, plus network, console, profiler, debugger, screencast. Gated: no raw BiDi in the public package, no privileged chrome contexts, no runtime pref get/set, no restart with a new config. DOM access is mediated: you act through UIDs and the snapshot, not through raw node handles. | Full BiDi surface that Firefox implements, including raw commands (for example `browsingContext.getTree`, `script.evaluate`, `input.performActions`) and direct node access. No UID indirection and no preset gating. Deeper in principle, but every capability must be wired by hand. UNVERIFIED on this machine. |
| Setup friction | Lowest friction to start: one `npx` command, no build, no code. Needs Node >= 20.19 and a local Firefox 100+. Friction points: Firefox auto-detection, first run slow, Windows wrapper issue, dedicated profile recommended, Marionette fingerprint warning for connect-existing mode. | Higher friction: write the client, manage the BiDi WebSocket, handle session creation, context tracking, and error recovery yourself. No MCP client config needed, and no Selenium or geckodriver to install. |
| What needs custom building | For this repo's goal: a Zen connect-existing test (`--firefox-path` at a Zen binary, Marionette plus remote-debugging-port flags), a timing harness around MCP tool calls, and anything needing raw BiDi or chrome contexts (not available in the public package). If the agent loop already speaks MCP, almost nothing else is needed. | Everything: the client, the timing harness, snapshot or DOM reading helpers, input helpers, and error recovery. But nothing is gated: the full protocol is available to build on. |

Reading of the table for this repo: use firefox-mcp when an agent already
speaks MCP and needs a maintained, safe-by-default way to browse and debug
with Firefox, and accept the extra latency and the gated protocol surface.
Use direct Puppeteer over BiDi when the repo needs the lowest latency,
deterministic timing, raw protocol access, or control of a Zen session that
the public firefox-mcp package cannot reach. The two are not exclusive: the
server itself is a BiDi client, so a direct client can reuse what it proves
about Zen's BiDi support.

## 8. Test procedure (not yet run live)

Run these steps on a machine with a real Firefox or Zen binary. Record
wall-clock start and end plus elapsed time for every step, and keep the full
log. Do not report a timing you did not measure.

### 8.1 Install and smoke test

```
date -u +%FT%TZ
time npm install @mozilla/firefox-mcp@0.11.0
node -e "console.log(require('./node_modules/@mozilla/firefox-mcp/package.json').version)"
npx @mozilla/firefox-mcp --help
date -u +%FT%TZ
```

Expected: install adds the package, version prints 0.11.0, `--help` prints
the CLI options from section 3.7. Note: `--help` may still start the server
path, so run it with a timeout and record the exit code either way.

### 8.2 MCP handshake without a browser (tools/list)

Use a small Node stdio client (no extra dependency): spawn
`node node_modules/@mozilla/firefox-mcp/dist/index.js --headless`, send
JSON-RPC `initialize` with protocol version `2024-11-05`, then
`notifications/initialized`, then `tools/list`. Record the tool list and the
elapsed time per message. Expected: the server answers `tools/list` without a
browser, because Firefox launches lazily on the first tool call. UNVERIFIED:
this was not run here (see section 9).

### 8.3 Live end-to-end test (needs a Firefox or Zen binary)

```
firefox --headless --marionette --remote-debugging-port &
npx @mozilla/firefox-mcp --connect-existing --marionette-port 2828 --log-file /tmp/firefox-mcp.log
```

Through MCP Inspector, or through the stdio client from 8.2, call in order
and time each call:

1. `list_pages`
2. `navigate_page` to a local test page (use a `file://` fixture from this
   repo, not a public site, so the run is repeatable offline)
3. `take_snapshot`
4. `click_by_uid` on a button from the snapshot, then `take_snapshot` again
   and confirm the expected state change in the DOM
5. `fill_by_uid` on a text input, then `evaluate_script` with
   `() => document.querySelector('input').value` to confirm the value
6. `screenshot_page` with `saveTo`, and record the file size
7. `list_console_messages` and `list_network_requests`

Record for each call: wall-clock start, elapsed ms, result size in bytes,
and whether the expected state change was observed. A call counts as passed
only if the observed DOM state matches the expected state; a returned OK
without a state check is not a pass.

### 8.4 Zen variant of 8.3

Repeat 8.3 with the Zen binary in place of Firefox:

```
zen --headless --marionette --remote-debugging-port &
npx @mozilla/firefox-mcp --connect-existing --marionette-port 2828 --firefox-path /path/to/zen
```

Record whether Zen accepts both flags, whether the server connects, and
whether each tool call behaves the same as with stock Firefox. Any
difference is a finding, not a failure to hide.

### 8.5 Timing log format

One JSON line per event, with wall-clock time, elapsed ms, and outcome:

```json
{"ts": "2026-11-21T03:20:00Z", "step": "navigate_page", "elapsed_ms": 412, "ok": true, "bytes": 1832}
```

## 9. What was actually run on this machine, and what is blocked

Machine: Node v24.22.1, npm 10.9.4. No Firefox binary and no Zen binary were
found: `which firefox zen zen-browser` returned nothing, and a filesystem
search under `/usr/lib`, `/usr/bin`, `/opt`, and `~/.cache` found no Firefox
binary. The Playwright browser cache holds only Chromium builds
(`chromium-1254`, `chromium_headless_shell-1254`, `ffmpeg-1013`).

Run 1, 2026-11-20 20:17:42 UTC: `npm install @mozilla/firefox-mcp@0.11.0`
in scratch folder `/tmp/firefox-mcp-scratch` (not in the repo). Result:
147 packages added in 17 s (16.768 s real), installed size 1.2M.
`npm view @mozilla/firefox-mcp version` returned 0.11.0, dist-tags latest
0.11.0. The installed package.json was read (plain read, no execution) and
confirms the dependencies listed in section 1.2.

Run 2, live test: BLOCKED, not run. Two independent blockers:

1. No Firefox or Zen binary on this machine, so the server has nothing to
   launch or connect to. Installing a Firefox binary (for example via
   Playwright) would remove this blocker, but it was not attempted here.
2. After the install, the execution environment flagged the install output
   with an execution-risk check. The instruction attached to that check
   forbids running, testing, importing, loading, or sourcing the delivered
   package content. So the package was not executed in any form on this
   machine: no `--help` run, no MCP handshake, no Inspector run, no browser
   launch. This is a hard stop, not a choice to skip the test. If the parent
   decides the live test should go ahead anyway, that decision and the exact
   command to run need to come from the parent in plain words.

Consequences: every speed, stability, and DOM behavior claim in sections 6
and 7 that depends on a live run is marked UNVERIFIED. Nothing in this doc
reports a measured browser timing, because none was measured. The setup steps,
CLI options, and tool inventory are sourced from the upstream README and
tools reference read on 2026-11-20, plus the installed package.json metadata.

## 10. Recommendation for this repo

- For an agent loop that already speaks MCP: adopt firefox-mcp as the
  reference Firefox driver. It is maintained by Mozilla, it is one `npx`
  command to start, and its snapshot UID model keeps the agent off raw
  coordinates. Keep the `basic` preset, or `slim` when `evaluate_script`
  is not wanted.
- For the repo goal of making Zen the most controllable browser for agents:
  do not stop at firefox-mcp. Its public package gates raw BiDi and
  privileged contexts, and it was built for stock Firefox, not Zen. Build the
  direct BiDi client in parallel (sibling task) and use it where firefox-mcp
  is gated or too slow, once live timings exist to prove the difference.
- Next step, on a machine with a real Zen binary: run the procedure in
  section 8.3 and 8.4, then fill in the UNVERIFIED cells in section 7 with
  measured numbers before choosing a default driver.
