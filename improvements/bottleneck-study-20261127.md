# Whole-project bottleneck study (clone2, 2026-11-27)

Scope: the computer-use-wayland project from its start to
2026-11-27, all lanes, all runs. Method: eight parallel research
lanes (waiting time, repeated steps, error rework, deliberation,
tool latency, git overhead, external sources, and a red team
against the study's own framing), one synthesis register, then
two debate rounds (three council scorers plus a red team in
round 1; a convergence council plus a second red team in
round 2). Every proposal below carries its final verdict from
that debate, not just the lane that proposed it.

Two laws governed the study, set by the owner on 2026-11-27.
Source law: every cited source was actually opened; repo sources
are cited by path and commit; external sources by URL with
access date 2026-11-27; anything not opened or not verifiable is
labelled UNVERIFIED and never stated as fact. Proof law: a claim
or proposal counts as proven only if it was run for real on
clone2's machine with measured before and after numbers;
everything else is labelled UNPROVEN, with the pilot that would
prove it named.

One source note, stated plainly: the owner supplied a full
events.log archive as the intended primary source. It could not
be downloaded from clone2's machine (the direct request was
refused and the browser route is policy-blocked), so it is an
UNOPENED source and no claim in this report rests on it. The
evidence base is the project record itself: rung3-run-log/,
improvements/, rung3-ci/, the coord files, and the git history,
all read at the fix-review checkout tip 91547db1 on 2026-11-27.
If the archive is attached directly in chat later, a
supplementary pass can re-check the waiting-time figures
against it.

Study cost, stated because the study's own red team demanded
it: 15 subagent sessions (8 lanes, 1 synthesis, 4 debaters in
round 1, 2 in round 2) plus coordinator time, roughly 45
minutes of wall clock. Token spend is UNMEASURED; no timesheet
exists for any figure in this report either, which is why
several totals below are volumes, not times.

## 1. The bottlenecks, ranked on three separate clocks

The debate's first ruling (conflict C14) is that this project
loses time on three clocks that must not be summed: staffed
cycle minutes inside a run, calendar and ceiling exposure, and
volume and attention. There is no honest exchange rate between
them, so there are three rankings, not one.

### Clock A: staffed-cycle minutes inside a run

The one complete partition in the record is the R3-L3 graded
cycle, computed from rung3-run-log/R3-L3-grades.jsonl: 1,729
minutes total, of which driving is 775 (44.8 percent), scoring
lag is 534, and the ledger tail after both scorers agreed is
420. Post-run processing is therefore 954 minutes, 55 percent
of the cycle, and it is bottleneck number one on this clock.
Inside it, the 420 minute tail is the mechanical part (about 15
boundary operations per task: collect, manifest handling,
pii-scan, snapshot, gate, push, two scorer verifications,
coordinator audit, two ledger validators). The 534 is mostly
scorer thinking time: the heartbeat log's maximum unscored
queue depth is 2, so it is serial latency, not a backlog, and
most of it is the price of blind double grading, not waste.
How much of the tail is audit versus recording is NOT settled
(conflict C6); nobody has timestamped the audit step.

Second on this clock: frozen spec defects. R3-L2 was cancelled
after 11 graded rows totalling 432.5 runner minutes of driving
were discarded, and the whole run was re-done as L3. The cause
was 18 text defects in the task list and keys (2 mandatory),
found by a triage that ran after the freeze instead of before
it.

Third: bot-check walls rooted in the webdriver signal. Six of
59 graded L3 rows are INVALID and all six are external service
failures (timeanddate, Google, Openverse, Coolors, Namechk,
Ezgif): 71.8 runner minutes, two blind gradings each, three
tasks dropped from the denominator, the invalid budget
exhausted, an owner re-plan forced, and the R10 response arc
(24 documents, 4,755 lines, about 9 hours of wall time on
2026-11-27) that eventually replaced the lane. The timeanddate
cluster alone put four tasks under one shared cause.

Fourth: error classes with no pre-agreed policy. One HTTP 429
episode (R3-040) cost a 245.0 minute FAIL retry run, the
longest in L2, because no retry rule existed; the rule was
drafted only afterwards. Runner fabrication on the earliest
tasks (R3-002 three times, R3-003) cost about 100 minutes of
windows plus 37.2 minutes of Rule-A re-runs and seven gradings.
The Y1b executor sandbox cluster gated the serial queue for
about 24 hours of commit window. The Marionette single-slot
wedge struck twice (9 failed session creations, one browser
restart, a 55-tab cleanup redo) and its trigger was never
reproduced, then or in this study.

