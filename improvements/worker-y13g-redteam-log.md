# Y13g redteam log: attack the Y13g FIX DIFF (431b2a9..b815590)

Worker Y13g redteam (independent Muse attacker). T0 (task received):
2026-11-22 00:05:34 +07. Scope: ONLY the Y13g fix diff (6 files).
No code modification to the fix files. No live Zen driving. No
ydotool. No em/en dashes. Work only in the repo worktree and
~/workspace/y13g-redteam/ (persistent; /tmp harnesses vanished
overnight). Never touch /usr/lib or any system path (the re.py
incident). Attack shims print a marker ONLY: no deletion, no
os.remove/unlink, no globals().update delegation, no file writes
outside the staged ship copies.

## 1. Live event log

- 00:05:34 +07 (T+0m00s): task received. Redteam the Y13g fix diff.
  Read Y13r2 redteam paper + rereview log + Y13g fix log in full.
  Fix commits: caa4a7c, 0cf43f8, 03303f4, 6cd0f7a, b815590.
  Manifest md5 0ca16ddd743acc9e28294fecd07a9c70, 27 files.
  Runner md5 db3e357f, launcher eec63492, run_live 84fa106c (pin holds).
- 00:10:30 +07 (T+4m56s): diff saved to
  ~/workspace/y13g-redteam/diff-431b2a9-b815590.txt (2015 lines),
  read in full (plan + SHIPPED.md + launcher + regen + runner
  top/verify/proven_no_body/tokenizer). Remote URL verified:
  `git remote get-url origin` returns exactly
  https://github.com/phamTuan207/computer-use-wayland.git, the
  KNOWN_REMOTE_URL in the launcher. Staging the fresh ship next.
- 00:10:54 +07 (T+5m20s): clean ship staged at
  ~/workspace/y13g-redteam/ship via regen --stage (0.5s):
  manifest md5 0ca16ddd743acc9e28294fecd07a9c70, 27 files,
  staged --verify-manifest exit 0. Regen rewrote an identical
  manifest (git diff empty). Log commit 576793a pushed,
  ls-remote matches.
- 00:11-00:18 +07 (T+6m to T+13m): A4 UNIT. Rebuilt the tokenizer
  table from the Y13r2 spec (39 cases) plus Y13g expectations
  plus 14 fresh attacks of my own. AST identity runner vs
  launcher: True (12 defs identical). Result 69/80 pass in BOTH
  copies, failures identical. All specified cases PASS: every
  -m form, flag-value form (-W/-X/--check-hash-based-pycs),
  renamed/extensionless/symlinked md5 copies, -c exec/eval,
  -- separator, attached forms, all holds, all correct
  non-matches (md5sum, -c import, echo/grep mentions, -m pytest,
  -m run_codex_y5.py, stdin). 11 fresh evasions, each proven a
  REAL execution form, not a tokenizer artifact:
  (1) -c os.system nesting: inner runner prints manifest_ok true
  (documented limit in the plan, now proven real);
  (2) -c runpy.run_path: manifest_ok true, rc 0 (real);
  (3) -c exec of a renamed copy with __file__ preset to the ship
  runner: manifest_ok true (real; bare exec crashes with NameError
  on __file__, and exec from the copy dir is refused by the scan
  as planted-py, so only the __file__-preset form reaches main);
  (4) wrappers nice, nice -n, stdbuf, taskset, sudo: all proven
  to run (NICE-OK, STDBUF-OK, TASKSET-OK, SUDO-OK);
  (5) combined flag-value forms -uW, -uX, -iuW with a separate
  value token: proven real (UW-OK, UX-OK, IUW-OK); the tokenizer
  mistakes the flag value for the script token.
  Two of my own attacks REFUTED by live proof and corrected in
  the table: "-Xu dev script" is not a runner form (-X takes the
  attached "u", "dev" is the script, proven by "can't open file
  'dev'"), and "-c runpy.run_module" is NOT viable (the module-top
  guard fires, "run as a script", proven). Both now want False
  and pass. Harness: attack_a4_unit.py + extract.py under
  ~/workspace/y13g-redteam/.
