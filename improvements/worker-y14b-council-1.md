# Council Voice 1: Y14b re-stage review, T10 translation only

- Scope: commit f732d6a on todolist-push, ONLY run_b3_t10 in
  tests/realistic/run_batch3.py against the new t10 checker
  tests/realistic/clone1-batch3/t10-music-player/check.mjs at main
  commit 1d23532 (353 lines, md5 c55ef3c792b2faaea7c829818eb6420b).
- Checker is byte-identical between 1d23532 and main HEAD 3b50e94
  (diff empty, md5 match), so "suite HEAD 1d23532" is the current
  main checker. No ambiguity about which checker was translated.
- Method: independent re-derivation, not trust in the Y14b log.
  Read check.mjs in full, read run_b3_t10 in full at f732d6a,
  enumerated checker asserts myself, ran /tmp/y14b-transcribe.py,
  checked the fixture at 1d23532, checked driver semantics in
  run_live.py (WD.eval, WD.value, Runner.step/check) and the t10
  helpers in run_batch3.py (press_keys, _rect_of, pointer_click_at,
  type_empty). Verified run_batch3.py is identical between f732d6a
  and HEAD a46d503 (git diff empty), so the transcribe run against
  the working tree is a run against f732d6a.
- Verdict: GO. No fixes required. One watch item for the live run
  (timing margin, section 5) and two honest notes (log count
  staleness, step-abort semantics). Neither blocks.

## 1. Assert coverage: 69/69 checker asserts, same order, same thresholds

Independent enumeration of check.mjs: 33 expectText call sites plus
36 direct failures.push assert sites (excluding the expectText helper
definition and the catch-all) = 69 assert sites. The runner has 33
expect_text calls plus 39 r.check calls = 72 check invocations.
72 = 69 + 3 extras, and the 3 extras are the volume value reads
(section 2). The transcribe script reports 72 PASS order lines and
0 failures, exit 0, which matches my independent count exactly.

Pairing, in checker order (thresholds verified equal at each site):

- Playlist 5, first track Morning Light: identical.
- Status Playing / now-playing Morning Light after play: identical.
- Position after 700 ms: pos >= 5, both.
- Status Paused, frozen1 == frozen2, resumed > frozen2: identical.
- Exact-zero playing Next: == 0, both. Now-playing River Road.
  Sampler: checker fails when min > 2 or min >= posBefore; runner
  passes only when min <= 2 and min < posBefore. Same condition,
  with posBefore = resumed on both sides.
- Advancing, plain Next: gain >= 2 across each 350 ms sleep, middle
  read 2..11, later read gain-only with NO absolute bound. Verified
  in the checker: the later read (line 123) has only the gain push,
  no range push. Runner matches exactly.
- Frozen Next: pause, status Paused, click Next, == 0, now-playing
  Night Drive, resume Playing, first resume read 2..11, second
  resume read gain >= 2 AND 2..11. Runner matches exactly.
- Double Prev: River Road then Morning Light. Runner matches.
- Volume: see section 2. Seek 85..100 read immediately after the
  50% click, no sleep between. Runner matches.
- Shuffle On, listed[1] Mountain Air, now-playing unchanged
  (Morning Light). Exact-zero shuffle Next == 0, now-playing
  Mountain Air, sampler same threshold with posBefore read before
  the click on both sides. Advancing shuffle: gain >= 2, middle
  2..11, later gain-only with NO absolute bound (checker line 210
  is gain-only; runner matches).
- Frozen shuffle Next: == 0, now-playing City Rain, resume reads
  2..11 then gain >= 2 AND 2..11. Prev to Mountain Air. Shuffle
  Off, listed[0] Morning Light, now-playing unchanged (Mountain
  Air). Runner matches.
- Repeat All / One / Off, click track[4] Mountain Air, 700 ms play,
  posBeforePlayingWrap >= 2, repeat All, exact-zero playing wrap
  == 0, now-playing Morning Light, sampler same threshold.
  Click track[4] again, 700 ms play, posBeforeFrozenWrap >= 2,
  pause, exact-zero frozen wrap == 0, now-playing Morning Light,
  resume reads 2..11 then gain >= 2 AND 2..11. Repeat One / Off
  after wrap. Runner matches.
- Search river: exactly 1 track, River Road. Clear search: 5
  tracks. Click track[2] Night Drive. Final pause. Runner matches.

No advancing check follows either wrap Next, on both sides. No
checker assert is missing, none is reordered, no threshold differs.

## 2. The 3 extra runner checks are sound (volume 50/0/30)

The checker asserts only #volume-value text == "30". The runner
additionally reads d.value("#volume") after click (want "50"),
after Home (want "0"), and after 30x ArrowRight (want "30").
Verified against the fixture at 1d23532: the range input has
value="50" and #volume-value text "50" by default; clicking the
slider only focuses it; Home sets 0; 30 ArrowRight steps from 0
set 30. WD.value reads the value property, returned as a string,
so the string comparisons are correct. These extras are stricter
than the checker, fail-closed on a wrong slider, and cannot false
fail on the shipped fixture. Acceptable, not a defect.

## 3. Same-task exact-zero eval is sound

Three exact_zero_next() call sites (playing Next, shuffle Next,
playing wrap), defined once. The eval string clicks #next-btn and
returns the position in one in-page task, so no 100 ms timer tick
can land between reset and read. Soundness proof, checked in the
driver rather than assumed:

