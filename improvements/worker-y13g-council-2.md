# Y13g Council Voice 2 (adversarial): re-review of the Y13g fix diff

- Reviewer: Council Voice 2 (successor to Y13r2 Council 2), 2026-11-22 ~00:05-00:55 +07
- Scope: Y13g fix diff 431b2a9..HEAD, restricted to the 6 files Y13g touched (commits caa4a7c, 0cf43f8, 03303f4, 6cd0f7a, b815590; HEAD 4075e0e at review start). Manifest md5 0ca16ddd743acc9e28294fecd07a9c70, verified by re-running the regen script (same md5, staged ship --verify-manifest exit 0).
- Sources read in full: improvements/worker-y13g-fix-log.md, improvements/worker-y13r2-council-2.md (the predecessor paper, 6 amends), the fix diff for all 6 files, and the two entry-point files end to end (module tops, _verify_manifest, _proven_no_body, tokenizer block, preflight, launcher checks).
- Method: assume the fixes are wrong until proven right. All probes are my own fresh implementations in ~/workspace/y13g-council-2/probes/ (probe1/probe1b .so + pre-scan plants, probe2 tokenizer 79 cases, probe3 AST identity, probe4 ordering + divergence, probe5 remote pin, probe6 -m guard edges, probe7 live forms + codex warning + _proven_no_body, probe8 run_live .pyc). No live Zen driving, no ydotool, no commit to the fix files, no modification of any runner/launcher file. The independent verifier's files under improvements/y13g-verify/ were not used; every verdict below rests on my own probes.
- Verdict: **BLOCK**. One HIGH hole in the ship-integrity layer, reachable on the production path: a planted stdlib-stem `.so` executes before any refusal (C2-1). The runner's pre-import scan was never extended to the full allowlist + md5s that AMEND 1(b) required; it is a narrow denylist. The fix is mechanical (extend the scan to a full allowlist, os-only), so after it lands only a re-review of the fix diff is needed, not a re-review of the whole runner. Three MEDIUMs ride with it (dead entry-.pyc check, tokenizer residuals, guard deletion through a symlink).

## What was verified as fixed (the positive side)

