# test-05-calendar-recurring.md

## Test ID
test-05-calendar-recurring

## Topic
Calendar recurring event creation, editing one occurrence versus the series, deletion recovery, and occurrence count verification.

## Context
A coordinator creates a five-week Monday series in Calendar Studio. They rename only the November 30 occurrence, change the location for the whole series, recover from deleting the wrong occurrence, then delete December 21 only. The fixed dates make occurrence counts reproducible. The fixture is tests/realistic/codex-y5/fixtures/test-05-calendar-recurring.html.

## Timing
- Baseline start time: 2026-11-21 18:21:00 Asia/Ho_Chi_Minh
- Expected duration: 270 seconds elapsed
- Maximum allowable latency: 390 seconds elapsed

## Goal
Keep four scheduled occurrences after deleting December 21, with November 30 titled Design review prep and the series location set to Room Cedar.

## Exact steps
1. Open tests/realistic/codex-y5/fixtures/test-05-calendar-recurring.html in the browser.
2. Verify #occurrence-count text is "0", #calendar-summary text is "No events", #delete-status text is "No occurrence deleted", and #series-location-summary text is "None".
3. Type "Design review" into #event-title-input; its value must be "Design review".
4. Type "2026-11-23" into #event-start-date; its value must be "2026-11-23".
5. Type "Room Ash" into #event-location-input; its value must be "Room Ash".
6. Select value "weekly" in #repeat-frequency; the selected value must be "weekly".
7. Replace #occurrence-limit value with "5".
8. Click button #btn-create-event; #occurrence-count must become "5".
9. Verify #calendar-summary text is "5 of 5 occurrences scheduled" and #create-status text is "Created weekly series: Design review (5 occurrences)".
10. Click button #btn-edit-1130 for the November 30 occurrence; #edit-occurrence-date must become "2026-11-30".
11. Verify #edit-scope value is "this" and #edit-event-title value is "Design review".
12. Replace #edit-event-title value with "Design review prep".
13. Click button #btn-save-event-changes; #title-1130 must become "Design review prep".
14. Verify #occurrence-count text is "5", #title-1130 text is "Design review prep", and #title-1123 text is "Design review".
15. Click button #btn-edit-1123 for the November 23 occurrence; #edit-occurrence-date must become "2026-11-23".
16. Select value "series" in #edit-scope; the selected value must be "series".
17. Replace #edit-event-location value with "Room Cedar".
18. Click button #btn-save-event-changes; #series-location-summary must become "Room Cedar".
19. Verify #series-location-summary text is "Room Cedar", #title-1130 text is "Design review prep", and #title-1207 text is "Design review".
20. Mistake: click button #btn-delete-1207 and delete the wrong December 7 occurrence; #occurrence-count must drop to "4".
21. Verify #delete-status text is "Deleted 2026-12-07" and #occurrence-summary text is exactly "2026-11-23 | Design review | Room Cedar\n2026-11-30 | Design review prep | Room Cedar\n2026-12-14 | Design review | Room Cedar\n2026-12-21 | Design review | Room Cedar".
22. Recovery: click button #btn-undo-calendar-delete; #occurrence-count must return to "5".
23. Verify #delete-status text is "Last occurrence restored" and #occurrence-summary text is exactly "2026-11-23 | Design review | Room Cedar\n2026-11-30 | Design review prep | Room Cedar\n2026-12-07 | Design review | Room Cedar\n2026-12-14 | Design review | Room Cedar\n2026-12-21 | Design review | Room Cedar".
24. Click button #btn-delete-1221 to delete only the December 21 occurrence; #occurrence-count must become "4".
25. Verify #delete-status text is "Deleted 2026-12-21" and #occurrence-summary text is exactly "2026-11-23 | Design review | Room Cedar\n2026-11-30 | Design review prep | Room Cedar\n2026-12-07 | Design review | Room Cedar\n2026-12-14 | Design review | Room Cedar".
26. Verify #calendar-summary text is "4 of 5 occurrences scheduled", #occurrence-summary text is exactly "2026-11-23 | Design review | Room Cedar\n2026-11-30 | Design review prep | Room Cedar\n2026-12-07 | Design review | Room Cedar\n2026-12-14 | Design review | Room Cedar", #title-1130 text is "Design review prep", #title-1123 text is "Design review", #title-1207 text is "Design review", #title-1214 text is "Design review", and #series-location-summary text is "Room Cedar".

## Pass/fail criteria
- Pass: Four of five occurrences remain, only November 30 has the edited title, all remaining events use Room Cedar, and December 21 is absent.
- Fail: Editing changes the whole series title, changing the series location updates only one date, deletion affects the wrong occurrence, or the count is not four.

## Errors designed to expose
- click miss: Repeated event rows place Edit and Delete controls beside each date.
- slow think: The workflow switches between single-occurrence and series scopes.
- stale observation: The occurrence count changes after delete, undo, and final delete.
- wrong diagnosis: Deleting December 7 is an intentional mistake that must be restored before deleting December 21.
- fabrication: The five dates, remaining four dates, titles, and location are checked exactly.

## Checker / expected end state
```bash
node tests/realistic/codex-y5/check.mjs --fixture tests/realistic/codex-y5/fixtures/test-05-calendar-recurring.html --test 05
```
