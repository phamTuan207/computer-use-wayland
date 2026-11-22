# Council 1 review: W-PILLFIX-AMEND2 (pid-keyed holders, R11, E1/E2, H2, C2/R4)

Reviewer: Council 1, independent (not W-PILLFIX-AMEND2, not
W-PILLFIX-AMEND, not COORD-CLICK-9). Report goes to Muse tong, not
directly to the owner. No amend modified, no live proof run, no
reviewer spawned, S2-flip holder NOT released (brief forbids it).
All verification is code/unit level plus read-only laptop checks,
plus my own re-runs of the targeted and full suites. No em dash or
en dash anywhere in this file. No personal info.

## 0. Task and sources (20:53 +07, 22/11/2026)

- Task received ~20:53 +07. Branch todolist-push, repo
  ~/workspace/computer-use-wayland, HEAD 4a4fae3 at review start.
- Amend under review, 3 commits:
  - 14cf4dc code + tests: 6 files, 305 insertions, 26 deletions.
  - 448fee6 amend log (286 lines).
  - 4a4fae3 log hash update (3 lines).
- Sources read before judging:
  - improvements/w-pillfix-amend2-log.md (full, 286 lines).
  - Full diff of 14cf4dc (scripts/overlay.py, scripts/s2_flip_live.py,
    scripts/hypr_cmd.py, tests/test_overlay.py,
    tests/test_s2_flip_pill.py, tests/test_hypr_cmd.py).
  - The 4 amend-1 reviews (council-1 e2ed4e8, council-2 1f28b3f,
    council-3 f294661, redteam 5d5111f) as the condition list.
  - scripts/overlay.py prune_dead_holders (line 155),
    apply_holders (line 309), _monitor (line 359), cmd_release
    (line 568), hold (line 626).
  - scripts/first_action.py acquire/release (lines 128, 176),
    scripts/cdp.mjs acquire/release (lines 65, 79),
    scripts/session_cleanup.py find_leftovers (line 52).

## 1. Time log (wall-clock Asia/Ho_Chi_Minh)

- 20:53 +07, T+0m: task received, amend log read, git fetch, diff stat.
- 20:55 +07, T+2m: code diff read in full (overlay, s2_flip, hypr_cmd).
- 20:56 +07, T+3m: test diff read in full; targeted suites re-run
  by me (27/27, 5/5, 25/25, 23/23).
- 20:57 +07, T+4m: full suite started in background (log
  /tmp/c1-amend2-fullsuite.log); prune/monitor/caller audit.
- 20:58 +07, T+5m: baseline worktree at 8f600b9, new tests fail as
  expected (8 / 1+1 / 1); nohup exec verified on VM.
- 20:59 +07, T+6m: laptop state verified read-only via ssh-laptop.sh
  (HEAD, sha256, daemon 160727, holders, no leftover sleeps).
- 21:00-21:03 +07, T+7m to T+10m: full suite finished; extra failure
  investigated and proven to be cross-lane interference (see 2.5);
  test_phase3_cleanup re-run passes in isolation (Ran 5, OK).
- 21:04 +07, T+11m: R11 verified directly by me (rc=0); em dash 0;
  review written, committing.

## 2. What I verified, with evidence

### 2.1 Diff scope is exactly the amend, nothing else

- git show --stat 14cf4dc: 6 files, 305 insertions, 26 deletions.
  Only scripts/overlay.py, scripts/s2_flip_live.py,
  scripts/hypr_cmd.py, tests/test_overlay.py,
  tests/test_s2_flip_pill.py, tests/test_hypr_cmd.py. No other file.
- 448fee6 is the log only; 4a4fae3 only replaces "(ghi sau khi chay)"
  with the two commit hashes. Both trivial and correct.
- 0 em dash (U+2014) and 0 en dash (U+2013) in the whole amend
  diff, counted by me.
- The dirty tests/realistic/clone1-batch3/results.json and the
  untracked prompt files from other workers are not in these
  commits. My own baseline worktree /tmp/amend2-baseline was
  removed after use.

