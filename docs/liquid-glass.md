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

- Source suite: **178 tests OK in 21.317 s, no skips**, including pinned-patch applicability.
  A separate restricted-sandbox run failed on environmental restrictions; that does not
  invalidate the successful full-access runs. Historical installed indicator suite: 28 tests; source entrance
  suite: 9.
- Nested backend, after Codex's review, build and GPU run: status reports shaders ready, active and
  a matching version check; hide acknowledgements 9–13.9 ms, show 13.9 ms; capture with the indicator
  hidden is pixel-identical to baseline. This was the nested compositor only.
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

The candidate preset in the source tree is a capsule-local rounded surface normal with refraction
approximated at an index of refraction of 1.45, no chromatic aberration and no lens dome, with
refraction strength 0.65, edge thickness 0.20 and blur strength 0.06. There is no tint and no grain.
The rim the effect applies to scales with edge thickness: at the built-in scale of 38 an edge
thickness of 0.20 gives a rim of **7.6 px**, not the 3.04 px the earlier edge value of 0.08
produced. This is an arithmetic consequence of the setting, not a measurement. An analytical bound
puts the resulting displacement at roughly **5.21 px**; that bound is computed, not observed, and no
capture was measured against it here. This is an approximation inspired by the Hyprliquid project
(commit `4bbb7028`, BSD 3-Clause); **no code from it was copied**. It is not a reproduction of
Apple's material.

The installed copy still carries the previous candidate values — refraction 0.9, edge thickness 0.12,
blur 0.08 — and was deliberately left untouched. **The source candidate is not installed**, so
neither the source nor the installed numbers describe what any running session shows.

The preset's `refraction_flow` and `refraction_spread` values are no longer what determines the
result: they are historical, and upstream, while the capsule-local normal and the refraction override
in the applied patch now take precedence. Setting them changes nothing the user sees today.

The displacement contract in `tests/test_glass_optics_contract.py` parses the current
preset and uses the analytical bound depth * strength * sqrt(IOR squared - 1), about
5.21 px. Modeled flat-centre zero, symmetry and sampled continuity convergence passed.
The bound is numerical evidence, not a measured GPU displacement or visual acceptance.

Earlier presets are history, not the shipped state: refraction 0.85 with the lens-shaping values was
the first candidate, then 0.35 with no blur, then 0.15 at edge 0.08 with blur 0.5, then 0.9 at edge
0.12 with blur 0.08. The source candidate is the 0.65 value above. None of these is a visual
acceptance.

## Current foreground policy: fixed white, clear transmission

The label and Escape hint now always use white ink, as requested. The client no
longer negotiates or emits the magenta encoding, and the badge always uses the
ordinary `computer-use-indicator` namespace. The backend's optional decoder is
retained for compatibility but is not selected by this client.

The liquid body has zero foreground fill alpha. Inner reflections are white-only;
bevel shadow, adaptive dimming, vibrancy and tint alpha are explicitly zero. Blur
remains slight (`blur_strength = 0.06`); the existing edge refraction is retained.
Dark scenery can still appear dark through transparent glass. Fixed white text
does not guarantee contrast over white scenery; no dark plate is added to hide
that limitation. Visual similarity to the reference still needs user acceptance.

The pinned backend queues `preset()` and `layer()` calls until config commit:
`hyprctl eval` returning `ok` did not prove the earlier material was applied.
This profile instead uses direct `config()` values, with identical dark/light
overrides and the default resolution path. Namespace filtering is still parsed
at plugin init/config reload, not immediately by `eval`; use the profile at
normal startup for that restriction. Do not reload or replace a loaded plugin
just to refresh it. The shader also retains a hardcoded, bottom-edge-only shadow
(maximum 6%); there is no switch for it in this backend. No claim of completely
shadow-free optical transmission is made.

## Historical experiment: foreground ink capability (no longer selected)

A near-clear backdrop makes a hardcoded foreground ink fail in both directions: white lettering is
unreadable on a bright background and fine on a dark one. The fix is a **capability**, not a chosen
colour.

The backend advertises `indicatorInkEncoding` with the exact value `magenta-v1` in its status. The
client compares that value for equality — nothing is accepted on a near-match — and only then
exports the opt-in variable to the badge process. The capability is re-probed after the backend
reports ready; a backend that is old, malformed, missing, pending or changed fails the check and the
ordinary white/native fallback is used instead.

When the capability is claimed, the badge draws the label and the Escape hint in the marker colour
and moves its layer to a separate namespace, `computer-use-indicator-ink-v1`. The normal badge keeps
`computer-use-indicator`, and only that namespace receives the glass, so the probe deliberately runs
with **no backdrop at all**. A screenshot taken in probe mode therefore says nothing about the
ordinary badge.

