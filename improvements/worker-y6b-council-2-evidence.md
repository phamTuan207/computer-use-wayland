# Council Member 2 (evidence and measurement): verdict on the Y6b Wayland-nested probe run

- Date: 2026-11-21, 18:54-19:05 +07
- Council member: Council 2, evidence and measurement
- Scope: the run plan in /tmp/y6-nested/run-nested-wayland.sh (216 lines), run-nested-pill.py, conf/hyprland-wayland.lua, conf/nested-visuals-hook.lua, conf/optics.lua, against Y6 FINAL report worker-y6-hyprglass-nested-probe.md (commit 482e4ba)
- Method: read the runner and all conf files, then tested every load-bearing claim on the laptop with read-only commands plus two small controlled experiments (grim captures to /tmp, a flock/timeout test with sleep processes). No live session state was changed. No ydotool. No em dash or en dash in this paper.

## Verdict: BLOCK

The design (two frame-diff arms, positive control, verdict asymmetry) is sound, and most of the measurement logic survives checking. But the script as written cannot run to a verdict: it has two independent fatal bugs that abort it before any measurement, and its teardown destroys the only full forensic log on every exit, including on the abort path. Running it now wastes a scarce handover window and leaves nothing to debug with. Apply fixes 1 to 9 below, re-verify with the checks listed under each fix, then run. Fixes 1 and 2 are fatal. Fixes 3 and 4 are evidence destruction and a lock leak. Fixes 5 to 9 are verdict-validity defects that would let a bad run print a confident wrong verdict.

## What checked out (keep as is)

- grim PNG output is deterministic for identical pixels. Two captures of the same static region 1s apart were byte-identical (md5 c3f9c1b9435f7be6c5192b806857cae8, both files). The PNG contains only IHDR, IDAT and IEND chunks, no tIME and no text chunks. So identical pixels give identical bytes (the positive control cannot false-fail on metadata), and different pixels give different bytes (lossless PNG; two different frames give identical bytes only if the pixels are actually identical). The positive-control design is sound. Full answer to question 3 is in the question-by-question section below.
- The testsrc2 backdrop moves in every sampled corner. Over the 10 one-second frames of backdrop.mp4, the full frame differed on 9/9 consecutive pairs, and both 200x200 corners (0,0 and 760,0) differed on 9/9 pairs. The corner sample is a valid motion proxy for this video.
- The pill is static when idle, so arm A "any diff = flicker" is valid in principle. Native code: entrance_progress starts at 1.0 and only animates if CU_INDICATOR_ENTRANCE is set; indicator.py pops that variable before spawning the native process, so entrance mode is STATIC. report_metrics fires every 1000ms but only logs to stderr, it never queues a draw. The painted callback only counts when idle. There is no clock, spinner or periodic redraw in the pill. The pill surface is 320x66 (pill 288x38 at local 16,16), top anchor only, so in the 960x540 nest it sits at x=320..640, y=0..66, and the chosen backdrop corner (760,0,200,200) does not overlap it.
- The verdict if-chain is exhaustive and mutually exclusive (question 5). For every (A_DIFF, B_PILL_ONLY) pair exactly one VERDICT line prints: A_DIFF > 0 prints REPRODUCED, A_DIFF = 0 with B_PILL_ONLY = 0 prints NOT reproduced in the nest, A_DIFF = 0 with B_PILL_ONLY > 0 prints REPRODUCED in animated arm only. No double print exists. The asymmetry clause is present in the branch 2 text ("a nest negative does not exonerate the live backdrop").
- grim is fast (0.028s per capture), so the 300s timeout budget has about 100s of slack at worst-case durations. The SIG pick by ls -t is safe because the runner deletes $RUN_DIR/hypr before launch, so exactly one signature dir exists. LIVE_SIG is pinned by value. The liquid gate and version-mismatch NO-GO are correctly specified.

## Required changes

### 1. FATAL: the pill-geometry parse crashes on the real layers JSON (script patch)

