# Worker 3 redteam: why do clicks miss? Coordinate calibration, first principles

- Role: Redteam Worker 3, coordinate calibration problem.
- Started: 2026-11-21 03:32:47 Asia/Ho_Chi_Minh. Finished: 2026-11-21 03:49 Asia/Ho_Chi_Minh. Elapsed about 16 minutes.
- Sources read: `~/workspace/cf26-upload/LOI-VA-GIAI-PHAP-TOAN-BO-20261121.md` sections G12, H3, I1-I8; `~/workspace/computer-use-wayland/improvements/muse-coordinate-accuracy-20261120.md`; `~/workspace/computer-use-wayland/scripts/cu.py` (observe, image_point, move, pointer verification); `~/workspace/computer-use-wayland/scripts/cdp.mjs` (DOM snapshot and click-by-ref); `~/workspace/computer-use-wayland/scripts/a11y.py` (AT-SPI extents); `~/workspace/computer-use-wayland/coord/clone1.md`; `~/workspace/computer-use-wayland/improvements/a1-code-exec-dom-design.md`.
- Live measurement: `hyprctl monitors` on the laptop via ssh-laptop.sh at 03:36, 21/11/2026. Monitor eDP-2, 1920x1200 at 2464x902, scale 1, transform 0.
- Web sources: MDN and Bugzilla 1496683 (transformed element click), Playwright locator docs (boundingBox, click steps), Mozilla firefox-devtools-mcp docs (connect-existing), cdp-toolkit commit 4cd3907 (Firefox cannot be attached to), browxai BiDi standards review June 2026, Lift element picker blog (shadow DOM, iframes).
- Rule: no em dashes or en dashes in this file, commas, periods and short hyphens only.

## 0. Bottom line up front

1. The admitted root cause ("screen ratio differs, coordinates skew right, never calibrated") does NOT fit the recorded numbers. The I1 data refutes a 1.55x frame error, and the live monitor scale is 1, so there is no monitor scale factor to mis-handle on this machine.
2. The audited code path (`cu.py`, the path on-laptop agents use) is exact end to end. Screenshot capture, image resize, coordinate mapping, and pointer placement are all linear and verified, with a live 3px pointer check that refuses the click on a miss. If this path were the one missing, the miss would have to be in the model's reading of the image, not in the pipeline math.
3. The misses happened on the VM Muse direct-driving path, whose screenshot and coordinate handling is NOT in this repo and cannot be audited here. The contrast in the files (on-laptop agents fast and accurate, VM Muses miss often, I7) points at a difference between the two drivers, not at the screen.
4. BiDi is the right fix for the browser part, but it is partial, not 100 percent, and not a drop-in. It removes coordinate estimation for web content, but it does not fix non-browser targets, does not fix picking the wrong element, does not always yield a clickable point, and cannot attach to the already-running Zen without a restart or a separate bridge.
5. Do the cheap discriminating experiments FIRST (section 6). A 5-minute known-point grid test separates "systematic mapping offset" from "vision grounding error" definitively. Everything else is guessing until that runs.

## 1. What the files actually record

### 1.1 The incident data (I1, I6, H3, G12)

- I1 (18:58-19:03, 20/11): aiming at View on the Polygon Invocations page, clicks at image x 805 and 825 hit Remove, clicks at 837 and 850 hit Rejudge, x 940 hit nothing. View is left of all of those.
- I2 (19:20-19:24): clicked Discard instead of Continue, opened the delete-working-copy dialog, Cancel took several tries to dismiss.
- I3 (19:28-19:29): mouse stood still, could not click Add to Contest. This is a stall, not a coordinate error. No coordinate was ever issued, or none landed. Do not count it as a miss.
- I4 (19:10-19:11): missed the General info link several times, fell back to the homepage.
- I6 (19:25-19:27): Muse admitted "I read the button position from the image, but the screen ratio differs, so my coordinates skew right. I never calibrated for the user's screen." The owner ordered this recorded as top priority.
- H3: same, listed as the biggest error. Suspected causes given: (1) unknown screen ratio/scale, (2) observation coordinates do not match real screen coordinates, (3) visual grounding measures pixels wrong, (4) observation crop/resize shifts coordinates.
- I8 (19:11-19:12): tests never measured hit rate. A task passes after retries, so misses hide inside retry loops. No first-try hit rate exists anywhere.
- Coordinate-accuracy file (20/11): observation image 1200x757, window 1863x1176, scale 0.644. Cancel clicks on the native dialog at (725, 388) and (668, 388) returned ok:true but the dialog stayed open for several attempts. The owner's bar (19:13): not 100 percent, occasional misses normal, missing every time unacceptable. The bar is speed with a low miss rate.

### 1.2 What was never measured

- The true image-x of View in the I1 screenshot was never measured independently. "Roughly x=770 or further left" in the coordinate-accuracy file is an estimate, not a measurement. Without ground truth, no one can say whether the 805 click was a 35px mapping offset or a misread of adjacent links.
- No click log pairs aimed coordinates with the element actually hit. The only evidence is the chat narrative plus which dialog opened.
- No hit rate, no error vector (mean dx, dy), no distribution. "Skews right" is a qualitative impression from a handful of samples, all on adjacent small links where the dangerous neighbor happens to sit on the right (Remove right of View, Discard right of Continue).

