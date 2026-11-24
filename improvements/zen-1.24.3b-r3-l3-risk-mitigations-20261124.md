# Zen 1.24.3b R3-L3 risk mitigations: seven open issues

Date: 2026-11-24. Run: R3-L3, a 19-31 hour automated browser run on Zen 1.24.3b, driven via Marionette plus WebDriver BiDi on a dedicated profile, Linux/Wayland. Each issue below is open (or closed without a fix) as of 24 Nov 2026, with its root cause as known, a concrete mitigation, and what to do if it happens mid-run. Hypotheses are labeled as hypotheses. One issue in the brief was mislabeled and is not a crash at all (section 2). "Session restore" below means reopening the previous session's tabs after a restart. RDD is the Remote Data Decoder, the media decoder process. Risk ratings in the table are the draft's own judgment, not the issues' labels.

## Risk table

| Issue | What it is | Risk to R3-L3 | Mitigation in one line |
|---|---|---|---|
| #16718 | RDD process SIGSEGV, browser self-kills | High on NVIDIA plus Wayland with video; low otherwise | Set the dmabuf and forced-decode prefs, never force VA-API |
| #16723 | Copy URL copies a rich-text hyperlink | None, not a crash | Read URLs from BiDi, not the clipboard |
| #16694 | Safe mode hangs and holds the profile lock | Low as a trigger, high as a recovery trap | Never use safe mode; pre-launch lock check |
| #16706 | Window stops rendering after a resize | High if headed on Wayland; low if headless | Freeze the window, never resize mid-run |
| #16746 | Drag-drop upload does nothing or crashes | Very low, the trigger (an OS-level drag) is absent from the automation path | Never drag; use `input.setFiles` |
| #16710 | Search lag, worse with background video | Low, costs time not state | Navigate by URL, never type in the urlbar |
| #16685 | Memory use above installed RAM | Medium, duration risk | Prefs plus watchdog RSS polling plus planned restarts |

## 1. #16718: RDD process SIGSEGV, browser self-SIGKILLs several times a day

Source: https://github.com/zen-browser/desktop/issues/16718, opened 20 Nov 2026, open, no maintainer comment as of 24 Nov 2026.

What the reporter observed: Zen 1.24.3b (BuildID 20261118023529, Firefox 160.0.1) on Arch Linux (Omarchy), Hyprland Wayland, NVIDIA GTX 1660 Ti Mobile, driver 620.73.04, system ffmpeg 9.1, closes itself randomly several times a day. Eight core dumps (26 Oct 2026, six on 9 Nov 2026 in about 13 minutes, two on 20 Nov 2026) all show the RDD (media decoder) process segfaulting in `av_buffer_unref()` in the system `libavutil.so.61`, after which the main process deliberately SIGKILLs itself (kernel probes show sending PID equals target PID). Firefox itself does not crash on the same machine.

Root cause: hypothesis only, refined by the reporter on 20 Nov 2026. The hypothesis is that the crash follows the dmabuf/VA-API hardware-decode path on NVIDIA plus Wayland. No fix has landed.

Mitigation (before the run, in user.js). Treat this as a reported workaround, not a proven fix: the reporter was still observing crashes on their own machine as of 20 Nov 2026. The workaround comes from upstream issue #10555 and was verified by other users on Fedora and Arch with NVIDIA:

```
user_pref("widget.dmabuf.force-enabled", true);
user_pref("media.hardware-video-decoding.force-enabled", true);
```

