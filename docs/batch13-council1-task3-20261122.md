# Batch 13 council 1: task 3 Y13g round-3 adjudication review

- Reviewer: batch 13 council 1 (task 3).
- Date: 2026-11-22, work 14:28 to 15:05 +07.
- Repo: ~/workspace/computer-use-wayland. Report branch: main.
- Adjudication under review: docs/batch13-task3-y13g-round3-adjudication-20261122.md, commit e7d9a1c.
- Code under review: branch todolist-push, HEAD 3167c76 (read-only, no file on todolist-push modified).
- Round-2 reviews re-read in full from todolist-push: redteam commit 167a2e9, verifier commit 75dff55, council 1 commit 1e49436, council 2 commit 6d83401, council 3 commit 31c1126, fix log commit ab0b62c. All six are ancestors of todolist-push.
- Authorization: coordinator Muse via coord/clone1.md batch 13, commit e03e288 on origin/main.
- Scope: review only. No shared code changed. No live run. coord/clone1.md and coord/clone2.md not edited. The untracked 0-byte test-w.txt was left alone.
- Method: every code claim in the adjudication was re-read first-hand in the files on todolist-push at 3167c76 (file and line numbers cited below). Every review characterization was checked against the review files themselves. Live numbers cited are the reviewers' numbers, confirmed present in their papers; no live battery was re-run here.

## Overall verdict: AGREE. BLOCK stands, no live run.

I agree with the adjudication's overall verdict and with all 35 UPHELD decisions below. The two HIGH findings (F1, F2) are correctly upheld at HIGH, the two sub-claim rejections are correct in substance, and the severity calls against council 2's lower votes are correct. I found no error that overturns any decision. I found 8 minor errors or gaps, all listed in the Errors and gaps section: 6 are wrong line-number ranges (substance correct), 1 is a misattributed citation, 1 is a small imprecision in a live-proof sentence, plus 3 minor omissions in fix instructions and 1 completeness note. None of them changes a verdict, a severity, or a fix.

Caveat: origin/todolist-push has advanced past the adjudicated base since the adjudication was written; it is now at 8c6553a while this review and the adjudication both use 3167c76. The round-3 fix pass should confirm its base against the current tip before starting.

## Decision table (all 35)

| Finding | Adjudication | Council 1 verdict |
|---|---|---|
| Redteam F1, check_manifest exemption dead code | UPHELD HIGH | AGREE |
| Redteam F2, PYTHONPATH plants execute under -P | UPHELD HIGH | AGREE |
| Redteam F3, tokenizer residuals | UPHELD MEDIUM | AGREE |
| Redteam F4, topo-order does not order across merges | UPHELD MEDIUM | AGREE |
| Redteam F5, relative-path py_compile co_filename mismatch | UPHELD MEDIUM | AGREE |
| Redteam F6, -m guard leaves empty nested dir | UPHELD LOW | AGREE |
| Redteam F7, check_manifest gaps | UPHELD LOW | AGREE |
| Verifier defect 1, filename-sensitive marshal comparison | UPHELD MEDIUM (same as F5) | AGREE |
| Verifier defect 2, symlink-unsafe deletion in _check_entry_pyc | UPHELD MEDIUM | AGREE |
| Council 1 F1, runner docstring launch lines lack -P | UPHELD Medium-Low | AGREE |
| Council 1 F2, launcher -m guard runs after _derive_ship_dir | UPHELD Medium-Low | AGREE |
| Council 1 F3, SHIPPED.md note omits constants | UPHELD Low | AGREE |
| Council 1 F4, -c sink docs say subprocess.* but code covers 5 methods | UPHELD Low | AGREE |
| Council 1 F5, stale two entry .pyc comment | UPHELD Low | AGREE |
| Council 1 F6, repo-tree wording overgeneralizes | UPHELD Low | AGREE |
| Council 1 F7, main exec subprocess.run unwrapped | UPHELD Low | AGREE |
| Council 1 F8, filename-sensitive marshal comparison, docs silent | UPHELD Low as doc gap, MEDIUM as defect | AGREE |
| Council 2 C2-1, R2 not fixed, exemption unsatisfiable | UPHELD HIGH | AGREE |
| Council 2 C2-2, tokenizer new generation | UPHELD MEDIUM | AGREE |
| Council 2 C2-3, PYTHONPATH survives -P | UPHELD HIGH | AGREE |
| Council 2 C2-4, ship missing SHIPPED.md passes every gate | UPHELD Low | AGREE |
| Council 2 C2-5, leftover empty nested dir | UPHELD Low (same as F6) | AGREE |
| Council 2 C2-6, codex warning fires on path mentions | UPHELD Low | AGREE |
| Council 2 C2-7, main exec subprocess.run unwrapped | UPHELD Low (same as C1-F7) | AGREE |
| Council 2 C2-8, ssh:// remote form refuses | UPHELD Low | AGREE |
| Council 2 C2-9, docs overclaim | UPHELD Low | AGREE |
| Council 2 C2-10, wrapper unit gaps | UPHELD Low | AGREE |
| Council 3 C3-1, --ship-dir= and --repo= silently ignored | UPHELD Moderate | AGREE |
| Council 3 C3-2, SHIPPED.md How to verify fails literally | UPHELD Moderate (same as C1-F3) | AGREE |
| Council 3 C3-3, runner docstring -P not fixed | UPHELD Moderate-Low (same as C1-F1) | AGREE |
| Council 3 C3-4, scan fix hint misleads for directories | UPHELD Moderate-Low | AGREE |
| Council 3 C3-5, B1 wording contradictory, stale comment | UPHELD Low (same as C1-F5/F6) | AGREE |
| Council 3 C3-6, _scan_ship md5 message does not distinguish edited case | UPHELD Low | AGREE |
| Council 3 C3-7, hint-less refusal legs | UPHELD Low | AGREE |
| Council 3 C3-8, write_token runs before integrity checks | UPHELD Low | AGREE |

