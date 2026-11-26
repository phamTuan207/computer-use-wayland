# R3-076 runner brief (Codex lane, R3-L3, position 38, Class S, Tier B)

## Task (from frozen list docs/rung3-list-100-tasks.md, "### R3-076")

Check disk, RAM, heavy processes; report the top 5 processes:

1. Open the terminal app, run a command to check free disk space, save the
   result with a timestamp into ~/rung3/d42-lenh-dia.txt.
2. Run a command to check used and free RAM, save the result with a
   timestamp into ~/rung3/d42-lenh-ram.txt.
3. Run a command listing processes by CPU usage, take the top 5, save the
   result with a timestamp into ~/rung3/d42-lenh-tien-trinh.txt.
4. Record the name, PID, CPU usage, RAM usage of those 5 processes.
5. Write the report ~/rung3/d42-bao-cao.txt containing free disk, free RAM,
   the table of 5 processes, and the recording time.
6. Check the report has all 3 sections, the process table has name, PID,
   CPU, RAM columns, and the numbers match the saved command files.

Pass: report has all 3 sections; disk and RAM numbers match the saved
timestamped command files; the 5-process table has name, PID, CPU, RAM
matching the saved command file; recording time present in the report.
Fail: report missing a section, numbers differ from the saved command
files, table missing a process or a column, recording time missing,
command file missing.

Note: disk/RAM/process values are LIVE at run time; there are no frozen
expected values. The report is judged ONLY against the saved command
files, never against freshly re-run commands.

## User-path test fields (owner hard rule 26/11 05:01)

User-path test: enter via search/homepage and click through like a normal
user; no deep links, no direct commands, no internal setters; evidence shows
entry, path, action, and resulting state.

- (a) User entry point for this test: open the terminal app from the
  launcher like a normal user and type the check commands in the visible
  terminal window; save each command output to its file from that session.
- (b) Forbidden shortcuts for this test: do NOT generate the report from
  a detached headless script or an SSH-only session as the recorded path;
  the commands must be typed in the visible terminal. Do NOT edit the
  saved command files after saving them (the report must match them as
  saved). Do NOT re-run the commands later and overwrite the files to
  "fix" a mismatch; record any mismatch chain instead.
- Evidence must show: entry (terminal open), path (three commands run and
  saved with timestamps), action (report written), resulting state (report
  + 3 command files consistent). End-state only evidence is returned
  unread.

## Drive method (desktop GUI task, no browser)

- Launch `codex exec` from /home/james (gpt-6-luna, --sandbox
  danger-full-access, --skip-git-repo-check) with the GUI env exported:
  XDG_RUNTIME_DIR=/run/user/1000, WAYLAND_DISPLAY=wayland-1,
  DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus,
  HYPRLAND_INSTANCE_SIGNATURE = the dir name under /run/user/1000/hypr/
  (re-read per launch, never hardcode). Zen is already running (PID
  578117); this task does not need it. No holder/probe (no browser drive).
- Work on ws2. One driver at a time.
- Evidence into ~/rung3-chung-cu/R3-076/:
  - d42-bao-cao.txt (report: free disk, free RAM, 5-process table with
    name/PID/CPU/RAM, recording time) (mandatory).
  - d42-lenh-dia.txt, d42-lenh-ram.txt, d42-lenh-tien-trinh.txt (saved
    command outputs with timestamps) (mandatory).
  - bao-cao.txt: commands used, recording time, consistency self-check
    result, any anomaly with full chain.
  - start_time.txt / end_time.txt (ISO with +07:00).
  - drive-log.txt with the full chain for every anomaly:
    failure -> reasoning -> attempts -> decision -> fix -> outcome.
  - Screenshots of the terminal at each command are welcome but not
    required (screenshots_min 0).

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
- Class S: after scoring, the coordinator removes the d42-* result files
  from ~/rung3 (reset). Leave them in place until then.
- 30-minute limit per drive. Timing/logging ALWAYS ON: wall-clock
  Asia/Ho_Chi_Minh + elapsed, full chain for every event.
- Ponytail for any code work: smallest complete change, reuse before
  writing, stdlib/platform before dependencies, no unrequested
  abstraction, one small test for non-trivial logic, never cut
  validation/security/error handling.
- NO personal info anywhere in evidence or logs.
- Delivery: evidence stays on the laptop in ~/rung3-chung-cu/R3-076/ plus
  a copy the driver transfers to the VM; the coordinator builds the
  snapshot and runs the report-consistency checker. Report back with
  file list + sha256 per file, start/end times, runner PID, and every
  anomaly chain. No score.
