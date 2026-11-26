# R3-016 calibration grade (blind, sealed)

- Session: cfdde5e8-29c0-499d-a27c-0ac8760231c2
- Task: R3-016 (Tier B)
- Verdict: PASS

## Key hashes (verified via GitHub API, branch todolist-push, tip 31fa2244)

- docs/rung3-answer-keys.md: `21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60` (expected value, match)
- docs/rung3-answer-keys.json: `5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8` (expected value, match)
- JSON R3-016 entry: `.tiers["R3-016"]` = `"B"` (tier label only; grading criteria taken from the .md key section, lines 246-254)

## Manifest hash

- manifest_sha256 field: `dd4992764d5923e5baf24b408471bcfd41e13cbc987a663b5350c6d82a0bdf2d` (expected value, match)
- manifest.json sha256: `dc4c5b41edd680d8e0ad2f52da2494545c1a707f2a04b7dfbe487a73752c8ebf`

## Per-file hash verification (against manifest per-file entries)

- 20261126-005725-mockaroo-preview.png: `556d6c0c5e525e2f470da4d90ea112b17934057dd5c27dd2fed790cd7c7f3032` — MATCH
- du-lieu.csv: `267c3bd3e22c703d77aa3cfbfde4c9b7cd3f096212ae9b4733748b526be41977` — MATCH
- end_time.txt: `9efc556788124dabd57ea9b103ac89ef4b8eee87a45c27ea7cf35ad7adf35942` — MATCH
- ket-qua.txt: `377e8b7750ea50c5c2c16e1b5d0db0cc2d5e9c092860ea78364b2f4a98527f2b` — MATCH
- start_time.txt: `d072e834fc3795d3782540ab4082eae7c3137457b0553fe50bd6a9a97219e757` — MATCH

All 5 snapshot files match their manifest entries. Directory listing via API showed exactly 6 files (the 5 above plus manifest.json): no file missing, no extra file.

## Files read (allowlist only)

- rung3-run-log/rung3-snapshots/R3-016-L3/manifest.json
- rung3-run-log/rung3-snapshots/R3-016-L3/du-lieu.csv
- rung3-run-log/rung3-snapshots/R3-016-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-016-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-016-L3/end_time.txt
- rung3-run-log/rung3-snapshots/R3-016-L3/20261126-005725-mockaroo-preview.png
- docs/rung3-answer-keys.md (lines 246-254 only)
- docs/rung3-answer-keys.json (R3-016 entry only)

## Independence declaration

I graded blind from the snapshot and key section only; I did not read the ledger, any grade file, or any other verdict for these tasks

## Checker

The Tier-A checker script (rung3-ci/tier-a-check.py) was not run; grading was done manually from the key criteria.

## Verdict: PASS

Reasons, tied to specific files:

1. Schema (ket-qua.txt, DOM read-back): fields First Name (First Name), Last Name (Last Name), Email Address (Email Address), Age (Number, min 18, max 90); format csv; rows 10; names and types match the key section exactly.
2. Row count (du-lieu.csv, counted by hand): header plus 10 data rows.
3. Columns (du-lieu.csv): header `First Name,Last Name,Email Address,Age` matches the 4 key fields.
4. Completeness (du-lieu.csv, counted by hand): every one of the 10 rows has 4 values.
5. Emails (du-lieu.csv, checked by hand): all 10 contain `@`.
6. Ages (du-lieu.csv, checked by hand): 81, 41, 30, 43, 85, 42, 71, 85, 73, 28 — all integers within 18-90.
7. Preview screenshot (20261126-005725-mockaroo-preview.png): the Mockaroo Preview TABLE shows the same 4 columns and 10 rows, all with `@` emails and ages 28-86; `# Rows: 10` is shown. No login screen appears, so the section-1 INVALID condition (page requires login to download) does not trigger.
8. Run window (start_time.txt `2026-11-26T00:38:32.955712+07:00`, end_time.txt `2026-11-26T01:01:15.520649+07:00`) is recorded; no criterion in the key section constrains duration.

No FAIL or INVALID criterion in the key section is met.
