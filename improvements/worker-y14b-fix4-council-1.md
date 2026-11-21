# Council 1 paper: fix pass 4 over fix-pass-3 redteam verdict (AMEND bd3c6c9)

- Subject: Worker Y14b fix pass 4, commit bf3c939741f86c6c639c730882f8a4f721265a74
  (todolist-push, ls-remote verified before review).
- Scope: ONLY the fix-pass-4 diff against its parent. Code changes are in
  tests/realistic/run_batch3.py; plan H4 wording in
  improvements/worker-y14-batch3-live-plan.md; log adjudication plus
  verification in improvements/worker-y14b-restage-log.md. The whole
  runner was NOT re-reviewed.
- Role: Council 1 (transcription and verification). No live Zen driving.
  No ydotool. No em/en dash in this paper.
- Verdict: **AMEND** (doc-only fixes; no code change required before ship).

## Method

1. Diff read line by line: `git show bf3c939 -- tests/realistic/run_batch3.py`
   (328 lines, 9 hunks, all in the scanner region lines 2309-2665).
2. Blob identity re-verified: `git show bf3c939:tests/realistic/run_batch3.py`
   gives blob 585fb8016b0618ab02b3e97afa362dbcce7342c9 and md5
   2920f1697edb3b33711b83b8a874d88b, exactly the values in the task brief.
   Parent blob 3875215 is 3a9b7b173c2d2d8e7ca1cc717e22d613bf376727, md5
   e9e3519af09fb5e1066a2a516dddda05. run_batch3.py is unchanged between
   bf3c939 and HEAD (`git log bf3c939..HEAD -- tests/realistic/run_batch3.py`
   empty), so the current tree is the reviewed code.
3. Independent differential probe /tmp/y14b-c1-diff-probe.py: loads both
   blobs as separate modules and compares _is_runner_cmdline and
   _is_codex_executor on every redteam example plus Council-1 boundary
   shapes (51 cases). Pure unit calls, no processes spawned.
4. All 8 claimed probes re-run against the current tree; PASS lines
   counted only (the "FAILURES:" summary line starts with FAIL and is
   excluded, per the F9 correction).
5. Live re-proof of the R1/F1/F9 execution claims with the dummy stub
   in /tmp/y14b-dummies (timeout-guarded, all stub processes verified
   gone afterwards).
6. H4 margin arithmetic re-derived independently with Decimal.
7. t10 assert set re-extracted independently from check.mjs at 1d23532
   and compared with run_b3_t10.

## Verification: probes re-run (all green, exact counts)

Command (each probe, exit code, PASS lines, FAIL lines):

- `python3 /tmp/y14b-transcribe.py`: exit 0, 82 PASS, 1 FAIL line
  (the "FAILURES: 0 []" summary only).
- `python3 /tmp/y14b-fix4-probe.py`: exit 0, 64 PASS, 1 FAIL line
  (summary only).
- `python3 /tmp/y14b-h2-probe.py`: exit 0, 45 PASS, 1 FAIL line (summary).
- `python3 /tmp/y14b-fix2-probe.py`: exit 0, 31 PASS, 1 FAIL line (summary).
- `python3 /tmp/y14b-fix3-probe.py`: exit 0, 70 PASS, 1 FAIL line (summary).
- `python3 /tmp/y14b-gate-dry.py`: exit 0, 4 PASS, 1 FAIL line (summary).
- `python3 /tmp/y14b-m1-probe.py`: exit 0, 3 PASS, 1 FAIL line (summary).
- `python3 /tmp/y14b-fix2-m1-probe.py`: exit 0, 4 PASS, 1 FAIL line (summary).

All counts match the log exactly. The F9 count correction (fix3 is 70,
not 72) is confirmed: the earlier 72 counted the summary line.

## Verification: code changes match the log, claim by claim

Differential probe result: 51/51 cases behave as the log claims for the
new code, 0 failures. Key rows (old blob 3875215 -> new blob bf3c939):

