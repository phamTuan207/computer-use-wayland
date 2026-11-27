# Integration-phase test plans: items not yet integrated (2026-11-27)

Status: FIXED DRAFT, RE-REVIEWED. Council of 3 independent reviewers plus a
separate redteam: all four NEEDS CHANGE (137 findings total); fix pass applied
per slice; re-review 2026-11-27 20:51-20:56 +07: all HIGH closed (40 closed,
4 moot), consistency re-review 5 LOW, all fixed in this file. Independent
verification from scratch 2026-11-27 21:00-21:05 +07: NEEDS CHANGE with
3 LOW, 0 HIGH, 0 MEDIUM, all fixed in this file. Ready to land.

Scope: test plans for the 46 items NOT yet integrated at draft time, from the
integration report queue (QUEUED items 16-25) and the pilot lists (M pilots +
I pilots). Items 0-15 of the integration report are already integrated or
live-tested, except where the report says a measurement is pending (see M17
below). Rejected items have no plan (not revived without new evidence). M25
is an owner-only recommendation, not built, no plan.

Coverage at fix time: 30 full plans + 16 one-liners = 46 items.
- Slice A (queue items 16-25): 0 full plans + 15 one-liners. All 15 merged
  during the review window: wave 1 (merge 58013edd) merged items 16, 18-25,
  and the I19 merge (c7709de2) merged item 17. Each one-liner cites its
  landing commit and the report's recorded live-test evidence.
- Slice B (M pilots 1): 10 full plans (M1, M4, M5, M6, M9, M11a, M11b, M12,
  M13, M15).
- Slice C (M pilots 2): 8 full plans (M19, M21, M26, M27, M30, M31, M32,
  M33) + 1 one-liner (M28b, DORMANT PERMANENTLY: its trigger, M28a refused,
  can never fire now that M28a merged as 877afe6d).
- Slice D (M34a-e + I pilots): 12 full plans (M34a, M34b, M34c, M34d, M34e,
  I2, I4, I6, I12, I14, I18, I23).

Sources:
- Integration report: improvements/integration-phase-20261127.md on branch
  integration-20261127 (547 lines at tip 167b5636, "Integration report:
  fix-discover merged, full-suite shard 2437/2437", re-verified 2026-11-27
  20:51-20:56 +07; fix pass verified against 5365c84c, 519 lines).
- Bottleneck register M1-M34: improvements/bottleneck-study-20261127.md on
  todolist-push (commit 26b1133d), section 2 lines 192-412, debate record
  section 3.
- Agent-desktop comparison I1-I23: improvements/agent-desktop-comparison-20261127.md
  on todolist-push (commit 6b67e286), sections 2-7.

Proof law (bottleneck study, introduction, lines 14-22): a claim counts as
PROVEN only if run for real on the laptop with measured before/after
numbers. Everything else is UNPROVEN until its live run reports. Figures
measured on the register machine are called "measured on the register
machine", never PROVEN. No number, command, path, or baseline in this file
is invented: anything the sources do not give is marked UNVERIFIED with
what would establish it, or is a named pre-run decision (who names it, by
when, what blocks the pilot).

Format: every full plan has ### (a)-(f) headings: (a) item/source/verdict,
(b) preconditions/setup, (c) numbered live steps, (d) before/after
measurements, (e) pass criteria with PROVEN vs UNPROVEN, (f) fail/rollback
notes. Live steps run under a cu.py session with the pill visible; the
owner Zen PID is recorded before and verified unchanged after unless the
item requires otherwise; every plan's (c) ends with a probes/ledger.jsonl
row, a grim screenshot, test files removed, and the desktop verified clean.
RDP port convention: 6021 is the observed value from the 2026-11-27 live
records, re-verify at run time. ID forms follow the integration report:
I19-substitute, I20-substitute.

Deferred with gates (no plan in this file, for coordinator confirmation):
four agent-desktop PILOT-FIRST halves are not in the integration report's
pilot list, so they have no plan here. I5 walk half (walk-cost + wrapper
census pilot, before any default is flipped); I9 unified-interface pilot
(after I23); I10 hit-test signal probe (prove a signal exists before any
battery work); I16 a11y-overlay half (gated on I14). Each gets a sequenced
plan once its gate passes, or stays deferred by coordinator decision.

Pending measurement, no plan here: M17 (sharding) is implemented and
measured on a 1.5-CPU VM (2340 tests, 175.7 s vs 292.0 s, 1.66x), and its
laptop re-measure is explicitly pending in the integration report. That
re-measure is tracked in the integration report, not planned in this file;
it needs an owner (who runs it, when).

Review record: draft (3,116 lines) reviewed 2026-11-27 20:28-20:38 +07.
Council 1 fidelity NEEDS CHANGE (14 findings), council 2 executability
NEEDS CHANGE (65 findings), council 3 completeness NEEDS CHANGE (12
findings), redteam NEEDS CHANGE (46 findings). Fix pass per slice applied
2026-11-27 20:38-20:47 +07, verified against tip 5365c84c. Re-review
2026-11-27 20:51-20:56 +07: HIGH re-review ALL HIGH CLOSED (40 closed, 4
moot, 0 open); consistency re-review NEEDS CHANGE with 5 LOW, all fixed.
Independent verification from scratch 2026-11-27 21:00-21:05 +07: NEEDS
CHANGE with 3 LOW, 0 HIGH, 0 MEDIUM, all fixed. All gates passed.

---

## Slice A: QUEUED queue items (integration report items 16-25), all merged

## 1. I15 root-level incomplete marking

Already integrated (commit `d725684f`, int-i15, via wave-1 merge `58013edd`), no plan.
Report record: read_errors + incomplete root marking, ground/act surface it;
45 a11y tests OK; live on 6 AT-SPI apps.

## 2. I19-substitute: MCP drift test

Already integrated (commit `acaa68ea`, int-i19, via merge `c7709de2`; report
`5ed2fd9a` "I19 merged"), no plan. Report record: `tests/test_mcp_drift.py`,
11 assertions over cu.py / mcp_bridge / session_driver surfaces;
deliberate-drift proof (3 scratch breaks all FAIL); laptop run 11/11. Note
from the report: the report's mcp_server.py no longer exists; the test
targets the live mcp_bridge surface. The draft's TOOLS-entries framing does
not exist anywhere in the implementation and is dropped with the plan.

## 3. I20-substitute: RDP lock hardening + lock map doc

Already integrated (commit `e1c52422`, int-i20, via wave-1 merge `58013edd`), no plan.
Report record: 5 lock weaknesses fixed + LOCK-MAP.md; 63 zen-rdp tests OK;
live lock refusal proven.

## 4. M14 adversarial probe gate, Y1b suite

Already integrated (commit `c0b5d14b`, int-m14, via wave-1 merge `58013edd`), no plan.
Report record: frozen-hash gate v1 + fast-pass FLAG; 5 tests OK; live PASS
VM+laptop.

## 5. M7 stall detector parts a+b

Already integrated (commit `f3033aa8`, int-m7, via wave-1 merge `58013edd`), no plan.
Report record: union detector, backtest reproduces study numbers; proposed
threshold 45min union silence; flag-only.

## 6. M11c Marionette pre-flight session check

Already integrated (commit `2889ca6e`, int-m11c, via wave-1 merge `58013edd`), no plan.
Report record: marionette_preflight() 4 named checks; 27 tests OK; live
pass+fail configs.

## 7. M11d pre-freeze triage, process + verify-list gate

Already integrated (commit `482aca7c`, int-m11d, via wave-1 merge `58013edd`), no plan.
Report record: procedure doc + pre-freeze-gate.py wrapper; 5 tests OK; live
PASS VM+laptop; catch rate unmeasured until first use.

## 8. M28a watchdog rolling branch, append-only form

Already integrated (commit `877afe6d`, int-m28a, via wave-1 merge `58013edd`), no plan.
Report record: watchdog_append.py (plumbing, ff-only, pii gate) + doc;
5 scratch-repo tests OK incl. concurrency; lane switch-over still a
coordinator decision. Consequence recorded for slices B/C: M28b's trigger
(M28a refused) is now permanently un-fireable, and M33's precondition is no
longer "M28a not landed" but "M28a code merged, lane switch-over still a
coordinator decision, so no durable record location exists yet".

## 9. M18-reduced module-first change-scoped runs as dev-loop guidance

Already integrated (commit `4ecc0ea9`), no plan.

## 10. M20 one-shot DOM harvests as a coding rule for new code, with element-set payload cap

Already integrated (commit `577b4d3f`), no plan.

## 11. M23 bounded and batched git output as scripting hygiene

Already integrated (commit `7e6e6896`), no plan.

## 12. M28d exempt mechanical log appends from the small-commit rule

Already integrated (commit `36b42910`), no plan.

## 13. M29 written no-council class for status, ack and log artifacts, FORMAT only

Already integrated (commit `fdb6f648`), no plan.

## 14. M34f rule only: every deliberation proposal and parallel-lane plan priced in wall time AND tokens

Already integrated (commit `af8f6453`), no plan.

## 15. M10-reduced pre-calibrated spare scorer

Already integrated (commit `89072e10`, int-m10, via wave-1 merge `58013edd`), no plan.
Report record: spare-scorer.md + check-spare-scorer.py; 10 tests OK; no
cap-hours claims ever.

---

Plans written: 0 full test plans. Already integrated at branch tip `5365c84c`,
no plan written: I15 (`d725684f`), I19-substitute (`acaa68ea`),
I20-substitute (`e1c52422`), M14 (`c0b5d14b`), M7 (`f3033aa8`), M11c
(`2889ca6e`), M11d (`482aca7c`), M28a (`877afe6d`), M18-reduced (`4ecc0ea9`),
M20 (`577b4d3f`), M23 (`7e6e6896`), M28d (`36b42910`), M29 (`fdb6f648`),
M34f (`af8f6453`), M10-reduced (`89072e10`). Items 9-14 via merge `1314b088`;
items 1, 3-8, 15 via wave-1 merge `58013edd`; item 2 via merge `c7709de2`.

---

## Slice B: M pilots 1 (M1, M4, M5, M6, M9, M11a, M11b, M12, M13, M15)


- Integration report: improvements/integration-phase-20261127.md (519 lines
  at tip 5365c84c), branch integration-20261127. Pilots list names M1,
  M12, M26, M4, M5, M6, M9, M11a, M11b, M13, M15, M19, M21, M27, M28b,
  M30, M31, M32, M33, M34a-e as PILOT-FIRST (UNPROVEN until they report).
- Bottleneck register: improvements/bottleneck-study-20261127.md (609
  lines), branch todolist-push, commit 26b1133d. Section 2, lines 192-412
  (Do first lines 209-311 incl. M1 #4, M12 #9, M26 #10; Adopted lower
  priority 312-348; Pilot-first full list 349-412). Section 3 is the
  debate record (lines 464-609). Introduction, lines 14-22, states the
  proof law.
- Agent-desktop comparison: improvements/agent-desktop-comparison-20261127.md
  (447 lines), branch todolist-push, commit 6b67e286, sections 2-4.
- Fourth sources, verified against the tree on branch
  integration-20261127 at tip 5365c84c (not in the three named sources;
  cited where used): frozen keys docs/rung3-answer-keys.md (caps L9,
  count-by-event ruling L23); Tier A checker rung3-ci/tier-a-check.py and
  regression tests rung3-ci/test_tier_a_check.py (R5, 2026-11-27); duplicate
  screen rung3-ci/collect-evidence.py (R9, lines 136-147); test runner
  rung3-ci/test-discover.py (subcommands run/hermetic/shard); ledger
  probes/README.md and probes/validate-ledger.py; coordinator state file
  rung3-run-log/r3-l3-coordinator-state.json (event notes, R3-002
  fabrication, event-6 decision); runner briefs rung3-run-log/briefs/
  (grim-screenshot rule, R3-029 brief line 48); screenshot capture
  scripts/cu.py observe() line 978, observe_screen() line 1032.

## Integration check (re-verified at fix time)

- Branch tip checked 2026-11-27 20:38:57 +07: origin/integration-20261127
  at 5365c84c (83 integration-phase commits since 4b70b71c).
- Word-boundary grep for M1, M4, M5, M6, M9, M11a, M11b, M12, M13, M15
  over the full branch log since 4b70b71c: zero matches. None of the 10
  items below is implemented or live-tested on the integration branch.
  All 10 get full plans.
- The wave-1 merge (58013edd, tip 67d9ce2c) landed 8 slice-A items after
  the first draft was written; it does not touch slice B.

## Proof law and terminology (binds every plan)

A claim counts as PROVEN only if it is run for real on the laptop with
measured before/after numbers (bottleneck study, introduction, lines
14-22). Anything else stays UNPROVEN, with the pilot that would prove it
named. Savings are never summed across proposals that share a pool.
PROVEN has one sense in this slice: laptop-run PROVEN. Figures measured
on the register machine are called "register-measured", never PROVEN.
The 59-vs-60 row-count conflict is recorded in the register section 3
(line 539: "row count 59 vs 60 behind identical cycle totals") and stands
unresolved; every "59" in this slice means the 59 preserved L3 sets as
re-counted at pilot start (56 directories ending in -L3 plus 3 -L3-rerun
directories), and the pilot re-counts before relying on it.

## Shared rules for every pilot in this slice

- Run naming: the coordinator names and schedules the pilot run in the
  pilot brief (run ID, task list, start condition) before the pilot
  starts. The pilot does not start until the run is named. No pilot in
  this slice assumes a live run exists without the brief naming it.
- Coordinator approval: every pilot that runs inside a live run needs
  coordinator approval naming the exact run (and, for M1 and M12, the
  exact tasks) before the pilot starts. The approval (who, when, where
  in the run record) is recorded in the pilot log. The pilot does not
  run on any other run without a fresh approval. A written protocol,
  rule, or default is not approval.
- Pilot report: every pilot writes its report to
  improvements/pilot-<ITEM>-<YYYYMMDD>.md in the integration-branch
  checkout on the laptop (for example improvements/pilot-M1-20261127.md).
  The ledger row cites that path.
