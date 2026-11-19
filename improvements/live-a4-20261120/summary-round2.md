# A4 live measurement, round 2

- Repo: `/home/james/computer-use-wayland`
- Repo HEAD: `7f3da57a76382dd2a73e3da896c5aaf773f0acfd`
- Relay `started_git_head`: `7f3da57a76382dd2a73e3da896c5aaf773f0acfd`
- Flag-off direct CLI envelope:

```json
{"ok": false, "status": "inconclusive", "needs_vision": true, "checks": [], "error": "deterministic verify is disabled; set CU_CODE_EXEC=1"}
```

## Smoke and CLI controls

The smoke code-exec completed with `ok=true`, `api_calls=1`, `elapsed_ms=1.471`.

Broker verify reproduction, recorded verbatim, not retried:

```json
{"cmd": "request", "label": "a4b-smoke-verify-repro", "kind": "verify", "sequence": 2, "submit_mono": 64637.537809375, "submit_wall": 1795117603.197092, "result_mono": 64637.590583317, "result_wall": 1795117603.2498655, "service_s": 0.053, "request_call_s": 0.053, "result_call_s": 0.0, "accepted": false, "ok": null, "status": null, "error": null, "request_error": "unsupported_command", "request_status": null, "request_files_private": ["/tmp/speed-a4-20261120/a4-measure2/a4b-smoke-verify-req2.json"]}
```

Relay allowlist evidence from `scripts/session_remote.py:41`:

```python
COMMANDS = {'observe', 'act', 'windows', 'doctor', 'status', 'browser', 'a11y', 'code-exec'}
```

The relay rejects `verify` before it reaches the driver.

Direct CLI control envelopes, each exit code 0:

Verified control:
```json
{"ok":true,"status":"verified","passed":["file_contains"],"failed":[],"checks":[{"kind":"file_contains","name":null,"passed":true,"detail":"contains 'beta two': sha256 c07ffe993ca796a8fdb4f125d1a25174a15bb906f4c9b533c4adaecb800c31cb, 31 bytes","subject":"/tmp/a4b-verify-fixture.txt"}],"needs_vision":false,"elapsed_ms":0.146}
```

Failed control:
```json
{"ok":false,"status":"failed","passed":[],"failed":["file_contains"],"checks":[{"kind":"file_contains","name":null,"passed":false,"detail":"missing 'this text is not in the file': sha256 c07ffe993ca796a8fdb4f125d1a25174a15bb906f4c9b533c4adaecb800c31cb, 31 bytes","subject":"/tmp/a4b-verify-fixture.txt"}],"needs_vision":false,"elapsed_ms":0.108}
```

Inconclusive control:
```json
{"ok":false,"status":"inconclusive","passed":["file_exists"],"failed":[],"checks":[{"kind":"file_exists","name":null,"passed":true,"detail":"exists: sha256 c07ffe993ca796a8fdb4f125d1a25174a15bb906f4c9b533c4adaecb800c31cb, 31 bytes","subject":"/tmp/a4b-verify-fixture.txt"}],"needs_vision":true,"elapsed_ms":0.172,"error":"checks passed but no exact proof: add a file_contains, file_equals or dom_text check, or a second check of another kind"}
```

## P3 B-01 baseline, a4bbase-p3

- Target was cleaned immediately before start with `shutil.rmtree`.
- Session start submit: 2026-11-20 02:49:26.616 +07:00. End state shell check finished: 2026-11-20 02:50:01.376 +07:00.
- Wall excluding dwell: 34.760 s. Wall strict: 34.760 s. Dwell: 0 s.
- Think before code-exec and think total: 3.040 s.
- Model calls: 2 expected, one code-exec request plus finish. Start and polls excluded.
- Broker service so far: request 1.091 s; finish service is recorded after this section.
- Requests: code-exec 1. Images: 3, 1,343,266 bytes. Refusals 0, misclicks 0, session deaths 0, program retries 0.
- Postcondition status: not applicable to baseline program; it used post-act observe and file-exists assertions. Envelope `postcondition_verified`: absent. `api_calls`: 4.
- Independent shell check: MATCH. Evidence from `find /tmp/hoc-ky-2 -type d`:

