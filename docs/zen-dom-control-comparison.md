# Zen DOM control comparison - 5 tools tested live, 21/11/2026

Measured on the laptop (Omarchy/Hyprland, Zen 1.24.2b/1.24.3b, Firefox 160.0.1)
by Muse (Worker G), Worker B (opencode), Worker C (fcc), clone1, clone2.
All timings are live measurements, not estimates. Wall clock Asia/Ho_Chi_Minh.

## Verdicts at a glance

| Tool | Verdict | Attach to live Zen | Read DOM | Click (verified) | Type | Speed per action |
|---|---|---|---|---|---|---|
| zen-mcp 1.2.3 | WORKS | yes | 3-5ms | 2-3ms, works | 7ms | 2-20ms |
| zenpilot 0.7.0 | WORKS | yes | - | works | - | 439-478ms |
| Selenium + geckodriver 0.36.0 | WORKS (headless) / PARTIAL (windowed) | yes, via --connect-existing | 14ms | 66ms, verified (headless only) | 23ms | 1-80ms |
| Puppeteer 25.18.1 via BiDi | PARTIAL | yes | 4ms | FAILED (counter stayed 0) | not reached | connect 109ms |
| Playwright 1.65.1 moz-firefox | BROKEN | no | n/a | n/a | n/a | n/a |
| firefox-mcp (@mozilla) | NOT TESTED | blocked | blocked | blocked | blocked | blocked |

## 1. zen-mcp 1.2.3 - WORKS (best for live Zen)

Tested by Worker B (opencode) on the live Zen. MCP init 96ms, 20 tools.
List tabs 1-19ms, new tab 111-138ms, read DOM 3-5ms, click 2-3ms,
fill 7ms, JS evaluate 2ms, navigate 803ms. Click verified to work.
Fastest of all tools on the live browser. Needs the same
--remote-debugging-port=9222 the live Zen already has.

## 2. zenpilot 0.7.0 - WORKS (slower, same access)

Tested by Worker B. Works, 439-478ms per call. Same BiDi session as
zen-mcp underneath. Use only if zen-mcp is unavailable; it is ~20x
slower per action for the same operations.

## 3. Selenium + geckodriver 0.36.0 - WORKS headless, PARTIAL windowed

Tested by Muse (Worker G) 07:09-07:20 on 21/11, on real Zen 1.24.2b.
No selenium Python module on the laptop (no pip), so the test drives
geckodriver's WebDriver HTTP API directly with urllib
(tests/zen_selenium_attach.py, no dependency). Clone2's script was the
base; it was NOT run as-is on the live Zen because it navigates the
user's current tab. The safe variant opens a NEW tab and closes it.

Headless temp-profile Zen (port 2830), full pass, total 0.227s:
- create_session 18ms, list_tabs 0.8ms, new tab + goto 79ms,
  read DOM 14ms (heading correct), type 23ms,
  click 66ms with DOM verified ("clicked:zen marionette test"),
  close tab 16ms, delete session 2ms, browser alive after delete.
- All 11 steps ok. This is the first verified Marionette CLICK on Zen.

Windowed temp-profile Zen (port 2829), element interaction FAILS:
- Session/list/read/JS-execute all work (session 4-16ms, list 1ms,
  read 6-15ms). execute_script returns correct DOM state.
- clear/click/get-text fail: "Element could not be scrolled into view".
- Root cause measured (diag3/diag4): the Marionette-opened tab reports
  window.innerWidth/innerHeight = 0, document.hasFocus = false,
  elementFromPoint = null at every point, even though the window is
  mapped, visible, focused, and getBoundingClientRect returns correct
  rects. The tab is "visible" but has NO viewport, so nothing can be
  scrolled into view and innerText is empty. Most likely Zen's own tab
  management never selects the Marionette-opened tab, so Gecko never
  allocates it a viewport. This is a Zen/windowed-environment quirk,
  not a Marionette defect: clone2's headless Firefox run passed all
  interaction steps, and headless Zen passes here.
- Workaround for live windowed Zen: use execute_script for DOM writes
  (works), and a REAL mouse click for clicks (see hybrid below).
  Do NOT rely on Marionette element click on the live windowed Zen
  until the viewport quirk is understood or fixed.

Live Zen (port 2828): BLOCKED by the session leak (section 6).
The test reached the browser and got a proper error, proving the
harness works; the browser refused the session, not the test.

## 4. Puppeteer 25.18.1 via BiDi - PARTIAL, click FAILED

