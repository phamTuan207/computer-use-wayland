# Worker B2-4 log (step 10): A5 migrate, A3 holder fix, A3 wedge drill, A4 CB-10 probe

Owner: the owner. Coordinator: parent orchestrator.
Repo ~/workspace/mochi-b2-4-work, base code ed4fcd4 for the
fix round (section 10); the original work in sections 0-9
was measured at detached HEAD 0400e86 (origin todolist-push,
latest at 00:08 23/11/2026), which was the HEAD when that
work was done. Redone from scratch:
the old worktree was gone, nothing was recoverable. NO commit, NO
push, NO live run, NO file deleted in this task. No em dash or en
dash anywhere in this file. No personal info. Every claim below
carries command, output, commit hash, and time in Asia/Ho_Chi_Minh
plus elapsed, per the Lauren Tan standard. Numbers were
re-measured in this task, not copied from other reports without
checking.

## 0. Task and sources

- Task received 00:09:47 +07, Mon 2026-11-23 (T+0m). Worktree
  HEAD 0400e869d4275fe58286412f8acde1824b1e3623 at start, verified
  00:09:53 +07 with `git rev-parse HEAD`.
- Docs read before work (in the worktree):
  improvements/worker-click5-step10-prep-log.md (prep, commit
  ccb2473, 873 lines); improvements/worker-click5-coord-log.md
  section 49 (decision 6: step 10 UNBLOCKED in principle, but
  proof-tied dates still govern, and the deletion date still
  depends on evidence; no deletions during the pause);
  docs/zen-error-fix-todolist-20261121.md (gate G-PILL, section
  4.29 pill rule); improvements/worker-click3-final-direction-log.md
  (section 3 step 10, section 5 B3/B4/B6, section 7 CB-10).
- Task parts: (a) A5 gate 2 migrate the S2 flip class send to
  the broker client; (b) A3 gate 5 fix the holder list to 5 and
  re-measure all coordinates; (c) A3 B6 prepare the wedge drill;
  (d) A4 CB-10 prepare the flicker probe or the deferral path.
  Parts (a) code and (b) docs are DONE in the worktree,
  uncommitted. The drills and the probe are PREPARED ONLY and
  need a GO from Muse tong before any live step runs.

## 1. Time log

- 00:09:47 +07, T+0m: task received. Worktree HEAD 0400e86.
- 00:09:53 +07, T+0m: verified HEAD and clean status (only the
  worktree files; git status showed no modifications yet).
  Read the prep log in full (873 lines).
- 00:10-00:11 +07, T+1m: read coord log section 49, final
  direction step 10/B3/B4/CB-10 rows, zen doc G-PILL and 4.29.
  Read scripts/s2_flip_live.py (1073 lines) and
  scripts/session_remote.py client functions (lines 1449-1681).
- 00:11 +07, T+2m: key design finding, verified from source.
  The broker envelope already allows code-exec
  (session_remote.py COMMANDS includes code-exec, line 42;
  _validate_envelope lines 352-378 accepts args[0] in COMMANDS
  plus stdin; session_driver.py relay_commands line 164
  allows code-exec and unwraps the result the same way the
  one-shot did). So the migrate needs no broker change. The
  flag precondition: the driver runs code-exec only when the
  relay env carries CU_CODE_EXEC=1 (cu.py line 3123,
  code_exec.py line 181; driver inherits the relay env, not
  the caller shell). The relay drop-in flags.conf carries the
  flag (coord-click-6 F3). The old header claim that the relay
  started without the flag is stale; the migrate records the
  flag as a precondition instead of working around it.
- 00:11 +07, T+2m: structural finding. The sends ran AFTER
  broker_finish in run(), outside the broker session. A broker
  send must run INSIDE the session, so run() was restructured
  (section 2).
- 00:12:39 +07, T+3m: migrate code written; py_compile passed
  (section 2).
- 00:13:06 +07, T+4m: s2 flip tests 46 OK (section 2).
- 00:13:20 +07, T+4m: baseline HEAD pristine copy 38 OK
  (section 2).
- 00:14:15 +07, T+5m: session_remote plus code_exec suites 163
  OK in 51.2s (section 2).
- 00:15:21 +07, T+6m: holder fix applied to the prep log;
  full coordinate re-measurement done (section 3).
- 00:16:00 +07, T+7m: A5 fallback drill procedure written
  (section 5).
- 00:17:00 +07, T+8m: A3 wedge drill procedure written
  (section 4). Dash check clean, diff stat recorded.
