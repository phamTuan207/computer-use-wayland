# Council 1 (feasibility and execution): Y6b Wayland-nested probe

- Date: 2026-11-21, 18:54-19:00 +07 (wall clock, Asia/Ho_Chi_Minh)
- Council member: Member 1, feasibility and execution
- Subject: /tmp/y6-nested/run-nested-wayland.sh plus run-nested-pill.py, conf/hyprland-wayland.lua, conf/nested-visuals-hook.lua, conf/optics.lua
- Basis: Y6 final report (commit 482e4ba), read in full, plus live checks on the laptop via ssh-laptop.sh in this session
- Verdict: APPROVE-WITH-CHANGES (numbered changes in section 7; changes 1, 2, 3, 4, 5 and 6 are must-fix before any run; the rest are must-fix or recommended as marked)

## 1. One line verdict

The run cannot complete as written: the pill geometry parser crashes on real Hyprland 0.57.2 layers JSON (proven below), and the autostart mpv/foot environment is an unverified guess that decides whether the backdrop lands in the nest or on the live screen. Both are small fixes. With changes 1 to 6 applied and re-verified by the stated checks, the run is feasible end to end, and the 300s nest timeout is adequate but thin, so change 8 raises it.

## 2. What was checked, and what passed

Commands run in this session (all times +07, 2026-11-21):

- `ls -lt /run/user/1000/hypr/` at about 18:55: exactly one entry, signature 11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795249046_1138556825. This matches the hardcoded LIVE_SIG in the launcher exactly. PID 1515 alive, started Sat Nov 21 15:17:25, cmd `Hyprland --watchdog-fd 4`.
- `bash -n /tmp/y6-nested/run-nested-wayland.sh`: OK. `python3 -m py_compile /tmp/y6-nested/run-nested-pill.py`: OK.
- `diff /tmp/y6-nested/conf/optics.lua` against the laptop repo `native/hyprglass-local-optics.lua`: identical, no output.
- Hook file compared line by line with `scripts/setup.py` `_hook_body`: the loaded-plugin loop, `plugin.name`, `plugin.version`, version `1.1.1-cu.1`, and the `dofile` branch match exactly. Only the else branch differs, and that difference is documented in the hook file (prints a marker instead of running the live visuals.py command).
- `grep -n "def liquid_available" -A 40 scripts/indicator.py`: signature is `liquid_available(env, *, ready=False)`. The launcher calls `indicator.liquid_available(env, ready=True)`, which is correct. `_status` runs one `hyprctl -j hyprglass status` with `timeout=1`, so the liquid gate loop cannot overshoot its 60s deadline by more than about 1s per call. `_valid_liquid` requires schema 1, version `1.1.1-cu.1`, `versionCheck` match, `active` true, shaders `ready` when `ready=True`, layers enabled and active with reason None, windows and subsurfaces enabled False. So the liquid gate does enforce the version indirectly, even though the launcher never parses the version itself (see change 5).
- `grep -n "class Native" -A 60 scripts/indicator.py`: `Native(env)` takes one env dict, probes `_status`, spawns `native/indicator` (exists, 50320 bytes) or a PATH binary, replies `ready`, and when liquid is true calls `activation_checks.wait_for_profile(env, timeout=LIQUID_READY_TIMEOUT)` with `LIQUID_READY_TIMEOUT = 30.0`. `wait_for_profile` polls `hyprctl configerrors` plus `liquid_available(ready=True)` every 0.1s. The pill ready loop allows 45s, so a worst case Native of about 34s fits. `listen(state, token)` and `serve(server, native, token)` signatures match the pill's calls. The pill token is `secrets.token_hex(16)`, not a literal. `native/require-liquid` does not exist, so Native does not take the final-profile raise branch.
- Repo state at check time: branch `todolist-push`, HEAD 4500a186a586e888cec984cd76365346ae4a6f9b, working tree clean except untracked files, no modified tracked files. Correction to the task brief: the checkout is NOT a detached HEAD with uncommitted changes. It is 28 commits behind `origin/todolist-push`, so the pill imports the indicator.py of this checkout, not of origin. That is the frozen design as Y6 used it, but Y6b must not pull before the run, or the imported code changes under the frozen design.
- `strings` on libaquamarine: the string `Wayland backend!` and `Wayland backend cannot start: wl_display_connect failed` are present, so the launcher grep pattern `Wayland backend` will match a successful Wayland backend start. The grep is still non-gating (see change 3).
- `ffprobe` on backdrop.mp4: duration 10.000000s, as Y6 stated.
- Grim determinism, tested live at 18:58: two back-to-back full-output grim frames of the live screen are byte identical (both 583855 bytes, same md5 9518ff18a553eaf5b0c78edcf6490afa). A 1s-apart pair differed, but that was live screen motion (clock and animation), not encoder noise. Conclusion: grim plus cmp is a valid flicker detector on a static scene. The earlier region test with `-g "0,0,100,100"` failed with invalid geometry because live global coordinates start at the monitor offset (eDP-2 at x 2464, y 902), not at 0,0. That does not affect the nest, whose single output is at 0,0.
- Grim speed, live full 1920x1200 frame: 0.15s per frame. Nested 960x540 frames will be no slower in the capture step itself.
- `pgrep -x mpv` and `pgrep -x foot` at about 18:55: no process, exit 1 for both. No live mpv or foot to collide with at check time.
- `flock -n` test on the lock file at about 18:58: LOCK-FREE-NOW, no runner holds it right now.
- All preconditions binaries present: Hyprland, grim, mpv, foot, ffmpeg, python3.

