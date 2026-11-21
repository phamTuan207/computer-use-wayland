# Independent re-verification report: Y13g ROUND-2 fix diff

- Verifier: independent Muse subagent (depth 2). Did NOT write the fix.
- Date: 2026-11-22, work 01:00 to 01:14 +07.
- Repo: ~/workspace/computer-use-wayland, branch todolist-push.
- Fix under test: Y13g round-2 commits 0639d04, 87eec47, 6ba43f2,
  8bdd5aa, 5a9b9e8 (6 files: run_codex_y5.py, launch_y13.py,
  codex-y5-manifest.json, codex-y5/SHIPPED.md,
  regen_codex_y5_manifest.py, worker-y13-codex-y5-live-plan.md).
- Scope: ONLY the round-2 diff. No fix file was edited. No live
  Zen driving. No ydotool. No em/en dashes. Never touched
  /usr/lib or any system path.
- Running log: improvements/worker-y13g-r2-verify-log.md.
- Harnesses: improvements/y13g-r2-verify/ (committed; rebuilt
  from the round-1 harnesses plus new R2 cases). Staged ships
  and result logs: ~/workspace/y13g-r2-verify/ (ships/,
  results/, so-plants/, so-markers/, a5/, a5b/, a7-outside/).

## Verdict: FAIL (narrow, 2 defects, both in _check_entry_pyc)

277 of 280 checks pass. Every security property holds: forged
entry .pyc files are refused in every form, .so and .py plants
never execute, the marker/log-order/remote pin all hold, and
the tokenizer rewrite is complete and identical in both
copies. The 3 failing checks come from 2 root causes, both in
the launcher's _check_entry_pyc:

1. **Filename-sensitive marshal comparison (A3h, 2 checks).** A
   legitimate entry .pyc produced by relative-path `python3 -m
   py_compile run_codex_y5.py` (run from inside the ship dir,
   the natural form) is refused: the cached code object has
   co_filename "run_codex_y5.py" while the fresh compile uses
   the absolute ship path. Consts, names, and code bytes are
   identical; marshal equality fails ONLY on co_filename. The
   ship therefore does NOT self-heal to direct verify rc 0
   after a relative-path py_compile. Fail-closed (refuse +
   "re-stage the ship"), trivial recovery (delete the .pyc).
   The documented self-cache path (-m/import, absolute
   filenames) is unaffected. Fix shape: normalize co_filename
   in the comparison (e.g. code.replace(co_filename=src) on
   both sides).
