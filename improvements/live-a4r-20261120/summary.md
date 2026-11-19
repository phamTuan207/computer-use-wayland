# A4 relay path re-test

Date: 2026-11-20, Asia/Ho_Chi_Minh
Repo HEAD: `7f259ffb172fda1fc553a2107c82c875ec986e38` (`7f259ff`).
Relay `started_git_head`: `7f259ffb172fda1fc553a2107c82c875ec986e38`.
Build-time gate, cited and not rerun: full suite 1404 tests, 7 failures, 0 errors, 2 skipped, zero new failures.

## Smoke verify controls

Code-exec smoke: accepted=true, ok=true, api_calls=1, elapsed_ms=2.361.
Expected control outcomes observed: verified, failed, inconclusive with needs_vision=true.

### A. Verified control

Verbatim envelope:

```json
{"cmd": "request", "label": "a4r-smoke-verify-a", "kind": "verify", "sequence": 2, "submit_mono": 75136.15358641, "submit_wall": 1795128101.812869, "result_mono": 75136.302467062, "result_wall": 1795128101.961749, "service_s": 0.149, "request_call_s": 0.074, "result_call_s": 0.074, "accepted": true, "ok": true, "status": "completed", "error": null, "request_error": null, "request_status": "accepted", "request_files_private": ["/tmp/speed-a4r-20261120/a4-relay/a4r-smoke-verify-a-req2.json"], "driver_returncode": 0, "result": {"ok": true, "status": "verified", "passed": ["file_contains"], "failed": [], "checks": [{"kind": "file_contains", "name": null, "passed": true, "detail": "contains 'beta two': sha256 c07ffe993ca796a8fdb4f125d1a25174a15bb906f4c9b533c4adaecb800c31cb, 31 bytes", "subject": "/tmp/a4r-fixture.txt"}], "needs_vision": false, "elapsed_ms": 0.132}}
```

### B. Failed control

Verbatim envelope:

```json
{"cmd": "request", "label": "a4r-smoke-verify-b", "kind": "verify", "sequence": 3, "submit_mono": 75144.299067843, "submit_wall": 1795128109.9583507, "result_mono": 75144.442052989, "result_wall": 1795128110.1013348, "service_s": 0.143, "request_call_s": 0.075, "result_call_s": 0.068, "accepted": true, "ok": true, "status": "completed", "error": null, "request_error": null, "request_status": "accepted", "request_files_private": ["/tmp/speed-a4r-20261120/a4-relay/a4r-smoke-verify-b-req3.json"], "driver_returncode": 0, "result": {"ok": false, "status": "failed", "passed": [], "failed": ["file_contains"], "checks": [{"kind": "file_contains", "name": null, "passed": false, "detail": "missing 'this text is not in the file': sha256 c07ffe993ca796a8fdb4f125d1a25174a15bb906f4c9b533c4adaecb800c31cb, 31 bytes", "subject": "/tmp/a4r-fixture.txt"}], "needs_vision": false, "elapsed_ms": 0.08}}
```

### C. Inconclusive control

Verbatim envelope:

```json
{"cmd": "request", "label": "a4r-smoke-verify-c", "kind": "verify", "sequence": 4, "submit_mono": 75152.619548713, "submit_wall": 1795128118.2788312, "result_mono": 75152.763840934, "result_wall": 1795128118.4231226, "service_s": 0.144, "request_call_s": 0.074, "result_call_s": 0.07, "accepted": true, "ok": true, "status": "completed", "error": null, "request_error": null, "request_status": "accepted", "request_files_private": ["/tmp/speed-a4r-20261120/a4-relay/a4r-smoke-verify-c-req4.json"], "driver_returncode": 0, "result": {"ok": false, "status": "inconclusive", "passed": ["file_exists"], "failed": [], "checks": [{"kind": "file_exists", "name": null, "passed": true, "detail": "exists: sha256 c07ffe993ca796a8fdb4f125d1a25174a15bb906f4c9b533c4adaecb800c31cb, 31 bytes", "subject": "/tmp/a4r-fixture.txt"}], "needs_vision": true, "elapsed_ms": 0.083, "error": "checks passed but no exact proof: add a file_contains, file_equals or dom_text check, or a second check of another kind"}}
```

## P3 B-01

