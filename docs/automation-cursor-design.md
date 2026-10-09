# Automation cursor lifecycle

The previous setcursor design is superseded by readable cursor zoom. The runtime
implementation is in scripts/cursor_session.py; lifecycle regressions are in
tests/test_cursor_session.py. No live desktop changes are part of these tests.

The session wrapper runs the automation driver, not a single action. A separate
guardian owns cursor.lock, saves the original zoom before any write, installs
physical Escape cancellation, then sets zoom factor 5 with Lua eval. The driver
starts only after the guardian confirms its process group registration. A gate
pipe prevents driver input if the wrapper dies during this handshake.

Success, failure, refusal, explicit finish, Escape, and wrapper signal/death end
the session. Stop markers reject subsequent commands. The driver group is stopped
before cursor restore. The guardian watches pipe EOF independently of the wrapper;
the surviving wrapper provides fallback when the guardian dies. Saved originals
are never overwritten by a concurrent session. Restoration retries and verifies
the readable value; a failed restore retains its snapshot for explicit recover.

The pill, stale-daemon probe, capture suspension, glass-plugin loading and reload
are removed. Captures call grim without -c, so zoom needs no capture cleanup.
Focus checks up to five times with 40 ms sleeps after dispatch. Browser adapter
execution timeout is capped at 60 seconds; it is not a measured maximum lock time.

OPEN: visual cursor visibility across real applications and physical outputs.
OPEN: simultaneous death of wrapper and guardian, unavailable compositor, or
system failure cannot guarantee automatic restore. Durable snapshot recovery is
provided, but no process can promise cleanup after all processes have been killed.

## Capture-path verification, 2026-10-09

Only two production grim calls remain: scripts/cu.py:217 (window) and
scripts/cu.py:241 (monitor). The preflight and final action captures reuse those
functions at scripts/cu.py:390 and scripts/cu.py:457. Neither call includes -c;
there is no tool-owned layer-shell surface or capture suspension path. The old
overlayctl.py is removed; physical Escape cancellation now lives in
scripts/cancel_hotkey.py:22, imported at scripts/cursor_session.py:119.

Offline validation passed: 31 unittest cases and tests/capture.py, including
late focus settlement (tests/capture.py:61), capture without overlay subprocesses
(tests/capture.py:108), and 32-action adapter timeout caps (tests/capture.py:121).

Live observe timing, 2026-10-09. Measured on a real desktop session (monitor
eDP-2, 1920x1200, scale 1) with a read-only harness: seven runs of
`observe --screen eDP-2`, each with a throwaway XDG_CACHE_HOME that is removed
on exit. No act, focus change, or pointer movement.

- per-run wall time (ms): 173.2, 174.6, 171.7, 168.3, 167.4, 176.1, 169.9
- median wall time: 171.7 ms
- median capture_ms (grim plus decode inside scripts/cu.py:239-245): 41 ms
- returned image: 1280x800

The reported 376 ms observe remains the user's baseline, not a measurement of
this working tree. Against it, median wall time here is about 54% lower
(2.19x faster); treat the delta as indicative because the methods may differ.
The roughly 530 ms act baseline is still unmeasured.