- R1 `python3 -m run_batch3.py`: False -> True. Same for `-u -m`,
  `-um`, `-mrun_batch3.py`. `python3 -m foo.run_tests.py` stays False;
  `python3 -m foo.run_batch3.py`: False -> True. The -m branch now
  runs before the runner-basename block (run_batch3.py:2446-2452) and
  _is_runner_module strips a trailing .py (run_batch3.py:2518-2521).
- F1 `python3 -crun_batch3.py`: True -> False. `python3 -c
  run_batch3.py`: True -> False. `bash -c run_batch3.py` stays True;
  `codex -c run_batch3.py`: True -> False. The -c branch now requires
  `prev == "-c" and _c_is_shell(tokens, i - 1)` plus the no-script-token
  check (run_batch3.py:2464-2471).
- F2 `bash -c "codex -c 'import time; x # marionette'"`: False -> True.
  _same_command_tokens extends past a -c flag (run_batch3.py:2641-2648).
- F3 `pytest -m run_batch3`, `echo -m run_batch3`, `echo import
  run_batch3`, `python3 other.py -m run_batch3`, `python3 script.py
  import run_batch3`: all True -> False. `python3 -c "import
  run_batch3"` stays True. `python3 run_other.py -m run_batch3` stays
  True (via run_other.py itself, the basename block, not the -m
  branch). The -m and import branches are guarded by _python_executes
  (run_batch3.py:2449-2452, 2498-2506).
- F4 `bash -c "python3 --version; pytest -W ignore run_batch3.py"`:
  True -> False. `bash -c "python3 -W ignore run_batch3.py"` stays
  True; `bash -c "python3 --version; python3 -W ignore run_batch3.py"`
  stays True. _python_executes stops at separators and -c
  (run_batch3.py:2329-2335).
- F5 `python3 run_other -W ignore run_batch3.py`: True -> False. See
  finding C1-1: the code change is real and correct, but the log and
  plan describe its outcome backwards.
- F6 `python3 -c "codex marionette"`: True -> False. `bash -c "codex
  exec marionette"` stays True. _codex_at_command bounds -c only when
  it is a shell -c (run_batch3.py:2577-2583).
- F7 `bash -c "codex --help;echo marionette"`: True -> False.
  `bash -c "codex exec marionette;echo done"` stays True.
  `bash -c "echo hi; codex exec marionette"` stays True.
  `bash -c "echo marionette;foo codex --help"` stays False (backward
  direction: old code included the marker across the glued separator,
  new code stops at it). Glued separators split in _same_command_tokens
  both directions (run_batch3.py:2633-2637 forward, 2650-2657 backward).
- F8 sudo restored: `grep -c sudo` on run_batch3.py is 0 at 3875215
  and 1 at bf3c939 ("nice and sudo wrappers", run_batch3.py:2566-2568).

## Verification: live execution claims re-proved

In /tmp/y14b-dummies (sleeping run_foo.py stub), timeout 3:

- `python3 -m run_foo.py`: exit 124 (executes).
- `python3 -mrun_foo.py`: exit 124 (executes).
- `python3 -um run_foo.py`: exit 124 (executes).
- `python3 -m run_foo`: exit 124 (executes).
- `python3 -crun_foo.py`: exit 1, `NameError: name 'run_foo' is not
  defined` (never runs).
- `python3 --check-hash-based-pycs=always --version`: exit 2,
  `unknown option --check-hash-based-pycs=always` (F9 joined form).
- `python3 --check-hash-based-pycs always --version`: exit 0, prints
  `Python 3.12.3` (F9 spaced form).

No stub processes left: `ps aux | grep -E "y14b|run_foo|run_shebang" |
grep -v grep` returns nothing (exit 1). (Two stale y14b-c2 dummy
processes seen mid-review belonged to another worker's /tmp/y14b-c2
directory and had already exited on their own; they were not touched.)

## Verification: H4 margin arithmetic re-derived (F10)

Model (from the plan note): position units = (850 + N*R)/100, where N
is effective round trips and R is ms per round trip; 1 tick = 100 ms;
bound is 2..11. Recomputed with Decimal, half-up to 2 places:

