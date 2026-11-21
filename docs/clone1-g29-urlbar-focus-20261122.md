# G29: click on the address bar moves the mouse but does not focus it

Task: batch 7 task 1 (Muse, 02:08 22/11). Investigate why clicking
the address bar moves the mouse but does not focus it, fix it, test
live on this machine.

## Verdict

Root cause found and fixed. `scripts/mcp_server.py`, function
`_real_click`, sent the pointer command `button 1` for a left click.
The native pointer binary sends evdev code `0x110 + index`, so
index 1 is BTN_RIGHT (0x111), not BTN_LEFT (0x110). The MCP hybrid
click therefore right-clicked everything it was asked to click. A
right-click on the address bar moves the cursor to the bar, opens
the bar context menu, and typed text never reaches the bar. That is
the G29 symptom, reproduced exactly, twice, on the live Firefox
160.0.1 on this machine.

Fix: `scripts/mcp_server.py` lines 308-309 now send `button 0 1` /
`button 0 0`, with a comment recording the mapping. Regression test
`RealClickButtonTest` added to `tests/test_mcp_server.py`: it fails
on the old code (recorded `button 1 1`, `button 1 0`) and passes on
the fixed code. Full MCP suite: 20 tests OK (1 skipped, RealDomTypeTest,
playwright-core is not installed on this machine).

## Evidence chain (each link checked, none taken on trust)

1. Kernel header on this machine, /usr/include/linux/input-event-codes.h:
   BTN_LEFT 0x110, BTN_RIGHT 0x111, BTN_MIDDLE 0x112.
2. `native/pointer.c`: `zwlr_virtual_pointer_v1_button(p, stamp(),
   0x110+button, down)` with `button < 3`. Index 0 is left, 1 is
   right, 2 is middle.
3. Native pointer tests, live against the mock Wayland server:
   `python3 -m unittest tests.test_pointer_native`, 12 tests OK,
   2.290 s. The `hold()` helper sends `button 0/1/2` and the mock
   records evdev codes 272/273/274 (0x110/0x111/0x112).
4. `scripts/cu.py` maps `{'left': 0, 'right': 1, 'middle': 2}` and
   `tests/e2_direct_clicks.py` sends `button 0` for a left click.
   A full-repo grep shows `scripts/mcp_server.py` was the only
   production sender of `button 1` as a click. The desktop-act path
   in `scripts/cu.py` was already correct.
5. Live Firefox experiment (below): a left click focuses the bar and
   typed text lands in it; a right click at the same point moves the
   mouse there, opens a context menu, and typed text does not land.

## Live experiment (Firefox 160.0.1, headed under Xvfb, AT-SPI session)

Session recipe from `tests/run_atspi_session.sh` (council 3, batch 4):
Xvfb :97, dbus-launch, GNOME_ACCESSIBILITY=1,
GTK_MODULES=gail:atk-bridge, registry activated before Firefox.
Session scripts: `~/workspace/b7t1/start_session.sh`,
`stop_session.sh`. One setup finding: XDG_RUNTIME_DIR must be
exported BEFORE dbus-launch, so the D-Bus-activated
at-spi-bus-launcher puts the a11y bus socket at
$XDG_RUNTIME_DIR/at-spi/bus. In this G29 session the probe failed
with "Couldn't register with accessibility bus" until the order was
fixed, then passed. The repo wrapper `tests/run_atspi_session.sh`
has the same broken ordering, export after dbus-launch (dbus-launch
at line 133, export at line 141). Whether the wrapper also fails
with two concurrent sessions was not tested on the wrapper itself:
council 3 found the fallback sockets are display-suffixed
(bus_97, bus_98 under ~/.cache/at-spi/) and a second session
registered fine, so the shared-socket contention did not reproduce
there. The wrapper's two-session behavior is untested, not proven
to work only with a single session.

