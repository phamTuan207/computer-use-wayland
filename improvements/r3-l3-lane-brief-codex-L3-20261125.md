# R3-L3 Lane Brief: Codex runner (positions 29-55)

- Date: 2026-11-25. Run: R3-L3, 55 tasks, branch todolist-push, frozen list commit 9b9d900, frozen key sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8. AMENDED 2026-11-25 (final prepare review): R3-047 dropped by owner order, DP-03 replaces it at position 34; pill mechanism named (section 11). Re-acknowledgement required before task 1.
- This brief SUPERSEDES all earlier runner briefs. The R3-L1 Codex brief (/home/james/rung3-runner-brief-codex.md and ~/workspace/rung3-runner-brief-codex.md, written 23/11 for R3-L1) is VOID for this run. Do NOT follow it. If any value in this brief conflicts with that file, THIS brief wins.
- Source of the rules in this brief: the R3-L3 re-plan ~/workspace/r3l3-run-wt/improvements/r3-l3-replan-final-20261124.md (worktree copy, the ONLY operative plan; the root copy is SUPERSEDED) and the execution plan ~/workspace/r3-l3-execution-plan-20261124.md. Pass bar 53/55. Invalid cap max 5 total, max 2 per difficulty group.
- No personal info in this brief. No credential value in this brief.
- No em dash or en dash in this brief. Commas, periods, short hyphens only.

## 1. Your lane

- Runner: Codex (Codex CLI on the laptop, model gpt-6-luna). Delivery: one `codex exec` invocation per task, launched by the coordinator from /home/james. There is NO interactive Codex tmux session for this run. The old tmux sessions r3-codex-runner and r3-codex-runner-L3 are DELETED. Do not use them. Do not touch the A1 pilot tmux session.
- Positions 29-55, in this fixed order, one task at a time, sequential:
  R3-040, R3-041, R3-042, R3-045, R3-046, DP-03, R3-049, R3-055, R3-067, R3-072, R3-074, R3-075, R3-076, R3-078, R3-079, R3-082, R3-083, R3-085, R3-086, R3-088, R3-089, R3-093, R3-094, R3-096, R3-098, R3-099, R3-100. (DP-03 replaces the dropped R3-047 at position 34, owner order 25/11 10:34. R3-047 does not run.)
- The run does NOT start until the coordinator releases task 1. Do NOT start any task until the coordinator assigns it to you in writing (one codex exec invocation per assigned task). Never run ahead, never run a task assigned to another runner, never re-run a task without a written coordinator order.

## 2. Corrections to the stale R3-L1 brief

- R3-082 expected values are 71, 78, 120, 89, 25 (frozen key). The stale brief lists 55, 75, 70, 68, 30. Those are WRONG. Do not use them. R3-082 is position 45 in YOUR lane.
- Scoring is NO LONGER always score-before-reset. Only Class L tasks are score-before-reset (section 5). Class S tasks use decoupled scoring: the lane proceeds after the manifest gate passes.
- The old interactive Codex sessions are gone. Each task is one codex exec invocation (section 1), not a persistent session.

## 3. What you read, and what you never read

- You read list section 6 ONLY (the task bodies). The coordinator hands you the section-6-only extract for your assigned task, inside the codex exec prompt for that task.
- You NEVER read: the frozen key file (docs/rung3-answer-keys.md, docs/rung3-answer-keys.json), list section 8, the trial report, the preflight report, rung3-ci/proof-log.md, the run ledger (rung3-run-log/R3-L3-grades.jsonl), any scorer brief, any coord file, or any grade while the run is in progress.
- If you find an answer in any of those places by accident, stop, tell the coordinator at once, and do not use it.

## 4. Frozen rulings you must follow

- DP-05 uses local sqlite3 on the laptop (/usr/bin/sqlite3), NOT sqliteonline.com. R3-021 still uses sqliteonline.com.
- R3-082 uses omacalc, NOT gnome-calculator. Expected results: 71, 78, 120, 89, 25. Table written in nano.
- No mid-run adaptation without a pre-written ruling. If a named tool is missing, stop and tell the coordinator. Do not improvise a replacement.

## 5. How each task runs

