# R3-088 scorer brief, Clone2 (Pair B scorer 1, R3-L3, Class L, Tier B)

You are scorer 1 for task R3-088 (Pair B). Score independently from the
snapshot and the key only. Do not read scorer 2's verdict, the ledger row
for R3-088, or contact the runner.

## Inputs

- Snapshot (pushed to todolist-push before scoring):
  rung3-run-log/rung3-snapshots/R3-088-L3/. Verify manifest_sha256 and every
  per-file sha256 against manifest.json before scoring; record the manifest
  hash in your verdict.
- Key: docs/rung3-answer-keys.md, section "## R3-088 (Tier B)" plus the
  R3-088 task section in docs/rung3-list-100-tasks.md. Verify before
  scoring: md sha256
  21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60,
  json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8.
- Key facts (Tier B: the truth is the state at run time in the saved
  files): directory ~/rung3/nd28-work, 10 files nd28-file-01.txt to
  nd28-file-10.txt. Archive file ~/rung3/nd28-luu-tru.tar.gz. Extraction
  check directory ~/rung3/nd28-check. Entries in archive = 11 (root
  directory + 10 files). Files in archive (not counting the directory
  entry ending with /) = source file count (10). Files after extraction =
  source file count (10). The 3 compared files at fixed positions 1st,
  5th, 10th in sorted name order (nd28-file-01.txt, nd28-file-05.txt,
  nd28-file-10.txt) correct content. Report ~/rung3/nd28-bao-cao.txt with:
  source file count, entries in archive (11), files in archive (10), files
  after extraction, the 3-file comparison results. Grading evidence: the
  tar.gz file (a copy is in the snapshot) + the report. List the files in
  the archive and count them yourself.

## Grade

PASS: entries in archive = 11 (including root directory), files in archive
= source file count (10), files after extraction = source file count, 3
compared files correct content, report correct numbers, tar.gz file exists.
FAIL: missing file in archive, wrong file count after extraction, compared
file wrong content, report wrong numbers, or a compression format other
than tar.gz used.
INVALID only if the evidence cannot be judged. Before any INVALID verdict,
record whether the infrastructure re-run path was considered (mandatory
from epoch 23).

## Deliverables (30 minutes)

- Verdict JSON + grade markdown, filed on branch clone2/verdict-R3-088-L3
  under rung3-run-log/verdicts/R3-088-L3/ (verdict, session, timestamp +07,
  key hashes, manifest hash, reason, files_read,
  infrastructure_rerun_considered, counted values). The coordinator copies
  them locally and audits.
- English only. No personal info anywhere.
- LOGGING (owner rule 18:20): log every event with the full chain:
  failure -> reasoning -> attempts -> decision -> fix -> outcome.
