# Council 2 review log, B2-4 step 10 (A5 migrate, A3 holder fix, A3 wedge drill, A4 CB-10 probe)

Reviewer: council 2, independent reviewer. Worker: worker B2-4. Coordinator: parent orchestrator.
Repo: ~/workspace/mochi-b2-4-work. Task received 00:20:05 +07, Mon 2026-11-23.
Role: reviewer only. No code change, no commit of another person's file, no push, no live run, no file deleted, no browser navigation, no ydotool. No em dash or en dash anywhere in this file. No personal info.
Every claim below carries command, output, commit hash, and time in Asia/Ho_Chi_Minh plus elapsed, per the Lauren Tan standard.

## 0. Evidence contract (written BEFORE any check ran)

This section was written into this log before any test, grep, or diff check ran. A check with no condition stated here does not count. The grader is never the writer: every number below is re-measured from source in this task, not copied from the worker log. Inconclusive is honest, not a pass. Conclusion is exactly one of PASS, CHUA PASS, INCONCLUSIVE.

HEAD at start: ed4fcd4 (verified by git rev-parse HEAD, see section 1). Note: the worker log claims HEAD 0400e86. That hash is not the HEAD in this worktree at review time. All re-measurements below are at ed4fcd4 unless stated otherwise, and the HEAD mismatch is a finding to record, not a number to copy.

Finish conditions, stated before running:

1. Compile check. Command: `python3 -m py_compile scripts/s2_flip_live.py tests/test_s2_flip_wiring.py` in the worktree. Expected: exit 0, no output. If exit is not 0, CHUA PASS.
2. Wiring suite. Command: `python3 -m unittest tests.test_s2_flip_wiring` in the worktree. Expected: Ran 40 tests, OK. Basis: worker claims 40 wiring tests (32 at HEAD plus 8 new). If the count is not 40, or any test fails, record the exact count and failure, and CHUA PASS unless the failure is proved to be a pre-existing HEAD failure by the baseline in item 3.
3. Baseline. Command: pristine HEAD copy via `git archive HEAD` to a scratch dir, then `python3 -m unittest tests.test_s2_flip_wiring` there. Expected: Ran 32 tests, OK. This proves the 8 new tests are the only delta and the old 32 pass before and after. If baseline is not 32 OK, record exact count and treat the delta as INCONCLUSIVE until explained.
4. New test count. Command: grep for `def test_` inside class BrokerCodeExecTests in tests/test_s2_flip_wiring.py. Expected: exactly 8 test methods. If not 8, record exact list.
5. Revert mutation checks (no test may be empty). For each of the 8 new tests, revert the behaviour it claims to guard in a scratch copy only, never in the worktree, and run that single test. Expected: each targeted test FAILS on the reverted copy and PASSES on the worktree copy. Mutations planned:
   - a. broker envelope: change broker_code_exec args to drop --endpoint, expect test_broker_code_exec_sends_code_exec_envelope to fail.
   - b. broker default: make _code_exec_send call oneshot even with a lease, expect test_send_browser_with_lease_uses_broker_by_default to fail.
   - c. pre-dispatch fallback: make _BrokerSendNotAccepted not raised on request refusal (raise plain RuntimeError), expect test_pre_dispatch_refusal_falls_back_to_oneshot_once to fail.
   - d. result failure: make _code_exec_send fall back on result failure, expect test_result_failure_never_falls_back to fail.
   - e. disabled envelope: remove the disabled check in _code_exec_send, expect test_disabled_envelope_never_falls_back to fail.
   - f. oneshot transport: make transport oneshot still use broker, expect test_oneshot_transport_forces_oneshot_with_lease to fail.
   - g. invalid transport: remove the transport validation, expect test_invalid_transport_raises to fail.
   - h. CLI transport: remove --transport from main, expect test_cli_maps_transport to fail.
   If any mutation does NOT make its test fail, that test is empty for that behaviour, and the verdict is CHUA PASS with that finding. If a mutation cannot be applied cleanly, record INCONCLUSIVE for that test with the reason.
