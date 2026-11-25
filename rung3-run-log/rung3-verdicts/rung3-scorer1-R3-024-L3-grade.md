# Scorer 1 grade, R3-L3, R3-024

- Session: 70cd99d1-ecef-4d02-9f42-714d7e86ab85 (scorer 1A, Pair A)
- Task: R3-024 (Tier B, position 21, run R3-L3)
- Verdict: INVALID (proposed, needs blind confirmation from scorer 2 and coordinator co-sign per section 1)
- Scored at: 2026-11-26 03:32:08 +07 (Asia/Ho_Chi_Minh)
- Snapshot: rung3-run-log/rung3-snapshots/R3-024-L3/ at todolist-push commit b46e8c03, manifest_sha256 0aa2cb239c8c5b75d900c42fbe1fc7559836729dcc6902086eb5b06d4f95c02d, all 4 evidence files hash-OK against manifest.json, manifest gate PASS (mechanical)
- Key file hashes (verified before scoring): docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both match the R3-L3 freeze)

## Files read

- rung3-run-log/rung3-snapshots/R3-024-L3/manifest.json (snapshot R3-024-L3, commit b46e8c03)
- rung3-run-log/rung3-snapshots/R3-024-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-024-L3/blocked-cloudflare-20261126-032300.png
- rung3-run-log/rung3-snapshots/R3-024-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-024-L3/end_time.txt
- docs/rung3-answer-keys.md, R3-024 key section (lines 307-312)
- docs/rung3-list-100-tasks.md, section 6, R3-024 task text (lines 438-442)
- docs/rung3-list-100-tasks.md, section 1, invalid rule (line 34)

I scored from the snapshot and the key only. I did not read any other scorer's grade or verdict file, did not contact the runner, and did not read any runner log, ledger, or trial report. I read the screenshot directly (including an enlarged crop of the Ray ID line) and collected my own independent evidence with a read-only cloud-browser check of the same search (see below). I also checked the public sealing-commit history only to determine which medium backups are already used, for the backup note at the end.

## Key (R3-024, Tier B)

3 keywords to search on openverse.org, filter only reusable images (in this order): 1. "mountain lake" 2. "city bicycle" 3. "old library". Each image records: image name, author, specific license, original link. All 3 images must have a reuse-allowed license. Name, author, license, link are live at run time; the truth is the detail-page screenshot of each image. Scoring evidence: 3 detail-page screenshots + ket-qua.txt. The scorer cross-checks against the screenshots. Only record links, do not download images to the machine.

Section 1 invalid rule (line 34): if the service changes interface, closes, runs out of stock, cannot be accessed, shows a bot-check or reCAPTCHA page, or the app on the laptop is missing, the scorer records the task as invalid, not counted in the sample. Max 5 invalid total, max 2 per difficulty group (medium, hard, very hard). Every invalid decision needs independent second confirmation from scorer 2, who sees only the invalid evidence and reason, not scorer 1's decision, before confirming. When a task is invalidated during the run, the scorer takes the FIRST UNUSED backup in the list with the same difficulty, in that fixed order.

## Evidence

- ket-qua.txt (2629B) records the task (Openverse image search for 3 keywords in order, images only, reuse-allowed filter, record first image of each, screenshots of the 3 detail pages, links only, no downloads) and the steps done in Zen (new tab, ws2): opened https://openverse.org/ (homepage loaded, title "Openly Licensed Images, Audio and More | Openverse"); selected content type "Images" via the search-type popover (verified: button label "Images", radio Images aria-checked=true); typed "mountain lake" in the search box (read-back verified); clicked Search. Browser navigated to https://openverse.org/search/image?q=mountain+lake. The results page never loaded. Cloudflare showed: title "Just a moment...", heading "openverse.org", text "Performing security verification - This website uses a security service to protect against malicious bots. This page is displayed while the website verifies you are not a bot." Ray ID: a6035b302a2fb39e. The runner waited 60 seconds and re-read the page: still the same Cloudflare verification page (same Ray ID), checked again at 2026-11-26T03:23+07:00. Per drive rules (stop on bot check, do not hammer), no reload, no challenge interaction, and no further searches were attempted. Keywords 2 and 3 were not searched because the service block applies to the search endpoint. All 3 rows: NOT OBTAINED. Original links: none obtained. No images downloaded. The reuse filter could not be applied or verified because it lives on the results page, which never loaded. Nothing was fabricated.
- Screenshot blocked-cloudflare-20261126-032300.png: the Cloudflare "Just a moment..." page on openverse.org, "Performing security verification", "This website uses a security service to protect against malicious bots. This page is displayed while the website verifies you are not a bot.", "Verify you are human" checkbox with the Cloudflare logo, "Performance and Security by Cloudflare". The tab bar shows only 2 tabs (openverse.org, "Just a moment..."), so there is no many-tabs abuse. The runner made a single search, waited, and stopped; no hammering, no reload, no challenge interaction.
- The runner did not cause the block: one search only, no reload, no challenge interaction, a 60-second wait with a re-read, then stopped per the drive rules.
- No Pass criterion is met: there are no image rows, no names, authors, licenses, or links, and no detail-page screenshots. Nothing was fabricated to fill the gap. This is not a FAIL either: the failure is a service-side bot-check page, which section 1 defines as invalid, not a runner error.

