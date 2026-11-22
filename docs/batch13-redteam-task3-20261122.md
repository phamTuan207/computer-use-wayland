# Batch 13 redteam task 3: Y13g round-3 adjudication review

- Redteam: batch 13 redteam task 3 agent (independent review of the adjudication, not its author).
- Date: 2026-11-22, work 14:27 to 14:42 +07.
- Repo: ~/workspace/computer-use-wayland. Report branch: main.
- Code under review: branch todolist-push, HEAD 3167c76.
- Adjudication under attack: docs/batch13-task3-y13g-round3-adjudication-20261122.md, commit e7d9a1c.
- Round-2 reviews re-read first-hand: redteam improvements/worker-y13g-r2-redteam.md commit 167a2e9, verifier improvements/worker-y13g-r2-verify-report.md commit 75dff55, council 1 improvements/worker-y13g-r2-council-1.md commit 1e49436, council 2 improvements/worker-y13g-r2-council-2.md commit 6d83401, council 3 improvements/worker-y13g-r2-council-3.md commit 31c1126, fix log improvements/worker-y13g-fix-log.md commit ab0b62c.
- Authorization: coordinator Muse via coord/clone1.md batch 13, commit e03e288 on origin/main.
- Scope: report only. No shared code changed. No live run. No file on todolist-push modified. coord/clone1.md and coord/clone2.md not edited. The untracked 0-byte test-w.txt was left alone.

## Method

Every attack below was verified first-hand against the real code on todolist-push (file paths and line numbers cited) or against a stdlib-only probe run in /tmp on Python 3.12.3, the same version the verifier used. I did not re-run the reviewers' live batteries and I did not run any live run. The marshal probes compiled a small scratch module in /tmp with relative and absolute filenames; they never executed repo code. Numbers quoted from the five round-2 reviews are the reviewers' numbers, checked against the review texts named above.

## Verdict: BROKEN

The adjudication document is BROKEN as a round-3 work order, even though its headline outcome survives: the facts behind F1 and F2 are correct, and BLOCK stands on F1 alone. Three breaking findings force the verdict:

1. B1: the adjudication's "Fix (exact)" for F5 lists a co_filename fix that provably does not work (top-level-only code.replace).
2. B2: the adjudication's F3 fix (b) rests on a false premise about check_runner_quiet (it does not read /proc/PID/environ anywhere).
3. B3: several cited line numbers are wrong, and three of them match council 3's identical wrong ranges, which contradicts the adjudication's method claim of first-hand line verification.

Round 3 must not follow the adjudication's fix text verbatim. Use the corrected fixes at the end of this report instead.

## Breaking findings

### B1 (breaking): the F5 "Fix (exact)" option (a) does not work

The adjudication's F5 section says, under the heading "Fix (exact)": "normalize co_filename in the comparison, e.g. code.replace(co_filename=src) on both sides before marshalling, or read co_filename from the cached code object and compile the fresh reference with that same filename."

Option (a) does not work. code.replace(co_filename=...) replaces only the top-level code object's filename. Nested function and class code objects keep the original spelling, and marshal.dumps of the top object includes those nested objects, so the comparison still mismatches. All three entry files contain nested defs, so option (a) would leave F5 unfixed for every real case.

First-hand probe (Python 3.12.3, scratch module with one function and one class with one method, compiled once with the relative name `cf_src.py` and once with the absolute name `/tmp/cf_src.py`):

- As compiled: marshal equal False (the F5 mechanism, confirmed).
- After top-level-only replace on the cached side: marshal equal False. Nested co_filenames stayed `cf_src.py`.
- After top-level-only replace on BOTH sides: marshal equal False. Nested co_filenames stayed `cf_src.py` on the cached side and `/tmp/cf_src.py` on the fresh side.
- The second alternative works: compiling fresh with the cached co_filename gives marshal equal True (verified twice in clean runs).

So the adjudication offers one broken option first and one working option second, under a heading that promises an exact fix. A round-3 implementer following option (a) would ship a still-broken F5 and fail re-verification. The adjudication inherited option (a) from the verifier's fix shape ("code.replace(co_filename=src) on both sides") without testing it, even though the F5 comparison it prescribes lives at launch_y13.py:1302 (`if marshal.dumps(cached_code) != marshal.dumps(fresh_code):`) and the fresh compile at :1285-1287 uses `compile(src, sys.argv[1], 'exec')` with the absolute SHIP_DIR path.

Supporting observation, reproduced three times on Python 3.12.3: while a code.replace() sibling of a code object is alive, marshal.dumps() of the original object returns different bytes (24 bytes differed in my probe, including small-tuple reference markers), and once the sibling is freed the bytes revert to the original. Any replace-based comparison is therefore fragile on this Python, on top of being incomplete for nested code objects. I assert the observed bytes, not a mechanism. Round 3 must use only the compile-with-cached-filename option.

