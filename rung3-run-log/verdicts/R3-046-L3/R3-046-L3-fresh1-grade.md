# R3-046-L3 verdict (scorer 1, Pair B, fresh session)

- Task: R3-046 (Tier B), run R3-L3
- Verdict: PASS
- Scorer session: 69d28ac3-8aca-4b97-b9a9-6be82865e065
- Graded at: 2026-11-26T17:52:10+07:00
- Snapshot commit: 0bd17c3e (snapshot sealed in 95792534, PNGs force-added in 96b2e6f7)
- Snapshot dir: rung3-run-log/rung3-snapshots/R3-046-L3

## Hash verification

- manifest_sha256 (from manifest.json): 5ac02800027900a2dc22bd8c2994c603c379331ad2e13d4ce4fe825c1da76054
- Every one of the 59 files listed in manifest.json was re-hashed with sha256; 0 mismatches.
- Key md sha256: 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (matches brief)
- Key json sha256: 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8 (matches brief)

## Key criteria (section ## R3-046 (Tier B))

3 cities (Ha Noi, London, Sydney), 2 dates (2026-12-02 and 2027-06-02), 6 rows; each row records sunrise, sunset, day length. Day-length difference per city (date 2 minus date 1) computed correctly. Values are live at run time on timeanddate.com; the 6 result screenshots are the ground truth. Evidence: 6 result screenshots + ket-qua.txt.

## Per-row comparison (ket-qua.txt vs screenshot)

- Ha Noi 2026-12-02 (20261126-172805-HaNoi-2026-12-02.png): sunrise 06:17, sunset 17:14, day length 10:56:38. Matches ket-qua.txt exactly.
- Ha Noi 2027-06-02 (20261126-173038-HaNoi-2027-06-02.png): sunrise 05:14, sunset 18:34, day length 13:19:54. Matches.
- London 2026-12-02 (20261126-173339-London-2026-12-02.png): sunrise 07:45, sunset 15:54, day length 8:09:15. Matches.
- London 2027-06-02 (20261126-173537-London-2027-06-02.png): sunrise 04:48, sunset 21:09, day length 16:20:30. Matches.
- Sydney 2026-12-02 (20261126-173757-Sydney-2026-12-02.png): sunrise 05:37, sunset 19:51, day length 14:14:38. Matches.
- Sydney 2027-06-02 (20261126-173944-Sydney-2027-06-02.png): sunrise 06:51, sunset 16:54, day length 10:02:13. Matches.

## Day-length differences (recomputed)

- Ha Noi: 13:19:54 - 10:56:38 = +2:23:16. Correct.
- London: 16:20:30 - 8:09:15 = +8:11:15. Correct.
- Sydney: 10:02:13 - 14:14:38 = -4:12:25. Correct.

## Block check

No browser block on timeanddate.com is evidenced: all 6 screenshots show the normal calculator pages with the correct city and month tables, and coordinator-report.txt records no bot-check/block and no block-evidence.txt. INVALID does not apply, so the infrastructure re-run consideration record is not required for this verdict.

## Independence declaration

I graded independently from the snapshot and key section only; I did not read scorer 2's verdict or contact the runner.
