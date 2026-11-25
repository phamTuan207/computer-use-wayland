# Scorer 1 grade, R3-L3, R3-013

- Session: 70cd99d1-ecef-4d02-9f42-714d7e86ab85 (scorer 1A, Pair A)
- Task: R3-013 (Tier A, position 13, run R3-L3)
- Verdict: PASS
- Scored at: 2026-11-26 00:08:53 +07 (Asia/Ho_Chi_Minh)
- Snapshot: rung3-run-log/rung3-snapshots/R3-013-L3/ at todolist-push commit 9edd5dcd, manifest_sha256 7d4a5c763010c87fb5b90378edfe022eb0dad88601105019207ad7bb5e8e161d, all 9 evidence files hash-OK against manifest.json, manifest gate PASS
- Key file hashes (verified before scoring): docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both match the R3-L3 freeze)
- Tier A checker (coordinator-supplied, aid only): {"verdict": "PASS", "reasons": [], "task": "R3-013", "key_hash": "5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8"}. I verified the evidence independently below; my verdict agrees with the checker. No checker-vs-evidence discrepancy found.

## Files read

- rung3-run-log/rung3-snapshots/R3-013-L3/manifest.json (snapshot R3-013-L3, commit 9edd5dcd)
- rung3-run-log/rung3-snapshots/R3-013-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-013-L3/explanation5.txt
- rung3-run-log/rung3-snapshots/R3-013-L3/20261125-235731-regex-1.png
- rung3-run-log/rung3-snapshots/R3-013-L3/20261125-235741-regex-2.png
- rung3-run-log/rung3-snapshots/R3-013-L3/20261125-235750-regex-3.png
- rung3-run-log/rung3-snapshots/R3-013-L3/20261125-235759-regex-4.png
- rung3-run-log/rung3-snapshots/R3-013-L3/20261125-235808-regex-5.png
- rung3-run-log/rung3-snapshots/R3-013-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-013-L3/end_time.txt
- docs/rung3-answer-keys.md, R3-013 key section (lines 225-233) and the pattern-3 escaped-form ruling (line 17)
- docs/rung3-answer-keys.json, R3-013 entry only (tasks.R3-013, type regex-counts)
- docs/rung3-list-100-tasks.md, section 6, R3-013 task text (lines 380-382)

I scored from the snapshot and the key only. I did not read any other scorer's grade or verdict file, did not contact the runner, and did not read any runner log, ledger, or trial report. I ran all 5 key patterns against the key's sample text myself with Python re to verify the key, and I read each of the 5 screenshots directly.

## Key (R3-013, Tier A)

Sample text: 'Lien he Hoa qua hoa@example.com hoac goi 0987654321. Hop luc 09:15 ngay 03/09/2026 tai Da Nang, ket thuc luc 17:45. Ma don DH-2026-0903, tong 2.750.000 VND, phi dich vu 350.000 VND. Han chot 10/09/2026. Email khac dung@test.org va khanh@example.com, dien thoai khac 0978123456. Lien he khan cap 0905551234.'

5 patterns and match counts:
1. Email: [A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,} : 3 results (hoa@example.com, dung@test.org, khanh@example.com)
2. Phone: 0\d{9} : 3 results (0987654321, 0978123456, 0905551234)
3. Date: \d{2}\/\d{2}\/\d{4} (escaped form, see ruling) : 2 results (03/09/2026, 10/09/2026)
4. Time: \d{2}:\d{2} : 2 results (09:15, 17:45)
5. Amount: \d{1,3}(?:\.\d{3})+ : 2 results (2.750.000, 350.000)

The site's explanation for pattern 5 must be recorded in ket-qua.txt. Evidence: 5 result screenshots + ket-qua.txt. The checker compares pattern (normalizing \/ to /), count, and matched strings. Ruling (line 17): pattern 3 in the frozen key file is the escaped form \d{2}\/\d{2}\/\d{4}; / is a delimiter in regex101 JS flavor so the unescaped form errors; the checker accepts both forms, but the escaped form is the standard in the key.

## Evidence

- ket-qua.txt (722B) records all 5 lines, each with pattern, count, and matches, matching the key exactly:
  1. [A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,} | 3 | hoa@example.com, dung@test.org, khanh@example.com
  2. 0\d{9} | 3 | 0987654321, 0978123456, 0905551234
  3. \d{2}\/\d{2}\/\d{4} | 2 | 03/09/2026, 10/09/2026
  4. \d{2}:\d{2} | 2 | 09:15, 17:45
  5. \d{1,3}(?:\.\d{3})+ | 2 | 2.750.000, 350.000
  Plus "Explanation pattern 5:" followed by the full explanation text (also saved separately in explanation5.txt).
- Pattern 3 is recorded in the escaped form \d{2}\/\d{2}\/\d{4}, the standard form in the key, not the unescaped form.
- Screenshot regex-1 (23:57:31): regex101.com, JavaScript flavor, pattern 1, "3 matches", Match Information lists hoa@example.com (16-31), dung@test.org (214-227), khanh@example.com (231-248). Matches the key.
- Screenshot regex-2 (23:57:41): pattern 0\d{9}, "3 matches", Match Information lists 0987654321 (41-51), 0978123456 (266-276), 0905551234 (295-305). Matches the key.
- Screenshot regex-3 (23:57:50): pattern \d{2}\/\d{2}\/\d{4} (escaped form, visible in the pattern box), "2 matches", Match Information lists 03/09/2026 (72-82), 10/09/2026 (191-201). Matches the key.
- Screenshot regex-4 (23:57:59): pattern \d{2}:\d{2}, "2 matches", Match Information lists 09:15 (61-66), 17:45 (109-114). Matches the key.
- Screenshot regex-5 (23:58:08): pattern \d{1,3}(?:\.\d{3})+, "2 matches", Match Information lists 2.750.000 (142-151), 350.000 (169-176). The Explanation panel is visible and matches the explanation recorded in ket-qua.txt and explanation5.txt: \d{1,3} a digit repeated between 1 and 3 times; Non-Capturing Group (?:\.\d{3})+ repeats the group contents at least once (\. the literal ., \d{3} a digit repeated exactly 3 times); g modifier global, m modifier multiline.
- Independent key check: I ran all 5 key patterns against the key's sample text with Python re; every pattern produced exactly the key's count and matches, so the key itself is correct.

## Reason

All 5 lines in ket-qua.txt match the key exactly on pattern, count, and matched strings; pattern 3 uses the escaped form the key requires; the explanation for pattern 5 is recorded in ket-qua.txt and matches the regex101 Explanation panel in the screenshot; all 5 result screenshots are present and each shows the correct pattern, match count, and matches on regex101.com. The Tier A checker said PASS; my independent verification agrees, with no discrepancy.

Timing note: start 2026-11-25T23:57:04+07:00, end 2026-11-25T23:58:32+07:00 (1 min 28 s); the 5 screenshots are timestamped 23:57:31, 23:57:41, 23:57:50, 23:57:59, 23:58:08, about 9-10 s apart, consistent with entering 5 patterns one by one.

Signed: mochi, scorer 1A, session 70cd99d1-ecef-4d02-9f42-714d7e86ab85.
