# Remaining bottleneck-study M items, ranked by time saved (2026-11-27)

Sources. The bottleneck study:
improvements/bottleneck-study-20261127.md on todolist-push
(commit 26b1133d), read in full. Integration status:
improvements/integration-phase-20261127.md on
origin/integration-20261127 (read at branch tip 97d22c70 on
2026-11-27). The idea queue
(improvements/idea-queue-20261127.md) was also checked: it
contains no M-item references at all, so integration status
rests entirely on the integration-phase report.

What counts as integrated: the integration-phase report
marks M16 (item 2, IMPLEMENTED), M17 (item 3, IMPLEMENTED +
MEASURED) and M2 (item 7, IMPLEMENTED). Those three are
excluded below. Everything else in the study register is
either QUEUED in that report's first batch (M14, M7, M11c,
M11d, M28a, the guidance set M18-reduced / M20 / M23 /
M28d / M29 / M34f-rule, M10-reduced), listed there as a
pilot that has not reported, or an owner-only
recommendation (M25). None of those count as integrated.

Savings rule: every figure below is a number the study
itself measured or stated, cited to the study section it
came from. Where the study gives no number, the saving is
marked UNQUANTIFIED and no figure is invented. The study
forbids summing savings across proposals that share a pool,
and its three clocks (staffed cycle minutes, calendar and
ceiling exposure, volume and attention) must not be summed;
this ranking keeps each figure on its own clock and never
adds them.

Qualitative rule for UNQUANTIFIED items, applied in
section 3 after all items with a study-stated figure:
(a) study verdict first (ADOPT before PILOT-FIRST);
(b) the size of the pool the item touches on its own clock;
(c) dependency order named in the study; (d) running cost
and risk, proven-cheap and low-risk first. Items that claim
zero or no saving, and items only the owner or a fallback
condition can activate, close the list.

## 1 and 2. Remaining items: definition and time saved

### M1, parallel-ledger release (PILOT-FIRST)
- Definition: release a task on two-verdict agreement and
  audit asynchronously, keeping audit-before-release for
  Class L and flagged grades.
- Time saved: UNQUANTIFIED share of a stated pool. The
  study names M1 the only minute claimant against the 420
  minute ledger tail of the 1,729 minute R3-L3 cycle (the
  other 534 post-run minutes are scoring lag), and states
  the share is unmeasured: the audit share of the tail is
  measured first, and if it lands under 10 percent M1
  closes as a negative result (study sections 1 and 2).

### M4, Class L hash-check decoupling (PILOT-FIRST)
- Definition: laptop handover for Class L tasks; the live
  re-read stays the default and any mismatch permanently
  reverts that task type.
- Time saved: 87.1 measured minutes of runner idle across
  9 tasks, the prize the pilot plays for; promotion needs
  zero mismatches across a full run of Class L tasks
  (study sections 1 and 2).

### M5, duplicate handling, converged form (PILOT-FIRST)
- Definition: storage-layer dedupe with loud alias entries
  that never assert evidence equivalence, the duplicate
  screen firing on every occurrence, and human review on
  duplicates-plus-anomaly.
- Time saved: UNQUANTIFIED. The study states no time
  figure; the item's value is correctness (it replaces a
  landed hard-fail rule that provably rejects 7 genuine
  PASS evidence sets of 59, study section 3).

### M6, JPEG for intermediate screenshots (PILOT-FIRST)
- Definition: JPEG for intermediate screenshots now; graded
  and text-bearing shots stay PNG until a scorer legibility
  trial shows zero verdict changes.
- Time saved: UNQUANTIFIED. Screenshot capture itself is
  proven not a bottleneck (36-58 ms, study sections 1 and
  3), so the stake is token and storage volume, which the
  study never quantified.

### M7, stall and latency detector, parts a and b (ADOPT)
- Definition: a detector that flags stalls and scoring
  latency for human judgement only; it may never trigger
  or pre-authorise a takeover.
- Time saved: detection latency only, by the study's own
  claim (section 2). Anchors on the calendar clock: about
  235 minutes of documented continuity episodes, including
  the 2026-11-27 R3-056 stall (silent 70 minutes, detected
  by peers after about 40 minutes of watching) (section 1).
  The analysis script is proven at 0.038 s (section 2).

