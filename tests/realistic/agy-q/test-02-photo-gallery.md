# test-02-photo-gallery.md

## Test ID
test-02-photo-gallery

## Topic
Photo gallery: organize photos into albums, tag management, compound tag search, and metadata export.

## Context
Pham Tuan needs to organize and tag visual assets from the Tokyo 2026 tech summit.
The offline photo organizer (`fixtures/test-02-photo-gallery.html`) contains a catalog of 12 photo
cards with location metadata and tags. The user must create an album named "Tokyo Architecture",
filter the gallery for Tokyo landmarks, add three specific photos to the album, open a photo detail
view to edit its tags (adding tag "night" and removing incorrect tag "nature"), perform a tag search
for "night" across the entire library, add an additional matching photo to the album, switch to the
album view to verify its contents, and export the album manifest.

## Goal
Create album "Tokyo Architecture", populate it with photos 101, 104, 108, and 102. Update photo 108
tags to include "night" and exclude "nature". Verify compound tag search for "night" displays exactly
3 photos. Confirm album contents and click "Export Album JSON".

## Exact steps
1. Open fixture `tests/realistic/agy-q/fixtures/test-02-photo-gallery.html` in the browser via file URL.
2. Confirm the gallery loads 12 photo cards and sidebar shows default view "All Photos (12)".
3. In the sidebar, click the "New Album" button (id `btn-new-album`).
4. In the album name input field (id `input-album-name`), type `Tokyo Architecture`.
5. Click the "Create Album" button (id `btn-confirm-album`).
6. Verify "Tokyo Architecture" appears under Albums in the sidebar with an initial count of 0.
7. Click the location filter dropdown (id `select-location-filter`) and select `Tokyo`.
8. Observe that the gallery filters down to 6 Tokyo photos (IDs 101, 103, 104, 105, 107, 108).
9. Click the selection checkbox on photo card 101 (id `chk-photo-101`).
10. Click the selection checkbox on photo card 104 (id `chk-photo-104`).
11. Click the selection checkbox on photo card 108 (id `chk-photo-108`).
12. Verify the batch actions bar appears at the bottom displaying "3 photos selected".
13. In the batch actions bar, select "Tokyo Architecture" from the target album dropdown (id `select-batch-target-album`).
14. Click the "Add to Album" button (id `btn-batch-add-album`).
15. Verify the selection is cleared and the sidebar indicates "Tokyo Architecture (3)".
16. Reset the location filter dropdown (id `select-location-filter`) back to `All Locations`.
17. Click the card for photo 108 ("Roppongi Tower") to open its details modal (id `modal-photo-details`).
18. In the tags container, locate the badge chip for the erroneous tag "nature" and click its delete icon (id `btn-remove-tag-nature`).
19. In the new tag input field (id `input-new-tag`), type `night`.
20. Click the "Add Tag" button (id `btn-add-tag`).
21. Verify the tags list for photo 108 now shows: `architecture`, `skyline`, `night`.
22. Click the "Save & Close" button (id `btn-save-photo-details`).
23. In the top search bar (id `input-tag-search`), type `night` and press Enter.
24. Verify the search results view displays exactly 3 photos (IDs 102, 106, 108).
25. Click the selection checkbox on photo card 102 (id `chk-photo-102`).
26. In the batch actions bar, select "Tokyo Architecture" from the dropdown and click "Add to Album".
27. Clear the search bar (id `input-tag-search`) and click on "Tokyo Architecture" in the sidebar album list.
28. Verify the album view displays exactly 4 photos (IDs 101, 104, 108, 102).
29. Click the "Export Album JSON" button (id `btn-export-album`).
30. Read the export output modal (id `modal-export-output`) and confirm the status banner displays "Exported 4 photo records successfully".

## Pass/fail criteria
- Pass: Album "Tokyo Architecture" contains exactly photos [101, 104, 108, 102], photo 108 has tags ["architecture", "skyline", "night"] without "nature", search for "night" matches 3 photos, and exported JSON confirms 4 records.
- Fail: Any missing or incorrect photo in the album, tag "nature" remains on photo 108, tag "night" not saved, missed clicks on checkbox or badge delete buttons, or failure to export.

## What to time
- Per-step wall time for album creation, filtering, multi-item checkbox selection, and tag modal edits.
- Total wall time from step 1 to step 30.
- Latency between clearing search filters and verifying updated grid counts.

## Errors designed to expose
- click miss: Checkbox targets on thumbnail corners are 18x18 px; delete tag cross buttons are 14x14 px.
- slow think: Pausing during tag modal navigation and dropdown selections.
- stale observation: Attempting to search for "night" before clicking "Save & Close" on the modal.
- wrong diagnosis: Assuming photo 102 is missing when the location filter is still locked to Tokyo.
- fabrication: Reporting tag search result count without checking the actual rendered card count.

## Checker / expected end state
Checker command:
```bash
node tests/realistic/agy-q/check.mjs --fixture tests/realistic/agy-q/fixtures/test-02-photo-gallery.html --test 02
```
Expected end state:
- Album: "Tokyo Architecture"
- Photo IDs in album: [101, 104, 108, 102]
- Photo 108 tags: ["architecture", "skyline", "night"]
- Tag search "night" matches: [102, 106, 108]
- Export status: "Exported 4 photo records successfully"
