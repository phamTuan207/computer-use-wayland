# Batch 13 council 3 review of task 3 (Y13g round-3 adjudication)

- Reviewer: batch 13 council 3 agent.
- Date: 2026-11-22, work 14:28 to 14:40 +07.
- Report under review: docs/batch13-task3-y13g-round3-adjudication-20261122.md, commit e7d9a1c on origin/main.
- Code under review: branch todolist-push, HEAD 3167c76.
- Round-2 reviews checked in full: improvements/worker-y13g-r2-redteam.md (167a2e9), improvements/worker-y13g-r2-verify-report.md (75dff55), improvements/worker-y13g-r2-council-1.md (1e49436), improvements/worker-y13g-r2-council-2.md (6d83401), improvements/worker-y13g-r2-council-3.md (31c1126), all confirmed ancestors of todolist-push.
- Fix log checked: improvements/worker-y13g-fix-log.md, commit ab0b62c, confirmed ancestor of todolist-push.
- Authorization: coordinator Muse via coord/clone1.md batch 13, commit e03e288 on origin/main.
- Scope: report only. No shared code changed. No live run. No file on todolist-push modified. coord/clone1.md and coord/clone2.md not edited. The untracked 0-byte test-w.txt was left alone.

## Method

Every adjudication decision was re-verified first-hand against the code on todolist-push and against the five round-2 review documents. I re-read each cited code line myself and re-derived the key reasoning (the F1 conjunction, the F5 marshal comparison, the F2 environment pass-through, the tokenizer gaps). Live numbers cited below are the reviewers' numbers from their reports; I did not re-run any live battery or any live run. All numbers below were read from the cited files in this pass.

## Pins verified first-hand

- Runner tests/realistic/run_codex_y5.py md5 d5047ff573820491263a2eb3805105f4. Confirmed by md5sum of the todolist-push bytes.
- Launcher tests/realistic/launch_y13.py md5 8e72a5ce85cbaf8382f998987e8890e5. Confirmed the same way.
- Manifest tests/realistic/codex-y5-manifest.json md5 7c76383402e4c50b28adab6b25a22e09, 27 files, SHIPPED.md not among them. Confirmed by parsing the manifest on todolist-push.
- _SHIP_FILES is 29 paths in both entry points, identical sets, including the manifest itself and SHIPPED.md. Confirmed by AST parse of both files.
- run_live md5 84fa106c253d5e7f16daccf2ce3f14a5 (pin 1e3901c holds). Confirmed from the manifest entry and the five reviews agreeing.
- Round-2 fix commits 0639d04, 87eec47, 6ba43f2, 8bdd5aa, 5a9b9e8 all exist and are ancestors of todolist-push. Confirmed.

## Overall verdict: AGREE. BLOCK stands, no live run.

I agree with the adjudication's overall verdict and with every UPHELD decision and both REJECTED sub-claims. The two HIGH findings are correctly upheld, the MEDIUM and LOW findings are correctly upheld, and the severity calls (F1 HIGH over council 2 MEDIUM, F2 HIGH over council 2 LOW) are correctly reasoned. I found 8 minor issues below: 5 line-citation imprecisions, 1 evidence-precision slip, 1 incomplete fix-log characterization, and 1 small omission from the round-3 instructions. None of them changes any verdict or any fix direction.

## Per-decision verdicts

### F1 (redteam HIGH, C2-1): check_manifest exemption is dead code. AGREE, UPHELD, HIGH.

- launch_y13.py:1197 reads `if (not rel_root and _is_entry_pyc_rel(rel)):`. Confirmed by direct read.
- _is_entry_pyc_rel, launch_y13.py:295-300, returns False unless rel starts with `__pycache__/`. Confirmed. An entry .pyc therefore has rel_root `"__pycache__"` (truthy) and `not rel_root` is False, so the conjunction can never be True. The adjudication's derivation is correct.
- The module-top scan exemption at launch_y13.py:354-355 works (gated by _EXEMPT_ENTRY_PYC_FROM_SCAN, True in the launcher at :292, False in the runner at run_codex_y5.py:279). Confirmed. The two layers disagree, as stated.
- main() order is check_go, check_marker, write_token, check_manifest, _check_entry_pyc, _scan_ship. Confirmed by reading main(), with the line citation corrected in the issues list below.
- Live numbers quoted (redteam A2L 7/7, A2x 8/8, council 2 probe2x, council 3 H8) match the redteam paper, council 2, and council 3 documents. Confirmed.
- Severity HIGH: AGREE. The round-2 headline fix fails on the live path, the documented launcher flow cannot proceed with a legitimate entry .pyc, and any -m, import, or py_compile bricks the ship for the launcher until manual deletion. Fail-closed does not lower it, because the failure mode is a bricked legitimate flow, not a refused attack. Council 2 rated this MEDIUM; the adjudication's reasons for keeping HIGH are sound.
- Fix direction (drop `not rel_root and` at :1197, launcher-path test per stem, forged case refuses via marshal comparison): AGREE.

