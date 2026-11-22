# Y13g round-3 fix log (COORD-CLICK-5, worker C5-Y13G-R3-FIX)

Worker: C5-Y13G-R3-FIX (subagent session e7f7e026). Reports to the
coordinator only. No live runs. No browser work. Tests only.
T0 (task received): 2026-11-22 15:24:57 +07.
Repo: ~/workspace/computer-use-wayland, branch todolist-push.
Base: HEAD ab1c57d (fast-forwarded from 704a218 at 15:26 +07; the
6 fix files are unchanged since the adjudicated base 3167c76, so
the round-3 base is the adjudicated code: runner md5
d5047ff573820491263a2eb3805105f4, launcher
8e72a5ce85cbaf8382f998987e8890e5, manifest
7c76383402e4c50b28adab6b25a22e09, 27 files, run_live pin
84fa106c253d5e7f16daccf2ce3f14a5 holds).

## Sources read in full (before any edit)

- Adjudication: docs/batch13-task3-y13g-round3-adjudication-20261122.md
  (origin/main, 260 lines + fix-pass edit section). Overall verdict:
  BLOCK stands, no live run. F1, F2 HIGH upheld; verifier defect 2
  MEDIUM upheld; tokenizer (F3) and marker-ordering (F4) MEDIUM
  upheld; all LOWs upheld. No finding REJECTED outright.
- Redteam round-2 paper (167a2e9, BLOCK, F1-F7, 510 probe cases).
- Independent verifier round-2 report (75dff55, FAIL 277/280,
  defects 1-2, both in _check_entry_pyc).
- Council 1 (1e49436, AMEND, F1-F8), Council 2 (6d83401, AMEND,
  C2-1..C2-10), Council 3 (31c1126, AMEND, C3-1..C3-8).
- Fix log (ab0b62c): R2 design section (lines 420-424), worker
  admission (lines 717-720), harness-loss entry (lines 187-195).

## REJECTED sub-claims: SKIPPED, do not fix

Two sub-claims inside otherwise good reviews were REJECTED by the
adjudication. Neither is acted on in this pass:

1. Council 1, "What was verified as consistent", R2: "launcher
   scan + check_manifest exempt top-level entry .pyc (any tag)".
   REJECTED on the check_manifest half (adjudication Disagreement
   resolution 1). The module-top scan exemption at
   launch_y13.py:354-355 works and is ACCEPTED; the check_manifest
   exemption at :1197 is unsatisfiable (see F1). SKIPPED as a
   claim: I do NOT treat check_manifest as already exempting; the
   F1 one-line fix below is the correction. No separate fix exists
   for a false claim; the fix is F1 itself.
2. Redteam "What survives" claim that the Design C characterization
   is correct (the early pre-implementation Design C wording in
   the fix log, lines 43-45, said the entry-.pyc exemption was
   REMOVED from the scan and from _verify_manifest). NOT applied
   (adjudication fix-pass edit, "Reviewer corrections NOT
   applied"). The fix log's own operative R2 design section (lines
   420-424) and the worker admission (lines 717-720) say the
   opposite for the live path: exempt the 3 entry stems from the
   launcher top scan AND check_manifest so _check_entry_pyc
   adjudicates. SKIPPED: I do NOT remove the exemption per the
   early Design C wording; the round-3 fix follows the operative
   R2 design (exempt on _is_entry_pyc_rel(rel) alone at :1197),
   because removal from check_manifest would keep refusing legit
   entry .pyc at check_manifest before _check_entry_pyc runs.

Note (not a skipped fix): council 2's severity votes (C2-1 MEDIUM,
C2-3 LOW) vs redteam (F1/F2 HIGH) are resolved in favor of the
redteam ratings (adjudication resolution 3). No action follows
except that F1/F2 are fixed as HIGH items, which this pass does.

## F4 precondition, verified before switching (2026-11-22 15:26 +07)

