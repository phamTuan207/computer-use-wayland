# Worker C5-STEP10-PREP log: deletion plan for A3/A4/A5 (design only)

Owner: the owner. Coordinator: COORD-CLICK-5. Repo
~/workspace/computer-use-wayland, branch todolist-push. This worker
is the design-only prep lane for step 10, running in parallel with
step 9, rung 2, and Y13G round-3. NO code changes, NO live runs, NO
browser work in this task. No em dash or en dash anywhere in this
file. No personal info. Wall-clock Asia/Ho_Chi_Minh plus elapsed
time on every entry.

## 0. Task and sources

- Task received 16:02 +07, Sun 2026-11-22 (T+0m). VM HEAD 5a8c29d
  at start.
- Final direction improvements/worker-click3-final-direction-log.md
  (commit e05fc58), section 3 step 10 and section 5 (B3/B4 lifts),
  plus the A3/A4/A5 rows in section 1. Step 10 in full: "A3/A4/A5
  deletions last, each gated on its replacement proving (A3:
  driver holds scope plus cancel latch plus lock; A4:
  session-level pill measured, then driver-owned pill crash
  proof, then delete the server; A5: broker proven on the VM
  path with one-shot SSH kept as recovery). DATES: ... the
  coordinator sets one date per deletion at the step-9 prototype
  decision, records it before any deletion executes, and a
  deletion with no date does not execute."
- Step 8 deletion spec as template:
  docs/batch11-task2-step8-deletion-spec-20261122.md, fetched
  read-only from origin/main with `git fetch origin main` and
  `git show origin/main:docs/batch11-task2-step8-deletion-spec-20261122.md`,
  234 lines, saved to /tmp/step8-spec.md for reading only, never
  committed. The spec was written against todolist-push HEAD
  759ce41 and re-checked at HEAD 0a1fad4.
- Step 8 log improvements/worker-click5-step8-log.md (commit
  4eebc15, 851 lines): how the spec turned into a landed deletion
  with proof. Pattern reused in section 2 below.
- Step 9 log improvements/worker-click5-step9-log.md (untracked
  at read time, in progress): (b1) landed as a first-class shape
  in cdp.mjs (option A), Zen pointer delegate wired
  (zen_pointer.py), 15 tests, 175 OK across zen_pointer plus
  p2_element_ref plus code_exec. LIVE PROOF still open at read
  time: the clone chats live in Brave/Chrome, not Zen, so a Zen
  live proof needs a scratch target in Zen. The step 9 prototype
  gate (B6 lift: snapshot/execute/verify end to end on one live
  ws2 clone chat plus held-out tasks, wedged-session recovery
  proven, destructive-action test proving no double-send on
  retry) is NOT yet met. Every gate in this plan that names the
  step 9 proof is therefore still open, and no deletion date in
  this plan is a calendar guess: each proposed date is tied to
  the day its gate proof lands.
- All file plus line coordinates below were re-measured at HEAD
  5a8c29d with grep in this task (see section 8). Where the step
  8 spec already corrected a wrong coordinate from an earlier
  review (for example the 9222 versus 9223 endpoint, or the
  nonexistent dom_act.open_dom_session), this plan cites the
  corrected form and the file it was verified in.

## 1. Time log

- 16:02 +07, T+0m: task received. Read the final direction
  step 10, the A3/A4/A5 rows, section 5 B3/B4 lifts, and the
  step 8 row for the pattern. VM HEAD 5a8c29d.
- 16:03 +07, T+1m: fetched the step 8 spec read-only from
  origin/main (234 lines) and read it in full. Read the step 8
  log sections 0, 1, 5, 6, 8.
- 16:04 +07, T+2m: mapped all three deletion targets at HEAD
  5a8c29d with grep: cursor_session.py (A3), overlay.py plus
  first_action.py overlay gate (A4), s2_flip_live.py plus
  ssh_mux.py plus session_remote.py (A5). Read
  cursor_session.py (344 lines) and ssh_mux.py in full,
  overlay.py entry points, cancel_hotkey.py latch functions,
  first_action.py stubs at lines 187-212, and the step 9 log
  head and tail.
- 16:05 +07, T+3m: wrote this plan file. No code touched, no
  live run made, no browser work done.

## 2. The step 8 pattern this plan follows

Step 8 landed the per-batch spawn deletion (commit 8c6553a)
this way, and each step 10 deletion worker must repeat the
shape:

1. Spec first, as a design doc with no code change. The step 8
   spec named the exact functions, the exact callers, the five
   measured preconditions, the queue discipline, the
   serialization decision, the fatal-on-read-failure matrix, the
   fallback and recovery procedure, and a gate test list with a
   command per item. It also corrected wrong coordinates from
   earlier reviews instead of repeating them.
2. Gate tests before the deletion executes. Step 8 ran a sync
   verification, a live broker batch re-run, a concurrency test
   (two workers, second gets busy, waits for finished/failed,
   unlinks the lease, retries with a fresh start_id), a
   fatal-on-read-failure test per matrix class, a recovery test
   with a real relay restart, and a live smoke plus fallback
   drill.
3. Deletion as one commit with an explicit pathspec, with the
   deleted entry points kept as loud stubs that raise
   RuntimeError (first_action.py session_cmd at line 187 and
   attempt_session at line 201), so any stale caller fails
   loudly instead of silently resurrecting the deleted path.
4. The fallback stays and is drilled, not just documented. Step
   8 kept one-shot SSH as fallback and recovery and proved it
   in a fallback drill (step 8 log section 6.2, passed on the
   second attempt).
5. The half that is not ready is deferred in writing, not
   dropped. Step 8 deferred the session-level pill because the
   CB-10 precondition was unmet (step 8 log section 8), and
   recorded it as BLOCKED. That deferral is why A4 step (a) is
   still open in this plan.
6. Every push verified with git ls-remote, every claim with a
   test command, its output, a commit hash, and a time log
   (Lauren Tan standard).

## 3. A3: delete the session supervisor tree

