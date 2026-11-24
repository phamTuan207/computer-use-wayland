R3-L3 coupled-task checks (precondition 16).
Written 2026-11-24 17:33 +07 by the Phase 0 coordinator.

COUPLED TASKS are tasks whose evidence or fixtures overlap, so a reset or a
re-run of one affects the other. The coordinator checks these explicitly
before the second task of each pair runs.

PAIR 1: R3-078 and R3-079 (positions 42 and 43, both Codex, back to back).
- Coupling: both use the d45/d46 backup-and-restore fixtures. R3-078 creates
  a backup in ~/rung3/d45-backup. R3-079 restores from a backup into
  ~/rung3/d46-restored.
- Check before R3-079 starts: after R3-078 is scored and the reset runs,
  confirm ~/rung3/d45-backup is gone (reset restored it) and
  ~/rung3/d46-restored does not exist yet. Then confirm the d46 fixture
  files are present in ~/rung3-goc/ (the source). If d45-backup still exists
  after the reset, the reset failed; do NOT start R3-079, report to the
  owner, and fix the reset first.
- Pass criteria: (a) R3-078 snapshot gate PASS and R3-078 graded; (b) after
  reset, ls ~/rung3/d45-backup returns "No such file" and
  ls ~/rung3/d46-restored returns "No such file"; (c) the d46 fixture is
  intact in ~/rung3-goc/. Fail criteria: any of (a), (b), (c) fails. On
  fail, stop, do not start R3-079.
- Both are Class L (score-before-reset), so the runner waits for the grade
  before the reset in each case. This removes most of the coupling risk.

PAIR 2: R3-067 and R3-083 (positions 37 and 44, both Tier C image tasks).
- Coupling: both are Tier C (image comparison) tasks graded from a saved PNG.
  They do not share fixtures or files. The coupling is only that both use
  the same Tier C grading rubric (the scorer compares the runner's PNG
  against the key's expected image pixel by pixel / region by region).
- Check before R3-083 starts: confirm R3-067 was graded and its snapshot
  (R3-067-L3) is sealed and the gate passed. Confirm the R3-083 fixture
  (the source image the runner edits) is intact in ~/rung3-goc/ and has not
  been modified by R3-067 (R3-067 works on a different file; verify by
  sha256 against the fixture record).
- Pass criteria: (a) R3-067 snapshot gate PASS and R3-067 graded; (b) the
  R3-083 source fixture sha256 matches the fixture record; (c) no file in
  ~/rung3/ is left over from R3-067 (diff -r -q ~/rung3/ ~/rung3-goc/ is
  empty after the reset). Fail criteria: any fails. On fail, stop, do not
  start R3-083, fix the fixture/reset first.
- Both are Class S (snapshot-sufficient), so scoring is decoupled and the
  coupling is only via the fixture, which the reset restores.

GENERAL RULE for all tasks (not just these pairs):
- Before ANY task starts, the coordinator runs diff -r -q ~/rung3/
  ~/rung3-goc/ and confirms it is empty (the workspace matches the fixture).
  If it is not empty, the reset from the previous task failed; do not start
  the next task.
- After ANY task, the coordinator snapshots the evidence, runs the manifest
  gate, grades (or queues the grade), then resets, then re-runs the diff to
  confirm the workspace is clean before the next task.
- The reset is: restore ~/rung3/ from ~/rung3-goc/ (copy the fixture back)
  and clear ~/rung3-chung-cu/R3-xxx/ for the task just run. The reset must
  not touch ~/rung3-goc/ (the source of truth).
