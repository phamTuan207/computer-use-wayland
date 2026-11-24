# R3-L3 Zen 1.24.3b optimizations (deep dive, 2026-11-24)

- Date: 2026-11-24, evening, before task 1 on 25/11.
- Author: R3-L3 optimization deep-diver (subagent).
- Scope: Zen 1.24.3b on the laptop only. Run is 55 tasks, 19-31 hours, driven via BiDi on 9222 plus Marionette on 2828.
- Constraints honored: user.js NOT touched (parallel update worker owns it), Zen NOT restarted, CDP/Marionette NOT driven, pill NOT acquired. All laptop reads below are read-only (ps, ss, profile files, sessionstore parse).
- No em dash or en dash in this file. Commas, periods, short hyphens only.

## 1. Laptop ground truth measured 2026-11-24 about 19:50-20:05 +07

- Zen version: 1.24.3b, BuildID 20261118023529, Firefox 160.0.1, from `/opt/zen-browser-bin/application.ini`. SourceStamp a127b1d27e5bb1f32f4b0f2368e7b1a81eb23e6f.
- Zen process: PID 381258, started 19:46, so the session was about 5 minutes old at probe time. Launch line is `/opt/zen-browser-bin/zen-bin --remote-debugging-port=9222 --marionette` via wrapper `~/.local/bin/zen-ai`. Ports 9222 and 2828 both LISTEN on 127.0.0.1, owned by PID 381258. `WebDriverBiDiServer.json` says ws_host 127.0.0.1, ws_port 9222. `MarionetteActivePort` says 2828.
- Profile: `/home/james/.config/zen/ae59l0ak.Default (release)/` (note: `~/.config/zen`, not `~/.zen`). Single profile in use, locked to PID 381258. There is no separate run profile; the Default (release) profile IS the run profile.
- `user.js` at probe time holds only 2 prefs: `browser.shell.checkDefaultBrowser=false` and `toolkit.legacyUserProfileCustomizations.stylesheets=true`. `remote.prefs.recommended=false` was NOT yet pinned when probed (parallel update worker pending). `prefs.js` holds NO override for `browser.tabs.unloadOnLowMemory`, `browser.sessionstore.*`, `media.suspend-bkgnd-video.*`, `remote.prefs.*`, or `dom.ipc.processCount`. All defaults therefore apply.
- Session: 1 window, 72 tabs, 49 pinned, from `sessionstore-backups/recovery.jsonlz4` (2.9 MB compressed, 3,690,637 bytes decompressed, parsed read-only with the system liblz4). Top domains: github.com 11, youtube.com 2, huggingface.co 2, lms.neu.edu.vn 2, claude.ai 2, plus Gmail, Calendar, Todoist, ChatGPT, Gemini, Perplexity, DeepSeek, Codeforces, research PDFs, and leftover test tabs (`https://example.com/`, several `about:blank`, `file:///tmp/pill-video/fixture.html`).
- Memory: 30 GB RAM total, 13 GB used, 17 GB available. Swap 5.3 GB used of 35 GB. Disk 228 GB free of 385 GB. Zen total RSS about 2.5 GB (main 608 MB, 7 tab processes 110-165 MB each, rdd 164 MB).
- CPU anomaly (flagged, not acted on): one tab content process (PID 381659) runs at about 49 percent CPU sustained, and the main process at about 37 percent lifetime average. The tab behind PID 381659 cannot be identified without driving CDP, so it is NOT named here and NOT closed. See D3.
- Sessionstore backups: `previous.jsonlz4` 5.1 MB, `recovery.jsonlz4` 2.9 MB, `recovery.baklz4` 2.9 MB. A restore fallback exists.

## 2. Bottleneck analysis: what Zen can and cannot move

- The plan's honest range is 19-31 hours. The biggest serial cost is coordinator work (55 manifest gates at about 2 min each is 1.8 hours; 110 grade audits at 5 min each is about 9 hours; 55 ledger appends; 9 Tier A checker runs). No browser change touches that. Any claim that a Zen pref saves hours off the run is false.
- What Zen CAN move: runner-side cycle time and stability. Two failure modes dominate: (a) a zombie BiDi session blocks ALL driving until Zen restarts (hard stop, no remote fix); (b) tab and memory accumulation over 19-31 hours slows the browser and the driver. A third cost is real but small: one hot background tab burning about half a core for the whole run.
- Expected effect of everything below: no minutes-per-task saving is claimed. The value is avoiding 1-2 hard stops and a slow drift over 19-31 hours.

