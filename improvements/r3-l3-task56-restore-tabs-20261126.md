# R3-L3 Task 56 (owner amendment 2026-11-26 02:18): restore pinned + essentials Zen tabs

Status: owner-ordered amendment, appended as position 56 (after position 55). The original 55 tasks and their freeze are untouched; thu-tu-chay.txt stays frozen, this file + the state file carry position 56. Counted task: closure counts BOTH ways (53/55 original set; 54/56 with this task). Class L (hard). Runner: Muse fresh independent subagent (Codex approved alternative; opencode cannot run, do not assign).

## Origin

Cleanup batch 2 (2026-11-26 02:15:58-02:15:59) closed 24 Zen tabs under the 02:14 hardened order, including the owner's pinned and essentials tabs. Owner decision 02:18: restoration is a new counted task at the end of the run. Do NOT restore anything before position 56.

## Tab set to restore (derived 2026-11-26 from pre-cleanup session store)

Source: Zen profile sessionstore-backups/recovery.baklz4 (modified 02:15, before cleanup), decompressed and extracted by coordinator epoch 8; extraction saved at ~/workspace/rung3-evidence-staging/zen-sessionstore/closed-tabs-pinned-state.json (VM). Cross-checked against the 02:08 WebDriver tab list (25 tabs, zen-tabs-0208.json) and the batch-2 closure log (zen-cleanup-batch2.log). Order below = original tab-bar order.

Essentials (pinned=True, zenEssential=True, global):
1. YouTube - https://www.youtube.com/
2. Reddit - https://www.reddit.com/ (sessionstore title "Reddit - The heart of the internet"; tab showed "Problem loading page" at cleanup)
3. Todoist Today - https://app.todoist.com/app/today
4. Gmail inbox - https://mail.google.com/mail/u/1/#inbox
5. Google Calendar week - https://calendar.google.com/calendar/u/1/r/week

Pinned (pinned=True, zenEssential=False, Zen workspace {4bea3fa8-8b69-4659-93b6-df70303fb3f1}):
6. PCCV CF26 sheet - https://docs.google.com/spreadsheets/d/1WzUJNuCQlYLAj59-gdIPFFQv2P_d3f2KhEYcGeWhRRY/edit?gid=0#gid=0
7. Free Claude Code Admin - http://127.0.0.1:8082/admin/model_config
8. Welcome! - https://zen-browser.app/welcome/

NOT restored (stale task tabs, correctly closed): Kiwi, Color Picker, TodoMVC x3, MIT doc + 3 license pages, BrowserLeaks, BBC x3, vanillajs x2.

## Open flags for owner confirmation before position 56

- F1: sessionstore shows TWO YouTube essentials (tab 0 global zenWorkspace=None; tab 1 workspace {4bea3fa8}); only one YouTube tab was closed. Confirm restoration = one YouTube essential.
- F2: "Chat - Muse" (https://muse.ai/thread/750c8dae-58fb-4a65-82ac-753e78d6ce93) was a regular (not pinned/essential) tab, closed per the 02:14 list. Confirm in or out of this task.
- F3: Zen workspace display name for {4bea3fa8-8b69-4659-93b6-df70303fb3f1} is not in sessionstore (activeZenSpace only); runner restores pinned tabs in the workspace active at task time unless owner names another.

## Steps (frozen task format)

1. Open Zen (ws2). Record the current tab list (zen_dom list) as the before state.
2. Recreate the 5 essentials tabs above, in order, each marked Essential (and pinned) exactly as listed.
3. Recreate the 3 pinned tabs above, in order, each pinned (not essential).
4. Verify with a fresh tab list + a sessionstore read that all 8 tabs exist with the correct URLs, pinned flags, zenEssential flags, and relative order.
5. Write ~/rung3-chung-cu/R3-056/ket-qua.txt: before list, after list, per-tab URL + pinned + essential state, and any tab that could not be restored exactly (with reason).
6. Save timestamped screenshot(s) of the restored tab bar into ~/rung3-chung-cu/R3-056/.

## Evidence requirements

Files: ket-qua.txt. Screenshots: at least 1 timestamped screenshot of the restored tab bar. Plus start_time.txt / end_time.txt per lane rules. Class L: leave the restored tabs LIVE after the drive (no reset); coordinator verifies against the live tab list + sessionstore before scoring closes.

## Key (pass criteria)

Pass: all 8 tabs present with exact URLs, correct pinned/essential flags, correct relative order (essentials block then pinned block as listed), verified from tab list + sessionstore, ket-qua.txt complete, screenshot shows the restored tab bar.
Fail: any tab missing, wrong URL, wrong pinned/essential state, wrong order, or a stale task tab recreated instead.
Scoring: Pair B mechanics (two fresh independent scorers) unless coordinator assigns Pair A; grader never the author. Scored from sealed snapshot + live verification note (Class L score-before-reset; no reset exists for this task).