### 3.1 What it removes

The tree is scripts/cursor_session.py (344 lines at HEAD
5a8c29d). Exact symbols:

- supervise(env, argv), line 228. Spawns the guardian as a
  child process (new session, pipe plus token), waits for the
  guardian `ready` line, spawns the driver gated on a `go`
  byte, registers the driver pid with the guardian, polls both
  processes, kills the driver group on cancel or stop, and
  reaps the guardian with a 20s wait. This is the process tree
  itself.
- guardian(env, pipe, token), line 136. Holds the single-runner
  lock (owner_lock, line 73), writes the session snapshot
  (STATE/session.json, version 4, token plus cursor theme),
  installs the temporary Escape binding, gates on the liquid
  backend before creating the indicator (hyprglass not active
  is a hard refusal), opens the indicator server, owns the
  driver process group, and cleans up in finally (stop marker,
  stop_group, drain_input, native close, server close, guard
  close, restore).
- stop_group(group), line 208, and terminate_driver(driver),
  line 220. The named killable scope: SIGTERM to the whole
  driver process group, 0.6s deadline, then SIGKILL, then
  reaping the direct child.
- request_stop(expected), line 27. Writes the stop-<token>
  marker that the guardian polls. Called by cu.py cancel (line
  3114) and by cancel_hotkey.py resume path (line 219-220).
- recover(env, expected), line 103, and stop(env, timeout=8),
  line 120. Recovery and stop under the owner lock.
- restore(env), line 39. Removes the Escape binding, restores
  the cursor theme, unlinks the indicator endpoint, the
  snapshot, and the stop marker. Three attempts, then the
  snapshot is retained and the operator is told to run
  `computer-use recover`.
- owner_lock(), line 73. flock LOCK_EX plus LOCK_NB on
  STATE/cursor.lock. This is the single-runner lock today. The
  comment at lines 76-80 records that the lock is also held by
  plugin activation, not only by a running session.
- SessionVisuals, line 93, and drain_input(), line 87.
  Presentation fence plus input drain before restore.
- The `__main__` dispatch, line 333: `driver` (gate read, then
  exec the driver argv) and `guard` (run guardian). The
  `guard`/`driver` argv protocol is the tree's internal wire
  format.
- The cancel latch itself lives in scripts/cancel_hotkey.py:
  latch_present, line 59; latch, line 120; cancellation_status,
  line 157; cancellation_message, line 197. The latch file is
  STATE/cancelled. The only two places that unlink it are
  cancel_hotkey.py line 222 (resume) and cu.py line 3179
  (resume). The latch module is NOT deleted with A3: the driver
  must hold the latch, which means the latch file and these
  functions stay, only their owner changes from the guardian to
  the driver.

What A3 does NOT remove: the driver itself
(scripts/session_driver.py relay, lines 59-129, which runs
inside the tree today), the broker (scripts/session_remote.py,
which spawns the tree at _launch, line 520, with argv
`[python, CU, 'session', '--', python, CU, 'session-driver']`),
the indicator module (scripts/indicator.py, the pill renderer
the guardian uses), the cancel latch module above, or the
cleanup verifier (scripts/session_cleanup.py, which checks for
a snapshot, an indicator socket, stop markers, overlay
holders, and a guardian process, and which must be updated to
check for the driver-held equivalents instead of a guardian
process).

### 3.2 What calls it today (callers, with file plus line)

- scripts/cu.py lines 3104-3114: the `session`, `stop`,
  `recover`, and `cancel` commands. `session` calls
  cursor_session.supervise(env, args.driver) at line 3109
  (after refusing a nested session when CU_SESSION_TOKEN is
  set, and after an optional replace stop). `stop` calls
  cursor_session.stop(env) at line 3105. `recover` calls
  cursor_session.recover(env) at line 3110. `cancel` latches
  and then calls cursor_session.request_stop() at line 3114.
- scripts/session_remote.py line 520 (_launch): the broker
  spawns the tree for every broker task. This is the only
  production spawner of supervise left after step 8 deleted
  the per-batch spawn in first_action.py.
- scripts/cu.py line 3460: stop_session_on_error calls
  cursor_session.request_stop(CU_SESSION_TOKEN) when a driver
  command fails.
- scripts/cancel_hotkey.py lines 219-220: resume calls
  cursor_session.request_stop().
- scripts/activate-cursor-guard.py lines 62-63, scripts/
  activate-session-backend.py line 72, scripts/setup.py lines
  314-315, scripts/visuals.py lines 242-243, scripts/
  sync-installed.py line 115: these hold
  cursor_session.owner_lock() directly (activation, setup, and
  installed-tree sync paths). The fifth holder is easy to miss:
  sync-installed.py loads cursor_session dynamically with
  importlib (lines 103-106) and holds the lock inside
  _session_lock (line 115, used at line 1259), so a plain grep
  for `import cursor_session` never finds it. They are lock
  holders, not tree callers, and they must keep working after
  A3: the lock file name (STATE/cursor.lock) and the flock
  semantics must be preserved by whatever the driver holds
  instead, or these five call sites must be migrated in the
  same commit. The three owner_lock() calls inside
  cursor_session.py itself (lines 104, 125, 142) are NOT
  counted here: they are tree-internal and die with the tree.
- scripts/session_cleanup.py lines 5-6 and the guardian check:
  documents that the guardian cleans up, and checks for a
  leftover guardian process. After A3 it must check for a
  leftover driver-held session instead.
- Tests: tests/test_cursor_session.py (955 lines, about 30
  tests, including test_guardian_death_reaps_whole_driver_
  group, test_concurrent_session_cannot_overwrite_original,
  test_old_command_cannot_stop_new_session, and
  test_indicator_loss_kills_driver_and_cleans_up). A deletion
  commit that removes supervise and guardian must delete or
  rewrite these tests in the same commit, and the gate must
  name the replacement tests that cover the same behaviors
  under the driver-held design.

### 3.3 Its gate (checkable condition, not a vibe)

