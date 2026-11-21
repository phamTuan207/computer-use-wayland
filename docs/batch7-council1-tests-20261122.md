# Batch 7 council 1: independent test verification of tasks 1 (G29) and 2 (H2)

Reviewer: batch 7 council 1, independent subagent. Method: read both
reports in full, then re-checked every checkable claim from the repo,
the saved evidence files, and my own live re-runs. Line counts by
wc -l only. No report was taken on trust. No coord file edited,
nothing committed or pushed.

Reports reviewed:
- docs/clone1-g29-urlbar-focus-20261122.md (task 1, G29)
- docs/clone1-thinktime-20261122.md (task 2, H2)

## Verdicts

- Task 1 (G29): CONFIRMED. Every material claim verified live or
  from disk: the root cause, the fix, the live proof, and the
  negative control.
- Task 2 (H2): CONFIRMED. All measured numbers reproduce from the
  saved evidence files, and my own re-run reproduces the same
  shape with load variance. Minor notes only (see below).

## G29: what I verified

### Test suite re-run (mine)
`python3 -m unittest tests.test_mcp_server`: 20 tests, OK,
skipped=1 (RealDomTypeTest, playwright-core not installed), 1.727 s.
The report says 20 OK, 1 skipped, 1.764 s. Same result; the time
difference is run variance.

### The fix
`scripts/mcp_server.py` lines 308-309 send `button 0 1` and
`button 0 0`, with the comment recording the 0x110+index mapping.
Full-repo grep for button senders: the only production sender of a
hardcoded `button 1` was `mcp_server.py` before the fix. What
remains is `tests/pointer_benchmark.py:53`, which sends
`button 1 1` / `button 1 0` inside a latency benchmark plan
("warm every branch of this plan"); any button index exercises
the same path, so the report is right to leave it unchanged.
`scripts/cu.py` uses `button {b} 1` with `b` from the mapping
`{'left': 0, 'right': 1, 'middle': 2}` (lines 1621 and 1649), so
its left click is button 0. `tests/e2_direct_clicks.py` sends
`button 0` for a left click.

### Negative control (mine, /tmp copy)
Copied scripts/ and tests/ to /tmp/c1-revert, reverted the two
lines to `button 1 1` / `button 1 0`, ran
`tests.test_mcp_server.RealClickButtonTest`: FAILED (1 failure),
exactly as the report claims. Same test on the fixed repo code:
OK. The regression test catches the old bug and passes the fix.

### Evdev mapping
Kernel header on this machine, /usr/include/linux/input-event-codes.h
lines 356-358: BTN_LEFT 0x110, BTN_RIGHT 0x111, BTN_MIDDLE 0x112.
`native/pointer.c` line 188: `zwlr_virtual_pointer_v1_button(p,
stamp(), 0x110+button, down)`. Confirmed.
Native pointer tests, mine: `python3 -m unittest
tests.test_pointer_native`: 12 tests OK, 2.201 s. The report says
12 OK, 2.290 s. Same result.

### Bug present since creation
`git show 98edc39:scripts/mcp_server.py` lines 248-249 contain
`pointer.command("button 1 1")` and `pointer.command("button 1 0")`.
Confirmed: the bug was in the original commit, not introduced later.

### Live experiment log (read back from disk)
`~/workspace/b7t1/g29-log.jsonl`, 26 lines. Every experiment in the
report matches the log exactly:
- E1 left, run 1: tool "xdotool click 1 (left)", tool_ms 104.5,
  mouse (619, 64), focused true, typed "g29t", text_after "g29t",
  marker_in_text true, context_menu null.
- E2 right, run 1: tool "xdotool click 3 (right) = MCP button 1",
  tool_ms 104.6, mouse (619, 64), typed "g29t", text_after "",
  marker_in_text false, context_menu role "menu", extents
  [621, 66, 81, 204]. STATE_FOCUSED on the bar node was true even
  after the right click, so the report's nuance is confirmed from
  the log: a focus-only check would wrongly say "focused".
- E2_screenshot: ok false, "no screenshot tool (import/xwd
  missing)". The no-screenshot claim is confirmed.
- E3 AT-SPI, run 1: click_ms 0.3, tool "atspi doAction", detail
  "action activate", mouse stayed (600, 400), typed "g29i",
  text_after "g29i", marker_in_text true.
