# R3-085 runner brief (Codex lane, R3-L3, position 43, Class S, Tier C)

## Task (from frozen list docs/rung3-list-100-tasks.md, "### R3-085")

Open a video with mpv, pause at second 10, screenshot, compare with the
reference frame:

1. Open a terminal, run `mpv --start=00:10 --pause ~/rung3/nd26-video.mp4`,
   wait for the mpv window to appear.
2. Check the mpv timeline shows 00:10 and the video is paused; record the
   shown time.
3. Screenshot the mpv window paused at 00:10, save to
   ~/rung3-chung-cu/R3-085/anh-mpv-00-10.png.
4. Open the reference frame ~/rung3/r3-085-khung-tham-chieu.png (extracted
   beforehand with ffmpeg), record 2 identifiable details in the reference
   frame (for example object, color, text).
5. Write ~/rung3-chung-cu/R3-085/ket-qua.txt with: pause time, screenshot
   file name, 2 identifiable details, conclusion whether the screenshot
   matches the reference frame or not.

Pass: screenshot shows the mpv window paused at 00:10, screenshot matches
the reference frame by the 2 details recorded in the result file, the 2
identifiable details are a mandatory criterion, mean-color deviation of the
center region is only a guide (under 10 percent accepted), no per-pixel
match required, result file has all items.
Fail: video not paused at 00:10, screenshot does not show the mpv window,
screenshot does not match the reference frame, missing identifiable
details, or a different video player used without stating it clearly.

## User-path test fields (owner hard rule 26/11 05:01)

User-path test: enter via search/homepage and click through like a normal
user; no deep links, no direct commands, no internal setters; evidence shows
entry, path, action, and resulting state.

- (a) User entry point for this test: open the terminal like a normal user
  and run the mpv command exactly as the task steps say (the task itself
  defines this command as the entry point), then use the visible mpv
  window and timeline.
- (b) Forbidden shortcuts for this test: do NOT extract the frame with
  ffmpeg, ffprobe, or any script as the recorded screenshot; the
  screenshot must show the actual mpv window paused at 00:10. Do NOT use
  a different video player. Do NOT fake the screenshot or the timeline.
- Evidence must show: entry (mpv window open), path (timeline at 00:10,
  paused), action (screenshot taken), resulting state (anh-mpv-00-10.png +
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
- Evidence into ~/rung3-chung-cu/R3-085/:
  - anh-mpv-00-10.png (screenshot of the mpv window paused at 00:10)
    (mandatory).
  - ket-qua.txt: pause time, screenshot file name, 2 identifiable details,
    match conclusion (mandatory).
  - A COPY of the reference frame ~/rung3/r3-085-khung-tham-chieu.png
    (read-only source; copy, do not modify) so the scorers can compare.
  - bao-cao.txt: steps, shown timeline time, any anomaly with full chain.
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
- Delivery: evidence stays on the laptop in ~/rung3-chung-cu/R3-085/ plus
  a copy the driver transfers to the VM; the coordinator builds the
  snapshot. Report back with file list + sha256 per file, start/end
  times, runner PID, the shown timeline time, the 2 details, and every
  anomaly chain. No score.
