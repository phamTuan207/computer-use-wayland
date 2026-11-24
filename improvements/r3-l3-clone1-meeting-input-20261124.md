# R3-L3 meeting input from clone1: missing risks and concrete preventions

Date: 2026-11-24. Run: R3-L3, 25 Nov 2026, 55 tasks, 2 lanes, 19-31 hours, Zen 1.24.3b, Marionette plus WebDriver BiDi, dedicated profile, Linux/Wayland. This input answers two questions: (1) what Zen or runner-side risk is the re-plan missing, (2) what concrete prevention to add. It builds on the two reports committed today: the source review (`improvements/zen-1.24.3b-source-review-20261124.md`, commit 2232c0c) and the risk mitigations (`improvements/zen-1.24.3b-r3-l3-risk-mitigations-20261124.md`, commit a587580). No OpenRouter is involved in this input; repo and web work only.

Two notes on how to read this input. First, "missing" means "not in the short list of failure modes the user gave for the re-plan (JSONL gluing, git add -A sweeps, plain-commit sweeps, SSH dying at 30s, hardcoded target IDs, daemon receipts not proving delivery, watchdog false positives, orphaned workers, silent reporting chain)". Verify each item against the full re-plan; the meeting should not take this input's word for what the re-plan contains. Second, numbers and rules labeled "proposed" are this input's proposals, not sourced values. Sourced values are labeled with where they come from; values the research calls recommendations are labeled as such.

## 1. Risks the re-plan may be missing

### 1.1 The run tab can be unloaded under memory pressure, or memory can grow unbounded

The timed unloader's pref registration is gone in 1.24.3b, and per Zen Discussion #9087 the mechanism was removed in favor of Firefox's native unloader. That mechanism claim is reported, not diff-proven. Unloading is now memory-pressure only, and `browser.tabs.unloadOnLowMemory` is false by default on Linux, so on Linux the native unloader does nothing unless the run sets it. This leaves two bad defaults, and the re-plan needs an explicit choice between them: if the unloader stays off, memory can grow over 19-31 hours with no unloader to bound it, and the run has no measured ceiling for a one-tab profile, so unbounded growth toward OOM is the worst case, not a certainty; if it is turned on without protection, the pressure unloader can unload the run tab itself during a long idle gap. The protection that limits that second risk is twofold: `zen.tab-unloader.excluded-urls` is the only reliable Zen-side lever that protects a specific tab, and the unloader skips tabs touched in the last 10 minutes (`browser.tabs.min_inactive_duration_before_unload`, 600000 ms by default), so an actively driven run tab is at risk mainly during long idle gaps, not mid-task while being driven. If the re-plan does not name this decision, it will be made by accident mid-run.

### 1.2 A frozen window is invisible to a heartbeat

Issue #16706: after a resize, the Zen window stops rendering and freezes on the last frame, while BiDi and Marionette may still answer. A heartbeat-only watchdog can report the run healthy while the window is dead. The re-plan lists watchdog false positives, but the other side is a false negative: a live heartbeat with a frozen window. Detection needs screenshot-hash comparison, and only after an action that should change the page, or paired with expected DOM changes. Entering fullscreen video playback is also a trigger for this freeze, so the run should avoid it.

### 1.3 An RDD crash kills the whole browser, not just a tab

Issue #16718: the RDD (media decoder) process segfaults, and the reporter showed from kernel probes that the main process then deliberately kills itself when the RDD child dies. The whole browser dies at once. Recovery is relaunch plus session restore (reopening the previous session's tabs after a restart) plus re-attach, and the crashed task must be re-run from its start, never scored as done. The two dmabuf prefs in the gate are a reported workaround, not a proven fix: the reporter was still observing crashes as of 20 Nov 2026. If the 30-minute video test in the gate fails, the next step is one of: `media.rdd-process.enabled=false` (decoding runs in the content process, weakens the media sandbox), or `media.hardware-video-decoding.enabled=false` (software decode, higher CPU), plus the workload fallback (avoid video-heavy, HLS, or YouTube-scroll pages on the run tab, prefer headless if no headed UI is needed).

### 1.4 A stale profile lock makes every relaunch fail silently

Issue #16694: a profile lock is a lock file in the profile that prevents a second instance from opening the same profile. A stuck or crashed Zen can leave `.parentlock` and the `lock` symlink held, and every later launch then fails silently with no window. The hang was reported on Fedora tarball and rpm builds, while the Flatpak build works fine. Recovery must include the full sequence: kill all Zen processes (`pkill zen`, verify with `pgrep zen` that none remain), confirm no `zen` process is alive (`pgrep -x zen` empty), then remove the stale lock files from the run profile only, then relaunch. Never delete a lock while a process is alive (profile corruption risk), and never recover with safe mode: safe mode reproduces the same hang on the Fedora tarball and rpm builds where it was reported.

