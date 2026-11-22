# Worker C5-MOZ-GROWTH log: why did Zen's mozInnerScreen grow

Role: live investigation on the laptop. Find out WHY Zen's
mozInnerScreen grew, which is what wedged the items 5-6 origin
re-read. Independent from C5-ITEMS56, which pinned the failure to
the dimension closure check. No code changes in this task. Report
to the COORD-CLICK-5 coordinator only, never message the user.
Owner asleep since 06:52 with a headache; Muse holds full authority.

Standing rules: wall-clock Asia/Ho_Chi_Minh plus elapsed time on
every log entry. No em dash (U+2014) or en dash (U+2013) anywhere.
No personal info on GitHub. Commit with explicit pathspec only,
immediately after staging, never plain git commit, never git add -A.
Verify every push with git ls-remote. Never ydotool.

Task start: 2026-11-22 10:59:59 +07 (T+0m). Task end: 11:25:24 +07.
Total elapsed about 25 minutes.

## 0. Primary source read (T+0m to T+2m)

- C5-ITEMS56 log, read in full:
  improvements/worker-click5-items56-log.md on todolist-push,
  commit 2942f68. Its live diagnostic (10:55:04 to 10:55:08 +07)
  reproduced the Codex items 5-6 FAIL deterministically:
  ZenSession.viewport_origin raises ZenDomError, "dimension closure
  fails: mozInner [274, 66] + inner [677, 1160] exceeds window size
  [925, 1176] (gaps -26, -50)". The C12 probe (03:36, same window
  address 0x557052b62dd0, 1863 wide) measured moz (240, 8), inner
  (1615, 1160), gaps +8/+8, PASS. Since then the window narrowed
  1863 to 925 (innerWidth tracked exactly: 1615 - 938 = 677) but
  moz grew +34/+58. Which Zen UI element grew the chrome was NOT
  identified.
- ITEMS56 probe script, reused verbatim for geometry reads:
  ~/workspace/c5-items56-probe.py, SHA-256
  8eb04d1ef24d1bfe6c850a624b5a82d817ab5f025d052a50214d85795ff0b29a,
  laptop copy /tmp/click5-items56-probe.py, SHA verified identical.

## 1. Pre-state (T+1m to T+5m)

Window, verified live 11:00:41 +07 (hyprctl -j clients):
address 0x557052b62dd0, origin [2509, 914], size [925, 1176],
monitor_box [2464, 902, 1920, 1200], workspace 1, PID 496121.
Active window then: Brave (ws1). Chromium PID 8059 on ws2, Brave
PID 1003210 on ws1. Same geometry as ITEMS56 and the Codex run.

Baseline geometry read, ITEMS56 probe, finished 11:01:01 +07:
moz [274, 66], inner [677, 1160], outer [925, 1176],
devicePixelRatio 1, screenPixelsPerCSSPixel null, zoom 1,
scale factor 1. Verdict FAIL (closure gaps -26/-50), same numbers
as ITEMS56. Scratch removed, original tab restored, session closed.

UI states in the pre-state, from the grim screenshot
/tmp/c5-moz-pre.png (taken 11:02, Zen window region), OCR of it,
prefs.js, and xulstore.json:
- Sidebar EXPANDED, vertical tabs visible, width 240px
  (xulstore navigator-toolbox width 240px, --zen-sidebar-width
  240px). Tab list (OCR): Welcome!, PCCV CF26, ModelArk-Coding-
  Plan, Example Domain, New Tab, New Tab, Just a moment..,
  Biome Finder, Gamerule keepinventory. The sidebar shows TABS,
  not a bookmarks panel; xulstore sidebar-title "Bookmarks" is
  stale (last-used panel, not the live one).
- Compact mode OFF: sidebar expanded; pref
  zen.view.compact.enable-at-startup false.
- Bookmarks toolbar: not visibly present; no toolbar row in the
  screenshot outside the page content.
- Top chrome: an 8px window border only. Row brightness profile
  of the content area (x 300 to 900): distinct lighter band y=0
  to 7 (mean 38.7), flat dark y=8 to 23, a busy band y=33 to 46
  which is the Welcome page's own header text, not chrome, then
  flat page background from y=56. Column profile at y=100:
  sidebar content x=8 to about 236, flat page background from
  x=240. So the VISIBLE page starts at about (240, 8) in window
  coords, while Firefox reports moz (274, 66).
