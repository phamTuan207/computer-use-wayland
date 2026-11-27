# Zen opencode-council prefs: apply report

- Date: 2026-11-24 (times Asia/Ho_Chi_Minh)
- Work started ~20:43, finished ~21:07 (elapsed ~24 min)
- Operator: council-decision applier (subagent)
- Machine: Omarchy laptop (user the owner), Zen run profile `/home/james/.config/zen/ae59l0ak.Default (release)/`
- No crash test was run (no kill -9). No commit made (coordinator handles git).
- Nothing else was applied: only the 13 council-approved prefs. ZCode untouched. No OpenRouter.

## 1. Prefs applied

Backup first: `user.js` copied to `user.js.bak-council-20261124` (760 bytes, md5 fde3e441ef3f593991af3c9da80d58c2).
Then appended 14 lines (1 comment header + 13 prefs). New `user.js` is 1566 bytes, md5 f74d47c48fb3f563bddb7b41ffe5561b, mtime 20:43.

```
// 2026-11-24: opencode council decision - crash/session stability prefs for R3-L3 run.
user_pref("toolkit.startup.max_resumed_crashes", -1);
user_pref("browser.sessionstore.max_resumed_crashes", 10);
user_pref("browser.warnOnQuit", false);
user_pref("browser.tabs.warnOnCloseOtherTabs", false);
user_pref("dom.max_script_run_time", 0);
user_pref("dom.max_chrome_script_run_time", 0);
user_pref("telemetry.fog.init_on_shutdown", false);
user_pref("browser.tabs.unloadOnLowMemory", false);
user_pref("dom.ipc.processPriorityManager.enabled", false);
user_pref("threads.lower_mainthread_priority_in_background.enabled", false);
user_pref("browser.pagethumbnails.capturing_disabled", true);
user_pref("network.captive-portal-service.enabled", false);
user_pref("network.connectivity-service.enabled", false);
```

Syntax check before restart: 17 `user_pref(` lines total (4 pre-existing + 13 new), zero lines failing the
`user_pref("name", value);` pattern. The 4 pre-existing prefs (`browser.shell.checkDefaultBrowser`,
`toolkit.legacyUserProfileCustomizations.stylesheets`, `remote.prefs.recommended`,
`app.update.enabled`) were left untouched.

## 2. Restart log (ONE controlled restart)

Method: clean quit via SIGTERM to the main process (no kill -9), wait for exit, relaunch via the
`zen-ai` wrapper (`/home/james/.local/bin/zen-ai`, supplies `--remote-debugging-port=9222 --marionette`).
Relaunch used the graphical-session env captured from the old process
(`WAYLAND_DISPLAY=wayland-1 DISPLAY=:0 XDG_RUNTIME_DIR=/run/user/1000
DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus`). Full log at `/tmp/zen-council-restart.log` on the laptop.

| Time (+07) | Event |
|---|---|
| 20:44:29 | SIGTERM sent to old PID 404548 (RSS before: 644264 KB) |
| 20:44:30 | All zen-bin processes exited (after 2 s) |
| 20:44:30 | Ports 9222/2828 free; relaunched zen-ai (launcher pid 788926) |
| 20:44:31 | New zen-bin PID 788926, ports 9222 + 2828 listening (after 2 s). RESTART_OK |

Total restart downtime ~2 s. Old process had been running since 19:59:31.

## 3. Pre-restart state (recorded 20:43)

- PID 404548, started 19:59:31, elapsed 43:19, RSS 642064 KB
- Ports 9222 (BiDi) and 2828 (Marionette) listening on 127.0.0.1
- Tabs: 72 total, 1 window, 49 pinned, 0 tabs without entries (counted from
  `sessionstore-backups/recovery.jsonlz4`, full URL list saved in the pre-restart check)

## 4. Post-restart state (21:06:49)

- PID 788926, elapsed 22:18, RSS 663052 KB (644908 KB at 01:18 elapsed, 20:45:48)
- Ports 9222 + 2828 listening on 127.0.0.1 (re-confirmed 21:06:09 and 21:06:49)
- Tabs: 72 total, 1 window, 49 pinned, 0 tabs without entries

## 5. Verification (a-e)

### (a) Version still 1.24.3b — PASS
- `/opt/zen-browser-bin/application.ini`: `Version=1.24.3b`, `BuildID=20261118023529`
- BiDi `session.new` capabilities agree: `browserName: zen`, `browserVersion: 1.24.3b`,
  `moz:buildID: 20261118023529`, `userAgent: Mozilla/5.0 (X11; Linux x86_64; rv:160.0) Gecko/20100101 Firefox/160.0`

### (b) Ports 9222 / 2828 listening — PASS
- `ss -tln`: `127.0.0.1:2828` and `127.0.0.1:9222` LISTEN, owned by zen-bin PID 788926.
  (One transient check at ~21:05:54 showed empty ps/ss output; the immediately repeated check
  showed the process and ports alive, and elapsed time confirms the process ran continuously
  since 20:44:31. Treated as a transient observation glitch, not a restart.)

### (c) Tab set restored — PASS (72/72, 0 lost)
- Pre-restart: 72 tabs. Post-restart: 72 tabs, same 1 window, same 49 pinned, same domain mix.
- Full URL-list diff pre vs post shows exactly ONE difference, and it is NOT a lost tab: one
  GitHub tab's current entry changed from `https://github.com/phamTuan207/computer-use-wayland`
  to `https://github.com/phamTuan207` (a within-tab navigation, repo page to user profile page).
  The tab itself is present. My probes never navigated any user tab, so this was not caused by
  this task (most likely the owner navigating, or a post-restore reload). No tab failed to restore.

