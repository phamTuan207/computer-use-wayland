# Session indicator validation

Real-desktop checks, 2026-10-10: one Hyprland output, 1920×1200 logical pixels,
scale 1, normal transform. An isolated inert GTK4 fixture had no accounts or
network actions. Grim ran silently, without screenshot shortcuts or notifications.

## Old style, 320×44 — historical

Every measurement in this section was taken with the previous 320×44 pill. It
describes that style only and does not validate the experimental style below.

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

## Installed release checks

The installed command's symlink was resolved before smoke tests. All tracked
release sources matched the repository, excluding an unrelated uncommitted
historical validation edit. Helpers were rebuilt in the installed directory.
The installed copy passed 127 unit tests in 20.225 seconds, capture/adapter
regressions, the no-magnifier check and all seven real-input demo assertions.
Five installed crash/cancel cases also had zero pixel difference from the
pre-session baseline in the expanded pill/shadow region after cleanup, as well
as zero owned living children, layers or snapshots. Measured cleanup was
62–726 ms in that run; cancellation remained latched in isolated test state.
The installed copy also repeated both clean-capture paths five times with
zero selected-region pixel differences and unchanged focus: 66, 64, 58, 40,
39 ms. These are capture samples, not throughput or percentile statistics.

## Experimental feature — liquid backdrop

Not part of the installed release above. Separate from it, this section covers the opt-in
compositor backend only.

Design, read from source: a compact top-only surface with a left-anchored pill; light neutral body
with a white wash, a directional rim gradient and four low-alpha shadow rings, and no Escape keycap
or divider, only plain `Esc` text when the binding is installed and the pill is wide enough. When the
backend is active the foreground body fill and both wash stops pass 0, so this surface draws only the
lettering, the dot, the faint rim and the shadow rings while the compositor draws the material
underneath; the non-liquid fallback still draws the earlier light plate. A too-small output now exits
with status 2 instead of drawing an unreadable pill.

Measured, by tier:

- **Mocked unit tests** — the full suite covers lifecycle, backend-status detection and the build
  script. Logic only, never pixels.
- **Real nested compositor runs** — hide/show presentation acknowledgements in the tens of
  milliseconds; unloading the backend stops the native helper; captures with the indicator hidden are
  pixel-identical to the baseline across the expanded pill and shadow area.
- **Displacement is geometrically real.** A forced-offset comparison on a static fixture measures
  horizontal displacement directly: an 8 px sample offset reads back as lag −8 with correlation 0.9236
  to 0.9288 across the measured rows, and a 16 px offset reads back at magnitude 16 with correlation
  0.9214 to 0.9262. Because the fixture repeats every 32 px, −16 and +16 describe the same shift and
  only the magnitude is meaningful. These are static-fixture measurements: they do not show that a
  moving backdrop is re-sampled, which is separately pending.
- **An earlier zero result was a measurement error, not a defect.** A previous run reported no
  displacement anywhere; that came from a flawed metric, not from the effect being absent. A later
  on/off comparison shows displacement varying by row — about −14 to −15 px near the top of the pill
  and about +14 px near the bottom, with correlations from 0.66 to 0.86, where +14 is the same 32 px
  alias. Displacement therefore differs across the pill rather than being uniform.
- **Surface geometry** — a real layer-shell query in the nested compositor reports the compact
  surface at 320×66, positioned at the top centre of a 1280-wide monitor.
- **Not measured** — a physical Escape keypress on real hardware, multiple physical outputs,
  fractional and rotated scales, compositor loss, and a full reboot with the new configuration in
  place.

## Installed release with the optional backend

The latest full-access source suite passed **178 tests in 21.317 s, with no skips**,
including pinned-patch applicability. A separate restricted-sandbox run failed on
environmental restrictions; it does not invalidate the successful full-access runs.
The following installed indicator counts are historical. The installed indicator suite is
at 28 tests and the
source entrance suite at 9. It
rebuilds its native helpers in place and passes the no-magnifier check. The optional backend was then built, installed and enabled on the development
host, which runs Hyprland 0.56.2 and therefore matches the pinned ABI: the plugin reported version
0.10.0-cu.1 with a matching version check, active status and ready shaders, window and subsurface
glass disabled, layer glass active, and no configuration errors after reload.

The paragraphs below were recorded against the **previous tinted material**. Input behaviour, capture
behaviour and cleanup are independent of the tint, so they still hold; the contrast figures do not.