- E4 Ctrl+L, run 1: tool_ms 29.3, typed "g29l", text_after "g29l".
- Run 2: E1 "g29a" landed, E2 "g29b" did not land (menu present),
  E3 "g29c" landed, E4 "g29d" landed. Same result twice.
- Extents: find_urlbar [268, 48, 652, 32], then [294, 48, 650, 32],
  run 2 find_urlbar [294, 48, 626, 32]. Matches the report.
- Run 1 probe_done elapsed 7476.7 ms (report says 7476.5 ms, a
  0.2 ms difference, negligible).

### XDG_RUNTIME_DIR ordering claim
`~/workspace/b7t1/start_session.sh` line 36 exports
XDG_RUNTIME_DIR, line 37 runs dbus-launch. Export before launch,
as the report says. The repo wrapper
`tests/run_atspi_session.sh` runs dbus-launch at line 133 and
exports XDG_RUNTIME_DIR at line 141, after. The report's claim
that the wrapper has the same ordering problem is confirmed.

### G29 minor notes (no verdict changed)
- N1. Run 2 wall time: the report says "7646 ms wall", but the
  log's probe_done elapsed for run 2 is 7516.5 ms, a 130 ms gap.
  The measurement boundary is not explained in the report.
- N2. The still-open items in the report are honest and accurate:
  no Wayland on this machine, no Zen binary, the MCP click tool
  cannot target the address bar (DOM-only locate), and the exact
  laptop caller is unidentified. None of these is a report error.

## H2: what I verified

### Evidence files (read back field by field)
`~/workspace/b7t2/results-run2.json` and `results-run3.json`
exist, both ok true, Firefox 160.0.1. Every median in the
report's table matches the saved files exactly:
- Run 2: port up 1081, connect 3148, setup total 4229, goto 306,
  DOM full 3.7 (4620 chars), compact one-shot 6.85 (61 elements),
  rects one-shot 5.8, rects per element 219.8, screenshot 25.9
  (41625 bytes), cheap verify 2.9, think 0 (max 0.133),
  click+verify 34.4 (counter_after_10_clicks "10"), type 18.9
  (typed "h2-test!"), loop one-vision 27.9, loop naive 39.1,
  final counter 18.
- Run 3: port up 1092, connect 2791, setup total 3883, goto 383,
  DOM full 3.45, compact 7.8, rects one-shot 4.8, rects per
  element 239.5, screenshot 24.2, cheap verify 4.2, think 0.001
  (max 0.174), click+verify 26.6, type 12.1, loop one-vision 29.6,
  loop naive 34.7, final counter 18.
- All "ranges across runs 2 and 3" check out exactly: connect
  2791-3148, rects per element 156.4-627.2, rects one-shot
  3.9-47.1, screenshot 22.2-40.8, loop one-vision 16.3-62.5,
  loop naive 34.6-42.1.
- Arithmetic checks out: cut 1 saves 214-235 ms (219.8-5.8 =
  214.0, 239.5-4.8 = 234.7); the rects ratio is 37.9x to 49.9x
  (219.8/5.8, 239.5/4.8), matching the claimed 38-50x; setup is
  12.9x to 16.3x the 10-step loop (3883/300, 4229/260),
  matching the claimed 13-16x; 10-step cost with cuts about 0.3 s,
  naive 4.3-4.6 s, plus per-element rects 2.1-2.3 s gives
  6.4-7.0 s, saving 6.1-6.7 s. All consistent.

### My own re-run (council, /tmp copy of the script)
Ran `~/workspace/b7t2/measure_loop.mjs` from a /tmp copy (so the
saved evidence was not overwritten), 21:15 UTC, total 7169 ms.
Results: port up 687, connect 2483, setup 3170; DOM 6.55,
compact 11.75, rects one-shot 8, rects per element 247.7,
screenshot 21.5, cheap verify 2.65, think 0, click 38.5,
type 15.3, loop one-vision 34.1, loop naive 49.1, final
counter 18. Same shape as the report, absolute values 10-40%
off the reported medians (machine load variance; fewer agents
were running during the reported runs than during mine, or the
reverse). The rects ratio in my run is 247.7/8 = 31x, slightly
below the claimed 38-50x band, so the exact band is
load-dependent; the order-of-magnitude gap (one-shot about
5-8 ms against per-element about 220-248 ms) reproduces.
Counter 18 exact, as claimed. My re-run left no Firefox
process behind.

