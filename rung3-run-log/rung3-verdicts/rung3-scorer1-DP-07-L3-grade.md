# Scorer 1 grade, R3-L3, DP-07

- Session: 70cd99d1-ecef-4d02-9f42-714d7e86ab85 (scorer 1A, Pair A)
- Task: DP-07 (Tier B, medium backup replacing R3-024 INVALID, position 21, run R3-L3)
- Verdict: PASS (scorer 1A)
- Scored at: 2026-11-26 03:55:48 +07 (Asia/Ho_Chi_Minh)
- Snapshot: rung3-run-log/rung3-snapshots/DP-07-L3/ at todolist-push commit b8145eb1, manifest_sha256 7f19b9072e87353c3a3063cb161989d739119209936faab7dcf04c51dfd11382, all 6 evidence files hash-OK against manifest.json, manifest gate PASS
- Key file hashes (verified before scoring): docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both match the R3-L3 freeze)

## Files read

- rung3-run-log/rung3-snapshots/DP-07-L3/manifest.json (snapshot DP-07-L3, commit b8145eb1)
- rung3-run-log/rung3-snapshots/DP-07-L3/bao-cao.txt
- rung3-run-log/rung3-snapshots/DP-07-L3/bang-kiem.txt
- rung3-run-log/rung3-snapshots/DP-07-L3/dp07-terminal-20261126-034642.png
- rung3-run-log/rung3-snapshots/DP-07-L3/dp07-report-20261126-034647.png
- rung3-run-log/rung3-snapshots/DP-07-L3/start_time.txt
- rung3-run-log/rung3-snapshots/DP-07-L3/end_time.txt
- docs/rung3-answer-keys.md, DP-07 key section (lines 676-688)
- docs/rung3-answer-keys.json, allocated.DP-07 entry (files + sha256)
- docs/rung3-list-100-tasks.md, section 8, DP-07 task text (line 733, including Pass/Fail criteria)

I scored from the snapshot and the key only. I did not read any other scorer's grade or verdict file, did not contact the runner, and did not read any runner log, ledger, or trial report. I viewed both screenshots directly and collected my own independent evidence by recreating the 3 files from the key's exact printf strings and re-running sha256sum and sha256sum -c (see below).

## Key (DP-07, Tier B, medium backup)

Contents of 3 files (exact to the byte, each file ends with newline): dp07-01.txt (69 byte) "Rung 3 du phong DP-07, tap 1.\nDong kiem tra thu hai.\nKet thuc tap 1.\n"; dp07-02.txt (69 byte) "Rung 3 du phong DP-07, tap 2.\nDong kiem tra thu hai.\nKet thuc tap 2.\n"; dp07-03.txt (69 byte) "Rung 3 du phong DP-07, tap 3.\nDong kiem tra thu hai.\nKet thuc tap 3.\n". sha256: dp07-01.txt f830f594f7cd7a442b93fda84fe76aa02e62156fd60dcb1c42315424f8b7ede7, dp07-02.txt 26030358212becda0e3e1395761db3f3d0e9620ae67047a0e1ab12e605c25b0c, dp07-03.txt 07c80615e134615320fa0b196b978c329375046a4aff622e013ad86602be9e1a. Total size of 3 files: 207 byte. Check table ~/rung3/dp07-bang-kiem.txt: 3 lines in "<sha256>  <filename>" format (default sha256sum format); verify with sha256sum -c for 3 lines ending in ": OK". Scoring evidence: bao-cao.txt + bang-kiem.txt + terminal screenshot (verification result 3 lines OK). The scorer re-runs sha256sum on the 3 files (read-only) and cross-checks each hash, re-runs sha256sum -c on the check table. Note: if a file's content is wrong by 1 byte, the sha256 is completely different, so this is the intended pass/fail criterion (content accuracy).

