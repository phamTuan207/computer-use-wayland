# Testing

Most of the suite is offline and runs from the repository root:

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
```

No session, browser or running GUI is needed. Some checks still need real build
dependencies — Python with Pillow, a C compiler, `libxkbcommon`, Node and
`pkg-config` with Cairo development files — because they compile and run native
and Node code. No compositor is
required.

## Building only the wtype helper

`native/wtype` is a gitignored build artifact (`.gitignore`), not in the repo,
so a fresh checkout has no helper and the P2/keyboard suites fail with 21
errors, all `RuntimeError: private wtype helper is missing: .../native/wtype`
(the error names this section). The full `python3 scripts/build.py` stops
before wtype on machines without `gtk4-layer-shell-0`: it builds the pointer,
then fails at `pkg-config --cflags --libs gtk4-layer-shell-0 gtk4
wayland-client` with exit status 1. Build only the wtype part instead, from
the repo root (needs `cc`, `wayland-scanner`, `patch`, and
`pkg-config wayland-client xkbcommon`; no download, the source is vendored
under `native/vendor/wtype`):

```sh
wayland-scanner client-header native/keyboard.xml native/keyboard-protocol.h
wayland-scanner private-code native/keyboard.xml native/keyboard-protocol.c
tmpdir=$(mktemp -d)
patch --batch --fuzz=0 --output "$tmpdir/main.c" \
  native/vendor/wtype/main.c native/vendor/wtype/keyboard-correction.patch
flags=$(pkg-config --cflags --libs wayland-client xkbcommon)
cc -Wall -Wextra -O2 -I native -o native/wtype "$tmpdir/main.c" \
  native/keyboard-protocol.c $flags
rm -rf "$tmpdir"
ls -la native/wtype
```

Run log on this VM, 2026-11-22 13:01:49 +07: `patching file .../main.c
(read from native/vendor/wtype/main.c)`, `cc flags: -lwayland-client
-lxkbcommon`, `wtype built`, `native/wtype` 35984 bytes. The `cc` unused
parameter warnings are from the vendored source and are harmless. After
this, `python3 -m unittest test_p2_element_ref` runs without the 21
wtype errors. The same commands are the wtype block of
`scripts/build.py`; if the full build ever succeeds on your machine,
it produces the same helper.

## What the suite actually exercises

It is a mixed suite, not a uniformly mocked one:

- **Real C** — `native/` sources are compiled and the resulting helpers are
  exercised where a mock would hide a compile error.
- **Fake Wayland** — compositor and protocol interactions are simulated. This
  proves our logic against the model, **not** compatibility with a real
  compositor ABI.
- **Real Node, fake CDP** — `scripts/cdp.mjs` runs for real against a fake
  WebSocket/DOM harness.
- **Mock tests** — many units patch their dependencies.

Do not assume every subprocess is mocked, and do not assume none are real.

One test is gated: the hyprglass patch-applicability check skips unless you point
`CU_HYPRGLASS_SOURCE` at a pinned upstream checkout.

## Default visual setup

Setup and login tests use temporary files and mocked compositor RPC. Cursor
tests also render real XCursor images, decode them with libXcursor and probe its
real search path when the dependencies are available. Lua startup-hook tests
use a real interpreter with a fake `hl` API. These checks do not load a plugin.

An isolated setup acceptance run additionally built all three native helpers,
the pinned glass plugin and the immutable theme with real tools, and loaded the
cursor by name with real libXcursor. Only its empty plugin inventory, temporary
installation paths and login desktop effects were fixtures. The running
compositor, installed plugin and real configuration were unchanged. This proves
artifact preparation; activation at a real fresh login remains unverified.

Setup tests declare their restore values explicitly with `--restore-theme` and
`--restore-size`, or through a profile written by the test itself. No test infers
a Hyprland cursor from GTK, and none asserts a cursor value from a real host; the
GTK values a task captures and restores are exercised through fakes.

## Live fixtures (optional)

Nothing here runs automatically on clone, and none of it assumes a specific
machine. These fixtures own the whole GUI: run them **exclusively**, with no other
automation active, and never against untrusted payloads or third-party accounts.
Physical Escape cancels; there is no automatic resume.

### Background/SSH environment proof

There are two different environments in this proof. A **bare SSH client** is
the `env -i` Python process that runs the test. It starts with identity and
`PATH` only; the installed relay service keeps its own existing environment.
A **bare broker** is a separate test-owned process that the fixture starts with
that same small environment and a private socket under `/tmp/opencode`. It
shares the normal `~/.cache/agent-computer-use` state root so it still meets the
real desktop-owner gate. The `stale` case adds the current runtime and display
with a signature that does not exist, then proves the broker selects the live
session.

Run these only when the installed broker is idle and no other automation owns
the desktop. The fixture checks the cancellation latch, retained snapshot,
current donor, compositor ABI, plugins, and cursor guard before it starts. A
blocker is reported as `blocked`; do not clear the latch or recover another
task to make the proof pass. Each case starts a private test broker, runs two
start/doctor/finish cycles, and verifies the driver environment and clean
cleanup. The only driver command is read-only `doctor`; the fixture does not
take screenshots, move the pointer, type, focus windows, or launch apps.

```sh
env -i HOME="$HOME" USER="$USER" LOGNAME="$USER" PATH=/usr/bin:/bin \
  PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B tests/envsteal_live.py \
  --case bare --repeat 2
