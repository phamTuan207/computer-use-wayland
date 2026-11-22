# Worker C5-BATCH3-CHECK log: todolist 4.24, Y12 H1-H4 + Y15 follow-up

Worker: C5-BATCH3-CHECK. Parent: COORD-CLICK-5 coordinator only. Never message the user.
Started: 2026-11-22 16:03 Asia/Ho_Chi_Minh (task received 16:03:27 +07).
Branch: todolist-push. Repo: ~/workspace/computer-use-wayland.
Owner asleep since 06:52 with a headache; Muse holds full authority. Owner order: MAXIMIZE PARALLELISM.
Standing rules: full access; no em dash (U+2014) or en dash (U+2013) anywhere;
no personal info on GitHub; commit with explicit pathspec only, immediately
after staging; verify every push with git ls-remote; never ydotool.

## 0. Paths located BEFORE any edit (16:03-16:12 +07)

Todolist: docs/zen-error-fix-todolist-20261121.md, section 4.24, line 205.
Y12 verify log: improvements/worker-y12-batch3-verify-log.md (commit 897ca17 on todolist-push).
Y15 fix log: improvements/worker-y15-t10-d1-fix-log.md (commit 3b50e94 on main;
fix commit 1d23532 on main).

Checker code and docs found on MAIN at 1d23532, NOT on todolist-push
(todolist-push has no tests/realistic/clone1-batch3/ directory at all;
merge-base with main is 7007efa). Read-only worktree for study:
 /tmp/c5b3-main (detached HEAD 1d23532).
Suite files on main:
- tests/realistic/clone1-batch3/run_all.mjs
- tests/realistic/clone1-batch3/lib/browser.mjs
- tests/realistic/clone1-batch3/lib/server.mjs
- tests/realistic/clone1-batch3/t05-file-manager/check.mjs, fixture.html, README.md
- tests/realistic/clone1-batch3/t09-multi-window/check.mjs, fixture.html, detail.html, prefs.html, README.md
- tests/realistic/clone1-batch3/t10-music-player/check.mjs, fixture.html, README.md
- plus t01-t04, t06-t08 (untouched by this task; only run as part of the suite).

Consequence: to do this work on todolist-push, the suite directory is first
imported verbatim from main @1d23532 as a base commit (no edits), then the
fixes land on top in separate commits. The import is additive (new directory),
so a later todolist-push to main merge sees identical content and stays clean.
No other way to run the checker test suite on this branch exists.

Environment:
- node v24.22.1.
- Chromium: /home/hatch/.cache/ms-playwright/chromium-1187/chrome-linux/chrome (exists).
- playwright-core: /tmp/y12-scratch is GONE (Y12/Y15 scratch wiped with /tmp).
  Reinstall to /tmp/c5b3-scratch (npm install playwright-core@1.65.1).
- Env prefix for every run:
  PLAYWRIGHT_CORE_PATH=/tmp/c5b3-scratch/node_modules/playwright-core
  CHROMIUM_PATH=/home/hatch/.cache/ms-playwright/chromium-1187/chrome-linux/chrome

## 1. Baseline (before) run

Started 2026-11-22 16:13 +07. Command:
`PLAYWRIGHT_CORE_PATH=/tmp/c5b3-scratch/node_modules/playwright-core CHROMIUM_PATH=/home/hatch/.cache/ms-playwright/chromium-1187/chrome-linux/chrome node tests/realistic/clone1-batch3/run_all.mjs`
Output (verbatim):
```
PASS t01-terminal 8936 ms
PASS t02-spreadsheet 3613 ms
PASS t03-video-call 5945 ms
PASS t04-email-client 6919 ms
PASS t05-file-manager 5571 ms
PASS t06-calendar 3144 ms
PASS t07-code-editor 2900 ms
PASS t08-settings-panel 3555 ms
PASS t09-multi-window 5391 ms
PASS t10-music-player 12355 ms
summary: 10 passed, 0 failed, wall clock 58372 ms, results written to results.json
exit=0
```
Baseline: 10/10 PASS, wall 58372 ms, exit 0. results.json restored with
`git checkout --` after the run; worktree clean for the suite after.
Base import commit: c48d398 (suite verbatim from main @1d23532, no edits).

