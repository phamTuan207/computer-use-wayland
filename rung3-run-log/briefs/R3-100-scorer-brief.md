# R3-100 scorer briefs (position 52, Class S, Tier B)

Prepared by coordinator (epoch 24), 2026-11-27. Scorers per F5.2: Mochi + Fresh (scorer 1 = Mochi, scorer 2 = Fresh per table "Mochi plus Fresh"). Prep reassignment per owner order 2026-11-26 21:36: prep Clone1 -> coordinator-live (Clone1 reduced to minimum; precedent R3-089, R3-096, R3-098, R3-099). The runner brief (rung3-run-log/briefs/R3-100-runner-brief.md, epoch 12 pre-staged with F12 guard verbatim) is unchanged. Disjointness re-checked: prep = coordinator-live (runner brief epoch 12), scorers = Mochi + Fresh, no overlap. Mochi's seat kept (Clone2 is analyst on-call for R3-100 per F5.2, so he cannot score it; Mochi's remaining load is this one task).

## Independence

- Score independently from the snapshot + answer key only. Do NOT read the other scorer's verdict, the ledger row for R3-100, or the drive report. Do NOT contact the runner.
- Graded from saved files ONLY: the scorer never re-checks the live port (F12 guard). The port-closed check is graded from the saved ss output / curl results in the snapshot.

## Inputs

- Snapshot: rung3-run-log/rung3-snapshots/R3-100-L3/ (coordinator seals it; manifest sha256 will be given at assignment). Verify manifest file sha256 + per-file hashes before scoring.
- Answer key: docs/rung3-answer-keys.md + docs/rung3-answer-keys.json, R3-100 section only. Key hashes: md 21f8b61a...bc60, json 5059f6c4...dae8 (verify; mismatch = STOP and report).
- Task: serve ~/rung3/nd20-web (3 HTML files) with python3 -m http.server 8899; all 3 pages return 200 via curl; titles: trang-chu.html "Trang chu", gioi-thieu.html "Gioi thieu", lien-he.html "Lien he"; each file links to the other 2. HTML sha256: trang-chu 2745056563d23d1cd02261ba134937a40ed188b60a355b81929abbb072da2eba; gioi-thieu e760910beb467319d939d528021ab04167882609dfed724ed88b407791b414b5; lien-he 339c81e9e5be6638e66f7d1078828843969bad168486dbcd42b27d12ad3be1fd. After completion, port 8899 closed (curl cannot connect). Graded evidence: report with port, 3 status codes, 3 titles; cross-check titles against the saved HTML files in the snapshot.

## Before any INVALID grade

- Record whether an infrastructure re-run was considered (infrastructure_rerun_considered + note).

## Deliverables

- Mochi (scorer 1): commit R3-100-L3-mochi.json + R3-100-L3-mochi-grade.md to branch mochi/verdict-R3-100-L3 under rung3-run-log/verdicts/R3-100-L3/ (explicit pathspec, add+commit atomically, push, verify ls-remote). Coordinator copies to ~/workspace/rung3-verdicts/R3-100-B1.json + R3-100-B1-grade.md. Verdicts via branch only, never chat.
- Fresh (scorer 2): ~/workspace/rung3-verdicts/R3-100-B2.json + R3-100-B2-grade.md. No git action; coordinator lands the files.
- Verdict JSON fields: verdict (PASS/FAIL/INVALID), task_id, session, timestamp (Asia/Ho_Chi_Minh), manifest_sha256, keyfile_sha256 (json key file), files_read, per-criterion results, infrastructure_rerun_considered + note.
- Include the full event log chain (failure -> reasoning -> attempts -> decision -> fix -> outcome) per the 18:20 super-detailed logging rule.
- English only, no personal info, no em/en dashes.
- Ponytail for any code: smallest complete change, reuse before writing, stdlib/platform before dependencies, no unrequested abstraction, one small test for non-trivial logic, never cut validation/security/error handling. Graphify for codebase context if needed (~/workspace/cu-graphify/graphify-out/).