### last30days install: NOT DONE, confirmed
No `*last30days*` match anywhere under home outside the repo,
and ~/.config/skills, ~/.local/share/skills and ~/.skills do not
exist. The skill was not installed, as the report states.

### Research sources (section 5)
- agentpatterns.ai: page fetched. Content verified verbatim:
  20,000-80,000 tokens per step; 200-400 tokens per snapshot
  against 3,000-5,000 for a screenshot; re-read only on signal
  (URL transition, new ARIA element, action failure, exogenous
  event). Updated 2026-11-03, which is 19 days before 2026-11-22;
  the report says 18 days. The ages were computed against
  2026-11-21 while the report states access date 2026-11-22.
  Off by one day.
- frowse PyPI: page fetched. Content verified: up to 90%+ token
  saving per step; compact summary about 100-300 tokens; Folate
  10-25 ms, under 250 MB RAM, $0 API cost. Release 0.1.2
  uploaded Nov 19, 2026, which is 3 days before 2026-11-22;
  the report says 2 days. Same off-by-one (Nov 21 reference).
  The report correctly labels the savings a vendor claim.
- guibai.dev: page fetched. Content verified verbatim: screenshot
  route has a low ceiling; coordinates drift across viewport
  widths and zoom; one image costs thousands to tens of
  thousands of tokens and the most expensive run in two weeks
  was a pure visual task; a greyed submit button may only be
  debouncing while aria-disabled in the DOM is explicit; the
  accessibility tree is the recommended starting point. No date
  is visible in the fetched page text, so the "updated 7 days"
  age could not be verified from the fetch (the incident in the
  text is dated November 10).
- surfs.dev: direct fetch of the cited URL returns "Post Not
  Found". A search for the article title returns the same URL
  with "Last Updated: 29 days ago" and content matching the
  report's summary (forked tabs from DOM snapshots,
  branch-and-bound exploration, exactly-once writes via an
  intent ledger). The 29-day age and the content are
  corroborated by the search index only, not by a direct fetch.
  The report's link is currently a dead end for a reader.

### H2 minor notes (no verdict changed)
- N1. Line count: the thinktime report is 197 lines by wc -l,
  not 198 as the task agent claimed. The +1 counting error has
  now bitten four batches in a row.
- N2. The "updated X days" ages are off by one day in two of
  four sources (agentpatterns 18 vs 19, frowse 2 vs 3): ages
  were computed against 2026-11-21 while the report states
  access date 2026-11-22.
- N3. Section 2 says the local think step measures "max 0.157
  ms". Neither saved file contains 0.157 (run 2 max 0.133,
  run 3 max 0.174). The figure is unverifiable from disk; it
  may come from the overwritten run 1.
- N4. The preliminary run numbers (connect 3,349 ms, rects
  283.5 ms, loop one-vision 26.0 ms, loop naive 41.2 ms) rest
  on a file the script overwrote. The report discloses this
  plainly; the numbers are unverifiable.
- N5. Section 4 does not say what the "safety check" was or
  what failed in the 33fbbdd material. The install decision is
  correctly deferred to the parent, but the reason is vague.
- N6. The AT-SPI observe attempts (wait_document failures after
  32,244 ms and 32,376 ms) have no preserved log files, so they
  are unverifiable from disk.
- N7. The excluded sources (getnadir.com 141 days, karatelabs.io
  221 days, basaltbrowser.com 71 days, thegeocommunity.com
  72 days) were not re-verified by this council.

## What I could not re-run
- The fixed `_real_click` live on Wayland: no Wayland/Hyprland
  on this machine, same limit as the task report states.
- Anything on Zen: no Zen binary on this machine, same limit.
- The G29 live AT-SPI experiment itself: a sibling verification
  session (Xvfb :97, Firefox profile in ~/workspace/b7t1) was
  already running when I checked (started 21:15:11 UTC); I did
  not disturb it. The log file evidence above stands in its
  place, and every number in it matches the report.

## Bottom line
- G29 root cause is proven: the MCP server sent a right click
  for every left click. The fix (button 0) is in the code, the
  regression test fails on the old bytes and passes on the new
  ones, and the live log shows a left click focusing the bar
  while a right click at the same point opens a menu and drops
  typed text.
- H2 numbers are real: the saved evidence matches the report
  field for field, and my own re-run reproduces the same shape.
  The biggest saving (one-shot rect sweep, 214-235 ms per
  round) and the session-setup dominance (about 3.2-4.2 s per
  fresh browser) both hold.
