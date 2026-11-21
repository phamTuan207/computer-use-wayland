# Test 05, canvas drawing app

## Goal

Prove an agent can operate a real canvas drawing app in a real
browser with mouse action chains, and that the drawing outcome can
be verified from canvas pixels, not from trusting the app state
alone. The app tracks strokes as point lists, supports undo and
redo by replaying strokes, erases with destination-out strokes,
and saves the canvas to a PNG data URL.

Fixture: fixtures/test05_canvas_drawing.html, fully offline,
inline CSS and JS. Canvas 640x440, six color swatches, brush size
slider 1 to 20, eraser toggle, undo, redo, clear, and save.
State is readable at window.drawApp.getState().

## Steps

1. Start the browser and load the fixture.
2. Read the initial state, expect 0 strokes.
3. Sample canvas pixels, expect all blank (alpha 0).
4. Click the red swatch.
5. Verify the state color is red, #e53935.
6. Set the brush size slider to 8 with arrow keys.
7. Verify the state brush size is 8.
8. Draw stroke 1, a horizontal line near y=100, with
   click_and_hold and move_by_offset action chains.
9. Verify the stroke count is 1.
10. Sample pixels along stroke 1, expect mostly red pixels.
11. Click the blue swatch and verify the state color is blue.
12. Draw stroke 2 near y=260 in blue.
13. Verify the stroke count is 2.
14. Sample pixels along stroke 2, expect blue pixels and no red.
15. Click undo, verify the stroke count drops to 1.
16. Click redo, verify the stroke count returns to 2.
17. Turn the eraser on and draw a short stroke across stroke 1.
18. Verify the erased sample point is blank again while a point
    further along stroke 1 is still red, and the erase stroke is
    counted, 3 strokes total.
19. Click save.
20. Verify the download link href starts with data:image/png,
    the preview image is shown and loaded, and the data URL is
    substantially longer than a blank canvas data URL.
21. Click clear.
22. Verify the stroke count is 0 and sampled pixels are blank.

## Expected results

Every step ok, every check ok. Stroke counts follow the sequence
0, 1, 2, 1 after undo, 2 after redo, 3 after the erase stroke, 0
after clear. Pixel checks confirm the visible outcome of each
drawing action: red on stroke 1, blue on stroke 2, a blank gap
where the eraser passed, and a blank canvas after clear.

## Timing

Filled after the verification runs on this machine, headless
Firefox 160.0.1, geckodriver 0.37.1, Selenium venv:

- RESULT ok: true, two consecutive full passes, final run wall
  clock 2026-11-21T11:28:21Z to 2026-11-21T11:28:30Z
- Step count: 26, including browser_start
- Checks: 17 of 17 ok
- Total elapsed: 8.8376 s on the final run, 11.2845 s on the pass
  before it, most of the variance is cold browser start
- Pixel verification in headless Firefox: getImageData sampling
  was exact and stable. Stroke 1 sampled 12 of 12 red pixels,
  [229, 57, 53, 255], stroke 2 sampled 12 of 12 blue pixels,
  [30, 136, 229, 255], with no red. The destination-out eraser
  returned the erased sample point to alpha 0 while a point
  further along the same stroke stayed red. ActionChains offsets
  landed on the intended canvas coordinates at device pixel
  ratio 1, no scaling correction was needed. The saved PNG data
  URL decoded back to 3656 non-blank pixels, against a blank
  canvas data URL length of 2846 characters and a saved length
  of 3478 characters.
