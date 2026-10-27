## Automation sessions

Standard setup and a fresh login enable the pill, liquid backdrop and
session-owned agent cursor lease, released after the driver stops during normal cleanup.
With no `native/agent-cursor.json`,
setup requires `--restore-theme YOUR_CURRENT_HYPRLAND_THEME --restore-size
YOUR_CURRENT_HYPRLAND_SIZE`, declared once: the compositor's cursor cannot be read
back, and it is never guessed from GTK. An existing valid manual profile is kept
byte for byte and needs no flags. Each session holds the native image lease
without changing global theme or GTK settings; the profile and asset gate alone
is not sufficient, and a backend that is not idle never starts a driver.
Pre-lease snapshots still restore their declared Hyprland values, where the
compositor restoration is mandatory and GTK restoration alone never proves
compositor state. Every session requires a configured, loadable agent cursor
plus the ready overlay before its driver can start. Losing the lease or the
overlay stops the running session. Existing installations first-load only the
guard through the guarded helper after the pinned ABI check (no unload or
reload of glass). The repo CLI reads only its own tree's
`native/agent-cursor.json`, never an installed copy.
There is one shared pointer. Do not operate simultaneously.

Run the whole task driver as `computer-use session -- DRIVER [ARGS...]`, not a
separate session around each action. Its child commands inherit session ownership.
Input commands require a live session; standalone capture remains available.
Sessions show a click-through layer-shell badge "Computer use active"; the badge takes
no keyboard focus and lets clicks through. The badge surface asks the compositor for a
per-surface backdrop blur (`ext_background-effect-v1`), applied only inside the rounded
pill. The compositor holds the session's owned agent image for the task
and releases it after the driver stops during normal cleanup; no marker is
drawn and the screen scale never changes. Window and screen captures both hide the badge
and the software cursor
for the shot and restore both after the native presented-frame acknowledgement fences the image — that hide/show fencing stays the only
exception to overlay visibility; hiding clears the blur region together with the pixels, so no blurred copy
survives in the capture, and no cursor pixels leak into the PNG. A cursor command failure
prevents the screenshot and ends the driver instead. Outputs are taken once at startup: adding or removing a
monitor mid-session ends the indicator.
`finish` requests completion; `cancel` latches cancellation. Best-effort physical
Escape works throughout the session, without a timer; installation failures warn.
The wrapper waits for input to stop and the temporary binding to be removed.
Desktop validation refusals before focus/input are typed preflight refusals: they return
`recoverable: true, completed: 0` and the driver keeps the session alive: correct the invalid
request while the observation is still valid (90 s), or observe again once it expired. An
exact transient guard refusal (`screen changed`/`screen_changed` or
`focus changed`/`focus_changed`, with no `capture_error` or `ime_restore_failed` in the
result) also keeps the session alive but arms a re-observe requirement: run a fresh
`observe` command before any further input — desktop, browser and accessibility `act` all
check it, and a following desktop `act` must reference that new observation. The failed
action's `after` image is evidence to inspect, not a substitute for that observe.
Continuation is the driver's own decision (typed preflight provenance or the exact
transient match), never guessed from message text alone: any other error — including one
whose text merely looks recoverable — ends the session; the MCP bridge reports
`session_ended` with reason, exit code, log path and captured stderr, and its `status`
operation reports `session_active`. `finish` on an inactive session succeeds as a no-op.
Use `recover` for retained records
after cleanup failure. Recover older magnifier records with the previous version
before upgrading; the new version preserves and rejects them.
Browser adapter timeout is capped at 60 seconds; split larger batches.

`computer-use status` is a read-only local-state command returning
`{"ok":true,"cancelled":<bool>}`: `cancelled: true` once Esc or `cancel` latched.
When latched it also carries a `cancellation` metadata object (`set_at`, `pid`,
`session_token`, `source`, plus `clear_with: "computer-use resume"` and an
instruction to clear only after the user asks to continue); a legacy or corrupted
latch file still reports `cancelled: true` with an unknown source. It
reports the cancellation latch, not whether a session or overlay is active. It
never clears cancellation; only user-requested `computer-use resume` does that.

# Commands and schemas

## Interactive agent driver

Read [Interactive agent driver](session.md).

## Chromium

Read [Chromium](browser.md).

## Native accessibility

Read [Native accessibility](accessibility.md).

## Desktop

Read [Desktop](desktop.md).

## Troubleshooting

Read [Troubleshooting](troubleshooting.md).