### F2 (redteam HIGH, C2-3): PYTHONPATH plants execute under -P. AGREE, UPHELD, HIGH.

- grep over both entry points returns zero matches for PYTHONPATH, PYTHONHOME, and PYTHONSTARTUP. Confirmed.
- Launcher exec env, launch_y13.py:1484-1499, is `env = dict(os.environ)` plus PYTHONSAFEPATH=1 and other keys, with no scrubbing. Confirmed.
- The launcher comment at :1495-1497 claims PYTHONSAFEPATH=1 keeps a planted stdlib .py from executing at import time in the runner. Confirmed. The claim is false for the PYTHONPATH channel, as stated, because -P removes sys.path[0] only and does not clear PYTHONPATH.
- The _check_entry_pyc fresh-compile subprocess, launch_y13.py:1289-1291, passes no env argument and inherits the caller environment. Confirmed.
- Live numbers quoted (redteam A6, 117 cases, 101 pass, 16 FAIL, all 16 this channel; the 13 .py names enum, re, json, socket, subprocess, hashlib, datetime, pathlib, copyreg, functools, collections, warnings, shlex; shlex.so fires; plant executes in the real launcher process at the post-scan import shlex; delegating shlex shim keeps verdicts correct; council 2 probe1 P1f rc 0 with marker present) match the redteam paper and council 2. Confirmed.
- The verifier does not contradict this: verifier A6d (66/66) tested ship-dir plants only, 15 .py names and 16 .so stems. Confirmed from the verifier report.
- Severity HIGH: AGREE. Planted code executes silently in both entry points with rc 0 and manifest_ok true, the launcher inherits the operator environment and passes it through, and the code's own comment makes a false safety claim. Council 2 rated this LOW on threat-model grounds; the adjudication's reasons for keeping HIGH are sound.
- Fix direction (scrub PYTHONPATH, PYTHONHOME, PYTHONSTARTUP from the launcher exec env and the fresh-compile subprocess env; refuse at module top in both entry points when PYTHONPATH is set and non-empty; correct the docstring claim): AGREE.

### F3 (redteam MEDIUM, C2-2): tokenizer residuals. AGREE, UPHELD, MEDIUM.

- _SINKS, launch_y13.py:569-572 and run_codex_y5.py:3984, lists 9 sinks and omits subprocess.getoutput, subprocess.getstatusoutput, os.popen, the os.exec and spawn family, and pty.spawn. Confirmed by grep over both files (zero matches for those names).
- _m_module_is_runner, launch_y13.py:586-600, special-cases only pdb; trace is not handled. Confirmed (the only "trace" match in the file is a comment about a traceback).
- _python_executes_runner, launch_y13.py:620-691: on tok `--` the parser breaks and falls through to `_token_is_runner_script(args[i], cwd)`. For `python3 -- -` that token is `-`, and _token_is_runner_script("-") returns False: `-` is not a runner basename or module name, and _path_is_runner_copy("-") returns False on a nonexistent file (os.path.isfile check). Confirmed by reading _token_is_runner_script (:534-543) and _path_is_runner_copy (run_codex_y5.py:3917 onward).
- The bare `python3 -` case is handled (tok `-` inside the loop returns True). Confirmed.
- Wrapper strip list in _command_executes_runner, launch_y13.py:706-855, covers env, nohup, setsid, exec, command, timeout, flock, bash/sh/zsh/dash -c, nice, stdbuf, taskset, sudo, uv. Confirmed. Absent: watch, xargs, ionice, chrt, numactl, systemd-run, unshare, su, runuser, prlimit, setarch (zero grep matches in the launcher for each). Confirmed.
- _is_timeout_dur, launch_y13.py:697-705, rejects `0x10` (not a digit string), so `timeout 0x10` is misread. Confirmed.
- Live numbers quoted (redteam A4 live dummy 59/59, live-forms 28/31 + 5/6, unit FRESH 2/29; council 2 probe3live and probe3_unit 63 cases; verifier A4 unit 81/81 and live 17/17 cover the specified table only) match the three documents. Confirmed.
- Mitigation accepted (in-process runs bind ports 8771/4452, check_runner_quiet scans every /proc entry, the child python is separately visible) matches council 2 C2-2 and C2-10. Confirmed. check_runner_quiet, launch_y13.py:993 onward, iterates /proc entries and reads cmdline and cwd per pid. Confirmed.
- Fix direction (a) through (f), including the argv/env smuggling note that check_runner_quiet already does per-pid /proc reads so an environ read is implementable: AGREE.

