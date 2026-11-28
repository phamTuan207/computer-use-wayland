# Deterministic finish: implementation report (Track 2, 19/11)

- Owner: the repository owner. Worker: Luna 6 Max (implementation).
- Branch: `det-finish`, from `origin/speed-swarm` 8727135 (DOM-first interim commit).
- Worktree (19:45 coordinator order, shared main checkout churning):
  `~/computer-use-wayland-detfinish`, branch `det-finish`, HEAD
  e01399d. All further work happens ONLY in the worktree; the main
  checkout is never touched again. The coordinator's urgent message named
  another worker's files (vault-move branch, scripts/cli-anything.py,
  tests/test_obsidian_vault_move.py); those are NOT this worker's files
  and were NOT moved or committed here. This worker's own 4 files were
  moved via stash + copy (tracked diffs verified before/after), committed
  as e01399d, pushed, ls-remote verified. VM backups of all 4 files:
  ~/workspace/det-finish-draft/backup-laptop/.
- Date: 2026-11-19 Asia/Ho_Chi_Minh.
- Status: IMPLEMENTED, unit-tested, committed, pushed. NOT live-measured yet.
  A live-measure worker tests it on the broker after the R3 live run.

## Problem (from improvements/overhead-analysis.md, Fix 1)

Executor close/finish think is 14 to 104s per task (Pick 4 arm means 35.8
and 40.1s), excluded from every headline loop wall. After the verify
observation the end state is already proven; the gap is pure post-task
deliberation plus in-session summary composition. It is the biggest
recurring chunk that is not task work at all.

## What was built

### 1. `scripts/det_finish.py` (new, canonical)

One shell call the executor makes immediately after the verify request
returns success, replacing the deliberated finish + in-session summary.
No model call between verify and finish. The script does, all scripted:

1. Scripted close-out checklist: broker `status` via `session_remote.py`,
   plus a best-effort `hyprctl clients` count (never fatal, `--skip-hyprctl`
   for offline use). The checks the analysis required are kept; only the
   model deliberation is removed.
2. Broker `finish` via `session_remote.py`, waiting for
   finished/stopped/clean (same 135s timeout as `timed.py`).
3. Offline summary from `records.jsonl` in the run dir: loop wall (first
   start submit to last verify result), broker service total, startup,
   request counts by kind, image bytes, and the verify-to-finish gap
   (det-finish submit minus verify result wall). Written to
   `det-finish-<task-id>.json` plus a fixed-format block in `summary.md`
   (marker-delimited, replaced on re-run for the same task, never duplicated).
4. Appends its own `det-finish` record to `records.jsonl` (with the same
   newline guard as `timed.py`, so a killed writer can never glue two JSON
   objects onto one line).
5. Prints exactly one JSON line on stdout; exit 0 only on
   finished/stopped/clean, exit 1 on a failed finish (summary still
   written, marked FINISH-FAILED), exit 2 on bad arguments (nothing
   touched, broker never called).

The verify evidence is a short pointer (observation id, image path, or
file sha), capped at 500 chars, never a composed paragraph. A task that
never verified finishes through the SAME path with evidence
`BLOCKED:<short reason>`; the summary records it as BLOCKED. There is no
fallback to a deliberated finish.

### 2. `improvements/pick2-executor-brief.md` (measurement instrument)

- Finish line replaced: `timed.py finish` is now forbidden; the NEXT shell
  command after a successful verify is the det_finish.py call (DECIDE line
  + script in one shell command, so no deliberation gap can creep in).
- New `## Deterministic finish` section: the mechanical 4-step rule,
  including the floor probe (task id `floor`).
- Reporting bullets updated: per-task summaries are written by the script,
  not the executor; the run-level summary is APPENDED, never a FRESH
  rewrite (the det-finish blocks are the per-task record). The 30-minute
  rule finishes via det_finish.py with `BLOCKED:<cause>`.

### 3. `scripts/mcp_bridge.py` (one sentence)

Tool description for `computer_use_session` now says: after a verified
end state, call finish immediately with no further deliberation or summary
composition; the summary is written offline from the session records.
This carries the rule to MCP-based executors too. `tc02_controller.py`
needed no change: S6 already calls finish directly in code after byte
verification.

### 4. `tests/test_det_finish.py` (new, 11 tests, offline)

Stub `session_remote.py` answers status/finish; synthetic records.jsonl
stands in for a run dir. No broker, no GUI. Covers: happy path (exact
loop wall 36.5s, service total, counts, image bytes, one stdout JSON
line, summary.md block, records append, stub saw status+finish); failed
finish (exit 1, summary still written, FINISH-FAILED); invalid task id /
empty / oversize evidence / missing lease (exit 2, broker never called);
missing records file (null timings, still finishes); truncated last line
(counted, not fatal); unterminated last line (append never glues);
second run replaces the summary block; hyprctl path non-fatal; BLOCKED
evidence (task_outcome BLOCKED, reason recorded).

## Expected saving

- Per task: the whole finish think, typically 30-40s (Pick 4 means),
  floor ~14s, worst case 100s+ (D1 finish 139.2s). The scripted finish
  call itself costs ~1s of broker service (the `_client_finish` poll
  loop), same as `timed.py finish` cost before.
- Per 4-task run: roughly 120-160s of span time.
- This moves the analyzer span / executor-summary wall (the real elapsed
  time), NOT the headline loop wall (which already excludes finish).
  Report it as span saving, not loop-wall saving.
