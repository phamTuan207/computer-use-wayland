# Fast DOM/a11y grounding for Firefox/Zen, batch 7 task 2

By clone2, 2026-11-22. Independent second opinion alongside the
coordinator's crawl team. Every measured number in this document was
measured by clone2 on this machine, with the machine, browser, date
and raw log named. Every web claim carries its source and date.
Anything not run here is labelled UNVERIFIED.

## 0. Verdict first

Stop reading screenshots to find buttons. The DOM already knows where
every element is, to the sub-pixel, in about 0.01 to 0.02 seconds for
a whole page. One `getBoundingClientRect` sweep over all interactive
elements gives 66 rects in a median 0.019 s (Marionette) or about
0.006 to 0.011 s (BiDi), and the two protocols agree to within
floating point noise (max delta 5.7e-14 px). That one snapshot can
drive 5 real pointer clicks, all 5 landing, verified by one cheap
DOM read in about 0.01 s, with no second screenshot and no second
observation of the page.

The design that follows from the measurements:

- BiDi primary for grounding and DOM actions: fastest rect read,
  fastest DOM clicks, single digit millisecond session start.
- Marionette only where real input events are needed: real pointer
  clicks cost about 0.30 s each through W3C actions, DOM clicks cost
  about 0.001 s each but skip the input pipeline.
- Selenium 4.53 accessibility snapshots, new 2026-11-17, give the
  a11y tree (role, name, states) in about 0.02 s on the same page,
  in both Classic and BiDi sessions. Semantics from the a11y tree,
  geometry from the DOM rect, in one design.
- CDP is dead on Firefox and Zen: removed in Firefox 141, the
  /json endpoints return 404. Do not build on it.
- AT-SPI stays the native desktop path, not the browser path. It was
  not runnable on this VM (no daemons, no pyatspi), so its numbers
  here are other people's, labelled as such.
- One hard constraint the bench proved three times: Firefox 160
  allows exactly one active remote session per browser instance,
  across protocols. A Marionette session blocks a BiDi session with
  "Maximum number of active sessions". Never design a flow that
  needs both at once on one browser.

## 1. What was measured, and how

Machine: headless Linux x86_64 VM, shared 1.5 CPU. Browser:
Firefox 160.0.1 as the Zen stand-in (Zen 1.24.3b rides Firefox
160.0.1, see section 6; real Zen numbers need the laptop run).
Driver: geckodriver 0.37.1, Selenium 4.53.0 in the repo venv.
Fixture: tests/dom_grounding_fixture.html, 66 interactive elements
(60 grid buttons, input, select, link, one button inside a
scroller, one hidden button, one CSS translated button), with a
click log the page itself keeps. Bench: tests/dom_grounding_bench.py.
Window: 1280x900 set, viewport 1280x814 in the Marionette runs
(headless chrome takes the rest), BiDi viewport set to 1280x900.

Three full runs, walls (UTC) 2026-11-21T19:31:59Z to 19:32:12Z
(14.35 s) and 2026-11-21T19:32:33Z to 19:32:45Z (12.74 s), plus
four partial runs that crashed on bench bugs before the BiDi phase
and still produced valid Marionette numbers. Raw JSONL logs:
 /tmp/dom_grounding_run1.log, /tmp/dom_grounding_run2.log,
 /tmp/dom_grounding_run3.log (kept on this machine, outside the
repo). Every step in the bench prints wall clock and elapsed seconds
from a monotonic clock.

Two bench bugs found and fixed during the runs, both recorded
because they are real findings, not hidden:

- websocket-client sends an Origin header by default and the
  Firefox Remote Agent rejects it with HTTP 400. Fix:
  suppress_origin=True. The repo's own BiDi client
  (scripts/zen_cli.py) sends no Origin header, which is why it
  works.
- BiDi message ids must be positive integers. A UUID string id is
  rejected with "Expected id to be a positive integer".
- BiDi RemoteValue serializes objects as [key, value] pairs, not
  plain objects. The bench returns JSON.stringify from evaluate
  and parses the string in Python instead.

## 2. Measured results

All times are per call unless stated. Medians across the runs.

