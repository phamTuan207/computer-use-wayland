# Council 1 review log: B2-4 step 10 (A5 migrate + prep log + 3 procedures)

Reviewer: council 1, doc lap. Task: review only, no worker code
changed, no live run, no browser work, no push. Worktree
~/workspace/mochi-b2-4-work, HEAD ed4fcd4
(ed4fcd49775db4c61f5238ce10ea515bcbd6e294), plus worker changes
uncommitted. Review started 2026-11-23 00:21 +07, finished
00:28 +07. No em dash or en dash anywhere in this file. No
personal info.

## 0. Evidence contract (written BEFORE any runnable check)

Orientation reads done before this contract (00:20-00:21 +07):
git status, git log, full read of scripts/s2_flip_live.py,
tests/test_s2_flip_wiring.py, the 3 drill files, prep log lines
1-330, and git diff stat plus prep log diff. No test was run, no
mutation was tried, no coordinate was re-measured before this
section was written. Every runnable check below was stated here
first. A check with no contract line here does not count.

Finish conditions, each needs command plus output plus commit
hash plus time log:

- C1, full new test file passes: `python3 -m pytest
  tests/test_s2_flip_wiring.py -q` run in the worktree.
  Expected: exit 0, zero failures, collected count equals the
  HEAD baseline count plus 8 new tests (baseline counted with
  grep on `git show HEAD:tests/test_s2_flip_wiring.py`).
  Hash: ed4fcd4 plus uncommitted worker diff, stated as such.
- C2, mutation per new test (8 mutations, one per new test in
  BrokerCodeExecTests, applied ONLY to a copy under /tmp, never
  to the worktree): M1 change the broker args, M2 force oneshot
  even with a lease, M3 fall back on result failure too, M4
  fall back on the disabled envelope, M5 use broker even with
  transport oneshot, M6 drop the transport validation, M7
  default the CLI transport to oneshot, M8 refuse fallback on
  pre-dispatch refusal. Expected: each mutation makes its one
  target test FAIL (exit nonzero for that test) while the other
  7 new tests still pass. A mutation that leaves its test
  green means that test is hollow for that behavior.
- C3, coordinates re-measured at HEAD ed4fcd4 with grep, at
  least 5: session_remote.py _launch line, the owner_lock
  holder list (count plus files plus lines), cu.py
  stop_session_on_error request_stop line, overlay.py total
  lines plus Daemon line, s2_flip_live.py broker_code_exec,
  _code_exec_send and oneshot_code_exec lines. Expected: each
  measured value either matches prep log section 9 or the
  mismatch is recorded as a finding with both values.
- C4, broker client cross-check with grep on
  scripts/session_remote.py: `code-exec` in the COMMANDS
  allowlist, request and result subcommands accept --lease-file
  plus --sequence, _client_start, _client_start_with_wait and
  _client_finish lines. Expected: all present, or the absence
  is recorded as a finding.
- C5, no em dash or en dash in any new or changed file:
  `grep -n` for the two characters across the 7 files under
  review. Expected: zero hits.
- C6, syntax: `python3 -m py_compile scripts/s2_flip_live.py
  tests/test_s2_flip_wiring.py`. Expected: exit 0.
- C7, HEAD label check: `git log --oneline 0400e86..ed4fcd4`
  plus `git diff 0400e86 ed4fcd4 --stat`. The drills and prep
  log section 9 claim HEAD 0400e86. Expected: either 0400e86
  is the worktree HEAD (it is not, per git rev-parse above) or
  the drift is measured and judged: do the commits between the
  two touch any file the coordinates cite.
- C8, trust pyramid spot check: for each finding, first ask
  whether a check can decide it, second whether the design can
  make the wrong choice impossible, only then a text rule.
  Recorded per finding in section 6.

Deviation from the contract, recorded honestly: pytest is not
installed in this VM (`python3 -m pytest` answers `No module
named pytest`), so C1 ran under unittest
(`python3 tests/test_s2_flip_wiring.py`), the same runner the
worker log cites for this VM. The contract expectation (exit 0,
zero failures, baseline plus 8) is unchanged, only the runner
differs. C2 expectation refined by evidence: M2 is a broad
mutation (forces oneshot for every broker call), so it
coherently fails 4 tests, not just its target; the pass
criterion applied is that the target test does not pass under
its mutation, and the other 7 pass except for coherent
collateral on a broad mutation. See section 3.

