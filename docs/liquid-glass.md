# Liquid glass backend (optional)

The session badge keeps its Cairo foreground in both cases. The optional compositor backend only
changes the **backdrop** behind that foreground: the compositor draws the blurred, refracting glass
layer, while the text, status dot and shadow are still drawn by our own surface on top. Nothing here
replaces the foreground, and the built-in path stays the default. The backend is opt-in: it is ABI-
specific, and setup is a manual two-step change to your own configuration. Nothing in this repository
installs it or edits your compositor configuration for you.

## What it is

An opt-in Hyprland plugin build from a pinned Hyprglass source tree, with one supplied patch applied
to it. The badge keeps requesting a blur region over `ext-background-effect-v1`, so the per-surface
blur path stays the same; only the backdrop material changes.

## Requirements

- A Hyprglass git worktree checked out at exactly
  `84c1a5ab217101a317d4edaab7fba2efcc1bf346`. The build script refuses any other commit.
- `pkg-config --modversion hyprland` must report `0.56.2`. This is mandatory, not advisory: Hyprglass
  plugins are ABI-specific, and a build for another Hyprland version stays paused or crashes the
  compositor. There is no supported "close enough" build.
- `native/hyprglass-capsule.patch`, supplied with the build. The script stops with a clear error if
  the patch file is absent; it never substitutes a generated diff.

## Building

```sh
python3 scripts/build-glass.py /path/to/hyprglass-checkout
```

The script checks the git toplevel, the exact commit and the Hyprland version, applies the patch only
when the tracked tree is clean, then runs `make -j2 -B HYPRGLASS_VERSION=0.10.0-cu.1`. It never
resets, cleans, stashes or deletes anything, and it prints the source path and the resulting
`hyprglass.so` without copying or loading it. Applying the same patch again is a no-op when the
reverse check succeeds. That reverse check does not reject unrelated existing edits.
Before applying a new patch, tracked edits are rejected. A failed apply stops before building;
the script does not reset the source tree to undo any changes.

## Scope

Only the `computer-use-indicator` layer namespace is meant to get glass. Window glass and
subsurface-item glass stay disabled. Configuring every layer or every window would change the whole
desktop, which this backend does not do.

## Fallback

Without the plugin loaded, or when the compositor does not expose it, the built-in badge path is used
unchanged. The compositor backend modifies the backdrop; the badge foreground remains our surface.
Readiness failure stops session startup rather than allowing input with an unverified indicator.

## Licensing