ALL of the following must be true, each with a log line, a
commit hash, and a time log, before the deletion executes:

1. B6 lift recorded: the step 9 prototype runs
   snapshot/execute/verify end to end on one live ws2 clone
   chat plus held-out tasks, with the wedged-session recovery
   protocol specified and proven, and a destructive-action
   test proving no double-send on retry. This is the final
   direction section 3 step 9 gate. Until the coordinator
   records the B6 lift, A3 does not execute.
2. B4 lift for the A3 limb recorded: on a live run, the driver
   demonstrably holds all three at once, scope plus cancel
   latch plus lock. Checkable form: one live run where (a) the
   driver holds STATE/cursor.lock for the whole task (a second
   start attempt during the run gets the lock refusal, same
   message as today), (b) setting the cancel latch mid-task
   stops the driver within the same bound the guardian meets
   today (measure it; the guardian polls every 0.05s in
   supervise and the latch check is in the guardian loop, so
   the driver-held bound must be stated as a number and met),
   and (c) killing the driver wrapper mid-task leaves no
   orphaned driver process group and no unrestored snapshot
   (session_cleanup.py --check exits 0 afterwards, with its
   guardian check migrated to the driver-held equivalent).
3. The contract line is satisfied, not just quoted:
   docs/layer0-cbexec-contract.md lines 466-471, "the session
   supervisor tree is deleted only when the driver demonstrably
   holds all three on a live run (A3 gate, B4 lift)". The
   demonstration is item 2, on a live run, not a unit test.
4. No live runner depends on the tree: the broker _launch path
   (session_remote.py line 520) is rewired to the driver-held
   start in the same commit, and a live broker batch runs end
   to end on the rewired path before the deletion lands (same
   shape as the step 8 live smoke: at least one batch, observe
   plus click plus type, with the result in the log).
5. The five direct owner_lock holders (activate-cursor-guard,
   activate-session-backend, setup, visuals, sync-installed) are
   verified against the driver-held lock in the same commit:
   either they are unchanged because the lock file and flock
   semantics are preserved, or they are migrated and their
   tests pass.

### 3.4 Proposed date

The day after the step 9 prototype proof lands AND the
driver-holds-three live proof (gate item 2) is recorded, both
at the step-9 decision where the coordinator sets the date.
Reason: A3 has no independent proof of its own; its gate is
the step 9 prototype plus one live run on the rewired path.
Setting the date earlier would schedule a deletion whose
replacement is still unbuilt. If the step 9 proof slips, the
A3 date slips with it by the same number of days; the date is
a function of the proof, not of the calendar.

### 3.5 Rollback plan

The deletion lands as one commit with an explicit pathspec,
so the rollback is one command:

`git revert <A3-deletion-commit-hash>`

then re-verify, in order, before any live run resumes:

1. `python3 -m py_compile scripts/cursor_session.py
   scripts/cu.py scripts/session_remote.py` exits 0.
2. `python3 -m pytest tests/test_cursor_session.py -q`
   passes (the restored tests).
3. One live broker batch runs end to end on the restored tree
   (observe plus click plus type), and
   `python3 scripts/session_cleanup.py --check` exits 0
   afterwards.
4. The push is verified with
   `git ls-remote origin todolist-push`.

If the revert itself conflicts (because later commits touched
the same files), the fallback is `git revert --no-commit`
followed by manual conflict resolution limited to
cursor_session.py, cu.py, and session_remote.py, then the
same four verification steps. The revert restores the tree
exactly as deleted, including the guardian, the lock, the
latch polling, and the snapshot restore, so no separate
reconstruction step is needed.

### 3.6 What breaks if it is deleted too early

- Two live runners: without owner_lock held by anything, two
  broker tasks (or a broker task plus a direct `cu.py session`)
  start at once. Both drive the same desktop, both open a
  browser session, and the single Firefox remote session
  constraint (one BiDi or Marionette session per instance)
  breaks. User-visible symptom: clicks and types land in the
  wrong window, or the second session fails with a remote
  session conflict while the first is mid-task.
- Cancel stops working: the Escape binding and the latch poll
  live in the guardian. If the driver does not yet hold the
  latch, pressing Escape or running `computer-use cancel` sets
  a latch nobody reads. The run continues while the owner
  believes it stopped. This is the worst early-deletion
  failure because it removes the owner's only stop path.
- Orphaned driver groups: supervise reaps the driver group
  when the guardian dies or the wrapper is killed. Without
  the tree, killing the wrapper leaves the driver process
  group alive, still able to send input. Symptom: input keeps
  arriving after the session appears dead, and the next
  session cannot start because the snapshot was never
  restored.
- Cursor theme stuck: restore() is called by the guardian
  finally block. Without it, the agent cursor theme and the
  temporary Escape binding stay installed after the session
  ends, and the next session refuses to start because the
  snapshot exists (guardian raises on an unrestored snapshot).
- Pill label lost: the guardian creates the indicator server
  that shows the session pill label. Deleting the tree before
  the driver holds the pill label removes the owner's
  visibility into which session is live.

## 4. A4: delete the overlay daemon server (keep pill visibility)

Pointer: the coordinates in this section were re-measured at
HEAD ed4fcd4; the corrected table lives in section 9, and the
numbers below now match it.

### 4.1 What it removes

The server is scripts/overlay.py (693 lines at HEAD ed4fcd4).
Exact symbols:

- State paths, lines 36-44: BASE
  (~/.cache/agent-computer-use), OVERLAY_DIR (BASE/overlay),
  HOLDERS_FILE (holders.json), DAEMON_FILE (daemon.json),
  SOCKET_FILE (overlay.sock), LOCK_FILE (holders.lock),
  LOG_FILE (daemon.log). The deletion removes the server, not
  necessarily the holder accounting files: the holder file is
  the record of who wants the pill, and the deletion worker
  must state whether holders.json stays as the driver-owned
  pill's record or goes with the server. Default in this plan:
  the socket, the daemon record, the daemon log, and the
  server process go; the holder accounting functions stay
  until the driver-owned pill replaces them, because
  session_cleanup.py reads holders.json.