- N=3.5, R=2: pos 8.57, margin 11 - 8.57 = 2.43.
- N=3.5, R=19: pos 9.165, margin 11 - 9.165 = 1.835, half-up 1.84.
  Matches the plan "1.84-2.43 continuous at the stated N=3.5" and the
  fix-pass-3 redteam recomputation (1.835 half-up to 1.84).
- N=3, R=2: margin 2.44; N=3, R=19: margin 1.93. Matches the plan's
  "earlier 1.93-2.44" (the N=3 range, corrected by fix-pass-2 redteam F6).
- First fail (continuous == 11): N=3.5 gives R = 250/3.5 = 71.43 ms;
  N=3 gives R = 250/3 = 83.33 ms. Matches the plan "roughly 70-85 ms".
- Sure fail (continuous == 12): N=3.5 gives R = 350/3.5 = 100.00 ms;
  N=3 gives R = 350/3 = 116.67 ms. Matches the plan "~100-117 ms".
- One round trip at 19 ms = 0.19 ticks. Matches "the two counts
  differ by at most 0.19 ticks".
- Reads: N=3.5, R=2 gives 8.57 (reads 8-9 with phase); R=19 gives
  9.165 (reads 9-10); R=50 gives 10.25 (reads 10-11, margin 0-1).
  Matches "correct fixture reads about 8-10" and "at 50 ms/round trip
  it reads 10-11 (margin 0-1)". Discrete margin 11 - read is 1-3
  (reads 8, 9, 10). Matches "margin 1-3 discrete ticks".
- F10 correction confirmed: the true count is 3.5, so Council 1's 3
  undercounts by half a round trip (3.5 - 3 = 0.5) and Council 3's 4
  overcounts by half (4 - 3.5 = 0.5). The plan diff shows the new
  wording states exactly this and the "bracket" phrasing is gone
  (plan diff hunk at line 641-647).

## Verification: t10 assert set vs check.mjs at 1d23532

- check.mjs at 1d23532 (extracted with `git show
  1d23532:tests/realistic/clone1-batch3/t10-music-player/check.mjs`,
  md5 c55ef3c792b2faaea7c829818eb6420b, 353 lines) has 33 expectText
  calls and 36 failures.push sites. The runner adds 3 volume checks
  (volume 50 after click, volume 0 after Home, volume 30 after arrows)
  that check.mjs does not have (check.mjs only asserts volume-value
  30). 33 + 36 + 3 = 72, exactly the transcription probe's ORDERED
  count (72 ordered entries; 72 + 2 D1 + 2 exact-zero + 4 sleep + 2
  sampler = 82 PASS lines, re-run confirmed).
- Thresholds cross-checked independently, check.mjs vs run_b3_t10:
  exact-zero `!== 0` x6 vs runner `== 0` x6; sampler `min > 2 ||
  min >= posBefore` x3 vs runner `min_after <= 2 and min_after <
  pos_before` x3; gain `< 2` x6 plus wrap-gate `< 2` x2 vs runner
  `2 <=` x8; range `< 2 || > 11` x8 vs runner `<= 11` x8; playlist
  `!== 5` x2 vs runner `== 5` x2; seek `pos < 85 || pos > 100` vs
  runner `85 <= pos <= 100`. No threshold changed.
- One label wording difference, no semantic effect: check.mjs what is
  'repeat All before wrap test', the runner's label is '"repeat All
  before wrap"' (the word "test" dropped). The probe's order check
  accounts for it.
- The fix-pass-4 diff has zero t10 hunks (all 9 hunks are in the
  scanner region, lines 2309-2665), so fix pass 4 changed no t10
  threshold by construction.
- Note: check.mjs is NOT in the todolist-push tree (1d23532 is not an
  ancestor of HEAD; `git ls-files | grep t10-music-player` is empty).
  The comparison above was done against the 1d23532 blob from git, as
  the task specifies. This does not affect the verdict; it only means
  the transcription probe's reference is the 1d23532 blob, not a
  worktree file.

