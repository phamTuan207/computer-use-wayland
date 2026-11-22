# Council 3 review log: B2-4 step 10 (A5 migrate, A3 holder fix, drills, CB-10 probe)

Reviewer: council 3 (independent reviewer, not the worker).
Worktree: ~/workspace/mochi-b2-4-work. HEAD at review start:
ed4fcd49775db4c61f5238ce10ea515bcbd6e294 (ed4fcd4), verified by
`git rev-parse HEAD` at 00:20 +07, 2026-11-23. Worker changes are
uncommitted on top of that HEAD. Reviewer changed no worker file,
ran no live step, made no commit except this log itself, pushed
nothing, deleted nothing. No em dash or en dash anywhere in this
file. No personal info.

Task received 00:20:05 +07, Mon 2026-11-23. Docs read before
review: improvements/lauren-tan-workflow-20261122.md (in full),
improvements/mochi-b2-4-worker-log.md, the full diff of
scripts/s2_flip_live.py, tests/test_s2_flip_wiring.py,
improvements/worker-click5-step10-prep-log.md, the three drill
files, scripts/session_remote.py (COMMANDS line 42,
_validate_envelope 352-378, _request 790-836, _client_with_lease,
main request handling), scripts/session_driver.py relay_commands
(129-200), scripts/cu.py code-exec disabled envelope (3101-3125).

## 0. Evidence contract (written BEFORE any evidence check ran)

Orientation reads above informed what to check. Every number in
sections 1-5 below comes from a check run AFTER this contract was
written into this file. A check with no contract line here does
not count. Conclusion is exactly one of PASS, CHUA PASS,
INCONCLUSIVE. "Inconclusive" is honest, not a pass.

- C1, compile: `python3 -m py_compile scripts/s2_flip_live.py`.
  Expected: exit 0, COMPILE-OK. HEAD ed4fcd4.
- C2, wiring suite: `python3 -m unittest tests.test_s2_flip_wiring
  tests.test_s2_flip_pill`. Expected: Ran 46 tests, OK (40 wiring
  including 8 new BrokerCodeExecTests, plus 6 pill). HEAD ed4fcd4.
- C3, baseline: pristine HEAD copy via `git archive HEAD` to
  /tmp/b24-c3-baseline, same wiring command there. Expected: Ran
  38 tests, OK. Delta 46 minus 38 is exactly the 8 new tests.
- C4, neighbour suites: `python3 -m unittest
  tests.test_session_remote tests.test_code_exec`. Expected: Ran
  163 tests, OK, about 51s. HEAD ed4fcd4.
- C5, holder census: `grep -rn "owner_lock()" scripts/`.
  Expected: exactly 8 call sites, 5 external holders plus 3
  internal calls inside scripts/cursor_session.py itself, and
  the 5 external lines are activate-cursor-guard.py 63,
  activate-session-backend.py 72, setup.py 314, visuals.py 242,
  sync-installed.py 115.
- C6, coordinate re-measurement (at least 5, by grep at HEAD
  ed4fcd4, worktree files): session_remote.py _launch 520,
  _client_start 1456, _client_start_with_wait 1494,
  _client_finish 1563, cu.py stop_session_on_error request_stop
  3460, overlay.py Daemon 238, cursor_session.py owner_lock 73,
  s2_flip_live.py broker_code_exec 423, _code_exec_send 467,
  oneshot_code_exec 506, send call site 928. Expected: every
  re-measured value equals the worker log section 3.3 table.
- C7, mutation checks on a COPY in /tmp (never the worktree):
  M1 make _code_exec_send fall back on result failure too,
  expected test_result_failure_never_falls_back FAILS. M2 remove
  the disabled-envelope check, expected
  test_disabled_envelope_never_falls_back FAILS. M3 change the
  default transport to oneshot, expected
  test_send_browser_with_lease_uses_broker_by_default FAILS.
  M4 drop --intent from the broker envelope args, expected
  test_broker_code_exec_sends_code_exec_envelope FAILS. A
  mutation that flips no test means that test is vacuous.
- C8, diff stat: `git diff --stat`. Expected: s2_flip_live.py
  245 lines changed, test_s2_flip_wiring.py 196 lines changed,
  prep log 118 lines changed, matching the worker claim.
- C9, dash check: `grep -r` for em/en dash in the worker log,
  the three drill files, the prep log diff, and this log.
  Expected: no match.
