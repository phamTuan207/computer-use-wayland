# R3-L3 pill path check, 2026-11-25

Pre-run test only. No run task was started, no run task was run. Both lanes were checked live on their actual drive paths, verified by screenshot.

## Verdicts

- FCC lane (positions 1-28, tmux session r3-fcc-runner-L3): PASS, with two caveats below.
- Codex lane (positions 29-55, codex exec 0.172.0): PASS on attempt 3. Attempts 1 and 2 did not complete the drive; both causes are documented below.

## FCC lane

Test window 10:54-10:57 Asia/Ho_Chi_Minh. Prompt sent via tmux paste-buffer to session r3-fcc-runner-L3. FCC replied in its pane and reported ready for task 1 afterwards.

- Pre: overlay status `{"holders": {}, "owner": "none", "visible": false}`. Pre grim `/tmp/pill-pre-fcc.png` viewed: pill absent.
- Acquire: visible true, twice observed. First acquire 10:54:53, owner daemon. Second acquire 10:57:07, owner session after `handover_to_session`. FCC reported acquire JSON: holders `FCC-PILL-TEST:22399`, acquired `2026-11-25T10:57:07+07:00`, label `Computer use active`, owner `session`, visible true.
- During: `/tmp/pill-during-fcc.png` viewed by me: the pill `Computer use active` is visible at top center during the drive. FCC opened one blank tab in Zen through its computer-use session, read the tab list, closed the tab (per its pane report; the tab open and close counts were not independently verified).
- Release: FCC reported `{"daemon_exiting": true, "holders": {}, "owner": "none", "visible": false}`. Independent overlay status check after the test confirmed holders empty, visible false.
- Post: workspace back to ws1, FCC pane idle at the prompt, waiting for task 1.

Caveats, FCC lane:

1. Stuck pill after release. The visual pill stayed on screen after FCC released: verified by viewing `/tmp/pill-post-fcc.png` (10:57), `/tmp/pill-verify-fcc.png` (10:59) and `/tmp/pill-verify2-fcc.png` (11:01). All three show the pill at top center while overlay status reported visible false. Root cause found in `overlay.py`, function `apply_holders`: when the pill owner is `session` (the live computer-use session indicator, after `handover_to_session`, confirmed in the daemon log at 10:57:00 and 10:57:07), the empty-holders branch returns visible False without sending `hide` to the session indicator. Only the daemon-owned branch sends `hide`. This failure mode is fail-safe (pill stuck ON, never stuck OFF), but status then lies about the visual state. I cleared it manually at 11:03:16 with an indicator `hide` request (acknowledged `hidden`), verified by viewing `/tmp/pill-pre-codex.png`: pill gone. No mechanism code was changed.
2. Leftover session. FCC left its computer-use session running after the test: session driver PID 157786 on pts/13 plus cursor guard and native indicator, started 10:56, plus Zen's quick-switcher dialog left open. That leftover session blocked the Codex lane attempt 1 (single-session latch). I ended it with the documented remedy `computer-use stop` at about 11:06, which also cleared the stuck pill. Verified: no session-driver, guard, or indicator processes remained, and `/tmp/pill-pre-codex2.png` (11:07) viewed: pill gone.
3. FCC struggled during the test: 7 computer-use-session calls with 6 failed, one wrong hyprctl syntax attempt (legacy `hyprctl dispatch workspace 2`), and two acquires. It completed and reported correctly.

## Codex lane

Three `codex exec` invocations, all launched detached from /home/james with `-s danger-full-access --skip-git-repo-check`, model default (gpt-6-luna per the lane brief). Prompt read from a file on stdin, final message captured with `-o`.

### Attempt 1, 11:04, PID 166854: drive did not start

- Acquire: PASS. `{"holders": {"CODEX-PILL-TEST:166853": {"acquired": "2026-11-25T11:04:22+07:00", "agent": "CODEX-PILL-TEST", "method": "CodexExec", "pid": 166853}}, "label": "Computer use active", "owner": "session", "visible": true}`.
- Drive: FAILED to start. Exact error: `{"ok": false, "error": "session guardian startup failed: another automation session or plugin activation is active"}`. Cause: FCC's leftover computer-use session from the FCC test still held the single-session latch. Codex sent no actions to Zen and stopped safely.
- During screenshot: not taken.
- Release: PASS. `{"daemon_exiting": true, "holders": {}, "owner": "none", "visible": false}`.
- Post grim `/tmp/pill-post-codex.png` (attempt 1) viewed: pill still visible, same stuck-pill defect as FCC (owner was session).

### Attempt 2, 11:08, PID 171725: drive ended immediately

