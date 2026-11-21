# Test 10, Data dashboard

## Goal

Prove an agent can audit an analytics dashboard in a real browser
against ground truth it computes itself: read the raw dataset out
of the page, recompute the KPI totals, and verify the rendered
cards, the table, both sort directions, a channel filter with
recomputed KPIs, a text search, a combined filter plus sort, a
date range that shrinks the view, and a CSV export whose decoded
content must match the current view row for row. The fixture is
fully offline, one HTML file with an inline dataset of 14 daily
rows across 4 channels, also exposed as JSON in a script tag with
id dataset-json so the checker never trusts the rendered page.

Fixture: fixtures/test10_data_dashboard.html
Test: tests/test10_data_dashboard.py

## Steps

1. Start the browser and load the fixture.
2. Read the dataset JSON from the page. It must hold at least 12
   rows and at least 3 distinct channels.
3. Read the 4 KPI cards and verify each one against the dataset
   sums recomputed in the test: total revenue, orders, visitors,
   and conversion, orders divided by visitors as a percent with
   2 decimals.
4. Read the table. Its row count equals the dataset size, the row
   count label reads Showing 14 of 14 rows, and the first row is
   the first dataset row.
5. Click the revenue header once. The indicator reads (desc), the
   first row revenue is the dataset maximum, and the revenue
   column is monotonic descending.
6. Click the revenue header again. The indicator reads (asc), the
   first row revenue is the dataset minimum, and the column is
   monotonic ascending.
7. Filter the channel dropdown to Paid. Every visible row is
   Paid, the row count equals the recomputed Paid count, and the
   revenue, orders, and conversion cards match the values
   recomputed in the test from the Paid rows only.
8. Type the search term 2026-11-1 with the Paid filter still on.
   The visible rows are exactly the recomputed matches, all Paid
   and all with a date containing the term.
9. Clear the search, then click the visitors header. With the
   Paid filter still active, all rows stay Paid, the count is the
   full Paid count, and visitors are monotonic descending.
10. Set the channel filter back to all and the date range to
    Last 7 entries. The range keeps the last 7 dataset rows by
    row count, so the table shrinks to exactly those 7 dates and
    the label reads Showing 7 of 14 rows.
11. Read the export CSV link. Its href is a CSV data URI, the
    decoded header is date,channel,visitors,orders,revenue, the
    decoded row count equals the current view, and the first data
    row equals the current first table row.
12. Clear all filters, channel all, range all, search empty. The
    full row count is restored, the KPI cards equal the dataset
    totals again, and the row count label is back to full.

## Expected results

- Every KPI card always equals the totals recomputed in the test
  from the dataset JSON, for the full dataset and for the Paid
  subset.
- Sorting is verified against the dataset maximum, minimum, and
  full column monotonicity in both directions, with the sort
  indicator text matching the direction.
- Combined filters behave as the intersection of their parts, and
  the export CSV is a faithful copy of the visible, sorted view.
- Clearing the filters restores the exact initial totals and row
  count.
- The test prints RESULT with ok true.

## Timing

Verified run on the clone2 machine, headless Firefox, real
browser through Selenium:

- Date: 2026-11-21
- Wall clock: 2026-11-21T11:30:23Z to 2026-11-21T11:30:52Z
- Total elapsed: 29.2974 s
- Steps: 23, including browser start, all ok
- Checks: 35, all ok
- RESULT: ok true
- KPI values verified, full dataset: revenue 51292, orders 980,
  visitors 24600, conversion 3.98 percent. Paid subset: revenue
  25960, orders 472, visitors 10800, conversion 4.37 percent.