Task: create `/tmp/hoc-ky-2` with subdirectories `dsa`, `ktvm`, `oop`.
P3 target was confirmed absent immediately before session start.
Wall start: 2026-11-20T05:43:18.527+07:00 HCM.
End state independently verified: 2026-11-20T05:44:23.376+07:00 HCM.
Evidence: `find /tmp/hoc-ky-2 -type d` listed exactly 4 directories and the independent check was MATCH.

Relay verify envelope, verbatim:

```json
{"cmd": "request", "label": "p3-verify", "kind": "verify", "sequence": 2, "submit_mono": 75255.375337664, "submit_wall": 1795128221.0346205, "result_mono": 75255.523052959, "result_wall": 1795128221.182339, "service_s": 0.148, "request_call_s": 0.076, "result_call_s": 0.072, "accepted": true, "ok": true, "status": "completed", "error": null, "request_error": null, "request_status": "accepted", "request_files_private": ["/tmp/speed-a4r-20261120/a4-relay/a4r-p3-verify-req2.json"], "driver_returncode": 0, "result": {"ok": true, "status": "verified", "passed": ["file_exists", "file_exists", "file_exists"], "failed": [], "checks": [{"kind": "file_exists", "name": null, "passed": true, "detail": "directory exists: /tmp/hoc-ky-2/dsa", "subject": "/tmp/hoc-ky-2/dsa"}, {"kind": "file_exists", "name": null, "passed": true, "detail": "directory exists: /tmp/hoc-ky-2/ktvm", "subject": "/tmp/hoc-ky-2/ktvm"}, {"kind": "file_exists", "name": null, "passed": true, "detail": "directory exists: /tmp/hoc-ky-2/oop", "subject": "/tmp/hoc-ky-2/oop"}], "needs_vision": false, "elapsed_ms": 0.087}}
```

P3 metrics:

| Wall excl dwell | Wall strict | Think excl dwell | Think strict | Think before code-exec | Model calls | Broker service | Requests | Refusals | Retries | Relay verify | Shell check |
|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|---|
| 64.848s | 64.848s | 20.485s | 20.485s | 8.858s | 3 | 1.265s | code-exec 1, verify 1 | 0 | 0 | verified | MATCH |

Close deliberation: end the broker session now, then close the retained target window through the prescribed Hyprland dispatcher during teardown.

Additional P3 observations: 3 images, 1,342,744 bytes; refusals 0; misclicks 0; session deaths 1 inferred idle timeout; program retries 0. Code-exec result: api_calls=4, elapsed_ms=976.086. The 352.420 s gap from verify result to finish exceeded the 300 s idle timeout. Finish then returned status=finished, driver=stopped, guardian=clean.

## Per-session table

| Session | Wall excl dwell | Wall strict | Think excl dwell | Think strict | Think before code-exec | Model calls | Broker service | Requests | Refusals | Retries | Relay verify | Shell check |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---|---|
| Smoke controls | 55.347s | 55.347s | 44.349s | 44.349s | 15.616s | 5 | 0.861s | code-exec 1, verify 3 | 0 | 0 | controls passed | n/a |
| P3 B-01 | 64.848s | 64.848s | 20.485s | 20.485s | 8.858s | 3 | 1.265s | code-exec 1, verify 1 | 0 | 0 | verified | MATCH |

False accepts: 0. Evidence: P3 relay returned verified and the independent shell check matched all four directories.

Verdict: WORKS. All three smoke controls were accepted with expected statuses, P3 relay verify was accepted and verified, and the independent shell check matched.

Session timeout note: the P3 result was complete at 05:44:23.376 HCM. The relay verify result was at 05:43:41.182 HCM, and finish was submitted at 05:49:33.602 HCM. The idle timeout is inferred from the 352.420 s request gap.

## Analyzer output