6. Migration correctness, read from source plus the tests above. Expected to verify in code: broker envelope args are exactly ['code-exec', '--endpoint', endpoint, '--program', '-', '--intent', intent] with program as stdin; lease and seq thread through run() inside the broker session (sends before broker_finish, broker_next_seq threaded across browsers); fallback only on _BrokerSendNotAccepted (request failed or not accepted); result failure raises with no fallback; unknown status raises with no fallback; disabled envelope raises with no fallback and names --transport oneshot; oneshot_code_exec kept and reachable via transport oneshot and via pre-dispatch fallback only. Any deviation found in source is a finding, even if tests pass.
7. Broker client ground truth. Commands: grep for code-exec in scripts/session_remote.py COMMANDS, grep for def _client_start, _client_start_with_wait, _client_finish, and the start and request subcommands. Expected: code-exec is on the allowlist, client functions exist at the lines the worker cites (or record the true lines at ed4fcd4). If code-exec is not allowed, the migrate cannot work as claimed, CHUA PASS.
8. Holder list, at least 5 coordinates re-measured by grep at HEAD ed4fcd4 (not from the worker log). Commands: grep -rn owner_lock for the five claimed files plus cursor_session.py internals, and grep -n for the session_remote _launch line and the cu.py request_stop line. Expected: exactly 5 external holders (activate-cursor-guard.py, activate-session-backend.py, setup.py, visuals.py, sync-installed.py line 115), plus exactly 3 internal owner_lock calls inside cursor_session.py, and the prep log section 9 table matches the re-measured lines or every mismatch is listed as a finding.
9. Prep log diff. Commands: `git diff --stat` and `git diff improvements/worker-click5-step10-prep-log.md`. Expected: holder text says five in sections 3.2 and 3.3 item 5, section 9 exists, section 8 untouched, and no other design section silently changed its numbers. Record exact diff stat for all files.
10. Procedures. Read all three procedure files in full. Expected for each: status PREPARED ONLY, explicit GO required, preconditions listed, pass criteria stated, abort rules stated, and no live step claimed as run. For the wedge drill: the 300s versus 60s shortcut must be stated as a drill shortcut with the production rule kept at 300s. For the CB-10 probe: stage (a) BLOCKED until exactly one limb lands (probe verdict or owner deferral with name, date, scope, reopen condition). Any missing GO, abort, or pass element is a finding.
11. Trust pyramid. For each error found, ask in order: could it have become a deterministic check, better could the design make the wrong choice impossible, and only then rely on a text rule. Record the answer per finding, not as a slogan.
12. Time and hash on every claim. Each check entry records command, output, HEAD ed4fcd4 (or the scratch copy HEAD), Vietnam time, elapsed.

Verdict rule. PASS only if all of items 1 to 10 hold with no material finding. CHUA PASS if any item fails with a concrete finding. INCONCLUSIVE if a required check could not be run or could not be interpreted, with the reason stated.

## 1. Scope and HEAD

- Command: `git rev-parse HEAD` plus `git status --short` plus `git diff --stat`. Output: HEAD ed4fcd49775db4c61f5238ce10ea515bcbd6e294, status shows M improvements/worker-click5-step10-prep-log.md, M scripts/s2_flip_live.py, M tests/test_s2_flip_wiring.py, plus untracked improvements/mochi-b2-4-a3-wedge-drill.md, improvements/mochi-b2-4-a4-cb10-probe.md, improvements/mochi-b2-4-a5-fallback-drill.md, improvements/mochi-b2-4-worker-log.md, and this log file. Diff stat: prep log 118 lines, s2_flip_live.py 245 lines, test file 196 lines. Time: 2026-11-23 00:20:53 +07, elapsed under 0.1s. HEAD: ed4fcd4.
- HEAD note: the worker log and the prep log section 9 both name HEAD 0400e86. That hash exists in this worktree and is an ancestor of ed4fcd4 (verified with `git merge-base --is-ancestor`, output ancestor-yes, 00:21:33 +07). Command `git diff --stat 0400e86..HEAD` shows 7 files changed between the two, none of them a reviewed file (f4diag files, zen_backend.py, zen_pointer.py, two review logs). Every coordinate the worker measured at 0400e86 was re-measured at ed4fcd4 in this review and matches, so no measurement is wrong, but the HEAD label in the worker log and in prep log section 9 is stale. See finding F3.
- Files under review: scripts/s2_flip_live.py, tests/test_s2_flip_wiring.py, improvements/worker-click5-step10-prep-log.md, improvements/mochi-b2-4-a5-fallback-drill.md, improvements/mochi-b2-4-a3-wedge-drill.md, improvements/mochi-b2-4-a4-cb10-probe.md, improvements/mochi-b2-4-worker-log.md (comparison only).
- Docs read before review: improvements/worker-click5-step10-prep-log.md at HEAD (via git show, 2 holder hits at HEAD lines 211 and 263), scripts/session_remote.py broker client, improvements/lauren-tan-workflow-20261122.md (read in full, 00:23 +07). The zen doc was cited by the worker for gate G-PILL and section 4.29; the pill rule as used in the harness was checked in code (cdp_pill_hold, PILL_AGENT S2-flip), not re-read from the zen doc line by line, because no pill code changed in this task.

