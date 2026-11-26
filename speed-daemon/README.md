# speed-daemon (Method 2, WARM DAEMON) - speed-test 2026-11-23

A persistent sender daemon on this VM. Each send is one IPC call to a warm
Python process; the daemon runs ONE batched mux SSH session per send, and
the laptop-side script does pill + CDP send + V12 + pill release inside
that single session. No per-send Python startup, no per-send SSH master
creation, no cu.py session-driver (so no session-guardian collision).

## Files

- `daemon.py` - the daemon (Unix socket server, serialised sends, heartbeat)
- `send.py` - client CLI (`--ping`, `--status`, `--recipient mei|mochi
  --run N --message "..."`)
- `daemon.sh` - `start | stop | restart | status`
- `watchdog.py` - liveness check: pings the socket, restarts the daemon if down
- `supervisor.sh` - detached loop running watchdog.py every 60s (no cron on this VM)
- `daemon-send.mjs` - laptop-side CDP send (VM copy; installed to /tmp on the laptop)
- `daemon-one-send.sh` - laptop-side batch wrapper: pill acquire+verify,
  node send, pill release+verify (VM copy; installed to /tmp on the laptop)
- `daemon.log` - daemon JSONL log, `daemon.out` - stdout/stderr, `watchdog.log`

## How to use

Start (also the one-command restart after a VM replacement):

```sh
~/workspace/speed-daemon/daemon.sh start
```

Send a message:

```sh
python3 ~/workspace/speed-daemon/send.py --recipient mei --run 9 \
  --message "Test toc do gui tin, lan 9, khong can lam gi. (daemon)"
```

Check it is alive / stop it:

```sh
~/workspace/speed-daemon/daemon.sh status
~/workspace/speed-daemon/daemon.sh stop
```

## Read back (new, 2026-11-23 23:17 +07)

The daemon could SEND to mei/mochi but not READ their replies, so a
reply in their tab looked like silence. `read.py` closes that half.

```sh
python3 ~/workspace/speed-daemon/read.py --recipient mei [--count 5]
python3 ~/workspace/speed-daemon/read.py --recipient mochi [--count 5]
python3 ~/workspace/speed-daemon/read.py --recipient mei --count 3 --raw
```

Files: `read.py` (VM client) + `daemon-read.mjs` (laptop-side CDP read,
installed to /tmp on the laptop, md5-checked and re-pushed when changed).

What it returns: the most recent N assistant messages (role !== 'user',
default 5, oldest-first) from that recipient's tab, verbatim, plus
total bubble count, assistant count, and elapsed time. Exit 0 iff ok.

Limits:
- Read-only: it only fetches /json/list and runs a Runtime.evaluate that
  reads `[data-message-item]` bubbles. It never types, clicks, navigates,
  or modifies the tab, and it acquires no pill (a read is not agent
  control). It never runs cu.py session-driver, so it cannot collide
  with the session guardian.
- Timestamps: the Muse UI shows group timestamps as separators between
  bubbles, not inside them, so per-message `time` is usually null. When
  a bubble carries a `<time>` element, its text and datetime are returned.
- Only messages currently in the DOM are visible. Empty bubbles (no text)
  are filtered out. Text is the bubble's textContent verbatim.
- Independent of the daemon socket: it uses the same mux SSH helper
  directly, so it works even when the daemon is down. Warm-master read
  takes ~1.7s; a cold read (master creation + script push) ~6s.

Tested 2026-11-23 23:17-23:18 +07: mei returned her blind-subagent
replies (dc7e0d0d, ready 21:58, prep done, FREEZE-2 list verified);
mochi returned her brief/template replies plus two new items (her coord
note 3fe02d1 push to main rejected as protected-branch, and her two
missing items: session ID not assigned, rung3-scorers.md not on the
machine).

## How it survives / restarts

1. Supervisor loop (`supervisor.sh start`): a detached loop that runs
   `watchdog.py` every 60s; the watchdog pings the socket and runs
   `daemon.sh restart` when the daemon is down. The supervisor is a
   separate process, so killing the daemon does NOT kill the supervisor.
   NOTE: this VM has NO cron daemon (no crontab/crond, no cron.service)
   and no user systemd bus, so a cron/systemd watchdog is not installable
   here; the supervisor loop is the working equivalent. `watchdog.py`
   itself is cron-compatible (one check per invocation) if cron ever exists.
   Tested 2026-11-23: kill the daemon, supervisor revives it within ~60s.
2. One-command manual restart: `~/workspace/speed-daemon/daemon.sh restart`.
3. Inside the daemon: a heartbeat every 60s checks the SSH master; a dead
   master self-heals on the next call (ControlMaster=auto creates a fresh
   one, ~3.3s once). An SSH rc=255 send is retried once.
