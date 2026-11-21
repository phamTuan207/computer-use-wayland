# test-01-spreadsheet-formula.md

## Test ID
test-01-spreadsheet-formula

## Topic
Spreadsheet data entry + formula check.

## Context
Pham Tuan needs to reconcile a small weekly sales sheet before a meeting. The
sheet opens in a local spreadsheet app (offline fixture). Pham Tuan enters
several rows of numbers, writes SUM/average formulas in a totals row, then
verifies the computed values match hand-computed expectations. The agent must
read cell values, spot a formula that returns wrong text (a typo in the formula
string), correct it, and confirm the totals update. This is a multi-step data
entry task with a verification pass after each batch of edits.

## Goal
Enter 5 sales rows, write 3 formulas (total, average, count), confirm each
computed cell equals the expected value, fix one intentionally wrong formula,
and re-confirm it computes correctly.

## Exact steps
1. Open the spreadsheet fixture `fixtures/test-01-spreadsheet.html` in the
   local browser (offline, file:// URL).
2. Verify the sheet grid is visible with headers Date, Item, Units, Price,
   Total.
3. Click cell A2 (first data row, Date column) and type `2026-11-16`.
4. Click cell B2 and type `Widget`.
5. Click cell C2 and type `12`.
6. Click cell D2 and type `45000`.
7. Click cell E2 and type formula `=C2*D2` then press Enter.
8. Click cell A3 and type `2026-11-17`.
9. Click cell B3 and type `Gadget`.
10. Click cell C3 and type `7`.
11. Click cell D3 and type `82000`.
12. Click cell E3 and type formula `=C3*D3` then press Enter.
13. Click cell A4 and type `2026-11-18`.
14. Click cell B4 and type `Tool`.
15. Click cell C4 and type `5`.
16. Click cell D4 and type `150000`.
17. Click cell E4 and type formula `=C4*D4` then press Enter.
18. Click cell E5 (totals row) and type formula `=SUM(E2:E4)` then press Enter.
19. Read the value of E5 and confirm it equals 1864000 (12*45000 + 7*82000 +
    5*150000).
20. Click cell E6 and type formula `=AVERAGE(E2:E4)` then press Enter.
21. Read E6 and confirm it equals 621333 (rounded) - the fixture reports
    rounded whole numbers.
22. Click cell E7 and type the intentionally wrong formula `=COUNT(E2:E4)`
    then press Enter.
23. Read E7: it should show 3. Observe that the agent notices E7 shows text
    instead of a number (intentional wrong formula planted by fixture).
24. Click E7 and replace the formula with `=COUNTA(E2:E4)` then press Enter.
25. Re-read E7 and confirm it shows 3.
26. Read C2,C3,C4,E2,E3,E4,E5,E6,E7 one final time and record all values as
    the end state.

## Pass/fail criteria
- Pass: E5 == 1864000, E6 == 621333, E7 == 3 after the correction, all cells
  readable, no missing clicks.
- Fail: any cell unreadable after a click, a formula value wrong after
  correction, more than 2 click misses requiring re-entry.

## What to time
- Per-step wall time for each click/type/read (40+ actions).
- Total wall time from step 1 to step 26.
- Time spent re-reading cells after the formula fix (stale observation check).

## Errors designed to expose
- click miss: clicking the wrong cell, entering data into the wrong row.
- slow think: long pause between reading a value and typing the next formula.
- stale observation: reading E5 before the SUM recalculates, trusting an old
  screenshot value.
- wrong diagnosis: concluding the app is broken when a formula is simply wrong.
- fabrication: reporting a cell value the agent never actually read.

## Checker / expected end state
Checker script: `tests/realistic/fcc-k/check.mjs --fixture
fixtures/test-01-spreadsheet.html --test 01`.
Expected end state: E5=1864000, E6=621333, E7=3, E2=540000, E3=574000,
E4=750000.