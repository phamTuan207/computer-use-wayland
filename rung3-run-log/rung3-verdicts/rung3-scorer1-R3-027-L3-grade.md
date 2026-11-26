# R3-027-L3 — Scorer 1 grade

- Session: 70cd99d1-ecef-4d02-9f42-714d7e86ab85
- Task: R3-027, Tier B, position 23, run R3-L3 (FCC lane)
- Scored at: 2026-11-26T07:21:49+07:00
- Verdict: INVALID (proposed)
- Snapshot: rung3-run-log/rung3-snapshots/R3-027-L3/ on todolist-push 5a501b64, manifest_sha256 be4791f1834df6badf4494cea81ee9351af497c92a8dec9b0703e3b4449582ff, gate FAIL (ket-qua.txt missing, expected for a blocked drive per the sealing commit)
- Key hashes verified before scoring: docs/rung3-answer-keys.json 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, docs/rung3-answer-keys.md 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both match freeze)
- Files read: 20 (17 snapshot files: manifest.json, brief-report.txt, start_time.txt, end_time.txt, 2 screenshots, act1-7.json, probe-ready.json, req-serp1.json, holder-pid.txt, holder-task.log; plus keys.md R3-027 section and section 1, keys.json R3-027 entry, list section 6 R3-027)
- Timing: start 2026-11-26T06:55:53+07:00, end 2026-11-26T07:15:51+07:00 (19 min 58 s), within the 30-min timeout

## Key (keys.md R3-027 section + JSON allocated.R3-027)