### 2.2 Targeted suites, re-run by me

- python3 -m unittest discover -s tests -p 'test_overlay.py':
  Ran 27 tests in 0.019s, OK (22 old + 5 new).
- test_s2_flip_pill.py: Ran 5 tests in 0.002s, OK (3 old + 2 new).
- test_hypr_cmd.py: Ran 25 tests in 0.036s, OK (24 old + 1 new).
- test_chromium_cli.py: Ran 23 tests in 1.442s, OK (hold() change
  did not break the CLI). All four match the log's numbers exactly.

### 2.3 New tests genuinely catch the old behavior (baseline 8f600b9)

- Worktree at 8f600b9 (pre-amend-1 code) + the 3 new test files
  copied in, run by me, worktree removed after:
  - test_overlay: Ran 27, FAILED (failures=8) = 5 new + 3 amend-1
    tests, exactly as the log claims.
  - test_s2_flip_pill: FAILED (failures=1, errors=1): the sleeper
    test fails ('nohup sleep 600' not found in the old acquire
    command) and test_send_browser errors because the old
    pill_release_cmd() takes no pid argument, proving the old code
    lacked the pid parameter.
  - test_hypr_cmd: Ran 25, FAILED (failures=1) = the R4 test only.
- So the 8 new tests are real guards, not vacuous.

### 2.4 Full suite, re-run by me, and the one extra failure explained

- My run: Ran 2366 tests in 379.549s, FAILED (failures=2,
  errors=2, skipped=17). The worker's run: Ran 2360 in 214.538s,
  FAILED (failures=1, errors=2, skipped=17). The +6 test count is
  other lanes adding tests in the shared checkout; my run was
  slower because several lanes ran full suites concurrently.
- The 3 shared problems are the same old environment errors in
  both runs, none touching overlay/s2_flip/hypr_cmd:
  - ERROR setUpClass test_cursor_file (g++: -std=c++26 unrecognized).
  - ERROR test_typed_text_check_passes (tesseract unavailable).
  - FAIL test_typed_text_check_fails (tesseract unavailable).
- The one extra failure in MY run only, test_cli_exit_codes
  (test_phase3_cleanup.py line 81), is NOT a regression. I proved
  it is cross-lane interference:
  - find_leftovers reads the LIVE /proc cmdlines and flags any
    process whose cmdline contains both 'cursor_session' and
    'guard', regardless of the fake state dir the test passes.
  - The flagged guardian was
    `/usr/bin/python3 /tmp/tmp1sebz7ha/runtime/scripts/cursor_session.py
    guard 3 ...`, a test fixture in a tmp dir, not the real
    scripts dir. The pid changed on every run I observed
    (109383, then 122342, then 123173), and the process and its
    tmp dir were gone seconds later.
  - /tmp/c3-amend2-fullsuite.log and c3-amend2-fullsuite2.log
    were modified 14:02-14:03 UTC, exactly during my run: another
    lane was running full suites concurrently and its tests spawn
    transient cursor_session guards.
  - Re-running test_phase3_cleanup.py alone right after, with no
    other lane's suite running, passes: Ran 5 tests, OK.
  - Amend 2 touches no file involved (cursor_session.py,
    session_cleanup.py untouched by 14cf4dc).
- Conclusion: 0 new regressions from this amend.

### 2.5 H1 caller semantics: every live caller is pid-keyed now

- overlay.hold(agent, method, pid=None): default pid =
  os.getpid() of the calling process. The calling process lives
  for the whole `with` block by definition, so the pid is alive
  for the hold and prune can heal the holder if the caller dies
  mid-block. Both the acquire and the release subprocess pass the
  same --pid, so release drops exactly the key acquire added.
  The new test test_hold_passes_calling_pid captures the argv and
  asserts both --pid values equal str(os.getpid()).
- Only caller of hold() is chromium_cli._pill_hold
  (scripts/chromium_cli.py line 654, `with overlay.hold("Muse",
  "CDP")`), running on the laptop, so the pid is a real laptop
  pid, distinct per concurrent command.
