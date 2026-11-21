# Worker Y6: hyprglass nested probe (option C for 2.2.3)

- Date: 2026-11-21, 18:17-18:28 +07
- Worker: Y6 (Muse subagent). Branch: todolist-push.
- Decision doc: docs/decision-2-2-3-hyprglass-test-20261121.md (Worker X). Owner chose C at 18:16.
- Status: DRAFT for council + redteam debate. Headless verdict is PROVEN. Wayland-nested is DESIGNED, not yet run.

## Verdict (one line)

HEADLESS nested Hyprland DOES NOT WORK on this machine: 5 launches, 5 identical crashes at CBackend::create(), root cause proven (Aquamarine needs a libseat seat even for headless, and no seat is obtainable while the live session holds it). The remaining option-C path is the nested WAYLAND backend (a small window on the live screen), which was designed but NOT run yet because Zen runners (Y4d rerun, Y8 E1) are active and a focus steal would pollute their observations.

## Evidence

### Attempt table (all times +07, 2026-11-21)

| # | Time | Env | Result | Crash evidence |
|---|------|-----|--------|----------------|
| 1 | ~18:20 | SSH, XDG_RUNTIME_DIR=/tmp/y6-nested/run, WAYLAND_DISPLAY=wayland-y6 (nonexistent), WLR_BACKENDS=headless | Crash, CBackend::create() failed | coredump 18:20:16 PID 215337 SIGABRT; report hyprlandCrashReport215337.txt |
| 2 | ~18:21 | SSH, same + AQ_BACKENDS=headless | Crash, identical | coredump 18:22:00 PID 217032 SIGABRT; report 217032 |
| 3 | ~18:22 | Hyprland child via hyprctl dispatch Lua os.execute (real graphical session), headless env | Crash, identical | coredump 18:22:35 PID 217712 SIGABRT; report 217712 |
| 4 | ~18:22 | SSH, AQ_BACKENDS=headless, debug.enable_stdout_logs=true in config | Crash, identical, no extra backend lines | coredump 18:23:03 PID 218283 SIGABRT; report 218283 |
| 5 | ~18:24 | SSH, headless env, seatd started as root (PID 219625, socket /run/seatd.sock, seat0) | Crash, identical + new detail (see below) | coredump PID 219789 SIGABRT; report 219789 |

No nested Hyprland process survived any attempt. No nested instance was ever alive to query.

### Root cause (proven from crash-report log tails)

Attempt 4/5 crash reports contain the Aquamarine log tail. Attempt 5 is the most complete:

```
DEBUG from aquamarine ]: Creating an Aquamarine backend!
ERR from aquamarine ]: [libseat] [libseat/backend/seatd.c:66] Could not connect to socket /run/seatd.sock: Permission denied
DEBUG from aquamarine ]: [libseat] [libseat/libseat.c:76] Backend 'seatd' failed to open seat, skipping
DEBUG from aquamarine ]: [libseat] [libseat/libseat.c:76] Backend 'logind' failed to open seat, skipping
ERR from aquamarine ]: [libseat] [libseat/libseat.c:79] No backend was able to open a seat
ERR from aquamarine ]: libseat: failed to open a seat
ERR from aquamarine ]: Failed to open a session
ERR from aquamarine ]: DRM Backend failed
DEBUG from aquamarine ]: Starting the Aquamarine backend!
DEBUG from aquamarine ]: Starting the Wayland backend!
ERR from aquamarine ]: Wayland backend cannot start: wl_display_connect failed (is a wayland compositor running?)
ERR from aquamarine ]: Requested backend (wayland) could not start, enabling fallbacks
ERR from aquamarine ]: Implementation wayland failed, erasing.
CRIT from aquamarine ]: Cannot open backend: no allocator available
```

Backtrace frame #11 is std::__throw_bad_any_cast inside CCompositor::initServer, after the seat failure. So:

1. Aquamarine creates a libseat seat BEFORE any backend, including headless. No seat, no compositor.
2. logind cannot open a seat for a second compositor: the live Hyprland already holds the session (logind TakeControl is exclusive). Proven by attempt 3 failing identically as a Hyprland child inside the real graphical session.
3. seatd does not rescue it: seatd is installed (/usr/bin/seatd) but was not running; after starting it as root, the nested process got EACCES connecting to /run/seatd.sock (socket perms srwxr-xr-x root root, seat0 created). The seatd path fails on permissions, not on absence.
4. Env vars do not select headless: libaquamarine.so.0.16.0 contains AQ_DRM_DEVICES but NO AQ_BACKENDS string, and WLR_BACKENDS is a wlroots variable Aquamarine does not read. Setting WAYLAND_DISPLAY to a nonexistent socket makes Aquamarine request the Wayland backend, which then fails to connect. The headless backend EXISTS in the library (CHeadlessBackend, CHeadlessOutput, HEADLESS-{} outputs) but was never reached in any attempt.

