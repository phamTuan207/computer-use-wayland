# Worker C5-STEP8 log: S1/CB-6 broker deletion (per-batch spawn removed, broker only)

Owner: the owner. Coordinator: COORD-CLICK-5. Repo
~/workspace/computer-use-wayland, branch todolist-push. This worker
did NOT do the S2 flip, the input fix, or the P2 work, so this is
independent work. No em dash or en dash anywhere in this file. No
personal info. Wall-clock Asia/Ho_Chi_Minh plus elapsed time on
every entry.

## 0. Task and starting point

- Task received 13:47 +07, Sun 2026-11-22 (T+0m). VM HEAD 04bc942
  at start. Final direction
  improvements/worker-click3-final-direction-log.md (commit
  e05fc58), section 3 step 8. Deletion spec
  docs/batch11-task2-step8-deletion-spec-20261122.md (clone1
  batch 11 task 2, origin/main commit e0187d7), read from
  origin/main before acting.
- Step 8 as ordered in the final direction: (a) sync the laptop
  tree and re-verify browser observe through the broker; (b)
  decide the fatal-on-read-failure behavior; (c) specify the
  queue discipline and the single-owner serialization under
  concurrent VM workers; (d) delete the per-batch spawn, keeping
  one-shot SSH as fallback and recovery. Session-level pill in
  the same step, with the CB-10 precondition.
- EXCLUDED from this task: the session-level pill. It stays OUT
  because the CB-10 precondition is still owed: the LIQUID
  flicker probe has not run, and there is no explicit owner
  deferral recorded. The pill half of step 8 is deferred, not
  forgotten. The overlay server is NOT touched in this task.
  Recorded as BLOCKED on the CB-10 precondition (see section 8).
- ALSO EXCLUDED: the (b1) durable landing in cdp.mjs (separate
  follow-up, spec coming from clone1 batch 12 task 2). cdp.mjs
  is not touched here. The Zen backend and the validator are not
  touched here.
- Focus rule (C5-FOCUS-INCIDENT, commit 2d198c4, section 7, read
  in full before acting): verify `hyprctl -j activewindow` in
  the SAME SSH call immediately before each keystroke batch;
  re-verify after any gap over 60 seconds or any intervening
  non-keystroke command; use only the working focus form
  `hyprctl dispatch 'hl.dsp.focus({ window = "address:0x..."})'`;
  never the string dispatcher form; if the focus command errors
  or the active window is wrong, STOP and do not send the key.
  Prefer CDP-only work with NO keystrokes. Laptop SSH only via
  ~/workspace/ssh-laptop.sh; long jobs detached (setsid nohup
  ... & disown), short checks only. Clone2-watch holds run
  :11:56, :26:56, :41:56, :56:56 (hold about start+1m to
  start+2m40s); verify live, never rely on the schedule.
- LESSON from C5-P2-AMEND-FIX: do NOT trust /tmp persistence
  across minutes on the laptop for live-run drivers; /tmp
  driver files vanished between 13:25 and 13:32 for an
  unestablished reason. Live-run drivers go in a persistent
  path (~/c5-step8-run/) with copies on the VM.
- LESSON from C5-P2-AMEND-FIX: `computer-use act` needs the
  persisted STATE observation file (result['observation'],
  backend='desktop'), NOT the observe stdout result; passing
  stdout fails with "desktop observation required", and the
  failing child calls stop_session_on_error(), which kills the
  session driver silently mid-run.
- Window map (re-list each run): ws1 Zen 0x557052b62dd0 (PID
  496121); ws2 clone1 Brave 0x55705383d420 (PID 1119832 after
  the reopen rollback), clone2 Chrome 0x5570538ed160 (PID 8059,
  app window, no tab strip). Brave is back on NO debug flag
  ([::1]:9223 closed); if CDP on Brave is needed, redo the
  P3-style relaunch and roll back afterwards. WINDOW MAP CHANGE
  recorded 14:53:13 +07 (section 6.1): the Brave relaunch moved
  Brave from ws1 to ws2; current layout is Zen ws1 [2509, 914]
  [1863, 1176] (full width), Chrome ws2 [2533, 914] [901,
  1176], Brave ws2 [3448, 914] [901, 1176]. Chrome resized 1853
  wide to 901 wide during smoke run 1 (cause not established;
  per-send fresh grounding made it harmless). Flag the layout
  change to the coordinator; do not move windows back
  unprompted.
- Test messages go into the clone1 and clone2 threads only.
  Clone2 is capped until Nov 25 02:38 (its account cannot
  work), but receiving test messages in its thread needs no
  clone2 activity. No other thread, no other tab.

## 1. Time log

- 13:47 +07, T+0m: task received. Read the final direction
  step 8, the deletion spec in full (234 lines, /tmp copy from
  origin/main), the FOCUS-INCIDENT section 7, the S2-REOPEN log
  sections 0-3, first_action.py run() in full, session_driver.py
  relay_commands in full, session_remote.py CLI and Broker
  index, docs/layer0-cbexec-contract.md section 6.
- 13:49 +07, T+2m: laptop pre-state via ssh-laptop.sh. Laptop
  HEAD 4305dcb, 2 commits behind VM HEAD 04bc942. Relay
  service active since 09:59:40 +07, Main PID 983809,
  socket /run/user/1000/computer-use-wayland/relay.sock mode
  0600. Status: broker running, generation
  136fefc43e215fd9b491c857ed98d48f, loaded_code_sha256
  43a492177f2317a26111c44bddf7526f4b079e4d8aa59451417a11020fdd00ea,
  started_git_head 350934a, state finished, owner s2-flip-run5,
  guardian clean, recovery none, next_sequence 5,
  last_start_error cleanup_failed (see section 2, item 1c).
