# test-06-video-editor.md

## Test ID
test-06-video-editor

## Topic
Video editor timeline workflow with clip import, split, trim recovery, reorder, transition, and export settings.

## Context
An editor assembles a short harbor recap in Cutline Video Editor. They import two video clips and a music asset, split a clip, recover from an incorrect trim, reorder the timeline, add a transition, and export with specified settings. The fixture is tests/realistic/codex-y5/fixtures/test-06-video-editor.html.

## Timing
- Baseline start time: 2026-11-21 18:21:00 Asia/Ho_Chi_Minh
- Expected duration: 300 seconds elapsed
- Maximum allowable latency: 420 seconds elapsed

## Goal
Export harbor-recap.mp4 at 1920x1080, 30 fps, H.264, with a 19-second timeline ordered City B-roll, a five-second Forest A-roll segment, and a six-second Forest A-roll segment.

## Exact steps
1. Open tests/realistic/codex-y5/fixtures/test-06-video-editor.html in the browser.
2. Verify #imported-clip-count text is "0", #timeline-clip-count text is "0", #timeline-duration text is "0 sec", #timeline-order text is "Timeline is empty", and #export-status text is "Not exported".
3. Click button #btn-open-import; #import-modal must become visible.
4. Verify #chk-import-forest is unchecked, #chk-import-city is unchecked, and #chk-import-score is unchecked.
5. Click checkbox #chk-import-forest; it must become checked.
6. Click checkbox #chk-import-city; it must become checked.
7. Click checkbox #chk-import-score; it must become checked.
8. Click button #btn-import-selected; #imported-clip-count must become "3".
9. Verify #media-name-forest text is "Forest A-roll (12 sec)", #media-name-city text is "City B-roll (8 sec)", and #media-name-score text is "Night Score (20 sec)".
10. Click button #btn-add-forest; #timeline-clip-count must become "1".
11. Click button #btn-add-city; #timeline-clip-count must become "2".
12. Verify #timeline-duration text is "20 sec" and #timeline-order text is exactly "Forest A-roll (12 sec)\nCity B-roll (8 sec)".
13. Click button #btn-select-forest, then replace #playhead-input value with "5".
14. Click button #btn-split-selected; #timeline-clip-count must become "3".
15. Verify #timeline-duration text is "20 sec" and #timeline-order text is exactly "Forest A-roll (5 sec)\nForest A-roll (7 sec)\nCity B-roll (8 sec)".
16. Click button #btn-select-forest-tail; #timeline-selection text must become "Selected Forest A-roll".
17. Mistake: replace #trim-duration-input value with "2"; its value must be "2".
18. Click button #btn-apply-trim; #timeline-duration must drop to "15 sec".
19. Verify #timeline-order text is exactly "Forest A-roll (5 sec)\nForest A-roll (2 sec)\nCity B-roll (8 sec)".
20. Recovery: click button #btn-undo-edit; #timeline-duration must return to "20 sec".
21. Verify #timeline-order text is exactly "Forest A-roll (5 sec)\nForest A-roll (7 sec)\nCity B-roll (8 sec)".
22. Replace #trim-duration-input value with "6"; its value must be "6".
23. Click button #btn-apply-trim; #timeline-duration must become "19 sec".
24. Verify #timeline-order text is exactly "Forest A-roll (5 sec)\nForest A-roll (6 sec)\nCity B-roll (8 sec)".
25. Click button #btn-select-city; #timeline-selection text must become "Selected City B-roll".
26. Click button #btn-move-selected-left; #timeline-order text must become exactly "Forest A-roll (5 sec)\nCity B-roll (8 sec)\nForest A-roll (6 sec)".
27. Click button #btn-move-selected-left again; #timeline-order text must become exactly "City B-roll (8 sec)\nForest A-roll (5 sec)\nForest A-roll (6 sec)".
28. Verify #timeline-order text is exactly "City B-roll (8 sec)\nForest A-roll (5 sec)\nForest A-roll (6 sec)" and #timeline-duration text is "19 sec".
29. Select value "Cross Dissolve" in #transition-type; its selected value must be "Cross Dissolve".
30. Click button #btn-add-transition; #transition-summary must become "Cross Dissolve between City B-roll and Forest A-roll".
31. Select value "1920x1080" in #export-resolution-select; the selected value must be "1920x1080".
32. Select value "30 fps" in #export-frame-rate-select; the selected value must be "30 fps".
33. Select value "H.264" in #export-codec-select; the selected value must be "H.264".
34. Type "harbor-recap.mp4" into #export-filename-input; its value must be "harbor-recap.mp4".
35. Click button #btn-export-video; #export-status must become "Export complete: harbor-recap.mp4 (1920x1080, 30 fps, H.264)".
36. Verify #export-resolution text is "1920x1080", #export-frame-rate text is "30 fps", #export-codec text is "H.264", #export-filename text is "harbor-recap.mp4", and #export-status text is "Export complete: harbor-recap.mp4 (1920x1080, 30 fps, H.264)".

## Pass/fail criteria
- Pass: The final timeline is 19 seconds in the specified order, the transition is Cross Dissolve, all three export settings match, and the export status names harbor-recap.mp4.
- Fail: The bad trim is not undone, clip order or duration is wrong, transition is missing, or export settings differ.

## Errors designed to expose
- click miss: Import checkboxes, timeline clip selectors, and edit buttons are grouped closely.
- slow think: The timeline changes shape after splitting and again after each reorder.
- stale observation: The trim mistake and undo change duration from 20 to 15 and back to 20.
- wrong diagnosis: The first trim value is accepted by the editor but must be recognized as incorrect and undone.
- fabrication: Clip durations add to 19 seconds and the export banner repeats all required settings.

## Checker / expected end state
```bash
node tests/realistic/codex-y5/check.mjs --fixture tests/realistic/codex-y5/fixtures/test-06-video-editor.html --test 06
```
