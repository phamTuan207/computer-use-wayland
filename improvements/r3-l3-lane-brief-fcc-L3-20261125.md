# R3-L3 Lane Brief: FCC runner (positions 1-28)

- Date: 2026-11-25. Run: R3-L3, 55 tasks, branch todolist-push, frozen list commit 9b9d900, frozen key sha256 5059f6c447f9df0b63c092589bbba0df9efe37b2b6b962f7a32194054abfdae8. AMENDED 2026-11-25 (final prepare review): pill mechanism named (section 9); OpenRouter carve-out for the FCC backend (section 10). Re-acknowledgement required before task 1.
- This brief SUPERSEDES all earlier runner briefs. The three R3-L1 files on the laptop are VOID for this run: /home/james/rung3-runner-brief.md, /home/james/rung3-runner-brief-fcc.md, /home/james/rung3-fcc-runner-brief.md (all written 23/11 for R3-L1). Do NOT follow them. If any value in this brief conflicts with those files, THIS brief wins.
- Source of the rules in this brief: the R3-L3 re-plan ~/workspace/r3l3-run-wt/improvements/r3-l3-replan-final-20261124.md (worktree copy, the ONLY operative plan; the root copy is SUPERSEDED) and the execution plan ~/workspace/r3-l3-execution-plan-20261124.md. Pass bar 53/55. Invalid cap max 5 total, max 2 per difficulty group.
- No personal info in this brief. No credential value in this brief.
- No em dash or en dash in this brief. Commas, periods, short hyphens only.

## 1. Your lane

- Runner: FCC (fcc-claude CLI on the laptop). Session: tmux r3-fcc-runner-L3 on the laptop.
- Positions 1-28, in this fixed order, one task at a time, sequential:
  R3-001, R3-002, R3-003, R3-004, R3-005, R3-006, R3-007, R3-008, R3-009, R3-010, R3-011, R3-013, R3-014, R3-016, R3-017, R3-018, R3-019, R3-021, R3-022, R3-024, R3-025, R3-026, R3-027, R3-028, R3-029, R3-035, R3-036, R3-037.
- FIRST TASK IS R3-001 (position 1). Correction: the stale R3-L1 batch brief named R3-002 as the first task. That is WRONG for R3-L3. Do not start with R3-002.
- The run does NOT start until the coordinator releases task 1. Do NOT start any task until the coordinator assigns it to you in writing. Never run ahead, never run a task assigned to another runner, never re-run a task without a written coordinator order.

## 2. Corrections to the stale R3-L1 briefs (read this first)

- R3-082 expected values are 71, 78, 120, 89, 25 (frozen key). The stale briefs list 55, 75, 70, 68, 30. Those are WRONG. Do not use them. (R3-082 itself runs in the Codex lane, but the stale FCC briefs carried the wrong values, so this correction is recorded here too.)
- First task is R3-001, not R3-002 (see section 1).
- Scoring is NO LONGER always score-before-reset. Only Class L tasks are score-before-reset (section 5). Class S tasks use decoupled scoring: you proceed after the manifest gate passes.
- The old sessions r3-fcc-runner (R3-L2) and the old Codex tmux sessions are DELETED. Your session is r3-fcc-runner-L3 only.

## 3. What you read, and what you never read

- You read list section 6 ONLY (the task bodies). The coordinator hands you the section-6-only extract for your assigned task.
- You NEVER read: the frozen key file (docs/rung3-answer-keys.md, docs/rung3-answer-keys.json), list section 8, the trial report, the preflight report, rung3-ci/proof-log.md, the run ledger (rung3-run-log/R3-L3-grades.jsonl), any scorer brief, any coord file, or any grade while the run is in progress.
- If you find an answer in any of those places by accident, stop, tell the coordinator at once, and do not use it.

## 4. Frozen rulings you must follow

- DP-05 uses local sqlite3 on the laptop (/usr/bin/sqlite3), NOT sqliteonline.com. R3-021 still uses sqliteonline.com.
- R3-082 uses omacalc, NOT gnome-calculator. Expected results: 71, 78, 120, 89, 25. Table written in nano.
- No mid-run adaptation without a pre-written ruling. If a named tool is missing, stop and tell the coordinator. Do not improvise a replacement.

