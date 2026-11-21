# test-09-notes-sync.md

## Test ID
test-09-notes-sync

## Topic
Notes synchronization and conflict resolution: create note, simulate multi-device edits, trigger conflict, resolve via "keep both", rename conflict copy, delete outdated version, and verify note inventory.

## Context
A mobile professional uses a cloud-synchronized note-taking application (fixtures/test-09-notes-sync.html).
The user must create a note titled "Shopping", simulate simultaneous conflicting edits originating from Device A (Laptop) and Device B (Phone),
trigger a sync sync collision, select the "Keep Both" conflict resolution strategy, rename the conflicted copy to "Shopping - Phone Copy",
delete the older conflicting draft, and verify that the notes list reflects both intended notes with correct bodies in the DOM.

## Timing
- Baseline start time: 2026-11-21 17:00:00 Asia/Ho_Chi_Minh
- Expected duration: 180 seconds elapsed
- Maximum allowable latency: 300 seconds elapsed

## Goal
Create note "Shopping", simulate edits on two devices, trigger sync conflict, resolve via "keep both", rename conflict copy, delete older draft, and verify note inventory.

## Exact steps
1. Open fixture tests/realistic/agy-y2/fixtures/test-09-notes-sync.html in the browser.
2. Verify element #notes-total-counter text is "2" and #sync-status-indicator text contains "Synchronized".
3. Click button #btn-create-new-note to create a new note.
4. Verify element #note-editor-title value is "Untitled Note".
5. Click input #note-editor-title, clear text, and type "Shopping".
6. Click textarea #note-editor-body and type "Milk, Eggs, Bread".
7. Click button #btn-save-note-edit to save initial version.
8. Verify element #notes-total-counter text is "3" and #note-item-title-shopping text is "Shopping".
9. Click tab #tab-device-a to switch to Laptop sync view.
10. Click textarea #note-editor-body and append ", Apples".
11. Click button #btn-stage-device-a to buffer change on Device A.
12. Verify element #device-a-status text contains "Draft ready: Laptop".
13. Click tab #tab-device-b to switch to Phone sync view.
14. Click textarea #note-editor-body, clear text, and type "Milk, Eggs, Bread, Bananas, Orange Juice".
15. Click button #btn-stage-device-b to buffer conflicting change on Device B.
16. Verify element #device-b-status text contains "Draft ready: Phone".
17. Click button #btn-trigger-cloud-sync to execute synchronization.
18. Verify element #conflict-resolution-modal has class "active".
19. Verify element #conflict-detected-banner text contains "Sync conflict detected for note Shopping".
20. Click button #btn-resolve-keep-both to preserve both versions.
21. Verify element #conflict-resolution-modal has class "closed".
22. Verify element #notes-total-counter text is "4".
23. Verify element #note-item-conflict-copy is present in notes list.
24. Click row #note-item-conflict-copy to load the second version.
25. Verify element #note-editor-title value contains "Shopping (Conflict Copy)".
26. Click input #note-editor-title, clear text, and type "Shopping - Phone Copy".
27. Click button #btn-save-note-edit to update title.
28. Verify element #note-item-title-conflict text is "Shopping - Phone Copy".
29. Simulate mistake: click row #note-item-archived-draft to select an outdated placeholder note.
30. Click button #btn-delete-active-note to delete the outdated version.
31. Verify element #notes-total-counter text is "3".
32. Click row #note-item-title-shopping to view primary note.
33. Verify element #note-editor-body value contains "Milk, Eggs, Bread, Apples".
34. Click button #btn-finalize-sync-report to compile sync verification.
35. Verify element #sync-summary-toast text contains "Sync completed: 3 notes active, Shopping and Shopping - Phone Copy verified".

## Pass/fail criteria
- Pass: Note "Shopping" created, simulated multi-device sync conflict triggered and resolved via "keep both", copy renamed to "Shopping - Phone Copy", outdated draft purged, 3 notes total, and summary toast displayed.
- Fail: Conflict modal does not appear, resolution fails, renamed copy missing from DOM, note count wrong, or summary toast not activated.

## Errors designed to expose
- click miss: Switching between Device A/B tabs and small modal resolution buttons.
- slow think: Delays during conflict resolution decision and payload verification.
- stale observation: Reading notes counter before sync merge settles.
- wrong diagnosis: Mistaking conflict alert for a network failure rather than resolving with "keep both".
- fabrication: Asserting note text without selecting the corresponding list item.

## Checker / expected end state
```bash
node tests/realistic/agy-y2/check.mjs --fixture tests/realistic/agy-y2/fixtures/test-09-notes-sync.html --test 09
```
