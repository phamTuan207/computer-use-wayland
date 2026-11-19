# A4 postcondition live measure

Date: 2026-11-20, timezone Asia/Ho_Chi_Minh

**Verdict: BLOCKED.** The smoke code-exec succeeded, but the broker rejected `verify` twice with `unsupported_command`. `scripts/session_remote.py:41` omits `verify` from `COMMANDS`, while `scripts/session_driver.py:117` includes it. The one allowed retry followed a fresh `windows` observation and still failed. Per the run instructions, the P3 and P4 arms were not started.

## Checkout and relay

- Initial repo HEAD: `56f5af4e521e1c20b26b56dc31d662e34f1c2668`.
- Checkout: detached `algo-a4`, HEAD `7f3da57a76382dd2a73e3da896c5aaf773f0acfd`.
- Relay `started_git_head`: `7f3da57a76382dd2a73e3da896c5aaf773f0acfd` both before and after teardown.
- Flag-on environment was verified as `CU_CODE_EXEC=1`; cleanup removed the drop-in. Final relay is active, broker idle, owner null, and Environment has no `CU_CODE_EXEC`.
- Checkout remains on `algo-a4`. The speed terminal and test fixtures were removed.

## Flag-off CLI verify

Command exit code: `0`. Envelope, verbatim:

```json
{"ok": false, "status": "inconclusive", "needs_vision": true, "checks": [], "error": "deterministic verify is disabled; set CU_CODE_EXEC=1"}
```

The broker remained idle after this direct flag-off check.

## Smoke and CLI controls

The first smoke code-exec request had `wall-seconds` encoded as a JSON number and was refused with `invalid_arg_type`. The seq 2 observe then returned `sequence_gap`; the refused request had not advanced the broker sequence. A fresh lease and fresh `windows` observation allowed the single corrected code-exec retry to succeed: `api_calls=1`, `elapsed_ms=1.408`, `ok=true`.

The CLI `verify` control returned no status. The broker refused the verified control with `unsupported_command`, then the one retry after a fresh observation returned the same error. That exhausted the allowed retry and blocked the smoke control group. The failed and inconclusive control requests below were prepared but not sent; no result envelopes exist for them.

Verified control, first broker response, verbatim:

```json
{"cmd": "request", "label": "a4-smoke-verify-verified", "kind": "verify", "sequence": 3, "submit_mono": 63536.83934437, "submit_wall": 1795116502.4986272, "result_mono": 63536.908927831, "result_wall": 1795116502.56821, "service_s": 0.07, "request_call_s": 0.07, "result_call_s": 0.0, "accepted": false, "ok": null, "status": null, "error": null, "request_error": "unsupported_command", "request_status": null, "request_files_private": ["/tmp/speed-a4-20261120/a4-measure/a4-smoke-verify-verified.json"]}
```

Verified control, retry response after fresh observation, verbatim:

```json
{"cmd": "request", "label": "a4-smoke-cli-retry-verify", "kind": "verify", "sequence": 2, "submit_mono": 63723.734117366, "submit_wall": 1795116689.3934004, "result_mono": 63723.803947838, "result_wall": 1795116689.4632301, "service_s": 0.07, "request_call_s": 0.07, "result_call_s": 0.0, "accepted": false, "ok": null, "status": null, "error": null, "request_error": "unsupported_command", "request_status": null, "request_files_private": ["/tmp/speed-a4-20261120/a4-measure/a4-smoke-cli-retry-verify.json"]}
```

Prepared verified control request, not sent on retry session:

```json
{"args": ["verify", "--spec", "-"], "stdin": "[{\"kind\": \"file_contains\", \"path\": \"/tmp/a4-verify-fixture.txt\", \"text\": \"beta two\"}]"}
```

Prepared failed control request, not sent:

```json
{"args": ["verify", "--spec", "-"], "stdin": "[{\"kind\": \"file_contains\", \"path\": \"/tmp/a4-verify-fixture.txt\", \"text\": \"this text is not in the file\"}]"}
```

Prepared inconclusive control request, not sent:

```json
{"args": ["verify", "--spec", "-"], "stdin": "[{\"kind\": \"file_exists\", \"path\": \"/tmp/a4-verify-fixture.txt\"}]"}
```

Smoke record summary: 24 valid JSONL records, 9 status polls, 15 other records, 1.694 seconds total broker service, 0 image bytes, 0 sleeps. Refusals were `invalid_arg_type` once, `sequence_gap` once, and `unsupported_command` twice. No session died. One diagnostic timed status call has no preceding `DECIDE` line; it is not counted as a model call. Maximum recorded gap between timed operations was 123.288 seconds, under the 240 second limit.

## P3 and P4 arms

