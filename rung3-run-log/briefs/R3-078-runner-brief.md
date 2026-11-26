# R3-078 runner brief (Codex lane, R3-L3, position 39, Class L, Tier B)

## Task (from frozen list docs/rung3-list-100-tasks.md, "### R3-078")

Back up the whole work folder to the backup location, verify checksums:

1. Open the work folder ~/rung3/d45-work, count the files and total size.
2. Copy the whole folder to the backup location ~/rung3/d45-backup,
   keeping the structure.
3. Compute the checksum of every original file and every backup file,
   compare pair by pair.
4. Write the backup list file: file name, size, checksum (one row per
   file).
5. Check the backup file count equals the original file count.
6. Open 3 backup files at fixed positions 1, 5, 10 by name order, check
   their contents match the originals.

Pass: backup file count equals original count, structure kept, checksums
match for all files, list has all rows, the 3 fixed-position files have
correct contents.
Fail: backup file missing, wrong structure, checksum wrong on more than
0 files, list missing rows, opened file content wrong.

## User-path test fields (owner hard rule 26/11 05:01)

User-path test: enter via search/homepage and click through like a normal
user; no deep links, no direct commands, no internal setters; evidence shows
entry, path, action, and resulting state.

- (a) User entry point for this test: open the work folder in the file
  manager like a normal user, count the files there, copy the folder to
  the backup location through the file manager UI, and open the 3
  fixed-position backup files in the UI to check contents.
- (b) Forbidden shortcuts for this test: do NOT do the copy with a
  detached headless script or rsync as the recorded path (this task is
  manual copy + checksum verification, not rsync, not a scheduled
  script). Do NOT write the backup list from a directory listing alone
  without computing the checksums. Do NOT skip opening the 3
  fixed-position files.
- Evidence must show: entry (work folder open with file count), path
  (copy action, checksum computation), action (list written, 3 files
  opened), resulting state (backup folder + list consistent). End-state
  only evidence is returned unread.

## Drive method (desktop GUI task, no browser)

- Launch `codex exec` from /home/james (gpt-6-luna, --sandbox
  danger-full-access, --skip-git-repo-check) with the GUI env exported:
  XDG_RUNTIME_DIR=/run/user/1000, WAYLAND_DISPLAY=wayland-1,
  DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus,
  HYPRLAND_INSTANCE_SIGNATURE = the dir name under /run/user/1000/hypr/
  (re-read per launch, never hardcode). Zen is already running (PID
  578117); this task does not need it. No holder/probe (no browser drive).
- Work on ws2. One driver at a time.
- Evidence into ~/rung3-chung-cu/R3-078/:
  - The backup list file (10 rows: file name, size, checksum) (mandatory).
  - bao-cao.txt: original file count + total size, backup file count,
    checksum comparison result (0 mismatches expected), the 3
    fixed-position content checks, any anomaly with full chain.
  - At least 1 timestamped screenshot (file manager showing the work
    folder or the backup folder) (mandatory, minimum 1).
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
- Class L score-before-reset: the backup folder ~/rung3/d45-backup and
  the backup list file stay in place after the drive; do NOT reset until
  scored.
- 30-minute limit per drive. Timing/logging ALWAYS ON: wall-clock
  Asia/Ho_Chi_Minh + elapsed, full chain for every event.
- Ponytail for any code work: smallest complete change, reuse before
  writing, stdlib/platform before dependencies, no unrequested
  abstraction, one small test for non-trivial logic, never cut
  validation/security/error handling.
- NO personal info anywhere in evidence or logs.
- Delivery: evidence stays on the laptop in ~/rung3-chung-cu/R3-078/ plus
  a copy the driver transfers to the VM; the coordinator builds the
  snapshot. Report back with file list + sha256 per file, start/end
  times, runner PID, and every anomaly chain. No score.
