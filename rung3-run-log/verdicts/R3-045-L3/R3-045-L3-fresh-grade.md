# R3-045-L3 fresh grade (scorer 2, Pair B)

- Task: R3-045 (Tier B), run R3-L3
- Scorer session: 501248a2-7704-4aec-86b9-b9e3beef2fa6
- Graded at: 2026-11-26T15:13:58+07:00 (Asia/Ho_Chi_Minh)
- Snapshot: rung3-run-log/rung3-snapshots/R3-045-L3 (snapshot commit cfc1e63c)
- Verdict: INVALID

## Independence declaration

I graded independently from the snapshot and key section only; I did not read scorer 1's verdict or contact the runner.

## Key verification (before scoring)

- docs/rung3-answer-keys.md sha256: 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 - matches brief.
- docs/rung3-answer-keys.json sha256: 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8 - matches brief. This value is recorded as keyfile_sha256 in the JSON verdict.
- Key section applied: "## R3-045 (Tier B)" in docs/rung3-answer-keys.md (line 419). The JSON key file carries only the tier entry for this task (R3-045: B); Tier B task bodies live in the markdown key.
- List rules applied with the key: docs/rung3-list-100-tasks.md section 1 invalid definition and section 6 R3-045 steps, pass and fail lines.

## Manifest and per-file hash verification

- Manifest hash recorded: ae8b7299f91b2c86c6939ed77d9c54b518e45e0fb9462aa3b8c11c7a86e55de1 (manifest_sha256 field in manifest.json; matches brief). For transparency, sha256 of the manifest.json file itself is 9fda51883629c9245881d80d208ea51b77413e040c7a445bb00dea186a261156.
- Every file listed in manifest.json was re-hashed and compared. Result: 8 of 8 OK, no mismatch.

| File | Result |
| --- | --- |
| 20261126-145853-serp.jpg | OK (08a8519714a943d7...) |
| 20261126-150806-block.jpg | OK (907a5590c2a8e8cf...) |
| block-evidence.txt | OK (3ed6df4dd3ee0fd4...) |
| end_time.txt | OK (fb5cb8f9fd339071...) |
| holder.log | OK (a47ffb54840c2f78...) |
| pill-gone.png | OK (58d5bddc28706fa3...) |
| probe-ready.json | OK (43f08edc5e315b16...) |
| start_time.txt | OK (a3df62d6749a4687...) |

## Key criteria (R3-045 Tier B, summarized)

- Three source image URLs: https://picsum.photos/seed/r3a/400/300 , https://picsum.photos/seed/r3b/400/300 , https://picsum.photos/seed/r3c/400/300 .
- Delay per frame: 50 (500 ms). Produced GIF has 3 frames. File: anh-dong.gif.
- Scoring evidence: anh-dong.gif plus ket-qua.txt plus screenshots of the GIF maker page and frame count. The scorer opens the GIF file and counts frames and checks the delay.
- List pass line (section 6): GIF file exists, has 3 frames, each frame has delay 50, result file complete, screenshots show the GIF maker page and frame count.
- List fail line (section 6): missing frame, wrong delay, file is not a GIF, or a different GIF maker page was used without recording it.
- List invalid definition (section 1): if the service changes its interface, closes, is out of stock, is inaccessible, shows a bot check page or reCAPTCHA, or the app is missing on the laptop, the scorer marks the task invalid and it is excluded from the sample.

## Evidence review (snapshot files only)

### Entry to the correct service - 20261126-145853-serp.jpg

- The screenshot shows a DuckDuckGo results page for a GIF maker search. The first result is the Free Online GIF Maker at ezgif.com/maker, the service named in list step 1. Entry was through search results, and the correct service was selected. No wrong-service use is evidenced.

### Block at the URL upload stage - 20261126-150806-block.jpg and block-evidence.txt

- 20261126-150806-block.jpg shows the ezgif Animated GIF Maker page with a red banner reading: "The HTTP request has failed. The URL may be incorrect, or the remote server has blocked our access. Please download the file to your computer and upload it manually!" The file area shows "No files selected" and the URL field is back to its empty placeholder, consistent with a failed submit that returned to the maker page. No frames, no delay controls with values, and no result GIF are visible.
- block-evidence.txt records the same event in text: stage "URL upload (source image 1)", first block observation after the visible Upload files action, page title "Free Online GIF Maker", page URL https://ezgif.com/maker?err=http , no Ray ID shown, and the identical visible banner text. It also records a 60000 ms wait after observing the block, then the block screenshot capture. The screenshot file named in block-evidence.txt matches the snapshot block screenshot, and its sha256 in block-evidence.txt (907a5590c2a8e8cf...) matches the re-hashed snapshot file.
- Together the screenshot and the text record evidence a service-side fetch failure at list step 2 (enter the three picsum URLs and press Upload): the ezgif server could not fetch the remote source image and returned err=http. Steps 3 to 6 (set delay 50, make the GIF, download anh-dong.gif, write ket-qua.txt) could not be reached through the prescribed URL path.
- Caveat recorded for honesty: the snapshot contains no pre-submit screenshot showing the filled URL field, so the exact characters entered cannot be re-read from the snapshot. The ruling below rests on the ezgif err=http service response itself plus the stage record in block-evidence.txt, not on any runner report text. No snapshot file shows a malformed URL, a wrong service, or a fabricated result.