### F4 (redteam MEDIUM): topo-order does not order across merges. AGREE, UPHELD, MEDIUM.

- check_marker git log call, launch_y13.py:1119-1122, uses `--topo-order` with no `--first-parent`. Confirmed.
- Live numbers quoted (redteam A5, 32/32; case 10 forged completion on a side branch passes; case 11 stale abort on a side branch refuses) match the redteam paper. Confirmed.
- Verifier A5 10/10 covered linear history only. Confirmed from the verifier report.
- Fix direction (order by first-parent position only, e.g. `git log --first-parent --topo-order`, re-test with A5 cases 10 and 11): AGREE.

### F5 (redteam MEDIUM, verifier defect 1, C1-F8): relative-path py_compile .pyc refused. AGREE, UPHELD, MEDIUM.

- _check_entry_pyc, launch_y13.py:1242-1313. The fresh compile runs `compile(src, sys.argv[1], 'exec')` with src the absolute SHIP_DIR path (code string at :1285-1287, subprocess at :1289-1291). The comparison at :1302 is `marshal.dumps(cached_code) != marshal.dumps(fresh_code)`. co_filename is part of the marshalled code object, so a relative-path spelling mismatches. Confirmed.
- Corroboration quoted (verifier defect 1, A3h, 2 checks FAIL; council 1 F8 probe P3b) matches the verifier report and council 1. Confirmed.
- Fix direction (normalize co_filename before comparing, re-test with the A3h cases): AGREE.

### Verifier defect 2: symlink-unsafe deletion in _check_entry_pyc. AGREE, UPHELD, MEDIUM.

- _check_entry_pyc, launch_y13.py:1263-1271, uses plain os.listdir(cache_dir), and deletes verified files with plain os.unlink(cached_path) at :1307. There is no realpath-inside-ship check anywhere in the function. Confirmed.
- Contrast with _entry_pyc_paths, launch_y13.py:190-213 (and the runner copy), which returns [] when the realpath of the cache dir is not inside the realpath of the ship dir. Confirmed.
- Live proof quoted (verifier A7 shape-6b, proven twice, legit .pyc behind a symlinked __pycache__ deleted outside the ship, driver rc 0 "verified + removed") matches the verifier report. Confirmed.
- Reachability limit honestly recorded (module-top scan refuses a symlinked __pycache__ first; the scan flags symlinks, launch_y13.py:350-355). Confirmed.
- Fix direction (one realpath check at the top of _check_entry_pyc, mirroring _entry_pyc_paths, re-test with A7 shape-6b): AGREE.

### F6 (redteam LOW-MEDIUM, C2-5, verifier A2l): -m guard leaves an empty nested dir. AGREE, UPHELD, LOW.

- _entry_pyc_paths (runner run_codex_y5.py:138-170, launcher launch_y13.py:190-213) returns file paths only, and both guards unlink files only, never pruning directories. Confirmed.
- _is_exempt_cache_dir (runner :290-312) exempts only a top-level __pycache__ (rel != "__pycache__" returns False). Confirmed.
- Corroboration quoted (council 2 C2-5 probe P4b, verifier A2l) matches both documents. Confirmed.
- Downgrade from LOW-MEDIUM to LOW: AGREE. The reasoning matches the verifier's own note that a probe only ever writes top-level .pycs, so a nested dir can only appear by hand, and recovery is one rmdir.
- Fix direction (guard removes empty dirs it emptied, bottom-up rmdir, keep the scan strict): AGREE.

### F7 (redteam LOW): check_manifest gaps. AGREE, UPHELD, LOW.

- check_manifest walk, launch_y13.py:1182-1204, flags only symlinked dirs, symlinked files, .pyc files, and top-level .py files not in the manifest. It does not flag a FILE named __pycache__, a DIRECTORY named like a .pyc, or a nested .py. Confirmed by reading the walk.
- Fix direction (flag any file or dir not in the manifest set, the same allowlist _scan_ship uses): AGREE.
- Severity LOW with the _scan_ship backstop: AGREE.