- first_action.acquire_overlay / release_overlay already used
  os.getpid() directly (lines 129, 176) and remove exactly that
  pid on failure; unchanged, and consistent with the new rule.
- cdp.mjs acquire (line 65) and release (line 79) both pass
  --pid String(process.pid), the node process pid on the laptop.
- Grep for every CLI acquire in scripts/: only overlay.py hold(),
  s2_flip_live.py (sleeper pid), and cdp.mjs (process.pid). No
  pid-less live caller remains. The bare key can now only come
  from legacy or manual pid-less callers, exactly as the narrowed
  docstring says.
- Docstring H3 fixed correctly: "No call ever removes another
  run's PID-KEYED entry" plus the explicit bare-key exception and
  the requirement that every live caller pass a real pid. The old
  absolute claim is gone.

### 2.6 The sleeper pid decision is correct (the key judgment)

- The brief said "pass a real --pid for s2_flip". The worker
  correctly refused the obvious reading (the VM harness pid):
  the holder lives on the laptop, and the daemon prunes any
  holder whose pid does not exist there.
- Prune mechanism verified in code, not trusted from the log:
  prune_dead_holders (line 155) drops a holder when
  os.kill(pid, 0) raises ProcessLookupError or PermissionError;
  apply_holders (line 309) calls it first; the daemon monitor
  (line 359) runs apply_holders every 2.0s. So a VM pid would be
  pruned within one monitor tick (~2s), the pill dropping
  mid-send. Passing the VM pid would have been a regression,
  not a fix.
- The worker's pre-decision experiment is consistent with the
  code: a holder with pid 999999 was pruned immediately, and
  laptop lacks VM pids 93722, 999999, 12345.
- The replacement, a detached `sleep 600` on the laptop, is
  sound: nohup execs sleep directly, so $! is the sleep pid
  itself. I verified this on the VM (ps shows comm=sleep for
  $!), and the worker's laptop smoke test proved it on the
  laptop (PILL_SLEEP_PID=160976, holder
  'AMEND2-SLEEPER:160976', kill 160976 removed the sleeper,
  no leftover sleep).
- The acquire command preserves its rc: ACQ_RC=$? is captured
  before the echo, the sleeper is killed inline on failure, and
  exit $ACQ_RC returns the acquire result. The echo cannot mask
  a failure.
- The 600s lifetime covers one send step with ~20x margin
  (median send ~28.6s). If the harness dies, the sleeper
  expires and prune heals the holder. If the acquire output
  carries no PILL_SLEEP_PID, the release falls back to pid-less
  and the holder heals via prune at expiry; the note records
  that. Both paths are documented in the cdp_pill_hold
  docstring, which no longer claims the holder is pid-less.
- One bound worth recording (G2, not a condition): a send step
  longer than 600s would let the sleeper expire mid-send and
  prune drop the holder. No send in this campaign is near that
  (median 28.6s), so 600s is a reasonable choice.

### 2.7 R11 verified directly by me

- Release parser now accepts --method (default None, ignored
  for removal because the holder key is (agent, pid)).
- I ran it myself on the VM: `release --agent R11-PROBE
  --method CDP --pid 1` returns rc=0 with an empty holders
  JSON. The old code at 8f600b9 has no --method in the release
  parser, and Council 1 (amend 1) verified it returned rc=2
  "unrecognized arguments" before. This closes the bug that
  made every s2_flip release fail and left the S2-flip holder
  stale since 20:34:45.
- The fix also covers cdp.mjs releaseCdpPill (line 79), which
  passes --method. cdp.mjs itself was correctly left untouched.

### 2.8 E1 and E2 tests are real

- E1 test_cmd_release_pid_none_keeps_pid_keyed_holder: pid-less
  release keeps the pid-keyed holder and the output still lists
  it, so the operator sees the pill stays up; the follow-up
  release with that --pid removes it. Help text added for both
  acquire (--pid is the holder key) and release (pid-less only
  removes the bare entry, a pid-keyed holder needs its own
  --pid).