## 3. Question 1: step by step trace of the launcher

Line references are to run-nested-wayland.sh as read at 18:54.

- Preconditions and handover gate: PASS. `Y6_HANDOVER_CONFIRMED=1` is enforced, live socket test, file existence loop, `command -v` checks. All files exist at check time.
- flock: PARTIAL FAIL, see section 5. `exec 9>"$LOCK"` then `flock -n 9` is correct flock mechanics, and the lock file exists (0 bytes, 17:48). But the premise is wrong: `run_agyq2.py` contains no flock or ZenDom reference at all (grep empty), and `run_live.py` also contains none. The only flock evidence found is a one-off Y4 launcher command in `improvements/worker-y4-run-log.md` (`flock -w 1800 ... -c "... run_agyq2.py all"`). A runner launched any other way is not blocked by this lock. Also `flock -w 1800` waits up to 30 minutes, it does not refuse, so even a wrapped runner would queue behind the nest run rather than fail. The flock is a useful tripwire, not a guarantee. Change 6 adds a process check.
- Lock fd inheritance: FAIL (minor, latent). Background jobs (`setsid nohup timeout 300 Hyprland ... &`, the pill, arm B mpv) inherit fd 9. flock locks are released only when every fd referring to that open file description closes. If teardown fails to kill a background child, that orphan keeps the lock held and blocks future runners indefinitely. Fix in change 4: close fd 9 in every background launch (`9>&-`).
- Nest launch: PASS with a caveat. `export WAYLAND_DISPLAY="$LIVE_SOCK"` (absolute parent socket path) plus `XDG_RUNTIME_DIR="$RUN_DIR"` plus `--socket wayland-y6` is the Council C design, and `wl_display_connect` accepts an absolute path. `unset HYPRLAND_INSTANCE_SIGNATURE` is correct. The stale socket `/tmp/y6-nested/run/wayland-1` from attempt 8 is not removed by the `rm -rf` line (it removes only `hypr`, `wayland-y6`, `wayland-y6.lock`), but it is harmless for the nest because every nest client uses `wayland-y6`. Change 13 removes it for cleanliness.
- Signature discovery: PASS. `rm -rf "$RUN_DIR/hypr"` then `ls -t "$RUN_DIR/hypr/"` picks the newest and only signature. At check time `/tmp/y6-nested/run/hypr/` does not exist (Y6 cleaned it), so the first `ls` failures in the 15s loop are expected and harmless.
- Wayland backend check: FAIL (non-gating). `grep -a "Wayland backend" "$LOG" | head -3` prints matches but its exit status is head's, and no `|| fail` follows. A nest that started on the wrong backend, or never logged the line, sails through to the socket check. Change 3 makes it gate.
- Nested socket check: PASS. `test -S "$RUN_DIR/wayland-y6"` is the right check for `--socket wayland-y6`.
- Plugin list and hyprglass status: PASS. `nest hyprctl -j plugin list` with grep for hyprglass, then `nest hyprctl -j hyprglass status` with `|| fail`, and the status JSON is saved and printed. But no version parse happens here (change 5).
- Liquid gate: PASS. Polls every 2s to a 60s deadline, correct `ready=True` semantics, correct env through `nest()`. One subtlety: the heredoc runs `nest python3 -`, and `nest()` passes stdin through `env`, which is correct.
- mpv/foot running checks: FAIL (false positive risk). `pgrep -x mpv` and `pgrep -x foot` are system-wide, and they check the wrong thing: they prove some mpv/foot exists, not that the nest autostart ones exist inside the nest. Combined with the exec env question in section 6, a live mpv would satisfy the check while the nest backdrop is absent. The positive control then fails and aborts the run, which is a safe direction, but it wastes the window and leaves a fullscreen mpv on the live screen until teardown. Change 2 removes the ambiguity at the source.
- Positive control: PASS in design. Two full-output grim frames 1s apart must differ. Grim determinism is proven above, so identical frames mean a truly static nest output.
- Pill start: PASS with one ordering bug. The launcher sets `Y6_NEST_SIG`, `XDG_RUNTIME_DIR`, `WAYLAND_DISPLAY`, `HYPRLAND_INSTANCE_SIGNATURE` for the pill process, matching what run-nested-pill.py reads. The pill sets the same values into the env it passes to `Native`. STATE_DIR is separate from live. But the pill prints `Y6-NEST-PILL: ready` BEFORE calling `native.command("show")`, so ready does not mean visible. If show fails, the launcher still proceeds and only fails later at layers. Change 7 swaps the order.
- Pill geometry: BLOCKING FAIL. Proven, see section 4. The parser assumes `hyprctl -j layers` returns `{monitor: {level: [entries]}}`. Real output is `{monitor: {"levels": {level: [entries]}}}`. The launcher parser iterates the string `"levels"` as if it were entries and crashes with AttributeError. Change 1 fixes it.
- Backdrop sample geometry: WEAK. `BACKDROP_GEOM` is chosen from `PILL_X` alone (480 threshold on a 960 wide output). It never checks the pill Y, W, or H, so a pill near the top could overlap the 200x200 corner sample. Change 11 picks a corner that does not intersect the pill rectangle in either axis.
- Arm A: PASS in design, with a note. `pkill -x mpv`, sleep 2, verify death, then 32 pill-region frames 1s apart. After mpv dies the nest output is black plus foot, which is static, so any pill-region change is flicker evidence. The arm is decisive, as Y6 claims.
- Arm B: PASS as data collection, FAIL as verdict logic. The mpv restart is launched correctly with explicit nest env, sleep 3, pgrep check, then 64 grim captures (pill plus backdrop per iteration). But the `B_PILL_ONLY` verdict is not clean flicker evidence: testsrc2 is spatially non-uniform, and the pill refracts the backdrop, so the pill region can legitimately change between two frames while the 200x200 corner sample happens to be identical (different regions of the pattern have different temporal periods). Change 9 downgrades the arm B only verdict to suggestive.
- Verdict lines: PARTIAL FAIL. The three branches cover all cases, but the third branch prints `REPRODUCED in animated arm only` from `B_PILL_ONLY > 0`, which overclaims for the reason above. Change 9.
- log_delta: FAIL (minor, evidence quality). `A_LOGCOUNT=$(log_delta ...)` captures all of log_delta stdout, including its `Y6-WAYLAND: log lines X -> Y during arm A` echo line, so `A_LOGCOUNT` is not a pure count. The printed summary line then contains that echo text embedded in it. Change 10 sends the echo to stderr. Also the grep pattern includes `frame`, which matches `framebuffer` and other unrelated lines, so the count is raw and inflated, as Y6 already labels it unverified. That part is acceptable if labelled, which it is.
- Teardown: PARTIAL FAIL, three holes. (a) `NESTED_PID` is the PID of `timeout`, not of Hyprland. A test on this VM confirmed GNU timeout forwards SIGTERM to its child (sleep child died when timeout was killed), so the common case works, but the second `kill -9 "$NESTED_PID"` then targets an already dead timeout process, never Hyprland itself. If Hyprland ignores or survives the forwarded TERM, it is orphaned. Change 4 records the real Hyprland PID. (b) `rm -rf "$RUN_DIR"` deletes `$RUN_DIR/hypr/$SIG/hyprland.log`, the per-instance nested log that was the key evidence in attempts 6 to 8, including the Wayland backend lines, plugin load lines, and the repaint pattern source. The stdout log `$NEST/hyprland-wayland.log` survives, but the per-instance log does not. Change 4 copies it out before removal. (c) Teardown runs on EXIT even on early failure, before the nest ever started, and still runs `pkill -x mpv` and `rm -rf "$RUN_DIR"`. A handover failure or a held flock would therefore kill an innocent live mpv and delete the runtime dir. Change 4 guards both. Teardown also never kills foot, so a nest foot (or a live foot, if the exec env question resolves the wrong way) survives the run. Change 2 removes foot or tracks it by PID.
- Live re-verification in teardown: PARTIAL FAIL. `ps -o pid,lstart,cmd -p 1515` hardcodes PID 1515, and `live hyprctl version 2>&1 | head -4 || echo FAILED` can never print FAILED because the pipeline exit status is head's. Change 12 resolves PID and signature at runtime; change 4 fixes the version check to not use a pipe, or to set pipefail.

