# Council Voice 3: Y14b re-stage review (re-stage hygiene only)

Scope: commit f732d6a on todolist-push (Y14b: re-stage batch3 runner from
suite HEAD 1d23532 + H2 tokenizer fix). Reviewed ONLY the re-stage diff,
not the whole runner. t10 translation faithfulness is Council 1; H2 fix
correctness and gate/preflight integration is Council 2; this paper
covers suite HEAD, diff scope, plan consistency, N/A honesty, Y15
limits, and log evidence.

Reviewer: Council Voice 3 (independent, no subagents). Review window:
21:13-21:17 +07, 21/11/2026. Method: every claim below was checked with
git/grep/python against the repo at HEAD a46d503 (f732d6a is its parent);
Y14b's log claims were re-run, not trusted. All commands and outputs are
recorded in the Evidence section.

## Verdict: AMEND

The re-stage itself is sound: the suite staging, the diff scope, the H2
copy, and the N/A disclosures all verify. The amendments are plan and log
wording plus one ship-time procedure item. No code change is needed, and
nothing below is a hole in the diff itself, so this is AMEND, not BLOCK.
But it is not GO: the plan as committed contains two live instructions
that contradict the re-stage (L413 still stages ed78e83; L427-428 still
describes the old pgrep launch gate), and the ship-time md5 substitute
has no recorded hashes, command, or expected values, so it is currently
a promise, not a checkable step. Ship must wait for these fixes; the
fixes are small and listed with exact file and line in Fixes F1-F7.

## 1. Suite HEAD claim: CONFIRMED (with one wording correction, F7)

- `git diff --name-status ed78e83..1d23532 -- tests/realistic/clone1-batch3/`
  shows exactly 2 files: t10-music-player/README.md and
  t10-music-player/check.mjs. No other file under the suite dir changed.
- t01-t09 check.mjs blob hashes are identical between ed78e83 and
  1d23532 (checked per file with `git rev-parse <commit>:<path>`; all 9
  IDENTICAL).
- Every other file under the suite dir is byte-identical across the
  range, including all fixture.html files, lib/browser.mjs,
  lib/server.mjs, run_all.mjs, and results.json (blob comparison over
  the full file list; zero DIFFERS lines).
- The single commit 1d23532 itself touches only those 2 files
  (+300/-37: README +97, check.mjs +240/-37, 167 to 353 lines).
- Caveat (wording, F7): the range ed78e83..1d23532 overall touches 7
  files, not 2. The other 5 are outside the suite (coord/clone1.md,
  coord/clone2.md, docs/clone1-batch5-firefox-20261121.md,
  docs/research/2026-11-21-atspi-probe-extended.md,
  improvements/worker-y10-batch3-fix-log.md). The log's sentence "Diff
  ed78e83..1d23532 touches ONLY t10..." is true only when scoped to
  tests/realistic/clone1-batch3/. The re-stage stages only the suite
  dir, so the other 5 files are irrelevant to the runner, but the
  sentence as written is overbroad.

## 2. Diff scope claim: CONFIRMED

- `git diff 5a2b69d f732d6a --stat`: run_batch3.py +452/-35, plus the
  plan (+95/-25) and the new log (101 lines). Exactly 3 files.
- Function-body comparison (old file vs new file, sliced per def):
  35 old functions, 41 new. Removed: none. Added: exactly the 6 H2
  helpers (_script_basename_is_runner, _is_python_token, _argv_tokens,
  _is_runner_cmdline, _ppid_of, _scan_other_runners). Changed bodies:
  exactly 3: run_b3_t10 (185 to 454 lines), run_preflight (224 to 232
  lines, re-check block only), launch_gate (98 to 98 lines, sweep
  replaced). run_one is untouched; no other test function changed.
- Header/imports: module docstring suite HEAD ed78e83 to 1d23532 with
  updated t10 description, plus `from pathlib import Path`. No other
  module-level constant changed except the new CODEX_REFUSE_MARKERS.
