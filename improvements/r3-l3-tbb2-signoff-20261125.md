# Independent Verification Sign-off: TB-B2 Calibration (Gate G-33)

Run code: R3-L3, branch todolist-push.
Verified: 2026-11-25 Asia/Ho_Chi_Minh. Committed 2026-11-25 09:20:08 +07 in b061f87c (R3-L3 Phase 0 prepare complete).
Verifier: independent verifier for the R3-L3 run. Verifier session id: not recorded in the prepare phase (the verifier was an independent subagent; it did not author the TB-B2 calibration file, did not run any rung 3 task, and did not run the preflight trial, as stated below). This file is identified by its commit b061f87c. I did NOT author the TB-B2 calibration file
(`~/workspace/r3-l3-calibration-TBB2.md`), did NOT run any rung 3 task, and did NOT run the
preflight trial. I re-graded all four calibration cases from scratch, from the snapshots plus
the frozen key only. I did not trust the calibration file's numbers: every measurement below
was computed by me directly (Python JSON parser, PIL pixel analysis, direct reading of both
screenshots, direct listing of snapshot contents).

## Frozen key verification (mine, independent)

Command: `sha256sum` on `/home/hatch/workspace/r3l3-run-wt/docs/rung3-answer-keys.json`
Result: `5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8`
Expected: `5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8`
Match: YES, exact match.

Key source used for grading: `docs/rung3-answer-keys.md` sections R3-041, R3-002, R3-003, R3-067
plus the Tier C rubric, and `docs/rung3-answer-keys.json` `tasks.R3-002`.

Manifest checks (mine): `sha256sum -c` passes OK for all three snapshot manifests
(R3-041-s1: 3 files OK; R3-002-s1: ket-qua.txt OK; R3-003-s1: runner-report.txt OK).

## Case-by-case re-grading

### 1. R3-041: PASS (agrees with TB-B2)

Key (Tier B): 8 items from browserleaks.com/javascript (first 7) and browserleaks.com/fonts
(font count); record window size after dragging the right edge inward 200 pixels
(innerWidth x innerHeight and outerWidth x outerHeight); screen size does not change;
evidence is a screenshot of the check page plus ket-qua.txt.

My checks:
- I read both screenshots directly. Screenshot 1 (10:21:03) and screenshot 2, the re-open
  verify (10:21:33), both show: userAgent `Mozilla/5.0 (X11; Linux x86_64)
  AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36`; language en-US;
  timeZone Asia/Saigon; Screen Resolution `1920x1200 16:10 24-bit TrueColor
  (viewport: 658x1069)`; JavaScript Enabled True; cookieEnabled true. All match ket-qua.txt
  exactly, with no contradiction, in both screenshots.
- Window drag: ket-qua.txt records before drag innerWidth 858 / outerWidth 878, after drag
  innerWidth 658 / outerWidth 678, height unchanged (innerHeight 1069, outerHeight 1176).
  That is exactly a 200-pixel width reduction. Both screenshots show viewport 658x1069,
  matching the after-drag inner size, and screen resolution is unchanged at 1920x1200.
- Caveat, same as TB-B2 noted: the font count (327 fonts, 113 unique metrics) appears only
  in ket-qua.txt; neither screenshot is a fonts-page screenshot. The key does not explicitly
  require a fonts-page screenshot and nothing contradicts the stated count, so this is not
  a failure.

Verdict: PASS. Correct.

### 2. R3-002: FAIL (agrees with TB-B2)

Key (Tier A): 3 JSON snippets, error line and column at start, checked on jsonlint.com.
JSON key rows: line 1 col 27, line 1 col 50, line 1 col 26. The checker reads line and
column from ket-qua.txt.

My independent verification: I ran a Python JSON parser (`json.loads`) on the 3 original
snippets as written in the key, not on the snapshot numbers. Parser results:
- Snippet 1: line 1, column 27, "Expecting property name enclosed in double quotes".
- Snippet 2: line 1, column 50, "Expecting ',' delimiter".
- Snippet 3: line 1, column 26, "Expecting ',' delimiter".
The parser confirms the frozen key columns exactly.

Snapshot ket-qua.txt reports: snippet 1 column 23, snippet 2 column 44, snippet 3
column 24. All three columns disagree with the independently verified key (27, 50, 26).
Lines are all 1, which matches, and the fixed JSON strings do parse as valid JSON, but
the scored fields are the error line and column. (Minor extra note: the snapshot's
snippet 3 error text says "Expecting '}' delimiter" while the parser says
"Expecting ',' delimiter"; the scored field is the column, which is wrong either way.)

