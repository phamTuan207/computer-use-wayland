# Worker C5-FOCUS-INCIDENT log: why focus moved for M1 and M2

Role: independent investigation of two misdirected-keystroke incidents
by worker C5-MOZ-GROWTH on the laptop. I did not do that work; I
investigate its failure. No code changes in this task. Report to the
COORD-CLICK-5 coordinator only, never message the user. Owner asleep
since 06:52 with a headache; Muse holds full authority.

Standing rules: wall-clock Asia/Ho_Chi_Minh plus elapsed time on
every log entry. No em dash (U+2014) or en dash (U+2013) anywhere.
No personal info on GitHub. Commit with explicit pathspec only,
immediately after staging, never plain git commit, never git add -A.
Verify every push with git ls-remote. Never ydotool.

Task start: 2026-11-22 11:28:09 +07 (T+0m). Task end:
2026-11-22 11:44:31 +07 (T+16m). Total elapsed about 16 minutes.

## 0. Primary sources read (T+0m to T+4m)

- C5-MOZ-GROWTH log, read in full:
  improvements/worker-click5-moz-growth-log.md on todolist-push,
  commit a42ef12. Section 4 (M1/M2) in full. Its pixel verdict
  (true viewport origin (240, 8)) is NOT my task; only the two
  incidents are.
- clone2-watch log, runs 47, 48, 49 (10:41 to 11:14 +07), read in
  full:
  ~/workspace/goals/zen-i-u-khi-n-c-t-i-a-b-i-agent-v-muse/hidden_files/clone2-watch-log.md.
- watchdog-zen-20m log, 11:12-11:15 +07 entry, read in full
  (same hidden_files dir, watchdog-log.md).
- Repo state at read time: branch todolist-push, HEAD 6aa911b
  (coord log noting this investigation spawned). Other workers
  have uncommitted changes in scripts/ and tests/; this log
  touches only its own file.

## 1. Merged timeline, all times +07

- 10:56:56 run 48 of clone2-watch starts (scheduled, every 15m).
- 10:57 clone1 commit 81ea6e0, batch 10 assigned, 3 subagents
  dispatched. Clone1 works in Brave on ws1.
- 10:58:xx run 48 switches to ws2 (proven command
  hl.dsp.focus({ workspace = 2 })). Active window after switch:
  clone2 Chrome 0x5570538ed160.
- 10:59:19 run 48 returns to ws1 (hl.dsp.focus({ workspace = 1 })).
  Verified active window: clone1 Brave 0x55705383d420, NOT Zen.
- 11:00:41 MOZ-GROWTH pre-state: active window Brave (ws1).
  Zen 0x557052b62dd0 at [2509, 914], [925, 1176], ws1, PID 496121.
  Chromium PID 8059 on ws2, Brave PID 1003210 on ws1.
- 11:01:01 baseline probe: moz (274, 66), inner (677, 1160).
- 11:01 coordinator nudge to clone1 (commit bdae91a, git only,
  no GUI action).
- 11:06:26 M1: first T1 Ctrl+S goes to Brave, opens a Save dialog
  via xdg-desktop-portal-gtk (window 875x600 at [3003, 1202]).
  Probe 11:06:27 reads moz (274, 66), Zen untouched.
- 11:06:47 M1 remediation: portal window closed with
  hl.dsp.window.close() while focused, no save performed.
- 11:08:03 T1 key, Zen verified focused; probe 11:08:05.
- 11:11:01 pixel run; 11:11:28 post-pixel probe.
- 11:11:56 run 49 of clone2-watch starts (scheduled).
- 11:12:xx run 49 observes ws1 (Zen + clone1 Brave tiled).
- 11:13:xx run 49 switches to ws2. Active window after switch:
  clone2 Chrome 0x5570538ed160.
- 11:13:xx run 49 observes clone2 Chrome (obs 1438114b30ad).
- 11:14:17 M2: T2 Ctrl+Shift+B goes to Chrome (clone2 endpoint,
  ws2). Effect unknown at the time, NOT undone.
- 11:14:18 transient probe read moz (264, 50) while Chrome is the
  active window (ws2 active), 1 second after M2.
- 11:14:36 run 49 returns to ws1. Verified active: Zen
  0x557052b62dd0 ("Welcome! - Zen Browser").
- 11:14:47 stability probe back at (274, 66). Noise series
  11:15:54, 11:16:02, 11:16:10, 11:16:19 all (274, 66).
