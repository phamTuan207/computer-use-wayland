# Troubleshooting

- `unknown XKB key name`: use an alias above or a validated keysym; no guessed syntax.
- `non-BMP text...`: use browser fill/a11y setter; do not replace emoji with a different character.

- Exact transient guard refusal (`screen changed`/`screen_changed`, `focus changed`/`focus_changed`, with no `capture_error` or `ime_restore_failed`): the session survives, but a fresh explicit `observe` is required before any further input; `after.image` (when present) is evidence, not that observe. For animation use a smaller target crop or semantic backend.
- `observation older than 120s`: run `observe` again in the same session; desktop observations expire after 120 seconds.
- Stale browser or a11y snapshot (semantic adapter failure): the session has ended — start a new session and observe there. Snapshots also expire after 120 seconds.
- SSH to the laptop dies after about 30 seconds: run long jobs fully detached (`setsid nohup ... > log 2>&1 < /dev/null & disown`) and check progress with short commands. Never hold an SSH session open waiting for a long job.
- Plain SSH without `-i` and `IdentitiesOnly=yes` fails with Permission denied: always use the provided SSH wrapper script.
- agy CLI cannot run non-interactive over SSH (it needs an interactive login): use fcc-claude for non-interactive agent runs.
- Live-site browsing from the VM's Chromium fails out of the box: run `python3 scripts/vm_proxy.py` (local forward proxy on 127.0.0.1:18080, auth from `VM_EGRESS_PROXY_AUTH` in env only) and launch Chromium with `--proxy-server="http://127.0.0.1:18080" --ignore-certificate-errors`.
- Google sign-in goes through the account chooser only. Never ask the user for a password; a password step means stop that provider.
- When tagged in a group, reply in the group immediately. Never process silently and leave people asking again.
- Image viewer is `imv-wayland`, not `imv`: kill it after every photo with `pkill -x imv-wayland`.
- Hyprland Lua dispatch takes the `hl.dsp` object form only; the string-dispatcher form is broken.
- After a broker code change, restart the relay when idle (sync-installed verifies the loaded code hash). A relay running stale code fails deterministically.
- A bad driver request line (a file path, non-JSON bytes) no longer drops the session: the relay answers an error envelope and stays alive; observe again and continue.
- `pointer missed target...`: input is stopped before button-down; inspect monitor/transform metadata. Do not fall back to guessed deltas.
- CDP tab missing: `browser tabs`, then select exact target; do not silently use the first tab.
- `element covered` / stale snapshot: inspect a fresh observation; close only the overlay the user authorized handling.
- Native rebuild: `python3 ~/.local/share/agent-computer-use/scripts/build.py` (needs cc, wayland-scanner, libwayland; bundled protocol license preserved).

IME control follows the [official fcitx5 interface](https://fcitx-im.org/wiki/DBus_Interface): query state, deactivate with `-c`, restore with `-o`; no clipboard replacement or persistent config changes. Desktop results remain event-level confirmations; verify drafts before external submission.