### 1.5 Window and tab counting can be wrong by one

As wired in the source, a bare `openPreferences()` call opens a separate `Zen:Settings` dialog window, not an `about:preferences` tab. The 17 Nov 2026 release notes call the settings window Twilight-only, so confirm on the built 1.24.3b before the run; the live check is in the gate (section 2.1). A harness that counts windows or looks for the preferences tab will miscount if the dialog is real on the run build. A URL-bar-only little window self-closes on urlbar blur, and little windows are excluded from top-window selection. Any step that opens settings or counts windows must account for the extra window, and the run must verify the run tab by URL, not by window position. Read that URL from BiDi or Marionette, never from the clipboard: issue #16723 changed Copy URL to copy a rich-text hyperlink, so a clipboard read gives a hyperlink, not a plain URL.

The external-URI routing also changed: `handURIToExistingBrowser` now calls `getWindowForExternalUri` unconditionally instead of `openInWindow`, and that method's off-state behavior is not visible in the diff (unverified). Launch without a start URL, wait for the run tab to appear, and verify it by URL. Three smaller defaults are still unknown on the run build and are open questions for the meeting, not settled risks: `zen.window-sync.open-link-in-new-unsynced-window` (a link-opened window may start unsynced with no spaces), `zen.urlbar.enable-overrides` (Shift/Alt urlbar overrides gated), and Glance from a popup or little window opening a plain tab in a regular window.

### 1.6 Search lag looks like a hang but is not a crash

Issue #16710: typing in the urlbar or floating search bar can freeze the UI while the process stays alive. Killing immediately on a timeout loses state and creates a false crash. The rule must be: wait first, kill only after the threshold, and never type a search into the urlbar at all (navigate by URL instead). The threshold is 60 seconds of no response, the risk report's example threshold. Two smaller mitigations from the same issue: pause any video tab before search navigation, and enable Zen's recommended performance settings (the source gives no pref names for these, so this is a settings-window action, not a user.js line).

### 1.7 The update lock is not verified

The run pins Zen 1.24.3b, but the update lock itself was not verified in the research. A mid-run update could invalidate the run over 19-31 hours. Verify before launch that updates are off on the run profile, and do not assume it from the pin alone. No check procedure exists in the research files, so the verification method is an open item: the run lead must define it before launch (which pref, policy file, or UI check proves updates are off), and the gate item does not pass until that definition exists.

### 1.8 Drag-drop uploads can crash the browser

Issue #16746: dragging a file from the file manager into a maximized Zen window can crash Zen on mouse release. Any task step that uploads a file must use the DOM file input (`input.setFiles` over BiDi, or Marionette send keys), never an OS-level drag.

### 1.9 Lane isolation

A browser crash, profile lock, or OOM in lane 1 must not block lane 2. Each lane needs its own profile, its own browser instance, and its own logs, so one lane's recovery never touches the other's profile or log state. That isolation is profile-level only: the lanes still share RAM, GPU, disk, and network, so an OOM in lane 1 can trigger the OOM killer against lane 2's browser. Two concrete items follow: each lane needs distinct Marionette and BiDi ports (two instances on default ports collide), and planned restarts must be staggered across lanes (both lanes restarting at once spikes machine load).

### 1.10 The run is long enough that planned restarts are the safer shape

At 19-31 hours, do not bet the run on one unbroken browser session. Memory growth needs planned restarts roughly every 8-10 hours at task boundaries, with session restore verified before resuming. The 8-10 hour interval is a recommendation, no source gives one. Do not wait for a crash to restart.

### 1.11 Issue #16723 is not a crash, and Copy URL now behaves differently

Issue #16723 is a feature request, not a crash: the Copy URL button copies a rich-text hyperlink (page title plus link) instead of plain text, and Copy URL now copies all selected tabs. No crash mitigation is needed, but any harness step that copies a URL with that button and pastes into a rich-text field gets a hyperlink. Read URLs from BiDi or Marionette, and paste with Ctrl+Shift+V.

## 2. Concrete preventions to add

### 2.1 Pre-launch gate: the run does not start until every item passes

