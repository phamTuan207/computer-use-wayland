# R3-099 scorer 1 grade (Pair B, R3-L3, Class S, Tier B)

scorer session ID: clone2-main-ad85548c-ced4-4f31-afdb-d1043dcabbd7
task ID: R3-099
verdict: PASS
timestamp: 2026-11-27 03:05 +07 (Asia/Ho_Chi_Minh)
key file hash: docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8; docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both verified against the brief's frozen hashes before scoring)
reason: the report matches the key exactly on all 4 groups (NhomA 14 rows average 7.91, NhomB 12/7.09, NhomC 13/7.86, NhomD 11/7.12, tolerance 0.01); the run 2 report is byte-identical to run 1; and the sealed script genuinely computes the averages from the CSV (no hard-coded values, proven by code reading, a literal grep, and my behavioral re-run of a path-redirected copy on synthetic data with known averages).

## Key section used

docs/rung3-answer-keys.md, "## R3-099 (Tier B)", lines 605-611: file ~/rung3/nd19-du-lieu.csv, 50 data rows plus a header row, columns ten,nhom,diem, sha256 fc7abae0e1b68312eac292518076bea9a9a03984d42d83279403728c2e20bea6. Per-group averages rounded to 2 decimals: NhomA 14 rows average 7.91; NhomB 12 rows average 7.09; NhomC 13 rows average 7.86; NhomD 11 rows average 7.12. Tolerance 0.01. Run 2 must produce a report identical to run 1. Grading evidence per the key: the script nd19-xu-ly.py plus the report nd19-bao-cao.txt; the scorer re-runs the script (read-only, on a copy if needed) and compares. The task steps in docs/rung3-list-100-tasks.md (line 689) match this contract.

## Snapshot verification

- Snapshot: rung3-run-log/rung3-snapshots/R3-099-L3/
- Manifest: the manifest.json file's own sha256 is c59593bdaab883a8488aa4f2b88698676af39b261122a011d5a7d579461705af, matching the dispatch notice. The manifest_sha256 field inside the file reads 544d90241ac81791fe01cbba4e1710b7a71da62883e43d04246017052d4d3444 (a hash of the file list). Per-file verification below was recomputed against this sealed manifest.json, so the verification chain is intact; both hashes are recorded here to keep the record unambiguous.
- Per-file sha256 verification against manifest.json (recomputed, hash and size): all 9 evidence files OK
  - bao-cao.txt ce85f5b72678ab6c3a62a6948e2c8786d3dd40722c27ccf60bc442e864146742 OK (byte-identical to both report files, same sha256)
  - drive-log.txt 52feaaf7284896d0b6c5d473331b25f0c3e23b5d8c88039438e9d1bfa792a12a OK
  - end_time.txt d484e0fa3044c2e2b20e09e7a128b5d09cfc2479e27ea8ccb080b524e11c614e OK
  - nd19-bao-cao-run2.txt ce85f5b72678ab6c3a62a6948e2c8786d3dd40722c27ccf60bc442e864146742 OK
  - nd19-bao-cao.txt ce85f5b72678ab6c3a62a6948e2c8786d3dd40722c27ccf60bc442e864146742 OK
  - nd19-xu-ly.py 9c211bd6330997119882a45b73b0e7da2bfad833306ff9337272d5ec1309f576 OK
  - pill-off.png 08c74c42ec46c8431dfe12c4f117b72aaa7510a3d6673e8c0761ecef5089ddd4 OK
  - pill-on.png 48f8b47e3c84d9443f1effe4d1ff07257b1fad5f00ff80fb1121c31f3ea3555f OK
  - start_time.txt 8996eb547e882a60805b4cbc020998c3123b592b003f927276de3e8901087905 OK
- No files in the snapshot dir beyond the manifest list plus manifest.json itself.
- Run window: start_time.txt 2026-11-27T02:59:29+07:00, end_time.txt 2026-11-27T03:01:27+07:00 (1m 58s), inside the 30 minute task limit.

## Files read