Do NOT set `media.ffmpeg.vaapi.enabled=true`: forcing VA-API on NVIDIA plus Wayland is itself a known crash trigger (see #14067). Do NOT use the reporter's LD_PRELOAD shim: it stops the crash but breaks YouTube playback, and the reporter retracted it the same day. Fallback if crashes continue: `media.rdd-process.enabled=false` (disables the RDD process, decoding runs in the content process; weakens the media sandbox, documented in the Fedora Project wiki and Mozilla Bug 1682834), or `media.hardware-video-decoding.enabled=false` (software decode, higher CPU). Workload fallback: avoid video-heavy, HLS, or YouTube-scroll pages on the run tab, and prefer headless if no headed UI is needed. Applicability is conditional on hardware: check `about:support` on the run machine first. Pre-launch check: play video for at least 30 minutes with these prefs set, confirm hardware decoding in `about:support`, and confirm no crash.

If it happens mid-run: detection is a Marionette/BiDi connection drop plus watchdog heartbeat failure, confirmed with `coredumpctl list` (RDD Process SIGSEGV). Recovery: relaunch Zen on the same profile, let session restore bring the tabs back, re-attach Marionette plus BiDi, verify the run tab by URL, and resume from the last checkpointed task. Lost: uncheckpointed in-page state and the in-progress task, which must be re-run from its start and scored once. Tabs and URLs restore.

## 2. #16723: NOT a crash (mislabeled in the brief)

Source: https://github.com/zen-browser/desktop/issues/16723, opened 20 Nov 2026, open. Title: "Add a toggle/setting to disable rich-text hyperlink when copying URL from the address bar icon". It is a feature request: the Copy URL icon copies a rich-text hyperlink (page title plus link) instead of a plain-text URL. No crash, no RDD process, no stability risk to a long run. The only automation note: if the harness copies URLs with that button and pastes into a rich-text field, it gets a hyperlink. Mitigation: read the URL from BiDi or Marionette instead of the clipboard, paste with Ctrl+Shift+V, or copy the address-bar text directly. No pref is known to change this behavior; the requested toggle does not exist. (Comments: kyriog reproduced it on Windows on 21 Nov 2026 and suggested a link to the removal of `displaySpec` and the `browser.urlbar.decodeURLsOnCopy` pref; ajhenry supported making it opt-in on 24 Nov 2026.)

## 3. #16694: safe mode never opens a window and keeps the profile lock

Source: https://github.com/zen-browser/desktop/issues/16694, opened 18 Nov 2026, open, 5 comments, last update 21 Nov 2026.

What the reporter observed: Zen 1.24.1b, Firefox 159.0.1, Fedora KDE Plasma on Wayland (KWin), NVIDIA GPU, 5.8 GB profile. Both `about:support` Troubleshoot Mode restart and `zen -safe-mode` produce no window. The process stays alive, holds the profile lock (a lock file in the profile, `.parentlock` plus a `lock` symlink, that prevents a second instance from opening the same profile), KWin reports zero Zen windows, thread count is 70-78 (healthy start 116-124), CPU stays at 0%, and every later launch then fails silently. A normal start with the same profile works, and a fresh profile opens a window at once. Comments confirm it is still present on 1.24.3b (19 Nov 2026) and that versions older than 1.23.2b work while 1.23.3b and newer reproduce it; the Flatpak build works fine and Firefox Nightly 163 works fine. One conflicting report (AnhBi11, 20 Nov 2026) says neither fresh installation nor new profile helps, so the trigger is not fully settled.

Root cause: not established. It is a Zen regression introduced in 1.23.3b, possibly Fedora-only (tarball and rpm; Flatpak unaffected; upstream Firefox unaffected). Hypothesis only: a Zen-side change in 1.23.3b interacts with Fedora system libraries or the safe-mode restart path.

Mitigation: never use safe mode or Troubleshoot Mode as a restart or recovery path; use planned restarts with session restore instead. Watchdog pre-launch lock check: before every launch, confirm no `zen` process is alive, then remove stale `.parentlock` and `lock` from the run profile only. Never launch a second instance on the same profile. Exact sequence:

```
pgrep -x zen || true
# only if the line above prints nothing:
rm -f "$PROFILE/.parentlock" "$PROFILE/lock"
```

Lock-removal safety: remove lock files only after all browser processes are dead; deleting a lock while a process is alive risks profile corruption (devanswers.net Ubuntu guide, updated about 6 Jul 2026; MozillaZine Knowledge Base, "Profile in use", undated).

If it happens mid-run: detection is BiDi/Marionette heartbeat failure plus a `zen` process alive at near 0% CPU with `.parentlock` present and no window in the compositor. Recovery: kill all Zen processes (`pkill zen`, verify with `pgrep zen` that none remain), remove the stale `.parentlock` and `lock` files from the run profile only, then relaunch with session restore. Do not use `-safe-mode` to diagnose mid-run; it reproduces the same hang. Lost: unsaved session state since the last sessionstore write (up to 60 s, because the interval is set to 60000 ms in section 7) and in-memory page state. Resume from the external tab-URL snapshot and verify the run tab by URL.

## 4. #16706: window stops rendering after resize while a game is running

Source: https://github.com/zen-browser/desktop/issues/16706, opened 19 Nov 2026, open, 0 comments as of 24 Nov 2026.

What the reporter observed: Arch, Hyprland, Wayland, hardware acceleration enabled, NVIDIA GTX 980 with nvidia-580xx-dkms, AUR zen-browser-bin. After a game loads into a save, a browser window resize (opening or closing another window, or entering fullscreen video playback) makes Zen stop updating its contents and freeze on the last frame. It also occurs when the game is paused, and does not recover when the game is closed. Restarting Zen is required. It does not occur under XWayland, or with hardware acceleration disabled. Not reproducible in Firefox.

Root cause: not established; no comments and no developer response. Hypothesis only: an interaction between Zen's Wayland/WebRender frame path and a resize while the GPU is busy, possibly a lost frame callback after the resize.

Mitigation: freeze the window. Set the size and viewport at launch and never resize, move, or fullscreen the window mid-run, and do not switch spaces or workspaces mid-run. Run no GPU-heavy application (games, video players) concurrently on the run machine. Prefer headless if no headed UI is needed: headless avoids the Wayland compositor entirely, so the resize path cannot fire. Fallbacks, both reporter-verified for this issue: run under XWayland (`MOZ_ENABLE_WAYLAND=0`), or disable hardware acceleration in user.js (`layers.acceleration.disabled=true` plus `gfx.webrender.software=true`, verify in about:support that Compositing reads "WebRender (Software)"). Tradeoff: software rendering raises CPU and can worsen video and WebGL, so test before the run and do not switch mid-run. Decision rule: keep hardware acceleration enabled by default. Switch to software rendering only if this freeze recurs, and accept two tradeoffs when doing so: it supersedes section 6's "keep hardware acceleration enabled" advice for the search lag, and it makes the section 1 video-decode prefs moot (software decoding takes over).

If it happens mid-run: detection by comparing consecutive BiDi screenshots (identical pixel hashes across two checks while the page should be changing). The BiDi/Marionette heartbeat may still respond, so heartbeat alone does not catch it. Recovery: restart Zen; a resize or window move will not recover it. Lost: unsaved session state since the last sessionstore write. If it recurs, switch the remaining run to headless, or to XWayland or software rendering, rather than restarting headed on Wayland again.

## 5. #16746: drag and drop into a maximized Zen does nothing or crashes

Source: https://github.com/zen-browser/desktop/issues/16746, opened 21 Nov 2026, open, 0 comments as of 24 Nov 2026.

What the reporter observed: Zen 1.24.3b AppImage (Firefox 160.0.1, Build ID 20261118023529) on Fedora 45, GNOME/Wayland. Dragging a file from GNOME Files (Nautilus) into a maximized Zen window after switching to Zen mid-drag (Alt+Tab, Activities, dock) either does nothing or crashes Zen on mouse release. The same file dropped with both windows snapped side by side uploads reliably. ChatGPT: crash; Claude: does nothing; Gemini: does nothing; OneDrive: crash. Reproduced with mods and custom CSS removed, and not reproducible on Mozilla Firefox.

Root cause: unknown. Hypothesis only: the Wayland drag-and-drop handoff combined with switching windows mid-drag into a maximized Zen window, since the tiled control case works and the same flow works on Firefox.

Mitigation: avoid the path entirely. A Marionette plus BiDi run never does an OS-level drag from the file manager, so this should not fire. If a task needs a file uploaded, use the DOM file input instead: BiDi `input.setFiles` on the page's `<input type="file">`, or Marionette send keys to that element. A maximized window by itself is fine; the crash needs a drag in progress.

If it happens mid-run: detection via watchdog heartbeat failure, dead browser process, or crash-reporter dialog. Treat any of these as a crash, not a hang: the process is gone or dying, not stuck and alive. Recovery: kill leftover Zen processes, check the profile is not locked (section 3), relaunch on the same dedicated profile with session restore, and resume from the last completed task checkpoint. Re-issue the step through the file-input path, never with a drag. Lost: the crashed tab's in-memory state and any unsent message; completed verified tasks are unaffected.

## 6. #16710: lag and stuttering when searching, worse with background video

Source: https://github.com/zen-browser/desktop/issues/16710, opened 19 Nov 2026, closed 20 Nov 2026 by maintainer mr-cheffy with no reason stated and no fix linked. Treat as unresolved for the run. Related report #16671 ("Floating search bar is extremely laggy after updating to v1.24.2b", opened 17 Nov 2026) is still open as of 24 Nov 2026.

What the reporter observed: Zen 1.24.3b on Windows x64, Google search engine. Opening the floating bar with the new tab button and typing causes significant lag and freezing across the browser, much worse with a video playing in the background, still present without one. A second reporter confirmed the same issue on Artix Linux x86-64 on 20 Nov 2026, so this is not Windows-only. Comments on #16671: one reporter traced their case to OS battery saver mode (17 Nov 2026); another had no battery saver and still saw lag (18 Nov 2026); the maintainer noted "a lot of painting stuff going on" in the profilers and asked whether hardware acceleration was disabled (20 Nov 2026); one reporter said enabling Zen's recommended performance settings made it "way smoother" (22 Nov 2026), while another on macOS 1.24.3b said those settings changed nothing (20 Nov 2026).

Root cause: unknown. Hypothesis only: excess painting during urlbar input, possibly tied to hardware acceleration or performance settings.

Mitigation: avoid the affected path. Never type a search into the floating bar or urlbar: navigate directly by URL with BiDi `browsingContext.navigate`, for example `https://www.google.com/search?q=<query>`. Do not play background video during search steps; pause any video tab before search navigation. Keep hardware acceleration enabled (the default) and enable Zen's recommended performance settings in the settings window before launch. No pref names for those settings are recorded in the issue, so this step is a settings-window action, not a user.js line, and it is not in the section 8 block. Neither is proven to fix it, but both are cheap and the only settings with any positive report. The lag is a UI freeze, not a crash, so it cannot corrupt state by itself; the risk is lost time and a watchdog false alarm.

If it happens mid-run: detection is BiDi/Marionette commands taking far longer than usual (no response within the watchdog threshold, for example 60 seconds) while the browser process is still alive. A live process plus no response means lag, not a crash. Recovery: wait first, do not kill immediately; if still unresponsive after the threshold, kill, relaunch on the same profile with session restore, resume from the last checkpoint, and re-issue the search by direct URL navigation. Lost: nothing if it is only lag; if a restart is needed, only the current step's in-progress state.

## 7. #16685: memory use exceeding installed RAM

Source: https://github.com/zen-browser/desktop/issues/16685, opened 18 Nov 2026 (01:34 UTC), open, one comment, no maintainer response.

What the reporter observed: Zen 1.24.1b on macOS aarch64, 8 GB RAM machine, Zen processes using more than 8 GB total, machine going into swap for everyday use, with frequent small lag and rainbow-wheel spins. About 100 tabs across about 15 spaces, no narrower repro steps. It still reproduces with all mods and custom CSS removed, and cannot be reproduced on Mozilla Firefox.

Root cause: unknown and undiagnosed. The most likely reading needs no leak: 100 live tabs is about 80 MB per tab, ordinary per-tab memory. The closed-window leak gh-16587, fixed in 1.24.3b, made memory grow over time because closed windows were never freed, but the reporter was on 1.24.1b and never tested 1.24.3b, and the reported pattern (many live tabs) is not the closed-window pattern. A third hypothesis is Zen-specific overhead (workspaces, vertical tabs, glance), since the reporter says Firefox does not reproduce it, but no evidence names a subsystem. The 1.24.3b diff contains no Zen memory-management code of its own (`memory.diff` is empty, see the source review); the only memory fix is gh-16587 through the Firefox 160.0.1 pin. The run profile differs from the reporter in the direction that helps: one run tab in one window, not 100 tabs in 15 spaces. The draft's reading is that the risk is duration, not tab count: 19-31 hours of growth plus any closed-window or popup churn.

Mitigation (before the run, in user.js on the dedicated profile):

```
user_pref("browser.tabs.unloadOnLowMemory", true);
user_pref("browser.tabs.min_inactive_duration_before_unload", 600000);
user_pref("browser.low_commit_space_threshold_mb", 1024);
user_pref("zen.tab-unloader.excluded-urls", "<run URL>");
user_pref("dom.ipc.processCount", 4);
user_pref("browser.sessionstore.interval", 60000);
user_pref("browser.startup.page", 3);
user_pref("zen.workspaces.continue-where-left-off", true);
```

Notes: run 1.24.3b pinned, with updates disabled. `browser.tabs.unloadOnLowMemory` is the key Linux lever; Firefox ships it true on Windows and macOS and false on Linux, so on Linux the native unloader does nothing unless this is set (Mozilla default pref file, described 23 Aug 2026). `browser.tabs.min_inactive_duration_before_unload` at 600000 ms is the default (10 min); the line is included to pin it, not to change it. `browser.low_commit_space_threshold_mb` (default 200 MiB) is an optional lever to fire the unloader before swap; it is not verified on Firefox 160. `zen.tab-unloader.excluded-urls` is untouched by the 1.24.3b diff and is the one Zen-side lever that protects a specific tab from the pressure unloader. `dom.ipc.processCount` 4 (default 8) caps the process-count part of the footprint at the cost of less crash isolation between sites. `browser.sessionstore.interval` at 60000 ms changes the default of 15000 ms, to cut session-write churn over a 31 h run. Keep the tab count minimal: one window, the run tab only, no popups, never a little window (it will not restore after a restart). Watchdog: poll the `zen` process RSS every 5-15 minutes, plus `about:memory` and `about:processes` snapshots. Thresholds are a recommendation, no source gives one: warn at 60% of system RAM, act at 70% or on sustained growth above about 1 GB per hour. Planned restart roughly every 8-10 hours at a task boundary, with session restore, verified before resuming; the interval is a recommendation, no source gives one.

If it happens mid-run: detection is RSS crossing 70%, swap growth, slow BiDi responses, UI freeze, or Marionette timeouts (no rainbow wheel on Linux). Recovery in order: (1) if BiDi still answers, open `about:memory` in a spare tab over BiDi and trigger its "Minimize memory usage" button, then unload non-run tabs from `about:unloads`, then confirm the run tab is still loaded; (2) if it does not answer, kill `zen` and restart on the same profile, verify run tab by URL and title over BiDi before resuming; (3) if the OS OOM killer took it, same path, and check `dmesg` for the OOM kill line; (4) if the run tab itself was unloaded, reload it over BiDi and re-check state. Lost: in-flight unsaved state and at most about 60 s of tab-state changes (session store interval). Completed tasks are safe in the coordinator log and repo. Resume from the last completed task and re-run the interrupted task from its start.

## 8. Shared run profile and watchdog duties

Consolidated user.js for the run profile (combine sections 1 and 7; the section 4 software-rendering fallback replaces only the two section 1 video-decode lines, not this whole block, so the section 7 memory lines stay in place under that fallback):

```
user_pref("widget.dmabuf.force-enabled", true);
user_pref("media.hardware-video-decoding.force-enabled", true);
user_pref("browser.tabs.unloadOnLowMemory", true);
user_pref("browser.tabs.min_inactive_duration_before_unload", 600000);
user_pref("browser.low_commit_space_threshold_mb", 1024);
user_pref("zen.tab-unloader.excluded-urls", "<run URL>");
user_pref("dom.ipc.processCount", 4);
user_pref("browser.sessionstore.interval", 60000);
user_pref("browser.startup.page", 3);
user_pref("zen.workspaces.continue-where-left-off", true);
```

Watchdog duties across all seven issues: heartbeat every 30-60 s; screenshot-hash comparison, only after an action that should change the page or paired with expected DOM changes (a static run tab during idle periods would otherwise false-alarm); RSS polling every 5-15 min; external tab-URL snapshots every few minutes; pre-launch check that no stale `zen` process or profile lock exists. Recovery rules that hold for every issue: resume from the last completed task, never from the interrupted one; verify the run tab by URL before resuming; never recover with safe mode; never delete a profile lock while a Zen process is alive; never re-issue a failed step the same way it failed (drag, urlbar typing, forced VA-API). Hardware acceleration stays enabled by default; switch to software rendering only if the #16706 freeze recurs (section 4).

## Sources

- Zen issues, fetched 24 Nov 2026: #16718, #16723, #16694, #16706, #16746, #16710, #16685, plus related #16671, #10555, #14067, #15992. All at https://github.com/zen-browser/desktop/issues/<number>.
- Zen 1.24.3b release notes, https://zen-browser.app/release-notes/ (17 Nov 2026): closed-window leak gh-16587.
- Zen 1.24.3b source review, `improvements/zen-1.24.3b-source-review-20261124.md` (24 Nov 2026): `memory.diff` empty, timed unloader gone, unloading memory-pressure only.
- Zen Discussion #9087, https://github.com/zen-browser/desktop/discussions/9087 (retrieved 24 Nov 2026): timed unload removed, replaced with Firefox's native tab unloader.
- Firefox memory presets, https://devcxl.cn/en-us/blog/firefox-memory-optimization-about-config/ (2026): `dom.ipc.processCount` 4, `about:memory` minimize, `about:processes`.
- R3-L3 long-run research report, `~/workspace/research_notes/zen-1-24-3b-r3l3-long-run-20261124-1253/report.md` (24 Nov 2026): watchdog heartbeat, RSS polling, planned restart, headed vs headless.
- Firefox tab unloading internals, https://thetabextension.com/blog/firefox-tab-management (read 23 Aug 2026): `browser.tabs.unloadOnLowMemory` false by default on Linux.
- Firefox low-memory tuning on Linux, https://Dev.to/msugakov/taking-firefox-memory-usage-under-control-on-linux-4b02 (2021): `browser.low_commit_space_threshold_mb` defaults.
- Fedora Project wiki, "Firefox Hardware acceleration", and Mozilla Bug 1682834: `media.rdd-process.enabled=false` weakens the media sandbox.
- gHacks Firefox hardware-acceleration guide (updated about 7 Nov 2026) and Mozilla admin docs HardwareAcceleration policy (updated about 19 Nov 2026): `layers.acceleration.disabled` pref.
- devanswers.net Ubuntu guide (updated about 6 Jul 2026) and MozillaZine Knowledge Base, "Profile in use" (undated): remove profile lock files only after all browser processes are dead.
