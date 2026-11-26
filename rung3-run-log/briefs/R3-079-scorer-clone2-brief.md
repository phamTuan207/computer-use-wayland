# R3-079 scorer brief, Clone2 (Pair B scorer 2, R3-L3, Class L, Tier B)

You are scorer 2 for task R3-079 (Pair B). Score independently from the
snapshot and the key only. Do not read scorer 1's verdict, the ledger row
for R3-079, or contact the runner.

## Inputs

- Snapshot (pushed to todolist-push before scoring):
  rung3-run-log/rung3-snapshots/R3-079-L3/. Verify manifest_sha256 and every
  per-file sha256 against manifest.json before scoring; record the manifest
  hash in your verdict.
- Key: docs/rung3-answer-keys.md, section "## R3-079 (Tier B)". Verify
  before scoring: md sha256
  21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60,
  json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8.
- Expected per key: backup folder ~/rung3/d46-backup with 2 dated backups
  (2026-11-20 and 2026-11-22), each containing bao-cao-tuan.txt. The
  request file d46-yeu-cau.txt asks to restore bao-cao-tuan.txt from the
  2026-11-22 backup into ~/rung3/d46-restored. Correct content: week 47,
  revenue 12500000, orders 320 (NOT week 46: revenue 9800000, orders 275).
  The current file in the work folder must not be overwritten. The report
  contains the file name, the backup date (2026-11-22), and the comparison
  result against manifest.txt. Grading evidence: the restored file + the
  report; the scorer opens the restored file and compares it with the
  manifest.

## Grade

PASS: file restored from the correct dated backup (2026-11-22), content
matches the manifest (week 47, 12500000, 320), current work-folder file
not overwritten, report correct (file name, date 2026-11-22, comparison
result).
FAIL: restored from the wrong backup, content does not match the manifest,
current file overwritten, report has the wrong date.
INVALID only if the evidence cannot be judged. Before any INVALID verdict,
record whether the infrastructure re-run path was considered (mandatory
from epoch 23).

## Deliverables (30 minutes)

- Branch: clone2/verdict-R3-079-L3 with two files under
  rung3-run-log/verdicts/R3-079-L3/: R3-079-L3-clone2.json (verdict,
  session, timestamp +07, key hashes, manifest hash, reason, files_read,
  infrastructure_rerun_considered) and R3-079-L3-clone2-grade.md (full
  grade with independence declaration). Push the branch; the coordinator
  verifies delivery by the branch landing.
- English only. No personal info anywhere.
- LOGGING (owner rule 18:20): log every event with the full chain:
  failure -> reasoning -> attempts -> decision -> fix -> outcome.
