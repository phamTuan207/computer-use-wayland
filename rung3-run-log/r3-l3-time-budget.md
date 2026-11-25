R3-L3 time budget and checkpoint decision rule.
Written 2026-11-24 17:39 +07 by the Phase 0 coordinator.

HONEST RUN ESTIMATE: 19 to 31 hours (planning council, execution plan
section 12). Staff for 31 hours. Do NOT promise 20 hours. The 19-hour
figure is the optimistic case (no timeouts, no INVALIDs, no disputes, no
re-runs). The 31-hour figure is the staffed case (timeouts, disputes,
INVALID handling, ledger pushes, and the normal friction of a 55-task run).

BREAKDOWN (for the coordinator to track against):
- 55 tasks, mean cycle time is the driver. At 19 hours the mean is about
  21 minutes per task (run + snapshot + gate + score + reset). At 31 hours
  the mean is about 34 minutes per task. The speedup (decoupled scoring,
  2 scorer pairs, snapshot-freeze gate) is what makes the lower end
  possible; without it the run would be longer.
- Class L tasks (9) are slower per task (score-before-reset, runner waits).
  Class S tasks (46) are faster (decoupled, runner proceeds after the
  snapshot gate). The coordinator tracks Class L and Class S cycle times
  separately so a slowdown in one class is visible.
- Timeouts (30 minutes each) add time. Each timeout costs up to 30 minutes
  of runner time plus the snapshot/gate/score time. Budget for up to 3
  timeouts in the 31-hour figure.

CHECKPOINT AFTER THE 3RD GRADED TASK:
- After the 3rd task is graded (not after the 3rd task runs, after the 3rd
  GRADE enters the ledger), the coordinator computes:
  (a) the revised run-complete estimate = (mean cycle time of the 3 graded
      tasks) x 55, and
  (b) whether the mean cycle time exceeds the plan estimate by more than
      25 percent.
- If the revised run-complete estimate is OUTSIDE 19-31 hours (i.e. the
  run will take longer than 31 hours at the current pace) OR the mean cycle
  time exceeds the plan estimate by more than 25 percent, the coordinator
  PAUSES the run and reports to the owner with options (continue at the
  slower pace, reduce scope, change the scoring approach, or stop). The run
  continues ONLY on the owner's decision.
- If the revised estimate is inside 19-31 hours and the mean cycle time is
  within 25 percent of the plan estimate, the coordinator continues without
  reporting (the checkpoint is passed, recorded in the state file).
- The checkpoint is mandatory. The coordinator does not skip it because
  the first 3 tasks went well. It is the only early warning that the run
  will overrun.

TRACKING: the coordinator records each task's cycle time (task_start to
recorded_at in the ledger row) and updates the running mean in the
coordinator state file after every task. The state file is the source of
truth for the checkpoint computation.
