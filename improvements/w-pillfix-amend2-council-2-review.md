# Council 2 review: W-PILLFIX-AMEND2 (H1/R11/E1/E2/H2/C2/R4)

Reviewer: Council 2, independent (not W-PILLFIX-AMEND2, not
W-PILLFIX-AMEND, not COORD-CLICK-9). This is the same Council 2
that set conditions E1 and E2 on amend 1 (commit 1f28b3f); this
review checks whether amend 2 closes them, plus test completeness
of the whole amend. Report goes to Muse tong, not directly to
the owner. No fix modified, no live proof run, no reviewer
spawned, S2-flip holder NOT released (brief forbids it). No em
dash or en dash anywhere in this file. No personal info.

## 0. Task and sources (20:53 +07, 22/11/2026)

- Task received ~20:53 +07. Branch todolist-push, repo
  ~/workspace/computer-use-wayland, HEAD 4a4fae3 at review start.
- Amend under review, 3 commits:
  - 14cf4dc code + tests: pid-keyed pill holders (H1 bare-bare),
    release --method (R11), E1/E2 tests, C2+R4.
  - 448fee6 amend log.
  - 4a4fae3 log hash record.
- Sources read before judging:
  - improvements/w-pillfix-amend2-log.md (the amend log, 304
    lines, read in full).
  - Full diff of 14cf4dc (6 files, read line by line, not
    skimmed): scripts/overlay.py, scripts/s2_flip_live.py,
    scripts/hypr_cmd.py, tests/test_overlay.py,
    tests/test_s2_flip_pill.py, tests/test_hypr_cmd.py.
  - scripts/overlay.py cmd_acquire lines 523-565 and cmd_release
    lines 568-582 (the branches E1/E2 must cover).
  - My own amend-1 review (commit 1f28b3f) for the exact E1/E2
    wording.

## 1. Time log (wall-clock Asia/Ho_Chi_Minh)

- 20:53 +07, T+0m: task received, amend log read in full.
- 20:54 +07, T+1m: full diff of 14cf4dc read; targeted suites
  re-run by me (see section 2.1).
- 20:55 +07, T+2m: baseline worktree at 8f600b9 created, new
  test files copied in, 3 suites run, failing test names
  recorded, worktree removed.
- 20:55 +07, T+2m: full suite started in background
  (log /tmp/c2-amend2-fullsuite.log).
- 20:56 +07, T+3m: --help output for acquire/release checked;
  em/en dash grep over all 6 changed files (0 in each).
- 20:57 +07, T+4m: read-only laptop check via ssh-laptop.sh
  (sha256 of overlay.py, live status); cmd_acquire/cmd_release
  branches re-read for E1/E2 coverage.
- 21:00 +07, T+7m: full suite summary in log (Ran 2366,
  failures=1, errors=2, skipped=17); leftover discover process
  killed after its summary printed, log verified intact.
- 21:02 +07, T+9m: review written, committing.

## 2. What I verified, with evidence

### 2.1 Targeted suites, re-run by me

Commands (all in ~/workspace/computer-use-wayland):

- python3 -m unittest discover -s tests -p 'test_overlay.py':
  Ran 27 tests in 0.023s, OK.
- python3 -m unittest discover -s tests -p 'test_s2_flip_pill.py':
  Ran 5 tests in 0.002s, OK.
- python3 -m unittest discover -s tests -p 'test_hypr_cmd.py':
  Ran 25 tests in 0.003s, OK.
- python3 -m unittest discover -s tests -p 'test_chromium_cli.py':
  Ran 23 tests in 1.548s, OK.

All four match the amend log exactly (27/27, 5/5, 25/25, 23/23).

### 2.2 The 5 new overlay tests genuinely catch the old code

Baseline worktree /tmp/amend2-c2-baseline at 8f600b9 (old code),
new test files copied in, worktree removed after. Results:

- test_overlay: Ran 27, FAILED (failures=8). The 8 failures are
  exactly the 5 new tests plus the 3 amend-1 tests:
  - test_cmd_acquire_daemon_failure_keeps_concurrent_holder (E2)
  - test_cmd_acquire_invisible_pid_keyed_keeps_bare_holder (H1)
  - test_cmd_release_pid_none_keeps_pid_keyed_holder (E1)
  - test_hold_passes_calling_pid (H1)
  - test_wayland_env_keeps_caller_display (C2)
  - test_cmd_acquire_invisible_keeps_concurrent_holder (amend 1)
  - test_remove_holder_pid_keeps_bare_holder (amend 1)
  - test_remove_holder_pid_none_keeps_pid_keyed_holder (amend 1)
