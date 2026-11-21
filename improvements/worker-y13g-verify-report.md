# Independent verification report: Y13g fix of Y13r2 BLOCK (Y13r3 re-review)

- Verifier: independent Muse subagent (depth 2). Did NOT write the fix.
- Date: 2026-11-22, work 00:05 to 00:31 +07.
- Repo: ~/workspace/computer-use-wayland, branch todolist-push.
- Fix under test: Y13g commits caa4a7c, 0cf43f8, 03303f4, 6cd0f7a,
  b815590 (fix diff 431b2a9..b815590, 6 files).
- Scope: ONLY the Y13g fix diff. No fix file was edited. No live
  Zen driving. No ydotool. No em/en dashes. Never touched /usr/lib
  or any system path.
- Running log: improvements/worker-y13g-verify-log.md.
- Harnesses: improvements/y13g-verify/ (committed; rebuilt from
  scratch because /tmp/y13r2/ and /tmp/y13r2-redteam/ vanished).
  Staged ships and result logs: ~/workspace/y13g-verify/.

## Verdict: PASS

Every re-test battery passes. All four Y13r2 blockers are fixed
and re-verified mechanically; all five amends hold. Two known
limitations are documented below (the in-process -m/import hole,
which is unfixable by design and controlled out-of-process, and
the subject-only marker, which passes a fake completion by
design). Neither is a fix failure: both are the documented
design, and the controls that contain them are verified live.

## Pins verified first

| file | md5 | brief pin | holds |
|---|---|---|---|
| tests/realistic/run_codex_y5.py | db3e357f616d21e1d6b2a573682019fd | db3e357f... | yes |
| tests/realistic/launch_y13.py | eec63492ae581b3046f2cc3baea97473 | eec63492... | yes |
| tests/realistic/run_live.py | 84fa106c253d5e7f16daccf2ce3f14a5 | 84fa106c... | yes |
| tests/realistic/codex-y5-manifest.json | 0ca16ddd743acc9e28294fecd07a9c70 | 0ca16ddd... | yes |

Y13g commits confirmed as the only commits touching the 6 fix
files in caa4a7c^..b815590. Python 3.12.3. Clean ship staged
with the regen script: verify rc 0, manifest_ok true, 27
checked, 0 mismatches, md5 0ca16ddd; regen rewrote the manifest
file but git shows no diff (bytes identical to committed).

## Method notes (harness rebuild)

- Importing run_codex_y5.py or launch_y13.py exits 2 (the
  script-form-only guard), so tokenizer/check functions were
  AST-extracted (extract_lib.py: parse, take the named
  FunctionDef/Assign nodes, exec in a fresh namespace with
  os/json/hashlib/re/shlex/subprocess/time/marshal and _SHIP_DIR
  set to the staged ship). The modules were never imported.
- Ships were staged fresh from the committed bytes with
  `python3 tests/realistic/regen_codex_y5_manifest.py --stage
  <dir>` and tampered only in the staged copy, never the repo
  tree. Forged .pyc files were built by forge_pyc.py (16-byte
  header: magic + flags 0 + mtime + size from the real source
  stat; code compiled from the source plus an injected marker
  print, or plus a fake-OK verify JSON + exit 0).
- Launcher checks were run out-of-process through
  launcher_check_driver.py, which AST-extracts one check from
  the committed launcher and calls it with SHIP_DIR pointed at
  the staged ship. A POISON-MARKER in that driver's output would
  prove the check itself executed ship code; none ever appeared.
- Every test is timed and logged (wall-clock Asia/Ho_Chi_Minh
  + elapsed). Result logs live at ~/workspace/y13g-verify/results/.

## Per-battery results (132 checks total)

### A2 forge set: 11/11 PASS (results/a2.log, 2.3s)