- Active tab: Welcome, https://zen-browser.app/welcome/, title
  "Welcome! - Zen Browser".
- No side panel open, no find bar, no split view (see section 6,
  split test).
- Prefs of note: sidebar.visibility "hide-launcher";
  zen.tabs.show-newtab-vertical false. customKeys.json remaps
  only key_openAddons, key_newNavigatorTab, key_newNavigator;
  no Ctrl+S remap, so Ctrl+S is the stock sidebar toggle here.

## 2. Method notes (how keys were sent)

- SSH only via ~/workspace/ssh-laptop.sh. GUI env on every call:
  XDG_RUNTIME_DIR=/run/user/1000, WAYLAND_DISPLAY=wayland-1,
  DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus,
  HYPRLAND_INSTANCE_SIGNATURE from /run/user/1000/hypr/.
- Focus: the string-dispatcher form is broken on Hyprland 0.57.2
  (Lua parse error, same as the 2026-11-17 lesson). The working
  form, proven in this task, is:
  hyprctl dispatch 'hl.dsp.focus({ window = "address:0x..." })'.
  Candidates that failed: hl.dsp.window.focus (nil field),
  hl.dsp.focuswindow (nil field), hl.dsp.focus({ address = ... })
  (unrecognized arguments). Focus was verified with
  hyprctl -j activewindow in the same call, immediately before
  each keystroke.
- Keys: wtype (virtual keyboard, NOT ydotool). Ctrl+S is
  wtype -M ctrl -P s -p s -m ctrl. Ctrl+Shift+B adds -M shift.
  Ctrl+Alt+C adds -M alt.
- Geometry reads: the ITEMS56 probe script, which creates scratch
  fields on the pre-existing about:blank tab (index 9), reads
  last_display_metrics even on failure, then removes the scratch
  and restores the original tab. No tab opened or closed, no
  window resized, no click, no message sent.
- Screenshots: grim -g '2509,914 925x1176'. Pixel analysis with
  PIL on the laptop (row/column brightness profiles, white-pixel
  bounding boxes). Small copies transferred to the VM for viewing
  by base64 in one chunk each, decoded and verified with PIL.

## 3. Toggle table

All rows: before and after numbers are (moz, inner, outer).
Window size stayed [925, 1176] in every row. moz y stayed 66 in
every row. "Restored" means a second toggle returned the exact
baseline numbers, verified by a probe read.

- T1 sidebar Ctrl+S, key 11:08:03 +07, probe 11:08:05:
  before (274, 66), (677, 1160) -> after (53, 66), (909, 1160).
  moz x -221, inner width +232, moz y unchanged. Restored
  11:08:17, probe 11:08:18: (274, 66), (677, 1160). Restored yes.
- T2 bookmarks toolbar Ctrl+Shift+B, REDO key 11:16:39, probe
  11:16:40: before (274, 66), (677, 1160) -> after (274, 66),
  (677, 1160). No change. Screenshot diff vs pre-state: 2423
  strongly-changed pixels scattered over 196 rows, no toolbar
  band appeared or disappeared. Restored (toggle back) 11:16:52,
  probe 11:16:53: (274, 66). Restored yes (state never left).
- T3 compact mode Ctrl+Alt+C, key 11:17:12, probe 11:17:13:
  before (274, 66), (677, 1160) -> after (274, 66), (677, 1160).
  No change. Screenshot diff vs pre-state: same scattered-noise
  pattern (2262 strong pixels), no visual change. The shortcut
  appears unbound or a no-op in this Zen; compact mode was not
  toggled by it, so no restore toggle was sent (state unchanged).
- T4 sidebar Ctrl+S (repeat of T1), key 11:17:25: before
  (274, 66), (677, 1160) -> after (53, 66), (909, 1160).
  Reproduces T1 exactly. Restored 11:19:32, probe 11:19:33:
  (274, 66). Restored yes.
- T5 sidebar Ctrl+S, key 11:20:05: before (274, 66),
  (677, 1160) -> after (53, 66), (909, 1160). See the bookkeeping
  note in section 4: this collapse was NOT restored until T6.
