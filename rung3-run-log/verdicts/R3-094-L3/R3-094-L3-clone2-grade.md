# R3-094 scorer 1 grade (Pair B, R3-L3, Class S, Tier B)

scorer session ID: clone2-main-ad85548c-ced4-4f31-afdb-d1043dcabbd7
task ID: R3-094
verdict: PASS
timestamp: 2026-11-27 02:19 +07 (Asia/Ho_Chi_Minh)
key file hash: docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8; docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both verified against the brief's frozen hashes before scoring)
reason: my own diff of the 3 saved result files shows run 1 with all 3 lines at the key's set values (TEN=An, TUOI=25, THANH_PHO=Ha Noi), run 2 differing from run 1 in exactly 1 line (TUOI 25 to 30), and run 3 byte-identical to run 1; the report's table and its 2 comparison statements match the saved files exactly.

## Key section used

docs/rung3-answer-keys.md, "## R3-094 (Tier B)", lines 582-588: script ~/rung3/nd14-in-bien.sh prints 3 variables R3_TEN, R3_TUOI, R3_THANH_PHO, one line per variable in the form "TEN=<value>". Values from the requirement file nd14-gia-tri.txt: R3_TEN=An, R3_TUOI=25, R3_THANH_PHO=Ha Noi. Run 1: TEN=An, TUOI=25, THANH_PHO=Ha Noi. Run 2: change 1 variable's value, only that variable's line changes. Run 3: restore the old value, result same as run 1. The 3 separate result files carry timestamps in ~/rung3-chung-cu/R3-094/: lan-1-YYYYMMDD-HHMMSS.txt, lan-2-YYYYMMDD-HHMMSS.txt, lan-3-YYYYMMDD-HHMMSS.txt. Grading evidence per the key: the 3 result files plus the report; the scorer compares the 3 runs. The task steps in docs/rung3-list-100-tasks.md (line 668) match this contract.

## Snapshot verification

- Snapshot: rung3-run-log/rung3-snapshots/R3-094-L3/
- Manifest: the manifest.json file's own sha256 is aa943235734f4caad56008da2d100b90d9a899720e9976d9d98dd32ab443a857, matching the dispatch notice. The manifest_sha256 field inside the file reads b7c9b94c1b5e5f050408e307a0d17d057424abfa19f300ae24701810513134f0 (a hash of the file list). Per-file verification below was recomputed against this sealed manifest.json, so the verification chain is intact; both hashes are recorded here to keep the record unambiguous.
- Per-file sha256 verification against manifest.json (recomputed, hash and size): all 9 evidence files OK
  - bao-cao.txt 11b785678c45ef51438893d390bd6bd2c80286a661d659a59712df846d75efcf OK
  - desktop-after.png 102aaba2ea61e256cf26f8dff9f1b45fc62712828d04a52b35c4322fb1af7d50 OK
  - drive-log.txt a6a559a9e5e7ff7e3e24ab827509fa035eb35bd38e1be97d9109cd216864e0f2 OK
  - end_time.txt 186c6c058256d4516b37d227916790f45d59a27d10af86a253cc40e0a6c90a15 OK
  - lan-1-20261127-021147.txt 2ee7a3375d6040f33da17356733a5d8f25018a439bc1196cb7bbf3a60279065d OK
  - lan-2-20261127-021220.txt e801562258173eb6eda5922f4f90ee239bacdaeddaa07f1bf5dafacca860631f OK
  - lan-3-20261127-021232.txt 2ee7a3375d6040f33da17356733a5d8f25018a439bc1196cb7bbf3a60279065d OK
  - report.txt 4442dfb4eff87fd807aeedb63327df297463944cb67ddd8e995aa50e627fc8fe OK
  - start_time.txt 90707e8302543da27c1147cee5d0eff6f1badb4f6c14f1c46fdabf0990e07aef OK
- No files in the snapshot dir beyond the manifest list plus manifest.json itself.
- Run window: start_time.txt 2026-11-27T02:09:32+07:00, end_time.txt 2026-11-27T02:16:44+07:00, inside the 30 minute task limit. The 3 result file timestamps (02:11:47, 02:12:20, 02:12:32) ascend and fall inside the window.

