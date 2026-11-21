# Batch 7 council 3: independent live verification of G29 and H2

Reviewer: batch 7 council 3, independent subagent. Method: read both
reports in full, then reproduced the live claims on this machine with
my own runs and my own logs. Nothing was taken on trust. Line counts
by wc -l. No coord file edited, nothing committed or pushed.

Reports reviewed:
- docs/clone1-g29-urlbar-focus-20261122.md (task 1, G29)
- docs/clone1-thinktime-20261122.md (task 2, H2)

## Verdicts

- **G29: CONFIRMED.** Live reproduction agrees on every experiment,
  including the exact context-menu extents and the STATE_FOCUSED
  nuance. The code chain checks out line by line. One side finding
  (XDG_RUNTIME_DIR ordering) is only partly confirmed, see below.
- **H2: PARTIALLY CONFIRMED.** The loop-shape numbers reproduce, and
  the 38-50x rects gap reproduces (47.6x in my run). The session
  setup total does NOT reproduce: 6,308 ms in my run against the
  report's 3,883-4,229 ms range. Setup is load-sensitive and the
  report's range understates what it costs under load.

## G29: my own live reproduction (Firefox 160.0.1, headed, Xvfb :97)

Session started with ~/workspace/b7t1/start_session.sh (display :97,
Xvfb, dbus-launch, GNOME_ACCESSIBILITY=1, GTK_MODULES=gail:atk-bridge,
registry before Firefox). Probe: my own copy of the agent's script at
~/workspace/b7c3/g29_probe_council.py, log
~/workspace/b7c3/council-g29-log.jsonl (the agent's log was not
touched). Dismiss first: AT-SPI dismiss "Continue", 0.4 ms (the
report says 0.2 ms; same order). Note: my first find_urlbar failed
before the dismiss, because the spotlight dialog blocks the bar from
the tree; this corroborates the report's statement that the dialog
must be dismissed first.

My run, total 7,706.3 ms (report run 1: 7,476.5 ms, run 2: 7,646 ms):
- find_urlbar: extents [268, 48, 652, 32], center [594, 64], identical
  to the report's run 1 first read.
- E1 left click (xdotool click 1) at (619, 64), tool 104.6 ms
  (report: 104.5 ms run 1, 107.5 ms run 2): PASS. Mouse at (619, 64),
  bar focused, typed "g29a" read back as "g29a".
- E2 right click (xdotool click 3) at (619, 64), tool 105.7 ms
  (report: 104.6 ms run 1, 104.3 ms run 2): FAIL, reproduces G29.
  Mouse at (619, 64), context menu role "menu", extents
  [621, 66, 81, 204], exactly the extents in the report. Typed
  "g29b" read back as "" (marker_in_text false). STATE_FOCUSED on
  the bar node was TRUE even after the right-click, so the report's
  nuance is confirmed by my own run: a check reading only
  STATE_FOCUSED would wrongly say "focused". The type test is the
  decisive check.
- E3 AT-SPI doAction click, 1.3 ms (report: 0.3 ms): PASS. Mouse
  stayed at (600, 400), typed "g29c" read back as "g29c".
- E4 Ctrl+L, 45.3 ms (report: 29.3 ms): PASS. Typed "g29d" read back
  as "g29d".

## G29: code chain, verified by me

- Kernel header /usr/include/linux/input-event-codes.h: BTN_LEFT
  0x110, BTN_RIGHT 0x111, BTN_MIDDLE 0x112. Exact.
- native/pointer.c line 188: zwlr_virtual_pointer_v1_button with
  0x110+button. Exact.
- scripts/cu.py lines 1621 and 1649: {'left': 0, 'right': 1,
  'middle': 2}. Exact.
- Full-repo grep for "button 1" in scripts/ and tests/: no production
  sender other than the fixed mcp_server.py (the only other hit is
  tests/pointer_benchmark.py, which the report discloses as
  intentional). Confirmed: mcp_server was the only wrong-button
  sender.
- Old code at commit 98edc39, scripts/mcp_server.py lines 248-249:
  pointer.command("button 1 1") and ("button 1 0"). Confirms the bug
  was present at creation.
- RealClickButtonTest exists at tests/test_mcp_server.py line 302,
  stubs the cu module and records command bytes. I re-ran both suites
  myself: tests.test_pointer_native 12 tests OK in 2.289 s (report:
  2.290 s), tests.test_mcp_server 20 tests OK, 1 skipped, in 1.615 s
  (report: 1.764 s; parent: 1.678 s; same counts, run-time jitter
  only). The fix (button 0 1 / button 0 0 at mcp_server.py lines
  308-309, with the mapping comment) is in the tree.

## G29: XDG_RUNTIME_DIR ordering finding, PARTLY confirmed

I tested the wrong-order case with a second session (display :98,
XDG_RUNTIME_DIR exported AFTER dbus-launch), script
~/workspace/b7c3/wrong_order_session.sh.

- Mechanism confirmed in part: with the wrong order, the registry
  address came back as unix:path=/home/hatch/.cache/at-spi/bus_98,
  i.e. the socket landed under ~/.cache/at-spi/, not under
  $XDG_RUNTIME_DIR. With the correct order (session :97), the socket
  was at b7t1/runtime.UqNddH/at-spi/bus_97.
- Socket names are display-suffixed (bus_97, bus_98), so the
  report's plain paths ("$XDG_RUNTIME_DIR/at-spi/bus",
  "~/.cache/at-spi/bus") are imprecise. Minor wording error.