- Holder accounting: _log, line 48; _label_for, line 62;
  _prepare, line 71; _holders_lock, line 77; load_holders,
  line 88; save_holders, line 96; _holder_key, line 104;
  add_holder, line 113; remove_holder, line 129;
  prune_dead_holders, line 157; session_live, line 177;
  session_label, line 194; wayland_env, line 202.
- Daemon, line 238: _spawn_native, line 245 (spawns
  indicator.Native, which renders the pill); _close_native,
  line 251; _ensure_native, line 260; _show_label, line 285;
  apply_holders, line 309; status_reply, line 349; _monitor,
  line 361 (polls every
  2.0s, stops the daemon after 3 empty polls with no holders);
  serve, line 377 (binds the Unix socket, chmod 0600,
  listens, writes DAEMON_FILE with pid and start time).
- Client side: _daemon_running, line 463; _send_socket, line
  475; _ensure_daemon, line 489 (spawns `overlay.py daemon`
  as a detached process, waits up to 15s for a status reply).
- CLI: cmd_acquire, line 525; cmd_release, line 570;
  cmd_status, line 587; cmd_stop, line 608; cmd_daemon, line
  625; hold, line 631 (context manager that shells out to
  acquire and release); main, line 659 (acquire, release,
  status, stop, daemon subcommands).
- The per-batch tax this deletion removes is real: overlay
  acquire costs 315-349ms per batch (final direction A4 row,
  citing SPEED). The session-level pill (step a) removes the
  same tax without deleting the server, which is why step (a)
  comes first.

What A4 does NOT remove: the pill itself (visibility stays),
the indicator module that renders it, the liquid backend
(hyprglass), or the first_action overlay gate (which must be
rewired to the driver-owned pill, not deleted: the gate is
the rule that no pointer action runs invisible).

### 4.2 What calls it today (callers, with file plus line)

- scripts/first_action.py acquire_overlay(agent, method,
  label), lines 116-148: add_holder, then _ensure_daemon,
  then _send_socket acquire, then _label_for. On failure it
  removes the holder. This is the production acquire path
  for every act-now batch.
- scripts/first_action.py overlay_visible(agent), lines
  150-165: _send_socket sync, True only when the daemon
  reports the pill visible.
- scripts/first_action.py release_overlay(agent), lines
  167-184: _send_socket release, then remove_holder.
- scripts/first_action.py line 978: `import overlay as
  overlay_mod` in run(), the overlay gate in the act-now
  entry point. The module docstring at lines 19-21 states
  the D1 rule: overlay acquire is a precondition of any
  pointer action, enforced in code; if the overlay cannot be
  shown, the run refuses loudly and never acts invisibly
  (exit 2, refused, no overlay).
- scripts/session_cleanup.py lines 84-89: clean_safe imports
  overlay, repoints BASE, OVERLAY_DIR, HOLDERS_FILE, and
  LOCK_FILE at the given state dir, and calls
  prune_dead_holders(). The --check path also fails loudly
  while overlay holders remain (check 4 in the module
  docstring).
- Tests: tests/test_overlay.py, tests/test_first_action.py,
  tests/test_visuals.py, tests/test_s0_bundle.py (all grep
  for overlay). A deletion commit must update these in the
  same commit, and the gate must name the replacement tests
  for the driver-owned pill.

### 4.3 Its gate (checkable condition, not a vibe)

The staged sequence from the final direction A4 row, in
order, each stage with its own proof before the next stage
starts:

