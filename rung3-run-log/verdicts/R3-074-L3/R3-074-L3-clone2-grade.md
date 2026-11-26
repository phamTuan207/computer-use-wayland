# R3-074 scorer 1 grade (Pair B, R3-L3, Class L, Tier B)

scorer session ID: clone2-main-ad85548c-ced4-4f31-afdb-d1043dcabbd7
task ID: R3-074
verdict: PASS
timestamp: 2026-11-26 20:59 +07 (Asia/Ho_Chi_Minh)
key file hash: docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8; docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both verified against the brief's frozen hashes before scoring)
reason: the initial-error screenshot shows the original NameError on line 8 exactly as the key describes; the snapshot's fixed script provably differs from the original by only the line-8 token (reverting {tong} to {tongue} on line 8 reproduces the key's original script sha256 f3b09ca0 exactly); the result files for run 1, run 2 and the final d40-ket-qua.txt are byte-identical to the key's expected file (sha256 f737a14b) with all 10 values correct; and my read-only re-run of the fixed script copy exited 0 with output identical to the snapshot run 1 file.

## Key section used

docs/rung3-answer-keys.md, "## R3-074 (Tier B)", lines 483-490: line 8 of the original script used the undefined variable `tongue` instead of `tong`, so the original run failed with NameError: name 'tongue' is not defined, exit 1. The fix renames `tongue` to `tong` at line 8 only, no variable renames, no main-logic change. The result file holds exactly 10 lines with values tong = 7, 9, 15, 11, 14, 24, 13, 18, 15, 13 in order; run 2 is identical to run 1. Original script sha256 f3b09ca0df66d3e4c4b8c88c78cffdb374d9ca6d988145587969034e4e3e7025; expected result file sha256 f737a14b0e450ed29e2b5842ca7a967a6c93cae20a500462dae027006a68d091. Grading evidence per the key: the result file plus the initial error screenshot; the grader may re-run the script read-only and compare the 10 lines.

## Snapshot verification

- Snapshot: rung3-run-log/rung3-snapshots/R3-074-L3/
- Manifest: the manifest.json file's own sha256 is 36e440e89a5ea97ed6930a9215a81534ac3eb28294395b6ea82e5bc70df38bb8, matching the dispatch notice. The manifest_sha256 field inside the file reads 1ee10926325f80f26094000190eaaca751225542afd9cb8932d422fba1a83950 (a hash of the file list). Per-file verification below was recomputed against this sealed manifest.json, so the verification chain is intact; both hashes are recorded here to keep the record unambiguous.
- Per-file sha256 verification against manifest.json (recomputed, hash and size): all 16 evidence files OK
  - 2026-11-26T20-33-02+07-00-initial-error.png c171ac18a979586d5649463b281ed86e9d8645e8d2e4b62c452f3620b7bacc0e OK
  - 2026-11-26T20-41-08+07-00-editor-faulty-line.png fc9f15d9336411bcd4a636d13afab299baa22739692700f21834fd76478795b5 OK
  - 2026-11-26T20-42-43+07-00-run1-terminal.png d96865502e8b3330afc313c362b476c2b54245bb1c78646a4f6032b3334e7b86 OK
  - 2026-11-26T20-44-02+07-00-run2-terminal.png e463e505176b256a913c71ecfd42aabb7b493135a4a42e364e5f558d102f2c27 OK
  - bao-cao.txt 72d6728a1abc4692d112fd0b959429fe324d98d9af3ac7f92fdd1c9a3780c840 OK
  - codex-R3-074.log 5a37cbb2e8a0c5bbaefee843584f982de7e5ed0a871346012d1fe01c01cc9e23 OK
  - d40-ket-qua.txt f737a14b0e450ed29e2b5842ca7a967a6c93cae20a500462dae027006a68d091 OK
  - d40-tinh-toan.py 01b2b00f3c57cb6960e2746015ab01705424e5c0bdcf8dced5857226e6cdac9c OK
  - desktop-after-pill-release.png a40baafad59ccc122dd5a6926e8bfe1419039db13c9b67b131d9b6acfdaaba9e OK
  - drive-log.txt 303557bce438dfbad00ea894f32d1aa9c48ae4cc27dcb0c503d0e07a61bc065a OK
  - end_time.txt 8def805c4e6c6ff63e6b89a542aed15f5b17a738e2af14c50e05a48008835e6e OK
  - ket-qua-run1.txt f737a14b0e450ed29e2b5842ca7a967a6c93cae20a500462dae027006a68d091 OK
  - ket-qua-run2.txt f737a14b0e450ed29e2b5842ca7a967a6c93cae20a500462dae027006a68d091 OK
  - pill-during-drive.png 7f8dfd84c57455c6a92e9397f3a95614e07700eb73ec15b327c8a493ead5f356 OK
  - r3-074-pill-gone-check.png c26a0eaebcfc25943e1da33d773c2692d60be24e3713f4cd550bb8c4e6eab28f OK
  - start_time.txt 024a36337794a765a61aa2297953cf1c84b2291429db4463e70065c52d431b15 OK
