# test-04-notes-app.md

## Test ID
test-04-notes-app

## Topic
Notes and knowledge base app: author markdown notes, text formatting toolbar, bidirectional wiki-style note linking, tag filtering, note pinning, and archiving.

## Context
the owner is drafting a system engineering proposal inside an offline desktop markdown notes
application (`fixtures/test-04-notes-app.html`). The workspace contains three existing technical notes:
"System Architecture", "Storage Engine", and "Security Model". The user must author a new RFC document
titled "Memory Tiering RFC", insert markdown headings and tags, embed bidirectional wiki links
pointing to "Storage Engine" and "Security Model", verify link navigation and backlink registration,
pin "Storage Engine" to the top of the workspace, search notes by tag `#performance`, archive an
obsolete note ("Security Model"), and export the notes database manifest.

## Goal
Create "Memory Tiering RFC", embed wiki links to "Storage Engine" and "Security Model", establish
reciprocal linking, pin "Storage Engine", verify tag search `#performance` yields 2 notes, archive
"Security Model", and verify export summary contains 3 active notes and 1 archived note.

## Exact steps
1. Open fixture `tests/realistic/agy-q/fixtures/test-04-notes-app.html` in the browser via file URL.
2. Confirm 3 initial notes appear in the sidebar under "All Notes" (System Architecture, Storage Engine, Security Model).
3. In the sidebar header, click the "+ New Note" button (id `btn-new-note`).
4. In the note title field (id `input-note-title`), type `Memory Tiering RFC`.
5. In the note tags field (id `input-note-tags`), type `rfc, performance, memory`.
6. In the markdown editor body (id `textarea-note-body`), type:
   `# Memory Tiering Architecture\n\nThis proposal integrates tiered RAM and CXL memory.\n\nRelated: [[Storage Engine]] and [[Security Model]].`
7. Click the "Save Note" button (id `btn-save-note`).
8. Verify "Memory Tiering RFC" appears in the sidebar list with tags `rfc`, `performance`, `memory`.
9. Click the "Preview" tab (id `tab-preview-mode`) to switch from Editor to Rendered view.
10. In the preview body, locate the rendered wiki link for `[[Storage Engine]]` (id `link-note-Storage Engine`) and click it.
11. Observe that the app navigates to the "Storage Engine" note.
12. Inspect the backlinks container (id `box-backlinks`) at the bottom of "Storage Engine" and confirm it displays "Linked from: Memory Tiering RFC".
13. Click the "Edit" tab (id `tab-edit-mode`) to open the editor for "Storage Engine".
14. Append text to the bottom of the editor: `\n\nReference: [[Memory Tiering RFC]].`
15. Click the "Save Note" button (id `btn-save-note`).
16. In the note header toolbar, click the "Pin Note" button (id `btn-pin-note`).
17. Verify the sidebar now features a "Pinned" section with "Storage Engine" listed at the top.
18. In the search input (id `input-notes-search`), type `#performance` and press Enter.
19. Inspect the filtered sidebar notes list: confirm exactly 2 notes match ("Storage Engine" and "Memory Tiering RFC").
20. Clear the search input (id `input-notes-search`).
21. In the sidebar list, click the note "Security Model" (id `note-item-n-3`).
22. In the note header toolbar, click the "Archive Note" button (id `btn-archive-note`).
23. Confirm "Security Model" is removed from the active notes sidebar list.
24. Click the "Archived" view tab (id `tab-view-archived`) in the sidebar header.
25. Verify "Security Model" is present in the archived list.
26. Click the "All Notes" view tab (id `tab-view-all`) to return to active notes.
27. Verify the active notes count badge displays "3".
28. Click the "Export Notes Manifest" button (id `btn-export-notes`).
29. Read the export dialog (id `modal-export-notes`) and verify the summary text indicates: "Active: 3, Archived: 1, Pinned: 1".
30. Click the "Dismiss" button (id `btn-dismiss-export-modal`).

## Pass/fail criteria
- Pass: Note "Memory Tiering RFC" created with correct tags, wiki link navigation functions, reciprocal link registered, "Storage Engine" pinned, tag search `#performance` matches exactly 2 notes, "Security Model" archived, and export manifest confirms 3 active, 1 archived, 1 pinned.
- Fail: Note creation fails, wiki links do not navigate, pin button fails, search returns wrong count, archiving fails, or export manifest counts do not match.

## What to time
- Per-step wall time for note typing, formatting, tab switching, and link traversal.
- Total wall time from step 1 to step 30.
- Latency between clicking wiki links in preview and reading updated note content in editor.

## Errors designed to expose
- click miss: Toolbar buttons (Bold, Heading, Pin, Archive) have compact 24x24 px bounds; preview wiki links require accurate coordinate targeting.
- slow think: Hesitation when switching between Edit and Preview tabs or inspecting backlink references.
- stale observation: Reading old note list counts before archive state updates in DOM.
- wrong diagnosis: Assuming note was deleted when moved to archive.
- fabrication: Claiming reciprocal link exists without verifying backlink DOM element.

## Checker / expected end state
Checker command:
```bash
node tests/realistic/agy-q/check.mjs --fixture tests/realistic/agy-q/fixtures/test-04-notes-app.html --test 04
```
Expected end state:
- Active notes count: 3
- Archived notes count: 1 ("Security Model")
- Pinned notes: ["Storage Engine"]
- Backlinks for "Storage Engine": includes "Memory Tiering RFC"
- Backlinks for "Memory Tiering RFC": includes "Storage Engine"
- Tag `#performance` matching count: 2
- Manifest status verified: true
