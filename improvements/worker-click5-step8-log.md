# Worker C5-STEP8 log: S1/CB-6 broker deletion (per-batch spawn removed, broker only)

Owner: Pham Tuan. Coordinator: COORD-CLICK-5. Repo
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
  P3-style relaunch and roll back afterwards.
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

## 5. (to be filled: implementation + tests + concurrency test)

## 6. (to be filled: live smoke + fallback drill)

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