- Ledger row: every pilot records one row in probes/ledger.jsonl citing
  its outputs. Row fields per probes/README.md: date (YYYY-MM-DD),
  probe (path or short name), question, result (the measured numbers or
  the observed behavior), output (citation: a repo path holding the
  output, or the output inline when short), verdict (what was decided
  from it). Validate with `python3 probes/validate-ledger.py` (must
  print LEDGER OK). Example row: {"date": "2026-11-27", "probe":
  "improvements/pilot-M1-20261127.md", "question": "M1 audit share of
  the tail?", "result": "audit share 12 percent over 5 tasks",
  "output": "improvements/pilot-M1-20261127.md", "verdict": "phase 2
  proceeds"}.
- Owner Zen PID: record it with `pgrep -x zen` (attested in
  improvements/live-test-log.md), then identify the owner Zen with
  `ps -o pid,lstart,args -p <pid>`: the owner Zen is the Zen process
  running before the pilot started, recorded at step 1 with its start
  time. Any Zen started by the pilot (throwaway profile) has a recorded
  PID and a later start time. Never assume a PID from past records
  (807599 on 2026-11-27 is historical; PIDs change on restart).
  NEVER ydotool. NEVER close or navigate owner tabs, pinned tabs,
  essentials, or anything on ws3. Close only your own terminal window
  after use.
- Desktop clean: at pilot start, record `hyprctl clients` output as the
  owner-window baseline. At pilot end, re-run `hyprctl clients` and
  diff it against the baseline. Clean means only the baseline owner
  windows remain: no pilot windows, no test instances (verified gone
  by recorded PID after a cmdline check). Save a grim screenshot of
  the desktop after release (runner-brief hard rule, R3-029 runner
  brief line 48: "save a grim screenshot of the desktop after
  release").
- Test runner: run suites with `python3 rung3-ci/test-discover.py run
  --start-dir tests [--modules <module> ...]` (serial, the gate of
  record; subcommands are run/hermetic/shard). Scope to one file with
  --modules. Never guess the invocation.
- RDP port convention for this slice: 6021 is the observed value from
  the 2026-11-27 live records; re-verify at run time.
- Every pilot runs on the real laptop, under a cu.py session, with the
  pill visible (label exactly "Computer use active"). Verify the pill
  is visible during the drive and gone after. Number every attempt/run
  with wall-clock timestamps; record failures and pill gaps honestly.
  Read-only where the plan says so.
- Mei does not score anything. Where a pilot needs grading, the run's
  independent scorers grade; the pilot measures timing, counts, and
  outcomes.
- Every plan's (c) ends with the closing steps: ledger row, grim
  screenshot, owner Zen PID re-verified, test files removed, desktop
  clean (per the shared rules above).

---

## M1: parallel-ledger release

### (a) Item, source, register verdict/conditions

- Source: bottleneck register #4 (Do first, PILOT-FIRST); integration
  report Pilots list: "M1 (audit-share instrumentation first)".
- Proposal: release a task on two-verdict agreement and audit
  asynchronously, attacking the 420 minute tail.
- Red-team conditions bind in full: audit-before-release is retained
  for Class L and any flagged grade; the audit share of the tail is
  measured FIRST via five tasks of timestamped instrumentation; if the
  share lands under 10 percent, M1 closes as a negative result; the
  overturn protocol is written BEFORE the pilot; savings are reported
  NET of any post-release overturn re-drive cost. UNPROVEN until that
  pilot reports.
- Sequencing hazard (register section 3): M1 and M4 adopted carelessly
  together would strip both protections on the most state-sensitive
  task class (Class L keeps audit-before-release under M1 and live
  re-read under M4). The M1 pilot must not run on Class L tasks and
  must not run concurrently with the M4 pilot.

### (b) Preconditions and setup on the real laptop

- Branch: integration-20261127 checked out on the laptop (exact laptop
  path UNVERIFIED; the pilot brief names it). No M1 code exists yet;
  the pilot is instrumentation first, so no release-path code change is
  needed for phase 1.
- Phase 1 is BLOCKED until the instrumentation exists. The
  instrumentation is a named prerequisite: a script that runs the
  release path and logs a wall-clock timestamp per boundary operation
  (collect, manifest handling, pii-scan, snapshot, gate, push, two
  scorer verifications, coordinator audit, two ledger validators). No
  such hook exists in the sources. The coordinator assigns the build,
  and the pilot brief names the script path and invocation before
  phase 1 starts. A runner must never timestamp the ten boundary
  operations by hand from watching a release path that runs across
  multiple agents and machines. If the script is not named, phase 1
  does not start.
- The coordinator selects the five tasks for phase 1 and names them in
  the pilot brief (non-Class-L, non-flagged, from the named run, or a
  replay of five already-graded tasks if the coordinator prefers; the
  choice is recorded before phase 1 starts). The coordinator performs
  the releases in phase 2; the runner runs the instrumentation and
  timestamps. The coordinator states in writing in the pilot brief
  that the M4 pilot is not running concurrently; phase 2 does not
  start without that statement.
- The coordinator writes the overturn protocol BEFORE the pilot starts.
  It must state in writing: how a released grade is corrected in the
  ledger, who is notified of the correction, and who re-drives what.
  Before phase 2, the correction is dry-run once on a scratch ledger
  and the dry-run result is recorded in the pilot log. No overturn
  protocol, no phase 2. No dry-run, no phase 2.
- Coordinator approval naming the exact run and the exact phase-2
  tasks is recorded in the pilot log before phase 2 starts (shared
  rules). Phase 2 never runs on a run whose grades are already being
  consumed downstream.
- Owner Zen untouched. Pill up for any driven step.

### (c) Live test steps

1. Record the integration-branch tip, the owner Zen PID (shared rules),
   the five selected task IDs, the instrumentation script path and
   invocation, and the coordinator approval (run + tasks). Start a
   cu.py session; confirm the pill is visible.
2. Phase 1, instrumentation: for each of the five tasks, run the normal
   release path (audit-before-release, as today) through the
   instrumentation script. Record each boundary-operation timestamp in
   the pilot log with task ID and operation name.
3. Compute the audit share of the tail from the five tasks (coordinator
   audit minutes divided by total tail minutes). If the share is under
   10 percent, STOP: M1 closes as a negative result, no phase 2,
   report the numbers.
4. Phase 2, release pilot (only if phase 1 share is 10 percent or
   more, and only on the approved run and tasks): for each approved
   task (non-Class-L, non-flagged only), the coordinator releases on
   two-verdict agreement and the audit runs asynchronously. Log release
   time and audit completion time per task.
5. Any Class L task or flagged grade in the run keeps
   audit-before-release; log each such retention.
6. If a post-release audit overturns a grade, STOP phase 2 at once
   (stop on the first overturn, not only on a breach), follow the
   pre-written overturn protocol exactly, and log the re-drive cost
   (minutes, tasks) and the ledger correction made.
7. Closing steps (shared rules): record one row in
   probes/ledger.jsonl citing the pilot report; save a grim screenshot
   of the desktop after release; verify the owner Zen PID is unchanged
   (shared rules); remove test files; verify the desktop is clean
   (`hyprctl clients` diff against the start baseline); end the
   session and verify the pill is gone.

### (d) Before/after measurements

- Baseline (register, Clock A, R3-L3 graded cycle, computed from
  rung3-run-log/R3-L3-grades.jsonl): 1,729 minutes total; driving 775
  (44.8 percent); scoring lag 534; ledger tail after both scorers
  agreed 420 minutes. Post-run processing 954 minutes, 55 percent of
  the cycle. Tail is about 15 boundary operations per task.
- Audit share of the tail: UNVERIFIED (conflict C6; nobody has
  timestamped the audit step). Phase 1 establishes it; capture method:
  the timestamped per-operation log from the instrumentation script
  in step 2, per task.
- Release-to-ledger time per task under two-verdict release (phase 2)
  versus audit-before-release (phase 1 / historical tail): capture
  from the pilot log timestamps.
- Overturn count and re-drive cost: count of post-release overturns;
  minutes spent re-driving per overturn, from the pilot log. Ledger
  corrections made: count, with the correction record cited.

### (e) Pass criteria

- Phase 1 completes on five tasks with a timestamped log for every
  boundary operation; audit share reported as a number.
- If audit share is under 10 percent, M1 closes as a negative result
  with the numbers reported. That is a PASS for the pilot (a printed
  negative result), not a failure.
- If phase 2 runs: zero Class L or flagged releases without audit;
  every release and every audit completion timestamped; net saving
  reported as tail reduction MINUS overturn re-drive cost, greater
  than zero to claim a saving; zero phase-2 releases on a run whose
  grades are consumed downstream; the overturn correction dry-run
  recorded before phase 2.
- PROVEN only when run for real on the laptop with the measured
  before/after numbers above. Anything less stays UNPROVEN.

### (f) Fail and rollback notes

- If the overturn protocol does not exist before the pilot, do not
  start phase 2; phase 1 instrumentation may still run (once the
  instrumentation script is named).
- If the instrumentation script is not named in the brief, phase 1
  does not start; the pilot is blocked, not failed.
- If a phase 2 release is found to have skipped audit on a Class L or
  flagged task, stop the pilot at once, restore audit-before-release
  for all remaining tasks, and report the breach with task IDs.
- If an overturn occurs, phase 2 stops at the first overturn; the
  protocol governs the correction; if the protocol is silent on a
  case, the coordinator decides and the case is logged as a protocol
  gap. No silent re-grading. Tasks already released under the pilot
  stay released and are corrected through the protocol, never
  silently re-graded.
- Rollback: the release path reverts to audit-before-release (the
  current behaviour); the instrumentation log is kept as the pilot
  record. No ledger rows are rewritten by the pilot except through
  the overturn protocol's stated correction path.

---

## M4: Class L hash-check decoupling

### (a) Item, source, register verdict/conditions

- Source: bottleneck register, Pilot-first full list; laptop handover
  list (M4's Class L pilot belongs to the coordinator's machine).
- Proposal: Class L hash-check decoupling. Live re-read stays default;
  any mismatch permanently reverts that task type; promotion needs zero
  mismatches across a full run of Class L tasks; the 87.1 idle minutes
  are the prize.
- Verdict: PILOT-FIRST, UNPROVEN until it reports.
- Sequencing hazard (register section 3): M1 and M4 adopted carelessly
  together would strip both protections on Class L. The M4 pilot must
  not run concurrently with the M1 pilot. The coordinator states in
  writing in the pilot brief that the M1 pilot is not running
  concurrently; the pilot does not start without that statement.

### (b) Preconditions and setup on the real laptop

- Branch: integration-20261127 checked out on the laptop (exact laptop
  path UNVERIFIED; the pilot brief names it).
- Class L task list for the pilot run (score-before-reset; coordinator
  verifies against the live tab list + sessionstore before scoring
  closes): R3-001, R3-055, R3-074, R3-075, R3-078, R3-079, R3-088,
  R3-089, R3-096 (9 tasks; 8 named in runner briefs, R3-001 per the
  run record) plus task 56 (Class L amendment). The pilot brief
  confirms the list against the coordinator's state file before the
  run; a full run of Class L tasks means every Class L task in that
  run, not a subset.
- The decoupling mechanism (which step moves async, what the runner
  may do while the hash check runs) is NOT spelled out in the
  register. The pilot is BLOCKED until the coordinator writes the
  exact mechanism into the pilot brief: which step moves async, what
  the runner does while the hash check runs, and what "decoupled"
  means for the release gate. The coordinator is the named author;
  the deadline is before the pilot starts. If the brief cannot state
  it, the pilot does not start. A runner must never invent the
  mechanism mid-run; a pilot run on an invented mechanism measures
  the invention, not the item.
- Live re-read stays the default check for every Class L task in the
  pilot.
- Coordinator approval naming the exact run is recorded in the pilot
  log before the pilot starts (shared rules).
- Owner Zen untouched except as the Class L tasks themselves require
  (their own live state is the evidence; no unrelated owner tab is
  touched).

### (c) Live test steps

1. Record the integration-branch tip, the owner Zen PID (shared
   rules), the confirmed Class L task list, the decoupling mechanism
   as written in the brief (quote it), the M1 non-concurrency
   statement, and the coordinator approval (run). Start a cu.py
   session; confirm the pill is visible.
2. For each Class L task in the run, run the drive under the decoupled
   procedure from the pilot brief (hash check decoupled; live re-read
   as the default check). Record wall-clock timestamps in the pilot
   log at each boundary event as it occurs: drive end, hash-check
   start, hash-check end, live re-read, runner release, scoring
   close. The timestamps are taken from the session transcript at
   each event, recorded by the runner in the pilot log.
3. After each task, record runner idle minutes and the live re-read
   outcome (match or mismatch) with the evidence cited (live tab list
   + sessionstore). Runner idle minutes per task are defined as
   (hash-check end minus drive end) plus (scoring close minus runner
   release): the two waits the runner incurs. The register does not
   state which timestamp pair defines its 87.1 figure, so the pilot
   also records the raw six timestamps per task, so the comparison
   can be recomputed if the register's definition differs.
4. If a mismatch is found on a task type: do NOT revert at once. The
   coordinator confirms the mismatch evidence (live tab list +
   sessionstore citations) first. If the re-check shows the mismatch
   was a measurement error (sessionstore read mid-update, live tab
   list captured mid-update), re-read once with settled state and do
   not revert. Only a confirmed mismatch permanently reverts that
   task type to the old procedure (live re-read coupled, no
   decoupling); log the reversion with task type, the coordinator's
   confirmation, and the cited evidence. No second attempt on that
   type after a confirmed reversion.
5. Closing steps (shared rules): record one row in
   probes/ledger.jsonl citing the pilot report; save a grim screenshot
   of the desktop after release; verify the owner Zen PID is unchanged
   (shared rules); remove test files; verify the desktop is clean
   (`hyprctl clients` diff against the start baseline); end the
   session and verify the pill is gone.

### (d) Before/after measurements

- Baseline (register, Clock A): Class L score-before-reset blocking,
  87.1 measured minutes of runner idle across 9 tasks. The 87.1
  figure covers the 9 named R3 Class L tasks; task 56 is NOT in it
  (the register's figure is 9 tasks, and task 56's membership is not
  established in the sources). Compare the 9-task summed idle
  minutes against 87.1. Task 56's idle minutes are measured and
  reported separately, never summed into the 87.1 comparison.
- Runner idle minutes per Class L task in the pilot run: capture from
  the timestamps in step 2, per task, using the definition in step 3;
  sum the 9 R3 tasks and compare with 87.1. The raw six timestamps
  per task are filed with the pilot report.
- Mismatch count per task type: capture from the live re-read outcome
  in step 3 (must be zero for promotion).
- Live re-read evidence: live tab list + sessionstore citations per
  task, filed into the snapshot as the Class L verification note.

### (e) Pass criteria

- Zero confirmed mismatches across a full run of Class L tasks. Any
  confirmed mismatch is not a pilot failure of the measurement; it
  triggers the permanent reversion of that task type (the condition,
  applied, with coordinator confirmation).
- Runner idle minutes measured and reported against the 87.1 baseline
  for the 9 R3 tasks; a reduction is claimed only from the measured
  numbers. Task 56 reported separately.
- Every Class L task in the run has a live re-read with cited evidence.
- PROVEN only when run for real on the laptop with the measured
  before/after numbers above. Anything less stays UNPROVEN.

### (f) Fail and rollback notes

- If the pilot brief cannot state the decoupling mechanism, do not
  start; the pilot is blocked, not failed.
- If a mismatch is found, it is confirmed by the coordinator before
  any permanent reversion; an unconfirmed (measurement-error)
  mismatch does not revert the type. The pilot continues for the
  remaining types (unless the coordinator stops it).
- If the live re-read cannot be performed (live state lost,
  sessionstore unreadable), the task is not promoted and the failure
  is logged; do not substitute a hash-only check.
- Rollback: the old coupled procedure (live re-read before release)
  is restored for any reverted type; the pilot log is kept as the
  record.

---

## M5: duplicate handling (converged form)

### (a) Item, source, register verdict/conditions

- Source: bottleneck register, Pilot-first full list + section 3 debate
  record.
- Proposal (converged form): storage-layer dedupe with loud alias
  entries that never assert evidence equivalence, the duplicate screen
  firing on every occurrence, and human review on duplicates-plus-anomaly
  or a freeze-time distinct-capture requirement.
- The pure-alias form was killed (it normalises the duplicate-hash
  signal that caught the project's one documented fabrication, inside
  the evidence format itself). The landed hard-fail rule is superseded
  in principle (register section 3: it provably rejects 7 genuine PASS
  evidence sets of 59); operationally it stays in force until this
  pilot reports. The naive dedupe rule fails 8 of 59 real sealed sets
  (7 genuine PASS + 1 fabrication; register section 3, negative
  results).
- The 59 figure carries the register's recorded row-count conflict
  (section 3: "row count 59 vs 60 behind identical cycle totals",
  unresolved). This pilot uses 59 as the re-counted set count (56 -L3
  + 3 -L3-rerun) and re-counts at start; if the count differs, the
  pilot stops and reports (step 1).
- Pilot: offline re-seal of the 59 preserved L3 sets; the 7 genuine
  PASS sets must pass, the 1 fabrication case must route to review.
- Verdict: PILOT-FIRST, UNPROVEN until it reports.
- Unresolved (register section 3, dissenters named): whether every
  duplicate group in a graded set should route to human review
  (councils 1 and 3) or duplicates-plus-anomaly is the right trigger
  (red team, adopted). The pilot follows the adopted trigger
  (duplicates-plus-anomaly) and reports any case where the
  councils-1-and-3 trigger would have differed.

### (b) Preconditions and setup on the real laptop

- Branch: integration-20261127 checked out on the laptop (exact laptop
  path UNVERIFIED; the pilot brief names it).
- The 59 preserved L3 sets: rung3-run-log/rung3-snapshots/ on
  todolist-push. Count reconciled by this draft: 56 directories ending
  in -L3 plus 3 -L3-rerun directories (R3-001-L3-rerun, R3-002-L3-rerun,
  R3-003-L3-rerun) = 59 sets. The pilot re-counts at start; if the
  count differs, stop and report the discrepancy before re-sealing.
- The 7 genuine PASS sets and the 1 fabrication case are identified by
  the coordinator before the re-seal (the pilot does not guess which
  sets they are). Delivery mechanism: the coordinator writes the 7+1
  set IDs into the pilot brief before the re-seal. The runner
  cross-checks each label against the run record before the re-seal
  (the fabrication case is the R3-002 fabrication from the run record:
  FCC fabricated R3-002 three times; the fabricated evidence is the
  sealed R3-002-L3 set; the 7 genuine sets are the ones the landed
  hard-fail rule rejects per the register) and records the source per
  label in the pilot log. A label that cannot be cross-checked is not
  used; the pilot stops and the coordinator re-issues it.
- The duplicate screen is rung3-ci/collect-evidence.py (R9: identical
  non-empty content under two different names is flagged as a duplicate
  and fails the collect; verified lines 136-147 on the integration
  branch). The converged dedupe code does not exist yet; the pilot is
  BLOCKED until it lands. The pilot brief names the implementation
  file path and the exact re-seal invocation (storage-layer dedupe +
  loud alias entries) before the re-seal runs. If the implementation
  is not named, the pilot does not start.
- The re-seal writes to a scratch copy only, never to the preserved
  sets. The landed hard-fail rule stays in force until the pilot
  reports.
- No live driving, no browser use, no owner tabs. Pill up only while
  the runner drives the laptop (cu.py session rule); the re-seal
  itself touches no browser.

### (c) Live test steps

1. Record the integration-branch tip and the re-count of preserved
   sets (expect 59: 56 -L3 + 3 -L3-rerun). If the count is not 59,
   stop before re-sealing and report the count and the directory
   listing. Start a cu.py session if the runner drives the laptop;
   confirm the pill is visible.
2. Check available disk space against the source size of the 59 sets
   (record both numbers: source bytes and available bytes); do not
   copy if the space is insufficient. Copy the 59 sets to a scratch
   directory (record the scratch path). After copying, re-count the
   scratch copy (must be 59) and verify it against the originals by
   comparing the per-set manifest.json sha256 entries (collect-evidence
   writes manifest.json with a sha256 per file into each evidence
   dir); record the comparison result (match or the differing files)
   before re-sealing. Never re-seal in place, and never re-seal an
   unverified copy.
3. Run the converged dedupe re-seal over the verified scratch copy
   using the implementation and invocation named in the brief:
   storage-layer dedupe with loud alias entries; the duplicate screen
   fires on every occurrence; duplicates-plus-anomaly routes to human
   review (log each routing with set ID and anomaly cited).
4. For each of the 59 sets, record the outcome: PASS, route-to-review
   (with reason), or FAIL (with reason).
5. Check the two required outcomes: all 7 genuine PASS sets PASS; the
   1 fabrication case routes to review (not silently passed, not
   hard-failed as genuine).
6. Count how many sets the old rules would have rejected versus the
   converged form, by running the landed rule over the scratch copy:
   `python3 rung3-ci/collect-evidence.py <task> --evidence-root
   <scratch set dir>` per set, and count the "duplicate file content"
   failures. Expected: the hard-fail rule rejects 7 genuine sets of
   59; the naive dedupe rule fails 8 of 59 (7 genuine + 1
   fabrication). The converged form must reject 0 genuine sets.
7. Closing steps (shared rules): record one row in
   probes/ledger.jsonl citing the pilot report; save a grim screenshot
   of the desktop after release; verify the owner Zen PID is unchanged
   (shared rules); remove the scratch copy and test files; verify the
   desktop is clean (`hyprctl clients` diff against the start
   baseline); end the session and verify the pill is gone.

### (d) Before/after measurements

- Baseline (register): naive dedupe rule fails 8 of 59 real sealed
  sets (7 genuine PASS + 1 fabrication). Landed hard-fail rule
  rejects 7 genuine PASS evidence sets of 59.
- Per-set outcome table (59 rows): set ID, outcome under the
  converged form, outcome under the old hard-fail rule. Capture: the
  pilot log plus the re-seal output (manifest + reasons).
- Duplicate-screen firings: count of occurrences where the screen
  fired, from the re-seal log (must fire on every occurrence, not a
  sample).
- Human-review routings: count and set IDs, with the anomaly cited per
  routing.
- Copy verification: source size, available space, scratch re-count
  (59), manifest comparison result, from step 2.

### (e) Pass criteria

- 7 of 7 genuine PASS sets PASS under the converged form.
- 1 of 1 fabrication case routes to review (not passed, not
  hard-failed as genuine).
- 0 genuine sets hard-failed by the converged form.
- Duplicate screen fired on every occurrence in the 59 sets (count
  reported).
- Scratch copy verified complete (59 sets, manifest comparison match)
  before the re-seal ran.
- PROVEN only when run for real on the laptop with the measured
  numbers above. Anything less stays UNPROVEN.

### (f) Fail and rollback notes

- If the set count at step 1 is not 59, stop before re-sealing and
  report the count and the directory listing.
- If the scratch copy fails the re-count or the manifest comparison,
  stop before re-sealing, delete the partial copy, and re-copy. Do
  not re-seal a partial copy.
- If a genuine PASS set FAILS under the converged form, stop the
  re-seal, keep the scratch copy and the log, and report the set ID
  with the failure reason. Do not patch the dedupe mid-pilot.
- If the fabrication case PASSES silently, the pilot FAILS outright:
  the converged form does not preserve the fabrication signal. Report
  it and do not adopt.
- Rollback: nothing in the preserved sets was touched (scratch copy
  only); the landed hard-fail rule stays in force. The scratch copy
  is deleted after the report.

---

## M6: JPEG for intermediate screenshots

### (a) Item, source, register verdict/conditions

- Source: bottleneck register, Pilot-first full list.
- Proposal: JPEG for intermediate screenshots now; graded and
  text-bearing shots stay PNG until a scorer legibility trial shows
  zero verdict changes.
- Verdict: PILOT-FIRST, UNPROVEN until it reports.
- Context (register, Clock A): screenshot capture is a proven
  NOT-bottleneck (36-58 ms). M6 therefore claims no capture-time
  saving; the register names no minutes figure for M6. The pilot must
  state what it measures (per-shot file size and scorer verdicts) and
  must not claim a time saving the register does not give.

### (b) Preconditions and setup on the real laptop

- Branch: integration-20261127 checked out on the laptop (exact laptop
  path UNVERIFIED; the pilot brief names it).
- Screenshot capture call site (verified against the tree on the
  integration branch at tip 5365c84c): scripts/cu.py `observe()` (line
  978) and `observe_screen()` (line 1032), which capture with `grim
  -s 1 -g <geometry> -t ppm -` (lines 1007 and 1044) and write
  observation files named `<12-hex>.(png|jpg|json)` in the session
  state dir. Evidence screenshots (the subject of this pilot) are
  captured by the runner's grim command during drives (attested in
  runner briefs, e.g. R3-029 brief line 48).
- The three shot classes (intermediate, graded, text-bearing) are
  defined by evidence role, not by the capture code. The pilot brief
  must name the class rule before the pilot starts, with a rule the
  runner can apply per shot (for example, by snapshot-dir role:
  intermediate = working shots not cited in ket-qua.txt; graded =
  shots cited as grading evidence; text-bearing = shots whose content
  is text the scorer must read). The brief states the rule; if it
  cannot state one, the pilot does not start. Do not guess it here.
- A scorer legibility trial is arranged by the coordinator: the
  coordinator names the run's independent scorers (not mei), contacts
  them, and files the trial. The trial set and the PNG baseline set
  are the same tasks, so verdicts are comparable. The baseline is a
  fresh all-PNG grading of the same tasks by the same scorers. The
  recorded R3-L3 grades are NOT an acceptable baseline for the format
  effect (a fresh trial verdict compared against a months-old grade
  confounds grader drift with format effect); if only stale grades
  exist, the pilot reports the comparison as UNPROVEN for the format
  effect.
- Trial verdicts are pilot data only. They live in the pilot report
  and never enter the ledger or any grading record. Trial shots are
  kept as the pilot record, not used as grading evidence.
- No trial drive touches the owner Zen. Pill up for any driven step.

### (c) Live test steps

1. Record the integration-branch tip, the owner Zen PID (shared
   rules), the capture call site (scripts/cu.py observe() line 978),
   the class rule from the pilot brief, the trial scorers, and the
   baseline choice (fresh all-PNG grading). Start a cu.py session;
   confirm the pill is visible.
2. Run the pilot drive(s) (tasks named in the pilot brief; at least
   one task producing all three shot classes). Intermediate screenshots
   are written as JPEG; graded and text-bearing shots stay PNG.
3. For every shot, record: shot class, format, file size in bytes,
   and file path.
4. Scorer legibility trial: the independent scorers grade the pilot
   tasks from the JPEG intermediates plus the PNG graded shots,
   exactly as they would grade a normal set. Record every verdict
   (PASS/FAIL) and any legibility complaint per shot, in the pilot
   report only.
5. Compare trial verdicts with the fresh all-PNG baseline verdicts for
   the same tasks (same scorers). Count verdict changes.
6. Closing steps (shared rules): record one row in
   probes/ledger.jsonl citing the pilot report; save a grim screenshot
   of the desktop after release; verify the owner Zen PID is unchanged
   (shared rules); remove test files; verify the desktop is clean
   (`hyprctl clients` diff against the start baseline); end the
   session and verify the pill is gone.

### (d) Before/after measurements

- Per-shot file size: PNG size versus JPEG size in bytes, per shot
  class; capture from the file listing in step 3.
- Scorer verdicts: trial verdicts versus fresh all-PNG baseline
  verdicts, per task; capture from the trial grading record. Verdict
  changes counted (must be zero).
- Legibility complaints: count and shot IDs, from the trial record.
- Capture time is NOT measured as a saving (proven not a bottleneck,
  36-58 ms); if timed anyway, report it separately and do not claim
  it.

### (e) Pass criteria

- Zero verdict changes in the scorer legibility trial (trial verdicts
  equal fresh baseline verdicts for every task).
- Graded and text-bearing shots stayed PNG in every pilot set (zero
  exceptions).
- Per-shot sizes reported for both formats; no size claim without the
  measured numbers.
- Trial verdicts kept out of the ledger and all grading records
  (quarantine verified by checking the trial verdicts appear only in
  the pilot report).
- PROVEN only when run for real on the laptop with the measured
  numbers above. Anything less stays UNPROVEN.

### (f) Fail and rollback notes

- If any trial verdict differs from baseline, stop and report the
  task, the shot, and both verdicts. Do not re-grade to make the
  numbers match.
- If a graded or text-bearing shot is found in JPEG, the pilot is void
  for that set; re-run that set with the correct formats.
- If the capture call site or the class rule cannot be named from the
  repo and the brief, do not start; the pilot is blocked, not failed.
- If a trial verdict is found in the ledger or a grading record, stop
  the pilot, remove it from the grading record, and report the breach.
- Rollback: the screenshot writer reverts to all-PNG (the current
  behaviour). Trial shots are kept as the pilot record, not used as
  grading evidence.

---

## M9: owner-decision defaults

### (a) Item, source, register verdict/conditions

- Source: bottleneck register, Pilot-first full list.
- Proposal: owner-decision defaults. The owner pre-writes each default
  per class before a run; invalid-budget and grading-rule classes are
  permanently excluded; pilot on exactly one already-ruled class,
  event counting, against the 126 minute baseline.
- Verdict: PILOT-FIRST, UNPROVEN until it reports.
- Baseline (register, Clock B): owner waits on already-ruled question
  classes. The epoch 22 HOLD cost 126 minutes (deputy hold 15:18,
  resume 17:20). A full-run HOLD on 2026-11-25 sat at least 65 minutes
  inside a 166 minute gap; R3-029 waited inside a 272 minute gap
  partly for a parent-supplied password (the split between password
  wait and scheduling is UNVERIFIED). Owner time in total is UNPROVEN
  and unranked by design.

### (b) Preconditions and setup on the real laptop

- Branch: integration-20261127 checked out on the laptop (exact laptop
  path UNVERIFIED; the pilot brief names it).
- The owner pre-writes the default for the event-counting class BEFORE
  the run starts (the already-ruled class for this pilot is event
  counting: the count-by-event ruling, frozen keys.md L23, verified:
  line 23 states that 4 tasks sharing one common cause count as 1
  invalid event against both caps, "tong 5, moi nhom 2"). The
  pre-written default is filed in the run record with the owner's
  name and timestamp. No pre-written default, no pilot.
- Invalid-budget and grading-rule classes are permanently excluded:
  no default is written for them, ever, in this pilot.
- The pilot run is the named run (shared rules: the coordinator names
  and schedules it in the pilot brief); the class of questions counted
  is event counting only.
- Coordinator approval naming the exact run is recorded in the pilot
  log before the pilot starts (shared rules). Approval of the
  pre-written default alone is not approval of the pilot run.
- Owner Zen untouched. Pill up for any driven step.

### (c) Live test steps

1. Record the integration-branch tip, the owner Zen PID (shared
   rules), the pre-written event-counting default (text, owner,
   timestamp), and the coordinator approval (run). Start a cu.py
   session; confirm the pill is visible.
2. During the run, whenever an event-counting question arises, the
   runner applies the pre-written default at once (no hold, no message
   to the owner). Timestamp each application in the pilot log with the
   question and the default applied. At each application, the
   coordinator tags it trivial or hard in the pilot log: trivial means
   the answer follows from the pre-written default with no judgement;
   hard means the default resolves a question that previously required
   owner judgement.
3. Log every hold on any question class during the run in the pilot
   log with start/end timestamps and the class it belongs to (event
   counting or other). The runner is the actor for steps 2-3; the
   pilot log is the pilot report file (shared rules).
4. If a question arises in the invalid-budget or grading-rule class,
   do NOT apply any default; follow the normal escalation path and
   log it as an excluded-class occurrence.
5. At run end, total the hold minutes on the event-counting class and
   the hold minutes on all other classes, separately.
6. Closing steps (shared rules): record one row in
   probes/ledger.jsonl citing the pilot report; save a grim screenshot
   of the desktop after release; verify the owner Zen PID is unchanged
   (shared rules); remove test files; verify the desktop is clean
   (`hyprctl clients` diff against the start baseline); end the
   session and verify the pill is gone.

### (d) Before/after measurements

- Baseline: epoch 22 HOLD, 126 minutes, on already-ruled question
  classes (deputy hold 15:18, resume 17:20, 2026-11-26). The epoch 22
  HOLD is one data point, not a distribution of holds per question;
  the pilot reports against it and does not claim a distribution.
- Hold minutes on the event-counting class in the pilot run: capture
  from the per-question timestamps in step 3.
- Hold minutes on all other classes in the pilot run (control):
  capture the same way, reported separately and never mixed into the
  pilot figure.
- Applications of the pre-written default: count, with question IDs
  and the trivial/hard tag per application, from step 2.
  Excluded-class occurrences: count, from step 4.
- Control comparison: holds on the event-counting class in a run
  without the default (the epoch 22 HOLD is the available control
  data point; if no comparable control run exists, the pilot reports
  that and claims no saving).

### (e) Pass criteria

- The default was pre-written before the run (filed with owner and
  timestamp); zero defaults improvised mid-run.
- No saving is claimed from hold minutes alone. A saving claim
  requires all three: the applications count, the trivial/hard tags,
  and the control comparison. One trivial application, or only
  trivial applications, claims no saving: the pilot reports "no
  hard-question evidence" and claims nothing against the 126 minute
  baseline. Hold minutes are zero by construction under this pilot
  (the default is applied at once), so a zero hold figure alone
  proves nothing.
- Hold minutes on the event-counting class are measured and reported
  against the 126 minute baseline; a reduction is claimed only from
  the measured numbers plus the control comparison.
- Zero defaults applied to the invalid-budget or grading-rule classes.
- PROVEN only when run for real on the laptop with the measured
  numbers above. Anything less stays UNPROVEN.

### (f) Fail and rollback notes

- If the owner has not pre-written the default before the run, do not
  start the pilot; run the normal escalation path instead.
- If a default is found to have been applied to an excluded class,
  the decision is VOID: stop the pilot, report the question and the
  class, and re-take the decision through the normal path. A wrongly
  applied default never stands, at the coordinator's discretion or
  otherwise.
- If the pilot run has zero event-counting questions, the pilot
  reports zero applications and no saving; that is an inconclusive
  pilot, not a pass. Do not claim the baseline as saved.
- Rollback: the normal escalation path (ask the owner/coordinator) is
  restored for all classes; the pre-written default is filed as a
  record, not used again until re-approved.

---

## M11a: pre-flight credential, URL and fixture check

### (a) Item, source, register verdict/conditions

- Source: bottleneck register, Pilot-first full list.
- Proposal: pre-flight credential, URL and fixture check. Presence
  and format only, NEVER a live login. Saving claimed for the 40
  minute class only; the 272 minute gap's split is UNVERIFIED.
- Verdict: PILOT-FIRST, UNPROVEN until it reports.
- Context (register, Clock B): R3-029 waited inside a 272 minute gap
  partly for a parent-supplied password; the split between password
  wait and scheduling is UNVERIFIED. The 40 minute class is not named
  in the register; the pilot must name the class from the run record
  before running (candidate: credential/password waits, e.g. the
  R3-029 password wait, but the split is UNVERIFIED, so the candidate
  is not the claim).

### (b) Preconditions and setup on the real laptop

- Branch: integration-20261127 checked out on the laptop (exact laptop
  path UNVERIFIED; the pilot brief names it).
- The 40 minute class MUST be named before the pilot starts: the pilot
  brief names it from the run record (task IDs and wait class). If the
  class cannot be named, the pilot is measurement-only: it measures
  catches and check duration, claims no saving, and its result is NOT
  a PROVEN for M11a. A pilot that proves only that the check runs does
  not prove that it saves anything.
- The pre-flight check itself does not exist yet. The pilot is BLOCKED
  until it is built: the pilot brief names its implementation (file
  path and invocation), the exact checked items (which credential
  files, which URLs, which fixture files), and the exact
  presence/format rules, before the pilot starts. The coordinator is
  the named author of that decision; the deadline is before the pilot
  starts. Presence and format only: the check reads files and parses
  formats; it never performs a live login, never opens a session,
  never submits a credential.
- The check runs before every drive in the pilot run.
- The pilot run is the named run (shared rules: the coordinator names
  and schedules it in the pilot brief).
- Owner Zen untouched. Pill up for any driven step.

### (c) Live test steps

1. Record the integration-branch tip, the owner Zen PID (shared
   rules), the named 40 minute class (or MEASUREMENT-ONLY if it could
   not be named), and the check implementation from the pilot brief.
   Start a cu.py session; confirm the pill is visible.
2. Before each drive in the pilot run, run the pre-flight check:
   credential files present and well-formed, URLs well-formed,
   fixture files present. Timestamp the check start and end; log PASS
   or, for each failure, the missing/malformed item.
3. If the check FAILS on an item, do not start the drive; log the
   catch (what was missing/malformed) and fix or escalate per the
   normal path. Record the drive-start delay the catch avoided as
   UNVERIFIED unless the pilot brief states how it is measured.
4. If the check PASSES, start the drive normally and log the check
   duration.
5. Never perform a live login at any step of the pilot. If a step
   would require one, stop and log it as a pilot violation.
6. Closing steps (shared rules): record one row in
   probes/ledger.jsonl citing the pilot report; save a grim screenshot
   of the desktop after release; verify the owner Zen PID is unchanged
   (shared rules); remove test files; verify the desktop is clean
   (`hyprctl clients` diff against the start baseline); end the
   session and verify the pill is gone.

### (d) Before/after measurements

- Baseline: the 40 minute class (register; class identity UNVERIFIED
  until the brief names it, see (a)). The 272 minute gap (R3-029) is
  context only; its split is UNVERIFIED and the pilot does not claim
  it.
- Pre-flight check duration per drive: capture from the timestamps in
  step 2.
- Catches: count of drives blocked by a failed check, with the
  missing/malformed item per catch, from step 3.
- Drive-start delays: measured only if the pilot brief states the
  measurement; otherwise reported as UNVERIFIED.

### (e) Pass criteria

- The check ran before every drive in the pilot run (count of checks
  equals count of drives attempted).
- Zero live logins performed at any step.
- Every catch logged with the item that failed; every PASS logged
  with duration.
- Any saving claimed is for the named 40 minute class only, from
  measured numbers; the 272 minute gap split stays UNVERIFIED unless
  the pilot's instrumentation separates password wait from scheduling.
- If the class was not named, the pilot is measurement-only and its
  result is NOT a PROVEN for M11a, whatever the catch count.
- PROVEN only when run for real on the laptop with the measured
  numbers above. Anything less stays UNPROVEN.

### (f) Fail and rollback notes

- If the check blocks a drive incorrectly (false positive: the item
  was present and well-formed), log it, let the drive proceed only on
  the coordinator's written say-so, and count the false positive. The
  coordinator's say-so is a written reply in the run record (coord
  file), cited by path and timestamp in the pilot log; the runner
  waits for it before proceeding. Drafter-added rule (not a register
  condition): two false positives stop the pilot; the check is
  advisory until it reports. The pilot brief may replace the number
  two before the pilot starts.