### C1-F1 and C3-3: runner docstring launch lines lack -P. AGREE, UPHELD, Medium-Low.

- run_codex_y5.py:103 reads `cd /tmp/worker-y13-server && Y13_GO=1 python3 launch_y13.py all` and :105 reads `Y13_GO=1 python3 launch_y13.py 01 02`, with no -P. Only :106 has -P. Confirmed.
- Probes quoted (council 1 P7, council 3 P7d, rc 2) match both documents. Confirmed.
- Council 3 also asks for --repo on those lines, matching the launcher docstring and SHIPPED.md. Confirmed from council 3 C3-3. The launcher docstring usage lines carry -P with --repo. Confirmed, with the line citation corrected in the issues list below.
- Fix direction (add -P and --repo to lines 103 and 105, regen the manifest, re-verifier runs the docstring lines as written): AGREE.

### C1-F2: launcher -m guard runs after _derive_ship_dir. AGREE, UPHELD, Medium-Low.

- launch_y13.py:185 `SHIP_DIR = _derive_ship_dir()` runs before the __spec__ guard at :227-236. Confirmed.
- The repo-tree refusal sits inside _derive_ship_dir (print at :170). Confirmed.
- _entry_pyc_paths uses the derived _SHIP_DIR (:190-213). Confirmed.
- The runner has no such ordering issue (its _SHIP_DIR is the file dir at run_codex_y5.py:131, guard at :184). Confirmed.
- Probes quoted (council 1 P4a repo-tree, P4b control, P4c --ship-dir elsewhere) match council 1. Confirmed.
- Fix direction (guard before _derive_ship_dir against a provisional file-dir ship, derive the real SHIP_DIR after the guard, keep the safe-path check after the guard): AGREE.

### C1-F3 and C3-2: SHIPPED.md How to verify omits the module constants. AGREE, UPHELD, Moderate (C3-2) / Low (C1-F3).

- tests/realistic/codex-y5/SHIPPED.md:43-49 says to exec the named FunctionDef nodes with os/json/hashlib/re/shlex/subprocess/time/marshal and _SHIP_DIR set, without naming the 14 functions or the 4 constants. Confirmed.
- The 4 constants are _RUNNER_MODULE_NAMES, _RUNNER_MANIFEST_PATHS, _RUNNER_MD5S (run_codex_y5.py:3860-3866) and _PY_NO_VALUE (:4032). Confirmed.
- Probes quoted (council 1 P2c and council 3 P6, NameError: name '_RUNNER_MODULE_NAMES' is not defined; council 3 also proved the NUL-joined argv gap, all 6 cases pass with the constants added and NUL-joined argv) match both documents. Confirmed.
- Fix direction (rewrite the note, name the 14 functions or point at the sync block, add the 4 constants, say cmdlines are NUL-joined argv lists, give one copy-pasteable snippet, or point at the verifier extraction script): AGREE.

### C1-F4: -c sink docs say subprocess.* but the code covers 5 methods. AGREE, UPHELD, Low.

- _SINKS lists subprocess.call, subprocess.run, subprocess.Popen, subprocess.check_output, subprocess.check_call; subprocess.getoutput and subprocess.getstatusoutput are absent. Confirmed.
- Council 1 probe P6 (getoutput returns False, run returns True) matches council 1. Confirmed.
- Fix direction (add the two methods to _SINKS in both copies, subsumed by the F3 sink extension): AGREE.

### C1-F5 and C3-5 (comment half): stale two entry .pyc comment. AGREE, UPHELD, Low.

- run_codex_y5.py:750 reads "the two entry .pyc files (0, 1, or 2)". Confirmed.
- The code now has three stems. Confirmed (_ENTRY_STEMS has 3 entries in both files).
- The related scope note (dir exemption uses _ENTRY_PYC_NAMES, current cache tag only, while the scan and _check_entry_pyc are any-tag; outcome-identical, no code change required) matches council 1 and is correct by code reading: the runner scan refuses any .pyc before _verify_manifest can see one. Confirmed.
- Fix direction (change the comment to three entry .pyc files): AGREE.

### C1-F6 and C3-5 (plan half): repo-tree wording overgeneralizes, B1 wording contradictory. AGREE, UPHELD, Low.