- C10, stale in-place numbers: grep the prep log sections 4
  and 5 for the old values (overlay 613 lines, _launch 522).
  Expected: record exactly what still says the old value in
  place, so the section 9 correction can be judged.
- C11, broker pre-dispatch proof (read, not run): session_remote
  _request raises before the worker thread starts for every
  refusal path (busy, cancelled, invalid lease, sequence,
  task stopped, driver failed). Expected: no refusal path
  starts the worker thread, so a refused request never saw
  the program.

- 00:22 +07: evidence contract (section 0) written into this
  log before any evidence check ran.
- 00:22:20 +07: C1 compile OK, 0.071s. C8 diff stat matches
  worker claim (245/196/118).
- 00:22:24 +07: C2 wiring suite 46 OK, 0.543s.
- 00:22:29 +07: C3 baseline 38 OK, 0.625s.
- 00:22:31 +07: C4 neighbour suites 163 OK, 51.789s.
- 00:23:25 +07: C5 holder census by grep.
- 00:23:32-00:23:35 +07: C6 coordinate re-measurement, 13 values.
- 00:23:45-00:24:17 +07: C7 mutations M1-M4 on a /tmp copy.
- 00:24:21 +07: C9 dash check clean, C10 stale in-place numbers
  confirmed. Review finished about 00:26 +07.

## 2. Migration correctness (criterion 1)

- C1: `python3 -m py_compile scripts/s2_flip_live.py`, exit 0,
  COMPILE-OK. Time 2026-11-23 00:22:20 +07, elapsed 0.071s.
  HEAD ed4fcd4.
- Envelope: broker_code_exec sends args ['code-exec',
  '--endpoint', endpoint, '--program', '-', '--intent', intent]
  with the program as stdin, byte-identical in shape to the
  envelope oneshot_code_exec builds. 'code-exec' is on the
  broker allowlist: session_remote.py COMMANDS line 42 includes
  it, _validate_envelope lines 352-378 accepts args[0] in
  COMMANDS, relay_commands line 164 allowlists it and unwraps
  the result the same way (driver_result). Verified by read.
- Lease and sequence threading: run() starts the broker session,
  routes, then sends INSIDE the same try block, with
  broker_finish in finally. Each send consumes one sequence
  number through broker_next_seq, threaded across browsers.
  Verified from the diff.
- Send inside the broker session: confirmed, the send loop
  moved from after broker_finish to before it. The old shape
  (sends after finish, outside the session) is gone.
- Fallback only pre-dispatch: _code_exec_send catches only
  _BrokerSendNotAccepted, raised only when the broker request
  call failed or answered not-accepted. C11, from broker
  source: session_remote.py _request raises before the worker
  thread starts for every refusal path (invalid sequence,
  invalid lease, expired, conflict, cancelled, task stopped,
  compositor changed, sequence gap, busy, driver failed,
  lines 790-836). A refused request never saw the program.
- Result failure never falls back: 'broker result failed'
  propagates as RuntimeError, unconverted. Unknown status
  raises with no fallback. Verified by code read and by
  mutation M1 (section 3).
- Disabled envelope never falls back: error_type 'disabled'
  raises with the --transport oneshot recovery path named.
  The disabled shape matches cu.py lines 3123-3125
  (error 'code execution is disabled; set CU_CODE_EXEC=1',
  error_type 'disabled'). Verified by code read and mutation M2.
- One-shot kept as fallback and recovery: oneshot_code_exec
  behavior untouched, only its docstring changed to say
  FALLBACK AND RECOVERY PATH. CLI gains --transport
  broker/oneshot, default broker. Run JSON gains a transport
  field, each send gains program.transport (broker,
  broker-fallback-oneshot, oneshot).
- Relay flag precondition: the worker records CU_CODE_EXEC=1
  in the relay env as a precondition, citing coord-click-6 F3.
  That F3 entry verifies flags.conf in the live relay env on
  22/11 18:32, but the same entry notes the relay has since
  fallen behind HEAD and resume MUST re-verify before run 1.
  So the flag is NOT proven current at review time. This is
  not a code defect: the migrate fails loudly on a disabled
  envelope instead of routing around it. It is a live
  precondition to re-verify before the A5 gate item 2 live
  proof, which still needs a GO in any case. No live send ran
  in this review, and none is claimed.

