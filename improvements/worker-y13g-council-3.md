# Council 3 (operator view): Y13g fix re-review

- Reviewer: Council 3, Muse subagent (operator voice)
- Date: 2026-11-22 00:05 to 00:20 +07
- Repo: ~/workspace/computer-use-wayland, branch todolist-push
- Fix diff under review: 431b2a9..HEAD, 6 files, +1413/-259
  (Y13g commits caa4a7c, 0cf43f8, 03303f4, 6cd0f7a, b815590;
  manifest md5 0ca16ddd743acc9e28294fecd07a9c70, 27 files)
- Scope: operability ONLY. Can the operator (Y13) and the verifier
  actually use this as written? No live Zen driving. No ydotool.
- Method: read all 6 files in full (runner top/guard/scan,
  _verify_manifest, tokenizer block in both copies, launcher
  derive/guard/scan/marker/manifest/entry-pyc/scan/main, regen,
  SHIPPED.md, plan Y13g amendments); AST-compared the shared
  tokenizer block; ran 10 operability probes on scratch staged
  ships under ~/workspace/y13g-council3-scratch/ (never the real
  /tmp/worker-y13-server ship, never a live run). Probe log:
  improvements/worker-y13g-council-3-log.md.

## Verdict: AMEND

The documented operator flow works end to end as far as it can be
tested without a live slot: regen --stage from committed bytes
stages a ship that verifies rc 0 (md5 0ca16ddd, twice,
deterministic); the -m guard exits 2 with a clear message, leaves
no .pyc, and a direct verify after is rc 0; an empty __pycache__
passes verify; --ship-dir to a staged ship reaches the go-order
gate; the remote pin matches this checkout's origin. Every refusal
I probed is fail-closed. So this is not a BLOCK.

But the first real use will hit three moderate operability defects
(C3-1, C3-2, C3-3), plus a reachable brick the runner cannot
self-heal (C3-4) and refusal messages that misdirect instead of
guiding recovery (C3-5, C3-9). All fixes are small: a guard stem
list, a derivation validation, message wording, and doc lines.
Fix them, then the operator and the verifier can use this as
written. No live driving is blocked by Council 3 alone, but the
operator should not have to discover C3-1 by trial and error on
launch day, and the verifier should not have to rediscover the
AST-extraction method that lives only in the Y13g log.

## Findings

### C3-1 (moderate): launcher invoked by its repo-tree path derives the repo tree as the ship and refuses it as "tampered"

- Files: tests/realistic/launch_y13.py:116-139 (_derive_ship_dir),
  tests/realistic/launch_y13.py:188-224 (_refuse_tampered_ship)
- Evidence (probe P5, live): from the repo root,
  `python3 -P tests/realistic/launch_y13.py --repo
  ~/workspace/computer-use-wayland all` refuses at module top with
  `[launch_y13] REFUSED: tampered ship dir
  /home/hatch/workspace/computer-use-wayland/tests/realistic:
  mixed: __pycache__/run_agyq2.cpython-312.pyc, ...,
  run_agy_y2.py, run_batch3.py, regen_codex_y5_manifest.py, ...`,
  exit 2. The file-dir leg of _derive_ship_dir accepts any dir
  holding run_codex_y5.py + the manifest, and the repo tree holds
  both, so the most likely operator mistake (running the launcher
  by its repo path instead of from the staged ship) is reported
  as ship tampering, with no hint of the real cause or fix.
- Fix: accept the file dir as the ship only when it is a plausible
  ship (for example: no .py file outside _SHIP_PY, and a codex-y5/
  dir present), otherwise fall through to the /tmp fallback or
  fail with "this looks like the repo tree, not a staged ship; cd
  to the ship dir or pass --ship-dir <ship>". At minimum, add the
  recovery to the module-top refusal: "if you ran this from the
  repo checkout, cd /tmp/worker-y13-server or pass --ship-dir".

### C3-2 (moderate): the manifest-md5 refusal prescribes a fix that cannot work when the cause is uncommitted edits

- Files: tests/realistic/launch_y13.py:857-859 (check_manifest),
  tests/realistic/launch_y13.py:1009 (_scan_ship md5 leg)
- Evidence (code + regen determinism): the refusal says "stale
  ship; re-stage from the committed bytes with the regen script
  --stage". But regen --stage stages WORKING-TREE bytes (everything
  except the pinned run_live.py), not committed bytes; re-running
  it with the same working tree reproduces the same manifest md5
  (proved: two --stage runs, same md5 0ca16ddd). If the operator
  edited the runner and re-staged without committing, the message
  sends them in a circle: re-stage, same md5, same refusal. The
  message is correct only for the stale-ship case, and the two
  cases are indistinguishable from the message alone.
