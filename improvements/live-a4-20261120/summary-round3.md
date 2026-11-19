# A4 live measurement, round 3

- Repo: `/home/james/computer-use-wayland`
- Repo HEAD: `7f3da57a76382dd2a73e3da896c5aaf773f0acfd` (`algo-a4`)
- Relay `started_git_head`: `7f3da57a76382dd2a73e3da896c5aaf773f0acfd`
- This round re-runs only P3 A4 with Python `True`, after round 2 used JSON `true` and raised `NameError: name 'true' is not defined`.
- Build-time gate, cited without rerunning: 63 new tests pass; full suite 1402 tests, 7 failures, 2 skipped, with zero new failures versus the clean baseline of 1339 tests, 7 failures, 0 errors, 2 skipped.
- Known finding, not retested: standalone relay `verify` is rejected as `unsupported_command` because `scripts/session_remote.py` line 41 omits `verify` from `COMMANDS`. The in-program `verify_postcondition()` path used here is not affected.

## Smoke

- Owner: `a4c-smoke`; code-exec returned `ok=true`.
- `api_calls`: 1. `elapsed_ms`: 1.505.
- Smoke session finished successfully.

## P3 B-01 A4, corrected program

- Target was cleaned immediately before session start with `shutil.rmtree`.
- Session start submit: 2026-11-20 03:11:40.133 +07:00. In-program postcondition returned verified: 2026-11-20 03:11:47.760 +07:00.
- Wall excluding dwell: 7.627 s. Wall strict: 7.627 s. Dwell: 0 s.
- Think before code-exec and think total: 5.728 s. Strict think: 5.728 s. Finish-confirmation think is excluded.
- Model calls: 2, one code-exec request plus finish. Start and status polls are excluded.
- Broker service: code-exec request 1.007 s, finish 0.155 s, total 1.162 s.
- Requests by kind: code-exec 1. Images: 2, 895615 bytes. Refusals 0, misclicks 0, session deaths 0, program retries 0.
- Postcondition status: verified. Envelope `postcondition_verified`: true. `api_calls`: 4.
- Independent shell check: MATCH. `find /tmp/hoc-ky-2 -type d` listed exactly four directories:

```text
/tmp/hoc-ky-2
/tmp/hoc-ky-2/oop
/tmp/hoc-ky-2/ktvm
/tmp/hoc-ky-2/dsa
```

Close decision: the envelope verified and the independent shell check matched, so no retry is needed. Finish this broker session after recording this section.

## P3 A4 delta versus round 2 baseline P3

| Metric | Round 2 baseline | Round 3 corrected A4 | Delta |
|---|---:|---:|---:|
| Wall excluding dwell / strict (s) | 34.760 / 34.760 | 7.627 / 7.627 | -27.133 / -27.133 |
| Think excluding dwell / strict (s) | 3.040 / 3.040 | 5.728 / 5.728 | +2.688 / +2.688 |
| Model calls | 2 | 2 | 0 |
| Broker service, code-exec request (s) | 1.091 | 1.007 | -0.084 |
| API calls | 4 | 4 | 0 |
| Images / bytes | 3 / 1343266 | 2 / 895615 | -1 / -447651 |
| Refusals / retries | 0 / 0 | 0 / 0 | 0 / 0 |
| Shell check | MATCH | MATCH | same |

False accepts: 0. The in-program verdict was verified and the independent shell check matched.

Verdict: WIN. P3 A4 verified all three directories, matched the independent shell check, and reduced wall time by 27.133 s with two model calls.

## Teardown

- Finished broker session `a4c-p3`: `ok=true`, driver stopped, guardian clean.
- Closed only `speed-a4c-term` at address `0x5564a64f5550` with `hl.dsp.window.close({ window = "address:0x5564a64f5550" })`; a subsequent Hyprland client query confirmed it was gone.
- Removed `/tmp/hoc-ky-2` with Python and removed the relay drop-in `a4.conf` with `Path.unlink`.
- Relay is active. Its environment no longer contains `CU_CODE_EXEC`. Broker status after restart: `started_git_head=7f3da57a76382dd2a73e3da896c5aaf773f0acfd`, `state=idle`, `owner=null`.
- Hyprland reports 3 remaining clients: `omarchy: ~`, Zen Browser, and `a4c-exec`; `speed-a4c-term` is absent. These remaining windows were left untouched.
- Checkout remains at `7f3da57a76382dd2a73e3da896c5aaf773f0acfd` on the `algo-a4` source; no checkout was performed during this round.
- Appended the P3 A4 result to `improvements/live-test-log.md`; the entry remains uncommitted for coordinator review. Before this append, Git already showed that log as modified and two latency-probe CSV files as untracked; those CSVs were left untouched.

## Analyzer output

```text
== overall ==
records (excluding status polls): 6
status polls: 6
total logged sleeps: 0.0 s in 0 entries

== task a4c ==
  code-exec  n=2 service=1.116 s
  finish     n=2 service=0.415 s
  start      n=2 service=0.000 s
  service total: 1.531 s
  image bytes total: 895615
  start call: 0.198 s, ready: 0.859 s, polls: 3
  first request after ready: 6.786 s
  between-request gaps: n=5 total=274.462 s max=204.472 s
    gap a4c-smoke-start -> a4c-smoke-code-exec : 7.447 s
    gap a4c-smoke-code-exec -> a4c-smoke-finish : 6.855 s
    gap a4c-smoke-finish -> a4c-p3-start : 49.262 s
    gap a4c-p3-start -> a4c-p3-code-exec : 6.427 s
    gap a4c-p3-code-exec -> a4c-p3-finish : 204.472 s
  task span (first submit to last result): 276.386 s
  gap share of span: 99.3%, service share: 0.6%
  think/prep split (DECIDE lines):
    a4c-smoke-code-exec    think=6.8 s prep=0.0 s
    a4c-smoke-finish       think=6.8 s prep=0.0 s
    a4c-p3-code-exec       think=5.7 s prep=0.0 s
    a4c-p3-finish          think=204.4 s prep=0.0 s

== grand totals (all tasks) ==
service total: 1.531 s, gap total: 274.462 s
```
