# Y13g Council Voice 2 (adversarial): re-review of the Y13g ROUND-2 fix diff

- Reviewer: Council Voice 2 (adversarial/edge-case), 2026-11-22 ~01:00-02:40 +07
- Scope: round-2 diff ONLY, commits 0639d04, 87eec47, 6ba43f2, 8bdd5aa, 5a9b9e8 on todolist-push (HEAD 334cf69 at review start). Files: tests/realistic/run_codex_y5.py, tests/realistic/launch_y13.py, tests/realistic/codex-y5-manifest.json, tests/realistic/codex-y5/SHIPPED.md, improvements/worker-y13-codex-y5-live-plan.md, tests/realistic/regen_codex_y5_manifest.py. Pins verified live by re-running the regen script: runner md5 d5047ff573820491263a2eb3805105f4, launcher 8e72a5ce85cbaf8382f998987e8890e5, run_live 84fa106c253d5e7f16daccf2ce3f14a5 (pin 1e3901c holds), manifest 7c76383402e4c50b28adab6b25a22e09, 27 files, staged ship 29 files, --verify-manifest exit 0.
- Sources read in full: improvements/worker-y13g-council-2.md (round-1 BLOCK), improvements/worker-y13g-redteam.md (round-1 AMEND), improvements/worker-y13g-fix-log.md (adjudication R1-R10 + round-2 implementation notes), the round-2 diff for all 6 files, and both entry-point files end to end (module tops, scan, guard, _verify_entry_hashes, tokenizer block, _check_entry_pyc, check_manifest, _scan_ship, _check_remote, check_marker, _proven_no_body, main() order).
- Method: assume the round-2 fixes are wrong until proven right. All probes are my own fresh implementations in ~/workspace/y13g-r2-council-2/probes/ (probe1_r1, probe2_r2, probe2x_r2_defect, probe2y_f1, probe3_unit, probe3live, probe3live_fix, probe3wrap, probe3wrap2, probe4_r4, probe5_r5, probe6_7_8_9, r2common), staged ships under ~/workspace/y13g-r2-council-2/ship. No live Zen driving, no ydotool, no commit to the fix files, no modification of any runner/launcher file. The independent verifier's files under improvements/y13g-verify/ were not used; every verdict below rests on my own probes.
- Verdict: **AMEND**. No HIGH: nothing executes attacker code on a supported flow, and every failure below is either a fail-closed refusal or an exotic-form evasion mitigated by the ports backstop. But the round-2 headline fix R2 does NOT work: check_manifest's entry-.pyc exemption is unsatisfiable, so _check_entry_pyc still never runs on the live flow and a legitimate entry .pyc still bricks the launcher (C2-1, MEDIUM, the round-1 C2-2 defect verbatim, now with a one-line root cause). And the tokenizer rewrite leaves a new generation of live-proven evasions (C2-2, MEDIUM): `python3 -- -`, -c argv/env smuggling, a wider -c sink gap, and `-m trace`. Fix C2-1 and C2-2 plus the LOWs, re-run probes P1/P2/P3, then a focused re-review of that fix diff only.

## What was verified as fixed (the positive side)

