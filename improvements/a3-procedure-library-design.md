# A3 procedure library: design

- Owner: Pham Tuan. Date: 2026-11-19, evening Asia/Ho_Chi_Minh.
- Worker: Luna 6 Max (Track 2 resume round 2, lever A4 + A3).
- Status: DESIGN + MINIMAL CORE IMPLEMENTED. The core
  (`scripts/procedure_library.py`, with unit tests) is built and
  committed on branch `algo-a4`. Broker wiring (retrieval at dispatch,
  extraction from traces) is designed here and NOT yet built; it needs
  a live-measure decision first. No live measurement in this round:
  the broker is single-owner and busy with the R3 live run.
- Source: `algorithm-research.md` section A3 (R1 from
  `speed-swarm-planning.md`, generalization of the adopted tc02
  procedure). No em dash or en dash in this file.

## 1. Goal, in one paragraph

A repeat task shape must cost 0 model turns on the happy path.
Measured precedent: tc02 trial 1 (no procedure, 36 requests) 823s
vs trial 3 (reused procedure, 14 requests) about 100s, 8.23x; the
Step 2 controller runs tc02 with 0 model turns on the happy path
(execution 9.60-9.90s, end-to-end 13.45-13.77s). On a repeat shape
every model call goes to 0 (derived: 5 to 0 on P1-P4-class tasks).
The first run of a new shape still pays full deliberation plus one
extraction pass. This is the only proposal that can reach the 10s
tc02 target, because it removes the loop rather than shortening it.

## 2. What a procedure is

A stored record with exactly these fields:

| Field | Meaning |
| --- | --- |
| key | Exact retrieval key (section 3). |
| name | Short human name, at most 128 chars. |
| program | Code-exec program source, validated with `code_exec.validate_program` at register time. Runs through the existing code-exec path, never a new executor. |
| checks | Postcondition spec (`postcondition.py`, A4), validated at register time. The checkpoint that decides pass/fail. |
| app, window_class, verbs, geometry_bucket | Key components, stored for audit. |
| uses, successes, failures, quarantined, created, updated | Counters. |

A procedure is a program plus its own proof. A program without
checks is not a procedure: it cannot be verified without a model,
so it cannot run as Level 1.

## 3. Retrieval key: exact match only

`procedure_key(app, window_class, verbs, geometry_bucket)` joins
four components with `|`:

- app: e.g. `kitty`, `chromium`, `gedit`.
- window_class: the Hyprland window class, e.g. `kitty`.
- verbs: the action-verb sequence, e.g. `['type', 'type']` or
  `['click', 'fill', 'assert']`. The sequence, not the arguments:
  arguments (filenames, text) are the procedure's parameters, filled
  at dispatch from the task, and they must be validated by the
  checkpoint, not trusted.
- geometry_bucket: a COARSE bucket such as `800x600` or
  `dialog-save-as`, never exact pixel coordinates. Exact coordinates
  go stale when the desktop reflows (Pick 3 incident log: kitty
  moved/resized between tasks with no input). A procedure stores
  relative layout (which window, which dialog class), and the
  program re-derives coordinates from a fresh observation at run
  time; the stored geometry only selects the bucket.

Retrieval is exact-match only. Similarity is not proof: a 0.95
match with a different filename is a wrong answer served fast.
There is no fuzzy lookup, no embedding search, no "close enough".
A miss means full deliberation, not a near-miss replay.

## 4. Execution levels

Borrowed from Pick 2 (`subgoal_policy.py`):

- Level 1, deterministic procedure: key hit, not quarantined.
  Run the stored program via code-exec, run the stored checks via
  postcondition verify. 0 model turns on the happy path.
- Level 2, bounded routine decision: no procedure, but the task is
  routine. Model decides at low effort with a strict JSON schema
  and a deterministic postcondition behind it. (Pick 2 rerun
  verdict: the sub-invocation route is NOT a win; any L2 must be
  in-session. This level is out of scope for the A3 core.)
- Level 3, genuine ambiguity, recovery, new procedure: model at
  max effort. A Level 3 run that succeeds is a candidate for
  extraction (section 6).

Escalation rule (from `subgoal_policy.should_escalate`): escalate
to Level 3 when the postcondition fails, when the state is
genuinely ambiguous, or when a new procedure must be created.

## 5. Checkpoints and quarantine

Every procedure run ends with its stored postcondition spec,
run by `ProcedureLibrary.checkpoint()`. The verdict decides the
outcome: `verified` counts as passed, anything else as failed.

Quarantine threshold is 2 consecutive checkpoint failures, the
same constant as `subgoal_policy.QUARANTINE_AFTER_FAILURES`
(imported, so the two stay in sync). A quarantined procedure is
invisible to `retrieve()`; the next run re-derives layout from a
fresh full-frame observation instead of trusting the stored
procedure. Re-registering a procedure (new extraction) clears its
quarantine. A success resets the consecutive-failure count.

