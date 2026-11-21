# Single-session manager for BiDi and Marionette

Date: 2026-11-21. Code: `scripts/session_manager.py`, tests:
`tests/test_session_manager.py`. Stdlib only, no browser needed for
the tests.

## Why this exists

The BiDi and Marionette session limit is shared. One leaked session
blocks everything, and only restarting Zen clears it. Marionette
accepts one client at a time, so two owners racing to open a session
can leave one session open with no owner to close it.

The existing repo code already closes sessions in a finally block:
`scripts/zen_cli.py` closes each `BidiSession` with `session.end()`,
and `tests/puppeteer_bidi.mjs` disconnects in `finally`. What was
missing was the single-owner lock and the hung detection. This
manager adds both, without changing how the existing commands open
their sessions.

## Rules

1. Every client must open its session through
   `SessionManager.session(kind, opener)`. The manager takes the
   file lock first, calls the opener, records the open with
   wall-clock time, yields the session, and in a finally block
   closes the session, clears the record, and releases the lock.
2. Every client must close its session in finally. The manager
   does this for Python clients. The Node side already does it in
   `tests/puppeteer_bidi.mjs` with `browser.disconnect()` in
   finally; the same rule applies there.
3. Never leak. A session that outlives its owner is a bug, not a
   leftover. The close runs even when the work raises, and the
   close method never raises.
4. Only one owner at a time. A second owner gets `SessionBusy`
   after the lock timeout instead of opening a second session.
5. Never kill a real user Zen. Reaping a hung session clears the
   record, and kills a browser process only when the caller passes
   `--kill-browser` and the recorded pid cmdline contains the
   recorded dedicated profile path, the same safety rule as
   `scripts/zen_cli.py`. A real user Zen cmdline does not contain
   a dedicated profile path.

## How it works

- Lock: `fcntl.flock` on `owner.lock` in the state directory
  (default `~/.local/share/agent-computer-use/session-manager`).
  The kernel releases the lock when the owner process dies, so a
  dead owner never holds the slot forever. `acquire()` blocks up
  to 30 seconds by default, polling every 50 ms.
- Close order: the manager tries `delete()`, then `end()`, then
  `disconnect()`, then `close()`, and calls the first one found.
  A `zen_cli.py` `BidiSession` has only `end()`, a raw BiDi or
  Marionette session has `delete()`, a Puppeteer browser object
  would use `disconnect()`.
- State: `session.json` records session id, kind (`bidi` or
  `marionette`), port, owner pid, browser pid, profile, opened
  wall-clock time, and last activity time. `heartbeat()` refreshes
  last activity; call it after each operation on a long session.
- Log: `session-manager.log` gets one JSON line per event
  (`lock_acquired`, `session_open`, `session_close`,
  `session_reaped`, `lock_released`), each with a wall-clock
  timestamp.
- Hung detection: a recorded session is hung when the lock is free
  (no live owner holds it) and either the owner process is dead or
  the last activity is older than the stale timeout (default 300
  seconds). A live owner holding the lock is never hung, however
  old its session is.

## CLI

```
python3 scripts/session_manager.py status
python3 scripts/session_manager.py check     # exit 1 when hung
python3 scripts/session_manager.py reap [--kill-browser]
```

## What the tests prove

Run: `python3 -m unittest tests.test_session_manager -v`.
9 tests, all pass, 1.281 s on 2026-11-21 (suite wall clock
1.492 s including interpreter start).

- Only one owner at a time: a second process holding the lock
  fails with `SessionBusy` after 1053 ms, exit 1, while the lock
  is held, and succeeds after the holder releases it.
- A session is always closed even when the work raises: the fake
  session `delete()` is called exactly once, the state file is
  cleared, and the lock is free again.
- A hung session is detected: a record with a dead owner pid and
  600 s old activity is flagged `owner_pid_dead`, reaping clears
  it, and a later check finds nothing hung.
- A live session is never flagged hung, and a stale record with
  no owner pid is flagged `stale_activity`.
- Log lines are JSON with wall-clock timestamps, and the CLI
  status, check, and reap commands behave as documented.

## UNVERIFIED

Real-browser behaviour is unverified on this machine because no
Firefox or Zen binary exists here: connecting to a live Zen,
Marionette `session.delete` over the wire, and killing a hung
dedicated Zen. The tests use fake sessions and a fake browser
process record, and they prove the lock, the finally close, and
the hung detection, not the browser side. Run the manager against
a dedicated Zen on a machine with Zen installed and record the
timed log before relying on it there.