- 11:16:39 T2 REDO with Zen verified focused (the table result).
- Clone2 commits around the incidents (UTC converted, +07):
  e248a7a 10:55:30 (batch 12 task 3), f49851f 11:01:13 (bench),
  b7c7894 11:09:16 (watchdog log 11:08), 9993e25 11:11:28
  (task 3 fix pass). No clone2 commit at 11:14.
- watchdog-zen-20m 11:12-11:15 run: its logged steps are SSH
  checks only (subagents, GitHub, Zen PID, laptop workers,
  Hyprland PID, coredumpctl, Lauren Tan sweep). No hyprctl
  focus or workspace command appears in any of its steps.

## 2. M2 cause ranking: why focus moved to Chrome/ws2

### Rank 1: clone2-watch run 49 held ws2 with Chrome focused across M2. PROVEN.

Evidence for:
- Run 49 switched to ws2 at 11:13:xx and returned at 11:14:36
  (watch log, run 49). M2 at 11:14:17 falls INSIDE that hold,
  about 1 minute after the switch and 19 seconds before the
  return.
- The watch log records the active window after its switch as
  clone2 Chrome 0x5570538ed160, the same window the keystroke
  hit.
- The MOZ-GROWTH log's own transient read at 11:14:18, one
  second after M2, confirms Chrome was the active window with
  ws2 active at that moment.
- The watch flips to ws2 and holds it on every run; run 49 is
  not an exception. Its hold (switch 11:13:xx to return
  11:14:36, about 90 seconds) matches the established pattern
  of runs 40 to 48.
- The MOZ-GROWTH log records no focus verification with a
  timestamp for the 11:14:17 T2 attempt itself. The last
  recorded Zen-focus verification before M2 was around the
  pixel run (11:11:01) and post-pixel probe (11:11:28), minutes
  before the key. So the verification, if one was done for
  that attempt, was stale by the time the key was sent, and
  the watch flipped the workspace in between. This is the
  exact race the procedure fix in section 7 closes.

Evidence against: none found. No other actor is timed to
11:13:xx-11:14:36 with a workspace switch.

### Rank 2: clone2's own activity pulled focus to its Chrome. WEAK, unproven.

Evidence for: clone2 works in that Chrome window and was
actively working batch 12 (commits 11:09:16 and 11:11:28).
Evidence against: no clone2 commit or recorded action at
11:14; clone2's agents type into the chat, and nothing in
the record shows a clone2-driven focus event at 11:14:17.
The watch's own switch at 11:13:xx already fully explains
Chrome being active. No separate clone2 action is needed,
and none is evidenced. Kept as an alternative only.

### Rank 3: Hyprland focus-follows-mouse or stray pointer. WEAK.

Evidence against: no pointer movement is recorded anywhere;
all workers use command-only focus, no mouse. The watch
switch is a complete explanation. The Hyprland log at
/run/user/1000/hypr/<sig>/hyprland.log was checked
(T+4m): its mtime is Nov 21 23:13, it holds no lines for
11:06 or 11:14 at all, so it neither supports nor refutes
anything here. Recorded as unavailable, not as evidence.

### Rank 4: watchdog-zen-20m. EXCLUDED.

Its 11:12-11:15 run overlaps M2 in time, but its body does
not touch the GUI: SSH checks only, no hyprctl focus or
workspace command in any logged step. Time overlap alone
is not causation.

### M2 verdict

The watch is the cause. Run 49 flipped to ws2 at 11:13:xx,
held it with Chrome focused, and the worker's T2 keystroke
at 11:14:17 landed inside that hold. The worker's focus
check for that attempt was stale (minutes old) or absent;
the log does not timestamp one. This also resolves open
hypothesis H3 in the MOZ-GROWTH log in the affirmative
direction: the transient moz (264, 50) read at 11:14:18
coincides exactly with the watch's ws2 hold, so a
workspace-state-dependent read is the leading explanation
for it. One sample does not prove H3; the deciding test
stays as the MOZ log states it (coordinated read with ws2
active vs ws1 active when clone2 is idle).

## 3. M1 cause ranking: why focus was on Brave

Note first: nothing moved focus TO Brave at 11:06. Focus
was ALREADY on Brave, and had been since at least 11:00:41
(the MOZ pre-state) and since run 48's return at 10:59:19.
M1 is a failure to move focus away, not a fresh move.

### Rank 1 (primary, worker-side): keystroke sent after a failed focus command, with no successful verification. PROVEN.

