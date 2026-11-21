# test-06-settings-two-apps.md

## Test ID
test-06-settings-two-apps

## Topic
Settings configuration across 2 apps.

## Context
Pham Tuan needs to align a preference across two local applications: set the
default font size in the notes app and the default zoom level in the reader app
to matching values, then confirm both apps reflect the change when a sample
document is opened. The agent opens app A settings, changes font size, opens app
B settings, changes zoom, opens a sample doc in each, and verifies the visual
setting took effect in both. This is a cross-app configuration task.

## Goal
Configure notes app font size and reader app zoom to matching values, open a
sample document in each app, and confirm both settings are applied.

## Exact steps
1. Open the settings fixture `fixtures/test-06-settings.html` in the local
   browser (offline, file:// URL).
2. Verify both app cards (Notes and Reader) are visible with their settings
   panels.
3. Open the Notes app card; click its Settings button.
4. Read the current font size value.
5. Change Notes font size to 18 (type or select 18).
6. Click Apply in Notes settings.
7. Close Notes settings and open the Notes app (click Open Notes).
8. Open a sample document in Notes and confirm the text renders at font size 18.
9. Close Notes and return to the settings fixture.
10. Open the Reader app card; click its Settings button.
11. Read the current zoom value.
12. Change Reader zoom to 150 percent.
13. Click Apply in Reader settings.
14. Close Reader settings and open the Reader app (click Open Reader).
15. Open a sample document in Reader and confirm the zoom is 150 percent.
16. Return to the settings fixture and re-read both settings values.
17. Confirm Notes font size still shows 18 and Reader zoom still shows 150%.
18. Confirm both sample documents remain open with the applied settings.

## Pass/fail criteria
- Pass: Notes font size 18 applied and visible in sample doc; Reader zoom 150%
  applied and visible in sample doc; both settings persist after re-read.
- Fail: font size not changed, zoom not changed, setting reverts on re-read,
  wrong app edited, sample doc not reflecting the setting.

## What to time
- Per-step wall time for each open/change/apply/read (18 steps).
- Total wall time from step 1 to step 18.
- Time opening settings and applying in each app (per-app config latency).
- Time re-reading settings after applying (stale observation check).

## Errors designed to expose
- click miss: clicking the wrong app card, the wrong settings field, or Apply
  in the wrong app.
- slow think: long pause between reading the current value and entering the
  new value.
- stale observation: reading the settings panel before Apply completes, seeing
  the old value.
- wrong diagnosis: concluding the app ignores settings when the sample doc was
  opened before Apply was clicked.
- fabrication: claiming a setting was applied without opening the sample doc.

## Checker / expected end state
Checker script: `tests/realistic/fcc-k/check.mjs --fixture
fixtures/test-06-settings.html --test 06`.
Expected end state: Notes font size = 18, Reader zoom = 150%, both settings
persist on re-read, both sample docs open with the applied values.