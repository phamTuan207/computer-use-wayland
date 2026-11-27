# Discord message-control CLI: Phase 1 Codebase Analysis

- Date: 2026-11-24, work window 20:26:59 to 20:31 Asia/Ho_Chi_Minh (see work log at the end)
- Analyst: Worker 1 (Phase 1 only, analysis, no building)
- Pipeline: CLI-Anything 7-phase, HARNESS.md Phase 1
- Scope: Discord desktop message read/send control. ZCode is OUT of scope. No OpenRouter.
- Test target (owner instruction, 2026-11-24 20:28): the DM with "Violet Joestar", the owner's clone nick. All later read/send/file tests use this DM. Phase 1 itself sent nothing and typed nothing.

## 1. Backend engine

Discord desktop 1.0.169 is an Electron app (Chromium + Node). Evidence from the live
CDP `/json/version` endpoint on the laptop:

- `Browser: Chrome/152.0.7977.169`, `Protocol-Version: 1.3`
- User-Agent: `Mozilla/5.0 (X11; Linux x86_64) ... discord/1.0.169 Chrome/152.0.7977.169 Electron/44.10.2`
- Binary: `/home/james/.local/opt/Discord/discord`
- Config dir: `/home/james/.config/discord/` (Chromium profile layout: `Local State`, `Cookies`, `Session Storage`, `app-1.0.169/`, `SingletonLock`, etc.)
- There is no local HTTP API, no scriptable backend CLI, and no supported automation
  interface for messages. The app is a web client (`https://discord.com/channels/...`)
  wrapped in Electron. All message state lives on Discord's servers and is rendered
  into the Chromium DOM. That makes the DOM itself the control surface.

## 2. GUI-to-API mapping

| GUI action | API / mechanism | Status |
|---|---|---|
| See presence (playing X) | Local IPC socket `$XDG_RUNTIME_DIR/discord-ipc-0`, opcode 0 handshake + opcode 1 `SET_ACTIVITY` | Works today (presence service), but presence only |
| Open a server / DM / channel | CDP `Page.navigate` to `https://discord.com/channels/<guildId>/<channelId>` or `/channels/@me/<dmChannelId>`; or click `a[href^="/channels/"]` | Proven live (see section 6) |
| Read messages in the open channel | CDP `Runtime.evaluate`: scrape `li[id^="chat-messages-"]` nodes | Proven live, read-only (see section 6) |
| Type and send a message | CDP: focus composer, insert text, dispatch Enter (design in Phase 2) | Not attempted in Phase 1 (read-only phase) |
| Send a file | CDP: set the upload file input (`DOM.setFileInputFiles`) or drive the upload button (design in Phase 2) | Not attempted in Phase 1 |
| Read/send via local IPC (RPC) | None exists. See section 7. | Rejected |
| Read/send via REST with a user token | `api.discord.com` with a user token (self-bot) | Rejected as primary path, fallback only (see section 7) |

## 3. Data model

- Identity: Discord snowflake IDs. Guilds, channels, DMs, messages are all snowflakes.
  DM channel with the test account: `865272264831139840` (URL form `/channels/@me/865272264831139840`).
- Message list in the DOM: one `li` per message, `id="chat-messages-<channelId>-<messageId>"`.
  The message id is the last dash segment. No local project file exists; the DOM is a
  live view of server state, paginated by scroll (only the viewport window is in the DOM).
- No native file format to manipulate. The CLI must not reimplement Discord; it drives
  the real client (HARNESS principle: the real software is a hard dependency).

## 4. Existing CLI tools

None for messages. Inventory:

- `discord-window-presence` service (`/home/james/.local/share/discord-window-presence/main.py`):
  presence only. It connects to `discord-ipc-0`, sends the opcode 0 handshake
  (`{"v": 1, "client_id": ...}`), then only ever sends opcode 1 frames with
  `cmd: SET_ACTIVITY` (or `activity: None` to clear). Client ids used: codex
  `1517375602662051900`, opencode `1538957549364322404`, claude `1521213655092428923`.
  It never reads or sends messages and cannot be extended to do so (see section 7).
- Read-only IPC probe: `~/workspace/machine-control-20261124/discord_ipc_probe.py`
  (handshake only, stops after READY). Used in this phase to confirm the logged-in user.
