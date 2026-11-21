# Redteam: Y13r2 re-review of the Y13f fix diff (BLOCK)

- Reviewer: Worker Y13r2 redteam (independent Muse reviewer)
- Date: 2026-11-21, work 22:02 to 22:45 +07
- Repo: ~/workspace/computer-use-wayland, branch todolist-push
- Commit under review: fix diff 118c67f + 3fa389a + 431b2a9 (range cb26d1d..431b2a9 also holds other workers' commits; only the Y13f files were attacked)
- Scope: ONLY the Y13f fix (tests/realistic/run_codex_y5.py, tests/realistic/launch_y13.py, tests/realistic/regen_codex_y5_manifest.py, manifest, SHIPPED.md, plan). No repo code was modified by this review. No live driving. No commits.
- Method: every claim below was reproduced live in temp ship copies under /tmp/y13r2-redteam/ (staged from committed bytes: runner md5 3cc5fa11, launcher md5 2b02c5ec, run_live md5 84fa106c pin 1e3901c, manifest md5 f27c0302, 27 files, clean ship --verify-manifest exit 0). Attack scripts are the redteam scratch in /tmp/y13r2-redteam/ (attack_a123.py, attack_a4_unit.py, attack_a4_live.py, attack_a5.py, attack_a6.py, attack_a6e.py, attack_a7.py, attack_a8.py, forge_pyc.py). The real /tmp/worker-y13-server ship was only read, never written. The real handover token was never touched.
- Verdict: BLOCK. Do not drive live until the four blockers below are fixed and re-verified mechanically.

## Verdict summary

The Y13f fix closes the exact H1 forge it was asked to close (A1 passes on all three forms), holds the manifest and symlink layers (A6a/b/c, A7 pass), and holds the wall-cap and _proven_no_body fixes (A8 passes 10/10 plus the step and gate proofs). But the fix reopens the same ship-integrity class through two new routes, leaves the H2 tokenizer blind to the standard module form plus five more live forms, and bricks its own ship on a single -m invocation. Three of the four blockers strike the load-bearing ship-integrity gate itself (B1 makes --verify-manifest lie; B2 executes attacker code on the production launch path before any gate runs; B4 bricks verify and the live run). B3 leaves the queue process check blind to real rival launches, including the standard `python3 -m` form.

- BLOCKER 1 (A2): forged ENTRY .pyc executes via -m and import; a fake-OK forge makes --verify-manifest print manifest_ok true, exit 0.
- BLOCKER 2 (A6d): planted stdlib .py files execute at import, before the pre-import scan, on the production launch path (9 of 15 names tested).
- BLOCKER 3 (A4): tokenizer misses -m forms (Finding 2, confirmed live) plus flag-with-value forms, renamed/extensionless/symlinked copies, and -c exec forms.
- BLOCKER 4 (A3, Finding 1): -m on a clean ship bricks verify and the live run until manual deletion; no auto-unbrick.
- AMEND 1 (A5): no remote-URL pinning; marker is subject/path/freshness only (subject spoof and old-date spoof pass by design).
- AMEND 2 (A4 FP): -c splitting false-positives on mere mentions; "codex" substring warning fires on any cmdline containing run_codex_y5.
- AMEND 3 (A7 nit): scan JSON key "pyc_refused" mislabels symlink refusals.
- AMEND 4: SHIP_DIR is hardcoded to /tmp/worker-y13-server; the launcher cannot verify a ship at any other path.
- AMEND 5 (A8 edge, informational): eval_error "" is falsy; unreachable per run_live today.

## Judgment on the re-reviewer's Finding 1 and Finding 2

- Finding 1 (CONFIRMED, with my own reproduction): `python3 -m run_codex_y5 --verify-manifest` on a clean staged ship fails exit 2 with `{"manifest_ok": false, "files_checked": 27, "mismatches": ["unexpected directory in ship dir: __pycache__"]}`. The -m form writes exactly `__pycache__/run_codex_y5.cpython-312.pyc` during get_code, before dont_write_bytecode is set. The scan exempts that file, but _verify_manifest refuses the __pycache__ directory itself (it is not a prefix of any manifest path), so the two layers disagree. Once the file exists, the direct form also fails rc 2, and a live-run attempt on the bricked ship fails with `MANIFEST FAILED: ['unexpected directory in ship dir: __pycache__']`, rc 2, before any driving (main() calls _verify_manifest first). Manual `rm -rf __pycache__` unbricks it (rc 0). An empty __pycache__ dir alone also bricks it. `PYTHONDONTWRITEBYTECODE=1 python3 -m ...` passes rc 0 with no cache written. This is a denial-of-service on the ship, not just a probe artifact: the trigger is any -m invocation or bare import without the env var, which the team's own probe habits produce (the Y13f log records the cache being recreated twice by probes). The launcher does not delete it and does not unbrick it; only regen --stage does, manually. Fail-closed (no unsafe run), but it blocks the launch path.
- Finding 2 (CONFIRMED, and extended): the tokenizer returns False for `python3 -m run_codex_y5` and `python3 -m run_live` in both copies (unit table), and live dummy processes in those forms pass the real launcher check_runner_quiet (CHECK-PASS). Five more live evasion forms were found (A4). See B3.

## Per-attack results

Notation: PASS means the fix holds (attack fails); FAIL means the attack succeeds (fix broken).

### A1. H1 forge, top level, nested, -m form: PASS (fix holds)

Forge script: build a .pyc from the real run_live.py source plus a marker print, header mtime/size from the real source stat (16-byte header: magic + flags 0 + mtime + size).

Commands (each on a fresh staged ship copy):
- `python3 forge_pyc.py run_live.py "A1 run_live forged" __pycache__/run_live.cpython-312.pyc`
- `python3 run_codex_y5.py --verify-manifest`
- nested: same forge into `codex-y5/__pycache__/run_live.cpython-312.pyc`
- -m form: same forge top-level, then `python3 -m run_codex_y5 --verify-manifest`

Outputs (all three): `{"pyc_refused": true, "files": ["__pycache__/run_live.cpython-312.pyc"], "manifest_ok": false}`, rc 2, marker never printed. Nested: same with `codex-y5/__pycache__/run_live.cpython-312.pyc`. The H1 fix holds for non-entry .pyc files.

### A2. H1 exemption abuse (entry .pyc): FAIL (attack succeeds)

Forge the ENTRY .pyc the same way (real run_codex_y5.py source plus a marker print, header from the real source stat), stage at `__pycache__/run_codex_y5.cpython-312.pyc`.

Commands and outputs:
- `python3 -m run_codex_y5 --verify-manifest` (forged entry .pyc present): stdout line 1 `POISON-MARKER: A2 entry run_codex_y5 forged`, line 2 `{"manifest_ok": false, ... "mismatches": ["unexpected directory in ship dir: __pycache__"]}`, rc 2. Marker printed: attacker code executed; the verify refusal came too late.
- `python3 -c "import run_codex_y5"` (same ship): `POISON-MARKER: A2 entry run_codex_y5 forged`, rc 0. A bare import executes the forged entry bytecode and exits clean.
- `python3 -m launch_y13 --help` (forged `__pycache__/launch_y13.cpython-312.pyc`): marker printed, then the launcher's normal REFUSED (no Y13_GO). Same hole for the launcher entry point. Import form: marker printed, rc 0.
- A2b, fake-OK forge (entry .pyc whose code prints a clean verify JSON and exits 0, header forged from the real source stat): `python3 -m run_codex_y5 --verify-manifest` prints `POISON-MARKER: A2b fake verify gate` then `{"manifest_ok": true, "files_checked": 27, "mismatches": [], "manifest_md5": "f27c03020c9866cfa0dcd637df6f8647"}`, rc 0. The integrity gate itself is spoofable through the exemption.
- Controls: direct script form `python3 run_codex_y5.py --verify-manifest` with the forged entry .pyc: rc 2, no marker (script __main__ never loads the cache). Wrong-tag forge (`run_codex_y5.cpython-311.pyc`): refused by the scan, no marker. Sourceless-name forge (`run_codex_y5.pyc` next to the .py): refused by the scan, no marker.

Root cause: the exemption's comment claims the two entry .pyc files "cannot execute in production: both entry points run as __main__, never from .pyc". That is false. `python3 -m run_codex_y5` loads __main__ from the cache, and any import loads the module from the cache. The scan exempts exactly the path the loader trusts, and the scan itself is part of the forged bytecode, so it cannot protect itself. Blast radius: probe/-m/import paths (the verify gate can be made to lie); the launcher-driven production path (script form plus PYTHONDONTWRITEBYTECODE=1) does not load the entry .pyc. See Blocker 1.

### A3. Finding 1 brick: CONFIRMED (see judgment above)

Commands on a fresh clean staged ship: `python3 -m run_codex_y5 --verify-manifest` (no env var) gives rc 2 with `unexpected directory in ship dir: __pycache__`, and leaves exactly `__pycache__/run_codex_y5.cpython-312.pyc` behind. Direct form after: rc 2, same mismatch. Live-run attempt `python3 run_codex_y5.py all` on the bricked ship: `MANIFEST FAILED: ['unexpected directory in ship dir: __pycache__']`, rc 2, no driving. After manual `rm -rf __pycache__`: direct form rc 0. Empty __pycache__ dir alone: rc 2. Env-guarded -m: rc 0, no cache written. See Blocker 4.

### A4. H2 tokenizer evasion: FAIL (attack succeeds; Finding 2 confirmed plus more)

Unit table: real `_is_runner_cmdline` from both copies (AST-verified logic-identical, CODEX_REFUSE_MARKERS identical), 39 raw NUL-separated cmdlines. Live probe: real dummy sleep processes plus the real launcher `check_runner_quiet` (imported from the staged ship), one case at a time, all dummies killed after.

Unit results (25 CAUGHT, 14 EVADE):
- Real evasions (12): `python3 -m run_codex_y5`, `python3 -m run_live`, `python3 -m pkg.run_codex_y5`, `python3 -m run_codex_y5 --verify-manifest`, `python3 -W ignore run_codex_y5.py`, `python3 -X dev run_codex_y5.py`, `python3 -X faulthandler run_codex_y5.py`, `python3 --check-hash-based-pycs always run_codex_y5.py`, `python3 -c "exec(open('run_codex_y5.py').read())"`, `python3 run_codex_y5` (no .py extension), renamed copy `python3 /tmp/mycopy.py`, symlink under another name `python3 /tmp/link.py`.
- Correct passes (2): `md5sum /abs/run_codex_y5.py` (False, correct); `python3 -c "import run_codex_y5"` (False, correct: an import is not a live run).
- False positives (2, CAUGHT): `bash -c "echo python3 run_codex_y5.py"` and `bash -c "grep python3 run_codex_y5.py file.txt"` both return True. The -c splitting treats every word of the -c string as a command, so a mere mention of the words `python3 <runner>` trips the gate.
- Holds (22 real catches): bare-relative, absolute, -u, env VAR=1, nohup, setsid, /usr/bin/python3, ./, ../, python3.12, python, run-nested-pill.py, bash run-nested-wayland.sh, sh -c, bash -c exec, flock -c, flock direct, timeout, run_live.py, hand_drive_e1.py, shebang ./, -I. (`python3 -m run_codex_y5.py` returns True but that form is invalid Python and never runs.)

Live results (20 cases, baseline first: CHECK-PASS with no dummies):
- Caught live (refused rc 2): bare-relative runner, absolute runner, Y6c pill bare-relative, Y6c pill absolute, bash run-nested-wayland.sh (with shell content; my first attempt used Python content in the .sh file and the dummy died, re-ran correctly), flock -c, sh -c, nohup, codex + geckodriver.
- Evade live (CHECK-PASS): `python3 -m run_codex_y5`, `python3 -m run_live`, `python3 -W ignore run_codex_y5.py`, `python3 -X dev run_codex_y5.py`, renamed copy, symlink other name, extensionless copy.
- Pass correctly: plain codex (WARNING only, CHECK-PASS), md5sum mention (CHECK-PASS).
- False positive live: `bash -c "echo python3 run_codex_y5.py && read x"` (bash stays bash, never executes the runner) is REFUSED rc 2 as a live runner. Note: a `bash -c "... && sleep 60"` variant exec-replaces itself with sleep, so the FP needs a bash that stays bash; the read-x form proves it live.

Two observations from the live run:
- Any cmdline containing the substring "codex" gets a `WARNING: codex process running` line, including a process whose cmdline merely mentions the runner filename run_codex_y5 (the filename contains "codex"). Warn-only, but the label is wrong and the noise hides real codex hits. The -m, -W, -X, and extensionless evasions all carried this misleading warning while passing.
- During the Y6c pill absolute case, the refusal also listed a concurrent sibling worker's probe process running `python3 run_codex_y5.py --verify-manifest` as an offender. A verify probe counts as "runner process running" for the gate, so concurrent fleet probes trip the launch gate (fail-closed, but a coordination footgun).

Root cause: `_script_basename_is_runner` requires a `run_*.py` suffix, so -m module names (no .py) never match; the python-token rule requires the runner token to follow a python token or a dash flag, so flag-with-value forms (`-W ignore`, `-X dev`, `--check-hash-based-pycs always`) miss because the value token sits between the flag and the script; name matching cannot see renamed/extensionless/symlinked copies at all. See Blocker 3.

### A5. H3 marker spoofing: MIXED (spoof succeeds by design; branch and ordering hold)

Synthetic bare remote plus clone (own test remote, not the real repo), real `check_marker` and `check_manifest` from the staged launcher. Committer/author dates set explicitly per case.

- Case 1, fake completion: subject exactly `Y6c nested run DONE`, touching improvements/worker-y6c-*.md, body and diff unrelated ("weekly notes", junk line). Result: MARKER-PASS. The gate checks subject, path, and freshness only, never diff/body content or authorship. Spoof succeeds.
- Case 2, marker on a different branch only: REFUSED rc 2 (no marker on todolist-push). Holds.
- Case 3, forged old commit date (committer date 2020-01-01, same subject): MARKER-PASS. There is no recency-vs-now check; freshness is only relative to the newest abort.
- Case 4, marker commit never pushed (local branch only): REFUSED rc 2. Holds.
- Case 5, --repo at a non-git path: REFUSED rc 2. Holds.
- Case 6, attacker-controlled repo end to end: a separate bare remote plus clone whose origin is a local path (not the real origin), holding a fake marker commit and a manifest byte-identical to the clean ship's. Result: check_marker MARKER-PASS and check_manifest MANIFEST-PASS. The launcher never checks the remote URL (no get-url or remote validation anywhere in launch_y13.py). Pointing --repo at any clone that serves a matching marker and an identical manifest passes both git gates.
- Controls, all correct: harness subject refuses; body-DONE under subject `Fix flake` refuses; abort newer than completion refuses; completion newer than abort passes; marker touching a different path (worker-y6d-*.md) refuses.

Judgment: cases 1 and 3 succeed by design of a subject-based marker check. The H3 fix spec never asked for content, authorship, or recency-vs-now checks, and the H3 false-accepts it did target (harness wording, body lines, stale markers) are all fixed and verified by the controls. A subject spoof needs push access to todolist-push (or control of the --repo path), which is outside the stated coordination threat model. Case 6 is the actionable gap: --repo is trusted blindly. See Amend 1.

### A6. Manifest tampering and stdlib shadowing: MIXED (manifest layer holds; shadowing FAILS)

- A6a, one fixture byte changed, manifest kept: `python3 run_codex_y5.py --verify-manifest` gives rc 2 with `codex-y5/fixtures/test-01-git-workflow.html: want ac0f3f5f..., got b7a7b9c5...`. Caught by _verify_manifest. PASS.
- A6b, fixture changed AND manifest entry edited to match: runner --verify-manifest gives rc 0, manifest_ok true, manifest md5 1ec56ec4 (self-consistent, as designed). The launcher's check_manifest against the real repo then REFUSES rc 2: `ship manifest md5 1ec56ec47b336ef1c75653c42b66efb3 != committed manifest md5 f27c03020c9866cfa0dcd637df6f8647`. Layering holds: the runner alone cannot catch a self-consistent edit; the git comparison does. PASS, with one harness note: SHIP_DIR is hardcoded to /tmp/worker-y13-server in launch_y13.py line 71, so a probe must redirect the `SHIP_DIR` global to test a ship elsewhere (my first attempt read the real staged ship instead of the tampered copy and passed spuriously; the corrected run with SHIP_DIR redirected refuses as above). See Amend 4.
- A6c, planted top-level live_metrics.py with a marker print: rc 2 `unexpected file in ship dir: live_metrics.py`, marker never printed (nothing imports it). PASS.
- A6d, planted stdlib .py shadowing: FAIL (attack succeeds). Each planted file prints a marker, then delegates to the real stdlib module so the run can continue. Results after the environment was repaired (see the incident note; the first map run was confounded by the broken `re` and is superseded by this one): marker printed, code executed at import before any gate, for enum, re, json, socket, subprocess, hashlib, datetime, pathlib, copyreg (9 of 15). Marker not printed for functools, collections, os, warnings (pre-loaded at interpreter startup, so never re-resolved from the ship dir), typing, sre_compile (not imported during the runner's import chain). Every case then refuses rc 2 (either `unexpected file` or the scan tripping on the self-written .pyc), but the code already ran, so the refusal is too late. The runner's own top-level imports (base64, glob, hashlib, json, os, re, socket, subprocess, sys, time, urllib.request, datetime, pathlib) execute before the scan code, and sys.path[0] is the ship dir from process start, so any stdlib module imported there that is not already in sys.modules resolves from the ship dir. The launcher entry point is equally exposed (its top imports include re; a planted re.py executes during the launcher's own import, before check_manifest). This fires on the production launch path (launcher execs the runner as a script), not only on probes. See Blocker 2.
- A6e, self-deleting shim: NOT completed as designed. The re.py variant printed its marker, then the scan refused on the self-written `__pycache__/re.cpython-312.pyc`: the bytecode cache is written at get_code time, before the shim runs, so setting dont_write_bytecode inside the shim is too late. Full self-erasure (marker printed plus clean verify) was not achieved by that construction. The experiment was STOPPED after the shim's `os.remove(__file__)` deleted the wrong file (see the incident note). The A6d result (code executes before any gate) stands on its own and does not need the self-deleting variant.

### A7. Symlink attacks: PASS (fix holds at both layers)

Five cases, each run unstripped (scan layer) and stripped (scan call removed in the temp copy only, staged manifest re-pointed at the stripped runner so the runner md5 is not a second refusal; stripped-copy sanity is a clean verify rc 0):
- Symlinked fixtures dir (correct content): scan refuses rc 2 `{"pyc_refused": true, "files": ["codex-y5/fixtures (symlink)"]}`; _verify_manifest refuses rc 2 `manifest path escapes ship dir: codex-y5/fixtures/test-01-git-workflow.html`.
- Symlinked manifest file (correct content): scan refuses; _verify_manifest refuses `manifest path escapes ship dir: codex-y5/test-01-git-workflow.md`.
- Symlinked codex-y5 dir itself: scan refuses; _verify_manifest refuses via path containment.
- Symlinked fixture file to an outside tampered target: scan refuses; _verify_manifest refuses via path containment.
- Symlinked non-manifest dir (codex-y5/extras to an outside dir): scan refuses; _verify_manifest refuses `symlink in ship dir: codex-y5/extras` (the os.walk islink check; this is the case the path-containment check cannot catch because no manifest entry resolves through it).
All rc 2, marker never printed. The Y13r L5 blind spot is closed. Nit: the scan prints `"pyc_refused": true` even when the found item is a symlink, which mislabels the refusal. See Amend 3.

### A8. Wall-cap / M2: PASS (fix holds)

Unit calls with the real functions imported from the staged ship (PYTHONDONTWRITEBYTECODE=1):
- _proven_no_body, 10/10: eval_error plus good snapshot returns False (the M2 redteam proof); eval_error "" or None plus good snapshot returns True; no eval_error plus good snapshot True; hasBody key missing False; hasBody None False; no snapshots False; eval_error plus no snapshots False; contradictory snapshots False; not complete False.
- Wall-cap trip: Y13Runner("01", ...) with t0 400 s in the past raises WallCapExceeded `wall cap exceeded: 400s > 360s at primitive '99 cap trip'`; with t0 now, no raise.
- step() re-raise by type: WallCapExceeded, InfraError, and FixtureUnavailableError propagate unwrapped; a plain RuntimeError mentioning "INFRA:" stays wrapped as `step failed: ...`. L1 holds.
- Re-run gate (code read): the only re-run path is main() line 4411 `if outcome == "infra-blocked" and attempt == 1:`; the WallCapExceeded branch at line 4188 sets outcome "failed" at line 4196 and never sets raised_infra, so a wall-cap trip cannot re-run. M1 holds.
- Edge noted: eval_error "" (empty string) is falsy, so _proven_no_body would return True for it. Run_live sets eval_error only to non-empty strings (lines 316, 323, 331, 335, 346, 352) or omits the key, so "" is unreachable in practice. See Amend 5 (informational, no action unless the diagnose contract changes).

## Incident note: my probe deleted a stdlib file, fleet repaired it

During A6e, my self-deleting shim had a bug: `globals().update(vars(_real))` overwrote the shim's own `__file__` with the real module's `__file__` before `os.remove(__file__)` ran, so it deleted /usr/lib/python3.12/re/__init__.py (the real CPython 3.12.3 re package init; there never was a single re.py file in 3.12.3) instead of the planted temp file. This broke `import re` VM-wide from about 22:25 to 22:31 +07 (SSH to the laptop broke in that window, and other fleet work was affected). The fleet's VMFIX restored re/__init__.py from CPython 3.12.3 at 22:31:12 and verified re_ok plus SSH_OK at 22:33. I verified myself after the repair: `import re` works (file /usr/lib/python3.12/re/__init__.py, compile and match work), stdlib imports work, and the clean ship verifies rc 0. The json.py and collections.py "missing" alarms during the incident were false alarms on my part (json and collections are packages, not single files; both work). The only file my shim deleted was re/__init__.py, now restored. The A6e self-deleting experiment was stopped at that point and not re-run. My earlier A6map run (before the repair) is confounded for the modules that died at `import glob` while re was broken; the A6map2 re-run above, after the repair, supersedes it.

## Blockers (fix before any live driving)

### BLOCKER 1: entry-point .pyc exemption lets forged entry bytecode execute (A2)

- Files: tests/realistic/run_codex_y5.py lines 149-181 (_ENTRY_PYC, _refuse_tampered_ship), lines 508-511 (entry_pyc_rel in _verify_manifest); tests/realistic/launch_y13.py (same exemption shape for its own entry .pyc).
- Precise fix: (1) Remove the exemption from the scan: any .pyc under the ship dir refuses, including the two entry paths. (2) In _verify_manifest, exempt the __pycache__ directory ONLY when it contains exactly the two entry .pyc files and nothing else (this keeps the legitimate self-pyc from bricking verify; see Blocker 4). (3) Enforce script-form-only invocation: both entry points refuse at the very top when loaded as a module or via -m (__spec__ is not None) with a clear "run as a script, not -m" error, and the launcher plus SHIPPED.md plus the regen script document script form only. (4) Out-of-process check in the launcher before exec: when an entry .pyc exists, compile the matching entry .py source fresh and compare the marshalled code object against the cached .pyc; refuse on any mismatch, then delete only the two entry .pyc paths before exec. An in-process check cannot be trusted here because a forged entry .pyc IS the running code.
- Re-test: re-run the A2 forge (entry .pyc, -m form, import form, fake-OK forge) and require no marker printed and no fake-OK pass; re-run A1 (non-entry forge still refuses); re-run the clean ship verify rc 0.

### BLOCKER 2: planted stdlib .py executes at import, before the scan (A6d)

- Files: tests/realistic/run_codex_y5.py lines 111-181 (top-level imports run before the scan); tests/realistic/launch_y13.py (same shape: top imports before any check).
- Precise fix: (1) Run both entry points with PYTHONSAFEPATH=1 (`python3 -P`): the ship dir must never be on sys.path for the entry point's own imports. The launcher sets PYTHONSAFEPATH=1 in the exec env (it already sets PYTHONDONTWRITEBYTECODE=1; add this next to it) and invokes the runner as `python3 -P run_codex_y5.py`. The runner inserts the ship dir into sys.path itself only after the scan passes (it already does this for the run_live import). (2) Defense in depth: move the pre-import scan to the very top of run_codex_y5.py, before any import except sys and os (both safe: sys is builtin, os is pre-loaded at startup), using only os.path (never pathlib, never json) for the scan and its refusal output. Set sys.dont_write_bytecode there, before the remaining imports. Apply the same bootstrap shape to launch_y13.py (scan the ship dir for .pyc/symlink/planted .py before its json/re imports, or verify the ship from the launcher with PYTHONSAFEPATH set). (3) The launcher's check_manifest must also refuse a planted file, not only a changed manifest md5: list the ship dir and refuse any top-level .py, any .pyc, and any symlink not in the manifest (an added file leaves the manifest md5 unchanged, so the md5 comparison alone cannot see it).
- Re-test: re-run the A6d map (all 15 stdlib names, simple delegating shim) with the fixed bytes and require the marker never printed for any name; re-run A6c (planted live_metrics.py still refuses); re-run the clean ship verify rc 0 and a launcher dry run.

### BLOCKER 3: tokenizer misses real rival launch forms (A4, Finding 2)

- Files: tests/realistic/run_codex_y5.py line 3575 and tests/realistic/launch_y13.py line 98 (`_script_basename_is_runner`), plus `_is_runner_cmdline` in both (AST-verified identical logic).
- Precise fix: (1) -m forms: when a "-m" token is followed by a module token, match if the module's last dotted segment is a runner module name (run_codex_y5, run_live; run-nested names cannot be -m targets because hyphens are not valid in module names, so keep the run-nested* basename rule for direct forms). (2) Flag-with-value forms: once a python token has been seen in the argv, treat ANY later token whose basename is a runner script as a match, regardless of intervening flags or flag values (this catches -W, -X, --check-hash-based-pycs, and any future value-taking flag). (3) -c strings: parse the -c string as a shell command line and only consider its FIRST word (plus the words that follow a python token in that same command); a runner name appearing as an argument to a non-python command (echo, grep) must not match. (4) Renamed/extensionless/symlinked copies: resolve the script token to its real path and compare the file's md5 against the known runner md5s from the manifest (name-independent); document that name matching alone cannot see a renamed copy, and keep the ports plus flock backstop. Apply the identical fix in both copies and re-verify with the AST comparison.
- Re-test: re-run the A4 unit table (all 39 cases) and require every real execution form CAUGHT (including all -m forms, flag-value forms, renamed/extensionless/symlinked copies, -c exec) and every mere mention NOT caught (md5sum, echo, grep); re-run the A4 live probe with real dummies for the same set.

### BLOCKER 4: -m bricks verify and the live run until manual deletion (A3, Finding 1)

- Files: tests/realistic/run_codex_y5.py lines 149-181 (scan exempts the entry .pyc) and line 528 (`unexpected directory in ship dir: __pycache__` in _verify_manifest).
- Precise fix: (1) Same as Blocker 1 item (2): _verify_manifest exempts the __pycache__ directory iff it contains exactly the two entry .pyc files and nothing else. (2) The launcher deletes ONLY the two entry .pyc paths (never the whole __pycache__, never any other .pyc) before exec, so a self-created entry cache cannot brick a launch; a forged run_live .pyc or any other .pyc still refuses via the scan. (3) Add the -m guard from Blocker 1 item (3) so a -m invocation fails fast with a clear "use script form" message instead of a confusing manifest failure. (4) Record in SHIPPED.md that -m and bare imports without PYTHONDONTWRITEBYTECODE=1 are unsupported invocation forms.
- Re-test: re-run A3 end to end (clean ship -m, direct form after, live-run attempt, empty __pycache__ dir, env-guarded -m) and require verify rc 0 and no brick in every case except a forged non-entry .pyc, which must still refuse rc 2 with no marker.

## AMEND items

### AMEND 1: pin the remote URL; document the marker as a coordination signal (A5)

- Files: tests/realistic/launch_y13.py check_marker (line 264) and check_manifest (line 327).
- Precise fix: (1) In check_marker and check_manifest, after `git fetch origin`, read `git remote get-url origin` and refuse unless it equals the known repo remote (the same URL the repo was cloned from; store it as a constant next to SHIP_DIR, never accept a --repo whose origin differs). (2) Document in the launcher docstring and SHIPPED.md that the Y6c marker is a coordination signal, not authentication: it checks subject, path, and freshness-vs-abort only, and a subject spoof or an old-date marker passes by design when the pusher has push access. If a content check is wanted later, require the marker commit's diff to add a real run-log file under improvements/worker-y6c-*.md containing a verdict token; do not add that check in this fix.
- Re-test: re-run the A5 suite; case 6 (attacker repo) must now refuse on the remote URL, cases 1 and 3 must still pass (documented limitation), controls C1-C5 unchanged.

### AMEND 2: -c mention false positive; "codex" substring warning noise (A4)

- Files: `_argv_tokens` / `_is_runner_cmdline` and `check_runner_quiet` in both files.
- Precise fix: same as Blocker 3 item (3) for the -c false positive (first-word semantics). For the warning: match "codex" as a path component or argv[0] basename (a process actually named codex), not as a raw substring, so a cmdline that merely mentions run_codex_y5.py does not warn. Keep the refuse markers unchanged.
- Re-test: the A4 FP cases (bash -c echo/grep) must pass the check; a real codex process must still warn; codex plus geckodriver must still refuse.

### AMEND 3: scan JSON key mislabels symlink refusals (A7)

- File: tests/realistic/run_codex_y5.py line 175.
- Precise fix: report the refusal kind honestly, e.g. `{"refused": true, "kind": "symlink", "files": [...]}` (or separate keys for pyc vs symlink), instead of `"pyc_refused": true` for every refusal. Update any parser that keys on pyc_refused.
- Re-test: re-run A7; the symlink cases must refuse with the corrected kind label.

### AMEND 4: SHIP_DIR is hardcoded (A6b harness note)

- File: tests/realistic/launch_y13.py line 71 (`SHIP_DIR = "/tmp/worker-y13-server"`).
- Precise fix: derive SHIP_DIR from the launcher file location (dirname of __file__) with the hardcoded path as an explicit fallback only when the file location is not a ship dir, or accept a --ship-dir flag. Until then, document that the launcher only ever checks /tmp/worker-y13-server and that probes must redirect the SHIP_DIR global to test another ship.
- Re-test: run check_manifest against a tampered ship staged at a temp path and require refusal without touching the real ship path.

### AMEND 5: eval_error "" edge (A8, informational)

- File: tests/realistic/run_codex_y5.py `_proven_no_body`.
- Note: `diag.get("eval_error")` is falsy for "", so an empty-string eval_error would read as a proven no-body fixture. Run_live only ever sets eval_error to a non-empty string or omits the key, so this is unreachable today. No code change required; if the diagnose contract ever changes to allow "", change the check to `diag.get("eval_error") is not None`.

## Confirmed holds (what the fix got right, verified live)

- A1 forged run_live .pyc (top, nested, -m): refused rc 2, no marker.
- H2 bare-relative, absolute, -u, env, nohup, setsid, /usr/bin/python3, ./, ../, python3.12, python, flock -c/direct, sh -c, timeout, run_live.py, hand_drive_e1.py, shebang, -I: all caught live.
- H3 harness subject, body-DONE, abort-newer, wrong-path, other-branch, unpushed, non-git --repo: all refuse; completion-newer-than-abort passes.
- Y6c process names: run-nested-pill.py bare and absolute caught live; bash run-nested-wayland.sh caught live.
- Codex rule: codex plus geckodriver refuses live; plain codex warns and passes live.
- Manifest: fixture tamper caught by md5; self-consistent manifest edit caught by the launcher git comparison; planted live_metrics.py refused and never executed.
- Symlinks: all five shapes refused at both layers.
- Wall-cap: trip raises WallCapExceeded, never re-runs (gate line 4411, outcome failed line 4196).
- _proven_no_body: 10/10 including the M2 proof and hasBody None/missing.
- step(): marker-class re-raise by type; plain RuntimeError mentioning INFRA: stays wrapped.
- Tokenizer and codex markers are logic-identical in the runner and launcher copies (AST comparison).

## Required re-review

After the four blockers and the five amends land, a fresh re-review of the FIX DIFF only is required (same scope rule as Y13r): re-run the A2 forge set, the A6d stdlib map, the A4 unit table plus live probe, the A3 brick sequence, the A5 suite with the remote-URL pin, and the A7/A8 sets. Do not drive live before that re-review lands.
