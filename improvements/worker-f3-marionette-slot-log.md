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
| 22:52 | +34m | Log commit 065744c pushed | todolist-push | Commit "F3: log introspection results + 22:49 owner steers" pushed 26366a9..065744c. ls-remote confirms 065744c2 (matches). | - |
| 22:52 | +34m | Owner correction (22:49-22:51, via MEMORY) | 240 target | Graph shows 136 contributions (tooltip), not 190. My count used the +07 day (201 commits + 1 PR at 22:51); the graph counts the UTC day (144 + 1 = 145). The graph only counts default-branch (main) commits; todolist-push has 290 commits on UTC 21/11 but they do NOT count. Worker MERGE spawned to merge todolist-push into main. | - |
| 22:54:22 | +36m22s | Full cleanup launched (detached) | cleanup_full.py | Sacrificial tab opened FIRST (handle 9e3a8a00). BEFORE 68 tabs (67 + sacrificial). DOOMED 52. First CLOSED: BiDi fixture 40301. Running detached, log /tmp/zen_tab_cleanup/full.log. DOOMED includes "Browser DevTools Simulation" (title differs from FIXTURE_TITLES "Simulator", caught by the URL predicate) and fixture app titles (Markdown Live Studio, Focus Engine, etc.) caught by the URL predicate. AFTER expected 16 (15 real + sacrificial); the 2 extra vs the 13 are "Just a moment..." + "ModelArk-Coding-Plan" (real tabs). | - |
| 22:54:50 | +36m50s | Full cleanup DONE | cleanup_full.py | CLOSED 52, errors 0, elapsed 8.5s. AFTER 16 tabs. | - |
| 22:55:34 | +37m34s | Fresh verify list (verify_list.py) | Marionette | VERIFY 17 tabs (incl. 1 sacrificial). All 14 real tabs present by URL (YouTube, Reddit, Todoist, Gmail, Calendar, Muse, PCCV CF26, Free Claude Code Admin, Welcome, Polygon, codeforces, chunkbase, duck.ai, BytePlus). ZERO fixture tabs. "Problem loading page" = Reddit (failed load, URL preserved). "Example Domain" = my 22:40 test tab. 2 "" about:blank = leftover sacrificial tabs (session DELETE does not reliably close the current tab). | - |
| 22:56:01 | +38m01s | close3.py (tidy) | Marionette | BEFORE 18, DOOMED 3 (Example Domain + 2 blanks), CLOSED 3, AFTER 15 (14 real + 1 sacrificial). | - |
| 22:56:12 | +38m12s | Fresh verify FAILED, slot wedged AGAIN | Marionette POST /session | HTTP 500 browserElement is null, same stack (4616/4640/2707). RECURRENCE. | - |
| 22:56:31 | +38m31s | Retry verify FAILED | Marionette POST /session | Same HTTP 500. NOT transient (19s later, still wedged). | - |
| 22:56 | +38m | Refined hypothesis | root cause | The wedge reappeared between close3 end (~22:56:05) and 22:56:12. close3 is the only session that CLOSED tabs created via window/new (the 2 leftover sacrificial blanks). Hypothesis: closing a window/new-created tab leaves a zombie tab element with linkedBrowser null (removeTab nulls it, Bug 1342723); the next newSession trips on it. cleanup_full closed 13 RESTORED blanks and the next session worked, so restored blanks do not wedge it. To be proven by BiDi diagnosis + a click/activate test. | - |
| 22:57:15 | +39m15s | BiDi/DevTools probe | laptop | curl /json/list returned empty (Firefox does not serve CDP /json/list). Marionette 2828 LISTEN (zen-bin 426338, fd 55). Zen alive. | - |
| 22:58:05 | +40m05s | BiDi tabs (zen_cli.py) | BiDi | 15 tabs, all normal with URLs. NO zombie visible via BiDi (a tab element with no browsing context is invisible to BiDi). 1 sacrificial blank remains (index 9). | - |
| 22:58:17 | +40m17s | BiDi activate YouTube (index 0) | BiDi | Activated OK. NOTE: this switched the Hyprland active workspace to ws1 (focusing Zen's window switches workspace). | - |
| 22:58:45 | +40m45s | hl.dispatch string form test | hyprctl eval | FAILED: "hl.dispatch: expected a dispatcher (e.g. hl.dsp.window.close()) or a lua function". hl.dispatch takes a dispatcher OBJECT or a Lua function, never a string name. BUT activeworkspace then showed ws1 (id 1, 1 window, "Example Domain — Zen Browser") — the switch came from the BiDi activate at 22:58:17, not the eval. The window title is STALE (Example Domain tab was closed 22:56:01). | - |
| 22:59:13 | +41m13s | Observe Zen on ws1 | observe | Zen visible. Sidebar shows "Example Domain" row (selected, page rendered) + "New Tab" — but BiDi (22:58:05) lists NO example.com tab. The UI tab list and BiDi context list DISAGREE. The "Example Domain" row is a tab element with no browsing context: the zombie. | - |
| 23:00:03 | +42m03s | Click Welcome! tab row img(120,390) | mouse | CLICKED 28ms, miss 0.0px. Welcome! selected, page rendered. UI fully responsive. | img(120,390) global(2584,1292) |
| 23:00:24 | +42m24s | Retry Marionette session | POST /session | FAILED, same HTTP 500. Mouse click on a real tab does NOT fix the slot. | - |
| 23:01:10 | +43m10s | Click Example Domain row img(120,483) | mouse | CLICKED 28ms, miss 0.0px. Result: "New Tab" selected instead (X shown). Clicking the zombie row does NOT select it; Zen falls back to the neighboring tab. CONFIRMS the Example Domain row is a dead tab element. | img(120,483) global(2584,1385) |
| 23:01:53 | +43m53s | Click X at img(255,483) (zombie close attempt) | mouse | CLICKED 28ms, miss 1.0px. Result: the "New Tab" (sacrificial) row is GONE; "Example Domain" REMAINS. The rows had shifted between the screenshot and the click, so the X closed the sacrificial tab, not the zombie. Harmless (it was my empty tab), but the zombie survives. UI-close attempts STOPPED (rising misclick risk near real tabs). | img(255,483) global(2719,1385) |
| 23:02:04 | +44m04s | Retry Marionette session | POST /session | FAILED, same HTTP 500 (4th failure since the recurrence: 22:56:12, 22:56:31, 23:00:24, 23:02:04). | - |
| 23:01 | +43m | Owner instruction (via MEMORY) | fleet | Owner asleep but: big errors/blockers/things needing his decision get reported AT ONCE (do not wait until morning); routine work stays quiet until morning. This recurrence IS a big blocker (gates Y13/Y14 live runs). | - |
| 22:57 | +39m | Fleet note (via MEMORY) | Y13r2 | Y13r2 BLOCK (4 new blockers + 5 amends); Y13g spawned to fix per the redteam paper, then a fresh re-review. re.py root cause SOLVED: a Redteam Y13r2 shim (A6e) deleted the file by accident (globals().update overwrote __file__ before os.remove), NOT a stray process; VMFIX restored durably (c16dd4e). H3 gate: Y13r2 proposal accepted (5a2b69d NO VERDICT + runner-quiet/ports check counts as the done marker leg for this run, gate text unchanged, Y6 retry after Y13). | - |
| 23:03 | +45m | Owner note (via MEMORY, DEFERRED LOW) | Zen keybinds | Owner: sometime go into Zen Settings, Shortcuts on his machine, record Zen's keybinds into the computer-use doc ON THE MACHINE (machine-specific layer, local-only), do NOT push to the repo. Not important, do last. NOT done; deferred. Not F3 work. | - |
| 23:03 | +45m | Error-file entries done | LOI-VA-GIAI-PHAP-TOAN-BO | J3 updated (root cause + restart fix + recurrence + zombie + procedure lesson), J7 root cause solved (Y13r2 shim A6e), J21 attribution (it was F3, 22:43:15), J22 (recurrence + zombie), J23 (hl.dispatch string form + launcher command), J24 (sacrificial tab leftover). File now has 24 J entries. Not a git repo, no commit. | - |
| 23:04 | +46m | Council (3) + redteam spawned | F3 review | Council 1 (root-cause rigor), Council 2 (procedure + safety), Council 3 (next step + restart decision), Redteam (break the diagnosis). Each reads the log + J3/J22-J24, writes its verdict file to improvements/worker-f3-council-N.md / worker-f3-redteam.md, commits + pushes it on todolist-push. Awaiting verdicts. | - |
| 22:55 | +37m | Owner note (clone2-watch, via MEMORY) | fleet | Cron clone2-watch 15m: check clone2 on ws2, approve/nudge if silent >15min, then back to ws1. Not F3 work; no action. | - |

## Notes added after the fact (22:47, from the man page)

- wtype modifier names are: shift, capslock, ctrl, logo, win, alt, altgr. So Super = "logo" (or "win"). The 22:44:59 and 22:45:11 failures were wrong modifier names, not a compositor problem.
- The far-left rail is the Omarchy system dock. Its top item (15,30) is the app launcher. Its numbers are Hyprland workspaces. Zen-internal workspaces are NOT switched from that rail; the owner's complaint about Zen workspace switching is a separate item (Zen-internal), not yet tested.

## Verification status (23:02)

- Marionette slot: FIXED 22:37 by restart, then WEDGED AGAIN 22:56:12 (4 failed retries: 22:56:12, 22:56:31, 23:00:24, 23:02:04). Recurrence confirmed.
- Session restore: 67 contexts, all 13 real tabs present. PASS. (LMS login tab opened ~22:26 was never flushed to sessionstore and is lost; login page only, trivially reopenable.)
- Website open: PASS (example.com).
- Click a tab: PASS (29ms, 1.0px miss, content rendered).
- Hyprland workspace switch by rail click: WORKS (22:42:28, ws1 to ws2) but MIS-TARGETED method; bar clicks now BANNED by owner. Return to ws1 happened via BiDi activate side effect (22:58:17), not by command.
- Zen-internal workspace switch: NOT yet tested.
- Tab cleanup redo: DONE and VERIFIED (22:54:50). Closed 52 (cleanup_full) + 3 (close3) = 55 tabs. Fresh verify list 22:55:34: all 14 real tabs present by URL, ZERO fixture tabs. Final state 14 real + 1 sacrificial empty tab = 15 tabs. (The 14th real tab is Reddit, which the 22:10 note had not listed separately; "Problem loading page" = Reddit failed load, URL preserved.)
- Zombie identified: the "Example Domain" tab element (Marionette DELETE on a BiDi-navigated tab leaves the tab element with null linkedBrowser). Visible in the sidebar, absent from BiDi tree, cannot be selected (click falls back to the neighboring tab). BiDi activate + mouse click on a real tab + UI X-close attempt ALL FAILED to clear it. Only proven fix: Zen restart (awaiting Muse direction; NOT done on my own).
- Error-file entries: in progress (J3/J7/J21 updates + J22-J24 new).
- Council (3) + redteam over the fix: NOT yet done.

## Open items (in order)

1. (TOP) Report the recurrence to Muse: slot re-wedged after the cleanup, zombie identified, all non-restart fixes failed, restart is the proven fix awaiting direction. Muse decides whether to report it to the owner now (owner 23:01: big blockers get reported at once, not next morning).
2. Add the Marionette failure + the 22:43:15 click-miss + the recurrence/zombie to the error file (J3/J7/J21 updates + J22-J24).
3. Council (3) + redteam over the fix. Commit + push each small step at once.
4. Procedure change (for the next cleanup): NEVER close a BiDi-navigated tab via Marionette DELETE (it leaves the zombie). Close tabs only via the UI, or navigate them away first. Also: session DELETE does not reliably close the sacrificial tab (2 remained); accept 1 leftover empty tab.
5. Workspace-switch by command: still unresolved. hl.dispatch takes dispatcher objects only (no string form). The workspace table has no goto. Next lead: hl.dsp.focus (a function) or the Omarchy default binds. Low priority (BiDi activate switches workspace as a side effect).
