# Realistic Test Suite agy-q2 (Antigravity Worker Q2)

This test suite provides 10 realistic, multi-step browser and desktop application workflows
designed specifically to benchmark computer-use agents (such as Muse, Claude, or agy)
under realistic human-like UI constraints.

## Hard Rules Enforced
1. Complexity and Step Count: Each test contains between 23 and 35 concrete,
   reproducible steps (strictly within the 15-40 steps requirement). Short or trivial tasks
   are excluded because they fail to exercise agent perception, latency, error recovery,
   or observation drift.
2. Distinct Topics: Zero overlap with prior suites (agy-q, fcc-k, fcc-k2, clone1, clone2).
3. Offline Fixtures: All fixtures are local, standalone HTML documents with pure
   JavaScript and CSS. No network access or external CDNs required.
4. Error Sensitivity: Specifically targets click misses (sub-pixel pointer accuracy
   vs vision grounding errors), slow thinking latency, stale observation drift (over
   120s observation window expiry), misdiagnoses, and hallucinated/fabricated values.
5. Automated Checker: Every fixture exposes a `window.__agyVerify()` verification hook
   that evaluates DOM state, internal data models, and action logs.

## Test Directory (10 Tests)
- `test-01-whiteboard.md` (33 steps): Online whiteboard / drawing board (shapes, colors, undo, save)
- `test-02-recipe-app.md` (35 steps): Recipe app with search, dietary filters, servings adjustment, and shopping list
- `test-03-habit-tracker.md` (27 steps): Habit tracker (check off days, streaks, completion rate, delete accidental habit)
- `test-04-budget-tracker.md` (35 steps): Budget tracker (budget limit adjustment, expense logging, over-budget alert, running balance)
- `test-05-contact-book.md` (28 steps): Contact book (add contact via modal, edit phone, favorite star, delete spam, search and filter)
- `test-06-file-converter.md` (26 steps): File converter UI (source and target formats, compression, metadata, error handling, batch download)
- `test-07-weather-dashboard.md` (28 steps): Weather dashboard (stations, 3-day forecast, unit toggle Celsius to Fahrenheit, primary station)
- `test-08-quiz-app.md` (29 steps): Quiz app (question navigation, option selection, mistake correction, review, score calculation, 100% result)
- `test-09-pomodoro-timer.md` (25 steps): Pomodoro timer (settings configuration, focus and break cycles, accidental reset recovery, history log)
- `test-10-markdown-editor.md` (23 steps): Markdown preview editor (dual-pane live preview, headings, bullet list, accidental text deletion, HTML export)

## Running the Automated Checker
```bash
# Check single test fixture:
node tests/realistic/agy-q2/check.mjs --fixture tests/realistic/agy-q2/fixtures/test-01-whiteboard.html --test 01

# Check all 10 fixtures:
node tests/realistic/agy-q2/check.mjs --all
```

## Running the Simulator
```bash
# Run simulator for single test:
node tests/realistic/agy-q2/simulate.mjs --test 01

# Run simulator for all 10 tests:
node tests/realistic/agy-q2/simulate.mjs --all
```

## Verifying Zero Em/En Dashes
```bash
python3 tests/realistic/agy-q2/check-dashes.py tests/realistic/agy-q2
```
