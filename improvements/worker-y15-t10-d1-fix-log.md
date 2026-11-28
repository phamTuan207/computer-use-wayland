# Worker Y15 log: fix defect D1 in t10-music-player

Worker: Y15 (Muse test fixer). Parent: main coordinator agent.
Date: Sat 2026-11-21. All times UTC unless marked +07.
Suite commit landed: 1d23532
("t10-music-player: assert exact-zero reset and clock liveness on Next paths (fix D1)").
Base suite commit: ed78e83 (Y10 merged clone1-batch3 suite).
Worktree: ~/workspace/cu-jpegq90-land (branch main).

## Task

Fix ONE narrow defect in the merged clone1-batch3 suite, verify it,
run a council (1, focused) plus redteam on the fix, land on main,
and state the new suite commit so Y14 can target it for its live run.

## Defect D1 (from Y12 verification)

Y12 independently verified Y10's merged suite as SOUND WITH NOTED
DEFECTS (log improvements/worker-y12-batch3-verify-log.md, commit
897ca17 on todolist-push; 10/10 x3 sequential plus 10/10 load, 11/12
mutation probes matched). The one executed defect:

- D1 (minor, narrow): the t10-music-player checker,
  tests/realistic/clone1-batch3/t10-music-player/check.mjs, accepted
  a nextTrack resetting position to 1 (or 2, or a reset delayed
  under 500 ms) because the 500 ms in-page sampler only required
  minAfterNext <= 2. The checker never asserted the reset value its
  own README states. Y12 probe t10-P2 (reset-to-1) expected FAIL,
  got PASS, exit 0.
- Remedy (Y12 council t10, already debated): add an exact-zero
  assertion on a clock-frozen path (pause before Next, require
  exactly 0, resume, keep the advancing check). Verify by re-running
  P2 (must FAIL) plus 3x positive full-suite runs (must be 10/10).

Scope: only tests/realistic/clone1-batch3/t10-music-player/check.mjs
and README.md changed. t05 and t09 untouched throughout. Fixture
fixture.html NOT modified. No em dash, no en dash, no personal info
in either file (verified by grep, 0 hits, after every round).

## Environment for every run

Headless Playwright Chromium on the VM. Env prefix for every run:

  PLAYWRIGHT_CORE_PATH=/tmp/y12-scratch/node_modules/playwright-core CHROMIUM_PATH=~/.cache/ms-playwright/chromium-1187/chrome-linux/chrome node <script>

run_all.mjs writes results.json; it was restored with git checkout
after every suite run. All runs timed (wall-clock UTC plus elapsed).

## What the checker does now (final state, commit 1d23532)

Fixture: demo music player, 5 tracks, 1 simulated second per 100 ms
while playing; nextTrack sets position = 0; pause stops the timer;
Play restarts it via startTimer().

1. Same-task exact-zero read after every playing Next (plain step 6,
   shuffle step 11, playing wrap step 15): the click and the read run
   in one page.evaluate task, so no timer tick can land between reset
   and read (page JS is single-threaded, handler runs synchronously).
   Requires exactly 0.
2. Sampler kept as second witness on all three playing Nexts: 500 ms
   in-page sample, minimum must be <= 2 AND below the pre-click value.
   Factored into a shared sampleMin() helper.
3. Three-point advancing checks after the plain Next and the shuffle
   Next: read at sampler end (about 5), after a 350 ms sleep (about 8),
   after another 350 ms sleep (about 12); require gain >= 2 across
   EACH sleep; absolute 2-11 bound on the middle read.
4. Frozen exact-zero checks: step 7 (paused Next to Night Drive,
   exact 0), step 11 paused shuffle Next (to City Rain, exact 0, then
   Prev back to Mountain Air), step 15 frozen wrap Next (to Morning
   Light, exact 0). Each preceded by a 700 ms wait after the playlist
   click so the pre-click position is clearly nonzero (asserted >= 2).
