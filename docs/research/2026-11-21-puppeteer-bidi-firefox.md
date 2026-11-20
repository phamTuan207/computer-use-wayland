# Puppeteer over WebDriver BiDi for Firefox and Zen

Reviewed: 2026-11-21. Sources were read as search results and official docs, not
run against a live Firefox or Zen here, because this machine has no Firefox or
Zen binary. All timings below are real runs on this machine, and the Firefox
and Zen behaviour is marked UNVERIFIED where no local browser existed to test it.

## Decision in one paragraph

Puppeteer can drive Firefox over WebDriver BiDi, a standard bidirectional
protocol, with the same high level API it uses for Chrome over CDP. For a
long lived Zen process, the intended path is to attach to the already running
browser with `puppeteer.connect` and `protocol: 'webDriverBiDi'`, not to launch
a fresh browser per task. That keeps the user session, tabs, and extensions
intact, and it avoids screenshots and pointer clicks for DOM work.

## Sources

- Puppeteer WebDriver BiDi support: https://pptr.dev/webdriver-bidi
- Puppeteer with Firefox, Chrome for Developers: https://developer.chrome.com/blog/firefox-support-in-puppeteer-with-webdriver-bidi
- Mozilla Hacks, Puppeteer support for WebDriver BiDi: https://hacks.mozilla.org/2023/12/puppeteer-webdriver-bidi/
- W3C WebDriver BiDi specification: https://w3c.github.io/webdriver-bidi/
- Mozilla bug 1943416, communicating with a Marionette session via BiDi: https://bugzilla.mozilla.org/show_bug.cgi?id=1943416
- Mozilla WebDriver project page: https://wiki.mozilla.org/WebDriver

## What the protocol is

WebDriver BiDi extends classic WebDriver with a bidirectional WebSocket
channel. Commands go one way, events such as console logs, network events,
and navigation come back the other way, on the same connection. It combines
the low level control of CDP with a cross browser standard, so one client can
drive Chrome and Firefox with the same calls.

Puppeteer added BiDi support in v21.6.0. From Puppeteer 23 and Firefox 129
it is production ready for Firefox. When launching Firefox, Puppeteer uses
WebDriver BiDi by default. When launching Chrome, CDP is still the default,
and BiDi must be requested explicitly. CDP support in Firefox was deprecated
from Firefox 129.

## Bug 1943416: attaching to a running session

Bug 1943416 is RESOLVED FIXED. It proved that a Marionette session can be
reached a second time over BiDi. The test in the bug opens Firefox with
Marionette, appends `--remote-debugging-port`, starts a session, then a
Puppeteer script connects with this exact call:

```js
const browser = await puppeteer.connect({
  browserWSEndpoint: 'ws://127.0.0.1:9222/session',
  protocol: 'webDriverBiDi',
});
const page = await browser.newPage();
await page.goto('https://www.example.com');
const element = await page.locator('h1').waitHandle();
const title_text = await page.evaluate((el) => el.textContent, element);
await browser.disconnect();
```

That is the pattern `tests/puppeteer_bidi.mjs` follows. Note that
`browser.disconnect()` detaches without closing the browser, which is what a
long lived Zen session needs. `browser.close()` would kill the browser.

## How to start Firefox or Zen with remote BiDi

UNVERIFIED on this machine. The flags below come from the sources above and
from the Firefox Remote Protocol docs, not from a local run.

```sh
firefox --remote-debugging-port=9222 --profile /tmp/bidi-profile
zen --remote-debugging-port=9222 --profile /tmp/bidi-profile
```

The BiDi endpoint is then `ws://127.0.0.1:9222/session`. Use a throwaway
profile for tests, never the daily profile, so a test cannot touch real tabs.
Zen is a Firefox fork, so it should inherit the same Remote Protocol
implementation, but its exact flag handling and default preferences are
UNVERIFIED here and must be checked on a machine with Zen installed.

## How to run the test in this repo

