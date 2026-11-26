# R3-067 scorer brief, Fresh (Pair B scorer 2, R3-L3, Class S)

You are scorer 2 for task R3-067 (Pair B), a fresh independent session.
Score independently from the snapshot and the key only. Do not read scorer
1's verdict, the ledger row for R3-067, or contact the runner.

## Inputs

- Snapshot (pushed to todolist-push before scoring):
  rung3-run-log/rung3-snapshots/R3-067-L3/. Verify manifest_sha256 and every
  per-file sha256 against manifest.json before scoring; record the manifest
  hash in your verdict.
- Key: docs/rung3-answer-keys.md, section "### R3-067 (ve 3 hinh trong
  Pinta, 800x600, nen trang)". Verify before scoring: md sha256
  21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60,
  json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8.
- Expected: file ~/rung3/nd23-hinh-ve.png, size 800x600, white background,
  exactly 3 filled shapes: (1) red filled rectangle, region x 50-350,
  y 50-250; (2) blue filled circle, region x 300-500, y 200-400 (Shift held
  while dragging); (3) green filled triangle, bottom-right region
  x 550-750, y 350-550 (Freeform Shape, dragged closed path). All 3 shapes
  must be solid-filled (Fill Shape); outline-only shapes are wrong. No text
  required.

## Grade

PASS / FAIL / INVALID per the frozen rubric. A shape is wrong if: missing;
wrong type (e.g. circle instead of rectangle); center outside its region;
wrong color; not filled (outline only). Wrong size or non-white background
is FAIL. Grade from the snapshot evidence (saved PNG copy, screenshots,
bao-cao.txt). Open the PNG copy and check each shape against the rubric; do
not grade on aesthetics. INVALID only if the evidence cannot be judged.
Before any INVALID verdict, record whether the infrastructure re-run path
was considered (mandatory from epoch 23).

Tracking note (frozen list section 1): R3-067 and R3-083 are the paired
Pinta drawing tasks. Record in your grade report which drawing method the
evidence shows for R3-067 (tools, Fill Style, drag technique), so the pair
comparison can be made when R3-083 is scored.

## Deliverables (30 minutes)

- Files: ~/workspace/rung3-verdicts/R3-067-B2.json (verdict, session,
  timestamp +07, key hashes, manifest hash, reason, files_read,
  infrastructure_rerun_considered) and
  ~/workspace/rung3-verdicts/R3-067-B2-grade.md (full grade with
  independence declaration).
- If git is blocked for you, do NOT retry through other routes: write the
  two files above and report the paths to the coordinator, who lands them.
- English only. No personal info anywhere.
- LOGGING (owner rule 18:20): log every event with the full chain:
  failure -> reasoning -> attempts -> decision -> fix -> outcome.