- Fix: distinguish the cases in the message: "if you edited the
  runner/launcher, commit + push the manifest first, then
  re-stage; if the ship is merely stale, re-stage". Apply the same
  wording to the _scan_ship md5 message "(stale or edited ship;
  re-stage)".

### C3-3 (moderate): the verifier's method is undocumented in the committed docs, and the md5 leg silently disables itself outside a ship dir

- Files: improvements/worker-y13-codex-y5-live-plan.md:571-576
  (stale import sentence), :644-658 (B3 bullet);
  tests/realistic/codex-y5/SHIPPED.md (no verifier note);
  tests/realistic/run_codex_y5.py:3729-3754 (_runner_md5s)
- Evidence: (a) Importing either entry point now exits 2, so the
  tokenizer can only be tested by AST-extraction (as Y13r2 did)
  or via subprocess. That method lives only in the Y13g log
  ("VERIFIER NOTE"), not in SHIPPED.md or the plan, so a verifier
  reading only the committed docs will try `import run_codex_y5`,
  hit exit 2, and lose a cycle. (b) _runner_md5s reads the
  manifest from _SHIP_DIR (the file's own dir) and yields an empty
  set when it is unreadable, with the md5 leg then silently off.
  An AST-extracted copy run outside a ship dir therefore gets
  false negatives on exactly the renamed/symlinked cases B3 was
  written to catch, and the plan's B3 bullet never says the leg
  needs the real files staged next to a manifest. (c) The plan's
  Y13f section still says "Probes importing the runner must use
  PYTHONDONTWRITEBYTECODE=1 or a clean extraction". Under Y13g
  the env var no longer helps at all: any import exits 2.
- Fix: add a "How to verify" note to SHIPPED.md (or the plan):
  never import the entry points; AST-extract the tokenizer block
  with __file__ pointed at a staged ship (or set _SHIP_DIR to one),
  and stage real files for renamed/symlinked cases, because the
  md5 leg reads the ship manifest and is off without it. Correct
  the stale sentence to "never import; use a clean extraction
  (AST-extract) or subprocess".

### C3-4 (moderate-low): the runner -m guard deletes only 2 stems, so a run_live .pyc bricks verify with no self-heal

- Files: tests/realistic/run_codex_y5.py:133-145
  (_ENTRY_PYC_NAMES, 2 stems), :172-183 (guard);
  tests/realistic/launch_y13.py:143 (_ENTRY_STEMS, 3 stems),
  :880-950 (_check_entry_pyc, 3 stems)
- Evidence (probe P9, live): `python3 -c "import run_live"` in a
  staged ship copy writes __pycache__/run_live.cpython-312.pyc;
  a direct `python3 -P run_codex_y5.py --verify-manifest` after
  refuses rc 2 (`{"refused": true, "kind": "pyc", "files":
  ["__pycache__/run_live.cpython-312.pyc"]}`), and the .pyc is
  still there afterwards: the guard never deletes the run_live
  stem. The launcher would delete it (_check_entry_pyc covers 3
  stems), but only after the marker + token + port gates; regen
  --stage (whole-dir rebuild) and manual rm are the other
  recoveries, and no refusal message names any of them (see
  C3-5). Note run_live.py itself (pinned 1e3901c) has a real
  `if __name__ == "__main__"` at line 1801, so `python3 -m
  run_live` is a live-driving form that also leaves this .pyc.
- Fix: add "run_live" to the runner's guard stem list (and to
  _ENTRY_PYC_NAMES, keeping the 3 stem sets in sync), and document
  that a run_live .pyc is cleared by the launcher or by re-stage.

### C3-5 (moderate-low): refusal messages name what is wrong but not what to do

- Files: tests/realistic/run_codex_y5.py:247-255 (scan JSON);
  tests/realistic/launch_y13.py:219-222 (launcher tamper refusal),
  :836-846 (check_manifest planted refusals), :950-1010
  (_scan_ship)
- Evidence (probes P4, P9, live): the scan JSON reports kind +
  files and nothing else, for example a nested
  codex-y5/__pycache__/check-dashes .pyc left by running
  check-dashes.py in the ship, or the run_live .pyc from C3-4.
  The launcher's planted-file failures likewise name the file
  only. A nested __pycache__ bricks BOTH verify and the launcher
  (_scan_ship refuses any .pyc at any depth and never auto-cleans
  nested caches); the only recoveries are manual rm or regen
  --stage, and neither message says so.
