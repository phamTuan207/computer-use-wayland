# AT-SPI self-contained session probe, 2026-11-21

One command that builds a working AT-SPI session from a clean
state (Xvfb plus D-Bus plus AT-SPI registry plus Firefox 160.0.1),
runs the probe, and cleans up. No inherited display or bus is used,
so the result does not depend on whatever session the caller
happens to be in.

Code: tests/run_atspi_session.sh (entry point) and
tests/atspi_probe.py (probe, modes dump, click, type, full,
dismiss, session). Fixture: tests/bidi_fixture.html.

## Why this exists

Batch 3 proved AT-SPI tree reading and clicking live, but its doc
omitted the session setup recipe. The coordinator and a fix agent
then failed to reproduce it three times with dbus-run-session:
find_app timed out after 30 s even though Firefox was running and
the bus answered. Council 3 in batch 4 found the working recipe
and reproduced all three batch 3 claims. This task turns that
recipe into a script anyone can run, and fixes two more bugs the
first end to end runs exposed (see "Bugs found while building
this").

## The recipe

- Start Xvfb on a free display (:97, :98 or :99).
- Start a private session bus with dbus-launch, not
  dbus-run-session. dbus-run-session was the failing path.
- Export DISPLAY, DBUS_SESSION_BUS_ADDRESS, GNOME_ACCESSIBILITY=1
  and GTK_MODULES=gail:atk-bridge.
- Activate the AT-SPI registry BEFORE Firefox starts, with a gdbus
  call to org.a11y.Bus GetAddress. That call triggers D-Bus
  activation of /usr/libexec/at-spi-bus-launcher, which starts
  at-spi2-registryd. If Firefox starts first it can miss the
  registry and the tree stays empty (childCount 0).
- Launch Firefox on the fixture with a fresh profile, wait for the
  first-run spotlight dialog to populate, dismiss it, wait for the
  fixture document to appear, then run the probe.

## Prerequisites

- Xvfb, dbus-launch, gdbus, python3, pyatspi, at-spi-bus-launcher
  (at /usr/libexec/at-spi-bus-launcher, not on PATH).
- Firefox 160.0.1 at /tmp/firefox/firefox (or pass --firefox PATH).
- The script checks all of these first and exits 2 with the exact
  install command when something is missing:
  sudo apt-get update && sudo apt-get install -y at-spi2-core python3-pyatspi dbus-x11 xvfb
- Note: apt-installed at-spi2-core, pyatspi and dbus-x11 do NOT
  survive a VM restart on this machine. Only /tmp/firefox survives.
  After a restart, reinstall the three packages and re-download
  nothing; the script will tell you if they are gone.
- /tmp needs a few MB free for the Firefox profile and the X
  socket. One run failed while /tmp was at 100 percent (Xvfb
  socket never appeared); at 79M free the same run passed.
  The script now checks this up front in the prereq stage: /tmp
  must be writable and have at least 50 MB free, and it fails
  fast with the exact free KB instead of a generic "X socket
  never appeared" 10 s later.

## How to run

From the repo root, with a clean environment (no DISPLAY, no
DBUS_SESSION_BUS_ADDRESS inherited):

  env -i HOME="$HOME" PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin bash tests/run_atspi_session.sh --mode both

Modes: dump (tree read only), full (click plus type plus
readback), both (default, dump then full). Exit 0 means the
session works (tree read and Action click verified). Exit 2
means the session itself failed. A failing type step does NOT
make the wrapper exit 2, because typing is broken in Firefox
itself (see "Known limits").

## Expected output, measured 2026-11-21

Two consecutive clean runs of --mode both, plus two of --mode
dump, all from a clean environment. Wall clock times are UTC.

Run 3, --mode both, 12:04:06Z, wrapper exit 0, total 19212 ms:

| Stage | Result | Stage elapsed |
| --- | --- | --- |
| prereq | ok | 120 ms |
| start_xvfb | ok, display :97 | 107 ms |
| start_session_bus | ok | 46 ms |
| activate_a11y_registry | ok, registry answered before Firefox | 35 ms |
| launch_firefox | ok | 5038 ms |
| wait_document | ok, document web named BiDi fixture present | 12001 ms |
| probe_dump | ok, 125 nodes | 730 ms |
| probe_full | ok (click), rc 2 from the type step | 1074 ms |
| session_verdict | ok, session works | 9 ms |

Probe steps inside the full run: find_app 52.1 ms, find_button ok,
click ok, click 3.1 ms, find_field ok (Name), type_editabletext
FAIL "EditableText returned True, read back ''", keysym fallback
FAIL "read back ''", final_readback paragraph "Counter: 1",
counter_seen true, entry "".

Run 4, --mode both, 12:04:29Z, wrapper exit 0, total 13272 ms:
wait_document 6658 ms, probe_dump 125 nodes in 176 ms, probe_full
606 ms, click 0.4 ms, same type failure, counter_seen true.

Run 5, --mode dump, 12:05:09Z, wrapper exit 0, total 12686 ms:
wait_document 6490 ms, probe_dump 125 nodes in 587 ms.
Run 6, --mode dump, 12:05:45Z, wrapper exit 0, total 13306 ms.

Cleanup verified after every run: 0 Firefox, Xvfb or dbus-daemon
processes left from the run, no profile or runtime directory left
under /tmp, no X socket left.

## What each mode proves

- dump: the tree is readable at all. Expect 125 nodes on the
  fixture, including the frame, the toolbars, the address bar
  combo box, and three document web nodes (one per tab plus an
  empty one). find_app takes about 5 to 75 ms, the walk about
  28 to 56 ms.
- click (inside full): the Action interface works. The Increment
  button is pressed through do_action, verified by the paragraph
  reading "Counter: 1". Click takes 0.3 to 3.1 ms.
- type (inside full): expected to FAIL on Firefox 160.0.1, see
  below. The failure is recorded with its exact detail, not
  hidden.
- dismiss: dismisses the first-run spotlight dialog and nothing
  else. Added in this task so the wrapper can poll for readiness
  without side effects. click and full modes must not be used as
  a readiness poll: they press the fixture button and would
  change the counter the full run later checks. Exit codes: 0
  when a dialog button was found and clicked, 3 when no dialog
  button is present (the dialog is already gone, which is the
  wanted state), 2 when a button was found but the click failed.
  The wrapper breaks its poll on 0 and 3 and retries only on 2.
- session: the older staged diagnostic from clone2, kept
  unchanged. It audits the environment and records where a
  machine stops. It does not run the live probe; use the wrapper
  script for that.

## Bugs found while building this

1. find_in_document searched only the FIRST document web node.
   Firefox exposes one document web node per tab, plus an empty
   one for about:blank or a not-yet-loaded tab, and the empty one
   comes first in tree order. The probe looked only inside the
   empty document, so Increment and Name were never found even
   though the tree held them. Fixed in tests/atspi_probe.py:
   find_documents collects all document web nodes and
   find_in_document searches every one of them. Chrome UI is
   still never searched, so the address bar cannot be mistaken
   for the fixture field.
2. The first-run spotlight dialog blocks the tab content until
   dismissed, and its Continue button takes about 10 s to appear
   in the tree. The wrapper now polls --mode dismiss until the
   dialog is gone, then polls dump until the document web node
   named "BiDi fixture" appears, and only then runs the probe.
   Before this fix the wait failed after 30 s with no document
   web node in the tree.

## Fixes after the batch 5 redteam review, 2026-11-21

The redteam found 4 bugs in the wrapper (docs/batch5-redteam-
20261121.md, findings 13, 14, 15, 21). All 4 are fixed in
tests/run_atspi_session.sh and tests/atspi_probe.py:

1. The dismiss poll could not tell "no dialog" from "dismiss
   failed": --mode dismiss returned 2 for both, so the wrapper
   retried 15 times when the dialog was already gone. Now the
   probe returns 3 when no dialog button is found, and the
   wrapper breaks its poll on 0 (clicked) and 3 (already gone)
   and retries only on 2 (click failed). The wait_document stage
   line now records the dismiss exit code as dismiss_rc.
2. A wait_document failure did not gate: the script logged the
   stage as failed and ran the probe stages anyway. Now it exits
   2 right there with a clear message, instead of spending probe
   time on a dead session. The final verdict is unchanged
   (exit 2), only the wasted work is gone.
3. The prereq stage did not check /tmp writability or free
   space, although the doc documents a /tmp-full failure mode.
   It now requires /tmp writable and at least 50 MB free and
   fails fast with the exact free KB. The passing prereq line
   records tmp_free_kb.
4. The script header comment said "full mode exits 2 even when
   the session is fine", which contradicted the doc and the code.
   The probe's full mode does return 2 when typing fails, but
   the wrapper exits 0 when the session works. The comment now
   says exactly that.

Verification of these fixes (live Firefox is down: it segfaults
on startup since about 12:29 UTC on 2026-11-21, same crash as
the Y10 retry log, so no live wrapper run was possible): bash -n
clean on the script, py_compile clean on the probe, a stubbed
unit test of --mode dismiss returns 3/2/0 for no-dialog /
click-fails / click-ok (ALL PASS), and a standalone run of the
poll loop and /tmp check logic (break after 1 call on rc 3,
retry then break on rc 0, all 15 tries on rc 2; /tmp check
passes at 123860 KB free and fails with exact numbers when the
threshold is forced high). The fixes are code-only until a live
run is possible again.

## Known limits

- Typing through EditableText is BROKEN on Firefox 160.0.1.
  setTextContents returns True but the read-back is empty.
  This is Mozilla Bug 2087495 (guard IsTextRole() inverted,
  fixed in the 161 branch). The keysym fallback also fails
  ("read back ''") under the Xvfb keymap. Both failures are
  reproduced by this probe on every run. Use BiDi for typing
  until the fix lands in the Firefox base. Do not use this probe
  to claim typing works.
- The probe runs under Xvfb (X11). Nothing here proves Wayland
  behaviour. On Wayland, tree reading and Action clicks go over
  D-Bus and should still work, but XTest-style key synthesis
  and xdotool will not.
- The probe reads the live tree, so timings depend on machine
  load. find_button took 2038.7 ms once when the tree was still
  settling, and 126.8 ms on a settled tree.
- Zen is not tested here. Zen shares the Gecko stack with
  Firefox, so tree reading and clicking should transfer, but
  the Zen sidebar, workspaces and base Firefox version are
  UNVERIFIED.
- The wrapper always uses a fresh Firefox profile, so every run
  sees the first-run spotlight. That is intentional: it proves
  the full path from a clean state.
