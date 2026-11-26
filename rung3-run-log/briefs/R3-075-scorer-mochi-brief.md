# R3-075 scorer brief, Mochi (Pair B scorer 1, R3-L3, Class L, Tier B)

You are scorer 1 for task R3-075 (Pair B). Score independently from the
snapshot and the key only. Do not read scorer 2's verdict, the ledger row
for R3-075, or contact the runner.

## Inputs

- Snapshot (pushed to todolist-push before scoring):
  rung3-run-log/rung3-snapshots/R3-075-L3/. Verify manifest_sha256 and every
  per-file sha256 against manifest.json before scoring; record the manifest
  hash in your verdict.
- Key: docs/rung3-answer-keys.md, section "## R3-075 (Tier B)". Verify
  before scoring: md sha256
  21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60,
  json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8.
- Expected per key: requirements.txt contains only requests==2.32.3
  (sha256 4b8183101fd19f071771805a42a31fbb234a7961921fdb8b783a279755a1b5d5);
  d41-app.py imports requests, prints "Xin chao rung 3" then the requests
  version (sha256 9f368adac0c3e4b2112679198a4f4df8ea9492f5b0db27ba5a08b28e4a85cc3b);
  expected greeting line "Xin chao rung 3", app runs in the venv and
  prints the greeting, exit 0; laptop Python 3.14.10; venv at
  ~/rung3/d41-venv; after deactivate the venv dir remains intact. Grading
  evidence: 3 terminal screenshots (Python version, venv python path, app
  output). The scorer checks the venv exists and the package is installed
  (from the snapshot evidence). Error path: if venv creation or pip
  install failed after 1 retry, the task is INVALID (error written into
  ket-qua.txt).

## Grade

PASS: venv created at ~/rung3/d41-venv, venv python path correct,
requests installed in the venv, app runs and prints "Xin chao rung 3",
venv intact after deactivate, 3 required screenshots present and readable.
FAIL: no venv, python path wrong, package missing, app errors or prints
wrong output, venv deleted, required screenshot missing/unreadable.
INVALID only if the evidence cannot be judged, or on the documented
venv/pip error path (1 retry exhausted, error in ket-qua.txt). Before any
INVALID verdict, record whether the infrastructure re-run path was
considered (mandatory from epoch 23).

## Deliverables (30 minutes)

- Branch: mochi/verdict-R3-075-L3 with two files under
  rung3-run-log/verdicts/R3-075-L3/: R3-075-L3-mochi.json (verdict,
  session, timestamp +07, key hashes, manifest hash, reason, files_read,
  infrastructure_rerun_considered) and R3-075-L3-mochi-grade.md (full
  grade with independence declaration). Push the branch; the coordinator
  verifies delivery by the branch landing. Verdicts via branch only,
  never via chat.
- English only. No personal info anywhere.
- LOGGING (owner rule 18:20): log every event with the full chain:
  failure -> reasoning -> attempts -> decision -> fix -> outcome.