Verdict scale: PASS, CHUA PASS (with concrete findings),
INCONCLUSIVE (with reason). The grader is never the writer:
every number below is re-measured from source, not copied
from the worker log.

## 1. Scope and files reviewed

- scripts/s2_flip_live.py, 1230 lines, diff 245 lines
  changed.
- tests/test_s2_flip_wiring.py, 1011 lines, 196 lines added.
- improvements/worker-click5-step10-prep-log.md, 961 lines,
  diff 118 lines (holder 4 to 5, coordinates re-measured,
  section 9 added).
- improvements/mochi-b2-4-a5-fallback-drill.md, 174 lines.
- improvements/mochi-b2-4-a3-wedge-drill.md, 212 lines.
- improvements/mochi-b2-4-a4-cb10-probe.md, 154 lines.
- improvements/mochi-b2-4-worker-log.md, 397 lines, used only
  for cross-check, never as proof in place of re-measurement.
- Sources read before judging: prep log at HEAD (873 lines),
  scripts/session_remote.py (broker client and request
  handling), scripts/session_driver.py relay allowlist,
  docs/zen-error-fix-todolist-20261121.md sections 2.2.3 and
  4.13, docs/decision-2-2-3-hyprglass-test-20261121.md,
  improvements/worker-click5-step8-log.md section 6.2, and the
  Lauren Tan workflow doc.

## 2. Migration correctness (read from source, verified in section 5)

- Broker envelope, CORRECT. broker_code_exec sends args
  ['code-exec', '--endpoint', endpoint, '--program', '-',
  '--intent', intent] with the program as stdin and
  image_policy auto, one request plus one result fetch, reusing
  self.broker() and self.driver_result(). The shape matches
  the one-shot envelope (ok, api_calls, elapsed_ms, error,
  error_type, log). 'code-exec' is on the broker allowlist
  (session_remote.py COMMANDS line 42), _validate_envelope
  accepts args[0] in COMMANDS (line 368), and the driver relay
  allowlist contains 'code-exec' (session_driver.py line 164).
  The broker request subcommand accepts --lease-file,
  --sequence, --request (lines 1600-1602) and result accepts
  --lease-file, --sequence (lines 1604-1605), exactly the flags
  the harness passes.
- Lease and sequence threading on the success path, CORRECT.
  run() routes, then sends, then broker_finish in finally, so
  sends run INSIDE the broker session. The sequence threads
  across browsers through broker_next_seq: broker success
  returns seq plus 1, pre-dispatch fallback returns seq
  unchanged (no broker sequence consumed), oneshot transport
  returns seq unchanged. The broker accepts a request only
  with the next expected sequence and answers 'accepted'
  (session_remote.py line 836); result statuses are
  completed, failed, unknown (lines 734, 751, 765), and the
  harness checks 'accepted' and 'unknown' exactly as the
  broker emits them.
- Fallback only pre-dispatch, CORRECT per send. _BrokerSend-
  NotAccepted is raised only when the request call failed or
  the broker answered with something other than accepted.
  A broker result failure raises RuntimeError, which is not
  caught as NotAccepted, so no fallback runs there. The 8 new
  tests pin all three branches (section 3).
- Disabled envelope, CORRECT per send but BROKEN across
  browsers, see finding F1. _code_exec_send raises RuntimeError
  naming --transport oneshot when envelope error_type is
  'disabled', with no fallback for that send. The unit test
  pins this for one browser. The multi-browser sequence bug
  (F1) defeats it for the second browser.
- One-shot kept as fallback and recovery, CORRECT.
  oneshot_code_exec is kept with the same behavior and its
  docstring says FALLBACK AND RECOVERY PATH. CLI gains
  --transport broker/oneshot (default broker). Run JSON gains
  a transport field and each send program dict gains a
  transport field (broker, broker-fallback-oneshot, oneshot).
