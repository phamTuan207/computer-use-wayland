# R3-094 scorer brief, Clone2 (Pair B scorer 1, R3-L3, Class S, Tier B)

You are scorer 1 for task R3-094 (Pair B). Score independently from the
snapshot and the key only. Do not read scorer 2's verdict, the ledger row
for R3-094, or contact the runner.

Note: this seat pairing is Clone2 + Fresh. The F5.2 table had Clone1 +
Fresh; Clone1 was reassigned under the owner order of 2026-11-26 21:36
(Clone2 is the main burner, Clone1 reduced). Mochi prepped this task and
cannot score it (disjointness).

## Inputs

- Snapshot (pushed to todolist-push before scoring):
  rung3-run-log/rung3-snapshots/R3-094-L3/. Verify manifest_sha256 and every
  per-file sha256 against manifest.json before scoring; record the manifest
  hash in your verdict.
- Key: docs/rung3-answer-keys.md, section "## R3-094 (Tier B)" plus the
  R3-094 task section in docs/rung3-list-100-tasks.md. Verify before
  scoring: md sha256
  21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60,
  json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8.
- Key facts (Tier B: the truth is the state at run time in the saved
  files): script ~/rung3/nd14-in-bien.sh prints 3 variables R3_TEN,
  R3_TUOI, R3_THANH_PHO, one line per variable in the form "TEN=<value>".
  Values from the requirement file nd14-gia-tri.txt: R3_TEN=An, R3_TUOI=25,
  R3_THANH_PHO=Ha Noi. Run 1: TEN=An, TUOI=25, THANH_PHO=Ha Noi. Run 2:
  change 1 variable's value, only that variable's line changes. Run 3:
  restore the old value, result same as run 1. The 3 result files have
  timestamps in ~/rung3-chung-cu/R3-094/: lan-1-YYYYMMDD-HHMMSS.txt,
  lan-2-YYYYMMDD-HHMMSS.txt, lan-3-YYYYMMDD-HHMMSS.txt. Grading evidence:
  the 3 result files + the report. Compare the 3 runs yourself.

## Grade

PASS: run 1 has all 3 lines with the correct set values, run 2 only 1 line
changes, run 3 same as run 1, report correct, report matches the 3 saved
result files.
FAIL: missing output line, wrong variable value, run 2 changes more than 1
line, run 3 differs from run 1, report wrong.
INVALID only if the evidence cannot be judged. Before any INVALID verdict,
record whether the infrastructure re-run path was considered (mandatory
from epoch 23).

## Deliverables (30 minutes)

- Verdict JSON + grade markdown, filed on branch clone2/verdict-R3-094-L3
  under rung3-run-log/verdicts/R3-094-L3/ (verdict, session, timestamp +07,
  key hashes, manifest hash, reason, files_read,
  infrastructure_rerun_considered, the 3 runs' lines). The coordinator
  copies them locally and audits.
- English only. No personal info anywhere.
- LOGGING (owner rule 18:20): log every event with the full chain:
  failure -> reasoning -> attempts -> decision -> fix -> outcome.