5. Two-point resume reads after every frozen resume (steps 7, 11, 15):
   sleep 350 ms, require 2-11; sleep another 350 ms, require gain
   >= 2 AND 2-11. Placed before any playlist click that could restart
   the timer and mask a dead Play.
6. README decisions recorded: Prev position deliberately NOT asserted
   (spec only requires Previous to change the track); clock-rate limits
   documented honestly (1.5x and faster caught, 1.3x intermittent,
   1.2x not distinguished, slow side 0.6x to 1.0x not distinguished,
   slower than about 0.6x caught by the gain floor; later advancing
   read gain-only with no upper bound, so a clock that speeds up after
   the middle read is not caught; second resume reads do carry the
   2-11 bound, so a speedup after a frozen resume is caught; no
   advancing check follows the playing wrap Next, so a timer that
   stops on the wrap path is masked by the next playlist click and is
   a known gap); final documented limit: the checks observe the clock
   at three points spanning about 1.2 s after each advancing-checked
   Next (plain step 6 and shuffle step 11) and at two points spanning
   about 700 ms after each frozen resume (steps 7, 11, 15); a defect
   that starts after the final observation cannot be caught by any
   finite test, and that is the documented limit, not a hole to chase
   with a fourth point.

Final diff vs ed78e83: 2 files, +300/-37 (check.mjs +213/-27,
README.md +87/-10). t10 standalone runtime about 10.2-10.5 s
sequential, about 13.0-13.2 s under 3-way parallel load.

## How the fix grew, round by round

### Round 1 (D1 proper)

Frozen exact-zero as a second Next after the playing-path sampler
plus advancing check. Design choice, debated and kept: the frozen
check runs as a SECOND Next, NOT by pausing before the first Next,
because pausing before the first Next and resuming with Play would
restart the timer and hide a nextTrack that stops the clock
(probe P4); the advancing check is the only witness for that defect.
Baseline reproduced 12:35 UTC 21/11: old checker vs Y12 P2 fixture,
exit 0, pass true, positionMinAfterNext 1. With the round-1 fixed
checker, exit 1, "position not exactly 0 after next while paused: 1".
Council APPROVED. Redteam BLOCKED on N1 (wrap branch no-reset
escapes) and N4 (double clock speed escapes, advancing check
one-sided).

### Round 2

Frozen wrap check plus 700 ms pre-wrap wait plus advancing bound
2-12. N1 first still escaped because the pre-wrap position was about
0 (Mountain Air click had just reset it); fixed by the 700 ms wait
plus >= 2 gate. Council APPROVED. Redteam BLOCKED on M2 (wrap
resets only when paused escapes; checker only wrapped while paused),
M3 (Next no-reset while shuffle on escapes; step 11 asserted only
the track name), M4 (1.5x clock escapes intermittently at bound 12;
correct 8-9, mutant 12-13).

### Round 3

Playing wrap (sampler) plus frozen wrap, shuffle Next sampler,
advancing bound tightened 12 to 11, Prev non-assertion documented.
sampleMin() helper factored out (behavior-identical, verified by
round-3 council: old inline sampler vs helper differ by exactly one
line). Council APPROVED. Redteam BLOCKED on E1 (shuffle Next resets
to 1; sampler tolerance, no frozen follow-up), E2 (wrap resets to 1
only while playing; playing-only wrong value), E3 (shuffle Next
stops the timer; no advancing check after it, masked by step 14
playTrack restart), E4 (1.2x clock inside the correct range; needs
a longer window, not a bound tweak).

### Round 4

Shuffle Next given the full first-Next pattern (sampler plus
advancing plus paused shuffle Next with exact-zero plus Prev back to
Mountain Air); E2/E4 documented as known limits. Council REJECTED
narrowly on F1 (the E2 "cannot be caught" claim is false; same-task
evaluate-click proof) plus F2 low (steps must state both sampler
conditions). Redteam BLOCKED on G1 (shuffle timer dies 600 ms after
the click; absolute advancing read passes), G2 (Play after frozen
shuffle Next does not restart the timer; no position read follows
that resume), G5 (same hole on the frozen wrap resume), G3 (1.3x
caught 3/3 at advancing 12, strongest attack that failed that
round), G4 control (paused shuffle reset to 1, caught).

