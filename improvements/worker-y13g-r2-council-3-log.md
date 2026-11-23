# Council 3 round-2 log (operator view)

- Reviewer: Council 3, Muse subagent
- Start: 2026-11-22 00:59 +07 (Asia/Ho_Chi_Minh)
- Repo: ~/workspace/computer-use-wayland, branch todolist-push
- Round-2 diff: 0639d04, 87eec47, 6ba43f2, 8bdd5aa, 5a9b9e8
- Pins at start: runner d5047ff573820491263a2eb3805105f4, launcher 8e72a5ce85cbaf8382f998987e8890e5, run_live 84fa106c253d5e7f16daccf2ce3f14a5, manifest 7c76383402e4c50b28adab6b25a22e09, 27 files. All match the brief.
- Scratch: ~/workspace/y13g-r2-council-3/ (persistent, never /tmp-only for ships; no live Zen, no live ports, no Y13_GO live run).

## 00:59 +07 (T+0m): setup
- Read round-1 Council 3 paper improvements/worker-y13g-council-3.md (verdict AMEND, C3-1..C3-11) and fix-log tail (round-2 adjudication R1-R10, implementation 01:12-01:35).
- Verified pins above via md5sum; manifest md5 7c76383402e4c50b28adab6b25a22e09, 27 paths.
- Read SHIPPED.md in full: How to verify present, --ship-dir documented (space-form only, existing dir), launch-form + direct form documented, manifest md5 line present, single --repo path ~/workspace/computer-use-wayland.
- Read launcher module top (lines 1-400) and main() (1451-1508), runner module top (1-420), check_manifest/_check_entry_pyc/_scan_ship, write_token/check_token, _proven_no_body (line 1232: `"eval_error" in diag`), _verify_manifest __pycache__ block (lines 748-795), plan B1-B4/Amends/round-2 section (lines 540-765), regen docstring.
- Round-1 re-check (code, before probes): C3-2 fixed (check_manifest md5 message names commit+push first); C3-4 fixed in code (3 stems); C3-6 fixed (no old ~/computer-use-wayland path anywhere, grep clean); C3-9 mostly fixed; C3-10 fixed in code (write_token exists); C3-11a/b/c fixed. NOT fixed: C3-7 runner docstring lines 103,105 still `python3 launch_y13.py` without -P; C3-8 plan B1 still "holds only entry .pyc files (0-3)" and runner _verify_manifest comment still "two entry .pyc files (0, 1, or 2)" while _ENTRY_PYC_NAMES has 3.

## 01:00 +07 (T+1m): stage clean ship
- `python3 tests/realistic/regen_codex_y5_manifest.py --stage ~/workspace/y13g-r2-council-3/ship` rc 0; manifest md5 7c76383402e4c50b28adab6b25a22e09, 27 files checked, 0 mismatches, verify rc 0; 29 files, 0 .pyc. `git status` after regen: no tracked file modified (manifest identical). _SHIP_FILES identical in both files (29 paths) and equal to manifest 27 + manifest + SHIPPED.md (AST check).

## 01:01 +07 (T+2m): P1 launcher dry run on clean staged ship
- P1a `--ship-dir <ship>`, no Y13_GO: rc 2, "Y13_GO is not 1: no recorded go order...", no traceback. P1b by ship path, no --ship-dir: same rc 2 go-order gate. PASS.

## 01:02 +07 (T+3m): P2 --ship-dir validation
- P2a dangling (`--ship-dir` last arg): rc 2 "REFUSED: --ship-dir needs a value (space-separated, an existing directory)". P2b non-dir: rc 2 "--ship-dir value '/tmp/does-not-exist-ship' is not an existing directory". P2c `--ship-dir all`: rc 2 "--ship-dir value 'all' is not an existing directory" (old silent-eat gone). P2d `--ship-dir=DIR`: rc 2 go-order gate, i.e. the = form was silently ignored (see C3-1). P2e `--ship-dir=<ship>` from ship dir: same, go gate, = value ignored. P2f Y13_SHIP_DIR invalid: rc 2 "Y13_SHIP_DIR value ... is not an existing directory". P2g Y13_SHIP_DIR valid: go gate. P2h --ship-dir to existing non-ship dir: rc 2 "run_codex_y5.py not found in ...; run this launcher from the ship dir, or point --ship-dir (or Y13_SHIP_DIR) at the ship dir".

## 01:03 +07 (T+4m): P3 repo-tree guard + /tmp ship
- P3a repo-tree launcher, no --ship-dir: rc 2 "this looks like the repo tree, not a staged ship; cd to the ship dir or pass --ship-dir". C3-1 plain case fixed. P3b repo-tree + `--ship-dir=<ship>` (= form): SAME repo-tree refusal, telling the operator to "pass --ship-dir" when they did (see C3-1). P3c repo-tree + space-form --ship-dir: go gate. P3d `--ship-dir=<emptydir>` from ship dir: go gate, proving the = value is ignored entirely (wrong-ship risk, see C3-1). P3e `--repo=<path>`: go gate (ignored at derivation). P3e2 Y13_GO=1 + `--repo=<path>`: rc 2 "--repo is required..." (misdirecting, the operator did pass --repo). P3f staged ship under /tmp (/tmp/y13g-r2-council-3-ship, regen rc 0, verify rc 0) invoked by its path: go gate, no repo-tree false-fire. Guard does not false-fire under ~/workspace/... or /tmp.

