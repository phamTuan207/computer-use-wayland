# R15 speed-daemon log archaeology (E2) - 27/11/2026

Item 6 of team-decisions-20261127.md, step 1: correlate the 46
daemon_start events in ~/workspace/speed-daemon/daemon.log with VM
replacement records and watchdog restart entries, BEFORE any code
change. Sources: daemon.log (46 starts, 0 daemon_stop events),
watchdog.log (3 restarts by watchdog.py supervisor loop),
watchdog-15m.log (9 restarts by watchdog-15m.py), daemon.out (2
address-already-in-use tracebacks), r3l3-zen-laptop-health watch log
(26/11 23:42 onward), daily notes ~/memory/2026-11-23..27.md, VM
uptime at analysis time (47 min at 06:28 27/11, so last replacement
about 05:41 27/11).

## Split (46 starts)

| Class | Count | Starts |
|---|---|---|
| Initial launch | 1 | #1 |
| VM replacement, confirmed (uptime/systemd evidence) | 3 | #31, #42, #46 |
| VM replacement, probable (daemon+supervisor co-death) | 12 | #27, #28, #29, #35, #36, #37, #39, #40, #41, #43, #44, #45 |
| VM replacement, probable (PID reset only) | 2 | #22, #34 |
| Watchdog-induced restart, death cause unattributed | 12 | watchdog.py loop: #2, #21 (deliberate kill test), #24; watchdog-15m.py: #9-#16, #18 |
| Worker-induced (not a death) | 3 | #32 (`daemon.py --help` accident), #33 (its recovery), #38 (double-restart race) |
| Manual restart after found-dead, death cause unknown | 5 | #7, #8, #19, #20, #25 |
| Unexplained (no restarter record) | 8 | #3, #4, #5, #6, #17, #23, #26, #30 |

Headline split: VM replacement 17, watchdog-induced 12, unexplained
8 (plus 5 manual-after-found-dead and 3 worker-induced, 1 initial).

## Reading of the evidence

- The dominant death class is named: daemon and supervisor die
  TOGETHER on a roughly 2h cadence (26/11: 09:28, 11:43, 13:26,
  15:43, 17:30, 19:42, 21:44, 23:44; 27/11: 01:43, 03:42, 05:42).
  Three are confirmed VM replacements by uptime/systemd evidence
  (26/11 about 05:23, VM uptime 1 min at 05:26 check; 26/11 about
  21:44, systemd start 14:44 UTC; 27/11 about 05:41, uptime 47 min
  at 06:28). Co-death of both layers is the replacement signature;
  no same-VM supervisor survives it, which is why the rescues come
  from runtime-cron watches (zen-laptop-health, agents-watch) or
  watchdog-15m.py, never from watchdog.py, in those cases.
- watchdog.py (supervisor loop) only ever restarted the daemon 3
  times, once as a deliberate kill test (25/11 09:01). In every
  co-death the supervisor was dead too, so the loop could not fire.
- watchdog-15m.py restarted the daemon 9 times on 24/11 at the same
  roughly 2h cadence. Whether those deaths were also VM
  replacements is unattributed: no supervisor-liveness record exists
  for 24/11. The cadence matches the VM restart cycle noted 21/11
  (2-3h, conflicting reports, no log at the time).
- daemon_stop appears 0 times in the whole log: SIGTERM never ran
  the finally block, so even deliberate `daemon.sh stop` kills left
  no exit record. Every death in the record is currently
  indistinguishable from every other.
- daemon.out holds exactly 2 address-already-in-use tracebacks:
  double-start races (#23/#24 on 25/11 12:28, #37/#38 on 26/11
  13:28 are the candidate pairs; one of each pair crashed on bind).
- One supervisor-only death class exists (supervisor dead, daemon
  alive): 25/11 about 20:11-20:28, 26/11 03:36, 26/11 17:41. Cause
  unknown; the supervisor loop has no liveness record of its own.

## Scope consequence

Unexplained is NOT small: 8 of 46 starts have no restarter record,
and the death cause is unattributed for all 12 watchdog-induced
restarts plus the 5 manual ones. Instrumentation scope therefore
does NOT shrink. What archaeology changes is the expectation:
exit-reason lines will mostly capture deliberate SIGTERMs from
restart paths, while the dominant class (VM replacement) will show
as heartbeat gaps with no exit line. That is exactly the stated
blind spot in the decision: "no exit lines" must never be misread
as "no deaths". Instrumentation proceeds as specified in Item 6
step 2, with the 7-day / two-named-cause-deaths trigger (E3)
unchanged.

## Baseline kill test (pre-instrumentation, 27/11 06:30 +07)

- Kill daemon (pid 2089, SIGTERM): supervisor loop restarted it in
  about 15s (watchdog.log 06:30:07 down, 06:30:16 restarted pid
  8228), well within one 60s cycle. PASS.
- Kill supervisor (supervisor.sh stop): daemon pid 8228 still
  answering ping after 70s. PASS. Supervisor restarted detached
  (pid 8616).