- 3 test usernames in order: rung3alpha01, rung3bravo02, rung3charlie03 (12/12/14 chars, within all 5 platforms' limits).
- 5 platforms per username: GitHub, X (Twitter), Instagram, YouTube, Reddit. Each records available, taken, or 'undetermined' (undetermined still counts as pass).
- Conclusion: which username is available on all 5 platforms if any, or record clearly that none is.
- Results are live at run time; truth is the screenshot of each username's results.
- Scoring evidence: 3 result screenshots + ket-qua.txt. Scorer cross-checks against the screenshots.
- Pre-freeze check note (2026-11-24): all 3 usernames already have users on X; the other 4 platforms are for the runner to check at run time.

## Evidence (snapshot)

- brief-report.txt (BLOCKED-FINALIZED): holder start 06:55:53, pill acquired 06:55:57 (FCC:22399, visible=true), holder launched 06:56:03 (PID 2331815), ready.json received 06:56:05, Zen address bar typed "namechk" and Return (DuckDuckGo SERP), clicked first SERP result to namechk.com (URL https://namechk.com/, title "Namechk: Username & Domain Name Checker"), typed "rung3alpha01" into the namechk search field, clicked Search, at 07:10:51 the captcha gate appeared, search submitted but NO results loaded, page stayed on https://namechk.com/homepage (blocked). Evidence screenshot saved, STOP per bot-check rule (no hammering, no captcha solve).
- Screenshot 20261126-071051-hcaptcha-blocked.png (07:10:51): namechk.com homepage loaded, search field contains "rung3alpha01", and below it a reCAPTCHA "I'm not a robot" checkbox (unchecked) with the reCAPTCHA logo. No results below. See correction note 1: the widget is reCAPTCHA, not hCaptcha.
- Screenshot 20261126-071620-pill-gone.png (07:16:20, after end_time): browser on a blank Zen start page, namechk tab closed (post-run cleanup; holder log shows session ended 07:16:11). The "Computer use active" pill is visible, so the filename is a misnomer; what is gone is the namechk tab, not the pill. Not material to the verdict.
- act1-7.json: click address bar, Ctrl+l + type "namechk" + Enter, click SERP result, clicks, type "rung3alpha01", click Search. Consistent with the brief-report timeline.
- probe-ready.json: webdriver false, own_on_proto true, own_on_navigator false, get_name "get webdriver", get_tostring "function () { [native code] }", shim_sha256 bb49ff3f974a0534445fa5bb8eac48b47a378f39d944706b10118d5ff9d630b8. The preload shim hid navigator.webdriver, so the block was not triggered by the webdriver signal.
- holder-task.log: shim pinned, session, preload installed, context created, descriptor probe (webdriver false), probe_ok, then a series of rpc evaluate calls (serp-1/2/4 ok:false, serp-3/5/6/7/8/9 and p1-p11 ok:true), preload_removed, context_closed, session_ended, done at 07:16:11. Spans the run window.
- ket-qua.txt: MISSING (no results produced). The sealing commit states this is expected for a blocked drive. The block itself IS recorded in brief-report.txt and in the 07:10:51 screenshot. This is a recording-location difference, not a failure to record; see correction note 3.

## Independent verification (scorer-collected)

- Read-only cloud-browser check, Environment 2, 07:21 +07, single navigation to https://namechk.com/, no reload, no typing, no search submitted, no challenge interaction.
- Result: homepage loaded normally (title "Namechk: Username & Domain Name Checker", heading "CHECK OVER 30 DOMAINS AND MORE THAN 90 SOCIAL MEDIA ACCOUNTS", search form visible), no captcha widget visible on initial load. Page text itself states a CAPTCHA is part of running a search ("Enter your brand, business or username idea in the search bar, complete the CAPTCHA and run the search").
- Conclusion: the gate is environment-specific (IP/time/fingerprint), the same pattern as R3-011 and R3-022. The service does present a CAPTCHA in its search flow, and the runner's environment was gated at search time. The block is genuine and service-side, not fabricated and not runner-caused.

## Corrections and notes

1. Challenge type mislabeled: brief-report.txt and the sealing commit (5a501b64) call the gate "hCaptcha" (and "4 hCaptcha iframes"). The 07:10:51 screenshot shows Google reCAPTCHA: the "I'm not a robot" checkbox with the reCAPTCHA logo and the text "This site is exceeding reCAPTCHA Enterprise free quota." The correct challenge type is reCAPTCHA, not hCaptcha. This is a labeling error in the runner's report and the sealing commit; the gate itself is real and visible in the screenshot. The verdict rests on the screenshot, not the label.
2. Missing brief file: the assignment named rung3-run-log/briefs/R3-027-scorer-mochi-brief.md, but that file does not exist at todolist-push tip 5a501b64 (the briefs dir holds R3-028 briefs and clone2-calibration only). I read brief-report.txt from the snapshot instead and scored per the standard scorer-1 brief plus the R3-L3 addendum. The coordinator should check the brief path for future assignments.
3. ket-qua.txt missing: see the Evidence section. The block is recorded in brief-report.txt and the screenshot. This differs from R3-025 original (FAIL), where the snapshot had no evidence of any service block at all (only a driver stall). Here the service block is documented in evidence, so INVALID applies.
4. The runner entered the user way (typed "namechk" in the address bar, clicked the first SERP result, no deep link), consistent with the TEST LIKE A NORMAL USER rule.

## Cap and backup note

- Sealed invalids before R3-027: R3-011 (medium), R3-022 (hard), R3-024 (medium), R3-026 (medium) = 4 total, 3 medium, 1 hard. R3-027 (medium) would be the 5th total (at cap 5) and the 4th medium (over group cap 2). No medium backup remains (DP-03, DP-06, DP-07 used); only DP-05 (very hard) is unused. If sealed INVALID, R3-027 drops from the denominator without replacement per section 8 (same as R3-026). This consequence does not affect the verdict; the block is a service bot-check regardless of caps.

## Verdict reasoning

- The task's results cannot be obtained: namechk.com gates the username search behind a reCAPTCHA, and the runner correctly stopped instead of solving it. No results were produced for any of the 3 usernames.
- The block is a service bot-check, not caused by the runner: user-way entry, webdriver hidden by the shim, single search attempt, no reload, no hammering, no challenge interaction, stop at the gate.
- Independent evidence confirms the service presents a CAPTCHA in its search flow and the runner's environment was gated at search time.
- Verdict: INVALID (proposed). Needs scorer 2 blind confirmation plus coordinator co-sign per the brief.
