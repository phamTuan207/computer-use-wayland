# Council Member 3 (safety and sequencing): verdict on the Y6b Wayland-nested run plan

- Date: 2026-11-21, 18:54-19:00 +07. Council member: C3 (safety and sequencing).
- Scope: Worker Y6 FINAL report (commit 482e4ba), the launcher
  /tmp/y6-nested/run-nested-wayland.sh, conf/hyprland-wayland.lua,
  conf/nested-visuals-hook.lua, conf/optics.lua, run-nested-pill.py,
  and Y6b's log (worker-y6b-nested-wayland-log.md).
- Verdict: APPROVE-WITH-CHANGES. Seven numbered changes below. All seven
  are required before Y6b launches. None of them redesigns the probe; four
  close real holes I proved with commands, three are cheap guards.

## What I checked, with commands and outputs

All wall-clock times +07, 2026-11-21. Laptop access only via
~/workspace/ssh-laptop.sh. No live session touched, no process killed,
no file written on the laptop.

1. 18:54:57. `cat /tmp/y6-nested/run-nested-wayland.sh` (11,648 bytes).
   Read in full. Then `cat run-nested-pill.py`, `conf/hyprland-wayland.lua`,
   `conf/nested-visuals-hook.lua`, `head -50 conf/optics.lua`.
   Plugin load is `hl.plugin.load` of backup 1 hyprglass, and it appears
   ONLY in the nest config file, which is passed to the nested Hyprland
   via `--config`. No other config is referenced.
2. 18:55. Danger grep over the launcher:
   `grep -n -i "reboot|modprobe|rmmod|hyprland.conf|load.so|1515|pkill -f|rm -rf /|~/.config"`.
   Result: only two PID 1515 lines, both read-only (`ps -o pid,lstart,cmd -p 1515`
   in teardown, plus a comment). Zero hits for reboot, modprobe, rmmod,
   hyprland.conf, load.so, pkill -f. Zero hits for `AQ_DRM|card0|vkms|renderD`
   in the launcher and in the nest conf (count 0 in both files).
3. 18:55. Live conf dir listing: `ls -l --time-style=full-iso ~/.config/hypr/`.
   Newest mtimes are bindings.lua and autostart.lua at 17:36-17:38, before
   Y6 started (18:17). Nothing in the live conf dir was touched 18:17-18:56.
4. 18:56. Lock check on the laptop: lock file
   ~/.cache/agent-computer-use/zen_dom.lock exists (0 bytes,
   mtime 17:48), inode 8620372. Python scan of /proc/locks for a FLOCK
   entry on that inode: NO holder. zen_dom.lock is free right now.
5. 18:56. Live session: `ps -o pid,lstart,cmd -p 1515` shows Hyprland
   alive since Sat Nov 21 15:17:25 2026. `fuser -v /dev/dri/card0` shows
   user PID 1515 holding card0. `lsmod | grep vkms` shows vkms loaded,
   refcount 2. /dev/dri/card0 (18:41) and /dev/fb1 (18:41) still present.
6. 18:56. Live signature: `ls /run/user/1000/hypr/` contains exactly
   `11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795249046_1138556825`,
   identical to the hardcoded LIVE_SIG in the launcher. `hyprctl version`
   with that signature returns Hyprland 0.57.2, commit 11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947.
   (Note: the sig dir is /run/user/1000/hypr/, not hyprland/.)
   LIVE_SIG is current as of 18:56. It must still be re-verified at run time.
7. 18:56. A1 pilot lock audit (VM repo): `grep -rn "zen_dom|flock"`
   over tests/realistic/a1-pilot/ returns NOTHING. The runbook
   (tests/realistic/a1-pilot/runbook.md) drives A1 arms through the
   broker plus managed Chromium (CDP 127.0.0.1:9222) and never mentions
   zen_dom.lock. run_agyq2.py preflight (lines 1458-1500) REQUIRES the
   lock be held by an ancestor process, and accepts FLOCK entries.
   Y9 launches under `flock -w 60 ~/.cache/agent-computer-use/zen_dom.lock`.
   So Zen runners are lock-serialized, A1 arms are not.
8. 18:56. Live proof of the gap, on the laptop, while zen_dom.lock is FREE:
   PID 184702 is a Codex exec session (`codex exec -s danger-full-access
   -m gpt-6-luna`, started 18:01:09), parent of PID 184812
   (playwright-mcp, headless Chromium) and of PID 186612 (headless
   puppeteer Chromium, --remote-debugging-port=0,
   user-data-dir /tmp/puppeteer_dev_chrome_profile-S4dcst, started 18:02:26).
   A broker/CDP live session is running right now with no lock held.
   This is not a hypothetical: flock does not serialize all live work.
