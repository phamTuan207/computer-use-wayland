# test-03-calendar-conflicts.md

## Test ID
test-03-calendar-conflicts

## Topic
Calendar scheduling across conflicts.

## Context
Pham Tuan needs to book a 30-minute project sync with two teammates across
three existing calendar events in a local calendar app. The fixture shows a
week view with existing busy blocks. The agent must find a free 30-minute slot
that does not conflict with any existing event on Tuesday, create the event,
invite both attendees, set a reminder, and confirm the event saves without
overlap. If no free slot exists on Tuesday, the agent must pick the earliest
free slot on Wednesday and document the conflict.

## Goal
Find a free 30-minute slot on Tuesday (or Wednesday if Tuesday is fully
blocked), create the sync event with 2 attendees and a 10-minute reminder, and
confirm it appears on the calendar without overlapping existing events.

## Exact steps
1. Open the calendar fixture `fixtures/test-03-calendar.html` in the local
   browser (offline, file:// URL).
2. Verify the week view is visible with Tuesday through Saturday shown.
3. Read all existing events on Tuesday: note title, start, end for each.
4. Read all existing events on Wednesday: note title, start, end for each.
5. Scan Tuesday 09:00-17:00 for a free 30-minute gap not touching any event.
6. Click the start of the first free Tuesday 30-minute gap.
7. Open the event creation dialog (click New Event or the time slot).
8. Set title to `Project sync`.
9. Set date to Tuesday and start time to the gap start.
10. Set duration to 30 minutes.
11. Add attendee 1 email.
12. Add attendee 2 email.
13. Set reminder to 10 minutes before.
14. Click Save.
15. Verify the new event appears on the Tuesday grid at the chosen time.
16. Verify no existing Tuesday event overlaps the new event (compare start/end
    minutes).
17. If step 5 found no Tuesday gap, click Wednesday, repeat steps 6-14 for the
    earliest free Wednesday gap, and record the day change.
18. Read back the saved event: title, date, time, duration, attendees,
    reminder.
19. Confirm the event block renders in the chosen day's column of the week
    grid within working hours (09:00-17:00).
20. Confirm the event does not appear on any other day.

## Pass/fail criteria
- Pass: event created with correct title/duration/attendees/reminder, placed in
  a genuine free gap, no overlap with existing events, saved to correct day.
- Fail: event overlaps an existing event, wrong duration, missing attendee,
  event on wrong day, creation dialog cancelled without saving.

## What to time
- Per-step wall time for each click/type/read (20 steps).
- Total wall time from step 1 to step 20.
- Time spent scanning for a free gap (conflict detection latency).
- Time re-reading the day view after save (stale observation check).

## Errors designed to expose
- click miss: clicking an existing event block instead of a free gap, opening
  the wrong dialog.
- slow think: long pause between reading busy blocks and picking a gap.
- stale observation: trusting a cached week view after saving, so the agent
  cannot see the new event.
- wrong diagnosis: concluding Tuesday is fully booked when a gap exists, or
  booking over an event because the block was misread.
- fabrication: claiming the event was saved when the dialog was cancelled.

## Checker / expected end state
Checker script: `tests/realistic/fcc-k/check.mjs --fixture
fixtures/test-03-calendar.html --test 03`.
Expected end state: one `Project sync` event, 30 minutes, 2 attendees,
10-minute reminder, on the chosen day in a free gap with zero overlap with
pre-existing events; if used, day changed from Tuesday to Wednesday documented.