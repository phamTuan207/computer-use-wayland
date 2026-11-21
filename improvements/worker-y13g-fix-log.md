# Y13g fix log: Y13r2 BLOCK (B1-B4 + 5 amends)

Worker Y13g, Muse fixer. T0 (task received): 2026-11-21 22:56 +07.
Scope: fix the 4 blockers + 5 amends from Y13r2's re-review
(commits 08014a0..2fee242, verdict BLOCK) using the PRECISE fixes
in improvements/worker-y13r2-redteam.md. Council (3) + redteam over
the fix diff; independent verifier runs all re-tests (generator
never runs its own tests). Commit small and many on todolist-push,
verify via ls-remote. Log discipline (owner rule 22:47): every
event appended here as it happens, wall-clock + elapsed, nothing
omitted. Never ydotool. No em/en dashes. No live Zen driving.
NEVER touch /usr/lib or any system path (the re.py incident: a
redteam shim deleted /usr/lib/python3.12/re/__init__.py). Work only
in the repo worktree and /tmp test copies.

## 1. Live event log

- 22:56 +07 (T+0m00s): task received. Y13r2 BLOCK: B1 forged entry
  .pyc via -m/import (fake-OK forge makes verify lie); B2 planted
  stdlib .py executes at import before the scan (9/15); B3
  tokenizer misses -m/flag-value/renamed/-c forms; B4 -m bricks
  verify/live until manual deletion; 5 amends (remote pin, -c FP +
  codex warning noise, scan JSON key, hardcoded SHIP_DIR,
  eval_error "" edge).
- 22:56-23:00 +07 (T+0m to T+~4m): read sources in full. Redteam
  paper (33,442 B, all sections incl. blockers + amends + re-test
  specs), Y13r2 log head, run_codex_y5.py top (imports + scan +
  _ENTRY_PYC), _verify_manifest (lines 456-552), tokenizer
  (3565-3660), _proven_no_body (961), preflight runner-quiet
  (3740+), launch_y13.py in full, regen script in full.
  Repo state: branch todolist-push, HEAD 0b8936e. Working tree has
  other workers' modifications (F3/OPT/Y14b logs, cursor_session.py,
  run_batch3.py) which I do NOT touch. Manifest: 27 files, md5
  f27c03020c9866cfa0dcd637df6f8647; runner 3cc5fa11, launcher
  2b02c5ec, run_live 84fa106c (pin 1e3901c).

- 23:00-23:20 +07 (T+4m to T+24m): design adjudication (written
  before any edit). Read Council 2's AMEND list (6 items) in full;
  it goes further than the redteam paper in places, and the two
  sources are in tension on the entry-.pyc exemption. Resolution
  below is the design I implement; council + redteam + independent
  verifier will judge it.
  - B1/B4 DESIGN C (strict scan, guard cleanup, no blind
    exemption): (a) Scan refuses ANY .pyc, ANY symlink, ANY
    unexpected .py; the blind _ENTRY_PYC exemption is REMOVED
    from the scan and from _verify_manifest (redteam B1(1) + C2
    AMEND 1(c)). (b) The -m guard (B1(3)) deletes the two entry
    .pyc paths (best effort) before exiting 2, so a -m/import
    probe does not brick the ship; this is the mechanism that
    makes B4's "direct form after -m is rc 0" true WITHOUT any
    exemption. (c) _verify_manifest exempts a __pycache__ dir
    from the "unexpected directory" refusal ONLY when it holds
    only entry .pyc files (0, 1, or 2) and nothing else; the
    files inside are still refused as bytecode (no per-file
    exemption). This keeps an empty __pycache__ (left by a probe)
    from bricking verify (B4 re-test) and is paired, as C2 AMEND
    2 requires, with removal of the file exemption AND the
    launcher-side full scan. (d) Launcher out-of-process check
    (B1(4)): before exec, compile each entry .py fresh in a
    separate python -P subprocess and compare marshalled code
    against the cached .pyc; refuse on mismatch, then delete
    ONLY the two entry .pyc paths (B4(2)). (e) Documented limit:
    a forged entry .pyc invoked DIRECTLY via -m/import executes
    (the forged bytecode IS the running code; C2-1 states this
    is unfixable in-process). The control is the launcher check
    + never invoking -m/import on an unverified ship; -m and
    bare imports are unsupported forms (SHIPPED.md + docstrings).
    The B1 re-test "-m/import form, no marker" is therefore
    tested THROUGH the launcher check (refuses, no marker), not
    by invoking -m on a forged ship (which no legitimate flow
    does). The B4 re-test "-m cases" are asserted as: -m exits 2
    with the "use script form" message, no .pyc is left behind,
    direct verify after is rc 0.
  - B2: PYTHONSAFEPATH=1 (python3 -P) in the launcher exec env +
    launch line; narrow top scan (sys/os only, no json/pathlib)
    in BOTH entry points before any other import; scan refuses
    .pyc/symlink/unexpected-.py; launcher full-allowlist scan
    before exec (C2 AMEND 1(a)); check_manifest refuses planted
    files (any top-level .py/.pyc/symlink not in the manifest).
  - B3: C2 AMEND 3 real python-argv parse (first positional
    after skipping flags and their values; -m module set incl.
    run_agyq2/run_batch3/run_agy_y2/run-nested-pill/hand_drive_e1;
    -c via shlex.split + trailing ; & | strip; python -c code
    checked for runner .py basenames so exec(open(...)) is
    caught and import is not; shell -c parsed recursively) +
    redteam B3(4) md5 check (resolve script token to real path,
    compare against manifest .py md5s; optional cwd param from
    /proc/<pid>/cwd). Bare module names count as script
    candidates (extensionless case). AST-identity between the
    two copies.
  - AMEND 1: remote URL pin (https://github.com/phamTuan207/
    computer-use-wayland.git, read from the real checkout) in
    check_marker + check_manifest; marker documented as a
    coordination signal, not authentication; marker ordering by
    git log position (C2 AMEND 5(a)), not %ct, so a forged old
    date cannot beat a genuinely newer abort.
  - AMEND 2: warning branch matches the codex executable
    basename only; refuse branch unchanged.
  - AMEND 3: scan JSON {"refused": true, "kind": ..., "files":
    [...]} (kind pyc/symlink/planted-py/mixed); no parser keys
    on pyc_refused (grep: only the runner itself printed it).
  - AMEND 4: SHIP_DIR from --ship-dir flag, else Y13_SHIP_DIR
    env, else dirname(__file__) if it holds run_codex_y5.py +
    manifest, else the hardcoded fallback; documented.
  - AMEND 5: _proven_no_body uses `diag.get("eval_error") is
    not None` ("" now returns False; unreachable today, hardened).
  - VERIFIER NOTE: importing run_codex_y5.py now exits 2 (the
    -m guard); the verifier must AST-extract tokenizer
    functions (as Y13r2 did) or test via subprocess. The
    generator (me) runs only py_compile as a build sanity check;
    ALL pass/fail evidence comes from the independent verifier.