9. 18:56. `pgrep -af "mpv|foot"` on the laptop returns no real process
   (only my own ssh command line matching the pattern). No mpv and no
   foot are running right now, so the script's system-wide `pkill -x mpv`
   would currently be harmless. The hazard is latent, not present.
10. 18:56. Timeout forwarding test on the VM (GNU coreutils timeout,
    same tool family as the laptop): `timeout 300 sleep 120 &`, then
    `kill` (TERM) on the timeout PID. Result: the child sleep died with
    it, timeout exit 143. So the normal TERM path in teardown works.
    The kill -9 fallback was NOT tested the same way, and by construction
    SIGKILL cannot be forwarded: killing the timeout wrapper with -9
    leaves its child alive. See change 3.
11. 18:56. Laptop repo state: branch todolist-push, HEAD 4500a18.
    `git status --porcelain` shows no modified tracked files (only
    untracked papers and node_modules). The pill imports
    scripts/indicator.py from this checkout, so it loads HEAD 4500a18
    as of now. Y6b must record the HEAD at run time.

## Question 1: hard rules, line by line

All hold, with one scoping flaw (change 4) and one teardown flaw (change 3).

- Never touch the live hyprland.conf: HOLDS. The launcher never opens,
  writes, or references ~/.config/hypr. The only config passed is
  /tmp/y6-nested/conf/hyprland-wayland.lua, to the nested process.
- Never load.so into the live compositor: HOLDS. `hl.plugin.load` is in
  the nest conf only. No `hyprctl plugin load` anywhere in the launcher.
- Never reboot: HOLDS. No reboot, shutdown, or systemctl call.
- Never force-remove the vkms module: HOLDS. No modprobe, no rmmod,
  no /dev/dri reference at all in the launcher or nest conf.
- Never touch the live Hyprland session (PID 1515): HOLDS, except for
  read-only observation. PID 1515 appears only in `ps -o pid,lstart,cmd -p 1515`
  (teardown live check). The `live()` helper runs only `hyprctl version`
  and `hyprctl -j plugin list`, both read-only.
- Teardown `pkill -x mpv`: SCOPE FLAW. It kills every mpv on the machine,
  not just the nest backdrop. Currently no mpv runs, so it is harmless
  today, but the script has no guard against a live mpv appearing.
  Same for `pkill -x mpv` in arm A and the `pgrep -x mpv` / `pgrep -x foot`
  readiness checks, which cannot tell a nest process from a live one.
  Fix in change 4.
- Teardown `rm -rf "$RUN_DIR"`: HOLDS on scope. RUN_DIR is
  /tmp/y6-nested/run, nest-only. It does not touch live state. But it
  destroys the nested per-instance log, which is the forensic record.
  Fix in change 5.
- `live hyprctl` calls in teardown: READ-ONLY, confirmed. `version` and
  `plugin list` mutate nothing.

## Question 2: flock, and the A1 coordination gap

Flock is sufficient for Zen runners and NOT sufficient for the run as a whole.

- For Zen runners: sufficient. run_agyq2.py preflight raises unless the
  lock is held by an ancestor, so a Zen runner cannot start without the
  lock. Y6b holds it with `flock -n 9` for the whole run. A runner
  launched mid-run waits on its `flock -w 60` (Y9) or `-w 1800` (Y4)
  and then either fails or starts after Y6b releases the lock. Either
  way it cannot run concurrently. Council C change 6 is correctly
  implemented.
- For everything else: NOT sufficient. The A1 pilot never touches
  zen_dom.lock (zero matches in runbook.md, preflight-probe.md,
  a1_manifest.py). A1 arms drive managed Chromium via CDP plus the
  broker. The nest window appears on the live screen as a Wayland client,
  tiles, resizes Zen, changes the live window list, and can take focus.
  That pollutes any concurrent broker/CDP observation (window list,
  hasFocus, visibility), even though no Zen runner is involved.
- PROVEN LIVE, not hypothetical: at 18:56, with zen_dom.lock FREE, a
  Codex session (PID 184702, started 18:01) is driving headless Chromium
  via playwright-mcp (PID 184812) and puppeteer (PID 186612). If Y6b had
  launched at that moment holding the lock, that session would still
  have been running alongside the nest window.
- The slot queue in Y6b's log (Y8, then Y9, then Y11, then Y6b) lists
  only Zen runners. It does not cover A1 arms. That is the exact gap.
  Fix in change 1.

## Question 3: handover

Setting Y6_HANDOVER_CONFIRMED=1 from the standing record is NOT sufficient.

