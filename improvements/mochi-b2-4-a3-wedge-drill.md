# A3 wedge drill (B6): recovery of a wedged session, driver holds scope plus cancel latch plus lock, no double-send on retry

Status: PREPARED ONLY, NOT RUN. Prepared by worker B2-4, 2026-11-23
00:17 +07, worktree HEAD ed4fcd4. This drill needs an explicit GO
from Muse tong before any live step runs. No live run, no browser
work, no SSH was done while writing this file. No em dash or en
dash anywhere in this file. No personal info.

## 0. What this drill proves

The B6 lift limb that step 9 left open (step 9 log section 12:
no dedicated wedge drill was run in step 9, gap recorded, not
papered over) and the A3 gate item 2 (prep log section 3.3): on
a live run, the driver demonstrably holds all three at once,
scope plus cancel latch plus lock, and a wedged session recovers
without a destructive action double-sending on retry. A wedge
here means: the driver holds the scope (its process group), the
cancel latch path, and STATE/cursor.lock, but stops making
progress and stops answering broker requests.

Sources for the recovery order below: step 8 log section 4
(queue discipline and recovery procedure) and section 6.2
(fallback drill), session_remote.py _task_recovery_required
(line 933), _fail_task (line 926), _client_start_with_wait
(line 1494), _status (line 871), _result (line 847),
_client_finish (line 1563), IDLE_TIMEOUT 300.0 and
REQUEST_TIMEOUT 120.0 (session_remote.py lines 38, 40).

## 1. Preconditions (all checked before step 2, any miss aborts)

1. A scratch target exists in Zen on ws1, or the owner hands
   over a scratch tab. NEVER use the owner's live tabs. All
   sends in this drill use a scratch tab with a fake composer
   (harness --dry-run seed) and unique test messages, so no
   message lands in a real thread.
2. No live owner session is running (broker status state idle,
   owner null). One runner live at a time (gate G-SINGLE-LIVE).
3. The pill is held for the whole drill (W-PILLCDP, rule 4.29):
   every live action goes through a computer-use session so
   the pill shows.
4. The drill operator is the ONLY recovery worker for this
   run. Nobody else kills, cancels, or restarts anything
   during the drill. The cancel latch belongs to the user;
   the coordinator never uses it as a stop tool (step 8 log
   section 4), so the drill's cancel step below is the
   operator acting on the owner's standing cancel path, not a
   second runner.
5. The wedge is induced deterministically: SIGSTOP on the
   session-driver child process. No code change, no poisoned
   program, no real hang is needed. The driver keeps holding
   all three while stopped, which is exactly the wedge shape.

## 2. Procedure

All commands run on the VM unless marked laptop. Times are
Asia/Ho_Chi_Minh plus elapsed.

Step 1, start a live broker session and a send. Start one
broker batch on the scratch target (harness dry-run, default
broker transport, new run number, unique message M1). Record
the lease file, owner, generation, and the first sequence
numbers. The SIGSTOP in step 2 must land while this batch is
still running, with a send in flight: if the batch already
finished before the SIGSTOP, no wedge happened, so stop,
record it, and restart from step 1 with a longer batch (both
browsers). While the session is running, record the three
holdings:

- Lock: a second start attempt during the run must be
  refused. Run it from a separate shell on the VM, fail fast
  (no --wait), with a fresh probe lease:

  `scripts/ssh-laptop-mux.sh "python3 ~/computer-use-wayland/scripts/session_remote.py start --owner a3-wedge-probe --lease-file ~/.cache/agent-computer-use/a3-wedge-probe.lease"`

  Expected output is `{"ok": false, "error": "busy", ...}`
  with rc 1: _start answers busy while a task runs
  (session_remote.py _start). That is the lock refusal at the
  broker layer. The sentence "another automation session or
  plugin activation is active" is NOT the expected output
  here: it is the owner_lock message from a direct `cu
  session` guardian startup, a different path, so do not
  abort for seeing `busy` instead of that sentence. Record
  the refusal, then do NOT retry it, and remove the probe
  lease on the laptop (`rm -f
  ~/.cache/agent-computer-use/a3-wedge-probe.lease`)
  so it cannot confuse a later start. This is the lock limb,
  measured live.