Hyprglass is BSD-3-Clause; its source and license text are in the
[upstream repository](https://github.com/hyprnux/hyprglass) you build from.
Redistributing a binary built from it carries the upstream license and notice obligations.
The patch contains modified upstream shader context; its BSD notice is preserved in
`native/hyprglass-LICENSE`. No code from the unlicensed ShojiWM reference was copied.

## Build evidence so far

A clean, detached worktree pinned to the required commit was built once through
`scripts/build-glass.py`: the gates accepted the exact commit and Hyprland version, the supplied
patch applied, and `make -j2 -B` finished with a link step and exit code 0 in roughly 37 seconds of
wall time. The resulting `hyprglass.so` was about 30.6 MB and carried the expected version string.
Running the same script again on the already-patched tree reported the patch as applied, exited 0,
and produced a byte-identical module, so the apply step is idempotent in practice.

`tests/test_glass_build.py` covers the script with a mocked `subprocess`: the failure paths and that a
failed patch stops before `make`. The positive path above is the real one.

## Measuring displacement yourself

`tests/glass_optics.py` is an optional numerical check, not a unit test — its name does not match the
suite's pattern, and it needs Pillow and numpy. Given three captures of the same synthetic fixture,
one without an offset and two with forced sample offsets:

```sh
python3 tests/glass_optics.py baseline.png forced8.png forced16.png
```

It prints a compact JSON report of the per-row best lag and correlation, and exits non-zero if any row
misses the correlation floor or its expected lag. It never creates or edits images.

## Refraction evidence

Displacement is measurable. With an 8 px forced sample offset the rows read back at lag −8 with
correlation 0.9236 to 0.9288; with 16 px the magnitude reads back at 16 with correlation 0.9214 to
0.9262. The fixture repeats every 32 px, so −16 and +16 are the same shift and only the magnitude is
meaningful.

An earlier run reported zero displacement everywhere. That was a faulty metric rather than a missing
effect. A later on/off comparison shows the displacement varying across the pill — roughly −14 to
−15 px near its top and about +14 px near its bottom, correlations 0.66 to 0.86, with +14 being the
same 32 px alias — so the effect is edge-graded, not uniform.

A real layer-shell query in the nested compositor reports the compact surface at 320×66 at the top
centre of a 1280-wide monitor. The indicator exits with status 2 on an output too small to draw a
readable pill instead of clipping it.

## Manual configuration

There is no automatic installer. Two steps, by hand:

```lua
-- in your Hyprland config, after the plugin is available
hl.plugin.load('/absolute/path/to/hyprglass.so')
dofile('/absolute/path/to/native/hyprglass-indicator.lua')
```

Replace both paths with absolute paths on your machine. The shipped Lua file only configures the
plugin — it deliberately does not load it — and it must not call blocking `hyprctl` at the top level,
because the config is executed more than once during startup.

Before editing, back up your own configuration. Afterwards reload and check the compositor reports no
errors; the plugin also reports its own status, which should show the expected version, an active
status, ready shaders, window and subsurface glass disabled, and layer glass active.

## Tested on the development host

The backend was built, installed and exercised on the machine it was developed on, Hyprland 0.56.2,
which matches the pinned ABI. The plugin reported version 0.10.0-cu.1, a matching version check,
active status, ready shaders, window and subsurface glass disabled and layer glass active. After
setup the compositor reported no configuration errors.

These were recorded against the previous tinted revision of the material. Input behaviour, capture
behaviour and cleanup do not depend on the material's tint, so they still stand as behaviour evidence,
but the contrast figures below do not.

- **Installed input demo** — all seven steps passed against the installed command: focus and literal
  text including Vietnamese, click, double click with three button activations, a visible drag, a
  Ctrl-modified click and scroll, with the resulting events asserted. Step times were 269.2, 367.3,
  268, 319.4, 537.9, 264.1 and 247.8 ms, each a single sample.
- **Clean capture** — three repetitions of both the screen and the window path, each pixel-identical
  in the expanded pill and shadow area with focus unchanged: 31, 32 and 42 ms for screen captures,
  35, 48 and 34 ms for window captures. Single samples, not percentiles.
- **Cleanup after failure** — five cases: a driver error, killing the wrapper, killing the guardian,
  killing the helper and an explicit cancel. Cleanup took 379.9, 60.8, 624.2, 144.8 and 692.0 ms, and
  every case ended with no live owned children, no indicator layer, no session snapshot and no
  overlay pixels. Cancellation stayed latched.
- **Text contrast — historical, not current** — those readings were taken on the earlier tinted
  material: 5.56 light body and 4.61 light Escape hint, 17.76 and 12.94 dark, and a first revision at
  2.22 for the light body. That material has since been replaced. None of these numbers describes the
  current near-clear backdrop, and readability of the current one is **pending**.

## Current near-clear material

The tinted plate was replaced. The preset no longer tints, blurs or dims the backdrop: tint alpha 0,
blur 0, noise 0, adaptive dim and boost 0, and brightness left at 1 so no tone shaping darkens the
moving content. On the client side the foreground body fill and both wash stops now pass 0 in liquid
mode, so the surface draws only the lettering, the dot, the faint rim and the shadow rings. The
non-liquid fallback is unchanged and still draws the previous light plate.

Current checks:

- Source suite: 151 unit tests in 20.750 s. Installed indicator suite: 28 tests; source entrance suite: 9.
- Clean capture on the earlier untinted material: three screen captures at 44, 41 and 28 ms and three
  window captures at 41, 26 and 28 ms, each pixel-identical across the expanded pill and shadow area
  with focus unchanged. Focus was settled before the baseline was taken.
- A first capture comparison taken immediately after a workspace switch failed; repeating it after
  the transient passed. The reason is not established, so treat the passing runs as the evidence and
  the failure as unexplained rather than diagnosed.
- **The backdrop does update under motion.** A nested run in which the liquid path was active counted
  backdrop cache misses during fixture motion, increasing from 2 to 27, which is evidence
  that a moving backdrop is re-sampled rather than frozen. An earlier run that appeared to show the
  opposite fell back to the native non-liquid path and has been withdrawn as invalid.
- **A rough knob comparison, not a clean causal result.** A bounded A/B varying the preset measured
  edge shift means of −4.15 for the stronger refraction, −2.04 for the weaker, and −0.42 when only the
  refraction strength differed. The metric is noisy: row medians were 0 and a single speckle can win
  the search, so the means carry what signal there is. The single-knob control suggests refraction
  strength is the main driver, but the three-knob variant changed more than one setting at once and
  remains a supported candidate, not a proven cause. Legibility captures from that run were black and
  invalid, so no contrast claim comes from it.

The shipped preset is the restrained candidate: refraction 0.35, no chromatic aberration, a slight
lens dome of 0.08, radial sampling toward the capsule centre rather than edge-following flow,
and a fully transparent base with no tint, no blur and no grain.
This is an approximation, not a reproduction of Apple's material.

## Startup animation, opt-in

`CU_INDICATOR_ENTRANCE` selects a startup animation: `drop` for a narrow-necked droplet or `sheet`
for a full-width sheet that protrudes from the top. The default is off, meaning the badge appears
statically with no startup delay. An animation runs 1000 ms and the ready acknowledgement then waits
for the actual final presentation; `hide` cancels one in flight and `show` does not replay it.

Measured on the installed build: 1135.6 ms for `drop` and 1136.3 ms for `sheet`, both including GTK
startup rather than the animation alone. `hide` then `show` took 11.9 ms and 17.6 ms. Short screen
recordings of both variants were captured privately; those clips and their paths stay private and are
not published.

The installed candidate also passed three clean-capture repetitions for each path after each
entrance: `drop` screen 39/48/44 ms and window 40/40/39 ms; `sheet` screen 35/33/29 ms and window
34/27/40 ms. The expanded pill/shadow pixels matched the hidden baseline and focus stayed unchanged.

To try one yourself, with a bounded driver that sends no input:

```sh
CU_INDICATOR_ENTRANCE=drop computer-use session -- sleep 3
CU_INDICATOR_ENTRANCE=sheet computer-use session -- sleep 3
```

Normal use without that variable is unaffected: there is no startup animation and no added delay.

Visual acceptance of the current material is **pending**. Readability against a live, bright or
high-contrast backdrop has not been assessed, and this is a prototype awaiting the user's choice of
entrance variant.

## Not verified

Still open: a physical Escape keypress on real hardware, multiple physical outputs, fractional and
rotated scales, compositor loss, a full reboot with the new configuration in place, and visual
acceptance of the current material.

Nothing here is automatic: setup is the two manual steps above, and there is no installer. Acceptance
covers one host and one ABI; a different Hyprland release needs its own build.
