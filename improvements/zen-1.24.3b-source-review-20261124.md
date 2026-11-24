# Zen Browser 1.24.3b source review: what changed for computer-use automation

Date: 2026-11-24. Base tag 1.24.2b (`0057b295aee4a1ff00e0bd24e1150b7bc1a28503`), head tag 1.24.3b (`300f9292ddbaaebf24626b4a7451e5426a11d3d8`), repo zen-browser/desktop. Diff: 22 commits, 169 files, +10,937/-1,174 lines, fetched through the GitHub compare API (the local clone was blocked by an execution-risk check, so no git was run inside it). Scope: Marionette, WebDriver BiDi, tab unloading, memory, Wayland, automation prefs, remote debugging, and anything else that could help or hurt a 19-31 hour automated run (R3-L3).

## Verdict in one paragraph

1.24.3b adds no new automation capability and changes no automation protocol in this repo's diff. No Zen-side change to the automation surface (Marionette plus WebDriver BiDi) is visible here; Firefox 160.0.1 engine-side BiDi changes are outside this repo and unchecked here. The real gains for a long run come from two places: the Firefox engine pin moves 160.0 to 160.0.1, which carries the tab-crash, Wayland colour, and closed-window leak fix; and two Zen-side fixes, the Zen-mode tab-unloading exemption now reads the flag from the linked browser, which likely makes it effective where it may not have matched before (inferred, see 3.1), and installed mods can no longer auto-update mid-run. The one behavior change to watch is external-URI space routing, but its deferred-open path is gated on a pref that is off by default on stable, so it should not fire on a stock run profile (verified, see section 6).

## 1. What this repo is, and what it is not

zen-browser/desktop holds Zen-specific code plus `.patch` files that the surfer build system applies to Firefox source at build time. It does not contain Firefox source: zero changed files live under top-level `remote/`, `toolkit/`, `widget/`, `gfx/`, `modules/`, `dom/`, `devtools/`, or `testing/`. Changed top-level paths are `src/` (156 files), `locales/` (6), `prefs/` (4), `.github/` (1), `build/` (1), `surfer.json` (1).

Consequence: every Firefox 160.0.1 engine fix reaches Zen only through the version pin in `surfer.json` (`"version"` and `"candidate"` 160.0 to 160.0.1, `"displayVersion"` 1.24.2b to 1.24.3b, hunks `@@ -5,8 +5,8 @@` and `@@ -20,7 +20,7 @@`). The engine fixes themselves (Wayland WebGL/canvas colour, Bug 2089043; tab crashes, most notably ChatGPT, Bug 2088486; MFSA 2026-130, CVE-2026-130020 and CVE-2026-130021) are real for the run, but their code is not in this repo and cannot be cited from this diff beyond the pin.

How to read the citations: many changed files under `src/` are `.patch` files, which are themselves unified diffs against Firefox source, applied at build time. In such a file, an outer `+` line that starts with another `+` is new Firefox code in 1.24.3b, while an outer context line starting with a space followed by `+` is Firefox code that already existed in 1.24.2b and is unchanged. An "inner hunk" (for example `@@ -7,7 +7,7 @@`) is a hunk header inside the patch file, pointing at the Firefox file it patches. "Scoped diff lines" are line numbers in the scoped diff files produced for this review (`marionette-bidi-remote.diff`, `tab-unload-session.diff`, `memory.diff`, `wayland-linux.diff`, `prefs-automation.diff`, `zen-ui.diff`, `version-build.diff`, `other.diff`), kept in the working notes. A "raw file" length is the length of a `.patch` file as fetched at a tag through the API. Where this report says something did not change, it means no change in this repo's diff; Firefox engine code is not in this repo.

For `.patch` files, line references below give the Zen repo path first, then the inner hunk against the Firefox file it patches. An inner addition that already existed in 1.24.2b is not a new change; only lines whose outer diff marker changed are new in 1.24.3b.

## 2. No Marionette, WebDriver BiDi, or remote debugging change (confirmed)

A path scan of all 169 changed files finds zero filenames containing marionette, webdriver, bidi, or remote-debugging. A case-insensitive text scan of the whole compare response finds those terms nowhere in any patch text. The only file in the automation area is a new test, `src/zen/tests/security/browser_remote_settings_env_version.js` (+42), which tests Mozilla RemoteSettings (remote configuration: CRLite revocation data), not remote control. It asserts `ClientEnvironmentBase.version` equals `Services.appinfo.platformVersion`, and that CRLite records pass their version gate.

