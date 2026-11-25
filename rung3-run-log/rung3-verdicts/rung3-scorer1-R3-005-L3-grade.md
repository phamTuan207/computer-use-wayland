# Scorer 1 grade, R3-L3, R3-005

- Session: 70cd99d1-ecef-4d02-9f42-714d7e86ab85 (scorer 1A, Pair A)
- Task: R3-005 (Tier B, position 5, run R3-L3)
- Verdict: PASS
- Scored at: 2026-11-25 21:28:11 +07 (Asia/Ho_Chi_Minh)
- Snapshot: rung3-run-log/rung3-snapshots/R3-005-L3/ at todolist-push commit ac6820d7, manifest_sha256 f4f7fa95e08d6a63e2f6544d77cf73bbdac9272dd64a64f4b7003a0d155ae4ed, all 7 evidence files hash-OK against manifest.json, manifest gate PASS
- Key file hashes (verified before scoring): docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both match the R3-L3 freeze)

## Files read

- rung3-run-log/rung3-snapshots/R3-005-L3/manifest.json (snapshot R3-005-L3, commit ac6820d7)
- rung3-run-log/rung3-snapshots/R3-005-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-005-L3/qr-1.jpg
- rung3-run-log/rung3-snapshots/R3-005-L3/qr-2.jpg
- rung3-run-log/rung3-snapshots/R3-005-L3/qr-3.jpg
- rung3-run-log/rung3-snapshots/R3-005-L3/20261125-211611-decode.png
- rung3-run-log/rung3-snapshots/R3-005-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-005-L3/end_time.txt
- docs/rung3-answer-keys.md, R3-005 section only (lines 159-163)
- docs/rung3-answer-keys.json, R3-005 entry only (allocated links)
- docs/rung3-list-100-tasks.md, section 6, R3-005 task text only

I scored from the snapshot and the key only. I did not read any other scorer's grade or verdict file, did not contact the runner, did not re-run the QR generation or decoding on the live sites, and did not read any runner log, ledger, or trial report. I decoded the 3 QR image files myself with OpenCV (cv2.QRCodeDetector) as the key allows ("Nguoi cham giai ma lai 1 ma bat ky de kiem tra neu can"); I decoded all 3.

## Key (R3-005, Tier B)

3 original links (in this order): 1. https://example.com 2. https://en.wikipedia.org/wiki/Computer 3. https://go.dev/doc/install. Each decoded link must match its original link exactly. 3 QR image files in JPG format. Evidence: 3 QR image files + ket-qua.txt with 3 pairs of original and decoded links.

## Evidence

- ket-qua.txt (252B) records 3 pairs: Link 1 Original https://example.com, Decoded https://example.com; Link 2 Original https://en.wikipedia.org/wiki/Computer, Decoded https://en.wikipedia.org/wiki/Computer; Link 3 Original https://go.dev/doc/install, Decoded https://go.dev/doc/install. All 3 pairs match.
- The 3 QR files are all valid JPEG images (JFIF 1.01, baseline, 300x300, 1 component): qr-1.jpg (22946B), qr-2.jpg (33611B), qr-3.jpg (23265B). All 3 present, all JPG as required.
- I independently decoded all 3 QR files with OpenCV: qr-1.jpg decodes to https://example.com, qr-2.jpg to https://en.wikipedia.org/wiki/Computer, qr-3.jpg to https://go.dev/doc/install. All 3 match the key's links and ket-qua.txt exactly (3/3).
- The decode screenshot 20261125-211611-decode.png shows the ZXing Decoder Online page (zxing.org) with "Decode Succeeded" for https://go.dev/doc/install (Raw text, Barcode format QR_CODE, Parsed Result Type URI, Parsed Result https://go.dev/doc/install). The tab list shows "QR Code Generator" tabs and "ZXing Decoder Online" tabs, consistent with the required services (qr-code-generator.com and zxing.org). The key requires 3 QR files + ket-qua.txt as evidence, not 3 decode screenshots, so the single decode screenshot is sufficient supplementary evidence.
- Timing: start 2026-11-25T21:00:44.664609+07:00, end 2026-11-25T21:17:33.743138+07:00 (16 min 49 s), plausible. No timing red flag.

## Reason

All 3 QR image files are present in JPG format, each independently decodes to exactly its original link (verified by my own decoding of all 3 codes plus the runner's ZXing screenshot), and ket-qua.txt has all 3 pairs with no pair wrong.

Signed: mochi, scorer 1A, session 70cd99d1-ecef-4d02-9f42-714d7e86ab85.
