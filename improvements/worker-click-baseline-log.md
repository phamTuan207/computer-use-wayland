# Worker CLICK-BASELINE log: pre-amend live baseline for the Brave address-bar discriminator

Branch: todolist-push. Task: measure the CURRENT (pre-amend) live baseline so the CLICK-AMEND fix can be judged against the goal bar (one vision drives as many actions as possible, total task time reduced as much as possible, accuracy 90% or above). Reference points: Codex send took 2.5 minutes and must be beaten; Muse 5 failed attempts are the accuracy baseline (0 text entered). No ydotool. No em/en dashes in this log or in any file written by this worker. All times wall-clock Asia/Ho_Chi_Minh + elapsed from task start 02:05.

## 2026-11-22 02:05:23 +07 (t+0s)
Start. Task received. Repo at ~/workspace/computer-use-wayland, branch todolist-push, HEAD 646cf71 (ZT-C ZT-07 PASS). CLICK-FIX commit is e4082ff (G28 loud refusal, type verification, zen_dom TimeoutError, ime trace in envelope); council verdicts AMEND, CLICK-AMEND not yet landed, so e4082ff is the pre-amend code under test. Discriminator: Brave address bar on ws2 (safe plain-text field, type one X, no Enter), one observe, ground the address bar, click it, type X, verify X appears. 3 runs if the lane allows. Do NOT message clone1, do NOT use the clone1 chat as target.

## 2026-11-22 02:06:02 +07 (t+1m) LANE CHECK 1: LANE BUSY, ZT-C LIVE
- ZT-B is DONE (ZT-00..ZT-06 finished 01:45, verdicts in worker-ztb-blind-run-log.md). ZT-C took over the lane at 01:48 and is LIVE: ZT-07 VERDICT PASS logged 02:05, elapsed ~17m, and ZT-08..ZT-10 remain. ZT-C log mtime is current (commit 646cf71 just landed at 02:05).
- Short SSH lane check 02:06:02: relay PID 1821 alive (session_remote.py serve, started Nov 21), no active computer-use session processes, zen_dom.lock touched 02:05 (ZT-C active). hyprctl in the SSH session failed with HYPRLAND_INSTANCE_SIGNATURE not set; the working form needs the signature exported from /run/user/1000/hypr/ first (per AGENTS.md 2026-11-21 23:19). Will use that form on the next check.
- Decision: DO NOT DRIVE. Lane is busy with ZT-C. Poll the ZT-C log every few minutes and wait for a gap (ZT-C between scenarios) or for ZT-C to finish. No workspace switch, no observe, no act while ZT-C runs.
- Next: poll ZT-C log + check installed laptop code version (read-only file check, no screen interaction) while waiting.

## 2026-11-22 02:07 +07 (t+2m) INSTALLED-CODE FINDING: laptop does NOT have e4082ff yet
- Installed tree ~/.local/share/agent-computer-use/scripts: cu.py md5 2d208d36, first_action.py md5 8caff365. grep type_verified = 0 in both installed files, ime_state_trace = 0 in installed first_action.py. The CLICK-FIX code (e4082ff) is NOT installed.
- Laptop repo copy ~/workspace/computer-use-wayland is at 4500a18 (old, pre-e4082ff), with untracked files, branch unknown. It needs fetch + checkout of todolist-push before any sync.
- VM repo check: zero scripts/ changes between e4082ff and HEAD 646cf71, so syncing the laptop to todolist-push HEAD installs exactly the e4082ff code. The discriminator procedure (worker-click-fix-log.md) requires this sync FIRST, or the envelope lacks ime_state_trace and type verification.
- Sync tool: scripts/sync-installed.py publishes the checkout to the installed tree and restarts the relay when idle; it REFUSES when the relay is busy. Sync is therefore a lane-free-only operation: it must wait until ZT-C is done, or it would change the code under ZT-C mid-scenario and invalidate both ZT-C and this baseline.
- Plan when the lane frees: (1) re-verify owner away + no human at keyboard via a fresh observe; (2) fetch + checkout todolist-push on the laptop repo; (3) run sync-installed.py (detached, relay restart when idle); (4) verify installed markers (type_verified and ime_state_trace present); (5) run the 3 discriminator runs, each as ONE combined SSH call (observe + act-now + verify observe + return to ws1) so the given observation stays fresh (G28 staleness rule, age under 100s).
- Owner goal updates noted from MEMORY.md (02:05-02:06, outside this task, no change to the task): 2-vision benchmark is the acceptance test and runs AFTER an improvement looks good, not before; each vision must extract maximum work (all coords, buttons, state from one image), verify cheaply without vision where possible. This baseline measures the pre-amend state against that bar.
- Parent sequencing (02:06-02:07): benchmark runs only AFTER the improvement method is ready; do NOT run it as exploration and do not proceed to it after the baseline. Baseline only, then report and wait. Benchmark spec for awareness: clone1 Brave 0x55705383d420 and clone2 Chrome 0x5570538ed160 on ws2; VISION 1 grounds ALL input bars and buttons for both; a script (no more vision) clicks/types/sends clone1 then clone2; VISION 2 checks both landed; EXACTLY 2 visions total. Record vision counts explicitly per run.

