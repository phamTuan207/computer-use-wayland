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

## Council + redteam verdict (2026-11-28)

Five independent workers argued from the evidence above plus
the spike. Verdicts:

- Council, performance lens: DO-NOT-BUILD the general feed.
  Happy-path saving is 0 ms (wait_load: tabNavigated is
  start-only, the readyState poll stays; wait_for: no event
  signals element appearance) to 1.7 ms (tab open, M2). The
  one real saving is F11 fail-fast (up to ~29 s per dead-tab
  wait at a 30 s budget), and it does not require the feed: a
  liveness check in the existing poll loop captures nearly all
  of it. Flip conditions: shipped replay path measured AND an
  event wake-up shown to cut its recovery by >500 ms; a
  completion-bearing event observed; dead-tab waits measured
  frequent AND the poll-loop check proven too slow; library
  mode becoming the dominant workload.
- Council, reliability lens: BUILD-SCOPED to terminal
  fast-fail on exact descriptor match plus tabListChanged
  wake-up, nothing else; flips to DO-NOT-BUILD if F11 is
  fixable by a cheap descriptor-existence check in the poll
  loop, or if the demux change cannot be proven pairing-safe
  under storm replay. Guarantees required: feed may only
  shorten a wait on positive evidence, never confirm one;
  dropped/gapped cursor forces poll fallback; ingest-filter
  noise classes; exact descriptor match pinned at wait start.
- Council, architecture lens: BUILD-SCOPED as a tap on the
  two existing skip points (request() and _evaluate_once()),
  reusing the probe BoundedLog, one cursor API, F11
  integration in wait_for only. Flips to DO-NOT-BUILD if F11
  is fixable by a sentinel in _evaluate_once() on
  descriptor-destroyed without the log, since the log then has
  no measured consumer.
- Redteam, cost/duplication lens: DO NOT BUILD, close P3.
  The feed replaces nothing (poll loops, listTabs, replay all
  remain authoritative), duplicates existing mechanisms minus
  their payloads, overflows exactly under storm load (M4: 86
  dropped), and its headline saving is misattributed (the
  honest comparison is feed vs a liveness-checking wait, a
  ~100 ms difference on an already-failed task). Narrowest
  surviving scope: an internal single-wait death flag set by
  the demux skip path on descriptor-destroyed for the waited
  actor, checked on the wait's next poll iteration, dying when
  the wait returns. No log, no cursor, no public feed.
  Reopen P3 only if F11 frequency data shows a material burn
  the narrow fix leaves behind.
- Redteam, risk/security lens: NO-GO as scoped against the
  owner's live Zen. tabNavigated would carry URLs of every
  tab including denylisted credential tabs (the denylist
  protects acts, not feed reads); shape-based redaction will
  miss a shape eventually; a demux change on the live session
  risks the wrong-tab incident class; a lossy feed invites
  stale action. Non-negotiable guards include: no URL
  payload at all, in-memory only, dropped>0 invalidates the
  feed, no actuation from feed events without synchronous
  re-validation, denylisted tabs produce no events. Surviving
  scope: dedicated-session, observe-only, URL-free counting
  only, which does not justify live-lane demux risk.

## Decision (converged)

DO NOT BUILD the general P3 event feed. P3 as a feed is
CLOSED. The two BUILD-SCOPED verdicts both carry explicit
flip conditions that the narrow F11 fix satisfies (a sentinel
in the skip path fixes F11 without a log; a cheap check in
the poll loop fixes F11 without a feed), and the remaining
three verdicts are against. Every lens agrees the only
measured win is F11 terminal fast-fail and that happy-path
savings are 0-1.7 ms.

F11 is finished by the narrowest means, per the decision
doc's own fallback ("if not, F11 is finished by other means
and P3 closes"). Specification for the fix:

1. Internal terminal-death signal, no feed: in the demux skip
   paths of RDPClient.request() and RDPClient._evaluate_once(),
   when a skipped packet has type "descriptor-destroyed" and
   its "from" equals the descriptor actor of the tab this
   client has pinned, record a per-client terminal flag (with
   the descriptor and a timestamp). Matching logic for
   responses is untouched; the check is a side observation on
   packets already being skipped and must never raise.
   descriptor-destroyed carries no URL, so no redaction
   surface is added. No log, no cursor, no retained history,
   no public API.
2. Waits fail fast on the flag: wait_for and wait_load check
   the flag each poll iteration; on a match for the tab being
   waited on, raise a terminal-classified RDPError (tab
   destroyed) immediately instead of burning the budget.
   The flag is scoped to the descriptor pinned at wait start
   and to the current connection; a descriptor-destroyed for
   any other tab is ignored by waits. evaluate(replay=True)
   must not replay past a terminal flag.
3. Why this catches the M8 shape: in M8, evaluate on the dead
   tab's console kept returning falsy with zero errors, so
   terminal-error classification alone would NOT have caught
   it. The descriptor-destroyed packet arrived during a poll
   evaluate's wait (0.1 ms after the close), so the skip-path
   flag catches it within one poll iteration. Navigation does
   not destroy the descriptor (M1: 5 navigations, zero
   descriptor-destroyed; M4 total 40 = exactly the 40 closes),
   so the flag cannot false-fire on navigation.
4. Tests required before landing: unit tests with a fake
   socket (descriptor-destroyed for pinned tab sets the flag;
   for another tab does not; pairing unchanged under a
   storm-shaped packet interleave; flag does not survive
   reconnect); a live dedicated-session test replicating M8
   (wait_for on a tab closed mid-wait fails fast with the
   terminal classification, target < 1.5 s vs 8 s budget);
   storm pairing regression (M4 shape, 100% paired); shipped
   wait_load before/after measurement on the same navigate
   fixture (closes the M1 caveat); full shard green;
   independent review with no BLOCKING; machine-layer refresh
   plus rdp_smoke on a dedicated session.
5. Explicitly NOT built: event log, cursor API, tabListChanged
   or tabNavigated retention, drain/long-poll, reader thread,
   server-side watches, any URL-bearing event handling, any
   actuation triggered by events. P3 reopens only if F11
   frequency instrumentation in real runs shows a material
   burn the narrow fix leaves behind, or a completion-bearing
   event class is ever observed.

## Build outcome

The build did not land in this session. A fresh repo worktree
created for the landing work failed a runtime execution-risk
check, and the governing security notice prohibits running,
testing, importing, or committing inside that checkout's
content without the owner's explicit go-ahead. The decision,
evidence, and fix specification above are recorded so the
build can proceed immediately once that go-ahead is given.
No code was changed; the shipped lane is exactly as landed in
PR #1187.

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
