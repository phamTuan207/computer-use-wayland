# Council 3 (operator view): Y13g ROUND-2 fix re-review

- Reviewer: Council 3, Muse subagent (operator voice)
- Date: 2026-11-22 00:59 to 01:08 +07
- Repo: ~/workspace/computer-use-wayland, branch todolist-push
- Fix diff under review (round 2 ONLY): 0639d04, 87eec47, 6ba43f2, 8bdd5aa, 5a9b9e8
  (runner d5047ff573820491263a2eb3805105f4, launcher 8e72a5ce85cbaf8382f998987e8890e5,
  run_live 84fa106c253d5e7f16daccf2ce3f14a5 (pin 1e3901c holds),
  manifest 7c76383402e4c50b28adab6b25a22e09, 27 files)
- Scope: operability ONLY. Can the operator (Y13) and the verifier
  actually use this as written? No live Zen driving. No ydotool.
- Method: read the round-1 Council 3 paper first and re-checked
  every round-1 finding against the round-2 diff (see Round-1
  re-verification below); read all 6 files in the diff (runner and
  launcher module tops, guard, scan, _verify_entry_hashes,
  _check_entry_pyc, check_manifest, _scan_ship, write_token,
  _proven_no_body, tokenizer block in both copies, regen,
  SHIPPED.md, plan B1-B4/Amends/round-2 section); ran 13
  operability probes on scratch staged ships under
  ~/workspace/y13g-r2-council-3/ (plus one regen-staged ship under
  /tmp/y13g-r2-council-3-ship), never the real
  /tmp/worker-y13-server ship, never a live run. Probe log:
  improvements/worker-y13g-r2-council-3-log.md; probe scripts:
  ~/workspace/y13g-r2-council-3/probes/ (p4_token.py, p4b_entry_pyc.py,
  p5d_manifest.py, p6_verify.py).

## Verdict: AMEND

The documented operator flow works end to end as far as it can be
tested without a live slot: regen --stage stages a ship that
verifies rc 0 (md5 7c763834, deterministic, 29 files, 0 .pyc);
--ship-dir to a staged ship reaches the go-order gate; the
repo-tree guard refuses the repo path with a clear message and
does not false-fire under ~/workspace or /tmp; the direct -P
verify is rc 0 and the bare form refuses at safe_path; the
launcher now really writes the handover token and the runner's
fingerprint binding accepts it; _check_entry_pyc verifies and
deletes a legit entry .pyc and refuses a forged one; the
manifest-md5 refusal now prescribes commit + push first. So this
is not a BLOCK, and every refusal I probed is fail-closed.

But two first-use defects remain (C3-1, C3-2), plus two
round-1 fixes that did not land (C3-3, C3-5) and three small
recovery-hint gaps (C3-4, C3-6, C3-7). The sharpest is C3-2: the
verifier following SHIPPED.md "How to verify" literally hits a
NameError on the first call, because the note omits the 4 module
constants the tokenizer closes over and never names the 14
functions. The sharpest operator defect is C3-1: the
--ship-dir=DIR form is silently ignored, so a tamper probe that
points at a staged ship in = form tests the wrong ship. All
fixes are small: one arg-form refusal, a doc paragraph, two
docstring lines, and message wording. Fix them, then the
operator and the verifier can use this as written.

## Findings

### C3-1 (moderate): --ship-dir=DIR and --repo=DIR are silently ignored, not refused

- Files: tests/realistic/launch_y13.py:144-157 (_derive_ship_dir),
  :1464-1472 (main stripping)
- Evidence (probes P2d, P2e, P3b, P3d, P3e, P3e2, live):
  "--ship-dir" is matched by exact string only, so
  `--ship-dir=/tmp/x` never registers. From the ship dir it is
  ignored and the launcher uses the file-dir ship (P3d:
  `--ship-dir=<emptydir>` still reaches the go gate). From the
  repo tree it falls through to the repo-tree refusal (P3b),
  which tells the operator to "pass --ship-dir" when they
  already did, in = form. `--repo=/path` behaves the same (P3e2,
  Y13_GO=1: "--repo is required", when --repo was passed). The
  docstring and SHIPPED.md both say the = form is unsupported,
  but the code never refuses it. Consequence: a tamper probe
  that stages a ship at a temp path and points --ship-dir at it
  in = form silently tests the file-dir ship instead, and can
  report a false PASS on the wrong ship. If the gates ever pass
  with the = token present, main() does not strip it, so it
  reaches the runner as an unknown test selector ("unknown
  tests: ['--ship-dir=...']", rc 2, before any driving or JSONL
  rotation; verified in run_codex_y5.py:4614-4627). Fail-closed
  at the runner, but confusing.
