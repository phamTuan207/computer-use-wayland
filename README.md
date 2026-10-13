# computer-use-wayland

A GUI-automation tool for AI agents on Wayland, targeting **Hyprland**. One CLI
drives a virtual pointer, virtual keyboard, screen capture, Chromium DOM and
native accessibility.

No model API calls. Commands print bounded JSON. An explicit automation session
owns the desktop for one task and cleans up afterwards.

## What it does

- **Virtual pointer** over a purpose-built Wayland protocol: drag, wheel, multi-button.
- **Keyboard** with grouped modifier chords, `repeat`, `hold_ms`, and explicit
  compose/literal control for Vietnamese and other IME input.
- **Screen capture** per window or monitor, with region crop. Captures omit the
  cursor and clear the session overlay, waiting for compositor presentation
  acknowledgements before copying pixels.
- **Chromium DOM** over CDP with element refs instead of coordinates.
- **Native accessibility** over AT-SPI.

Desktop input is GUI-exclusive: only one automation session may hold the desktop.
The pointer is shared with the user; simultaneous human input is not blocked.

## Requirements

Runtime: Python 3 with Pillow, plus `grim`, `hyprctl` and `wtype` on PATH.
Desktop input needs a compositor with virtual-pointer and virtual-keyboard
support (Hyprland).

Native build: `cc`, `wayland-scanner` and `libwayland-client`. The session
indicator also needs `pkg-config`, GTK4 and `gtk4-layer-shell`
(`pkg-config --exists gtk4-layer-shell-0 gtk4 wayland-client`), plus
`wayland-protocols` for `stable/presentation-time/presentation-time.xml` and the
staging protocol `staging/ext-background-effect/ext-background-effect-v1.xml` used
for the badge backdrop blur. That protocol is staging: if the file is absent from
your `wayland-protocols` package, `wayland-scanner` fails and the build stops.
A compositor without `ext_background_effect_manager_v1` makes the indicator exit
with a warning instead of drawing an unblurred badge. The mouse-modifier helper
additionally needs `libxkbcommon`.

Optional: browser control needs Node >= 22 and Chromium; native accessibility
needs Python GObject/AT-SPI bindings; the safe demo fixture needs GTK bindings.

## Install

```sh
git clone https://github.com/phamTuan207/computer-use-wayland
cd computer-use-wayland
python3 scripts/build.py
mkdir -p ~/.local/bin
ln -sf "$PWD/scripts/cu.py" ~/.local/bin/computer-use
chmod +x scripts/cu.py
```

`scripts/build.py` regenerates protocol glue from the XML files in `native/`,
compiles the pointer, builds the `native/indicator` binary, then builds the
`native/modifiers` keyboard helper. Nothing is downloaded, and no compositor
plugin is installed automatically: optional backends stay off until you build
and enable them yourself.

