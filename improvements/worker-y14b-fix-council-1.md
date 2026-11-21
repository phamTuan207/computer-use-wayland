# Council Voice 1: Y14b fix pass review, t10 translation fix only

## Verdict: GO

The fix diff does exactly the two t10 changes it claims, no more, no
less. Every check in my scope passes with file and line evidence
below. The H4 margin is arithmetically as claimed, but it is still
thin by redteam's own 3 tick bar, and the laptop re-measurement has
not happened yet. That residual thinness was adjudicated, not hidden
(margin analysis recorded instead of re-derived caps, plan watch item
in place), so it does not block this diff. The live run must watch the
two advancing details as the plan already requires.

## Scope and a correction to the brief

Scope: the FIX DIFF ONLY for `run_b3_t10` in
`tests/realistic/run_batch3.py`, commit `8bee524`, plus `ebe5853`
(log hash record only). I did not re-review the rest of the runner
(H2/M1/M2/M3) or the original re-stage.

Correction: the brief says `8bee524` vs "its parent `f732d6a`". That
is not the git parent. Direct parent of `8bee524` is `431b2a9`
(Y13f log commit); `f732d6a` is the re-stage ancestor. This changes
nothing for my scope: `run_batch3.py` is byte-identical between
`f732d6a` and `431b2a9` (0 line diff), and the two diffs
`f732d6a..8bee524` and `431b2a9..8bee524` for that file are
byte-identical (289 lines each, `diff` of the two diffs empty).

`ebe5853` touches only `improvements/worker-y14b-restage-log.md`
(6 lines). Its recorded hashes verify exactly against the fix
commit: `git show 8bee524:tests/realistic/run_batch3.py` gives blob
`ed4de81d914f3a75df31554c0b2369110f7e27b0` and md5
`65818867865ad4772e78cc2bcac015d6`, matching the log entry.

## Check 1: the t10-only diff is exactly the two claimed changes

Command: extract `run_b3_t10` from `f732d6a` and from HEAD and diff
the bodies. Result: 4 hunks, nothing else.

1. `position()`, new L1472-1480: `return int(d.eval(...))` became
   `return d.eval(...)`, with a comment citing redteam L1.
2. `exact_zero_next()`, new L1512-1527: `return int(result)` became
   `return result`, same L1 comment.
3. River Road now-playing assert removed from between the sampler
   and the min check (old hunk `@@ -1563,8`) and added after the
   advancing-later gain check, new L1610-1611, with an H4
   alternative (c) comment.
4. Mountain Air now-playing assert removed from between the shuffle
   sampler and its min check (old hunk `@@ -1694,8`) and added after
   the shuffle advancing-later gain check, new L1749-1750, same
   comment.

Net t10 change: +19 lines, all of it the two moves plus explanatory
comments. No other t10 line changed.

## Check 2: assert set vs check.mjs at main 1d23532

`git show 1d23532:tests/realistic/clone1-batch3/t10-music-player/check.mjs`
gives 353 lines, md5 `c55ef3c792b2faaea7c829818eb6420b`, as briefed.

Independent count (my own extraction, not the transcribe script):
check.mjs has 33 `expectText` calls and 36 `failures.push` calls,
69 asserts. The runner t10 has 33 `expect_text` calls and 39
`r.check` calls, 72 asserts, before and after the fix (multisets
equal old vs new).

Mapping, order-insensitive (order differs only by the two moves):

- `expectText`: selector plus expected value identical 33/33.
  One label-only wording difference, pre-existing in the re-stage,
  not introduced by this fix: runner `repeat All before wrap` vs
  check.mjs `repeat All before wrap test` (same selector
  `#repeat-btn`, same value `Repeat: All`).
- `failures.push` vs `r.check`: 36/36 matched after removing the 3
  runner-only volume value checks below. 29 match on distinctive
  tokens directly; 7 match as polarity pairs (check.mjs failure
  wording vs runner check label, same proposition): `did not
  advance` vs `advanced` (3 pairs), `did not gain` vs `gained`
  (3 pairs), `moved while paused` vs `frozen while paused`
  (1 pair).

Qualifier on the word "identical": the runner set is a superset,
not a strict equal. The 3 extra runner checks (`volume 50 after
click`, `volume 0 after Home`, `volume 30 after arrows`, new
L1666-1680 area) read `d.value('#volume')`; check.mjs never reads
`#volume` value, it only asserts `#volume-value` text `30`. These
3 extras predate the fix (present in `f732d6a`, Council 1 recorded
the translation as 69/69 covered). The fix diff adds and removes no
assert, so the qualifier is a re-stage property, not a fix defect.
I record it so the "identical" claim is not overstated.

## Check 3: no threshold changed

Numeric literals in the t10 body are identical old vs new (sorted
set comparison, empty difference both ways). The `2..11` bounds sit
at new L1593 and L1735, untouched. The gain thresholds
(`>= 2`, new L1599, L1743), sampler threshold (`min <= 2 and
min < pos_before`), exact-zero (`== 0`), seek range (`85..100`),
and volume values are all unchanged. `py_compile` and `ast.parse`
on the new file pass.

