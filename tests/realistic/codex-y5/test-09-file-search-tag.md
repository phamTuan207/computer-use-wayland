# test-09-file-search-tag.md

## Test ID
test-09-file-search-tag

## Topic
File manager name search, tagging a set, filtering by tag, bulk rename, and moving the tagged files.

## Context
A project coordinator is organizing release materials in Cabinet File Manager. They search by name, correct an overly narrow query, tag the checklist and plan, filter to that tag, rename the selected set, and move it to the Reviewed folder. The fixture is tests/realistic/codex-y5/fixtures/test-09-file-search-tag.html.

## Timing
- Baseline start time: 2026-11-21 18:21:00 Asia/Ho_Chi_Minh
- Expected duration: 240 seconds elapsed
- Maximum allowable latency: 360 seconds elapsed

## Goal
Move two files tagged Review into Reviewed and rename them approved-release-checklist.md and approved-release-plan.md.

## Exact steps
1. Open tests/realistic/codex-y5/fixtures/test-09-file-search-tag.html in the browser.
2. Verify #active-folder text is "Root", #visible-file-count text is "6", #selected-file-count text is "0", and #active-tag-filter text is "All".
3. Type "releases" into #file-search-input; its value must be "releases".
4. Click button #btn-search-files; #visible-file-count must become "0".
5. Verify #file-list text is "No matching files" and #visible-file-count text is "0".
6. Recovery: replace #file-search-input value with "release"; its value must be "release".
7. Click button #btn-search-files; #visible-file-count must become "3".
8. Verify #file-name-checklist text is "release-checklist.md", #file-name-plan text is "release-plan.md", and #file-name-artwork text is "release-artwork.png".
9. Click checkbox #check-file-checklist; #selected-file-count must become "1".
10. Click checkbox #check-file-plan; #selected-file-count must become "2".
11. Verify #selected-file-count text is "2".
12. Click button #btn-open-tag-panel; #tag-panel must become visible.
13. Type "Review" into #tag-name-input; its value must be "Review".
14. Click button #btn-apply-tag; #file-action-status must become "Tagged 2 files with Review".
15. Verify #tag-checklist text is "Review", #tag-plan text is "Review", and #tag-artwork text is "No tag".
16. Click button #btn-filter-review; #active-tag-filter must become "Review".
17. Verify #visible-file-count text is "2", #file-name-checklist text is "release-checklist.md", and #file-name-plan text is "release-plan.md".
18. Click button #btn-select-visible-files; #selected-file-count must become "2".
19. Type "approved-" into #rename-prefix-input; its value must be "approved-".
20. Click button #btn-rename-selected; #file-name-checklist must become "approved-release-checklist.md".
21. Verify #file-name-plan text is "approved-release-plan.md" and #active-tag-filter text is "Review".
22. Select value "Reviewed" in #move-target-folder; its selected value must be "Reviewed".
23. Click button #btn-move-selected; #active-folder must become "Reviewed".
24. Verify #active-folder text is "Reviewed", #active-tag-filter text is "Review", #visible-file-count text is "2", #file-name-checklist text is "approved-release-checklist.md", #file-name-plan text is "approved-release-plan.md", #tag-checklist text is "Review", #tag-plan text is "Review", #file-location-checklist text is "Reviewed", #file-location-plan text is "Reviewed", and #file-action-status text is "Moved 2 tagged files to Reviewed".

## Pass/fail criteria
- Pass: Exactly the two tagged release files are visible in Reviewed with the required names and Review tags.
- Fail: The wrong files are tagged, the artwork is renamed or moved, the wrong folder is active, or either required filename or tag differs.

## Errors designed to expose
- click miss: File checkboxes and bulk controls are close to each other.
- slow think: Search results shrink after the tag filter and change names after the bulk rename.
- stale observation: The tag filter must be reapplied to confirm only two rows remain.
- wrong diagnosis: The initial plural query returns no files and must be corrected to the singular prefix.
- fabrication: The final folder, exact filenames, tags, and visible count are all asserted.

## Checker / expected end state
```bash
node tests/realistic/codex-y5/check.mjs --fixture tests/realistic/codex-y5/fixtures/test-09-file-search-tag.html --test 09
```
