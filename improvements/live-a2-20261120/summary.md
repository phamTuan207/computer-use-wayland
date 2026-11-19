# A2 preflight absorb measurement

- Status: IN PROGRESS.
- Date: 2026-11-20, Asia/Ho_Chi_Minh.
- Repo HEAD: 296ce45715cc16d39e6fca63060cce70910d5019 (`a2-preflight`).
- Relay started_git_head: 296ce45715cc16d39e6fca63060cce70910d5019, broker idle before measurement.
- Build gate cited, not rerun: full suite 1341 tests, 7 failures, 2 skipped, zero new failures versus baseline 1339 tests, 7 failures, 0 errors, 2 skipped; `tests/test_act_diagnostics.py` 22/22.
- Smoke: accepted true, ok true, api_calls 1, elapsed_ms 1.77; smoke session finished successfully.

## P3 B-01 attempt 1

- Start submit: 2026-11-20 03:38:21.354 +07:00.
- Program result and in-program verification: 2026-11-20 03:38:33.380 +07:00.
- Measured start-to-result wall: 12.026 s. No timed-request dwell preceded the only task request.
- Timed code-exec: accepted true, ok true, api_calls 4, elapsed_ms 1032.098, images 3, image bytes 1,342,929.
- Act result markers: `preflight_absorbed` absent, `preflight_retries` absent. No refusal surfaced; diagnostics event `preflight_absorb_retry` absent in `diagnostics-9556c8e9e6f47747.jsonl`.
- Independent shell check: MATCH. Evidence: `find /tmp/hoc-ky-2 -type d` listed exactly `/tmp/hoc-ky-2`, `/tmp/hoc-ky-2/oop`, `/tmp/hoc-ky-2/ktvm`, and `/tmp/hoc-ky-2/dsa`.
- This was a clean run with no natural flake hit. A second fresh attempt is required by the measurement protocol.

## P3 B-01 attempt 2

- Start submit: 2026-11-20 03:40:56.859 +07:00.
- Program result and in-program verification: 2026-11-20 03:41:07.191 +07:00.
- Measured start-to-result wall: 10.332 s. No timed-request dwell preceded the only task request.
- Timed code-exec: accepted true, ok true, api_calls 4, elapsed_ms 1023.843, images 3, image bytes 1,356,827.
- Act result markers: `preflight_absorbed` absent, `preflight_retries` absent. No refusal surfaced; diagnostics event `preflight_absorb_retry` absent in `diagnostics-0dbcb1b48e4b9d17.jsonl`.
- Independent shell check: MATCH. Evidence: `find /tmp/hoc-ky-2 -type d` listed exactly `/tmp/hoc-ky-2`, `/tmp/hoc-ky-2/oop`, `/tmp/hoc-ky-2/ktvm`, and `/tmp/hoc-ky-2/dsa`.
- No natural flake hit.

## P4 A-01 attempt 1

- Start submit: 2026-11-20 03:41:40.437 +07:00.
- Program result and in-program verification: 2026-11-20 03:41:50.395 +07:00.
- Measured start-to-result wall: 9.958 s. No timed-request dwell preceded the only task request.
- Timed code-exec: accepted true, ok true, api_calls 4, elapsed_ms 1293.217, images 3, image bytes 1,382,448.
- Act result markers: `preflight_absorbed` absent, `preflight_retries` absent. No refusal surfaced; diagnostics event `preflight_absorb_retry` absent in `diagnostics-afbf525da748fddc.jsonl`.
- Independent shell check: MATCH. `cat` showed the three expected Vietnamese lines. `sha256sum` returned `a6e58cb9f73ad08a588ed6668f72bcdc29b91af575860b35848c041d1ca7b170`; file size was 128 bytes with one trailing newline.
- No natural flake hit. A second fresh attempt is required by the measurement protocol.

## P4 A-01 attempt 2

- Start submit: 2026-11-20 03:42:30.760 +07:00.
- Program result and in-program verification: 2026-11-20 03:42:40.221 +07:00.
- Measured start-to-result wall: 9.460 s. No timed-request dwell preceded the only task request.
- Timed code-exec: accepted true, ok true, api_calls 4, elapsed_ms 1278.607, images 3, image bytes 1,414,766.
- Act result markers: `preflight_absorbed` absent, `preflight_retries` absent. No refusal surfaced; diagnostics event `preflight_absorb_retry` absent in `diagnostics-be1ed2550f0c1350.jsonl`.
- Independent shell check: MATCH. `cat` showed the three expected Vietnamese lines. `sha256sum` returned `a6e58cb9f73ad08a588ed6668f72bcdc29b91af575860b35848c041d1ca7b170`; file size was 128 bytes with one trailing newline.
- No natural flake hit.
