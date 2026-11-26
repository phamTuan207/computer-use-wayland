# R3-083 scorer brief, Fresh 1 (Pair B scorer 1, R3-L3, Class S, Tier C)

You are scorer 1 for task R3-083 (Pair B), a fresh independent session.
Score independently from the snapshot and the key only. Do not read scorer
2's verdict, the ledger row for R3-083, or contact the runner.

Note: this seat pairing is Fresh + Fresh. The F5.2 table had Fresh +
Clone1; Clone1 was reassigned under the owner order of 2026-11-26 21:36
(Clone1 reduced), and Clone2 cannot score this task because he prepped it
(disjointness). Two independent fresh sessions score instead (R3-046
precedent).

## Inputs

- Snapshot (pushed to todolist-push before scoring):
  rung3-run-log/rung3-snapshots/R3-083-L3/. Verify manifest_sha256 and every
  per-file sha256 against manifest.json before scoring; record the manifest
  hash in your verdict.
- Key: docs/rung3-answer-keys.md, Tier C rubric section "### R3-083 (anh
  bia trong Pinta, 1200x628, nen chuyen sac, chu lon o giua)" plus the
  R3-083 task section. Verify before scoring: md sha256
  21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60,
  json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8.
- Rubric (both scorers use the same rubric; grade by measurement, not
  taste): background MUST be a gradient from #1E88E5 at the top to
  #43A047 at the bottom; both colors must appear in the background (blue
  top, green bottom); a solid single-color background is wrong; a
  gradient with 2 other colors is wrong. Text MUST be "Chao mung", white,
  font size 72, centered in x 300-900, y 250-380, tolerance 50 px (the
  text center inside that region); wrong content, wrong color, clearly
  wrong size (much smaller than 72), or outside the region beyond
  tolerance is wrong. File size MUST be 1200x628, format PNG. Wrong
  counts as: background not a gradient; either color wrong; text missing;
  text content wrong; text not white; text outside the region; wrong
  size; not PNG. Grading evidence: anh-bia.png + ket-qua.txt + screenshot
  of the cover image. Measure the PNG directly (dimensions, sample top
  and bottom background colors, locate the text and its center).

## Grade

PASS: correct size 1200x628 PNG, gradient background with the 2 correct
colors, text "Chao mung" white, size 72, inside the region (with
tolerance).
FAIL: any rubric item wrong per the definitions above.
INVALID only if the evidence cannot be judged. Before any INVALID verdict,
record whether the infrastructure re-run path was considered (mandatory
from epoch 23).

## Deliverables (30 minutes)

- Files: ~/workspace/rung3-verdicts/R3-083-B1.json (verdict, session,
  timestamp +07, key hashes, manifest hash, reason, files_read,
  infrastructure_rerun_considered, measured values: dimensions, top/bottom
  colors, text center) and
  ~/workspace/rung3-verdicts/R3-083-B1-grade.md (full grade with
  independence declaration).
- If git is blocked for you, do NOT retry through other routes: write the
  two files above and report the paths to the coordinator, who lands them.
- English only. No personal info anywhere.
- LOGGING (owner rule 18:20): log every event with the full chain:
  failure -> reasoning -> attempts -> decision -> fix -> outcome.
