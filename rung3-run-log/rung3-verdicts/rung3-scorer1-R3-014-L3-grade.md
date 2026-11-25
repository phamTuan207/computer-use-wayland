# Scorer 1 grade, R3-L3, R3-014

- Session: 70cd99d1-ecef-4d02-9f42-714d7e86ab85 (scorer 1A, Pair A)
- Task: R3-014 (Tier A, position 14, FCC-run, run R3-L3)
- Verdict: PASS
- Scored at: 2026-11-26 00:35:47 +07 (Asia/Ho_Chi_Minh)
- Snapshot: rung3-run-log/rung3-snapshots/R3-014-L3/ at todolist-push commit 38cd6c95, manifest_sha256 b6540e2c0cb71c03830f8a902d95447bf8f427fc18ccb1b9e81a7ac2c1115e23, all 6 evidence files hash-OK against manifest.json, manifest gate PASS
- Key file hashes (verified before scoring): docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both match the R3-L3 freeze)
- Tier A checker (coordinator-supplied, aid only): {"verdict": "PASS", "reasons": [], "task": "R3-014", "key_hash": "5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8"}. I verified the evidence independently below, including the check the assignment flagged (whether the 3 screenshots each show a different hex code); my verdict agrees with the checker. No checker-vs-evidence discrepancy found.

## Files read

- rung3-run-log/rung3-snapshots/R3-014-L3/manifest.json (snapshot R3-014-L3, commit 38cd6c95)
- rung3-run-log/rung3-snapshots/R3-014-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-014-L3/20261126-002359-FF0000.png
- rung3-run-log/rung3-snapshots/R3-014-L3/20261126-002424-008080.png
- rung3-run-log/rung3-snapshots/R3-014-L3/20261126-002446-FFD700.png
- rung3-run-log/rung3-snapshots/R3-014-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-014-L3/end_time.txt
- docs/rung3-answer-keys.md, R3-014 key section (lines 237-243)
- docs/rung3-answer-keys.json, R3-014 entry only (tasks.R3-014, type color-rgb)
- docs/rung3-list-100-tasks.md, section 6, R3-014 task text (lines 387-389)

I scored from the snapshot and the key only. I did not read any other scorer's grade or verdict file, did not contact the runner, and did not read any runner log, ledger, or trial report. I verified the RGB and HSL values independently with Python colorsys, and I read each of the 3 screenshots directly.

## Key (R3-014, Tier A)

3 colors and their correct RGB values:
- #FF0000: RGB(255, 0, 0)
- #008080: RGB(0, 128, 128)
- #FFD700: RGB(255, 215, 0)

The HSL values of the 3 colors are recorded as shown on the page (live, compared against the screenshot). Evidence: 3 screenshots (each 1 code) + ket-qua.txt. The checker compares hex and RGB.

Task text: open htmlcolorcodes.com, open the color picker tool; enter the first hex #FF0000, record the RGB value shown; enter the second #008080 and third #FFD700 similarly; switch the display unit to HSL if available, record the HSL value of the 3 colors; save 3 screenshots, each showing 1 hex code, because the picker only shows 1 color at a time; write ket-qua.txt with 3 lines, each line with hex code, RGB triple, HSL value.

## Evidence

- ket-qua.txt (130B) records all 3 lines:
  - #FF0000 RGB(255, 0, 0) HSL(0, 100%, 50%)
  - #008080 RGB(0, 128, 128) HSL(180, 100%, 25%)
  - #FFD700 RGB(255, 215, 0) HSL(51, 100%, 50%)
- Screenshot FF0000 (00:23:59, 960x609 JPEG): htmlcolorcodes.com Color Picker showing a red swatch labeled FF0000, top bar reads HEX FF0000, RGB 255, 0, 0, HSL 0, 100, 50, hex input box "# FF0000". Matches ket-qua.txt line 1.
- Screenshot 008080 (00:24:24, 960x609 JPEG): Color Picker showing a teal swatch labeled 008080, top bar reads HEX #008080, RGB 0, 128, 128, HSL 180, 100, 25, hex input box "# 008080". Matches ket-qua.txt line 2. This is a DIFFERENT hex code from the first screenshot.
- Screenshot FFD700 (00:24:46, 960x609 JPEG): Color Picker showing a gold swatch labeled FFD700, top bar reads HEX #FFD700, RGB 255, 215, 0, HSL 51, 100, 50, hex input box "# FFD700". Matches ket-qua.txt line 3. This is a DIFFERENT hex code from the first two screenshots.
- The 3 screenshots are distinct files (different sha256, different sizes 153440 / 155548 / 157660 bytes), not copies of one image.
- Independent value check: hex-to-RGB conversion and HSL computation (Python colorsys) confirm all 3 RGB triples and all 3 HSL values in ket-qua.txt: #FF0000 HSL(0, 100%, 50%), #008080 HSL(180, 100%, 25%), #FFD700 HSL(51, 100%, 50%).

## Reason

All 3 lines in ket-qua.txt match the key on hex and RGB, and the HSL values match the page display in the screenshots and my independent computation. The 3 screenshots each show a different hex code on the color picker (FF0000 red, 008080 teal, FFD700 gold), each with the correct RGB and HSL shown, so the runner did not reuse one color. The Tier A checker said PASS; my independent verification agrees, with no discrepancy.

Timing note: start 2026-11-26T00:20:14+07:00, end 2026-11-26T00:24:46+07:00 (4 min 32 s); the 3 screenshots are timestamped 00:23:59, 00:24:24, 00:24:46, about 25 s apart, consistent with entering 3 hex codes one by one.

Signed: mochi, scorer 1A, session 70cd99d1-ecef-4d02-9f42-714d7e86ab85.
