# R3-007 calibration grade (clone2, sealed, blind)

- Task: R3-007 (Tier A)
- Grader: clone2
- Session: clone2-main-ad85548c-ced4-4f31-afdb-d1043dcabbd7
- Date: 2026-11-26
- Verdict: PASS

## Key verification

- docs/rung3-answer-keys.md sha256: 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (matches the brief)
- docs/rung3-answer-keys.json sha256: 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8 (matches the brief)
- Key section used: docs/rung3-answer-keys.md, "## R3-007 (Tier A)", lines 173-184

## Snapshot verification

- Snapshot: rung3-run-log/rung3-snapshots/R3-007-L3/
- Manifest hash (manifest_sha256 field in manifest.json): 4be235466584890828e249224f0a8700a0f5f2eb783eaa4c609ac90c9d87a7c2 (matches the brief)
- Per-file sha256 verification against manifest.json (recomputed, hash and size): all OK
  - 20261125-214834-convert-1.png b0e7c60bae2a9561d7a43f96602a872a55d2f6d6ad0b7d0b5e8c29c773314ff4 OK
  - 20261125-214842-convert-2.png bc12df8f2f043102dee70560411fc4f4ecd044cdeaacf4a1b50ccb36a7f75754 OK
  - 20261125-214850-convert-3.png cd7d8d49e123d1bbcaf6fb2bfb630ca3dc736b3dd996ac7d1ef8c0c3e699bcf4 OK
  - 20261125-214858-convert-4.png 39fce2c52722cc5ae0f0785730faa6bc4a78b3fc0ca5094f7c828b5c422ba0c8 OK
  - 20261125-214906-convert-5.png 245e5853853ca8349dfdbfd12df30282c5e70df81e5a0d4650c9dd5d1f2eab69 OK
  - end_time.txt afcc7de0587452d65d6a8ce4163a7b0114c84bea00829457cb819d3ac5564857 OK
  - ket-qua.txt 74ca8d14d5884c951cb744a03b50b523830ae591a1acd9dc4574b43fb022b0cb OK
  - start_time.txt 11b67ffbd78c9e4578375fa9400d037e3985b6ade818594135fc258ecb43d275 OK
- No files in the snapshot dir beyond the manifest list.

## Files read

- rung3-run-log/briefs/clone2-calibration-brief.md (the assignment)
- docs/rung3-answer-keys.md (sha256 verification; key section lines 173-184 only)
- docs/rung3-answer-keys.json (sha256 verification; also passed as --key to the Tier A checker)
- docs/rung3-list-100-tasks.md section 1, lines 9-40 (grading rules, as the brief directs)
- rung3-ci/tier-a-check.py (executed, see below)
- rung3-run-log/rung3-snapshots/R3-007-L3/manifest.json
- rung3-run-log/rung3-snapshots/R3-007-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-007-L3/20261125-214834-convert-1.png
- rung3-run-log/rung3-snapshots/R3-007-L3/20261125-214842-convert-2.png
- rung3-run-log/rung3-snapshots/R3-007-L3/20261125-214850-convert-3.png
- rung3-run-log/rung3-snapshots/R3-007-L3/20261125-214858-convert-4.png
- rung3-run-log/rung3-snapshots/R3-007-L3/20261125-214906-convert-5.png
- rung3-run-log/rung3-snapshots/R3-007-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-007-L3/end_time.txt

## Independence declaration

I graded blind from the snapshot and key section only; I did not read the ledger, any grade file, or any other verdict for these tasks.

## Reasons

- I ran rung3-ci/tier-a-check.py against the frozen key JSON (python3 rung3-ci/tier-a-check.py --key docs/rung3-answer-keys.json --evidence rung3-run-log/rung3-snapshots/R3-007-L3 --task R3-007), as real scorers do. It returned verdict PASS with exit code 0, no reasons, and key_hash 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8.
- My own comparison of ket-qua.txt against the key section agrees: all 5 lines follow the required format and fall inside the 0.01 rounding tolerance. Differences from the key values: 12 km line 0.0000457, 8 miles line 0.000048, 7 kg line 0.0000416, 30 C line exact (86), 5 L line 0.0000397.
- All 5 screenshots are present and legible, and each shows the matching UnitConverters.net result line: convert-1 "12 kilometer = 7.4564543068 mile", convert-2 "8 mile = 12.874752 kilometer", convert-3 "7 kilogram = 15.432358353 pound", convert-4 "30 Celsius = 86 Fahrenheit", convert-5 "5 liter = 1.3208602618 gallon (US)". The screenshots agree with ket-qua.txt line by line.
- Run window from start_time.txt and end_time.txt: 2026-11-25T21:48:24+07:00 to 21:49:08+07:00, inside the 30 minute limit.
