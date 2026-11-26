# R3-036-L3 fresh grade (scorer 2, Pair A)

- Task: R3-036 (Tier B), run R3-L3
- Scorer session: 861775d2-8b6f-4c74-a166-eb38b9c125aa
- Graded at: 2026-11-26T14:06:14+07:00 (Asia/Ho_Chi_Minh)
- Snapshot: rung3-run-log/rung3-snapshots/R3-036-L3 (snapshot commit 36687609)
- Verdict: PASS

## Independence declaration

I graded independently from the snapshot and key section only; I did not read scorer 1's verdict or contact the runner.

## Key verification (before scoring)

- docs/rung3-answer-keys.md sha256: 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 - matches brief.
- docs/rung3-answer-keys.json sha256: 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8 - matches brief. This value is recorded as keyfile_sha256 in the JSON verdict.
- Key section applied: "## R3-036 (Tier B)" plus the R3-011 ruling at the top of the key file (shared timeanddate.com cause for R3-011, R3-028, R3-036, R3-046; browser-level block at run time makes the task an INVALID candidate under list section 1).

## Manifest and per-file hash verification

- Manifest hash recorded: f857cf4f8abcb07288fc142b8d0e0c26dd255dbb69d6d36cb8396769b16ab010 (manifest_sha256 field in manifest.json; matches brief). For transparency, sha256 of the manifest.json file itself is e52743502dd941fc3270e9b2e39e35520bac1c46ae701266e0f0a4ea5990e3b5.
- Every file listed in manifest.json was re-hashed and compared. Result: 14 of 14 OK, no mismatch.

| File | Result |
| --- | --- |
| 20261126-134539-meeting-timetable.jpg | OK (da02c3937dd6f203...) |
| 20261126-134621-worldclock-readings.jpg | OK (9b319d10dc241dc1...) |
| 20261126-134951-worldclock-readings.jpg | OK (82988b081937e759...) |
| 20261126-135323-doc-saved.jpg | OK (c7660c67b7b1b889...) |
| 20261126-135432-doc-reopened.jpg | OK (73304caca1763cf7...) |
| drive-r3036.log | OK (50deecc42011333a...) |
| drive-stdout.log | OK (b677b2a14aae5ee2...) |
| drive-stdout2.log | OK (23dafb41d3dda89c...) |
| drive-stdout3.log | OK (a0564a2caa45f731...) |
| end_time.txt | OK (1c887cb5e0960a1a...) |
| holder-r3036.log | OK (43ac762166f9a6f7...) |
| ket-qua.txt | OK (24509f2507566b94...) |
| probe-ready.json | OK (0777475af4c5aa49...) |
| start_time.txt | OK (c801bdc6f0a9c00b...) |

## Key criteria (R3-036 Tier B, summarized)

- Cities in order: Hanoi (UTC+7), Tokyo (UTC+9), Sydney (UTC+11, AEDT in December).
- Meeting date: Wednesday 2026-12-02. Working hours defined as 09:00-17:00 local.
- Common window: 02:00-06:00 UTC (Hanoi 09:00-13:00, Tokyo 11:00-15:00, Sydney 13:00-17:00).
- Chosen 60-minute meeting: 03:00 UTC, i.e. Hanoi 10:00, Tokyo 12:00, Sydney 14:00 on 2026-12-02; all three inside 09:00-17:00 local.
- Online document with a 3-row table of meeting times per city plus one explanation line stating why the time suits all three (inside working hours of all three, inside the 02:00-06:00 UTC common window); document reopened to check.
- Scorer cross-check: meeting time verified through offset differences and confirmed inside working hours of all three cities.

## Evidence review (snapshot files only)

### City readings - 20261126-134951-worldclock-readings.jpg and ket-qua.txt

- The World Clock screenshot (Thu 2026-11-26, a Thursday - verified) shows Hanoi Thu 13:49, Tokyo Thu 15:49, Sydney Thu 17:49 with the DST asterisk on Sydney. ket-qua.txt records the same three readings and the asterisk meaning.
- Differences: Tokyo +2h vs Hanoi, Sydney +4h vs Hanoi, Sydney +2h vs Tokyo. Consistent with UTC+7 / UTC+9 / UTC+11 (DST). PASS on readings.

### Chosen-slot view - 20261126-134539-meeting-timetable.jpg (plus 20261126-134621-worldclock-readings.jpg)