- Stage (a), session-level pill first, server KEPT: the pill
  is acquired once per task instead of once per batch, and
  measured. Pass criteria, from the step 8 spec section 7:
  acquire count per task is 1 in the log; repaints and events
  counted per phase (think-time, act, observe), not as one
  lumped number; the pill shows the right content and clears
  cleanly at task end, with a log or a screenshot as evidence.
  Precondition on stage (a): the CB-10 precondition is met,
  which is the LIQUID flicker probe run (load the plugin,
  reproduce the flicker, count repaints) OR an explicit owner
  deferral recorded with a name and a date. Current status:
  BLOCKED. The step 8 log section 8 records that the probe
  has not run and no deferral is recorded, and the step 9 log
  repeats the block ("Session-level pill: BLOCKED on the
  CB-10 precondition. Do NOT touch the overlay server or the
  pill."). Stage (a) cannot be judged until one of the two
  limbs lands. The CB-10 limb owner is the A4 step-(a)
  worker (final direction section 7).
- Stage (b), driver-owned pill (or compositor-plugin
  indicator), only with proof it shows and clears, including
  no stale or missing pill when the driver dies mid-task.
  Checkable form: a crash drill where the driver is killed
  mid-task (SIGKILL, not a clean finish), after which (i) no
  stale pill remains on screen, verified by screenshot or by
  the compositor state, and (ii) a new task opens its pill
  correctly, verified the same way. The drill is run twice:
  once with the driver killed during think-time, once during
  act. Both must pass.
- Stage (c), delete the server, only then. B3 lift condition,
  final direction section 5: session-level pill measured
  (server kept, CB-10 precondition met), then driver-owned
  pill proves no stale or missing pill on crash. The deletion
  commit itself must also pass: a live broker batch runs end
  to end with the driver-owned pill (observe plus click plus
  type), the pill is visible during the batch and gone
  afterwards, and session_cleanup.py --check exits 0.

### 4.4 Proposed date

The day after the stage (b) crash proof lands, which is
itself after stage (a) is measured. Reason: A4 is three
proofs in sequence, and the first is currently BLOCKED on
CB-10, so no calendar date can be set from this plan alone.
The coordinator sets the A4 date at the step-9 decision
only as a provisional date conditioned on stage (a) and (b)
landing; if either slips, the A4 date slips by the same
number of days. A4 is the last of the three deletions by
gate readiness (see section 6).

### 4.5 Rollback plan

The deletion lands as one commit with an explicit pathspec,
so the rollback is one command:

`git revert <A4-deletion-commit-hash>`

then re-verify, in order, before any live run resumes:

1. `python3 -m py_compile scripts/overlay.py
   scripts/first_action.py scripts/session_cleanup.py`
   exits 0.
2. `python3 -m pytest tests/test_overlay.py
   tests/test_first_action.py -q` passes.
3. `python3 scripts/overlay.py acquire --agent rollback
   --method rollback` shows the pill, and
   `python3 scripts/overlay.py release --agent rollback`
   clears it, verified by status and by sight on a live
   run.
4. One live act-now batch runs end to end with the pill
   visible, and `python3 scripts/session_cleanup.py --check`
   exits 0 afterwards.
5. The push is verified with
   `git ls-remote origin todolist-push`.

If the revert conflicts, the fallback is `git revert
--no-commit` with manual resolution limited to overlay.py,
first_action.py, session_cleanup.py, and the overlay tests,
then the same five verification steps. Note the revert
restores the daemon server, not the driver-owned pill: after
a revert the driver-owned pill code must be disabled or
removed in the same revert commit, or two pill owners will
fight over the screen.

### 4.6 What breaks if it is deleted too early

- The owner goes blind: the pill is the owner's only
  visibility into live runs (final direction A4 row, RTD
  review). Deleting the server before the driver-owned pill
  is proven means live runs happen with no visible
  indicator. The owner cannot tell a run is active, cannot
  tell it apart from the user's own input, and cannot see when it
  ends.
- Act-now refuses every batch: the D1 overlay gate in
  first_action.py refuses loudly (exit 2) when the overlay
  cannot be shown. If the gate is not rewired to the
  driver-owned pill in the same commit, every pointer action
  fails before it starts, and the failure looks like a
  refusal rather than a missing server, which misleads
  diagnosis.
- Stale pill after a driver crash: the daemon's holder
  accounting exists to prevent exactly this (RTD review). A
  driver-owned pill that dies with the driver leaves the pill
  up with no owner, or leaves no pill during action. The
  owner sees a pill for a run that is dead, or sees nothing
  while input is being sent.
- Holder leak: cmd_acquire adds a holder before the daemon
  answers, and removes it on failure (D1 re-check hardening).
  If the deletion removes add_holder and remove_holder
  without a replacement record, session_cleanup.py loses its
  holder check and a leaked holder keeps the pill up after
  the run ends, with nothing to prune it.

## 5. A5: delete one-shot SSH as the default transport (keep it as fallback and recovery)

Pointer: the line numbers in 5.1 describe the tree BEFORE
the B2-4 migrate (HEAD 0400e86). The current post-migrate
numbers live in section 9 (9.2, updated again in 9.4 by the
fix round): broker_code_exec 455, _code_exec_send 563,
oneshot_code_exec 648, send call site 1087, file 1400 lines.

### 5.1 What it removes

A5 as MODIFY, final direction section 1: the word "only" is
REJECTED. This is not deletion of SSH. It is deletion of
one-shot SSH as the DEFAULT transport, in favor of
multiplexed SSH plus broker RPC. What is removed (all line
numbers in this subsection are pre-migrate):

- scripts/s2_flip_live.py oneshot_code_exec(endpoint, program,
  intent), lines 292-322. Every code-exec send for the S2 flip
  class runs as one fresh session-driver invocation over one
  SSH call: the remote command at lines 304-306 is
  `CU_CODE_EXEC=1 python3 <LAPTOP_CU> session -- python3
  <LAPTOP_CU> session-driver`, with LAPTOP_CU at line 70
  (`~/computer-use-wayland/scripts/cu.py`), the
  JSONL action line built at lines 301-303, and the call made
  through self.ssh at line 306. The call site is line 531.
  The transport underneath is already the S0 mux wrapper
  (SSH at line 69, scripts/ssh-laptop-mux.sh), so the per-send
  cost today is one session-driver invocation per send, not
  one fresh SSH connect per send. What dies is the
  one-invocation-per-send loop, not the SSH channel.
- The ssh() helper's one-shot use, scripts/s2_flip_live.py
  lines 209 and following, insofar as it serves
  oneshot_code_exec. The helper itself stays for the
  broker-path sends and for diagnostics.
- Docs that present one-shot SSH as a supported default path
  for sends. The deletion worker must grep the docs for
  one-shot as a default and update them in the same commit.
  What is already gone and needs no deletion:
  first_action.py session_cmd (line 187) and attempt_session
  (line 201) are loud stubs since step 8 (commit 8c6553a);
  the per-batch session spawn is already deleted, and the
  comment at lines 219-222 records that the fresh-SSH
  one-shot path (`cu.py session -- cu.py session-driver`,
  JSONL over stdin) is the VM-side fallback and recovery
  path, documented in the step 8 log section 6, used when
  the broker is down.

What A5 does NOT remove, and must never remove:

- Fresh SSH as fallback and recovery. scripts/ssh_mux.py
  run(), line 303: on a connection-level failure it retries
  once, and ControlMaster=auto self-heals by paying one
  fresh connect (about 4.5s) and becoming the new master.
  The via values "fresh-fallback" and "fresh" (lines 309-310,
  320, 337) are the fallback contract, recorded in the module
  docstring at lines 42-47: "fresh SSH stays as the
  documented fallback AND the recovery path".
- The one-shot driver path as the recovery path: when the
  broker dies, one-shot SSH is how the relay gets restarted
  (step 8 spec section 6.2: `systemctl --user restart
  computer-use-relay.service` over one-shot SSH, then a fresh
  lease, because a restart invalidates every lease with
  broker_changed). The step 8 fallback drill proved this
  path; deleting it would remove the only way back from a
  dead broker.
- ~/workspace/ssh-laptop.sh, the human and agent one-shot SSH
  tool outside the repo. It is not repo code and is not in
  the deletion.
- scripts/sync-installed.py, which uses git and subprocess
  locally (lines 89-90, 168-170) and is not a one-shot SSH
  send path.

### 5.2 What calls it today (callers, with file plus line)

- scripts/s2_flip_live.py line 531: the S2 flip harness
  calls oneshot_code_exec for every send in the flipped
  class. This is the only production caller of the one-shot
  session-driver invocation left in the repo.
- scripts/s2_flip_live.py line 69: SSH is the mux wrapper,
  so the one-shot loop rides on the multiplexed channel
  today. Deleting the loop does not touch the mux master.
- The replacement that already exists: scripts/
  session_remote.py _client_start, line 1456;
  _client_start_with_wait, line 1494 (step 8, waits up to
  300s on busy with 5s polls and a fresh start_id);
  _client_finish, line 1563; the `start` subcommand, line
  1591, and the `request` subcommand, line 1599. Note the
  harness does not call those Python functions: it shells
  the broker CLI subcommands (start, request, result,
  finish) directly, and broker_start has no busy-wait (it
  runs the start subcommand once, fail fast). The broker
  path is the replacement for the one-shot loop, and it is
  already proven: PROBE-S1 (commit 1af7330) ran one live
  batch end to end over the broker from the VM, 12.110s
  versus 28.700s one-shot, 2.37x faster, and step 8 ran a
  live smoke (2 runs, 4 sends) plus a fallback drill on it.
- Tests that touch the one-shot path: tests/test_s0_bundle.py
  (mux plus fallback contract). The deletion worker must run
  it after the deletion and confirm the fallback contract
  tests still pass, since the fallback is kept.

### 5.3 Its gate (checkable condition, not a vibe)

ALL of the following must be true before the deletion
executes:

1. Broker proven on the VM path: DONE, PROBE-S1 (commit
   1af7330), re-confirmed by the step 8 live smoke and
   fallback drill (step 8 log sections 6.1 and 6.2). This
   limb is already met and does not need re-proving, only
   citing.
2. The S2 flip class migrates off oneshot_code_exec: the
   step 9 prototype proves the same sends go through the
   broker for the flipped class, with wall time equal or
   better than the one-shot sends on the same tasks (the
   step 9 gate: snapshot/execute/verify end to end on one
   live ws2 clone chat plus held-out tasks, no double-send
   on retry). Checkable form: the s2_flip_live harness runs
   its send set through the broker client and the log shows
   the same postconditions (dom-value, sent-bubble) passing
   with no oneshot_code_exec call in the run.
3. The fallback is re-drilled after the migration: with the
   broker stopped, a one-shot SSH restart of the relay
   (`systemctl --user restart computer-use-relay.service`)
   brings the broker back, a fresh lease starts a batch, and
   the batch completes. This is the step 8 fallback drill
   repeated on the post-migration code, because the drill
   proves the recovery path that A5 explicitly keeps.
4. The coordinator records the A5 date at the step-9
   prototype decision (final direction step 10). A deletion
   with no date does not execute.

### 5.4 Proposed date

The step-9 decision day itself, if gate item 2 (the S2
class migration proof) has already landed by then; otherwise
the day after that migration proof lands. Reason: A5 is the
only one of the three whose core proof (broker on the VM
path, 1af7330) already exists, so its date is gated only on
the migration proof for the one remaining caller, not on a
new invention. If the migration proof is not in by the
step-9 decision, the date moves with it, one day after the
proof, not on a calendar guess.

### 5.5 Rollback plan

The deletion lands as one commit with an explicit pathspec,
so the rollback is one command:

`git revert <A5-deletion-commit-hash>`

then re-verify, in order, before any live run resumes:

1. `python3 -m py_compile scripts/s2_flip_live.py
   scripts/session_remote.py scripts/ssh_mux.py` exits 0.
2. `python3 -m pytest tests/test_s0_bundle.py -q` passes
   (mux plus fallback contract intact).
3. One s2_flip_live one-shot send runs end to end and its
   V12 check passes (the restored path works).
4. One broker batch runs end to end (the replacement path
   still works after the revert).
5. The push is verified with
   `git ls-remote origin todolist-push`.

If the revert conflicts, the fallback is `git revert
--no-commit` with manual resolution limited to
s2_flip_live.py and its docs, then the same five
verification steps. The revert restores oneshot_code_exec
exactly as deleted, so the flipped class can send again
immediately while the broker migration is re-examined.

### 5.6 What breaks if it is deleted too early

- The S2 flip class cannot send: oneshot_code_exec is the
  only send path for that class today. Deleting it before
  the broker migration proof means the flipped class has no
  way to deliver a program to the laptop at all. Symptom:
  the harness fails with no driver result, or the run
  aborts before the first send.
- The recovery path is mistaken for the deleted path: the
  most dangerous early-deletion failure is not technical but
  procedural, deleting the fallback along with the default.
  If the one-shot driver invocation is removed from the docs
  and from ssh_mux.py's fresh-fallback branch as well as
  from s2_flip_live.py, then a dead broker has no restart
  path (the relay restart command travels over one-shot
  SSH), and the only recovery left is a human logging into
  the laptop. Symptom: broker down, no remote recovery, all
  live work stops until manual intervention.
- A double-send on migration: if the migration routes the
  same send through both the broker and a leftover one-shot
  call during a half-finished deletion, a destructive action
  can execute twice. This is why gate item 2 requires the
  destructive-action no-double-send test from step 9 before
  the deletion, and why the deletion must remove the
  one-shot call site (line 531) in the same commit as the
  function (lines 292-322), never in a later cleanup.

## 6. Ordering: which goes first, and one commit per deletion

Dependency order, not alphabetical: A5 first, A3 second, A4
last.

- A5 first. Its replacement is already proven (broker on the
  VM path, 1af7330; step 8 live smoke plus fallback drill),
  its remaining caller is exactly one function in one file
  (s2_flip_live.py oneshot_code_exec), and it blocks nothing
  else. It is the only deletion whose gate can be met at the
  step-9 decision without new invention. Deleting it first
  also removes the per-send session-driver invocation tax
  from the flipped class before the heavier deletions land.
- A3 second. Its gate is the step 9 prototype (B6 lift) plus
  one live run proving the driver holds scope plus cancel
  latch plus lock (B4 lift). That proof cannot exist before
  the prototype does, so A3 cannot go before the step-9
  decision, and it should not go before A5 either: A5's
  migration proof is part of the same prototype evidence,
  and landing A5 first keeps the two proofs separable (if
  the broker migration regresses, the A5 revert restores it
  without touching the supervisor tree).
- A4 last. Its gate is three proofs in sequence, and the
  first (stage a, session-level pill measured) is currently
  BLOCKED on the CB-10 precondition (flicker probe not run,
  no owner deferral recorded). A4 also depends on the
  driver-owned pill, which is built on the post-A3 driver:
  building a driver-owned pill inside a driver that still
  runs under the supervisor tree, then deleting the tree,
  would force the pill to be re-proven after the tree
  deletion. Deleting A3 first, then proving the driver-owned
  pill on the post-A3 driver, avoids proving the same crash
  behavior twice.

Separate commits is the default, and this plan argues for
keeping it for all three: one deletion per commit, each with
its own date, its own gate proof, and its own revert. The
reasons:

1. Bisection: if a regression appears after the deletions, a
   single combined commit cannot tell the coordinator
   whether the transport (A5), the process tree (A3), or
   the pill (A4) caused it. Three commits give three
   revert points.
2. Different risk shapes: A5 risks a lost send path, A3
   risks a lost stop path, A4 risks lost visibility. A
   combined commit couples a recoverable transport
   regression to an unrecoverable safety regression (a lost
   cancel path while the owner is blind is worse than
   either alone).
3. Different gates, different dates: A5 can land at the
   step-9 decision, A3 the day after the prototype proof,
   A4 only after two more staged proofs. A combined commit
   would have to wait for the slowest gate (A4), which
   delays the two deletions that are ready, or it would
   land early and violate the A4 gate.
4. A3 plus A4 must never combine: they are two different
   visibility mechanisms (the supervisor's indicator pill
   label versus the overlay daemon pill). Deleting both in
   one commit removes the owner's visibility twice over
   with one revert point.

No two of the three should go in one commit. If the
coordinator wants speed, the way to get it is to land the
three commits on consecutive days as each gate clears, not
to merge them.

## 7. UNKNOWNs (not invented, needs a decision or a measurement)

1. The exact driver-held lock, latch, and scope design for
   A3 lives in the step 9 prototype, which is still in
   progress with live proof open. This plan states the
   checkable gate (section 3.3 item 2) but cannot name the
   driver functions that will hold the three, because they
   do not exist yet at HEAD 5a8c29d.
2. The CB-10 precondition for A4 stage (a): the LIQUID
   flicker probe has not run, and no explicit owner deferral
   is recorded. The probe owner is the A4 step-(a) worker.
   Until one limb lands, no A4 date can be more than
   provisional.
3. Whether holders.json stays as the driver-owned pill's
   record or goes with the server (section 4.1). The
   deletion worker must decide this when the driver-owned
   pill is built, because session_cleanup.py reads the file.
4. The measured cancel latency bound for the driver-held
   latch (section 3.3 item 2b). The guardian polls every
   0.05s; the driver-held bound must be stated as a number
   and met on a live run, and no number exists yet.
5. Whether the S2 flip class migration proof (A5 gate item
   2) will land in time for the step-9 decision day, or slip
   it by a day. The step 9 log records live proof still
   open because the clone chats live in Brave/Chrome, not
   Zen.
6. The step 8 spec's UNKNOWN 10 (idle timeout versus
   owner-held session over 300s) is still open and interacts
   with A3: if the broker ends a task after 300s idle, the
   driver-held session scope must be defined against that
   timeout before the tree is deleted, or a long think-time
   loses the session mid-task.

