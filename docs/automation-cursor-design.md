# Automation session: indicator and clean capture

Current design: a session-owned, click-through layer-shell surface per output
draws a top-center pill only. The pointer itself is never overdrawn: the user's
normal cursor is the single cursor, and no global cursor theme or screen-scale
setting is changed. The pill requests a per-surface backdrop blur through
`ext_background_effect_manager_v1`; hiding it clears the blur region together with
the pixels. Capture clears the surface buffer, waits for
`wp_presentation_feedback.presented` on each output, runs grim, then restores
visibility in a finally block. EOF and parent-loss signals end the helper.
Monitor hotplug ends the session rather than allowing an unmarked output.

Material and light reference only, no code or asset vendored:
<https://github.com/emilkowalski/skills> (Apple design skill) and
<https://github.com/sdegenaar/liquid_glass_widgets> (Flutter liquid-glass
widgets). The shipped look is plain Cairo drawing on a compositor blur surface;
the Flutter widget and its shader-based refraction are not ported.

Current measurements and limits: [indicator-validation.md](indicator-validation.md).

The historical removal decision below describes the previous version, not the
current overlay. The prohibition on magnifying the whole screen remains.

## Historical removal decision

Decision, 2026-10-09: use the user's normal cursor. The actions themselves are the
visible signal. Nothing changes screen scale, cursor theme, or cursor size; no
layer-shell surface is created and captures need no suspension.

The removed `cursor:zoom_factor` mechanism magnified the entire desktop. Omitting
the cursor from grim did not omit that screen transformation. Claims that it
only enlarged the pointer, or was invisible in captures, were incorrect.

## Alternatives and their costs

- A small static Quickshell corner badge would avoid the old 282x38 top-centre
  pill's placement, but still cover pixels in captures. Suspending it would add
  capture transitions and crash cleanup. A static badge's effect on refusal rate
  has not been measured; no claim of safety is made for it. It is not shipped.
- `hyprctl setcursor` has no corresponding current-theme readback here. The loaded
  user config is `~/.config/hypr/hyprland.lua`; Omarchy's bootstrap loads generated
  theme state from `~/.local/state/omarchy/current/theme/hyprland.lua`. That file
  sets borders and terminal opacity, not a cursor theme. The loaded default
  `/usr/share/omarchy/default/hypr/envs.lua` only sets XCURSOR_SIZE and
  HYPRCURSOR_SIZE to 24. Live Hyprland environment has neither theme name; sampled
  Quickshell environments only have size 24. Config/environment defaults would
  not prove the current theme after a runtime setcursor change anyway. A reliable
  restoration source was not found, so no theme change is shipped.
- No separate indicator adds no pixels, subprocess or appearance restoration.
  It does not advertise ownership while the driver is idle; the human explicitly
  accepts that tradeoff. This is the preferred choice, not a temporary fallback.

## Lifecycle and recovery

`scripts/cursor_session.py` retains its separate guardian, process-group
registration gate, cancellation latch, durable session token and exclusive lock.
The historical `cursor.lock` name stays compatible with the previous version's
lock. Version-2 records contain only a version and token, no appearance setting.
Startup installs best-effort physical Escape cancellation, then releases the
registered driver. No capture, quiescence gate or guessed startup delay remains.
The unchanged action preflight still checks focus, layout, global image changes
and a 49x49 region around pointer targets.

Success, driver error, refusal, finish, Escape and signals stop the driver group,
drain in-flight input, then remove the temporary Escape binding. Cleanup retries
three times. A failed cleanup retains the record; the wrapper provides fallback
recovery and `computer-use recover` can retry later. SIGKILL of the wrapper is
handled by the guardian's pipe EOF; SIGKILL of the guardian is handled by the
wrapper. Tests include a SIGTERM-ignoring descendant and interrupted startup gate.
There is one less desktop setting to restore: no cursor/screen mutation occurs.

An older appearance snapshot is preserved and rejected before the driver starts;
recover it using the previous implementation before upgrading. Never replace it
with a guessed default. Simultaneous death of wrapper and guardian, system failure,
or an unavailable compositor can still leave the temporary Escape binding behind.
Recover when the compositor is available. Those events cannot leave a new
magnification/theme/overlay behind because this version creates none.

## Evidence

The earlier removal report is historical local evidence, not part of this
publication. Earlier startup settlement results are withdrawn as guidance for
the current implementation; see the current validation report linked above.
