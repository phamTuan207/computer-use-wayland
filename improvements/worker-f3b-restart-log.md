# Worker F3b log: second restart + discriminating trigger test

Branch: todolist-push. Worker: F3b (Muse fixer), continuing F3 (9ebdd500).
Start: 23:14 21/11/2026 (+07). Owner asleep; do not disturb.

## State inherited from F3

- Zen PID 426338 (restarted 22:36, BiDi 9222 + Marionette 2828 LISTEN).
- Marionette slot WEDGED since 22:56:12 (newSession HTTP 500 'browserElement is null', 4 failures).
- Root cause SOURCE-PROVEN: driver.sys.mjs #registerWindow line 4639 passes
  TabManager.getBrowserForTab(tab) unchecked into #registerBrowser line 4616
  (null dereference). Restart fixed it once (22:36, session in 0.1s).
- Suspected zombie: 'Example Domain' sidebar row, absent from BiDi tree 22:58:05,
  click on its row falls back to the neighboring tab. HYPOTHESIS, not proven
  (Council 1/2/3 AMEND + redteam BLOCK, 23:06-23:10; B2/B3/B5/B7 open).
- F3's 23:01 UI X-close closed the WRONG tab (sacrificial New Tab) after a row
  shift. Do NOT UI X-close any row again.
- Council 3 recommends a second restart now; Muse authorizes it.
- 14 real tabs + 1 sacrificial empty tab expected at start (verify 22:55:34);
  the sacrificial was closed by F3's misclick at 23:01:53, so the count may be 14.

## Owner rules in force

- 22:45: NEVER click workspace/menu buttons on the bar; workspace/menu by command only.
- 22:47: log EVERY event with time as it happens (wall-clock +07 + elapsed).
- Commit small and many on todolist-push, verify via ls-remote.
- Never ydotool; no em/en dashes; never touch /usr/lib or any system path;
  never write outside the repo worktree and /tmp test copies.
- 23:01: big errors/blockers get reported at once; routine work stays quiet
  until morning.

## Event log (chronological, wall-clock +07, elapsed from 23:14)

