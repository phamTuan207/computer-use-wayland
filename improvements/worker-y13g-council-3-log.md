# Y13g Council 3 log (operator view)

Council 3 reviewer, Muse subagent. T0 (task received): 2026-11-22 00:05 +07.
Scope: operability of the Y13g fix diff ONLY (431b2a9..HEAD, 6 files).
No live Zen driving. No ydotool. No em/en dashes. Work only in the
repo worktree and ~/workspace scratch.

## Live event log

- 00:05 +07 (T+0m): task received. Read Y13g fix log first, then the
  redteam paper, then the 6-file diff stat (+1413/-259).
- 00:06 +07 (T+1m): read SHIPPED.md, regen script, manifest in full.
  Noted: SHIPPED.md has no --ship-dir mention; launch command uses
  --repo /home/james/workspace/computer-use-wayland.
- 00:07 +07 (T+2m): read plan Y13g amendments section + Y13f section
  it supersedes. Noted B3 -m list includes hyphenated names.
- 00:08 +07 (T+3m): read runner top (guard/scan) + launcher top
  (derive/guard/scan) in full. Noted runner docstring launch lines
  lack -P while the SCRIPT FORM ONLY block demands it.
- 00:09 +07 (T+4m): read _verify_manifest + check_marker /
  check_manifest / _check_entry_pyc / _scan_ship / main in full.
  Noted: check_manifest md5 refusal says "re-stage from the
  committed bytes" though regen stages working-tree bytes.
- 00:10 +07 (T+5m): read tokenizer block in full (both copies).
  Noted _runner_md5s reads the manifest from _SHIP_DIR.
- 00:11 +07 (T+6m): AST comparison of the shared tokenizer block:
  all 12 functions + 4 constants identical ignoring docstrings;
  _is_runner_cmdline differs only in its docstring (sync note).
  Claim "AST-verified identical" HOLDS. Scratch dir created at
  ~/workspace/y13g-council3-scratch/.
- 00:12 +07 (T+7m): PROBES P1-P4 on scratch staged ships (regen
  --stage exit 0, md5 0ca16ddd, verify rc 0; -m exits 2 + clear
  message + no .pyc left + direct verify after rc 0; empty
  __pycache__ rc 0; nested codex-y5/__pycache__ .pyc refuses rc 2
  with kind pyc, no recovery hint). py_compile OK on all 3 files.
- 00:13 +07 (T+8m): PROBE P9: `import run_live` in a ship copy
  writes run_live.cpython-312.pyc; direct verify then refuses rc
  2 and the guard does NOT delete it (runner guard covers 2
  stems, launcher covers 3). PROBE P5: launcher by its repo-tree
  path refuses "tampered ship dir .../tests/realistic" (derivation
  picks the repo tree).
- 00:14 +07 (T+9m): PROBES P6-P8: --ship-dir to a staged ship
  reaches the go-order gate (clear message); --ship-dir to a
  nonexistent dir gives a misleading "run this launcher from the
  ship dir"; dangling --ship-dir eats the next arg ("all" becomes
  SHIP_DIR). PROBE P10: Y13_GO=1 + staged ship reaches the marker
  gate, refuses "no Y6c completion marker", exit 2 (expected:
  Y6c has no completion marker). Remote origin matches the pin.
  Regen --stage a second time: same md5 0ca16ddd (deterministic).
  6 files clean in git status.
- 00:15 +07 (T+10m): _proven_no_body Amend 5 confirmed in code
  (`is not None`, line 1081). Handover-token writer claim checked:
  no code in launch_y13.py writes TOKEN_PATH (read-only
  check_token); SHIPPED.md + plan + runner comment all claim the
  launcher writes it. --repo paths disagree (launcher docstring
  ~/computer-use-wayland vs SHIPPED.md
  /home/james/workspace/computer-use-wayland).
- 00:16 +07 (T+11m): verdict paper written:
  improvements/worker-y13g-council-3.md, verdict AMEND, findings
  C3-1..C3-11 + 10 verified holds. Dash sweep: 0 em/en dashes in
  both files. Committing now.
