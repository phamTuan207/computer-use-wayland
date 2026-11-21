# Council Member 2 (structure): review of the A1 narrow pilot plan

- Date: 2026-11-21
- Role: Council Member 2, structure only. Worker A1 (Muse) is the pilot worker.
- Reviewed: improvements/worker-a1-pilot-plan.md (DRAFT, uncommitted at review time),
  improvements/working-structure-redesign-20261121.md sections 5.1-5.4,
  improvements/a1-code-exec-dom-design.md sections 5-7.
- Owner order: best quality, not speed. Owner approved the working-structure
  redesign proposal 2026-11-21 18:17, follow it as Lauren Tan advises.
- Standing rules applied: no fabrication, unknown stays UNVERIFIED, no em dash
  or en dash anywhere, never ydotool, no personal info in any commit, small
  commits push as you go.
- Status of the pilot at review time: NO live arm has run. Nothing below is
  contaminated by results, because there are no results yet.

## Verdict summary

| Design point | Verdict | One line |
|---|---|---|
| 0. Referenced artifacts exist (runbook, schema, checker) | BLOCK | Three files the plan cites do not exist yet |
| 1. One fresh executor runs both arms | AMEND | Right choice, but the no-knowledge list and the learning control are underspecified |
| 2. Blinded checker | AMEND | The checker as specified is not blind; the log shape leaks the arm |
| 3. Evidence contract per run | AMEND | Necessary evidence listed, but commit hash, flags, broker-solo proof, and an independent checker re-run are missing |
| 4. Resume preconditions | AMEND | Mostly checkable in principle; three are currently unmet and two are unverifiable as worded |
| 5. Sealed manifest custody | AMEND | Writer, holder, and early-open prevention are undefined; a repo-committed manifest is not sealed from an executor with repo access |
| 6. Executor death mid-pilot | AMEND | No restart rule exists at all; one must be pre-registered before run 1 |
| Overall pilot plan | AMEND, not BLOCK | The design is sound and every gap below is closable by writing, not by redesign. No live run may start until points 0, 4, 5, and 6 are closed. |

## Finding 0: three files the plan cites do not exist (BLOCK)

Verified 2026-11-21 by direct listing in the repo on branch todolist-push:

- tests/realistic/a1-pilot/runbook.md: does NOT exist. Plan section 3 says
  the executor follows this runbook; section 9 says the executor is briefed
  from the runbook only.
- tests/realistic/a1-pilot/run-log-schema.md: does NOT exist. Plan section 8
  says the schema lives here.
- tests/realistic/a1-pilot/check_run.py: does NOT exist. Plan section 6 says
  this script is the checker.
- runs/manifest-sealed.jsonl: does NOT exist, and the runs/ directory does
  not exist either. Plan section 6 says the manifest is sealed here.

This is a BLOCK on starting any live run, not on the plan itself. A plan
whose executor brief, log schema, and checker are all unwritten cannot be
executed, and any run done before they exist would be unblinded by
construction (there would be no checker to be blind, and no runbook to
brief from). The block lifts when all three files exist, are committed,
and pass the checks in Finding 4.

Exact amendment text (plan section 9, add as the first precondition):

> No live arm starts until tests/realistic/a1-pilot/runbook.md,
> tests/realistic/a1-pilot/run-log-schema.md, and
> tests/realistic/a1-pilot/check_run.py all exist on branch todolist-push,
> are committed, and are named by commit hash in the pilot log. The
> runbook contains no numbers, no hypothesis, and no Pick 1 results
> (see Finding 1). The checker passes its self-test (see Finding 4)
> before run 1.

Also verified while checking: the pick4 fixture md5 matches the plan
(91b2f92945c167306a13ae32977a9bf3, 719 bytes). The f01 fixture md5 was
computed during this review as 2b6eda97036af51510b7eefe6d36dd93; the plan
only says the f01 fixture is "present" and gives no checksum. Freeze
that md5 in the plan before run 1 (see Finding 4).

## Finding 1: one fresh executor runs both arms (AMEND)

### Verdict

GO on the choice itself: one fresh executor running both arms is the
right design. AMEND on what the executor must not know and on how
learning across runs is controlled.

### Why one executor is right