- The record is: owner handed the machine over 18:24 +07, out of the
  house, busy. That was a real handover, but it is time-bound (Y6's own
  report says so, resolution 16), and Y6b runs after three other runners
  (Y8, Y9, Y11). By launch time the record will be hours old.
- The script's gate is only the env flag. Nothing in the script verifies
  the owner is still away. The flag is a claim by whoever launches it.
- Fix in change 7: Y6b must get a fresh confirmation from Muse
  immediately before launching, and record its wall-clock time in the
  run log. The check must cover: owner still away with no return signal,
  no Zen runner active, no A1 arm scheduled in the 30 minute window,
  no broker/CDP session active, live PID 1515 alive with hyprctl
  responsive, and LIVE_SIG still matching the live session.

## Question 4: failure modes, exit paths

Five modes, all abort through fail() into the EXIT trap on the normal
paths, with two trap gaps.

- Nest crashes: fail at the sig wait (15s), socket check, or plugin
  list step. Teardown runs. Residual: a nested Hyprland crash writes a
  crash report to ~/.cache/hyprland/ and can pop a desktop crash
  notification on the live screen, exactly as Y6's 8 DRM crashes did
  (owner saw one at ~18:23). Owner is away; the notification persists
  until return. Log it if it happens. Not a blocker.
- Plugin refuses to load: caught by `grep -q hyprglass` on the nested
  plugin list, fail, teardown. Clean.
- Version mismatch: caught by the liquid gate (hook prints the marker,
  liquid_available stays false for 60s) and by the status JSON. The
  script correctly does NOT substitute backup 2. Clean, but the nested
  per-instance log that would prove the mismatch is deleted by teardown.
  See change 5.
- Pill never becomes ready: fail after 45s, teardown. Clean.
- Nest hangs past timeout 300: timeout sends TERM to the nest. My test
  proves TERM to the timeout wrapper reaches the child. But timeout has
  no --kill-after, so a TERM-ignoring nest would keep the timeout waiting
  indefinitely, and teardown's `kill -9 "$NESTED_PID"` then kills only
  the wrapper, orphaning a live nested Hyprland (setsid, own session).
  Also worst-case elapsed is marginal against 300 (see change 6).
  Fix in changes 3 and 6.
- Trap coverage: `trap teardown EXIT` runs on fail() exits and on
  normal exit 0. It does NOT run if the script itself is killed by
  SIGTERM, SIGINT, or SIGHUP (for example an SSH drop while Y6b runs it
  in the foreground). In that case the nest and pill survive as orphans
  (both setsid nohup), the nest window stays on the live screen, and,
  worse, the orphaned children inherit fd 9, so they keep holding
  zen_dom.lock forever and every later runner's flock blocks or fails.
  Fix in change 2.

## Question 5: vkms leftover

No interaction. Confirmed from the script and config, not assumed.

- Zero references to card0, vkms, renderD, AQ_DRM_DEVICES, or any
  /dev/dri path in run-nested-wayland.sh and hyprland-wayland.lua.
- The nest uses the Wayland backend (parent socket
  /run/user/1000/wayland-1, absolute path). Its allocator comes from the
  parent compositor via dmabuf. It never opens a DRM device and never
  needs DRM master, which is exactly why option C survives the wall
  that killed headless.
- The vkms module stays loaded (refcount 2), card0 stays held open by
  live PID 1515, /dev/fb1 stays. The script does nothing to any of them.
  No change needed here.

## Question 6: other holes found

- Lock fd inheritance (change 2, worst hole): `exec 9>"$LOCK"` then
  `setsid nohup ... &` for the nest, pill, and arm B mpv. All three
  children inherit fd 9. Any orphaned child keeps the flock held after
  the script dies. On the normal path teardown kills the children first,
  so this only bites on abnormal script death, but that is exactly the
  path with no other protection.
- Worst-case elapsed vs timeout 300 (change 6): sleeps alone sum to
  about 197s in the worst case (sig wait 15, sleep 5, liquid gate 60,
  sleep 2, control 1, pill wait 45, sleep 2, arm A 32, arm B sleep 3
  plus 32). On top of that sit about 98 grim invocations (2 control,
  32 arm A, 64 arm B), each a nested capture through the parent
  compositor. At 0.3-1.0s per grim that is 30-98s more, putting the
  worst case at roughly 230-295s, inside 300 but with almost no margin.
  A slow grim or a full liquid/pill wait can fire the timeout mid arm B
  and produce a spurious abort.
- Pill repo state (minor): the pill imports scripts/indicator.py from
  the laptop checkout (HEAD 4500a18 at 18:56, no modified tracked files).
  Y6b must record the HEAD at run time so the loaded code is identified.
  Fold into change 7, no separate fix.
