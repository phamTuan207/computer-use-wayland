# A2 flake-trigger run

Run date: 2026-11-20, Asia/Ho_Chi_Minh
Owner: Pham Tuan
Repo: /home/james/computer-use-wayland

## Setup

- Main checkout began at 56f5af4e521e1c20b26b56dc31d662e34f1c2668 and was checked out as detached a2-preflight at 296ce45715cc16d39e6fca63060cce70910d5019.
- Relay restarted with started_git_head 296ce45715cc16d39e6fca63060cce70910d5019. Broker was idle with owner null.
- CU_CODE_EXEC=1 was verified in the relay service environment.
- Target terminal title: speed-a2t-term. Exactly one matching Hyprland client was found, address 0x5564a6346fd0.
- timed.py md5: 82176e2a4b84691a1584ed68ce82953f. analyze.py md5: 39170ad8dcfd90016806f87ab50ee9df.
- Build-time gate supplied for A2, not rerun: full suite 1341 tests, 7 failures, 2 skipped, zero new failures against baseline 1339 tests, 7 failures, 0 errors, 2 skipped. tests/test_act_diagnostics.py passed 22/22.

## Trigger round trip

- Original get-colors output: `background              #282828`.
- set-colors background=#2e2e2e: exit 0, stdout empty, stderr empty.
- Get after set: `background              #2e2e2e`.
- set-colors background=#282828: exit 0, stdout empty, stderr empty.
- Get after restore: `background              #282828`.
- Trigger status: TRIGGER-AVAILABLE. Full get-colors stdout and stderr were saved as trigger-*.txt files in this run directory.

## Smoke

- Result: wrapper accepted=true, ok=true; inner code-exec result was ok=false, error_type=sandbox, error=`import is not allowed in a code-exec program`, api_calls=0, elapsed_ms=0.268. Session finished cleanly.
- Fallback: use the specified race method. The P3/P4 programs omit import time and time.sleep(3); the trigger background delay starts at 0.4 seconds. If a timing miss occurs, adjust the delay by 0.3 seconds for the single permitted retry and record the evidence.

## Task measurements

Wall is measured from session start submit to the final independent shell check. Strict and excluding dwell are equal because the import fallback removed the in-program sleep, dwell=0 s. Think totals use the analyzer DECIDE gaps before each code-exec request and the explicit P3 status call; finish-confirmation think is excluded. Each trigger attempt used one code-exec request. The task total adds one finish call, so a task with two trigger attempts used 3 model calls; a single-attempt run would use 2.

| Task and attempts | Wall excl dwell | Wall strict | Think excl dwell | Think strict | Model calls | Broker service | Requests | Refusals absorbed / escaped | Program retries | preflight_absorbed | preflight_retries | Diagnostics event | Shell check |
|---|---:|---:|---:|---:|---:|---|---|---|---:|---|---|---|---|
| P3, attempts 1 and 2 MISS | 335.899 s | 335.899 s | 247.2 s | 247.2 s | 3 | 2.482 s | code-exec x2, finish x1, status x1 | 0 / 0 | 1 | 0 | absent both | absent | MATCH, 4 dirs |
| P4, attempts 1 and 2 MISS | 96.981 s | 96.981 s | 53.0 s | 53.0 s | 3 | 2.940 s | code-exec x2, finish x1 | 0 / 0 | 1 | 0 | absent both | absent | MATCH |

For both tasks, the action returned ok=true and no preflight refusal. Therefore preflight_retries is absent and absorbed-retry success is N/A. No refusal means no global-mean or threshold diagnostic was emitted. The P3 status DECIDE entry was logged after the status call using its actual submit_wall timestamp, 06:14:29.040 +07; this is included in the analyzer think total and noted in progress.log.

## Comparison

| Task | This run, wall / think / calls / broker service | Pick 1 re-measure anchor, wall / think / calls | A4 baseline, wall / think / calls / broker service |
|---|---|---|---|
| P3 | 335.899 s / 247.2 s / 3 / 2.482 s | 20.72 s / 17.99 s / 4 | 34.760 s / 3.040 s / 2 / 1.091 s |
| P4 | 96.981 s / 53.0 s / 3 / 2.940 s | 20.58 s / 17.74 s / 3 | 23.752 s / 3.789 s / 2 / 1.360 s |

