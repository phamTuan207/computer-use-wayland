# Y13g Council 1 verdict: AMEND (design/consistency)

Council 1 (design/consistency voice) review of the Y13g fix
diff, 431b2a9..HEAD, scoped to the 6 files Y13g touched.
Reviewed 2026-11-22 00:05-00:17 +07. No live Zen driving.
Method: full read of the diff and both entry points; AST
comparison of the shared tokenizer block (17 names,
docstrings stripped); behavioral probes on the AST-extracted
tokenizer; md5 recomputation of runner, launcher, manifest,
and every SHIPPED.md entry.

## Verdict: AMEND

No BLOCK-grade hole. Every .pyc refusal in the fix is
fail-closed (a forged entry .pyc is refused before it can
execute through the launcher path), the tokenizer block is
AST-identical between the two copies, and the regen script,
manifest, and SHIPPED.md agree on all md5s. But the fix has
one structural doc-vs-code mismatch (F1: the documented
out-of-process .pyc check cannot run on a pre-existing
.pyc), one guard asymmetry (F2), one shared tokenizer gap
against its own doc claim (F3), and a set of smaller
doc inconsistencies (F4-F10). All are fixable without
changing the security posture; F1-F3 need a code or doc
change before the fix is called coherent.

## What passed

- (Check 1) Module-top bootstraps: both entry points import
  only sys/os before the guard + narrow os.path-only scan,
  refuse any .pyc / symlink / non-ship .py, set
  sys.dont_write_bytecode, and only then import the rest.
  _SHIP_PY is identical in both files (3 entry points +
  codex-y5/check-dashes.py). SHIP_DIR derivation differs
  by design (runner: file dir; launcher: --ship-dir >
  Y13_SHIP_DIR > file dir > fallback, Amend 4) and both
  resolve to the staged ship dir in the live flow.
- (Check 2) Tokenizer block: AST-identical (docstrings
  stripped) across all 17 shared names between
  run_codex_y5.py and launch_y13.py; the text diff shows
  ONLY the sync-direction notes (plus the trivial CODEX
  comment drift in F10). Behavior probed on 18 cases:
  -P, -m (bare and dotted), -W value, -c exec(open(...)),
  -c import (correctly not caught), md5sum/echo mentions
  (correctly not caught) all behave as documented.
- (Check 3, outcome level) _verify_manifest, _scan_ship,
  and check_manifest agree on outcomes: any non-empty
  __pycache__ refuses everywhere; an empty __pycache__ is
  allowed everywhere. The _verify_manifest dir exemption
  only ever matters for the empty-dir case, as its comment
  states.
- (Check 4, limits mostly consistent) The forged entry
  .pyc via -m/import executes limit is stated in all four
  surfaces (runner docstring, launcher docstring check 4,
  plan B1, SHIPPED.md). The marker-is-coordination-not-auth
  limit is stated in all four surfaces. The -m guard is in
  both entry points; _proven_no_body uses `is not None`
  (Amend 5) as documented.
- (Check 5) Regen, manifest, SHIPPED.md agree: manifest
  file md5 0ca16ddd743acc9e28294fecd07a9c70, runner
  db3e357f616d21e1d6b2a573682019fd, launcher
  eec63492ae581b3046f2cc3baea97473, run_live pin 84fa106c
  holds; all 27 manifest entries appear in SHIPPED.md
  with matching md5s. The working-tree run_live.py md5
  differs from the pin by design (frozen 1e3901c bytes;
  the regen script hashes the pinned commit).
- Hygiene: no em/en dashes anywhere in the fix diff; no
  pyc_refused key left in code (the plan doc names it only
  as the old key).

## Findings

### F1 (Medium): _check_entry_pyc is unreachable for a pre-existing .pyc; the docs present it as the operative B1 control

- Files: tests/realistic/launch_y13.py:188-224 (module-top
  scan, exits 2 at line 221 on any .pyc),
  tests/realistic/launch_y13.py:806-848 (check_manifest,
  refuses any .pyc at line 843),
  tests/realistic/launch_y13.py:1107-1110 (main() order:
  check_marker, check_manifest, _check_entry_pyc,
  _scan_ship), tests/realistic/launch_y13.py:880-947
  (_check_entry_pyc), tests/realistic/launch_y13.py:35-46
  (docstring check 4), tests/realistic/launch_y13.py:950-958
  (_scan_ship docstring), tests/realistic/codex-y5/SHIPPED.md:12-14,
  improvements/worker-y13-codex-y5-live-plan.md:616-633
  (B1 bullet) and :660-663 (B4 bullet).
