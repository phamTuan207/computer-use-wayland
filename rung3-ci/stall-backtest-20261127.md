# M7 stall detector backtest (2026-11-27)

Detector: `rung3-ci/stall-detector.py`. Flag rule: a gap longer than
the threshold in the UNION of activity timestamps (heartbeat log,
per-task reports, grades recorded_at, git commits touching
rung3-run-log/). Flags are for human judgement only; the detector
triggers nothing.

## Logs scanned (repo, aggregates only)

- Heartbeat log: 119 events, 2026-11-25 13:06 to 2026-11-26 07:58 +07.
- Per-task reports: 15 timestamped rows in the run window.
- Grades ledger: 59 graded tasks (test row excluded).
- Git ledger commits: 333 in the run window (395 all-time).
- Run window used: 2026-11-25T13:00+07:00 to 2026-11-27T05:00+07:00.
- Union events in window: 470.

## Reproduced study numbers

- Post-run latency (task_end to recorded_at): 59 tasks, total
  953.6 min, max 51.2 min. Matches the study 954 min table.
- Heartbeat gaps over 30 min: exactly 3 (55.8, 49.9, 98.7 min).
  Matches the study count.

## M7 backtest conditions

1. Fire on the 2026-11-27 stall window: PASS at every threshold
   15-60 min. Flag: 70.9 min, 2026-11-27 03:31 to 04:42 +07
   (task 56 drive launched 03:28, owner decision 04:41).
2. Stay silent across the 2026-11-25 owner-corrected window: PASS.
   A git-only detector flags the 91 min ledger gap
   2026-11-25 22:01 to 23:32 +07; the union detector does not,
   because 13 heartbeats cover that window (run healthy, tasks
   grading normally). Single-signal silence is not flagged.

## Threshold sweep (union flags in run window)

- 15 min: 39 flags. 20 min: 29. 30 min: 11. 45 min: 5. 60 min: 4.

Flags at 45 min, with disposition:

- 49.9 min, 2026-11-25 17:58 to 18:48: coordinator takeover gap
  (epoch 8). Real continuity episode. True positive class.
- 87.5 min, 2026-11-26 05:05 to 06:32: owner-ordered pause and
  resume checks. Intentional pause; human dismisses.
- 189.7 min, 2026-11-26 09:03 to 12:13: owner-ordered run pause
  (in-flight work finished, then paused). Intentional; dismiss.
- 109.8 min, 2026-11-26 15:18 to 17:08: same pause period.
  Intentional; dismiss.
- 70.9 min, 2026-11-27 03:31 to 04:42: the documented stall.
  True positive.

At 30 min, six extra flags (30.2 to 39.0 min) are scoring-cadence
gaps on 2026-11-26, not stalls. At 60 min the 49.9 min takeover
gap is missed.

## Proposed threshold

45 min union silence. It catches both documented continuity
failures in the window (27 Nov stall, 25 Nov takeover), drops the
scoring-cadence noise seen at 30 min, and its only false positives
are the three documented intentional pauses on 2026-11-26, which a
human dismisses from pause state. The detector flags only; it must
never trigger or pre-authorise a takeover (M8 rejection stands).

## Known incidents outside repo log coverage

- 2026-11-19 two-hour stall and 2026-11-14 73-hour silent agent:
  repo logs start 2026-11-23 (git ledger) and 2026-11-25
  (heartbeat), so neither incident is covered. Checked the laptop
  master event log read-only (timestamps only, 7,022 events,
  2026-11-13 to 2026-11-19): no team-wide gap over 2 h exists,
  because other lanes kept logging. Both incidents were
  single-agent silence, which a team-union detector cannot see.
  Recorded as a scope limit, not a detector failure: per-agent
  silence needs per-agent signals, which M7 does not claim.

## Tests

`python3 rung3-ci/test-stall-detector.py`: 7 checks PASS
(synthetic fixtures: gap detection, union corroboration, parsers,
latency math, malformed input, missing files).

Backtest runtime: about 4 s on the VM including the git scan.
No live watchdog or cron wiring. Detector and backtest only.