- 23:18 +07 (T+22m): STATUS CHECK from Muse: log had no commit in
  18+ min. Appending progress now and committing the log
  immediately. Done so far: full source read (redteam paper,
  Y13r2 log, runner top/verify/tokenizer/proven_no_body/main,
  launcher full, regen full, SHIPPED.md, Council 2 AMEND list);
  design adjudication written (Design C for B1/B4, real argv
  parse for B3, -P + top scan for B2, remote pin + log-order
  marker for Amend 1, basename codex warning, kind-labeled scan
  JSON, derived SHIP_DIR, eval_error is-not-None). Code edits
  landed in the working tree (not yet committed): runner module
  top rewritten (script-form-only guard with entry-.pyc cleanup,
  narrow os.path-only scan, kind-labeled JSON,
  sys.dont_write_bytecode, deferred imports). Remaining:
  _verify_manifest exemption removal + __pycache__ dir rule,
  tokenizer rewrite (both copies), launcher rewrite
  (guard/scan/remote pin/entry-.pyc out-of-process check/full
  scan/-P/--ship-dir/codex warning), _proven_no_body, regen +
  SHIPPED.md + plan updates, manifest regen, then council (3) +
  redteam + independent verifier in parallel.

- 23:20 +07 (T+24m): log commit LANDED: 4ad7b88 on todolist-push,
  verified via ls-remote (bbbdf73..4ad7b88). Rebase was blocked by
  unstaged changes (other workers' files + my runner edits), but
  the parent was still origin HEAD so a fast-forward push worked.
  Continuing: _verify_manifest fix next.
- 23:33 +07 (T+37m): KB DONE noted in MEMORY (not my lane; no
  action). caa4a7c CONFIRMED in history (ancestor of HEAD
  e7913d5, ls-remote = e7913d5). A4 unit table re-read
  (/tmp/y13r2-redteam/attack_a4_unit.py, 39 cases): old wants
  are False for -m (old tokenizer missed them) and None for
  flag-value/-c/renamed cases (undetermined then). New
  expectations per adjudicated design: -m forms CAUGHT,
  flag-value forms CAUGHT, -c exec(open(...)) CAUGHT,
  -c import NOT caught, renamed/symlinked CAUGHT via md5
  (needs the real file staged; unresolvable path is NOT a
  copy, fail-open on identity only), echo/grep/md5sum mentions
  NOT caught. Writing the runner tokenizer rewrite now.
- 23:44 +07 (T+48m): RUNNER TOKENIZER COMMIT LANDED: 0cf43f8,
  verified via ls-remote (1c08f8a..0cf43f8). Fleet notes from
  MEMORY (not my lane): F1+F2 DONE, F3b slot HEALED (Zen PID
  479395, Arms A/B/C PASS), OA imported the Omarchy skill to
  custom-skills. Live slot healing matters for the eventual Y13
  live run (after my re-review), not for this fix diff.
- 23:47 +07 (T+51m): BUG FOUND in my own caa4a7c scan (by
  re-reading _refuse_tampered_ship against the manifest): _SHIP_PY
  lists only the 3 entry .py files, but the ship holds a 4th
  .py, codex-y5/check-dashes.py (manifest entry). The scan walks
  the whole ship, so it refuses the LEGITIMATE check-dashes.py
  as planted-py and a clean staged ship would fail at module
  top. Fix: add "codex-y5/check-dashes.py" to _SHIP_PY (the set
  is exactly the manifest's .py paths). A3 sequence re-read
  (attack_a123.py): -m is ONLY `python3 -m run_codex_y5`; direct
  verify after must be rc 0; empty __pycache__ rc 0; env-guarded
  -m writes nothing. A2 controls: wrong-tag (cpython-311) .pyc
  is ignored by the interpreter but still bricks a later direct
  run (scan refuses ANY .pyc), so the guard must delete ALL
  cache-tag variants of the two entry stems, not just the
  current tag. Fixing both in the runner now, then the launcher.

- 23:52 +07 (T+56m): LAUNCHER REWRITE STARTS. Design (from log
  adjudication): module top = guard + narrow os.path-only scan
  (mirror of runner, _SHIP_PY incl. check-dashes.py) + SHIP_DIR
  derivation (Amend 4: --ship-dir > Y13_SHIP_DIR > file dir >
  /tmp/worker-y13-server fallback) + _SHIP_DIR alias so the
  shared tokenizer block stays byte-identical; remote pin
  https://github.com/phamTuan207/computer-use-wayland.git
  (verified via git remote get-url origin just now); marker
  ordering by git log position, not %ct; _check_entry_pyc
  (out-of-process compile + marshal compare, 3 stems incl.
  run_live, all tags, delete matches / refuse mismatches) runs
  BEFORE _scan_ship (full allowlist; empty __pycache__ allowed,
  any remaining .pyc refuses); exec `python3 -P` +
  PYTHONSAFEPATH=1; codex warning via _is_codex_process.

- 23:58 +07 (T+1h02m): HARNESS LOSS. /tmp/y13r2/ and
  /tmp/y13r2-redteam/ are GONE (existed 23:45 when I read
  attack_a123.py; gone by 23:56; full-disk find confirms no
  copies of forge_pyc.py / attack_a4_unit.py /
  probe_b_tokenizer.py anywhere; repo only mentions them in
  .md). Cause UNKNOWN (no rm by me; /tmp is tmpfs, y14b files
  survive, so not a reboot; possibly another worker's cleanup
  or a tmp reaper). IMPACT: the verifier CANNOT reuse the
  attack harnesses as-is; it must REBUILD them from the specs
  (redteam paper + this log, which preserves the full A4
  39-case table, the A3 sequence, and the A2/A1 shapes).
  LESSON: future harnesses stage under ~/workspace (persistent),
  never /tmp-only. Verifier brief will carry the full tables.

- 00:01 +07 (T+1h05m): LAUNCHER REWRITE DONE. py_compile OK.
  Tokenizer block AST-identical between runner and launcher
  (12 functions, docstrings stripped; text diff shows ONLY the
  2 sync-direction notes, each file naming its counterpart).
  Launcher now: module-top guard + narrow scan (same _SHIP_PY
  incl. check-dashes.py), SHIP_DIR derivation, _check_remote
  pin, check_marker log-order, check_manifest planted refusal,
  _check_entry_pyc (3 stems, all tags, marshal compare in a
  separate python3 -P subprocess), _scan_ship full allowlist,
  codex warning via _is_codex_process, exec python3 -P +
  PYTHONSAFEPATH=1. Committing now.

- 00:03 +07 (T+1h07m): REGEN + STAGE OK (build step, not a test
  verdict): manifest md5 0ca16ddd743acc9e28294fecd07a9c70 (27
  files); staged ship /tmp/y13g-ship-stage; staged
  --verify-manifest exit 0, manifest_ok true, 27 checked, 0
  mismatches. This proves the check-dashes.py scan fix: the
  staged ship passes the module-top scan with the new runner
  bytes. New file md5s: runner db3e357f, launcher eec63492,
  run_live 84fa106c (pin holds). SHIPPED.md + plan doc updated
  (Y13g amendments section). Committing now, then spawning
  council (3) + redteam + independent verifier in parallel.

- 00:05 +07 (T+1h09m): FIX DIFF COMPLETE + REVIEWERS SPAWNED.
  Fix diff 431b2a9..HEAD, 6 files, +1413/-259 (only Y13g commits
  touch them): runner db3e357f, launcher eec63492, manifest
  0ca16ddd, run_live pin holds 84fa106c. Commits: 4ad7b88 (log),
  caa4a7c, 0cf43f8, 03303f4, 6cd0f7a, b815590 (all verified via
  ls-remote). Spawned in parallel: Council 1 (design), Council 2
  (adversarial, checks all 6 of Y13r2-C2 amends), Council 3
  (operator), Redteam (fresh A1-A8+ attacks on new bytes),
  Independent Verifier (rebuilds harnesses from specs - /tmp
  harnesses lost - full battery A2/A6d/A4/A3/A5/A7/A8 + AST +
  clean verify + launcher dry run; stages under
  ~/workspace/y13g-verify/). Awaiting their results; will
  adjudicate findings, fix holes in small commits, re-verify,
  then report to Muse. No live Zen driving before the fresh
  re-review (Y13r3) lands.

- 00:16 +07 (T+1h20m): COUNCIL 3 DONE, verdict AMEND, paper
  a2d46b2 (improvements/worker-y13g-council-3.md + log). Method:
  read all 6 files, AST-compared tokenizer block, 10 operability
  probes on scratch staged ships (no live Zen). 11 findings:
  C3-1 repo-tree path derives repo as ship, refuses as tampered
  (moderate); C3-2 manifest-md5 refusal prescribes a fix that
  cannot work for uncommitted edits (moderate); C3-3 verifier
  method undocumented (AST-extraction lives only in my log;
  md5 leg silently disables when manifest unreadable; plan
  PYTHONDONTWRITEBYTECODE sentence stale) (moderate); C3-4
  runner -m guard deletes only 2 stems, run_live .pyc bricks
  verify with no self-heal, proved live P9 (moderate-low);
  C3-5 refusal messages lack recovery hints (moderate-low);
  C3-6 --repo paths disagree between launcher docstring and
  SHIPPED.md (low-moderate); C3-7 runner docstring launch lines
  lack -P (low); C3-8 plan B1 wording implies 1-2 entry .pyc
  pass verify, they do not (low-moderate); C3-9 --ship-dir absent
  from SHIPPED.md, dangling value silently eats next arg, proved
  P8 (low-moderate); C3-10 handover-token "written by launcher"
  claim false in code (low); C3-11 doc batch (plan overstates
  check_manifest, regen docstring stale, SHIPPED regen line
  lacks cwd note) (low). Holds verified: regen --stage rc 0 x2
  deterministic (0ca16ddd), -m sequence clean, empty __pycache__
  passes, tokenizer AST-identical, remote pin matches, Amend 5
  in code. NOT adjudicating yet: waiting on Council 1/2,
  Redteam, Verifier (4/5 still running).

- 00:18 +07 (T+1h22m): COUNCIL 1 DONE, verdict AMEND, paper
  6e9544f (improvements/worker-y13g-council-1.md + log). 10
  findings: F1 (Medium) _check_entry_pyc UNREACHABLE for a
  pre-existing .pyc (module-top scan + check_manifest refuse
  first); docs present it as the operative B1 control. Fix (a)
  rewrite docs to name top scan + check_manifest operative and
  _check_entry_pyc TOCTOU-only, or (b) exempt entry .pyc from
  the launcher top scan + check_manifest so _check_entry_pyc
  adjudicates. F2 (Medium-Low) guard stem asymmetry, same as
  C3-4 (run_live missing from runner guard + _ENTRY_PYC_NAMES).
  F3 (Medium-Low) NEW REAL BUG: bundled value-flags misparsed
  (-uc, -Bc, -um, -Bum fall through to generic skip, want True,
  got False; 4 probes). Fix: consume next token as -c/-m value
  when a bundled token ends in c/m, both copies, add cases to
  verifier battery. F4 (Low-Medium) -c docstring claims os.system
  caught, plan says not, probe confirms False; fix docstring in
  both copies + SHIPPED.md + launcher check 7. F5 (Low)
  _proven_no_body docstring contradicts code (None accepted).
  F6 (Low) runner docstring launch lines lack -P (same as C3-7).
  F7 (Low) plan B2 bullet overstates check_manifest (same as
  C3-11a). F8 (Low) runner preflight comment says plain codex
  "only warns" but runner has no warning branch. F9 (Low)
  Amend 3 "scan JSON" unscoped (runner only). F10 (Trivial)
  CODEX comment drift in the "identical" block. Holds: both
  bootstraps consistent, tokenizer AST-identical, 18 behavioral
  probes pass, manifest/SHIPPED agree, no dashes, no
  pyc_refused left. Still waiting: Council 2, Redteam,
  Verifier (3/5 running).

- 00:32 +07 (T+1h36m): REDTEAM DONE, verdict AMEND, paper
  7c2d1dd (improvements/worker-y13g-redteam.md + log; 4 commits;
  harnesses rebuilt from spec under ~/workspace/y13g-redteam/).
  Results: A1 PASS 3/3; A2 direct PASS, -m/import marker PRINTS
  (documented unfixable hole, confirmed live), fake-OK forge via
  -m prints fake manifest_ok true rc 0, launcher path refuses
  pre-exec rc 2 no marker, isolated _check_entry_pyc 8/8 correct;
  A3 PASS (residual: import run_live / py_compile still brick
  verify until re-stage, F4); A4 specified set PASS (unit 69/80,
  live 24/24), 11 FRESH evasions proven real execution forms;
  A5 13/13 (case 1 passes BY DESIGN, case 3 refuses by log
  order, fork refuses); A6 PASS 38/38 (all 15 names, marker never
  prints); A7 PASS 22/22 (kind symlink); A8 PASS 12/12 ("" False).
  A9 extra: tampered run_live.py executes on the DIRECT path
  (launcher layers refuse pre-exec, no marker); --ship-dir refuses
  tampered ship, real ship untouched. Findings: F1 documented
  residual (-m/import forged entry .pyc executes; accept
  adjudication, do not claim literal B1 re-test met); F2
  _check_entry_pyc unreachable (same as C1-F1); F3 11 tokenizer
  evasions (wrappers nice/nice -n/stdbuf/taskset/sudo, trailing
  -W/-X bundles -uW/-uX/-iuW, -c os.system nesting, -c
  runpy.run_path, -c exec of renamed copy with __file__ preset;
  re-test must reach A4 unit 80/80, live 6/6); F4 import
  run_live / py_compile brick verify (same family as C3-4/F2);
  F5 tampered run_live.py executes on direct path, fix: verify
  entry .py hashes at module top before importing run_live; F6
  marker case 1 passes by design (keep documented). Redteam says
  fix F2-F5, re-run probes, then live may proceed. Still waiting:
  Council 2, Verifier (2/5 running).

- 00:56 +07 (T+2h00m): COUNCIL 2 DONE, verdict BLOCK, paper
  cb499a8 (improvements/worker-y13g-council-2.md + log; probes
  under ~/workspace/y13g-council-2/probes/, persistent). One HIGH
  hole C2-1: planted stdlib-stem .so executes before any refusal
  (glob.so bare form marker PRESENT rc 2; http.so marker PRESENT
  rc 1; hashlib.so via LAUNCHER bare form marker PRESENT; shlex.so
  under -P via _is_runner_cmdline marker PRESENT, the -P bypass:
  -P protects only imports before the sys.path insert, and shlex
  is lazily imported after it). Root: runner scan is a denylist
  (.pyc/symlink/planted-.py only), never the full allowlist +
  md5s AMEND 1(b) required; sys.flags.safe_path never checked,
  so -P is documentary only. Proposed fix: full allowlist scan
  in BOTH files (os-only, refuse any path not in the manifest set
  + any unexpected dir), enforce safe_path (refuse without -P),
  pre-import shlex at top. 3 MEDIUM: C2-2 _check_entry_pyc dead
  on launcher path (same as C1-F1/redteam-F2; legit entry .pyc
  bricks LAUNCHER path via check_manifest first; run_live .pyc
  never cleaned by runner guard); C2-3 tokenizer residuals 20/79
  miss (-m pdb + script runs, __spec__ None; python3 - stdin;
  -uc/-Bc bundled -c; timeout 60s/1m units; bash -c glued ;
  separators; -c runpy.run_path / os.system / split-concat exec;
  pypy3; wrappers nice/sudo/stdbuf/uv run; exec -a; FIFO /
  unreadable md5 fail-open; 2 FPs fail-closed, harmless;
  corrected: -m runpy / -m cProfile correctly NOT caught, guard
  fires); C2-4 guard deletes through a symlinked __pycache__
  (outside file deleted before scan runs). 7 LOW: C2-5 codex
  warning bare token still warns (grep codex, echo codex,
  /path/codex/run_codex_y5.py); C2-6 remote pin strict-string
  (SSH/trailing-slash/no-.git refuse) + no --topo-order +
  content-free marker (documented limit); C2-7 guard gaps
  (nested .pyc, non-cpython tag, dir-named-.pyc, __pycache__ as
  file); C2-8 uncaught subprocess exceptions exit 1 not 2;
  C2-9 doc overclaims (plan B1/B4 launcher-verify, B2
  check_manifest scope, B3 bundled, stale PYTHONDONTWRITEBYTECODE
  line, launcher-only vs direct form); C2-10 md5 leg edges
  (FIFO/unreadable fail-open, renamed .sh not in set, no size
  cap); C2-11 _proven_no_body eval_error None treated as absent.
  Positive side: B1 exemption gone, B4 happy path works, B2 .py
  plants refused, B3 common forms catch (79 cases agree), AMEND
  2/5 done in substance, eval_error "" False, tokenizer
  AST-identical. Still waiting: Verifier (1/5 running).

  PUSH INCIDENT 00:33-00:40 (logged 00:56): my commit e05bbc9
  accidentally swept Y14b's staged file
  improvements/worker-y14b-fix8-redteam.md (plain `git commit`
  commits everything staged in the shared worktree). The file is
  Y14b's legitimate content, already on origin now under my
  message; attribution wrinkle only, no loss (Y14b noted it in
  b69f1cf). The fallback chain then stashed others' work
  (y13g-wip10) and the push raced (remote moved ea8369cb to
  3f62d67 mid-push); rebase replayed e05bbc9 onto origin, stash
  pop conflicted on Y14b's fix8-council-1.md (already committed
  at HEAD, stale copy in stash), resolved to HEAD's version,
  stash dropped, tree clean. LESSON: always
  `git commit --only <my files>` in this shared worktree, never a
  bare `git commit`.

- 01:05 +07 (T+2h09m): ALL 5 REVIEWERS DONE. Verifier PASS
  132/132, report improvements/worker-y13g-verify-report.md,
  final commit 138d08e (on origin; 5 verify commits d76daba,
  4651ef8, c45e1ad, cbddfca, 138d08e). Batteries: A2 11/11,
  A6d 18/18, A4 unit 39/39, A4 live 6/6, A3 7/7, A5 10/10,
  A7 10/10, A8 12/12, AST 13/13, clean ship 6/6. Pins hold
  (runner db3e357f, launcher eec63492, run_live 84fa106c,
  manifest 0ca16ddd). Known limits documented: -m/import hole
  (unfixable in-process, launcher-controlled), marker case 1
  passes by design, md5 leg fails open on unresolvable paths.
  Harnesses committed under improvements/y13g-verify/
  (reusable by the re-verifier). NOTE: A8 table records
  eval_error None returns True under the current is-not-None
  code; R9 below flips that row to False (key-presence check),
  the re-verifier must expect False.
  Council 2 formal handoff also arrived (paper cb499a8 + log
  follow-up fd0cb7d, remote HEAD fd0cb7d); substance already
  logged 00:56. Tally: C1 AMEND, C3 AMEND, Redteam AMEND,
  C2 BLOCK (C2-1 HIGH), Verifier PASS. The verifier's PASS is
  on the SPECIFIED batteries; C2 + redteam found NEW holes
  beyond that set (.so plants, tokenizer residuals, dead
  _check_entry_pyc, guard symlink delete, tampered run_live.py
  on direct path). So round 2 fixes those, then a fresh review
  round over the new diff.

  ADJUDICATION, ROUND 2 FIX LIST (all findings, one pass):
  R1 (C2-1 HIGH): full-allowlist module-top scan in BOTH entry
  points, os-only. Hardcode _SHIP_FILES = the 27 manifest rel
  paths (identical in both files). Refuse any file not in the
  set, any dir not a parent of a manifest path (except the
  narrow top-level __pycache__ dir exemption), any symlink.
  Kind labels kept (pyc/symlink/planted-py + new
  unexpected-file/unexpected-dir). Enforce sys.flags.safe_path
  at module top AFTER the guard, BEFORE the scan (refuse exit
  2 without -P; -m probes still get the script-form message
  because the guard fires first). Pre-import shlex at the top
  (deferred imports, before the sys.path insert) in both files.
  R2 (C2-2/F2/redteam-F2/C1-F1): _check_entry_pyc operative.
  Exempt the 3 entry stems (any tag, top-level __pycache__
  only) from the LAUNCHER top scan AND check_manifest .pyc
  refusal, so _check_entry_pyc adjudicates; runner scan stays
  strict. Docs updated to the new flow. Add run_live to the
  runner guard stems + _ENTRY_PYC_NAMES (3 stems, "two" to
  "three" everywhere). R3 (C1-F3/C2-3/redteam-F3): tokenizer
  rewrite in both copies, AST-identity: unified short-flag
  branch (c/m/W/X value flags, no-value bundles, unknown-flag
  skip); -m pdb inspects following args for a script
  candidate; python3 - returns True (fail-closed stdin);
  timeout accepts unit suffixes/decimals; _shlex_tokens splits
  on ; & | mid-token; -c sinks extended (os.system,
  subprocess.*, runpy.run_path) + quoted .py path md5 check
  (split-concat fully-split form documented as residual);
  pypy3/pypy in _PYTHON_TOKENS; wrappers nice/stdbuf/taskset/
  sudo/uv with flag skipping; exec -a/-l/-c flag skipping;
  md5 size cap 10MB + documented FIFO/unreadable/.sh limits.
  R4 (C2-4/C2-7): guard symlink safety + recursive + any-tag:
  _entry_pyc_paths requires realpath(cache) inside the ship
  dir (symlinked __pycache__ returns [], scan refuses it);
  recursive walk, any implementation tag. R5 (redteam F5):
  runner verifies entry .py md5s against the ship manifest
  BEFORE importing run_live (refuse exit 2 on mismatch;
  self-consistent manifest tamper documented as needing the
  launcher git comparison). R6 (C2-5/C1-F8): _is_codex_process
  matches only argv[0] basename codex or a token ending in
  /codex; runner preflight comment reworded (warning lives in
  launcher). R7 (C2-6): remote URL normalization (strip
  trailing /, optional .git, case-fold host, accept
  git@github.com: SSH form) + --topo-order on the marker git
  log. R8 (C2-8): wrap launcher subprocess.run calls
  (OSError, TimeoutExpired) into _fail exit 2. R9 (C2-11/
  C1-F5): _proven_no_body uses "eval_error" in diag + docstring
  fix (proof needs the key ABSENT). R10 docs (C3-1..C3-11,
  C1-F6/F7/F9/F10, C2-9): runner docstring -P; plan B2 scope;
  Amend 3 runner-only; CODEX comment sync; launcher repo-tree
  ship guard; manifest-md5 message (commit + push first, then
  re-stage); "How to verify" note in SHIPPED.md/plan + remove
  stale PYTHONDONTWRITEBYTECODE sentence; recovery hints in
  refusals; single --repo path (verify on laptop:
  /home/james/workspace/computer-use-wayland); plan B1 wording
  (EMPTY __pycache__ only); --ship-dir in SHIPPED.md + value
  validation + name in not-found message + space-form only;
  handover-token writer correction (find the real writer);
  regen docstring + SHIPPED cwd note; B1/B4 launcher-verify
  wording per R2; launcher-only vs direct form (direct WITH
  -P supported for verify/staging, launcher required for live
  runs). R11 = R3 md5 cap/limits (folded in). BEHAVIOR CHANGE
  NOTE for the re-verifier: bare (no -P) invocations now refuse
  at the safe_path gate (exit 2, no marker), so A6d no-P spot
  checks expect the safe_path refusal, not the scan JSON; the
  -P form still expects kind planted-py. Next: implement R1-R10
  in small commits, regen manifest, then spawn a fresh review
  round (council x3 + redteam + verifier) over the new diff.

- 01:12 +07 (T+2h16m): ROUND 2 IMPLEMENTATION STARTED. Runner
  module top committed 0639d04 (R1 allowlist scan + safe_path +
  shlex pre-import, R2/R4 guard 3 stems recursive any-tag
  symlink-safe, R5 entry-hash check before run_live import).
  Launcher module top committed 87eec47 (same R1/R2/R4, plus
  C3-1 repo-tree guard, C3-9 --ship-dir validation). Both
  py_compile OK; _SHIP_FILES identical (29 paths) and equal to
  manifest + manifest itself + SHIPPED.md. CAUGHT WHILE
  EDITING: the staged ship holds 29 files, not 27 (regen also
  copies codex-y5-manifest.json + codex-y5/SHIPPED.md); the
  first _SHIP_FILES draft (27) would have refused every clean
  ship. Fixed before commit. C3-6 VERIFIED ON LAPTOP via SSH:
  both /home/james/computer-use-wayland (detached HEAD 56f5af4)
  and /home/james/workspace/computer-use-wayland (branch
  todolist-push, HEAD 4500a18) exist; neither currently holds
  tests/realistic/launch_y13.py; the todolist-push checkout is
  /home/james/workspace/computer-use-wayland, now the single
  --repo path in both docs. Also verified: no .git at
  ~/workspace, ~, or /tmp, so the repo-tree guard cannot
  false-fire on staged ships there. Next: R3 tokenizer rewrite
  (both copies), then R6/R7/R8 launcher checks, R9, R10 docs,
  regen, fresh review round.

- 01:35 +07 (T+2h39m): ROUND 2 FIX DIFF COMPLETE. Commits
  (todolist-push, all verified via ls-remote): 0639d04 runner
  module top (R1/R2/R4/R5), 87eec47 launcher module top
  (R1/R2/R4/C3-1/C3-9), 6ba43f2 R3 tokenizer rewrite + R6 codex
  warning + F10 comment sync (both files, 14 tokenizer functions
  AST-identical docstring-stripped, raw diff = the 2 sync notes +
  the CODEX comment which is now synced), 8bdd5aa R7/R8/R9/C3-10
  (remote normalization + topo-order, subprocess exit 2, proven_
  no_body key-presence, launcher writes handover token), 5a9b9e8
  R10 docs + regen manifest 7c763834 (runner d5047ff5, launcher
  8e72a5ce, run_live 84fa106c pin holds). Regen --stage verify on
  a fresh staged ship: exit 0, manifest_ok true, 27 checked, 0
  mismatches (build step, not a test verdict). All files
  py_compile OK. Spawning the fresh review round (council x3 +
  redteam + verifier) over the round-2 diff now; each brief
  carries the new pins, the behavior changes (bare no-P refuses
  at safe_path, A8 None flips to False, 14 tokenizer functions,
  launcher writes the token), and the harness locations
  (~/workspace/y13g-redteam/, ~/workspace/y13g-council-2/probes/,
  improvements/y13g-verify/).

- 01:41 +07 (T+2h45m): COUNCIL 3 ROUND-2 DONE, verdict AMEND,
  paper 31c1126 (improvements/worker-y13g-r2-council-3.md + log;
  probes ~/workspace/y13g-r2-council-3/). 13 probes, pins hold.
  Findings C3-1..C3-8: C3-1 (moderate) --ship-dir=DIR and
  --repo=DIR silently ignored, not refused (P3d: = form tests
  the wrong ship and can false-PASS; P3b: from the repo tree it
  yields the repo-tree refusal telling the operator to "pass
  --ship-dir" when they did). Fix: refuse any --ship-dir=/--repo=
  token in _derive_ship_dir. C3-2 (moderate) SHIPPED.md "How to
  verify" fails literally at the first call (NameError:
  _RUNNER_MODULE_NAMES not defined); the note omits the 4 module
  constants, never names the 14 functions, never says cmdlines
  are NUL-joined /proc form. Fix: correct the note. C3-3
  (moderate-low) round-1 C3-7 NOT fixed: runner docstring lines
  103,105 still `python3 launch_y13.py` without -P (and no
  --repo); under R1 a bare invocation refuses, so these are
  commands that cannot run as written. (My R10 missed the Usage
  lines; only the SCRIPT FORM ONLY block was fixed.) C3-4
  (moderate-low) scan "fix" hint misleads on nested dirs:
  deleting only the named .pyc leaves the empty nested dir and
  verify still refuses unexpected-dir; only rmdir recovers. C3-5
  (low) round-1 C3-8 NOT fixed in substance: plan B1 still says
  "(0-3)" while only the EMPTY dir passes; _verify_manifest
  comment still says "two entry .pyc files (0, 1, or 2)" while
  _ENTRY_PYC_NAMES has 3 stems. C3-6 (low) _scan_ship md5 message
  lacks the commit+push-first branch. C3-7 (low) remaining
  hint-less refusal legs (check_manifest planted .py/symlink,
  _scan_ship symlink/bytecode/unexpected/unreadable). C3-8 (low)
  write_token() runs before check_manifest/_scan_ship, so a
  refused launch still leaves a fresh token asserting go+marker;
  move it to just before check_token(). Holds verified: regen
  clean ship rc 0 (7c763834, 29 files), _SHIP_FILES 29/29,
  launcher dry run reaches go gate, --ship-dir validation,
  repo-tree guard no false-fire, direct -P rc 0 / bare safe_path
  refusal, launcher-written token accepted + fingerprint binding,
  _check_entry_pyc operative in isolation, tokenizer
  AST-identical, R7 8/8, R9/R8/R5 hold. Caveat: marker gate not
  passable live (no Y6c marker), so check_manifest/_scan_ship/
  _check_entry_pyc probed by AST-extraction only. Still waiting:
  Council 1, Council 2, Redteam, Verifier (4/5 running).

01:14 +07 22/11 (T+2h18m) COUNCIL 1 ROUND-2 DONE, verdict AMEND.
  Paper commit 1e49436 (improvements/worker-y13g-r2-council-1.md),
  log follow-up ecadd31, both verified on origin via ls-remote.
  Probes persistent under ~/workspace/y13g-r2-council-1/ (probe_r2.py,
  probe_r2b.py, staged ships ship1/3a/b/c/4/4c/5b/6/8/9, repotree).
  Pins hold: runner d5047ff5, launcher 8e72a5ce, manifest 7c763834
  (27 files), run_live 84fa106c (pin 1e3901c holds). Findings F1-F8:
  F1 (Medium-Low) runner docstring launch lines 103,105 still
  `python3 launch_y13.py` without -P; probe P7 proves the exact form
  exits 2 at the safe-path gate. R10 claim "runner docstring -P"
  NOT fixed (same as round-1 C3-7/C1-F6). F2 (Medium-Low) launcher
  -m guard runs AFTER _derive_ship_dir and cleans the derived dir,
  not the file's dir (launch_y13.py:185,227): (a) -m from a repo-tree
  copy exits with the new C3-1 message and leaves the .pyc behind
  (P4a); (b) -m with --ship-dir elsewhere prints the guard message
  but the real .pyc stays (P4c). Contradicts the B4 "no .pyc is left
  behind" assertion. Fix: guard before derive, against
  dirname(__file__). F3 (Low) SHIPPED.md "How to verify" omits the
  Assign constants; literal method raises NameError:
  _RUNNER_MODULE_NAMES on extensionless, -m, -m pdb inputs (P2c);
  working method is extract_lib.py. (Overlaps C3-2 round-2.) F4
  (Low) -c sink docs say "subprocess.*" but _SINKS covers only
  call/run/Popen/check_output/check_call; subprocess.getoutput(...)
  returns False (P6). F5 (Low) runner _verify_manifest comment
  still says "two entry .pyc files (0, 1, or 2)"
  (run_codex_y5.py:750); code has 3 stems. Tag-scope difference
  there (current-tag only vs any-tag elsewhere) outcome-identical.
  (Overlaps C3-5 round-2.) F6 (Low) plan Amend 4 / SHIPPED.md "a
  repo-tree path refuses with..." holds only for the file-dir
  branch; explicit --ship-dir at a repo tree is refused later as
  tampered (different message, proven live). F7 (Low) R8 missed the
  main() exec subprocess.run (launch_y13.py:1503), the only
  unwrapped launcher call; a missing flock would exit 1 with a
  traceback. F8 (Low) _check_entry_pyc marshal comparison is
  filename-sensitive: a relative-path-compiled legitimate .pyc is
  refused as forged (P3b); absolute py_compile, `import run_live`,
  and stale-tag .pyc all verify+delete (P3a/P3c/P8).
  Verified consistent: allowlist 29 = manifest 27 + manifest +
  SHIPPED.md, identical in both files (P1b); tokenizer
  AST-identical 14/14 (P1-AST14); guard stems 3/3 everywhere
  (P1c); R2 composition (launcher scan + check_manifest exempt
  top-level entry .pyc, _check_entry_pyc adjudicates, _scan_ship
  backstops); symlinked __pycache__ refuses, sentinel survives;
  R5 tampered run_live.py refused before import, import marker
  never written (P9); write_token before check_token, after
  go+marker; R7 remote normalization all 7 forms, --topo-order
  present; R9 A8 6/6; R6 basename-only + reworded preflight;
  regen reproduces manifest 7c763834, staged verify exit 0.
  Council 1: no live run until F1 + F2 are fixed and re-verified;
  F3-F8 can ride the same fix pass.
  NOTE: verifier interim commit dec965c landed BEFORE this log
  entry (A2/A4-unit/A8/A3/A6d/A7 results, "2 defects found, both
  in _check_entry_pyc"). I have NOT yet read its detail; will read
  improvements/worker-y13g-r2-verify-log.md before adjudication.
  Still waiting: Council 2, Redteam, Verifier (3/5 running).

01:16 +07 22/11 (T+2h20m) VERIFIER ROUND-2 REPORT LANDED, verdict FAIL.
  Report commit 75dff55 (improvements/worker-y13g-r2-verify-report.md,
  314 lines), log dec965c + 0d628f8. Note: 75dff55 landed on top of
  my log commit b74b36d in the shared worktree (verifier committed
  + pushed in the same checkout between my commit and my push);
  ls-remote = 75dff55 = local HEAD, my b74b36d is on origin as its
  parent. No conflict, no loss. Score 277/280 across 10 batteries.
  2 root causes, BOTH in the launcher's _check_entry_pyc:
  (1) A3h co_filename sensitivity (2 checks): a legitimate entry
  .pyc from relative-path `python3 -m py_compile run_codex_y5.py`
  (run from inside the ship dir, the natural form) is refused:
  cached code has co_filename "run_codex_y5.py" while the fresh
  compile uses the absolute ship path; consts/names/code bytes
  identical, marshal equality fails ONLY on co_filename. Ship
  does NOT self-heal to direct verify rc 0 after a relative-path
  py_compile. Fail-closed (refuse + "re-stage the ship"), trivial
  recovery (delete the .pyc). Documented self-cache path
  (-m/import, absolute filenames) unaffected. Fix shape:
  normalize co_filename in the comparison (e.g.
  code.replace(co_filename=src) on both sides). Same root cause
  as Council 1 F8 (P3b). (2) A7 shape-6b symlink-unsafe deletion
  (1 check): _check_entry_pyc uses plain os.listdir() +
  os.unlink() on SHIP_DIR/__pycache__ and never applies the
  realpath-inside-ship check that _entry_pyc_paths (the -m guard
  helper) has. A legitimate .pyc behind a symlinked __pycache__
  is DELETED OUTSIDE the ship (proven twice: manual probe +
  harness re-run). R4 claims symlink safety ("the guard never
  deletes a file OUTSIDE the ship") but that holds only for the
  guard helper, not for the function that deletes files during
  launch checks. Reachability in production flow is LIMITED:
  the launcher module-top scan refuses a symlinked __pycache__
  before main() runs _check_entry_pyc. Damage scope narrow (only
  a file under the symlinked dir). Fix shape: apply the same
  realpath-inside-ship check inside _check_entry_pyc (or reuse
  _entry_pyc_paths). Everything else passes, including every
  security property (forged entry .pyc refused in all forms,
  .so/.py plants refused, marker/log-order/remote pin hold,
  tokenizer rewrite complete and identical in both copies).
  Harness bugs found and fixed during the run (all in verifier
  code, none in the fix): driver missing _normalize_remote_url
  (A5 0/10 first run), missing _m_module_is_runner +
  _is_timeout_dur (A4 live 12/17 first run), missing TOKEN_TTL_S
  (clean ship 7/9 first run); A2j/A2l expectations corrected
  after root-causing (kind mixed; empty nested-dir residue).
  NOT tested: no live run; R8 TimeoutExpired not directly
  triggered (only OSError path). The verifier subagent has NOT
  yet delivered its formal completion handoff (still listed
  running); this entry is from its committed report only.
  Still waiting: Council 2, Redteam, Verifier handoff (3/5).
