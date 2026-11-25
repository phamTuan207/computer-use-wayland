# Scorer 1 grade, R3-L3, R3-006

- Session: 70cd99d1-ecef-4d02-9f42-714d7e86ab85 (scorer 1A, Pair A)
- Task: R3-006 (Tier B, position 6, run R3-L3)
- Verdict: PASS
- Scored at: 2026-11-25 21:47:37 +07 (Asia/Ho_Chi_Minh)
- Snapshot: rung3-run-log/rung3-snapshots/R3-006-L3/ at todolist-push commit 777b5b8a, manifest_sha256 04dd4e38308ac38377811370fb6ddb78e46e6fb6454f63e83a12b71899414e4a, all 4 evidence files hash-OK against manifest.json, manifest gate PASS
- Key file hashes (verified before scoring): docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both match the R3-L3 freeze)

## Files read

- rung3-run-log/rung3-snapshots/R3-006-L3/manifest.json (snapshot R3-006-L3, commit 777b5b8a)
- rung3-run-log/rung3-snapshots/R3-006-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-006-L3/20261125-213525-diff.png
- rung3-run-log/rung3-snapshots/R3-006-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-006-L3/end_time.txt
- docs/rung3-answer-keys.md, R3-006 section only (lines 165-171)
- docs/rung3-answer-keys.json, R3-006 entry only (allocated article)
- docs/rung3-list-100-tasks.md, section 6, R3-006 task text only

I scored from the snapshot, the key, and the live Wikipedia diff page, which the key explicitly requires the scorer to re-open ("Nguoi cham mo lai trang khac nhau giua 2 ban sua da ghi va doi chieu 3 thay doi, ten nguoi sua, thoi gian sua"). I did not read any other scorer's grade or verdict file, did not contact the runner, and did not read any runner log, ledger, or trial report. I did not edit Wikipedia and did not log in.

## Key (R3-006, Tier B)

English Wikipedia article "Albert Einstein", https://en.wikipedia.org/wiki/Albert_Einstein. 2 revisions chosen by the runner at run time from the article's history tab, recording the revision IDs and edit times of both. 3 content changes, each recording old and new, matching the diff page between those 2 revisions. The editors' names and edit times of both revisions must be correct per the history. 1 of the 3 changes must actually be present in the current article (checked by opening the newer revision). Evidence: diff page screenshot + ket-qua.txt.

## Evidence

- ket-qua.txt (5587B) records: Article URL https://en.wikipedia.org/wiki/Albert_Einstein; history reached via click; newer revision oldid 1383618653, edit time 18:53, 3 November 2026, editor Sainide; older revision oldid 1383609309, edit time 17:44, 3 November 2026, editor David Eppstein; Diff URL https://en.wikipedia.org/w/index.php?title=Albert_Einstein&diff=1383618653&oldid=1383609309; 3 changes with OLD and NEW text and the changed part noted; a verification line stating Change #1's inserted NEW text was found verbatim in the newer revision via DOM innerText search.
- The diff screenshot 20261125-213525-diff.png shows the Wikipedia "Albert Einstein: Difference between revisions" page with the 2 revisions (17:44, 3 November 2026 by David Eppstein; 18:53, 3 November 2026 by Sainide) and Change 1 visible in the Wikitext diff. The tab list shows the diff tab, the article tab, and a revision-history tab, confirming the runner opened the history.
- Live diff verification (browser, read-only, 21:46-21:47 +07, cloud browser): I re-opened the exact diff URL from ket-qua.txt. The live page confirms:
  - Older revision 1383609309: 17:44, 3 November 2026, editor David Eppstein. Newer revision 1383618653: 18:53, 3 November 2026, editor Sainide. Both match ket-qua.txt.
  - Change 1: YES. OLD "Einstein moved to Switzerland in 1895, forsaking his citizenship the following year." NEW "which he later renounced on 28 January 1896, just 6 weeks before he turned 17, avoiding conscription into military service."
  - Change 2: YES. OLD "where they settled in Palazzo Cornazzani." NEW "where his father Hermann and his uncle Jakob Einstein ran 'Einstein-Garrone National Electrotechnical Workshop'."
  - Change 3: YES. OLD "On the advice of the polytechnic's principal, he completed his secondary education." NEW "On the advice of the polytechnic's principal, Albin Herzog, he completed his secondary education."
  - The newer revision contains the Change 1 new text "renounced on 28 January 1896, just 6 weeks before he turned 17" (shown in the diff's newer column).
- All 3 changes have both old and new matching the diff. Editors' names and edit times are correct. 1 change (Change 1) is verified present in the newer revision, both by the runner's own DOM check recorded in ket-qua.txt and by my live diff read.
- Timing: start 2026-11-25T21:30:44+07:00, end 2026-11-25T21:36:10+07:00 (5 min 26 s). Fast for this task, but the evidence is independently verified correct against the live diff page, so timing alone is not a fail. No timing red flag changes the verdict.
- Note: I did not independently verify that the 2 revisions are consecutive in the article's history (the diff page does not show whether intermediate revisions exist). The key's Pass criteria do not score consecutiveness; they score the 3 changes matching the diff, correct editors/times, and 1 change verified in the newer revision, all of which are confirmed. There is no evidence the revisions are non-consecutive.

## Reason

All 3 changes are present in the diff with old and new matching, the editors' names and edit times are correct, and Change 1 is verified present in the newer revision, all confirmed by re-opening the live diff page as the key requires.

Signed: mochi, scorer 1A, session 70cd99d1-ecef-4d02-9f42-714d7e86ab85.
