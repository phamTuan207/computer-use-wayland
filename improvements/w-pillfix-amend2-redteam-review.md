# Redteam review: W-PILLFIX-AMEND2 (pid-keyed holders, release --method, laptop sync + daemon restart)

Reviewer: Redteam, independent (not W-PILLFIX-AMEND2, not
W-PILLFIX-AMEND, not COORD-CLICK-9). Report goes to Muse tong, not
directly to the owner. No amend modified, no live proof run, no
S2-flip holder released, no reviewer spawned. All verification is
code/unit level plus my own live read-only checks on the laptop
(holders.json, daemon.json, ps, one throwaway `sleep 120` that I
killed right after). No em dash or en dash anywhere in this file.
No personal info.

## 0. Task and sources

- Task received ~20:53 +07, 22/11/2026. Branch todolist-push, repo
  ~/workspace/computer-use-wayland. Amend 2 under review, 3 commits:
  - 14cf4dc code + tests: pid-keyed pill holders (H1 bare-bare),
    release --method (R11), E1/E2 tests, C2+R4. 6 files, 305
    insertions, 26 deletions.
  - 448fee6 amend2 log.
  - 4a4fae3 record amend2 commit hashes in log.
- Sources read before judging:
  - improvements/w-pillfix-amend2-log.md (full log, sections 0-9).
  - Full diff of 14cf4dc (overlay.py, s2_flip_live.py, hypr_cmd.py,
    3 test files), read line by line.
  - scripts/overlay.py: _holders_lock, load/save_holders,
    _holder_key, add/remove_holder, prune_dead_holders,
    apply_holders, _monitor, serve finally, _ensure_daemon,
    cmd_acquire (D1 + invisible paths), cmd_release, hold().
  - scripts/s2_flip_live.py: pill_acquire_cmd, pill_release_cmd,
    cdp_pill_hold, send_browser, _send_browser_inner,
    oneshot_code_exec, v12_check, activate_browser, count_check.
  - scripts/cdp.mjs: pill gate (acquireCdpPill before first input,
    releaseCdpPill in outer finally), PILL_ACQUIRE_TIMEOUT_MS,
    PILL_RELEASE_TIMEOUT_MS.
  - scripts/chromium_cli.py _pill_hold (overlay.hold caller).
  - /tmp/c5-activate.mjs on the laptop (grep pill/overlay, no match).

## 1. Time log (wall-clock Asia/Ho_Chi_Minh)

- ~20:53 +07, T+0m: task received, amend2 log + diff read.
- T+2m: targeted suites re-run by me (test_overlay 27/27,
  test_s2_flip_pill 5/5, test_hypr_cmd 25/25).
- T+2m: full suite started in background (discover test_*.py).
- T+3m: sleeper survival test live on the laptop (spawn 163627,
  separate SSH call shows it alive, kill it, confirm gone).
- T+4m to T+7m: laptop state verify (holders.json, daemon.json,
  daemon ps, overlay.py sha256, no sleep 600 left, one hypr entry),
  send-path timeout arithmetic, cdp.mjs gate read.
- 21:02 +07, T+9m: full suite finished (Ran 2366, 374.2s,
  failures=1, errors=2, skipped=17).
- T+10m: baseline worktree at 8f600b9 with new test files
  (test_overlay 8 failures, test_s2_flip_pill 1 failure + 1 error,
  test_hypr_cmd 1 failure), worktree removed, dash check 0.
- T+11m: test_chromium_cli re-run by me (23/23 OK).
- 21:04 +07, T+11m: review written, committing.

## 2. What I verified independently (attacks that failed)

### 2.1 Targeted suites and full suite, re-run by me

- test_overlay: Ran 27 tests in 0.026s, OK (22 old + 5 new).
- test_s2_flip_pill: Ran 5 tests in 0.001s, OK (3 old + 2 new).
- test_hypr_cmd: Ran 25 tests in 0.003s, OK (24 old + 1 new).
- test_chromium_cli: Ran 23 tests in 1.409s, OK (hold() default
  pid change breaks nothing in the CLI).
- Full suite, re-run by me in background: Ran 2366 tests in
  374.227s, FAILED (failures=1, errors=2, skipped=17). The exact
  same 3 environment errors as the worker claimed:
  ERROR setUpClass test_cursor_file.CursorFileTests (g++ C++26),
  ERROR test_tc02_controller
  test_typed_text_check_passes_when_fragment_is_visible (tesseract),
  FAIL test_tc02_controller
  test_typed_text_check_fails_when_fragment_is_absent (tesseract).
  Ran 2366 vs worker 2360 (+6, other lanes adding tests in the
  shared checkout; the invariant is identical). 0 new regressions.
  EXIT=1 from unittest, as expected with the 3 pre-existing errors.

