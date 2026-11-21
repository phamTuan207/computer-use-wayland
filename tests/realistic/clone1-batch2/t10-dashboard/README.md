# t10-dashboard: filter, sort, export sales data

## Context

A sales dashboard with 12 orders, KPI cards (revenue, orders, average),
filters for status, category, date range, and search, a sortable table
with pagination and row selection, a canvas chart by category, and a CSV
export of the filtered rows.

## Goal

Prove the KPIs match the filters, sort and paginate correctly, select
rows, export a correct CSV, and handle an empty result.

## Steps (40)

1. Open the fixture.
2. Check the starting KPIs: $610.39, 12 orders, $50.87 average.
3. Check page 1 shows 5 rows.
4. Check the first row is A1001.
5. Filter status paid.
6. Check paid KPIs: $437.92, 8 orders, $54.74 average.
7. Filter category electronics too.
8. Check paid electronics: $369.96, 4 orders.
9. Clear the category filter.
10. Search for lamp.
11. Check paid lamp: 2 orders, $49.98.
12. Clear the search.
13. Set the date range Nov 5 to Nov 10.
14. Check the range: 3 orders, $187.97.
15. Reset filters.
16. Check the KPIs are back to the full set.
17. Sort by amount ascending.
18. Check the cheapest first is $7.99.
19. Sort by amount descending.
20. Check the priciest first is $129.99.
21. Reset to date order.
22. Go to page 2.
23. Check page 2 starts with A1006.
24. Go back to page 1.
25. Check page 1 starts with A1001 again.
26. Select two rows.
27. Check the selected count is 2.
28. Select all on the page.
29. Check the selected count is 5.
30. Deselect all on the page.
31. Check the selected count is 0.
32. Filter paid for export.
33. Export the CSV.
34. Check the CSV has the header, 8 paid rows, and the Monitor row.
35. Check the chart totals for the paid filter.
36. Filter to an empty result.
37. Check the empty message is shown.
38. Check 0 orders for the empty filter.
39. Reset filters.
40. Check 12 orders are back.

## Pass

All 39 steps run, every KPI matches hand-computed figures, sorting and
pagination land on the right rows, selection counts are right, the CSV
has exactly the filtered rows, and the empty state shows.

## Fail

Any step above fails, a KPI is off, a sort or page is wrong, the CSV
has the wrong rows, or the empty state does not show.