- run() restructure, CORRECT as designed and NOT the cause of
  F2. The worker moved sends inside the broker session, which
  the A5 gate requires. The A5 drill step 3 problem (F2) is
  that the drill asks the harness to run a whole run while the
  broker is dead; the harness has no run-level oneshot mode,
  only a send-level fallback.
- Docstring overclaim, MINOR, see finding F8. The header
  docstring says the send goes "through the broker client
  (session_remote.py _client_start, _client_start_with_wait,
  _client_finish, subcommands start and request)", but the
  harness never calls those Python functions; it shells the
  CLI subcommands start, request, result, finish directly,
  and broker_start has no busy-wait. Same broker surface, so
  harmless, but the names are wrong.

## 3. The 8 new tests (mutation results)

Baseline: HEAD test file has 32 test defs in 2 classes;
worktree file has 40 test defs in 3 classes. The new class
BrokerCodeExecTests holds exactly the 8 claimed tests. Full
file: 40 tests OK (section 5). Wiring plus pill: 46 tests OK.

Mutation runs (copy under /tmp/b24-mut, worktree untouched,
each mutation runs the 8-test class):

- M1, change broker args 'code-exec' to 'codeexec':
  target test_broker_code_exec_sends_code_exec_envelope FAILS,
  other 7 pass.
- M2, force oneshot even with a lease: target
  test_send_browser_with_lease_uses_broker_by_default FAILS,
  plus 3 collateral failures, all broker-default tests. The
  collateral is coherent for a broad mutation; the target
  does not pass.
- M3, fall back on result failure too: target
  test_result_failure_never_falls_back FAILS, other 7 pass.
- M4, remove the disabled check: target
  test_disabled_envelope_never_falls_back FAILS, other 7 pass.
- M5, ignore the transport flag (use broker even with
  transport oneshot): target
  test_oneshot_transport_forces_oneshot_with_lease ERRORS
  (AssertionError from the mocked broker), other 7 pass. An
  error is not a pass; the mutation is caught.
- M6, drop transport validation: target
  test_invalid_transport_raises FAILS, other 7 pass.
- M7, default CLI transport to oneshot: target
  test_cli_maps_transport FAILS, other 7 pass.
- M8, refuse fallback on pre-dispatch refusal: target
  test_pre_dispatch_refusal_falls_back_to_oneshot_once FAILS,
  other 7 pass.

Conclusion: no hollow test among the 8. Every target behavior
is pinned by its test. Gap: all 8 tests are single-browser
send_browser calls. No test covers the two-browser sequence
threading on the error path, which is exactly where finding
F1 lives. A two-browser test with a broker mock that models
accept-time consumption would have caught F1.

## 4. Holder list and coordinates (re-measured at ed4fcd4)

- Holder list 5, CORRECT. grep over scripts finds 8
  owner_lock() call sites: 5 external (activate-cursor-guard
  63, activate-session-backend 72, setup 314, visuals 242,
  sync-installed 115) plus 3 tree-internal in
  cursor_session.py (104, 125, 142). sync-installed.py loads
  cursor_session with importlib (lines 103-107), so a plain
  grep for `import cursor_session` misses it; the worker's
  explanation for the miss is correct. The prep log sections
  3.1, 3.2, 3.3 item 5 now say five, consistent.
- cursor_session.py, 344 lines, all 12 symbols match section
  9: prepare 22, request_stop 27, restore 39, owner_lock 73,
  drain_input 87, SessionVisuals 93, recover 103, stop 120,
  guardian 136, stop_group 208, terminate_driver 220,
  supervise 228.
- session_remote.py, 1681 lines: _launch 520 (prep said 522),
  _client_start 1456, _client_start_with_wait 1494,
  _client_finish 1563, start subcommand 1591, request
  subcommand 1599. All match section 9.
- cu.py: stop_session_on_error request_stop at 3460 (prep
  said 3458-3459), other call sites 3105, 3109, 3110, 3114.
  All match section 9.
- cancel_hotkey.py: latch_present 59, latch 120,
  cancellation_status 157, cancellation_message 197,
  request_stop call 220, resume unlink 222. All match.
