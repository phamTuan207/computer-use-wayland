# TEST.md - cli-anything-discord (HARNESS Phase 4 plan; Phase 6 results appended by test worker)

## Test Inventory Plan (Phase 4, written before test code)

- `test_core.py`: 7 unit tests planned (session save/load round-trip, missing
  file defaults, corrupt file defaults, set_current_channel, repeated-save
  no-corruption, test-DM constant, READ_JS attachment extraction present).
- `test_full_e2e.py`: 16 E2E tests planned:
  - `TestCLISubprocess` (7): `--help`, `--json status`, `servers list`,
    `channels list --dm` (test DM present), `channels open` (test DM),
    `messages read --limit 5` (JSON shape), `session show`.
  - `TestLiveRead` (2): read returns real messages with
    id/author/timestamp/content; every row has a numeric snowflake id and a
    non-empty author.
  - `TestLiveSend` (2): send a unique marker text to the test DM; read-back
    finds the exact text with a new message id. Send returns `ok: true`.
  - `TestLiveSendFile` (3): send-file with a unique caption to the test DM;
    read-back finds the caption; the message carries an attachment URL on
    `cdn.discordapp.com/attachments/865272264831139840/`; send-file returns
    `ok: true`.
  - `TestSessionRelaunch` (2): `session stop --force` quits Discord fully
    (CDP down, no `Discord` process); `session start` relaunches it detached
    (`launched: true`), CDP answers, `session attach` works, and a
    follow-up `messages read` proves the relaunched client works.
- Total planned: 23 tests (7 unit + 16 E2E). No test may skip: if Discord or
  CDP is down, the live tests FAIL loudly, they do not skip (HARNESS rule:
  the real software is a hard dependency).

Test target for ALL live traffic: the Violet Joestar DM, channel
865272264831139840 (owner-designated). No other channel, no public server,
no other DM receives anything. Each send uses a unique per-run marker
(`[cli-anything-discord e2e <token>] ...`) so read-back is unambiguous
against earlier test traffic.

## Unit Test Plan

- Module `core/session.py`: `_locked_save_json` (exclusive lock, truncate
  inside lock), `load_session` defaults + corrupt-file tolerance,
  `set_current_channel`, repeated saves.
  Edge cases: missing file, corrupt JSON, concurrent-ish repeated writes.
  Expected: 5 tests (Worker 3, already passing; re-run to confirm).
- Module `utils/discord_backend.py` (constants / static checks, no Discord
  needed): `TEST_DM_CHANNEL_ID` is the owner-designated test DM id;
  `READ_JS` extracts per-message `attachments` (CDN hrefs) so a file send
  can be verified by read-back.
  Expected: 2 tests.

## E2E Test Plan

- Subprocess tests use the HARNESS `_resolve_cli("cli-anything-discord")`
  helper (installed command, never a hardcoded path) and run with
  `CLI_ANYTHING_FORCE_INSTALLED=1`. No `cwd` is set; the installed command
  must work from any directory. `--help` and `--json` are exercised on
  every command group used.
- Real workflows: open test DM -> read -> send -> read-back verify ->
  send-file -> read-back verify (attachment URL) -> quit Discord fully ->
  relaunch via `session start` -> attach -> read again. All traffic ONLY
  in the Violet Joestar DM.
- Verify output properties: message JSON fields present (`id`, `author`,
  `timestamp`, `content`, `attachments`); send appears in a subsequent
  read with the exact text; file message carries an attachment URL on
  `cdn.discordapp.com`; relaunch reports `launched: true` and CDP answers
  afterwards.
- Print artifact evidence (channel id, message ids, attachment URL,
  relaunch `launched` flag) for manual inspection.
- Backend change required by the plan: `READ_JS` must surface attachments
  (Worker 3's read returned content only; a file send could not be verified
  by read-back). The test worker adds an `attachments` array per message
  (CDN/media hrefs inside the message row).

## Realistic Workflow Scenarios

- **Workflow 1, "Check what was said, then reply"**: `status` ->
  `channels open <test DM>` -> `messages read --limit 5` -> `messages send`
  a reply -> `messages read --limit 10` and confirm the reply is the
  newest message with the exact text. Simulates an agent answering a DM
  after reading context. Verified: read shape, send `ok`, read-back exact
  text + new id.
- **Workflow 2, "Send a file with a caption"**: create a small text file ->
  `messages send-file <test DM> --file <path> --text <caption>` ->
  `messages read --limit 10` and confirm the caption row carries an
  attachment URL on `cdn.discordapp.com/attachments/<test DM>/`.
  Simulates an agent delivering a generated file. Verified: send-file
  `ok`, caption present, attachment URL present and channel-scoped.