This run used two trigger attempts per task after the import fallback. Both task wall times are above the Pick 1 and A4 anchors. P3 used fewer calls than its Pick 1 anchor; P4 matched its Pick 1 call count and used one more call than the A4 baseline.

## Verdict

INCONCLUSIVE. The trigger round trip worked, but it produced 0 preflight refusals across 4 attempts, so live absorption is unproven. Both task actions succeeded and both independent shell checks matched. The supplied build-time gate still stands: tests/test_act_diagnostics.py 22/22 and no new full-suite failures against the clean baseline. The wall-time and call guard for WIN was not met.

## P3 B-01 record

- Status: task succeeded, trigger MISS on both permitted attempts. The action result was ok=true both times. No preflight refusal occurred, so this is not evidence of absorption.
- Session start submit: 2026-11-20 06:09:46.367 +07. Final independent shell check: 2026-11-20 06:15:22.266 +07. Wall excluding dwell: 335.899 s. Wall strict including dwell: 335.899 s. Race fallback had no in-program sleep, dwell=0 s.
- Attempt 1: trigger fired 06:10:32.830 and was restored at 06:10:33.528, values #2e2e2e and #282828. Initial observation was created at 06:10:32.666. Diagnostics show keyboard_group_started at 06:10:32.774, so the color change landed after preflight and during input. At blank sample pixel (800,550), the initial image was RGB (58,53,46) and verify image was RGB (63,58,51), confirming the background change reached verify. Result markers: preflight_absorbed absent, preflight_retries absent.
- Attempt 2: trigger fired 06:14:03.112 and was restored at 06:14:04.114. Initial observation capture started at 06:14:03.105 and was created at 06:14:03.190. The initial image sample at (800,550) was already RGB (63,58,51), so the trigger arrived during observation. Result markers: preflight_absorbed absent, preflight_retries absent.
- Diagnostics: /home/james/.cache/agent-computer-use/diagnostics-6d05af65545647c6.jsonl contains two keyboard groups and no preflight_absorb_retry event. Refusals: absorbed=0, escaped=0. Program retries: 1. Session deaths: 0. Misclicks: 0.
- Requests: 2 code-exec. Images: 6, total 2,694,897 bytes. Analyzer broker service total: 2.482 s, comprising code-exec requests 2.126 s, explicit status 0.084 s, finish 0.272 s. Start call 0.208 s and 3 internal status polls totaling 0.223 s are reported separately and excluded from analyzer service total.
- Independent shell evidence: `find /tmp/hoc-ky-2 -type d` listed exactly `/tmp/hoc-ky-2`, `/tmp/hoc-ky-2/dsa`, `/tmp/hoc-ky-2/ktvm`, `/tmp/hoc-ky-2/oop`; `SHELL_CHECK MATCH count 4`.
- Close decision: P3 is complete and verified; finish this broker session before P4.

## P4 A-01 record

- Status: task succeeded, trigger MISS on both permitted attempts. The action result was ok=true both times. No preflight refusal occurred, so this is not evidence of absorption.
- Session start submit: 2026-11-20 06:18:52.325 +07. Final independent shell check: 2026-11-20 06:20:29.306 +07. Wall excluding dwell: 96.981 s. Wall strict including dwell: 96.981 s. Race fallback had no in-program sleep, dwell=0 s.
- Attempt 1: trigger fired 06:19:12.409 and was restored at 06:19:13.416, values #2e2e2e and #282828. Initial observation was created at 06:19:12.238. Diagnostics show keyboard_group_started at 06:19:12.345, so the color change landed after preflight and during input. At blank sample pixel (800,550), the initial image was RGB (58,53,46) and verify image was RGB (63,58,51), confirming the background change reached verify. Result markers: preflight_absorbed absent, preflight_retries absent.
- Attempt 2: trigger fired 06:20:11.292 and was restored at 06:20:12.522. Initial observation capture started at 06:20:11.284 and was created at 06:20:11.359. The initial image sample at (800,550) was already RGB (63,58,51), so the trigger arrived during observation. No refusal or absorption marker followed.
- Diagnostics: /home/james/.cache/agent-computer-use/diagnostics-23a8d2856a0e8159.jsonl contains two keyboard groups and no preflight_absorb_retry event. Refusals: absorbed=0, escaped=0. Program retries: 1. Session deaths: 0. Misclicks: 0.
- Requests: 2 code-exec. Images: 6, total 2,793,061 bytes. Analyzer broker service total: 2.940 s, comprising code-exec requests 2.664 s and finish 0.276 s. Start call 0.175 s and 3 internal status polls totaling 0.222 s are reported separately and excluded from analyzer service total.
- Independent shell evidence: `cat /tmp/y-tuong.txt` printed the requested three UTF-8 lines. `sha256sum` returned `a6e58cb9f73ad08a588ed6668f72bcdc29b91af575860b35848c041d1ca7b170`; file size was 128 bytes. SHELL_CHECK MATCH.
- Close decision: P4 is complete and verified; finish this broker session.

