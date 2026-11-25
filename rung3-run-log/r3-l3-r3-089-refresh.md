R3-089 fixture refresh (precondition 17).
Written 2026-11-24 17:34 +07 by the Phase 0 coordinator.

R3-089 (position 49, Codex) checks log files by mtime. The fixture has 12 log
files (log-01 to log-12). The key expects find -mtime -7 to return exactly 6
files (log-01 to log-06). The fixture is time-sensitive: the mtimes must be
set so that log-01..06 are within 7 days and log-07..12 are older than 7 days.

CURRENT FIXTURE STATE (verified 2026-11-25 08:59 +07, refreshed by touch -d "1 day ago"):
- log-01..06 mtime 2026-11-24 08:59:42 (within 7 days). find -mtime -7 returns 6.
- log-07..12 mtime 2026-11-15 08:59:42 (older than 7 days). find -mtime -7
  excludes them.
- HARD EXPIRY: 2026-12-01 08:59 +07. After that, log-01..06 are older than
  7 days and find -mtime -7 returns 0, not 6. The task becomes ungradeable.

REFRESH OWNER AND DATE:
- Owner: the run coordinator (whoever is coordinating when R3-089 approaches).
  The coordinator is responsible for refreshing the fixture the day before
  R3-089 runs. If the coordinator is unavailable, the deputy does it.
- Refresh date: the day before R3-089 runs. R3-089 is position 49 (Codex
  lane, second half of the run). The coordinator will know the run date when
  the run starts; the refresh is done 1 day before the task, not earlier
  (refreshing too early risks the mtimes ageing past the window if the run
  slips).
- If the run has not reached R3-089 by 2026-11-30 12:00, the coordinator
  refreshes the fixture on 2026-11-30 (so it stays valid through 2026-12-07)
  and records the refresh here. (Date guard, final review 25/11.)

REFRESH PROCEDURE (run on the laptop, in ~/rung3-goc/nd09-logs/):
1. Confirm the current state first: run
   find ~/rung3-goc/nd09-logs -name "*.log" -mtime -7 | wc -l
   and record the count. If it is 6, the fixture is still valid; refresh
   only if the run date is within 1 day of expiry.
2. Refresh the mtimes:
   touch -d "1 day ago" ~/rung3-goc/nd09-logs/log-01.log
   touch -d "1 day ago" ~/rung3-goc/nd09-logs/log-02.log
   touch -d "1 day ago" ~/rung3-goc/nd09-logs/log-03.log
   touch -d "1 day ago" ~/rung3-goc/nd09-logs/log-04.log
   touch -d "1 day ago" ~/rung3-goc/nd09-logs/log-05.log
   touch -d "1 day ago" ~/rung3-goc/nd09-logs/log-06.log
   touch -d "10 days ago" ~/rung3-goc/nd09-logs/log-07.log
   touch -d "10 days ago" ~/rung3-goc/nd09-logs/log-08.log
   touch -d "10 days ago" ~/rung3-goc/nd09-logs/log-09.log
   touch -d "10 days ago" ~/rung3-goc/nd09-logs/log-10.log
   touch -d "10 days ago" ~/rung3-goc/nd09-logs/log-11.log
   touch -d "10 days ago" ~/rung3-goc/nd09-logs/log-12.log
   (Adjust the filenames to the actual log filenames in nd09-logs; the
   principle is log-01..06 = 1 day ago, log-07..12 = 10 days ago.)
3. Verify after the refresh:
   find ~/rung3-goc/nd09-logs -name "*.log" -mtime -7 | wc -l
   must return exactly 6. If it does not, do NOT run R3-089; fix the mtimes
   and re-verify.
4. Record the refresh here (date, time, who did it, and the post-refresh
   find count). Update the hard expiry to (refresh time + 7 days).
5. The refresh touches ONLY the mtimes in ~/rung3-goc/nd09-logs/. It does not
   change file contents. It does not touch the frozen key or list.

CONFIRMATION PROCEDURE (before R3-089 starts):
- The coordinator runs the find -mtime -7 count on the laptop and confirms
  it is exactly 6. This is done AFTER the reset that precedes R3-089 (so the
  live ~/rung3/nd09-logs/ matches the fixture) and BEFORE the runner starts.
- If the count is not 6, the coordinator refreshes the fixture (procedure
  above), re-verifies, and only then starts R3-089. If the refresh cannot
  make the count 6, the coordinator stops and reports to the owner (the
  task cannot be graded fairly).
- R3-089 is Class L (score-before-reset), so the runner waits for the grade.
  The grade uses the live find output, which is why the fixture mtimes
  matter.

REFRESH LOG:
- 2026-11-25 08:59 +07: fixture refreshed (touch -d "1 day ago" log-01..06, "10 days ago" log-07..12), count 6, expiry 2026-12-01 08:59. Verified by prepare (G-39).
- (earlier: fixture verified fresh 2026-11-24 17:07 +07, count 6, expiry 2026-11-29 19:20; superseded by the 25/11 refresh.)