### M9, owner-decision defaults (PILOT-FIRST)
- Definition: the owner pre-writes a default per question
  class before a run; invalid-budget and grading-rule
  classes are permanently excluded; pilot on exactly one
  already-ruled class.
- Time saved: UNQUANTIFIED share of a stated baseline: the
  pilot counts events against the 126 minute baseline of
  the epoch 22 HOLD (deputy hold to resume, study sections
  1 and 2).

### M10 (reduced), pre-calibrated spare scorer (ADOPT)
- Definition: pre-calibrate one named spare scorer at run
  start; no standing warm seat.
- Time saved: UNQUANTIFIED, and zero cap hours are claimed,
  ever. The study relabels "calibration is cheap" as
  DOCUMENTED, not measured (sections 2 and 3).

### M11a, pre-flight credential, URL and fixture check (PILOT-FIRST)
- Definition: check presence and format only before a run;
  never a live login.
- Time saved: claimed for the 40 minute class only (the
  pre-flight failure class). The larger 272 minute gap it
  also touches has an UNVERIFIED split between password
  wait and scheduling, and the study claims nothing
  against it (sections 1 and 2).

### M11b, bot-wall probe in the runner's own session (PILOT-FIRST)
- Definition: probe for bot-check walls inside the runner's
  own session; it informs only, and substitution stays a
  coordinator decision. Laptop handover.
- Time saved: UNQUANTIFIED. The study claims no saving for
  the probe itself. Its pool on clock A: six of 59 graded
  L3 rows INVALID from bot-wall service failures, 71.8
  runner minutes plus two blind gradings each (section 1).
  The fixture result behind it is code-runs evidence only
  (section 3).

### M11c, Marionette pre-flight session check (ADOPT, check half)
- Definition: run a cheap session check before work;
  restart only after an actual session-creation failure,
  never on an error string match.
- Time saved: UNQUANTIFIED. The check's cost is proven
  (0.01-0.19 s on Zen 1.24.3b, section 2); the wedge it
  detects cost 9 failed session creations, one browser
  restart and a 55-tab cleanup redo in the recorded
  instance, with no minutes figure stated, and the wedge
  trigger remains unreproduced (section 1).

### M11d, pre-freeze triage of the task list and keys (ADOPT)
- Definition: move the triage that caught L2's 18 text
  defects to before the freeze: a time-boxed human triage
  with the mandatory bar written down first, plus the
  mechanical verify-list gate.
- Time saved: up to 432.5 runner minutes plus a cancelled
  run generation per affected run, claimed only as an "up
  to" figure (section 2). The mechanical gate is proven
  trivial: 62 checks in 75 ms (section 2). The catch rate
  must be reported after first use.

### M12, adopt the drafted 429 rule (PILOT-FIRST)
- Definition: adopt the rule already drafted in
  coord/mei.md section 9, in pilot form: total backoff
  window widened to 30-45 minutes with jitter, every
  invocation logged with its outcome.
- Time saved: it caps an observed loss of 245.0 minutes on
  one task (the R3-040 FAIL retry run, the longest in L2,
  run because no retry rule existed) (sections 1 and 2).

### M13, Tier A result language and checker widening (split)
- Definition: pin the Tier A result language in runner
  briefs now (the adopted half); widen the checker to both
  formats only after it also proves it still rejects the
  preserved R3-002 fabrication patterns (the pilot half).
- Time saved: UNQUANTIFIED. The study states no figure for
  either half (section 2).

### M14, adversarial probe gate before executor changes (ADOPT)
- Definition: the frozen Y1b probe suite stands in front of
  executor changes; probe changes go through full council
  plus redteam, and a suspiciously fast pass is a flag.
- Time saved: avoidance of a failure class that took about
  24 hours of multi-lane remediation (the Y1b sandbox
  cluster also gated the serial queue for about 24 hours
  of commit window) (sections 1 and 2). Expected saving
  per period is UNQUANTIFIED because it depends on
  recurrence; the gate's own cost is proven: the suite
  passes 4/4 in 15.478 s (section 2).

