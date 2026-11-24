# Zen 1.24.2b vs 1.24.3b source diff, computer-use areas (2026-11-24)

- Worker: Zen source-diff worker (subagent). Owner-ordered.
- Method: repo zen-browser/desktop, tags 1.24.2b (base 0057b29) vs 1.24.3b (head 300f929). 22 commits ahead, 169 files changed (GitHub compare API).
- Execution-risk note: the shallow clone to ~/workspace/zen-diff-1243b tripped a runtime execution-risk flag, so NO git command was run inside the clone. The diff was done by other means: GitHub compare API JSON, per-commit .patch files, and raw file fetches at both tags. All machine checks were read-only over SSH. No BiDi or Marionette session was opened, no tab was driven, Zen was not restarted, user.js was not touched.
- No em dash or en dash in this file. Commas, periods, short hyphens only.

## 1. Machine ground truth, 2026-11-24 about 20:20-20:35 +07 (read-only SSH)

- Zen 1.24.3b, BuildID 20261118023529, Firefox 160.0.1, SourceStamp a127b1d27e5bb1f32f4b0f2368e7b1a81eb23e6f, from /opt/zen-browser-bin/application.ini.
- Main process PID 404548, started 2026-11-24 19:59:31, launch line `/opt/zen-browser-bin/zen-bin --remote-debugging-port=9222 --marionette`. Ports 9222 (BiDi) and 2828 (Marionette) listen on 127.0.0.1, owned by PID 404548.
- Zen total RSS 1791 MB. System 30 GB RAM, 20 GB available. Headroom is ample.
- user.js holds the D2 pins, and prefs.js holds them effective: `app.update.enabled=false`, `remote.prefs.recommended=false`. No staged update: no /opt/zen-browser-bin/updates/ dir, no profile updates/ dir.
- prefs.js holds NO override for `zen.little-window.enabled`, `zen.mods.auto-update`, `browser.tabs.unloadOnLowMemory`, `browser.sessionstore.interval`, or `zen.tab-unloader.*`. Defaults apply everywhere.
- Shipped-build verification (read-only `unzip -p` on omni.ja, no extraction to disk): the fixes below were confirmed present in the installed 1.24.3b binaries, not just in the repo.

## 2. What the diff found, by area

### A. Closed-window memory leak, fixed in source (gh-16587, gh-16618)

- Commit 8e76e2c0 (gh-16594, "Accept string values for boosts settings", 12 Nov): the leak fix rides in this commit. `src/zen/common/modules/ZenStartup.mjs` gains `#observingDelayedStartup` and `#stopObservingDelayedStartup()`: the `browser-delayed-startup-finished` observer is now removed on window unload, where before a window closed before delayed startup finished kept its observer and the whole `browser.xhtml` window stayed alive in the main process (about 6 MB each, cycle-collector pauses up to about 2 s, issue gh-16587). The same commit also switches `ClientEnvironment.version` to `Services.appinfo.platformVersion` (remote-settings env version, minor) and makes boosts accept string slider values (unrelated to the run).
- Commit 707532ee (gh-16629, "Remove pref observer on unload", 14 Nov): one line in `src/zen/library/ZenLibrary.mjs`, `#teardown()` now calls `Services.prefs.removeObserver(HIDDEN_TABS_PREF, this.#tabsObserver)`. This is the follow-up to gh-16587 (issue gh-16618: closed windows still never freed after the first fix).
- Verified in the shipped build: `ZenStartup.mjs` in browser/omni.ja contains `#stopObservingDelayedStartup` (lines 93-105); `ZenLibrary.mjs` in omni.ja line 960 has the `removeObserver(HIDDEN_TABS_PREF, ...)` call inside `#teardown()`.
- Why it matters: the run opens and closes task tabs and popups for 19-31 h. On 1.24.2b each closed window leaked; on 1.24.3b closing actually frees. This is the mechanism behind the A1 tab-hygiene rule in the optimizations doc, and it is now source-verified, not just release-note-verified.

### B. Tab unload, split-view protection now real (gh-16624)

- Commit 6880e903 (gh-16622, "Don't unload visible split view panes on low memory", 14 Nov): one line in `src/browser/components/tabbrowser/TabUnloader-sys-mjs.patch`, `isNonDiscardable` changes from `tab.zenModeActive` to `tab.linkedBrowser?.zenModeActive`.
- The nuance the release notes miss: raw files at both tags confirm 1.24.2b shipped `tab.zenModeActive`, a property that does not exist on tab elements (`zenModeActive` lives on the linked browser). The 1.24.2b check was dead code, so visible split-view panes were NOT actually protected. In 1.24.3b the check reads the real property, so the protection works for the first time.
- Verified in the shipped build: `TabUnloader.sys.mjs` in omni.ja line 54 reads `if (tab.undiscardable || tab.selected || tab.linkedBrowser?.zenModeActive)`.
- Why it matters: it strengthens the D4 conditional-unload decision. If `browser.tabs.unloadOnLowMemory` is ever enabled at the RSS trigger, visible split-view panes are genuinely exempt. It does not change the D4 trigger itself (still RSS over 8 GB, still not pre-emptive).