Probe harness: /tmp/c5b3-probes/probe.py. Each mutant copies the suite from
the repo working tree to /tmp/c5b3-probes/<name>, applies ONE fixture patch,
runs that test's check.mjs standalone, prints exit + failures. Phase "old"
runs below, against the base checker. Phase "new" re-runs the same mutants
after the fixes.

### Phase old results (started 2026-11-22 16:09 UTC / 16:09 +07, wall 256 s for the full matrix)

Command: `cd /tmp/c5b3-probes && python3 probe.py --all` (16 mutants).
Verbatim summary (full output in the run transcript):

```
h1-hardcode-old: exit 0 | failures: []
h2-wrong-text: exit 0 | failures: []
h2-ws-applied: exit 0 | failures: []
h2-dup-rejected: exit 0 | failures: []
h3-late-6s: exit 1 | failures: ["Alpha title after first rename: expected effect not seen after popup closed, click may not have landed", "Alpha title after first rename: project alpha is \"Alpha\", want \"Alpha v2\"", "status wrong after first rename: Ready.", "detail window did not prefill Alpha v2 on reopen", ...]
h3-nostore: exit 0 | failures: []
h3-status-once: exit 0 | failures: []
h3-spurious: exit 0 | failures: []
h4-prev-noreset: exit 0 | failures: []
h4-prev-stops-timer: exit 1 | failures: ["position did not gain after shuffle next while playing: 0 to 0", "position after shuffle next while playing out of range 2-11: 0", "position did not gain again after shuffle next while playing: 0 to 0"]
r5-playtrack-noreset: exit 0 | failures: []
r1-slow-170: exit 0 | failures: [] (first run of the weak mutant; see correction below)
r2-wrap-stop: exit 0 | failures: []
w1-wrap-die-100: exit 1 | failures: ["position did not advance after resume from frozen wrap next: 0", ...] (leak, see correction below)
r3b-fast-tail-10ms: exit 1 | failures: ["position after next while playing out of range 2-11: 50", "position after shuffle next while playing out of range 2-11: 82", ...] (early tail, see correction below)
r3-mild-tail-70ms: exit 1 | failures: ["position after shuffle next while playing out of range 2-11: 12"] (early tail, see correction below)
e1-shuffle-reset-1: exit 1 | failures: ["position not exactly 0 after shuffle next while playing: 1", "position not exactly 0 after shuffle next while paused: 1"]
e2-wrap-reset-1-playing: exit 1 | failures: ["position not exactly 0 after playing wrap next while playing: 1"]
e5-playtrack-stops-timer: exit 1 | failures: ["position did not advance before playing wrap next: 0", "position not reset after playing wrap next: min observed 0 after 0", "position did not advance before frozen wrap next: 0"]
```

Reading: every H1/H2/H3/R5/R2 hole is LIVE on the base checker (mutant
passes, exit 0). h3-late-6s is the false fail: the old checker fails a
correct 6 s delivery. e1/e2/e5 are already caught (regression checks); e5
shows the confusing follow-on message verbatim
('min observed 0 after 0'). h4-prev-stops-timer fails only via a downstream
cascade at the shuffle Next, not at the Prev itself.

Three of my own probe mutants were unfaithful and were fixed before being
trusted (the fixes are in probe.py, repo untouched throughout):
- r1-slow-170 first only changed the stored interval, so the plain Next
  still ran at 100 ms. Fixed: restart the running timer in nextTrack when
  playing. Re-run: exit 0, advancing 5/7 plain and shuffle, resumes 2/4,
  matching Y15's R1 numbers exactly.
- w1-wrap-die-100 first scheduled the death in the wrap branch for both
  wraps, so the frozen wrap's death timer leaked into the resume and the
  old checker failed there. Fixed: only when playing. Re-run: exit 0.