- H2 copy check against the Y13f source (run_codex_y5.py working
  tree): _script_basename_is_runner, _is_python_token, _argv_tokens,
  _ppid_of byte-identical; CODEX_REFUSE_MARKERS byte-identical;
  _is_runner_cmdline identical except its docstring tail, which records
  this Y14 application instead of the "must apply" note (by design, and
  the log says so). _scan_other_runners() is new, as claimed.
- Re-ran Y14b's probes from /tmp (scripts still present): H2 probe
  21/21 PASS (14 unit synthetic cmdlines + 7 live /proc cases),
  transcription 0 failures (68 ordered assert alignments), launch-gate
  dry run 0 failures (4/4). Re-ran py_compile (OK) and import (OK, 10
  tests b3-t01..b3-t10). Sleep counts in run_b3_t10 match the log:
  0.7x3, 0.5x1, 0.4x1, 0.35x10. exact_zero_next: 1 definition + 3 call
  sites (lines 1555, 1690, 1819), matching the plan. The old
  supplementary D1 probe is gone; only a NOTE comment remains (line
  1909-1914) explaining the removal.
- Observations (not fixes):
  - (a) The H2 tokenizer does NOT exist in run_codex_y5.py at HEAD
    cb26d1d (0 hits); it is entirely uncommitted Y13f working-tree
    work, and the working tree is still dirty. The "copied verbatim"
    provenance therefore cannot be re-verified against any commit.
    This does not weaken the runner: the logic is now committed in
    f732d6a itself, and I verified the copies match the current
    working tree. It only means the provenance anchor is the log's
    word plus the current tree, and the log does record that honestly
    ("uncommitted at copy time").
  - (b) _ppid_of differs from the launch_y13.py copy (Path.read_text
    plus broad `except Exception` vs binary read plus narrow except)
    but matches the run_codex_y5.py working-tree copy. Functionally
    equivalent (same parse after the last ")"). No action.
  - (c) The pre-re-stage runner content equals commit 70061e2
    ("y14: apply redteam 2 AMEND fixes H1-H5 + M1"): `git diff
    70061e2 5a2b69d -- tests/realistic/run_batch3.py` is empty, and
    the blob at both is 72d8eb6. The log's "at 70061e2" is therefore
    substantively correct, though 70061e2 is a commit hash, not a blob
    hash (see F7 wording).

## 3. Plan consistency: MOSTLY CONFIRMED, 6 stale or overstated lines (F1-F6)

Checked: improvements/worker-y14-batch3-live-plan.md as changed by
f732d6a.

- Y12 verdict: NO contradiction. The plan records it accurately
  (section "Y12 headless verdict", L465+): SOUND WITH NOTED DEFECTS,
  t10 DEFECT D1 (executed, minor, narrow), the exact-zero remedy, and
  the "Do NOT run live on the ed78e83 copy once Y15's fix has landed"
  instruction. I verified the Y12 log (897ca17) independently: same
  verdict, same D1 wording, same remedy (P2 must FAIL + 3x 10/10).
- Redteam-2 AMEND condition: SATISFIED. The condition
  (worker-y14-redteam2-verdict.md, L237-244) is: "conditional on the
  staged suite still being ed78e83 at slot time... re-verify the
  staging md5s against the then-current main HEAD; if Y15 has landed,
  re-stage, update the t10 translation to Y15's checker, and drop or
  keep the D1 probe only as a duplicate diagnostic." Y14b did exactly
  that: re-staged to 1d23532, rewrote the t10 translation, dropped the
  D1 probe with a stated reason (superseded by the real frozen-Next
  steps).
- t10 section numbers match the new checker (spot-checked against
  check.mjs at 1d23532): three-point advancing gain >= 2 per 350 ms
  sleep with the 2-11 bound on the middle read (checker L114-115,
  L123, L205-206, L210); two-point resume reads 2-11 plus second gain
  >= 2 (checker L147, L155-156, L230, L237-238, L311, L318-319);
  wrap gates posBefore >= 2 (checker L261, L290); sampler min > 2 or
  min >= posBefore fails (checker L98, L191). Runner bounds match
  (2 <= x <= 11 checks in run_b3_t10).
