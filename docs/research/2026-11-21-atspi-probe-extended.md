# AT-SPI probe, extended run and exact limits on this machine

Date: 2026-11-21. Machine: the clone2 headless VM (Linux, Python 3.12.3).
Companion code: tests/atspi_probe.py, extended in this batch with a
staged session mode. Related earlier work, both on branch coord-clone2-setup:
tests/atspi_prototype.py and
docs/research/2026-11-21-atspi-desktop-control.md.

## What was done

tests/atspi_probe.py previously imported pyatspi at module top level,
so on a machine without pyatspi it died with a traceback before it
could record anything. It now:

- imports pyatspi lazily and records the exact import error,
- keeps the dump, click, type and full modes unchanged when pyatspi
  is present, and exits 2 with a JSON log line when it is not,
- adds a session mode that runs a timed, staged bring-up: audit the
  environment, try the raw desktop, start Xvfb, start a private
  session bus with dbus-daemon, probe the a11y bus with gdbus,
  launch a real GUI app inside the virtual session, then attempt
  the accessible tree read and a button press through do_action.
  Every stage logs wall clock, per-stage elapsed and total elapsed,
  and every failure carries its exact error.

## Environment, verified directly on 2026-11-21

- DISPLAY unset, WAYLAND_DISPLAY unset, DBUS_SESSION_BUS_ADDRESS
  unset, XDG_RUNTIME_DIR unset. No X, Wayland or session bus exists
  in the raw environment.
- No at-spi processes running.
- Binaries present: Xvfb at /usr/bin/Xvfb, dbus-run-session,
  dbus-daemon, gdbus, dbus-send.
- Binaries missing, confirmed by a full filesystem search, not only
  PATH: at-spi-bus-launcher and at-spi2-registryd exist nowhere on
  this machine. No D-Bus a11y service files exist either.
- Packages present: at-spi2-common 2.52.0 (documentation and data
  only, no daemons), libatk-bridge2.0-0t64, libgtk-3-0t64.
- Packages missing: at-spi2-core, python3-gi, python3-pyatspi.
  apt-cache policy shows no installation candidate for at-spi2-core
  or python3-gi in the configured mirrors, so the daemons cannot be
  installed from the current apt state. An apt-get update attempt
  hit ignored InRelease files on the mirror and its follow-up was
  not approved in time, so no install was performed; any claim that
  apt could fix this later is UNVERIFIED.
- pyatspi is not importable by the system python3 or by the venv at
  ~/workspace/tools/venv: ModuleNotFoundError: No module named
  'pyatspi'. The gi module is likewise missing.
- pip cannot provide pyatspi: pypi.org/simple/pyatspi returns HTTP
  404, the project is not published on PyPI, and the venv pip
  install attempt failed with "No matching distribution found".
  pyatspi only ships as a system package, which loops back to the
  missing apt candidate above.
- GUI apps present: LibreOffice at /usr/bin/libreoffice, and the
  Firefox 160.0.1 binary at ~/workspace/tools/firefox/firefox.
  No xterm, gedit or other small GTK app is installed.

## Raw desktop attempt, no virtual session

Command: python3 tests/atspi_probe.py --mode full
Wall clock: 2026-11-21T11:52:13Z, total elapsed 0.062 s, exit 2.
Single log line: op import_pyatspi, ok false, error
"ModuleNotFoundError: No module named 'pyatspi'".
Result: FAILED at the import, before any bus or tree access. The
raw desktop offers nothing to connect to in any case: no display,
no session bus, no a11y bus.

## Virtual session attempt, staged

Command: python3 tests/atspi_probe.py --mode session
Wall clock: 2026-11-21T11:52:16Z to 11:52:21Z, total elapsed
5172.1 ms, exit 2.

| Stage | Result | Stage elapsed | Detail |
| --- | --- | --- | --- |
| audit_environment | ok | 1.2 ms | env and binary audit as above |
| raw_desktop_registry | FAILED | 0.0 ms | pyatspi not importable |
| start_xvfb | ok | 101.6 ms | Xvfb up on display :97, X socket appeared |
| start_session_bus | ok | 8.1 ms | dbus-daemon session bus forked, address issued |
| check_a11y_bus | FAILED | 11.2 ms | at-spi-bus-launcher missing; gdbus call to org.a11y.Bus.GetAddress returned org.freedesktop.DBus.Error.ServiceUnknown, "The name org.a11y.Bus was not provided by any .service files" |
| launch_gui_app | ok, process level only | 5015.1 ms | Firefox started under Xvfb with the session bus address and stayed alive for the 5 s observation window; no window-level proof possible, no X query tools installed and no tree to read |
| read_accessible_tree | FAILED | 0.0 ms | pyatspi not importable |
| press_button_do_action | FAILED, not attempted | 0.0 ms | no tree was read, so there is no button object to press |

Cleanup verified afterwards: no Xvfb, Firefox or dbus-daemon
processes left running, the X socket directory is empty again.

## Precise limits

1. The display and bus layers are solvable here: Xvfb and a private
   session bus both start in about 110 ms combined, and a real GUI
   app runs under them.
2. The accessibility layer is absent at two independent points.
   First, the server side: at-spi-bus-launcher and
   at-spi2-registryd are not installed, so org.a11y.Bus can never
   be owned and no application can register an accessible tree.
   Second, the client side: pyatspi is not installed and cannot be
   obtained from pip at all, or from apt in its current state.
   Either gap alone is fatal; both are present.
3. Because of limit 2, no accessible tree was read on this machine
   in this run: tree reading is FAILED, not partially done.
4. No real button press happened: FAILED, not attempted, because a
   press needs a tree node. Nothing in this report claims a press.
5. The Firefox launch is verified at process level only. Whether
   its window rendered correctly under Xvfb is UNVERIFIED, and
   Firefox would only publish a tree once an a11y bus exists and
   its accessibility engine is active, neither of which held here.

## What would unblock live AT-SPI control

- Install at-spi2-core (provides at-spi-bus-launcher and
  at-spi2-registryd) and python3-pyatspi (or python3-gi plus the
  Atspi typelib) from a working apt mirror, then rerun the session
  mode. The staged probe is already shaped for that rerun: stages
  check_a11y_bus, read_accessible_tree and press_button_do_action
  are exactly the ones that would turn green.
- On the coordinator machine with a real desktop session, none of
  these gaps apply, and the original full mode of the probe remains
  the right tool there.

## Bottom line

On this machine AT-SPI control stops at the accessibility layer:
virtual display and session bus work and are fast, a real app runs
inside them, but with no AT-SPI daemons and no pyatspi client there
is no tree to read and no button to press. Both failures are
recorded with their exact errors in the probe output, and the
extended probe now states these limits by itself on every run.
