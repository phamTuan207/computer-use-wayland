# Y13g Council 1 (design/consistency) log

Council 1, design/consistency voice. T0 (task received):
2026-11-22 00:05 +07. Scope: review the Y13g fix diff ONLY
(431b2a9..HEAD, 6 files) for design coherence and consistency.
No live Zen driving. No ydotool. No em/en dashes. Work only in
the repo worktree and /tmp scratch.

## Live event log

- 00:05 +07 (T+0m00s): task received. Read
  improvements/worker-y13g-fix-log.md in full (design
  adjudication: Design C strict scan + guard cleanup, real
  python-argv parse + md5, -P + top scan, remote pin +
  log-order marker). Branch todolist-push, HEAD f7384a3 at
  start (other workers' commits interleaved; Y13g commits
  caa4a7c, 0cf43f8, 03303f4, 6cd0f7a, b815590).
- 00:06 +07 (T+1m): diff stat for the 6 files: +1413/-259.
  Read the regen/SHIPPED/manifest/plan diffs in full.
  Manifest md5 0ca16ddd743acc9e28294fecd07a9c70, 27 files.
- 00:07 +07 (T+2m): read runner module top (lines 1-280):
  guard + narrow scan + _SHIP_PY incl. check-dashes.py.
  Read _verify_manifest (545-660) and _proven_no_body
  (1062-1082, `is not None` confirmed, Amend 5 in code).
- 00:08 +07 (T+3m): read launcher in full (1-1141):
  module-top guard + scan, _derive_ship_dir, _check_remote,
  check_marker (log order), check_manifest, _check_entry_pyc,
  _scan_ship, main() order (check_marker, check_manifest,
  _check_entry_pyc, _scan_ship). KEY OBSERVATION recorded:
  main() calls check_manifest BEFORE _check_entry_pyc, and
  both the module-top scan and check_manifest refuse ANY
  .pyc, so _check_entry_pyc cannot see a pre-existing .pyc.
- 00:10 +07 (T+5m): AST comparison of the tokenizer block
  (17 shared names, docstrings stripped): ALL SAME between
  runner and launcher. Text diff of the block: ONLY the
  sync-direction notes differ, plus the runner CODEX comment
  carries two extra sentences the launcher lacks.
- 00:12 +07 (T+7m): behavioral probes on the AST-extracted
  tokenizer (runner copy): -P/-m/-c exec/import cases all
  correct; MISSES confirmed: `python3 -uc
  exec(open('run_codex_y5.py').read())` False (want True),
  `python3 -um pkg.run_codex_y5` False (want True),
  `python3 -Bum pkg.run_codex_y5` False (want True),
  `python3 -Bc exec(...)` False (want True),
  `python3 -c os.system('python3 run_codex_y5.py')` False.
  The os.system miss CONFIRMS the plan doc LIMIT and
  CONTRADICTS the _c_code_executes_runner docstring claim
  that os.system-nested python "is caught by the same
  recursive parse" (shlex keeps os.system('...') as one
  token). `python3 -c "python3 run_codex_y5.py"` False is
  CORRECT (that -c string is a Python SyntaxError, never
  an execution); my first probe expectation for it was
  wrong, corrected here.
- 00:13 +07 (T+8m): md5 verification: runner db3e357f,
  launcher eec63492, manifest file 0ca16ddd, all match the
  manifest and SHIPPED.md; all 27 manifest entries listed
  in SHIPPED.md with matching md5s. Working-tree
  run_live.py differs from the manifest pin 84fa106c by
  design (frozen 1e3901c bytes; regen hashes the pinned
  commit, confirmed in regen_codex_y5_manifest.py).
  SHIPPED.md has NO mention of the nested -c / os.system
  limit ("nested" hit is Y6c Wayland-nested only).
- 00:14 +07 (T+9m): remaining checks: _is_codex_process
  defined in the runner (3999) but NEVER called there,
  and the runner preflight has no codex warning branch
  despite its comment saying a plain codex process "only
  warns"; runner docstring Usage lines 103/105 show
  `python3 launch_y13.py` WITHOUT -P while SHIPPED.md,
  the launcher docstring, the regen docstring, and the
  runner's own SCRIPT FORM ONLY block all require -P;
  no em/en dashes anywhere in the fix diff; no
  pyc_refused key left in code (plan doc mentions it only
  as the old key name).
- 00:15 +07 (T+10m): verdict settled: AMEND. No
  BLOCK-grade hole (every .pyc refusal is fail-closed;
  the tokenizer gaps are narrow and backstopped by ports
  + flock). Findings: F1 _check_entry_pyc unreachable
  for pre-existing .pyc (docs present it as the operative
  control); F2 guard stem asymmetry 2 vs 3 (run_live
  .pyc unhealed in the runner path); F3 bundled -c/-m
  tokenizer miss vs "bundled forms" doc claim; F4 -c
  os.system docstring contradicts the plan limit and
  SHIPPED.md omits the limit; F5 _proven_no_body
  docstring stale first paragraph; F6 runner Usage lines
  lack -P; F7 plan B2 overstates check_manifest; F8
  runner preflight codex-warning comment vs no warning
  branch, dead _is_codex_process in runner; F9 scan JSON
  vs plain text (Amend 3 unscoped); F10 CODEX comment
  drift in the "identical" block (trivial). Writing the
  verdict paper now.
- 00:17 +07 (T+12m): verdict paper
  improvements/worker-y13g-council-1.md written; this log
  written. Committing both, verifying via ls-remote.
- 00:19 +07 (T+14m): DONE. Log commit 8b520ba and verdict
  commit 6e9544f both pushed, ls-remote confirms
  6e9544f4d4a670f90451949053f93ea4be315a55 on
  todolist-push. Verdict AMEND, 10 findings (F1-F10).
  Report delivered to parent.
