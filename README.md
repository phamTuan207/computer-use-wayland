# computer-use-wayland

A local GUI-automation tool for AI agents on Wayland/Hyprland. One binary-style
CLI drives the pointer, keyboard, screen capture, Chromium DOM and native
accessibility, so an agent can act on a real desktop instead of guessing.

No model API calls. CLI commands print bounded JSON; an explicit automation
session uses a cursor guardian that exits when the session ends.

## What it does

- **Virtual pointer** on Wayland via a purpose-built protocol, with drag, wheel
  and multi-button support. Real input, not screen-scraping clicks.
- **Keyboard** with grouped modifier chords, `repeat` and `hold_ms`, plus
  deliberate fcitx5 compose/literal control for Vietnamese input.
- **Screen capture** per window or per monitor, with optional region crop.
  Captures omit the cursor; no status overlay or screenshot suspension is needed.
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

# Run the agent/automation driver inside one session, including time between commands:
$CU session -- python3 automation.py

# The driver invokes these commands as needed:
$CU windows                       # exact address, title, bounds, workspace
$CU observe --window 0xADDRESS    # image + observation paths
$CU act --observation PATH --actions - <<'JSON'
[{"type":"click","x":210,"y":140},{"type":"key","keys":["Ctrl","a"]}]
JSON
```

`observe` returns an image path and an observation path; `act` takes coordinates
**in the returned image** and converts them itself, so they stay correct no
matter how the image was scaled for viewing.

### Session boundary

Launch the program responsible for the whole task with
`computer-use session -- DRIVER [ARGS...]`. Commands launched by that driver
inherit the session. The real cursor uses zoom factor 5 throughout the session;
the original value read from Hyprland is restored when the driver finishes,
fails, receives cancellation, or a tool refuses an operation. Input commands
require this session. Standalone observations remain available.

Before handing control to the driver, the guardian captures every enabled
monitor until three consecutive image pairs are identical at up to 1280 pixels
wide. There is no fixed startup sleep. Sampling is limited to 120 rounds and a
six-second deadline, with bounded capture commands. A desktop that keeps changing
(for example video playback), failed captures, or cancellation aborts startup and
restores the saved zoom; the driver does not run.

Physical Escape cancels even while the driver is thinking. Its temporary binding
is best-effort: a failure logs a warning; explicit cancellation and signals still
work. `computer-use cancel`
also latches cancellation; `computer-use finish` requests completion. The wrapper
waits for input to stop and cursor restoration before it exits. Use
`computer-use resume` only after the user asks to continue, then launch a new
session. Failed restoration keeps the saved value; `computer-use recover`
retries it without guessing a default. These commands replace the old status pill.

The guardian survives an abruptly killed wrapper; the wrapper also recovers if
the guardian is killed or retains a snapshot after failed restoration. Simultaneous loss of both processes, a broken compositor,
or system failure cannot guarantee automatic restoration. The saved snapshot
supports recovery after those failures.

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
| `scripts/cursor_session.py` | session cursor ownership and recovery |
| `scripts/cancel_hotkey.py` | physical Escape cancellation binding |
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