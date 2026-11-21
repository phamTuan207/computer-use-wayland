# WebExtension plus native messaging bridge

DOM control of the user's own running Firefox or Zen, without a remote
debugging port. A small extension lives inside the real browser session
and talks to a local native host over stdin/stdout; the host relays
agent commands over a loopback TCP port. This is the bridge that can
reach the tabs the user already has open, which the BiDi path in
`scripts/zen_cli.py` deliberately cannot: the user's Zen runs without
a debug port, so BiDi only ever sees a dedicated session.

## Architecture

```
agent (this repo, or any MCP client)
  -- TCP, one JSON object per line, 127.0.0.1:18711 -->
native host (host/cu_bridge_host.py, stdlib Python)
  -- native messaging, framed JSON on stdin/stdout -->
extension background script (extension/background.js, MV2, persistent)
  -- runtime messaging -->
content script (extension/content.js) in the target tab
  -- DOM APIs -->
page
```

The browser launches the host when the extension calls
`runtime.connectNative("computer_use_bridge")` and kills it when the
port closes. The host's TCP server therefore only lives while the
extension holds the port open. The host never touches the network
beyond loopback, and it never spawns a browser.

## Protocol

Agent to host, one JSON object per line over TCP:

| op | fields | result |
| --- | --- | --- |
| host.ping | id | {pong: true}, answered by the host, no browser needed |
| host.status | id | {host, pending, uptime_s, timeouts, errors} |
| ping | id | {pong: true, native_deaths}, answered in the background script |
| listTabs | id | [{id, index, url, title, active}] |
| activate | id, tabId | {activated: tabId} |
| navigate | id, tabId, url | {navigated: url} |
| snapshot | id, tabId, maxNodes | {title, url, nodes, truncated} |
| click | id, tabId, selector | {clicked, tag, text} |
| type | id, tabId, selector, text | {typed, tag, length} |
| evaluate | id, tabId, expression | {value, type} |
| scroll | id, tabId, selector?, x?, y?, behavior? | {scrolled, scrollX, scrollY, rect?} |
| hover | id, tabId, selector | {hovered, tag, text, rect} |
| select | id, tabId, selector, value | {selected, value, text} |
| upload | id, tabId, selector, filename, mime, data | {uploaded, filename, size, type} |
| waitFor | id, tabId, selector, timeoutMs | {found, tag, text, waited_ms, rect} |

Every reply carries the same `id`, `ok`, `elapsed_ms` measured inside
the extension, and `host_elapsed_ms` measured in the host. Request ids
are positive integers; id -1 is reserved for the background script's
own host.ping smoke check at connect time.

Error handling: the background script gives up on a tab that does not
reply within 25 s and reports the tab id and op in the error; the host
gives up after `CU_BRIDGE_TIMEOUT_S` (default 30 s), logs the timeout
with a timestamp, and counts it in `host.status`. If the native host
dies, the browser closes the port, the background script counts the
death, logs it with a timestamp, and reconnects with backoff
(1s, 2s, 5s, 10s, 30s), which relaunches the host. Every host log
line carries a UTC timestamp.

Native messaging framing, per MDN: each message is JSON, UTF-8
encoded, prefixed with a 32-bit unsigned length in native byte order.
Host to extension messages must stay under 1 MB; the host rejects
larger agent requests before forwarding. Extension to host messages
may be up to 4 GB by spec; this host refuses frames over 16 MB.

## Why Manifest V2

The background page must be persistent, because the native port dies
with it. Firefox MV3 uses a non-persistent event page
(`background.scripts`, no service worker support in Firefox), which
would drop the port whenever the page is unloaded. Firefox MV2 is
still fully supported with no deprecation timeline (Mozilla promised
at least 12 months notice if that ever changes), and the same project
that drives this choice, firefox-mcp by dh1011, uses MV2 for exactly
this reason: only a persistent background page keeps the connection
to the server open.

## Files

- `extension/manifest.json`: MV2, permissions `nativeMessaging`,
  `tabs`, `<all_urls>`, explicit id `cu-bridge@example.local`.
