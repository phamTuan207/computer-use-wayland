# Work log - cli-anything-discord (Phases 2-6)

Wall-clock Asia/Ho_Chi_Minh. T+0 = task receipt 2026-11-24 20:32:39 +07.

## Worker 3 (Phases 2-3)
- 20:32:39 (T+0m): task received. Read HARNESS.md Phases 2-3 + Principles,
  Phase 1 analysis, ToS research, session-locking guide, repl_skin.py.
- 20:33 (T+1m): verified live: Discord CDP up on 9229 (Chrome/152,
  Electron 44.10.2, discord 1.0.169), test DM page target already open.
  Laptop has Node 26, uv 0.13.9, no system pip, no click, no python
  websocket-client. Decision: transport = Node 26 built-in WebSocket
  (utils/cdp_client.mjs), install via `uv tool install --editable`.
- 20:35 (T+3m): owner follow-up received: minimize Vision/mouse, CDP only.
  Design already CDP-only; added the rule to README.md + SKILL.md.
- 20:35-20:40 (T+3-8m): wrote the package (Click CLI + REPL default,
  session with locked saves, Node CDP client, backend, README, draft
  SKILL.md, TEST.md plan, 5 unit tests). Synced to laptop via rsync.
- 20:40 (T+8m): `uv tool install --editable` (detached) installed
  cli-anything-discord 1.0.0 + click 8.5.1 + prompt-toolkit 3.0.53.
- 20:41 (T+9m): smoke test live. `status` PASS. `servers list` FAIL:
  "server rail not found". Probe found the cause: Vietnamese locale,
  rail aria-label is "Thanh bên máy chủ", not "Servers" (Phase 1's
  English selector). Fixed SERVERS_JS to use the locale-proof
  `data-list-item-id^="guildsnav___"` hook. Retest PASS (13 servers).
- 20:42 (T+10m): `channels list --dm` PASS (8 DMs, test DM present).
  `channels open 865272264831139840` PASS. `messages read --limit 5`
  PASS (5 msgs, id/author/timestamp/content) but 2 authors empty:
  Discord omits the author header on follow-up messages. Fixed READ_JS
  to inherit the last seen author. Retest PASS (all authors filled).
- 20:43 (T+11m): `messages send` to test DM PASS (returned ok, composer
  label "Nhắn @Violet Joestar"). Read-back probe: new message
  1574781159320199189 with exact text. Slate send = Input.insertText +
  Enter rawKeyDown/keyUp. VERIFIED LIVE.
- 20:44 (T+12m): `messages send-file` PASS. Read-back: new message
  1574781352874872916, attachment confirmed on CDN
  (cdn.discordapp.com/attachments/865272264831139840/.../discord-smoke-test.txt).
  VERIFIED LIVE.
- 20:45 (T+13m): `session attach` PASS (note: --json is a group option,
  must precede the subcommand). REPL piped smoke PASS (banner + status).
  `session show` PASS. 5/5 unit tests PASS (pytest 9.2.0 in tool env).
- 20:46 (T+14m): `session start` smoke test + commit to repo.

## Test traffic sent (all to the Violet Joestar test DM only)

1. Text: "[cli-anything-discord smoke test] hello from the CLI"
   (message 1574781159320199189).
2. File: /tmp/discord-smoke-test.txt with caption
   "[cli-anything-discord smoke test] file upload"
   (message 1574781352874872916, attachment on CDN).

No other channel, no public server, no other DM received anything.

## Known minor issues (for the test worker)

- `channels open` reports `channel_title: ""` in DM views (the `h1`
  selector finds no text there); session `current_channel_name` stays
  null. Cosmetic only.
- Server names from the rail carry locale unread-count prefixes
  (e.g. "Tin nhắn chưa đọc, Optimus[Prime]").
- `messages read` returns the viewport window; scrolling up loads older
  messages, so the newest messages can leave the DOM after a scroll.
  A read-back check should scroll to bottom first (see /tmp/probe-last.mjs).
- No Vision/mouse anywhere in this CLI (owner rule 2026-11-24). All
  operations are CDP. Nothing in the CLI required a Vision/mouse step.

---

# Worker 4 work log - cli-anything-discord (Phases 4-6, 6.5 + report draft)

Wall-clock Asia/Ho_Chi_Minh. T+0 = task receipt 2026-11-24 20:41:51 +07.

- 20:41:51 (T+0m): task received. Read HARNESS.md Phases 4-6 + 6.5,
  Phase 1 analysis, ToS research, Worker 3 WORKLOG.
