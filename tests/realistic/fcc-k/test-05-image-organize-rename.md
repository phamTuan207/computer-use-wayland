# test-05-image-organize-rename.md

## Test ID
test-05-image-organize-rename

## Topic
Image download + organize + rename batch.

## Context
Pham Tuan downloaded a batch of images into a local downloads folder (fixture
simulates a file manager view of downloaded images with generic names like
`img_01.jpg`, `screenshot.png`, `photo from web.jpg`). The agent must move the
images into an `Organized` subfolder, rename each to a descriptive scheme
(`trip-01.jpg`, `trip-02.jpg`, ...), create a text index listing each original
name mapped to its new name, and confirm every file is present and correctly
named. This is a batch file-organization task across many files.

## Goal
Move 8 images into an Organized subfolder, rename them trip-01..trip-08 with
correct extensions, write an index file mapping original->new names, and verify
all 8 files exist with correct names and the index is complete.

## Exact steps
1. Open the file manager fixture `fixtures/test-05-image.html` in the local
   browser (offline, file:// URL).
2. Verify the downloads view lists exactly 8 image files with original names.
3. Create the `Organized` subfolder (click New Folder, type `Organized`).
4. Select image 1 and move it into Organized.
5. Rename image 1 inside Organized to `trip-01.jpg`.
6. Select image 2 and move it into Organized.
7. Rename image 2 inside Organized to `trip-02.jpg`.
8. Select image 3 and move it into Organized.
9. Rename image 3 inside Organized to `trip-03.png`.
10. Select image 4 and move it into Organized.
11. Rename image 4 inside Organized to `trip-04.jpg`.
12. Select image 5 and move it into Organized.
13. Rename image 5 inside Organized to `trip-05.jpg`.
14. Select image 6 and move it into Organized.
15. Rename image 6 inside Organized to `trip-06.png`.
16. Select image 7 and move it into Organized.
17. Rename image 7 inside Organized to `trip-07.jpg`.
18. Select image 8 and move it into Organized.
19. Rename image 8 inside Organized to `trip-08.jpg`.
20. Open the Organized folder and list all files; confirm exactly 8 files named
    trip-01..trip-08 with correct extensions.
21. Open (or create) `index.txt` and write one line per file mapping original
    name to new name (8 lines).
22. Save index.txt.
23. Re-open index.txt and confirm all 8 mappings are present and readable.
24. Confirm the original downloads folder now lists 0 image files (all moved).

## Pass/fail criteria
- Pass: Organized contains exactly 8 files trip-01..trip-08 with correct
  extensions, index.txt has 8 correct mappings, downloads folder empty of
  images.
- Fail: a file misnamed, wrong extension, missing file, index mapping wrong or
  incomplete, image left in downloads.

## What to time
- Per-step wall time for each move/rename/type (24 steps).
- Total wall time from step 1 to step 24.
- Time to list and verify the Organized folder (verification latency).
- Time re-reading index.txt after save (stale observation check).

## Errors designed to expose
- click miss: moving the wrong image, renaming the wrong file, clicking the
  wrong row.
- slow think: long pause between moving a file and typing its new name.
- stale observation: reading the Organized folder before the move completes,
  seeing a stale file list.
- wrong diagnosis: concluding a rename failed when the file list just needs a
  refresh.
- fabrication: claiming a file was renamed or index written without verifying.

## Checker / expected end state
Checker script: `tests/realistic/fcc-k/check.mjs --fixture
fixtures/test-05-image.html --test 05`.
Expected end state: Organized folder has exactly trip-01.jpg..trip-08.jpg/png
with correct extensions, index.txt has 8 original->new mappings, downloads
folder has 0 images.