Fifth: repeated test-suite runs. A full discover takes 95 to
374 seconds depending on suite size, and every worker, council,
redteam and verifier lane runs its own. Thirty-nine explicit
run lines in improvements/ sum to 9,390 seconds (an upper bound;
runs are re-quoted across logs). One fix consumed four valid
full runs totalling 1,010 seconds.

Sixth: Class L score-before-reset blocking, 87.1 measured
minutes of runner idle across 9 tasks, a safety rule's known
price.

Proven NOT bottlenecks on this clock, recorded so nobody
optimises them: hashing (the whole 231 MB evidence corpus
hashes in 2.18 s), screenshot capture (36-58 ms), RDP attach
(3.0-4.5 ms) and DOM reads (0.3-0.9 ms), and the seal chain's
machine time (1.10 s on the largest evidence set).

### Clock B: calendar and ceiling exposure

The largest single loss in the whole record sits here and is
not close: usage caps. Clone2 was capped from about 12:14 on
2026-11-22 to the reset at 02:38 on 2026-11-25, about 62.4
hours (two cited timestamps; the run's own span is only about
39.4 hours). The re-plan gated the entire run start on capped
members unlocking; a scorer seat stood empty for the run's
first 18 hours. Cap losses leave no trace in run logs, so any
lane that sums logged activity structurally misses them. No
proposal in this study reduces the cap itself; the only levers
are token spend per unit of work (deliberation pricing) and not
wasting capped hours when they return.

Second: coordinator continuity. Fifteen takeovers across the
run, epochs 15, 16 and 17 inside 26 minutes on 2026-11-26,
about 235 minutes of documented continuity episodes, including
the 2026-11-27 stall on R3-056 (silent 03:31 to the owner's
04:41 decision, 70 minutes, detected by peers after about 40
minutes of watching). The coordinator is also the only ledger
pusher, so every continuity failure lands directly on clock A.

Third: owner waits on already-ruled question classes. The
epoch 22 HOLD cost 126 minutes (deputy hold 15:18, resume
17:20); a full-run HOLD on 2026-11-25 sat at least 65 minutes
inside a 166 minute gap; R3-029 waited inside a 272 minute gap
partly for a parent-supplied password (the split between
password wait and scheduling is UNVERIFIED). Post-run, the
coordinator was silent from 07:48 on 2026-11-27 until the
owner's nudge at 09:59, 131 minutes. Owner time in total is
UNPROVEN and unranked by design: no log of it exists, and
inventing one would be fabrication.

Fourth: one laptop, one driver slot. The shared-resources
rules document a single cursor lock, a shared browser, serial
message sends. The 633 minutes of merged-timeline gaps are an
upper bound mixing contention, holds and nights, and must not
be attributed to the machine wholesale.

### Clock C: volume and attention

First: the watchdog machine. Of 4,732 commits in the project,
2,001 (42 percent) are watchdog commits; of 1,109 PRs, 1,017
(92 percent) are watchdog PRs. Clone2's 476 watchdog PRs are
all still open, zero merged; clone1's 539 were mostly merged.
The consequence is an integrity harm, not just noise:
docs/clone2-watchdog-log.md on main was last updated
2026-11-23 (commit edcfc363) and is frozen, while the real
record scatters across 476 unmerged branches, which are
currently the only complete copy of that record. There are 898
remote branches (706 watchdog, 78 coord, 67 verdict).

Second: deliberation volume. Council and redteam output is
71,971 lines across 273 entries in improvements/, about 38
percent of all improvements/ documentation (187,560 lines);
344 of 1,951 commits (17.6 percent) mention council or
redteam; there are at least 56, plausibly 100+, distinct
review sets of at least four sessions each. Where it
concentrates: re-review tails (the R3-L3 final chain's rounds
3 and 4 produced 911 lines, 8 sessions, zero blocking
findings), fix-pass loops (one translation-review task
accumulated 30 review files and 13,634 lines through fix8),
and single decisions (the R10 decision consumed about 5,900
lines). The volume is proven; the waste share is NOT. The
counter-evidence is real: the Zen folder-tool council pass
caught two HIGH defects now locked in as tests, both CF735368
BLOCKING flags from single-reviewer work were later
vindicated, and the R3-L2 triage's own post-mortem records a
council misclassifying 11 of 13 amendments toward more
mandated work. Whether the current spend is mostly waste or
mostly integrity is unsettled (conflict C8) and every proposal
touching it is a pilot designed to measure exactly that.

