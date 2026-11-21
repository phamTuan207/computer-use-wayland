# A1 narrow pilot plan (DRAFT for council + redteam debate, 2026-11-21)

- Owner: Pham Tuan. Pilot worker: Worker A1 (Muse).
- Proposal: improvements/working-structure-redesign-20261121.md section 6,
  commit fb00973. Owner approved 2026-11-21 18:17, "follow it as Lauren Tan
  advises".
- Design: improvements/a1-code-exec-dom-design.md (2026-11-19).
- Status: DRAFT. Thresholds below are PROPOSED, frozen only after council +
  redteam debate and Worker A1 synthesis. No live arm has run. No speedup
  is claimed.
- Sequencing: ALL prep now. NO live Zen/Chromium arm runs until Muse gives
  the resume order (owner away from keyboard). Non-driving prep only.

## 1. Question

Does batching actions per observation inside code-exec programs cut total
wall time on deterministic short tasks, versus the step-by-step model loop,
without losing pass rate or adding recovery steps?

Lever under test: ONE observation yields MANY actions (code-exec program
absorbs observe-act-branch-retry locally, zero model round trips in between).
Nothing else changes between arms: same fixture, same browser, same task,
same executor, same checker.

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
  deterministic task that exercises observe-click-assert.

### Case B: f01 spreadsheet (long, 26 spec steps)

- Spec: tests/realistic/fcc-k/test-01-spreadsheet-formula.md.
- Fixture: tests/realistic/fcc-k/fixtures/test-01-spreadsheet.html
  (already in the repo, unchanged).
- Task: the spec's 26 steps exactly: enter 5 sales rows, write SUM /
  AVERAGE / COUNT formulas, spot the wrong COUNT formula returning text,
  fix it to COUNTA, confirm E5=1864000, E6=621333, E7=3.
- Step counts, three ways (all recorded, none hidden): 26 spec steps,
  40+ low-level click/type/read actions, 71 steps in Worker U's scripted
  DOM run (tests/realistic/live-run-u-20261121.jsonl, f01 PASS 3,604 ms).
  The proposal's "70 scripted steps" means the 71-step scripted run.
- Why this case: the hard case. It has a mid-task diagnosis step (the
  wrong formula) that the program must branch on locally, which is
  exactly what batching claims to absorb.

### Held-out task (phase 2, frozen AFTER the pilot verdict, BEFORE its run)

- One realistic task, run by an INDEPENDENT runner (never the pilot
  executor), using the GO-arm method only if the pilot goes GO.
- Selection rule (pre-registered): Muse picks it after the pilot verdict
  from the pool {agy-q2 test-06..test-10, clone1-batch3 t-series},
  excluding any test used in deliberation or pilot prep. The choice is
  written down before the runner starts. The runner does not know the
  pilot's numbers.

## 3. Arms

### Arm CODE: code-exec program

- The executor submits programs through the code-exec path
  (scripts/code_exec.py, DOM ops dom_start/dom_tabs/dom_observe/dom_act/
  dom_assert, unchanged from the design file).
- Case A program: the D1 program from the design file section 3, adapted
  only for the frozen fixture path (tests/realistic/a1-pilot/fixtures/
  pick4-fixture.html served over the local HTTP server, same as the
  existing runners do for fcc-k/agy-q fixtures).
- Case B program: one program that does all 26 steps with local branching
  on the wrong-formula diagnosis (re-read E7, if text then replace with
  COUNTA, re-read). It may chain several dom_act calls inside the program.
- Caps (pre-registered): each program at most 8192 chars (the interpreter
  MAX_PROGRAM_CHARS, hard cap). At most 3 program calls per run. Program
  char count and program call count are reported per run. If a case needs
  more than 3 program calls, that is recorded as a design miss, not
  worked around by editing the cap.
- Think-before-first-program-call is measured per run (the P3/P4 lesson:
  program-composition think was about 18s vs P2 8.59s).

### Arm STEP: step-by-step model loop

- The executor drives through the broker one tool call per step: observe,
  act, observe, act, exactly as the Pick 1 / Pick 4 arm-1 baselines did.
  No code-exec, no batching, no program calls.
- Case A: windows, observe, navigate act (Ctrl+L + type URL + Enter),
  observe, tabs, DOM observe, DOM act click, DOM assert, close. One model
  turn per call.
- Case B: the 26 spec steps, one model turn per action, re-observing
  after each batch of edits as the spec requires.

### Common to both arms

- Browser: managed Chromium via the existing code-exec DOM path (CDP),
  exactly as D1 did. NOT Zen. Reason: the pilot tests the batching lever,
  not Zen control. Zen has its own open failure modes (hidden-body
  incident 17:52 21/11, BiDi click false-ok) that would confound the
  lever. Transfer to Zen is a follow-up experiment, not this pilot.
- Run window: task start (session start submit) to verified end state,
  same as Pick 1 / Pick 4 measurement.
- Executor: ONE fresh executor agent runs both arms (same model, same
  harness), following the written runbook
  (tests/realistic/a1-pilot/runbook.md), to minimize executor variance.
  The executor is not Worker A1 and not the checker.

## 4. Run order and n

- n=3 per arm per case. Total 12 runs (2 cases x 2 arms x 3).
- Alternating arms, step first: per case, run order is STEP, CODE, STEP,
  CODE, STEP, CODE. Step first so any first-run warmup cost lands on the
  control arm, conservative against the hypothesis.
- One run at a time. Broker SOLO (the Pick 4 arm-1 run-1 lesson: parallel
  workers held the single-owner broker and 0/4 runs blocked).
