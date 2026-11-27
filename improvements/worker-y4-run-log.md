# Worker Y4 run log - agy-q2 live run on Zen

- Worker: Y4 (independent runner, Muse)
- Started: 2026-11-21 17:52 +07
- Task: run agy-q2 test-01..10 LIVE on the owner's Zen, sequentially, DOM-verified.
- Runner: tests/realistic/run_agyq2.py (new, modeled on run_fcck.py / run_agyq.py)
- Server: /tmp/worker-y4-server on laptop, port 8768, WD_PORT 4448
- Lock: flock on ~/.cache/agent-computer-use/zen_dom.lock (30 min wait cap)
- Pre-run checks: Zen PID 27958 alive since 15:31 with --remote-debugging-port=9222 --marionette; geckodriver present; lock free; no other runner active.
- Static fixture review before run: no confirm() dialogs; test-03 math checks out (16/28=57% initial, 23/35=66% final); test-05 renderGrid runs on load so count is 6 not 5; test-09 has no real setInterval so clock checks are deterministic; test-01 circle r = input W; test-06 item ids are slugified filenames.
- Simulator (simulate.mjs) NOT runnable on VM: needs puppeteer-core, not installed. Static review substituted.

## Progress
- 17:52: files shipped to laptop, run launched detached (PID 175805).
- 17:52: FIRST RUN FAILED 0/2 and aborted. q01 and q02 both failed the same way: body visible=False, then "element not interactable / could not be scrolled into view" on the first type/click. Root cause of the ABORT (not of the failure): my wd_failures heuristic counted any error containing the word "session", and every WebDriver error URL contains "/session/<id>/...". Fixed: only session-CREATION failures count toward the abort threshold.
- 17:53-18:00: diagnosis via probes (probe_y4, y4b, y4c, y4d), all read-only except navigating test tabs:
  - body computed visibility:hidden on NEW tabs (rect non-zero, display block, hasFocus true, visibilityState visible). All 22 pre-existing tabs visible. window.focus() did not fix it. Persisted 5+ s.
  - Not fixture-specific (q02 fixture AND example.com both hidden), not localhost-specific.
  - Reusing a pre-existing about:blank tab + goto: body VISIBLE, click OK, type OK.
  - Switch-away-and-back did not un-hide (probe d's fresh tab was visible from the start; the hidden state had cleared by itself ~17:59, right after a real click in the reused tab).
  - Side findings: Hyprland IPC socket unresponsive the whole time (hyprctl version/monitors/clients all hang until timeout; socat to .socket.sock also hangs). Zen PID 27958 alive, Marionette fine. One user tab has an open alert (tab [4], "unexpected alert open" on eval) - never touched.
- 18:01: PAUSE ORDER from parent. Owner's physical keyboard + mouse stopped responding ~1 min during probes y4b/y4c/y4d (17:57-18:00), self-recovered 18:00. Likely cause: tab navigation stole window focus mid-use. Rule going forward: NEVER open/navigate/switch tabs in the user's Zen while the user is at the keyboard. The rerun is prepared but NOT launched; it waits for a resume order.
- 18:01-18:05 (non-driving work only): runner fixes below, static fixture review, rerun prepared.

## Runner changes to survive the hidden-body incident (run_agyq2.py)
1. Abort heuristic fixed (see above): only session-creation failures count; a step failure never aborts the suite after 2 tests.
2. Shared visible test tab (bootstrap_tab): instead of window/new per test, all 10 tests share ONE pre-existing visible tab (about:blank preferred, else any tab already on the test origin). Each test still gets a FRESH WebDriver session, clears storage, and reloads the fixture, so test isolation is kept. The tab is returned to about:blank at suite end and never closed by session cleanup.
3. ensure_visible(d, r) recovery: after open, if body is not visible, switch away to a different tab and back, window.focus(), wait 2s, re-check. If still hidden, the test fails with an explicit driver-state error ("test tab body still hidden after recovery"), never a fake fixture verdict.
4. Server reuse fix: run_live.start_server only reuses when the clone1 fixture answers, so a relaunch would try to bind 8768 twice and die EADDRINUSE (a persistent probe server is listening there). Local start_server() now probes the agy-q2 fixture first and reuses the listening server.
5. Probes kept as evidence: tests/realistic/probe_y4.py, probe_y4b.py, probe_y4c.py, probe_y4d.py.

## Static fixture review (no live driving, all 10 specs + fixture code read)
- q01: circle r = input W; line x2=x+w, y2=y+h; undo pops history stack. OK.
- q02: shopping list aggregates 4 (salmon) + 4 (pancakes) + 3 (smoothie) = 11 unique items, >= 5 required. OK.
- q03: math verified: 16/28 = 57% initial, 23/35 = 66% final; streak ids streak-deep-work-sprint / streak-water; select values are the category names. OK.
- q04: initial 1200+70+145.50+60 = $1475.50; only 1 initial Groceries row, so filter = 2 after adding. Select values "Tech"/"Groceries"/"all". OK.
- q05: renderGrid runs on load so count is 6 (HTML hardcodes 5); Alice + David + Frank = 3 Engineering; no confirm() dialogs anywhere. OK.
- q06: Download buttons only flip a flag and re-render, NO real file download, no popup. OK.
- q07: temps Tokyo 18, London 12, HCMC 32, Reykjavik -2 "Snow Showers"; Math.round conversions 64F/54F/90F. OK.
- q08: submit button display:none until Q5; score 5/5 from correct answers. OK.
- q09: no setInterval at all, Start only toggles a flag, so clock checks are deterministic; setMode resets display. OK.
- q10: preview updates on input events; initial message "Live preview will appear here...". OK.
- No fixture bug found statically. The 0/2 first run was a driver/window state failure, not a fixture failure.

## Rerun plan (PREPARED, NOT LAUNCHED - awaiting resume order)
- Preconditions: owner NOT at the keyboard (confirm before launching); lock free; no other runner active.
- Laptop already has: /tmp/worker-y4-server/ with fixtures + latest run_agyq2.py (re-shipped 18:05), persistent http.server on 8768 (runner reuses it).
- Launch (detached, under flock, one SSH call):
  setsid nohup flock -w 1800 ~/.cache/agent-computer-use/zen_dom.lock -c "cd /tmp/worker-y4-server && LIVE_SERVER_ROOT=/tmp/worker-y4-server LIVE_SERVER_PORT=8768 LIVE_LOG=/tmp/worker-y4-live.jsonl WD_PORT=4448 python3 run_agyq2.py all > /tmp/worker-y4-run.log 2>&1; echo EXIT:\$? >> /tmp/worker-y4-run.log" > /tmp/worker-y4-launch.log 2>&1 < /dev/null & disown
- Then poll /tmp/worker-y4-run.log with short SSH calls; write tests/realistic/RUN-REPORT-AGYQ2-20261121.md; commit + push on todolist-push.
- Known open question for the report: the hidden-body incident self-cleared and its root cause is NOT proven (candidates: new tabs in an inactive window; Hyprland IPC wedge at the same time). Report it as an observed driver failure mode with the workaround, not as a fixed bug.
