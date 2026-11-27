# Pain-point audit 2026-11-28 (clone2, independent)

Prepared for the pain-point sweep and the council+redteam
meeting that decides what to build next. Sources: the full
project logs and git history (lane A), clone2's 47-entry idea
queue with its pilot results and the M-item ranking (lane B),
and fresh live measurements on clone2's VM (lane C). Lane files
kept locally in ~/workspace/pain-audit-out/ (lane-a-logs.md,
lane-b-queue.md, lane-c-measured.md).

Method rules, per the assignment: every figure is either
measured in a log or a live run, derived from counts times a
measured unit cost, or marked UNQUANTIFIED. Three clocks appear
in this record (runner minutes inside graded runs, wall-clock
hours of calendar time, and machine volume in commits and
lines); they are never summed into one number. Each ranked
item carries its clock in brackets. Items 4, 5, 8, 13, and 14
are placed by volume, recurrence, and integrity judgment, not
by a minutes figure; in particular, item 4's position asserts
nothing about minutes against item 7's measured 245.0 min.
Basis limitation: the minute ranking rests on one complete
graded cycle (R3-L3), one cancelled generation (R3-L2), and
9 days of record (2026-11-20 to 2026-11-28); per-cycle figures
should not be extrapolated until a second cycle is measured.
Overlap: items 3 and 7 may overlap by up to 245 min (the
study does not settle whether R3-040's retry sits inside the
432.5 min total), and items 6, 9, 11, and 12 are subsets or
re-slices of cycles already reported in items 2 and 3, not
additional burn; item 6's episodes also land on item 2's
clock. Lane A
re-measured the bottleneck study's headline figures a day
later and reproduced them (watchdog commits 2,117 of 4,645 in
the window, 45.6 percent, against the study's 42 percent
all-time; watchdog PRs 1,134 of 1,224, 92.6 percent, against
the study's 92 percent; median commit 10 lines; 60 grade rows
with exactly 6 INVALID), so the study's numbers are safe to
build on.

## Ranked pain points by time burned (from the logs)

1. Usage-cap exposure. [wall-clock] About 62.4 h of capped
   time against a 39.4 h run span in the R3-L3 cycle; the
   scorer seat stood empty for the first 18 h. MEASURED
   (study timestamps). No queue entry covers it, and none of
   the M register's priced pools (M1, M4, M11d, M12) is a cap
   item; it is a staffing and scheduling exposure, and it is
   the largest single number in the record.
2. Post-run processing in the graded cycle. [runner minutes]
   954 of 1,729 min (55 percent) came after driving: scoring
   lag 534 min plus ledger tail 420 min, against 775 min of
   driving. MEASURED; the audit share inside the ledger tail
   is UNQUANTIFIED. Maps to M1 (ledger tail) in the M
   ranking; no landing record for M1 was found in the sources
   the lanes checked. No queue entry.
3. Frozen spec defects. [runner minutes] 432.5 runner min
   discarded in R3-L2 when 18 defects surfaced after the spec
   froze. MEASURED. Mitigation M11d (pre-freeze triage) is
   recorded DONE (merged) in the integration phase report
   (its item 22, commit 482aca7c), with that report's own
   caveat that the catch rate is unmeasured until first use;
   the residual is whether the triage runs before the next
   freeze and what it catches.
4. Watchdog machine volume. [volume] 2,117 watchdog commits
   in 9 days (average about 348 per day across 2026-11-23 to
   2026-11-27, peak day 429) and 1,134 watchdog PRs; clone2's
   539 watchdog PRs are all still open, zero merged, and the
   on-main watchdog log has been frozen since 2026-11-23.
   MEASURED as volume; minutes per round are UNQUANTIFIED
   because no round has ever logged its own duration.
   Mitigation M28a (append-only watchdog branch) is recorded
   DONE (merged) in the integration phase report (its
   item 23, commit 877afe6d), with the caveat that the lane
   switch-over is still a coordinator decision, so the merged
   tooling may not be the path the watchdog lanes actually
   use; the volume since then has not been re-measured, so
   the residual burn is UNQUANTIFIED.
5. Deliberation volume. [volume] The study counts 71,971
   lines in 273
   entries, 38 percent of improvements/ lines; lane A's
   recount at a later tip gives 313 files and 85,080 of 189,554
   lines (44.9 percent, broader match). MEASURED as volume;
   the waste share is UNQUANTIFIED (the study's own conflict
   C8 leaves it open). No queue entry prices deliberation.
6. Coordinator continuity. [wall-clock episodes] About
   235 min across documented unresponsive episodes, 15
   takeovers; the R3-056 stall ran 70 min with about 40 min
   to detection. MEASURED.
7. No pre-agreed 429 policy. [runner minutes] One FAIL retry
   burned 245.0 min (R3-040). MEASURED. Maps to M12 in the M
   ranking; no landing record for M12 was found in the sources
   the lanes checked.