Impact: anything that drove 1.24.2b over Marionette plus BiDi drives 1.24.3b the same way, as far as this repo's diff shows. No new capability, no regression visible in this repo's diff.

## 3. Tab unloading: exemption fix (inferred), timed-unloader registration gone

### 3.1 One-line fix to the non-discardable check

`src/browser/components/tabbrowser/TabUnloader-sys-mjs.patch`, targeting Firefox `browser/components/tabbrowser/TabUnloader.sys.mjs`, `DefaultTabUnloaderMethods.isNonDiscardable`, inner hunk `@@ -7,7 +7,7 @@` (scoped diff lines 343-344). The added line changed from `if (tab.undiscardable || tab.selected || tab.zenModeActive)` to `if (tab.undiscardable || tab.selected || tab.linkedBrowser?.zenModeActive)`. No other unloader logic changed anywhere in the diff.

Impact: `isNonDiscardable` decides which tabs the memory-pressure unloader must never unload. The 1.24.2b check read the Zen-mode flag off the tab element; 1.24.3b reads it off the tab's linked browser element, with `?.` guarding tabs that have no linked browser yet. The plausible reading (inferred) is that the old check never matched, so the exemption now likely works where it did not before. But whether `linkedBrowser.zenModeActive` is ever true is unverifiable from this diff: `zenModeActive` occurs exactly twice in the whole compare response, both lines of this change, and its definition site is in unchanged code outside the diff. If the property is set on the tab element rather than the browser element, the new check would fail in the opposite direction. This report also cannot state what Zen mode is or how a tab enters it; that is open question 5. This lines up with the release-note fix for tabs being unloaded under memory pressure (gh-16624, split view and Glance tabs); the commit attribution is inferred, and the code change itself only touches the Zen-mode flag, so the full split-view/Glance fix may also depend on Firefox 160.0.1 engine behavior arriving through the pin.

### 3.2 The timed unloader's pref registration is gone

`src/browser/components/preferences/zen-settings.js`, scoped diff lines 684-790: the whole `Preferences.addAll` block was deleted in the settings-window rewrite. It defined `zen.tab-unloader.timeout-minutes` (type int, default 10). A grep of the entire compare response finds that pref exactly once, in this deletion. It appears in no new file and no new settings pane. The related pref `zen.tab-unloader.excluded-urls` appears 0 times in the compare response, so it is untouched by this diff.

Impact: the pref's UI registration is gone with no replacement, so setting `zen.tab-unloader.timeout-minutes` in a user.js does nothing as far as this diff shows. What this diff does not show is a timer implementation being removed, so the claim that the timed unloader mechanism itself is gone rests on Zen Discussion #9087 (retrieved 24 Nov 2026, discussion date not shown), which reports that Zen's timed unload was removed and replaced with Firefox's native tab unloader, so tabs now unload only on low memory. A live check (set the pref in a test profile and watch whether timed unloading still happens) would confirm it. Until then, treat the mechanism claim as reported, not diff-proven. The levers that remain are the Firefox prefs `browser.tabs.unloadOnLowMemory` and `browser.tabs.min_inactive_duration_before_unload`, which are not changed anywhere in this diff, and keeping memory headroom so the pressure unloader never fires.

## 4. Session restore: little windows are excluded, the rest is unchanged

`src/browser/components/sessionstore/SessionStore-sys-mjs.patch`, targeting Firefox `browser/components/sessionstore/SessionStore.sys.mjs`, inner hunk `@@ -1767,10 +1796,17 @@` (scoped diff lines 19-27). The mini-window test changed from matching only the `mini-window` attribute to matching `mini-window` or `zen-little-window`, so a little window is marked `isMiniWindow = true` and excluded from saved session state. All other hunks in this patch file only shift line numbers by +3. The Zen session hooks (`ZenSessionStore.onNewEmptySession`, `onRestoringClosedWindow`, `maybeSaveClosedWindow`, `_shouldOverrideTabs`, the `zen.workspaces.continue-where-left-off` check) already existed in 1.24.2b and are byte-identical here. New test `src/zen/tests/little_window/browser_little_window_session.js` (+26) asserts the exclusion: an open little window is not counted in `SessionStore.getBrowserState()`, and closing one does not increase the closed-window count.