- B1 exemption removed: no per-file entry-.pyc exemption remains in the scan (run_codex_y5.py:215-255) or in _verify_manifest (run_codex_y5.py:545-645); any .pyc at any depth is refused.
- B4 happy path works (probe6 G0): `-m` on a clean ship exits 2, leaves an empty __pycache__, and the direct form after is rc 0, manifest_ok true.
- B2 .py plants refused with no execution (probe1 case I, glob.py control): the scan refuses planted .py before any import, bare or -P.
- B3 common tokenizer forms catch, both copies agree on all 79 probe2 cases: -m forms, -W/-X values (separate and attached), -c exec(/eval( open(...)), quoted -c script tokens, -- separator, env -u/-i/VAR=1, timeout -k, flock file/-c forms, bash --norc/-x -c, script paths with spaces, md5 renamed/symlink/extensionless copies. The shared tokenizer block is AST-identical with docstrings stripped (probe3, 12 functions, raw text differs only in the 2 sync-direction notes).
- AMEND 2 pairing done: the __pycache__ dir exemption is narrow (top-level only, only when every entry is a current-tag entry name) and is paired with removal of the file exemption and with the launcher-side scan. Observably it is equivalent to exempting an empty __pycache__ only, since a non-empty one always fails on the files inside.
- AMEND 5 done in substance: marker ordering uses git log position, never a date (probe5 simulation: forged-date completion cannot beat a newer abort; only a fresh push on top passes, which is a new push, not a date trick); the remote is pinned to the exact https URL in both check_marker and check_manifest (probe5: no origin, SSH origin, trailing slash, no .git, wrong case, http, and a non-checkout path all refuse exit 2; only the exact pinned URL allows); the coordination-signal (not authentication) wording is in the docstrings, SHIPPED.md, and the plan.
- AMEND 5 (eval_error, the redteam's Amend 5 / _proven_no_body): `diag.get("eval_error") is not None` is implemented exactly (run_codex_y5.py:1062-1091). All 5 call sites (lines 1147, 1164, 1216, 1252, 4640) treat False as InfraError / "infra-blocked" (re-run); no caller relied on the old falsy behavior. Unit checks match, including eval_error "" -> False.
- Pre-scan startup imports do NOT execute plants (probe1 D/E/F/H, probe1b L): sitecustomize.py, usercustomize.py, and an encodings package plant do not execute in the bare, -P, or -m forms (site loads them before sys.path[0] is set); planted os.py does not execute (os is preloaded, verified: 'os' in sys.modules is True at startup).

## Check of Y13r2 Council 2's 6 amends against what Y13g implemented

1. AMEND 1 (close the .py hole and the entry .pyc hole together, launcher first). PARTIAL.
   (a) Launcher full-allowlist scan before exec + PYTHONSAFEPATH=1 + record in SHIPPED.md: DONE. _scan_ship (launch_y13.py:950-1012) is a full allowlist with md5s; the exec env sets PYTHONSAFEPATH=1 and runs `python3 -P`; SHIPPED.md records it.
   (b) Runner pre-import scan extended the same way (full allowlist plus md5s, no .pyc at all): NOT DONE. The runner scan (run_codex_y5.py:215-255) refuses only .pyc, symlinks, and planted .py. It does not verify md5s, does not refuse .so files, other files, or unexpected directories. This is the root of C2-1.
   (c) REMOVE the _ENTRY_PYC exemption from the scan and _verify_manifest: DONE. Document -m/import as probe-only, never the live path: DONE in docstrings, SHIPPED.md, and the plan (one stale line remains, see C2-9).
2. AMEND 2 (do not fix Finding 1 by exempting the __pycache__ directory alone). DONE. The file exemption is removed, the launcher-side scan exists, and the kept dir exemption is narrow and paired as required.
3. AMEND 3 (real python-argv parse, both copies). DONE in structure, PARTIAL in coverage. The parse exists and the two copies are AST-identical, but 20 of my 79 cases still miss (C2-3). The common forms are fixed; the residuals are all uncommon forms.
4. AMEND 4 (rename/symlink blindness, md5 hardening, optional). DONE. The md5 leg works for renamed, symlinked, and extensionless copies (probe2). LOW residuals only (C2-10).
5. AMEND 5 (harden the H3 marker gate: log order, remote pin, document). DONE in substance. Residuals are LOW (C2-6): strict-string false refusals, no --topo-order, and the content-free marker (which AMEND 5 did not ask to close).
6. AMEND 6 (codex warning matches the executable basename; refuse branch unchanged). PARTIAL. The warning now uses _is_codex_process, the runner itself no longer warns, and the ssh -c form no longer warns. But a bare "codex" argv token still warns (C2-5). The refuse branch is unchanged (substring), as required.

## Where Y13g went further than, or diverged from, the predecessor AMEND list

- FURTHER (good): the -m guard + deletion of entry .pyc files goes beyond AMEND 1(c)'s "remove + document"; it is the mechanism that makes B4's "direct form after -m is rc 0" true. The out-of-process marshal check (_check_entry_pyc) implements the redteam's B1(4) and the predecessor's "control must live outside the runner, in the launcher" - but see C2-2: on the actual launcher path it never runs.
- FURTHER (good): the tokenizer's md5 leg and -m last-dotted-segment handling go beyond AMEND 3's minimum (the md5 leg was AMEND 4, optional).
- DIVERGED (bad): AMEND 1(b) asked for the runner's pre-import scan to become a full allowlist plus md5s. Y13g implemented a narrow denylist instead ("narrow top scan (sys/os only, no json/pathlib)" in the fix log) and relied on the launcher's scan. A full allowlist of PATHS is achievable with os-only code (the manifest path set could be hardcoded exactly like _SHIP_PY); md5s are the only part that needs hashlib, and the scan does not need md5s to refuse a .so. The consequence is C2-1.
- DIVERGED (minor): the __pycache__ dir exemption's stem set (run_codex_y5, launch_y13; current tag only) does not match the guard's stem set (launcher guard: 3 stems, all tags). A run_live .pyc or a stale-tag .pyc is never exempt from the dir refusal. Fail-closed, but inconsistent; see C2-2 and C2-7.
- OVERCLAIM (doc): the plan's B3 bullet says bundled/attached flag forms are handled, but -uc/-Bc are missed (C2-3). The plan's B1/B4 bullets say the launcher verifies + deletes entry .pyc before exec, but check_manifest refuses first (C2-2).

## Findings

### C2-1 (HIGH): a planted stdlib-stem `.so` executes before any refusal; the runner scan is a denylist, not a full allowlist; `-P` is never enforced

- Files: run_codex_y5.py:215-255 (module-top scan), run_codex_y5.py:272 (`sys.path.insert(0, _SHIP_DIR)`), run_codex_y5.py:3711-3728 (`_shlex_tokens`, lazy `import shlex` at line 3716), launch_y13.py:188-230 (module-top scan), launch_y13.py:248-253 (post-scan imports hashlib/json/re/socket/subprocess/time).
- Evidence (probe1/probe1b/probe2, all on fresh staged ships):
  - A. Planted `glob.cpython-312-x86_64-linux-gnu.so`, runner bare form: marker PRESENT, rc=2 (verify refused AFTER execution). The .so executed at the runner's own `import glob`.
  - N. Planted `http.cpython-312-x86_64-linux-gnu.so`, runner bare form: marker PRESENT, rc=1 (`ModuleNotFoundError: No module named 'http.client'; 'http' is not a package` - the .so replaced the http package during `import urllib.request`).
  - K. Planted `hashlib.cpython-312-x86_64-linux-gnu.so`, LAUNCHER bare form (no -P, no Y13_GO): marker PRESENT, rc=2 (refused on Y13_GO only after the .so executed at the launcher's post-scan `import hashlib`).
  - M + probe2 SHLEX-LIVE-PATH. Planted `shlex.cpython-312-x86_64-linux-gnu.so`, runner WITH -P: calling the runner's own `_is_runner_cmdline` on a `bash -c` cmdline executed the plant (marker PRESENT) while returning True. The runner lazily imports shlex in `_shlex_tokens` (line 3716) AFTER `sys.path.insert(0, _SHIP_DIR)` (line 272); preflight calls `_is_runner_cmdline` for every /proc entry, so any `-c` process present during preflight triggers it. This is the -P bypass: -P protects only the imports that happen before the sys.path insert.
  - Killed for contrast: re/json/http .so under -P via run_live do NOT execute (probe1 B/C, probe1b J), because the runner already imported those modules from stdlib before the insert, so run_live reuses them. The live stems under -P are the ones the runner does NOT import at top and that something imports later: shlex (lazy, proven) is the one in this codebase.
- Root cause: the module-top scan refuses only .pyc, symlinks, and planted .py. A `.so` file is none of those, so it passes the only pre-import gate. `_verify_manifest` refuses it (unexpected file) but runs in main(), after the imports. Neither file checks `sys.flags.safe_path` anywhere, so the `-P` requirement is documentary only: a bare invocation is never refused, and the launcher's own post-scan imports then load a plant (case K). The old SHIPPED.md launch line had no -P, so a bare invocation is one forgotten flag away.
- Proposed fix: (1) extend the module-top scan in BOTH files to a full allowlist using os-only code: refuse any file whose relative path is not in the manifest path set (hardcode the set exactly like _SHIP_PY) and refuse any unexpected directory; a `.so` is then refused before any import, which also closes the shlex leg. (2) Enforce `sys.flags.safe_path` in both entry points: refuse (exit 2) when run without -P, or at minimum refuse the bare form for the launcher. (3) Defense in depth: pre-import shlex at the top (before the sys.path insert) so the lazy import can never load a plant, and import run_live without inserting the ship dir at sys.path[0] if feasible.
- Re-test: rerun probe1/probe1b against the fixed bytes (all .so plants must refuse with NO marker, bare and -P, runner and launcher, plus a full-run-equivalent shlex trigger through _is_runner_cmdline).

### C2-2 (MEDIUM): `_check_entry_pyc` is dead code on the launcher path; a legitimate entry .pyc bricks the LAUNCHER path; run_live's .pyc is never cleaned by the runner's guard

- Files: launch_y13.py:806-863 (`check_manifest`, .pyc refusal), launch_y13.py:880-949 (`_check_entry_pyc`), launch_y13.py:1107-1110 (main order: check_marker, check_manifest, _check_entry_pyc, _scan_ship), run_codex_y5.py:131-143 (`_ENTRY_PYC_NAMES`, 2 stems), run_codex_y5.py:138-158 (guard, 2 stems).
- Evidence (probe4 Part 1, probe8): a LEGITIMATE entry .pyc (py_compile, never executed) is refused by check_manifest as "planted bytecode in ship" BEFORE _check_entry_pyc runs, so the verify-and-delete path never executes on the launcher path. Called directly, _check_entry_pyc works correctly (legit .pyc verified + deleted, forged .pyc refused on marshal mismatch), so the failure is ordering, not the function. Separately, a run_live .pyc survives the RUNNER's -m guard (2 stems only) and bricks the direct verify (scan refuses, kind pyc); only the launcher's -m guard (3 stems) deletes it, and only when launch_y13 itself is the imported module.
- Consequence: the B1(4)/B4(2) recovery Y13g claims ("the launcher verifies the entry .pyc out-of-process and deletes it before exec") never runs. Any legitimate entry .pyc that survives the guard (py_compile, a guard unlink failure, a run_live probe) bricks the LAUNCHER path with "planted bytecode" and needs manual deletion - the exact B4 brick, moved to the launcher. The forged-.pyc-via-launcher case still refuses, but by check_manifest's blanket refusal, not by the marshal comparison, so the marshal check itself is untested by any live path.
- Proposed fix: reorder main() to run _check_entry_pyc BEFORE check_manifest's .pyc refusal (check_marker, _check_entry_pyc, check_manifest, _scan_ship), or exempt the 3 entry stems from check_manifest's .pyc refusal pending _check_entry_pyc. Add run_live to the runner's guard stem list and to _ENTRY_PYC_NAMES so the runner's guard and the verify dir exemption cover all 3 entry files.
- Note (code reading, not a separate hole): the marshal comparison itself is sound - it skips the 16-byte header, so hash-based and timestamp-based .pyc are both handled; it compares re-dumped marshalled code objects, so a forged code object refuses and a different-Python-version .pyc fails closed (unmarshallable or dump mismatch); truncated (len <= 16) and corrupt .pyc refuse; the subprocess -c code takes the source path as argv (sys.argv[1]), not interpolated, with no shell, so no injection via the src path. One fail-closed quirk: co_filename is part of the marshalled code object, so a .pyc compiled from a different path string mismatches and refuses instead of verifying + deleting.

### C2-3 (MEDIUM): tokenizer residuals - 20 of 79 cases still miss (corrected count)

- Files: run_codex_y5.py:3822-3881 (`_python_executes_runner`), run_codex_y5.py:3883-3971 (`_command_executes_runner`), run_codex_y5.py:3794-3820 (`_c_code_executes_runner`); launch_y13.py has the identical block (probe3).
- Evidence (probe2, 79 cases, both copies agree on all 79; probe7 live confirmations). Misses, each a real execution form:
  - `-m pdb` + script: pdb's _ScriptTarget namespace sets `__spec__=None`, so the guard does NOT fire and the suite runs (probe7 pdb live: manifest_ok true, no guard message). The tokenizer's -m branch returns False for any non-runner module without inspecting the following args.
  - `python3 -` (stdin, 2 rows): `cat run_codex_y5.py | python3 - --verify-manifest` executes the runner (probe7 S1, manifest_ok true; __file__ is "<stdin>", __spec__ is None). The tokenizer returns False for tok == "-".
  - `-uc` / `-Bc` bundled -c (probe7 S4: `-uc` runs the code, BUNDLED-C-WORKS). A bundled flag token containing 'c' after another flag is skipped wholesale, and the code string is then misread as a positional script candidate.
  - `timeout 60s` / `1m` (probe7 S5: timeout accepts unit suffixes). The duration skip requires pure digits, so "60s" is treated as the command.
  - `bash -c 'python3 run_codex_y5.py;echo done'` and `...&&echo done` (glued separators): `_shlex_tokens` rstrips trailing separators only, so a separator glued mid-token survives and the script token never matches.
  - `-c` runpy.run_path / os.system / split-concat exec: `runpy.run_path('run_codex_y5.py')` inside -c is not covered (the predecessor recorded runpy-in--c as a limitation; it is still open); `os.system('python3 run_codex_y5.py')` is not covered (documented limit in the code); `exec(open('run_'+'codex_y5.py').read())` defeats the literal-name regex.
  - pypy3 (interpreter token not in the python set); unlisted wrappers nice/sudo/stdbuf/uv run (the wrapper set is an allowlist, so every new wrapper is a miss); `exec -a` (the -a argument is misread as the command).
  - FIFO script token and unreadable copy: the md5 leg fails open (isfile False / open raises). See C2-10.
  - False positives (fail-closed, 2 rows): a compiled non-python binary named run_codex_y5 or run_live is flagged by the bare-module-name stem check. Harmless direction, noted for completeness.
- Corrected rows (NOT misses, verified live + stdlib source): `-m runpy` + script and `-m cProfile` + script are correctly NOT caught - runpy sets __spec__ (probe7 S2, guard fires) and cProfile sets '__spec__' explicitly in its globs (probe7 S3, guard fires, suite does not run). Oddity worth a footnote: -m cProfile exits rc 0 while refusing (cProfile swallows the guard's SystemExit).
- Proposed fix, per class: in the -m branch, when the module is not a known runner, inspect the following args for a script candidate for modules that run scripts with __spec__ None (at minimum pdb; runpy/cProfile are already safe via the guard). In the bundled-flag branch, treat a token containing 'c' after other flags as -c (code is the rest of the token, else the next arg). Accept timeout durations with unit suffixes (strip a trailing [smhd] / decimal + unit). Split -c tokens on ; & | mid-token, not just trailing. Treat `python3 -` as a possible runner (fail-closed) or record it as a known uncovered form. Add pypy3 (and a generic "unknown wrapper followed by a python token" rule) instead of growing the wrapper allowlist one name at a time. Extend the -c exec regex to runpy.run_path and os.system, or record both as known limits in the plan.

### C2-4 (MEDIUM): the -m guard deletes through a symlinked `__pycache__`, deleting a file OUTSIDE the ship before the scan runs

- Files: run_codex_y5.py:138-158 (`_entry_pyc_paths` + guard), launch_y13.py:144-160 (same).
- Evidence (probe6 G1): with __pycache__ a symlink to an outside dir holding a legitimate `run_codex_y5.cpython-312.pyc`, a `-m` probe deleted the outside file (still exists: False). The guard runs before the scan, and `os.listdir` follows the symlink, so the deletion primitive fires before the scan can refuse the symlinked dir.
- Proposed fix: before deleting, require the cache dir to be a real directory inside _SHIP_DIR (compare os.path.realpath(cache) against os.path.realpath(_SHIP_DIR)); refuse to follow a symlinked __pycache__ (let the scan refuse it instead). Or reorder: run the scan's symlink refusal before the guard's deletion (the scan already runs before any import, so scan-then-guard is safe).

### C2-5 (LOW): codex warning is only partly fixed (AMEND 6)

- Files: run_codex_y5.py:3999-4029 (`_is_codex_process`), launch_y13.py:584-602 (same).
- Evidence (probe7): the runner itself no longer warns (W5) and the ssh -c form no longer warns (W2) - both fixed. But a bare "codex" argv token still warns (W1 `grep codex file`, W7 `echo codex`), and a path merely containing a codex directory still warns (W8 `/path/codex/run_codex_y5.py`). The predecessor's re-test ("a fleet shell command mentioning codex in a grep pattern no longer warns") fails for the direct grep form. Warning noise only; the refuse branch is unchanged (substring), as required.
- Proposed fix: match only argv[0] whose basename is "codex", or a token that is a path ENDING in "/codex" (an execution position), not any token with a "codex" path component.

### C2-6 (LOW): remote pin is strict-string (false refusals) and the marker check has no --topo-order; the marker stays content-free

- Files: launch_y13.py:251 (`KNOWN_REMOTE_URL`), launch_y13.py:722-739 (`_check_remote`), launch_y13.py:741-804 (`check_marker`, git log call without --topo-order).
- Evidence (probe5): fail-closed for no origin, SSH origin, trailing slash, no .git, wrong case, and http - all refuse exit 2. The real checkout uses the exact pinned https URL (verified: `git remote get-url origin` on this checkout matches), so this does not block the real launch; but any operator checkout with an SSH remote, or an equivalent URL spelling, can never launch. Marker ordering by log position is correct (probe5 simulation). Residuals: the log call does not pass --topo-order, so with a merge the order between independent lines is date-influenced (for linear history it equals branch position); and the marker is still content-free (a one-line diff to a worker-y6c-*.md file with the exact subject passes, no diff inspection) - a documented coordination-signal limit that AMEND 5 did not ask to close. A git `url.<base>.insteadOf` redirect could also defeat the string pin, but that needs git-config write access, outside the file-plant threat model.
- Proposed fix: normalize the URL before comparing (strip a trailing "/", accept an optional ".git", case-fold the host, accept the SSH form git@github.com:phamTuan207/computer-use-wayland.git for the same repo). Add --topo-order to the git log call. Keep the content-free marker documented, or add a diff-content check if the council wants it closed.

### C2-7 (LOW): -m guard gaps - nested and non-cpython-tag .pyc survive and brick the ship; scan/verify diverge on odd __pycache__ shapes

- Files: run_codex_y5.py:138-158 (guard), run_codex_y5.py:215-255 (scan), run_codex_y5.py:545-645 (verify).
- Evidence (probe6): G2 nested `__pycache__/sub/run_codex_y5.cpython-312.pyc` survives the guard (listdir is non-recursive) and bricks the direct run (scan refuses, kind pyc). G3 `run_codex_y5.pypy38.pyc` survives (the guard matches only ".cpython-") and bricks the direct run. G5 (a directory named `run_codex_y5.cpython-312.pyc` inside __pycache__) and G6 (__pycache__ as a file) survive the guard and PASS the scan (the scan sees a dir, not a file, and a file not ending .pyc/.py), but verify refuses (unexpected directory / bytecode). G4 (unreadable __pycache__ dir) is not testable on this VM (root + overlay FS lets listdir succeed on a mode-000 dir); by code reading, on a non-root laptop account the guard's listdir fails, the scan's os.walk silently skips the dir (blind), and verify refuses via the dir-exemption listdir failure - fail-closed at verify.
- Proposed fix: make the guard recursive over __pycache__ and match any implementation tag, not just ".cpython-". The full-allowlist scan fix in C2-1 subsumes the G5/G6 divergences (any unexpected file/dir refuses).

### C2-8 (LOW): uncaught subprocess exceptions in the launcher exit 1, not the documented exit-2 refusal

- Files: launch_y13.py:722-739 (`_check_remote`), launch_y13.py:768-804 (`check_marker` fetch/log), launch_y13.py:840-863 (`check_manifest` git show). None catches FileNotFoundError (git missing) or subprocess.TimeoutExpired (timeout=30/60/120). Both are still fail-closed (non-zero exit) but produce an uncaught traceback instead of the "[launch_y13] REFUSED" exit-2 path.
- Proposed fix: wrap the subprocess.run calls in try/except (OSError, subprocess.TimeoutExpired) and _fail.

### C2-9 (LOW): plan and SHIPPED.md overclaim what the code does

- Files: improvements/worker-y13-codex-y5-live-plan.md (Y13g amendments section), tests/realistic/codex-y5/SHIPPED.md.
- Details: the plan's B1/B4 bullets say the launcher verifies each entry .pyc out-of-process and deletes it before exec (dead code, C2-2); the B2 bullet says check_manifest refuses any planted file (it refuses only symlinks, .pyc, and top-level .py - probe4 Part 2 D-pass rows for .so/.txt/dirs/subdir-.py); the B3 bullet says bundled/attached flag forms are handled (-uc/-Bc are missed, C2-3); the plan still carries the stale line "Probes importing the runner must use PYTHONDONTWRITEBYTECODE=1" although the guard now makes that unnecessary. SHIPPED.md says "Launch ONLY via the launcher, never directly" while the regen script's staged verify and the verifiers use the direct form.
- Proposed fix: correct the bullets to match the code (state the check_manifest-before-_check_entry_pyc order, the exact check_manifest plant set, and the bundled-flag gap); either enforce "launcher only" or document the direct form as supported with its -P requirement.

### C2-10 (LOW): md5 leg edges - FIFO and unreadable files fail open; renamed .sh copies are not in the md5 set; no size cap

- Files: run_codex_y5.py:3729-3755 (`_runner_md5s`), run_codex_y5.py:3756-3779 (`_path_is_runner_copy`).
- Evidence (probe2): a FIFO script token returns False (isfile False; a FIFO streaming runner bytes would execute but cannot be md5'd without blocking). An unreadable copy returns False (open raises PermissionError, caught, returns False). A renamed .sh copy is not caught by md5 (the set holds only the 3 .py md5s; the Y6c run-nested-wayland.sh bytes are not in this ship's manifest). The md5 leg reads the whole file with no size cap.
- Proposed fix: document the FIFO/unreadable fail-open (the unresolvable-path fail-open is already documented in the docstring); add the Y6c .sh files to the md5 set or document the gap; check os.path.getsize before reading and refuse to md5 files over a sane size.

### C2-11 (LOW): `_proven_no_body` treats an explicit eval_error None as absent

- Files: run_codex_y5.py:1062-1091.
- Details: `diag.get("eval_error") is not None` returns False for a missing key (correct) but also treats an explicitly-None eval_error as absent, so a diag with eval_error None and a hasBody False + complete snapshot returns True (probe7 unit check). Unreachable today: run_live sets non-empty strings or omits the key (per the docstring), and all 5 callers treat False as INFRA. Hardening only.
- Proposed fix: use `"eval_error" in diag` instead of the is-not-None check, or leave as is and note the None edge in the docstring.

## Killed leads (tested, no hole)

- sitecustomize.py / usercustomize.py / encodings package plants do not execute in the bare, -P, or -m forms (probe1 D/E/F/H, probe1b L). site loads them before sys.path[0] is set.
- Planted os.py does not execute (os is preloaded).
- re/json/http .so under -P via run_live do not execute (the runner already imported them from stdlib before the sys.path insert).
- The -m guard works for its covered stems (probe6 G0/G8); a missing entry .py fails cleanly (G7, rc 1, No module named).
- _check_entry_pyc itself is sound when called directly (probe4 Part 1): legit .pyc verified + deleted, forged .pyc refused on marshal mismatch.
- The remote pin fails closed in every tested variant (probe5); marker ordering ignores dates entirely (probe5 simulation).
- The tokenizer's -m runpy and -m cProfile rows are correctly NOT caught (probe7 S2/S3 + stdlib source: both set __spec__, so the guard kills those forms before the suite runs).
- The shared tokenizer block is AST-identical between the two files (probe3).

## Probe index

All probes under ~/workspace/y13g-council-2/probes/ (persistent, outside the repo); staged ships under ~/workspace/y13g-council-2/ship (clean) and per-probe work dirs.
- probe1_prescan.py (+ plant_so.c): 9 cases, .so + startup-import plants. A CONFIRMED, B/C/D/E/F/G/H/I killed or control.
- probe1b_so_followup.py: 5 cases. J killed, N/K/M CONFIRMED, L killed.
- probe2_tokenizer.py: 79-case unit table + SHLEX-LIVE-PATH. 20 misses (corrected), 2 FPs.
- probe3_ast_identity.py: shared-block AST identity. Identical with docstrings stripped.
- probe4_ordering.py: check_manifest vs _check_entry_pyc ordering + 12-row divergence table.
- probe5_remote.py: 8 _check_remote variants + marker-order simulation.
- probe6_guard.py: 9 guard edge cases (G0-G8).
- probe7_liveforms.py: stdin / -m runpy / -m cProfile / -uc / timeout-unit live forms, 8 codex-warning cases, 5 _proven_no_body call sites + 9 unit checks.
- probe8_runlive_pyc.py: run_live .pyc stem gap + stdlib pdb/cProfile/runpy source checks.

## Methodology notes (honest artifacts)

- This VM runs as root (uid 0) on an overlay FS. Two permission-sensitive results are artifacts of that, and are reported as code-reading verdicts instead: probe6 G4 (unreadable __pycache__ dir - listdir succeeds here, would fail for a non-root laptop account) and probe2's unreadable-copy row (a mode-000 file is unreadable even to root on this FS, so the md5 leg fails open here; on a normal single-user system the same-uid rival could not read it either, so that row matters only across uids).
- Probe2's -m runpy / -m cProfile expectations were corrected after live testing (probe7 S2/S3): my first table counted them as misses, but both forms hit the -m guard, so the tokenizer is right not to catch them. -m pdb is the real miss (pdb sets __spec__=None, verified live and from the pdb source).
- The verifier's files under improvements/y13g-verify/ were present in the worktree during this review; I did not read or use them, and my probes are independent implementations.
- The regen script was run once to stage my clean ship; it rewrote the manifest with the identical md5 (0ca16ddd...) and removed the untracked tests/realistic/__pycache__. No fix file was modified by this review.
