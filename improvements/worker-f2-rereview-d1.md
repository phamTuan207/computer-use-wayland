# Worker F2 re-review D1: narrow re-check

Reviewer: independent re-checker (D1 only).
Scope: the D1 fix in commit 1c6344e and the D1 test in commit 526919d,
on branch todolist-push, HEAD 526919d at check time (fetched before reading).
Method: read the fix, the test, and `first_action.acquire_overlay`;
ran both suites on the VM; re-ran the re-review's D1 repro against the
fixed code with an isolated BASE in a temp dir; attacked once more.
No code or test file modified, no live driving, no ydotool.

## Verdict: GO

D1 is fixed. Both repro faults leave zero holders, the success path
still returns visible True with the holder present, `hold()` goes
through the fixed `cmd_acquire`, and no other leak path was found.
One theoretical hole remains below the fix's try block (non-dict
socket reply, `scripts/overlay.py:510`), unreachable through the real
daemon, recorded as a hardening note, not a blocker.

## Evidence

### Test runs measured on the VM

- `python3 tests/test_overlay.py`: "all overlay tests pass", exit 0.
  12 test functions (`grep -c "def test"` = 12), including the new
  `test_cmd_acquire_failure_leaks_nothing`.
- `python3 tests/test_first_action.py`: Ran 46 tests, OK, 0.580s, exit 0.
- Both counts match the expected 12 and 46.

### D1 repro, re-run against the fixed code

Isolated BASE in a temp dir (`/tmp/d1_rereview_repro.py`, repo files
untouched, `_ensure_daemon` / `_send_socket` monkeypatched):

- Fault 1, `_ensure_daemon` raises RuntimeError
  ('overlay daemon exited during startup'): `cmd_acquire` raises,
  `load_holders() == {}`, `prune_dead_holders() == []`. PASS, no leak.
- Fault 2, `_send_socket` raises OSError ('socket gone') after a
  healthy ensure: `cmd_acquire` raises, `load_holders() == {}`,
  `prune_dead_holders() == []`. PASS, no leak.

The fix (`scripts/overlay.py:494-511`) wraps `_ensure_daemon`,
`_label_for`, and `_send_socket` in try/except and calls
`remove_holder(args.agent, args.pid)` on failure, then re-raises.
It mirrors `first_action.acquire_overlay`
(`scripts/first_action.py:101-132`), which removes the holder in its
except path. The `remove_holder` call itself is guarded, so a failure
there cannot mask the original error.

### Success path still works

With `_ensure_daemon` returning True and `_send_socket` returning
`{'visible': True, ...}`, `cmd_acquire` returns 0, prints
`"visible": true` with label `Muse via act-now`, and the holder
`{'Muse': {'agent': 'Muse', 'method': 'act-now', 'pid': None}}`
is present in `holders.json`. PASS.

### `hold()` finding

`hold()` (`scripts/overlay.py:572-585`) does NOT call `add_holder`
directly. It shells out to `overlay.py acquire --agent ... --method ...`,
which runs `cmd_acquire`, so it is covered by the fix. Its finally
block shells out to `overlay.py release`. No separate leak class here.

### Extra attack: non-dict socket reply leaks at line 510

Attempt: `_send_socket` returns a valid JSON non-dict (`['not', 'a',
'dict']`). `cmd_acquire` then raises `TypeError: list indices must be
integers or slices, not str` at `reply['label'] = label`
(`scripts/overlay.py:510`), which sits OUTSIDE the try/except.
Result: the holder stays in `holders.json`
(`{'Muse': {..., 'pid': None}}`), `prune_dead_holders() == []`. LEAK
demonstrated with the mocked socket.

Reachability assessment: NOT reachable through the real daemon. Every
reply the daemon sends is a dict: `apply_holders()` returns dict
literals on all branches (`scripts/overlay.py:288-322`), and the
status, stop, and unknown-command replies are dict literals
(`:386-403`). A non-dict reply needs a foreign peer on the socket,
which is chmod 0600 and bound only by the daemon. Sibling code
`first_action.acquire_overlay` does guard with
`isinstance(reply, dict)` (`scripts/first_action.py:125`), so the
one-line hardening is to move `reply['label'] = label` inside the
try, or add the same isinstance check to `cmd_acquire`. Not a
blocker: no component in the repo can produce this trigger.

For completeness, `_label_for` raising inside the try was also
tested: `cmd_acquire` raises, `load_holders() == {}`. PASS.

### Daemon 'acquire' handler and `cmd_release` no-daemon branch

- Daemon handler (`scripts/overlay.py:386-389`): `add_holder` then
  `apply_holders()` with no try around them. If `apply_holders`
  raises, the exception escapes `serve()` (no per-client handler
  try), the daemon dies without sending a reply, and the client sees
  EOF, so `_send_socket` raises and `cmd_acquire`'s except path
  removes the holder from the same `holders.json`. No holder is left
  behind by this path. The pre-existing corrupt-entry crash shape
  (non-dict value in `holders.json` breaking `sorted(...)[1].get`)
  is a daemon robustness gap, not a D1 leak: it predates the failed
  acquire and is not left by it.
- `cmd_release` no-daemon branch (`scripts/overlay.py:517-521`):
  verified by run. With no daemon, it calls `remove_holder`,
  returns 0, prints `{"visible": false, "owner": "none", "holders":
  {}}`, and `load_holders() == {}`. PASS, no leak.

## Observations (non-blocking)

- Over-removal on the CLI path: the fix's `remove_holder(args.agent,
  args.pid)` with pid None removes ALL of the agent's holders
  (`scripts/overlay.py:127-151`, else branch), so a failed CLI
  acquire while a concurrent same-agent run holds the pill would
  drop the live run's holder too. Opposite direction from a leak,
  and concurrent same-agent CLI acquires are not a real pattern
  (`hold()` is per agent, act-now passes a pid). Note only.
- `cmd_acquire` returns 0 even when the daemon replies
  `visible: False` (pill show failed), unlike `acquire_overlay`,
  which raises unless `visible is True`. The holder stays by design
  here (the daemon monitor retries the show), so this is a reporting
  gap, not a leak.

## Bottom line

GO. D1 is fixed and tested, the success path is intact, `hold()` is
covered, and the one remaining hole needs a trigger no code in the
repo can produce. Suggested follow-up, not required for GO: move
`reply['label'] = label` inside the try in `cmd_acquire`, or add the
`isinstance(reply, dict)` guard `acquire_overlay` already has.