- Stale or overstated lines (fixes F1-F6 below):
  - F1: L413 still says the suite is "copied from main ed78e83,
    md5-verified". This is the one load-bearing stale reference: it
    directly contradicts the re-stage section and the Y12 section's
    own do-not-run-on-ed78e83 instruction.
  - F2: L36-37 still says "Y12 is independently verifying the merged
    suite headless. If Y12 reports a defect before my slot opens..."
    in the present tense, while L465 and L617 record that Y12 HAS
    reported. Internal tense contradiction.
  - F3: L427-428 launch gate still describes the OLD pgrep sweep
    ("sweep for stale geckodriver processes by PID (pgrep, parent
    PID, cmdline...)"). The code now uses the /proc tokenizer scan.
    A slot runner following L427-428 would run the wrong check.
  - F4: L520 (re-stage section) says the H2 helpers are "all
    byte-identical to run_codex_y5.py". The _is_runner_cmdline
    docstring differs (see section 2). The log qualifies this; the
    plan does not.
  - F5: the Y12 "Consequence for this live run" paragraph (L479-487)
    still describes the min <= 2 runner plus the supplementary D1
    probe as the current state. It is superseded by the re-stage and
    needs a superseded marker, or the probe paragraph will be read
    as a live instruction.
  - F6: L269 cites "check.mjs L103-106" for the seek 85-100 assert.
    In the new 353-line checker that assert is at L169 (old checker
    had it at L103-106).

## 4. N/A honesty (no manifest, no STEP_COUNTS audit): CONFIRMED as stated; substitute judged ADEQUATE only if F6/F7 procedure is added

- Verified by grep (counts, not eyeballing): 0 hits for
  _manifest_entries, --verify-manifest, or MANIFEST in
  tests/realistic/run_batch3.py and tests/realistic/run_live.py; 0
  hits for STEP_COUNTS, _audit_count, or AUDIT in either file. The
  runner has no manifest mechanism and no STEP_COUNTS audit mechanism.
  The log and plan state this honestly and do not paper it over.
- Judgment on the "verified by md5 against git HEAD at ship time"
  substitute: the staging half is STRONGER than md5, because I
  reproduced it at git blob level (section 1). The ship half is
  currently a promise, not a procedure: no md5 values, no command, and
  no expected hashes appear anywhere in the plan, the re-stage log, or
  the live log (grep for 32-hex strings: zero hits), and the only plan
  mention of md5 is the stale L413 (F1). A tampered suite copied to
  the laptop would not be caught by anything in the runner.
- Is the missing manifest itself a gap that must be fixed before the
  slot? NO. Adding a manifest is new design work beyond a re-stage,
  and redteam-2's AMEND condition explicitly scoped the fix to
  re-stage plus t10 update; demanding a manifest now would contradict
  redteam-2's own verdict. The re-stage does not make the tamper
  exposure worse than the Y14 original that redteam-2 already
  AMEND-approved. What IS required before the slot is F6: pin the
  ship-time md5 procedure in the plan (exact command, exact file set,
  expected git blob hashes), and record the actual command output in
  the live log at ship time. That makes the substitute checkable.
  Dissent recorded: a stricter reader could still call the absent
  manifest a BLOCK on tamper grounds; I do not, because the slot is a
  single live run on a handed-over machine, the suite is verified at
  stage time by git, and the ship check (once pinned) covers the copy
  step. If the ship check is not pinned, my verdict would become
  BLOCK at ship time, not now.

## 5. Y15 limits (R1/R2/R3b): CONFIRMED, correctly reflected, no change to what the live run must prove

- Verified against the t10 README at 1d23532 (Notes section) and the
  Y15 log (commit 3b50e94, on main): round-6 redteam BLOCK rests on
  exactly R1 (slow clock 170 ms per tick, 0.59x, escapes; advancing
  reads 5/7 vs correct 8/12), R2 (wrap branch only stops the timer;
  no advancing check after the playing wrap; next playlist click
  restarts the timer and masks it), R3b (clock 10x in the tail of
  each advancing window; later read gain-only with no absolute upper
  bound; advancingLater 40-41 vs correct 12). Council APPROVE.
  Landed per the pre-set stopping rule (round 6 is the LAST fix round;
  land regardless unless P2-must-FAIL, 3x 10/10, or a README
  contradiction breaks). The plan's summary matches the README
  wording: slow-side clock 0.6x-1.0x not distinguished, later
  advancing read gain-only with no upper bound, no advancing check
  after the playing wrap.
