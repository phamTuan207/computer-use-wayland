# Council Voice 1 verdict: Worker F2 silence fix (code correctness)

Reviewer: Council Voice 1 (code correctness)
Scope: `scripts/first_action.py` (363 lines, read end to end), `scripts/cu.py` wiring (commit 8d1f775), `tests/test_first_action.py`
Branch: todolist-push. F2 commits reviewed: a576e69, afed06e, 8d1f775, 8979b30, 2495382, c2c0a8b, e016cde, 62ad028, 82539bf
Supporting code read: `scripts/overlay.py` (session_live, add_holder, release path), `scripts/cursor_session.py` (guardian, supervise, driver/guard process groups), `scripts/cu.py` (act exit codes, `__main__` handler, desktop_act guards)
Tests run by reviewer: `python3 tests/test_first_action.py` -> 21 tests, all pass, 0.592s

## Verdict: BLOCK

The fallback safety predicate, the one invariant this fix exists to guarantee (D3: never replay a partially run batch), has two independent false positive paths that replay a batch that already acted, plus a fail open liveness check. Those are B1, B2 and B3 below. They must be fixed and retested before this lands. Everything else in the fix is sound, see "Verified correct".

## Verified correct

- (a) Overlay acquire first holds on the main paths. `run()` acquires the overlay at first_action.py:265-271 before `_fresh_observation` and before the session attempt at :280, and the refusal path (acquire raises RuntimeError) returns 2 with no action. Bad actions file is read before overlay (first_action.py:233-242) but no action runs on that path.
- (c) Deadline enforcement works for the wrapper process group. `attempt_session` (first_action.py:112-140) uses `start_new_session=True`, `communicate(timeout=...)`, SIGTERM to the group, a 3s grace period, then SIGKILL. The timeout kill test passes.
- Session success path is mostly sound. `cu.py` returns exit 1 for an act result with ok False (cu.py:2589-2597), except the completed capture error case which returns 0 after the full batch ran, so trusting rc 0 at first_action.py:285-289 is defensible today. See A3 for why it is still fragile.
- `append_log` (first_action.py:177-189) writes 0600 with a trailing newline and checks for a short write. Good.
- Stale observation risk is mitigated downstream: `desktop_act` (cu.py:1465+) re observes and re guards focus, geometry and monitor layout before acting, so the fallback reusing the pre session observation is guarded there.
- `cu.py` wiring (8d1f775) is minimal and correct: one subparser line plus a 3 line dispatch at cu.py:2491-2493 that returns `first_action.run(args)` directly with no extra print.
- No ydotool, no personal info, no em or en dashes found in the new code.

## Blockers

### B1. Timeout fallback replays a batch that already acted (BLOCK)

Evidence:

- first_action.py:153-165: `is_session_start_failure` returns `not session_live` when `timed_out` is True.
- first_action.py:294-299: `run()` checks liveness only AFTER `attempt_session` has already killed the session wrapper.
- first_action.py:112-140: `attempt_session` kills only the wrapper process group (`start_new_session=True` at :122, `killpg(proc.pid, ...)` at :128-138). The guardian and the driver live in their own process groups: cursor_session.py:238 (guard, `start_new_session=True`) and cursor_session.py:280 (driver, `start_new_session=True`).
- cursor_session.py:308-318: on SIGTERM the supervise wrapper runs `terminate_driver(driver)` (SIGTERM to the driver group, 0.6s, then SIGKILL), closes the guard pipe, then `guard.wait(timeout=20)` and recovers the snapshot. The guardian restore unlinks `session.json`.
- overlay.py:146-160: `session_live()` returns False once `session.json` is gone or the indicator socket stops answering.

Why this is unsafe: after a timeout that fires mid batch, the teardown above is the expected path, so `session_live()` False is the normal outcome, not proof that no action ran. A 20s deadline firing during a slow batch (waits, slow app) will normally come back `timed_out=True, live=False`, and the whole batch is replayed from scratch by the fallback at first_action.py:300-312. Double clicks and double typing on a live desktop are the direct consequence. The liveness probe measures "is a session live after we killed it", which cannot distinguish "never started" from "started, acted, and was just torn down". The existing test `test_timeout_no_session_falls_back` (tests/test_first_action.py) encodes this flawed assumption: it asserts fallback on timeout plus live False with no evidence about whether the driver ever started. `FakeOverlay.session_live` always returns False, so the suite cannot catch this.

