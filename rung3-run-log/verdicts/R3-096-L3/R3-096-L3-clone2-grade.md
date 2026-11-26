# R3-096 scorer 1 grade (Pair B, R3-L3, Class L, Tier B)

scorer session ID: clone2-main-ad85548c-ced4-4f31-afdb-d1043dcabbd7
task ID: R3-096
verdict: PASS
timestamp: 2026-11-27 02:38 +07 (Asia/Ho_Chi_Minh)
key file hash: docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8; docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both verified against the brief's frozen hashes before scoring)
reason: the report lists the 4 initial differing lines with the key's old and new values, the merged line cong=9090 and the remaining count 3; the sealed post-merge old file shows cong=9090 with che_do, ngon_ngu and bo_nho still at their old values; and my own read-only diff re-runs give 4 differing lines before the merge and exactly 3 after it.

Note on the brief file: the assignment named rung3-run-log/briefs/R3-096-clone2-scorer-brief.md, which does not exist on todolist-push. The brief actually issued for this seat is rung3-run-log/briefs/R3-096-scorer-clone2-brief.md, and I scored under it. The gap is recorded here for the coordinator.

## Key section used

docs/rung3-answer-keys.md, "## R3-096 (Tier B)", lines 590-596: 2 files ~/rung3/nd16-cu.conf and ~/rung3/nd16-moi.conf. Initially exactly 4 differing lines: cong 8080 to 9090; che_do dem to ngay; ngon_ngu vi to en; bo_nho 512 to 1024. The requirement file nd16-yeu-cau.txt specifies merging cong (9090), only this 1 line, keeping the other 3 differing lines at their old values. After merging, diff has only 3 differing lines; the merged line has the new value (9090), the other 3 differing lines still keep the old values. The report has the 4 initial differing lines, the merged line, and the remaining differing-line count (3). Grading evidence per the key: the report plus the old file after merging; the scorer re-runs diff read-only and compares. The task steps in docs/rung3-list-100-tasks.md (line 675) match this contract.

## Snapshot verification

- Snapshot: rung3-run-log/rung3-snapshots/R3-096-L3/
- Manifest: the manifest.json file's own sha256 is 7b23611fedb8bebfbb6eebd613042c3f11e24475cddb6c7c58b5b75de43a4716, matching the dispatch notice. The manifest_sha256 field inside the file reads 2b0b6562f15fce612a5c81d5323b5a18721e7cf8413717632051289b79b025de (a hash of the file list). Per-file verification below was recomputed against this sealed manifest.json, so the verification chain is intact; both hashes are recorded here to keep the record unambiguous.
- Per-file sha256 verification against manifest.json (recomputed, hash and size): all 8 evidence files OK
  - bao-cao.txt 08555f71b3539b7e82d1f9e4735e119b4f6731ba5bf1b336a250a0838dfa41a3 OK
  - drive-log.txt 7dcb352af15c1bdaab1fa5e1797af488839dbc0c3903e84ddc28355ec6480912 OK
  - end_time.txt 5734547b26d9583aef404951afdf6311ff8da4bc9375f3d3aa90524beba94cfa OK
  - nd16-bao-cao.txt f721903dfe2ebfdd3aff8d03d45fb62c207be6251998f785626132370ef6ad2a OK
  - nd16-cu.conf b2554c0e7e39330d2013a64e85ba2d44c117d6659fe1307a8cd029cfbe6ee212 OK
  - pill-off.png b6cb841728aa4b2a72238da973c0f6d6a3a1c3e618981a9621eb0ec3d7dfdc67 OK
  - pill-on.png 102dbffc99458bfeb032edee445d86f6e67259802f9982031c97450091a44120 OK
  - start_time.txt 535f9db9c9e52f7847e349e058500006cd841c8ab7e26ef8e597ccd4659a9798 OK
- No files in the snapshot dir beyond the manifest list plus manifest.json itself.
- Run window: start_time.txt 2026-11-27T02:26:58+07:00, end_time.txt 2026-11-27T02:31:32+07:00 (4m 34s), inside the 30 minute task limit.

## Files read

