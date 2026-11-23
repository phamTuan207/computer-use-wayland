# Worker C4-STEP1-CLOSEOUT log: AMEND4 step-1 close-out verification

Owner: the owner. Worker: C4-STEP1-CLOSEOUT, for COORD-CLICK-4.
Branch: todolist-push. Repo HEAD at start: 36364b1
(36364b16c9223b15a415e037fd117593424d064f).
Start: 2026-11-22 08:48 +07 (Asia/Ho_Chi_Minh). All times below are
wall-clock +07 unless noted. Verification only, no code fixes.
Standing rules: no em dash (U+2014) or en dash (U+2013) anywhere in
this file, no personal info, never ydotool, full access, explicit
pathspec commits only, every push verified with git ls-remote.

Basis read first: improvements/worker-click3-final-direction-log.md,
sections 0.1 (V-Z1, V-Z2), 1.1 (A7 row), 1.4 (CB-9 row), 3 step 1,
6 worker 3, 7 (item-12 owners).

Headline: item-12 tests 4/4 PASS; Codex-lane item 12 LANDED (via the
resume run, not the first run); S0 soak verdict PASS advisory for the
keepalive form only, plain form NOT FEASIBLE; full discover at
36364b1: Ran 1974 in 248.397s, 0 failures, 4 pre-existing errors,
17 skipped; the Y1b 8 issues are GONE; CB-9 manifest for the bench
build a1a672d NOT locked, installed artifact hashes missing.

## 1. Item-12 regression tests (task a): 4/4 PASS

The four tests landed in cbab398, all in class TestRun in
tests/test_first_action.py (lines 977, 1003, 1023, 1041):

- test_session_after_is_scope_matching_not_screen
- test_fallback_after_is_scope_matching_not_screen
- test_after_without_result_after_captures_fresh_window
- test_screen_observation_key_batch_refused_before_overlay

Command (repo root, HEAD 36364b1):

```
python3 -m unittest tests.test_first_action.TestRun.test_session_after_is_scope_matching_not_screen tests.test_first_action.TestRun.test_fallback_after_is_scope_matching_not_screen tests.test_first_action.TestRun.test_after_without_result_after_captures_fresh_window tests.test_first_action.TestRun.test_screen_observation_key_batch_refused_before_overlay -v
```

Run: 2026-11-22 08:49:39-08:49:40 +07 (01:49:39-01:49:40 UTC).
Output (verbatim tail):

```
test_session_after_is_scope_matching_not_screen ... ok
test_fallback_after_is_scope_matching_not_screen ... ok
test_after_without_result_after_captures_fresh_window ... ok
test_screen_observation_key_batch_refused_before_overlay ... ok
Ran 4 tests in 0.008s
OK
```

Result: PASS 4/4. This closes the open test-pass evidence from the
final direction (V-Z1: shape verified from the diff only, tests not
run by anyone).

Supporting run, same session, whole file:

```
python3 tests/test_first_action.py
```

Ran 71 tests in 0.762s, OK. That is the 4 item-12 tests plus the
3 TEST-REPAIR-C12 tests (2ec3d67) plus the 64 pre-existing tests,
matching the reconcile log count (71 OK at 77c72be).

## 2. Codex-lane item-12 confirmation (task b): LANDED via resume

The final direction V-Z2 (06:19 queue-check, 0 hits, Result still
pending) is now STALE. The Codex lane did land item 12, in a second
run. Evidence, in order:

- First run (driver log
  improvements/worker-codex-amend4-driver-log.md, committed e77bc7b):
  Codex session 01a20054 finished 07:21 +07 with 15 commits on
  branch amend4-codex, HEAD 274270c, items 1-11 only. The queued
  follow-ups (item 12, first principles, pragmatic rule, message
  01a20058) never surfaced in the exec log (final grep 0 at 07:21);
  the queue ID persisted in ~/.codex/queue_1.sqlite-wal
  but the live exec process never consumed it. Item 12 was NOT
  implemented in that run.