- Fix: add a "fix" hint to the scan JSON (for example: "delete the
  listed .pyc files if a legitimate self-cache, else re-stage
  with regen --stage") and to the launcher's planted/tamper
  messages ("delete the listed file, or re-stage the ship").

### C3-6 (low-moderate): the two documented --repo paths disagree

- Files: tests/realistic/launch_y13.py:97
  (`--repo ~/computer-use-wayland`) vs
  tests/realistic/codex-y5/SHIPPED.md:42
  (`--repo /home/james/workspace/computer-use-wayland`)
- Evidence: `~/computer-use-wayland` is
  /home/james/computer-use-wayland; SHIPPED.md says
  /home/james/workspace/computer-use-wayland. One of them is not
  the laptop checkout. Fail-closed (a wrong path gives a clear
  "--repo X is not a git checkout"), so the operator recovers by
  guessing the other path, but they should not have to guess on
  launch day.
- Fix: verify on the laptop which checkout path is real and use
  that one path in both docs.

### C3-7 (low): the runner docstring's launch lines lack -P

- File: tests/realistic/run_codex_y5.py:102-104
  (`Y13_GO=1 python3 launch_y13.py all`,
  `Y13_GO=1 python3 launch_y13.py 01 02`)
- Evidence: the same file's SCRIPT FORM ONLY block (:106-113)
  demands `python3 -P`, and the launcher docstring + SHIPPED.md
  both use -P. Copy-paste from the runner docstring is the one
  place an operator gets the no--P form. Functionally harmless
  (the launcher's own top imports are sys/os only, and it execs
  the runner with -P anyway), but the docstring contradicts its
  own rule.
- Fix: add -P to both launch lines.

### C3-8 (low-moderate): the plan's B1 __pycache__ wording implies 1-2 entry .pyc files pass verify; they do not

- File: improvements/worker-y13-codex-y5-live-plan.md:621-626
- Evidence: "exempts a __pycache__ dir ONLY when it holds only
  entry .pyc files (0-2); the files inside are still refused as
  bytecode, so the exemption exists only to keep an empty
  __pycache__ left by a probe from bricking verify." The two
  halves contradict for the operator: with 1-2 entry .pyc files
  present, the module-top scan refuses first, and
  _verify_manifest's own bytecode line
  (run_codex_y5.py:639) refuses second. Only the EMPTY dir passes
  (proved P3, rc 0). An operator reading the bullet will expect
  verify to pass with 1-2 entry .pyc present. The same section's
  "The -m guard deletes a legitimate self-cache (every cache-tag
  variant)" needs the C3-4 qualifier (two stems only in the
  runner; run_live is launcher-only).
- Fix: reword to "exempts an EMPTY __pycache__ dir only; any .pyc
  inside still refuses (scan first, then verify)". Add the
  run_live qualifier to the guard sentence.

### C3-9 (low-moderate): --ship-dir is undocumented in SHIPPED.md, and its failure messages misdirect

- Files: tests/realistic/codex-y5/SHIPPED.md (no --ship-dir
  mention anywhere); tests/realistic/launch_y13.py:1085-1089
  (not-found message), :116-139 (_derive_ship_dir),
  :1098-1106 (main stripping)
- Evidence (probes P6, P7, P8, live): --ship-dir to a staged
  ship works (P6 reaches the go-order gate, so derivation + scan
  pass). But: (a) SHIPPED.md, the doc the operator reads at
  launch time, never mentions --ship-dir or Y13_SHIP_DIR, so a
  verifier staging at a temp path has to find it in the launcher
  docstring or the plan. (b) `--ship-dir /tmp/does-not-exist-ship`
  gives "run_codex_y5.py not found in /tmp/does-not-exist-ship;
  run this launcher from the ship dir", which never names
  --ship-dir/Y13_SHIP_DIR as the suspect (same for a stale
  Y13_SHIP_DIR env var). (c) A dangling --ship-dir silently eats
  the next arg as its value: `--ship-dir all` sets SHIP_DIR to
  "all" and fails with "run_codex_y5.py not found in all". (d)
  The `=` forms (--ship-dir=/tmp/x, --repo=/tmp/x) are not parsed
  at all and would reach the runner as test selectors.
- Fix: add a --ship-dir line to SHIPPED.md; validate the
  --ship-dir value in _derive_ship_dir (refuse when it is not an
  existing directory, or is a known test selector); name
  --ship-dir/Y13_SHIP_DIR in the not-found message; document
  space-form only.

### C3-10 (low): the handover-token "written by the launcher" claim is false in the code

- Files: tests/realistic/codex-y5/SHIPPED.md:35;
  improvements/worker-y13-codex-y5-live-plan.md:405-407;
  tests/realistic/run_codex_y5.py:297, :314;
  tests/realistic/launch_y13.py:658-679 (check_token, read-only)