### Required outputs absent - manifest.json inventory

- manifest.json lists exactly 8 files (two screenshots, block-evidence.txt, holder.log, probe-ready.json, start_time.txt, end_time.txt, pill-gone.png). There is no anh-dong.gif to open, so frame count and per-frame delays cannot be checked. There is no ket-qua.txt. There are no maker or result screenshots showing 3 frames or delay 50.
- On end state alone the pass criteria are not met. The question for this grade is therefore invalid versus fail, decided in the next section. Absence of the GIF is the expected consequence of the step 2 block, not by itself proof of runner error.

### Run bounds and session state - start_time.txt, end_time.txt, holder.log, probe-ready.json, pill-gone.png

- start_time.txt: 2026-11-26T14:54:14+07:00. end_time.txt: 2026-11-26T15:09:37+07:00. The drive ran about 15 minutes, inside the 30 minute task timeout in list section 1. No timeout failure applies.
- probe-ready.json and holder.log show the session probe passed (webdriver false) and a normal sequence of page evaluations ending with a clean session close. They are session records only and are not used as task evidence either way.
- pill-gone.png shows the desktop after cleanup with no task content. It confirms teardown only.

## Invalid ruling (list section 1)

INVALID applies, for these snapshot-grounded reasons:

- The prescribed function was inaccessible at run time. List step 2 requires ezgif to fetch the three picsum source URLs server-side. The ezgif response evidenced in 20261126-150806-block.jpg and block-evidence.txt (maker?err=http, "remote server has blocked our access") is a service-side fetch failure: the maker page loaded, but its URL-fetch path could not retrieve the source image. Under the section 1 definition this is the service being inaccessible for the required operation, the same family as a closed or unreachable service. The task therefore cannot be scored on its GIF merits.
- The block occurred before any scorable output could exist, at source image 1 of step 2. Delay setting, GIF creation, download, and ket-qua.txt (steps 3 to 6) were unreachable through the prescribed path. Scoring this as FAIL for a missing GIF would punish the runner for a service failure outside its control, which section 1 exists to prevent.
- No fail-line condition is evidenced. The fail line covers a missing frame in a produced GIF, a wrong delay, a non-GIF file, or silent use of a different maker page. None of these is present: no GIF was produced at all, and both screenshots show the correct ezgif service. The ezgif banner suggestion to download and upload manually is not a step in the frozen list for R3-045, and list section 8 directs that a non-working service makes the task invalid rather than switching method or service mid-run. The scorer does not invent a fallback the list does not contain.
- The alternative cause in the ezgif banner ("URL may be incorrect") was considered. The snapshot contains no evidence of an incorrect URL entry, while it does contain a service err=http response recorded with stage, page URL, wait log, and a matching screenshot hash. Judged strictly from snapshot files, the evidenced event is a service fetch failure. If a future review produced pre-submit evidence of a mistyped URL, that would be new evidence outside this snapshot; on this snapshot the invalid ruling stands.

## Shared-cause statement (for INVALID-cap counting)

shared_cause_confirmed: false.

R3-045 has no pre-declared shared-cause group in the key file (the shared groups concern other services). This invalid event is a standalone ezgif server-side fetch failure for picsum URLs, evidenced only in this snapshot. It counts as one invalid event for this task alone and confirms no shared cause with any other task.

## Verdict

INVALID. The snapshot evidences a service-side block at the ezgif URL-upload stage (20261126-150806-block.jpg plus block-evidence.txt, maker?err=http fetch failure on source image 1), which prevented the prescribed steps from producing anh-dong.gif (3 frames, delay 50 each) or ket-qua.txt. Per the list section 1 invalid definition the task is excluded from the sample rather than failed. All 8 snapshot files verified against manifest ae8b7299f91b2c86c6939ed77d9c54b518e45e0fb9462aa3b8c11c7a86e55de1, and both key hashes verified before scoring.