- 00:18:00 +07, T+9m: A4 CB-10 probe procedure written
  (section 6).
- 00:18 +07, T+9m: this log written, final re-run 46 OK at
  00:17:53 +07. No step was stuck more than 15 minutes; no live
  action was taken at any point.

## 2. (a) A5 gate 2: migrate the S2 flip send to the broker client

### 2.1 Design (decided from source, not assumed)

- New method broker_code_exec(lease, seq, endpoint, program,
  intent): one broker request with args ['code-exec',
  '--endpoint', endpoint, '--program', '-', '--intent', intent]
  and the program as stdin, plus one result fetch, reusing the
  existing self.broker() and self.driver_result(). Returns
  (wall_ms, envelope, next_seq). The envelope shape is the
  same as the one-shot's (ok, api_calls, elapsed_ms, error,
  error_type, log), because the driver unwraps it the same way.
- New method _code_exec_send(lease, seq, endpoint, program,
  intent): the single send dispatch. Default transport broker
  with a lease; one-shot when transport is forced to oneshot,
  or when no lease exists (legacy callers and unit tests).
- Fallback rule, the safety core: automatic one-shot fallback
  runs ONLY on a pre-dispatch broker refusal
  (_BrokerSendNotAccepted: the request call failed or the
  broker answered with something other than accepted, so the
  driver never saw the program). A broker result failure
  leaves the outcome unknown, so no fallback runs there. A
  disabled envelope (relay lacks CU_CODE_EXEC=1) also raises
  with no fallback: the flag is a relay precondition, and
  silently routing around it would hide it; the error message
  names the recovery path (--transport oneshot).
- run() restructured: sends now run INSIDE the broker session
  (routing, then sends, then broker_finish in finally), with
  the sequence threaded across browsers through
  broker_next_seq on the send result dict. The pill hold,
  the CB-2 pre-send count check, the V12 verify, and the
  delayed recount are unchanged.
- oneshot_code_exec is KEPT, untouched in behavior, and its
  docstring now says FALLBACK AND RECOVERY PATH. Nothing was
  deleted. CLI gains --transport broker/oneshot (default
  broker). Run JSON gains a transport field; each send's
  program dict gains a transport field (broker,
  broker-fallback-oneshot, or oneshot), so the log always
  shows which path carried the send.

### 2.2 Evidence (non-live checks only)

- Command: `python3 -m py_compile scripts/s2_flip_live.py`.
  Output: COMPILE-OK. Time: 2026-11-23 00:12:39 +07, elapsed
  0.070s. HEAD: 0400e869d4275fe58286412f8acde1824b1e3623.
- Command: `python3 -m unittest tests.test_s2_flip_wiring
  tests.test_s2_flip_pill`. Output: Ran 46 tests in 0.332s,
  OK. Time: 2026-11-23 00:13:06 +07, elapsed 0.607s. HEAD:
  0400e869d4275fe58286412f8acde1824b1e3623. The 46 are 40
  wiring tests (32 at HEAD plus 8 new BrokerCodeExecTests)
  plus 6 pill tests. The 8 new tests: broker envelope shape
  and sequence advance; broker default with a lease; pre-
  dispatch refusal falls back to one-shot exactly once;
  result failure never falls back; disabled envelope never
  falls back; oneshot transport forces one-shot with a lease;
  invalid transport raises; CLI maps --transport.
- Baseline check (proves no regression): pristine HEAD copy
  in /tmp/b24-baseline via `git archive HEAD`, same command.
  Output: Ran 38 tests in 0.342s, OK. Time: 2026-11-23
  00:13:20 +07, elapsed 0.573s. HEAD: same 0400e86. So 38 old
  tests pass before and after; 8 new tests pass after.
- Command: `python3 -m unittest tests.test_session_remote
  tests.test_code_exec`. Output: Ran 163 tests in 51.201s,
  OK. Time: 2026-11-23 00:14:15 +07, elapsed 51.425s. HEAD:
  0400e869d4275fe58286412f8acde1824b1e3623. (pytest is not
  installed in this VM, so unittest was used; the prep and
  step 9 logs cite pytest, but the same suites run under
  unittest here.)
- Diff stat at 00:17:00 +07: scripts/s2_flip_live.py 245
  lines changed, tests/test_s2_flip_wiring.py 196 lines
  changed. HEAD: 0400e869d4275fe58286412f8acde1824b1e3623.
  Files are modified in the worktree, NOT committed.

### 2.3 What is NOT proven by the checks above

