# test-03-habit-tracker.md

## Test ID
test-03-habit-tracker

## Topic
Habit tracker with daily checkboxes, streak computation, category filtering, habit deletion, and weekly adherence statistics.

## Context
the owner needs to log weekly habits for team productivity and health tracking.
The workstation runs an offline browser dashboard (fixtures/test-03-habit-tracker.html).
There are 4 existing habits with initial checkmarks. The user must add a new habit
"Deep Work Sprint" under "Productivity" with a 5-day target, check off Monday through Friday,
accidentally add an unwanted habit "Social Media Browsing", delete the unwanted habit,
complete Saturday and Sunday checks for "Drink 2L Water" to achieve a 7-day streak,
verify the adherence rate updates to 66% (23 total checks), and save the log.

## Timing
- Baseline start time: 2026-11-21 16:44:00 Asia/Ho_Chi_Minh
- Expected duration: 150 seconds elapsed
- Maximum allowable latency: 260 seconds elapsed

## Goal
Add "Deep Work Sprint" (Productivity, Mon-Fri checked), delete accidental habit "Social Media Browsing",
bring "Drink 2L Water" to 7 days, save log for 5 active habits with 23 total checks, and verify confirmation.

## Exact steps
1. Open fixture tests/realistic/agy-q2/fixtures/test-03-habit-tracker.html in the browser.
2. Confirm the active habits count reads 4 and adherence rate reads 57%.
3. Click the habit name input field (id "input-habit-name").
4. Type "Deep Work Sprint" into the habit name input.
5. Click the category dropdown (id "select-habit-category") and choose "Productivity".
6. In target days input (id "input-target-days"), set the value to 5.
7. Click the "Add Habit" button (id "btn-add-habit").
8. Verify the table now displays 5 habit rows.
9. Locate "Deep Work Sprint" and check Mon checkbox (id "check-habit-deep-work-sprint-mon").
10. Check Tue checkbox (id "check-habit-deep-work-sprint-tue").
11. Check Wed checkbox (id "check-habit-deep-work-sprint-wed").
12. Check Thu checkbox (id "check-habit-deep-work-sprint-thu").
13. Check Fri checkbox (id "check-habit-deep-work-sprint-fri").
14. Verify the streak badge for Deep Work Sprint displays "5d".
15. Accidental creation: Type "Social Media Browsing" in input (id "input-habit-name").
16. Select category "Mindset" in dropdown (id "select-habit-category").
17. Click "Add Habit" (id "btn-add-habit").
18. Observe table now has 6 rows.
19. Click the Delete button for Social Media Browsing (id "btn-del-habit-social-media-browsing").
20. Confirm the table returns to 5 rows and Social Media Browsing is gone.
21. Locate "Drink 2L Water" row and check Sat checkbox (id "check-habit-water-sat").
22. Check Sun checkbox for "Drink 2L Water" (id "check-habit-water-sun").
23. Confirm the streak for "Drink 2L Water" updates to "7d".
24. Click the Filter dropdown (id "filter-category") and select "Productivity".
25. Verify only "Deep Work Sprint" is rendered in the filtered view.
26. Reset the Filter dropdown to "All Categories".
27. Verify all 5 habits are visible.
28. Inspect adherence rate metric (id "stat-adherence-rate"): confirm it displays "66%".
29. Click the "Save Tracking Log" button (id "btn-save-habits").
30. Read the status banner (id "habit-status-banner") and confirm text contains "Habit log saved successfully for 5 habits (23 completed checks)".

## Pass/fail criteria
- Pass: 5 habits exist, Deep Work Sprint has Mon-Fri checked, Water has all 7 days checked, Social Media Browsing is deleted, 23 total checks logged, and status banner confirms save.
- Fail: Unintended habit remains, wrong checkmark counts, adherence rate incorrect, or save not triggered.

## Errors designed to expose
- click miss: Checkbox grid has tight spacing (45px columns); vision models often check adjacent days.
- slow think: Latency during sequential 7-day checkbox interactions.
- stale observation: Reading streak value before DOM recomputation completes.
- wrong diagnosis: Mistaking the filtered view for missing habits.
- fabrication: Claiming log saved without verifying status banner text.

## Checker / expected end state
```bash
node tests/realistic/agy-q2/check.mjs --fixture tests/realistic/agy-q2/fixtures/test-03-habit-tracker.html --test 03
```