| case | command (abridged) | rc | outcome |
|---|---|---|---|
| A2a launcher-check forged run_codex_y5 entry .pyc | launcher_check_driver.py --check entry-pyc | 2 | PASS, no marker, "entry .pyc mismatch" |
| A2a-hole direct -m on forged ship | python3 -m run_codex_y5 --verify-manifest | 2 | marker printed (known hole, see below) |
| A2b launcher-check fake-OK forge | launcher_check_driver.py --check entry-pyc | 2 | PASS, no marker, no fake manifest_ok |
| A2b-hole direct -m fake-OK | python3 -m run_codex_y5 --verify-manifest | 0 | marker + fake {"manifest_ok": true} printed (known hole) |
| A2c launcher-check forged entry (import form) | launcher_check_driver.py --check entry-pyc | 2 | PASS, no marker |
| A2c-hole direct import | python3 -c "import run_codex_y5" | 2 | marker printed (known hole) |
| A2d direct script form fake-OK forge | python3 -P run_codex_y5.py --verify-manifest | 2 | PASS, {"refused": true, "kind": "pyc"}, no marker, no fake manifest_ok |
| A2e launcher-check forged launch_y13 entry .pyc | launcher_check_driver.py --check entry-pyc | 2 | PASS, no marker |
| A2e-hole direct -m launch_y13 | python3 -m launch_y13 --help | 2 | marker printed (known hole) |
| A2f A1-control forged run_live .pyc, direct form | python3 -P run_codex_y5.py --verify-manifest | 2 | PASS, kind pyc, no marker |
| A2g A1-control forged run_live .pyc, launcher check | launcher_check_driver.py --check entry-pyc | 2 | PASS, no marker |

The hole demos prove the forges were live (the marker is the
first statement of the forged code). A forged entry .pyc
invoked directly via -m/import executes in-process; that is the
documented unfixable hole, and the production control (the
launcher's out-of-process marshal comparison + never invoking
-m/import on an unverified ship) refuses every form tested.

### A6d stdlib map: 18/18 PASS (results/a6d.log, 2.0s)

All 15 names planted as a top-level .py in a fresh staged ship
(marker print first, then a delegating shim that never deletes
any file), run as `python3 -P run_codex_y5.py
--verify-manifest`. Every name: rc 2, marker never printed,
`{"refused": true, "kind": "planted-py", "files": ["<name>.py"]}`.

enum, re, json, socket, subprocess, hashlib, datetime, pathlib,
copyreg, functools, collections, os, warnings, typing,
sre_compile: 15/15. Extra no-P spot checks (re, json, enum)
also refuse rc 2 with no marker: the module-top scan protects
even the non-P path. (Pre-loaded vs never-imported distinctions
are moot under the fix: the scan refuses before any import.)

### A4 unit table: 39/39 PASS (results/a4_unit.log, 0.1s)

_is_runner_cmdline AST-extracted from BOTH copies; the two
copies agree on every case. All -m forms, flag-value forms
(-W, -X, --check-hash-based-pycs), -c exec(open(...)),
renamed copy (real /tmp/mycopy.py) and symlinked copy (real
/tmp/link.py, md5 leg) caught. Mere mentions NOT caught:
-c import, bash -c echo/grep, md5sum, and the invalid
`python3 -m run_codex_y5.py` form. Full table (True=CAUGHT):

bare-relative True, absolute True, -m run_codex_y5 True,
-m run_live True, -m pkg.run_codex_y5 True,
-m run_codex_y5 --verify-manifest True, -u True, -W ignore True,
-X dev True, -X faulthandler True, --check-hash-based-pycs
always True, -c import False, -c exec(open(...)) True,
env VAR=1 True, nohup True, setsid True, /usr/bin/python3 True,
./ True, ../ship True, python3.12 True, python True, no-ext
True, run-nested-pill.py True, bash run-nested-wayland.sh True,
sh -c True, bash -c exec True, bash -c echo False,
bash -c grep False, flock -c True, flock direct True,
md5sum False, renamed copy True, symlink True, timeout True,
run_live.py True, hand_drive_e1.py True, ./ shebang True,
-I True, -m run_codex_y5.py (invalid) False.