- Strictly sequential: one task at a time, in the fixed order, no parallel tasks, no skipping ahead.
- Class L (score-before-reset, the lane WAITS): 8 tasks in your lane. For each, finish the task, write the evidence, hand it to the coordinator, and WAIT. Both scorers score from the live state BEFORE the reset. The lane proceeds only when the coordinator says the reset is done and assigns the next task.
  - R3-055 (position 36): scorer opens each directory and checks permissions live.
  - R3-074 (position 39): scorer re-runs a read-only script and compares 10 lines live.
  - R3-075 (position 40): scorer checks the venv exists and packages are installed live.
  - R3-078 (position 42): scorer checks the backup file count and checksums of 3 fixed backup files live.
  - R3-079 (position 43): scorer opens the restored file live and compares with manifest.txt. Coupled reset applied before this position.
  - R3-088 (position 48): scorer lists files in the tar.gz archive and counts (11 entries, 10 files) live.
  - R3-089 (position 49): scorer re-runs find (read-only) on the live log files. Fixture refresh verified before this position (find -mtime -7 must return exactly 6).
  - R3-096 (position 52): scorer re-runs diff (read-only) on the live config files.
- Class S (decoupled scoring, the other 19 tasks in your lane): finish the task, write the evidence and the snapshot, hand it to the coordinator. The coordinator runs the manifest gate (required files, sha256 per file, mtimes inside the run window). If the gate passes, the coordinator resets and the lane proceeds to the next assigned task. Scorers score asynchronously from the sealed snapshot behind the lane. If the gate fails, do NOT proceed and NO reset happens: re-collect the missing or changed evidence and the coordinator re-runs the gate. After 3 gate failures for one task, the coordinator pauses the lane.
- Timeout: 30 minutes per task, wall clock, from task start to evidence-ready. Over 30 minutes is FAIL, stop, log. A timed-out task is never graded from partial evidence. (R3-040 ran 4h05 in R3-L2. That must not recur.)
- Backpressure: max 2 unscored tasks outstanding. If the lane has 2 unscored tasks AND the oldest scoring lag exceeds 30 minutes, the coordinator pauses the lane (the other lane continues). The lane resumes when the outstanding count drops below 2.
- Tier A tasks in your lane (the coordinator runs the checker once and hands the identical output to both scorers; you still write full evidence): R3-072, R3-082.
- Pre-milestone reminders in your lane: DP-03 runs at position 34 in place of the dropped R3-047 (owner order 25/11 10:34). No Gutenberg check, no Gutenberg monitoring. R3-079 coupled reset before position 43. R3-089 fixture verified before position 49. R3-100 port check before position 55 (R3-100 is graded from saved files only; the live port check is done by the runner at run time, immediately after the task, and recorded in the evidence).
- Session rule (single driver): one driver at a time. Before you drive, confirm the session is free. Session free only by /proc fd scan for cursor.lock. If you get a guardian or session-busy error, STOP and report at once, do not retry blindly.

## 6. Durable trace per codex exec invocation (re-plan rule, G-25)

- For EVERY task invocation, the coordinator records, BEFORE launch: task ID, session ID, and the full launch command. IMMEDIATELY after spawn, the coordinator records the PID, verified by ps, before any task work starts.
- Your invocation reports the same trace back in its output: task ID, session ID, launch command, PID.
- This trace is what lets the coordinator kill a stale invocation by exact recorded PID only (never by pkill -f), and what proves which invocation drove which task if the coordinator dies mid-task.

## 7. Retry rule (re-plan rule, section 1)

- If a codex exec invocation fails, the coordinator retries ONLY after checking the evidence dir and the runner state (no partial drive recorded).
- If a partial drive IS recorded, the coordinator re-runs the task from the START on a clean fixture. NEVER resume the failed invocation. Never continue a half-driven task.
- If the invocation itself fails to launch (no PID, no output), the coordinator records the failure and relaunches with a fresh invocation, same rule.

## 8. Evidence and snapshot (per task)

- Evidence goes in ~/rung3-chung-cu/R3-XXX/ on the laptop: timestamped screenshots plus ket-qua.txt exactly as the task requires. Every evidence file mtime must fall inside the run window for that task.
- Snapshot: each task has one snapshot dir, ~/workspace/rung3-snapshots/R3-xxx-L3/ (the -L3 suffix is mandatory). The snapshot carries a manifest.json with a sha256 per file and the mtime window.
- Report values come from saved files, never from a live re-run. Every reported value is derived from the saved command output files in the evidence folder.
- Verify every action by DOM or file read-back, never by the act ok flag alone. Write evidence even after a failed-flag episode.
- Clear inputs first (focus, ctrl+a, Backspace in one program), then set_value in a fresh program. set_value appends to existing text.
- Do not rely on dom_assert on inputs as the sole check; verify by eval read-back.
- DOM key names are ArrowDown and Enter, not Down and Return.
- After each state-changing action, take a screenshot and hash it. If the hash is unchanged after a state-changing action, retry once, then report a freeze to the coordinator.
- Never type a search into the urlbar; navigate by URL instead. If a page is slow, wait 60 seconds before reporting it stuck.

