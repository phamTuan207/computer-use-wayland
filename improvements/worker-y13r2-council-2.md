# Y13r2 Council Voice 2 (adversarial): re-review of the Y13f fix diff

- Reviewer: Council Voice 2, independent, 2026-11-21 ~22:00-22:30 +07
- Scope: Y13f fix commits 118c67f + 3fa389a + 431b2a9 on todolist-push, HEAD 431b2a9. Fix diff read as `git diff cb26d1d 431b2a9` restricted to tests/realistic/run_codex_y5.py, launch_y13.py, regen_codex_y5_manifest.py. Both logs read in full (worker-y13r-rereview-log.md, worker-y13f-fix-log.md). The re-reviewer's probes at /tmp/y13r2/probe_*.py were read for orientation only; every probe below is my own fresh implementation in /tmp/y13r2-council-2/probes/.
- Method: assume the fixes are wrong until proven right. All probes run in temp dirs under /tmp/y13r2-council-2/ (ship staged once with the regen script, manifest md5 verified unchanged after, f27c0302...). No code or runner file modified, no live driving, no commit, no git checkout/reset/clean. The real ship/token paths and the uncommitted working-tree changes were not touched.
- Verdict: **BLOCK**. Two new HIGH holes in the ship-integrity layer the H1 fix was meant to close (C2-1, C2-2), one of them reachable on the exact production launch path. The fixes are mechanical and small, so after they land only a re-review of the fix diff is needed, not a re-review of the whole runner.

## Judgments on the re-reviewer's findings

### Finding 1: CONFIRMED, exactly as stated

`python3 -m run_codex_y5 --verify-manifest` on a clean staged ship fails exit 2, and the failure then poisons the direct form too. My probe 1 (probe1_finding1.py, staged ship at /tmp/y13r2-council-2/ship1):

```
A. -m form, no env var: rc=2
   out='{"manifest_ok": false, "files_checked": 27, "mismatches": ["unexpected directory in ship dir: __pycache__"], "manifest_md5": "f27c03020c9866cfa0dcd637df6f8647"}'
   __pycache__ after A: ['run_codex_y5.cpython-312.pyc']
C. direct form after A: rc=2, same "unexpected directory" mismatch
D. -m form WITH PYTHONDONTWRITEBYTECODE=1, clean ship: rc=0, manifest_ok true, no __pycache__ dir
E. direct form, empty __pycache__/ only: rc=2, same "unexpected directory" mismatch
```

Root cause in code: `_verify_manifest` (run_codex_y5.py:456) walks dirs and refuses any directory not a prefix of a manifest path (line 528), while `__pycache__` is not such a prefix. The file loop exempts the two entry .pyc files (lines 511, 535), but the directory check has no matching exemption, so the scan and the verify disagree: the scan passes a ship the verify refuses. Case E proves the refusal is dir-level: an empty `__pycache__` with no files in it still fails. The launcher's production path sets PYTHONDONTWRITEBYTECODE=1 (launch_y13.py:460), so a launcher-driven run does not trip this, but any direct `-m` invocation without the variable breaks the ship until someone deletes `__pycache__` by hand.

### Finding 2: CONFIRMED, live and end to end

The tokenizer misses `python3 -m run_codex_y5` and `python3 -m run_live` in both copies. My probe 4 unit table (probe4_tokenizer.py, AST-extracted `_is_runner_cmdline` from both files, 36 cases, both copies agree on every case):

```
MISS real=True want=True runner=False launcher=False -m run_codex_y5 (FINDING 2)
MISS real=True want=True runner=False launcher=False -m run_live (FINDING 2)
MISS real=True want=True runner=False launcher=False -m with -u first
```