### A4 live probe: 6/6 PASS (results/a4_live2.log, 106.8s)

Real dummy processes (an argv-ignoring C sleeper, so /proc
cmdline is exactly the target argv) plus the real launcher
check_runner_quiet via the driver, one case at a time.
Baseline had 3 fleet-probe offenders on the second run (other
workers); verdicts key on the dummy pid being named.

| case | dummy pid named | driver rc | outcome |
|---|---|---|---|
| bare python3 run_codex_y5.py | yes (19312) | 2 | PASS |
| python3 -m run_codex_y5 | yes (19463) | 2 | PASS |
| renamed python3 /tmp/mycopy.py | yes (19642) | 2 | PASS |
| symlink python3 /tmp/link.py | yes (19742) | 2 | PASS |
| bash -c "echo python3 run_codex_y5.py; read x" | no (19868) | 0 | PASS, not flagged |

Warnings 0 on every case (no misleading "codex" warning on
runner cmdlines; Amend 2 works). First run's echo case was
VACUOUS (bash exec-replaced itself with the trailing
`sleep 60`, so the process under test was `sleep 60`, not
bash); fixed with a trailing `read x` builtin on a held-open
pipe and the whole probe re-run. Note: each driver run takes
12-23s on this loaded VM (full /proc scan); slow, not a
failure.

### A3 brick sequence: 7/7 PASS (results/a3.log, 1.4s)

| case | command | rc | outcome |
|---|---|---|---|
| (a) -m on clean ship | python3 -m run_codex_y5 --verify-manifest | 2 | PASS, guard message, no .pyc left behind |
| (b) direct verify after (a) | python3 -P run_codex_y5.py --verify-manifest | 0 | PASS, manifest_ok true |
| (c) live-run attempt | python3 -P run_codex_y5.py all | 2 | PASS, MANIFEST OK printed, fails later (see note) |
| (c2) live-run with LIVE_SERVER_ROOT=ship | python3 -P run_codex_y5.py all | 2 | PASS, SERVED FILES OK then PREFLIGHT FAILED "LIVE_OWNER_AWAY is not 1", no driving |
| (d) empty __pycache__ alone | python3 -P run_codex_y5.py --verify-manifest | 0 | PASS, manifest_ok true |
| (e) env-guarded -m | PYTHONDONTWRITEBYTECODE=1 python3 -m run_codex_y5 --verify-manifest | 2 | PASS, no __pycache__ created |
| (f) forged non-entry run_live .pyc | python3 -P run_codex_y5.py --verify-manifest | 2 | PASS, kind pyc, no marker |

Note on (c): without LIVE_SERVER_ROOT the attempt fails at
the served-files check with all 27 files 404, because the
server root defaults to the production path, not the staged
ship dir (a staging artifact, not a runner defect). With the
root pointed at the staged ship (c2) it reaches preflight and
fails on the owner-away check, exactly as specified.

### A5 marker + remote-URL suite: 10/10 PASS (results/a5.log, 9.3s)

Synthetic bare repo + clone under ~/workspace/y13g-verify/a5/
(never the real repo; nothing pushed to the real origin).
Marker-logic cases run with a git test-double (a5/bin/git)
that intercepts ONLY `git remote get-url origin` (returns the
known URL) and `git fetch origin todolist-push` (real fetch
from the local bare repo, explicit refspec updating
origin/todolist-push); every other git call passes through to
real git. The pin itself is verified with REAL git (case 6 +
real-repo control), so the stub only supplies the pin's input.