## 3. The 8 new tests (criterion 2)

- C2: `python3 -m unittest tests.test_s2_flip_wiring
  tests.test_s2_flip_pill`. Output: Ran 46 tests in 0.350s,
  OK. Time 2026-11-23 00:22:24 +07, elapsed 0.543s. HEAD
  ed4fcd4.
- C3: pristine HEAD copy via `git archive HEAD` to
  /tmp/b24-c3-baseline, same command. Output: Ran 38 tests
  in 0.368s, OK. Time 2026-11-23 00:22:29 +07, elapsed
  0.625s. Delta 46 minus 38 is exactly the 8 new
  BrokerCodeExecTests: test_broker_code_exec_sends_code_exec_
  envelope, test_send_browser_with_lease_uses_broker_by_
  default, test_pre_dispatch_refusal_falls_back_to_oneshot_
  once, test_result_failure_never_falls_back,
  test_disabled_envelope_never_falls_back,
  test_oneshot_transport_forces_oneshot_with_lease,
  test_invalid_transport_raises, test_cli_maps_transport.
- C4: `python3 -m unittest tests.test_session_remote
  tests.test_code_exec`. Output: Ran 163 tests in 51.586s,
  OK. Time 2026-11-23 00:22:31 +07, elapsed 51.789s. HEAD
  ed4fcd4. No regression in the neighbour suites.
- Test file is purely additive: 196 insertions, 0 deletions.
  No existing test was modified.
- C7 mutations, each on a fresh copy built from `git archive
  HEAD` plus the worker diff, in /tmp (never the worktree):
  M1 (fall back on result failure too) flips
  test_result_failure_never_falls_back to FAILED, 00:23:48
  +07. M2 (remove the disabled check) flips
  test_disabled_envelope_never_falls_back to FAILED,
  00:24:02 +07. M3 (default transport oneshot) flips
  test_send_browser_with_lease_uses_broker_by_default to
  FAILED, 00:24:06 +07 (test_cli_maps_transport still passes,
  correctly: the CLI argparse default is independent of the
  Harness default). M4 (drop --intent from the broker args)
  flips test_broker_code_exec_sends_code_exec_envelope to
  FAILED, 00:24:14 +07. All four mutations flip their target
  test, so none of the four is vacuous. Honest note: my first
  M2 attempt was invalid (the copy-restore sequence failed
  and the test ran on the M1-mutated copy, passing). I
  discarded that run, rebuilt the copy from scratch, and
  re-ran M2 properly at 00:24:02 with the FAIL result above.
- The remaining 4 new tests were not mutation-checked
  individually (invalid transport, oneshot forcing, CLI map,
  refusal fallback once). The refusal-fallback test is
  exercised indirectly by M1/M4 (both ran it as a control and
  it behaved correctly). This is a stated limit, not a pass
  claim: the 4 mutation-checked tests cover the safety core
  (envelope shape, broker default, result failure, disabled).

## 4. Holder list and coordinates (criterion 3)

- C5: `grep -rn "owner_lock()" scripts/`, 00:23:25 +07.
  Five external holders, exactly as the worker lists:
  activate-cursor-guard.py 63, activate-session-backend.py 72,
  setup.py 314, visuals.py 242, sync-installed.py 115. Three
  internal calls inside cursor_session.py itself: lines 104,
  125, 142, plus the def at line 73. One extra grep hit is a
  comment (activate-session-backend.py line 7), not a call
  site. Total call sites 8, matching the worker claim. The
  fifth holder is real: sync-installed.py loads
  cursor_session dynamically with importlib (lines 103-107),
  holds the lock in _session_lock at line 115, used at line
  1259. A grep for `import cursor_session` misses it, as the
  worker says. Holder list 5 is complete and sufficient.
- C6: 13 coordinates re-measured by grep at HEAD ed4fcd4,
  00:23:32-00:23:35 +07, all equal to the worker log section
  3.3 table: session_remote.py _launch 520, _client_start
  1456, _client_start_with_wait 1494, _client_finish 1563;
  cu.py stop_session_on_error def 3457, request_stop call
  3460; overlay.py _log 48, Daemon 238, serve 377,
  _ensure_daemon 489, cmd_acquire 525, cmd_release 570;
  cursor_session.py prepare 22, request_stop 27, owner_lock
  73, stop 120, supervise 228; s2_flip_live.py
  broker_code_exec 423, _code_exec_send 467,
  oneshot_code_exec 506, send call site 928. File lengths:
  session_remote.py 1681, overlay.py 693, cursor_session.py
  344, s2_flip_live.py 1230. All match.
