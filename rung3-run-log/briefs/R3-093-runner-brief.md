# R3-093 runner brief (Codex lane, R3-L3, position 47, Class S, Tier B)

## Task (from frozen list docs/rung3-list-100-tasks.md, "### R3-093")

Split a large file into 3 parts, rejoin, verify checksum:

1. Open a terminal, check the size and checksum of the source file
   ~/rung3/nd13-file-lon.bin.
2. Split the source file into 3 equal parts with the command
   `split -n 3 -d --numeric-suffixes=1 -a 2 ~/rung3/nd13-file-lon.bin ~/rung3/phan-`,
   named phan-01, phan-02, phan-03 (each part 1000000 bytes).
3. Check the number of parts = 3, total size of the 3 parts = source
   file size.
4. Rejoin the 3 parts into the new file ~/rung3/nd13-ghep-lai.bin with
   the `cat` command.
5. Compute the checksum of the new file, compare with the source checksum.
6. Write the report ~/rung3/nd13-bao-cao.txt with: source file size, each
   part size, source checksum, new checksum; copy the report, the 3 part
   files, and the rejoined file into ~/rung3-chung-cu/R3-093/.

Pass: exactly 3 parts, total size of the 3 parts = source file, new file
checksum matches the source, report correct numbers.
Fail: missing part, wrong total size, different checksums, report wrong
numbers.

Amendment (R3-L3, 2026-11-24): default split cuts by 1000 lines (12 parts
measured); `split -n 3 -d` gives phan-00/01/02; only --numeric-suffixes=1
gives phan-01/02/03. Step 2 uses the full split command with flags; step 6
states the report path and copies evidence into the R3-093 directory.

## User-path test fields (owner hard rule 26/11 05:01)

User-path test: enter via search/homepage and click through like a normal
user; no deep links, no direct commands, no internal setters; evidence shows
entry, path, action, and resulting state.

- (a) User entry point for this test: open the terminal like a normal user
  and run the split/cat/checksum commands exactly as the task steps say
  (the task itself defines these commands as the entry point).
- (b) Forbidden shortcuts for this test: do NOT copy the source file as
  the rejoined file (the rejoined file must come from `cat` of the 3
  parts); do NOT fabricate sizes or checksums; do NOT reuse outputs from
  any earlier run.
- Evidence must show: entry (terminal open), path (split + cat run),
  action (checksums computed), resulting state (3 parts + rejoined file +
  report in ~/rung3-chung-cu/R3-093/). End-state only evidence is returned
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
- Evidence into ~/rung3-chung-cu/R3-093/:
  - nd13-bao-cao.txt (copy of ~/rung3/nd13-bao-cao.txt) (mandatory).
  - The 3 part files phan-01, phan-02, phan-03 (copies) (mandatory).
  - nd13-ghep-lai.bin (copy of the rejoined file) (mandatory).
  - bao-cao.txt: steps, commands used, any anomaly with full chain.
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
- Delivery: evidence stays on the laptop in ~/rung3-chung-cu/R3-093/ plus
  a copy the driver transfers to the VM; the coordinator builds the
  snapshot. Report back with file list + sha256 per file, start/end
  times, runner PID, sizes + checksums, and every anomaly chain. No score.
