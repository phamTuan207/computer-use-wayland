R3-L3 ledger push job and append/push protocol (precondition 20, and the
append/push part of precondition 11).
Written 2026-11-24 17:37 +07 by the Phase 0 coordinator.

LEDGER: rung3-run-log/R3-L3-grades.jsonl (on todolist-push). One JSON object
per line. Schema: rung3-ci/ledger-schema.json. Validator:
rung3-ci/validate-ledger.py. The ledger currently has 1 trial row
(test_row=true, task_id R3-TEST), validated PASS 2026-11-24 17:20 +07.
The trial row stays in the file (it proves the schema); real rows are
appended after it. The trial row is never counted as a grade.

APPEND PROTOCOL (the coordinator appends a row as soon as a task is graded):
1. The coordinator builds the row (task_id, run_code R3-L3, runner_session,
   scorer1 {session, verdict, keyfile_sha256, files_read}, scorer2 {session,
   verdict}, scorer3 if needed, final_grade, invalid {is_invalid, reason,
   backup_task}, evidence_manifest_hash, timestamps {task_start, task_end,
   scored1_at, scored2_at, recorded_at}, test_row false).
2. The coordinator checks the file ends with a newline. If the last line has
   no trailing newline, the coordinator adds one first (otherwise the new
   row glues onto the previous row and the file fails to parse).
3. The coordinator appends the row (one line, JSON, sorted keys).
4. The coordinator parse-verifies the whole file immediately: every line
   must parse as JSON, and validate-ledger.py must exit 0. If it fails, the
   coordinator fixes the file before doing anything else.
5. The coordinator appends LOCALLY immediately (the row is in the local
   worktree file the moment it is graded). The push to GitHub is async (see
   push job below).

PUSH JOB (ledger push to GitHub, at least hourly and immediately on
INVALID/dispute):
- The coordinator pushes the ledger to todolist-push at least once per hour
  during the run, and IMMEDIATELY (within 5 minutes) when a row is INVALID
  or when a scorer dispute is recorded (scorer 1 and scorer 2 disagree and
  a tiebreaker is invoked).
- How: the coordinator commits the ledger file (explicit pathspec, bare
  commit, never git add -A) and pushes, then verifies with
  git ls-remote origin todolist-push. The push is verified, not assumed.
- If the push fails (network, auth, conflict), the coordinator retries in
  5 minutes, then in 15 minutes, then reports to the parent agent. The
  local ledger file is the source of truth while the push is pending; no
  grade is lost if the push is delayed, but the coordinator must not let
  the push lag more than 1 hour (the hourly rule).
- The push job is MANUAL (the coordinator does it), not a cron, because the
  coordinator is the only one who knows when a row is graded and when an
  INVALID/dispute needs an immediate push. A cron would push on a timer
  regardless of whether a row was just graded. The coordinator sets a
  reminder to push at least hourly.
- RETRY RULE: if a push fails, retry after 5 minutes. If it fails again,
  retry after 15 minutes. If it fails a third time, escalate to the parent
  agent (Muse) with the error message and the local ledger file path. Do not
  keep retrying silently.
- ESCALATION: if the ledger cannot be pushed for more than 2 hours, the
  coordinator pauses the run (does not start new tasks) and reports to the
  parent. The grades already recorded locally are safe, but the run should
  not continue grading tasks whose rows cannot be published.

LEDGER PUSH JOB (record):
- Method: manual push by the coordinator (see above), at least hourly,
  immediately on INVALID/dispute.
- Verified: the trial row was committed and validated (validate-ledger.py
  exit 0). The push mechanism (explicit pathspec, bare commit, ls-remote
  verify) is the same as the rest of the run-log commits and will be proven
  when the Phase 0 files are committed and pushed.
