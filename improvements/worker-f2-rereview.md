# Worker F2 re-review: silence-weakness fix (council + redteam combined)

Reviewer: independent re-reviewer (council + redteam combined).
Scope: `scripts/first_action.py`, `scripts/overlay.py`, `tests/test_first_action.py`,
`tests/test_overlay.py`, plus the evidence chain in `scripts/cursor_session.py`,
`scripts/cu.py`, `scripts/indicator.py`.
Branch: todolist-push, HEAD 2ba6fc5 at review time (fetched before reading).
F2 fix commits in HEAD: bb8f4e3 (council 1 BLOCK fixes), 91895b3 (overlay A3+A4),
268fcbf (first_action A2+A5+A6), dcabc4c (46 tests), 3eb53b1 (11 overlay tests).
Method: read the code end to end, ran both suites on the VM, traced each
charged item to its raise site, ran concrete repros for the attack items.
No code modified, no live Zen driving, no ydotool.

## Verdict: BLOCK

One remaining defect, in the same class as a charged BLOCK item (redteam A4):
`overlay.cmd_acquire` still leaks a holder when the daemon fails to start or
the socket fails, and the leaked holder carries no pid, so no prune path can
ever remove it. Everything charged against the act-now path itself is fixed
and tested (B1, B2, B3, A1-A5 council; A1, A3, A5, A7, A8 redteam). The fix
must not land until the CLI acquire path gets the same remove-on-failure
treatment `first_action.acquire_overlay` already has. The fix is small
(mirror the try/except plus remove_holder pattern, or pass the pid through),
but it is not done, and the log's claim that A4 is fixed is overstated for
the overlay module as a whole.

## Test runs measured on the VM

- `python3 tests/test_first_action.py`: Ran 46 tests, OK, 0.577s.
- `python3 tests/test_overlay.py`: all overlay tests pass (11 test functions),
  0.097s class of run. `grep -c "def test"` gives 46 and 11.
- F2's claimed counts (46 and 11) are confirmed.

## Blocking defect

### D1. `cmd_acquire` leaks a holder on failure, and it can never be pruned (redteam A4, incomplete)

File: `scripts/overlay.py:494-503`.

```
def cmd_acquire(args):
    holders, _ = add_holder(args.agent, args.method, args.pid)
    _ensure_daemon()
    label = args.label or _label_for(args.agent, args.method)
    reply = _send_socket({'command': 'acquire', ...})
```

`add_holder` runs first with no try/except around the rest. If
`_ensure_daemon()` raises (daemon exits during startup, or no answer in 15s)
or `_send_socket` raises (daemon died between ensure and send), the exception
propagates out of `main()` as a traceback and the holder stays in
`holders.json`. Contrast `first_action.acquire_overlay`
(`scripts/first_action.py:101-132`), which removes the just-added holder in
its except path (council 1, A1 fix). `cmd_acquire` has no equivalent.

Why it never heals: the CLI acquire passes `args.pid`, which defaults to
None (`scripts/overlay.py:580`, `--pid` default None), and `hold()`
(`scripts/overlay.py:561-570`) also passes no pid. So the leaked entry is
`{'Muse': {..., 'pid': None}}`. `prune_dead_holders`
(`scripts/overlay.py:153-171`) only drops entries whose pid is an int above 0,
so it skips this entry forever. The daemon monitor calls `apply_holders`,
which calls `prune_dead_holders`, so it skips it too. `session_cleanup.py`
prunes through the same function, so it cannot heal it either. Only a manual
`overlay.py release --agent Muse` or `stop` clears it.

Consequence: the next daemon spawn shows a pill for the dead run, and after
the next live run releases its own holder, the stale entry keeps the pill up
with no live run, and the daemon never exits (holders never empty). That is
exactly the "pill that stays up after the run ends" shape.

Concrete repro (run from /tmp, repo files untouched, isolated BASE in a
temp dir, `_ensure_daemon` monkeypatched to raise, then `_send_socket`
monkeypatched to raise in a second run):

- Fault 1, daemon start failure: `cmd_acquire` raises RuntimeError
  'overlay daemon exited during startup'; holders after: `{'Muse':
  {'agent': 'Muse', 'method': 'act-now', 'pid': None}}`;
  `prune_dead_holders()` removes `[]`; holders after prune unchanged. LEAK.