8. Owner waits on ruled classes. [wall-clock episodes]
   Documented HOLDs of 126 min and at least 65 min, plus
   131 min of post-run silence before an owner nudge.
   MEASURED episodes; total owner time UNQUANTIFIED.
9. Bot-check walls from the webdriver signal. [runner
   minutes] 71.8 runner min across 6 INVALID grade rows, plus
   a response arc of about 9 h (24 documents, 4,755 lines)
   for the R10 work. MEASURED.
10. Repeated full test-suite runs. [machine time] 39 logged
    runs sum 9,390 s
    as an upper bound (95 to 374 s each); sharding per M17
    leaves 133 s per run unclaimed. MEASURED. Fresh price from
    lane C (clone2's VM, a shared sandbox capped at 1.5 CPU,
    NOT the owner's machine; ratios are the signal): the full
    repo tests/ serial run is 7,570 tests in 121.4 s wall,
    while the zen-rdp suite itself is only about 3 to 4 s. The
    M17 shard tool crashed at --timeout 120 with an unhandled
    subprocess.TimeoutExpired (each shard subprocess receives
    the whole budget, so a large shard cannot finish and the
    tool dies instead of reporting), and at --timeout 600 it
    took 240.4 s, about 2x SLOWER than serial on this
    CPU-capped VM; whether the sign flips on a multi-core
    machine is UNVERIFIED.
11. Runner fabrication rework. [runner minutes] About
    100 min of windows plus 37.2 min of Rule-A re-runs across
    7 gradings. MEASURED. Lane A notes this class is
    earliest-tasks only and was closed by later rules; it is
    ranked as recorded burn, not a live pain.
12. Class L score-before-reset blocking. [runner minutes]
    87.1 idle min across 9 tasks. MEASURED. Maps to M4 in the
    M ranking; no landing record for M4 was found in the
    sources the lanes checked.
13. Single-driver contention. [runner minutes, upper bound]
    633 min of merged-timeline gaps as an upper bound only;
    the true share is UNQUANTIFIED.
14. Y1b sandbox cluster. [wall-clock window] About a 24 h
    commit window with a serial queue gated behind it.
    MEASURED as a window.
15. Marionette single-slot wedge. [frequency] 2 strikes,
    9 failed
    sessions, a 55-tab cleanup redo. Frequency MEASURED;
    minutes UNQUANTIFIED. Lane C prices the related pattern:
    on local Zen 1.24.3b with the R17 fixed client, per-op
    latency is a few ms (introspect median about 6 to 7 ms),
    but session setup costs about 5 to 9 s (launch 1 to 4 s
    plus new_session about 4.3 to 4.6 s), so session churn,
    not op latency, is the expensive habit.

## The queue's pains (lane B): priced in defects and rates, not minutes

Lane B assigned all 47 queue entries to pain groups and
checked each against the integration and adoption landing
records. The structural headline: the queue's pains are code
and contract pains that the source documents almost never
price in minutes, while the big minute figures above (items
2, 3, 7, 12) belong to run-process pains with no queue entries
at all. The queue under-covers process pain. Live groups,
ranked by documented stakes:

G1. AT-SPI walk cost, truncation, and silent caps (Q5, Q6,
    Q7, Q8, Q9, Q25, Q26, Q27, Q28, Q44). Status split: the
    accounting and silence half of this pain is already fixed
    (Q43 spent, closing the W12/W16 silence component); only
    the cost half is live. Structural stakes are sourced: an
    800 ms per-call default timeout against a 2 s walk budget,
    real trees of 1,554 to 1,826 nodes against a 500-node cap,
    and a 2^31-child GetChildren freeze. All
    savings are PROJECTED (Q7's pre-registered 2x factor, Q27's
    at least 30 percent D-Bus reduction, Q26's at most
    10 percent repeat cost) and all untested: the U4
    five-variant measurement everything hangs on has not run.
    Lane C could not run it here either: this VM has no Python
    AT-SPI bindings (no gi, no pyatspi, no Atspi typelib), so
    the walk cost on this machine is UNVERIFIED and the
    measurement needs the owner's machine or a VM with the
    bindings installed.
G2. Marionette client response misattribution under threads
    (Q33). (Lane B's body sections number this group and G3
    in the opposite order; the entry lists are the identity.)
    The only queue group with a measured local time
    figure: in the pilot, 3 of 6 interleaving rounds ended in a
    30.0 s stall with an id mismatch and the other 3 were
    silent misattribution. The lock fix is specified; neither
    landing doc records it as landed.
G3. Element identity and wrong acts in the I2 pilot (Q11 to
    Q17, Q37, Q41). Priced in failure rates, not minutes:
    name-only identity on repeated rows scores 13 to 18 percent
    accuracy against 99.5 to 100 percent with row context;
    look-alike refusal runs 49 to 79 percent. All untested; the
    I2 pilot has not reported.
G4. Delivery uncertainty and double execution (Q2, Q3, Q35).
    A live double execution from "noSuchActor" message-text
    matching is a measured local incident. Scope reduced by the
    landings (the gate-fix batch closed the page-text
    classification hole; the adopted P2a form removes act-path
    replay), but Q2's stored-outcome keys and Q3's distinct
    exception kind are not recorded as built.
G5. Chrome-context launch route (Q1, Q47). Q1's pilot is
    PROVEN (the capabilities route refused outright; the
    geckodriver flag reaches chrome context), but no zen_dom.py
    flag change is recorded in the landing docs, so the code
    state is UNVERIFIED from these sources. Q47's
    laptop-launcher half remains UNVERIFIED (quarantine).
G6. Error-contract gaps around the landed I1 envelope v1
    (Q18 to Q24). All sourced (gRPC, RFC 9457, WebDriver,
    Appium), all untested, all UNQUANTIFIED.
G7. BiDi lane capability gaps (Q10, Q31, Q32, Q34, Q46). Q10's
    pilot is PROVEN with the env-var recipe correction;
    migration not done, RDP stays primary. UNQUANTIFIED.
G8. RDP debuggability and Firefox-version drift (Q29, Q30).
    Sourced, untested, UNQUANTIFIED.
G9. Snapshot-ref invalidation semantics (Q36). Residual only;
    the base I3 mechanism landed.

Dead or spent, excluded from the ranking and verified against
the landing records: Q4's core (the four zen_live.py defects
are fixed and live-tested; residuals are the move-tab index
semantics and a CLI exit-code side finding, UNVERIFIED on the
landed copy), Q42, Q43, Q38, Q39, Q40, Q45 (all landed or
spent as confirmations). One orphan: correction W17 (remove
lingering CDP assumptions) has no queue entry and no landing
record.