| Step | Marionette | BiDi | Notes |
| --- | --- | --- | --- |
| One shot, all 66 rects | 0.019 s median (range 0.009 to 0.071) | 0.006 to 0.011 s | one evaluate, whole page |
| Per element rect, 66 calls | 1.05 s total, about 16 ms each | not measured, same shape | 66 round trips, 55x slower than one shot |
| Screenshot PNG 1280x900 | 0.039 s median, 62,400 bytes | not applicable | capture only, no locate step |
| Session start | 2.65 to 3.49 s attach (warm browser) | 0.002 to 0.005 s session.new alone | BiDi session is nearly free |
| 5 pointer clicks from one snapshot | 1.49 s total, about 0.30 s each | not measured | all 5 landed, 3 of 3 runs |
| 5 DOM clicks (.click() in one evaluate) | 0.0047 s total | 0.0034 to 0.050 s for 3 clicks plus verify | DOM clicks skip the input pipeline |
| Verify by one DOM read | 0.005 to 0.015 s | included above | reads the page's own click log |
| a11y snapshot, whole page | 0.018 to 0.025 s repeat (0.051 s first) | not measured here | 83 nodes, 5,065 chars JSON |
| a11y snapshot, one element | 0.0166 s | not measured here | role button, name Button 42 |

Rect agreement, measured twice: BiDi rects against Marionette
rects on the same fixture, max delta 5.7e-14 px (floating point
noise, effectively zero). One shot Marionette rects against
per-element Marionette rects, max delta 0.0 px exactly. The rect
is the same number no matter which protocol reads it.

What the numbers mean for a task of, say, 20 actions on one page:

- Screenshot path per action: one capture (0.04 s) plus one model
  round trip to locate the target (seconds, from the repo's own
  architecture notes) plus the click, plus a verification capture.
  The locate step dominates and it is a model call every time.
- DOM path per action: one snapshot for the whole page (0.01 to
  0.02 s), then each action is a DOM click (0.001 s) or a pointer
  click at a known coordinate (0.30 s), verified by one DOM read
  (0.01 s). The observation cost is paid once per page, not once
  per action. This is the same structural win the E1 experiment
  (docs/research/2026-11-21-e1-planning-vs-execution.md) measured
  for planning: observations are the expensive unit, so batch them.

## 3. The three browser paths

### 3.1 BiDi (primary)

Firefox's only bidirectional protocol since CDP was removed.
Connect to ws://127.0.0.1:PORT/session with no Origin header,
session.new with integer ids, script.evaluate for rects and DOM
clicks, browsingContext.navigate, browsingContext.getTree.
Measured here: session.new 0.002 to 0.005 s, one shot rects
0.006 to 0.011 s for 66 elements, DOM clicks plus verify 0.0034
to 0.050 s. The repo's own scripts/zen_cli.py already speaks this
protocol to Zen 1.24.2b (verified 2026-11-18 on the laptop).
Firefox 160 BiDi changes (MDN release notes, 2026-11-10):
machine-readable CDDL for the moz: vendor extensions, a
script.message context fix, and script.evaluate no longer clearing
a pre-existing user activation flag when called with
userActivation false. Nothing in the 160 notes breaks the rect
or evaluate flows used here.

Limits, measured: BiDi DOM clicks are not real input. Some apps
ignore DOM set values and synthetic clicks, exactly as the speed
comparison doc (docs/zen-speed-comparison.md, 2026-11-21) already
records. BiDi cannot do real key events or real pointer moves;
that is what Marionette is for.

### 3.2 Marionette / Selenium Classic (real input fallback)

Attach with geckodriver --connect-existing to a browser started
with -marionette. Measured here: session attach 2.65 to 3.49 s
on a warm browser, one shot rects 0.019 s median, per-element
rects 16 ms each, pointer clicks 0.30 s each, screenshot PNG
0.039 s median. The per-element cost is the trap: a naive loop
over find_element plus .rect pays 66 round trips for what one
evaluate does in 0.019 s. Always read rects in one shot.

Two Firefox command line facts the bench tripped over, both
measured: --remote-debugging-port cannot be set through Selenium
capabilities (InvalidArgumentException), it must be a browser
command line flag; and a profile directory given with -profile
must already exist or Firefox exits with "Could not find profile
folder".

### 3.3 CDP (dead, do not build on it)

