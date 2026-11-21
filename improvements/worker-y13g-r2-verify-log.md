# Independent re-verification log: Y13g ROUND-2 fix diff (R2 verifier)

- Verifier: independent Muse subagent (depth 2). Did NOT write the fix.
- Parent: Worker Y13g (session b58d1a36). Report:
  improvements/worker-y13g-r2-verify-report.md (this log's sibling).
- Repo: ~/workspace/computer-use-wayland, branch todolist-push.
- Scope: ONLY the round-2 diff (commits 0639d04, 87eec47, 6ba43f2,
  8bdd5aa, 5a9b9e8). No fix file edited. No live Zen driving. No
  ydotool. No em/en dashes. Never touched /usr/lib or any system
  path.
- Harnesses: improvements/y13g-r2-verify/ (committed). Staged
  ships + result logs: ~/workspace/y13g-r2-verify/ (persistent,
  never /tmp-only).
- All times wall-clock Asia/Ho_Chi_Minh + elapsed per test.

## 2026-11-22 01:00:42 +07 (T+0m): START, pins verified FIRST

- Branch todolist-push, HEAD 334cf69 at start.
- python3: 3.12.3.
- md5 tests/realistic/run_codex_y5.py = d5047ff573820491263a2eb3805105f4
  (pin d5047ff5 holds).
- md5 tests/realistic/launch_y13.py = 8e72a5ce85cbaf8382f998987e8890e5
  (pin 8e72a5ce holds).
- md5 tests/realistic/codex-y5-manifest.json =
  7c76383402e4c50b28adab6b25a22e09 (pin 7c763834 holds, 27 files).
- run_live.py: manifest records 84fa106c253d5e7f16daccf2ce3f14a5
  (the 1e3901c pin); working-tree file md5 is
  d8e2b14d7456b2866790f4a87ec1919e (91d3cd2 changed HEAD). BY DESIGN:
  the regen script stages run_live.py from `git show
  1e3901c:tests/realistic/run_live.py`, never from the working
  tree (commit 9564304). Verified below: all 27 manifest md5s
  match the working tree except run_live.py, which matches the
  pinned commit bytes instead.
- Round-2 commit scope: each of 0639d04, 87eec47, 6ba43f2, 8bdd5aa,
  5a9b9e8 touches only the 6 fix files (runner, launcher, plan,
  manifest, SHIPPED.md, regen). The wider range also shows
  worker-y13g-fix-log.md from the log commit 6cf7166, which is
  not one of the 5 fix commits.
- Raw tokenizer-block text diff (runner vs launcher, # Y13g B3
  through _is_codex_process): exactly 4 lines, the 2 sync notes.
  The CODEX comment block (Keep in sync with <counterpart>)
  differs only in the counterpart filename. Both checked
  mechanically in the A8/AST battery.

## 2026-11-22 01:0x +07: harness build (T+?m)

- Copied the round-1 harnesses (improvements/y13g-verify/) into
  improvements/y13g-r2-verify/ and adapted them for round 2:
  WORK dir ~/workspace/y13g-r2-verify, manifest pin 7c763834,
  14 tokenizer functions, new R2 cases per battery (see the
  report for the full list). New: attack_a5b.py (remote-URL
  normalization), .so plant compilation in attack_a6d.py from
  the council-2 probe plant_so.c.
- Clean ship staged with the regen script: exit 0,
  {"manifest_ok": true, "files_checked": 27, "mismatches": [],
  "manifest_md5": "7c76383402e4c50b28adab6b25a22e09"}. Regen
  rewrote the manifest file; git shows NO diff (bytes
  identical to committed). Staged run_live.py md5 is
  84fa106c253d5e7f16daccf2ce3f14a5 (the 1e3901c pin); staged
  runner d5047ff5, launcher 8e72a5ce. All 14 harness files
  py_compile OK; sleeper built (gcc -O2).
- Commit: harness + this log start (small commit 1).
## 2026-11-22 01:08:26 +07 (T+8m): A2 19/19 PASS (after 2 harness fixes)

- First run 16/18: A2j runner-scan assertion too narrow (kind
  "mixed", not "pyc", because the nested dir is itself an
  unexpected dir; refusal + no marker held) and A2l expectation
  wrong (the -m guard deletes the nested .pyc but leaves the
  EMPTY __pycache__/sub dir, which the scan refuses as
  unexpected-dir). Both are harness-expectation errors, not fix
  failures: a -m/import probe only ever writes TOP-LEVEL .pycs
  (empty top-level __pycache__ IS exempt), so a nested dir can
  only appear by hand, and refusing it is fail-closed tamper
  evidence. Corrected the harness (A2j accepts kind mixed/pyc
  with the .pyc listed; A2l asserts the residue refusal, then
  deleting the empty dir restores rc 0) and re-ran: 19/19 PASS
  in 3.5s (results/a2.log). New R2 cases all pass: legit .pyc
  accepted + deleted (A2h), forged .pyc exempt from launcher
  scan (A2i, reaches Y13_GO check), nested forge refused at
  both scans (A2j), pypy-tag forge refused (A2k), nested legit
  deleted by the -m guard (A2l).

## 2026-11-22 01:09:17 +07 (T+9m): A4 unit 81/81 PASS

- 39 original + 42 new R2 cases, both copies agree on every
  case (results/a4_unit.log, 0.2s). All new forms behave as
  specified: -uc/-Bc/-um/-Bum, -uW/-uX/-iuW, -m pdb + script
  (True) vs -m runpy/-m cProfile (False), python3 - stdin
  (True), timeout 60s/1m/1.5m/90. (True), bash -c glued ;/&&
  (True), -c os.system / runpy.run_path / exec of renamed copy
  (True, incl. __file__ preset), wrappers nice/stdbuf/taskset/
  sudo/uv run (True), exec -a (True), pypy3 (True); mere
  mentions NOT caught: -c import, echo/grep, md5sum.

## 2026-11-22 01:09:21 +07 (T+9m): A8/AST 27/27 PASS

- A8 12/12: eval_error None now returns False (R9), "" still
  False, all other rows as specified. AST 14/14 functions
  identical docstring-stripped. Raw block diff (extended
  through the CODEX comment) = exactly 6 lines: the 2 sync
  notes (4 lines) + the CODEX comment (2 lines), all naming
  the counterpart file (results/a8_ast.log, 1.6s).

## 2026-11-22 01:10:19 +07 (T+10m): A3 17/19, ONE ROOT CAUSE FAILS

- A3g bare -m (no -P): guard fires first, rc 2, no .pyc left.
  A3i import run_live self-heals fully (refuse, entry-pyc
  deletes, rc 0).
- A3h FAIL (2 checks, 1 root cause): a LEGITIMATE entry .pyc
  produced by relative-path `python3 -m py_compile
  run_codex_y5.py` (run from inside the ship dir, the natural
  form) is REFUSED by _check_entry_pyc (rc 2, .pyc not
  deleted), so the ship does NOT self-heal to direct verify
  rc 0. Root cause proven mechanically: the cached code object
  has co_filename "run_codex_y5.py" (relative, as invoked)
  while the fresh compile uses the absolute ship path; consts,
  names, and code bytes are IDENTICAL, marshal equality fails
  ONLY on co_filename. Control A3h-abs PASSES: absolute-path
  py_compile is accepted + deleted + rc 0. The documented
  self-cache path (-m/import, absolute filenames) is
  unaffected (A2h, A3i). The failure is FAIL-CLOSED (refuse +
  "re-stage the ship", no forged code executes) with trivial
  recovery (delete the .pyc, re-stage). It is a real false
  refusal of a legitimate .pyc, not a harness artifact: the
  specified battery ("py_compile must self-heal to direct
  verify rc 0") is NOT met in its natural form. Round-3 fix
  shape: normalize co_filename in the marshal comparison
  (e.g. code.replace(co_filename=src) on both sides).

## 2026-11-22 01:10:46 +07 (T+10m): A6d 66/66 PASS

- 15 .py names -P (kind planted-py) + 3 no-P (safe_path
  refusal, no scan JSON) + 16 .so stems x 3 forms (runner -P
  kind unexpected-file, runner bare safe_path, launcher -P
  tampered-ship), marker never printed / marker file never
  created (results/a6d.log, 11.3s). Control: a direct import of
  the built glob .so plant writes SO-EXECUTED, proving the
  plants were armed and the refusals are what kept them from
  executing. The shlex stem is covered in all 3 forms.

## 2026-11-22 01:11:46 +07 (T+11m): A7 13/14, ONE ROOT CAUSE FAILS

- 5 original shapes x 2 layers all pass (kind symlink).
- Shape 6 (symlinked __pycache__ -> outside dir holding a
  FORGED entry .pyc): direct verify refuses kind symlink; the
  launcher scan refuses "symlink dir in ship: __pycache__";
  _check_entry_pyc refuses the forged outside .pyc rc 2 with
  the file intact (it sees it via os.listdir and the marshal
  comparison refuses before any delete).
- A7 shape-6b FAIL: _check_entry_pyc DELETES a LEGITIMATE
  .pyc OUTSIDE the ship when __pycache__ is a symlink to an
  outside dir (proven twice: manual probe + harness re-run;
  driver rc 0 "verified + removed", outside file gone). Root
  cause: _check_entry_pyc uses plain os.listdir(cache_dir) +
  os.unlink and never applies the realpath-inside-ship check
  that _entry_pyc_paths (the -m guard helper) has. R4 claims
  symlink safety ("the guard never deletes a file OUTSIDE the
  ship"), but that property holds only for the guard helper,
  not for the function that deletes files during launch
  checks. Reachability in the production flow is LIMITED: the
  launcher module-top scan refuses a symlinked __pycache__
  before main() runs _check_entry_pyc, so the normal sequence
  cannot reach it; the gap is defense-in-depth (any caller
  that reaches _check_entry_pyc without the scan, or a future
  scan bypass, deletes outside files). Damage scope is also
  narrow: only a file named <entry-stem>.*.pyc in the linked
  dir, and only when its bytes match a fresh compile. Still
  a real defect against the R4 spec: the fix is one realpath
  check at the top of _check_entry_pyc (return [] / refuse
  when realpath(cache) is outside the ship dir, mirroring
  _entry_pyc_paths).