Evidence: the MOZ-GROWTH log section 4 states it directly.
The first T1 attempt used the broken string form (hyprctl
dispatch focuswindow address:...) which errored, so focus
stayed on Brave and the Ctrl+S went to Brave. The worker
sent the key after the focus step failed instead of
stopping. The probe at 11:06:27 (moz (274, 66), unchanged)
confirms Zen was untouched and the key went elsewhere.

### Rank 2 (background condition): Brave was the last-focused ws1 window, left there by watch run 48's return. PROVEN as the condition.

Evidence for:
- Run 48 returned to ws1 at 10:59:19 and verified the active
  window as clone1 Brave 0x55705383d420, not Zen.
- The MOZ pre-state at 11:00:41 confirms Brave still active
  82 seconds later. Nothing between 10:59:19 and 11:06:26
  moved focus to Zen: the baseline probe (11:01:01) reads
  over CDP and the grim screenshot (11:02) change no focus.
- Mechanism, confirmed by three data points: returning to
  ws1 by workspace-focus restores the LAST-FOCUSED window on
  that workspace. Run 47 return: Brave active. Run 48
  return: Brave active. Run 49 return: Zen active, after the
  MOZ worker itself had focused Zen repeatedly (T1 11:08,
  pixel run 11:11), making Zen the last-focused ws1 window.
  The pattern fits the last-focused-window rule exactly,
  with no exceptions in runs 47 to 49.
- Clone1 kept Brave as the last-focused ws1 window: it was
  actively working batch 10 in Brave (commit 81ea6e0 10:57,
  3 subagents dispatched), so Brave was the window in use
  on ws1 when run 48 returned.

Evidence against: none. Run 48's switch to ws2 ended at
10:59:19, 7 minutes before M1, so run 48 is the background
condition, not the trigger. The trigger is rank 1.

### Rank 3: clone1 activity re-focusing Brave. CONTRIBUTING, not the trigger.

Clone1 was actively working in Brave on ws1 (batch 10).
That activity kept Brave the last-focused window and could
re-focus it at any time, but no clone1 action is timed to
11:06:26, and no fresh move was needed: Brave was already
focused. Contributing condition only.

### Excluded for M1

- clone2-watch run 48: returned 10:59:19, 7 minutes before
  M1; sets the condition, does not act at 11:06.
- watchdog-zen-20m: no GUI action in its body (see
  section 1).
- Owner input: owner asleep since 06:52, no input.
- Clone2/Chrome: on ws2, cannot explain Brave focus on ws1.

### M1 verdict

Worker-side error as the trigger (key sent after a failed
focus command, no verification), on top of a background
condition the worker did not check (Brave already focused,
left there by run 48's workspace-focus return plus clone1's
ongoing Brave work). The focus move itself is explained:
there was no move at 11:06. The move that failed to happen
was the worker's own move to Zen.

## 4. Chrome bookmarks bar: current state and pre-M2 state

Commands run live on the laptop (T+2m to T+4m, 11:30-11:31 +07):

- Process: `ps -o args= -p 8059` returns
  /usr/lib/chromium/chromium --ozone-platform=wayland ...
  --remote-debugging-port=9223 --profile-directory=Default
  --app-id=hichoggbhebpgpgcbcgfpkjmohpcflhh
  (checked 11:31 +07). The clone2 Chrome window is an APP
  window (a site installed as an app), not a normal browser
  window. App windows have no tab strip, no address bar, and
  no bookmarks bar UI.
- Preferences: ~/.config/chromium/Default/Preferences, read
  11:30 +07. No "bookmark_bar" key present; 0 occurrences
  of "show_on_all_tabs" in the file. File mtime 11:29:39,
  so it is written live; a persisted toggle would be
  present. The one "bookmarks":false hit is inside a sync
  datatype list, unrelated to the bar.
- Watch screenshots cannot establish the pre-M2 state. The
  run 47, 48 and 50 ws2 captures are all 1280x812 crops of
  the page content (checked with PIL on the VM, T+3m); they
  show only the Muse web app, never Chrome's own top chrome.
  The full window is 901x1176 per the watch log (and 1853
  wide at 11:29:28, see section 8), so the captures are
  crops, not the whole window. No screenshot in the record
  shows the bookmarks bar region before M2.
