# Scorer 1 grade, R3-L3, R3-017

- Session: 70cd99d1-ecef-4d02-9f42-714d7e86ab85 (scorer 1A, Pair A)
- Task: R3-017 (Tier B, position 16, run R3-L3)
- Verdict: PASS
- Scored at: 2026-11-26 01:22:03 +07 (Asia/Ho_Chi_Minh)
- Snapshot: rung3-run-log/rung3-snapshots/R3-017-L3/ at todolist-push commit 796eabad, manifest_sha256 0c5f876438105f10b9464364b07fd9d71c659302c2ea26c75d566c8e963c9dc5, all 4 evidence files hash-OK against manifest.json, manifest gate PASS
- Key file hashes (verified before scoring): docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both match the R3-L3 freeze)

## Files read

- rung3-run-log/rung3-snapshots/R3-017-L3/manifest.json (snapshot R3-017-L3, commit 796eabad)
- rung3-run-log/rung3-snapshots/R3-017-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-017-L3/20261126-011455-brave-taskmgr.png
- rung3-run-log/rung3-snapshots/R3-017-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-017-L3/end_time.txt
- docs/rung3-answer-keys.md, R3-017 key section (lines 255-262)
- docs/rung3-list-100-tasks.md, section 6, R3-017 task text (lines 402-404)

I scored from the snapshot and the key only. I did not read any other scorer's grade or verdict file, did not contact the runner, and did not read any runner log, ledger, or trial report. I read the task manager screenshot directly and cross-checked every value in ket-qua.txt against it.

## Key (R3-017, Tier B)

5 tabs opened on the Brave browser, in this opening order: 1. https://example.com 2. https://en.wikipedia.org/wiki/Main_Page 3. https://www.bbc.com/ 4. https://github.com 5. https://www.python.org. Open the task manager with Shift Esc; if the test browser has no such shortcut, stop, record it in ket-qua.txt, task invalid per section 1. Table of the 5 tabs with the highest memory usage among the tab rows (only count rows with a tab title; ignore Browser, GPU Process, extension and utility service rows), with memory and CPU, sorted descending by memory. Memory and CPU values are live at run time; the truth is the task manager screenshot, not a re-run command. Evidence: task manager screenshot + ket-qua.txt. The scorer cross-checks the table against the screenshot. Amendment note (R3-L3, 2026-11-24): define the 5 tabs as section 6 of the list; values in the file must match the screenshot.

## Evidence

- The screenshot (01:14:55) shows the Brave Task Manager, All tasks tab. The browser tab bar shows the 5 tabs in the key's opening order: Example D..., Wikipedia, the..., www.bbc.com, GitHub, Welcome to Python.org. The active tab is example.com, showing the Example Domain page.
- The task manager lists these Tab rows with Memory footprint and CPU:
  - Tab: Example Domain, 27,592K, 0.0
  - Tab: Wikipedia, the free encyclopedia, 38,288K, 0.0
  - Tab: www.bbc.com, 25,580K, 0.0
  - Tab: GitHub, Change is constant. GitHub keep... (title truncated by column width), 73,144K, 0.0
  - Tab: Welcome to Python.org, 35,548K, 0.0
- ket-qua.txt (436B) records the 5-tab table, sorted by memory descending:
  - 1. Tab: GitHub, Change is constant. GitHub keeps you ahead., GitHub, GitHub | 73,144K | 0.0
  - 2. Tab: Wikipedia, the free encyclopedia | 38,288K | 0.0
  - 3. Tab: Welcome to Python.org | 35,548K | 0.0
  - 4. Tab: Example Domain | 27,592K | 0.0
  - 5. Tab: www.bbc.com | 25,580K | 0.0
- Cross-check: every memory value and every CPU value in ket-qua.txt matches the screenshot exactly (73,144K, 38,288K, 35,548K, 27,592K, 25,580K; all CPU 0.0). The order is correct descending by memory: 73,144 > 38,288 > 35,548 > 27,592 > 25,580. The GitHub tab title in ket-qua.txt is the full title; the screenshot truncates it at the column width ("GitHub, Change is constant. GitHub keep"), and the visible prefix matches.
- Non-tab rows are correctly excluded from the table: App: Muse (181,008K), Private Tab: Muse (198,364K), and the stripe subframes are the agent's own tooling, not among the 5 task tabs defined in section 6 of the list, so they do not belong in the 5-tab table.

## Reason

All 5 required tabs are open in the specified order, the task manager opened (Shift Esc worked, so no invalid condition), and ket-qua.txt lists exactly those 5 tabs with memory and CPU values that match the screenshot exactly, in correct descending memory order. Every key check passes.

Timing note: start 2026-11-26T01:10:34+07:00, end 2026-11-26T01:15:28+07:00 (4 min 54 s); the screenshot is timestamped 01:14:55 and ket-qua.txt was captured 01:15:24, consistent with reading the task manager and then writing the table.

Signed: mochi, scorer 1A, session 70cd99d1-ecef-4d02-9f42-714d7e86ab85.