## 5. How each task runs

- Strictly sequential: one task at a time, in the fixed order, no parallel tasks, no skipping ahead.
- Class L (score-before-reset, you WAIT): R3-001 (position 1) is the only Class L task in your lane. For R3-001, finish the task, write the evidence, hand it to the coordinator, and WAIT. Both scorers score from the live state BEFORE the reset. You proceed only when the coordinator tells you the reset is done and assigns the next task.
- Class S (decoupled scoring, all other 27 tasks in your lane): finish the task, write the evidence and the snapshot, hand it to the coordinator. The coordinator runs the manifest gate (required files, sha256 per file, mtimes inside the run window). If the gate passes, the coordinator resets and you proceed to the next assigned task. Scorers score asynchronously from the sealed snapshot behind you. If the gate fails, do NOT proceed and NO reset happens: re-collect the missing or changed evidence and the coordinator re-runs the gate. After 3 gate failures for one task, the coordinator pauses the lane.
- Timeout: 30 minutes per task, wall clock, from task start to evidence-ready. Over 30 minutes is FAIL, stop, log. A timed-out task is never graded from partial evidence.
- Backpressure: max 2 unscored tasks outstanding. If you have 2 unscored tasks AND the oldest scoring lag exceeds 30 minutes, the coordinator pauses you (the other lane continues). You resume when the outstanding count drops below 2.
- Tier A tasks in your lane (the coordinator runs the checker once and hands the identical output to both scorers; you still write full evidence): R3-002, R3-007, R3-013, R3-014, R3-021.
- R3-029 (position 25): the test-account credential for this task comes to you in the task brief ONLY, from the coordinator. Never write the credential in any file, never put it in repo text, never send it anywhere else. If the task brief has no credential when position 25 arrives, stop and ask the coordinator. Do not guess it.
- Session rule (single driver): one driver at a time. Before you drive, confirm the session is free (the coordinator tells you when to start; if you get a guardian or session-busy error, STOP and report at once, do not retry blindly). Session free only by /proc fd scan for cursor.lock.

## 6. Evidence and snapshot (per task)

- Evidence goes in ~/rung3-chung-cu/R3-XXX/ on the laptop: timestamped screenshots plus ket-qua.txt exactly as the task requires. Every evidence file mtime must fall inside the run window for that task.
- Snapshot: each task has one snapshot dir, ~/workspace/rung3-snapshots/R3-xxx-L3/ (the -L3 suffix is mandatory). The snapshot carries a manifest.json with a sha256 per file and the mtime window.
- Report values come from saved files, never from a live re-run. Every reported value is derived from the saved command output files in the evidence folder.
- Verify every action by DOM or file read-back, never by the act ok flag alone. Write evidence even after a failed-flag episode.
- Clear inputs first (focus, ctrl+a, Backspace in one program), then set_value in a fresh program. set_value appends to existing text.
- Do not rely on dom_assert on inputs as the sole check; verify by eval read-back.
- DOM key names are ArrowDown and Enter, not Down and Return.
- After each state-changing action, take a screenshot and hash it. If the hash is unchanged after a state-changing action, retry once, then report a freeze to the coordinator.
- Never type a search into the urlbar; navigate by URL instead. If a page is slow, wait 60 seconds before reporting it stuck.

## 7. Heartbeat (re-plan rule)

- While you have an outstanding task, write one heartbeat line every 10 minutes into the shared append-only JSONL heartbeat log file (task ID, status, elapsed, next milestone). Check the file ends with a newline before appending, and parse-verify after.
- Heartbeats ride the shared log file, NOT the daemon. The daemon can die; the file does not. If you cannot reach the coordinator, keep writing heartbeats to the file.
- The coordinator does NOT ack each heartbeat. Acks are batched once per 30 minutes. A missing ack is normal, not a broken chain.

## 8. Self-stop at the task boundary (F-01)