- R1 (round-1 C2-1 HIGH) FIXED: glob.so + shlex.so refuse rc 2 with NO marker on the runner, bare and -P; hashlib.so refuses on the launcher, bare (safe_path gate) and -P (scan), no marker. All P1b shapes refuse on both paths: planted .txt, unexpected dir, nested __pycache__, __pycache__ as a file, .pyc-named dir (top + nested), case-variant .py, manifest file replaced by a dir. Bare and -E refuse at the safe_path gate; -I and PYTHONSAFEPATH env pass because they set the flag (legitimate, not bypasses). The scan is a true full allowlist: _SHIP_FILES identical in both files, 29 paths = manifest 27 + manifest + SHIPPED.md.
- R3 round-1 residuals FIXED (P3 fix cases, 14/14): -m pdb, -uc/-Bc bundles, timeout 60s/1m units, glued `;` separators, pypy3, wrappers nice/sudo/stdbuf/taskset/uv, exec -a, -c os.system/runpy.run_path literals, stdin `-`, -uW flag values. Redteam F3's renamed-copy exec (exec(open('mycopy.py').read()) with __file__ preset) is caught by the md5 leg in both files. Correct non-matches still pass: grep/md5sum/pytest/runpy/cProfile/import/print-mention.
- R4 (round-1 C2-4) FIXED: symlinked __pycache__, symlinked subdir inside __pycache__, and symlinked entry .pyc file all delete NOTHING outside the ship on -m (P4a/P4f/P4g); the direct form refuses each symlink. Guard is recursive + any-tag: nested entry .pyc and pypy38-tag .pyc are deleted by the -m guard (P4b/P4c).
- R5 (redteam F5) FIXED for the direct path: tampered run_live.py (manifest untouched) refuses BEFORE import, rc 2, no marker (P5a); tampered launch_y13.py likewise (P5e). Missing / dir / corrupt / files-less manifest all refuse rc 2 (P5d). The self-consistent tamper still executes on the direct path (P5b, documented limit) and the launcher's git comparison refuses it (P5c).
- R6 (round-1 C2-5) mostly FIXED: bare codex token and path-contains-codex-dir no longer warn (P6, 14 cases, both files agree).
- R7 (round-1 C2-6) FIXED: remote normalization 20/20 (exact, trailing slash, no .git, SSH form, host/scheme case) + --topo-order present on the marker git log call.
- R8 (round-1 C2-8) FIXED for the listed calls: _check_remote with git missing from PATH fails via _fail exit 2, no traceback; check_marker with a dead-proxy fetch fails via _fail exit 2.
- R9 (round-1 C2-11) FIXED: _proven_no_body 12/12, eval_error None returns False, "" returns False, missing key with a good snapshot returns True.
- R1/R3 mechanics: the shared tokenizer block is AST-identical between the files (14 functions + 3 constants, 17 parts); the two copies agree on all 63 unit cases. The md5 leg carries the 10 MB size cap in code. F1 (documented -m/import residual) re-confirmed on round-2 bytes: a properly re-headed forged entry .pyc via -m prints its marker, and the launcher path refuses it pre-exec.

## Findings

### C2-1 (MEDIUM): R2 NOT fixed, check_manifest's entry-.pyc exemption is unsatisfiable; _check_entry_pyc still never runs on the live flow

- Files: tests/realistic/launch_y13.py:1197 (`if (not rel_root and _is_entry_pyc_rel(rel))`), launch_y13.py:1242-1313 (`_check_entry_pyc`), launch_y13.py:1468-1472 (main order: check_manifest, _check_entry_pyc, _scan_ship).
- Evidence (probe2_r2, probe2x_r2_defect, all on fresh staged ships):
  - A LEGITIMATE entry .pyc (py_compile of the real ship source) is refused by check_manifest as "planted bytecode in ship: __pycache__/run_codex_y5.cpython-312.pyc" for all 3 stems (run_codex_y5, run_live, launch_y13), before _check_entry_pyc runs. Direct verify afterwards stays rc 2, kind pyc.
  - The condition is unsatisfiable by construction. An entry .pyc lives in `__pycache__/`, so in the os.walk rel_root is `"__pycache__"` (truthy) and `not rel_root` is False. The only way `not rel_root` is True is rel_root `""`, where rel cannot start with `"__pycache__/"` and `_is_entry_pyc_rel` is False. Direct evaluation: COND rel_root=`'__pycache__'` exempt=False; the conjunction never fires in the real walk.
  - The module-top scan exemption DOES work (real binary with a legit entry .pyc reaches check_go, no scan refusal, all 3 stems), and _check_entry_pyc itself WORKS when called directly (legit verified + deleted for all 3 stems, forged refused on marshal mismatch, probe2x). So the failure is exactly one wrong condition in check_manifest, not the function and not the scan.
  - Consequence: the R2 deliverable ("a legit entry .pyc is verified + deleted by the launcher, not refused") fails its own re-test. Redteam F4's re-test (py_compile / import run_live unbricked without manual deletion) FAILS on the launcher flow too (P2e), not just the direct path. A forged entry .pyc still refuses, but only via check_manifest's blanket refusal, never via the marshal comparison, so the marshal check is still untested by any live path. A wrong-tag legit .pyc refuses the same way (fail-closed).
