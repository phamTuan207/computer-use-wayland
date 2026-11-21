# Y13g verification log (independent verifier)

Worker: Y13g verifier (independent Muse subagent, depth 2). T0 (task
received): 2026-11-22 00:05 +07. Scope: ONLY the Y13g fix diff
(431b2a9..b815590, commits caa4a7c, 0cf43f8, 03303f4, 6cd0f7a,
b815590). No code modification to fix files. No live Zen driving.
No ydotool. No em/en dashes anywhere. Never touch /usr/lib or any
system path. All work staged under ~/workspace/y13g-verify/
(persistent); harnesses committed to improvements/y13g-verify/.
Log discipline: every event appended here as it happens,
wall-clock Asia/Ho_Chi_Minh + elapsed since T0.

## 1. Live event log

- 00:05 +07 (T+0m00s): task received. Re-verify the Y13g fix of
  Y13r2 BLOCK (B1-B4 + 5 amends). Rebuild all harnesses from the
  specs (old /tmp/y13r2* harnesses lost). Run A2 forge set, A6d
  stdlib map, A4 unit table + live probe, A3 brick sequence, A5
  suite, A7 symlink set, A8, AST comparison, clean ship + launcher
  dry run. Report to improvements/worker-y13g-verify-report.md.
- 00:05-00:12 +07 (T+0m to T+~7m): read sources in full. Redteam
  paper improvements/worker-y13r2-redteam.md (BLOCK, B1-B4 + 5
  amends), Y13r2 re-review log, Y13g fix log. Read the new runner
  module top (guard + narrow os.path-only scan, _SHIP_PY incl.
  codex-y5/check-dashes.py), _verify_manifest (__pycache__ dir
  rule, no per-file exemption), tokenizer block (real argv parse
  + md5 leg), _proven_no_body (is not None), launcher top
  (guard + scan + SHIP_DIR derivation), check_runner_quiet,
  _check_remote (KNOWN_REMOTE_URL pin), check_marker (log-order),
  check_manifest (planted refusal + md5 pin), _check_entry_pyc
  (out-of-process marshal compare), _scan_ship (full allowlist),
  main (exec python3 -P + PYTHONSAFEPATH=1).
- 00:12 +07 (T+~7m): pins verified against the task brief.
  Runner db3e357f616d21e1d6b2a573682019fd, launcher
  eec63492ae581b3046f2cc3baea97473, run_live
  84fa106c253d5e7f16daccf2ce3f14a5, manifest
  0ca16ddd743acc9e28294fecd07a9c70. All hold. Y13g commits
  confirmed as the only commits touching the 6 fix files in
  caa4a7c^..b815590. Python 3.12.3.
- 00:12 +07 (T+~7m): clean ship staged with the regen script:
  python3 tests/realistic/regen_codex_y5_manifest.py --stage
  ~/workspace/y13g-verify/ships/clean. Staged verify rc 0,
  manifest_ok true, 27 checked, 0 mismatches, md5 0ca16ddd.
  Regen rewrote the manifest file but git shows no diff (bytes
  identical to committed). No __pycache__ in the staged ship.
- 00:12-00:14 +07 (T+~7m to T+~9m): harnesses rebuilt under
  improvements/y13g-verify/: extract_lib.py (AST extraction, no
  import), forge_pyc.py (16-byte header forge, fake-OK form),
  launcher_check_driver.py (runs one extracted launcher check
  in a subprocess against a staged ship). Driver sanity on the
  clean ship: entry-pyc check OK rc 0, allowlist scan OK rc 0.
- 00:14 +07 (T+~9m): A2 forge set DONE, 11/11 PASS in 2.3s
  (results ~/workspace/y13g-verify/results/a2.log). Launcher
  _check_entry_pyc refuses every forged entry .pyc (run_codex_y5,
  fake-OK, launch_y13, run_live) rc 2, no marker, "entry .pyc
  mismatch" in output. Direct script form with fake-OK forge
  refuses rc 2 with {"refused": true, "kind": "pyc"}, no marker,
  no fake manifest_ok. Hole demos confirm the forges were live:
  direct -m on forged entry .pyc prints the marker (rc 2, guard
  fires after); direct -m on fake-OK prints marker + fake
  {"manifest_ok": true} rc 0 (the gate lies); direct import
  prints the marker; direct -m launch_y13 prints the marker.
  The in-process hole is real and unfixable in-process, as
  designed; the production control (launcher out-of-process
  check + never invoking -m/import on an unverified ship) holds
  on every form tested.