- The plan correctly states these are documented limits, not gates,
  and that the live run is the real test. They do not change what the
  live run must prove: the live run executes the same checker on Zen
  and must prove the fixture passes it (exact-zero resets, advancing
  clocks, frozen resumes). The limits are checker blind spots; the
  live run cannot prove what the checker cannot see, and the plan
  does not claim otherwise. No contradiction found.

## 6. Log evidence: CONFIRMED, no bare "done"

- improvements/worker-y14b-restage-log.md (101 lines in f732d6a, plus
  12 lines appended in a46d503 recording council/redteam spawn):
  timed entries 21:06-21:13 +07, baseline hashes (ed78e83, 1d23532,
  70061e2, f48b54c), probe counts (H2 21/21, transcription 68
  asserts, gate dry 4/4), diff stat (+452/-35), commit hash f732d6a,
  ls-remote verification. No bare "done" anywhere.
- I re-ran all three /tmp probe scripts and the compile/import
  checks myself (section 2); all green. No stray run_foo.py
  processes left (pgrep hit was my own shell command string).
- The commit contains exactly its 3 claimed files, no em dash or en
  dash in the diff (0 hits), no ydotool mention (0 hits), and
  f732d6a is reachable on origin/todolist-push (ls-remote shows
  a46d503, its child). The claim "Only my 3 files staged; Y13f's
  uncommitted working-tree changes untouched" is consistent with the
  current tree (run_codex_y5.py and launch_y13.py are still modified
  in the working tree, uncommitted).
- Minor wording imprecisions in the log (fold into F7, not separate
  fixes): "all 5 functions IDENTICAL (docstring tail ... differs)"
  contradicts itself in one sentence (the qualification is present,
  the headline overstates); "verified by git diff --stat" is cited as
  the method for byte-identity of t01-t09 (diff --stat shows which
  files changed, not byte identity; the claim itself is true, I
  verified it by blob hash).

## Fixes (all AMEND, in priority order)

- F1 (plan L413, load-bearing): change "suite copied from main
  ed78e83, md5-verified" to "suite copied from main 1d23532,
  md5-verified". The ed78e83 reference must not survive anywhere as
  a live staging instruction.
- F2 (plan L36-37): reword the Y12 sentence to past tense and point
  at the verdict section, e.g. "Y12 verified the merged suite
  headless (see 'Y12 headless verdict' below); its D1 defect is
  fixed by Y15 in 1d23532, which this re-stage adopts."
- F3 (plan L427-428): rewrite the launch-gate bullet to describe the
  code as re-staged: the /proc tokenizer scan (_scan_other_runners)
  instead of the pgrep -f sweep. Keep the rest of the A4 checks
  (Zen alive, Marionette 2828, ports 8771/4452 and predecessors
  free, LIVE_SLOT_OK=1, slot ownership).
- F4 (plan L520): qualify the byte-identical claim: "all
  byte-identical to run_codex_y5.py except the _is_runner_cmdline
  docstring tail, which records this Y14 application instead of the
  'must apply' note (logic identical)."
- F5 (plan L479-487): mark the "Consequence for this live run"
  paragraph SUPERSEDED by the re-stage (min <= 2 runner and
  supplementary D1 probe no longer current; Y15 checker plus the
  re-stage section govern).
- F6 (plan L269 and L534): replace the stale seek citation
  "check.mjs L103-106" with "check.mjs L169" (new checker), and
  expand L534 into a pinned ship-time procedure: the exact md5
  command, the exact file set (at minimum every check.mjs, every
  fixture.html, lib/, run_all.mjs under tests/realistic/clone1-batch3/
  plus run_batch3.py), and the expected git blob hashes (or md5s) for
  those files at 1d23532, with the actual command output to be pasted
  into the live log at ship time. Until F6 is done, the md5
  substitute is a promise, not a check.
