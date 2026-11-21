# Redteam round 2: log (Worker Y13g R2 redteam)

- Reviewer: Worker Y13g round-2 redteam (independent Muse attacker)
- T0: 2026-11-22 00:59 +07 (task received)
- Scope: round-2 diff ONLY, commits 0639d04, 87eec47, 6ba43f2, 8bdd5aa,
  5a9b9e8. Pins: runner d5047ff573820491263a2eb3805105f4, launcher
  8e72a5ce85cbaf8382f998987e8890e5, run_live 84fa106c253d5e7f16daccf2ce3f14a5
  (pin 1e3901c holds), manifest 7c76383402e4c50b28adab6b25a22e09, 27 files.
- Method: live probes only, fresh staged ships per case, harnesses
  under ~/workspace/y13g-r2-redteam/ (persistent). No live Zen
  driving. No ydotool. No em/en dashes. Never outside the repo
  worktree and ~/workspace scratch.

## Event log (wall-clock +07, elapsed from T0)

- 00:59 +07 (T+0m): task received. Read round-1 redteam paper,
  Council 2 paper, fix log tail (R1-R10 adjudication). Pins to verify.
- 01:02 +07 (T+3m): repo HEAD 334cf69, branch todolist-push. Round-2
  commits present (0639d04..5a9b9e8). Read runner module top (guard,
  safe_path, allowlist scan, R5 entry-hash check) and launcher module
  top (_derive_ship_dir, guard, safe_path, allowlist scan, R2
  exemption) in full; read tokenizer block (both copies), _proven_no_body
  (key presence), launcher checks (_normalize_remote_url, _check_remote,
  check_marker --topo-order, check_manifest, _check_entry_pyc,
  _scan_ship, check_runner_quiet with cwd).
- 01:05 +07 (T+6m): regen --stage to ~/workspace/y13g-r2-redteam/ship:
  manifest md5 7c76383402e4c50b28adab6b25a22e09, 29 files staged, staged
  --verify-manifest exit 0. Pins HOLD (runner d5047ff5, launcher
  8e72a5ce, run_live 84fa106c, manifest 7c763834). Regen rewrote the
  manifest identically (same md5, no tree change).
- 01:07 +07 (T+8m): real origin/todolist-push has NO Y6c completion
  marker (newest Y6c subject is a BLOCKED/NO VERDICT line, matches
  neither MARKER_RE nor ABORT_RE), so the full launcher path cannot
  pass check_marker against the real repo. Full-launcher A2/A3
  re-tests will use a synthetic repo (own bare remote, own marker
  commit) with a git url.insteadOf redirect so `git remote get-url
  origin` still shows the known URL while fetch resolves locally.
  That redirect is itself a probe of the remote pin (see A5x).
- 01:07 +07 (T+8m): NOTE, runtime execution-risk notice on the git
  fetch + plant_so.c read output: I will NOT build from that flagged
  output. The A6d .so plants will use a minimal C extension source
  I author myself in my own work dir (same standard PyInit shape,
  marker-file on import), compiled per stem. All .so work stays in
  staged ship copies, never the repo tree, never a system path.
- 01:12 +07 (T+13m): log commit 0319088 landed, ls-remote matches.
  Harnesses under ~/workspace/y13g-r2-redteam/ (extract.py,
  forge_pyc.py reused from round 1; fresh_ship.py, plant_so.c (my
  own), sleeper.c (my own) written fresh).