## Check 4: the moved asserts still prove the same thing

Between the Next click and the moved assert, the only intervening
steps are position reads (evals) and sleeps. Nothing in that window
clicks Next, Prev, or a playlist track, so nothing can change the
track name. Fixture proof (`fixture.html` at `1d23532`, md5
`eb814c944dab6279417c6182e1950876`): `nextTrack()` sets
`position = 0` and calls `render()` synchronously, and `render()`
sets `nowPlaying.textContent` synchronously (L113-125, L66-69). The
name is therefore fixed from the click onward, and an assert at
about 1.2 s after the click proves the same proposition as one at
about 0.5 s, on this fixture.

Precision note: in principle the moved assert proves "name correct
at about 1.2 s" rather than check.mjs's "name correct within the
500 ms sampler window". No defect class on this fixture
distinguishes those two, because the name update is synchronous in
the click handler. I note the weaker timing bound for accuracy; it
is not a finding against the fix, which implements redteam H4
alternative (c) exactly as adjudicated.

Also exact: the permutation is minimal. Each moved assert jumps
over only `r.check` calls (min check, gain and range checks). No
other `expect_text` sits between the old and new positions, so the
`expect_text` subsequence order is unchanged, and the `r.check`
subsequence order is unchanged.

## Check 5: int() removal cannot false-pass exact-zero

Zero `int()` code calls remain in t10. The 2 remaining `int(`
matches in the t10 body are inside the new comments ("no int()
truncation"). The old calls were `return int(d.eval(...))` (old
L1473) and `return int(result)` (old L1521); both are gone.

Both readers keep their fail-closed guards: non-numeric results
still raise (`isinstance(result, (int, float))`, new L1508-1510 and
L1523-1526), never default to 0. A fractional read can no longer
truncate to 0: `0.5` now returns `0.5` and fails `== 0`, where the
old code returned `0` and passed. That is the whole point of L1.

No live value changes on this fixture. Fixture proof: `position`
is an integer throughout (`position += 1` in the 100 ms interval,
`position = 0` on reset, `Math.round(...)` on seek, fixture
L88-94, L178), and `dataset.seconds = String(position)` (L69).
`Number()` of that string is always an integer, so `int()` was a
no-op on every live read and removing it changes no value.

## Check 6: frozen Nexts' now-playing asserts stayed in place

The t10 diff touches no frozen assert. Verified by line:

- Night Drive after frozen next: old L1614, new L1629.
- City Rain after frozen shuffle next: old L1750, new L1768.
- Wrap Morning Light (playing): old L1826, new L1845.
- Wrap Morning Light (paused): old L1859, new L1878.

Line shifts are +15 to +19 from the added comment lines above
them; relative order and wording unchanged.

## Check 7: transcribe script re-run

Command: `python3 /tmp/y14b-transcribe.py` (updated for the new
order; its ORDERED list places River Road after the advancing-later
gain check and Mountain Air after the shuffle advancing-later gain
check). Result: 72 order PASS plus 10 structural PASS, 82 PASS
total, 0 failures, exit 0, 0.045 s. The structural checks cover:
D1 probe removed, `exact_zero_next` 3 call sites and 1 definition,
sleep counts 0.7 x3, 0.5 x1, 0.4 x1, 0.35 x10, sampler
fail-closed, sampler threshold.

I read the script before relying on it. Its ordered check is
`T10.find(needle, pos + 1)` with strictly increasing positions,
sound for an ordered-subsequence check. Its needles are exact
quoted labels, so the River Road needle cannot match the shuffle
label or the exact-zero labels.

## Check 8: H4 margin, arithmetic and plain judgment

Transport facts re-verified, not taken on trust:

- `d.text(css)` is find (1 POST) plus GET text (1 POST), 2 round
  trips (`run_live.py` L800-802). `d.eval` is 1 POST (L587-589).
  The "2 round trips" claim for the moved assert and the "5 round
  trips" old-path count (sampler flight 1, find 1, text 1,
  afterSampler read 1, advancing read 1) are correct.
- Y11b proof file `tests/realistic/live-run-y11b-proof-20261121.jsonl`
  (76 rows), recomputed by me: eval n=3, median 1.5 ms (plan says
  about 2 ms, correct). Genuine WD.click steps n=20, median 58.4 ms,
  p90 59.2 ms. The other 26 `op=click` rows are eval-driven press
  steps at 1.3 to 3.4 ms, not WD clicks. Redteam's "click steps
  median about 56 ms" is the genuine-click median, slightly
  understated (58.4), and its "round trip roughly 5 to 20 ms"
  follows from 58.4 ms over about 3 POSTs, about 19.5 ms each.
  Note the tension: eval POSTs measure about 1.5 ms while click
  POSTs imply about 19 ms each, so the click cost is mostly
  scroll and actionability work, not pure round trip time. For the
  advancing path, which uses only evals, the eval rate is the
  operative one.