- No files in the snapshot dir beyond the manifest list plus manifest.json itself.
- Run window: start_time.txt 2026-11-26T20:29:44+07:00, end_time.txt 2026-11-26T20:49:44+07:00, inside the 30 minute task limit. All screenshot timestamps (20:33:02, 20:41:08, 20:42:43, 20:44:02) fall inside the window.

## Files read

- rung3-run-log/briefs/R3-074-scorer-clone2-brief.md
- docs/rung3-answer-keys.md (sha256 verification; key section lines 483-490 only)
- docs/rung3-answer-keys.json (sha256 verification only)
- rung3-run-log/rung3-snapshots/R3-074-L3/manifest.json
- rung3-run-log/rung3-snapshots/R3-074-L3/d40-tinh-toan.py
- rung3-run-log/rung3-snapshots/R3-074-L3/d40-ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-074-L3/ket-qua-run1.txt
- rung3-run-log/rung3-snapshots/R3-074-L3/ket-qua-run2.txt
- rung3-run-log/rung3-snapshots/R3-074-L3/2026-11-26T20-33-02+07-00-initial-error.png
- rung3-run-log/rung3-snapshots/R3-074-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-074-L3/end_time.txt

The remaining snapshot files (bao-cao.txt, codex-R3-074.log, drive-log.txt, the editor and run terminal screenshots, the pill and desktop screenshots) were hash-verified against the manifest but not read for grading: the key grades the result file and the initial error screenshot, and the brief's optional re-run was performed instead of relying on the run terminal screenshots.

## Independence declaration

I graded independently from the snapshot and key section only; I did not read scorer 2's verdict or contact the runner.

## Infrastructure re-run consideration

Considered, and recorded here as required from epoch 23: the verdict is not INVALID, so no infrastructure re-run path applies. The snapshot evidence was complete and judgeable (sealed manifest, fixed script, both run outputs, the final result file and the initial error screenshot all present and hash-verified), and no infrastructure failure appears anywhere in it. Separately, the brief's optional read-only re-run of the fixed script was performed as a grading check (see Reasons), which is a scorer verification step, not an infrastructure re-run of the task.

## Reasons

- Initial error (2026-11-26T20-33-02+07-00-initial-error.png): the terminal shows the run of python3 ~/rung3/d40-tinh-toan.py failing with a traceback at File "/home/james/rung3/d40-tinh-toan.py", line 8, in main, on the line ket_qua.append(f"dong {i+1}: tong = {tongue}"), ending in "NameError: name 'tongue' is not defined. Did you mean: 'tong'?". This is exactly the original error the key describes, at line 8, and the screenshot is present as the brief requires.
- Only the line-8 fix (hash proof): the snapshot's fixed script d40-tinh-toan.py (sha256 01b2b00f) has line 8 as ket_qua.append(f"dong {i+1}: tong = {tong}"). Reverting just that one token, {tong} back to {tongue}, on line 8 of a copy reproduces sha256 f3b09ca0df66d3e4c4b8c88c78cffdb374d9ca6d988145587969034e4e3e7025, exactly the key's original script hash. The fixed script therefore differs from the original by that single token and nothing else: no variable renames, no main-logic change.
- Result values: d40-ket-qua.txt holds exactly 10 lines, "dong 1: tong = 7" through "dong 10: tong = 13", with values 7, 9, 15, 11, 14, 24, 13, 18, 15, 13 in order, matching the key line by line. The sums also check out by hand against the script's lists a and b (3+4, 7+2, 12+3, 5+6, 9+5, 20+4, 4+9, 15+3, 8+7, 11+2).
- Run 2 identical to run 1: ket-qua-run1.txt, ket-qua-run2.txt and d40-ket-qua.txt are byte-identical (diff empty), and all three carry sha256 f737a14b0e450ed29e2b5842ca7a967a6c93cae20a500462dae027006a68d091, exactly the key's expected result file hash.
- Re-run check (permitted by the brief): I ran a copy of the fixed script read-only in a temp dir, with only its output path redirected to the temp dir because the script writes to an absolute laptop path; it exited 0 with no error and its output file is byte-identical to the snapshot's ket-qua-run1.txt. The script runs clean and deterministically produces the 10 expected lines.
- Rubric check: script runs with no error, result file has all 10 lines with correct values, run 2 identical to run 1, main logic unchanged (only the line-8 fix, hash-proven), initial-error screenshot present and showing the original NameError. Every PASS criterion is met, and the evidence was complete and judgeable, so the invalid case does not arise.
