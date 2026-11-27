---
name: "cli-anything-discord"
description: "Read and send Discord messages by driving the real Discord desktop client over CDP. Status, servers, channels, messages, session. Every command supports --json."
---

# cli-anything-discord

Message read/send control for the Discord desktop client, built with the
[CLI-Anything](https://github.com/HKUDS/CLI-Anything) 7-phase pipeline
(Apache-2.0). The CLI drives the REAL official client over Chrome DevTools
Protocol on `127.0.0.1:9229` (Node 26 WebSocket transport,
`utils/cdp_client.mjs`). No user token, no self-bot REST calls, no
reimplementation of Discord. Tested live 2026-11-24: 22/22 pytest pass
(see `tests/TEST.md`).

## Machine-private vs portable (read first)

This CLI was built for ONE machine: the owner's Omarchy laptop. Most of it
is machine-private setup, not a generic tool:

- Machine-private (only works on the owner's laptop as built): Discord
  binary at `~/.local/opt/Discord/discord`, CDP port 9229, the
  GUI launch env (`DISPLAY=:0` XWayland, `XDG_RUNTIME_DIR=/run/user/1000`,
  `HYPRLAND_INSTANCE_SIGNATURE`), install via `uv tool install --editable`,
  the test DM with Violet Joestar (channel 865272264831139840). If you run
  this elsewhere, every one of those must be re-pointed (they live in
  `utils/discord_backend.py`: `DISCORD_BIN`, `CDP_PORT`, `_gui_env()`).
- Portable (works for any Electron app, and is the part worth reusing):
  the pattern itself. Launch any Electron/Chromium app with
  `--remote-debugging-port=<port>`, resolve the page target at runtime via
  `GET /json/list` (never hardcode a target id), drive it with
  `Runtime.evaluate` / `Input.insertText` / `Input.dispatchKeyEvent` /
  `DOM.setFileInputFiles`. The CDP client (`utils/cdp_client.mjs`) is
  app-agnostic: `targets`, `version`, `eval`, `navigate`, `send`,
  `sendfile` work against any Chromium target. The selector discipline
  also ports: prefer roles, aria-labels and stable `id`/`data-*` hooks;
  hashed class suffixes are fallbacks only and drift per build.

## Optional / opt-in (default: OFF)

CDP control is OPTIONAL and OFF by default. A normally launched Discord
has no CDP endpoint at all, and this CLI does nothing to it: it does not
relaunch Discord on its own, does not inject anything, and does not change
any setting. Enabling it is an explicit opt-in:

- Opt in with `cli-anything-discord session start` (launches Discord
  detached with `--remote-debugging-port=9229`), or launch Discord
  yourself with that flag.
- Opt out any time: quit Discord normally, or `session stop --force`.
  After a normal quit, Discord is back to stock; the CLI is inert.
- When CDP is off, the CLI fails LOUDLY with the fix, it never fails
  silently and never touches anything else. Verified live with Discord
  down: `session attach` -> "Discord CDP is not reachable on port 9229.
  Run `session start` to launch Discord with --remote-debugging-port=9229."
  and `messages read` -> the same, naming `session start` and the flag.
  `status` is the read-only probe: it returns `discord_running: false`
  with `ok: true` so agents can check before acting.

## Install (owner's laptop)

- Hard dependencies: official Discord desktop client (logged in, same
  machine), Node.js >= 22 (global `WebSocket`, no npm deps), Python >=
  3.10 with `click` and `prompt-toolkit`.
- `uv tool install --editable <path-to-discord-cli>` (laptop has no system
  pip). Entry point: `cli-anything-discord`.
- `cli-anything-discord session start` launches Discord with CDP on port
  9229 if it is not already running. Never run `session stop` without
  `--force`. Cold launch after a full quit can take up to ~60s to answer
  CDP (Discord self-updated 1.0.169 -> 1.0.170 during the 2026-11-24 test
  run; the updater once relaunched the client without the debug flag, so
  `session start` waits for a real CDP answer and fails loudly if none
  comes).

## ToS risk (must tell the user)

Automating a normal Discord user account is forbidden by Discord's
Community Guidelines (rule 14, self-bots) and Discord's support article
says it "can result in an account termination if found". The CDP route
(driving the official client) is not named in the terms, but is probably
treated as self-botting if detected. Do not present it as safe. The only
sanctioned automation is a bot token, which cannot read owner DMs. This CLI
never uses, asks for, or stores a user token. Full research (sources,
dates, per-route assessment): `discord-tos-research.md`, read 2026-11-24.
Keep volume low and human-paced, never send bulk or unsolicited messages,
and prefer a secondary account you can afford to lose for anything beyond
personal test traffic.

## Commands

All commands accept a global `--json` flag for machine-readable output.
The flag is a group option: it goes BEFORE the subcommand
(`--json messages read ...`). A bare channel id is a DM channel id.
`channels open <id>` sets the current channel; later `messages` commands
can omit the id. Session state lives in
`~/.cli-anything-discord/session.json`.

```
cli-anything-discord status
cli-anything-discord servers list
cli-anything-discord channels list [--dm | --guild]
cli-anything-discord channels open <channelId>
cli-anything-discord messages read [channelId] [--limit N]
cli-anything-discord messages send [channelId] --text "..."
cli-anything-discord messages send-file [channelId] --file <path> [--text "..."]
cli-anything-discord session start | attach | show | stop --force
cli-anything-discord            # REPL (default with no args)
```

### Real examples (verified live 2026-11-24)

```bash
cli-anything-discord --json status
# {"discord_running": true, "cdp_port": 9229, "target_id": "...",
#  "target_url": "https://discord.com/channels/@me/865272264831139840", "ok": true, ...}

cli-anything-discord --json servers list
# {"count": 13, "servers": [{"id": "...", "name": "..."}, ...], "ok": true}

cli-anything-discord --json channels list --dm
# {"dms": [{"href": "/channels/@me/865272264831139840", "name": "..."}, ...],
#  "dm_count": 8, "ok": true}

cli-anything-discord --json messages read 865272264831139840 --limit 5
# {"channel_id": "865272264831139840", "count": 5, "total_visible": 5,
#  "messages": [{"id": "1574784744309268551", "author": "...",
#  "timestamp": "2026-11-24T13:51:...", "content": "...",
#  "attachments": ["https://cdn.discordapp.com/attachments/865272264831139840/..."]}], "ok": true}

cli-anything-discord --json messages send 865272264831139840 --text "hello"
# {"ok": true, "sent": "hello", "composer_label": "Nhắn @Violet Joestar", ...}

cli-anything-discord --json messages send-file 865272264831139840 --file ./note.txt --text "caption"
# {"ok": true, "file": "./note.txt", "caption": "caption", ...}
```

## Usage notes for agents

- Always run `status` first to confirm Discord + CDP are up before reading
  or sending. If CDP is off, `status` says `discord_running: false`; run
  `session start` (the opt-in) and re-check.
- Test traffic goes ONLY to the owner-designated test DM unless the owner
  explicitly names another channel. Never send to a public server or
  another DM unasked.
- `messages read` returns only the viewport window of messages (scroll
  loads a bounded amount of older history). `count` vs `total_visible`
  shows whether the result was truncated by `--limit`. A read always
  ends scrolled to the bottom, so the newest messages are what you get.
- Sending is irreversible; there is no undo and no delete command.
- If a command fails with "composer not found", "file input not found" or
  "No messages found", the channel view was probably still loading or the
  Discord DOM changed; the CLI waits up to 15s for the element before
  failing. Report the exact error, do not retry blindly.
- Page target is resolved at runtime via `/json/list` (never hardcoded).
- Presence stays out of this CLI; the existing `discord-window-presence`
  service keeps owning Rich Presence.
- No Vision, no mouse: every operation is CDP. Never add a Vision/mouse
  step unless CDP provably cannot do it, and document it in README.md
  first (where, why no CDP alternative). Owner rule, 2026-11-24.
- Pipeline attribution: built with HKUDS/CLI-Anything (Apache-2.0).
