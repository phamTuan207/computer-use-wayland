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