- 20:43 (T+1m): verified repo split with `git ls-remote`: CLI source is
  in phamTuan207/muse-army-ranger, branch todolist-push, HEAD 6aa22a2
  (Worker 3's commit); earlier Discord files (ToS 00e3e462, Phase 1
  ce4389ec/39044449) are in phamTuan207/computer-use-wayland,
  todolist-push @ c400f12. All new work stays in muse-army-ranger.
  Local landing clone: ~/frontend-agent-kit/repo (on todolist-push).
- 20:43 (T+1m): verified live: Discord 1.0.169 running (pid 765722),
  CDP answering on 9229, installed CLI at ~/.local/bin/cli-anything-discord.
  Note: process comm is "Discord" (capital D); `pgrep -x discord`
  matches nothing, so the Phase 3 `session stop` (`pkill -x discord`)
  could never quit Discord. Fixed (see below).
- 20:44 (T+2m): wrote TEST.md Part 1 (23 planned: 7 unit + 16 E2E) and
  tests/test_full_e2e.py (subprocess via _resolve_cli + live E2E: read,
  send + read-back, send-file + attachment-URL read-back, full
  quit/relaunch). Synced to laptop via tar-over-SSH (rsync -e with the
  ssh wrapper fails: "100.70.92.52: command not found").
- 20:45 (T+3m): first full run: 16 passed, 6 failed in 49.16s. One
  cascade: limit-10 read returned zero rows (scroll-up unloaded the
  viewport, never scrolled back); send "composer not found"; send-file
  "file input not found in DOM" (channel view still loading). Relaunch:
  `session stop --force` DID quit Discord fully (CDP down, no process),
  but `session start` failed after 20s: the relaunch had triggered a
  Discord self-update 1.0.169 -> 1.0.170 and the updater relaunched the
  client WITHOUT --remote-debugging-port (cmdline had no flag; the
  inherited 9229 listener accepted TCP but never answered HTTP/WS).
- 20:46-20:50 (T+4-8m): fixes in utils/discord_backend.py +
  discord_cli.py: (1) read scrolls back to bottom before the final read
  + polls for messages to appear; (2) send/send-file wait up to 15s for
  composer / file input; (3) ensure_running wait 20s -> 60s; (4) pkill
  -x Discord (lowercase fallback); (5) READ_JS adds per-message
  `attachments` (CDN hrefs); (6) resolve_page_target fails with a clear
  opt-in message when CDP is absent (was a bare "fetch failed").
  Verified live with Discord down: attach + read both name `session
  start` and the flag. Then quit the wedged 1.0.170 instance fully and
  relaunched via `session start`: launched:true, CDP answering,
  discord 1.0.170, cmdline carries --remote-debugging-port=9229.
- 20:51-20:53 (T+9-11m): second full run: 22 PASSED in 54.99s (7 unit +
  15 E2E; relaunch implemented as 1 combined test, not 2). Live evidence:
  send read-back message 1574784672334880920; file message
  1574784744309268551 with attachment on cdn.discordapp.com; relaunch
  launched=True, target 3F35B522C61F59C46142820905CDF1AA, post-relaunch
  read OK. Run marker e2e-20261124-2051-b7c10a.
- 20:53-20:55 (T+11-13m): TEST.md Part 2 (full output, stats, gaps);
  SKILL.md finished to canonical form via skill_generator.py output as a
  cross-check (generator's draft was generic/wrong on project/undo, so
  the Phase 3 draft was finished by hand with verified live outputs);
  README.md + SKILL.md updated with the owner design principle
  (2026-11-24 20:48/20:49): machine-private vs portable split, CDP
  control OPTIONAL, default OFF, with the exact enable path and the
  loud-failure behavior when off.
- 20:55+ (T+13m): final report draft
  (~/workspace/machine-control-20261124/discord-message-control-REPORT.md)
  + commit to muse-army-ranger todolist-push (explicit pathspec, verified
  via git ls-remote).

## Test traffic sent (Worker 4, all to the Violet Joestar test DM only)

1. Text: "[cli-anything-discord e2e e2e-20261124-2051-b7c10a] send-ok probe"
   (sent, verified by its own ok; read-back covered by test 2).
2. Text: "[cli-anything-discord e2e e2e-20261124-2051-b7c10a] hello from
   the E2E suite" (message 1574784672334880920, read back with exact text).
3. File: discord-e2e-test.txt with caption "[...] file upload"
   (send-file ok).
4. File: discord-e2e-attach.txt with caption "[...] attachment check"
   (message 1574784744309268551, attachment URL on cdn.discordapp.com).
   (First-run failures sent NOTHING: the sends failed before typing.)

No other channel, no public server, no other DM received anything.
Discord was quit fully twice (once by the relaunch test, once manually to
clear the wedged 1.0.170 instance) and relaunched; it is running again
with CDP on 9229 at the end of this work.