## 2. The full click pipeline, stage by stage, and where error can enter

There are two different drivers in play. They must not be conflated.

- Driver A (auditable, in repo): `scripts/cu.py`, used by on-laptop agents (Codex, Luna) through the broker. Screenshot, mapping, and pointer code all live here.
- Driver B (unauditable, not in repo): the VM Muse's own computer-use tool path that drove the direct session on 20/11 evening. Its screenshot size, resize behavior, and coordinate frame are not visible from this repo. The 1200x757 image with a 1863x1176 window is the only hard fact about it.

### 2.1 Stage 1: screenshot capture (grim)

- `cu.py observe()` calls `grim -s 1 -g <window geometry> -t ppm -`. The code comment states grim `-s 1` uses logical layout pixels. Window bounds come from `hyprctl clients` via `bounds(c)`, monitor box from `hyprctl monitors` via `monitor_box(m)`, which divides physical size by monitor scale.
- Guard: after capture it re-reads the window and monitor and raises if the window moved or the monitor layout, scale, or transform changed during capture.
- Live fact: monitor scale is 1, transform 0. Logical pixels equal physical pixels on this machine. There is no scale conversion that can go wrong here today.
- Deduction about 20/11: the window was 1863 wide. If the monitor scale had been 1.25, the logical monitor width would be 1536 and a 1863-wide window could not fit. So the scale was 1 during the incident too. The "unknown monitor scale" hypothesis is dead for this machine, both then and now.
- Error contribution of this stage in Driver A: zero by construction, assuming grim and Hyprland report honestly. The one real risk is a stale capture (page changed between capture and click). That is handled by the preflight re-observe and `screen_changed` check in `act()` (section 2.5).

### 2.2 Stage 2: image scaling and cropping

- `save_observation()` resizes the captured image to `max_width` with LANCZOS (default 960 in `observe()`, the 20/11 session image was 1200 wide, so that session used max-width 1200 or a different capture path). Aspect is preserved: 1863x1176 (aspect 1.584) becomes 1200x757 (aspect 1.585).
- The recorded `image_size` is the RESIZED size, and `validate_coordinate_metadata()` enforces that the stored image matches the expected resized dimensions. The mapping in stage 3 uses the resized size, so the resize itself is exactly invertible.
- Crop: `observe()` supports `--crop`, and rejects out-of-bounds crops instead of silently capturing a smaller region. A crop changes the region origin, and `image_point` adds the region origin back. Correct if the model knows it is looking at a crop. Dangerous if the model is shown a crop but thinks it is the full window.
- Error contribution: zero in the math, large in the human factors. Downscaling from 1863 to 1200 (0.644) shrinks every button to 64 percent of its screen size. Polygon action links (View, Remove, Rejudge) are small text links a few dozen screen pixels apart. At 1200 wide, two adjacent links sit roughly 30 to 50 image pixels apart. A vision model localizing a small text link to within 15 image pixels is a hard task, and an error of one link width is the normal failure mode. This stage does not introduce a systematic offset, it amplifies random grounding error by shrinking the targets.

### 2.3 Stage 3: visual grounding (the model reads the image)

- The model looks at the downscaled image and estimates the target's pixel coordinates. This is the only stage that involves judgment, and the only stage whose error is unmeasured.
- `compact_result()` hands the agent `image_size`, `region`, `window_bounds`, `monitor_scale`, `scale_x`, `scale_y`, and `scale` (x-ratio alias). So Driver A DOES tell the agent the image size and the image-to-region scale. Whether the agent uses those numbers correctly is not enforced anywhere. Nothing stops the model from estimating coordinates in the wrong frame.
- Candidate failure modes at this stage:
  - (a) Frame confusion: model estimates a position as a fraction of image width, then multiplies by the wrong width (window width 1863 instead of image width 1200, or a nominal 1920). This produces a systematic rightward error proportional to x.
  - (b) Plain misread: model picks the wrong adjacent link (thinks Remove is View). No systematic offset, just a wrong target.
  - (c) Resolution error: model cannot resolve small adjacent links at 1200 wide and guesses between them.
  - (d) Stale image: model aims at a button that moved since the screenshot (layout shift, dialog appearing). The preflight guard catches screen changes before the batch, but not changes between the preflight re-observe and the click, and not hover-induced layout shifts.
- The I1 numbers discriminate (a) from (b)/(c). See section 2.6.

### 2.4 Stage 4: coordinate mapping (image_point)

- `image_point(meta, x, y)` returns `rx + x*rw/iw, ry + y*rh/ih`, where (rx, ry, rw, rh) is the captured region in logical screen pixels and (iw, ih) is the resized image size. It rejects points outside the image. This is exact linear math. Given correct image coordinates, it returns the correct screen coordinates to sub-pixel precision.
- Error contribution: zero, if the input is in image pixel space. The mapping is only as correct as the model's frame assumption. If the model supplies coordinates in any other frame (screen pixels, 0-1000 normalized, a differently-sized rendering), the output is wrong by exactly the frame ratio, and no later stage can detect it, because the values are in range and plausible.

