# Detached terminal launch for broker executors

Choose a title unique to the worker and reuse it only for that worker. Launch
Kitty with `setsid -f`, then confirm exactly one matching row appears in
`hyprctl clients -j` before calling the broker start command. Keep that row's
window address for the later broker window lookup.

Example:

```sh
setsid -f kitty --single-instance=no --title pick2-term-pick2-worker-42 \
  >/tmp/pick2-worker-42-kitty.log 2>&1
hyprctl clients -j
```

Export the current GUI environment and active Hyprland instance signature
before running either command. Replace the example worker ID for every new
worker. Do not start a broker session if the title is absent or duplicated.

The controlled detach probes on 2026-11-19 confirmed the reason. After the
transient shell exited, the `nohup` Kitty form left no window or process. A
sleep probe showed `nohup` stayed in the shell's process group and died when
that group was terminated, while `setsid -f` gave its worker a separate
session and group. The `setsid -f` Kitty probe created the requested window;
it was closed by its PID immediately after inspection. The desktop returned to
Jarvis and Zen Browser only.