- Fault 2, socket failure after a healthy ensure: `cmd_acquire` raises
  OSError 'socket gone'; same leaked `pid: None` entry. LEAK.

Reachability: `overlay.py acquire` is the documented interface for any agent
(`scripts/overlay.py:6-8`, "Any agent ... calls: overlay.py acquire ..."),
and `hold()` uses it. The trigger (daemon fails to start, socket dies) is
the same failure mode this whole fix is about, so it is reachable, not
theoretical.

Required fix: wrap the post-`add_holder` steps in `cmd_acquire` in
try/except and call `remove_holder(args.agent, args.pid)` on failure, the
same pattern as `first_action.acquire_overlay`; add a test that a failed CLI
acquire leaves zero holders. Passing the caller's pid through the CLI path
would also let prune drop a killed run's entry, but the remove-on-failure
is the required part.

## Per-item table

### Council 1

| Item | Status | Evidence |
|---|---|---|
| B1 timeout never falls back | FIXED | `scripts/first_action.py:267-268`, `if timed_out: return False` in `is_session_start_failure` (def at :249). Tests: `test_timeout_never_falls_back`, `test_timeout_after_driver_started_never_replays`, run-level `test_timeout_never_replays` (no desktop calls). |
| B2 prefix classifier, no substrings | FIXED | `scripts/first_action.py:89-90`, `START_FAILURE_PREFIXES`; parsed stdout JSON error only, startswith check. Raise sites verified: `scripts/cursor_session.py:281` raises 'session guardian startup failed' before the driver is spawned; `:293` raises 'driver registration failed' before the 'go' byte is written; the driver only execs when `os.read(gate,2)==b'go'` (`:337`), and supervise closes the gate without 'go' on the raise path, so the driver can never act. The `__main__` handler (`scripts/cu.py:2616-2618`) prints the supervise error as the stdout JSON envelope the classifier parses. Tests: `test_mid_session_guard_lost_never_replays` (stdout and stderr variants), `test_late_expecting_value_never_replays`, `test_bare_cursor_guard_substring_never_replays`. |
| B3 liveness probe removed | FIXED | No `session_live` call remains in `first_action.py` (only a docstring mention of why it was removed). No post-kill probe anywhere on the fallback decision. |
| A1 acquire failure leaks nothing | FIXED | `scripts/first_action.py:101-132`, except path calls `remove_holder(agent, pid)`. Tests: `test_not_visible_refuses_and_leaks_nothing`, `test_daemon_start_failure_refuses_and_leaks_nothing` (both assert `fake.holders == {}`). |
| A2 no exception escapes run(), deadline validated | FIXED | Outer `except Exception` in `run()` fills the envelope and returns 1; deadline check `scripts/first_action.py:379` rejects non-finite, zero, negative, and over-120s values. Tests: `test_nan_deadline_refused_single_json`, `test_negative_deadline_refused`, `test_huge_deadline_refused`, `test_fallback_desktop_act_raises_single_json`, `test_stale_monitor_observation_raises_single_json` (stdout parsed as exactly one JSON object in every case). |
| A3 session success needs the stdout envelope | FIXED | `scripts/first_action.py:330-356`, rc 0 alone is not success; requires `ok is True` or the completed-capture-error shape. `_is_completed_capture` (`:240-247`) matches `is_completed_capture_error` in `scripts/cu.py:1341-1345` field for field. Tests: `test_session_path_rc0_ok_false_not_ok`, `test_session_path_completed_capture_error_ok`, `test_session_path_rc0_empty_stdout_not_ok`. |
| A4 bad actions file via envelope + log | FIXED | `scripts/first_action.py:273-283`, path `bad_actions`, error set, envelope printed and logged by the finally. Tests: `test_bad_actions_file_envelope` (asserts the JSONL line), `test_empty_actions_list_envelope`. |
| A5 overlay re-checked before fallback; release failure recorded | FIXED | `scripts/first_action.py:451`, `overlay_visible` (sync round trip, def at :135) immediately before the fallback `desktop_act`; refusal path sets 'overlay lost before fallback'. Release failure is recorded as `release_error` in the finally. Tests: `test_overlay_lost_before_fallback_refuses`, `test_release_returns_error_on_failure`. |
| M1 stderr tail only when it names a failure | FIXED | `scripts/first_action.py:321-328`, keyword filter ('error', 'failed', 'traceback'). |
| M2 STATE dir created, log failure recorded | FIXED | `scripts/first_action.py:490-499`, `mkdir(parents=True, exist_ok=True)`, `log_error` set on failure. |
| M3 overlay module threaded through | FIXED | `run()` imports overlay once (`:338`) and passes `overlay_mod` to acquire, visible check, and release. No re-import in the fallback branch. |