### 2.5 Stage 5: mouse movement and click (native pointer, Hyprland)

- `act()` moves the pointer with the native `pointer` binary using normalized 0..1000000 coordinates over the monitor box: `abs round((gx-mx)/mw*1000000) round((gy-my)/mh*1000000)`. The monitor offset (mx, my) IS subtracted, so the multi-monitor layout (laptop screen at 2464x902 in the virtual layout) is handled. If it were not handled, clicks would be off by 2464px, which was never observed.
- Verification: after every move, it reads `hyprctl cursorpos` and raises `pointer missed target; refusing click` if the cursor is more than 3px from the intended point. So the cursor lands within 3px of the mapped point, or the click does not happen at all.
- Consequence: the OS pointer is EXONERATED as a cause of I1/I2. A click that lands on Remove when View was intended means the mapped point itself was over Remove. The error entered at stage 3 or 4, never at stage 5.
- What stage 5 cannot verify: which UI element receives the event. The code says so explicitly in its diagnostics: "the desktop backend cannot identify the UI element receiving the event". `ok:true` on a click means the pointer moved and the button event was sent, nothing more. This explains the coordinate-accuracy file note that Cancel clicks returned ok:true while the dialog stayed open. Either the point was not over Cancel, or the dialog needed something else, and ok:true cannot distinguish those.
- The one stage-5-adjacent failure that IS real: B9/I21, the Browse button. The pointer was on the button and the click did not register until the mouse hovered off-center long enough for the hover state to darken. That is a hit-testing / event-target quirk (a label over a hidden file input, or a hover-gated control), not a coordinate error. Correct coordinates are necessary but not sufficient. Any fix that only improves coordinates will still fail on Browse-type controls unless it also does hover-first and verifies the effect.

### 2.6 Quantitative check: does the "ratio" story fit I1?

- Scale factor: 1200 / 1863 = 0.644. Inverse: 1863 / 1200 = 1.5525.
- Hypothesis A (frame confusion, model multiplies by window width): true View image-x about 770 implies the model would report about 770 / 0.644 = 1196. Observed reports: 805, 825, 837, 850, 940. The largest observed value is 22 percent below the prediction, the smallest 33 percent below. Hypothesis A does NOT fit.
- Hypothesis B (uniform rightward offset): 805 - 770 = 35 image px (54 screen px). Fits the first click, but "770" is itself an unmeasured estimate, and the later clicks (837, 850, 940) wander further right instead of converging, which is not the behavior of a fixed offset being corrected. A fixed offset, once noticed, gets subtracted. The observed pattern (aim, miss right, aim a bit further right, miss right again) looks like the model re-estimating from a fresh screenshot each time and misreading the same pair of links, not like a constant it failed to correct.
- Hypothesis C (adjacent-link misread at low resolution): View, Remove, Rejudge are adjacent links roughly 30 to 50 image px apart at 1200 wide. Clicks at 805/825 hitting Remove and 837/850 hitting Rejudge are consistent with the model aiming at the link it believed was View while the screenshot actually showed Remove/Rejudge at those pixels. No systematic offset is needed. This fits all five data points with the fewest assumptions.
- Verdict on the admitted root cause: the admission ("ratio differs, skews right, never calibrated") is a plausible-sounding story that the numbers do not support as stated. A 1.55x frame error would have produced clicks near x=1196 and wild misses everywhere, including large buttons. The observed misses are small (tens of pixels) and confined to small adjacent links. The true cause is most likely grounding resolution on small targets, possibly plus a small frame or bias component that cannot be separated from the misread hypothesis without ground truth. This is the single most important correction in this report: DO NOT build the fix on the "screen ratio" story. Build it on measurements.

### 2.7 Why on-laptop agents are accurate and VM Muses miss (I7)

- The files record that agents running directly on the laptop (Codex, Luna via Driver A) are fast and accurate, while VM Muses (Muse, mimeo) miss often.
- Driver A is exact by the audit above, and its pointer is verified to 3px. Driver B is unaudited. The difference between the two populations is therefore most plausibly a difference in the drivers, not in the screen, the network, or the model. Tailscale and SSH were already ruled out by Muse in I6, correctly: they add latency, not a rightward offset.
- This is a hypothesis, not a proof. It cannot be proven from this repo because Driver B's code is not here. But it is the only hypothesis that explains why the same screen, the same buttons, and the same task produce accurate clicks from one driver and misses from the other. The fix must include auditing Driver B's screenshot frame, or routing VM Muse clicks through Driver A.

## 3. Is BiDi really 100 percent accurate? No. Edge cases, one by one.

"BiDi" here means: resolve the element in the DOM, take its geometry from the layout engine, and click it through the browser's own input pipeline (BiDi `input.performActions` or CDP `Input.dispatchMouseEvent`), instead of estimating pixels from a screenshot and moving the OS pointer. The existing `cdp.mjs` already does exactly this for Chromium. The question is whether the same idea on Firefox/Zen via BiDi is exact, and where it breaks.

