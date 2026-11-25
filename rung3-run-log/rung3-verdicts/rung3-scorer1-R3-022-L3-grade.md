# Scorer 1 grade, R3-L3, R3-022

- Session: 70cd99d1-ecef-4d02-9f42-714d7e86ab85 (scorer 1A, Pair A)
- Task: R3-022 (Tier B hybrid, position 20, run R3-L3)
- Verdict: INVALID (proposed, needs blind confirmation from scorer 2 and coordinator co-sign per section 1)
- Scored at: 2026-11-26 03:10:09 +07 (Asia/Ho_Chi_Minh)
- Snapshot: rung3-run-log/rung3-snapshots/R3-022-L3/ at todolist-push commit 906d0921, manifest_sha256 f457c5c405e0b159243dc4f5f7e138f2a9f4fafff8d55fb05b06c675c1e42fed, all 5 evidence files hash-OK against manifest.json, manifest gate PASS (mechanical)
- Key file hashes (verified before scoring): docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both match the R3-L3 freeze)

## Files read

- rung3-run-log/rung3-snapshots/R3-022-L3/manifest.json (snapshot R3-022-L3, commit 906d0921)
- rung3-run-log/rung3-snapshots/R3-022-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-022-L3/translated-page-blocked-20261126-025929.png
- rung3-run-log/rung3-snapshots/R3-022-L3/websites-mode-20261126-030003.png
- rung3-run-log/rung3-snapshots/R3-022-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-022-L3/end_time.txt
- docs/rung3-answer-keys.md, R3-022 key section (lines 287-301)
- docs/rung3-list-100-tasks.md, section 6, R3-022 task text (lines 431-435)
- docs/rung3-list-100-tasks.md, section 1, invalid rule (line 34)

I scored from the snapshot and the key only. I did not read any other scorer's grade or verdict file, did not contact the runner, and did not read any runner log, ledger, or trial report. I read both screenshots directly and collected my own independent evidence with a read-only cloud-browser check of the same translation (see below); I recorded no translations from that check beyond the one heading needed to answer whether the page loads.

## Key (R3-022, Tier B hybrid)

Source English page: https://en.wikipedia.org/wiki/Computer, translate to Vietnamese on translate.google.com (website translation). 5 terms and their Vietnamese translations (expected strings; scorer accepts semantically matching translations): central processing unit -> "bộ xử lý trung tâm", random-access memory -> "bộ nhớ truy cập ngẫu nhiên", motherboard -> "bộ mạch chủ", operating system -> "hệ điều hành", hard disk drive -> "ổ đĩa cứng". Back-translate 2 of the 5 terms (runner chooses any 2), accepted if semantically matching the original, with the listed synonyms accepted. The translated page title must be correct. Key-scored part: all 5 term pairs, translations semantically matching, 2 back-translation results semantically matching the original. Human-scored part: screenshot shows the translated page. Scoring evidence: translated-page screenshot + ket-qua.txt.

Section 1 invalid rule (line 34): if the service changes interface, closes, runs out of stock, cannot be accessed, shows a bot-check or reCAPTCHA page, or the app on the laptop is missing, the scorer records the task as invalid, not counted in the sample. Max 5 invalid total, max 2 per difficulty group (medium, hard, very hard). Every invalid decision needs independent second confirmation from scorer 2, who sees only the invalid evidence and reason, not scorer 1's decision, before confirming. When a task is invalidated during the run, the scorer takes the FIRST UNUSED backup in the list with the same difficulty, in that fixed order.

## Evidence