- first_action.py overlay gate: acquire_overlay 116,
  overlay_visible 150, release_overlay 167, import overlay
  978. All match.
- session_cleanup.py: guardian doc lines 5-6, holder check
  lines 62-69. Match.
- overlay.py, 693 lines, all 32 symbols match section 9:
  _log 48, _label_for 62, _prepare 71, _holders_lock 77,
  load_holders 88, save_holders 96, _holder_key 104,
  add_holder 113, remove_holder 129, prune_dead_holders 157,
  session_live 177, session_label 194, wayland_env 202,
  Daemon 238, _spawn_native 245, _close_native 251,
  _ensure_native 260, _show_label 285, apply_holders 309,
  status_reply 349, _monitor 361, serve 377,
  _daemon_running 463, _send_socket 475, _ensure_daemon 489,
  cmd_acquire 525, cmd_release 570, cmd_status 587,
  cmd_stop 608, cmd_daemon 625, hold 631, main 659. The
  "DRIFTED HARD" note is accurate: prep said 613 lines,
  Daemon 217, serve 344, _ensure_daemon 458, cmd_acquire 494.
- ssh_mux.py, 403 lines: run 303, fresh-fallback contract
  docstring 42-47, via values 309-310, 320, 337. Match.
- s2_flip_live.py after migrate, 1230 lines:
  broker_code_exec 423, _code_exec_send 467, oneshot_code_exec
  506, send call site 928. Match. Before migrate at 0400e86:
  oneshot_code_exec 388, call site 794. Match.
- HEAD label, STALE but harmless for coordinates, see
  finding F4. The 5 commits between 0400e86 and ed4fcd4 touch
  only zen_backend.py, zen_pointer.py, f4diag files, and
  review logs; no cited file changed, so every coordinate
  above holds at ed4fcd4.

## 5. Check evidence (command, output, hash, time, elapsed)

Hash for all checks: ed4fcd4 plus uncommitted worker diff,
unless a check names another hash. Times Asia/Ho_Chi_Minh.

- C6 py_compile: `python3 -m py_compile
  scripts/s2_flip_live.py tests/test_s2_flip_wiring.py`.
  Output PY_COMPILE_OK. 00:21:28 +07, elapsed 0.106s.
- Baseline count: `git show HEAD:tests/test_s2_flip_wiring.py`
  has 32 test defs, 2 classes; worktree file has 40 test
  defs, 3 classes. Difference plus 8. 00:21:28 +07.
- C5 dash scan: grep for em dash and en dash across the 7
  files under review returns rc 1, zero hits. 00:21:33 +07.
- C1 test run: pytest is not installed (`No module named
  pytest`), so `python3 tests/test_s2_flip_wiring.py` ran
  under unittest. Output: Ran 40 tests in 0.406s, OK.
  00:21:38 +07, elapsed 0.646s. Note: the run prints one
  `pill acquire failed (best effort...): rc=255 Connection
  closed by UNKNOWN port 65535` note, because the
  ProgramShapeTests send_browser tests do not mock ssh and
  the pill acquire attempts a real SSH call, which fails
  fast here. No live effect. See observation O1.
- C1b wiring plus pill: `python3 -m unittest
  tests.test_s2_flip_wiring tests.test_s2_flip_pill`. Output:
  Ran 46 tests in 0.324s, OK. 00:25:03 +07, elapsed 0.497s.
  Matches the worker claim of 46 OK.
- Worker cross-check, session_remote plus code_exec:
  `python3 -m unittest tests.test_session_remote
  tests.test_code_exec`. Output: Ran 163 tests in 52.735s,
  OK. 00:25:58 +07, elapsed 52.898s. Matches the worker
  claim of 163 OK (worker: 51.2s).
- Baseline HEAD pristine: `git archive HEAD` to
  /tmp/b24-base-check, same two suites. Output: Ran 38 tests
  in 1.276s, OK. 00:27:23 +07, elapsed 2.323s. Matches the
  worker claim of 38 OK (32 wiring plus 6 pill). So 38 old
  tests pass before and after, 8 new tests pass after.