- Fix: in _derive_ship_dir (before the repo-tree check), refuse
  any argv token starting with "--ship-dir=" or "--repo=" with
  "use the space-separated form --ship-dir DIR / --repo DIR".
  Do the same in main() as a backstop.

### C3-2 (moderate): SHIPPED.md "How to verify" fails literally at the first call

- File: tests/realistic/codex-y5/SHIPPED.md:43-49
- Evidence (probe P6, live): following the note exactly,
  AST-extract the 14 tokenizer FunctionDefs and exec them with
  the listed globals (os/json/hashlib/re/shlex/subprocess/time/
  marshal + _SHIP_DIR), then the first call raises
  `NameError: name '_RUNNER_MODULE_NAMES' is not defined`
  (probes/p6_verify.py, P6-1b). The 14 functions close over 4
  module-level constants that the note never mentions:
  _RUNNER_MODULE_NAMES, _RUNNER_MANIFEST_PATHS, _RUNNER_MD5S,
  _PY_NO_VALUE (run_codex_y5.py:3860-3865, :4032). The note
  also never names the 14 functions (it says "the named
  FunctionDef nodes" without naming them; the plan names only
  the 2 new ones), so the verifier must discover the block by
  reading the source. A third gap: the note never says the
  input is a NUL-joined /proc cmdline (_argv_tokens splits on
  \x00); my first space-joined attempt returned false negatives
  on every positive case. With the 4 constants added and
  NUL-joined argv, all 6 cases pass in both copies and the md5
  leg returns 3 entries (P6-4/5/6), so the method is sound
  once corrected. This is the round-1 C3-3 fix as shipped, but
  it does not work as written.
- Fix: rewrite the note to name the 14 functions (or point at
  the "Keep in sync" block delimiters), add the 4 constants to
  the globals list, and say cmdlines are NUL-joined argv lists
  as read from /proc, with one copy-pasteable snippet. Suggested
  snippet (verified in P6): extract the 14 FunctionDefs plus
  the 4 Assign nodes, exec with the listed globals and
  _SHIP_DIR set to the staged ship, then call
  _is_runner_cmdline("\x00".join(argv), ship_dir).

### C3-3 (moderate-low): round-1 C3-7 NOT fixed, runner docstring launch lines still lack -P

- File: tests/realistic/run_codex_y5.py:103,105
- Evidence: `cd /tmp/worker-y13-server && Y13_GO=1 python3
  launch_y13.py all` and `Y13_GO=1 python3 launch_y13.py 01 02`
  still carry no -P, and no --repo either. R10 claimed this fix
  but commit 5a9b9e8 touched only the plan, manifest, SHIPPED.md
  and regen, never the runner; no R2 commit changes these lines
  (verified by diff). Under R1 this is no longer a cosmetic
  mismatch: a bare invocation now refuses at the safe_path gate
  (probe P7d, rc 2), so the docstring's own launch lines are
  commands that cannot run as written. The launcher docstring
  (:109-110) and SHIPPED.md both use -P with --repo.
- Fix: add `-P` and `--repo ~/workspace/
  computer-use-wayland` to both lines, matching the launcher
  docstring and SHIPPED.md.

### C3-4 (moderate-low): the scan "fix" hint misleads when a directory is in the list

- Files: tests/realistic/run_codex_y5.py:347-353 (scan JSON fix
  field); tests/realistic/launch_y13.py:367-371 (launcher message)