- No Discord CLI, no `discord` subcommand, no bot token in scope. Nothing else exists.

## 5. Command / undo system

Not applicable. Discord has no local undo/redo for messages. Message send is
irreversible (delete is a separate destructive action and is OUT of the Phase 2 scope
unless the owner asks for it). The CLI therefore needs no undo stack; it needs
confirmation/idempotency guards instead (Phase 2: send requires an explicit channel
target, and test sends go only to the designated test DM).

## 6. Chosen control surface: Chrome DevTools Protocol (CDP) on the Electron client

### 6.1 Launch (live, proven)

Discord was NOT running at the start of this phase (no `discord-ipc-*` socket, no
Discord process; only the presence service, pid 1117, was running idle).

First launch attempt failed: Electron errored `Missing X server or $DISPLAY` and
`The platform failed to initialize. Exiting.` because `DISPLAY` was not set.
Working launch (detached, survives the short SSH sessions):

```
XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-1 DISPLAY=:0 XDG_SESSION_TYPE=wayland \
DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus \
HYPRLAND_INSTANCE_SIGNATURE=<from ls /run/user/1000/hypr/ | head -n1> \
/home/james/.local/opt/Discord/discord --remote-debugging-port=9229
```

Key points: `DISPLAY=:0` (XWayland) is REQUIRED; the other GUI env vars alone are not
enough. Port 9229 was chosen to avoid colliding with the Muse PWA CDP on 9224.
Log: `/tmp/discord-cdp-9229.log` on the laptop.

### 6.2 Live evidence (all read-only, 2026-11-24 ~20:28-20:30 +07)

CDP `/json/version` (curl, laptop):

- `Browser: Chrome/152.0.7977.169`, `Protocol-Version: 1.3`, Electron 44.10.2, discord 1.0.169
- `webSocketDebuggerUrl: ws://127.0.0.1:9229/devtools/browser/ea8cfcaa-98a7-4255-aeef-a17ba8766735`

CDP `/json/list` (curl, laptop): main page target

- `id: 6CF67A765793FA1F26FD7965534AEE5A`, `type: page`
- `title: @Violet Joestar`, `url: https://discord.com/channels/@me/865272264831139840`
- `webSocketDebuggerUrl: ws://127.0.0.1:9229/devtools/page/6CF67A765793FA1F26FD7965534AEE5A`

Logged-in user: confirmed live via the IPC probe handshake READY reply
(`python3 discord_ipc_probe.py`, socket `/run/user/1000/discord-ipc-0`, exit 0).
The username and user id are verified but WITHHELD from this repo file per the
no-PII-on-GitHub rule; they are reported in the Phase 1 handoff to the coordinator.
The account is a normal user account (not a bot).

DOM probe (Node 26 built-in WebSocket, `Runtime.evaluate`, read-only):

- Server rail present: `nav[aria-label="Servers"]`, 13 servers listed (count only).
- DM/channel sidebar present; DM links are `a[href^="/channels/@me/"]`.
- After `Page.navigate` to the test DM, title is `@Violet Joestar`,
  path `/channels/@me/865272264831139840`, header shows the test account name.
- Message list: 13 messages visible in the viewport at probe time.
- Composer present, aria-label `Nhắn @Violet Joestar` (locale is Vietnamese;
  in English it reads `Message @Violet Joestar`).
- No message text is quoted in this file. No message was sent, no text was typed.

### 6.3 DOM selectors to use (Phase 2/3)

Primary selectors use stable hooks (roles, aria-labels, id prefixes). Hashed class
suffixes (e.g. `_2i8Bfm`, `_q99V_-`) are build-specific and WILL change across Discord
updates, so use them only as fallbacks, never as the sole selector.

| Element | Primary selector | Fallback / notes |
|---|---|---|
| Server rail | `nav[aria-label="Servers"]` | `[data-list-item-id^="guildsnav___"]` per server |
| DM / channel links | `a[href^="/channels/"]` | guild channels also carry `data-list-item-id^="channels___"`; DMs use `/channels/@me/<id>` |
| Message list | `li[id^="chat-messages-"]` | container `[class*="messagesWrapper"]`; id form is `chat-messages-<channelId>-<messageId>` |
| One message | `li.messageListItem_*` | child `div.message_* > div.contents_*` |
| Message author | `span.username_*` inside the message `h3.header_*` | `span.headerText_*` wraps author + timestamp |
| Message timestamp | `span.timestamp_* > time` | `time` carries the `datetime` attribute |
| Message content | `div.messageContent_*` (`div.markup_*`) | attachments/embeds are sibling nodes inside the same message |
| Composer | `div[role="textbox"][contenteditable="true"]` | aria-label `Nhắn @<name>` / `Message @<name>`; class contains `slateTextArea` |
| Composer container | `[class*="channelTextArea"]` | inner `textArea_* slateContainer_*` |
| Channel header | `h1` in the chat title area | shows DM recipient name |

