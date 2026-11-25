# Scorer 1 grade, R3-L3, R3-018

- Session: 70cd99d1-ecef-4d02-9f42-714d7e86ab85 (scorer 1A, Pair A)
- Task: R3-018 (Tier B, position 17, run R3-L3)
- Verdict: PASS
- Scored at: 2026-11-26 01:35:53 +07 (Asia/Ho_Chi_Minh)
- Snapshot: rung3-run-log/rung3-snapshots/R3-018-L3/ at todolist-push commit 4f1b82cf, manifest_sha256 9db397d59ae138d7b25e21e1a818e3b615c92f97060b6ec0e4e0a29b7d66e89f, all 6 evidence files hash-OK against manifest.json, manifest gate PASS
- Key file hashes (verified before scoring): docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8, docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (both match the R3-L3 freeze)

## Files read

- rung3-run-log/rung3-snapshots/R3-018-L3/manifest.json (snapshot R3-018-L3, commit 4f1b82cf)
- rung3-run-log/rung3-snapshots/R3-018-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-018-L3/20261126-012849-domain-1.png
- rung3-run-log/rung3-snapshots/R3-018-L3/20261126-012902-domain-2.png
- rung3-run-log/rung3-snapshots/R3-018-L3/20261126-012916-domain-3.png
- rung3-run-log/rung3-snapshots/R3-018-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-018-L3/end_time.txt
- docs/rung3-answer-keys.md, R3-018 key section (lines 263-269)
- docs/rung3-list-100-tasks.md, section 6, R3-018 task text (lines 410-412)

I scored from the snapshot and the key only. I did not read any other scorer's grade or verdict file, did not contact the runner, and did not read any runner log, ledger, or trial report. I read each of the 3 screenshots directly and cross-checked every value in ket-qua.txt against them.

## Key (R3-018, Tier B)

3 domain names, in this order: 1. rung3khaosat01.com 2. rung3khaosat02.com 3. rung3khaosat03.com. Each name records: status (available or taken), first-year price (if available), suggested alternative name (if any name is taken). Status and price are live at run time; the truth is the lookup result screenshot, not the current price. Do not buy any domain. If the page shows a 'Verify you are human' check page or a Cloudflare page, stop, record it in ket-qua.txt, task invalid per section 1. Evidence: 3 result screenshots + ket-qua.txt. The scorer cross-checks against the screenshots.

## Evidence

- ket-qua.txt (705B) records the Namecheap domain lookup (lookup only, nothing purchased), results pages /domains/registration/results/, tool https://www.namecheap.com domain search, and a table of 3 rows: rung3khaosat01.com available $12.08/yr, rung3khaosat02.com available $12.08/yr, rung3khaosat03.com available $12.08/yr. Notes: each result shows "Add to cart" with Retail $15.98/yr; new customers can get $6.48 first year with promo code NEWCOM648 (T&Cs apply). No domain was taken, so no alternatives needed. Suggested other extensions shown by the site (not needed): .to $39.98/yr, .org $8.48/yr, .ai $89.98/yr, .net $12.48/yr.
- Screenshot domain-1 (01:28:49): Namecheap results page for rung3khaosat01.com, green checkmark, $12.08/yr, Retail $15.98/yr, NEWCOM648 badge, "Add to cart" button. Available. Suggested Results show rung3khaosat01.com $12.08/yr, .to $39.98/yr, .org $8.48/yr, .ai $89.98/yr, .net $12.48/yr. Matches ket-qua.txt row 1 and the notes exactly.
- Screenshot domain-2 (01:29:02): Namecheap results page for rung3khaosat02.com, green checkmark, $12.08/yr, Retail $15.98/yr, NEWCOM648 badge, "Add to cart" button. Available. Suggested Results show the same extension prices for the 02 name. Matches ket-qua.txt row 2 exactly. This is a different domain from screenshot 1.
- Screenshot domain-3 (01:29:16): Namecheap results page for rung3khaosat03.com, green checkmark, $12.08/yr, Retail $15.98/yr, NEWCOM648 badge, "Add to cart" button. Available. Suggested Results show the same extension prices for the 03 name. Matches ket-qua.txt row 3 exactly. This is a different domain from screenshots 1 and 2.
- The 3 screenshots are distinct files (different sha256, different sizes 732056 / 734292 / 733866 bytes), not copies of one image.
- No 'Verify you are human' check page and no Cloudflare page appeared, so the task ran normally and no invalid condition applies. No domain was purchased; the lookup was read-only.

## Reason

All 3 domains were checked in the key's order on Namecheap, all 3 are available at $12.08/yr first year, and every status and price in ket-qua.txt matches the screenshots exactly, including the Retail $15.98/yr and the suggested extension prices. No domain was taken, so no alternative names were needed. Every key check passes.

Timing note: start 2026-11-26T01:23:47+07:00, end 2026-11-26T01:29:17+07:00 (5 min 31 s); the 3 screenshots are timestamped 01:28:49, 01:29:02, 01:29:16, about 13-14 s apart, consistent with searching 3 domains one by one.

Signed: mochi, scorer 1A, session 70cd99d1-ecef-4d02-9f42-714d7e86ab85.