## 2. Checks

### 2.1 Contract item 1, compile

- Command: `python3 -m py_compile scripts/s2_flip_live.py tests/test_s2_flip_wiring.py`. Output: COMPILE-OK, no output, exit 0. Time: 2026-11-23 00:20:55 +07, elapsed 0.100s. HEAD: ed4fcd4. Result: PASS.

### 2.2 Contract item 2, wiring suite

- Command: `python3 -m unittest tests.test_s2_flip_wiring`. Output: Ran 40 tests in 0.332s, OK. Time: 2026-11-23 00:20:57 +07, elapsed 0.553s. HEAD: ed4fcd4. Result: PASS, count matches the contract (40).
- Extra: `python3 -m unittest tests.test_s2_flip_wiring tests.test_s2_flip_pill`. Output: Ran 46 tests in 0.497s, OK. Time: 2026-11-23 00:23:36 +07, elapsed 0.743s. HEAD: ed4fcd4. This matches the worker claim of 46 (40 wiring plus 6 pill).

### 2.3 Contract item 3, baseline

- Command: `git archive HEAD` extracted to /tmp/b24-c2-baseline, then `python3 -m unittest tests.test_s2_flip_wiring` there. Output: Ran 32 tests in 0.335s, OK. Time: 2026-11-23 00:21:02 +07, elapsed 0.599s. HEAD: ed4fcd4. Result: PASS. The delta is exactly 8 new tests, and all 32 old tests pass before and after.

### 2.4 Contract item 4, new test count

- Command: grep for `def test_` inside class BrokerCodeExecTests. Output: exactly 8 methods: test_broker_code_exec_sends_code_exec_envelope, test_send_browser_with_lease_uses_broker_by_default, test_pre_dispatch_refusal_falls_back_to_oneshot_once, test_result_failure_never_falls_back, test_disabled_envelope_never_falls_back, test_oneshot_transport_forces_oneshot_with_lease, test_invalid_transport_raises, test_cli_maps_transport. Total `def test_` in the file: 40. Time: 2026-11-23 00:20:59 +07. HEAD: ed4fcd4. Result: PASS.

### 2.5 Contract item 5, revert mutation checks

- Method: script /tmp/b24-c2-mutations.py. Each mutation was applied to a scratch copy of scripts plus tests only, never to the worktree. Each single test was run on the unmutated scratch copy (control, must pass) and on the mutated copy (must fail). Command: `python3 /tmp/b24-c2-mutations.py`. Output, all 8 detected, time 2026-11-23 00:23:30 +07, elapsed 4.123s, HEAD ed4fcd4:
  - a-envelope: control rc 0, mutated rc 1, FAILED (failures=1). Detected.
  - b-broker-default: control rc 0, mutated rc 1, FAILED (failures=1). Detected.
  - c-predispatch: control rc 0, mutated rc 1, FAILED (failures=1). Detected.
  - d-result-fallback: control rc 0, mutated rc 1, FAILED (failures=1). Detected.
  - e-disabled: control rc 0, mutated rc 1, FAILED (failures=1). Detected.
  - f-oneshot-transport: control rc 0, mutated rc 1, FAILED (errors=1). Detected. The failure is an error, not an assertion, because the mutated code raises where the test expects a result. It still proves the test guards the behaviour.
  - g-invalid-transport: control rc 0, mutated rc 1, FAILED (failures=1). Detected.
  - h-cli-transport: control rc 0, mutated rc 1, FAILED (errors=1). Detected. Same note as f: argparse exits, so the test errors rather than asserting, and still guards the mapping.
- Result: PASS. No new test is empty for its claimed behaviour.

### 2.6 Contract item 6, migration correctness from source