- Resume run (resume log
  improvements/worker-codex-amend4-resume-log.md, committed 2de4c31):
  launched 07:27 +07, `codex exec resume
  01a20054-e53a-77c3-a0f1-383a3b6f409f` with
  /tmp/codex-amend4-followup.md, finished 07:48 +07 (about 21 min).
  Four new commits on amend4-codex:
  ee8ccb7 "test: reproduce act-now scope and after-image defects",
  aa0fbbb "test: cover chainable act-now fallback after-image",
  f4c0482 "fix: separate chainable and screen act-now captures",
  06a34e8 "docs: record amend4 first-principles and item 12".
- Remote HEAD verified this session: `git ls-remote origin
  amend4-codex` returns
  06a34e8610a9467c3884f6dd7a567293c747da45, matching the resume
  worker's laptop and VM checks at 07:48 +07. Local
  origin/amend4-codex in this repo is also 06a34e8 (19 commits
  from base f0ddd41).
- Three new item-12 tests on the Codex lane (resume worker
  verification, run on the laptop worktree):
  test_after_preserves_input_scope_and_labels_screen_capture,
  test_screen_scoped_key_refuses_before_overlay,
  test_fallback_returns_desktop_act_after_as_chainable. All pass.
  test_first_action.py on the Codex lane: Ran 67 tests, OK
  (64 + 3 item-12). 15 RT proof tests: Ran 15, OK. R7 shadow:
  Ran 3, OK. Codex-lane full discover (from its log, not re-run
  by me): Ran 1925 in 127.084s, FAILED (failures=2, errors=4,
  skipped=2).
- Reconciliation (worker-click3-reconcile-amend4-log.md, e1a4e77,
  item 12 row): SAME design, VM shape kept. Codex gap recorded
  there: when no result after exists (or it is scope-mismatched),
  its envelope after is None instead of a fresh window capture;
  and its pre-overlay refusal is stricter (refuses scopeless
  metas the VM lane deliberately accepts). Verdict KEEP VM.

Conclusion: Codex-lane item 12 is LANDED, not open. No
re-commission is needed for the item-12 delivery itself. What
remains open is the round-3 council judgment on the VM-vs-Codex
shape difference (already recorded in the reconcile log), which
is not this worker's task. I launched no Codex run.

## 3. S0 soak result (task c): keepalive PASS advisory, plain NOT FEASIBLE

Soak logs found (PROBE-S0 follow-up commits):

- improvements/worker-probe-s0-log.md, final commit 39e1450
  (2026-11-22 ~07:53 +07).
- improvements/worker-s0-impl-log.md, follow-up commit 8817a90
  (~07:55 +07), section 7 soak-B verdict plus push record
  18f2304.

Wording correction: the final direction calls this a "1-day soak
ending about 07:41 +07". No 1-day soak log exists. The soak on
record is a 60-minute soak pair (plain master vs keepalive
master), whose t+60 tick was due about 07:42:31 +07 and is
UNCONFIRMED. The "1-day" label in the direction is a mislabel;
the 07:41 time matches the 60-minute soak's scheduled end.

Plain soak (no ServerAliveInterval, master pid 13662 from
06:41:20 +07, samples every 10 min plus keepalive every 5 min):
12 confirmed ticks t+0..t+55. t+0: 0.894s rc=0 (fast mux). The
other 11 ticks: 4.461-5.929s, each a fresh-connect fallback with
a NEW master pid each time. Master survived 60 min (plain): NO.
Died 11 times in 55 min. Fallback mean 5.141s.

Keepalive soak-B (ServerAliveInterval=15, master pid 25435 from
07:00:06 +07): 9 confirmed ticks t+0..t+40 in the probe log, all
on the SAME master pid, all rc=0, mean 0.958s. S0-IMPL log
section 7 adds t+45 keepalive 1.822s and t+50 1.078s, same pid.
Master survived 50 min (keepalive): YES, 11/11 confirmed ticks
fast, zero deaths, zero fallbacks.

Why the soak is incomplete: the VM restarted about 07:51 +07
(uptime 1 min on recovery), wiping /tmp (soak logs, sockets,
masters). Ticks t+55 and t+60 never ran. The verdict rests on
the t+0..t+50 rows recorded before the restart.

Verdict (as recorded in both logs): S0 is FEASIBLE ONLY with
ServerAliveInterval on the master (plus setsid/nohup start, never
ssh -f, plus ControlMaster=auto clients). As specified without
keepalives it delivers zero saving at real cadences. With
keepalives it delivers 3.49x, 3.33s saved per connection,
residual about 1.3s per session. 460x is refuted. Advisory, not
a gate (a master death falls back to fresh SSH, slow but
correct). No soak process remains; nothing to stop.