Margin model, reset to advancing read: sampler 500 ms plus sleep
350 ms is 850 ms of playing, plus round trips. The fixture ticks
once per 100 ms, and `nextTrack()` does not restart the timer, so
the tick phase is arbitrary and the value at a given elapsed time
is 8 or 9 by phase.

- Old path, 850 ms + 5 round trips. Redteam sim: RTT 0 gives 8,
  10 gives 9, 25 gives 9, 50 gives 11 (zero margin), 75 gives 12
  (FAIL). I reproduce these numbers from the model
  floor((850 + 5*RTT)/100): 850, 900, 975, 1100, 1225 ms.
- New path, 850 ms + 3 round trips. Same model: RTT 2 ms gives
  856 ms (8.56 ticks, value 8 or 9, discrete margin 2 or 3,
  continuous margin 2.44 at 8.56). RTT 19 ms gives 907 ms (9.07
  ticks, value 9, discrete margin 2, continuous margin 1.93).
- The brief's "~2.4 ticks margin" is the fast-end continuous
  figure: 11 - 8.56 = 2.44. The plan's "about 8-9, margin ~2 ticks"
  is the fair summary across the measured rate range. The move
  buys 2*RTT/100 ticks: 0.04 at 2 ms, 0.38 (about 0.4) at 19 ms,
  matching the plan's "buying ~0.4 ticks" at the slow end.
- New path at higher RTTs (my recomputation): RTT 50 ms gives
  1000 ms, value 10, margin 1. RTT 100 ms gives 1150 ms, value 11,
  zero margin. RTT 150 ms gives 1300 ms, value 13, FAIL.

Plain judgment: the arithmetic is sane, and the move helps, but
the margin is STILL THIN. It does not meet redteam unblock (c)'s
"at least 3 ticks of margin" alternative. The fix took the other
branch of (c) (move, then re-measure), and the re-measure has not
happened: the runner is not yet shipped to the laptop and not yet
run (plan: "Not yet shipped to the laptop, not yet run"), and the
Y11b rates come from a quiet 2-test run, not a loaded 10-test
batch. At quiet-machine rates the margin is 2 ticks in the adverse
phase. Under load, at 50 ms round trips it falls to 1 tick, and at
100 ms it is gone. A correct fixture failing t10 under load would
be misread as a fixture failure and could burn the slot.

Why this is still GO and not AMEND: the residual thinness was
adjudicated (caps not re-derived in the runner, margin analysis
recorded instead), and the plan already carries the correct
tripwire: watch `details.positionAdvancingAfterNext` and
`details.positionAdvancingAfterShuffleNext`, and if either reads 11
repeatedly, report the thin margin explicitly instead of calling it
a fixture failure outright (plan L616-627). I checked whether the
frozen resume later reads need the same tripwire: they do not. They
sit on a lower base (about 700 ms plus the resume click), read
about 8 at 19 ms round trips (margin 3) and 11 at 100 ms (zero),
so the playing advancing reads are the binding constraint, tied at
worst. Watching the two playing details suffices. Ship condition:
the live run performs the re-measurement redteam (c) requires, and
the watch item is honored.

## Hygiene

Fix diff for `run_batch3.py`: 0 em dash (U+2014), 0 en dash
(U+2013), 0 mentions of ydotool (counted with Python on the diff
text; an earlier shell grep count of 197 was a quoting artifact,
re-checked and corrected). No personal info in the diff. No live
Zen driving was done for this review.

## Timed work log (Asia/Ho_Chi_Minh, 21/11)

- 21:33: task received. Fetch origin, confirm HEAD `ebe5853` on
  `todolist-push`.
- 21:33-21:34: scope diff. Found the parent-label correction
  (`431b2a9`, not `f732d6a` as direct parent) and proved the
  `run_batch3.py` diff identical either way.
- 21:34: check.mjs at `1d23532` verified (353 lines, md5
  `c55ef3c792b2faaea7c829818eb6420b`).
- 21:34-21:35: read `run_b3_t10` in full; t10-only diff, exactly
  4 hunks; assert inventory old vs new.
- 21:35-21:36: Y11b jsonl recompute (eval median 1.5 ms, genuine
  click median 58.4 ms); redteam H4 sim reproduced from the model.
- 21:36: transcribe script re-run, 82 PASS, 0 failures, 0.045 s.
  Fixture integer and synchronous-render proof.
- 21:36-21:37: check.mjs multiset mapping (69/69 plus 3 volume
  extras), frozen asserts, `py_compile`, dash and ydotool counts.
- 21:37-21:40: paper written, committed, pushed, verified.

## Commit

Paper: `improvements/worker-y14b-fix-council-1.md` on
`todolist-push`. Commit hash filled below after push.
