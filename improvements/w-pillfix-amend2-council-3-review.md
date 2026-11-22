# Council 3 review: W-PILLFIX-AMEND2 (pid-keyed holders, R11, E1/E2, C2+R4, H2)

Reviewer: Council 3, independent (not W-PILLFIX-AMEND2, not
W-PILLFIX-AMEND, not COORD-CLICK-9). Report goes to Muse tong, not
directly to the owner. No amend modified, no live proof run, no
holder released, no reviewer spawned. All verification below is my
own: targeted suites re-run, baseline worktrees built and removed,
caller audit by grep, laptop state read-only via ssh-laptop.sh.
No em dash or en dash anywhere in this file. No personal info.

## 0. Task and sources (20:53 +07, 22/11/2026)

- Task received ~20:53 +07. Branch todolist-push, repo
  ~/workspace/computer-use-wayland. The 3 amend2 commits:
  - 14cf4dc code + tests (6 files, 305 insertions, 26 deletions).
  - 448fee6 amend2 log.
  - 4a4fae3 hash record in log.
- Sources read before judging:
  - improvements/w-pillfix-amend2-log.md (288 lines, read in full).
  - Full diff of 14cf4dc (scripts/overlay.py, scripts/s2_flip_live.py,
    scripts/hypr_cmd.py, tests/test_overlay.py, tests/test_s2_flip_pill.py,
    tests/test_hypr_cmd.py).
  - The 4 amend-1 reviews (council-1 e2ed4e8, council-2 1f28b3f,
    council-3 f294661, redteam 5d5111f) for condition coverage.
  - Laptop state via ssh-laptop.sh (read-only commands only).

## 1. Time log (wall-clock Asia/Ho_Chi_Minh)

- 20:53 +07, T+0m: task received, amend2 log + diff read.
- 20:54 +07, T+1m: targeted suites re-run by me (overlay 27/27,
  s2_flip_pill 5/5, hypr_cmd 25/25).
- 20:54 +07, T+1m: baseline worktree at 8f600b9 (overlay 8 failures,
  hypr_cmd 1 failure, s2_flip_pill 1 failure + 1 error).
- 20:55 +07, T+2m: caller audit (cdp.mjs, first_action.py, hold,
  s2_flip, session_cleanup); laptop checks (HEAD, sha, daemon,
  holders, backup, results.json).
- 20:56-21:02 +07, T+3m to T+9m: full suite run 1 by me (Ran 2366,
  failures=4, errors=2, skipped=17).
- 21:02-21:06 +07, T+9m to T+13m: full suite rerun detached by me
  (Ran 2366, failures=1, errors=2, skipped=17).
- 21:06-21:08 +07, T+13m to T+15m: chromium_cli suite (23/23 OK),
  em/en dash counts (0/0), s2_flip baseline (already done),
  cdp.mjs gate grep on laptop.
- 21:08 +07, T+15m: review written, committing.

## 2. What I verified, with evidence

### 2.1 Diff scope is exactly the amend, nothing else

- git show --stat 14cf4dc: 6 files, 305 insertions, 26 deletions.
  Only scripts/overlay.py, scripts/s2_flip_live.py,
  scripts/hypr_cmd.py and the 3 test files. No shared library
  beyond these, no cdp.mjs change (deliberate, fail-closed gate),
  no results.json touch.
- 0 em dash (U+2014) and 0 en dash (U+2013) in the 14cf4dc diff
  across all 6 files, counted by me (grep -c, both 0).

### 2.2 Targeted suites, re-run by me

- python3 -m unittest discover -s tests -p 'test_overlay.py':
  Ran 27 tests, OK (22 old + 5 new).
- python3 -m unittest discover -s tests -p 'test_s2_flip_pill.py':
  Ran 5 tests, OK (3 old + 2 new).
- python3 -m unittest discover -s tests -p 'test_hypr_cmd.py':
  Ran 25 tests, OK (24 old + 1 new).
- python3 -m unittest discover -s tests -p 'test_chromium_cli.py':
  Ran 23 tests, OK (hold() change breaks no CLI caller).

### 2.3 New tests really catch the old behavior (baseline worktrees)

