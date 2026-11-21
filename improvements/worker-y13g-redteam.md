# Redteam: Y13g fix re-review (AMEND)

- Reviewer: Worker Y13g redteam (independent Muse attacker)
- Date: 2026-11-22, work 00:05 to 00:30 +07
- Repo: ~/workspace/computer-use-wayland, branch todolist-push
- Commit under review: fix diff 431b2a9..b815590 (Y13g commits
  caa4a7c, 0cf43f8, 03303f4, 6cd0f7a, b815590)
- Scope: ONLY the Y13g fix diff (tests/realistic/run_codex_y5.py,
  tests/realistic/launch_y13.py,
  tests/realistic/regen_codex_y5_manifest.py, manifest,
  SHIPPED.md, plan). No fix file was modified by this review. No
  live driving. No commits by the review itself except its own
  paper and log.
- Method: every claim below was reproduced live on freshly staged
  ships built from the NEW committed bytes (regen --stage to
  ~/workspace/y13g-redteam/ship: manifest md5
  0ca16ddd743acc9e28294fecd07a9c70, 27 files, clean verify rc 0;
  runner md5 db3e357f, launcher eec63492, run_live 84fa106c pin
  holds). Each attack ran on its own fresh ship copy under
  ~/workspace/y13g-redteam/ships/ (tampering the staged copy,
  never the repo tree, never the real /tmp/worker-y13-server
  ship). Attack harnesses are the redteam scratch in
  ~/workspace/y13g-redteam/ (forge_pyc.py, fresh_ship.py,
  extract.py, attack_a123.py, attack_a4_unit.py,
  attack_a4_live.py, attack_a5.py, attack_a6.py, attack_a7.py,
  attack_a8.py, attack_a9.py; logs a123-run1.log, a6-run1.log,
  a7-run1.log, a5-run1.log, a4live-run1.log). Pure functions were
  tested by AST extraction from the committed bytes (the entry
  points refuse import/-m at the module top, so extraction is the
  only unit route, as Y13r2 did). Attack shims print a marker
  ONLY: no deletion, no delegation, no file writes outside the
  staged ship copies. Nothing was written to /usr/lib or any
  system path.
- Verdict: AMEND. The fix holds for the specified set and all
  five amends verify, but it leaves real, narrow residuals in the
  same classes (tokenizer evasions, the -m forge, import-before-
  verify, the _check_entry_pyc reachability, the run_live brick).
  None of them lets a forged or tampered ship execute on a
  supported flow, and none lets a standard rival form evade into
  a concurrent run. Fix the amend items below, re-run the listed
  probes, then the live run may proceed.

## Verdict summary

What holds, proven live:

- B1 (forged entry .pyc): the launcher path refuses before exec
  with no marker (module-top scan, and the isolated
  _check_entry_pyc is correct on all 8 shapes). The direct
  script form never loads the cache. The -m/import direct
  invocation on a forged ship STILL executes the marker (the
  documented unfixable in-process hole, confirmed live, see
  Finding F1). The control Y13g adjudicated (launcher check +
  never invoking -m/import on an unverified ship) is implemented
  and proven: the launcher execs `python3 -P run_codex_y5.py`
  only, never -m.
- B2 (planted stdlib .py): FIXED completely, stronger than
  specified. All 15 names refuse rc 2 with kind "planted-py",
  marker never prints, in BOTH the -P and the plain form, nested,
  and through the launcher (38/38).
- B3 (tokenizer): the full specified set is caught, unit (both
  copies, AST-identical) and live (real dummies, real
  check_runner_quiet). Every -m form, flag-value form,
  renamed/extensionless/symlinked md5 copy, -c exec/eval form,
  and every mere mention correctly passes. Eleven FRESH evasions
  were found in the same class (Finding F3), each proven a real
  execution form, each mitigated by the ports backstop.
- B4 (-m brick): the specified sequence passes end to end (-m
  rc 2 with the script-form message, no .pyc left, direct verify
  after rc 0, empty __pycache__ rc 0, env-guarded -m writes
  nothing). Residual: `import run_live` and `py_compile` still
  brick verify until re-stage (Finding F4).
