# test-02-recipe-app.md

## Test ID
test-02-recipe-app

## Topic
Recipe catalog application with category filtering, dietary constraints, servings adjustment, meal planning, and shopping list generation.

## Context
the owner needs to assemble a healthy weekly meal plan for three meals adhering to dietary guidelines.
The workstation runs an offline browser application (fixtures/test-02-recipe-app.html).
The catalog contains 12 diverse recipes. The user must filter for a Gluten-Free dinner, inspect
Lemon Herb Salmon, scale its servings from 2 to 4 in the detail modal, add it to the meal planner,
search and add Banana Oat Pancakes and Berry Protein Smoothie, accidentally add Crispy Beef Tacos,
detect and remove the tacos, generate the aggregated shopping list, and save the meal plan as
"Weekly Health Plan".

## Timing
- Baseline start time: 2026-11-21 16:42:00 Asia/Ho_Chi_Minh
- Expected duration: 160 seconds elapsed
- Maximum allowable latency: 280 seconds elapsed

## Goal
Build a meal plan titled "Weekly Health Plan" containing exactly:
1. Lemon Herb Salmon (scaled to 4 servings)
2. Fluffy Banana Oat Pancakes (2 servings)
3. Berry Protein Smoothie (1 serving)
Generate the consolidated shopping list, save the plan, and verify the confirmation banner.

## Exact steps
1. Open fixture tests/realistic/agy-q2/fixtures/test-02-recipe-app.html in the browser.
2. Confirm the recipe catalog displays 12 items and the meal planner count reads 0.
3. Click the Plan Name input field (id "input-plan-name").
4. Type "Weekly Health Plan" into the Plan Name input.
5. Click the Category dropdown (id "filter-category") and select "Dinner" (value "dinner").
6. Verify catalog count drops to 4 recipes.
7. Click the "Gluten-Free" checkbox (id "filter-diet-gf").
8. Verify catalog count narrows down to 2 recipes (Lemon Herb Salmon and Quinoa Vegetable Bowl).
9. Click "View Recipe" button on Lemon Herb Salmon (id "btn-view-salmon").
10. Confirm the recipe modal opens with base servings displaying 2 (id "servings-count").
11. Click the increase servings button (id "btn-inc-servings") once to set servings to 3.
12. Click the increase servings button (id "btn-inc-servings") a second time to set servings to 4.
13. Verify the ingredient list updates to show 4 fillets and 4 tbsp olive oil.
14. Click the modal button "Add to Meal Plan" (id "btn-modal-add-plan").
15. Verify the modal closes and the Meal Planner count reads 1.
16. Reset filters: change Category dropdown (id "filter-category") back to "All Categories" (value "all").
17. Uncheck the "Gluten-Free" checkbox (id "filter-diet-gf").
18. Click the Search input (id "recipe-search") and type "Pancakes".
19. Verify only Fluffy Banana Oat Pancakes is visible in the grid.
20. Click the "Add to Plan" button on the pancakes card (id "btn-plan-pancakes").
21. Clear the search input and type "Smoothie".
22. Click the "Add to Plan" button on Berry Protein Smoothie (id "btn-plan-smoothie").
23. Clear search input and type "Tacos".
24. Mistakenly click "Add to Plan" on Crispy Beef Tacos (id "btn-plan-tacos").
25. Observe the Meal Planner sidebar: count displays 4 items.
26. Locate the Crispy Beef Tacos item in the planner and click its "Remove" button (id "btn-remove-plan-tacos").
27. Confirm the Meal Planner count returns to 3 items.
28. Click the "Generate List" button (id "btn-generate-shopping-list").
29. Confirm the shopping list container (id "shopping-list-output") populates with aggregated items.
30. Click the "Save Meal Plan" button (id "btn-save-plan").
31. Inspect the status banner (id "recipe-status-banner") and verify it displays "Meal plan 'Weekly Health Plan' saved with 3 recipes and shopping list".

## Pass/fail criteria
- Pass: Plan name is "Weekly Health Plan", exactly 3 planned meals exist (Salmon at 4 servings, Pancakes, Smoothie), Tacos correctly removed, shopping list generated with at least 5 items, and save confirmation displayed.
- Fail: Tacos remain in planner, wrong recipe count, unadjusted servings for salmon, empty shopping list, or plan not saved.

## Errors designed to expose
- click miss: Servings increment button is compact; misclicking causes wrong serving multipliers.
- slow think: Delays during multi-criteria filtering (category + diet checkbox + text query).
- stale observation: Reading planner count before the delete action updates the DOM.
- wrong diagnosis: Failing to clear the search filter before looking for the next meal.
- fabrication: Asserting shopping list is compiled without clicking the generate list button.

## Checker / expected end state
```bash
node tests/realistic/agy-q2/check.mjs --fixture tests/realistic/agy-q2/fixtures/test-02-recipe-app.html --test 02
```
