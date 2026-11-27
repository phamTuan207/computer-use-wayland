# R3-L3 Task 56 (owner amendment 2026-11-26 02:18): restore pinned + essentials Zen tabs

Status: owner-ordered amendment, appended as position 56 (after position 55). The original 55 tasks and their freeze are untouched; thu-tu-chay.txt stays frozen, this file + the state file carry position 56. Counted task: closure counts BOTH ways (53/55 original set; 54/56 with this task). Class L (hard). Runner: Muse fresh independent subagent (Codex approved alternative; opencode cannot run, do not assign).

## Origin

Cleanup batch 2 (2026-11-26 02:15:58-02:15:59) closed 24 Zen tabs under the 02:14 hardened order, including the owner's pinned and essentials tabs. Owner decision 02:18: restoration is a new counted task at the end of the run. Do NOT restore anything before position 56.

## Evidence base (parent recovery 02:22 + coordinator extraction)

Pre-cleanup session store: Zen profile sessionstore-backups/recovery.baklz4 (written 02:15, right before cleanup). Preserved copy on the laptop: ~/zen-sessionstore-pre-cleanup-20261126.jsonlz4 (mozLz40 format; pure-python LZ4 block decompressor works). Coordinator VM extraction: ~/workspace/rung3-evidence-staging/zen-sessionstore/closed-tabs-pinned-state.json.

Counts: pre-cleanup (02:15) 78 tabs, 49 pinned, 12 essentials. Post-cleanup (02:16) 54 tabs, 41 pinned, 7 essentials. Closed: 24 tabs = 5 essentials + 3 pinned + 16 normal.

Essentials BEFORE (in order): YouTube, YouTube (2nd copy), Reddit, Todoist Today, Gmail, Google Calendar, GitHub phamTuan207, LeetCode 75, Qwen-Image-2.1-GGUF (HuggingFace), NEU LMS Chapter 5, tinchi.neu.edu.vn, nguoihoc.neu.edu.vn.
Essentials NOW: YouTube, GitHub, LeetCode, Qwen-Image, NEU LMS, tinchi, nguoihoc.

## Tab set to restore (exact)

Recreate as ESSENTIALS, inserted after the first YouTube and before GitHub, in this order:
1. YouTube (2nd copy) - https://www.youtube.com/
2. Reddit - https://www.reddit.com/
3. Todoist Today - https://app.todoist.com/app/today
4. Gmail - https://mail.google.com/mail/u/1/#inbox
5. Google Calendar - https://calendar.google.com/calendar/u/1/r/week

Recreate as PINNED at the head of the pinned section, in this order:
6. PCCV CF26 Google Sheet - https://docs.google.com/spreadsheets/d/1WzUJNuCQlYLAj59-gdIPFFQv2P_d3f2KhEYcGeWhRRY/edit?gid=0#gid=0
7. Free Claude Code Admin - http://127.0.0.1:8082/admin/model_config
8. Welcome - https://zen-browser.app/welcome/

Exact URLs and each tab's zenWorkspace are in the preserved sessionstore file; restore in the same workspace. The 16 closed normal tabs (TodoMVC, licenses, Kiwi, Color Picker, BrowserLeaks, BBC, Chat-Muse, etc.) are NOT restored.

## Steps (frozen task format)

1. Decompress ~/zen-sessionstore-pre-cleanup-20261126.jsonlz4 (mozLz40: 8-byte magic + 4-byte LE uncompressed size + LZ4 block) and extract the 8 tabs above with their URLs, pinned/zenEssential flags, zenWorkspace, and order. Record the extracted list.
2. Open Zen (ws2). Record the current tab list (zen_dom list) as the before state.
3. Recreate the 5 essentials above, inserted after the first YouTube and before GitHub, in order, each marked Essential (and pinned), in the recorded workspace.
4. Recreate the 3 pinned tabs above at the head of the pinned section, in order, each pinned (not essential), in the recorded workspace.
5. Verify with a fresh tab list + a sessionstore read that all 8 tabs exist with correct URLs, pinned flags, zenEssential flags, workspaces, and relative order.
6. Write ~/rung3-chung-cu/R3-056/ket-qua.txt: extracted pre-cleanup list, before list, after list, per-tab URL + pinned + essential + workspace state, and any tab that could not be restored exactly (with reason).
7. Save timestamped screenshot(s) of the sidebar/tab bar showing the restored essentials + pinned in order into ~/rung3-chung-cu/R3-056/.

## Evidence requirements

Files: ket-qua.txt. Screenshots: at least 1 timestamped screenshot of the sidebar/tab bar showing restored essentials/pinned in order. Plus start_time.txt / end_time.txt per lane rules. Class L: leave the restored tabs LIVE after the drive (no reset); coordinator verifies against the live tab list + sessionstore before scoring closes.

## Key (pass criteria)

Pass: all 8 tabs present with exact URLs from the preserved sessionstore, correct pinned/essential flags, correct workspaces, correct insertion order (5 essentials after first YouTube before GitHub; 3 pinned at head of pinned section), verified from tab list + sessionstore, ket-qua.txt complete, screenshot shows the restored order.
Fail: any tab missing, wrong URL, wrong pinned/essential state, wrong workspace, wrong order, or a normal task tab recreated instead.
Scoring: Pair B mechanics (two fresh independent scorers) unless coordinator assigns Pair A; grader never the author. Scored from sealed snapshot + live verification note (Class L score-before-reset; no reset exists for this task).