- Worktree at 8f600b9 (pre-amend-1 code) + new test files copied in:
  - test_overlay: Ran 27, FAILED (failures=8) = 5 new amend2 tests
    + 3 amend-1 tests, exactly as the worker claimed.
  - test_hypr_cmd: Ran 25, FAILED (failures=1) = the R4 test only.
  - test_s2_flip_pill: Ran 5, FAILED (failures=1, errors=1) =
    sleeper test FAIL (old code has no sleeper) + send_browser
    ERROR (old pill_release_cmd() takes no pid argument).
- Worktrees removed after. The new tests are real regression tests,
  not vacuous assertions.

### 2.4 H1 bare-bare is closed, and the sleeper design is the right answer

- The worker's key decision is correct and was proven by experiment
  before being made: a VM pid does not exist on the laptop, and the
  daemon prunes a holder whose pid is dead within ~2s, so passing
  the harness pid would have been a regression (pill dropping
  mid-send). The laptop sleeper (nohup sleep 600, pid keys the
  holder) is the correct construct.
- Verified in code: nohup sleep execs directly, so $! is the sleep
  pid itself; stdin/stdout/stderr redirected, survives SSH end;
  600s covers one send step; acquire failure kills the sleeper
  inline; ACQ_RC is captured before the echo and returned via
  `exit $ACQ_RC`, so the echo cannot mask a failure; the release
  passes the same pid (parsed from PILL_SLEEP_PID=) and kills the
  sleeper; if the pid cannot be parsed, the release falls back to
  pid-less and the note records it, with prune healing the holder
  at sleeper expiry. All of this is covered by the 2 new s2_flip
  tests, which I re-ran (section 2.2).
- overlay.hold() now defaults pid to os.getpid() of the calling
  process, and test_hold_passes_calling_pid captures the argv and
  proves acquire and release carry the same --pid. The calling
  process lives for the whole `with` block by definition, so the
  pid is alive for the hold and prune heals it if the caller dies.

### 2.5 Every live caller is now pid-keyed (caller audit, grep by me)

- scripts/cdp.mjs:65 acquire passes `--pid String(process.pid)`;
  :79 release passes `--pid String(process.pid)` plus --method.
- scripts/first_action.py: pid = os.getpid(); add_holder with that
  pid; acquire socket request carries 'pid': pid; failure path calls
  remove_holder(agent, pid); release_overlay sends pid in the
  release request.
- scripts/overlay.py hold(): pid-keyed by default (section 2.4).
- scripts/s2_flip_live.py: sleeper pid (section 2.4).
- session_cleanup: prune_dead_holders only, no acquire/release.
- No live caller still acquires or releases pid-less, except the
  deliberate fallback in cdp_pill_hold when PILL_SLEEP_PID cannot
  be parsed (documented, tested, heals via prune, see G3).

### 2.6 R11 is closed, and the release parser change is safe

- scripts/overlay.py release subparser now accepts --method
  (default None). The holder key is (agent, pid), the method is
  not part of it, so the value is accepted and ignored for removal.
  This fixes both callers that pass --method: s2_flip
  pill_release_cmd and cdp.mjs releaseCdpPill (line 79).
- The worker verified on the VM after the fix that
  `release --agent X --method CDP --pid 1` returns rc=0 (before
  the fix rc=2 "unrecognized arguments"). I verified the parser
  change in the diff; the rc=0 evidence itself is worker-reported.
- Help text for --pid on both acquire and release states the key
  rule (acquire: key is agent:pid; release: pid-less only removes
  the bare entry, a pid-keyed holder needs its own --pid). This
  closes Council 2 E1's help-text half.

### 2.7 Council 2 E1 + E2 are closed by real tests

- E1: test_cmd_release_pid_none_keeps_pid_keyed_holder proves a
  pid-less release keeps the pid-keyed holder, the release output
  still lists it, and a follow-up release with that --pid removes
  it. Re-run by me in the targeted suite (section 2.2) and proven
  to fail on old code (section 2.3).
- E2: test_cmd_acquire_daemon_failure_keeps_concurrent_holder
  proves the D1 exception path (daemon ensure failure) keeps a
  concurrent pid-keyed holder, mirroring the invisible-path test.
  Same verification as E1.

