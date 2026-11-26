# R3-082 scorer brief, Fresh 1 (Pair B scorer 1, R3-L3, Class S, Tier A)

You are scorer 1 for task R3-082 (Pair B), a fresh independent session.
Score independently from the snapshot and the key only. Do not read scorer
2's verdict, the ledger row for R3-082, or contact the runner.

Note: this seat pairing is Fresh + Fresh. The F5.2 table had Clone1 +
Fresh; Clone1 was reassigned under the owner order of 2026-11-26 21:36
(Clone1 reduced), and Clone2 cannot score this task because he prepped it
(disjointness). Two independent fresh sessions score instead (R3-046
precedent).

## Inputs

- Snapshot (pushed to todolist-push before scoring):
  rung3-run-log/rung3-snapshots/R3-082-L3/. Verify manifest_sha256 and every
  per-file sha256 against manifest.json before scoring; record the manifest
  hash in your verdict.
- Key: docs/rung3-answer-keys.md, section "## R3-082 (Tier A)". Verify
  before scoring: md sha256
  21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60,
  json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8.
- Expected per key (computed with omacalc, step by step, operator
  precedence handled by the runner):
  (14 + 6) * 4 - 9 = 71
  120 / 5 + 18 * 3 = 78
  (60 - 24) * 3 + 12 = 120
  300 / 6 * 2 - 11 = 89
  (11 + 9) * 5 / 4 = 25
  Rounding tolerance 0.01. The result file ket-qua.txt has a 6-row table
  (title + 5 calculation rows) and 1 hand-check note line in the form
  "Kiem tra lai: <expression> = <result>" with the correct result.
  Grading evidence: ket-qua.txt + 5 calculator screenshots. The
  coordinator runs tier-a-check.py (type calculations) on the snapshot
  and hands the output identically to both scorers. If the checker output
  and your own reading disagree, say so in your grade (do not silently
  override).

## Grade

PASS: ket-qua.txt has all 5 calculation rows with correct results
(tolerance 0.01), the hand-check note line present in the required form
with the correct result, no expression missing, 5 screenshots present and
readable showing the correct expressions + results.
FAIL: missing expression, wrong result beyond tolerance, expression with
fewer than 3 operands, missing hand-check note or wrong hand-check
result, file not saved, screenshot missing/unreadable.
INVALID only if the evidence cannot be judged. Before any INVALID verdict,
record whether the infrastructure re-run path was considered (mandatory
from epoch 23).

## Deliverables (30 minutes)

- Files: ~/workspace/rung3-verdicts/R3-082-B1.json (verdict, session,
  timestamp +07, key hashes, manifest hash, reason, files_read,
  infrastructure_rerun_considered) and
  ~/workspace/rung3-verdicts/R3-082-B1-grade.md (full grade with
  independence declaration).
- If git is blocked for you, do NOT retry through other routes: write the
  two files above and report the paths to the coordinator, who lands them.
- English only. No personal info anywhere.
- LOGGING (owner rule 18:20): log every event with the full chain:
  failure -> reasoning -> attempts -> decision -> fix -> outcome.
