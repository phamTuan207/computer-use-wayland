# R3-098 scorer briefs (position 50, Class S, Tier B)

Prepared by coordinator (epoch 24), 2026-11-27. Scorers per F5.2: Fresh + Clone2 (scorer 1 = Fresh, scorer 2 = Clone2 per table "Fresh plus Clone2"). Prep reassignment per owner order 2026-11-26 21:36: prep Clone1 -> coordinator-live (Clone1 reduced to minimum; precedent R3-089, R3-096). Disjointness re-checked: prep = coordinator-live, scorers = Fresh + Clone2, no overlap.

## Independence

- Score independently from the snapshot + answer key only. Do NOT read the other scorer's verdict, the ledger row for R3-098, or the drive report. Do NOT contact the runner.

## Inputs

- Snapshot: rung3-run-log/rung3-snapshots/R3-098-L3/ (coordinator seals it; manifest sha256 will be given at assignment). Verify manifest file sha256 + per-file hashes before scoring.
- Answer key: docs/rung3-answer-keys.md + docs/rung3-answer-keys.json, R3-098 section only. Key hashes: md 21f8b61a...bc60, json 5059f6c4...dae8 (verify; mismatch = STOP and report).
- Task: awk per-group sums on ~/rung3/nd18-du-lieu.csv (sha256 71dd42639dadbd62d458d2304e30f05e7ed227f8b55387f830eadd4262648eea). Expected: NhomA 14 rows sum 66193; NhomB 12/52674; NhomC 13/69300; NhomD 11/51018; grand total 239185. Graded evidence: bao-cao.txt. Re-run the awk read-only on the CSV (or on a copy) and compare line by line.

## Before any INVALID grade

- Record whether an infrastructure re-run was considered (infrastructure_rerun_considered + note).

## Deliverables

- Fresh (scorer 1): ~/workspace/rung3-verdicts/R3-098-B1.json + R3-098-B1-grade.md. No git action; coordinator lands the files.
- Clone2 (scorer 2): commit R3-098-L3-clone2.json + R3-098-L3-clone2-grade.md to branch clone2/verdict-R3-098-L3 under rung3-run-log/verdicts/R3-098-L3/ (explicit pathspec, add+commit atomically, push, verify ls-remote). Coordinator copies to ~/workspace/rung3-verdicts/R3-098-B2.json + R3-098-B2-grade.md.
- Verdict JSON fields: verdict (PASS/FAIL/INVALID), task_id, session, timestamp (Asia/Ho_Chi_Minh), manifest_sha256, keyfile_sha256 (json key file), files_read, per-criterion results, infrastructure_rerun_considered + note.
- Include the full event log chain (failure -> reasoning -> attempts -> decision -> fix -> outcome) per the 18:20 super-detailed logging rule.
- English only, no personal info, no em/en dashes.
- Ponytail for any code: smallest complete change, reuse before writing, stdlib/platform before dependencies, no unrequested abstraction, one small test for non-trivial logic, never cut validation/security/error handling. Graphify for codebase context if needed (~/workspace/cu-graphify/graphify-out/).