- The module-top scan runs at import and exits 2 on ANY
  .pyc in the ship dir. main() then runs check_manifest,
  which also exits 2 on any .pyc, BEFORE _check_entry_pyc
  is called. So the out-of-process marshal comparison can
  never observe a pre-existing .pyc; the only .pyc it could
  ever see is one planted mid-run between the top scan and
  its own call (a TOCTOU window; the launcher's own
  check_marker/check_manifest subprocesses are git only
  and write no .pyc). The docs in all three surfaces
  describe it as the control that "refuses on mismatch,
  and deletes ONLY the matching entry .pyc files" (plan
  B1; SHIPPED.md lists the "entry-.pyc out-of-process
  check" among the launch-time checks; launcher docstring
  check 4). The B1 re-test as specified in the Y13g log
  ("tested THROUGH the launcher check (refuses, no
  marker)") cannot discriminate _check_entry_pyc from the
  top scan: it passes via the coarse refusal without ever
  exercising the marshal comparison. The _scan_ship
  docstring compounds it by saying the empty __pycache__
  is a leftover "whose .pyc files _check_entry_pyc just
  deleted"; in practice the empty dir comes from the -m
  guard's deletion, not from _check_entry_pyc.
- Severity: Medium. Not a security hole (refusal is
  fail-closed either way, exit 2, no marker, no exec),
  but ~70 lines of dead code presented as the control,
  and the documented mechanism does not match the code
  flow. A future worker that "fixes" the top scan to
  exempt entry .pyc on the strength of these docs would
  silently promote _check_entry_pyc to sole control.
- Proposed fix (pick one): (a, minimal, recommended)
  rewrite the three doc surfaces to name the module-top
  scan + check_manifest as the operative refusal and
  _check_entry_pyc as TOCTOU defense-in-depth only, fix
  the _scan_ship docstring to credit the -m guard for the
  empty __pycache__, and adjust the B1 re-test to assert
  the top-scan refusal (exit 2, "tampered ship dir" /
  "planted bytecode") rather than a _check_entry_pyc
  refusal; or (b) exempt entry .pyc from the LAUNCHER's
  top scan and check_manifest so _check_entry_pyc
  adjudicates (verify-then-delete) as documented. Do NOT
  narrow the RUNNER's scan: the runner imports run_live,
  so a forged run_live .pyc would execute at import.

### F2 (Medium-Low): guard stem asymmetry, 2 stems in the runner vs 3 in the launcher; a run_live .pyc is unhealed in the runner path

- Files: tests/realistic/run_codex_y5.py:113,139,163
  ("the two entry .pyc files"), tests/realistic/run_codex_y5.py:132-150
  (_ENTRY_PYC_NAMES and _entry_pyc_paths cover only
  run_codex_y5 / launch_y13),
  tests/realistic/run_codex_y5.py:598-602 and :619-628
  (_verify_manifest dir exemption uses the 2-stem,
  current-tag-only _ENTRY_PYC_NAMES),
  tests/realistic/launch_y13.py:141-160 (_ENTRY_STEMS
  includes run_live), tests/realistic/launch_y13.py:880
  (_check_entry_pyc covers all 3 stems).
- run_live.py has no guard (frozen base), so a
  `python3 -m run_live` or `import run_live` probe in the
  ship dir leaves a run_live .pyc behind with nothing to
  delete it. The runner's guard cannot heal it (2 stems);
  the launcher's guard would delete it, but only when the
  launcher itself is invoked via -m (as a script its guard
  never runs, and its top scan then refuses). The only
  other healer, _check_entry_pyc, is unreachable (F1). So
  a run_live -m probe bricks the ship until manual
  deletion or a -m invocation of a guarded file, which is
  exactly the B4 failure mode the fix claims to close.
  Secondary: _ENTRY_PYC_NAMES recognizes only the current
  cache tag while the guard deletes every cache-tag
  variant, so a stale-tag entry .pyc fails the dir
  exemption and adds a spurious "unexpected directory"
  line next to the "bytecode" refusal (same refusal,
  noisier reason list).
- Severity: Medium-Low. Narrow trigger (requires a -m /
  import probe of run_live specifically), but it is the
  one stem the design says is "NEVER exempt" while the
  launcher simultaneously treats it as a deletable entry
  .pyc.
- Proposed fix: add run_live to the runner's guard stems
  and to _ENTRY_PYC_NAMES (the file is still refused as
  bytecode by _verify_manifest, so "NEVER exempt" stays
  true at the file level; only the dir-exemption error
  list changes), update the runner docstring "two" to
  "three", and document the residual: a -m run_live probe
  leaves a .pyc that the next guarded -m invocation heals
  or that must be deleted by hand. Or document run_live
  as explicitly unguarded with the manual-deletion remedy
  in SHIPPED.md.