### Round 5

Same-task exact reads on all three playing Nexts (F1), delta
advancing checks (G1), resume reads after every frozen resume
(G2/G5), F2 README wording, E4 documented. Council APPROVED (E2/G1/G2
re-run and closed; G3 failed on its run, confirming 1.3x
intermittency). Redteam BLOCKED on H1 (timer dies 750 ms after the
first playing Next, about 240 ms into the 350 ms delta sleep; gain
exactly 5 to 7; falsifies the Notes sentence "a timer that dies
part-way through the window fails"), H2 (timer dies 250 ms after
the frozen wrap resume Play; resume read exactly 2; step 15 has no
downstream position witness), H3 (supporting: clock 3x fast only
after the frozen wrap resume; resume read 10; does not contradict
the Notes 1.5x sentence, which is scoped to the 850 ms window).
H4 control (untrusted evaluate-click skips the reset) was CAUGHT on
the first playing Next, proving the same-task click design survives
synthetic-click discrimination.

Probe matrix (grew each round): Y12 P1-P4, round-1 N1-N4, round-2
M1-M5, round-3 E1-E5, round-4 G1-G5, round-5 H1-H4. Mutant dirs:
/tmp/y12-mutations/, /tmp/y15-rt/, /tmp/y15b-rt/, /tmp/y15e-rt/,
/tmp/y15g-rt/, /tmp/y15i-rt/ (each a full suite copy with one
fixture break; the current fixed check.mjs swapped in verbatim
before running). Latest full matrix (round-5 checker, 23 probes,
completed about 13:13 UTC 21/11): all FAIL except N2 (Prev
no-reset, PASS by design), E4 (1.2x, documented limit), G3 (1.3x,
passed that run; caught 3/3 by round-4 redteam, intermittent, as
documented). Notable: E2 FAIL ("position not exactly 0 after
playing wrap next while playing: 1"), G1 FAIL ("position did not
gain after shuffle next while playing: 5 to 6"), G2 FAIL (resume 0),
G5 FAIL (resume 0), P2 FAIL (exact 1 on all four reads), M4 FAIL
5/5 (advancing 12-13 at bound 11).

### Full suite sequential 10/10, exit 0, every round

- Round 1: 24965/24148/24556 ms (t10 about 4.6 s).
- Round 2: 25001/23984/24660 ms (t10 about 5.5-6.1 s).
- Round 3: 28333/28746/27127 ms (t10 7.2-7.6 s).
- Round 4: 27339/25822/26669 ms (t10 7.8-8.1 s).
- Round 5: 29787/27368/26269 ms (t10 8.3-8.6 s).
- Load (3 parallel full suites): 10/10 each in rounds 1-5; no flake
  found in any round. Correct advancing values observed 8-10 (max 10
  once, in a P2 run); correct gains 3-4; correct resume reads 3
  (round-5 council noted one tick of margin on the resume floor, no
  flake observed).

Reviewers: 10 child agents total across rounds 1-5 (council plus
redteam per round). Reports in /tmp/y15-council.md,
/tmp/y15-redteam.md, /tmp/y15b-council.md, /tmp/y15b-redteam.md,
/tmp/y15e-council.md, /tmp/y15e-redteam.md, /tmp/y15g-council.md,
/tmp/y15g-redteam.md, /tmp/y15i-council.md, /tmp/y15i-redteam.md
(round 5).

### Round 6 (final fix round)

Three-point advancing checks plus two-point resume reads (H1/H2/H3
fixes); README Notes corrected (three-point deltas, two-point
resumes, final documented limit). Stopping rule set by Y15 before
round 6: round 6 is the LAST fix round. After it, land regardless;
any new round-6 finding is recorded as a follow-up in the log unless
it breaks P2-must-FAIL or 3x-10/10 or contradicts a README assertion
that cannot be fixed with a one-line doc correction. The principled
basis: the residual blind spot is "after the last observation",
unobservable by any finite test.

## Round-6 verification

### 27-probe matrix, round-6 checker

Launched about 13:39 UTC 21/11 as background exec session
proc_afc404202192, completed about 13:44 UTC, wall 283080 ms,
exit 0. Command: copy each mutant dir to /tmp/y15j/<probe>, swap
in the current fixed check.mjs verbatim, run
t10-music-player/check.mjs with the env prefix above, print exit
and failures. Probes: P1-P4, N1-N4, M1-M5, E1-E5, G1-G5, H1-H4.

Verbatim output:

  P1: exit 1 | failures: ['position not exactly 0 after next while playing: 12', 'position not reset after next: min observed 12 after 12', 'position after next while playing out of range 2-11: 20', 'position not exactly 0 after next while paused: 24', 'position did not advance after resume from frozen next: 27', 'position after resume from frozen next out of range 2-11: 31', 'position not exactly 0 after shuffle next while playing: 90', 'position not reset after shuffle next: min observed 90 after 90', 'position after shuffle next while playing out of range 2-11: 99', 'position not exactly 0 after shuffle next while paused: 103', 'position did not advance after resume from frozen shuffle next: 106', 'position after resume from frozen shuffle next out of range 2-11: 110']
  P2: exit 1 | failures: ['position not exactly 0 after next while playing: 1', 'position not exactly 0 after next while paused: 1', 'position not exactly 0 after shuffle next while playing: 1', 'position not exactly 0 after shuffle next while paused: 1']
  P3: exit 1 | failures: ['position not exactly 0 after next while playing: 12', 'position not reset after next: min observed 12 after 12', 'position after next while playing out of range 2-11: 20', 'position not exactly 0 after shuffle next while playing: 91', 'position not reset after shuffle next: min observed 91 after 91', 'position after shuffle next while playing out of range 2-11: 99']
  P4: exit 1 | failures: ['position did not gain after next while playing: 0 to 0', 'position after next while playing out of range 2-11: 0', 'position did not gain again after next while playing: 0 to 0', 'position did not gain after shuffle next while playing: 0 to 0', 'position after shuffle next while playing out of range 2-11: 0', 'position did not gain again after shuffle next while playing: 0 to 0']
  N1: exit 1 | failures: ['position not exactly 0 after playing wrap next while playing: 7', 'position not reset after playing wrap next: min observed 7 after 7', 'position not exactly 0 after wrap next while paused: 7', 'position after resume from frozen wrap next out of range 2-11: 14']
  N2: exit 0 | failures: []
  N3: exit 1 | failures: ['position not exactly 0 after next while playing: 12', 'position not exactly 0 after next while paused: 9', 'position did not advance after resume from frozen next: 1', 'position not exactly 0 after shuffle next while playing: 90', 'position not exactly 0 after shuffle next while paused: 9', 'position did not advance after resume from frozen shuffle next: 1']
  N4: exit 1 | failures: ['position after next while playing out of range 2-11: 16', 'position after resume from frozen next out of range 2-11: 14', 'position after shuffle next while playing out of range 2-11: 18', 'position after resume from frozen shuffle next out of range 2-11: 14', 'position after resume from frozen wrap next out of range 2-11: 14']
  M1: exit 1 | failures: ['position not exactly 0 after playing wrap next while playing: 1', 'position not exactly 0 after wrap next while paused: 1']
  M2: exit 1 | failures: ['position not exactly 0 after playing wrap next while playing: 7', 'position not reset after playing wrap next: min observed 7 after 7']
  M3: exit 1 | failures: ['position not exactly 0 after shuffle next while playing: 91', 'position not reset after shuffle next: min observed 91 after 91', 'position after shuffle next while playing out of range 2-11: 99', 'position not exactly 0 after shuffle next while paused: 103', 'position did not advance after resume from frozen shuffle next: 106', 'position after resume from frozen shuffle next out of range 2-11: 110']
  M4: exit 1 | failures: ['position after next while playing out of range 2-11: 13', 'position after shuffle next while playing out of range 2-11: 12']
  M5: exit 1 | failures: ['position not exactly 0 after playing wrap next while playing: 7', 'position not exactly 0 after wrap next while paused: 7', 'position did not advance after resume from frozen wrap next: 1']
  E1: exit 1 | failures: ['position not exactly 0 after shuffle next while playing: 1', 'position not exactly 0 after shuffle next while paused: 1']
  E2: exit 1 | failures: ['position not exactly 0 after playing wrap next while playing: 1']
  E3: exit 1 | failures: ['position did not gain after shuffle next while playing: 0 to 0', 'position after shuffle next while playing out of range 2-11: 0', 'position did not gain again after shuffle next while playing: 0 to 0']
  E4: exit 0 | failures: []
  E5: exit 1 | failures: ['position did not advance before playing wrap next: 0', 'position not reset after playing wrap next: min observed 0 after 0', 'position did not advance before frozen wrap next: 0']
  G1: exit 1 | failures: ['position did not gain after shuffle next while playing: 5 to 6', 'position did not gain again after shuffle next while playing: 6 to 6']
  G2: exit 1 | failures: ['position did not advance after resume from frozen shuffle next: 0', 'position did not gain again after resume from frozen shuffle next: 0 to 0', 'position after resume from frozen shuffle next out of range 2-11: 0']
  G3: exit 0 | failures: []
  G4: exit 1 | failures: ['position not exactly 0 after shuffle next while paused: 1']
  G5: exit 1 | failures: ['position did not advance after resume from frozen wrap next: 0', 'position did not gain again after resume from frozen wrap next: 0 to 0', 'position after resume from frozen wrap next out of range 2-11: 0']
  H1: exit 1 | failures: ['position did not gain again after next while playing: 7 to 7']
  H2: exit 1 | failures: ['position did not gain again after resume from frozen wrap next: 2 to 2']
  H3: exit 1 | failures: ['position after resume from frozen wrap next out of range 2-11: 21']
  H4: exit 1 | failures: ['position not exactly 0 after next while playing: 12', 'position not reset after next: min observed 12 after 12', 'position after next while playing out of range 2-11: 20', 'position not exactly 0 after shuffle next while playing: 92', 'position not reset after shuffle next: min observed 92 after 92', 'position after shuffle next while playing out of range 2-11: 100']

Summary: 24 FAIL plus 3 expected PASS. N2 PASS by design (Prev
position deliberately not asserted). E4 PASS, documented limit
(1.2x clock). G3 PASS, 1.3x intermittent, documented as either
outcome fits. H1 FAILs "did not gain again after next while
playing: 7 to 7" (second gain 0, exactly as designed). H2 FAILs
"did not gain again after resume from frozen wrap next: 2 to 2".
H3 FAILs resume second read 21 > 11. H4 FAILs on the first playing
Next. P2 (D1) FAILs with exact 1 on all four reads.

### Full suite 3x sequential, round-6 checker

Worktree run_all.mjs, starts 13:44:31, 13:45:00, 13:45:30 UTC.

- Run 1: 10 passed, 0 failed, wall clock 29504 ms, run wall 29 s.
  t10 10204 ms.
- Run 2: 10 passed, 0 failed, wall clock 29421 ms, run wall 30 s.
  t10 10503 ms.
- Run 3: 10 passed, 0 failed, wall clock 29730 ms, run wall 30 s.
  t10 10410 ms.

All exit 0. results.json restored with git checkout after each run.

### Load: 3x parallel full suites

Three fresh copies in /tmp/y15k-load, launched together, wall 65 s,
all finished 13:47:09 UTC, exit 0 each:

- run1: 10 passed, 0 failed, wall clock 65608 ms, t10 13073 ms.
- run2: 10 passed, 0 failed, wall clock 65640 ms, t10 13023 ms.
- run3: 10 passed, 0 failed, wall clock 65316 ms, t10 13233 ms.

No flake. Leftover chrome processes observed after runs were
transient shutdown remnants (each checked PID gone within seconds;
final check: no chrome, no node test processes left).

### Final confirmatory suite run (after the last README edit)

Start 13:59:45 UTC, wall 31 s: 10 passed, 0 failed, wall clock
30752 ms, t10 10360 ms, exit 0. Doc-only change; checker identical
to the 3x runs (verified: check.mjs untouched since the 3x runs).

## Round-6 council: APPROVE

Report: /tmp/y15k-council.md. Verdict APPROVE. Verified by execution:

- H1 (timer dies 750 ms after first playing Next): FAIL, exit 1,
  13:49:09-13:49:20Z, 11 s, single failure "position did not gain
  again after next while playing: 7 to 7" (details 5 to 7 to 7).
- H2 (timer dies 250 ms after frozen wrap resume): FAIL, exit 1,
  13:49:24-13:49:35Z, 11 s, single failure "position did not gain
  again after resume from frozen wrap next: 2 to 2" (first read 2
  passes 2-11, so the second read is the catcher).