Third: commit ceremony. Median commit size is 10 lines; 699
commits (14.8 percent) change five lines or fewer; 439 change
at most one line. About 723 subjects (15.3 percent) mention a
fix, a crude upper bound on rework's share.

## 2. Proposals: the converged register

Thirty-four proposals (M1-M34, counting lettered sub-items
separately where the debate split them) came out of the lanes.
Verdicts after two debate rounds: ADOPT means do it, with the
stated conditions; PILOT-FIRST means the named pilot runs
before any adoption, and the proposal is UNPROVEN until it
reports; REJECTED means eliminated, with the reason recorded
in section 3. Savings are never summed across proposals that
share a pool: the post-run 954 minutes have exactly one minute
claimant (M1, against the 420 tail only, share unmeasured);
the continuity episodes have one claimant (M7, detection
latency only); the tc02 transaction (about 11 s per session)
has one claimant (M19, capped, unproven); the deliberation
family claims nothing in aggregate because its pool's waste
share is unmeasured.

### Do first, in order

1. **M16, hermetic-suite gate in CI (ADOPT).** Run the test
   discover in a tool-stripped environment so missing-tool
   defects fail in CI instead of in a lane. PROVEN detector:
   the tc02 tesseract pair reproduces its exact batch-12
   failure in 0.038 s without tesseract, and the fix for that
   pair is on main but NOT on todolist-push (merge-base
   proven), so the defect is live today on the branch the runs
   use. The gate is a detector for this class, never a
   hermeticity certificate, and the lineage check (fix present
   on the branch in use) is part of the gate. Break-even: about
   six recurrences on convention arithmetic; the first
   prevented recurrence is the next todolist-push discover.
2. **M17, shard the full discover (ADOPT).** PROVEN on this
   machine: 2,433 tests, serial wall 365 s, four size-balanced
   shards wall 232 s (1.57x, 133 s saved per run), shard sums
   reproducing the serial totals exactly (10 failures, 270
   errors, 17 skipped). The serial run stays the gate of
   record; any shard versus serial mismatch quarantines
   sharding until explained in writing, and the comparison
   must be per-test identity, not totals only. The 1.57x is a
   1.5-CPU VM figure and will differ on the laptop. Break-even
   about 47 four-lane verification cycles; the logged sample
   (39 full runs in about 9 days) reaches that inside one
   phase.
3. **M11d, pre-freeze triage of the task list and keys
   (ADOPT).** Move the triage that caught L2's 18 defects to
   before the freeze. The mechanical gate is proven trivial
   (rung3-ci/verify-list.py, 62 checks in 75 ms); the value is
   the scheduled human triage, time-boxed, with the mandatory
   bar written down first and the triage's own documented
   over-classification failure (11 of 13) cited in its brief.
   Saving claimed only as "up to" 432.5 runner minutes plus a
   cancelled generation per affected run; the catch rate must
   be reported after first use.
4. **M1, parallel-ledger release (PILOT-FIRST).** Release a
   task on two-verdict agreement and audit asynchronously,
   attacking the 420 minute tail. The red team's conditions
   bind in full: audit-before-release is retained for Class L
   and any flagged grade; the audit share of the tail is
   measured first (five tasks of timestamped instrumentation);
   if the share lands under 10 percent, M1 closes as a
   negative result; the overturn protocol is written before
   the pilot; savings are reported net of any post-release
   overturn's re-drive cost. UNPROVEN until that pilot reports.
5. **M2, one-pass seal (ADOPT, wrapper form only).** A thin
   wrapper invoking the existing collect, snapshot and gate
   tools in sequence, collapsing about six boundary operations
   to one and structurally deleting the self-hash trap class
   (four dated traps lived in these seams). PROVEN: the
   prototype's manifest is identical to the current tool's
   output on the largest evidence set, all 59 hashes equal.
   The gate remains a separately runnable verification over
   the wrapper's output (a merged rewrite would be
   self-certification and was rejected). No time saving may be
   cited: the machine delta is 0.35 s and the agent-minute
   effect is UNPROVEN.