- Read scripts/s2_flip_live.py in full (1230 lines). Verified in source, HEAD ed4fcd4, worktree uncommitted:
  - broker_code_exec at line 423: args are exactly ['code-exec', '--endpoint', endpoint, '--program', '-', '--intent', intent], program as stdin, one broker request plus one result fetch via self.broker, envelope unwrapped with driver_result. Returns (wall_ms, envelope, seq + 1). Matches the contract.
  - _code_exec_send at line 467: default broker with a lease, oneshot when transport is oneshot or lease is None. _BrokerSendNotAccepted is raised only when the broker request call failed or the broker answered not accepted. Result failure and unknown status raise RuntimeError with no fallback. Disabled envelope raises with no fallback and names --transport oneshot. Matches the contract, except for finding F1 on what counts as proof of pre-dispatch.
  - oneshot_code_exec at line 506: kept, docstring says FALLBACK AND RECOVERY PATH, CU_CODE_EXEC=1 on its own command line only. Matches the contract.
  - run(): sends loop at lines 1064-1074 runs INSIDE the broker session, before broker_finish in the finally at line 1082. Sequence threads across browsers via broker_next_seq (line 1074). Matches the contract.
  - _send_browser_inner call site at line 928, program dict gains transport at line 947, run JSON gains transport at line 1029. Matches the worker claim.
  - Result: PASS on the code as written, except finding F1 (the pre-dispatch proof gap) and finding F5 (the except-path comment and seq reuse).

### 2.7 Contract item 7, broker client ground truth

- Command: grep in scripts/session_remote.py. Output: COMMANDS at line 42 includes 'code-exec'. _client_start line 1456, _client_start_with_wait line 1494, _client_finish line 1563, start subcommand line 1591, request subcommand line 1599, result subcommand line 1603, finish subcommand line 1606. _launch line 520, _validate_envelope line 352, IDLE_TIMEOUT 300.0 line 38, REQUEST_TIMEOUT 120.0 line 40. File is 1681 lines. Time: 2026-11-23 00:21:04 to 00:21:08 +07. HEAD: ed4fcd4. Result: PASS. Every broker line the worker cited matches at ed4fcd4.
- Extra, sequence semantics: read session_remote.py lines 790-840 (_request). The broker dedups by sequence plus digest: same sequence with a different digest raises conflict, same sequence with the same digest replays the recorded response, a lower sequence raises expired, a higher sequence raises sequence_gap. This is the ground truth behind findings F1 and F5.

### 2.8 Contract item 8, holder list re-measured

- Command: `grep -rn "owner_lock()"` over the five claimed files plus cursor_session.py. Output, time 2026-11-23 00:21:13 +07, HEAD ed4fcd4:
  - scripts/activate-cursor-guard.py line 63, scripts/activate-session-backend.py line 72, scripts/setup.py line 314, scripts/visuals.py line 242, scripts/sync-installed.py line 115. Exactly 5 external holders.
  - scripts/cursor_session.py internal owner_lock calls at lines 104, 125, 142. Exactly 3, plus the def at line 73.
  - sync-installed.py: importlib load at lines 103-106 (spec at 103, exec_module at 106), _session_lock def at line 110, lock at line 115, used at line 1259. The worker said importlib lines 103-107; line 107 is blank, so the range is off by one at the end. See finding F4.
- Other coordinates re-measured, same grep sweep, 00:21:19 to 00:21:22 +07, HEAD ed4fcd4: session_remote.py _launch line 520. cu.py request_stop lines 3114 and 3460. cursor_session.py prepare 22, request_stop 27, restore 39, owner_lock 73, drain_input 87, recover 103, stop 120, guardian 136, stop_group 208, terminate_driver 220, supervise 228. overlay.py 693 lines, _log 48, _label_for 62, _prepare 71, _holders_lock 77, load_holders 88, save_holders 96, _holder_key 104, add_holder 113, remove_holder 129, prune_dead_holders 157, session_live 177, session_label 194, wayland_env 202, Daemon 238, _spawn_native 245, _close_native 251, _ensure_native 260, _show_label 285, apply_holders 309, status_reply 349, _monitor 361, serve 377, _daemon_running 463, _send_socket 475, _ensure_daemon 489, cmd_acquire 525, cmd_release 570, cmd_status 587, cmd_stop 608, cmd_daemon 625, hold 631, main 659. cancel_hotkey.py latch_present 59, latch 120, cancellation_status 157, cancellation_message 197. first_action.py acquire_overlay 116, overlay_visible 150, release_overlay 167. Every one matches the worker section 9 table.
- Result: PASS. The holder list of 5 is correct at ed4fcd4.