- Amends 1-5: ALL verify. Remote pin (attacker fork refuses,
  known URL passes, trailing slash refuses, no origin refuses).
  -c mention false positives gone (echo/grep/md5sum pass) and
  the codex warning now matches the executable basename
  (mycodex-backup is silent, /usr/bin/codex warns). Scan JSON
  kind label is correct ("symlink", "mixed"). --ship-dir and
  Y13_SHIP_DIR refuse a tampered ship without touching the real
  ship. eval_error "" returns False from _proven_no_body.
- A1, A5, A7, A8: all hold (forged run_live .pyc refused;
  marker log-order refusal works; all 5 symlink shapes refuse
  at all layers; _proven_no_body 12/12).

Why AMEND and not GO: Finding F3 (11 tokenizer evasions),
Finding F5 (a tampered run_live.py executes on the direct path
before the manifest refusal), Finding F2 (_check_entry_pyc is
unreachable in the live flow, so a documented control never
runs), and Finding F4 (the run_live/py_compile brick) are all
real, all in the classes this fix was supposed to close, and
all fixable with small changes. Why AMEND and not BLOCK: none
of them executes attacker code on a supported flow (the
launcher refuses every tampered ship pre-exec; the direct
forms that execute require ship-dir write access plus an
unsupported or unverified invocation), and none lets a standard
rival form evade (the evasions are exotic forms, and a rival in
any form still holds ports 8771/4452, so check_ports refuses
the new launch).

## Per-attack results

Notation: PASS means the fix holds (attack fails); FAIL means the
attack succeeds (fix broken); DOCUMENTED means the outcome was
predicted by the fix design and is recorded as a known
limitation, not counted as a pass.

### A1. H1 forge, top level, nested, -m form: PASS (3/3)

Forge: real run_live.py source plus a marker print, header
mtime/size from the real source stat.

- Top level, direct `python3 -P run_codex_y5.py
  --verify-manifest`: `{"refused": true, "kind": "pyc",
  "files": ["__pycache__/run_live.cpython-312.pyc"],
  "manifest_ok": false}`, rc 2, marker never printed.
- Nested `codex-y5/__pycache__/run_live.cpython-312.pyc`:
  same refusal with the nested path, rc 2, no marker.
- -m form on the forged ship: rc 2, "run as a script", no
  marker (the guard fires before the run_live import).

### A2. Forged ENTRY .pyc: MIXED (direct + launcher PASS, -m/import DOCUMENTED hole)

- Direct form, forged `__pycache__/run_codex_y5.cpython-312.pyc`:
  rc 2, kind "pyc", no marker. The script __main__ never loads
  the cache.
- -m form, same forge: MARKER PRINTS, then the guard message,
  rc 2. Output line 1 `POISON-MARKER: A2 entry run_codex_y5
  forged`, line 2 `run as a script (python3 run_codex_y5.py),
  not with -m and not via import`. The forged bytecode IS the
  running code; the guard cannot protect it. DOCUMENTED hole,
  confirmed live (Finding F1).
- Import form (`python3 -c "import run_codex_y5"`, same forge):
  MARKER PRINTS, rc 2 (guard message after the marker).
  DOCUMENTED hole, confirmed live (Finding F1).
- A2b fake-OK forge (entry .pyc whose code prints a clean
  verify JSON and exits 0, header forged from the real source
  stat), via -m: MARKER PRINTS, then `{"manifest_ok": true,
  "files_checked": 27, "mismatches": [], "manifest_md5":
  "f27c03020c9866cfa0dcd637df6f8647"}`, rc 0. The gate lies via
  -m. DOCUMENTED hole, confirmed live (Finding F1).
- Launcher script form on a forged-entry ship (`python3 -P
  launch_y13.py --ship-dir <ship> --repo <repo> all`): rc 2,
  `[launch_y13] REFUSED: tampered ship dir <ship>: pyc:
  __pycache__/run_codex_y5.cpython-312.pyc`, no marker. Refuses
  pre-exec at the module-top scan.
- Launcher self-pyc (forged `__pycache__/launch_y13.cpython-312.pyc`):
  same, rc 2, no marker.
- Wrong-tag forge (`run_codex_y5.cpython-311.pyc`), direct form:
  rc 2, kind "pyc", no marker.