What must change: a timeout must NEVER fall back on liveness alone. Fall back on timeout only with positive evidence the driver never started (for example, the supervise wrapper never reported the driver registered, or the guardian died before driver start). The simplest correct fix is to remove the timeout branch from the fallback set: timeout means do not replay, report it, and let the agent re observe and decide. If F2 keeps a timeout fallback, it must record a driver started marker from the session attempt itself (before the kill) and consult that marker, not a post kill liveness probe. Add a test that simulates timeout after the driver started (driver acted, then killed) and asserts no fallback.

### B2. Substring predicate matches mid session failures, not only start failures (BLOCK)

Evidence:

- first_action.py:168-170: `if 'Expecting value' in combined: return True` and `if 'cursor guard' in combined: return True`, where `combined` is the whole stdout plus stderr of the session command.
- cursor_session.py:178: the guardian loop raises `RuntimeError('session cursor guard lost')` MID SESSION, after the driver has started and may have acted. The supervise wrapper prints `session guardian died mid-session: ...` to stderr. That text contains `cursor guard`, so this mid session death classifies as a start failure and the batch is replayed.
- cu.py:519 and cu.py:213: `hypr()` parses hyprctl output with `json.loads`, which raises `JSONDecodeError: Expecting value: ...` on corrupt output. `desktop_act` calls `guard()`, which calls `hypr()`, before EVERY action, so a transient hyprctl parse failure on a later action (after earlier actions ran) produces exactly the `Expecting value` signature, and the batch is replayed.
- first_action.py:172: the exact equality branch `_stdout_session_error(stdout) == 'session guardian startup failed'` is dead code in practice. The real supervise error envelope is `{'ok': False, 'error': 'session guardian startup failed: <detail>'}` (cursor_session.py:275, printed by the cu.py `__main__` handler), so the equality never matches and the substring branch at :166 does all the work.

What must change: replace substring matching with a positive start failure signal. Accept only the guardian startup error in the exact form the session command emits before driver start (for example, an error whose text starts with `session guardian startup failed` AND no driver registration happened), or have the session command emit a machine readable marker that distinguishes pre driver from post driver failure. Delete or narrow the bare `Expecting value` and `cursor guard` substring branches: neither string is specific to startup. Add tests for both counterexamples: mid session `session cursor guard lost` must NOT fall back, and a late `Expecting value` from hyprctl after partial completion must NOT fall back.

### B3. Liveness check failure defaults to fallback (fail open) (BLOCK)

Evidence: first_action.py:294-298.

```
live = False
try:
    live = overlay_mod.session_live()
except Exception:
    live = False
```

If the liveness probe itself errors (stale socket, unreadable session file, indicator failure), the code assumes no live session and proceeds toward fallback. The safe default for a predicate whose job is to prove "no action can have run" is the opposite: unknown liveness must mean no fallback. Combined with B1 and B2, this turns every probe error into a replay.

What must change: on any exception from `session_live()`, treat the session as live (or at least as unknown) and do not fall back. Log the probe error in the envelope so the failure is visible instead of silently resolving to False.

## Amends (must fix before landing, not replay hazards)

### A1. Partial overlay acquire leaks a holder (AMEND)

Evidence: first_action.py:68-89. `acquire_overlay` calls `add_holder` at :79, which persists the holder to `holders.json` (overlay.py:102-114), BEFORE `_ensure_daemon()` at :80 and `_send_socket` acquire at :81-82. If the daemon fails to start, the socket fails, or the reply says not visible, the RuntimeError propagates, but `run()` only sets `overlay_acquired = True` after a successful return (first_action.py:263-270), so the `finally` at :327-328 never releases. The leaked holder is only pruned by `overlay.py cmd_status` (overlay.py:484) or `session_cleanup.py:89`, neither of which runs on the act-now path, so the pill and daemon can stay up for a dead process until something else runs status or cleanup.

What must change: clean up on acquire failure. Either have `acquire_overlay` call `remove_holder` in an except path after `add_holder` succeeded, or set the acquired flag before the acquire call and always release in the `finally`. Add a test: daemon start failure leaves zero holders.

### A2. Exceptions escaping `run()` print a second JSON object on stdout (AMEND, sibling of the fixed double print bug)

Evidence: first_action.py:324-336 prints the envelope in `finally`. But several paths raise out of `run()` before returning: `_fresh_observation` raising from `observe_screen` (ValueError or RuntimeError, monitor gone or layout changed), `desktop_act` raising in the fallback at first_action.py:302-312 (PreflightRefusal, RuntimeError), and `acquire_overlay` raising a non RuntimeError (`_send_socket` can raise OSError or ValueError from `json.loads`, `add_holder` can raise OSError). Those propagate through `cu.py main()` to the `__main__` handler at cu.py:2616-2618, which prints a second JSON line `{'ok': False, 'error': ...}` to stdout. A caller doing a strict single JSON parse of stdout then fails. On those paths the envelope already printed also has `path: 'refused'` and no `error` field, which misdescribes what happened. Verified by hand: a NaN deadline raises `ValueError: cannot convert float NaN to integer` out of `communicate`, and a negative deadline raises `TimeoutExpired` immediately, both escaping `run()`.