### M15, defective-test register (PILOT-FIRST)
- Definition: a register of defective tests, every entry
  carrying branch lineage (merge-base checked), an owner,
  and an expiry that deletes.
- Time saved: UNQUANTIFIED. The study states no figure for
  the register itself (section 2). The repeated-suite
  figures nearby in the study (a full discover at 95 to
  374 s, 39 logged runs summing to 9,390 s) belong to the
  M17 and M18 pools and are not claimed here.

### M18 (reduced), module-first change-scoped runs (ADOPT, guidance only)
- Definition: module-first runs as written dev-loop
  guidance; the full discover stays mandatory at every
  gate. The automatic selection half is rejected (see
  section 4).
- Time saved: a module runs in 2.217 s against 365 s for
  the full discover, a difference of about 363 s per
  dev-loop invocation (section 2). The study is explicit
  that this proves speed, not selection safety, and no
  gate time is saved because gates keep the full run.

### M19, persistent tc02 client (PILOT-FIRST, conditional)
- Definition: keep one tc02 client process alive instead of
  paying import per spawn; only if tc02 Step 3 happens for
  other reasons.
- Time saved: an UNPROVEN projection capped at about 11 s
  per session (the tc02 transaction pool, one claimant,
  sections 2 and 3). Only the direction is proven: the
  import costs 228-270 ms per spawn (section 2).

### M20, one-shot DOM harvests as a coding rule (ADOPT)
- Definition: new code harvests the DOM in one shot instead
  of per-element calls, with an element-set payload cap.
- Time saved: UNQUANTIFIED at run level. The study states
  no run-level saving until a census of remaining
  per-element call sites exists and one conversion is
  timed; the mechanism ratios it proves (11x local BiDi
  median, 54x in the repo's Marionette bench) are
  transport-specific and none is quoted as transferable
  (section 2).

### M21, predicted-crop OCR (PILOT-FIRST)
- Definition: keep the already-landed predicted-crop OCR
  practice; any future saving claim needs a before/after
  on a tesseract machine over pages not used to tune the
  predictor.
- Time saved: zero claimed. The study records it as
  already-landed practice claiming no new saving, locally
  UNPROVEN because clone2's VM has no tesseract (section
  2).

### M23, bounded and batched git output (ADOPT, hygiene)
- Definition: bound and batch git output in scripts
  (for example log -20 instead of log --all).
- Time saved: UNQUANTIFIED in total. Per-command medians
  are proven (log -20 at 0.392 s against log --all at
  0.843 s), but the study deliberately puts M23 in no
  savings table because the total depends on an UNVERIFIED
  loop frequency (section 2).

### M25, risk-tiered review (RECOMMENDATION TO THE OWNER ONLY)
- Definition: tier review depth by risk. The study makes
  this a recommendation to the owner only; no lane builds
  it (sections 2 and 3).
- Time saved: UNQUANTIFIED. It aims at the deliberation
  pool (71,971 lines, about 38 percent of improvements/
  documentation, section 1), whose waste share the study
  states is NOT measured (conflict C8, sections 1 and 3).

### M26, verdict template with a line cap (PILOT-FIRST)
- Definition: a verdict template with a line cap; every
  capped verdict carries a "dropped for length: N" count,
  and the cap never applies to BLOCKING findings.
- Time saved: UNQUANTIFIED. The supporting experiment was
  downgraded from PROVEN to UNPROVEN in the debate (one
  artifact, two different agents, no recall measurement),
  so the pilot must measure findings recall against a
  free-form arm before any saving can be stated (sections
  2 and 3).

### M27, two-round re-review cap (PILOT-FIRST)
- Definition: cap re-review at two rounds, but only after a
  retro-count of blocking findings first raised in round 3
  or later across all chains in improvements/; if that
  count is nonzero the cap becomes "round 3 requires a
  named new-evidence reason".
- Time saved: UNQUANTIFIED in minutes. Volume anchor only:
  the R3-L3 final chain's rounds 3 and 4 produced 911
  lines across 8 sessions with zero blocking findings
  (section 1). The "proven on historical data" label was
  downgraded to UNPROVEN as a policy (section 3).

