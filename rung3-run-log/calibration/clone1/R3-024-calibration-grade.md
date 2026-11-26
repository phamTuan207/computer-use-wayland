# R3-024 calibration grade (sealed, blind)

- Task: R3-024
- Session: 29c95656-2940-4ec5-999f-4ed3e3b72ac2
- Verdict: INVALID

## Key hashes verified

- docs/rung3-answer-keys.md sha256: 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (matches required value)
- docs/rung3-answer-keys.json sha256: 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8 (matches required value)
- Key section read: docs/rung3-answer-keys.md lines 307-313 only (section "## R3-024 (Tier B)")
- JSON entry read: R3-024 only — allocated keywords ["mountain lake", "city bicycle", "old library"], tier "B"

## Manifest hash verification

- Snapshot dir: rung3-run-log/rung3-snapshots/R3-024-L3/ (origin/todolist-push, tip 31fa2244)
- manifest.json manifest_sha256 field: 0aa2cb239c8c5b75d900c42fbe1fc7559836729dcc6902086eb5b06d4f95c02d (matches required value)
- Per-file sha256, all match the manifest entries:
  - blocked-cloudflare-20261126-032300.png: 9f67e5f6ee007d2ef2638fc4383f906a5b540a7ce3564b15592f38d6f2ec8b94 — MATCH
  - end_time.txt: 556f8d4ea13162c5836df7f9a689eedcc55c97ebbb9d99ed23d3660a09e11932 — MATCH
  - ket-qua.txt: 5a52ff12b6d05fd92b325d0bff022c3309883f3f31473d430b4b86f2ea671e82 — MATCH
  - start_time.txt: e27fe24040df6dfc14268213b50ec3719144b3741ae5d216ee16c11f752b28fa — MATCH

## Files read (allowlist only)

- rung3-run-log/rung3-snapshots/R3-024-L3/manifest.json
- rung3-run-log/rung3-snapshots/R3-024-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-024-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-024-L3/end_time.txt
- rung3-run-log/rung3-snapshots/R3-024-L3/blocked-cloudflare-20261126-032300.png
- docs/rung3-answer-keys.md lines 307-313
- docs/rung3-answer-keys.json, R3-024 entry only

## Independence declaration

I graded blind from the snapshot and key section only; I did not read the ledger, any grade file, or any other verdict for these tasks

## Checker

The tier-A checker (rung3-ci/tier-a-check.py) was not run. Grading was done manually from the key criteria.

## Read-route note

The initial local git read (fetch + tip/hash check) was flagged by an execution-risk notice. The coordinator then authorized the GitHub API route for remaining reads. All required reads were already complete and hash-verified by then; no further git reads were made after the route-change instruction.

## Verdict: INVALID

### Key criteria applied

From the key section (docs/rung3-answer-keys.md lines 307-313) and the R3-024 JSON entry: search 3 keywords on openverse.org in order ("mountain lake", "city bicycle", "old library"), reuse-allowed filter only; record for each image its name, author, specific reuse license, and original link; all 3 images must have a reuse-permitting license; name, author, license, and link are live at run time and the truth is the screenshot of each image's detail page; grading evidence is 3 detail-page screenshots + ket-qua.txt, cross-checked against the screenshots, links only, no downloads.

### Reasons tied to specific files

- ket-qua.txt: the run was BLOCKED by a Cloudflare bot check on the search results page for keyword 1 "mountain lake" (https://openverse.org/search/image?q=mountain+lake). No image data was obtained. All 3 rows are marked NOT OBTAINED; keywords 2 and 3 were never searched because the service block applies to the search endpoint. No original links were obtained and no images were downloaded. The runner waited 60 seconds, re-checked at 03:23, and stopped per drive rules (no reload, no challenge interaction, no further searches).
- blocked-cloudflare-20261126-032300.png: viewed directly; it shows the Cloudflare "Just a moment..." verification page for openverse.org ("Performing security verification", "Verify you are human", Cloudflare branding), with the browser tab titled "Just a moment..." and no search results visible. This confirms the block is genuine and the ket-qua.txt account is accurate.
- start_time.txt (2026-11-26T03:10:54+07:00) and end_time.txt (2026-11-26T03:24:32+07:00): consistent with the ket-qua.txt timeline (block first seen about 03:21, re-checked 03:23, 60-second wait observed).
- Not PASS: the required evidence (3 detail-page screenshots plus 3 rows of name, author, license, link) does not exist, so nothing can be verified against the key.
- Not FAIL: no wrong data was produced and no procedure was violated; the runner followed the task up to the block and stopped correctly. The absence of data is caused by an external service block, not by runner error.
- INVALID: the task could not be attempted because the Cloudflare bot check blocked the search endpoint, per the bot-check invalid definition. A backup or re-run is a coordinator decision, not a grading matter.

### Minor observation (does not change the verdict)

The Ray ID recorded in ket-qua.txt (a6035b302a2fb39e) differs from the Ray ID visible in the screenshot (a6035e3aee11b39e), although ket-qua.txt states the re-check showed the "same Ray ID". This is a documentation inconsistency only: the block itself is proven by the screenshot, and the required evidence cannot exist either way.
