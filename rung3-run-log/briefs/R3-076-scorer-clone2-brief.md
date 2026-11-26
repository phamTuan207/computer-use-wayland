# R3-076 scorer brief, Clone2 (Pair B scorer 2, R3-L3, Class S, Tier B)

You are scorer 2 for task R3-076 (Pair B). Score independently from the
snapshot and the key only. Do not read scorer 1's verdict, the ledger row
for R3-076, or contact the runner.

Note: this seat was reassigned from Clone1 to you under the owner order of
2026-11-26 21:36 (Clone2 main burner; Clone1/Mochi reduced). Disjointness
re-checked: prep Mei, scorers Fresh + Clone2, reviewer Mochi.

## Inputs

- Snapshot (pushed to todolist-push before scoring):
  rung3-run-log/rung3-snapshots/R3-076-L3/. Verify manifest_sha256 and every
  per-file sha256 against manifest.json before scoring; record the manifest
  hash in your verdict.
- Key: docs/rung3-answer-keys.md, section "## R3-076 (Tier B, kem script
  kiem tra nhat quan bao cao)". Verify before scoring: md sha256
  21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60,
  json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8.
- Expected per key: the report d42-bao-cao.txt has 3 sections (free disk,
  free RAM, table of 5 processes with name, PID, CPU, RAM) plus a recording
  time. The disk and RAM numbers in the report must match the saved
  timestamped command files (d42-lenh-dia.txt, d42-lenh-ram.txt). The
  5-process table must match d42-lenh-tien-trinh.txt (name and PID of all
  5 processes present in the command file). Disk/RAM/process values are
  LIVE at run time; there are NO frozen expected values. Do NOT re-run
  the commands to get new values (RAM changes between runs); compare the
  report ONLY against the saved command files. Evidence: d42-bao-cao.txt +
  the 3 command files. The coordinator runs tier-a-check.py (type
  report-consistency) on the snapshot and hands the output identically to
  both scorers. If the checker output and your own reading disagree, say
  so in your grade (do not silently override).

## Grade

PASS: report has all 3 sections + recording time; disk/RAM numbers match
the saved command files; the 5-process table has name, PID, CPU, RAM for
all 5 processes matching the saved command file.
FAIL: missing section, numbers differ from the saved command files, table
missing a process or a column, recording time missing, command file
missing.
INVALID only if the evidence cannot be judged. Before any INVALID verdict,
record whether the infrastructure re-run path was considered (mandatory
from epoch 23).

## Deliverables (30 minutes)

- Branch: clone2/verdict-R3-076-L3 with two files under
  rung3-run-log/verdicts/R3-076-L3/: R3-076-L3-clone2.json (verdict,
  session, timestamp +07, key hashes, manifest hash, reason, files_read,
  infrastructure_rerun_considered) and R3-076-L3-clone2-grade.md (full
  grade with independence declaration). Push the branch; the coordinator
  verifies delivery by the branch landing.
- English only. No personal info anywhere.
- LOGGING (owner rule 18:20): log every event with the full chain:
  failure -> reasoning -> attempts -> decision -> fix -> outcome.
