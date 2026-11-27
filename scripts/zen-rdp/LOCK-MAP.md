# Lock map (I20 substitute)

Every file lock in the computer-use stack, who takes it, what it
fences, and what happens when the holder dies. Written for the I20
substitute decision (RDP lock hardening plus this map) in
`../../improvements/agent-desktop-comparison-20261127.md`. There is
deliberately NO cross-lane interaction lease: the lanes fence
themselves, and this map is the record of how. Paths below are
generic (cache/state roots under the operator's home); concrete
machine paths live in the machine layer, never in this repo.

## The one rule that governs all of them

Every lock here is an `flock()` on an open file description. The
kernel releases an flock when the last fd referencing it closes,
including on process death (crash, kill -9, OOM). A leftover lock
FILE is therefore never stale in the wedging sense: the file may
remain on disk with an old holder record in it, but the next
acquirer succeeds immediately. What can go wrong instead:

- **Inherited fd.** A child process that inherits the lock fd keeps
  the flock alive after the parent dies. Defences: `O_CLOEXEC`
  (RDP lock, relay lock) or not spawning children while holding.
- **Unlink race.** Deleting the lock file while it is held lets a
  second acquirer create a fresh inode and lock that instead: two
  holders, no error. Defences: never unlink a lock file (all lanes
  here keep the file), plus the RDP lock re-checks the path inode
  after acquiring and retries if the file was replaced.
- **Stale holder record.** File content naming a dead pid misleads
  diagnostics, never acquisition. The RDP lock records pid +
  process start time and classifies the record (alive / dead /
  pid reused) in its refusal message.

## The locks

| Lock file (generic location) | Taken by | Fences | Mode | Holder record | On holder death |
|---|---|---|---|---|---|
| RDP drive lock: path from `--lock-file` / `RDP_LOCK_FILE` (machine layer chooses it) | `rdp_client.py` `RDPClient._acquire_lock` | One RDP drive against the browser session at a time (RT-23 single-drive fence) | `LOCK_EX\|LOCK_NB`, refuse fast | `pid=N start=T at=ISO` in the file; drive report carries `lock.holder_pid` | flock auto-released; record stays as stale text until next holder overwrites |
| `desktop.lock` in the agent-computer-use cache dir | `scripts/cu.py` `locked()`; also taken blocking by `cursor_session.drain_input()` | One desktop-driving operation at a time (the shared seat) | `LOCK_EX\|LOCK_NB` in `locked()` (refuse fast); blocking `LOCK_EX` in `drain_input()` (wait for in-flight input to finish) | none | flock auto-released; file persists |
| `cursor.lock` in the same cache dir | `scripts/cursor_session.py` `owner_lock()` | One automation session owner (also held by plugin activation) | `LOCK_EX\|LOCK_NB`, refuse fast | none | flock auto-released; file persists |
| `zen_dom.lock` in the agent-computer-use cache dir (env `ZEN_DOM_LOCK` overrides) | `scripts/zen_dom.py` session enter; `scripts/zen_cli.py` BiDi session init (same path, shared fence) | One remote (WebDriver/BiDi) session per browser instance; both lanes share this one lock so they exclude each other | `LOCK_EX\|LOCK_NB`, refuse fast | none (file opened `w`, truncated) | flock auto-released; note the browser-side session slot is separate: a leaked browser session is cleared only by a browser restart, which the zen_dom error message says |
| `holders.lock` in the overlay cache dir | `scripts/overlay.py` `_holders_lock()` | Short critical section around the pill holders file (read-modify-write) | blocking `LOCK_EX`, held for milliseconds | n/a (mutex, not ownership) | flock auto-released; a crashed holder mid-section can leave the holders file half-updated, which `load_holders()` tolerates by returning empty on parse failure |
| `relay.lock` next to the relay socket | `scripts/session_remote.py` `UnixSocketServer.bind()` | One broker/relay process per socket | `LOCK_EX\|LOCK_NB`, refuse fast; `O_NOFOLLOW\|O_CLOEXEC`, mode 0600, regular-file + owner check | none | flock auto-released; the socket file itself is probed for liveness on next bind |

Thread-level `threading.Lock`/`RLock` uses (overlay state, relay
broker internals) are in-process only and are not part of this map.

## What does not take a lock (known gaps, by decision)

- **No Zen lane takes `desktop.lock`.** The RDP, BiDi, and
  Marionette lanes can run while a desktop operation holds the
  shared seat. This is the gap the rejected I20 lease would have
  closed; the adopted substitute fences each lane against itself
  and records the map instead. No interleaving incident is
  recorded. Revisit only with one.
- **The RDP drive lock is opt-in.** `rdp_client.py` takes it only
  when `--lock-file` / `RDP_LOCK_FILE` is set. The machine-layer
  wrapper for owner drives MUST set it (see README, machine layer
  section); throwaway/test drives may omit it.
- **The pill holders file is not an ownership lock.** It is a
  reference-counted display fence with its own short mutex
  (`holders.lock` above); it never blocks input by itself.

## RDP lock hardening (this change)

- Holder identity: `pid + /proc start time + timestamp` recorded
  on acquire; refusals name the holder and classify it alive,
  dead (stale record), or pid-reused. Legacy bare-pid records
  still parse.
- `O_CLOEXEC`: the lock fd is never inherited by child processes.
- `O_NOFOLLOW`, mode 0600, regular-file + same-owner check on
  open (same fence as `relay.lock`).
- Inode re-check after flock: if the file was replaced during
  acquisition, drop and retry (bounded) instead of holding an
  unlinked inode.
- Attach failure after acquisition releases the lock (the raw fd
  has no finalizer; before this change a failed connect wedged
  the fence for the life of the importing process).
- Tests: `test_lock.py` (record round-trip, liveness classes,
  live-holder and stale-record contention messages, stale content
  not wedging, release-on-failed-attach, CLOEXEC, symlink refusal,
  replaced-inode detection).
