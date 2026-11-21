# t10-music-player: music player workflow

## Context

A demo music player with a 5-track playlist. Playback is simulated
in the page: one simulated second passes every 100 ms of real time
while playing. Controls: play, pause, previous, next, volume slider,
seek by clicking the progress bar, shuffle, repeat modes, search,
and click a track to play it. Shuffle uses a fixed deterministic
order (current track first, then the rest reversed) so the test can
assert it.

## Goal

Play, pause, and resume with the position moving only while playing,
step through tracks, set the volume, seek, shuffle, cycle repeat
modes, wrap around with repeat All, filter with search, and pick a
track from the list.

## Steps

1. Open the fixture page, check 5 tracks list with Morning Light first.
2. Click Play, check the status is `Playing` and the track is shown.
3. Wait 700 ms, check the position advanced past 5 seconds.
4. Click Pause, check the status is `Paused` and the position is
   frozen over 400 ms.
5. Click Play, wait 500 ms, check the position advanced again.
6. Click Next, check River Road plays from position 0.
7. Click Previous, check Morning Light plays again.
8. Set the volume slider to 30 with the keyboard, check the value.
9. Click the middle of the progress bar, check the position is
   near 90 seconds (half of 180).
10. Turn Shuffle on, check the second track in the list is
    Mountain Air and the current track is unchanged.
11. Click Next, check Mountain Air plays.
12. Turn Shuffle off, check the list order is back to normal and
    Mountain Air still plays.
13. Click Repeat three times, check All, then One, then Off.
14. Click Mountain Air in the list, check it plays.
15. Set Repeat to All, click Next, check it wraps to Morning Light.
16. Click Repeat twice, check One then Off.
17. Search `river`, check only River Road shows.
18. Clear the search, check 5 tracks show again.
19. Click Night Drive in the list, check it plays.
20. Click Pause, check the status is `Paused`.

## Pass conditions

- Every status, track name, position, and value above matches.
- The position moves only while playing.
- Repeat All wraps from the last track to the first.
- Search filters the list and clearing it restores all tracks.

## Fail conditions

- Any status, track, position, or value differs from the expected
  value.
- The position moves while paused or stays still while playing.
- Shuffle or repeat changes the current track unexpectedly.

## Notes

No audio is played; timing is simulated in the page. All state
lives in the page. After Next the checker samples the position
inside the page for 500 ms and takes the minimum: a real reset
passes through 0, while a missed reset leaves the position at its
pre-click value. It then checks the position advances, proving
the playback clock kept running after the change.
The browser run is Playwright Chromium; the same flow on Firefox
or Zen is UNVERIFIED.
