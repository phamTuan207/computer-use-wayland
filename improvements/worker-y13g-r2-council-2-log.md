# Council Voice 2 (round 2) running log

- Reviewer: Council Voice 2 (adversarial/edge-case), round-2 diff review
- Scope: commits 0639d04, 87eec47, 6ba43f2, 8bdd5aa, 5a9b9e8 on todolist-push
- Start: 2026-11-22 01:00 +07 (T+0)
- Method: assume the round-2 fixes are wrong until proven right. Fresh probes under ~/workspace/y13g-r2-council-2/probes/, staged ships under ~/workspace/y13g-r2-council-2/ship. No live Zen, no ydotool, no system paths, no em/en dash.

## T+0 01:00 +07: setup
- Repo on todolist-push, HEAD 334cf69. Round-2 commits present (0639d04..5a9b9e8).
- Read round-1 Council 2 paper (BLOCK, C2-1 HIGH .so + C2-2..C2-11), redteam paper (AMEND, F1-F6), fix-log adjudication R1-R10.
- Read runner module top (lines 1-660), launcher module top (lines 120-450), tokenizer blocks both files, _check_entry_pyc, check_manifest, _scan_ship, _check_remote, check_marker, _proven_no_body, main() order.
- Pins verified live: runner d5047ff5, launcher 8e72a5ce, run_live 84fa106c, manifest 7c763834, 27 files. Regen --stage to ~/workspace/y13g-r2-council-2/ship: rc 0, manifest_ok true, 29 files on disk.
- Pre-probe flag checks: -I sets safe_path True (legit pass, -I implies safe_path), -E False, PYTHONSAFEPATH=1 env True, PYTHONPATH survives -P (sys.path[0] is /tmp/evil under -P).

## T+0h08 01:08 +07: P1 (R1 allowlist) DONE, 30/30
- C2-1 FIXED live: glob.so + shlex.so runner bare and -P refuse rc 2, no marker; hashlib.so launcher bare (safe_path gate) and -P (scan) refuse, no marker.
- All P1b shapes refuse both paths: planted .txt, unexpected dir, nested __pycache__, __pycache__ as file, .pyc-named dir (top + nested), case-variant .py, manifest file replaced by a dir.
- Bare + -E refuse at safe_path; -I and PYTHONSAFEPATH env pass (both set the flag, legitimate, not bypasses). Symlinked ship dir verifies rc 0 (content still scanned).
- FINDING (new, LOW): P1c missing SHIPPED.md: direct verify rc 0 manifest_ok true. The scan refuses unexpected files only, never missing ones; SHIPPED.md is not a manifest entry and _verify_manifest does not check it. A ship missing SHIPPED.md passes every gate. Missing manifest itself refuses rc 2 (unreadable).
- FINDING (new, LOW): P1f PYTHONPATH plant EXECUTES under -P: PYTHONPATH=/tmp/evil with glob.py marker, direct -P run rc 0, marker PRESENT. -P removes sys.path[0] only; PYTHONPATH dirs stay on sys.path and the runner's post-scan `import glob` loads the plant. Same class hits the launcher (post-scan hashlib import) and _check_entry_pyc's `python3 -P -c` compile subprocess (inherits env, imports marshal). Needs env control, outside the ship-tamper model, but the fix is cheap (scrub PYTHONPATH in the launcher exec env + compile subprocess env, or refuse at module top when PYTHONPATH is set). The docstring claim "-P keeps the ship dir off sys.path, so a planted stdlib .py cannot execute at import" is false when PYTHONPATH is set.

## T+0h15 01:15 +07: P2 (R2 entry .pyc) DONE: C2-2 NOT FIXED, MEDIUM
- Module-top scan exemption WORKS (real binary with a legit entry .pyc reaches check_go, no scan refusal, all 3 stems).
- _check_entry_pyc itself WORKS when called directly: legit verified+deleted for all 3 stems, forged refused on marshal mismatch (probe2x).
- BUT check_manifest's exemption is UNSATISFIABLE: launch_y13.py:1197 `if (not rel_root and _is_entry_pyc_rel(rel))`. An entry .pyc lives in __pycache__/, so rel_root is "__pycache__" (truthy) and the condition is False; the only way `not rel_root` is True is rel_root "", where rel cannot start with "__pycache__/". Proven by direct evaluation (COND rel_root='__pycache__' exempt=False) and by the flow: a legit entry .pyc is refused by check_manifest as "planted bytecode in ship" for all 3 stems, before _check_entry_pyc runs (P2a, P2e, P2f). Consequence: a legit entry .pyc still bricks the LAUNCHER flow (C2-2 verbatim); redteam F4's re-test (py_compile / import run_live unbricked without manual deletion) FAILS on the launcher flow too; the forged-.pyc refusals in P2b pass only via the blanket refusal, never via the marshal comparison, so the marshal check is still untested by any live path. Fix: drop `not rel_root and` at line 1197 (_is_entry_pyc_rel already requires the __pycache__/ prefix and no subdir).
- Side confirmations: wrong-tag legit .pyc refuses via check_manifest (same blanket refusal, fail-closed); non-entry-named .pyc refused by the scan; nested entry .pyc refused (unexpected-dir); .pyc-named dir refused by _check_entry_pyc as unreadable (fail-closed); direct runner path stays strict (legit entry .pyc refuses kind pyc, by design).
- Probe bug caught and fixed mid-run: my first extraction exec'd the launcher's own _fail (sys.exit) over my raising _fail, and I read the go-refusal from stderr while _fail prints to stdout. Both fixed; the P2a/P2b FAILs above are real, re-verified after the fix.