- Evidence (probes P5a, P5a2, P5a3, live): a nested
  codex-y5/__pycache__/check-dashes.cpython-312.pyc refuses with
  files ["codex-y5/__pycache__", "codex-y5/__pycache__/
  check-dashes.cpython-312.pyc"] and the hint "delete the named
  files, or re-stage the ship with the regen script". Deleting
  ONLY the named .pyc file, exactly as told, leaves the empty
  nested dir, and verify still refuses rc 2, kind
  "unexpected-dir", naming the dir again. Only `rmdir` of the
  empty dir recovers (verify rc 0 after). The list mixes a
  directory with a file, and the hint says "files".
- Fix: word the hint "delete the named files and directories,
  or re-stage the ship with the regen script", or do not list a
  directory whose only content is already listed as a file.

### C3-5 (low): round-1 C3-8 NOT fixed in substance, B1 wording still contradictory

- Files: improvements/worker-y13-codex-y5-live-plan.md:633-638
  (B1); tests/realistic/run_codex_y5.py:748-753 (_verify_manifest
  comment)
- Evidence: the plan still says "_verify_manifest exempts a
  __pycache__ dir ONLY when it holds only entry .pyc files
  (0-3); the files inside are still refused as bytecode, so
  the exemption exists only to keep an EMPTY __pycache__ left
  by a probe from bricking verify." The count changed 2 to 3
  but the contradiction is the same as round 1: with 1-3 entry
  .pyc files present the dir is exempt but the files refuse, so
  only the EMPTY dir passes (proved round 1, probe P3, and the
  code comment at :294-299 says "observably this exempts an
  EMPTY __pycache__ dir only"). The _verify_manifest comment
  itself is now stale in the other direction: it still says
  "the two entry .pyc files (0, 1, or 2)" while
  _ENTRY_PYC_NAMES holds 3 stems (run_codex_y5, launch_y13,
  run_live). The B4 line ("EMPTY only, see B1") is correct, so
  the fix is wording only.
- Fix: reword B1 to "exempts an EMPTY __pycache__ dir only; any
  .pyc inside still refuses (scan first, then verify)", and fix
  the _verify_manifest comment to "three entry .pyc files
  (0-3)".

### C3-6 (low): _scan_ship md5 message does not distinguish the edited case

- File: tests/realistic/launch_y13.py:1340-1345 (_scan_ship)
- Evidence (probe P5e, live, AST-extracted): an edited ship
  file refuses "ship file md5 mismatch: codex-y5/
  test-01-git-workflow.md (stale or edited ship; re-stage)".
  Re-stage alone does not settle the edited case: regen
  --stage rebuilds the manifest from the working tree, so
  _scan_ship then passes but check_manifest refuses next (its
  message does give the full instruction, probe P5d). The
  operator learns the real fix one refusal later than they
  need to. This is the same family as round-1 C3-2, one level
  down: the check_manifest message was fixed, this one was not.
- Fix: mirror the check_manifest wording: "(stale or edited
  ship; if you edited a ship file, commit + push the manifest
  first, then re-stage)".

### C3-7 (low): the remaining hint-less refusal legs

- Files: tests/realistic/launch_y13.py:1188-1210
  (check_manifest planted symlink / .py legs); :1336-1345
  (_scan_ship symlink / bytecode / unexpected / __pycache__ /
  unreadable legs)
- Evidence (code read): check_manifest refuses "planted symlink
  dir in ship", "planted symlink in ship" and "planted
  top-level .py in ship" with no fix hint, while its .pyc leg
  right next to them says "Fix: delete the file, or re-stage
  the ship". _scan_ship's legs likewise name the path only.
  Reachability is limited: the module-top scan fires first on
  every one of these through the launcher, so these legs are
  TOCTOU-only in practice, which is why this stays low. R10
  claimed "recovery hints in refusals" without qualification.
- Fix: add the same "Fix: delete the named file, or re-stage
  the ship" suffix to each leg.

### C3-8 (low, observation): write_token runs before the ship-integrity checks

- File: tests/realistic/launch_y13.py:1474-1479 (main order:
  check_go, check_marker, write_token, check_manifest,
  _check_entry_pyc, _scan_ship, check_token)
- Evidence (code read + probe P4): the token is written after
  go + marker, as documented, but before check_manifest and
  _scan_ship. A launch that then refuses as tampered still
  leaves a fresh token on disk asserting a go order + marker
  for a run that never happened. The basis claim stays true
  (go + marker did pass), and the launcher rewrites the token
  on every launch attempt, so the only exposure is a direct
  runner invocation reusing the leftover token with
  LIVE_OWNER_AWAY=1, a form SHIPPED.md already forbids for live
  runs. Low.
- Fix: move write_token() to just after _scan_ship, immediately
  before check_token(); the docstring claim "written after the
  go order + marker pass" stays true and gains "and after the
  ship passes its integrity checks".

## Round-1 re-verification (C3-1..C3-11 against the round-2 diff)

- C3-1 repo-tree guard: FIXED for the documented form (P3a
  clear refusal; P3c space-form reaches the go gate; no
  false-fire under ~/workspace or /tmp, P1b/P3f). Residual:
  the = form (see C3-1 above).
- C3-2 manifest-md5 message: FIXED (P5d: "commit + push the
  manifest first, then re-stage from the committed bytes with
  the regen script --stage").
- C3-3 verifier method: PARTLY FIXED. The "How to verify" note
  exists in SHIPPED.md and the stale PYTHONDONTWRITEBYTECODE
  sentence is gone (plan now says probes cannot import at all
  and must AST-extract). But the note does not work as written
  (see C3-2 above). The md5-leg warning in the note is accurate
  (P6-6: the leg reads the ship manifest and yields 3 md5s
  only with _SHIP_DIR set to a staged ship).
- C3-4 run_live .pyc brick: FIXED (P5c: -m guard deletes the
  run_live .pyc, verify after rc 0; runner guard now 3 stems).
- C3-5 refusal hints: MOSTLY FIXED. Scan JSON "fix" field and
  launcher tamper message both name the fix (P5a/P5b); the
  check_manifest .pyc leg and _check_entry_pyc mismatch message
  name it too. Residuals: nested-dir wording (C3-4) and the
  hint-less legs (C3-7).
- C3-6 --repo paths: FIXED. Launcher docstring and SHIPPED.md
  both use ~/workspace/computer-use-wayland; the old
  ~/computer-use-wayland path appears nowhere in the 6 files
  (grep clean). The runner docstring carries no --repo at all
  (see C3-3).
- C3-7 runner docstring -P: NOT FIXED (see C3-3 above).
- C3-8 B1 __pycache__ wording: NOT FIXED in substance (see
  C3-5 above). The guard sentence now correctly says 3 stems.
- C3-9 --ship-dir: MOSTLY FIXED. SHIPPED.md documents it
  (space-form only, existing directory); dangling, non-dir,
  `--ship-dir all`, and invalid Y13_SHIP_DIR all refuse
  clearly (P2a-c, P2f); the not-found message names
  --ship-dir/Y13_SHIP_DIR (P2h). Residual: the = form (C3-1).
- C3-10 handover token: FIXED (P4: launcher writes a fresh
  token, check_token accepts it, runner fingerprint binding
  accepts it twice and refuses a mid-run rewrite).
- C3-11 doc batch: FIXED. (a) Plan B2 now says
  "check_manifest refuses planted top-level .py, non-entry
  .pyc, and symlinks (nested planted files are caught by ...
  _scan_ship)". (b) Regen docstring now says the .pyc
  deletion is hygiene, not for "the next module import".
  (c) SHIPPED.md regen line now says "(from the repo root)".

## Verified holds (checked, passing)

- H1: regen --stage from the working tree stages a ship that
  verifies rc 0, manifest md5 7c76383402e4c50b28adab6b25a22e09,
  27 files, 0 mismatches, 29 files on disk, 0 .pyc;
  deterministic (same md5 as the committed manifest, and the
  regen rewrote no tracked file).
- H2: _SHIP_FILES identical in both entry points (29 paths)
  and equal to manifest 27 + manifest + SHIPPED.md (AST check).
- H3: launcher dry run on a clean staged ship reaches the
  go-order gate, rc 2, clear message, no traceback, with and
  without --ship-dir (P1a/P1b).
- H4: --ship-dir validation refuses dangling, non-dir,
  `--ship-dir all`, and invalid Y13_SHIP_DIR values, each rc 2
  with a message naming the flag (P2a-c, P2f).
- H5: repo-tree guard refuses by repo path (P3a) and does not
  false-fire for ships under ~/workspace or /tmp (P1b, P3f).
- H6: direct form `python3 -P run_codex_y5.py
  --verify-manifest` on a staged ship is rc 0; bare (no -P)
  refuses at safe_path, rc 2, clear message, no .pyc left
  (P7a/P7b; launcher bare likewise, P7d).
- H7: handover token round-trips launcher-written to
  runner-checked with the fingerprint binding intact (P4).
- H8: _check_entry_pyc is operative in isolation: legit entry
  .pyc verified + deleted, forged entry .pyc refuses rc 2 and
  is left in place (P4b).
- H9: the shared tokenizer block is AST-identical between the
  files except _is_runner_cmdline (docstring only, the known
  sync-direction note); with the corrected extraction method
  all 6 probe cases agree in both copies (P6-3/4/5).
- H10: R7 remote normalization passes 8/8 cases (https, .git,
  trailing slash, SSH form, host case-fold match; other owner
  and http do not match). R9 holds in code
  (`"eval_error" in diag`, run_codex_y5.py:1232). R8 holds in
  code (subprocess calls wrapped into _fail, exit 2). R5 holds
  in code (_verify_entry_hashes before the run_live import).

## Out of scope / not re-verified

- Correctness of the R1-R5 security fixes themselves (Council 1
  / redteam territory); this paper judges operability only.
- The marker gate itself: no Y6c completion marker exists, so
  the launcher path past check_marker could not be run live;
  check_manifest and _scan_ship were probed by AST-extraction
  only (P5d/P5e), and _check_entry_pyc the same way (P4b).
- Whether ~/workspace/computer-use-wayland is the
  real laptop checkout: not verifiable from this VM (same
  limit as round 1).
