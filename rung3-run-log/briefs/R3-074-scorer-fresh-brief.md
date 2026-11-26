# R3-074 scorer brief, Fresh (Pair B scorer 2, R3-L3, Class L, Tier B)

You are scorer 2 for task R3-074 (Pair B), a fresh independent session.
Score independently from the snapshot and the key only. Do not read scorer
1's verdict, the ledger row for R3-074, or contact the runner.

## Inputs

- Snapshot (pushed to todolist-push before scoring):
  rung3-run-log/rung3-snapshots/R3-074-L3/. Verify manifest_sha256 and every
  per-file sha256 against manifest.json before scoring; record the manifest
  hash in your verdict.
- Key: docs/rung3-answer-keys.md, section "## R3-074 (Tier B)". Verify
  before scoring: md sha256
  21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60,
  json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8.
- Expected: the original script fails with NameError: name 'tongue' is not
  defined (line 8 uses undefined `tongue` instead of `tong`), exit 1. The
  fix renames `tongue` to `tong` at line 8 only; no variable renames, no
  main-logic change. Result file has exactly 10 lines: tong = 7, 9, 15, 11,
  14, 24, 13, 18, 15, 13 (in order). Run 2 identical to run 1. Original
  script sha256 f3b09ca0df66d3e4c4b8c88c78cffdb374d9ca6d988145587969034e4e3e7025;
  expected-file sha256 f737a14b0e450ed29e2b5842ca7a967a6c93cae20a500462dae027006a68d091.

## Grade

PASS: script runs with no error, result file has all 10 lines with correct
values, run 2 identical to run 1, main logic unchanged (only the line-8
fix). You may re-run the fixed script copy from the snapshot (read-only,
in a temp dir) and compare its output to the 10 lines. FAIL: script still
errors, result missing lines or wrong values, run 2 differs, or main logic
changed. The initial-error screenshot must be present and show the original
NameError. INVALID only if the evidence cannot be judged. Before any
INVALID verdict, record whether the infrastructure re-run path was
considered (mandatory from epoch 23).

## Deliverables (30 minutes)

- Files: ~/workspace/rung3-verdicts/R3-074-B2.json (verdict, session,
  timestamp +07, key hashes, manifest hash, reason, files_read,
  infrastructure_rerun_considered) and
  ~/workspace/rung3-verdicts/R3-074-B2-grade.md (full grade with
  independence declaration).
- If git is blocked for you, do NOT retry through other routes: write the
  two files above and report the paths to the coordinator, who lands them.
- English only. No personal info anywhere.
- LOGGING (owner rule 18:20): log every event with the full chain:
  failure -> reasoning -> attempts -> decision -> fix -> outcome.