- C2 mutations: 8 runs of the BrokerCodeExecTests class on a
  /tmp copy, script /tmp/b24-mut/run_mutations.py. Results:
  M1 1 failure (target), M2 4 failures (target plus 3
  broker-default collateral), M3 1 failure (target), M4 1
  failure (target), M5 1 error (target), M6 1 failure
  (target), M7 1 failure (target), M8 1 failure (target).
  Copy baseline before mutations: 40 tests OK in 0.589s.
  Mutated file restored to pristine after, verified by diff.
  00:24:32-00:24:59 +07.
- C3 and C4 greps: coordinates in section 4, all re-measured
  00:21:52-00:24:25 +07. Broker COMMANDS line 42 contains
  'code-exec'; request subcommand lines 1600-1602, result
  1604-1605; _client_start 1456, _client_start_with_wait
  1494, _client_finish 1563.
- C7 HEAD drift: `git log --oneline 0400e86..ed4fcd4` shows 5
  commits (ed4fcd4, cac7d74, 59f8a44, 1b4c0f2, eec6141).
  `git diff 0400e86 ed4fcd4 --stat` shows 7 files:
  c5-zenproof-runs/c5-zen-delegate-f4diag.py,
  improvements/f4-repro-coords.py,
  improvements/f4diag-driver.py,
  improvements/mochi-b2-3-review-log.md,
  improvements/mochi-b2-5-review-log.md, scripts/zen_backend.py,
  scripts/zen_pointer.py. No cited file changed. 00:21:52 +07.
- F1 demonstration: /tmp/b24-mut/demo_seq_bug.py imports the
  worktree s2_flip_live read-only and runs two send_browser
  calls against a fake broker that models accept-time
  consumption (reused sequence with a different digest raises
  'conflict', session_remote.py _request lines 800-802).
  Output: brave outcome error (disabled envelope),
  broker_next_seq 3 (broker consumed 3, next must be 4);
  chromium reuses seq 3, hits conflict, falls back to
  one-shot, outcome sent, transport broker-fallback-oneshot,
  oneshot_calls 1, verdict line BUG. 00:27:12 +07, elapsed
  0.179s. Worktree untouched.
- A4 citations verified in docs/zen-error-fix-todolist-
  20261121.md: owner chose C at 18:24 (lines 34, 74, 194);
  indicator idle proof 122 one-second windows 0 callbacks,
  32/32 frames identical, 3 minutes 0 commits, deployed
  binary 3 windows 0 (lines 72, 74); Y6e nested LOAD TEST
  PASS 21:57, commit 915121d exists (git cat-file -t
  915121d returns commit); hyprglass not loaded live, .so
  only in backups (line 74). The backup .so paths named in
  the probe are laptop backup paths (~/.../backups/,
  per zen doc and improvements/worker-y6e-rebuild-load-log.md
  lines 514-520); they do not exist in the VM worktree.
  00:24:16-00:24:25 +07.
- A3 drill citations verified: IDLE_TIMEOUT 300.0 line 38,
  REQUEST_TIMEOUT 120.0 line 40, _fail_task 926,
  _task_recovery_required 933, _client_start_with_wait 1494.
  00:23:59 +07.
- Flag precondition verified: code_exec.py line 181 is the
  CU_CODE_EXEC enabled check; cu.py line 3101 is the flag
  check and line 3124 prints the disabled message; the worker
  log says "cu.py line 3123", which is off by one (trivial,
  worker log only, not a deliverable). session_driver.py
  line 164 allowlist contains 'code-exec'. 00:23:59 +07.

## 6. Findings (with trust pyramid per finding)