- Proposed fix: drop `not rel_root and` at launch_y13.py:1197 (use `if _is_entry_pyc_rel(rel):` alone; it already requires the `__pycache__/` prefix and no subdir). Re-test: P2a (legit verifies + deletes for all 3 stems, direct verify rc 0 after) and P2e (py_compile / import run_live unbricked by the launcher flow).
- Note: the plan's B1/B4 wording and the round-2 section claim the launcher verifies + deletes entry .pyc; that claim is false until this fix lands (see C2-9).

### C2-2 (MEDIUM): R3 tokenizer residuals, new generation, all proven live executions

- Files: tests/realistic/run_codex_y5.py:3868-4270 (tokenizer block), tests/realistic/launch_y13.py:453-855 (identical block, AST-verified).
- Evidence (probe3_unit 63 cases, both copies agree on all 63; probe3live + probe3live_fix, every case below prints manifest_ok true on a fresh staged ship while the tokenizer returns False):
  - (a) `python3 -- -` (stdin after `--`): tokenizer False (after `--` the `-` goes through `_token_is_runner_script`, which returns False); live EXECUTES, rc 0, manifest_ok true. One-character variant of the fixed `-` row.
  - (b) -c argv/env smuggling (no runner literal anywhere in the code string): `python3 -c "import sys; __file__=sys.argv[1]; sys.argv=sys.argv[1:]; exec(open(__file__).read())" run_codex_y5.py --verify-manifest` EXECUTES rc 0; the unrepaired form also reaches main() (rc 2, "unknown tests"); `runpy.run_path(sys.argv[1], run_name='__main__')` EXECUTES rc 0; `os.system('python3 -P '+sys.argv[1]+' --verify-manifest')` EXECUTES rc 0; `__file__=os.environ['R']; exec(open(__file__).read())` EXECUTES rc 0. A cmdline-only check cannot see env at all; the fix would need /proc/PID/environ.
  - (c) -c sink gaps (literal present, sink missing, so the basename/md5 legs never run): os.execv, os.execve, os.execl, os.spawnl, os.spawnv, os.popen, subprocess.getoutput, subprocess.getstatusoutput, `__import__('os').system`, `__import__('subprocess').run`, `__import__('runpy').run_path`, pty.spawn. Each live EXECUTES rc 0 with manifest_ok true. (One probe note: `__import__('runpy').run_path('run_codex_y5.py', run_name='__main__')` without --verify-manifest accidentally ran the full suite: fixture fetches 404, rc 2, no Zen driving, no ports left listening, no log clobbered.)
  - (d) `-m trace --count run_codex_y5.py --verify-manifest`: live EXECUTES rc 0, manifest_ok true. The guard does not fire for -m trace, and the tokenizer's -m branch only special-cases pdb.
- Mitigation (why MEDIUM, not HIGH): every one of these runs the runner in-process, so a suite run binds ports 8771/4452 and check_ports refuses a second launch; check_runner_quiet scans every /proc entry, so the miss only matters for the in-process form itself. No standard worker form uses these.
- Proposed fix, per class: (a) treat `-` as a possible runner in the post-`--` position too (or treat any `-` token after `--` as stdin). (b) When a -c sink is present, also treat `sys.argv[N]` / `os.environ[...]` path sources as runner candidates (fail-closed: a -c sink whose path comes from argv/env counts when the argv/env value is a runner script; at minimum document argv/env smuggling as a known limit alongside string-concatenation). (c) Extend the sink list to the os.exec*/spawn*/popen family, subprocess.getoutput/getstatusoutput, pty.spawn, and `__import__(...)` obfuscated attribute access (match `__import__('os').system(` etc. by normalizing `__import__('X').Y(` to `X.Y(`). (d) In the -m branch, treat `trace` (and any -m module not known safe) like pdb: inspect following args for a runner script, or at minimum add `trace` to the pdb-style special case. Re-test: probe3_unit must reach 63/63 (with the refuted rows corrected, see below) plus probe3live/probe3live_fix all EXECUTE forms caught.

