# R3-098 runner brief (position 50, Class S, Tier B, Codex lane)

Prepared by coordinator (epoch 24), 2026-11-27. Prep reassignment per owner order 2026-11-26 21:36: prep Clone1 -> coordinator-live (Clone1 reduced to minimum; precedent R3-089, R3-096). Scorers: Fresh + Clone2 (F5.2 row, unchanged). Disjointness re-checked: prep = coordinator-live, scorers = Fresh + Clone2, no overlap.

## Task (from docs/rung3-list-100-tasks.md + docs/rung3-answer-keys.md, R3-098 section)

- File: ~/rung3/nd18-du-lieu.csv, 50 data rows + header, columns ten,nhom,so_tien. sha256: 71dd42639dadbd62d458d2304e30f05e7ed227f8b55387f830eadd4262648eea.
- Use awk in a terminal to compute per-group sums (NhomA/B/C/D) and the grand total. Write the report to ~/rung3/nd18-bao-cao.txt (or the name the task specifies; copy the report + outputs into the evidence dir).
- Expected (key): NhomA: 14 rows, sum 66193. NhomB: 12 rows, sum 52674. NhomC: 13 rows, sum 69300. NhomD: 11 rows, sum 51018. Grand total: 239185.
- Graded evidence: bao-cao.txt (evidence-requirements.json). Scorers re-run the awk read-only and compare.

## Evidence requirements (rung3-ci/evidence-requirements.json, R3-098)

- files: ["bao-cao.txt"], patterns: [], screenshots_min: 0.
- Save into ~/rung3-chung-cu/R3-098/: bao-cao.txt (required), the awk command(s) run (save the command text + output), start_time.txt, end_time.txt, drive-log.txt, pill screenshots if the pill is used.

## Drive rules (standing, restated)

- Cloudflare shim: NOT needed (terminal task, no browser).
- Pre-flight: hyprctl configerrors must be empty before launch.
- NEVER timeout-kill/SIGTERM the holder; stop via stop file, wait session_ended.
- Pill: plain "Computer use active" on ANY agent control. Acquire the pill with the LONG-LIVED codex process PID (or a long-lived terminal PID), NEVER an ephemeral shell PID (R3-089 lesson: shell exit auto-releases the pill ~1s later). Re-check pill status mid-drive.
- NEVER ydotool (ban).
- TEST LIKE A NORMAL USER: enter via search/homepage and click through like a normal user; no deep links, no direct commands, no internal setters; evidence shows entry, path, action, and resulting state. Terminal-file task: work in one visible terminal the normal way. (a) user entry point: an already-open terminal on ws2. (b) forbidden shortcuts: no GUI spreadsheet, no one-shot script that skips the visible awk steps, no editing the CSV.
- NEVER close/navigate owner tabs (YouTube, Todoist, Gmail, Calendar, PCCV sheet, FCC Admin, Welcome!, Chat - Muse, pinned/essentials). ws3 never touched, ws2 = run work, ws1 = owner's.
- Full access: codex exec --sandbox danger-full-access. Exactly ONE stdin redirect on launch.
- Timing/logging always on: wall-clock Asia/Ho_Chi_Minh + elapsed, full chain (failure -> reasoning -> attempts -> decision -> fix -> outcome) per the 18:20 super-detailed logging rule, into master event log + run log.
- NO personal info on GitHub ever. Fail only after 2-3 ways + retries.
- Ponytail for code work: smallest complete change, reuse before writing, stdlib/platform before dependencies, no unrequested abstraction, one small test for non-trivial logic, never cut validation/security/error handling.
- Graphify for codebase context (~/workspace/cu-graphify/graphify-out/).
- Class S: coordinator resets after scoring (clear evidence dir; report file removed).

## Coordinator notes

- Runner: codex exec per task from /home/james, -m gpt-6-luna --sandbox danger-full-access --skip-git-repo-check, Hyprland env exported in every launch.
- 30-min timeout per drive (watch kills by exact recorded PID).
- Before any INVALID grade: record whether an infrastructure re-run was considered.