### C. Firefox 160.0.1 engine (gh-16681, commits 1664693b and 300f9292)

- The Zen repo change is only the version bump: `surfer.json` `version.version` 160.0 to 160.0.1, plus `build/firefox-cache/l10n-last-commit-hash` and a sessionstore test removal. The engine delta lives in mozilla-central, not this repo.
- Bug 2075175 confirmed FIXED with target milestone "160 Branch" (Bugzilla REST, 2026-11-24): "Subscribing to WebDriver BiDi network events blocks the parent process main thread while pages load". MDN Firefox 160 for developers lists it under WebDriver BiDi: "Updated network events monitoring to stop computing unused security details, which could have visible impacts on the performance, e.g., during a page load."
- Other Firefox 160 BiDi changes on the same MDN page (verified by fetch 2026-11-24): machine-readable CDDL for `moz:` extensions (bug 2057588); `script.message` context fix for `window.open` preload scripts (bug 2079905); Set-Cookie newline-split fix (bug 1940389); `runtime.PlatformInfo.arch` now `arm64` (bug 2080310); `windowId` on `runtime.MessageSender` (bug 2072133). Of these, only 2075175 and 2079905 touch the run's driving path, and neither changes any command shape the runner uses.
- Why it matters: the speed-crawl recommendation to subscribe to BiDi network events (`network.responseCompleted` etc.) was a performance trap on 1.24.2b / Firefox 159. On 1.24.3b / 160.0.1 that trap is fixed at the engine level. No runner code change is needed for this; it removes a known risk from the event-subscription pattern.
- Note: the worktree run scripts (`scripts/*.py`) contain no `subscribe` call, so the current tooling does not subscribe to network events at all. The fix therefore covers the pattern if the live executor adopts it, and is neutral otherwise.

### D. Mods: startup auto-update removed, duplicate stylesheet insert removed (gh-16674)

- Commit 37e77265 (gh-16675, "Skip redundant mods stylesheet re-parse on window init", 18 Nov): `src/zen/mods/ZenMods.mjs` loses the second `#insertStylesheet()` call on the window-init path, plus `#setNewMilestoneIfNeeded()`, `#shouldAutoUpdate()`, and the `requestIdleCallback` block that called `checkForModsUpdates()` at startup. Prefs `zen.mods.auto-update`, `zen.mods.auto-update-days`, and `zen.mods.last-update` are removed from `prefs/zen/mods.yaml` and from the settings UI.
- Precision from raw files at both tags: 1.24.3b still has ONE `#insertStylesheet()` call (line 101, in the initial mods load), and `checkForModsUpdates()` still exists as a callable method (line 533). What is gone is the duplicate insert on window init and the whole automatic startup update check. So window init is faster and no mod update fetch can fire at startup.
- Verified in the shipped build: `ZenMods.mjs` in browser/omni.ja has the single insert at line 101 and no `shouldAutoUpdate` or `auto-update` string; grep of the 1.24.3b source shows the same.
- Why it matters: no mid-run mod update can change the UI mid-measurement, and the D1 restart does not need a mods-update check. Any run doc telling the runner to set `zen.mods.auto-update` would be dead; grep of the worktree run docs finds no such reference.

### E. Little Zen mini-windows: present but Twilight-gated, off on 1.24.3b (gh-16638 and follow-ups)

- Commits 0691849c, 09431ff0, c7bbc2e3, 37513f03, 45dbc9fb (Little Zen, 14-17 Nov): new `src/zen/little-window/` modules, `prefs/zen/little-window.yaml`, sessionstore `isMiniWindow` marking, space-routing target, external-URI routing hooks, `zen.keyboard.global-shortcuts.enabled`.
- The gating pref: `prefs/zen/little-window.yaml` sets `zen.little-window.enabled` to `"@IS_TWILIGHT@"`. `surfer.json` at 1.24.3b defines two brands, release 1.24.3b and twilight 1.25t. The installed build is the release brand, so the pref defaults to false. prefs.js has no override. The feature is inert on this build unless the pref is flipped.
- Global shortcuts are Windows and macOS only: `prefs/zen/static.yaml` adds `zen.keyboard.global-shortcuts.enabled` with condition `defined(XP_MACOSX) || defined(XP_WIN)`. On Linux the pref does not exist and the service has no Linux implementation in the diff. No effect on this machine.
- Why it matters: if the pref were ever flipped on, external links and space routing could open pages in little windows instead of tabs, which would break BiDi window assumptions. Keep it off. See the applied guard in section 3.

