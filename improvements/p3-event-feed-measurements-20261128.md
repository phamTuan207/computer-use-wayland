# P3 event feed: extended measurements (2026-11-28)

Owner order 2026-11-28 06:12: the team tests P3, meets
(council + redteam), and decides itself. This file records the
extended test evidence. The council + redteam verdict and the
build outcome are appended at the end when decided.

Safety frame: all live work ran against a dedicated throwaway Zen
session on RDP port 9241 (launch_dedicated profile under /tmp,
--start-debugger-server 9241), launched detached on the laptop.
The owner Zen (PID 807599, RDP port 6021) was only probed
read-only for liveness and verified untouched at cleanup (same
PID, 6021 listening). Test pages were local fixtures on
127.0.0.1 served by an in-process HTTP server. No real accounts,
no cookies, no sensitive data. The measurement client was a
standalone stdlib-only raw RDP client (same length-prefixed JSON
framing as rdp_client.py) that logs every packet it skips,
mirroring the 2026-11-27 spike probe discipline: bounded
200-entry log with dropped counter, seq/cursor reads, URLs
redacted (query values stripped) before logging, no long-poll,
no reader thread, no server-side watches, nothing subscribed.

Note on method honesty: the polling baselines below are the raw
client's poll loops (evaluate every 50-100 ms, no replay logic).
The shipped rdp_client wait_load uses evaluate(replay=True)
re-attach logic, which may recover from stale actors faster than
the raw loop; the shipped number was not measured in this run
and the M1 poll figure must be read with that caveat.

## Results (run 2026-11-28 06:24:38 to 06:25:43 +07)

### M1 navigate detection (5 reps)

tabNavigated arrived median 3.7 ms after the navigateTo send
(reps: 3.3, 3.7, 2.1, 36.2, 4.5 ms), state ALWAYS "start",
never "complete". The raw poll loop detected readyState
"complete" at median 5083.5 ms with exactly 2 polls per rep:
the first evaluate on the stale pre-navigation console actor
hung the full 5 s timeout (no error packet, just silence),
then re-attach, then success on the second poll. Reading: the
event cannot signal load completion (state is start-only), so
it cannot replace the readyState read; what it can do is tell
the client at ~4 ms that navigation started and the old target
is dying, instead of discovering that via a timed-out evaluate.
How much of the 5 s the shipped replay path already saves is
unmeasured.

### M2 tab open detection (5 reps)

tabListChanged median 5.1 ms (reps: 11.5, 5.3, 4.4, 5.0, 5.1)
vs listTabs poll median 6.8 ms (reps: 8.3, 6.8, 6.2, 7.1, 6.1).
Near-equal, because the poll loop started right after the
synchronous open evaluate returned. The feed's value here is
not latency; it is that a library consumer doing other work
learns of the change without polling at all. tabListChanged
carries no payload, so the consumer must still re-list to get
the delta.

### M3 tab close detection (3 reps)

descriptor-destroyed arrived during the close evaluate's own
wait in all 3 reps (the measurement's wait_for_event window saw
none because the event had already been logged as unsolicited
inside evaluate; the M4 inventory total of 40
descriptor-destroyed = 37 storm closes + 3 M3 closes confirms
delivery in every rep).

### M4 storm 30 (37 closes total)

Open phase 210.1 ms (30 tabs, listTabs interleaved after each),
close phase 1045.2 ms. All 108 requests paired correctly
(all_paired true). Max unsolicited packets skipped inside one
request wait: 48 (the close-storm evaluate). Bounded log:
retained 200, dropped 86, dropped_flag true; 286 packets passed
through a 200-entry log, so the overflow path and the
dropped-count flag are exercised, not theoretical. Unsolicited
inventory this run: tabListChanged 49, descriptor-destroyed 40,
frameUpdate 24, tabNavigated 5, forwardingCancelled 2,
processListChanged 1, plus consoleActor resultID acks (44 from
the parent console actor alone) and a few bare target-actor
packets. The resultID acks and frameUpdate are noise a feed
must filter; they are not lifecycle events.

### M5 idle 10 s

Zero packets arrived in a 10 s idle drain; a listTabs request
immediately after paired correctly. No heartbeat traffic; the
feed is silent when nothing happens.

### M8 F11 terminal-state shape (the headline number)

A waiter polled evaluate every 100 ms for a never-appearing
element with an 8 s budget (the wait_for shape). A second RDP
connection closed the tab at 1023.7 ms into the wait.
descriptor-destroyed arrived on the waiter's connection at
1023.8 ms, 0.1 ms after the close, inside a poll evaluate's
wait. The poll loop, deliberately not acting on the event,
burned the full 8004.6 ms budget with ZERO evaluate errors:
evaluate on the dead tab's console actor kept returning falsy
instead of failing. Without the feed, shipped wait_for with a
30 s budget burns 30 s in this shape and reports a plain
timeout; with the feed, the same wait can fail fast at ~1 s
with a terminal-state classification. This is the F11 wait
burn the decision doc named, now quantified.

### M7 socket death (last, session stopped mid-evaluate)

A slow in-flight evaluate (4 s busy-wait in page) failed with
ConnectionError ("RDP socket closed by server") 565.4 ms after
send, of which 500 ms was the deliberate stop delay: actual
fail latency after the browser stopped is ~65 ms. Clean fast
failure, no hang, no pairing confusion afterwards (the client
is unusable after socket death, as expected; no feed state
survives a dead socket).

## What the evidence supports, stated plainly

- Coarse lifecycle events (tabListChanged, tabNavigated,
  descriptor-destroyed, processListChanged) arrive reliably
  and fast (single-digit ms) with no subscription, and demux
  pairing held under a 30-tab storm (108/108) and after idle.
- The one large measured win is terminal-state detection
  (M8): 0.1 ms event vs full-budget poll burn.
- Navigate/open latency wins are small or conditional:
  tabNavigated is start-only (M1), tab-open event vs poll is
  near-equal when the poll starts immediately (M2).
- Overflow is real: a 37-close storm drops 86 of 286 packets
  through a 200-entry log. Any consumer must treat the feed as
  lossy and use the dropped flag; a dropped
  descriptor-destroyed must never be read as "tab still alive".
- One-shot CLI mode still gains nothing cross-call (the log
  dies per invocation). Library mode only, as decided.
- Unmeasured: the shipped wait_load replay path's stale-actor
  recovery time (M1 caveat), event behaviour on the owner's
  real session with many tabs (dedicated sessions here had at
  most 39), and any Zen-version drift in packet shapes.

## Council + redteam verdict

(Pending. Appended when the decision meeting concludes.)

## Build outcome

(Pending the verdict.)

## Sources

All accessed 2026-11-28.

- improvements/zen-mcp-adoption-decision-20261127.md (this
  repo): P3 section, spike scope, binding constraints.
- improvements/zen-mcp-spikes-20261127.md (main): spike packet
  inventory and demux proof this run extends.
- scripts/zen-rdp/probes/p3_unsolicited_probe.py (main): the
  spike probe whose discipline this measurement mirrors.
- scripts/zen-rdp/rdp_client.py (main): request() demux shape,
  wait_load/wait_for poll loops, F11 context.
- Measurement run: dedicated session port 9241, 2026-11-28
  06:24:38-06:25:43 +07, raw stdlib client, localhost fixtures;
  numbers above are from that run's JSON output.