The runner parses nested `hyprctl -j layers` as `{monitor: {level: [entries]}}`. The real structure, read live at 18:57, is `{monitor: {"levels": {"0": [...], "1": [...], "2": [...], "3": [...]}}}`. Each entry does have x, y, w, h and namespace, but there is an extra "levels" wrapper. The runner's loop iterates the wrapper dict, so `e` is the string "0", and `e.get("namespace")` raises AttributeError. I ran the runner's exact snippet against live layers JSON: traceback `AttributeError: 'str' object has no attribute 'get'`, exit 1. The `|| fail` then reports "pill surface not found in nested layers (pill not visible)", which is a wrong diagnosis masking a parse bug. The run can never reach arm A.

Fix, replace the parse block with:

```python
import json
import sys
data = json.load(open(sys.argv[1]))
for monitor, mdata in data.items():
    for level, entries in mdata.get("levels", {}).items():
        for e in entries:
            if e.get("namespace") == "computer-use-indicator":
                print(str(e["x"]) + "," + str(e["y"]) + "," + str(e["w"]) + "," + str(e["h"]))
                sys.exit(0)
sys.exit(1)
```

Re-verify: run the fixed snippet against live `hyprctl -j layers` (must exit 1 cleanly with no traceback, since no pill is live) and against a synthetic JSON containing a computer-use-indicator entry (must print its geometry).

### 2. FATAL: every frame capture fails twice over (script patch)

`capture()` runs `nest grim -g "$3" -o WAYLAND-1 file`. Both parts are wrong, tested live at 18:57:

- grim rejects `-o` together with `-g`: stderr `-o and -g are mutually exclusive`. The `-o` must go. In the nest there is a single output, so `-g` alone suffices.
- grim rejects the comma geometry the runner passes: `grim -g "2464,902,200,200"` fails with `invalid geometry`. grim accepts only the `X,Y WxH` form: `grim -g "2464,902 200x200"` succeeded (37981 bytes).

So the control frames (which use `-o` without `-g`) would pass, then the first arm A capture would fail with "grim armA-01 failed", the script would exit 1, and teardown would destroy the nested log (see fix 3). No frame would ever be captured.

Fix: drop `-o` from `capture()`, and emit geometry in `X,Y WxH` form. The python in fix 1 must print `str(x) + "," + str(y) + " " + str(w) + "x" + str(h)`, and BACKDROP_GEOM must become `0,0 200x200` or `760,0 200x200`.

Re-verify: run `grim -g "2464,902 200x200"` on live (already verified working) and, once the nest is up, one `nest grim -g` call with the exact string the fixed script will pass.

Note: grim `-g` coordinates are layout coordinates, and layers x,y are layout coordinates too (live: the monitor sits at 2464,902 in both). In the nest (one output at 0x0, scale 1) they coincide. Add a bounds check that the pill rect lies inside the 960x540 output before capturing, so an out-of-range geometry fails loudly instead of capturing black.

### 3. FATAL to forensics: teardown deletes the only full nested log on every exit (script patch)

Teardown runs `rm -rf "$RUN_DIR"` on EXIT, success and failure alike. The nested per-instance log lives at `$RUN_DIR/hypr/$SIG/hyprland.log`, so it is destroyed on every run. Nothing else preserves it: the surviving `$NEST/hyprland-wayland.log` is only Hyprland stdout, 54 lines for attempt 8, against 2842 lines in the attempt 8 per-instance log (Y6 figure). The log arm, the Wayland-backend check, the plugin load, the liquid gate and any crash diagnosis all depend on the per-instance log, and it will be gone. The answer to question 1 is: no forensic evidence of the nested compositor survives a failure, or a success. The frames, the JSONs and the pill log survive (they live under $NEST), but the compositor log does not.

Fix in teardown, before `rm -rf "$RUN_DIR"`:

```bash
if [ -n "$SIG" ] && [ -d "$RUN_DIR/hypr/$SIG" ]; then
  cp -r "$RUN_DIR/hypr/$SIG" "$NEST/hypr-saved-$(date +%Y%m%d-%H%M%S)-$SIG"
fi
```