- No live broker send ran (live runs need a GO). The A5 gate
  item 2 proof (the s2_flip_live harness runs its send set
  through the broker client on live tasks, same
  postconditions, no oneshot_code_exec call in the run) is
  still open. The fallback drill that re-proves the recovery
  path on the post-migration code is prepared (section 5) and
  also needs a GO. The migrate is code-complete and
  unit-proven only.

## 3. (b) A3 gate 5: holder list 4 becomes 5, all coordinates re-measured

### 3.1 The fix

The fifth holder is scripts/sync-installed.py line 115: lock =
session.owner_lock() inside _session_lock, used at line 1259.
It was missed because sync-installed.py loads cursor_session
dynamically with importlib (lines 103-106), so a grep for
`import cursor_session` never finds it. The five, re-measured
at HEAD 0400e86 with grep (command output saved to
/tmp/b24-coords.txt during the task):

- scripts/activate-cursor-guard.py line 63
- scripts/activate-session-backend.py line 72
- scripts/setup.py line 314
- scripts/visuals.py line 242
- scripts/sync-installed.py line 115 (importlib load, _session_lock)

NOT counted: the three owner_lock() calls inside
cursor_session.py itself (lines 104, 125, 142). They are
tree-internal and die with the tree. A future grep that finds
eight call sites has found five external holders plus three
internal ones, not eight holders.

### 3.2 Where the list lived, and what changed

Searched with `grep -rn "four.*holder|holder.*four|4 direct|
4 holder"` across docs, improvements, and scripts. Exactly
two places recorded 4 holders, both in
improvements/worker-click5-step10-prep-log.md: section 3.2
(the holder bullet, "four call sites") and section 3.3 item 5
("The four direct owner_lock holders"). Both now say five.
No other file in the repo records 4 holders (the remaining
"four" hits are unrelated: "same four verification steps"
in the A3 rollback, which is four rollback steps, not
holders, and is correct as-is). Time of the fix: 2026-11-23
00:15:21 +07. HEAD: 0400e869d4275fe58286412f8acde1824b1e3623.

### 3.3 Full coordinate re-measurement at HEAD 0400e86

Command: one grep sweep over cursor_session.py, overlay.py,
s2_flip_live.py, session_remote.py, ssh_mux.py,
cancel_hotkey.py, cu.py, first_action.py, session_cleanup.py.
Output: saved to /tmp/b24-coords.txt (ephemeral scratch).
HEAD: 0400e869d4275fe58286412f8acde1824b1e3623. Time:
2026-11-23 00:15 +07. The table below is the re-measured
result (old prep value first, new value second; UNCHANGED
means the prep value still holds):

- cursor_session.py, 344 lines, UNCHANGED: prepare 22,
  request_stop 27, restore 39, owner_lock 73, drain_input 87,
  SessionVisuals 93, recover 103, stop 120, guardian 136,
  stop_group 208, terminate_driver 220, supervise 228.
- session_remote.py _launch: prep 522, NOW 520. Fixed in
  prep log sections 3.1, 3.2, 3.3 item 4. Client functions
  UNCHANGED: _client_start 1456, _client_start_with_wait 1494,
  _client_finish 1563, start subcommand 1591, request
  subcommand 1599. File is 1681 lines.
- cu.py stop_session_on_error request_stop: prep 3458-3459,
  NOW 3460. Fixed in prep log section 3.2. Other call sites
  UNCHANGED: stop 3105, supervise 3109, recover 3110,
  request_stop 3114.
- cancel_hotkey.py UNCHANGED: latch_present 59, latch 120,
  cancellation_status 157, cancellation_message 197, resume
  unlink 222, request_stop call 220.
- first_action.py overlay gate UNCHANGED: acquire_overlay 116,
  overlay_visible 150, release_overlay 167, import overlay 978.
- session_cleanup.py UNCHANGED: guardian doc lines 5-6,
  holder check lines 62-69.
- overlay.py DRIFTED HARD: prep 613 lines, NOW 693 lines.
  _log 48, _label_for 62, _prepare 71, _holders_lock 77,
  load_holders 88, save_holders 96, _holder_key 104, add_holder
  113, remove_holder 129, prune_dead_holders 157, session_live
  177, session_label 194, wayland_env 202, Daemon 238 (prep
  217), _spawn_native 245, _close_native 251, _ensure_native
  260, _show_label 285, apply_holders 309, status_reply 349,
  _monitor 361, serve 377 (prep 344), _daemon_running 463,
  _send_socket 475, _ensure_daemon 489 (prep 458), cmd_acquire
  525 (prep 494), cmd_release 570, cmd_status 587, cmd_stop 608,
  cmd_daemon 625, hold 631, main 659. Any A4 worker must use
  these numbers, not the prep log section 4 numbers.
