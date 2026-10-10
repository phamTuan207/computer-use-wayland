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
  Captures omit the normal cursor and temporarily clear the session overlay,
  waiting for compositor presentation acknowledgements before copying pixels.
  Actions re-check window geometry and monitor layout before moving anything, and
  refuse input if the screen changed since the observation.
- **Chromium DOM** control over CDP with refs instead of coordinates.
- **Native accessibility** over AT-SPI.

## Install

Requires `cc`, `wayland-scanner` and `libwayland-client` to build the pointer. The indicator additionally requires `pkg-config`, GTK4 and `gtk4-layer-shell` (pkg-config module `gtk4-layer-shell-0 gtk4 wayland-client`), plus `wayland-protocols` for `stable/presentation-time/presentation-time.xml` and for the staging protocol `staging/ext-background-effect/ext-background-effect-v1.xml` that the badge uses for its backdrop blur. Because that protocol is staging, the file must exist in your `wayland-protocols` package; if it is missing, `wayland-scanner` fails and the build stops. A compositor without `ext_background_effect_manager_v1` makes the indicator exit with a warning rather than draw an unblurred badge. The mouse-modifier helper additionally requires `libxkbcommon`.

```sh
git clone https://github.com/phamTuan207/computer-use-wayland
cd computer-use-wayland
python3 scripts/build.py
mkdir -p ~/.local/bin
ln -sf "$PWD/scripts/cu.py" ~/.local/bin/computer-use
chmod +x scripts/cu.py
```

`scripts/build.py` regenerates the protocol glue from `native/pointer.xml`, compiles
the pointer, regenerates the indicator's `presentation-time` and
`ext-background-effect-v1` protocol glue, builds the `native/indicator` binary, then
builds the `native/modifiers` helper from `native/keyboard.xml`. Nothing is downloaded.

The vendored virtual-keyboard protocol comes from
[wtype](https://github.com/atx/wtype/blob/master/protocol/virtual-keyboard-unstable-v1.xml);
its MIT copyright and license are preserved in the XML.

## Usage

### Safe desktop demo

The optional GTK demo has no network or account actions. In one terminal:

```sh
demo_dir=$(mktemp -d)
python3 tests/demo.py --layout "$demo_dir/layout.json" --events "$demo_dir/events.json"
```

In another terminal, use the same directory value:

```sh
python3 scripts/cu.py session -- python3 tests/demo_driver.py \
  --layout "$demo_dir/layout.json" --events "$demo_dir/events.json"
```

The driver targets only this fixture, checks actual text/button/drag/modifier/
scroll events, and restores the previous focus on normal completion. Use a
separate workspace and do not interact during the run. Escape cancels the session.
The fixture requires Python GObject/GTK4 bindings in addition to the build tools.

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

`observe --window` captures visible screen pixels without changing focus or
workspace. Hidden windows and windows on inactive workspaces are refused.
Add `--focus` to explicitly activate the target before capture; this may switch
workspace. Overlapping windows can still cover the captured area.

### Session boundary

Launch the program responsible for the whole task with
`computer-use session -- DRIVER [ARGS...]`. Commands launched by that driver
inherit the session. A top-center “Computer use active” pill identifies agent
control; the real cursor stays the user’s normal one, with no cursor theme
change and no desktop magnification. The pill asks the compositor for a
per-surface backdrop blur, and the overlay is click-through and never takes
keyboard focus. Input commands require this
session; standalone observations remain available.

Startup installs best-effort physical Escape cancellation and registers the
driver's process group before releasing it. The indicator must acknowledge
presented buffers before the driver can run. Capture clears it temporarily and
restores it in a finally block; failed acknowledgements stop input. Each action still checks geometry, focus and image
changes immediately before input.

Physical Escape cancels even while the driver is thinking. If its temporary
binding cannot be installed, a warning is logged; explicit cancellation and
signals still work. `computer-use cancel` latches cancellation;
`computer-use finish` requests completion. Use `computer-use resume` only after
the user asks to continue, then launch a new session.

The guardian survives an abruptly killed wrapper; the wrapper provides fallback
if the guardian dies. Cleanup stops the driver group, drains input, closes the
owned indicator pipe and removes the temporary Escape binding. The indicator
also exits on pipe EOF or parent loss. Failed cleanup retains the session record for
`computer-use recover`. Simultaneous loss of both processes or an unavailable
compositor can leave that binding installed; recover after service returns.
No cursor theme or screen-scale setting is changed. For a retained record from the
old magnifier implementation, run that previous version's recovery before
upgrading; the new version refuses to discard it or guess the old setting.

## Agent skill

`skill/SKILL.md` plus `skill/references/usage.md` are written to be loaded by
an agent. `validation.md` records what was measured, and what was not.
`docs/liquid-glass.md` describes the optional experimental compositor backend: it
is ABI-specific, was built and exercised on Hyprland 0.56.2 with a measurable
refraction effect and a backdrop that updates under motion, and setup is a manual
two-step change to your own configuration — there is no installer. The material is
a transparent approximation, not a reproduction of Apple's, and its appearance is
not yet accepted. An optional startup animation is selected with
`CU_INDICATOR_ENTRANCE` and is off by default. `tests/glass_optics.py` is an
optional command for measuring that displacement and needs Pillow and numpy; it
is not part of the test suite.

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
