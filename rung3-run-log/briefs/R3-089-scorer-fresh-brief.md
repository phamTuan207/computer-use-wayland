# R3-089 scorer brief, Fresh (Pair B scorer 2, R3-L3, Class L, Tier B)

You are scorer 2 for task R3-089 (Pair B), a fresh independent session.
Score independently from the snapshot and the key only. Do not read scorer
1's verdict, the ledger row for R3-089, or contact the runner.

Note: this seat pairing is Clone2 + Fresh. The F5.2 table had Mochi +
Clone2; Mochi was reassigned under the owner order of 2026-11-26 21:36
(Mochi reduced). Prep for this task was coordinator-live, so no
disjointness issue.

## Inputs

- Snapshot (pushed to todolist-push before scoring):
  rung3-run-log/rung3-snapshots/R3-089-L3/. Verify manifest_sha256 and every
  per-file sha256 against manifest.json before scoring; record the manifest
  hash in your verdict.
- Key: docs/rung3-answer-keys.md, section "## R3-089 (Tier B)" plus the
  R3-089 task section in docs/rung3-list-100-tasks.md. Verify before
  scoring: md sha256
  21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60,
  json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8.
- Key facts (Tier B: the truth is the state at run time in the saved
  files): directory ~/rung3/nd09-logs, 12 .log files. Line counts: log-01
  50, log-02 65, log-03 80, log-04 95, log-05 110, log-06 125, log-07 140,
  log-08 155, log-09 170, log-10 185, log-11 195, log-12 200 (total 1570).
  Modification times: log-01 to log-06 are 1 day old, log-07 to log-12 are
  10 days old (anchor 2026-11-23 19:20). `find -mtime -7` returns exactly
  6 files: log-01 to log-06. Report ~/rung3/nd09-bao-cao.txt: total 6
  files, table of path, line count, modification date per file, sorted
  descending by line count (log-06 125, log-05 110, log-04 95, log-03 80,
  log-02 65, log-01 50). The runner re-runs find a second time; the count
  must match. Grading evidence: the report nd09-bao-cao.txt (a copy is in
  the snapshot). NOTE: modification dates in the report are run-time
  values; judge them against the fixture rule (6 files within 7 days), not
  against today's dates.

## Grade

PASS: report has the correct file count as the find command (6), each file
with path, line count, modification date, descending order by line count
correct, second find run matches the count.
FAIL: missing file, wrong line count, wrong modification date, wrong
order, report wrong total file count.
INVALID only if the evidence cannot be judged. Before any INVALID verdict,
record whether the infrastructure re-run path was considered (mandatory
from epoch 23).

## Deliverables (30 minutes)

- Files: ~/workspace/rung3-verdicts/R3-089-B2.json (verdict, session,
  timestamp +07, key hashes, manifest hash, reason, files_read,
  infrastructure_rerun_considered, counted values) and
  ~/workspace/rung3-verdicts/R3-089-B2-grade.md (full grade with
  independence declaration).
- If git is blocked for you, do NOT retry through other routes: write the
  two files above and report the paths to the coordinator, who lands them.
- English only. No personal info anywhere.
- LOGGING (owner rule 18:20): log every event with the full chain:
  failure -> reasoning -> attempts -> decision -> fix -> outcome.
