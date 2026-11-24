# Discord message-control CLI: final report (Phases 1-6.5)

- Date: 2026-11-24, work window 20:26-20:56 Asia/Ho_Chi_Minh
- Owner: dang (Pham Tuan Huy). Machine: Omarchy laptop (user james).
- Pipeline: CLI-Anything 7-phase (HARNESS.md). Phase 7 (PyPI) NOT done,
  deliberately: this CLI is machine-private (see section 6), not a
  public package.
- Status: DONE through Phase 6.5. Full test suite green: 22/22 pytest
  pass, live against the real Discord client.

## 1. The control path (what it is and how it works)

Discord desktop (Electron, Chromium + Node) has no supported automation
interface for messages: no local HTTP API, no scriptable backend CLI, and
the local IPC/RPC socket only does Rich Presence (`SET_ACTIVITY`; the
official RPC command table has no send-message or read-messages command).
The REST API with a user token would work but is self-botting (see
section 5) and needs a token this project never extracts, asks for, or
stores. So the CLI drives the REAL official client over Chrome DevTools
Protocol on `127.0.0.1:9229`:

- Attach: `GET /json/list`, pick the `discord.com` page target at runtime
  (never a hardcoded target id), connect its `webSocketDebuggerUrl`.
- Read: `Runtime.evaluate` scraping `li[id^="chat-messages-"]` rows
  (id, author, timestamp, content, attachments). Only the viewport window
  is in the DOM; the CLI scrolls up (bounded, 5 pages) to load older
  messages and always scrolls back to the bottom before the final read.
- Send: focus the Slate composer (`div[role="textbox"]`), `Input.insertText`,
  then Enter via `Input.dispatchKeyEvent` (rawKeyDown + keyUp).
- Send a file: `DOM.setFileInputFiles` on `input[type=file]`, optional
  caption, Enter.
- Transport: Node 26 built-in WebSocket, no npm deps
  (`utils/cdp_client.mjs`: `targets`, `version`, `eval`, `navigate`,
  `send`, `sendfile`). Python (Click) shells out to it.
- Session: JSON session file (`~/.cli-anything-discord/session.json`)
  holding CDP port, target id, current channel, saved with the HARNESS
  exclusive-lock pattern. REPL is the default (no args); every command
  supports `--json` (group option, goes before the subcommand).

Launch (verified live): Discord needs `DISPLAY=:0` (XWayland) plus
`XDG_RUNTIME_DIR=/run/user/1000`, `WAYLAND_DISPLAY=wayland-1`,
`DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus` and
`HYPRLAND_INSTANCE_SIGNATURE`. `session start` launches it detached with
`--remote-debugging-port=9229` and waits up to 60s for a real CDP answer.

## 2. Commands

```
cli-anything-discord status                                        # process, CDP, current channel (read-only)
cli-anything-discord servers list                                  # 13 servers (live)
cli-anything-discord channels list [--dm | --guild]                # 8 DMs (live)
cli-anything-discord channels open <channelId>                     # navigate + set current channel
cli-anything-discord messages read [channelId] [--limit N]         # default: current channel
cli-anything-discord messages send [channelId] --text "..."
cli-anything-discord messages send-file [channelId] --file <path> [--text "..."]
cli-anything-discord session start | attach | show | stop --force  # stop requires --force, never implicit
cli-anything-discord                                               # REPL (default)
```

Installed on the laptop as `cli-anything-discord`
(`uv tool install --editable /home/james/workspace/discord-cli`,
entry `~/.local/bin/cli-anything-discord`, version 1.0.0).

## 3. Live-test evidence (all in the Violet Joestar test DM only)

Test target (owner instruction): DM with "Violet Joestar", channel
865272264831139840. No other channel, no public server, no other DM
received anything. Full suite: `tests/TEST.md` (plan + full output).

Final run, 2026-11-24 ~20:51-20:53 +07, Discord 1.0.170, CDP 9229,
`CLI_ANYTHING_FORCE_INSTALLED=1`: **22 passed in 54.99s** (7 unit + 15
E2E, 0 failed, 0 skipped). Run marker `e2e-20261124-2051-b7c10a`.

- Live read: `messages read` returns real messages with
  id/author/timestamp/content/attachments; newest id at the time
  1574781352874872916; authors and timestamps all filled.
- Live send: text "[cli-anything-discord e2e e2e-20261124-2051-b7c10a]
  hello from the E2E suite" sent, verified by read-back: new message id
  **1574784672334880920**, exact text present.