### Plugin file verification (done before launching)

- Backup 1 (decision-doc first path): /home/james/.local/share/agent-computer-use/backups/full-1791544423/native/hyprglass.so, 26,643,888 bytes, sha256 2671d4ac41941ca62ae8100fc3b57bf3153bf6def893334f3a8ecbc1ea0145d5. IDENTICAL (same sha256) to vendor/hyprglass/hyprglass.so.
- Backup 2: /home/james/.local/share/agent-computer-use/backups/sync-20261116-230254-783160-a9a24690/trees/native/hyprglass.so, 30,622,520 bytes, sha256 ddfff1c2f2cebb66e10b85a739beae0c7c562ccf9d78e3250647c07f8f31fa8b. DIFFERENT build, not used.
- Both are ELF 64-bit shared objects. nm -D shows __hyprland_api_get_client_hash and pluginAPIVersion. No version string is embedded (strings found only "Hyprnux"); the plugin version (expected 1.1.1-cu.1) is only visible via `hyprctl hyprglass status` AFTER a successful load, so it is UNVERIFIED.
- Installed tree has NO hyprglass .so in native/ (only patches and lua profiles), matching the decision doc.
- Live Hyprland is 0.57.2, commit 11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947. Terminals available for a test client: foot, kitty.
- Optics profile: native/hyprglass-local-optics.lua (repo), applied in the live setup via a Lua hook (scripts/setup.py _hook_body: dofile the profile when exactly one hyprglass of the right version is loaded). The profile sets layers.enabled=true with mask_mode contour for namespace computer-use-indicator, blur_strength 0.15, refraction 0.55. Readiness is defined by indicator.liquid_available: hyprglass status layers.enabled=true, layers.active=true, layers.reason=null, windows.enabled=false, subsurfaces.enabled=false.

### Crash-notification incident (18:23)

- A "Process crashed: Hyprland" desktop notification appeared ~18:23. Cause: my 5 nested attempts (coredumps 18:20:16, 18:22:00, 18:22:35, 18:23:03, ~18:25, all SIGABRT /usr/bin/Hyprland). Each crash wrote a report to /home/james/.cache/hyprland/hyprlandCrashReport*.txt.
- LIVE session verified unaffected at 18:23:33: PID 1515 alive, `hyprctl version` responds 0.57.2, `hyprctl clients` shows mapped windows (omarchy terminal 1574x816, special:herdrdrop). No live process was touched.
- Standing rule added 18:23 (owner): Muses watch crash notifications themselves, check logs themselves, fix themselves, do not bother him. Watchdog gained a coredump check.
- Cleanup done 18:28: seatd (my daemon, PID 219625) killed, /run/seatd.sock gone. Nested artifacts kept at /tmp/y6-nested/ (configs, 5 logs, runner script) as evidence.

## What was NOT tested

- The nested WAYLAND backend (nested Hyprland as a Wayland client of the live compositor, opening a small window). Not run because: (a) until 18:24 the owner was at the keyboard and a new window steals focus; (b) after 18:24 the owner left, but Zen runners Y4d (agy-q2 rerun) and Y8 (E1) started, one runner at a time, and a focus steal would pollute their hasFocus/visibility observations. The exact run is designed below.
- The hyprglass plugin was never loaded anywhere (no nested compositor ever lived). Plugin load, optics profile application, shader compile, and any pixel rendering are all UNVERIFIED.
- The 20/11 backdrop incident itself is NOT reproduced and NOT explained by this probe.

## Incident-reproduction design (Wayland-nested, NOT yet run)

Goal: reproduce the 20/11 flicker (overlay flicker in LIQUID mode with the animated backdrop) inside the nest, or prove the backdrop is not the cause.

### Preconditions (all must hold before launching)

1. No Zen runner active: check the flock on /home/james/.cache/agent-computer-use/zen_dom.lock is free AND no run_agyq2/run_live/E1 process is running on the laptop AND Muse confirms no runner is scheduled in the next 30 minutes.
2. Owner away (handover confirmed 18:24, still in force).
3. seatd NOT required (Wayland backend needs no seat).

### Launch (exact commands, via ssh-laptop.sh, detached)