### 6.4 CDP operations the CLI will need (Phase 2 design)

- Attach: HTTP `GET /json/list` on 127.0.0.1:9229, pick the `type: page` target,
  connect its `webSocketDebuggerUrl`.
- Read: `Runtime.evaluate` scraping the selectors above; scroll the message scroller
  (`[class*="scroller"]` inside the messages wrapper) to load older messages.
- Send: focus composer, insert text, dispatch Enter (exact event sequence is a
  Phase 2/3 detail; Slate-based composer, so plain `value` assignment will not work).
- Files: `DOM.setFileInputFiles` on the upload input (Phase 2/3 detail).
- Session: the CLI must ensure Discord is running with `--remote-debugging-port=9229`
  (launch if absent, attach if present), and must never kill the owner's Discord
  without an explicit stop command.

### 6.5 Limitations found

- Only the viewport window of messages is in the DOM; history requires scrolling.
- No push/event stream over CDP for new messages; the CLI polls by re-reading.
- Hashed class names drift per build; selectors must prefer roles/aria/id prefixes.
- CDP is bound to 127.0.0.1 on the laptop; the CLI runs on the laptop (over SSH),
  same as the Muse PWA CDP pattern on port 9224.
- Driving the real client means the owner's Discord window visibly navigates when the
  CLI opens a channel. That is expected and acceptable for this owner-approved tool.

## 7. Rejected alternative 1: Discord RPC / IPC (Rich Presence)

REJECTED, with evidence, not assumption.

- Local service source (`discord-window-presence/main.py`): the only IPC operations
  it ever performs are the opcode 0 handshake and opcode 1 `SET_ACTIVITY` frames.
- Official docs, `https://discord.com/developers/docs/topics/rpc` (crawled 2026-11-24
  13:29 UTC): the full RPC command table is DISPATCH, AUTHORIZE, AUTHENTICATE,
  GET_GUILD, GET_GUILDS, GET_CHANNEL, GET_CHANNELS, SUBSCRIBE, UNSUBSCRIBE,
  SET_USER_VOICE_SETTINGS, SELECT_VOICE_CHANNEL, GET_SELECTED_VOICE_CHANNEL,
  SELECT_TEXT_CHANNEL, GET_VOICE_SETTINGS, SET_VOICE_SETTINGS, SET_CERTIFIED_DEVICES,
  SET_ACTIVITY, SEND_ACTIVITY_JOIN_INVITE, CLOSE_ACTIVITY_REQUEST. There is NO
  send-message command and NO read-messages command. `SELECT_TEXT_CHANNEL` only
  switches the open channel. `MESSAGE_CREATE` / `MESSAGE_UPDATE` / `MESSAGE_DELETE`
  are subscribe-only EVENTS (notifications, no history fetch), and the docs state the
  `rpc_token` path explicitly disallows the `messages.read` scope.
- Conclusion: IPC/RPC can do Rich Presence only (write-only presence). It cannot read
  or send messages. The existing presence service stays as-is; the message CLI does
  not use IPC.

## 8. Rejected alternative 2: user-token REST API (self-bot) - fallback only

The REST API at `api.discord.com` with a user token WOULD give full read/send, but:

- It is self-botting: automating a user account against Discord's terms. A prior
  research commit on branch `todolist-push` documents the ban and the per-route
  account risk (`00e3e462 Discord ToS research: self-bot ban, per-route account risk
  for message-control CLI`).
- It needs the owner's user token. NO token was extracted in this phase, from local
  storage or anywhere else. Credential extraction is forbidden and was not attempted.
- Recommendation: CDP (section 6) is the primary path. The token route is a fallback
  ONLY if CDP proves unworkable AND the owner supplies the token. The CLI
  must never read Discord's local storage for a token.

