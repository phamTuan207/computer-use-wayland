# A1 pilot runbook (for the executor only)

- Pilot: A1 narrow pilot. Plan: improvements/worker-a1-pilot-plan.md.
- You are the EXECUTOR. You run 12 runs and nothing else. You do NOT
  read the plan, the hypothesis, or any pilot numbers. This runbook is
  your only instruction. Do not go looking for the plan.
- Executor: ONE Codex (Luna 6 Max) session on the owner's laptop, broker
  SOLO. The same session runs all 12 runs. If the session dies, STOP and
  report to Muse immediately; do not restart it yourself (a restart voids
  the pre-registration, see the plan).
- Sequencing: no run starts until Muse gives the resume order.

## 0. Setup (once, before run 1)

1. SSH to the laptop is already available to you; the broker runs there.
   Work in a fresh run directory on the laptop: /tmp/a1-pilot-20261121/.
2. Ship the fixtures from the VM repo to the laptop and verify checksums:
   - tests/realistic/a1-pilot/fixtures/pick4-fixture.html,
     md5 must be 91b2f92945c167306a13ae32977a9bf3.
   - tests/realistic/fcc-k/fixtures/test-01-spreadsheet.html (record its
     md5 in the setup log; it must match the VM repo copy).
   Serve them over the local HTTP server on 127.0.0.1:8768, same pattern
   as the existing runners. Record the exact URLs in the setup log.
3. Verify the broker is SOLO and idle (no other session, no other runner).
   Verify managed Chromium starts via the code-exec DOM path (one
   dom_start probe, no fixture). Record the endpoint in the setup log.
4. Create runs/ under /tmp/a1-pilot-20261121/. For each run, create
   runs/<run-id>/ where <run-id> is a random 8-hex string you generate
   at run start. Write ONE line per run to runs/manifest-sealed.jsonl:
   {"run_id", "case", "arm", "run_number", "started_at"}. NEVER write
   the arm label anywhere inside a run directory. NEVER open the
   manifest after writing it.

## 1. Run order (fixed, do not change)

Per case, in this order: Case A runs 1-6, then Case B runs 1-6.
Within each case: STEP, CODE, STEP, CODE, STEP, CODE.
So the full order is: A1-STEP, A1-CODE, A2-STEP, A2-CODE, A3-STEP,
A3-CODE, B1-STEP, B1-CODE, B2-STEP, B2-CODE, B3-STEP, B3-CODE.

Between runs: fresh browser session, storage cleared, fixture reloaded,
desktop verified clean. Log each reset as a run-log line.

## 2. Case A task (both arms)

Open the Pick 4 fixture in the managed browser, click the "Show result"
button, verify #result contains "pick4-ok". Leave the name field empty.

## 3. Case B task (both arms)

Follow tests/realistic/fcc-k/test-01-spreadsheet-formula.md steps 1-26
exactly: enter 5 sales rows, write SUM / AVERAGE / COUNT formulas,
notice the COUNT formula returns text instead of a number, fix it to
COUNTA, confirm E5=1864000, E6=621333, E7=3. Record all end-state cell
values (C2, C3, C4, E2, E3, E4, E5, E6, E7).

## 4. Arm STEP (step-by-step)

Drive through the broker one tool call per step. Observe, act, observe,
act. No code-exec, no program calls, no batching. One model turn per
broker call. If an action is refused (stale observation, element not
interactable), re-observe and retry; log the refusal and the retry as
run-log lines. Do not skip steps. Do not invent shortcuts.

## 5. Arm CODE (code-exec program)

1. Think, then compose a program that does the whole task. Compose it
   FRESH for this run, from the task description above and the template
   rules below. NEVER copy a program from any example, file, or earlier
   run verbatim. Copying a program verbatim voids the run; if you catch
   yourself doing it, stop and report to Muse.
2. Template rules (from improvements/a1-code-exec-dom-design.md):
   - Start the managed browser, look up its window, observe it, navigate
     with one desktop act (Ctrl+L, type the URL, Enter), observe again.
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
3. Caps: each program at most 8192 chars. At most 3 program calls per
   run. Record the char count of every program and the number of program
   calls in the run log. If the task needs more than 3 program calls,
   STOP the run, mark it as a design miss in the run log, and report to
   Muse. Do not raise the cap.
4. Record think-before-first-program-call: the wall time from run start
   to the first program submit, as a run-log line.

## 6. Evidence per run (every run, both arms)

In runs/<run-id>/ write:
- run-log.jsonl: one JSON line per action/observation, schema in
  tests/realistic/a1-pilot/run-log-schema.md. Include run_start and
  run_end marker lines. Include every refusal, retry, recovery step,
  misclick, session death, and program call (with char count).
  run_start detail includes run_sequence (1-12, the run's position in
  the full 12-run sequence) so a learning trend is visible at analysis.
- provenance.json: git HEAD of the repo at run start, relay
  started_git_head plus the values of CU_CODE_EXEC and
  CU_PICK4_FASTPATH, broker-status output proving SOLO at run start,
  and md5 of both fixtures at run start. A run missing any of the
  eight evidence items (run log, end state, screenshot, commands,
  provenance) is not counted in n=3; it is recorded as INCOMPLETE and
  re-run under a new run-id.
- end-state.json: the final DOM state. Case A: {"result_text": ...}.
  Case B: {"C2", "C3", "C4", "E2", "E3", "E4", "E5", "E6", "E7"}.
- verify.png: the final verification screenshot (desktop observe image).
- commands.txt: the exact commands run (broker calls / program submits).
Do NOT write the arm label, the case label, or any hypothesis in the run
directory. The run directory contains only evidence.

## 7. If something goes wrong

- Refusal / stale observation / element not interactable: re-observe,
  retry, log it. A retry is a recovery step, not a failure.
- Session death / broker error / browser crash: STOP the run, mark it
  failed in the run log with the exact error text, report to Muse, and
  wait for instructions. Do not start the next run.
- A run that takes more than 30 minutes wall: STOP work, write the
  run_end marker with verdict "failed" and reason "timeout", and
  report to Muse. Do not let a run hang. A run with a start marker
  and no end marker within 30 minutes is declared DEAD by Muse (the
  watchdog reports it); a dead run-id is voided and replaced under a
  new run-id, and completed runs stand. Do not restart a dead run
  yourself.
- If you are unsure about any step: STOP and ask Muse. Do not improvise.
  A stopped run with an honest log beats a finished run with a guessed
  step.

## 8. What you must NOT know (no-knowledge list)

You receive one run at a time: a run-id plus the arm procedure for
that run, and nothing else. After each run you report only that the
run finished and where its evidence directory is. You receive no
feedback before the next run. You must NOT know:

(a) which arm is expected to be faster;
(b) the GO bar (any percentage, any pass-rate rule, any recovery rule);
(c) the wall time, pass/fail, or any metric of any completed run;
(d) any checker verdict;
(e) the sealed run-id mapping, its location, or any run-id to arm
    mapping beyond the run you are currently doing;
(f) the held-out task identity.

You DO know the procedure of the arm you are currently running.
This runbook contains procedure only: caps, timeouts, task values,
and the exact steps. It contains no hypothesis, no GO bar, and no
prior results.