Nested config /tmp/y6-nested/conf/hyprland-wayland.conf:
```
debug {
    enable_stdout_logs = true
}
monitor=WAYLAND-1,960x540@60,0x0,1
plugin=/home/james/.local/share/agent-computer-use/backups/full-1791544423/native/hyprglass.so
exec-once=foot --title y6-nested-glass-probe
```
Launch as a Hyprland child (real session env) so it connects to the live compositor:
```
export XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-1
export HYPRLAND_INSTANCE_SIGNATURE="$(ls /run/user/1000/hypr/ | head -1)"
hyprctl dispatch "function() os.execute(\"/tmp/y6-nested/run-nested-wayland.sh\") end"
```
where run-nested-wayland.sh sets XDG_RUNTIME_DIR=/tmp/y6-nested/run, WAYLAND_DISPLAY=wayland-1, unsets HYPRLAND_INSTANCE_SIGNATURE, and starts setsid nohup Hyprland --config /tmp/y6-nested/conf/hyprland-wayland.conf, logging to /tmp/y6-nested/hyprland-wayland.log. Expected: a 960x540 window titled Hyprland appears on the live screen. That window IS the nested compositor; do not click it.

### Checks inside the nest (env: XDG_RUNTIME_DIR=/tmp/y6-nested/run, WAYLAND_DISPLAY=wayland-y6, HYPRLAND_INSTANCE_SIGNATURE=<nested sig from /tmp/y6-nested/run/hypr/>)

1. `hyprctl -j plugin list` shows exactly one hyprglass entry; record its version.
2. `hyprctl -j hyprglass status` returns JSON; record version, versionCheck, active, shaders state, layers/windows/subsurface flags.
3. If version is 1.1.1-cu.1, apply the optics profile: source the lua profile in the nested config (add `source=/tmp/y6-nested/conf/optics.lua` AFTER the plugin line, where optics.lua is a copy of native/hyprglass-local-optics.lua) and reload the nested compositor, OR restart the nest with the source line included. Then re-check status until layers.active=true (wait up to 30 s; the live activation needed ~8 s for first-use shader compile).
4. Screenshot inside the nest: `grim -o HEADLESS-1` does not apply (Wayland backend output is WAYLAND-1); use `grim` with the nested WAYLAND_DISPLAY and confirm the output name from `hyprctl -j monitors` inside the nest. Capture the foot window over the backdrop.
5. Reproduction proper: run the indicator (pill) inside the nest the same way the live session does (scripts/indicator.py against the nested env, namespace computer-use-indicator), in LIQUID mode, then capture 32 frames with grim 1 s apart and count paint callbacks/commits (the live measurement method: 0 callbacks/commits over minutes means no flicker). REPRODUCED means: frames differ pixel-wise in the backdrop region while the pill is idle, or paint callbacks fire repeatedly with no input. NOT reproduced means: 32/32 frames identical and 0 callbacks, same as the live indicator measurement.

### GO/NO-GO for the reproduction

- GO (run the repro): nested starts, plugin loads, status shows version 1.1.1-cu.1 and layers.active=true after the profile.
- NO-GO, stop and report: nested crashes again, plugin refuses to load, version is not 1.1.1-cu.1 (profile mismatch), or shaders never become ready after 30 s.

## Recommended next step

Run the Wayland-nested attempt (section above) during the next runner-quiet window, with the preconditions checked first. If it works, run the reproduction design inside the nest. If the nested Wayland backend also fails, option C is dead and the choice is A (handover + live load, crash risk) vs D (skip repro, monitor via E1 logging).

## Council + redteam debate

(To be appended after the debate. Council A/B/C position papers and the redteam attack live in improvements/worker-y6-council-*.md and improvements/worker-y6-redteam.md.)

## Timed run log (evidence contract)

- 18:17-18:19: read decision doc + pending decisions; verified .so files exist (ls + file); Hyprland 0.57.2.
- 18:19-18:20: read activate-glass.py, activation_checks.py, optics lua, setup.py hook, liquid_available; launch attempt 1 (SSH, WLR_BACKENDS=headless) -> crash 18:20:16.
- 18:21: attempt 2 (SSH + AQ_BACKENDS=headless) -> crash 18:22:00. Read agy-hypr helper for the working dispatch form.
- 18:22: attempt 3 (Hyprland child, real session) -> crash 18:22:35. Attempt 4 (SSH, stdout logs on) -> crash 18:23:03.
- 18:23: desktop crash notification; verified live PID 1515 alive + hyprctl responsive; read full crash report 218283 (aquamarine log tail: no seat).
- 18:24: checked seatd installed but not running; libaquamarine has AQ_DRM_DEVICES, no AQ_BACKENDS; started seatd as root (PID 219625).
- 18:24-18:25: attempt 5 (SSH, seatd running) -> crash PID 219789; log tail shows seatd EACCES + DRM failed + Wayland failed + no allocator.
- 18:26: confirmed headless backend exists in libaquamarine (CHeadlessBackend symbols) but is never reached.
- 18:28: killed seatd, socket gone. Wrote this report.
