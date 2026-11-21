# Y13g Council 2 log (adversarial re-review)

Reviewer: Council Voice 2 (successor to Y13r2 Council 2), 2026-11-22 +07.
Scope: Y13g fix diff 431b2a9..HEAD, 6 files only (Y13g commits
caa4a7c, 0cf43f8, 03303f4, 6cd0f7a, b815590). No live Zen driving.
No ydotool. No em/en dashes. Work only in the repo worktree and
~/workspace/y13g-council-2 scratch.

## Live event log

- 00:05:35 +07 (T+0m00s): task received. Y13g fix diff, 6 files,
  5 commits, manifest md5 0ca16ddd743acc9e28294fecd07a9c70.
- 00:05-00:16 +07 (T+0m to T+11m): read Y13g fix log in full and
  Y13r2 Council 2 paper (6 amends) in full. Repo state: branch
  todolist-push, HEAD 4075e0e (Y13g log commit, after b815590).
  Origin URL verified: https://github.com/phamTuan207/computer-use-wayland.git
  (matches KNOWN_REMOTE_URL in the launcher).
- 00:16 +07 (T+11m): interpreter facts probed: `os` IS preloaded at
  startup (`'os' in sys.modules` True); `python3 -P -c` drops the
  cwd entry from sys.path; `python3 -` DOES define __file__ as
  "<stdin>" (so the stdin form is a live execution path, not a
  crash); gcc present (/usr/bin/gcc). run_live.py (working tree)
  imports re/json/socket/subprocess/pathlib/datetime/threading/time
  plus functools (preloaded) and a live_metrics import at line 73
  (working-tree version only; pinned ship run_live has none).
- 00:16 +07 (T+11m): log file started. Staging a clean ship next,
  then probes: .so plant, sitecustomize/os pre-scan plants,
  tokenizer unit table, AST identity, check_manifest vs
  _check_entry_pyc ordering, remote pin, -m guard edges,
  scan divergence table, _proven_no_body callers.
- 00:17-00:22 +07 (T+12m to T+17m): clean ship staged at
  ~/workspace/y13g-council-2/ship (regen script, manifest md5
  0ca16ddd..., staged --verify-manifest exit 0). Pinned ship
  run_live imports: datetime/json/os/re/socket/subprocess/sys/
  threading/time/urllib/http.server/pathlib/functools. Preloaded at
  startup: time/threading/functools/encodings/site/os. NOT
  preloaded: base64/glob/hashlib/json/re/socket/subprocess/
  datetime/pathlib/urllib/http/shlex.
- 00:22 +07 (T+17m): PROBE 1 DONE (pre-scan plants, 9 cases).
  CONFIRMED A: planted glob .so, bare runner form, marker PRESENT,
  rc=2 (verify refused AFTER execution). KILLED B/C: re/json .so
  with -P, marker absent (runner already imported them from
  stdlib before the sys.path insert, so run_live reuses them).
  KILLED D/E/F/H: sitecustomize/usercustomize/encodings plants do
  NOT execute (bare or -P); site loads them before sys.path[0]
  is set. KILLED G: os.py does not execute (os preloaded).
  KILLED I: glob.py control, scan refuses, no marker.
- 00:24 +07 (T+19m): PROBE 1b DONE (.so follow-ups). CONFIRMED N:
  http .so bare form, marker PRESENT, rc=1 (ModuleNotFoundError
  http.client, the .so replaced the http package). CONFIRMED K:
  hashlib .so, bare LAUNCHER form, marker PRESENT (executed at
  launcher import, before Y13_GO refusal). KILLED J: http .so
  with -P, marker absent (urllib.request already loaded stdlib
  http). KILLED L: sitecustomize -m form, marker absent.
  CONFIRMED M (mechanism): shlex .so executes on `import shlex`
  after the ship dir is on sys.path.
- 00:25 +07 (T+20m): grep confirms the runner's ONLY lazy import
  not already loaded at top is shlex (_shlex_tokens, line 3716);
  json/hashlib/re lazy imports are already loaded. Launcher lazy:
  shlex (301), marshal (892, preloaded), glob (1050). NEITHER file
  checks sys.flags.safe_path anywhere: -P is documentary only,
  a bare invocation is never refused.