### 2.2 The new tests genuinely pin the new behavior (baseline check)

- Worktree /tmp/amend2-redteam-baseline at 8f600b9 (old code),
  copied the 3 new test files in, ran the 3 targeted suites:
  test_overlay FAILED (failures=8) = 5 new + 3 amend-1 tests;
  test_s2_flip_pill FAILED (failures=1, errors=1) = sleeper test
  FAIL + old pill_release_cmd() taking no pid arg (send_browser
  ERROR); test_hypr_cmd FAILED (failures=1) = R4 test. All three
  match the worker's claim exactly. Worktree removed after.

### 2.3 Sleeper survival across SSH session end: VERIFIED LIVE

- This is the central claim of the sleeper design, and the
  worker's smoke tests did NOT prove it (their acquire-reply
  checks happen inside the acquire SSH session, and the release
  output looks the same whether the sleeper lived or died). I
  tested it directly with the exact pill_acquire_cmd construct
  (no setsid, nohup, stdin/stdout/stderr redirected):
  `nohup sleep 120 >/dev/null 2>&1 < /dev/null & echo SLEEP_PID=$!`
  via ssh-laptop.sh returned SLEEP_PID=163627. A SEPARATE ssh
  call seconds later showed pid 163627 alive, elapsed 00:07,
  `sleep 120`. Then `kill 163627`, verified SLEEPER_GONE and 0
  `sleep 120` left. The construct survives the session end on
  this machine with this SSH route. The claim holds.

### 2.4 Sleeper expiry mid-send: CLOSED by timeout arithmetic

- Worst case inside one cdp_pill_hold, every step at its SSH
  timeout: acquire 60 + activate 60 + count-check 60 +
  oneshot_code_exec 90 + v12_check 60 + release 60 = 390s,
  under the 600s sleeper life with 210s margin. V12_TIMEOUT_MS
  is 10000, bounded by the 60s ssh timeout anyway. A step that
  times out raises out of _send_browser_inner into the `with`
  exit, so the hold cannot stretch past the sum of the timeouts.
- And during the actual input there is a SECOND independent
  holder: cdp.mjs acquireCdpPill runs before the first input or
  DOM effect (cdp.mjs, act handler) and releases in the outer
  finally, keyed by the Node process pid
  (`--pid String(process.pid)`, cdp.mjs line 65). So even if the
  sleeper died mid-act, the Muse holder keeps the pill up. The
  sleeper is the sole holder only for activate and the read-only
  steps (see H1 for the activate gap).

### 2.5 Two runs picking the same sleeper pid: IMPOSSIBLE while alive

- Live pids are unique per machine by kernel guarantee; two
  concurrent runs spawn two sleepers with distinct pids and
  distinct keys. Sequential reuse needs the pid counter to wrap
  (~4M spawns, pid_max 4194304) AND a stale holder surviving
  prune, but prune runs every 2s via the daemon monitor and on
  every _ensure_daemon and cmd_status. A stale same-key entry
  would also just be overwritten by add_holder with a fresh
  timestamp. Negligible.

### 2.6 Daemon restart: holders.json cannot be lost this way

- _holders_lock is fcntl.flock on a lock file: the kernel
  releases it when the process dies, so a SIGINT-killed daemon
  cannot leave a stale lock. save_holders writes a tmp file
  then os.replace (atomic): a SIGINT mid-write leaves
  holders.json intact and at most an orphaned .tmp file.
- Verified live after the restart: holders.json holds only the
  stale bare S2-flip entry (acquired 2026-11-22T20:34:45+07:00,
  method CDP, pid null), daemon.json pid 160727 started
  2026-11-22T20:50:47+07:00, daemon alive with elapsed 06:03,
  overlay.py sha256
  4cb46f9d1329034a1e0ad9c78e5b904ebd725835ec6de0f14ff2fae78d7059ae
  matching the VM, no `sleep 600` left running. The restart
  preserved the registry and landed the new code, exactly as
  the log claims.
- The manual HYPRLAND_INSTANCE_SIGNATURE pick (`ls | head -n1`)
  was unambiguous in this instance: /run/user/1000/hypr/ holds
  exactly one entry
  (11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795342782_301493614).