```sh
mkdir -p /tmp/bidi-scratch && cd /tmp/bidi-scratch
npm init -y && npm install puppeteer-core@24
PUPPETEER_CORE_PATH=/tmp/bidi-scratch/node_modules/puppeteer-core \
  node tests/puppeteer_bidi.mjs
```

Options: `--endpoint ws://127.0.0.1:9222/session`, `--url URL`,
`--timeout-ms 30000`, `--help`. With no `--url`, the script serves
`tests/bidi_fixture.html` on a loopback HTTP server and drives that page.

The script does, in order: connect, list tabs, open the fixture, read the DOM
(title, heading, input value, counter), click the counter button and verify
it becomes 1, type `bidi-test` into the input and verify the value, list tabs
again. Each step logs one JSON line with wall clock time and elapsed
milliseconds, and the run ends with a summary line. Exit 0 on success, 2 on
a failed run, 3 when puppeteer-core is not installed.

`tests/bidi_smoke.mjs` checks the script with no browser at all: `--help`
exits 0, and an unreachable endpoint fails with a structured JSON error and
exit code 2. Run it with `node tests/bidi_smoke.mjs`.

## What was verified on this machine, with real timings

All runs on 2026-11-20, Node v24.22.1, repo HEAD 6f055e1.

- puppeteer-core 24.43.1 installs from npm in 12.565 s wall clock, 81 packages.
- `node tests/bidi_smoke.mjs` passes in 0.508 s wall clock. The unreachable
  endpoint check (`ws://127.0.0.1:1/session`, timeout 5000 ms) fails in
  307 ms with `connect ECONNREFUSED 127.0.0.1:1` and exit code 2.
- `node tests/puppeteer_bidi.mjs` against `ws://127.0.0.1:9222/session`
  fails in 145 ms total with `connect ECONNREFUSED 127.0.0.1:9222` and exit
  code 2. This is the expected result here, because nothing listens on
  port 9222.
- No Firefox binary exists on this machine. `which firefox zen zen-browser`
  finds nothing, and there is no Firefox directory under `/usr/lib` or
  `/opt`. Only Playwright Chromium 1254 is cached, which is a different
  browser and a different protocol, so it was not used as a stand in.

## What is UNVERIFIED

- The full happy path: connect, list tabs, read DOM, click, type, and the
  per operation timings on a real Firefox or Zen. No local browser existed.
- That Zen accepts `--remote-debugging-port=9222` and serves BiDi at
  `/session` exactly like Firefox. Zen is a fork, so this is likely, not
  proven.
- Whether an already open Zen tab can be listed and driven without disturbing
  the user session, and whether `browser.disconnect()` leaves Zen usable.
- Performance numbers for DOM operations over BiDi on Zen. Do not quote any
  per operation millisecond figure for Zen until a real run produces it.

## Known gaps in Puppeteer over BiDi

From the Puppeteer docs and Mozilla posts, these are still limited or
missing over WebDriver BiDi compared with Chrome over CDP: cookie store
access, network request interception, some emulation features, and
permissions. Unsupported operations throw `UnsupportedOperation`. For
Firefox, cookie access was the only missing feature compared with the old
Firefox CDP implementation. The Puppeteer test suite passed about 55 percent
of tests over BiDi on Firefox at the time of the Chrome blog post, and
about 68 percent on Chrome. Those are the authors reported figures, not
measurements from this repo.

## What this means for the Zen goal

For DOM-first control of Zen, Puppeteer over BiDi is the most direct path
that needs no custom browser build: one WebSocket, standard protocol, same
API as the existing Chromium CDP work in this repo. The open risks are all
on the Zen side, not the protocol side: confirming the endpoint exists on a
real Zen build, confirming attach does not disturb the session, and measuring
real latencies. The next step is to run `tests/puppeteer_bidi.mjs` on a
machine with Zen installed and record the timed log, then compare it with
the other approaches in the comparison doc.
