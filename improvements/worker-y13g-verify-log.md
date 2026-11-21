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
- 00:14 +07 (T+~9m): commit d76daba pushed (harness rebuild +
  A2, 5 files), ls-remote matches d76daba.
- 00:14-00:15 +07 (T+~9m to T+~10m): A6d stdlib map DONE, 18/18
  PASS in 2.0s (results a6d.log). All 15 names (enum, re, json,
  socket, subprocess, hashlib, datetime, pathlib, copyreg,
  functools, collections, os, warnings, typing, sre_compile)
  refused rc 2 with {"refused": true, "kind": "planted-py"},
  marker never printed, via `python3 -P run_codex_y5.py
  --verify-manifest`. Extra no-P spot checks (re, json, enum)
  also refuse rc 2, marker never printed: the module-top scan
  protects even the non-P path. Shims never delete any file.
- 00:15 +07 (T+~10m): A4 unit table DONE, 39/39 PASS in 0.1s
  (results a4_unit.log). Both copies agree on every case; all
  -m forms, flag-value forms, renamed/symlinked copies (md5
  leg, real /tmp/mycopy.py + /tmp/link.py fixtures), -c exec
  caught; -c import, echo/grep mentions, md5sum mention, and
  the invalid -m .py form correctly NOT caught.
- 00:17-00:21 +07 (T+~12m to T+~16m): A4 live probe DONE, 6/6
  PASS in 106.8s over two runs (results a4_live.log +
  a4_live2.log). First run's echo case was VACUOUS (bash
  exec-replaced itself with the trailing `sleep 60`, so the
  process under test was `sleep 60`, not bash); fixed with a
  trailing `read x` builtin on a held-open pipe, re-ran the
  whole probe. Second run: baseline had 3 fleet-probe offenders
  (pids 19080/19089/19097, other workers), per-case verdicts
  keyed on the dummy pid being named. Bare, -m, renamed,
  symlink dummies all refused rc 2 with the dummy pid named;
  the echo-mention bash (cmdline verified `bash -c echo
  python3 run_codex_y5.py; read x`) was NOT flagged, rc 0.
  Warnings 0 on every case (no misleading "codex" warning on
  runner cmdlines; Amend 2 works). Note: each driver run takes
  12-23s on this loaded VM (full /proc scan); slow, not a
  failure. Dummies used an argv-ignoring C sleeper (gcc -O2,
  improvements/y13g-verify/sleeper.c).
- 00:22-00:23 +07 (T+~17m to T+~18m): A3 brick sequence DONE,
  7/7 PASS in 1.4s (results a3.log). (a) -m on a clean ship exits
  2 via the guard ("run as a script..."), no .pyc left behind.
  (b) Direct verify after is rc 0, manifest_ok true. (c)
  Live-run attempt `python3 -P run_codex_y5.py all` prints
  MANIFEST OK, then fails rc 2 at the served-files check with
  all 27 files 404: the server root defaults to the production
  path, not the staged ship dir (harness artifact, not a
  runner defect). (c2, added after manual confirmation) With
  LIVE_SERVER_ROOT pointed at the staged ship it reaches
  SERVED FILES OK (27 files over HTTP) then PREFLIGHT FAILED
  "LIVE_OWNER_AWAY is not 1", rc 2, no driving. (d) Empty
  __pycache__ dir alone, direct verify rc 0. (e)
  PYTHONDONTWRITEBYTECODE=1 -m writes nothing (no __pycache__
  created). (f) Forged non-entry run_live .pyc refuses rc 2,
  no marker, kind pyc.
- 00:27-00:28 +07 (T+~22m to T+~23m): A5 marker + remote-URL
  suite DONE, 10/10 PASS in 9.3s (results a5.log). Setup:
  synthetic bare repo + clone under ~/workspace/y13g-verify/a5/
  (never the real repo). Driver bug found and fixed first:
  launcher_check_driver.py required --ship-dir even for marker
  checks (it printed its own docstring, rc 2); --ship-dir now
  defaults to the repo dir. Marker logic runs with a git
  test-double (a5/bin/git) that intercepts only `git remote
  get-url origin` (returns the known URL) and `git fetch origin
  todolist-push` (real fetch from the local bare, explicit
  refspec); all other git calls pass through to real git. The
  pin itself is verified with REAL git (case 6 + real-repo
  control). Results: case 1 fake completion PASSES BY DESIGN
  (subject spoof, documented limitation, not a pass); 3a
  old-date completion vs newer abort refuses; 3b forged
  FUTURE-date completion (2026-11-23 %ct) older in log position
  than a genuine abort (2026-11-22 %ct) refuses via log-order
  (state log confirms position order: abort first despite the
  older %ct; old %ct code would have passed this); C1
  completion newer than abort passes; C2 harness subject
  refuses; C3 body-DONE under "Fix flake" refuses; C4
  completion on the wrong path refuses; case 6 attacker repo
  refuses on the remote URL in BOTH check_marker and
  check_manifest (exact message: "git remote origin is
  .../a5/attacker.git, not the known repo
  https://github.com/phamTuan207/computer-use-wayland.git;
  refusing (attacker fork?)"); real-repo control: pin passes
  with real git, refuses "no Y6c completion marker on
  todolist-push" (real state, as expected).
