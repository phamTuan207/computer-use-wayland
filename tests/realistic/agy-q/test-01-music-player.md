# test-01-music-player.md

## Test ID
test-01-music-player

## Topic
Music player: create playlist, filter library, add tracks, reorder, remove mistake, and save playlist.

## Context
the owner needs to assemble a focused audio tracklist for an engineering sprint.
The workstation runs an offline browser player (`fixtures/test-01-music-player.html`).
The track catalog holds 12 tracks across four genres (Synthwave, Ambient, Lo-Fi, Classical).
The user must create a new playlist titled "Deep Work 2026", locate and add four specific
tracks from the catalog, detect and remove one incorrectly added track, reorder the tracks
into an exact sequence to optimize flow, verify that the computed total runtime updates
accurately to 15:40 (940 seconds), and save the playlist to local storage.

## Goal
Create playlist "Deep Work 2026", populate it with the specified 4 tracks in exact order:
1. Solar Winds (Ambient, 4:15)
2. Neon Horizon (Synthwave, 3:45)
3. Coffee Beans (Lo-Fi, 2:30)
4. Midnight Pulse (Synthwave, 5:10)
Confirm total duration equals 15:40, click Save Playlist, and verify save confirmation.

## Exact steps
1. Open fixture `tests/realistic/agy-q/fixtures/test-01-music-player.html` in the browser via file URL.
2. Verify the library displays 12 tracks and the default playlist list shows "Favorites" and "Recently Played".
3. Click the "New Playlist" button (id `btn-new-playlist`) in the left sidebar.
4. In the playlist name input prompt (id `input-playlist-name`), type `Deep Work 2026`.
5. Click the "Create" button (id `btn-create-playlist`).
6. Verify "Deep Work 2026" appears in the sidebar and is highlighted as the active playlist.
7. Click the library search box (id `input-library-search`) and type `Neon Horizon`.
8. Locate "Neon Horizon" in the filtered catalog table and click its "+ Add" button (id `add-track-1`).
9. Clear the search box and type `Midnight Pulse`.
10. Locate "Midnight Pulse" in the table and click its "+ Add" button (id `add-track-3`).
11. Clear the search box and type `Coffee Beans`.
12. Locate "Coffee Beans" in the table and click its "+ Add" button (id `add-track-5`).
13. Clear the search box and type `Solar Winds`.
14. Locate "Solar Winds" in the table and click its "+ Add" button (id `add-track-7`).
15. By mistake, click "+ Add" on the adjacent track "Rainy Window" (id `add-track-8`).
16. Inspect the active playlist table: observe that 5 tracks are present and total duration shows 19:10.
17. In the playlist table, find the row for "Rainy Window" and click its "Remove" button (button with data-action="remove-8").
18. Verify the playlist now contains exactly 4 tracks and the duration displays 15:40.
19. Reorder tracks: Locate "Solar Winds" (currently at position 4) and click its "Move Up" arrow (button with data-action="up-7") three times until it reaches position 1.
20. In the playlist table, verify the current order from top to bottom is:
    - 1. Solar Winds (4:15)
    - 2. Neon Horizon (3:45)
    - 3. Midnight Pulse (5:10)
    - 4. Coffee Beans (2:30)
21. Move "Coffee Beans" up one slot by clicking its "Move Up" arrow (button with data-action="up-5") so that it moves to position 3 and pushes "Midnight Pulse" to position 4.
22. Confirm the final playlist track order is:
    - 1. Solar Winds
    - 2. Neon Horizon
    - 3. Coffee Beans
    - 4. Midnight Pulse
23. Click the "Save Playlist" button (id `btn-save-playlist`).
24. Read the status banner (id `save-status-banner`) and confirm it displays "Playlist Deep Work 2026 saved successfully (4 tracks, 15:40)".

## Pass/fail criteria
- Pass: Playlist "Deep Work 2026" exists with exactly 4 tracks in sequence (Solar Winds, Neon Horizon, Coffee Beans, Midnight Pulse), duration equals 15:40, status banner confirms save, and no phantom tracks remain.
- Fail: Any wrong track in playlist, track sequence incorrect, total runtime not 15:40, missed clicks on move up/down controls, or unconfirmed save status.

## What to time
- Per-step wall time for search queries, button clicks, and order changes.
- Total wall time from opening the fixture to clicking save and confirming status.
- Recovery latency when detecting the mistakenly added track "Rainy Window" and removing it.

## Errors designed to expose
- click miss: Move Up and Move Down buttons have small bounding boxes (24x24 px); vision model grounding often offsets clicks into table borders.
- slow think: Delays during multi-step filtering and typing across multiple tracks.
- stale observation: Reading outdated duration before the removal of "Rainy Window" has re-rendered.
- wrong diagnosis: Mistaking the library search filter for a missing track when the search box was not cleared.
- fabrication: Asserting the playlist is saved without verifying the confirmation message in `save-status-banner`.

## Checker / expected end state
Checker command:
```bash
node tests/realistic/agy-q/check.mjs --fixture tests/realistic/agy-q/fixtures/test-01-music-player.html --test 01
```
Expected end state:
- Playlist: "Deep Work 2026"
- Track count: 4
- Track IDs in order: [7, 1, 5, 3]
- Total seconds: 940 (15:40)
- Saved flag: true
