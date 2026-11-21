# t05-multi-tab: work across many tabs

## Context

A problem setter works with five problem tabs open at once. The list
tab shows five problems. Opening one problem in a new tab, editing its
title there, and going back to the list must show the new title after
a refresh. The tabs share state through local storage on the same
origin, the way a real judge site shares a session across tabs.

## Goal

Open five tabs, edit a problem title in its own tab, close that tab,
and confirm the list tab shows the updated title after refresh.

## Steps

1. Open the fixture list page.
2. Confirm five problem rows are listed.
3. Open problem 2 in a new tab from the list.
4. In the new tab, change the title to `Edited Title Two` and save.
5. Close the detail tab and return to the list tab.
6. Click `Refresh list` and read the row for problem 2.

## Pass conditions

- The list shows exactly five rows at the start.
- The detail tab opens with the original title `Problem Two`.
- After save, close, and refresh, the list row for problem 2 shows
  `Edited Title Two`.
- The other four rows are unchanged.

## Fail conditions

- Fewer or more than five rows at the start.
- The edited title does not appear in the list after refresh.
- Another row changes, or a row disappears.

## Notes

The fixture pages share local storage on the same origin, served by
the loopback server. No data leaves the machine. The browser run is
Playwright Chromium; the same flow on Firefox or Zen is UNVERIFIED.
