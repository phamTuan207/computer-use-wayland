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

`tests/test_glass_build.py` still covers the script only, with a mocked `subprocess`: it proves the
failure paths and that a failed patch stops before `make`. The positive path above is the real one.

## Not verified

Optics are **not** accepted. In a nested compositor the on/off comparison shows pixel differences
inside the pill area but no measurable geometric displacement: best-fit shift stays at zero, so the
refraction claim is still unproven. Diagnosis of that is ongoing.

Also unverified: physical Escape input, multiple physical outputs, fractional and rotated scales,
compositor loss, and any behaviour on the live host desktop. No plugin has been installed or loaded
on the host, and the 320×66 compact surface has not been confirmed against a real layer-shell query.

Nothing here is ready to use. Treat manual setup as pending acceptance, not a supported
configuration.
