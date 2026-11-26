# R3-078 scorer 1 grade (Pair B, R3-L3, Class L, Tier B)

scorer session ID: clone2-main-ad85548c-ced4-4f31-afdb-d1043dcabbd7
task ID: R3-078
verdict: PASS
timestamp: 2026-11-26 22:50 +07 (Asia/Ho_Chi_Minh)
key file hash: docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8; docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both verified against the brief's frozen hashes before scoring)
reason: the backup list holds exactly 10 rows (name, size, backup SHA-256) for d45-file-01.txt to d45-file-10.txt; the work and backup folder screenshots each show the same 10 files at 56 bytes in a flat structure; the report's checksum comparison records all 10 pairs matching with 0 mismatches; and for the 3 fixed-position files I independently recomputed SHA-256 of the quoted content line plus LF and reproduced the list checksums exactly at 56 bytes each, with the opened d45-file-10.txt screenshot corroborating its content firsthand.

## Key section used

docs/rung3-answer-keys.md, "## R3-078 (Tier B)", lines 508-514: work folder ~/rung3/d45-work with 10 files d45-file-01.txt to d45-file-10.txt; backup folder ~/rung3/d45-backup. Backup file count equals the original count (10), structure kept, checksums match for all files (0 wrong). The backup list has all rows (10 rows: file name, size, checksum). The 3 fixed-position files (1st, 5th, 10th by name order: d45-file-01.txt, d45-file-05.txt, d45-file-10.txt) have contents matching the originals. Grading evidence per the key: the backup list file plus the report; the scorer checks the file count and compares the checksums of the 3 fixed files.

## Snapshot verification

- Snapshot: rung3-run-log/rung3-snapshots/R3-078-L3/
- Manifest: the manifest.json file's own sha256 is 6f16a394817406fcd4377e0912bfd360e26c25ce9442e5ea75f9a1c26fdbc5bf, matching the dispatch notice. The manifest_sha256 field inside the file reads 712245195a3d6489fa63bc36e690c640623dbccd5b1d1503fe226e1b63e1d851 (a hash of the file list). Per-file verification below was recomputed against this sealed manifest.json, so the verification chain is intact; both hashes are recorded here to keep the record unambiguous.
- Per-file sha256 verification against manifest.json (recomputed, hash and size): all 12 evidence files OK
  - 20261126T222328+0700-d45-work-open.png 8e3f21690282ad9034add6606cc7e67c0dbbb058d679e3b50ffbf25e574e714d OK
  - 20261126T222506+0700-d45-backup-open.png 2408bb72eca8f4dcd3d6307c4779c969057dfef60fe7184cf2d8a713e2dd38e2 OK
  - 20261126T223137+0700-opened-backup-file.png 8a133e2471b57a2c8b75fb30a094541e690330977392df35f14a7db674b30b51 OK
  - bao-cao.txt 4ecdbb8e3051d2de3d5d9f40b95f26ae6cc1dbcfa08ea66c952260c8f903cec8 OK
  - codex-R3-078.log 0d05ebd69500faac1ad9ce16ad441e6e6ee3985cd165b12ce02fad626f908a86 OK
  - d45-backup-list.txt 9428cc68b0aa078289c28f7138c52a09004fbf707d3f16b4010fa4760429531f OK
  - desktop-after-release.png c00c910406e97f45d310b23091886dc52520396da1ba5e5476941ecbe8a582a5 OK
  - drive-log.txt 074f7a52052cfaa16b92be952d59ae569917ee5d52f7cf6fccad88dc214ceb7a OK
  - driver-pill-after.png dd18fbfa965b5cf005a47f822a3c4e0914464523fb8c22f88db1f1f16d913d51 OK
  - driver-pill-during.png 477b5830adc998bb7a1b160a508681a4154c8dceb9d64b280800f7e18dd2bb88 OK
  - end_time.txt 6d4564ba1652e2849e003b2c2d9211011f0872c37766f397e841d82c699ff0f7 OK
  - start_time.txt 12994535d00b53f93c00e7e150603d78803e98dadc0eba725d4a28729f99d603 OK
