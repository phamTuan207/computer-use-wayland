# Worker ZK log - Zen keybind storage probe
Started 23:04:10 +07, 2026-11-21. Owner question: are Zen shortcuts stored as a file, or UI-only?
Rule: read-only on the laptop. No profile/settings modification. Log every step with wall-clock + elapsed.

## 23:04 +07 (t+0s) - START
Brief received. Plan: file-based first (profile grep, prefs.js, shortcut files), web docs if needed, UI observe only if no file route answers.

## 23:04:37 +07 (t+27s) - PROFILE LISTED
~/.config/zen/ has 2 profiles; live one is ae59l0ak.Default (release). Notable file spotted in listing: customKeys.json in the profile root. prefs.js grep: only accessibility.browsewithcaret_shortcut.enabled; no ui.key / browser key prefs. find *shortcut*/*keybind*/*hotkey*: no files by those names (customKeys.json does not match those patterns).

## 23:04:41 +07 (t+31s) - customKeys.json READ
442 bytes, mtime Nov 13 13:36. Contents: key_openAddons accel+shift+A, key_newNavigatorTab accel+N, key_newNavigator accel+T, zen-workspace-switch-1..10 all {}. user.js: nothing key-related. This is the customized-shortcuts store.

## 23:04:50 +07 (t+40s) - WEB CONFIRMATION
Search: Bugzilla 2001528 confirms customKeys.json is the customisable-shortcuts store in the profile dir. Docs page confirms UI path Settings > Keyboard Shortcuts. Gist naming zen-keyboard-shortcuts.json does NOT match this machine (no such file).

## 23:05:12 +07 (t+62s) - NO OTHER STORE
grep zen.keyboard/zen.keybind in prefs.js: empty. grep -r zen-workspace-switch across profile (excl. customKeys.json, storage, sessionstore-backups): empty. Docs page fetched (crawled 16:05 UTC): full default table captured; docs list Firefox mapping for New Tab/Window, file on machine shows Zen swap, file wins.

## 23:05 +07 (t+~90s) - VERDICT
FILE-BASED for customizations (customKeys.json). FULL list needs defaults (docs/source or Settings DOM) + customKeys.json overrides. No UI visit needed for the probe; nothing modified on the laptop (read-only). Findings written to improvements/zen-keybind-storage-probe-20261121.md.