This must be a script patch, not an external watcher: the script's own rm races any watcher, and the trap already runs on every exit path including fail(). Also save the runner's own stdout, which currently lives only in ephemeral SSH stdout: the SUMMARY and VERDICT lines are printed, never written to disk. The run takes about 4 minutes and the laptop SSH session dies at about 30 seconds (observed directly at 19:00, exit 255 Broken pipe, during a 35 second sleep), so Y6b must run detached, and a detached run without a log file loses the verdict. Either tee inside the script (for example `exec > >(tee -a "$NEST/run-$(date +%Y%m%d-%H%M%S).log") 2>&1` at the top) or run it detached with stdout redirected to a timestamped file and record that invocation. Prefer the script patch so the verdict cannot be lost by an operator mistake. Also put frames in a timestamped per-run directory instead of fixed names under $NEST/frames, so a rerun does not overwrite the previous run's evidence. Crash reports under ~/.cache/hyprland already survive teardown; note them in the run report if the nest crashes.

### 4. Teardown kill is racy and leaks the runner lock (script patch)

Two facts, both verified PID-exact at 19:00:

- NESTED_PID is the `timeout` PID, not the Hyprland PID (`setsid nohup timeout 300 Hyprland ... &`). Sending TERM to timeout does forward to the child (verified: timeout's sleep child died after TERM to timeout). But teardown then sends `kill -9 $NESTED_PID`, which SIGKILLs timeout without forwarding, so a Hyprland that is slow to exit after TERM survives orphaned, still holding its window on the live screen.
- File descriptor 9, which holds the flock on zen_dom.lock, is inherited by the nested session. Verified: a subshell holding the lock and spawning a setsid child, then exiting, left the lock held until the child was killed (`flock -n -c true` failed after subshell exit, succeeded after the child died). So a surviving nest holds zen_dom.lock and blocks every future runner, silently: teardown's live checks (PID 1515, hyprctl, plugin list) would all still pass.

Fix: kill the whole nested session process group instead of the timeout PID (setsid makes NESTED_PID the session leader, so `kill -- -$NESTED_PID`, then a delayed SIGKILL to the group), and verify in teardown that no Hyprland besides PID 1515 remains and that the lock is free (a `flock -n` test). Also delete the two `pkill -x mpv` calls: they kill ANY mpv on the machine, including the owner's, and arm A's `pgrep -x mpv` check fails if any foreign mpv runs. Kill mpv by PID instead: find it in the nested `hyprctl -j clients` list (mpv is a nest client with a listed PID) and kill that PID, and check death by that PID. Killing the nest session group already kills its mpv and foot children, so the teardown pkill becomes unnecessary.

### 5. A single differing pair must not declare REPRODUCED (script patch)

A_DIFF counts any of 31 pairs. One differing pair (1/31) triggers REPRODUCED. The incident flicker runs at about 10 Hz, so a true reproduction differs on most 1s-apart pairs; a single diff is more likely a one-off glitch (a capture tear, a compositor hiccup, first-frame settle). Fix: A_DIFF >= 3 is REPRODUCED, 1-2 is INCONCLUSIVE (rerun arm A once, same rule decides; if still 1-2, report INCONCLUSIVE with the counts), 0 is negative. Apply the same rule to B_PILL_ONLY (>= 3 reproduced in the animated arm, 1-2 inconclusive). Report the counts in every case; the counts, not just the word, are the evidence.

### 6. Both arms lack validity gates (script patch)

- Arm A never proves the backdrop was actually static. Capture a backdrop sample during arm A (same cadence as the pill captures) and require 0 diffs. If the sample moves, arm A is VOID (mpv did not die, or something else moves), not a flicker verdict.
- Arm B never proves the animated arm actually animated in the sample. Require B_BG_DIFF >= 15/31. If it is near 0, arm B is VOID (mpv frozen, or the corner blind) and no verdict may be drawn from it. My testsrc2 analysis says the gate is easily met when mpv runs (corners differ 9/9 pairs), so the gate costs nothing when the arm is healthy.
- After restarting mpv for arm B, the script only sleeps 3s and checks pgrep, which proves the process exists, not that it presents moving frames. Wait until two consecutive full-output frames differ (bounded, for example 10s) before starting arm B captures. This also re-validates nest liveness after arm A. Note the residual limit: the static arm cannot prove liveness during itself, since a stalled nest reads exactly like a static scene (identical frames). Bracketing arm A with the pre-run positive control and this post-arm-A motion check is the mitigation, and the run report must state that limit instead of implying arm A alone proves a negative.

### 7. The backdrop-sample non-overlap is assumed, not computed (script patch)

The branch uses only PILL_X >= 480 and never looks at width or height. With the real pill surface (320x66 at x=320..640, y=0..66) the chosen corner (760,0,200,200) is safe, but the code does not prove it: a wider or differently placed pill could overlap the sample and corrupt arm B silently. Fix: compute the intersection of the pill rect (x, y, w, h) with each candidate corner rect, pick a corner with zero intersection, and fail if none exists. Also re-read pill geometry from nested layers immediately before arm B and abort or re-baseline if it changed; the current code reads geometry once and assumes the pill never moves between arms.

### 8. The launcher waits for "ready", which prints before show (script patch)

run-nested-pill.py prints `Y6-NEST-PILL: ready` after Native() returns but before `native.command("show")` runs, and command("show") blocks until the frame is presented (it waits for the 'visible' acknowledgement). The launcher proceeds on "ready" plus sleep 2, so the pill may still be settling when arm A starts. Fix: wait for the `Y6-NEST-PILL: show=visible` line in nest-pill.log before the layers check. Cheap, removes first-frame settle as a source of spurious arm A diffs.

### 9. Drop the log-pattern arm from the evidence (script patch)

The callback/log arm counts lines matching repaint|paint|commit|frame in the nested log. Calibration on the live log, the best available proxy for the nested log, kills it as a signal: 6 matches in 4959 lines over about 3.7 hours, zero of them repaint events (two giant GL extension dump lines matching "framebuffer", two "failed to commit" DRM lines, two "Cannot commit when a page-flip is awaiting" lines). Over a 32 second idle window the log grew 0 lines and the count stayed at 6. A per-arm count over 32 seconds will be 0 in both arms regardless of flicker, and any nonzero value would be startup or error noise, not a repaint. It cannot discriminate flicker from quiet, and a "0 in both arms" reading would be misread as "no repaints". It is not evidence, and Y6 already marks it UNVERIFIED. Remove the log_delta calls and the counts from the arm echo lines. If the raw counts are kept anywhere, label them uninterrupted telemetry, never evidence. Note the log arm also carries a reporting bug that disappears with it: log_delta echoes a status line to stdout together with the count, so A_LOGCOUNT and B_LOGCOUNT capture a two-line blob that the arm echo lines then print. Keep the nested log file itself for crash forensics (fix 3); drop the count as a measurement.

Also label B_PILL_DIFF honestly in the SUMMARY. The captured pill region is the 320x66 layer surface, mostly transparent margins showing the raw backdrop, so in arm B the pill region differs on most pairs from the backdrop alone: in my testsrc2 analysis the pill-surface region differed on 7/9 one-second steps while the corners differed on 9/9. B_PILL_DIFF will read high (roughly 25/31) under pure expected motion. Only B_PILL_ONLY is flicker evidence. The SUMMARY and the run report must say so, or a reader will misread B_PILL_DIFF as flicker.

## Question-by-question answers

### 1. Teardown destroys the nested log

Yes. `rm -rf "$RUN_DIR"` in teardown deletes `$RUN_DIR/hypr/$SIG/hyprland.log` on success and on failure. The surviving `$NEST/hyprland-wayland.log` is 54 lines (attempt 8) against 2842 lines in the per-instance log, so it is not a substitute. No forensic evidence of the nested compositor survives. Fix 3 (copy in teardown before removal, plus tee the runner's own stdout, plus timestamped frames) is a script patch; an external watcher cannot be relied on because the script's own rm races it. The copy must handle SIG empty (nest never started) gracefully.

### 2. Measurement exactness: geometry, scale, backdrop sample, pill movement

- Pill geometry from `hyprctl -j layers` is reliable in content (x, y, w, h, namespace all present) but the runner's parse of it is broken (fix 1). The coordinates are layout coordinates, matching grim -g (verified: the live monitor sits at 2464,902 in layers, and `grim -g "2464,902 200x200"` captured that region). Scale is 1 in the nest, so logical equals physical.
- The backdrop sample is safe for the real pill geometry (pill x=320..640, corner at 760..960, no overlap) but the code does not prove it: it checks only PILL_X >= 480, not the right or bottom edge (fix 7).
- If the pill moved between arms, arm B would capture the wrong region silently, since geometry is read once. Fix 7 (re-read before arm B) closes it.
- If the pill geometry were wrong, arm A would capture backdrop (or empty space) instead of the pill: with a static backdrop it would read 0 diffs and falsely report NOT reproduced, and with a moving backdrop it would read diffs and falsely report REPRODUCED. Geometry correctness is load-bearing, which is why fixes 1, 2 and 7 are all required, not optional.

### 3. The positive control and cmp on full-output PNG bytes

Byte comparison is the right test, and grim output is deterministic (evidence above: byte-identical repeat captures, PNG with only IHDR/IDAT/IEND, no tIME or text chunks). Two different frames cannot produce identical bytes unless the pixels are actually identical (lossless PNG, deterministic encoder), so the control cannot false-pass on distinct frames. Two identical frames cannot produce different bytes (no metadata chunks), so it cannot false-fail on identical pixels. The residual risks are not in cmp: mpv paused or looping badly would make frames identical, which the control correctly reports as a failure; the 10 second loop seam is untested and could repeat or drop a frame at the wrap, affecting at most 1-2 of 31 pairs, which the >= 3 threshold in fix 5 absorbs. The control's real gap is that it runs once before the pill starts and is never repeated (fix 6).

### 4. The callback/log arm

Not worth keeping as evidence. Calibration above: 6 matches in 4959 live-log lines, zero repaint events, 0 lines growth over a 32 second idle window. It could misleadingly "prove" quiet (0 in both arms is the expected outcome either way) or "prove" repainting (a nonzero count would be DRM error or startup lines, or grim's own screencopy activity, not pill repaints). It is also confounded between arms: arm B has mpv running and arm A does not, so any mpv-driven log lines would make B exceed A with zero flicker. Drop it (fix 9). The frame arm is primary, and after this fix it is the only arm.

### 5. Verdict lines

The three branches are exhaustive and mutually exclusive, no case prints two VERDICT lines, and the asymmetry clause is present in the branch 2 text. The branches are only as good as arm validity, which fixes 5, 6 and 7 supply. Branch 1's "decisive" claim holds once the pill-settle fix (8) and the threshold fix (5) are in, because the pill is verified static when idle (see "what checked out"). One gap the branches do not cover: a VOID arm (fix 6) has no verdict line at all, so add an explicit VOID line for that case instead of letting the script fall through to a misleading NOT reproduced.

### 6. Other measurement holes

- `pkill -x mpv` in arm A and teardown kills any mpv on the machine, and the `pgrep -x mpv` death check fails if a foreign mpv runs (fix 4).
- foot, started as a launch-gate client, is never closed and its window position is unchecked. If it overlaps the backdrop sample corner, or its cursor blinks, it could move pixels in the sample. The arm A backdrop validity check (fix 6) backstops this, but the cheap fix is to close foot after the launch gate, since it serves no measurement purpose. I did not verify foot's position or blink behavior; this is an unverified risk with a cheap mitigation, not a proven defect.
- The runner never re-validates that mpv is fullscreen in arm B. If mpv opens windowed, the corner sample could sit outside the video (black, static) and arm B would be void. The B_BG_DIFF gate (fix 6) catches exactly this, which is why the gate matters.
- The 300 second timeout has about 100 seconds of slack at worst-case durations (grim costs 0.028s per capture). Acceptable, but raise it to 600 seconds anyway, since the operator window is 30 minutes and the timeout is a needless tripwire.
- The verdict lines live only in SSH stdout (fix 3). The laptop SSH session dies at about 30 seconds (observed at 19:00), so the run must be detached and its output must be on disk.

## Evidence log (commands and outputs, all times +07, 2026-11-21)

- 18:54: read Y6 FINAL report and listed /tmp/y6-nested (runner 11648 bytes, 216 lines; backdrop.mp4 1991554 bytes, 10.0s).
- 18:55: read run-nested-wayland.sh, run-nested-pill.py, conf/hyprland-wayland.lua, conf/nested-visuals-hook.lua, conf/optics.lua via ssh-laptop.sh.
- 18:57: `hyprctl -j layers` live (with live signature env): structure `{monitor: {"levels": {"0": [...], "1": [...], "2": [...], "3": [...]}}}`, entries carry x, y, w, h, namespace, pid. Live monitor eDP-2 at layout 2464,902.
- 18:57: runner's exact layers-parse snippet against live layers JSON: `AttributeError: 'str' object has no attribute 'get'`, exit 1.
- 18:57: `grim -g "0,0,200,200" -o eDP-2`: `invalid geometry`; `grim -g "0,0 200x200" -o eDP-2`: `-o and -g are mutually exclusive`; `grim -g "2464,902 200x200"` (no -o): OK, 37981 bytes.
- 18:57: two `grim -g "2464,902 200x200"` captures 1s apart: byte-identical, md5 c3f9c1b9435f7be6c5192b806857cae8.
- 18:57: PNG chunk parse of the capture: chunks IHDR, IDAT x5, IEND. No tIME, no text chunks.
- 18:58: ffmpeg extracted 10 frames at 1 fps from backdrop.mp4; PIL per-second md5: full frame DIFF 9/9, corner-L DIFF 9/9, corner-R DIFF 9/9, pill-surface (320,0,640,66) DIFF 7/9, same on 2/9.
- 18:58: indicator.c: PILL_WIDTH 288.0, PILL_HEIGHT 38, SURFACE_WIDTH 320, SURFACE_HEIGHT 66, PILL_LEFT 16, PILL_TOP 16, top anchor only; entrance_progress starts 1.0, entrance only if CU_INDICATOR_ENTRANCE set; report_metrics only logs to stderr; painted callback only counts when idle. indicator.py pops CU_INDICATOR_ENTRANCE before spawning the native process.
- 18:59: `wc -l /tmp/y6-nested/hyprland8.log`: 54 lines, against Y6's 2842-line per-instance log for attempt 8. grim timing: 0.028s per capture. No mpv running at check time.
- 19:00: flock inheritance, PID-exact: subshell held the lock, spawned a setsid sleep child, exited; `flock -n -c true` failed (lock still held); after killing the child by PID it succeeded. Timeout TERM forwarding, PID-exact: TERM to timeout killed its sleep child.
- 19:00: live log pattern count: `grep -a -c -E "repaint|paint|commit|frame"` over /run/user/1000/hypr/11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795249046_1138556825/hyprland.log (4959 lines): 6 matches, zero repaint events (two GL extension dump lines, two "failed to commit" lines, two "Cannot commit" lines). The 35 second growth check in the same SSH call was cut by the session dying at about 30 seconds (exit 255, Broken pipe).
- 19:01-19:02: growth check rerun detached: start 4959 lines, pattern 6; after 32 seconds idle, end 4959 lines, pattern 6. Zero growth.

## Re-verify checklist before the run (Y6b)

1. Apply fixes 1 to 9. `bash -n` on the runner, `py_compile` on the pill script.
2. Fixed layers parse against live layers JSON: clean exit 1, no traceback. Against a synthetic nested-shaped JSON with a computer-use-indicator entry: prints the geometry.
3. One `grim -g "X,Y WxH"` call (no -o) with the exact geometry string the fixed script will pass.
4. Teardown copy: run the teardown function in a dry harness with a fake $RUN_DIR/hypr/$SIG/hyprland.log and confirm the copy lands under $NEST before removal.
5. Confirm the runner tees its own stdout to a timestamped file, and the detached invocation (nohup, output to that file) is recorded.
6. Confirm no `pkill -x mpv` and no `pkill -x` on a shared process name remains in the runner.

## Bottom line

BLOCK the run as written. The two fatal bugs (layers parse, grim capture) mean it aborts before measuring, and the teardown would destroy the nested log on the abort. The design underneath is sound, the positive control is valid, the pill is verified static when idle, and the verdict branches are exhaustive. Fix 1 to 9, re-verify with the checklist, then run in the next runner-quiet window with handover re-confirmed.