6. **M14, adversarial probe gate before executor changes
   (ADOPT).** PROVEN cost: the Y1b probe suite passes 4/4 in
   15.478 s on this machine, standing in front of a failure
   class that took about 24 hours of multi-lane remediation.
   Conditions: the probe file is frozen per gate version, probe
   changes go through full council plus redteam, and a
   suspiciously fast pass after an executor change is treated
   as a flag, not a comfort.
7. **M7, stall and latency detector (ADOPT, parts a and b).**
   PROVEN in part: the analysis script runs in 0.038 s and
   reproduces both the 954 minute latency table and the three
   heartbeat gaps over 30 minutes. It may only FLAG for human
   judgement, never trigger or pre-authorise a takeover. The
   git-activity part ships only after passing both backtests:
   it must fire on the 2026-11-27 stall window and stay silent
   across the 2026-11-25 window the owner later corrected.
   Saving claimed: detection latency only.
8. **M28a, watchdog rolling branch (ADOPT, append-only form
   only).** One rolling branch per lane, APPEND-ONLY and never
   force-pushed, a PR opened on material flags as today, plus
   a periodic rollup PR so the log actually lands on main.
   The force-updated variant in the original proposal is
   rejected (section 3). Savings stated in counts only (about
   476 PR creations per lane per period, about 90 percent of
   watchdog commit ceremony), never minutes. Needs one
   coordinator approval. A one-week count comparison against
   the 300-430 per day baseline runs as a post-adoption check.
9. **M12, adopt the drafted 429 rule (PILOT-FIRST).** The rule
   text already exists (coord/mei.md section 9). Pilot form:
   total backoff window widened to 30-45 minutes with jitter
   (at 15 minutes it would spend the finite invalid budget on
   429s that might clear), every invocation logged with its
   outcome, false-INVALID count reported after one run. The
   observed loss it caps is 245.0 minutes on one task.
10. **M26, verdict template with a line cap (PILOT-FIRST).**
    Aimed at the deliberation pool. Its proof label is
    UNPROVEN (see the downgrade in section 3): the supporting
    experiment was one artifact, two different agents, no
    recall measurement. Pilot: controlled repeat, agent pool
    held constant or arms swapped, at least three artifacts
    including one hard one, findings recall reported against
    the free-form arm; every capped verdict carries a
    "dropped for length: N" count, and the cap never applies
    to BLOCKING findings.

### Adopted, lower priority

- **M10 (reduced):** pre-calibrate one named spare scorer at
  run start; no standing warm seat. "Calibration is cheap" is
  DOCUMENTED, not measured. Claims no cap hours, ever.
- **M11c (check half):** Marionette pre-flight session check
  (cost proven, 0.01-0.19 s on Zen 1.24.3b here). Restart only
  after an actual session-creation failure, never on an error
  string match. This is detection plus cheap recovery, never a
  proven wedge fix; the wedge trigger remains unreproduced.
- **M18 (reduced):** module-first change-scoped runs as written
  dev-loop guidance (a module runs in 2.217 s against 365 s
  full; that proves speed, not selection safety). Full
  discover stays mandatory at every gate. The automatic
  coverage-based selection half is rejected (section 3).
- **M20:** one-shot DOM harvests as a coding rule for new code,
  with an element-set payload cap. Mechanism PROVEN twice (11x
  local BiDi median, 54x in the repo's Marionette bench;
  ratios are transport-specific and none is quoted as
  transferable). No run-level saving until a census of
  remaining per-element call sites exists and one conversion
  is timed.
- **M23:** bounded and batched git output as scripting hygiene.
  Measurements proven (log -20 median 0.392 s vs log --all
  0.843 s); it appears in no savings table, because its total
  impact depends on an UNVERIFIED loop frequency.
- **M28d:** exempt mechanical log appends from the
  small-commit rule. Trivial, negligible risk.
- **M29:** a written no-council class for status, ack and log
  artifacts, FORMAT only. Any artifact asserting another
  lane's liveness or a stall is outside the exemption (the
  2026-11-25 false flags are the standing counterexample).
  Peer corrections counted for a week as monitoring.
- **M34f (rule only):** every deliberation proposal and
  parallel-lane plan is priced in wall time AND tokens. The
  imported 15x constant is rejected (section 3).

### Pilot-first, full list

