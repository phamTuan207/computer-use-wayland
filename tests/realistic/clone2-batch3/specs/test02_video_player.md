# Test 02, video player controls, simulated playback

## Goal

Prove an agent can operate a video player UI end to end in a real
browser: transport controls, seek, volume and mute, playback speed,
subtitles in two languages, and a playlist, verifying the player
state from the DOM after every action. The fixture simulates
playback with a JavaScript clock, so no real media file or network
is involved and the test is fully offline.

Fixture: fixtures/test02_video_player.html
Test: tests/test02_video_player.py

## Steps

1. Start the browser and load the fixture.
2. Verify the initial state: paused, video 1 title shown, duration
   label 4:00, toggle button labelled Play, time 0:00.
3. Click the toggle button to play.
4. Wait about 1.2 real seconds and verify the clock advanced and
   the state reads playing.
5. Pause and verify the clock stays frozen across a 0.6 second
   wait.
6. Seek to 120 seconds with the seek slider and verify the time
   label reads 2:00 and the progress bar is about 50 percent.
7. Set the volume slider to 30 and verify the volume label.
8. Mute and verify the muted state and a zero volume slider.
9. Unmute and verify the volume restores to 30.
10. Set playback speed to 2x.
11. Play for about 1.2 real seconds and verify the clock advanced
    at least 1.5 times the distance it covered at speed 1.
12. Seek to 15 seconds.
13. Enable English subtitles and verify the caption for the 10 to
    30 second segment appears.
14. Switch subtitles to Vietnamese and verify the caption text
    changes to the Vietnamese line for the same segment.
15. Load playlist item 2 and verify its title, its 3:00 duration,
    a reset time of 0:00, and the highlight on the item.
16. Load playlist item 3 and verify its title and 5:00 duration.
17. Play item 3 briefly and verify the clock advances.

## Expected results

- Playing state is always readable from the player data attribute
  and the toggle button label.
- Seeking, volume, mute, speed and subtitle changes are all
  reflected in the DOM immediately.
- Loading a playlist item resets the time to zero and pauses.
- Every check in the test passes.

## Timing

Filled after the verification run on the clone2 machine, headless
Firefox, 2026-11-21:

- RESULT ok: true, on two consecutive runs
- Step count: 21, including browser_start
- Checks: 32, all passing on both runs
- Total elapsed: 28.2941 s on the first run, 31.1248 s on the
  second run, most of it browser start and per call latency on
  this machine, the in-test waits total about 4 seconds
- Measured playback: 1.20 s of video time in about 1.2 real
  seconds at speed 1, and 2.40 s of video time in about 1.2 real
  seconds at speed 2, an exact 2.0 ratio against the 1.5 minimum
  the test asserts