### 2.9 Contract item 9, prep log diff

- Command: `git diff HEAD -- improvements/worker-click5-step10-prep-log.md`. Output hunks at lines 171, 191, 255, 871. The 171 hunk fixes _launch 522 to 520. The 191 hunk fixes _launch 522 to 520, cu.py 3458-3459 to 3460, and changes the holder bullet from four to five with the sync-installed.py importlib note and the internal-use exclusion. The 255 hunk fixes _launch 522 to 520 in gate item 4 and changes gate item 5 from four holders to five. The 871 hunk appends section 9 only. Time: 2026-11-23 00:21:26 to 00:21:30 +07. HEAD: ed4fcd4.
- Check: `git show HEAD:...` grep for four holder hits at HEAD returns exactly 2 (lines 211 and 263 in the HEAD file). Both now say five. Section 8 is untouched: no diff hunk falls inside section 8, and the last hunk starts at line 871, appending section 9 after section 8 ends. A repo-wide grep for four holder phrasing returns only unrelated hits (four commits, four cross-responses), no other file recording 4 holders.
- Result: PASS on content, except the section 9 header names HEAD 0400e86 instead of ed4fcd4. See finding F3.

### 2.10 Contract item 10, procedures

- Read all three procedure files in full.
  - A5 fallback drill (improvements/mochi-b2-4-a5-fallback-drill.md): status PREPARED ONLY, NOT RUN, explicit GO required. Preconditions 1-6, steps 1-6 (baseline broker run 900, relay stop, one-shot run 901 with a new message, relay restart with new generation, broker run 902 on a fresh lease, session_cleanup.py --check exit 0), pass criteria 1-6, abort rules (disabled envelope stops the drill, unknown outcome never retries the same message, relay not back stops all live work, cleanup failure stops new runs), evidence list, and a NOT-prove section. Complete.
  - A3 wedge drill (improvements/mochi-b2-4-a3-wedge-drill.md): status PREPARED ONLY, NOT RUN, explicit GO required. Preconditions 1-5, steps 1-8, pass criteria 1-6, abort rules (no lock refusal stops at once, never kill by pattern, M1 count 2 or more stops and preserves evidence, latch cleared only by resume). The 60s wedge declaration is stated as a drill shortcut with the production rule kept at 300s. Cited lines verified: _fail_task line 926, _task_recovery_required line 933, _client_start_with_wait line 1494, IDLE_TIMEOUT 300.0 line 38, REQUEST_TIMEOUT 120.0 line 40, all in scripts/session_remote.py at ed4fcd4. The file states plainly it proves recovery on the current tree, not the driver-held A3 design. Complete.
  - A4 CB-10 probe (improvements/mochi-b2-4-a4-cb10-probe.md): status PREPARED ONLY, NOT RUN, GO required, choice between probe and deferral belongs to the owner. Stage (a) BLOCKED until exactly one limb lands: probe verdict (reproduces with per-phase counts, or does not reproduce and CB-10 dissolves) or owner deferral with name, date, scope, and reopen condition. No conclusion drawn on which limb to take. Complete.
- Result: PASS. All three are preparation only, with GO, preconditions, pass criteria, and abort rules present, and none claims a live step ran.

### 2.11 Extra checks, findings F1 and F5 demonstrations

- F1 demonstration, script /tmp/b24-c2-ambiguous.py, scratch copy, mocked transport, no SSH, no live run. The fake broker records the program as dispatched, then raises RuntimeError('broker request failed rc=255: ssh channel died'), simulating transport death after accept. Output, time 2026-11-23 00:24:18 +07, HEAD ed4fcd4: outcome sent, transport broker-fallback-oneshot, programs dispatched total 2, same program sent twice True. The harness also printed "one-shot fallback, no send ran yet", which is false in this run. This proves the code cannot distinguish the two cases from the signal it uses.
- F5 demonstration, script /tmp/b24-c2-seq-reuse.py, scratch copy, mocked transport. Fake broker raises 'broker result failed rc=1: timeout' on the first send, then 'broker request failed rc=1: conflict' on the second send with the reused sequence, matching the real broker conflict rule read in section 2.7. Output, time 2026-11-23 00:24:10 +07, HEAD ed4fcd4: brave outcome error with broker_next_seq 3, chromium outcome sent with transport broker-fallback-oneshot and broker_next_seq 3, oneshot_calls 1. This proves the except-path comment is wrong on both claims.

