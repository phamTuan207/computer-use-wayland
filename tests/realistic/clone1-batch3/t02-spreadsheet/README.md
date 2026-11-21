# t02-spreadsheet: spreadsheet with formulas

## Context

A demo spreadsheet grid, columns A to D, rows 1 to 8. Cells hold
numbers, text, or formulas. Supported formulas: SUM(range),
AVERAGE(range), binary arithmetic between cells and numbers, and a
plain cell reference. A formula that cannot be evaluated shows
#ERR. Editing a source cell recomputes every dependent formula.

## Goal

Fill numbers and formulas, check computed values, edit source cells
and check the dependents update, and check error handling for bad
formulas, missing cells, and division by zero.

## Steps

1. Open the fixture page.
2. Fill A1=10, A2=20, A3=30.
3. Set C1 to `=SUM(A1:A3)`, check it shows 60.
4. Set C2 to `=AVERAGE(A1:A3)`, check it shows 20.
5. Fill B1=2, set D1 to `=A1*B1`, check it shows 20.
6. Change A1 to 40, check C1 is 90, C2 is 30, D1 is 80.
7. Set B2 to `=A1+A2`, check it shows 60.
8. Set D4 to `=C1/2`, check it shows 45 (chained formula).
9. Set D2 to `=FOO(1)`, check it shows #ERR.
10. Set D3 to `=A9`, check it shows #ERR (outside the grid).
11. Fill A5 with the text `hello`.
12. Set C3 to `=SUM(A1:A5)`, check it shows 90 (text ignored).
13. Fill A4=5, check C3 becomes 95 and C1 stays 90.
14. Clear B1, check D1 becomes 0.
15. Fill A6=2.5, set C4 to `=A6*2`, check it shows 5.
16. Set D5 to `=A3/A2`, check it shows 1.5.
17. Set D6 to `=A3/0`, check it shows #ERR.
18. Change A3 to 10, check C1 becomes 70 and D5 becomes 0.5.
19. Check the status line reads `Recalculated.`

## Pass conditions

- Every computed value above matches exactly.
- Editing a source cell updates all dependent formulas.
- Bad formulas, out-of-grid references, and division by zero show #ERR.
- Text cells are ignored by SUM.

## Fail conditions

- Any computed value differs from the expected value.
- A dependent formula does not update after an edit.
- An error case shows a number instead of #ERR.

## Notes

All calculation happens in the page. No data leaves the machine.
The browser run is Playwright Chromium; the same flow on Firefox or
Zen is UNVERIFIED.