| case | expectation | driver rc | outcome |
|---|---|---|---|
| 1 fake completion (subject "Y6c nested run DONE", junk body/diff) | passes BY DESIGN | 0 | documented limitation, not a pass (see below) |
| 3a old-date completion (2020-01-01) vs newer abort | refuse | 2 | PASS, "abort ... is newer than the newest completion" |
| 3b forged FUTURE-date completion (2026-11-23 %ct), older in log position than a genuine abort (2026-11-22 %ct) | refuse via log-order | 2 | PASS (old %ct code would have passed this; state log confirms position order: abort first despite the older %ct) |
| C1 completion newer than abort | pass | 0 | PASS |
| C2 harness subject | refuse | 2 | PASS, "no Y6c completion marker" |
| C3 body-DONE under "Fix flake" | refuse | 2 | PASS |
| C4 completion on the wrong path (y6d) | refuse | 2 | PASS |
| 6 attacker repo, check_marker | refuse on remote URL | 2 | PASS, "git remote origin is .../a5/attacker.git, not the known repo https://github.com/phamTuan207/computer-use-wayland.git; refusing (attacker fork?)" (real git) |
| 6 attacker repo, check_manifest | refuse on remote URL | 2 | PASS, same message (real git) |
| R real repo control | pin passes, marker check runs on real state | 2 | PASS, "no Y6c completion marker on todolist-push" (real git, real fetch) |

### A7 symlink set: 10/10 PASS (results/a7.log, 2.2s)

Five shapes, each refused at BOTH layers with the corrected
kind label ("symlink", never "pyc_refused").

| shape | scan layer (rc 2) | _verify_manifest layer (rc 2, stripped copy) |
|---|---|---|
| symlinked fixtures dir | {"refused": true, "kind": "symlink", "files": ["codex-y5/fixtures"]} | "manifest path escapes ship dir: codex-y5/fixtures/test-01-git-workflow.html" |
| symlinked manifest file | kind symlink, files ["codex-y5/test-01-git-workflow.md"] | "manifest path escapes ship dir: codex-y5/test-01-git-workflow.md" |
| symlinked codex-y5 dir | kind symlink, files ["codex-y5"] | "manifest path escapes ship dir: codex-y5/test-01-git-workflow.md" |
| symlinked fixture to outside tampered target | kind symlink, files ["codex-y5/fixtures/test-01-git-workflow.html"] | "manifest path escapes ship dir: codex-y5/fixtures/test-01-git-workflow.html" |
| symlinked non-manifest dir (codex-y5/extras) | kind symlink, files ["codex-y5/extras"] | "symlink in ship dir: codex-y5/extras" (27 checked) |

### A8 _proven_no_body: 12/12 PASS (results/a8_ast.log)

Required case: `_proven_no_body({"eval_error": "",
"snapshots": [{"hasBody": False, "readyState": "complete"}]})`
returns False (Amend 5 `is not None`). Full table: eval_error
+ good snapshot False; eval_error "" False; eval_error None
True; no eval_error True; hasBody missing False; hasBody None
False; no snapshots False; eval_error + no snapshots False;
contradictory snapshots False; not complete False; eval_error
"" + no snapshots False; non-dict snapshot ignored True.

### AST comparison: 13/13 PASS (results/a8_ast.log)

All 12 tokenizer functions AST-identical between the runner
and the launcher copies (docstrings stripped):
_script_basename_is_runner, _is_python_token, _shlex_tokens,
_runner_md5s, _path_is_runner_copy, _token_is_runner_script,
_c_code_executes_runner, _python_executes_runner,
_command_executes_runner, _argv_tokens, _is_runner_cmdline,
_is_codex_process. Raw tokenizer-block text diff is exactly 4
lines = the two sync-direction notes (the block comment and the
_is_runner_cmdline docstring naming the counterpart file).

### Clean ship + launcher dry run: 6/6 PASS (results/clean_ship.log)