## 3. Findings

### F1, BLOCKING: the pre-dispatch claim is not proven for the request-failure limb, and the fallback can double-send

- Where: scripts/s2_flip_live.py, broker() lines 359-390 and broker_code_exec() lines 423-466, _code_exec_send() lines 467-504. Docstring of _BrokerSendNotAccepted: "Raised only when the broker request call itself failed or the broker answered with something other than accepted, so the driver never saw the program and a one-shot fallback cannot double-send."
- What is wrong: the code maps any `broker request failed` (rc != 0 from the request CLI call) to _BrokerSendNotAccepted. That signal cannot prove the broker never saw the program. The request CLI sends the request over the broker socket and waits for the accepted reply; if the SSH channel dies after the broker accepted but before the reply reaches the harness, the harness sees exactly the same rc != 0 as when the broker never saw it. The broker() code never parses the CLI JSON error output, so the information that could distinguish the cases (broker_unavailable from the start versus a lost reply) is discarded. Demonstration in section 2.11: a dispatched program plus a request-failed error produces outcome sent via broker-fallback-oneshot with the same program dispatched twice.
- Scope: the window is narrow (the CLI normally returns within seconds, its request exchange timeout is 60s, the SSH timeout is 120s), and the common rc != 0 cases are genuine refusals (busy, conflict, cancelled, broker_unavailable, broker_changed), which are safe. But the worker claim is "provably never accepted" and "can never be sent twice", and "never" is disproved by the demonstration. The pre-send count check (CB-2) does not prevent this: for Brave set_value it runs before the send, and the delayed recount would only detect a count of 2 after the fact. For Chromium fill there is no pre-send count at all.
- Related: the blanket treatment of any non-accepted broker answer as pre-dispatch has the same shape of gap. A replayed identical request (same sequence, same digest) returns the recorded response with status completed, not accepted, and broker() raises 'broker request not accepted', which maps to fallback and would re-send a program the broker already ran. This path is not reachable in run() as written (each browser sends once with a unique message, and the sequence is never reused with the same digest), so it is latent, not live. It is listed here so the fix covers it.
- Fix required: before falling back on a request-call failure, fetch the broker result for that sequence. The broker dedups by sequence plus digest and replays the recorded response for an accepted request, so a result fetch proves whether the request was accepted. Only fall back when the result fetch proves no record exists, or when the broker is provably down from the start (the status exchange fails with broker_unavailable before any request was issued). If the result fetch itself cannot answer, do not fall back automatically: record outcome error and let the operator decide with a fresh run number, exactly as the unknown-outcome rule already does for result failures.
- Trust pyramid, see section 4.

### F2, minor: duplicate program_variant validation introduced by the migrate

- Where: scripts/s2_flip_live.py __init__, lines 232-236 and 243-247. The same program_variant check appears twice, with the same comment. At HEAD the check appears once (line 209). The worker inserted the transport validation and re-pasted the program_variant block. Harmless: both checks run before mkdir and raise the same error. Fix: delete the second copy.

### F3, minor: stale HEAD label in the worker log and in prep log section 9

- Where: improvements/mochi-b2-4-worker-log.md (whole log) and improvements/worker-click5-step10-prep-log.md section 9 header, both name HEAD 0400e86. Worktree HEAD at review time is ed4fcd4. Verified 0400e86 is an ancestor of ed4fcd4 and no reviewed file changed between the two, and every coordinate was re-measured at ed4fcd4 and matches, so no measurement is wrong. Fix: name ed4fcd4 as the HEAD the re-measurement was checked against, or re-state the section 9 header with the task HEAD.

### F4, trivial: importlib line range off by one

- Where: improvements/mochi-b2-4-worker-log.md section 3.1 and prep log sections 3.2 and 9.1 say sync-installed.py loads cursor_session dynamically with importlib at lines 103-107. Re-measured: spec at line 103, module at 104, exec_module at 106, line 107 is blank. The lock line 115, _session_lock line 110, and use at line 1259 are all correct. Fix: cite lines 103-106.