- Contention NOT reproduced: the two sessions got distinct sockets,
  and a probe in the wrong-order session registered fine: with
  Firefox running on :98, find_app returned ok true in 9.8 ms, and
  dismiss returned "no dialog button found" (exit code 3, the
  documented no-dialog case). I saw no "Couldn't register with
  accessibility bus" error anywhere. The report's contention claim
  did not reproduce in this configuration; it may need both sessions
  on the same display or different conditions. The correct-order
  recipe itself works and is worth keeping.

Cleanup verified: both sessions stopped, 0 Xvfb/Firefox processes
left, /tmp/.X11-unix empty.

## H2: my own re-run of measure_loop.mjs

I copied the script to ~/workspace/b7c3/measure_loop.mjs and ran it
there, so the agent's evidence in ~/workspace/b7t2/ is untouched.
My run: ~/workspace/b7c3/results.json, wall start 2026-11-21T21:14:17Z,
total 9,867 ms, free_mb_at_start 409 (report runs 2/3: 1,412 and 944).

Medians, mine against the report's run 2 / run 3 medians:
- Session setup (port up + connect): mine 6,308 ms (port up 2,575,
  connect 3,733) against 4,229 and 3,883 ms. OUTSIDE the range.
  The setup step is load-sensitive: my run started with 409 MB free
  against 944-1,412 MB for runs 2/3, and other agents were active.
  The report's headline range (3,883-4,229 ms) understates what
  setup costs under load; the "setup dominates" conclusion still
  holds, more so.
- goto fixture: mine 537 ms against 306 / 383 ms. Slower, same
  direction as setup.
- Observe full DOM: mine 2.3 ms against 3.7 / 3.5 ms. Faster.
- Compact one-shot: mine 5.7 ms against 6.9 / 7.8 ms. Faster.
- Rects one-shot: mine 4.55 ms against 5.8 / 4.8 ms. In range.
- Rects per element (60 calls): mine 216.8 ms against 219.8 / 239.5
  ms. In range. Ratio one-shot vs per-element in my run: 47.6x,
  inside the report's 38-50x.
- Screenshot PNG: mine 22.0 ms against 25.9 / 24.2 ms. Faster.
- Cheap verify: mine 3.1 ms against 2.9 / 4.2 ms. In range.
- Think local policy: mine 0.0 ms median, max 0.129 ms (report: max
  0.157 ms). Agrees.
- Click + verify: mine 24.7 ms against 34.4 / 26.6 ms. Just below
  the range.
- Type 8 chars: mine 14.9 ms against 18.9 / 12.1 ms. In range.
- Loop one-vision: mine 20.1 ms against 27.9 / 29.6 ms. Faster.
- Loop naive: mine 39.2 ms against 39.1 / 34.7 ms. At the top edge.
- Final counter: "18" in my run, exact, matching the report.

The individual medians landing outside the report's narrow 2-run
ranges on the fast side is expected run variance, not an error: two
runs make a fragile range. The ratios and orders of magnitude the
proposed cuts rest on all reproduced. The one material miss is the
setup total, which went the other way (slower) and matters because
the report presents it as a stable range.

I also re-read the saved evidence files: results-run2.json and
results-run3.json hold the exact numbers in the report table
(setup 4,229 / 3,883 ms, rects per-element 219.8 / 239.5 ms,
one-shot 5.8 / 4.8 ms, loop one-vision 27.9 / 29.6 ms, loop naive
39.1 / 34.7 ms). The report's table is faithful to its files.

## H2: AT-SPI observe-cost claim, NOT VERIFIED

The report says two attempts with tests/run_atspi_session.sh
--mode dump failed at wait_document after 32,244 ms and 32,376 ms,
Firefox launching fine both times (5,005 ms and 5,006 ms). I
searched ~/workspace for any log or artifact of those attempts
("wait_document", "32,244", "32244", "no BiDi fixture document"):
the only hits are unrelated files (SVG icons, old probe records).
~/workspace/b7t2/ holds only measure_loop.mjs, profiles/measure,
and the results JSONs. No log of the two failed attempts exists on
disk. The claim rests on the report's word only. I did not re-run
--mode dump myself, so I add no new evidence either way.

## Minor discrepancies

- M1: the thinktime report is 197 lines by wc -l, not 198 as the
  agent's handoff says. Same +1 counting error as batches 4, 5
  and 6. The G29 report is 185 lines, as stated.
- M2: the G29 report's socket paths ("$XDG_RUNTIME_DIR/at-spi/bus",
  "~/.cache/at-spi/bus") omit the display suffix; actual names are
  bus_97 and bus_98. See the XDG section above.

## What I could not reproduce

- No Wayland/Hyprland on this machine: the fixed _real_click cannot
  run live here (it raises "real click needs a Wayland session").
  My G29 proof is the same chain as the report's: fixed bytes match
  cu.py's left-click commands, a left click focuses the bar live,
  the unit test asserts the exact bytes. End-to-end on the laptop's
  Wayland session is still owed, as the report states.
- No Zen binary here: no Zen run was possible; all live work is
  Firefox 160.0.1.
- LLM think time: unmeasured, no model call on this machine, as the
  report states.
- Real-page scaling of the H2 numbers: unmeasured, fixture only,
  as the report states.
- The last30days-skill install question is outside this council's
  brief; I did not install anything and I make no finding on it.

## Bottom line

- G29 root cause (MCP click sent BTN_RIGHT) is proven live by my
  own reproduction and by the code chain. The fix is correct and
  the regression test holds.
- H2 loop-shape numbers reproduce and the proposed cuts rest on
  ratios that held in my run. The session-setup range does not
  reproduce under load (6,308 ms vs 3,883-4,229 ms) and should be
  presented as load-dependent, not as a stable range.
- The AT-SPI observe-cost claim has no disk evidence and is
  unverified.
- The XDG ordering contention claim did not reproduce; the socket
  location mechanism did, with display-suffixed names.
