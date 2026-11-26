# R3-093 scorer brief, Fresh 1 (Pair B scorer 1, R3-L3, Class S, Tier B)

You are scorer 1 for task R3-093 (Pair B), a fresh independent session.
Score independently from the snapshot and the key only. Do not read scorer
2's verdict, the ledger row for R3-093, or contact the runner.

Note: this seat pairing is Fresh + Fresh. The F5.2 table had Fresh +
Clone1; Clone1 was reassigned under the owner order of 2026-11-26 21:36
(Clone1 reduced), and Clone2 cannot score this task because he prepped it
(disjointness). Two independent fresh sessions score instead (R3-046
precedent).

## Inputs

- Snapshot (pushed to todolist-push before scoring):
  rung3-run-log/rung3-snapshots/R3-093-L3/. Verify manifest_sha256 and every
  per-file sha256 against manifest.json before scoring; record the manifest
  hash in your verdict.
- Key: docs/rung3-answer-keys.md, section "## R3-093 (Tier B)" plus the
  R3-093 task section in docs/rung3-list-100-tasks.md. Verify before
  scoring: md sha256
  21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60,
  json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8.
- Key facts (Tier B: the truth is the state at run time in the saved
  files): source file ~/rung3/nd13-file-lon.bin, 3000000 bytes (from
  /dev/urandom). Split into 3 parts with `split -n 3 -d
  --numeric-suffixes=1 -a 2`, named phan-01, phan-02, phan-03 (each part
  1000000 bytes). Exactly 3 parts; total size of the 3 parts = source file
  size (3000000 bytes). Rejoined into ~/rung3/nd13-ghep-lai.bin with `cat`.
  The new file checksum matches the source checksum (the checksum is the
  live value of the file, recorded in the report; recompute the checksums
  of both files yourself: the source checksum from the report vs the
  rejoined file in the snapshot, and cat the 3 parts and compare with the
  rejoined file). Report with: source file size, each part size, source
  checksum, new checksum. Grading evidence: the report nd13-bao-cao.txt +
  the 3 part files + the rejoined file (all in the snapshot).

## Grade

PASS: exactly 3 parts, total size of the 3 parts = source file, new file
checksum matches the source, report correct numbers.
FAIL: missing part, wrong total size, different checksums, report wrong
numbers.
INVALID only if the evidence cannot be judged. Before any INVALID verdict,
record whether the infrastructure re-run path was considered (mandatory
from epoch 23).

## Deliverables (30 minutes)

- Files: ~/workspace/rung3-verdicts/R3-093-B1.json (verdict, session,
  timestamp +07, key hashes, manifest hash, reason, files_read,
  infrastructure_rerun_considered, measured sizes + checksums) and
  ~/workspace/rung3-verdicts/R3-093-B1-grade.md (full grade with
  independence declaration).
- If git is blocked for you, do NOT retry through other routes: write the
  two files above and report the paths to the coordinator, who lands them.
- English only. No personal info anywhere.
- LOGGING (owner rule 18:20): log every event with the full chain:
  failure -> reasoning -> attempts -> decision -> fix -> outcome.