- ssh_mux.py UNCHANGED: run 303, fresh-fallback contract
  docstring 42-47, via values 309-310, 320, 337. File is 403
  lines.
- s2_flip_live.py at HEAD 0400e86 (BEFORE this migrate):
  oneshot_code_exec 388, call site in _send_browser_inner 794
  (prep said 292-322 and 531). AFTER this migrate in the
  worktree (uncommitted): broker_code_exec 423,
  _code_exec_send 467, oneshot_code_exec 506, send call site
  928. File is 1230 lines after the migrate.
- Prep log section 8 was left untouched: it is the prep
  task's evidence record at HEAD 5a8c29d, and it stays true as
  a record of that moment. The corrections live in the design
  sections (3.1, 3.2, 3.3) and in the appended prep log
  section 9, which carries this same table.

## 4. (c) A3 B6: wedge drill prepared, NOT run

File: improvements/mochi-b2-4-a3-wedge-drill.md (written
00:17:00 +07, HEAD 0400e869d4275fe58286412f8acde1824b1e3623).
Status: PREPARED ONLY, needs an explicit GO from Muse tong.
Why not run: it is a live drill (SIGSTOP the live driver,
cancel latch, kill the driver group, relay restart, retry a
destructive action). It needs a live session, a scratch
target, and the owner's GO. The step 9 log section 12
records the same gap (no dedicated wedge drill in step 9),
so this file closes the preparation gap, not the proof gap.

Contents: preconditions (scratch target, no live owner
session, pill held, one recovery worker only); 8 steps
(start and record the three holdings, wedge with SIGSTOP on
the driver PID only, observe the frozen status, set the
cancel latch, SIGCONT then finish with the owner's lease
then SIGTERM/SIGKILL by PID only, verify no orphaned group
and the lock free, recover with relay restart plus
session_cleanup.py --check exit 0, retry with a NEW message
on a NEW lease); pass criteria (lock refusal live, latch
visible, no orphaned group, clean recovery, delayed count
exactly 1, old batch abandoned never replayed); abort rules
(no lock refusal means stop at once, never kill by pattern,
M1 count 2 or more means stop and preserve evidence).
Sources: step 8 log section 4 (recovery order, 300s wedge
threshold, killer is the recovery worker) and section 6.2,
session_remote.py _task_recovery_required line 933,
IDLE_TIMEOUT 300.0 and REQUEST_TIMEOUT 120.0 (lines 38, 40).
The drill states plainly that it proves recovery against
the CURRENT tree, not the driver-held A3 design (which does
not exist yet).

## 5. (a) Fallback drill prepared, NOT run

File: improvements/mochi-b2-4-a5-fallback-drill.md (written
00:16:00 +07, HEAD 0400e869d4275fe58286412f8acde1824b1e3623).
Status: PREPARED ONLY, needs an explicit GO from Muse tong.
Why not run: it stops and restarts the live relay and sends
live (scratch-target) messages. It repeats the step 8
fallback drill (step 8 log section 6.2, passed on the second
attempt) on the post-migration code: baseline broker send
(run 900, transport broker), relay stop, one-shot fallback
send (run 901, --transport oneshot, new message), relay
restart with a new generation, broker batch on a fresh lease
(run 902), session_cleanup.py --check exit 0. Abort rules:
disabled envelope stops the drill (no automatic fallback),
unknown outcome never retries the same message, relay not
coming back stops all live work. This drill is the A5 gate
item 3 proof; the migrate in section 2 is its precondition.

## 6. (d) A4 CB-10: flicker probe prepared, stage (a) BLOCKED

File: improvements/mochi-b2-4-a4-cb10-probe.md (written
00:18:00 +07, HEAD 0400e869d4275fe58286412f8acde1824b1e3623).
Status: PREPARED ONLY, needs an explicit GO from Muse tong,
and the choice between probe and deferral belongs to the
owner, not to this worker. No conclusion is drawn here.

