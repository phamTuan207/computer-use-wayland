# Scorer 1 grade, R3-L3, R3-011

- Session: 70cd99d1-ecef-4d02-9f42-714d7e86ab85 (scorer 1A, Pair A)
- Task: R3-011 (Tier B, position 11, run R3-L3)
- Verdict: INVALID (proposed)
- Scored at: 2026-11-25 23:19:27 +07 (Asia/Ho_Chi_Minh)
- Snapshot: rung3-run-log/rung3-snapshots/R3-011-L3/ at todolist-push commit 67445f75, manifest_sha256 df6d1163774df6c1719fd448b43bdb47257f5d2375e1c321fe0e8e4d9182aa1f, all 6 evidence files hash-OK against manifest.json. Note: manifest gate FAIL is expected here (the drive was blocked before any result existed); the snapshot is the block evidence, not result evidence.
- Key file hashes (verified before scoring): docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both match the R3-L3 freeze)

## Files read

- rung3-run-log/rung3-snapshots/R3-011-L3/manifest.json (snapshot R3-011-L3, commit 67445f75)
- rung3-run-log/rung3-snapshots/R3-011-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-011-L3/block-state.png
- rung3-run-log/rung3-snapshots/R3-011-L3/pill-gone.png
- rung3-run-log/rung3-snapshots/R3-011-L3/result.json
- rung3-run-log/rung3-snapshots/R3-011-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-011-L3/end_time.txt
- docs/rung3-answer-keys.md, R3-011 key section (lines 213-220) and the pre-declared ruling for R3-011, R3-028, R3-036, R3-046 (lines 23-24)
- docs/rung3-list-100-tasks.md, section 1 invalid definition (lines 9-40) and R3-011 task text (lines 373-379)

I scored from the snapshot and the key only. I did not read any other scorer's grade or verdict file, did not contact the runner, and did not read any runner log, ledger, or trial report. I collected independent evidence myself (see below): a read-only cloud-browser check of the same timeanddate.com URL.

## Key (R3-011, Tier B)

5 dates (in this order), correct weekdays: 2024-02-29 Thursday, 2026-01-01 Thursday, 2026-07-04 Saturday, 2026-12-31 Thursday, 2000-02-29 Tuesday. At least 1 Feb 29 leap year date (here 2) and 1 last-day-of-year date. Evidence: 5 result screenshots + ket-qua.txt; the scorer compares the weekdays with the screenshots.

Pre-declared ruling (keys.md lines 23-24): R3-011, R3-028, R3-036, R3-046 all use timeanddate.com. timeanddate.com was still blocked at the curl level (HTTP 403, Cloudflare "Just a moment..." page, checked 2026-11-23 19:23); curl on 2026-11-24 06:10 returned HTTP 200, the block may depend on IP/time, only a browser check can decide. If at run time the site is blocked at the browser level, all 4 tasks are invalid candidates per section 1. If the browser check proves timeanddate.com is blocked (a shared cause for all 4 tasks), the 4 tasks count as 1 invalid event for both caps (total 5, per group 2). Each invalid task still needs 1 backup of the same difficulty; the remaining medium backups are DP-03, DP-06, DP-07 (3 backups for 4 tasks), the 4th task without a backup is removed from the sample without replacement per section 8. Amendment note: the pre-freeze browser check (2026-11-24 14:26 +07) showed timeanddate.com opened normally, not blocked, so the 4 tasks run normally; the cap question was temporarily moot because the site opened.

Section 1 invalid definition: a task is invalid if the service changes its interface, closes, is out of stock, cannot be accessed, shows a bot-check or reCAPTCHA page, or the app on the laptop is missing; the scorer records the task as invalid, not counted in the sample. Max 5 invalid total, max 2 per difficulty group. Each invalid decision needs independent second confirmation from scorer 2 (blind) plus coordinator co-sign.

## Evidence

