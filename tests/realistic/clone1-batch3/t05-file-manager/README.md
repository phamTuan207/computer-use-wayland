# t05-file-manager: file manager workflow

## Context

A demo file manager with a folder tree (Home, Documents, Pictures),
a file list with name and size, search, sorting, and actions: new
folder, rename through a dialog that takes a typed name, delete with
a confirm dialog, and move between folders. Home starts with
budget.csv, notes.txt, photo.jpg, and video.mp4.

## Goal

Organize files the way a real user would: sort and search, create a
folder, move a file in and out, rename a file and a folder with
names typed into the rename dialog, and delete a file with confirm
and cancel.

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
11. Select budget.csv, click Rename, check the dialog opens
    prefilled with `budget.csv`, type `budget2.csv`, click Cancel,
    check the name is unchanged and the dialog closed.
12. Click Rename again, submit an empty name, check the name is
    unchanged, the error shows, and the dialog stays open; then
    Cancel and check the dialog closed.
13. Select notes.txt, click Rename, check the dialog is prefilled
    with `notes.txt` and the old name is still listed, type
    `field-notes-7.txt`, click Save, check the new name appears
    and notes.txt is gone.
14. Select photo.jpg, click Delete, check the confirm dialog asks
    about photo.jpg, then Cancel and check the list is unchanged.
15. Select photo.jpg again, click Delete, confirm, check it is gone.
16. Select video.mp4, click Move, choose Archive, check Home no
    longer lists it.
17. Open Archive, check video.mp4 is there.
18. Go back to Home, select Archive, click Rename, type
    `  Old Files 2026  ` with surrounding spaces, click Save,
    check the trimmed name `Old Files 2026` appears, Archive is
    gone, and the tree button reads `Old Files 2026`.
19. Open `Old Files 2026` from the tree, check the crumbs read
    `Old Files 2026` and video.mp4 is still inside it.
20. Move video.mp4 back to Home, check the folder is empty again.
21. Go back to Home, check all 4 items are there.
22. Search `2026`, check only `Old Files 2026` shows.
23. Clear the search, double-click `Old Files 2026`, check the
    crumbs read `Old Files 2026` and the empty state shows.

## Pass conditions

- Every list order, count, crumb, and status above matches.
- Rename applies the typed name, trimmed; the dialog closes after
  Save and after Cancel.
- Cancel and an empty rename keep the name unchanged; an empty
  rename shows the error and leaves the dialog open.
- Moved files appear in the target folder and leave the source.
- A renamed folder keeps its contents and still opens from the
  list and the tree.

## Fail conditions

- Any list, count, crumb, or status differs from the expected value.
- A moved file is in both folders or in neither.
- A renamed folder cannot be opened, or it lost its contents.
- The rename dialog is left open after Save or Cancel (except on
  an empty name, where it must stay open with the error shown).
- A rename applies a name the user did not type.

## Notes

Rename in this demo applies whatever name is typed into the
dialog, trimmed of surrounding spaces. Determinism comes from the
checker typing fixed strings, not from the fixture knowing them:
the names `field-notes-7.txt` and `Old Files 2026` appear only in
the checker, never in the fixture. All state lives in the page.
The browser run is Playwright Chromium; the same flow on Firefox
or Zen is UNVERIFIED.
