# A1 pilot runbook (for the executor only)

- Pilot: A1 narrow pilot.
- You are the EXECUTOR. You run 12 runs and nothing else. Your
  instructions are this runbook plus its two named appendices: the
  run-log schema (tests/realistic/a1-pilot/run-log-schema.md) and the
  preflight probe list (tests/realistic/a1-pilot/preflight-probe.md).
  You do NOT read any other pilot document. Do not go looking for
  other documents.
- Executor: ONE Codex (Luna 6 Max) session on the owner's laptop, broker
  SOLO. The same session runs all 12 runs. If the session dies, STOP and
  report to Muse immediately; do not restart it yourself. Muse decides
  the restart under the death rule in section 7.
- Sequencing: no run starts until Muse gives the resume order. Muse
  issues runs one at a time: a run-id plus the arm procedure for that
  run, and nothing else.

## 0. Setup (once, before run 1)

1. SSH to the laptop is already available to you; the broker runs there.
   Work in a fresh run directory on the laptop: /tmp/a1-pilot-20261121/.
2. Ship the fixtures from the VM repo to the laptop and verify checksums:
   - tests/realistic/a1-pilot/fixtures/pick4-fixture.html,
     md5 must be 91b2f92945c167306a13ae32977a9bf3.
   - tests/realistic/fcc-k/fixtures/test-01-spreadsheet.html,
     md5 must be 2b6eda97036af51510b7eefe6d36dd93.
   Serve them over the local HTTP server on 127.0.0.1:8768, same pattern
   as the existing runners. Record the exact URLs in the setup log.
3. Verify the broker is SOLO and idle (no other session, no other runner).
   Verify managed Chromium starts via the code-exec DOM path (one
   dom_start probe, no fixture). Record the endpoint in the setup log.
   If the managed Chromium endpoint is not 127.0.0.1:9222, record the
   actual endpoint and report it to Muse before run 1; do not assume.
4. Create runs/ under /tmp/a1-pilot-20261121/. For each run, Muse gives
   you a run-id (a random 8-hex string). Create runs/<run-id>/ for it.
   NEVER write the arm label anywhere inside a run directory. NEVER ask
   for, look for, or open any run-id mapping file. You receive one
   run-id at a time and never see the full set.
5. Run the Layer-2 preflight probes in
   tests/realistic/a1-pilot/preflight-probe.md before run 1, and record
   the probe evidence. If any probe shows a partial effect, STOP and
   report to Muse. Do not start run 1 until Muse confirms the probes
   pass or a fix is landed and the probes are re-run.

## 1. Run order (issued by Muse, do not change)

Muse issues the 12 runs one at a time, in an order fixed before run 1.
You do not know the future order. Each run tells you its case and its
arm procedure. Run the run you are given, report that it finished and
where its evidence directory is, and wait for the next run.

Between runs: fresh browser session, storage cleared, fixture reloaded,
desktop verified clean. Log each reset as a line in setup-log.jsonl in
the run directory, never in run-log.jsonl.

Per-case run caps: Case A 15 min, Case B 60 min. A run that exceeds its
cap is STOPPED at the cap: write the run_end marker with verdict
"failed" and reason "timeout", and report to Muse. Do not let a run hang.

## 2. Case A task (both arms)

Open the Pick 4 fixture in the managed browser, click the "Show result"
button, verify #result contains "pick4-ok". Leave the name field empty.

## 3. Case B task (both arms)

Follow tests/realistic/fcc-k/test-01-spreadsheet-formula.md steps 1-26
exactly: enter 5 sales rows, write SUM / AVERAGE / COUNT formulas,
notice the COUNT formula returns text instead of a number, fix it to
COUNTA, confirm E5=1864000, E6=621333, E7=3. Record all end-state cell
values (C2, C3, C4, E2, E3, E4, E5, E6, E7).

How cells are entered (both arms, identically): the fixture selects a
cell by clicking its BUTTON (labeled A2, B2, and so on), then you fill
the #typed input, click the "type" button, and click the "Enter" button.
Clicking a table cell directly selects nothing, so never click a cell.
For each value you enter, the four actions are: click the cell button,
fill #typed, click "type", click "Enter".

