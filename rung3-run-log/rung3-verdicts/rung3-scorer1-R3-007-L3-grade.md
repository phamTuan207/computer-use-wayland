# Scorer 1 grade, R3-L3, R3-007

- Session: 70cd99d1-ecef-4d02-9f42-714d7e86ab85 (scorer 1A, Pair A)
- Task: R3-007 (Tier A, position 7, run R3-L3)
- Verdict: PASS
- Scored at: 2026-11-25 21:59:13 +07 (Asia/Ho_Chi_Minh)
- Snapshot: rung3-run-log/rung3-snapshots/R3-007-L3/ at todolist-push commit e73578c8, manifest_sha256 4be235466584890828e249224f0a8700a0f5f2eb783eaa4c609ac90c9d87a7c2, all 8 evidence files hash-OK against manifest.json, manifest gate PASS
- Key file hashes (verified before scoring): docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both match the R3-L3 freeze)
- Tier A checker output (coordinator supplied, aid only, not a substitute for reading the evidence): verdict PASS, reasons empty. I read the evidence myself and verified each item below independently.

## Files read

- rung3-run-log/rung3-snapshots/R3-007-L3/manifest.json (snapshot R3-007-L3, commit e73578c8)
- rung3-run-log/rung3-snapshots/R3-007-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-007-L3/20261125-214834-convert-1.png
- rung3-run-log/rung3-snapshots/R3-007-L3/20261125-214842-convert-2.png
- rung3-run-log/rung3-snapshots/R3-007-L3/20261125-214850-convert-3.png
- rung3-run-log/rung3-snapshots/R3-007-L3/20261125-214858-convert-4.png
- rung3-run-log/rung3-snapshots/R3-007-L3/20261125-214906-convert-5.png
- rung3-run-log/rung3-snapshots/R3-007-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-007-L3/end_time.txt
- docs/rung3-answer-keys.md, R3-007 section only (lines 173-180)
- docs/rung3-answer-keys.json, R3-007 entry only (no allocated entry, null)
- docs/rung3-list-100-tasks.md, section 6, R3-007 task text only

I scored from the snapshot and the key only. I did not read any other scorer's grade or verdict file, did not contact the runner, and did not read any runner log, ledger, or trial report. I did not re-run any conversion on the live site.

## Key (R3-007, Tier A)

5 conversions, input values chosen for this frozen run:
1. 12 km = 7.4565 miles
2. 8 miles = 12.8748 km
3. 7 kg = 15.4324 lb
4. 30 C = 86.0 F
5. 5 L = 1.3209 US gallons

Task text Pass: all 5 conversions, results correct within rounding tolerance 0.01, target unit correct, result file has all 5 conversions, screenshots show all 5 results. Fail: missing conversion, wrong result beyond tolerance, wrong target unit, missing screenshot, or using a different unit conversion site without stating it clearly.

## Evidence

- ket-qua.txt (115B) records all 5 conversions with original value, original unit, result, target unit:
  1. 12 km = 7.4564543068 miles (key 7.4565, diff 0.0000457, within 0.01)
  2. 8 miles = 12.874752 km (key 12.8748, diff 0.000048, within 0.01)
  3. 7 kg = 15.432358353 lb (key 15.4324, diff 0.0000416, within 0.01)
  4. 30 C = 86 F (key 86.0, diff 0)
  5. 5 L = 1.3208602618 US gallons (key 1.3209, diff 0.0000397, within 0.01)
- All 5 screenshots show unitconverters.net (the required site), each showing the matching conversion result in the page's Result line and the From/To fields:
  - convert-1.png: Length Converter, "12 kilometer = 7.4564543068 mile", From 12 kilometer, To 7.4564543068 mile.
  - convert-2.png: Length Converter, "8 mile = 12.874752 kilometer", From 8 mile, To 12.874752 kilometer.
  - convert-3.png: Weight and Mass Converter, "7 kilogram = 15.432358353 pound", From 7 kilogram, To 15.432358353 pound.
  - convert-4.png: Temperature Converter, "30 Celsius = 86 Fahrenheit", From 30 Celsius, To 86 Fahrenheit.
  - convert-5.png: Volume Converter, "5 liter = 1.3208602618 gallon (US)", From 5 liter, To 1.3208602618 gallon (US).
- Categories match the task: 2 length, 1 mass, 1 temperature, 1 volume. All target units are correct. All 5 screenshots are present, one per conversion.
- Timing: start 2026-11-25T21:48:24+07:00, end 2026-11-25T21:49:08+07:00 (44 s). Fast, but the 5 screenshots are timestamped about 8 s apart in sequence (21:48:34, 21:48:42, 21:48:50, 21:48:58, 21:49:06) and each shows the correct result, so the evidence is verified, not assumed. Timing alone is not a fail.
- Minor note (not a fail): ket-qua.txt does not record a formula or conversion ratio per conversion. Task step 4 asks for it only "if the page shows it" (neu trang hien), and the Pass criteria do not require it, so its absence does not change the verdict.

## Reason

All 5 conversions are present with results within the 0.01 rounding tolerance of the key and correct target units, and all 5 screenshots on unitconverters.net show the matching results. My independent read agrees with the Tier A checker output.

Signed: mochi, scorer 1A, session 70cd99d1-ecef-4d02-9f42-714d7e86ab85.
