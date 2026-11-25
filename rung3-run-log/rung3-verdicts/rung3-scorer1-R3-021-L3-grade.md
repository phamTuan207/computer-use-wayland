# Scorer 1 grade, R3-L3, R3-021

- Session: 70cd99d1-ecef-4d02-9f42-714d7e86ab85 (scorer 1A, Pair A)
- Task: R3-021 (Tier A, position 19, run R3-L3)
- Verdict: PASS
- Scored at: 2026-11-26 02:49:46 +07 (Asia/Ho_Chi_Minh)
- Snapshot: rung3-run-log/rung3-snapshots/R3-021-L3/ at todolist-push commit 441b4ab3, manifest_sha256 fe64cddd88a9f0c4b92185021ed566da5c207e96016c556e9b5766652a7c9a21, all 6 evidence files hash-OK against manifest.json, manifest gate PASS
- Key file hashes (verified before scoring): docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both match the R3-L3 freeze)

## Files read

- rung3-run-log/rung3-snapshots/R3-021-L3/manifest.json (snapshot R3-021-L3, commit 441b4ab3)
- rung3-run-log/rung3-snapshots/R3-021-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-021-L3/ket-qua-truy-van.csv
- rung3-run-log/rung3-snapshots/R3-021-L3/query-results-20261126-022637.jpg
- rung3-run-log/rung3-snapshots/R3-021-L3/query-results-20261126-022929.jpg
- rung3-run-log/rung3-snapshots/R3-021-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-021-L3/end_time.txt
- docs/rung3-answer-keys.md, R3-021 key section (lines 279-285)
- docs/rung3-answer-keys.json, tasks.R3-021 entry (type sql-order-total, order Giuong 600, Tu 400, Ghe 250, Ban 150, total 6750)
- docs/rung3-list-100-tasks.md, section 6, R3-021 task text (lines 424-426)

I scored from the snapshot and the key only. I did not read any other scorer's grade or verdict file, did not contact the runner, and did not read any runner log, ledger, or trial report. I read both screenshots directly, parsed the CSV independently with Python csv, and re-ran both queries independently in an in-memory sqlite3 database built from the key's own table definition and 5 rows. I verified the step-5 total independently by arithmetic.

## Key (R3-021, Tier A)

Table san_pham (id INTEGER PRIMARY KEY, ten TEXT, gia INTEGER, so_luong INTEGER). 5 rows: Ban 150x10, Ghe 250x5, Den 80x20, Tu 400x3, Giuong 600x2. Query step 4 (SELECT ten, gia FROM san_pham WHERE gia > 100 ORDER BY gia DESC), result order: Giuong 600, Tu 400, Ghe 250, Ban 150. Query step 5 (SELECT SUM(gia * so_luong) FROM san_pham): total 6750. CSV file ket-qua-truy-van.csv: 4 result rows (not counting the header row). Scoring evidence: ket-qua-truy-van.csv + ket-qua.txt + query result screenshot. Checker compares order, total, CSV row count.

## Evidence

- ket-qua.txt (400B) records: the step-4 result (Giuong 600, Tu 400, Ghe 250, Ban 150), the step-5 total (6750), the CREATE TABLE statement exactly as in the key, the 5 inserted rows (Ban, 150, 10; Ghe, 250, 5; Den, 80, 20; Tu, 400, 3; Giuong, 600, 2), the CSV file name (ket-qua-truy-van.csv), the page title (SQL Online IDE - Fast SQL Editor | SQL Compiler), and the create-table success note (no text message shown by the site; empty result grid, table san_pham appears in the schema tree). All 7 items the task text step 7 requires are present.
- ket-qua-truy-van.csv (54B) parsed independently: 4 rows, no header row, quoted fields, CRLF endings: ("Giuong","600"), ("Tu","400"), ("Ghe","250"), ("Ban","150"). Order and values match the key exactly.
- Screenshot query-results-20261126-022637.jpg: sqliteonline.com, editor shows SELECT ten, gia FROM san_pham WHERE gia > 100 ORDER BY gia DESC, result grid shows columns ten/gia with rows Giuong 600, Tu 400, Ghe 250, Ban 150. The schema tree shows the san_pham table under SQLite (Demo Memory, the in-memory database). History shows CREATE TABLE san_pham (02:26:18), INSERT INTO san_pham (02:26:23), SELECT COUNT(*) FROM san_pham (02:26:27), and the step-4 query (02:26:32).
- Screenshot query-results-20261126-022929.jpg: sqliteonline.com, same editor query and the same 4-row result grid. The schema tree shows the san_pham table under r3db.db; history shows the CREATE TABLE, INSERT, and step-4 query re-run at 02:29:11-02:29:25. Both screenshots show the same correct result; the runner re-ran the sequence in a named database after the in-memory one, which does not change the outcome.
- Independent verification: re-running the step-4 query in an in-memory sqlite3 database built from the key's table and 5 rows returns [('Giuong', 600), ('Tu', 400), ('Ghe', 250), ('Ban', 150)]; the step-5 query returns 6750; the table count is 5. Arithmetic: 150*10 + 250*5 + 80*20 + 400*3 + 600*2 = 1500 + 1250 + 1600 + 1200 + 1200 = 6750. All match the key, ket-qua.txt, the CSV, and both screenshots.

## Checker discrepancy (documented, same pattern as R3-002)

The coordinator-supplied Tier A checker said FAIL with reason "CSV has 3 data rows, expected 4". That count is wrong for this file. The CSV has 4 rows in total and no header row, so it has 4 data rows, not 3. The checker evidently subtracted one row for an assumed header (4 - 1 = 3, exactly the checker's number). The key does not require a header row: it requires "4 dong ket qua (khong tinh dong tieu de)", that is, 4 result rows, with a header row not counted if one is present. Here there is no header row to exclude, so the count is 4, which meets the key. The checker is an aid only; the evidence and the key agree, so I do not follow the checker's FAIL. The sealing commit message ("Tier A checker FAIL on CSV header count") records the same checker view, not a key requirement.

## Reason

The step-4 query result order matches the key exactly in ket-qua.txt, in the CSV, and in both screenshots (Giuong 600, Tu 400, Ghe 250, Ban 150); the step-5 total is 6750 by independent arithmetic and by an independent sqlite3 re-run; the CSV holds exactly the 4 expected result rows; ket-qua.txt records every item step 7 requires. Every key check passes.

Timing note: start 2026-11-26T02:17:36+07:00, end 2026-11-26T02:40:12.271164+07:00 (22 min 36 s), within the 30-min task timeout; the query screenshots are at 02:26:37 and 02:29:29, inside the run window.

Signed: mochi, scorer 1A, session 70cd99d1-ecef-4d02-9f42-714d7e86ab85.
