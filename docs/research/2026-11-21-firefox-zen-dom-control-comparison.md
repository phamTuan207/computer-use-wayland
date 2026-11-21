# Comparing ways to drive Firefox and Zen through the DOM

Date: 2026-11-21. Machine: this sandbox, Node v24.22.1, npm 10.9.4, repo
HEAD 6f055e1. No Firefox or Zen binary exists on this machine, so every
live-browser result below is marked UNVERIFIED. All timings quoted are real
runs on this machine, and nothing here is a measured browser timing.

## The four paths

1. Direct Puppeteer over WebDriver BiDi. One WebSocket to the browser.
   See `docs/research/2026-11-21-puppeteer-bidi-firefox.md` and
   `tests/puppeteer_bidi.mjs`.
2. Mozilla firefox-mcp, npm `@mozilla/firefox-mcp` v0.11.0. An MCP server
   that drives Firefox through Selenium and geckodriver over BiDi.
   See `docs/research/2026-11-21-firefox-mcp.md`.
3. WebExtension plus native messaging bridge, the prototype in this repo.
   An MV2 extension in the real session talks to a local host over stdio,
   and the host relays agent commands over loopback TCP.
   See `tests/webext-native-bridge/README.md`.
4. firefox-mcp by dh1011. Extension plus WebSocket daemon, researched
   only, not built here. It reaches the user's own tabs but cannot send
   trusted input, attach a debugger, or answer dialogs.

## Comparison

| Axis | Puppeteer BiDi | Mozilla firefox-mcp | WebExtension bridge | dh1011 firefox-mcp |
| --- | --- | --- | --- | --- |
| Reaches the user's real tabs | Only if the browser was started with a remote debugging port, attach with `puppeteer.connect`. UNVERIFIED on Zen. | Connect-existing mode only, Marionette plus remote debugging port flags. UNVERIFIED on Zen. | Yes, the extension lives in the real session, no debug port. Browser side UNVERIFIED here. | Yes, own profile tabs. |
| Needs a debug port | Yes for attach, `ws://127.0.0.1:9222/session`. | No for its own launch, yes for connect-existing. | No. | No. |
| Trusted input | Yes, BiDi input actions. UNVERIFIED on Zen. | Yes, through BiDi and Selenium. UNVERIFIED. | No, synthetic DOM events, pages checking `event.isTrusted` see them as untrusted. | No, DOM only. |
| Speed | One WebSocket hop, lowest per-action latency of the BiDi paths in principle. No live timing measured. | Extra hops: MCP stdio, Selenium, geckodriver, BiDi, plus a snapshot round trip per tool call. Expected slower per action, by an unmeasured amount. UNVERIFIED. | Host-only relay round trip measured at 1.1-1.4 ms on loopback. Real browser timing will be larger and is UNVERIFIED. | Not measured here. |
| Stability | Depends on the client: reconnect, session recovery, and BiDi version skew are yours to own. BiDi coverage still grows, some ops missing across versions. | Maintained by Mozilla, 589 stars, 440 commits, 45 releases at time of reading. Known modes: Firefox not found, slow first run, stale UIDs after navigation, Marionette one client at a time with 1800 s idle timeout. | Host lives only while the extension holds the native port. Reconnect backoff 1s, 2s, 5s, 10s, 30s. MV2 persistent background required. | Extension plus daemon, needs its own auth pairing. |
| DOM depth | Full BiDi surface Firefox implements, raw commands included, direct node access. Gaps: cookie access, network interception, some emulation, permissions. Unsupported ops throw `UnsupportedOperation`. | Deep for page content: snapshot UIDs, click, fill, hover, drag, type, press key, upload, `evaluate_script`, network, console, profiler, debugger, screencast. Gated in the public package: no raw BiDi, no privileged chrome contexts, no runtime pref get/set, no restart with a new config. | Snapshot, click, type, evaluate in the page's isolated content-script world. No debugger, no dialog handling, no screenshots, no `about:` or restricted pages, 1 MB reply cap so snapshots must page with `maxNodes`. | DOM only, same class of limits as the bridge. |
| Setup friction | Higher: write the client, manage the WebSocket, session, context tracking, error recovery. No MCP config, no Selenium or geckodriver. | Lowest to start: one `npx` command, no build, no code. Needs Node 20.19+ and a local Firefox 100+. | Medium: install host manifest, load extension temporarily or sign it for permanent install. | Medium: build plus sideload plus pairing code. |
| Custom build needed | Everything: client, timing harness, snapshot helpers, input helpers, recovery. Nothing gated. | For this repo's goal: a Zen connect-existing test, a timing harness around MCP tool calls, anything needing raw BiDi or chrome contexts. If the agent loop already speaks MCP, almost nothing else. | The prototype is built. Still needed: the browser-side test on a real Zen, and the permanent install path (signed unlisted build or Nightly). | Not built here. |
| Status on this machine | Smoke tests pass, live run fails as expected with no browser listening. | Installed, not executed. See the block below. | 9 unit tests pass with a fake extension, no browser. | Researched only. |

