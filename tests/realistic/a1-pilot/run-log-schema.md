# A1 pilot run-log JSONL schema

- One line per action, observation, or event. File: runs/<run-id>/run-log.jsonl.
- The run directory NEVER contains the arm label. The arm label lives
  only in the sealed manifest, held by Muse outside the repo, which the
  checker never opens.
- The checker (tests/realistic/a1-pilot/check_run.py) recomputes every
  per-run number from the run dir (run-log.jsonl plus end-state.json plus
  verify.png plus setup.json), and every arm-level number from the run
  dirs plus the sealed manifest plus the frozen thresholds, with no
  executor memory. (Council 3 section 3.4 item 4: the old claim "from
  this log alone" was false, because pass/fail needs end-state.json, arm
  medians need the manifest, program integrity needs commands.txt, and
  the f01 cell list needs the frozen plan.)

## Line shape

{"ts": "<RFC 3339 UTC, op completion>", "run_id": "<8-hex>",
 "step_index": <int>, "op": "<op>", "elapsed_ms": <number>,
 "ok": <bool>, "progress_marker": <bool>, "detail": <any>,
 "error": <string|null>}

- ts: wall time the line is written (op completion). run_start is the
  exception: its ts is the task start instant. ts must be non-decreasing
  down the file; the checker flags a problem otherwise. A negative wall
  is a logging failure, not a number.
- step_index: 1-based per run, sequential. run_start carries 0. run_end
  carries the last index.
- elapsed_ms: harness service time for the op (round trip, excluding
  model think before the call). Settle sleeps inside the op count inside
  elapsed_ms. run_start and run_end carry 0.
- progress_marker: true when the line records a step completed, an
  artifact written, or a checker state changed; false for heartbeat,
  status-poll, and waiting lines. A line with progress_marker false never
  covers time for stall purposes.
- New ops: tokens (detail {"in": n, "out": n}, at most one per run),
  think (detail {"ms": n}, optional, model turn with no tool call).
- observe detail gains "image": true or false.
- act detail gains "target_ref" and "intended" (section 5A, misclicks).
- run_end detail reason is one of: done, failed, timeout, invalid,
  killed.
- Reset lines live in setup-log.jsonl, never in run-log.jsonl.
- The run dir also carries setup.json (fixture name plus md5, browser,
  harness commit, checker version, runbook version) and commands.txt as
  JSONL (one line per broker call or program submit, program text inline).

## Ops

- run_start: first line of every run. detail: {"case_task": "pick4" | "f01",
  "run_sequence": <1..12, position in the full 12-run sequence>}.
  Note: the case TASK name is allowed in the log (the checker needs to
  know which end state to verify). The ARM label is never allowed.
  run_start detail case_task is the only place a case label appears in
  the run directory.
- run_end: last line of every run. detail: {"verdict": "done" | "failed",
  "reason": "done" | "failed" | "timeout" | "invalid" | "killed"}.
- observe: a browser/desktop observation. detail: {"kind": "dom|desktop",
  "elements": <count>, "image": <true|false>}.
- act: a broker act (STEP arm) or a DOM act inside a program (CODE arm).
  detail: {"kind": "broker|dom", "actions": <count>, "completed": <count>,
  "target_ref": "<ref acted on, for click/fill>", "intended": "<intended element>"}.
  One act line per DOM action executed, including in-program retries.
- program_submit: a code-exec program submit (CODE arm only).
  detail: {"chars": <program char count>, "calls_so_far": <1..3>,
  "planned": <true|false>}. Framing lines: counted only for the program
  caps, excluded from the checker metric input.
- think_before_program: CODE arm only, one line per program call.
  detail: {"ms": <wall ms from end of previous model turn, or from run
  start for the first call, to this program submit>, "call": <1..3>}.
- think: optional, a model turn with no tool call. detail: {"ms": n}.
  If the executor cannot distinguish think from idle, the think op is
  omitted and gap ms is reported as "gap (think plus idle)".
- tokens: at most one line per run, written at run end from the session
  usage record if one exists. detail: {"in": n, "out": n}.
- verify_start / verify_end: optional lines bracketing the final
  verification phase. Without them, wall-time VCR stays UNMEASURED.
- assert: a DOM or state assertion. detail: {"what": "<selector or cell>",
  "expected": "<expected>", "got": "<actual>"}.
- refusal: a refused action (stale observation, element not
  interactable, session error). detail: {"reason": "<exact error>"}.
- retry: a retry after a refusal. detail: {"after_refusal": "<reason>"}.
  A retry is also a recovery step for gate purposes.
