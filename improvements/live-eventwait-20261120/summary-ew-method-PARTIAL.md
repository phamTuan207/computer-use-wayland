# EVENT-WAIT-SEQ METHOD arm summary - PARTIAL (PAUSED 14:39 for CF26 upload task)

## Status

PARTIAL. The method arm was stopped mid-run by Pham Tuan's pause order at 14:39 on 20/11 (time-critical CF26 Polygon upload, deadline 17:00, broker is single-owner). The coordinator killed the executor (codex PID 1642399, SIGTERM, exit 143) and finished the broker session explicitly. No new live arm was started. This file records only what was measured before the stop; it is NOT a verdict.

## Setup (verified)

- Checkout event-wait-seq 3113fb1 (after the stash fix: log stashed as ewmethod-log, checkout succeeded, relay restarted to 3113fb1, suite gate cited: 1360 tests, 7 failures, 0 errors, FAIL set identical to the 1339-test baseline).
- Broker at setup: free (finished, owner h3land2-check, driver stopped, guardian clean, explicit_finish) after the sibling H3 land worker's D1 run ended.
- Terminal ewmethod-term launched, address saved, driven only through the broker.

## Measurements (partial, n=1)

Wall is start submit to the VERIFIED timestamp, from wall-clock.log. Calls count operation requests plus finish (session start and status polling excluded).

| Task | Wall s | Result | Observes | Re-observes | Sleeps | wait_for steps | Timeouts | Missed events | Waits absorbed |
| --- | ---: | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| P1 C-03 | 71.125 | VERIFIED 14:36:50, Avail 11G (then image; tesseract 116; own read and ground truth 11G) | 1 initial + then image | 0 | 0 | openwindow class=kitty title=ewmethod-term already:true 0.063 ms; activewindow already:true 0.032 ms | 0 | 0 | 2 |
| P2 E-04 | 54.038 | VERIFIED 14:38:27, 96.0 (then image; tesseract, own read, ground truth 96.0) | 1 initial + then image | 0 | 0 | activewindow already:true 0.036 ms | 0 | 0 | 1 |
| P3 B-01 | NOT VERIFIED | mkdir executed (act-dirt-mkdir-find-then, sequence 2, service 1.062s, ok true); the three subdirs dsa/ktvm/oop were present on disk at the stop, but the executor's verify step never ran | 1 initial + then image (unread) | 0 | 0 | none recorded before the stop | 0 | 0 | 0 |
| P4 A-01 | NOT RUN | No session started | 0 | 0 | 0 | none | 0 | 0 | 0 |
| Probe (wait_for live, real kitty open) | NOT RUN | Never started | 0 | 0 | 0 | openwindow and activewindow probes not run | 0 | 0 | 0 |

Requests per completed task: 3 (initial observe + act with then + finish), vs baseline 4 calls per task (P1/P2) with 2 observes and 1 sleep each. Baseline walls for comparison (same tasks, n=1): P1 102.939s, P2 46.349s. No speedup factor is claimed: think dominates both arms and n=1.

Honest read: both wait_for steps on P1/P2 answered already:true in 0.03-0.06 ms because the terminal was already open and focused, so no event-fired wait was exercised. The then-image judging worked (0 re-observes on P1/P2). The live probe that would have exercised a real event-fired openwindow wait never ran.

## Stop and teardown (coordinator, 14:39-14:41)

- 14:39: SIGTERM to executor codex PID 1642399 only (never pkill all codex); exit 143; kitty ewmethod-exec closed on its own.
- Broker session ewmethod-p3 finished explicitly via timed.py finish (label P3-STOP-finish, ok true, status finished, driver stopped, guardian clean, service 0.154s).
- Desktop: ewmethod-term kitty (PID 1645375) closed with SIGTERM to that PID only; verified gone. No codex processes left, no Chromium running. Test artifacts removed (rm -rf /tmp/hoc-ky-2, which P3 had created; /tmp/y-tuong.txt never existed).
- Restore: git checkout --detach 56f5af4, relay restart, verified started_git_head 56f5af4e521e1c20b26b56dc31d662e34f1c2668, broker state idle, owner null, driver idle, guardian idle (relay generation fcf9ec77). Log stash ewmethod-log popped (dropped); only the three pre-existing stashes remain (a4-live-measure, rust-rewrite-eval, Phase-B). Laptop log md5 0fee1435cfb43d554404caf487ed80f2 matches the backup. git status shows only the expected entries (M log + 4 untracked other-worker files).
- Note: loaded_code_sha256 stayed 84f65d16ad3dd26b23c1ef75d8614cbb8c1e6539d0512cce65c8c8111d65d4a5 across both the 56f5af4 and 3113fb1 relay generations; started_git_head did change correctly. The executor's suite-gate citation and wait_for grep at setup are the evidence the method code was live; the unchanged code hash is recorded here as an open observation, not a finding.

## What remains unmeasured

- Event-wait method arm remainder: P3 verify, P4, and the wait_for live probe (real kitty openwindow + activewindow event-fired waits). The A/B has no verdict yet.
- Task 2 (A2 finer delay sweep on P3/P4) has not started.
- Run dir: /tmp/speed-eventwait-20261120/ew-method (records.jsonl 23 lines, wall-clock.log, progress.log). Blocked first method attempt preserved at ew-method-blocked-1426.
