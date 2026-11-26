# R3-072 scorer brief, Clone1 (Pair B scorer 2, R3-L3, Class S, Tier A)

You are scorer 2 for task R3-072 (Pair B). Score independently from the
snapshot and the key only. Do not read scorer 1's verdict, the ledger row
for R3-072, or contact the runner. (Your calibration sign-off is on file:
rung3-run-log/r3-l3-clone1-calibration-signoff-20261126.md; your first real
scoring was R3-037.)

## Inputs

- Snapshot (pushed to todolist-push before scoring):
  rung3-run-log/rung3-snapshots/R3-072-L3/. Verify manifest_sha256 and every
  per-file sha256 against manifest.json before scoring; record the manifest
  hash in your verdict.
- Key: docs/rung3-answer-keys.md, section "## R3-072 (Tier A)". Verify
  before scoring: md sha256
  21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60,
  json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8.
- Expected (folder order): d72-anh-1.png 800x600; d72-anh-2.png 1024x768;
  d72-anh-3.png 640x480; d72-anh-4.png 1280x720; d72-anh-5.png 400x400.
  Sizes written as width x height, spaces around x accepted.
- Tier A: the coordinator runs tier-a-check.py on ket-qua.txt and hands the
  output identically to both scorers. Your job: confirm the evidence files
  exist in the snapshot, the overlay screenshot is readable and shows image
  1's file name + size, ket-qua.txt has exactly 5 rows in folder order, and
  the Tier A output matches what you see. If the checker output and your
  own reading disagree, say so in your grade (do not silently override).

## Grade

PASS: ket-qua.txt has all 5 rows with correct file names + sizes in folder
order, and the overlay screenshot of image 1 is present and readable.
FAIL: missing row, wrong name, wrong size, wrong order, missing/unreadable
overlay screenshot, or a different viewer used without a recorded reason.
INVALID only if the evidence cannot be judged. Before any INVALID verdict,
record whether the infrastructure re-run path was considered (mandatory
from epoch 23).

## Deliverables (30 minutes)

- Branch: clone1/verdict-R3-072-L3
- Files: rung3-run-log/verdicts/R3-072-L3/R3-072-L3-clone1.json (verdict,
  session, timestamp +07, key hashes, manifest hash, reason, files_read,
  infrastructure_rerun_considered) and
  rung3-run-log/verdicts/R3-072-L3/R3-072-L3-clone1-grade.md (full grade
  with independence declaration).
- Push with explicit pathspec on add AND commit (never git add -A), verify
  via ls-remote, then tell the coordinator the branch name (no verdict
  value in the subject). English only. No personal info on GitHub.
- LOGGING (owner rule 18:20): log every event with the full chain:
  failure -> reasoning -> attempts -> decision -> fix -> outcome.