### 2.8 C2 + R4 are closed by real tests

- C2: wayland_env discovery branch uses setdefault for
  WAYLAND_DISPLAY (never clobbers a caller-provided display).
  Test test_wayland_env_keeps_caller_display proves a caller
  display of wayland-9 survives discovery. Re-run by me.
- R4: hypr_cmd.desktop_env only picks directories as signatures
  (is_dir). Test test_from_dir_listing_skips_files proves a stray
  file sorting first is never picked. Re-run by me, and proven to
  fail on old code (section 2.3).

### 2.9 H2: laptop fast-forward was safe, daemon restart was correct

Pre-sync state (worker log, confirmed by my own checks after):
- Laptop HEAD was 331523f, dirty on 5 files, all of them
  W-PILLFIX/F4 code already landed on the VM. The worker's
  `git diff origin/todolist-push` showed only 4 `+` lines across
  the 5 files, i.e. the old remove_holder (wipe-all) code, not
  unlanded local work. No incoming commit touched results.json
  (git log 331523f..origin/todolist-push -- results.json empty).
- Backup first: /tmp/amend2-laptop-backup/ holds all 5 files.
  I verified the directory exists on the laptop with exactly
  those 5 files (cdp.mjs, indicator.py, overlay.py,
  test_indicator.py, test_overlay.py).
- Sync: checkout origin/todolist-push -- 5 files, then merge
  --ff-only origin/todolist-push. HEAD is now 14cf4dc (verified
  by me: git log -1 on the laptop).
