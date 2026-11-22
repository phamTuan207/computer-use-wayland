# test-10-markdown-editor.md

## Test ID
test-10-markdown-editor

## Topic
Markdown preview editor: dual-pane editing and live HTML preview, document renaming, markdown syntax formatting, accidental text entry and deletion, word counting, HTML export, and document saving.

## Context
the owner is drafting technical release documentation for version 2.3.0.
The workstation runs an offline markdown editor (fixtures/test-10-markdown-editor.html).
The user must rename the document to "Release Notes v2.3.0", compose structured markdown featuring an H1 title ("# Architecture Overview"), an H2 subheading ("## Core Changes"), a bulleted list with two verified entries, handle and remove an accidental entry ("- Broken experimental feature (deprecated)"), add a strong emphasis note ("**Zero regressions** observed in test suite."), verify real-time preview DOM rendering, trigger HTML export, and save the document.

## Timing
- Baseline start time: 2026-11-21 17:30:00 Asia/Ho_Chi_Minh
- Expected duration: 150 seconds elapsed
- Maximum allowable latency: 260 seconds elapsed

## Goal
Set title to "Release Notes v2.3.0", write markdown with H1, H2, 2 list items, strong note, remove accidental broken feature, export HTML, verify live preview DOM state, and save document.

## Exact steps
1. Open fixture tests/realistic/agy-q2/fixtures/test-10-markdown-editor.html in the browser.
2. Verify initial empty preview message in live preview pane (id "markdown-preview").
3. Click document title input (id "input-doc-title").
4. Clear existing value and type "Release Notes v2.3.0".
5. Click markdown source textarea (id "markdown-source").
6. Type `# Architecture Overview`.
7. Verify live preview renders an `<h1>` tag with text "Architecture Overview".
8. In markdown source, type newline and `## Core Changes`.
9. Verify live preview renders an `<h2>` tag with text "Core Changes".
10. In markdown source, type newline and `- Replaced X11 with native Wayland compositor`.
11. Type newline and `- Added offline test validation suite`.
12. Verify live preview renders an unordered list (`<ul>`) with 2 list items (`<li>`).
13. Accidental entry: type newline and `- Broken experimental feature (deprecated)`.
14. Verify preview shows 3 list items.
15. Remove the accidental line from the textarea so only the 2 valid items remain.
16. Verify preview returns to exactly 2 list items.
17. Type newline and `**Zero regressions** observed in test suite.`.
18. Verify preview renders a `<p>` containing a `<strong>` tag with text "Zero regressions".
19. Inspect word count indicator (id "stat-word-count") and confirm it reflects non-zero word count.
20. Click "Export HTML" button (id "btn-export-html").
21. Verify export badge (id "export-status-tag") becomes visible displaying "HTML Exported".
22. Click "Save Document" button (id "btn-save-doc").
23. Read status banner (id "editor-status-banner") and confirm it displays "Document saved: 'Release Notes v2.3.0' (HTML exported, 0 errors)".

## Pass/fail criteria
- Pass: Title is "Release Notes v2.3.0", live preview contains H1, H2, exactly 2 list items, strong tag, accidental entry removed, HTML exported, and status banner confirms saved document.
- Fail: Accidental entry retained, wrong title, missing headings or list items, HTML not exported, or status banner unconfirmed.

## Errors designed to expose
- text editing precision: Leaving stray markdown syntax or newline discrepancies.
- preview synchronization: Failing to check DOM elements in the live preview pane.
- accidental entry retention: Failing to remove the broken experimental feature line.
- export omission: Saving before triggering HTML export.
- fabrication: Asserting valid Markdown structure without checking the rendered preview tags.

## Checker / expected end state
```bash
node tests/realistic/agy-q2/check.mjs --fixture tests/realistic/agy-q2/fixtures/test-10-markdown-editor.html --test 10
```
