# Zen structured-equivalent probe, DOM-replicate run, 2026-11-19

Owner: Pham Tuan. Worker: Luna 6 Max. Verdict: YES, definite, live-verified.
Probe log: /tmp/speed-dom-replicate-20261119/zen-probe.log (run 17:52:45 to 17:52:47 +07, 2 seconds).

## Answer in ladder terms (priority ladder, 19/11 17:58)

The ladder is CLI first, then code-exec, then vision + mouse. For Zen the
top rung ALREADY EXISTS: a repo-owned CLI, scripts/zen_cli.py, talks to Zen
over WebDriver BiDi (Firefox Remote Agent) and was re-verified live on the
current build in this probe. So Zen does not need a new CLI built, and does
not need to fall back to code-exec or vision for structured access: the CLI
path is the answer, and it is already built, tested, and in the repo.
(The 12:42 rule is respected: this CLI was built for an app he uses
repeatedly, not for a one-off task plain shell does in milliseconds.)

## What was verified live (this probe, fresh profile only)

- Zen 1.24.2b. `zen-browser --version` rc=0, "Mozilla Zen 1.24.2b".
- His running Zen has NOTHING listening on 9222, 2828, or 6000 before the
  probe start. BiDi can never attach to his session; a dedicated instance
  is the only route. His Zen, its tabs, and ~/.config/zen were not touched.
- Dedicated headless instance on a FRESH profile
  (~/.cache/cli-anything-zen/profile), pid 303828, port 9222:
  `session start` ok, browser "zen", version "1.24.2b",
  ws_url ws://127.0.0.1:9222/session. Two about:blank tabs at start.
- DOM-first primitives, all through BiDi script.evaluate on the fixture
  (file:///tmp/speed-pick4-20261118/pick4-fixture.html):
  - Rects: INPUT #name at (50.2, 78.87, 180x22); BUTTON #show "Show result"
    at (234.2, 78.87, 81.65x22). Viewport-relative rects, exactly the
    DOM-first grounding input.
  - In-page click: document.querySelector('#show').click() returned
    "clicked".
  - Assert: #result textContent read back as "pick4-ok hello stranger".
  - Title: "Pick 4 fixture".
- Session stop clean (pid 303828 stopped, running false); status after
  stop: session_up false. No leftover Zen process, no leftover profile
  lock, desktop untouched.

## Named mechanism

WebDriver BiDi (Firefox Remote Agent) over `--remote-debugging-port`,
reached through scripts/zen_cli.py. Firefox documents Marionette and
WebDriver BiDi as its remote protocols, NOT CDP; Zen's own --help lists
--remote-debugging-port as "Start the Firefox Remote Agent". BiDi gives
session.new, browsingContext.getTree / navigate / activate / close, and
script.evaluate, which is the whole DOM-first toolkit (rects, click,
assert). The CLI wraps exactly these calls plus read-only history reads
from a copy of places.sqlite.

## Known gaps and limits (from scripts/zen_cli.py, verified 18/11)

- browsingContext.createContext is "unknown command" in this build, so a
  new tab is opened with window.open from an existing tab, then found in
  getTree by its opener. Tab creation works, just not through the
  createContext call.
- Context ids (and clientWindow ids) change on every new BiDi session;
  tabs are addressed by INDEX (getTree order), never by context id.
- Headless mode starts with two about:blank tabs.
- `open --live` (open a URL in his RUNNING Zen via remoting) is PROPOSED
  only and was NEVER run in this probe: it would add a tab to his Zen.
- Marionette is the other documented Firefox remote protocol, but it was
  not needed: BiDi already covers the DOM-first primitives, so no
  Marionette probe was run.

## Second mechanism (not the verdict)

AT-SPI a11y tree (scripts/a11y.py) is the structured route to the VISIBLE
GUI Zen, but it is NOT proven for Zen: the 18/11 00:40 probe failed on a
PID lookup artifact, and this probe did not re-test it. BiDi is the
verdict; a11y-for-Zen stays unproven, not negative.

## Implication for DOM-first

A Zen DOM-first path is available at the CLI rung: zen_cli.py plus one
script.evaluate per grounding step returns rects, and in-page click plus
a text read replaces screenshot grounding and OCR verification. It runs
against a DEDICATED headless Zen, never his running Zen, so it cannot
drive the Zen he is looking at; for the visible Zen, vision or a11y
remain the only routes. No new CLI needs building for Zen.