## T+0h30 01:30 +07: P4 (R4 guard) DONE, 13/14
- C2-4 FIXED live: symlinked __pycache__ (P4a), symlinked subdir inside __pycache__ (P4f), and symlinked entry .pyc file (P4g, link unlinked, target survives) all delete NOTHING outside the ship. Direct form refuses the symlink in each case.
- C2-7 FIXED in the file dimension: nested entry .pyc deleted by the -m guard (P4b), pypy38 tag deleted (P4c), __pycache__-as-file and .pyc-named dir refuse fail-closed (P4d/P4e), nested forged .pyc deleted unverified (P4h, harmless: nested .pyc never executes, deletion is cleanup).
- FINDING (new, LOW): P4b leftover empty nested dir still bricks the ship. The guard deletes the nested .pyc FILE but leaves the empty `__pycache__/sub` directory; the scan then refuses `__pycache__` + `__pycache__/sub` as unexpected-dir, so direct verify stays rc 2 after the -m recovery. The top-level empty __pycache__ is exempt, but an empty NESTED dir is not. Fix: have the guard remove empty dirs it emptied (bottom-up rmdir), or exempt empty nested dirs under __pycache__ in the scan.

## T+0h40 01:40 +07: P5 (R5 entry-hash check) DONE, 9/9
- R5 FIXED for the direct path (redteam F5 closed): tampered run_live.py (manifest untouched) refuses BEFORE import, rc 2, no marker (P5a); tampered launch_y13.py likewise (P5e). Missing / dir / corrupt / files-less manifest all refuse rc 2 (P5d).
- P5b self-consistent tamper (run_live.py + re-signed manifest) still EXECUTES on the direct path: marker prints, rc 0, manifest_ok true. This is the DOCUMENTED limit, and the control holds: P5c extracted check_manifest refuses it on the git comparison (ship manifest md5 != committed manifest md5). So the direct path is safe only when the launcher gates it; the direct form alone is not a trust root for a self-consistent tamper. Documented as designed.
- P5e note: a tampered runner itself prints its marker then refuses rc 2 (_verify_entry_hashes catches its own md5 mismatch); only the self-consistent variant would pass, same as P5b.

## T+1h05 02:05 +07: P3 (R3 tokenizer) unit + live DONE
- Shared block verified: 14 tokenizer functions + 3 constants AST-identical between the files (17 parts); _SHIP_FILES identical (29 paths = manifest 27 + manifest + SHIPPED.md). Two copies agree on all 63 unit cases.
- Round-2 fixes hold: -m pdb, -uc/-Bc bundles, timeout 60s/1m, glued ; separators, pypy3, nice/sudo/stdbuf/taskset/uv, exec -a, -c os.system/runpy.run_path literals, stdin `-`, -uW flag values, all correct non-matches (grep/md5sum/pytest/runpy/cProfile/import/print-mention) still pass.
- CONFIRMED REAL evasions, all proven live on staged ships (manifest_ok true, tokenizer False):
  (a) `python3 -- -` stdin after -- (variant of the fixed `-` row);
  (b) -c argv/env-smuggled paths: exec/open with __file__ from sys.argv[1] (with sys.argv repaired, and even unrepaired main() runs and rejects args), runpy.run_path(sys.argv[1]), os.system('python3 '+sys.argv[1]), exec with __file__ from os.environ['R'] (cmdline-only check cannot see env);
  (c) -c sink gaps: os.execv/execve/execl/spawnl/spawnv, os.popen, subprocess.getoutput/getstatusoutput, __import__('os').system, __import__('subprocess').run, __import__('runpy').run_path, pty.spawn (each live EXECUTES);
  (d) `-m trace --count` EXECUTES live (guard does not fire), tokenizer False.
