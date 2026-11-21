# Zen keybind storage probe - verdict: FILE-BASED (customizations only)

Worker ZK, 2026-11-21 23:04-23:05 +07. Owner question: are Zen shortcuts stored as a file, or UI-only?
Answer: **file-based for customized shortcuts; defaults live in source, not in any file.**

## Evidence

### 1. The live file: customKeys.json (FOUND, read 23:04:37 +07)

Path: `/home/james/.config/zen/ae59l0ak.Default (release)/customKeys.json`
Size: 442 bytes, mtime Nov 13 13:36, owner james, mode 644.

Full contents (verbatim):
```json
{"key_openAddons":{"modifiers":"accel,shift","key":"A"},"key_newNavigatorTab":{"modifiers":"accel","key":"N"},"key_newNavigator":{"modifiers":"accel","key":"T"},"zen-workspace-switch-10":{},"zen-workspace-switch-9":{},"zen-workspace-switch-8":{},"zen-workspace-switch-7":{},"zen-workspace-switch-6":{},"zen-workspace-switch-5":{},"zen-workspace-switch-4":{},"zen-workspace-switch-3":{},"zen-workspace-switch-2":{},"zen-workspace-switch-1":{}}
```

Decoded (on Linux, `accel` = Ctrl):
- `key_openAddons` = Ctrl+Shift+A (Open Add-ons)
- `key_newNavigatorTab` = Ctrl+N (New Tab; Zen swaps Ctrl+N/Ctrl+T vs Firefox)
- `key_newNavigator` = Ctrl+T (New Window)
- `zen-workspace-switch-1` to `-10` = `{}` (cleared / unbound)

So this file records ONLY shortcuts that were changed or cleared. Everything else on this machine is a default.

### 2. No other store exists (checked 23:04-23:05 +07)

- `prefs.js`: zero shortcut/keybind prefs. Only match for `shortcut|keybind` is `accessibility.browsewithcaret_shortcut.enabled`. No `zen.keyboard` or `zen.keybind` pref.
- `user.js`: nothing key-related.
- `find` for `*shortcut*` / `*keybind*` / `*hotkey*` under `~/.config/zen`: no files. In particular there is NO `zen-keyboard-shortcuts.json` on this machine (a backup gist names that file; it does not exist here).
- `grep -r "zen-workspace-switch"` across the whole profile (excluding customKeys.json, storage, sessionstore-backups): no other file mentions it.

### 3. Mechanism confirmed by source/docs (web, 23:05 +07)

- Bugzilla 2001528 (Mozilla, customisable shortcuts implementation): "This stores shortcut information in a file called customKeys.json in the profile directory." Matches the live file exactly.
- Official docs https://docs.zen-browser.app/user-manual/shortcuts (crawled 2026-11-21 16:05 UTC): UI path is Settings > Keyboard Shortcuts (`about:preferences#zen-shortcuts`); editing a field writes the customization; the page lists the full DEFAULT table (Zen + Firefox inherited keys).
- Note: the docs table lists New Window Ctrl+N / New Tab Ctrl+T (Firefox mapping, with a `Crtl` typo), while this machine's customKeys.json shows the Zen swap (New Tab Ctrl+N, New Window Ctrl+T). The file on the machine is the ground truth for this machine, not the docs page.

## Verdict

- (a) **File-based, for customizations**: `customKeys.json` in the profile root. Reading it needs no browser, no UI, no session. That answers the owner's question: no, it is NOT UI-only.
- (b) **The FULL list (defaults + customs) is NOT in any single file.** Defaults live in Zen/Firefox source keysets. The Settings page renders defaults merged with customKeys.json. So a complete keybind list needs two sources: customKeys.json (machine truth for customs) + the default table (docs page, or the Settings DOM for the exact installed version).
- (c) UI path if ever needed: `about:preferences#zen-shortcuts` (Settings > Keyboard Shortcuts). No setting was changed during this probe (read-only).

## Recommended fastest way to extract the FULL keybind list later

1. Copy (never edit in place while Zen runs) customKeys.json and parse it: 1 command, exact, machine truth for every customized/cleared binding.
2. Get defaults from the already-fetched docs table (https://docs.zen-browser.app/user-manual/shortcuts), or, for the exact installed version, scrape the Settings page DOM via Marionette/BiDi at `about:preferences#zen-shortcuts` (DOM read, no screenshots, no clicking). Only use manual UI reading as a visual cross-check.
3. Merge: defaults + customKeys.json overrides = the full effective list. Write the result into the laptop-local computer-use install (machine-specific layer) only, never push it to the repo (owner order 23:03).