Impact: never run the automation tab in a little window, it will not restore after a crash or restart. Main-window restore behavior is otherwise unchanged in this release. The removed sessionstore unit test `test_write_json_length_hint.js` (-73) is test-only and has no runtime impact.

## 5. Prefs: 21 removed from the old UI, 15 rewired, 6 without rewiring

The deleted `Preferences.addAll` block in `zen-settings.js` (scoped diff lines 684-790) defined 21 prefs. (The separate `Preferences.addSetting` statement at lines 792-796 defines the `zenWorkspaceContinueWhereLeftOff` setting, not part of the block.) Fifteen reappear as `data-pref` toggles in the new settings window, so they keep their names as far as this diff shows; their defaults are unverified from this diff, because the defaults listed here came from the deleted block and the new window must get defaults from the static pref definitions (`prefs/zen/*.yaml`) or from Firefox, so a fresh profile could behave differently for a pref with no static definition. The exceptions:

- `zen.tab-unloader.timeout-minutes`: dead, see 3.2. No replacement anywhere.
- `zen.mods.auto-update` and `zen.mods.auto-update-days`: fully removed, see section 7.
- `zen.pinned-tab-manager.close-shortcut-behavior` (string, default "switch"): its UI is gone. The whole old Tabs Management pane `src/browser/components/preferences/zenTabsManagement.inc.xhtml` (-82) was deleted, including the menulist with options `reset-unload-switch`, `unload-switch`, `reset-switch`, `switch`, `reset`, `close`. The pref appears only in deletion lines across the diff. Whether unchanged runtime code still reads it is not visible in this diff; do not depend on close-shortcut unload behavior.
- `zen.workspaces.open-new-tab-if-last-unpinned-tab-is-closed`: its only occurrence in the whole compare response is this deletion, with no replacement wiring found.
- `zen.glance.enabled`: no `data-pref` toggle found, but the new settings window references it via `data-depends-on`, so the pref is still live.
- `media.videocontrols.picture-in-picture.enabled`: registration removed only. It is a Firefox builtin pref with its own Firefox-side default, and no change to that default is visible in this diff.

Also moved, not removed: the `zen.workspaces.continue-where-left-off` checkbox left Firefox's own startup settings UI (`src/browser/components/preferences/main-js.patch`) and is now a toggle in the new settings window; the pref itself still works and SessionStore still reads it. Set it in user.js if a restart-with-restore strategy is intended. The old Looks and Feel pane `src/browser/components/preferences/zenLooksAndFeel.inc.xhtml` (-104 lines) was deleted too, including the `#zenTabsUnloadDelayContainer` styles, consistent with the timed unloader being gone; the layout prefs `zen.view.sidebar-expanded` and `zen.view.use-single-toolbar` themselves are not removed, only their old picker UI.