- Scope: record the driver process group (driver PID and its
  process group) from the laptop process list while the
  session runs. First the relay PID:

  `scripts/ssh-laptop-mux.sh "systemctl --user show computer-use-relay.service -p MainPID"`

  Then the relay children, which include the session-driver:

  `scripts/ssh-laptop-mux.sh "ps --ppid <relay-pid> -o pid,pgid,args"`

  The driver is the child whose args contain `session-driver`.
  Record its PID and PGID in the drill log, and confirm with
  `scripts/ssh-laptop-mux.sh "ps -o pid,pgid,args -p <driver-pid>"`.
  Listing by process tree is allowed; killing is by the
  recorded PID only, never by pattern.
- Latch: record that STATE/cancelled is absent before the
  cancel step (latch clear):

  `scripts/ssh-laptop-mux.sh "test ! -e ~/.cache/agent-computer-use/cancelled && echo latch-clear"`

Step 2, wedge it. On the laptop, SIGSTOP the session-driver
child PID recorded in step 1 (kill ONLY that PID, never
pkill -f with a pattern that could match the operator's own
command line, step 8 log section 4):

`scripts/ssh-laptop-mux.sh "kill -STOP <driver-pid>"`

Record the time. The driver now holds scope plus latch path
plus lock and answers nothing.

Step 3, observe the wedge (do not touch anything yet).
Poll broker status every 5s with the exact command:

`scripts/ssh-laptop-mux.sh "python3 ~/computer-use-wayland/scripts/session_remote.py status --lease-file <lease>"`

Record each poll: state must stay running, active_sequence
stuck on the in-flight sequence, next_sequence unchanged,
driver still ready, guardian active, cancelled false,
recovery none. Two corrections to the old expectation: the
driver stays `ready` while the process is SIGSTOPped (the
broker tick only changes the driver field when the process
exits or the request worker errors, so "driver not ready" is
wrong), and _status has NO last_activity field (its fields
are state, owner, generation, driver, guardian, cancelled,
cancellation_state, recovery, next_sequence,
active_sequence, error, stop_reason), so frozen activity is
evidenced by active_sequence stuck plus next_sequence
unchanged, not by a last_activity value. The wedge threshold
is 300s with no progress and no status change (one
IDLE_TIMEOUT, step 8 log section 4). For this drill the
operator may declare the wedge after 60s of frozen status
PLUS the stuck active_sequence, and record that the full
300s threshold was NOT waited out: the 60s declaration is a
drill shortcut, and the log must say so. The production rule
stays 300s. Do NOT send a new broker request expecting
silence: a request during the wedge returns `accepted` at
once (the worker thread starts immediately) or `busy` if a
request is already active. The 120s wait applies to the
result of the in-flight sequence only, so poll it once:

`scripts/ssh-laptop-mux.sh "python3 ~/computer-use-wayland/scripts/session_remote.py result --lease-file <lease> --sequence <in-flight-seq>"`

It waits up to REQUEST_TIMEOUT 120s (plus 5s client margin)
and returns the record status, expected `running` while the
driver is stopped. Do NOT send a second request for the same
sequence while the first is unanswered (one request at a
time, strictly increasing sequence).

Step 4, cancel latch. Set the cancel latch (the owner's
cancel path: `computer-use cancel` on the laptop, that is
`python3 ~/computer-use-wayland/scripts/cu.py cancel`,
or the Escape binding). Record the time. The wedged driver cannot
act on the latch while stopped, so nothing is expected to
stop yet. This step proves the latch was set and is visible
in broker status (cancelled true, cancellation_state
latched), not that a stopped driver obeys it. Note the
broker tick also fails the task on the latch
(_fail_task, 'cancelled'): state becomes failed and driver
becomes failed while the driver process is still stopped,
so the step 3 "state running" expectation no longer holds
after this step; that is the latch working, not a new failure.