Short answer: the rect is exact, the click is not automatically exact. Getting the rectangle right removes the grounding error, but choosing a clickable point inside it, and delivering a real user-like click to it, still have failure modes. None of them is a coordinate scaling error. All of them are element-geometry or event-fidelity issues.

### 3.1 What BiDi gets exactly right

- `getBoundingClientRect()` is layout-engine ground truth in CSS pixels, sub-pixel doubles. No screenshot, no downscale, no model estimation. For an ordinary untransformed button in the top document, rect center plus `elementFromPoint` verification is effectively exact.
- The existing `cdp.mjs` click already implements the good pattern: `scrollIntoView` center, recompute rect, compute center, `elementFromPoint` coverage check (refuses with "element covered; observe again" if the top element is not the target or its descendant), then dispatch mouseMoved, mousePressed, mouseReleased at viewport coordinates. No OS pointer, no window-origin math, no DPR conversion. This is the design to copy.
- BiDi `input.performActions` is spec-defined and stable, and Firefox moved to widget-level event dispatch for fidelity (BiDi standards review, June 2026). Firefox is the friendliest engine for BiDi: CDP was removed in Firefox 141, `--remote-debugging-port` now serves a BiDi WebSocket.

### 3.2 Iframes: naive rect code FAILS

- A rect inside an iframe is relative to that frame's viewport, not the top viewport. `cdp.mjs` only queries the top document (`querySelectorAll` on `document`) and merely counts iframes. It cannot see or click elements inside any iframe.
- Fix: resolve the iframe element's own rect in the top document, recurse into the frame's browsing context, and add offsets at each level. Playwright does this internally (its `boundingBox` is relative to the main frame even for child-frame elements). A hand-rolled BiDi script must do the same, per frame level, including nested frames. Cross-origin iframes cannot be scripted at all from the parent (same-origin policy), so elements inside a cross-origin frame are unreachable by DOM rects and fall back to vision or to BiDi's browsing-context-scoped script calls, which still need the frame's own context handle.
- Polygon relevance: the upload flow pages are plain pages, no evidence of iframes in the task. Low risk for this task, real risk in general. Must be tested, not assumed.

### 3.3 Shadow DOM: finding the element FAILS, the rect itself is fine

- `querySelectorAll` does not pierce shadow roots, so a button inside a shadow tree is invisible to `cdp.mjs` snapshotting. Once you hold the element reference, `getBoundingClientRect()` works normally.
- Fix: recursive shadow-root traversal in the snapshot script (`elementFromPoint` recursion through `shadowRoot.elementFromPoint`, as element-picker implementations do). BiDi script evaluation can do this, but the snapshot code must be written for it. `cdp.mjs` as it stands does not do it.
- Polygon relevance: low for the current pages, but web components are common in modern UIs. A "100 percent" claim must carry this qualifier.

### 3.4 CSS transforms: rect center can lie OUTSIDE the element

- `getBoundingClientRect()` returns the axis-aligned bounding box of the transformed element. For translate and uniform scale, the center is still on the element. For rotate, skew, or non-uniform transforms, the bounding-box center can fall outside the visible element entirely. Clicking it hits whatever is behind.
- This is not theoretical. Mozilla Bug 1496683 documents that Firefox's own WebDriver ElementClick fails on transformed elements for exactly this reason, and that the fix needs `getBoxQuads()`, a Firefox-only, not-yet-standard API that returns the real transformed quads.
- Fix: prefer a point inside the actual quad (from `getBoxQuads` where available), or verify with `elementFromPoint` and fall back to sampling candidate points inside the rect until `elementFromPoint` returns the target. `cdp.mjs` already does the `elementFromPoint` check and refuses on cover, which converts a wrong click into a refusal, but a refusal is still a failed step, and for a rotated element it will refuse forever. Needs the quad-based point choice.
- Polygon relevance: low (admin pages rarely rotate buttons), but the blanket claim "BiDi is 100 percent accurate" is false as stated because of this case.

### 3.5 Scrollable containers, sticky and fixed positioning: mostly handled, one trap

- Rects are viewport-relative and already account for scroll, so scrolling does not invalidate a freshly-read rect. `cdp.mjs` calls `scrollIntoView({block: center})` before reading the rect, which handles offscreen elements and nested scroll containers.
- Trap: after `scrollIntoView`, a sticky header or fixed bar can cover the element. Then `elementFromPoint` returns the header, and `cdp.mjs` correctly refuses. The refusal is safe but the step is stuck unless the code scrolls a little further or clicks a point that avoids the covering bar. Needs a retry that adjusts scroll offset.
- Fixed elements themselves are fine (stable rect across scroll). Sticky elements are fine as targets. The failure is only cover-after-scroll, and it is a refusal, not a wrong click.

### 3.6 Zoom and devicePixelRatio: self-consistent inside BiDi, dangerous across the boundary