Current status, from the repo: probe NOT run (the LIQUID
background test never ran because the plugin was not
loaded); no deferral recorded; stage (a) of A4 is therefore
BLOCKED. What exists: indicator proven NOT to repaint at
idle three times (122 one-second windows 0 callbacks, 3
minutes 0 commits, deployed binary 3 windows 0; E1 per-event
logging ready); the owner chose option C (nested Hyprland)
on 18:24 (decision doc
docs/decision-2-2-3-hyprglass-test-20261121.md); Y6e nested
LOAD TEST PASSED 21:57 (915121d), which proves the plugin
loads nested, NOT that the flicker reproduces, and counted
no repaints; hyprglass is NOT loaded live (only hyprbars),
NOT in hyprland.conf, .so only in backups.

What unlocks stage (a), exactly one of: (1) probe verdict
from the nested venue (flicker reproduces with per-phase
repaint counts, or does not reproduce and CB-10 dissolves);
or (2) an owner deferral recorded with name, date, scope,
and reopen condition. Until one limb lands, stage (a) stays
BLOCKED, stage (b) cannot start, and the A4 date cannot be
set.

## 7. Files changed (worktree, uncommitted)

Command: `git status --short` and `git diff --stat`. Output
at 00:17:00 +07, HEAD 0400e869d4275fe58286412f8acde1824b1e3623:

- M improvements/worker-click5-step10-prep-log.md (118 lines
  changed: holder fix plus section 9)
- M scripts/s2_flip_live.py (245 lines changed: migrate)
- M tests/test_s2_flip_wiring.py (196 lines changed: 8 new
  tests)
- ?? improvements/mochi-b2-4-a5-fallback-drill.md (new)
- ?? improvements/mochi-b2-4-a3-wedge-drill.md (new)
- ?? improvements/mochi-b2-4-a4-cb10-probe.md (new)
- ?? improvements/mochi-b2-4-worker-log.md (new, this file)

No file was deleted. No commit was made. No push was made.
No live run, no browser work, no SSH was done in this task.

## 8. Parts prepared only, awaiting GO, and why

- A5 fallback drill (section 5): needs GO because it stops
  and restarts the live relay and sends live messages. It is
  the A5 gate item 3 proof.
- A3 wedge drill (section 4): needs GO because it wedges,
  cancels, and kills a live session and retries a
  destructive action. It is the B6 lift limb step 9 left
  open.
- A4 CB-10 probe (section 6): needs GO because it runs a
  nested compositor with the plugin and drives the pill, and
  the probe-versus-deferral choice belongs to the owner.
  Stage (a) stays BLOCKED until one limb lands.
- The live broker-send proof for the migrate (A5 gate item
  2): needs GO because it sends on live clone chats. The
  code is ready; the proof is not claimed.

## 9. Leftovers and open items

- The A5 gate item 2 live proof and the fallback drill both
  need a GO and a synced laptop tree (the drill is
  meaningless on a stale laptop tree).
- The A3 gate still needs the driver-held design (step 9
  prototype) and a live run proving the driver holds scope
  plus cancel latch plus lock on the rewired path. The wedge
  drill proves recovery on the current tree only.
- The A4 stage (a) decision (probe GO or owner deferral) is
  with the owner and the coordinator, not with this worker.
- The prep log section 4 (A4) and section 5 (A5) coordinate
  numbers were the prep values in place when this log was
  first written; the fix round (section 10 below) corrects
  them in place and adds a pointer to section 9. A future
  A4 or A5 worker must use the section 9 table, not the
  in-place section 4 or 5 numbers.
- Baseline evidence copy /tmp/b24-baseline was a pristine
  HEAD checkout made only to run the 38-test baseline; it is
  scratch, not a deliverable.

## 10. Fix round (fix worker B2-4, 2026-11-23): all findings of 4 reviews

Base code for this round: ed4fcd4 (the worktree HEAD at fix
time; the original work in sections 0-9 was measured at
0400e86, which was the HEAD at 00:09 23/11/2026, and every
coordinate was re-measured at ed4fcd4 by councils 1-3 and the
redteam with no value changed, because no cited file changed
between the two). This section records the fix round only.
No live run, no push, no file deleted in this round.

### 10.0 Evidence contract (written BEFORE any fix check ran)

Every check below was stated here first. A check with no
contract line here does not count. Each claim needs command,
output, commit hash, and time in Asia/Ho_Chi_Minh plus
elapsed. The fix commit hash is recorded in the fix report to
the coordinator (a commit cannot contain its own hash); until
the commit, the hash is the worktree base ed4fcd4 plus the
uncommitted fix diff, stated as such.

- F-C1, compile: `python3 -m py_compile
  scripts/s2_flip_live.py tests/test_s2_flip_wiring.py` in
  the worktree. Expected: exit 0, no output.