- rung3-run-log/briefs/R3-099-scorer-brief.md
- docs/rung3-answer-keys.md (sha256 verification; key section lines 605-611 only)
- docs/rung3-answer-keys.json (sha256 verification only)
- docs/rung3-list-100-tasks.md (R3-099 task steps, line 689)
- rung3-run-log/rung3-snapshots/R3-099-L3/manifest.json
- rung3-run-log/rung3-snapshots/R3-099-L3/nd19-xu-ly.py (the graded script)
- rung3-run-log/rung3-snapshots/R3-099-L3/nd19-bao-cao.txt (the graded run 1 report)
- rung3-run-log/rung3-snapshots/R3-099-L3/nd19-bao-cao-run2.txt (hash-compared to run 1; byte-identical, same sha256)
- rung3-run-log/rung3-snapshots/R3-099-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-099-L3/end_time.txt

Per the brief's independence rule I did not read drive-log.txt (the drive report), scorer 2's verdict, or the ledger row. drive-log.txt, bao-cao.txt (byte-identical to the report files by hash) and the 2 pill screenshots were hash-verified against the manifest only.

## Independence declaration

I graded independently from the snapshot and key section only; I did not read scorer 2's verdict, the ledger row, or the drive report, and I did not contact the runner.

## Infrastructure re-run consideration

Considered, and recorded here as required from epoch 23: the verdict is not INVALID, so no infrastructure re-run path applies. The graded evidence (the script and both reports) was present, sealed and fully judgeable against the key, and no infrastructure failure appears in the evidence I graded.

## Script verification: computes from the CSV, no hard-coded averages

- Code reading: the sealed script opens the CSV with csv.DictReader, validates that the nhom and diem columns exist (raising ValueError otherwise), accumulates per-group totals and counts from float(row["diem"]), and writes each group sorted with count and round(total/count, 2) formatted to 2 decimals. The averages are derived entirely from the file contents.
- Literal check: a grep of the script for the 4 expected averages (7.91, 7.09, 7.86, 7.12) found none of them anywhere in the code.
- Behavioral re-run: no copy of nd19-du-lieu.csv was sealed into the snapshot or found on this machine, so the script could not be re-run against the real data (recorded openly). Instead, as the brief allows a copy, I ran a copy of the sealed script with only its 2 absolute paths redirected to /tmp, against a synthetic CSV with hand-computed expectations (NhomA 7.90, 7.92, 7.91 giving average 7.91 over 3 rows; NhomB 3 rows of 9.00; NhomC 1 row of 5.50). The copy exited 0 and printed exactly NhomA, 3, 7.91 / NhomB, 3, 9.00 / NhomC, 1, 5.50, in the sealed report's format, and a second run was identical. A script with hard-coded fixture averages would have printed the fixture values instead of the synthetic ones, so the computation is genuine.

## Per-criterion results

- Per-group averages: PASS. Report: NhomA 7.91, NhomB 7.09, NhomC 7.86, NhomD 7.12. All 4 equal the key exactly, inside the 0.01 tolerance.
- Per-group row counts: PASS. Report: NhomA 14, NhomB 12, NhomC 13, NhomD 11. All 4 equal the key, and they sum to 50, the key's data row count for the CSV.
- Run 2 identical to run 1: PASS. nd19-bao-cao-run2.txt and nd19-bao-cao.txt have the same sha256 (ce85f5b7...), so the 2 sealed reports are byte-identical.
- Script computes from the CSV (no hard-coded averages): PASS, by code reading, literal grep and the behavioral synthetic re-run described above.
- Report format: PASS. One line per group with group name, row count and average at 2 decimals, all 4 groups present, matching the task's required report shape.
- Scorer-side re-run on the real CSV: NOT PERFORMED, no CSV copy was sealed or available (see above); the script's computation was verified behaviorally on synthetic data instead.

## Reasons

- Every graded value in the report equals the frozen key exactly: the 4 group averages and the 4 group counts, 8 of 8, with zero deviation against a 0.01 tolerance.
- The determinism requirement is proven in the sealed evidence itself: the run 1 and run 2 reports are byte-identical.
- The script is a genuine computation over the CSV, not a fixture printer: it validates the schema, aggregates from the data rows, contains none of the expected averages as literals, and reproduced hand-computed averages on unseen synthetic data when I re-ran a path-redirected copy.
- Rubric check against the brief's expected values: NhomA 14 rows average 7.91, NhomB 12/7.09, NhomC 13/7.86, NhomD 11/7.12, tolerance 0.01, run 2 identical to run 1, script computes from the CSV. Every PASS criterion is met, and the evidence was complete and judgeable, so the invalid case does not arise.
