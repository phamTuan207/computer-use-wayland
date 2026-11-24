# cli-anything-discord

Message read/send control for the Discord desktop client, built with the
[CLI-Anything](https://github.com/HKUDS/CLI-Anything) 7-phase pipeline
(Apache-2.0). Attribution: the pipeline, HARNESS.md, `repl_skin.py` and the
session-locking pattern come from HKUDS/CLI-Anything.

## What it does

Drives the REAL Discord desktop client (Electron 1.0.169) over Chrome
DevTools Protocol on `127.0.0.1:9229`. No reimplementation, no user token,
no self-bot REST calls. The CLI navigates the client, scrapes the message
DOM, and types into the real composer.

Commands (every command supports `--json`):

```
cli-anything-discord status
cli-anything-discord servers list
cli-anything-discord channels list [--dm | --guild]
cli-anything-discord channels open <channelId>
cli-anything-discord messages read [channelId] [--limit N]
cli-anything-discord messages send [channelId] --text "..."
cli-anything-discord messages send-file [channelId] --file <path> [--text "..."]
cli-anything-discord session start | attach | show | stop --force
cli-anything-discord            # no args: interactive REPL
```

A bare channel id is treated as a DM channel id. `channels open` sets the
current channel in the session file (`~/.cli-anything-discord/session.json`),
so later `messages read/send` can omit the id.

## Machine-private vs portable

This CLI was built for ONE machine (the owner's Omarchy laptop) and is
machine-private setup, not a generic tool. The owner-design principle
(2026-11-24): apps on his machine are deliberately optimized for AI, but
a repo for outsiders must work on stock, unoptimized apps, so any
machine-private optimization that goes into a shared repo must be
OPTIONAL (opt-in), default off.

- Machine-private (only works on the owner's laptop as built): Discord
  binary at `/home/james/.local/opt/Discord/discord`, CDP port 9229, the
  GUI launch env (`DISPLAY=:0` XWayland, `XDG_RUNTIME_DIR=/run/user/1000`,
  `HYPRLAND_INSTANCE_SIGNATURE`), install via `uv tool install
  --editable`, the test DM with Violet Joestar (channel
  865272264831139840). All of these live in `utils/discord_backend.py`
  (`DISCORD_BIN`, `CDP_PORT`, `_gui_env()`, `TEST_DM_CHANNEL_ID`) and must
  be re-pointed to run anywhere else.
- Portable (worth reusing anywhere): the pattern. Launch any
  Electron/Chromium app with `--remote-debugging-port=<port>`, resolve the
  page target at runtime via `GET /json/list` (never hardcode a target
  id), drive it with `Runtime.evaluate` / `Input.insertText` /
  `Input.dispatchKeyEvent` / `DOM.setFileInputFiles`. The CDP client
  (`utils/cdp_client.mjs`: `targets`, `version`, `eval`, `navigate`,
  `send`, `sendfile`) is app-agnostic. The selector discipline ports too:
  prefer roles, aria-labels and stable `id`/`data-*` hooks; hashed class
  suffixes are fallbacks only and drift per build.

## Optional / opt-in (default: OFF)

CDP control is OPTIONAL and OFF by default. A normally launched Discord
has no CDP endpoint, and this CLI does nothing to it: it does not relaunch
Discord on its own, does not inject anything, and does not change any
setting. Opt in with `session start` (launches Discord detached with
`--remote-debugging-port=9229`) or by launching Discord yourself with
that flag. Opt out any time by quitting Discord normally or with
`session stop --force`; after a normal quit Discord is back to stock and
the CLI is inert. When CDP is off, the CLI fails LOUDLY with the fix
(`session attach` / `messages read` both name `session start` and the
flag), never silently, and never touches anything else. `status` is the
read-only probe: it returns `discord_running: false` with `ok: true`.

## Hard dependencies

- The official Discord desktop client, logged in, on the same machine.
- Node.js >= 22 (global `WebSocket`, no npm deps) for the CDP transport
  (`utils/cdp_client.mjs`).
- Python >= 3.10, `click`, `prompt-toolkit`.

## Install

```bash
# on the laptop (uv is the available installer; no system pip)
uv tool install --editable /path/to/discord-cli
# or: uv venv ~/.cli-anything-discord-venv && uv pip install --python <venv> -e /path/to/discord-cli
cli-anything-discord status
```

If Discord is not running, `session start` launches it detached with
`--remote-debugging-port=9229` (needs `DISPLAY=:0` XWayland plus the usual
GUI env; the backend handles this).

## ToS risk note (read before use)

This section summarizes research done 2026-11-24 (see
`discord-tos-research.md` in the parent project dir; sources re-checked
there). It is not legal advice. Discord can change its terms at any time.

- Discord's Community Guidelines rule 14: "Do not use self-bots or
  user-bots. Each account must be associated with a human, not a bot."
- Discord's support article on Automated User Accounts says automating
  normal user accounts outside the OAuth2/bot API "is forbidden, and can
  result in an account termination if found".
- The CDP/GUI-automation route is NOT named anywhere in Discord's terms
  (no clause mentions CDP, DevTools, GUI automation or RPA). The honest
  position: probably treated as self-botting if detected, but Discord has
  not published a position on GUI automation specifically. Do NOT present
  this route as safe or compliant.
- The only sanctioned automation path is a proper bot account with a bot
  token, invited to servers. It cannot read the owner's DMs or act as the
  owner, so it does not cover the same use cases.
- The owner approved building this CLI knowing the risk. That approval
  does not change Discord's terms or bind Discord. Keep volume low and
  human-paced, never send bulk or unsolicited messages, never store a
  user token anywhere, and prefer a secondary account you can afford to
  lose for anything beyond personal test traffic.
- This CLI never asks for, reads, or stores a Discord user token or
  password. It only drives the already-logged-in official client on the
  owner's own machine.

## Design notes

- Page target is resolved at runtime via `/json/list` (never hardcoded).
- No Vision, no mouse: this CLI drives Discord purely through CDP
  (HTTP `/json/*` + WebSocket `Runtime.evaluate` / `Input.*` / `DOM.*`).
  Per the owner's standing rule (2026-11-24), Vision/mouse automation is
  used only when no CLI/API/CDP path exists. No step in this CLI uses
  Vision or mouse input, and no such step was added: navigation, reading,
  sending and file upload are all CDP operations. If a future Discord
  change breaks a CDP path and only a Vision/mouse step can replace it,
  that step must be documented here (where, why CDP cannot do it) before
  it is added.
- Selectors prefer stable hooks (roles, aria-labels, `id^="chat-messages-"`);
  hashed class suffixes are fallbacks only and will drift per Discord build.
- Only the viewport window of messages is in the DOM; `messages read`
  scrolls up (bounded, 5 scrolls) to load older messages.
- Sending is irreversible; there is no undo. `session stop` requires
  `--force` and never runs implicitly.
- Presence stays out of this CLI; the existing `discord-window-presence`
  service keeps owning Rich Presence.

## Tests

See `tests/TEST.md` (plan + results). Full suite: 22 tests (7 unit + 15
E2E), 22 passed in 54.99s on the laptop 2026-11-24, live against the real
Discord client (send read-back message 1574784672334880920, file message
1574784744309268551 with a `cdn.discordapp.com` attachment, full quit +
relaunch with `launched: true`). Run it with
`CLI_ANYTHING_FORCE_INSTALLED=1 python3 -m pytest cli_anything/discord/tests/ -v -s`
from the package dir on the laptop.