- Plan improvements/worker-y13-codex-y5-live-plan.md:714-716 says a repo-tree path refuses with the repo-tree message; SHIPPED.md:20-24 says the same. Confirmed.
- Only the file-dir derivation branch refuses with that message; an explicit --ship-dir pointing at a repo tree is accepted as SHIP_DIR and refused later by the module-top scan as tampered. Confirmed by reading _derive_ship_dir and by council 1's live probe quoted in the adjudication.
- Plan :633-638 (B1) still says the dir exemption holds "ONLY when it holds only entry .pyc files (0-3)", while run_codex_y5.py:294-299 says observably this exempts an EMPTY __pycache__ dir only. Confirmed.
- Fix direction (scope the repo-tree sentences to the file-dir branch; reword B1 to empty-dir only): AGREE.

### C1-F7 and C2-7: main exec subprocess.run is not wrapped. AGREE, UPHELD, Low.

- launch_y13.py:1503 `proc = subprocess.run(cmd, cwd=SHIP_DIR, env=env)` has no try/except. Confirmed.
- The other five launcher subprocess.run calls (remote 1068, fetch 1110, log 1119, show 1206, fresh compile 1289) are wrapped in try/except (OSError, TimeoutExpired) into _fail exit 2. Confirmed by reading each call site.
- Council 2 notes the OSError path is a code-reading verdict, not live-proven. The adjudication accepts it as such. Correct.
- Fix direction (wrap the exec call the same way): AGREE.

### C2-4: a ship missing SHIPPED.md passes every gate. AGREE, UPHELD, Low.

- The scan iterates files present, so a missing file is invisible; _verify_manifest checks only the 27 manifest entries, and SHIPPED.md is not one. Confirmed from the manifest (27 entries, no SHIPPED.md) and the scan code.
- Council 2 probe1 P1c (ship with SHIPPED.md deleted, direct verify rc 0, manifest_ok true) matches council 2. Confirmed.
- Fix direction (refuse when any allowlist file is absent, or add SHIPPED.md to the manifest-checked set): AGREE.

### C2-6: codex warning fires on mere mentions of the codex path. AGREE, UPHELD, Low.

- _is_codex_process, launch_y13.py:872-888, checks `for tok in parts[1:]: if tok.lower().endswith("/codex"): return True`, so any token in any position ending in /codex counts. Confirmed. The docstring claims an execution position, but the code does not check position. Confirmed.
- Council 2 probe P6 (grep, echo, ls with a /codex path all return True) matches council 2. Confirmed.
- Fix direction (match only argv[0] basename codex, or a /codex token in an execution position): AGREE.

### C2-8: ssh:// remote form refuses. AGREE, UPHELD, Low.

