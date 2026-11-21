# test-05-file-search.md

## Test ID
test-05-file-search

## Topic
File search explorer: filename vs full-text content search, file extension filtering, code preview inspection, file renaming, editor launch simulation, and file permissions.

## Context
Pham Tuan needs to audit and update configuration paths in an offline multi-language codebase
explorer (`fixtures/test-05-file-search.html`). The simulated file repository contains 15 files
across `/src`, `/config`, `/docs`, and `/scripts`. The user must execute a filename search for
"compositor", preview the configuration, switch to full-text content search for the symbol
`socket_path`, apply an extension filter to isolate the target JSON file, rename `compositor.json`
to `wayland-compositor.json`, verify the rename across file search indices, open the file into the
active editor context, mark it read-only, and export the file search audit trail.

## Goal
Search by filename "compositor", switch to content search for "socket_path", filter by `.json`,
rename `config/compositor.json` to `config/wayland-compositor.json`, open it in editor, mark it
read-only, and verify the audit export reports 1 rename and 1 active file in editor.

## Exact steps
1. Open fixture `tests/realistic/agy-q/fixtures/test-05-file-search.html` in the browser via file URL.
2. Confirm the repository tree reports 15 files indexed.
3. Verify the default search mode radio is selected as "Filename" (id `radio-search-name`).
4. In the search query field (id `input-file-search`), type `compositor`.
5. Observe the search results table updates to show 2 files:
   - `src/compositor.rs` (id `row-file-1`)
   - `config/compositor.json` (id `row-file-6`)
6. Click the table row for `config/compositor.json` (id `row-file-6`).
7. Observe the right-side preview pane renders the JSON contents of the file with line numbers.
8. Switch search mode by clicking the "Search by Content" radio option (id `radio-search-content`).
9. Clear the search field and type `socket_path`.
10. Confirm the results table populates with 3 files containing `socket_path` in their text:
    - `src/server.rs` (id `row-file-2`)
    - `config/compositor.json` (id `row-file-6`)
    - `scripts/launch.sh` (id `row-file-11`)
11. Click the file extension filter dropdown (id `select-ext-filter`) and select `.json`.
12. Confirm the results table narrows to display exactly 1 result: `config/compositor.json`.
13. In the preview header toolbar, click the "Rename File" button (id `btn-rename-file`).
14. In the rename modal input field (id `input-new-filename`), type `wayland-compositor.json`.
15. Click the "Confirm Rename" button (id `btn-confirm-rename`).
16. Verify the status banner displays: "File config/compositor.json renamed to config/wayland-compositor.json".
17. In the extension filter dropdown (id `select-ext-filter`), reset the value to `All Extensions`.
18. Click the "Search by Filename" radio button (id `radio-search-name`).
19. In the search input field (id `input-file-search`), type `wayland-compositor`.
20. Confirm exactly 1 result appears in the results table: `config/wayland-compositor.json`.
21. Click row `config/wayland-compositor.json` to ensure it is selected.
22. In the preview pane toolbar, click the "Open in Editor" button (id `btn-open-file`).
23. Verify the editor status banner (id `status-open-indicator`) displays: "Active in editor: config/wayland-compositor.json".
24. Click the row selection checkbox on `config/wayland-compositor.json` (id `chk-file-6`).
25. In the batch action dropdown (id `select-batch-action`), choose `Mark Read-Only`.
26. Click the "Apply Action" button (id `btn-apply-batch`).
27. Confirm the file preview attributes badge displays `[RO]` (Read-Only).
28. Click the "Export Search Audit" button (id `btn-export-audit`).
29. Inspect the audit export dialog (id `modal-export-audit`) and confirm the summary line displays: "Renamed: 1, Active Editor: config/wayland-compositor.json, Read-Only Files: 1".
30. Click the "Done" button (id `btn-close-audit-modal`).

## Pass/fail criteria
- Pass: Filename search for "compositor" returns 2 results, content search for "socket_path" returns 3 results, extension filter isolates JSON file, file renamed to `wayland-compositor.json`, opened in editor, marked read-only, and audit export confirms all counts.
- Fail: Content search fails, extension filter does not isolate, rename does not persist in repository index, read-only attribute missing, or audit export mismatch.

## What to time
- Per-step wall time for radio selection, search query entries, dropdown filtering, modal inputs, and batch actions.
- Total wall time from step 1 to step 30.
- Latency between clicking "Confirm Rename" and verifying updated filename in the index.

## Errors designed to expose
- click miss: Radio buttons (16x16 px), row checkboxes, and compact action buttons in the preview toolbar.
- slow think: Analyzing content search snippets or waiting before selecting the extension filter.
- stale observation: Attempting to search for the old filename `compositor.json` after rename occurred.
- wrong diagnosis: Concluding file was deleted when extension filter excluded it.
- fabrication: Reporting content search match count without reading table rows.

## Checker / expected end state
Checker command:
```bash
node tests/realistic/agy-q/check.mjs --fixture tests/realistic/agy-q/fixtures/test-05-file-search.html --test 05
```
Expected end state:
- Renamed file: `config/wayland-compositor.json`
- Content search "socket_path" total: 3
- Extension filter `.json` total: 1
- Active editor file: `config/wayland-compositor.json`
- Read-only flag: true
- Audit exported: true