- WD.eval posts the script as-is to /execute/sync
  (run_live.py line 587). Marionette runs it as a function body,
  so the mid-script `return` after the click statement is valid;
  run_live.py lines 204-210 state the same top-level-return rule
  and every value-returning script in the file relies on it.
- Fail-closed: a None or non-numeric result raises RuntimeError
  inside the r.step lambda; Runner.step records the failure and
  raises, so the test aborts as a failure, never passes on a bad
  read. int() conversion of a float is exact for 0. A NaN result
  would raise ValueError from int(), also a recorded failure.
- The frozen exact-zero reads (3 more sites, == 0 each) use plain
  d.click plus a separate read, which is correct because the clock
  is stopped while paused. Total exact-zero == 0 checks: 6, same
  as the checker.
- Sampler: 500 ms window, 10 ms interval, min returned, started
  before the now-playing assert on both sides. Fail-closed on
  non-numeric. An Infinity min (element missing, NaN never below
  min) passes the isinstance gate but fails the <= 2 check, same
  as the checker (Infinity > 2 pushes a failure). No pass path
  on a broken read.

## 4. D1 probe removal is correct

Parent version (f732d6a^) had a supplementary D1 probe after the
final pause: click Next while paused, read position, store in
r.details["D1_exact_zero_probe"], print a [D1] line. It was
details-only, never a pass/fail check. The new checker carries
real frozen-Next exact-zero steps (mid-list, shuffle, wrap), so
the probe is superseded. git grep for D1_exact_zero_probe at
f732d6a returns nothing; no other code references the details
key; the only D1 mentions left in run_batch3.py are the removal
NOTE, the unrelated spreadsheet D1 cells in another test, and a
preflight comment. Keeping the probe would have double-driven
Next after the suite final pause. Removal is correct and complete.

## 5. Sleeps match, in position as well as count

Runner: time.sleep(0.7) x3, 0.5 x1, 0.4 x1, 0.35 x10. Checker:
sleep(700) x3, sleep(500) x1, sleep(400) x1, sleep(350) x10.
Placement matches site by site: 0.7 after play, 0.4 after the
first frozen read, 0.5 after resume, 0.35 x2 per advancing block
(plain, frozen resume, shuffle advancing, frozen shuffle resume,
frozen wrap resume), 0.7 before each wrap Next. Details keys:
25 in the checker, 25 in the runner, identical sets.
py_compile on the f732d6a file passes. Diff hunks outside
run_b3_t10 (header docstring, pathlib import, preflight, run_one,
launch_gate) touch no t10 helper; press_keys, _rect_of,
pointer_click_at, type_empty are unchanged by this commit.
Seek click coordinates are the progress bar center on both sides
(x + w*0.5, y + h/2); the fallback d.click("#progress") also
clicks the center. Fixture cross-checks: Morning Light duration
180, so 50% seek reads 90, inside 85..100; shuffle queue from
Morning Light is [0,4,3,2,1], so listed[1] is Mountain Air,
shuffle Next is Mountain Air, frozen shuffle Next is City Rain;
nextTrack and prevTrack both reset position to 0; timer is 1
simulated second per 100 ms real time, so 700 ms reads about 7
and 350 ms gains about 3 ticks, inside every bound used.

## 6. Watch item for the live run (not a defect, no fix demanded)

Timing margin on the middle advancing read (2..11). The checker
runs its sampler promise concurrently with the now-playing assert,
so its after-sampler read lands about 500 ms after the click and
its advancing read about 850 ms after, about 8 ticks. The runner
serializes: the sampler eval blocks 500 ms, then the now-playing
text read, then the after-sampler read, then 350 ms, then the
advancing read. That adds roughly 1-2 Marionette round trips,
so the runner advancing read should land near 8-10 ticks, still
inside 2..11 with at least 1 tick of margin in the plausible
case. Only pathologically slow round trips (over about 300 ms
each) would push it to 12. The live run should watch
details.positionAdvancingAfterNext and
details.positionAdvancingAfterShuffleNext: if either reads 11
repeatedly, tighten by reading after_sampler before the
now-playing text check (check order is unaffected, the
after-sampler read is a step, not a check). I do not demand that
reorder now; the translation is faithful and the live run is the
proper judge.

## 7. Honest notes

- Log count staleness: the Y14b log says "68 ordered assert
  alignments", but the current /tmp/y14b-transcribe.py reports 72
  PASS order lines. I re-derived 72 independently (69 checker
  asserts + 3 volume extras), so the log number is stale, not
  the diff. The diff is fine.
- Step-abort semantics: a fail-closed raise inside exact_zero_next
  or the sampler aborts t10 at that step (Runner.step raises)
  instead of collecting the remaining asserts the way the checker
  would. That is pre-existing runner-wide behavior, not introduced
  by this diff. Noted, not a defect.
- This review is static plus mechanical script runs. The runner
  was not driven live here, so live behavior (round-trip times,
  the section 6 margin) is still to be proven by the live run.

## Timings (Asia/Ho_Chi_Minh)

- Task received 21:13:15. Review started 21:13.
- Transcribe script run 21:14, exit 0, 82 PASS lines (72 order
  + 10 structural), 0 failures.
- Independent enumeration, fixture check, driver check 21:14-21:17.
- Paper written and committed 21:17.