```text
/tmp/hoc-ky-2
/tmp/hoc-ky-2/oop
/tmp/hoc-ky-2/ktvm
/tmp/hoc-ky-2/dsa
```

## P4 A-01 baseline, a4bbase-p4

- Target was cleaned immediately before start with `Path.unlink(missing_ok=True)`.
- Session start submit: 2026-11-20 02:51:24.471 +07:00. End state shell check finished: 2026-11-20 02:51:48.223 +07:00.
- Wall excluding dwell: 23.752 s. Wall strict: 23.752 s. Dwell: 0 s.
- Think before code-exec and think total: 3.789 s.
- Model calls: 2 expected, one code-exec request plus finish. Start and polls excluded.
- Broker service so far: request 1.360 s; finish service is recorded after this section.
- Requests: code-exec 1. Images: 3, 1,357,091 bytes. Refusals 0, misclicks 0, session deaths 0, program retries 0.
- Postcondition status: not applicable to baseline program; it used post-act observe and file-contains assertions. Envelope `postcondition_verified`: absent. `api_calls`: 4.
- Independent shell check: MATCH. Exact text and SHA-256 evidence:

```text
Ý tưởng 1: app nhắc uống nước.
Ý tưởng 2: bot tóm tắt bài giảng.
Ý tưởng 3: web bán đồ secondhand.
a6e58cb9f73ad08a588ed6668f72bcdc29b91af575860b35848c041d1ca7b170  /tmp/y-tuong.txt
128 /tmp/y-tuong.txt
```

## P3 B-01 A4, a4b-p3, FAIL after one identical retry

- Target was cleaned immediately before start with `shutil.rmtree`.
- Session start submit: 2026-11-20 02:52:32.513 +07:00. End state shell check finished: 2026-11-20 02:53:29.351 +07:00.
- Wall excluding retry dwell: 37.657 s. Wall strict: 56.838 s. Retry diagnosis dwell: 19.181 s.
- Think before first code-exec and think excluding dwell: 2.913 s. Think strict including retry gap: 22.094 s.
- Model calls: 3 expected, two code-exec requests plus finish. Start and polls excluded.
- Broker service for requests: 1.826 s; finish service is recorded after this section.
- Requests: code-exec 2. Images: 0, 0 bytes. Refusals 0, misclicks 0, session deaths 0, program retries 1.
- Run 1 and identical retry both returned inner `ok=false`, `api_calls=3`, error verbatim: `name 'true' is not defined`. `postcondition_verified`: absent on both runs; the postcondition was not reached.
- Independent shell check after retry: MATCH. Evidence from `find /tmp/hoc-ky-2 -type d`:

```text
/tmp/hoc-ky-2
/tmp/hoc-ky-2/oop
/tmp/hoc-ky-2/ktvm
/tmp/hoc-ky-2/dsa
```

This is a program failure, not a false accept: no run returned a verified verdict.

## P4 A-01 A4, a4b-p4, PASS

- Target was cleaned immediately before start with `Path.unlink(missing_ok=True)`.
- Session start submit: 2026-11-20 02:54:22.896 +07:00. End state shell check finished: 2026-11-20 02:54:37.980 +07:00.
- Wall excluding dwell: 15.084 s. Wall strict: 15.084 s. Dwell: 0 s.
- Think before code-exec and think total: 2.893 s.
- Model calls: 2, one code-exec request plus finish. Start and polls excluded.
- Broker service so far: request 1.247 s; finish service is recorded after this section.
- Requests: code-exec 1. Images: 2, 934,923 bytes. Refusals 0, misclicks 0, session deaths 0, program retries 0.
- Postcondition status: verified. Envelope `postcondition_verified`: true. `api_calls`: 4.
- Independent shell check: MATCH. Exact text and SHA-256 evidence:

