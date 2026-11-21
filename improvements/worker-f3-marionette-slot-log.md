# Worker F3 log: Marionette slot failure + Zen restore

Branch: todolist-push. Worker: F3 (Muse fixer). Start: 22:18 21/11/2026 (+07).
Owner: machine handed over, working overnight, do not disturb. Owner is asleep since ~22:27.

## Owner rules in force (new, 21/11 evening)

- 22:22 method: read source code + crawl for the root cause first, then fix at the root. No guessing.
- 22:40 target: whole team to 240 commits before 24:00 today (189 at 22:40). Every small step done = commit + push at once. Quality above all, council + redteam fully.
- 22:45 correction: NEVER click the mouse on workspace buttons or menu buttons on the bar. Switch workspaces by command (hyprctl dispatch in hl.dsp form). Open the Omarchy menu by command (exact launcher command from the Hyprland/Omarchy config, do not guess). Fastest-path-first: CLI first, mouse last.
- 22:47 rule: log EVERY event with time as it happens. Wall-clock Asia/Ho_Chi_Minh + elapsed from F3 start (22:18). Nothing omitted. If the owner asks, the answer is in this log, never "I don't know".

## Root cause (source-proven)

Error: HTTP 500 on POST /session, `TypeError: can't access property "namespaceURI", browserElement is null`, at Marionette newSession (#registerBrowser / #registerWindow).

Source: shipped driver `chrome/remote/content/marionette/driver.sys.mjs` (160,552 B, 4,794 lines, extracted from the laptop's top-level omni.ja, copy at `~/workspace/zen_tab_cleanup/source/driver.sys.mjs-FIREFOX_160_0_RELEASE` on the VM; upstream cross-check FIREFOX_160_0_RELEASE, line numbers identical).

- `#registerBrowser(browserElement)` lines 4608-4623: line 4616 dereferences `browserElement.namespaceURI` with NO null check. Null input throws exactly the observed TypeError.
- `#registerWindow(win, {registerBrowsers})` lines 4634-4645: line 4640 passes `TabManager.getBrowserForTab(tab)` unchecked into `#registerBrowser`.
- `newSession` line 2707: loops every window and every tab with `registerBrowsers: true`. ONE null browser kills the whole session.
- `TabManager.sys.mjs` `getBrowserForTab(tab)` lines 39-41 returns `tab?.linkedBrowser ?? null`. `getBrowsers()` excludes unloaded tabs and filters nulls, but `#registerWindow` does NOT use it.
- Crawl: Bug 1366988 (2017, same `be.namespaceURI` access, same error family). Bug 1342723: `removeTab` sets `aTab.linkedBrowser = null`.

Corrected theory (22:38, after restart): lazy tabs do NOT break `#registerBrowser` (their `linkedBrowser` exists; proven by the restart, Marionette works with ~52 lazy tabs present). The null tab was most likely a tab mid-removal / whose browser element was destroyed (prime suspect, UNPROVEN: the pass-1 cleanup teardown, sacrificial-tab open failed 404 "Browsing context has been discarded", DELETE /session ran while current was a discarded tab). The pre-restart tabbrowser held a zombie tab element with null `linkedBrowser` from ~22:06 through 22:31. The restart rebuilt the tabbrowser fresh and cleared it. The 22:03 to 22:06 change trigger is still unproven. BiDi worked throughout (BiDi `session.new` + `browsingContext.getTree` do not call `#registerBrowser`).

## Event log (chronological, wall-clock +07, elapsed from 22:18)

| Time | Elapsed | Action | Target | Outcome | Coords |
|---|---|---|---|---|---|
| 22:06 | pre-task | Marionette session fail 1 | POST /session | HTTP 500 browserElement is null | - |
| 22:10 | pre-task | Marionette session fail 2 | POST /session | HTTP 500 browserElement is null | - |
| 22:12 | pre-task | Marionette session fail 3 | POST /session | HTTP 500 browserElement is null | - |
| 22:20 | +2m | Marionette session fail 4 | POST /session | HTTP 500 browserElement is null | - |
| 22:22 | +4m | Owner method order received | F1/F2/F3 | Read source + crawl first, then fix at root | - |
| 22:25-22:27 | +7m to +9m | Owner redirect received | Zen restore | Zen unusable, restore it; owner to sleep 22:27 | - |
| 22:29-22:31 | +11m to +13m | VM Python repair (mine) | /usr/lib/python3.12/re/__init__.py | Repaired from CPython 3.12 branch (16,315 B); `re.compile` works; SSH back. VMFIX later confirmed durable (dpkg -V clean). Root cause of the file loss still unknown. | - |
| 22:31 | +13m | Marionette session fail 5 | POST /session via zen_dom.py | HTTP 500 browserElement is null, instant 0.0s | - |
| 22:32-22:33 | +14m to +15m | SSH VM to laptop down, then back | ssh-laptop.sh | Muse verified 22:33: re_ok + SSH_OK. Resume Zen restore at once. | - |
| 22:36:24 | +18m24s | pkill -TERM zen-bin | PID 27958 | Clean exit after 1s. No zen/gecko processes left. Sessionstore NOT rewritten on exit (recovery.jsonlz4 still 22:04). | - |
| 22:36:48 | +18m48s | Relaunch Zen via zen-ai wrapper | zen-ai, detached | New PID 426338. BiDi 200, ports 2828 + 9222 LISTEN. | - |
| 22:37:32 | +19m32s | Marionette session create | POST /session | CREATED in 0.1s (id dfd532f5-7423-4e11-9171-f35410d0a73e). list_tabs 67 tabs in 7.7s, titles empty (lazy). SLOT FIXED. | - |
| 22:38:32 | +20m32s | BiDi tree + screenshot | browsingContext.getTree | 67 top-level contexts. All 13 real tabs present. 39 fixture tabs RESURRECTED by restore (sessionstore 22:04 predates the pass-1 cleanup). | - |
| ~22:40 | +22m | Website-open test | BiDi navigate example.com | PASS. URL https://example.com/, title "Example Domain". | - |
| 22:40:15 | +22m15s | click.py run 1 | BiDi fixture tab row img(120,700) | FAIL: ValueError embedded null byte (Python \0 escape in tr command). Fixed by reading /proc/PID/environ in Python. | img(120,700) |
| 22:40:31 | +22m31s | click.py run 2 | same | FAIL: hyprctl cursorpos -j returned empty JSON (wrong flag position). Patched to cu.hypr(env, "cursorpos"). | img(120,700) |
| 22:41:01 | +22m41s | click.py run 3 | same | FAIL: RuntimeError hyprctl (empty stderr). cu.hypr fell back to hyprctl because env lacked HYPRLAND_INSTANCE_SIGNATURE: the new zen-bin (426338) was launched WITHOUT it. | img(120,700) |
| 22:41:39 | +23m39s | click.py patched + run 4 | BiDi fixture tab row img(120,700) | PASS. Move miss 1.0px, CLICKED in 29ms, cursor (2584,1601). Observe 0ebd63aefe9c: Whitehead Architect Studio whiteboard rendered; selected row was "Offline Whiteboard App" (row positions shifted one row vs the 22:38 screenshot; the click landed on the row at y=700 as displayed at click time, not "BiDi fixture" as labeled in the earlier screenshot). CLICK TEST PASSED: tab selected + content rendered. | img(120,700) global(2584,1602) |
| 22:42:28 | +24m28s | click.py run 5 | Zen workspace-2 rail icon img(15,90) | CLICKED in 35ms, move miss 1.0px. Outcome: switched HYPRLAND workspace to 2 (two Muse chat windows). MIS-TARGET: the rail is the system dock, NOT Zen-internal. Workspace switching itself works. | img(15,90) global(2479,992) |
| 22:43:15 | +25m15s | click.py run 6 | Hyprland workspace 1 img(15,30) | CLICKED in 28ms, move miss 1.0px. Outcome: opened OMARCHY LAUNCHER menu ("What would you like to do?"). CONFIRMED CLICK-MISS (owner saw it ~22:44). (15,30) is the app-launcher button, not workspace 1. | img(15,30) global(2479,932) |
| 22:43:54 | +25m54s | wtype Escape | Omarchy launcher | Launcher CLOSED. Observe 439bfd00ca66 confirmed. (First wtype try used key name "esc", error "Unknown key 'esc'"; correct name is "Escape".) | - |
| 22:44:59 | +26m59s | wtype Super+1 | Hyprland workspace 1 | FAILED, no action: "Invalid modifier name 'super'". | - |
| 22:45:11 | +27m11s | wtype Meta+1 | Hyprland workspace 1 | FAILED, no action: "Invalid modifier name 'meta'". | - |
| 22:45:38 | +27m38s | wtype Logo+1 | Hyprland workspace 1 | Executed, no error. Outcome: opened OMARCHY SYSTEM menu ("Search system...", Reboot / Shutdown / Logout / Screensaver / Suspend / Lock). Logo+1 is bound to the system menu, NOT workspace 1. Second menu-opening miss. No menu item clicked. | - |
| 22:45 | +27m | Owner correction received | F3 | Never click workspace/menu buttons on the bar again. CLI first. | - |
| 22:47 | +29m | Owner log rule received | F3 | Log every event with time as it happens. This log is now the live record. | - |
| 22:47:xx | +29m | wtype Escape | Omarchy System menu | System menu CLOSED (observe 8b3d868f88c9, verified by viewing 22:48: two Muse windows, no menu overlay). | - |
| 22:48 | +30m | Log file created + viewed | worker-f3 log | Log written to improvements/worker-f3-marionette-slot-log.md. Screenshot after-esc3 confirmed System menu closed. | - |
| 22:48 | +30m | Log commit 8a5b18a pushed | todolist-push | Commit "F3: live event log, Marionette root cause + restore + 22:43 click-miss" pushed 072e973..8a5b18a. ls-remote then showed b45f3b82 (another worker pushed after me; my commit is in, ancestry to verify). | - |
| 22:48 | +30m | Owner orders (22:45-22:48, via MEMORY) | F3 + fleet | 22:45 fastest-path-first (CLI, no bar clicks). 22:46-22:47 OPT coordinator: find ONE optimal fix method for the whole error pile, all agents + crawlers + council + redteam. 22:48 Lauren Tan, NO cutting steps. Owner asleep, work overnight, report in the morning. | - |
| 22:49 | +31m | Owner steer (240 target) | F3 | GitHub graph 136 contributions, need 240 before end of day. Commit EVEN MORE and EVEN SMALLER: every small step its own commit, push at once, do not batch. | - |
| 22:49-22:50 | +31m to +32m | Owner steer (cleanup redo) | F3 | Owner screenshot 22:50 proves the 39 fixture tabs came back after the restart. Re-run FULL cleanup with the same keep-list (28 real tabs), verify with a fresh tab list they do not come back. Delete any tab definitely no longer used. | - |
| 22:50 | +32m | Launcher command confirmed from config | bindings.lua | Exact launcher command: `omarchy-menu toggle root` (SUPER+SPACE). Found in ~/.config/hypr/bindings.lua, not guessed. | - |
| 22:50 | +32m | hyprctl activeworkspace | compositor | Active workspace 2 (id 2, eDP-2, 2 windows, last "Muse"). Still on ws2. | - |
| 22:50 | +32m | hl.dsp.workspace introspection via hyprctl eval | hl.dsp.workspace | Methods: swap_monitors, rename, move, change_id, toggle_special. NO goto/switch. (via hl.exec_cmd writing to /tmp/dsp-ws.txt) | - |
| 22:51 | +33m | hl.dsp top-level introspection | hl.dsp | 21 keys. cursor=table, group=table, window=table, workspace=table; dpms/event/exec_cmd/exec_raw/exit/focus/force_idle/force_renderer_reload/global/layout/no_op/pass/release_input_capture/reload_config/send_key_state/send_shortcut/submap=function. focus is a FUNCTION. | - |
| 22:51 | +33m | hl.dsp.focus introspection attempt | hl.dsp.focus | FAILED as expected: pairs() on a function ("bad argument #1 ... got function"). Confirms focus is a function, not a table. | - |

## Notes added after the fact (22:47, from the man page)

- wtype modifier names are: shift, capslock, ctrl, logo, win, alt, altgr. So Super = "logo" (or "win"). The 22:44:59 and 22:45:11 failures were wrong modifier names, not a compositor problem.
- The far-left rail is the Omarchy system dock. Its top item (15,30) is the app launcher. Its numbers are Hyprland workspaces. Zen-internal workspaces are NOT switched from that rail; the owner's complaint about Zen workspace switching is a separate item (Zen-internal), not yet tested.

## Verification status (22:48)

- Marionette slot: FIXED (session 0.1s, 67 tabs listed). PASS.
- Session restore: 67 contexts, all 13 real tabs present. PASS. (LMS login tab opened ~22:26 was never flushed to sessionstore and is lost; login page only, trivially reopenable.)
- Website open: PASS (example.com).
- Click a tab: PASS (29ms, 1.0px miss, content rendered).
- Hyprland workspace switch by rail click: WORKS (22:42:28, ws1 to ws2) but MIS-TARGETED method; bar clicks now BANNED by owner. Return to ws1 by COMMAND is still pending.
- Zen-internal workspace switch: NOT yet tested.
- Tab cleanup redo (39 resurrected fixture tabs + 13 about:blank + httpbin + BiDi fixture 40301): NOT yet done. KEEP Free Claude Code Admin 127.0.0.1:8082 and all real tabs.
- Error-file entry (Marionette failure + 22:43:15 click-miss): NOT yet done.
- Council (3) + redteam over the fix: NOT yet done.

## Open items (in order)

1. (TOP, owner 22:49) Re-run the FULL tab cleanup via Marionette: close the 39 resurrected fixture tabs + the definitely-unused ones among the 28 (13 about:blank, httpbin, BiDi fixture 40301), keep the 13 real tabs (incl. Free Claude Code Admin 127.0.0.1:8082). Verify with a FRESH tab list that they do not come back. Sacrificial tab FIRST, end the session on a live tab.
2. Workspace-switch by command: hl.dsp has no goto. Next: check `hyprctl binds -j` for the Omarchy default workspace binds, and test `hl.dispatch("workspace", "1")` (string form) with immediate activeworkspace verification. Then return to ws1 and verify Zen visible.
3. Add the Marionette failure + the 22:43:15 click-miss to the error file.
4. Council (3) + redteam over the fix. Commit + push each small step at once.