Planned branch (not a recovery step): step 23, the wrong-formula
diagnosis, is prescribed by the spec: re-read E7, and if it holds text
instead of a number, replace COUNT with COUNTA and re-read. Those steps
are forward steps. If the same COUNTA fix has to be attempted a second
time because the first attempt failed, the second attempt IS a recovery
step.

## 4. Arm STEP (step-by-step)

Drive through the broker one tool call per step. Observe, act, observe,
act. No code-exec, no program calls, no batching. One model turn per
broker call. If an action is refused (stale observation, element not
interactable), re-observe and retry; log the refusal and the retry as
run-log lines. Do not skip steps. Do not invent shortcuts.

Case B in this arm: use DOM observe and DOM act per step, with the same
element refs the other arm uses: click the cell button by ref, fill
#typed by ref, click "type" by ref, click "Enter" by ref. One model turn
per action. Re-observe after each batch of edits as the spec requires.

## 5. Arm CODE (code-exec program)

1. Think, then compose a program that does the whole task. Compose it
   FRESH for this run, from the task description above and the template
   rules below. NEVER copy a program from any example, file, or earlier
   run verbatim. Copying a program verbatim voids the run; if you catch
   yourself doing it, stop and report to Muse. Compose the program live
   inside the timed run, after the session has started. NEVER write
   program text before the session starts; any program text written
   before session start voids the run.
2. Template rules:
   - Start the managed browser, look up its window, observe it, navigate
     with one desktop act (Ctrl+L, type the URL, Enter), observe again.
   - Stamp every act and every dom_act action with scope plus
     observation_id, taken from the fresh observe or snapshot the action
     is written against. A desktop act action uses "scope": obs["scope"]
     and "observation_id": obs["id"]; a dom_act action uses "scope":
     tab["id"] and "observation_id": snap["snapshot"]. An action without
     both fields is refused by the adapter before anything runs (CB-2:
     "action 0 is missing scope"), so the navigate act above must be
     written stamped, for example act([{"type": "key", "keys": ["ctrl",
     "l"], "scope": obs["scope"], "observation_id": obs["id"]},
     {"type": "type", "text": "<URL>\n", "scope": obs["scope"],
     "observation_id": obs["id"]}], obs). A retry re-observes first and
     stamps from the fresh observe or snapshot, never from the old one.
   - Get the tab from dom_tabs, observe the DOM with dom_observe.
   - Find the target element by name/role in the snapshot. Click by ref
     with dom_act. Assert on the AFTER snapshot returned by dom_act,
     never on the pre-click snapshot. If an act used no_after, observe
     the DOM again before asserting.
   - Branch locally on results: if a dom_act returns ok:false, or an
     assert fails, re-observe and retry from a fresh snapshot inside the
     program. A retry costs zero model calls; that is the point.
   - End every program with a desktop observe for the final verification
     image, and record its image path in the run log.
3. Caps: each program at most 8192 chars. Case A: at most 1 planned
   program call plus at most 1 recovery call. Case B: at most 2 planned
   program calls plus at most 1 recovery call. A recovery call is a
   program call issued only after a previous program returned ok false
   or a failed assert with completed 0 or no effect, and it counts as 1
   recovery step. Planned split points, frozen before the first live run:
   a single program covering all 26 steps is allowed and preferred if it
   fits the caps. If you split, split after step 17 (after entering the
   E7 COUNT formula and reading E7): program 1 covers steps 1-17,
   program 2 covers steps 18-26. No other split point. No adaptive
   re-splitting mid-run except through the single recovery call.
   Program wall budget: Case A 30s, Case B 60s. If the task needs more
   planned calls than the cap, STOP the run, mark it as a design miss
   in the run log, and report to Muse. Do not raise the cap.
4. Record think before EACH program call, not only the first: the wall
   time from the end of the previous model turn (or from task start for
   the first call) to the submit timestamp of that program call, as a
   run-log line per call. Do no exploratory observe between the end of
   the previous turn and a program submit except the observes the
   program itself performs; any exploratory observe before a program
   call is logged as its own run-log line and its think counts toward
   that call.
5. After each program call, log one act line per DOM action the program
   executed, including any in-program retries, using the same op
   vocabulary as the step-by-step arm. A program that retries internally
   without logging the retry breaks the run: if you cannot log a retry
   the program performed, STOP and report to Muse instead of hiding it.
   Log each retry as a retry line and each other recovery step as a
   recovery line, exactly once per corrective action.