| Task | Arm | Wall excl dwell / strict | Think excl dwell / strict | Model calls | Broker service | Requests by kind | Refusals | Images / bytes | Misclicks | Session deaths | Retries | Postcondition status / postcondition_verified | Independent shell check |
|---|---|---|---|---:|---:|---|---:|---:|---:|---:|---:|---|---|
| P3 B-01 | Baseline | N/A | N/A | 0 | 0.000 s | none | 0 | 0 / 0 | 0 | 0 | 0 | not run / N/A | not checked |
| P3 B-01 | A4 | N/A | N/A | 0 | 0.000 s | none | 0 | 0 / 0 | 0 | 0 | 0 | not run / N/A | not checked |
| P4 A-01 | Baseline | N/A | N/A | 0 | 0.000 s | none | 0 | 0 / 0 | 0 | 0 | 0 | not run / N/A | not checked |
| P4 A-01 | A4 | N/A | N/A | 0 | 0.000 s | none | 0 | 0 / 0 | 0 | 0 | 0 | not run / N/A | not checked |

## Before and after deltas

| Task | Baseline wall | A4 wall | Wall delta | Call delta |
|---|---:|---:|---:|---:|
| P3 B-01 | N/A | N/A | N/A | N/A |
| P4 A-01 | N/A | N/A | N/A | N/A |
| Mean | N/A | N/A | N/A | N/A |

**False accepts observed: 0.** The arms did not run, so there is no A4 end-state verdict or independent shell check to score.

Build-time gate from the supplied brief, not rerun: 63 new tests pass; full suite 1402 tests, 7 failures, 2 skipped, zero new failures against the clean baseline of 1339 tests, 7 failures, 0 errors, 2 skipped.

## Teardown

- Final broker state: idle, owner null, started git HEAD `7f3da57a76382dd2a73e3da896c5aaf773f0acfd`.
- Relay active; Environment is `PYTHONDONTWRITEBYTECODE=1 XDG_CACHE_HOME=/home/james/.cache`, with no `CU_CODE_EXEC`.
- Final `hyprctl clients` listed three pre-existing clients: `org.omarchy.herdrdrop` (`omarchy: ~`), `zen` (`Pill video fixture (200 lines) - Zen Browser`), and `kitty` (`a4-exec`). `speed-a4-term` count is zero. No pre-existing client was closed.
- `/tmp/hoc-ky-2`, `/tmp/y-tuong.txt`, and `/tmp/a4-verify-fixture.txt` were removed.
- The required live-test log entry is appended and left uncommitted for the coordinator.

## Analyzer output

```text
== overall ==
records (excluding status polls): 15
status polls: 9
total logged sleeps: 0.0 s in 0 entries

== task a4 ==
  code-exec  n=2 service=0.220 s
  finish     n=3 service=0.825 s
  start      n=3 service=0.000 s
  status     n=2 service=0.145 s
  verify     n=2 service=0.140 s
  windows    n=3 service=0.364 s
  service total: 1.694 s
  image bytes total: 0
  start call: 0.194 s, ready: 0.917 s, polls: 3
  first request after ready: 8.755 s
  between-request gaps: n=14 total=391.249 s max=123.288 s
    gap a4-smoke-start -> a4-smoke-codeexec : 9.477 s
    gap a4-smoke-codeexec -> a4-smoke-reobserve : 35.233 s
    gap a4-smoke-reobserve -> a4-smoke-status : 28.762 s
    gap a4-smoke-status -> a4-smoke-abandoned-finish : 8.395 s
    gap a4-smoke-abandoned-finish -> a4-smoke-retry-start : 19.413 s
    gap a4-smoke-retry-start -> a4-smoke-retry-observe : 9.116 s
    gap a4-smoke-retry-observe -> a4-smoke-codeexec-retry : 8.341 s
    gap a4-smoke-codeexec-retry -> a4-smoke-verify-verified : 21.898 s
    gap a4-smoke-verify-verified -> a4-smoke-diagnostic-status : 30.151 s
    gap a4-smoke-diagnostic-status -> a4-smoke-refused-finish : 123.288 s
    gap a4-smoke-refused-finish -> a4-smoke-cli-retry-start : 15.734 s
    gap a4-smoke-cli-retry-start -> a4-smoke-cli-retry-observe : 9.076 s
    gap a4-smoke-cli-retry-observe -> a4-smoke-cli-retry-verify : 7.887 s
    gap a4-smoke-cli-retry-verify -> a4-smoke-cli-retry-finish : 64.476 s
  task span (first submit to last result): 393.512 s
  gap share of span: 99.4%, service share: 0.4%
  think/prep split (DECIDE lines):
    a4-smoke-codeexec      think=4.3 s prep=4.5 s
    a4-smoke-reobserve     think=30.9 s prep=4.4 s
    a4-smoke-status        think=25.3 s prep=3.5 s
    a4-smoke-abandoned-finish think=4.5 s prep=3.9 s
    a4-smoke-retry-observe think=4.2 s prep=4.2 s
    a4-smoke-codeexec-retry think=3.4 s prep=4.9 s
    a4-smoke-verify-verified think=17.4 s prep=4.5 s
    a4-smoke-refused-finish think=119.7 s prep=3.6 s
    a4-smoke-cli-retry-observe think=3.5 s prep=4.9 s
    a4-smoke-cli-retry-verify think=3.3 s prep=4.6 s
    a4-smoke-cli-retry-finish think=60.4 s prep=4.0 s

== grand totals (all tasks) ==
service total: 1.694 s, gap total: 391.249 s
```