On that host the installed command passed all seven demo steps — entry focus, literal text including
Vietnamese, click, double click with three button activations, a visible drag, a Ctrl-modified click
and scroll — with the resulting events asserted, at 269.2, 367.3, 268, 319.4, 537.9, 264.1 and
247.8 ms per step, each a single sample rather than a percentile.

Clean capture held on three repetitions of both paths, pixel-identical across the expanded pill and
shadow area with focus unchanged: screen 31, 32 and 42 ms, window 35, 48 and 34 ms. Afterwards no
indicator layer and no session record remained. Five cleanup cases — driver error, wrapper kill,
guardian kill, helper kill and explicit cancel — took 379.9, 60.8, 624.2, 144.8 and 692.0 ms, and each
ended with zero live owned children, zero layers, no snapshot and no overlay pixels, with
cancellation latched.

Text contrast on that tinted material: light 5.56 body and 4.61 Escape hint, dark 17.76 and 12.94,
after a first revision that measured 2.22 for the light body. **These are historical numbers for a
material that has been replaced** and say nothing about whether the current near-clear material is
readable. That is pending.

## Current material, re-measured

With the tint, blur, noise and adaptive dim removed and brightness kept at 1, clean capture was
re-run on an earlier untinted material: three screen captures at 44, 41 and 28 ms and three window captures
at 41, 26 and 28 ms, each pixel-identical across the expanded pill and shadow area with focus
unchanged, focus being settled before the baseline. A first comparison taken straight after a
workspace switch failed and a rerun passed; the cause of the failure is not established, so it is
recorded as unexplained rather than diagnosed.

The label is plain Inter at 14 px with no outline. The current material has no tint and no grain. The
refraction model is a capsule-local rounded surface normal with refraction approximated at an index of
refraction of 1.45, no chromatic aberration and no lens dome; the source candidate uses refraction
strength 0.65, edge thickness 0.20 and blur strength 0.06. The rim scales with edge thickness: at the
built-in scale of 38, an edge thickness of 0.20 gives a rim of **7.6 px**, not the 3.04 px that the
earlier edge value of 0.08 produced, and the analytical displacement bound is about **5.21 px**. The
rim figure is arithmetic and the displacement figure is computed; neither was measured here. This is
an approximation inspired by
the Hyprliquid project (commit `4bbb7028`, BSD 3-Clause); **no code from it was copied**. It is not
a reproduction of a look.

The installed copy still carries the earlier candidate values — refraction 0.9, edge thickness 0.12,
blur 0.08 — and was not updated. The source candidate and the installed copy therefore differ, and
neither is evidence of what any running session displays.

The preset's `refraction_flow` and `refraction_spread` values are historical and upstream-only; the
capsule-local normal and the refraction override in the applied patch now determine the result, so
changing those two values has no visible effect today.

A numerical contract in `tests/test_glass_optics_contract.py` parses the current preset
and bounds modeled displacement by depth * strength * sqrt(IOR squared - 1),
about 5.21 px. Flat-centre zero, symmetry and sampled continuity convergence passed.
This is a numerical model, not a measured GPU displacement or visual acceptance.

Earlier presets are history: refraction 0.85 with lens shaping, then 0.35 with no blur, then 0.15 at
edge 0.08 with blur 0.5, then 0.9 at edge 0.12 with blur 0.08. The source candidate is 0.65 at edge
0.20 with blur 0.06.

The backdrop does update under motion: a nested run with the liquid path active counted backdrop
cache misses during fixture motion, rising from 2 to 27. An earlier run suggesting otherwise fell back to
the native non-liquid path and has been withdrawn as invalid. A separate bounded knob comparison is
rough: the edge metric is noisy with row medians at 0, only the single-knob control isolates refraction
strength, and its legibility captures were black and invalid, so it supports a candidate setting
rather than proving a cause.

The badge now starts statically: no animation, no startup delay. The user asked to keep the liquid
backdrop and drop the animation. `CU_INDICATOR_ENTRANCE` still selects an animation — `drop` or
`sheet` — but only when set explicitly; unset or empty means static. The optional duration stays at
1000 ms and `CU_INDICATOR_ENTRANCE_MS` accepts 250 to 4000 ms. That path is experimental and inactive
by default. Earlier installed measurements of 1135.6 ms for `drop` and 1136.3 ms for `sheet` were
taken at a 1000 ms animation and include GTK startup, and a later revision briefly raised the default
to 1500 ms before it was set back; nothing was measured at 1500 ms, and nothing has been measured
since the default became static. Private screen recordings exist; clips and paths stay private.

