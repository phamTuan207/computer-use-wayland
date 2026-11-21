# t09-multi-window: multi-window workflow

## Context

A project dashboard with three projects (Alpha, Beta, Gamma). Each
project opens a detail window in a real popup where its title can be
edited, and a preferences window where the theme can be changed. The
popups send their result back to the main window with postMessage
and then close. Renames and the theme are also saved to localStorage.

## Goal

Rename a project through its popup twice, change the theme through
the preferences popup twice, cancel a rename, and handle two popups
open at the same time.

## Steps

1. Open the fixture page, check the three titles Alpha, Beta, Gamma.
2. Open the detail window for Alpha, check the input is prefilled
   with `Alpha`.
3. Change the title to `Alpha v2`, Save, check the main window
   shows `Alpha v2` and the status confirms the rename.
4. Open the detail window for Alpha again, check it prefills
   `Alpha v2`.
5. Change the title to `Alpha Final`, Save, check the main window.
6. Open the preferences window, pick Dark, Apply, check the main
   window turns dark.
7. Open the preferences window again, pick Light, Apply, check the
   dark style is gone.
8. Open the detail window for Beta, change the title, click Cancel,
   check Beta is still `Beta`.
9. Open the detail window for Gamma and the preferences window at
   the same time, check 3 pages exist in the browser context.
10. In the preferences popup pick Dark and Apply, check the main
    window turns dark.
11. In the detail popup save `Gamma v2`, check the main window
    shows it.
12. Check the final titles: Alpha Final, Beta, Gamma v2, and that
    only the main page remains open.

## Pass conditions

- Every title, status line, and theme change above matches.
- A cancelled rename leaves the title unchanged.
- Two popups open at once both deliver their result to the main
  window.

## Fail conditions

- Any title or theme state differs from the expected value.
- A popup result is lost or applied to the wrong project.
- A page remains open after all popups are closed.

## Notes

Popups are real browser pages opened with window.open and closed
with window.close. All state lives in the pages and localStorage.
After a popup closes, the checker polls the expected effect on the
main window for up to 5 s, because the popup posts its result with
postMessage and closes synchronously, so the opener applies the
effect on a later task. A cancelled rename is checked with a 500 ms
dwell and then an immediate read, because waiting for the unchanged
title would return instantly and prove nothing.
The browser run is Playwright Chromium; the same flow on Firefox
or Zen is UNVERIFIED.