- test_s2_flip_pill: Ran 5, FAILED (failures=1, errors=1).
  FAIL test_acquire_keys_holder_by_laptop_sleeper_pid (old code
  has no sleeper); ERROR test_send_browser_holds_pill_around_send
  (old pill_release_cmd() takes no pid argument, new test calls
  pill_release_cmd(4242), TypeError).
- test_hypr_cmd: Ran 25, FAILED (failures=1).
  FAIL test_from_dir_listing_skips_files (R4).

Every new test fails on old code and passes on new code. The
worker's baseline claim is confirmed name by name, not just by
count.

### 2.3 E1: closed, correct branch

My amend-1 condition E1 asked for a test that cmd_release with
pid None keeps a pid-keyed holder, plus --pid help text. Amend 2
delivers both:

- test_cmd_release_pid_none_keeps_pid_keyed_holder: adds holder
  Muse:999001, releases pid-less, asserts the holder survives
  AND the printed output still lists it (operator can see the
  pill stays up), then releases with --pid 999001 and asserts
  holders == {}. This targets cmd_release (overlay.py 568-582):
  in the test the isolated tmp dir has no daemon, so it runs the
  no-daemon branch (line 570), which calls remove_holder(agent,
  None). The socket branch (line 574-579) and the daemon release
  handler call the same remove_holder with the same args, and
  remove_holder semantics are unit-tested, so the branch
  coverage is adequate (see note G3).