## 01:04 +07 (T+5m): P7 direct form
- P7a `python3 -P run_codex_y5.py --verify-manifest` on a ship copy: rc 0, manifest_ok true, 27 files, 0 mismatches, md5 7c763834. P7b bare (no -P): rc 2 "run with python3 -P (PYTHONSAFEPATH=1): the bare form is refused, a planted file could execute at import". P7c launcher -P no args: go gate rc 2. P7d launcher bare: safe_path refusal rc 2. No .pyc left after any of them.

## 01:05 +07 (T+6m): P4 handover token (isolation, probes/p4_token.py)
- AST-extracted write_token + check_token with TOKEN_PATH pointed at scratch (real /tmp/worker-y13-handover.json absent before and after). write_token wrote {"asserted_at_unix": <now>, "basis": "Y13 go order (Y13_GO=1) + Y6c marker confirmed"}; check_token ACCEPTED it. Runner _check_handover (AST-extracted, LIVE_OWNER_AWAY=1) accepted the launcher-written token twice (fingerprint binds), then after a rewrite refused "handover token changed mid-run". P4 ALL PASS. C3-10 fixed. Note: main() calls write_token after go+marker but BEFORE check_manifest/_scan_ship (see C3-8).

## 01:06 +07 (T+7m): P5 recovery hints
- P5a nested codex-y5/__pycache__ .pyc: runner scan JSON rc 2 with "fix": "delete the named files, or re-stage the ship with the regen script"; launcher message same wording. P5b planted top-level evil.py: launcher "planted-py: evil.py. Fix: delete the named files, or re-stage the ship with the regen script" rc 2. P5c run_live .pyc (C3-4 retest): `python3 -m run_codex_y5 --verify-manifest` rc 2 script-form message, .pyc deleted (empty __pycache__ left), direct verify after rc 0. C3-4 fixed.
- P5a2: deleting ONLY the named .pyc file (as the hint says) leaves the empty nested dir; verify still refuses rc 2 kind "unexpected-dir" ("codex-y5/__pycache__"). Only after `rmdir` does verify pass rc 0 (P5a3). See C3-4.
- P5d check_manifest on tampered-manifest ship (AST-extracted, repo this checkout): rc 2 "ship manifest md5 7f3fbdec... != committed manifest md5 7c763834... (stale ship: commit + push the manifest first, then re-stage from the committed bytes with the regen script --stage)". C3-2 fixed.
- P5e _scan_ship on edited-file ship (AST-extracted): rc 2 "ship file md5 mismatch: codex-y5/test-01-git-workflow.md (stale or edited ship; re-stage)". No commit+push branch in this message (see C3-6).
- R7 spot: _normalize_remote_url 8/8 cases pass (https/.git/trailing slash/SSH/case-fold match; other owner and http do not match).
- check_manifest planted .py/symlink legs and _scan_ship symlink/bytecode/unexpected legs carry NO fix hint (read in code); they are unreachable via the launcher in practice (module-top scan fires first), TOCTOU-only. See C3-7.

## 01:07 +07 (T+8m): P6 SHIPPED.md How to verify, followed literally (probes/p6_verify.py)
- P6-1: extracted 14/14 tokenizer FunctionDefs from the runner with exactly SHIPPED.md's globals (os/json/hashlib/re/shlex/subprocess/time/marshal + _SHIP_DIR). P6-1b: first call raises NameError: "_RUNNER_MODULE_NAMES is not defined". SHIPPED.md never names the 14 functions and omits the 4 module constants the block closes over (_RUNNER_MODULE_NAMES, _RUNNER_MANIFEST_PATHS, _RUNNER_MD5S, _PY_NO_VALUE). My first space-joined cmdline attempt also returned false negatives: _argv_tokens splits on NUL (/proc form), which the note never says. See C3-2.
- P6-1c/2: with the 4 constants added, extraction works for both files. P6-3: AST-identity holds except _is_runner_cmdline (docstring only, the known sync-direction note). P6-4/5: 6 cases each pass in both copies (run, -P verify, -m, md5sum mention False, echo codex False, -c import False), NUL-joined argv. P6-6: _runner_md5s() returns 3 md5s incl. runner d5047ff5 and run_live 84fa106c. P6 ALL PASS with the corrected method.

## 01:07 +07 (T+8m): P4b _check_entry_pyc in isolation (probes/p4b_entry_pyc.py)
- Live path blocked by the marker gate, so AST-extracted. (a) Legit run_codex_y5 .pyc: "verified + removed entry .pyc", rc 0, cache empty after. (b) Forged .pyc (launch_y13 bytes under the run_codex_y5 name): rc 2 "entry .pyc mismatch (forged?)... re-stage the ship", .pyc left in place. R2 operative. P4b ALL PASS.

## 01:08 +07 (T+9m): remaining checks
- Runner main() unknown-arg handling: a leaked "--ship-dir=..." token would reach the runner as an unknown test selector ("unknown tests: [...]", rc 2) before any driving or JSONL rotation. Fail-closed, confusing message only (see C3-1).
- R9 verified in code: run_codex_y5.py:1232 `"eval_error" in diag` (key presence). R8 verified in code: check_marker/check_manifest/_check_entry_pyc wrap OSError/TimeoutExpired into _fail (exit 2). R5 verified in code: _verify_entry_hashes runs before the run_live import.
- No live Zen driven, no live ports used, no Y13_GO live run. Real token path untouched. Probes under ~/workspace/y13g-r2-council-3/ (persistent) + one /tmp ship (P3f, regen-staged, kept for the record).