- Acquire: PASS. `{"holders": {"CODEX-PILL-TEST:171724": {"acquired": "2026-11-25T11:08:23+07:00", "agent": "CODEX-PILL-TEST", "method": "CodexExec", "pid": 171724}}, "label": "Computer use active", "owner": "daemon", "visible": true}`.
- Drive: FAILED. Exact error: `window is not visible on its monitor; switch workspace yourself or use observe --window ADDRESS --focus`. Cause: my prompt told Codex to switch to workspace 2 first (the G-44 procedure, which was proven for BiDi). The pixel session driver can only see a window on the active workspace, and Zen lives on workspace 1. The session ended itself. Codex stopped safely.
- During screenshot: not taken.
- Release: PASS. `{"daemon_exiting": true, "holders": {}, "owner": "none", "visible": false}`.
- Post grim viewed: empty workspace 2 desktop, pill gone. This confirms the daemon-owned release hides the pill correctly, and confirms the drive failed because Zen was not on workspace 2.

### Attempt 3, 11:12, PID 176430: PASS

Procedure corrected: stay on workspace 1 where Zen is visible, no workspace 2 switch. The pill is a global overlay and shows on any workspace.

- Acquire: PASS. `{"holders": {"CODEX-PILL-TEST:176428": {"acquired": "2026-11-25T11:12:35+07:00", "agent": "CODEX-PILL-TEST", "method": "CodexExec", "pid": 176428}}, "label": "Computer use active", "owner": "daemon", "visible": true}`.
- Drive: DONE. Session driver started, Zen window observed with focus, one new about:blank tab opened, tab list read (count only), session finished cleanly.
- During: `/tmp/pill-during-codex.png` (11:13) viewed by me: the pill `Computer use active` is visible at top center, and the new blank tab is active in Zen.
- Release: PASS. `{"daemon_exiting": true, "holders": {}, "owner": "none", "visible": false}`.
- Post: `/tmp/pill-post-codex.png` (11:14) viewed by me: pill gone, Zen back on the pre-test tab, the test tab closed, the quick-switcher dialog closed.

## Findings for the run

1. Release does not hide a session-owned pill. In `overlay.py` `apply_holders`, the empty-holders branch only sends `hide` when owner is `daemon`. When owner is `session`, the last release leaves the pill visible on screen while status reports visible false. Fail-safe direction, but status cannot be trusted for the visual state in that case, and the lingering pill plus the lingering session block the next lane. The run procedure should verify the pill is actually gone with a grim, not only with status, and should end each lane's computer-use session (send `finish`) at the end of each task.
2. One session latch. The two lanes must never overlap drives. Before launching a lane's drive, verify no session-driver process from the other lane remains (`computer-use stop` is the documented remedy for a stuck session).
3. Workspace 2 first is BiDi-only. The Codex session-driver lane must drive where Zen is visible (workspace 1) or use `observe --window ADDRESS --focus`. Do not instruct the Codex lane to switch to workspace 2 before driving.
4. FCC's test left Zen's quick-switcher dialog open; Codex attempt 3 cleared it with observe and focus. Minor, no action needed.

## Evidence

Laptop paths (primary, under /tmp on the laptop):

- FCC: `/tmp/pill-pre-fcc.png`, `/tmp/pill-during-fcc.png`, `/tmp/pill-post-fcc.png`, `/tmp/pill-verify-fcc.png`, `/tmp/pill-verify2-fcc.png`, `/tmp/fcc-pill-test.txt`
- Codex: `/tmp/pill-pre-codex.png`, `/tmp/pill-pre-codex2.png`, `/tmp/pill-during-codex.png`, `/tmp/pill-post-codex.png`, `/tmp/codex-pill-test-prompt.txt`, `/tmp/codex-pill-test-prompt2.txt`, `/tmp/codex-pill-test-prompt3.txt`, `/tmp/codex-pill-test-attempt1.log`, `/tmp/codex-pill-test-attempt2.log`, `/tmp/codex-pill-test.log`, `/tmp/codex-pill-test-report.txt`, `/tmp/codex-pill-test-report-attempt1.txt`, `/tmp/codex-pill-test-report-attempt2.txt`
- VM copies of the screenshots are in `~/workspace/r3l3-run-wt/improvements/` next to this report (same file names, plus `pill-post-codex-attempt2.png` and `pill-post-codex-attempt3.png` for the Codex post shots and `pill-now-codex.png` for the 11:10 clean-state check).

This report contains no personal info: no tab titles, URLs, names, or message text. The screenshots themselves show the laptop screen and are kept local only; nothing was committed.

## End state, about 11:15

- Overlay status: holders empty, owner none, visible false.
- Active workspace: 1. No stray session-driver, guard, indicator, or codex exec processes.
- FCC pane idle at the prompt, waiting for task 1. It also ACKed an amended-brief request from the coordinator at 11:05, unrelated to this test.
- The run was NOT started. No run task was run by either lane.