- rung3-run-log/briefs/R3-096-scorer-clone2-brief.md
- docs/rung3-answer-keys.md (sha256 verification; key section lines 590-596 only)
- docs/rung3-answer-keys.json (sha256 verification only)
- docs/rung3-list-100-tasks.md (R3-096 task steps, line 675)
- rung3-run-log/rung3-snapshots/R3-096-L3/manifest.json
- rung3-run-log/rung3-snapshots/R3-096-L3/nd16-bao-cao.txt (the graded report, grading evidence for this task per the key)
- rung3-run-log/rung3-snapshots/R3-096-L3/nd16-cu.conf (the old file after merging, grading evidence per the key)
- rung3-run-log/rung3-snapshots/R3-096-L3/bao-cao.txt (carries the run's 2 full diff -u outputs, used to reconstruct the new file and the pre-merge old file for my own diff re-runs)
- rung3-run-log/rung3-snapshots/R3-096-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-096-L3/end_time.txt

The remaining snapshot files (drive-log.txt, pill-on.png, pill-off.png) were hash-verified against the manifest but not read for grading.

## Independence declaration

I graded independently from the snapshot and key section only; I did not read scorer 2's verdict or contact the runner.

## Infrastructure re-run consideration

Considered, and recorded here as required from epoch 23: the verdict is not INVALID, so no infrastructure re-run path applies. The snapshot evidence was complete and judgeable (sealed manifest, the graded report, the sealed post-merge old file and both recorded diff outputs present and hash-verified). The one anomaly in bao-cao.txt (a PID-keyed overlay release) is a session-cleanup matter after the graded work and does not touch the graded files.

## My own diff re-runs (read-only, per the brief)

The snapshot seals the post-merge old file but no separate copy of nd16-moi.conf. I reconstructed both comparison files from the run's first diff -u output recorded in bao-cao.txt (its minus lines give the pre-merge old file, its plus lines the new file; the common context lines and the sealed file's tail give the shared lines), then ran diff myself:

- Pre-merge old file vs new file: 4 differing lines, exactly cong (8080 vs 9090), che_do (dem vs ngay), ngon_ngu (vi vs en), bo_nho (512 vs 1024). The initial count is 4, matching the key and the report.
- Sealed post-merge old file (the snapshot's nd16-cu.conf, used as-is) vs new file: 3 differing lines, exactly che_do (dem vs ngay), ngon_ngu (vi vs en), bo_nho (512 vs 1024). The cong line no longer differs. The remaining count is 3, matching the key and the report.
- The sealed post-merge old file itself reads: cong=9090, che_do=dem, ngon_ngu=vi, bo_nho=512, then the common lines ghi_log=bat, thoi_gian_cho=30, may_chu=localhost, phien_ban=1.0. The merged line carries the new value 9090; the other 3 differing lines keep their old values; exactly 1 line was merged.

## Reasons

- Initial state correct: the report's 4 initial differing lines carry the key's exact key names and old to new values (cong 8080 to 9090, che_do dem to ngay, ngon_ngu vi to en, bo_nho 512 to 1024), and my reconstructed diff reproduces the count of 4.
- The right line merged, and only that line: the drive report records the merge as a single sed substitution on the cong line (s/^cong=8080$/cong=9090/), the requirement file's designated line; the merged line in both reports is cong=9090, the correct new value.
- The other 3 differing lines unchanged: the sealed post-merge old file still shows che_do=dem, ngon_ngu=vi, bo_nho=512, and my post-merge diff shows those 3 lines as the only remaining differences, so nothing beyond the cong line was merged.
- Report correct: nd16-bao-cao.txt contains all 3 required elements, the 4 initial differing lines, the merged line (cong=9090), and the remaining differing-line count 3 with the 3 keys named (che_do, ngon_ngu, bo_nho). Every value agrees with the key and with my own diff re-runs.
- Rubric check: initially exactly 4 differing lines, after merging only 3 differing lines remain, the merged line has the correct new value, the other 3 differing lines unchanged, report correct. Every PASS criterion is met, and the evidence was complete and judgeable, so the invalid case does not arise.