- The Meeting Planner Results screenshot is set to Day 2, December 2026, with Hanoi / Tokyo / Sydney columns. The row "Wednesday, 2 December 2026, 03:00:00" (UTC) reads Hanoi Wed 10:00, Tokyo Wed 12:00, Sydney Wed 14:00 - exactly the key meeting. 2026-12-02 is a Wednesday (verified).
- Rows 02:00-06:00 UTC are all in the green "General working hours" band (legend visible in 20261126-134621-worldclock-readings.jpg, which also shows the lower timetable rows and the DST asterisk note), matching the key common window 02:00-06:00 UTC (Hanoi 09:00-13:00, Tokyo 11:00-15:00, Sydney 13:00-17:00).
- Offsets read from the UTC column (UTC 03:00 to Hanoi 10:00 = +7, to Tokyo 12:00 = +9, to Sydney 14:00 = +11) match ket-qua.txt. PASS on timetable and offsets.

### Saved online document - 20261126-135323-doc-saved.jpg, 20261126-135432-doc-reopened.jpg, ket-qua.txt

- ket-qua.txt gives the Google Docs URL and the full document content: chosen 60-minute meeting Hanoi Wed 2 Dec 2026 10:00-11:00 (UTC+7), Tokyo 12:00-13:00 (UTC+9), Sydney 14:00-15:00 (UTC+11, DST), plus the explanation line "This time suits all three sides because it falls inside the shared 09:00-17:00 working-hours window (Hanoi 09:00-13:00 = Tokyo 11:00-15:00 = Sydney 13:00-17:00), so every participant joins during normal work hours."
- The reopened-document screenshot (135432) shows the same three rows and explanation line in the live document: "Hanoi - Wed 2 Dec 2026, 10:00-11:00 (UTC+7)", "Tokyo - Wed 2 Dec 2026, 12:00-13:00 (UTC+9)", "Sydney - Wed 2 Dec 2026, 14:00-15:00 (UTC+11, DST)", followed by "This time suits all three sides because it falls inside the shared window (Hanoi 09:00-13:00 = Tokyo 11:00-15:00 = Sydney 13..." and "...participant joins during normal work hours." The right edge of the screenshot clips a few characters, but all three times and the substance of the explanation are legible and match ket-qua.txt word for word. The saved-document screenshot (135323) shows the same content, proving the document persisted and was reopened for checking.
- Note on form: the three rows are presented as three text rows (no visible table gridlines in the screenshots). Content-wise they are the required 3-row table (one row per city, correct times and offsets) plus the required explanation line, and the key scorer check (offset cross-check plus inside-working-hours check) passes on the visible content. This is accepted as meeting the key; the absence of gridlines is not treated as a failure because the key defines the check in content terms.
- Cross-check: Hanoi 10:00-11:00 UTC+7 = UTC 03:00-04:00; Tokyo 12:00-13:00 UTC+9 = UTC 03:00-04:00; Sydney 14:00-15:00 UTC+11 = UTC 03:00-04:00. All three inside 09:00-17:00 local and inside 02:00-06:00 UTC. Each block is 60 minutes. PASS.

### ket-qua.txt

- Cities in order Hanoi, Tokyo, Sydney; meeting date Wednesday 2026-12-02; working hours 09:00-17:00; current readings, offsets, differences, common window, chosen time, explanation, document URL, and screenshot references all present and consistent with the screenshots and the key. PASS.

## Shared-cause statement (required for INVALID-cap counting)

shared_cause_confirmed: false.

The snapshot does NOT evidence a browser block on timeanddate.com, so the shared timeanddate cause (R3-011 group) is NOT proven for this task and INVALID does not apply:

- No block screenshot exists in the snapshot; instead 20261126-134951-worldclock-readings.jpg and 20261126-134539-meeting-timetable.jpg show timeanddate.com fully rendered (World Clock list and Meeting Planner Results) in the browser.
- No block-evidence.txt exists in the snapshot (no wait log, no Ray ID). No Ray ID appears in any snapshot file.
- probe-ready.json shows webdriver false (own_on_navigator false, own_on_proto true, native getter), i.e. the probe passed; it is not block evidence.
- Spot-checked drive log states record blocked false with null ray_id and normal page bodies for timeanddate.com (supporting only; the screenshots alone already prove the site loaded). Curl output was not used as proof either way.

Because there was no block at all, there is no same-cause event to confirm; this task contributes 0 new INVALID cap events on the shared-cause ground and is graded on its merits as PASS.

## Verdict

PASS. All key criteria are met from snapshot evidence: correct cities and offsets, correct common window, correct chosen 60-minute meeting (Hanoi 10:00, Tokyo 12:00, Sydney 14:00 on Wed 2026-12-02, 03:00 UTC), 3-row document plus explanation line saved and reopened, and ket-qua.txt consistent throughout. No browser block occurred, so the pre-declared INVALID candidate condition was not triggered.
