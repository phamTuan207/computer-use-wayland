# R3-082 runner brief (Codex lane, R3-L3, position 41, Class S, Tier A)

## Task (from frozen list docs/rung3-list-100-tasks.md, "### R3-082")

Compute 5 multi-step calculations with the desktop calculator, record
the results:

1. Open the omacalc calculator app on the machine (gnome-calculator is
   NOT on the laptop; use omacalc instead), do NOT use scientific mode.
2. Compute the first expression given by the task, record the result.
3. Compute the 2nd, 3rd, 4th, 5th expressions the same way (each has at
   least 3 operands and 2 operations).
4. Open a text editor, write a 6-row table (title + 5 calculation rows),
   each row with the expression and its result.
5. Pick any 1 expression, recompute it by hand, add 1 note line to the
   file in the form "Kiem tra lai: <expression> = <result>".
6. Save timestamped screenshots of the calculator app showing each
   expression and result into ~/rung3-chung-cu/R3-082/ (5 screenshots, one
   per calculation). Save the file ~/rung3/nd02-ket-qua.txt, copy it to
   ~/rung3-chung-cu/R3-082/ket-qua.txt, reopen to verify.

The 5 expressions (from the frozen list/key):
  (14 + 6) * 4 - 9
  120 / 5 + 18 * 3
  (60 - 24) * 3 + 12
  300 / 6 * 2 - 11
  (11 + 9) * 5 / 4

Pass: file has all 5 calculation rows, results correct within rounding
tolerance 0.01, 1 hand-check note line in the required form with the
correct result, no expression missing, screenshots show the correct
expression and result.
Fail: missing expression, wrong result beyond tolerance, expression with
fewer than 3 operands, missing hand-check note or wrong hand-check
result, file not saved.

## User-path test fields (owner hard rule 26/11 05:01)

User-path test: enter via search/homepage and click through like a normal
user; no deep links, no direct commands, no internal setters; evidence shows
entry, path, action, and resulting state.

- (a) User entry point for this test: open the omacalc app from the
  launcher like a normal user and type each expression into the visible
  calculator UI, reading each result off the calculator display.
- (b) Forbidden shortcuts for this test: do NOT compute the results with
  a shell, Python, or any CLI calculator as the recorded source; the
  recorded results must come from the omacalc UI. Do NOT use scientific
  mode. Do NOT write the table from memory without the 5 screenshots.
- Evidence must show: entry (omacalc open), path (each expression typed
  and result shown), action (editor table written + hand-check note),
  resulting state (ket-qua.txt with 6 rows + note). End-state only
  evidence is returned unread.

## Drive method (desktop GUI task, no browser)

- Launch `codex exec` from /home/james (gpt-6-luna, --sandbox
  danger-full-access, --skip-git-repo-check) with the GUI env exported:
  XDG_RUNTIME_DIR=/run/user/1000, WAYLAND_DISPLAY=wayland-1,
  DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus,
  HYPRLAND_INSTANCE_SIGNATURE = the dir name under /run/user/1000/hypr/
  (re-read per launch, never hardcode). Zen is already running (PID
  578117); this task does not need it. No holder/probe (no browser drive).
- Work on ws2. One driver at a time.
- Evidence into ~/rung3-chung-cu/R3-082/:
  - ket-qua.txt: 6-row table (title + 5 rows: expression, result) + 1
    hand-check note line "Kiem tra lai: <expression> = <result>"
    (mandatory). Identical copy of ~/rung3/nd02-ket-qua.txt.
  - 5 timestamped screenshots of omacalc showing each expression + result
    (mandatory, minimum 5).
  - bao-cao.txt: results per expression as read off the display, the
    hand-check expression + hand result, any anomaly with full chain.
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
- Class S: after scoring, the coordinator removes ~/rung3/nd02-ket-qua.txt
  (reset). Leave it in place until then.
- 30-minute limit per drive. Timing/logging ALWAYS ON: wall-clock
  Asia/Ho_Chi_Minh + elapsed, full chain for every event.
- Ponytail for any code work: smallest complete change, reuse before
  writing, stdlib/platform before dependencies, no unrequested
  abstraction, one small test for non-trivial logic, never cut
  validation/security/error handling.
- NO personal info anywhere in evidence or logs.
- Delivery: evidence stays on the laptop in ~/rung3-chung-cu/R3-082/ plus
  a copy the driver transfers to the VM; the coordinator builds the
  snapshot and runs the calculations checker. Report back with file
  list + sha256 per file, start/end times, runner PID, and every anomaly
  chain. No score.
