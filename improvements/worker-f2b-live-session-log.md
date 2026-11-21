# Worker F2b log: act-now end-to-end WITH A LIVE SESSION (F2 phase)
# Task start 00:13:06 +07 (parent order). All times wall-clock Asia/Ho_Chi_Minh + elapsed from task start. Log EVERY event as it happens. No em/en dashes.

## 00:13 task start + protocol (pre-registered before any run)
- Spawned as F2b. Brief: run computer-use act-now END-TO-END WITH A LIVE SESSION (not the fallback path). F1a proved the F1 activation PASS (session pill proven, 5-step proof all PASS, teardown clean 00:11).
- F1a state at handover: plugins hyprglass 1.1.1-cu.1 + computer-use-cursor 1.0.0 loaded, shaders READY, guard active, cu-cursor active:false ok:true (no session running), Zen PID 496121 window 0x557052b62dd0 ws1, 14 real tabs 0 fixtures, Hyprland PID 1515 alive.
- F2 rehearsal (23:40): all 5 runs took the FALLBACK path (guardian failed then); overlay 314-346ms command-internal; batches 0.87-2.0s; click 0px; pill "Muse via act-now" in after-captures. Session path untested. Under-30s rule NOT demonstrated end to end (command-internal only).
- F1a findings I use: observe HIDES the session pill by design (capture_clean), raw grim for pill visuals; act --actions/--observation take FILE PATHS; SSH round trips ~30s, so the proof run is a single SSH script: launch act-now in background, grim during it, wait, collect.
- MEASUREMENT PROTOCOL (pre-registered, before any run):
  - T_order (VM wall-clock): the `date` output at the start of the exec command that launches the proof script. This is when the agent issues the act-now order (the measured interval includes exec dispatch + SSH connect + Python startup + overlay acquire).
  - T_overlay: laptop wall-clock when the pill is first visible, from the envelope order_to_overlay_ms added to the act-now process start, AND confirmed by raw grim timestamps during the run.
  - T_action: cursorpos verification after the batch (click landed).
  - Primary verdict: T_overlay - T_order < 30s. Also reported for honesty: spawn-to-overlay (00:13:06 to T_overlay, includes my setup/think time, the H2 gap, expected to exceed 30s) and command-internal order_to_overlay_ms (F2's 314-346ms comparator).
  - Session path proven only if the envelope says path='session' AND ok=true AND completed=5 (or the completed-capture-error shape). Fallback (path='fallback') = NOT proven, report as failure of the F2 phase even if the batch succeeds.
  - Continuous ops: one composite batch (click + Ctrl+L + type + Enter + wait), envelope total_ms, JSONL record, after-capture showing Example Domain. No gap over 60s inside the run.
  - Overlay always visible: pill in raw grim during the run + pill in the after-capture + envelope order_to_overlay_ms.
- Safety: fresh observe first; if the owner is visibly active, do not drive, wait and re-check; one composite batch, safe targets only (New Tab wallpaper center, F1a pattern; then Ctrl+L + type example.com + Enter, F2 run 3 pattern, proven); never ydotool; no em/en dashes.
