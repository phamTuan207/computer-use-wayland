# Scorer 1 grade, R3-L3, R3-009

- Session: 70cd99d1-ecef-4d02-9f42-714d7e86ab85 (scorer 1A, Pair A)
- Task: R3-009 (Tier B, position 9, run R3-L3)
- Verdict: PASS
- Scored at: 2026-11-25 22:39:19 +07 (Asia/Ho_Chi_Minh)
- Snapshot: rung3-run-log/rung3-snapshots/R3-009-L3/ at todolist-push commit 81d754ee, manifest_sha256 61c0ba3bf24e5fbea3c6470c39cc0604d858d8702af27a70e59ba86caa6d6889, all 9 evidence files hash-OK against manifest.json, manifest gate PASS
- Key file hashes (verified before scoring): docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both match the R3-L3 freeze)

## Files read

- rung3-run-log/rung3-snapshots/R3-009-L3/manifest.json (snapshot R3-009-L3, commit 81d754ee)
- rung3-run-log/rung3-snapshots/R3-009-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-009-L3/20261125-222309-wave-site1.png
- rung3-run-log/rung3-snapshots/R3-009-L3/20261125-222326-wave-site2.png
- rung3-run-log/rung3-snapshots/R3-009-L3/20261125-222609-wave-site1-error-detail.png
- rung3-run-log/rung3-snapshots/R3-009-L3/20261125-222715-wave-site1-error-info.png
- rung3-run-log/rung3-snapshots/R3-009-L3/20261125-222802-wave-site1-error-info2.png
- rung3-run-log/rung3-snapshots/R3-009-L3/pill-gone-check.png
- rung3-run-log/rung3-snapshots/R3-009-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-009-L3/end_time.txt
- docs/rung3-answer-keys.md, R3-009 section only (lines 196-203)
- docs/rung3-answer-keys.json, R3-009 entry only (check_date 2026-11-24, urls Fox News and Wikipedia Main Page)
- docs/rung3-list-100-tasks.md, section 6, R3-009 task text only

I scored from the snapshot and the key only. I did not read any other scorer's grade or verdict file, did not contact the runner, and did not read any runner log, ledger, or trial report. I did not re-run any WAVE check on the live sites; the key states the metrics are live values at run time and the truth is the summary table in the screenshot, not the current value of the page.

## Key (R3-009, Tier B)

URL 1: https://www.foxnews.com/. URL 2: https://en.wikipedia.org/wiki/Main_Page. Each page had at least 1 error (Errors) in the pre-run check on 2026-11-24 (Fox News: Errors 2, Contrast Errors 17, Alerts 312, Features 142, Structural Elements 383; Wikipedia: Errors 7, Alerts 80, Features 451, Structural Elements 75, Contrast Errors 0). If at run time the first page has 0 errors, the task is invalid per section 1 (record clearly in ket-qua.txt), not counted as fail; the second page with 0 errors still records all 5 metrics normally. 5 metrics per page: Errors, Alerts, Features, Structural Elements, Contrast Errors. The metrics are live values at run time; the truth is the summary table in the screenshot. Conclusion: which page has the larger Errors + Alerts total; if the totals are equal, record clearly that the 2 pages are equal. The error item is taken only from the first page; the second page only needs all 5 metrics.

Task text Pass: all 5 metrics for both pages, metrics match the summary table at run time per the screenshots, has the name and description of 1 error item, conclusion correctly identifies the page with the larger Errors + Alerts total (or records clearly that the 2 pages are equal if totals are equal), result file has all items, screenshots show both summary tables.

## Evidence

- ket-qua.txt (540B) records:
  - Site 1 Fox News: Errors 2, Alerts 309, Features 152, Structural Elements 378, Contrast Errors 18. First error item: Missing form label (1 instance). Description: "A form control does not have a corresponding label."
  - Site 2 Wikipedia Main Page: Errors 7, Alerts 90, Features 452, Structural Elements 78, Contrast Errors 0.
  - Conclusion: Site 1 has the larger Errors + Alerts total (311 vs 97).
- Site 1 summary screenshot 20261125-222309-wave-site1.png (WAVE, Address https://www.foxnews.com/) shows: Errors 2, Contrast Errors 18, Alerts 309, Features 152, Structure 378, ARIA 569, AIM Score 6.7 out of 10; the Errors list shows "1 Missing form label" and "1 Empty heading". All 5 metrics in ket-qua.txt match this screenshot exactly.
- Site 2 summary screenshot 20261125-222326-wave-site2.png (WAVE, Address https://en.wikipedia.org/wiki/Main_Page) shows: Errors 7, Contrast Errors 0, Alerts 90, Features 452, Structure 78, ARIA 64, AIM Score 8 out of 10. All 5 metrics in ket-qua.txt match this screenshot exactly.
- Error detail screenshots confirm the error item: 20261125-222609-wave-site1-error-detail.png shows the runner clicking the "1 Missing form label" item; 20261125-222802-wave-site1-error-info2.png shows the WAVE Reference panel for "Missing form label" with "What It Means: A form control does not have a corresponding label." The name and description in ket-qua.txt match exactly.
- Conclusion arithmetic: Site 1 Errors + Alerts = 2 + 309 = 311. Site 2 Errors + Alerts = 7 + 90 = 97. 311 is larger than 97, so Site 1 has the larger total. The conclusion in ket-qua.txt is correct.
- Site 1 has Errors 2 (not 0), so the task is not invalid; it runs normally, as the pre-run WAVE gate predicted (Fox News Errors 2 on 2026-11-24).
- Live variation note: the later Fox News screenshots (22:26 and 22:27) show slightly different numbers (Structure 377, Alerts 307, Features 153) because the Fox News homepage updates live. The ket-qua.txt numbers match the first summary screenshot (22:23:09), which is the screenshot of record for the summary table; the key says the truth is the summary table in the screenshot. This drift does not change the verdict.
- Extra file note: pill-gone-check.png is a screenshot of a Muse chat about closing tabs after each task, not a WAVE screenshot. It is not part of the required evidence (2 summary screenshots + ket-qua.txt), and the Pass criteria do not forbid extra files, so it does not affect the verdict.
- Timing: start 2026-11-25T22:22:47+07:00, end 2026-11-25T22:28:06+07:00 (5 min 19 s), plausible for 2 WAVE checks plus the error detail.

## Reason

All 5 metrics for both pages match the WAVE summary screenshots exactly, the error item (Missing form label) and its description match the WAVE Reference panel, and the conclusion correctly identifies Site 1 as having the larger Errors + Alerts total (311 vs 97).

Signed: mochi, scorer 1A, session 70cd99d1-ecef-4d02-9f42-714d7e86ab85.