The marker is decoded **semantically inside the compositor**, where the backdrop is already sampled
and its luminance is already computed. There is **no screenshot polling, no per-pixel scan and no
change to the acknowledgement protocol**; the client still receives exactly the acknowledgements it
did before.

- A first implementation decided the ink locally per pixel. Against a photographic backdrop it was
  noisy — the decision flickered along the lettering.
- It was changed to a **shared 5-sample decision taken separately for the label and for the Escape
  hint** — two independent decisions, one per text element, each averaged over five samples rather
  than decided per fragment. **The label and the hint can therefore disagree.**
- **Confirmed in nested runs.** Against an exact-white background the badge resolved to black ink,
  and against a forest-like photographic background it resolved to uniform white lettering. The
  per-fragment speckle seen in the earlier version is gone. Hide and show acknowledgements ran in
  8.9–14.3 ms, and a capture with the expanded pill and shadow area was clean and pixel-identical to
  its baseline.
- **Contrast is not guaranteed on every background.** Two backends behaving correctly is a sample of
  two, not a guarantee; no contrast figure exists for any backdrop, and no threshold has been
  measured.

## Not installed, not active

This capability is source-only. It is not present in any installed copy and is not running anywhere.
Nothing here claims the installed command or the development host supports it.

Swapping a plugin module underneath a running compositor is **forbidden**. A new build becomes
active only in a **fresh compositor session**; an already-mapped module is never unloaded, removed or
reloaded to pick up new code.

## Startup animation, off by default

The badge now starts **statically**: no animation, no startup delay. The user asked to keep the
liquid backdrop but drop the animation.

`CU_INDICATOR_ENTRANCE` still selects an animation, but only when set explicitly — `drop` for a
narrow-necked droplet, `sheet` for a full-width sheet that protrudes from the top. An unset or empty
variable means static. The optional duration stays at 1000 ms and `CU_INDICATOR_ENTRANCE_MS` overrides
it anywhere in 250 to 4000 ms. This whole path is **experimental and inactive by default**: it has not
been run since the default changed, and the duration was only ever measured with an animation
requested.

Measured on an installed build at a 1000 ms animation: 1135.6 ms for `drop` and 1136.3 ms for `sheet`,
both including GTK startup rather than the animation alone. `hide` then `show` took 11.9 ms and
17.6 ms. A later revision briefly raised the default to 1500 ms before it was set back to 1000 ms; no
measurement was taken at 1500 ms. Short screen recordings of both variants were captured privately;
those clips and their paths stay private and are not published.

The installed candidate also passed three clean-capture repetitions for each path after each
entrance: `drop` screen 39/48/44 ms and window 40/40/39 ms; `sheet` screen 35/33/29 ms and window
34/27/40 ms. The expanded pill/shadow pixels matched the hidden baseline and focus stayed unchanged.

To try one yourself, with a bounded driver that sends no input:

```sh
computer-use session -- sleep 6                      # static, the default
CU_INDICATOR_ENTRANCE=drop computer-use session -- sleep 6
CU_INDICATOR_ENTRANCE=sheet computer-use session -- sleep 6
CU_INDICATOR_ENTRANCE_MS=2500 computer-use session -- sleep 6
```

Visual acceptance of the current material is **pending**, and **nothing here is a claim about the host**.
The host crashed with SIGSEGV after the shader module was swapped in place while the older module was
loaded, and autoload plus features were disabled. **The cause is unproven**: no stack trace was
captured. Replacing the file under a loaded plugin, rather than publishing a new file atomically, is a
candidate explanation and not a finding.

Since then the identical binary has been installed as a separate immutable hash-named file and loaded
once, fresh, on a host with no other plugins: no hot swap and no autoload. The plugin reported
shaders ready, an active status and a matching version check. A twelve-second static-pill session ran
to a clean exit with no crash observed. That is a single bounded observation: **visual approval is
still pending**, and one clean run says nothing about whether the earlier crash can recur.

## Not verified

Still open: a physical Escape keypress on real hardware, multiple physical outputs, fractional and
rotated scales, compositor loss, a full reboot with the new configuration in place, and visual
acceptance of the current material.

For the foreground ink capability: only two backends have been measured — exact white and a forest
photograph — so behaviour on any other backdrop is unknown; the label and the Escape hint are decided
separately and may disagree; no contrast figure and no threshold exist; the 5.21 px displacement
figure is analytical, not measured; and the capability has never been installed or exercised outside
the nested compositor.

Nothing here is automatic: setup is the two manual steps above, and there is no installer. Acceptance
covers one host and one ABI; a different Hyprland release needs its own build.