## 4. Full discover at HEAD 36364b1 (task d): 1974 tests, 0 failures

Clean worktree: /tmp/click4-step1-discover, `git worktree add
/tmp/click4-step1-discover 36364b1` (detached HEAD, verified
36364b16c9223b15a415e037fd117593424d064f). Untracked native
artifacts copied in from the main checkout first, per the
reconcile-log worktree lesson (a fresh worktree lacks them and
the numbers would be environmental, not HEAD evidence):
native/pointer, native/wtype, native/keyboard-protocol.c/.h,
native/pointer-protocol.c/.h. Worktree status clean before the
run. Main checkout untouched by this run.

Command (from tests/ in the worktree, same command as the
reconcile run):

```
PYTHONPATH=../scripts:. python3 -m unittest discover -s . -p "test_*.py"
```

Launched detached 08:50:43 +07 (01:50:43 UTC), log
/tmp/click4-discover.log, finished about 08:54:54 +07 (log
mtime 01:54:54 UTC). Output tail (verbatim):

```
Ran 1974 tests in 248.397s
FAILED (errors=4, skipped=17)
```

Failures: 0. Errors: 4, all pre-existing baseline, identical
to the 4 errors at 77c72be:

1. test_a11y_skeleton (unittest.loader._FailedTest):
   ModuleNotFoundError: No module named 'tests'
   (test_a11y_skeleton.py line 8, `from tests import test_a11y`).
2. test_cursor_file.CursorFileTests.setUpClass: harness compile
   failed, g++ error unrecognized command-line option
   '-std=c++26' (did you mean '-std=c++20'?).
3. test_perf_evidence.EvidenceChecks.test_valid_normal:
   FileNotFoundError docs/benchmarks/r5_cdp_aggregate.json.
4. test_perf_evidence.EvidenceChecks.test_valid_optimized: same
   missing JSON.

No FAIL lines in the log (grep for ^FAIL: returns nothing).
Zero EPERM/tempfile failures. Skipped: 17, same as 77c72be.

Reconciliation with the 77c72be baseline (reconcile log:
Ran 1974 in 207.962s, failures=2, errors=4, skipped=17): same
test count (1974), same errors (4), same skipped (17), but
failures dropped 2 to 0. The 2 failures at 77c72be were
test_browser_image test_persist_false_returns_rgb_without_state
(RGB and RGBA), caused by the S0 J37 keys; they were fixed by
e83b72d ("test: update browser_image expectations for S0 J37
jpeg keys"), with the log 56179a3 recording failures 2 to 0.
Wall time 248.397s vs 207.962s at 77c72be is VM contention, not
a code change (another worker's discover was running
concurrently from 01:53 UTC; I did not touch it).

Y1b 8-issue status: GONE at 36364b1. Clone2 batch 10 task 2
(fix pass, b8c908a) found at 17fdb9b: 8 issues in test_code_exec
(4 failures, 3 errors) and test_codemode (1 failure), executor
recording zero backend calls (windows_calls 0 instead of 4,
calls list empty), consistent with the Y1b forked-child change.
At 36364b1, neither file appears in the failure or error list.
Direct re-run in the same clean worktree, same session:

```
PYTHONPATH=../scripts:. python3 -m unittest test_code_exec test_codemode
```

Ran 81 tests in 14.757s, OK (test_code_exec 55, test_codemode
26). Failing test names per file at 36364b1: none in either
file. The Y1b executor fix (Y1B-RPC-LAND, ed2d559) plus
TESTREPAIR-D (29083cd, codemode builtins-pin test captures via
a temp file because exec now runs in the forked child) closed
all 8 between 17fdb9b and 36364b1.

Note: the other worker's discover (PID 36565/36566, from
~/workspace/computer-use-wayland, log
/tmp/step5-baseline-discover.log, started 01:53 UTC) was
running concurrently and is NOT mine; I left it alone.

## 5. CB-9 manifest for the bench build a1a672d (task e): NOT locked

What exists:

