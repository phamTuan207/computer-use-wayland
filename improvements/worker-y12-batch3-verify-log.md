# Worker Y12 log: independent verification of the merged clone1-batch3 suite

Worker: Y12 (Muse). Owner order: full autonomy per the Lauren Tan direction.
Started 2026-11-21 19:21 Asia/Ho_Chi_Minh. Verification worktree
~/workspace/y12-verify, detached HEAD ed78e83 (origin/main).

## Redirect note (why there is no reconciliation in this log)

Y12 was first spawned to reconcile clone1's fix (08f36d2) with Y10's fix
(branch y10-batch3-fix, 0b61bd1) into one suite. While Y12's council (3)
and redteam were deliberating, Y10 reconciled the two versions itself
and landed the merged suite on main as commit ed78e83 (plus 5b15aa9 log
commit). Muse redirected Y12 to INDEPENDENT VERIFICATION of the merged
suite instead. The reconciliation council was stopped (redteam child
closed mid-run, no result; the three completed council verdicts are
moot for landing but informed the probe design). Nothing from the
reconcile worktree (~/workspace/y12-reconcile, branch
y12-batch3-reconcile, no commits) was landed and nothing collides with
ed78e83.

## Scope

Verify, do not modify. The suite tests/realistic/clone1-batch3/ was not
modified in any way: the verify worktree was checked clean with
`git status --short` (empty) after all runs, and run_all.mjs output
(results.json) was restored to HEAD. The live run of the fixed suite is
a separate worker's job (Y14), not this one. All verification below is
headless Playwright Chromium on the VM, never the live Zen.

Environment: node v24.22.1, playwright-core 1.65.1 installed once to
/tmp/y12-scratch (npm install playwright-core@1.65.1),
CHROMIUM_PATH=~/.cache/ms-playwright/chromium-1187/chrome-linux/chrome.

## What was verified

Merged suite at ed78e83, per Y10's reconcile (MEMORY.md 19:20):
t05 = clone1 fixture (real rename dialog, Save, error on empty, trim)
+ Y10-style checker (novel names, cancel-first, dialog asserts, folder
rename with contents); t09 = clone1 clickAndClose-with-verify (5 s poll)
+ cancel dwell (500 ms, then immediate read); t10 = clone1 500 ms
in-page sampler (min <= 2) + advancing check (sleep 350 ms, position
>= 2); t10 fixture does NOT restart the clock on track change.

## Positive runs: 6/6 full suites 10/10 PASS

Command (each run):
`PLAYWRIGHT_CORE_PATH=/tmp/y12-scratch/node_modules/playwright-core CHROMIUM_PATH=~/.cache/ms-playwright/chromium-1187/chrome-linux/chrome node tests/realistic/clone1-batch3/run_all.mjs`

Sequential x3, from ~/workspace/y12-verify:
- Run 1, 19:22:27 +07: 10/10, exit 0, wall 26929 ms.
  t05 2789 ms, t09 3002 ms, t10 4262 ms.
- Run 2, 19:22:50 +07: 10/10, exit 0, wall 23378 ms.
  t05 2533 ms, t09 3020 ms, t10 4388 ms.
- Run 3, 19:23:14 +07: 10/10, exit 0, wall 23051 ms.
  t05 2694 ms, t09 2899 ms, t10 4333 ms.
Logs: /tmp/y12/runs/seq-1.log, seq-2.log, seq-3.log.

Concurrent load x3, three full suites in parallel from separate copies
(/tmp/y12-load/a, b, c), 19:24 +07:
- A: 10/10, exit 0, wall 65998 ms. t05 6710 ms, t09 10032 ms, t10 8484 ms.
- B: 10/10, exit 0, wall 65702 ms. t05 6688 ms, t09 10067 ms, t10 8430 ms.
- C: 10/10, exit 0, wall 64939 ms. t05 7125 ms, t09 10153 ms, t10 7885 ms.
Logs: /tmp/y12/runs/load-a.log, load-b.log, load-c.log.

## Mutation probes: 11/12 matched (own design, own script)

