# R3-074 runner brief (Codex lane, R3-L3, position 36, Class L, Tier B)

## Task (from frozen list docs/rung3-list-100-tasks.md, "### R3-074")

Find and fix a Python script that does not run, verify the result:

1. Open a terminal, run ~/rung3/d40-tinh-toan.py, record the error message,
   save a timestamped screenshot of the terminal showing the initial error
   to ~/rung3-chung-cu/R3-074/.
2. Open the script in a text editor application, read the whole code, find
   the line causing the error.
3. Fix the error. Do NOT rename variables. Do NOT change the script's main
   logic.
4. Run the script again, verify it finishes with no error.
5. Verify the result file ~/rung3/d40-ket-qua.txt has all 10 lines with the
   correct values in the expected file.
6. Run a second time, verify the result is identical to the first run.

## User-path test fields (owner hard rule 26/11 05:01)

User-path test: enter via search/homepage and click through like a normal
user; no deep links, no direct commands, no internal setters; evidence shows
entry, path, action, and resulting state.

- (a) User entry point for this test: open a terminal application on ws2
  like a normal user and run the script there; open the script in a text
  editor application (GUI) to read and fix it.
- (b) Forbidden shortcuts for this test: do NOT rewrite the script from
  scratch; do NOT fix it with sed/awk one-liners without first reading the
  code in the editor and identifying the faulty line (the task is find +
  fix, evidence must show the initial error and the identified line); do NOT
  rename variables or change main logic; do NOT hand-write the result file
  (it must be produced by running the fixed script).
- Evidence must show: entry (terminal run with initial error), path (script
  opened in editor, faulty line identified), action (fix + rerun), resulting
  state (result file with 10 lines, second run identical). End-state only
  evidence is returned unread.

## Drive method (desktop GUI + terminal task, no browser)

- Launch `codex exec` from /home/james (gpt-6-luna, --sandbox
  danger-full-access, --skip-git-repo-check) with the GUI env exported:
  XDG_RUNTIME_DIR=/run/user/1000, WAYLAND_DISPLAY=wayland-1,
  DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus,
  HYPRLAND_INSTANCE_SIGNATURE = the dir name under /run/user/1000/hypr/
  (re-read per launch, never hardcode). Zen is already running (PID 578117);
  this task does not need it. No holder/probe (no browser drive).
- Work on ws2. One driver at a time.
- Evidence into ~/rung3-chung-cu/R3-074/:
  - Timestamped screenshot of the terminal showing the INITIAL error
    (before any fix).
  - Copy of the fixed ~/rung3/d40-tinh-toan.py (as fixed, byte-identical).
  - Copy of ~/rung3/d40-ket-qua.txt from run 1 and from run 2 (name them
    ket-qua-run1.txt / ket-qua-run2.txt) so scorers can diff them.
  - bao-cao.txt: the initial error text, the faulty line identified, the
    exact fix made (old text -> new text), run 1 + run 2 outcomes, the 10
    result lines.
  - start_time.txt / end_time.txt (ISO with +07:00).
  - drive-log.txt with the full chain for every anomaly:
    failure -> reasoning -> attempts -> decision -> fix -> outcome.

## Class L note

R3-074 is Class L: score-before-reset. Do NOT delete or modify the fixed
script or the result file after the drive; the reset (restore the original
script from ~/rung3-goc) happens only after scoring, by coordinator
instruction. Scorers re-run the fixed script read-only from the snapshot
copy and compare the 10 lines.

## Hard rules (restated per standing rules)

- The computer-use pill MUST show (label exactly "Computer use active")
  while any agent controls the machine. Verify visible during the drive and
  gone after; save a grim screenshot of the desktop after release.
- NEVER ydotool. NEVER close or navigate owner tabs, pinned tabs,
  essentials, or anything on ws3. Close only your own terminal/editor
  windows after use.
- Hyprland 0.57.2: hl.dsp OBJECT FORM ONLY for any dispatch (string-form
  dispatchers fail AND poison hyprctl configerrors, which breaks the overlay
  daemon). Pre-flight: `hyprctl configerrors` must be empty before launch
  (clear with `hyprctl eval "return true"` if needed, record the result).
- NEVER timeout-kill/SIGTERM any session holder; stop via stop file and wait
  for session_ended; on abrupt death wait ~10 min and poll session.new.
- NEVER touch the FCC tmux pane (PID 22399) or the fcc-server on port 8082.
- No personal info anywhere in files or reports. English only (script and
  result file contents are the task's own fixtures).
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
  pill process, configerrors empty; confirm ~/rung3/d40-tinh-toan.py exists
  with sha256 f3b09ca0df66d3e4c4b8c88c78cffdb374d9ca6d988145587969034e4e3e7025
  (original buggy fixture) and ~/rung3/d40-ket-qua.txt does NOT exist yet
  (clean start); record task_start + runner PID in the laptop event log via
  log-event.sh immediately (the coordinator copies them into state at once).
- Launch detached (setsid nohup ... > log 2>&1 < /dev/null & disown). SSH
  dies ~30 s; poll with short SSH calls (ps + tail log).
- On completion: pull evidence to /tmp/r3-074-evidence/ on the VM, sha256
  every file, confirm the runner PID is gone, grim-check the pill is gone,
  log completion via log-event.sh, report facts (PID, start/end wall-clock,
  evidence paths + sha256, pill status, anything unusual, full chain for
  any anomaly).
- Hard timeout 30 minutes from launch.
