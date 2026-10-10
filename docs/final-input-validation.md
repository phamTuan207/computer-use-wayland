# Installed input validation

A bounded run against the inert GTK fixture in `tests/demo.py` used the installed
engine through `tests/demo_driver.py`. Real GTK events confirmed literal Vietnamese
text, three button activations, drag displacement, Ctrl-assisted click and scrolling.
Per-step elapsed times, including guards and capture: entry focus 224.7 ms, literal
text 337.9 ms, click 214.4 ms, double click 281.4 ms, requested 300 ms drag 488.6 ms,
Ctrl-click 208.4 ms and scroll 208.7 ms. These are single samples, not latency percentiles.
The driver restored prior focus and its session removed the indicator.

Three separate installed-engine quiet sessions completed with zero startup failures,
refusals or action errors. Median CLI observation was 225.7 ms, no-input act 417.7 ms
and complete session 1025.5 ms. Capture times were 65/70/69 ms. These include process
startup and full-screen capture; they are not native pointer round-trip latency.

The current source suite passed 178 tests in 21.317 seconds with pinned patch
applicability enabled and no skips. The new adaptive-ink backend passed isolated
compositor white/forest rendering and clean-hide comparisons, but is only staged
for the host: it must be activated in a fresh compositor session. Do not overwrite,
unload or hot-reload the currently mapped module. Mixed-backdrop contrast, physical
multi-monitor scaling and long-duration dynamic-background behavior remain unverified.

For observation efficiency, prefer app APIs or DOM when available; use desktop
cropped screenshots where necessary, grouping predictable actions within a checkpoint.
Keep preflight, cancellation and capture-clean fences. Image pixel counts and JSON
bytes are useful proxies, not measurements of billed model tokens or vision accuracy.