## 4. The blocking bug, proven

Live layers JSON from Hyprland 0.57.2 (18:58, via the live signature):

- Top keys: `['eDP-2']`
- Monitor value keys: `['levels']`
- Running the launcher parser verbatim against that JSON raises `AttributeError: 'str' object has no attribute 'get'` at the `e.get("namespace")` line, exit 1. The launcher then prints `pill surface not found in nested layers`, even though the pill may be visible.
- The fixed form, iterating `levels["levels"]`, works on the same file and lists real entries (`omarchy-bar`, `omarchy-dock` with their x, y, w, h).

This bug alone guarantees the run aborts after the pill starts, having already spent the launch, plugin, liquid gate, and positive control time. It is not a judgment call. It is reproduced.

## 5. Question 2: hardcoded LIVE_SIG

Verified current: the hardcoded value `11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795249046_1138556825` matches `ls /run/user/1000/hypr/` exactly at 18:55, and PID 1515 is the live Hyprland, started 15:17:25. So the hardcoded value is NOT stale right now.

What breaks if it goes stale before Y6b runs: the `live()` helper would fail every live hyprctl call, so teardown would print `live hyprctl FAILED` (for the plugin list) and the version check would be masked by the head pipe, and the claim `live re-verified` in the report would be false even if the live session is healthy. The nest itself does not use LIVE_SIG, so the run would still proceed and then report a false live failure. The hardcoded PID 1515 has the same fragility: if the live session restarts, teardown prints `LIVE PID 1515 MISSING` wrongly. Change 12 resolves both at runtime. This is not a blocker today, but it is a must-fix because the run may happen hours after this check.