Task text (list section 8, DP-07): create 3 text files with printf, compute sha256, write a check table and verify (difficulty medium, type terminal-command). Steps: mkdir -p ~/rung3/dp07-tap, record 0 files initially; printf each of the 3 exact strings to create the files, wc -c each (69 byte); cd into the directory and run sha256sum on the 3 files to write the check table; run sha256sum -c from within the directory to verify (3 lines ending in ": OK"), take a timestamped terminal screenshot; write the report with a 3-row table (filename, size, sha256, check result) and total size 207 byte, copy the report and check table into ~/rung3-chung-cu/DP-07/.

Pass: all 3 files, correct content (each file 69 byte), sha256 matches key, check table has all 3 lines, verification gives 3 lines OK, report has all 3 rows and total size 207 byte. Fail: missing file, wrong size, wrong sha256, check table missing lines, verification not 3 lines OK, report has wrong numbers.

## Evidence

- bao-cao.txt (413B): "DP-07 bao cao kiem tra sha256", directory ~/rung3/dp07-tap, table with 3 rows: dp07-01.txt | 69 | f830f594f7cd7a442b93fda84fe76aa02e62156fd60dcb1c42315424f8b7ede7 | OK; dp07-02.txt | 69 | 26030358212becda0e3e1395761db3f3d0e9620ae67047a0e1ab12e605c25b0c | OK; dp07-03.txt | 69 | 07c80615e134615320fa0b196b978c329375046a4aff622e013ad86602be9e1a | OK. "Tong kich thuoc 3 tap: 207 byte". All 3 hashes match the key exactly, all sizes are 69 byte, total is 207 byte.
- bang-kiem.txt (234B): 3 lines in "<sha256>  <filename>" format with two spaces (default sha256sum format), hashes exactly matching the key for all 3 files.
- Terminal screenshot dp07-terminal-20261126-034642.png: shows the full workflow in the terminal: mkdir -p ~/rung3/dp07-tap; ls -1 | wc -l gives 0; the 3 printf commands with the exact key strings; wc -c gives 69 for dp07-01.txt and 69 each for dp07-02.txt and dp07-03.txt (138 total); cd ~/rung3/dp07-tap && sha256sum on the 3 files to write the check table; cat shows the 3 hashes matching the key; sha256sum -c gives dp07-01.txt: OK, dp07-02.txt: OK, dp07-03.txt: OK.
- Report screenshot dp07-report-20261126-034647.png: shows the same terminal session scrolled down, with the verification (3 lines OK) and cat ~/rung3/dp07-bao-cao.txt displaying the full report, matching the snapshot's bao-cao.txt exactly.
- Independent verification by me: I recreated all 3 files from the key's exact printf strings (in a temp dir, removed after): each is 69 bytes, total 207 bytes; their sha256 values are f830f594..., 26030358..., 07c80615..., exactly matching the key. I then ran sha256sum -c on the snapshot's bang-kiem.txt against the recreated files: dp07-01.txt: OK, dp07-02.txt: OK, dp07-03.txt: OK, exit 0. The check table is valid and the key's hashes are correct for the specified contents.

## Reason

All 3 files have the correct content (69 bytes each, exact key strings), their sha256 hashes match the key, the check table has all 3 lines in the correct format and verifies with 3 lines OK (both in the runner's terminal screenshot and in my independent re-run), and the report has all 3 rows with correct sizes, hashes, and OK results plus the correct total of 207 bytes. Every Pass criterion is met.

Minor note: the report screenshot shows the runner also ran `python3 ~/rung3/dp07-gen.py` (output "GEN OK total=207") before displaying the report. The task does not require the report to be written by hand, and the report's content is correct and matches the key; the generator script does not change the result. This is a note for the coordinator, not a fail.

Timing note: start 2026-11-26T03:43:58+07:00, end 2026-11-26T03:47:06+07:00 (3 min 8 s), within the 30-min task timeout.

Signed: mochi, scorer 1A, session 70cd99d1-ecef-4d02-9f42-714d7e86ab85.
