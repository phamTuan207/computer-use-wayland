# R3-075 runner brief (Codex lane, R3-L3, position 37, Class L, Tier B)

## Task (from frozen list docs/rung3-list-100-tasks.md, "### R3-075")

Install a Python virtual environment and run a sample app:

1. Open the terminal app, check the installed Python version with
   `python3 --version`, save a timestamped screenshot of the terminal
   showing the Python version into ~/rung3-chung-cu/R3-075/.
2. Create a virtual environment at ~/rung3/d41-venv with
   `python3 -m venv ~/rung3/d41-venv`.
3. Activate the venv, check the python path points into the venv dir
   (e.g. `which python`), save a timestamped screenshot of the terminal
   showing the venv python path into ~/rung3-chung-cu/R3-075/.
4. Install the packages in ~/rung3/d41-requirements.txt into the venv
   (`pip install -r ~/rung3/d41-requirements.txt`). If venv creation at
   step 2 or the pip install fails: retry ONCE after 5 minutes; if it
   still fails, write the error into ~/rung3-chung-cu/R3-075/ket-qua.txt
   and stop (task INVALID path per section 1 of the list; record the full
   chain).
5. Run the sample app ~/rung3/d41-app.py inside the venv, check it prints
   the expected greeting line, save a timestamped screenshot of the
   terminal showing the app output into ~/rung3-chung-cu/R3-075/.
6. Deactivate the venv, check the venv directory is still intact.

Pass: venv created at the right location, venv python path correct,
packages installed in full, sample app runs and prints the correct
greeting, venv intact after deactivate.
Fail: cannot create venv, python path wrong, package missing, app errors
or prints wrong output, venv deleted.

## User-path test fields (owner hard rule 26/11 05:01)

User-path test: enter via search/homepage and click through like a normal
user; no deep links, no direct commands, no internal setters; evidence shows
entry, path, action, and resulting state.

- (a) User entry point for this test: open the terminal app from the
  launcher like a normal user and type the commands in the visible
  terminal window; the three required screenshots show that terminal.
- (b) Forbidden shortcuts for this test: do NOT create the venv or install
  packages through a detached headless script or an SSH-only session as
  the recorded path; the commands must be typed in the visible terminal.
  Do NOT fake or reuse screenshots from another run. Do NOT delete the
  venv at the end (Class L: it stays until scored).
- Evidence must show: entry (terminal open with python3 --version), path
  (venv creation, activation, pip install), action (app run), resulting
  state (venv intact after deactivate). End-state only evidence is
  returned unread.

## Drive method (desktop GUI task, no browser)

- Launch `codex exec` from /home/james (gpt-6-luna, --sandbox
  danger-full-access, --skip-git-repo-check) with the GUI env exported:
  XDG_RUNTIME_DIR=/run/user/1000, WAYLAND_DISPLAY=wayland-1,
  DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus,
  HYPRLAND_INSTANCE_SIGNATURE = the dir name under /run/user/1000/hypr/
  (re-read per launch, never hardcode). Zen is already running (PID
  578117); this task does not need it. No holder/probe (no browser drive).
- Work on ws2. One driver at a time.
- Evidence into ~/rung3-chung-cu/R3-075/:
  - 3 timestamped terminal screenshots (Python version, venv python path,
    app output) (mandatory, minimum 3).
  - bao-cao.txt: Python version seen, venv python path seen, pip install
    result, app output lines, venv-intact check result, any anomaly with
    full chain.
  - start_time.txt / end_time.txt (ISO with +07:00).
  - drive-log.txt with the full chain for every anomaly:
    failure -> reasoning -> attempts -> decision -> fix -> outcome.
  - On the INVALID path only: ket-qua.txt with the venv/pip error.

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
- Class L score-before-reset: the venv at ~/rung3/d41-venv stays in place
  after the drive; do NOT reset until scored.
- 30-minute limit per drive. Timing/logging ALWAYS ON: wall-clock
  Asia/Ho_Chi_Minh + elapsed, full chain for every event.
- Ponytail for any code work: smallest complete change, reuse before
  writing, stdlib/platform before dependencies, no unrequested
  abstraction, one small test for non-trivial logic, never cut
  validation/security/error handling.
- NO personal info anywhere in evidence or logs.
- Delivery: evidence stays on the laptop in ~/rung3-chung-cu/R3-075/ plus
  a copy the driver transfers to the VM; the coordinator builds the
  snapshot. Report back with file list + sha256 per file, start/end
  times, runner PID, and every anomaly chain. No score.
