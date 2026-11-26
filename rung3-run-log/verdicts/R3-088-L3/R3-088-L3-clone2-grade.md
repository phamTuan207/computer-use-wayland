# R3-088 scorer 1 grade (Pair B, R3-L3, Class L, Tier B)

scorer session ID: clone2-main-ad85548c-ced4-4f31-afdb-d1043dcabbd7
task ID: R3-088
verdict: PASS
timestamp: 2026-11-27 01:30 +07 (Asia/Ho_Chi_Minh)
key file hash: docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8; docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both verified against the brief's frozen hashes before scoring)
reason: I listed and extracted the sealed archive copy myself: it is a genuine gzip tar with 11 entries (the root directory nd28-work/ plus 10 files), 10 file entries equal to the source count, and 10 files after my own extraction; the 3 fixed-position files carry their correct numbered contents; and the report's numbers (source 10, entries 11, files in archive 10, files after extraction 10, 3 comparisons MATCH) agree with my counts exactly.

## Key section used

docs/rung3-answer-keys.md, "## R3-088 (Tier B)", lines 556-563: directory ~/rung3/nd28-work with 10 files nd28-file-01.txt to nd28-file-10.txt; archive ~/rung3/nd28-luu-tru.tar.gz; extraction check directory ~/rung3/nd28-check. Entries in the archive are 11 (root directory + 10 files); files in the archive (not counting the directory entry ending with /) equal the source file count (10); files after extraction equal the source file count (10). The 3 compared files at fixed positions 1st, 5th, 10th in sorted name order (nd28-file-01.txt, nd28-file-05.txt, nd28-file-10.txt) have correct content. Report ~/rung3/nd28-bao-cao.txt holds the source file count, entries in archive (11), files in archive (10), files after extraction, and the 3-file comparison results. Grading evidence per the key: the tar.gz file plus the report; the scorer lists the files in the archive and counts them. The key's amendment note (R3-L2, 2026-11-24) records that tar -tzf counts 11 entries including the root directory, trial-run and independently verified, and the key was set to 11 entries, 10 files. The task steps in docs/rung3-list-100-tasks.md (line 645) match this contract.

## Snapshot verification

- Snapshot: rung3-run-log/rung3-snapshots/R3-088-L3/
- Manifest: the manifest.json file's own sha256 is 2d0ceca8d022752248f04b2888c3b265e906cdcf6d7a05367b49889a60f478b7, matching the dispatch notice. The manifest_sha256 field inside the file reads 3e6392f16a5969663e542eb9713ef7cabb2fe6b7cbbed0de9bb1f6f2ce54aecf (a hash of the file list). Per-file verification below was recomputed against this sealed manifest.json, so the verification chain is intact; both hashes are recorded here to keep the record unambiguous.
- Per-file sha256 verification against manifest.json (recomputed, hash and size): all 11 evidence files OK
  - bao-cao.txt ef6d3986142746c3500e8df5b5b644140b7723a48024e2ea82a75dff290a7161 OK
  - drive-log.txt 933d63dbef1fc299bef396f0ac19ddae27e1e964c0581fbe9c6176ec9398fdfc OK
  - end_time.txt c069b13ea6f5687f924fee6e700058c3a6750f279fd1eba36c2f4ae276358179 OK
  - nd28-bao-cao.txt 0160af4b5e05bca7d6c82468ba84dca160d62286fac1470e99836a129a75a503 OK
  - nd28-luu-tru.tar.gz 491ef848433497226787a3fa2d18053e4e2e19951b8379a7faa9bf5681532db6 OK
  - shot-00-pill.png 5ca59e357850f2e99977bcc54a7f63db6dbd6fa9343d3628f06a80f04844f189 OK
  - shot-01-terminal.png d1652944823349012dfa4054cd2be2451ace2281ab0c4cf85cd36b61cd08e6cc OK
  - shot-02-tar.png 177357efa094d1ea0f409ab0e202ff4695d5b850867e9c00d3eb3ccde1f35730 OK
  - shot-03-result.png d07010e5b6186f33370bb5e9c737694bb901e4c3348142f63f9b01335dc6cf25 OK
  - shot-04-after-release.png 39b6b95c15f1938e42490354d3442199401cc2d1063aa8e05512d419b35a9a21 OK
  - start_time.txt 78969e2389bd66785ed3586aa1f4d4848575c2c1536949aa10e2684e22ad18c0 OK