### C2-3 (LOW): PYTHONPATH survives -P; a plant in a PYTHONPATH dir executes at post-scan stdlib imports

- Files: tests/realistic/run_codex_y5.py:376-380 (post-scan `import glob` etc.), tests/realistic/launch_y13.py:400-408 (post-scan `import hashlib` etc.), launch_y13.py:1289-1300 (_check_entry_pyc fresh-compile subprocess, inherits env).
- Evidence (probe1_r1 P1f): PYTHONPATH=/tmp/evil holding glob.py (marker print), direct `python3 -P run_codex_y5.py --verify-manifest` rc 0, marker PRESENT. -P removes sys.path[0] only; PYTHONPATH dirs stay on sys.path (verified: `PYTHONPATH=/tmp/evil python3 -P -c` shows /tmp/evil first in sys.path). The same class hits the launcher's post-scan `import hashlib` and _check_entry_pyc's `python3 -P -c` compile subprocess (inherits env, imports marshal, so a planted marshal.py could forge the fresh-compile output and make a forged .pyc verify).
- Threat model: needs env control, outside the ship-tamper model, so LOW. But the docstring claim "-P keeps the ship dir off sys.path, so a planted stdlib .py cannot execute at import" is false when PYTHONPATH is set.
- Proposed fix: scrub PYTHONPATH (and PYTHONHOME) from the launcher's exec env and from the _check_entry_pyc subprocess env, and/or refuse at the module top when PYTHONPATH is set. Correct the docstring to name PYTHONPATH as a precondition.

### C2-4 (LOW): a ship missing SHIPPED.md passes every gate; the scan never refuses a missing file

- Files: tests/realistic/run_codex_y5.py:316-370 (scan refuses unexpected files only), launch_y13.py:327-381 (same), run_codex_y5.py:545-645 (_verify_manifest, manifest entries only).
- Evidence (probe1_r1 P1c): ship with codex-y5/SHIPPED.md deleted, direct verify rc 0, manifest_ok true. The scan iterates files present; a missing file is invisible to it. _verify_manifest checks only the 27 manifest entries, and SHIPPED.md is not one. The launcher's _scan_ship and check_manifest likewise never notice. A missing manifest itself refuses rc 2 (unreadable), so SHIPPED.md is the only silently-missing file.
- Proposed fix: refuse when any allowlist file is absent (walk _SHIP_FILES and require each to exist as a regular file), in both scans, or add SHIPPED.md to the manifest-checked set. SHIPPED.md is docs, not code, so this is integrity, not execution.

### C2-5 (LOW): R4 leftover empty nested dir still bricks the ship after the guard deletes the nested .pyc

- Files: tests/realistic/run_codex_y5.py:138-170 (_entry_pyc_paths, deletes files only), run_codex_y5.py:290-312 (_is_exempt_cache_dir, top-level only).
- Evidence (probe4_r4 P4b): nested `__pycache__/sub/run_codex_y5.cpython-312.pyc` is deleted by the -m guard (gone=True), but the empty `__pycache__/sub` directory remains, and direct verify stays rc 2, kind unexpected-dir, files ["__pycache__", "__pycache__/sub"]. The top-level empty __pycache__ is exempt, but an empty NESTED dir is not.
- Proposed fix: have the guard remove empty dirs it emptied (bottom-up rmdir after unlinking), or exempt empty nested dirs under __pycache__ in the scan.

### C2-6 (LOW): R6 codex warning still fires on mere mentions of the codex PATH

- Files: tests/realistic/run_codex_y5.py:4287-4303 (`_is_codex_process`), tests/realistic/launch_y13.py:872-888 (same).
- Evidence (probe6_7_8_9 P6): `grep /usr/bin/codex file`, `echo /codex`, and `ls /usr/bin/codex` all return True (warn). The /codex-suffix rule fires on any token ending in /codex, not only on a token in an execution position. The round-1 cases are fixed (bare `codex` token, path-contains-codex-dir no longer warn), so this is the residual half of C2-5.
- Proposed fix: match only argv[0] whose basename is codex, or a token ending in /codex that sits in an execution position (first non-wrapper token); a bare /codex path argument to grep/echo/ls must not warn. Warning noise only; the refuse branch is unchanged (substring), as required.

