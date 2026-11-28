# PILOT FIRST decisions 2026-11-28: measurements, council+redteam verdicts, build scopes

Owner order 2026-11-28 10:14: run the PILOT FIRST items
from the pain-point meeting
(improvements/pain-point-meeting-20261128.md). Five
measurement workers ran in parallel on dedicated sessions
(ports 9261-9305); council (performance/reliability seat,
risk/cost seat) + redteam then ruled per pilot against the
pre-agreed decision rules. Owner permission 10:20: agents
may operate on the live Zen (real-combat Zen); owner tabs
never closed/navigated, no compositor window-close. Owner
order 10:29: dedicated sessions closed by recorded pid
immediately when tests finish.

Evidence files (VM ~/workspace/pilot-first-20261128/):
pilot1-shadow-iframe-evidence.md, pilot2-background-tab.md,
pilot3-idle-lock-evidence.md, pilot4-m1-replay.md,
pilot5-p2b-settling-evidence.md, pilot-council-perf.md,
pilot-council-risk.md, pilot-redteam.md. Note: /tmp cleared
mid-round and took three full pilot reports; evidence for
pilots 1/3/5 was recovered from worker handoffs with all
key numbers.

## Pilot 1: shadow-root / same-origin-iframe waits

Measurement: 6 of 8 fixture shapes fail today (wait burns
full 3 s budget; act not_found). Traversing workaround
0.5-1.1 ms but first-match, no count==1 proof. Real
frequency 0/63 R3-L3 graded tasks (redteam caveat: R3-L3
ran BiDi/cursor lanes, so 0/63 is prioritization evidence,
not RDP-lane demand proof). Shape (e) duplicate is a live
silent wrong-click today (Pilot 5 F08/F10 prove the class);
gone=true returns in ~1 ms over shadow-hidden elements.

Decision: NOT BUILD (unanimous). Reopen triggers: first
real RDP-lane shadow/frame target, Messenger-class target
assigned to RDP lane, or a caught first-match workaround
click in a real run. Any future build moves wait+act
together (breaking: dup shape counts 2 where act today
claims 1), renames poolScope, redefines SCAN_CAP over the
merged pool, decides snapshot scope. Interim docs
paragraph approved ONLY as drive-by with a hard count gate
(count first, act only on count==1, never first-match);
without the gate, skip it.

## Pilot 2: background-tab discipline

Measurement: RDP open (gBrowser.addTrustedTab) never
switches the selected tab (5/5 dedicated x2 + 5/5 live
owner Zen). zen_cli open (window.open via BiDi) switches
5/5, matching the 2026-11-21 incident. navigate/evaluate/
act/attach/close on pinned background tabs never switch.
Side findings: addTrustedTab inserts before the selected
tab (index +1; never cache indices across an open);
parent currentURI reports about:blank for loaded
background tabs (use RDP URLs); act refused on live pinned
background tab while evaluate worked (own probe if
act-on-background becomes supported).

Decision: RDP path NOT BUILD, close as covered (cheap
smoke assertion approved). zen_cli cmd_open BUILD-SCOPED:
re-activate the opener context immediately after the new
tab is found (before title fetch; redteam: immediate, the
up-to-8 s poll is the steal window), session path only
(--live unchanged, documented; session path can never
attach to owner Zen, no BiDi port there), fail-open with
disclosure if activate fails, dual-protocol smoke
assertion (BiDi alone cannot read selected), index-shift
line in skill doc. browsingContext.createContext is
unknown-command in this build; no cleaner background
create exists. Flip condition: if a focus flash remains
after the fix, ban zen_cli open on the owner session.

## Pilot 3: idle-lock contention

Measurement: flock LOCK_EX|LOCK_NB fail-fast by
construction; no wait exists to log; refusal median
0.075 ms (cheaper than success); zero LOCK REFUSED /
lock_held across 937 log files. Honest caveat: lock
landed 2026-11-27 and no machine-layer wrapper enables
--lock-file yet, so the historical zero is partly "lock
never taken" and must never be cited as contention
evidence.