## Teardown

- Restored and confirmed terminal background #282828, then focused only address 0x5564a6346fd0 and closed it with `hl.dsp.window.close()`.
- Final Hyprland check: 3 clients remained and speed-a2t-term count was 0. Reported titles were omarchy: ~, Pill video fixture (200 lines) - Zen Browser, and a2t-exec. No other client was changed.
- Removed /tmp/hoc-ky-2 and /tmp/y-tuong.txt. The kitty socket and a2t.conf drop-in are absent.
- Removed CU_CODE_EXEC, reloaded and restarted the relay. Relay is active, broker is idle with owner null, and Environment has no CU_CODE_EXEC.
- Restored checkout to 56f5af4e521e1c20b26b56dc31d662e34f1c2668, restarted relay, and verified started_git_head matches 56f5af4e521e1c20b26b56dc31d662e34f1c2668.
- records.jsonl contains 21 valid JSON lines. A captured window-title en dash was normalized to an ASCII hyphen in our request transcripts and records JSONL; no metric fields changed.
- Before the required live-test-log append, git status showed two untracked latency-probe result CSV files. They were left untouched. The live-test-log entry is appended separately and remains uncommitted for the coordinator.

## Analyzer output

```text
== overall ==
records (excluding status polls): 12
status polls: 9
total logged sleeps: 0.0 s in 0 entries

== task a2t ==
  code-exec  n=5 service=4.933 s
  finish     n=3 service=0.822 s
  start      n=3 service=0.000 s
  status     n=1 service=0.084 s
  service total: 5.839 s
  image bytes total: 5487958
  start call: 0.217 s, ready: 0.942 s, polls: 3
  first request after ready: 8.087 s
  between-request gaps: n=11 total=835.037 s max=236.683 s
    gap a2t-smoke-start -> a2t-smoke-req1 : 8.812 s
    gap a2t-smoke-req1 -> a2t-smoke-finish : 24.601 s
    gap a2t-smoke-finish -> a2t-p3-start : 100.349 s
    gap a2t-p3-start -> a2t-p3-req1 : 45.869 s
    gap a2t-p3-req1 -> a2t-p3-req2 : 209.519 s
    gap a2t-p3-req2 -> a2t-p3-status : 24.951 s
    gap a2t-p3-status -> a2t-p3-finish : 236.683 s
    gap a2t-p3-finish -> a2t-p4-start : 26.246 s
    gap a2t-p4-start -> a2t-p4-req1 : 19.522 s
    gap a2t-p4-req1 -> a2t-p4-req2 : 57.813 s
    gap a2t-p4-req2 -> a2t-p4-finish : 80.672 s
  task span (first submit to last result): 841.478 s
  gap share of span: 99.2%, service share: 0.7%
  think/prep split (DECIDE lines):
    a2t-smoke-req1         think=4.0 s prep=4.1 s
    a2t-smoke-finish       think=20.5 s prep=4.1 s
    a2t-p3-req1            think=24.3 s prep=20.9 s
    a2t-p3-req2            think=197.9 s prep=11.7 s
    a2t-p3-status          think=25.0 s prep=0.0 s
    a2t-p3-finish          think=232.7 s prep=4.0 s
    a2t-p4-req1            think=6.9 s prep=11.9 s
    a2t-p4-req2            think=46.1 s prep=11.7 s
    a2t-p4-finish          think=77.2 s prep=3.5 s

== grand totals (all tasks) ==
service total: 5.839 s, gap total: 835.037 s
```