- Page zoom changes CSS pixel size, and `window.devicePixelRatio` changes with zoom. `getBoundingClientRect()` returns CSS pixels post-zoom, and `input.performActions` consumes viewport CSS pixels, so inside the BiDi path zoom cancels out. No conversion needed, no error.
- The danger is only when crossing from CSS pixels to OS screen pixels (desktop pointer path) or to screenshot pixels (grim captures physical pixels). Then you must multiply by DPR and add the window origin and browser chrome offset. Every one of those terms is a chance to be wrong. This is a strong argument for BiDi: it deletes three conversion steps by staying inside the browser.
- Requirement: record `window.devicePixelRatio` and page zoom state with every DOM snapshot anyway, so that any future code that does cross the boundary can do it correctly, and so that a zoom change is detectable as a snapshot invalidation.

### 3.7 Inline elements split across lines: rect center can be in a gap

- For an inline element that wraps across two lines (a long link), `getBoundingClientRect()` returns the union box, whose center can fall in the gap between lines, on a different element. `getClientRects()` returns one box per line fragment. Fix: use `getClientRects()` and pick the center of the largest fragment, then `elementFromPoint`-verify. `cdp.mjs` does not do this today.
- Polygon relevance: moderate. Action links are short and single-line, but statement text links and table cells can wrap.

### 3.8 Element identification is still the model's job, and it can still be wrong

- BiDi moves the error, it does not delete it. With vision, the model must estimate pixels (hard). With BiDi, the model must pick the right ref from a text snapshot (easier, but not infallible). Picking the "Remove" ref when "View" was intended produces exactly the I1 outcome, with perfect coordinates. The snapshot labels (role, name) distinguish View from Remove, which is why BiDi should sharply reduce this class of error, but a wrong ref is still possible, especially with duplicate names, truncated labels, or dynamic lists. The snapshot must therefore include enough disambiguation (rect, nearby text, index) and the click must be verified after the fact (did the expected page or dialog appear?).
- Also: the element can move between rect read and click (animation, layout shift, lazy load). Playwright handles this with actionability waits and stability checks. Raw BiDi does not. The design must re-read the rect immediately before the click and refuse if it moved, or wait for stability.

### 3.9 Synthetic click vs real user click: event fidelity

- Two ways to "click" in BiDi: (a) dispatch real input events at coordinates (`input.performActions`, or CDP `Input.dispatchMouseEvent` as `cdp.mjs` does), which produces mousemove, mousedown, mouseup, and click with hover behavior, or (b) call `el.click()` in script, which dispatches only a click event, with no hover, no mousedown/mouseup, and `isTrusted` false.
- (a) is faithful and is what should be used. (b) is tempting because it needs no coordinates at all, but it bypasses exactly the behaviors that real pages depend on: hover-gated controls (the Browse button lesson, B9), mousedown handlers, and any code that checks `isTrusted` or coordinates. A page that opens a file picker on a label click may still work with (b), or may not, depending on user-activation rules. Do not use (b) as the default. Use (a), with (b) only as a diagnosed fallback for a specific control.
- Consequence for the Browse button: BiDi coordinate click with a preceding mouse move reproduces the hover, so it should succeed where a bare center click failed. But that is a prediction, not a measurement. Experiment E6 tests it.

### 3.10 The attach problem: BiDi cannot reach the running Zen today

