# Council 2 review: W-PILLFIX-AMEND (5a272ae + a355002)

Reviewer: Council 2, independent (not W-PILLFIX-AMEND, not W-PILLFIX,
not COORD-CLICK-9). Scope: fix R6/C1 (narrow remove_holder) + 3 new
tests + step-0 release. Focus: test completeness and regression
capability. No fix modification, no live run, no reviewer spawning.

Verdict: GO WITH CONDITIONS. The conditions are small follow-ups, not
a rework and not a re-review trigger. The amend itself is accepted:
the R6 hole is closed, the 3 new tests genuinely catch it, and the
full suite shows 0 regression.

## 1. What was reviewed

- improvements/w-pillfix-amend-log.md (read in full).
- Commit 5a272ae (fix + 3 tests + log): scripts/overlay.py,
  tests/test_overlay.py, improvements/w-pillfix-amend-log.md.
- Commit a355002 (docs only: records the 5a272ae hash in the log).
- Old code baseline 8f600b9 (W-PILLFIX).

## 2. Fix correctness (read + caller audit)

- The fix narrows remove_holder to exactly one key via
  _holder_key(agent, pid): pid int > 0 removes only agent:pid; pid
  None removes only the bare agent key. The old code removed the
  pid-keyed key AND the bare key (pid int), or every key of the agent
  (pid None). The new code cannot remove another run's entry. Correct
  and minimal (remove_holder body replaced, docstring updated).
- Caller audit, all callers pass the specific pid they added, or bare
  consistently; none depends on the old wipe-all behavior:
  - overlay.py cmd_acquire D1 exception path (line 532) and invisible
    path (line 547): remove_holder(args.agent, args.pid), removes
    exactly the just-added key.
  - overlay.py cmd_release (lines 561, 569) and daemon release handler
    (line 413): remove_holder(agent, pid) from the request/args,
    removes exactly the named holder.
  - first_action.py acquire_overlay (line 143) and release_overlay
    (line 181): remove_holder(agent, os.getpid()), removes exactly
    this run's pid-keyed entry.
  - overlay.hold() (line 620) acquires bare and releases bare, so it
    is consistent and does not leak under the new code. See gap E4 for
    the pre-existing bare-key sharing, which is out of scope.

## 3. New tests: pass on fix, fail on old code (verified independently)

- Targeted suite on fixed code, run by Council 2:
  `python3 -m unittest discover -s tests -p 'test_overlay.py'`
  Ran 22 tests, OK (19 old + 3 new, all pass).
- Regression check on old code, run by Council 2 in its own worktree
  at 8f600b9 with the new test file copied in:
  Ran 22 tests, FAILED (failures=3), and the 3 failures are exactly
  the 3 new tests
  (test_remove_holder_pid_none_keeps_pid_keyed_holder,
  test_remove_holder_pid_keeps_bare_holder,
  test_cmd_acquire_invisible_keeps_concurrent_holder); the 19 old
  tests still pass. Worktree removed after the check. So the 3 new
  tests genuinely catch R6, they are not decorative.
- The R6 repro in the amend log (holder Muse:999001 survives a failed
  pid-less acquire) is consistent with test 1 and test 3.

## 4. Full suite vs baseline (verified independently, clean runs)

- Fix tree (a355002, clean worktree, gitignored native build artifacts
  copied in so the suite can run):
  Ran 2316 tests in 216.293s, FAILED (failures=1, errors=2, skipped=17).
  Log /tmp/c2-fullsuite-fix2.log.
- Pre-fix baseline (e02286a, parent of 5a272ae, same setup):
  Ran 2313 tests in 214.384s, FAILED (failures=1, errors=2, skipped=17).
  Log /tmp/c2-fullsuite-prefx2.log.
- Delta: +3 tests, all 3 pass, 0 new failures, 0 new errors, skipped
  unchanged (17). The 3 failures are identical in both runs and are
  pre-existing environment failures, unrelated to overlay:
  ERROR setUpClass test_cursor_file.CursorFileTests (g++ C++26),
  ERROR test_tc02_controller
  test_typed_text_check_passes_when_fragment_is_visible (tesseract
  unavailable), FAIL test_tc02_controller
  test_typed_text_check_fails_when_fragment_is_absent (tesseract
  unavailable).
- The worker's numbers (Ran 2316, failures=1, errors=2, skipped=17)
  match my independent fix-tree run exactly, and the worker's log file
  /tmp/w-pillfix-amend-fullsuite.log shows the same summary.
- Note on method: a first worktree run without the gitignored
  native/wtype helper produced 259 errors (private wtype helper
  missing) and Ran 2293; that run is invalid and was discarded. The
  clean runs above copy the 6 gitignored native build artifacts
  (wtype, pointer, keyboard-protocol.c/.h, pointer-protocol.c/.h) from
  the main checkout into the worktrees. A separate full-suite run from
  the main checkout (Ran 2332 = 2316 + 16 ZENPROOF2-FIX tests) is
  consistent, with one extra failure (test_cli_exit_codes, session
  guardian still running on the laptop during a live window) that is a
  live-state artifact, not a regression.