- ket-qua.txt (2477B) records the task (Google Translate website translation of https://en.wikipedia.org/wiki/Computer to Vietnamese) and the steps done in Zen: opened translate.google.com in a new tab (loaded as Google Dich, sl=en tl=vi); clicked "Trang web" (Websites); verified languages source English, target Vietnamese; entered https://en.wikipedia.org/wiki/Computer in the URL input (read-back verified exact value); clicked the translate submit button. Result: BLOCKED by Google unusual-traffic check; the translated page never loaded. Attempt 1 (UI flow): new tab went to https://www.google.com/sorry/index?continue=https://translate.google.com/translate%3Fsl%3Den%26tl%3Dvi%26hl%3Dvi%26u%3Dhttps://en.wikipedia.org/wiki/Computer%26client%3Dwebapp&hl=vi (reCAPTCHA page), page text "He thong cua chung toi da phat hien thay luu luong truy cap bat thuong tu mang may tinh cua ban..." (Our systems have detected unusual traffic from your computer network), time shown 2026-11-25T19:53:35Z. Attempt 2 (direct proxy URL in a new tab): https://en-wikipedia-org.translate.goog/wiki/Computer?_x_tr_sl=en&_x_tr_tl=vi&_x_tr_hl=vi also redirected to https://www.google.com/sorry/index (same unusual-traffic message, English), time shown 2026-11-25T19:58:22Z. Per drive rules (stop on bot check, do not hammer), no further attempts were made. Translated page title: NOT OBTAINED. All 5 term pairs: NOT OBTAINED. Back-translation results: NOT OBTAINED. No substitute translations were fabricated.
- Screenshot translated-page-blocked-20261126-025929.png: the Google sorry page with the "I'm not a robot" reCAPTCHA checkbox, "About this page: Our systems have detected unusual traffic from your computer network. This page checks to see if it's really you sending the requests, and not a robot.", IP address 2001:ee0:4141:6c79:eaea:e080:7aa:4010, Time 2026-11-25T19:58:22Z, URL https://en-wikipedia-org.translate.goog/wiki/Computer?_x_tr_sl=en&_x_tr_tl=vi&_x_tr_hl=vi. This matches ket-qua.txt attempt 2 exactly (same URL, same time). The tab bar shows only 3-4 tabs (google.com sorry page, the translate proxy tab, Google Dich, translate.google.com), so there is no many-tabs abuse.
- Screenshot websites-mode-20261126-030003.png: Google Translate (Google Dich) in Websites mode, "Trang web" selected, source "Anh" (English), target "Việt" (Vietnamese), URL input containing https://en.wikipedia.org/wiki/Computer, cursor on the submit arrow. This confirms translate.google.com itself loaded normally and the runner set up the translation correctly; the block happened only when the translated page was requested.
- The runner did not cause the block: only 2 attempts (one UI flow, one direct proxy URL), then stopped per the drive rules; no hammering, no repeated retries, only a few tabs open. The block is tied to the runner's network/IP (the sorry page names IP 2001:ee0:4141:6c79:eaea:e080:7aa:4010).
- No Pass criterion is met: there is no translated title, no term pairs, no back-translations, and no screenshot of a translated page. Nothing was fabricated to fill the gap. This is not a FAIL either: the failure is a service-side bot-check page, which section 1 defines as invalid, not a runner error.

## Independent evidence collected by me

Read-only cloud-browser check (cloud browser, Environment 2, 03:09-03:10 +07, under 1 minute, single navigation, no CAPTCHA encountered or solved): I opened https://translate.google.com/translate?sl=en&tl=vi&hl=vi&u=https://en.wikipedia.org/wiki/Computer&client=webapp exactly once. The translated Wikipedia page loaded successfully: final URL https://en-wikipedia-org.translate.goog/wiki/Computer?_x_tr_sl=en&_x_tr_tl=vi&_x_tr_hl=vi&_x_tr_pto=wapp, tab title "Computer - Wikipedia", first heading "Máy tính", Google Translate toolbar in Vietnamese and the Wikipedia article in Vietnamese. No google.com/sorry page, no reCAPTCHA, no unusual-traffic message appeared. This shows the block is IP/time/fingerprint-specific to the runner's Zen environment, as with R3-011, and does not refute the runner's block at run time. The service itself works; the runner's environment was blocked.

## Reason

The service showed a bot-check/reCAPTCHA page (google.com/sorry, "unusual traffic") on both attempts, which section 1 defines as invalid; the runner made only 2 attempts and stopped per the rules, so the runner did not cause the block; and my independent check shows the same translation loads normally from another environment, confirming the block is environment-specific. No result could be obtained, so no Pass criterion is met, and the failure is a service-side block, not a runner error, so it is not a FAIL. Proposed INVALID, needs blind confirmation from scorer 2 and coordinator co-sign per section 1.

Cap and backup note: R3-022 is hard difficulty ("do kho: kho"). The hard group currently has 0 invalids; the group cap is 2 and the total cap is 5 (current total: R3-011 event + R3-047 = 2), so this proposed invalid is within both caps. Per section 1, the sealing decision names the first unused hard backup, DP-02 (the hard group has only DP-02 left as a backup).

Timing note: start 2026-11-26T02:49:06+07:00, end 2026-11-26T03:05:35+07:00 (16 min 29 s), within the 30-min task timeout; the block page times (19:53:35Z and 19:58:22Z = 02:53:35 and 02:58:22 +07) and the screenshots (02:59:29 and 03:00:03) are inside the run window.

Signed: mochi, scorer 1A, session 70cd99d1-ecef-4d02-9f42-714d7e86ab85.
