# R3-099 runner brief (position 51, Class S, Tier B, Codex lane)

Prepared by coordinator (epoch 24), 2026-11-27. Prep reassignment per owner order 2026-11-26 21:36: prep Clone1 -> coordinator-live (Clone1 reduced to minimum; precedent R3-089, R3-096, R3-098). Scorers: Clone2 + Fresh (F5.2 row, unchanged). Disjointness re-checked: prep = coordinator-live, scorers = Clone2 + Fresh, no overlap.

## Task (from docs/rung3-list-100-tasks.md + docs/rung3-answer-keys.md, R3-099 section)

- File: ~/rung3/nd19-du-lieu.csv, 50 data rows + header, columns ten,nhom,diem. sha256: fc7abae0e1b68312eac292518076bea9a9a03984d42d83279403728c2e20bea6.
- Write a Python script nd19-xu-ly.py that reads the CSV, computes per-group average scores (rounded to 2 decimals), and writes the report nd19-bao-cao.txt. Run the script twice; run 2 must produce a report identical to run 1.
- Expected (key): NhomA: 14 rows, average 7.91. NhomB: 12 rows, average 7.09. NhomC: 13 rows, average 7.86. NhomD: 11 rows, average 7.12. Tolerance 0.01.
- Graded evidence: script nd19-xu-ly.py + report nd19-bao-cao.txt. Scorers re-run the script read-only (on a copy if needed) and compare.

## Evidence requirements (rung3-ci/evidence-requirements.json, R3-099)

- files: ["bao-cao.txt"], patterns: [], screenshots_min: 0.
- Save into ~/rung3-chung-cu/R3-099/: bao-cao.txt (required; use the report name the task specifies and include a copy named bao-cao.txt if the names differ), nd19-xu-ly.py (the script), nd19-bao-cao.txt (run 1), the run 2 report copy, start_time.txt, end_time.txt, drive-log.txt, pill screenshots if the pill is used.

## Drive rules (standing, restated)

- Cloudflare shim: NOT needed (terminal task, no browser).
- Pre-flight: hyprctl configerrors must be empty before launch.
- NEVER timeout-kill/SIGTERM the holder; stop via stop file, wait session_ended.
- Pill: plain "Computer use active" on ANY agent control. Acquire the pill with the LONG-LIVED codex process PID (or a long-lived terminal PID), NEVER an ephemeral shell PID (R3-089 lesson: shell exit auto-releases the pill ~1s later). Re-check pill status mid-drive.
- NEVER ydotool (ban).
- TEST LIKE A NORMAL USER: enter via search/homepage and click through like a normal user; no deep links, no direct commands, no internal setters; evidence shows entry, path, action, and resulting state. Terminal-file task: write and run the script in one visible terminal the normal way. (a) user entry point: an already-open terminal on ws2. (b) forbidden shortcuts: no GUI spreadsheet, no pre-written script copied in without the visible write+run steps, no editing the CSV, no hard-coding the averages (the script must compute them from the CSV).
- NEVER close/navigate owner tabs (YouTube, Todoist, Gmail, Calendar, PCCV sheet, FCC Admin, Welcome!, Chat - Muse, pinned/essentials). ws3 never touched, ws2 = run work, ws1 = owner's.
- Full access: codex exec --sandbox danger-full-access. Exactly ONE stdin redirect on launch.
- Timing/logging always on: wall-clock Asia/Ho_Chi_Minh + elapsed, full chain (failure -> reasoning -> attempts -> decision -> fix -> outcome) per the 18:20 super-detailed logging rule, into master event log + run log.
- NO personal info on GitHub ever. Fail only after 2-3 ways + retries.
- Ponytail for code work: smallest complete change, reuse before writing, stdlib/platform before dependencies, no unrequested abstraction, one small test for non-trivial logic, never cut validation/security/error handling. (Script: stdlib csv only.)
- Graphify for codebase context (~/workspace/cu-graphify/graphify-out/).
- Class S: coordinator resets after scoring (clear evidence dir; script + reports removed).

## Coordinator notes

- Runner: codex exec per task from /home/james, -m gpt-6-luna --sandbox danger-full-access --skip-git-repo-check, Hyprland env exported in every launch.
- 30-min timeout per drive (watch kills by exact recorded PID).
- Before any INVALID grade: record whether an infrastructure re-run was considered.
