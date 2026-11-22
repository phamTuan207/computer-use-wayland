# t08-settings-panel: settings panel workflow

## Context

A demo settings panel with four sections: Appearance (theme select,
accent radios), Notifications (two toggles), Privacy (one toggle),
and Account (display name, volume slider). Changes apply live, Save
persists them to localStorage, Reset restores defaults, and a search
box filters sections by keyword.

## Goal

Change every kind of control, save, reload to check persistence,
filter with search, reset to defaults, and confirm the defaults
persist too.

## Steps

1. Open the fixture page, check the preview is Light, volume 50,
   notifications On.
2. Select the Dark theme, check the preview reads Dark and the page
   gets the dark style.
3. Pick the Blue accent, check the preview swatch turns blue.
4. Turn notifications off, check the state reads Off.
5. Turn the weekly digest on, check the state reads On.
6. Turn share usage data off, check the state reads Off.
7. Fill the display name with `Demo User`.
8. Set the volume slider to 70, check the value reads 70.
9. Click Save, check the toast reads `Settings saved.`
10. Reload, check theme Dark, volume 70, name `Demo User`,
    notifications Off, digest On, privacy Off, accent Blue.
11. Search `theme`, check only the Appearance section shows.
12. Clear the search, check all 4 sections show.
13. Search `xyz`, check the no-match message shows.
14. Clear the search, click Reset, check the toast and the Light
    theme, volume 50, notifications On, empty name.
15. Reload, check the defaults are still in place.
16. Turn notifications on again and save.

## Pass conditions

- Every state, preview, value, and toast above matches.
- Saved settings survive a reload, and reset defaults survive a
  reload too.
- Search shows only matching sections and the no-match message
  when nothing matches.

## Fail conditions

- Any state or value differs from the expected value after an
  action, a save, a reload, or a reset.
- Search shows the wrong sections.

## Notes

`Demo User` is a placeholder name typed into a demo form, not a
real person's name. All state lives in the page and localStorage.
The browser run is Playwright Chromium; the same flow on Firefox
or Zen is UNVERIFIED.
