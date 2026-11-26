# R3-096 runner brief (Codex lane, R3-L3, position 49, Class L, Tier B)

## Task (from frozen list docs/rung3-list-100-tasks.md, "### R3-096")

Compare 2 config files with the diff command, merge 1 change, verify:

1. Open a terminal, run `diff` between ~/rung3/nd16-cu.conf and
   ~/rung3/nd16-moi.conf, record the number of differing lines.
2. Read the diff result, record the key name and old/new values of each
   differing line, total 4 differing lines.
3. Choose 1 differing line specified by the requirement file
   (~/rung3/nd16-yeu-cau.txt: merge cong (9090), only this 1 line), merge
   the new value into the old file, keep the other 3 differing lines at
   their old values.
4. Re-run `diff` between the old file after merging and the new file,
   check only 3 differing lines remain.
5. Open the old file, check the merged line has the new value, the other
   3 differing lines still keep the old values.
6. Write the report with: the 4 initial differing lines, the merged line,
   the number of remaining differing lines.

Pass: initially exactly 4 differing lines, after merging only 3 differing
lines remain, the merged line has the correct new value, the other 3
differing lines unchanged, report correct.
Fail: wrong differing-line count, wrong line merged, more than 1 line
merged, report wrong line count.

Key facts (for the runner's own verification): the 4 differing lines are
cong 8080 -> 9090; che_do dem -> ngay; ngon_ngu vi -> en; bo_nho 512 ->
1024. The requirement file specifies merging cong (9090) only.

## User-path test fields (owner hard rule 26/11 05:01)

User-path test: enter via search/homepage and click through like a normal
user; no deep links, no direct commands, no internal setters; evidence shows
entry, path, action, and resulting state.

- (a) User entry point for this test: open the terminal like a normal user
  and run the diff command exactly as the task steps say, then edit the
  old config file in a visible editor in the terminal session.
- (b) Forbidden shortcuts for this test: do NOT copy the new file over the
  old file (only the 1 specified line may change); do NOT merge more than
  1 line; do NOT fabricate the diff counts.
- Evidence must show: entry (terminal open), path (diff run, 1 line
  merged), action (second diff run), resulting state (merged file +
  report). End-state only evidence is returned unread.

## Drive method (desktop GUI task, no browser)

- Launch `codex exec` from /home/james (gpt-6-luna, --sandbox
  danger-full-access, --skip-git-repo-check) with the GUI env exported:
  XDG_RUNTIME_DIR=/run/user/1000, WAYLAND_DISPLAY=wayland-1,
  DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus,
  HYPRLAND_INSTANCE_SIGNATURE = the dir name under /run/user/1000/hypr/
  (re-read per launch, never hardcode). Zen is already running (PID
  578117); this task does not need it. No holder/probe (no browser drive).
- Work on ws2. One driver at a time.
- Evidence into ~/rung3-chung-cu/R3-096/:
  - The report (4 initial differing lines, merged line, remaining
    differing-line count) (mandatory).
  - A copy of the old config file after merging (nd16-cu.conf) (the file
    itself stays in ~/rung3/ until scored) (mandatory).
  - bao-cao.txt: steps, both diff outputs, any anomaly with full chain.
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
- Class L: score-before-reset. Do NOT restore ~/rung3/nd16-cu.conf after
  the drive; the coordinator resets only after scoring.
- 30-minute limit per drive. Timing/logging ALWAYS ON: wall-clock
  Asia/Ho_Chi_Minh + elapsed, full chain for every event.
- Ponytail for any code work: smallest complete change, reuse before
  writing, stdlib/platform before dependencies, no unrequested
  abstraction, one small test for non-trivial logic, never cut
  validation/security/error handling.
- NO personal info anywhere in evidence or logs.
- Delivery: evidence stays on the laptop in ~/rung3-chung-cu/R3-096/ plus
  a copy the driver transfers to the VM; the coordinator builds the
  snapshot. Report back with file list + sha256 per file, start/end
  times, runner PID, both diff counts + merged line, and every anomaly
  chain. No score.
