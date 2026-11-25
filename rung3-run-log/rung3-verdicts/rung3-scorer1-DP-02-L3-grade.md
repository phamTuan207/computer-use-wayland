# Scorer 1 grade, R3-L3, DP-02

- Session: 70cd99d1-ecef-4d02-9f42-714d7e86ab85 (scorer 1A, Pair A)
- Task: DP-02 (Tier A, hard backup replacing R3-022 INVALID, position 20, run R3-L3)
- Verdict: PASS (scorer 1A)
- Scored at: 2026-11-26 03:44:48 +07 (Asia/Ho_Chi_Minh)
- Snapshot: rung3-run-log/rung3-snapshots/DP-02-L3/ at todolist-push commit 1cdbe8ff, manifest_sha256 fe58d4235f88a1870611239dfa3ca3d8584cf62cd8fb3a968ce3500da931da39, all 16 evidence files hash-OK against manifest.json, manifest gate PASS
- Key file hashes (verified before scoring): docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both match the R3-L3 freeze)

## Files read

- rung3-run-log/rung3-snapshots/DP-02-L3/manifest.json (snapshot DP-02-L3, commit 1cdbe8ff)
- rung3-run-log/rung3-snapshots/DP-02-L3/bao-cao.txt
- rung3-run-log/rung3-snapshots/DP-02-L3/dp02-code/dp02-01.txt through dp02-12.txt (all 12 fixture files)
- rung3-run-log/rung3-snapshots/DP-02-L3/start_time.txt
- rung3-run-log/rung3-snapshots/DP-02-L3/end_time.txt
- docs/rung3-answer-keys.md, DP-02 key section (lines 619-646)
- docs/rung3-answer-keys.json, tasks.DP-02 entry (type keyword-counts, grand_total 54, files_with_keyword 12, 5 keyword entries, per_file 12x5 matrix)
- docs/rung3-list-100-tasks.md, section 8, DP-02 task text (including Pass/Fail criteria)

I scored from the snapshot and the key only. I did not read any other scorer's grade or verdict file, did not contact the runner, and did not read any runner log, ledger, or trial report. I re-ran grep -r -o -F (read-only) on all 12 fixture files myself, per the key's cross-check instruction, and compared every number to the key and to the report.

## Key (DP-02, Tier A, hard backup)

Fixture: ~/rung3/dp02-code, 12 text files (dp02-01.txt to dp02-12.txt), each 20-60 lines. 5 keywords (letters and digits only, no keyword is a substring of another): alpha7 total 12, most-hit file dp02-01.txt (4 hits); bravo21 total 9, most-hit file dp02-02.txt (3 hits); charlie9 total 15, most-hit file dp02-03.txt (5 hits); delta42 total 7, most-hit file dp02-06.txt (3 hits); echo13 total 11, most-hit file dp02-04.txt (4 hits). Grand total of all 5 keywords: 54. Number of files containing at least 1 of the 5 keywords: 12 (all 12 files). The key also gives the per-file hit table (12 files x 5 keywords, counted with grep -r -o -F, never -w) for the scorer's cross-check. Each most-hit file is unique (no tie for any keyword). Scoring evidence: report dp02-bao-cao.txt + copy in ~/rung3-chung-cu/DP-02/bao-cao.txt. The scorer re-runs grep -r -o -F (read-only) and cross-checks each number. Note: tier-a-check.py has a keyword-counts checker; DP-02 is scored by script, and the hand grep is the fallback cross-check.

Task text (list section 8, DP-02): find 5 keywords in a directory tree with grep -r, count true occurrences, write a report (difficulty hard, type terminal-command). Steps: check the fixture has 12 files, record file count and total lines; run grep -r -o -F <keyword> on the fixture, count true occurrences with wc -l, record the total and the most-hit file name (never -w, partial matches of a longer word still count; group the filename:result lines by file or run grep per file to find the most-hit file; each keyword appears at least 3 times; on a tie take the first file by filename order); repeat for the other 4 keywords; run grep -r -l -F with the 5 keywords to list files containing at least 1 keyword, count the files, record the names of those files.

Pass (list section 8): report has all 5 rows, total true occurrences of each keyword correct, most-hit file name of each keyword correct, number of files containing keywords correct, grand total correct, re-run matches. Fail: missing keyword, wrong total, wrong most-hit file name, wrong file count, report not saved, re-run does not match.

## Evidence