## Findings

### C1-1 (MEDIUM, doc): F5 outcome stated backwards in the log and the plan

- Log (fix-pass-4 adjudication, F5): "`python3 run_other -W ignore
  run_batch3.py` is now True via run_other itself."
- Plan (fix-pass-4 bullet, F5): same sentence, "is now True via
  run_other itself".
- Reality: the cmdline returns False in the new code. Evidence:
  differential probe row `F5 python3 run_other -W ignore
  run_batch3.py: old=True new=False want=False`; the fix4 probe
  itself expects False for this case
  ("python3 run_other -W ignore stays False") and passes 64/64.
  Extensionless `run_other` is not a runner basename
  (_script_basename_is_runner requires a .py suffix for run_*,
  run_batch3.py:2217-2225), so nothing in the cmdline is a runner and
  False is the CORRECT verdict; the old True was the false positive
  (the -W two-back rule firing through the missing barrier).
- The code fix is real and correct; only the record is wrong. The
  fix4 probe label "stays False" is also wrong about history: the
  verdict changed True -> False, it did not stay False.
- Fix (doc-only): in the log F5 bullet and the plan F5 bullet, replace
  the sentence with: "`python3 run_other -W ignore run_batch3.py` is
  now False (it was True in fix pass 3, a false positive through the
  -W two-back rule); extensionless run_other itself remains
  undetected as a runner (recorded residual)". Correct the probe
  label to "now False" as well, or leave the probe and note the label
  is historical.

### C1-2 (MEDIUM, doc, ship-blocking if uncorrected): pinned ship-time md5 is stale

- Plan at bf3c939, ship-time md5 procedure (lines 612-615): "compare
  against the md5 recorded in the re-stage log's fix-pass-3 entry:
  e9e3519af09fb5e1066a2a516dddda05 (git blob
  3a9b7b173c2d2d8e7ca1cc717e22d613bf376727, commit 3875215)".
- The log at bf3c939 contains no superseding fix-pass-4 entry
  (`grep 2920f169|585fb80` on the log at bf3c939 returns nothing).
  The fix-pass-3 entry (log lines 496-498) is the last md5 record,
  and the fix-pass-2 and fix-pass-1 entries each recorded "ship-time
  expected values ... supersedes the fix-pass-N values", so the
  convention is that each fix pass updates the pinned values. Fix
  pass 4 did not.
- The actual fix-pass-4 file is blob
  585fb8016b0618ab02b3e97afa362dbcce7342c9, md5
  2920f1697edb3b33711b83b8a874d88b (re-verified above). The procedure
  says "Any mismatch refuses the slot", so shipping the fix-pass-4
  runner and following the pinned procedure false-refuses the slot.
- Fix (doc-only, before ship): update the plan's md5 line to the
  fix-pass-4 values (blob 585fb8016b0618ab02b3e97afa362dbcce7342c9,
  md5 2920f1697edb3b33711b83b8a874d88b, commit bf3c939) and add a
  superseding line to the log's fix-pass-4 verification section.
  This is the one finding that must be fixed before the slot runs;
  it is doc-only, so AMEND, not BLOCK.

### C1-R1 (LOW, record): import guard still leaks across a shell separator

- `bash -c "python3 -c 'import x'; echo import run_batch3"` flags
  True in BOTH blobs (differential probe rows F3-RESID, glued and
  spaced `;`). The import branch finds the nearest -c by scanning
  back to index 0 without stopping at separators
  (run_batch3.py:2498-2501), so a python -c from an earlier command
  legitimises an `import run_batch3` that is an echo argument in a
  later command. The log's F3 claim holds for its stated examples
  (bare `echo import run_batch3` now misses); this is the narrower
  residual. A token-level fix is fiddly (a `;` inside a -c string is
  Python code, not a shell separator, and is indistinguishable after
  _argv_tokens splits on whitespace), so record it instead of
  fixing it in this pass. Fail-closed false positive, contrived
  shape. Add one line to the known-limitations docstring.

### C1-R2 (LOW, record): non-run_ extensionless script is still not a barrier

- `python3 other -W ignore run_batch3.py` flags True in BOTH blobs
  (differential probe row F5-RESID). The barrier set covers .py,
  -m, -c and extensionless run_* only (run_batch3.py:2342-2346); a
  generic extensionless script ("other") is not recognised, so the
  -W two-back rule still fires through it. Same class as F5, fixed
  only for run_*. Fail-closed false positive, contrived shape. Add
  one line to the known-limitations docstring.

### C1-R3 (INFO, pre-existing, record): glued `;codex` still misses

- `bash -c "echo foo;codex marionette"` and `bash -c "cd
  dir;codex exec marionette"` return False in BOTH blobs
  (differential probe rows F7-GLUED, F7-GLUED2). The codex token
  never exists: _argv_tokens splits on whitespace, so "foo;codex" is
  one token whose basename is not "codex", and _is_codex_executor
  requires an exact codex token. This is a token-identity gap one
  layer below _same_command_tokens, NOT a fix-pass-4 regression (old
  blob misses it too) and NOT claimed fixed by fix pass 4. Record it
  in the known limitations for a future pass; do not hold the ship
  for it (no fleet launcher uses the glued `;codex` form; all H2
  live executor forms are spaced).