- Zen 1.24.3b pinned. Update lock verified off on the run profile, with the verification method defined by the run lead before launch (open item, section 1.7).
- user.js set, the full consolidated block from the risk mitigations report section 8 (10 lines, not a subset): `widget.dmabuf.force-enabled=true`, `media.hardware-video-decoding.force-enabled=true`, `media.ffmpeg.vaapi.enabled` NOT forced, `browser.tabs.unloadOnLowMemory=true`, `browser.tabs.min_inactive_duration_before_unload=600000`, `browser.low_commit_space_threshold_mb=1024` (optional lever, not verified on Firefox 160), `dom.ipc.processCount=4`, `zen.tab-unloader.excluded-urls` set to the run URL, `browser.sessionstore.interval=60000`, `browser.startup.page=3`, `zen.workspaces.continue-where-left-off=true`.
- `zen.little-window.enabled` left at its default (off on stable), verified in `about:config` on the exact build the run will use.
- 30-minute video playback test on the run machine with no crash, plus the `about:support` hardware-decoding confirmation step. If the test fails, use the fallback chain in section 1.3.
- Settings live check: call `openPreferences()` with no arguments on the built 1.24.3b and record whether it opens a dialog window or a tab, before the run starts.
- Window size set at launch from the size named in the run config, then frozen; no GPU-heavy application running concurrently; no fullscreen video playback.
- Launch without a start URL; wait for the run tab to appear and verify it by URL read from BiDi or Marionette.
- Pre-launch lock check clean: no `zen` process alive, no stale `.parentlock` or `lock` in either lane's profile.
- One profile, one browser instance, one set of distinct Marionette and BiDi ports, and separate logs per lane.

### 2.2 Orphaned workers if the coordinator dies

Name a deputy coordinator in advance, in writing, before the run starts. The deputy is authorized to take over coordination, assign tasks, score completed tasks from validated checkpoints, restart lanes, and report to the owner through the repo path. Promotion is automatic, not decided by the owner mid-run: when the coordinator heartbeat is stale for more than 15 minutes, the deputy declares the takeover in writing in the run status file. The 15-minute threshold is proposed, and it is deliberately aligned with the standing 15-minute stall rule (report any stall over 15 minutes). Fencing stops two coordinators from assigning the same task twice: the heartbeat file carries a coordinator epoch (an integer, starting at 1), the deputy increments it on takeover, and workers only accept assignments carrying the current epoch; assignments from the old epoch are ignored.

The coordinator writes a heartbeat file with a timestamp at least every 5 minutes (proposed cadence) into the run's shared status location on the run machine, owned by whoever holds the coordinator role. Workers poll it every 2 minutes (proposed). If the heartbeat is stale for more than 15 minutes (three missed 5-minute heartbeats), each worker finishes its current task, then stops: it checkpoints, stops taking new tasks, and writes a `COORDINATOR-MISSING` flag with its last checkpoint. A current task can run 20-35 minutes (the run's own estimate from 55 tasks over 19-31 hours), so "finish the current task, then stop" is the intended behavior, not "stop instantly". Workers never take a new task without a live coordinator heartbeat.

Checkpoints are validated before anyone resumes from them: the deputy checks that the checkpoint parses as JSON, that its task ID matches, and that its completion artifact is present. A corrupt checkpoint forces a re-run from the last validated checkpoint. A task completed after the coordinator dies is scored by the deputy from its checkpoint, and never re-assigned once its completion is validated. The independent watchdog writes the flag to the run status file in the repo for coordinator Muse, which is the standing reporting path; no agent messages the owner directly.

### 2.3 Silent reporting chain: make staleness a first-class state

The levels are worker, lane coordinator, coordinator, watchdog. Every level reports up on every task completion and with a status heartbeat at least every 15 minutes. The coordinator also writes its heartbeat file every 5 minutes (section 2.2); the watchdog also runs a browser-health heartbeat every 30-60 seconds (section 2.9). The 5-minute cadence is the coordinator's heartbeat file, the 15-minute cadence is every level's status heartbeat, and the 30-60 second cadence is the browser-health heartbeat. These are different levels, so they do not contradict.

Every status file carries a timestamp. Any level whose timestamp is older than its cadence plus a 5-minute grace (proposed) is flagged STALE by the level above, in the run status file in the repo, which is the same place the owner reads status. The level above escalates it to the coordinator through the repo, and the coordinator alerts the owner. No news is news: silence for one full cadence is itself a reportable event, and the level above escalates it instead of waiting for the next scheduled check.

While the coordinator is missing, workers report to the deputy (section 2.2), and the deputy reports to the run status file in the repo. The chain never terminates at one person or one file with no backup; see section 2.11 for the watchdog's own backup.

### 2.4 Receipts must prove delivery

A delivery receipt must include a verifiable artifact: the platform message ID. A read-back counts only if it comes from an independent path, for example reading the message back through the platform API, never from the same daemon whose word is being checked. "Daemon accepted it" is not a receipt. If the artifact cannot be produced, the delivery is recorded as UNVERIFIED, not delivered, and the step is retried through a different path: first the platform API directly, and if that is unavailable, the delivery note is written to the run status file in the repo for the coordinator to relay.