- VISUAL, completed 11:43:45 +07 (T+15m): full-screen grim
  taken during the run 51 ws2 hold, read-only, no workspace
  flip by me. Active workspace 2, active window Chrome
  0x5570538ed160, [2514, 914] [1853, 1176]. The capture
  (/tmp/c5focus-ws2-full.png on the laptop, small copy
  ~/workspace/c5focus-ws2-full.jpg) shows the Muse web app
  starting at the very top edge of the window: NO tab strip,
  NO address bar, NO bookmarks bar row anywhere. The window
  renders no browser chrome at all in which a bar could
  appear. Current state, by direct visual evidence: no
  bookmarks bar shown.

Pre-M2 state, stated plainly: NOT directly evidenced by
any screenshot or file in the record, and it cannot be
recovered from one, because no pre-M2 capture shows the
bar region. What can be said is structural, not a guess
about a screenshot: this window is an app window and
renders no browser chrome, so its visible state before
M2 was necessarily the same as now, no bar shown. The
only thing a toggle could have changed is the pref, and
the pref key is absent from a live-written Preferences
file. So the M2 keystroke changed nothing visible and
nothing persisted. The disposition in section 5 does not
depend on recovering a pre-M2 screenshot, because there
is no bar to restore in either state.

## 5. M2 disposition: LEAVE AS IS, no keystroke

Decision: do NOT undo the toggle. No restoration keystroke
is warranted, and sending one would be the wrong move.

Reasons:
- The target is an app window with no bookmarks bar UI.
  There is nothing visible to restore in either toggle
  state.
- The Preferences file shows no persisted toggle (no
  bookmark_bar key, 0 occurrences of show_on_all_tabs).
  There is no persisted state to revert.
- Sending Ctrl+Shift+B into Chrome now would not be an
  undo: if the original keystroke was a no-op (as all
  evidence indicates), a new keystroke would be the FIRST
  live toggle attempt, and could CREATE a change rather
  than remove one. The safe action is no action.
- The effect, if any, is cosmetic and confined to clone2's
  own app window. Clone2 has continued working batch 12
  normally since (commits 11:09:16, 11:11:28, and later),
  with no report of a UI problem.

Safe procedure if the coordinator ever wants it verified
anyway: wait for a clone2-watch ws2 hold (runs start
:11:56, :26:56, :41:56, :56:56, hold about start+1m to
start+2m40s), take a full-screen grim during the hold
(read-only, no focus change), and compare the top of the
Chrome window against this log's capture. Do NOT send
Ctrl+Shift+B to test it. A keystroke whose target window
was not verified in the same minute is exactly how M2
happened.

## 6. M1 assessment: no file was saved

Assessment: NO SAVE occurred. Corroborated by two
independent checks plus the worker's own account.

- Worker account (MOZ log section 4): the portal window
  was closed with hl.dsp.window.close() at 11:06:47 while
  focused, no save performed, and the portal is gone from
  the client list. Closing the dialog performs no write by
  construction.
- Downloads check (T+2m, 11:30 +07): `ls -lt ~/Downloads`
  shows the newest file Nov 21 16:16; `find ~/Downloads
  -newermt "2026-11-22 11:05:00" ! -newermt
  "2026-11-22 11:08:00"` returns nothing. No file was
  written to the Save dialog's default location in the M1
  window.
- Wider check (same call): find across the laptop home,
  maxdepth 3, same 11:05 to 11:08 window, excluding
  .cache and .config, returns only a gvfs-metadata entry
  (system metadata, not a saved page). No saved page
  anywhere in the searched paths.
- Residual caveat, stated plainly: a save to a
  non-default location outside the searched paths cannot
  be excluded by file listing alone. But the dialog was
  closed, not saved, so no write was requested in the
  first place. The no-save conclusion rests on the close
  action, with the file checks as corroboration.

## 7. Procedure fix: rule for every future live-machine worker

RULE (concrete, not advice): verify the active window in
the SAME SSH call, immediately before the keystroke batch,
and re-verify after ANY gap longer than 60 seconds or ANY
intervening command that is not the keystroke itself. A
focus check from an earlier call is stale the moment the
call ends, because the clone2-watch flips to ws2 every 15
minutes and holds it about 90 seconds, and clone1's Brave
work can re-focus ws1 at any time.

Exact commands (GUI env on every call):

export HYPRLAND_INSTANCE_SIGNATURE=$(ls /run/user/1000/hypr/ | head -n1)
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-1 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus

Focus (working form ONLY, proven in the MOZ-GROWTH task):
hyprctl dispatch 'hl.dsp.focus({ window = "address:0x557052b62dd0" })'
then in the SAME call:
hyprctl -j activewindow
The output must show address 0x557052b62dd0, workspace 1,
before any key is sent. Then send the keys with wtype in
that same call.