New prefs: `zen.little-window.enabled` (`prefs/zen/little-window.yaml`, value `"@IS_TWILIGHT@"`, Twilight only, where Twilight is Zen's pre-release channel; see section 8); `zen.keyboard.global-shortcuts.enabled` (Mac/Windows only, see section 9); `zen.urlbar.single-toolbar-show-zoom-button` (false, cosmetic).

## 6. External URIs: space-routed or deferred, but gated off by default (verified)

This is the largest automation-relevant behavior change in the diff, and the verification below settles when it fires.

`src/browser/components/BrowserContentHandler-sys-mjs.patch` (+68/-2), targeting Firefox `browser/components/BrowserContentHandler.sys.mjs` (raw file 95 lines at 1.24.2b, 161 at 1.24.3b). In `handURIToExistingBrowser`, inner hunk `@@ -1331,13 +1390,38 @@`, an external URI first goes to `gZenSpaceRoutingManager.handleExternalUri`; if it claims the URI, no regular window opens. When `takesExternalUrisWithoutWindow` is true, the URI is queued with `openExternalUrisAfterStartup` instead of opening immediately. In `nsDefaultCommandLineHandler`, inner hunks `@@ -1771,6 +1855,7 @@`, `@@ -1786,6 +1871,10 @@`, `@@ -1793,6 +1882,17 @@`, command-line URLs are collected into a new `zenExternalURIs` array when the same condition holds, and likewise deferred until after startup.

Verification of the trigger (checked directly in the diff by the reviewer): the getter is added in `src/zen/space-routing/ZenSpaceRoutingManager.sys.mjs` (zen-ui.diff lines 638-640) and reads:

```
get takesExternalUrisWithoutWindow() {
  return lazy.ZenLittleWindow.enabled;
}
```

`ZenLittleWindow.enabled` is the pref `zen.little-window.enabled`, defined in `prefs/zen/little-window.yaml` with value `"@IS_TWILIGHT@"`, which is false on stable builds. The default external route also falls back to `most-recent-space` when the feature is off (`ZenSpaceRoutingManager.sys.mjs`, `getDefaultExternalRoute()`).

The chain is complete: `ZenLittleWindow.enabled` reads the pref through a lazy preference getter with default false (`ZenLittleWindow.sys.mjs`, other.diff lines 3087-3090), and the yaml value `"@IS_TWILIGHT@"` is false on stable.

Conclusion, in three parts. Deferral does not fire (verified): on a stock stable 1.24.3b run profile, the deferred-open path should not fire, because the getter returns false. Command-line URLs take the old path (verified): collection into `zenExternalURIs` is conditional on the same getter. External URIs to a running instance (unverified): `handURIToExistingBrowser` now calls `getWindowForExternalUri(uri, navWin)` unconditionally instead of `openInWindow(navWin)`, and that method has no definition in this diff, only call sites, so its behavior when the feature is off is not visible here. The harness adaptation is still cheap insurance: after launch, wait for the run tab to appear rather than assuming it opens at launch, and verify the run tab by URL rather than by window position, since a URI can land in a different space or window than the top window. If the run profile ever enables the little-window pref, the deferred path becomes live.

Related: `src/browser/modules/BrowserWindowTracker-sys-mjs.patch` (+11/-3), inner hunk `@@ -211,6 +211,7 @@`, adds `!win.document.documentElement.hasAttribute("zen-little-window")` to the window-selection filter, so Little Window windows are never picked as the top window. `src/browser/modules/BrowserDOMWindow-sys-mjs.patch` (+3/-3) is re-anchored only (anchors moved +19 lines because Firefox 160.0.1 added code above); no Zen logic changed there. `src/browser/modules/URILoadingHelper-sys-mjs.patch` (+5/-5) adds one line in `openInWindow` (inner hunk `@@ -252,6 +252,7 @@`): a window opened from a link gets `win._zenStartupSyncFlag` set from the pref `zen.window-sync.open-link-in-new-unsynced-window` (default not defined in this diff), so a link-opened window may start unsynced, with no spaces.

## 7. Mods auto-update fully removed (stability gain)

`prefs/zen/mods.yaml` (lines 44-52) deleted `zen.mods.auto-update-days` (20) and `zen.mods.auto-update`. `src/zen/mods/ZenMods.mjs` (+0/-53, deletions only) deleted `#shouldAutoUpdate()`, `#setNewMilestoneIfNeeded()`, and the idle-callback trigger for `checkForModsUpdates()`; the manual check method itself was not deleted. The marketplace auto-update checkbox and its Fluent string were deleted, and `src/zen/tests/ignorePrefs.json` dropped `zen.mods.last-update` from its ignore list.

Impact: installed mods can no longer auto-update on startup or on a version milestone, so a mod cannot change behavior mid-run and no update check runs on an idle callback during the run. Set the desired mods before launch; they stay fixed. This is mods (themes) only; `app.update.*` is untouched by this diff. The same file also drops a redundant mods stylesheet re-parse on window init, likely part of gh-16674 (attribution inferred), the release-note fix for slow new-window opening with mods installed, a small window-init speedup.

## 8. Little Window: new feature, off by default on stable

New files: `src/zen/little-window/ZenLittleWindow.sys.mjs` (+275), `ZenLittleWindowChrome.mjs` (+789), `zen-little-window.css` (+423). A little window is a small chromeless window for one page (default 960x680, URL-bar-only 680x66, minimum 400x300), with no tabs toolbar, no sidebar, and no workspaces UI. Entry points: the `cmd_zenNewLittleWindow` command, the `zen-new-little-window` key (Ctrl+Alt+N), the app menu item, and external URIs when the feature is on.

Gating: `prefs/zen/little-window.yaml` sets `zen.little-window.enabled` to `"@IS_TWILIGHT@"`, false on stable 1.24.3b. When disabled, `open()` returns null, the menu command is disabled, and external URIs stay on the most-recent-space route.

If enabled, the impact is large: little windows are excluded from top-window selection (section 6), a URL-bar-only little window self-closes on urlbar blur, closing one returns focus to the previous app, little windows are not saved in session state (section 4), external links default to little windows when no explicit default route is stored, and a glance request from a popup or little window opens a plain tab in a regular window instead of a glance. BiDi window handles include little windows as normal browsing contexts; they are distinguishable by the documentElement attribute only from chrome context, not from a web page.

Recommendation: leave `zen.little-window.enabled` at its default (off) for R3-L3. If the run profile ever enables it, add a watchdog check that no window carries the `zen-little-window` document attribute.

## 9. Settings window rewrite and global shortcuts

### 9.1 Settings window: bare openPreferences() now opens a separate dialog

New module `src/zen/settings/ZenSettings.sys.mjs` (+84) and window `src/zen/settings/ZenSettingsWindow.mjs` (+392), with ten panes under `src/zen/settings/panes/` and seven section modules under `src/zen/settings/sections/`. Wiring: `src/browser/base/content/utilityOverlay-js.patch` makes `openPreferences(paneID, extraArgs)` first call `ZenSettings.handleOpenPreferences`, which opens the new `Zen:Settings` dialog window (`chrome://browser/content/zen-components/windows/zen-settings-window.xhtml`, features `chrome,centerscreen,dialog,resizable=no`) for a bare call, and returns false for a pane-specific call, which still opens the old `about:preferences` tab. The new window hands off to the old UI for things it does not own (mods, more settings, privacy, sync).

Impact: a harness that opens settings and then counts tabs or looks for an `about:preferences` tab will not find one for a bare call, and will see an extra top-level window instead. Pane-specific calls are unchanged.

Open question: the 17 Nov 2026 release notes describe the Zen settings window as Twilight-only, but no Twilight gate exists anywhere in this diff (the only `"@IS_TWILIGHT@"` value in the whole diff is the little-window pref). The wiring calls `handleOpenPreferences` unconditionally. Recommend a live check in the built 1.24.3b (call `openPreferences()` with no arguments) before asserting either way.

Also removed with the old UI: the restart prompt for unload-related prefs. `zen-settings.js` (scoped diff lines 634-682) deleted `gZenWorkspacesSettings` and `tabsUnloaderPrefListener`, which restarted the browser on changes to `zen.glance.enabled`, `zen.workspaces.separate-essentials`, and `zen.window-sync.sync-only-pinned-tabs`. `confirmRestartPrompt` occurs exactly once in the whole compare response, in this deletion. The same deleted object also held `toggleZenCycleByAttrWarning`, which observed `zen.tabs.ctrl-tab.ignore-essential-tabs` and `browser.ctrlTab.sortByRecentlyUsed`. Replacement is a static "Takes effect after restarting" note under the two toggles in the new settings window. Impact: a scripted pref change will not hit a modal mid-run, but a restart may still be silently needed. Set these prefs before launch, not mid-run.

### 9.2 Global keyboard shortcuts: inert on Linux

New service `src/zen/kbs/ZenGlobalShortcuts.cpp` (+318) and `.h` (+109), with macOS (`ZenGlobalShortcutsCocoa.mm`, +119) and Windows (`ZenGlobalShortcutsWin.cpp`, +130) implementations and no Linux implementation file. The header compiles `AttachKeyset`/`DetachKeyset` as empty inline functions on any platform other than macOS or Windows, and the pref `zen.keyboard.global-shortcuts.enabled` (`prefs/zen/static.yaml`) is conditioned on `XP_MACOSX || XP_WIN`. The only global key in the diff is Ctrl+Alt+N for a new little window.

Impact: on Linux/Wayland this feature does nothing. Ctrl+Alt+N cannot steal keys or fire during a Linux run, because the OS-level registration never happens there. Note the same key is also a normal in-window key, so pressing it while Zen is focused still runs the little-window command when that pref is on; with the pref off the command is disabled.

## 10. Other changes with automation consequences

- Glance from a popup or little window now opens a plain tab in a regular window (`src/zen/glance/ZenGlanceManager.mjs`, `openGlance()` checks `gZenVerticalTabsManager.hidesTabsToolbar`). In a regular window glance works as before. A harness that opens a glance from a popup window would see a tab appear in a different window than expected.
- Spaces Sync creates missing built-in containers on demand (`src/zen/sync/ZenSpacesSyncModel.sys.mjs`, +76/-16; `ZenSpacesSyncApplier.sys.mjs`, +2/-4). Containers 1-4 (Personal, Work, Banking, Shopping) are created through `ContextualIdentityService` when a synced record references a guid with no local mapping, instead of failing the record. On a fresh synced profile they can appear mid-run; R3-L3 does not use sync, so low risk.
- Zoom change shows a toast in single-toolbar or compact layouts (`src/zen/common/modules/ZenUIManager.mjs`, +41, `zen-zoom-changed-toast`), because the zoom level button is hidden there. A harness that screenshots or queries toasts should expect it.
- Copy URL now copies all selected tabs (`src/zen/common/modules/ZenCommonUtils.mjs`, new `getCurrentURLs()`), through the new `BrowserUtils.getExposableURI` helper (`src/external-patches/firefox/get_exposable_uri.patch`, new, +124), which unwraps Reader Mode URLs, strips credentials, and optionally strips tracking parameters. Clipboard content only; no driving impact. The old urlbar `zenStrippedURI` getter (25 lines) was removed and replaced by this helper.
- `ClientEnvironmentBase.version` now returns the Gecko platform version instead of the Zen display version (`src/toolkit/components/utils/ClientEnvironment-sys-mjs.patch`, new, +13, inner hunk `@@ -132,7 +132,7 @@`: `AppConstants.MOZ_APP_VERSION_DISPLAY` to `Services.appinfo.platformVersion`). This is why the RemoteSettings test in section 2 exists. No automation impact; only RemoteSettings version gating changes.
- Shift/Alt urlbar overrides are now gated on the pref `zen.urlbar.enable-overrides` (`_toggleActionOverride` returns early unless it is true). Its default is not defined anywhere in this diff (open question 4).
- The pinned-tab context menu item "Replace pinned URL with current" is now disabled when the tab is already on its pinned URL (new `#isPinnedUrl` helper, fragment-stripped comparison). A harness that clicks it must check disabled state first.
- The `tabs-css.patch` change is a rebase only: the Firefox 160.0.1 base CSS changed one line, Zen still removes it and still adds its own `top: -2px`. Net rendered result is identical to 1.24.2b, so coordinate-based automation is unaffected.
- Space switching is now a scripted crossfade (`src/zen/spaces/ZenSpaceManager.mjs`, `#crossfadeBackgrounds`; `src/zen/spaces/ZenGradientGenerator.mjs`, cached gradients). The state change (active workspace id) is the same; a harness should wait for the workspace change to settle rather than timing the animation.
- `src/zen/common/modules/ZenStartup.mjs` (+16/-1) removes the delayed-startup observer on window unload, a small robustness fix for windows closed before delayed startup. `src/zen/mods/ZenMods.mjs` also skips a redundant stylesheet re-parse on window init (section 7).

## 11. What did NOT change in this repo's diff (confirmed by absence)

Checked by grepping the whole compare response:

- No Marionette, WebDriver BiDi, or remote debugging code or pref (section 2).
- No memory-management code: `memory.diff` is empty. The release-note fix for closed windows never being freed (gh-16587) is therefore inherited through the Firefox 160.0.1 pin, not implemented in Zen code here.
- No Wayland, XWayland, X11, widget/gtk, gfx, or Linux code: `wayland-linux.diff` is empty, zero hits for those terms across all diff files. The Wayland colour fix (Bug 2089043) is likewise inherited through the pin.
- No change to `browser.tabs.unloadOnLowMemory`, `browser.tabs.min_inactive_duration_before_unload`, `browser.sessionstore.interval`, or `app.update.*`: 0 occurrences each.
- No change to `zen.tab-unloader.excluded-urls`: 0 occurrences, untouched by this diff.
- `.github/workflows/sync-upstream.yml` (+23/-1) only adds tracking-issue creation for future Firefox syncs (process only, no browser impact).

The engine side is unchecked here: whether Firefox 160.0.1 itself changed BiDi behavior cannot be stated from this repo, because the engine code is not in it.

## 12. Ranked recommendations for the R3-L3 run

1. Run 1.24.3b, pinned. The long-run stability gains are the Firefox 160.0.1 engine fixes, which arrive only through the `surfer.json` pin, plus the Zen-mode exemption, which now reads the flag from the linked browser (inferred, section 3.1), and mods, which cannot auto-update (manual check survives, section 7). No driver change is needed: no Zen-side change to Marionette plus BiDi is visible in this repo's diff, so existing drivers should work as on 1.24.2b.
2. Do not set `zen.tab-unloader.timeout-minutes`. It does nothing as far as this diff shows (section 3.2). Protect the run tab by excluding its URL with `zen.tab-unloader.excluded-urls` (untouched by this diff) and by keeping memory headroom so the pressure unloader never fires. Do not rely on the Zen-mode exemption: it is inferred only, and this report does not establish how a tab enters Zen mode.
3. Keep the run tab in the main window. Little windows are not restored after a restart (section 4), are excluded from top-window selection (section 6), and self-close on blur when URL-bar-only.
4. Leave `zen.little-window.enabled` at its default (off on stable). If it is ever enabled, the external-URI deferral path in section 6 becomes live.
5. Launch without a start URL, or wait for the run tab to appear and verify it by URL. The deferred-open path is gated off on a stock profile, but the external-URI routing call changed (section 6), so the check costs nothing and survives a future pref flip.
6. Set `zen.glance.enabled`, `zen.workspaces.separate-essentials`, and `zen.window-sync.sync-only-pinned-tabs` before launch. Changing them mid-run no longer pops a restart prompt, but a restart may still be silently needed.
7. Set mods before launch; they cannot auto-update mid-run. Do not depend on the pinned-tab close-shortcut unload options; their UI is gone.
8. Expect a separate `Zen:Settings` dialog window from a bare `openPreferences()` call, pending the live check in open question 1, and a zoom toast on zoom changes in single-toolbar or compact layouts. Count windows and tabs accordingly.
9. Do not rely on Ctrl+Alt+N or any global shortcut on Linux; the service is inert there. No key-stealing risk from it during the run.

## 13. Open questions

1. Settings window Twilight status: the source wires it unconditionally, the 17 Nov 2026 release notes call it Twilight-only. Live-check the built 1.24.3b before asserting.
2. Whether `zen.pinned-tab-manager.close-shortcut-behavior` still has any effect when set as a raw pref. The UI is gone and no code in this diff reads the pref, but unchanged code outside the diff may still read it.
3. Whether `"@IS_TWILIGHT@"` for `zen.little-window.enabled` evaluates to false on the exact stable 1.24.3b build the run will use. The yaml says so; a live `about:config` check settles it.
4. The default values of `zen.window-sync.open-link-in-new-unsynced-window` and `zen.urlbar.enable-overrides` are not defined anywhere in this diff, so whether a link-opened window starts synced or unsynced by default, and whether Shift/Alt urlbar overrides are on by default, cannot be stated from the source alone.
5. Where is `zenModeActive` set, and how does a tab enter Zen mode? The property occurs exactly twice in the whole compare response, both lines of the TabUnloader change, so its definition site is in unchanged code outside this diff.

## Sources

- GitHub compare API, `repos/zen-browser/desktop/compare/1.24.2b...1.24.3b`, fetched 2026-11-24 (22 commits, 169 files, +10,937/-1,174, not truncated). Raw response and scoped diffs kept in the working notes.
- Zen official release notes, https://zen-browser.app/release-notes/ (1.24.3b, 17 Nov 2026).
- Firefox 160.0.1 release notes, https://www.firefox.com/en-US/firefox/160.0.1/releasenotes/ (17 Nov 2026); MFSA 2026-130, https://www.mozilla.org/en-US/security/advisories/mfsa2026-130/ (17 Nov 2026).
- Zen Discussion #9087, https://github.com/zen-browser/desktop/discussions/9087 (retrieved 24 Nov 2026, discussion date not shown): Zen's timed tab unload was removed and replaced with Firefox's native tab unloader.
- Scoped diff files: `marionette-bidi-remote.diff` (1 file), `tab-unload-session.diff` (6 files), `memory.diff` (empty), `wayland-linux.diff` (empty), `prefs-automation.diff` (14 files), `zen-ui.diff` (22 files), `version-build.diff` (11 files), `other.diff` (119 files).
- Three independent analyses (tab unloading and prefs; automation surface; Zen UI and other) plus reviewer verification of the load-bearing claims against the raw diffs (TabUnloader one-liner, `takesExternalUrisWithoutWindow` getter, `surfer.json` pin, zero marionette/bidi hits, single `timeout-minutes` occurrence).