- `git rev-list --count --merges HEAD` = 15 (matches the
  adjudication's "15 merge commits in 1234").
- Exactly 1 commit touches improvements/worker-y6c-*.md: 5a2b69d
  ("Y6c: nested v2 run BLOCKED at launch ... NO VERDICT").
- 5a2b69d IS on the first-parent leg (`git log --first-parent --
  improvements/worker-y6c-*.md` lists it; it is an ancestor of
  HEAD). Switching check_marker to --first-parent changes no live
  marker today. Precondition documented with the fix: markers
  must land as first-parent commits on todolist-push.

## Live probes run before fixing (evidence for corrected table rows)

- 2026-11-22 ~15:36 +07, staged ship /tmp/y13g-r3-ship (regen
  --stage, manifest 7c763834, verify rc 0):
  - `python3 -P -m profile run_codex_y5.py --verify-manifest`:
    rc 0, 0 manifest_ok lines, output "run as a script (python3
    run_codex_y5.py), not with -m and not via import". The guard
    fires; profile does NOT execute the suite. Council 2
    probe3_unit's m-profile=True row is REFUTED; corrected
    expectation is False.
  - `python3 -P -m timeit -n 1 -s "__file__='run_codex_y5.py'"
    "exec(open(__file__).read())"`: rc 1, NameError: name 'os'
    is not defined (at _entry_pyc_paths, line 155 of the exec'd
    code). No run. Council 2 probe3_unit's m-timeit-exec=True
    row is REFUTED; corrected expectation is False. (Matches
    council 2's own killed-leads note; the probe3_unit rows
    contradict the reviewer's live results.)
  - m-pudb: pudb is not installed on this VM, so no live proof
    either way; pudb is treated like pdb (fail-closed, debugger
    that runs a script arg with __spec__ None), expectation True.

## Fix plan (adjudication instructions 1-8, in order)

- F1: launch_y13.py:1197 drop `not rel_root and`.
- F5 + verifier defect 2: _check_entry_pyc, compile fresh with the
  cached co_filename (NO code.replace on either side), one realpath
  check at the top treating a symlinked cache dir as absent.
- F2: module-top PYTHONPATH refusal in both entry points; scrub
  PYTHONPATH/PYTHONHOME/PYTHONSTARTUP from the launcher exec env
  and the _check_entry_pyc subprocess env; correct the false
  docstring claims in both files. Residual (documented): a
  poisoned PYTHONHOME / sitecustomize.py fires at interpreter
  startup, before any module-top code runs; no in-process check
  can close that channel.
- F4: check_marker git log gains --first-parent; document the
  first-parent precondition.
- F3/C2-2/C2-10: tokenizer in BOTH copies, block kept
  AST-identical: (a) `-` after `--`; (b) -c argv/env smuggling,
  argv threaded through as the effective sys.argv, env via a new
  /proc/PID/environ reader in check_runner_quiet / preflight
  (environ None = fail-closed True for unresolvable env refs);
  (c) _SINKS extended (subprocess.getoutput/getstatusoutput,
  os.popen, full os.exec/spawn families incl. posix_spawn,
  pty.spawn, pdb.run) + inline __import__/from-import/alias
  normalization; (d) -m trace like pdb, plus pudb; -m profile /
  runpy / cProfile / timeit stay False (guard fires or no run,
  live-proved above); (e) wrappers extended (time, watch, xargs,
  ionice, chrt, numactl, systemd-run, unshare, su, runuser,
  prlimit, setarch, firejail, bwrap) + generic path-like
  unknown-wrapper / renamed-interpreter rule + hex/inf durations;
  (f) all commands in a -c string scanned, not just the first.
  Documented residuals kept: string-concatenation -c forms,
  FIFO md5 fail-open, bare-word unknown wrappers, -m bundled
  trace flags.
- F6: guard prunes empty dirs it emptied (bottom-up rmdir), both
  entry points; scan stays strict.
- F7: check_manifest walk flags any file/dir not in the manifest
  set (same allowlist _scan_ship uses).
- C1-F2: launcher __spec__ guard runs BEFORE _derive_ship_dir,
  against provisional _SHIP_DIR = dirname(abspath(__file__)).
- C3-1: _derive_ship_dir refuses --ship-dir= / --repo= tokens.
  No main() backstop (unreachable by construction, adjudication).
- C1-F1/C3-3: runner docstring lines 103/105 gain -P and --repo
  /home/james/workspace/computer-use-wayland.
- C1-F3/C3-2: SHIPPED.md "How to verify" rewritten (14 functions
  named + 4 constants + NUL-joined argv + copy-pasteable snippet
  + _fail/SHIP_DIR for _check_entry_pyc extraction).
- C2-4: missing allowlist file refuses in both module-top scans,
  check_manifest, and _scan_ship.
- C2-6: _is_codex_process matches only argv[0] basename codex or
  a /codex token in execution position (first non-wrapper token).
- C1-F7/C2-7: main exec subprocess.run wrapped (OSError,
  TimeoutExpired) into _fail.
- C2-8: ssh:// normalizes to https; all trailing slashes
  stripped; .git suffix case-folded.
- C3-4/C3-6/C3-7: refusal hints (scan fix field "files and
  directories"; _scan_ship md5 commit+push-first wording; Fix
  suffix on check_manifest and _scan_ship legs).
- C3-8: write_token moved to just after _scan_ship, immediately
  before check_token().
- Docs: C1-F5 (three entry .pyc comment), C1-F6/C3-5 (repo-tree
  wording scoped to the file-dir branch; B1 "EMPTY __pycache__
  dir only"), C2-9 (plan B1/B2/B3/LIMIT/Amend 2 corrected to the
  fixed code).
- extract_lib.py TOKENIZER_FUNCS 12 to 14 (add _m_module_is_runner
  and _is_timeout_dur); launcher_check_driver.py runner-quiet
  list gains _m_module_is_runner, _is_timeout_dur, _environ.
- Regen the manifest after any runner/launcher byte change; keep
  _SHIP_FILES identical and the tokenizer block AST-identical.

## 2. Live event log (wall-clock Asia/Ho_Chi_Minh + elapsed)

- 15:24:57 +07 (T+0m00s): task received. Read the adjudication
  (260 lines + fix-pass edit), redteam paper (373 lines), verifier
  report (314 lines), councils 1-3 (82 + 150 + 325 lines), fix log
  (873 lines). Base confirmed: HEAD ab1c57d, pins hold (runner
  d5047ff5, launcher 8e72a5ce, manifest 7c763834, run_live pin
  84fa106c). F4 precondition verified (15 merges, 1 marker
  commit 5a2b69d, on the first-parent leg).
- 15:36 +07 (T+11m): live probes on a staged ship (/tmp/y13g-r3-ship,
  regen --stage, verify rc 0): -m profile guard fires (rc 0, no
  manifest_ok); -m timeit exec NameError (rc 1, no run). Both
  probe3_unit rows refuted; corrected expectations False.
- 15:38 +07 (T+13m): harnesses staged under ~/workspace/y13g-r3/
  (persistent, never /tmp-only): verify/ (copy of
  improvements/y13g-verify/), redteam/ (attack_a*.py + forge_pyc.py
  + fresh_ship.py + extract.py + confirm_pycompile.py from
  ~/workspace/y13g-r2-redteam/), probes/ (council-2 probe3_unit,
  probe3live, probe3live_fix, probe6_7_8_9, r2common).

## 3. Work completed after the plan (15:38 to 16:38 +07)

- Runner remaining fixes: C2-4 missing-file check in the runner
  module-top scan; C3-4 scan fix hint ("files and directories");
  C1-F5 _verify_manifest comment now "three entry .pyc files
  (0, 1, 2, or 3)"; preflight reads /proc/<pid>/environ
  (NUL-separated, try/except to None) and passes it to
  _is_runner_cmdline. Launcher: _environ(pid) helper added;
  check_runner_quiet passes it.
- Docs done: SHIPPED.md rewritten (How to verify, marker
  --first-parent ordering + precondition, repo-tree scoping,
  handover-token line, Files/md5 list); plan B1/B2/B3/B4/Amend
  1/2/4 corrected to the fixed code (C2-9) + a new "Y13g round 3"
  section with the behavior changes for the re-verifier.
- Regen + restage verified rc 0; _SHIP_FILES identical (29)
  in both files; tokenizer block AST-identical (14 functions).

### 3a. Harness bugs found during the battery runs (all in my
### code or the harness, fixed before re-running)

- launcher_check_driver.py was missing _normalize_remote_url
  from the manifest/marker extraction lists: A5 ran 0/10 and
  clean_ship 4/6 with NameError. The verifier's round-2 report
  (75dff55, "Harness bugs" section) records the SAME bug ("A5
  first run 0/10") fixed in their working tree but never
  committed; my fix is the same one (add the helper to both
  lists, repo copy + R3 copy). A5 now 10/10.
- Same driver was missing _is_exempt_cache_dir,
  _is_entry_pyc_rel, _ENTRY_STEMS for check_manifest (my F7
  rewrite calls them): added to the manifest list (both
  copies). The A7 redteam harness had the same gap: added the
  three names to its extraction set.
- A2L redteam harness WANTED missed _environ, _is_entry_pyc_rel,
  _is_exempt_cache_dir, _ENTRY_STEMS (all called on the main()
  path after the R3 rewrite): added.
- attack_a4_live.py WANTED missed _environ: added.
- Redteam fresh_ship.py still pointed at the R2 base
  (~/workspace/y13g-r2-redteam, manifest 7c763834): repointed
  to the R3 base (~/workspace/y13g-r3/redteam/ship, manifest
  d2a2bf08). plant_so.c and sleeper.c were missing from the R3
  redteam dir: copied from the R2 dir.
- Probes r2common.py still staged from the R2 council-2 ship:
  repointed CLEAN/WORK to ~/workspace/y13g-r3/probes/ship
  (new bytes) and the plant_so.c path to the R3 redteam copy;
  probe3live.py's stdin source path updated the same way;
  direct_verify/launcher_scan_only now use -P -E.

### 3b. C2-4 double-flag fix (found by redteam A7)

- The C2-4 missing-file check flagged symlinked allowlist
  files as "missing-file" AND the walk flagged them as
  "symlink", so the scan kind came out "mixed" instead of
  "symlink" (A7 shapes 2/4 failed). Fixed in all four places
  (runner scan, launcher scan, check_manifest, _scan_ship):
  only a genuinely absent path, or a non-file non-symlink in
  its place, is "missing-file"; a symlink is left to the
  walk's "symlink" kind. A7 now 36/36 (redteam) and 10/10
  (verifier).

### 3c. F2 completion: -E closes the startup channel

- After the adjudication-exact F2 fix (module-top PYTHONPATH
  refusal + env scrub), redteam A6 still failed 3 cases:
  functools, collections, warnings plants via PYTHONPATH in
  the DIRECT runner form. Root cause, live-proved 2026-11-22
  ~16:20 +07: the interpreter itself imports warnings (then
  re/functools/collections) at startup, before any module-top
  code runs, resolving them via PYTHONPATH. `PYTHONPATH=/tmp/pp-test
  python3 -P -c "print('main runs')"` prints the plant markers
  for warnings and functools before main runs; with -E, no
  plant executes. The adjudication's exact fix cannot close
  this channel (it names PYTHONHOME/sitecustomize as the
  residual, same startup class); the task requires planted code
  to not execute in either entry point, so the documented
  invocation form is now `python3 -P -E` in both entry points:
  docstrings, SHIPPED.md, regen script (docstring + verify
  subprocess argv), plan B2, launcher exec argv, and the
  _check_entry_pyc fresh-compile subprocess argv. The
  module-top PYTHONPATH refusal stays as defense-in-depth for
  an invocation without -E. Residual, documented: without -E,
  a PYTHONHOME/sitecustomize plant, or a PYTHONPATH plant of a
  startup-imported name (warnings, functools, collections),
  executes at interpreter startup; the run still does not
  proceed (functools/warnings reach the module-top refusal
  rc 2; collections kills startup during site/.pth processing
  rc 1). A6 records this with 3 explicit residual cases
  (A6pp-runner <name> -P without -E) and 16 -P -E cases.
  A6 now 120/120.

### 3d. Harness expectations flipped to the fixed behavior

- probe3_unit: m-profile True to False, m-timeit-exec True to
  False (live-proved 15:36 +07).
- Redteam A5-pin: "known URL double slash" False to True,
  "ssh:// form" False to True (C2-8 normalizes both).
- Redteam A2L: all 6 finding cases flipped to R3 behavior
  (legit .pyc verified + removed rc 0; forged refuses by
  marshal comparison "entry .pyc mismatch").
- Redteam A123: src-path-differs legit refuse to delete (F5);
  py_compile relpath refuse to verify + delete (F5); A3d
  guard-prunes-subdir now verify rc 0 (F6); moved-ship label
  updated (F5 verifies).
- Redteam A4-live: 19 "want evade" cases flipped to "caught"
  (F3); split-concat stays "evade" (documented residual).
- Redteam A4-liveforms: chrt -f now SKIP-probed (no CAP_SYS_NICE
  on this VM; -o/-i/-b covered in liveforms2); watch now runs
  with TERM=xterm (was "Error opening terminal: unknown");
  pdb.run __file__ preset now pipes "continue" (was stuck at
  the (Pdb) prompt). liveforms2 pty watch rewritten: outer
  `timeout 6` (TERM only) around script + read the typescript
  FILE (inner timeout breaks watch's curses draw under a pty;
  a KILL leaves a 0-byte typescript because script only
  flushes on clean exit).
- Council-2 probe6_7_8_9: P6 grep-codex-path / echo-slash-codex
  / ls-slash-codex True to False, env-codex False to True
  (C2-6); P7 ssh-url-form / double-slash / dot-git-upper False
  to True (C2-8).
- A5b has no committed script (verifier report cites
  results/a5b.log only); its coverage is subsumed by P7 (20
  normalization cases) + redteam A5-pin (15 _check_remote
  cases).

## 4. Final battery results (2026-11-22 16:36-16:38 +07, final bytes)

Final pins: runner md5 510336331de0e93c06c3195d52fac51f,
launcher md5 3ac1b74524b5f3a6518787f808d5a2f2, manifest md5
d2a2bf08ae1c942f9bd888793ef7eb2e, 27 files, _SHIP_FILES 29
in both files, tokenizer block AST-identical (14 functions).

Verifier (~/workspace/y13g-r3/verify/):
- attack_a2.py: A2 DONE 11/11 pass in 2.0s
- attack_a3.py: A3 DONE 7/7 pass in 1.5s
- attack_a4_unit.py: A4-UNIT DONE 39/39 pass in 0.1s
- attack_a4_live.py: A4-LIVE DONE 6/6 pass in 2.3s
- attack_a5.py: A5 DONE 10/10 pass in 4.4s
- attack_a6d.py: A6d DONE 18/18 pass in 2.3s
- attack_a7.py: A7 DONE 10/10 pass in 1.9s
- attack_a8_ast.py: A8-AST DONE 27/27 pass in 1.6s
- clean_ship.py: CLEAN-SHIP DONE 5/6 pass in 2.3s (the 1 FAIL
  is the manifest dry run: ship md5 d2a2bf08 != committed
  7c763834, expected until this fix is committed + pushed;
  re-run after push)

Redteam (~/workspace/y13g-r3/redteam/):
- attack_a123.py: TOTAL 43 cases, 0 FAIL
- attack_a4_unit.py: SPEC 80/80, EXTRA 49/49, FRESH 26/29
  (3 FAIL are the documented residuals: 2 split-concat exec,
  1 FIFO stream fail-open)
- attack_a5.py: TOTAL 32 cases, 0 FAIL (merge cases 10/11
  pass with real assertions: case 10 REFUSE, case 11 PASS)
- attack_a6.py: TOTAL 120 cases, 0 FAIL (16 PYTHONPATH -P -E
  cases + 3 -P-only documented residuals + ship-dir plants)
- attack_a7.py: TOTAL 36 cases, 0 FAIL
- attack_a8.py: TOTAL 14/14 pass
- attack_a9.py: TOTAL 7 cases, 0 FAIL
- attack_a4_live.py: TOTAL 59 cases, 0 FAIL
- attack_a4_liveforms.py: TOTAL 31 cases, 0 FAIL
- attack_a4_liveforms2.py: TOTAL 6 cases, 0 FAIL

Council-2 probes (~/workspace/y13g-r3/probes/):
- probe3_unit.py: P3-UNIT SUMMARY 63/63 correct; copies
  disagree on none; MISSES []
- probe6_7_8_9.py: P6-P9 SUMMARY 48/48 pass
- probe3live.py / probe3live_fix.py: live proofs on the new
  ship (manifest d2a2bf08); EXECUTES forms match the unit
  True rows; m-profile/m-timeit-exec NO-RUN (guard fires /
  NameError), m-pudb not installed on this VM (fail-closed
  True by analogy with pdb).

NOT yet run (blocked on commit + push): redteam A2L
(attack_a2_launcher.py, 7 cases: clean ship + legit/forged
entry .pyc through the real launcher main; the manifest pin
refuses until the new manifest is committed + pushed) and
the clean_ship manifest dry run above. Re-run both after
push and record here before declaring re-verification ready.

## 5. Files changed (commit with explicit pathspecs only)

- tests/realistic/run_codex_y5.py
- tests/realistic/launch_y13.py
- tests/realistic/codex-y5-manifest.json
- tests/realistic/codex-y5/SHIPPED.md
- tests/realistic/regen_codex_y5_manifest.py
- improvements/worker-y13-codex-y5-live-plan.md
- improvements/y13g-verify/extract_lib.py
- improvements/y13g-verify/launcher_check_driver.py
- improvements/worker-click5-y13g-r3-fix-log.md (this file)

Do NOT stage or commit the sibling worker's files:
tests/cdp_validation.mjs (C5-STEP9) and the untracked
improvements/c5-step9-runs/, improvements/worker-click5-step9-log.md,
improvements/codex-discuss-prompt*.md,
improvements/multi-agent-deliberation-idea-20261121.md,
improvements/muse-coordinate-accuracy-20261120.md,
improvements/worker-y14b-fix6-redteam.md.
