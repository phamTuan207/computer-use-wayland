# test-08-spreadsheet-pivot.md

## Test ID
test-08-spreadsheet-pivot

## Topic
Spreadsheet pivot table creation, category grouping, sum aggregation, region filtering, and refresh after a source edit.

## Context
A data analyst builds a pivot table in Grid Ledger from six rows of regional sales data. They group by Category, catch an accidental Count aggregation, switch to Sum, filter to South, edit one source value, and refresh the pivot. The fixture is tests/realistic/codex-y5/fixtures/test-08-spreadsheet-pivot.html.

## Timing
- Baseline start time: 2026-11-21 18:21:00 Asia/Ho_Chi_Minh
- Expected duration: 240 seconds elapsed
- Maximum allowable latency: 360 seconds elapsed

## Goal
Show South category totals after refresh: Hardware 900, Software 1400, and Grand total 2300, grouped by Category and summarized by Sum.

## Exact steps
1. Open tests/realistic/codex-y5/fixtures/test-08-spreadsheet-pivot.html in the browser.
2. Verify #source-row-count text is "6", #pivot-row-count text is "0", #pivot-status text is "No pivot table", #pivot-hardware-total text is "-", and #pivot-grand-total text is "-".
3. Click button #btn-create-pivot; #pivot-status must become "Pivot created from 6 rows".
4. Verify #pivot-status text is "Pivot created from 6 rows", #pivot-group-field text is "None", and #pivot-value-field text is "None".
5. Select value "Category" in #pivot-group-select; its selected value must be "Category".
6. Verify #pivot-group-select value is "Category".
7. Select value "Amount" in #pivot-value-select; its selected value must be "Amount".
8. Verify #pivot-value-select value is "Amount".
9. Mistake: select value "Count" in #pivot-aggregation-select and apply the wrong aggregation; its selected value must be "Count".
10. Click button #btn-refresh-pivot; #pivot-status must become "Pivot table ready".
11. Verify #pivot-hardware-total text is "3", #pivot-software-total text is "3", and #pivot-grand-total text is "6".
12. Recovery: select value "Sum" in #pivot-aggregation-select; its selected value must be "Sum".
13. Click button #btn-refresh-pivot; #pivot-grand-total must become "5200".
14. Verify #pivot-group-field text is "Category", #pivot-value-field text is "Amount", #pivot-aggregation text is "Sum", #pivot-hardware-total text is "2300", #pivot-software-total text is "2900", and #pivot-grand-total text is "5200".
15. Select value "South" in #pivot-filter-select; its selected value must be "South".
16. Click button #btn-refresh-pivot; #pivot-filter-region must become "South".
17. Verify #pivot-hardware-total text is "600", #pivot-software-total text is "1400", and #pivot-grand-total text is "2000".
18. Replace #source-south-hardware value with "900"; its value must be "900".
19. Verify #source-south-hardware value is "900" while #pivot-hardware-total text remains "600" and #pivot-grand-total text remains "2000" before refresh.
20. Click button #btn-refresh-pivot; #pivot-hardware-total must become "900".
21. Verify #pivot-group-field text is "Category", #pivot-value-field text is "Amount", #pivot-aggregation text is "Sum", #pivot-filter-region text is "South", #pivot-row-count text is "2", #pivot-hardware-total text is "900", #pivot-software-total text is "1400", #pivot-grand-total text is "2300", #pivot-refresh-status text is "Pivot refreshed from 6 rows", and #source-south-hardware value is "900".

## Pass/fail criteria
- Pass: The refreshed pivot groups by Category, sums Amount, filters to South, and reports 900 + 1400 = 2300 after the source edit.
- Fail: Count is left as the aggregation, the old South hardware value remains after refresh, the filter is not South, or any total is arithmetically incorrect.

## Errors designed to expose
- click miss: Pivot selectors and refresh controls share a compact settings panel.
- slow think: The table must be refreshed once for the aggregation, again for the filter, and again after the edit.
- stale observation: The pivot intentionally remains at 600 until Refresh is clicked after the source edit.
- wrong diagnosis: Count produces plausible row counts but is the wrong measure for the requested totals.
- fabrication: The six source values sum to 5200 overall and the filtered updated values sum to 2300.

## Checker / expected end state
```bash
node tests/realistic/codex-y5/check.mjs --fixture tests/realistic/codex-y5/fixtures/test-08-spreadsheet-pivot.html --test 08
```