## What the meeting should notice

- The top of the minute ranking (items 1, 2, 5, 6, 8) is
  process and staffing pain: cap exposure, post-run
  processing, deliberation volume, coordinator continuity,
  owner waits. None of it has a queue entry, and only item 2
  has an M item. If the sweep only funds code, the largest
  burns stay untouched.
- Two of the top four ranked pains already have mitigations
  recorded as merged (M11d for item 3, M28a for item 4) whose
  effect has never been re-measured, and M28a's lane
  switch-over is still an open coordinator decision.
  Ranking residual burn, not
  historical burn, requires one cheap re-measurement pass
  after the next graded run and one week of watchdog volume.
- The cheapest fully-specified fix with a measured price is
  the 429 policy (item 7, M12): a single incident cost
  245.0 min and the policy is a document plus a retry rule,
  not a build.
- The largest code-side unknown is G1: the AT-SPI walk. Its
  settling measurement (U4, five variants) is specified,
  pre-registered, and blocked only on a machine with AT-SPI
  bindings. Until it runs, every walk saving in the queue is
  PROJECTED.
- The M17 shard tool has a live defect found today: it
  crashes on a whole-budget timeout instead of reporting, and
  on a CPU-capped machine it is slower than serial. Sharding
  should not be the default verification path until the
  timeout handling is fixed and the multi-core sign is
  measured.
- Two numbers the project has never recorded would change
  future rankings: minutes per watchdog round (item 4) and the
  audit share of the ledger tail (item 2). Both are one line
  of logging each.

## Evidence index

- Lane A figures: bottleneck study
  (improvements/bottleneck-study-20261127.md), git and gh
  counts re-run 2026-11-28 over all branches, rung3-run-log
  grades, docs/clone2-watchdog-log.md.
- Lane B figures: idea queue
  (improvements/idea-queue-20261127.md), pilot results
  (improvements/pilot-results-20261127.md), M ranking
  (improvements/m-remaining-ranking-20261127.md), integration
  phase report, adoption decision doc. The queue's section 4
  UNVERIFIED quarantine is carried forward untouched; nothing
  in this audit rests on quarantined material.
- Lane C figures: live runs on clone2's VM 2026-11-28, record
  in ~/workspace/pain-audit-out/ (lane-c-measured.md and the
  preserved shard-crash and zen-rdp suite logs; the serial
  and timeout-600 figures rest on lane C's written record,
  their raw logs were not preserved). The VM is a
  shared sandbox capped at 1.5 CPU with 6 GB RAM, not the
  owner's machine; absolute times do not transfer, ratios and
  orders of magnitude are the signal.

## Review record

Council (2 reviewers) plus redteam, 2026-11-28. Council
fidelity found the M11d and M28a merged status unsupported by
the lanes; it is now cited to the integration phase report
directly (items 22 and 23, with their caveats). Council
method forced the per-item clock tags, the non-comparability
sentence for items 4, 5, 8, 13, and 14, the closed-class note
on item 11, and the M1 and M4 status lines. Redteam verified
the headline figures reproduce (62.4 h, the 954 min split,
the shard-crash traceback in the preserved log) and forced
the overlap note, the single-cycle basis limitation, the
item 4 average-versus-peak correction, and the evidence-index
log correction. No figure was found fabricated; no BLOCKING
finding remains open.