- No files in the snapshot dir beyond the manifest list plus manifest.json itself.
- Run window: start_time.txt 2026-11-27T01:10:32+07:00, end_time.txt 2026-11-27T01:25:36+07:00 (15m 04s), inside the 30 minute task limit.

## Files read

- rung3-run-log/briefs/R3-088-scorer-clone2-brief.md
- docs/rung3-answer-keys.md (sha256 verification; key section lines 556-563 only)
- docs/rung3-answer-keys.json (sha256 verification only)
- docs/rung3-list-100-tasks.md (R3-088 task steps, line 645)
- rung3-run-log/rung3-snapshots/R3-088-L3/manifest.json
- rung3-run-log/rung3-snapshots/R3-088-L3/nd28-bao-cao.txt (the report, grading evidence for this task per the key)
- rung3-run-log/rung3-snapshots/R3-088-L3/nd28-luu-tru.tar.gz (listed with tar -tzf and extracted to a temp directory by me; grading evidence per the key)
- rung3-run-log/rung3-snapshots/R3-088-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-088-L3/end_time.txt

The remaining snapshot files (bao-cao.txt drive report, drive-log.txt, shot-00-pill.png, shot-01-terminal.png, shot-02-tar.png, shot-03-result.png, shot-04-after-release.png) were hash-verified against the manifest but not read for grading; the key designates the tar.gz and the report as the grading evidence, and both were examined directly.

## Independence declaration

I graded independently from the snapshot and key section only; I did not read scorer 2's verdict or contact the runner.

## Infrastructure re-run consideration

Considered, and recorded here as required from epoch 23: the verdict is not INVALID, so no infrastructure re-run path applies. The snapshot evidence was complete and judgeable (sealed manifest, the archive copy and the report present and hash-verified, and the archive readable and extractable by me), and no infrastructure failure appears anywhere in it.

## Counted values (my own count from the sealed archive copy)

- Format check: file(1) identifies nd28-luu-tru.tar.gz as gzip compressed data; tar -tzf lists it cleanly. The archive is a real tar.gz, not another compression format.
- Entries in archive (tar -tzf): 11 total = 1 directory entry (nd28-work/) + 10 file entries (nd28-work/nd28-file-01.txt through nd28-work/nd28-file-10.txt).
- Files in archive (entries not ending with /): 10, equal to the source file count 10.
- Files after extraction: I extracted the archive to a temp directory myself; it yields exactly 10 regular files under nd28-work/, the same 10 names.
- The 3 fixed-position files, contents read from my extraction:
  - nd28-file-01.txt: "Noi dung file nen so 01, dung de kiem tra tar." (sha256 ad055706cd712e55b9f00bd7140d84cd941d25ea6b7485919715b0eca2a2c04b)
  - nd28-file-05.txt: "Noi dung file nen so 05, dung de kiem tra tar." (sha256 d37396ed103bb25a4dc12567bbfd4f16cba96baa757f2f17601bc472e8fb30fc)
  - nd28-file-10.txt: "Noi dung file nen so 10, dung de kiem tra tar." (sha256 3d37491d04d1d25567ec25e5978fad16af3cc029383cbe96c6b298b15b68a356)
  Each file's single line names its own number, the correct content for its position; these are the source contents as archived, and the report's cmp -s comparisons against the live sources record MATCH for all 3.

## Reasons

- Every count the key fixes is reproduced by my own listing and extraction of the sealed archive: entries 11 including the root directory, files in archive 10, files after extraction 10, source count 10. No file is missing from the archive and no extra file is present.
- Report numbers correct: nd28-bao-cao.txt states source regular files 10 (by find -maxdepth 1 -type f), source total size 470 bytes, the archive command (tar -czf ~/rung3/nd28-luu-tru.tar.gz -C ~/rung3 nd28-work), entries including root directory 11, regular files in archive 10, regular files after extraction 10, and the 3 comparisons (nd28-file-01.txt, nd28-file-05.txt, nd28-file-10.txt) all MATCH. Each figure agrees with my independent counts. The report also discloses that ls is aliased to eza with headers (an ls count of 11 including a header line) and that find was used for the true count of 10, which is consistent and honest reporting, not a wrong number.
- The tar.gz file exists in the snapshot as a sealed, hash-verified copy and is a valid gzip tar, satisfying the format criterion; no other compression format was used.
- Rubric check: entries in archive 11 including the root directory, files in archive equal to the source count 10, files after extraction equal to the source count, the 3 compared files correct content, report numbers correct, tar.gz file exists. Every PASS criterion is met, and the evidence was complete and judgeable, so the invalid case does not arise.