- F1, MAJOR, code: error-path broker_next_seq resets to the
  pre-send sequence even when the broker already consumed it.
  _send_browser_inner except handler sets broker_next_seq to
  seq on every exception, but every exception that escapes
  _code_exec_send happens after the broker accepted the
  request (result failure, unknown status, disabled
  envelope), so the broker next_sequence is already seq plus
  1. The next browser reuses seq with a different program,
  the broker answers 'conflict' (sequence already used for a
  different request, session_remote.py lines 800-802), and
  _code_exec_send treats that pre-dispatch refusal as a
  fallback trigger. Demonstrated live in the mock (section
  5): brave disabled, chromium sent via broker-fallback-
  oneshot. This defeats the documented disabled rule for the
  second browser: the design says a disabled envelope never
  falls back automatically and the operator reruns with
  --transport oneshot, but browser 2 already fell back and
  sent. The same overwrite also hits the v12 exception path:
  a v12 failure after a successful send overwrites the
  correct next_seq (seq plus 1) with seq. The existing tests
  do not cover it: all 8 are single-browser. Trust pyramid:
  a check decides it (the demo above, plus a two-browser
  test with an accept-modeling broker mock would pin it);
  better, the design can make it impossible (broker_code_exec
  returns next_seq equal to seq plus 1 on every post-accept
  path, or run() stops the run after a post-accept send
  error instead of continuing to the next browser). A text
  rule alone ("remember to advance the sequence") is the
  weakest fix and is not enough. Fix before PASS: advance
  the sequence on post-accept failures and add a two-browser
  test that models accept-time consumption.
- F2, MODERATE, A5 drill step 3 infeasible as written: with
  the relay stopped, the harness run dies at broker_start
  before any send. run() calls self.broker_start(lease,
  owner) unconditionally, with no transport branch, and
  routing also needs the broker, so --transport oneshot does
  not help: the run raises RuntimeError and main() writes no
  run JSON. The drill step 3 expects a run JSON with
  transport oneshot, outcome sent, V12 found, delayed count
  1, which cannot exist. Precedent: the step 8 fallback drill
  (step 8 log section 6.2) did not run the harness with the
  broker down; it used a standalone script with the direct
  one-shot JSONL path (`cu.py session -- python3 cu.py
  session-driver`, act envelope then finish). Trust pyramid:
  a code read decides it (unconditional broker_start plus
  the step 8 precedent); the design fix is a drill rewrite
  (use the direct one-shot send like step 8) or a run-level
  oneshot mode that skips broker_start and broker routing.
  Fix before GO: rewrite step 3 to the step 8 shape.
- F3, MODERATE, A5 drill steps 1, 3, 5 expect evidence the
  given commands cannot produce: pre-count 0 and delayed
  count 1. All three commands use --browser chromium with
  default fill. Fill has no pre_count (only the set_value
  branch runs count_check) and no delayed_count
  (delayed_targets only covers set_value browsers). The run
  JSONs for those commands have no delayed_count key at all.
  The worker log section 5 repeats the same expectation.
  Trust pyramid: a code read decides it (variant_for plus
  delayed_targets plus the set_value-only pre-count branch);
  the design fix is to add --chromium-set-value to the three
  commands, or change the expected evidence to fill-run
  evidence (V12 found, outcome sent, no delayed count).
  Fix before GO.
- F4, MINOR, docs: all 3 drills, prep log section 9, and the
  worker log claim HEAD 0400e86, but the worktree HEAD is
  ed4fcd4. Harmless for coordinates (C7: no cited file
  changed between the two, every coordinate re-verified at
  ed4fcd4), but the label is wrong and a future reader will
  re-measure against the wrong base. Fix: correct the HEAD
  label to ed4fcd4 in the 4 files.
- F5, MINOR, prep log: sections 4.1, 4.2, 5.1, 5.2 in place
  still carry stale numbers (overlay.py 613 lines, Daemon
  217, serve 344, _ensure_daemon 458, cmd_acquire 494;
  oneshot_code_exec 292-322, call site 531). The corrected
  numbers live only in section 9. The worker log section 9
  admits this and tells future workers to use section 9, but
  a reader of sections 4 and 5 gets wrong numbers. Trust
  pyramid: a text rule ("use section 9") is the weakest
  form; the design fix is to correct the numbers in place
  or add a pointer at the top of sections 4 and 5 to
  section 9. Fix: correct in place.