```text
== overall ==
records (excluding status polls): 10
status polls: 6
total logged sleeps: 1.0 s in 1 entries
  sleep 05:39:56.071 1.0s wait for target Kitty window to register

== task a4r ==
  code-exec  n=1 service=0.148 s
  finish     n=1 service=0.277 s
  start      n=1 service=0.000 s
  verify     n=3 service=0.436 s
  service total: 0.861 s
  image bytes total: 0
  start call: 0.186 s, ready: 0.906 s, polls: 3
  first request after ready: 15.646 s
  between-request gaps: n=5 total=54.299 s max=16.366 s
    gap a4r-smoke-start -> a4r-smoke-code-exec : 16.366 s
    gap a4r-smoke-code-exec -> a4r-smoke-verify-a : 12.649 s
    gap a4r-smoke-verify-a -> a4r-smoke-verify-b : 7.997 s
    gap a4r-smoke-verify-b -> a4r-smoke-verify-c : 8.177 s
    gap a4r-smoke-verify-c -> a4r-smoke-finish : 9.110 s
  task span (first submit to last result): 55.347 s
  gap share of span: 98.1%, service share: 1.6%
  think/prep split (DECIDE lines):
    a4r-smoke-code-exec    think=15.6 s prep=0.0 s
    a4r-smoke-verify-a     think=12.6 s prep=0.0 s
    a4r-smoke-verify-b     think=8.0 s prep=0.0 s
    a4r-smoke-verify-c     think=8.1 s prep=0.0 s
    a4r-smoke-finish       think=9.1 s prep=0.0 s

== task p3 ==
  code-exec  n=1 service=1.064 s
  finish     n=1 service=0.053 s
  start      n=1 service=0.000 s
  verify     n=1 service=0.148 s
  service total: 1.265 s
  image bytes total: 1342744
  start call: 0.172 s, ready: 0.893 s, polls: 3
  first request after ready: 8.889 s
  between-request gaps: n=3 total=373.691 s max=352.420 s
    gap p3-start -> p3-code-exec : 9.610 s
    gap p3-code-exec -> p3-verify : 11.660 s
    gap p3-verify -> p3-finish : 352.420 s
  task span (first submit to last result): 375.128 s
  gap share of span: 99.6%, service share: 0.3%
  think/prep split (DECIDE lines):
    p3-code-exec           think=8.9 s prep=0.0 s
    p3-verify              think=11.6 s prep=0.0 s
    p3-finish              think=352.4 s prep=0.0 s

== grand totals (all tasks) ==
service total: 2.126 s, gap total: 427.990 s
```

## Analyzer output

== overall ==
records (excluding status polls): 10
status polls: 6
total logged sleeps: 1.0 s in 1 entries
  sleep 05:39:56.071 1.0s wait for target Kitty window to register

== task a4r ==
  code-exec  n=1 service=0.148 s
  finish     n=1 service=0.277 s
  start      n=1 service=0.000 s
  verify     n=3 service=0.436 s
  service total: 0.861 s
  image bytes total: 0
  start call: 0.186 s, ready: 0.906 s, polls: 3
  first request after ready: 15.646 s
  between-request gaps: n=5 total=54.299 s max=16.366 s
    gap a4r-smoke-start -> a4r-smoke-code-exec : 16.366 s
    gap a4r-smoke-code-exec -> a4r-smoke-verify-a : 12.649 s
    gap a4r-smoke-verify-a -> a4r-smoke-verify-b : 7.997 s
    gap a4r-smoke-verify-b -> a4r-smoke-verify-c : 8.177 s
    gap a4r-smoke-verify-c -> a4r-smoke-finish : 9.110 s
  task span (first submit to last result): 55.347 s
  gap share of span: 98.1%, service share: 1.6%
  think/prep split (DECIDE lines):
    a4r-smoke-code-exec    think=15.6 s prep=0.0 s
    a4r-smoke-verify-a     think=12.6 s prep=0.0 s
    a4r-smoke-verify-b     think=8.0 s prep=0.0 s
    a4r-smoke-verify-c     think=8.1 s prep=0.0 s
    a4r-smoke-finish       think=9.1 s prep=0.0 s

== task p3 ==
  code-exec  n=1 service=1.064 s
  finish     n=1 service=0.053 s
  start      n=1 service=0.000 s
  verify     n=1 service=0.148 s
  service total: 1.265 s
  image bytes total: 1342744
  start call: 0.172 s, ready: 0.893 s, polls: 3
  first request after ready: 8.889 s
  between-request gaps: n=3 total=373.691 s max=352.420 s
    gap p3-start -> p3-code-exec : 9.610 s
    gap p3-code-exec -> p3-verify : 11.660 s
    gap p3-verify -> p3-finish : 352.420 s
  task span (first submit to last result): 375.128 s
  gap share of span: 99.6%, service share: 0.3%
  think/prep split (DECIDE lines):
    p3-code-exec           think=8.9 s prep=0.0 s
    p3-verify              think=11.6 s prep=0.0 s
    p3-finish              think=352.4 s prep=0.0 s

== grand totals (all tasks) ==
service total: 2.126 s, gap total: 427.990 s