- Help text verified live by me, not just read in the diff:
  `overlay.py acquire --help` shows "--pid PID: pid of the
  calling process; the holder key is agent:pid, so concurrent
  runs of one agent never share a key"; `overlay.py release
  --help` shows "--pid PID: pid of the holder to drop; a
  pid-less release only removes the bare agent entry, a
  pid-keyed holder needs its own --pid". Both say exactly what
  E1 asked for.

### 2.4 E2: closed, correct branch

My amend-1 condition E2 asked for an end-to-end test of the D1
exception path keeping a concurrent pid-keyed holder. Amend 2
delivers it:

- test_cmd_acquire_daemon_failure_keeps_concurrent_holder: adds
  holder Muse:999001, replaces _ensure_daemon with a function
  raising RuntimeError, calls cmd_acquire with pid None, asserts
  it raises, asserts load_holders() == {'Muse:999001'}.
- This targets the D1 except path (overlay.py 531-544):
  add_holder runs first (line 524, adds the bare key),
  _ensure_daemon raises, the handler calls
  remove_holder(args.agent, args.pid) with pid None, which
  removes only the just-added bare key and keeps the pid-keyed
  holder. The test mirrors test 3 (invisible path) as E2 asked,
  and the two paths share the same remove_holder call, but the
  D1 path is now proven end to end, not just by analogy.

### 2.5 H1: both live callers pass a real pid, tested

- hold() (overlay.py): pid defaults to os.getpid() of the
  calling process; acquire and release both pass --pid. Test
  test_hold_passes_calling_pid captures subprocess argv (no real
  holder touched), asserts exactly 2 calls, both carry --pid,
  both pids equal str(os.getpid()), release pid == acquire pid.
- s2_flip pill_acquire_cmd: starts `nohup sleep 600` on the
  laptop, acquires with --pid $SLEEP_PID, echoes
  PILL_SLEEP_PID=. Test
  test_acquire_keys_holder_by_laptop_sleeper_pid (FakeHarness
  returns PILL_SLEEP_PID=4242) asserts the acquire command
  contains 'nohup sleep 600', '--pid $SLEEP_PID',
  'PILL_SLEEP_PID=$SLEEP_PID', and the release command contains
  '--pid 4242' and 'kill 4242'.
- The VM-pid trap the worker found is real and correctly
  handled: a VM pid does not exist on the laptop, the daemon
  would prune the holder within one monitor tick (~2s). The
  worker verified this empirically before choosing the sleeper
  (log section 1) and documented the reason in the
  pill_acquire_cmd docstring so a later lane does not "fix" it
  back to a VM pid. The sleeper lives 600s, covers one send
  step, and prune heals the holder when it expires.
- Fallback path tested: when acquire succeeds but no
  PILL_SLEEP_PID parses, the release falls back pid-less and
  does not crash
  (test_release_falls_back_pid_less_without_parsed_pid); the
  note records that the pid-keyed holder survives until prune.
  That matches the E1 semantics by design.

### 2.6 R11, C2, R4: all closed and tested

- R11: release subparser accepts --method (overlay.py, with a
  comment that the method is not part of the holder key). Live
  --help output confirms `[--method METHOD]` on release. This
  fixes the rc=2 "unrecognized arguments" both s2_flip and
  cdp.mjs hit.
- C2: wayland_env uses setdefault for WAYLAND_DISPLAY, so a
  caller-provided display is never clobbered; the discovered
  display is only the fallback. Test
  test_wayland_env_keeps_caller_display sets WAYLAND_DISPLAY
  to wayland-9 and asserts it survives discovery.
- R4: desktop_env only picks directories as signatures
  (os.path.isdir filter). Test test_from_dir_listing_skips_files
  puts a file aaa_file sorting before a directory zzz_sig and
  asserts zzz_sig is picked.

### 2.7 H2 (deploy): corroborated read-only, S2-flip untouched

Read-only checks via ssh-laptop.sh (no holder released, no
daemon touched):

- Laptop scripts/overlay.py sha256 is
  4cb46f9d1329034a1e0ad9c78e5b904ebd725835ec6de0f14ff2fae78d7059ae,
  exactly the VM value recorded in the amend log. The fix is
  deployed on the laptop.
- Live `overlay.py status` answers and shows the S2-flip bare
  holder (acquired 2026-11-22T20:34:45+07:00) still present.
  That bare holder is stale (from before R11 was fixed; its
  release always failed rc=2), and it can only be dropped by a
  manual pid-less `overlay.py release --agent S2-flip` once no
  send is running. The amend log section 8 already flags this
  for Muse tong to decide; the new pid-keyed releases
  correctly leave it alone by design (E1). Not a condition on
  this amend.

### 2.8 Full suite, re-run by me

Command: python3 -m unittest discover -s tests, log
/tmp/c2-amend2-fullsuite.log. Result:

- Ran 2366 tests in 377.044s
- FAILED (failures=1, errors=2, skipped=17)

The 3 failures are exactly the known environment errors, same
names as the worker's run and the amend-1 baseline:

- ERROR setUpClass test_cursor_file.CursorFileTests (g++ C++26)
- ERROR test_tc02_controller
  test_typed_text_check_passes_when_fragment_is_visible
  (tesseract)
- FAIL test_tc02_controller
  test_typed_text_check_fails_when_fragment_is_absent
  (tesseract)

0 new regressions. Ran 2366 vs the worker's 2360 (+6) is other
lanes adding tests in the shared checkout; the invariant that
matters (failures=1, errors=2, skipped=17, same 3 names)
matches exactly. (My run took 377s vs the worker's 214s;
shared CPU, not a code difference. One discover process
lingered after its summary printed; I killed it after the log
showed the final summary, log verified intact.)

### 2.9 Scope and hygiene

- Diff of 14cf4dc: exactly 6 files, 305 insertions, 26
  deletions, matching the log. No other file touched. The
  dirty tests/realistic/clone1-batch3/results.json (another
  worker's) was not committed by the amend worker and was not
  touched by me.
- 0 em dashes and 0 en dashes in all 6 changed files (grep
  count 0 each), verified by me.

## 3. Gaps (test completeness)

Two gaps, both test-only, both cheap. Neither needs a code
change or a re-review.

- G1 (condition 1): two load-bearing shell fragments of the
  s2_flip acquire command are unasserted. The sleeper test
  asserts 'nohup sleep 600', '--pid $SLEEP_PID' and the
  PILL_SLEEP_PID echo, and the release side asserts 'kill
  4242', but nothing pins `[ $ACQ_RC -ne 0 ] && kill $SLEEP_PID`
  (kills the sleeper when the acquire fails) or `exit $ACQ_RC`
  (preserves the acquire rc so a failed acquire is not masked
  as success). If either fragment is dropped in a later edit,
  no test fails. The kill clause failing only leaks a stray
  `sleep 600` (harmless, self-expires); the `exit $ACQ_RC`
  failing is sharper, because held would read True with no
  holder. Condition: add string assertions for both fragments
  in the sleeper test (or a dedicated test).
- G2 (condition 2): the hold() acquire-failure path is
  untested. hold() runs acquire with check=True, so a failed
  acquire raises CalledProcessError before yielding and no
  release call runs. No test pins that behavior (raise, exactly
  1 subprocess call, no release). The raise is the designed
  behavior (cmd_acquire documents that overlay.hold raises),
  and a failed acquire holds nothing, so nothing leaks; it is
  still an unproven branch of the hold/release surface this
  review was asked to audit. Condition: add a test with the
  same argv-capture fake asserting hold() raises on acquire
  failure and issues no release call.

Notes, not conditions:

- G3: the E1 test exercises cmd_release's no-daemon branch
  (isolated tmp dir, no daemon). The socket branch and the
  daemon release handler call the same remove_holder with the
  same args, and remove_holder semantics are unit-tested.
  Coverage is adequate.
- G4: the wayland_env discovery-failure branch (except
  ImportError/ValueError) also uses setdefault, so a caller
  display survives there too. Untested, but symmetric with the
  tested success branch.
- G5: the stale S2-flip bare holder on the laptop (section
  2.7) is Muse tong's decision, not this amend's. Do not
  release it from a review follow-up.

## 4. Verdict: GO WITH CONDITIONS

E1 and E2 (my amend-1 conditions) are both closed on the
correct branches with tests that fail on old code and pass on
new code. H1, R11, C2, R4 are closed and tested. H2 is deployed
on the laptop (sha match) with the daemon answering and the
S2-flip holder preserved. The full suite shows 0 new
regressions (same 3 environment errors as baseline).

Conditions, both test-only follow-ups, no re-review needed:

- C1: pin the two load-bearing shell fragments in the s2_flip
  acquire command (`[ $ACQ_RC -ne 0 ] && kill $SLEEP_PID` and
  `exit $ACQ_RC`) with string assertions in the sleeper test.
- C2: add a hold() acquire-failure test (raises, exactly 1
  subprocess call, no release).

The amend is accepted. No fix modified, no live proof run, no
reviewer spawned, S2-flip holder not released.

## 5. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received ~20:53 +07, 22/11/2026. HEAD at review start
  4a4fae3.
- Targeted suites, re-run by me 20:54 +07: test_overlay Ran
  27 OK; test_s2_flip_pill Ran 5 OK; test_hypr_cmd Ran 25 OK;
  test_chromium_cli Ran 23 OK.
- Baseline worktree /tmp/amend2-c2-baseline at 8f600b9,
  20:55 +07: test_overlay Ran 27 FAILED (failures=8, names
  recorded in section 2.2); test_s2_flip_pill Ran 5 FAILED
  (failures=1, errors=1); test_hypr_cmd Ran 25 FAILED
  (failures=1). Worktree removed after.
- Full suite, re-run by me 20:55-21:00 +07, log
  /tmp/c2-amend2-fullsuite.log: Ran 2366 tests in 377.044s,
  FAILED (failures=1, errors=2, skipped=17), same 3
  environment errors as baseline.
- --help check 20:56 +07: acquire and release --pid help texts
  present and correct (section 2.3).
- Em/en dash grep 20:56 +07: 0 in all 6 changed files.
- Laptop read-only check 20:57 +07 (ssh-laptop.sh): laptop
  overlay.py sha256
  4cb46f9d1329034a1e0ad9c78e5b904ebd725835ec6de0f14ff2fae78d7059ae,
  matches VM; live status shows S2-flip bare holder
  (2026-11-22T20:34:45+07:00) present.
- Diff scope 20:54 +07: git show --stat 14cf4dc, 6 files, 305
  insertions, 26 deletions.
- Files changed by me (review only):
  improvements/w-pillfix-amend2-council-2-review.md (new, this
  file). No fix file modified. No live proof run. No reviewer
  spawned.