- Refuted (tokenizer right not to catch): -m profile (guard fires, "run as a script"), -m timeit exec (crashes NameError, no run), -m pudb (not installed).
- Wrappers: 12 new wrapper unit misses (time, watch, xargs, ionice, chrt, numactl, systemd-run, unshare, su, runuser, prlimit, setarch) + 6 flag gaps in listed wrappers (sudo VAR=1, setsid -w/--wait, command -p, nohup --, env -S). Live persistence survey: nice/stdbuf/taskset/ionice/prlimit/setarch exec-replace (no parent persists); sudo/unshare/xargs parents persist BUT the child python is always separately visible in /proc and IS caught (check_runner_quiet scans every /proc entry). So wrapper misses are unit-table gaps only, LOW. The -c/-m/stdin evasions are the live-relevant ones (in-process, no child to catch), MEDIUM, mitigated by the ports backstop (a suite run binds 8771/4452).
- Probe notes: probe3live's first run had an uninterpolated `R` variable in 7 -c snippets (NameError, not refutations) and one accidental full-suite invocation (c-dunder-import-runpy, no --verify-manifest arg: the suite ran, fixture fetches 404, rc 2, no Zen driving, no ports left listening, no log clobbered). Both fixed/verified in probe3live_fix.py (10/10 EXECUTE). The first probe3wrap run died on my own `pkill -f sleeper_dummy.py` matching my own shell cmdline; rerun as probe3wrap2 with killpg.

## T+1h30 02:30 +07: P6-P9 (R6/R7/R8/R9) DONE, 48/48
- R6 mostly fixed: argv[0] basename codex, ./codex, /usr/bin/codex warn; mycodex, codex.exe, bare grep/echo codex, path-contains-codex-dir do not. Residual LOW: a token ending in /codex in a NON-execution position still warns (grep /usr/bin/codex, echo /codex, ls /usr/bin/codex all True).
- R7 fixed 20/20: exact, trailing slash, no .git, SSH form, host/scheme case all normalize to the pin; http, wrong owner/repo, path case, userinfo, local path, empty all refuse. Note LOW: ssh:// URL form refuses (fail-closed false refusal for an ssh://-remote checkout); double trailing slash and .GIT uppercase also refuse (fail-closed).
- R8 fixed for the listed calls: _check_remote with git missing from PATH fails via _fail exit 2 (no traceback); check_marker with a dead-proxy fetch fails via _fail exit 2. Residual LOW (code reading): main()'s flock exec subprocess.run at launch_y13.py:1503 is the one launcher subprocess.run call NOT wrapped (OSError traceback exit 1 if flock/python3 is missing). Full main() was NOT run end to end (write_token would clobber the live handover token); the flow was proven via the real binary to check_go + extracted checks in main() order.
- R9 fixed 12/12: eval_error None returns False, "" returns False, missing key with a good snapshot returns True, all other A8 rows match.
- P8b probe bug fixed mid-run: my extraction included "_fail" in the extracted set, so the real _fail (sys.exit) overwrote my raising one; after removing it, the fetch-fail path returns Refused cleanly.

## T+1h35 02:35 +07: P10 (R10 docs) + F1 re-check DONE
- SHIPPED.md accurate: pins (runner d5047ff5, launcher 8e72a5ce, run_live 84fa106c, manifest 7c763834, 27 files), launch form with -P, --ship-dir space-only + existing-dir, "How to verify" AST-extraction note, marker log-order + --topo-order + normalization wording.
- Plan B1 (lines 634-638) and the round-2 section claim "the launcher verifies the entry .pyc out-of-process and deletes it before exec (the scan + check_manifest exempt entry .pyc so they reach that check)". FALSE in the round-2 code: the check_manifest exemption never fires (same root cause as the P2 defect). Doc side of C2-1.
- Plan B3 sink coverage now incomplete: the bullet lists exec(/eval(/os.system(/subprocess.*/runpy.run_path() but the code misses os.execv/spawn/popen, subprocess.getoutput, __import__-obfuscated sinks, pty.spawn; the LIMIT paragraph documents only string-concatenation, not argv/env smuggling, -m trace, or `python3 -- -`. "python3 - counts as a possible runner" is true, but `python3 -- -` does not.
- Plan B2 "check_manifest refuses planted top-level .py, non-entry .pyc, and symlinks": check_manifest refuses ALL .pyc including entry ones, so the "non-entry" qualifier is wrong in the other direction (minor).
- Plan Amend 2 "a bare codex token elsewhere and a path merely containing a codex directory do NOT warn": true for those cases, but path MENTIONS (grep /usr/bin/codex, echo /codex) still warn. Partial overclaim, same residual as P6.
- F1 re-confirmed on round-2 bytes: a properly re-headed forged entry .pyc via -m prints its marker (rc 2, guard message after). My first F1 attempt used an un-re-headed forge (header mtime/size from the temp source), so the import system ignored it; re-heading from the real source stat reproduces the redteam forge exactly.
- Redteam F3 renamed-copy exec re-verified: exec(open('mycopy.py').read()) with __file__ preset on a runner copy is CAUGHT by the md5 leg in both files (True/True).

## T+1h40 02:40 +07: paper written, verdict AMEND
- Paper improvements/worker-y13g-r2-council-2.md: verdict AMEND. Findings C2-1 (MEDIUM, R2 not fixed) + C2-2 (MEDIUM, new tokenizer evasions live-proven) + C2-3..C2-10 (LOW). No HIGH: nothing executes attacker code on a supported flow; every failure is fail-closed refusal or an exotic-form evasion mitigated by the ports backstop.
- Commits: paper + this log, small + many, explicit pathspec + --only, verified via ls-remote (see paper for hashes).