- F-C2, wiring plus pill suite: `python3 -m unittest
  tests.test_s2_flip_wiring tests.test_s2_flip_pill`.
  Expected: Ran 60 tests, OK (54 wiring: 40 old plus 14 new,
  plus 6 pill). If the count differs, record the exact count
  and the new test names.
- F-C3, baseline: pristine HEAD copy via `git archive HEAD`
  to a scratch dir, same command as F-C2. Expected: Ran 38
  tests, OK (32 wiring plus 6 pill). Proves the delta is
  exactly the 14 new tests.
- F-C4, neighbour suites: `python3 -m unittest
  tests.test_session_remote tests.test_code_exec`. Expected:
  Ran 163 tests, OK.
- F-C5, revert mutations on a /tmp copy only (never the
  worktree), one per new-test group, each must flip its
  target test to FAIL while the other new tests pass:
  M-F1 restore the except handler to `broker_next_seq = seq`,
  target test_two_browser_disabled_then_broker_seq_advances.
  M-F2 skip the result probe (fall back on any
  _BrokerSendNotAccepted), target
  test_probe_record_found_refuses_fallback. M-F3 treat a
  replay completed status as not accepted, target
  test_real_broker_replay_completed_accepted. M-F4 return the
  envelope for result status running and failed, targets
  test_result_running_raises_with_next_seq and
  test_result_failed_raises_with_next_seq. M-F5 drop the
  unknown-status raise, target
  test_result_unknown_raises_with_next_seq. M-F6 drop the
  recount before fallback, target
  test_recount_refuses_fallback_when_message_present. M-F7
  drop the accepted-status check in broker(), target
  test_real_broker_rejects_unknown_request_status. M-F8 add
  --bogus-flag to the real broker request command, target
  test_real_broker_request_command_shape. A mutation that
  leaves its target green means that test is hollow.
- F-C6, doc checks by grep, no run needed: no em dash or en
  dash in any of the 7 B2-4 files; HEAD label ed4fcd4 in the
  3 drills, prep log section 9, and this log header; the
  importlib range reads 103-106 in the worker log 3.1 and
  prep log 3.2 and 9.1; prep log section 4 overlay numbers
  match section 9 (Daemon 238, serve 377, _ensure_daemon
  489, cmd_acquire 525, 693 lines).
- F-C7, A3 drill citations by grep at ed4fcd4:
  session_remote.py _status 871, _result 847, _request 790,
  _client_finish 1563, _fail_task 926,
  _task_recovery_required 933. Expected: every line matches
  the drill.

### 10.1 Findings fixed (to be filled with evidence in 10.8)

- Code, scripts/s2_flip_live.py: (1) post-accept failures
  return next_seq seq plus 1, two-browser test with a broker
  mock modelling accept-time consumption; (2) result probe
  before fallback, fallback only on not_found (or a
  broker-generated refusal the probe confirms with
  not_found); broker_unavailable alone is NOT proof, because
  _exchange maps any socket OSError, including a recv
  failure after transmit, to broker_unavailable; (3) replay
  completed accepted; (4) running and failed result statuses
  raise with next_seq seq plus 1; (5) recount before fallback
  for both variants, fill included; (6) duplicate
  program_variant validation removed; (7) header docstring
  names the CLI subcommands only.
- Tests, tests/test_s2_flip_wiring.py: (8) 14 new tests for
  the real broker path and status handling, each with a
  revert mutation in F-C5.
- Docs: (9) HEAD ed4fcd4 in 3 drills, prep log section 9,
  this log; (10) prep log sections 4 and 5 fixed in place
  plus a pointer to section 9; (11) importlib 103-106.
- Drills: (12) A5 step 3 rewritten as a standalone one-shot
  JSONL script in the step 8 shape, --chromium-set-value on
  steps 1, 3, 5, precondition 3 points at step 1, run JSON
  has no broker_finish field; (13) A3 wedge drill with exact
  lock, status, result, finish, recovery and PID commands
  and corrected expectations; (14) A4 probe with the laptop
  .so paths and hashes, the Y6e launcher, and the Y6b v2
  runner arms for steps 2-4.

### 10.8 Fix evidence (checks ran after the fixes)

Hash for all checks: ed4fcd4
(ed4fcd49775db4c61f5238ce10ea515bcbd6e294) plus the uncommitted
fix diff. Fix commit hash: reported to the coordinator in the
fix report, not in this file, because a commit cannot contain
its own hash. Times Asia/Ho_Chi_Minh.

