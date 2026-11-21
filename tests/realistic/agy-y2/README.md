# Realistic Test Suite agy-y2 (Antigravity Worker Y2)

This test suite provides 10 realistic, multi-step browser application workflows
designed specifically to benchmark computer-use agents (such as Muse, Claude, or agy)
under realistic human-like UI constraints.

## Hard Rules Enforced
1. Complexity and Step Count: Each test contains between 23 and 35 concrete,
   reproducible steps (strictly within the 15-40 steps requirement). Short or trivial tasks
   are excluded because they fail to exercise agent perception, latency, error recovery,
   or observation drift.
2. Distinct Topics: Zero overlap with prior suites (agy-q, fcc-k, fcc-k2, clone1, clone2, agy-q2).
3. Offline Fixtures: All fixtures are local, standalone HTML documents with pure
   JavaScript and CSS. No network access, external CDNs, or external images required.
4. Error Sensitivity: Specifically targets click misses (sub-pixel pointer accuracy
   vs vision grounding errors), slow thinking latency, stale observation drift (over
   120s observation window expiry), misdiagnoses, and hallucinated/fabricated values.
5. DOM Verification Without Fixture Hooks: Fixtures contain no self-check or verification
   functions (window.__verify is strictly forbidden). Verification is performed externally
   by check.mjs reading raw DOM elements against hard-coded expectations.
6. Negative Verification: simulate.mjs confirms that assertions fail on fresh untouched fixtures
   and pass after step simulation.
7. Zero Em/En Dashes: Only standard hyphens, commas, or periods are permitted.

## Test Directory (10 Tests)
- `test-01-tmux-session.md` (35 steps): tmux terminal multiplexer (session create, split panes, rename window, fake command, kill pane mistake recovery, detach and reattach, session list verify)
- `test-02-network-settings.md` (35 steps): System network and device settings (Wi-Fi on, connect HomeFiber-5G, forget CafeFree, pair MX Master 3S, Bluetooth toggle persistence, metered Wi-Fi, status panel verify)
- `test-03-photo-editor.md` (33 steps): Photo editor crop and filter (load sunset.jpg, 4:3 crop, Vivid filter, +20 brightness mistake undo, 90 deg rotation, PNG export dialog and banner verify)
- `test-04-email-compose.md` (33 steps): Email compose with attachment (recipient, CC, Q4 report subject, report.pdf attachment picker, save draft, reopen draft, remove attachment mistake recovery, send, Sent counter verify)
- `test-05-spreadsheet-chart.md` (35 steps): Spreadsheet formulas with chart (enter monthly sales, SUM formula, AVERAGE formula, 9800 to 1800 mistake fix, bar chart insert, chart title edit, total/average DOM verify)
- `test-06-video-call.md` (35 steps): Video-call UI (join Sprint Planning, mute/unmute mic, camera off/on, screen share, raise hand, chat message, leave and rejoin, participant list verify)
- `test-07-file-manager.md` (35 steps): File manager bulk rename and move (select 5 files, rename photo-2026-##, move 3 to Archive, delete and restore from Trash, create folder Processed, inventory verify)
- `test-08-devtools.md` (35 steps): Browser devtools console and network (open panel, run console command, filter api requests, inspect 404 request, clear console, log and network table verify)
- `test-09-notes-sync.md` (35 steps): Notes app with sync conflict (create Shopping note, Device A and B conflicting edits, sync conflict, keep both, rename conflict copy, delete archived draft, inventory verify)
- `test-10-ide-debug.md` (32 steps): IDE debugging (open app.js, breakpoint line 12, start debugging, step over twice, watch total, change value, continue to next breakpoint, stop, call stack verify)

## Running the Automated Checker
```bash
# Check single test fixture:
node tests/realistic/agy-y2/check.mjs --fixture tests/realistic/agy-y2/fixtures/test-01-tmux-session.html --test 01

# Check all fixtures:
node tests/realistic/agy-y2/check.mjs --all
```

## Running the Simulator
```bash
# Run simulator for single test:
node tests/realistic/agy-y2/simulate.mjs --test 01

# Run simulator for all 10 tests:
node tests/realistic/agy-y2/simulate.mjs --all
```

## Verifying Zero Em/En Dashes
```bash
python3 tests/realistic/agy-y2/check-dashes.py tests/realistic/agy-y2
```
