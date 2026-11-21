# test-02-music-player.md

## Test ID
test-02-music-player

## Topic
Music player playlist management with track selection, reordering, shuffle, removal, recovery, and saving.

## Context
A listener is building a focused playlist in Music Desk. They must add four library tracks, reorder one, recover after removing the wrong track, shuffle the list, remove the unwanted track, and save the final three-track playlist. The fixture is tests/realistic/codex-y5/fixtures/test-02-music-player.html.

## Timing
- Baseline start time: 2026-11-21 18:21:00 Asia/Ho_Chi_Minh
- Expected duration: 210 seconds elapsed
- Maximum allowable latency: 330 seconds elapsed

## Goal
Save playlist Morning Focus with three tracks in the order Quiet Circuit, Paper Planes, Low Tide and total duration 10:10.

## Exact steps
1. Open tests/realistic/codex-y5/fixtures/test-02-music-player.html in the browser.
2. Verify #playlist-name text is "No playlist selected", #playlist-count text is "0", #playlist-duration text is "0:00", #playlist-track-list text is "No tracks", #shuffle-status text is "Shuffle Off", and #save-status text is "Not saved".
3. Type "Morning Focus" into #playlist-name-input; its value must be "Morning Focus".
4. Click button #btn-create-playlist; #playlist-name must become "Morning Focus".
5. Click button #btn-add-track-low-tide; #playlist-count must become "1".
6. Verify #playlist-duration text is "3:20" and #playlist-track-list text is "Low Tide".
7. Click button #btn-add-track-paper-planes; #playlist-count must become "2".
8. Click button #btn-add-track-quiet-circuit; #playlist-count must become "3".
9. Click button #btn-add-track-night-shift; #playlist-count must become "4".
10. Verify #playlist-duration text is "14:00" and #playlist-track-list text is exactly "Low Tide\nPaper Planes\nQuiet Circuit\nNight Shift".
11. Click button #btn-move-paper-up; the first playlist track must become "Paper Planes".
12. Verify #playlist-track-list text is exactly "Paper Planes\nLow Tide\nQuiet Circuit\nNight Shift".
13. Mistake: click button #btn-remove-quiet-circuit and remove the wrong track; #playlist-count must drop to "3".
14. Verify #playlist-action-status text is "Removed Quiet Circuit" and #playlist-duration text is "11:15".
15. Recovery: click button #btn-undo-playlist-change; #playlist-count must return to "4".
16. Verify #playlist-action-status text is "Last removal undone", #playlist-duration text is "14:00", and #playlist-track-list text is exactly "Paper Planes\nLow Tide\nQuiet Circuit\nNight Shift".
17. Click button #btn-shuffle; #shuffle-status must become "Shuffle On".
18. Verify #playlist-track-list text is exactly "Night Shift\nQuiet Circuit\nPaper Planes\nLow Tide".
19. Click button #btn-remove-night-shift; #playlist-count must become "3" and #playlist-duration must become "10:10".
20. Verify #playlist-track-list text is exactly "Quiet Circuit\nPaper Planes\nLow Tide" and #shuffle-status text is "Shuffle On".
21. Click button #btn-save-playlist; #save-status must become "Playlist saved: Morning Focus (3 tracks, 10:10)".
22. Verify #playlist-name text is "Morning Focus", #playlist-count text is "3", and #save-status text is "Playlist saved: Morning Focus (3 tracks, 10:10)".

## Pass/fail criteria
- Pass: Morning Focus is saved with Quiet Circuit, Paper Planes, and Low Tide in that order, shuffle is on, and the duration is 10:10.
- Fail: The accidental removal is not undone, a wrong track remains, the order differs, the duration is incorrect, or the save status does not name the exact playlist and count.

## Errors designed to expose
- click miss: Track add, reorder, remove, and undo controls sit close together.
- slow think: The task requires tracking order while shuffle changes every row.
- stale observation: The duration and count change after removal and recovery.
- wrong diagnosis: The first removal is intentional-looking but targets a required track.
- fabrication: The final duration is independently checkable from 2:45, 4:05, and 3:20.

## Checker / expected end state
```bash
node tests/realistic/codex-y5/check.mjs --fixture tests/realistic/codex-y5/fixtures/test-02-music-player.html --test 02
```
