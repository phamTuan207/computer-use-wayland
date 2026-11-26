# R3-099 scorer briefs (position 51, Class S, Tier B)

Prepared by coordinator (epoch 24), 2026-11-27. Scorers per F5.2: Clone2 + Fresh (scorer 1 = Clone2, scorer 2 = Fresh per table "Clone2 plus Fresh"). Prep reassignment per owner order 2026-11-26 21:36: prep Clone1 -> coordinator-live (Clone1 reduced to minimum; precedent R3-089, R3-096, R3-098). Disjointness re-checked: prep = coordinator-live, scorers = Clone2 + Fresh, no overlap.

## Independence

- Score independently from the snapshot + answer key only. Do NOT read the other scorer's verdict, the ledger row for R3-099, or the drive report. Do NOT contact the runner.

## Inputs

- Snapshot: rung3-run-log/rung3-snapshots/R3-099-L3/ (coordinator seals it; manifest sha256 will be given at assignment). Verify manifest file sha256 + per-file hashes before scoring.
- Answer key: docs/rung3-answer-keys.md + docs/rung3-answer-keys.json, R3-099 section only. Key hashes: md 21f8b61a...bc60, json 5059f6c4...dae8 (verify; mismatch = STOP and report).
- Task: Python script nd19-xu-ly.py computing per-group averages from ~/rung3/nd19-du-lieu.csv (sha256 fc7abae0e1b68312eac292518076bea9a9a03984d42d83279403728c2e20bea6). Expected: NhomA 14 rows average 7.91; NhomB 12/7.09; NhomC 13/7.86; NhomD 11/7.12. Tolerance 0.01. Run 2 report identical to run 1. Graded evidence: script nd19-xu-ly.py + report nd19-bao-cao.txt. Re-run the script read-only (on a copy if needed) and compare; verify the script computes from the CSV (no hard-coded averages).

## Before any INVALID grade

- Record whether an infrastructure re-run was considered (infrastructure_rerun_considered + note).

## Deliverables

- Clone2 (scorer 1): commit R3-099-L3-clone2.json + R3-099-L3-clone2-grade.md to branch clone2/verdict-R3-099-L3 under rung3-run-log/verdicts/R3-099-L3/ (explicit pathspec, add+commit atomically, push, verify ls-remote). Coordinator copies to ~/workspace/rung3-verdicts/R3-099-B1.json + R3-099-B1-grade.md.
- Fresh (scorer 2): ~/workspace/rung3-verdicts/R3-099-B2.json + R3-099-B2-grade.md. No git action; coordinator lands the files.
- Verdict JSON fields: verdict (PASS/FAIL/INVALID), task_id, session, timestamp (Asia/Ho_Chi_Minh), manifest_sha256, keyfile_sha256 (json key file), files_read, per-criterion results, infrastructure_rerun_considered + note.
- Include the full event log chain (failure -> reasoning -> attempts -> decision -> fix -> outcome) per the 18:20 super-detailed logging rule.
- English only, no personal info, no em/en dashes.
- Ponytail for any code: smallest complete change, reuse before writing, stdlib/platform before dependencies, no unrequested abstraction, one small test for non-trivial logic, never cut validation/security/error handling. Graphify for codebase context if needed (~/workspace/cu-graphify/graphify-out/).