Decision: NOT BUILD (no idle timer, no wait logging).
Wrapper wiring BUILD-SCOPED, machine layer only, separate
from repo builds: per-port lock file set via preflight +
PLAYBOOK (a choke point must be created; drives currently
call rdp_client directly), rdp_client stays opt-in, one
live two-client refusal test, watchdog interaction decided
explicitly before wiring. Reopen the contention question
only if lock_held appears in a real drive report.

## Pilot 4: M1 shipped replay timing

Measurement: the 5 s hang survives on the shipped path,
worse than raw. S1 fast navigate+wait_load median 53.7 ms
(F11 replicated). S2 slow page: 8/8 wait_load timeouts at
~11.3 s (default 30 s budget burns ~30 s and still fails);
manual recovery median 4.9 ms. S3 page-initiated nav:
first-success median 5017.6 ms, 12/12 socket_timeout,
replay 0/12. S6 direct evaluate: ~20 s timeouts. Root
cause: evaluate() replays only on noSuchActor text; a
stale console actor stays silent, TimeoutError never
reaches the replay branch; wait_load's _reattach_pinned
refuses on the URL-changed guard, exactly the
post-navigation state.

Decision: BUILD-SCOPED, fixes 1+2, both flip conditions
met (recovery 5017 ms median; early abort would cut
~4976 ms). Merged conditions from all three seats:
- Fix 1: TimeoutError replayable in evaluate(), replay=True
  callers only, exactly once, F11 terminal check first,
  replay ONLY if re-attach yields a DIFFERENT console actor
  (separates dead actor from slow-but-alive; kills the
  double-execution and late-packet correlation risks), and
  only when the receive buffer holds no partial packet.
  act and CLI eval stay replay=False; parent_evaluate
  untouched.
- Fix 2: navigation-aware _reattach_pinned in scoped form
  only: allow URL-change re-attach only when the pinned URL
  is absent from the tab list (if the old URL is found
  under another id, refuse as today) + descriptor match +
  F11 flag clear + tab count unchanged + url_substr match
  for wait_load. The URL guard is never deleted outright
  (descriptor ids are positional; Pilot 2 measured index
  shifts).
- Tests: execute-then-silence fault tests extending
  test_f1_replay.py (F1 exactly-once preserved), slow-JS
  no-replay test, late-packet desync test, id-shift refusal
  test, re-measure S2-S6 shapes, full shard, independent
  review.
- Recovery honesty: fixes 1+2 bound recovery at one
  timeout + ~5 ms, not the simulated ~9 ms. The builder
  reports measured recovery; the <500 ms bar is claimed
  only if measured (cutting wait-loop poll timeout needs
  measured false-timeout cost). tabNavigated sentinel NOT
  in scope: S0 never observed the packet on the shipped
  attach shape (20/20 zero), so sentinel feasibility is
  unproven; revisit only if a tail remains after 1+2 and
  arrival is first proven.

## Pilot 5: P2b settling tests + wrong-match rate

Measurement: settling tests PASS live (8/8 twice; submit
counter stays 1 with retry=unsafe; digest = descriptor
stability, not identity). Wrong-match rate: CORRECT 6,
REFUSAL 9, WRONG_ACT 3 of 18 fixtures (F08 shadow dup,
F10 iframe dup = pool blind spots; F12 node replacement =
identity gap). Historical: zero wrong-match FAIL/INVALID
in 59 R3-L3 rows.

Decision: NOT BUILD, P2b gate stays shut (unanimous).
All formal gate inputs exist (F1 closed, settling pass,
rate measured), but P2b-as-specified fixes 0 of 3 wrong
acts (redteam correction: F12 would convert wrong-act to
refusal under a digest+ordinal registry, which counts for
safety; F08/F10 need Pilot 1 pool expansion first) and
converts only 4/9 refusals at proven stale-ordinal risk.
Reopen: instrument real-run act refusals +
snapshot-to-act mutation for one cycle (must be assigned,
not suggested, when the next run cycle is planned).

## Build order

1. Pilot 4 fixes 1+2 (rdp_client.py) + Pilot 1 docs
   paragraph as drive-by in the same PR.
2. Pilot 2 zen_cli cmd_open re-activate + smoke assertion.
3. Pilot 3 machine-layer lock wiring (separate; laptop
   machine layer, not repo main).

Nothing trades correctness for speed. Ponytail throughout:
smallest complete change, reuse what exists, one small
test for non-trivial logic.