Script: /tmp/y12/probe.py (written fresh by Y12). Each probe copies the
merged suite to /tmp/y12-mutations/<name>, applies ONE named break,
runs that test's check.mjs standalone, and compares the exit code with
the expectation stated BEFORE running. Summary:
 /tmp/y12-mutations/probe-summary.json. Diffs:
 /tmp/y12-mutations/<name>.diff. Total wall 176042 ms.
The canonical breaks coincide with any honest probe set because they are
the direct negation of each fix; the script, the extra probes
(reset-to-1, 2000 ms delay, late cancel rename, folder drops contents)
and every expectation are Y12's own design, not copied from Y10's probe
script. Two probe designs were corrected before running: a popup-side
delay is killed by window.close, so the 2000 ms delay lives in the
opener's handler (t09-P2) and the late cancel rename keeps the popup
open 800 ms before posting and closing (t09-P3).

| Probe | Break applied | Expect | Got | Result |
|---|---|---|---|---|
| t05-P1 | rename-save ignores typed input, hardcodes old mapping (notes.txt to meeting-notes.txt, Archive to Old files) | FAIL (1) | 1 | MATCH. "field-notes-7.txt missing after rename" |
| t05-P2 | rename applies on Rename-button click, Save is a no-op | FAIL (1) | 1 | MATCH. Caught by cascade (dialog not visible at next step, 30 s fill timeout on stale DOM) |
| t05-P3 | Cancel applies the typed rename | FAIL (1) | 1 | MATCH. Same cascade as P2 |
| t05-P4 | folder rename drops contents (store[next] assignment removed) | FAIL (1) | 1 | MATCH. "Old Files 2026 still holds video.mp4 after rename: got [], want [video.mp4]" |
| t09-P1 | prefs.html theme postMessage dropped | FAIL (1) | 1 | MATCH. Verify poll failure + "main window missing dark class after prefs dark" |
| t09-P2 | opener applies the rename 2000 ms late | PASS (0) | 0 | MATCH. 8929 ms. The 5 s verify poll absorbs the delay |
| t09-P3 | cancelled popup posts a rename 800 ms after the click, then closes | FAIL (1) | 1 | MATCH. Caught at the cancel assert AND the final Beta assert |
| t09-P4 | rename sets title but never status text | FAIL (1) | 1 | MATCH. "status wrong after first rename: Ready." |
| t10-P1 | nextTrack never resets position | FAIL (1) | 1 | MATCH. "position not reset after next: min observed 12 after 12" |
| t10-P2 | nextTrack resets to 1, not 0 | FAIL (1) | 0 | MISMATCH. No failures. The sampler allows min <= 2, so a reset to 1 passes. DEFECT, see D1 |
| t10-P3 | nextTrack resets only when paused | FAIL (1) | 1 | MATCH. "position not reset after next: min observed 12 after 12" |
| t10-P4 | nextTrack stops the playback clock, never restarts | FAIL (1) | 1 | MATCH. "position did not advance after next while playing: 0" |

Note: t05 probe runs took about 32 s each (a 30 s Playwright locator
timeout on the broken fixture). The checker still fails deterministically;
the slowness is failure-path latency, not a pass.

## Council + redteam verdicts (debated Y12's evidence)

Brief: /tmp/y12/verify-brief.md. All read-only, no repo edits, no contact
with Y10 or clone1.
- Council t05 (/tmp/y12/verify-council-t05.md): t05 SOUND. All 4 probes
  matched; fixture grep 0 hits for field-notes-7, Old Files 2026,
  meeting-notes. P2/P3 cascade noted as evidence-quality caveat, low.
- Council t09 (/tmp/y12/verify-council-t09.md): t09 SOUND. All 4 probes
  matched. Holes all LOW (status only after first rename, no post-final
  settle read, verify loop swallowing errors for diagnosis).
- Council t10 (/tmp/y12/verify-council-t10.md): t10 DEFECT (minor,
  narrow). P2 is a defect, not acceptable tolerance: the sampler cannot
  distinguish a correct reset sampled late from a wrong reset to 1.
  Remedy: exact-zero assert on a clock-frozen path (pause before Next,
  require exactly 0, resume, keep advancing check). Blocks clean SOUND
  for t10, not SOUND WITH NOTED DEFECTS.
