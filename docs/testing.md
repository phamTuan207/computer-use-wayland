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

## Live fixtures (optional)

Nothing here runs automatically on clone, and none of it assumes a specific
machine. These fixtures own the whole GUI: run them **exclusively**, with no other
automation active, and never against untrusted payloads or third-party accounts.
Physical Escape cancels; there is no automatic resume.

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
full offline suite before you trust the change. Build or install from source and
verify the CLI you run matches your source — for example by comparing file
hashes — because a stale installed CLI will silently keep the old behaviour.

Never hot-swap a native or UI module that a running process has already loaded.
Rebuild, reinstall, and start a fresh session.

Reports are written outside the public repository and must not contain account
data, private paths or window titles.
