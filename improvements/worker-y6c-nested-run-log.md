# Worker Y6c log: Wayland-nested v2 run (todolist 2.2.3 I11)

- Worker: Y6c (Muse live runner). Branch: todolist-push.
- Design: v2 runner /tmp/y6-nested/run-nested-wayland.sh (md5 8cd00a16d417bc49595ebc6cb775ce99), pill run-nested-pill.py (3488c1812b0cd70b0629fb8c14fc5ae2), conf hyprland-wayland.lua (0e0dd3f63d50ad3a12d1f6a962f06098). Reference copies in the repo match the laptop files exactly (verified 20:39).
- GO order: Muse spawn 20:39 +07, Y6_HANDOVER_CONFIRMED=1. Owner handover 18:24 stands (out of house, busy; any signal saying the user is using the machine is fake). No A1 arm scheduled in the window (A1 stays frozen).
- Slot: Y11b finished metrics proof PASS 20:38 (commit 8e4331c) and released the slot. Y6c was the only live runner.

## Verdict: NO VERDICT (run blocked at launch, question unanswered)

The v2 runner cannot start the nested Hyprland (finding F0, proven live), and the pinned plugin binary cannot load on this machine at all (finding F1, proven live). The pill never started, no arm ran, no frame was captured. This is NOT "NOT reproduced": the measurement never happened. Option C is NOT dead by exhaustion: the Wayland-nested mechanism itself works (probe 1: nest starts, Wayland backend runs, monitor WAYLAND-1 exists). What is dead is the pinned plugin binary, which needs a rebuild against the current libraries. A retry needs a fixed launcher plus a loadable plugin, then a re-review before running (the adjudication requires review for any deviation from the frozen design).

## Timeline (Asia/Ho_Chi_Minh, 2026-11-21, wall clock + elapsed from run start)

- 20:39:30: pre-run checks. Live Hyprland PID 1515 alive (started 15:17:25), single signature 11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795249046_1138556825. Zen PID 27958 alive. No runner processes, no geckodriver, no mpv, no foot. Lock free. Laptop repo branch todolist-push at 4500a18, tracked tree clean (only the known untracked files). vkms loaded, refcount 2, untouched. Runner-quiet gate: PASS.
- 20:40:42 (T+0s): v2 runner launched detached (setsid nohup, Y6_HANDOVER_CONFIRMED=1), PID 348727, run log /tmp/y6-nested/run-20261121-204042.log.
- 20:40:42-20:40:58: runner passed its own preconditions (live sig/pid resolved, runner-quiet process check OK, flock held), launched the nested Hyprland (timeout wrapper PID 348752), then failed: "no nested instance signature after 15s". Teardown ran, verified live PID 1515 + hyprctl + hyprbars only, lock free, no strays. Runner exit 1. Total run 18s.
- 20:41-20:43: diagnosis. Nested log /tmp/y6-nested/hyprland-wayland.log contains only the startup error (see F0).
- 20:43:27-20:44:12: probe 1 (drop --socket, timeout 30). Nest started, see below.
- 20:44:44-20:45:44: probe 2 (drop --socket, timeout 60). Plugin list empty at 20s, see F1.
- 20:46:02-20:48:02: probe 3 (drop --socket, timeout 120). hyprctl plugin load error, see F1. Nest killed by timeout 20:48:02.
- 20:48:11: final state verified: only live Hyprland PID 1515, no mpv, no foot, lock free, run dir cleaned. Live session untouched throughout.

## Finding F0 (fatal, launch): --socket without --wayland-fd is a hard startup error

Nested log (hyprland-wayland.log, 266 bytes, in improvements/y6c-evidence/):

```
DEBUG ]: [main] User-specified config location: '/tmp/y6-nested/conf/hyprland-wayland.lua'
[ ERROR ] Hyprland was launched with only one of --socket and --wayland-fd.
          Hint: Pass both --socket and --wayland-fd to perform Wayland socket handover.
```

`Hyprland --help` confirms: `--socket NAME` sets the Wayland socket name (for Wayland socket handover), `--wayland-fd FD` sets the Wayland socket fd (for handover). In 0.57.2, passing exactly one of them exits immediately. The v2 launch line passes `--socket wayland-y6` with no `--wayland-fd`, so the nest dies before creating a signature, and the runner fails at the 15s signature wait.

Why no council caught it: the v1 Wayland script (same launch line) was NEVER executed. The 8 DRM attempts used run-nested.sh, which launches `Hyprland --config .../hyprland.conf` with NO --socket, so they passed arg parsing and died later at DRM initServer (SIGABRT). The v1 Wayland design was reviewed but never run, so this validation was never hit.

## Probe 1 (F0 fix candidate, proven): dropping --socket starts the nest

Launch: same env as v2 (XDG_RUNTIME_DIR=/tmp/y6-nested/run, WAYLAND_DISPLAY=/run/user/1000/wayland-1, no HYPRLAND_INSTANCE_SIGNATURE), `timeout 30 Hyprland --config /tmp/y6-nested/conf/hyprland-wayland.lua`, no --socket. Result at 12s: nested Hyprland PID 350555 running, signature dir created (11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_1795268607_1015342488), Wayland socket auto-named `wayland-1` in /tmp/y6-nested/run/. Per-instance log: "Starting the Wayland backend!" (aquamarine). Killed by timeout at ~30s; only live 1515 remained after.

