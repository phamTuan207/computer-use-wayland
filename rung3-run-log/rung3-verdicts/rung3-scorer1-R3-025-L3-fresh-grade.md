# R3-025-L3 (fresh) — Scorer 1 grade

- Session: 70cd99d1-ecef-4d02-9f42-714d7e86ab85
- Task: R3-025, Tier B, position 22, run R3-L3 (fresh attempt; supersedes the empty-snapshot attempt scored FAIL earlier)
- Scored at: 2026-11-26T04:55:15+07:00
- Verdict: PASS
- Snapshot: rung3-run-log/rung3-snapshots/R3-025-L3-fresh/ on todolist-push f0f39a9e, manifest_sha256 40f661b31f974d869f569d3f682700642a55dc0309b61a078230dfbab1c701ad, gate PASS
- Key hashes verified before scoring: docs/rung3-answer-keys.json 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, docs/rung3-answer-keys.md 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both match freeze)
- Files read: 9 (manifest.json, ket-qua.txt, start_time.txt, end_time.txt, search1-20261126-044358.png, search2-20261126-044557.png, keys.md R3-025 section, keys.json R3-025 entry, list section 6 R3-025)
- Timing: start 2026-11-26T04:41:03+07:00, end 2026-11-26T04:48:50+07:00 (7 min 47 s), within the 30-min timeout

## Key (keys.md lines 314-322 + JSON allocated.R3-025)

- Query 1 (site: operator): site:en.wikipedia.org photosynthesis
- Query 2 (filetype:pdf operator): filetype:pdf photosynthesis
- Each query records the first 3 results with title and URL. URL matches the search result at run time; truth is the search-result screenshot.
- Open 1 PDF result in Brave, check the file opens, record page count (page count is the live value of that file, cross-checked with the screenshot).
- If Google shows a 'Verify you are human' verification page or asks for captcha, stop, record clearly in ket-qua.txt, task invalid per section 1.
- Scoring evidence: 2 search-result screenshots + ket-qua.txt. Scorer cross-checks URL and page count against the screenshot.

## Task text (list section 6, lines 445-447)

Find 3 PDF files using the site and filetype search operators, record the URL of each file (source MOI-B36, group browser, difficulty medium). Steps: open Google search, enter the site: query on a public domain with a topic keyword (bot-check page = stop, record, invalid per section 1); record the first 3 results with title and URL; enter the filetype:pdf query, record the first 3 results; open 1 PDF result in Brave (built-in PDF viewer), check the file opens, record page count; save timestamped screenshots of both search-result pages; write ket-qua.txt with 2 queries, 6 results with URL, page count of the opened PDF.

## Evidence check

- Query 1 screenshot (search1-20261126-044358.png, 04:43:58): Google search "site:en.wikipedia.org photosynthesis", no bot-check page. Result 1 "Photosynthesis", https://en.wikipedia.org/wiki/Photosynthesis, fully visible, matches ket-qua.txt. Result 2 "Evolution of photosynthesis", https://en.wikipedia.org/wiki/Evolution_of_photosynthesis, fully visible, matches ket-qua.txt. Result 3: URL line visible as "https://en.wikipedia.org › wiki › File:..." (title below the fold); the file name "C4 photosynthesis.svg" appears in the same screenshot's image block ("File:C4 photosynthesis.svg - ...", Wikimedia Commons), corroborating ket-qua.txt result 3 (File:C4 photosynthesis.svg - Wikimedia Commons - https://en.wikipedia.org/wiki/File:C4_photosynthesis.svg).
- Query 2 screenshot (search2-20261126-044557.png, 04:45:57): Google search "filetype:pdf photosynthesis", no bot-check page. Result 1 "What Is Photosynthesis? A Broader and Inclusive View" (UIUC Life Sciences, https://www.life.illinois.edu › recent_papers_files, PDF badge) matches ket-qua.txt. Result 2 "PHOTOSYNTHESIS" (NIOS, https://digital.nios.ac.in › content › Lesson-11, PDF badge) matches ket-qua.txt; snippet reads "20 trang" (20 pages). Result 3 "Photosynthesis" (Prefeitura de Jundiai, https://educacao.jundiai.sp.gov.br › 2026/05 › Ph..., PDF badge) matches ket-qua.txt. Google truncates the URLs in the display; domain and path fragments match in all 3 cases.
- PDF opened: ket-qua.txt records result 2 of query 2 (Lesson-11.pdf) opened in a new Brave tab, built-in PDF viewer, viewer title "Lesson-11.pmd", file opened OK, page count 20 (pagelength=20, pages 1-20), matching the Google snippet "20 trang".
- Independent verification by scorer: downloaded the live PDF from https://digital.nios.ac.in/content/314en/Lesson-11.pdf (public URL, read-only) and ran pdfinfo: Title "Lesson-11.pmd", Pages 20. Both match ket-qua.txt exactly. Temp file removed after the check.
- No 'Verify you are human' or captcha page on either search; task ran normally, no invalid.
- ket-qua.txt complete: 2 queries, 6 results with title and URL, PDF opened with page count 20.

## Minor note

Result 3 of query 1 is cut off at the bottom edge of the search1 screenshot: its title is not directly readable and its URL is truncated at "File:...". All visible fragments match ket-qua.txt, the file name is corroborated by the image block in the same screenshot, and nothing contradicts the record. Noted, not a fail. Precedent: R3-017 accepted a truncated title where the visible prefix matched.

## Note on the fresh attempt

The first R3-025 attempt produced an empty snapshot (no ket-qua.txt, no screenshots) and was scored FAIL by scorer 1 (branch mochi/verdict-R3-025-L3, commit 44bacdaa). This fresh attempt is a new sealed snapshot with full evidence; per counting rule A, the fresh attempt supersedes the original at closure.

## Verdict

PASS. All Pass criteria met: 6 results recorded with title and URL matching the screenshots, 1 PDF opened in Brave with page count 20 independently verified, no bot-check page.
