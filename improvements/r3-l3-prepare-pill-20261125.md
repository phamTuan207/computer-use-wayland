# G-44: pill live test drive over WebDriver BiDi

Date: Wed 2026-11-25, 09:01:48-09:01:52 +07 (Asia/Ho_Chi_Minh).
Worker: G-44 prepare worker. Gate: R3-L3 re-plan G-44.
Verdict: **PROVEN**.

## Verdict

A live WebDriver BiDi drive on the laptop Zen CAN be done with the pill
visible. The pill text is exactly "Computer use active", verified by
screenshot viewed directly, plus OCR, plus the overlay daemon reply.
The mechanism is the central overlay (`scripts/overlay.py acquire`,
method `BiDi`), called manually before the drive and released after.

Caveat that matters for the run (see section 5): the mechanism is
MANUAL. No BiDi driver enforces it. `scripts/zen_dom.py` (the
single-session manager) contains zero references to overlay/pill, so a
BiDi worker that forgets the acquire drives invisibly. That is the
explanation for last night's 19:58:53 no-pill BiDi drive: the mechanism
existed centrally, nothing in the BiDi path called it. The run must
wrap every BiDi drive with acquire/release, or add a fail-closed gate
to the BiDi path the way W-PILLCDP did for `cdp.mjs`. Do not assume the
driver does it.

## What was driven (live, laptop)

- Zen running on the laptop, `--remote-debugging-port=9222 --marionette`,
  PID 6444. BiDi endpoint `ws://127.0.0.1:9222/session`.
- Work done in Hyprland workspace 2 only (ws2, 0 windows). Zen lives on
  ws1; ws3 (4 agent windows) untouched, no owner tab/window touched,
  navigated, moved, or closed.
- Test script (Node, built-in global WebSocket, no new dependency):
  `improvements/g44-bidi-pill-test.mjs` (also on laptop
  `/tmp/g44-bidi-pill-test.mjs`). Full log on laptop
  `/tmp/g44-bidi-pill-test.log`.
- Timeline (all +07):
  - 09:01:48 switch to ws2 (rc 0, activeworkspace 2, 0 windows).
  - 09:01:49 pre grim, pill absent (OCR 0 matches for the pill text).
  - 09:01:50 acquire pill, see below.
  - 09:01:50 BiDi `session.new` ok; `browsingContext.getTree` = 2 contexts.
  - 09:01:50 `browsingContext.create` type tab, `about:blank`, new
    context, tree = 3 contexts.
  - 09:01:51 grim DURING the drive (pill visible, see evidence).
  - 09:01:51 `browsingContext.close` the new tab, tree back to 2.
  - 09:01:51 `session.end`, WS closed.
  - 09:01:52 re-probe: fresh `session.new` ok then `session.end`.
    The single session slot is free, NO LEAK.
  - 09:01:52 release pill, post grim, pill absent (OCR 0 matches).
  - 09:01:52 back to ws1 (1 window, Zen, as before).

## Evidence

1. Acquire reply (09:01:50, from the overlay daemon on the laptop):
   `{"holders":{"G44:31085":{"acquired":"2026-11-25T09:01:50+07:00",
   "agent":"G44","method":"BiDi","pid":31085}},
   "label":"Computer use active","owner":"daemon","visible":true}`.
   Daemon spawned fresh at 09:01:50.003 (PID 31171).
2. Screenshot DURING the drive, viewed directly by the worker:
   - Full frame on laptop: `/tmp/g44-pill-during.png`
     (1920x1200, 1878869 bytes, taken 09:01:51 while the BiDi session
     was open and the blank tab existed).
   - VM copy, centre top strip 700x150, byte-identical to the laptop
     crop (sha256 `a7c516cdee2c85b680322d6739251ba19268e3659f6c772bf295be8c95dc7150`):
     `improvements/g44-during-tight.jpg`.
     It shows the pill top centre, green dot, text exactly
     "Computer use active".
   - Independent check: tesseract OCR on the full during frame reads
     "Computer use active". OCR on the pre and post frames reads it
     0 times.
3. Release reply (09:01:52): `{"daemon_exiting":true,"holders":{},
   "owner":"none","visible":false}`.
4. Cleanup re-verified by separate SSH after the run: overlay status
   `holders {}, owner none, visible false`; 0 overlay daemon
   processes; 0 test processes; active workspace back to ws1 with
   1 window; Zen context count restored 2.

## Exact pill procedure for a BiDi drive (proven)

