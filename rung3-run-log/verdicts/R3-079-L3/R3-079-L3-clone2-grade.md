# R3-079 scorer 2 grade (Pair B, R3-L3, Class L, Tier B)

scorer session ID: clone2-main-ad85548c-ced4-4f31-afdb-d1043dcabbd7
task ID: R3-079
verdict: PASS
timestamp: 2026-11-26 23:19 +07 (Asia/Ho_Chi_Minh)
key file hash: docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8; docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both verified against the brief's frozen hashes before scoring)
reason: the sealed restored file contains exactly "Bao cao tuan 47, doanh thu 12500000, don hang 320.", matching the manifest's 2026-11-22 line, which I read firsthand in the manifest screenshot; the restored file's SHA-256 (407851fc...) equals the report's recorded hash of the 2026-11-22 backup source and differs from the 2026-11-20 backup's hash, proving the restore came from the correct dated backup; the report and ket-qua.txt carry the file name, the date 2026-11-22 and the comparison result match; and the report's before and after hashes show no existing file was overwritten.

## Key section used

docs/rung3-answer-keys.md, "## R3-079 (Tier B)", lines 516-522: backup folder ~/rung3/d46-backup with 2 dated backups, 2026-11-20 and 2026-11-22, each containing bao-cao-tuan.txt. The request file d46-yeu-cau.txt asks to restore bao-cao-tuan.txt from the 2026-11-22 backup into ~/rung3/d46-restored. Correct content: week 47, revenue 12500000, orders 320 (not week 46: revenue 9800000, orders 275). The current file in the work folder must not be overwritten. The report contains the file name, the backup date (2026-11-22), and the comparison result against manifest.txt. Grading evidence per the key: the restored file plus the report; the scorer opens the restored file and compares it with the manifest.

## Snapshot verification

- Snapshot: rung3-run-log/rung3-snapshots/R3-079-L3/
- Manifest: the manifest.json file's own sha256 is d0bedcee2e76bc75321c6f76daf4ce05adaab61f0557c30b3bc868ac693e8420, matching the dispatch notice. The manifest_sha256 field inside the file reads cbf937c3ab1405e075f775a1cc374745fdd8603393e7e755ec92fe2252c3aa00 (a hash of the file list). Per-file verification below was recomputed against this sealed manifest.json, so the verification chain is intact; both hashes are recorded here to keep the record unambiguous.
- Per-file sha256 verification against manifest.json (recomputed, hash and size): all 13 evidence files OK
  - 20261126T230228+0700-d46-backup-open.png 654eace7b7d934cabad6a80bd47e4c704b902b62b6e5657f5953069985f9aeb8 OK
  - 20261126T230610+0700-restored-file-open.png ba388e17f42e2593157e3fc4b22250fb993e90d40a57aa0a925819f507d0c23b OK
  - 20261126T230727+0700-manifest-open.png 9f04380dcf0ac5dcdcda1ae4198ff890e15bcfd140ddbcf48c333d79c21d23a4 OK
  - bao-cao-tuan.txt 407851fceb795390b95868f95df15b31cbac5e8ce0044bd3f56e0949b1e17359 OK
  - bao-cao.txt d8ee15f42b06d13ae9444494c698ae31da2b5363aefb9ac160e90d182e9bbf7f OK
  - codex-R3-079.log 24529d65940c9be28dd57a2d27d6bf70c0e69c23f7f842412b38c8626a05446f OK
  - desktop-after-release.png 5e9200efb6d85af801e311438826facf1df8154a876f83a98b0c292a7b8b90ab OK
  - drive-log.txt 19ae4d36ce481af23b2337ab6af653bc0ebf786bb682ae1a76c999bc0701d455 OK
  - driver-pill-after.png 67fd7a1c61d33b2e0c35e07286052ff90cad074b8db7cc52dbd5af5dbec52c33 OK
  - driver-pill-during.png 23ca596e631fd2d253aaf06360a250083bce43fd71d259a41770b8c8bbb48c7e OK
  - end_time.txt c014650a14eb4008429dc4445526958c3e7354db713b0892446e56bba6b1119c OK
  - ket-qua.txt 9b9a6f67b2b7fcd48f5d509894c1295103fe139a23ba91a156c459747874c566 OK
  - start_time.txt c7903a6fba8c9df5c6a6edfd3fff5f04bd0d45bfc2511f029fd55c40bdddecd2 OK
- No files in the snapshot dir beyond the manifest list plus manifest.json itself.
- Run window: start_time.txt 2026-11-26T22:59:41+07:00, end_time.txt 2026-11-26T23:11:55+07:00 (12m 14s), inside the 30 minute task limit. All 3 screenshot timestamps (23:02:28, 23:06:10, 23:07:27) fall inside the window.

