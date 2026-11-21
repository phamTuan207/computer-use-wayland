# Test 04, kanban drag and drop with persistence

## Goal

Prove that an agent can reorganize a kanban board in a real
browser and that the board state is exactly right after every
move: drag cards between the todo, doing and done columns, add a
card through the form, reload the page and confirm the moved
state persisted from localStorage, then reset and confirm the
initial board is restored and storage is cleared. The board state
is read exactly from the hidden pre element board-state-json in
the DOM, not inferred from pixels.

Fixture: fixtures/test04_kanban_drag_drop.html, fully offline,
HTML5 draggable cards, state persisted to localStorage under the
key kanban-board-v1 on every change, a live counter per column
header, an add card form, and a reset button.

Initial board: todo has card-1 Write report, card-2 Fix login
bug, card-3 Review pull request. Doing has card-4 Build
prototype, card-5 Test checkout flow. Done has card-6 Set up
repository.

## Steps

1. Start the browser through the shared harness.
2. Load the fixture page.
3. Read the initial state JSON from board-state-json.
4. Verify the initial DOM card counts per column, 3, 2, 1.
5. Verify the initial column counters in the headers, 3, 2, 1.
6. Drag card-2 from todo to doing.
7. Verify the state JSON after the first drag.
8. Verify the column counters after the first drag, 2, 3, 1.
9. Drag card-4 from doing to done.
10. Verify the state JSON after the second drag.
11. Drag card-6 back from done to todo.
12. Verify the state JSON after the drag back.
13. Verify the column counters after the drag back, 3, 2, 1.
14. Add a new card titled New test card through the form.
15. Verify the new card is in todo in the state JSON with id
    card-7 and present in the DOM.
16. Reload the page.
17. Verify the state after reload equals the state before reload,
    and the counters read 4, 2, 1.
18. Click the reset button.
19. Verify the initial state is restored exactly.
20. Verify localStorage for the board key is cleared and the
    counters are back to 3, 2, 1.

## Expected results

- After step 6: todo is card-1, card-3 and doing is card-4,
  card-5, card-2.
- After step 9: doing is card-5, card-2 and done is card-6,
  card-4.
- After step 11: done is card-4 only and todo is card-1, card-3,
  card-6.
- After step 14: todo ends with card-7, New test card, and the
  todo counter reads 4.
- After step 17: the full state is unchanged by the reload,
  proving localStorage persistence.
- After step 19: the state equals the initial board exactly and
  the storage key is absent.

## Drag mechanism note

Every drag is attempted first with Selenium ActionChains
drag_and_drop. In the verification runs on headless Firefox that
attempt did not move any card, all 3 ActionChains drags left the
state unchanged, which matches the known weakness of synthetic
mouse input with HTML5 drag and drop. The cards were actually
moved by the fixture fallback helper, window.__kanbanSimulateDrag,
which dispatches the real dragstart, dragover, drop and dragend
event sequence with a dataTransfer shim through the board's own
handlers, so the move, the counters, the state JSON and the
localStorage write all went through the fixture's production code
paths. The test records the mechanism per drag and prints a
DRAG_MECHANISM line, and the mechanism check only passes when all
3 drags are accounted for.

One implementation note: the state pre element is display none,
so Selenium element.text returns an empty string for it. The test
reads its textContent through execute_script, which is the exact
DOM state.

## Timing

Measured on the clone2 machine, headless Firefox 160.0.1,
geckodriver via the shared harness, 2026-11-21.

Verification run 1: wall clock 2026-11-21T11:27:17Z to
2026-11-21T11:27:46Z, total elapsed 29.1275 s, 20 steps, 17
checks, all checks ok, RESULT ok true. The browser start step
alone took 12.9866 s of that total, a cold start.

Verification run 2: wall clock 2026-11-21T11:27:53Z to
2026-11-21T11:28:09Z, total elapsed 15.7999 s, 20 steps, 17
checks, all checks ok, RESULT ok true, same drag mechanism
result as run 1.

Per step elapsed in run 1, seconds: load page 1.5286, read
initial state 0.1794, first drag including the failed ActionChains
attempt and the fallback 1.626, second drag 2.1072, drag back
2.8189, add card 0.9838, reload 0.278, reset click 0.4665, all
state verification steps between 0.0045 and 0.57.