## 6. Evidence per run (every run, both arms)

In runs/<run-id>/ write:
- run-log.jsonl: one JSON line per action/observation, schema in
  tests/realistic/a1-pilot/run-log-schema.md. Include run_start and
  run_end marker lines. Include every refusal, retry, recovery step,
  misclick, session death, and program call (with char count). Include
  step_index (1-based, sequential; run_start carries 0) and
  progress_marker (true when the line records a step completed, an
  artifact written, or a checker state changed) on every line.
  run_start detail includes case_task ("pick4" or "f01") and
  run_sequence (1-12, the run's position in the full 12-run sequence)
  so a learning trend is visible at analysis. The ARM label is NEVER
  in the run log. The case task name is allowed in run_start detail
  and nowhere else in the run directory.
- setup-log.jsonl: one line per between-run reset (fresh session,
  storage cleared, fixture reloaded, desktop verified clean). Never in
  run-log.jsonl.
- setup.json: git HEAD of the repo at run start, relay
  started_git_head plus the values of CU_CODE_EXEC and
  CU_PICK4_FASTPATH, broker-status output proving SOLO at run start,
  and md5 of both fixtures at run start.
- end-state.json: the final DOM state. Case A: {"result_text": ...}.
  Case B: {"C2", "C3", "C4", "E2", "E3", "E4", "E5", "E6", "E7"}.
- verify.png: the final verification screenshot (desktop observe image).
- commands.txt: JSONL, one line per broker call or program submit, with
  the full text of every program submitted inline. The char count in
  each program_submit line must equal the length of the corresponding
  program text here.
- verify_start / verify_end lines: log a verify_start line when the
  final verification phase begins and a verify_end line when it ends,
  bracketing the final verification only.
- Progress markers: one per run start, one per program submission, and
  one per 15 min of wall time.

A run missing any of the eight evidence items (run log, end state,
screenshot, commands, setup, setup log, verify image, progress markers)
is not counted; it is recorded as INCOMPLETE and re-run under a new
run-id.

Do NOT write the arm label or any hypothesis in the run directory. The
run directory contains only evidence.

## 7. If something goes wrong

- Refusal / stale observation / element not interactable: re-observe,
  retry, log it. A retry is a recovery step, not a failure. One
  corrective action is exactly one log line: a retry line if it repeats
  the same action, a recovery line otherwise, never both.
- Session death / broker error / browser crash: log one session_death
  line with the exact error text. ONE restart per run is allowed: the
  death is counted, the restart steps are recovery steps, and wall time
  keeps running. A second death in the same run ends the run as FAIL
  with run_end reason failed. A restart that itself fails to start ends
  the pilot: STOP, report to Muse, do not start the next run.
- A run with a start marker and no end marker within 30 minutes is
  declared DEAD by Muse (the watchdog reports it); a dead run-id is
  voided and replaced under a new run-id, and completed runs stand. Do
  not restart a dead run yourself.
- If the watchdog flags a stall (no progress marker for 15 min of wall),
  STOP work on that run, write the run_end marker with verdict "failed"
  and reason "killed", and report to Muse.
- If you are unsure about any step: STOP and ask Muse. Do not improvise.
  A stopped run with an honest log beats a finished run with a guessed
  step.

## 8. What you must NOT know (no-knowledge list)

You receive one run at a time: a run-id plus the arm procedure for
that run, and nothing else. After each run you report only that the
run finished and where its evidence directory is. You receive no
feedback before the next run. You must NOT know:

(a) which arm is expected to be faster;
(b) the GO bar (any percentage, any pass-rate rule, any recovery rule,
    any think rule);
(c) the wall time, pass/fail, or any metric of any completed run;
(d) any checker verdict;
(e) the sealed run-id mapping, its location, or any run-id to arm
    mapping beyond the run you are currently doing;
(f) the held-out task identity.

You DO know the procedure of the arm you are currently running.
This runbook contains procedure only: caps, timeouts, task values,
and the exact steps. It contains no hypothesis, no GO bar, and no
prior results. Do not read any pilot document other than this runbook and
its two named appendices (the run-log schema and the preflight probe
list). After the pilot, your transcript is checked for reads of other
pilot documents; any such read voids the affected runs.