### M28a, watchdog rolling branch (ADOPT, append-only form only)
- Definition: one rolling branch per lane, append-only and
  never force-pushed, a PR opened on material flags as
  today, plus a periodic rollup PR so the log lands on
  main. The coordinator has approved this form
  (integration-phase report, coordinator decisions).
- Time saved: stated in counts only, never minutes, by the
  study's own ruling: about 476 PR creations per lane per
  period avoided, about 90 percent of watchdog commit
  ceremony (section 2). Context: 2,001 of 4,732 commits
  and 1,017 of 1,109 PRs are watchdog traffic (section 1).

### M28b, watchdog daily rollup (PILOT-FIRST, fallback only)
- Definition: a daily rollup of watchdog logs; fallback
  only if M28a is refused, never both.
- Time saved: UNQUANTIFIED. No figure stated (section 2).

### M28d, exempt mechanical log appends from the small-commit rule (ADOPT)
- Definition: mechanical log appends no longer need the
  small-commit ceremony.
- Time saved: UNQUANTIFIED. The study calls the item
  trivial with negligible risk and states no figure
  (section 2).

### M29, written no-council class for status, ack and log artifacts (ADOPT)
- Definition: a written class of format-only artifacts
  (status, ack, log) that needs no council; any artifact
  asserting another lane's liveness or a stall is outside
  the exemption.
- Time saved: UNQUANTIFIED. No figure stated; peer
  corrections are counted for a week as monitoring
  (section 2).

### M30, package reviews of small homogeneous items (PILOT-FIRST)
- Definition: review small, homogeneous, low-tier items in
  packages, findings per item compared against solo
  review; runs only after M26's pilot.
- Time saved: UNQUANTIFIED. No figure stated (section 2).

### M31, guard-block snippet library (PILOT-FIRST, library half only)
- Definition: a manually pasted library of guard blocks for
  briefs; the generator half is rejected (section 4).
  Pilot: five briefs diffed against hand-written
  equivalents, zero guard drift required.
- Time saved: UNQUANTIFIED. The naive brief-templating
  saving was refuted by measurement (16 percent shared
  lines in scorer briefs, section 3), so the library
  claims nothing until its own diff pilot reports.

### M32, versioned run kit (PILOT-FIRST, tooling half only)
- Definition: a versioned run kit; the calibration bank
  half persists only if re-validated per generation at
  clearly less than a fresh calibration's cost.
- Time saved: UNQUANTIFIED. No figure stated (section 2).

### M33, branch hygiene (PILOT-FIRST, sequenced)
- Definition: clean up the branch sprawl, sequenced
  strictly after M28a lands the watchdog record somewhere
  durable; verdict branches excluded permanently; dry-run
  list reviewed first.
- Time saved: UNQUANTIFIED. No minutes figure; context is
  898 remote branches (706 watchdog, 78 coord, 67 verdict)
  (sections 1 and 2). Sequencing hazard: running M33
  before M28a would delete the only complete copy of the
  watchdog record (section 3).

### M34a, prompt caching (PILOT-FIRST, measurement only)
- Definition: measure prompt caching, starting with whether
  the harness exposes cache controls at all.
- Time saved: UNQUANTIFIED for this project. The only
  numbers the study cites are an external vendor table
  (section 4), and imported constants are banned as this
  project's rates (see M34f in section 4).

### M34b, viewport-limited accessibility trees (PILOT-FIRST)
- Definition: viewport-limited accessibility trees for
  navigation hints only, never grading, verification or
  final-state reads.
- Time saved: UNQUANTIFIED. No project figure stated
  (section 2).

### M34c, DOM snapshot cache (PILOT-FIRST)
- Definition: cache DOM snapshots, only after a
  mutation-detection test with zero tolerated misses.
- Time saved: UNQUANTIFIED. No figure stated (section 2).

### M34d, sparse checkout timing pilot (PILOT-FIRST)
- Definition: time sparse checkout on this repo.
- Time saved: UNQUANTIFIED until the pilot runs. The study
  expects the pilot's own figure to be in minutes and bans
  the external ratio from reporting (section 2).

### M34e, CI batching (PILOT-FIRST, measurement only)
- Definition: measure CI batching; if the project's own
  cancelled-run share is small it closes as a printed
  negative result.
- Time saved: UNQUANTIFIED. No figure stated (section 2).