- Isolated _check_entry_pyc (extracted from the launcher,
  called directly, 8/8): forged entry refuses; legit entry
  verified and deleted; wrong-tag forged refuses; hash-based
  forged refuses; source-path-differs forged refuses;
  source-path-differs LEGIT also refuses (co_filename differs,
  fail-closed, correct); forged run_live refuses; legit run_live
  verified and deleted. The function itself is correct. It is
  unreachable in the live flow (Finding F2).

### A3. -m brick sequence: PASS (specified set) + residual (F4)

- `python3 -m run_codex_y5 --verify-manifest` on a clean ship:
  rc 2, `run as a script (python3 run_codex_y5.py), not with -m
  and not via import`, NO .pyc left behind (__pycache__ empty).
- Direct verify after: rc 0, manifest_ok true, 27 checked.
- Empty __pycache__ dir alone: rc 0, manifest_ok true.
- Env-guarded -m (`PYTHONDONTWRITEBYTECODE=1 python3 -m ...`):
  rc 2 (guard), writes nothing.
- A3b residual: `python3 -c "import run_live"` (no env guard)
  writes `__pycache__/run_live.cpython-312.pyc`, and the next
  direct verify is rc 2, kind "pyc" (BRICKED until manual
  re-stage). Env-guarded import writes nothing, verify rc 0.
  The guard covers the two entry stems only.
- A3c residual: `python3 -m py_compile run_codex_y5.py` writes
  the entry .pyc and BRICKS verify rc 2 the same way.

### A4. Tokenizer: specified set PASS, fresh evasions FAIL (11)

Unit table (attack_a4_unit.py, AST-extracted _is_runner_cmdline
from BOTH files; AST identity True, 12 defs identical; both
copies agree on every case): 69/80 pass. Every specified case
passes: bare-relative, absolute, -u, env VAR=1, nohup, setsid,
/usr/bin/python3, ./, ../, python3.12, python, run-nested-pill.py,
bash run-nested-wayland.sh, sh -c, bash -c exec, flock -c/direct,
timeout, run_live.py, hand_drive_e1.py, shebang ./, -I, all -m
forms (bare, dotted, with args, attached), -W/-X flag-value
forms (separate and attached), --check-hash-based-pycs (separate
and =), -c exec(open)/eval/compile forms, extensionless,
renamed/symlink/extensionless md5 copies (including a renamed
run_live copy), -- separator, bash -c semicolon, setsid -m,
env -i/-u, flock -w/--timeout, timeout --signal, /usr/bin/env,
command/exec wrappers, -uB bundled. Every correct non-match
passes: md5sum, -c import, -c print mention, bash -c echo/grep
mentions, cat, -m pytest, -m run_codex_y5.py (invalid), stdin,
plain codex.

Live probe (attack_a4_live.py, cc-compiled sleeper exec'd with
fake argv vectors, real check_runner_quiet, 1m51s, baseline
CHECK-PASS): 24/24 by defined expectations. All 14 CAUGHT cases
refused naming exactly the dummy pid. All 4 pass cases passed
(plain codex warns only, mycodex-backup silent, md5sum mention
passes). All 6 fresh evasions passed the check entirely
(refused=False, empty output), confirming the unit evasions live.

The 11 fresh evasions (each proven a REAL execution form, not a
tokenizer artifact; see Finding F3):