- F6, MINOR, A3 drill: the in-run observations have no exact
  commands and no timing mechanism. The second-start lock
  probe says "run it from a separate shell" with no command
  named; the broker status polls every 5s name no status
  command; the lock refusal, the driver process group, and
  the latch-absent check must all land inside one short
  dry-run window, with no stated hold. The drill is still
  usable, but the operator must improvise the commands and
  race the run. Fix: name the exact commands and state how
  the session stays alive long enough for the probes.
- F7, MINOR, A4 probe: step 1 names backup .so paths that do
  not exist in the VM worktree (they are laptop backup paths)
  and gives no expected hash, so "verify the .so hash before
  loading" cannot be executed as written; step 3 names no
  script or schedule for the scripted LIQUID driver, and the
  Y6e launcher file is not named (it exists:
  improvements/worker-y6e-nested-load-test.sh). The probe is
  honest about what it does not do (no probe run, no choice
  made, stage (a) BLOCKED), and its citations check out
  (section 5). Fix: name machine plus full path plus expected
  hash, name the launcher file, name or attach the driver
  script.
- F8, MINOR, doc: s2_flip_live.py header docstring names
  _client_start, _client_start_with_wait, _client_finish as
  the delivery path, but the harness shells the CLI
  subcommands directly and never calls those Python
  functions, and broker_start has no busy-wait. Same broker
  surface, so harmless. Fix: name the subcommands only.
  Prep log section 5.2 repeats the same list; fix it there
  too if it is touched.

Observations, not findings:

- O1: the ProgramShapeTests send_browser tests do not mock
  ssh, so running the test file attempts a real SSH call in
  cdp_pill_hold. It fails fast here (rc 255) and the
  best-effort hold lets the tests pass, but on a network
  where SSH hangs the tests could stall up to the 60s pill
  timeout. Mock ssh in those tests like BrokerCodeExecTests
  does.
- O2, trivial: Harness.__init__ validates program_variant
  twice (lines 233 and 246). Dead code, harmless.
- O3, trivial: worker log "cu.py line 3123" for the flag is
  off by one (check at 3101, disabled message at 3124).
  Worker log only, not a deliverable.

What the worker got right and this review confirms by
re-measurement: the broker envelope and allowlist, the
send-inside-session restructure, the per-send fallback rule,
the 8 non-hollow tests, the 46 and 163 and 38 test counts,
the 5-holder list with the importlib explanation, every
coordinate in section 9 (all 12 cursor_session symbols, all
32 overlay symbols, all client and gate lines), the A3 drill
citations, the A4 probe citations and its honest BLOCKED
status, and the GO and abort conditions in all 3 procedures
(the drills all say PREPARED ONLY, NOT RUN, and need an
explicit GO from Muse tong).

## 7. Verdict

CHUA PASS.

Reasons: finding F1 is a real defect in the migrate code,
demonstrated dynamically, and it defeats a documented safety
rule (disabled envelope never falls back automatically) on
multi-browser runs. Findings F2 and F3 make the A5 fallback
drill unrunnable and unverifiable as written: step 3 cannot
reach a send with the broker down, and steps 1, 3, 5 expect
pre-count and delayed count evidence that a chromium fill run
never produces. The rest is verified: the envelope, the
success-path sequence threading, the per-send fallback rule,
the 8 tests, all coordinates, and the A3 and A4 procedures
with their GO and abort conditions.

What must change before PASS:

1. Fix F1: advance the broker sequence on post-accept
   failures (or stop the run after a post-accept send error)
   and add a two-browser test with a broker mock that models
   accept-time consumption, proving the second browser does
   not fall back after a first-browser disabled envelope.
2. Fix F2: rewrite A5 drill step 3 to the step 8 shape
   (direct one-shot send, not the full harness) or add a
   run-level oneshot mode.
3. Fix F3: add --chromium-set-value to the A5 drill commands
   or correct the expected evidence to fill-run evidence.
4. Fix F4, F5, F7, F8 (minor doc corrections) in the same
   round; F6 in the same round if the coordinator wants the
   A3 drill executable without improvisation.

No live proof is claimed here and none is needed for this
verdict: the A5 gate item 2 live proof and the 3 drills still
need a GO, as the worker log already states. This review
judges the code and the procedures only.