Any silent replay is a failed run, not a saving. Stale-procedure
incidents must be 0: the checkpoint is the mitigation, not a hope.
Checkpoint failure twice in a row quarantines; checkpoint failure
once still escalates that run to Level 3.

## 6. Extraction: how a procedure gets into the library

Extraction is one supervisor session per new shape, amortized
over every later repeat. It is NOT built in the minimal core; the
core only stores what extraction produces. The extraction pass:

1. Take a successful trace (a Pick 1 program that passed its
   postcondition, or a tc02-v1.json controller run).
2. Generalize: replace task-specific literals (filenames, text,
   window titles that vary) with parameters; keep the verb
   sequence, the window/dialog class, and the checkpoint.
3. Derive the key from the generalized shape (section 3).
4. Derive the checks from the task's end state: file bytes/SHA,
   window class/title, DOM text. Every check must be an exact
   local proof (A4 pairing rule).
5. Register with `ProcedureLibrary.register()`, which validates
   the program (AST sandbox) and the checks (spec validation)
   and fails closed on either.
6. Prove it: run the procedure once from a cold start on the same
   held-out task and require a `verified` checkpoint before the
   procedure counts as warm. An extraction that fails its own
   proof run is not stored.

Extraction must never bake in coordinates from one run, never
bake in a transient window address, and never store a program
that passed only because a vision verify said so: the stored
checks must prove the end state on their own.

## 7. Storage

One JSON file, `procedures.json`, mode 0600, under the
caller-supplied state directory (same private-state discipline
as code-exec state files). At most 256 procedures; registering
past that fails closed. A corrupt or unreadable store loads as
empty; a failed save never raises (best effort, like code-exec
state). The store is per-machine state, not repo content: it is
never committed. What IS committed is the code and the design;
the procedures a machine accumulates live in its state dir.

## 8. What the minimal core implements (done, tested)

`scripts/procedure_library.py`:

- `procedure_key()` (exact key construction, section 3).
- `ProcedureLibrary.register/retrieve/is_quarantined/record_result/
  checkpoint/list_procedures`, with JSON persistence, quarantine
  after 2 consecutive failures, quarantine surviving reload,
  re-register clearing quarantine.
- `checkpoint()` runs the stored A4 spec and records the outcome.

Tests: `tests/test_procedure_library.py`, 19 tests, all passing
on 2026-11-19 (see the A4 report for the full-suite comparison).

## 9. What is NOT built yet (needs a decision, then a worker)

1. Dispatch wiring: at task dispatch, build the key from the task
   shape, call `retrieve()`, and run the stored program through
   code-exec when it hits. This is the step that actually cuts
   model turns; the core alone cuts nothing.
2. Extraction pass: section 6, as a supervisor prompt or a small
   script over successful traces. Needs one worked example (P3 or
   P4 as the first stored procedure) before generalizing.
3. Parameter binding: how task arguments (filename, text) flow
   into a stored program safely. Current core stores a fixed
   program; a parameterized program needs a binding step that
   keeps the sandbox (no string-built code from task text).
4. Cold/warm reporting: per-shape first-run wall vs repeat-run
   wall, retrieval hit rate, quarantine events,
   stale-procedure incidents (must be 0 silent wrong actions).
   Report cold and warm stopwatches separately, per the 10x
   review's two-stopwatch rule.

## 10. How to measure (for the live-measure worker)

Same 4 held-out tasks (P1 C-03, P2 E-04, P3 B-01, P4 A-01) plus
D1 browser task where the procedure touches the browser; same
timed.py wrapper; fresh broker session and fresh lease per task;
baseline arm first, then procedure arm. Per task: wall, think
total, model calls, broker service, refusals, misclicks, session
deaths, program retries. Report cold (first-run) and warm
(repeat) separately. Success bar: warm wall approaches the Step 2
controller numbers (about 10-14s end-to-end for tc02-class)
instead of the 36.4s clean mean, with 0 silent wrong actions and
0 stale-procedure incidents. A table whose winning tasks used
zero procedure retrievals proves nothing; the retrieval count
must be non-zero by construction.

## 11. Risks

- Stale procedures acting on a changed app. Mitigation is the
  design (checkpoints plus quarantine), not a hope.
- Key collision: two different shapes sharing a key. The key
  includes the verb sequence and geometry bucket; if a collision
  is ever observed, add a discriminating component (dialog class)
  rather than loosening retrieval.
- Store growth: 256 cap plus manual review; procedures that never
  hit again are dead weight, not a correctness risk.
- Parameter injection: task text flowing into a stored program
  must go through the existing code-exec sandbox (values, never
  code). Until the binding step (section 9.3) is designed, stored
  programs take no parameters.
