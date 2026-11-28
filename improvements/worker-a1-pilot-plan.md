# A1 narrow pilot plan (FROZEN, 2026-11-21)

- Owner: the repository owner. Pilot worker: Worker A1 (Muse).
- Proposal: improvements/working-structure-redesign-20261121.md section 6,
  commit fb00973. Owner approved 2026-11-21 18:17, "follow it as Lauren Tan
  advises".
- Design: improvements/a1-code-exec-dom-design.md (2026-11-19).
- Status: FROZEN. Thresholds below were debated by Council 1 (performance),
  Council 2 (structure), Council 3 (measurement), and the Redteam, and
  resolved by Worker A1 synthesis in section 11. No live arm has run.
  No speedup is claimed.
- Freeze commit: recorded in tests/realistic/a1-pilot/FREEZE.md and in
  improvements/worker-a1-pilot-log.md. No threshold, case, cap, run order,
  or checker rule changes after that commit without an AMENDMENT commit
  under section 5.5 rules (see section 9, freeze mechanism).
- Sequencing: ALL prep now. NO live arm runs until Muse gives the resume
  order (owner away from keyboard). Non-driving prep only.

## 1. Question

Does batching actions per observation inside code-exec programs cut total
wall time on deterministic short tasks, versus the step-by-step model loop,
without losing pass rate or adding recovery steps?

Lever under test: ONE observation yields MANY actions (code-exec program
absorbs observe-act-branch-retry locally, zero model round trips in between).
Nothing else changes between arms: same fixture, same browser, same task,
same executor, same checker. In particular the interaction path is the same
in both arms: both arms use DOM observe and DOM act by ref (section 3).
The pilot does not test DOM refs against mouse clicks; that is a different
experiment.

## 2. Cases (frozen)

### Case A: Pick 4 fixture (short, 1 action)

- Fixture: tests/realistic/a1-pilot/fixtures/pick4-fixture.html
  (md5 91b2f92945c167306a13ae32977a9bf3, 719 bytes, byte-identical to the
  18/11 original; laptop /tmp copy lost, VM copy is the survivor).
- Task: open the fixture in the managed browser, click the "Show result"
  button, verify #result contains "pick4-ok". Leave #name empty, so the
  expected end state is "pick4-ok hello stranger".
- Why this case: the D1 task from Pick 4 already proved the DOM path works
  (click by ref + DOM assert, 0 browser screenshots). It is the smallest
  deterministic task that exercises observe-click-assert. It is a
  feasibility gate and a cheap tripwire, not a wall gate (section 5).

### Case B: f01 spreadsheet (long, 26 spec steps)

- Spec: tests/realistic/fcc-k/test-01-spreadsheet-formula.md.
- Fixture: tests/realistic/fcc-k/fixtures/test-01-spreadsheet.html
  (md5 2b6eda97036af51510b7eefe6d36dd93, last changed at commit cbbb748,
  which fixed the fixture so formulas are case-insensitive).
- Task: the spec's 26 steps exactly: enter 5 sales rows, write SUM /
  AVERAGE / COUNT formulas, spot the wrong COUNT formula returning text,
  fix it to COUNTA, confirm the six end-state cells E2=540000, E3=574000,
  E4=750000, E5=1864000, E6=621333, E7=3. (The plan's earlier draft named
  only three cells; the checker enforces six, matching the spec expected
  end state. E6 = 621333 exactly because the fixture rounds AVERAGE with
  Math.round.)
- Step counts, three ways (all recorded, none hidden): 26 spec steps,
  40+ low-level click/type/read actions, 71 steps in Worker U's scripted
  DOM run (tests/realistic/live-run-u-20261121.jsonl, f01 PASS, 3,604 ms
  per tests/realistic/run-u-all-20261121.log, NOT per the jsonl, whose
  rows sum to 2,960.7 ms). The 3,604 ms figure is the scripted floor, not
  a target: no model loop can touch it, and it is never compared against
  a CODE arm wall. The proposal's "70 scripted steps" means the 71-step
  scripted run.
- Why this case: the hard case. It has a mid-task diagnosis step (the
  wrong formula) that the program must branch on locally, which is
  exactly what batching claims to absorb.
- Fixture-fix rule: if the f01 fixture is fixed after the freeze, the
  freeze is broken: the fixture checksum is re-verified and the freeze
  is re-recorded before the first live run. No live run starts on a
  fixture whose checksum differs from the frozen value.

### Case B program-length preflight (measured, not assumed)

Worker A1 drafted the Case B program on the VM with no browser (2026-11-21)
and counted chars against the 8192 cap (Council 1 point 3, Redteam A9):

- Loop/table shape (one program, 18 cell values in a table, 4 DOM actions
  per value in chunks of 8 values = 32 actions per dom_act, E7 diagnosis
  branch, COUNTA fix, six final dom_asserts, final desktop observe):
  2,453 chars, 70.1 percent headroom under 8192, about 18 of 32 API calls.
- Fully unrolled shape (one dom_act per cell, ref map rebuilt each time):
  8,603 chars, 411 over the cap, about 31 of 32 API calls. The cap is
  satisfiable only in a compact shape.
