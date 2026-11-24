Calibration exposure limitation (precondition 22).
Written 2026-11-24 17:40 +07 by the Phase 0 coordinator.

LIMITATION: the 4-task calibration (R3-041, R3-002, R3-003, R3-067) proves a
scorer can grade those 4 task types correctly. It does NOT prove the scorer
can grade all 55 tasks. The calibration covers:
- R3-041: a browser task (drag + 8 leak items, screenshot + ket-qua.txt).
- R3-002: a file/JSON task (error columns in ket-qua.txt).
- R3-003: a B-hybrid task (online doc, BLOCKED, incomplete deliverable).
- R3-067: a Tier C synthetic image task (shapes, colors, regions, measured
  with PIL).
It does NOT cover:
- Tier A checker tasks (R3-002 is Tier A but the calibration only covers
  its ket-qua.txt columns, not running the Tier A checker itself).
- Class L live re-read tasks (the calibration uses sealed snapshots; a Class
  L grade requires a live re-read, which the calibration does not test).
- INVALID decisions (the calibration tasks have a known final grade; the
  scorer is not tested on deciding INVALID vs FAIL for a new task).
- Scorer disputes and tiebreaker decisions (the calibration is single-scorer
  per task; the pair-agreement and tiebreaker flow is not calibrated).
- Tasks the scorer has not seen (the other 51 tasks use the same evidence
  contract, but the scorer's first grade of a new task type is uncalibrated).

WHAT THIS MEANS FOR THE RUN:
- A scorer who passes calibration is approved to grade, but the coordinator
  audits the scorer's first 2 grades of each new task type (Tier A, Tier C,
  B-hybrid, Class L) before those grades enter the ledger. The audit is the
  manifest-gate + audit-scan + the coordinator reading the grade and
  confirming it cites the key correctly.
- If a scorer's grade is overturned on audit (the coordinator finds the
  grade does not match the key), the coordinator re-assigns the task to the
  other scorer in the pair and records the overturn. Two overturns for the
  same scorer trigger a re-calibration (the scorer re-does the 4-task
  calibration before grading again).
- The calibration is a gate, not a guarantee. The coordinator's audit is the
  guarantee. No grade enters the ledger without the coordinator's audit
  (manifest gate + audit scan + a read of the grade).
- This limitation is recorded here so no one over-claims what calibration
  proves. The run's accuracy comes from the evidence contract + independent
  scoring + coordinator audit, not from calibration alone.
