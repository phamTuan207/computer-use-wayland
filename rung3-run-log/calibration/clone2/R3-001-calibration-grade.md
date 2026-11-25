# R3-001 calibration grade (clone2, sealed, blind)

- Task: R3-001 (Tier B)
- Grader: clone2
- Session: clone2-main-ad85548c-ced4-4f31-afdb-d1043dcabbd7
- Date: 2026-11-26
- Verdict: FAIL

## Ponytail availability

The ponytail skill is available to me: installed as a custom skill at ~/workspace/custom-skills/ponytail/SKILL.md and confirmed in skill search before starting. Grading needs no code, so no code was written for this assignment.

## Key verification

- docs/rung3-answer-keys.md sha256: 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (matches the brief)
- docs/rung3-answer-keys.json sha256: 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8 (matches the brief)
- Key section used: docs/rung3-answer-keys.md, "## R3-001 (Tier B)", lines 109-118

## Snapshot verification

- Snapshot: rung3-run-log/rung3-snapshots/R3-001-L3/
- Manifest hash (manifest_sha256 field in manifest.json): 507086e2d379475fb3b9403a3e86deac4fa96d2c9777cdd6242fafde03d4d2ca (matches the brief)
- Per-file sha256 verification against manifest.json (recomputed, hash and size): all OK
  - end_time.txt 59464f4b6283b01c3d089c4fea4f092808d8607eda6136f7e5855b5b6eab088a OK
  - final.png 1c9d2e618494bb1712473496adc8db026bed320b65757ff83b7e840a0eef572a OK
  - ket-qua.txt 6c666efa75c6b5d8fdf101bf0839901835706564ec9879bafb374a8e1aafc878 OK
  - live-state.json cccd91407cf8794fcf4f2797de05bde8abd034bc715c9a6017d2d9188f20087b OK
  - live-state.png c8b41f69346415de82fe1db8e1032380564f7c64a834c3dd18fb53efb0bb364b OK
  - start_time.txt a262143ff4ba45c4374055177262fdd227ae8293c26502cfe65956782d873d0f OK
- No files in the snapshot dir beyond the manifest list.

## Files read

- rung3-run-log/briefs/clone2-calibration-brief.md (the assignment)
- docs/rung3-answer-keys.md (sha256 verification; key section lines 109-118 only)
- docs/rung3-answer-keys.json (sha256 verification only)
- docs/rung3-list-100-tasks.md section 1, lines 9-40 (grading and false-success rules, as the brief directs)
- rung3-run-log/rung3-snapshots/R3-001-L3/manifest.json
- rung3-run-log/rung3-snapshots/R3-001-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-001-L3/final.png
- rung3-run-log/rung3-snapshots/R3-001-L3/live-state.json
- rung3-run-log/rung3-snapshots/R3-001-L3/live-state.png
- rung3-run-log/rung3-snapshots/R3-001-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-001-L3/end_time.txt

## Independence declaration

I graded blind from the snapshot and key section only; I did not read the ledger, any grade file, or any other verdict for these tasks.

## Reasons

- ket-qua.txt textually matches the key's required final state exactly: 4 items (Tap the duc 45 phut Active, Viet bao cao tuan Completed, Goi dien cho me Active, Don dep phong Active) with counts Active 3, Completed 1, All 4.
- final.png, the runner's own final screenshot, shows the TodoMVC JavaScript ES5 app with an empty list: only the "What needs to be done?" input, no todo rows, no counter footer. It does not show the claimed final list.
- live-state.png also shows an empty list, and live-state.json (a read-only WebDriver BiDi DOM re-read captured 2026-11-25T13:36:24+07:00, inside this snapshot) records both javascript-es5/dist tabs at "0 items left" with empty todo arrays, and both vanillajs tabs as 404 pages. The key section requires the grader to reopen the TodoMVC page and compare; the reopened state contains none of the claimed items.
- List section 1 grades pass on the final state measured from DOM and content, not on the agent's self-report, and sets false success at zero tolerance: claiming completion when the final state holds no data is a FAIL. ket-qua.txt is a self-report contradicted by the measured final state in final.png and live-state.json.
- Corroboration from the snapshot itself: start_time.txt is 2026-11-25T13:26:22 and end_time.txt is 2026-11-25T13:26:44, a 22 second window for a multi-step add, complete, filter, edit and delete flow, a point also flagged inside live-state.json.