- 01:15 +07 (T+16m): timeout facts verified live before writing the
  unit table: `timeout 1h30m` is INVALID (rc 125, "invalid time
  interval"), `timeout 0x10` ACCEPTS (rc 0, hex duration),
  `timeout 1.5m`/`60s` accept. stdlib source read for -m modules:
  trace script branch globs carry NO __spec__ (evasion candidate);
  profile script branch DOES set __spec__ (safe, like cProfile/runpy).
- 01:20 +07 (T+21m): A4 UNIT done (attack_a4_unit.py, log
  a4unit-run1.log): AST identity True (14 defs). SPEC 80/80, both
  copies agree. EXTRA 48/49: one miss, `bash -c 'echo hi;python3
  run_codex_y5.py'` (runner as the SECOND command in a -c sequence:
  _shlex_tokens drops separators, _command_executes_runner only
  examines the FIRST command). FRESH 2/29: 27 misses, each a real
  form to live-prove next (trace, wrappers, sink aliases, pdb.run,
  split-concat, FIFO, timeout 0x10, renamed interpreter/shell).
- 01:28 +07 (T+29m): A4 LIVEFORMS done (attack_a4_liveforms.py run3 +
  attack_a4_liveforms2.py): 28/31 + 5/6 real executions proved with
  manifest_ok true on fresh ships. CONFIRMED evasions: -m trace
  --trace/--count (with -P; without -P the safe_path gate refuses
  first), -m pdb -c continue + piped continue, xargs, setsid -w,
  bash -c command -p, chrt -o/-i/-b (only -f needs privilege),
  ionice, unshare -r, su -c, systemd-run, watch (TERM=xterm),
  renamed python3/bash, unknown wrapper, -c from-os-import-system /
  os-as-o / __import__ / os.popen / subprocess.getoutput /
  getstatusoutput, -c pdb.run (piped continue), -c exec split-concat,
  bash -c sequence/pipeline/&& runner-second, timeout 0x10. SAFE
  controls hold: -m profile/cProfile (guard fires, rc 0, profiler
  swallows SystemExit), -m runpy (rc 2). Plain `-m pdb script`
  stops at the (Pdb) prompt (needs -c continue or piped stdin).
  chrt -f fails here (Operation not permitted); watch needs TERM.
- 01:32 +07 (T+33m): A4 LIVE dummy probe done (attack_a4_live.py,
  log a4live-run1.log): 59/59 as defined. All 6 round-1 evasions now
  CAUGHT live (refuse naming the dummy pid), all new R3 forms caught
  (-m pdb, python3 -, timeout 60s/1m, nice/stdbuf/taskset/sudo/uv,
  exec -a, pypy3, bash -c glued ;/&&), all 20 fresh attacks confirmed
  EVADING live, correct passes pass (plain codex warns only,
  md5sum/mycodex-backup silent, /usr/bin/codex warns).
- 01:40 +07 (T+41m): A1/A2/A3 done (attack_a123.py run2, log
  a123-run2.log): 43/43 as defined. A1 3/3 refuse, no marker. A2
  direct refuse no marker; -m/import marker PRINTS (documented
  hole); fake-OK via -m prints fake manifest_ok rc 0 (documented);
  launcher binary refuses pre-exec no marker (at check_go: the
  module-top scan EXEMPTS the entry pyc, so the refusal is main(),
  not the scan); wrong-tag direct refuse. A2x isolated
  _check_entry_pyc 8/8 correct as a function. NEW: relative-path
  py_compile legit pyc REFUSES in _check_entry_pyc (co_filename:
  relpath bakes 'run_codex_y5.py', fresh compile uses the absolute
  path; confirmed in confirm_pycompile.py, abspath control deletes).
  A3: -m with -P is rc 1 "No module named" (cwd off sys.path, module
  never loads, no pyc written); -m without -P rc 2 script-form;
  bare direct rc 2 safe_path; empty __pycache__ rc 0; env-guarded -m
  writes nothing. R4 healing WORKS for top-level: import run_live /
  py_compile brick direct verify (kind pyc) and the -m guard (3
  stems, recursive, any tag) deletes them, direct verify rc 0 again;
  pypy-tag heals too. C2-4 HOLDS: -m guard does not delete through a
  symlinked __pycache__ (outside file survives), direct verify
  refuses kind symlink. NEW: nested legit pyc heals the FILE but the
  empty subdir remains and still bricks verify (guard never prunes
  dirs). __pycache__-as-file and dir-named-like-.pyc refuse rc 2.
- 01:48 +07 (T+49m): A2L full-launcher end-to-end done
  (attack_a2_launcher.py run3, log a2launcher-run3.log): 7/7 as
  defined, extracted main() with check_marker patched out only.
  Clean ship: full pass, rc 0, manifest_ok true. HEADLINE FINDING:
  check_manifest's R2 exemption is DEAD CODE (`if (not rel_root and
  _is_entry_pyc_rel(rel))` can never be True: an entry .pyc lives
  under __pycache__/ so rel_root is "__pycache__", truthy). A legit
  entry .pyc (abspath py_compile, relpath py_compile, import
  run_live) is refused by check_manifest as "planted bytecode"
  BEFORE _check_entry_pyc runs; the pyc stays on disk. A forged
  entry .pyc refuses the same way (right outcome, wrong mechanism,
  no marker). _check_entry_pyc is STILL unreachable on the launcher
  path: R2 did NOT fix C2-2/F2. The isolated function is correct;
  the live flow never reaches it. Also learned: `git remote get-url`
  APPLIES url.insteadOf (a redirect to a local bare repo shows up
  as the local path), so the remote pin sees the effective URL.