## 8. Evidence for this plan (Lauren Tan standard)

Commands run, all read-only except the plan file itself and
its commit:

- `git rev-parse HEAD` returned 5a8c29de1abe20df881b2aa9e084f8879a33ec2e,
  branch todolist-push, 16:02 +07.
- `git fetch origin main` then `git show
  origin/main:docs/batch11-task2-step8-deletion-spec-20261122.md`,
  234 lines, 16:03 +07.
- `git show e05fc58 --stat` confirmed the final direction is
  one file, improvements/worker-click3-final-direction-log.md,
  1073 lines.
- `git show 4eebc15 --stat` confirmed the step 8 log commit,
  851 lines in improvements/worker-click5-step8-log.md.
- `git show 8c6553a --stat` confirmed the step 8 deletion
  commit (first_action.py session_cmd/attempt_session deleted
  as loud stubs, broker_attempt added).
- Grep sweeps at HEAD 5a8c29d, 16:04 +07: `grep -rn
  "supervis" scripts/` (cursor_session.py supervise line 228,
  guardian line 136); `grep -n "^def \|^class " scripts/
  overlay.py` (613 lines, Daemon line 217, serve line 344,
  _ensure_daemon line 458, cmd_acquire line 494); `grep -rn
  "oneshot\|one_shot" scripts/` (s2_flip_live.py
  oneshot_code_exec line 292, call site line 531);
  `grep -n "def _client_start" scripts/session_remote.py`
  (line 1456, _client_start_with_wait line 1494);
  `grep -rn "SshMux\|ssh_mux" scripts/` (ssh_mux.py run line
  303, fresh-fallback contract lines 42-47); `grep -n
  "unlink" scripts/cancel_hotkey.py scripts/cu.py`
  (cancel_hotkey.py line 222, cu.py line 3179).
