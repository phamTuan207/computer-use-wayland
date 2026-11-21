# t07-code-editor: code editor workflow

## Context

A demo code editor with three file tabs (main.js, utils.js,
notes.md), line numbers, Save (persisted to localStorage), Run
(evaluates the current file as a JavaScript expression), Find, and
Replace. Editing a tab marks it dirty until saved. Markdown files
cannot be run.

## Goal

Edit and run code, save and reload to check persistence, switch
tabs without losing unsaved edits, use find and replace, and check
error handling for bad code and markdown.

## Steps

1. Open the fixture page, check main.js contains `2 + 3`.
2. Click Run, check the output is `Result: 5`.
3. Change the editor to `10 * 4`, click Run, check `Result: 40`.
4. Check the main.js tab shows the dirty mark.
5. Click Save, check the status reads `Saved main.js.` and the
   dirty mark is gone.
6. Reload the page, check main.js still contains `10 * 4`.
7. Switch to utils.js, check it contains `7 - 2`, Run gives 5.
8. Edit utils.js to `7 - 2 + 100`, check its tab is dirty.
9. Switch to main.js and back, check the unsaved edit is kept.
10. Save utils.js, reload, check the edit persisted.
11. Switch to main.js, Find `10`, check `1 match`.
12. Replace `10` with `20`, check the editor reads `20 * 4` and
    Run gives 80.
13. Find `zzz`, check `0 matches`.
14. Switch to notes.md, click Run, check the markdown error.
15. Edit notes.md, Save, reload, check the new line persisted.
16. Switch to main.js, set the editor to `2 +`, click Run, check
    an error is shown.
17. Clear the editor, click Run, check an error is shown.

## Pass conditions

- Every run result, status line, editor content, and find result
  above matches.
- Saved edits survive a reload; unsaved edits survive a tab switch.
- The dirty mark appears on edit and clears on save.

## Fail conditions

- Any run result, content, or status differs from the expected value.
- A saved edit is lost after reload.
- Invalid code or a markdown file runs without an error.

## Notes

Run evaluates the editor text as a JavaScript expression inside the
page. All state lives in the page and localStorage. The browser run
is Playwright Chromium; the same flow on Firefox or Zen is UNVERIFIED.
