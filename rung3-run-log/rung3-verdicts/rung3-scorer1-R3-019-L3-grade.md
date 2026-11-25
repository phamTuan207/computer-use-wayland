# Scorer 1 grade, R3-L3, R3-019

- Session: 70cd99d1-ecef-4d02-9f42-714d7e86ab85 (scorer 1A, Pair A)
- Task: R3-019 (Tier B, position 18, run R3-L3)
- Verdict: PASS
- Scored at: 2026-11-26 02:10:01 +07 (Asia/Ho_Chi_Minh)
- Snapshot: rung3-run-log/rung3-snapshots/R3-019-L3/ at todolist-push commit 21fc43f8, manifest_sha256 c21f3909933a08204c615d647dcfcde4bbaf3b30002d49d07ab1133f3b81da62, all 6 evidence files hash-OK against manifest.json, manifest gate PASS
- Key file hashes (verified before scoring): docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both match the R3-L3 freeze)

## Files read

- rung3-run-log/rung3-snapshots/R3-019-L3/manifest.json (snapshot R3-019-L3, commit 21fc43f8)
- rung3-run-log/rung3-snapshots/R3-019-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-019-L3/20261126-014322-kiwi-date1.png
- rung3-run-log/rung3-snapshots/R3-019-L3/20261126-014401-kiwi-date2.png
- rung3-run-log/rung3-snapshots/R3-019-L3/20261126-015859-doc-reopened.png
- rung3-run-log/rung3-snapshots/R3-019-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-019-L3/end_time.txt
- docs/rung3-answer-keys.md, R3-019 key section (lines 271-277)
- docs/rung3-list-100-tasks.md, section 6, R3-019 task text (lines 417-419)

I scored from the snapshot and the key only. I did not read any other scorer's grade or verdict file, did not contact the runner, and did not read any runner log, ledger, or trial report. I read each of the 3 screenshots directly and cross-checked every value in ket-qua.txt against them. I verified the two dates independently with date -d (run date 2026-11-26 + 30 days = 2026-12-26, + 37 days = 2027-01-02, both Saturdays).

## Key (R3-019, Tier B)

Route: Hanoi to Ho Chi Minh. Date 1 = run date + 30 days, date 2 = run date + 37 days; specific dates are fixed only when the run date is set. Each date records: lowest price, flight time, airline. 2-row date table. Price difference calculated correctly. Conclusion names the specific chosen date. Do not buy tickets. Prices are live at run time; the truth is the price screenshot for each date, not the current price. If the page shows a bot-check page or asks for human verification, stop, record it in ket-qua.txt, task invalid per section 1. Evidence: 2 price screenshots + online document (table + conclusion). The scorer cross-checks prices against the screenshots.

## Evidence

- ket-qua.txt (466B) records: the Google Docs document URL; route Hanoi (HAN) to Ho Chi Minh City (SGN), one-way, Kiwi.com; Date 1: 2026-12-26, Price $62, Flight time 20:50 - 23:00 (2h 10m, direct), Airline VietJet Air; Date 2: 2027-01-02, Price $67, Flight time 22:25 - 00:35 (+1) (2h 10m, direct), Airline VietJet Air; Price difference $5; Conclusion: Choose 2026-12-26 (cheapest at $62, $5 cheaper than 2027-01-02).
- Screenshot kiwi-date1 (01:43:22): Kiwi.com, From Hanoi, To Ho Chi Minh City, Departure Sat 26 Dec, One-way, Economy, 1 Passenger. Date strip shows Sat 26 Dec $62 selected. Best $62, 2h 10m; Cheapest $62, 2h 10m; Fastest $62, 2h 10m. First flight card: 20:50 HAN, 2h 10m, Direct, VietJet logo, 23:00 SGN, $62. Matches ket-qua.txt date 1 exactly on price, flight time, and airline.
- Screenshot kiwi-date2 (01:44:01): Kiwi.com, From Hanoi, To Ho Chi Minh City, Departure Sat 2 Jan, One-way, Economy, 1 Passenger. Date strip shows Sat 2 Jan $67 selected. Best $67, 2h 10m; Cheapest $67, 2h 10m; Fastest $67, 2h 10m. First flight card: 22:25 HAN, 2h 10m, Direct, VietJet logo, 00:35+1 SGN, $67. Matches ket-qua.txt date 2 exactly on price, flight time, and airline. This is a different date from screenshot 1.
- Screenshot doc-reopened (01:58:59): the reopened Google Docs document "R3-019 Kiwi flight price comparison" with the heading "Hanoi to Ho Chi Minh flight price comparison (Kiwi.com)", a table with header Date | Price | Flight time | Airline and 2 rows (2026-12-26, 62 USD, 20:50 - 23:00 (2h 10m), VietJet Air; 2027-01-02, 67 USD, 22:25 - 00:35 (+1) (2h 10m), VietJet Air), and below the table "Price difference: 5 USD. Conclusion: choose 2026-12-26 (cheapest at 62 USD, 5 USD cheaper than 2027-01-02)." Every value in the document matches ket-qua.txt and the two Kiwi screenshots. The document was saved and reopened, as the task requires.
- Price difference arithmetic: $67 - $62 = $5, correct. The conclusion names the specific chosen date (2026-12-26), which is the cheaper of the two.
- No bot-check page and no human-verification request appeared, so the task ran normally and no invalid condition applies. No ticket was purchased.

## Reason

Both dates are the correct key dates (run date + 30 and + 37 days), both lowest prices match the Kiwi screenshots exactly ($62 for 2026-12-26, $67 for 2027-01-02), both flight times and airlines match the screenshots exactly, the price difference is calculated correctly ($5), and the document contains the 2-row table plus a conclusion naming the specific cheaper date. Every key check passes.

Timing note: start 2026-11-26T01:37:02+07:00, end 2026-11-26T02:03:09+07:00 (26 min 7 s), within the 30-min task timeout; the Kiwi screenshots are at 01:43:22 and 01:44:01 and the document reopen screenshot at 01:58:59, consistent with searching both dates, then creating the document and reopening it.

Signed: mochi, scorer 1A, session 70cd99d1-ecef-4d02-9f42-714d7e86ab85.