- 00:18-00:21 +07 (T+13m to T+16m): A1/A2/A3. Harness
  attack_a123.py + forge_pyc.py, 25 cases, 0 FAIL by defined
  expectations (full log a123-run1.log). A1: forged run_live .pyc
  refused rc 2, no marker, top + nested + -m. A2 direct form:
  rc 2, no marker. A2 -m form: MARKER PRINTS (rc 2, marker then
  guard message) - the documented unfixable in-process hole,
  CONFIRMED live. A2 import form: MARKER PRINTS (rc 2).
  A2b fake-OK forge via -m: marker prints + fake manifest_ok
  true, rc 0 - the gate lies via -m, CONFIRMED. A2 launcher
  script form on a forged-entry ship: refuses pre-exec rc 2, no
  marker (module-top scan). A2 launcher self-pyc: same. A2
  wrong-tag (cpython-311): rc 2, no marker. A2x isolated
  _check_entry_pyc (extracted, called directly): 8/8 - forged,
  wrong-tag, hash-based, src-path-differs forged, forged
  run_live all refuse; legit entry + legit run_live verified and
  deleted; src-path-differs LEGIT also refuses (co_filename
  differs, fail-closed, correct). A3: -m on a clean ship rc 2
  "run as a script", NO .pyc left, direct verify after rc 0;
  empty __pycache__ rc 0; env-guarded -m rc 2, writes nothing.
  A3b extra: `python3 -c "import run_live"` (no env guard) writes
  run_live.cpython-312.pyc and BRICKS verify rc 2 until manual
  re-stage (guard covers entry stems only); env-guarded import
  writes nothing, verify rc 0. A3c: `python3 -m py_compile
  run_codex_y5.py` writes the entry .pyc and BRICKS verify rc 2.
  FINDING (reachability): _check_entry_pyc is UNREACHABLE in the
  launcher flow when a .pyc exists - the module-top scan refuses
  first (proven: the A2 launcher refusal message is the scan's
  format), and check_manifest's planted walk refuses any .pyc
  before _check_entry_pyc runs in main(). It can only ever see a
  .pyc that appears between check_manifest and itself (TOCTOU
  window). The isolated test proves the function itself is
  correct; the live flow never reaches it. The SHIPPED.md/plan
  claim that the launcher "verifies the entry .pyc out-of-process
  and deletes it before exec" is not what happens on that path.
- 00:21 +07 (T+16m): log commit cda2b66 pushed, ls-remote matches.
- 00:21-00:23 +07 (T+16m to T+18m): A8 + A6. A8: _proven_no_body
  12/12 (extracted from the new runner bytes), including
  eval_error "" returning False (Amend 5 holds). A6: planted
  stdlib .py, all 15 names, BOTH forms (-P and plain), 38/38,
  marker NEVER prints. Every plant refuses rc 2 with kind
  "planted-py". Nested codex-y5/re.py refuses both forms.
  Launcher form for re/os/json refuses both forms, no marker.
  My startup-shadowing hypothesis (planted os.py executes before
  the scan in the plain form) was WRONG: CPython loads os from
  stdlib before the script dir joins sys.path, so even the plain
  form is safe. B2 is fixed more strongly than specified.
  Harness: attack_a6.py + attack_a8.py (a6-run1.log).
- 00:23-00:24 +07 (T+18m to T+19m): A9 (extra). Tampered run_live.py
  (marker print prepended, manifest untouched) on the DIRECT path:
  MARKER PRINTS, then _verify_manifest refuses rc 2 on the md5
  mismatch (direct rc=2, confirmed without a pipe). The runner
  imports run_live BEFORE verifying it, so any tampered manifest
  .py executes on the direct path. Launcher layers (extracted
  check_manifest + _check_entry_pyc + _scan_ship, real repo):
  check_manifest PASSES (ship manifest md5 unchanged),
  _check_entry_pyc passes (no .pyc), _scan_ship REFUSES rc 2 on
  the run_live.py md5 mismatch, no marker. Production path safe;
  direct path residual. _SHIP_PY path confusion
  (codex-y5/run_live.py) refuses as planted-py, no marker.
  Harness: attack_a9.py.
