## Automation sessions

Run the whole task driver as `computer-use session -- DRIVER [ARGS...]`, not a
separate session around each action. Its child commands inherit session ownership.
Input commands require a live session; standalone capture remains available.
Sessions show a click-through layer-shell badge "Computer use active"; the badge takes
no keyboard focus and lets clicks through. The badge surface asks the compositor for a
per-surface backdrop blur (`ext_background-effect-v1`), applied only inside the rounded
pill. The actual cursor stays normal: no marker is drawn and no cursor theme or screen
scale changes. Window and screen captures both hide the badge for the shot and restore
it after; hiding clears the blur region together with the pixels, so no blurred copy
survives in the capture. Outputs are taken once at startup: adding or removing a
monitor mid-session ends the indicator.
`finish` requests completion; `cancel` latches cancellation. Best-effort physical
Escape works throughout the session, without a timer; installation failures warn.
The wrapper waits for input to stop and the temporary binding to be removed.
A refusal or tool error ends the session. Use `recover` for retained records
after cleanup failure. Recover older magnifier records with the previous version
before upgrading; the new version preserves and rejects them.
Browser adapter timeout is capped at 60 seconds; split larger batches.

# Commands and schemas

All commands emit bounded JSON. `--actions -` accepts JSON from stdin. Prefer a JSON file for complex input; never interpolate user text into shell code.

## Chromium

```bash
CU=computer-use
"$CU" browser start
"$CU" browser tabs
"$CU" browser observe --target EXACT_TAB_ID
"$CU" browser act --target EXACT_TAB_ID --snapshot ID_FROM_OBSERVE --actions /tmp/actions.json
```

`start` reuses a loopback CDP endpoint if available; otherwise opens Chromium with a dedicated persistent profile at `~/.local/share/agent-computer-use/browser-profile`. No `--no-sandbox` or wildcard remote origin. This profile has its own logins. Do not assume it is the user's other browser session. `--endpoint http://127.0.0.1:PORT` selects another locally exposed CDP endpoint.

`observe` returns up to 80 interactive elements with short names and refs, password values redacted. Long page contents and base64 screenshots are not printed. Add `--image` when needed; an image file path is returned. DOM operation is top-document only, excludes canvas internals and does not enumerate shadow roots.

Browser actions:

```json
[
 {"type":"fill","ref":"e1","text":"Tiếng Việt 🐱"},
 {"type":"click","ref":"e2"},
 {"type":"assert","selector":"#status","text":"Saved","timeout_ms":1000}
]
```

`click`, `fill`, `assert`: use a ref or an exact single-match CSS `selector`. `fill` uses trusted input and verifies the resulting value. `assert` accepts `text` (substring), `value` (exact), `checked` (boolean), or defaults to nonzero element width; timeout max 3000 ms. `key`: `keys` array (`Ctrl`, `Alt`, `Shift`, `Meta`, `Enter`, `Tab`, `Escape`, arrows, editing keys, one character). `scroll`: `dy`, optional `dx`,`x`,`y` in viewport CSS pixels. `wait`: `ms` max 2000. Navigation ends the old snapshot; observe the new page before further input. Result includes a fresh `after` snapshot.

## Native accessibility

```bash
"$CU" a11y apps
"$CU" a11y observe --pid EXACT_APP_PID
"$CU" a11y act --snapshot /path/returned.json --actions /tmp/actions.json
```

Actions: `{"type":"click","ref":"e2"}` or `{"type":"set_text","ref":"e1","text":"Tiếng Việt 🐱"}`. Setter verifies full text but does not log field contents. A native button must expose `click`, `press` or `toggle`; an entry's `activate` is never substituted for a click. Snapshot is bounded to 80 actionable elements, 500 visited nodes, depth 12 and roughly 2 seconds plus outstanding DBus calls. If app absent / tree empty / unsupported, use desktop. Do not change accessibility settings without task-specific need. A11y tree paths are rechecked by name and role; identical replacement widgets cannot be distinguished solely by that check.

## Desktop

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
- `wait`: `ms` 0..2000. Adjacent key/type/wait actions are combined with a 12 ms settling gap; Tab/Enter/Escape, delay reset and IME-mode changes split groups to preserve the correct input context. A keyboard group may last at most 5 seconds.

Max 32 actions per batch. Stop at layout-changing or consequential steps. Desktop `completed` counts completed actions/groups, not confirmed application outcomes. User interaction during a keyboard group cannot be intercepted per keystroke. This is foreground automation, not an isolated desktop.

## Troubleshooting

- `unknown XKB key name`: use an alias above or a validated keysym; no guessed syntax.
- `non-BMP text...`: use browser fill/a11y setter; do not replace emoji with a different character.
- `screen changed...`: inspect the returned `after.image` and reuse `after.observation` only after inspecting; for animation use a smaller target crop or semantic backend.
- `pointer missed target...`: input is stopped before button-down; inspect monitor/transform metadata. Do not fall back to guessed deltas.
- CDP tab missing: `browser tabs`, then select exact target; do not silently use the first tab.
- `element covered` / stale snapshot: inspect a fresh observation; close only the overlay the user authorized handling.
- Native rebuild: `python3 ~/.local/share/agent-computer-use/scripts/build.py` (needs cc, wayland-scanner, libwayland; bundled protocol license preserved).

IME control follows the [official fcitx5 interface](https://fcitx-im.org/wiki/DBus_Interface): query state, deactivate with `-c`, restore with `-o`; no clipboard replacement or persistent config changes. Desktop results remain event-level confirmations; verify drafts before external submission.