Step 5, kill the driver, in order (step 8 log section 4).
SIGCONT the driver first (a stopped process cannot die
cleanly or run its cleanup):

`scripts/ssh-laptop-mux.sh "kill -CONT <driver-pid>"`

Then finish with the owner's lease when held (120s timeout):

`scripts/ssh-laptop-mux.sh "python3 ~/computer-use-wayland/scripts/session_remote.py finish --lease-file <lease>"`

Expected: the finish call runs the full 120s and returns
`{"ok": false, "status": "cleaning", "error":
"cleanup_pending"}`. That is the correct outcome here, not a
clean finish: _client_finish waits until state is finished
or failed AND the guardian is not active, and the guardian
is still active because the snapshot is retained and the
driver process is still alive, so the poll hits the deadline.
Then kill ONLY the driver child by PID: SIGTERM, wait,
SIGKILL when still alive. Never the cancel latch as the kill
tool, never a pattern kill. The exact commands, with the
recorded PID only:

`scripts/ssh-laptop-mux.sh "kill -TERM <driver-pid>"`

then, after a wait, if `ps -o pid= -p <driver-pid>` still
prints the PID:

`scripts/ssh-laptop-mux.sh "kill -KILL <driver-pid>"`

Record each signal and time.

Step 6, verify the kill. Broker status (same status command
as step 3) must show state failed, driver failed,
stop_reason cancelled, guardian recovery_required, recovery
required. The process list must show no driver process group
left: `ps -o pid= -p <driver-pid>` prints nothing, and
`ps --ppid <relay-pid> -o pid,pgid,args` shows no
session-driver child (no orphaned driver group, the scope
limb). A fresh start attempt now must return
recovery_required, NOT an acceptance: the failed task plus
the retained snapshot make _start refuse until recovery
(step 7). Run it fail fast with a fresh probe lease:

`scripts/ssh-laptop-mux.sh "python3 ~/computer-use-wayland/scripts/session_remote.py start --owner a3-wedge-probe2 --lease-file ~/.cache/agent-computer-use/a3-wedge-probe2.lease"`

Expected output is `{"ok": false, "error":
"recovery_required", ...}` with rc 1. Record it, do NOT
start a probe session here, and remove the probe lease.
The lock-free check (a fresh start accepted) moves to after
step 7: only a recovered broker can accept.

Step 7, recover. Follow the recovery procedure in order:
verify the driver is dead and status shows driver failed
(step 6), then run `computer-use recover` FIRST, before
anything else touches the snapshot:

`scripts/ssh-laptop-mux.sh "python3 ~/computer-use-wayland/scripts/cu.py recover"`

Recover takes the owner lock, stops the session, and
restores the desktop from session.json, and restore()
unlinks session.json itself when it succeeds. NEVER unlink
session.json by hand: it is the recovery state restore()
needs, and hand-unlinking would discard an unrestored
desktop (restore() refuses to silently discard one). If
recover exits nonzero, or session.json is still present
afterwards, STOP and report to the coordinator: do not
hand-delete the snapshot and do not proceed. Only after a
clean recover, restart the relay (`systemctl --user restart
computer-use-relay.service` over mux SSH), verify a clean
broker status (state idle, owner null, recovery none, new
generation), then prove the lock is free: a fresh start with
a fresh lease must now be ACCEPTED (record the ok True
answer, then finish that probe session at once with the
finish command from step 5; it is a probe, not a batch).
Then `python3 scripts/session_cleanup.py --check` must exit 0
(no snapshot, no indicator socket, no stop markers, no
overlay holders, no guardian process).

Step 8, the destructive-action retry (no double-send proof).
First determine the outcome of the wedged attempt: count
message M1 in the scratch thread with the exact count call:

`scripts/ssh-laptop-mux.sh "node /tmp/c5-count.mjs <endpoint> <tab-id> 'M1'"`