- bao-cao.txt (337B):
  - alpha7: tong 12, file nhieu hit nhat dp02-01.txt (4 hit)
  - bravo21: tong 9, file nhieu hit nhat dp02-02.txt (3 hit)
  - charlie9: tong 15, file nhieu hit nhat dp02-03.txt (5 hit)
  - delta42: tong 7, file nhieu hit nhat dp02-06.txt (3 hit)
  - echo13: tong 11, file nhieu hit nhat dp02-04.txt (4 hit)
  - Tong chung: 54
  - So file chua it nhat 1 tu khoa: 12
- All 5 keyword rows are present. Every total, every most-hit file, the grand total (54), and the file count (12) match the key exactly.
- Independent verification by me (grep -r -o -F, never -w, run on the snapshot's dp02-code/ files): the per-file hit matrix matches the key for ALL 12 files (12/12 KEY-MATCH), with totals alpha7 12, bravo21 9, charlie9 15, delta42 7, echo13 11, grand total 54. Top files: alpha7 dp02-01.txt (4), bravo21 dp02-02.txt (3), charlie9 dp02-03.txt (5), delta42 dp02-06.txt (3), echo13 dp02-04.txt (4), all unique, no ties. Files containing at least 1 keyword: 12. Line counts also match the key for all 12 files (40, 35, 45, 30, 50, 25, 60, 20, 55, 38, 28, 48; total 474 lines). The re-run matches the key and the report exactly, so the Pass criterion "chay lai khop" is met.

## CHECKER DISCREPANCY (documented in full)

The coordinator-supplied Tier A checker said FAIL, with 12 reasons: "report per-file detail missing for dp02-01.txt in bao-cao.txt" through "dp02-12.txt". I disagree with the checker, for the following reasons, and I judged from the evidence and the key, as the brief requires:

1. The checker's expectation is not in the key's Pass criteria. The Pass criteria (list section 8) require exactly six things: the report has all 5 rows, each keyword's total is correct, each keyword's most-hit file name is correct, the number of files containing keywords is correct, the grand total is correct, and the re-run matches. They do not require the report to contain per-file hit detail (the 12x5 matrix) for all 12 files. The report satisfies all six.
2. The key's per-file table is the scorer's cross-check data, not a report requirement. Keys.md says: "Nguoi cham chay lai lenh grep -r -o -F (chi doc) va doi chieu tung so" (the scorer re-runs grep read-only and cross-checks each number). I did that, and the per-file matrix matches the key 12/12, so the underlying data is correct.
3. The checker flags per-file detail as missing even for files that ARE named in the report (dp02-01.txt, dp02-02.txt, dp02-03.txt, dp02-04.txt, dp02-06.txt appear as most-hit files), which shows it is looking for per-file hit counts, not file names. That is a checker expectation, not a key requirement.
4. This is the third checker discrepancy of this kind in R3-L3: R3-002 re-run (checker said FAIL, independent verification found all 3 error positions correct, PASS) and R3-021 (checker said FAIL on a CSV header assumption, independent verification found 4 rows correct, PASS, later graded PASS via tiebreaker). The pattern is the same: the checker demands something the key does not require, and independent verification of the evidence against the key's Pass criteria gives PASS.

Minor note: step 4 of the task text asks the runner to record the names of the files containing at least 1 keyword; the report records only the count (12), not the names. The Pass criteria require only that the file count be correct ("so file chua tu khoa dung"), which it is, and the Fail criteria list only a wrong file count ("sai so file"), which does not apply. Since all 12 files contain at least 1 keyword, the count fully determines the set. This is a note for the coordinator, not a fail.

## Reason

The report has all 5 keyword rows with correct totals (12, 9, 15, 7, 11), correct most-hit files (dp02-01, dp02-02, dp02-03, dp02-06, dp02-04), correct grand total (54), and correct file count (12), and my independent grep re-run matches the key's per-file matrix 12/12, so every Pass criterion is met. The Tier A checker's FAIL is a checker expectation (per-file detail in the report) that the key's Pass criteria do not require; documented in full above.

Timing note: start 2026-11-26T03:30:42+07:00, end 2026-11-26T03:31:25+07:00 (43 s). Fast, but this is a grep task on 12 small text files (474 lines total), and every number was independently verified, so timing alone is not a fail.

Signed: mochi, scorer 1A, session 70cd99d1-ecef-4d02-9f42-714d7e86ab85.