- `extension/background.js`: holds the native port, reconnects with
  backoff (1s, 2s, 5s, 10s, 30s), counts native host deaths, routes
  commands to tabs, gives up on a silent tab after 25 s.
- `extension/content.js`: snapshot, click, type, evaluate, scroll,
  hover, select, upload (base64 file data rebuilt as a File object),
  waitFor (MutationObserver plus timeout).
- `content_node_test.mjs`: Node harness that runs the real content.js
  against a fake DOM and checks all 15 content ops, no browser needed.
- `host/cu_bridge_host.py`: framing plus loopback TCP relay, stdlib
  only. Port from `CU_BRIDGE_PORT` (default 18711), per-request
  timeout from `CU_BRIDGE_TIMEOUT_S` (default 30). Logs every error
  and timeout with a UTC timestamp, counts them in `host.status`.
- `host/cu_bridge_client.py`: minimal manual client with wall-clock
  and elapsed timing on stderr.
- `host/computer_use_bridge.json.template`: host manifest template.
- `install.py`: writes the host manifest to
  `~/.mozilla/native-messaging-hosts/computer_use_bridge.json` and
  makes the host executable. Also `--check`, `--uninstall`, `--sign`
  (web-ext build), and `--policies` (force-install via policies.json).
- `../test_webext_native_bridge.py`: 16 unit tests, no browser needed.

## Setup on the laptop

1. From this folder, install the host manifest:
   `python3 install.py`
   This writes `~/.mozilla/native-messaging-hosts/`.
   Verify it with `python3 install.py --check`.
   Zen reads the same `~/.mozilla` registration as Firefox. Do not
   write a copy under `~/.zen`: other projects tried that and it did
   not work, and the fix was to move the manifest back to `.mozilla`.
   Flatpak Zen is the exception: the manifest and the host must also
   be visible inside the sandbox.
2. Load the extension temporarily: open
   `about:debugging#/runtime/this-firefox`, choose Load Temporary
   Add-on, pick `extension/manifest.json`. Temporary add-ons last
   until Firefox restarts.
   For a permanent install, sign the extension (`python3 install.py
   --sign`, then the printed sign step with AMO keys) and force-install
   it with `python3 install.py --policies <browser-dir> --xpi
   <signed.xpi>`. Full steps are in `docs/webext-bridge-install.md`.
3. Open the background console and confirm
   `[cu-bridge] connected to native host computer_use_bridge`.
4. From a terminal, list tabs:
   `python3 host/cu_bridge_client.py --port 18711 '{"id": 1, "op": "listTabs"}'`

Permanent install needs signing or a build that allows unsigned
add-ons: `web-ext sign --channel unlisted` for a signed unlisted
build, or Nightly / Developer Edition with
`xpinstall.signatures.required` set to false. Neither path is
verified here.

## What it can and cannot do

Can:
- List, activate, and navigate tabs in the user's real session.
- Read a bounded snapshot of interactive elements (tag, text, rect,
  value, href) without screenshots.
- Click and type through DOM APIs, and evaluate expressions in the
  page's isolated content-script world.
- Scroll to an element or a window position, hover an element, pick a
  select option by value or visible text, upload a file (bytes sent
  as base64, rebuilt as a File object), and wait for an element to
  appear with a timeout.

Cannot:
- Send trusted input. `element.click()` and dispatched input events
  are synthetic; pages that check `event.isTrusted` see them as
  untrusted. Real keystrokes and pointer input need the OS-level
  keyboard and pointer path in this repo, not this bridge.
- Attach a debugger, answer dialogs, or take screenshots. The
  extension API has no debugger surface in Firefox.
- Read pages the content script cannot run in (internal `about:`
  pages, `addons.mozilla.org` restricted pages, some privileged
  pages). Those fail with a clear error, not silently.
- Move more than 1 MB in a single host to extension reply. Large
  snapshots must be paged with `maxNodes`.
- Survive a browser restart as a temporary add-on. Reinstall after
  restart, or use a signed build.

