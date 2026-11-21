# test-03-photo-editor.md

## Test ID
test-03-photo-editor

## Topic
Photo editor crop, color filters, accidental brightness undo, 90-degree rotation, and format export.

## Context
A graphic designer needs to prepare a web hero asset from a raw image file.
The workstation runs a local browser-based photo editor (fixtures/test-03-photo-editor.html).
The user must load "sunset.jpg" from the photo library, crop the canvas to a 4:3 aspect ratio,
apply a "Vivid" color filter, increase brightness by +20, identify overexposure and undo the adjustment,
rotate the canvas 90 degrees clockwise, configure the export settings to PNG format, verify the updated dimensions
(750 x 1000 px) in the export dialog, and confirm the export banner.

## Timing
- Baseline start time: 2026-11-21 17:00:00 Asia/Ho_Chi_Minh
- Expected duration: 180 seconds elapsed
- Maximum allowable latency: 300 seconds elapsed

## Goal
Load "sunset.jpg", crop to 4:3 (1000x750), apply Vivid filter, add +20 brightness, undo brightness to 0,
rotate 90 degrees clockwise (750x1000), export as PNG, and verify export confirmation banner.

## Exact steps
1. Open fixture tests/realistic/agy-y2/fixtures/test-03-photo-editor.html in the browser.
2. Verify element #editor-status-text text is "Ready. No file loaded.".
3. Click list item #file-item-sunset to select "sunset.jpg" from the library.
4. Click button #btn-load-photo to load the photo into the editor canvas.
5. Verify element #current-filename text is "sunset.jpg".
6. Verify element #dim-width text is "1200" and #dim-height text is "900".
7. Click button #tool-tab-crop to switch to the crop controls tab.
8. Verify element #crop-controls has class "active".
9. Click button #btn-ratio-4-3 to choose 4:3 aspect ratio.
10. Verify element #active-crop-ratio text is "4:3".
11. Click button #btn-apply-crop to commit the crop modification.
12. Verify element #dim-width text is "1000" and #dim-height text is "750".
13. Click button #tool-tab-filters to switch to the filters panel.
14. Verify element #filters-panel has class "active".
15. Click button #btn-filter-vivid to select the Vivid filter preset.
16. Verify element #active-filter-name text is "Vivid".
17. Click button #tool-tab-adjust to open color adjustment controls.
18. Verify element #brightness-display text is "0".
19. Click button #btn-brightness-plus to raise brightness by 20.
20. Verify element #brightness-display text is "20".
21. Simulate mistake: identify brightness overexposure and click button #btn-undo-adjust.
22. Verify element #brightness-display text returns to "0".
23. Click button #tool-tab-transform to open transformation options.
24. Click button #btn-rotate-90-cw to rotate the canvas 90 degrees clockwise.
25. Verify element #rotation-angle text is "90 deg".
26. Verify element #dim-width text is "750" and #dim-height text is "1000".
27. Click button #btn-open-export to open the export options modal.
28. Verify modal #export-modal has class "active".
29. Select dropdown option "PNG" in select #select-export-format.
30. Verify element #dialog-format-display text is "PNG".
31. Verify element #dialog-dimensions-display text is "750 x 1000 px".
32. Click button #btn-confirm-export to finalize export.
33. Verify element #export-status-banner text contains "Image exported: sunset.png (750x1000, PNG)".

## Pass/fail criteria
- Pass: "sunset.jpg" loaded, cropped to 4:3 (1000x750), Vivid filter active, brightness reverted to 0, rotated 90 deg clockwise to 750x1000, exported as PNG, and export banner confirmed.
- Fail: File not loaded, wrong crop ratio, Vivid filter inactive, brightness not restored to 0, rotation angle not 90 deg, format not PNG, or export banner missing.

## Errors designed to expose
- click miss: Switching between compact sidebar tool tabs and clicking small ratio buttons.
- slow think: Delays during multi-stage image editing and dialog configuration.
- stale observation: Reading dimension counters before rotation transformation updates the DOM.
- wrong diagnosis: Failing to undo the brightness adjustment before initiating rotation.
- fabrication: Assuming default JPEG format in export modal without selecting PNG.

## Checker / expected end state
```bash
node tests/realistic/agy-y2/check.mjs --fixture tests/realistic/agy-y2/fixtures/test-03-photo-editor.html --test 03
```
