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

**Hyprland exactly `0.56.2`**, with development headers from that same release.
Setup builds a compositor plugin, so the plugin ABI must match the running
compositor. Setup reconstructs the ABI fingerprint from your installed headers
and compares it with `hyprctl -j version`; if the two disagree, or if
`pkg-config --modversion hyprland` is not exactly `0.56.2`, setup refuses before
building anything. A different Hyprland release needs a rebuild and
re-verification, not an in-place upgrade.

On `PATH`, all of:

`cc`, `c++`, `pkg-config`, `wayland-scanner`, `rsvg-convert`, `make`, `git`,
`hyprctl`, `gsettings`, `grim`, `wtype`

Setup does **not** install any of them or invoke `sudo`. Install them
with your own package manager first.

Runtime and native libraries: Python 3 with Pillow, `libwayland-client`, GTK4 and
`gtk4-layer-shell` (`pkg-config --exists gtk4-layer-shell-0 gtk4 wayland-client`),
`libxkbcommon` for the mouse-modifier helper, and `wayland-protocols` supplying
both `stable/presentation-time/presentation-time.xml` and the staging protocol
`staging/ext-background-effect/ext-background-effect-v1.xml` used for the badge
backdrop blur. That protocol is staging: if your `wayland-protocols` package
lacks it, `wayland-scanner` fails and the build stops.

Optional: browser control needs Node >= 22 and Chromium; native accessibility
needs Python GObject/AT-SPI bindings; the safe demo fixture needs GTK bindings.

## Install

```sh
git clone https://github.com/phamTuan207/computer-use-wayland
cd computer-use-wayland
python3 scripts/setup.py \
  --restore-theme YOUR_CURRENT_HYPRLAND_THEME \
  --restore-size YOUR_CURRENT_HYPRLAND_SIZE
```

Then **log out and log back in once.** That is the whole installation.

The two `--restore-*` values are the Hyprland cursor theme and size you use
**today**. Nothing can read them back from the compositor, so you declare them
once, here. Setup stores them in the cursor profile and puts your original cursor
back at the end of every task. If a valid `native/agent-cursor.json` already
exists, setup keeps that file byte-identical and the two flags are not needed.

For paths, setup uses `~/.config/hypr/hyprland.lua`, your XDG data directory and
`~/.local/bin`. If your config or data layout differs, `--hypr-config`,
`--data-dir` and `--bin-dir` take the alternatives; everything else is automatic.
Cursor themes always go in `~/.local/share/icons`, independently of `--data-dir`.
Setup and the login loader verify the actual libXcursor search path; an
`XCURSOR_PATH` override that excludes this directory is refused.

`scripts/setup.py` is the standard setup. It builds every native component,
fetches a pinned Hyprglass commit into an owned temporary directory and builds
the liquid glass from it, installs the library and the cursor theme under
hash-named immutable paths, writes a private manifest, cursor profile and
startup hook, backs up your Hyprland config before appending one clearly marked
managed block to it, and links `computer-use` into `~/.local/bin`.

What setup deliberately does **not** do: it never loads a plugin, never hot-swaps
or unloads one, never restarts or logs out, and never loads anything inside a
`computer-use` session. It also refuses to run at all if `CU_SESSION_TOKEN` is
set or a session record is retained, and it refuses when any plugin is already
loaded, because editing the config could auto-reload one. It holds the session
owner lock for the whole run, so an automation cannot start in the middle of the
build. On an unsupported version, a missing dependency, an already-loaded plugin
or an unreadable config, setup stops with a message instead of guessing.

At your next fresh login the generated hook runs once. It verifies the manifest,
the pinned optics profile, the installed cursor tree and the recorded ABI, checks
that the compositor really did just start, and only then loads the backend. If any
check fails it stops and says why; it does not fall back to a plain background.
Setup never hot-swaps or unloads a plugin the compositor is already running.

## Defaults after that first login

Every session gets, with no further configuration:

- the **session pill** ("Computer use active") overlay,
- the **liquid glass** backdrop,
- an agent cursor on the shared desktop pointer.

### Cursor restoration

A task temporarily switches the desktop cursor to the agent theme, and at the end
of the task the guardian puts **your declared Hyprland cursor** back. GTK is
handled on its own track: the guardian also restores the GTK cursor values it
recorded at task start.

Those restore values come only from the two `--restore-*` flags or from a profile
you wrote yourself. Setup never infers the Hyprland cursor from GTK, and there is
no read-only API that reports the compositor's current cursor back, so no value
is ever guessed. If you would rather keep the file in your own hands, write
`native/agent-cursor.json` before running setup and pass no flags:

```json
{"theme":"your-built-theme","size":32,"restore_theme":"your-current-theme","restore_size":24}
```

Setup preserves an existing valid profile **byte for byte** and never rewrites
it; supplying the same two values again is accepted, different ones are refused.
Without a profile and without the flags, setup refuses before building anything.
A corrupt or unreadable profile fails closed. Nothing in setup or the loader
resumes input automatically after cancellation.

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

For a task that continues in one panel, use `browser observe --scope '#panel'`
and pass `--after-scope '#panel'` to each `browser act` that needs the next refs.
Successful results stay within that panel; failures keep the full-page diagnostic.
If the panel disappears, observe again. `--after-scope` cannot combine with
`--no-after`. See [measured results](docs/optimization-experiments.md#scoped-successful-after-snapshots)
for the output savings and timing limits.

### Session lifecycle and limits

A top-centre "Computer use active" pill identifies agent control. It is
click-through, never takes keyboard focus, and is mandatory by default. Startup
registers a best-effort physical Escape cancellation binding; if it cannot be
installed, a warning is logged and explicit cancellation still works. `computer-use cancel` latches cancellation,
`finish` requests completion, and `resume` only after the user asks to continue.
Esc cancels; it is never an instruction to retry input.

A session shows and restores its visuals without building, downloading or
loading a compositor plugin. Setup prepares the backend and registers the hook;
the hook activates the backend at a fresh login.

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

The three visuals above are the defaults and need no flags. The items here are
secondary, developer-facing paths that standard setup already handles for you.

**A hand-built cursor theme.** `python3 scripts/build-cursor.py THEME_DIR` builds
an XCursor theme (needs Pillow and `rsvg-convert` at build time). To use it
instead of the generated one, place `native/agent-cursor.json` in your CLI tree
with the real restoration settings *before* running setup, so setup preserves it:

```json
{"theme":"your-built-theme","size":32,"restore_theme":"your-current-theme","restore_size":24}
```

Use your actual current theme and size for restoration. The session guardian
restores them when the task ends. This uses the shared desktop pointer.

**Building native components alone.** `python3 scripts/build.py` regenerates
protocol glue from the XML files in `native/`, compiles the pointer, then builds
the `indicator` and `modifiers` binaries. It is the developer/native path: it
downloads nothing and configures **no** automatic visuals. Standard setup calls
it for you.

**Liquid glass from pinned upstream source by hand.** Standard setup fetches the
pinned commit, builds it and registers the login hook itself.
[docs/liquid-glass.md](docs/liquid-glass.md) documents that backend and the manual
build, immutable install and activation steps behind it.

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
| `scripts/setup.py` | standard one-command setup and the fresh-login hook |
| `scripts/visuals.py` | fresh-login loader that validates the manifest before activating |
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
