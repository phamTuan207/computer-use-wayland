# test-04-budget-tracker.md

## Test ID
test-04-budget-tracker

## Topic
Monthly budget and expense tracker: budget limit adjustment, expense logging, category filtering, delete mistake, and running total balance calculation.

## Context
Pham Tuan needs to update monthly team project expenditures and ensure operational costs remain within limits.
The workstation runs an offline browser manager (fixtures/test-04-budget-tracker.html).
There are 4 existing expenses totaling $1475.50 against an initial budget of $2500.00.
The user must increase the budget limit to $3000.00, log two legitimate expenses ("Cloud Server Hosting" for $85.00
and "Weekly Groceries" for $112.50), enter an accidental high-cost item ("Luxury Watch" for $1500.00) that
triggers an "Over Budget" alert, remove the accidental item, verify the balance returns to "Safe" with
$1673.00 spent and $1327.00 remaining, filter the table by "Groceries", reset the filter, and save the report.

## Timing
- Baseline start time: 2026-11-21 16:45:00 Asia/Ho_Chi_Minh
- Expected duration: 160 seconds elapsed
- Maximum allowable latency: 270 seconds elapsed

## Goal
Set monthly budget to $3000.00, add Cloud Server Hosting ($85.00) and Weekly Groceries ($112.50),
delete accidental Luxury Watch ($1500.00), verify 6 expenses totaling $1673.00, and save budget report.

## Exact steps
1. Open fixture tests/realistic/agy-q2/fixtures/test-04-budget-tracker.html in the browser.
2. Confirm 4 initial expenses are displayed, total spent is $1475.50, and budget limit is $2500.00.
3. Click the monthly budget input (id "input-monthly-budget").
4. Clear the value and type "3000".
5. Click the "Set Budget" button (id "btn-set-budget").
6. Verify the Budget Limit stat card (id "stat-budget-limit") displays "$3000.00".
7. Click the expense description input (id "input-expense-desc").
8. Type "Cloud Server Hosting" into description.
9. Click the expense amount input (id "input-expense-amount") and type "85.00".
10. Select "Tech" in category dropdown (id "select-expense-category").
11. Set date to "2026-11-12" (id "input-expense-date").
12. Click "Add Expense" button (id "btn-add-expense").
13. Verify table now displays 5 rows.
14. Type "Weekly Groceries" in description input (id "input-expense-desc").
15. Type "112.50" in amount input (id "input-expense-amount").
16. Select "Groceries" in category dropdown (id "select-expense-category").
17. Set date to "2026-11-15" (id "input-expense-date").
18. Click "Add Expense" button (id "btn-add-expense").
19. Verify table displays 6 rows.
20. Accidental expense: type "Luxury Watch" in description input (id "input-expense-desc").
21. Type "1500.00" in amount input (id "input-expense-amount").
22. Select "Tech" in category dropdown (id "select-expense-category").
23. Set date to "2026-11-16" (id "input-expense-date").
24. Click "Add Expense" button (id "btn-add-expense").
25. Observe the budget status card (id "stat-budget-status"): confirm it turns red and reads "Over Budget".
26. Locate "Luxury Watch" in the table and click its Delete button (id "btn-del-expense-luxury-watch").
27. Confirm the budget status returns to "Safe".
28. Inspect remaining budget card (id "stat-remaining-budget"): confirm it displays "$1327.00".
29. Inspect total spent card (id "stat-total-spent"): confirm it displays "$1673.00".
30. Filter by category: select "Groceries" in filter dropdown (id "filter-expense-category").
31. Verify exactly 2 rows are visible in the table.
32. Reset filter dropdown to "All Categories".
33. Verify all 6 rows are visible.
34. Click the "Save Budget Report" button (id "btn-save-budget").
35. Read status banner (id "budget-status-banner") and confirm it displays "Budget report saved: 6 expenses totaling $1673.00 (Remaining: $1327.00)".

## Pass/fail criteria
- Pass: Budget limit is $3000.00, exactly 6 expenses exist totaling $1673.00, remaining budget is $1327.00, Luxury Watch removed, and status banner confirms save.
- Fail: Luxury Watch remains, wrong expense count or sums, incorrect budget limit, or unconfirmed save status.

## Errors designed to expose
- click miss: Delete buttons on specific table rows are small; clicking the wrong row deletes a valid expense.
- slow think: Delays during repeated numerical entry and date inputs.
- stale observation: Reading remaining balance before recalculation updates the DOM.
- wrong diagnosis: Mistaking an over-budget status for a system calculation error instead of an accidental input.
- fabrication: Asserting save confirmation without checking the status banner.

## Checker / expected end state
```bash
node tests/realistic/agy-q2/check.mjs --fixture tests/realistic/agy-q2/fixtures/test-04-budget-tracker.html --test 04
```
