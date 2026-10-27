# Troubleshooting

- `unknown XKB key name`: use an alias above or a validated keysym; no guessed syntax.
- `non-BMP text...`: use browser fill/a11y setter; do not replace emoji with a different character.

- Exact transient guard refusal (`screen changed`/`screen_changed`, `focus changed`/`focus_changed`, with no `capture_error` or `ime_restore_failed`): the session survives, but a fresh explicit `observe` is required before any further input; `after.image` (when present) is evidence, not that observe. For animation use a smaller target crop or semantic backend.
- `observation older than 90s`: run `observe` again in the same session; desktop observations expire after 90 seconds.
- Stale browser or a11y snapshot (semantic adapter failure): the session has ended — start a new session and observe there. Snapshots also expire after 90 seconds.
- `pointer missed target...`: input is stopped before button-down; inspect monitor/transform metadata. Do not fall back to guessed deltas.
- CDP tab missing: `browser tabs`, then select exact target; do not silently use the first tab.
- `element covered` / stale snapshot: inspect a fresh observation; close only the overlay the user authorized handling.
- Native rebuild: `python3 ~/.local/share/agent-computer-use/scripts/build.py` (needs cc, wayland-scanner, libwayland; bundled protocol license preserved).

IME control follows the [official fcitx5 interface](https://fcitx-im.org/wiki/DBus_Interface): query state, deactivate with `-c`, restore with `-o`; no clipboard replacement or persistent config changes. Desktop results remain event-level confirmations; verify drafts before external submission.
