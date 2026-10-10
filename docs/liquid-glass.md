# Liquid glass backend (optional)

The session badge keeps its Cairo foreground in both cases. The optional compositor backend only
changes the **backdrop** behind that foreground: the compositor draws the blurred, refracting glass
layer, while the text, status dot and shadow are still drawn by our own surface on top. Nothing here
replaces the foreground, and the built-in path stays the default. That backend is **not installed,
not loaded, and not part of the default setup**. Nothing in this repository installs it or edits your
compositor configuration.

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
Redistributing a binary built from it carries the upstream license and notice obligations. No third
party shader or widget code was copied into this repository; the build is upstream source plus the
supplied patch only.

## Not verified

`native/hyprglass-capsule.patch` is **not in the repository yet**, so no build of this backend has run
here. Only the script's failure paths are covered by tests
(`tests/test_glass_build.py`); the successful apply-then-build path is exercised with a mocked
`subprocess`, never a real `make`.

Nothing here is ready to use. Optics, live-host behaviour, and multimonitor or fractional-scale
coverage are unmeasured, no host plugin has been loaded, and manual setup is pending acceptance. Do
not treat this document as a supported configuration.