## Ray ID discrepancy (documented for the coordinator/auditor)

The Ray ID in the screenshot differs from the one in ket-qua.txt. I read the screenshot's Ray ID from an enlarged crop of the footer line: "Ray ID: a6035e3aee11b39e". ket-qua.txt records "Ray ID: a6035b302a2fb39e" (the assignment states the same value). The two do not match. The most plausible explanation is that Cloudflare re-issued the challenge with a new Ray ID during the 60-second wait / auto-retry, so the Ray ID at screenshot time (03:23:00) differs from the one at first sighting (about 03:21); the runner's note that it was the "same Ray ID" at the re-check is therefore not supported by the screenshot, or the runner mis-transcribed the first value. This discrepancy is in a recorded identifier only. It does not change the verdict: the screenshot itself proves a Cloudflare bot-check page blocked the search results page, which is what section 1 requires.

## Independent evidence collected by me

Read-only cloud-browser check (cloud browser, Environment 2, 03:31-03:31 +07, under 1 minute, single navigation, no CAPTCHA encountered or solved): I opened https://openverse.org/search/image?q=mountain+lake exactly once (after first opening https://openverse.org, which also showed the same Cloudflare verification). The search results page did NOT load: the page showed the Cloudflare "Just a moment..." verification ("openverse.org", "Performing security verification", "This website uses a security service to protect against malicious bots...", "Verifying..." with a Cloudflare widget), Ray ID a6036b222c2c7eb7, "Performance and Security by Cloudflare". No image results, no result count, no first result title could be observed. Unlike R3-011 and R3-022, where the same service loaded normally from the cloud browser, here Openverse is blocked in BOTH the runner's Zen environment AND the cloud browser, with a different Ray ID in each. This shows the block is broader than the runner's environment: it is a service-side Cloudflare block on Openverse, not caused by the runner and not specific to the runner's IP.

## Reason

The service showed a bot-check page (Cloudflare "Just a moment...", "Performing security verification") on the search results page, which section 1 defines as invalid; the runner made a single search, waited 60 seconds, and stopped per the rules, so the runner did not cause the block; and my independent check shows the same search is blocked in a second, independent environment too, confirming a service-side block. No result could be obtained, so no Pass criterion is met, and the failure is a service-side block, not a runner error, so it is not a FAIL. Proposed INVALID, needs blind confirmation from scorer 2 and coordinator co-sign per section 1.

Cap and backup note: R3-024 is medium difficulty ("do kho: trung binh"). The medium group already has 2 invalids (R3-011 event, replaced by DP-06, and R3-047, replaced by DP-03), which is AT the group cap of 2. A 3rd medium invalid during the run STOPS the run per the pre-run rule, and the owner decides. I state this as a consequence for the coordinator/owner; it did not influence the verdict, which follows from the evidence alone. Total invalids would become 4 (R3-011 event, R3-047, R3-022, R3-024), within the total cap of 5. Per section 1, the sealing decision names the first unused medium backup: DP-07 (DP-03 was used for R3-047, DP-06 was used for R3-011, both confirmed in the public sealing-commit history; DP-07 is the last unused medium backup).

Timing note: start 2026-11-26T03:10:54+07:00, end 2026-11-26T03:24:32+07:00 (13 min 38 s), within the 30-min task timeout; the block was first seen about 03:21, re-checked 03:23, screenshot at 03:23:00, all inside the run window.

Signed: mochi, scorer 1A, session 70cd99d1-ecef-4d02-9f42-714d7e86ab85.