- Between runs: fresh browser session, fresh fixture state (storage
  cleared, fixture reloaded), desktop verified clean.

## 5. GO / NO-GO bar (PRE-REGISTERED, frozen before any run)

GO only if ALL of these hold, per case, on BOTH cases:

1. Median wall time (CODE arm) down at least 30% versus median wall time
   (STEP arm), per case.
2. Pass rate (CODE) equal or better than pass rate (STEP), per case.
3. Recovery steps (CODE) not higher than recovery steps (STEP), per case.

Any one failing on any case is NO-GO. If one case passes and the other
fails, the verdict is PARTIAL with per-case verdicts, and Exp1 does not
proceed on the failed case's shape. Actions-per-observation is reported
as a diagnostic, never as a gate. Think-before-first-program-call is
reported alongside wall time, so a wall win bought by huge composition
think is visible, not hidden.

## 6. Blinded checker

- Each run writes evidence to runs/<run-id>/ where run-id is a random
  8-hex string assigned at run start. The run manifest (arm label,
  case, run number) is sealed in runs/manifest-sealed.jsonl, which the
  checker never opens.
- Evidence per run: timed run log (JSONL, schema section 8), end-state
  DOM dump (final cell values / #result text), final verification
  screenshot, exact commands run.
- Checker: tests/realistic/a1-pilot/check_run.py. Input: one run
  directory. It reads ONLY the run directory (never the manifest) and
  outputs PASS/FAIL + the six metrics + per-run fields, from the DOM
  dump and the timed log. It does not know the arm.
- Unblinding happens only after ALL 12 runs are checked, in a separate
  step that joins run-id to arm from the sealed manifest, done by
  Worker A1 (not the checker, not the executor).

## 7. Preflight test (the safety gate)

The design file requires testing the preflight guarantee deliberately
with a bad ref mid-list across every action type used. Two layers:

- Layer 1, interpreter (VM, no browser, prep now): unit test with a
  FakeDomBackend proving _validate_dom_actions rejects a bad ref before
  any backend call, for each ref-taking action type used in the pilot
  (click, fill/set_value, assert). A bad ref anywhere in the list means
  the whole batch is refused with completed: 0.
- Layer 2, adapter (live browser, AT RESUME, before any pilot arm): a
  probe program that issues a real dom_act with a bad ref in the middle
  of the list against the real fixture and verifies completed: 0 and zero
  DOM effects (cell values / #result unchanged). One probe per ref-taking
  action type used. If any probe shows a partial effect, the pilot does
  NOT proceed; that is a NO-GO by safety, reported plainly.

## 8. Metrics (run-log JSONL schema, per run)

Six metrics from the proposal, plus per-run fields. Computed by script
from the run log, never self-reported by the executor.

1. wall_ms: task start to verified end state (headline).
2. tool_calls: model tool calls in the run, counted from the transcript.
3. tokens_in / tokens_out: BEST-EFFORT. If the session does not expose a
   per-task token count, report UNMEASURED, never estimated.
4. observation_cost_ms_by_type: aspirational until the harness logs it.
   Until then, report per-observation elapsed from the timed log where
   available, else UNMEASURED.
5. vcr_flag: verification cost divided by production cost. A flag with an
   explanation when it exceeds 1.0, not an automatic verdict.
6. stall_minutes: wall time minus time covered by progress markers.
Per run also: pass/fail by the blinded checker, recovery steps,
refusals, misclicks, session deaths, retries, program calls (CODE arm),
program chars (CODE arm), think-before-first-program-call (CODE arm).
A win on wall with a rise in refusals or deaths is not a win.

Schema file: tests/realistic/a1-pilot/run-log-schema.md. Each log line:
{"ts", "run_id", "case", "op", "elapsed_ms", "ok", "detail", "error"}.
Arm label is NEVER in the run log (it lives only in the sealed manifest).

## 9. Resume preconditions (all must hold before any live arm)

- Owner away from the keyboard (no live driving while he is at it).
- Broker SOLO and idle, no other runner active, Zen untouched by the
  pilot (Chromium only).
- Layer-2 preflight probes pass (section 7).
- Fixture checksums re-verified (pick4 md5, f01 fixture present).
- Run directories + sealed manifest created, checker verified against a
  known-good and a known-bad run directory (checker self-test).
- Executor briefed from the runbook only, no knowledge of the pilot's
  numbers or the hypothesis direction beyond the arm procedure.

## 10. What this pilot does NOT prove

- It does not prove batching wins on Zen (Chromium/CDP only).
- n=3 per arm is small. A GO is a pilot GO, not a proven speedup factor.
  The confirmatory run (Council C Exp1, model-turn batching as its own
  named experiment, pilot-sized set first) follows only on GO.
- Pick 1 minus 53% was n=1 per arm and the Pick 4 mean delta was
  inflated by incidentals (clean pair only minus 5%). This pilot exists
  because those numbers are not solid.
- If the pilot goes NO-GO: stop, report plainly, do not proceed to
  Exp1/Exp2 on the same lever.

## 11. Open questions for council + redteam

1. Is n=3 per arm enough for a pilot GO, or does the small n make the
   30% bar meaningless on noisy wall times?
2. Is the 3-program-call cap for Case B honest, or does it let the CODE
   arm smuggle in extra model turns through program splits?
3. Is Chromium/CDP (not Zen) the right isolation, or does it make the
   pilot irrelevant to the owner's actual goal (Muses driving HIS Zen)?
4. Does STEP-first alternation actually protect against warmup bias, or
   should the start arm be randomized per case?
5. Is the blinded checker really blind, or can it infer the arm from
   the run log shape (e.g., program-call lines)?