## 9. Phase 2 proposal: command groups for `cli-anything-discord`

Following HARNESS.md Phase 2 (subcommand CLI + REPL, `--json` on every command,
`info`/`list`/`status` introspection first):

- `status`: Discord process state, CDP endpoint reachability, page target id,
  logged-in user (from IPC READY or DOM), current channel. Read-only.
- `servers`: list servers (from the server rail / RPC `GET_GUILDS` as a read-only
  helper). Read-only.
- `channels`: list DMs and guild channels (`a[href^="/channels/"]`); `channels open
  <channelId>` navigates the client to a channel. Navigation only, no sending.
- `messages read <channelId> [--limit N] [--before <messageId>]`: scrape the message
  list DOM (scroll to load more), output author + timestamp + text as JSON.
  Default target for tests: the Violet Joestar DM.
- `messages send <channelId> --text "..."`: focus composer, insert text, send with
  Enter. Test target: the Violet Joestar DM only, per owner instruction.
- `messages send-file <channelId> --file <path> [--text "..."]`: upload an attachment
  via the file input. Test target: the Violet Joestar DM only.
- `session`: `session start` (launch Discord with `--remote-debugging-port=9229` if
  not running), `session attach`, `session stop` (explicit only, never implicit).
- Session state: JSON session file holding the CDP port, target id, and current
  channel (HARNESS session model). Presence stays OUT of this CLI; the existing
  `discord-window-presence` service keeps owning it.

## 10. Risks and open questions for Phase 2

- ToS risk: CDP drives the user's own logged-in client the same way the user would by
  hand; lower risk than a self-bot token, but still automation of the client. The
  owner approved building this path. Keep all test traffic in the Violet Joestar DM.
- Selector drift: hashed classes change per Discord build; Phase 3 must centralize
  selectors and fail loudly when a primary selector matches nothing.
- Slate composer send sequence (insert text + Enter) is unproven until Phase 5 tests
  it against the test DM.
- Discord must be relaunched with the debug flag after every full quit; `session
  start` must handle the stale `SingletonLock` case and the `DISPLAY=:0` requirement.
- The DM list in the probe showed other DM names; none are recorded in this file.
  Only the owner-designated test account is named here.

## 11. Work log (wall-clock Asia/Ho_Chi_Minh, elapsed from task receipt)

- 20:26:59 +07 (T+0m): task received. Read HARNESS.md Phase 1 + Principles,
  `~/workspace/ssh-laptop.sh`, `discord_ipc_probe.py`.
- 20:27 (T+1m): read presence service `main.py` live via SSH. Confirmed SET_ACTIVITY
  only. Discord not running (no `discord-ipc-*` socket, no Discord process).
  Found `HYPRLAND_INSTANCE_SIGNATURE` for the GUI env.
- 20:27 (T+1m): web search + official RPC docs read. RPC command table has no
  message operations.
- 20:27 (T+1m): launched Discord detached with `--remote-debugging-port=9229`.
  First launch FAILED (`Missing X server or $DISPLAY`, platform init failure).
- 20:27-20:28 (T+1-2m): found running GUI apps carry `DISPLAY=:0` (XWayland);
  relaunched with `DISPLAY=:0`. CDP answered.
- 20:28-20:29 (T+2-3m): `curl /json/version` and `/json/list` confirmed CDP
  (Chrome/152.0.7977.169, Electron/44.10.2, page target `6CF67A765793FA1F26FD7965534AEE5A`,
  test DM URL). Node 26 built-in WebSocket used for DOM probes (no python websocket libs).
- 20:29 (T+3m): DOM probe 1 on the Friends view: server rail, sidebar, DM links found;
  no message list (not a channel view). Navigated via CDP `Page.navigate` to the
  test DM (read-only navigation, no typing, no sending).
- 20:29 (T+3m): DOM probe 2 in the test DM: 13 visible messages, message/composer
  selectors recorded (section 6.3). IPC probe handshake READY confirmed the logged-in
  user (identity withheld from this file, see section 6.2).
- 20:30-20:31 (T+4-5m): official RPC docs page fetched and cited; this analysis
  written and committed.
- Test traffic sent in this phase: none. Messages sent: 0. Text typed: none.
  Only read-only CDP evaluation, one read-only navigation, and one IPC handshake.