- 13:53 +07, T+6m: laptop fast-forwarded 4305dcb to 2fc4661
  (origin moved during the task: 2fc4661 is a docs-only coord
  log commit; the 04bc942 to 2fc4661 diff is 1 file, the coord
  log, 123 insertions). VM fast-forwarded to the same 2fc4661.
  Verified: git ls-remote origin todolist-push =
  2fc46616e201ab1c032adcf9a43d277dc022005d on both sides.
  sync-installed.py ran on the laptop: published and verified,
  --check exit 0, 647 managed files, source_commit 2fc4661,
  source_content_sha256
  24d94e422de602fe2989888538a7abc7f3bf27179680c0399533802c28ad7547,
  synced 13:53:27 +07. CB-9 manifest:
  ~/.local/share/agent-computer-use/deploy-manifest.json,
  ledger releases/20261122-135327-075417-2fc46616e2.json.
- 13:55 +07, T+8m: installed tree verified against the repo
  tree (section 2). Relay loaded hash matches current
  session_remote.py, so no relay restart is needed (section 2).
  Master watchdog / soak status recorded (section 7): the mux
  master is currently DEAD (ssh_mux.py check, alive false,
  check_rc 255); no cron watchdog is installed on the VM
  (crontab not found); the 1-day soak never ran; the 60-min
  soak reached 40 min then a VM restart cut it (PROBE-S0
  section 10). Soak is advisory-only per the final direction,
  not a gate. Relay service Restart=no, so a dead broker does
  NOT auto-restart; the one-shot SSH restart is the recovery.

## 2. Step 1: sync verification (condition 1 of 5)

- (1a) Laptop tree: fast-forwarded to 2fc4661, verified
  against git ls-remote (see time log 13:53). The diff from
  the brief's HEAD 04bc942 to 2fc4661 is log-only (coord log).
  The diff from the S2 sync point 4305dcb to 2fc4661 is also
  log-only (coord log + the P2-AMEND-FIX log, 651 insertions).
  No code changed in either diff.
- (1b) Installed tree: sync-installed.py published and
  verified, --check exit 0, 647 managed files. Installed
  hashes match the repo checkout exactly for the three files
  the broker path loads: session_remote.py
  43a492177f2317a26111c44bddf7526f4b079e4d8aa59451417a11020fdd00ea,
  session_driver.py
  9e5834e6572adc77d7d882d63fd8abcdc50e0a611ed568a9e39b0a0ded557e7a,
  first_action.py
  bee6d2d73a10bdce3625d77a764109c9a2b34bda082b14499e50ad4e51bda846
  (installed vs repo, all three identical). zen_backend.py
  NOW EXISTS in the installed tree (the brief said it was
  missing; the sync fixed that).
- (1c) Relay loaded code: the running relay (PID 983809,
  started 09:59:40 +07 at 350934a) reports loaded_code_sha256
  43a492177f2317a26111c44bddf7526f4b079e4d8aa59451417a11020fdd00ea,
  which EQUALS the current session_remote.py hash. The broker
  file itself is unchanged since 350934a (git log 350934a to
  2fc4661 for session_remote.py is empty), so the running relay
  loads the current broker code and no restart is needed. The
  driver it spawns per task comes from the laptop checkout
  (session_remote.py CU = ROOT/scripts/cu.py, ROOT is the
  checkout holding session_remote.py; the service runs
  /home/james/computer-use-wayland/scripts/session_remote.py),
  so the next start picks up the current cu.py, first_action.py
  and zen_backend.py automatically. Code changed since the
  relay started (cu.py, dom_act.py, code_exec.py, element_ref.py,
  fastpath.py, first_action.py, s2_flip_live.py, zen_backend.py,
  zen_dom.py; commits 292753f P2 and 507a50b P2-AMEND-FIX) is
  therefore live for the next broker start without a restart.
- (1d) The stale last_start_error cleanup_failed in the status
  output is a leftover record from the S2 run-5 finish, not a
  live fault: session_remote.py tick sets task.error to
  cleanup_failed only when a finishing task's driver exits
  with a non-zero code or a session token remains (line 1025).
  The current status is state finished, driver stopped,
  guardian clean, recovery none, so the broker accepts a new
  start. Verified live by the probe start in section 5 (start
  + finish cycle, owner c5-step8-probe).
- (1e) The B8c2 root cause is FIXED in the current tree:
  cu.py:40 sets BROWSER_ENDPOINT to http://127.0.0.1:9223,
  session_driver.py relay() hardcodes 9223, and the installed
  tree carries both. A browser observe through the broker no
  longer 404s for the endpoint reason. Verified live by the
  browser-observe step in the smoke run (section 6).

## 3. Fatal-on-read-failure decision (condition 4 of 5)

Decided 14:02 +07, BEFORE any deletion, adopting the deletion
spec matrix (section 5.2) with two adjustments noted below.
Reasons are recorded per class; the code changes that carry
the decision are named.

- R1. Read-only, typed transient (PreflightRefusal by internal
  provenance, or the act transient matcher): RETRY, max 1
  (2 attempts total), fresh sequence per retry, fresh
  observation per retry. Session stays alive. The retry
  re-observes INSIDE the broker session (a broker observe
  request, so the session marker updates to the fresh
  observation path), never outside it: an outside re-observe
  cannot update the marker, and the retry act would then die
  on the require_observation RuntimeError. Implemented in
  first_action.broker_attempt (client-side counter).
- R2. Read-only, unknown cause (CDP 404, wrong endpoint,
  window gone, unclear driver error, stale snapshot via the
  require_observation RuntimeError): STOP at once, 0 retries,
  session ends (fatal). Reason: retrying repeats the same
  error (a wrong endpoint 404s every time; a gone window has
  no target to re-read). No code change; this is the current
  behavior and it stays. The stale-snapshot RuntimeError is
  NOT converted to PreflightRefusal in this step: the R1 retry
  path avoids it by construction (it re-observes inside the
  session first), so no cu.py change is needed and none is
  made. The B8c2 instance of this class is fixed by the
  endpoint correction (section 2, item 1e), not by retrying.