### F. Verified no-change areas (read, no automation impact)

- SessionStore patch (`src/browser/components/sessionstore/SessionStore-sys-mjs.patch`, 44/36): the hunks are little-window `isMiniWindow` marking plus upstream Firefox 160 rebase line shifts. No save-interval, restore, or crash-recovery behavior change for normal windows. Sessionstore is untouched as a mechanism.
- BrowserContentHandler / BrowserDOMWindow / BrowserWindowTracker / URILoadingHelper patches: space-routing for external URIs (`handleExternalUri`, `takesExternalUrisWithoutWindow`, `openExternalUrisAfterStartup`) plus little-window exclusions. BiDi-created tabs are unaffected. CLI or OS-opened URLs while Zen runs could route through space routing, but no run step opens URLs that way.
- `src/external-patches/firefox/get_exposable_uri.patch` (new, via D336362): adds `BrowserUtils.getExposableURI`, used only for copy/share URL cleanup (unwrap Reader Mode, strip credentials, optional tracking-param strip). No automation impact.
- Pinned tabs (`src/zen/tabs/ZenPinnedTabManager.mjs`): pinned-URL comparison now ignores fragments; "Replace with Current URL" is disabled while on the pinned URL. Cosmetic.
- Vertical tabs manager, spaces manager, UI manager changes: little-window gating and a settings-window refactor. No tab-strip behavior change on this build.
- URL bar yaml: new pref `zen.urlbar.single-toolbar-show-zoom-button`, default false. Cosmetic.
- No change anywhere in the diff touches Marionette, BiDi, remote debugging, the remote port, or profile format. Those live in mozilla-central; the only engine delta is the 160.0.1 bump in section C.
- No new prefs the run should set were introduced. The only pref defaults added are `zen.little-window.enabled` (off) and `zen.keyboard.global-shortcuts.enabled` (Win/Mac only).

## 3. APPLIED for R3-L3 (each with test result on the real machine)

- A1. Little-window guard, recorded as a run rule (this file): do NOT enable `zen.little-window.enabled` at any point during the run. Test: prefs.js has no override (SSH read 2026-11-24 about 20:25 +07); the pref defaults to false on the release brand (surfer.json brands release 1.24.3b vs twilight 1.25t, yaml value `@IS_TWILIGHT@`). No pref change was needed because the default is already off. A live about:config read was deliberately not done (opening a session risks the runner slot; file evidence is sufficient).
- A2. Mods auto-update removal, recorded (this file): no mid-run mod update can fire, and the D1 restart procedure needs no mods-update check. Test: shipped `ZenMods.mjs` has no `shouldAutoUpdate` and no `auto-update` string (SSH read of browser/omni.ja); 1.24.3b source confirms the same; worktree grep finds no run doc referencing the removed prefs.
- A3. D4 conditional unload strengthened (this file): if the RSS trigger fires, visible split-view panes are genuinely protected in 1.24.3b. Test: shipped `TabUnloader.sys.mjs` line 54 reads `tab.linkedBrowser?.zenModeActive` (SSH read of omni.ja); 1.24.2b raw file confirms the old dead `tab.zenModeActive` check. The D4 trigger itself is unchanged (RSS over 8 GB, not pre-emptive).
- A4. Leak-fix mechanism confirmed (this file): the A1 tab-hygiene rule now rests on source-verified fixes, not only release notes. Test: shipped `ZenStartup.mjs` contains `#stopObservingDelayedStartup`; shipped `ZenLibrary.mjs` line 960 has the `removeObserver` in `#teardown()` (SSH reads of omni.ja).
- A5. BiDi network-event trap cleared (this file): subscribing to network events no longer blocks the parent main thread on this build. Test: Bugzilla bug 2075175 RESOLVED FIXED, target 160 Branch; MDN Firefox 160 lists the fix; installed engine is 160.0.1 (application.ini). No runner code change needed; the worktree scripts do not subscribe today.
- No code, pref, or user.js change was applied, because every fix above is already inside the shipped 1.24.3b build. The applied work is verification plus the two recorded guards (A1, A2) and the two strengthened decisions (A3, A4, A5).

## 4. NOT applied, with evidence and reason