- This is the largest practical obstacle, and it has nothing to do with coordinate accuracy.
- Firefox and Zen only serve BiDi if launched with `--remote-debugging-port` (and for the Mozilla MCP, also `--marionette`). If Zen is already running on the user's profile without those flags, re-running the binary with flags only opens a new window in the existing instance and the flags are ignored. Mozilla's own firefox-devtools-mcp docs state this explicitly, and cdp-toolkit verified against Firefox 153.0.3 that there is no way to add a debug port to an already-running Firefox.
- `coord/clone1.md` claims Bug 1943416 (RESOLVED FIXED) proves an attach-to-running-session pattern. That claim is unverified on Zen and conflicts with the two sources above. It must be tested on the laptop's actual Zen before any plan depends on it. There is also a Nightly-only dynamic-start path (`remote.experimental.dynamicstart.enabled`), which is experimental and not a basis for a production workflow.
- Practical options, each with a cost:
  - Restart Zen with `--remote-debugging-port=9222` (and `--marionette` if the MCP path is used). Cost: interrupts the user's session, all tabs reload state, and the logged-in Polygon session must survive the restart (it should, cookies persist, but it must be verified). Also sets `navigator.webdriver = true`, which can trip bot detection on protected sites.
  - Run a second Zen/Firefox instance on a dedicated profile with the debug port. Cost: that profile has no login session, so Polygon must be logged in again there, which defeats the "use the already logged-in tab" rule that the 20/11 task depended on (B10).
  - WebExtension plus native-messaging bridge (clone1's prototype). This is the only path in the research that reaches already-open tabs without a restart or a new profile. Cost: needs a custom extension installed in the user's Zen, a native host manifest, and a relay. Unverified on a real Zen.
- Verdict on this point: BiDi is not a drop-in fix for the Polygon workflow as actually run. The coordinate math is ready, the connection to the live browser is not. Any plan that says "switch to BiDi" without solving attach is incomplete.

## 4. Non-browser apps: BiDi fixes nothing there

### 4.1 What is out of BiDi scope

- The native file picker (GTK portal window, separate process), native dialogs (the delete-confirm dialog in I1/I2), the terminal, VS Code, Zen's own chrome (address bar, tabs, menus), and the desktop itself. All of these are invisible to BiDi. The coordinate problem persists there in full.
- The 20/11 task touched all of these: the file picker (B9, 70 minutes stuck), the native confirm dialog (I1/I2 Cancel struggle), and Zen chrome navigation. A BiDi-only fix would have left the longest stuck step (the picker) completely untouched.

### 4.2 The native equivalent: AT-SPI (a11y.py)

- `scripts/a11y.py` already implements the native analogue of DOM rects: `get_extents(Atspi.CoordType.SCREEN)` returns the element's exact screen box, and `a11y act()` invokes the element's native click action directly, with no pointer movement and no coordinates at all. That is the same structural win as BiDi, for native apps.
- Coverage limits, stated honestly:
  - Many elements expose no extents (custom-drawn UI, canvas, VS Code editor surface, some picker list items). `a11y.py` falls back to vision when extents are None, which is correct but means the accuracy win is partial.
  - The extents path is gated behind `CU_PICK4_FASTPATH=1` and is marked experimental. `ground()` warns about screen-vs-window-relative ambiguity and returns root extents so the caller can disambiguate. That ambiguity is unresolved in the current code.
  - AT-SPI tree traversal is slow on large trees, and the snapshot expires after 90 seconds, same as DOM snapshots.
  - The file picker is a separate portal process with its own PID. AT-SPI can see it, but the driver must observe the right app by PID, and focus must be on the picker window before typing (the Browse lesson file already notes this: keys go to the focused window, Ctrl+L inside a picker hits the browser URL bar).
- What is still needed for non-browser targets: enable and harden the AT-SPI path (extents-first, vision fallback), add a native-dialog handler (confirm dialogs are small, high-risk, and AT-SPI-visible), and keep the desktop pointer path as the fallback, with hover-first and verify-after-click (section 5).

### 4.3 Hyprland IPC gives the frame, not the button

- `hyprctl clients` gives exact window position and size, `hyprctl monitors` gives exact monitor geometry and scale. The code already uses both. There is nothing to fix there, and no button position can ever come from Hyprland. Anyone proposing "use Hyprland IPC to get exact coordinates" is confusing the window frame with the contents. Hyprland answers "where is the window", never "where is the button inside it".

## 5. Cheaper fixes than full BiDi

Ordered by cost, cheapest first. None of these requires a browser restart, a new protocol, or a custom extension.

### 5.1 Calibrate once per screen (diagnostic, nearly free)

- Run a known-point grid test (experiment E2). If it measures a systematic offset, fit a 2-point affine correction and apply it in `image_point`. If it measures no offset, the hypothesis is dead and the team stops chasing calibration.
- Cost: one script, one page, 20 clicks, 5 minutes. Value: discriminates the root cause definitively. This should have been done on 20/11 before any fix was designed.
- Limitation: calibration only fixes systematic affine error (offset, scale, rotation). It does nothing for random grounding error, which is the leading hypothesis for I1. A zero result is still valuable because it kills the calibration story.

### 5.2 Crop-zoom before clicking small targets (cheap, high value for I1/I2)

- `observe()` already supports `--crop`. Before clicking a small target, re-observe cropped around the target region at full resolution (no downscale to 960/1200). The model then reads the links at 2x to 3x effective size, and adjacent links separate clearly.
- Cost: one extra observe call per small target, a few lines of driver logic. This directly attacks the observed failure shape (small adjacent links) without any new protocol.

### 5.3 Grid or ruler overlay on the observation image (cheap, proven practice)

- Draw a numbered coordinate grid over the screenshot before showing it to the model. Vision grounding with an explicit ruler is substantially more accurate than free estimation in published computer-use practice. Cost: an image-drawing step in `save_observation` or in the driver. Risk: the overlay can obscure small text, so it must be toggleable and light.

### 5.4 Hover-first, then click, then verify (cheap, prevents destructive misses)

- Generalize the Browse lesson (B9): always move to the target, observe the hover state, and only click if the hover highlights the INTENDED element. If hover darkens Remove when View was intended, abort before the destructive click. After the click, re-observe and confirm the expected effect (page changed, dialog opened, picker appeared). This converts a wrong click from "deleted something" into "refused in time".
- Cost: one extra observe per risky click. Value: prevents the worst outcomes (I1 nearly deleting an invocation, I2 nearly discarding a working copy) even if grounding never improves.

### 5.5 Fix the frame the model is told (free, but unaudited)

- Make sure the agent is told, in the prompt, the exact image pixel dimensions and that coordinates are in image pixels, and make the driver reject coordinates that look like another frame (for example, a value above the image width). Driver A already returns `image_size` and `scale_x`/`scale_y`, but nothing enforces their use.
- Blocker: Driver B (the VM Muse tool path) is not in this repo, so this fix cannot be verified or applied from here. If Driver B is the one missing, this is the fix, and it lives outside this repo.

### 5.6 AT-SPI extents first for native targets (medium, already half-built)

- Enable the `a11y.py` extents path by default for native apps and dialogs, with vision fallback. This is the non-browser version of BiDi and it already exists. Cost: hardening, testing coverage on the picker and dialogs, resolving the screen-vs-window extents ambiguity.

### 5.7 DOM click-by-ref for Chromium today, BiDi for Zen after attach is solved (medium)

- `cdp.mjs` already implements click-by-ref for Chromium. The Polygon task uses Zen, so the remaining work is the Zen connection (section 3.10), not the click math. Do not re-implement clicking. Implement the connection, or the WebExtension bridge, and reuse the `cdp.mjs` pattern (scrollIntoView, rect, elementFromPoint check, dispatched mouse events).

### 5.8 What NOT to do

- Do not "calibrate the screen ratio" as a standalone fix. Monitor scale is 1, the ratio story does not fit the numbers, and a calibration constant fitted to I1's five clicks would be fitting noise.
- Do not add a second vision model or a heavier grounding model before measuring whether grounding is even the bottleneck. Measure first (E2, E4).
- Do not claim BiDi is 100 percent. It is exact for plain buttons and wrong or unreachable for transformed elements, shadow DOM, cross-origin iframes, and everything outside the browser.

## 6. Experiments to find the true root cause

Each experiment names what it measures, the setup, and the pass/fail reading. All are runnable on the laptop with the existing tooling. Log wall-clock time and every aimed vs landed coordinate.

### E1. Pipeline unit audit (no laptop needed, 10 minutes)

- Feed a synthetic observation (known region, known image size) through `image_point` and confirm the mapping inverts the resize exactly, including a crop region and a monitor offset (2464x902).
- Confirm the pointer verification threshold (3px) and the refusal behavior with a mocked cursorpos.
- Pass: mapping error 0px on all cases. Expected result: pass. This closes the "pipeline math is wrong" hypothesis by proof rather than by argument.

### E2. Known-point grid test (the decisive experiment, 5 minutes on the laptop)

- Open a test page (or a fullscreen window) showing a grid of labeled targets at known screen coordinates, for example 20 targets in a 5x4 grid spanning the window, each labeled with its own coordinates.
- The agent clicks each target using screenshots only, exactly as in production (same max-width, same driver). For each click record: aimed image coords, mapped screen coords, actual cursorpos after the move, and which element received the event (a JS mouseover/click listener on the page records the true target, or the hover style shows it).
- Compute: first-try hit rate, mean error vector (dx, dy), standard deviation, and error as a function of x (does error grow with x? that is the signature of a scale error) and of target size.
- Readings:
  - Mean error near 0, random scatter, hits mostly on target: the pipeline is fine, the error is grounding noise. Calibration is dead. Fix by crop-zoom, grid overlay, or DOM rects.
  - Mean dx consistently positive (for example +50px) with small scatter: systematic mapping offset. Then find which stage produces it (compare aimed image coords against the true target image coords; if the model aimed right and the cursor landed right of aim, the mapping or pointer is at fault; if the model aimed right of target, grounding is at fault).
  - Error proportional to x: a scale/frame error. Then identify the wrong width in the chain.
- This one experiment answers the question the whole redteam was asked. Run it before building anything.

### E3. Downscale sensitivity (15 minutes, same grid as E2)

- Repeat E2 at max-width 960, 1200, and 1920 (full resolution). Plot hit rate against image width.
- Reading: if hit rate rises sharply with resolution, the cause is target size on screen (grounding resolution), and crop-zoom is the cheap fix. If hit rate is flat across resolutions, resolution is not the cause.

### E4. DOM rect vs vision estimate, head to head (20 minutes, Polygon invocations page)

- On the real Polygon Invocations page (or a local copy of its layout), get View/Remove/Rejudge rects from the DOM (CDP on Chromium, or BiDi/WebExtension on Zen), and separately ask the model to estimate the same buttons from a screenshot.
- The difference between the DOM rect center and the model's estimate IS the grounding error, measured directly, per button. This replaces the "roughly x=770" guess with a number.
- Reading: if the model's estimates are within 10 image px of the DOM centers, grounding is fine and something else caused I1. If they are 30 to 80px off, grounding is confirmed as the cause.

### E5. Scale robustness (10 minutes)

- Set the monitor scale to 1.25, repeat E2. Then restore scale 1.
- Reading: does `image_point` still hold (it should, since monitor_box divides by scale and grim uses logical pixels)? Does the pointer normalization still hold? Does the model cope? This tests whether the pipeline is fragile to a future scale change, even though scale is 1 today. If it breaks, the fix is a scale-aware regression test, not a calibration constant.

### E6. Browse button hover test (10 minutes, Polygon file picker)

- Instrument a file-input label button: log mousemove, mouseover, mousedown, and click events with coordinates.
- Try: (a) center click with no prior hover, (b) off-center click with no prior hover, (c) move to the button, wait for hover state, then click, (d) BiDi coordinate click with preceding mouse move, (e) `el.click()` in script.
- Reading: which sequences open the picker. This separates a coordinate problem from a hover/event problem and tells the team which click method to use for label-over-input controls.

### E7. Native dialog accuracy (10 minutes)

- Open a native confirm dialog with known button positions. Click Cancel by screenshot coordinates, then by AT-SPI extents, then by AT-SPI native click action.
- Reading: whether dialog clicks miss for the same reason as page clicks, and whether the AT-SPI path fixes them. This covers the I1/I2 Cancel struggle, which BiDi cannot touch.

### E8. Hit-rate instrumentation (ongoing, not an experiment)

- Log every production click with: aimed image coords, mapped screen coords, cursorpos after move, expected element, and observed effect (from the after-screenshot). Compute first-try hit rate daily.
- This is the metric I8 says never existed. Without it, no fix can be proven to work. Any BiDi rollout must report its hit rate against the vision baseline on the same tasks, or the claim "BiDi fixed it" is unproven.

## 7. Verdict

- Is DOM/BiDi the right fix? PARTIAL, and the strongest available fix for the browser part. It deletes the largest error source (pixel estimation from a downscaled screenshot) for web content, replaces it with layout-engine ground truth, and removes three fragile conversions (window origin, chrome offset, DPR) by clicking inside the browser. The existing `cdp.mjs` proves the pattern works for Chromium. For the Polygon workflow, which is almost entirely web content, BiDi should cut the I1/I2/I4 class of misses sharply, provided the model picks the right ref and the click is verified after the fact.
- Is it 100 percent? NO. Transformed elements (rect center off-element, Bug 1496683), shadow DOM (invisible to naive snapshots), cross-origin iframes (unreachable), wrapped inline elements (center in a gap), cover-after-scroll (sticky headers), element motion between read and click, and wrong-ref selection all survive a naive BiDi implementation. Each needs a specific handling (getBoxQuads or point sampling, shadow traversal, frame offset math, getClientRects fragments, scroll adjustment, re-read before click, post-click verification). A BiDi rollout that implements none of those will still miss, just on different elements.
- Is it the wrong fix? NO for the browser, YES if it is presented as the whole fix. It fixes nothing outside the browser (file picker, native dialogs, terminal, VS Code, Zen chrome), and it cannot even connect to the running Zen today without solving the attach problem (restart with flags, separate profile with re-login, or the unverified WebExtension bridge). A plan that says "BiDi" and stops there leaves the 70-minute file-picker stall and the dialog misses exactly where they are.
- What else is needed, in order:
  1. Run E2 (and E4) first, before building. Five minutes to know whether the cause is mapping or grounding. If E2 shows no systematic offset, drop the calibration story permanently.
  2. Ship the cheap defenses now: crop-zoom on small targets, hover-first plus verify-after-click on destructive targets, and hit-rate logging (E8). These help on every driver, browser or not, and they prevent the worst outcomes even if grounding never improves.
  3. Audit Driver B (the VM Muse tool path) or route VM Muse clicks through Driver A. The audited path is exact; the missing path is unaudited. Until Driver B's screenshot frame is known, the team is fixing a driver it cannot see.
  4. Build the Zen connection (BiDi with a restarted Zen, or the WebExtension bridge for the live session), then port the `cdp.mjs` click pattern to it, including the elementFromPoint check, getBoxQuads or point sampling for transforms, shadow traversal, frame offsets, and getClientRects fragments.
  5. Harden the AT-SPI path for native targets (picker, dialogs), with vision fallback. That is the non-browser half of the fix.
  6. Measure hit rate before and after on the same tasks. If BiDi does not move first-try hit rate, say so and revisit, do not declare victory from the design alone.
- One-line verdict: BiDi is the right fix for web clicks, a partial fix for the system, and the wrong story if it is justified by "screen ratio calibration", which the numbers refute and the live monitor scale of 1 contradicts.

## 8. Open questions and blockers

- Driver B (VM Muse direct-driving tool path) is not in this repo. Its screenshot size, resize behavior, and coordinate frame could not be audited. If the parent can point to that code, the frame-confusion hypothesis can be tested directly.
- `coord/clone1.md` claims Bug 1943416 proves attach-to-running-session for BiDi. That conflicts with Mozilla's firefox-devtools-mcp docs and cdp-toolkit's verification on Firefox 153.0.3. Needs a live test on the laptop's Zen before any plan depends on it.
- The true image-x of View in the I1 screenshot is unknown. E4 is the experiment that replaces the "roughly x=770" estimate with a measurement.
- AT-SPI extents behavior under monitor scale above 1 is unverified. Moot at scale 1 today, relevant if the scale ever changes (E5).
- The Browse button mechanism (why center click fails, why hover-off-center works) is still unexplained at the event level. E6 tests it.
- No blocker stopped this redteam. All files read, live monitor geometry measured, web sources checked. Elapsed about 16 minutes, no 15-minute stall occurred.
