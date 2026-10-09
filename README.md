# computer-use-wayland

A local GUI-automation tool for AI agents on Wayland/Hyprland. One binary-style
CLI drives the pointer, keyboard, screen capture, Chromium DOM and native
accessibility, so an agent can act on a real desktop instead of guessing.

No model API calls. CLI commands print bounded JSON; an explicit automation
session uses a session guardian that exits when the session ends.

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
inherit the session. Sessions leave the normal cursor and desktop appearance
alone: no magnification, cursor theme change, badge, or capture suspension.
The visible actions themselves signal control. Input commands require this
session; standalone observations remain available.

Startup installs best-effort physical Escape cancellation and registers the
driver's process group before releasing it. It does not capture the desktop or
wait for identical frames. Each action still checks geometry, focus and image
changes immediately before input.

Physical Escape cancels even while the driver is thinking. If its temporary
binding cannot be installed, a warning is logged; explicit cancellation and
signals still work. `computer-use cancel` latches cancellation;
`computer-use finish` requests completion. Use `computer-use resume` only after
the user asks to continue, then launch a new session.

The guardian survives an abruptly killed wrapper; the wrapper provides fallback
if the guardian dies. Cleanup stops the driver group, drains input, then removes
the temporary Escape binding. Failed cleanup retains the session record for
`computer-use recover`. Simultaneous loss of both processes or an unavailable
compositor can leave that binding installed; recover after service returns.
There is no cursor or screen setting to restore. For a retained record from the
old magnifier implementation, run that previous version's recovery before
upgrading; the new version refuses to discard it or guess the old setting.

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
| `scripts/cursor_session.py` | session ownership and cleanup recovery |
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