Consequence for a fix: the nest Wayland socket is auto-named `wayland-1`, NOT `wayland-y6`. The runner hardcodes WAYLAND_DISPLAY=wayland-y6 in nest(), mpv launches, and the pill launch. A fix must discover the socket name after launch (ls $RUN_DIR/wayland-* excluding *.lock) and use it everywhere, or implement proper handover (pre-create the socket, pass its fd as --wayland-fd). Drop---socket alone is not enough.

## Finding F1 (fatal, deeper): hyprglass 1.1.1-cu.1 cannot load on this machine

Probe 2 (nest up 20s, no --socket): nested `hyprctl -j plugin list` returned `[]`; `hyprctl -j hyprglass status` returned `unknown request`. Nested monitors worked (WAYLAND-1, width 924). Per-instance log shows only the hook marker `Y6-NEST-HOOK: hyprglass not ready (count=0 version=nil)`; the config `hl.plugin.load()` call fails silently (no load error in the log).

Probe 3: nested `hyprctl plugin load ~/.local/share/agent-computer-use/backups/full-1791544423/native/hyprglass.so` returned:

```
Plugin .../hyprglass.so could not be loaded: libaquamarine.so.14: cannot open shared object file: No such file or directory
```

ldd on backup 1: `libaquamarine.so.14 => not found`, `libhyprgraphics.so.4 => not found`. The system has libaquamarine.so.15 (0.16.0) and libhyprgraphics.so.5 (0.6.0) only. Every hyprglass binary on disk shares the dead ABI: vendor copy (Oct 6), backup 1 (Oct 6), 3 sync-20261116 backups (Oct 10), and 6 hashed variants (sampled 2/6, same result). The live session also loads no hyprglass (live plugin list is hyprbars only; live hyprland config has no hyprglass plugin lines). This explains the standing note "plugin version 1.1.1-cu.1 still UNVERIFIED (never loaded anywhere)".

Fix direction (not attempted by Y6c): rebuild hyprglass from the vendor source (src/, Makefile, hyprpm.toml exist under ~/.local/share/agent-computer-use/vendor/hyprglass/) against the current aquamarine .15 / hyprgraphics .5, or find another loadable build. Restoring the old .so.14/.so.4 libraries would break the current Hyprland and is not recommended. A rebuilt plugin still needs its version verified as 1.1.1-cu.1 (or the design re-pinned) before any retry.

## Finding U5b (runner bug): the Wayland-backend gate greps the wrong log

The v2 script gates on `grep -a -q "Wayland backend" "$LOG"` where $LOG is the stdout redirect (hyprland-wayland.log). On a healthy start that line goes ONLY to the per-instance log: probe 1 and probe 2 stdout logs contain 0 matches, while the per-instance log has "Starting the Wayland backend!". Reason: postConfigReload sets debug.enable_stdout_logs = 0 ("Disabling stdout logs ... Further logs will be written to /tmp/y6-nested/run/hypr/<sig>/hyprland.log"). Fix: grep $NEST_LOG (the per-instance log, available after signature discovery) instead of $LOG, or the gate false-NO-GOs a healthy nest.

## Related observations

- U6/U18: the hook marker check would correctly NO-GO a plugin-less nest (count=0), but with the wrong diagnosis (hook race vs missing libs). The U18 classification should include the loader error from `hyprctl plugin load` (or ldd) before declaring the cause.
- XWayland `(EE) could not connect to wayland server` appears in probe stdout logs. No X clients are used by the measurement (mpv and the pill are Wayland-native), so this is likely harmless; noted, not investigated.
- libseat errors in the per-instance log ("failed to open a seat", "DRM Backend failed") are expected for a Wayland-backend nest with no seat; the Wayland backend started anyway.
- The v2 runner teardown worked correctly (live re-verified, lock free, no strays). The v2 run's own runner-quiet process check and flock behaved as designed.
- The nested monitor reported width 924, not the configured 960. The nest output is sized by the live compositor window; geometry must be read live (the runner already does this via layers JSON), not assumed.
- Y13r BLOCK noted a "Y6c gate blind" HIGH (Y13's runner-quiet check does not see the Y6c run). Y6c's run is over and the slot is free again (verified 20:48:11: only PID 1515, lock free), so the concern is moot for this window; Y13's gate still needs its own fix per Y13f.

## Evidence

- improvements/y6c-evidence/run-20261121-204042.log (v2 run log, 18s, FAIL at signature wait, clean teardown)
- improvements/y6c-evidence/hyprland-wayland.log (F0 error, 266 bytes)
- improvements/y6c-evidence/y6c-launch-20261121-2040.log (launch wrapper)
- improvements/y6c-evidence/probe-nosocket.log + probe2-nosocket.log + probe3-nosocket.log (probe stdout logs)
- improvements/y6c-evidence/probe2-hyprland.log + probe3-hyprland.log (per-instance logs; backend start, hook marker, libseat lines)
- Laptop originals remain at /tmp/y6-nested/ (same filenames).

## What Y6c did NOT do

- Did not attempt option A (load backup hyprglass into the live compositor) or option B (hyprland.conf + reboot). Per the brief, those are Muse's decision after this report.
- Did not fix the runner, rebuild the plugin, or retry the measurement run. The fixes (F0 launch line + socket discovery, F1 plugin rebuild, U5b log path) change the frozen design and need review before any retry, per the Y6b adjudication.
- Did not touch the live Hyprland session (PID 1515), Zen (PID 27958), vkms (still loaded, refcount 2), or the laptop repo (branch todolist-push at 4500a18, no pull).
- Did not spawn the next runner. The slot is free; Y13 codex-y5 runs next after its re-review clears, spawned by Muse.
