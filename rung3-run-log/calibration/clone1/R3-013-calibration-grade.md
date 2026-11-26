# R3-013 calibration grade (blind, sealed)

- Task: R3-013
- Session: a28c4ffe-e1bc-4b8c-ac3f-9c4969046c82
- Verdict: PASS
- Coordinator: epoch 10, check 7 (clone1 rule), R3-L3 calibration
- Branch tip verified: origin/todolist-push 31fa224403fe6ad31ef83e03443c529e1a4696ce (local git fetch, then re-verified via GitHub API)

## Key hashes (verified)

- docs/rung3-answer-keys.md sha256: 21f8b61a6eaa0097e9840adb218f15e99d446fc2a62968aef614116c8831bc60 (matches required value)
- docs/rung3-answer-keys.json sha256: 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8 (matches required value)
- Key section read: docs/rung3-answer-keys.md lines 225-236 only (section "## R3-013 (Tier A)")
- JSON entry read: docs/rung3-answer-keys.json `.tasks["R3-013"]` only (type regex-counts, 5 rows, sample_text)

## Manifest hash verification

- Snapshot dir: rung3-run-log/rung3-snapshots/R3-013-L3/
- manifest.json `manifest_sha256` field: 7d4a5c763010c87fb5b90378edfe022eb0dad88601105019207ad7bb5e8e161d (matches required value)
- Note: manifest.json file's own sha256 is 7bdf5ab9cf150549f3038eeedc9e90413307e2059ef19fbe2b356a465cbda142, so the `manifest_sha256` field is not a self-hash of the manifest file; its exact construction was not needed for the verdict. The prescribed check (field value) passes.

## Per-file hash verification (all 9 manifest-listed files)

| File | sha256 | Manifest entry | Result |
|---|---|---|---|
| 20261125-235731-regex-1.png | daa77fafa4bac82107e727e2eef9b89d0d5e3573e5dbf6c3e6bd7cb6990bc829 | daa77fafa4bac82107e727e2eef9b89d0d5e3573e5dbf6c3e6bd7cb6990bc829 | MATCH |
| 20261125-235741-regex-2.png | 732616059f07c5a2dde8d5883c744d2c42967cc84344b9632de3706eef43a1d1 | 732616059f07c5a2dde8d5883c744d2c42967cc84344b9632de3706eef43a1d1 | MATCH |
| 20261125-235750-regex-3.png | 48a947dd8b99e487ea4991c80be0aecd900afee6fae8ed1e37cf2b242a330c67 | 48a947dd8b99e487ea4991c80be0aecd900afee6fae8ed1e37cf2b242a330c67 | MATCH |
| 20261125-235759-regex-4.png | 8c16a20184ffa78858bd038caad17e18ae0b9b9c63161a91b2b35e22411e6473 | 8c16a20184ffa78858bd038caad17e18ae0b9b9c63161a91b2b35e22411e6473 | MATCH |
| 20261125-235808-regex-5.png | c5543b47fc190f92f1f791fcafd71f1fd073fab34f9018aa00945a3356904fde | c5543b47fc190f92f1f791fcafd71f1fd073fab34f9018aa00945a3356904fde | MATCH |
| end_time.txt | 43c841b8284b3abf2d72c35c34fbd645d3d2c293133f1313a6a6152ca3e05358 | 43c841b8284b3abf2d72c35c34fbd645d3d2c293133f1313a6a6152ca3e05358 | MATCH |
| explanation5.txt | a2c176a38baae4407889244f735e7ca6057eadc64ca961bc3e97117756b11be9 | a2c176a38baae4407889244f735e7ca6057eadc64ca961bc3e97117756b11be9 | MATCH |
| ket-qua.txt | 50f6f90211fbb4c8abb6875dae13284deb8a2eea244a482a1a68ef91ec9990dc | 50f6f90211fbb4c8abb6875dae13284deb8a2eea244a482a1a68ef91ec9990dc | MATCH |
| start_time.txt | 6c80ebe8660ab1e7ae49ac08619e3f830add6cc05d6db9a51d146fcea65fbd4c | 6c80ebe8660ab1e7ae49ac08619e3f830add6cc05d6db9a51d146fcea65fbd4c | MATCH |

9 of 9 files MATCH. No missing, extra, or altered snapshot file.

## Files read (allowlist only)

- rung3-run-log/rung3-snapshots/R3-013-L3/manifest.json
- rung3-run-log/rung3-snapshots/R3-013-L3/ket-qua.txt
- rung3-run-log/rung3-snapshots/R3-013-L3/explanation5.txt
- rung3-run-log/rung3-snapshots/R3-013-L3/start_time.txt
- rung3-run-log/rung3-snapshots/R3-013-L3/end_time.txt
- rung3-run-log/rung3-snapshots/R3-013-L3/20261125-235731-regex-1.png
- rung3-run-log/rung3-snapshots/R3-013-L3/20261125-235741-regex-2.png
- rung3-run-log/rung3-snapshots/R3-013-L3/20261125-235750-regex-3.png
- rung3-run-log/rung3-snapshots/R3-013-L3/20261125-235759-regex-4.png
- rung3-run-log/rung3-snapshots/R3-013-L3/20261125-235808-regex-5.png
- docs/rung3-answer-keys.md lines 225-236 only (section "## R3-013 (Tier A)")
- docs/rung3-answer-keys.json entry `.tasks["R3-013"]` only