- Files read in full: scripts/cursor_session.py (344 lines),
  scripts/ssh_mux.py, the step 8 spec (234 lines), the step 8
  log sections 0, 1, 5, 6, 8, the step 9 log head and tail.
  Files read in part: scripts/overlay.py (entry points and
  serve), scripts/first_action.py (lines 116-230, 970-980),
  scripts/session_remote.py (_launch line 522, client
  functions), scripts/session_cleanup.py,
  docs/layer0-cbexec-contract.md (lines 460-480).
- No code changed in this task. No live run made. No browser
  work done. The only file written is this plan.

## 9. B2-4 correction, 2026-11-23 00:15 +07 (worker B2-4, HEAD ed4fcd4)

Section 8 above stays as the prep task's own record (measured at
HEAD 5a8c29d). This section corrects the live design sections
above to HEAD ed4fcd4, measured again with grep in the B2-4 task.
Originally measured at 0400e86, which was the HEAD at 00:09;
re-checked at ed4fcd4, and no cited file changed between the
two, so every value below holds at ed4fcd4 (councils 1-3 and
the redteam re-measured all of them at ed4fcd4).
No em dash or en dash anywhere in this file. No personal info.

### 9.1 Holder list: 4 becomes 5

Sections 3.2 and 3.3 item 5 above now say five direct owner_lock
holders. The fifth is scripts/sync-installed.py line 115: lock =
session.owner_lock() inside _session_lock, used at line 1259. It
was missed because sync-installed.py loads cursor_session
dynamically with importlib (lines 103-106), so a grep for
`import cursor_session` never finds it. The five, re-measured at
HEAD ed4fcd4:

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