## 3. Applied: file-based rules, effective immediately, no restart needed

### A1. Runner tab hygiene (operative rule, also in plan Appendix Z)

- Each runner works in ONE dedicated task tab and reuses it by navigation for its next task. A new tab per task is forbidden.
- After a task's evidence is sealed, the runner closes every tab or popup IT created for that task, except its one dedicated task tab. Closed windows and popups are now actually freed (gh-16587), so closing helps instead of leaking.
- NEVER close, unload, or navigate any of the owner's 72 baseline tabs. Runner-created tabs only.
- Cap: at most 2 runner-created tabs at any time per runner.
- Why this is the real lever: on Linux, Firefox does NOT auto-unload tabs (default `browser.tabs.unloadOnLowMemory=false`, see section 6), and Zen removed its own unload timer in recent versions in favor of the Firefox native unloader (Zen discussion 9087). Without this rule, 55 tasks could leave 55 loaded tabs behind for the whole run. With it, runner tab count stays flat.
- Sources: Mozilla tab-unloading docs (firefox-source-docs.mozilla.org/browser/components/tabbrowser/docs/tab-unloading.html); Zen discussion 9087 (github.com/zen-browser/desktop/discussions/9087); Zen 1.24.3b release notes for gh-16587 (zen-browser.app/release-notes/).

### A2. BiDi session end-on-handover (operative rule, also in plan Appendix Z)

- Firefox allows exactly ONE BiDi session at a time. A second `session.new` fails with "Session already started".
- The session OUTLIVES its WebSocket connection. Dropping the socket, killing the driver, or `kill -9` on the driver does NOT end the session. A new connection cannot end it. Only a clean `session.end` (or closing the browser) frees it.
- Rule: whoever holds the BiDi session MUST call session end before handing the session to the next driver. The handover is: end session, confirm, then the next driver creates its session. No driver starts by assuming the session is free; it checks `session.status` first.
- On "Session already started": do NOT retry in a loop, it can never succeed. Stop, report to the coordinator, and use the restart procedure D1. A retry loop burns the 30-minute task timeout for nothing.
- The same single-session rule is why the plan's "one driver at a time" plus cursor.lock exists. This rule adds the missing half: clean release, not just clean acquisition.
- Sources: bidi-lite docs (docs.rs/bidi-lite, "Firefox allows a single BiDi session, and it outlives the connection"); zenpilot PyPI 0.2.0 (pypi.org/project/zenpilot/0.2.0/, "One session at a time", "Stuck sessions ... Zen refuses new sessions until you restart"); Mozilla firefox-devtools-mcp README (github.com/mozilla/firefox-devtools-mcp, idle-timeout 1800, "Firefox accepts one client at a time"); prior workspace research `firefox-automation-research-20261121.md` section 4.5 ("Zombie session chi clear duoc bang restart Zen").

### A3. Mid-run restart procedure (written now, executed tomorrow)

- Full procedure is D1 below. The text is applied to the plan as Appendix Z so the coordinator can execute it without asking. No restart is performed by this dive.

## 4. Documented for tomorrow: needs a restart or a live change

### D1. Mid-run Zen restart point (coordinator executes)