- Redteam (/tmp/y12/verify-redteam.md): overall SOUND WITH NOTED
  DEFECTS. Confirms t10-P2 executed. Adds static-trace escapes for t05
  (future hardcoding of the now-public novel names is sharpest) and t09
  (localStorage persistence dropped, transient theme revert, spurious
  message after final read, 6 s delivery would false-fail on the 5 s
  poll cap). No canonical Y3 property was found escaping, so not
  NOT SOUND.

## Y12 adjudication and overall verdict: SOUND WITH NOTED DEFECTS

- t05 SOUND. Executed evidence is 4/4 probes + 6/6 positive runs.
  Redteam items are static traces, none demonstrated as a false pass.
- t09 SOUND. Executed evidence is 4/4 probes + 6/6 positive runs.
  The 6 s delivery false-fail is fail-closed strictness, not a false
  pass; the fixture posts synchronously and locally, so no realistic
  6 s delivery exists here.
- t10 DEFECT (minor, narrow), executed. See D1.
- The Y3 FAILs are all fixed: every canonical break (old-mapping
  hardcode, rename-on-button, Cancel-applies, folder-drops-contents,
  dropped theme, late cancel rename, title-without-status, no-reset,
  reset-only-when-paused, timer-stops) is caught by execution.

## Defect list

D1 (EXECUTED, minor, narrow): t10 sampler tolerance hole.
tests/realistic/clone1-batch3/t10-music-player/check.mjs line 85:
`if (minAfterNext > 2 || minAfterNext >= posBeforeNext)`. A nextTrack
that resets position to 1 (or 2, or a reset delayed under 500 ms)
passes: the sampler takes the minimum over 500 ms and accepts 1-2,
so it never asserts the reset value its own README states ("plays
from position 0"). Proven by probe t10-P2 (exit 0, no failures).
Remedy (council t10): add an exact-zero assertion on a clock-frozen
path, keep the sampler for the playing path. Verify by re-running P2
(must FAIL) plus 3x positive runs (must stay 10/10). Does not block
the suite's use; it blocks a clean SOUND label only.

Noted holes (static, not demonstrated as false passes; follow-ups,
not gates):
- H1: fixed novel names (t05 check.mjs lines 103, 134) could be
  hardcoded by a future fixture. Durable fix is a per-run random
  suffix.
- H2: t05 error assert checks only visibility of #rename-error
  (check.mjs line 92), never its text; whitespace-only and
  duplicate-name renames untested.
- H3: t09 status asserted only after the first rename (check.mjs
  lines 104-105); localStorage persistence never verified; prefs
  Cancel never clicked; spurious message after the final read would
  escape (check.mjs lines 147-148); a correct 6 s delivery would
  false-fail on the 5 s poll cap (line 74).
- H4: t10 position never read after Prev, playlist clicks, shuffle
  Next, or wrap Next; advancing threshold >= 2 tolerates a slow
  clock; the Mountain Air playlist click asserts now-playing that is
  already Mountain Air.

## Limits

- Headless Chromium only. Firefox/Zen behavior is UNVERIFIED here.
- Probes mutate the fixture, not the checker; checker-side bugs that
  make asserts vacuous in a different way are not covered.
- The t05 P2/P3 failures are caught by cascade (stale DOM), not by a
  direct assert on the mutant's first wrong step.

## Commands (all in ~/workspace/y12-verify unless noted)

- git worktree add --detach ~/workspace/y12-verify ed78e83
- npm install playwright-core@1.65.1 in /tmp/y12-scratch
- run_all.mjs x3 sequential + x3 concurrent load (see Positive runs)
- python3 /tmp/y12/probe.py (12 probes, 11/12 matched)
- git checkout -- tests/realistic/clone1-batch3/results.json (worktree
  restored clean after runs)

## Commit

Log file: improvements/worker-y12-batch3-verify-log.md, committed on
todolist-push as 897ca17 (verified on origin via git ls-remote).
Follow-up commit records this hash.

No em dash or en dash in any file touched. No personal info in any
commit. No ydotool. All runs timed and logged above.
