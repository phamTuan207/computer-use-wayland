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
   shows `Alpha v2`, the status confirms the rename, and
   localStorage holds `project:alpha` as `Alpha v2`.
4. Open the detail window for Alpha again, check it prefills
   `Alpha v2`.
5. Change the title to `Alpha Final`, Save, check the main window,
   the status, and localStorage the same way.
6. Open the preferences window, pick Dark, Apply, check the main
   window turns dark, the status confirms it, and localStorage
   holds `theme` as `dark`.
7. Open the preferences window again, pick Light, Apply, check the
   dark style is gone, the status confirms it, and localStorage
   holds `theme` as `light`.
8. Open the preferences window, pick Dark, click Cancel, check the
   main window stays light and localStorage still holds `light`.
9. Open the detail window for Beta, change the title, click Cancel,
   check Beta is still `Beta`.
10. Open the detail window for Gamma and the preferences window at
    the same time, check 3 pages exist in the browser context.
11. In the preferences popup pick Dark and Apply, check the main
    window turns dark, the status confirms it, and localStorage
    holds `dark`.
12. In the detail popup save `Gamma v2`, check the main window
    shows it, the status confirms it, and localStorage holds it.
13. Check the final titles: Alpha Final, Beta, Gamma v2, and that
    only the main page remains open.
14. Dwell 500 ms and re-read the final titles and status, so a
    spurious message arriving after the final read is caught.
15. Reload the page and check the titles and the dark theme are
    restored from localStorage.

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
main window for up to 10 s, because the popup posts its result with
postMessage and closes synchronously, so the opener applies the
effect on a later task. The cap is 10 s so that a correct delivery
taking 6 s verifies instead of failing wrongly on the poll cap.
A cancelled rename is checked with a 500 ms dwell and then an
immediate read, because waiting for the unchanged title would return
instantly and prove nothing; a cancelled theme change is checked
the same way, against both the live theme and the saved one. The
checker reads localStorage after every rename and theme change and
reloads the page at the end to prove the saved state restores. A
500 ms settle re-read of the final titles guards against a spurious
message arriving after the final read.
The browser run is Playwright Chromium; the same flow on Firefox
or Zen is UNVERIFIED.