Run on the LAPTOP (the pill renders on the laptop screen, not the VM).
The holder must be pid-keyed with a pid that lives on the laptop for
the whole drive, so the daemon never prunes it mid-drive.

1. Switch to ws2 (or stay where the drive happens; the pill is
   layer-shell top centre and shows on any workspace):
   `hyprctl dispatch 'hl.dsp.focus({ workspace = 2 })'`
   with `HYPRLAND_INSTANCE_SIGNATURE` from `/run/user/1000/hypr/`,
   `WAYLAND_DISPLAY=wayland-1`, `XDG_RUNTIME_DIR=/run/user/1000`.
2. Acquire BEFORE any BiDi call, fail closed:
   `python3 ~/computer-use-wayland/scripts/overlay.py acquire --agent <NAME> --method BiDi --pid <PID>`
   Proceed ONLY if exit code is 0 AND the reply JSON has
   `visible: true` AND `label: "Computer use active"`. Anything else
   means refuse the drive, no BiDi session, no input.
3. Open the BiDi session: WebSocket `ws://127.0.0.1:9222/session`,
   `session.new` with `{"capabilities":{}}`.
4. Drive. Only ever touch a tab the drive itself created, never an
   existing tab. Harmless pattern proven here: create one
   `about:blank` tab, read state, close it, confirm the context
   count returns to the pre-drive count.
5. While the session is open, screenshot with `grim` to prove the
   pill is visible during the drive.
6. End the session in a finally block: `session.end`, close the WS.
   Re-probe with a fresh `session.new` + `session.end` to prove the
   single session slot is free (a leaked session blocks ALL remote
   control until Zen restarts).
7. Release AFTER the session is ended:
   `python3 ~/computer-use-wayland/scripts/overlay.py release --agent <NAME> --method BiDi --pid <PID>`
   (same agent and pid as the acquire, or the holder is not removed).
   Confirm `overlay.py status` shows `holders {}` and
   `visible: false`.
8. Return to ws1 if the drive moved workspaces.

A ready-made implementation of exactly this is
`improvements/g44-bidi-pill-test.mjs` (Node, no dependencies beyond
the repo's `overlay.py` and the laptop's Node 26 global WebSocket).
It does steps 1-8 with fail-closed acquire and finally-block
session/pill cleanup, and logs every step with timestamps.

## What was tried

- Way 1 (this test, worked): manual central-overlay acquire with
  method `BiDi`, pid-keyed, around a raw BiDi session. PROVEN.
- Background check, not a separate live attempt: the CDP path already
  has a fail-closed gate (`cdp.mjs`, W-PILLCDP) that acquires the same
  central overlay automatically; the BiDi path has no equivalent.
  `grep` over `scripts/zen_dom.py`, `scripts/zen_backend.py`, and
  `scripts/zen_cli.py` finds no overlay/pill reference at all.
  No second live drive was needed: the first live attempt passed
  end to end in 4 seconds, so no retries were consumed.

## Gaps and notes (honest)

- The test script's own `status` log lines read `null`: its JSON
  parser took only the last line of `overlay.py status`, which prints
  pretty multi-line JSON. The acquire/release replies are single-line
  JSON and parsed correctly; the nulls are a logging artifact in the
  test script only. Final status was re-verified by a separate SSH
  call (holders {}, visible false).
- `session.new` was the only BiDi write besides the blank-tab
  create/close. No click, no typing, no navigation of any existing
  tab was attempted; the gate asked for a small harmless drive action,
  and the blank-tab create/close plus state reads are exactly that.
- No OpenRouter was used or proposed. No personal info in any file.
  The report and the test script log context counts only, never tab
  titles or URLs.
- The file `improvements/g44-during-tight.jpg` is screenshot
  evidence for this gate, kept in the worktree; the full frame stays
  on the laptop at `/tmp/g44-pill-during.png`.

## Recommendation to the parent (not a decision)

Gate G-44 passes as a procedure. For the run, either (a) every BiDi
worker must run the acquire/release wrapper above (copy the proven
script pattern, do not hand-roll it), or (b) add a fail-closed pill
gate to the BiDi entry point used by the run, mirroring W-PILLCDP for
CDP. Option (b) is the durable fix; option (a) is enough for task 1
if the wrapper is actually used. The deviation fallback (raw BiDi
read-only, live drives only through a computer-use session) is NOT
needed: the pill mechanism for BiDi drives exists and works.
