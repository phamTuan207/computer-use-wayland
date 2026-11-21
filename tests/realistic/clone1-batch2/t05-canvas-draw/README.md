# t05-canvas-draw: draw, erase, undo, save

## Context

A drawing app on a canvas: colour swatches, brush sizes, pen and eraser,
background fill, undo, redo, clear, and save to PNG with a preview and a
download link. Every claim is checked against real pixels.

## Goal

Draw lines, prove the pixels are the right colour, undo and redo, erase
part of a line, fill the background, save a PNG, clear, and prove a thick
brush covers more pixels.

## Steps (36)

1. Open the fixture.
2. Check the canvas starts blank white.
3. Pick the red pen.
4. Pick brush size 8.
5. Draw a red line.
6. Check the pixel on the line is red.
7. Check the stroke count is 1.
8. Pick the blue pen.
9. Draw a blue line.
10. Check the pixel on the line is blue.
11. Check the stroke count is 2.
12. Press undo.
13. Check the count is 1 after undo.
14. Check the blue line is gone after undo.
15. Press redo.
16. Check the count is 2 after redo.
17. Check the blue line is back after redo.
18. Pick the eraser.
19. Erase the middle of the red line.
20. Check the erased pixel is white.
21. Check an untouched red pixel stays red.
22. Pick green for fill.
23. Fill the background green.
24. Check a corner pixel is green after fill.
25. Save the PNG.
26. Check the preview image shows.
27. Check the preview is a PNG data URL longer than 1000 chars.
28. Check the download link points at the PNG.
29. Clear the canvas.
30. Check the count is 0 after clear.
31. Check the canvas is white after clear.
32. Pick the black pen.
33. Pick brush size 20.
34. Draw a thick black line.
35. Check a pixel 8 px off the line centre is black.
36. Check the final stroke count is 1.

## Pass

All 36 steps run, every pixel check matches, undo and redo restore the
strokes, the PNG preview is a real data URL, and the thick brush covers
8 px off centre.

## Fail

Any step above fails, a pixel is the wrong colour, undo or redo does
not restore the drawing, or the PNG is missing.