- 00:26 +07 (T+21m): PROBE 2 DONE (tokenizer, 79 cases, own
  harness, AST-extracted from both files). Both copies agree on
  all 79. 22 misses, 2 false positives. Misses: -m runpy/pdb/
  cProfile + script (3), -uc/-Bc bundled -c (2), -c runpy.run_path
  (1), -c os.system (1, documented limit), -c split-concat exec
  (1), python3 - stdin (2), timeout 60s/1m units (2), bash -c
  glued ;/&& (2), FIFO script (1), unreadable copy (1), pypy3
  (1), nice/sudo/stdbuf/uv run wrappers (4), exec -a (1).
  FPs (fail-closed): non-python binary named run_codex_y5 or
  run_live (2). SHLEX-LIVE-PATH: calling the runner's own
  _is_runner_cmdline on a bash -c cmdline executed the planted
  shlex.so (marker PRESENT) while returning True: the safety
  check itself imports shlex from the ship dir after the
  sys.path insert.
- 00:28 +07 (T+23m): PROBE 3 DONE (AST identity). The shared
  tokenizer block is AST-identical with docstrings stripped
  (12 functions, same names); raw text differs ONLY in the 2
  sync-direction notes (each file naming its counterpart).
  _SHIP_PY identical in both files.
- 00:30 +07 (T+25m): PROBE 4 DONE (ordering + divergence).
  CONFIRMED: check_manifest refuses a LEGITIMATE entry .pyc
  ("planted bytecode") BEFORE _check_entry_pyc runs, so the
  verify-and-delete path is dead code on the launcher path.
  _check_entry_pyc itself works when called directly (legit
  verified + deleted, forged refused). Divergence table: the
  runner module-top scan PASSES .so, .txt, empty dirs,
  namespace-package dirs, subdir .so, nested empty __pycache__
  (all refused later by _verify_manifest, after imports);
  check_manifest PASSES .so/.txt/dirs/subdir-.py (refuses only
  symlinks, .pyc, top-level .py) and _scan_ship refuses them all.
  Empty top-level __pycache__ passes everywhere (B4 case E).
- 00:33 +07 (T+28m): PROBE 5 DONE (remote pin). _check_remote
  fails closed for no origin, SSH origin, trailing slash, no
  .git, wrong case, http, and a non-checkout path; only the
  exact pinned https URL allows. Marker order simulation: A
  PASS, C1 REFUSE (abort newer), harness subject REFUSE,
  abort-matching-marker REFUSE; a forged-date completion passes
  ONLY if pushed on top (a new push, not a date trick), because
  the loop reads no date field at all.
- 00:35 +07 (T+30m): PROBE 6 DONE (-m guard edges). G0 control
  passes (-m rc 2, empty __pycache__, direct rc 0). CONFIRMED
  G1: symlinked __pycache__ makes the guard delete a file
  OUTSIDE the ship. CONFIRMED G2/G3: nested .pyc and pypy-tag
  .pyc survive the guard and brick the direct run (scan
  refuses). G5 (.pyc as a dir) and G6 (__pycache__ as a file)
  survive the guard; the scan passes them but verify refuses
  (fail-closed). G7 (entry .py missing) fails cleanly rc 1.
  G8 (unreadable .pyc file) is still deleted (unlink needs dir
  write only). G4 (unreadable dir) is NOT testable on this VM:
  the process runs as root (uid 0) and the overlay FS lets
  listdir succeed on a mode-000 dir, so the guard deleted the
  .pyc; code-reading verdict for a non-root laptop account is
  scan-blind (os.walk skips it) but verify refuses via the dir
  exemption listdir failure.
