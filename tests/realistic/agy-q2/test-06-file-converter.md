# test-06-file-converter.md

## Test ID
test-06-file-converter

## Topic
Universal file converter UI: file selection, target format configuration, compression and metadata settings, queue management, invalid file error handling and removal, batch conversion execution, output downloads, and session persistence.

## Context
the owner needs to convert multi-format assets for a web application deployment.
The workstation runs an offline browser converter tool (fixtures/test-06-file-converter.html).
The user must select "sample-data.csv" and convert to JSON format, select "photo.png" and convert to WEBP format, configure compression quality to "High", enable metadata preservation, handle an accidentally queued corrupted binary file ("corrupted.bin") by removing it from the queue, execute the batch conversion, download both converted outputs, and save the session.

## Timing
- Baseline start time: 2026-11-21 17:10:00 Asia/Ho_Chi_Minh
- Expected duration: 160 seconds elapsed
- Maximum allowable latency: 270 seconds elapsed

## Goal
Queue sample-data.csv to JSON and photo.png to WEBP with High compression and metadata preservation, remove corrupted.bin from queue, convert both files, download both outputs, and verify saved session banner.

## Exact steps
1. Open fixture tests/realistic/agy-q2/fixtures/test-06-file-converter.html in the browser.
2. Verify queue indicator (id "queue-count") displays "0".
3. Select "sample-data.csv" in source file dropdown (id "select-source-file").
4. Select "JSON" in target format dropdown (id "select-target-format").
5. Select "High" in compression quality dropdown (id "select-compression").
6. Click the checkbox "Preserve document metadata and tags" (id "check-preserve-meta") so it becomes checked.
7. Click "+ Add to Queue" button (id "btn-add-queue").
8. Verify queue table has 1 row with target format "JSON".
9. Select "photo.png" in source file dropdown (id "select-source-file").
10. Select "WEBP" in target format dropdown (id "select-target-format").
11. Click "+ Add to Queue" button (id "btn-add-queue").
12. Verify queue table has 2 rows.
13. Mistaken entry: select "corrupted.bin" in source file dropdown (id "select-source-file").
14. Click "+ Add to Queue" button (id "btn-add-queue").
15. Verify queue table has 3 rows and corrupted row status badge (id "status-corrupted-bin") displays "Invalid format".
16. Click "Remove" button on the corrupted file row (id "btn-remove-queue-corrupted-bin").
17. Verify queue table now contains exactly 2 valid items.
18. Click "Convert All Files" button (id "btn-convert-all").
19. Verify queue status indicator (id "queue-status-text") displays "Conversion complete".
20. Verify completed downloads list (id "output-count") displays "2".
21. Find "sample-data.json" in output list and click its "Download" button (id "btn-download-sample-data-csv").
22. Verify badge for sample-data (id "badge-download-sample-data-csv") displays "Downloaded".
23. Find "photo.webp" in output list and click its "Download" button (id "btn-download-photo-png").
24. Verify badge for photo (id "badge-download-photo-png") displays "Downloaded".
25. Click "Save Conversion Session" button (id "btn-save-session").
26. Read status banner (id "converter-status-banner") and confirm it displays "Batch complete: 2 files converted and 2 downloaded".

## Pass/fail criteria
- Pass: Exactly 2 files converted (sample-data.json, photo.webp), corrupted.bin removed, both files downloaded, compression is High, preserve metadata is checked, and status banner confirms batch completion.
- Fail: corrupted.bin still in queue, missing converted files, undownloaded files, wrong compression setting, or unverified banner.

## Errors designed to expose
- click miss: Small Remove buttons in table rows or Download buttons in output cards.
- unhandled validation: Attempting to convert while invalid corrupted file is still in the queue.
- option oversight: Forgetting to toggle the preserve metadata checkbox or leaving compression at Normal.
- premature completion: Saving session before downloading both converted files.
- fabrication: Asserting completion without verifying status badges.

## Checker / expected end state
```bash
node tests/realistic/agy-q2/check.mjs --fixture tests/realistic/agy-q2/fixtures/test-06-file-converter.html --test 06
```