## Files read

- rung3-run-log/briefs/R3-079-scorer-clone2-brief.md
- docs/rung3-answer-keys.md (sha256 verification; key section lines 516-522 only)
- docs/rung3-answer-keys.json (sha256 verification only)
- rung3-run-log/rung3-snapshots/R3-079-L3/manifest.json
- rung3-run-log/rung3-snapshots/R3-079-L3/bao-cao-tuan.txt (the restored file)
- rung3-run-log/rung3-snapshots/R3-079-L3/bao-cao.txt (the report, grading evidence for this task per the key)
- rung3-run-log/rung3-snapshots/R3-079-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-079-L3/20261126T230228+0700-d46-backup-open.png
- rung3-run-log/rung3-snapshots/R3-079-L3/20261126T230610+0700-restored-file-open.png
- rung3-run-log/rung3-snapshots/R3-079-L3/20261126T230727+0700-manifest-open.png
- rung3-run-log/rung3-snapshots/R3-079-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-079-L3/end_time.txt

The remaining snapshot files (codex-R3-079.log, drive-log.txt, driver-pill-during.png, driver-pill-after.png, desktop-after-release.png) were hash-verified against the manifest but not read for grading.

## Independence declaration

I graded independently from the snapshot and key section only; I did not read scorer 1's verdict or contact the runner.

## Infrastructure re-run consideration

Considered, and recorded here as required from epoch 23: the verdict is not INVALID, so no infrastructure re-run path applies. The snapshot evidence was complete and judgeable (sealed manifest, the restored file, the report, ket-qua.txt and all 3 folder and file screenshots present and hash-verified), and no infrastructure failure bears on the graded end state.

## Reasons

- Correct backup chosen, proven at byte level: the sealed restored file bao-cao-tuan.txt has SHA-256 407851fceb795390b95868f95df15b31cbac5e8ce0044bd3f56e0949b1e17359 (recomputed by me against the snapshot manifest). The report records that same hash for the source file /home/james/rung3/d46-backup/2026-11-22/bao-cao-tuan.txt, and a different hash (3dcf8de4d8a347b40f691abe0b3a1afbfe7da38d46dfd2702ccad04d8d5ace03) for the 2026-11-20 backup. The restored file is therefore byte-identical to the 2026-11-22 backup and distinct from the 2026-11-20 backup.
- Content matches the manifest (the scorer's designated comparison, done firsthand): the restored file reads exactly "Bao cao tuan 47, doanh thu 12500000, don hang 320." The manifest screenshot (23:07:27) shows rung3/d46-backup/manifest.txt line 1: "Ban sao luu ngay 2026-11-22 chua file bao-cao-tuan.txt voi noi dung: Bao cao tuan 47, doanh thu 12500000, don hang 320.", and line 2 the 2026-11-20 entry with week 46, 9800000, 275. The restored content equals the manifest's 2026-11-22 content, week 47, revenue 12500000, orders 320, as the key requires.
- Location corroborated: the restored-file screenshot (23:06:10) shows the editor open on rung3/d46-restored/bao-cao-tuan.txt displaying the week 47 line, so the file sits in the requested destination folder with the right content.
- Backup structure as described: the backup-folder screenshot (23:02:28) shows Nautilus at Home / rung3 / d46-backup with the 2026-11-20 folder (1 item), the 2026-11-22 folder (1 item) and manifest.txt, matching the key's setup.
- Report correct: bao-cao.txt names the file (bao-cao-tuan.txt), the backup date 2026-11-22 (copy source /home/james/rung3/d46-backup/2026-11-22/bao-cao-tuan.txt, destination /home/james/rung3/d46-restored/bao-cao-tuan.txt), quotes the manifest line and states "Comparison: match." ket-qua.txt carries the same 3 elements: file name, backup date used 2026-11-22, manifest comparison result match.
- Current file not overwritten: the report's before and after SHA-256 sets are identical for every listed pre-existing file (both dated backups, manifest.txt, the request file d46-yeu-cau.txt and the d45-work set), it records that d46-restored was empty before the copy, and that after the copy the restored file exists only in d46-restored. Nothing in the snapshot contradicts this, and the source backups' hashes in the report match the values the restored-file hash chain relies on.
- Rubric check: restored from the correct dated backup (2026-11-22), content matches the manifest (week 47, 12500000, 320), current work-folder file not overwritten, report correct (file name, date 2026-11-22, comparison result). Every PASS criterion is met, and the evidence was complete and judgeable, so the invalid case does not arise.
