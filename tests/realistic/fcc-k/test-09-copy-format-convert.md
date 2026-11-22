# test-09-copy-format-convert.md

## Test ID
test-09-copy-format-convert

## Topic
Copy data between app A and app B with format conversion.

## Context
the owner has a source table in App A (a spreadsheet-like fixture) and needs the
same data in App B (a document-style fixture) in a different format: App A holds
rows of comma-separated values, App B expects a numbered list of `key: value`
lines. The agent reads App A data, converts the format (strip headers, reorder
fields, add numbering), types it into App B, and verifies the converted output
matches a canonical expected form. This tests format transformation between two
different UIs.

## Goal
Read a 4-row source table from App A, convert each row to `N. key: value` format
in App B, and confirm the converted list exactly matches the expected canonical
form.

## Exact steps
1. Open the conversion fixture `fixtures/test-09-convert.html` in the local
   browser (offline, file:// URL).
2. Verify App A (source) and App B (target) are both visible side by side.
3. Read the App A header row (note column names and order).
4. Read row 1 of App A (all cells, in order).
5. Read row 2 of App A (all cells, in order).
6. Read row 3 of App A (all cells, in order).
7. Read row 4 of App A (all cells, in order).
8. Determine the conversion rule from the header order (e.g., field order maps
   to the numbered key lines).
9. In App B, type converted line 1: `1. key: value`.
10. Type converted line 2: `2. key: value`.
11. Type converted line 3: `3. key: value`.
12. Type converted line 4: `4. key: value`.
13. Click Convert / Apply in App B.
14. Read the converted output area in App B.
15. Compare each line against the canonical expected form (visible in the
    fixture as a reference block).
16. Fix any mismatched line and re-apply if needed.
17. Confirm all 4 lines match the reference and no extra lines exist.
18. Read back the final converted list as the end state.

## Pass/fail criteria
- Pass: 4 rows converted to 4 numbered `key: value` lines, each matching the
  canonical reference, no extra or missing lines, applied result visible.
- Fail: a line mismatched, wrong field order, missing line, extra line, number
  format wrong, conversion not applied.

## What to time
- Per-step wall time for each read/type/click (18 steps).
- Total wall time from step 1 to step 18.
- Time spent reading App A and converting mentally (conversion latency).
- Time re-reading converted output after apply (stale observation check).

## Errors designed to expose
- click miss: clicking the wrong app pane, the wrong apply button.
- slow think: long pause between reading a row and typing the converted line.
- stale observation: reading the converted output before Convert completes.
- wrong diagnosis: concluding conversion failed because the reference differs
  only in whitespace.
- fabrication: claiming the output matches the reference without comparing each
  line.

## Checker / expected end state
Checker script: `tests/realistic/fcc-k/check.mjs --fixture
fixtures/test-09-convert.html --test 09`.
Expected end state: App B converted list has exactly 4 numbered `key: value`
lines matching the reference block line for line, applied state present.