- Evidence: three docs say the token is "written by the launcher
  at run start", but no code in launch_y13.py writes TOKEN_PATH
  (verified by grep; the launcher only reads it in check_token).
  If the token is missing, the refusal names the path but the
  operator has no code-backed way to create it from these 6
  files. Pre-existing text that the Y13g SHIPPED.md/plan edits
  left standing.
- Fix: either make the launcher write a fresh token at run start
  (as the docs claim) or correct all three docs to say who writes
  it (Muse, at handover) with the exact JSON shape
  (asserted_at_unix + basis + run id).

### C3-11 (low, doc batch): three small doc inaccuracies

- (a) Plan B2 bullet
  (improvements/worker-y13-codex-y5-live-plan.md, B2):
  "check_manifest refuses any planted file" overstates it.
  check_manifest (launch_y13.py:829-846) refuses only top-level
  .py, any .pyc, and symlinks; a planted file under codex-y5/
  (for example codex-y5/evil.py) passes check_manifest and is
  caught only by _scan_ship. Fix the wording to "check_manifest
  refuses planted top-level .py/.pyc/symlink; _scan_ship refuses
  any other planted file".
- (b) Regen docstring
  (tests/realistic/regen_codex_y5_manifest.py:33-35, as edited by
  Y13g b815590): "stale .pyc files there would otherwise trip the
  runner's pre-import tamper scan on the next module import".
  There is no next module import under Y13g (any import exits 2).
  Fix the rationale (for example: "keeps the repo tree clean; the
  scan refuses any .pyc").
- (c) SHIPPED.md regen line
  (tests/realistic/codex-y5/SHIPPED.md:27): the command
  `python3 tests/realistic/regen_codex_y5_manifest.py --stage
  /tmp/worker-y13-server` carries no cwd note; run from the ship
  dir it fails with "can't open file". The regen docstring says
  "from the repo root". Fix: add "(from the repo root)" to the
  SHIPPED.md line.

## Verified holds (checked, passing)

- H1: regen --stage from committed bytes stages a ship that
  verifies rc 0, manifest md5 0ca16ddd743acc9e28294fecd07a9c70,
  27 files, 0 mismatches; run twice, same md5 (deterministic).
  No __pycache__ or .pyc left in the staged ship.
- H2: -m sequence (probe P2): `python3 -m run_codex_y5
  --verify-manifest` exits 2 with the clear guard message on
  stderr, leaves no .pyc behind (empty __pycache__ dir only),
  and a direct verify after is rc 0.
- H3: empty __pycache__ passes verify rc 0 (probe P3).
- H4: the shared tokenizer block is AST-identical between
  run_codex_y5.py and launch_y13.py: all 12 functions + 4
  constants identical ignoring docstrings; _is_runner_cmdline
  differs only in its docstring (the sync-direction note). The
  "AST-verified identical" claim HOLDS.
- H5: --ship-dir to a staged ship works: derivation + module-top
  scan pass and the launcher reaches the go-order gate with a
  clear actionable message (probe P6).
- H6: the remote pin matches this checkout's origin
  (https://github.com/phamTuan207/computer-use-wayland.git).
- H7: Amend 5 is in the code: _proven_no_body uses
  `diag.get("eval_error") is not None`
  (run_codex_y5.py:1081).
- H8: with Y13_GO=1 and a staged ship, the launcher reaches the
  marker gate and refuses "no Y6c completion marker on
  todolist-push", exit 2 (probe P10). Expected current state
  (Y6c ended NO VERDICT); the message could add "(wait for a
  fresh Y6c-pattern marker or Muse direction)" but SHIPPED.md
  already documents the gate.
- H9: Amend 2 is in the code as claimed: the WARNING branch uses
  the basename/component match (_is_codex_process), the REFUSE
  branch keeps the fail-closed substring rule
  (launch_y13.py:584-608, :700-712).
- H10: SHIPPED.md launch command (with -P, --repo, `all`) and the
  regen command are copy-paste runnable in their stated cwds,
  except for the C3-6 --repo path question and the C3-11(c) cwd
  note.

## Out of scope / not re-verified

- Correctness of the B1-B4 security fixes themselves (Council 1 /
  redteam territory); this paper judges operability only.
- The A2/A4/A6d/A3/A5/A7/A8 re-test batteries: the independent
  verifier runs them (its harnesses were lost with /tmp/y13r2/;
  see C3-3 for the method note it needs). Council 3 ran only the
  10 operability probes above, on scratch copies, no live Zen.
- Whether /home/james/workspace/computer-use-wayland is the real
  laptop checkout (C3-6): not verifiable from this VM.
