# R3-055 runner brief (Codex lane, R3-L3, position 33, Class L)

## Task (from frozen list docs/rung3-list-100-tasks.md, "### R3-055")

Create a new project folder tree from a template and set read-only permission
on one folder:

1. Read ~/rung3/d06-template.txt, record the required structure.
2. Create root ~/rung3/d06-du-an-moi with exactly: 5 level-1 folders
   (Tai-lieu, Ma-nguon, Kiem-thu, Du-lieu, Cong-cu) and 3 level-2 folders
   (Ma-nguon/thu-vien, Ma-nguon/ung-dung, Kiem-thu/kiem-thu-don-vi).
3. Create README.md at the root with: project name, creation date, folder list.
4. Create .gitignore with the template content: __pycache__/, *.pyc, .venv/
5. Set folder Tai-lieu read-only; all other folders normal read-write.
6. Verify the whole tree (tree command or open each folder).

## Drive method (terminal task, no browser)

- Launch `codex exec` from /home/james (gpt-6-luna, --sandbox
  danger-full-access, --skip-git-repo-check) with the GUI env exported:
  XDG_RUNTIME_DIR=/run/user/1000, WAYLAND_DISPLAY=wayland-1,
  DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus,
  HYPRLAND_INSTANCE_SIGNATURE = the dir name under /run/user/1000/hypr/
  (re-read per launch, never hardcode). Zen is already running (PID 578117);
  this task does not need it. No holder/probe (no browser drive).
- Work in a terminal on ws2. Read the template file first and follow it
  exactly. Create the tree, README.md, .gitignore, set Tai-lieu read-only
  (chmod a-w or 555), verify with `find`/`tree` and `ls -ld` on every folder.
- Evidence into ~/rung3-chung-cu/R3-055/:
  - A timestamped screenshot of the terminal showing the tree listing and the
    permissions of all folders.
  - bao-cao.txt: the template structure read, the created tree (full paths),
    README.md contents, .gitignore contents, and the permission of every
    folder (from ls -ld / stat output).
  - Copies of README.md and .gitignore as created.
  - start_time.txt / end_time.txt (ISO with +07:00).

## Class L note

R3-055 is Class L: score-before-reset. Do NOT delete or modify the created
tree after the drive; the reset (removing ~/rung3/d06-du-an-moi) happens only
after scoring, by coordinator instruction.

## Hard rules (restated per standing rules)

- The computer-use pill MUST show (label exactly "Computer use active") while
  any agent controls the machine. Verify visible during the drive and gone
  after; save a grim screenshot of the desktop after release.
- NEVER ydotool. NEVER close or navigate owner tabs, pinned tabs, essentials,
  or anything on ws3. Close only your own terminal window after use.
- Hyprland 0.57.2: hl.dsp OBJECT FORM ONLY for any dispatch (string-form
  dispatchers fail AND poison hyprctl configerrors, which breaks the overlay
  daemon). Pre-flight: `hyprctl configerrors` must be empty before launch
  (clear with `hyprctl eval "return true"` if needed, record the result).
- NEVER touch the FCC tmux pane (PID 22399) or the fcc-server on port 8082.
- No personal info anywhere in files or reports. English only (the folder
  names above are the task's own required names).
- Full access (Codex --sandbox danger-full-access). Log wall-clock
  Asia/Ho_Chi_Minh + elapsed. Do NOT score. Do NOT write coordinator state.
  Do NOT commit. Report facts only.
- LOGGING (owner rule 18:20): log EVERY event with the full chain:
  failure -> reasoning -> attempts -> decision -> fix -> outcome.

## Coordinator bookkeeping (driver script duties)

- Before launch: confirm Zen PID 578117 alive, no cursor.lock holder, no pill
  process, configerrors empty; confirm ~/rung3/d06-du-an-moi does NOT exist
  yet (clean start); record task_start + runner PID in the laptop event log
  via log-event.sh immediately (the coordinator copies them into state).
- Launch detached (setsid nohup ... > log 2>&1 < /dev/null & disown). SSH dies
  ~30 s; poll with short SSH calls (ps + tail log).
- On completion: pull evidence to /tmp/r3-055-evidence/ on the VM, sha256 every
  file, confirm the runner PID is gone, grim-check the pill is gone, log
  completion via log-event.sh, report facts (PID, start/end wall-clock,
  evidence paths + sha256, pill status, anything unusual, full chain for any
  anomaly).
- Hard timeout 30 minutes from launch.