### Redteam

| Item | Status | Evidence |
|---|---|---|
| A1 prefixes ARE phase evidence | FIXED, reasoning sound | Verified against the source, not assumed: supervise raises both prefixes only pre-driver/pre-go (`scripts/cursor_session.py:281,293`); the driver gate (`:337`) means a gated driver cannot exec. A post-start 'Expecting value' or 'cursor guard lost' can never carry these prefixes, because the session stdout JSON on those paths is the act result, not a supervise raise. No counterexample constructed: the two error paths are mutually exclusive in one supervise run (either the raise happens before 'go', or the driver runs and prints its own result). |
| A2 deadline / lock / grandchild / budget | PARTIAL, not blocking | Deadline clamp is implemented as refusal above 120s (`scripts/first_action.py:379`, test `test_huge_deadline_refused`). The lock-timeout premise is FALSE, verified: `cu.locked()` is non-blocking (`scripts/cu.py:1991-1992`, `LOCK_EX\|LOCK_NB`, raises RuntimeError on contention), so the fallback already fails fast instead of hanging. Whole-run budget is recorded as `target_breached` (total over 30000ms), not enforced; test `test_target_breached_recorded` covers the recording. The SIGTERM-grandchild test was NOT implemented. The reasoning for skipping it is sound for this code: the timeout fallback was removed (B1), so no replay decision depends on driver death, and nothing in the session tree escapes its process group by calling setsid (guardian and driver are spawned with `start_new_session=True` by supervise, and the supervisor finally runs `terminate_driver` before `guard.wait`). An orphan driver would need both the supervisor finally and the guardian cleanup to fail, which is session machinery (F1's domain), not act-now's. No concrete repro with the actual code was constructible. Residual risk noted as amend A-M1 below. |
| A3 show ack propagates | FIXED | `_show_label` returns bool (`scripts/overlay.py:264-286`); `apply_holders` returns visible False with error 'pill show failed' on a failed show (`:288-322`). The ack is real, verified: `Native.command` waits for the exact expected reply ('visible' for show, `scripts/indicator.py:99-104`, `reply` at :82-97 raises on timeout or mismatch), and `indicator.request` requires `b'visible\n'` for show (`scripts/indicator.py:181-184`). `overlay_visible` uses the 'sync' round trip, not 'status'. Tests: `test_show_label_returns_bool`, `test_apply_holders_visible_false_on_show_failure`. |
| A4 per-run holders + prune | PARTIAL, see D1 | Fixed for the act-now path: holders keyed by (agent, pid) via `_holder_key` (`scripts/overlay.py:102-108`); `remove_holder` with a pid removes only that run's entry (`:127-151`); daemon 'release' passes the request pid; `cmd_release` has `--pid`; `prune_dead_holders` is called by `_ensure_daemon` and by `apply_holders`. Tests: `test_same_agent_two_pids_are_independent`, `test_apply_holders_prunes_dead_holders`, `test_prune_dead_pid`. NOT fixed for the CLI acquire path: D1 above. The redteam required fix ("remove the just-added holder when acquire fails after add_holder") was applied to `first_action.acquire_overlay` only. |
| A5 fallback preflight refusals clean | FIXED | Fallback `desktop_act` wrapped in try/except (ValueError, RuntimeError) (`scripts/first_action.py:461-471`), error into the envelope, path stays 'fallback', clean return 1, after-capture still attempted. Tests: `test_fallback_desktop_act_raises_single_json` (RuntimeError) and `test_fallback_desktop_act_raises_valueerror` (PreflightRefusal is a ValueError subclass), both asserting the after-capture ran (`observe_calls` == 2). |
| A6 stale observation | PARTIAL, not blocking | Age plus deadline under 120s is implemented in `_fresh_observation` (`scripts/first_action.py:289-312`, deadline_s parameter) with tests `test_age_plus_deadline_must_stay_under_120` and `test_age_plus_deadline_within_120_is_used`. Up-front scope/backend/window validation was NOT implemented. The reasoning is sound as to safety: the worst case is a wasted session attempt plus a clean refusal (A5 catches the desktop_act refusal into the envelope), never a replay and never a crash, because the fallback only triggers on the start-failure prefixes, which a scope refusal cannot carry. A future-dated `created` passes the wall check but fails desktop_act validation the same clean way. Efficiency gap only. |
| A7 urlbar finding overstated | FIXED | Downgraded to HYPOTHESIS in the rule doc (`improvements/first-visible-action-rule-20261121.md:110`, "HYPOTHESIS, 2/2, not proven") and in the fix log. Discriminating probes are queued for the next live run, not run yet (live driving is out of scope for this review). |
| A8 session-path completed asserted | FIXED | Same fix as council A3 above; completed is taken from the parsed stdout envelope, never assumed to be len(actions). |
| A9 test gaps | PARTIAL, follows A2/A4/A6 | 46 + 11 tests, all green on the VM (measured above). The A9 list is closed except: no SIGTERM-grandchild test (A2), no CLI acquire-failure test (A4/D1), no whole-run budget enforcement test (budget is recorded, not enforced). |

## Attack attempts and outcomes

- Replay path: none found in the act-now path. Tried: timeout with a start-failure prefix in stdout (refused, `first_action.py:267-268` checks timeout first); mid-session guard loss and late 'Expecting value' (both return False, covered by tests); rc 0 with ok False or empty stdout (reported not-ok, no fallback); a second JSON object after the act result (supervise prints no stdout JSON on the normal path; the guardian stdout is a pipe consumed by supervise, not forwarded). The classifier was traced end to end from the raise sites to the `__main__` envelope print.
- Holder leak: ONE found, D1 (`cmd_acquire`, `scripts/overlay.py:494-503`), repro above. The act-now path itself is clean: acquire failure removes the holder, SIGKILL leaves a pid-bearing entry the daemon monitor prunes within one reconcile, and two same-agent pids are independent (tested).
- False-visible claim: none found on the act-now gate path. `overlay_visible` uses the sync round trip with a real show ack, and a failed show returns visible False. Residual reporting gap, see amend A-M2.
- Crash: none found escaping `run()`. The outer except catches Exception on every path, including non-RuntimeError acquire failures and after-capture failures; stdout is exactly one JSON object in all tested exception paths. Only a closed-stdout BrokenPipeError from the finally's print could escape, which is an environment edge, not a code path.

## Amends (non-blocking)

- A-M1 (A2 residual): after a timeout, `attempt_session` SIGTERMs the supervisor group and SIGKILLs after a 3s grace. If the kill lands mid-finally during `guard.wait(20)`, the driver is already terminated (`terminate_driver` runs first in the finally), and the guardian's own cleanup stops the driver group on pipe EOF. No concrete orphan repro exists with the actual code. If F1 ever adds a setsid escape anywhere in the session tree, this needs re-checking.
- A-M2 ('status' reports holders, not the pill): the daemon 'status' reply and `cmd_status` report `visible: bool(holders)` (`scripts/overlay.py:400, 526`). That is "holders exist", not "pill rendered". A stale holder (D1) makes status claim visible True with no pill. Consider making 'status' report the last show-ack result, or renaming the field. Not used as a gate by act-now, so amend only.
- A-M3: `prune_dead_holders` treats PermissionError as dead (`scripts/overlay.py:163`). A pid owned by another user exists but cannot be signalled, and would be pruned while live. Same-user in practice on this machine; consider only pruning on ProcessLookupError.
- A-M4: the pill is re-checked immediately before the fallback acts, but not during `desktop_act` itself. If the daemon dies mid-batch, the tail of the batch acts with no pill until something re-acquires. Fixing that needs a pill check inside `desktop_act`, which is outside the act-now scope; noted as a follow-up.
- A-M5 (trivial): a non-RuntimeError acquire failure returns exit 1 while a RuntimeError acquire failure returns 2 (`scripts/first_action.py:375-377` catches RuntimeError only). Same refusal, inconsistent code. Cosmetic.

## Bottom line

BLOCK on D1 only. The act-now path is clean and its tests prove it; the
overlay module's CLI acquire path still carries the exact leak redteam A4
was about. Apply the remove-on-failure to `cmd_acquire`, add the
CLI-acquire-failure test, re-run both suites, and this should go GO.
