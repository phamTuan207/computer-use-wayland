# Scorer 1 grade, R3-L3, DP-06

- Session: 70cd99d1-ecef-4d02-9f42-714d7e86ab85 (scorer 1A, Pair A)
- Task: DP-06 (Tier B, position 12, medium backup replacing R3-011 INVALID, run R3-L3)
- Verdict: PASS
- Scored at: 2026-11-25 23:43:21 +07 (Asia/Ho_Chi_Minh)
- Snapshot: rung3-run-log/rung3-snapshots/DP-06-L3/ at todolist-push commit 93838247, manifest_sha256 3ef9dd40122ae09a1706a238b8bc3c99fc50dc1b22e251cac6f00ae9b333b404, all 6 evidence files hash-OK against manifest.json, manifest gate PASS
- Key file hashes (verified before scoring): docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both match the R3-L3 freeze)

## Files read

- rung3-run-log/rung3-snapshots/DP-06-L3/manifest.json (snapshot DP-06-L3, commit 93838247)
- rung3-run-log/rung3-snapshots/DP-06-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/DP-06-L3/20261125-233554-paris.png
- rung3-run-log/rung3-snapshots/DP-06-L3/20261125-233557-berlin.png
- rung3-run-log/rung3-snapshots/DP-06-L3/20261125-233559-rome.png
- rung3-run-log/rung3-snapshots/DP-06-L3/start_time.txt
- rung3-run-log/rung3-snapshots/DP-06-L3/end_time.txt
- docs/rung3-answer-keys.md, DP-06 key section (lines 667-675)
- docs/rung3-answer-keys.json, DP-06 entry only (cities Paris, Berlin, Rome)
- docs/rung3-list-100-tasks.md, section 8, DP-06 backup entry (line 732)

I scored from the snapshot and the key only. I did not read any other scorer's grade or verdict file, did not contact the runner, and did not read any runner log, ledger, or trial report. I did not re-open the live Wikipedia pages; the key states the population is live at run time and the truth is the infobox screenshot taken as soon as the figure appears, not the current value.

## Key (DP-06, Tier B, medium backup)

3 cities on en.wikipedia.org (in this order): 1. Paris 2. Berlin 3. Rome. Each city: record the city population (first line of the Population row in the infobox) and the date accompanying the figure. The population is live at run time (Wikipedia can change); the truth is the infobox screenshot taken as soon as the figure appears, not the current value. Verification values on 2026-11-24: Paris 2,047,602 (Jan 2026); Berlin 3,596,999 (2022 census, City/State line; do NOT take the Estimate December 2025 line: 3,700,577); Rome 2,745,062 (2026, Municipality line; do NOT take the Metropolitan city line: 4,224,901). Evidence: 3 infobox screenshots + ket-qua.txt; the scorer compares the population and date with the screenshots.

Task text Pass: all 3 lines, population matches the infobox screenshot of each city at run time, the accompanying date is correct, screenshots of all 3 pages. Fail: missing line, population does not match the screenshot, wrong date, took the wrong line (Urban, Metro, Metropolitan city, or Estimate), missing screenshots.

## Evidence

- ket-qua.txt (80B) records: "Paris, 2,047,602, Jan 2026", "Berlin, 3,596,999, 2022 census", "Rome, 2,745,062, 2026". All 3 lines present, in the required order (Paris, Berlin, Rome).
- Paris screenshot 20261125-233554-paris.png (Wikipedia Paris article, infobox visible) shows the Population row: first line "2,047,602" with date "(Jan 2026)". The Urban line (11,013,774) and Metro line (13,320,752) are separate lines below. ket-qua.txt matches the first line exactly, and the runner took the correct city-population line, not Urban or Metro.
- Berlin screenshot 20261125-233557-berlin.png (Wikipedia Berlin article, infobox visible) shows the Population row: first line "City/State 3,596,999" with date "(2022 census)". The Estimate line (December 2025) shows 3,700,577. ket-qua.txt matches the City/State line exactly, and the runner took the correct line, not the Estimate line the key warns about.
- Rome screenshot 20261125-233559-rome.png (Wikipedia Rome article, infobox visible) shows the Population row: first line "Municipality 2,745,062" with date "(2026)". The Metropolitan city line shows 4,224,901. ket-qua.txt matches the Municipality line exactly, and the runner took the correct line, not the Metropolitan city line the key warns about.
- All 3 screenshots show the Wikipedia infobox for the correct city, with the population figures matching ket-qua.txt exactly and the accompanying dates correct.

## Reason

All 3 lines are present in ket-qua.txt, each population matches the infobox screenshot of its city at run time, each accompanying date is correct, and the runner took the correct first line for each city (Paris city population, Berlin City/State, Rome Municipality), avoiding the Urban, Metro, Estimate, and Metropolitan city traps the key names. Screenshots of all 3 pages are present.

Timing note: start 2026-11-25T23:35:50+07:00, end 2026-11-25T23:36:00+07:00 (10 s); the 3 screenshots are timestamped 23:35:54, 23:35:57, 23:35:59. Fast, but every figure was independently verified against its infobox screenshot, so timing alone is not a fail.

Signed: mochi, scorer 1A, session 70cd99d1-ecef-4d02-9f42-714d7e86ab85.