- W1. Act, certainly unsent (preflight refusal before
  focus/input, validation failure before send): RETRY after a
  fresh re-ground, max 1, session alive. Same mechanism as
  R1, with one guard added by this worker: the retry observe
  must return the SAME region (window bounds / region) as the
  original observation, or the retry is refused and the batch
  stops with the session alive. Reason: the actions file
  carries pixel coordinates bound to the original frame; if
  the window moved, the old coordinates map to the wrong
  screen point in the new frame, and retrying would click
  the wrong target. The guard makes the retry safe by
  construction; a moved window reports for the model to
  re-ground instead of clicking blind.
- W2. Act, outcome uncertain (timeout, driver error after a
  possible send): NO retry, 0 retries, stop the batch,
  report outcome unknown with the unconfirmed action list.
  The model decides on fresh state; never auto-replay.
  No code change; this is the current timeout behavior
  (timeout never falls back, never replays).
- W3a. Non-JSON request line: error envelope, session alive,
  0 retries. Already implemented (I43). No change.
- W3b. Well-formed JSON but invalid shape (non-dict request,
  bad image_policy, args not a non-empty string array, stdin
  not a string, unsupported command): CHANGED in this step
  from a fatal ValueError (driver dies, session ends) to an
  error envelope with session_continues True, same shape as
  the I43 non-JSON branch. Reason: the command never
  executed, so input is certainly unsent; ending a live
  session over a caller typo destroys the session for
  nothing. The caller corrects the request and resends with
  the correct sequence. Code change in
  session_driver.relay_commands, with the existing test
  test_invalid_requests_never_execute rewritten to assert
  the envelope instead of the raise.
- W4. Act failed but the postcondition is already true
  (already-done): NOT implementable in this step (needs the
  P5 postcondition set). Recorded as deferred, no code.
- Broker-level errors (busy, recovery_required,
  broker_changed, cancelled, invalid_lease, broker_unavailable,
  driver_failed, nested_session, native_unavailable,
  cancellation_unavailable) are NOT in this matrix. They are
  handled by the queue discipline (section 4) and the recovery
  procedure (section 6).
- Retry counting: client-side, per task per command, in
  first_action.broker_attempt. Max 1 retry. Fresh sequence
  per retry (the broker replays the recorded response for a
  duplicate sequence, so reuse would return the same failure).
  Every stop logs class, command, sequences, reason,
  input_sent true/false/unknown, verified true/false. A
  verified true is never reported without a postcondition.
- D3 reviewer check (spec gate item 10): this matrix was
  checked against the timeout rule (W2, no replay on
  uncertain outcome) before the deletion; the timeout test
  in section 5 covers it.

## 4. Queue discipline + single-owner serialization (condition 5 of 5)

Decided 14:02 +07, BEFORE any deletion, adopting the deletion
spec sections 3.2 and 4.2 with the open values below chosen
and recorded. The spec left poll interval, backoff/jitter,
wedged threshold and the killer owner as UNKNOWN; this worker
decides them here (the coordinator holds full authority while
the owner sleeps, and these values are recorded for the
coordinator to overturn, not left open).

- One owner at a time holds pointer, overlay and Firefox
  session together (broker-enforced: one Task object, one
  Unix socket, lease authorization on every request, RLock
  around every accept/refuse decision). No shared-read owner,
  no deputy owner, no temporary slot loan.
- Second starter gets `busy` from the broker. The waiter
  WAITS, never fast-fails and never opens a parallel path.
  Wait loop: poll `status` (no lease) every 5s, up to 300s
  total (one IDLE_TIMEOUT, adopted from the spec proposal).
  The wait ends when status shows state finished or failed
  AND guardian is not active AND recovery is none. Then the
  waiter unlinks its lease file and retries start with a
  FRESH start_id (the broker replays the recorded response
  for a reused start_id, so retrying with the same start_id
  would return busy forever). On 300s expiry: stop waiting,
  log busy with the current owner read from status, report
  to the coordinator. Poll interval 5s (spec proposal,
  adopted). Retry-start jitter uniform 0 to 1s (chosen here
  to break thundering-herd ties when several waiters poll
  and restart together).
- No preemption through the broker API. An owner can still
  be ended by the cancel latch (user only), the 300s idle
  timeout (broker tick), a broker restart (leases
  invalidated, broker_changed), or a driver kill under the
  recovery procedure. The coordinator never uses the cancel
  latch as a stop tool: the latch belongs to the user and
  only `resume` clears it.
- Within one owner, requests are strictly sequential: one
  request at a time, sequence strictly increasing; a second
  concurrent request gets `busy`. No queue inside the broker.
- Owner identity is the lease: owner string 1-80 chars,
  [A-Za-z0-9_.:@+-]; every request carries owner, secret and
  task generation; a mismatch is refused, never silently
  repaired. A lease has no TTL; it is invalid only on broker
  restart (generation change), wrong secret, or wrong owner.