## Verification notes (first-hand)

### Pins (adjudication Method section). AGREE.

- Runner md5 d5047ff573820491263a2eb3805105f4, launcher 8e72a5ce85cbaf8382f998987e8890e5: both match the manifest entries and the blobs on todolist-push at 3167c76.
- run_live pin 84fa106c253d5e7f16daccf2ce3f14a5: this is the 1e3901c version by design, not a stale pin. The regen script tests/realistic/regen_codex_y5_manifest.py states it owns the 1e3901c run_live.py pin and stages run_live.py from `git show 1e3901c`, everything else from the working tree. I confirmed run_live.py at 1e3901c hashes to 84fa106c253d5e7f16daccf2ce3f14a5, while the working-tree run_live.py (changed at 91d3cd2, an ancestor of the regen commit 5a9b9e8) hashes to d8e2b14d7456b2866790f4a87ec1919e. The staged ship therefore matches the manifest, and _ship_manifest_entries (launch_y13.py:1226-1238) reads the staged ship manifest, so _scan_ship compares staged files against staged bytes. The adjudication's "(pin 1e3901c holds)" is correct.
- Manifest md5 7c76383402e4c50b28adab6b25a22e09, 27 entries, SHIPPED.md absent: confirmed by hashing the manifest on todolist-push and checking all 27 entries against their blobs; 26 of 27 match the working tree and the one exception is the deliberate run_live pin above.
- Round-2 fix diff commits 0639d04, 87eec47, 6ba43f2, 8bdd5aa, 5a9b9e8 and review commits 167a2e9, 75dff55, 1e49436, 6d83401, 31c1126 and fix-log commit ab0b62c: all present and all ancestors of todolist-push.

### F1 (HIGH). AGREE.

- launch_y13.py:1197 reads `if (not rel_root and _is_entry_pyc_rel(rel)):` (confirmed).
- _is_entry_pyc_rel, launch_y13.py:295-300, returns False unless rel starts with `__pycache__/` and the name after the prefix holds no `/` (confirmed). The conjunction is unsatisfiable for the exact reason the adjudication gives.
- The module-top scan exemption at launch_y13.py:354-355 exempts on `_is_entry_pyc_rel(_rel)` alone (confirmed), so the two layers disagree as stated.
- Main order: check_manifest runs before _check_entry_pyc (confirmed), but the cited range is wrong, see E1a.
- Redteam A2L 7/7, log logs/a2launcher-run3.log, and A2x 8/8: confirmed present in the redteam paper (lines 66-99, 334-335). The adjudication's summary of the A2L cases is faithful except for the filename in the quoted refusal, see E2.
- Council 2 C2-1 independently root-caused the same condition at the same line (council 2 paper, C2-1 section), and council 1's R2 line is the claim the adjudication rejects (council 1 paper, line 62).
- Severity HIGH over council 2 MEDIUM: AGREE. The defect bricks the legitimate launcher flow for any entry .pyc (a routine -m/import/py_compile artifact) until manual deletion, and the marshal adjudication the round was built around never runs on any live path. Fail-closed does not lower it, because the failure mode is a bricked legitimate flow, not a refused attack.

### F2 (HIGH). AGREE.