- results.json untouched: 4113 bytes, modified 17:50 (verified
  by me on the laptop). git status shows only untracked
  improvements/* files belonging to other workers; no modified
  file remains.
- File verification: sha256sum scripts/overlay.py on the laptop
  is 4cb46f9d1329034a1e0ad9c78e5b904ebd725835ec6de0f14ff2fae78d7059ae,
  identical to the VM copy (verified by me). "PID-KEYED" grep
  count is 1 (the new docstring).
- cdp.mjs pill gate restored: I grepped the laptop file and found
  the full gate present (header comment citing W-PILLCDP rule
  18:30, pillEnabled, pillIdentity, pillHook, acquire with
  --pid process.pid at line 65, release with --pid plus --method
  at line 79, fail-closed 'CDP pill unavailable', gate call site
  at line 560). The worker's claim that the laptop had lost the
  gate before this sync is credible: the laptop had not synced
  since the gate landed (d0602dd).
- Daemon restart: old daemon 115582 (started 19:40:45) killed
  with SIGINT, so KeyboardInterrupt ran the finally block (hide
  pill, close native, unlink socket/daemon.json). New daemon
  160727 started 20:50:47 detached with GUI env. My own check
  at ~20:55 confirmed daemon 160727 alive (elapsed 03:26) and
  holders still only S2-flip (bare, 20:34:45), visible true.
  Pill blackout was only the seconds between kill and start.
- Smoke tests on the new daemon (worker-reported, 20:51:01 and
  20:51:13): sleeper pid acquire/release pid-keyed plus --method
  rc=0, holders back to only S2-flip; sleeper construct test with
  agent AMEND2-SLEEPER, release plus kill, no leftover sleeps,
  daemon 160727 still alive. I did not re-run the smoke commands
  myself; I verified the post-state independently (daemon alive
  on new code, holders intact, no sleeper processes running).
  See G2.

### 2.10 Amend-1 conditions: all closed, nothing left open

- Council 1 e2ed4e8: (1) hold() + s2_flip pass a real pid
  (sections 2.4, 2.5); (2) fix pill_release_cmd dropping --method
  plus docstrings (section 2.6, remove_holder docstring narrowed,
  cdp_pill_hold docstring rewritten); (3) sync overlay.py to the
  laptop, restart daemon 115582, verify (section 2.9).
- Council 2 1f28b3f: E1 test + help text (sections 2.6, 2.7);
  E2 D1 end-to-end test (section 2.7). E3 was trivial, no action.
  E4 (hold() sharing the bare key) is now closed by the hold()
  change in section 2.4.
- Council 3 f294661: conditions 1+2 as above; C2 setdefault
  (section 2.8); R4 is_dir (section 2.8).
- Redteam 5d5111f: C1 H1 bare-bare (sections 2.4, 2.5) plus H3
  docstring narrowed (section 2.6); C2 H2 deploy (section 2.9);
  C3 R11 recommended fix (section 2.6).
- Deferred items from amend-1 stay deferred, not reopened: R1,
  R2/R3, R7 (warn log for CU_CDP_PILL=0), R8/R9, R10. None of
  them is a condition of this amend.

### 2.11 Full suite, re-run by me twice

- Run 1 (~21:00 +07): Ran 2366 tests in 373.003s, FAILED
  (failures=4, errors=2, skipped=17).
- Rerun, detached (~21:06 +07): Ran 2366 tests in 220.823s,
  FAILED (failures=1, errors=2, skipped=17), exactly the
  worker's numbers and the known baseline. The 3 failing items
  are the same 3 environment errors as every prior run, none
  touching overlay/s2_flip/hypr_cmd:
  - ERROR setUpClass test_cursor_file.CursorFileTests (g++ C++26).
  - ERROR test_typed_text_check_passes_when_fragment_is_visible
    (test_tc02_controller, tesseract).
  - FAIL test_typed_text_check_fails_when_fragment_is_absent
    (test_tc02_controller, tesseract).
- The 3 extra failures in run 1 did not reproduce on the rerun
  on identical HEAD. Their names were not captured (I piped run
  1 through tail -8, my error, recorded honestly in G1). The
  run-1 log tail showed session_remote start failures
  (cancelled/busy/nested_session/recovery_required), the known
  flaky family in this suite. Conclusion: 0 new regressions;
  the rerun matching the baseline exactly is the operative
  evidence.

## 3. The stale S2-flip bare holder: assessment (my brief asked)

State verified by me at ~20:55 +07 via overlay.py status on the
laptop: holders contain only S2-flip, bare key, acquired
2026-11-22T20:34:45+07:00, method CDP, pid null, visible true.
No send is running right now: no s2_flip process, no node cdp
process, no sleep process (checked by me with ps).

- It does NOT block the next live run. A new s2_flip send
  acquires S2-flip:<sleeper pid> and releases exactly that key;
  the bare holder is untouched by design (E1). The run's own
  pill lifecycle is correct with the bare holder present.
- It SHOULD still be cleaned before the next live run, because
  leaving it has two real costs: the pill stays up forever
  between runs (the "pill only while a run holds it" invariant
  is permanently violated by this one key), and the daemon never
  self-exits (holders never reach 0), so every future overlay.py
  update on the laptop will need another manual daemon restart
  instead of the daemon self-cycling.
- Cleaning is one manual command on the laptop:
  `overlay.py release --agent S2-flip` (no --pid), only after
  re-verifying no send is running immediately before it. After
  it, holders go to 0, the daemon exits, the pill drops, and the
  next send re-acquires normally with a pid-keyed holder.
- I did NOT release it (my brief forbids it). This is a
  coordinator action, listed as condition C1 below. It is a
  pre-live cleanup, not a code gate: the amend itself is
  accepted whether or not the holder has been cleaned yet.

## 4. Gaps and minor observations (not blockers)

- G1 (my own limitation, not the worker's): the 3 extra failures
  in full-suite run 1 are unattributed because I piped the run
  through tail -8 and did not save the output. The rerun on
  identical HEAD is clean apart from the 3 known environment
  errors, so this does not change the verdict, but a future
  reviewer should always save full-suite output to a log file.
- G2: the H2 smoke-test evidence (commands, outputs, times) is
  worker-reported; I verified the post-state independently
  (daemon 160727 alive on the new code, holders intact, no
  leftover sleepers), not the smoke commands themselves.
- G3: when PILL_SLEEP_PID cannot be parsed from the acquire
  output, the release falls back to pid-less and cannot remove
  the pid-keyed holder; it heals via prune when the sleeper
  expires (at most 600s). Documented and tested. Acceptable,
  but the pill can stay up to 10 minutes after such a run.
- G4: while the stale bare holder remains, `overlay.py status`
  keeps reporting S2-flip visible between runs, which could
  mislead a future operator into thinking a send is live.
  Cleaning it (C1) removes this too.
- G5: the laptop repo lags the VM by the W-ZENPROOF2-AMEND3
  commits (HEAD 14cf4dc on the laptop, 4a4fae3 plus amend3
  commits on the VM). That lag does not touch the pill files,
  so it is not a defect of this amend, but any lane managing
  the laptop repo should know the sync gap exists.

## 5. Verdict: GO WITH CONDITIONS

The amend closes every condition from all 4 amend-1 reviews,
with real tests that fail on old code, a safe laptop sync with
backup and an intact results.json, a correct daemon restart,
and a full suite at the known baseline. The one remaining
physical item is the stale bare holder, which is a cleanup
action, not a code defect.

Conditions, all before the next live run (not before landing
this amend):

- C1. Clean the stale S2-flip bare holder. Coordinator action,
  not mine: on the laptop, after re-verifying no send is
  running (no s2_flip, no node cdp, no sleeper process),
  run one manual `overlay.py release --agent S2-flip` with no
  --pid. Verify holders go to 0 and the pill drops. The next
  s2_flip send then re-acquires normally with a pid-keyed
  holder. Do not clean it while any send is running.

No other condition. Deferred items R1, R2/R3, R7, R8/R9, R10
stay deferred as recorded by Council 3 of amend-1.

## 6. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received ~20:53 +07, 22/11/2026. Amend2 commits:
  14cf4dc93aa18d6e03bdb8c29ec514289a464d3b (code + tests),
  448fee69925e94eb340de4e3179458e31cccedc4 (log),
  4a4fae3 (hash record).
- Targeted suites, re-run by me 20:54 +07: test_overlay Ran 27
  OK; test_s2_flip_pill Ran 5 OK; test_hypr_cmd Ran 25 OK.
  test_chromium_cli Ran 23 OK (21:06 +07).
- Baseline worktrees at 8f600b9, re-run by me 20:54 +07:
  test_overlay Ran 27 FAILED failures=8; test_hypr_cmd Ran 25
  FAILED failures=1; test_s2_flip_pill Ran 5 FAILED failures=1
  errors=1. Worktrees removed.
- Caller audit 20:55 +07: cdp.mjs:65 acquire --pid
  process.pid, :79 release --pid plus --method; first_action.py
  pid = os.getpid(), socket acquire/release carry pid;
  overlay.hold() defaults to os.getpid(); s2_flip sleeper pid.
- Laptop checks 20:55 +07 (ssh-laptop.sh, read-only): HEAD
  14cf4dc; overlay.py sha256
  4cb46f9d1329034a1e0ad9c78e5b904ebd725835ec6de0f14ff2fae78d7059ae
  (matches VM); "PID-KEYED" grep 1; backup
  /tmp/amend2-laptop-backup/ holds the 5 files; results.json
  4113 bytes, 17:50, intact; daemon 160727 alive, elapsed 03:26;
  holders only S2-flip bare 20:34:45, visible true; no s2_flip,
  node cdp, or sleeper process running.
- cdp.mjs gate on laptop, grepped by me 21:08 +07: header
  comment (W-PILLCDP rule 18:30), pillEnabled, pillIdentity,
  pillHook, acquire --pid at line 65, release --pid plus --method
  at line 79, fail-closed 'CDP pill unavailable', gate call
  site at line 560.
- Full suite run 1 by me ~21:00 +07: Ran 2366 in 373.003s,
  FAILED (failures=4, errors=2, skipped=17); extra 3 failure
  names not captured (tail -8, my error, see G1).
- Full suite rerun by me ~21:06 +07 (detached, log
  /tmp/c3-amend2-fullsuite2.log): Ran 2366 in 220.823s, FAILED
  (failures=1, errors=2, skipped=17); the 3 failing items are
  the known environment errors (g++ C++26, tesseract x2).
- Em dash 0, en dash 0 in the 14cf4dc diff across all 6 files,
  counted by me.
- Files changed by me (review only):
  improvements/w-pillfix-amend2-council-3-review.md (new, this
  file). No amend file modified. No live proof run. No holder
  released. No reviewer spawned.