- When: at the first task boundary AFTER the FCC lane completes (position 28, R3-037), or after 12 hours of run wall time, whichever comes first. Also immediately on any zombie BiDi session (A2) or if Zen total RSS passes 8 GB.
- Why then: position 28 is a natural lane boundary, and 12 hours is before the gh-16587-era drift would have mattered on older builds. A restart also clears any zombie session and re-reads user.js (so the update worker's pin takes effect for the second half).
- Steps, in order:
  1. Coordinator pauses BOTH lanes at task boundaries. No task mid-flight, no Class L scoring in progress.
  2. Current BiDi holder calls session end and confirms it. No `kill -9` on Zen or on the driver.
  3. Clean quit of Zen (quit from the app, not kill). A clean quit writes a fresh sessionstore; a kill leaves an unclean shutdown.
  4. Verify the Zen processes are gone (`ps` shows no zen-bin) and ports 9222/2828 are free (`ss -ltnp`).
  5. Relaunch with the normal path (`zen-ai` wrapper, which supplies `--remote-debugging-port=9222 --marionette`). Do NOT relaunch by calling zen-bin directly without the flags.
  6. Verify: `ss` shows 9222 and 2828 listening on 127.0.0.1; `WebDriverBiDiServer.json` in the profile shows ws_port 9222; version is still 1.24.3b (check `application.ini` Version and BuildID 20261118023529); tabs restored (baseline 72 plus runner tabs); a fresh `session.status` accepts a new BiDi session.
  7. Record restart time, pre-restart RSS, post-restart RSS, and version check in the run log. Resume both lanes.
- Why a clean quit matters: `browser.sessionstore.max_resumed_crashes` defaults to 1. After a second consecutive unclean start, Zen shows the session-restore prompt and automation blocks waiting for a human. A clean quit resets that counter. Never `kill -9` Zen mid-run.
- Why the version check matters: if an update was staged, the restart is the moment it would apply. The run stays on 1.24.3b. If the version is not 1.24.3b after restart, STOP and escalate to the owner before resuming.
- Sources: Mozilla session-restore prefs (wiki.mozilla.org, Session Restore: `browser.sessionstore.max_resumed_crashes` default 1, `browser.sessionstore.resume_from_crash` default true); zenpilot stuck-session note; prior research note section 4.7 (flags only apply at startup).

### D2. For the parallel update worker (owns user.js, do NOT do this myself)

- The worker is pinning `remote.prefs.recommended=false`. That pin has a side effect the run must cover: the recommended prefs normally disable auto-updates (Mozilla Prefs doc: recommended prefs include "disabling auto-updates, Telemetry, and first-run UX"). With the pin, auto-update is no longer suppressed by that mechanism.
- Ask the worker to add, in the same user.js, an explicit update guard: `user_pref("app.update.enabled", false);` (user prefs take precedence over recommended prefs, per the Mozilla Prefs doc, so this holds either way). If Zen on this install does not honor `app.update.*` (Zen ships its own updater path on some installs), the worker must verify that and record which mechanism freezes updates, instead of assuming the pref works.
- Also ask the worker to verify BEFORE task 1 that no update is already staged or pending (a staged update would apply at the D1 restart). Record the check in the run log.
- Rationale: a mid-run update to Twilight or a new stable would change the automation surface mid-measurement and void comparability. The freeze is 1.24.3b for the whole run.
- Sources: Firefox Source Docs, Remote protocol preferences (firefox-source-docs.mozilla.org/remote/Prefs.html); zenpilot note that recommended prefs rewrite about 40 prefs including crash session restore, password autofill, popup blocker, tracking protection (pypi.org/project/zenpilot/0.2.0/).

### D3. Pre-task-1 live checks (coordinator, needs the browser, NOT done by this dive)

- Identify the hot tab: open `about:processes` (or `about:performance`) and find which tab owns the content process burning about 50 percent CPU (PID 381659 at probe time; PID will differ tomorrow). If it is a leftover test or fixture tab (for example `file:///tmp/pill-video/fixture.html` or the `example.com` tab from driver tests), close it ONLY if it is a runner or test leftover. If it is an owner tab (YouTube, an AI chat, Gmail), leave it alone and record the CPU cost. Never close an owner-opened tab (standing rule, 2026-11-22).
- Open `about:unloads` once and record the unload priority order as a baseline. It shows which tabs Firefox would unload first if memory pressure ever hits.
- Confirm the pill is present and the BiDi session is free (`session.status`) before releasing task 1.

### D4. Conditional only: enable tab auto-unload if memory fills (NOT pre-emptive)

- Do NOT set `browser.tabs.unloadOnLowMemory=true` before task 1. Enable it ONLY if Zen total RSS passes 8 GB mid-run, applied at the D1 restart point via user.js (needs the update worker or the coordinator at the restart, plus a restart to take effect).
- If enabled, the verified semantics are: tabs unload in least-recently-used order; tabs touched in the last 10 minutes are skipped (`browser.tabs.min_inactive_duration_before_unload` default 600000 ms); tabs playing media, in PiP, or using WebRTC are excluded; pinned tabs are only deprioritized, NOT exempt; the foreground tab is never unloaded; visible split-view panes are protected by gh-16624.
- Why conditional: with 17 GB free at run start, memory pressure is unlikely, so the benefit is speculative, while the risk is real (a background reference tab or a Class L re-read tab could be unloaded mid-task and need a reload). The trigger (RSS over 8 GB) makes the trade honest.
- Sources: Firefox tab-unloading docs (firefox-source-docs.mozilla.org/browser/components/tabbrowser/docs/tab-unloading.html); thetabextension.com tab-management writeup (Linux default false, weight table); Zen discussion 9087 ("On Linux, you may need to set browser.tabs.unloadOnLowMemory to true for tab unloading to work"); Zen 1.24.3b notes for gh-16624.

## 5. Verified no-action: already optimal on 1.24.3b

- V1. `media.suspend-bkgnd-video.enabled` defaults to true with a 10 second delay (`media.suspend-bkgnd-video.delay-ms` 10000) in mozilla-central `modules/libpref/init/all.js`, and no override exists in prefs.js. Background video already suspends. No change.
- V2. Firefox 160 BiDi perf (bug 2075175): network events no longer compute unused security details, "could have visible impacts on performance, e.g. during a page load". Already in 1.24.3b (Firefox 160.0.1). No change. Source: MDN Firefox 160 release notes for developers (developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/160).
- V3. gh-16587 (closed windows freed from memory) and gh-16624 (visible split-view and glance tabs not unloaded under memory pressure) are both in 1.24.3b. Verified against the official release notes (zen-browser.app/release-notes/) and the GitHub pulse record (gh-16624 merged 14 Nov 2026 as PR 16622; gh-16618 is the follow-up window-freeing fix). No change.
- V4. Pill optics blur 0.30 / refraction 0.75 and the light terminal icon in profile chrome/ are already in place (commit 58c419f). No change.
- V5. Launch line is already correct (`--remote-debugging-port=9222 --marionette` in the zen-ai wrapper, used by all zen.desktop Exec lines). No flag to add or remove. No 1.24.x release note touches CDP, Marionette, the remote port, profile format, or tab behavior in a breaking way.
- V6. Session restore defaults favor the restart point: `browser.sessionstore.resume_from_crash` defaults to true, and pinning `remote.prefs.recommended=false` keeps crash session restore enabled (recommended prefs would disable it, per zenpilot). No change.
- V7. Disk and RAM headroom are ample (228 GB free, 17 GB RAM available). Sessionstore writes (3.7 MB every interval) are negligible. No change.

## 6. Rejected as unsafe or unvetted (with reason)

- R1. Random "Firefox fast" user.js pastebins and about:config tables (dom.ipc.processCount cuts, cache size cuts, sessionhistory cuts, network tweaks): no official source ties any of them to BiDi throughput on this run, and several cut parallelism or caching that heavy task pages need. Rejected, per the task's vetting rule.
- R2. Pre-emptive `browser.tabs.unloadOnLowMemory=true`: see D4. Benefit speculative at 17 GB free; risk to reference and Class L re-read tabs is real because pinned tabs are only deprioritized, not exempt. Deferred to the RSS trigger.
- R3. Disabling or gutting sessionstore (`browser.sessionstore.interval` to a huge value, or disabling restore): would destroy crash recovery and the D1 restart point. Rejected.
- R4. Moving to Twilight 1.25t: pre-release, owner said no, release notes already advertise Twilight-only UI changes (Little Zen window, Zen's own settings window) that could change the automation surface. Rejected.
- R5. Installing an auto-unload extension (Auto Tab Discard, Sleeping Tabs, or similar) into the run profile: a new, unvetted extension mid-run that could unload task tabs on its own timer. Manual hygiene (A1) does the same job with no new code. Rejected.
- R6. Cutting `dom.ipc.processCount` or other fission/process tweaks: unverified for this workload, reduces parallelism for the 55 heavy pages, and the machine has 30 GB RAM so process-count memory saving is not needed. Rejected.
- R7. `remote.screenshot.use_readback=true`: the Mozilla Prefs doc says readback degrades full-document, clip-region, and element screenshots to the viewport, and chrome-scope captures keep the old path. Evidence screenshots need full-document and element captures, so this would break evidence. Rejected.
- R8. `remote.experimental.enabled=true`: defaults to false outside Nightly; it unlocks experimental BiDi commands that are unvetted for this run. Rejected.
- R9. Lowering `browser.sessionstore.interval` for "faster" recovery or raising it to "save disk": no measured problem exists (3.7 MB writes, ample disk), and changing it trades recovery freshness against nothing. Rejected.
- R10. Any pref that disables Safe Browsing, tracking protection, or the popup blocker to "speed up" page loads: the recommended-prefs pin already preserves the user's values, and weakening them changes what task pages do (bot checks, popups) mid-measurement. Rejected.

## 7. What this dive did NOT do (explicit limits)

- Did not touch user.js, prefs.js, or any laptop file. Did not restart Zen. Did not open a BiDi or Marionette session, did not acquire the pill, did not navigate or close any tab.
- Did not identify the hot tab (needs a live browser check, D3). Did not measure per-task BiDi latency (no task has run on this build yet; the checkpoint after the 3rd graded task is the right place to measure it).
- Did not use Codex, FCC, or opencode: the work is verification and file edits, and parallel agents would have risked conflicting with the update worker on the same profile. Full token use was authorized but not needed.
- The execution plan file (`~/workspace/r3-l3-execution-plan-20261124.md`) is VM-local, not in the run-log repo, so its Appendix Z edit below is NOT part of this commit. The coordinator should copy Appendix Z into the repo copy if one exists.

## 8. Appendix Z text (added to the execution plan, VM-local copy)

- A1 tab hygiene, A2 BiDi end-on-handover, and the D1 restart point are added as Appendix Z to the execution plan. The full evidence lives in this file.

## Sources (all accessed 2026-11-24)

- Zen 1.24.3b release notes: https://zen-browser.app/release-notes/
- Zen 1.24.3b mirror: https://whatsnew.fyi/product/zen-browser/releases/1.24.3b
- MDN Firefox 160 release notes for developers: https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/160
- Firefox Source Docs, Remote protocol preferences: https://firefox-source-docs.mozilla.org/remote/Prefs.html
- Firefox Source Docs, Tab Unloading: https://firefox-source-docs.mozilla.org/browser/components/tabbrowser/docs/tab-unloading.html
- Mozilla Support, Unload inactive tabs: https://Support.mozilla.org/en-US/kb/unload-inactive-tabs-save-system-memory-firefox/revision/299171
- bidi-lite docs (single BiDi session, outlives connection): https://docs.rs/bidi-lite/latest/bidi_lite/
- zenpilot PyPI 0.2.0 (one session, stuck sessions, recommended prefs rewrite about 40 prefs): https://pypi.org/project/zenpilot/0.2.0/
- Mozilla firefox-devtools-mcp README (one client at a time, idle-timeout): https://github.com/mozilla/firefox-devtools-mcp
- Zen discussion 9087 (unload timer removed, Linux needs unloadOnLowMemory=true): https://github.com/zen-browser/desktop/discussions/9087
- Tab-management writeup (Linux default false, unloader weights): https://thetabextension.com/blog/firefox-tab-management
- mozilla-central all.js (media.suspend-bkgnd-video.enabled true, delay 10000): https://dev.phabricator.nonprod.webservices.mozgcp.net/source/mozilla-central/browse/default/modules/libpref/init/all.js;6776d69d2f03814fcd1d93e0912df2598d32a357
- MozillaWiki Session Restore (resume_from_crash true, max_resumed_crashes 1, interval 10000): https://wiki.mozilla.org/index.php?title=Session_Restore&diff=1258651&oldid=25708&mobileaction=toggle_view_mobile
- Prior workspace research: `~/workspace/zen-1.24.3b-research.md` (versions, fixes, BiDi notes); `~/workspace/firefox-automation-research-20261121.md` section 4.5 (zenpilot/zen-mcp, zombie sessions).
- Laptop measurements: see section 1 (commands run read-only over SSH, 2026-11-24 about 19:50-20:05 +07).