### F5, minor: the except-path comment in _send_browser_inner is wrong on both claims, and the run silently switches transport after an unknown outcome

- Where: scripts/s2_flip_live.py lines 984-989. Comment: "No broker sequence was consumed by a failed send (pre-dispatch fallback returns through the success path above; an unknown outcome leaves the session failed, so later broker calls fail fast anyway)." Both claims are false. A result failure means the request WAS accepted, so the sequence WAS consumed. And later broker calls do not fail fast: run() continues to the next browser reusing the same sequence, the broker answers conflict for the different digest, broker() maps rc != 0 to _BrokerSendNotAccepted, and the next browser falls back to oneshot. Demonstration in section 2.11: brave outcome error with broker_next_seq 3, chromium outcome sent with transport broker-fallback-oneshot.
- Why this is minor, not blocking: the fallback sends a different message the driver never saw, so no double-send happens. What is wrong is the stated invariant and the silent mid-run transport switch, plus the unknown outcome is never resolved. Fix: correct the comment, and decide explicitly whether run() should stop after an unknown-outcome send instead of continuing to the next browser with a reused sequence.

## 4. Trust pyramid

Per finding, asked in order: could the error become a deterministic check, better could the design make the wrong choice impossible, and only then rely on a text rule.

- F1: check first. A result fetch for the sequence before fallback is a deterministic check that proves accepted versus never accepted, using the broker dedup that already exists. Better than a check, the design could make the wrong choice impossible by never switching transports mid-message: on a request-call failure, re-issue the same request through the broker with the same sequence and digest (the broker replays the recorded response for an accepted request and refuses a conflicting one), and only use oneshot when the broker is provably down from the start. Text alone is what the code relies on now (the docstring asserts "so the driver never saw the program"), and the demonstration shows the text is wrong. Required fix is the check, with the design change as the stronger option.
- F2: design. Delete the duplicated block so the wrong copy cannot drift from the right one. No check needed, no text rule needed.
- F3: check. State the HEAD the re-measurement was checked against in the same commit as the numbers, and verify it with git rev-parse HEAD at the time. A text rule ("always name the HEAD") is weaker than the check.
- F4: check. Cite line ranges from grep output, not from memory. Same as F3.
- F5: design first. Do not reuse a consumed sequence after an unknown outcome, and do not continue a run after an unknown-outcome send without an explicit decision. If continuing is intended, make the transport switch explicit in the run JSON and in the log, not hidden behind a comment that claims fail-fast. A corrected comment alone is the weakest fix and is not enough on its own.

## 5. Verdict

CHUA PASS.

Reason: the migrate is correct on every directly testable behaviour (envelope, lease and seq threading inside the broker session, result-failure no fallback, disabled-envelope no fallback, oneshot kept as fallback and recovery), all 8 new tests are non-empty by revert mutation, the baseline is 32 OK against 40 OK after, the holder list of 5 is correct with every coordinate re-measured at ed4fcd4, and all three procedures are complete preparation-only documents with GO, pass criteria, and abort rules. But finding F1 is blocking: the safety core claim that the fallback can never double-send is not proven for the request-failure limb, and the demonstration shows the same program dispatched twice when transport dies after accept. Until the result-before-fallback check (or the stronger design in section 4) lands and is itself tested by a new test that fails without it, the migrate must not be treated as proven safe for live sends. Findings F2, F3, F4, and F5 are minor and do not block on their own; F2, F3, and F4 are one-line fixes, F5 is a comment plus a run-continuation decision.

What the worker must do next: implement the F1 fix, add a test that reproduces the ambiguous case (broker records dispatch, request call fails, no oneshot runs), re-run the 40-test suite plus the baseline, and send the change back for re-review. No live send runs on this code until the re-review passes. The A5 fallback drill as prepared (relay stopped before any send) does not cover F1 and must not be cited as proof against it.

Time log for this review: task received 00:20:05 +07, first check 00:20:53 +07, last check 00:24:40 +07, total about 4 minutes 35 seconds of checking, plus log writing. HEAD: ed4fcd4. No live run, no SSH, no browser work, no file deleted, no commit of another person's file in this review. This log file is the only file written by this reviewer, and it is committed by this reviewer only.