- N1. Pre-emptive `browser.tabs.unloadOnLowMemory=true`: not set. Evidence: prefs.js has no override, default false on Linux; the optimizations doc D4 already decided conditional-only on RSS over 8 GB, and the 16624 fix (section 2B) only strengthens that conditional, it does not justify pre-empting it. Risk to reference and Class L re-read tabs is unchanged.
- N2. `browser.sessionstore.interval` change: not set. Evidence: sessionstore behavior is unchanged in the diff (section 2F); writes are 3.7 MB per interval with ample disk. The earlier R9 rejection stands.
- N3. Enabling Little Zen (`zen.little-window.enabled=true`): not set, and forbidden by A1. Evidence: Twilight-gated feature (section 2E); enabling it would change the window model the runner assumes. Owner rule: no Twilight 1.25t, stay on 1.24.3b.
- N4. Global shortcuts: nothing to set on Linux. Evidence: pref is conditioned to XP_MACOSX or XP_WIN (section 2E); no Linux implementation in the diff.
- N5. Any user.js addition: not touched. Evidence: user.js is owned by the parallel update worker and already holds the D2 pins (`app.update.enabled=false`, `remote.prefs.recommended=false`, both effective in prefs.js). No new pref from this diff needs pinning.
- N6. `zen.mods.auto-update=false` or similar: not set. Evidence: the pref no longer exists in 1.24.3b (removed from mods.yaml, absent from shipped ZenMods.mjs). Setting it would be dead.
- N7. Any pastebin user.js table, process-count cut, sessionstore gutting, or security-pref weakening: not applied. Evidence: none of these is supported by anything in the diff; the earlier R1/R3/R6/R10 rejections stand.

## 5. Uncertain items, not applied

- U1. Whether the live executor subscribes to BiDi network events. The worktree scripts do not, but the live executor is a separate agent and the speed-crawl doc recommends subscribing to `network.responseCompleted`. If it does, bug 2075175 covers it on this build. If it polls instead, the fix is neutral. No action; the uncertainty is about the executor's pattern, not the build.
- U2. External-URI space routing. BiDi-created tabs are unaffected (section 2F), but a URL opened via CLI or OS handler mid-run could route through space routing. No run step does that, so no action. If a future step does, it must be tested first.
- U3. Live about:config value of `zen.little-window.enabled`. Not read live (deliberate, see A1). The evidence chain is: yaml default `@IS_TWILIGHT@`, release brand 1.24.3b vs twilight 1.25t in surfer.json, no override in prefs.js. That chain is strong but not a live read.

## 6. Verdict

- GO on 1.24.3b. Every computer-use-relevant change in the 1.24.2b to 1.24.3b diff helps or is neutral: the closed-window leak is fixed twice over in source and in the shipped build, split-view unload protection works for the first time, the BiDi network-event main-thread block is fixed in Firefox 160.0.1, mods can no longer auto-update at startup, and the new Little Zen surface is off by default on this build. Nothing in the diff breaks BiDi on 9222, Marionette on 2828, session restore, or tab behavior the runner relies on.
- Diff artifacts kept on the VM (not committed): ~/workspace/zen-compare.json, ~/workspace/zen-compare.patch, ~/workspace/zen-c-16618.patch, ~/workspace/zen-c-16624.patch, ~/workspace/zen-c-16674.patch, ~/workspace/zen-c-16594.patch. The scratch clone at ~/workspace/zen-diff-1243b was not used for diffing after the execution-risk flag and will be removed.

## Sources (all accessed 2026-11-24)

- GitHub compare API: https://api.github.com/repos/zen-browser/desktop/compare/1.24.2b...1.24.3b (22 commits, 169 files; base 0057b29, head 300f929).
- Raw files at both tags: TabUnloader-sys-mjs.patch, ZenMods.mjs, surfer.json, prefs/zen/little-window.yaml (raw.githubusercontent.com/zen-browser/desktop/1.24.2b and /1.24.3b).
- Bugzilla bug 2075175: https://bugzilla.mozilla.org/rest/bug/2075175 (RESOLVED FIXED, target 160 Branch).
- MDN Firefox 160 for developers: https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/160 (BiDi section, fetched 2026-11-24).
- GitHub issues: gh-16587 (closed popup windows never freed), gh-16618 (follow-up), gh-16624 (split-view unload), via api.github.com/repos/zen-browser/desktop/issues.
- Laptop verification: SSH read-only, 2026-11-24 about 20:20-20:35 +07 (application.ini, ps, ss, user.js, prefs.js, omni.ja member reads).
- Prior work this builds on: rung3-run-log/r3-l3-zen-1.24.3b-optimizations-20261124.md (deep dive, A1/A2/D1/D4), improvements/zen-1.24.3b-r3-l3-report-20261124.md (clone1 web research, used as a cross-check, not as ground truth).