2. **Symlink-unsafe deletion (A7 shape-6b, 1 check).**
   _check_entry_pyc uses plain os.listdir() + os.unlink() on
   SHIP_DIR/__pycache__ and never applies the realpath-inside-
   ship check that _entry_pyc_paths (the -m guard helper) has.
   A legitimate .pyc behind a symlinked __pycache__ is
   DELETED outside the ship (proven twice: manual probe +
   harness re-run). R4 claims symlink safety ("the guard
   never deletes a file OUTSIDE the ship"), but that property
   holds only for the guard helper, not for the function that
   deletes files during launch checks. Reachability in the
   production flow is LIMITED: the launcher module-top scan
   refuses a symlinked __pycache__ before main() runs
   _check_entry_pyc. Damage scope is narrow (only a file
   named <entry-stem>.*.pyc in the linked dir, only when its
   bytes match a fresh compile). Fix shape: one realpath
   check at the top of _check_entry_pyc (treat a symlinked
   cache dir as absent, mirroring _entry_pyc_paths).

## Pins verified first

| file | md5 | brief pin | holds |
|---|---|---|---|
| tests/realistic/run_codex_y5.py | d5047ff573820491263a2eb3805105f4 | d5047ff5 | yes |
| tests/realistic/launch_y13.py | 8e72a5ce85cbaf8382f998987e8890e5 | 8e72a5ce | yes |
| tests/realistic/run_live.py (manifest) | 84fa106c253d5e7f16daccf2ce3f14a5 | 84fa106c | yes |
| tests/realistic/codex-y5-manifest.json | 7c76383402e4c50b28adab6b25a22e09 | 7c763834 | yes |

Manifest: 27 files. The working-tree run_live.py md5 is
d8e2b14d (91d3cd2 changed HEAD); BY DESIGN the manifest pins
the 1e3901c bytes (84fa106c), and the regen script stages
run_live.py from `git show 1e3901c:...`, never from the working
tree. Verified: all 27 manifest md5s match the working tree
except run_live.py, which matches the pinned commit bytes
(staged ship run_live.py md5 is 84fa106c). Python 3.12.3.
Each round-2 commit touches only the 6 fix files. Clean ship
staged with the regen script: verify rc 0, manifest_ok true,
27 checked, 0 mismatches, md5 7c763834; regen rewrote the
manifest file but git shows no diff (bytes identical).

Expected behavior changes confirmed, not failures: bare (no
-P) invocations refuse at the safe_path gate (exit 2, no
marker); A8 eval_error None returns False; the tokenizer
block has 14 functions; the launcher writes a fresh handover
token at run start (verified in isolation + accepted by
check_token).

## Method notes

- Importing either entry point exits 2 (the script-form-only
  guard), so functions were AST-extracted (extract_lib.py)
  and run in a fresh namespace, or tested out-of-process via
  subprocess with -P. The modules were never imported.
- Ships were staged fresh from the committed bytes with the
  regen script and tampered only in the staged copy, never
  the repo tree. Forged .pyc files were built by forge_pyc.py
  (correct header + marker first); legitimate .pyc files by
  forge_pyc.legit() (unmodified source, correct header) or
  by real py_compile / -m / import.
- Launcher checks ran out-of-process through
  launcher_check_driver.py, which AST-extracts checks from
  the committed launcher. A POISON-MARKER in driver output
  would prove a check executed ship code; none ever appeared.
- Every test is timed and logged (wall-clock
  Asia/Ho_Chi_Minh + elapsed). Result logs live at
  ~/workspace/y13g-r2-verify/results/.

## Per-battery results (280 checks total, 277 pass)

### A2 forge set: 19/19 PASS (results/a2.log, 3.5s)

11 original + 8 new R2 checks. Launcher _check_entry_pyc
refuses every forged entry .pyc (run_codex_y5, launch_y13,
run_live) rc 2, no marker; direct script-form fake-OK
refuses kind pyc rc 2; hole demos (-m/import) still execute
the forged bytecode, as documented (known unfixable hole,
controlled out-of-process). New: legit entry .pyc accepted
+ deleted (A2h); forged entry .pyc exempt from the launcher
module-top scan, reaching the go check (A2i); nested forged
entry .pyc refused at both scans, kind mixed (A2j); pypy-tag
forge refused (A2k); nested legit .pyc deleted by the -m
guard, with the empty nested dir residue refused
fail-closed and rc 0 restored after deleting the empty dir
(A2l).

### A6d stdlib map + .so plants: 66/66 PASS (results/a6d.log, 11.3s)

15 .py names -P refuse rc 2 kind planted-py, marker never
prints; 3 no-P spot checks (re, json, enum) refuse at the
safe_path gate (exit 2, "run with python3 -P", no scan JSON).
16 .so stems (glob, http, hashlib, shlex, re, json, socket,
subprocess, datetime, pathlib, enum, copyreg, functools,
collections, typing, sre_compile) x 3 forms: runner -P
(kind unexpected-file), runner bare (safe_path), launcher -P
(tampered-ship); marker file never created. Control: a
direct import of the built glob .so plant writes
SO-EXECUTED, proving the plants were armed. The shlex stem
(the module-top `import shlex` trigger) is covered in all 3
forms.

### A4 unit table: 81/81 PASS (results/a4_unit.log, 0.2s)

39 original + 42 new R2 cases; both copies agree on every
case. New forms all behave as specified: -uc/-Bc/-um/-Bum,
-uW/-uX/-iuW, -m pdb + script (True) vs -m runpy/-m cProfile
(False), python3 - stdin (True), timeout 60s/1m/1.5m/90.
(True), bash -c glued ;/&& (True), -c os.system /
runpy.run_path / exec of a renamed copy (True, incl.
__file__ preset), wrappers nice/stdbuf/taskset/sudo/uv run
(True), exec -a (True), pypy3 (True); mere mentions NOT
caught: -c import, echo/grep, md5sum.

### A4 live probe: 17/17 PASS (results/a4_live.log, 6.6s)

Real dummy processes (argv-ignoring sleeper) + the real
launcher check_runner_quiet via the driver. Baseline clean
(rc 0, no offenders, 0 warnings). All flagged cases name
the dummy pid: bare, -m, renamed, symlink, nice, sudo,
uv run, timeout 60s, timeout 1m, pdb, stdin, bash -c glued
;, exec -a. Not flagged: echo, md5sum, python3 -c import.

### A3 brick sequence: 17/19, 2 FAIL (results/a3.log, 3.8s)

| case | outcome |
|---|---|
| (a) -m on clean ship | PASS, guard rc 2, no .pyc left |
| (b) direct verify after (a) | PASS, rc 0 |
| (c/c2) live-run attempt | PASS, MANIFEST OK, fails at preflight (owner-away) |
| (d) empty __pycache__ alone | PASS, rc 0 |
| (e) env-guarded -m | PASS, writes nothing |
| (f) forged non-entry .pyc | PASS, kind pyc rc 2, no marker |
| (g) -m without -P | PASS, guard fires first, no .pyc left |
| (h) py_compile self-heal | FAIL, see defect 1 below |
| (h-abs) absolute-path py_compile control | PASS, accepted + deleted + rc 0 |
| (i) import run_live self-heal | PASS, refuse, delete, rc 0 |

Defect 1: relative-path `python3 -m py_compile run_codex_y5.py`
produces a legitimate .pyc (same source bytes) that
_check_entry_pyc refuses (rc 2, .pyc not deleted), so the
ship does not self-heal. Proven: cached co_filename is
"run_codex_y5.py" (relative, as invoked) vs the fresh
compile's absolute path; consts, names, and code bytes are
identical. The absolute-path control passes, bounding the
defect to the filename metadata.

### A5 marker + remote-URL suite: 10/10 PASS (results/a5.log, 6.0s)

Fake completion passes BY DESIGN (known limitation, case
1). 3a/3b refuse by log order (forged old/future dates do
not outrank a newer abort). C1 passes, C2/C3/C4 refuse.
Attacker fork refuses on the remote URL (real git, both
check_marker and check_manifest). Real-repo control: pin
passes, marker check runs on real state (refuses: no Y6c
marker).

### A5b remote-URL normalization: 18/18 PASS (results/a5b.log, 1.0s)

_unit _normalize_remote_url (12 checks): SSH form, trailing
slash, no .git, wrong-case host all normalize equal to the
pinned URL; http, wrong owner/repo/host do not. Driver
_check_remote (6 checks) against a synthetic clone: the 4
pass variants rc 0, http + attacker fork refuse rc 2 "not
the known repo".

### A7 symlink set: 13/14, 1 FAIL (results/a7.log, 4.2s)

5 original shapes x 2 layers all pass (kind symlink). Shape
6 (symlinked __pycache__ -> outside dir): direct verify
refuses kind symlink; launcher scan refuses "symlink dir in
ship: __pycache__"; _check_entry_pyc refuses the FORGED
outside .pyc rc 2 with the file intact. Defect 2: a
LEGITIMATE .pyc behind the symlinked __pycache__ is DELETED
outside the ship (driver rc 0 "verified + removed", outside
file gone; proven twice). _check_entry_pyc uses plain
os.listdir + os.unlink with no realpath check, unlike the
guard helper _entry_pyc_paths.

### A8 _proven_no_body: 12/12 PASS (results/a8_ast.log)

eval_error None returns False now (R9); "" still False; all
other rows as specified.

### AST comparison: 15/15 PASS (results/a8_ast.log)

All 14 tokenizer functions AST-identical between the runner
and the launcher copies (docstrings stripped), including
the 2 new ones (_m_module_is_runner, _is_timeout_dur).
Raw block diff (extended through the CODEX comment) =
exactly 6 lines: the 2 sync notes (4 lines) + the CODEX
comment (2 lines), all naming the counterpart file.

### Clean ship + launcher dry run: 9/9 PASS (results/clean_ship.log, 2.5s)

Fresh re-stage rc 0; direct verify rc 0 (27 checked, md5
7c763834); launcher dry run check_manifest / _scan_ship /
_check_entry_pyc all rc 0; self-consistent tampered ship
refused by the manifest pin. Token checks (C3-10):
write_token produces a fresh token check_token accepts
(temp path, never the real token); 5h-stale and missing
tokens refuse.

### Spot checks: R6 7/7, R8 1/1

- R6 _is_codex_process: argv[0] codex True, /usr/bin/codex
  True, token ending /codex True; grep/echo codex False;
  path containing a codex dir False; empty False.
- R8 _check_remote with git missing from PATH: refuses
  exit 2 with a clean message, no traceback.

## Known limitations (documented, not failures)

1. Direct -m/import on a FORGED entry .pyc executes the
   forged bytecode in-process (A2 hole demos). Unfixable
   in-process by design; the production control is the
   launcher's out-of-process _check_entry_pyc plus never
   invoking -m/import on an unverified ship. -m and bare
   imports are unsupported invocation forms (guard exits 2).
2. A5 case 1: the Y6c marker is a coordination signal, not
   authentication. A subject spoof passes by design. The
   remote-URL pin (A5 case 6, A5b) closes the
   attacker-controlled --repo route.
3. `_path_is_runner_copy` fails open on an unresolvable path
   (documented in code; the ports + flock backstop applies).
4. A5 marker-logic cases used a git test-double for the
   get-url/fetch transport calls. The pin itself was
   verified with real git.
5. Nested empty-dir residue (A2l): the -m guard deletes
   nested .pyc files but leaves empty nested dirs, which the
   scan refuses as unexpected-dir. A probe only ever writes
   top-level .pycs (empty top-level __pycache__ IS exempt),
   so a nested dir can only appear by hand; refusing it is
   fail-closed tamper evidence, and deleting the empty dir
   restores rc 0.

## Harness bugs found and fixed during the run (all in my code, none in the fix)

- Driver missing _normalize_remote_url (A5 first run 0/10),
  missing _m_module_is_runner + _is_timeout_dur (A4 live
  first run 12/17, driver rc 1), missing TOKEN_TTL_S
  (clean ship first run 7/9). Each fix was followed by a
  full re-run of the affected battery.
- A2j/A2l expectations corrected after root-causing the
  outputs (kind mixed, not pyc; empty nested-dir residue).
- The A3h and A7-6b failures were NOT harness artifacts:
  both were root-caused mechanically (co_filename-only
  marshal difference; outside file deleted, verified present
  before and absent after) and reproduced.

## What was NOT tested

- No live run was attempted (no Y13_GO, no live ports, no
  Zen driving). The live-run attempt in A3 stops at
  preflight by design.
- R8 TimeoutExpired was not directly triggered (only the
  OSError path, via git missing from PATH); the
  TimeoutExpired branch uses the same _fail wrapper.
- The A6e self-deleting shim was not re-run (it caused the
  Y13r2 re.py incident); A6d on its own proves code executes
  before any gate, and the fix closes it for all 15 names
  plus 16 .so stems.
- Docs (R10 plan/SHIPPED.md/regen docstring) were not
  mechanically verified beyond the SHIPPED.md staged bytes
  being in the allowlist; the AST/sync checks cover the
  CODEX comment sync.

## Commits

- 3129ba2: harness rebuild + pins
- dec965c: A2/A4-unit/A8/A3/A6d/A7 results (2 defects found)
- 0d628f8: driver extraction fixes + A5/A5b/A4-live/clean results
- (this report + final log: next commit)

Each commit pushed to todolist-push and verified with
`git ls-remote origin todolist-push`.