- ket-qua.txt (235B) records: "BLOCKED: timeanddate calculator did not return a weekday result. markers=[] title='Just a moment...' href=https://www.timeanddate.com/date/weekday.html?year=2026&month=11&day=11 body_head='Just a moment…\n\nRay ID: a601e73fd83ea29d'". No weekday result for any of the 5 dates; no result screenshots exist (the drive was blocked before any result existed).
- result.json (662B) records: task R3-011, landing_url https://www.timeanddate.com/date/weekday.html?year=2026&month=11&day=11, blocked state {title: "Just a moment...", href: same URL, ready: "complete"}, dates: [], markers: []. Tabs before 23, tabs after 23 (no tab flood). The blocked tab was closed after recording (closed_tabs lists the timeanddate URL), pill released 23:08:25.
- block-state.png (1920 x 1200) shows the Zen browser on timeanddate.com displaying the Cloudflare "Just a moment..." challenge page: blue background, timeanddate.com logo, large text "Just a moment...", a "Verify you are human" checkbox with the Cloudflare logo, and "Ray ID: a601e73fd83ea29d". The Ray ID matches ket-qua.txt exactly. The "Computer use active" pill is visible at the top.
- pill-gone.png (1920 x 1200) shows the Zen browser after the pill was released, back on a YouTube tab, with no pill visible. This confirms the runner closed the blocked tab and released control after recording the block.
- Timing: start 2026-11-25T23:06:52+07:00, end 2026-11-25T23:08:27+07:00 (1 min 34 s). The block appeared on the first navigation; the runner did not hammer the site (single navigation, no repeated reloads in the evidence) and did not open many tabs (tab count stable at 23).

## Independent evidence collected by the scorer

- I opened the same URL (https://www.timeanddate.com/date/weekday.html?year=2026&month=11&day=11) in a read-only cloud browser (Environment 1) at 23:18 +07. The weekday calculator result page loaded normally, with no Cloudflare challenge and no error. Page title: "Weekday Calculator – What Day is this Date?". It showed "11 November 2026 is a Wednesday". No sign-in, form submission, date entry, or challenge interaction was performed.
- This shows timeanddate.com is not down site-wide; the block is IP/time/fingerprint-specific, which the ruling explicitly anticipates ("chan co the tuy IP/thoi diem"). It does NOT refute the runner's block at run time in Zen, and it does NOT show the runner caused the block. The runner's block at run time is the exact condition the ruling covers.
- Key sanity check: I verified all 5 weekdays in the frozen key with the system date command (2024-02-29 Thursday, 2026-01-01 Thursday, 2026-07-04 Saturday, 2026-12-31 Thursday, 2000-02-29 Tuesday). All 5 are correct, so the key is not wrong; the invalid is due to the service block, not a key error.

## Reason

The service showed a Cloudflare bot-check page ("Just a moment..." with "Verify you are human", Ray ID a601e73fd83ea29d) at the browser level at run time, so no weekday result could be obtained for any of the 5 dates. This matches the section 1 invalid definition (service shows a bot-check page) and the pre-declared ruling for this exact condition (if at run time the site is blocked at the browser level, the 4 timeanddate tasks are invalid candidates per section 1). The runner did not cause the block (single navigation, no hammering, tab count stable), and the block was recorded clearly in ket-qua.txt with a matching screenshot. This is a proposed INVALID; it needs blind confirmation from scorer 2 and coordinator co-sign per section 1.

Note for the coordinator: per the ruling, if the browser check proves timeanddate.com is blocked (a shared cause for all 4 tasks), the 4 tasks count as 1 invalid event for both caps (total 5, per group 2). This R3-011 verdict is the first confirmation of the pre-declared timeanddate shared-cause event. The coordinator should confirm the event counting and the backup assignment (the sealing commit message names backup DP-06 for R3-011). The run-stop decision, if a further medium invalid event occurs, is the coordinator's and owner's.

Signed: mochi, scorer 1A, session 70cd99d1-ecef-4d02-9f42-714d7e86ab85.
