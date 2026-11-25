# R3-025 (R3-L3) - Scorer 1 grade

- Scorer: A1 (mochi), session 70cd99d1-ecef-4d02-9f42-714d7e86ab85
- Task: R3-025, Pair A, position 22, Tier B, medium difficulty
- Snapshot: rung3-run-log/rung3-snapshots/R3-025-L3/ on todolist-push e4600512
- Manifest sha256: 13d5004bd6f0df609bf1da016e6e1538e397aab206ebdd10480125e30d4a52c8
- Scored at: 2026-11-26T04:28:38+07:00 (Asia/Ho_Chi_Minh)
- Verdict: FAIL

## Key (verified before scoring)

- Key file hashes at tip e4600512 match the R3-L3 freeze: docs/rung3-answer-keys.json 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, docs/rung3-answer-keys.md 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60.
- Key section: docs/rung3-answer-keys.md lines 314-322 (## R3-025, Tier B) + docs/rung3-answer-keys.json allocated.R3-025 entry.
- Query 1 (site: operator): site:en.wikipedia.org photosynthesis
- Query 2 (filetype:pdf operator): filetype:pdf photosynthesis
- Each query records the first 3 results, with title and URL. URLs match the search results at run time; truth is the search-result screenshot.
- Open 1 PDF result in the Brave browser, check the file opens, record the page count (live value of that file, cross-checked with the screenshot).
- If Google shows a 'Verify you are human' verification page or asks for a captcha, stop, record clearly in ket-qua.txt, task invalid per section 1.
- Scoring evidence: 2 search-result screenshots + ket-qua.txt. Scorer cross-checks URLs and page count with the screenshots.
- Task text: docs/rung3-list-100-tasks.md section 6, lines 445-447 (find 3 PDF files with the site and filetype search operators, record the URL of each file; steps: Google search with site:, record first 3 results with title and URL; second query with filetype:pdf, record first 3 results; open 1 PDF result in Brave, record page count; save timestamped screenshots of both queries; write ket-qua.txt with the 2 queries, 6 results with URLs, page count of the opened PDF).

## Snapshot verification

- Snapshot extracted to ~/workspace/rung3-scorer1-R3-025-L3-snapshot/.
- Manifest field manifest_sha256 13d5004b... matches the assignment.
- Manifest lists 2 files, both hash-OK and size-OK: start_time.txt (26 B, sha256 24c6e665...), end_time.txt (26 B, sha256 cf1128f0...).
- The snapshot directory contains only 3 files: manifest.json, start_time.txt, end_time.txt.
- ket-qua.txt: MISSING. Screenshots: 0. No deliverable of any kind.
- Start time: 2026-11-26T03:55:30+07:00. End time: 2026-11-26T04:23:32+07:00. Run duration 28 min 2 s, within the 30-min task timeout.
- The sealing commit message (e4600512) states "runner/driver failure": the runner's driver stalled and produced no task evidence.

## Evidence check

- Pass criteria require: 2 queries, 6 results with titles and URLs, 1 PDF page count, 2 search-result screenshots, ket-qua.txt.
- None of these exist in the snapshot. Zero Pass criteria can be checked. There is nothing to cross-check against the screenshots, because there are no screenshots.
- No ket-qua.txt exists, so there is no record of any Google verification/captcha page either. The key's section 1 invalid rule (stop and record a bot-check page in ket-qua.txt) was not triggered in any evidence, and no such page is shown anywhere.
- This is a runner-side driver stall that produced no evidence at all. It is not a service bot-check page, and no independent evidence of a service block exists to collect. Per the run rule, too-incomplete evidence (no ket-qua.txt, no screenshots, no deliverable) is FAIL (incomplete), not INVALID.
- The run duration (28 min 2 s) is within the 30-min timeout, so the failure is not a timeout overrun; the driver stalled inside the allowed window and produced nothing.

## Verdict

FAIL (incomplete). No task evidence was produced: ket-qua.txt is missing and there are 0 screenshots, so no Pass criterion is met. The failure is a runner-side driver stall, not a recorded service block, so it is not INVALID.

## Files read

- /home/hatch/workspace/rung3-scorer1-R3-025-L3-snapshot/rung3-run-log/rung3-snapshots/R3-025-L3/manifest.json
- /home/hatch/workspace/rung3-scorer1-R3-025-L3-snapshot/rung3-run-log/rung3-snapshots/R3-025-L3/start_time.txt
- /home/hatch/workspace/rung3-scorer1-R3-025-L3-snapshot/rung3-run-log/rung3-snapshots/R3-025-L3/end_time.txt
- docs/rung3-answer-keys.md (R3-025 key section lines 314-322, todolist-push e4600512)
- docs/rung3-answer-keys.json (allocated.R3-025 entry, todolist-push e4600512)
- docs/rung3-list-100-tasks.md (section 6, R3-025 task text lines 445-447, todolist-push e4600512)
