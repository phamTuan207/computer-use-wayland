# H6 prefetch URL normalization

## Change

Added `_normalize_prefetch_url` to parse URLs and insert `/` only when an otherwise valid authority has an empty path. The open lookup, duplicate-prefetch lookup, and both adoption checks now compare normalized URLs, so Chromium's `https://example.com/` matches a stored `https://example.com` record. Stored record URLs remain unchanged. The 30 second TTL, maximum of three entries, eviction and close behavior, and ready, error-free adoption checks remain unchanged.

## Verification

All times are Asia/Ho_Chi_Minh (UTC+07:00), on 2026-11-20.

- 05:37:15: confirmed clean worktree, branch `harness-prefetch`, HEAD `ac3882b2b3daeb4a7166346064e9b8036218a61b`.
- 05:37:36 to 05:39:19: clean-tree baseline full suite, 1358 tests, 7 failures, 0 errors, 2 skipped.
- 05:42:56: reviewed implementation and test diff; `git diff --check` passed.
- 05:43:08 to 05:43:09: `python3 tests/test_chromium_cli.py`, 36 tests; 1 known baseline failure, `test_chromium_cli.CuCliWiringTests.test_cli_list_includes_chromium` (expected 13 commands, found 15).
- 05:43:26: prefetch-focused tests, 13 tests, all passed.
- 05:44:01 to 05:45:45: post-fix full suite, 1362 tests, 7 failures, 0 errors, 2 skipped.
- 05:46:21: compared full-suite failure and error IDs before and after; the sets are identical. Confirmed the remote branch still pointed to the baseline commit before publishing this fix.

Full-suite failure IDs, present both before and after:

- `test_chromium_cli.CuCliWiringTests.test_cli_list_includes_chromium`
- `test_session_driver.DoctorCliTests.test_base_exception_from_probe_is_not_converted_to_ime_error`
- `test_session_driver.DoctorCliTests.test_first_failure_skips_second_probe`
- `test_session_driver.DoctorCliTests.test_long_crlf_probe_error_is_single_line_bounded`
- `test_session_driver.DoctorCliTests.test_remote_success_keeps_schema`
- `test_session_driver.DoctorCliTests.test_second_probe_failure_after_first_success`
- `test_session_policy.RefusalFlow.test_screen_refusal_keeps_session_then_fresh_act_succeeds`

There were no full-suite errors before or after. The four added tests increased the full-suite count from 1358 to 1362 without adding a failure.

## Live re-measure

In a later live run, prefetch `https://example.com` and open `https://example.com/` in one burst. Check that open reports `prefetched:true`, reuses the prefetch tab ID, and has `load_ms` near the adopted result of 13 ms rather than the fresh-load result near 50 ms. No live re-measure was run for this fix.

## Scope

Code and test changes are confined to `/home/james/computer-use-wayland-prefetch`. The required progress and test logs are under `/tmp`. The main checkout was not changed. The relay was not restarted. No broker or executor was used, and no live task was run.