- 00:24-00:25 +07 (T+19m to T+20m): A7. All 5 symlink shapes refuse
  at ALL layers, 22/22 (control stripped-clean rc 0; layer 1
  scan kind "symlink" on every shape; layer 2 stripped
  _verify_manifest rc 2; layer 3 _scan_ship + check_manifest
  refuse; mixed symlink + .pyc kind "mixed"). The corrected kind
  label holds (Amend 3). Harness: attack_a7.py (a7-run1.log).
- 00:25-00:26 +07 (T+20m to T+21m): A5. Synthetic bare remotes +
  clones under ~/workspace/y13g-redteam/a5/ (own test remotes,
  never the real branch). 13/13. Case 1 fake completion PASSES
  BY DESIGN (exact subject + junk body/diff; documented
  limitation, not a pass). Case 2 other-branch refuses. Case 3
  forged old-date completion vs newer abort REFUSES by log order
  (abort is the child with committer date 2020-01-01; old %ct
  code would have PASSED). Case 4 completion-newer passes.
  Cases 5-9 refuse (no marker, unpushed, harness, body-DONE,
  non-git repo). A5-pin (real _check_remote, unpatched): attacker
  fork remote (origin = local path) refuses; KNOWN URL passes;
  KNOWN URL + trailing slash refuses (exact match); no origin
  refuses. Amend 1 holds. Harness: attack_a5.py (a5-run1.log).
  Two harness bugs of mine fixed during the run: MARKER_RE /
  ABORT_RE missing from the extraction set (NameError), and the
  case-2 setup (branch does not exist before its first commit).
- 00:26-00:28 +07 (T+21m to T+23m): A4 LIVE. Sleeper binary
  (cc-compiled) exec'd with fake argv vectors; real
  check_runner_quiet extracted from the new launcher bytes.
  24/24 in 1m51s, baseline CHECK-PASS (no fleet noise). All 14
  CAUGHT cases refused naming exactly the dummy pid (-m forms,
  -W/-X, renamed/symlink/extensionless md5 copies, flock -c,
  sh -c, bash run-nested-wayland.sh, codex+geckodriver). All 6
  fresh evasions passed the check entirely (refused=False,
  empty output): -c os.system, -c runpy.run_path, -c exec
  renamed, nice wrapper, -uW, -uX. Pass cases correct: plain
  codex warns only, mycodex-backup silent (no warning), md5sum
  mention passes. Harness: attack_a4_live.py (a4live-run1.log).
- 00:28 +07 (T+23m): --ship-dir test. Launcher with --ship-dir
  at a tampered ship (planted re.py) refuses rc 2 naming the
  tampered dir, no marker; Y13_SHIP_DIR env form identical.
  Real ship still verifies rc 0 afterwards (untouched). Amend 4
  holds. Launcher never invokes -m: the only exec line is
  `python3 -P run_codex_y5.py` (launch_y13.py line 1135); every
  other "-m" hit is a comment or the tokenizer's own -m
  detection. Dash sweep on my files: 0 em/en dashes.

- 00:30-00:31 +07 (T+25m to T+26m): redteam paper written to
  improvements/worker-y13g-redteam.md (472 lines, 23,795 bytes).
  Verdict AMEND. All 4 blockers' specified re-tests pass
  except B1's literal -m criterion (adjudicated: unfixable
  in-process, launcher control proven); all 5 amends verify.
  Findings: F1 -m/import forge executes (documented residual);
  F2 _check_entry_pyc unreachable in the live flow; F3 11 fresh
  tokenizer evasions (all proven real); F4 run_live/py_compile
  brick; F5 tampered run_live.py executes on the direct path;
  F6 marker case 1 passes by design. Dash sweep on the paper +
  log + all harness files: 0 em/en dashes. Committing now.