### F3 (Medium-Low): bundled value-flags -c/-m are misparsed; the plan claims "bundled/attached forms" are handled

- Files: tests/realistic/launch_y13.py:404-465
  (_PY_NO_VALUE at :404, _python_executes_runner at
  :407-465), tests/realistic/run_codex_y5.py:3819-3880
  (identical block),
  improvements/worker-y13-codex-y5-live-plan.md:646-650
  (B3 bullet: "bundled/attached forms").
- _python_executes_runner handles attached -c/-m only
  when the flag is the first character after "-"
  (tok.startswith("-c") / ("-m")), and bundled no-value
  clusters only when every character is in _PY_NO_VALUE
  (which excludes c and m). A cluster ending in c or m
  falls through to the generic unknown-flag skip, so the
  following value token is misread as the script
  candidate. Probes on the AST-extracted tokenizer
  (both copies share the code, so one probe covers both):
  `python3 -uc exec(open('run_codex_y5.py').read())`
  returns False (want True); `python3 -Bc
  exec(open('run_codex_y5.py').read())` returns False
  (want True); `python3 -um pkg.run_codex_y5` returns
  False (want True); `python3 -Bum pkg.run_codex_y5`
  returns False (want True). `-um run_codex_y5` (bare
  module) is caught only accidentally via the
  bare-module-name leg, not via -m parsing. The copies
  are consistent with each other (AST-identical); the gap
  is shared code vs the doc claim.
- Severity: Medium-Low. Narrow form (requires deliberate
  flag bundling with a value flag last), and ports +
  flock backstop applies, but the runner-quiet check is
  the slot guard and the doc claim is broader than the
  code.
- Proposed fix: in _python_executes_runner (both copies,
  keep them identical), when a bundled short-flag token
  ends in c or m, consume the next token as the -c/-m
  value and parse it accordingly; add the four probe
  cases above to the verifier's battery. If the fix is
  deferred, narrow the plan B3 bullet to "attached -c/-m
  and bundled no-value flags" and record bundled -c/-m
  as a known gap.

### F4 (Low-Medium): the -c limit is stated in the plan, contradicted in the code docstring, and absent from SHIPPED.md and the launcher docstring

- Files: tests/realistic/launch_y13.py:379-395
  (_c_code_executes_runner docstring),
  tests/realistic/run_codex_y5.py:3794-3810 (identical),
  improvements/worker-y13-codex-y5-live-plan.md:658-659
  (B3 LIMIT), tests/realistic/codex-y5/SHIPPED.md (no
  mention of the -c / os.system limit),
  tests/realistic/launch_y13.py:59-75 (docstring check 7,
  no limit stated).
- The code docstring says a nested 'python3
  run_codex_y5.py', "e.g. via os.system or a -c inside
  -c, is caught by the same recursive parse". The plan
  B3 bullet states the opposite as a documented LIMIT:
  "a nested os.system/exec inside -c code beyond exec(/
  eval( is not caught; ports + flock backstop." Probe
  confirms the plan: `python3 -c "os.system('python3
  run_codex_y5.py')"` returns False, because shlex keeps
  os.system('...') as a single token and the recursive
  parse never sees a python token. The first leg of
  _c_code_executes_runner only fires when the -c string
  itself starts with a bare shell command, which as Python
  code is a SyntaxError and can never execute. SHIPPED.md
  and the launcher docstring check 7 do not state the
  limit at all.
- Severity: Low-Medium. Behavior matches the plan's
  stated limit (no hole beyond the documented one); the
  defect is the code docstring claiming the opposite.
- Proposed fix: rewrite the _c_code_executes_runner
  docstring in both copies to state the plan's LIMIT
  verbatim and drop the os.system example; add one line
  stating the limit to SHIPPED.md and to the launcher
  docstring check 7.

### F5 (Low): _proven_no_body docstring contradicts itself on the eval_error key

- File: tests/realistic/run_codex_y5.py:1062-1082.
- The first paragraph defines proof as "the diagnose
  carries NO eval_error key at all", but the code checks
  `diag.get("eval_error") is not None`, which also treats
  a present-but-None eval_error as proof. The Y13g note
  later in the same docstring states the `is not None`
  rule correctly. Unreachable in practice today (run_live
  sets non-empty strings or omits the key), but the
  definition paragraph is stale relative to the code it
  documents.
- Proposed fix: change "carries NO eval_error key at all"
  to "carries no non-None eval_error (key absent, or
  present with value None)".

### F6 (Low): runner docstring Usage lines show the launcher without -P