### B2 (breaking): the F3 fix (b) premise about /proc/PID/environ is false

The adjudication's F3 fix (b) says: "when a -c sink is present, treat sys.argv[N] and os.environ[...] path sources as runner candidates (fail-closed when the argv/env value is a runner script); check_runner_quiet can read /proc/PID/environ, so this is implementable".

check_runner_quiet cannot read /proc/PID/environ today, because no such read exists. First-hand from launch_y13.py:993-1032: check_runner_quiet reads /proc/PID/cmdline (via _cmdline) and /proc/PID/cwd (via os.readlink) only. A grep over both entry-point files finds zero reads of /proc/PID/environ, and zero occurrences of the string `environ` outside os.environ calls. The argv half of the fix is implementable as stated (argv values are present in the cmdline that _is_runner_cmdline already receives), but the env half needs a brand-new environ-reading capability in check_runner_quiet, with its own permission and robustness questions, and _c_code_executes_runner would also need the following argv threaded through, since it currently receives only the code string (launch_y13.py:548-568). The adjudication presents the env half as already available. It is not. The fix as written is under-specified, not exact.

### B3 (breaking): wrong line numbers, copied from council 3

The adjudication's method section claims every decision "rests on first-hand reading of the round-2 code on todolist-push (file and line numbers cited)". The following citations are wrong, verified against todolist-push HEAD 3167c76. Three of them repeat council 3's identical wrong ranges, so they were copied, not verified.

| Adjudication citation | What is actually there | Correct lines |
|---|---|---|
| C3-6: "_scan_ship, launch_y13.py:1340-1345, refuses an edited ship file with ship file md5 mismatch" | 1340-1345 is the allowlist-prefix loop plus the os.walk header; no refusal leg at all | md5 _fail at :1373-1374 |
| C3-7: "_scan_ship legs at :1336-1345 likewise name the path only" | 1336-1345 contains zero refusal legs; the first _scan_ship leg (symlink dir) is at :1346 | legs at :1346-1373 |
| C3-4: "scan JSON fix field, run_codex_y5.py:347-353" | 347-353 is the file-loop exemption logic; the fix field string is not there | fix field at run_codex_y5.py:363 (launcher half :367-371 is correct, message at :368) |
| F1: "main() order, launch_y13.py:1468-1472, is check_go, check_marker, write_token, check_manifest, _check_entry_pyc, _scan_ship" | 1468-1472 covers the --ship-dir stripping plus check_go only | order at :1472-1477 |
| C3-8: "main() order, launch_y13.py:1474-1479, is check_go, check_marker, write_token, check_manifest, _check_entry_pyc, _scan_ship, check_token" | check_go is :1472 and check_marker is :1473, both outside the cited range | order at :1472-1478 |
| F2: "Launcher exec env, launch_y13.py:1486-1498: env = dict(os.environ) plus PYTHONSAFEPATH=1" | env = dict(os.environ) is at :1484; :1486 is LIVE_SERVER_ROOT | env block at :1484-1500 |
| Verifier defect 2: "_check_entry_pyc, launch_y13.py:1263-1271: cached_names comes from plain os.listdir(cache_dir), and verified files are deleted with plain os.unlink(cached_path)" | listdir comprehension starts at :1262; the unlink is at :1307, outside the cited range | listdir at :1262-1264, unlink at :1307 |

The substance behind C3-6, C3-7, and C3-4 (messages lack hints, hint says "files" for a dir) is correct; only the citations are wrong. But a work order whose line citations point at the wrong code cannot be followed as written, and the copying shows the method claim fails for these items.

## Minor findings

### M1 (moderate): the F4 --first-parent fix lacks its linearity precondition

The adjudication calls `git log --first-parent --topo-order` "the correct fix" and says side-branch markers "are ignored entirely". It never checks the real marker history. The real todolist-push history is not linear: it has 15 merge commits in 1234 commits. I verified the current marker set is safe (exactly 1 commit touches improvements/worker-y6c-*.md, commit 5a2b69d, and it is on the first-parent leg), so the fix would not change any live marker today. But the adjudication never establishes that, and never states the precondition the fix needs: markers must land as first-parent commits, and a marker that ever arrives via a merge would be silently ignored by the gate, which is the same false-refusal class as redteam case 11. The fix needs the precondition documented and a check that no marker commit is merge-introduced before the switch.

### M2 (moderate): the adjudication missed council 1's stale-extractor flag

