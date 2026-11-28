# Broker reliability fix report

Owner: the owner
Branch: `speed-swarm-brokerfix`
Base: `2aa74ff`
Verdict: PROVISIONAL, non-Astra

## Problem 1: terminal window loss

**Root cause, verified.** The prescribed executor command used `nohup kitty ... &`. `nohup` ignores SIGHUP but leaves Kitty in the launching shell's process group. The controlled sleep probe showed that the background `nohup` worker stopped when that group was cleaned up, while `setsid -f` gave its worker a separate session and process group. The controlled Kitty probe matched the campaign evidence: the `nohup` form created no matching Hyprland client after the transient shell exited; `setsid -f kitty --single-instance=no --title brokerfix-probe-setsid` created one. This explains the missing target window. In code, `scripts/cu.py:523` raises `ValueError('window no longer exists')` when the exact address is absent. `scripts/session_driver.py:35-38` treats that generic exception as fatal and stops the session.

**Fix.** Updated the executor brief and added `improvements/terminal-launch-runbook.md`. Executors now launch with `setsid -f`, use a unique title per worker, and verify exactly one matching row via `hyprctl clients -j` before starting the broker session. The title includes the arm and worker ID. The controlled Kitty probe was closed by PID immediately after inspection.

**Driver hardening verdict: UNPROVEN, unchanged.** I did not make window-loss errors recoverable. `window()` is used in checks before actions and in guards around action execution. A vanished target may be discovered before input or after some input has already happened. Treating every matching `ValueError` as retryable could replay a partially completed action. The new relay regression asserts a vanished target without typed transient provenance ends the session and sends no input. This keeps the existing cancellation and refusal provenance rules intact.

**Regression and suite.** `test_vanished_target_window_remains_fatal_without_typed_provenance` in `tests/test_session_continuation.py`. The full `test_session_continuation.py` suite passed, 10 tests.

**Commit pushed.** `cd1dc1c`, `fix: detach executor terminal launches`.

## Problem 2: starts that never become ready

**Measured root cause: UNPROVEN.** The campaign records show three successful start responses with `status=starting`, followed by 83 fast status failures with null state and driver. The relay journal has no restart during those attempts. The missing `timed.py` records omitted the error string, and the referenced lease files are gone. The remaining client or broker error candidates are `invalid_lease_file`, `broker_unavailable`, `broker_changed`, `no_task`, and `invalid_lease`. There is no evidence selecting one as the actual campaign cause.

**Isolation results.** A real in-process `Broker` and the real `_exchange`, client start, lease and status paths with a gated fake driver returned `ok=true,state=starting,driver=starting` for 83 polls. This rules out a spurious leased-status refusal merely because the task is still starting in the tested code path. Separately, intentionally changing a valid lease generation after a successful start produced 83 fast `ok=false,error=invalid_lease` status responses. That proves a generation mismatch can create the same shape, but it does not prove that happened in the measured run.

**Fix and diagnostics.** No start or lease behavior was changed because the measured cause remains unproven. The broker now writes a deduplicated stderr line for broker-handled start and status failures (`scripts/session_remote.py:492-505`, `1213-1231`). Global status includes `last_start_error` and `last_status_error` (`scripts/session_remote.py:859-900`), including the task's error for a failed start. Errors that fail in the client before reaching the broker, such as unreadable lease files, broker unavailability, and generation changes detected before a request, cannot appear in this broker-side record. The measurement wrapper `timed.py` is outside this repository and still drops status error fields, so the next harness revision needs to record them.

**Regression and suite.** `test_client_start_then_83_status_polls_are_ok_while_driver_is_starting`, `test_status_authorization_failure_is_exposed_by_broker_status`, and `test_refused_start_error_is_exposed_by_broker_status` in `tests/test_session_remote.py`. The latter authorization test also exercises the 83-poll generation-mismatch candidate. Full suite passed, 48 tests.

**Commits pushed.** `9df47a8`, `fix: expose broker start and status failures`; `df28da9`, `test: reproduce repeated lease status refusals`.

## Problem 3: first-act screen-change flake

**Root cause, verified from measurements and code.** `scripts/cu.py:1003-1007` marks the frame changed when global mean pixel difference exceeds 3, or an action-point patch exceeds 6. The two measured first acts had a global mean difference of 3.56, above 3, while the whole image was brighter by about 2.8 and stayed pixel-stable before and after. The original `desktop_act()` at line 1485 immediately returned `screen_changed`, even though the action-point patch remained below 6. The transient refusal preserved the session but required another model observation round trip.

**Fix.** `desktop_act()` waits 150 ms, half the observed roughly 300 ms capture interval, and takes one second fresh frame only after the initial `screen_changed` result (`scripts/cu.py:1485-1497`). It proceeds only if the two fresh frames agree under the existing screen and patch thresholds, and action-point patches from the original program observation to the settled frame stay below the existing patch threshold. Otherwise it saves the settled frame and returns the same refusal. It never raises the global threshold and never retries more than once. An accepted retry emits `preflight_retry`; an unsafe retry keeps `preflight_refused`.

**Regression and suites.** Synthetic PIL tests cover a 3.5 mean uniform brightness shift, a moved button at the action point, an unstable second frame, and the one-retry limit. `test_act_diagnostics.py` passed, 20 tests. A session-driver in-process test exercises the stable shift through the real relay and passed as part of `test_session_continuation.py`, 10 tests. The code-exec route was checked: `scripts/code_exec.py:418` calls `CodeExecBackend.act`, which calls shared `desktop_act()` in `scripts/cu.py:2013`. `test_code_exec.py` passed, 32 tests.

**Commit pushed.** `1e055eb`, `fix: retry stable screen brightness preflight`.

## Verification and limits

- No live broker session was started and the relay was not restarted. The driver and broker paths were exercised in-process with fake drivers and mocked desktop backends.
- The controlled Kitty detach checks were the only GUI-process probes. The `nohup` Kitty process was already gone after the shell exited; the `setsid` Kitty window was closed by PID. The test-created fake broker drivers were cleaned by their test harnesses.
- The supplemental `test_session_driver.py` suite ran 28 tests: 21 passed and 7 failed on existing unrelated issues. Five DoctorCliTests expose a local `run` parser shadowing the `run()` helper in `scripts/cu.py:2110,2216-2217`. Two FullRestoreEnvelope typing tests need the absent `native/wtype` binary in this worktree. The broker window-loss continuation regression in `test_session_continuation.py` passed.
- An unattributed Nautilus window appeared during earlier post-test checks and was left untouched because it could be user-owned. It disappeared before the final broker-suite cleanup check at 07:11:53 +07. That final check showed only Jarvis and Zen Browser. No test-created GUI window was identified.
- Detailed wall-clock timings, test failures, and cleanup checks are in `improvements/live-test-log.md`.

## Pushed commits

| Commit | Change |
| --- | --- |
| `cd1dc1c` | Detached executor terminal launch prescription and window-loss fail-closed regression |
| `9df47a8` | Broker start and status failure diagnostics |
| `df28da9` | 83-poll lease-generation candidate regression |
| `1e055eb` | One-shot stable brightness retry with fail-closed checks |