## 2026-11-22 02:11:31 +07 (t+6m) POLL 2: LANE STILL BUSY, ZT-C IS MID-ZT-08
- ZT-C log file mtime unchanged since 02:05:03 (ZT-07 verdict), no new log entries for 6 min. Log mtime alone would say "quiet", but the LIVE signal says otherwise: /tmp/ztc-zt08-s7.json, /tmp/ztc-zt08-s6.json, /tmp/ztc-zt08-park.json exist on the laptop and ~/workspace/ztc-obs-zt08-s4.jpg exists on the VM, so ZT-C is mid-ZT-08 (step 6/7). ZT-C writes its log in chunks, so mtime is NOT a reliable lane signal; the /tmp/ztc-* and obs files are.
- Laptop state 02:11:31: active workspace 1, Zen 0x557052b62dd0 "Vietnam - Wikipedia", no active session process (ZT-C between batches), relay 1821 alive. Hyprland check now works with HYPRLAND_INSTANCE_SIGNATURE exported from /run/user/1000/hypr/.
- Decision: DO NOT DRIVE. Keep polling every few minutes. ZT-08 is at step 6/7, then ZT-09 and ZT-10 remain. Also noted: VM working tree has uncommitted `M scripts/cu.py` (CLICK-AMEND editing live) plus new crawl logs; my commits use explicit pathspec on my log file only.
- Run-plan prep (no driving): drive directly via SSH + act-now, following the CLICK-FIX discriminator procedure. Per run: grounding observe (viewed, vision 1) + one combined SSH call (fresh observe as given observation, then act-now at once so age stays under 100s) + verify observe (viewed, vision 2, ground truth for the X) + return to ws1. Batch mirrors Stage A: click title (450,13), click address bar (grounded from the fresh image), wait 2000, type single X, wait 800, NO Enter. Record per run: total wall time (order to verified X), observes executed, visions viewed, actions per observation, X landed or not, envelope ok/completed/type_verified/ime_state_trace. No park move in the batch (J37: the park move trips the screen-changed preflight).

## 2026-11-22 02:17:57 +07 (t+13m) POLL 3: LANE STILL BUSY, ZT-08 DONE, ZT-09 AT STEP 5
- ZT-08 VERDICT PASS at 02:12 (elapsed ~7m). ZT-09 is now running: ztc-obs-zt09-s5.jpg and ztc-obs-zt09-s5hover.jpg exist on the VM, so ZT-C is at ZT-09 step 5. New ZT-C error J40 recorded: stale given observation falls back to captured screen observation, window-space point then misses by the window origin offset (same G28 class, reinforces the same-call observe+act rule).
- Decision: DO NOT DRIVE. Keep polling every few minutes. ZT-09 in progress, ZT-10 still to come after it.

## 2026-11-22 02:23:12 +07 (t+18m) POLL 4: LANE STILL BUSY, ZT-09 AT STEP 9 + CLEANUP
- Poll 4 glob was wrong (zt1* misses zt09 files) and the ZT-C log still ends at the ZT-08 verdict, so a direct check followed: laptop /tmp holds ztc-zt09-s9c/d/e.json + park2 + restore, and the VM holds ztc-obs-zt09-cleanup.jpg + cleanup2.jpg (newest). ZT-09 is at step 9 / cleanup, nearly done. No active session process at this instant, relay 1821 alive.
- Decision: DO NOT DRIVE. ZT-10 still to come after ZT-09. Keep polling.

## 2026-11-22 02:28:29 +07 (t+23m) POLL 5: LANE STILL BUSY, ZT-09 FAIL, ZT-10 AT STEP 6
- ZT-09 VERDICT FAIL at 02:23 (elapsed ~11m). Steps 1-4 pass; steps 5-6 fail on activation (J42), steps 7-8 fail (J43 guard blocks Ctrl+Shift+T). Worker error J44 owned in the log: ZT-C closed the owner's pre-existing ModelArk-Coding-Plan tab with an unverified Ctrl+W, then restored it from the exact URL in places.sqlite (count back to 18, set equal by title/URL, tab at a different position with fresh history). Not my task, noted only as lane context.
- ZT-10 is now running: ztc-obs-zt10-s6a.jpg, s6hover, s5, s3 exist, so ZT-C is at ZT-10 step 6. ZT-10 is the last scenario in ZT-C's batch (ZT-07..ZT-10); after it the lane should free unless ZT-C takes more work.
- Decision: DO NOT DRIVE. Keep polling.

## 2026-11-22 02:33:40 +07 (t+28m) POLL 6: LANE STILL BUSY, ZT-10 STILL AT STEP 6
- ZT-10 still running: newest files zt10-menu.jpg, zt10-s6hover4.jpg, s6c, s6hover3/2. Step 6 is taking a while (repeated hovers). ZT-C log still ends at the ZT-09 verdict (chunked writes).
- CLICK-AMEND is progressing on the VM (commits 96a9e46, 4b7d6ac). Caution for the baseline: if the amend lands and syncs to the laptop before I run, the installed code would no longer be pre-amend. I will re-verify the installed code markers (type_verified / ime_state_trace presence, md5) immediately before running, and report any change.
- Decision: DO NOT DRIVE. Keep polling.

## 2026-11-22 02:38:48 +07 (t+33m) POLL 7: LANE STILL BUSY, ZT-10 PAST STEP 6 INTO ABOUT:CONFIG
- ZT-10 still running: newest files zt10-aboutconfig.jpg, s6e, dismiss, esc2, s6d. It has moved past step 6 into an about:config phase. ZT-C log still ends at the ZT-09 verdict (chunked writes).
- Decision: DO NOT DRIVE. Keep polling.

## 2026-11-22 02:44:08 +07 (t+39m) POLL 8: LANE STILL BUSY, ZT-10 STILL IN STEP 6 / SETTINGS
- ZT-10 still running: newest files zt10-s6f.jpg, setsearch, lookfeel, prefs, rclick. Still working step 6 in the settings area, about 20 min into ZT-10. ZT-C log still ends at the ZT-09 verdict (chunked writes).
- Decision: DO NOT DRIVE. Keep polling.