- If the check itself fails to run (missing implementation, crash),
  the pilot is blocked; drives proceed on the old path (no pre-flight
  check) and the blockage is logged.
- If a live login is performed by mistake, stop the pilot at once and
  report it. The affected credential is identified from the check log
  (the failed check names the credential file); rotation or
  re-verification happens only on the coordinator's instruction, and
  the rotation is confirmed (old credential rejected, new credential
  accepted) and recorded before the pilot closes. The pilot does not
  continue after a live login.
- Rollback: drives run without the pre-flight check (the current
  behaviour). The check code stays off until the pilot reports.

---

## M11b: bot-wall probe in the runner's own session

### (a) Item, source, register verdict/conditions

- Source: bottleneck register, Pilot-first full list + section 3 proof
  downgrade; laptop handover list (M11b's live probe belongs to the
  coordinator's machine).
- Proposal: bot-wall probe in the runner's own session. Informs only;
  substitution stays a coordinator decision. The 4/4 fixture result is
  code-runs evidence (relabelled by council 3; it is not a live proof);
  the fixtures were built from the classifier's own marker list.
- Verdict: PILOT-FIRST, UNPROVEN until it reports.
- Context (register, Clock A): bot-check walls rooted in the webdriver
  signal. Six of 59 graded L3 rows are INVALID and all six are external
  service failures (timeanddate, Google, Openverse, Coolors, Namechk,
  Ezgif): 71.8 runner minutes, two blind gradings each, three tasks
  dropped from the denominator, the invalid budget exhausted, an owner
  re-plan forced, and the R10 response arc. The 59 figure carries the
  register's recorded row-count conflict (section 3: "row count 59 vs
  60 behind identical cycle totals", unresolved); this pilot uses 59
  as the re-counted set count and re-counts at start if it relies on
  it.

### (b) Preconditions and setup on the real laptop

- BLOCKED: the instrument does not exist as a named thing in the repo.
  Verified at fix time (2026-11-27, branch integration-20261127 at
  tip 5365c84c): no bot-wall classifier exists in scripts/, skill/,
  or rung3-ci/; no marker list is locatable anywhere in the repo
  (the only "marker list" hit in the whole tree is the register's own
  mention). The closest real artifact is
  improvements/council2-harness/bidi_round5.mjs, a direct check for
  one bot-wall class (R3-022, Google sorry), not a classifier. The
  pilot does not start until the coordinator cites the classifier
  path and marker list, or commissions the probe implementation, and
  the pilot brief names all three (classifier path, marker list,
  probe implementation: what the probe requests, what counts as a
  wall, what is recorded). Until then this plan is blocked, not
  runnable. A runner must never probe with an unnamed classifier.
- Session: the probe runs in a throwaway-profile Zen session on the
  laptop, never in the owner Zen, and never in a new tab in the owner
  Zen. A new tab in the owner Zen is a write to the owner's session,
  and a probe hit there is a wall hit on the owner's session. The
  throwaway session's PID is recorded at pilot start; the owner Zen
  PID is recorded before and after (shared rules) and must be
  unchanged.
- Attempt cap: one probe plus one drive per target, no retries. If a
  probe hits a wall on a target, there is no retry on that target in
  this pilot. No backoff beyond the single drive leg; a probe that
  retries on a wall hammers the service.
- Coordinator approval listing the exact targets is recorded in the
  pilot log before the pilot starts (shared rules). Default target
  list (confirmed by that approval): the six external-failure services
  from the run record (timeanddate, Google, Openverse, Coolors,
  Namechk, Ezgif). The laptop IP is long-term rate-limited (M12
  record); deliberately re-hitting all six spends the project's
  remaining standing with those services, so the approval is per
  target, not blanket.
- The probe informs only: it never authorises a substitution, a skip,
  or an INVALID on its own. Substitution stays a coordinator decision.
- Pill up for any driven step.

### (c) Live test steps

0. GATE (runs first and alone): confirm the classifier path, the
   marker list, and the probe implementation are named in the pilot
   brief. If any of the three is unnamed, STOP: the pilot is blocked,
   not failed. Record the gate outcome in the pilot log.
1. Record the integration-branch tip, the owner Zen PID (shared
   rules), the throwaway session PID, the classifier path and marker
   list, the probe implementation, and the coordinator approval
   (targets). Start a cu.py session; confirm the pill is visible.
2. For each approved target service, run the probe once in the
   throwaway-profile session. Timestamp start and end; record the
   probe outcome (wall present, wall absent, or inconclusive) with
   the evidence cited.
3. Run the drive leg once for the same target: one access to the same
   URL the original task used (named in the brief with the task ID),
   from the throwaway session, no retries. Record the real outcome:
   wall hit or not, with timestamps.
4. Compare probe outcome with real outcome per target; record
   agreement, false positives (probe said wall, drive found none),
   and false negatives (probe said none, drive hit a wall).
5. If the probe says a wall is present, the runner does NOT substitute
   on that basis; the substitution decision goes to the coordinator
   with the probe record attached. The referral is a written message
   in the run record (coord file), cited by path and timestamp in the
   pilot log. Log each such referral.
6. If a target is stopped early (probe triggers a wall, the session
   is flagged, or a service block occurs), stop probing that target
   at once and do not probe it again in the pilot. The pilot still
   reports: the stopped target is marked "stopped early, no real
   outcome" in the agreement table, and no accuracy claim is made
   from incomplete rows.
7. Closing steps (shared rules): kill the throwaway session by
   recorded PID after a cmdline check and verify it is gone; record
   one row in probes/ledger.jsonl citing the pilot report; save a
   grim screenshot of the desktop after release; verify the owner Zen
   PID is unchanged (shared rules); remove test files; verify the
   desktop is clean (`hyprctl clients` diff against the start
   baseline); end the session and verify the pill is gone.

### (d) Before/after measurements

- Baseline: the 4/4 fixture result is code-runs evidence only (not a
  live proof). No live probe accuracy figure exists.
- Probe outcome per target: wall present / absent / inconclusive, from
  step 2, with timestamps.
- Real outcome per target: wall hit or not, from step 3.
- Agreement table: agreements, false positives, false negatives, from
  step 4. Probe duration per target, from the timestamps. Stopped-early
  targets listed separately with the reason.
- Referrals to the coordinator: count, from step 5.

### (e) Pass criteria

- The probe ran in the throwaway-profile session for every pilot
  target that completed; every outcome logged with evidence and
  timestamps.
- Zero substitutions, skips, or INVALIDs made on probe authority
  alone.
- The agreement table is reported with counts (no accuracy claim
  without the measured table, and no accuracy claim from incomplete
  rows).
- PROVEN only when run for real on the laptop with the measured
  numbers above. Anything less stays UNPROVEN, including the 4/4
  fixture result, which remains code-runs evidence.

### (f) Fail and rollback notes

- If the probe itself triggers a wall, gets the runner session
  flagged, or causes a service block, stop probing that target at
  once (step 6), record it, and the runner proceeds only on
  coordinator instruction. Do not probe the same target again in the
  pilot.
- If the classifier path, marker list, or probe implementation cannot
  be cited before the pilot, do not start; the pilot is blocked, not
  failed (gate step 0).
- If a substitution is made on probe authority alone (bypassing the
  coordinator), stop the pilot, report it, and the substitution is
  reviewed by the coordinator as an unapproved change.
- Rollback: no probe runs; the runner follows the old path (hit the
  wall during the drive, then escalate). Probe records are kept as
  the pilot record.

---

## M12: adopt the drafted 429 rule

### (a) Item, source, register verdict/conditions

- Source: bottleneck register #9 (Do first, PILOT-FIRST); integration
  report Pilots list: "M12 (429 rule, coord/mei.md s.9)".
- Proposal: adopt the drafted 429 rule. The rule text already exists
  (coord/mei.md triage section 9, R3-L2 triage report, PR #225,
  merged; quoted text verified verbatim against coord/mei.md line 751
  on main): "(i) them luat gioi han toc do vao list muc 1: 'Neu dich
  vu tra ve HTTP 429 (gioi han toc do), doi 5 phut roi thu lai toi da
  2 lan; neu van 429, ghi ro vao file ket qua, task vo hieu theo muc
  1.'; (ii) o R3-040, pin 1 trang va phuong thuc lay (VM-fetch, vi IP
  laptop bi gioi han lau dai) luc dong bang; neu 429 van tiep dien
  thi vo hieu + backup DP-02 (du phong kho duy nhat)."
- Pilot form: total backoff window widened to 30-45 minutes with
  jitter (at 15 minutes it would spend the finite invalid budget on
  429s that might clear); every invocation logged with its outcome;
  false-INVALID count reported after one run. The observed loss it
  caps is 245.0 minutes on one task.
- Verdict: PILOT-FIRST, UNPROVEN until it reports.

### (b) Preconditions and setup on the real laptop

- Branch: integration-20261127 checked out on the laptop (exact laptop
  path UNVERIFIED; the pilot brief names it).
- The rule is written into the run's list section 1 (or the pilot run's
  brief) in the pilot form before the run: total backoff window 30-45
  minutes with jitter (the drafted 5 minutes, up to 2 retries, is the
  base text the pilot widens). The jitter rule is stated in writing
  (distribution and bounds) AND approved by the coordinator before the
  run; a jitter rule that is merely written down, unapproved, is not
  a control (a runner could write instant retries and burn the
  window). If the jitter rule is not stated and approved, the pilot
  does not start.
- The invalid budget is finite (frozen keys.md L9, verified: "Muc
  tran vo hieu: toi da 5 tong, toi da 2 moi nhom do kho", max 5 total,
  max 2 per difficulty group; L23, verified: one common-cause event
  counts as 1 event against both caps). The owner ruling on event 6
  (R3-045 ezgif) that external errors do not count toward the cap is
  recorded in the run record (R3-045 graded INVALID as event 6 on
  2026-11-26; the run continued and closed at 52/1 with 6 invalid
  events; coordinator state file); the pilot brief quotes the ruling
  text before the pilot starts. The pilot log tracks budget
  consumption per invocation.
- Cap on declarations: at most 1 INVALID declaration per difficulty
  group in this pilot (default cap, stated in the brief; the brief
  may set a lower cap, never a higher one without coordinator
  approval).
- The R3-040 pin (one page and fetch method, VM-fetch, because the
  laptop IP is long-term rate-limited) is recorded in the pilot brief
  where it applies; DP-02 is the hard backup and is used only per the
  rule.
- Coordinator approval naming the exact run is recorded in the pilot
  log before the pilot starts (shared rules).
- Owner Zen untouched. Pill up for any driven step.

### (c) Live test steps

1. Record the integration-branch tip, the owner Zen PID (shared
   rules), the rule text as written for the pilot (window 30-45
   minutes, jitter rule, coordinator approval of the jitter rule),
   the declaration cap (1 per group), and the invalid budget state
   at run start. Start a cu.py session; confirm the pill is visible.
2. During the pilot run, on every HTTP 429 from a service: log the
   invocation (task, service, URL, timestamp), then back off with
   jitter inside the 30-45 minute total window and retry. Log each
   retry with its timestamp and jitter value. Wait procedure: the
   affected task is parked; the run continues with other tasks (or
   the runner idles if none remain); the re-attempt happens after
   the jittered backoff. The wait is a scheduling action on the
   parked task, not a pause of the whole run.
3. If the service clears within the window, log the clear (time
   waited, retries used) and continue the task normally.
4. If the service is still 429 after the window: STOP and get
   coordinator approval for the declaration before making it. The
   runner presents the invocation history; the coordinator approves
   in writing in the run record. Only then record it in the result
   file and declare the task INVALID per list section 1 (with backup
   DP-02 only where the rule allows it). Log the declaration with
   the full invocation history and the approval citation. If the cap
   (1 per group) is already reached, no further declaration is made
   in this pilot; the task is escalated to the coordinator instead.