### 2.5 Git: explicit pathspec on every commit

Never `git add -A`, never `git commit -a`, never a plain `git add .`. Every commit uses an explicit pathspec, the exact file paths named on the git add line, and the commit log line lists the files committed. A commit that touches files outside its pathspec is rejected by the committer before pushing.

### 2.6 JSONL: one validated line per record

Each record is one line with a trailing newline, flushed and forced to disk (fsync) before the next record. The reader validates each line as JSON before accepting it; a partial or invalid line is quarantined, never glued onto the next record. A quarantined record has a disposition: the task it described is marked for re-run from its start, and the quarantine is logged with the record's raw bytes. Checkpoints are written to a temp file and atomically renamed into place, never appended in place.

### 2.7 SSH: a 30-second timeout is a transport failure, not a task failure

The 30-second figure comes from the user's brief and the campaign log. Keep SSH alive with a keepalive interval of 15 seconds (proposed, below the 30-second death point), reconnect with retry, and never score a task on a single SSH timeout. On a timeout, re-check the remote state before deciding: retry up to 3 times with 5, 15, then 30 seconds of backoff (proposed) before declaring the remote state unknown. If the remote work completed, record it; only if the remote state is unknown after retry is the task marked for re-run.

### 2.8 Target IDs: resolve at runtime, validate against live state

No hardcoded target IDs anywhere in runner code. Every target ID is resolved at runtime from the single task-list file and validated before the task starts. Validation means a check against live state: the target element exists on the live page, or the ID resolves in the current session. Validating an ID against the same task-list file it came from is circular and proves nothing. A task whose target fails validation is blocked, not attempted with a stale ID.

### 2.9 Watchdog: heartbeat plus hash plus RSS plus snapshots

Browser-health heartbeat every 30-60 s, screenshot-hash comparison only after actions that should change the page (catches the #16706 freeze), RSS polling every 5-15 min with warn at 60% of system RAM and act at 70% or sustained growth above about 1 GB per hour (recommended values, no source gives them), and external tab-URL snapshots every few minutes. The action at 70% is, in order: minimize memory in `about:memory`, unload non-run tabs in `about:unloads`, then restart at the next task boundary.

Memory mid-run recovery ladder: if BiDi still answers, minimize memory in `about:memory` and unload non-run tabs in `about:unloads`; if it does not answer, kill and restart; if the OS OOM killer took it, same path plus check `dmesg` for the OOM kill line; if the run tab itself was unloaded, reload it over BiDi and re-check state.

On a slow response, wait first (search lag, section 1.6); kill only after 60 seconds of no response (the risk report's example threshold), then relaunch, verify the run tab by URL read from BiDi, and resume from the last completed task. If the #16706 freeze recurs after a restart, change the rendering path instead of restarting the same way again: run under XWayland (`MOZ_ENABLE_WAYLAND=0`), or disable hardware acceleration (`layers.acceleration.disabled=true` plus `gfx.webrender.software=true`, verify "WebRender (Software)" in `about:support`). Keep hardware acceleration enabled by default and switch only if the freeze recurs, and prefer headless if no headed UI is needed.

### 2.10 Recovery rules that hold for every failure

Resume from the last completed task, never from the interrupted one. Verify the run tab by URL read from BiDi before resuming. Never recover with safe mode. Never delete a profile lock while a Zen process is alive. Never re-issue a failed step the same way it failed (drag, urlbar typing, forced VA-API, stale target ID). A crashed task is re-run from its start and scored once.

### 2.11 Watchdog of the watchdog

The watchdog writes its own heartbeat with a timestamp to the run status file at least every 15 minutes. A second, independent check verifies it: the coordinator (or the deputy, if the coordinator is missing) reads the watchdog heartbeat on the same 15-minute cadence. If the watchdog heartbeat is stale, the coordinator writes the STALE flag to the run status file in the repo and alerts the owner through the standing path. The chain that catches silence must itself be watched, or the run is back to the failure mode the user named: nobody reports up until the owner asks.

## Sources

- Zen 1.24.3b source review, `improvements/zen-1.24.3b-source-review-20261124.md` (24 Nov 2026, commit 2232c0c).
- Zen 1.24.3b R3-L3 risk mitigations, `improvements/zen-1.24.3b-r3-l3-risk-mitigations-20261124.md` (24 Nov 2026, commit a587580).
- Zen issues, fetched 24 Nov 2026: #16718, #16723, #16694, #16706, #16746, #16710, #16685, plus related #16671, #10555, #14067, #15992. All at https://github.com/zen-browser/desktop/issues/<number>.
- R3-L3 long-run research report, `~/workspace/research_notes/zen-1-24-3b-r3l3-long-run-20261124-1253/report.md` (24 Nov 2026).
