# DP-03 runner brief (Codex lane) - R3-L3, frozen position 31 (DP-03 replaces R3-047 at frozen position 34)

From: run coordinator epoch 23 (0d5fb18c). To: Codex exec runner (launched by the coordinator's driver at release).
Lane note: Codex exec drives DP-03. Lane-switch agreement rule: the assigned lane is fixed in this brief. A lane switch happens ONLY with coordinator agreement recorded in advance in the state file. If you cannot proceed in this lane, stop and report to the coordinator; never hand the task off silently.

Standing rules (restated): ydotool is BANNED, never use it. Pill "Computer use active" on any agent control, fail closed if not visible. One driver at a time on the shared desktop; never drive while another runner holds it. Never close or navigate owner-opened windows or tabs; close only your own task windows when done. ws3 untouched; work on ws2. Never restart Zen. Full access (--sandbox danger-full-access). English only. No personal info in any file. You never commit to the repo. You never read the answer keys (docs/rung3-answer-keys.*), the ledger, or any grade. Timeout: 30 minutes wall clock from task start to evidence-ready. Over 30 minutes is FAIL, stop, log.

Event-log duty: log key events via ~/workspace/agent-event-log/log-event.sh to the master log on the laptop at ~/agent-event-log/events.log. (On the laptop, append "ISO-ts | codex-DP-03 | <event>" to ~/agent-event-log/events.log if the helper is not present.)

Ponytail (applies if you write any code; this task needs none beyond drive scripts): smallest complete change, reuse what exists before writing, standard library and platform before new dependencies, no unrequested abstraction or for-later code, one small test for non-trivial logic, never cut validation, security, error handling, or accessibility.

Graphify for codebase context: query ~/workspace/cu-graphify/graphify-out/ instead of re-reading code.

User-path test: this is a desktop terminal task, not a web surface. Real entry point: the terminal application on the laptop desktop (foot or kitty), opened like a user opens it, command typed visibly. Forbidden shortcuts for this test: running ss only through a non-visible shell pipe with no terminal window and no screenshot, reading port data from /proc instead of the ss output, inventing process names not shown in the saved output. Evidence shows the terminal with the command and its output, the saved output file, and the report.

Desktop discipline (no browser holder for this task): acquire the pill first (overlay.py acquire --agent Codex --method Codex --pid <your-pid>; fail closed if visible is not true). Verify your terminal window is the focused window before typing (hyprctl activewindow); if focus moves to another window, stop sending input, try once to re-focus your own window, else stop cleanly and report. At task end: release the pill, verify pill gone by grim, close only your own terminal window.

## Task DP-03 (frozen list extract, section 8)

Check listening ports on localhost with the ss command; record port, protocol, process name.
N = 5 (pre-declared). N minimum 3.

Steps:
1. Open the terminal application. Run: ss -tlnp
   Save the full command output to ~/rung3-chung-cu/DP-03/ss-output.txt. Screenshot the terminal showing the command and output (timestamped) into ~/rung3-chung-cu/DP-03/.
   If process names are missing for ports (ss without root hides other users' processes), re-run with sudo so names show: sudo -S ss -tlnp < ~/.config/agent-computer-use/sudo-pass, and save THAT output as ss-output.txt (the saved output is what scorers check against; note in the report which form was used).
2. From the saved output, take the first 5 listening TCP ports that have a process name shown, in ascending port order. For each: port, protocol, process name.
   If fewer than 5 ports have process names, record the actual count (minimum 3). If fewer than 3, stop and report to the coordinator (the backup declares invalid before running per the frozen rule).
3. Write the report ~/rung3/nd43-bao-cao.txt with a table of N rows (port, protocol, process name), then copy it to ~/rung3-chung-cu/DP-03/bao-cao.txt. Values come from the saved ss-output.txt, never from a live re-run.

Evidence: ~/rung3-chung-cu/DP-03/ holds ss-output.txt, bao-cao.txt, timestamped terminal screenshot(s), start_time.txt, end_time.txt. Every file mtime inside the run window. Verify every action by file read-back, never by the act ok flag alone.

## Completion

Report to the coordinator: task ID DP-03, your session id, evidence folder path, start/end wall-clock times, the N recorded, any pill gap, anything unusual, and whether the drive completed. Then WAIT. Do not start any other task.
