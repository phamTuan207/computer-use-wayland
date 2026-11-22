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
6. Click Next, check River Road plays from position exactly 0 (the
   click and the read run in the same in-page task, so no timer
   tick can land between them), the sampled position minimum is at
   most 2 and below the pre-click value, and the position gains at
   least 2 ticks across each of two 350 ms windows, stays
   between 6 and 11 on the middle read, and stays at most 15 on
   the later read while playing.
7. Click Pause, click Next, check Night Drive plays from position
   exactly 0 with the clock frozen, click Play to resume, check
   the position advances to between 2 and 11, then again after
   another 350 ms, then click Previous twice to return to
   Morning Light, checking the position is exactly 0 after each
   Previous and advances again after them.
8. Set the volume slider to 30 with the keyboard, check the value.
9. Click the middle of the progress bar, check the position is
   near 90 seconds (half of 180).
10. Turn Shuffle on, check the second track in the list is
    Mountain Air and the current track is unchanged.
11. Click Next, check Mountain Air plays from position exactly 0
    (same-task click and read), the sampled position minimum is at
    most 2 and below the pre-click value, and the position gains at
    least 2 ticks across each of two 350 ms windows, stays
    between 6 and 11 on the middle read, and stays at most 15 on
    the later read while playing; click Pause, click Next, check
    City Rain plays from position exactly 0 with the clock frozen,
    click Play to resume, check the position advances to between 2
    and 11, then again after another 350 ms, click Previous to
    return to Mountain Air, checking the position is exactly 0
    after it and advances again after it.
12. Turn Shuffle off, check the list order is back to normal and
    Mountain Air still plays.
13. Click Repeat three times, check All, then One, then Off.
14. Click Mountain Air in the list, check it plays from position
    exactly 0 (same-task click and read).
15. Wait 700 ms so the position advances, set Repeat to All, click
    Next, check it wraps to Morning Light from position exactly 0
    (same-task click and read), the sampled position minimum is at
    most 2 and below the pre-click value, and the position gains at
    least 2 ticks across each of two 350 ms windows, stays
    between 6 and 11 on the middle read, and stays at most 15 on
    the later read; click Mountain Air again, check it plays from
    position exactly 0, wait 700 ms, click Pause, click Next, check
    it wraps to Morning Light from position exactly 0 with the clock
    frozen, click Play to resume, check the position advances to
    between 2 and 11, then again after another 350 ms.
16. Click Repeat twice, check One then Off.
17. Search `river`, check only River Road shows.
18. Clear the search, check 5 tracks show again.
19. Click Night Drive in the list, check it plays from position
    exactly 0 (same-task click and read).
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
lives in the page. Every playing Next (plain, shuffle, wrap) is
clicked and read in the same in-page task, so no timer tick can
land between the reset and the read: page JavaScript is
single-threaded, and the click handler runs synchronously inside
the task. That same-task read requires exactly 0. The checker also
samples the position inside the page for 500 ms after each playing
Next and takes the minimum: a real reset passes through 0, while a
missed reset leaves the position at its pre-click value. The
exact-zero check in step 7 runs as a second Next on purpose:
pausing before the first Next and resuming with Play would restart
the playback timer and hide a nextTrack that stops the clock, so
the first Next keeps its playing-path sampler and advancing check,
and the frozen read is a separate step that requires exactly 0.
The same frozen exact-zero read covers the repeat-All wrap Next in
step 15: the wrap branch resets position too, and the track-name
assert alone cannot see a wrap that leaves the old position behind.
The checker waits 700 ms after picking Mountain Air so the position
is past 0 before the wrap; a wrap that fails to reset is only
observable from a nonzero position. The wrap is tested twice: once
while playing, where the same-task read, the sampler, and the
three-point advancing check prove the reset happens, its value, and
that the timer keeps running, and once while paused, where the
exact-zero read proves the reset value again. The step
11 shuffle Next is tested the same way: once while playing
(same-task read, sampler, advancing check) and once while paused
(exact-zero read), with Previous returning to Mountain Air before
Shuffle is turned off. The position is read after every Previous
and every playlist click too, in the same in-page task, requiring
exactly 0: Previous resets the position, and playTrack resets it,
so a Previous or a playlist click that leaves the old position
behind fails there. The Mountain Air click in step 14 is the
sharpest case for that: Mountain Air is already the current track,
so the track-name assert alone cannot see a click that does nothing,
and the position read is its only live witness.
The advancing checks are three-point deltas, not absolute reads:
the checker reads the position when the sampler window ends and
again after two 350 ms sleeps, and requires a gain of at least 2
ticks across each sleep, so a timer that dies part-way through
either window fails even though the absolute position looks
advanced. The absolute 6 to 11 bound on the middle read still
catches a clock at 1.5x or faster; a 1.3x clock sits on the bound
and is caught only intermittently, and a 1.2x clock reads inside
the correct range and is not distinguished in this 850 ms window.
On the slow side the middle-read floor catches a clock slower than
about 0.65x (a 0.59x clock reads 5 on the middle read and fails;
a 0.70x clock reads 6 and is not distinguished in this window).
The later read requires a gain of at least 2 ticks and carries an
absolute upper bound of 15, so a clock that speeds up after the
middle read is caught (a 10x tail reads about 40); a mild 1.43x
tail reads about 13 and is not distinguished. The sampler's
below-pre-click clause is guarded by the pre-click position being
above 0: when the pre-click position is 0 the clause is vacuous
(minimum at least 0 always holds) and only adds a confusing
follow-on failure after a real one, as when playTrack stops the
timer and the position is stuck at 0; the exact-zero read is the
witness in that case.
After every frozen resume the checker waits 350 ms, requires the
position to have advanced to between 2 and 11, waits another
350 ms, and requires a second gain of at least 2 ticks as well as
the absolute 2 to 11 bound: a Play that does not restart the timer
fails here, before any later playlist click can restart it and
mask the defect. The checks observe the clock at three points
spanning about 1.2 s after each advancing-checked Next (plain
step 6, shuffle step 11, and the playing wrap in step 15) and at two points spanning
about 700 ms after each frozen resume (steps 7, 11, 15); a defect that starts after the
final observation cannot be caught by any finite test, and that
is the documented limit, not a hole to chase with a fourth point.
The browser run is Playwright Chromium; the same flow on Firefox
or Zen is UNVERIFIED.
