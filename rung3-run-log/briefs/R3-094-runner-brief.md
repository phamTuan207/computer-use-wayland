# R3-094 runner brief (Codex lane, R3-L3, position 48, Class S, Tier B)

## Task (from frozen list docs/rung3-list-100-tasks.md, "### R3-094")

Run a script that prints 3 environment variables, check the results:

1. Open ONE terminal window only, use the same window for the whole task,
   read the script ~/rung3/nd14-in-bien.sh, record the names of the 3
   environment variables the script prints. The script prints 3 variables
   R3_TEN, R3_TUOI, R3_THANH_PHO, one line per variable in the form
   "TEN=<value>".
2. Set values for the 3 variables in the current terminal with `export`,
   one specific value per variable from the requirement file
   (~/rung3/nd14-gia-tri.txt: R3_TEN=An, R3_TUOI=25, R3_THANH_PHO=Ha Noi).
3. Run the script, record the 3 output lines.
4. Change the value of 1 variable, run the script again, check only that
   variable's line changes.
5. Restore the old value for that variable, run a 3rd time, check the
   result is the same as run 1.
6. Save the results of the 3 script runs to 3 separate timestamped files
   in ~/rung3-chung-cu/R3-094/: lan-1-YYYYMMDD-HHMMSS.txt,
   lan-2-YYYYMMDD-HHMMSS.txt, lan-3-YYYYMMDD-HHMMSS.txt. Write the report
   with variable names, values per run, comparison results.

Pass: run 1 has all 3 lines with the correct set values, run 2 only 1 line
changes, run 3 same as run 1, report correct, report matches the 3 saved
result files.
Fail: missing output line, wrong variable value, run 2 changes more than 1
line, run 3 differs from run 1, report wrong.

## User-path test fields (owner hard rule 26/11 05:01)

User-path test: enter via search/homepage and click through like a normal
user; no deep links, no direct commands, no internal setters; evidence shows
entry, path, action, and resulting state.

- (a) User entry point for this test: open ONE terminal window like a
  normal user and use that same window for the whole task (exports must
  live in that shell), run the script from that window.
- (b) Forbidden shortcuts for this test: do NOT open a second terminal or
  a new shell for runs 2/3 (the exported values must persist in the same
  shell); do NOT edit the script; do NOT fabricate the output lines.
- Evidence must show: entry (one terminal window), path (3 runs in the
  same window), action (exports + runs), resulting state (3 timestamped
  files + report). End-state only evidence is returned unread.

## Drive method (desktop GUI task, no browser)

- Launch `codex exec` from /home/james (gpt-6-luna, --sandbox
  danger-full-access, --skip-git-repo-check) with the GUI env exported:
  XDG_RUNTIME_DIR=/run/user/1000, WAYLAND_DISPLAY=wayland-1,
  DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus,
  HYPRLAND_INSTANCE_SIGNATURE = the dir name under /run/user/1000/hypr/
  (re-read per launch, never hardcode). Zen is already running (PID
  578117); this task does not need it. No holder/probe (no browser drive).
- Work on ws2. One driver at a time.
- Evidence into ~/rung3-chung-cu/R3-094/:
  - lan-1-YYYYMMDD-HHMMSS.txt, lan-2-YYYYMMDD-HHMMSS.txt,
    lan-3-YYYYMMDD-HHMMSS.txt (mandatory).
  - The report (variable names, values per run, comparison results).
  - bao-cao.txt: steps, any anomaly with full chain.
  - start_time.txt / end_time.txt (ISO with +07:00).
  - drive-log.txt with the full chain for every anomaly:
    failure -> reasoning -> attempts -> decision -> fix -> outcome.
- Pill acquire: acquire with the LONG-LIVED codex process PID (or a
  long-lived terminal PID), never an ephemeral shell PID, and re-check
  pill status mid-drive (R3-089 pill-gap lesson).

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
- Delivery: evidence stays on the laptop in ~/rung3-chung-cu/R3-094/ plus
  a copy the driver transfers to the VM; the coordinator builds the
  snapshot. Report back with file list + sha256 per file, start/end
  times, runner PID, the 3 runs' outputs, and every anomaly chain.
  No score.