- T6 sidebar Ctrl+S, key 11:22:56: before (53, 66), (909, 1160)
  (still collapsed from T5) -> after (274, 66), (677, 1160).
  This toggle was an EXPAND, not a collapse. Clip probe run in
  this state (section 5) confirmed the expanded state
  (inner 677, moz (274, 66)). State after T6 equals the pre-state.
- T7 sidebar Ctrl+S, key 11:23:26: before (274, 66), (677, 1160)
  -> after (53, 66), (909, 1160). Restored 11:24:22, probe
  11:24:23: (274, 66), (677, 1160). Restored yes.

No toggle moved moz toward the C12 values (240, 8). The sidebar
toggle moves moz x between 274 and 53 but never to 240, and it
never moves moz y off 66. The bookmarks toolbar and the
compact-mode shortcut do not move moz at all.

## 4. Incidents and bookkeeping (read before trusting the table)

- M1, misdirected keystroke, 11:06:26: the first T1 attempt used
  the broken string form (hyprctl dispatch focuswindow
  address:...) which errored, so focus stayed on Brave and the
  Ctrl+S went to Brave. It opened a Save dialog via
  xdg-desktop-portal-gtk (window 875x600 at [3003, 1202]).
  Remediation: the portal window was closed with
  hyprctl dispatch 'hl.dsp.window.close()' while it was focused
  (11:06:47), no save performed; verified the portal is gone from
  the client list and focus is back on Brave. Zen untouched: the
  probe at 11:06:27 read moz (274, 66), unchanged.
- M2, misdirected keystroke, 11:14:17: focus had moved to Chrome
  (clone2 endpoint, ws2) without my input, and the T2
  Ctrl+Shift+B went to Chrome (in Chrome it toggles the bookmarks
  bar). Its effect on Chrome's UI state is unknown and was NOT
  undone: undoing it would need more keystrokes into clone2's
  browser, which the task forbids. Flagged here for the
  coordinator. The T2 result in the table is from the REDO at
  11:16:39 with Zen verified focused, not from the 11:14:17
  attempt. Focus bounces between ws1/Zen and ws2/Chrome on its
  own while clone2 works; every toggle in the table verified Zen
  focused in the same call before sending its key.
- Transient read, 11:14:18: one probe read moz (264, 50) while
  Chrome was the active window (ws2 active), 1 second after M2.
  The next read (11:14:47, Zen focused) was back at (274, 66),
  and a 4-read noise series (11:15:54, 11:16:02, 11:16:10,
  11:16:19) all read (274, 66). The (264, 50) value was a single
  transient, not reproduced; see open hypothesis H3.
- Toggle bookkeeping slip: T5 (11:20:05) collapsed the sidebar
  and I did not restore it before moving to screenshot analysis.
  T6 (11:22:56) therefore EXPANDED it back. The slip was caught
  because the T6 clip probe read inner 677 and moz (274, 66).
  T7 then did a clean collapse/restore pair. No harm: the final
  state was verified to equal the pre-state (section 7).

## 5. Pixel proof: the true viewport origin is (240, 8)

The decisive instrument: a white scratch host div
(position:fixed, left:8px, top:8px, 428x104 CSS px) on the
about:blank tab, photographed with grim, so the host's screen
position minus (8, 8) IS the true viewport origin in window
coords. Script: ~/workspace/c5-moz-pixel.py, SHA-256
7e30f8c5c6708dde678f9fc4fd2f33b138d6b07c8d94869f0ba521aab36e1e31,
laptop copy /tmp/c5-moz-pixel.py, SHA verified identical.

- Expanded state, run 11:11:01 to 11:11:02 +07: solid white
  block x 248 to 675, y 16 to 119 (428 by 104 px, exactly the
  host size). True origin = (248 - 8, 16 - 8) = (240, 8).
  Firefox reports moz (274, 66). Offset = (+34, +58).
  Cross-check: (240, 8) plus inner (677, 1160) gives gaps
  925 - 677 - 240 = +8 and 1176 - 1160 - 8 = +8, exactly the C12
  gaps. The viewport SIZE matches the old chrome; only the
  REPORTED position is offset. The viewport did not move; moz
  reports it 34px right and 58px down from where it renders.
  (The about:blank page itself renders dark, a Zen dark gradient,
  so the host is the only white object; the scattered white
  pixels elsewhere are sidebar icons.)