- Source commit: bench code at 7f3a70b (bench file commit
  c5311ce, blob 80b00469c4676d7a9a8934626b6bf66ed2a5aeee, 868
  lines, matches origin/main; fixture commit 7f3a70b, blob
  bac2702efa375ad330cce8130df40d8025d86261, 48 lines; base
  49081aa). Log commit a1a672d
  (a1a672db3d93d19bbd5a44868ea7ed43cb9fa876, 2026-11-22 06:44
  +07), "probe-s2: fixture 2-vision bench PASS 10.86s, Y1b 3
  fails still open, flag NOT flipped (gate b unmet)", push
  verified via git ls-remote at commit time.
- Log of the same build: improvements/worker-probe-s2-log.md
  (a1a672d) plus /home/hatch/probe-s2-work/results.json, still
  present, 733 bytes: run_id bench-20261121T234030Z-86e8d8,
  mode run, live false, visions_used 2, outcome PASS,
  wall_s 10.8596, both sends V12-gated (clone1 0.6904s,
  clone2 0.6807s). Bench run 06:40:30-06:40:41 +07, EXIT 0.
  Runtime: Firefox 160.0.1, geckodriver 0.36.0, selenium
  4.53.0, installed at /home/hatch/workspace/tools/ for the
  probe (environment setup, not a bench edit).

What is missing (manifest cannot be locked):

- Installed artifact hashes: NONE exist for this build. No
  deploy-manifest.json exists anywhere in the repo (find
  returns nothing; only the mechanism references it in
  scripts/sync-installed.py, tests/test_s0_bundle.py, and the
  S0-IMPL log). The CB-9 manifest mechanism
  (_write_deploy_manifest in sync-installed.py) only landed in
  18f2304 (S0-IMPL), AFTER the bench ran at 06:40 +07, so no
  manifest could have been written for the bench build.
- The bench ran from the VM repo checkout, not from an
  installed tree, so there was no installed artifact set to
  hash at bench time. The VM checkout has since moved on, so
  the installed-at-bench-time tree cannot be reconstructed
  from a manifest now; only the git blobs above pin the code.
- Laptop drift (why a manifest is needed, from the final
  direction section 2 item (i), FCODEX V-F7 / FGROUND V-F10,
  read-only SSH check 06:40 +07): installed first_action.py
  23442 bytes vs repo 33893 bytes, installed cu.py also
  differs, laptop HEAD 3790901 at that check. That drift is
  about the laptop installed tree, not the bench build, and it
  was never resolved by a manifest either.

Conclusion: the CB-9 manifest for a1a672d is NOT locked. The
bench pass (10.86s, PASS, run_id
bench-20261121T234030Z-86e8d8) must not be quoted as a gate
until a manifest is locked, per the final direction section 4
precondition. A retroactive manifest cannot be manufactured:
the build predates the mechanism and the installed tree at
bench time is gone. The honest record is the source blobs,
the probe log, and results.json above.

## 6. Side observation (evidence preservation)

docs/clone2-amend4-reverify-20261122.md (clone2 batch 10 task 2
report, commits 84e4519 and b8c908a) does NOT exist at HEAD
36364b1: `git cat-file -t
HEAD:docs/clone2-amend4-reverify-20261122.md` returns "fatal:
path does not exist in HEAD", and no deletion commit for it
appears in `git log --all`. It is reachable only via `git show
b8c908a:docs/clone2-amend4-reverify-20261122.md` (the version
quoted in section 4 above). Likely dropped in a shared-branch
rebase; not investigated further here.

## 7. Commit record

- Log file: improvements/worker-click4-step1-closeout-log.md
  (this file).
- Commit: 4ac9320
  ("docs: C4 step-1 closeout, item-12 4/4 PASS, Codex-lane
  landed, discover 1974 0 failures, Y1b 8 gone, CB-9 manifest
  not locked"), 1 file, 322 insertions, on top of 65a2df6.
- Push verification: 2026-11-22 about 08:58 +07, `git ls-remote
  origin todolist-push` returns
  4ac9320f77f5fa47c48c6d51fdd3f3a0c443529f, matching local HEAD.
- Commit-record follow-up: this section filled in by commit
  (filled at commit time, second commit).

Elapsed: task received about 08:48 +07; item-12 tests 08:49
+07; discover launched 08:50 +07, finished about 08:54 +07;
executor re-run about 08:56 +07; log written about 08:57 +07.
Total about 9 min of wall time plus the 248s discover run.