Verdict: FAIL. Correct.

### 3. R3-003: FAIL (agrees with TB-B2)

Key (Tier B hybrid): 9-cell answer table (3 rows: announcement date 9 October 2026, place
Oslo, Norway, main person Navanethem (Navi) Pillay; 3 columns, one per paper: Al Jazeera,
CNA, NPR) plus a 3-line conclusion stating clearly that there is no contradiction and all
3 items match across all 3 papers. Evidence is a saved online document with the table
plus the conclusion.

My checks: I listed the snapshot directory directly. It contains only `runner-report.txt`
and `manifest.sha256`. No ket-qua.txt, no table, no conclusion document exists. The report
itself states "Evidence files written: None yet for R3-003 (no ket-qua.txt written, no
screenshots taken)" and "Status: Task R3-003 is BLOCKED". Only articles 1 (Al Jazeera) and
2 (CNA) were read; article 3 (NPR via WCBE) returned a persistent CloudFront 403 block
and the Wayback Machine returned 429. The blocker is documented honestly and no values
were fabricated, but the keyed part (9-cell table) and the human-graded part (3-line
conclusion) are both absent, so the task cannot pass. This is FAIL, not INVALID: no key
invalidity rule for R3-003 applies.

Verdict: FAIL. Correct.

### 4. R3-067: PASS (agrees with TB-B2)

Key (Tier C rubric): 3 shapes, all solid Fill Shape: (1) rectangle, region x 50-350,
y 50-250, filled red; (2) circle, region x 300-500, y 200-400, filled blue; (3) triangle,
region x 550-750, y 350-550, filled green; white background; file size 800x600. PASS
only if all 3 shapes are correct type, correct region, correct color, solid fill, on
white 800x600.

My measurement method: fresh PIL pixel analysis of
`/home/hatch/workspace/r3-067-calibration.png`, computed by me (exact RGB counts,
bounding boxes, centers, row widths, fill ratio against the ideal circle). Results:
- Size and format: PNG, 800x600, RGB. Background white (255, 255, 255), 368452 pixels.
  Only 4 distinct colors in the whole image: white, red (255, 0, 0), blue (0, 0, 255),
  green (0, 128, 0). No stray colors.
- Rectangle, red: bounding box x 50-350, y 50-250 exactly, center (198.1, 148.8),
  59658 red pixels. Red pixels inside the rectangle region: 59658 of 60501; the deficit
  is the corner where the blue circle overlaps the rectangle, not a hollow fill. Solid.
- Circle, blue: bounding box x 300-500, y 200-400 exactly, center (400.0, 300.0),
  31689 blue pixels. Fill inside the ideal circle of radius 100 centered at (400, 300):
  31417 of 31417, ratio 1.0000. Correct type (circle, not ellipse), correct region,
  correct color.
- Triangle, green: bounding box x 550-750, y 350-550 exactly, center x 650.0,
  20201 green pixels. Row widths grow linearly from 11 pixels wide at y 360 (x 645-655)
  to 199 pixels wide at y 549 (x 551-749), apex at top center (650, 350), base along
  y 550. Filled triangle with the required shape, region, and color.

Verdict: PASS. Correct.

## Verdict

I independently verified the TB-B2 calibration, case by case, from the frozen key and the
snapshots. My re-grading agrees with the calibration file on all four cases:

- R3-041: PASS
- R3-002: FAIL
- R3-003: FAIL
- R3-067: PASS

Agreement: 4/4. The TB-B2 calibration is correct as graded.

## Sign-off

I sign off on the TB-B2 calibration for gate G-33. The gap identified in the coordinator
note (approval resting on the coordinator's own check only, with no independent
verification) is now closed by this independent verification. I did not start the run and
did not run any run task.

## Round-2 fix note (R2-S1, 2026-11-25)

The verifier session id was searched in the prepare records (memory log ~/memory/2026-11-25.md, the prepare report, this sign-off file) and is NOT recoverable; the prepare phase recorded only that the verifier was an independent subagent, with no session id. Commit-identification is accepted instead: this sign-off is identified by commit b061f87c, committed 2026-11-25 09:20:08 +07. N-06 is closed as a recorded limitation, per the round-2 redteam fallback (fix if recoverable, otherwise accept commit-identification).
