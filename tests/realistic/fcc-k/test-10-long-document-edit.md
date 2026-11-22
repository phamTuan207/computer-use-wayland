# test-10-long-document-edit.md

## Test ID
test-10-long-document-edit

## Topic
Long document edit: find/replace across sections, add table, export.

## Context
the owner edits a long offline document (a report fixture with multiple
sections). The agent must replace a term across all sections, insert a table
with fixed headers and rows, update the document's table of contents count, and
export the document to a new filename, then verify the export contains the
edits. This is a long-document editing task with find/replace, structured
insertion, and export.

## Goal
Replace `old vendor` with `new vendor` across all sections, add a 3-column,
2-row table under the Summary section, update the TOC count, export to a new
filename, and verify the export contains all edits.

## Exact steps
1. Open the document fixture `fixtures/test-10-document.html` in the local
   browser (offline, file:// URL).
2. Verify the document is loaded with a visible table of contents and at least
   3 sections.
3. Open Find/Replace.
4. Search for the term `old vendor` and note the number of matches.
5. Replace all `old vendor` with `new vendor`.
6. Close Find/Replace and confirm no `old vendor` remains (search again).
7. Scroll to the Summary section.
8. Insert a table with 3 columns and 2 rows.
9. Fill the table header row: Column A, Column B, Column C.
10. Fill the table body row 1 with values.
11. Fill the table body row 2 with values.
12. Verify the table of contents count now shows Tables: 1 (the fixture
    updates it when the table is added).
13. Click Save (in-document).
14. Export the document to `report-export.md`.
15. Read the export view (the exported file rendered on the page) and confirm
    it contains `new vendor` and the table with Column A/B/C headers and the
    two body rows.
16. Confirm the exported file contains no `old vendor` text.
17. Confirm the export filename is exactly `report-export.md`.

## Pass/fail criteria
- Pass: all `old vendor` replaced with `new vendor`, table added with 3
    columns 2 rows and correct headers/values, TOC count updated, export to
    report-export.md contains all edits and no old term.
- Fail: any `old vendor` remains, table missing or wrong shape, TOC not updated,
  export missing or wrong filename, export missing edits.

## What to time
- Per-step wall time for each find/replace/insert/fill/export (17 steps).
- Total wall time from step 1 to step 17.
- Time to scan all sections for the term (find/replace latency).
- Time re-reading the export after download (stale observation check).

## Errors designed to expose
- click miss: clicking the wrong Find/Replace control, the wrong table cell, or
  the wrong export option.
- slow think: long pause between inserting a table and filling its cells.
- stale observation: reading the export before the download completes, seeing an
  old version.
- wrong diagnosis: concluding replace failed because the search still finds
  `new vendor` (substring match).
- fabrication: claiming the export contains the table without opening the
  exported file.

## Checker / expected end state
Checker script: `tests/realistic/fcc-k/check.mjs --fixture
fixtures/test-10-document.html --test 10`.
Expected end state: document has zero `old vendor` occurrences, a 3-column
2-row table with headers Column A/B/C under Summary, TOC count updated, and an
export named report-export.md that contains `new vendor` and the full table and
no `old vendor`.