- H3 (3x clock after frozen wrap resume): FAIL, exit 1,
  13:49:41-13:49:53Z, 12 s, single failure "position after resume
  from frozen wrap next out of range 2-11: 21" (first read 10,
  second 21).
- P2 (fresh copy /tmp/y15k-P2, checker verified identical): FAIL,
  exit 1, 13:50:04-13:50:14Z, 10 s, all four exact-zero failures.
  P2-must-FAIL holds.
- Full suite once: 10/10 PASS, exit 0, 13:50:26-13:50:56Z, 30 s wall,
  t10 10438 ms, details 5 to 8 to 12 on both Nexts, resumes 3 to 7.
- Code/README audit: three-point advancing checks and two-point
  resumes all in the right places; README steps 6/7/11/15 and Notes
  match the code; 1.5x/1.3x/1.2x clock arithmetic checks out against
  the observed nominal middle read near 8.
- Diff note: actual diff at review time was +289/-36 (check.mjs
  +213/-27, README +76/-9); the brief's +240/-36 was a stale number
  in the brief, not a defect in the files. Final diff after the F1
  fix and round-6 doc corrections: +300/-37.
- Follow-up F1 (doc precision, fixed before landing): the Notes
  summary sentence read "after each Next / after each resume",
  which overclaims literally (playing wrap has no three-point check;
  step 5 resume has one read). Fixed with a one-line doc
  qualification: "after each advancing-checked Next (plain step 6
  and shuffle step 11)" and "after each frozen resume (steps 7, 11,
  15)". Verified 0 em/en dashes after the edit.