- Conclusion: no cap reversion (the draft is well under 2 times 8192, so
  Council 1's reversion condition does not trigger). The runbook states
  the 8192 cap upfront; a first program submission that exceeds the cap
  counts as a recovery step (a re-submission). The draft program text
  itself was DELETED after measurement and never entered the repo or the
  runbook (Redteam A1: no program text anywhere the executor could copy).
  Only the counts above are recorded.

### Held-out task (phase 2, drawn and sealed BEFORE run 1)

- One realistic task, run by an INDEPENDENT runner (never the pilot
  executor), using the GO-arm method only if the pilot goes GO, with BOTH
  arms at n=1 each (exploratory, not confirmatory).
- Pool (frozen): agy-q2 test-06 through test-10 only. The draft pool
  member "clone1-batch3 t-series" does not exist anywhere in the repo
  (Redteam H1) and is DROPPED. It returns only with paths, test IDs, and
  fixture checksums committed.
- Live validation (before the draw): each pool candidate is live-run once
  with the scripted runner (not the GO arm, not the executor). Only
  candidates that pass live as specced stay in the pool. A candidate that
  fails live is a fixture bug to fix, not a held-out task. The agy-q2 pool
  was validated by simulation only (10/10 simulated), and the fcc-k
  precedent shows simulation passes while live runs go 0/10 on
  fixture/spec defects.
- Draw: Muse draws one task from the validated pool by a recorded random
  draw, seals it in the manifest, and opens it only after the pilot
  verdict. Choosing after the verdict is forbidden (Redteam H2).
- Runner: briefed with the task spec and the GO-arm procedure only, no
  pilot numbers, no plan reference, no mention of the pilot verdict.
  The runner's transcript is checked for reads of the pilot plan and the
  pilot run directories; any such read voids the held-out run (Redteam H3).
- Held-out status here means "not used in pilot prep and not selected
  after the verdict", not "never seen by any agent" (Redteam H6). The
  held-out run is labeled "feasibility check only, not a speedup
  confirmation" and is never cited as confirmation of the 30 percent
  claim (Redteam H4).

## 3. Arms

### Arm CODE: code-exec program

- The executor submits programs through the code-exec path
  (scripts/code_exec.py, DOM ops dom_start/dom_tabs/dom_observe/dom_act/
  dom_assert, unchanged from the design file).
- Case A program: composed live by the executor for the frozen fixture
  path (tests/realistic/a1-pilot/fixtures/pick4-fixture.html served over
  the local HTTP server). The D1 program text from the design file is NOT
  in the runbook and must not be copied: the executor composes the program
  fresh inside the timed run (Redteam A1).
- Case B program: composed live by the executor, covering all 26 steps
  with local branching on the wrong-formula diagnosis (re-read E7, if text
  then replace with COUNTA, re-read). It may chain several dom_act calls
  inside the program.
- Off-clock authorship rule (Redteam A1, frozen): the runbook contains NO
  program text, no pseudocode, and no ref lists. The executor composes
  each program live inside the timed run, with the session started BEFORE
  any program text is written. The executor's transcript must show the
  program's first draft appearing after session start. Any program text
  written before session start voids the run.
- Caps (pre-registered): each program at most 8192 chars (the interpreter
  MAX_PROGRAM_CHARS, hard cap). Case A: at most 1 planned program call
  plus at most 1 recovery call. Case B: at most 2 planned program calls
  plus at most 1 recovery call (Council 1 point 3). A recovery call is a
  program call issued only after a previous program returned ok false or
  a failed assert with completed 0 or no effect, and it counts as 1
  recovery step against the section 5 recovery gate. Planned split points
  are frozen in the runbook before the first live run: which spec steps
  each planned program covers. No adaptive re-splitting mid-run except
  through the single recovery call. Program char count per call, program
  call count, and planned versus recovery label are reported per run. If
  a case needs more planned calls than the cap, that is recorded as a
  design miss, not worked around by editing the cap.
- Program wall budget (frozen, Redteam B6): Case A default 30s, Case B
  max 60s, stated explicitly in the runbook. A program killed mid-run by
  the wall budget is FAIL, not VOID, unless the budget itself is the thing
  under test (it is not in this pilot).
- Think-before-program-call is timed for EACH program call, not only the
  first (Council 1 point 6). Definition: elapsed wall time from the end
  of the previous model turn (or from task start for the first call) to
  the submit timestamp of that program call, taken from the timed run log.
  The executor does no exploratory observe between the end of the previous
  turn and the program submit except the observes the program itself
  performs; any exploratory observe before a program call is logged as its
  own run-log line and its think counts toward that call. Report per run:
  think before each program call, the sum over all program calls (total
  composition think), and the largest single call. Report finish think
  separately: elapsed from verified end state to session finish. Wall time
  ends at verified end state (DOM assert pass), so finish think is OUTSIDE
  wall and is reported as a diagnostic only.

### Arm STEP: step-by-step model loop

- The executor drives through the broker one tool call per step: observe,
  act, observe, act, exactly as the Pick 1 / Pick 4 arm-1 baselines did.
  No code-exec, no batching, no program calls.
- Case A: windows, observe, navigate act (Ctrl+L + type URL + Enter),
  observe, tabs, DOM observe, DOM act click, DOM assert, close. One model
  turn per call.
- Case B: the 26 spec steps, one model turn per action, using
  dom_observe/dom_act per step with the SAME refs the CODE program uses
  (Redteam A4, frozen): click the cell BUTTON by ref to select the cell,
  fill the #typed input by ref, click the "type" button by ref, click the
  "Enter" button by ref. The spec's "click cell" language is translated to
  the button path explicitly, identically for both arms. Clicking a td
  directly selects nothing (the fixture has no click handler on td
  elements); the STEP arm must not use the mouse-click path. If STEP used
  mouse clicks and CODE used DOM refs, the arms would differ in TWO levers
  (batching AND interaction path) and a CODE win would prove nothing about
  batching. Re-observing after each batch of edits as the spec requires.

### Common to both arms

- Browser: managed Chromium via the existing code-exec DOM path (CDP),
  exactly as D1 did. NOT Zen. Reason: the pilot tests the batching lever,
  not Zen control. Zen has its own open failure modes (hidden-body
  incident 17:52 21/11, BiDi click false-ok) that would confound the
  lever. Transfer to Zen is a follow-up probe, not this pilot (section 10).
- Run window: task start (session start submit) to verified end state,
  same as Pick 1 / Pick 4 measurement. Finish-confirmation think is
  OUTSIDE wall (section 3, CODE arm). The runbook bounds finish to one
  confirmation turn.
- Executor: ONE fresh executor agent runs both arms (same model, same
  harness), following the written runbook
  (tests/realistic/a1-pilot/runbook.md) and nothing else. The executor
  is not Worker A1 and not the checker. Fresh means the executor has
  read the runbook only: it has not read the pilot plan, the design
  file, or any prior run report. The runbook contains the procedure
  for each arm and no numbers, no hypothesis, and no prior results.
  (Two executors were considered and rejected: executor skill variance
  at n=3 confounds the arm effect more than within-executor learning
  does under alternation with no feedback. Council 1 point 4 dissent,
  Council 2 Finding 1, section 11 D3.)
- The executor receives one run at a time: run-id plus the arm procedure
  for that run, nothing else. After each run the executor reports only
  that the run finished and where its evidence directory is; it receives
  no feedback before the next run. The executor must NOT know:
  (a) the hypothesis direction (which arm is expected to be faster);
  (b) the GO bar (the 30% figure, the pass-rate rule, the recovery
  rule, the composition-think rule); (c) the wall time, pass/fail, or
  any metric of any completed run; (d) any checker verdict; (e) the
  sealed manifest, its location, or any run-id to arm mapping beyond
  the run it is currently doing; (f) the held-out task identity.
  The executor DOES know the procedure of the arm it is currently
  running; executor blinding to the arm is impossible and is not
  claimed. Only checker blinding is claimed. (Council 2 Finding 1.)
- The executor's repo access during runs excludes improvements/
  (enforced by the spawn brief). After the pilot, the executor's
  transcript is checked for reads of the pilot plan; any such read
  voids the affected runs (Redteam A3 minimum control).

## 4. Run order and n

- n=3 per arm per case. Total 12 runs (2 cases x 2 arms x 3).
- Run order is stratified-randomized per pair, not STEP-first on both
  cases (section 11 D2). Within each case the 3 run-pairs are assigned
  start arms by random draw with exactly 2 pairs starting on one arm
  and 1 pair starting on the other, so learning effects split across
  arms inside each case instead of always favoring CODE. The assignment
  is drawn by Muse before run 1, sealed in the manifest, and issued one
  run at a time. The first run of each case is reported separately as
  the least-contaminated comparison, because only the first run in a
  case has no prior exposure to that case by the same executor.
  The draft plan's claim that STEP-first is conservative is withdrawn:
  landing warmup on the control arm favours the hypothesis, it does not
  protect against it (Council 1 point 4, Redteam A2).
- One run at a time. Broker SOLO (the Pick 4 arm-1 run-1 lesson:
  parallel workers held the single-owner broker and 0/4 runs blocked).
- Between runs: fresh browser session, fresh fixture state (storage
  cleared, fixture reloaded), desktop verified clean. Reset lines go in
  setup-log.jsonl in the run directory, never in run-log.jsonl (Council 3
  3.4 item 1). Wall excludes reset time.
- Per-case run caps (Council 3 3.4 item 6): Case A 15 min, Case B 60 min.
  A run that exceeds its cap is STOPPED at the cap, run_end is written
  with reason timeout and ts at the kill instant, and the run is FAIL.
  A timed-out run wall is censored data: its true wall is greater than
  the kill-time wall, not equal to it. In the verdict table it is printed
  with a ">" flag. If the median of an arm is itself a timed-out run,
  that median is reported as a lower bound and the GO bar cannot pass on
  that case; the case verdict is INCONCLUSIVE, not GO. (The runbook's old
  30-minute cap is replaced; Council C estimates f01 at about 40 minutes
  hand-driven per run, extrapolated NOT measured, so a 30-minute cap
  would manufacture timeouts in the STEP arm.)
- run_sequence: the run's position in the full 12-run sequence (1-12),
  recorded in run_start detail, so a learning trend in wall time across
  the sequence is visible at analysis time. The unblinding step reports
  wall time by run sequence as well as by arm (Council 2 Finding 1).

## 5. GO / NO-GO bar (PRE-REGISTERED, frozen before any run)

GO (pilot GO: proceed to the confirmatory run, not adoption) only if ALL
of these hold:

Case B (f01), all four conditions:
1. Median wall time (CODE arm) at or below 0.70 times median wall time
   (STEP arm). Medians are medians of 3 runs. All six walls per case are
   printed in the verdict table; a verdict that reports medians without
   the six walls is incomplete.
2. Pass rate (CODE) equal to or better than pass rate (STEP), counted as
   passes out of 3, with the failure reason of every failed run printed
   alongside its count.
3. Total recovery steps across the 3 runs (CODE) not higher than total
   recovery steps across the 3 runs (STEP). Recovery steps are defined in
   section 5A. The per-run counts are printed alongside the totals.
4. Total composition think (CODE, sum over all program calls) is less
   than STEP median total think for that case (Council 1 point 6).
   Batching claims to cut think by cutting turns; if total think does not
   fall, the wall win was bought elsewhere and the verdict is NO-GO on the
   lever, even if wall passes. If total composition think exceeds 50
   percent of CODE median wall, that is flagged in the report even when
   condition 4 passes.

Case A (Pick 4), feasibility gate (Council 1 point 1, Redteam B1/C4):
pass rate (CODE) equal or better than pass rate (STEP), recovery steps
(CODE) not higher than recovery steps (STEP) in total across the 3 runs,
and total composition think (CODE) less than STEP median total think.
Its median wall time is reported as a diagnostic only, not a gate: the
batchable DOM loop in D1 was 20.7s of think inside a 293.401s wall (about
7 percent), so a 30 percent cut of total wall is structurally unreachable
on this case, and the case cannot confirm a 30 percent win (Council 3
section 1.2). This deviates from the proposal's "median wall down at
least 30% per case" bar, deliberately and for the stated reason.

If Case B passes all four of its conditions and Case A passes its
feasibility gate, the verdict is GO. If Case B fails any condition, the
verdict is NO-GO regardless of Case A. If Case A fails its feasibility
gate, the verdict is NO-GO regardless of Case B, because the lever does
not work at all. A partial outcome is reported per case in all cases.

Additional rules (Council 1 point 2):
- 2-of-3 rule: at least 2 of the 3 CODE runs in Case B are individually
  at least 20 percent below the STEP median wall for that case. A median
  that passes only because of one fast run does not pass.
- Dispersion: for each arm-case cell of 3 runs, report (max minus min)
  divided by the median. If that ratio exceeds 50 percent in any cell,
  the verdict for that case is INCONCLUSIVE, not GO and not NO-GO,
  regardless of the median. Report all 12 runs, including failures,
  timeouts, and kills, with no run silently dropped.
- Flagged runs are flagged, not deleted. A run is flagged if it contains
  any of: session death and restart, broker contention, a stale-snapshot
  refusal, or an extra verification act not in the runbook. Flagged runs
  stay in the median. If 2 or more runs in one arm-case cell are flagged,
  the verdict for that case is INCONCLUSIVE, not GO.
- INCONCLUSIVE is a third outcome. On INCONCLUSIVE, Worker A1 reports
  the noise source plainly and the pilot is re-run after the noise source
  is fixed, it is not re-run unchanged hoping for a cleaner draw.

Robustness check (mandatory reporting, NOT a gate, Council 3 section 1):
for each case, check whether every CODE run wall is at or below the STEP
median wall. Report PASS or FAIL per case. A GO with the robustness check
passed on both cases is labeled GO, HIGH CONFIDENCE. A GO with the
robustness check failed on any case is labeled GO, LOW CONFIDENCE, and
the confirmatory run for that case uses double the n it would otherwise
use. A GO, LOW CONFIDENCE is never cited as evidence of a 30% effect,
only as a proceed signal.

Detection limit (frozen, read before interpreting any verdict): at n=3,
this pilot is powered to detect a 50% wall cut (joint both-cases power
about 58 to 93% in the lognormal model at sigma 0.2 to 0.5), not a 30%
cut. A true exactly-30% effect passes the median bar about 50% of the
time per case and about 25% of the time on both cases. A NO-GO therefore
means "not proven at pilot scale", never "batching does not work". A GO
means "proceed to the confirmatory run", never "a 30% speedup is proven".
The confirmatory run sizes n from the pilot measured within-arm spread,
and its bar sits below the effect it is powered to detect. (Council 3
section 1.3. Model calculation, not measured fact: lognormal walls,
100,000 to 200,000 simulated trials, seed 20261121.)

Diagnostics reported alongside every verdict, never gated on: mean wall
per arm, min wall per arm, geometric mean wall ratio, think-before-each-
program-call per CODE run, gap ms (wall minus summed service ms) per run,
and every run wall flagged incident-suspect when it exceeds twice its arm
median, with the reason taken from its log.

Actions-per-observation is reported as a diagnostic, never as a gate.

## 5A. Frozen counting definitions (Council 3 section 4.2)

One definition, in the plan, the schema file, and the runbook, no paraphrase.

Step: one logged action at action level. Each DOM action (click, fill,
assert, navigate, observe) is one step, whether issued by the model
(STEP arm) or by a program (CODE arm). A program that executes 5 DOM
actions logs 5 act lines, one per action, plus its program_submit line.
A model turn that issues 4 tool calls logs 4 tool_call lines. Counting
is at action level in both arms, so the counts are comparable. The CODE
program must emit one act line per DOM action it executes, including
retries, with the same op vocabulary as the STEP arm. If the program
retries internally without logging, gate 3 is void. The preflight probe
(section 7) must verify that a program logs its internal retries, not
only that it preflights correctly.

Recovery step: one corrective action taken because a preceding action
returned ok:false, or because an observation or assert showed the state
diverging from the intended state. The original failed action does NOT
count as recovery. The diagnostic re-observe after a failure counts.
The re-try of the failed action counts. A state repair counts. A
recovery step is logged exactly once, as one line: op retry if it
repeats the same action (same intent, same target) after a refusal or
failure, op recovery otherwise. Recovery steps for the gate (plan
section 5, condition 3) equal count(retry lines) plus count(recovery
lines), summed across the 3 runs per case per arm. One corrective action
is exactly one line, or the gate double counts.

Planned branch (NOT recovery): a step the runbook or spec prescribes
conditional on observed state. In Case B, the wrong-formula diagnosis
is a planned branch: re-read E7, and if it holds text, replace COUNT
with COUNTA and re-read. Those steps are forward steps, logged as act
lines, never as recovery. If the same COUNTA fix has to be attempted a
second time because the first attempt failed, the second attempt IS
recovery. The runbook marks every planned branch in the case procedure
before run 1, so the checker and the executor agree on which steps are
planned.

Refusal: one request that returns an error without executing any action.
Completed 0 with an error present. Examples from Pick 4: stale
observation (observation older than 90s), sequence_gap, task_stopped,
unsupported_command, invalid_lease. A refusal is logged as one refusal
line with detail.reason carrying the exact error text. An action that
executed and then produced the wrong state is NOT a refusal; it is a
failure, and its correction is recovery.

Retry: one repeated attempt of the same action (same intent, same
target) after a refusal or failure. Logged as op retry, detail
after_refusal carrying the exact error text of the refusal or failure
it follows. A retry is also a recovery step for gate purposes (see
above). A retry that itself fails and is tried a third time logs a
second retry line.

Misclick: one click or fill action that executed on an element other
than the one the step intended. Intended means the element named in the
runbook step (STEP arm) or the element the program selected as its
target (CODE arm). Every act line for a click or fill carries
detail.target_ref (the ref acted on) and detail.intended (the intended
element). A misclick is logged as one misclick line with detail
{intended, actual}. The checker counts misclick lines. Limitation,
stated in every verdict: a misclick the executor never detects is never
logged, so a run with zero misclick lines is reported as "none
detected", never as "0 misclicks". Until act lines carry target_ref and
intended, misclicks are UNMEASURED, not zero.

Session death: the broker session or the browser session terminates
before the verified end state, so the run cannot continue without a
restart. Logged as one session_death line with detail {what:
"browser" or "broker", error: exact error text}. One restart per run is
allowed: the death is counted, the restart steps are recovery steps,
and wall time keeps running. A second death in the same run ends the
run as FAIL with run_end reason failed. A restart that itself fails to
start ends the pilot: STOP, report to Muse, do not start the next run.
(This replaces runbook section 7 "STOP on death". A death is a cost to
be counted, not a reason to waste a pilot, but a second death is a
harness failure, not a lever signal.)

Pass: the blinded checker finds the frozen end state in end-state.json
(Case A: result_text contains "pick4-ok". Case B: E2=540000, E3=574000,
E4=750000, E5=1864000, E6=621333, E7=3) and verify.png exists and is
non-empty, and the run log parses and starts with run_start and ends
with run_end. A run that reaches the end state by writing fixture
internals directly (setting state rather than acting through the UI or
DOM ops) is FAIL by fabrication; the program text in commands.txt is
the evidence, checked at unblinding by Muse, not by the checker.

Fail: any run that is not a pass. The run_end reason says why: failed
(wrong end state or driver failure), timeout, invalid, killed.

Timeout: wall time exceeds the per-case cap (Case A 15 min, Case B 60
min). The run is STOPPED at the cap, run_end is written with reason
timeout and ts at the kill instant, and the run is FAIL. A timed-out
run wall is censored data: its true wall is greater than the kill-time
wall, not equal to it. In the verdict table it is printed with a ">"
flag. If the median of an arm is itself a timed-out run, that median
is reported as a lower bound and the GO bar cannot pass on that case;
the case verdict is INCONCLUSIVE, not GO.

Invalid: a run voided for a cause outside the arm under test. Only
three causes qualify: (a) fixture or harness fault found after the run
(fixture md5 mismatch, wrong fixture served, broker outage affecting
both arms); (b) executor violated the runbook (copied a program
verbatim, used the wrong arm procedure, opened the sealed manifest);
(c) run evidence lost through no fault of the arm (log file destroyed).
An INVALID run is logged with reason invalid, preserved, and re-run
once. Two invalidations of the same case-arm pair stop that pair and
the pair is UNMEASURED. A run that fails because the arm did the task
wrong is FAIL, not INVALID.

Incident-suspect run: a run whose wall exceeds twice its arm median.
Flagged in the verdict with the reason taken from its log (for example
windows-retry think, extra verification rounds, session death). The
flag is diagnostic; the run stays in the median.

## 6. Blinded checker (two stages)

Each run writes evidence to runs/<run-id>/ where run-id is a random
8-hex string assigned by Muse before run 1 (see section 9b). The run
manifest (arm label, case, run number) is sealed under the custody rule
in section 9b and the checker never opens it.

Stage 1, blind verdict. The checker is
tests/realistic/a1-pilot/check_run.py. Input: one run directory, given
as a single path. It reads ONLY the end-state DOM dump and the final
verification screenshot in that directory, and outputs ONLY PASS/FAIL
plus the end-state values it checked. It reads no timed log, no
transcript, no timestamps, no run number, and no directory listing
across runs. It contains no code path that opens the manifest; a grep
for "manifest" in check_run.py must return nothing, verified before
run 1. Stage 1 runs once per run directory, and its verdict files are
committed before unblinding. Checker outputs are sealed per run until
unblinding: the checker writes its full output to
runs/<run-id>/check-output-sealed.json, which no human reads before
unblinding. This is required because the output leaks the arm
(program_calls above 0 implies CODE), so reading it early unblinds the
reader even though the script itself does not branch on arm.
(Council 3 section 5.3 item 5, section 6.4.)

Stage 2, unblinded metrics. Only after ALL 12 Stage 1 verdicts are
committed, the metrics script runs over the full timed logs and
transcripts, computing the six metrics plus per-run fields (section 8).
Stage 2 is explicitly unblinded: it runs after the verdicts are locked,
so metric computation cannot influence any verdict. Wall time by run
sequence is reported alongside wall time by arm (Council 2 Finding 1).
Program_submit framing lines are excluded from the checker metric input
(they are counted only for the program caps), so the two arms' logs
differ in counts, not in kinds (Council 3 section 6.4).

Unblinding happens only after ALL 12 runs are checked (Stage 1 verdicts
committed), in a separate step that joins run-id to arm from the sealed
manifest, done by Muse (not the checker, not the executor, not Worker A1).
See section 9b for custody.

Evidence per run: timed run log (JSONL, schema section 8), end-state DOM
dump (final cell values / #result text), final verification screenshot,
exact commands run, git HEAD of the repo at run start, relay
started_git_head plus the values of CU_CODE_EXEC and CU_PICK4_FASTPATH,
broker-status output proving SOLO at run start, and md5 of both fixtures
at run start. All eight items are written into runs/<run-id>/ before the
run is counted as complete. A run missing any item is not counted in n=3;
it is recorded as INCOMPLETE and re-run under a new run-id (see the
restart rule, section 9c).

Independent checker re-run. After Stage 1 verdicts are committed, an
independent runner (not Worker A1, not the executor) re-runs check_run.py
over all 12 run directories and confirms identical verdicts. Any
discrepancy stops unblinding until the cause is found and recorded.
(Council 2 Finding 3.)

## 7. Preflight test (the safety gate)

The design file requires testing the preflight guarantee deliberately
with a bad ref mid-list across every action type used. Two layers:

- Layer 1, interpreter (VM, no browser, DONE): unit test with a
  FakeDomBackend proving _validate_dom_actions rejects a bad ref before
  any backend call, for each ref-taking action type used in the pilot
  (click, fill/set_value, assert). A bad ref anywhere in the list means
  the whole batch is refused with completed: 0. Test:
  tests/test_a1_preflight.py, 7/7 PASS in 0.014s, committed.
- Layer 2, adapter (live browser, AT RESUME, before any pilot arm): a
  probe program that issues a real dom_act with a bad ref in the middle
  of the list against the real fixture and verifies completed: 0 and zero
  DOM effects (cell values / #result unchanged). One probe per ref-taking
  action type the Case B program uses: click, fill, set_value, assert.
  Plus Probe 5: a program that retries internally must produce retry
  lines in the run log (section 5A). Probe programs:
  tests/realistic/a1-pilot/preflight-probe.md.

A probe failure triggers STOP, FIX THE ADAPTER, RE-PROBE, not a safety
NO-GO (Redteam B4). A partial effect on a probe proves the ADAPTER
preflight or its interpreter mirror is wrong, not that batching is a bad
lever. Only a partial effect that survives a fix attempt, or a partial
effect the owner explicitly accepts as unfixable, becomes a safety NO-GO.
Triage checklist before any probe result is recorded: confirm the fixture
is loaded, the snapshot is fresh (under 90s), the browser is up, and the
ref namespace is correct. A probe that fails for a setup reason is
re-run after the setup is fixed, not recorded as a safety result.

## 8. Metrics (run-log JSONL schema, per run)

Six metrics from the proposal, plus per-run fields. Computed by script
from the run log, never self-reported by the executor. The checker counts
tool_call lines the executor writes itself, which is executor self-report;
the checker flags a run with act lines but zero tool_call lines as a
logging failure (Council 3 section 6.2 item i).

1. wall_ms: task start to verified end state (headline). run_start ts is
   the task start instant; run_end ts is the verified end state instant.
   Finish think is outside wall.
2. tool_calls: model tool calls in the run, counted from tool_call lines
   in the log.
3. tokens_in / tokens_out: EXPECTED UNMEASURED. No evidence the executor
   session exposes a per-task token count. If the tokens lines never
   appear, the verdict says UNMEASURED with the reason "session exposes
   no per-task count". Never estimated, never 0, never a calls-times-
   constant multiplication.
4. observation service cost: mean elapsed_ms of observe lines, split by
   (kind, image), plus gap-before ms per observe kind (mean of ts
   difference from the previous metric line minus elapsed_ms of that
   line, the think plus idle before that observation; the previous
   metric line is the previous line that carries a ts and an
   elapsed_ms, framing lines such as program_submit and
   think_before_program are skipped). Until the gap-before number
   exists, the metric is labeled "observation service cost", not
   "observation cost": it measures harness service time only, not the
   think before each observation, which is the dominant cost.
5. vcr_service: verification service time divided by production service
   time (assert elapsed plus last desktop observe, over act plus observe
   elapsed). Labeled as a service-time ratio, never bare "VCR". The
   wall-time VCR of Council C 3.5 is UNMEASURED in this pilot unless the
   run carries verify_start and verify_end lines bracketing the final
   verification phase; the runbook asks the executor to log them, and the
   checker reports vcr_wall only when they are present, else UNMEASURED.
   A flag with an explanation when vcr_service exceeds 1.0, not an
   automatic verdict.
6. silence_minutes: sum of inter-line gaps over 900s. This measures log
   silence, not lack of progress, and is labeled as such until the schema
   gains a progress_marker field and the checker computes stall from
   progress coverage. A run that writes lines while making no progress
   must not be reported as having zero stall.

UNMEASURED rule (frozen): a metric that was not measured is reported as
UNMEASURED with the reason, never as 0, never as an estimate, never
silently dropped. A GO verdict may stand with UNMEASURED diagnostic
metrics (tokens, observation cost detail) only if all three gate metrics
(wall, pass rate, recovery steps) plus condition 4 (composition think)
are measured on all 12 runs. If any gate metric is UNMEASURED on any run,
the verdict for that case is INCONCLUSIVE, not GO. Every UNMEASURED metric
is listed in the verdict with the question it leaves open. For this pilot
the expected open questions are: tokens (cost effect unknown; a wall win
may be a speed-for-cost trade, and the report must say so) and
observation cost by type in the think-inclusive sense (mechanism unknown;
we do not know whether a wall win came from fewer observations or from
something else).

Per run also: pass/fail by the blinded checker, recovery steps (retry
lines plus recovery lines), refusals, misclicks (misclick_lines count
plus the misclicks field, "none detected" when the count is 0, never
"0 misclicks", until act lines carry target_ref and intended), session
deaths, retries,
program calls (CODE arm), program chars (CODE arm), think before each
program call and total composition think (CODE arm), run_sequence.
A win on wall with a rise in refusals or deaths is not a win.

Schema file: tests/realistic/a1-pilot/run-log-schema.md. Each log line:
{"ts", "run_id", "step_index", "op", "elapsed_ms", "ok",
"progress_marker", "detail", "error"}. Arm label is NEVER in the run log
(it lives only in the sealed manifest, held by Muse outside the repo).

## 9. Resume preconditions (all must hold before any live arm)

- The frozen pilot plan commit hash is recorded in the pilot log. No
  threshold, case, or cap changes after that hash. Any change voids the
  freeze and requires a new hash and a new resume check.
- Resume order: a written resume order from Muse, timestamped, in the
  pilot log. "Owner away from the keyboard" is satisfied by that order
  and by nothing else; no agent infers it from idle signals. The order
  names the 12 pre-generated run-ids.
- Broker SOLO and idle, proven by broker-status command output saved per
  run (see section 6). Zen untouched by the pilot (Chromium only);
  desktop state checked before run 1 and after run 12.
- Relay verified before run 1: started_git_head equals the repo HEAD,
  CU_CODE_EXEC=1, CU_PICK4_FASTPATH=1, from relay status output saved
  in the pilot log. Re-checked if the relay restarts mid-pilot; a restart
  with a different HEAD voids all runs after the restart point unless the
  change is recorded and the freeze is re-issued.
- Layer-1 preflight unit test run on the VM with output committed
  (FakeDomBackend, bad ref rejected before any backend call, for click,
  fill/set_value, and assert). Status: DONE, tests/test_a1_preflight.py,
  7/7 PASS in 0.014s.
- Layer-2 preflight probes pass (section 7), run by the executor at
  resume before any pilot arm, with probe evidence (completed: 0 and zero
  DOM effects) saved per probe. A probe failure triggers stop-fix-reprobe
  (section 7), not an automatic safety NO-GO.
- Pool live validation done and held-out draw sealed (section 2).
- Fixture checksums re-verified: pick4 md5
  91b2f92945c167306a13ae32977a9bf3, f01 md5
  2b6eda97036af51510b7eefe6d36dd93. Both recorded per run (see section 6).
- Run directories plus sealed manifest created under the custody rule in
  section 9b. Checker self-test matrix T1-T16 (section 9, checker trust)
  run and passing, with expected outputs committed; the matrix is reviewed
  and executed by an INDEPENDENT worker (not Worker A1, not the executor).
  Real-run cross-check: the checker run on the real Layer-2 preflight
  probe directories produces the hand-verified PASS/FAIL.
- Runbook, run-log schema, and checker exist and are committed (see
  Finding 0, closed). Executor briefed from the runbook only, under the
  no-knowledge list in section 3.
- No live arm starts until tests/realistic/a1-pilot/runbook.md,
  tests/realistic/a1-pilot/run-log-schema.md, and
  tests/realistic/a1-pilot/check_run.py all exist on branch todolist-push,
  are committed, and are named by commit hash in the pilot log. The
  runbook contains no numbers, no hypothesis, and no Pick 1 results.

### Checker trust (how the checker is verified before run 1)

The two-directory self-test (one known-good plus one known-bad run
directory) is NOT the trust gate (Council 3 section 6, BLOCK). The trust
gate is the T1-T16 matrix in tests/realistic/a1-pilot/checker-selftest/
(one command runs the whole matrix; each case is a synthetic run dir with
hand-computed expected output frozen alongside it; the checker must match
every expected value exactly, not approximately):

- T1 known-good pick4: PASS, golden metrics hand-computed.
- T2 known-bad pick4 (result_text without "pick4-ok"): FAIL, metrics
  still reported.
- T3 known-good f01 (all six cells): PASS, golden metrics hand-computed.
- T4 f01 with E7 wrong: FAIL, metrics still reported.
- T5 timeout run: log ends with run_end reason timeout, wall at the cap.
  FAIL the run AND still report metrics (wall present, not empty).
- T6 session death then FAIL: session_death line present, run_end reason
  failed. Count deaths 1 and FAIL.
- T7 missing run-log.jsonl: FAIL. Empty metrics acceptable here.
- T8 missing end-state.json with a complete log: FAIL, metrics computed
  from the log and reported.
- T9 empty verify.png: FAIL, metrics reported.
- T10 malformed JSON line: report the line number and FAIL, not crash.
- T11 arm-leak test: T1 in two versions differing only in arm-revealing
  lines (one with program_submit lines, one without). PASS/FAIL and all
  arm-neutral metrics identical across both versions.
- T12 determinism: run the checker twice on T1, byte-identical stdout.
- T13 out-of-order ts: flag a problem (ts not non-decreasing), not a
  silent negative wall.
- T14 zero observe lines: observation cost UNMEASURED, not a crash.
- T15 act lines with zero tool_call lines: flag "tool_call lines
  missing" as a problem.
- T16 unknown op value: ignore the line for metrics, not crash, and do
  not count it as a step.

Also frozen: the checker contains no reference to the manifest path
(verified by grep in the self-test run), and the self-test expected
outputs are committed in the freeze commit, so a later checker change
that alters an output is visible as a diff. The matrix is re-run after
ANY checker change, and a checker change after run 1 starts follows the
amendment procedure in the freeze mechanism below.

Synthetic dirs cover edge cases that cannot occur in a real run
(malformed JSON, missing files, out-of-order ts). The verdict-critical
cases (T1, T3 known-good; T2, T4 known-bad) are ALSO validated against
real runs: the checker run on the real Layer-2 preflight probe
directories must produce the hand-verified PASS/FAIL (Redteam C2).
Hand-written run directories are forbidden as the sole self-test input.

### Freeze mechanism

1. FREEZE.md is committed at the freeze commit. It lists, per frozen
   file, the file path and its sha256 hash, plus the GO bar in full text,
   plus the freeze commit hash itself once committed (added in a second
   commit that changes nothing else; the hashes of the frozen files must
   not change between the two).
2. Manifest lines are written by a script run by Muse, not by hand and
   not by the executor. The script pre-generates the 12 random 8-hex
   run-ids plus the sealed held-out draw, writes one line {"run_id",
   "case", "arm", "run_number", "agent", "run_sequence"} per run to the
   manifest held outside the repo, and prints only the manifest sha256.
   started_at is NOT stored in the manifest: writing it would change the
   file hash mid-pilot and break tamper detection. started_at is verified
   at unblinding from the run_start timestamps in the run logs.
   Hand-written manifest lines are forbidden.
3. The unblinding step is a separate script, run by Muse only after all
   12 runs are checked. It verifies: every run dir id appears exactly
   once in the manifest; run_number runs 1 to 3 per case-arm with no
   gaps; started_at is non-decreasing in run order; the manifest has
   exactly 12 lines. Only then does it join run-id to arm and compute
   the arm medians. The join output is a new file, never an edit to the
   manifest.
4. Run dirs are immutable after run_end. Any correction goes in a
   separate amendments file, never by editing run-log.jsonl,
   end-state.json, or verify.png. check_run.py contains no reference to
   the manifest path (verified by grep in the self-test), so the checker
   cannot open it even by accident.
5. Checker outputs are sealed per run until unblinding (section 6).

What counts as a violation (frozen list):
- Changing the GO bar, the case list, the fixture files, the program
  caps, the run caps, the run order, or the checker verdict rules after
  run 1 starts.
- Editing any frozen file without an AMENDMENT commit that names the
  file, the change, the reason, and whether any completed run is
  affected.
- Opening runs/manifest-sealed.jsonl after writing it, by the executor
  or the checker, before all 12 runs are checked.
- Reading a sealed checker output before unblinding.
- Re-running a failed run and replacing it. The original stays, marked
  FAIL or INVALID with its reason, and the re-run is a new run only when
  the run was INVALID under section 5A.
- Editing a run dir after its run_end.
- Changing the checker to reclassify a run after seeing that run output.

Amendment procedure: amendments BEFORE run 1 are free: commit them,
update FREEZE.md hashes, record the new freeze commit hash. Amendments
AFTER run 1 starts are allowed only for (a) a safety stop, or (b) a
logging fix that does not change thresholds, cases, caps, run order, or
checker verdict rules. Each requires an AMENDMENT commit plus one line in
the verdict stating what changed, when, and whether any completed run is
affected. Any run completed before such an amendment is flagged, and if
the amendment could have changed that run outcome, the run is marked
INVALID and re-run once under the new rule, with the original preserved.
If a threshold was wrong, the pilot is re-run as a new pre-registered
pilot with a new freeze commit; the old pilot stays NO-GO or
INCONCLUSIVE. Thresholds are never moved to rescue a run.

What is frozen (exact list): the amended pilot plan; the amended run-log
schema; the amended runbook; the frozen check_run.py; the checker
self-test matrix and its expected outputs; the frozen fixtures (pick4 md5
91b2f92945c167306a13ae32977a9bf3, f01 md5 2b6eda97036af51510b7eefe6d36dd93);
the f01 spec file; the GO bar in full text; the definitions in section
5A; the program caps (8192 chars, Case A 1 planned + 1 recovery, Case B
2 planned + 1 recovery); the per-case run caps (Case A 15 min, Case B
60 min); the run order (stratified-randomized per pair, sealed in the
manifest); the invalidation rules; the unblinding procedure. The freeze
commit hash is recorded in every run report and in the verdict.

## 9b. Sealed manifest custody rule (Council 2 Finding 5)

- Custodian: Muse (coordinator) holds the manifest. Nobody else holds a
  copy. Worker A1 holds only the sha256 hash. The executor and the checker
  operator never receive the file, its path, or its contents.
- Creation: before run 1, Muse pre-generates 12 random 8-hex run-ids and
  writes the mapping (run-id, case, arm, run number) to a file OUTSIDE
  the repo (not under runs/, not committed). Muse publishes only the
  sha256 of that file in the pilot log before run 1. The manifest is never
  committed to the branch before unblinding, because any repo reader
  (including the executor) could open it.
- Issue: the executor receives one run-id at a time with the arm procedure
  for that run, and nothing else. It never sees the full set of 12 ids.
- Checker enforcement: check_run.py takes a single run directory path and
  contains no code path to the manifest. Verified before run 1 by grep for
  "manifest" returning nothing (see section 6).
- Early-open prevention: (a) separation: the holder (Muse) is not the
  executor, not the checker operator, and not the Stage 2 metrics runner;
  (b) tamper detection: at unblinding, Muse re-hashes the file and
  compares against the hash published before run 1; a mismatch voids the
  pilot and is reported plainly; (c) audit: after the pilot, the
  executor's transcript is grepped for the manifest path and filename;
  any access is reported in the final report, and any access before
  unblinding voids the affected runs.
- Opening: only after all 12 Stage 1 verdict files are committed, Muse
  opens the manifest in a single unblinding step, joins run-id to arm,
  publishes the joined table, and only then commits the manifest contents
  to the repo with the final report. Opening before that point, by anyone,
  is a protocol violation and is reported as one even if the verdicts are
  unaffected.

Honest limit (stated plainly, not hidden): on a shared filesystem with
one user, no technical seal can stop a determined same-user agent from
reading a file. What the custody rule provides is separation of holders,
a pre-published tamper hash, and a post-hoc audit. That is the strongest
seal available here, and it is described as that, not as an unbreakable
seal.

## 9c. Executor death and restart rule (pre-registered)

Two different events, two rules. Do not confuse them.

A. Executor liveness death (Council 2 Finding 6). The executor emits a
progress marker at every run start and every run end, in the pilot log.
The watchdog polls every 5 min and reports to Muse directly. A run with
a start marker and no end marker within 30 minutes is declared DEAD by
Muse. The 30-minute figure is a death declaration for runs whose measured
predecessors run in seconds to a few minutes; it is not a performance
timeout and it is not a p95 timeout, which the redesign correctly says
must be measured first, not invented. A dead run's run-id is voided. Its
partial evidence stays in its directory, marked DEAD, and is never counted
in n=3, never checked, never unblinded. The replacement run gets a NEW
random run-id, a new manifest entry appended by Muse (the hash is
re-published), and starts from a fresh browser session with storage
cleared and the fixture reloaded. It is a fresh run, never a resume of
the dead run's state. Completed runs stand and are never re-run. The
replacement executor is briefed identically from the same runbook and
receives no interim results. Restarting under this rule does not void the
pre-registration, because the rule, the exclusion-by-death criterion, and
the no-interim-results condition are all frozen before run 1. Excluding a
run for its partial result, re-running a completed run, or changing the
runbook mid-pilot DOES void the pre-registration and requires a new
freeze. Second death: if the executor dies twice, the pilot PAUSES. Muse
reviews, records the cause, and decides in writing whether to appoint a
new executor under the same rule or stop the pilot. A third executor is
never spawned silently.

B. Session death inside a run (Council 3 section 5A). The broker session
or the browser session terminates before the verified end state. Logged
as one session_death line. One restart per run is allowed: the death is
counted, the restart steps are recovery steps, and wall time keeps
running. A second death in the same run ends the run as FAIL with
run_end reason failed. A restart that itself fails to start ends the
pilot: STOP, report to Muse, do not start the next run. (This replaces
the runbook's old "STOP on death" rule. A death is a cost to be counted,
not a reason to waste a pilot.)

C. Stall (Redteam C3). Pilot runs carry progress markers (one per run
start, per program submission, per 15 min of wall). The watchdog watches
the executor; the first stall flag kills the run. A stalled run is
recorded with run_end reason killed and verdict FAIL, unless the stall
cause is an INVALID cause under section 5A, in which case the run is
INVALID and re-run once. No pilot run proceeds without a named watchdog.

## 10. What this pilot does NOT prove

- It does not prove batching wins on Zen (Chromium/CDP only).
- n=3 per arm is small. A GO is a pilot GO, not a proven speedup factor.
  The confirmatory run (Council C Exp1, model-turn batching as its own
  named experiment, pilot-sized set first) follows only on GO.
- Pick 1 minus 53% was n=1 per arm and the Pick 4 mean delta was
  inflated by incidentals (clean pair only minus 5%). This pilot exists
  because those numbers are not solid. The Pick 1 figure carries four
  caveats (Redteam N1): P3/P4 walls exclude dwell (P3 strict wall was
  295.22s with 274.51s dwell, P4 98.62s with 78.04s dwell); both P3 and
  P4 attempt 1 failed identically on the screen-changed preflight flake
  and only passed on retry; the mean is across 4 DIFFERENT tasks, each
  run once per arm, with no variance estimate; "calls 5 to 2" is a range
  (2-4 per task), not a uniform result. The design file's own warning
  applies: n=1 per arm, do not quote a precise speedup factor.
- The 87.8 percent loop share is UNVERIFIED: the redesign section 9
  admits it has no time-motion confirmation, and no crawled source gives
  a think-vs-observe-vs-act split. The pilot's metrics are designed to
  measure it. Until then, no ranking in this plan rests on 87.8 percent.
- D1's "about 21s core DOM loop" is 20.7s of THINK (browser-observe 7.5s
  plus browser-act 13.2s), not wall. D1 total wall was 293.401s. The
  design file's "time-to-verified about 82s" is UNVERIFIED: no derivation
  appears in the summary or the design file, so it is not quoted here.
- "Program-composition think about 18s vs P2 8.59s" is UNVERIFIED and
  apples-to-oranges (the 18s matches P3/P4 TOTAL think, the 8.59s is P2
  total think; no source breaks out think-before-first-program-call).
  It is deleted from this plan's motivation. The pilot measures the
  component directly instead (section 3).
- If the pilot goes NO-GO: stop, report plainly, do not proceed to
  Exp1/Exp2 on the same lever.

Power note: at n=3 this pilot is powered to detect a 50% wall cut, not
a 30% cut. A true exactly-30% effect passes the median bar about 50% of
the time per case and about 25% of the time on both cases. A NO-GO is
therefore reported as "not proven at pilot scale", never as "batching
does not work". A GO is reported as "proceed to the confirmatory run",
never as "a 30% speedup is proven". The confirmatory run sizes n from
the pilot measured within-arm spread. (Council 3 section 7.)

Zen transfer probe (Council 1 point 5, Redteam A10): a Chromium GO does
not authorize Exp1. Between a Chromium GO and Exp1, a Zen transfer probe
runs: Case A only, 1 run per arm on Zen, same fixture and task, same
blinded checker, no GO bar. The probe is diagnostic. If the CODE probe
run fails, or its wall is worse than the STEP probe run wall, Exp1 is
paused and the transfer failure is investigated and reported before any
scale-up. Exp1 proceeds only after the probe is reported. The pilot
report states Chromium-only in its title and in every claim: no
wall-time claim in the pilot report names Zen. A pilot GO authorizes
Exp1 design work only.

## 11. Synthesis: how the four verdicts were resolved

All four verdicts landed before any live arm ran. Council 1 (performance,
commit f2d64e7): AMEND, 6 points. Council 2 (structure, commit bf3b25b):
AMEND, 7 findings. Council 3 (measurement): AMEND on 7 points, BLOCK on
the two-directory checker self-test. Redteam (commits c4743dd, 536c41e):
7 attacks KILL the design as written, all fixable. No verdict was BLOCK
on the pilot itself. Every KILL and BLOCK below is closed by a specific
amendment in this frozen plan. Contradictions are resolved here, not
hidden; the losing position is named in each case.

- D1, Case A wall gate: Council 1 point 1 and Redteam B1/C4 adopted;
  Council 3 section 1.5 (per-case wall gate on both cases) superseded on
  this point only. Reason: Council 3's own section 1.2 proves Case A
  cannot confirm a 30% cut (13s effect vs 110-139s incidents), and
  Redteam B1 proves the batchable portion is 7% of D1 wall. Keeping the
  gate would stack a known-unattainable condition onto the verdict.
  Case A is a feasibility gate (pass rate, recovery, composition think);
  wall is diagnostic.
- D2, run order: stratified per-pair randomization adopted (2-1 split per
  case, sealed in the manifest). Supersedes Council 1 counterbalance
  (it confounds start-arm with case: Case A CODE always second and always
  informed, Case B STEP always second; the GO bar is per-case, so
  per-case bias is exactly what matters) and Council 2's STEP-first
  endorsement (its reasoning repeats the plan's own backwards claim that
  landing warmup on the control is conservative; Council 1 and Redteam A2
  independently show it favours the hypothesis). Council 1's "first runs
  reported separately" is kept.
- D3, executor count: ONE executor (Council 1, Council 2). Redteam A3's
  two-executor option rejected: between-executor skill variance at n=3
  is a larger confound than within-executor learning under alternation
  with no feedback, and composition skill is already the key confound
  (Redteam B5). Redteam A3's minimum controls adopted instead (runbook
  procedure-only, no improvements/ access during runs, transcript check).
- D4, off-clock authorship (Redteam A1): adopted in full. No program text
  in the runbook; live composition inside the timed run; pre-session
  program text voids the run. The Case B feasibility draft was measured
  (2,453 chars) and DELETED; only the count is recorded.
- D5, STEP Case B path (Redteam A4): adopted. STEP Case B uses DOM
  observe/act per step with the same refs as CODE. The td-click trap is
  named in the runbook so neither arm falls into it.
- D6, recovery invisibility (Redteam A5, Council 3 section 4.2): section
  5A definitions adopted verbatim; CODE programs log one act line per DOM
  action including in-program retries. Fallback kept: if Layer-2 Probe 5
  cannot demonstrate in-program retry logging, condition 3 is dropped
  BEFORE run 1, never mid-pilot.
- D7, wall definition (Redteam B1, Council 1 point 6): wall ends at
  verified end state; finish think outside wall, bounded to one
  confirmation turn; think per program call; GO condition 4 (total CODE
  composition think below STEP median total think) added.
- D8, n and power: n=3 stays (all four agree; Council 3's model shows
  raising n does not fix at-boundary power, and Redteam B2's separate
  variance probe is rejected as superseded: the pilot's own STEP runs
  measure the spread, a separate probe would contaminate the executor
  with extra fixture exposure, and the dispersion rule converts excessive
  spread into INCONCLUSIVE). Council 1's 2-of-3, dispersion, flagged-run,
  and INCONCLUSIVE rules adopted. Council 3's robustness check adopted as
  a reporting label, not a gate.
- D9, program caps: Council 1 point 3 adopted (1+1, 2+1, split points
  frozen). Char check measured (section 2): loop shape 2,453 chars fits
  with 70.1% headroom; unrolled shape 8,603 busts the cap. No reversion
  needed. Program wall budgets frozen (Case A 30s, Case B 60s).
- D10, Zen transfer: Council 1 point 5 and Redteam A10 adopted. Chromium
  GO authorizes Exp1 design work only; Exp1 runs wait for the transfer
  probe. Report titled Chromium-only.
- D11, checker blinding and unblinding: Council 2 Finding 2, Council 3
  section 6.4, Redteam A6 adopted (two stages, sealed outputs, T11
  arm-leak test). Unblinding by Muse, not Worker A1 (Council 2 section
  9b, Redteam C1); Council 3 section 5.3 item 3 naming Worker A1 is
  superseded, because A1 generated the instruments. A1's role after the
  freeze is evidence packager only.
- D12, custody: Council 2 section 9b adopted (Muse holds the only copy
  outside the repo, sha256 published). Council 3 section 5.3 items 2-3
  (executor calls the manifest script; A1 runs unblinding) superseded by
  9b/C1. Redteam C5's run-id assignment rule adopted (script run by Muse,
  not by the executor).