- F-C1, compile: `python3 -m py_compile
  scripts/s2_flip_live.py tests/test_s2_flip_wiring.py`.
  Output: PY_COMPILE_OK, exit 0. Time: 2026-11-23 00:37:48
  +07, elapsed 0.152s. Re-run after all doc edits:
  00:42:59 +07, exit 0.
- F-C2, wiring plus pill: `python3 -m unittest
  tests.test_s2_flip_wiring tests.test_s2_flip_pill`.
  Output: Ran 60 tests in 0.367s, OK. Time: 2026-11-23
  00:37:48 +07, elapsed 0.8s. The 60 are 54 wiring (40 old
  plus 14 new BrokerProbeRecountTests) plus 6 pill. Re-run
  after the M-F5 test fix: 00:39:32 +07, Ran 60 tests in
  0.307s, OK. Final re-run: 00:42:59 +07, Ran 60 tests in
  0.397s, OK.
- F-C3, baseline: pristine HEAD copy via `git archive HEAD`
  to /tmp/b24-fix-baseline, same command. Output: Ran 38
  tests in 0.331s, OK. Time: 2026-11-23 00:38 +07. Delta 60
  minus 38 is 22: the 8 BrokerCodeExecTests from the original
  migrate plus the 14 new BrokerProbeRecountTests from this
  fix round.
- F-C4, neighbours: `python3 -m unittest
  tests.test_session_remote tests.test_code_exec`. Output:
  Ran 163 tests in 51.289s, OK. Time: 2026-11-23 00:38 +07,
  elapsed 51.5s.
- F-C5, mutations on a /tmp copy only
  (/tmp/b24-fix-mutations.py, base /tmp/b24-fix-mutbase):
  control BrokerProbeRecountTests rc 0. All 8 mutations flip
  their target test to FAIL (M-F1, M-F2, M-F4, M-F5, M-F6,
  M-F8 fail; M-F3 and M-F7 error). Time: 2026-11-23
  00:39:21-00:39:28 +07, elapsed 7.2s. Collateral is coherent
  (shared code paths: M-F1 also flips the other 4 tests that
  assert broker_next_seq 4; M-F2 also flips the
  probe-unavailable test; M-F3 also errors the replay-failed
  test; M-F4 also flips the replay-failed test; M-F6 also
  flips the fill-recount test; M-F7 also errors both replay
  tests). Honest note: the first mutation run, 00:39:05
  +07, FAILED on M-F5 (the unknown-status test stayed green)
  because the catch-all raise at the end of broker_code_exec
  still raised with 'unknown' in its message. That run caught
  a hollow assertion, so the test was tightened to assert
  'result unknown' in the error, and the full mutation script
  was re-run clean at 00:39:21 +07.
- F-C6, doc greps, 00:41-00:42 +07: no em dash or en dash in
  any of the 7 B2-4 files (grep rc 1, zero hits); HEAD label
  ed4fcd4 in the 3 drills, prep log section 9, and this log
  header; importlib range 103-106 in this log 3.1 and prep
  log 3.2 and 9.1; prep log section 4 overlay numbers match
  section 9 (693 lines, Daemon 238, serve 377,
  _ensure_daemon 489, cmd_acquire 525). The remaining
  0400e86 mentions are true history: the original work was
  measured when 0400e86 was HEAD at 00:09, and prep log
  section 5.1 plus 9.2 name it as the pre-migrate base.
- F-C7, A3 citations by grep at ed4fcd4, 00:41 +07:
  session_remote.py _status 871, _result 847, _request 790,
  _client_finish 1563, _fail_task 926,
  _task_recovery_required 933. Every line matches the drill.
- A5 step 3 script check: the standalone script embedded in
  the A5 drill was extracted to /tmp/a5-drill-step3-check.py
  and compiled: `python3 -m py_compile` exit 0, STEP3_OK.
  Time: 2026-11-23 00:42 +07. The script was not run live
  (it needs a GO and a stopped relay); only its syntax was
  checked.

### 10.9 Per-finding verdict

- (1) Seq reuse: FIXED. Post-accept paths raise
  _BrokerSendConsumed carrying broker_next_seq seq plus 1;
  the except handler keeps a success-path next_seq on V12
  errors; the two-browser test pins it and M-F1 flips it.