where endpoint is the browser endpoint (Brave
http://127.0.0.1:9224, Chromium http://127.0.0.1:9223) and
tab-id is the scratch tab from step 1. If the count is 0, M1
never sent: retry with a NEW run number and a NEW unique
message M2 through a fresh broker lease, and verify M2
arrives exactly once (pre-count 0, delayed count 1). If the
count is 1, M1 already sent: mark the attempt already-sent,
do NOT retry M1, and verify with a fresh message M2 on a
fresh lease that the session works. NEVER replay the old
batch for an uncertain-outcome action (step 8 log section 4):
the old batch is abandoned, and only a new message on a new
lease proves the retry path.

## 3. Pass criteria (all must hold)

1. Lock limb: the second start during the run got `busy`;
   after recovery (step 7) a fresh start is accepted.
2. Latch limb: the cancel latch set in step 4 is visible in
   broker status (cancelled true, cancellation_state latched),
   and after recovery the latch is cleared by resume (only
   resume clears it).
3. Scope limb: after the kill, no orphaned driver process
   group remains and session_cleanup.py --check exits 0.
4. Recovery: `computer-use recover` exits 0 and session.json
   is gone, relay restarted, clean broker status with a new
   generation, fresh lease starts a batch end to end.
5. No double-send: the wedged message count is 0 or 1 (never
   2), the retry message M2 has pre-count 0 and delayed
   count exactly 1.
6. The old batch is abandoned, never replayed.

## 4. Abort and failure rules

- If the lock refusal does NOT happen in step 1 (the second
  start returns anything other than `busy`, including an
  acceptance, while the first runs), STOP at once.
  Two live runners is the worst A3 failure mode: do not
  proceed to the wedge. Report to the coordinator.
- If the driver process group cannot be identified
  unambiguously by PID, STOP. Never kill by pattern.
- If the kill in step 5 leaves a live driver process, or
  `computer-use recover` in step 7 exits nonzero, or
  session.json is still present after recover, STOP with the
  session unrestored and report to the coordinator. Never
  unlink session.json by hand. No new live run until --check
  exits 0.
- If the wedged message M1 count is 2 or more at step 8,
  STOP: a double-send happened. Do not retry anything.
  Preserve the run JSONs and the broker status log and
  report to the coordinator.
- If the cancel latch is still latched after recovery,
  clear it only with resume (the user's resume path), never
  by deleting the latch file by hand while a session could
  be live.

## 5. Evidence to collect

- Broker status polls from step 3 (state, active_sequence,
  next_sequence, driver, guardian, recovery, error,
  stop_reason) with times. Note _status has no last_activity
  field, so no last_activity value is recorded.
- The driver PID and process group recorded in step 1, the
  SIGSTOP/SIGCONT/SIGTERM/SIGKILL times in steps 2 and 5.
- The lock probe outputs (step 1 `busy`, step 6
  `recovery_required`, step 7 fresh start accepted).
- The latch set and clear records (steps 4 and 6).
- The `computer-use recover` output and the session.json
  absence check (step 7), the relay restart PID and
  generation before and after (step 7), the
  session_cleanup.py --check output.
- The M1 count, the M2 pre-count and delayed count, and the
  run JSONs (step 8).
- Times in Asia/Ho_Chi_Minh plus elapsed per step, and the
  commit hash of the code under test.

## 6. What this drill does NOT prove

- It does not prove the driver-held design for A3 (that
  design does not exist yet; it lives in the step 9
  prototype, and the A3 gate needs a live run on the
  rewired driver-held start, not on the supervisor tree).
  This drill proves the recovery procedure against the
  CURRENT tree, so the A3 gate has a recovery proof to
  compare the driver-held behavior against.
- It does not prove the A5 fallback (separate file,
  improvements/mochi-b2-4-a5-fallback-drill.md).
- It does not prove the pill crash behavior (A4 stage (b),
  separate crash drill, not yet written).