Address bar node: role "combo box", name "Search with Google or
enter address", inside the "Navigation" toolbar. Extents moved
between runs as the chrome settled ([268, 48, 652, 32], then
[294, 48, 650, 32], then [294, 48, 626, 32]); the probe re-reads
the node fresh before every experiment, so every click used
current coordinates. No spotlight-dialog dismiss step is recorded
in the probe code, the session starter, or the log; the log starts
with find_app and find_urlbar succeeding.

Probe: `~/workspace/b7t1/g29_probe.py`, log
`~/workspace/b7t1/g29-log.jsonl`. Each experiment: clear the bar
(Ctrl+L, BackSpace), click neutral page content to move focus away,
verify the bar is not focused, perform the click, then check focus
two ways: AT-SPI STATE_FOCUSED on the bar node, and a type test
(xdotool type a marker, read the bar text back through the AT-SPI
Text interface; the marker lands in the bar only if it has
keyboard focus).

Run 1 (2026-11-21T21:05:53Z to 21:06:01Z, 7476.5 ms total;
markers E1/E2 shared "g29t" by a probe bug, fixed before run 2):
- E1 left click (xdotool click 1) at (619, 64), tool 104.5 ms:
  PASS. Mouse at (619, 64), bar focused, focused node is the combo
  box, typed "g29t" read back as "g29t".
- E2 right click (xdotool click 3) at (619, 64), tool 104.6 ms:
  FAIL, reproduces G29. Mouse at (619, 64), a context menu appeared
  (role "menu", extents [621, 66, 81, 204]), typed "g29t" read back
  as "" (empty). Note: AT-SPI STATE_FOCUSED on the bar node was
  true even after the right-click. A check that only reads
  STATE_FOCUSED would wrongly say "focused". The type test is the
  decisive check: the menu captures the keyboard.
- E3 AT-SPI doAction click (action "activate", 0.3 ms): PASS. Bar
  focused, typed "g29i" read back as "g29i". The visible cursor did
  not move (mouse stayed at 600, 400), as expected for an
  AT-SPI click.
- E4 Ctrl+L (29.3 ms): PASS (control). Bar focused, typed "g29l"
  read back as "g29l".

Run 2 (unique markers, same session, 7516.5 ms wall): E1 left PASS
("g29a" landed), E2 right FAIL ("g29b" did not land, context menu
present), E3 AT-SPI PASS ("g29c" landed), E4 Ctrl+L PASS ("g29d"
landed). Same result twice.

No screenshot: neither `import` nor `xwd` is installed on this
machine, so the context menu is evidenced by the AT-SPI tree
(role "menu" with real extents), not by an image.

## Why the bug survived

The fake backend in `tests/test_mcp_server.py` masks it: its click
returns a counter without ever touching the pointer binary, so the
existing click test passed while the real path right-clicked. Same
pattern as the batch 4 TYPE bug (fake backend masked the
`Illegal invocation` on textarea/contenteditable). The new
`RealClickButtonTest` stubs the `cu` module and asserts the exact
command bytes `abs ...`, `button 0 1`, `button 0 0`, so the fake
backend can no longer hide a wrong button.

The bug has been present since the file was created (commit
98edc39, "MCP server prototype"); the `button 1` lines were in the
original commit, not introduced by a later fix. The likely cause is
X11 numbering: in X11, button 1 is the left button. The pointer
binary's protocol is 0-based (0 is left), as `cu.py` and the
native tests use it.

`tests/pointer_benchmark.py:53` also sends `button 1 1` / `button 1 0`,
intentionally unchanged: it benchmarks command latency against the
mock server, and any button index exercises the same path. It is
not a click-behavior test.

## Fix

`scripts/mcp_server.py`, `_real_click` (lines 308-309):
- `pointer.command("button 0 1")` (press left)
- `pointer.command("button 0 0")` (release left)
plus a comment recording the 0x110+index mapping and the G29
reference. Diff: 2 files, `scripts/mcp_server.py` +10/-2,
`tests/test_mcp_server.py` +61.