Firefox deprecated its experimental CDP in Firefox 129 and removed
it completely in Firefox 141 (Bugzilla 1882096, RESOLVED FIXED,
141 Branch). On current Firefox the /json discovery endpoints
return HTTP 404 and --remote-debugging-port serves BiDi only.
Foxbridge (foxbridge.vulpineos.com, updated 2026-11-08) confirms
Firefox has no native CDP and translates CDP to Juggler or BiDi
instead, with 62/62 integration tests passing on Firefox 148.
Playwright connectOverCDP is Chromium only; for Firefox it uses
Juggler. Any plan that assumes a CDP endpoint on Zen is wrong.

## 4. Accessibility: the semantic half of grounding

Selenium 4.53, released 2026-11-17 (selenium.dev blog), adds
accessibility snapshots: driver.accessibility_snapshot() and
element.accessibility_snapshot() return the accessibility tree of
a page or element, in both Classic and BiDi sessions. Measured
here, Classic session on the same fixture: whole page snapshot
0.018 to 0.025 s on repeat runs (0.051 s first), 83 nodes, 5,065
chars of JSON; one element snapshot 0.0166 s. A button node
carries role button, name Button 42, states, and a handle back to
its WebElement, so the agent can pick by meaning and act by
element. The node carries no coordinates in the Python binding
(the AccessibilityNode attributes are children, description,
element, name, role, states, to_text, url, value), so geometry
still comes from the DOM rect. The pair is the design: a11y tree
for what the element is, DOM rect for where it is. This matches
the Playwright MCP approach (Glama comparison, November 2026):
drive the browser from accessibility snapshots instead of
screenshots.

AT-SPI is the same idea one level down, for native desktop apps
rather than web pages. Every GTK or Qt app publishes its UI tree
over D-Bus: role, name, states, and exact bounding boxes via the
Component interface get_extents(). Recent work in the last 30
days: Vercel Labs released agent-desktop on 2026-11-04
(mlllm.io, 2026-11-04), a Rust tool that reads the OS
accessibility tree (AT-SPI on Linux) and returns a JSON snapshot
with refs, with STALE_REF and AMBIGUOUS_TARGET errors when the UI
moves; and linux-use (techbytes.app, 2026-11-07) walks the AT-SPI
tree and reports 28 interactive elements in 48 ms in the
author's benchmark. On this VM AT-SPI is UNVERIFIED: no
at-spi2-registryd, no at-spi-bus-launcher, pyatspi not
importable, and the repo's own AT-SPI doc already records the
unblock path (apt-get update plus install). The 48 ms figure is
author reported, not measured here.

## 5. One observation, many actions, and verify without re-observing

The pattern the bench proves end to end, 3 of 3 runs:

1. One evaluate returns rects, tags, labels and visibility for
   every interactive element on the page (0.01 to 0.02 s).
2. The agent picks targets by label and role from that snapshot,
   never by pixels in an image.
3. Each action uses the snapshot coordinates: real pointer clicks
   at rect centers through W3C pointer actions (0.30 s each),
   or DOM clicks (0.001 s each) where the app tolerates them.
4. Below the fold targets are scrolled into view with
   scrollIntoView and only that element's rect is re-read, one
   cheap call, not a fresh snapshot. The bench's translated
   button (CSS transform) and the button inside a scroller both
   landed, which is the point of using getBoundingClientRect: it
   already accounts for transforms and scroll.
5. Verification is one cheap DOM read (0.005 to 0.015 s): read
   the page's own state (the fixture's click log and counter)
   instead of taking another screenshot. A stale snapshot is
   detected when the verify read disagrees with the expected
   state, and only then is a fresh snapshot taken.

Failure modes to design for: a snapshot goes stale when the page
mutates between the read and the click (the agent-desktop
STALE_REF idea applies here too); a rect with zero width or
height means hidden, the fixture's hidden button reports exactly
that; a click that lands on the wrong element is caught by the
verify read naming the element that actually received the click.

## 6. Recent sources, last 30 days

All web claims in this report come from sources dated in the last
30 days, except where marked older. Accessed 2026-11-22.

- Firefox 160.0 released 2026-11-10, 160.0.1 released
  2026-11-17 (firefox.com release notes). BiDi changes in 160
  listed in section 3.1 (MDN, Firefox 160 release notes for
  developers).
- Zen Browser 1.24.3b released 2026-11-18, rides Firefox
  160.0.1 (linuxcompatible.org, 2 days ago; whatsnew.fyi,
  2026-11-18; zen-browser.app release notes). Zen 1.24.2b
  (2026-11-11/12) rides Firefox 160.0. The repo's BiDi wrapper
  was verified against Zen 1.24.2b on 2026-11-18, so the
  grounding paths in this report apply to the current Zen.