4. CAVEAT: a VM replacement wipes the daemon process AND the supervisor.
   After a replacement, run `daemon.sh start` and `supervisor.sh start`.
   There is no way to auto-restart across a full VM replacement from
   inside the VM itself.

## Why there is no warm CDP websocket from the VM

Tested 2026-11-23 ~06:54 +07: CONNECT via the runtime tunnel proxy (port
3130) to 100.70.92.52:22 returns HTTP 200, but CONNECT to
100.70.92.52:9223 / :9224 returns an empty reply (proxy closes it). `ss`
on the laptop confirms why: Chromium/Brave listen on 127.0.0.1:9223 and
127.0.0.1:9224 ONLY (loopback-bound). No VM-side socket can ever reach CDP
directly, so CDP runs ON the laptop (node, loopback) inside the one batched
SSH session. The daemon still bypasses the session guardian because it
never runs cu.py session-driver; sends are serialised by a lock.

## Measured costs (2026-11-23, warm master)

- One mux SSH session (`true`): 0.64-0.94s (n=3). First call after master
  death creates the master, ~3.3s.
- Node probe (composer ground, both tabs): 35-38ms on the laptop.
- Pill acquire/release cycle via SSH: verified, holders {} + visible false
  after release.

## Test results (3 runs, each to BOTH mei and mochi) - measured 2026-11-23 06:57 +07

- 6/6 sends delivered and V12-verified, 0 failures, 0 retries.
- Per-send: mei 1.287s / 1.265s / 1.277s (median 1.277s); mochi 1.521s /
  1.482s / 1.488s (median 1.488s); overall median per-send 1.38s.
- Total per run (both, sequential): 2.81s / 2.75s / 2.77s (median 2.77s)
  vs baseline 18.18s. About 6.6x faster for both, 5.8x per send.
- Breakdown per send: IPC 0.0-0.1ms; one mux SSH session 1265-1521ms
  (~93%); node CDP work 87-98ms. Pill acquired+verified before every send,
  released+verified after every send, 6/6.
- Kill+restart test PASSED: daemon killed 06:58:06, supervisor revived it
  by 06:58:18 (~12s downtime); manual `daemon.sh restart` also tested, and
  a verification send (mochi run 99) through the restarted daemon delivered
  in 1.337s, verified. Daemon left running with supervisor watching.
- Full log in `~/workspace/speed-test-20261123.log` (Method 2 section).
- Caveat: sends are serialised by design (one at a time); true concurrent
  sends were not attempted. The session-guardian collision is bypassed
  (no cu.py session-driver), so serialised back-to-back sends are the
  intended use.

## Instrumentation (R15, landed 2026-11-27)

Append-only logging added by team decision Item 6 (R15) of
2026-11-27. No lifecycle change: supervision stays three-layer
(supervisor.sh 60s loop running watchdog.py, watchdog-15m.py, and
the zen-laptop-health runtime cron). The service-manager route was
killed (no user systemd bus on this VM). Supervision is re-decided
at the earlier of (a) two deaths with named causes captured by this
instrumentation, or (b) 7 days after landing (2026-12-04).

What is logged now:

- `daemon.log` `daemon_exit` (reason = signal name, pid): written by
  the SIGTERM/SIGINT handler in daemon.py, so every deliberate stop
  (daemon.sh stop, any restarter) names itself. `daemon_stop` still
  follows from the serve() finally.
- `daemon.log` `daemon_start` now carries `restarter` (env
  DAEMON_RESTARTER, set by watchdog.py and watchdog-15m.py; default
  "direct/unknown"), so "daemon was restarted by X" is recorded at
  the start, not inferred later.
- `daemon.log` `daemon_bind_failed` (pid, sock, error): a second
  daemon starting while one is live fails on bind and logs the
  contention before crashing as before.
- `watchdog.log` `watchdog_heartbeat` (daemon_up true): one line
  per 60s supervisor cycle. Its absence is the supervisor-liveness
  signal that did not exist before.
- `watchdog.log` restart lines and `watchdog-15m.log` DAEMON lines
  carry their restarter identity. `supervisor.log` gets
  supervisor_start / supervisor_stop lines.

BLIND SPOT (read this before interpreting the logs): exit logging
cannot capture VM death. SIGKILL and VM replacement kill the daemon
without any exit line. For that class, the evidence is a
watchdog_heartbeat gap correlated with VM replacement records
(uptime resets, co-death of daemon + supervisor). "No exit lines"
must NEVER be misread as "no deaths": a death with no exit line
means the daemon vanished (VM replacement or SIGKILL), which is
the dominant death class in the 2026-11-27 archaeology (17 of 45
deaths). Conversely, a daemon_exit SIGTERM line followed by a
daemon_start with a named restarter is a deliberate restart, not a
failure.
