-- Y6 nested Wayland probe config, v2 (U3).
-- Isolated nest, Wayland backend via the live compositor.
-- Launcher sets: WAYLAND_DISPLAY=/run/user/1000/wayland-1 (absolute parent socket),
-- XDG_RUNTIME_DIR=/tmp/y6-nested/run (nest runtime dir), --socket wayland-y6
-- (nest socket pinned, so the in-nest client pair is XDG_RUNTIME_DIR=/tmp/y6-nested/run
-- plus WAYLAND_DISPLAY=wayland-y6). Monitor: the nest virtual output 960x540@60.
-- Plugin: backup 1 hyprglass.
-- v2 change: NO autostart mpv/foot. Config-time exec children may inherit the
-- parent display instead of wayland-y6 (unverified), and foot serves no
-- measurement purpose. The launcher starts mpv with explicit nest env and a
-- recorded PID after the plugin and liquid checks pass.
hl.monitor({ output = "WAYLAND-1", mode = "960x540@60", position = "0x0", scale = 1 })
hl.plugin.load("/home/james/.local/share/agent-computer-use/backups/full-1791544423/native/hyprglass.so")
-- computer-use-visuals-begin
dofile("/tmp/y6-nested/conf/nested-visuals-hook.lua")
-- computer-use-visuals-end