- `-c os.system` nesting: `python3 -c "import os;
  os.system('python3 run_codex_y5.py ...')"` reaches main()
  (inner runner printed manifest_ok true, rc 0). This one is a
  DOCUMENTED limit in the plan ("nested os.system/exec inside -c
  code beyond exec(/eval( is not caught"), now proven real.
- `-c runpy.run_path`: `runpy.run_path('<ship>/run_codex_y5.py',
  run_name='__main__')` with sys.argv set prints manifest_ok
  true, rc 0. Real execution, evades.
- `-c exec of a renamed copy`: `exec(open('mycopy.py').read())`
  with `__file__` preset to the ship runner prints manifest_ok
  true, rc 0. Real execution, evades. (Bare exec without
  `__file__` crashes with NameError, and exec from the copy dir
  is refused by the scan as planted-py, so only the
  `__file__`-preset form reaches main(); the tokenizer misses
  both.)
- Wrappers: `nice`, `nice -n 5`, `stdbuf -oL`, `taskset -c 0`,
  `sudo -n` all proven to run (NICE-OK, STDBUF-OK, TASKSET-OK,
  SUDO-OK). None is in the wrapper list.
- Combined flag-value forms: `python3 -uW ignore
  run_codex_y5.py`, `python3 -uX dev run_codex_y5.py`,
  `python3 -iuW ignore run_codex_y5.py` all proven real
  (UW-OK, UX-OK, IUW-OK). The tokenizer mistakes the flag value
  for the script token.

Two of my own attacks were REFUTED by live proof and corrected
in the table (recorded so the next worker does not re-chase
them): "-Xu dev script" is NOT a runner form (-X takes the
attached "u" as its value, so "dev" is the script; proven by
`python3 -Xu dev -c ...` failing "can't open file 'dev'"), and
"-c runpy.run_module" is NOT viable (the module-top guard fires,
"run as a script", proven). Both now want False and pass.

### A5. Marker spoofing: PASS except case 1 BY DESIGN (13/13)

Synthetic bare remotes + clones under ~/workspace/y13g-redteam/a5/
(own test remotes, never the real branch). check_marker is
AST-extracted; _check_remote is monkeypatched to a no-op for the
ordering cases only (the pin is tested separately, unpatched).

- Case 1, fake completion (subject exactly `Y6c nested run
  DONE`, touching improvements/worker-y6c-*.md, junk body/diff):
  MARKER-PASS. The gate checks subject, path, and log order
  only, never diff/body content or authorship. Spoof succeeds BY
  DESIGN (documented limitation, not counted as a pass).
- Case 2, marker on a different branch only: REFUSED rc 2.
- Case 3, forged old-date completion vs newer abort BY LOG
  ORDER: abort is the child (newer in log order) with committer
  date 2020-01-01, completion is the parent with a real date.
  REFUSED rc 2 (`Y6c abort ... is newer than the newest
  completion`). The old %ct code would have PASSED (completion
  date newer). The log-order fix works.
- Case 4, completion newer than abort by log order: PASS
  (control).
- Case 5, no marker: REFUSED. Case 6, unpushed marker: REFUSED.
  Case 7, harness subject: REFUSED. Case 8, body-DONE under
  "Fix flake": REFUSED. Case 9, non-git --repo: REFUSED.
- A5-pin, real _check_remote unpatched: attacker fork remote
  (origin = local path) REFUSES rc 2 (`git remote origin is
  <local path>, not the known repo ...; refusing (attacker
  fork?)`); origin = KNOWN URL passes; KNOWN URL + trailing
  slash refuses (exact match); no origin refuses.

### A6. Planted stdlib .py: PASS (38/38)

Print-only shims (no deletion, no delegation) for all 15 names
(enum, re, json, socket, subprocess, hashlib, datetime, pathlib,
copyreg, functools, collections, os, warnings, typing,
sre_compile), both forms (-P and plain): every case rc 2, kind
"planted-py", marker NEVER prints. Nested codex-y5/re.py refuses
both forms, no marker. Launcher form for re/os/json refuses both
forms, no marker. My startup-shadowing hypothesis (planted os.py
executing before the scan in the plain form) was WRONG: CPython
loads os from stdlib before the script dir joins sys.path, so
even the plain form is safe. B2 is fixed more strongly than
specified.

### A7. Symlinks: PASS (22/22)

All 5 shapes refuse at all layers, with the corrected kind
label. Control (stripped runner on a clean ship) verifies rc 0.

- Shape 1, symlinked fixtures dir (correct content): scan
  refuses rc 2, kind "symlink", files ["codex-y5/fixtures"];
  _verify_manifest refuses `manifest path escapes ship dir:
  codex-y5/fixtures/test-01-git-workflow.html`; _scan_ship and
  check_manifest refuse.
- Shape 2, symlinked manifest file (correct content): same
  pattern, kind "symlink".
- Shape 3, symlinked codex-y5 dir: same pattern.
- Shape 4, symlinked fixture to an outside TAMPERED target:
  same pattern (refused as a symlink before any content check).
- Shape 5, symlinked non-manifest dir (codex-y5/extras):
  refused at all layers (the os.walk islink check catches what
  path containment cannot).
- Mixed (symlink + .pyc): kind "mixed".

### A8. Wall-cap / _proven_no_body: PASS (12/12)

Extracted _proven_no_body from the new runner bytes. eval_error
"" + good snapshot returns False (Amend 5 holds). eval_error
None + good snapshot returns True (key present with None reads
as no error, same as before). All other table rows match Y13r2:
eval_error + good snapshot False; no eval_error + good snapshot
True; hasBody missing/None False; no snapshots False; eval_error
+ no snapshots False; contradictory False; not complete False;
empty diag False; non-dict snapshot ignored True.

### A9 (extra). Tampered run_live.py: DIRECT executes, LAUNCHER refuses

Tampered run_live.py (marker print prepended, manifest
untouched) on the DIRECT path: MARKER PRINTS, then
_verify_manifest refuses rc 2 on the md5 mismatch
(`run_live.py: want 84fa106c..., got 1a396f5d...`). The runner
imports run_live BEFORE verifying it, so any tampered manifest
.py executes on the direct path (Finding F5). Launcher layers
(extracted, real repo): check_manifest PASSES (ship manifest
md5 unchanged, as expected), _check_entry_pyc passes (no .pyc),
_scan_ship REFUSES rc 2 (`ship file md5 mismatch: run_live.py`),
no marker. The production path is safe; the direct path is the
residual.

### --ship-dir (extra): PASS

Launcher with --ship-dir at a tampered ship (planted re.py)
refuses rc 2 naming the tampered dir, no marker; Y13_SHIP_DIR
env form identical. The real ship still verifies rc 0
afterwards (untouched). Amend 4 holds end to end.

## Findings (fix list for the next worker)

### F1 (residual, documented): -m/import on a forged entry .pyc still executes

- Evidence: A2 -m form (marker prints, rc 2), A2 import form
  (marker prints, rc 2), A2b fake-OK via -m (marker prints +
  fake manifest_ok true, rc 0).
- Assessment: the forged bytecode IS the running code, so no
  in-process guard can stop it; Y13g documented this and built
  the control (launcher refuses pre-exec, never invokes -m; the
  launcher exec line is `python3 -P run_codex_y5.py`, verified
  by grep, line 1135). The control is proven (A2 launcher
  2/2). The residual needs ship-dir write access plus an
  operator invoking an unsupported form on an unverified ship.
  Accept the adjudication, but do NOT claim the Y13r2 B1
  re-test ("-m/import form, no marker") is met as literally
  written: it is met only through the launcher path.
- No code change required by this finding alone; keep the
  documented limit in SHIPPED.md and the plan.

### F2 (design accuracy): _check_entry_pyc is unreachable in the live flow

- Evidence: A2 launcher test (the refusal message is the
  module-top scan's format, not _check_entry_pyc's); main()
  order (check_manifest's planted walk refuses any .pyc before
  _check_entry_pyc runs); isolated test proves the function
  itself is correct on all 8 shapes.
- Precise fix (pick one): (a) reorder so _check_entry_pyc runs
  BEFORE the planted-.pyc refusal in check_manifest (defer
  entry .pyc files to _check_entry_pyc, which refuses forged
  ones and deletes legit ones), so the "verify then delete a
  legit cache" mechanism actually operates; or (b) document
  _check_entry_pyc as a TOCTOU-only backstop and correct the
  SHIPPED.md/plan claims that the launcher "verifies the entry
  .pyc out-of-process and deletes it before exec".
- Re-test: a ship with a legit entry .pyc from `py_compile`
  must be verified + deleted by the launcher (not refused as
  planted bytecode), and a forged one must still refuse with
  no marker.

### F3 (tokenizer residuals): 11 fresh evasions, all proven real

- Evidence: A4 unit 69/80 (both copies identical) + A4 live
  24/24 (6 evasions confirmed live, refused=False).
- Precise fix: (1) wrappers: add nice, stdbuf, taskset, sudo
  (and any other command-prefix wrapper) to the wrapper strip
  list in _command_executes_runner, both copies; (2) bundled
  flag-value: when a dash token ends in W or X with no attached
  value after it (e.g. -uW, -uX, -iuW), skip the next token as
  the flag value (the value-taking flag is the LAST char of the
  bundle); (3) -c code: extend the exec(/eval( leg to runpy
  (run_path) and os.system, and apply the md5 leg to paths
  inside exec(/eval( strings (a renamed copy exec'd with
  `__file__` preset reaches main()); (4) keep the documented
  os.system limit honest: it is now PROVEN real, not
  hypothetical, so either close it or keep it listed with the
  ports backstop named.
- Mitigation today (why this is AMEND, not BLOCK): a rival in
  any of these forms still holds ports 8771/4452, so
  check_ports refuses the new launch; no worker uses these
  forms. The fix is small and the re-test is the A4 unit table
  (must reach 80/80) plus the A4 live probe (the 6 live
  evasions must refuse naming the dummy pid).
- Re-test: re-run attack_a4_unit.py (69/80 must become 80/80)
  and attack_a4_live.py (the 6 evade cases must become caught).

### F4 (residual brick): `import run_live` and `py_compile` brick verify until re-stage

- Evidence: A3b (import run_live writes run_live .pyc, verify
  rc 2), A3c (py_compile writes the entry .pyc, verify rc 2).
  Fail-closed, manual remedy (re-stage or rm __pycache__).
- Precise fix: extend the unbrick to the run_live stem (the
  launcher already lists run_live in _check_entry_pyc, but see
  F2: it never runs), or have the runner's module-top guard
  delete a run_live .pyc whose source matches a fresh compile
  (same out-of-process shape as the launcher check), or document
  that `import run_live` and `py_compile` on ship files require
  PYTHONDONTWRITEBYTECODE=1 and a re-stage if forgotten.
- Re-test: the A3b/A3c sequences must end with direct verify
  rc 0 without manual deletion.

### F5 (defense in depth): tampered run_live.py executes on the direct path

- Evidence: A9 (marker prints, then manifest_ok false, rc 2).
  The runner imports run_live before _verify_manifest runs.
- Precise fix: verify the entry .py hashes against the manifest
  at module top, after the scan and after importing hashlib but
  BEFORE importing run_live (the manifest is readable there;
  refuse rc 2 on any mismatch). The launcher already does this
  pre-exec (_scan_ship); the runner should do the same
  pre-import.
- Re-test: re-run the A9 tamper (direct verify must refuse rc 2
  with NO marker printed).

### F6 (documented limitation): marker case 1 still passes by design

- Evidence: A5 case 1 (exact subject + junk body/diff passes).
  A subject spoof needs push access to todolist-push (or
  control of the --repo path, now pinned). Same assessment as
  Y13r2: outside the stated coordination threat model. No code
  change; keep it documented as a coordination signal, not
  authentication.

## Confirmed holds (what the fix got right, verified live)

- A1 forged run_live .pyc (top, nested, -m): refused rc 2, no
  marker.
- B2 planted stdlib .py (15/15, both forms, nested, launcher):
  refused rc 2, kind "planted-py", marker never prints.
- B3 specified set: all -m, flag-value, renamed/extensionless/
  symlinked, -c exec/eval forms caught, unit and live; all mere
  mentions pass (md5sum, echo, grep, -c import, -c print).
- B4 specified sequence: -m rc 2 + no .pyc left + direct verify
  rc 0; empty __pycache__ rc 0; env-guarded -m writes nothing.
- H3 marker: log-order refusal works (old-date completion vs
  newer abort); remote pin works (fork refuses, known URL
  passes, trailing slash refuses, no origin refuses).
- Symlinks: all 5 shapes refuse at all 3 layers with the
  corrected kind label.
- _proven_no_body: 12/12 including eval_error "" -> False.
- Tokenizer AST-identical between the runner and launcher
  copies (12 defs).
- --ship-dir / Y13_SHIP_DIR: tampered ship refuses, real ship
  untouched.
- Launcher never invokes -m (exec line is `python3 -P
  run_codex_y5.py`).

## Required re-review

After findings F2-F5 are addressed, a fresh re-review of that
fix diff only is required (same scope rule as Y13r): re-run the
A4 unit table (must be 80/80) plus the A4 live probe (the 6
evade cases must refuse), the A9 tamper (direct verify must
refuse with no marker), the A3b/A3c unbrick sequences, and the
F2 launcher flow (a legit entry .pyc must be verified + deleted,
not refused as planted bytecode). Do not treat the F1 -m/import
residual as re-testable in-process: its re-test is the launcher
path (refuse pre-exec, no marker), which already passes.
