# t05-file-manager: file manager workflow

## Context

A demo file manager with a folder tree (Home, Documents, Pictures),
a file list with name and size, search, sorting, and actions: new
folder, rename, delete with a confirm dialog, and move between
folders. Home starts with budget.csv, notes.txt, photo.jpg, and
video.mp4.

## Goal

Organize files the way a real user would: sort and search, create a
folder, move a file in and out, rename a file and a folder, and
delete a file with confirm and cancel.

## Steps

1. Open the fixture page, check Home lists 4 items in name order.
2. Sort by size descending, check video.mp4 is first.
3. Sort by name, check budget.csv is first.
4. Sort by size ascending, check notes.txt is first.
5. Sort by name again.
6. Search `photo`, check only photo.jpg shows.
7. Clear the search, check all 4 items show again.
8. Click New folder, check Archive appears and has a tree button.
9. Double-click Archive, check the crumbs read `Archive` and the
   empty state shows.
10. Go back to Home via the tree.
11. Select notes.txt, click Rename, check the rename dialog opens.
    Cancel and check the name is unchanged. Open it again, submit an
    empty name and check it is rejected with the dialog still open.
    Type meeting-notes.txt, click Save, check the rename applies.
12. Select photo.jpg, click Delete, check the confirm dialog asks
    about photo.jpg, then Cancel and check the list is unchanged.
13. Select photo.jpg again, click Delete, confirm, check it is gone.
14. Select video.mp4, click Move, choose Archive, check Home no
    longer lists it.
15. Open Archive, check video.mp4 is there.
16. Move video.mp4 back to Home, check Archive is empty again.
17. Go back to Home, check all 4 items are there.
18. Select Archive, click Rename, type Old files in the dialog,
    click Save, check it becomes Old files.
19. Search `old`, check only Old files shows.
20. Clear the search, double-click Old files, check the crumbs read
    `Old files` and the empty state shows.

## Pass conditions

- Every list order, count, crumb, and status above matches.
- Cancel keeps the list unchanged; confirm removes the file.
- Moved files appear in the target folder and leave the source.
- A renamed folder still opens from the list and the tree.

## Fail conditions

- Any list, count, crumb, or status differs from the expected value.
- A moved file is in both folders or in neither.
- A renamed folder cannot be opened.

## Notes

Rename opens a dialog with a text input, Save, and Cancel. The new
name comes from what the user types; an empty name is rejected and
the dialog stays open. All state lives in the page. The browser run
is Playwright Chromium; the same flow on Firefox or Zen is UNVERIFIED.