A different executor per arm would trade a controllable problem
(learning across runs) for an uncontrollable one (executor skill
variance). Two executors differ in speed, error rate, and recovery
style, and with n=3 per arm that difference would confound the arm
effect directly: a fast CODE executor and a slow STEP executor would
look like a batching win. One executor, same model, same harness,
alternating arms, is a within-subject design, and it is the only
design in which the arm comparison is interpretable at n=3. The
alternating order (STEP, CODE, STEP, CODE, STEP, CODE) with STEP first
so first-run warmup lands on the control arm is conservative and
correct. Keep it.

### What is wrong

First, the no-knowledge rule in plan section 9 ("no knowledge of the
pilot's numbers or the hypothesis direction beyond the arm procedure")
is vague in exactly the place where vagueness leaks. The executor
cannot be blind to the arm: it performs the procedure, so it knows
which procedure it just ran. What it must not know is narrower and
must be listed exactly, or the briefer will improvise.

Second, the plan has no control for learning. The same executor runs
Case B (26 spec steps with a mid-task wrong-formula diagnosis) six
times. By run 3 it knows where the wrong formula sits, what the fixed
values are (E5=1864000, E6=621333, E7=3), and which steps are slow.
That learning accrues to both arms through alternation, so it does not
favor one arm outright, but it shrinks wall times across the sequence
and can shrink the arm gap if the learned parts are the parts batching
was supposed to absorb. The plan never records run sequence against
wall time, so this trend would be invisible.

Third, "fresh" is undefined. A fresh executor that has read the pilot
plan or the design file is not fresh: the design file states Pick 1
wall minus 53% and D1 think 99.2s to 20.7s, which reveal the direction
of the hypothesis. Fresh must mean the executor has read the runbook
only.

### Exact amendment text (replace plan section 3, "Executor", and plan section 9, last bullet)

Replace the executor paragraph in section 3 with:

> Executor: ONE fresh executor agent runs both arms (same model, same
> harness), following the written runbook
> (tests/realistic/a1-pilot/runbook.md) and nothing else. The executor
> is not Worker A1 and not the checker. Fresh means the executor has
> read the runbook only: it has not read the pilot plan, the design
> file, or any prior run report. The runbook contains the procedure
> for each arm and no numbers, no hypothesis, and no prior results.

Replace the last bullet of section 9 with:

> Executor briefed from the runbook only. The executor must NOT know:
> (a) the hypothesis direction (which arm is expected to be faster);
> (b) the GO bar (the 30% figure, the pass-rate rule, the recovery
> rule); (c) the wall time, pass/fail, or any metric of any completed
> run; (d) any checker verdict; (e) the sealed manifest, its location,
> or any run-id to arm mapping beyond the run it is currently doing;
> (f) the held-out task identity. The executor DOES know the procedure
> of the arm it is currently running; executor blinding to the arm is
> impossible and is not claimed. Only checker blinding is claimed.
> The executor receives one run at a time: run-id plus the arm
> procedure for that run, nothing else. After each run the executor
> reports only that the run finished and where its evidence directory
> is; it receives no feedback before the next run.

Add to plan section 8, per-run fields:

> run_sequence: the run's position in the full 12-run sequence (1-12),
> recorded so a learning trend in wall time across the sequence is
> visible at analysis time. The unblinding step reports wall time by
> run sequence as well as by arm.

### Washout: considered and rejected

A washout task between arms (an unrelated task to clear working
memory) was considered. It does not fix task-specific learning: the
executor would still remember where the wrong formula sits in Case B
and what the fixed values are. A washout costs wall time and adds a
new confound (washout-task fatigue) while leaving the actual leak
untouched. Rejected. The controls are no interim feedback, no
knowledge of the GO bar or direction, and run-sequence logging, all
above.

### Different executor per arm: considered and rejected

Rejected for the variance reason above. Model variance between two
executors at n=3 is a larger threat than learning within one executor
under alternation with no feedback.

## Finding 2: the blinded checker is not blind (AMEND)

### Verdict

AMEND. The checker as specified in plan section 6 can infer the arm
from the run-log shape, so it is not blind. This is plan open
question 5, and the answer is yes, it leaks, in at least four ways.

### The leaks

1. Program-call lines. CODE runs contain program calls and program
   char counts; STEP runs contain zero program calls by definition.
   Any checker that reads the timed log sees this immediately.
2. Tool-call counts. STEP runs make one model tool call per step
   (Case B: 40+ low-level actions); CODE runs make at most 3 program
   calls plus setup calls (Pick 1: 5 calls to 2). The plan's own
   metric 2 (tool_calls, counted from the transcript) differs by an
   order of magnitude between arms.
3. Timing patterns. CODE runs have few, long in-program gaps; STEP
   runs have many short observe-act gaps. Wall time itself is the
   effect under test, so any faithful timing read leaks the arm.
4. Run-number parity. Run order is fixed as STEP, CODE, STEP, CODE
   per case. If the checker ever sees a run number, or a directory
   listing ordered by creation time, parity reveals the arm. The
   random 8-hex run-id helps only if the run number and the creation
   timestamp are both withheld from the checker, which the plan does
   not state.

The DOM dump and the final screenshot do not leak: both arms end at
the same end state, so the end-state DOM and the final screenshot
should be identical in content. The leak is entirely in the log.

### Why log normalization does not fix it

Stripping op names or program-call lines from the log before the
checker reads it was considered. It fails because the metrics
themselves leak: tool_calls and wall_ms are the effect under test,
and any checker that outputs the six metrics from the full log has
read the leaking fields. You cannot both compute the metrics from a
log and stay blind to what the log says about the arm. The fix is
structural, not cosmetic: split the verdict from the metrics.

### Exact amendment text (replace plan section 6 in full)

> ## 6. Blinded checker (two stages)
>
> Each run writes evidence to runs/<run-id>/ where run-id is a random
> 8-hex string assigned at run start from a pre-generated set (see
> section 9). The run manifest (arm label, case, run number) is
> sealed under the custody rule in section 9b and the checker never
> opens it.
>
> Stage 1, blind verdict. The checker is
> tests/realistic/a1-pilot/check_run.py. Input: one run directory,
> given as a single path. It reads ONLY the end-state DOM dump and
> the final verification screenshot in that directory, and outputs
> ONLY PASS/FAIL plus the end-state values it checked. It reads no
> timed log, no transcript, no timestamps, no run number, and no
> directory listing across runs. It contains no code path that opens
> the manifest; a grep for "manifest" in check_run.py must return
> nothing, verified before run 1. Stage 1 runs once per run
> directory, and its verdict files are committed before unblinding.
>
> Stage 2, unblinded metrics. Only after ALL 12 Stage 1 verdicts
> are committed, Worker A1 runs the metrics script over the full
> timed logs and transcripts, computing the six metrics plus
> per-run fields (section 8). Stage 2 is explicitly unblinded: it
> runs after the verdicts are locked, so metric computation cannot
> influence any verdict. Wall time by run sequence is reported
> alongside wall time by arm (see Finding 1).
>
> Unblinding happens only after ALL 12 runs are checked (Stage 1
> verdicts committed), in a separate step that joins run-id to arm
> from the sealed manifest, done by Muse (not the checker, not the
> executor, not Worker A1). See section 9b for custody.

Note the two changes inside that text: the checker no longer outputs
metrics (metrics move to Stage 2), and unblinding is done by Muse,
not Worker A1 (see Finding 5).

## Finding 3: evidence contract per run (AMEND)

### Verdict

AMEND. The plan's evidence per run satisfies the shape of the
redesign evidence contract (section 5.3: timed run log plus
end-state screenshot for machine tasks) but misses four items the
contract requires for the evidence to be runnable and attributable.

### What is present (GO)

Timed run log (JSONL), end-state DOM dump, final verification
screenshot, exact commands run. That is the right set for a machine
task, and the screenshot-or-video leg is satisfied by the screenshot.

### What is missing

1. Commit hash of the code under test. The pilot result is a claim
   about a harness (scripts/code_exec.py, scripts/cdp.mjs, the relay
   config). If that code changes mid-pilot, runs before and after
   are not comparable and the pilot is void, but nothing in the
   per-run evidence would show the change. The redesign contract
   requires "exact test command plus output/log, commit hash".
2. Relay flags and relay HEAD. The design file (section 5) requires
   CU_CODE_EXEC=1 and CU_PICK4_FASTPATH=1, and the relay reports
   started_git_head. A run done with the flags off is a different
   experiment. Per-run evidence must record both flags and the
   relay's started_git_head.
3. Broker-SOLO proof. Plan section 4 requires broker SOLO, citing
   the Pick 4 lesson that parallel workers blocked 0/4 runs. No
   per-run artifact proves SOLO held. A broker-status output per
   run is cheap and closes this.
4. Fixture checksum re-verification per run. Plan section 9 requires
   checksums re-verified before the pilot, but not per run. A
   fixture edited mid-pilot (even accidentally) would silently
   change the task. Per-run md5 of both fixtures is one command.
5. Independent re-run of the checker. The redesign contract says
   the generator never runs its own tests and only a different
   agent's runner evidence counts for landed changes. Here the
   executor generates the run evidence and a deterministic script
   checks it, so script execution by Worker A1 is acceptable, but
   the contract's separate-runner leg still needs a named actor:
   an independent runner (not Worker A1, not the executor) re-runs
   check_run.py over all 12 directories after Stage 1 and confirms
   identical verdicts. Without that, the verdicts rest on one
   operator running one script once.

### Exact amendment text (add to plan section 6, evidence per run, and to section 8)

Add to the evidence list in section 6:

> Evidence per run: timed run log (JSONL, schema section 8),
> end-state DOM dump (final cell values / #result text), final
> verification screenshot, exact commands run, git HEAD of the repo
> at run start, relay started_git_head plus the values of
> CU_CODE_EXEC and CU_PICK4_FASTPATH, broker-status output proving
> SOLO at run start, and md5 of both fixtures at run start. All
> eight items are written into runs/<run-id>/ before the run is
> counted as complete. A run missing any item is not counted in n=3;
> it is recorded as INCOMPLETE and re-run under a new run-id (see
> the restart rule, section 9c).

Add to section 6, after the Stage 1 paragraph:

> Independent checker re-run. After Stage 1 verdicts are committed,
> an independent runner (not Worker A1, not the executor) re-runs
> check_run.py over all 12 run directories and confirms identical
> verdicts. Any discrepancy stops unblinding until the cause is
> found and recorded.

## Finding 4: resume preconditions (AMEND)

### Verdict

AMEND. The preconditions in plan section 9 are mostly checkable in
principle, but three are currently unmet because their artifacts do
not exist, and two are unverifiable as worded. A precondition that
cannot be checked before a run starts is not a precondition, it is
a wish.

### Precondition by precondition

| Precondition as written | Checkable? | Status now |
|---|---|---|
| Owner away from the keyboard | No, as worded. No observation is named. | UNVERIFIED method |
| Broker SOLO and idle, Zen untouched | Yes, if the exact command is named | Command unnamed |
| Layer-2 preflight probes pass | Yes, once the probe programs exist | Probe programs UNVERIFIED (do not exist yet) |
| Fixture checksums re-verified | Yes | Pick4 md5 verified; f01 md5 never frozen in the plan |
| Run dirs + sealed manifest created, checker self-tested | Yes, once the files exist | UNMET: runbook, schema, checker, runs/ all missing |
| Executor briefed from runbook only | Yes, once the runbook exists | UNMET: runbook missing |

Additional gaps:

- Layer-1 preflight (unit test with FakeDomBackend, VM, prep now)
  has no recorded status anywhere. It is UNVERIFIED until the test
  file and its output exist and are committed. The plan must not
  claim Layer 1 as done.
- No precondition freezes the plan itself. Plan section 5 says
  thresholds are frozen only after council plus redteam debate and
  Worker A1 synthesis. Resume therefore also requires: the frozen
  plan commit hash recorded in the pilot log, and no threshold or
  case change after that hash.
- No precondition verifies the relay flags and HEAD (see Finding 3).
  Add it: relay started_git_head equals the repo HEAD at run start,
  CU_CODE_EXEC=1, CU_PICK4_FASTPATH=1, verified from relay status
  output before run 1 and re-checked if the relay restarts mid-pilot.
- "Zen untouched by the pilot" is checkable only if someone looks.
  Add: a desktop-state check (no Zen window touched by the pilot
  executor) recorded per run, or at minimum before run 1 and after
  run 12.

### Exact amendment text (replace plan section 9 in full)

> ## 9. Resume preconditions (all must hold before any live arm)
>
> - The frozen pilot plan commit hash is recorded in the pilot log.
>   No threshold, case, or cap changes after that hash. Any change
>   voids the freeze and requires a new hash and a new resume check.
> - Resume order: a written resume order from Muse, timestamped, in
>   the pilot log. "Owner away from the keyboard" is satisfied by
>   that order and by nothing else; no agent infers it from idle
>   signals. The order names the 12 pre-generated run-ids.
> - Broker SOLO and idle, proven by broker-status command output
>   saved per run (see section 6). Zen untouched by the pilot
>   (Chromium only); desktop state checked before run 1 and after
>   run 12.
> - Relay verified before run 1: started_git_head equals the repo
>   HEAD, CU_CODE_EXEC=1, CU_PICK4_FASTPATH=1, from relay status
>   output saved in the pilot log. Re-checked if the relay restarts
>   mid-pilot; a restart with a different HEAD voids all runs after
>   the restart point unless the change is recorded and the freeze
>   is re-issued.
> - Layer-1 preflight unit test run on the VM with output committed
>   (FakeDomBackend, bad ref rejected before any backend call, for
>   click, fill/set_value, and assert). Status is UNVERIFIED until
>   that output exists.
> - Layer-2 preflight probes pass (section 7), run by the executor
>   at resume before any pilot arm, with probe evidence (completed: 0
>   and zero DOM effects) saved per probe. If any probe shows a
>   partial effect, the pilot does NOT proceed; that is a NO-GO by
>   safety.
> - Fixture checksums re-verified: pick4 md5
>   91b2f92945c167306a13ae32977a9bf3, f01 md5
>   2b6eda97036af51510b7eefe6d36dd93. Both recorded per run (see
>   section 6).
> - Run directories plus sealed manifest created under the custody
>   rule in section 9b. Checker verified against a known-good and a
>   known-bad run directory (checker self-test), with both test
>   directories and both outputs committed. The known-good and
>   known-bad directories are built from frozen fixtures, not from
>   live runs.
> - Runbook, run-log schema, and checker exist and are committed
>   (see Finding 0). Executor briefed from the runbook only, under
>   the no-knowledge list in section 3.

## Finding 5: sealed manifest custody (AMEND)

### Verdict

AMEND. The plan names one non-reader (the checker) and one opener
(Worker A1, after all 12 runs). It does not name the writer, does
not name the holder, and does not say what stops the executor or
the checker from opening it early. A seal with no custodian and no
early-open prevention is a filename, not a seal.

### The concrete problems

1. Writer undefined. If the executor writes the manifest as runs
   proceed (run-ids "assigned at run start"), the executor holds
   the mapping while running. If Worker A1 writes it, Worker A1
   holds it and also does the unblinding, so one person holds both
   the seal and the key.
2. Holder undefined. The manifest lives at runs/manifest-sealed.jsonl
   inside the repo. Anyone with repo read access can open it,
   including the executor, which needs repo access for the runbook
   and fixtures. A file in the repo is not sealed from repo readers.
3. Early opening has no prevention and no detection. Nothing in
   the plan stops Worker A1 from opening it after run 6, or the
   executor from reading it between runs. There is no hash, no
   access log, and no audit.
4. Unblinding by Worker A1 is the wrong holder. Worker A1 authored
   the plan and runs Stage 2 metrics; letting the same agent hold
   the manifest and join verdicts to arms concentrates the two
   roles that must be separate.

### Honest limit (stated plainly, not hidden)

On a shared filesystem with one user, no technical seal can stop a
determined same-user agent from reading a file. This review does
not pretend otherwise. What the custody rule below provides is
separation of holders, a pre-published tamper hash, and a post-hoc
audit. That is the strongest seal available here, and it must be
described as that, not as an unbreakable seal.

### Exact amendment text (add as new plan section 9b)

> ## 9b. Sealed manifest custody rule
>
> - Custodian: Muse (coordinator) holds the manifest. Nobody else
>   holds a copy. Worker A1 holds only the sha256 hash. The
>   executor and the checker operator never receive the file, its
>   path, or its contents.
> - Creation: before run 1, Muse pre-generates 12 random 8-hex
>   run-ids and writes the mapping (run-id, case, arm, run number)
>   to a file OUTSIDE the repo (not under runs/, not committed).
>   Muse publishes only the sha256 of that file in the pilot log
>   before run 1. The manifest is never committed to the branch
>   before unblinding, because any repo reader (including the
>   executor) could open it.
> - Issue: the executor receives one run-id at a time with the arm
>   procedure for that run, and nothing else. It never sees the
>   full set of 12 ids.
> - Checker enforcement: check_run.py takes a single run directory
>   path and contains no code path to the manifest. Verified before
>   run 1 by grep for "manifest" returning nothing (see section 6).
> - Early-open prevention: (a) separation: the holder (Muse) is
>   not the executor, not the checker operator, and not the Stage 2
>   metrics runner; (b) tamper detection: at unblinding, Muse
>   re-hashes the file and compares against the hash published
>   before run 1; a mismatch voids the pilot and is reported
>   plainly; (c) audit: after the pilot, the executor's transcript
>   is grepped for the manifest path and filename; any access is
>   reported in the final report, and any access before unblinding
>   voids the affected runs.
> - Opening: only after all 12 Stage 1 verdict files are committed,
>   Muse opens the manifest in a single unblinding step, joins
>   run-id to arm, publishes the joined table, and only then
>   commits the manifest contents to the repo with the final
>   report. Opening before that point, by anyone, is a protocol
>   violation and is reported as one even if the verdicts are
>   unaffected.

## Finding 6: executor death mid-pilot (AMEND)

### Verdict

AMEND. The plan has no restart rule at all. The fcc K2 lesson in
the redesign (section 3, point 4) is exactly this failure: K2 died
twice with zero output and an empty directory, and the retry log
only said it was drafting. A 12-run pilot with one executor and no
death rule will repeat it, and without a pre-registered rule any
ad-hoc restart would be indistinguishable from cherry-picking runs.

### The rule (pre-registered before run 1)

Liveness: the executor emits a progress marker at every run start
and every run end, in the pilot log. The watchdog polls every 5 min
and reports to Muse directly, per redesign section 5.4. A run with
a start marker and no end marker within 30 minutes is declared
DEAD. The 30-minute figure is a death declaration for runs whose
measured predecessors run in seconds to a few minutes (Pick 1 arms
ran 17-37s; the scripted Case B floor is 3.6s); it is not a
performance timeout and it is not a p95 timeout, which the redesign
correctly says must be measured first, not invented.

What happens to the dead run: the run-id is voided. Its partial
evidence stays in its directory, marked DEAD, and is never counted
in n=3, never checked, never unblinded. The replacement run gets a
NEW random run-id, a new manifest entry appended by Muse (the hash
is re-published), and starts from a fresh browser session with
storage cleared and the fixture reloaded. It is a fresh run, never
a resume of the dead run's state.

Does restarting void the pre-registration? No, provided all four
conditions hold: (a) this restart rule is in the frozen plan before
run 1; (b) the replacement executor is briefed identically from the
same runbook and receives no interim results; (c) the dead run is
excluded by death, not by outcome: the exclusion decision is made
from the missing end marker alone, without looking at any partial
result; (d) completed runs stand and are never re-run. What WOULD
void the pre-registration: replacing the executor after showing it
interim results, re-running a completed run, changing the runbook
mid-pilot, or excluding a run because its partial result looked bad.

Second death: if the executor dies twice, the pilot PAUSES. Muse
reviews, records the cause, and decides in writing whether to
appoint a new executor under the same rule or stop the pilot. A
third executor is never spawned silently.

### Exact amendment text (add as new plan section 9c)

> ## 9c. Executor death and restart rule (pre-registered)
>
> - Liveness: the executor writes a progress marker at every run
>   start and every run end in the pilot log. The watchdog polls
>   every 5 min and reports to Muse directly. A run with a start
>   marker and no end marker within 30 min is declared DEAD by
>   Muse. The 30-min figure is a death declaration, not a
>   performance bar and not a p95 timeout.
> - A dead run's run-id is voided. Its partial evidence stays in
>   its directory marked DEAD, is never counted in n=3, never
>   checked, and never unblinded.
> - The replacement run uses a NEW random run-id, a new manifest
>   entry appended by Muse with the hash re-published, and starts
>   from a fresh browser session with storage cleared and the
>   fixture reloaded. It is a fresh run, never a resume of the dead
>   run's state.
> - Completed runs stand and are never re-run. The replacement
>   executor is briefed identically from the same runbook and
>   receives no interim results, no checker verdicts, and no GO-bar
>   knowledge (see section 3).
> - Restarting under this rule does not void the pre-registration,
>   because the rule, the exclusion-by-death criterion, and the
>   no-interim-results condition are all frozen before run 1.
>   Excluding a run for its partial result, re-running a completed
>   run, or changing the runbook mid-pilot DOES void the
>   pre-registration and requires a new freeze.
> - Second death: if the executor dies twice, the pilot PAUSES.
>   Muse reviews, records the cause, and decides in writing
>   whether to appoint a new executor under this rule or stop the
>   pilot. No third executor is spawned silently.

## Dissent considered

- Different executor per arm. Considered, rejected: executor skill
  variance at n=3 confounds the arm effect more than within-executor
  learning does under alternation with no feedback.
- Washout task between arms. Considered, rejected: it does not clear
  task-specific learning (wrong-formula location, fixed values) and
  adds a fatigue confound.
- Log normalization to preserve a single-stage checker. Considered,
  rejected: tool_calls and wall_ms are the effect under test, so any
  faithful metric computation leaks the arm. Two stages (blind
  verdict on DOM plus screenshot, unblinded metrics after verdicts
  lock) is the fix.
- Committing the sealed manifest to the repo. Considered, rejected:
  any repo reader, including the executor, could open it. The
  manifest lives outside the repo; only its sha256 is published
  before run 1.
- Restart voids pre-registration. Considered, rejected with
  conditions: a restart under a rule frozen before run 1, with
  exclusion by death (not outcome) and no interim results shown to
  the replacement, preserves the registration. The voiding cases
  are named explicitly in section 9c.
- n=3 adequacy and the 30% bar. Out of scope for structure; that is
  Council C (measurement). This review notes only that the restart
  rule preserves n=3 per arm per case by replacing, not by shrinking.
- Chromium instead of Zen. Out of scope for structure; that is
  Council A (performance) and the pilot plan's own open question 3.
  This review takes the Chromium isolation as given and judges only
  whether the structure around it holds.
- A technical seal (encryption with a key held by Muse). Considered,
  not required: on this setup the custodian holds the only copy
  outside the repo, and a passphrase would add a key-management
  failure mode (lost key voids the pilot) for no added separation.
  If Muse prefers encryption, the rule still holds with the
  ciphertext in place of the plaintext file and the same hash
  publication; that change needs no re-freeze of thresholds.

## What must happen before any live run (checklist)

1. Write and commit runbook.md, run-log-schema.md, check_run.py.
2. Freeze the f01 md5 (2b6eda97036af51510b7eefe6d36dd93) in the plan.
3. Build the known-good and known-bad checker self-test directories
   and commit their outputs.
4. Run and commit the Layer-1 preflight unit test output.
5. Write the Layer-2 probe programs.
6. Apply the amendments above to the pilot plan (sections 3, 6, 8, 9,
   plus new sections 9b and 9c), freeze the plan, and record its
   commit hash in the pilot log.
7. Muse pre-generates the 12 run-ids, writes the manifest outside
   the repo, and publishes only its sha256.
8. Muse issues the written, timestamped resume order naming the 12
   run-ids.

Until all eight hold, the pilot is not ready to run. None of the eight
requires redesign, and none requires new infrastructure beyond files
that the plan already assumes exist.

## Sources

- improvements/worker-a1-pilot-plan.md (DRAFT, read 2026-11-21).
- improvements/working-structure-redesign-20261121.md sections 5.1-5.4
  (roles, handoffs, evidence contract, spawn/kill rules), read 2026-11-21.
- improvements/a1-code-exec-dom-design.md sections 5-7 (trace budget,
  sandbox, risks and guards), read 2026-11-21.
- Repo state verified by direct listing 2026-11-21: runbook.md,
  run-log-schema.md, check_run.py, runs/ all absent; pick4 md5
  91b2f92945c167306a13ae32977a9bf3 matches the plan; f01 md5
  2b6eda97036af51510b7eefe6d36dd93 computed during this review.
- Redesign section 3 point 4 (fcc K2 silent deaths) for the death rule.
- Pick 1 numbers (wall 37.54s to 17.59s, calls 5 to 2) and D1 think
  (99.2s to 20.7s) as stated in the design file, used only to size the
  30-minute death declaration, not as a speedup claim.
