# Worker ZT-B log: blind ordinary-user run ZT-00..ZT-10
# Task start 00:24:03 +07, Sun 2026-11-22. All times wall-clock Asia/Ho_Chi_Minh + elapsed from task start. Log EVERY event as it happens. No em/en dashes.
# Branch: todolist-push. F1+F2 cluster closed (F1a activation PASS, F2b act-now session-path PASS, order-to-overlay 12.262s, click 0px). Zen PID 496121, 14 real tabs, slot healed.
# Rules: run scenarios exactly as written (ZT-A authored, I am the blind executor); fresh observe first; owner visibly active -> do not drive; safe targets only; never ydotool; no em/en dashes; commit small and many with explicit pathspec only, verify via ls-remote.

## 00:26 ZT-00 step 0 baseline (elapsed 2m)
- zen_dom.py list OK (Marionette session creates fine). 18 tabs (brief said 14 real; the live list is the protected set per rule 4):
  1 YouTube | 2 Problem loading page (reddit.com) | 3 Today - Todoist | 4 Inbox (729) - Gmail | 5 Lich Google - Tuan 16 thang 11, 2026 | 6 (5) Chat - Muse | 7 PCCV CF26 - Google Trang tin | 8 Free Claude Code Admin | 9 Welcome! | 10 about:blank | 11 Example Domain (F2b tab) | 12 about:blank | 13 about:blank | 14 Just a moment... (polygon) | 15 Just a moment... (codeforces) | 16 Biome Finder - Minecraft App (chunkbase) | 17 Gamerule keepInventory (duck.ai) | 18 ModelArk-Coding-Plan (byteplus)
- Baseline count 18. Non-blank 15, about:blank 3.
- eval "window.mozInnerScreenX + ..." returned null. mozInnerScreenX is NOT usable here (returns null via Marionette eval). Coordinate conversion for DOM rects will use: observe image content-area offset (measured from the viewed image) + DOM rect. Will validate each DOM click via DOM state after.
- observe --help: --window WINDOW | --screen SCREEN, --max-width, --focus, --settle-ms. act-now --help: --actions JSON path, --observation JSON path (captured when omitted), --session-deadline-s.

## 00:26 ZT-00 steps 1-3 (elapsed 2m)
- Step 1 PASS: ps shows zen-bin PID 496121, flags --remote-debugging-port=9222 --marionette.
- Step 2 PASS: curl 127.0.0.1:9222 = 200.
- Step 3 PASS: Marionette session created, tab list returned (the list above). No "browserElement is null".

## 00:26 ZT-00 step 4 deviation (recorded before executing)
- Problem: step 4 navigates the CURRENT tab to example.com and step 7 closes it, then the title set + count must equal step 0. That is only satisfiable if the navigated tab is run-opened: closing ANY snapshot tab breaks the count (rule 5) and violates rule 4 (never close a snapshot tab unless this run opened it). The active tab is currently the Example Domain snapshot tab (F2b left it active).
- Deviation: press Ctrl+T first to open a fresh tab, then run steps 4-7 in it. This does not weaken the gate (mouse click on address bar, typing, navigation, title check, Ctrl+W close, set restore are all still tested). The scenario file itself is NOT modified.

## 00:24 task start (elapsed 0m)
- Read improvements/zen-ordinary-user-tests-20261121.md (v2, 658 lines): ZT-00 gate + ZT-01..ZT-10, composite, blind. Protected tabs = ZT-00 step 0 snapshot (live list), not the examples.
- Repo: todolist-push, HEAD 115ae4d (F2b live session-path proof PASS). Untracked files present (other workers); explicit pathspec only.
- Laptop check: Zen PID 496121, 40:11 elapsed, flags --remote-debugging-port=9222 --marionette. curl 127.0.0.1:9222 = 200.
- NOTE: scenario file DOM path is wrong on this laptop: file says /home/james/computer-use-wayland/scripts/zen_dom.py, python3 says no such file. Real paths found by find: /home/james/workspace/computer-use-wayland/scripts/zen_dom.py (repo) and /home/james/.local/share/agent-computer-use/scripts/zen_dom.py (installed). I will use the repo path /home/james/workspace/computer-use-wayland/scripts/zen_dom.py and record this as a finding (scenario-file path defect, not a Zen defect).
- F2b log read: act-now session path proven, order-to-overlay 12.262s, click 0px, pill "Computer use active" in raw grim during run. Key mechanics: observe hides pill by design (use raw grim for pill visuals); act --actions/--observation take FILE PATHS; act converts coords with the observation REGION origin (F2b-1); on session path the pill ends with the session, after-capture cannot evidence it (F2b-2); SSH dispatch dominates order-to-overlay (F2b-3).