Live proof (probe5_live_m.py, real dummy modules in a scratch dir): `python3 -m run_codex_y5` pid 181420 cmdline `python3\x00-m\x00run_codex_y5\x00` gives runner_fn=False, launcher_fn=False; the bare-relative control gives True. End to end (probe5b_live_m_only.py, only the `-m` dummy alive): `check_runner_quiet` exits 0 with only `WARNING: codex process running (pid 181657): python3 -m run_codex_y5` and `CHECK_QUIET_PASSED`. A live `-m` rival does not block the launch. (Probe 5's first end-to-end run refused, but only because its bare-relative control dummy was also alive; 5b isolates the `-m` case.)

## New holes

### C2-1 (HIGH): a forged ENTRY .pyc executes under -m and import, and the exemption never helps a legitimate run

The exemption's justification (run_codex_y5.py:136-146, "They cannot execute in production: both entry points run as __main__, never from .pyc") is false for `-m` and for `import`. A forged entry .pyc with a header patched from the source stat (mtime/size, the only fields the import system checks for timestamp-based .pyc) loads instead of the source.

Probe 2 (probe2_entry_pyc_forge.py), attacker code prints a marker and exits 42:

```
A. -m form, forged entry .pyc: rc=42, out='FORGED-ENTRY-PYC-EXECUTED'
B. direct form, same forged .pyc: rc=2, out='{"manifest_ok": false, ... "unexpected directory in ship dir: __pycache__" ...}'
C. -m launch_y13, forged launcher .pyc: rc=42, out='FORGED-ENTRY-PYC-EXECUTED'
D. -m form, forged .pyc with stale header: rc=2 (import falls back to source, then verify fails on the dir)
```

Probe 8 case 4 (probe8_verify_isolated.py): `import run_codex_y5` with a forged entry .pyc also executes it (`FORGED-PYC-EXECUTED` printed, then AttributeError because the forged module has no `_verify_manifest`). So both `-m` and plain import execute the forgery.

Two further facts make this worse than a narrow exemption bug. First, the exemption can never help a legitimate run pass: probe 8 case 5 (forged launch_y13 .pyc) shows `_verify_manifest` reporting only the directory mismatch, with NO bytecode mismatch for the exempted file, while case 6 (same file named `cpython-311` instead of `cpython-312`) reports both the directory AND `bytecode in ship dir: __pycache__/run_codex_y5.cpython-311.pyc`. The file-level exemption is real, but it is dead in practice because the directory check fires first. The exemption buys nothing and costs the `-m`/import execution path. Second, the exemption interacts with the Finding 1 fix: any fix for Finding 1 that exempts the `__pycache__` directory in `_verify_manifest` without also removing the file exemption would let a forged entry .pyc pass `_verify_manifest` outright (case 5 would have zero mismatches apart from the probe's own edit artifact, see the methodology note).

Note the deeper point: the entry .pyc cannot be policed from inside the module it belongs to. Under `-m`, a forged .pyc replaces the module wholesale, so the scan code inside it never runs. The control for the entry .pyc must live outside the runner, in the launcher, before exec. See AMEND 1.

### C2-2 (HIGH): a planted .py executes before ANY refusal, on the production script path

The pre-import scan (run_codex_y5.py:157-181) refuses only `.pyc` files and symlinks. It never refuses a `.py` file, and it runs after the runner's own stdlib imports (lines 111-123) and before the `from run_live import` (line 185). With the script form, sys.path[0] is the ship dir, so a planted stdlib-shadow module executes during those imports, and a planted `run_live.py` executes at line 185. `_verify_manifest` refuses the plant, but only in main(), after the code already ran.

Probe 3c (probe3c_shadow.py): planted `glob.py` that writes a marker at import time, then loads the real glob via an explicit file location and re-exports it, so the runner keeps working:

```
planted glob.py (clean delegate), script form: rc=2
   out='{"manifest_ok": false, "files_checked": 27, "mismatches": ["unexpected file in ship dir: glob.py"], ...}'
marker exists: True content='SHADOW-EXECUTED'
```

Probe 10 (probe10_run_live_plant.py): same pattern for the pinned driver itself, planted `run_live.py` delegating to the real bytes kept aside:

```
planted run_live.py, script form: rc=2
   out='{"manifest_ok": false, "files_checked": 27, "mismatches": ["run_live.py: want 84fa106c253d5e7f16daccf2ce3f14a5, got 925db273a75f9479415251d20a471724"], ...}'
marker exists: True content='RL-EXECUTED'
```

Probe 3b confirms the second shadow target (`fnmatch.py`, also executed, marker present). My first attempt (probe3_shadow.py) planted `functools.py` and got no marker; that was a probe error, not a refutation: `functools` is preloaded by the interpreter (fresh `python3 -c` shows it in sys.modules before any user code), so it never loads from the ship dir. The corrected targets (`glob`, `fnmatch`) are not preloaded and are imported by the runner's own imports. The full shadow surface is every not-preloaded stdlib module the runner or run_live imports before the scan: `glob`, `fnmatch`, `re`, `json`, `pathlib`, `socket`, `subprocess`, `base64`, `hashlib`, `struct`, `http.client`, `urllib.parse`, and any manifest `.py` (`run_live.py` proven; `launch_y13.py` is not imported by the runner). This is the `.py` twin of H1, on the production path, under the same attacker capability H1 assumes (write one file into the ship dir). The M1 allowlist's premise, verify-before-execution, does not hold for `.py`.

### C2-3 (MEDIUM): the tokenizer misses every python flag that takes a value, not just -m

Probe 4: `python3 -W ignore run_codex_y5.py` and `python3 -X utf8 run_codex_y5.py` both return False in both copies. The prev-token rule (`_is_runner_cmdline`, run_codex_y5.py:3604, launch_y13.py:125) only handles a flag directly before the script; any flag whose value sits between the flag and the script breaks it. `-m` is one instance of this class, `-W`/`-X` are siblings. A patch that special-cases `-m` only would leave this class open. The fix must be a real python-argv parse (find the python token, skip flags and their values, take the first positional as the script candidate). See AMEND 3.

### C2-4 (MEDIUM): the -c splitter misses quoted and semicolon-joined script tokens

Probe 4: `sh -c 'python3 "run_codex_y5.py" all'`, `sh -c "python3 'run_codex_y5.py'"`, and `bash -c 'python3 run_codex_y5.py; echo done'` all return False in both copies. `_argv_tokens` splits the `-c` string on whitespace only (run_codex_y5.py:3584, launch_y13.py:107), so quotes stay attached to the token (`"run_codex_y5.py"` does not start with `run_`) and `;` stays attached (`run_codex_y5.py;` does not end with `.py`). The unquoted, space-separated `-c` form is caught. Fix: `shlex.split` for `-c` strings (fall back to whitespace split on error) plus stripping trailing `;`, `&`, `|` from tokens. See AMEND 3.

### C2-5 (LOW): name-based blindness to a symlink or renamed copy

Probe 4: `python3 /tmp/x/link.py` (symlink to the runner) and `python3 /tmp/x/batch3.py` (renamed copy) both return False in both copies, while `python3 /tmp/x/run_batch3_copy.py` returns True. The check matches names, never content, so any rename or symlink evades it. This is a deliberate-evasion class, not a documented launch form: no worker launches a renamed copy today, and the flock plus port backstops still apply to a renamed rival that holds the usual ports. I rate it LOW and propose the content-hash check below as optional hardening, not as a blocker. If the council wants it closed, the check is: resolve the script token to a file (via the process cwd for relative tokens, directly for absolute ones) and compare its md5 against the known runner md5s. See AMEND 4.

### C2-6 (MEDIUM): the H3 marker is content-free, date-forgeable, and remote-unchecked

Probe 7 (probe7_marker.py, synthetic bare remotes plus clones, the real `check_marker`/`check_manifest` imported from the repo):

```
A. trivial-diff completion: PASS ("Y6c completion marker found: ... (Y6c nested run DONE)")
B. marker on other branch only: REFUSE(rc=2) (git fetch failed: couldn't find remote ref todolist-push)
C1. completion T1 then abort T2 (baseline): REFUSE(rc=2) (abort is newer than the newest completion)
C2. same, plus completion with FORGED date T2+1h: PASS
D. fork remote (different origin path) marker: PASS (fork origin URL: /tmp/y13r2-council-2/p7/repoD-fork.git)
E. fork committed manifest == tampered ship manifest: PASS (ship manifest md5 matches committed)
E-control. no committed manifest in repoA: REFUSE(rc=2)
```

Concretely: (a) a commit whose subject is exactly `Y6c nested run DONE` and whose diff is a one-line change to a `worker-y6c-*.md` file passes; the gate never inspects diff content. (b) Committer dates are trusted for the freshness rule (`%ct`, launch_y13.py:264-325), and any committer can forge them with one env var (case C2 beats a genuinely newer abort). (c) `check_marker` never checks the remote URL: `--repo` pointing at a clone of a different remote passes with a forged marker, and `check_manifest` then compares the ship manifest against that same fork's committed manifest, so a tampered ship plus a matching forged manifest passes both gates (case E). The real-repo state bounds this today: the only Y6c commit on todolist-push is 5a2b69d (NO VERDICT, matches neither pattern), so no stale completion currently satisfies the gate. And the gate is an ordering signal among cooperating workers who can already push code, not an authentication boundary, so I rate this MEDIUM, not HIGH. Still, the ordering rule should be based on branch position, not forgeable dates, and the remote should be pinned. See AMEND 5.

### C2-7 (LOW): the codex rule refuses on a mere mention, and the warning branch fires on the word "codex" anywhere

Probe 6 (probe6_codex.py, live dummies with argv[0] set to `codex`, real `check_runner_quiet` per case):

```
A. codex + geckodriver arg: check rc=2 (REFUSED, correct)
B. plain codex: check rc=0 (WARNING only, correct per spec)
C. codex + geckodriver-notes.md filename: check rc=2 (REFUSED)
D. codex + marionette-notes substring: check rc=2 (REFUSED)
```

The rule as specified says "mentions", so C and D are per-spec behavior, but the boundary is worth recording: a codex process editing notes about geckodriver, or with `marionette` as a substring of an unrelated argument, blocks the launch. Fail-closed direction, so LOW. Separately, the warning branch (`"codex" in cmd.lower()`, launch_y13.py:232-258 and the preflight copy) fires on any process whose cmdline merely contains the substring, including the runner itself (`run_codex_y5` contains it; probe 5b shows the `-m` dummy warned as a "codex process") and unrelated fleet shell/ssh commands whose `-c` text mentions codex in a grep pattern (probe 5 output shows two such warnings for pids running ssh-laptop.sh). Warning noise only. Recommend matching the codex executable basename for the warning branch. See AMEND 6.

## Killed leads (tested, no hole)

- live_metrics plant (probe 9): a planted `live_metrics.py` in the ship, and a planted one via `LIVE_METRICS_DIR`, both do NOT execute against the staged ship (no marker, rc=2 for the ship plant on the unexpected file, rc=0 clean for the env-dir plant). Reason: the pinned run_live.py (commit 1e3901c) contains zero occurrences of `live_metrics`; the import exists only in the working-tree run_live.py (Y11, later commit). Forward note: the hole reactivates if the pin advances past the commit that added the import without adding `live_metrics.py` to the manifest and the scan allowlist. Any future pin bump must re-check run_live's import surface.
- Marker on the wrong branch correctly refuses (probe 7B). No stale Y6c completion exists on todolist-push today (only 5a2b69d, NO VERDICT).
- The entry exemption cannot be smuggled under a subdirectory: probe 8 case 8, an entry-named `.pyc` under `codex-y5/__pycache__/`, is refused (directory plus bytecode mismatches). A wrong-tag entry `.pyc` is refused (case 6). A symlinked directory and a non-prefix directory are refused by `_verify_manifest` (cases 1, 2). A forged `run_live` `.pyc` is refused by the scan in the real file; probe 8 case 3 shows it executes only when the scan call is stripped, which proves the scan (not `_verify_manifest`) is the load-bearing layer for `.pyc`, since `_verify_manifest` runs after the import.
- Tokenizer forms that DO catch, both copies: bare-relative, absolute, `./`, shebang exec, `python -u`, `python3.12`, `env VAR=1 python3`, `nohup`, `setsid`, `/usr/bin/python3`, `flock` file form, `flock -c`, `bash -c` unquoted, `bash -c exec python3`, `python3 --`, `run_live` by absolute path, Y6c `run-nested-pill.py` and `run-nested-wayland.sh` via bash, `hand_drive_e1.py`. Path mentions (`md5sum`, `grep`) correctly do not trip.
- Not findings, only limitations: `python3 -m tests.realistic.run_codex_y5` (no package structure exists, not a real path), zipapp launch, and a runner launched via `runpy` inside a `-c` string (arbitrary code in `-c` cannot be covered by token scanning). These are recorded, not counted.

## AMEND list (fixes required to lift the BLOCK)

1. Close the .py execution hole (C2-2) and the entry .pyc hole (C2-1) together, in the launcher first and the runner second. (a) The launcher must run a full allowlist scan of the ship dir BEFORE exec: every file must be a manifest path with matching md5, plus the manifest itself and SHIPPED.md; refuse any symlink, any non-prefix directory, and any `.pyc` at any depth, including the two entry `.pyc` files. The scan must run in the launcher process, whose own imports must resolve from stdlib only, so invoke the launcher with PYTHONSAFEPATH=1 and record that in the SHIPPED.md launch line. (b) Extend the runner's pre-import scan the same way (full allowlist plus md5s, no `.pyc` at all), as defense in depth; the launcher's exec env must add PYTHONSAFEPATH=1 alongside PYTHONDONTWRITEBYTECODE=1 (verified: script form `--verify-manifest` exits 0 under PYTHONSAFEPATH=1; `-m` under safepath fails with "No module named run_codex_y5", which is fail-closed and acceptable). (c) REMOVE the `_ENTRY_PYC` exemption from both the scan and `_verify_manifest` (run_codex_y5.py:149-155, 511, 535). It never helps a legitimate run pass (the directory check fails verify anyway) and it weakens the scan. Document that `-m` and plain `import` of the runner are probe forms only, require PYTHONDONTWRITEBYTECODE=1, and are never the live launch path. Re-test: rerun probes 1, 2, 3c, 8, 10 against the fixed bytes (all plants must refuse with no marker printed, including the `.py` plants and the forged entry `.pyc` under `-m`/import; the clean ship must still verify exit 0 under both the launcher env and the bare script form with PYTHONDONTWRITEBYTECODE=1).
2. Do NOT fix Finding 1 by exempting the `__pycache__` directory in `_verify_manifest` alone. That change without AMEND 1(c) would let a forged entry `.pyc` pass verify (probe 8 case 5 vs 6). If any directory exemption is kept, it must be paired with removal of the file exemption and with the launcher-side scan from AMEND 1. Re-test: probe 1 cases A-E plus probe 2A must all behave as in AMEND 1.
3. Replace the tokenizer's prev-token heuristic with a real python-argv parse, in BOTH copies (run_codex_y5.py:3604, launch_y13.py:125). Parse: find a python interpreter token; skip flags and their values (`-u -B -E -s -v -W <val> -X <val> -O -c <code> -m <mod>`, `--` separator); the first positional token is the script candidate. Accept a bare module name after `-m` when its basename is a known runner module (`run_codex_y5`, `run_live`, `run_agyq2`, `run_batch3`, `run_agy_y2`, `run-nested-pill`, `hand_drive_e1`) as well as the `.py` forms. For `-c` strings, split with `shlex.split` (fall back to whitespace split on error) and strip trailing `;`, `&`, `|` from tokens before matching. This closes Finding 2, C2-3, and C2-4 in one change. Re-test: rerun the probe 4 table (all real-path cases must catch, both copies agree) plus the probe 5b live `-m` case (check_runner_quiet must refuse rc=2 naming the `-m` dummy) and the path-mention cases (must still not trip).
4. Rename/symlink blindness (C2-5, LOW, optional hardening): resolve each script candidate token to a file (process cwd for relative tokens, directly for absolute ones) and compare its md5 against the known runner md5s, in addition to the name check. If this is not implemented, record the name-based limitation in the plan and rely on the flock plus port backstops. Re-test: probe 4 symlink and renamed-copy cases, live if implemented.
5. Harden the H3 marker gate (C2-6). (a) Order completions and aborts by branch position in `git log origin/todolist-push` order (topological order), not by committer date `%ct`, so a forged date cannot beat a genuinely newer abort. (b) Pin the remote: in `check_marker` and `check_manifest`, verify `git remote get-url origin` equals the expected origin URL for the real repo (read it from the real checkout's git config at fix time; refuse on mismatch). (c) Document that the marker is an ordering signal among pushers, not authentication. Re-test: rerun probe 7 (A must still pass, B must still refuse, C2 forged-date must now refuse, D fork remote must now refuse, E fork manifest must now refuse).
6. Codex rule boundary (C2-7, LOW). Keep the refuse rule as specified (any mention refuses, fail-closed). Change only the WARNING branch to match the codex executable basename (a token whose basename is `codex`, or a path ending in `/codex`) instead of the substring `"codex"` anywhere in the cmdline, so the runner itself and unrelated commands mentioning codex in passing no longer warn. Re-test: probe 6B still warns, probe 5b `-m` dummy no longer warns as codex (it must refuse as a runner instead, per AMEND 3), and a fleet shell command mentioning codex in a grep pattern no longer warns.

After the fixes: regenerate the manifest LAST from the final bytes, re-stage, re-run the full mechanical set (probes 1-10 equivalents plus the Y13f set), and get a fresh re-review of the fix diff only.

## Methodology notes (honest artifacts)

- Probe 8 strips only the `_refuse_tampered_ship()` call in a temp copy, which changes the runner's bytes, so every case 0-8 carries one extra `run_codex_y5.py: want 3cc5fa11..., got 9e5770d4...` mismatch from my own edit. Judgments rest on the EXTRA mismatches per case and on contrasts between cases (notably case 5 vs 6), not on the overall pass/fail.
- Probe 3's first plant target was wrong (`functools` is preloaded and never loads from the ship dir); the finding rests on the corrected targets in probes 3b/3c (`glob`, `fnmatch`) and probe 10 (`run_live.py`).
- Probe 5's first end-to-end run refused only because its bare-relative control dummy was also alive; probe 5b isolates the `-m` case.
- Probe 7 uses synthetic test identities and synthetic remotes only. No personal info appears in this paper or in the probes.

## Probe index

All probes under /tmp/y13r2-council-2/probes/: probe1_finding1.py, probe2_entry_pyc_forge.py, probe3_shadow.py, probe3b_shadow.py, probe3c_shadow.py, probe4_tokenizer.py, probe5_live_m.py, probe5b_live_m_only.py, probe6_codex.py, probe7_marker.py, probe8_verify_isolated.py, probe9_live_metrics.py, probe10_run_live_plant.py. Staged ships and markers under /tmp/y13r2-council-2/ (ship1, p1-ship*, p2-ship*, p3*-ship*, p8-*, p9-*, p10-*).
