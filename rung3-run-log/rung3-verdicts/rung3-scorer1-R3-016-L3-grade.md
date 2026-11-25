# Scorer 1 grade, R3-L3, R3-016

- Session: 70cd99d1-ecef-4d02-9f42-714d7e86ab85 (scorer 1A, Pair A)
- Task: R3-016 (Tier B, position 15, run R3-L3)
- Verdict: PASS
- Scored at: 2026-11-26 01:09:31 +07 (Asia/Ho_Chi_Minh)
- Snapshot: rung3-run-log/rung3-snapshots/R3-016-L3/ at todolist-push commit a5abe880, manifest_sha256 dd4992764d5923e5baf24b408471bcfd41e13cbc987a663b5350c6d82a0bdf2d, all 5 evidence files hash-OK against manifest.json, manifest gate PASS
- Key file hashes (verified before scoring): docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both match the R3-L3 freeze)

## Files read

- rung3-run-log/rung3-snapshots/R3-016-L3/manifest.json (snapshot R3-016-L3, commit a5abe880)
- rung3-run-log/rung3-snapshots/R3-016-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-016-L3/du-lieu.csv
- rung3-run-log/rung3-snapshots/R3-016-L3/20261126-005725-mockaroo-preview.png
- rung3-run-log/rung3-snapshots/R3-016-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-016-L3/end_time.txt
- docs/rung3-answer-keys.md, R3-016 key section (lines 246-254)
- docs/rung3-answer-keys.json, R3-016 entry only (allocated.R3-016)
- docs/rung3-list-100-tasks.md, section 6, R3-016 task text (lines 394-396)

I scored from the snapshot and the key only. I did not read any other scorer's grade or verdict file, did not contact the runner, and did not read any runner log, ledger, or trial report. I opened and parsed du-lieu.csv myself and counted every row, column, email, and age.

## Key (R3-016, Tier B)

Schema 4 fields: First Name (First Name), Last Name (Last Name), Email Address (Email Address), Age (Number) with min value 18 and max value 90. Number of rows: 10. Format: CSV. File: du-lieu.csv. Checks: 10 data rows, 4 columns, column names match the 4 fields, every row has all 4 values, every email has @ character, every age is an integer from 18 to 90. Test account: not needed (verified by browser before the R3-L3 freeze: Mockaroo allows CSV download without an account). Evidence: du-lieu.csv + ket-qua.txt + preview screenshot. The scorer opens the CSV file and counts.

## Evidence

- ket-qua.txt (738B) records: the Mockaroo page title; the 4 fields with types (First Name, Last Name, Email Address, Age Number min 18 max 90); a schema note from DOM read-back (format csv, rows 10, Age min 18 max 90, the 4 field names and types); rows requested 10, format CSV; CSV data rows (excluding header) 10; CSV columns (4) First Name, Last Name, Email Address, Age; every row has 4 values True; email verification (every email contains @) True; age verification (every age integer 18-90) True.
- du-lieu.csv (441B), verified independently by parsing it: header First Name, Last Name, Email Address, Age (matches the 4 key fields exactly); 10 data rows; every row has 4 values and no empty value; every email contains @ (10 emails, vharden0@mashable.com through jfrascone9@businessweek.com); every age is an integer 18-90 (81, 41, 30, 43, 85, 42, 71, 85, 73, 28). Every claim in ket-qua.txt about the CSV is confirmed.
- Preview screenshot 20261126-005725-mockaroo-preview.png (00:57:25): the Mockaroo Preview dialog, TABLE tab, shows 4 columns (First Name, Last Name, Email Address, Age) and 10 data rows, with "# Rows: 10" at the bottom. Every preview row has 4 values, every preview email has @, every preview age is an integer 18-90 (54, 82, 54, 33, 31, 77, 58, 80, 86, 28). No login screen is shown; the page works without an account, as the key expects.
- Note on the preview vs the CSV: the preview shows different names, emails, and ages from du-lieu.csv. This is expected and correct: Mockaroo generates random data on each Preview/Generate, so the preview and the downloaded CSV are two separate generations. The key checks structure (10 rows, 4 columns, correct column names, all rows complete, emails with @, ages 18-90), not specific random values, and both the preview and the CSV pass every structural check.

## Reason

du-lieu.csv has 10 data rows, 4 columns with the exact key field names, every row has all 4 values, every email contains @, and every age is an integer 18-90. ket-qua.txt records the 4 fields with types, the row count, the 4 column names, and the email and age check results, all confirmed against the CSV. The preview screenshot shows the Mockaroo preview with 10 rows and 4 columns and no login screen. Every key check passes.

Timing note: start 2026-11-26T00:38:32+07:00, end 2026-11-26T01:01:15+07:00 (22 min 43 s), within the 30-min task timeout; the duration is consistent with setting up 4 schema fields with types and min/max, previewing, and downloading.

Signed: mochi, scorer 1A, session 70cd99d1-ecef-4d02-9f42-714d7e86ab85.
