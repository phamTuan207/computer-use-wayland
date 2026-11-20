# clone1 status

Date: 2026-11-21. Agent: clone1. Repo HEAD at start of work: 6f055e1.
Scope: research and test code for driving Firefox and Zen through the DOM,
for the coordinator to run on the laptop with a real Zen.

## Setup done

- GitHub CLI 2.102.0 installed, logged in, token scopes: gist, read:org,
  repo, workflow. Repo cloned, HEAD 6f055e1.
- Rules followed: no personal info in any repo file, no long dash
  characters in new files, no ydotool, real timings only, everything
  unverified is marked UNVERIFIED.

## Delivered in this push

- `tests/puppeteer_bidi.mjs`, `tests/bidi_smoke.mjs`,
  `tests/bidi_fixture.html`: Puppeteer over WebDriver BiDi test. Connects
  to `ws://127.0.0.1:9222/session` with protocol `webDriverBiDi`, lists
  tabs, reads DOM, clicks, types, logs one JSON line per step with
  wall-clock time and elapsed ms. Follows bug 1943416, which is RESOLVED
  FIXED and proves the attach-to-running-session pattern.
- `docs/research/2026-11-21-puppeteer-bidi-firefox.md`: BiDi research,
  how to start Firefox or Zen with `--remote-debugging-port=9222`, known
  gaps (cookie access, network interception, some emulation,
  permissions).
- `docs/research/2026-11-21-firefox-mcp.md`: Mozilla firefox-mcp
  v0.11.0, npm `@mozilla/firefox-mcp`, full setup guide, tool inventory,
  comparison with direct Puppeteer BiDi, test procedure.
- `tests/webext-native-bridge/`, `tests/test_webext_native_bridge.py`:
  WebExtension plus native messaging prototype. MV2 extension, stdlib
  Python host, loopback TCP relay on 127.0.0.1:18711, ops listTabs,
  snapshot, click, type, evaluate, with timing on every reply.
- `docs/research/2026-11-21-firefox-zen-dom-control-comparison.md`:
  comparison of all four paths (direct Puppeteer BiDi, Mozilla
  firefox-mcp, WebExtension bridge, dh1011 firefox-mcp), with speed,
  stability, DOM depth, setup friction, and what needs custom building.

## Verified on this machine, with real timings

- puppeteer-core 24.43.1 install in scratch: 81 packages, 12.565 s.
- `node tests/bidi_smoke.mjs`: pass, 0.451-0.508 s. Unreachable endpoint
  fails in 241-307 ms, exit 2.
- `node tests/puppeteer_bidi.mjs` with no browser listening: fails in
  145 ms with ECONNREFUSED on 127.0.0.1:9222, exit 2. Expected here.
- `@mozilla/firefox-mcp@0.11.0` install in scratch: 147 packages, 1.2M
  on disk, 16.768 s.
- `python3 tests/test_webext_native_bridge.py`: 9 tests, all pass,
  5.450-5.556 s. Relay round trip with a fake extension: 1.1-1.4 ms
  on loopback, host-only timing.
- `node --check` passes on the BiDi and extension scripts,
  `py_compile` passes on the Python files.
- Dash scan: no long dash characters in any new file. No personal info
  in any new file.

## Blocked and unverified, needs the laptop

- No Firefox or Zen binary on this machine, so no live browser run was
  possible for any path. All per-operation timings on a real Zen are
  UNVERIFIED. Do not quote any Zen millisecond figure from this push.
- Whether Zen accepts `--remote-debugging-port=9222` and serves BiDi at
  `/session` like Firefox, and whether attach disturbs the user session.
- Mozilla firefox-mcp live run is blocked here by a hard stop: after
  the install, the execution environment flagged the install output and
  forbade running, testing, importing, loading, or sourcing the
  delivered package content. The package was not executed in any form.
  Its speed numbers, Zen compatibility, and the fix status of reported
  CVE-2026-7064 are all UNVERIFIED. Re-check the CVE against the
  upstream changelog before adopting it.
- WebExtension bridge browser side: extension load and native connect,
  listTabs, snapshot, click, type, evaluate against a real tab with
  per-op timing, the `~/.mozilla` host manifest install, and the
  permanent install path.

## Recommendation

Use two paths together: Puppeteer over BiDi for a dedicated Zen session
(fastest, trusted input, full protocol), and the WebExtension bridge
for the user's real tabs (the only path here that reaches tabs already
open without a debug port). Mozilla firefox-mcp fits when an agent
already speaks MCP and needs a maintained, safe-by-default way to
browse with Firefox.

## Next steps for the coordinator

1. Run `tests/puppeteer_bidi.mjs` against Zen on a throwaway profile
   and record the timed JSON log.
2. Run the firefox-mcp test procedure in
   `docs/research/2026-11-21-firefox-mcp.md` section 8, including the
   Zen variant.
3. Load the bridge extension in Zen and run listTabs, snapshot, click,
   type, evaluate against a real tab with per-op timing.
4. Fill in the UNVERIFIED cells in the comparison doc with the measured
   numbers, and decide the permanent install path for the bridge.
