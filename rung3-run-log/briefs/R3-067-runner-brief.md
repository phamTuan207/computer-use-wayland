# R3-067 runner brief (Codex lane, R3-L3, position 34, Class S)

## Task (from frozen list docs/rung3-list-100-tasks.md, "### R3-067")

Draw 3 basic shapes in Pinta, fill them, save as PNG:

1. Open Pinta, create a new image 800x600, white background.
2. Rectangle, top-left region (x 50-350, y 50-250): Rectangle tool, Fill
   Style = Fill Shape (solid fill), color red, drag from (50, 50) to
   (350, 250).
3. Circle, center region (x 300-500, y 200-400): Ellipse tool, Fill Style =
   Fill Shape, color blue, hold Shift while dragging to keep it a circle,
   drag from (300, 200) to (500, 400).
4. Triangle, bottom-right region: Freeform Shape tool, Fill Style = Fill
   Shape, color green. Press and hold left mouse at vertex 1 (650, 350),
   drag to vertex 2 (750, 550), drag to vertex 3 (550, 550), drag back to
   vertex 1, then release to close the path and fill green. Do NOT click 3
   separate points (Freeform Shape only draws while dragging; 3 clicks make
   no triangle).
5. Save the file as ~/rung3/nd23-hinh-ve.png, keep size 800x600.
6. Reopen the PNG file, verify all 3 shapes, correct positions, correct
   colors.

Known gotchas (from the frozen list correction note, verified from Pinta
source): Fill Style defaults to Outline Shape (outline only = FAIL); set Fill
Shape for all 3 shapes. Freeform Shape draws only while dragging; the path
must be dragged closed back to the first vertex before releasing.

## User-path test fields (owner hard rule 26/11 05:01)

User-path test: enter via search/homepage and click through like a normal
user; no deep links, no direct commands, no internal setters; evidence shows
entry, path, action, and resulting state.

- (a) User entry point for this test: launch the Pinta application on ws2 the
  way a normal user does (app launcher / desktop entry), then create the new
  800x600 image through Pinta's own New Image dialog.
- (b) Forbidden shortcuts for this test: no scripting the PNG (no
  Python/PIL/ImageMagick/CLI image generation), no Pinta internal setters or
  config edits, no editing the PNG bytes after saving. All 3 shapes must be
  drawn with Pinta's Rectangle / Ellipse / Freeform Shape tools via mouse
  drags in the visible UI.
- Evidence must show: entry (Pinta open, new image dialog or blank canvas),
  path (each shape as drawn, tool settings visible where possible), action
  (save), resulting state (reopened PNG showing 3 filled shapes). End-state
  only evidence is returned unread.

## Drive method (desktop GUI task, no browser)

- Launch `codex exec` from /home/james (gpt-6-luna, --sandbox
  danger-full-access, --skip-git-repo-check) with the GUI env exported:
  XDG_RUNTIME_DIR=/run/user/1000, WAYLAND_DISPLAY=wayland-1,
  DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus,
  HYPRLAND_INSTANCE_SIGNATURE = the dir name under /run/user/1000/hypr/
  (re-read per launch, never hardcode). Zen is already running (PID 578117);
  this task does not need it. No holder/probe (no browser drive).
- Work on ws2. One driver at a time. Canvas coordinates are image
  coordinates (800x600); account for Pinta window position/zoom when mapping
  to screen coordinates, and verify each shape's position from screenshots
  before saving.
- Evidence into ~/rung3-chung-cu/R3-067/:
  - Timestamped screenshots: Pinta open with new 800x600 canvas; canvas
    after the 3 shapes are drawn (before save); reopened PNG verification
    view.
  - A copy of ~/rung3/nd23-hinh-ve.png as saved.
  - bao-cao.txt: steps taken, tool + Fill Style + color used per shape,
    drag endpoints used, save path, reopen verification result.
  - start_time.txt / end_time.txt (ISO with +07:00).
  - drive-log.txt with the full chain for every anomaly:
    failure -> reasoning -> attempts -> decision -> fix -> outcome.

## Pre-drive cleanup (coordinator duty, folded in)

- With the pill ON, before starting Pinta: list ws2 windows
  (`hyprctl clients`). There is a foreign untitled Google Docs window on ws2
  (leftover from R3-046 attempt 1). Close ONLY that window if it is
  unambiguously identified (untitled Google Docs title); verify with
  `hyprctl clients` after. If identification is ambiguous, skip the cleanup
  and report it. NEVER close owner windows/tabs, pinned, essentials, or
  anything on ws3. NEVER close the main Zen window.

## Hard rules (restated per standing rules)

- The computer-use pill MUST show (label exactly "Computer use active")
  while any agent controls the machine. Verify visible during the drive and
  gone after; save a grim screenshot of the desktop after release.
- NEVER ydotool. NEVER close or navigate owner tabs, pinned tabs,
  essentials, or anything on ws3. Close only your own Pinta window after use.
- Hyprland 0.57.2: hl.dsp OBJECT FORM ONLY for any dispatch (string-form
  dispatchers fail AND poison hyprctl configerrors, which breaks the overlay
  daemon). Pre-flight: `hyprctl configerrors` must be empty before launch
  (clear with `hyprctl eval "return true"` if needed, record the result).
- NEVER timeout-kill/SIGTERM any session holder; stop via stop file and wait
  for session_ended; on abrupt death wait ~10 min and poll session.new.
- NEVER touch the FCC tmux pane (PID 22399) or the fcc-server on port 8082.
- No personal info anywhere in files or reports. English only.
- Full access (Codex --sandbox danger-full-access). Log wall-clock
  Asia/Ho_Chi_Minh + elapsed. Do NOT score. Do NOT write coordinator state.
  Do NOT commit. Report facts only.
- LOGGING (owner rule 18:20): log EVERY event with the full chain:
  failure -> reasoning -> attempts -> decision -> fix -> outcome.
- Ponytail for any code touched: smallest complete change, reuse before
  writing, stdlib/platform before dependencies, no unrequested abstraction,
  one small test for non-trivial logic, never cut validation/security/error
  handling. Graphify for codebase context (~/workspace/cu-graphify/graphify-out/).

## Coordinator bookkeeping (driver script duties)

- Before launch: confirm Zen PID 578117 alive, no cursor.lock holder, no
  pill process, configerrors empty; confirm ~/rung3/nd23-hinh-ve.png does
  NOT exist yet (clean start); record task_start + runner PID in the laptop
  event log via log-event.sh immediately (the coordinator copies them into
  state at once).
- Launch detached (setsid nohup ... > log 2>&1 < /dev/null & disown). SSH
  dies ~30 s; poll with short SSH calls (ps + tail log).
- On completion: pull evidence to /tmp/r3-067-evidence/ on the VM, sha256
  every file, confirm the runner PID is gone, grim-check the pill is gone,
  log completion via log-event.sh, report facts (PID, start/end wall-clock,
  evidence paths + sha256, pill status, foreign-window cleanup result,
  anything unusual, full chain for any anomaly).
- Hard timeout 30 minutes from launch.