- D13, death and stall: merged rule in section 9c. Session death follows
  Council 3 section 5A (one restart, counted, wall keeps running);
  Council 2 Finding 6's void-and-replace is superseded for session death
  (voiding discards data and invites re-running until clean) but its
  30-minute executor-liveness declaration and second-death pause are kept
  as event A. Stall follows Redteam C3 (first flag kills the run).
- D14, checker self-test: Council 3's T1-T16 matrix adopted (its BLOCK is
  closed by building it). Redteam C2 vs Council 3 synthetic dirs resolved:
  synthetic dirs for edge cases that cannot occur in real runs; the
  verdict-critical cases (T1, T3, T2, T4) are ALSO validated against real
  runs via the Layer-2 probe directories at resume. The matrix is reviewed
  and executed by an INDEPENDENT worker, not A1 (Redteam C1). Council 2
  Finding 4's "known-good/known-bad built from frozen fixtures, not from
  live runs" is superseded for the verdict-critical cases by the real-run
  cross-check.
- D15, held-out: Redteam H1-H6 adopted in full (section 2). Pool is agy-q2
  test-06..test-10 only; draw sealed before run 1; candidates live-
  validated first; both arms n=1 exploratory; runner brief plus transcript
  check.
- D16, preflight gate: Redteam B4 adopted (stop-fix-reprobe, not automatic
  safety NO-GO). Council 2 Finding 4's "probe failure is a safety NO-GO"
  is superseded: a probe failure proves a harness bug, not a lever
  failure. Triage checklist and Probe 5 (retry logging) added.