- recovery: any recovery step (re-observe, re-navigate, re-type after a
  miss). detail: {"what": "<what was redone>"}. One corrective action is
  exactly one line: retry or recovery, never both.
- misclick: a click that landed on the wrong element. detail:
  {"intended": "<intended element>", "actual": "<element acted on>"}.
- session_death: the browser or broker session died.
  detail: {"what": "<browser|broker>", "error": "<exact error>"}.
- tool_call: one model tool call. The executor writes one line per tool
  call it makes for the arm, detail: {"tool": "<tool name>"}.
  The checker counts these for the tool_calls metric. A run with act
  lines but zero tool_call lines is flagged as a logging failure, not
  reported as zero calls.

## Metrics computed by the checker from the run dir

1. wall_ms = run_end.ts - run_start.ts. Finish think is outside wall:
   run_end ts is the verified end state instant.
2. tool_calls = count of tool_call lines.
3. tokens_in / tokens_out: UNMEASURED unless the executor records them
   in a tokens line; otherwise UNMEASURED, never estimated.
4. observation service cost: mean elapsed_ms of observe lines, split by
   (kind, image), plus gap-before ms per observe kind (mean of ts
   difference from the previous metric line minus elapsed_ms of that
   line; the previous metric line is the previous line that carries a
   ts and an elapsed_ms, framing lines such as program_submit and
   think_before_program are skipped). Labeled
   "observation service cost", not "observation cost", until the
   gap-before number exists. UNMEASURED if no observe lines.
5. vcr_service: (time in verification ops) / (time in production ops).
   Verification ops: assert lines + final desktop observe. Production
   ops: all act/observe lines (the final desktop observe is counted in
   both verification and production). Flag with explanation when > 1.0.
   vcr_wall: computed only when verify_start and verify_end lines are
   present (wall time of the verification phase over wall time of the
   production phase); otherwise UNMEASURED.
6. silence_minutes = (sum of inter-line gaps over 900s) / 60. This
   measures log silence, not lack of progress. Stall from progress
   coverage is computed only when progress_marker lines are present;
   until then the number is silence_minutes, not stall_minutes.
Per run also: pass/fail (from end-state.json, not the log), recovery
steps (count of retry lines plus count of recovery lines), refusals
(count of refusal lines), misclick_lines (count of misclick lines) and
misclicks ("none detected" when misclick_lines is 0, else the count),
session deaths (count of session_death lines), retries (count of retry
lines), program calls (CODE arm: max calls_so_far), program chars (CODE
arm: sum of chars), think before each program call and total composition
think (CODE arm), run_sequence, gap ms (wall minus summed service ms).

UNMEASURED rule: a metric that was not measured is reported as UNMEASURED
with the reason, never as 0, never as an estimate, never silently dropped.
A GO verdict may stand with UNMEASURED diagnostic metrics (tokens,
observation cost detail) only if all gate metrics (wall, pass rate,
recovery steps, composition think) are measured on all 12 runs. If any
gate metric is UNMEASURED on any run, the verdict for that case is
INCONCLUSIVE, not GO.

## Provenance per run (setup.json in the run directory)

{"repo_head": "<git HEAD at run start>",
 "relay_head": "<relay started_git_head>",
 "cu_code_exec": "1", "cu_pick4_fastpath": "1",
 "broker_solo_proof": "<broker-status output at run start>",
 "fixture_md5": {"pick4": "91b2f92945c167306a13ae32977a9bf3",
                 "f01": "2b6eda97036af51510b7eefe6d36dd93"},
 "checker_version": "<freeze commit hash of check_run.py>",
 "runbook_version": "<freeze commit hash of runbook.md>"}
The checker reads setup.json and reports its fixture md5; a run whose
fixture md5 differs from the frozen value is INVALID, not FAIL.
A run missing any of the eight evidence items is INCOMPLETE, not
counted in n=3, and re-run under a new run-id.

## commands.txt (JSONL, in the run directory)

One line per broker call or program submit, with the program text inline:
{"ts": "<RFC 3339 UTC>", "kind": "broker_call" | "program_submit",
 "chars": <program char count>, "text": "<full program text>"}.
The checker verifies that the char count in each program_submit line of
run-log.jsonl equals the length of the corresponding program text here.
Without the program text, nobody can check that the program did not
touch fixture internals to set the end state directly, or that it was
composed fresh per run.

## Counting definitions (copied from the plan section 5A, no paraphrase)

Step: one logged action at action level. Each DOM action (click, fill,
assert, navigate, observe) is one step, whether issued by the model
(STEP arm) or by a program (CODE arm). A program that executes 5 DOM
actions logs 5 act lines, one per action, plus its program_submit line.
A model turn that issues 4 tool calls logs 4 tool_call lines. Counting
is at action level in both arms, so the counts are comparable.

