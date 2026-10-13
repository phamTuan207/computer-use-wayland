# Optional liquid backdrop backend

The session badge always draws its foreground with Cairo. It already needs the
compositor backdrop-blur protocol to present that badge. The **optional plugin**
described here changes the backdrop to a refracting liquid material.

Nothing here is a default. The CLI never installs or loads a plugin for you, and
the Cairo path keeps working if you skip this entire document.

At build time, `wayland-protocols` must supply the presentation-time XML and
`staging/ext-background-effect/ext-background-effect-v1.xml`. At runtime, the
compositor must advertise `ext_background_effect_manager_v1` and presentation
feedback. Missing backdrop support stops the indicator and prevents input.

## Get the exact upstream source

The build is pinned. Clone upstream, check out the pinned commit, and pass that
checkout as `SOURCE`:

```sh
git clone https://github.com/hyprnux/hyprglass.git /path/to/hyprglass
git -C /path/to/hyprglass checkout 84c1a5ab217101a317d4edaab7fba2efcc1bf346
```

Run these commands from the computer-use-wayland checkout. The upstream source
is [Hyprglass](https://github.com/hyprnux/hyprglass).

## Build

Before building, record `abiHash` from `hyprctl -j version` for the compositor
whose headers and runtime you have verified together. The activation guard
compares this recorded value; it cannot infer ABI compatibility from the binary.

```sh
python3 scripts/build-glass.py /path/to/hyprglass --local-optics
```

`scripts/build-glass.py` enforces two constraints: the checkout must be a git
worktree at `84c1a5ab217101a317d4edaab7fba2efcc1bf346`, and
`pkg-config --modversion hyprland` must report exactly `0.56.2`, because the
plugin links against that ABI. Besides the core dependencies in the README, the
[pinned upstream Makefile](https://github.com/hyprnux/hyprglass/blob/84c1a5ab217101a317d4edaab7fba2efcc1bf346/Makefile)
requires `make`, a C++23 compiler and development files discoverable through
`pkg-config` for `hyprland`, `pixman-1`, `libdrm` and `wayland-server`.

**`--local-optics` is the recommended form**, and it is the form
`scripts/activate-glass.py` expects: that script loads
`native/hyprglass-local-optics.lua` from its own tree, with no option to choose
another. Omitting the flag applies a different patch — the capsule patch
`native/hyprglass-capsule.patch` — which is an **exclusive experimental
alternative** matching `native/hyprglass-indicator.lua`. Do not combine patches,
and do not mix a library built one way with the profile of the other.

The build script only selects and applies a patch. It does **not** copy or
install any Lua profile. If you deploy these scripts somewhere other than the
repository root, `native/hyprglass-local-optics.lua` must exist at
`native/` in the same project or installation root as `scripts/`.

## Install the library immutably

The destination directory must already exist:

```sh
mkdir -p /path/to/plugin-dir
python3 scripts/install-glass.py /path/to/built/hyprglass.so /path/to/plugin-dir
```

The installer publishes to a hash-named path `hyprglass-<sha256>.so` using an
atomic no-replace link, and refuses to overwrite differing bytes at an existing
hash path, so a loaded inode can never be truncated. **Library only** — copy the
matching Lua profile into place yourself.

## Activate, at a fresh login only

Use the installer-returned library path and the ABI hash recorded for your
verified build. From a fresh login with no plugins loaded:

```sh
python3 scripts/activate-glass.py /path/to/plugin-dir/hyprglass-SHA256HERE.so --abi ABIFROMSTEP1
```

`--abi` is the compositor ABI you recorded, not something detected from the
binary. Activation reads Hyprland's ABI hash back and refuses to continue on a
mismatch, and refuses if any plugin is already loaded.

Activation **does** change the running session: it issues `plugin load` and then
`eval dofile` on the profile. That is why it is a login-time step:

- build and install never load anything;
- **never** hot-swap, reload or replace a module the compositor has loaded;
- to change backend, roll back to the previous immutable library and start a
  fresh login.

For the capsule alternative there is no activation script. After verifying its
ABI at a fresh login, load its immutable library first, then apply the matching
`native/hyprglass-indicator.lua` profile manually. Do not use the local-optics
activation helper for that alternative.

Your personal configuration files are never edited by any of these scripts, and
nothing here should be run automatically inside an automation session.

## Optional fail-closed switch

`native/require-liquid` makes the session refuse to run when the backend is
absent instead of silently falling back to the Cairo backdrop. It does **not**
load a plugin. It is local configuration, not part of the source tree.

## Attribution and limits

Hyprglass is distributed under BSD-3-Clause; see
[native/hyprglass-LICENSE](../native/hyprglass-LICENSE). The patches under `native/` keep their upstream
copyright and licence notices. Building against a pinned upstream commit means a
later Hyprland release needs a rebuild and re-verification rather than an
in-place upgrade.

This approximates a translucent material. It is not a reproduction of any
platform's rendering, and nothing here is a general claim about performance or
visual fidelity.

`tests/glass_optics.py` is an optional measurement helper needing Pillow and
numpy. It computes optical quantities numerically; it does not measure GPU
timings.

## Further reading

- [testing.md](testing.md) — running the checks
- [optimization-experiments.md](optimization-experiments.md) — measured results