### 2.7 hold() default pid and --method: correct for the live callers

- hold() defaults to os.getpid() of the calling process, and
  the calling process lives for the whole `with` block by
  definition, so the pid is alive for the hold and prune heals
  it if the caller dies mid-block. The only caller is
  chromium_cli._pill_hold (single-threaded CLI, one command per
  process). test_hold_passes_calling_pid captures the argv and
  proves acquire and release carry the same pid.
- --method accept-and-ignore loses no safety: the holder key
  is (agent, pid) and method never selected anything, so a
  wrong --method value cannot release the wrong entry. The
  pre-R11 loud rc=2 was the only signal that releases were
  broken, and the fix removes that failure mode (verified:
  release with --method now rc=0). See H5 for the observability
  note that remains.
- 0 em dash (U+2014) and 0 en dash (U+2013) in all 6 changed
  files, counted by me.

## 3. Holes found

### H1 (MEDIUM): activate runs under ONLY the sleeper holder, and nothing re-checks the holder mid-hold

- send_browser wraps activate + program + V12 in one
  cdp_pill_hold (s2_flip_live.py:703). During the program the
  cdp.mjs per-act hold is a second independent holder (section
  2.4), but activate_browser (Target.activateTarget +
  Page.bringToFront via /tmp/c5-activate.mjs, timeout 60) runs
  under ONLY the S2-flip sleeper holder: the helper is a raw
  node script with no pill/overlay reference at all (grep on
  the laptop returns nothing), and it does not go through the
  cdp.mjs act gate.
- cdp_pill_hold checks the acquire rc exactly once, then yields
  (s2_flip_live.py:666-690). Nothing in _send_browser_inner
  re-validates that the S2-flip:<sleeper-pid> key is still
  present before activate, before the program, or before V12.
- If the sleeper dies before or during activate (killed
  externally, OOM, `pkill sleep`, a laptop cleanup script),
  the monitor prunes the holder within ~2s, the pill drops,
  and activate still runs: a visible browser-control action
  (tab switch + bringToFront, a focus steal) with no pill and
  no re-check. That is the standing 18:30 rule (pill must show
  on ANY agent control) violated in that window.
- Likelihood is low: the window is ~1-2s (activate is one CDP
  call) and the trigger needs an external sleeper kill in that
  window. But there is no defense in depth at all for this
  step, and the design never measures the holder again after
  acquire. The same single-holder exposure covers the short
  gaps between acquire and body and body and release, but
  activate is the only VISIBLE action in that set (count-check
  and V12 are read-only Runtime.evaluate).
- Repro (mechanism, no live proof needed): in a test harness,
  acquire a sleeper-keyed holder, kill the sleeper, wait for
  prune (or call prune_dead_holders directly), then run the
  activate step: the step runs with no holder present and
  nothing refuses it. The code path is already proven by
  reading cdp_pill_hold: no re-check exists between the yield
  and the release.

### H2 (MEDIUM): the pid-less fallback release can delete another run's live bare holder, and reports rc=0 while the live holder stays

- When the acquire succeeds but PILL_SLEEP_PID cannot be
  parsed, cdp_pill_hold falls back to pill_release_cmd(None):
  a pid-less release (s2_flip_live.py pill_release_cmd, pid
  None branch: no --pid, no kill). A pid-less release removes
  ONLY the bare key. Two consequences:
  (a) It can delete a LIVE bare holder of another pid-less run
  of the same agent: the exact H1 bare-bare hazard this whole
  amend was built to close, reintroduced in the parse-failure
  branch. Today the only bare S2-flip holder is the stale one
  from 20:34:45, so in practice the fallback would remove a
  stale entry (harmless, arguably good), but the branch is
  structurally wrong: it fires exactly when the harness has
  lost track of its own pid, the worst moment to guess at a
  key.
  (b) It returns rc=0 having removed the wrong entry while the
  live pid-keyed holder stays and the orphaned sleeper runs
  the full 600s (no kill is issued because the pid is
  unknown). The harness notes the parse failure, so the signal
  exists in the notes, but the release "succeeds" and the pill
  stays up for up to 600s after the send.
- Trigger is near-impossible in the current transport: the
  echo line runs unconditionally when the command completes,
  so parse failure needs SSH output truncation. But the test
  test_release_falls_back_pid_less_without_parsed_pid PINS
  this behavior as intended, which enshrines the wrong
  fallback instead of flagging it.