5. After the pilot run ends, re-attempt each declared-INVALID service
   once from a scratch context (a fresh throwaway-profile session,
   not the run's session) and record cleared or still-429, with
   timestamps. The runner performs the re-attempts after the run;
   the result is logged per declaration. A declaration whose service
   clears on re-attempt is a false-INVALID. Count false-INVALIDs and
   report the count. Also count 429s that cleared after 15 minutes
   inside the window (the widened-window justification).
6. If the first false-INVALID is found, STOP the pilot's remaining
   declarations at once (stop rule); no further INVALID is declared
   in this pilot, and the coordinator decides whether the affected
   declaration stands.
7. Closing steps (shared rules): record one row in
   probes/ledger.jsonl citing the pilot report; save a grim screenshot
   of the desktop after release; verify the owner Zen PID is unchanged
   (shared rules); remove test files; verify the desktop is clean
   (`hyprctl clients` diff against the start baseline); end the
   session and verify the pill is gone.

### (d) Before/after measurements

- Baseline (register, Clock A): one HTTP 429 episode (R3-040) cost a
  245.0 minute FAIL retry run, the longest in L2, because no retry
  rule existed.
- Invocations: count of 429 invocations in the pilot run, with
  per-invocation wait time, jitter value, and outcome (cleared vs
  still 429), from steps 2-4.
- False-INVALID count after one run: from step 5 (re-attempt results).
- Within-window clears after 15 minutes: count, from steps 3 and 5.
- Task minutes: per-task drive time for tasks that hit 429s, versus
  the 245.0 minute R3-040 loss; capture from the run record
  timestamps.
- Invalid budget consumption: budget used by 429 declarations in the
  pilot run, from the pilot log (capped at 1 per group).

### (e) Pass criteria

- Every 429 invocation logged with its outcome (no unlogged
  invocation).
- False-INVALID count reported after one run (a number, even if
  zero), measured by the step 5 re-attempts.
- The widened window is justified only if the log shows 429s
  clearing after 15 minutes that would otherwise have spent the
  invalid budget; report the count of such clears.
- Zero 429 declarations made outside the written rule (no ad-hoc
  INVALID); zero declarations without prior coordinator approval;
  zero declarations past the 1-per-group cap.
- PROVEN only when run for real on the laptop with the measured
  numbers above. Anything less stays UNPROVEN.

### (f) Fail and rollback notes

- If the jitter rule was not stated in writing AND approved by the
  coordinator before the run, the pilot is void; re-run with the
  rule written and approved.
- If a 429 is declared INVALID inside the window without the retries
  the rule requires, stop the pilot, report the task, and the
  coordinator decides whether the declaration stands.
- If the window is exhausted on every invocation (nothing ever
  clears), the pilot reports that with the numbers; the window is
  not widened further mid-pilot.
- If the first false-INVALID is found, the pilot stops declaring
  (step 6); remaining 429 tasks are escalated, not declared.
- Rollback: the rule reverts to the drafted text (5 minutes, up to 2
  retries) or to no rule, per the coordinator's decision; the pilot
  log is kept as the record. No ledger rows are rewritten by the
  pilot.

---

## M13: pin the Tier A result language in runner briefs

### (a) Item, source, register verdict/conditions

- Source: bottleneck register, Pilot-first full list.
- Proposal: pin the Tier A result language in runner briefs now
  (adopted); widen the checker to both formats ONLY after it also
  proves it still rejects the preserved R3-002 fabrication patterns.
- The two formats are the Vietnamese and English error-position forms
  (the bilingual union). Verified: rung3-ci/test_tier_a_check.py
  docstring ("Covers the formats that produced Tier A false negatives
  in R3-L3 ... json-errors: Vietnamese and English error-position
  forms (bilingual union fixed 2026-11-25; these tests lock it in)")
  and the coordinator state file ("OWNER INSTRUCTION 21:20 #1 (Tier
  A checker English support) APPLIED: rung3-ci/tier-a-check.py
  broadened to accept BOTH Vietnamese and English formats ...
  check_json_errors now unions 4 patterns (Vietnamese 'dong loi N,
  cot loi M'; English 'line N, col M', 'line N column M', 'Error
  line N ...')"). If the pilot brief finds the register meant a
  different pair, the widening half does not run until the pair is
  re-named in writing.
- Verdict: PILOT-FIRST for the widening half; the pin half is adopted
  now. The whole item stays UNPROVEN until the pilot reports.
- Checker: rung3-ci/tier-a-check.py (compares evidence values to the
  frozen key JSON; exits 0 for PASS, 1 for FAIL with machine-readable
  reasons, 2 for SKIP). Invocation: `python3
  rung3-ci/tier-a-check.py --key docs/rung3-answer-keys.json
  --evidence <dir> --task <ID>` (--key defaults to the frozen key
  JSON; never grade a real run against the test key
  rung3-ci/test-keys.json). Regression tests:
  rung3-ci/test_tier_a_check.py (R5, 2026-11-27; run with `python3 -m
  unittest rung3-ci/test_tier_a_check.py`). Tier A tasks
  (docs/rung3-answer-keys.md L39): R3-002, R3-007, R3-013, R3-014,
  R3-021, R3-072, R3-082, DP-02, DP-05. All verified against the tree
  on the integration branch at tip 5365c84c.
- The "result language" forms locked in by the regression tests (the
  formats that produced Tier A false negatives in R3-L3 and forced
  tiebreakers or scorer overrides): Vietnamese and English
  error-position forms (bilingual union fixed 2026-11-25); R3-021
  headerless quoted CSV counted as if it had a header row; R3-072
  pipe-separated table rows ("1 | d72-anh-1.png | 800 x 600") and
  numbered dash rows; R3-076 section labels "Free on /:" and "Free
  (free column):" plus pipe-separated process rows; DP-02 5-row
  summary table, grand total and files-with-keyword count, per-file
  detail block optional as a whole.
- Mutation controls (test file docstring): wrong values must still
  FAIL (off-by-one line or column, wrong number, missing row, wrong
  size, wrong PID).
- Forward only (test file docstring): these tests and the
  accompanying parser broadening apply to future grading.
  Already-graded R3-L3 results are not changed or re-graded.

### (b) Preconditions and setup on the real laptop

- Branch: integration-20261127 checked out on the laptop (exact laptop
  path UNVERIFIED; the pilot brief names it).
- Pin half: the Tier A result language (the forms in (a)) is written
  into the runner briefs for the Tier A tasks before the pilot run.
  The briefs are the ones the runners actually receive; the pin is
  verified by reading the briefs, not by assumption.
- Widening half: the two formats are the Vietnamese and English
  error-position forms (see (a)). The widened checker is the checker
  with the bilingual union applied; before steps 4-5, record
  `sha256sum rung3-ci/tier-a-check.py` and the git commit in the
  pilot log, and verify the binary under test is the widened checker
  (by that hash), not the current checker. A runner who runs the
  current checker by mistake records exit 1s that prove nothing
  about the widening.
- Preserved R3-002 fabrication evidence (verified from the run
  record, coordinator state file, 2026-11-25, epoch 5): the sealed
  snapshot set rung3-run-log/rung3-snapshots/R3-002-L3/ (9 files,
  manifest sha256
  0741a1aa90bc20b1257888fc6be33377aae02b351693a581c850b1b4d6852f15).
  The fabrication patterns are the 4 byte-identical timestamped PNGs
  (20261125-154500-json1, 154600-json2, 154700-json3, plus
  pill-verify-gone-2.png; all four sha256
  1a9daf3f097340cc6671122704a9ddda36ad0dbb953cf7c4b972faae83da37f0),
  each showing the jsonlint.com page with an EMPTY editor, no JSON
  content, no Valid JSON result, plus a ket-qua.txt claiming values
  with no evidence behind them. The R3-002-L3-rerun set is the
  genuine Muse re-run PASS set and must NEVER be used as fabrication
  evidence; using it would test the widening against a genuine set
  and reject the widening on a false failure.
- Coordinator approval naming the exact run is recorded in the pilot
  log before the pin half starts (shared rules).
- Owner Zen untouched. Pill up for any driven step.

### (c) Live test steps

1. Record the integration-branch tip, the owner Zen PID (shared
   rules), the pinned result language as written in the runner briefs
   (quote the brief lines), the two formats (Vietnamese + English
   error-position forms), the fabrication evidence path (R3-002-L3,
   manifest hash above), the checker hash, and the coordinator
   approval (run). Start a cu.py session; confirm the pill is
   visible.
2. Pin half: run the pilot tasks (Tier A tasks, named in the pilot
   brief). Runners write results in the pinned language. After each
   task, run `python3 rung3-ci/tier-a-check.py --key
   docs/rung3-answer-keys.json --evidence <evidence dir> --task
   <ID>` over the evidence and record the exit code (0 PASS, 1 FAIL,
   2 SKIP) with reasons, from the tool output, not from memory.
3. Count Tier A false negatives in the pilot run: checker FAILs on
   evidence written in the pinned language that the scorers judge
   correct, forcing a tiebreaker or scorer override. Checker FAILs on
   evidence written OUTSIDE the pinned language do NOT count in this
   total; they are brief-compliance misses, logged separately in (f).
   Compare with the R3-L3 baseline: the pilot brief states the
   baseline count with its source before step 3 (source: the
   coordinator state notes; known cases include the R3-002 re-run,
   where the checker FAILED on 'line 1, col N' phrasing the scorers
   judged correct, R3-021 which went to a tiebreaker, and R3-072,
   whose checker FAIL was overridden openly).
4. Widening half (only after step 3, and only with the two formats,
   the fabrication evidence, and the checker hash recorded in step
   1): run the widened checker against the preserved R3-002
   fabrication evidence (`python3 rung3-ci/tier-a-check.py --key
   docs/rung3-answer-keys.json --evidence
   rung3-run-log/rung3-snapshots/R3-002-L3/ --task R3-002`) and
   confirm it still FAILs (exit 1) on every fabrication pattern
   (the 4 byte-identical PNGs and the unsupported ket-qua.txt).
5. Run the mutation controls: wrong values (off-by-one line or
   column, wrong number, missing row, wrong size, wrong PID) must
   still FAIL under the widened checker. Record each control and its
   exit code.
6. Closing steps (shared rules): record one row in
   probes/ledger.jsonl citing the pilot report; save a grim screenshot
   of the desktop after release; verify the owner Zen PID is unchanged
   (shared rules); remove test files; verify the desktop is clean
   (`hyprctl clients` diff against the start baseline); end the
   session and verify the pill is gone.

### (d) Before/after measurements

- Baseline: Tier A false negatives in R3-L3 forced tiebreakers or
  scorer overrides (the regression tests lock in the formats that
  caused them). The baseline count is stated in the brief with its
  source before step 3 (see (c)).
- False negatives in the pilot run: count, with task IDs and checker
  reasons, from step 3 (pinned-language evidence only). Capture: the
  checker output per task.
- Fabrication-pattern rejections: per-pattern checker exit code (must
  be 1 FAIL), from step 4.
- Mutation controls: per-control exit code (must be 1 FAIL), from
  step 5.
- Checker version under test: sha256 + git commit, recorded before
  steps 4-5.
- Checker exit codes are captured from the tool output, not from
  memory.

### (e) Pass criteria

- The pinned result language is present in the runner briefs (quoted
  in the pilot log) and the runners used it.
- False-negative count for the pilot run is measured and reported; a
  reduction is claimed only from the measured numbers.
- The widened checker FAILs (exit 1) on every preserved R3-002
  fabrication pattern and on every mutation control.
- Zero already-graded R3-L3 results changed or re-graded (forward
  only).
- PROVEN only when run for real on the laptop with the measured
  numbers above. Anything less stays UNPROVEN.

### (f) Fail and rollback notes

- If the two formats or the preserved fabrication evidence cannot be
  named before the widening half, that half does not run; the pin half
  still reports on its own.
- If the widened checker PASSES any fabrication pattern or mutation
  control, stop: the widening is rejected, the checker reverts to the
  current form, and the failure is reported with the pattern and the
  checker output.
- If a pilot task's evidence is graded from a format outside the
  pinned language, log it as a brief-compliance miss, not as a checker
  failure; it does not count in the step 3 false-negative total.
- If the checker hash recorded before steps 4-5 does not match the
  widened checker, stop: the steps were run against the wrong binary
  and prove nothing; re-run with the right one.
- Rollback: the checker reverts to the current form; the pinned
  language stays in the briefs (adopted) unless the coordinator
  removes it. The pilot log is kept as the record.

---

## M15: defective-test register

### (a) Item, source, register verdict/conditions

- Source: bottleneck register, Pilot-first full list.
- Proposal: defective-test register. Every entry carries branch
  lineage (merge-base checked), an owner, and an expiry that deletes.
- Verdict: PILOT-FIRST, UNPROVEN until it reports.
- Context (integration report, M17 record): pre-existing suite state
  on the VM is 2233 ok, 81 error, 9 fail, 17 skip (missing build
  artifacts/binaries; identical in serial and sharded). Known
  defective tests documented in the M17 record: test_ime_cleanup
  (real-signal timing tests flaking under 4-way parallel load on a
  1.5-CPU VM; serial 3/3 OK) and test_cli_exit_codes (exists as a
  bare function test in two modules, test_phase3_brief and
  test_phase3_cleanup, colliding in the outcome map). These are
  candidates for entries, not entries yet.

### (b) Preconditions and setup on the real laptop

- Branch: integration-20261127 checked out on the laptop (exact laptop
  path UNVERIFIED; the pilot brief names it).
- The register file path is NOT named in the register. The pilot brief
  must name it before the pilot starts (candidate: rung3-ci/
  alongside the other CI tools, but do not assume; the path is
  UNVERIFIED until the brief names it). The coordinator is the named
  author of that decision; the deadline is before the pilot starts.
- Seed candidates (from the M17 record): test_ime_cleanup
  (parallel-load flake), test_cli_exit_codes (two-module collision).
  Each seed entry needs all three fields before it is added: branch
  lineage (merge-base checked against the branch it applies to), an
  owner, and an expiry (a date after which the entry is deleted).
- The expiry mechanism (what deletes the entry, when, and by what
  command or job) is stated in the pilot brief before the pilot
  starts; a register that only flags expiry without deleting does not
  meet the condition.
- At least one entry in the pilot has an expiry inside the pilot
  window: a deliberately short-lived test entry (expiring 1 hour
  after creation) so a deletion is actually observed. A deletion
  mechanism that never runs is not proven by this pilot.
- Owner Zen untouched. Pill up for any driven step.

### (c) Live test steps

1. Record the integration-branch tip, the owner Zen PID (shared
   rules), the register path from the pilot brief, and the expiry
   mechanism (what deletes, when, by what command or job). Start a
   cu.py session; confirm the pill is visible.
2. Create the register at the named path with the required fields per
   entry: test ID, branch lineage (merge-base checked), owner, expiry.
   Add the short-lived test entry (expiry 1 hour after creation) in
   addition to the seed entries.
3. Add the seed entries (test_ime_cleanup, test_cli_exit_codes) with
   all three fields verified: lineage checked by merge-base (record
   the merge-base hash per entry), owner named, expiry dated.
4. Run the full test discover (serial, the gate of record):
   `python3 rung3-ci/test-discover.py run --start-dir tests`, and
   record the wall time and the output file path. Then, for each
   registered test, check the discover output for that test ID with
   `grep -F <test-id> <discover-output-file>` and record the matched
   lines as the match evidence: whether the register's entry matched
   the run outcome (failed/flaked as registered, or passed). The
   match verdict is read from the grep output, not from eyeballing
   two lists.
5. Check the expiry mechanism: after the short-lived entry's expiry
   passes, verify it was deleted (record the deletion with the
   command or job output that deleted it). For entries not yet
   expired, record the next expiry date. If no deletion is observed
   in the pilot window, the expiry condition stays UNPROVEN (the
   pilot does not pass it).
6. Closing steps (shared rules): record one row in
   probes/ledger.jsonl citing the pilot report; save a grim screenshot
   of the desktop after release; verify the owner Zen PID is unchanged
   (shared rules); remove test files; verify the desktop is clean
   (`hyprctl clients` diff against the start baseline); end the
   session and verify the pill is gone.

### (d) Before/after measurements

- Baseline: suite state on the VM is 2233 ok, 81 error, 9 fail, 17
  skip (M17 record). The register does not yet exist, so there is no
  before figure for register use; the pilot establishes the first
  figures.
- Entries: count of entries, with per-entry lineage (merge-base
  hash), owner, and expiry, from step 3.
- Register consultations: per registered test, whether the entry
  matched the run outcome, from the grep output in step 4.
- Expiry deletions: count of entries deleted on expiry, from step 5,
  with the deleting command or job output cited; next expiry date per
  surviving entry.
- Full discover wall time with the register consulted versus the
  serial baseline (M17: serial 292.0-313.0 s on the VM; laptop
  re-measure pending). Report both numbers; do not claim a saving
  without them.

### (e) Pass criteria

- Every entry carries all three fields (branch lineage, owner,
  expiry); zero entries missing any field.
- Lineage verified by merge-base for every entry (hash recorded per
  entry); any entry whose lineage does not check out is removed, not
  corrected silently.
- At least one deletion observed in the pilot window (the short-lived
  test entry), with the deleting command or job output cited. If no
  deletion is observed, the expiry condition stays UNPROVEN and the
  pilot does not pass it.
- Match evidence for every registered test comes from the grep output
  in step 4, not from a human eyeball.
- PROVEN only when run for real on the laptop with the measured
  numbers above. Anything less stays UNPROVEN.

### (f) Fail and rollback notes

- If the register path cannot be named before the pilot, do not
  start; the pilot is blocked, not failed.
- If the expiry mechanism is not stated before the pilot (what
  deletes, when, by what command or job), do not start; the pilot is
  blocked, not failed.
- If an entry outlives its expiry without deletion, the pilot FAILS
  on the expiry condition: the entry is deleted at once and the
  failure is reported with the entry ID and the missed date.
- If the register is consulted but a registered test's outcome does
  not match its entry (e.g. it passes cleanly), log the mismatch; the
  entry is reviewed by its owner, not deleted silently.
- Rollback: the register file is removed (or left empty with a note)
  and test runs proceed without it (the current behaviour). The pilot
  log is kept as the record.

---

## Count

Plans written: 10 full plans (M1, M4, M5, M6, M9, M11a, M11b, M12, M13,
M15). Items found already integrated on origin/integration-20261127 at
tip 5365c84c (83 integration-phase commits since 4b70b71c checked):
none. Token measurements: none in this slice (grep for "token" returns
0 hits); council-2 H3 does not touch slice B.

---

## Slice C: M pilots 2 (M19, M21, M26, M27, M28b, M30, M31, M32, M33)

Verification status at fix time (2026-11-27 13:39 UTC, tip `5365c84c`, merge int-rt-a11y): grepped the full branch log since `4b70b71c`. None of the 9 items below is implemented or
live-tested there. M28a (append-only watchdog rolling branch)
MERGED (`877afe6d`, wave 1, merge `58013edd`): script
`scripts/watchdog_append.py` plus `docs/watchdog-rolling-branch.md`,
one rolling branch per lane (`watchdog/<lane>`), fast-forward
pushes only, no force-push path. Lane switch-over is still a
coordinator decision, and no `watchdog/*` branch exists on origin
yet (verified by `git ls-remote` at fix time), so no durable
watchdog record location exists yet. That changes two plans:
M28b is DORMANT PERMANENTLY (its trigger can no longer fire)
and M33 is still BLOCKED, with the reason updated (see below).

Proof law (owner-set, bottleneck study introduction, lines
14-22): a claim counts as proven only if run for real on the
laptop with measured before/after numbers; everything else is
UNPROVEN, with the pilot that would prove it named. PROVEN in
this file means laptop-PROVEN only. A measurement made on the
register machine is written as "measured on the register
machine", never as PROVEN.

No figure in this draft is invented: where the sources give no
number, command, path, or baseline, the plan says UNVERIFIED and
states the pre-run decision that supplies it (who names it, by
when). A pilot does not start while a load-bearing pre-run
decision is unnamed.

## Shared rails (every plan in this slice)

These rails apply to all plans below and are not repeated in
full per plan; each plan's (c) ends with the closing steps.

- Owner Zen PID: record it with `pgrep -af zen-bin` and
  identify the owner Zen by the owner profile dir in its
  cmdline (a throwaway-profile Zen uses a different profile
  dir). Record the PID at pilot start; re-run the same command
  at pilot end and confirm the same PID is alive and no new
  owner-profile Zen appeared. Never copy a PID from an earlier
  record (807599 was the 2026-11-27 PID, historical only).
- Branch tip: record the `integration-20261127` tip at pilot
  start in the pilot report.
- Desktop clean: record `hyprctl clients` at pilot start
  (the owner-window baseline); at pilot end re-run it and
  confirm only owner windows remain, save a grim screenshot
  of the desktop after release, and remove test files.
- Ledger row: every pilot writes one row to
  `probes/ledger.jsonl` citing its outputs. Row fields
  (`probes/README.md`): `date`, `probe`, `question`,
  `result`, `output`, `verdict`. Validate with
  `python3 probes/validate-ledger.py` (required fields are
  `date`, `probe`, `question`, `result`, `output`, `verdict`).
  Example row: `{"date": "2026-11-27", "probe":
  "improvements/m19-pilot-20261127.md", "question": "M19
  per-session saving, persistent tc02 client",
  "result": "before X s, after Y s, delta Z s",
  "output": "improvements/m19-pilot-20261127.md",
  "verdict": "UNPROVEN until laptop run"}`.
- Test runner: suites run with
  `python3 rung3-ci/test-discover.py run --modules <module>`
  from the repo root (serial mode, the gate of record).
- Pilot report: each pilot files its report at
  `improvements/<item>-pilot-20261127.md` on the pilot
  branch, and the ledger row cites that path.
- RDP port convention: 6021 is the observed value from the
  2026-11-27 live records; re-verify at run time, never
  assume it.
- Token capture: per-verdict token counts come from the
  harness/model usage readout recorded verbatim per verdict
  (the agent session's own reported token use). If the
  harness gives no per-verdict figure, tokens are UNMEASURED
  and the token half of the pass criterion is INCONCLUSIVE,
  not passed. No token figure is ever estimated.
- Live steps run under a `cu.py` session with the pill
  visible; record the owner Zen PID before the run and verify
  it is unchanged after (never copy a PID from an earlier
  record as a current fact); remove test files; verify the
  desktop is clean at the end. Pilot work goes on its own
  branch off `integration-20261127`; the coordinator merges,
  gates, and lands. Quality gates unchanged: unit green, live
  test, gate, measured numbers. The cu.py session + owner-Zen-PID rail
  applies only to driven steps; the repo-only pilots in this slice
  (M27, M30, M31, M32, M33) never drive a browser, so for them the rail
  is vacuous and no session is opened.

Owner Zen is untouched by all 9 pilots below unless the item
says otherwise; none of the 9 requires it.

---

## M19: persistent tc02 client

### (a) Item, source, register verdict/conditions

M19, bottleneck register pilot-first list: persistent tc02
client, ONLY if the tc02 Step 3 happens for other reasons.
Direction measured on the register machine (import paid once
vs 228-270 ms per spawn); the end-to-end saving is an UNPROVEN
projection capped at about 11 s per session (register section 2
intro: the tc02 transaction, about 11 s per session, has one
claimant, M19, capped, unproven; section 3: M19 end-to-end
figures quarantined as a repo projection, only the direction
is proven on the register machine). Laptop handover list:
M19's end-to-end timing belongs to the coordinator's machine.

"Step 3" here means the third tc02 work phase, after Step 2
(the predict-then-verify crop grounding, commit `58704a28`,
verified at fix time: `58704a28 feat(tc02):
predict-then-verify-crop grounding (Step 2)`). It does NOT
mean procedure step S3 (the observe step) in
`scripts/plans/tc02-v1.json`. No Step 3 change is named
anywhere in the sources read; see (b).

### (b) Preconditions and setup on the real laptop

- Branch: own pilot branch off `integration-20261127`.
- A tc02 Step 3 change must already be happening for other
  reasons; this pilot does not start one. The Step 3 change
  (what it changes, who owns it, which branch) is UNVERIFIED
  from the sources read. The coordinator names the Step 3
  change in the pilot brief before the pilot starts; if no
  Step 3 change is named, the pilot does not start. Do not
  guess it here.
- tesseract must be installed on the laptop (`which tesseract`;
  the tc02 typed-text tests fail without it). If absent, stop:
  that is the M16 defect class, not this pilot.
- Files the pilot touches: `scripts/tc02_controller.py` and
  `tests/test_tc02_controller.py` (the 2 typed-text tests are
  `test_typed_text_check_passes_when_fragment_is_visible`
  at line 640 and
  `test_typed_text_check_fails_when_fragment_is_absent`
  at line 657, verified on the branch at fix time).
- Test command (verified on the branch): from the repo root,
  `python3 rung3-ci/test-discover.py run --modules
  test_tc02_controller` (run mode, serial, gate of record;
  `--modules` restricts to that module).
- Per-spawn import-cost capture (verified mechanism): run
  `python3 -X importtime -c "import sys; sys.path.insert(0, 'scripts'); import tc02_controller"`
  from the repo root and read the cumulative
  `tc02_controller` import-time line. On this VM at fix time
  it reported 146902 us (about 147 ms). The runner records
  the exact command and the laptop figure.
- Baseline to re-confirm on the laptop before the change:
  per-spawn import cost, register figure 228-270 ms.
- Persistent-client build spec: one `Tc02Controller`
  instance (`scripts/tc02_controller.py`, class at line 323)
  held in a single long-lived process on the pilot branch,
  imported once and reused across the session's checks,
  instead of one script process per check
  (`python3 scripts/tc02_controller.py --plan <plan> --live`,
  `main()` at line 1644). The interface by which checks reach
  the client is stated in the pilot brief before the build
  starts; the Step 3 change it rides on is untouched.

### (c) Live test steps

1. Start a `cu.py` session with the pill visible. Record the
   owner Zen PID (shared rails); verify it is unchanged at
   the end.
2. Baseline arm: run the tc02 typed-text tests in the current
   per-spawn form with the command in (b). Record wall time
   per test and per session, and the import cost per spawn
   with the importtime command in (b).
3. Implement the persistent client on the pilot branch per
   the build spec in (b), keeping the Step 3 change it rides
   on untouched.
4. Pilot arm: run the same typed-text tests against the
   persistent client. Record the same wall times.
5. Run the full `tests/test_tc02_controller.py` suite in both
   arms and confirm identical pass/fail outcomes.
6. Kill the persistent client: record its PID, check its
   cmdline matches the pilot client, kill it, and verify it
   is gone (`pgrep` shows no such process). Run a
   process-list check at pilot end: no pilot client remains.
7. Closing rails: remove test files; verify the desktop is
   clean (`hyprctl clients` plus grim screenshot, shared
   rails); write one row to `probes/ledger.jsonl` citing the
   pilot report; end the session.

### (d) Before/after measurements

- Per-spawn import cost, before arm: register baseline 228-270
  ms per spawn; re-measure on the laptop with the importtime
  command in (b) and report the laptop figure.
- Per-session wall time, before vs after: capture from the test
  run output for the typed-text tests and the full
  `test_tc02_controller.py` suite.
- End-to-end tc02 session saving: register projection capped at
  about 11 s per session; the pilot must measure the real
  per-session delta and report it against that cap.
- Correctness: pass/fail outcomes of the full tc02 controller
  suite, before vs after (must be identical).

### (e) Pass criteria

- Direction: the persistent client pays the import once and
  the per-spawn 228-270 ms cost is gone from the after arm,
  measured on the laptop with the importtime command in (b).
- End-to-end: PROVEN only if the measured per-session saving
  is reported with before/after numbers and is at or under
  the about-11 s cap; a saving above the cap is a failed
  measurement to investigate, not a better result.
- The claim stays UNPROVEN if either arm was not run on the
  laptop, if the Step 3 trigger is not named, if the suite
  outcomes differ between arms, or if the persistent client
  was not killed at pilot end.
- Adoption decision belongs to the coordinator after the pilot
  report; no adoption is part of this pilot.

### (f) Fail and rollback notes

- If the after arm changes any suite outcome, stop, keep the
  per-spawn form as the working code, and report the differing
  test names and outputs. Do not land a client that changes
  verdicts.
- If tesseract is missing, stop the pilot and file the M16-class
  defect instead; do not substitute a fake OCR path.
- If the persistent client cannot be killed cleanly, stop and
  report it; do not leave a background client holding OCR
  state or a port.
- Rollback: revert the pilot branch; the per-spawn client is the
  shipped form and is restored by dropping the branch.

---
## M21: predicted-crop OCR

### (a) Item, source, register verdict/conditions

M21, bottleneck register pilot-first list: predicted-crop OCR is
already-landed practice claiming no new saving; any future claim
needs a before/after on a tesseract machine over pages NOT used
to tune the predictor. Locally UNPROVEN: the register's machine
has no tesseract, which is itself the M16 defect class
(register section 2 intro lists M21's tesseract before/after
among the four laptop-bound, VM-unverifiable pilots; section 3
laptop handover list: M21's tesseract before/after belongs to
the coordinator's machine).

### (b) Preconditions and setup on the real laptop

- Branch: own pilot branch off `integration-20261127`.
- tesseract installed on the laptop: check `which tesseract`
  first and record `tesseract --version`. Laptop tesseract state
  is UNVERIFIED from the sources read. If absent, stop: the M16
  defect class applies, not this pilot.
- The already-landed practice to measure against is the
  predict-then-verify-crop grounding, tc02 Step 2, commit
  `58704a28` on `todolist-push` (`scripts/tc02_controller.py`,
  `scripts/multi_candidate.py`, `scripts/omarchy_cmd.py`).
- OCR command, both arms (verified in the code):
  `tesseract <image> stdout --psm 6`, from
  `scripts/tc02_controller.py` `_ocr_text` (lines 1122-1145:
  `tesseract = shutil.which('tesseract')`, then
  `subprocess.run([tesseract, candidate_path, 'stdout',
  '--psm', '6'], ...)`). Before arm runs it on the full page
  image; after arm runs it on the cropped image, with crop
  rects from `scripts/plans/tc02-v1.json` `layout`. Pin
  `--psm 6` and the recorded tesseract version for both arms;
  a version or config difference between arms voids the
  comparison.
- Held-out page set: pages NOT used to tune the predictor.
  The tuning set is exactly the files hashed in the tc02
  evidence manifest,
  `improvements/v3-judge-evidence-20261117/tc02-evidence/evidence-manifest.md`
  (113 hashed files; the crop rects were derived from
  gate3-A2 TSV on those pages). The held-out check is
  mechanical, not an assertion: a page is held out only if
  its SHA-256 does not appear in that manifest. The pilot
  must name the pages, where they came from, and how they
  were captured, BEFORE running either arm. New held-out pages
  are captured fresh on the laptop; their SHA-256 values are
  recorded and checked against the manifest before either arm
  runs. Pages from the tc02 evidence set must be excluded;
  any page whose SHA-256 matches the manifest is in the
  tuning set.
- Accuracy metric: the register names no metric. Ground truth
  must be independent of both arms: a human transcript of
  each page's text, written before either arm runs. One arm's
  output must never serve as the other arm's ground truth;
  if ground truth is created by running full-page OCR (the
  before arm), the comparison is circular and the pilot is
  void. The pilot states before running whether it measures
  character/word accuracy against the transcript, verdict
  agreement, or both.

### (c) Live test steps

1. Start a `cu.py` session with the pill visible. Record the
   owner Zen PID (shared rails); verify it is unchanged at
   the end. Owner Zen is untouched by this pilot (OCR runs
   over captured pages, not live browsing).
2. Confirm `which tesseract` succeeds on the laptop and record
   the tesseract version. If it fails, stop per (b).
3. Freeze the held-out page list in the pilot report before
   either arm runs, with each page's SHA-256 and the manifest
   check result (not in the tuning set). Freeze the human
   transcript ground truth per page at the same time.
4. Before arm: run full-page OCR over every held-out page with
   the command in (b). Record per-page wall time and the
   accuracy metric stated in (b).
5. After arm: run predicted-crop OCR over the same pages with
   the same command on the cropped images. Record per-page
   wall time and the same accuracy metric.
6. Compare per page: wall time delta and accuracy delta.
   Record every page where the two arms disagree.
7. Closing rails: remove test files; verify the desktop is
   clean (`hyprctl clients` plus grim screenshot, shared
   rails); write one row to `probes/ledger.jsonl` citing the
   pilot report; end the session.

### (d) Before/after measurements

- Per-page OCR wall time, full-page (before) vs predicted crop
  (after): capture from the OCR run output per page.
- Accuracy metric as stated in (b), per page, both arms,
  against the human transcript.
- Page-level disagreement count: number of held-out pages where
  the arms differ on the accuracy metric.
- No baseline numbers exist in the register for either metric;
  the before arm IS the baseline and must be measured first.

### (e) Pass criteria

- A future saving/accuracy claim counts as PROVEN only if the
  before/after ran on a tesseract machine (the laptop) over
  held-out pages verified mechanically against the manifest,
  with per-page numbers reported and ground truth independent
  of both arms.
- The claim stays UNPROVEN if any page in the set was used to
  tune the predictor, if tesseract was absent, if the
  accuracy metric was chosen after seeing the results, or if
  ground truth came from either arm's output.
- The already-landed practice claims no new saving; this pilot
  proves or fails a NEW claim only. A null result (no measured
  difference) is a result and is reported as such.
- Adoption decision belongs to the coordinator after the pilot
  report.

### (f) Fail and rollback notes

- If the held-out set cannot be shown to exclude tuning pages,
  stop and report the pilot as not run; do not re-label tuned
  pages as held out.
- If predicted-crop accuracy is worse than full-page on any
  held-out page, report the per-page deltas; do not average
  the loss away.
- If the tesseract version or config differs between arms,
  the comparison is void; re-run with both pinned.
- Rollback: nothing is landed by this pilot; the landed
  predict-then-verify practice is untouched either way.

---

## M26: verdict template with a line cap

### (a) Item, source, register verdict/conditions

M26, bottleneck register do-first #10, PILOT-FIRST, proof label
UNPROVEN. Supporting experiment downgraded in section 3
(council 3, unrefuted): one artifact, two different agents, no
recall measurement; "kept the top findings" is judgement, not
recall. Pilot (register #10): controlled repeat, agent pool
held constant or arms swapped, at least three artifacts
including one hard one, findings recall reported against the
free-form arm; every capped verdict carries a "dropped for
length: N" count; the cap NEVER applies to BLOCKING findings.
Aimed at the deliberation pool, whose waste share is unmeasured
(register section 2 intro: the deliberation family claims
nothing in aggregate).

### (b) Preconditions and setup on the real laptop

- Branch: own pilot branch off `integration-20261127`.
- The verdict template with its line cap must exist as a
  written template before the pilot; template text is
  UNVERIFIED from the sources read (the register names the
  template but gives no text or line number). The coordinator
  writes (or approves) the exact template text and cap value
  in the pilot brief before any verdict is written; the pilot
  does not start without them. The pilot records the exact
  template text and cap value used.
- Artifact set: at least three artifacts, including one hard
  one. The exact artifacts are UNVERIFIED from the sources
  read. The coordinator names them in the pilot brief before
  running, and the hard one must be identified as hard before
  the verdicts are written; the pilot does not start without
  them.
- Agent pool: the same agents grade in both arms, or the arms
  are swapped across agents (register condition). The
  coordinator names the pool and the arm assignment in the
  pilot brief before running; the pilot does not start without
  them.
- Blinding (anti-contamination rule): agents in one arm do
  not see the other arm's verdicts. Either the capped arm runs
  first, or different agents write each arm. The arm order and
  the blinding method are recorded in the pilot log before
  either arm runs. Same agents writing both arms in sequence
  with no blinding voids the recall measurement.
- Recall threshold: the register gives no numeric recall
  threshold. The coordinator states a threshold in the pilot
  brief before running, or the pilot reports the recall figure
  with no held/not-held verdict and the coordinator decides.
  Either way the choice is recorded before any verdict is
  written.
- Pricing: per the M34f rule adopted in the register, every
  deliberation measurement is priced in wall time AND tokens
  (token capture per the shared rails).

### (c) Live test steps

1. Start a `cu.py` session with the pill visible whenever the
   runner drives the laptop; record the owner Zen PID and verify
   it is unchanged at the end. Owner Zen is untouched by this
   pilot (review work, not live browsing).
2. Freeze the artifact list (at least three, one hard), the
   agent pool and arm assignment, the template text with
   its cap, the blinding method and arm order, and the recall
   threshold decision in the pilot report before any verdict
   is written.
3. Free-form arm: each agent writes verdicts on each artifact
   with no line cap. Record findings per artifact, wall time
   and tokens per verdict.
4. Capped arm: the same agents (or swapped arms, per the
   blinding rule in (b)) write verdicts on the same artifacts
   under the template cap. Record findings per artifact, wall
   time and tokens per verdict, and the "dropped for length:
   N" count on every capped verdict.
5. Score recall: a third reader who wrote neither arm's
   verdicts scores recall per artifact. A finding counts as
   kept on semantic match, judged by the scorer, with the
   matching capped-arm text quoted per finding. Count the
   findings the capped arm kept against the free-form arm's
   findings (recall reported against the free-form arm, per
   the register). Record separately whether any BLOCKING
   finding from the free-form arm is missing from the capped
   arm. Disputed BLOCKING findings (a BLOCKING finding in the
   free-form arm that may itself be wrong) go to the
   coordinator for adjudication before they count as dropped;
   the adjudication and its outcome are recorded.
6. Closing rails: remove test files; verify the desktop is
   clean (`hyprctl clients` plus grim screenshot, shared
   rails); write one row to `probes/ledger.jsonl` citing the
   pilot report; end the session.

### (d) Before/after measurements

- Findings recall, capped arm vs free-form arm, per artifact
  and in aggregate: capture from the two verdict sets, scored
  per step 5.
- "Dropped for length: N" count on every capped verdict:
  capture from the verdict text itself.
- BLOCKING findings: count missing from the capped arm per
  artifact; the cap never applies to BLOCKING findings, so
  any missing BLOCKING finding is recorded individually, with
  adjudication where disputed.
- Wall time and tokens per verdict, both arms: capture from
  the run record for each verdict; tokens per the shared
  rails (UNMEASURED if the harness gives no per-verdict
  figure, never estimated).
- No baseline recall figure exists in the register; the
  free-form arm IS the baseline.

### (e) Pass criteria

- PROVEN only if the controlled repeat ran with the pool held
  constant or arms swapped, at least three artifacts including
  one hard one, recall reported against the free-form arm by
  the third-reader scoring in step 5, blinding per (b), and
  every capped verdict carrying its dropped count.
- The pilot FAILS its own terms if any BLOCKING finding is
  dropped by the cap (after adjudication), or if any capped
  verdict lacks a dropped count.
- The pilot must report the measured recall figure and, where
  the brief stated a threshold, whether it was met; where no
  threshold was stated, it reports the figure with no
  held/not-held verdict and the coordinator decides.
- The claim stays UNPROVEN if the arms used different agents
  without swapping, if fewer than three artifacts were used,
  if recall was not measured, or if the blinding rule was
  broken.
- The adoption threshold is a coordinator decision, not part
  of this pilot.

### (f) Fail and rollback notes

- If a BLOCKING finding is dropped, stop the capped arm for
  that artifact, keep the free-form verdict as the record, and
  report the dropped finding by name.
- If recall cannot be scored (for example the free-form arm
  has no agreed finding list), stop and report the pilot as
  not run; do not substitute a judgement call for recall.
- If the blinding rule is broken (an agent saw the other arm's
  verdicts before writing), stop that arm, discard its
  verdicts, and re-run with the blinding fixed.
- Rollback: nothing is landed by this pilot; the template is
  not adopted on a failed or inconclusive pilot.

---
## M27: two-round re-review cap

### (a) Item, source, register verdict/conditions

M27, bottleneck register pilot-first list: two-round re-review
cap, AFTER the retro-count of blocking findings first raised in
round 3 or later across all chains in `improvements/`; if that
count is nonzero the cap becomes "round 3 requires a named
new-evidence reason". Section 3 downgrade (council 3,
unrefuted): "proven on historical data" to UNPROVEN as a
policy (one chain, selected because its tail was empty). The
C8 waste-versus-integrity question is assigned to the M25-M27
pilots (register section 3, unresolved).

### (b) Preconditions and setup on the real laptop

- Branch: own pilot branch off `integration-20261127`.
- Chain defined: one chain is one item's review set, the
  council review file(s) plus the redteam file(s) for that
  item in `improvements/` and its subdirectories, grouped by
  item name. Enumeration method: list files under
  `improvements/` matching `*council*` and `*redteam*`,
  group them by item, and record the list. The coordinator
  approves the enumerated list before any counting starts.
- Retro-count first: count blocking findings first raised in
  round 3 or later across all review chains in `improvements/`.
  The retro-count is verified by a second reader who did not
  do the count, or every counted finding is cited with file
  and finding id so it can be checked; the verification method
  is recorded before counting starts.
- Pilot window: stated in the pilot brief before the pilot
  starts (an end date, or a chain count); the pilot does not
  start without it.
- The cap text ("two-round re-review cap") and the fallback
  rule text ("round 3 requires a named new-evidence reason")
  must be written down before the pilot applies either.
- Owner Zen is untouched by this pilot (document review work).

### (c) Live test steps

1. Enumerate every review chain in `improvements/` per the
   definition in (b) and record the list in the pilot report.
   The coordinator approves the list before counting.
2. Retro-count: for each chain, count blocking findings first
   raised in round 3 or later. Record the count per chain and
   the total, with each finding named (file and finding id
   where the chain gives one). Record rounds consumed per
   historical chain as the before figure for step 6.
3. Branch on the count. If the count is zero, the pilot applies
   the two-round cap to the next review chains. If the count is
   nonzero, the pilot applies instead "round 3 requires a named
   new-evidence reason" to the next review chains. Record which
   branch was taken and why.
4. Apply the chosen rule to the next review chains that run
   during the pilot window. For each chain, record the rounds
   used, whether round 3 was requested, and, under the fallback
   rule, the named new-evidence reason for every round 3.
5. At the end of the pilot window, count blocking findings
   first raised in round 3 or later under the new rule, and
   count rounds consumed per chain versus the pre-pilot chains
   recorded in step 2.
6. Closing rails: remove test files; verify the desktop is
   clean (`hyprctl clients` plus grim screenshot, shared
   rails); write one row to `probes/ledger.jsonl` citing the
   pilot report; end the session.

### (d) Before/after measurements

- Retro-count (before): blocking findings first raised in
  round 3+ per chain and total, from the historical chains in
  `improvements/`. Capture: the per-chain count table in the
  pilot report.
- Rounds consumed per chain, before (historical chains, step 2)
  vs after (pilot-window chains, step 5): capture from the
  chain records.
- Round-3 requests under the pilot rule, with the named
  new-evidence reason for each (fallback branch only).
- Blocking findings first raised in round 3+ under the pilot
  rule: capture per chain.
- No baseline round counts exist in the register; the historical
  chains ARE the baseline and must be counted first, including
  rounds consumed per chain.

### (e) Pass criteria

- PROVEN only if the retro-count ran across all chains in
  `improvements/` per the approved list, the count branch was
  followed as written, and the pilot-window chains ran under
  the chosen rule with rounds and round-3 reasons recorded.
- If the retro-count is nonzero and the pilot still applied
  the plain two-round cap, the pilot is void.
- Under the fallback rule, any round 3 without a named
  new-evidence reason is a pilot violation, recorded as such.
- The register gives no numeric target for rounds saved; the
  pilot must report rounds consumed before vs after and state
  whether any blocking finding was lost to the cap. The
  adoption threshold is a coordinator decision.
- The claim stays UNPROVEN if the retro-count did not cover
  all chains, if the chain list was not approved before
  counting, or if no pilot-window chain ran under the rule.

### (f) Fail and rollback notes

- If the retro-count finds a nonzero count and the team wants
  the plain cap anyway, stop: the register condition forbids
  it. The fallback rule is the only path.
- If a blocking finding surfaces only in round 3 of a
  pilot-window chain under the plain cap, keep the finding,
  record it, and report the cap as having lost a finding.
- Rollback: the cap is a process rule, not code; rolling back
  means the next chains run uncapped, recorded in the pilot
  report.

---

## M28b: watchdog daily rollup

DORMANT PERMANENTLY: trigger (M28a refused) cannot fire, M28a
merged `877afe6d`; plan retained as record only, never to run.
M28a was approved by the coordinator and its code merged in
wave 1 (merge `58013edd`); the trigger "M28a refused" is now
permanently un-fireable, not merely dormant-for-now. The full
conditional plan is kept in the draft history for the record;
it must not run. Notes: the same-day escalation emergency path
under a daily rollup was never defined (a daily rollup by
definition delays late-day flags; no emergency path was
specified), and the dormant-trigger re-check gap is moot
because the trigger can no longer fire.

---

## M30: package reviews of small, homogeneous, low-tier items only

### (a) Item, source, register verdict/conditions

M30, bottleneck register pilot-first list: package reviews of
small, homogeneous, low-tier items only, findings per item
compared, AFTER M26's pilot. Sequencing: M26's pilot must
have reported before this pilot starts.

### (b) Preconditions and setup on the real laptop

- Branch: own pilot branch off `integration-20261127`.
- M26's pilot must have reported (pilot report filed, recall
  figure stated). If M26 has not reported, stop: this pilot
  is sequenced after it.
- Item set: small, homogeneous, low-tier items only. The exact
  items are UNVERIFIED from the sources read. The item set is
  drawn from `improvements/idea-queue-20261127.md` (47
  entries) or the register's Adopted lower-priority list, and
  the coordinator approves the item set before any review
  runs; the pilot runner's own justification alone is not
  enough. For each item the pilot states why it qualifies as
  small, homogeneous, and low-tier, before any review runs.
- Reviewers: different reviewers per arm, or a washout period
  with the item order shuffled between arms; record which.
  The same reviewers reviewing the same items twice with no
  blinding voids the comparison. Record the pool before
  running.
- Owner Zen is untouched by this pilot (review work).

### (c) Live test steps

1. Confirm M26's pilot has reported and cite the report. If
   not, stop.
2. Freeze the item list with the small/homogeneous/low-tier
   justification per item, the reviewer pool, and the
   blinding method (different reviewers per arm, or washout
   plus shuffled order) in the pilot report before any review
   runs.
3. Individual arm: review each item separately. Record findings
   per item, wall time and tokens per item.
4. Packaged arm: review the same items as one package. Record
   findings per item (attributed back to each item), wall time
   and tokens for the package.
5. Compare findings per item between the arms. Record every
   finding present in the individual arm and missing from the
   packaged arm, per item.
6. Closing rails: remove test files; verify the desktop is
   clean (`hyprctl clients` plus grim screenshot, shared
   rails); write one row to `probes/ledger.jsonl` citing the
   pilot report; end the session.

### (d) Before/after measurements

- Findings per item, individual arm vs packaged arm: capture
  from the two review sets, per item.
- Findings lost to packaging, per item: count of findings in
  the individual arm missing from the packaged arm.
- Wall time and tokens per item (individual arm) vs per package
  (packaged arm): capture from the run record. Per the M34f
  rule, price in wall time AND tokens; tokens per the shared
  rails (UNMEASURED if the harness gives no per-item figure,
  never estimated).
- No baseline findings counts exist in the register; the
  individual arm IS the baseline.

### (e) Pass criteria

- PROVEN only if M26's pilot had reported first, the items
  were small, homogeneous, and low-tier as justified before
  running and approved by the coordinator, the arms used
  different reviewers or a washout plus shuffled order, and
  findings per item were compared between arms.
- The pilot FAILS its own terms if any item reviewed was not
  small, homogeneous, or low-tier, or if findings were only
  compared at package level rather than per item.
- The register gives no numeric threshold for findings lost;
  the pilot must report the per-item lost-finding counts and
  state plainly whether packaging lost findings. The adoption
  threshold is a coordinator decision.
- The claim stays UNPROVEN if M26 had not reported, if
  findings per item were not compared, or if the blinding
  rule was broken.

### (f) Fail and rollback notes

- If an item turns out not to be small, homogeneous, or
  low-tier once review starts, pull it from the package, review
  it individually, and report it as excluded.
- If packaging loses a finding on any item, keep the individual
  review as the record for that item and report the lost
  finding by name.
- If the blinding rule is broken (the same reviewers saw the
  individual-arm findings before the packaged arm with no
  washout), stop that arm, discard its findings, and re-run
  with the blinding fixed.
- Rollback: nothing is landed by this pilot; packaged review
  is not adopted on a failed or inconclusive pilot.

---
## M31: guard-block snippet library only

### (a) Item, source, register verdict/conditions

M31, bottleneck register pilot-first list: guard-block snippet
library only (the generator is REJECTED; section 3: a wrong
generated brief looks authoritative and feeds blind scoring.
Only the manually pasted snippet library survives, to pilot).
Pilot: five briefs diffed against hand-written equivalents,
zero guard drift required.

### (b) Preconditions and setup on the real laptop

- Branch: own pilot branch off `integration-20261127`.
- The snippet library must exist as manually pasted snippets
  (no generator; the generator is rejected and must not be
  built as part of this pilot).
- Five briefs to write using the library, and their
  hand-written equivalents to diff against. The exact five
  briefs are UNVERIFIED from the sources read. The coordinator
  names the five briefs (subject and purpose each) in the
  pilot brief before running; the pilot does not start without
  them.
- The hand-written equivalents are drawn from existing briefs
  in `rung3-run-log/briefs/` written before the library
  existed, and the library-based versions are written by a
  different author. The same author writing both versions does
  not establish independence.
- Guard drift defined: any difference in a guard rule,
  threshold, condition, or required step. A wording-only
  difference is not guard drift; a changed threshold inside
  a guard block is.
- Guard-block extraction rule: stated in the pilot brief before
  diffing (heading name and boundaries, for example the text
  under the brief's guard heading through the next same-level
  heading). The extracted guard text is recorded verbatim in
  the pilot report so the diff is auditable.
- Owner Zen is untouched by this pilot (brief-writing work).

### (c) Live test steps

1. Freeze the five brief names and the hand-written equivalent
   for each, the extraction rule, and the two authors in the
   pilot report before writing the library-based versions.
2. Write the five briefs using the snippet library only.
   Record the snippets used per brief.
3. Extract the guard block of each library-based brief and of
   its hand-written equivalent per the rule in (b). Diff the
   two extracted blocks. Record the diff output for each of
   the five pairs.
4. For any diff found, classify it per the definition in (b)
   (guard drift or non-guard difference) and quote the guard
   text involved. A changed threshold, condition, or required
   step is guard drift.
5. Closing rails: remove test files; verify the desktop is
   clean (`hyprctl clients` plus grim screenshot, shared
   rails); write one row to `probes/ledger.jsonl` citing the
   pilot report; end the session.

### (d) Before/after measurements

- Guard-block diffs, five pairs: capture the diff output per
  pair. Required result: zero guard drift.
- Non-guard differences per pair: count and describe each;
  they do not count as guard drift but must be listed.
- Snippets used per brief: capture from the brief-writing
  record.
- No baseline drift figure exists in the register; the
  hand-written equivalents ARE the baseline.

### (e) Pass criteria

- PROVEN only if five briefs were diffed against hand-written
  equivalents (drawn from pre-library briefs, different
  author) and zero guard drift was found across all five.
- Any guard drift in any of the five pairs fails the pilot;
  the drift must be named and the snippet fixed or removed,
  and the pair re-diffed.
- The claim stays UNPROVEN if fewer than five briefs were
  diffed, if the hand-written equivalents were derived from
  the library or written by the same author as the
  library-based versions, or if any pair was not diffed.
- Adoption decision belongs to the coordinator after the pilot
  report.

### (f) Fail and rollback notes

- If a guard drift is found, stop using that snippet, revert
  the affected brief to its hand-written equivalent, and
  report the drift.
- If the library cannot produce a brief without hand-editing a
  guard block, record that as a library gap, not as a pass.
- Rollback: the library is not adopted; briefs stay
  hand-written. The rejected generator is never built as a
  fallback.

---

## M32: versioned run kit, tooling half only

### (a) Item, source, register verdict/conditions

M32, bottleneck register pilot-first list: versioned run kit,
tooling half only; the calibration bank persists ONLY if
re-validated per generation at clearly less than a fresh
calibration's cost. Context: M10's "calibration is cheap" is
DOCUMENTED, not measured (register section 3 downgrade), so no
calibration cost figure may be assumed by this pilot.

### (b) Preconditions and setup on the real laptop

- Branch: own pilot branch off `integration-20261127`.
- Scope is the tooling half only (the versioned run kit). The
  calibration bank is the item under test, not the tooling.
- Generation defined: one generation is one run's
  scorer-calibration cycle (run start through sign-off to the
  next run start). The coordinator confirms this definition
  in the pilot brief before any measurement; if the
  coordinator defines it differently, the pilot uses that
  definition and records it. The pilot does not start
  measuring without a confirmed definition.
- Fresh calibration procedure (verified on the branch): the
  M10 run-start procedure in `rung3-ci/spare-scorer.md`
  steps 1-5: name the spare, file the independence
  declaration, pre-calibrate sealed and blind (held-out set
  of 4 cases graded blind from snapshot plus frozen key
  section only, pass bar 4/4, at most one re-calibration on a
  second sealed set), independent verifier sign-off (4/4 and
  APPROVED), then record and run
  `python3 rung3-ci/check-spare-scorer.py <spare-record.json>`
  (exit 0 required).
- Re-validation procedure (verified on the branch): run
  `python3 rung3-ci/check-spare-scorer.py` over each bank
  record and verify the sign-off files still exist and carry
  4/4 and APPROVED. Any record that fails means the bank
  fails re-validation.
- Each cost is measured in wall time AND tokens (M34f rule);
  tokens per the shared rails.
- Fresh-calibration budget: the fresh calibration run consumes
  real scorer sessions and cap hours. The coordinator approves
  the run and states its budget (sessions and cap hours) in
  the pilot brief before step 2 runs.
- Owner Zen is untouched by this pilot (tooling and calibration
  work, no live driving unless a calibration run itself needs
  it; if it does, that step runs under a `cu.py` session with
  the pill visible and the owner Zen PID recorded before/after).

### (c) Live test steps

1. Freeze the generation definition (confirmed per (b)), the
   re-validation procedure, the fresh-calibration procedure,
   the "clearly less" threshold decision (see (e)), and the
   fresh-calibration budget in the pilot report before
   measuring either cost.
2. Measure a fresh calibration end to end on the laptop per
   the procedure in (b), within the approved budget. Record
   wall time and tokens, and the calibration result.
3. Build the versioned run kit tooling on the pilot branch.
4. At the next generation boundary (as defined in step 1),
   re-validate the calibration bank with the kit per (b).
   Record wall time and tokens, and whether the bank still
   validates.
5. Compare re-validation cost against fresh-calibration cost,
   both in wall time and in tokens.
6. Repeat steps 4-5 for a second generation if one falls
   inside the pilot window; if none does, record that only
   one generation was measured (see (e)).
7. Closing rails: remove test files; verify the desktop is
   clean (`hyprctl clients` plus grim screenshot, shared
   rails); write one row to `probes/ledger.jsonl` citing the
   pilot report; end the session.

### (d) Before/after measurements

- Fresh calibration cost: wall time and tokens, measured in
  step 2. No figure exists in the register; this measurement
  IS the baseline.
- Re-validation cost per generation: wall time and tokens,
  measured in step 4, per generation.
- Bank validity per generation: whether the bank still
  validates after re-validation (pass/fail per generation).
- Ratio re-validation cost to fresh calibration cost, in wall
  time and in tokens, per generation.

### (e) Pass criteria

- The bank persists ONLY if re-validation per generation costs
  clearly less than a fresh calibration, in both wall time and
  tokens. "Clearly less" needs a numeric threshold: the pilot
  brief states it (a ratio or percentage, in both wall time
  and tokens) before measuring, or the pilot reports both
  numbers and the ratio with no pass/fail judgement and the
  coordinator decides. Either way the choice is recorded
  before measuring.
- At least two generations measured, or a single-generation
  result is INCONCLUSIVE for persistence (not a pass).
- The pilot FAILS its own terms if the bank fails
  re-validation in any measured generation, or if either cost
  was not measured.
- The claim stays UNPROVEN if no generation boundary was
  reached during the pilot (no re-validation measured), or if
  the fresh-calibration cost was assumed rather than measured.
- The adoption threshold ("clearly less") is a coordinator
  decision after the pilot report.

### (f) Fail and rollback notes

- If the bank fails re-validation, do not persist it; run a
  fresh calibration and record the bank as not carried over.
- If re-validation costs as much as, or more than, a fresh
  calibration, report the numbers; the bank does not persist
  and the kit's re-validation path is not adopted.
- If the fresh calibration exceeds its approved budget, stop
  and report it; do not spend further scorer sessions to
  finish the measurement.
- Rollback: the versioned run kit tooling is not landed; the
  existing calibration practice continues unchanged.

---

## M33: branch hygiene

### (a) Item, source, register verdict/conditions

M33, bottleneck register pilot-first list: branch hygiene,
sequenced STRICTLY after M28a lands the watchdog record
somewhere durable; verdict branches excluded permanently;
dry-run list reviewed first. Section 3 sequencing hazard:
M33 before M28a lands the watchdog record would delete the
only complete copy of that record. M28a code MERGED
(`877afe6d`, wave 1, merge `58013edd`): script
`scripts/watchdog_append.py` plus
`docs/watchdog-rolling-branch.md`, one rolling branch per lane
(`watchdog/<lane>`), fast-forward pushes only. Lane
switch-over is still a coordinator decision (integration
report queue row 23), and no `watchdog/*` branch exists on
origin yet (verified by `git ls-remote` at fix time), so no
durable record location exists yet. This pilot is still
BLOCKED; the reason is now "merged but not switched over",
not "not landed".

### (b) Preconditions and setup on the real laptop

- Branch: own pilot branch off `integration-20261127`,
  created only after the precondition is met.
- Precondition (gating): M28a has landed the watchdog record
  somewhere durable. The pilot runner must cite the landing
  (the `watchdog/<lane>` branch name and the durable
  location) before any other step. As of this fix M28a has
  merged but no rolling branch exists; the pilot does not
  start.
- Verdict branches are excluded permanently. Identification
  method (verified on the branch at fix time): `git branch -a`
  entries matching `(^|/)verdict-.*-L3$` (63 such branches at
  fix time across remotes clone1, clone2, fresh, fresh1,
  fresh2, mochi; zero local). The pilot enumerates them with
  that command and records the list before producing the
  dry-run list.
- Protected sets (excluded from deletion alongside verdict
  branches, before the dry-run list is produced): the
  watchdog rolling branches (`watchdog/<lane>`, per
  `docs/watchdog-rolling-branch.md`), any branch holding the
  only complete copy of a record, and active work branches
  named by the coordinator.
- Deletion-list selection rule: branches fully merged into
  `todolist-push` (`git branch -a --merged origin/todolist-push`),
  excluding the protected sets above.
  No branch is proposed for deletion on runner judgement
  alone.
- Tip SHA record home: the pilot report file
  (`improvements/m33-pilot-20261127.md`), committed and pushed
  to `integration-20261127` before any deletion, and read back
  before deletion. The SHA record must never live on the pilot
  branch or any branch the pilot may delete.
- The dry-run list must be reviewed first (reviewer named in
  the pilot brief before the dry-run list is produced; the
  register does not name the reviewer). No deletion happens
  before the review is recorded as approved.
- Owner Zen is untouched by this pilot (git hygiene).

### (c) Live test steps

1. PRECONDITION CHECK (gating step, runs first and alone):
   confirm M28a has landed the watchdog record somewhere
   durable, with the landing cited (the `watchdog/<lane>`
   branch name). If no rolling branch exists, STOP: this pilot
   is blocked and does not run. Record the check outcome even
   when it stops the pilot.
2. Only if step 1 passes: verify the watchdog record is
   complete at its durable location. Compare the rolling
   branch's entries against the live watchdog log (the
   per-flag PR stream), entry by entry; the branch under
   consideration for deletion is never the comparison source.
   Record the verification.
3. List the verdict branches by name per the method in (b) and
   mark them permanently excluded. List the protected sets
   (watchdog rolling branches, only-copy branches, active
   work branches) by name as well.
4. Produce the dry-run deletion list per the selection rule in
   (b): every other branch proposed for deletion, with its tip
   SHA recorded per branch in the pilot report file.
5. Commit and push the pilot report file (with the SHA record)
   to `integration-20261127`; read the SHA record back and
   confirm it matches. The dry-run list is reviewed (reviewer
   named in (b)). No deletion happens before the review is
   recorded as approved.
6. Only after review approval: delete the listed branches.
   Record each deletion with its tip SHA.
7. After deletion, verify the watchdog record is still complete
   at its durable location (re-run the step 2 comparison
   against the live watchdog log), and verify no verdict branch
   and no watchdog rolling branch was deleted (re-run the
   `git branch -a` listings).
8. Closing rails: remove test files; verify the desktop is
   clean (`hyprctl clients` plus grim screenshot, shared
   rails); write one row to `probes/ledger.jsonl` citing the
   pilot report; end the session.

### (d) Before/after measurements

- Branch count before vs after, by category (verdict branches
  kept, watchdog-record branches kept, deleted): capture from
  `git branch -a` listings before and after, saved with the
  pilot report.
- Tip SHAs recorded per deleted branch (step 4): capture in
  the dry-run list in the pilot report file.
- Watchdog record completeness before vs after: the same
  verification as step 2, run again in step 7, with the
  result recorded.
- Verdict branches deleted: must be zero; watchdog rolling
  branches deleted: must be zero; capture from the
  post-deletion branch listing.
- No baseline branch counts exist in the register; the
  pre-deletion listing IS the baseline.

### (e) Pass criteria

- PROVEN only if M28a had landed the watchdog record durably
  first, the dry-run list was reviewed and approved before any
  deletion, zero verdict branches and zero watchdog rolling
  branches were deleted, and the watchdog record verified
  complete after deletion.
- The pilot FAILS its own terms if any verdict branch or any
  watchdog rolling branch was deleted, if any deletion
  happened before review approval, or if the watchdog record
  is incomplete after deletion.
- The claim stays UNPROVEN if the precondition check did not
  run, or if the post-deletion verification was skipped.
- The adoption threshold is not applicable here: this is a
  one-off hygiene operation, and its completion is the
  recorded branch state before vs after.

### (f) Fail and rollback notes

- If the precondition check fails, the plan stops with no work
  done and no rollback needed; record the check.
- If the post-deletion verification shows the watchdog record
  incomplete, stop and report it immediately; restore from the
  recorded tip SHAs (step 4, in the pilot report file on
  `integration-20261127`) any branch whose deletion caused
  the loss, starting with the watchdog-record branches.
- If a verdict branch or a watchdog rolling branch is deleted
  by mistake, restore it from its recorded tip SHA at once and
  report the error by branch name; the deletion list process
  is then re-reviewed before any further deletion.
- Rollback in general: every deleted branch is restorable from
  its recorded tip SHA while the SHA remains reachable; the
  pilot must not delete the SHA record itself (it lives on
  `integration-20261127`, not on any deletable branch).

---

Plans written: 8 full test plans (M19, M21, M26, M27, M30, M31,
M32, M33). M28b is a one-line permanent-dormant entry above,
not a full plan.

Already integrated on `integration-20261127` (tip `5365c84c`,
verified 2026-11-27 13:39 UTC): none of the 9 slice C items.
M28a merged (`877afe6d`) but is not a slice C item; its merge
changes M28b (permanently dormant) and M33 (still blocked,
reason now "merged but not switched over").

---

## Slice D: M34a-e + I pilots (I2, I4, I6, I12, I14, I18, I23)

## Sources

- Integration report: origin/integration-20261127:improvements/integration-phase-20261127.md
  (519 lines at tip 5365c84c). Pilots list names M34a-e and I2, I4, I6, I12,
  I14, I18, I23, all PILOT-FIRST, UNPROVEN until they report. Live-test
  record format model: the per-item records for items 1, 6, 9, 10, 12-15.
- Bottleneck register: origin/todolist-push:improvements/bottleneck-study-20261127.md,
  section 2 lines 192-412 (pilot-first full list 349-412, M34a-e at the end).
- Agent-desktop comparison: origin/todolist-push:improvements/agent-desktop-comparison-20261127.md,
  idea table section 2 lines 104-144, do-first section 3 lines 145-178,
  rejected section 4 lines 179-255, sections 5-7 for U3 and the I18 finding.

## Verification against the integration branch

Branch tip checked before fixing: origin/integration-20261127 at 5365c84c
("Merge int-rt-a11y (opencode laptop CLI) into integration-20261127"),
checked 2026-11-27 20:39 +07. Log grep for M34a-e, I2, I4, I6, I12, I14,
I18, I23 found no implementation commit for any of the 12 items (only
4b70b71c, the queue commit that lists them). The integration report's queue
table also lists all 12 as PILOT, not IMPLEMENTED. None of the 12 is already
integrated. Full plans follow for all 12.

Note: the tip moved since the draft (1314b088) and since the reviews
(67d9ce2c). The int-rt-a11y merge (6b943977) shifted scripts/a11y.py line
numbers again; every line citation below was re-verified against tip
5365c84c, not copied from the reviews.

## Proof law (binds every plan)

A claim counts as PROVEN only if it was run for real on the laptop with
measured before/after numbers. Anything else is UNPROVEN. PROVEN in this
file always means laptop-PROVEN; a figure measured on the register machine
is written as "measured on the register machine (not laptop-PROVEN)", never
as PROVEN. A pilot that returns "no win available" is a valid result and
closes the pilot; it is not a failure of the pilot. Numbers, commands, file
paths and baseline figures come from the sources above, from the branch
itself where stated, or are marked UNVERIFIED with what would establish
them. Nothing here is invented. A value marked DRAFTER RULE is a rule this
draft adds (not a register condition); the pilot brief confirms or replaces
it before the first run.

## Common live-test rules (from the integration report's live records)

- Run under a cu.py session started with a driver command so the pill shows;
  the pill stays visible for the whole run. (Item 1 run 1 had no pill because
  `cu.py session` without a driver command errored; record any pill gap
  honestly instead of hiding it.)
- Record the owner Zen PID before and after with this command:
  `pgrep -af zen-bin`, then identify the owner Zen by the --profile
  argument in its cmdline, which must match the owner profile dir recorded
  in the machine layer. A throwaway-profile Zen has a different --profile
  path and is not the owner Zen. Record the PID and the full cmdline; never
  assume the PID (807599 was the PID on 2026-11-27; PIDs change on restart).
- Owner Zen untouched unless the plan says otherwise. RDP port 6021 is the
  observed value from the 2026-11-27 live records; re-verify at run time.
  Marionette throwaway-profile port 2829 (MOZ_REMOTE_ALLOW_SYSTEM_ACCESS=1)
  is the value from the 2026-11-27 live records; re-verify at run time.
- Every plan ends with: one row in probes/ledger.jsonl citing the outputs,
  a grim screenshot of the desktop after release, the owner Zen PID
  re-verified, test files removed, test instances killed by recorded PID
  after a cmdline check, the session ended, and the desktop verified clean.
  Desktop clean is checked by `hyprctl clients` output (recorded) plus the
  grim screenshot; clean means only owner windows remain, no test windows,
  no test processes.
- Ledger row fields, per probes/README.md: `date` (YYYY-MM-DD), `probe`
  (path or short name), `question`, `result` (the measured numbers or the
  observed behavior), `output` (citation: a repo path holding the output,
  or the output inline when short), `verdict` (what was decided from it).
  Validate the ledger with `python3 probes/validate-ledger.py` after
  adding the row; the validator must print LEDGER OK. Example row:
  `{"date": "2026-11-27", "probe": "improvements/M34a-pilot-record-20261127.md", "question": "does the harness expose prompt-cache controls", "result": "NOT EXPOSED", "output": "improvements/M34a-pilot-record-20261127.md", "verdict": "pilot closes as a negative result"}`.
- Pilot report path (shared pattern, per plan): the pilot report is
  `improvements/<item-id>-pilot-record-20261127.md` on branch
  integration-20261127, created by the pilot; the brief records the exact
  path before the first run. Results also go in the integration report
  per-item record format. Public aggregates go in docs/benchmarks/.
- Suite runs use `python3 rung3-ci/test-discover.py` (serial is the gate of
  record; scope with its flags). The per-test runner, hermetic diff gate,
  and sharded runner live in that file per the M17 record.
- Safe-target rule (binds I2, I4, I6, M34b): a baseline act runs only on a
  safe target (a throwaway app, a fixture window, or an app in a
  known-safe state) and only with an act set pre-approved as
  non-destructive. The brief lists, per act, the expected target and the
  worst-case effect of landing on the wrong element; any act whose worst
  case is destructive (delete, send, close without saving, or equivalent)
  is forbidden. Where possible the baseline runs on a scratch copy or
  scratch state of the target.
- Pre-run decisions: where a plan says the pilot brief names a value
  before the first run, the pilot is BLOCKED until that value is recorded
  in the pilot report. The coordinator owns the brief and names the values;
  the runner does not invent them mid-run.
- No scoring anywhere in any pilot.

---

## 1. M34a prompt caching, measurement only

### (a) Item, source, register verdict/conditions

Bottleneck register M34a, PILOT-FIRST: "prompt caching, measurement only,
starting with whether the harness exposes cache controls at all."
Integration report pilots list includes M34a-e. UNPROVEN until it reports.

### (b) Preconditions and setup on the real laptop

- Branch: integration-20261127 checkout at the tip recorded at run time.
  No code changes before the inspection.
- The inspection target is the agent harness that runs lane work. Brief
  decisions required before the first run (pilot BLOCKED until all three
  are recorded in the pilot report): (1) the exact harness/config surface
  to inspect (config file path or documentation URL); (2) one fixed prompt
  and the model to run it with; (3) the capture meter or command that
  yields time-to-first-token and tokens billed. The coordinator names all
  three in the brief. The harness surface is UNVERIFIED in the sources;
  do not guess it here.

### (c) Live test steps

1. Record the integration-branch tip, the owner Zen PID (see common rules),
   and the three brief decisions. Start a cu.py session; confirm the pill
   is visible.
2. Inspect the named harness surface for prompt-cache controls. List every
   cache control exposed (flag, config key, or API parameter) and record
   where each is documented (file path or URL), or record NOT EXPOSED.
3. If no control is exposed: stop, record the negative result, close the
   pilot. No measurement is possible.
4. If a control is exposed and the named meter exists: run the fixed prompt
   with caching off. Record time-to-first-token and tokens billed from the
   named meter.
5. Run the same prompt with caching on, same meter, same model.
6. Repeat each arm at least 3 times (DRAFTER RULE: minimum N=3; N=1 is
   forbidden, a single sample per arm is noise, not a measurement). Record
   the N used.
7. If no meter exists that yields time-to-first-token or tokens billed:
   stop and record INCONCLUSIVE for that metric. Never estimate a meter
   reading. Time-to-first-token may still be measured by wall clock with
   time.monotonic() around the call, recorded as such.
8. Record every run in probes/ledger.jsonl; save a grim screenshot; verify
   the owner Zen PID is unchanged; remove test files; verify the desktop
   is clean; end the session.

### (d) Before/after measurements

- Cache-controls-exposed (yes/no plus the list); time-to-first-token per
  arm in seconds (median of at least 3 runs); tokens billed per arm
  (median of at least 3 runs, from the named meter only).
- Baseline: none exists in the sources (UNVERIFIED). The external vendor
  table (100K-token prompt, time-to-first-token 11.5 s to 2.4 s, claude.com,
  cited in the register's sources) is an external figure only and must NOT
  be reported as this project's baseline or expected saving.

### (e) Pass criteria

- The pilot reports the exposure answer with evidence. If controls exist,
  it reports measured before/after time-to-first-token and tokens on the
  laptop, each from at least 3 runs. PROVEN only if run for real on the
  laptop with measured before/after numbers; otherwise UNPROVEN. If no
  controls are exposed, the pilot closes as a printed negative result (the
  measurement question is answered: not measurable here). If no meter
  exists, the affected metric stays UNPROVEN (INCONCLUSIVE), never
  estimated.

### (f) Fail and rollback notes

- If the inspection cannot determine whether controls are exposed, record
  INCONCLUSIVE and claim neither way. No code or config changes are made
  by this pilot, so there is nothing to roll back; if a cache flag was
  toggled for the measurement arm, restore the prior setting and record
  the restore.

## 2. M34b viewport-limited accessibility trees, navigation hints only

### (a) Item, source, register verdict/conditions

Bottleneck register M34b, PILOT-FIRST: "viewport-limited accessibility
trees for navigation hints only, never grading, verification or
final-state reads." Integration report pilots list includes M34b.
UNPROVEN until it reports.

### (b) Preconditions and setup on the real laptop

- Branch: integration-20261127 checkout at the tip recorded at run time.
- scripts/a11y.py observe() caps at 500 nodes / 2 s; the cap loop is at
  a11y.py:107 on branch integration-20261127
  (`while pending and visited<500 and time.monotonic()-start<2:`).
  The I5 accounting half is already implemented (children_count, cut
  flags, complete flag), so the measurement hooks exist.
- The pilot brief names the AT-SPI app before running, by this selection
  rule: the app must be AT-SPI-registered (confirmed by one observe
  returning elements for its PID), must have a tree deep or wide enough
  to exercise the viewport limit, and must be in a safe state where
  navigation acts are non-destructive. Prior live tests used an AT-SPI app
  pid 1072896 'Unnamed' and quickshell; Zen is not AT-SPI-registered, so
  Zen is not the target. The brief records the app, its launch method, and
  how registration is confirmed. Pilot BLOCKED until the app is named.
- Variant build spec (the experiment, not a landed change): in
  scripts/a11y.py observe(), behind a flag, filter the collected items to
  those whose extents intersect the active window's viewport rect, using
  the extents the observe already collects. Items with no extents are
  counted as "no extents" and excluded from the variant tree, with the
  count recorded. The viewport source (the app root window rect) is
  confirmed by the brief before building. cu.py session with the pill
  visible.

### (c) Live test steps

1. Record the integration-branch tip, the owner Zen PID (see common rules),
   the named app, and the navigation task (step 4) with its target element
   (named in the brief before step 4; the element must be visible in the
   full tree and inside the viewport). Start a cu.py session; confirm the
   pill is visible.
2. Baseline: observe the named app with the current full observe. Record
   node count, wall time in ms, and snapshot byte size.
3. Build the viewport-limited variant per the spec in (b), in a scratch
   copy or behind a flag. Record where the variant lives.
4. Observe the same app in the same window state with the variant. Record
   the same three metrics.
5. Use the variant tree for navigation hints only: drive the navigation
   task (move to the named element by hint) and record success or failure
   per attempt. Success means the named element is the focused or selected
   element after the act. The navigation act set is non-destructive per
   the safe-target rule in the common rules; the brief lists the worst-case
   effect per act.
6. Verify the restriction holds mechanically: the variant lives behind a
   flag that only the navigation path sets. Grep the pilot branch for the
   flag's uses and record the output; the grading, verification, and
   final-state-read paths must not reference the flag. A runner's say-so
   is not evidence.
7. Repeat the baseline/variant pair on a second app named in the brief by
   the same selection rule as (b); the second app must differ in toolkit
   class from the first.
8. Record in probes/ledger.jsonl; save a grim screenshot; verify the owner
   Zen PID is unchanged; remove test files and the scratch variant; verify
   the desktop is clean; end the session.

### (d) Before/after measurements

- Node count, observe wall time in ms, snapshot bytes, navigation-hint
  success per attempt, "no extents" item count in the variant arm.
- Baseline: the current full observe on the named app, measured in step 2
  (no baseline numbers exist in the sources, UNVERIFIED). The external
  accessibility-tree-vs-screenshot token-cost measurement (dev.to, cited
  in the register's sources) is external only, not this project's baseline.

### (e) Pass criteria

- Measured before/after node count, wall time and bytes on the laptop;
  navigation hints work from the limited tree; the mechanical flag-use
  check shows zero grading, verification, or final-state reads used the
  limited tree. PROVEN only with real laptop before/after numbers;
  otherwise UNPROVEN. A "no win available" result (limited tree not
  cheaper, or hints unusable) is a valid pilot outcome and closes the
  pilot.

### (f) Fail and rollback notes

- If the variant tree misses elements needed for navigation, record the
  miss rate and stop; do not widen the tree silently. The variant is not
  landed; remove the scratch copy or flag after the pilot. Owner Zen
  untouched (Zen is not AT-SPI-registered; use the named AT-SPI app).

## 3. M34c DOM snapshot cache, mutation-detection gate first

### (a) Item, source, register verdict/conditions

Bottleneck register M34c, PILOT-FIRST: "DOM snapshot cache, only after a
mutation-detection test with zero tolerated misses." Integration report
pilots list includes M34c. UNPROVEN until it reports.

### (b) Preconditions and setup on the real laptop

- Branch: integration-20261127 checkout at the tip recorded at run time.
- DOM lane to cache: scripts/zen_dom.py (the DOM lane; main() at line 1710,
  subcommands list, tab, eval, locate, kill-hung on branch
  integration-20261127). The read whose wall time is measured is
  `python3 scripts/zen_dom.py eval <expr>` (the DOM read path); the exact
  eval expression is stated in the brief before timing (it reads the
  fixture page's DOM state).
- A mutation-detection test does NOT exist in the sources (UNVERIFIED);
  the pilot builds it first. No cache is enabled before the detection test
  passes.
- The mutation list is set by a second reader, not the detector author (see
  (c) step 1). The detector is a scratch script created by the pilot at a
  recorded path, following the probes/ naming rule (YYYYMMDD-<slug>.py);
  it is not landed. The fixture page is a local HTML file at a recorded
  scratch path, served by `python3 -m http.server <port>` from the
  scratch dir.

### (c) Live test steps

1. Record the integration-branch tip, the owner Zen PID (see common rules),
   the fixture path, and the detector path. Start a cu.py session; confirm
   the pill is visible.
2. Build the mutation-detection test: the fixture page mutates in a stated
   set of ways. The mutation list is set by a second reader (not the
   detector author) before the detector is built, and must include at
   least one adversarial mutation kind the detector was not designed for
   (a kind outside the natural set of node added, node removed, attribute
   changed, text changed). Record the list and who set it.
3. Run the detector over the fixture. Record misses (mutations the detector
   did not flag) and which source each detection used (fresh observe).
4. Require zero misses. Any miss fails the gate and the cache is NOT built:
   record the miss and stop, or fix the detector and re-run the full test.
   A miss on any unlisted-but-real mutation kind found during the pilot
   also fails the gate.
5. Only after zero misses: enable the snapshot cache on scripts/zen_dom.py.
   Measure eval wall time with the cache cold vs warm on the same page.
6. Re-run the detection test with the cache enabled, with the detector
   reading FRESH state (cache bypass for the detector, so a stale read is
   visible to it). Record which source each detection used (fresh vs
   cached). Confirm zero misses again. A detector that reads the cached
   snapshot cannot see mutations, so a cached-source detection run proves
   nothing and does not count.
7. Stale-read check: after each cached read, perform a fresh observe of the
   same page and compare; any difference is a stale read and counts as a
   miss.
8. Record in probes/ledger.jsonl; save a grim screenshot; verify the owner
   Zen PID is unchanged; remove test files and the scratch detector;
   verify the desktop is clean; end the session.

### (d) Before/after measurements

- Mutation-detection misses (must be 0), with the source (fresh vs cached)
  recorded per detection; eval wall time cache-cold vs cache-warm in ms;
  stale-read count (must be 0; any read served from a stale snapshot
  counts as a miss).
- Baseline: no cache exists; cold timings are the baseline, measured in
  step 5 (UNVERIFIED in the sources).

### (e) Pass criteria

- The detection test reports zero misses before the cache is enabled AND
  zero misses with it enabled, where the enabled run read fresh state and
  the mutation list was set by a second reader including an adversarial
  kind. Both requirements are pass conditions, not notes. Measured cold
  and warm wall times are recorded on the laptop. PROVEN only with real
  laptop numbers; otherwise UNPROVEN. One tolerated miss is a fail, not a
  pass; zero tolerated misses is the stated condition.

### (f) Fail and rollback notes

- Any miss kills the cache. Disable it, remove the cache code or flag,
  record the miss. A stale read served to any consumer is a fail: stop
  the pilot, restore uncached reads, record the incident.

## 4. M34d sparse checkout timing pilot, minutes only

### (a) Item, source, register verdict/conditions

Bottleneck register M34d, PILOT-FIRST: "sparse checkout timing pilot on
this repo (minutes; the external ratio is banned from reporting)."
Section 3 dissent: council 1 would reject outright. External source:
GitHub sparse-checkout blog on GitHub's test repository (ratio recorded,
banned as an expectation for this repo). Integration report pilots list
includes M34d. UNPROVEN until it reports.

### (b) Preconditions and setup on the real laptop

- Branch: integration-20261127 checkout on the laptop (the pilot measures
  on the laptop). Clone URL, verified from the repo remote:
  https://github.com/phamTuan207/computer-use-wayland.git (this URL is
  from the repo itself, not the three named sources).
- Clone branch: integration-20261127 at the tip recorded at run time, for
  both arms, so the comparison is on the same commit.
- Sparse profile (stated here, frozen after the first timing): the paths
  the test-discover lane reads, namely scripts/, rung3-ci/, tests/, plus
  the repo root files the discover runner needs. The brief confirms the
  exact path list before the first timing and records it in the pilot
  report; the profile must not change after the first timing. A profile of
  only a trivial subset (for example only a README) is forbidden: the
  profile must be a stated, realistic lane need, and the lane is the
  test-discover lane.
- A clean scratch directory for the timed clones; the runner picks the
  path and records it. `git` available. No changes to the real worktree.

### (c) Live test steps

1. Record the integration-branch tip and the owner Zen PID (see common
   rules). Start a cu.py session; confirm the pill is visible.
2. Disk-space check first: run `df` on the scratch filesystem and record
   available space. Available space must exceed twice the step 3 full-clone
   size before the second clone starts; if it does not, stop and record
   INCONCLUSIVE.
3. Time a full clone of the repo at the recorded tip into a scratch dir
   (wall minutes, `time git clone --branch integration-20261127 <url>
   <dir>`). Record the exact command and the resulting checkout size.
4. Time a sparse checkout of the same repo at the same tip into a second
   scratch dir, using the profile from (b). Record the exact commands.
5. Verify the sparse checkout contains exactly the profiled paths
   (`git sparse-checkout list` output must match the brief's profile) and
   that the smoke command works: `git status` exits 0 AND every profiled
   path exists.
6. Repeat each arm twice more (three runs per arm total). Run both arms
   back-to-back in the same session so network conditions are shared;
   record the run order and times. If a local mirror of the same commit
   exists, record one local-mirror clone time as the network-free control.
7. Record minutes per arm plus checkout sizes in probes/ledger.jsonl; save
   a grim screenshot; verify the owner Zen PID is unchanged; delete both
   scratch dirs; verify the desktop is clean; end the session.

### (d) Before/after measurements

- Full-clone wall minutes plus size (3 runs); sparse-checkout wall minutes
  plus size (3 runs); local-mirror control minutes if a mirror exists.
- Baseline: UNVERIFIED (no clone timing in the sources). The external
  GitHub test-repo ratio is BANNED from reporting; report minutes only.

### (e) Pass criteria

- Both arms timed on the laptop (3 runs each), minutes reported, sparse
  profile recorded and frozen after the first timing. PROVEN only with
  real laptop minutes; otherwise UNPROVEN. The pilot reports minutes; it
  does not claim a ratio or a saving. Council 1's reject-outright dissent
  is recorded; the pilot runs per the register's PILOT-FIRST verdict.

### (f) Fail and rollback notes

- If the sparse checkout is missing paths a lane needs, record which paths
  and stop; do not silently widen the profile mid-run. Delete both scratch
  dirs after the pilot; the real worktree is untouched.

## 5. M34e CI batching, measurement only

### (a) Item, source, register verdict/conditions

Bottleneck register M34e, PILOT-FIRST: "CI batching, measurement only; if
the project's own cancelled-run share is small it closes as a printed
negative result." Integration report pilots list includes M34e. UNPROVEN
until it reports.

### (b) Preconditions and setup on the real laptop

- Branch: integration-20261127 checkout at the tip recorded at run time.
- GitHub Actions workflows exist on the repo (.github/workflows/
  rung3-checks.yml, secret-scan.yml, secret-scan-history.yml, verified in
  the tree on branch integration-20261127). No workflow changes.
- Capture command: `gh run list` (with --json for conclusion, headBranch,
  createdAt). gh CLI access to the repo's Actions history is UNVERIFIED on
  the laptop until the pilot checks it; if `gh run list` fails on the
  laptop, record INCONCLUSIVE and do not estimate the share.
- Measurement window (fixed here): the last 30 days ending on the pilot
  start date; minimum 50 runs. If fewer than 50 runs fall in 30 days,
  extend backwards until 50 runs or 90 days, whichever comes first. The
  window is frozen before listing and recorded in the pilot report; it
  must not change after the data is seen.

### (c) Live test steps

1. Record the integration-branch tip, the owner Zen PID (see common rules),
   and the window. Start a cu.py session; confirm the pill is visible.
2. List runs in the window with their conclusions (completed, cancelled,
   failed). Count cancelled vs total. If the window holds fewer than 50
   runs, extend it per (b) before counting.
3. For cancelled runs, record the cause by this rule: a cancelled run is
   batching-relevant (superseded) if a newer completed run exists for the
   same workflow and branch within the window after it; otherwise record
   UNKNOWN. `gh run list` exposes no cancellation-cause field, so the
   cause is inferred by this stated rule, not read from a field.
4. Compute the cancelled-run share (cancelled divided by total) for the
   window, and the batching-relevant share (superseded divided by total).
   Count UNKNOWN-cause cancellations separately.
5. If UNKNOWN exceeds 25 percent of cancelled runs (DRAFTER RULE), report
   the batching-relevant share as a range, not a point figure: lower bound
   the confirmed-superseded share, upper bound the confirmed-superseded
   plus UNKNOWN share.
6. Record the window, counts, and share in probes/ledger.jsonl; save a
   grim screenshot; verify the owner Zen PID is unchanged; remove test
   files; verify the desktop is clean; end the session.

### (d) Before/after measurements

- There is no before/after change (measurement only). Metrics are total
  runs, cancelled runs, cancelled-run share, batching-relevant share, and
  the UNKNOWN count. Baseline: UNVERIFIED (no share in the sources).

### (e) Pass criteria

- The share is measured on the project's own runs and reported with the
  window and counts. If the share is small, the pilot closes as a printed
  negative result (per the register). PROVEN only with real measured
  counts; otherwise UNPROVEN. The pilot implements no batching.

### (f) Fail and rollback notes

- If the Actions history is unavailable (no gh access, no permission),
  record INCONCLUSIVE and do not estimate the share. No workflow files
  are changed, so there is nothing to roll back.

## 6. I2 a11y identity probe, refusal budget named first

### (a) Item, source, register verdict/conditions

Agent-desktop I2, PILOT-FIRST, W4 D4: "Strict ref re-identification,
a11y-only scope." Binding conditions: full RefStore version REJECTED
(complete-read proof fails on dense apps inside the 500-node / 2 s caps,
and more refusals push agents to coordinates). Pilot scope is a11y-only.
No benefit claim until the pilot measures it. (R2) The pilot must be
specified before it runs: named apps including a dense one, a pre-stated
refusal budget, and per-act cost measurement; a pilot that cannot fail is
not an experiment. Integration report pilots list: "I2 (a11y identity
probe, refusal budget named first)". Unresolved U3: the refusal-rate
budget is unnamed (no one has named a number); the pilot design must name
X before it runs.

### (b) Preconditions and setup on the real laptop

- Branch: integration-20261127 checkout at the tip recorded at run time.
- I8 probes/ plus ledger exist (do-first sequencing: I8 lands before the
  I2 and I10 pilots). scripts/a11y.py observe() caps at 500 nodes / 2 s;
  the cap loop is at a11y.py:107 on branch integration-20261127. I3
  snapshot-qualified refs are implemented and live-tested, so the probe
  builds on qualified refs.
- The pilot brief names the apps before running, by this selection rule:
  one GTK, one Qt, one Electron class app plus one dense app; each app
  must be AT-SPI-registered, launchable on the laptop, and in a safe state
  where the act set is non-destructive. The dense app is confirmed dense
  by one observe (node count recorded, near the 500-node cap). The brief
  records each app, its launch method, and how registration is confirmed.
- The brief names the refusal budget X (a coordinator decision, recorded
  in the brief before the first run; X is UNVERIFIED in the sources). The
  pilot is BLOCKED until X is named.
- The brief lists the act set per act, with the expected target and the
  worst-case effect of landing on the wrong element, per the safe-target
  rule in the common rules. Any act whose worst case is destructive is
  forbidden. The baseline runs on a safe target (throwaway app, fixture
  window, or an app in a known-safe state); where possible it runs on a
  scratch copy or scratch state. Pilot BLOCKED until the act set is
  recorded.
- Probe enable mechanism (built as part of this pilot): a flag-gated step
  in scripts/a11y.py, strict re-identification before dispatch: re-resolve
  the ref against a fresh observation and refuse to act if it does not
  resolve to the same element. Per-act cost capture: the probe logs
  observe wall time plus re-identification wall time per act, with
  time.monotonic() timestamps in the pilot log; the instrumentation is
  part of the probe build. cu.py session with the pill visible.

### (c) Live test steps

1. Record the integration-branch tip, the owner Zen PID (see common rules),
   the four named apps, the budget X, and the act set. Start a cu.py
   session; confirm the pill is visible.
2. Mis-click baseline first: on each named app, run the stated act set
   using current refs. Record mis-clicks (an act lands on the wrong
   element) per act. Only safe acts on safe targets, per (b).
3. Enable the identity-stability probe (strict re-identification on the
   a11y lane only, per the mechanism in (b)). Run the same act set.
   Record refusals (the probe refuses to act) per act and mis-clicks per
   act.
4. Record per-act cost (observe plus re-identification wall time, ms) in
   both arms, from the probe log.
5. Compare the refusal rate against the pre-stated budget X.
6. Record in probes/ledger.jsonl plus the integration report per-item
   record; save a grim screenshot; verify the owner Zen PID is unchanged;
   remove test files and disable the probe; verify the desktop is clean;
   end the session.

### (d) Before/after measurements

- Mis-click baseline (mis-clicks per act, per app); refusal rate with the
  probe (refusals per act, per app); per-act cost in ms in both arms.
- Baseline: no mis-click baseline exists in the sources (UNVERIFIED). The
  comparison's "largest accuracy payoff" benefit is UNPROVEN and the
  twin-control evidence is theirs, not ours; the changelog anecdotes are
  not our baseline.

### (e) Pass criteria

- Mis-click baseline measured first; refusal rate measured against the
  pre-stated budget X; per-act cost measured. If refusals exceed X, the
  pilot FAILS (the probe is too refusal-happy) and the RefStore form stays
  rejected. PROVEN only with real laptop numbers; otherwise UNPROVEN. A
  pilot that cannot fail is not an experiment; the budget X is the fail
  line.

### (f) Fail and rollback notes

- If the probe refuses constantly on the dense app (the complete-read
  proof fails inside the caps), record it and stop; do not widen the caps
  mid-run. The probe is not landed; remove or disable it after the pilot.
  Owner Zen untouched (Zen is not AT-SPI-registered).

## 7. I4 stale-ref preflight, a11y lane first

### (a) Item, source, register verdict/conditions

Agent-desktop I4, SPLIT, W3 D2: "Batch executor + whole-batch preflight."
D6 validation half is ALREADY BUILT (cu.py:1933, a11y.py parse_ref def at
line 183, on branch integration-20261127), no work. Cross-command executor
REJECTED (duplicates the more token-efficient cu.py act model, no measured
need). Remaining gap is stale-ref preflight only. Pilot: "Stale-ref
preflight pilot: validate refs against a fresh observation before dispatch,
on the a11y lane first." Integration report pilots list: "I4 stale-ref
preflight". UNPROVEN until it reports.

### (b) Preconditions and setup on the real laptop

- Branch: integration-20261127 checkout at the tip recorded at run time.
- cu.py:1933 is the batch validation call (`validate_actions(actions,
  'desktop')`; the function is defined at cu.py:1328). a11y.py parse_ref
  (def line 183) is the ref-resolution code; ground() is defined at
  line 207. All line numbers are on branch integration-20261127.
- The a11y lane. The pilot brief names the AT-SPI app before running, by
  the selection rule in the I2 plan (AT-SPI-registered, launchable, safe
  state), and lists the act set per act with the expected target and the
  worst-case effect, per the safe-target rule in the common rules. Pilot
  BLOCKED until the app and act set are recorded.
- Preflight enable mechanism (built as part of this pilot): a flag-gated
  step in the cu.py dispatch path, before the existing batch validation
  at cu.py:1933, that validates each ref against a fresh observation
  (a11y.py parse_ref / ground against the fresh snapshot) and skips the
  dispatch when validation fails.
- False-positive threshold: stated in the brief before running (a
  coordinator decision). Drafter-proposed default: at most 1 false
  positive per 20 dispatches (5 percent), marked DRAFTER RULE; the brief
  confirms or replaces it before the first run. Exceeding the stated
  threshold is a pilot failure, not a judgement call. cu.py session with
  the pill visible.

### (c) Live test steps

1. Record the integration-branch tip, the owner Zen PID (see common rules),
   the named app, the act set, and the false-positive threshold. Start a
   cu.py session; confirm the pill is visible.
2. Baseline: run the stated act set on the named app with current dispatch
   (no preflight). Record acts that fail or land wrong because the ref went
   stale between observation and dispatch (stale means the ref no longer
   resolves in a fresh observation taken at dispatch time). Only safe acts
   on safe targets, per (b).
3. Enable stale-ref preflight per the mechanism in (b): before each
   dispatch, validate the ref against a fresh observation. If it fails
   validation, skip the dispatch and record a preflight catch; do not
   dispatch.
4. Run the same act set. Record catches, false positives (valid refs
   flagged stale, checked by re-validating against a second fresh
   observation), and added latency per dispatch in ms.
5. Record in probes/ledger.jsonl; save a grim screenshot; verify the owner
   Zen PID is unchanged; remove test files and disable the preflight;
   verify the desktop is clean; end the session.

### (d) Before/after measurements

- Stale-caused failures per act set (baseline); preflight catches, false
  positives, added ms per dispatch (pilot arm).
- Baseline: no stale-ref rate exists in the sources (UNVERIFIED). The 54x
  DOM-rect figure evidences DOM rect round trips, not the executor, and
  must not be cited as the preflight's saving.

### (e) Pass criteria

- Stale-ref catches measured with a false-positive count and per-dispatch
  latency on the laptop. The false-positive count must stay at or below
  the threshold stated before the run; above it, the pilot FAILS.
  PROVEN only with real laptop numbers; otherwise UNPROVEN. The executor
  form stays REJECTED regardless of the pilot outcome; the pilot covers
  preflight only.

### (f) Fail and rollback notes

- If false positives exceed the stated threshold (valid refs blocked),
  record the rate and stop; do not loosen validation silently. The
  preflight is not landed; disable it after the pilot. No executor code
  is built.

## 8. I6 click verification, gated on measured silent-failure rate

### (a) Item, source, register verdict/conditions

Agent-desktop I6, PILOT-FIRST, W3 D2: "Post-action verification as a tool
duty." NARROWED premise (C3 stands): set_text already verifies
(a11y.py:329-331 in act(), def at line 307, on branch
integration-20261127) and act() already re-observes; the RDP "read-back"
claim is corrected (navigate re-reads the tab list to re-attach identity,
not page state; no verify symbol in rdp_client.py). Remaining gap is click
verification plus the disposition field, depending on I1. Uniform duty
REJECTED (doubles observation cost for correlated evidence). (R2) Build
opposed until a silent-failure rate for clicks is measured on named apps.
Pilot: "Click verification pilot: one action family (click on a11y act),
gated by a measured silent-failure rate for that family." Integration
report pilots list: "I6 (click verification, gated on measured
silent-failure rate)". I1 (envelope plus disposition, Zen lane) is
implemented and live-tested; the combined items 1-15 gate still runs for
items 6-15 coverage. UNPROVEN until it reports.
- Note: the non-zero-rate requirement for the Phase 2 build below is a
  DRAFTER STRENGTHENING of the register's R2 condition, which gates the
  build on measurement alone. It is stated here as a drafter rule, not a
  register condition.

### (b) Preconditions and setup on the real laptop

- Branch: integration-20261127 checkout at the tip recorded at run time.
- I1 envelope plus disposition exists on the Zen lane (queue item 9,
  live-tested). The a11y lane.
- The pilot brief names the apps and, per click, the expected observable
  effect, by the selection rule in the I2 plan (AT-SPI-registered, safe
  state) and the safe-target rule in the common rules (worst-case effect
  listed per click; any click whose worst case is destructive is
  forbidden). Pilot BLOCKED until the apps and the per-click expected
  effects are recorded.
- Check-window amount (DRAFTER RULE): re-observe 1 s after the click. The
  1 s value follows the R3-072 prep record (wait about 1 s plus re-read
  after each step); the brief confirms or replaces it before Phase 1.
- Phase 2 build spec (only if Phase 1 finds a non-zero rate): click
  verification for the a11y act family, reporting through the I1
  disposition field; for the a11y lane the disposition is recorded in the
  pilot log per click with values verified_ok, verified_failed, or
  unverified. cu.py session with the pill visible.

### (c) Live test steps

Phase 1 (measure, no build):

1. Record the integration-branch tip, the owner Zen PID (see common rules),
   the named apps, the click set, and the expected effect per click.
   Start a cu.py session; confirm the pill is visible.
2. Verify each expected effect once per click type before counting
   failures: one observed successful effect per type, recorded in the
   pilot log. An unverified expectation cannot count failures against it.
3. On each named app, run the stated set of clicks. After each click,
   re-observe after the check window and check the expected effect. Record
   silent failures (the click reported success, no expected effect
   observed) per click. Only safe clicks on safe targets, per (b).
4. Record the silent-failure rate.

Phase 2 (build, only if Phase 1 finds a non-zero rate):

5. Build click verification for the a11y act family per the spec in (b)
   (verify after click; report the outcome through the disposition field).
6. Re-run the same click set with verification. Record verified failures
   caught, false alarms, and added cost per click (extra observation ms).
   A false alarm is distinguished from a real failure by re-checking the
   effect after the check window: if the effect is present on re-check,
   the verification's failure report was a false alarm.
7. Record in probes/ledger.jsonl; save a grim screenshot; verify the owner
   Zen PID is unchanged; remove test files and disable the verification
   build; verify the desktop is clean; end the session.

### (d) Before/after measurements

- Silent-failure rate per click set (Phase 1); with verification: caught
  failures, false alarms, added ms per click (Phase 2).
- Baseline: no silent-failure rate exists in the sources (UNVERIFIED).

### (e) Pass criteria

- Phase 1 reports a measured silent-failure rate on the laptop. If the
  rate is zero across the measured sample, the pilot closes as a negative
  result and NO build happens (per the drafter strengthening in (a); the
  register's R2 condition gates the build on measurement alone). If
  non-zero, Phase 2 reports caught failures, false alarms, and cost.
  PROVEN only with real laptop numbers; otherwise UNPROVEN. The uniform
  duty stays REJECTED regardless.

### (f) Fail and rollback notes

- If Phase 1 cannot distinguish silent failure from slow effect (the
  effect arrives after the re-observation), record the ambiguity and
  lengthen the check window only by the pre-stated amount in the brief;
  do not tune it until the rate looks good. The verification build is not
  landed; disable it after the pilot.

## 9. I12 event-line convention, drive logs first, one lane

### (a) Item, source, register verdict/conditions

Agent-desktop I12, PILOT-FIRST, W3 D2: "Append-only trace segments." Form
changed by redteam condition: the session-trace subsystem (merge/read
commands, new storage contract) is REJECTED. What survives is a one JSONL
event-line convention adopted by the noisiest emitters, with grep as the
reader. Traces stay local, never committed. Verdict adjusted from ADOPT
(C1/C2) to PILOT-FIRST because the remaining form is unproven on any lane.
Pilot: "Event-line convention pilot: drive logs first, one lane, no new
commands." Integration report pilots list: "I12 (event-line convention)".
I13 (architecture guard) is implemented; it makes the local-only trace
rule enforceable rather than aspirational. UNPROVEN until it reports.

### (b) Preconditions and setup on the real laptop

- Branch: integration-20261127 checkout at the tip recorded at run time.
- I13 guard implemented (it covers the local-only rule).
- Lane: drive logs. The pilot brief names a specific past event chain
  from the run record and the log files that hold it, before the first
  run. Pilot BLOCKED until the chain and the log files are named.
- Emitter selection: step 1 counts lines per emitter in the named baseline
  drive log and names the top emitter. The first emitter to check is
  scripts/timing.py TimingLogger (the always-on run-timing JSONL writer:
  one row per step, wall clock Asia/Ho_Chi_Minh, elapsed seconds from run
  start). Before adopting the convention in the named emitter, verify the
  emitter is lane-local via an import/call graph (the emitter must be
  called only from the drive lane); record the check output. A shared
  emitter (for example a drive logger used by all lanes) must not be
  changed as a one-lane pilot.
- Event-line schema (DRAFTER-SPECIFIED SCHEMA, stated here): one JSON
  object per line with fields ts (ISO, Asia/Ho_Chi_Minh), lane, event,
  run_id, task, detail. No new commands are built.

### (c) Live test steps

1. Record the integration-branch tip, the owner Zen PID (see common rules),
   the named baseline chain and its log files. Start a cu.py session;
   confirm the pill is visible.
2. Baseline: time the reconstruction of the named chain from the current
   mixed-format logs with grep (wall minutes plus commands used).
3. Name the emitter by counting lines per emitter in the baseline drive
   log; verify it is lane-local per (b); record the emitter name and the
   check output.
4. Adopt the event-line convention (schema in (b)) in the named lane's
   emitter(s) only.
5. Drive a stated run (the brief states which drive). Record the event
   lines produced.
6. Reconstruct the SAME chain named in step 2 (not merely the same kind of
   chain) with one grep over the JSONL lines; time it. The before and
   after times are comparable only because they are the same chain.
7. Parse-check: every line in the pilot window parses as JSON; count
   unparsable lines.
8. Verify no trace file was committed: check `git log --name-only` over
   the pilot branch for any trace-file path AND `git status` for
   uncommitted trace files. `git status` alone cannot detect a trace file
   committed in an earlier step. Verify no new command was added.
9. Record in probes/ledger.jsonl; save a grim screenshot; verify the owner
   Zen PID is unchanged; remove local trace files created for the pilot
   unless the convention lands; verify the desktop is clean; end the
   session.

### (d) Before/after measurements

- Reconstruction time in minutes before vs after, on the SAME chain; grep
  commands used before vs after (count); unparsable lines (must be 0).
- Baseline: no reconstruction time exists in the sources (UNVERIFIED; the
  pilot measures the before case first).

### (e) Pass criteria

- The chain reconstructs with one grep; 0 unparsable lines; 0 trace files
  committed (history check plus worktree check); 0 new commands added.
  PROVEN only with real laptop numbers; otherwise UNPROVEN. The subsystem
  form stays REJECTED regardless.

### (f) Fail and rollback notes

- If emitters produce unparsable lines, record the count and fix the
  emitter, not the reader; if the convention slows the emitter measurably,
  record the cost. Remove the convention from the pilot lane's emitters
  after the pilot if it does not land; delete local trace files created
  for the pilot.

## 10. I14 bench re-run, query() ungate only, extents stays opt-in

### (a) Item, source, register verdict/conditions

Agent-desktop I14, PILOT-FIRST, W4 D2: "Ungate pick4 extents / query /
ground + find-style locator." Not a single flip. Re-run the observation
timing benches first; ungate query() only; extents stays opt-in until its
per-element cost is measured. (R2) Bench must measure coverage too, not
only cost (which widget classes silently report no extents); query() and
extents-default ungate separately. Pilot: "Bench re-run + query() ungate
experiment." Integration report pilots list: "I14 (bench re-run, query()
ungate separately)". The I16 a11y half is gated on I14. UNPROVEN until it
reports.

### (b) Preconditions and setup on the real laptop

- Branch: integration-20261127 checkout at the tip recorded at run time.
- scripts/a11y.py query() exists (def at line 156, docstring lines 156-161:
  "One observe (same 500-node, 2s, 80-item bounds), then filter in
  memory"); it is dispatched as the 'query' operation at a11y.py:351.
  Line numbers are on branch integration-20261127. There is NO flag gating
  query(): the "gate" is that the default read path is the full observe()
  and query() is not used by it. The ungate mechanism is therefore to run
  the bench's query workload through the query operation; re-gate is
  removing the query workload from the bench (no code change to revert).
- Bench script: NO observation-timing bench exists in the tree. The three
  candidates from the draft measure other things (verified in the tree on
  branch integration-20261127): tests/control_benchmark.py benchmarks the
  CLI vs the resident executor (session_driver timing); tests/
  browser_task_benchmark.py benchmarks Chromium task routes (batch vs
  split/wait); scripts/bench_manifest.py is a manifest writer, not a
  bench. The pilot's first build step is to write the observation-timing
  bench: a script that times observe, query, and ground via the a11y
  operation dispatch (a11y.py:348-351), 10 repeated runs per operation
  (DRAFTER RULE), median plus p95 recorded. Record the bench path in the
  pilot report. docs/benchmarks/ exists as the baseline store (I8).
  docs/benchmarks/adaptive-observation-2026-10-19.json carries no
  query/extents timing (verified: 0 mentions).
- A named AT-SPI app for the coverage arm, by the selection rule in the I2
  plan (AT-SPI-registered; include widget classes that may silently report
  no extents). The brief names it before the arm runs. Pilot BLOCKED until
  the app is named.

### (c) Live test steps

1. Record the integration-branch tip, the owner Zen PID (see common rules),
   and the bench path. Start a cu.py session; confirm the pill is visible.
2. Write the observation-timing bench per (b) and run it on the laptop.
   Record the bench numbers (cost per observe, query, and ground) into
   probes/ledger.jsonl plus docs/benchmarks/. This re-run IS the baseline.
3. Coverage arm: on the named app, record per widget class whether extents
   are reported or silently absent. "Silently absent" means a widget class
   that should have extents (visible, with a bounding box in the app's own
   layout) but reports none; classes with no visual representation are
   "correctly absent", not gaps. The expectation per class is stated
   before the arm runs.
4. Ungate query() only (extents stays opt-in): run the same bench's query
   workload through the query operation. Record per-query wall time and
   result correctness vs the gated form.
5. Do NOT ungate extents-default in this pilot.
6. Record all numbers in probes/ledger.jsonl; save a grim screenshot;
   verify the owner Zen PID is unchanged; remove test files; verify the
   desktop is clean; end the session.

### (d) Before/after measurements

- Bench cost numbers before (the re-run is the baseline) vs query()-ungated
  (per-query ms, correctness match rate); coverage table (widget class
  maps to extents reported, silently absent, or correctly absent).
- Baseline: no bench numbers exist in the named sources (UNVERIFIED).

### (e) Pass criteria

- Bench re-run numbers recorded; query() ungated with measured cost and
  correctness; coverage table recorded; extents still opt-in. PROVEN only
  with real laptop numbers; otherwise UNPROVEN. A single flip (query plus
  extents together) is a fail of the pilot design, not a pass.

### (f) Fail and rollback notes

- If ungated query() is slower or returns wrong results, record the
  numbers and re-gate it (remove the query workload from the bench); do
  not keep it ungated on a partial result. The bench re-run numbers stay
  recorded even if the ungate fails (the bench is the durable output).

## 11. I18 drift check, after item 0 privacy scrub

### (a) Item, source, register verdict/conditions

Agent-desktop I18, PILOT-FIRST, W3 D2: "Tool-served, version-matched
guidance." Form changed: embedding/serving guidance is REJECTED (creates
a second source of truth). What survives is a version-matched drift check
(doctor check that the checked-out skill matches the tool version).
Pilot: "Drift-check pilot: one CLI, generic text only, scrub list
applied." Integration report pilots list: "I18 (drift check, after item
0)". Precondition SATISFIED: item 0 privacy scrub is ON MAIN (PR #1140
merged d69ef7c9); on todolist-push the name was scrubbed (8b9f5da4,
9fd84006); the profile dir was genericized on integration-20261127
(7caff5b9); the I13 guard (name
denylist over skill/docs) is implemented. The scrub list must cover
personal names, not only ports and paths (section 6 finding). UNPROVEN
until it reports.

PRIVACY RULE binding this whole plan: no step in this pilot reads, writes,
or searches for the scrubbed name. The scrub verification is the I13
arch-guard pass alone; nobody greps for the name to prove it is gone.

### (b) Preconditions and setup on the real laptop

- Branch: integration-20261127 checkout at the tip recorded at run time.
- CLI and skill pair (named here): CLI scripts/zen_cli.py, skill
  skill/cli-anything/zen.md (both exist on branch integration-20261127).
  Tool version: the CLI has no --version flag (verified: no --version
  argument in scripts/cu.py, scripts/zen_dom.py, or scripts/zen_cli.py;
  zen_cli.py reports browser_version via BiDi, not a tool version). The
  version used by this drift check is therefore the integration-branch
  tip hash at run time: the skill must describe the CLI as of that tip.
- Drift-check build spec: compare the skill text's stated subcommands and
  flags against the CLI's actual argparse subcommands at the recorded tip;
  match means every subcommand and flag the skill names exists in the CLI;
  drift means any mismatch.
- Scrub list: the I13 machine-value denylist in rung3-ci/arch-guard.py
  (personal name forms, profile-dir hash pattern, home paths, Tailscale
  IPs), scanned over scripts/, skill/, docs/, and the other trees the
  guard covers. Only generic text is checked; no personal data in the
  checked text or the pilot output.

### (c) Live test steps

1. Record the integration-branch tip (this is the tool version for the
   check) and the owner Zen PID (see common rules). Start a cu.py session;
   confirm the pill is visible.
2. Verify the item 0 scrub is in place on the checkout by running
   `python3 rung3-ci/arch-guard.py` and requiring exit 0 (PASS). This is
   the SOLE scrub verification. Do not search for the scrubbed name in any
   file, in any form.
3. Implement the drift check as a doctor check for scripts/zen_cli.py:
   compare the checked-out skill text (skill/cli-anything/zen.md) against
   the CLI as of the recorded tip; report match or drift.
4. Run it against the known current state (expect match; record the
   result).
5. Negative control: stage a mismatch by editing ONE generic field in a
   copy of the CURRENT scrubbed skill text (for example remove one real
   subcommand name from the copy's stated list) and confirm the check
   reports drift. The staged pair is produced from the current scrubbed
   text only, never from an older version of the skill (any older version
   predates the scrub). Verify the staging by diffing the staged copy
   against the current scrubbed original: the diff must show exactly the
   one intended generic-field change and nothing else. The staged pair is
   never committed.
6. Record runtime plus results. Confirm the staged pair contains no
   personal data by the diff check in step 5 (the guard passes on the
   checkout before and after; the guard's fixed scan trees do not cover
   scratch files, so the diff check is the control for the staged pair).
7. Record in probes/ledger.jsonl; save a grim screenshot; verify the owner
   Zen PID is unchanged; remove test files and the staged copy; verify the
   desktop is clean; end the session.

### (d) Before/after measurements

- Drift-check result on the true pair (match) vs the staged mismatch pair
  (drift reported); check runtime in seconds; arch-guard exit code before
  and after (must be 0); staged-pair diff (must show exactly the one
  intended change).
- Baseline: no drift check exists (UNVERIFIED); the true-pair result is
  the baseline.

### (e) Pass criteria

- The check reports match on the true pair and drift on the staged
  mismatch; arch-guard exit 0 before and after; the staged-pair diff
  shows exactly the one intended generic-field change; runtime recorded.
  PROVEN only with real laptop numbers; otherwise UNPROVEN. The serving
  form stays REJECTED regardless.

### (f) Fail and rollback notes

- If the check cannot distinguish match from drift, record the confusion
  and stop; do not ship a check that cries drift on clean pairs. The drift
  check is not landed; remove or disable it after the pilot. If any
  personal data appears in pilot output, stop, delete the output, and
  record the leak (the scrub list failed). If the arch-guard fails at any
  point, stop: the scrub precondition is not met.

## 12. I23 browser-lane conformance, one fixture page, two lanes first

### (a) Item, source, register verdict/conditions

Agent-desktop I23, SPLIT, W4 D3: "Conformance contract tests." Browser
lanes (BiDi, Marionette, RDP) on one fixture page PILOT-FIRST. AT-SPI half
REJECTED until a fixture app exists (no native app with a stable a11y tree
launches headlessly on this VM today). C3's correction stands: the R3-100
webdriver-disagreement anecdote is UNVERIFIED (the file checked is about
port rules) and must not be cited as established; the idea stands on the
verified lane divergence. Pilot: "Browser-lane conformance pilot: one
fixture page, two lanes first." Integration report pilots list: "I23
(browser-lane conformance)". The I9 unified interface pilot waits on I23.
UNPROVEN until it reports.

### (b) Preconditions and setup on the real laptop

- Branch: integration-20261127 checkout at the tip recorded at run time.
- Lanes (named here): RDP lane scripts/zen-rdp/rdp_client.py (subcommands
  probe, tabs, report, eval <expr>, peval <expr>, navigate <url>, bench;
  --port is required) and Marionette lane improvements/zen-sidebar/
  zen_live.py (subcommands introspect, list, pin, unpin, move-tab,
  create-folder, leave-folder, move-folder-space, switch-workspace,
  move-workspace, move-folder, preflight; --host defaults to 127.0.0.1,
  --port defaults to 2828). Both exist on branch integration-20261127.
- Fixture page: a single local HTML file created by the pilot at a
  recorded scratch path, containing at least one link, one button, one
  text input, and one heading (the elements the action set needs). Serve
  it with `python3 -m http.server <port>` from the scratch dir; record
  the URL.
- Action set (drafter-proposed, verified per lane in step 0): list tabs
  (RDP `tabs`, Marionette `list`), read tab state (RDP `probe`,
  Marionette `introspect`), navigate (RDP `navigate <url>`; Marionette
  zen_live.py has no navigate subcommand, so it is lane-unsupported, not
  faked), evaluate (RDP `eval <expr>`; Marionette has no eval subcommand,
  so it is lane-unsupported, not faked).
- Sessions: default to throwaway-profile sessions for both lanes. Owner
  Zen only with explicit coordinator approval, and then only a new tab
  beside (hard rule: never close or navigate the user's browser tabs),
  with the pill up. cu.py session with the pill visible.

### (c) Live test steps

1. Record the integration-branch tip, the owner Zen PID (see common rules),
   the fixture path and URL, and the two lanes. Start a cu.py session;
   confirm the pill is visible.
2. Step 0 (support check): verify each lane supports each action in the
   set by running it once on the fixture. Drop any action a lane does not
   support from the comparison set, with the reason recorded. The set must
   keep at least 2 actions to proceed; otherwise stop and record
   INCONCLUSIVE.
3. Run the comparison action set through lane 1 on the fixture page;
   record each action's outcome.
4. Reset the fixture to its initial state: reload the fixture page and
   verify the initial state (element count and known content) before lane
   2 runs. Record the reset and the verification.
5. Run the same action set through lane 2 on the same fixture page; record
   each outcome.
6. Compare per action: agreement or divergence. For every divergence,
   record the reason, or mark it UNEXPLAINED.
7. Do not cite the R3-100 anecdote anywhere in the record. Before filing,
   a named second reader confirms the pilot report contains no reference
   to the R3-100 incident; the check verifies absence of the citation and
   does not quote the incident.
8. Record in probes/ledger.jsonl; save a grim screenshot. If the pilot
   used the owner Zen, verify its PID and tab state before and after and
   RESTORE the tab state (close only the tab the pilot opened; the tab
   list must be verified identical after, not merely recorded). Remove the
   fixture staging; verify the desktop is clean; end the session.

### (d) Before/after measurements

- There is no before/after change (conformance measurement). Metrics are
  actions run per lane, agreements, divergences, and unexplained
  divergences (must be 0 for a pass).
- Baseline: the verified lane divergence is the premise; no per-action
  divergence counts exist in the sources (UNVERIFIED).

### (e) Pass criteria

- 0 unexplained divergences across the pilot's action set; every divergence
  explained in writing; fixture reset verified between lanes; tab state
  restored if the owner Zen was used. PROVEN only with real laptop
  numbers; otherwise UNPROVEN. The AT-SPI half stays out of this pilot.

### (f) Fail and rollback notes

- Any unexplained divergence fails the pilot's pass bar. Record it; do not
  relabel it as a quirk. No lane code is changed by the pilot, so there is
  nothing to roll back; remove the fixture staging after the pilot if it
  was created for it.

---

## Deferred halves (not plans in this slice; for the assembler header)

Four agent-desktop PILOT-FIRST halves have no test plan in this draft and
are recorded here as an explicit deferral, not silently dropped (council 1
M7, council 3 M1). Each is gated on another pilot's outcome, so a full plan
cannot run yet:

- I5 walk half: "Walk-cost + wrapper census pilot" (bounded-concurrency
  GetAll rewrite). Gate: a pre-stated success metric for the walk, then
  the pilot runs.
- I9 unified interface pilot: "One-lane-pair interface pilot". Gate: I23
  (this slice, plan 12) pins lane behavior first.
- I10 hit-test half: "Hit-test signal probe". Gate: a hit-test signal is
  proven to exist first.
- I16 a11y half: "a11y overlay pilot". Gate: I14 (this slice, plan 10)
  reports first.

The coordinator confirms this deferral. When a gate fires, the half gets a
full plan in the same (a)-(f) format.

---

