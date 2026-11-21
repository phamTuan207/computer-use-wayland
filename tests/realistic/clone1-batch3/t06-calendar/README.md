# t06-calendar: calendar event workflow

## Context

A demo month calendar starting at June 2026. The fixture world date
is fixed at 15 June 2026 so every run is deterministic. Clicking a
day opens an event form, events show as chips on their day, clicking
a chip opens details where the time can be edited or the event
deleted. Previous, Next, and Today move the visible month.

## Goal

Create events on several days, check them on the grid, edit one
event's time, delete another, move to another month and back, cancel
a new event, and return with Today.

## Steps

1. Open the fixture page, check the title is `June 2026`.
2. Check day 15 carries the today highlight.
3. Click day 12, check the form opens for `June 12, 2026`.
4. Add `Team sync` at 10:00, check the chip reads `10:00 Team sync`.
5. Add `Lunch` at 12:30 on day 12, check day 12 has 2 chips.
6. Add `Deadline` at 09:00 on day 20, check its chip.
7. Check the status reads `Events: 3`.
8. Click the Team sync chip, check the details title and meta.
9. Change the time to 11:00, update, check the details and the chip.
10. Open the Lunch chip, delete it, check day 12 has 1 chip left.
11. Check the status reads `Events: 2`.
12. Click Next, check the title is `July 2026` with no chips.
13. Click Previous, check June returns with 2 chips.
14. Click day 5, then Cancel, check day 5 has no chip.
15. Add `Demo` at 14:00 on day 15, check the chip and `Events: 3`.
16. Click Next twice, check the title is `August 2026`.
17. Click Today, check June returns with 3 events.

## Pass conditions

- Every chip, title, meta line, and count above matches.
- Events survive month navigation and the Today jump.
- Cancelling a new event creates nothing.

## Fail conditions

- Any chip, count, or title differs from the expected value.
- An edited time does not show in the details and on the chip.
- A deleted event is still listed.

## Notes

The fixture date is fixed, so the test does not depend on the real
clock. All state lives in the page. The browser run is Playwright
Chromium; the same flow on Firefox or Zen is UNVERIFIED.