- Live send-file: file `discord-e2e-attach.txt` with caption "[...]
  attachment check" sent, verified by read-back: message id
  **1574784744309268551**, attachment URL
  `https://cdn.discordapp.com/attachments/865272264831139840/1574784744007147643/discord-e2e-attach.txt?...`
  (query params are Discord's signed-URL expiry fields).
- Session relaunch (required, was untested): `session stop --force`
  quit Discord FULLY (verified: CDP down, no `Discord` process), then
  `session start` returned `running: true, launched: true`, new target
  **3F35B522C61F59C46142820905CDF1AA**, `session attach` ok, and a
  post-relaunch `messages read` returned 3 messages (newest
  1574784744309268551). Relaunch proven end to end.
- Worker 3 smoke traffic (same DM): text message 1574781159320199189,
  file message 1574781352874872916.

First run failed 6/22 and drove real fixes (all in
`utils/discord_backend.py` + `discord_cli.py`, see `tests/TEST.md` and
`WORKLOG.md`): read scrolls back to bottom + polls for messages; send /
send-file wait up to 15s for composer / file input; launch wait 20s ->
60s; `session stop` now kills `Discord` (capital D; the old
`pkill -x discord` matched nothing); `READ_JS` surfaces `attachments`;
CDP-absent errors name the opt-in fix instead of a bare "fetch failed".

Incident during testing: the first relaunch triggered a Discord
self-update 1.0.169 -> 1.0.170, and the updater relaunched the client
WITHOUT `--remote-debugging-port`. The inherited 9229 listener accepted
TCP but never answered HTTP or WS, so `session start` correctly failed
after its poll. Recovery was a full quit + fresh `session start`, after
which 1.0.170 launched with the flag and CDP answered. Lesson recorded:
after any Discord self-update, expect the debug flag to be dropped and
relaunch via `session start`.

## 4. ToS risk note (read before use; not legal advice)

Research: `discord-tos-research.md`, sources read 2026-11-24
(Terms effective Dec 15, 2026; Community Guidelines; self-bot support
article; Developer Terms; Developer Policy; OAuth2 docs; Platform
Manipulation explainer). Discord can change these pages at any time;
re-check before any release.

- Automating a normal user account is forbidden: Community Guidelines
  rule 14 ("Do not use self-bots or user-bots. Each account must be
  associated with a human, not a bot.") and the support article
  ("Automating normal user accounts ... is forbidden, and can result in
  an account termination if found."). Stated worst case: account
  termination, with or without notice, warning first not promised.
- The CDP/GUI-automation route is NOT named anywhere in the terms (no
  clause mentions CDP, DevTools, GUI automation or RPA). Honest position:
  probably treated as self-botting if detected, because the rule turns
  on the account being automated, not the mechanism; but Discord has not
  published a position on GUI automation specifically. Do NOT present
  this route as safe or compliant.
- The user-token REST route is the clearest violation (textbook
  self-bot) and is NOT used: this CLI never asks for, reads, or stores a
  user token or password.
- The only sanctioned automation is a proper bot token, which cannot read
  the owner's DMs or act as the owner, so it does not cover this use case.
- The owner approved building this CLI knowing the risk; that approval
  does not change Discord's terms or bind Discord. Mitigations in place:
  test traffic only in one DM, low volume, human-paced, no bulk or
  unsolicited messages, local-only, 2FA on the account is the owner's
  call. For anything beyond personal test traffic, prefer a secondary
  account the owner can afford to lose.

## 5. Vision / mouse note

ZERO Vision/mouse use, anywhere, in any phase. Owner rule (2026-11-24):
minimize Vision/mouse maximally, prioritize CLI/API/CDP; use
Vision/mouse only when forced with no alternative, and record where and
why. Nothing in this CLI required a Vision/mouse step: navigation,
reading, sending, file upload, launch, attach and quit are all CDP or
process operations. No Vision/mouse step was added at any point, and no
diagnosis in testing needed the screen either (the hung-client incident
was diagnosed from process state, cmdline, socket state and logs). If a
future Discord change breaks a CDP path and only a Vision/mouse step can
replace it, that step must be documented in README.md first (where, why
CDP cannot do it) before it is added.

## 6. Machine-private vs repo-shared (owner design principle, 2026-11-24 20:48/20:49)

Apps on the owner's machine are deliberately optimized for AI (CDP port,
CLI, setup of his own). The computer-use repo is for outsiders, whose
apps are usually NOT optimized for AI (no CDP, no CLI, no setup). So the
repo must work on stock, unoptimized apps: the vision/mouse/accessibility
path must stay strong there. Machine-private optimization MAY still be
committed to a repo, but only as OPTIONAL (opt-in), never forced the way
it is on the local machine (where it is always on). Every optimization
decision must say clearly which side it belongs to.

Applied to this Discord work, the split is:

- Machine-private (only runs on the owner's laptop as built): Discord
  binary path, CDP port 9229, the GUI launch env (`DISPLAY=:0`,
  `XDG_RUNTIME_DIR`, `HYPRLAND_INSTANCE_SIGNATURE`), install via
  `uv tool install --editable`, the Violet Joestar test DM, the whole
  "launch Discord with the debug flag" setup. None of this is assumed
  to exist anywhere else.
- Portable / repo-shared (worth reusing): the pattern, not the setup.
  Launch any Electron/Chromium app with `--remote-debugging-port`,
  resolve the page target at runtime via `/json/list`, drive it with
  `Runtime.evaluate` / `Input.*` / `DOM.setFileInputFiles`, prefer
  roles/aria-labels/stable hooks over hashed classes. The CDP client
  (`utils/cdp_client.mjs`) is app-agnostic.
- Optional / opt-in, default OFF: CDP control of Discord is optional.
  A normally launched Discord has no CDP endpoint and this CLI does
  nothing to it: no relaunch on its own, no injection, no settings
  changed. Opt in with `session start` (or launching Discord with the
  flag yourself); opt out by quitting normally or `session stop
  --force`, after which Discord is back to stock and the CLI is inert.
  When CDP is off, the CLI fails LOUDLY with the exact enable path
  (verified live with Discord down: `session attach` and `messages
  read` both name `session start` and `--remote-debugging-port=9229`).
  `status` is the read-only probe (`discord_running: false`).
  If any part of this ever goes into a shared repo, it goes in exactly
  this shape: optional, default off, working fine with it off.

## 7. Repo split note (owner decision needed)

The Discord work is currently SPLIT across two repos, verified with
`git ls-remote` 2026-11-24:

- phamTuan207/muse-army-ranger, branch `todolist-push`, HEAD 6aa22a2:
  the CLI source itself (`improvements/discord-cli/`, 15 files, Worker 3)
  plus all of Worker 4's work (tests, TEST.md results, finished SKILL.md,
  README updates, WORKLOG). This is where ALL new work in this report
  lives.
- phamTuan207/computer-use-wayland, branch `todolist-push`, HEAD
  c400f12: the earlier files (ToS research 00e3e462, Phase 1 analysis
  ce4389ec/39044449).

Nothing was pushed to computer-use-wayland in this phase, per the brief.
The owner should decide whether to consolidate (e.g. move the ToS
research + Phase 1 analysis into muse-army-ranger, or move the CLI into
computer-use-wayland). Until then, the ToS research and Phase 1 files
live in a different repo from the CLI they describe; the SKILL.md and
README.md reference them by filename.

## 8. What is still missing

- REPL has no pytest test (only a piped smoke in Phase 3: banner +
  status). `session stop` without `--force` (refusal path) is untested.
- `messages read` with a large `--limit` loads at most 5 scroll-pages of
  older history; very old history is not covered.
- Guild-channel send is untested (test DM only, by owner instruction).
- A Discord self-update mid-run drops the debug flag (observed once);
  recovery is manual (`session stop --force` + `session start`), not
  automated, and there is no watcher that notices the flag is gone.
- No delete/undo command (sending is irreversible by design; delete was
  out of scope).
- Phase 7 (PyPI publishing) not done and not recommended: this CLI is
  machine-private, and publishing it would hand out a self-bot tool with
  the owner's paths baked in.
- The two-repo split (section 7) is unresolved pending the owner's call.
- Known cosmetic issues: `channels open` reports `channel_title: ""` in
  some DM views; server names carry locale unread-count prefixes
  ("Tin nhắn chưa đọc, ..."); session `current_channel_name` can be
  concatenated ("Violet Joestarvioletjoestar1154").

## 9. Files and locations

- CLI source (VM work dir): `~/workspace/machine-control-20261124/discord-cli/`
- Installed on laptop: `/home/james/workspace/discord-cli/`,
  entry `~/.local/bin/cli-anything-discord`
- Phase 1 analysis: `~/workspace/machine-control-20261124/discord-phase1-analysis.md`
- ToS research: `~/workspace/machine-control-20261124/discord-tos-research.md`
- Work log: `discord-cli/WORKLOG.md` (Workers 3 + 4, wall-clock +07)
- Tests: `discord-cli/cli_anything/discord/tests/` (`TEST.md` plan +
  results, `test_core.py`, `test_full_e2e.py`)
- Skill: `skills/cli-anything-discord/SKILL.md` (canonical, repo root)
  + packaged copy `cli_anything/discord/skills/SKILL.md`
- This report: `~/workspace/machine-control-20261124/discord-message-control-REPORT.md`
- Repo: phamTuan207/muse-army-ranger, branch `todolist-push`
  (commit for this phase: see `git log`; verified via `git ls-remote`)

## 10. Work log (this report's phase, Worker 4)

Wall-clock Asia/Ho_Chi_Minh, T+0 = 2026-11-24 20:41:51 +07. T+1m: read
harness + prior phases, verified repo split and live state. T+2m: TEST.md
Part 1 + test_full_e2e.py written, synced to laptop. T+3m: first run
16 passed / 6 failed (49.16s). T+4-8m: diagnosed the cascade + the
1.0.170 self-update incident, fixed backend + CLI, verified the CDP-absent
error messages live, relaunched Discord cleanly. T+9-11m: second run
22/22 passed (54.99s). T+11-13m: TEST.md Part 2, SKILL.md, README.md
(machine-private / opt-in notes). T+13m+: this report + commit.
Total elapsed to report: ~15 minutes.