- File: tests/realistic/run_codex_y5.py:103,105
  (`Y13_GO=1 python3 launch_y13.py all` and `...
  launch_y13.py 01 02`, no -P).
- Every other surface requires -P: SHIPPED.md:41
  (`python3 -P launch_y13.py`), the launcher docstring
  ("Run with -P"), the regen docstring, and the runner's
  own SCRIPT FORM ONLY block a few lines below (:109,
  `python3 -P run_codex_y5.py`). The Usage lines are the
  odd ones out.
- Proposed fix: add -P to both Usage lines.

### F7 (Low): plan B2 bullet overstates check_manifest

- Files: improvements/worker-y13-codex-y5-live-plan.md:641-643
  ("check_manifest refuses any planted file"),
  tests/realistic/launch_y13.py:806-848
  (check_manifest), tests/realistic/launch_y13.py:28-34
  (docstring check 3, correctly scoped).
- check_manifest refuses only a top-level .py not in the
  manifest, any .pyc, and any symlink. A planted .py in a
  subdirectory (e.g. codex-y5/evil.py) or a planted
  non-.py file is NOT refused by check_manifest; it is
  refused later by _scan_ship. The launcher docstring's
  parenthetical scopes this correctly; the plan bullet
  does not.
- Proposed fix: reword the plan bullet to "check_manifest
  refuses a planted top-level .py, any .pyc, and any
  symlink; _scan_ship refuses any other planted file".

### F8 (Low): runner preflight comment claims a plain codex process "only warns", but the runner has no warning branch; _is_codex_process is dead code in the runner

- Files: tests/realistic/run_codex_y5.py:3999-4017
  (_is_codex_process defined, never called in this file),
  tests/realistic/run_codex_y5.py:4150-4165 (preflight
  loop: runner-refuse and codex-refuse branches only),
  tests/realistic/launch_y13.py:584,709-717 (the warning
  branch lives only in the launcher).
- The preflight comment says "a plain codex process only
  warns (see the launcher, same rule)", but in the runner
  a plain codex process is silently ignored, neither
  warned nor refused. _is_codex_process is kept in the
  runner only "so the shared block stays identical" (its
  docstring is honest about that). The behavior is
  defensible (warning is the launcher's job; preflight is
  defense-in-depth), but the comment misdescribes this
  file's behavior.
- Proposed fix: reword the preflight comment to "a plain
  codex process is ignored here; the launcher warns on
  it" (or add the warning branch to preflight); keep the
  function for block identity.

### F9 (Low): Amend 3 "scan JSON" is unscoped; only the runner emits JSON

- Files: improvements/worker-y13-codex-y5-live-plan.md:676-678
  ("the scan JSON reports {...}"),
  tests/realistic/run_codex_y5.py:248-254 (JSON refusal),
  tests/realistic/launch_y13.py:215-221 (plain-text
  refusal: "[launch_y13] REFUSED: tampered ship dir ...").
- The plan bullet reads as if both scans emit the JSON
  form; only the runner does. The launcher's scan prints
  plain text with the same kind labels. Nothing parses
  the launcher's refusal, so this is doc scoping only.
- Proposed fix: scope the plan bullet to "the runner's
  scan JSON", or note the launcher's plain-text form
  alongside it.

### F10 (Trivial): CODEX comment drift inside the "identical" tokenizer block

- Files: tests/realistic/run_codex_y5.py:4019-4024 vs
  tests/realistic/launch_y13.py:604-608.
- The runner's comment above CODEX_REFUSE_MARKERS carries
  two sentences the launcher lacks ("A plain "codex"
  match with none of these is warning-only (a Codex CLI
  may be doing unrelated work)."). Comment-only; the
  values and behavior are identical (AST-verified).
- Proposed fix: copy the two sentences into the
  launcher's comment, or delete them from the runner's,
  so the block stays text-identical apart from the
  sync-direction notes.

## Notes (not findings)

- N1: -P is absent from _PY_NO_VALUE
  (launch_y13.py:404, run_codex_y5.py:3819) and from the
  _python_executes_runner flag list, but `python3 -P
  run_codex_y5.py` is still caught correctly via the
  generic unknown-flag skip. Add -P to the documented
  flag list when F3 is fixed; no behavior change needed.
- N2: The Y13g log's "12 functions" count for the
  tokenizer block understates the shared surface (17
  names including constants); the AST comparison above
  covers all 17.

## Scope note

This review covers the fix diff only. The Y13f code
outside the diff was used as context only. Behavioral
holes that need live or adversarial probing (as opposed
to design/doc consistency) belong to the redteam and the
independent verifier; the probe results above are
Council 1's own checks on the tokenizer behavior, run on
AST-extracted functions, not on the live ship.