- Repro: FakeHarness with acquire output lacking
  PILL_SLEEP_PID (the existing test does exactly this) shows
  the release command has no --pid; run against the laptop
  state with a live bare holder and it deletes that holder.

### H3 (LOW): `kill <pid>` can kill an unrelated process if the pid was recycled

- pill_release_cmd(pid) runs `kill <pid>` after the release,
  and pill_acquire_cmd runs `kill $SLEEP_PID` on acquire
  failure. If the sleeper died and its pid was recycled by an
  unrelated process before the kill runs, the kill terminates
  that process. Likelihood is negligible in practice: reuse
  needs the pid counter to wrap to that exact pid inside a
  seconds-long window (pid_max 4194304), and the release
  normally runs seconds after the acquire. Hardening only
  (see C3): verify /proc/<pid>/cmdline is a sleep before
  killing, or kill by exact match.

### H4 (LOW): hold() same-pid threads, and pid validity across namespaces/machines

- Two threads in one process calling hold() with the same
  agent share one key (same os.getpid()); thread A's release
  drops thread B's holder mid-block. No threaded caller
  exists today (chromium_cli is single-threaded, one command
  per process). Latent only.
- os.getpid() in a pid namespace or container returns a
  namespaced pid that may collide with, or be absent on, the
  host where the daemon runs; the daemon's prune
  (os.kill(pid, 0)) would misjudge it. No containerized caller
  exists. The docstring warns the pid "must be real on the
  machine holding the registry" but nothing enforces it: a
  future VM-side caller of hold() targeting the laptop would
  get its holder pruned in ~2s, the exact regression the log
  documents for VM pids (20:38 experiment). Latent only.

### H5 (LOW): cmd_release always returns 0, so silent no-op releases are invisible

- cmd_release returns rc=0 even when was_present is False
  (wrong pid, wrong agent typo, already pruned). This is
  pre-existing, not introduced by amend2, but amend2's
  fallback path makes silent no-op releases more likely
  (parse failure, pid-less release, removes the stale bare
  entry or nothing, rc=0). The harness notes the parse
  failure, so the signal exists in notes, not in rc.
  Observability only (see C4): log a warning when
  was_present is False and a pid was given.

### H6 (LOW, procedural): the daemon restart has no wait-for-death and no bind-failure retry

- The worker ran `kill -INT 115582` then immediately started
  a new daemon with setsid nohup, with no poll for the old
  pid's death or the socket/daemon.json unlink, and no retry
  if the manual bind fails (a bind failure kills the new
  daemon with a traceback and leaves no daemon until the next
  _ensure_daemon). In this instance it worked (verified pid
  160727, status ok, no competing daemon), and _ensure_daemon
  self-heals the failure mode, but the procedure as written
  in the log is racy by construction: if a live run's
  _ensure_daemon spawns a daemon in the window, the manual
  start dies on bind and the log does not say what the worker
  would have done then. Recommend the procedure poll until
  the old pid is gone and the socket is unlinked before
  starting, and verify the started pid matches daemon.json.

## 4. Residual for Muse tong (NOT a condition, NOT a hole in this amend)

- R1: the stale bare S2-flip holder (acquired 20:34:45+07:00,
  pid null) still pins the pill up around the clock. It is
  never pruned (bare keys carry no pid) and no pid-keyed
  release ever touches it, so the daemon never idle-exits
  and the "pill off = nobody driving" signal is broken. The
  manual cleanup is `overlay.py release --agent S2-flip`
  (pid-less) on the laptop, and it is safe NOW: no live
  caller is pid-less anymore, so a pid-less release can only
  remove this stale entry. The decision belongs to Muse tong;
  I did not release it, per the brief. Until it is cleaned,
  every live run's pill acquire adds a pid-keyed holder
  alongside a permanently-up pill.

## 5. Verdict: GO WITH CONDITIONS

The amend closes what it was asked to close: H1 bare-bare is
fixed for every live caller (hold() default pid, s2_flip
sleeper pid, cdp.mjs and first_action own pid), R11 is fixed
(release accepts --method, verified rc=0), E1/E2 tests exist
and genuinely fail on old code, C2+R4 are in, and H2 is done
(laptop synced to 14cf4dc, daemon restarted 115582 to 160727,
smoke acquire/release pass, S2-flip preserved). The full
suite is clean of new regressions on my own re-run.

Conditions, all before the next live proof unless marked
optional:

