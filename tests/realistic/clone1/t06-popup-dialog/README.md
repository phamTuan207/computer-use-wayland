# t06-popup-dialog: popup and dialog handling

## Context

A problem setter works through a review flow that mixes four kinds of
interruption: a browser alert, a confirm dialog, a prompt dialog, a
custom modal in the page, and a real popup window with its own form.
Each one must be handled and the page must record the right outcome
for each.

## Goal

Handle an alert, accept one confirm and dismiss another, answer a
prompt, fill and save the custom modal, and fill the popup window form
so the main page receives the value back.

## Steps

1. Open the fixture page.
2. Click `Show alert` and accept it.
3. Click `Ask confirm`, accept it, then click it again and dismiss it.
4. Click `Ask name`, answer `Reviewer` in the prompt.
5. Click `Open modal`, fill the note, save it.
6. Click `Open popup`, fill the name in the popup window, submit it,
   and read the value back on the main page.

## Pass conditions

- The alert is accepted and the page records `alert accepted`.
- The first confirm records `confirmed`, the second records
  `cancelled`.
- The prompt records `name: Reviewer`.
- The modal records the note text that was typed.
- The popup returns the name typed in the popup, shown on the main page.

## Fail conditions

- Any dialog leaves the page stuck with no recorded outcome.
- A confirm outcome is recorded backwards.
- The modal or popup value never reaches the main page.

## Notes

The fixture uses real browser dialogs and a real popup window. No data
leaves the machine. The browser run is Playwright Chromium; the same
flow on Firefox or Zen is UNVERIFIED.