- Grep over both entry points: zero matches for PYTHONPATH, PYTHONHOME, PYTHONSTARTUP in tests/realistic/run_codex_y5.py and tests/realistic/launch_y13.py (confirmed).
- Launcher exec env, launch_y13.py:1485-1499: `env = dict(os.environ)` plus PYTHONSAFEPATH=1 and other keys, PYTHONPATH passed through untouched (confirmed). The comment at :1495-1498 claims PYTHONSAFEPATH=1 keeps "a planted stdlib .py" from executing at import time in the runner; that claim is false for the PYTHONPATH channel, because -P removes sys.path[0] only (confirmed by reading the comment and the env construction).
- The _check_entry_pyc fresh-compile subprocess at launch_y13.py:1289-1292 passes no env argument, so it inherits the caller environment (confirmed).
- The launcher imports shlex at module top, line 381, after the module-top scan, so a PYTHONPATH shlex plant executes in the launcher process before check_go runs (confirmed structurally; the live proof is the redteam's).
- Redteam A6, log logs/a6-run3.log, 117 cases, 101 pass, 16 FAIL, all 16 this channel, and the 13 .py names (enum, re, json, socket, subprocess, hashlib, datetime, pathlib, copyreg, functools, collections, warnings, shlex): confirmed verbatim in the redteam paper (lines 114-115, 340-341). Council 2 probe1 P1f (PYTHONPATH plant executes under -P, rc 0, marker present) is confirmed in the council 2 paper (C2-3 section).
- Severity HIGH over council 2 LOW: AGREE. The observed effect is planted code executing in both entry points with rc 0 and manifest_ok true while the code claims -P prevents it. The threat needs env control, but the launcher inherits the operator environment and passes it through, so a poisoned operator environment is the channel, and the fix (scrub plus refusal) is cheap. A false safety claim in the code is itself a HIGH defect.

### F3 (MEDIUM). AGREE.

- _SINKS, launch_y13.py:569-572 and run_codex_y5.py:3984, same tuple in both copies, missing subprocess.getoutput, subprocess.getstatusoutput, os.popen, os.exec*/spawn*, pty.spawn, __import__ forms (confirmed).
- _m_module_is_runner, launch_y13.py:586-600: only pdb is special-cased; trace is not handled (confirmed; the only "trace" match in the launcher is the word "traceback" in a comment at line 976).
- `python3 -- -`: _python_executes_runner, launch_y13.py:620-693, breaks on `--` at :636-638 with i incremented past it, then falls through to `_token_is_runner_script(args[i], cwd)` at :691-692; `_token_is_runner_script("-")` (launch_y13.py:534-543) returns False as the adjudication derives (confirmed by reading). The bare `python3 -` case returns True inside the loop (confirmed).
- Wrapper strip list in _command_executes_runner, launch_y13.py:706-855: env, nohup, setsid, exec, command, timeout, flock, bash/sh/zsh/dash -c, nice, stdbuf, taskset, sudo, uv (confirmed); time, watch, xargs, ionice, chrt, numactl, systemd-run, unshare, su, runuser, prlimit, setarch are absent (confirmed by reading the function). See E5 for two further class gaps the adjudication omits.
- _is_timeout_dur, launch_y13.py:697-703: `t.replace(".", "", 1).isdigit()` rejects hex, so `timeout 0x10` is not recognised as a duration (confirmed).
- _shlex_tokens, launch_y13.py:453-471, splits tokens on `;`, `&`, `|` and drops the separators; _command_executes_runner examines only the first command, so a runner as the second command in a bash -c string is missed (confirmed by reading both functions; the redteam paper states the same mechanism).
- Live numbers: redteam A4 live dummy probe 59/59, live-forms 28/31 + 5/6, unit SPEC 80/80, EXTRA 48/49, FRESH 2/29 (confirmed in the redteam paper, lines 165-170, 337-339). Verifier A4 unit 81/81 and live 17/17 cover the specified table only (confirmed in the verifier report, lines 141-153); the listed new forms are not in that table. Council 2 C2-2(a)-(d) live-proved the same classes (confirmed in the council 2 paper). No contradiction between the reviewers.
- The MEDIUM rating with the ports plus per-process-scan mitigation: AGREE. The single-cmdline verdict is wrong and the child python is separately visible in /proc (council 2 probe3wrap2, confirmed in the council 2 paper, C2-10 section), so both redteam F3 and council 2 C2-10 stand as the adjudication resolves in item 4.

### F4 (MEDIUM). AGREE.

- check_marker git log call, launch_y13.py:1119-1122: `git log origin/todolist-push --topo-order --format=%H%x09%s`, no `--first-parent` (confirmed).
- Redteam A5, log logs/a5-run1.log, 32/32: case 10 (main-line abort 2026-11-21 vs side-branch completion forged 2026-11-22, merged, PASSES) and case 11 (main-line completion 2026-11-21 vs side-branch abort forged 2020-01-01, merged, REFUSES with "Y6c abort ... is newer than the newest completion"), linear case 3 holds (confirmed verbatim in the redteam paper).
- Verifier A5 10/10 covered linear history only: confirmed in the verifier report (A5 section: cases 3a/3b refuse by log order on forged dates; no merge case). Council 2 R7 FIXED covers normalization 20/20 and --topo-order presence, not merges (confirmed in the council 2 paper). See E4 for the mislabeled citation in the adjudication's F4 paragraph.
- The --first-parent fix is the correct shape.

### F5 (MEDIUM, also verifier defect 1 and C1-F8). AGREE.

- _check_entry_pyc, launch_y13.py:1242-1313: the fresh compile runs `compile(src, sys.argv[1], 'exec')` with src the absolute SHIP_DIR path (launch_y13.py:1279-1290), and the comparison at :1302 is `marshal.dumps(cached_code) != marshal.dumps(fresh_code)` (confirmed). co_filename is part of the marshalled code object, so a relative-path py_compile .pyc mismatches (confirmed by reading).
- Verifier defect 1 (A3h, 2 checks FAIL, results/a3.log): confirmed in the verifier report (lines 28-41, 162, 173). Council 1 F8 probe P3b (relative-path run_live.py compile refuses as forged) and P3a/P3c/P8 passing controls: confirmed in the council 1 paper (F8 section). All three reviewers independently root-caused co_filename only.
- The co_filename normalization fix (code.replace on both sides, or compile the fresh reference with the cached co_filename) matches the verifier's proposed fix shape.

### Verifier defect 2 (MEDIUM). AGREE.

- _check_entry_pyc, launch_y13.py:1263-1266, `cached_names` comes from plain os.listdir(cache_dir), and verified files are deleted with plain os.unlink(cached_path) at :1307 (confirmed). There is no realpath check anywhere in the function (confirmed by reading the whole function, :1242-1313). See E1c for the wrong range on the unlink.
- Contrast with _entry_pyc_paths, launch_y13.py:190-213 (and the runner copy at run_codex_y5.py:138-170), which returns [] when realpath(cache) is not inside realpath(_SHIP_DIR) (confirmed).
- Verifier A7 shape-6b, results/a7.log, proven twice (manual probe plus harness re-run), legitimate .pyc behind a symlinked __pycache__ deleted outside the ship, forged outside .pyc refuses intact: confirmed verbatim in the verifier report (defect 2 text, lines 42-60, and A7 section).
- Reachability limit is honestly recorded by both the verifier and the adjudication (the launcher module-top scan refuses a symlinked __pycache__ before main() runs _check_entry_pyc). The function that deletes files during launch checks must still carry the same safety property as the guard helper.

### F6 (LOW). AGREE.

- _entry_pyc_paths (runner run_codex_y5.py:138-170, launcher launch_y13.py:190-213) returns file paths only and both guards unlink files only, never pruning directories (confirmed).
- _is_exempt_cache_dir (runner :290-312) returns False unless rel is exactly "__pycache__", so an empty nested __pycache__/sub still refuses as unexpected-dir (confirmed).
- Corroboration: redteam F6, council 2 C2-5 probe P4b (nested .pyc deleted, empty sub dir remains, direct verify stays rc 2 kind unexpected-dir), verifier A2l (same residue, rc 0 restored after deleting the empty dir): all three confirmed present in their papers.
- Downgrade from redteam LOW-MEDIUM to LOW: AGREE. A -m/import probe only ever writes top-level .pycs, so a nested dir can only appear by hand; the failure is fail-closed and recovery is one rmdir.
- The adjudication picks council 2's first fix option (bottom-up rmdir) and explicitly rejects the second (exempt empty nested dirs in the scan). That is a legitimate adjudication choice, stated openly.

### F7 (LOW). AGREE.

- check_manifest walk, launch_y13.py:1182-1204, flags only symlinked dirs, symlinked files, .pyc files, and top-level .py files not in the manifest (confirmed by reading). It does not flag a FILE named __pycache__, a DIRECTORY named like a .pyc, or a nested .py such as http/__init__.py (confirmed by reading the walk conditions).
- Redteam F7 live proof (all three pass check_manifest and refuse at _scan_ship, A6 http launcher, A7 cachefile/pycdir): confirmed in the redteam paper. Severity LOW with the _scan_ship backstop: AGREE.

### C1-F1 and C3-3 (Medium-Low / Moderate-Low). AGREE.

- run_codex_y5.py:103 reads `cd /tmp/worker-y13-server && Y13_GO=1 python3 launch_y13.py all` and :105 reads `Y13_GO=1 python3 launch_y13.py 01 02`, with no -P; only :106 has -P (confirmed). The round-2 diff never touches :103/:105 (the diff commits touch the plan, manifest, SHIPPED.md and regen for docs; council 1 and council 3 both verified this by diff).
- Launcher docstring lines 109-110 carry -P with --repo, and SHIPPED.md carries -P (confirmed by reading launch_y13.py:108-110 and SHIPPED.md).
- Council 1 probe P7 and council 3 probe P7d ran the docstring form verbatim, rc 2, "run with python3 -P" (confirmed in both papers).
- The adjudication's fix combines council 1 (add -P, regen manifest, re-verifier runs the lines as written) with council 3 (add --repo matching the launcher docstring and SHIPPED.md). Correct combination. The adjudication does not write the literal laptop checkout path; that is correct under the no-personal-information rule, since the path is already documented in the launcher docstring and SHIPPED.md.

### C1-F2 (Medium-Low). AGREE.

- launch_y13.py:185 `SHIP_DIR = _derive_ship_dir()` runs before the __spec__ guard at :227-236, and the guard cleanup walks _entry_pyc_paths(), which uses the derived _SHIP_DIR (:190-213) (confirmed). The repo-tree refusal sits inside _derive_ship_dir, print starting at :170 (confirmed).
- Council 1 probes P4a (repo-tree -m exits 2 with the repo-tree message, .pyc stays), P4b control (staged ship, guard message plus .pyc deleted), P4c (-m launch_y13 --ship-dir elsewhere prints the script-form message but the .pyc stays in the file's own dir): confirmed in the council 1 paper (F2 section). The B4 re-test assertion is contradicted for both invocations as the adjudication states.
- The runner has no such ordering issue (its _SHIP_DIR is the file dir). The proposed fix (guard before _derive_ship_dir against a provisional file-dir ship) matches council 1's fix.

### C1-F3 and C3-2 (Low / Moderate). AGREE.

- SHIPPED.md:43-49 says to exec the named FunctionDef nodes with os/json/hashlib/re/shlex/subprocess/time/marshal and _SHIP_DIR set, without naming the 14 functions and without the 4 module-level constants (confirmed by reading SHIPPED.md).
- The 4 constants are _RUNNER_MODULE_NAMES, _RUNNER_MANIFEST_PATHS, _RUNNER_MD5S at run_codex_y5.py:3860-3865 and _PY_NO_VALUE at :4032 (confirmed by grep).
- Council 1 probe P2c and council 3 probe P6 followed the note literally and hit NameError: name '_RUNNER_MODULE_NAMES' is not defined on the first call (confirmed in both papers). Council 3 also proved the note omits that cmdlines are NUL-joined argv lists; with the 4 constants added and NUL-joined argv, all 6 cases pass in both copies (confirmed in the council 3 paper, C3-2 section).
- See E6 for one element of council 1 F3 that the adjudication's fix does not carry over.

### C1-F4 (Low). AGREE.

- _SINKS lists subprocess.call, subprocess.run, subprocess.Popen, subprocess.check_output, subprocess.check_call; subprocess.getoutput and subprocess.getstatusoutput are absent (confirmed).
- Council 1 probe P6: `python3 -c "import subprocess; subprocess.getoutput('python3 run_codex_y5.py')"` returns False via the extracted tokenizer, while the subprocess.run form returns True (confirmed in the council 1 paper, F4 section).
- The code fix is required because this is subsumed by the F3 sink extension, as the adjudication states.

### C1-F5 and C3-5 comment half (Low). AGREE.

- run_codex_y5.py:750 reads "the two entry .pyc files (0, 1, or 2)" (confirmed). Grep over the reviewed files (runner, launcher, SHIPPED.md, plan) confirms this is the only remaining "two entry" mention.
- _ENTRY_PYC_NAMES at run_codex_y5.py:133 is built from sys.implementation.cache_tag (current tag only), and the _verify_manifest dir exemption at :775 uses it, while the module-top scan, _is_entry_pyc_rel, and _check_entry_pyc are any-tag (confirmed). The scope difference is outcome-identical as the adjudication states (the runner scan refuses any .pyc before _verify_manifest can see one).
- The fix (comment to "three entry .pyc files (0, 1, 2, or 3)") matches council 1's fix.

### C1-F6 and C3-5 plan half (Low). AGREE.

- Plan lines 714-716 say a repo-tree path refuses with "this looks like the repo tree, not a staged ship; cd to the ship dir or pass --ship-dir", and SHIPPED.md:20-24 says the same (confirmed by reading both).
- Only the file-dir derivation branch refuses with that message (launch_y13.py _derive_ship_dir, :169-173); an explicit --ship-dir pointing at a repo tree is accepted as SHIP_DIR and refused later by the module-top scan as tampered (council 1 live probe, confirmed in the council 1 paper, F6 section). Both paths refuse exit 2; the message differs.
- Plan B1 at :633-638 still says _verify_manifest exempts a __pycache__ dir "ONLY when it holds only entry .pyc files (0-3)" while the code comment at run_codex_y5.py:294-299 says observably this exempts an EMPTY __pycache__ dir only (confirmed by reading both).
- The fix (scope the repo-tree sentences to the file-dir branch; reword B1 to "exempts an EMPTY __pycache__ dir only; any .pyc inside still refuses (scan first, then verify)") matches council 1 and council 3.

### C1-F7 and C2-7 (Low). AGREE.

- launch_y13.py:1503 `proc = subprocess.run(cmd, cwd=SHIP_DIR, env=env)` in main() has no try/except (confirmed).
- The other five launcher subprocess.run calls are wrapped in try/except (OSError, TimeoutExpired) into _fail exit 2: remote :1068, fetch :1110, log :1119, show :1206, fresh compile :1289 (confirmed each by reading; council 1 F7 and council 2 C2-7 both inventory the same six call sites with the same line numbers).
- Council 2 notes the OSError path is a code-reading verdict, not live-proven, because full main() was not run end to end; the adjudication accepts it as a code-reading finding and repeats the caveat accurately.

### C2-4 (Low). AGREE.

- The manifest has 27 entries and SHIPPED.md is not one (confirmed by reading the manifest on todolist-push). The staged ship is 29 files: manifest 27 plus the manifest itself plus SHIPPED.md (confirmed by the _scan_ship allowlist at launch_y13.py:1330-1333 and by council 1 P1b and council 2 R1).
- Council 2 probe P1c: ship with codex-y5/SHIPPED.md deleted, direct verify rc 0, manifest_ok true (confirmed in the council 2 paper, C2-4 section). The scan iterates files present, so a missing file is invisible to it.
- The fix (refuse when any allowlist file is absent, or add SHIPPED.md to the manifest-checked set) matches council 2's fix.

### C2-6 (Low). AGREE.

- _is_codex_process, launch_y13.py:872-888, checks `for tok in parts[1:]: if tok.lower().endswith("/codex"): return True`, so any token in any position ending in /codex counts (confirmed). The docstring claims "/codex (an execution position)", but the code does not check position (confirmed).
- Council 2 probe P6: `grep /usr/bin/codex file`, `echo /codex`, and `ls /usr/bin/codex` all return True (warn) (confirmed in the council 2 paper, C2-6 section). Council 1 R6 describes the code accurately but does not flag the position issue; council 2 does. The adjudication correctly follows council 2.

### C2-8 (Low). AGREE.

- _normalize_remote_url, launch_y13.py:1033-1056: strips only one trailing slash (`u = u[:-1]`), strips `.git` case-sensitively (`u.endswith(".git")`), and the ssh:// form falls into the :// branch which keeps the ssh:// scheme, so it mismatches the pinned https URL (confirmed by reading).
- Council 2 probe P7 (20 cases) proved the ssh:// refusal plus double-slash and uppercase .GIT refusals (confirmed in the council 2 paper, C2-8 section). Council 1 R7 considered these fail-closed non-findings; council 2 rates the ssh:// form a LOW usability finding. The adjudication correctly upholds C2-8 as LOW (fail-closed direction, usability fix, not a hole).
- The fix (normalize ssh:// to https like the scp-like form; strip all trailing slashes; case-fold the .git suffix) matches council 2's fix.

### C2-9 (Low). AGREE.

- Plan B1/B4 plus the round-2 section claim "the launcher verifies the entry .pyc out-of-process and deletes it before exec (the scan + check_manifest exempt entry .pyc so they reach that check)": false in the round-2 code, see F1 (confirmed; the same wording is quoted in council 2 C2-9 and council 3 C3-11(a)).
- B3 lists the -c sinks as exec(/eval(/os.system(/subprocess.*/runpy.run_path() plus a quoted .py path md5 check, and the LIMIT paragraph documents only string-concatenation, not argv/env smuggling, -m trace, or `python3 -- -` (confirmed by reading plan lines 673-684).
- B2 says "check_manifest refuses planted top-level .py, non-entry .pyc, and symlinks" (plan line 656, confirmed); check_manifest refuses ALL .pyc including entry ones, so the "non-entry" qualifier is wrong in the other direction, as the adjudication states.
- Amend 2 says a bare codex token and a path merely containing a codex directory do NOT warn (plan lines 700-704, confirmed); true for those cases, but path mentions still warn, see C2-6.

### C2-10 (Low). AGREE.

- The wrapper strip list covers env, nohup, setsid, exec, command, timeout, flock, bash/sh -c, nice, stdbuf, taskset, sudo, uv (confirmed). Council 2 probe3_unit unit misses for the 12 wrappers plus sudo VAR=1, setsid -w / --wait, command -p, nohup --, env -S (confirmed in the council 2 paper, C2-10 section). See E5 for two further names.
- Council 2 probe3wrap2 found live impact nil (nice/stdbuf/taskset/ionice/prlimit/setarch exec-replace with no parent persisting; sudo/unshare/xargs parents persist but the child python is always separately visible in /proc and IS caught) (confirmed in the council 2 paper). The LOW rating reflects the per-process scan backstop, not a claim that the verdicts are correct, as the adjudication states.
- This item is correctly folded into the F3 fix.

### C3-1 (Moderate). AGREE.

- _derive_ship_dir, launch_y13.py:144-157, matches "--ship-dir" by exact string only, so `--ship-dir=/tmp/x` never registers (confirmed). Main() stripping at :1458-1471 likewise handles only the exact "--ship-dir" and "--repo" tokens (confirmed; "--repo" in args at :1458, "--ship-dir" in args at :1464).
- Council 3 probes P2d, P2e, P3b, P3d, P3e, P3e2: from the ship dir the = form is ignored and the launcher uses the file-dir ship; from the repo tree it falls through to the repo-tree refusal telling the operator to "pass --ship-dir" when they already did; `--repo=/path` behaves the same (confirmed in the council 3 paper, C3-1 section).
- The consequence (a tamper probe in = form can silently test the wrong ship and report a false PASS) is correctly stated as the sharpest operator defect. The fix (refuse any argv token starting with "--ship-dir=" or "--repo=" in _derive_ship_dir before the repo-tree check, plus main() as a backstop) matches council 3's fix.

### C3-4 (Moderate-Low). AGREE.

- Runner scan JSON fix field says "delete the named files, or re-stage the ship with the regen script" (confirmed; the fix field print is at run_codex_y5.py:361-363, see E1d) and the launcher message at launch_y13.py:367-371 says the same (confirmed).
- Council 3 probes P5a, P5a2, P5a3: a nested codex-y5/__pycache__/check-dashes.cpython-312.pyc refuses listing both the dir and the file, deleting only the .pyc leaves the empty nested dir, verify still refuses rc 2 kind "unexpected-dir", only rmdir recovers (confirmed in the council 3 paper, C3-4 section).
- The fix (word the hint "delete the named files and directories, or re-stage the ship with the regen script", or do not list a directory whose only content is already listed) matches council 3's fix.

### C3-6 (Low). AGREE.

- _scan_ship refuses an edited ship file with "ship file md5 mismatch: ... (stale or edited ship; re-stage)" (confirmed; the message is at launch_y13.py:1373-1374, see E1e).
- Council 3 probe P5e: re-stage alone does not settle the edited case because regen --stage rebuilds the manifest from the working tree, so _scan_ship then passes but check_manifest refuses next (its message does give the full instruction, probe P5d) (confirmed in the council 3 paper, C3-6 section).
- The fix (mirror the check_manifest wording) matches council 3's fix.

### C3-7 (Low). AGREE.

- check_manifest, launch_y13.py:1188-1210, refuses "planted symlink dir in ship", "planted symlink in ship", and "planted top-level .py in ship" with no fix hint, while its .pyc leg right next to them says "Fix: delete the file, or re-stage the ship" (confirmed by reading). _scan_ship legs likewise name the path only (confirmed; the legs are at about :1347-1375, see E1f).
- Reachability is limited as stated: the module-top scan fires first on every one of these through the launcher, so these legs are TOCTOU-only in practice (confirmed by the main() order and the scan position at module top).

### C3-8 (Low). AGREE.

- Main order is check_go, check_marker, write_token, check_manifest, _check_entry_pyc, _scan_ship, check_token (confirmed; the calls are at launch_y13.py:1472-1478, see E1b). A launch that then refuses as tampered still leaves a fresh token on disk asserting a go order plus marker for a run that never happened (confirmed by reading the order). The exposure is limited as stated (direct runner invocation reusing the leftover token with LIVE_OWNER_AWAY=1, a form SHIPPED.md forbids for live runs).
- The fix (move write_token() to just after _scan_ship, immediately before check_token()) matches council 3's fix.

## Disagreement resolutions

1. Council 1 R2, check_manifest half: REJECTED. AGREE. The module-top scan exemption at launch_y13.py:354-355 works; the check_manifest exemption at :1197 is unsatisfiable (see F1). The scan half is accepted, as the adjudication states. The quote is verbatim from the council 1 paper (line 62).
2. Council 2 C2-4, "R4 FIXED", as applied to _check_entry_pyc: REJECTED in substance. AGREE with the substance, DISAGREE with the attribution, see E3. The guard helper _entry_pyc_paths is symlink-safe (realpath check, launch_y13.py:190-213); _check_entry_pyc has no such check (see defect 2). The verifier report's own defect 2 text states the same distinction verbatim.
3. Severity votes (council 2 C2-1 MEDIUM and C2-3 LOW vs redteam F1/F2 HIGH): redteam ratings stand. AGREE, for the reasons under F1 and F2 above. The underlying facts are not in dispute; all three reviewers agree on the code facts (redteam F1/F2, council 2 C2-1/C2-3, and the verifier's A2/A3/A7 sections all describe the same code behavior).
4. Redteam F3 vs council 2 C2-10 on wrapper live impact: both stand. AGREE. The single-cmdline verdict is wrong for the listed wrappers (redteam live proof, confirmed in the redteam paper); the child python is separately visible in /proc and caught by the per-process scan (council 2 probe3wrap2, confirmed in the council 2 paper). The MEDIUM rating for F3 already reflects that mitigation.
5. Verifier 277/280 vs redteam BLOCK: consistent. AGREE. The verifier's 3 failures are A3h 2 checks plus A7 shape-6b 1 check (confirmed: A3 17/19, A7 13/14, 280 total, 277 pass in the verifier report), both root causes in _check_entry_pyc (F5 and defect 2). The verifier did not test the check_manifest path (A2h tested _check_entry_pyc in isolation via the driver, A2i tested the module-top scan exemption; confirmed in the verifier report A2 section), the PYTHONPATH channel (A6d 66/66 tested ship-dir plants only, 15 .py names and 16 .so stems; confirmed), the new tokenizer evasions (A4 unit 81/81 and live 17/17 cover the specified table only; confirmed), or merge ordering (A5 10/10 covered linear history only; confirmed). Its FAIL verdict and the redteam BLOCK verdict agree that no live run may proceed.
6. Fix-log Design C vs the implemented code. AGREE. The fix log at commit ab0b62c says the entry-.pyc exemption was REMOVED from the scan and from _verify_manifest (fix-log lines 44-51, Design C). The implemented code instead adds a broken exemption attempt in check_manifest at launch_y13.py:1197, while keeping a working flag-gated exemption in the module-top scan at :354-355. The adjudication's resolution is sound: follow the adjudication's fix (exempt on _is_entry_pyc_rel(rel) alone at :1197), not the log's removal wording, because removal from check_manifest would keep refusing legit entry .pyc at check_manifest before _check_entry_pyc runs. The plan B1/B4 wording must be corrected to the fixed behavior (see C2-9).

## "What round 2 fixed" (accepted items). AGREE.

All accepted items check out against the five reviews: ship-dir .so and .py plants all refuse; symlinks all refuse (except verifier defect 2); R5 entry .py hash check (tampered run_live.py refuses before import on the direct path); R9 _proven_no_body 14/14 per redteam A8 (confirmed in the redteam paper, line 343), verifier 12/12 (confirmed, verifier report line 218), council 2 12/12 (confirmed, council 2 paper R9 bullet); marker ordering on a linear history; remote-URL normalization (except C2-8 ssh://); _SHIP_FILES identical between the two entry points (29 files, confirmed); AST identity True for the 14 tokenizer defs (confirmed in council 1 R3 and council 2 R1/R3 mechanics; council 3 H9 notes _is_runner_cmdline differs in docstring only, which is consistent because council 1 compared with docstrings stripped); handover token round-trip (council 3 H7, confirmed). See the completeness note N1 on council 1's R9 row count.

## Errors and gaps in the adjudication

None of these overturns any verdict, severity, or fix. They are corrections and small omissions the round-3 pass should carry.

- E1a. F1 cites main() order at launch_y13.py:1468-1472. The check calls are at :1472-1477 (check_go :1472, check_marker :1473, write_token :1474, check_manifest :1475, _check_entry_pyc :1476, _scan_ship :1477). Lines 1468-1471 are the --ship-dir/--repo stripping code, not the check calls. The wrong range is inherited from council 2 C2-1, which cites the same range. Substance (check_manifest before _check_entry_pyc) is correct.
- E1b. C3-8 cites main() order at launch_y13.py:1474-1479 for check_go through check_token. The calls are at :1472-1478 (check_go :1472 through check_token :1478; :1479 is check_runner_quiet). The range starts at write_token, not check_go. Inherited from council 3 C3-8. Substance (order) is correct.
- E1c. Verifier defect 2 cites launch_y13.py:1263-1271 for both the listdir and the unlink. The listdir is at :1263-1266, but the unlink is at :1307. The cited range covers only the listdir part. Substance (no realpath check in the function) is correct.
- E1d. C3-4 cites the runner scan JSON fix field at run_codex_y5.py:347-353. The fix-field print is at :361-363; lines 347-353 are the file-classification block (`elif _rel not in _SHIP_FILES:`). Inherited from council 3 C3-4. Substance (the hint text and the misleading behavior) is correct.
- E1e. C3-6 cites the _scan_ship md5 message at launch_y13.py:1340-1345. The message is at :1373-1374; lines 1340-1345 are the walk setup (allowed set and prefixes). Inherited from council 3 C3-6. Substance (the message text and the edited-case gap) is correct.
- E1f. C3-7 cites the _scan_ship refusal legs at launch_y13.py:1336-1345. The legs are at about :1347-1375; lines 1336-1345 are the setup. Inherited from council 3 C3-7. Substance (the legs name the path only) is correct.
- E2. F1 live-proof sentence attributes the refusal message `[launch_y13] REFUSED: planted bytecode in ship: __pycache__/run_codex_y5.cpython-312.pyc` to all four A2L cases including the run_live .pyc cases. The run_live case refuses naming run_live.cpython-312.pyc, not run_codex_y5. The redteam paper gives the run_codex_y5 filename explicitly only for the absolute-path case and says "same refusal" for the others. Minor imprecision; the rc 2 outcome and the .pyc-left-on-disk fact are correct for all four.
- E3. Resolution 2 mislabels its target as "Council 2 C2-4, 'R4 FIXED'". Council 2's C2-4 is the SHIPPED.md finding; the "R4 FIXED" claim is council 2's unnumbered verified bullet (council 2 paper, line 13), and it is explicitly scoped to the -m guard ("on -m (P4a/P4f/P4g)") and never claims _check_entry_pyc safety. The R4-vs-_check_entry_pyc tension is raised by the verifier report's own defect 2 text, not by council 2. The rejection is correct in substance (the symlink-safety property holds only for the guard helper), but the citation should name the verifier's framing and council 2's R4 bullet, not "C2-4".
- E4. F4 says "Council 2 C2-6 (R7 FIXED) likewise covers the linear case and the normalization set, not merges." Council 2's C2-6 is the codex-warning finding and has nothing to do with marker history. The linear-case coverage is council 2's R7 FIXED bullet (remote normalization 20/20 plus --topo-order present) and verifier A5 10/10. The point stands; the citation should read "Council 2 R7 FIXED".
- E5. The C2-10/F3 wrapper lists omit firejail and bwrap, which council 2 C2-10 names as class gaps (not installed on the VM, so not live forms there). The generic fix (extend the wrapper list, or resolve the ultimate command generically) covers them, but the summary lists should name them so the round-3 unit table does not drop them.
- E6. The C1-F3 fix omits council 1's _fail/SHIP_DIR point: council 1 F3 evidence says the SHIPPED.md note also does not mention _fail/SHIP_DIR, "which extracting _check_entry_pyc needs". The adjudication's fix covers the 14 tokenizer functions, the 4 constants, NUL-joined argv, and a copy-pasteable snippet or the extract_lib.py pointer, but not _fail/SHIP_DIR. The round-3 rewrite should add them if the note is meant to support extracting _check_entry_pyc, or the adjudication should have said the note covers the tokenizer only.
- E7. Round-3 instruction 9 omits council 1's INFO note that the verifier's extract_lib.py TOKENIZER_FUNCS still lists 12 functions (the round-1 set) while the plan round-2 section requires all 14. The re-verifier must update that list before re-running the batteries, or the AST comparison will under-cover the block. The adjudication's instruction 9 should name this.
- E8. The F3 (c) fix does not name `__import__('runpy').run_path` explicitly, although council 2 C2-2(c) lists it among the live-proved sink gaps. The generic "normalized __import__('X').Y( forms" covers it, but naming it explicitly would prevent it being dropped from the sink extension.

## Completeness note (not an error)

- N1. "What round 2 fixed" gives R9 _proven_no_body as 14/14 per redteam A8, verifier 12/12, council 2 12/12. Council 1 R9 probed 6 rows and all 6 matched. The adjudication does not mention council 1's count, but the row-set explanation ("the count difference is the row set, not a disagreement") covers it: council 1 probed 6 rows (no-key plus good snapshots True; eval_error empty, None, and set False; no snapshots False; hasBody True False).

## Round-3 fix pass instructions (council 1 additions to the adjudication's list)

1. All 10 instructions in the adjudication's round-3 fix pass stand as written; I agree with each.
2. Re-verify the corrected line numbers in E1a-E1f when the round-3 fix lands, so the next adjudication does not inherit the wrong ranges.
3. Add the firejail and bwrap wrapper names (E5), the _fail/SHIP_DIR note element (E6), the `__import__('runpy').run_path` sink name (E8), and the extract_lib.py TOKENIZER_FUNCS update to 14 (E7) to the round-3 fix list.
4. Confirm the round-3 base against the current tip of origin/todolist-push (now 8c6553a, past the adjudicated base 3167c76) before starting, and record the base commit in the round-3 report.
5. Re-verification must re-run the full batteries as the adjudication instructs, with an independent verifier that did not write the fix. No live run until that re-verification passes.

## Limits of this council review

- I did not re-run any live battery or any live run. Live numbers cited are the reviewers' numbers, confirmed present in their papers; my first-hand verification is the code reading cited by file and line and the review-file cross-checks.
- I did not re-review round 1. Findings above are round-2 diff items or round-2 interactions with existing code.
- The documented limits recorded in the round-2 reviews stand and are not findings: -m/import on a forged entry .pyc executes the forged bytecode in-process (unfixable in-process, controlled out-of-process by _check_entry_pyc); the Y6c marker is a coordination signal, not authentication (subject spoof passes by design); a self-consistent tamper (run_live.py plus manifest entry md5) passes the direct path and is refused by the launcher git comparison; `_path_is_runner_copy` fails open on an unresolvable path (documented in code at launch_y13.py:502-530, ports plus flock backstop applies).