- C8: `git diff --stat`, 00:22:20 +07: prep log 118 lines,
  s2_flip_live.py 245 lines, test file 196 lines, matching
  the worker claim exactly.
- C9: dash grep over the worker log, the three drill files,
  the prep log, this log, and both code files, 00:24:21 +07:
  no match (exit 1). No em dash or en dash anywhere.
- The worker measured at HEAD 0400e86 while this review base
  is ed4fcd4. The 5 commits between them touch only
  zen_backend.py, zen_pointer.py, f4diag files, and review
  logs (verified by `git diff --stat 0400e86..ed4fcd4`), none
  of the files the worker measured. That is why every
  coordinate still holds at ed4fcd4, but the HEAD label in
  the worker files is still wrong (finding F1).

## 5. The three procedures (criterion 4)

- A5 fallback drill: PREPARED ONLY, GO required from Muse
  tong, stated on page 1. Preconditions 1-6 (migrate present,
  laptop tree synced, relay flag, scratch target, no live
  owner session, pill held). Six steps with exact commands
  (runs 900, 901, 902, relay stop and restart, cleanup
  check). Six pass criteria. Four abort rules, including
  disabled envelope stops the drill and unknown outcome
  never retries the same message. Evidence list names the
  three run JSONs, broker status outputs, relay PIDs, and
  cleanup output. Complete and feasible. One stale label:
  precondition 2 cites VM HEAD 0400e86 (finding F1).
- A3 wedge drill: PREPARED ONLY, GO required, stated on page
  1. Preconditions 1-5 (scratch target, no live owner
  session, pill held, one recovery worker only, deterministic
  SIGSTOP wedge). Eight steps with the recovery order
  (SIGCONT, finish with the owner's lease, SIGTERM then
  SIGKILL by PID only, never by pattern). Six pass criteria.
  Five abort rules, including lock refusal missing means stop
  at once and M1 count 2 or more means stop and preserve
  evidence. The 60s wedge declaration versus the 300s
  production threshold is explicitly recorded as a drill
  shortcut, with the production rule unchanged. It states
  plainly that it proves recovery on the current tree, not
  the driver-held A3 design. Complete and feasible, except
  finding F3 (step 1 lock probe names no exact command).
