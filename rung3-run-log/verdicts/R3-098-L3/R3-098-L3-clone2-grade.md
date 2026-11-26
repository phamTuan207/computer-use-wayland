# R3-098 scorer 2 grade (Pair B, R3-L3, Class S, Tier B)

scorer session ID: clone2-main-ad85548c-ced4-4f31-afdb-d1043dcabbd7
task ID: R3-098
verdict: PASS
timestamp: 2026-11-27 02:52 +07 (Asia/Ho_Chi_Minh)
key file hash: docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8; docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both verified against the brief's frozen hashes before scoring)
reason: the graded report matches the key on all 9 values (NhomA 14 rows sum 66193, NhomB 12/52674, NhomC 13/69300, NhomD 11/51018, grand total 239185); the sealed awk-commands.txt records the correct awk for the CSV schema with 2 identical runs matching the report; and my arithmetic cross-checks pass (the 4 group sums add to 239185, the 4 group counts add to the key's 50 data rows).

## Key section used

docs/rung3-answer-keys.md, "## R3-098 (Tier B)", lines 598-603: file ~/rung3/nd18-du-lieu.csv, 50 data rows plus a header row, columns ten,nhom,so_tien, sha256 71dd42639dadbd62d458d2304e30f05e7ed227f8b55387f830eadd4262648eea. Per-group table: NhomA 14 rows sum 66193; NhomB 12 rows sum 52674; NhomC 13 rows sum 69300; NhomD 11 rows sum 51018. Grand total 239185, equal to the sum of the groups. Grading evidence per the key: the report nd18-bao-cao.txt; the scorer re-runs the awk read-only and compares. The task steps in docs/rung3-list-100-tasks.md (line 682) match this contract, including step 6: re-run the awk a second time and the results must match.

## Snapshot verification

- Snapshot: rung3-run-log/rung3-snapshots/R3-098-L3/
- Manifest: the manifest.json file's own sha256 is bd55300ce6e672ebd884cff87462f466ecc615dd75c53552e9187d999e69939e, matching the dispatch notice. The manifest_sha256 field inside the file reads 5d33c1ec4dd54f26802654ad6889de91b3507f358b53c5006ebb1ab51c0622b8 (a hash of the file list). Per-file verification below was recomputed against this sealed manifest.json, so the verification chain is intact; both hashes are recorded here to keep the record unambiguous.
- Per-file sha256 verification against manifest.json (recomputed, hash and size): all 8 evidence files OK
  - awk-commands.txt 5703d17289d9cd09e78a2651114922a41245b572cacf3962461d752954df67ca OK
  - bao-cao.txt 5ddb3c41b670316e80c4b0ae882a34f314499fc964c878fa07a81e0b2dc99eed OK
  - drive-log.txt a8d4cc3caa3ddb68dd5c49f49d3257467d06d6c3012fb2ea740102c25b6cfcc5 OK
  - end_time.txt 9b654aefe0a4bf755658fbb61a14e17dfd9fd48d13368fa1de7186acd5555425 OK
  - nd18-bao-cao.txt 5ddb3c41b670316e80c4b0ae882a34f314499fc964c878fa07a81e0b2dc99eed OK (byte-identical to bao-cao.txt, same sha256)
  - pill-off.png 4d5dc8ef27d30ffbd5e0a404df933ccda90e0d4034315a6b70fe75b72b0f48b3 OK
  - pill-on.png f3107c84b134b856446d324c5edf4f2c7a65de670e0cbfc4d35fc9421e8183e7 OK
  - start_time.txt 18d33761af98e283437f252b64c58b2ecf4bc1a9ebde63e0ae47f4b8a6b7fcca OK
- No files in the snapshot dir beyond the manifest list plus manifest.json itself.
- Run window: start_time.txt 2026-11-27T02:44:40+07:00, end_time.txt 2026-11-27T02:48:20+07:00 (3m 40s), inside the 30 minute task limit.

## Files read

- rung3-run-log/briefs/R3-098-scorer-brief.md
- docs/rung3-answer-keys.md (sha256 verification; key section lines 598-603 only)
- docs/rung3-answer-keys.json (sha256 verification only)
- docs/rung3-list-100-tasks.md (R3-098 task steps, line 682)
- rung3-run-log/rung3-snapshots/R3-098-L3/manifest.json
- rung3-run-log/rung3-snapshots/R3-098-L3/bao-cao.txt (the graded report, grading evidence for this task per the key; byte-identical to nd18-bao-cao.txt)
- rung3-run-log/rung3-snapshots/R3-098-L3/awk-commands.txt
- rung3-run-log/rung3-snapshots/R3-098-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-098-L3/end_time.txt

Per the brief's independence rule I did not read drive-log.txt (the drive report), scorer 1's verdict, or the ledger row. drive-log.txt and the 2 pill screenshots were hash-verified against the manifest only.

## Independence declaration

I graded independently from the snapshot and key section only; I did not read scorer 1's verdict, the ledger row, or the drive report, and I did not contact the runner.

## Infrastructure re-run consideration

Considered, and recorded here as required from epoch 23: the verdict is not INVALID, so no infrastructure re-run path applies. The graded evidence (the report) was present, sealed and fully judgeable against the key, and no infrastructure failure appears in the evidence I graded.

## The awk re-run: what I could and could not do

- The brief and the assignment ask the scorer to re-run the awk read-only on the CSV or a copy. No copy of nd18-du-lieu.csv was sealed into the snapshot, and a search of the worktree and of this machine's home directory found no copy, so a scorer-side re-run on the raw data was not possible. I record this openly rather than claim a re-run I did not perform.
- What I verified instead, from sealed evidence: (1) the graded report against the key, line by line, all 9 values; (2) awk-commands.txt, which records the 3 awk commands and both runs' outputs; the commands are the correct awk for the key's schema (comma separator, NR>1 to skip the header, group key $2, amount $3: sum[$2]+=$3, count[$2]++, total+=$3), and the first and second run outputs are identical to each other and to the report, satisfying the task's re-run check at run time; (3) my own arithmetic cross-checks: 66193 + 52674 + 69300 + 51018 = 239185, equal to the report's and the key's grand total, and 14 + 12 + 13 + 11 = 50, equal to the key's data row count for the CSV.

## Per-criterion results

- Per-group sums: PASS. Report: NhomA 66193, NhomB 52674, NhomC 69300, NhomD 51018. All 4 equal the key exactly.
- Per-group row counts: PASS. Report: NhomA 14, NhomB 12, NhomC 13, NhomD 11. All 4 equal the key exactly.
- Grand total: PASS. Report: 239185, equal to the key and to the sum of the 4 group sums (my computation).
- Report completeness: PASS. The report carries the per-group sum table, the per-group row count table and the grand total, the 3 elements the task requires.
- Second awk run matches (task step 6): PASS on the sealed record. awk-commands.txt shows the second run of all 3 commands producing outputs identical to the first run and to the report.
- Scorer-side awk re-run on the CSV: NOT PERFORMED, no CSV copy was sealed or available (see above). This limits one verification method; it does not make the evidence unjudgeable, because the key designates the report as the graded evidence and every value in it is checkable against the key and the sealed dual-run record.

## Reasons

- Every graded value in the report equals the frozen key: the 4 group sums, the 4 group counts and the grand total, 9 of 9, with no deviation.
- The recorded awk is correct for the stated schema and file shape (50 data rows plus header), and its 2 recorded runs agree with each other and with the report, so the result is stable, not a one-off transcription.
- The report's internal arithmetic is consistent (groups sum to the total; counts sum to the key's row count), which a fabricated or mis-transcribed table would be unlikely to preserve across all 3 tables.
- Rubric check against the brief's expected values: NhomA 14 rows sum 66193, NhomB 12/52674, NhomC 13/69300, NhomD 11/51018, total 239185, all present and exact in the graded evidence. The PASS criteria are met, and the evidence was complete and judgeable, so the invalid case does not arise.