- (2) Pre-dispatch proof: FIXED. _code_exec_send probes
  `result --sequence N` before fallback and falls back only
  on not_found; a record refuses the fallback, an
  unanswerable probe refuses it too. broker_unavailable is
  deliberately NOT proof, because _exchange maps any socket
  OSError (including a receive failure after transmit) to
  that name. M-F2 flips the probe test.
- (3) Replay completed: FIXED. broker() returns the recorded
  response for status completed without a result fetch;
  broker_code_exec returns its envelope with next_seq seq
  plus 1. M-F3 flips it.
- (4) Running/failed statuses: FIXED. Only completed
  returns an envelope; running, failed, unknown, and any
  unexpected status raise _BrokerSendConsumed with next_seq
  seq plus 1. M-F4 and M-F5 flip them.
- (5) Recount before fallback: FIXED. _send_browser_inner
  passes a recount closure that re-runs count_check for
  both variants (fill included) and refuses the fallback on
  count not 0 or a count error. M-F6 flips it.
- (6) Duplicate validation: FIXED. Second program_variant
  block deleted; Harness.__init__ validates once.
- (7) Header docstring: FIXED. Names the CLI subcommands
  (start, request, result, finish) and states the harness
  never calls _client_start, _client_start_with_wait, or
  _client_finish, and broker_start has no busy-wait.
- (8) Test coverage: FIXED. 14 new tests, all flipped by
  their F-C5 mutations; the real broker() path is now
  covered by ssh-faked tests (replay, unknown status,
  exact command shape).
- (9) HEAD labels: FIXED. ed4fcd4 in the 3 drills, prep log
  section 9, and this log header; the original 0400e86
  mentions that remain are dated history, stated as such.
- (10) Prep sections 4/5: FIXED. Section 4.1 numbers
  corrected in place to the section 9 table; sections 4
  and 5 carry a pointer to section 9; section 5.1 marked
  pre-migrate; section 5.2 clarifies the harness shells the
  CLI and never calls the Python client functions.
- (11) Importlib range: FIXED. 103-106 in all three places.
- (12) A5 drill: FIXED. Step 3 is a standalone one-shot
  JSONL script in the step 8 shape (extracted and compiled,
  not run live); steps 1 and 5 carry --chromium-set-value;
  precondition 3 points at step 1; the run JSON has no
  broker_finish field, stated twice. Also fixed in the same
  pass: the drill now names scripts/ssh-laptop-mux.sh as the
  SSH path, because ~/workspace/ssh-laptop.sh does not exist
  in this VM (verified by ls).
- (13) A3 drill: FIXED. Exact commands for the lock probe
  (broker start, fail fast, expect busy, not the owner_lock
  sentence), status polls (fields as _status returns them,
  driver stays ready under SIGSTOP, no last_activity field),
  result poll for the in-flight sequence (request returns
  accepted or busy at once; only result waits 120s),
  finish returning cleanup_pending after 120s, fresh start
  returning recovery_required at step 6 and accepted only
  after step 7, recover before any snapshot handling with
  an explicit never-unlink-session.json rule, and PID/PGID
  capture via the relay process tree with PID-only kills.
- (14) A4 probe: FIXED. Step 1 names the loadable rebuilt
  .so on the laptop with its md5 and the grep plus md5sum
  commands, records backup 1 as a dead ABI path (sha256
  given only to identify it) and backup 2 as an unused
  different build; names the Y6e launcher
  (improvements/worker-y6e-nested-load-test.sh, 291 lines)
  and states it is load-only; steps 2-4 name the Y6b v2
  runner (improvements/worker-y6b-run-nested-wayland-v2.sh,
  973 lines; laptop copy /tmp/y6-nested/run-nested-wayland.sh)
  with its Arm A and Arm B verdict lines, and state plainly
  that no standalone LIQUID driver script exists in the
  repo. Step 4 counts come from the runner SUMMARY lines
  plus E1 [indicator-metrics] stderr counts; the live-run
  capture parameters do not apply to grim PNGs in the nest.

### 10.10 Leftovers

- No finding was left unfixed. The live proofs still need
  a GO: the A5 gate item 2 live broker send, the A5 drill,
  the A3 wedge drill, and the A4 probe. Nothing live was run
  in this round.
- The automatic fallback still refuses when the broker is
  down and the probe cannot answer: the operator then reruns
  with --transport oneshot (documented recovery) or runs
  the A5 drill step 3 standalone script. That conservatism
  is deliberate (see (2) above), not an oversight.
- The A5 drill step 3 script is syntax-checked only, never
  run live; its first live run is the drill itself, under GO.
