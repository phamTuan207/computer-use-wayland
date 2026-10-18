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
A refusal or tool error ends the session. Use `recover` for retained records
after cleanup failure. Recover older magnifier records with the previous version
before upgrading; the new version preserves and rejects them.
Browser adapter timeout is capped at 60 seconds; split larger batches.

`computer-use status` is a read-only local-state command returning
`{"ok":true,"cancelled":true}` when latched (`cancelled: false` otherwise). It reports the cancellation latch, not
whether a session or overlay is active. It never clears cancellation; only
user-requested `computer-use resume` does that.

# Commands and schemas

## Interactive agent driver

Use one initial model view, one batch of all predictable actions, then its final image. See the
required [batch-first policy](../SKILL.md#batch-first-required). Keep machine-side preflight
captures and guards enabled; these checks do not need a model decision.

Start `computer-use session -- computer-use session-driver` with your tool's
persistent interactive process facility (PTY/stdin session or background terminal).
Keep that process handle for the whole task; do not launch a new shell session
for each action and do not redirect stdin to `/dev/null`. The pill remains active
while the driver waits for the next instruction. Send one JSON object per line:

```json
{"args":["observe","--window","0xEXACT_ADDRESS","--focus"]}
{"args":["act","--observation","/returned/path.json","--actions","-"],"stdin":"[{\"type\":\"click\",\"x\":210,\"y\":140}]"}
{"args":["finish"]}
```

Inspect each returned image before choosing coordinates; these lines show the
wire format, not a batch to paste blindly. The relay reuses the installed Python CLI runtime
and returns decoded JSON in `result`, rather than escaped JSON in `stdout`.
Only non-JSON output falls back to `stdout`; empty stderr is omitted. It runs
directly without a shell, preserves session ownership, and exits on CLI error. The driver itself
continues past exactly one case — a desktop `act` returning code 1 with a whitelisted transient
refusal (`screen changed`/`screen_changed`, `focus changed`/`focus_changed`) — so an explicit
observe plus fresh-path retry can follow; every other error ends the relay.
EOF, finish, physical Esc, or a crash lets the guardian remove the overlay.
Do not automatically resume or repeat input after cancellation/failure.

Browser commands in this relay lazily start one private Node worker for the task.
It reuses the runtime, not a cached snapshot: one slot is reused only for a
fresh, validated same target; standalone CLI commands keep their isolated
behavior. Finish/EOF/error/cancellation closes the child; failures never
restart it or replay input. Each complete request/response is limited to
32 MiB. The cold first request is not faster. Cancellation latches and stops
new input; it does not instantly intercept a live input group already
dispatched.

If your tool cannot keep stdin/process state between calls, run a complete task
driver inside one session instead. Do not simulate persistence with detached
sessions or manually copied session tokens.

All commands emit bounded JSON. `--actions -` accepts JSON from stdin. Prefer a JSON file for complex input; never interpolate user text into shell code.

If the caller exposes `yield_time_ms`, use a short output wait (about 250–1000 ms for short
requests, allowing for a longer drag/wait batch). A persistent driver remains alive after it
returns a response: waiting 10000 ms for it to exit adds avoidable caller latency. Consume one
response before sending the next request; wait again only while that response is pending.

### Ground once, execute, verify

- Use DOM/accessibility refs where supported. For screenshots, choose the center of a visible
  control, not its edge, and keep coordinates in the returned image's space. The executor applies
  crop offsets, resize factors and monitor origins.
- If small controls would be lost at 1280 px, choose a reliable crop or `--max-width 3840` on the
  initial observation to preserve available detail; this never creates detail absent at capture.
  With an image-viewing tool that supports it, request original detail. Avoid a second image just
  to recheck a clear large target.
- Example: in a visible Pinta canvas, plan ellipse-tool click → visible color click → Shift-drag
  a square bounding box → hand-tool click to commit. Submit one action array and inspect only
  its final result when every target is already visible and stays fixed. Setting an absolute
  visible width value is preferable to guessing how many plus clicks a previous value needs.
- An unseen fill-style popup is a real observation boundary. A selected-tool highlight is not.
  Keep the final result screenshot by default. Never use a fixed two-image ceiling to ignore
  uncertainty, errors, navigation or changed geometry.

Evidence and limits: [batching and grounding research](../../docs/research/2026-10-19-batching-grounding.md).

## Chromium

```bash
CU=computer-use
"$CU" browser start
"$CU" browser tabs
"$CU" browser observe --target EXACT_TAB_ID
"$CU" browser act --target EXACT_TAB_ID --snapshot ID_FROM_OBSERVE --actions /tmp/actions.json
```

`start` reuses a loopback CDP endpoint if available; otherwise opens Chromium with a dedicated persistent profile at `~/.local/share/agent-computer-use/browser-profile`. No `--no-sandbox` or wildcard remote origin. This profile has its own logins. Do not assume it is the user's other browser session. `--endpoint http://127.0.0.1:PORT` selects another locally exposed CDP endpoint.

`observe` returns up to 80 interactive elements with short names and refs, visible controls first. All form values and editable contents are redacted; checked state remains available. Screenshots and page labels may still contain private data. Use `--max-elements 16` on observe/act when a smaller output is sufficient (range 1..80, default 80); increase it if the target is absent, never guess a ref. Long page contents and base64 screenshots are not printed. Add `--image` when needed; an image file path is returned. DOM operation is top-document only, excludes canvas internals and does not enumerate shadow roots.

Browser actions:

```json
[
 {"type":"fill","ref":"e1","text":"Tiếng Việt 🐱"},
 {"type":"click","ref":"e2"},
 {"type":"assert","selector":"#status","text":"Saved","timeout_ms":1000}
]
```

`click`, `fill`, `assert`: use a ref or an exact single-match CSS `selector`. `fill` uses trusted input and verifies the resulting value. `assert` accepts `text` (substring), `value` (exact), `checked` (boolean), or defaults to nonzero element width; timeout max 3000 ms. `key`: `keys` array (`Ctrl`, `Alt`, `Shift`, `Meta`, `Enter`, `Tab`, `Escape`, arrows, editing keys, one character). `scroll`: `dy`, optional `dx`,`x`,`y` in viewport CSS pixels. `wait`: `ms` max 2000. Navigation ends the old snapshot; observe the new page before further input. Result includes a fresh `after` snapshot.

`set_value` also takes one `ref` or exact `selector` plus `text`. Prefer it for
ordinary text inputs and textareas: it avoids focus-dependent typing, uses the
native value setter and verifies the value, but dispatches synthetic, untrusted
`input`/`change` events. Follow it with an assertion on the app's result. Use
`fill` when trusted keyboard events are required and the target is controlled.
See [field routing evidence](../../docs/optimization-experiments.md#browser-field-assignment-with-routing-faults).

Snapshots list interactive controls, not arbitrary status messages. A successful
`act` and its `after` alone do not prove that Save succeeded. Use a known app-result
assert; if the result is not yet understood, request `--image` and inspect it.
Do not invent a status selector or expected message to avoid that check.

When the next targets and success condition are known, keep `fill`, `click` and
the result `assert` in one `act`, as above. A fixed `wait` cannot establish that
the application finished. Use an exact `value` assertion for field contents and
a specific result condition for an action; the default width assertion only
checks element presence. Split at unknown layout changes or navigation, and stop
after failure without replaying input. This recipe reduces request roundtrips;
it does not change the input backend or prove model-token savings. Reproduction
and limitations: [task experiments](../../docs/optimization-experiments.md).

### Scope the observation: `browser observe --scope`

Opt-in, one read, never sticky:

```bash
"$CU" browser observe --target EXACT_TAB_ID --scope '#task'
```

`--scope` is valid on `observe` only. The value is a CSS selector that must match
exactly one top-document element; it must be non-empty and at most 1024 UTF-16
units. The selector is resolved read-only before the snapshot is replaced, so a
failed match leaves the previous snapshot id and refs usable — there is no
fallback to the whole page.

The result enumerates only the interactive descendants of that root, plus the root
itself when it is interactive. Iframes inside the scope are counted but not
traversed. `scoped: true` in the result marks it; `title` and `url` remain whole
page metadata. `--image` still captures the full viewport.

Scope is **not** an input, security or privacy boundary: existing selectors can
address anything on the page, and every action guard is unchanged. This is worth
using when the page carries many irrelevant controls, because the observation is
what you have to read.

### Scope the successful after-snapshot

When the next browser step is still in one panel, ask `act` for its new refs there:

```bash
"$CU" browser act --target EXACT_TAB_ID --snapshot ID_FROM_OBSERVE \
  --actions /tmp/actions.json --after-scope '#task'
```

This scopes only a **successful** `act` after-snapshot. A failed action keeps a
whole-page diagnostic. If the panel is gone or no longer unique after the action,
the result says `after_unavailable`; observe again before further input. The
default `act` still returns the whole page. `--after-scope` cannot combine with
`--no-after`; use `--no-after` when a final assert already proves completion and
no next refs are needed. `--image` still captures the full viewport.

### Skip the final snapshot: `browser act --no-after`

Opt-in. The same recipe, with the result `assert` last:

```bash
"$CU" browser act --target EXACT_TAB_ID --snapshot ID_FROM_OBSERVE \
  --actions /tmp/actions.json --no-after
```

On a successful `act` the result carries `after_skipped: true` and no `after`
snapshot, so the response is much smaller. An execution failure still attempts a
diagnostic `after` snapshot (or sets `after_unavailable`) and never sets
`after_skipped`; preflight failures happen before input. Omitting the flag keeps
today's behaviour.

Because that assert is now the only evidence of success, the last action must
be an `assert` with a condition it really evaluates. `assert` resolves one
predicate in `value` > `text` > `checked` order and ignores the rest, so:

- `value`: a string; `""` is allowed and means "the field is empty".
- `text`: a non-empty string. An empty `text` proves nothing.
- `checked`: a boolean.
- none of these — the default nonzero-width check — is refused.

`--no-after` is rejected on `observe`, `tabs` and `start`, cannot be combined
with `--image`, and is refused before any network or input effect if the final
action is `wait`, `click` or `fill`, or if `actions` is empty.

There is no automatic observation, retry or replay. If the layout or the page
changes after the assert, the previous snapshot is spent: run `observe` again
before any further input. Split at unknown layout changes and navigation as
usual. This reduces response size; it is not a claim about billed model tokens.

## Native accessibility

```bash
"$CU" a11y apps
"$CU" a11y observe --pid EXACT_APP_PID --skeleton
"$CU" a11y drill REF_FROM_SKELETON --snapshot SNAPSHOT_FROM_SKELETON
"$CU" a11y act --snapshot /path/returned.json --actions /tmp/actions.json
```

Actions: `{"type":"click","ref":"e2"}` or `{"type":"set_text","ref":"e1","text":"Tiếng Việt 🐱"}`. Setter verifies full text but does not log field contents. A native button must expose `click`, `press` or `toggle`; an entry's `activate` is never substituted for a click. Snapshot is bounded to 80 actionable elements, 500 visited nodes, depth 12 and roughly 2 seconds plus outstanding DBus calls. If app absent / tree empty / unsupported, use desktop. Do not change accessibility settings without task-specific need. A11y tree paths are rechecked by name and role; identical replacement widgets cannot be distinguished solely by that check.

For native app UI, prefer skeleton → drill → act → re-drill before requesting
screenshots when refs suffice. Skeleton includes containers, their `children_count`
and `path`, and stops at depth three relative to its root. A truncated container's
`ref` can be drilled with its matching snapshot; drill returns a new snapshot and
new refs. Both modes retain the 80-element/500-node/time budgets and absolute path
depth 12. Disabled or changed refs are refused; snapshots expire after 90 seconds.
Keep each ref with the snapshot that issued it. After an action, verify the app
result; re-drill a still-valid container or obtain a fresh skeleton after a tree
change. Ordinary `a11y observe --pid PID` keeps its existing actionable-only output.

The a11y JSON was already bounded, so skeleton saves little within that backend.
Its possible benefit is skipping PNG-based rounds. Latency and output savings
depend on the actual app and are UNVERIFIED until measured; no percentage of model-token savings has been established.

## Desktop

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

Begin with a bounded crop when the app window, semantics or geometry determine
one: the crop must contain both the target and enough context to identify it,
and the returned image must be inspected before choosing input coordinates.
Expand or re-observe when the target or context is absent. A full view is the
explicit fallback only when no reliable crop can be determined; never guess
action coordinates and never crop past an unseen menu or popup change.
Crop coordinates are logical pixels relative to the selected window or monitor; action coordinates come from the returned image. Use a fresh view
for an unknown menu/popup or after geometry, focus or screen changes.

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

Max 32 actions per batch. Stop at layout-changing or consequential steps. Desktop `completed` counts completed actions/groups, not confirmed application outcomes. User interaction during a keyboard group cannot be intercepted per keystroke. This is foreground automation, not an isolated desktop.

Desktop `type` is not a guarantee of exact field contents: an installed Chromium
fixture lost BMP characters when a synthetic key occupied physical Backspace.
Adding typing delay did not fix it. Prefer browser `fill` or a verified accessibility
setter, then assert the exact application value. Desktop focus guards also cannot
prevent input reaching another window during one running wtype group. Use an
isolated target; a refusal can follow partial input and must not trigger replay.
See [installed diagnostics](../../docs/optimization-experiments.md#installed-keyboard-diagnostics).

## Troubleshooting

- `unknown XKB key name`: use an alias above or a validated keysym; no guessed syntax.
- `non-BMP text...`: use browser fill/a11y setter; do not replace emoji with a different character.

- `screen changed` / `screen_changed` or `focus changed` / `focus_changed`: inspect any returned `after.image`, then run an explicit desktop `observe` and use its fresh path for the next desktop `act`. The automatic `after.observation` does not satisfy this requirement. Other input backends are blocked until that explicit observation too. Capture, cleanup or IME restoration errors end the session even alongside a transient refusal.
- `pointer missed target...`: input is stopped before button-down; inspect monitor/transform metadata. Do not fall back to guessed deltas.
- CDP tab missing: `browser tabs`, then select exact target; do not silently use the first tab.
- `element covered` / stale snapshot: inspect a fresh observation; close only the overlay the user authorized handling.
- Native rebuild: `python3 ~/.local/share/agent-computer-use/scripts/build.py` (needs cc, wayland-scanner, libwayland; bundled protocol license preserved).
- Glass backend build refuses a dirty source tree by default (tracked or untracked, regardless of git untracked-visibility config); pass `--allow-dirty` to build intentionally. Dirt from the build's own patch in the same run is permitted, but rerunning over an already-patched dirty tree still needs the flag. The build stamps `commit`/`initial_dirty`/`allow_dirty` before patching and `build_dirty` after.

IME control follows the [official fcitx5 interface](https://fcitx-im.org/wiki/DBus_Interface): query state, deactivate with `-c`, restore with `-o`; no clipboard replacement or persistent config changes. Desktop results remain event-level confirmations; verify drafts before external submission.