## What was actually measured on this machine

| Run | Result | Wall clock |
| --- | --- | --- |
| `npm install puppeteer-core@24.43.1` in scratch | 81 packages installed | 12.565 s |
| `node tests/bidi_smoke.mjs` | Pass, `--help` exit 0, unreachable endpoint fails in 241-307 ms with ECONNREFUSED, exit 2 | 0.451-0.508 s |
| `node tests/puppeteer_bidi.mjs` vs `ws://127.0.0.1:9222/session` | Fails in 145 ms with ECONNREFUSED, exit 2, structured JSON log. Expected, nothing listens on 9222. | 0.145 s |
| `npm install @mozilla/firefox-mcp@0.11.0` in scratch | 147 packages, 1.2M on disk | 16.768 s |
| `python3 tests/test_webext_native_bridge.py` | 9 tests, all pass, fake extension proves framing, relay, 1 MB outbound limit, bad-frame survival, clean exit on stdin EOF | 5.450-5.556 s |
| Bridge relay round trip, fake extension | 1.1-1.4 ms elapsed on loopback, host-only timing | per op |

No per-operation millisecond figure for any real Firefox or Zen action is
claimed anywhere in this repo. The cells above are the only timings.

## What is blocked or unverified

- No Firefox or Zen binary on this machine, so the full happy path for
  every approach is unverified: connect, list tabs, read DOM, click, type,
  and per-operation timings on a real Zen.
- Whether Zen accepts `--remote-debugging-port=9222` and serves BiDi at
  `/session` exactly like Firefox, and whether attach disturbs the user
  session. Zen is a Firefox fork, so this is likely, not proven.
- Mozilla firefox-mcp live run is blocked here by a hard stop: after the
  install, the execution environment flagged the install output and
  forbade running, testing, importing, loading, or sourcing the delivered
  package content. The package was not executed in any form, so no
  `--help`, no MCP handshake, no Inspector run, no browser launch.
  All speed numbers for it are UNVERIFIED, and Zen compatibility is
  UNVERIFIED. Correction, checked 2026-11-21: CVE-2026-7064 does not
  apply to firefox-mcp. It belongs to AgentDeskAI/browser-tools-mcp,
  a different, now discontinued project, so it is not a blocker for
  adopting firefox-mcp.
- WebExtension bridge browser side: extension load and native connect,
  `listTabs`, `snapshot`, `click`, `type`, `evaluate` against a real
  tab with per-op timing, the `~/.mozilla` host manifest install, and
  the permanent install path. Temporary add-on load lasts until the
  browser restarts; permanent install needs AMO signing (unlisted) or
  Nightly or Developer Edition with signatures off.

## Recommendation

No single path covers the goal. Use two paths together:

- Puppeteer over BiDi for a dedicated Zen session: fastest, trusted
  input, full protocol, lowest latency, no custom browser build.
  First prove the endpoint exists on a real Zen and measure it with
  `tests/puppeteer_bidi.mjs`.
- The WebExtension bridge for the user's real tabs: the only path here
  that reaches tabs already open without a debug port. Accept DOM-only
  actions and the install step, and keep OS-level input for trusted
  keystrokes and pointer input.
- Mozilla firefox-mcp when an agent already speaks MCP and needs a
  maintained, safe-by-default way to browse and debug with Firefox.
  Accept the extra latency and the gated protocol surface. CVE-2026-7064
  does not apply to this project, see the correction above.

## Next steps on a machine with Zen

1. Run `tests/puppeteer_bidi.mjs` against a Zen started with
   `--remote-debugging-port=9222` on a throwaway profile, record the
   timed JSON log, and fill in the UNVERIFIED cells above.
2. Run the firefox-mcp test procedure in
   `docs/research/2026-11-21-firefox-mcp.md` section 8, including the
   Zen variant, and record timings in the same log format.
3. Load the bridge extension in Zen, run `listTabs`, `snapshot`,
   `click`, `type`, `evaluate` against a real tab, and record per-op
   wall-clock and elapsed timing.
4. Decide the permanent install path for the bridge, signed unlisted
   build or Nightly, and record which one was chosen.