### M34f, two-clock pricing rule (ADOPT, rule only)
- Definition: every deliberation proposal and parallel-lane
  plan is priced in wall time AND tokens. The imported 15x
  constant is rejected (section 4).
- Time saved: UNQUANTIFIED. The rule saves nothing by
  itself; it disciplines the pricing of other proposals
  (section 2).

## 3. Priority order for the remaining items

Order rule: study-stated time figures first (largest pool
or ceiling first, keeping each figure on its own clock),
then the qualitative rule of the header (verdict, pool,
dependency, cost and risk). One line of justification per
item.

1. **M11d** - largest stated ceiling: up to 432.5 runner
   minutes plus a cancelled run generation per affected
   run, ADOPT, and its mechanical gate is proven trivial.
2. **M1** - largest recurring pool: the 420 minute ledger
   tail in every R3-L3-scale cycle; the pilot's first step
   is only five tasks of timestamped instrumentation.
3. **M12** - caps a proven 245.0 minute single-task loss
   and the rule text already exists, so the pilot is cheap
   to start.
4. **M14** - stands in front of a failure class that cost
   about 24 hours of multi-lane remediation; ADOPT, with a
   proven running cost of 15.478 s.
5. **M9** - plays against a 126 minute measured baseline
   per HOLD episode of a ruled class; the pilot is event
   counting on one class only.
6. **M4** - 87.1 measured idle minutes per Class L run set;
   ranked below the VM-advanceable items because its pilot
   is laptop-bound.
7. **M7** - buys detection latency on a 235 minute
   continuity pool (one stall ran about 40 minutes before
   detection); ADOPT, script proven at 0.038 s.
8. **M11a** - saving claimed for the 40 minute pre-flight
   class per occurrence; checks are presence and format
   only, so the pilot is cheap and safe.
9. **M11b** - touches the 71.8 runner minute bot-wall pool
   but saves nothing directly (it informs a coordinator
   decision) and is laptop-bound.
10. **M18 (reduced)** - about 363 s saved per dev-loop
    module run against the 365 s full discover; guidance
    only and gates keep the full run, so risk is minimal.
11. **M28a** - no minutes claimable, but it removes about
    476 PR creations per lane per period (about 90 percent
    of watchdog ceremony), the coordinator has approved
    the form, and it is the precondition for M33.
12. **M19** - capped at about 11 s per tc02 session and
    UNPROVEN; worth doing only if tc02 Step 3 happens for
    other reasons.
13. **M29** - ADOPT; removes council ceremony from pure
    format artifacts at trivial risk, with the liveness
    and stall assertions carved out.
14. **M34f (rule only)** - ADOPT; costs no build and prices
    every later deliberation and parallel-lane proposal in
    wall time and tokens.
15. **M20** - ADOPT coding rule; stating it costs nothing
    and its census is the precondition for any later
    run-level saving claim.
16. **M28d** - ADOPT; a trivial exemption with negligible
    risk.
17. **M23** - ADOPT hygiene; the per-command gain is proven
    (0.392 s against 0.843 s medians) even though the total
    stays UNQUANTIFIED.
18. **M11c** - ADOPT check half at 0.01-0.19 s per check;
    the wedge it detects once cost a browser restart and a
    55-tab cleanup redo, but the trigger is unreproduced.
19. **M10 (reduced)** - ADOPT process item; claims no cap
    hours, its value is continuity insurance for the scorer
    seat, and calibration cost is DOCUMENTED only.
20. **M26** - PILOT aimed at the deliberation pool (71,971
    lines, waste share unmeasured); its recall pilot also
    gates M30.
21. **M27** - PILOT whose first step, the retro-count of
    late-round blocking findings, is cheap and decides
    whether the cap is safe at all.
22. **M5** - PILOT; saves no measured time but retires a
    landed rule that provably rejects 7 genuine PASS
    evidence sets of 59, a correctness risk to every future
    graded run.
23. **M15** - PILOT; the register underpins the landed M16
    and M17 hygiene and every future suite run.
24. **M13 (pilot half)** - checker widening gated on still
    rejecting the preserved R3-002 fabrication patterns;
    the language-pinning half is already adopted.