- C1 (mandatory, H1): re-check the holder before the visible
  step. In send_browser, verify the S2-flip:<sleeper-pid> key
  is still present (overlay.py status or holders.json) right
  before activate, and abort the send if it is gone; or route
  activate through a pill-holding path (chromium_cli
  _pill_hold or the cdp.mjs act gate). Add a test: kill the
  sleeper between acquire and activate, the send aborts before
  activate, 0 visible actions run.
- C2 (mandatory, H2): remove the pid-less fallback release in
  cdp_pill_hold. When the pid cannot be parsed, release
  nothing, note it, and let prune heal the holder at sleeper
  expiry. Update
  test_release_falls_back_pid_less_without_parsed_pid to
  assert NO release call (or a note only) instead of a
  pid-less release.
- C3 (optional hardening, H3): verify /proc/<pid>/cmdline is
  a sleep before killing in pill_release_cmd and
  pill_acquire_cmd, so a recycled pid is never killed.
- C4 (optional observability, H5): cmd_release logs a
  warning when was_present is False and a pid was given, so
  silent no-op releases are visible in the log.
- C5 (optional procedural, H6): write the daemon restart
  procedure down with a wait-for-death poll (old pid gone,
  socket and daemon.json unlinked) before starting the new
  daemon, plus a bind-failure retry.
- C6 (note only, H4): record that hold() assumes one
  (agent, pid) per live run and a pid valid on the registry
  machine; no threaded or namespaced caller exists today.

## 6. Evidence appendix (Lauren Tan: command, output, commit hash, time)

- Task received ~20:53 +07, 22/11/2026. HEAD at review start
  4a4fae3 (amend2 log hash commit on top of 14cf4dc).
- Diff scope: git show --stat 14cf4dc, 6 files, 305 insertions,
  26 deletions. Commits 448fee6 and 4a4fae3 are docs-only.
- Targeted, re-run by me ~20:55 +07: test_overlay Ran 27
  OK (0.026s); test_s2_flip_pill Ran 5 OK (0.001s);
  test_hypr_cmd Ran 25 OK (0.003s); test_chromium_cli Ran 23
  OK (1.409s).
- Full suite, re-run by me, finished 21:02 +07: Ran 2366
  tests in 374.227s, FAILED (failures=1, errors=2,
  skipped=17); the 3 errors are the known environment ones
  (g++ C++26 cursor file, tesseract x2 in tc02_controller).
  Log /tmp/c2-amend2-redteam-fullsuite.log.
- Baseline worktree at 8f600b9 with new test files, ran by me
  ~21:02 +07: test_overlay FAILED (failures=8);
  test_s2_flip_pill FAILED (failures=1, errors=1);
  test_hypr_cmd FAILED (failures=1). Matches the worker claim.
  Worktree removed.
- Sleeper survival, live on the laptop ~20:56 +07:
  ssh-laptop.sh `nohup sleep 120 >/dev/null 2>&1 < /dev/null &
  echo SLEEP_PID=$!` returned SLEEP_PID=163627; separate ssh
  call showed pid 163627 alive, elapsed 00:07, `sleep 120`;
  kill 163627, verified SLEEPER_GONE and 0 `sleep 120` left.
- Laptop state, read-only ssh-laptop.sh ~20:57 +07:
  holders.json holds only the bare S2-flip entry (acquired
  2026-11-22T20:34:45+07:00, method CDP, pid null); daemon.json
  pid 160727 started 2026-11-22T20:50:47+07:00; daemon alive,
  elapsed 06:03; overlay.py sha256 4cb46f9d1329034a1e0ad9c78e5
  b904ebd725835ec6de0f14ff2fae78d7059ae, matching the log;
  no `sleep 600` running; /run/user/1000/hypr/ holds exactly
  one entry.
- Timeout arithmetic: acquire ssh 60 + activate 60 +
  count-check 60 + oneshot_code_exec 90 + v12_check 60 +
  release ssh 60 = 390s worst case inside one hold, under
  PILL_SLEEP_SECONDS 600. V12_TIMEOUT_MS is 10000.
- cdp.mjs gate: acquireCdpPill before the first input or DOM
  effect, released in the outer finally; acquire passes
  `--pid String(process.pid)`. /tmp/c5-activate.mjs: grep
  pill/overlay returns nothing.
- _holders_lock is fcntl.flock; save_holders is tmp file then
  os.replace. 0 em dash and 0 en dash in all 6 changed files,
  counted by me.
- Files changed by me (review only):
  improvements/w-pillfix-amend2-redteam-review.md (new, this
  file). No amend file modified. No live proof run. No
  S2-flip holder released. No reviewer spawned.
