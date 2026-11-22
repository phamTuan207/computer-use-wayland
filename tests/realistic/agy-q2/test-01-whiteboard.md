# test-01-whiteboard.md

## Test ID
test-01-whiteboard

## Topic
Online whiteboard and drawing board: shapes, colors, undo, and save.

## Context
the owner needs to draw an architecture diagram for a system review.
The workstation runs an offline browser whiteboard application (fixtures/test-01-whiteboard.html).
The user must name the board "Architecture Sprint 2026", configure shapes with specific colors,
place an API Gateway box, a Green service circle, an API Gateway label, an accidental Red connector
line that gets undone via Undo, a Yellow database rectangle, and a Database Cluster label.
Finally, the user saves the diagram and verifies the confirmation message.

## Timing
- Baseline start time: 2026-11-21 16:40:00 Asia/Ho_Chi_Minh
- Expected duration: 180 seconds elapsed
- Maximum allowable latency: 300 seconds elapsed

## Goal
Create board "Architecture Sprint 2026", draw 5 objects in exact order:
1. Blue Rectangle at (100, 80) with dimensions 180x120
2. Green Circle at (400, 150) with radius 50
3. Text "API Gateway" at (120, 130)
4. Yellow Rectangle at (400, 300) with dimensions 200x100
5. Text "Database Cluster" at (420, 340)
Handle an accidental Red line between step 3 and 4 by pressing Undo.
Save the board and confirm status banner shows "Board 'Architecture Sprint 2026' saved with 5 objects".

## Exact steps
1. Open fixture tests/realistic/agy-q2/fixtures/test-01-whiteboard.html in the browser.
2. Verify canvas is displayed (800x500 px) and Objects Layer count reads 0.
3. Click the board title input field (id "input-board-title").
4. Type "Architecture Sprint 2026" into the title input.
5. Click the Rectangle tool button (id "tool-rect").
6. Click the Blue color swatch (id "color-blue").
7. In the placement inputs, set X to 100 (id "input-coord-x") and Y to 80 (id "input-coord-y").
8. Set W to 180 (id "input-coord-w") and H to 120 (id "input-coord-h").
9. Click the "Place at Coordinates" button (id "btn-add-shape").
10. Inspect the Objects Layer table: confirm 1 object appears with type "rect" and color "Blue".
11. Click the Circle tool button (id "tool-circle").
12. Click the Green color swatch (id "color-green").
13. Set X to 400 (id "input-coord-x"), Y to 150 (id "input-coord-y"), and W/R to 50 (id "input-coord-w").
14. Click the "Place at Coordinates" button (id "btn-add-shape").
15. Inspect the Objects Layer table: confirm 2 objects appear.
16. Click the Text tool button (id "tool-text").
17. Click the Blue color swatch (id "color-blue").
18. Click the text input box (id "input-canvas-text") and type "API Gateway".
19. Set X to 120 (id "input-coord-x") and Y to 130 (id "input-coord-y").
20. Click "Place at Coordinates" (id "btn-add-shape").
21. Verify Objects Layer shows 3 objects.
22. Simulate human mistake: Click the Line tool (id "tool-line"), click Red swatch (id "color-red"), and click "Place at Coordinates" (id "btn-add-shape").
23. Observe that Objects Layer count increases to 4 with an unintended red line.
24. Click the "Undo" button (id "btn-undo").
25. Verify Objects Layer count returns to 3 and the red line is gone.
26. Click the Rectangle tool button (id "tool-rect").
27. Click the Yellow color swatch (id "color-yellow").
28. Set X to 400, Y to 300, W to 200, H to 100 using coordinate input fields.
29. Click "Place at Coordinates" (id "btn-add-shape").
30. Click the Text tool button (id "tool-text").
31. Click text input box (id "input-canvas-text"), clear it, and type "Database Cluster".
32. Set X to 420 and Y to 340.
33. Click "Place at Coordinates" (id "btn-add-shape").
34. Verify Objects Layer count equals 5.
35. Click the "Save Board" button (id "btn-save-board").
36. Read status banner (id "status-banner") and confirm text contains "Board 'Architecture Sprint 2026' saved with 5 objects".

## Pass/fail criteria
- Pass: Board title is "Architecture Sprint 2026", exactly 5 objects exist in the correct sequence and styles, undo correctly reverted the unintended line, and status banner confirms save.
- Fail: Less than or more than 5 objects, incorrect coordinates or colors, undone line remains, board title missing, or save button not triggered.

## Errors designed to expose
- click miss: Small 24x24 px color swatches can be missed by inaccurate coordinate transforms.
- slow think: Delays during multi-step tool switching and coordinate entry.
- stale observation: Reading object count before the Undo operation finishes repainting the DOM table.
- wrong diagnosis: Mistaking an accidental line for a permanent object rather than using Undo.
- fabrication: Asserting the board is saved without inspecting status-banner text.

## Checker / expected end state
```bash
node tests/realistic/agy-q2/check.mjs --fixture tests/realistic/agy-q2/fixtures/test-01-whiteboard.html --test 01
```