## 5. Step 0 release (verified by read-only laptop state)

- Log claims: holders.json had S2-flip (20:02:18, CDP, pid null) and
  W-PILLFIX (19:40:45, smoke, pid null); release via
  `overlay.py release --agent W-PILLFIX` rc=0 at 20:09:25; after
  release only S2-flip remains; daemon PID 115582 alive.
- Council 2 read-only check (ssh-laptop.sh, no write, no live run) at
  ~20:20 +07: holders.json contains only S2-flip (acquired 20:20:52,
  CDP, pid null); W-PILLFIX is gone; daemon.json pid 115582, started
  2026-11-22T19:40:45+07:00; PID 115582 running, elapsed 40:08.
  S2-flip re-acquired at 20:20:52 (a live run re-acquiring after the
  amend's step 0), which is expected, not a problem. Step 0 outcome
  confirmed.

## 6. Gaps (edge cases of remove_holder not covered)

- E1 (minor, condition): cmd_release with pid=None when a pid-keyed
  holder exists has no test. Under the new code the pid-keyed holder
  survives and the pill stays up; the operator must pass --pid. The
  CLI has no help text for --pid on release (or acquire), so nothing
  tells the operator. The release output does print the remaining
  holders, so it is visible, not silent. But the behavior is untested
  and undocumented.
- E2 (minor, condition): cmd_acquire D1 exception path (daemon/ensure
  failure) has no end-to-end test; only the invisible path is covered
  by test 3. Both paths call the same remove_holder with the same
  args, and test 1 proves remove_holder is scoped, so the risk is
  low, but the path is unproven end to end.
- E3 (trivial, no action): remove_holder with pid=0/negative or
  agent='' behaves equivalently to the old code (pid<=0 maps to the
  bare key via _holder_key; empty agent matches only the empty key).
  Not tested, not worth a test.
- E4 (known follow-up, out of scope): overlay.hold() acquires and
  releases bare, so two concurrent hold() contexts share the bare key
  and one release drops the other's pill. Pre-existing, not introduced
  by this fix, and the fix does not make it worse (old code's release
  would also remove the bare key, plus any pid-keyed ones). The
  follow-up is redteam amend 1 part 2 (hold() and s2_flip pass a real
  --pid), which the amend log already records as a separate lane. Not
  a condition for this amend.

## 7. Log and hygiene

- The amend log has timestamps, commands, outputs, commit hash, and a
  time log (Lauren Tan). Section 6 was added by a355002 as promised.
  0 em dashes in both diffs (checked). No personal info. No live runs
  by the worker. No fix modification by this reviewer.

## Verdict: GO WITH CONDITIONS

- Condition 1 (required, follow-up commit): add a test for cmd_release
  pid=None with a pid-keyed holder present (assert the pid-keyed
  holder survives and the release output still lists it), and add
  --pid help text to the release (and acquire) subparsers stating
  that a pid-less release only removes the bare entry and a pid-keyed
  holder needs its --pid.
- Condition 2 (recommended, same follow-up): add an end-to-end test
  for the cmd_acquire D1 exception path (ensure/daemon failure)
  keeping a concurrent pid-keyed holder, mirroring test 3.
- These are small follow-ups, not a rework and not a re-review
  trigger. The amend itself (R6/C1 fix + 3 tests + step 0) is
  accepted.

## Time log (Asia/Ho_Chi_Minh)

- 20:15:45 +07: task received, started review.
- 20:16: read amend log + diffs (5a272ae, a355002); targeted overlay
  suite on fixed code Ran 22, OK.
- 20:17: caller audit (overlay.py, first_action.py, hold); old-code
  check (8f600b9 remove_holder is the wipe-all version).
- 20:18: baseline repro worktree at 8f600b9 + new test file, Ran 22,
  FAILED (failures=3), exactly the 3 new tests; worktree removed.
- 20:20: read-only laptop check (holders.json, daemon.json, PID
  115582) confirms step 0.
- 20:16:49-20:21:49: full suite from main checkout Ran 2332
  (=2316+16 ZENPROOF2-FIX), failures=2 (1 tesseract + 1 guardian
  live-state), errors=2, skipped=17; guardian failure identified as
  a live-state artifact.
- 20:22-20:28: diagnosed the first worktree full-suite run as invalid
  (259 errors, native/wtype gitignored artifact missing); killed the
  contaminated prefix run; copied the 6 gitignored native build
  artifacts into both worktrees.
- 20:28:37-20:32:14: clean fix-tree full suite (a355002) Ran 2316,
  failures=1, errors=2, skipped=17, same 3 env failures.
- 20:32:14-20:35:50: clean pre-fix baseline full suite (e02286a) Ran
  2313, failures=1, errors=2, skipped=17, same 3 env failures.
- 20:36: worktrees removed, branch up to date, review written.
