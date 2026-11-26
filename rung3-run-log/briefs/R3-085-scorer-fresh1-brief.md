# R3-085 scorer brief, Fresh 1 (Pair B scorer 1, R3-L3, Class S, Tier C)

You are scorer 1 for task R3-085 (Pair B), a fresh independent session.
Score independently from the snapshot and the key only. Do not read scorer
2's verdict, the ledger row for R3-085, or contact the runner.

Note: this seat pairing is Fresh + Fresh. The F5.2 table had Mochi +
Fresh; Mochi was reassigned under the owner order of 2026-11-26 21:36
(Mochi reduced), and Clone2 cannot score this task because he prepped it
(disjointness). Two independent fresh sessions score instead (R3-046
precedent).

## Inputs

- Snapshot (pushed to todolist-push before scoring):
  rung3-run-log/rung3-snapshots/R3-085-L3/. Verify manifest_sha256 and every
  per-file sha256 against manifest.json before scoring; record the manifest
  hash in your verdict.
- Key: docs/rung3-answer-keys.md, Tier C rubric section "### R3-085 (mpv
  dung o 00:10, chup anh, doi chieu khung tham chieu)" plus the R3-085 task
  section. Verify before scoring: md sha256
  21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60,
  json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8.
- Rubric (both scorers use the same rubric; grade by measurement, not
  taste): the screenshot MUST show the mpv window paused at 00:10 (timeline
  shows 00:10, video paused). Compare the screenshot with the reference
  frame r3-085-khung-tham-chieu.png (sha256
  de410f94b2192e553f4a78ff42df8bcfd84e29e5908c3f02775125cfa4c759c2; a copy is
  in the snapshot) side by side. Mandatory criteria: the screenshot matches
  the reference frame in scene and objects; the result file records exactly
  2 identifiable details (object, color, text, layout) that are real in
  both images. Color guide (not a mandatory criterion): mean color of the
  center region (x 25-75 percent, y 25-75 percent) of the screenshot vs the
  reference frame, deviation under 10 percent accepted; reference mean
  color RGB (118.2, 139.7, 121.3). No per-pixel match required. Record the
  2 details you verified and the match conclusion in your grade.

## Grade

PASS: mpv paused at 00:10, screenshot matches the reference frame by the 2
details, result file complete.
FAIL: video not paused at 00:10, screenshot does not show the mpv window,
screenshot does not match the reference frame, missing identifiable
details.
INVALID only if the evidence cannot be judged. Before any INVALID verdict,
record whether the infrastructure re-run path was considered (mandatory
from epoch 23).

## Deliverables (30 minutes)

- Files: ~/workspace/rung3-verdicts/R3-085-B1.json (verdict, session,
  timestamp +07, key hashes, manifest hash, reason, files_read,
  infrastructure_rerun_considered, the 2 details verified, mean-color
  values if measured) and ~/workspace/rung3-verdicts/R3-085-B1-grade.md
  (full grade with independence declaration).
- If git is blocked for you, do NOT retry through other routes: write the
  two files above and report the paths to the coordinator, who lands them.
- English only. No personal info anywhere.
- LOGGING (owner rule 18:20): log every event with the full chain:
  failure -> reasoning -> attempts -> decision -> fix -> outcome.