- E2 test_cmd_acquire_daemon_failure_keeps_concurrent_holder:
  the D1 exception path (daemon ensure failure) keeps a
  concurrent pid-keyed holder, mirroring the invisible-path
  test. Both failure paths call the same remove_holder, but the
  D1 path was unproven end to end until now.
- Both tests fail on the old code (section 2.3) and pass on the
  new code (section 2.2).

### 2.9 C2 and R4 are correct and minimal

- C2: wayland_env uses setdefault for WAYLAND_DISPLAY, so a
  caller-provided display is never clobbered; the discovered
  display is only the fallback. Test
  test_wayland_env_keeps_caller_display proves it (wayland-9
  kept, signature still discovered).
- R4: hypr_cmd.desktop_env filters the signature dir listing
  to directories (is_dir), so a stray file sorting first can
  never be picked as the instance signature. Test
  test_from_dir_listing_skips_files proves it (aaa_file ignored,
  zzz_sig picked).

### 2.10 H2: laptop sync + daemon restart verified read-only by me

- Laptop HEAD is 14cf4dc (the amend commit itself), branch
  todolist-push. sha256 of scripts/overlay.py on the laptop is
  4cb46f9d1329034a1e0ad9c78e5b904ebd725835ec6de0f14ff2fae78d7059ae,
  matching the VM and the log's claim.
- Daemon PID 160727 alive, started Sun Nov 22 20:50:46 2026,
  running the new overlay.py daemon. Old daemon 115582 is gone.
- Status (read-only) shows holders contain ONLY S2-flip
  (acquired 2026-11-22T20:34:45+07:00, method CDP, pid null),
  label "S2-flip via CDP", owner daemon, visible true.
  S2-flip was preserved across the restart; no holder was
  added or lost.
- cdp.mjs on the laptop carries the pill gate again (12 PILL
  matches); the pre-sync laptop copy lacked it because the
  laptop lagged the VM since the gate landed. No leftover
  sleep 120/600 processes from the smoke tests.
- Backup of the 5 pre-sync files exists at
  /tmp/amend2-laptop-backup/ on the laptop; the new daemon log
  is /tmp/amend2-daemon.log.
- The restart was safe: SIGINT to 115582, finally cleanup ran
  (daemon.json unlinked, holders.json untouched), new daemon
  started with the same GUI env. The pill was off only for the
  seconds between kill and start.

### 2.11 Every amend-1 review condition is closed

- Council 1 e2ed4e8: (1) hold() and s2_flip pass a real --pid:
  closed (2.5, 2.6). (2) fix pill_release_cmd dropping --method
  + fix the docstring: closed (2.7; the parser fix covers both
  callers, and both docstrings are corrected). (3) sync new
  overlay.py to the laptop, restart daemon 115582, verify:
  closed (2.10).
- Council 2 1f28b3f: E1 and E2: closed (2.8).
- Council 3 f294661: conditions 1+2 as above, plus C2+R4 in the
  same lane: closed (2.9).
- Redteam 5d5111f: H1 bare-bare (C1): closed (2.5, 2.6). H2 not
  deployed (C2): closed (2.10). R11 (C3): closed (2.7). H3
  overstated docstring: closed (2.5).

## 3. Small notes (not blockers)