Fresh re-stage rc 0; direct verify rc 0 (27 checked, md5
0ca16ddd). Launcher dry run on the staged ship with --ship-dir
(real repo, no Y13_GO, no live ports, no live run):
check_manifest rc 0, _scan_ship rc 0 ("ship allowlist scan
passed (27 manifest files)"), _check_entry_pyc rc 0. Extra
(A6b re-test): a self-consistent tampered ship (fixture byte
changed + manifest entry edited to match) is refused by
check_manifest: "ship manifest md5 e657094887a1450a96188d13952b93f3
!= committed manifest md5 0ca16ddd743acc9e28294fecd07a9c70".

## Known limitations (documented, not failures)

1. Direct -m/import on a FORGED entry .pyc executes the forged
   bytecode in-process (A2 hole demos: marker prints; the
   fake-OK forge prints {"manifest_ok": true} and exits 0, so
   the gate lies). Unfixable in-process by design: the forged
   bytecode IS the running code. The production control is the
   launcher's out-of-process _check_entry_pyc (refuses every
   forged entry .pyc with no marker, verified on run_codex_y5,
   launch_y13, and run_live) plus never invoking -m/import on
   an unverified ship. -m and bare imports are unsupported
   invocation forms (guard exits 2, SHIPPED.md + docstrings).
2. A5 case 1: the Y6c marker is a coordination signal, not
   authentication. A subject spoof (exact subject, junk
   body/diff, pushed by anyone with push access) passes by
   design. The fix documents this; it does not add a content
   check. The remote-URL pin (case 6) closes the
   attacker-controlled --repo route.
3. `_path_is_runner_copy` fails open on an unresolvable path
   (documented in code; the ports + flock backstop applies).
   Not a test failure; noted for the record.
4. A5 marker-logic cases used a git test-double for the
   get-url/fetch transport calls (a single URL cannot both
   equal the pinned GitHub string and point at a local test
   repo). The pin itself was verified with real git.

## Harness inventory (committed, so they survive)

improvements/y13g-verify/: extract_lib.py (AST extraction +
func_ast_dump), forge_pyc.py (header forge + fake-OK form),
launcher_check_driver.py (one extracted launcher check in a
subprocess), attack_a2.py, attack_a6d.py, attack_a4_unit.py,
attack_a4_live.py, attack_a3.py, attack_a5.py (incl. the git
test-double a5/bin/git, rebuilt by the script), attack_a7.py,
attack_a8_ast.py, clean_ship.py, sleeper.c (argv-ignoring
sleeper for live dummies, gcc -O2).

Harness bugs found and fixed during the run (all in my code,
none in the fix): the driver required --ship-dir even for
marker checks (now defaults to the repo dir); the A4 live echo
case was vacuous on its first run (bash exec-replaced itself
with the trailing sleep; fixed with a trailing `read x`
builtin and the whole probe re-run); the A7 outside paths
collided between the two ships per shape (made per-ship); the
A7 verify-layer assertion required the literal word "symlink"
while the containment refusal says "escapes ship dir"
(assertion widened; the refusal was always correct). The
verify log itself lost one entry twice to an anchor mistake
while editing (A4-live entry, then A3 entry); both were
restored and the log order verified before committing.

## What was NOT tested

- No live run was attempted (no Y13_GO, no live ports, no Zen
  driving). The live-run attempt in A3 stops at preflight by
  design. The H3 gate state (no Y6c-pattern marker will ever
  land) is a Muse direction question, not part of this fix
  verification.
- The A6e self-deleting shim was not re-run (it caused the
  Y13r2 re.py incident); A6d on its own proves code executes
  before any gate, and the fix closes it for all 15 names.

## Commits

- d76daba: harness rebuild + A2 11/11 PASS
- 4651ef8: A6d 18/18, A4 unit 39/39, A4 live 6/6 PASS
- c45e1ad: A3 7/7 PASS
- cbddfca: A5 10/10 PASS (driver ship-dir fix)
- (this report + A7/A8/AST/clean-ship + log: next commit)

Each commit pushed to todolist-push and verified with
`git ls-remote origin todolist-push`.
