# R3-083 runner brief (Codex lane, R3-L3, position 42, Class S, Tier C)

## Task (from frozen list docs/rung3-list-100-tasks.md, "### R3-083")

Create a cover image in Pinta: gradient background, large centered text,
export PNG:

1. Open Pinta, create a new image 1200x628, record the size.
2. Draw a gradient background from color #1E88E5 at the top to color
   #43A047 at the bottom with the Gradient tool, record the 2 color codes.
3. With the Text tool, type "Chao mung", font size 72, white color,
   centered in the region x 300 to 900, y 250 to 380, tolerance 50 px,
   record the text position.
4. Save the image as PNG to ~/rung3-chung-cu/R3-083/anh-bia.png.
5. Write ~/rung3-chung-cu/R3-083/ket-qua.txt with: image size, the 2
   background color codes, text content, font size, text color, saved
   file name.

Pass: PNG file exists, size 1200x628, gradient background with the 2
correct colors, text "Chao mung" white size 72 centered in x 300-900,
y 250-380 (tolerance 50 px), ket-qua.txt has all items, screenshot shows
the cover image.
Fail: wrong size, background not a gradient, wrong colors, missing text,
wrong font size, or saved file not PNG.

Tracking pair note (R3-067/R3-083): record in bao-cao.txt exactly which
drawing method was used for the gradient and the text (tools, drag
geometry, any workaround), the same way the R3-067 method was recorded.

## User-path test fields (owner hard rule 26/11 05:01)

User-path test: enter via search/homepage and click through like a normal
user; no deep links, no direct commands, no internal setters; evidence shows
entry, path, action, and resulting state.

- (a) User entry point for this test: open Pinta from the launcher like a
  normal user, create the new image through the New Image dialog, and use
  the visible Gradient and Text tools in the Pinta UI.
- (b) Forbidden shortcuts for this test: do NOT generate the image with
  ImageMagick, Python PIL, ffmpeg, or any CLI/script as the recorded
  source; the image must be drawn in the Pinta UI. Do NOT open or edit
  an existing image (this task creates a new image from scratch). Do NOT
  fake the screenshot.
- Evidence must show: entry (Pinta new image 1200x628), path (gradient
  drawn, text typed), action (PNG saved), resulting state (anh-bia.png +
  ket-qua.txt). End-state only evidence is returned unread.

## Drive method (desktop GUI task, no browser)

- Launch `codex exec` from /home/james (gpt-6-luna, --sandbox
  danger-full-access, --skip-git-repo-check) with the GUI env exported:
  XDG_RUNTIME_DIR=/run/user/1000, WAYLAND_DISPLAY=wayland-1,
  DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus,
  HYPRLAND_INSTANCE_SIGNATURE = the dir name under /run/user/1000/hypr/
  (re-read per launch, never hardcode). Zen is already running (PID
  578117); this task does not need it. No holder/probe (no browser drive).
- Work on ws2. One driver at a time.
- Evidence into ~/rung3-chung-cu/R3-083/:
  - anh-bia.png (1200x628 PNG) (mandatory).
  - ket-qua.txt: image size, 2 background color codes, text content,
    font size, text color, saved file name (mandatory).
  - A timestamped screenshot showing the cover image in Pinta.
  - bao-cao.txt: drawing method used (tools, drag geometry, workarounds),
    text position recorded, any anomaly with full chain.
  - start_time.txt / end_time.txt (ISO with +07:00).
  - drive-log.txt with the full chain for every anomaly:
    failure -> reasoning -> attempts -> decision -> fix -> outcome.

## Hard rules (restated per standing rules)

- The computer-use pill MUST show (label exactly "Computer use active")
  while any agent controls the machine. Verify visible during the drive
  and gone after; save a grim screenshot of the desktop after release.
- NEVER ydotool. NEVER close or navigate owner tabs, pinned tabs,
  essentials, or anything on ws3. Close only your own windows after use.
- Hyprland 0.57.2: hl.dsp OBJECT FORM ONLY for any dispatch (string-form
  dispatchers fail AND poison hyprctl configerrors, which breaks the
  overlay daemon). Pre-flight: `hyprctl configerrors` must be empty
  before launch (clear with `hyprctl eval "return true"` if needed,
  record the result).
- Class S: after scoring, the coordinator removes the evidence outputs
  (reset). Leave them in place until then.
- 30-minute limit per drive. Timing/logging ALWAYS ON: wall-clock
  Asia/Ho_Chi_Minh + elapsed, full chain for every event.
- Ponytail for any code work: smallest complete change, reuse before
  writing, stdlib/platform before dependencies, no unrequested
  abstraction, one small test for non-trivial logic, never cut
  validation/security/error handling.
- NO personal info anywhere in evidence or logs.
- Delivery: evidence stays on the laptop in ~/rung3-chung-cu/R3-083/ plus
  a copy the driver transfers to the VM; the coordinator builds the
  snapshot. Report back with file list + sha256 per file, start/end
  times, runner PID, the drawing method used, and every anomaly chain.
  No score.
