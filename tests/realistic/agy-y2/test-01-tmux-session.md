# test-01-tmux-session.md

## Test ID
test-01-tmux-session

## Topic
tmux terminal multiplexer: session creation, window management, pane splitting, mistake recovery, and reattachment.

## Context
A DevOps engineer needs to manage an interactive terminal multiplexer environment.
The workstation runs a local browser-based terminal multiplexer application (fixtures/test-01-tmux-session.html).
The user must create a session named "deploy", split panes, verify command execution, create a second window,
rename that window to "worker-logs", handle an accidental pane termination by undoing it, detach from the session,
inspect the session overview to verify 2 windows, reattach to the session, and save session state.

## Timing
- Baseline start time: 2026-11-21 17:00:00 Asia/Ho_Chi_Minh
- Expected duration: 180 seconds elapsed
- Maximum allowable latency: 300 seconds elapsed

## Goal
Create session "deploy", split panes, run uptime, add and rename window "worker-logs", kill and restore pane,
detach, verify 2 windows in session list, reattach, and save state.

## Exact steps
1. Open fixture tests/realistic/agy-y2/fixtures/test-01-tmux-session.html in the browser.
2. Verify element #session-count text is "0" and #status-indicator text is "No Active Session".
3. Click button #btn-new-session to open the new session dialog.
4. Verify element #session-modal has class "open".
5. Click input #input-session-name and type "deploy".
6. Click button #btn-create-session to initialize session "deploy".
7. Verify element #active-session-name text is "deploy".
8. Verify element #status-indicator text contains "deploy: Attached".
9. Verify element #window-count text is "1" and #pane-count text is "1".
10. Click button #btn-split-horizontal to split window 0 horizontally.
11. Verify element #pane-count text is "2".
12. Verify element #pane-2 is present and visible.
13. Click input #pane-terminal-input and type "uptime".
14. Click button #btn-send-command to execute the command.
15. Verify element #pane-active-output text contains "load average: 0.18, 0.22, 0.15".
16. Click button #btn-new-window to create a second tmux window.
17. Verify element #window-count text is "2".
18. Click button #btn-rename-window to open window rename modal.
19. Verify element #rename-window-modal has class "open".
20. Click input #input-window-name, clear existing text, and type "worker-logs".
21. Click button #btn-confirm-rename to apply the new window name.
22. Verify element #window-tab-1 text contains "1:worker-logs".
23. Click button #btn-split-vertical to split window 1 vertically.
24. Verify element #pane-count text is "2".
25. Simulate mistake: click button #btn-kill-pane to accidentally terminate the active pane.
26. Verify element #pane-count text drops to "1" and #alert-banner text contains "Pane 2 closed".
27. Recovery: click button #btn-undo-pane to restore the closed pane.
28. Verify element #pane-count text returns to "2".
29. Click button #btn-detach-session to detach from session deploy.
30. Verify element #status-indicator text contains "deploy: Detached" and #session-overview is visible.
31. Verify element #session-windows-deploy text is "2 windows".
32. Click button #btn-attach-deploy to reattach to session deploy.
33. Verify element #status-indicator text contains "deploy: Attached".
34. Click button #btn-save-session-state to persist the session configuration.
35. Verify element #saved-status-message text contains "Session deploy saved with 2 windows".

## Pass/fail criteria
- Pass: Session "deploy" exists with exactly 2 windows (window 0 "bash" and window 1 "worker-logs"), window 1 has 2 panes after undo recovery, session detachment and reattachment succeed, and saved state is confirmed.
- Fail: Session not created, window 1 missing or not renamed, wrong pane count, undo not triggered, or state not saved.

## Errors designed to expose
- click miss: Terminal action buttons and modal inputs require precise coordinate clicks.
- slow think: Delays during multi-pane navigation and modal interactions.
- stale observation: Reading pane count before DOM update completes following undo.
- wrong diagnosis: Mistaking an accidental pane close for an unrecoverable failure instead of using undo.
- fabrication: Asserting session state without verifying saved status banner.

## Checker / expected end state
```bash
node tests/realistic/agy-y2/check.mjs --fixture tests/realistic/agy-y2/fixtures/test-01-tmux-session.html --test 01
```