M1 and M12 and M26 above, plus: **M4** Class L hash-check
decoupling (laptop handover; live re-read stays default, any
mismatch permanently reverts that task type; promotion needs
zero mismatches across a full run of Class L tasks; the 87.1
idle minutes are the prize). **M5** duplicate handling in the
converged form of section 3 (offline re-seal of the 59
preserved L3 sets; the 7 genuine PASS sets must pass, the 1
fabrication case must route to review). **M6** JPEG for
intermediate screenshots now; graded and text-bearing shots
stay PNG until a scorer legibility trial shows zero verdict
changes. **M9** owner-decision defaults (owner pre-writes each
default per class before a run; invalid-budget and
grading-rule classes permanently excluded; pilot on exactly
one already-ruled class, event counting, against the 126
minute baseline). **M11a** pre-flight credential, URL and
fixture check (presence and format only, never a live login;
saving claimed for the 40 minute class only, the 272 minute
gap's split is UNVERIFIED). **M11b** bot-wall probe in the
runner's own session (laptop handover; informs only,
substitution stays a coordinator decision; the 4/4 fixture
result is code-runs evidence, the fixtures were built from the
classifier's own marker list). **M13** pin the Tier A result
language in runner briefs now (adopted); widen the checker to
both formats only after it also proves it still rejects the
preserved R3-002 fabrication patterns. **M15** defective-test
register, every entry carrying branch lineage (merge-base
checked), an owner, and an expiry that deletes. **M19**
persistent tc02 client, only if the tc02 Step 3 happens for
other reasons; direction proven (import paid once vs 228-270
ms per spawn), the end-to-end saving is an UNPROVEN projection
capped at about 11 s per session. **M21** predicted-crop OCR:
already-landed practice claiming no new saving; any future
claim needs a before/after on a tesseract machine over pages
not used to tune the predictor (locally UNPROVEN, this VM has
no tesseract, which is itself the M16 defect class). **M25**
risk-tiered review, as a RECOMMENDATION TO THE OWNER only
(section 3). **M27** two-round re-review cap, after the
retro-count of blocking findings first raised in round 3 or
later across all chains in improvements/; if that count is
nonzero the cap becomes "round 3 requires a named new-evidence
reason". **M28b** watchdog daily rollup, fallback only if M28a
is refused (never both). **M30** package reviews of small,
homogeneous, low-tier items only, findings per item compared,
after M26's pilot. **M31** guard-block snippet library only
(the generator is rejected); five briefs diffed against
hand-written equivalents, zero guard drift required. **M32**
versioned run kit, tooling half only; the calibration bank
persists only if re-validated per generation at clearly less
than a fresh calibration's cost. **M33** branch hygiene,
sequenced strictly after M28a lands the watchdog record
somewhere durable, verdict branches excluded permanently,
dry-run list reviewed first. **M34a** prompt caching,
measurement only, starting with whether the harness exposes
cache controls at all. **M34b** viewport-limited accessibility
trees for navigation hints only, never grading, verification
or final-state reads. **M34c** DOM snapshot cache, only after
a mutation-detection test with zero tolerated misses.
**M34d** sparse checkout timing pilot on this repo (minutes;
the external ratio is banned from reporting). **M34e** CI
batching, measurement only; if the project's own cancelled-run
share is small it closes as a printed negative result.

### Rejected, with reasons

- **M3, verify-once receipt.** Replaces each scorer's
  independent key and manifest verification with trust in one
  gate run. That replacement IS the proposal, so no condition
  trims it; the survivable residue (a receipt as an extra
  artifact, verification untouched) saves nothing. Independent
  verification is the mechanism that keeps frozen keys frozen;
  the 126 recorded verifications are that mechanism working,
  not ceremony.
- **M8, standing deputy with 15-minute automatic takeover.**
  The trigger is the defect: 15 minutes of coordinator silence
  is proven-normal in this record (the coordinator drives on
  the laptop, which emits no git signal; the team's corrected
  watchdog rule says silence toward one lane is not evidence).
  The failure mode is a forked grading ledger. A rehearsed
  handover on POSITIVE evidence of a stall is a different
  proposal and may return as one, owner-approved.
- **M22, standalone load_image fix.** A real defect with a
  saving ceiling of 0.22-0.37 s per task, below the cost of
  the review set any standalone change consumes. Recorded in
  the tc02 backlog as a drive-by for the next substantive
  tc02 change; it earns no slot and no savings line.
- **M24, lower timeout ceilings.** No saving stated by its own
  lane, no wedge reproduced, frequency UNVERIFIED, and the
  proven risk runs the other way (R3-037's 30-minute timeout
  FAIL). Instrumentation (log calls exceeding 80 percent of
  their ceiling for one run) is the precondition for any
  future version of this idea.
- **M28c, watchdog auto-merge.** 300+ merges a day would flood
  main with a log that has already carried owner-corrected
  false flags once; the proposing lane does not prefer it;
  M28a reaches the readability goal without touching main.
- **M28a as originally written (force-updated branch).** A
  force-updated branch is a rewritable audit record, and the
  PR stream it replaced is the channel that surfaced the
  2026-11-27 stall. Only the append-only form was adopted.
- **M31, brief generator.** A wrong generated brief looks
  authoritative and feeds blind scoring. Only the manually
  pasted snippet library survives, to pilot.
- **M18, automatic coverage or trace-based test selection.**
  Lane 7's own measured external result is negative (about 2
  percent of test-seconds saved, no run shortened, and
  hand-written skip rules that all missed files, one breaking
  production). Rejected until a design carries an escape
  budget and a skip audit.