- Selenium 4.53 released 2026-11-17, accessibility snapshots
  for Python and JavaScript (selenium.dev blog, 2026-11-17).
  Docker Selenium 4.53.0 ships Firefox 160.0.1.
- Vercel Labs agent-desktop released 2026-11-04, AT-SPI on
  Linux, JSON snapshots with refs (mlllm.io, 2026-11-04).
- linux-use, AT-SPI tree walk, 28 elements in 48 ms, author
  benchmark (techbytes.app, 2026-11-07).
- Foxbridge CDP to Firefox proxy, BiDi backend 62/62 tests on
  Firefox 148 (foxbridge.vulpineos.com, updated 2026-11-08).
- CDP removal: Firefox 129 deprecated, Firefox 141 removed
  (Bugzilla 1882096). Older than 30 days, documented, not recent.
- Cypress requires Firefox 140 or newer because BiDi below 140
  is incomplete (docs.cypress.io, 2 days ago).

## 7. The last30days-skill install: NOT installed, and why

The task asked to install mvanhorn/last30days-skill with npx
skills add and use it for this research. The install did not
complete. The plain command hung for 25 minutes on an interactive
agent selection prompt (79 agents, arrow keys, no TTY). Retried
non-interactively with -a claude-code, the installer cloned the
repo, found 1 skill, and then printed a security risk assessment
flagging last30days as Critical Risk on all three scanners (Gen,
Socket, Snyk) and stopped at a "Proceed with installation?"
confirmation. The install aborted there (EOF on stdin) and nothing
was written: ~/.agents/skills does not exist on this machine.
Clone2 did not confirm the install, because a Critical Risk flag
from the installer's own scanners is a reason to stop and report,
not to click through. The research in section 6 was done instead
with web search restricted to sources dated in the last 30 days,
and every claim carries its source and date. If the coordinator
wants the skill installed despite the flag, that is the
coordinator's call, and the install command is: npx skills add
mvanhorn/last30days-skill -g.

## 8. Recommendations for the repo

1. Make the one-shot rect sweep the standard observation for
   browser tasks: one script.evaluate returning id, tag, label,
   role, rect, center and visibility for every interactive
   element. Never loop per-element .rect calls.
2. Pair it with the Selenium 4.53 accessibility snapshot for
   semantics: role and accessible name from the a11y tree,
   geometry from the DOM rect.
3. Keep two drivers behind one interface: BiDi for grounding and
   DOM actions, Marionette for real pointer and key input. Never
   open both sessions on one browser instance; Firefox 160
   refuses the second with "Maximum number of active sessions",
   reproduced three times here. Sequence them instead: ground
   and plan on BiDi, hand over to a fresh Marionette session
   for real input, or stay on one protocol per browser instance.
4. Verify by DOM read, not by re-screenshot: after each action,
   one cheap evaluate reads the resulting state, and a fresh
   snapshot is taken only when the verify read disagrees.
5. Keep AT-SPI as the native app path and the screenshot path as
   the last fallback for canvas, games and video, where no DOM
   and no tree exist.
6. On the laptop, re-run tests/dom_grounding_bench.py against
   real Zen 1.24.3b and replace the Firefox stand-in medians in
   section 2 with Zen medians. The bench takes the fixture path
   as a constant; point it at the Zen binary the same way
   tests/zen_speed_benchmark.py does.

## 9. UNVERIFIED on this machine

- Real Zen: every number here is Firefox 160.0.1 as a stand-in.
  Zen 1.24.3b on Firefox 160.0.1 should behave the same at this
  level, but that is an inference, not a measurement.
- AT-SPI live: no daemons and no pyatspi on this VM, so no AT-SPI
  number in this report was measured here. The linux-use 48 ms
  figure is author reported.
- Headed runs under Xvfb and real web pages: the fixture is local
  and static. Rects on a live page with lazy loading and
  animations will move; the verify-read pattern in section 5 is
  designed for exactly that, but it was not exercised on a live
  site here.
- BiDi accessibility module (accessibility.getComputedLabel and
  friends): not measured here. The Selenium snapshot path in
  section 4 covers the same need for this repo.
