# computer-use-wayland

A local GUI-automation tool for AI agents on Wayland/Hyprland. One binary-style
CLI drives the pointer, keyboard, screen capture, Chromium DOM and native
accessibility, so an agent can act on a real desktop instead of guessing.

No model API calls and no daemon: every command is a short-lived process that
prints bounded JSON.

## What it does

- **Virtual pointer** on Wayland via a purpose-built protocol, with drag, wheel
  and multi-button support. Real input, not screen-scraping clicks.
- **Keyboard** with grouped modifier chords, `repeat` and `hold_ms`, plus
  deliberate fcitx5 compose/literal control for Vietnamese input.
- **Screen capture** per window or per monitor, with optional region crop.
  Actions re-check window geometry and monitor layout before moving anything, and
  refuse input if the screen changed since the observation.
- **Chromium DOM** control over CDP with refs instead of coordinates.
- **Native accessibility** over AT-SPI.

## Install

Requires `cc`, `wayland-scanner` and `libwayland-client` to build the pointer.

```sh
git clone https://github.com/phamTuan207/computer-use-wayland
cd computer-use-wayland
python3 scripts/build.py
mkdir -p ~/.local/bin
ln -sf "$PWD/scripts/cu.py" ~/.local/bin/computer-use
chmod +x scripts/cu.py
```

`scripts/build.py` regenerates the protocol glue from `native/pointer.xml` and
compiles the pointer. Nothing is downloaded.

## Usage

```sh
CU=computer-use

$CU windows                       # exact address, title, bounds, workspace
$CU observe --window 0xADDRESS    # image + observation paths
$CU act --observation PATH --actions - <<'JSON'
[{"type":"click","x":210,"y":140},{"type":"key","keys":["Ctrl","a"]}]
JSON
```

`observe` returns an image path and an observation path; `act` takes coordinates
**in the returned image** and converts them itself, so they stay correct no
matter how the image was scaled for viewing.

### Coordinate rule

Coordinates belong to the image `observe` returned. Do not measure them off a
resized copy of it. If a target is too small to read, capture it again with a
smaller `--crop` or a larger `--max-width` and take the coordinates from *that*
fresh observation.

### When to stop

If a click misses twice, stop and re-observe rather than nudging the
coordinates. Repeated misses mean the layout moved or the target is not what it
looked like.

## Agent skill

`skill/SKILL.md` plus `skill/references/usage.md` are written to be loaded by
an agent. `validation.md` records what was measured, and what was not.

Symlink the skill into your agent's skills directory to share one copy between
Codex and OpenCode:

```sh
ln -s "$PWD/skill" ~/.config/opencode/skills/computer-use
```

## Layout

| Path | What |
|---|---|
| `scripts/cu.py` | CLI entry point and orchestration |
| `scripts/cdp.mjs` | Chromium CDP backend |
| `scripts/a11y.py` | AT-SPI backend |
| `native/` | Wayland pointer protocol and C source |
| `overlay/` | shell.qml notification overlay for the hotkey |
| `skill/` | agent-facing documentation |
| `tests/` | unit tests and live fixtures |

## Scope and honesty

Desktop results are event-level confirmations. `completed` counts dispatched
actions, not confirmed application outcomes. This is foreground automation on a
live desktop, not an isolated sandbox.

Nothing here is measured against a published benchmark. Numbers in
`validation.md` come from specific local runs and are labelled as such.

## License

See `LICENSE`.