| Time | Elapsed | Action | Target | Outcome | Coords |
|---|---|---|---|---|---|
| 23:14:50 | +0m00s | F3b start; read F3 log + redteam paper | improvements/ | F3 log + redteam read. Evidence dir present on VM (f3-evidence/). | - |
| 23:15:00 | +0m10s | Zen PID check | laptop ps | PID 426338 alive, 38:05 old. BiDi 9222 + Marionette 2828 expected. | - |
| 23:15:20 | +0m30s | BASELINE BiDi tabs | zen_cli.py tabs | 13 contexts, saved to improvements/f3-evidence/bidi-tabs-231520.json. Present by URL: 12 of 14 real tabs. MISSING vs 22:58 list: Polygon + codeforces (both had contexts at 22:58). ADDED: Example Domain at index 9 (https://example.com/). No about:blank (sacrificial gone, closed 23:01:53 as expected). | - |
| 23:15:20 | +0m30s | BASELINE recovery.jsonlz4 | sessionstore-backups | mtime 2026-11-21 22:55:45, size 2,955,016 B; recovery.baklz4 same minute, 2,954,984 B; previous.jsonlz4 15:19, 7,734,778 B. Last flush 22:55:45 is AFTER cleanup_full (22:54:50) and the 22:55:34 verify, BEFORE close3 (22:56:01). A restart now restores the 22:55:45 state; fixtures closed before the flush should NOT resurrect (to confirm by parsing the file). sessionstore.jsonlz4 (clean-exit file) does NOT exist in the profile root. | - |
| 23:16:35 | +1m45s | BASELINE Example liveness | zen_cli.py page --tab 9 | Example Domain tab is LIVE: BiDi reads real visible page text ("This domain is for use in documentation examples..."). The zombie-as-Example-Domain theory is REFUTED: a tab element with null linkedBrowser cannot serve DOM text. The null-browser tab is something else (unknown). Also NOTE: between 22:58 and 23:15, Polygon + codeforces LOST their BiDi contexts with no user action (tab discard suspected, unproven); Example GAINED one (most likely loaded when F3's 23:01:53 X-close of the sacrificial tab made Zen select the neighboring Example row). | - |
| 23:17:07 | +2m17s | BASELINE observe | computer-use observe eDP-2 | id 77cf7aab579f. Screen is on Hyprland ws2 (two Muse chat windows), Zen not visible. No action taken on it. | - |
| 23:18:05 | +3m15s | BASELINE BiDi activate YouTube | zen_cli.py activate 0 | OK (first try failed: activate takes a positional index, not --tab). Switched the screen to ws1 / Zen as a side effect (same as F3 22:58:17). | - |
| 23:18:20 | +3m30s | BASELINE observe Zen | computer-use observe eDP-2 | id 0dc2b9aa84e0. Zen in front, YouTube selected and rendered. Sidebar (workspace "zen basics") text rows: PCCV CF26, Free Claude Code Admin, Welcome!, Example Domain, Biome Finder, Gamerule keepInventory, ModelArk-Coding-Plan. Polygon + codeforces rows NOT visible in this workspace (may be in another Zen workspace or discarded; sessionstore parse will settle it). The other 6 real tabs sit in the top icon grid (pinned). | - |
| 23:18:49 | +3m59s | BASELINE Marionette probe (curl) | curl POST 127.0.0.1:2828/session | HTTP 000 instantly, twice (with and without --noproxy). NOT a slot signal: port 2828 is the raw Marionette protocol port, not HTTP (ss confirms LISTEN, zen-bin 426338 fd 55). Lesson: never probe 2828 with curl. | - |
| 23:19:18 | +4m28s | BASELINE Marionette probe (raw socket) | python3 socket 2828 | TCP connects; server sends the greeting `50:{"applicationType":"gecko","marionetteProtocol":3}`. Listener ALIVE. | - |
| 23:19:49 | +4m59s | BASELINE Marionette newSession | zen_dom.py list (geckodriver 4444) | 5th failure since the recurrence: HTTP 500, same error. FULL STACK TEXT captured (closes redteam A2): `#registerBrowser@driver.sys.mjs:4616:38`, `#registerWindow@driver.sys.mjs:4640:30`, `newSession@driver.sys.mjs:2707:31`. Slot STILL WEDGED. Note: the Example tab being alive means the null tab is elsewhere; the wedge cause is now UNKNOWN again, not Example. | - |
| 23:19:06 | +4m16s | MEMORY update (outside this task) | parent context | OPT DONE (optimal-fix-method, 202 lines, 6 commits); clone2-watch cron MISSED its 23:11 run (still running 5+ min, no log); owner himself switched to ws2 to approve. ZK probe: Zen keybinds live in customKeys.json in the profile (3 custom keys). Owner is AWAKE again (on ws2). F3b work stays BiDi/CLI; the one UI step (step 2 right-click) is quick and authorized. | - |
| 23:21:22 | +6m32s | STEP 2 right-click Example row | rclick.py 145 455 | RIGHT-CLICKED in 29ms, miss 0.0px. Context menu opened (observe 2eb2d3dbb305). rclick.py is new (copy of click.py with button 1), scp'd to /tmp/zen_tab_cleanup/. | img(145,455) global(2609,1357) |
| 23:21:52 | +7m02s | STEP 2 click Close Tab (1st try) | click.py 195 946 | CLICKED 28ms, miss 1.4px. NO EFFECT: menu stayed open, Example tab still in BiDi list. Cause found by visual grounding on the menu screenshot: my y-estimate was 18px low; (195,946) is the DISABLED "Close Duplicate Tabs (X)" row, "Close Tab" is at y=928. Lesson: never estimate a menu row y by eye; ground it. | img(195,946) global(2659,1848) |
| 23:23:35 | +8m45s | STEP 2 click Close Tab (2nd try) | click.py 194 928 (grounded) | CLICKED 28ms, miss 1.0px. Example Domain tab CLOSED: BiDi now 12 tabs, no example.com. The 12 are the 14 real tabs minus Polygon + codeforces (still context-less). | img(194,928) global(2658,1830) |
| 23:23:43 | +8m53s | STEP 2 newSession after close | zen_dom.py list | 7th failure since the recurrence: same HTTP 500, same stack. Right-click Close Tab on Example did NOT heal the slot. Step 2 EXHAUSTED; proceed to step 3 (restart). | - |
| 23:24:01 | +9m11s | Sessionstore parse attempt 1 | parse_sessionstore.py (ctypes liblz4) | FAILED: LZ4_decompress_safe -3. Cause: mozLz4 = magic + uint32 LE decompressed size + raw block; my parser fed the size bytes as block data. Also lz4 CLI: "Unrecognized header" (payload is a raw block, not a frame). Fixed the parser (skip 12 bytes, use the size field). | - |
| 23:24:46 | +9m56s | Sessionstore parse attempt 2 | parse_sessionstore.py (fixed) | SUCCESS. recovery.jsonlz4 (22:55:45) = 1 window, 68 tabs, selected=11, closedTabs 0. ZERO fixture tabs (the 22:54 cleanup's 52 closes ARE in the flush, so a restart should NOT resurrect fixtures). All 14 real tabs present in the file, INCLUDING Polygon (w0t52) + codeforces (w0t53): they are lazy/discarded (no BiDi context), NOT closed, NOT lost. 7 about:blank tabs (w0t16/23/24/30/37/42/51). 2 YouTube tabs (w0t0/1). Example at w0t50 (will resurrect on restart, as will the 7 blanks). The owner's other real tabs are all present and untouched. Full tab list NOT copied into this log (personal tabs stay out of the repo). | - |