- **Workflow 3, "Discord was quit, bring it back"**: `session stop --force`
  -> confirm CDP is down and no `Discord` process remains ->
  `session start` -> confirm `launched: true`, CDP answers, `session attach`
  succeeds -> `messages read --limit 3` succeeds. Simulates recovery after
  the owner (or the machine) quit Discord. Verified: full quit, relaunch,
  attach, post-relaunch read.
- **Workflow 4, "Read-only inspection"**: `status` -> `servers list` (13
  servers) -> `channels list --dm` (test DM present) -> `messages read`.
  Simulates an agent orienting itself before acting. Verified: every
  command returns `ok: true` with JSON shape intact; nothing is sent.

## Test Results (Phase 6 - appended by test worker)

Run on the laptop 2026-11-24 ~20:51-20:53 +07 (Discord 1.0.170, CDP 9229,
installed `cli-anything-discord`, `CLI_ANYTHING_FORCE_INSTALLED=1`).
Full log: `/tmp/discord-e2e-phase5b.log` on the laptop.

### First run (20:45 +07): 16 passed, 6 failed in 49.16s

Failures, all one cascade from the channel view not being ready / the
message list virtualizing:

- `test_read_authors_and_timestamps_filled` (limit 10): "No messages found
  in the DOM" - scrolling up to load older messages unloaded the visible
  window and the read never scrolled back to the bottom.
- `test_send_returns_ok`, `test_send_verified_by_readback`: "composer not
  found" - send ran 2s after navigation while the channel view was still
  rendering; no wait for the composer.
- `test_send_file_returns_ok`,
  `test_send_file_verified_by_readback_attachment`: "file input not found
  in DOM" - same loading race for the upload input.
- `test_quit_relaunch_attach_and_read`: `session stop --force` DID quit
  Discord fully (verified: CDP down, no process - the `pkill -x Discord`
  fix works), but `session start` failed: "Discord did not answer CDP on
  port 9229 within 20s after launch". Root cause found afterwards: the
  relaunch triggered a Discord self-update 1.0.169 -> 1.0.170, and the
  updater relaunched the client WITHOUT `--remote-debugging-port`; the
  inherited listener on 9229 accepted TCP but never answered HTTP/WS.
  The 20s wait was also too short for a cold launch.

Fixes made by the test worker (all in `utils/discord_backend.py` and
`discord_cli.py`, see WORKLOG.md):

1. `read_messages` scrolls back to the bottom before the final read, and
   waits (polls) for messages to appear instead of failing on an empty DOM.
2. `send_message` / `send_file` wait up to 15s for the composer / file
   input to appear after navigation.
3. `ensure_running` wait 20s -> 60s (cold launch after a full quit).
4. `session stop --force`: `pkill -x discord` matched nothing (process
   comm is `Discord`, capital D); now kills `Discord` first, lowercase as
   fallback.
5. `READ_JS` surfaces per-message `attachments` (CDN hrefs) so a file send
   is verifiable by read-back.
6. `resolve_page_target` fails with a clear opt-in message when CDP is
   absent instead of a bare "fetch failed" (verified live with Discord
   down: `session attach` and `messages read` both name `session start`
   and `--remote-debugging-port=9229`).

### Second run (20:51 +07): 22 passed in 54.99s

