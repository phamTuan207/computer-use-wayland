# Troubleshooting

- `unknown XKB key name`: use an alias above or a validated keysym; no guessed syntax.
- `non-BMP text...`: use browser fill/a11y setter; do not replace emoji with a different character.

- Exact transient guard refusal (`screen changed`/`screen_changed`, `focus changed`/`focus_changed`, with no `capture_error` or `ime_restore_failed`): the session survives, but a fresh explicit `observe` is required before any further input; `after.image` (when present) is evidence, not that observe. For animation use a smaller target crop or semantic backend.
- `expected window geometry changed`: the session ENDED, even when the action itself
  succeeded. A click that opens, closes, or re-tiles any window changes the observed
  window's geometry, so the next guard fails and the driver reports `session_ended`.
  This is expected. Verify the result outside the session (`windows`, file bytes),
  then start a NEW session and observe there. The words `observe again` in that error
  do NOT mean you can continue in the old session.
- `ok: false` with `completed` equal to the number of actions sent and an error naming
  the AFTER-capture (for example `final capture failed: window no longer exists`):
  the INPUT SUCCEEDED and only the verification screenshot failed. Verify the
  application state independently. NEVER replay the input.
- `observation older than 90s`: run `observe` again in the same session; desktop observations expire after 90 seconds. If you cannot act within 90 seconds of observing, observe again immediately before the act; never act on an observation older than 90 seconds.
- Stale browser or a11y snapshot (semantic adapter failure): the session has ended — start a new session and observe there. Snapshots also expire after 90 seconds.
- `pointer missed target...`: input is stopped before button-down; inspect monitor/transform metadata. Do not fall back to guessed deltas.
- A click that reports success with `frame_bytes_changed: false` changed no pixels;
  treat it as a likely miss. Measure small or edge controls from a full-resolution
  window observation or a crop, never from a downscaled screen image (default
  `--max-width` 960: a 1920 px monitor becomes a 960 px image, so a 5-image-pixel
  error is a 10-monitor-pixel miss). Prefer keyboard navigation (Down/Enter) for menus.
- In a GTK/xdg-desktop-portal Save dialog, Ctrl+L selects the filename instead of
  opening a location bar, and the file-type filter appends its extension
  (`name.txt` under `Markdown files` saves as `name.txt.md`). Switch the filter to
  `All files` BEFORE typing the name.
- `key action needs a non-modifier key`: a `key` action must contain at least one
  non-modifier key; a lone Super/Ctrl/Alt/Shift press is refused. To open the app
  launcher, use the machine's actual launcher chord (on this machine Super+Space
  for the Omarchy menu); never assume bare Super opens anything.
- A command the repo lists is missing from `computer-use --help` (for example
  `code-exec`): the installed CLI is stale. The repo is authoritative; re-run
  `python3 scripts/sync-installed.py` and `--check`. There is no `verify` command:
  `verify` appears only as a field in the `a11y ground` result.
- CDP tab missing: `browser tabs`, then select exact target; do not silently use the first tab.
- `element covered` / stale snapshot: inspect a fresh observation; close only the overlay the user authorized handling.
- Native rebuild: `python3 ~/.local/share/agent-computer-use/scripts/build.py` (needs cc, wayland-scanner, libwayland; bundled protocol license preserved).

IME control follows the [official fcitx5 interface](https://fcitx-im.org/wiki/DBus_Interface): query state, deactivate with `-c`, restore with `-o`; no clipboard replacement or persistent config changes. Desktop results remain event-level confirmations; verify drafts before external submission.
