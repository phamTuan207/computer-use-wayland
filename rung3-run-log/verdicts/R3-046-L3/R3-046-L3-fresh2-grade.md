# R3-046 verdict (Fresh session, Pair B scorer 2) - R3-L3

- Task: R3-046 (Tier B)
- Scorer session: 4ac339a6-4621-4c9a-8b21-612f7469d215
- Verdict: PASS

## Independence declaration

I graded independently from the snapshot and key section only; I did not read scorer 1's verdict or contact the runner.

## Key verification

- docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (matches brief)
- docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8 (matches brief)
- Key criteria applied: section "## R3-046 (Tier B)" plus the R3-011 ruling at the top of the md key. JSON key confirms cities Ha Noi, London, Sydney; date1 2026-12-02; date2 2027-06-02; tier B.
- Criteria: 6 rows (3 cities x 2 dates), each with sunrise, sunset, day length; day-length difference per city (date2 minus date1) computed correctly; ground truth is the 6 result screenshots (values are live at run time on timeanddate.com).

## Snapshot hash verification

- Snapshot: rung3-run-log/rung3-snapshots/R3-046-L3/
- manifest.json manifest_sha256 field: 5ac02800027900a2dc22bd8c2994c603c379331ad2e13d4ce4fe825c1da76054 (matches brief)
- manifest.json file sha256: 791b42995267c1c83459b6ea8440c2f7e4fa0e2d418973536266c4d53372e07f
- Per-file check: all 59 files listed in manifest.json were re-hashed; every file matches its recorded sha256 and size. 0 mismatches, 0 missing, 0 extra files on disk.

## Evidence cross-check (screenshots vs ket-qua.txt)

Each ket-qua.txt row was checked against the day-2 row of the matching timeanddate result screenshot (the expanded row in each screenshot):

| City | Date | Screenshot | Sunrise | Sunset | Day length | ket-qua.txt match |
|---|---|---|---|---|---|---|
| Ha Noi | 2026-12-02 | 20261126-172805-HaNoi-2026-12-02.png | 06:17 | 17:14 | 10:56:38 | yes |
| Ha Noi | 2027-06-02 | 20261126-173038-HaNoi-2027-06-02.png | 05:14 | 18:34 | 13:19:54 | yes |
| London | 2026-12-02 | 20261126-173339-London-2026-12-02.png | 07:45 | 15:54 | 8:09:15 | yes |
| London | 2027-06-02 | 20261126-173537-London-2027-06-02.png | 04:48 | 21:09 | 16:20:30 | yes |
| Sydney | 2026-12-02 | 20261126-173757-Sydney-2026-12-02.png | 05:37 | 19:51 | 14:14:38 | yes |
| Sydney | 2027-06-02 | 20261126-173944-Sydney-2027-06-02.png | 06:51 | 16:54 | 10:02:13 | yes |

Day-length differences (2027-06-02 minus 2026-12-02), recomputed independently:

- Ha Noi: 13:19:54 - 10:56:38 = +2:23:16. ket-qua.txt says +2:23:16. Correct.
- London: 16:20:30 - 8:09:15 = +8:11:15. ket-qua.txt says +8:11:15. Correct.
- Sydney: 10:02:13 - 14:14:38 = -4:12:25. ket-qua.txt says -4:12:25. Correct.

## Block / INVALID consideration

No browser block on timeanddate.com is evidenced anywhere in the snapshot: all 6 result screenshots show fully loaded timeanddate sun tables for the correct city and month, and there is no block-evidence.txt. The R3-011 ruling INVALID path therefore does not apply, and the shared-cause confirmation duty (R3-011/028/036/046 group) is not triggered: shared_cause_confirmed is null in the verdict JSON. Because the verdict is PASS and not INVALID, the epoch-23 infrastructure re-run consideration record for INVALID verdicts is not required; for completeness, no infrastructure failure was observed, so no re-run was needed.

## Verdict reasoning

All 6 required lookups are present as timestamped result screenshots, every value in ket-qua.txt matches its screenshot exactly, and all 3 day-length differences are arithmetically correct. The task meets the Tier B key criteria in full. Verdict: PASS.