env -i HOME="$HOME" USER="$USER" LOGNAME="$USER" PATH=/usr/bin:/bin \
  PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B tests/envsteal_live.py \
  --case stale --repeat 2
```

These commands are opt-in and are not part of `unittest discover`. A passing
JSON proof includes the imported source paths and hash asserted by the
test-owned broker, all 18 driver keys matched to the verified donor, tuple and
readiness results, the doctor result, and clean finish status. A full-key
source that lacks any allowlisted value is blocked with the missing key names.

### GTK demo, two terminals

The fixture and its driver share one temporary directory. Create it once:

```sh
demo_dir=$(mktemp -d)
```

In the first terminal, start the inert GTK fixture:

```sh
python3 tests/demo.py --layout "$demo_dir/layout.json" --events "$demo_dir/events.json"
```

In a second terminal, with the **same** `demo_dir` value, drive it inside a
session:

```sh
computer-use session -- python3 tests/demo_driver.py \
  --layout "$demo_dir/layout.json" --events "$demo_dir/events.json"
```

### Browser fixture

`tests/browser_driver_live.py` requires an outer session; it refuses to start
without one:

```sh
computer-use session -- python3 tests/browser_driver_live.py
```

### Browser task benchmark

This one owns its own session and **must be run outside an existing one**:

```sh
report_dir=$(mktemp -d)
python3 tests/browser_task_benchmark.py --report "$report_dir/report.json" \
  --modes batch batch-no-after --controls 0
```

Write reports to a directory outside the public repository, and give each run a
fresh path. By default the benchmark drives the **source** CLI; `--cli` points it
at an installed CLI instead, and the report records which. Setup and the initial
observe sit outside the timed span, and cold and warm runs are reported
separately. Result byte counts are bytes, not billed tokens. See
[optimization-experiments.md](optimization-experiments.md).

Proof matters: these fixtures verify the application's actual events and result
state, not merely a zero exit code. A fixture that only exits cleanly has not
proven anything about the UI.

## Known limits

Only Hyprland was tested. Multi-monitor layouts, fractional scaling, rotated
outputs and physical input hardware are unverified here unless you have validated
them on your own setup. Native accessibility depends on each application actually
exposing AT-SPI.

For ordinary browser fields prefer `set_value`: it is focus-independent but
dispatches synthetic, untrusted events. `fill` sends trusted keyboard input and
carries a focus race, so use it only where trusted behaviour is required and the
target is controlled, and verify with an app-result assertion. Desktop `wtype` can
lose characters through key collisions, and non-BMP emoji are refused on that
route — use browser `set_value`/`fill` or the accessibility setter instead.

Focus guards, screen guards, cancellation and IME behaviour are described in the
README and [skill/references/usage.md](../skill/references/usage.md). There is no
automatic retry or replay after a failure or an Escape.

## Customising the code

Change code and its focused tests together, then run the focused tests and the
full offline suite before you trust the change. In the dev loop, run the
changed module's tests first (for example `python3 -m unittest
tests.test_<module>`), then the full discover above before any gate, review,
or push: a module run proves speed, not selection safety, so automatic
coverage-based test selection is not used and the full discover stays
mandatory at every gate. Build or install from source and
verify the CLI you run matches your source — for example by comparing file
hashes — because a stale installed CLI will silently keep the old behaviour.

Never hot-swap a native or UI module that a running process has already loaded.
Rebuild, reinstall, and start a fresh session.

Reports are written outside the public repository and must not contain account
data, private paths or window titles.