```text
Ý tưởng 1: app nhắc uống nước.
Ý tưởng 2: bot tóm tắt bài giảng.
Ý tưởng 3: web bán đồ secondhand.
a6e58cb9f73ad08a588ed6668f72bcdc29b91af575860b35848c041d1ca7b170  /tmp/y-tuong.txt
128 /tmp/y-tuong.txt
```

## Per-task comparison

| Arm | Wall excl / strict (s) | Think excl / strict (s) | Model calls | Broker service (s) | Requests | Images / bytes | Refusals / retries | API calls | Misclicks / deaths | Postcondition (`postcondition_verified`) | Shell check |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---|---|
| P3 baseline | 34.760 / 34.760 | 3.040 / 3.040 | 2 | 1.245 | code-exec 1 | 3 / 1,343,266 | 0 / 0 | 4 | 0 / 0 | N/A / absent | MATCH |
| P4 baseline | 23.752 / 23.752 | 3.789 / 3.789 | 2 | 1.519 | code-exec 1 | 3 / 1,357,091 | 0 / 0 | 4 | 0 / 0 | N/A / absent | MATCH |
| P3 A4 | 37.657 / 56.838 | 2.913 / 22.094 | 3 | 2.080 | code-exec 2 | 0 / 0 | 0 / 1 | 6 total, 3 per run | 0 / 0 | FAIL / absent on both runs | MATCH |
| P4 A4 | 15.084 / 15.084 | 2.893 / 2.893 | 2 | 1.502 | code-exec 1 | 2 / 934,923 | 0 / 0 | 4 | 0 / 0 | verified / true | MATCH |

Dwell was 0 s except P3 A4, where retry diagnosis dwell was 19.181 s. Model calls count timed requests plus finish; start and status polls are excluded. Broker service includes request and finish calls.

## A4 minus baseline

| Task | Metric | Baseline | A4 | Delta |
|---|---|---:|---:|---:|
| P3 | Wall excluding dwell (s) | 34.760 | 37.657 | +2.897 |
| P3 | Wall strict (s) | 34.760 | 56.838 | +22.078 |
| P3 | Think excluding dwell (s) | 3.040 | 2.913 | -0.127 |
| P3 | Think strict (s) | 3.040 | 22.094 | +19.054 |
| P3 | Model calls | 2 | 3 | +1 |
| P4 | Wall excluding dwell (s) | 23.752 | 15.084 | -8.668 |
| P4 | Wall strict (s) | 23.752 | 15.084 | -8.668 |
| P4 | Think excluding dwell (s) | 3.789 | 2.893 | -0.896 |
| P4 | Think strict (s) | 3.789 | 2.893 | -0.896 |
| P4 | Model calls | 2 | 2 | 0 |
| Mean | Wall excluding dwell (s) | 29.256 | 26.371 | -2.886 |
| Mean | Wall strict (s) | 29.256 | 35.961 | +6.705 |
| Mean | Think excluding dwell (s) | 3.415 | 2.903 | -0.512 |
| Mean | Think strict (s) | 3.415 | 12.494 | +9.079 |
| Mean | Model calls | 2.000 | 2.500 | +0.500 |

False accepts: 0. P4 A4 returned verified and matched the independent shell check. P3 A4 returned no verified verdict on either attempt, although the shell state matched; this is a program failure and not a false accept.

## Teardown

- Closed only `speed-a4b-term` with `hl.dsp.window.close({ window = "address:0x5564a64f5550" })`; a subsequent Hyprland client query confirmed it was gone.
- Removed `/tmp/hoc-ky-2`, `/tmp/y-tuong.txt`, `/tmp/a4b-verify-fixture.txt`, and the relay drop-in `a4.conf`.
- Relay is active. Its environment no longer contains `CU_CODE_EXEC`. Broker status after restart: `started_git_head=7f3da57a76382dd2a73e3da896c5aaf773f0acfd`, `state=idle`, `owner=null`.
- Hyprland reports zero `speed-a4b-term` clients. The remaining reported clients include `omarchy: ~`, Zen Browser, and `a4b-exec`. The `a4b-exec` process was a separate Codex exec using `brief-a4b.md`; it was left untouched.
- `timed.py status` using the already finished lease returned `ok=false` with a null state. The read-only broker status check after restart confirmed the required idle state.
- Checkout remains on `algo-a4` at `7f3da57a76382dd2a73e3da896c5aaf773f0acfd`.