25. **M31 (snippet library)** - PILOT with a hard gate:
    five briefs diffed, zero guard drift required.
26. **M32 (tooling half)** - PILOT; the calibration bank
    survives only if re-validation clearly beats fresh
    calibration cost.
27. **M30** - PILOT; dependency order, it runs only after
    M26's pilot reports.
28. **M33** - PILOT; dependency order, strictly after M28a
    lands the watchdog record somewhere durable.
29. **M34a** - measurement only; the first question is
    whether the harness exposes cache controls at all.
30. **M34c** - gated on a mutation-detection test with zero
    tolerated misses before any cache is trusted.
31. **M34b** - navigation hints only; fenced off from
    grading, verification and final-state reads by design.
32. **M34d** - timing pilot on this repo; the study expects
    a minutes-scale figure and bans the external ratio.
33. **M34e** - measurement only and may honestly close as a
    printed negative result.
34. **M6** - capture is proven not a bottleneck (36-58 ms),
    so only unquantified token and storage volume is at
    stake.
35. **M21** - already-landed practice claiming no new
    saving; any claim needs a tesseract before/after no
    worker VM can run.
36. **M25** - recommendation to the owner only; no lane can
    build it, listed so it is not mistaken for queued work.
37. **M28b** - fallback only; the coordinator approved
    M28a, so this activates only if M28a is refused in
    practice or fails its post-adoption check.

## 4. Rejected or superseded: do not integrate

From the study's rejected list (section 2) and debate
record (section 3):

- **M3, verify-once receipt. REJECTED.** It replaces each
  scorer's independent key and manifest verification with
  trust in one gate run; independent verification is the
  mechanism that keeps frozen keys frozen, and the residue
  that survives (a receipt as an extra artifact) saves
  nothing.
- **M8, standing deputy with 15-minute automatic takeover.
  REJECTED.** The trigger is the defect: 15 minutes of
  coordinator silence is proven-normal in this record, and
  the failure mode is a forked grading ledger. A rehearsed
  handover on positive evidence of a stall would be a
  different, owner-approved proposal.
- **M22, standalone load_image fix. REJECTED as a
  standalone.** A real defect with a saving ceiling of
  0.22-0.37 s per task, below the cost of the review set a
  standalone change consumes; recorded as a drive-by for
  the next substantive tc02 change only.
- **M24, lower timeout ceilings. REJECTED.** No saving
  stated by its own lane, no wedge reproduced, frequency
  UNVERIFIED, and the proven risk runs the other way
  (R3-037's 30-minute timeout FAIL). Instrumentation is
  the precondition for any future version.
- **M28c, watchdog auto-merge. REJECTED.** It would flood
  main with a log that has already carried owner-corrected
  false flags once; M28a reaches the readability goal
  without touching main.
- **M28a, force-updated branch form. REJECTED.** A
  force-updated branch is a rewritable audit record; only
  the append-only form was adopted (see M28a in sections 1
  and 3).
- **M31, brief generator. REJECTED.** A wrong generated
  brief looks authoritative and feeds blind scoring; only
  the manually pasted snippet library survives, as a pilot
  (see M31 in sections 1 and 3).
- **M18, automatic coverage or trace-based test selection.
  REJECTED.** The measured external result is negative
  (about 2 percent of test-seconds saved, no run shortened,
  skip rules that missed files and one that broke
  production); it returns only with an escape budget and a
  skip audit.
- **M34f, the imported 15x token constant. REJECTED.** One
  vendor's internal evaluation figure is not this project's
  exchange rate; the two-clock pricing rule was adopted,
  the constant was not.
- **M5, pure-alias form. KILLED in debate.** It normalises
  the duplicate-hash signal that caught the project's one
  documented fabrication, inside the evidence format
  itself; only the converged storage-layer form in
  sections 1 and 3 survives.
- **The landed hard-fail duplicate rule. SUPERSEDED** by
  M5's converged form: it provably rejects 7 genuine PASS
  evidence sets of 59 and must not be treated as current
  policy (study section 3).

Already integrated, for the record (excluded from the
ranking): M16, M17 and M2, per the integration-phase
report items 2, 3 and 7.

Clone2 analysis, 2026-11-27. English only. No personal
information in this document.
