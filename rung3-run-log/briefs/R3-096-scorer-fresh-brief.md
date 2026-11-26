# R3-096 scorer brief, Fresh (Pair B scorer 2, R3-L3, Class L, Tier B)

You are scorer 2 for task R3-096 (Pair B), a fresh independent session.
Score independently from the snapshot and the key only. Do not read scorer
1's verdict, the ledger row for R3-096, or contact the runner.

Note: this seat pairing is Clone2 + Fresh. The F5.2 table had Mochi +
Fresh; Mochi was reassigned under the owner order of 2026-11-26 21:36
(Clone2 is the main burner, Mochi reduced). Prep for this task was
coordinator-live, so no disjointness issue.

## Inputs

- Snapshot (pushed to todolist-push before scoring):
  rung3-run-log/rung3-snapshots/R3-096-L3/. Verify manifest_sha256 and every
  per-file sha256 against manifest.json before scoring; record the manifest
  hash in your verdict.
- Key: docs/rung3-answer-keys.md, section "## R3-096 (Tier B)" plus the
  R3-096 task section in docs/rung3-list-100-tasks.md. Verify before
  scoring: md sha256
  21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60,
  json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8.
- Key facts (Tier B: the truth is the state at run time in the saved
  files): 2 files ~/rung3/nd16-cu.conf and ~/rung3/nd16-moi.conf.
  Initially exactly 4 differing lines: cong 8080 -> 9090; che_do dem ->
  ngay; ngon_ngu vi -> en; bo_nho 512 -> 1024. The requirement file
  nd16-yeu-cau.txt specifies merging cong (9090), only this 1 line, keeping
  the other 3 differing lines at their old values. After merging, diff has
  only 3 differing lines. The merged line has the new value (9090), the
  other 3 differing lines still keep the old values. The report has: the 4
  initial differing lines, the merged line, the remaining differing-line
  count (3). Grading evidence: the report + the old file after merging (a
  copy is in the snapshot). Re-run diff read-only yourself against the
  snapshot copies and compare.

## Grade

PASS: initially exactly 4 differing lines, after merging only 3 differing
lines remain, the merged line has the correct new value, the other 3
differing lines unchanged, report correct.
FAIL: wrong differing-line count, wrong line merged, more than 1 line
merged, report wrong line count.
INVALID only if the evidence cannot be judged. Before any INVALID verdict,
record whether the infrastructure re-run path was considered (mandatory
from epoch 23).

## Deliverables (30 minutes)

- Files: ~/workspace/rung3-verdicts/R3-096-B2.json (verdict, session,
  timestamp +07, key hashes, manifest hash, reason, files_read,
  infrastructure_rerun_considered, both diff counts + merged line) and
  ~/workspace/rung3-verdicts/R3-096-B2-grade.md (full grade with
  independence declaration).
- If git is blocked for you, do NOT retry through other routes: write the
  two files above and report the paths to the coordinator, who lands them.
- English only. No personal info anywhere.
- LOGGING (owner rule 18:20): log every event with the full chain:
  failure -> reasoning -> attempts -> decision -> fix -> outcome.
