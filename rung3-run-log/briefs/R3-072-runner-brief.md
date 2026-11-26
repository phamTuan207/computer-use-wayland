# R3-072 runner brief (Codex lane, R3-L3, position 35, Class S, Tier A)

## Task (from frozen list docs/rung3-list-100-tasks.md, "### R3-072")

View 5 images with the imv image viewer and record file names + sizes from
the info overlay:

1. Open Nautilus, open the folder ~/rung3/d72-anh, record the 5 image file
   names.
2. Select all 5 files (Ctrl+A in the folder), press Enter to open all 5 in
   the laptop's default image viewer (imv-wayland), record the window title.
3. Press d to turn on the info overlay; if the overlay does not show, type
   :overlay then Enter. Record the file name and size (width x height) of
   the first image shown in the overlay. Save a timestamped screenshot of
   the overlay to ~/rung3-chung-cu/R3-072/.
4. Press Right arrow 4 times to view images 2, 3, 4, 5; record the file
   name and size of each.
5. Press q to close the viewer; check the Nautilus window is still open.
6. Open a text editor, write ~/rung3/d72-ket-qua.txt with a 5-row table
   (index, file name, size), save it, copy it to
   ~/rung3-chung-cu/R3-072/ket-qua.txt, reopen to verify.

## User-path test fields (owner hard rule 26/11 05:01)

User-path test: enter via search/homepage and click through like a normal
user; no deep links, no direct commands, no internal setters; evidence shows
entry, path, action, and resulting state.

- (a) User entry point for this test: open the folder in Nautilus like a
  normal user (file manager UI), select the 5 images there, and open them
  with Enter so the default viewer (imv-wayland) shows them.
- (b) Forbidden shortcuts for this test: do NOT read sizes with CLI tools
  (identify/file/identify -format, Python PIL, etc.) as the source of the
  recorded values; the recorded names + sizes must come from the imv info
  overlay in the visible UI. Do NOT open the images in a different viewer
  without recording why. Do NOT write ket-qua.txt from a directory listing
  alone.
- Evidence must show: entry (Nautilus folder with 5 files), path (viewer
  open, overlay on image 1, navigation), action (q close, editor write),
  resulting state (ket-qua.txt with 5 rows). End-state only evidence is
  returned unread.

## Drive method (desktop GUI task, no browser)

- Launch `codex exec` from /home/james (gpt-6-luna, --sandbox
  danger-full-access, --skip-git-repo-check) with the GUI env exported:
  XDG_RUNTIME_DIR=/run/user/1000, WAYLAND_DISPLAY=wayland-1,
  DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus,
  HYPRLAND_INSTANCE_SIGNATURE = the dir name under /run/user/1000/hypr/
  (re-read per launch, never hardcode). Zen is already running (PID 578117);
  this task does not need it. No holder/probe (no browser drive).
- Work on ws2. One driver at a time.
- Viewer binary is `imv-wayland` (NOT imv). After pressing q, verify the
  viewer process is gone (`pgrep -x imv-wayland` empty); if an instance
  hangs, kill it with `pkill -x imv-wayland` and record the chain. Never
  leave imv-wayland instances running.
- Evidence into ~/rung3-chung-cu/R3-072/:
  - Timestamped screenshot of the imv overlay on image 1 (mandatory).
  - ket-qua.txt: 5 rows, format per row: index, file name, size as
    "width x height" (spaces around x accepted). Also copy the editor file
    ~/rung3/d72-ket-qua.txt content identically.
  - bao-cao.txt: window title recorded at step 2, overlay values per image,
    Nautilus-still-open check result, any anomaly with full chain.
  - start_time.txt / end_time.txt (ISO with +07:00).
  - drive-log.txt with the full chain for every anomaly:
    failure -> reasoning -> attempts -> decision -> fix -> outcome.

## Hard rules (restated per standing rules)

- The computer-use pill MUST show (label exactly "Computer use active")
  while any agent controls the machine. Verify visible during the drive and
  gone after; save a grim screenshot of the desktop after release.
- NEVER ydotool. NEVER close or navigate owner tabs, pinned tabs,
  essentials, or anything on ws3. Close only your own windows after use
  (viewer via q, editor after save; leave Nautilus as the task leaves it,
  then close your Nautilus window if you opened it).
- Hyprland 0.57.2: hl.dsp OBJECT FORM ONLY for any dispatch (string-form
  dispatchers fail AND poison hyprctl configerrors, which breaks the overlay
  daemon). Pre-flight: `hyprctl configerrors` must be empty before launch
  (clear with `hyprctl eval "return true"` if needed, record the result).
- NEVER timeout-kill/SIGTERM any session holder; stop via stop file and wait
  for session_ended; on abrupt death wait ~10 min and poll session.new.
- NEVER touch the FCC tmux pane (PID 22399) or the fcc-server on port 8082.
- No personal info anywhere in files or reports. English only (file names
  above are the task's own fixture names).
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
  pill process, configerrors empty; confirm ~/rung3/d72-anh/ holds exactly
  5 image files (record names + sha256, do NOT use them as answer source);
  confirm ~/rung3/d72-ket-qua.txt does NOT exist yet (clean start); record
  task_start + runner PID in the laptop event log via log-event.sh
  immediately (the coordinator copies them into state at once).
- Launch detached (setsid nohup ... > log 2>&1 < /dev/null & disown). SSH
  dies ~30 s; poll with short SSH calls (ps + tail log).
- On completion: pull evidence to /tmp/r3-072-evidence/ on the VM, sha256
  every file, confirm the runner PID is gone, confirm no imv-wayland
  process remains, grim-check the pill is gone, log completion via
  log-event.sh, report facts (PID, start/end wall-clock, evidence paths +
  sha256, pill status, anything unusual, full chain for any anomaly).
- Hard timeout 30 minutes from launch.
