# R3-014 calibration grade (clone2, sealed, blind)

- Task: R3-014 (Tier A)
- Grader: clone2
- Session: clone2-main-ad85548c-ced4-4f31-afdb-d1043dcabbd7
- Date: 2026-11-26
- Verdict: PASS

## Key verification

- docs/rung3-answer-keys.md sha256: 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (matches the brief)
- docs/rung3-answer-keys.json sha256: 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8 (matches the brief)
- Key section used: docs/rung3-answer-keys.md, "## R3-014 (Tier A)", lines 237-245

## Snapshot verification

- Snapshot: rung3-run-log/rung3-snapshots/R3-014-L3/
- Manifest hash (manifest_sha256 field in manifest.json): b6540e2c0cb71c03830f8a902d95447bf8f427fc18ccb1b9e81a7ac2c1115e23 (matches the brief)
- Per-file sha256 verification against manifest.json (recomputed, hash and size): all OK
  - 20261126-002359-FF0000.png 46e023b7bbab957be1abec84e17c1583657bd448e175245717f1eb4077a5d3bb OK
  - 20261126-002424-008080.png 1524d1b9df530db823607aba4f48b4a01e69101382c4eeab01ba14767acd21f1 OK
  - 20261126-002446-FFD700.png 5ce64fc20ab1d798406598591a490873ae2f88252bcae99adcb11a44c28163f3 OK
  - end_time.txt b2f93e269ea539abae0fc0c1502f9f1e0181aa0a42f6fbf8c0b182c55978441c OK
  - ket-qua.txt 2fffa3255513ca56d836506e632cb6cc140b5c0a735b95d7df8bc3c17a200e90 OK
  - start_time.txt 7d0c227b5a3cfee197990fc5a16b636d6752f9bb813ca40cbde60085a56ecf57 OK
- No files in the snapshot dir beyond the manifest list.

## Files read

- rung3-run-log/briefs/clone2-calibration-brief.md (the assignment)
- docs/rung3-answer-keys.md (sha256 verification; key section lines 237-245 only)
- docs/rung3-answer-keys.json (sha256 verification; also passed as --key to the Tier A checker)
- docs/rung3-list-100-tasks.md section 1, lines 9-40 (grading rules, as the brief directs)
- rung3-ci/tier-a-check.py (executed, see below)
- rung3-run-log/rung3-snapshots/R3-014-L3/manifest.json
- rung3-run-log/rung3-snapshots/R3-014-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-014-L3/20261126-002359-FF0000.png
- rung3-run-log/rung3-snapshots/R3-014-L3/20261126-002424-008080.png
- rung3-run-log/rung3-snapshots/R3-014-L3/20261126-002446-FFD700.png
- rung3-run-log/rung3-snapshots/R3-014-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-014-L3/end_time.txt

## Independence declaration

I graded blind from the snapshot and key section only; I did not read the ledger, any grade file, or any other verdict for these tasks.

## Reasons

- I ran rung3-ci/tier-a-check.py against the frozen key JSON (python3 rung3-ci/tier-a-check.py --key docs/rung3-answer-keys.json --evidence rung3-run-log/rung3-snapshots/R3-014-L3 --task R3-014), as real scorers do. It returned verdict PASS with exit code 0, no reasons, and key_hash 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8.
- My own comparison of ket-qua.txt against the key section agrees: hex and RGB match the key exactly for all 3 colors (#FF0000 RGB(255, 0, 0); #008080 RGB(0, 128, 128); #FFD700 RGB(255, 215, 0)).
- The key grades HSL by the page display, checked against the screenshots. All 3 screenshots are present and legible, each showing the htmlcolorcodes.com picker for one code with matching hex, RGB and HSL readouts: FF0000 shows RGB 255, 0, 0 and HSL 0, 100, 50; 008080 shows RGB 0, 128, 128 and HSL 180, 100, 25; FFD700 shows RGB 255, 215, 0 and HSL 51, 100, 50. These match the HSL values recorded in ket-qua.txt.
- Run window from start_time.txt and end_time.txt: 2026-11-26T00:20:14+07:00 to 00:24:46+07:00, inside the 30 minute limit.