- _normalize_remote_url, launch_y13.py:1033-1056, handles the scp-like git@ form and :// forms, but an ssh:// URL normalizes to an ssh:// URL that mismatches the pinned https URL; it strips only one trailing slash and strips `.git` case-sensitively. Confirmed.
- Council 2 probe P7 (20 cases) matches council 2. Confirmed.
- Fix direction (normalize ssh:// to https the same way as the scp-like form; strip all trailing slashes; case-fold the .git suffix): AGREE.

### C2-9: docs still overclaim what the code does. AGREE, UPHELD, Low.

- Plan B1/B4 plus the round-2 section claim the launcher verifies the entry .pyc out-of-process and deletes it before exec, with the scan plus check_manifest exempting entry .pyc. Confirmed in the plan at :633-638. False in the round-2 code, per F1. Confirmed.
- B3 lists the -c sinks as exec, eval, os.system, subprocess.*, runpy.run_path plus a quoted .py path md5 check (plan :673-674), but the code misses the C2-2 sinks. Confirmed.
- The LIMIT paragraph documents only string-concatenation, not argv/env smuggling, -m trace, or `python3 -- -`. Confirmed by reading the plan B3 LIMIT paragraph.
- B2 says "check_manifest refuses planted top-level .py, non-entry .pyc, and symlinks" (plan :656-657). Confirmed. check_manifest refuses ALL .pyc including entry ones, so the "non-entry" qualifier is wrong, as stated.
- Amend 2 says a bare codex token and a path merely containing a codex directory do NOT warn (plan :699-702). Confirmed. True for those cases, but path mentions still warn, per C2-6. Confirmed.
- Fix direction (correct each bullet to the code as fixed): AGREE.

### C2-10: wrapper unit gaps. AGREE, UPHELD, Low.

- Wrapper strip list covers env, nohup, setsid, exec, command, timeout, flock, bash/sh -c, nice, stdbuf, taskset, sudo, uv. Confirmed.
- Council 2 probe3_unit misses (time, watch, xargs, ionice, chrt, numactl, systemd-run, unshare, su, runuser, prlimit, setarch; sudo VAR=1, setsid -w / --wait, command -p, nohup --, env -S) match council 2. Confirmed.
- Live impact nil per council 2 probe3wrap2 (child python separately visible in /proc and caught by the per-process scan). Matches council 2. Confirmed as reported.
- Fix direction (extend the wrapper list or apply a generic rule, folded into the F3 fix): AGREE.

### C3-1: --ship-dir=DIR and --repo=DIR are silently ignored. AGREE, UPHELD, Moderate.

- _derive_ship_dir, launch_y13.py:144-157, matches "--ship-dir" by exact string only. Confirmed.
- main() stripping at :1464-1472 handles only the exact "--ship-dir" token. Confirmed.
- Probes quoted (council 3 P2d, P2e, P3b, P3d, P3e, P3e2; `--ship-dir=<emptydir>` still reaches the go gate; `--repo=/path` gives "--repo is required"; unstripped = token reaches the runner as an unknown test selector) match council 3. Confirmed.
- Fix direction (refuse any argv token starting with "--ship-dir=" or "--repo=" in _derive_ship_dir before the repo-tree check, with the same refusal in main() as a backstop): AGREE.

### C3-4: scan fix hint misleads when a directory is in the list. AGREE, UPHELD, Moderate-Low.

- Scan JSON fix field, run_codex_y5.py:347-353, and launcher message, launch_y13.py:367-371, say "delete the named files, or re-stage the ship with the regen script". Confirmed.
- Probes quoted (council 3 P5a, P5a2, P5a3; deleting only the named .pyc leaves the empty nested dir, verify still refuses rc 2 kind unexpected-dir; only rmdir recovers) match council 3. Confirmed.
- Fix direction (word the hint "delete the named files and directories", or do not list a directory whose only content is already listed): AGREE.

### C3-6: _scan_ship md5 message does not distinguish the edited case. AGREE, UPHELD, Low.

- _scan_ship refuses an edited ship file with "ship file md5 mismatch: ... (stale or edited ship; re-stage)". Confirmed, with the line citation corrected in the issues list below.
- Council 3 probe P5e (re-stage alone does not settle the edited case, because regen rebuilds the manifest from the working tree, so _scan_ship then passes but check_manifest refuses next) matches council 3. Confirmed as reported.
- Fix direction (mirror the check_manifest wording about commit plus push first, then re-stage): AGREE.

### C3-7: hint-less refusal legs. AGREE, UPHELD, Low.

- check_manifest, launch_y13.py:1188-1210, refuses "planted symlink dir in ship", "planted symlink in ship", and "planted top-level .py in ship" with no fix hint, while the .pyc leg right next to them says "Fix: delete the file, or re-stage the ship". Confirmed.
- _scan_ship legs likewise name the path only (symlink dir, __pycache__ holds files, unexpected directory, symlink, bytecode, unexpected file, unreadable, md5 mismatch). Confirmed by reading _scan_ship.
- Reachability limited (module-top scan fires first, so these legs are TOCTOU-only in practice). The adjudication records this. Correct.
- Fix direction (add the same Fix suffix to each leg): AGREE.

### C3-8: write_token runs before the ship-integrity checks. AGREE, UPHELD, Low.

- main() order is check_go, check_marker, write_token, check_manifest, _check_entry_pyc, _scan_ship, check_token. Confirmed by reading main().
- Fix direction (move write_token() to just after _scan_ship, immediately before check_token()): AGREE.

### Disagreement resolution 1: council 1 R2 "launcher scan + check_manifest exempt top-level entry .pyc". AGREE, REJECTED on the check_manifest half.

- Council 1's "What was verified as consistent" R2 states exactly this claim. Confirmed.
- The module-top scan exemption works (launch_y13.py:354-355, flag True). The check_manifest exemption at :1197 is unsatisfiable (see F1). The adjudication's split verdict (scan half accepted, check_manifest half rejected) is correct.

### Disagreement resolution 2: council 2 C2-4 "R4 FIXED" as applied to _check_entry_pyc. AGREE, REJECTED.

- Council 2's R4 FIXED claim covers the guard helper _entry_pyc_paths on -m (symlinked __pycache__ deletes nothing outside the ship). Confirmed from council 2.
- _check_entry_pyc has no such check (see verifier defect 2). Confirmed by code reading.
- C2-4 stands only for the guard helper. Correct.

### Disagreement resolution 3: severity votes (C2-1 MEDIUM, C2-3 LOW) vs redteam (F1 HIGH, F2 HIGH). AGREE, redteam ratings stand.

- Council 2 rated C2-1 MEDIUM and C2-3 LOW; redteam rated F1 and F2 HIGH. Confirmed from both documents.
- The underlying facts are not in dispute; all reviewers agree on the code facts. Confirmed by cross-reading the five reviews.
- The adjudication's reasons for keeping HIGH are sound (see F1 and F2 above).

### Disagreement resolution 4: redteam F3 vs council 2 C2-10 on wrapper live impact. AGREE, both stand.

- The single-cmdline verdict is wrong for the listed wrappers (redteam live proof). The child python is separately visible in /proc and caught by the per-process scan (council 2 probe3wrap2). Both are true, and the MEDIUM rating for F3 already reflects the mitigation. Correct.

### Disagreement resolution 5: verifier 277/280 vs redteam BLOCK. AGREE, consistent.

- The verifier's 3 failures are 2 root causes, both in _check_entry_pyc (F5 and defect 2). Confirmed from the verifier report (277/280, A3h 2 checks, A7 shape-6b 1 check).
- The verifier did not test the check_manifest path (F1), the PYTHONPATH channel (F2), the new tokenizer evasions (F3), or merge ordering (F4). Confirmed from the verifier report (A2h/A2i cover the isolated function and the scan exemption, A6d covers ship-dir plants only, A4 covers the specified table, A5 covers linear history).
- Its FAIL verdict and the redteam BLOCK verdict agree that no live run may proceed. Correct.

### Disagreement resolution 6: fix-log Design C vs the implemented code. AGREE on the fix direction, DISAGREE in part on the fix-log characterization. See issue 6 below.

- The fix direction (exempt on _is_entry_pyc_rel(rel) alone at :1197) is correct and I agree with it.
- The adjudication's characterization of the fix log is incomplete: it cites only the early pre-implementation Design C wording and omits the log's own operative R2 design section, which directs the same exemption the adjudication prescribes.

### "What round 2 fixed" section. AGREE.

- Ship-dir .so and .py plants all refuse; symlinks all refuse except verifier defect 2; R5 entry .py hash check (tampered run_live.py refuses before import on the direct path); R9 _proven_no_body 14/14 per redteam A8, verifier 12/12, council 2 12/12 (the count difference is the row set, not a disagreement); marker ordering on a linear history; remote-URL normalization except C2-8 ssh://; _SHIP_FILES identical (29 files); AST identity True for the 14 tokenizer defs; handover token round-trip (council 3 H7). All match the five round-2 reviews. Confirmed.

### Round-3 fix pass instructions (items 1-10). AGREE, with one addition.

- Items 1-8 (fix order, F1 plus F5 together, F2 env scrub plus refusal plus docstring, defect 2 realpath check, F4 first-parent, F3 tokenizer in both copies AST-identical, F6/F7, the council items, manifest regen and doc sync) follow correctly from the upheld findings. AGREE.
- Item 9 (re-verification re-runs the full batteries plus new cases, independent verifier, no live run until it passes) is correct. AGREE, with the addition in issue 7 below.
- Item 10 (harness lesson: round-2 attack harnesses under /tmp were lost before round-2 review closed; stage round-3 harnesses under the persistent workspace, never /tmp-only) matches the fix log lines 187-195 ("HARNESS LOSS. /tmp/y13r2/ and /tmp/y13r2-redteam/ are GONE"). Confirmed. AGREE.

### Limits section. AGREE.

- The adjudication states it did not re-run any live battery or live run, that live numbers cited are the reviewers' numbers, and that its first-hand verification is the code reading cited by file and line. Honest and accurate.
- The documented limits listed (forged entry .pyc executes via -m/import in-process; Y6c marker is a coordination signal, not authentication; self-consistent tamper passes the direct path and is refused by the launcher git comparison; _path_is_runner_copy fails open on an unresolvable path) match the redteam and verifier documented limits. Confirmed.

## Issues found in the adjudication (none verdict-changing)

1. Line citation, F1 main() order: the adjudication cites launch_y13.py:1468-1472 for the check order, but the order lines are 1472-1477 (check_go at 1472, check_marker at 1473, write_token at 1474, check_manifest at 1475, _check_entry_pyc at 1476, _scan_ship at 1477). The order stated is correct; only the range is off. Council 2 made the same citation, and the adjudication inherited it.
2. Line citation, C3-6: the adjudication cites launch_y13.py:1340-1345 for the _scan_ship md5 message, but the message is at :1373-1374 ("ship file md5 mismatch: {rel} (stale or edited ship; re-stage)"). Lines 1340-1345 are the walk start of _scan_ship. The message text quoted is correct; only the line range is off. Council 3 made the same citation, and the adjudication inherited it.
3. Line citation, C3-7: the adjudication cites launch_y13.py:1336-1345 for the _scan_ship legs, but the legs span :1346-1374 (symlink dir, __pycache__ holds files, unexpected directory, symlink, bytecode, unexpected file, unreadable, md5 mismatch). The substance (legs name the path only, no fix hint) is correct; only the range is off. Council 3 made the same citation, and the adjudication inherited it.
4. Line citation, C1-F1/C3-3: the adjudication cites the launcher docstring usage lines as (:109-110), but the -P with --repo lines are at launch_y13.py:107-108. The substance (launcher docstring and SHIPPED.md both use -P with --repo) is correct; only the line numbers are off by 2. Council 3 made the same citation, and the adjudication inherited it.
5. Evidence precision, F1: the adjudication writes that the legit entry .pyc cases "all refuse rc 2 with '[launch_y13] REFUSED: planted bytecode in ship: __pycache__/run_codex_y5.cpython-312.pyc'". That exact filename is correct for the run_codex_y5 stem cases; the run_live stem case would name run_live.cpython-312.pyc instead. The message template and the rc 2 outcome are right for all four cases; only the quoted filename is stem-specific. Trivial; no verdict impact.
6. Incomplete fix-log characterization, disagreement resolution 6: the adjudication says the fix log says the entry-.pyc exemption was REMOVED from the scan and from _verify_manifest, and that the round-3 fix follows "this adjudication, not the log's removal wording". That removal wording is real, but it is only the early pre-implementation Design C in the log (lines 43-45, written before any edit). The log's own operative R2 design section (lines 420-424) says the opposite for the live path: "Exempt the 3 entry stems (any tag, top-level __pycache__ only) from the LAUNCHER top scan AND check_manifest .pyc refusal, so _check_entry_pyc adjudicates; runner scan stays strict." The log also records the worker's own admission of the bug (lines 717-720: the R2 design said "exempt the 3 entry stems from check_manifest", and the rel_root gate was the worker's own error in 87eec47). So the adjudication's fix direction (exempt at :1197) actually matches the log's operative R2 design; the contrast with "the log's removal wording" is incomplete because it omits the R2 section. The fix direction is still correct, and the round-3 pass should follow the adjudication's fix, but the resolution should have cited the R2 section and the worker's admission, which corroborate the fix rather than conflict with it. Also unnoted: Design C (a) says the exemption was "REMOVED from the scan", while the implemented launcher scan does exempt entry .pyc (flag True at launch_y13.py:292, exemption at :354-355); the R2 design section supersedes Design C on that point too, and the adjudication does not note the supersession.
7. Small omission, round-3 instructions item 9: the re-verification instructions do not mention council 1's INFO note that the verifier's extract_lib.py TOKENIZER_FUNCS still lists 12 functions (the round-1 set) and must be updated to cover all 14 for the AST comparison. The re-verifier needs that update; add it to the round-3 instructions.
8. Trivial precision, C1-F5: the adjudication repeats council 1's "grep confirms this is the only remaining 'two entry' mention in the reviewed files". That is true within the six fix files (run_codex_y5.py:750 is the only one), but the fix log itself contains five "two entry" mentions (lines 47, 62, 169, 543, 585) quoting old text. The stale comment at :750 is real and verified; the grep claim is only true if the log is excluded from "the reviewed files". No verdict impact.

## Missing fixes

None substantive. Every finding in all five round-2 reviews is adjudicated, and every upheld finding has a correct fix direction in the adjudication. The only additions are the two notes in issues 6 and 7 above: cite the fix log's R2 design section and the worker's admission when justifying the :1197 fix, and add the extract_lib.py TOKENIZER_FUNCS update (12 to 14) to the round-3 re-verification instructions.

## Final verdict

AGREE with the adjudication in full: BLOCK stands, F1 and F2 HIGH upheld, all MEDIUM and LOW findings upheld, both sub-claim rejections correct, both severity calls correct, and no live run until the round-3 fix pass lands and is independently re-verified. The 8 issues above are citation and completeness notes only; none changes any verdict or fix direction.