- If you cannot reach the coordinator, finish the current task, preserve the evidence, and do NOT start the next one. This is the floor under every other failure rule. It bounds orphan work even if nobody takes over.
- If the run stalls (no progress 15 minutes, a service blocks, a fixture looks wrong), stop and tell the coordinator. Do not push on alone.
- If a service blocks you (429, 403, bot check, Turnstile), STOP and report. Do not hammer the service with repeat requests, do not open many tabs, do not try a workaround that changes the task. A block caused by your own repeat requests counts as FAIL, not invalid.

## 9. Pill (re-plan rule)

- The "Computer use active" pill MUST show on ANY live drive, before you drive. Re-acquire it proactively before any segment expected to exceed about 8 minutes. Log each acquire and expire with wall-clock time. Record any gap in the task evidence with its duration.
- Pill mechanism (exact, final review 25/11): before ANY live drive, acquire the pill with: python3 /home/james/computer-use-wayland/scripts/overlay.py acquire --agent FCC --method FCC --pid <your-own-pid>. Env on the laptop: HYPRLAND_INSTANCE_SIGNATURE (dir name under /run/user/1000/hypr), WAYLAND_DISPLAY=wayland-1, XDG_RUNTIME_DIR=/run/user/1000. FAIL CLOSED: if acquire does not return visible=true, do NOT drive. After the drive, release with: python3 /home/james/computer-use-wayland/scripts/overlay.py release --agent FCC --method FCC --pid <your-own-pid>. Check status with: python3 /home/james/computer-use-wayland/scripts/overlay.py status. After release, verify the pill is actually gone with a grim screenshot, not only with status (a session-owned pill can stay visible after release while status says false; fail-safe direction). End your computer-use session (finish) at the end of each task. Drives run on ws2. Before driving, confirm Zen is visible on ws2 (hyprctl workspaces shows Zen on ws2). If Zen is not visible on ws2, do NOT switch workspaces blindly; report to the coordinator and wait. Log each acquire and release with wall-clock time.

## 10. Git, models, personal data (re-plan rules)

- You NEVER commit, push, or edit repo files. Only the coordinator commits to the run-log branch during the run. (For the record, the coordinator rule is: explicit pathspec on BOTH the add and the commit, verify git status --porcelain shows only intended files before committing, never git add -A, verify every push via ls-remote.)
- NO OpenRouter for Opencode. Never try it, never propose it. No banned model routes of any kind. CARVE-OUT (owner decision 25/11 09:23): FCC MAY use its built-in OpenRouter-free backend (fcc-server reports provider open_router, model open_router/openrouter/free). The OpenRouter ban applies ONLY to Opencode. Your built-in backend is allowed; do not treat it as a violation and do not re-flag it.
- NO personal data in any repo text or evidence file: no real name, address, email, phone, schedule, photo, account, password, or token. The R3-029 credential stays in the task brief only (section 5) and never in a file.

## 11. What you NEVER do

- NEVER read the answer keys or any grade (section 3).
- NEVER reset fixtures (only the coordinator resets, after scoring, except the manifest-gate branch in section 5).
- NEVER commit anything to the repo.
- NEVER contact the scorers directly. All communication goes through the coordinator.
- NEVER open or navigate any tab or window the owner opened. NEVER close the owner's Zen tabs, Zalo, Teams, music, or any app you did not open.
- NEVER use ydotool.
- NEVER score. You never write a grade and never edit the ledger.

## 12. Handoff and acknowledgement

- When a task is done, write a short completion report in this pane: task ID, session ID (r3-fcc-runner-L3), evidence folder path, manifest hash, start and end wall-clock times, any pill gap, anything unusual. Then WAIT for the next task message.
- The run does NOT start until the coordinator releases task 1. Do NOT start any task until assigned.
- Acknowledge this brief IN WRITING in this pane with this exact line, filled in:
  ACK, FCC R3-L3 lane brief read, positions 1-28, first task R3-001, R3-082 values 71/78/120/89/25, waiting for task 1 from the coordinator. I will not start any task until assigned.