- No files in the snapshot dir beyond the manifest list plus manifest.json itself.
- Run window: start_time.txt 2026-11-26T22:20:46+07:00, end_time.txt 2026-11-26T22:38:47+07:00, inside the 30 minute task limit. All 3 screenshot timestamps (22:23:28, 22:25:06, 22:31:37) fall inside the window.

## Files read

- rung3-run-log/briefs/R3-078-scorer-clone2-brief.md
- docs/rung3-answer-keys.md (sha256 verification; key section lines 508-514 only)
- docs/rung3-answer-keys.json (sha256 verification only)
- rung3-run-log/rung3-snapshots/R3-078-L3/manifest.json
- rung3-run-log/rung3-snapshots/R3-078-L3/d45-backup-list.txt
- rung3-run-log/rung3-snapshots/R3-078-L3/bao-cao.txt (grading evidence for this task per the key)
- rung3-run-log/rung3-snapshots/R3-078-L3/20261126T222328+0700-d45-work-open.png
- rung3-run-log/rung3-snapshots/R3-078-L3/20261126T222506+0700-d45-backup-open.png
- rung3-run-log/rung3-snapshots/R3-078-L3/20261126T223137+0700-opened-backup-file.png
- rung3-run-log/rung3-snapshots/R3-078-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-078-L3/end_time.txt

The remaining snapshot files (codex-R3-078.log, drive-log.txt, driver-pill-during.png, driver-pill-after.png, desktop-after-release.png) were hash-verified against the manifest but not read for grading.

## Independence declaration

I graded independently from the snapshot and key section only; I did not read scorer 2's verdict or contact the runner.

## Infrastructure re-run consideration

Considered, and recorded here as required from epoch 23: the verdict is not INVALID, so no infrastructure re-run path applies. The snapshot evidence was complete and judgeable (sealed manifest, the backup list, the report and all 3 folder and file screenshots present and hash-verified), and no infrastructure failure appears anywhere in it.

## Reasons

- Backup list (d45-backup-list.txt, read directly): exactly 10 rows, sorted by name, d45-file-01.txt through d45-file-10.txt, each row carrying file name, size 56 and a SHA-256 checksum. The list has all 10 rows with all 3 required fields, as the key requires.
- Counts and structure (screenshots, firsthand): the d45-work screenshot (22:23:28) shows Nautilus at Home / rung3 / d45-work listing exactly the 10 files d45-file-01.txt to d45-file-10.txt, each 56 bytes, flat. The d45-backup screenshot (22:25:06) shows Nautilus at Home / rung3 / d45-backup listing the same 10 names, each 56 bytes, flat. Backup count 10 equals original count 10, names match, structure kept.
- Checksums, all files: the report (bao-cao.txt, grading evidence for this task per the key) records the checksum comparison as all 10 original/backup SHA-256 pairs matching with 0 mismatches, with a per-file MATCH line for each of the 10 files. The list file itself carries the backup checksums the comparison is stated against.
- The 3 fixed-position files (d45-file-01.txt, d45-file-05.txt, d45-file-10.txt): the report quotes the backup line and the original line for each, identical in all 3 cases ("Noi dung file lam viec so 01, dung de kiem tra sao luu.", and the so 05 and so 10 variants), each marked match yes. I verified this beyond the report's statement: SHA-256 of each quoted content line plus a trailing LF reproduces the backup list's checksum for that file exactly (file-01: 8e9a592136bedd1e951346cd5ea839478e456c86810ce569368ab592ff72e587; file-05: 46233fdf64b22726c55b66854b1381b1c1d93b4942f18ebb7f86234caa49b01e; file-10: 45426004afd4481991c2f1e7e5c51f46d1f854da870ff97865c72f4ef23d3c82), and each reconstruction is exactly 56 bytes, matching the list's size column. The list checksums therefore correspond to the very contents the report quotes for both the originals and the backups.
- Opened backup file (22:31:37 screenshot): the editor shows rung3/d45-backup/d45-file-10.txt containing the line ending "...i dung file lam viec so 10, dung de kiem tra sao luu.", the visible tail of the quoted file-10 content, corroborating that file's backup content firsthand.
- Rubric check: backup count 10 equals original count, structure kept, checksums match all files with 0 wrong, list has 10 rows, the 3 fixed-position files correct. Every PASS criterion is met, and the evidence was complete and judgeable, so the invalid case does not arise.
