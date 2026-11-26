# R3-067 prep note (clone2, prep owner, not a scorer)

Advisory for the R3-067 drive (Pinta, 800x600 white canvas, 3 filled shapes).
Researched from Pinta documentation and source on the web, 2026-11-26.
Main source: Pinta master source file Pinta.Tools/Tools/FreeformShapeTool.cs
(read at commit 8e84d43b), plus the Pinta User Guide overview page and the
DeepWiki shape tools page (which cites ShapeTool.cs, EllipseTool.cs,
EllipseEditEngine.cs and BaseEditEngine.cs). The installed Pinta version on
the laptop is UNVERIFIED from here; if it is an older release, recheck
point 2, because the Fill Style dropdown layout is version dependent.

## 1. Freeform Shape tool: drag only, auto-closed path

- The tool builds its path only in OnMouseMove, and only while a mouse
  button is held (IsLeftMousePressed or IsRightMousePressed). With no
  button pressed, mouse move just resets the last point and returns.
- OnMouseDown records no point at all; it only resets state. A click
  without a drag creates no path (path stays null), and OnMouseUp then
  draws nothing. There is no click-to-add-vertex or polygon mode: the
  tool cannot place 3 corner points by clicking.
- Each move event appends one straight LineTo segment to the path, so
  the outline is the polyline of sampled drag positions.
- The path is closed automatically: both the live preview and the final
  commit on mouse up call ClosePath() before rendering, so the last
  point connects straight back to the first point. For the triangle:
  press at vertex 1, drag through vertex 2 and vertex 3, release near
  vertex 1; the closing edge is drawn by the tool, not by the driver.
- On mouse up the shape is committed to the current layer in one go
  (SimpleHistoryItem). Fill uses Cairo FillRule.EvenOdd (see gotchas).
- Colors on a left-button drag: outline = primary color, fill =
  secondary color. Right-button drag swaps them. In Fill Shape only
  mode (see point 2) the code fills AND strokes with the outline color,
  so for a left drag the fill color is effectively the primary color.

## 2. Fill Style: default is Outline Shape, set in the tool bar

- FreeformShapeTool builds its own "Fill Style" drop-down in the tool
  options bar (label "Fill Style:") with 3 items: index 0 "Outline
  Shape", index 1 "Fill Shape", index 2 "Fill and Outline Shape".
  StrokeShape is index % 2 == 0, FillShape is index >= 1.
- Default: SelectedIndex = Settings.GetSetting(FREEFORM_SHAPE_FILL_TYPE,
  0), so on a fresh profile the default is index 0, Outline Shape. The
  choice is saved on exit (OnSaveSettings), so a profile that once used
  Fill Shape keeps it; do not rely on the default, check the drop-down.
- Practical step for R3-067: with the Freeform Shape tool active, set
  Fill Style to "Fill Shape" before drawing each shape (the Rectangle
  and Ellipse tools have their own fill settings through the shared
  shape tool bar; set Fill Shape there too, per the task requirement
  that all 3 shapes are filled).
- With Fill Style = Fill Shape and a left drag, set the primary color
  to the required fill color (red, blue, green per shape).

## 3. Ellipse tool + Shift: perfect circle

- Confirmed twice: the Pinta User Guide (Ellipse: "if you hold the
  Shift key, it will create a circle shape instead of an ellipse") and
  the source-based DeepWiki page (EllipseTool: "Hold Shift while
  drawing to create perfect circles"). Same for Rectangle + Shift =
  square.
- Hold Shift for the whole drag, from before the press until after the
  release; releasing Shift mid-drag drops the constraint.
- The circle is defined by its bounding square. For the R3-067 circle
  region x 300-500, y 200-400 the bounding box is already square
  (200x200), so a Shift drag from (300, 200) to (500, 400) gives the
  exact circle.

## 4. Gotchas for exact canvas coordinates (800x600)

- Canvas vs screen pixels: tool points are canvas (image) coordinates,
  converted by the workspace. At any zoom other than 100 percent,
  screen pixels do not map 1:1 to image pixels. Work at 100 percent
  zoom and trust the status bar cursor position readout, not counted
  screen pixels, when placing drag starts and ends.
- Editable shapes (Rectangle, Ellipse) stay editable until finalized
  (Enter, switching tool, or saving). After a rough drag, the bounding
  box control points can be nudged with the arrow keys for exact
  placement; that is the reliable way to hit an exact region. Finalize
  one shape before starting the next.
- Freeform has no numeric entry and no post-edit: the traced polyline
  is final once the button is released. Drag slowly; move events are
  sampled, so fast drags give sparse points and chords that cut
  corners. Release as close to the start point as possible so the
  auto-closed edge is short and clean.
- Stroke width spills over the path: outlines are stroked centered on
  the path with the current brush width, and even Fill Shape mode
  strokes once in the fill color, so the colored region extends about
  half the brush width outside the traced path. A small brush width
  keeps the region closest to the nominal coordinates.
- Antialiasing: the shape tools apply the tool antialiasing setting
  (Cairo Subpixel when on). Edge pixels are blended, not pure color;
  interiors are exact. Region and color checks should sample interior
  pixels, not boundary pixels.
- EvenOdd fill rule (Freeform): if the dragged path crosses itself,
  the overlap area is left unfilled. Keep the triangle path simple,
  no self-intersections.
- Draw order and overlap: shape 2 (circle, x 300-500) overlaps shape 1
  (rectangle, x 50-350) in x 300-350, y 200-250, and shape 3 starts at
  x 550. Later shapes paint over earlier ones; draw in the task order
  1, 2, 3 so overlaps match the task's intent.

## Research log (full chains)

- Q1 Freeform behavior: searched for the source file, opened the
  DeepWiki shape tools summary (claim: auto-closes path), then read
  FreeformShapeTool.cs itself on GitHub master and verified the claim
  line by line (OnMouseDown no point, OnMouseMove gated on a pressed
  button, ClosePath in preview and in OnMouseUp). Outcome: confirmed,
  with the extra finding that clicks alone draw nothing.
- Q2 Fill Style default: first search surfaced Paint.NET documentation
  (wrong product, rejected). The FreeformShapeTool.cs toolbar code
  itself lists the 3 items and the settings default of 0, which
  settles it from source. Outcome: default Outline Shape, persisted
  per profile.
- Q3 Ellipse + Shift: confirmed in the official Pinta User Guide
  overview and independently in the source-cited DeepWiki page.
  Outcome: confirmed.
- Q4 Gotchas: derived from the same source read (EvenOdd fill rule,
  stroke in Fill mode, antialiasing flag, PointInCanvas and canvas
  coordinate conversion) plus the DeepWiki finalization and control
  point notes (Enter to finalize, arrow key nudging). Outcome: listed
  above; the laptop's Pinta version and its zoom and brush settings at
  drive time are UNVERIFIED from here.
