# Scorer 1 grade, R3-L3, R3-010

- Session: 70cd99d1-ecef-4d02-9f42-714d7e86ab85 (scorer 1A, Pair A)
- Task: R3-010 (Tier C, position 10, run R3-L3)
- Verdict: PASS
- Scored at: 2026-11-25 23:05:52 +07 (Asia/Ho_Chi_Minh)
- Snapshot: rung3-run-log/rung3-snapshots/R3-010-L3/ at todolist-push commit d2023919, manifest_sha256 7c0788a7ce58bfbc845f5f830b16ae9717322b49892031469d7e91b9b2b96111, all 7 evidence files hash-OK against manifest.json, manifest gate PASS
- Key file hashes (verified before scoring): docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both match the R3-L3 freeze)

## Files read

- rung3-run-log/rung3-snapshots/R3-010-L3/manifest.json (snapshot R3-010-L3, commit d2023919)
- rung3-run-log/rung3-snapshots/R3-010-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-010-L3/so-do.png (exported PNG, 1157 x 146)
- rung3-run-log/rung3-snapshots/R3-010-L3/20261125-225332-excalidraw.png (board screenshot, 1920 x 1200)
- rung3-run-log/rung3-snapshots/R3-010-L3/scene-final.json (cross-check only, not the evidence of record)
- rung3-run-log/rung3-snapshots/R3-010-L3/result.json (cross-check only, not the evidence of record)
- rung3-run-log/rung3-snapshots/R3-010-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-010-L3/end_time.txt
- docs/rung3-answer-keys.md, Tier C rubric for R3-010 (lines 69-80) and R3-010 key section (lines 206-212)
- docs/rung3-list-100-tasks.md, section 6, R3-010 task text only

I scored from the snapshot and the key only. I did not read any other scorer's grade or verdict file, did not contact the runner, and did not read any runner log, ledger, or trial report. I measured directly on the exported PNG (so-do.png) with an independent pixel analysis, as the Tier C rubric requires; the scene-final.json and result.json were used only as a cross-check, not as the evidence of record. The keys.json has no R3-010 entry (the key lives in the md file and the rubric).

## Key (R3-010, Tier C)

Rubric: the scorer opens the exported PNG and measures directly on the image. The center of each shape is the midpoint of that shape. The exported image width is W pixels. Rectangle: center x in [0, 33% W], tolerance 50 px, text must read "Bat dau". Circle: center x in [33, 66% W], tolerance 50 px, text must read "Xu ly"; the circle is drawn with the O key holding Shift while dragging, a free-dragged ellipse (not holding Shift) counts as the wrong shape type. Diamond: center x in [66, 100% W], tolerance 50 px, text must read "Ket thuc". Arrow 1: rectangle to circle, overall direction left to right, tolerance 30 degrees. Arrow 2: circle to diamond, overall direction left to right, tolerance 30 degrees. The scorer records the measured x of all 3 centers (pixels and % W) and the measured direction of both arrows (degrees) in the grade file. PASS: all 3 shapes correct type, correct text, centers in the correct regions (with tolerance), all 2 arrows correct direction (with tolerance). FAIL: missing shape, wrong shape type, wrong text, center outside region beyond tolerance, missing arrow, arrow reversed beyond tolerance, file not PNG.

Task text Pass: PNG file exists and opens, all 3 shapes correct type and correct text, all 2 arrows correct direction within 30 degrees, rectangle center in the left part (x 0-33% of exported image width), circle center in the middle (x 33-66%), diamond center in the right part (x 66-100%), 50 pixel tolerance, result file has all items, screenshot shows the board.

## Evidence

- ket-qua.txt (283B) records: Page title "Excalidraw Whiteboard"; shapes 1. Rectangle "Bat dau", 2. Ellipse (circle) "Xu ly", 3. Diamond "Ket thuc"; arrows 1. "Bat dau -> Xu ly (rectangle right edge to circle left edge)", 2. "Xu ly -> Ket thuc (circle right edge to diamond left edge)"; exported PNG "so-do.png". All items present.
- so-do.png is a valid PNG, 1157 x 146, opens fine. W = 1157 px.
- Board screenshot 20261125-225332-excalidraw.png shows the Excalidraw whiteboard at excalidraw.com (tab "Excalidraw Whiteboard") with the same 3 shapes and 2 arrows, matching the exported PNG.

## Measurements on the exported PNG (so-do.png), measured directly by pixel analysis

- Rectangle "Bat dau": left edge column x = 11, right edge column x = 178. Center x = 94.5 px = 8.2% of W. Region [0, 33%] = [0, 382] px. Inside, well within the 50 px tolerance. Text "Bat dau" is readable in the PNG.
- Circle "Xu ly": center x = 576.0 px (measured at row y = 40) and 576.5 px (at row y = 110), so 576 px = 49.8% of W. Region [33, 66%] = [382, 764] px. Inside, well within the 50 px tolerance. Text "Xu ly" is readable in the PNG. Circle check: height via center column x = 576 is 130 px (top y = 7, bottom y = 136); chord widths at y = 40 (113 px) and y = 110 (106 px) are consistent with a circle of radius about 65 px (diameter about 130 px). Width equals height within stroke width, so it is a circle, not a free-dragged ellipse. The scene data cross-check agrees (ellipse w = 125, h = 125).
- Diamond "Ket thuc": left vertex x = 972, right vertex x = 1142. Center x = 1057.0 px = 91.4% of W. Region [66, 100%] = [764, 1157] px. Inside, well within the 50 px tolerance. Text "Ket thuc" is readable in the PNG (split across two lines, "Ket" / "thuc", same as on the board).
- Arrow 1 (rectangle to circle): shaft centerline y = 73.0 at x = 200 and y = 73.4 at x = 490. Direction angle = 0.07 degrees (left to right, horizontal). Within the 30 degree tolerance. Scene cross-check: 0.18 degrees.
- Arrow 2 (circle to diamond): shaft centerline y = 73.0 at x = 650 and y = 74.8 at x = 950. Direction angle = 0.34 degrees (left to right, horizontal). Within the 30 degree tolerance. Scene cross-check: 0.52 degrees.

## Reason

All 3 shapes are the correct type with the correct readable text, all 3 centers are inside their required regions (rectangle 8.2%, circle 49.8%, diamond 91.4% of W), the middle shape is a true circle (width equals height), and both arrows run left to right and horizontal (0.07 and 0.34 degrees, within the 30 degree tolerance). The exported file is a valid PNG, ket-qua.txt has all items, and the board screenshot shows the same drawing.

Timing note: start 2026-11-25T22:52:47+07:00, end 2026-11-25T22:54:02+07:00 (1 min 15 s). Fast, but every item was independently measured on the exported PNG, so timing alone is not a fail.

Signed: mochi, scorer 1A, session 70cd99d1-ecef-4d02-9f42-714d7e86ab85.
