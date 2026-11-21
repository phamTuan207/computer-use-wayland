# Council Member 1 verdict: Worker Y7 test-07 fix

- Council member: Council 1 (Muse, independent of Y7 and Y2b)
- Date: 2026-11-21 ~18:25 +07
- Question: is the test-07 fix correct? Proposed fix: change 'Root: 3 files' to 'Root: 5 files' in check.mjs AND in the spec. Do NOT change the fixture.
- Verdict: **GO**. The count is 5, verified independently from the fixture code alone. The fix as specified is correct.

## Note on current working tree state

- check.mjs line 240 already reads 'Root: 5 files, Archive: 3 files, Trash: 0 files, Folder Processed created'.
- test-07-file-manager.md step 35 (line 58) already reads the same string.
- grep over tests/realistic/agy-y2/ finds no remaining 'Root: 3' anywhere.
- So the fix text is already present in the working tree (presumably applied by Y7 before this council read). This verdict judges the VALUE, not the edit: my independent trace below derives 5 from the fixture code, so the present text is correct and no further change is needed for defect 1.

## Independent count trace (fixture code only, no trust in Y2b's trace)

Fixture: tests/realistic/agy-y2/fixtures/test-07-file-manager.html

1. Initial tbody rows: 8. Rows at lines 95, 101, 107, 113, 119, 125, 131, 137: file-row-img1, file-row-img2, file-row-img3, file-row-img4, file-row-img5, file-row-doc1, file-row-doc2, file-row-doc3. Header total-files-count is static '8' (line 55), consistent.
2. Rename handler, lines 233-247: iterates img1 to img5 in order, assigns sequential numbers, then clears the selection (lines 245-247: unchecks all, state.selected.clear()). So at move time the only selected files are the ones re-selected in spec steps 15-17: img1, img2, img3.
3. Move handler, lines 259-271: for each selected id, adds class 'hidden' to the row (line 264) and pushes the id to state.archive (line 265). Hides exactly img1, img2, img3. Archive length becomes 3. Visible rows: 8 - 3 = 5.
4. Delete handler, lines 275-280: adds class 'hidden' to file-row-img4 (line 277) and pushes 'img4' to state.trash (line 278). Visible rows: 5 - 1 = 4. Trash count becomes 1.
5. Restore handler, lines 289-294: filters 'img4' out of state.trash (line 290), sets the trash counter to 0, removes the trash row, and removes class 'hidden' from file-row-img4 (line 294). Visible rows: 4 + 1 = 5. Trash count becomes 0.
6. Toast code, lines 331-334: rootVisible counts '#table-root-files tbody tr:not(.hidden)' (line 332). At report time the hidden rows are exactly img1, img2, img3, so the visible rows are img4, img5, doc1, doc2, doc3 = 5. Archive is state.archive.length = 3, Trash is state.trash.length = 0. The toast prints: 'Root: 5 files, Archive: 3 files, Trash: 0 files, Folder Processed created'.

Computed final visible Root count: **5**. The old expected value 3 matches no step of this trace (8 - 3 moved = 5, and 3 is the Archive count, not the Root count).

## Live-run evidence check

- Y2b's report (improvements/worker-y2b-verification.md, defect 1) cites the live toast as: 'Root: 5 files, Archive: 3 files, Trash: 0 files, Folder Processed created'.
- I re-checked the cited source directly: /tmp/y2b-sim-07.log on the laptop (via ssh-laptop.sh) contains 'Root: 5 files, Archive: 3 files, Trash: 0 files'.
- Code trace and live evidence agree exactly on all three numbers (Root 5, Archive 3, Trash 0).
- Limitation: I could not re-run simulate.mjs on the VM myself (no chromium binary and no puppeteer-core installed here), so the live confirmation rests on Y2b's cited log, which I re-read directly rather than taking the report's word for it.

## Other counts in test-07 spec and checker: checked, no additional mismatch

Each value below was checked against the fixture code:

- Archive 3: move handler pushes 3 ids (lines 259-271); badge set to state.archive.length + ' files' (line 270) = '3 files'. Spec step 22 and check.mjs (archiveCount includes '3 files') are correct.
- Trash 0: restore handler sets the trash counter to state.trash.length = 0 (lines 290-292). Spec step 28 and check.mjs (trashCount === '0') are correct. Intermediate Trash 1 (spec step 24) also matches the delete handler (line 278).
- Names photo-2026-01 and photo-2026-05: rename handler lines 236-242 assigns idx 1 to img1 and idx 5 to img5 (all 5 selected, in order), pattern replace gives 'photo-2026-01.jpg' and 'photo-2026-05.jpg'. Spec steps 13-14 and check.mjs name checks are correct.
- Folder Processed: folder handler lines 320-327 creates div id 'folder-item-' + name.toLowerCase(), so 'Processed' gives 'folder-item-processed'. check.mjs asserts that id exists, and the spec step 35 suffix matches. Correct.
- Spec step 2 (total 8, selected 0) and step 8 (selected 5) match the 8 initial rows and the 5 checkboxes selected in steps 3-7. Correct.
- Pass/fail criteria ('5 files renamed, 3 files moved, 1 deleted file restored, folder Processed created') match the trace. Correct.

Result: **no additional mismatch found** in test-07.

## Minor observation (not a mismatch, no action required)

- The toast suffix 'Folder Processed created' is a hardcoded string in the fixture (line 334), not computed from state.folders, so the toast text alone cannot prove the folder was created. This does not affect the fix: check.mjs separately asserts #folder-item-processed exists, so the end state check as a whole is sound. No change recommended.

## Scope and method

- I read the fixture, check.mjs test-07 branch, the spec, and Y2b's verification report in full. I did not edit any suite file (no change to the fixture, check.mjs, spec, or simulate.mjs). I wrote only this verdict file.
- No ydotool used. No em dash or en dash used in this file. No personal info included.
