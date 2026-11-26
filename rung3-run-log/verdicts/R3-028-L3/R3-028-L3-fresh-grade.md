# R3-028-L3 fresh grade (Pair B scorer 2)

- Task: R3-028 (Tier B), run R3-L3
- Verdict: PASS
- Scorer: fresh Muse scorer session d91a1e37-cfbc-4f89-bfdb-6698a306491c
- Graded: 2026-11-26T07:39:41+07:00
- Base: todolist-push 5c0202984876e4207b3c3094c76e4f292e68dcad
- Snapshot: rung3-run-log/rung3-snapshots/R3-028-L3/

## Key verification

- docs/rung3-answer-keys.md sha256 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60: matches the brief.
- docs/rung3-answer-keys.json sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8: matches the brief.
- Key section: "## R3-028 (Tier B)" at line 343. Grading evidence required: 3 result screenshots + ket-qua.txt; the scorer cross-checks local times and offsets against the screenshots.
- Key answers: 2026-12-01 12:00 UTC gives Hanoi 19:00, London 12:00, New York 07:00 (all 1 Dec); 2026-12-01 18:00 UTC gives Hanoi 2026-12-02 01:00, London 18:00, New York 13:00; 2026-12-02 00:00 UTC gives Hanoi 07:00, London 00:00, New York 2026-12-01 19:00. Offsets: Hanoi +7, London +0, New York -5.

## Snapshot hash verification

manifest.json manifest_sha256 field: aa4e4e15be9856627479801398398cee95f8f70874283c52f19f62a8806e2906 (matches the brief). sha256 of the manifest.json file itself: adbb659a251d4a1d9733c73890e96d6b0e2eb561b22b2485cadba2a0a0703e9d. Every listed file was re-hashed and matches:

| File | Result |
|---|---|
| 20261126-073106-result1-utc-2026-12-01-1200.jpg | OK |
| 20261126-073257-result2-utc-2026-12-01-1800.jpg | OK |
| 20261126-073507-result3-utc-2026-12-02-0000.jpg | OK |
| drive-r3028.log | OK |
| drive-stdout.log | OK |
| end_time.txt | OK |
| holder-r3028.log | OK |
| ket-qua.txt | OK |
| probe-ready.json | OK |
| start_time.txt | OK |

## Evidence check against the key

Each screenshot was read visually and cross-checked with ket-qua.txt and the key:

1. 20261126-073106-result1-utc-2026-12-01-1200.jpg: UTC Tue, 1 Dec 2026 12:00; Hanoi, Vietnam ICT (UTC +7) Tue, 1 Dec 2026 19:00; London, United Kingdom GMT (UTC +0) Tue, 1 Dec 2026 12:00; New York, NY, USA EST (UTC -5) Tue, 1 Dec 2026 07:00. Matches key row 1 and ket-qua.txt entry 1.
2. 20261126-073257-result2-utc-2026-12-01-1800.jpg: UTC Tue, 1 Dec 2026 18:00; Hanoi Wed, 2 Dec 2026 01:00; London Tue, 1 Dec 2026 18:00; New York Tue, 1 Dec 2026 13:00. Matches key row 2 and ket-qua.txt entry 2.
3. 20261126-073507-result3-utc-2026-12-02-0000.jpg: UTC Wed, 2 Dec 2026 00:00; Hanoi Wed, 2 Dec 2026 07:00; London Wed, 2 Dec 2026 00:00; New York Tue, 1 Dec 2026 19:00. Matches key row 3 and ket-qua.txt entry 3.

Offsets shown on all 3 screenshots (ICT UTC +7, GMT UTC +0, EST UTC -5) match the key offsets and the ket-qua.txt offset summary. ket-qua.txt states the values were read from the saved screenshots, and every value agrees. No mismatch found.

## INVALID candidate check (shared timeanddate cause)

The key pre-declares R3-028 (with R3-011, R3-036, R3-046) an INVALID candidate only if the site is blocked at browser level at run time. The snapshot proves the opposite: all 3 screenshots show the live timeanddate.com Time Zone Converter fully loaded with computed results; drive-r3028.log records "blocked": false in every page state (25 states, 0 blocked) and no Cloudflare challenge, captcha, or 403 page; probe-ready.json shows webdriver false with a clean native-code getter. There is no block screenshot and no block-evidence.txt in the snapshot. The INVALID condition is not met.

## Shared-cause statement

shared_cause_confirmed: false. The snapshot browser evidence does NOT prove a timeanddate.com block; it proves the site was reachable and functional at run time (2026-11-26 07:21:44 to 07:35:54 +07:00). There is no shared block cause to confirm for R3-028, so this task contributes no shared-cause invalid event. The task is graded on its merits as PASS.

## Independence declaration

I graded independently from the snapshot and key section only; I did not read scorer 1's verdict or contact the runner. I also did not read the ledger row for R3-028 and did not read the live site.
