# Pick 1 P3/P4 fix report

Date: 2026-11-19
Owner: the owner
Verdict: PROVISIONAL (non-Astra). Astra 6 is out of credit and remains blocked.

## Root causes verified

### P3 template race

The `pick1-p3-code` envelope in `/tmp/speed-profile-20261118/pick1/records.jsonl` failed with `assert failed: file does not exist: /tmp/hoc-ky-2/dsa` after three API calls. The typed command can still be running after `act()` returns, so the immediate file assertions can beat the shell. The retry at label `pick1-p3-code-retry` failed with `assert failed: wait failed` after sending a wait act with the old observation. `scripts/code_exec.py:399-421` binds acts to observations returned in that session. `scripts/cu.py:1471-1479` re-observes before acting and refuses a screen-changed observation. The canonical template now observes after the type act, then asserts, and returns that observation image.

Mock testing exposed one related code defect: `assert_file_exists` used `Path.is_file()`, which always rejects P3's directories. It now checks path existence, including directories, while polling. P3's three directory assertions pass with the corrected semantics.

The requested P3 negative control and the new poll requirement cannot both be observed with identical production behavior: a 2 second poll will see a directory created 300 ms after the act, so the old direct-assert program would pass too. The negative control patches only `api_assert_file_exists` to its immediate pre-poll behavior, isolating and reproducing the original race. The production template program runs with the real poll and passes. The old shape remains invalid because it has no fresh post-act verification image and violates the canonical order.

### P4 shell command construction

The source confirms the cause is not byte rewriting in code-exec `act()`. `scripts/cu.py:1995-2002` passes the actions list directly to `desktop_act`. The old `prog-pick1-p4.py` matches the base request JSON stdin byte-for-byte; the retry record at label `pick1-p4-code-retry` preserves the accented assertion text. `native/vendor/wtype/main.c:161-187` remaps real newline to Return and maps other characters with `xkb_utf32_to_keysym`.

The old Python program used `\n` in its source string, which Python turns into real newline characters at runtime. wtype therefore pressed Return in the middle of the shell command. The `printf` argument was also unquoted. Diagnostic image `~/.cache/agent-computer-use/d5e0d6a1bee7.png` shows command-not-found errors and the redirect on a separate prompt. The baseline action in `actions-base-p4.json` contains the corrected single-quoted command with literal backslash-n and one final real newline. Baseline verify image `~/.cache/agent-computer-use/cf009120181b.png` shows `cat` printing all three lines with diacritics. Rapid input echo looked mangled in both images, but the baseline output was correct.

The fixed runtime string matches the specified characters. One formatting detail in the request's expected repr was not literal Python `repr` output: because the shell argument contains single quotes, Python displays the outer repr with double quotes. The actual repr recorded in the template is:

```text
"printf 'Ý tưởng 1: app nhắc uống nước.\\nÝ tưởng 2: bot tóm tắt bài giảng.\\nÝ tưởng 3: web bán đồ secondhand.\\n' > /tmp/y-tuong.txt && cat /tmp/y-tuong.txt\n"
```

The codepoint content is exact, including three literal backslash-n sequences and one trailing U+000A. The repr quote style differs, the command string does not.

## Changes and commits

- `improvements/pick1-program-template.md`: canonical windows, observe, act, observe, assert order; fixed P3 and P4 programs; unchanged P1/P2 order; root-cause evidence; byte escaping rule; Phase B handoff. Commits `d86e88c76502550e350af7a4aeb09dadf2378478` and `73bc427953c68ae6de07c49fd1608fcb873a2057`.
- `scripts/code_exec.py`: module docstring points to the template. File asserts poll for at most 2.0 seconds in 100 ms intervals, pass without sleeping when already satisfied, retry missing files, and check cancellation and wall budgets on each poll. `assert_file_exists` recognizes directories. Commit `92f3fbd64115310eb9f3356e9eb578bb30cedd2b`.
- `tests/test_code_exec.py`: mock-only coverage for P3 ordering, P4 shell splitting and UTF-8 bytes, direct act passthrough, assert polling, timeout messages, wall budget, and both template dry runs. Commit `e4064a4168db2e3646b1e9ff7b2a25742cfc36b6`.
- `improvements/live-test-log.md`: timestamps, durations, all test attempts, dry-run envelopes, and cleanup checks. Included in the final handoff commit with this report.

## Test results

`pytest` is not installed (`No module named pytest`), so the requested unittest fallback was used. The final full run passed all 32 tests, including the existing trace-budget and infinite-loop wall-budget tests. The log also records earlier iteration failures and their fixes:

| Run | Result | Duration |
| --- | --- | ---: |
| pytest availability check | 0 tests started, pytest unavailable | 0.008 s |
| unittest first run | 32 total, 28 passed, 4 failed due to mock window title | 6.112 s |
| unittest second run | 32 total, 30 passed, 2 failed, exposed directory assertion semantics | 13.772 s |
| unittest third run | 32 total, 31 passed, 1 failed due to a missing test fixture parent directory | 10.128 s |
| unittest final run | 32 passed, 0 failed | 10.274 s |

All runs used in-process mock backends. No broker, relay, or desktop action was used.

## Fixed-template dry run

Both templates ran through `code_exec.run_program` with `FakeTerminalBackend`, which simulates shell effects and 150 ms observation latency. The P4 file bytes matched the three brief lines plus one newline exactly.

| Program | ok | api_calls | elapsed_ms |
| --- | ---: | ---: | ---: |
| P3 | true | 4 | 301.662 |
| P4 | true | 4 | 302.077 |

Total dry-run wall time was 0.604 seconds. The dry-run envelopes and timing are in `improvements/live-test-log.md`.

## Still required for Phase B

This is mock evidence only. Live wtype typing, live shell completion timing, and the post-act observe behavior through the broker have not been measured here. The Phase B broker re-measure of P3/P4 is still required and remains the final proof. The coordinator should amend the Phase B brief to copy P3/P4 from `improvements/pick1-program-template.md`, not the old brief. Verdict remains PROVISIONAL (non-Astra); do not report live success until that rerun completes.

## Cleanup and current clients

No windows or broker sessions were opened, the relay was not restarted, and the live checkout was not edited. The final read-only `hyprctl clients` query, after exporting the signature from the directory containing `hyprland.lock`, returned only these pre-existing clients:

- Address `55fafcba8080`, class `org.omarchy.herdrdrop`, title `omarchy: Jarvis`, PID `148305`.
- Address `55faff012300`, class `zen`, title `Giảng lại AD AS (2) \u2014 Zen Browser`, PID `600148`. The title's separator is written as the escaped code point U+2014 to keep this report free of dash punctuation outside ASCII hyphens.

No `code-exec-test-*` paths remained in `/tmp`. The worktree is intended to be clean after the report and log commit. All changes are on branch `speed-swarm-pick1p34fix` and pushed to origin. the user's existing Jarvis and Zen clients were left untouched.
