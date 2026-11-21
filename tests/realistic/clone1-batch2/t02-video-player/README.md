# t02-video-player: play a real clip end to end

## Context

A video player page with a real 10 s clip (clip.mp4, generated with
ffmpeg, 320x180, test picture and tone), a captions track
(captions.vtt), and custom controls: play, pause, seek, volume, mute,
speed, captions toggle, replay.

## Goal

Drive every control, prove the time actually moves, the captions follow
the position, and the clip ends and replays.

## Steps (35)

1. Open the fixture.
2. Wait for video metadata.
3. Check the duration is about 10 s.
4. Press play.
5. Let it play 2 s.
6. Check currentTime advanced past 1.2 s.
7. Check the video is not paused.
8. Press pause.
9. Check the video is paused.
10. Check the time stays frozen while paused.
11. Seek to 5 s.
12. Check the seek landed near 5 s.
13. Set volume to 0.5.
14. Check the volume is 0.5.
15. Press mute.
16. Check the video is muted.
17. Press unmute.
18. Check the video is unmuted.
19. Set speed to 2x.
20. Check playbackRate is 2.
21. Set speed back to 1x.
22. Seek to 1 s for captions.
23. Check the first caption text is shown.
24. Seek to 7 s.
25. Check the last caption text is shown.
26. Turn captions off.
27. Check the caption box cleared.
28. Turn captions back on.
29. Seek near the end and play.
30. Wait for the ended state.
31. Check the ended flag.
32. Press replay.
33. Check replay restarted near 0.
34. Check the video plays after replay.
35. Check the time label shows the / 10.0 s format.

## Pass

All 35 steps run, the time moves only while playing, seek lands where
asked, volume, mute, and speed match, captions follow the position, the
clip reports ended, and replay restarts it.

## Fail

Any step above fails, the time moves while paused, a seek lands far
from the target, a caption is wrong or missing, or the clip never ends.
