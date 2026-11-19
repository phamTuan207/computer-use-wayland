# `vault move` subcommand: Obsidian note move with backlink updates

- Date: 2026-11-19, work 19:40 to 19:46 Asia/Ho_Chi_Minh. Worker: Luna 6 Max.
- Laptop: james@100.70.92.52 (Omarchy/Hyprland). Repo /home/james/computer-use-wayland,
  branch vault-move, from origin/speed-swarm 8727135 (the interim DOM commit).
- Task: implement the briefed `vault move` subcommand in the harness
  (`computer-use cli`) so the executor can move vault notes in 0 model
  calls instead of deliberating. Main stays FROZEN, no merge to main.

## What was built

- `computer-use cli run obsidian -- vault move <source> <destination>`
  now works. Both paths are vault-relative, e.g.
  `vault move "CU-Proof-B.md" "998- Unsorted/CU-Proof-B.md"`.
- Implementation: `scripts/cli-anything.py` intercepts `obsidian` +
  `vault move` in `cmd_run` (after the registry check, before the
  harness-binary check, so the move needs no binary) and performs the
  move itself through the same Local REST API the upstream harness
  wraps: HTTP MOVE on /vault/<per-segment URL-encoded source path>
  with a Destination header and Bearer auth from OBSIDIAN_API_KEY.
  Base URL defaults to https://127.0.0.1:27124, overridable with
  OBSIDIAN_API_URL. Stdlib only (urllib), TLS verification off for
  this loopback call, same as the upstream harness (verify=False).
  The plugin answers 204 and renames through
  app.fileManager.renameFile, the link-updating rename.
- Why this qualifies under the last-resort rule: upstream
  cli-anything-obsidian 1.1.1 has no move/rename command (vault group
  offers append, create, delete, list, read, update only), and the
  move is the one vault operation that needs the API. Plain mv leaves
  backlinks pointing at the old path; only the API updates them
  (proven 19/11, improvements/summary-vault-move-proof.md).
- Envelope shape is unchanged (app, args, returncode,
  stdout_truncated, stderr_truncated, plus result on success), so
  `computer-use cli` reports it like any other harness call. Usage
  errors (wrong arg count, empty path, source == destination) exit 2;
  missing OBSIDIAN_API_KEY exits 1 without touching the network;
  API errors exit 1 with the status in the message; unreachable
  server exits 1 with the upstream wording ("Cannot connect to
  Obsidian REST API at ...").
- Docs: `docs/cli-anything.md` gains a "Repo-owned extensions" section
  and `skill/references/cli-anything.md` a `vault move` subsection.
  The vendored skill doc (`skill/cli-anything/obsidian.md`) is
  upstream-verbatim and was NOT edited.
- Tests: `tests/test_obsidian_vault_move.py`, 10 tests, non-live
  (fake Local REST API on 127.0.0.1, ephemeral port). Proves the exact
  request (MOVE, per-segment encoding, Destination header, Bearer
  auth), usage/auth/API/server-down failures, that the move needs no
  harness binary, and that non-move obsidian commands still go
  through the binary. 10/10 pass in 0.711s.

## Test evidence (full suite, before vs after)

- Baseline, branch speed-swarm 8727135, 19:40 to 19:42 +07:
  1339 tests, FAILED (failures=7, skipped=2), 103.166s.
- After, branch vault-move (this work), 19:43 to 19:45 +07:
  1415 tests, FAILED (failures=10, skipped=2), 105.486s.
- FAIL set after = the 7 baseline failures PLUS 3 from another
  worker's new module: test_directory_exists_via_dir_backend,
  test_dom_without_backend_is_inconclusive,
  test_no_file_backend_is_inconclusive (all test_postcondition).
  Those 3 are NOT mine: the module (tests/test_postcondition.py
  plus scripts/postcondition.py) is untracked, landed 19:43:37 from
  another worker, imports nothing from cli-anything, and fails the
  same 3 deterministically on a standalone re-run (36 tests, 0.002s).
  Zero new failures in anything this change touches, zero new
  errors, and no obsidian_vault_move failure in the full run.
- FAIL set, the 7 pre-existing at 8727135, identical both runs:
  test_cli_list_includes_chromium;
  test_base_exception_from_probe_is_not_converted_to_ime_error,
  test_first_failure_skips_second_probe,
  test_long_crlf_probe_error_is_single_line_bounded,
  test_remote_success_keeps_schema,
  test_second_probe_failure_after_first_success (all
  test_session_driver.DoctorCliTests); and
  test_screen_refusal_keeps_session_then_fresh_act_succeeds
  (test_session_policy.RefusalFlow). All 7 are pre-existing at
  8727135 and untouched by this change (no file they cover was
  modified).
- Note: two more untracked files from another worker
  (scripts/det_finish.py, tests/test_det_finish.py, mtime 19:42:27
  and 19:42:33, still being edited at 19:46:05) appeared after the
  baseline run started; the post-change count of 1415 includes
  their tests plus mine (10) plus test_postcondition (36). The
  FAIL/ERROR set comparison above is unaffected: no det_finish test
  is in the FAIL set. All other-worker files left untouched.

## What was NOT done (open for the live-measure worker)

- NO live measurement, per the brief: the broker is SINGLE-OWNER and
  was busy with the R3 live run. Obsidian was not running (port
  27124 down) and was NOT launched, to avoid disturbing the R3 run.
- The live backlink check on a scratch vault (never his real vault)
  is still open. What the live-measure worker should run after R3:
  start Obsidian against a scratch vault, export OBSIDIAN_API_KEY,
  create a linking note plus a target note through the CLI, run
  `python3 scripts/cu.py cli run obsidian -- vault move <target>
  <new path>`, and verify the link text in the linking note changed
  to the new path while the moved note is byte-identical. The request
  this subcommand issues is the same MOVE request (method, encoded
  path, Destination header, Bearer auth) the 19/11 proof ran live
  against the real plugin, where a pure rename changed [[CU-Proof-H]]
  to [[CU-Proof-H2]] and a pathed folder move changed
  [[998- Unsorted/CU-Proof-F]] to [[CU-Proof-F]].
- No relay restart was needed: no broker code changed (only
  scripts/cli-anything.py, docs, and tests). The relay was not
  touched.
- No GUI was driven, no Zen tabs touched, no music touched. Desktop
  untouched (this work is files plus unit tests only).

## Wall times (WALL TIME is the headline number)

- New unit tests: 10 tests in 0.711s (0.720s on first run with 1
  failure, fixed expectation, re-run 10/10 in 0.711s; also 10/10
  inside the full post-change suite).
- Full suite baseline: 1339 tests, 103.166s, 7 failures. Full suite
  after: 1415 tests, 105.486s, 10 failures (7 pre-existing + 3
  other-worker postcondition, see above).
- The MOVE call itself was measured at 0.008s to 0.023s in the 19/11
  proof; the harness call around it is about 0.31s per CLI call.
  No live wall time is claimed for the subcommand until the
  live-measure worker runs it.

## Commits

- Branch vault-move, from origin/speed-swarm 8727135. Commits pushed,
  verified with git ls-remote (see report). Main stays FROZEN.