### 9.2 Coordinates re-measured at HEAD ed4fcd4 (old prep value first)

- cursor_session.py, 344 lines, UNCHANGED from prep: prepare 22,
  request_stop 27, restore 39, owner_lock 73, drain_input 87,
  SessionVisuals 93, recover 103, stop 120, guardian 136,
  stop_group 208, terminate_driver 220, supervise 228.
- session_remote.py _launch: prep 522, NOW 520. Fixed in
  sections 3.1, 3.2, 3.3 item 4 above. Client functions
  UNCHANGED: _client_start 1456, _client_start_with_wait 1494,
  _client_finish 1563, start subcommand 1591, request subcommand
  1599. File is 1681 lines.
- cu.py stop_session_on_error request_stop: prep 3458-3459, NOW
  3460. Fixed in section 3.2 above. Other call sites UNCHANGED:
  stop 3105, supervise 3109, recover 3110, request_stop 3114.
- cancel_hotkey.py UNCHANGED: latch_present 59, latch 120,
  cancellation_status 157, cancellation_message 197, resume
  unlink 222, request_stop call 220.
- first_action.py overlay gate UNCHANGED: acquire_overlay 116,
  overlay_visible 150, release_overlay 167, import overlay 978.
- session_cleanup.py UNCHANGED: guardian doc lines 5-6, holder
  check lines 62-69.
- overlay.py DRIFTED HARD: prep 613 lines, NOW 693 lines.
  _log 48, _label_for 62, _prepare 71, _holders_lock 77,
  load_holders 88, save_holders 96, _holder_key 104, add_holder
  113, remove_holder 129, prune_dead_holders 157, session_live
  177, session_label 194, wayland_env 202, Daemon 238 (prep
  217), _spawn_native 245, _close_native 251, _ensure_native 260,
  _show_label 285, apply_holders 309, status_reply 349,
  _monitor 361, serve 377 (prep 344), _daemon_running 463,
  _send_socket 475, _ensure_daemon 489 (prep 458), cmd_acquire
  525 (prep 494), cmd_release 570, cmd_status 587, cmd_stop 608,
  cmd_daemon 625, hold 631, main 659. Any A4 worker must use
  these numbers, not the section 4 numbers above.
- ssh_mux.py run 303, fresh-fallback contract docstring 42-47,
  via values 309-310, 320, 337. File is 403 lines. UNCHANGED.
- s2_flip_live.py at HEAD 0400e86 (BEFORE the B2-4 migrate):
  oneshot_code_exec 388, call site in _send_browser_inner 794
  (prep said 292-322 and 531). AFTER the B2-4 migrate in the
  worktree (uncommitted): broker_code_exec 423,
  _code_exec_send 467, oneshot_code_exec 506, send call site 928.
  File is 1230 lines after the migrate. AFTER the B2-4 fix round
  (section 9.4): broker_code_exec 455, _code_exec_send 563,
  oneshot_code_exec 648, send call site 1087. File is 1400
  lines after the fix round.

### 9.3 What was changed in this file by B2-4

- Sections 3.1, 3.2, 3.3: holder list 4 to 5 (sync-installed.py
  line 115 added, with the importlib note and the internal-use
  exclusion), _launch 522 to 520, cu.py 3458-3459 to 3460.
- This section 9 appended. Section 8 left untouched: it is the
  prep task's evidence record at HEAD 5a8c29d, and it stays true
  as a record of that moment.

### 9.4 Fix round (B2-4 fix worker, 2026-11-23, base ed4fcd4)

- Section 4.1 overlay numbers corrected in place to the
  section 9.2 table (693 lines, Daemon 238, serve 377,
  _ensure_daemon 489, cmd_acquire 525, cmd_release 570,
  cmd_status 587, cmd_stop 608, cmd_daemon 625, hold 631,
  main 659), with a pointer at the top of sections 4 and 5
  to this section.
- Section 5.1 marked as pre-migrate numbers, with a pointer
  to the current numbers in 9.2 above. Section 5.2
  clarified: the harness shells the broker CLI subcommands
  (start, request, result, finish) directly and never calls
  the session_remote.py Python functions _client_start,
  _client_start_with_wait, or _client_finish.
- Importlib range corrected to 103-106 (sections 3.2, 9.1).
- s2_flip_live.py numbers after the fix round: broker_code_exec
  455, _code_exec_send 563, oneshot_code_exec 648, send call
  site 1087, file 1400 lines. The fix commit hash is reported
  to the coordinator in the fix report (a commit cannot
  contain its own hash); the evidence contract and results
  live in the worker log, section 10.