```
============================= test session starts ==============================
platform linux -- Python 3.13.15, pytest-9.2.0, pluggy-1.7.0 -- /home/james/.local/share/uv/tools/cli-anything-discord/bin/python
cachedir: .pytest_cache
rootdir: /home/james/workspace/discord-cli
collecting ... [_resolve_cli] Using installed command: /home/james/.local/bin/cli-anything-discord
collected 22 items

cli_anything/discord/tests/test_core.py::test_locked_save_and_load_roundtrip PASSED
cli_anything/discord/tests/test_core.py::test_load_missing_session_returns_defaults PASSED
cli_anything/discord/tests/test_core.py::test_load_corrupt_session_returns_defaults PASSED
cli_anything/discord/tests/test_core.py::test_set_current_channel PASSED
cli_anything/discord/tests/test_core.py::test_double_save_no_corruption PASSED
cli_anything/discord/tests/test_core.py::test_test_dm_constant_is_owner_designated_dm PASSED
cli_anything/discord/tests/test_core.py::test_read_js_extracts_attachments PASSED
cli_anything/discord/tests/test_full_e2e.py::TestCLISubprocess::test_help PASSED
cli_anything/discord/tests/test_full_e2e.py::TestCLISubprocess::test_status_json
  status target: 851C77954A88BFA11B6B3EF420EB15E2 https://discord.com/channels/@me
PASSED
cli_anything/discord/tests/test_full_e2e.py::TestCLISubprocess::test_servers_list
  servers: 13
PASSED
cli_anything/discord/tests/test_full_e2e.py::TestCLISubprocess::test_channels_list_dm_contains_test_dm PASSED
cli_anything/discord/tests/test_full_e2e.py::TestCLISubprocess::test_channels_open_test_dm PASSED
cli_anything/discord/tests/test_full_e2e.py::TestCLISubprocess::test_messages_read_json_shape PASSED
cli_anything/discord/tests/test_full_e2e.py::TestCLISubprocess::test_session_show PASSED
cli_anything/discord/tests/test_full_e2e.py::TestLiveRead::test_read_returns_real_messages
  read 5 messages, newest id=1574781352874872916
PASSED
cli_anything/discord/tests/test_full_e2e.py::TestLiveRead::test_read_authors_and_timestamps_filled PASSED
cli_anything/discord/tests/test_full_e2e.py::TestLiveSend::test_send_returns_ok
  sent probe, will verify by read-back: [cli-anything-discord e2e e2e-20261124-2051-b7c10a] send-ok probe
PASSED
cli_anything/discord/tests/test_full_e2e.py::TestLiveSend::test_send_verified_by_readback
  read-back OK: message id=1574784672334880920 author='(owner account)'
PASSED
cli_anything/discord/tests/test_full_e2e.py::TestLiveSendFile::test_send_file_returns_ok
  send-file ok: /tmp/pytest-of-james/pytest-2/test_send_file_returns_ok0/discord-e2e-test.txt caption='[cli-anything-discord e2e e2e-20261124-2051-b7c10a] file upload'
PASSED
cli_anything/discord/tests/test_full_e2e.py::TestLiveSendFile::test_send_file_verified_by_readback_attachment
  attachment OK: message id=1574784744309268551 url=https://cdn.discordapp.com/attachments/865272264831139840/1574784744007147643/discord-e2e-attach.txt?ex=6b06e815&is=6b059695&hm=9edcebd8aa7784b96312f8ae777dfe601deadd0035f655584079e7af02acf45e&
PASSED
cli_anything/discord/tests/test_full_e2e.py::TestLiveSendFile::test_send_missing_file_fails_loudly PASSED
cli_anything/discord/tests/test_full_e2e.py::TestSessionRelaunch::test_quit_relaunch_attach_and_read
  Discord fully quit (CDP down, no Discord process)

  relaunched: launched=True target=3F35B522C61F59C46142820905CDF1AA

  post-relaunch read OK: 3 messages, newest id=1574784744309268551
PASSED

============================= 22 passed in 54.99s ==============================
```

### Summary Statistics

- Total: 22 tests (7 unit + 15 E2E), 22 passed, 0 failed, 0 skipped.
  (Plan said 16 E2E; the relaunch was implemented as 1 combined test
  instead of 2, so the actual E2E count is 15.)
- Pass rate: 100%. Execution time: 54.99s.
- Live evidence (all in the Violet Joestar test DM, channel
  865272264831139840): sent message id 1574784672334880920 (exact text
  read back); file message id 1574784744309268551 with attachment
  `https://cdn.discordapp.com/attachments/865272264831139840/1574784744007147643/discord-e2e-attach.txt?...`;
  relaunch `launched=True`, new target 3F35B522C61F59C46142820905CDF1AA,
  post-relaunch read OK.
- Run marker for this suite: `e2e-20261124-2051-b7c10a`. Worker 3's smoke
  traffic (messages 1574781159320199189, 1574781352874872916) is also in
  the same DM.

### Coverage Notes / Gaps

- Covered: session save/load + locking (unit), all read-only commands,
  send + read-back, send-file + attachment-URL read-back, missing-file
  failure, full quit + relaunch + attach + post-relaunch read, CDP-absent
  error messages (manual probe, not a pytest test: with Discord down,
  `session attach` and `messages read` name the opt-in fix).
- NOT covered: REPL interaction (only a piped smoke in Phase 3, no pytest
  test); `session stop` without `--force` (refusal path); `--limit` above
  the viewport with very old history (scroll-up loads at most 5 pages);
  guild-channel send (test DM only, by owner instruction); Discord
  self-update during a run (happened once live, 1.0.169 -> 1.0.170, and
  broke the relaunch; the retry path is manual, not automated).
- Known cosmetic issues (unchanged from Phase 3): `channels open` reports
  `channel_title: ""` in some DM views (session `current_channel_name`
  may be null or concatenated, e.g. "Violet Joestarvioletjoestar1154");
  server names carry locale unread-count prefixes.