- 00:38 +07 (T+33m): PROBE 7 DONE (live forms + codex warning +
  _proven_no_body). S1 CONFIRMED: `python3 - < run_codex_y5.py`
  executes the runner (manifest_ok true). S2: -m runpy hits the
  guard (rc 2), so the tokenizer is RIGHT not to catch it.
  S3: -m cProfile hits the guard (message in stderr) but exits
  rc 0 (cProfile swallows the guard's SystemExit); the suite
  does not run, so the tokenizer is RIGHT not to catch it.
  S4 CONFIRMED: -uc combines -u and -c (BUNDLED-C-WORKS).
  S5 CONFIRMED: timeout accepts 60s. Codex warning: the runner
  itself no longer warns (W5), the ssh -c form no longer warns
  (W2), but a bare "codex" token still warns (W1 grep codex,
  W7 echo codex) and a path merely containing a codex dir still
  warns (W8). _proven_no_body: all 5 call sites treat False as
  INFRA (re-run); unit checks all match, including eval_error ""
  -> False (AMEND 5) and explicit None -> True (reads as absent,
  unreachable per the docstring).
- 00:42 +07 (T+37m): PROBE 8 DONE (run_live .pyc). A run_live
  .pyc survives the RUNNER's -m guard (2 stems only) and bricks
  the direct verify (scan refuses); the LAUNCHER's -m guard
  (3 stems) does delete it, but only when launch_y13 itself is
  the imported module. Stdlib source confirms: runpy sets
  __spec__ (S2's guard hit), cProfile sets __spec__ explicitly
  (S3's guard hit), pdb's _ScriptTarget sets __spec__=None.
- 00:44 +07 (T+39m): pdb live check: `python3 -m pdb -c continue
  run_codex_y5.py --verify-manifest` runs the verify
  (manifest_ok true, no guard message). So -m pdb IS a real
  tokenizer miss (pdb sets __spec__=None). CORRECTED probe 2
  count: -m runpy and -m cProfile are NOT misses (the guard
  kills those forms); -m pdb IS a miss. Corrected tokenizer
  misses: 20 of 79 (was 22). The unreadable-copy probe 2 row
  is also a VM artifact in part: on this overlay FS a mode-000
  file is unreadable even to root, so the md5 leg fails open;
  on a normal single-user system the same-uid rival could not
  read it either, so that row matters only across uids (LOW).
- 00:44 +07 (T+39m): _proven_no_body False-branch treatment
  verified in source at all 5 sites (1147, 1164, 1216, 1252,
  4640): False raises InfraError / "infra-blocked" (re-run),
  True raises FixtureUnavailableError / "fixture-unavailable".
  No caller relied on the old falsy behavior. Plan doc diff
  read: the Y13g amendments section overclaims in three places
  (B1/B4 say the launcher verifies + deletes entry .pyc before
  exec, but check_manifest refuses first; B2 says
  check_manifest refuses any planted file, but it only refuses
  symlinks/.pyc/top-level-.py; B3 says bundled forms are
  handled, but -uc/-Bc are missed).
- 00:55 +07 (T+50m): VERDICT BLOCK. Paper written:
  improvements/worker-y13g-council-2.md. 1 HIGH (C2-1 .so plants
  execute; runner scan is a denylist, AMEND 1(b) not done),
  3 MEDIUM (C2-2 dead _check_entry_pyc + run_live stem gap,
  C2-3 tokenizer 20 residual misses, C2-4 guard deletes through
  a symlinked __pycache__), 7 LOW (C2-5 codex warning partial,
  C2-6 remote/marker residuals, C2-7 guard + scan edge gaps,
  C2-8 uncaught subprocess exceptions, C2-9 doc overclaims,
  C2-10 md5 leg edges, C2-11 eval_error None edge). AMEND
  check: 1 PARTIAL, 2 DONE, 3 DONE-in-structure/PARTIAL-in-
  coverage, 4 DONE, 5 DONE-in-substance, 6 PARTIAL. Dash sweep:
  0 em dashes, 0 en dashes in both files. Committing the paper
  + this log now (only these two files; other workers' files
  in the worktree are untouched).
- 00:57 +07 (T+52m): COMMIT LANDED: cb499a8 on todolist-push
  (paper + log, 2 files, 330 insertions), push verified
  (3f62d67..cb499a8). Remote HEAD moved on right after to
  ea06c93 (Y14b redteam fix pass 8 GO); fetch confirms cb499a8
  IS an ancestor of origin/todolist-push. Work complete.
  Probes kept at ~/workspace/y13g-council-2/probes/ (persistent).