Negative control for the test: run against the unfixed code, the
new test fails with recorded
`['abs 78125 250000 1000000 1000000', 'button 1 1', 'button 1 0']`
versus expected `button 0 1`, `button 0 0`. After the fix the full
suite passes: 20 tests OK in 1.764 s (1 skipped).

## What is still open (stated plainly)

1. The fixed `_real_click` cannot run live on this machine: there
   is no Wayland/Hyprland here, and it raises "real click needs a
   Wayland session" without one. The live proof is a chain, not a
   single run: (a) the fixed command bytes are identical to the
   left-click commands `cu.py` sends; (b) a left click focuses the
   bar live (E1, twice); (c) the unit test asserts the exact bytes.
   The end-to-end run of the fixed MCP click on the laptop's
   Wayland session is still owed.
2. Zen itself is unverified: no Zen binary exists on this machine.
   Zen's toolbar layout differs from Firefox, so the urlbar rect
   and the click behavior on Zen still need the laptop run. The
   bug is in shared code (mcp_server plus the pointer binary) used
   for Zen too, so the fix applies to the Zen path, but the
   end-to-end Zen test is owed.
3. The MCP `click` tool takes a DOM selector, and `locate()` is
   DOM-only, so the address bar cannot be targeted through
   `mcp_server.click` with a selector at all. The exact caller
   that produced the G29 click on the laptop is not identified
   from this machine. What is proven is that the only
   wrong-button sender in the repo is `mcp_server._real_click`,
   and that a right-click on the bar reproduces the symptom
   exactly. If the G29 click on the laptop came through the
   `cu.py` desktop-act path (which maps left to 0 correctly),
   the root cause is elsewhere and a live Zen run is needed to
   find it. The fix is correct and necessary regardless: a click
   tool that right-clicks is a real bug.
4. The `cu.py` desktop-act click holds the button 25 ms; the MCP
   click releases immediately. The live E1 test used xdotool click
   (no dwell) and passed, so dwell is not the cause here.

## Files

- Report: docs/clone1-g29-urlbar-focus-20261122.md (this file)
- Fix: scripts/mcp_server.py (button 0)
- Regression test: tests/test_mcp_server.py (RealClickButtonTest)
- Probe: ~/workspace/b7t1/g29_probe.py, ~/workspace/b7t1/g29_discover.py
- Session: ~/workspace/b7t1/start_session.sh, ~/workspace/b7t1/stop_session.sh
- Log: ~/workspace/b7t1/g29-log.jsonl (both probe runs, JSON lines)

## Corrections after the batch 7 redteam review

Applied by the batch 7 fix agent, each recomputed first-hand from
the saved log (g29-log.jsonl) and the probe code.

- W6: run 2 wall "7646 ms" was wrong; g29-log.jsonl records
  probe_done total_ms 7516.5 for run 2 (run 1 matches exactly at
  7476.5 ms). Fixed in the run 2 header.
- U1: the earlier draft said the first-run spotlight dialog was
  dismissed with "(AT-SPI dismiss, 'Continue', 0.2 ms)". No such
  step exists in the evidence: no dismiss step appears in the probe
  code, the session starter, or the log, and the only "0.2" in the
  probe code is time.sleep(0.2), which is 0.2 seconds in
  clear_urlbar, not a dismiss timing. The parenthetical is removed
  and the sentence now states what the log shows (it starts with
  find_app and find_urlbar succeeding). The context-menu dismiss in
  the probe is a different step (Escape key, logged as
  E2_menu_dismissed) and is unaffected.
- U6: the XDG setup finding is reworded. What was observed: in this
  G29 session the probe failed with "Couldn't register with
  accessibility bus" until XDG_RUNTIME_DIR was exported before
  dbus-launch, then passed. What was not tested: the repo wrapper
  with two concurrent sessions, so "works only when a single
  session runs" is dropped. The ambiguous "the same ordering" now
  states the ordering explicitly (the wrapper exports after
  dbus-launch, lines 133 then 141, i.e. the broken order). Council 3's
  qualification is added: the fallback sockets are display-suffixed
  (bus_97, bus_98), and a second session registered fine there.