- What to measure live: per-task `verify_to_finish_s` from
  `det-finish-<task-id>.json` (the residual gap between the verify result
  and the script submit; should be seconds of shell, not 30-40s of
  think), plus the analyzer finish split, which should be ~0 model think.

## Test evidence

- Baseline at 8727135 (before changes): `python3 -m unittest discover -s
  tests -p 'test_*.py'` => Ran 1339 tests, FAILED (failures=7, skipped=2).
  FAIL set: test_chromium_cli.CuCliWiringTests.test_cli_list_includes_chromium;
  test_session_driver.DoctorCliTests x5 (test_base_exception_from_probe_is_not_converted_to_ime_error,
  test_first_failure_skips_second_probe,
  test_long_crlf_probe_error_is_single_line_bounded,
  test_remote_success_keeps_schema,
  test_second_probe_failure_after_first_success);
  test_session_policy.RefusalFlow.test_screen_refusal_keeps_session_then_fresh_act_succeeds.
  (Full log: /tmp/det-finish-baseline-tests.log on the laptop.)
- After changes (first pass, before BLOCKED path): Ran 1359 tests,
  FAILED (failures=8, skipped=2). The 7 baseline failures are identical.
  The 8th is test_obsidian_vault_move.ObsidianVaultMoveTest.test_move_missing_api_key,
  from another worker's untracked file tests/test_obsidian_vault_move.py
  (mtime 2026-11-19 19:43 +07, created after the baseline run; not this
  worker's file, not touched). Zero failures in test_det_finish (10/10)
  or test_mcp_bridge. The +20 test count vs baseline is 10 det_finish +
  10 from that other worker's file. (Full log:
  /tmp/det-finish-after-tests.log on the laptop.)
- After BLOCKED path added: `python3 -m unittest tests.test_det_finish
  tests.test_mcp_bridge` => Ran 87 tests, OK (11 det_finish + 76 mcp_bridge).
- Final full suite, clean worktree `~/computer-use-wayland-detfinish`
  at e01399d, native helpers built with scripts/build.py (pointer,
  indicator, modifiers, wtype): Ran 1350 tests, FAILED (failures=7,
  errors=1, skipped=2). The 7 failures are IDENTICAL to the baseline 7.
  Zero new failures. The 1 error is
  test_cursor_theme.GuardProtocol.test_wrong_token_oversize_framing_and_drop_all_fail_closed
  (BrokenPipeError in cursor_theme.py socket sendall): it passes standalone
  twice in a row (33 tests OK, twice), so it is a flaky/order-dependent
  race, not caused by this change (this change does not touch cursor
  theme). Test count 1350 vs baseline 1339: +11 new det_finish tests,
  other workers' untracked test files absent from the clean worktree.
  (Full log: /tmp/det-finish-worktree2-tests.log on the laptop.)
- NOTE: an earlier worktree run without the built natives gave 66 errors
  (missing native/wtype helper + ungenerated keyboard-protocol.c); building
  with scripts/build.py cleared all of them, including the 2
  FullRestoreEnvelope failures, which were downstream of the missing
  helper. The earlier /tmp/det-finish-final-tests.log run (main checkout)
  is INVALID as evidence: the shared checkout switched branches
  (det-finish to harness-prefetch to detached HEAD) and other workers
  edited the tree mid-run. Discard it; the worktree2 run above is the
  comparison.

## Deliberately NOT changed

- `scripts/session_remote.py` broker semantics untouched (no new broker
  command; det_finish.py is a client-side wrapper around the existing
  status/finish calls). The broker is single-owner and busy with R3; no
  relay restart needed because no broker code changed.
- `scripts/timed.py` untouched (per-run copies; the live-measure worker
  uses det_finish.py directly, not through timed.py).
- Main stays FROZEN; work is on branch `det-finish` only.
- No live measurement in this task (per brief): no broker session started,
  no desktop touched, no Zen tabs / Jarvis / music touched.
- Other workers' uncommitted/untracked files left untouched
  (scripts/cli-anything.py, scripts/postcondition.py,
  scripts/procedure_library.py, tests/test_obsidian_vault_move.py).

## Live-measure handoff (for the next worker)

- Branch `det-finish`, HEAD e01399d (e01399d67b35fc1c78afca28b0e623e4907731e0),
  pushed, verified with `git ls-remote`.
- Executor brief to use: `improvements/pick2-executor-brief.md` on this
  branch (deterministic finish section). Same 4 held-out tasks as the
  profile run, fresh dated run dir, floor probe per arm.
- Measure alone, never stacked with another lever. Record per task, side
  by side: loop wall (start to verify) AND span (first submit to last
  result, including finish) AND the finish gap as its own column
  (`verify_to_finish_s` from det-finish-*.json + analyzer finish split).
- Success bar: finish think ~0 (verify-to-finish gap seconds, not 30-40s)
  on every task, summaries present in summary.md from the script, sessions
  finished/stopped/clean, zero new unit failures.

## Bai hoc

(Danh cho the owner, viet bang tieng Viet don gian.)

- Doan nghi sau verify la doan de cat nhat vi ket qua da co trong tay roi.
  Bai hoc: cai gi da biet chac thi finish ngay bang script, viet bao cao
  sau tu records, dung de model ngoi nghi ve thu da xong.
- Finish cu ton 30-40s moi task ma khong ai ghi vao wall. Bai hoc: muon
  biet task that su ton bao lau thi phai do ca doan sau verify.