The installed candidate passed three clean-capture repetitions per path after each entrance:
`drop` screen 39/48/44 ms, window 40/40/39 ms; `sheet` screen 35/33/29 ms, window 34/27/40 ms.
Expanded pill/shadow pixels matched the hidden baseline and focus remained unchanged.

Visual acceptance of the current material is **pending**. The host previously crashed with SIGSEGV
after a module swap, with no stack trace and therefore **no proven root cause**; replacing a file under
a loaded plugin is a candidate explanation, not a finding. The identical binary has since been loaded
once as a fresh immutable hash-named file on a host with no other plugins, no hot swap and no
autoload: shaders ready, active, version matched, and a twelve-second static session exited cleanly
with no crash observed. One clean bounded run is not acceptance. Readability against a live bright or
high-contrast backdrop is the open question, and no contrast figure exists for it yet. This is a
prototype, not a completed project.

Acceptance covers one host and one ABI. Setup is manual; `docs/liquid-glass.md` documents the two
steps.

The earlier 320×44 and 288×38 measurements do not transfer to this surface.

## Current policy

The current client uses fixed white lettering and the normal layer namespace;
adaptive ink negotiation is removed. Liquid fill alpha is zero, inner rim light
is white-only, and the preset disables bevel shadow, tint and adaptive dimming.
These source contracts are tested; they do not establish visual acceptance or
contrast on every backdrop. The following records describe an older experiment.

Fixed-white/clear-transmission validation: native helpers built successfully;
the source suite ran 178 tests in 20.861 s (one optional skip), and the installed
indicator/material suites ran 39 tests successfully. A bounded no-input host
preview using direct config had ready 139.7 ms and hide/show 27.1 ms, unchanged
focus, no config errors, and helper exit 0. The later direct config corrected a
real runtime problem: queued preset declarations did not apply through eval.

Three installed no-input sessions then had zero startup failures, refusals or
action errors: median observation 210.5 ms, zero-wait action 394.3 ms, whole
session 985.0 ms; capture samples 59/62/56 ms. These small samples do not measure
mouse/keyboard latency, prove clean screenshots pixel-for-pixel on moving
backgrounds, establish visual similarity, or explain an earlier transient
startup failure. No compositor plugin was swapped, unloaded or reloaded.

## Historical adaptive foreground ink experiment — not selected now

A near-clear backdrop gives a fixed foreground ink no safe default: white lettering that reads well on
a dark desktop is unreadable on a bright one. The badge therefore does not pick a colour. The backend
advertises a capability, `indicatorInkEncoding` with the exact value `magenta-v1`, the client compares
that value for equality and only then opts the badge in, and the resulting marker is decoded inside
the compositor, where the backdrop is already sampled. The probe also moves the badge to a separate
layer namespace, so it runs with no glass behind it and cannot be confused with the ordinary badge.

There is **no screenshot polling and no change to the acknowledgement protocol**. The client still
gets exactly the acknowledgements it got before, and no per-pixel scan runs outside the compositor.

Measured, by tier:

- **Mocked unit tests** cover the capability negotiation only: an exact match opts in, and an old,
  malformed, missing, pending or changed backend keeps the ordinary fallback.
- **Real nested compositor runs, both backends confirmed.** Against an **exact-white background** the
  badge resolved to **black ink**; against a **forest-like photographic background** it resolved to
  **uniform white lettering**. The per-fragment speckle of the earlier version is gone in both.
  Hide and show acknowledgements ran in **8.9–14.3 ms**, and a capture with the expanded pill and
  shadow area was clean and pixel-identical to its baseline. Nested compositor only.
- **The decision is per text element, not global.** The current version takes a shared 5-sample
  decision **separately for the label and for the Escape hint** — two independent decisions, one per
  element, each averaged over five samples instead of being decided per fragment. **The label and the
  hint can therefore disagree**, and that was not checked in either confirmed run.
- **Contrast is not guaranteed across backgrounds.** Two backends behaving correctly is a sample of
  two. No contrast figure exists for any backdrop, no threshold has been measured, and nothing shows
  that a luminance-based decision is enough where a backdrop is half bright and half dark.

This capability exists only in the source tree. It is not in any installed copy, has not run outside
the nested compositor, and nothing here claims the installed command or the development host
supports it. Swapping a plugin module under a running compositor is forbidden: a new build takes
effect only in a fresh compositor session, and an already-mapped module is never unloaded or reloaded
to pick up new code.

## Unverified configurations

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
