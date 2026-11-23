-- Y6 nested Wayland probe config, v2 (U3) + Y6d v3.
-- Isolated nest, Wayland backend via the live compositor.
-- Launcher sets: WAYLAND_DISPLAY=/run/user/1000/wayland-1 (absolute parent socket),
-- XDG_RUNTIME_DIR=/tmp/y6-nested/run (nest runtime dir), no --socket flag:
-- the nest auto-names its socket and the launcher discovers it (F0, v3), so
-- the in-nest client pair is XDG_RUNTIME_DIR=/tmp/y6-nested/run plus
-- WAYLAND_DISPLAY=<discovered socket name>. Monitor: the nest virtual output 960x540@60.
-- Plugin: REBUILT hyprglass 1.1.1-cu.1 from worktree 03a57c4 (Y6e). Backup 1 stays the recorded dead path (dead ABI, see Y6c F1); do NOT put its .so path in a comment here, the ldd pre-flight greps the FIRST hyprglass.so path in this file.
-- Y6d: switch this load to the rebuilt plugin path once the rebuild lands;
-- do NOT run the measurement with backup 1 (it cannot load on this machine).
-- v2 change: NO autostart mpv/foot. Config-time exec children may inherit the
-- parent display instead of the nest socket (unverified), and foot serves no
-- measurement purpose. The launcher starts mpv with explicit nest env and a
-- recorded PID after the plugin and liquid checks pass.
hl.monitor({ output = "WAYLAND-1", mode = "960x540@60", position = "0x0", scale = 1 })
hl.plugin.load(os.getenv("HOME") .. "/.local/share/agent-computer-use/worktrees/hyprglass-03a57c4/hyprglass.so")
-- computer-use-visuals-begin
dofile("/tmp/y6-nested/conf/nested-visuals-hook.lua")
-- computer-use-visuals-end