Recovery step: one corrective action taken because a preceding action
returned ok:false, or because an observation or assert showed the state
diverging from the intended state. The original failed action does NOT
count as recovery. The diagnostic re-observe after a failure counts.
The re-try of the failed action counts. A state repair counts. A
recovery step is logged exactly once, as one line: op retry if it
repeats the same action (same intent, same target) after a refusal or
failure, op recovery otherwise. Recovery steps for the gate equal
count(retry lines) plus count(recovery lines), summed across the 3 runs
per case per arm.

Planned branch (NOT recovery): a step the runbook or spec prescribes
conditional on observed state. In Case B, the wrong-formula diagnosis
is a planned branch: re-read E7, and if it holds text, replace COUNT
with COUNTA and re-read. Those steps are forward steps, logged as act
lines, never as recovery. If the same COUNTA fix has to be attempted a
second time because the first attempt failed, the second attempt IS
recovery.

Refusal: one request that returns an error without executing any action.
Completed 0 with an error present. A refusal is logged as one refusal
line with detail.reason carrying the exact error text. An action that
executed and then produced the wrong state is NOT a refusal; it is a
failure, and its correction is recovery.

Retry: one repeated attempt of the same action (same intent, same
target) after a refusal or failure. Logged as op retry, detail
after_refusal carrying the exact error text of the refusal or failure
it follows. A retry is also a recovery step for gate purposes. A retry
that itself fails and is tried a third time logs a second retry line.

Misclick: one click or fill action that executed on an element other
than the one the step intended. Intended means the element named in the
runbook step (STEP arm) or the element the program selected as its
target (CODE arm). Every act line for a click or fill carries
detail.target_ref and detail.intended. A misclick is logged as one
misclick line with detail {intended, actual}. The checker counts
misclick lines. A run with zero misclick lines is reported as "none
detected", never as "0 misclicks".

Session death: the broker session or the browser session terminates
before the verified end state, so the run cannot continue without a
restart. Logged as one session_death line with detail {what:
"browser" or "broker", error: exact error text}. One restart per run is
allowed: the death is counted, the restart steps are recovery steps,
and wall time keeps running. A second death in the same run ends the
run as FAIL with run_end reason failed. A restart that itself fails to
start ends the pilot.

Pass: the blinded checker finds the frozen end state in end-state.json
(Case A: result_text contains "pick4-ok". Case B: E2=540000, E3=574000,
E4=750000, E5=1864000, E6=621333, E7=3) and verify.png exists and is
non-empty, and the run log parses and starts with run_start and ends
with run_end. A run that reaches the end state by writing fixture
internals directly is FAIL by fabrication; the program text in
commands.txt is the evidence, checked at unblinding by Muse, not by
the checker.

Fail: any run that is not a pass. The run_end reason says why: failed
(wrong end state or driver failure), timeout, invalid, killed.

Timeout: wall time exceeds the per-case cap (Case A 15 min, Case B 60
min). The run is STOPPED at the cap, run_end is written with reason
timeout and ts at the kill instant, and the run is FAIL. A timed-out
run wall is censored data: its true wall is greater than the kill-time
wall, not equal to it. If the median of an arm is itself a timed-out
run, that median is reported as a lower bound and the GO bar cannot
pass on that case; the case verdict is INCONCLUSIVE, not GO.

Invalid: a run voided for a cause outside the arm under test. Only
three causes qualify: (a) fixture or harness fault found after the run
(fixture md5 mismatch, wrong fixture served, broker outage affecting
both arms); (b) executor violated the runbook (copied a program
verbatim, used the wrong arm procedure, opened the sealed manifest);
(c) run evidence lost through no fault of the arm (log file destroyed).
An INVALID run is logged with reason invalid, preserved, and re-run
once. Two invalidations of the same case-arm pair stop that pair and
the pair is UNMEASURED.

Incident-suspect run: a run whose wall exceeds twice its arm median.
Flagged in the verdict with the reason taken from its log. The flag is
diagnostic; the run stays in the median.

## Blinding note

The checker is a deterministic script, not a model. Stage 1 reads
only the end-state dump and the final screenshot and outputs only
PASS/FAIL. Stage 2 reads the timed log only after all Stage 1
verdicts are committed, and outputs the metrics. The pass/fail rules
depend only on end-state.json values, so no leniency by arm is
possible. The log shape differs between arms (CODE runs have fewer,
longer ops), but Stage 1 never reads the log. Checker outputs are
sealed per run until unblinding, because the output leaks the arm
(program_calls above 0 implies CODE).