The vendored virtual-keyboard protocol comes from
[wtype](https://github.com/atx/wtype/blob/master/protocol/virtual-keyboard-unstable-v1.xml);
its MIT copyright and license are preserved in the XML.

## Quickstart: one session per task

```sh
computer-use session -- your-agent-command --flag
```

Launch the program responsible for the whole task inside the session; commands
it starts inherit the session. An interactive agent that pauses between tool
calls speaks JSON lines over the session driver and keeps one stdin handle alive:

```sh
computer-use session -- computer-use session-driver
```

Do not start one session per `act` — the overlay would vanish between commands.
The driver protocol is described in
[skill/references/usage.md](skill/references/usage.md#interactive-agent-driver).

## Usage

```sh
computer-use observe --window 0xADDRESS --max-width 1280
computer-use act --observation /tmp/obs.json --actions /tmp/actions.json
computer-use doctor
```

Desktop `observe` returns screenshot and observation paths. Use coordinates in
that returned image; `act` maps them to the desktop and may focus its target.
Desktop `observe` leaves focus unchanged unless `--focus` is given. Input commands must run inside the task session above;
read-only observations may run standalone. `--crop X Y W H` limits the image and
`--settle-ms 600` waits for bounded pixel stability. `settle_stable` is not proof
that the application finished. Screenshots may contain private data.

Prefer API/DOM targets when an app offers one; use cropped desktop observations
only when it does not. Batch related actions into one `act`.

For ordinary browser text fields prefer `set_value` plus a check of the app's own
result: it is focus-independent but dispatches synthetic, untrusted events. Use
browser `fill` only when trusted keyboard behaviour is needed and the target is
controlled, and verify with an app-result assertion.

### Browser act

Browser `observe` returns up to 80 interactive elements with refs, visible ones
first. Form values are redacted; screenshots and labels may still be private.
Use `--max-elements 16` for a smaller response (range 1..80), raising it when a
target is missing rather than guessing a ref. Select the exact tab ID and use
the snapshot ID returned by `browser observe`.

```sh
computer-use browser start
computer-use browser tabs
computer-use browser observe --target EXACT_TAB_ID
computer-use browser act --target EXACT_TAB_ID --snapshot ID --actions /tmp/actions.json --no-after
```

`--no-after` is opt-in and applies to `act` only: on success the result carries
`after_skipped: true` and no fresh snapshot, so the response is smaller. It
cannot be combined with `--image`, and the final action must be an `assert`
carrying a condition it really evaluates — `value` (string, `""` allowed),
non-empty `text`, or boolean `checked`. Execution failures still attempt a
diagnostic `after` snapshot; preflight errors happen before input. Because no
fresh snapshot comes back, observe again before any
further input. The desktop `act --no-after` flag is a different feature.

### Session lifecycle and limits

A top-centre "Computer use active" pill identifies agent control. It is
click-through, never takes keyboard focus, and is mandatory by default. Startup
registers a best-effort physical Escape cancellation binding; if it cannot be
installed, a warning is logged and explicit cancellation still works. `computer-use cancel` latches cancellation,
`finish` requests completion, and `resume` only after the user asks to continue.
Esc cancels; it is never an instruction to retry input.

Desktop actions re-check window geometry, focus and screen state before
input and **may refuse** rather than act on a stale observation. There is no
automatic observation, retry or replay. Cleanup stops the driver group, drains
input and removes the overlay; failed cleanup retains a session record for
`computer-use recover`.

Warm driver loops reuse the Python runtime between requests and one private Node
runtime for browser commands, cleaned up at task end. Every browser command
revalidates its target and opens a fresh CDP connection; there is no snapshot
caching and no persistent websocket.

Unicode and IME limits are real: desktop `wtype` can lose characters through key
collisions, and non-BMP emoji are refused on that route. Use browser `set_value`
for ordinary fields, `fill` when trusted input is needed, or an accessibility
setter. Native focus checks run between keyboard groups; typing is not bound to
a particular window. Details and measured limits are in
[docs/optimization-experiments.md](docs/optimization-experiments.md).

## Optional extras

`python3 scripts/build-cursor.py THEME_DIR` builds an XCursor theme (needs
Pillow and `rsvg-convert` at build time); enable it by placing
`native/agent-cursor.json` in your CLI tree with the real restoration settings:

```json
{"theme":"your-built-theme","size":32,"restore_theme":"your-current-theme","restore_size":24}
```

Use your actual current theme and size for restoration. The session guardian
restores them when the task ends. This uses the shared desktop pointer.

[docs/liquid-glass.md](docs/liquid-glass.md) covers the optional compositor
backdrop backend and how to build it from pinned upstream source. Both are
opt-in and are not defaults.

## Agent skill

`skill/SKILL.md` plus `skill/references/usage.md` are written to be loaded by an
agent. Symlink the directory into your agent's skills directory, for example:

```sh
ln -s "$PWD/skill" ~/.config/opencode/skills/computer-use
```

## Layout

| Path | What |
|---|---|
| `scripts/cu.py` | CLI entry point and orchestration |
| `scripts/cdp.mjs` | Chromium CDP backend |
| `scripts/a11y.py` | AT-SPI backend |
| `scripts/cursor_session.py` | session ownership and cleanup recovery |
| `native/` | Wayland pointer protocol and C source |
| `skill/` | agent-facing documentation |
| `tests/` | unit tests and live fixtures |
| `docs/` | measured results and backend notes |

## Testing

```sh
python3 scripts/build.py
python3 -m unittest discover -s tests -p 'test_*.py'
```

Most tests are offline. Live fixtures need a real session; see
[docs/testing.md](docs/testing.md).

## Scope and honesty

Results are event-level confirmations: `completed` counts dispatched actions,
not confirmed application outcomes. This is foreground automation on a live
desktop, not an isolated sandbox. Numbers quoted in docs come from specific
local runs and are labelled as such.

## License

See `LICENSE`. Vendored protocol XML keeps its upstream MIT notice.