## Files read

- rung3-run-log/briefs/R3-094-scorer-clone2-brief.md
- docs/rung3-answer-keys.md (sha256 verification; key section lines 582-588 only)
- docs/rung3-answer-keys.json (sha256 verification only)
- docs/rung3-list-100-tasks.md (R3-094 task steps, line 668)
- rung3-run-log/rung3-snapshots/R3-094-L3/manifest.json
- rung3-run-log/rung3-snapshots/R3-094-L3/lan-1-20261127-021147.txt
- rung3-run-log/rung3-snapshots/R3-094-L3/lan-2-20261127-021220.txt
- rung3-run-log/rung3-snapshots/R3-094-L3/lan-3-20261127-021232.txt
- rung3-run-log/rung3-snapshots/R3-094-L3/report.txt
- rung3-run-log/rung3-snapshots/R3-094-L3/bao-cao.txt
- rung3-run-log/rung3-snapshots/R3-094-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-094-L3/end_time.txt

The remaining snapshot files (drive-log.txt, desktop-after.png) were hash-verified against the manifest but not read for grading; the key designates the 3 result files and the report as the grading evidence.

## Independence declaration

I graded independently from the snapshot and key section only; I did not read scorer 2's verdict or contact the runner.

## Infrastructure re-run consideration

Considered, and recorded here as required from epoch 23: the verdict is not INVALID, so no infrastructure re-run path applies. The snapshot evidence was complete and judgeable (sealed manifest, all 3 result files, the report and bao-cao.txt present and hash-verified), and the anomalies recorded in bao-cao.txt are driver and observation tooling issues that were recovered during the drive and do not touch the graded outputs.

## The 3 runs (read and compared by me)

- Run 1, lan-1-20261127-021147.txt:
  TEN=An
  TUOI=25
  THANH_PHO=Ha Noi
- Run 2, lan-2-20261127-021220.txt:
  TEN=An
  TUOI=30
  THANH_PHO=Ha Noi
- Run 3, lan-3-20261127-021232.txt:
  TEN=An
  TUOI=25
  THANH_PHO=Ha Noi
- My diff, run 1 vs run 2: exactly 1 line differs, line 2, TUOI=25 becomes TUOI=30. The TEN and THANH_PHO lines are unchanged.
- My diff, run 1 vs run 3: no differences (diff exit 0); the 2 files are byte-identical and share sha256 2ee7a3375d6040f33da17356733a5d8f25018a439bc1196cb7bbf3a60279065d in the sealed manifest.

## Reasons

- Run 1 correct: all 3 lines carry the key's set values from nd14-gia-tri.txt, TEN=An, TUOI=25, THANH_PHO=Ha Noi, in the script's "TEN=<value>" form, no line missing and no extra line.
- Run 2 changes exactly 1 line: only R3_TUOI moves 25 to 30; the other 2 lines are untouched, satisfying the "change 1 variable, only that line changes" requirement. The changed variable and its new value are the runner's choice, which the key leaves open.
- Run 3 equals run 1: byte-identical files, so the restored value reproduces run 1 exactly, as required.
- Report correct and consistent: report.txt tabulates the 3 variables across the 3 runs (R3_TEN An, An, An; R3_TUOI 25, 30, 25; R3_THANH_PHO Ha Noi in all runs), matching the saved result files cell for cell, and states the 2 comparisons (run 1 vs run 2 differ in exactly 1 line, R3_TUOI, confirmed yes; run 1 vs run 3 identical, confirmed yes). Both statements agree with my own diffs.
- File naming and timing: the 3 result files follow the required lan-N-YYYYMMDD-HHMMSS.txt pattern with ascending timestamps inside the run window.
- Process note: bao-cao.txt records 5 recovered anomalies (observe target selection, driver PTY, screen identifier, an early ls check, a screenshot crop), each with its full chain; none altered the terminal session's exported values or the saved outputs, and the final state they produced is exactly what the result files show.
- Rubric check: run 1 has all 3 lines with the correct set values, run 2 only 1 line changes, run 3 same as run 1, report correct, report matches the 3 saved result files. Every PASS criterion is met, and the evidence was complete and judgeable, so the invalid case does not arise.