- F7 (log, wording only): qualify L14 "Diff ed78e83..1d23532 touches
  ONLY t10..." with "within tests/realistic/clone1-batch3/"; fix
  L59 "all 5 functions IDENTICAL (docstring ... differs)" to "all 5
  functions identical in logic (docstring tail of _is_runner_cmdline
  differs by design)"; clarify L18 "run_batch3.py at 70061e2" as
  "run_batch3.py as at commit 70061e2 (blob 72d8eb6)".

## Uncertainty and dissent (recorded honestly)

- I could not verify that the run_codex_y5.py working tree was
  byte-identical at Y14b's copy time (21:09 +07) to what it is now;
  I verified the copies match the CURRENT tree. If Y13f edited its
  tokenizer between the copy and now, the provenance check would
  silently pass against the wrong version. The committed copy in
  f732d6a is what the slot will run, so this does not affect the
  verdict; it only limits the provenance claim.
- The transcribe script's 68-assert alignment is Council 1's
  territory (translation faithfulness). I re-ran it (0 failures) and
  spot-checked the checker's numbers against the plan and the runner,
  but I did not independently re-derive all 68 alignments.
- The Y15 log lives on main (3b50e94), not on todolist-push; I read
  it via `git show 3b50e94:...`. Its R1/R2/R3b and stopping-rule
  claims match the plan's summary.
- One council-3 dissent from myself, recorded: the absent manifest
  (section 4) is a real tamper-exposure gap. I judge it AMEND-level
  (pin the ship md5 procedure) rather than BLOCK, for the reasons
  given. If Council 1, Council 2, or redteam finds a tamper path
  that the ship md5 check cannot cover, that finding should upgrade
  this to BLOCK.

## Evidence (commands run, all on the VM, repo ~/workspace/computer-use-wayland)

- git show f732d6a --stat; git log --format parent; git diff
  --name-status ed78e83..1d23532 (full range: 7 files) and scoped to
  tests/realistic/clone1-batch3/ (2 files); per-file blob-hash
  comparison for t01-t09 check.mjs and the full suite file list
  (all other files identical); git show 1d23532 --stat.
- git diff 5a2b69d f732d6a --stat; python function-body slicer over
  both run_batch3.py versions (35 vs 41 defs, 0 removed, 6 added, 3
  changed bodies); python byte-compare of the 5 H2 functions plus
  CODEX_REFUSE_MARKERS against run_codex_y5.py working tree and
  launch_y13.py; git diff 70061e2 5a2b69d -- run_batch3.py (empty).
- grep -c for manifest/audit terms in run_batch3.py and run_live.py
  (all 0); grep exact_zero_next (1 def + 3 sites); grep D1 probe
  (NOTE comment only, L1909-1914).
- Re-runs: python3 /tmp/y14b-h2-probe.py (21 PASS, 0 failures);
  python3 /tmp/y14b-transcribe.py (0 failures); python3
  /tmp/y14b-gate-dry.py (0 failures); python3 -m py_compile
  run_batch3.py (OK); import run_batch3 (OK, 10 tests).
- Plan/log reads: full f732d6a diff of the plan and log; Y12 log
  (worker-y12-batch3-verify-log.md, verdict + D1 + remedy);
  redteam-2 verdict (worker-y14-redteam2-verdict.md L237-244
  condition); Y15 log via git show 3b50e94 (round-6 redteam BLOCK
  R1/R2/R3b, stopping rule L210-215); t10 README at 1d23532 (Notes
  L82-L142); new check.mjs at 1d23532 (seek L169, bounds L115/L147/
  L156/L206/L230/L238/L311/L319, gains L114/L123/L155/L205/L210/
  L237/L318, wrap gates L261/L290).
- Hygiene: git show f732d6a has 0 em/en dash hits and 0 ydotool
  hits; commit has exactly 3 files; git ls-remote origin
  todolist-push shows a46d503 (child of f732d6a).

Timings: review 21:13-21:17 +07 (14:13-14:17 UTC), 21/11/2026.
No personal info in this paper. No em dash or en dash in this paper.