### C2-7 (LOW): R8 main exec subprocess.run is not wrapped; OSError gives a traceback exit 1, not the exit-2 refusal

- Files: tests/realistic/launch_y13.py:1503 (`proc = subprocess.run(cmd, cwd=SHIP_DIR, env=env)` in main(), no try/except).
- Evidence: inventory of every subprocess.run in launch_y13.py (probe P8c): lines 1068 (_check_remote), 1110 (fetch), 1119 (log), 1206 (git show), 1289 (fresh compile) are all wrapped in try/except (OSError, subprocess.TimeoutExpired) into _fail; line 1503 (the flock exec) is the only one not wrapped. Code-reading verdict: full main() was not run end to end (write_token would clobber the live handover token), so the OSError path is not live-proven, only read.
- Proposed fix: wrap the exec call in try/except (OSError, subprocess.TimeoutExpired) into _fail, same shape as the other five.

### C2-8 (LOW): R7 ssh:// remote form refuses (fail-closed false refusal)

- Files: tests/realistic/launch_y13.py:1033-1056 (`_normalize_remote_url`).
- Evidence (probe6_7_8_9 P7, 20 cases): `ssh://git@github.com/phamTuan207/computer-use-wayland.git` normalizes to `ssh://git@github.com/...` and refuses. A checkout with an ssh:// remote can never launch. Double trailing slash and `.GIT` uppercase also refuse (fail-closed). All other forms normalize correctly.
- Proposed fix: normalize the ssh:// URL form to https the same way as the scp-like SSH form (strip the ssh:// scheme and git@ userinfo); strip all trailing slashes, case-fold the .git suffix. Fail-closed direction, so this is a usability fix, not a hole.

### C2-9 (LOW): R10 docs still overclaim what the code does