- Owner death: a dead owner's task stays until the 300s idle
  timeout ends it, or the recovery procedure runs (section
  6). Wedged threshold: 300s with no progress and no status
  change (one IDLE_TIMEOUT, adopted from the spec interim
  proposal). The killer is the worker running the recovery,
  following spec section 6.3 in order: finish with the
  owner's lease when held (120s timeout), never the cancel
  latch, kill ONLY the driver child by PID from ps (SIGTERM,
  wait, SIGKILL when still alive; never pkill -f with a
  pattern matching the killer's own command line), verify
  the driver is dead and status shows driver stopped, only
  then unlink session.json, restart the relay, verify a
  clean status, start a fresh batch. The old batch is
  abandoned, never replayed for uncertain-outcome actions.
- Start-error handling for a waiter: busy waits as above;
  recovery_required goes to the recovery procedure (no
  retry); cancelled waits for the user to resume (no retry,
  no latch removal by any worker); broker_changed re-reads
  status and creates a new lease only after cleanup;
  invalid_lease or lease_owner_mismatch stops and reports
  (never reuse the old lease); broker_unavailable goes to
  the one-shot fallback (section 6).
- Think-time vs idle timeout (spec UNKNOWN 10): an owner
  holding a task with more than 300s between requests loses
  the session to idle timeout. act-now batches issue
  requests seconds apart, so this does not bite in this
  step. Leased status polls refresh last_activity, but no
  keepalive is added for the agent loop's think time here;
  recorded as a known limit, not fixed in this step.
- Implementation location (one implementation, two
  callers): the wait loop lives in session_remote.py as
  `start --wait SECONDS` (in-process status polling, no SSH
  round trip per poll). act-now on the laptop calls the CLI
  with --wait 300; VM harnesses call the same flag over SSH.
  The concurrency test in section 5 proves it with two
  concurrent workers.

## 5. Implementation + tests + concurrency test

### 5.1 Code changes (commits 8c6553a and 1b5a6e6, both pushed, verified via git ls-remote)

- scripts/session_remote.py (8c6553a): added `import random`;
  constants WAIT_POLL_S = 5.0, WAIT_JITTER_S = 1.0, WAIT_BUDGET_S
  = 300.0. New `_client_start_with_wait(owner, lease_path,
  wait_s=300.0, *, _sleep, _jitter, _now)`: on `busy` it polls
  status every 5s until free (state finished/failed, guardian
  not active, recovery none), unlinks the lease, retries with a
  FRESH start_id; other refusals return at once; on budget
  expiry it returns the busy response with `waited_s` and
  `current_owner`. BrokerError propagates. The `start`
  subcommand gained `--wait SECONDS` (default 0.0, fail fast,
  old behavior); a negative wait raises BrokerError
  `invalid_wait`.
- scripts/session_driver.py (8c6553a): new `_request_error(sink,
  error)` helper printing an error envelope `{'ok': False,
  'returncode': 1, 'error': <msg>, 'session_continues': True}`.
  In relay_commands the four W3b raises (non-dict request, bad
  image_policy, args not a non-empty string array, stdin not a
  string, unsupported command) are replaced with
  `_request_error(...)` + `continue`. The >8MiB request_lines
  ValueError stays fatal (transport-level, out of scope). The
  first output line is the driver-ready row `{'ok': True,
  'driver': 'ready'}`.
- scripts/first_action.py (8c6553a, then 1b5a6e6): `session_cmd`
  and `attempt_session` DELETED as live code; both kept as stubs
  that raise RuntimeError ("session_cmd was deleted in step
  8...") so any caller fails loudly instead of resurrecting the
  spawn. Removed now-unused `import signal`; added `import re`,
  `import secrets`. New `broker_attempt(observation_path,
  actions_path, deadline_s, state_dir, meta, screen, owner)`
  returning `(returncode, stdout, stderr, timed_out, elapsed_s,
  detail)` where stdout carries exactly one JSON object (the
  driver act result, or a start-failure error) so `run()` parses
  it unchanged. Flow: start with `--wait 300` (CLI timeout 360s)
  -> wait for the task to reach running (see the ready-wait fix
  below) -> request act sequence 1 -> result bounded by
  deadline_s -> finish (best-effort, 130s CLI timeout) on every
  path where a start succeeded. R1/W1 retry: on rc 1 with
  session_continues True, re-observe INSIDE the session via
  `_observe_args` (window scope: `observe --window <addr>`;
  screen scope: `observe --screen <monitor>`, plus --max-width
  and --crop from meta when present), then re-send act with a
  fresh sequence and a fresh observation, only when
  `_regions_equal` holds; max 1 retry. Timeout never falls back
  or replays; finish is still attempted. Start failures mapping
  to fallback-eligible: BROKER_START_FAILURE_ERRORS = {'busy',
  'broker_unavailable', 'broker_changed', 'broker_stopping',
  'nested_session', 'native_unavailable',
  'driver_start_failed', 'broker_command_failed'} produce out
  starting with `session guardian startup failed: broker
  <error>` (matches START_FAILURE_PREFIXES, so the existing
  `is_session_start_failure` triggers the in-process desktop_act
  fallback). `cancelled` and `recovery_required` are deliberately
  NOT in that set (out is `broker start refused: <error>`, no
  fallback). A request never accepted also maps to a
  start-failure out (no action ran). Lease and request files
  live in `cu.STATE` (user-owned dir; /tmp is root-owned so
  `_write_new_lease` would reject it), named
  `act-now-<pid>-<token>.lease` and `.json`, unlinked in
  finally. Owner via `_broker_owner` (valid agent name kept,
  else fallback `'act-now'`). `run()` rewired: the call site now
  unpacks the 6-tuple from `broker_attempt(obs_path,
  args.actions, deadline, cu.STATE, meta, args.screen, agent)`
  and sets envelope fields `broker_owner`, `broker_sequences`,
  `broker_retries`, `broker_finish` (also added to the initial
  envelope literal as None for early-return paths). Removed the
  now-unused `cu_py` assignment. `--session-deadline-s` help
  updated: it bounds each broker result wait; the 300s queue
  wait is separate. The direct Pointer fallback (in-process
  `desktop_act`) STAYS, triggered only on proven start failure.
  The act-now stdout envelope is the `envelope` dict (keys: ok,
  method 'act-now', completed, error, broker_owner,
  broker_sequences, broker_retries, broker_finish,
  session_error, first_pointer_ms, phase_ms, etc.). It has NO
  `returncode` key. Any parser of act-now stdout must match
  `method == 'act-now'` and check `ok`, not `returncode`.
- Key integration facts established while designing (do not
  re-derive): the broker session-driver runs `cu.main()` in
  process with the session token set, so `cu.py act`'s
  `require_observation` marker protocol applies; a fresh broker
  task has no marker, so act-now's externally captured persisted
  observation is accepted; after a transient refusal
  `record_refusal` creates marker `{observation: None}`, and
  only an observe INSIDE the same session updates it (via
  `record_observation`, which returns early unless a marker
  file already exists), hence the retry must re-observe through
  the broker. CB-2 on the `cu.py act` CLI path is
  binding-when-present, not mandatory (actions unstamped,
  legacy pixel path), so a retry act with a fresh observation
  works. `cu.py observe` CLI takes `--window` or `--screen`
  (mutually exclusive, required) plus `--crop` (4 ints) and
  `--max-width` (default 960).
- Ready-wait fix (1b5a6e6, the reason the first smoke failed):
  the relay answers start with status `starting` BEFORE the
  driver prints its ready line (about 0.5s of Python startup).
  broker_attempt sent the act request in that window; the
  relay's `_request` handler refuses requests while
  `task.state != 'running'` or `task.driver != 'ready'` with
  `task_stopped`; then the immediate finish set
  `finish_requested`, which made `_await_ready` raise
  `driver_not_ready` ("driver stopped during startup"), failing
  the task. Three consecutive act-now attempts failed identically
  (14:33:57, 14:39:06, 14:44:27 +07, session_attempt_ms about
  255ms, "overlay lost before fallback; refused") while direct
  CLI starts worked (their SSH latency gave the driver time to
  become ready). The shader-warmup hypothesis was tested and
  refuted (a manual driver launch immediately after an overlay
  daemon spawn succeeded at 14:45:25 +07, rc 0, ready line
  printed). Fix: new `_wait_for_task_running(remote_py,
  generation, timeout_s=30.0)` in first_action.py polls
  `status` until state `running` with driver `ready` (matching
  the start's generation); a task that fails while starting
  reports a start failure (fallback-safe); a 30s timeout reports
  unknown outcome with no replay. Wired into broker_attempt
  right after `started = True`.
- Syncs after the first commit: laptop fast-forwarded to
  8c6553a at 14:27 +07 and to 1b5a6e6 at 14:48 +07 (VM at the
  same heads, verified via git ls-remote). sync-installed.py
  ran at both points (647 managed files, 11 preserved-history
  exceptions). The 8c6553a sync restarted the relay: new PID
  1167236 (was 983809), active/running, loaded_code_sha256
  `d490f369...` matching the new session_remote.py,
  started_git_head 8c6553a5e54c6c31c18bcb3de6d347f61c3b318f,
  state idle, owner None, next_sequence 1, last_start_error
  None. The 1b5a6e6 sync did NOT restart the relay (only
  first_action.py changed; the driver loads it fresh per task).
  After the 8c6553a sync: session_remote.py
  `d490f369f6b754d200518055025ef956284a759cc49e3ee70ed6b2a4483e3da4`,
  session_driver.py `c267e5ba6cd9`, first_action.py
  `265e193f3ff5`. After the 1b5a6e6 sync: first_action.py
  `1270139f957b80a475abbc05e10e5b09fddf4769941ed4947af5aa4631f31a66`
  (repo and installed match).
- Probe of the browser-observe shape (14:15 +07,
  ~/workspace/c5-step8-run/probe-browser.py): broker start ok,
  clone2 tab found, observe returned 80 elements, composer e61
  role textarea name Message. The snapshot elements carry NO
  rect, so grounding uses c5-ground.mjs (CDP Runtime.evaluate)
  instead.
- Click-only probe (~/workspace/c5-step8-run/probe-act.py,
  clone2 composer click, no message sent): failed 3 times
  before the ready-wait fix (14:39:06, 14:44:27 +07, same
  driver_not_ready signature), then PASSED at 14:48:36 +07
  (send-act rc 0, first_pointer_ms 486.8, error null,
  session_attempt_ms 1680.6) and again at 14:50:03 +07
  (session_attempt_ms 1651.8). This was the proof the
  ready-wait fix worked before the smoke ran.

### 5.2 Tests updated and results

- tests/test_first_action.py: TestAttemptSession and
  TestSessionCmd replaced with TestDeletedSpawn (stubs raise),
  TestBrokerOwner, TestRegionsEqual, TestObserveArgs,
  TestBrokerAttempt (9 tests with a faked `_broker_cli`:
  success, busy-start falls back, cancelled never falls back,
  recovery_required never falls back, transient retries once
  on the same region, transient no retry when the region moved,
  result timeout never falls back, start waits for running
  before request, start failed before request falls back). The
  fake CLI is scripted in order; every script that reaches the
  request phase includes a `('status', {'ok': True,
  'generation': 'g1', 'state': 'running', 'driver': 'ready'},
  0)` entry after start. TestRun._run and _run_raw_args now
  mock `broker_attempt` and append a default broker detail dict
  to the old 5-tuple session results; the four
  `assert_not_called` mocks renamed to `broker_attempt`.
- tests/test_session_driver.py:
  `test_invalid_requests_never_execute` rewritten to assert the
  error envelope + session stays alive + the status request
  executes exactly once (previously asserted ValueError).
- tests/test_session_remote.py: new
  `ClientStartWaitTests(SessionRemoteIntegration)` (3 tests,
  real in-process broker + fake driver, WAIT_POLL_S patched to
  0.2, jitter 0): the waiter starts after the holder finishes
  with a fresh start_id (the background thread sends a finish
  exchange only, because `finish_owned_task`'s wait for state
  `finished` races the waiter replacing it with `running`; it
  also waits for driver ready before asserting state `running`);
  wait budget expiry reports busy with the current owner (2s
  real budget); a non-busy refusal (cancelled latch) returns at
  once.
- tests/test_visual_delivery.py:
  `test_invalid_delivery_policy_never_executes_input` updated
  to the W3b envelope shape (the old test asserted ValueError
  for image_policy "never"; the invariant "never executes input"
  is preserved, the mechanism changed). The envelope is
  top-level `{'ok': False, 'returncode': 1, 'error':
  'image_policy must be auto or always', 'session_continues':
  True}`; row 0 of relay_commands output is the driver-ready
  row. The test patches execute with `return_value=
  subprocess.CompletedProcess([], 0, '{"ok": true}', '')` and
  asserts the error envelope, session_continues True, no
  session_ended, the status result `{'ok': True}`, and execute
  called once with `['status']`.
- Results: `tests.test_first_action tests.test_session_driver
  tests.test_visual_delivery` = 124 tests OK (1.017s, after the
  ready-wait fix); full three-file run including
  test_session_remote = 225 tests OK (41.5s). Full suite
  (`python3 -m unittest discover -s tests -q`, 2192 tests): 0
  failures, 1 pre-existing environment error only:
  test_cursor_file setUpClass, `g++: error: unrecognized
  command-line option '-std=c++26'` (the VM's g++ has no C++26
  support; unrelated to this task, verified separately at
  14:31 +07).

### 5.3 Concurrency test: PASSED (14:30:39-14:31:13 +07, run c5-step8-conc-073039)

- Script: ~/workspace/c5-step8-run/concurrency_test.py
  (renamed from concurrency-test.py because the hyphen was not
  importable). Worker A (owner c5-step8-conc-A) starts first,
  holds about 15s (observe screen, 12s hold, windows, finish);
  worker B (owner c5-step8-conc-B) starts +2s with `start
  --wait 300`, then runs observe + windows. An independent
  observer thread polls status every 2s. Assertions: B starts
  only after A finishes (timestamps), B start wall >= 8s
  (proves it waited), both workers complete all requests, no
  lost action. Read-only commands only (observe, windows); no
  desktop action, no keystrokes, no test messages. Lease and
  request files in /home/james/.cache/agent-computer-use,
  cleaned up in finally. Uses scripts/ssh-laptop-mux.sh (S0 mux)
  for all SSH calls; envelopes written via SSH stdin (`umask
  077; cat > <file>; chmod 600`).
- BUG FOUND AND FIXED in the test itself (14:30 +07): the first
  two runs failed rc=2 because `broker_call` never passed
  `--owner` to the start command (argparse exits 2 on the
  missing required flag; the error went to stderr, which the
  test did not log). Fixed: `broker_call` now adds `--owner
  <owner>` for the start command only (request/result/finish
  take only --lease-file); the worker error message now includes
  stderr.
- Evidence log: ~/workspace/c5-step8-run/concurrency-test-c5-step8-conc-073039.jsonl.
  A started (1.07s), ran observe + windows, held 12s,
  finished clean (guardian clean, error null). B started with
  --wait 300, wall 22.120s (waited out A), started 3.405s
  after A finished, ran both requests to completion, finished
  clean. No interleaving, no lost action. Queue discipline
  proven live on the new code.
- A debug start earlier (14:28 +07) also worked through the
  same harness (owner c5-step8-dbg2, finished clean); the
  first two concurrency runs failed only on the missing --owner
  test bug, not the broker.

## 6. Live smoke + fallback drill

### 6.1 Live smoke: PASSED (14:50:14-14:51:56 +07, 2 runs, 4 sends)

- Driver: ~/workspace/c5-step8-run/smoke.py. Grounding is
  deterministic, no vision: the composer rect + viewport
  metrics from CDP (c5-ground.mjs), window bounds from
  hyprctl, viewport origin = [win_x, win_y + win_h -
  innerHeight*dpr], screen point = origin + rect center * dpr,
  image point from the screen observation meta
  (region/image_size). The observation is captured fresh per
  send via direct SSH `cu.py observe --screen eDP-2` (under
  120s old when act-now runs). Focus-verify + act-now in one
  SSH call via laptop script ~/c5-step8-run/send-act.sh
  (focuses the target window, verifies hyprctl activewindow
  shows that address, aborts exit 2 on mismatch, then runs
  act-now). The clone2-watch hold guard waits out holds before
  each send. Brave was relaunched P3-style with
  `--remote-debugging-port=9223` before run 1, rolled back
  after run 2.
- Results (run JSONs ~/workspace/c5-step8-run/smoke-run1.json,
  smoke-run2.json):
  - Run 1 clone1: wall 22.6s, origin [3448, 942], screen
    [3734.5, 2045], image [635.2, 571.5], pre-count 0 (items
    40), V12 found, delayed count 1, broker_sequences [1],
    retries 0, finish finished. Ground rect {x 141, y 1091,
    w 291, h 24, cx 286.5, cy 1103}, inner 901x1148, dpr 1,
    window at [3448, 914] size [901, 1176] pid 1183366.
  - Run 1 clone2: wall 22.7s, origin [2533, 942], screen
    [2819.5, 2045], image [177.8, 571.5], pre-count 0 (items
    40), V12 found, delayed count 1, broker_sequences [1],
    retries 0, finish finished. Window at [2533, 914] size
    [901, 1176] pid 8059.
  - Run 2 clone1: wall 23.0s, same grounding, pre-count 0
    (items 43), V12 found, delayed count 1, broker_sequences
    [1], retries 0, finish finished.
  - Run 2 clone2: wall 22.9s, same grounding, pre-count 0
    (items 43), V12 found, delayed count 1, broker_sequences
    [1], retries 0, finish finished.
  - Messages sent: C5-STEP8-SMOKE-R1-CLONE1,
    C5-STEP8-SMOKE-R1-CLONE2, C5-STEP8-SMOKE-R2-CLONE1,
    C5-STEP8-SMOKE-R2-CLONE2.
  - Observation region for the screen captures: [2464, 902,
    1920, 1200], image [960, 600] (the eDP-2 monitor area in
    virtual coordinates, NOT [0,0,1920,1200]; the image-point
    math reads region/image_size from the meta, so it is
    correct).
- P9 review (F2 hard condition): run-2 screenshots reviewed
  visually. Clone1 (Brave): bubbles
  C5-STEP8-SMOKE-R1-CLONE1 (2:50 PM) and
  C5-STEP8-SMOKE-R2-CLONE1 (2:51 PM) rendered as user bubbles,
  with the "You've reached your usage limit" system cards
  between them. Clone2 (Chromium): bubbles
  C5-STEP8-SMOKE-R1-CLONE2 and C5-STEP8-SMOKE-R2-CLONE2
  rendered as user bubbles, same usage-limit cards. No
  DOM-vs-render mismatch. Files on the VM:
  ~/workspace/c5-step8-run/review-run2-clone1-scp.jpg,
  review-run2-clone2-scp.jpg (fetched via scp over the mux;
  the manual base64 chunk reassembly corrupted the first copy,
  scp is the reliable path). Laptop originals:
  ~/c5-step8-run/smoke-run*-p9-decoded.png,
  smoke-run*-p9.jpg, review-run2-*.jpg.
- Smoke script bugs found and fixed during the work:
  send-act.sh quoting bug (the focus dispatch built
  `"address:0x...})` with a missing closing quote, causing a
  Lua "unfinished string near <eof>" error; the script had
  `set -u` but no `set -e`, so the failed focus was silently
  ignored when the target was already active; fixed to
  `hyprctl dispatch "hl.dsp.focus({ window =
  \"address:$ADDR\"})"` with `set -eu`); envelope parser bug
  (matched `returncode`, which the act-now stdout envelope does
  not carry; now matches `method == 'act-now'` and checks
  `ok`); P9 save bug (s2-p9.mjs prints base64 to stdout, so
  the .png files held base64 text; decode with
  base64.b64decode first, via laptop script
  ~/c5-step8-run/decode-p9.py); downscale quoting bug (nested
  double quotes broke the inline python -c; use a script file
  instead).
- WINDOW MAP CHANGE from the smoke (recorded 14:53:13 +07):
  the Brave relaunch moved Brave from ws1 to ws2. Current: Zen
  ws1 [2509, 914] [1863, 1176] (full width); Chrome ws2 [2533,
  914] [901, 1176]; Brave ws2 [3448, 914] [901, 1176]. Chrome
  also resized 1853 wide to 901 wide during smoke run 1 (cause
  not established; per-send fresh grounding made it harmless).
  Flag this layout change to the coordinator; do not move
  windows back unprompted.
- Brave was relaunched twice with the debug flag and rolled
  back twice without it (P3 procedure, S2-REOPEN precedent);
  CDP verified up after each flagged launch and closed after
  each rollback.
- Clone1 activity check before the Brave relaunch (14:33 +07):
  clone1 batch 13 task 3 done, no new Muse request as of the
  14:28 watchdog note; last clone1 commit 14:26 +07. Safe to
  relaunch.

### 6.2 Fallback drill: PASSED on the second attempt (15:07:26-15:08:15 +07)

- Script: ~/workspace/c5-step8-run/fallback-drill.py. Plan:
  stop the relay, verify the broker is down, send one test
  message C5-STEP8-FALLBACK-R1-CLONE2 in the clone2 thread via
  the fresh-SSH one-shot path (`cu.py session -- python3 cu.py
  session-driver` with two JSONL lines on stdin: the act
  envelope then `{"args": ["finish"]}`), gate with V12 +
  delayed count, restart the relay, verify status (loaded hash,
  state idle), and verify the broker path works again (start +
  status + finish cycle, expecting running/ready). Uses FRESH
  SSH (~/workspace/ssh-laptop.sh) throughout.
- FIRST ATTEMPT FAILED (15:04:15-15:04:34 +07), correctly and
  safely. Relay stopped (STOPPED), broker confirmed down
  (broker_unavailable, RC 1). Ground rect {x 141, y 1091, w
  291, h 24, cx 286.5, cy 1103}, origin [2533, 942], screen
  [2819.5, 2045], pre-count 0 (items 45), image point [177.8,
  571.5], obs /home/james/.cache/agent-computer-use/167f25514e55.json.
  One-shot rc 0, driver ready, but the act returned returncode
  1, error `screen changed`, error_code `screen_changed`,
  preflight_ms 361.862, input_sent False, session_continues
  True, driver finished. The drill raised RuntimeError and
  stopped before the restart step, leaving the relay stopped.
  ROOT CAUSE (proven by comparing the two captures): the given
  observation showed the ZEN Welcome page (ws1), while the
  after-capture showed ws2 (Chrome clone2 + Brave clone1 side
  by side). At observe time the active workspace was ws1 (the
  clone2-watch hold had returned the active workspace to ws1
  after the smoke); the focus inside the one-shot call then
  switched to ws2, so the act preflight correctly refused a
  stale-workspace observation. The ordering observe-then-focus
  is wrong when the workspace is not already the target's; the
  smoke only passed because both browsers were already on the
  active workspace. LESSON: focus FIRST, then observe, then
  act. No message was sent (input_sent False), so the retry
  carries no duplicate risk. Files on the VM:
  ~/workspace/c5-step8-run/drill-given.jpg (Zen Welcome, ws1),
  drill-after.jpg (ws2, both browsers).
- RELAY RESTARTED MANUALLY between attempts (15:07:07 +07):
  new PID 1195590, active, state idle, owner None, loaded
  d490f369f6b7 matching the current session_remote.py.
- DRILL FIX: focus the target window and verify the active
  window BEFORE the ground/observe step (added to
  fallback-drill.py with the focus rule's hl.dsp form and an
  activewindow check that aborts on mismatch).
- SECOND ATTEMPT PASSED (15:07:26-15:08:15 +07). Relay
  stopped 15:07:29 (STOPPED), broker confirmed down 15:07:34
  (broker_unavailable). Focus rc 0, active 0x5570538ed160
  (Chrome). Ground rect as above, origin [2533, 942],
  pre-count 0 (items 45), image point [177.8, 571.5], obs
  /home/james/.cache/agent-computer-use/76f9163771ae.json.
  One-shot rc 0, driver ready, act returncode 0, completed 3
  (click + type + Return), preflight_ms 111.016,
  execution_ms 222.042, input_sent True, type_verified True
  (input-line-band, necessary not sufficient; the DOM check is
  the sufficient one). V12 found True, role user, side user,
  textLen 31, attempts 1. Delayed count 1 (items 47). Relay
  restarted 15:08:05, new PID 1196429, active. Broker status
  after restart: state idle, owner None, loaded d490f369f6b7,
  head 1b5a6e6. Broker start/finish cycle 15:08:08-15:08:15:
  start ok (generation 4716e03767646201e27e8ee7c1117859, owner
  c5-step8-drill) -> running/ready -> finished, guardian clean,
  error null. Drill JSON:
  ~/workspace/c5-step8-run/fallback-drill.json.
  CONCLUSION: the one-shot SSH path recovers a run with the
  broker dead, and the broker restarts cleanly afterwards.
  Spec gate item 5 (one real relay restart) is covered by this
  drill, plus the 14:27 sync restart and the 15:07:07 manual
  restart.

## 7. Master watchdog + soak status (condition 3 of 5)

- Operative watchdog (IN PLACE): per-use liveness check plus
  restart-on-death in scripts/ssh_mux.py (ensure_master runs
  `-O check` before use and restarts a dead master; deaths
  and restarts go to the JSONL log), plus ControlMaster=auto
  on clients so a master death self-heals with one slow
  correct fallback instead of a hard failure, plus the
  per-socket watchdog() single-shot check in ssh_mux.py.
  ServerAliveInterval=15 is set on the mux wrapper
  (scripts/ssh-laptop-mux.sh). The relay itself has NO
  auto-restart: the service file sets Restart=no, so a dead
  broker stays dead until the one-shot SSH restart (section
  6). That is the documented recovery, not a watchdog gap
  being hidden.
- NOT in place: no cron-installed watchdog on the VM
  (crontab binary not found; nothing calls ssh_mux.py
  watchdog on a schedule). No standing soak process.
- Soak (ADVISORY-ONLY, stated plainly): the 1-day soak
  never ran. The 60-minute keepalive soak reached 40
  minutes confirmed, then a VM restart cut it short
  (PROBE-S0 log section 10, verdict 07:52 +07). Per the
  final direction S0 row, the soak runs in parallel and is
  advisory, not a gate (a master death falls back to fresh
  SSH, slow but correct). This step does not claim a soak
  that did not happen. The live evidence that the channel
  works is the per-use liveness path exercised by every
  broker call in this log (each broker round trip runs over
  the mux master, restarted on death by ControlMaster=auto
  when needed).
- Current master state at 13:55 +07: DEAD (ssh_mux.py check:
  alive false, check_rc 255, pid null). The VM-side broker
  calls in this task use scripts/ssh-laptop-mux.sh, whose
  ControlMaster=auto creates a fresh master on first use;
  the first call after a death pays one slow fresh connect
  and then mux resumes. Recorded, not hidden.
- 14:02 +07, T+15m: fatal-on-read-failure decision (section 3)
  and queue discipline (section 4) written, before any
  deletion.
- 14:15 +07, T+28m: browser-observe probe through the broker
  (80 elements, composer e61 role textarea name Message);
  B8c2 endpoint fix verified live.
- 14:27 +07, T+40m: laptop fast-forwarded to 8c6553a (step-8
  deletion + tests + log sections 0-4, 7, 8 committed and
  pushed); sync-installed.py ran; relay restarted by the sync
  (new PID 1167236, loaded hash d490f369 matching, head
  8c6553a). Commit 8c6553a verified via git ls-remote.
- 14:30:39-14:31:13 +07, T+43m: concurrency test PASSED (run
  c5-step8-conc-073039; A held 12s, B waited, started 3.405s
  after A finished, wall 22.120s, no interleaving).
- 14:31 +07, T+44m: full suite 2192 tests, 0 failures, 1
  pre-existing environment error (g++ C++26).
- 14:33:57-14:44:27 +07, T+46-57m: three act-now attempts
  failed identically (driver_not_ready, session_attempt_ms
  about 255ms); shader-warmup hypothesis tested and refuted
  (manual driver launch 14:45:25 rc 0).
- 14:48 +07, T+61m: laptop fast-forwarded to 1b5a6e6
  (ready-wait fix + 2 tests), pushed, verified via ls-remote;
  sync-installed.py ran (first_action.py 1270139f957b...);
  relay NOT restarted (only first_action.py changed).
  Click-only probe PASSED 14:48:36 (session_attempt_ms
  1680.6) and 14:50:03 (1651.8).
- 14:50:14-14:51:56 +07, T+63-64m: live smoke PASSED, 2 runs,
  4 sends, walls 22.6-23.0s, broker_sequences [1], retries 0,
  V12 + delayed count 1 on every send. P9 review done (section
  6.1).
- 14:53:13 +07, T+66m: window map change recorded (Brave ws1
  to ws2; Chrome resized 1853 to 901 wide; Zen full width ws1).
- 15:04:15-15:04:34 +07, T+77m: fallback drill first attempt
  FAILED safely (screen_changed, input_sent False); relay left
  stopped. Root cause proven by comparing the given and after
  captures (ws1 Zen vs ws2 browsers); drill fixed to focus
  first, then observe.
- 15:07:07 +07, T+80m: relay restarted manually (PID 1195590,
  idle, hash d490f369f6b7).
- 15:07:26-15:08:15 +07, T+80-81m: fallback drill second
  attempt PASSED. One-shot recovered the send (V12, delayed
  count 1); relay restarted (PID 1196429); broker start/finish
  cycle clean.
- 15:10 +07, T+83m: log sections 5 and 6 finished; log
  committed (see section 6.2 end for the commit).

## 8. Session-level pill: BLOCKED on the CB-10 precondition

- The pill half of step 8 is EXCLUDED from this task by the
  brief, and it stays excluded. Status verified against the
  spec section 7: the LIQUID flicker probe has not run (no
  log in the repo records a plugin load, a flicker
  reproduction, or a repaint count), and no explicit owner
  deferral is recorded anywhere in the repo. Both limbs are
  still missing, exactly as the spec left them.
- Consequence: no session-level pill change is made here,
  the overlay server is NOT touched, and act-now keeps its
  per-batch overlay acquire. Step 8 is therefore complete
  for its transport half (the per-batch spawn deletion)
  and BLOCKED for its pill half until one CB-10 limb lands.
  This is recorded here so the step is not quoted as fully
  done.
- The CB-10 eval limb (remove unrestricted zen_dom eval) is
  a separate item and is not a precondition of step 8; it is
  not touched here either.

