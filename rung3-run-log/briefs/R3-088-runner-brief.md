# R3-088 runner brief (Codex lane, R3-L3, position 45, Class L, Tier B)

## Task (from frozen list docs/rung3-list-100-tasks.md, "### R3-088")

Create a tar.gz archive with the tar command, verify and extract:

1. Open a terminal, count the files in ~/rung3/nd28-work and compute the
   total size.
2. Run `tar -czf` to compress the whole directory into
   ~/rung3/nd28-luu-tru.tar.gz; record the command used.
3. Run `tar -tzf` to list the entries in the archive, count the entries
   (including the root directory entry, total 11 entries) and the files
   (10 files, not counting the directory entry ending with /), compare
   with the source directory.
4. Extract the tar.gz into the new directory ~/rung3/nd28-check with
   `tar -xzf`.
5. Count the files after extraction, compare the contents of 3 files at
   fixed positions 1st, 5th, 10th in sorted name order.
6. Write the report ~/rung3/nd28-bao-cao.txt with: source file count,
   entries in archive (11), files in archive (10), files after
   extraction, the 3-file comparison results.

Pass: entries in archive = 11 (including root directory), files in archive
= source file count (10), files after extraction = source file count, 3
compared files correct content, report correct numbers, tar.gz file
exists.
Fail: missing file in archive, wrong file count after extraction, compared
file wrong content, report wrong numbers, or a compression format other
than tar.gz used.

Amendment (R3-L2, 2026-11-24): `tar -czf` of the whole directory then
`tar -tzf` counts 11 entries (root directory + 10 files); step 3 and the
grading criteria count entries (11) and files (10) separately; the
compression command is unchanged.

## User-path test fields (owner hard rule 26/11 05:01)

User-path test: enter via search/homepage and click through like a normal
user; no deep links, no direct commands, no internal setters; evidence shows
entry, path, action, and resulting state.

- (a) User entry point for this test: open the terminal like a normal user
  and type the tar commands exactly as the task steps say (the task itself
  defines these commands as the entry point; commands typed by hand, a
  typing error counts as an agent error per the list note).
- (b) Forbidden shortcuts for this test: do NOT create the archive with a
  GUI archive manager, Python tarfile, or any script as the recorded
  source; the archive must be created by the `tar -czf` command in the
  terminal. Do NOT fabricate counts or comparison results.
- Evidence must show: entry (terminal open), path (tar commands run),
  action (archive created + extracted), resulting state (tar.gz +
  nd28-check + nd28-bao-cao.txt). End-state only evidence is returned
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
- Evidence into ~/rung3-chung-cu/R3-088/:
  - bao-cao.txt: steps, the tar commands used, counts, comparison
    results, any anomaly with full chain (mandatory per
    evidence-requirements.json).
  - A copy of ~/rung3/nd28-bao-cao.txt (the report itself stays in
    ~/rung3/ until scored).
  - A copy of ~/rung3/nd28-luu-tru.tar.gz (the archive itself stays in
    ~/rung3/ until scored).
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
- Class L: score-before-reset. Do NOT remove ~/rung3/nd28-luu-tru.tar.gz,
  ~/rung3/nd28-check, or ~/rung3/nd28-bao-cao.txt after the drive; the
  coordinator resets only after scoring.
- 30-minute limit per drive. Timing/logging ALWAYS ON: wall-clock
  Asia/Ho_Chi_Minh + elapsed, full chain for every event.
- Ponytail for any code work: smallest complete change, reuse before
  writing, stdlib/platform before dependencies, no unrequested
  abstraction, one small test for non-trivial logic, never cut
  validation/security/error handling.
- NO personal info anywhere in evidence or logs.
- Delivery: evidence stays on the laptop in ~/rung3-chung-cu/R3-088/ plus
  a copy the driver transfers to the VM; the coordinator builds the
  snapshot. Report back with file list + sha256 per file, start/end
  times, runner PID, all counts, and every anomaly chain. No score.
