R3-L3 timeout watcher and kill procedure (precondition 8, Decision B).
Written 2026-11-24 17:30 +07 by the Phase 0 coordinator.

TASK TIMEOUT: 30 minutes per task (hard, speedup council decision).
The coordinator starts a wall-clock timer when the runner begins a task.
If the runner has not produced a completed evidence folder within 30 minutes,
the coordinator follows this procedure. No task runs past 30 minutes.

TIMEOUT WATCHER (how the coordinator watches):
- The coordinator records task_start (ISO 8601, +07) in the coordinator state
  file (rung3-run-log/r3-l3-coordinator-state.json) when the task is handed to
  the runner.
- The coordinator checks the runner session and the evidence folder at
  15 minutes (midpoint) and at 30 minutes (deadline).
- The runner is expected to report progress at least every 10 minutes. If the
  runner is silent for 15 minutes with no progress, the coordinator pokes it
  once (a short message asking for status). If it is still silent 5 minutes
  later, the coordinator treats it as stuck.
- The 30-minute deadline is absolute. A task that is 90 percent done at
  29 minutes still stops at 30 minutes. Partial evidence is kept and graded
  as-is (see partial-evidence rule below).

KILL PROCEDURE (what the coordinator does at 30 minutes):
1. Tell the runner to STOP the current task immediately (a short message in
   its session: "STOP. 30-minute timeout. Do not start anything else. Report
   what you have in the evidence folder now.").
2. Wait 2 minutes for the runner to stop and report.
3. If the runner does not stop, the coordinator kills its session:
   - FCC: tmux send-keys -t <runner-session> C-c, wait 10 seconds, then
     tmux kill-session -t <runner-session> if still running, then start a
     fresh FCC session (new tmux session, verify it responds) before the
     next task.
   - Codex: if using codex exec, the invocation is a single process; kill it
     with pkill -f "codex exec" (or kill the PID recorded at launch). If using
     an interactive session, tmux send-keys C-c, then kill-session if needed.
4. Freeze the evidence folder as-is (snapshot it with snapshot.py --name
   R3-xxx-L3). Do NOT delete partial evidence.
5. Run the manifest gate on the snapshot. If the gate FAILS (missing required
   files), the task is graded from whatever is in the snapshot (partial
   evidence rule). If the gate PASSES, grade normally.
6. Record the timeout in the coordinator state file and in the ledger row
   (timestamps.task_end = the 30-minute mark, and a note that the task timed
   out). The timeout itself is not a verdict; the grade comes from the
   evidence (PASS/FAIL/INVALID per the key).
7. The next task starts only after the timeout is fully recorded and the
   runner session is verified responsive again. Do not start the next task
   while the timed-out runner is still running.

PARTIAL-EVIDENCE RULE:
- A task that times out is graded on the evidence that exists at the timeout.
- If the evidence is enough to check against the key, grade PASS or FAIL.
- If the evidence is too incomplete to check (no ket-qua.txt, no screenshots,
  no deliverable), grade FAIL (incomplete), not INVALID. A timeout is a
  runner failure, not a task defect.
- A timeout does NOT consume a backup slot. Backups are only for INVALID
  tasks. A timed-out task is recorded as FAIL and the run continues to the
  next task.
- If the SAME runner times out twice in a row, the coordinator pauses the run
  and reports to the owner before continuing (the runner may be degraded).

TASKS EXPECTED TO EXCEED 30 MINUTES (from the R3-L2 timing data and the
planning council estimate; these are the tasks the coordinator watches most
closely, and the timeout applies to them the same as to all tasks):
- R3-003 (B-hybrid, 3 articles with Wayback fallbacks): R3-L2 took the full
  window and ended BLOCKED. If the runner cannot finish the 3-article table
  in 30 minutes, it stops and is graded on what exists.
- R3-040 (B-hybrid, Wayback + archive.org): R3-L2 retry took a long time
  (Wayback 429s). Same 30-minute cap.
- R3-042 (B-hybrid): similar multi-step web research.
- R3-041 (browser drag + 8 leak items): multi-step, watch the midpoint.
- R3-082 (omacalc, 5 values): if the tool is slow, the cap still applies.
- R3-096 (diff + merge): normally fast; if the runner stalls, cap applies.
- R3-100 (port check + HTML save): normally fast; cap applies.
This is not a permission to run long. Every task, including these, stops at
30 minutes. The list exists so the coordinator knows which tasks to check at
the 15-minute midpoint rather than waiting for the deadline.

NO EXCEPTIONS: the 30-minute timeout has no exceptions, no extensions, and no
owner override during the run. If a task genuinely needs more than 30 minutes
(the key says so), the coordinator reports that to the owner BEFORE the task
starts and the owner decides (exclude the task, or accept a FAIL). The
coordinator does not grant itself an extension.
