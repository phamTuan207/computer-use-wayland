# Session indicator validation

Real-desktop checks, 2026-10-10: one Hyprland output, 1920×1200 logical pixels,
scale 1, normal transform. An isolated inert GTK4 fixture had no accounts or
network actions. Grim ran silently, without screenshot shortcuts or notifications.

- Visible top-center glass pill: 320×44 pixels, actual per-surface compositor
  blur, restrained directional rim and soft shadow. The normal cursor stays
  unchanged; no second cursor marker or global theme edits.
- Five repetitions of both window and screen capture: zero pixel differences
  in selected static fixture and pill regions versus the acknowledged hidden
  baseline, including the expanded shadow region. Capture times: 56, 47, 48,
  40, 39 ms. Focus stayed unchanged. Fixture focus-border animation settled
  before the baseline; hide/show correctness uses presentation ACKs, not sleeps.
- Fifteen input batches passed: click, literal Vietnamese, leading-dash text,
  normal-cursor click, scroll, three-button drag, Ctrl/Shift/Alt clicks,
  Ctrl scroll and typing after modifier release. Actual GTK events confirmed
  buttons, supported modifiers and final text, not merely command ACKs.
- A 300 ms left drag took 553 ms total versus 784 ms in the earlier CLI-query
  run. These are single samples, not statistical benchmarks. A repeat with glass
  took 552 ms, kept 68 safety queries, taking 10.933 ms combined, with zero read-query hyprctl
  subprocesses. Other batches used 24–36 queries.
- Removing the redundant 35 ms wait after the last click retained the hold,
  between-click interval, guards and final UI settlement. A live repeat passed
  all fifteen batches: single click 262 ms total (109 ms execution), compared
  with 306 ms before this change. The repeated drag took 557 ms. These are
  individual samples; no percentile or throughput claim is inferred.
- The public inert GTK demo passed seven real-input steps and actual event
  assertions: entry focus, literal text, click, double-click (three button
  activations total), visible drag, Ctrl click and scroll. Step times were
  255, 387, 278, 331, 548, 274 and 263 ms, excluding initial observation.
- Actual driver failure, wrapper SIGKILL, guardian SIGKILL, indicator SIGKILL
  and explicit cancellation: no living owned children, indicator layers or
  session snapshots after cleanup. Cancellation stayed latched in isolated
  test state. Glass-session cleanup measured 61–685 ms, not a guaranteed upper bound.

## Limits

Physical Escape input, multiple physical outputs, fractional scales, rotated
outputs and compositor loss have not been live-tested. Automated Escape binding
and cleanup checks do not prove a physical keypress. GTK4's public modifier flags
do not expose Mod5/AltGr; that needs separate XKB/protocol evidence, not a GTK
bit-128 claim. Other compositors require their own presentation-fence validation.
XKB checks confirm RALT is ISO_Level3_Shift and mask 128 activates Mod5, then
mask 0 releases it. These do not substitute for a live AltGr application check.
SIGTERM/SIGHUP during literal typing restore IME state in tests; SIGKILL cannot
run the typing driver's finally block, so hard-kill IME restoration is not proven.

Raw images, PIDs, window addresses and host paths stay outside the public repo.
Automated checks: `python3 -m unittest discover -s tests -p 'test_*.py'`,
`python3 tests/capture.py`, `python3 tests/no_magnifier.py`.