- Collapsed state, runs 11:17:36 and 11:20:08 (2s settle on the
  second): the host's left edge is still solid at x=244 and its
  top at y=16, giving a true origin of (236, 8). BUT the host
  renders only 200px wide (white x 244 to 443, y 16 to 119),
  not its CSS 428px. The CSS rects in that state are normal
  (host (8, 8, 428, 104), input (12, 12, 420, 28), inner
  (909, 1160), scroll (0, 0)), the ancestor chain has no
  transform and no clipping ancestor (all overflow visible), and
  elementFromPoint(500, 60) returns HTML while (100, 60) and
  (300, 60) return the textarea, so the layout says the host
  spans CSS x 8 to 436 while the paint shows white only to
  window x=443. The mapping is consistent with a horizontal
  paint scale of about 0.465 (199 / 428) with vertical scale 1,
  or equivalently a clip at window x=443. Cause unknown; see
  open hypothesis H2. The left/top edges are solid, so the
  collapsed true origin (236, 8) is still read off the left
  edge, but it carries this caveat.
- Consequence for the sidebar question: collapsing the sidebar
  moves the TRUE origin only 240 to 236 (-4), while moz moves
  274 to 53 (-221). moz does not track the true origin.

## 6. Split-view test: no split view (expanded state)

Script: ~/workspace/c5-moz-split.py, SHA-256
c79e6eb4f6ebb1140bdb3d837a7f1746d370fe2cdc14a44c0975b0e166fce7f3,
laptop copy identical. Run 11:24:49 to 11:24:50 +07, expanded
state: host created on the scratch tab, switched back to the
Welcome tab (https://zen-browser.app/welcome/), screenshot
after 1s. White pixels in the host's expected region
(window x 244 to 675, y 16 to 119): 291 of 44928 (0.6%).
The host is NOT visible while the Welcome tab is active, so
only one tab renders at a time. No split view in the expanded
state. (Not re-tested in the collapsed state; see H2.)

## 7. Final state and verdict

Final verification 11:25:23 to 11:25:24 +07: focus restored to
Brave (0x55705383d420), ws1 active. Zen window unchanged at
[2509, 914] [925, 1176]. Final probe: moz [274, 66], inner
[677, 1160], outer [925, 1176], identical to the 11:01:01
baseline. Scratch removed, original tab restored, session
closed. No tab opened or closed, no window resized, no chat
thread, Brave, or Chromium endpoint touched except the two
misdirected keystrokes recorded in section 4 (M1 remediated,
M2 flagged).

### Verdict: NO UI element accounts for moz +34/+58

- The sidebar (Ctrl+S) moves moz x between 274 and 53, but the
  true viewport origin barely moves (240 to 236), and moz y
  never leaves 66. The sidebar explains the difference between
  its own two states, not the +34 growth vs C12.
- The bookmarks toolbar (Ctrl+Shift+B) does not move moz and
  produces no visible change.
- Compact mode via Ctrl+Alt+C does not move moz and produces no
  visible change (shortcut appears unbound or a no-op here).
- The +58 in y is untouched by every toggle, and there is no
  visible top chrome beyond the 8px window border (section 1).
- The pixel proof shows the viewport itself is at (240, 8) with
  +8/+8 gaps, exactly as in C12. What grew is not the chrome;
  it is Firefox's REPORTED mozInnerScreen, offset (+34, +58)
  from the true origin. The validator's closure model
  (moz + inner <= window size) is false for this Zen state
  because moz itself is displaced, not because the viewport
  moved or overflowed. The fix must not trust moz blindly: the
  pixel-proven origin (240, 8) passes closure with +8/+8, so a
  fix that verifies the origin against an independent instrument
  (screenshot pixel edges, as done here) instead of refusing on
  moz alone is the shape ITEMS56 section 7 already points to.

### Open hypotheses with deciding tests

- H1: the moz reporting offset is tied to the narrowed window
  (1863 to 925). The offset appeared when the window narrowed;
  no toggle removes it. Deciding test: widen the Zen window back
  toward 1863 and re-read moz (coordinator decision required;
  this task forbade resizing, so it was not done). If moz returns
  to (240, 8), the offset is width dependent. If it stays
  (274, 66), the offset is a persistent state independent of
  width.
- H2: collapsed-state host paint clip at window x=443 (host
  renders 200 of its 428 CSS px wide, about 0.465 horizontal
  scale, vertical scale 1; layout normal, no transform, no
  clipping ancestor). Deciding test: repeat the split test in
  the COLLAPSED state (host on scratch tab, Welcome tab active,
  screenshot: if the host shows in a left pane while Welcome is
  active, a collapsed-only split exists; if not, the clip is a
  paint quirk). Also re-run the collapsed pixel test with a 5s
  settle and a full-res screenshot.
- H3: the single transient read moz (264, 50) at 11:14:18 while
  ws2/Chrome was active. Deciding test: read moz with ws2 active
  vs ws1 active in a coordinated window when clone2 is idle. If
  it reproduces only with ws2 active, the read is
  workspace-state dependent; if it never reproduces, it was a
  one-off layout transient (possibly the M2 keystroke landing
  during a focus bounce).

## 8. Evidence index

- Geometry reads: ITEMS56 probe, SHA-256
  8eb04d1ef24d1bfe6c850a624b5a82d817ab5f025d052a50214d85795ff0b29a.
  Baseline 11:01:01, T1 11:08:05, T1 restore 11:08:18, pixel
  11:11:01, post-pixel 11:11:28, T2 transient 11:14:18,
  stability 11:14:47, noise series 11:15:54 to 11:16:19 (4 reads),
  T2 redo 11:16:40, T2 restore 11:16:53, T3 11:17:13, T4
  11:17:25, T4 restore 11:19:33, T5 11:20:05, T6 11:22:56,
  T7 11:23:26, T7 restore 11:24:22, final 11:25:24.
- Pixel scripts (VM and laptop copies, SHAs verified identical):
  c5-moz-pixel.py
  7e30f8c5c6708dde678f9fc4fd2f33b138d6b07c8d94869f0ba521aab36e1e31,
  c5-moz-clip.py
  687c79b78ad8e50c3d7f288318a32fb2766599bbd17d0614d27ca6d32940285d,
  c5-moz-split.py
  c79e6eb4f6ebb1140bdb3d837a7f1746d370fe2cdc14a44c0975b0e166fce7f3.
  Laptop scripts at /tmp/c5-moz-pixel.py, /tmp/c5-moz-clip.py,
  /tmp/c5-moz-split.py. Probe JSONs on the laptop at /tmp/c5-t1.json,
  /tmp/c5-t1-restore.json, /tmp/c5-t2.json,
  /tmp/c5-t2-stability.json, /tmp/c5-noise1.json to
  /tmp/c5-noise4.json, /tmp/c5-t2-redo.json,
  /tmp/c5-t2-restore.json, /tmp/c5-t3.json, /tmp/c5-t4.json,
  /tmp/c5-t4-restore.json, /tmp/c5-pixel2.json,
  /tmp/c5-clip.json, /tmp/c5-clip2.json, /tmp/c5-t7.json,
  /tmp/c5-t7-restore.json, /tmp/c5-final.json.
- Screenshots: laptop /tmp/c5-moz-pre.png (pre-state),
  /tmp/c5-t1-after.png, /tmp/c5-t2-after.png,
  /tmp/c5-t3-after.png, /tmp/c5-moz-pixel.png (collapsed pixel
  run, overwritten twice), /tmp/c5-moz-split.png. VM small
  copies: ~/workspace/c5-moz-pre-small.jpg,
  ~/workspace/c5-top.jpg, ~/workspace/c5-pixel-small.jpg,
  ~/workspace/c5-pixel2-small.jpg.
- Repo state for this log: branch todolist-push, HEAD d2da482
  at log time (other workers' uncommitted changes present in
  scripts/ and tests/; this commit touches only this log file).
- No code changed. No retry of the full live-confirm suite. No
  stall over 15 minutes at any point.
