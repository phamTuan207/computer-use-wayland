# test-09-pomodoro-timer.md

## Test ID
test-09-pomodoro-timer

## Topic
Pomodoro workflow timer: custom settings configuration (work and break durations, auto-break toggle), timer state controls (start, pause, reset mistake), cycle completions, history logging, and session reporting.

## Context
the owner uses the offline Pomodoro timer to organize structured engineering sprints.
The workstation runs an offline browser timer (fixtures/test-09-pomodoro-timer.html).
Default durations are 25 minutes focus and 5 minutes break.
The user must open the settings modal, configure focus duration to 30 minutes and short break to 6 minutes, enable the "Auto-start next break cycle" checkbox, save the settings, start the first focus session, complete it via the cycle completion control, complete the subsequent short break, begin a second focus session, trigger a reset to simulate accidental interruption recovery, execute and complete the second focus session (totaling 2 focus cycles and 60 minutes of focus time), and save the session log.

## Timing
- Baseline start time: 2026-11-21 17:25:00 Asia/Ho_Chi_Minh
- Expected duration: 150 seconds elapsed
- Maximum allowable latency: 260 seconds elapsed

## Goal
Configure 30m work and 6m break, complete 2 focus cycles (60m total) and 1 break cycle, recover from an accidental reset, verify 3 logged history items, and save the session log.

## Exact steps
1. Open fixture tests/realistic/agy-q2/fixtures/test-09-pomodoro-timer.html in the browser.
2. Verify initial mode button "Focus Session" (id "btn-mode-work") is active and clock (id "timer-display") shows "25:00".
3. Click "Settings" button (id "btn-open-settings").
4. In modal, clear focus duration input (id "input-work-duration") and type "30".
5. Clear short break duration input (id "input-break-duration") and type "6".
6. Click the checkbox "Auto-start next break cycle" (id "check-auto-break") so it becomes checked.
7. Click "Save Settings" button (id "btn-save-settings").
8. Verify modal closes and clock display (id "timer-display") updates to "30:00".
9. Click "Start" button (id "btn-start-pause").
10. Verify button label changes to "Pause".
11. Click "Complete Cycle" button (id "btn-complete-cycle").
12. Verify session history logs "Session 1: Focus (30m, Focus)".
13. Verify mode automatically transitions to "Short Break" (id "btn-mode-short-break" gains active styling) and clock shows "06:00".
14. Click "Complete Cycle" button (id "btn-complete-cycle").
15. Verify session history logs "Session 2: Short Break (6m, Break)".
16. Verify mode switches back to "Focus Session" and clock shows "30:00".
17. Click "Start" button (id "btn-start-pause").
18. Accidental interruption simulation: click "Reset" button (id "btn-reset-timer").
19. Verify timer pauses and clock resets to "30:00" without appending an incomplete session to history.
20. Click "Complete Cycle" button (id "btn-complete-cycle") to finish the second focus sprint.
21. Verify session history logs "Session 3: Focus (30m, Focus)".
22. Verify completed focus cycles stat (id "stat-completed-cycles") displays "2".
23. Verify total focus time stat (id "stat-total-focus") displays "60 min".
24. Click "Save Session Log" button (id "btn-save-session").
25. Read status banner (id "pomodoro-status-banner") and confirm it displays "Session log saved: 2 focus cycles completed (60 min total focus)".

## Pass/fail criteria
- Pass: Work duration configured to 30 min, break configured to 6 min, auto-break checked, exactly 2 focus cycles completed totaling 60 min focus, 3 history entries present, and status banner confirms saved session log.
- Fail: Default durations unchanged, incomplete cycles, wrong focus duration total, or status banner unconfirmed.

## Errors designed to expose
- click miss: Settings modal controls or start/pause/reset buttons.
- modal uncommitted: Closing settings dialog without clicking Save Settings.
- mode confusion: Not noticing timer mode switch between focus and break.
- accidental reset handling: Misinterpreting reset button behavior during active sessions.
- fabrication: Asserting sprint completion without checking the history log rows.

## Checker / expected end state
```bash
node tests/realistic/agy-q2/check.mjs --fixture tests/realistic/agy-q2/fixtures/test-09-pomodoro-timer.html --test 09
```
