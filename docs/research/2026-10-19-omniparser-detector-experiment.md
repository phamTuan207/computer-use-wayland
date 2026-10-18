# Local OmniParser detector experiment (2026-10-19)

## Question and scope

Can an external, current interactive-region detector provide tighter clickable targets on the actual Pinta screenshots used in the circle demonstration? This is a **detector-only** experiment. It does not test semantic target selection, OCR, icon captioning, an agent, or successful input. It cannot establish a 95% click success rate or improvement over the current vision model.

We ran Microsoft's official July 2026 YOLOv9-E addition, not the earlier Ultralytics detector. No GUI input was sent and no production dependencies/configuration changed.

## Sources and reproducibility

- [Official repository](https://github.com/microsoft/OmniParser), source commit `354021201345a96178360b28733573e27269f2de`.
- [Official detector implementation](https://github.com/microsoft/OmniParser/blob/354021201345a96178360b28733573e27269f2de/util/yolov9.py).
- [Official weights PR 37](https://huggingface.co/microsoft/OmniParser-v2.0/discussions/37); `icon_detect_v3/model.pt`, revision `refs/pr/37`, 281,182,680 bytes. SHA256 is recorded in the JSON results.
- [Official demo defaults](https://github.com/microsoft/OmniParser/blob/354021201345a96178360b28733573e27269f2de/gradio_demo.py): confidence threshold .05, IoU threshold .1, image size 640. We additionally tested 1280 to check whether small controls benefit from resolution.

Environment: isolated uv Python 3.12.14 environment under `~/.cache/computer-use-research`, torch 2.14.1+cpu, torchvision 0.29.1+cpu, Intel Core 5 210H, six torch CPU threads. About 500 MB downloaded; no CUDA stack or caption model downloaded. GPU speed was not measured.

The executable benchmark and source copies remain in `~/.cache/computer-use-research/`; machine-readable boxes and timing are preserved in [results JSON](2026-10-19-omniparser-detector-results.json). Each case ran four times with one model resident in the same process; warm median is the last three runs. Inputs are private local Pinta screenshots `4ec32b8d528c.png` and `9801b2a8bc4d.png` under the computer-use cache, both 924×1176. They are initial/final views of the same window and strongly correlated.

## Actual results

Hand-labeled reference centers: ellipse (27, 944), hand (27, 253), red swatch (226, 1139). The detector never received target names: we checked its output boxes afterward.

| Input size | Screenshot | Ellipse box contains center | Hand box contains center | Red swatch | First call / warm median |
|---|---|---|---|---|---|
|640|initial|yes,44.6×43.9|yes,49.8×40.6|no box contains center|1.387s /1.203s|
|640|final|yes,51.0×41.2|yes,50.5×42.2|no box contains center|1.201s /1.191s|
|1280|initial|yes,53.2×45.4|yes,49.3×40.0|whole palette row372.2×39.8 only|4.839s /4.734s|
|1280|final|yes,49.5×40.3|yes,49.7×41.0|whole palette row372.6×39.5 only|4.763s /4.815s|

Model loading after imports took 0.544 s. Peak process RSS was 1281 MiB after 640 tests and 2388 MiB after 1280 tests. RSS is cumulative process peak, not exclusive model memory. Whole-process Python import/startup latency was not recorded.

At 1280 the palette-row box technically contains the red center, but its midpoint is around (190, 1149), about 38 px away from red's reference center. **That is not successful red swatch localization** and should not be scored as such. Large boxes also span several toolbar controls at low confidence; the smallest containing box is used in the table.

## Decision

This provides an actual working alternative for proposing button boxes and centers. It finds useful ellipse/hand regions in this example, but does not identify what those icons mean. It misses individual color swatches, adds about 1.2 s per screenshot on CPU at the default resolution, and increasing resolution quadruples latency without fixing the swatch. Installing it as the mandatory path is not justified by these results.

A sensible optional use is proposing local boxes when semantic targeting is unavailable and the model has difficulty localizing an icon. Browser DOM/accessibility identifiers remain a separate way to avoid estimating a pixel target. To establish a reliability improvement, run a larger labeled set covering multiple apps, DPI/scaling, theme/layout changes and ambiguous controls, measure end-to-end correct target selection and click outcomes, and include current model baseline with the same screenshots.