- Y6b's own open question 2 (forensic log loss) is valid and is change 5.

## Required changes (all seven, before launch)

1. Close the A1 / non-flock gap with Muse, at run time. Y6b must get an
   explicit go from Muse for its 30 minute window, covering all three
   legs, and record the go with its wall-clock time in the run log:
   (a) no A1 pilot arm scheduled in the window; (b) no broker/CDP/
   playwright session active, checked by `pgrep -af "codex exec|playwright-mcp|puppeteer|chromium --headless"` on the laptop plus
   Muse confirming no A1 arm is booked; (c) no Zen runner active,
   checked by the /proc/locks inode method for zen_dom.lock plus
   `pgrep -af "run_agyq2|run_agy_y2|run_live"`. Flock alone is not the
   go. Do not launch on the slot queue alone.
2. Stop the lock from outliving the script. Add `9>&-` to all three
   background launches (nest, pill, arm B mpv) so no child inherits the
   lock fd. Change the trap to `trap teardown EXIT TERM INT HUP` so
   script death by signal still runs teardown. Y6b must also launch the
   script itself detached (setsid nohup, disown) so an SSH drop cannot
   kill it in the first place.
3. Kill the real nested Hyprland in teardown, not just its timeout
   wrapper. Resolve the child with
   `NEST_CHILD=$(pgrep -P "$NESTED_PID" -x Hyprland)` before killing,
   then TERM the child, sleep 2, then -9 the child. Add
   `--kill-after=10` to the `timeout 300` invocation (change 6 raises
   the 300) so expiry guarantees nest death even if it ignores TERM.
4. Scope the mpv kills. Add a pre-launch guard that fails the run if
   any mpv or foot is already running (`pgrep -x mpv` / `pgrep -x foot`
   must be empty before launch), so the later system-wide `pkill -x mpv`
   and the `pgrep` readiness checks can only match nest processes.
   Better still, capture the arm B mpv PID (`MPV_B_PID=$!`) and kill it
   by PID, and resolve the autostart mpv PID as a child of the nested
   Hyprland PID. The guard is the minimum; PID-scoped kills are preferred.
5. Preserve forensics before destroying them. In teardown, before
   `rm -rf "$RUN_DIR"`, copy `$RUN_DIR/hypr/$SIG/hyprland.log` to
   `$NEST/nest-hyprland-$SIG.log` (best effort, `cp ... || true`), and
   keep the copy on every exit path including failure. The per-instance
   log is the only record of a plugin refusal, version mismatch, or
   nest crash signature.
6. Raise the nest timeout from 300 to 600. Worst-case elapsed is about
   197s of sleeps plus about 98 grim calls, roughly 230-295s total, so
   300 has almost no margin and can fire mid arm B. 600 covers the
   worst case with room for slow grim calls.
7. Fresh handover at run time, not the standing record. Immediately
   before launching, Y6b must confirm with Muse that the owner is still
   away with no return signal, then set Y6_HANDOVER_CONFIRMED=1 and log
   the confirmation wall-clock time. In the same pre-launch block,
   re-verify: live PID 1515 alive with `hyprctl version` responsive,
   LIVE_SIG still matches `ls /run/user/1000/hypr/`, zen_dom.lock free,
   no mpv/foot running (change 4 guard), and the laptop repo HEAD
   (for the pill's indicator.py import). If any check fails, do not launch.

## What is sound and needs no change

- Hard rules (question 1): all hold, verified line by line and by grep.
- Flock for Zen runners: correctly implemented and enforced by the
  run_agyq2.py preflight. Council C change 6 stands.
- Failure abort paths: fail() plus EXIT trap covers every in-script
  failure mode (crash, plugin refusal, version mismatch, pill timeout,
  positive control failure). Version mismatch correctly refuses backup 2.
- vkms isolation (question 5): the nested Wayland run never touches a
  DRM device. The leftover module, card0, and /dev/fb1 are undisturbed.
- Asymmetry clause: a nest negative stays "not reproduced in the nest"
  and never exonerates the live backdrop. No safety impact, but correct
  to keep.

## Verdict restated

APPROVE-WITH-CHANGES. Apply changes 1-7, then run in the next window
that Muse explicitly clears under change 1. The probe itself is safe to
run; the holes are in coordination (A1 arms run outside the flock, and a
live CDP session was running with the lock free at 18:56), in teardown
robustness (lock fd inheritance, timeout wrapper kill, forensic log loss),
and in stale handover (18:24 record will be hours old at launch). None of
these requires redesigning the probe.
