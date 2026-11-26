# R3-078 scorer brief, Fresh (Pair B scorer 2, R3-L3, Class L, Tier B)

You are scorer 2 for task R3-078 (Pair B), a fresh independent session.
Score independently from the snapshot and the key only. Do not read scorer
1's verdict, the ledger row for R3-078, or contact the runner.

## Inputs

- Snapshot (pushed to todolist-push before scoring):
  rung3-run-log/rung3-snapshots/R3-078-L3/. Verify manifest_sha256 and every
  per-file sha256 against manifest.json before scoring; record the manifest
  hash in your verdict.
- Key: docs/rung3-answer-keys.md, section "## R3-078 (Tier B)". Verify
  before scoring: md sha256
  21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60,
  json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8.
- Expected per key: work folder ~/rung3/d45-work with 10 files
  d45-file-01.txt .. d45-file-10.txt; backup folder ~/rung3/d45-backup.
  Backup file count equals original count (10), structure kept, checksums
  match for all files (0 wrong). The backup list has all rows (10 rows:
  file name, size, checksum). The 3 fixed-position files (1st, 5th, 10th
  by name order: d45-file-01.txt, d45-file-05.txt, d45-file-10.txt) have
  contents matching the originals. Grading evidence: the backup list file
  + the report; the scorer checks the file count and compares checksums of
  the 3 fixed files.

## Grade

PASS: backup count 10 = original count, structure kept, checksums match
all files, list has 10 rows, the 3 fixed-position files correct.
FAIL: backup file missing, wrong structure, checksum wrong on more than
0 files, list missing rows, fixed-position file content wrong.
INVALID only if the evidence cannot be judged. Before any INVALID verdict,
record whether the infrastructure re-run path was considered (mandatory
from epoch 23).

## Deliverables (30 minutes)

- Files: ~/workspace/rung3-verdicts/R3-078-B2.json (verdict, session,
  timestamp +07, key hashes, manifest hash, reason, files_read,
  infrastructure_rerun_considered) and
  ~/workspace/rung3-verdicts/R3-078-B2-grade.md (full grade with
  independence declaration).
- If git is blocked for you, do NOT retry through other routes: write the
  two files above and report the paths to the coordinator, who lands them.
- English only. No personal info anywhere.
- LOGGING (owner rule 18:20): log every event with the full chain:
  failure -> reasoning -> attempts -> decision -> fix -> outcome.