## 6. Question 3: timeout 300 versus the worst case

Worst case inside the 300s timeout clock (clock starts at nest launch):

- Signature wait max 15s, plus sleep 5s: 20s
- Plugin list plus status: about 2s
- Liquid gate max: 60s, plus under 1s overshoot per the 1s `_status` timeout: 61s
- Sleep 2s plus pgrep: 2s
- Positive control: 2 grim frames at about 0.15s each plus sleep 1s: about 2s
- Pill ready max: 45s
- Sleep 2s, layers about 1s: 3s
- Arm A: pkill plus sleep 2s, plus 32 times (grim about 0.15s plus sleep 1s): about 39s
- Arm B: sleep 3s, plus 32 times (2 grim frames about 0.3s plus sleep 1s): about 45s
- Verdict printing: under 1s
- Total worst case: about 219s. Margin under 300s: about 80s.

So 300s is ENOUGH at the measured grim speed, and the nominal run (fast gate, fast pill) is about 150s. The fragility is grim speed inside the nest: if nest grim frames cost 1s each (unproven, but software GL rendering through the parent could slow screencopy), the arms alone cost 160s instead of 84s and the total reaches about 295s, leaving about 5s of margin before timeout kills Hyprland mid arm B. Timeout expiry mid arm makes grim fail, which makes `capture()` fail, which aborts the run with no verdict. Change 8 raises timeout to 420s. It costs nothing: the script own gates still bound the total time, and timeout only kills a hung nest.

Note the pill timing fits: Native internal worst case is about 34s (reply timeout 3s plus wait_for_profile 30s plus spawn), inside the 45s pill loop. Note the liquid gate fits: each `liquid_available` call is a single hyprctl with a 1s timeout and no internal wait, so the 60s deadline is real.

## 7. Question 4: pill import path and liquid_available signature

Verified, PASS with two corrections to the brief:

- Import path: `sys.path.insert(0, "<laptop repo>/scripts")` in run-nested-pill.py (the literal path in the file points at the laptop repo checkout), then `import indicator`. The directory exists and contains indicator.py. The pill calls `indicator.listen(STATE_DIR, token)`, `indicator.Native(env)`, `native.command("show")`, and `indicator.serve(server, native, token)`, and all four signatures match the source read in this session.
- `liquid_available(env, ready=True)` matches the keyword-only signature `liquid_available(env, *, ready=False)`.
- Correction 1: the repo is on branch `todolist-push` at HEAD 4500a186, working tree clean except untracked files. It is NOT a detached HEAD with uncommitted changes, as the task brief states. Y6b must not pull (28 commits behind origin) before the run, or the imported indicator.py changes.
- Correction 2: the pill token line is `token = secrets.token_hex(16)` (the earlier tool output display redacted the token value itself, the file is correct).
- Optics file is byte identical to the live repo optics file, and the hook matches `setup.py` `_hook_body` except for the documented else branch. The frozen design matches the code the pill will actually load.

## 8. Question 5: system-wide pgrep and pkill

Risk at check time is LOW: no mpv and no foot are running now, and the owner is away, so a false positive from a live mpv is unlikely at the moment of the run. The structural risk is MEDIUM and remains:

- `pgrep -x mpv` and `pgrep -x foot` cannot tell a nest client from a live client. If the owner returns and plays media, or a live mpv exists, arm A `pkill -x mpv` kills the live player, and the pre-arm check passes for the wrong process.
- Teardown `pkill -x mpv` runs even when the nest never started, so an early failure (handover, flock, missing socket) still kills a live mpv.
- Foot is never killed in teardown at all. If foot landed on the live display, it stays there after the run.
- Do NOT fix this by adding `pkill -x indicator`: the live pill uses the same `native/indicator` binary, so that would kill the live pill too. Kill by recorded PID only.
- Change 2 and change 4 replace all system-wide process checks and kills with PID-scoped ones.

## 9. Question 6: other execution holes

- Autostart environment (highest risk after the parser bug): the config calls `hl.exec_cmd("mpv ...")` and `hl.exec_cmd("foot ...")` at top level during config evaluation, not inside a `hyprland.start` handler. Hyprland exports its own `WAYLAND_DISPLAY` and `HYPRLAND_INSTANCE_SIGNATURE` in `startCompositor`, which runs after config evaluation, so config-time exec children may inherit the parent display (`/run/user/1000/wayland-1`, absolute) instead of `wayland-y6`. The web and binary evidence found in this session confirms the export happens, but not that it applies to config-time exec children. If mpv lands on the live display, it plays fullscreen on the live screen, the nest positive control fails, and the run aborts with a live fullscreen video to clean up. The launcher own arm B mpv launch, with explicit nest env, shows the author already knows the explicit form is needed. Change 2 removes the autostart lines and launches mpv from the launcher with explicit nest env after the nest checks pass.
- Plugin load timing versus hook: `hl.plugin.load` is called, then `dofile` of the hook runs immediately after in the same config. If plugin loading is not synchronous, the hook sees count 0, prints the not-ready marker, never applies optics, and the liquid gate then NO-GOs for the wrong reason. The launcher never checks for the hook marker in the nest log. Safe direction (NO-GO, not a false verdict), but a possible false NO-GO. Change 5 includes checking the hook marker.
- Monitor name `WAYLAND-1`: unverified until the run. If the Wayland backend names its output differently, the monitor rule is ignored and `grim -o WAYLAND-1` fails, aborting the run. Safe failure, no fix needed, but Y6b should record the actual output name from `nest hyprctl -j monitors` before the control frames, so a failure is diagnosable.
- `NEST_LOG` path `$RUN_DIR/hypr/$SIG/hyprland.log` matches the attempt 6 to 8 layout, so the log_delta source path is correct, but the log is deleted by teardown (change 4).
- The `frames` directory is created by the launcher (`mkdir -p "$NEST/frames"`), so the missing `frames` directory at check time is not a bug. The `cache` directory is likewise created.
- No `set -e` is in effect, but every load-bearing step uses `|| fail` or an explicit test, except the Wayland backend grep (change 3) and the version parse (change 5). No other silent pass was found.
- The pill `serve_loop` thread catches exceptions and retries, and the main thread sleeps 3600 in a loop, so the pill survives a transient serve error. On SIGTERM the pill python dies without running its `finally: native.close()`, and the native indicator child was started with `start_new_session=True`, so it is not in the pill process group. It should exit when the nest display disconnects, but that is assumed, not verified. Teardown order (pill first, nest second) gives the nest death a chance to clean it. Note it in the run report if a stray indicator process remains after teardown.