Security notes: the TCP port binds loopback only and has no
authentication, so any local process can drive the browser through
it. That is the same trust model as the loopback BiDi port in
`scripts/zen_cli.py`. Only run it on a machine where local processes
are trusted, and do not forward the port.

## Comparison

| Path | Reaches the user's real tabs | Needs a debug port | Trusted input | Setup burden | Liveness |
| --- | --- | --- | --- | --- | --- |
| Puppeteer BiDi (`scripts/zen_cli.py`, repo) | No, dedicated session only | Yes, dedicated session | Yes, BiDi input actions | Low, stdlib wrapper | Verified live on the laptop, Zen 1.24.2b |
| Mozilla firefox-mcp (ex firefox-devtools-mcp, npm `@mozilla/firefox-mcp`) | No, dedicated Firefox | No, launches its own Firefox | Yes, through BiDi and Selenium | Low, npx | Upstream maintained, renamed in v0.11.0 |
| firefox-mcp by dh1011 (extension plus daemon) | Yes, own profile tabs | No | No, DOM only | Medium, build plus sideload plus pairing code | Extension plus WebSocket daemon, needs its own auth |
| This bridge (extension plus native messaging) | Yes, own profile tabs | No | No, DOM only | Medium, install manifest plus sideload or sign | Host lives only while the extension holds the port |

In short: BiDi paths are faster and give trusted input, but they
cannot see the user's session. Extension paths can, but they are
limited to DOM-level actions and need an install step the BiDi paths
do not. This bridge and firefox-mcp by dh1011 solve the same
reach problem; the bridge swaps the WebSocket daemon for native
messaging, which removes the pairing ceremony and the always-on
daemon (trust comes from the host manifest file on disk and the
extension id allowlist instead), at the cost of the host only running
while the browser holds the port.

## Verification status

Verified on this machine (no Firefox or Zen binary, no `~/.mozilla`
profile here):
- `python3 tests/test_webext_native_bridge.py`: 16 tests, all pass,
  8.390 seconds wall-clock (run 2026-11-21T08:24:52Z to 08:25:00Z).
  A fake extension stands in for the browser and proves framing,
  full relay, the 1 MB outbound limit, bad-frame survival, clean
  shutdown on stdin EOF, forwarding of all 5 new ops, and the
  install check, uninstall, and policies round trips against a
  temporary home directory.
- `node tests/webext-native-bridge/content_node_test.mjs`: 16 checks,
  all pass, 0.570 seconds wall-clock. Runs the real content.js
  against a fake DOM and proves snapshot, click, type (input and
  textarea), scroll (element and window), hover, select, upload
  (10 byte file rebuilt from base64), waitFor (immediate, on
  mutation, and timeout), evaluate, and the missing-element and
  bad-option error paths.
- Relay timing with the fake extension: 1.1-1.2 ms elapsed for a
  snapshot round trip on loopback. That is host-only timing; real
  browser timing will be larger and must be measured on the laptop.
- `node --check` passes for both extension scripts and the harness;
  `py_compile` passes for all Python files; both manifests parse as
  JSON.

NOT verified, needs the laptop with a real Zen:
- Extension loads and connects to the host (step 3 above).
- listTabs, snapshot, click, type, evaluate, scroll, hover, select,
  upload, waitFor against a real tab, with wall-clock and elapsed
  timing per op.
- Host manifest install on the laptop, including the Zen
  `~/.mozilla` registration, and `install.py --check`.
- Permanent install path (signed unlisted build or Nightly), and the
  policies.json force-install path.

Sources checked 2026-11-21: MDN Native messaging and Native
manifests pages; Mozilla Add-ons blog on MV2 support; firefox-mcp
by dh1011 (extension plus daemon, MV2, pairing code); Mozilla
firefox-mcp repository and v0.11.0 release note (rename from
firefox-devtools-mcp, BiDi through Selenium); Zen native messaging
path reports (caelestia fix moving the manifest from `.zen` to
`.mozilla`, codex-firefox-bridge install notes).