Verdict: LOSS. P4 A4 reduced wall time but did not reduce calls; P3 A4 failed twice with `name 'true' is not defined`, so the success bar was not met.

## Analyzer output

```text
== overall ==
records (excluding status polls): 18
status polls: 15
total logged sleeps: 0.0 s in 0 entries

== task a4b ==
  code-exec  n=4 service=3.182 s
  finish     n=3 service=0.763 s
  start      n=3 service=0.000 s
  status     n=1 service=0.048 s
  verify     n=1 service=0.053 s
  service total: 4.046 s
  image bytes total: 934923
  start call: 0.160 s, ready: 0.825 s, polls: 3
  first request after ready: 8.099 s
  between-request gaps: n=11 total=737.245 s max=323.542 s
    gap a4b-smoke-start -> a4b-smoke-code-exec : 8.763 s
    gap a4b-smoke-code-exec -> a4b-smoke-verify-repro : 12.797 s
    gap a4b-smoke-verify-repro -> a4b-smoke-finish : 25.468 s
    gap a4b-smoke-finish -> a4b-p3-start : 323.542 s
    gap a4b-p3-start -> a4b-p3-code-exec : 7.707 s
    gap a4b-p3-code-exec -> a4b-p3-code-exec-retry : 23.577 s
    gap a4b-p3-code-exec-retry -> a4b-p3-finish : 65.143 s
    gap a4b-p3-finish -> a4b-p4-start : 11.718 s
    gap a4b-p4-start -> a4b-p4-code-exec : 7.737 s
    gap a4b-p4-code-exec -> a4b-p4-finish : 32.786 s
    gap a4b-p4-finish -> a4b-p4-teardown-status : 218.007 s
  task span (first submit to last result): 741.771 s
  gap share of span: 99.4%, service share: 0.5%
  think/prep split (DECIDE lines):
    a4b-smoke-code-exec    think=3.9 s prep=4.2 s
    a4b-smoke-verify-repro think=8.6 s prep=4.2 s
    a4b-smoke-finish       think=21.4 s prep=4.1 s
    a4b-p3-code-exec       think=2.9 s prep=4.1 s
    a4b-p3-code-exec-retry think=19.2 s prep=4.4 s
    a4b-p3-finish          think=61.2 s prep=4.0 s
    a4b-p4-code-exec       think=2.9 s prep=4.2 s
    a4b-p4-finish          think=28.5 s prep=4.3 s
    a4b-p4-teardown-status think=213.9 s prep=4.1 s

== task a4bbase ==
  code-exec  n=2 service=2.451 s
  finish     n=2 service=0.313 s
  start      n=2 service=0.000 s
  service total: 2.764 s
  image bytes total: 2700357
  start call: 0.190 s, ready: 0.854 s, polls: 3
  first request after ready: 7.299 s
  between-request gaps: n=5 total=168.534 s max=96.230 s
    gap a4bbase-p3-start -> a4bbase-p3-code-exec : 7.964 s
    gap a4bbase-p3-code-exec -> a4bbase-p3-finish : 96.230 s
    gap a4bbase-p3-finish -> a4bbase-p4-start : 12.226 s
    gap a4bbase-p4-start -> a4bbase-p4-code-exec : 9.575 s
    gap a4bbase-p4-code-exec -> a4bbase-p4-finish : 42.539 s
  task span (first submit to last result): 171.696 s
  gap share of span: 98.2%, service share: 1.6%
  think/prep split (DECIDE lines):
    a4bbase-p3-code-exec   think=3.0 s prep=4.3 s
    a4bbase-p3-finish      think=91.8 s prep=4.4 s
    a4bbase-p4-code-exec   think=3.8 s prep=5.1 s
    a4bbase-p4-finish      think=37.9 s prep=4.7 s

== grand totals (all tasks) ==
service total: 6.810 s, gap total: 905.778 s
