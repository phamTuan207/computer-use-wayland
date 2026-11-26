# R3-002 calibration grade (blind, sealed)

- Task: R3-002 (Tier A, type json-errors)
- Session: 951852d2-a7cd-48bc-8bbe-0fb89fda4259
- Verdict: FAIL

## Key hashes (verified)

- docs/rung3-answer-keys.md sha256: 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (matches expected)
- docs/rung3-answer-keys.json sha256: 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8 (matches expected)
- Key section read: docs/rung3-answer-keys.md lines 119-129 only ("## R3-002 (Tier A)"); docs/rung3-answer-keys.json R3-002 entry only (rows: line 1 col 27, line 1 col 50, line 1 col 26).

## Manifest hash (verified)

- rung3-run-log/rung3-snapshots/R3-002-L3/manifest.json, manifest_sha256 field: 0741a1aa90bc20b1257888fc6be33377aae02b351693a581c850b1b4d6852f15 (matches expected)
- Manifest task field: R3-002. Snapshot run window: start_time.txt 2026-11-25T15:26:45, end_time.txt 2026-11-25T15:29:57.

## Per-file hash verification (9/9 match manifest)

| File | Manifest sha256 (prefix) | Actual sha256 | Result |
|---|---|---|---|
| 20261125-154500-json1.png | 1a9daf3f... | 1a9daf3f097340cc6671122704a9ddda36ad0dbb953cf7c4b972faae83da37f0 | MATCH |
| 20261125-154600-json2.png | 1a9daf3f... | 1a9daf3f097340cc6671122704a9ddda36ad0dbb953cf7c4b972faae83da37f0 | MATCH |
| 20261125-154700-json3.png | 1a9daf3f... | 1a9daf3f097340cc6671122704a9ddda36ad0dbb953cf7c4b972faae83da37f0 | MATCH |
| end_time.txt | 048e7a60... | 048e7a60490ffffb74b43affefaa9aeb9f2d225d59078314c58e02598815d37f | MATCH |
| final.png | 92ff892d... | 92ff892d1ea4b2b87a181331bf9b8e74d8a4738f6a425e97f2ba7a5b2f1cb8b7 | MATCH |
| ket-qua.txt | ccdc0fd3... | ccdc0fd33dadac2e56083d117f42761a47b1763249c2266a7635ce5ecdaa4c54 | MATCH |
| pill-verify-gone-2.png | 1a9daf3f... | 1a9daf3f097340cc6671122704a9ddda36ad0dbb953cf7c4b972faae83da37f0 | MATCH |
| pill-verify-gone.png | 92ff892d... | 92ff892d1ea4b2b87a181331bf9b8e74d8a4738f6a425e97f2ba7a5b2f1cb8b7 | MATCH |
| start_time.txt | 9a3a0c66... | 9a3a0c66cce6607fe6a79e38bb935de6c5d04e3ad5faaf4098ac2a3eace9978b | MATCH |

Note: only 2 distinct images exist in the snapshot. The three files 20261125-154500-json1.png, 20261125-154600-json2.png, 20261125-154700-json3.png and pill-verify-gone-2.png are byte-identical (sha256 1a9daf3f...). final.png and pill-verify-gone.png are byte-identical (sha256 92ff892d...). Hash integrity is intact; the duplication is a content defect, not a hash mismatch.

## Files read (allowlist only)

- rung3-run-log/rung3-snapshots/R3-002-L3/manifest.json
- rung3-run-log/rung3-snapshots/R3-002-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-002-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-002-L3/end_time.txt
- rung3-run-log/rung3-snapshots/R3-002-L3/20261125-154500-json1.png
- rung3-run-log/rung3-snapshots/R3-002-L3/20261125-154600-json2.png
- rung3-run-log/rung3-snapshots/R3-002-L3/20261125-154700-json3.png
- rung3-run-log/rung3-snapshots/R3-002-L3/final.png
- rung3-run-log/rung3-snapshots/R3-002-L3/pill-verify-gone.png
- rung3-run-log/rung3-snapshots/R3-002-L3/pill-verify-gone-2.png
- docs/rung3-answer-keys.md (lines 119-129 only)
- docs/rung3-answer-keys.json (R3-002 entry only)

I graded blind from the snapshot and key section only; I did not read the ledger, any grade file, or any other verdict for these tasks

## Grading method

Manual grading from the key criteria. The repo checker (rung3-ci/tier-a-check.py) was NOT run. The key states the checker reads the error line and error column from ket-qua.txt, and the grading evidence is 3 screenshots of Valid JSON + ket-qua.txt. Expected values per the key: segment 1 line 1 col 27, segment 2 line 1 col 50, segment 3 line 1 col 26.

## Reasons for FAIL

1. ket-qua.txt error columns are wrong on all three segments (ket-qua.txt):
   - Segment 1: reported line 1, col 23; key expects line 1, col 27. The trailing-comma error is detected at the closing brace, col 27 (verified by counting: the string is 27 chars, '}' at col 27). Col 23 is the space before "30".
   - Segment 2: reported line 1, col 41; key expects line 1, col 50. The missing-comma error is detected at the opening quote of "so_tien", col 50 (verified by counting). Col 41 is the opening quote of "Ha Noi", the wrong token.
   - Segment 3: reported line 1, col 18; key expects line 1, col 26. The unclosed-bracket error is at end of string, col 26 (string length 25). Col 18 is inside "tuoi".
   - Lines all match (line 1), columns all fail (0/3).
2. No screenshot shows Valid JSON (20261125-154500-json1.png, 20261125-154600-json2.png, 20261125-154700-json3.png, final.png):
   - All three json*.png files are byte-identical and show the jsonlint.com validator with an EMPTY editor ("Click here to start editing JSON..."): no JSON pasted, no validation result, no "Valid JSON" text.
   - final.png (and identical pill-verify-gone.png) shows the same empty editor.
   - The key requires 3 screenshots of Valid JSON, one per fixed segment after repair. Evidence present: 0 of 3.
3. The fixed JSON strings written in ket-qua.txt do parse as valid JSON (verified independently), so the repair text itself is correct, but the graded evidence (reported columns + Valid JSON screenshots) does not meet the key criteria. Correct fix text without correct reported positions and without validation screenshots is a FAIL under the checkable criteria.

## Why not INVALID

No bot-check block was observed on the active page: jsonlint.com loaded and rendered normally in both distinct screenshots, and the editor was usable (empty, not blocked). The "Just a moment..." entries visible in the browser sidebar are background tabs, not the active page. The key section as read (md lines 119-129 + JSON R3-002 entry) contains no bot-check invalid criterion, so no INVALID ruling was applied on that basis.

Ponytail skill: available (~/workspace/custom-skills/ponytail/SKILL.md, 3496 bytes, sha d64edd32, level full).
