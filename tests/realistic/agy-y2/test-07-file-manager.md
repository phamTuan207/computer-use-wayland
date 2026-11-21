# test-07-file-manager.md

## Test ID
test-07-file-manager

## Topic
File manager bulk file management: selection, bulk renaming with counter pattern, moving files to folder, accidental deletion and trash restoration, folder creation, and inventory validation.

## Context
A data administrator needs to organize incoming raw asset files inside a web-based file management portal (fixtures/test-07-file-manager.html).
The user must select 5 target photo files, bulk rename them using the pattern "photo-2026-##", move 3 of the renamed files into the "Archive" folder,
accidentally delete 1 file, recover by opening the Trash view and restoring the deleted file, create a new directory named "Processed",
and verify directory file counts and final filenames in the DOM.

## Timing
- Baseline start time: 2026-11-21 17:00:00 Asia/Ho_Chi_Minh
- Expected duration: 180 seconds elapsed
- Maximum allowable latency: 300 seconds elapsed

## Goal
Select 5 files, bulk rename to "photo-2026-##", move 3 to "Archive", delete 1 file and restore from trash, create folder "Processed", and verify file counts and names.

## Exact steps
1. Open fixture tests/realistic/agy-y2/fixtures/test-07-file-manager.html in the browser.
2. Verify element #total-files-count text is "8" and #selected-files-count text is "0".
3. Click checkbox #checkbox-file-img1 to select first file.
4. Click checkbox #checkbox-file-img2 to select second file.
5. Click checkbox #checkbox-file-img3 to select third file.
6. Click checkbox #checkbox-file-img4 to select fourth file.
7. Click checkbox #checkbox-file-img5 to select fifth file.
8. Verify element #selected-files-count text is "5".
9. Click button #btn-open-bulk-rename to open bulk rename modal.
10. Verify element #bulk-rename-modal has class "active".
11. Click input #input-rename-pattern and type "photo-2026-##".
12. Click button #btn-apply-bulk-rename to execute pattern renaming.
13. Verify element #file-name-img1 text is "photo-2026-01.jpg".
14. Verify element #file-name-img5 text is "photo-2026-05.jpg".
15. Click checkbox #checkbox-file-img1 to select "photo-2026-01.jpg".
16. Click checkbox #checkbox-file-img2 to select "photo-2026-02.jpg".
17. Click checkbox #checkbox-file-img3 to select "photo-2026-03.jpg".
18. Click button #btn-open-move-dialog to open folder move dialog.
19. Verify element #move-modal has class "active".
20. Click option #move-target-archive to pick folder "Archive".
21. Click button #btn-confirm-move to move files into Archive.
22. Verify element #folder-count-archive text contains "3 files".
23. Simulate mistake: click button #btn-delete-file-img4 to delete file "photo-2026-04.jpg".
24. Verify element #file-row-img4 has class "hidden" and #trash-counter text is "1".
25. Recovery: click folder link #nav-folder-trash to view trash items.
26. Verify element #trash-table is visible and contains element #trash-row-img4.
27. Click button #btn-restore-file-img4 to restore the deleted file.
28. Verify element #trash-counter text is "0".
29. Click folder link #nav-folder-root to return to main files view.
30. Click button #btn-new-folder to open folder creation modal.
31. Verify element #new-folder-modal has class "active".
32. Click input #input-new-folder-name and type "Processed".
33. Click button #btn-confirm-create-folder to create folder.
34. Click button #btn-generate-inventory-report to finalize operation summary.
35. Verify element #inventory-summary-toast text contains "Root: 5 files, Archive: 3 files, Trash: 0 files, Folder Processed created".

## Pass/fail criteria
- Pass: 5 files renamed with pattern "photo-2026-##", 3 files moved to "Archive", 1 deleted file restored from Trash, new folder "Processed" created, and summary toast verifies correct file counts.
- Fail: Pattern rename incomplete, files not moved into Archive, Trash restore not performed, folder Processed missing, or summary toast not activated.

## Errors designed to expose
- click miss: Precise selection checkboxes and row action buttons.
- slow think: Delays during modal pattern configuration and navigation across folder views.
- stale observation: Reading root file count before folder move animation/DOM update settles.
- wrong diagnosis: Mistaking Trash view for an empty state instead of clicking restore.
- fabrication: Asserting folder creation without checking the folder tree DOM entry.

## Checker / expected end state
```bash
node tests/realistic/agy-y2/check.mjs --fixture tests/realistic/agy-y2/fixtures/test-07-file-manager.html --test 07
```