- G1 (open housekeeping, coordinator's call): the bare S2-flip
  holder (acquired 20:34:45, pid null) is still present. It is
  stale because every release of it failed rc=2 before R11 was
  fixed, and prune never touches a bare key. It does not block
  the next live run: a new pid-keyed acquire creates the
  distinct key S2-flip:<pid>, and its release removes only
  that key. But while the bare holder lives, holders never
  reach 0, so the daemon never idle-exits and the pill stays
  up after a run ends. Cleanup is one command on the laptop,
  `overlay.py release --agent S2-flip` (no --pid), when no send
  is running. The worker correctly did NOT do it (brief
  forbade releasing S2-flip); the coordinator decides when.
- G2: the 600s sleeper bound (see 2.6). If a send step ever
  exceeded 600s, prune would drop the holder mid-send. No send
  in this campaign is near that; the bound is acceptable and
  the heal path is by design.
- G3: pill_release_cmd appends `|| true` after the kill, so the
  release command always returns rc 0 and a failed release is
  not visible in the rc. No observable change: cdp_pill_hold
  ignores the release rc anyway (ssh returns a tuple, the
  finally block does not check it), and the old command had the
  same silent-ignore behavior. Harmless, but the `|| true`
  adds nothing; a later cleanup may drop it.
- G4: hold() uses check=True on the release subprocess inside
  the finally block, so a failed release can mask the block's
  own exception. Pre-existing behavior, unchanged by this
  amend.

## 4. Verdict: GO

The amend is correct and complete for its scope. The sleeper
pid decision is the right call and is the one judgment that
could have gone wrong (a VM pid would have been pruned in
~2s); the worker caught it with an experiment before
committing. Every live caller is now pid-keyed, R11 is fixed
and verified by me, E1/E2/C2/R4 are covered by real tests
that fail on the old code, and the laptop runs the fixed code
with the new daemon and the S2-flip holder preserved. The
full suite shows 0 new regressions; the one extra failure in
my run is proven cross-lane interference, not this amend.
No condition gates the next live run. The stale bare S2-flip
holder (G1) is housekeeping for the coordinator, not a
blocker.

## 5. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received ~20:53 +07, 22/11/2026. HEAD at review start
  4a4fae3.
- Diff scope 20:54 +07: git show --stat 14cf4dc, 6 files, 305
  insertions, 26 deletions. Em dash 0, en dash 0 in the diff.
- Targeted suites, re-run by me 20:56 +07: test_overlay Ran 27
  OK (0.019s); test_s2_flip_pill Ran 5 OK (0.002s);
  test_hypr_cmd Ran 25 OK (0.036s); test_chromium_cli Ran 23
  OK (1.442s).
- Baseline worktree at 8f600b9, run by me 20:58 +07:
  test_overlay Ran 27 FAILED failures=8; test_s2_flip_pill
  FAILED failures=1 errors=1; test_hypr_cmd Ran 25 FAILED
  failures=1. Worktree removed after.
- Full suite, run by me 20:57-21:03 +07, log
  /tmp/c1-amend2-fullsuite.log: Ran 2366 tests in 379.549s,
  FAILED (failures=2, errors=2, skipped=17). The 3 shared
  errors are g++ C++26 and tesseract x2, identical to the
  worker's run (Ran 2360, failures=1, errors=2, skipped=17).
- Extra failure proven environmental 21:01-21:03 +07:
  test_phase3_cleanup fails only while another lane's suite
  runs (guardian pids 109383, 122342, 123173 in tmp runtime
  dirs; c3-amend2-fullsuite logs 14:02-14:03 UTC); re-run
  alone passes (Ran 5, OK).
- nohup exec verified 20:58 +07: $! pid shows comm=sleep.
- Prune verified in code 20:57 +07: prune_dead_holders line
  155, apply_holders line 309, monitor every 2.0s line 359.
- Callers verified by grep 20:57 +07: hold() only called by
  chromium_cli.py line 654; first_action os.getpid() lines
  129, 176; cdp.mjs --pid process.pid lines 65, 79.
- Laptop verified read-only 20:59 +07 via ssh-laptop.sh: HEAD
  14cf4dc; overlay.py sha256
  4cb46f9d1329034a1e0ad9c78e5b904ebd725835ec6de0f14ff2fae78d7059ae;
  daemon 160727 started 20:50:46; status holders only S2-flip
  (20:34:45, pid null), visible true; no leftover sleep
  120/600; cdp.mjs pill gate present.
- R11 verified directly by me 21:04 +07: release --agent
  R11-PROBE --method CDP --pid 1 returns rc=0; old parser at
  8f600b9 has no --method argument.
- Files changed by me (review only): improvements/
  w-pillfix-amend2-council-1-review.md (new, this file).
  No amend file modified. No live proof run. No reviewer
  spawned. S2-flip holder not released.
