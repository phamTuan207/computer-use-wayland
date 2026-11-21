# test-05-spreadsheet-chart.md

## Test ID
test-05-spreadsheet-chart

## Topic
Spreadsheet formulas, data validation mistake correction, automatic recalculation, and bar chart rendering.

## Context
A financial analyst needs to compile quarterly sales figures and prepare an executive summary chart.
The workstation runs a local browser-based spreadsheet application (fixtures/test-05-spreadsheet-chart.html).
The user must enter sales labels and figures for Jan, Feb, and Mar, enter an initial erroneous value of 9800
for March sales, apply a =SUM(B2:B4) formula to calculate Total sales, apply an =AVERAGE(B2:B4) formula for Average sales,
correct the March sales value to 1800, trigger sheet recalculation, verify that Total updates to 4500 and Average
updates to 1500.00, insert a bar chart, customize the chart title to "Q1 Regional Sales", and save the sheet.

## Timing
- Baseline start time: 2026-11-21 17:00:00 Asia/Ho_Chi_Minh
- Expected duration: 180 seconds elapsed
- Maximum allowable latency: 300 seconds elapsed

## Goal
Enter sales data, apply SUM and AVERAGE formulas, correct March sales from 9800 to 1800, recalculate sheet
to achieve Total 4500 and Average 1500.00, insert bar chart titled "Q1 Regional Sales", and save sheet state.

## Exact steps
1. Open fixture tests/realistic/agy-y2/fixtures/test-05-spreadsheet-chart.html in the browser.
2. Verify element #active-sheet-name text is "Sales Forecast".
3. Click input #cell-input-a1 and type "Month".
4. Click input #cell-input-b1 and type "Sales".
5. Click input #cell-input-a2 and type "Jan".
6. Click input #cell-input-b2 and type "1200".
7. Click input #cell-input-a3 and type "Feb".
8. Click input #cell-input-b3 and type "1500".
9. Click input #cell-input-a4 and type "Mar".
10. Click input #cell-input-b4 and simulate data entry mistake by typing "9800".
11. Verify element #cell-value-b4 text is "9800".
12. Click input #cell-input-a5 and type "Total".
13. Click input #cell-input-b5 to select cell B5.
14. Click input #formula-bar-input and type "=SUM(B2:B4)".
15. Click button #btn-commit-formula to evaluate the SUM formula.
16. Verify element #cell-value-b5 text is "12500".
17. Click input #cell-input-a6 and type "Average".
18. Click input #cell-input-b6 to select cell B6.
19. Click input #formula-bar-input and type "=AVERAGE(B2:B4)".
20. Click button #btn-commit-formula to evaluate the AVERAGE formula.
21. Verify element #cell-value-b6 text is "4166.67".
22. Recover from mistake: click input #cell-input-b4, clear existing text, and type "1800".
23. Click button #btn-recalculate-sheet to update all formula cells.
24. Verify element #cell-value-b5 text updates to "4500".
25. Verify element #cell-value-b6 text updates to "1500.00".
26. Click button #btn-insert-chart-modal to open chart generator dialog.
27. Verify modal #chart-modal has class "active".
28. Select option "Bar" in select #select-chart-type.
29. Click button #btn-render-chart to insert chart onto sheet.
30. Verify element #chart-wrapper contains SVG element #sales-bar-svg.
31. Click input #input-chart-title, clear existing text, and type "Q1 Regional Sales".
32. Click button #btn-apply-chart-title to update chart title.
33. Verify element #chart-title-text text is "Q1 Regional Sales".
34. Click button #btn-save-sheet-state to persist worksheet state.
35. Verify element #sheet-status-toast text contains "Sheet saved: Total=4500, Average=1500.00, Chart=Q1 Regional Sales".

## Pass/fail criteria
- Pass: Monthly figures populated, March figure fixed to 1800, Total cell displays 4500, Average cell displays 1500.00, bar chart rendered with title "Q1 Regional Sales", and sheet state saved.
- Fail: March typo retained (Total 12500), formula calculation missing, bar chart not rendered, chart title incorrect, or save toast missing.

## Errors designed to expose
- click miss: Cell inputs in dense tabular grid require accurate targeting.
- slow think: Delays between formula bar entry and sheet recalculation.
- stale observation: Reading formula cell values before triggering recalculation.
- wrong diagnosis: Overwriting calculated cells with raw values instead of using formulas.
- fabrication: Asserting formula outputs without reading cell text content.

## Checker / expected end state
```bash
node tests/realistic/agy-y2/check.mjs --fixture tests/realistic/agy-y2/fixtures/test-05-spreadsheet-chart.html --test 05
```