- **M34f, the imported 15x token constant.** One vendor's
  internal evaluation figure is not this project's exchange
  rate. The two-clock pricing rule was adopted; the constant
  was not.

## 3. The debate record

Round 1: three council scorers (value, feasibility, evidence)
scored all 34 proposals independently; the red team attacked
all 34 plus the bottleneck ranking itself. Round 2: a
convergence council produced the final table under two rules
(council 3's proof downgrades stand unless a cited run refutes
them; red team kills stand unless the converged form removes
the attacked mechanism entirely), and a second red team took a
last shot at the consensus, conceding most items with tightened
conditions and holding three kills.

Proof downgrades that bind every downstream document
(council 3, unrefuted): **M26** PROVEN to UNPROVEN (n=1, two
different agents in the arms, no recall measurement; "kept the
top findings" is judgement, not recall). **M27** "proven on
historical data" to UNPROVEN as a policy (one chain, selected
because its tail was empty). **M19** end-to-end figures
quarantined as a repo projection; only the direction is
proven. **M2** proof scope restricted to correctness and step
count; no time saving may be cited. **M11b** fixture proof
relabelled code-runs evidence. **M10** "calibration is cheap"
relabelled DOCUMENTED, not measured. **M18** speed proven,
selection safety unmeasured.

Red team kills and their fate: M3, M8, M24, M28c killed and
the kills stand. M22 killed as a standalone, survives as a
drive-by note. M28a's force-update mechanism killed; the
append-only form adopted. M5's pure-alias form killed (it
normalises the duplicate-hash signal that caught the project's
one documented fabrication, inside the evidence format
itself); the converged form is storage-layer dedupe with loud
alias entries that never assert evidence equivalence, the
duplicate screen firing on every occurrence, and human review
on duplicates-plus-anomaly or a freeze-time distinct-capture
requirement. The landed hard-fail rule is superseded: it
provably rejects 7 genuine PASS evidence sets of 59.

Cross-cutting attacks that shaped the register: almost no
lane saving was netted against build plus verification cost
(the netting table in the working papers prices the top ten;
only M14 and M16 survive netting trivially); the same minutes
were claimed by several proposals (the pool allocation in
section 2 is the fix); four pilots are laptop-bound and
unverifiable from a worker VM (M4, M11b, M19's end-to-end,
M21); VM-measured savings will differ on real hardware;
deliberation proposals were not priced in tokens until M34f
made it a rule. The red team's ranking attack also stands in
part: B1 (caps) ranks first on the calendar clock while no
proposal reduces it, and B3 and B4 grade the past; the report
answers by ranking on three clocks and saying so, not by
hiding either fact.

Sequencing hazards, recorded so they cannot be lost: M33
(branch cleanup) before M28a lands the watchdog record would
delete the only complete copy of that record. M1 and M4
adopted carelessly together would strip both protections on
the most state-sensitive task class (Class L keeps
audit-before-release under M1 and live re-read under M4).