- r3b/r3-mild first counted tail ticks from Play and never reset the
  counter in startTimer, then left the fast interval sticky across Nexts,
  so the tail fired during the sampler (middle 50/87). Fixed: reset the
  counter in startTimer and restart the timer at each playing Next, so the
  fast tail starts about 900 ms after that Next. Re-run: r3b exit 0, later
  40/41 vs correct 12 (Y15's numbers exactly); r3-mild exit 0, later 13/13
  (Y15's R3 exactly).
- Threshold mapping (old checker, all exit 0): r1-slow-143 (0.70x) middle
  6, later 8; r1-slow-125 (0.80x) middle 6, later 9. So the middle floor
  of 6 catches 0.59x (middle 5) and the detection threshold sits between
  0.59x (caught) and 0.70x (escapes).

Correct-value distribution measured across the old-phase runs (16 runs):
middle read plain 8-9, shuffle 8-9 (10 only on the reset-to-1 mutant);
later read plain 12-13, shuffle 12-13 (14 only on the reset-to-1 mutant);
resume first reads 3-4, second 7-8. This sets the new bounds with margin:
middle floor 6 (2 ticks below the correct minimum 8), later cap 15
(2 ticks above the correct-fixture maximum 13). Load can only delay ticks,
never add them, so the upper bound cannot flake under load; the floor is
validated by the 3x parallel load runs in section 3.

## 2. Fixes

### H1 (t05): per-run random suffix for novel names
Before: fixed strings 'field-notes-7.txt' (check.mjs) and 'Old Files 2026'
(check.mjs) appear only in the checker, never in the fixture. A future fixture
could hardcode them and pass without applying the typed rename.
Fix: novel names built from a per-run tag (Date.now base36 + random base36).
Proof: run t05 twice, compare details.novelFileName / details.novelFolderName
(must differ); mutant fixture that hardcodes the OLD fixed names must FAIL
against the new checker and PASS against the old checker.

### H2 (t05): error assert checks only visibility, never text
Before: `if (!(await page.isVisible('#rename-error'))) failures.push('empty rename error not shown')`.
It never reads the error text. Whitespace-only renames untested. The fixture
shows exactly 'Name cannot be empty.' and leaves the dialog open.
Now: assert the exact error text 'Name cannot be empty.' on the empty-name
case, plus a NEW whitespace-only case (fill '   ', Save, expect the same exact
text, dialog open, name unchanged). Why this is correct: the text is the
fixture's only signal distinguishing an empty-name rejection from any other
visible error element; visibility alone passes a fixture that shows the wrong
message. Duplicate names: NOT an error case in this demo. The fixture applies
whatever name is typed, trimmed (README Notes), with no duplicate rule, so
there is no duplicate error to assert; asserting one would fail the correct
fixture. Instead the duplicate case is tested as specified behavior: rename to
an existing name at the end of the flow and assert the list shows it applied
verbatim (duplicate present, old name gone).
Proof: mutant A (wrong error text) must FAIL new / PASS old; mutant B
(whitespace name applied as-is) must FAIL new; mutant C (duplicate rejected)
must FAIL new.

### H3 (t09): localStorage unverified; 6 s delivery false-fails on 5 s poll cap
Before: status asserted only after the first rename; localStorage never read;
prefs Cancel never clicked; no settle read after the final titles; verify poll
cap 5000 ms in clickAndClose (check.mjs line 74).
Now: (a) localStorage 'project:<id>' asserted after every rename and 'theme'
after every theme change, plus a reload persistence check at the end (titles
and theme survive reload, which is what localStorage is for); (b) poll cap
raised 5000 ms to 10000 ms so a correct 6 s delivery verifies; (c) status
asserted after the second rename, after each theme apply, and after Gamma v2;
(d) prefs Cancel exercised (select dark, Cancel, dwell, assert still light and
localStorage theme unchanged); (e) 500 ms settle re-read of the final titles
and status after the last rename. Why 10 s: it covers deliveries up to 10 s
with margin over the 6 s case; the close wait is already 10 s; beyond 10 s a
lost result is a genuine failure, and the failure-path cost is one extra 5 s
wait. README Notes updated 5 s to 10 s.
Proof: mutant D (opener applies the rename 6000 ms late) must PASS new /
FAIL old (false-fail demonstrated); mutant E (localStorage write dropped)
must FAIL new / PASS old; mutant F (status only on first rename) must FAIL
new; mutant G (spurious rename 300 ms after the final rename) must FAIL new /
PASS old.

### H4 (t10): position not read after Prev / playlist / shuffle / wrap Next
Before (Y12, pre-Y15): position never read after Prev, playlist clicks,
shuffle Next, or wrap Next. Y15 (1d23532) already added same-task exact-zero
+ sampler + advancing reads after the playing and frozen shuffle Nexts and
both wrap Nexts (verified by its 27-probe matrix). What is still missing on
this base: (a) Prev: no position read after any of the 3 Prev clicks; (b)
playlist clicks: only a >= 2 advancing read after steps 14/15, no reset-value
read, and nothing after the step 19 Night Drive click; step 14 also asserts a
now-playing value (Mountain Air) that is already current, so the click's only
live witness is the position read.
Now: (a) same-task exact-zero read after EVERY Prev click (Prev resets
position to 0 synchronously in the fixture; evaluate-click + read is
deterministic, same pattern as Next), plus a 350 ms advancing read (2-11)
after the step 7 Prevs and after the step 11 Prev, so a Prev that stops the
timer fails; (b) same-task exact-zero read after EVERY playlist click
(steps 14, 15, 19), which is also the R5 fix (playTrack no-reset); (c)
shuffle/wrap Next reads re-verified by re-running the Y15 probes (E1, E2, W1
class) against this base, results recorded, not re-implemented.
Proof, one per action: Prev no-reset mutant must FAIL; Prev stops-timer
mutant must FAIL; playlist no-reset (R5) mutant must FAIL; shuffle reset-to-1
(E1) re-run must FAIL; wrap reset-to-1 (E2) re-run must FAIL; wrap timer-stop
(R2/W1) must FAIL after the R2 fix (see below).

### Y15 R1: slow clock 0.59x-1.0x not distinguished
Sketch: tighter bounds on the advancing points, not just gain of 2.
Implement: raise the middle-read lower bound on the advancing-checked Nexts
(plain step 6, shuffle step 11, new playing-wrap check) and measure the
correct-value distribution under load before fixing the number; document the
measured slow-side threshold honestly (which slow factors still escape).
Proof: R1 mutant (170 ms/tick after Next) must FAIL new / PASS old.
If load runs show the tightened bound flakes on the correct fixture, the
bound is loosened to what the data supports and the residual gap is recorded
with the measured numbers instead of shipping a flaky bound.

### Y15 R2 (+ W1, same class): timer stops on the playing wrap path
Sketch: same three-point advancing check as the plain and shuffle Nexts, or a
position read after the wrap before any playlist click restarts the timer.
Implement: full three-point advancing check after the playing wrap Next
(sampler already exists; add after-sampler / +350 ms / +350 ms reads with
gain >= 2 and the middle bound, plus the R3b later-read bound), placed BEFORE
the next playlist click. This also closes W1 (timer dies 100 ms after the
playing wrap Next), which is the same class with a different death time.
Proof: R2 mutant (wrap-only timer stop) must FAIL new / PASS old; W1 mutant
(timer dies 100 ms after playing wrap) must FAIL new / PASS old.

### Y15 R3b: clock speeds up after the middle read; later read has no bound
Sketch: third advancing point needs an absolute upper bound, as the middle
point already has.
Implement: advancingLater bound (correct value near 12; bound set from the
measured correct distribution with margin; R3b gives 40-41). Apply to the
plain, shuffle, and new playing-wrap advancing checks. Second resume reads
already carry 2-11 (unchanged).
Proof: R3b mutant (10x tail) must FAIL new / PASS old; R3 mutant (1.43x,
later 13) is expected to still PASS and is recorded as the documented
residual, with the measured numbers.

### Y15 R5: playTrack no-reset escapes
Sketch: position after a playlist click needs an assertion (exact 0 before
the 700 ms wait, or a bounded value after it).
Implement: same-task exact-0 read after every playlist click (see H4 (b)).
This is the same code as the H4 playlist fix, not a second change.
Proof: R5 mutant (playTrack no-reset) must FAIL new / PASS old.

### Y15 E5 wart: confusing follow-on sampler message
Before: E5 (playTrack stops the timer) fails correctly via the pre-wrap
>= 2 gates, but the sampler then adds 'position not reset after playing wrap
next: min observed 0 after 0'. The message is confusing because min 0 looks
like a reset. Root cause: the sampler condition `minAfter >= posBefore`
is vacuous when posBefore is 0 (min >= 0 is always true), so it fires on
exactly the case where the position is stuck at 0.
Fix: guard the clause with `posBefore > 0` in all three sampler checks
(plain, shuffle, wrap). A true reset still gives min 0; a missed reset with
posBefore > 0 still fails via the same clause; only the vacuous case is
silenced, and the pre-wrap gate failure stands alone and clear.
Proof: E5 mutant must FAIL new with NO 'min observed 0 after 0' message;
old checker run against the same mutant must show the confusing message.

## 3. Suite runs (before/after)

BEFORE (base c48d398, 2026-11-22 16:13 +07): 10/10 PASS, wall 58372 ms,
exit 0. Per-test: t01 8936, t02 3613, t03 5945, t04 6919, t05 5571,
t06 3144, t07 2900, t08 3555, t09 5391, t10 12355 ms.

AFTER (fixed checker, 2026-11-22 16:27 +07): 10/10 PASS, wall 43303 ms,
exit 0. Per-test: t01 3639, t02 2805, t03 2939, t04 2817, t05 3720,
t06 2853, t07 3327, t08 2786, t09 5897, t10 12500 ms. The wall difference
is run-to-run variance: the untouched tests moved by seconds between the
two runs (t01 8936 to 3639, t04 6919 to 2817), so no wall-time claim is
made from a single pair of runs. The added reads cost real time by
construction: about 1400 ms of sleeps on t10 (700 ms wrap advancing +
350 ms + 350 ms Prev advancing) and about 1000 ms on t09 (500 ms settle
dwell + reload).

New-checker standalone runs (2026-11-22 16:25-16:27 +07):
- t05 run 1: pass true, novelFile field-notes-mwrmlvj66be4f.txt,
  novelFolder 'Old Files mwrmlvj68jfcd', failures [].
- t05 run 2: pass true, novelFile field-notes-mwrmm1j9ipgum.txt,
  novelFolder 'Old Files mwrmm1j9i3xi6', failures [].
  The two runs used different names: H1 non-collision proven by execution.
  (One draft bug found and fixed during this step: the first draft used a
  single tag for both names, so searching the tag matched both the file
  and the folder and t05 failed twice with 'search <tag>: got
  [field-notes-<tag>.txt, Old Files <tag>], want [Old Files <tag>]'.
  Fixed with two independent tags, one per name; re-ran, both pass.)
- t09: pass true, elapsed 9494 ms, failures [], final titles
  Alpha Final / Beta / Gamma v2.
- t10: pass true, failures []. New details observed on the correct
  fixture: positionAfterFirstPrev 0, positionAfterSecondPrev 0,
  positionAfterPrev 3, positionAfterShufflePrev 0,
  positionAfterShufflePrevAdvance 3, positionAfterPlaylistMountain 0,
  positionAfterPlaylistMountainAgain 0, positionAfterPlaylistNight 0,
  positionAtWrapSamplerEnd 5, positionAdvancingAfterWrap 9,
  positionAdvancingLaterAfterWrap 13, middle reads 9/9, later reads 13/13.
  All inside the new bounds (middle 6-11, later at most 15).

### Phase new results (started 2026-11-22 16:28 +07, wall 310 s for the full matrix)

Command: `cd /tmp/c5b3-probes && python3 probe.py --all` (18 mutants,
same script, same fixtures, against the fixed checker). Verbatim:

```
h1-hardcode-old: exit 1 | failures: ["field-notes-mwrmnwzcbxyzx.txt missing after rename", "after delete: got [Archive, budget.csv, field-notes-7.txt, video.mp4], want [Archive, budget.csv, field-notes-mwrmnwzcbxyzx.txt, video.mp4]", "Home after moving video out: ...", "Old Files mwrmnwzc33uyk missing after folder rename", "tree button for Old Files mwrmnwzc33uyk missing", "page.click: Timeout 30000ms exceeded ... #tree-old-files-mwrmnwzc33uyk"]
h2-wrong-text: exit 1 | failures: ["empty rename error text wrong: \"Something went wrong.\"", "whitespace-only rename error text wrong: \"Something went wrong.\""]
h2-ws-applied: exit 1 | failures: ["budget.csv missing after whitespace-only rename", "rename dialog closed on whitespace-only name", "whitespace-only rename error not shown", "page.click: Timeout 30000ms exceeded ... #rename-cancel ... element is not visible"]
h2-dup-rejected: exit 1 | failures: ["after duplicate rename: rename dialog still visible", "duplicate rename did not apply verbatim: got [budget.csv, field-notes-mwrmpgbcxfopr.txt, Old Files mwrmpgbcysw0f, video.mp4]", "budget.csv still present after duplicate rename"]
h3-late-6s: exit 0 | failures: []
h3-nostore: exit 1 | failures: ["localStorage after first rename: ... is \"null\", want \"Alpha v2\"", "localStorage after second rename: ...", "localStorage after prefs dark: ...", "localStorage after prefs light: ...", "localStorage after cancelled prefs change: ...", "localStorage after second prefs dark: ...", "localStorage after Gamma rename: ...", "Alpha title after reload: ...", "Gamma title after reload: ...", "main window missing dark class after reload", "localStorage after reload: ... x3"]
h3-status-once: exit 1 | failures: ["status wrong after second rename: Renamed alpha to Alpha v2.", "status wrong after Gamma rename: Theme set to dark.", "status wrong after settle: Theme set to dark."]
h3-spurious: exit 1 | failures: ["Alpha title after settle: project alpha is \"Alpha HACKED\", want \"Alpha Final\"", "Alpha title after reload: ...", "localStorage after reload: ... is \"Alpha HACKED\""]
h4-prev-noreset: exit 1 | failures: ["position not exactly 0 after first prev: 7", "position not exactly 0 after second prev: 7", "position not exactly 0 after prev in shuffle order: 7"]
h4-prev-stops-timer: exit 1 | failures: ["position did not advance after prev: 0", "position did not gain after shuffle next while playing: 0 to 0", "position after shuffle next while playing out of range 6-11: 0", "position did not gain again after shuffle next while playing: 0 to 0", "position did not advance after prev in shuffle order: 0"]
r5-playtrack-noreset: exit 1 | failures: ["position not exactly 0 after clicking Mountain Air: 5", "position not exactly 0 after clicking Mountain Air again: 12", "position not exactly 0 after clicking Night Drive: 8"]
r1-slow-170: exit 1 | failures: ["position after next while playing out of range 6-11: 5", "position after shuffle next while playing out of range 6-11: 5", "position after playing wrap next while playing out of range 6-11: 5"]
r1-slow-143: exit 0 | failures: []
r1-slow-125: exit 0 | failures: []
r2-wrap-stop: exit 1 | failures: ["position did not gain after playing wrap next while playing: 0 to 0", "position after playing wrap next while playing out of range 6-11: 0", "position did not gain again after playing wrap next while playing: 0 to 0"]
w1-wrap-die-100: exit 1 | failures: ["position did not gain after playing wrap next while playing: 1 to 1", "position after playing wrap next while playing out of range 6-11: 1", "position did not gain again after playing wrap next while playing: 1 to 1"]
r3b-fast-tail-10ms: exit 1 | failures: ["position after next while playing too far advanced: 41", "position did not advance after prev: 20", "position after shuffle next while playing too far advanced: 41", "position did not advance after prev in shuffle order: 19", "position after playing wrap next while playing too far advanced: 41"]
r3-mild-tail-70ms: exit 0 | failures: []
e1-shuffle-reset-1: exit 1 | failures: ["position not exactly 0 after shuffle next while playing: 1", "position not exactly 0 after shuffle next while paused: 1"]
e2-wrap-reset-1-playing: exit 1 | failures: ["position not exactly 0 after playing wrap next while playing: 1"]
e5-playtrack-stops-timer: exit 1 | failures: ["position did not advance before playing wrap next: 0", "position did not gain after playing wrap next while playing: 0 to 0", "position after playing wrap next while playing out of range 6-11: 0", "position did not gain again after playing wrap next while playing: 0 to 0", "position did not advance before frozen wrap next: 0"]
```

Score: 15 FAIL as required (every hole that passed before now fails), 3 PASS
as documented residuals, 0 regressions:
- h3-late-6s now PASSES: the 6 s delivery verifies on the 10 s poll cap.
  The false fail is fixed.
- r1-slow-143 (0.70x, middle 6) and r1-slow-125 (0.80x, middle 6-7) still
  PASS: the detection threshold sits between 0.59x (caught, middle 5)
  and 0.70x (escapes, middle 6). Recorded in the README, not chased: a
  lower floor would eat the margin under load.
- r3-mild (1.43x tail, later 13) still PASSES, matching Y15's R3 exactly.
  The later cap of 15 catches the 10x tail (41) with 2 ticks of margin
  over the correct maximum (13).
- e1/e2 still FAIL: no regression on the Y15 coverage.
- e5 still FAILS, and the confusing 'min observed 0 after 0' message is
  GONE: the failures are now the two pre-wrap gates plus the new wrap
  advancing failures (0 to 0). The wart is fixed.
- h4-prev-stops-timer now fails FIRST with 'position did not advance
  after prev: 0', at the Prev itself, instead of only downstream.
- h1/h2 failure-path latency note: the hardcode and whitespace mutants
  each add one 30 s Playwright locator timeout (missing tree button /
  hidden Cancel button) after the first real failure. Same class as
  Y12's P2/P3 cascade note: slow failure path, deterministic failure.

### Repeat suite runs (after)

Sequential, fixed checker:
- Run 2, 2026-11-22 16:33 +07: 10 passed, 0 failed, wall 46708 ms, exit 0.
  t05 4408, t09 7194, t10 13281 ms.
- Run 3, 2026-11-22 16:34 +07: 10 passed, 0 failed, wall 51467 ms, exit 0.
  t05 5549, t09 7768, t10 13267 ms.

Parallel load, 3 full suites at once from separate copies
(/tmp/c5b3-load/a, b, c), 2026-11-22 16:36 +07: all 10/10, exit 0 each.
- a: wall 125630 ms, t10 14600 ms.
- b: wall 122798 ms, t10 15762 ms.
- c: wall 125956 ms, t10 14166 ms.
t10 middle reads under load: a 8/9/8, b 10/9/8, c 8/9/9 (plain/shuffle/wrap);
later reads: a 12/12/12, b 14/12/12, c 12/12/13. Minimum middle 8 stays
2 ticks above the floor of 6; maximum later 14 stays below the cap of 15.
The tightened bounds do not flake under load.
(One load attempt before this failed 0/10 on copies b and c in about
300 ms each with 'playwright-core not found': my shell line exported the
env vars inside the first background job only, so the sibling jobs did
not inherit them. Infrastructure mistake in the launch line, not a test
failure; re-ran with the exports in the parent shell and all three
passed. The first attempt's copy a passed 10/10 in the same run.)

Total after-fix suite evidence: 3 sequential 10/10 + 3 parallel 10/10,
plus t05/t09/t10 standalone passes and the 18-mutant phase-new matrix.

## 4. Commits and push verification

- Base import (suite verbatim from main @1d23532, no edits): c48d398.
  Pushed in the same push as the fix commit (verified below).
- Fix commit: 42d5e39, 7 files, +335/-109 (6 checker files + todolist
  4.24 tick). Pushed 2026-11-22 16:39 +07:
  `git push origin todolist-push` -> `abca0bd..42d5e39 todolist-push -> todolist-push`.
  `git ls-remote origin todolist-push`:
  `42d5e39a88e94ed3debc46f37b312f32825b1692 refs/heads/todolist-push`,
  matching local HEAD. Push verified.
- Log commit: 49e871d (this file). Pushed 2026-11-22 16:40 +07:
  `42d5e39..49e871d todolist-push -> todolist-push`. `git ls-remote origin todolist-push`:
  `49e871d92a8b6506bbcfd3206a9e9779d1b31c89 refs/heads/todolist-push`,
  matching local HEAD. Push verified.
- Note on the 16:32 PAUSE order (coord log section 44, commit 25c91aa):
  in-flight workers finish their current item cleanly and report, then
  HOLD with no new items until the resume signal. This push is the clean
  finish of the assigned item, not a new item. No new work spawned.
- Worktree state after the fix commit: only other lanes' files remain
  modified/untracked (step 9, Y13G, S2 flip, Y1B, Y6); none of them were
  staged or committed by this worker. results.json was restored with
  `git checkout --` after every suite run.
- No em dash or en dash in any touched file (grep 0 hits on all 6 checker
  files + log). No personal info in any commit. No ydotool. All runs
  timed and logged above. Finished 2026-11-22 16:39 +07. Elapsed from
  task receipt (16:03) to fix push: about 36 minutes.