NEVER use the string form:
hyprctl dispatch focuswindow address:...
It errors on Hyprland 0.57.2 (Lua parse error) and leaves
focus wherever it was. That exact failure is M1. If the
focus command errors, STOP. Do not send the key.

If activewindow is not the intended window, STOP. Do not
send the key. Re-focus, re-verify, then send, still in one
call.

Scheduling note: the clone2-watch runs start at :11:56,
:26:56, :41:56, :56:56 and hold ws2 roughly start+1m to
start+2m40s. Prefer keystroke batches outside those
windows, but NEVER rely on the schedule instead of the
same-call verification. The watch is the known
interference; an unknown one can flip focus at any other
time.

After a misdirected keystroke: stop the batch at once,
record the time and the activewindow output, remediate
(close the dialog, do not save, do not send more keys
into the wrong window), re-verify focus in a fresh call,
and only then continue. That is what the MOZ worker did
for M1; for M2 the correct call was to flag it and redo
from a verified state, which is what it did at 11:16:39.

## 8. Incidental observations (not my task, flagged for the coordinator)

- Full-screen grim 11:30 +07 (1920x1200, /tmp/c5focus-chrome-full.jpg
  on the laptop, small copy ~/workspace/c5focus-chrome-full.jpg):
  it caught ws1 AFTER run 50 returned, so it shows Zen tiled
  left and clone1 Brave tiled right, not Chrome. It is NOT the
  ws2 visual; the run 51 capture in section 4 is the one that
  counts. Incidental: clone1 Brave shows 2 pending "Needs
  review" approval cards (web access for scheduled tasks: an
  IRS form download and the Wikipedia Main Page). Run 50
  presumably saw them; flagged here in case it did not. No
  action taken by me.
- Chrome window geometry at 11:29:28 +07: at [2514, 914],
  size [1853, 1176], ws2, 1 window. The 901-wide figure in
  the watch log is the observe capture width, not the live
  window size. Not an incident, a measurement note.
- Hyprland log unavailable as evidence: mtime Nov 21 23:13,
  no lines for 11:06 or 11:14. See section 2 rank 3.

## 9. Evidence index

- MOZ-GROWTH log: improvements/worker-click5-moz-growth-log.md,
  commit a42ef12, section 4 (M1 11:06:26, M2 11:14:17,
  transient 11:14:18).
- clone2-watch log: hidden_files/clone2-watch-log.md, runs 47
  (10:41:56), 48 (10:56:56, return 10:59:19 Brave active),
  49 (11:11:56, switch 11:13:xx, return 11:14:36 Zen active).
- watchdog-zen-20m log: hidden_files/watchdog-log.md,
  11:12-11:15 +07 entry (SSH checks only, no GUI action).
- Laptop live checks (SSH only, ~/workspace/ssh-laptop.sh):
  activewindow/activeworkspace 11:29:28 (Chrome 0x5570538ed160,
  ws2, [2514, 914] [1853, 1176]); `ps -o args= -p 8059`
  (--app-id=hichoggbhebpgpgcbcgfpkjmohpcflhh) 11:31;
  Preferences read 11:30 (no bookmark_bar key, 0
  show_on_all_tabs, mtime 11:29:39); Downloads find
  11:05-11:08 empty 11:30; full-screen grim 11:30
  (1920x1200, ws1 after run 50 return); full-screen grim
  11:43:45 during run 51 ws2 hold (1920x1200, ws2 active,
  Chrome 0x5570538ed160 [1853, 1176], no tab strip, no
  address bar, no bookmarks bar; /tmp/c5focus-ws2-full.png,
  small copy ~/workspace/c5focus-ws2-full.jpg).
- VM checks: run 47/48/50 ws2 captures all 1280x812 (PIL,
  11:31 +07), so crops, not full-window evidence.
- Clone2 commits (origin/main): e248a7a 10:55:30, f49851f
  11:01:13, b7c7894 11:09:16, 9993e25 11:11:28. No commit
  at 11:14. Clone1 commit 81ea6e0 10:57 (batch 10, 3
  subagents).
- Repo state for this log: branch todolist-push, HEAD
  6aa911b at log time. No code changed. No keystroke sent
  by me at any point in this task. No unplanned stall; the
  10-minute wait for the run 51 ws2 hold was planned, with
  this log drafted during it.