### (d) The 13 prefs effective — YES, all 13 (9 in prefs.js + 4 equal to build defaults)
- `prefs.js` (flushed 20:45, 20:50, 20:57, 20:59, 21:04; 27171 bytes) contains 9 of the 13
  with exactly the council values:
  - `toolkit.startup.max_resumed_crashes = -1`
  - `browser.sessionstore.max_resumed_crashes = 10`
  - `browser.warnOnQuit = false`
  - `browser.tabs.warnOnCloseOtherTabs = false`
  - `dom.max_script_run_time = 0`
  - `dom.ipc.processPriorityManager.enabled = false`
  - `browser.pagethumbnails.capturing_disabled = true`
  - `network.captive-portal-service.enabled = false`
  - `network.connectivity-service.enabled = false`
- 4 names are absent from `prefs.js`:
  - `dom.max_chrome_script_run_time` (council: 0)
  - `telemetry.fog.init_on_shutdown` (council: false)
  - `browser.tabs.unloadOnLowMemory` (council: false)
  - `threads.lower_mainthread_priority_in_background.enabled` (council: false)
- Why absent: Firefox only writes user prefs to `prefs.js` when they differ from the build default.
  Proven by a clean scratch-profile experiment on this exact build (headless Zen,
  fresh profile in `/tmp/zen-scratch-profile`, user.js with only these 4 prefs at council values
  plus control `browser.warnOnQuit=false`; started 21:04:58, SIGTERM 21:05:08, exited 21:05:09):
  the control appeared in the scratch `prefs.js`, the same 4 did NOT — with no remote session,
  no agent activity, and no prior state. So on this build these 4 council values EQUAL the
  build defaults, and the effective value in the running browser IS the council value.
  Independent corroboration: `browser.tabs.unloadOnLowMemory` default `false` was confirmed in
  the shipped `browser/omni.ja` `defaults/preferences/firefox.js`. All 13 council values are
  also exactly the values in the remote agent's shipped recommended-prefs list
  (`chrome/remote/content/shared/RecommendedPreferences.sys.mjs` in the main `omni.ja`).
- Verdict: all 13 prefs are effective at the council values. The `prefs.js` file alone shows 9/13;
  the other 4 are effective via build defaults (scratch-profile proof above).

### (e) BiDi works, session ended cleanly — PASS
- `session.new` + `session.end` via `ws://127.0.0.1:9222/session`, run three times (20:50, 20:54,
  final 21:07), all succeeded; final session `35c95700-b08d-4351-b66e-5389f4186e94` ended with
  `BIDI_SESSION_END_OK`. No BiDi session left open; the runner slot is free.

## 6. Incidents during verification (all resolved, no lasting effect)

1. A BiDi probe that tried to navigate to `about:config` failed (Firefox forbids WebDriver
   navigation to `about:config`, in both BiDi and Marionette) and its script exited without
   `session.end`. The orphaned session blocked new sessions ("Maximum number of active sessions")
   for ~3 minutes, then the server reaped it; a retry then succeeded. It also left a stray
   `about:blank` tab, which was reaped together with the session (tab count back to 72, verified
   by URL-list diff). Lesson for future probes: always `session.end` in a `finally`/error path,
   and never navigate to `about:` pages via WebDriver.
2. Marionette needed protocol v3 array framing (`[0, id, "WebDriver:NewSession", {...}]`);
   the legacy object format (`{"to","name","parameters"}`) gets no reply, and plain `newSession`
   is rejected as `invalid session id`. `WebDriver:NewSession` works and returns
   `browserVersion 1.24.3b`, `moz:buildID 20261118023529`.
3. Chrome-context pref reads via Marionette are blocked on this instance:
   `Marionette:SetContext` returns "System access is required. Start Zen with the
   `MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1` environment variable". No restart was done to add it
   (task allows one restart only, already used). Pref effectiveness was instead proven via
   `prefs.js` + the scratch-profile experiment (section 5d).
4. One Marionette probe opened a new tab and failed its navigate step; the tab did not persist
   (72 tabs after, URL diff clean apart from the one GitHub navigation noted in 5c).
5. `toolkit.telemetry.server = "https://%(server)s/telemetry-dummy/"` (a recommended-pref value)
   is present in `prefs.js` although it is not in `user.js`; it is a leftover from an earlier
   session predating this task (the `remote.prefs.recommended=false` pin predates the restart),
   not something this task set. Left as is.

## 7. Files

- Report (this file): `~/workspace/zen-opencode-council/apply-report.md`
- Backup: `/home/james/.config/zen/ae59l0ak.Default (release)/user.js.bak-council-20261124`
- Updated: `/home/james/.config/zen/ae59l0ak.Default (release)/user.js` (21 lines, 1566 bytes)
- Restart log: `/tmp/zen-council-restart.log` (laptop)
- Scratch experiment log: `/tmp/scratch-test.log` (laptop; scratch profile removed afterwards)

## 8. Bottom line

- All 13 council prefs applied and effective (9 as user prefs in `prefs.js`, 4 equal to build defaults).
- Zen restarted cleanly in ~2 s (SIGTERM, no kill -9): same version/build, both control ports up,
  all 72 tabs restored (0 lost), BiDi `session.new`/`session.end` working with the slot left free.
- Ready for tomorrow's R3-L3 run. No follow-up action needed from the coordinator except noting
  the section 5c single-tab navigation (not a restore failure) and the section 6 item 5 leftover pref.