## 10. Numbered changes (must-fix before the run unless marked recommended)

1. MUST-FIX, run-blocking: fix the pill geometry parser to handle the `levels` wrapper. Replace the loop body with iteration over `data[monitor]["levels"]`, for example by changing the inner loop to iterate `levels.get("levels", levels).items()` and then entries, or by restructuring to `for level_entries in data[monitor]["levels"].values(): for e in level_entries:`. Re-verify by running the exact parser snippet against live `hyprctl -j layers` output and confirming it finds a layer entry instead of raising AttributeError.
2. MUST-FIX, highest risk: remove `hl.exec_cmd("mpv ...")` and `hl.exec_cmd("foot ...")` from conf/hyprland-wayland.lua. Launch mpv from the launcher with explicit nest env after the plugin and liquid checks pass, record its PID in a variable, and use that PID for the arm A kill and the arm B restart check. Remove foot entirely (no measurement uses it) or launch it the same explicit way with a recorded PID and a teardown kill by that PID. Replace the `pgrep -x mpv` and `pgrep -x foot` checks with PID checks (`kill -0 $MPV_PID`).
3. MUST-FIX: make the Wayland backend check gate the run. Replace `grep -a "Wayland backend" "$LOG" | head -3` with `grep -a -q "Wayland backend" "$LOG" || fail "Wayland backend did not start in nested log"`, keeping a separate `grep -a "Wayland backend" "$LOG" | head -3` line only for display.
4. MUST-FIX: fix teardown. (a) Copy `$RUN_DIR/hypr/$SIG/hyprland.log` to `$NEST/nest-hyprland.log` before `rm -rf "$RUN_DIR"`. (b) Guard `pkill` and `rm -rf "$RUN_DIR"` so they run only if the nest was actually started (`[ -n "$NESTED_PID" ]`), so an early failure cannot kill a live mpv or delete the runtime dir. (c) Record the real nested Hyprland PID (child of the timeout process, via `pgrep -P "$NESTED_PID" -x Hyprland` after signature discovery, or drop the `timeout` wrapper and enforce the time budget in the script) and kill that PID in teardown, not only the timeout PID. (d) Close fd 9 in every background launch (`9>&-` on the setsid lines) so a leaked child cannot hold the flock. (e) Fix the live version check so a failure is detectable: do not pipe through head, or add pipefail, for example `live hyprctl version > /tmp/live-version.txt 2>&1 || echo "Y6-WAYLAND: live hyprctl FAILED"`.
5. MUST-FIX: parse the hyprglass status JSON explicitly before the liquid gate. Fail fast with the observed version recorded if `version` is not `1.1.1-cu.1` or `versionCheck` is not `match`, instead of burning the full 60s liquid gate on a version mismatch. Also grep the nested log for the `Y6-NEST-HOOK: hyprglass not ready` marker after the plugin check and record it, so a hook timing miss is diagnosable instead of silent.
6. MUST-FIX: do not rely on flock alone for runner quiet. Before acquiring the lock, check for live runner processes (`pgrep -af "run_agyq2.py|run_live.py|run_agyq.py"` and a geckodriver check) and abort if any are present. Correct the comment: `run_agyq2.py` has no flock preflight, the only flock wrapper found is the one-off Y4 launcher command, and `flock -w 1800` waits rather than refuses. Handover re-confirmation at run time remains the real gate.
7. MUST-FIX, small: in run-nested-pill.py, call `native.command("show")` BEFORE printing `Y6-NEST-PILL: ready`, and print ready only after show succeeds, so the launcher ready signal means visible.
8. RECOMMENDED, cheap insurance: raise `timeout 300` to `timeout 420`. Worst case computed in section 6 is about 219s, so 300s passes at measured grim speed, but 420s removes the mid arm kill risk if nest grim frames are slower.
9. MUST-FIX, verdict honesty: downgrade the arm B only verdict. If `A_DIFF` is 0 and `B_PILL_ONLY` is greater than 0, print `SUGGESTIVE in animated arm only (pill changed while backdrop sample was identical; not decisive, see testsrc2 spatial non-uniformity plus refraction)` and do NOT print `REPRODUCED`. The decisive verdict rests on arm A only.
10. RECOMMENDED: fix log_delta so the count is a pure count. Send its `log lines X -> Y` echo to stderr, so `A_LOGCOUNT` and `B_LOGCOUNT` capture only the grep count number.
11. RECOMMENDED: choose `BACKDROP_GEOM` from the full pill rectangle, not `PILL_X` alone. Pick the 200x200 corner whose rectangle does not intersect the pill rectangle in either axis, and fail if no corner is clear.
12. MUST-FIX: resolve the live signature and live PID at runtime instead of hardcoding them. Derive `LIVE_SIG` from `ls -t /run/user/1000/hypr/ | head -1` and the live PID from `pgrep -x Hyprland`, fail if either is ambiguous (zero or more than one), and use those values in `live()` and teardown. Keep the currently verified values only as a comment.
13. RECOMMENDED: extend the pre-launch cleanup to remove the stale `/tmp/y6-nested/run/wayland-1` and `wayland-1.lock` left by attempt 8, so a future debug cannot mistake a dead socket for a live one.
14. RECOMMENDED: record the actual nest output name with `nest hyprctl -j monitors` after signature discovery and before the control frames, and use that name in the grim `-o` calls instead of assuming `WAYLAND-1`, or at least log it so a monitor name mismatch is diagnosable.
15. RECOMMENDED: in the run report, record the post-teardown process check for a stray native indicator child (from the pill) and for any surviving nested Hyprland, since teardown kills the pill python but not its separate-session native child directly.