- Follow-up F2 (residual gap, future work): council's novel probe W1
  (timer dies 100 ms after the playing wrap Next, /tmp/y15k-W1)
  PASSES undetected because the next playlist click restarts the
  timer. Breaks neither P2 nor the suite; no README assertion
  promised an advancing check on the playing wrap. Recorded as
  future work, not a round-7 demand.

## Round-6 redteam: BLOCK

Report: /tmp/y15k-redteam.md. Verdict BLOCK. Builder:
 /tmp/y15k-rt/build.py. Probe: /tmp/y15k-rt/probe-r2.mjs.
Controls first: base PASS exit 0; P2 CAUGHT exit 1 (4 failures
verbatim); H2 CAUGHT exit 1 ("position did not gain again after
resume from frozen wrap next: 2 to 2"). All runs 13:51-13:55 UTC.

Three escaping mutants, each 3/3 deterministic:

- R1, slow clock 170 ms per tick (0.59x) after Next, dir
  /tmp/y15k-rt/R1-slow-170ms-after-next: PASS 3/3, exit 0.
  Advancing reads 5/7 vs correct 8/12, resume 2 then 4 vs 3 then 7.
  Mechanism: gain >= 2 per 350 ms always holds at 170 ms
  (2x170=340<350) and middle read about 5 sits inside 2-11.
  Claimed breach: README Context (1 sim-second per 100 ms); README
  documents only the fast side (1.2x), slow side escapes down to
  about 0.59x.
- R2, wrap branch only stops the timer, dir
  /tmp/y15k-rt/R2-wrap-only-timer-stop: PASS 3/3, exit 0, checker
  details byte-identical to base. Mechanism: the playing wrap Next
  has no advancing check; the next playlist click restarts the
  timer before any later read. Independently confirmed with
  probe-r2.mjs (13:55:42-13:55:45Z): after a playing wrap, base
  advances 8 then 12 over 1100 ms with status Playing; R2 stays 0
  then 0 with status Playing and track Morning Light. Claimed
  breach: Pass conditions say the position moves only while playing,
  Fail conditions list the position staying still while playing.
  Same class as council F2/W1 (two agents found it independently).
- R3b, clock 10x in the tail of each advancing window, dir
  /tmp/y15k-rt/R3b-fast-10ms-after-900ms: PASS 3/3, exit 0.
  AdvancingLater 40 vs correct 12, both plain and shuffle Nexts.
  Mechanism: first two points read at the correct rate, third point
  has gain-only with no absolute upper bound. Milder 1.43x version
  (R3, 70 ms interval, advancingLater 13) also passed 1/1.
  Claimed breach: README Context (1 sim-second per 100 ms); checker
  accepts position 40 where 12 is correct.
- C2, timer dies 900 ms after the frozen wrap resume: PASS 1/1,
  but the death starts after the final observation (second resume
  read about 730 ms) with no later position read, so it falls
  inside the README documented final limit. Per the stopping rule,
  NOT a basis for the BLOCK and not a round-7 demand.
- R5, playTrack no-reset, dir /tmp/y15k-rt/R5-playtrack-no-reset:
  PASS 1/1. Only trace: positionBeforePlayingWrap 12 instead of 7,
  checker only requires at least 2. Supporting evidence only; BLOCK
  rests on R1/R2/R3b.

Y15 independent re-runs (checkers verified identical to the worktree
by diff -q before running):

- R1 13:58:39 UTC: exit 0, failures []. Details: advancing 5,
  advancingLater 7, resumes 2 then 4, beforeWrap 4. Confirmed.
- R2 13:58:51 UTC: exit 0, failures []. Details identical to base
  (advancing 8/12, resumes 3/7). Confirmed.
- R3b 13:59:01 UTC: exit 0, failures []. Details: advancingLater 41
  (plain) and 40 (shuffle) vs correct 12. Confirmed.

## Adjudication (Y15) and doc corrections applied

Council APPROVE vs redteam BLOCK. Y15 adjudicated against the
stopping rule set before round 6 (land unless a finding breaks
P2-must-FAIL or 3x-10/10 or contradicts a README assertion that
cannot be fixed with a one-line doc correction):

- P2-must-FAIL intact (redteam controls, council re-run, matrix).
- 3x-10/10 intact (sequential and parallel, plus council run).
- R1: the README Notes document only the fast side and never claim
  slow-side verification; the Notes already concede rate
  non-distinction on the fast side (1.2x). The slow-side gap
  (0.6x-1.0x not distinguished; slower than about 0.6x caught by
  the gain floor) is the same kind of limit as E4/G3, accepted as
  documented limits in earlier rounds. Fixed with a doc sentence.
- R2: the general Fail condition was stated universally, but step 15
  plus the Notes wrap paragraph scope the playing-wrap verification
  to reset-only, and the council independently read it that way.
  The inconsistency is narrow and fixable by qualifying the Fail
  line and adding the explicit gap sentence to the Notes (same as
  council F2, already classified as future work).
- R3b: the Notes attribute the absolute bound to the middle read
  only; no assertion claims a bound on the later read. The later
  read's job (gain-only liveness) is accurately described. A clock
  that speeds up after the middle read is an undocumented limit of
  the same family. Fixed with a doc sentence.
- Correction to the redteam fix sketch: it says the second resume
  read needs an absolute upper bound, but the code already gives
  the second resume reads the 2-11 bound (check.mjs lines 155-156,
  237-238, 318-319); H3 proved it (second read 21 caught). Only
  the third advancing point lacks an upper bound. The doc sentence
  states this precisely instead.
- No round 7: every round's redteam will always find new timing
  mutants (finite observations leave gaps by construction); the
  README documented-limit pattern is the honest way to close the
  loop, and the code fixes for R1/R2/R3b would each need their own
  reviewed round. All three are recorded below as follow-ups with
  the redteam's fix sketches.

Doc corrections applied to README.md (no code change):

1. Fail conditions: "The position moves while paused or stays still
   while playing, except that advancing is not checked after the
   playing wrap Next (see Notes)."
2. Clock paragraph: "On the slow side the gain floor catches a clock
   slower than about 0.6x, and a clock between 0.6x and 1.0x reads
   inside the bounds and is not distinguished in this window."
3. Later read: "The later read requires gain only and carries no
   absolute upper bound, so a clock that speeds up after the middle
   read is not caught; the second resume reads do carry the 2 to 11
   bound, so a speedup after a frozen resume is caught."
4. Wrap paragraph: "No advancing check follows the playing wrap
   Next, so a timer that stops on the wrap path is masked by the
   next playlist click and is a known gap, not a verified behavior."

## Landing

- git fetch origin (about 14:00 UTC 21/11): origin/main had moved
  5 commits past local HEAD 5b15aa9 (f006137 clone1 note, 4ae08ce
  clone1 batch 5, 5df7535 clone2 coord merge, 5fea284 coord clone2
  batch 4, 041b1ac clone2 batch4 task5). None touched t10 files.
- Fix committed on 5b15aa9 as 364affe, then rebased cleanly onto
  origin/main f006137 with no conflicts. Fix commit after rebase:
  1d23532. git status clean after. git diff origin/main --stat:
  2 files, +300/-37, only the two t10 files.
- git push origin main: "f006137..1d23532 main -> main".
  git ls-remote origin main:
  1d235321f6d66fde6c0217b38287c233f37fa2ec refs/heads/main.
  Matches local HEAD 1d23532. Push verified.
- Log commit (this file) pushed separately after the fix commit;
  verified with git ls-remote in the final report to the parent.

## Follow-ups (recorded, not gates)

- N2 (Prev position, by design, documented in README Notes).
- E4 (1.2x clock, needs a longer measurement window).
- G3 (1.3x, intermittent at bound 11).
- E5 diagnostic wart: E5 (playTrack stops the timer) fails correctly
  via the pre-wrap >= 2 gates, but produces a confusing follow-on
  sampler message ("min observed 0 after 0").
- R1 (slow clock 0.59x-1.0x not distinguished): needs tighter bounds
  on the advancing points, not just gain of 2.
- R2/F2/W1 (timer stops on the playing wrap path, masked by the next
  playlist click): playing wrap Next needs the same three-point
  advancing check as the plain and shuffle Nexts, or a position read
  after the wrap before any playlist click restarts the timer.
- R3b (clock speeds up after the middle read; later advancing read
  has no upper bound): third advancing point needs an absolute upper
  bound, as the middle point already has. Note the second resume
  reads already have the 2-11 bound.
- R5 (playTrack no-reset escapes): the position after a playlist
  click needs an assertion (exact 0 before the 700 ms wait, or a
  bounded value after it).
- C2 (timer dies after the final observation): inside the documented
  final limit by construction; no action.
- Council round-5 observations O1 (timer dying about 700 ms post-Next
  still passes the delta window) and O2 (resume floor margin one
  tick): O1 is the same class H1 closed with the three-point check
  in round 6.

## Notes

- No em dash or en dash in check.mjs, README.md, or this log
  (grep 0 hits on all three after the final edit).
- No personal info in any landed file; no banned automation tool
  used anywhere in this task.
- The brief's +240/-36 diff figure was stale; the actual final diff
  is +300/-37 (check.mjs +213/-27, README.md +87/-10).
- Y14 note: Y14's live run of the suite is queued after Y13. The
  suite condition was ed78e83; it is now 1d23532. Y14 must re-stage
  to 1d23532 (and fix the H2 regex miss in the runner preflight when
  re-staging, per the fleet-state note).