Unresolved, with dissenters named: whether every duplicate
group in a graded set should route to human review (councils
1 and 3) or duplicates-plus-anomaly is the right trigger
(red team, adopted); M28a adopt-now (convergence) versus
pilot-first (council 3, whose position revives if the
post-adoption check shows any loss of escalation signal);
M11b's worth (council 3 scores 5, councils 1 and 2 score 3;
only the laptop pilot settles it); M18's reduced form (council
2 wanted the whole proposal pilot-first, fearing a dev-loop
shortcut becoming the de facto gate); M22 (council 2 would
adopt standalone); M29 (council 3 wanted a pilot week first);
M34d (council 1 would reject outright); the C6 audit-share
question and the C8 waste-versus-integrity question, both
genuinely unmeasured and assigned to the M1 and M25-M27
pilots respectively; and the smaller figure conflicts (row
count 59 vs 60 behind identical cycle totals, three different
gap intervals with different endpoints, the 166 minute gap's
unattributed remainder), which stand as recorded in the
working papers.

Laptop handover list (this study cannot run or verify these;
they belong to the coordinator's machine): M4's Class L pilot,
M11b's live probe, M11c's restart behaviour against the real
slot, M19's end-to-end timing, M21's tesseract before/after,
and M17's shard ratio re-measurement on real hardware.

Negative results, printed because they are results: hashing
is not a bottleneck (2.18 s for the corpus); screenshot
capture is not a bottleneck; the RDP lane's attach and read
times are not bottlenecks; the unscored queue never exceeded
depth 2, so there is no scoring backlog to fix; the naive
dedupe rule fails 8 of 59 real sealed sets; brief templating's
naive saving is refuted by measurement (16 percent shared
lines in scorer briefs, Jaccard 0.00-0.20 between runner
briefs); the Marionette wedge trigger was not reproduced in
either council-specified arm; the events.log archive was never
obtained (see the source note at the top).

## 4. Sources

All repo sources were opened at the fix-review checkout
(~/workspace/cuw-fixreview, tip 91547db1) on 2026-11-27:
rung3-run-log/ (R3-L3-grades.jsonl, heartbeat and rerun logs,
briefs, snapshots), improvements/ (batch reports, R10 landing
and switch reports, fix-review council files, live-test-log),
rung3-ci/ (verify-list.py), coord/ files including
coord/mei.md sections 7, 9 and 12, docs/clone2-watchdog-log.md,
and the git history itself (4,732 commits; all lane-6 figures
from read-only git and gh commands run that day). Working
papers for this study (eight lane files, the synthesis
register, and five debate files) are held locally with the
study outputs and are available to any lane on request.

External sources, all opened on 2026-11-27 and cited only for
what the opened page itself measures: Gel engineering blog on
test sharding (about 5,000 tests, 2 h 22 min to about 7 min
with 16 shards), https://www.geldata.com/blog/how-we-sharded-our-test-suite-for-10x-faster-runs-on-github-actions ;
Contentstack on Vitest sharding (887 s to about 4.5 min with 6
shards), https://developers.contentstack.com/blog/the-waiting-tax-on-every-pr-how-sharding-vitest-cut-ci-from-15-minutes-to-4-5 ;
impact-based selection and its measured negative result
(coverage narrowing saved about 2 percent and shortened no
run), https://medium.com/@rakesh.ramanikanth/smarter-ci-optimizing-unit-test-execution-with-impact-based-test-selection-d13975e99b9f and https://blog.catalex.co/ci-at-agent-speed ;
browser automation protocol latency (per-message round trips
dominate; batching is the measured mitigation),
https://gologin.com/blog/browser-automation-tools/ ;
accessibility tree versus screenshot token costs (measured,
script shown), https://dev.to/neeraj_sharma_757fbb49aa7/pixels-vs-the-accessibility-tree-i-measured-what-a-web-page-costs-an-ai-agent-67-lines-of-python-2hn8 ;
multi-agent token costs (about 15x chat; vendor figure, used
only as the reason M34f demands local measurement, never as
this project's rate), https://www.anthropic.com/engineering/multi-agent-research-system ;
prompt caching measured table only (100K-token prompt,
time-to-first-token 11.5 s to 2.4 s),
https://claude.com/resources/articles/prompt-caching ;
sparse checkout on GitHub's test repository (ratio recorded,
banned as an expectation for this repo),
https://github.blog/2020-01-17-bring-your-monorepo-down-to-size-with-sparse-checkout/ .
Retry guidance from AWS Well-Architected (REL05-BP03) was
opened and is authoritative guidance but reports no measured
saving, so every quantified saving for the retry class in this
report is the project's own (M12) or UNVERIFIED. Three further
pages surfaced by search were never opened and are recorded as
UNVERIFIED in the working papers; nothing in this report cites
them.

Clone2, 2026-11-27. English only. No personal information in
this document.
