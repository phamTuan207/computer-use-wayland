# A1 pilot run-log JSONL schema

- One line per action, observation, or event. File: runs/<run-id>/run-log.jsonl.
- The run directory NEVER contains the arm label or the case label. Those
  live only in runs/manifest-sealed.jsonl, which the checker never opens.
- The checker (tests/realistic/a1-pilot/check_run.py) recomputes every
  number from this log alone. No executor memory is used.

## Line shape

{"ts": "<RFC 3339 UTC>", "run_id": "<8-hex>", "op": "<op>",
 "elapsed_ms": <number>, "ok": <bool>, "detail": <any>, "error": <string|null>}

- ts: wall-clock time of the line (UTC, RFC 3339).
- run_id: the run's random 8-hex id.
- op: one of the ops below.
- elapsed_ms: how long this op took (for run_start / run_end: 0).
- ok: whether the op succeeded.
- detail: op-specific payload (see below).
- error: exact error text, or null.

## Ops

- run_start: first line of every run. detail: {"case_task": "pick4" | "f01",
  "run_sequence": <1..12, position in the full 12-run sequence>}.
  Note: the case TASK name is allowed in the log (the checker needs to
  know which end state to verify). The ARM label is never allowed.
- run_end: last line of every run. detail: {"verdict": "done" | "failed",
  "reason": "<short reason>"}.
- reset: between-run reset (fresh session, storage cleared, fixture
  reloaded). detail: {"what": "session|storage|fixture|desktop"}.
- observe: a browser/desktop observation. detail: {"kind": "dom|desktop",
  "elements": <count>}.
- act: a broker act (STEP arm) or a DOM act inside a program (CODE arm).
  detail: {"kind": "broker|dom", "actions": <count>, "completed": <count>}.
- program_submit: a code-exec program submit (CODE arm only).
  detail: {"chars": <program char count>, "calls_so_far": <1..3>}.
- think_before_program: CODE arm only, one line per run.
  detail: {"ms": <wall ms from run_start to first program_submit>}.
- assert: a DOM or state assertion. detail: {"what": "<selector or cell>",
  "expected": "<expected>", "got": "<actual>"}.
- refusal: a refused action (stale observation, element not
  interactable, session error). detail: {"reason": "<exact error>"}.
- retry: a retry after a refusal. detail: {"after_refusal": "<reason>"}.
- recovery: any recovery step (re-observe, re-navigate, re-type after a
  miss). detail: {"what": "<what was redone>"}.
- misclick: a click that landed on the wrong element. detail: {"what": ...}.
- session_death: the browser or broker session died.
  detail: {"what": "<browser|broker>", "error": "<exact error>"}.
- tool_call: one model tool call. The executor writes one line per tool
  call it makes for the arm, detail: {"tool": "<tool name>"}.
  The checker counts these for the tool_calls metric.

## Metrics computed by the checker from this log

1. wall_ms = run_end.ts - run_start.ts.
2. tool_calls = count of tool_call lines.
3. tokens_in / tokens_out: UNMEASURED unless the executor records them
   (the executor may add {"op": "tokens", "detail": {"in": n, "out": n}}
   if its session exposes per-task counts; otherwise UNMEASURED).
4. observation_cost_ms_by_type: mean elapsed_ms of observe lines, split
   by detail.kind (dom vs desktop). UNMEASURED if no observe lines.
5. vcr_flag: (time in verification ops) / (time in production ops).
   Verification ops: assert lines + final desktop observe. Production
   ops: all other act/observe lines. Flag with explanation when > 1.0.
6. stall_minutes = (wall_ms - time covered by progress lines) / 60000.
   Progress lines: any line except run_start/run_end. In practice the
   log is dense, so stall_minutes is near 0; a gap over 15 min between
   consecutive lines counts as stall.
Per run also: pass/fail (from end-state.json, not the log), recovery
steps (count of recovery lines), refusals (count of refusal lines),
misclicks (count of misclick lines), session deaths (count of
session_death lines), retries (count of retry lines), program calls
(CODE arm: max calls_so_far), program chars (CODE arm: sum of chars).

## Provenance per run (provenance.json in the run directory)

{"repo_head": "<git HEAD at run start>",
 "relay_head": "<relay started_git_head>",
 "cu_code_exec": "1", "cu_pick4_fastpath": "1",
 "broker_solo_proof": "<broker-status output at run start>",
 "fixture_md5": {"pick4": "91b2f92945c167306a13ae32977a9bf3",
                 "f01": "2b6eda97036af51510b7eefe6d36dd93"}}
A run missing any of the eight evidence items is INCOMPLETE, not
counted in n=3, and re-run under a new run-id.

## Blinding note

The checker is a deterministic script, not a model. Stage 1 reads
only the end-state dump and the final screenshot and outputs only
PASS/FAIL. Stage 2 reads the timed log only after all Stage 1
verdicts are committed, and outputs the metrics. The pass/fail rules
depend only on end-state.json values, so no leniency by arm is
possible. The log shape differs between arms (CODE runs have fewer,
longer ops), but Stage 1 never reads the log.