- A4 CB-10 probe: PREPARED ONLY, GO required, and the
  probe-versus-deferral choice is left to the owner. Stage
  (a) is stated BLOCKED, with no conclusion drawn about
  whether the flicker exists. Probe path is 5 steps in the
  nested venue (owner's option C), deferral path lists the
  4 required items (name, date, scope, reopen condition),
  unlock limbs are exact. Complete and feasible as a
  procedure. Spot checks: docs/decision-2-2-3-hyprglass-test-
  20261121.md exists; the Y6e nested load test and the
  indicator idle proof are cited from other logs, not
  re-measured here; the hyprglass .so backup paths named in
  the file were not found in this worktree (find returned no
  hyprglass.so), so that sub-claim is not confirmed by this
  review. It does not block the procedure, which runs in the
  nested venue and verifies the .so hash before loading.
- All three files state PREPARED ONLY, NOT RUN, name the GO
  they need, and list what they do NOT prove. No live step
  is smuggled in as preparation.

## 6. Trust pyramid (criterion 5)

- Level 2, deterministic checks: the fallback safety is
  enforced by code (exception classification in
  broker_code_exec and _code_exec_send) plus 8 tests, 4 of
  which were mutation-checked to flip. This is the right
  level for a double-send guard, and it holds for every
  broker-generated refusal and every deterministic path.
- Level 1, design: the one residual hole (finding F4, the
  accept-then-response-loss window) could be designed out
  rather than text-ruled: before falling back, probe the
  broker result or status for that sequence, and fall back
  only if the broker does not know the sequence. That turns
  the classification from "the call failed, so it must be
  pre-dispatch" into "the broker says it never accepted".
  Recommended, not required for this review, because the
  window needs a relay crash in the milliseconds between
  dispatch and the accepted response, and the delayed
  recount would catch a double-send after the fact.
- Level 4, text rules: the stale coordinates in prep log
  sections 4 and 5 (finding F2) are exactly what the pyramid
  warns against: prose numbers that drift while the truth
  lives elsewhere. The fix is level 1 or 2 thinking applied
  to docs: one source for coordinates (section 9) with
  pointers from sections 4 and 5, not a second copy of the
  numbers and not silence.
- The duplicate program_variant validation block in
  Harness.__init__ (finding F5) is dead code a lint would
  catch. Cosmetic.

## 7. Findings

- F1, BLOCKING, doc: the base HEAD is misstated in four
  files. The worker log, the three drill files, and prep log
  section 9 all say HEAD 0400e86 (full hash
  0400e869d4275fe58286412f8acde1824b1e3623). The actual HEAD
  at review time is ed4fcd4
  (ed4fcd49775db4c61f5238ce10ea515bcbd6e294). Substance is
  unaffected (section 4: the intervening commits touch none
  of the measured files), but the evidence as written points
  at the wrong base, and the A5 drill precondition 2 tells
  the operator to compare the relay head against 0400e86.
  Fix: correct the HEAD label to ed4fcd4 in the four files,
  or re-verify and re-label at the new base.
- F2, BLOCKING, doc: prep log sections 4 and 5 still carry
  stale coordinates in place, with no pointer to the
  correction. Section 4 (lines 356, 378-388): overlay.py 613
  lines, Daemon 217, serve 344, _ensure_daemon 458,
  cmd_acquire 494, cmd_release 521. True values at ed4fcd4:
  693 lines, Daemon 238, serve 377, _ensure_daemon 489,
  cmd_acquire 525, cmd_release 570. Section 5 (lines
  564-580): s2_flip_live.py lines 292-322 and call site 531,
  pre-migrate numbers; true post-migrate values are
  broker_code_exec 423, _code_exec_send 467,
  oneshot_code_exec 506, call site 928. The corrections exist
  only in section 9 and in the worker log, which admits the
  in-place numbers are stale. A future A4 or A5 worker
  reading section 4 or 5 top-down will use wrong numbers.
  Fix: update the in-place numbers, or put a pointer at the
  top of sections 4 and 5 to section 9. Section 8 is the
  prep task's own evidence record at 5a8c29d and is correctly
  left untouched.
- F3, note, procedure: wedge drill step 1 says a second
  start attempt "must get the lock refusal" and to run it
  "from a separate shell", but names no exact command. A
  start with --wait would wait instead of refusing. Fix:
  name the exact command (broker start, fail-fast default,
  no --wait) in the step.
- F4, note, residual risk: the fallback classification
  treats any request-call failure (rc nonzero, SSH failure,
  timeout) as pre-dispatch. All broker-generated refusals
  provably precede dispatch (section 2, C11). But if the
  relay accepts and starts the worker, then dies before the
  accepted response reaches the client, the harness will
  misclassify the failure as pre-dispatch and the one-shot
  fallback could double-send while the orphaned driver
  completes the first send. Narrow crash window, unmeasured,
  not proven. The delayed recount would detect count 2 after
  the fact but cannot prevent it. Proposed deterministic fix:
  probe broker result or status for that sequence before
  falling back, and fall back only if the broker does not
  know the sequence.
- F5, note, cosmetic: Harness.__init__ validates
  program_variant twice (two identical checks). Harmless
  dead code. Remove one copy.

## 8. Conclusion

CHUA PASS.

The migration code is correct and the tests are real: compile
OK, 46 tests OK against a 38-test baseline, 163 neighbour
tests OK, 4 of 4 mutations flip their target test, holder
list 5 complete, 13 coordinates re-measured and all correct
at HEAD ed4fcd4, all three procedures complete with GO and
abort rules. No live proof exists yet (A5 gate item 2 and the
drills still need a GO), and none is claimed.

It is not a PASS because two doc findings are blocking under
the team's own evidence standard: F1, the base HEAD is
misstated as 0400e86 in four files while the review base is
ed4fcd4; and F2, prep log sections 4 and 5 still present
superseded coordinates as current design truth with no
pointer to the section 9 correction. Both are small, fully
specified, and fixable without touching code. Fix F1 and F2,
and the item passes on the docs; F3, F4, F5 ride as notes,
with F4 as the one design improvement to consider before the
live proof runs.