## 11. Re-verification required after the changes

- `bash -n` on the edited launcher, `python3 -m py_compile` on the edited pill.
- Run the fixed geometry parser verbatim against live `hyprctl -j layers` output and confirm no AttributeError and a real entry is found.
- Confirm `LIVE_SIG` and live PID are resolved at runtime, not hardcoded, by reading the edited script.
- No second council is needed for these mechanical edits if all of changes 1 to 9 are applied as written. If change 2 is applied in a different form (for example keeping config autostart with an env wrapper), re-review that part before running, because the autostart environment is the one point where this council could not prove the behaviour from source.

## 12. Evidence log (commands and outputs, condensed)

- 18:54: read Y6 final report (commit 482e4ba) and the launcher (11,648 bytes) in full.
- 18:55: `ls /run/user/1000/hypr/` shows the single live signature matching LIVE_SIG; `ps -p 1515` shows Hyprland started 15:17:25; `pgrep -x mpv` and `pgrep -x foot` both exit 1; lock file exists.
- 18:56: indicator.py read: `liquid_available(env, *, ready=False)`, `_status` timeout 1, `_valid_liquid` version and shader rules, `Native` wait_for_profile 30s, `listen` and `serve` signatures; setup.py `_hook_body` matches the nested hook; optics diff identical; repo HEAD 4500a186 on todolist-push, clean except untracked, 28 behind origin.
- 18:57: strings on libaquamarine show `Wayland backend!`; grim live full frame 0.15s; two 1s-apart live frames differ (screen motion); `grep flock run_agyq2.py` empty.
- 18:58: clean grim test, two back-to-back full frames byte identical (583855 bytes, md5 9518ff18a553eaf5b0c78edcf6490afa); `flock -n` on the lock file reports free; `grep -rn flock` in y5-tests shows only the Y4 one-off wrapper and unrelated locks.
- 18:59: parser proof: launcher parser verbatim raises AttributeError on live layers JSON, fixed parser lists real entries; `bash -n` OK, `py_compile` OK.
- 19:00: timeout forwarding test on this VM: killing a `timeout 300 sleep` process killed its sleep child, confirming the common teardown case works while the kill target is still the wrong PID.

## 13. What this council did not verify

- Whether Hyprland config-time `hl.exec_cmd` children inherit the parent or the nest `WAYLAND_DISPLAY`. The source evidence found confirms the export in `startCompositor` but not its application to config-time exec. Change 2 removes the need to know.
- Whether `hl.plugin.load` is synchronous with respect to the hook `dofile` that follows it in the same config. Change 5 makes a miss diagnosable.
- The actual nest output name (`WAYLAND-1` assumed). Change 14 records it.
- No nested Hyprland was launched in this review, so no new crash was produced and no live session state was changed except read-only grim screenshots (files removed after the test) and read-only hyprctl queries.
