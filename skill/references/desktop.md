# Desktop

Desktop `act --no-after` skips the successful final screenshot while keeping the
fresh pre-input capture and all focus, geometry and cancellation guards. Use it
only when an independent application result check will confirm the outcome and
no next screenshot is needed. `ok`/`after_skipped` alone are not that check.
Execution failures still attempt a diagnostic `after`; never replay uncertain
input. This differs from browser `--no-after`, which requires a final assert.

For a known application class, `windows --class CLASS` returns only exact,
case-sensitive matches; no match returns `[]`. Add `--no-titles` to omit the title
field. Both options are independent, read-only and apply to one request. Every
matching address remains in the result; verify the target before input.

`doctor`: dependencies and monitor names. `windows`: exact address, title, bounds, workspace. `observe --window ADDRESS [--crop X Y W H]` captures visible screen pixels without changing focus or workspace; hidden windows and inactive workspaces are refused. Add `--focus` to explicitly activate the window before capture (may switch workspace); this flag requires `--window`. A window on an inactive workspace is refused without it. When `act` will focus the window anyway, run `observe --window ADDRESS --focus` first: a plain observe leaves focus unchanged, so the later act focus can restack windows and change the view you captured. Overlapping windows can cover the capture. `observe --screen MONITOR [--crop X Y W H]` captures the whole monitor or a monitor-relative region, including layer-shell and popups; use pointer actions only with this scope. Both accept `--max-width 320..3840` and return image + observation paths; full metadata stays in the JSON file. Add `--verbose` to print it. Captures use `grim -s 1` without cursor; a live session's badge is hidden for the capture and restored after, for both window and screen scopes; hiding also clears its blur region. Actions recheck monitor geometry and the target region before input. Cache is user-private; files older than 24 hours are pruned on the next capture.

Desktop actions:

```json
[
 {"type":"click","x":210,"y":140,"button":"left"},
 {"type":"click","x":300,"y":180,"modifiers":["Ctrl","Shift"]},
 {"type":"key","keys":["Ctrl","a"]},
 {"type":"type","text":"example","delay_ms":0},
 {"type":"key","keys":["Shift","ArrowRight"],"repeat":3},
 {"type":"key","keys":["F1"],"hold_ms":70}
]
```

- `move`, `click`, `double_click`: image `x`,`y`; click button left/right/middle. `click`, `double_click`, `drag` and `scroll` accept `modifiers`, an array of up to 5 names from `Ctrl`, `Shift`, `Alt`, `Super`, `AltGr` (aliases `Control`, `Meta`, `Win`, `Logo`); the modifiers are held for that one action and released after. `move` rejects `modifiers`.
- `drag`: image `from:[x,y]`, `to:[x,y]`, `button` left/right/middle (default left), duration `ms` 50..2000 (default 300). Held pointer survives the whole drag; release attempted on failure.
- `scroll`: image `x`,`y`, `dx`,`dy` in Wayland axis units; positive dy down. Wheel output includes discrete steps (one per 15 axis units, minimum one for nonzero input) and a 30 ms pointer-enter settling gap. These are not necessarily browser CSS pixels.
- `key`: array of modifiers and XKB/alias key names. Modifier entries are held for the whole action while the non-modifier keys are pressed and released one at a time in array order, so `["Ctrl","a"]` is the Ctrl+a chord but `["a","b"]` types `a` then `b`, not held together. `repeat` 1..30, `hold_ms` 0..2000 (default 12); modifiers released in the same process. Shift+Tab maps to `ISO_Left_Tab` with Shift; editing-key-only groups also bypass composition temporarily. A one-character key is a keysym, not a physical US scancode. Prefer lowercase letters with Shift explicitly for shortcuts.
- `type`: exact text by default (`ime:"literal"`), temporarily disables and restores fcitx5 composition. Use `ime:"compose"` for intentional Telex input. `delay_ms` 0..100 (default 0). Leading-dash text uses a standalone literal invocation. Enter/newlines typed as content may trigger app behavior; choose keys explicitly when needed.
- `wait`: `ms` 0..2000, cancellation-aware timer without keyboard input. Adjacent key/type actions are combined with a 12 ms settling gap; waits, Tab/Enter/Escape, delay reset and IME-mode changes split groups to preserve the correct input context. A keyboard group may last at most 5 seconds.

Max 32 actions per batch. Stop at layout-changing or consequential steps. Desktop `completed` counts completed actions/groups, not confirmed application outcomes.
The result reports `frame_bytes_changed` — the final capture's pixel hash differs from the input
observation's, so animations also count — and keeps `changed` as a compatibility alias with the
same value; neither proves the application applied the action, so verify application state
separately. `input_diagnostics` records the pre-batch focus state (`focus_before`,
`target_was_focused`) and reports pointer verification as cursor position only: the desktop
backend cannot identify the UI element receiving the event, so use DOM/accessibility targeting
when element identity is needed. A pre-input guard refuses with `focus changed` when
the target window is not the active window at execution time. User interaction during a keyboard group cannot be intercepted per keystroke. This is foreground automation, not an isolated desktop.

Desktop `type` is not a guarantee of exact field contents: an installed Chromium
fixture lost BMP characters when a synthetic key occupied physical Backspace.
Adding typing delay did not fix it. Prefer browser `fill` or a verified accessibility
setter, then assert the exact application value. Desktop focus guards also cannot
prevent input reaching another window during one running wtype group. Use an
isolated target; a refusal can follow partial input and must not trigger replay.
See [installed diagnostics](../../docs/optimization-experiments.md#installed-keyboard-diagnostics).