- Files: improvements/worker-y13-codex-y5-live-plan.md (B1 lines 634-638, B2 line 656, B3 lines 673-684 + LIMIT paragraph, Amend 2 lines 700-704, round-2 section lines 734-748).
- Details:
  - B1/B4 + round-2 section claim "the launcher verifies the entry .pyc out-of-process and deletes it before exec (the scan + check_manifest exempt entry .pyc so they reach that check)". False in the round-2 code (see C2-1). Correct the bullets to match the code once C2-1 is fixed, or state the current behavior (check_manifest refuses any .pyc) until then.
  - B3 lists the -c sinks as exec(/eval(/os.system(/subprocess.*/runpy.run_path() + a quoted .py path md5 check, but the code misses the C2-2 sinks; the LIMIT paragraph documents only string-concatenation, not argv/env smuggling, -m trace, or `python3 -- -`. "python3 - (stdin) counts as a possible runner" is true, but `python3 -- -` does not.
  - B2 says "check_manifest refuses planted top-level .py, non-entry .pyc, and symlinks". check_manifest refuses ALL .pyc including entry ones, so the "non-entry" qualifier is wrong in the other direction.
  - Amend 2 says a bare codex token and a path merely containing a codex directory do NOT warn. True for those cases, but path MENTIONS (grep /usr/bin/codex, echo /codex) still warn (see C2-6).
- Proposed fix: correct each bullet to the code as fixed (state the check_manifest-before-_check_entry_pyc order per C2-1, the exact sink list, and the path-mention warning residual).

### C2-10 (LOW): wrapper unit gaps, 12 new wrappers + 6 flag gaps in listed wrappers

- Files: tests/realistic/run_codex_y5.py:4121-4270 (`_command_executes_runner`), tests/realistic/launch_y13.py:706-855 (same).
- Evidence (probe3_unit): unit misses for time, watch, xargs, ionice, chrt, numactl, systemd-run, unshare, su, runuser, prlimit, setarch (each `WRAPPER python3 run_codex_y5.py` returns False), and for sudo VAR=1 (`sudo FOO=bar python3 ...`), setsid -w / --wait, command -p, nohup --, env -S. time, numactl, firejail, bwrap are not installed on this VM, so those four are class gaps, not live forms here; uv is not installed either (LAUNCH-FAILED).
- Live impact is nil (probe3wrap2): nice/stdbuf/taskset/ionice/prlimit/setarch exec-replace (no parent persists); sudo/unshare/xargs parents persist BUT the child python is always separately visible in /proc and IS caught, because check_runner_quiet scans every /proc entry. Watch/chrt/runuser persistence was inconclusive (watch needs a terminal, chrt needs realtime setup, runuser cannot read the probe dir as nobody). So these are unit-table gaps only; the A4 re-test contract (unit table) is what they fail.
- Proposed fix: extend the wrapper strip list (a generic rule beats one name at a time: after the known wrappers, treat an unknown leading token followed by a python token as a wrapper), skip VAR= assignments after sudo, and skip flags for setsid/command/nohup (with their value flags). Or document the wrapper list as the supported set and record the rest as known unit gaps.

## Killed leads (tested, no hole)

- sitecustomize / usercustomize / encodings plants: not re-tested (round-1 kill stands, nothing in round 2 touches site loading); the R1 scan refuses any planted file before any import, which subsumes them.
- Planted os.py: same, subsumed by the R1 scan (any planted file refuses before import).
- -m profile: the guard fires ("run as a script"), so the tokenizer is right not to catch it. -m timeit exec: crashes with NameError (os undefined in the timeit exec namespace), no run. -m pudb: not installed. -m runpy / -m cProfile: correctly NOT caught (both set __spec__, guard fires).
- -I and PYTHONSAFEPATH env pass the safe_path gate legitimately (both set sys.flags.safe_path; -I is at least as safe as -P). -E refuses, bare refuses.
- Symlinked ship dir verifies rc 0 (the content is still scanned; the link itself is not a plant).
- Wrong-tag legit .pyc: refuses via check_manifest (fail-closed); after the C2-1 fix it should verify + delete, since the tag is only a filename and the marshal comparison ignores the header.
- ssh://, double-slash, .GIT remote forms refuse fail-closed (C2-8), not holes.
- The accidental full-suite invocation in probe3live (c-dunder-import-runpy without --verify-manifest) ran the suite, fixture fetches 404, rc 2, no Zen driving, no ports left listening, no log clobbered.

## Round-1 findings, re-checked

- C2-1 HIGH (.so executes): FIXED (P1a/P1a2, all refuse, no marker).
- C2-2 MEDIUM (_check_entry_pyc dead): NOT FIXED (C2-1 above, same defect, new root cause: the exemption condition is unsatisfiable).
- C2-3 MEDIUM (tokenizer residuals): OLD 20 FIXED, NEW generation found (C2-2 above).
- C2-4 MEDIUM (guard deletes through symlinked __pycache__): FIXED (P4a/P4f/P4g, nothing outside deleted).
- C2-5 LOW (codex warning): MOSTLY FIXED (bare token + path-dir fixed; path-mention residual is C2-6).
- C2-6 LOW (remote pin strict + no topo-order): FIXED (normalization 20/20, --topo-order present; ssh:// false refusal is C2-8).
- C2-7 LOW (guard gaps): FIXED for the file dimension (recursive + any-tag deletion proven); leftover empty nested dir is C2-5.
- C2-8 LOW (uncaught subprocess exceptions): FIXED for the listed calls; main exec is C2-7.
- C2-9 LOW (doc overclaims): PARTIALLY FIXED (SHIPPED.md + regen docstring + B2/B3 bullets improved); B1/B4 + round-2 wording still wrong (C2-9).
- C2-10 LOW (md5 leg edges): CAP ADDED (10 MB check in code); FIFO/unreadable fail open remains, documented in the docstring; renamed .sh not in the set, documented.
- C2-11 LOW (_proven_no_body None): FIXED (R9, 12/12).
- Redteam F1 (-m/import forged entry .pyc executes): DOCUMENTED RESIDUAL, re-confirmed (marker prints via -m with a properly re-headed forge; launcher refuses pre-exec).
- Redteam F2 (_check_entry_pyc unreachable): NOT FIXED (C2-1).
- Redteam F3 (11 tokenizer evasions): FIXED for the listed 11 (wrappers, -uW/-uX/-iuW, -c os.system/runpy literals, renamed-copy exec); NEW evasions are C2-2/C2-10.
- Redteam F4 (import run_live / py_compile brick): NOT FIXED on either path (P2e; same R2 root cause).
- Redteam F5 (tampered run_live.py executes on direct path): FIXED for the non-self-consistent case (P5a); self-consistent remains the documented limit, launcher git comparison holds (P5b/P5c).
- Redteam F6 (marker case 1 passes by design): UNCHANGED, documented coordination-signal limit, not re-tested (round 2 did not touch marker content checks).

## Probe index

All probes under ~/workspace/y13g-r2-council-2/probes/ (persistent, outside the repo); staged ships under ~/workspace/y13g-r2-council-2/ship (clean) and per-probe work dirs under probes/work/.
- r2common.py: fresh(), direct_verify(), launcher_scan_only(), build_so(), run().
- probe1_r1.py: P1 R1 allowlist (30 checks: .so bare/-P runner + launcher, 8 odd shapes x2 paths, missing SHIPPED.md/manifest, symlinked ship dir, safe_path forms, PYTHONPATH plant).
- probe2_r2.py: P2 R2 flow (27 checks: legit/forged entry .pyc x3 stems, weird tag, non-entry name, nested, .pyc-named dir, direct-path brick, py_compile/import run_live unbrick, mixed tags).
- probe2x_r2_defect.py: P2x isolation (exemption condition evaluation, direct _check_entry_pyc 4/4, real-binary scan exemption).
- probe2y_f1.py: F1 re-confirmation (re-headed forged entry .pyc via -m prints the marker).
- probe3_unit.py: P3 unit table (63 cases, AST-identity + _SHIP_FILES identity + manifest cross-check).
- probe3live.py + probe3live_fix.py: P3 live execution proofs (20 + 10 forms, --verify-manifest oracle, staged ships).
- probe3wrap.py + probe3wrap2.py: wrapper parent-persistence survey (ps snapshots, killpg cleanup, no sleepers left).
- probe4_r4.py: P4 guard edges (14 checks: 3 symlink shapes, nested, tag, cache-as-file, .pyc-named dir, nested forged).
- probe5_r5.py: P5 entry-hash check (9 checks: tampered run_live, self-consistent tamper + launcher git refusal, manifest shapes, tampered launcher/runner).
- probe6_7_8_9.py: P6 codex (14 cases), P7 remote (20 cases), P8 git-missing + fetch-fail + subprocess.run inventory, P9 _proven_no_body (12 cases). 48/48.

## Methodology notes (honest artifacts)

- This VM runs as root (uid 0) on an overlay FS. Permission-sensitive results are code-reading verdicts, not live proofs: an unreadable __pycache__ dir cannot be staged here (root lists mode-000 dirs); by code reading the scan refuses it anyway (_is_exempt_cache_dir returns False on listdir OSError, so the dir is refused as unexpected-dir).
- Full launcher main() was NOT run end to end: check_marker needs a network fetch and write_token would clobber the live handover token (/tmp/worker-y13-handover.json), which could refuse a live runner mid-run on its token fingerprint. The flow was proven instead via the real binary up to check_go (module-top scan) plus AST-extracted check_manifest + _check_entry_pyc + _scan_ship run in main() order plus source-order reading of main().
- Probe bugs found and fixed during the run (all in the log): my first extraction exec'd the launcher's own _fail (sys.exit) over my raising _fail (twice, P2 and P8b); I read the go-refusal from stderr while _fail prints to stdout; probe3live left a literal `R` uninterpolated in 7 -c snippets (NameError, not refutations); my first F1 forge was un-re-headed so the import system ignored it; the first probe3wrap run died on my own `pkill -f sleeper_dummy.py` matching my own shell cmdline.
- The verifier's files under improvements/y13g-verify/ were not read or used; every verdict above rests on my own probes. No fix file was modified by this review.