Council 1's INFO note says the verifier's extract_lib.py TOKENIZER_FUNCS still lists 12 functions (the round-1 set) while the plan says the AST comparison must cover all 14. The adjudication never mentions this, and its "What round 2 fixed" section accepts "AST identity True for the 14 tokenizer defs" from the reviews. I counted first-hand: the tokenizer block holds 14 defs in both files (_script_basename_is_runner, _is_python_token, _shlex_tokens, _runner_md5s, _path_is_runner_copy, _token_is_runner_script, _c_code_executes_runner, _m_module_is_runner, _python_executes_runner, _is_timeout_dur, _command_executes_runner, _argv_tokens, _is_runner_cmdline, _is_codex_process), while the committed improvements/y13g-verify/extract_lib.py TOKENIZER_FUNCS lists 12, missing _m_module_is_runner and _is_timeout_dur. The claimed 14-function AST check therefore cannot be reproduced from the committed extractor. The adjudication should have flagged the stale committed harness instead of accepting the 14-function claim unexamined.

### M3 (minor): the F2 HIGH rating is debatable, but it does not change the verdict

Council 2 rated C2-3 LOW on threat-model grounds: the channel needs attacker control of the operator environment, which is outside the ship-tamper model, and an attacker with env control already owns the operator shell. The adjudication keeps HIGH, arguing the poisoned-operator-environment threat "closes cheaply" and "a false safety claim in the code is itself a HIGH defect". The first argument is weakened by M4 (the fix does not close the launcher's own startup channel), and the second upgrades a documentation falsehood to HIGH, which is a stretch. The F2 facts are not in dispute, and BLOCK stands on F1 regardless, so this is a severity judgment call, not a factual error. I record the disagreement rather than overturning the rating.

### M4 (minor): the F2 fix does not close the launcher's own startup channel

The adjudication's F2 fix refuses on PYTHONPATH at module top "next to the safe-path check" and scrubs PYTHONPATH, PYTHONHOME, and PYTHONSTARTUP from the launcher exec env and the fresh-compile subprocess env. The child-env scrub works. But the module-top refusal covers PYTHONPATH only, never PYTHONHOME, and no in-process check can close the launcher's own startup channel: a poisoned PYTHONHOME or a sitecustomize.py plant fires at interpreter startup, before any module-top code runs. The adjudication's claim that the fix "closes cheaply" the poisoned-operator-environment threat is therefore an overclaim for the launcher's own process and the direct-runner path. The fix is still the right shape for the child processes; the residual startup channel should be stated as a documented limit, not implied closed.

### M5 (minor): the C3-1 main() backstop can never fire

The adjudication's C3-1 fix says to refuse --ship-dir= and --repo= tokens in _derive_ship_dir and to "do the same in main() as a backstop". _derive_ship_dir runs at module top (launch_y13.py:185), before main() runs, so a = form token is refused at import and main() can never see one. The backstop is dead code by construction. Harmless, but the "exact" fix prescribes unreachable code.

### M6 (minor): one finding carries two severities

The decision table lists C1-F3 as Low and C3-2 as Moderate for the same SHIPPED.md "How to verify" gap, and the section heading repeats "Moderate (C3-2) / Low (C1-F3)". One finding should carry one severity with the differing reviewer ratings noted, not two.

### M7 (minor): the F3 fix (c) is under-specified

"Normalized __import__('X').Y( forms" requires a normalization step the code does not have: _SINKS is a plain substring list checked with `any(_s in code for _s in _SINKS)` (launch_y13.py:569-572), and no normalization happens before that check. The os.exec and spawn families are also not enumerated, and enumeration matters: the substring "os.execv(" does not match "os.execve(", and "os.spawnl(" does not match "os.spawnle(". The fix direction is right; the exact list and the normalization point are missing.

### M8 (trivial): the wrapper list prose omits zsh and dash

The adjudication's F3 wrapper list names "bash/sh -c", but the code handles bash, sh, zsh, and dash (launch_y13.py:706-855, shell branch). The finding is unaffected.

### M9 (minor): the C1-F1/C3-3 fix adds --repo on an unverified basis

The adjudication instructs adding --repo to the runner docstring lines "matching the launcher docstring and SHIPPED.md (the laptop checkout path already documented there)". Council 3 itself records that whether that path is the real laptop checkout is not verifiable from this VM. The -P addition is the real fix and is correct; the --repo addition rests on an unverified path claim the adjudication does not flag.

### M10 (trivial): the harness-lesson wording is imprecise

The adjudication says "the round-2 attack harnesses under /tmp were lost before round-2 review closed". The fix log (commit ab0b62c, HARNESS LOSS entry) records the Y13r2 harnesses in /tmp/y13r2/ and /tmp/y13r2-redteam/ as gone at 23:58 on 21/11, during round-2 work; the round-2 review harnesses themselves live under ~/workspace (redteam, council 2, council 3, verifier). The lesson itself (stage harnesses under ~/workspace, never /tmp-only) is the fix log's own lesson and is correct; only the attribution is imprecise.

## What survives (checked correct, not attacked)

- Pins: runner md5 d5047ff573820491263a2eb3805105f4, launcher 8e72a5ce85cbaf8382f998987e8890e5, manifest 7c76383402e4c50b28adab6b25a22e09 with 27 entries, run_live manifest entry 84fa106c253d5e7f16daccf2ce3f14a5, pin 1e3901c verified (git show 1e3901c run_live.py md5 is 84fa106c253d5e7f16daccf2ce3f14a5). _SHIP_FILES is 29 paths in both files.
- F1: the dead-code proof is correct. launch_y13.py:1197 reads `if (not rel_root and _is_entry_pyc_rel(rel)):`; _is_entry_pyc_rel at :295-300 requires the __pycache__/ prefix; the module-top scan exemption at :354-355 works on _is_entry_pyc_rel alone; main() order at :1472-1477 puts check_manifest before _check_entry_pyc.
- F2: the channel is real. The strings PYTHONPATH, PYTHONHOME, and PYTHONSTARTUP occur zero times in either entry-point file; the launcher exec env at :1484-1500 passes os.environ through with only PYTHONSAFEPATH added; the comment at :1495-1497 claims -P keeps a planted stdlib .py from executing; the fresh-compile subprocess at :1289 runs with no env argument. The runner docstring carries the same false claim (run_codex_y5.py:109-111).
- F3: the tokenizer evidence is correct. After `--` the parser falls through to _token_is_runner_script (launch_y13.py:620-691, :534-543), which returns False for `-`; _m_module_is_runner at :586-600 special-cases pdb only; _is_timeout_dur at :697-705 rejects `0x10`; _SINKS at :569-572 lacks the named methods; the wrapper list covers env, nohup, setsid, exec, command, timeout, flock, bash/sh/zsh/dash -c, nice, stdbuf, taskset, sudo, uv.
- F4: the git log call at :1120-1121 uses --topo-order with no --first-parent; redteam cases 10 and 11 are as quoted.
- F5: the mechanism is co_filename only, as all three reviewers independently found. The comparison is at :1302 and the fresh compile uses the absolute SHIP_DIR path at :1285-1287.
- Verifier defect 2: _check_entry_pyc uses plain os.listdir plus os.unlink with no realpath check, unlike _entry_pyc_paths at :190-213.
- Decision-table coverage: every finding from all five reviews appears (redteam F1-F7, verifier defects 1-2, council 1 F1-F8, council 2 C2-1 to C2-10, council 3 C3-1 to C3-8). Disagreement resolutions 1 and 2 are correct: council 1's "launcher scan + check_manifest exempt top-level entry .pyc" is wrong on the check_manifest half, and council 2's C2-4 "R4 FIXED" holds only for the guard helper, not for _check_entry_pyc.
- Arithmetic: verifier 277/280 is 3 failures from 2 root causes, both in _check_entry_pyc, as the adjudication states.
- Fix-log Design C: the adjudication's characterization is correct. The fix log (commit ab0b62c) says the blind entry-.pyc exemption was REMOVED from the scan and from _verify_manifest, while the implemented code instead adds the broken exemption attempt at launch_y13.py:1197.

## Corrected fixes for round 3

1. F5: use ONLY the compile-with-cached-filename option. Delete option (a) (code.replace on either or both sides) from the work order; it provably fails for modules with nested defs and is fragile on Python 3.12.3. Re-test with relative-path py_compile for all 3 stems plus the absolute-path control and the forged refusal.
2. F3(b): thread the following argv through to _c_code_executes_runner for the argv half. For the env half, either add a new /proc/PID/environ reader to check_runner_quiet (new capability, permission and robustness to be verified) or record argv/env smuggling as a documented limit alongside string concatenation. Do not state that check_runner_quiet can already read environ.
3. Line numbers: use the corrected ranges in the B3 table above.
4. F4: state the precondition that markers must land as first-parent commits, verify no marker commit is merge-introduced before switching to --first-parent, and document that a merge-introduced marker would be ignored.
5. F2: state the startup residual (PYTHONHOME and sitecustomize fire before any in-process check) as a documented limit; keep the child-env scrub and the module-top PYTHONPATH refusal.
6. Round-3 re-verification must also cover the corrected F5 fix, the new environ reader if added, and the 14-function AST check with the committed extractor updated to list all 14 functions.

## Limits of this redteam

- I did not re-run any reviewer battery or any live run. Live numbers cited are the reviewers' numbers; my first-hand verification is the code reading and the stdlib marshal probes described above.
- I did not re-review round 1. Severity judgments (notably M3) are mine; BLOCK stands on F1 regardless of the F2 severity debate.
- The verdict BROKEN is about the adjudication document as a round-3 work order. It does not overturn the adjudication's headline outcome: F1 and F2 are upheld on the facts, and no live run may proceed until round 3 lands and is independently re-verified.