### C1-R4 (disclosed, no action): F2 later-command marker over-inclusion

- `bash -c "codex -c 'prompt'; echo marionette"` flags True in the
  new code, False in the old (differential probe row F2-DISC). This
  is exactly the over-inclusion the log discloses ("A marker in a
  LATER shell command would also count, but that form is contrived
  and the gate is fail-closed") and the code comment repeats
  (run_batch3.py:2644-2648). Disclosure matches behavior. No action.

## Ship condition: CONFIRMED with amendment

- The H4 watch item is actionable as written: the runner records
  details["positionAdvancingAfterNext"] (run_batch3.py:1588) and
  details["positionAdvancingAfterShuffleNext"] (run_batch3.py:1730),
  and the plan's ship condition instructs the live run to report a
  repeated read of 11 as a thin margin instead of a fixture failure.
- The round-trip re-measurement is procedural: no dedicated
  round-trip probe exists in the runner; the live run derives the
  round-trip time from the recorded step timings (live_metrics.py,
  scripts/live_metrics.py, records think/act/wait/exec per step) plus
  the recorded advancing reads. That is sufficient for the watch
  item, and the condition is confirmed as written.
- Amendment: C1-2 must be fixed before the slot runs. The pinned
  ship-time md5 still points at the fix-pass-3 file, so following the
  procedure as written false-refuses the fix-pass-4 runner. Update
  the plan md5 line and add the superseding log line first.

## Hygiene

- `python3 -m py_compile tests/realistic/run_batch3.py`: OK.
- Import OK, 10 tests registered.
- Em/en dash in the fix diff: 0 (`grep -c` for U+2014 and U+2013
  over the three-file diff returns 0; the code diff alone also 0).
- ydotool: the only 2 hits in the diff are the words "no ydotool"
  in the commit message and the log (assertions of absence), not uses.
- Personal info: the only hit is the git Author line (commit
  metadata, not file content). No names, emails, addresses or phone
  numbers in any committed file content.
- No live Zen driving by this council; all live checks used the
  /tmp/y14b-dummies stub only. All stub processes verified gone.

## Verdict: AMEND

The code is correct: every R1/F1-F8 claim verifies against the diff,
against the old blob, and live where the log claims live proof; all 8
probes re-run green with exact counts; the H4 arithmetic re-derives
exactly; the t10 assert set matches check.mjs at 1d23532 with no
threshold changed. Ship after the doc-only fixes: correct the F5
sentence in the log and the plan (C1-1), update the pinned ship-time
md5 to the fix-pass-4 values (C1-2, required before the slot), and
record the three residuals in the known-limitations docstring
(C1-R1, C1-R2, C1-R3). No code change is required. Ship still waits
for the redteam re-review over the fix-pass-4 diff, per the plan.