Tested by Muse 04:49 on 21/11 on the live Zen. Connect 109ms, list 111
tabs ok, read DOM 4ms ok. page.click('#count-btn') took 971ms, reported
ok, but the counter stayed 0: the button's click handler never fired.
UNRESOLVED whether this is a BiDi click defect or the same 0x0-viewport
quirk (the test navigated pages[0], the first tab, to the fixture;
that tab may not have been the selected/visible tab). Re-test after
the reboot with an explicitly activated tab, comparing
input.performActions mouse events against element click. Until then,
do NOT trust Puppeteer BiDi click on Zen.

## 5. Playwright 1.65.1 moz-firefox - BROKEN

Tested by Worker C (fcc). Cannot attach to a running Zen, and
launch-only also cannot drive Zen. Dead for this use. Remove from
the todo list as a candidate; keep the note so nobody re-tests it.

## 6. firefox-mcp - NOT TESTED (blocked)

Needs a BiDi session. The live Zen's single remote session is leaked
(see below), so no session could be created. Re-test after the reboot.
It is the official Mozilla MCP server and the most likely long-term
standard, but zen-mcp already works, so firefox-mcp is a backup, not
a blocker.

## 7. THE SESSION LEAK (major finding, blocks everything)

- Symptom: session.new fails "Maximum number of active sessions" on
  BOTH BiDi (9222) and Marionette (2828), even with ZERO TCP
  connections to either port, 4+ minutes after killing the client.
- Cause: a hung node process (PID 122460, tests/puppeteer_bidi.mjs,
  ran 1h51m from the overlay worker's 04:58 run) held the one remote
  session. Killing the client does NOT free the session server-side.
- Proof the cap is SHARED across protocols: geckodriver on the live
  Zen got the same "Maximum number of active sessions" from Marionette
  at 07:09, while the leak was a BiDi session. One remote session
  TOTAL per Zen instance, not one per protocol.
- Only a Zen restart clears it. The user reboots tomorrow morning.
- Consequence: every BiDi/Marionette client MUST delete its session
  in a finally block, and a single session manager must own the one
  session (scripts/zen_dom.py). A watchdog must kill hung remote
  clients. No parallel remote-control workers, ever, on the live Zen.

## 8. DOM vs screenshot/mouse (1.2.2)

- DOM read: 3-14ms. Screenshot + vision observe: seconds (observe
  round trip is the dominant cost; the think-observe-think loop is
  87.8% of task time per the 10x review). DOM is 100x+ faster for
  reading state.
- DOM locate: exact rects (getBoundingClientRect), zero vision error.
  Vision grounding measured 17/29 = 58.6% on a known-point grid
  (Phase 2.1 E2). DOM locate removes the entire miss class.
- DOM click: does NOT equal a real mouse click. BiDi click failed to
  fire the handler (04:49). Marionette click works headless but fails
  on windowed Zen (0x0 viewport). The Polygon Browse button needs a
  real hover-then-click. DOM alone cannot do that.
- Conclusion: DOM for LOCATE and READ, real mouse for CLICK. Never
  DOM click on a control whose behavior depends on hover or trusted
  mouse events.

## 9. Recommendation (1.2.3, 1.2.4): hybrid, zen-mcp first

Primary: **zen-mcp 1.2.3** for all DOM work on the live Zen
(list/read/evaluate/navigate). It is the fastest verified path
(2-20ms) and its click works on the live browser.

Fallback: **Selenium + geckodriver** for headless/off-screen work
(full pass, 0.23s total) and for anything needing the standard
WebDriver API. Not for clicks on the live windowed Zen.

Clicks on the live Zen: **DOM rect + real mouse click** through the
existing computer-use driver (cu.py pointer, verified exact to <1px).
Never trust a DOM/BiDi click to fire a handler; always verify the DOM
changed after the click, and fall back to the real mouse.

Session discipline: **scripts/zen_dom.py** owns the single remote
session (one at a time, file lock, session.delete in finally, hung
client watchdog). No other code opens a BiDi/Marionette session.

Breakthrough direction (for the 10x question): the fastest path is
not a faster tool, it is FEWER round trips. Batching (Microsoft HCU:
up to 64 actions per call) plus diff-only observation plus DOM locate
is the lever, not a new driver. The driver is already 2-20ms; the
cost is the think-observe loop around it. See redteam verdict
docs/redteam-council-20261121/VERDICT.md section 5.

## 10. What is still blocked (needs the reboot)

- firefox-mcp test (1.1.2), Puppeteer click re-test (1.1.1),
  Selenium on the live Zen (1.1.3), re-test on a real task (1.3.2),
  .desktop verify after reboot (1.3.3).
- E2 phase B (animated backdrop flicker test) also needs the reboot
  (BiDi session leak blocks the animated tab).
- All of these are recorded as BLOCKED, not skipped. Run them first
  after the user reboots.