I graded blind from the snapshot and key section only; I did not read the ledger, any grade file, or any other verdict for these tasks

## Method note

- Graded manually from the key criteria. The Tier A checker (rung3-ci/tier-a-check.py) was NOT run.
- Read route: the initial local git fetch and hash check were done first (tip and both key hashes verified); the first git result was then flagged by an execution-risk notice, so all remaining file reads used the GitHub API route (`gh api repos/phamTuan207/computer-use-wayland/contents/<path>?ref=todolist-push`) per the coordinator's route-change authorization. No repo script was run. No live site was visited. No other case's key section, no ledger, no existing grade file, and no other scorer's verdict was read.

## Reasons (verdict PASS)

Key criteria (key section lines 225-236 + JSON entry `.tasks["R3-013"]`): 5 regex patterns applied to the sample text on regex101, with exact counts and match strings; the site's explanation for pattern 5 recorded in ket-qua.txt; evidence = 5 result screenshots + ket-qua.txt.

1. Email, pattern `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}`, 3 matches (hoa@example.com, dung@test.org, khanh@example.com).
   - ket-qua.txt row 1: same pattern, count 3, same 3 strings. Match.
   - 20261125-235731-regex-1.png: regex101 shows the same pattern with flags /gm, "3 matches", the same sample text, the 3 addresses highlighted, Match Information listing Match 1 16-31 hoa@example.com, Match 2 214-227 dung@test.org, Match 3 231-248 khanh@example.com. Match.
2. Phone, pattern `0\d{9}`, 3 matches (0987654321, 0978123456, 0905551234).
   - ket-qua.txt row 2: same pattern, count 3, same 3 strings. Match.
   - 20261125-235741-regex-2.png: regex101 shows `0\d{9}`, "3 matches", Match Information listing Match 1 41-51 0987654321, Match 2 266-276 0978123456, Match 3 295-305 0905551234. Match.
3. Date, pattern `\d{2}\/\d{2}\/\d{4}` (escaped form per the key's ruling note; checker normalizes `\/` to `/`), 2 matches (03/09/2026, 10/09/2026).
   - ket-qua.txt row 3: same escaped pattern, count 2, same 2 strings. Match.
   - 20261125-235750-regex-3.png: regex101 shows `\d{2}\/\d{2}\/\d{4}`, "2 matches", Match Information listing Match 1 72-82 03/09/2026, Match 2 191-201 10/09/2026. Match.
4. Time, pattern `\d{2}:\d{2}`, 2 matches (09:15, 17:45).
   - ket-qua.txt row 4: same pattern, count 2, same 2 strings. Match.
   - 20261125-235759-regex-4.png: regex101 shows `\d{2}:\d{2}`, "2 matches", Match Information listing Match 1 61-66 09:15, Match 2 109-114 17:45. Match.
5. Money, pattern `\d{1,3}(?:\.\d{3})+`, 2 matches (2.750.000, 350.000).
   - ket-qua.txt row 5: same pattern, count 2, same 2 strings, followed by the site's explanation for pattern 5. Match.
   - 20261125-235808-regex-5.png: regex101 shows `\d{1,3}(?:\.\d{3})+`, "2 matches", Match Information listing Match 1 142-151 2.750.000, Match 2 169-176 350.000; the Explanation panel shows the same `\d{1,3}` / non-capturing group / `\d{3}` / g and m flag text recorded in ket-qua.txt and explanation5.txt. Match.

Additional checks:

- Pattern-5 explanation requirement: the key requires the site's explanation for pattern 5 to be recorded in ket-qua.txt. It is present in ket-qua.txt ("Explanation pattern 5: ... Global pattern flags g modifier ... m modifier ...") and matches explanation5.txt and the screenshot's Explanation panel. Satisfied.
- Evidence completeness: 5 screenshots + ket-qua.txt all present, all hash-verified against the manifest. Satisfied.
- Sample text: the test string shown in all 5 screenshots is the key's sample text. Satisfied.
- Timing: start_time.txt 2026-11-25T23:57:04.393587+07:00, end_time.txt 2026-11-25T23:58:32.195437+07:00; consistent with the screenshot timestamps (23:57:31-23:58:08). No anomaly.
- Bot-check / INVALID: no screenshot shows a bot-check, CAPTCHA, block page, or error; all 5 show regex101 working normally on the sample text. No INVALID trigger in the snapshot or the key criteria for this case.

All 5 patterns, counts, and match strings agree exactly between the key, ket-qua.txt, and the screenshots. Verdict: PASS.
