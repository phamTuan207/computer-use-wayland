# Scorer 1 grade, R3-L3, R3-001 RE-RUN

- Session: 70cd99d1-ecef-4d02-9f42-714d7e86ab85 (scorer 1A, Pair A)
- Task: R3-001 RE-RUN (Tier B, position 1, Class L, run R3-L3, counting rule A, owner approved 18:46)
- Verdict: PASS
- Scored at: 2026-11-25 19:15:29 +07 (Asia/Ho_Chi_Minh)
- Snapshot: rung3-run-log/rung3-snapshots/R3-001-L3-rerun/ at todolist-push commit 3511b060, manifest_sha256 23c250b28131aef88151935ecae8a0825712de8a2e97cce796deb4f04c1b34a2, all 4 evidence files hash-OK against manifest.json, manifest gate PASS
- Key file hashes (verified before scoring): docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both match the R3-L3 freeze)

## Files read

- rung3-run-log/rung3-snapshots/R3-001-L3-rerun/manifest.json (snapshot R3-001-L3-rerun, commit 3511b060)
- rung3-run-log/rung3-snapshots/R3-001-L3-rerun/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-001-L3-rerun/20261125-190300-final-list.png
- rung3-run-log/rung3-snapshots/R3-001-L3-rerun/start_time.txt
- rung3-run-log/rung3-snapshots/R3-001-L3-rerun/end_time.txt
- docs/rung3-answer-keys.md, R3-001 section only (lines 109-117)
- docs/rung3-list-100-tasks.md, section 6, R3-001 task text only (lines 300-304)

I scored this RE-RUN execution on its own evidence only. I did not use the original R3-001 (13:51:40 +07) verdict to prejudge this run, did not read any other scorer's grade or verdict file, did not contact the runner, did not read any runner log, ledger, or trial report, and did not open TodoMVC in my own Chromium. The JSON key file has no R3-001 entry (it holds only Tier A/machine keys), so the key for this task is the md section. Class L: the live state is not reset until both verdicts are audited; I scored from the sealed snapshot as the brief requires.

## Key (R3-001, Tier B)

Final list (4 items): "Tap the duc 45 phut" (not complete), "Viet bao cao tuan" (complete), "Goi dien cho me" (not complete), "Don dep phong" (not complete). Filter at step 4 (before edit and delete): Active 3, Completed 2, All 5. Filter after step 6: Active 3, Completed 1, All 4. The edited item shows the new content ("Tap the duc 45 phut"); the deleted item ("Mua sach Python") is gone. Scoring evidence per the key: screenshot of the final list + ket-qua.txt. Task text (list section 6) Pass: final list 4 items, 1 complete, 3 incomplete, Active 3, Completed 1 after step 6, All 4, edited item has new content, screenshot shows the final list.

## Evidence (this re-run execution)

- ket-qua.txt (250B): page title "TodoMVC: JavaScript Es5"; final tasks (4): 1. "Tap the duc 45 phut" not completed, 2. "Viet bao cao tuan" completed, 3. "Goi dien cho me" not completed, 4. "Don dep phong" not completed; filter counts at step 4: Active 3, Completed 2, All 5. Matches the key exactly.
- 20261125-190300-final-list.png: I visually confirmed the TodoMVC JavaScript ES5 app shows the final list with the same 4 items and statuses: "Tap the duc 45 phut" unchecked, "Viet bao cao tuan" checked and struck through, "Goi dien cho me" unchecked, "Don dep phong" unchecked; footer "3 items left", All filter selected showing all 4 items. The screenshot and ket-qua.txt agree with each other and with the key. The edited item shows the new content; the deleted item is absent.
- Timing: start 2026-11-25T18:53:21+07:00, end 2026-11-25T19:03:16+07:00 (9 min 55 s), plausible for 7 browser steps. No timing red flag.
- Note: this re-run snapshot has no live-state.json (no coordinator BiDi capture file); the evidence is ket-qua.txt plus the final-list screenshot, which is exactly the evidence the key specifies for this task. The screenshot is a direct visual record of the populated app state.

## Reason

The final list matches the key exactly (4 items, correct contents and statuses, Active 3, Completed 1, All 4 after step 6), the edited item shows the new content, the deleted item is gone, and the screenshot corroborates ket-qua.txt. This execution passes on its own evidence.

Signed: mochi, scorer 1A, session 70cd99d1-ecef-4d02-9f42-714d7e86ab85.