What must change: `run()` must never let an exception escape. Catch Exception around the body, fill `envelope['error']` and a correct `path`, return 1, and let the `finally` print the single envelope. Validate `--session-deadline-s` as positive and finite before use (reject zero, negative, NaN, infinite). Add tests: fallback `desktop_act` raising, stale monitor observation raising, NaN deadline, each asserting exactly one JSON object on stdout.

### A3. Session success trusts the exit code alone, never the stdout envelope (AMEND)

Evidence: first_action.py:285-289 sets `ok=True` and `completed=len(actions)` on `rc == 0` without parsing stdout. Today this is defensible only because cu.py:2589-2597 returns 1 for an act result with ok False, except the completed capture error case which returns 0 after the full batch ran. That coupling is implicit and fragile: any future cu.py path that returns 0 with ok False becomes a false success in the envelope and the JSONL log.

What must change: parse the session stdout envelope on the success path and require `ok` True, or the completed capture error shape with `completed == len(actions)`, and take `completed` from stdout instead of assuming `len(actions)`. Add a test with rc 0 and a stdout envelope of ok False asserting the run is not reported ok.

### A4. Bad actions file bypasses the envelope and the log (AMEND)

Evidence: first_action.py:233-242 prints an ad hoc JSON object (`{'ok': False, 'error': 'bad actions file: ...'}` or `'actions must be a non-empty JSON list'`) and returns 1 before the envelope exists, so there is no envelope schema, no timings, and no JSONL record for the run. Callers expecting the envelope shape get a different shape.

What must change: route this path through the same envelope (path `refused` or `bad_actions`, with the error) and the same JSONL append, so every invocation produces exactly one envelope and one log line.

### A5. Overlay visibility is checked once, never re checked before the fallback acts (AMEND)

Evidence: first_action.py:68-89 checks `visible is True` once at acquire. The fallback at first_action.py:300-312 then calls `desktop_act` with no re check. If the overlay daemon dies mid run (the exact edge case in the brief), the fallback acts with no pill, violating D1, which states the overlay is a precondition of any pointer action. `release_overlay` (first_action.py:91-104) also swallows failures silently in its outer `except Exception: pass`, and a release failure is recorded nowhere in the envelope or log.

What must change: re check overlay visibility immediately before the fallback `desktop_act` and refuse (return 1, no action) if the pill is not visible. Record a release failure in the envelope instead of swallowing it silently.

## Minor notes (fix if cheap, do not block on these alone)

- M1. `session_error` falls back to the last stderr line (first_action.py:283-286). A trailing warning (for example the Escape binding warning teed by the guardian drain) can be mislabelled as the session error. Prefer the parsed stdout error, and only use stderr when it names the failure.
- M2. `append_log` failure is swallowed silently in the `finally` (first_action.py:329-334), and `run()` never ensures the STATE directory exists before logging, so a missing STATE dir drops the timing record without a trace. Either ensure STATE exists or note the log failure in the envelope.
- M3. `run()` imports `overlay` fresh inside the fallback branch (first_action.py:295) instead of using the same module `acquire_overlay` used, so the injectable `overlay_mod` parameter is bypassed there. Tests only pass because they patch `sys.modules`. Thread the module through for consistency.
- M4. The `--session-deadline-s` default of 20s is fine, but there is no validation anywhere (see A2). A deadline longer than the 120s observation freshness window also means the fallback could act on an observation older than the stated max age; `desktop_act` re guards this, so this is a note, not a defect.

## Test coverage gaps (why the 21 passing tests do not settle this)

All 21 tests pass, but the fakes make the safety predicate untestable as written: `FakeOverlay.session_live` always returns False, `FakeCu.desktop_act` always succeeds, and there is no test for timeout after the driver started, mid session cursor guard loss, a late `Expecting value`, `desktop_act` raising, non RuntimeError acquire failure, daemon death mid run, or the bad actions envelope shape. The fix needs at least: timeout after driver start asserts no fallback, mid session cursor guard loss asserts no fallback, late hyprctl JSON failure asserts no fallback, acquire failure asserts zero holders, and every exception path asserts exactly one JSON object on stdout.

## Bottom line for the parent

BLOCK. Fix B1, B2 and B3 at the root: the fallback decision needs positive evidence the driver never started, not substring matching and not a post kill liveness probe. A1 to A5 are required fixes in the same pass. Re run the 21 tests plus the new counter example tests before re review.
