# Envelope validator fix: distinct invalid_arg_type error (19/11 12:16-12:24 +07)

Worker: Luna 6 Max (envelope-validator fix worker). Owner: the owner.
Report to the resume coordinator. Main stays FROZEN.

## Decision implemented

G1 proved the Layer 1 block root cause in-process: `_validate_envelope`
(scripts/session_remote.py:348-357) required every arg to be a string and
mislabeled ANY non-string arg as `unsupported_command`. The executor sent
`--pid` as a JSON integer; the G1 Codex run took 260s to reach that
blocker. The coordinator decided: implement a DISTINCT error for
non-string args so the failure is diagnosable instantly.

Error name chosen: `invalid_arg_type`.

## Change (commit e6784ab, origin speed-swarm, ls-remote verified)

`scripts/session_remote.py` `_validate_envelope`: the old combined check
is split in three, in this order:

1. args not a list, or empty: still `unsupported_command` (unchanged).
2. any arg not a string: `BrokerError('invalid_arg_type',
   'driver arg {index} must be a string, got {type}: {value}')`.
   The envelope is still REJECTED, only the error label changes.
   The value repr is truncated to 80 chars.
3. args[0] not on the allowlist: still `unsupported_command` (unchanged).

Live example, in-process: `['a11y', 'query', '--pid', 1234]` returns
error `invalid_arg_type`, message `driver arg 3 must be a string, got
int: 1234`.

`tests/test_session_remote.py`: new class `ValidateEnvelopeArgTypeTests`
(4 tests): int --pid gives `invalid_arg_type` naming 1234 and int;
string --pid is accepted; a11y query/observe/ground with string args
are accepted; unknown string command still gives `unsupported_command`.

## Regression tests (4 suites, before vs after)

Before: 2026-11-19 12:17:49 to 12:18:16 +07, 27s wall. 129 tests:
test_session_remote 49 OK, test_session_driver 28 FAILED (5 failures),
test_act_diagnostics 20 OK, test_code_exec 32 OK.

After: 2026-11-19 12:19:29 to 12:19:56 +07, 27s wall. 133 tests
(129 + 4 new): test_session_remote 53 OK, test_session_driver 28
FAILED (5 failures), test_act_diagnostics 20 OK, test_code_exec 32 OK.

Sorted FAIL/ERROR diff: EMPTY. Identical sha256
9d2bf0e6a73b02020e951f5789e689efb7b37ee6242e4b64029b18460d44d0dd.
The 5 failures are the pre-existing test_session_driver.DoctorCliTests
failures (base_exception_from_probe, first_failure_skips_second_probe,
long_crlf_probe_error, remote_success_keeps_schema,
second_probe_failure_after_first_success), unrelated to the validator.

The 4c2118a a11y acceptance test
(test_broker_handle_accepts_a11y_and_rejects_unlisted_command) passes
post-change, 0.246s, OK.

## Relay restart (G0 lesson)

The relay at probe time was STALE: started 12:00:32 +07, MainPID 97108,
started_git_head 0db0a43 (pre-merge HEAD). Restarted 12:21:10 +07,
4s wall, MainPID 111176, active, started_git_head
e6784abe4e7470339756596f0eee5991d15b6e8b, broker idle, clean env.
No drop-in exists: the pick4.conf drop-in from 11:37 is gone (lost in
the 12:00 restart), so CU_PICK4_FASTPATH is NOT set on the current
relay. Flagged for the coordinator; the restart preserved the clean env
as found, no flags were set or removed by this worker.

## Live verification (bogus-lease probe, no session, no state touched)

Probe: /tmp/envelope-fix-20261119/probe-envelope.py, through the relay
socket with session_remote._exchange. Validation runs BEFORE lease
authorization in broker._request, so a request with no valid lease
proves the validator verdict without starting a session.

Before restart (stale relay, started_git_head 0db0a43), 12:20:42 +07:
int --pid returned `unsupported_command`, string --pid returned
`no_task`, unknown string command returned `unsupported_command`.
The old mislabeling is proven live, not just in-process.

After restart (fix commit), 12:21:13 +07, all 4 checks PASS:
- int --pid returns `invalid_arg_type` (0.000s).
- string --pid passes validation and fails later at authorize with
  `no_task` (no task active), proving acceptance.
- unknown string command still returns `unsupported_command`.
- broker still idle, next_sequence still 1, no task started.

No live broker session was needed. No desktop windows were opened.
Desktop clean at finish: Jarvis only (hyprctl --instance clients).
Broker free. Relay left clean-env on e6784ab.

## Verdict

SUCCESS (PROVISIONAL, non-Astra). The validator fix is implemented,
regression-tested with zero diff, committed, pushed, relay-restarted,
and live-verified through the relay socket before and after the
restart.

## What remains open

- Sidebar-item precision probe (the G1 re-probe query matched the
  window frame, not the sidebar Home row).
- The pick4.conf drop-in is gone; if CU_PICK4_FASTPATH=1 is still
  wanted on the relay, the coordinator must re-create it and restart.
- The 5 pre-existing test_session_driver.DoctorCliTests failures.
- VM live-test-log has watchdog-resume entries the repo log lacks;
  coordinator to merge logs as at 08:20 (pre-existing note).