## 9. Heartbeat (re-plan rule)

- While you have an outstanding task, write one heartbeat line every 10 minutes into the shared append-only JSONL heartbeat log file (task ID, status, elapsed, next milestone). Check the file ends with a newline before appending, and parse-verify after.
- Heartbeats ride the shared log file, NOT the daemon. The daemon can die; the file does not. If you cannot reach the coordinator, keep writing heartbeats to the file.
- The coordinator does NOT ack each heartbeat. Acks are batched once per 30 minutes. A missing ack is normal, not a broken chain.

## 10. Self-stop at the task boundary (F-01)

- If you cannot reach the coordinator, finish the current task, preserve the evidence, and do NOT start the next one. This is the floor under every other failure rule. It bounds orphan work even if nobody takes over.
- If the run stalls (no progress 15 minutes, a service blocks, a fixture looks wrong), stop and tell the coordinator. Do not push on alone.
- If a service blocks you (429, 403, bot check, Turnstile), STOP and report. Do not hammer the service with repeat requests, do not open many tabs, do not try a workaround that changes the task. A block caused by your own repeat requests counts as FAIL, not invalid.

## 11. Pill (re-plan rule)

- The "Computer use active" pill MUST show on ANY live drive, before you drive. Re-acquire it proactively before any segment expected to exceed about 8 minutes. Log each acquire and expire with wall-clock time. Record any gap in the task evidence with its duration.
- Pill mechanism (exact, final review 25/11): before ANY live drive, acquire the pill with: python3 /home/james/computer-use-wayland/scripts/overlay.py acquire --agent CODEX --method CodexExec --pid <your-own-pid>. Env on the laptop: HYPRLAND_INSTANCE_SIGNATURE (dir name under /run/user/1000/hypr), WAYLAND_DISPLAY=wayland-1, XDG_RUNTIME_DIR=/run/user/1000. FAIL CLOSED: if acquire does not return visible=true, do NOT drive. After the drive, release with: python3 /home/james/computer-use-wayland/scripts/overlay.py release --agent CODEX --method CodexExec --pid <your-own-pid>. Check status with: python3 /home/james/computer-use-wayland/scripts/overlay.py status. After release, verify the pill is actually gone with a grim screenshot, not only with status (a session-owned pill can stay visible after release while status says false; fail-safe direction). End your computer-use session (finish) at the end of each task. Drives run on ws2. Before driving, confirm Zen is visible on ws2 (hyprctl workspaces shows Zen on ws2). If Zen is not visible on ws2, do NOT switch workspaces blindly; report to the coordinator and wait. Log each acquire and release with wall-clock time.

## 12. Git, models, personal data (re-plan rules)

- You NEVER commit, push, or edit repo files. Only the coordinator commits to the run-log branch during the run. (For the record, the coordinator rule is: explicit pathspec on BOTH the add and the commit, verify git status --porcelain shows only intended files before committing, never git add -A, verify every push via ls-remote.)
- NO OpenRouter. Never try it, never propose it. No banned model routes of any kind. (The OpenRouter ban applies ONLY to Opencode; it does not restrict Codex's own backend.)
- NO personal data in any repo text or evidence file: no real name, address, email, phone, schedule, photo, account, password, or token. No credential value in any brief or file.

## 13. What you NEVER do

- NEVER read the answer keys or any grade (section 3).
- NEVER reset fixtures (only the coordinator resets, after scoring, except the manifest-gate branch in section 5).
- NEVER commit anything to the repo.
- NEVER contact the scorers directly. All communication goes through the coordinator.
- NEVER open or navigate any tab or window the owner opened. NEVER close the owner's Zen tabs, Zalo, Teams, music, or any app you did not open.
- NEVER use ydotool.
- NEVER score. You never write a grade and never edit the ledger.

## 14. Handoff and acknowledgement

- When a task is done, the invocation output reports: task ID, session ID, PID, evidence folder path, manifest hash, start and end wall-clock times, any pill gap, anything unusual. Then the invocation ends and the lane waits for the next assigned task.
- The run does NOT start until the coordinator releases task 1. Do NOT start any task until assigned.
- Acknowledge this brief IN WRITING with this exact line, filled in:
  ACK, Codex R3-L3 lane brief read, positions 29-55, first task R3-040, R3-082 values 71/78/120/89/25, durable trace and retry rules understood, waiting for task 1 from the coordinator. I will not start any task until assigned.
