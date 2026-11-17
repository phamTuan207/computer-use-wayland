# Liquid backdrop backend

The session badge always draws its foreground with Cairo. It already needs the
compositor backdrop-blur protocol to present that badge. The **plugin** described
here changes that backdrop to a refracting liquid material.

It is a default. Standard setup builds and registers it for you; see the README
Install section. This document explains that backend, and then documents the
manual developer path behind it.

The roles are separated on purpose:

- **a session** shows and restores its visuals, without building, downloading
  or loading a plugin;
- **`scripts/setup.py`** prepares everything and registers a startup hook, but
  loads nothing — it never runs `plugin load`, never hot-swaps, explicitly reloads,
  restarts or logs out;
- **the hook** runs once at the next fresh login and performs the single guarded
  activation described below.

If you prefer to do every step yourself, skip the setup command and follow
[Build](#build), [Install the library immutably](#install-the-library-immutably)
and [Activate](#activate-at-a-fresh-login-only) here. The Cairo path keeps
working if you never build the plugin at all.

At build time, `wayland-protocols` must supply the presentation-time XML and
`staging/ext-background-effect/ext-background-effect-v1.xml`. At runtime, the
compositor must advertise `ext_background_effect_manager_v1` and presentation
feedback. Missing backdrop support stops the indicator and prevents input.

## What the setup path does

Setup clones the pinned upstream commit into a temporary directory it owns,
builds it with the pinned local-optics patch, installs the library under a
hash-named immutable path, records the ABI and the cursor tree in a private
manifest, and appends one clearly marked managed block to your Hyprland config
(after backing it up). The generated hook is a `hyprland.start` listener.
Saving the config may trigger its normal auto-reload; the listener does not
activate a plugin during a reload. On every config evaluation, the hook sources
the repo's optics only when Hyprland reports exactly one loaded `hyprglass`
version `1.1.1-cu.1`.

Setup refuses to run — before building anything — when the compositor is not
exactly `0.57.2`, when the header ABI does not match the running compositor,
when a required dependency is missing, when the plugin inventory is not empty
or exactly one verified `hyprbars` (`Vaxry`, `1.0`), when your config carries
an edited managed block, when it is running inside a
`computer-use` session, or when no cursor profile exists and you did not pass
`--restore-theme` and `--restore-size`. It holds the session owner lock for the
whole run so an automation cannot start mid-build.

At the next fresh login the hook validates the manifest, the optics profile
digest, the installed cursor tree and the recorded ABI, confirms the compositor
actually just started (a 30-second window checked immediately before each
first-load), and refuses if any of that fails or if the plugin inventory has
changed. Glass first-load permits only no plugins or the same verified
`hyprbars`; cursor first-load requires the accepted glass plus optional verified
`hyprbars`. The complete inventory, including handles, is rechecked before each
load. It never falls back to a plain background on failure. **Never** unload,
hot-swap or replace a module the compositor has loaded; to change backend, use
the previous immutable library at a fresh login.

Loader results and failures are recorded as private JSON lines in
`~/.cache/agent-computer-use/logs/visuals.jsonl`. Records include the stage,
compositor instance and artifact hashes; they do not include session tokens or
screenshots.

## Get the exact upstream source

Only for the manual path. The build is pinned. Clone upstream, check out the
pinned commit, and pass that checkout as `SOURCE`:

```sh
git clone https://github.com/hyprnux/hyprglass.git /path/to/hyprglass
git -C /path/to/hyprglass checkout 03a57c4451b4abee38feda2ffb725f55ecc0f2fd
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

`scripts/build-glass.py` requires `--local-optics` and enforces two constraints:
the checkout must be a git worktree at
`03a57c4451b4abee38feda2ffb725f55ecc0f2fd`, and
`pkg-config --modversion hyprland` must report exactly `0.57.2`, because the
plugin links against that ABI. Besides the core dependencies in the README, the
[pinned upstream Makefile](https://github.com/hyprnux/hyprglass/blob/03a57c4451b4abee38feda2ffb725f55ecc0f2fd/Makefile)
requires `make`, a C++23 compiler and development files discoverable through
`pkg-config` for `hyprland`, `pixman-1`, `libdrm` and `wayland-server`.
The v1.1.1 source is the selected candidate from Hyprglass's 0.57 line; its
upstream pin table does not list 0.57.2, so build and live acceptance on 0.57.2
remain separate checks.

**`--local-optics` is required**, and it is the form
`scripts/activate-glass.py` expects: that script loads
`native/hyprglass-local-optics.lua` from its own tree, with no option to choose
another. This build reports version `1.1.1-cu.1`. The capsule patch
`native/hyprglass-capsule.patch` and profile `native/hyprglass-indicator.lua`
remain historical experimental 0.10.0 material; the current build rejects the
old mode and does not select either file. Do not combine patches or mix a
library with a profile from another version.

The build script only selects and applies a patch. It does **not** copy or
install any Lua profile. If you deploy these scripts somewhere other than the
repository root, `native/hyprglass-local-optics.lua` must exist at
`native/` in the same project or installation root as `scripts/`.

After editing `native/hyprglass-local-optics.lua`, follow the manifest check,
sync, and commit rule in the README Install section; the repository pre-commit
hook enforces it after `bash scripts/install-git-hooks.sh` is run once per clone.

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

Use the installer-returned library path, ABI hash and optics profile hash for
your verified build. From a fresh login with either no plugins loaded or the
verified `hyprbars` plugin loaded:

```sh
python3 scripts/activate-glass.py /path/to/plugin-dir/hyprglass-SHA256HERE.so \
  --abi ABIFROMSTEP1 --profile-sha256 "$(sha256sum native/hyprglass-local-optics.lua | cut -d' ' -f1)"
```

`--abi` is the compositor ABI you recorded, not something detected from the
binary. `--profile-sha256` must match the repo optics file. Activation reads
Hyprland's ABI and complete plugin inventory back, and refuses a mismatch or
any plugin set other than empty or the same verified `hyprbars`.

Activation **does** change the running session: it issues `plugin load`, then a
bounded normal config reload, and waits for clean `configerrors` and ready glass
metadata. The config hook sources the optics during that reload, committing the
indicator layer settings. Glass status is metadata only; it does not prove the
indicator namespace's rendered appearance. That is why activation is a login-time
step:

- build and install never load anything;
- **never** unload, hot-swap or replace a plugin the compositor has loaded;
- to change backend, roll back to the previous immutable library and start a
  fresh login.

The preserved capsule patch and profile are historical 0.10.0 experimental
material and are not accepted by the current build or activation path.

These manual scripts never edit your personal configuration. `scripts/setup.py`
does, and only in one way: it backs your Hyprland config up and appends a single
clearly marked managed block that calls the generated hook. It never replaces a
block you edited. Nothing here should be run inside an automation session; the
session commands never load a plugin at all.

## Fail-closed switch

`native/require-liquid` makes the session refuse to run when the backend is
absent instead of silently falling back to the Cairo backdrop. It does **not**
load a plugin. Standard setup creates it; on the manual path, create it yourself.
It is generated local configuration, not a tracked source file, along with the
generated profile, manifest, managed Lua file and the managed block in your
Hyprland config — none of those belong in version control.

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