- D17, citations: Redteam N2/N3/N4/N6/N8 corrections adopted (3,604 ms
  cited to the run-u-all log; "18s vs 8.59s" deleted as UNVERIFIED; 21s
  labeled think; 87.8% labeled UNVERIFIED; f01 pinned by commit plus md5;
  Pick 1 caveats in section 10).
- D18, metrics: Council 3 sections 2.3 and 2.4 adopted (UNMEASURED rule;
  observation service cost, vcr_service, silence_minutes). Tokens expected
  UNMEASURED. Wall-time VCR UNMEASURED unless verify lines are present.
- D19, schema: Council 3 sections 3.3, 3.4, 3.5 adopted (line shape,
  step_index, progress_marker, tokens/think ops, image flag,
  target_ref/intended, run_end reasons, setup-log.jsonl, setup.json,
  commands.txt as JSONL, recompute claim restated).
- D20, freeze: Council 3 sections 5.2, 5.3, 5.5 adopted with the custody
  correction in D12. FREEZE.md plus manifest and unblinding scripts are
  part of the freeze commit.
- D21, stall rule: Redteam C3 adopted (progress markers per run start,
  per program submit, per 15 min of wall; watchdog; first stall flag
  kills the run).

Timing note: Council 2 Finding 0 and Redteam A8/C6 (runbook, schema,
checker "do not exist", plan uncommitted) were true at review time and
are stale now: the three artifacts were written and committed after the
reviews began (runbook, schema, checker, preflight probe, Layer-1 test).
This freeze commit contains the amended versions of all three plus the
self-test matrix, FREEZE.md, and scripts. The plan file itself is
committed in this freeze.

## 12. Open questions (from the draft; all answered)

1. Is n=3 per arm enough for a pilot GO? Answered: yes as a screen, no as
   proof (Council 3 section 1, D8). Powered for a 50% cut, not 30%.
2. Is the 3-program-call cap honest? Answered: replaced by 1+1 / 2+1 with
   planned-vs-recovery labels and frozen split points (Council 1 point 3,
   D9). Char check measured.
3. Is Chromium/CDP the right isolation? Answered: yes for the pilot, with
   the mandatory Zen transfer probe before Exp1 (Council 1 point 5, D10).
4. Does STEP-first alternation protect against warmup bias? Answered: no,
   it favours the hypothesis; replaced by stratified per-pair
   randomization (D2).
5. Is the blinded checker really blind? Answered: strictly no as specified;
   fixed by two stages, sealed outputs, and the T11 arm-leak test
   (Council 2 Finding 2, Council 3 section 6.4, D11). PASS/FAIL itself is
   unbiased (DOM values only); the leak was on the human side.
