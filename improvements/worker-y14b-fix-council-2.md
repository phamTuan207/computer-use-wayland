# Council Voice 2: Y14b fix-pass review, H2 gate fix only

- Scope: the FIX DIFF ONLY, commit 8bee524 on todolist-push, file
  tests/realistic/run_batch3.py, H2 gate items only: (1) the -m
  module-form branch and the -c import branch in _is_runner_cmdline;
  (2) the _is_codex_executor anchor used by _scan_other_runners;
  (3) the plain-codex warning in launch_gate via
  _plain_codex_processes and the stale-comment fix; (4) the run_one
  per-test re-scan returning INFRA. Plus ebe5853 (log hash record
  only). Out of scope, not re-reviewed here: the H4 now-playing
  reorder, the L1 int() removal, the M1 _verify_served_fixture, and
  all plan/log wording (Council 3 F1-F7). Those verdicts already
  exist and this paper does not touch them.
- Verdict: AMEND. All four H2 items are correct, verified live by
  re-running the probes (45/45, 4/4, plus 25/25 in my own extra
  probe), and no regression on any case the predecessor verified.
  The single required fix is docstring-only, in the
  _is_runner_cmdline docstring: its "identical logic" sync claim is
  now false (the siblings were not fixed), and two residuals need
  recording (multi-import second name, run-nested* extensionless).
  No behavior change is required. The sibling -m gap is FLAGGED to
  Y13f, not required of Y14b.
- Reviewer: Council Voice 2 (independent review, no subagents
  spawned, no live Zen driving, no ydotool).
- Timing (Asia/Ho_Chi_Minh): review 21:33-21:36, paper written
  21:37-21:44, committed same evening. VM clock is UTC; +07 times
  below are UTC+7.

## 0. Diff identity: a scope note worth recording

The brief says "commit 8bee524 vs its parent f732d6a". Strictly,
8bee524's parent is 431b2a9 (Y13f hash record), and f732d6a is the
re-stage commit, an ancestor. This does not change the scope: no
commit between f732d6a and 8bee524 touched run_batch3.py
(`git log f732d6a..8bee524 -- tests/realistic/run_batch3.py` shows
only 8bee524), and the two diffs are byte-identical
(md5 dee5bad9cc1e954804950fe74cb3b93c for both
`git diff f732d6a 8bee524` and `git diff 431b2a9 8bee524` on this
file). So "fix diff" is unambiguous. ebe5853 touches only
improvements/worker-y14b-restage-log.md (hash record); its claims
are verified in section 8.

## 1. The -m fix matches Council 2 Fix 1 exactly (check 1): PASS

Council 2 Fix 1 (paper b445257) specified, after the "prev == -c"
branch:

    if prev == "-m" and (base.startswith("run_")
                         or base == "hand_drive_e1"):
        return True

The fix, run_batch3.py:2301-2303, implements exactly this, plus
the `i > 0` guard the spec's placement assumes:

    if i > 0 and tokens[i - 1] == "-m" and (
            base.startswith("run_") or base == "hand_drive_e1"):
        return True

The guard matters: without it, i == 0 would read tokens[-1]
(Python wraparound, the last token) as "prev". The fix has it.
The loop was restructured (old `if not _script_basename_is_runner:
continue` became `if _script_basename_is_runner: ...; continue`
with the new branches in the else path). I diffed the old function
at f732d6a against the new one: every pre-fix branch is preserved
in the same order (argv[0], python token, -c first word, flag
branch, bash/sh run-nested branch). No pre-fix case regressed:
all 21 original H2 probe cases still pass inside the 45/45 rerun
(section 5).

Spec cases verified live (H2 probe + my extra probe, section 5-6):
"python3 -m run_batch3" True, "python3 -u -m run_batch3" True
(the -u case reaches the branch because prev is "-m", not "-u"),
"python3 -m hand_drive_e1" True, "python3 -m run_batch3 all" True
(extra args), live "python3 -m run_foo" dummy caught by
_scan_other_runners. Regressions held: "python3 -m pytest
run_batch3.py" False, "python3 -m pytest" alone False, "-c code
path arg" False, mention-only False.

## 2. The -c import branch (check 2): PASS, one new residual

The branch, run_batch3.py:2304-2307, accepts a bare runner module
name after "import" or "from" in the -c words, with trailing
`; , ( )` stripped. Verified True: "import run_batch3;
run_batch3.main()", "from run_batch3 import main",
"import run_foo, run_bar" (first name), "from x import run_foo",
"import hand_drive_e1". Verified False on realistic non-runner
-c strings: "import sys", "import os, sys", "from os import path",
"import runpy", "print('run_foo')", "print(\"import run_foo\")"
(quoted mention does not fire: the word before run_foo is
`print("import`, not `import`), and the -c code path arg case.

New residual, found by my extra probe (not in the fix log): a
comma-list import with the runner NOT first misses.
"python3 -c 'import os, run_foo'" returns False, because only the
token immediately after "import" is checked; the second name's
prev is "os,", not "import". "import run_foo, os" (runner first)
returns True. No launcher uses a comma-list -c import (grep over
the repo finds no `-c "import run_` launcher form at all), so
this is the same class as double-nested -c: a recorded residual,
not a required behavior fix. It must be recorded in the docstring
(see Required fix, item 2), because the branch as specified
("a bare runner module name after import/from") reads as if any
name in the import list qualifies.

Note on scope of the match: the branch matches ANY run_* module
name, not just known runners ("import run_batch3x" returns True).
That is consistent with the -m spec (same run_ prefix rule) and
with the tokenizer's whole design (any run_*.py token is a
runner). No non-runner module named run_* exists in the fleet.
Recorded as an observation, not a finding.

## 3. Codex anchor and plain-codex warning (check 3): PASS

_is_codex_executor, run_batch3.py:2335-2351, anchors "codex" to
the executable token (argv[0] basename, or a token exactly
"codex" as in a shell -c string) and requires a refuse marker in
a DIFFERENT token. _scan_other_runners (line 2353) now calls it
at line 2385 instead of the old substring predicate. All 7 H2
probe codex cases pass: codex + marionette True, codex +
.config/zen True, codex + geckodriver True, plain codex False,
sleep argv[0] "codex marionette notes" False (the redteam M3
repro), grep marionette in a codex dir False, bash -c codex +
marionette True. My extra probe adds: "/usr/local/bin/codex exec
marionette" True (path argv[0] basename anchors), "codex-marionette"
argv[0] False (not an exact codex token). Live: the codex
executor dummy was caught, the codex false-positive dummy was
not, inside the 45/45 run.

_plain_codex_processes, run_batch3.py:2390-2408, lists processes
whose argv[0] basename is codex. launch_gate (lines 2506-2510)
prints a warning for each and still returns True. I verified the
helper live with a dummy plain-codex process (sleep, argv[0]
"codex", argv[1] "60", cmdline verified from /proc first): the
helper found it, _is_codex_executor returned False for it, and
_scan_other_runners excluded it. The warning print loop itself
was verified by source read only (the gate dry run had no plain
codex live, 0 warning lines in its log); the loop is 3 lines
feeding a helper that is verified live, so this is a stated
limit, not a gap. Two observations, neither a finding:
(a) the helper checks argv[0] only, so a plain codex wrapped in
`bash -c "codex ..."` gets no warning (its executor form IS
caught by _is_codex_executor, which scans all tokens); warning
coverage is narrower than refusal coverage, consistent with
warning-only intent. (b) the helper does not exclude own
ancestry, unlike _scan_other_runners, so if the runner was
launched from a plain codex session the warning may name that
launching session. Warning-only, no refusal, so harmless noise.

## 4. run_one per-test re-scan, M2 (check 4): PASS

run_one, run_batch3.py:2174, re-scans at lines 2181-2190, before
WD() at line 2191. On a hit it appends an INFRA failure, prints
the RESULT summary, and returns without opening any session. The
H2 probe proves it live: with 7 dummies live, run_one("b3-t01")
returned pass False with an INFRA failure listing all 7 pids, in
1 ms elapsed (started 2026-11-21T14:33:42.348749+00:00, finished
.349333, 1 ms). No Marionette connection is possible in that
path: the re-scan sits before WD(), and the probe environment has
no Zen. The failure text names every hit pid and cmdline, so it
stays diagnosable, and it flows into the existing one-retry plus
breaker counting as INFRA, not as a fixture failure.

## 5. Probe re-runs (check 5): PASS, 45/45 and 4/4

Re-ran both probes from the repo at HEAD ebe5853, VM, 21:33 +07:

- `python3 /tmp/y14b-h2-probe.py`, 1.3 s wall, exit 0,
  45 PASS lines, FAILURES: 0. Log: /tmp/y14b-c2-rerun.log.
  (grep counts 45 "^PASS" lines; the single "^FAIL" line is the
  summary "FAILURES: 0 []", not a failure.) Covers: 27 unit
  synthetic cmdlines incl. -m x3, -c import x2, -c string-mention
  False, codex anchor x7, residuals x6; 10 live /proc cases incl.
  -m dummy caught, codex executor caught, codex false-positive
  NOT caught, hit set exactly the dummies plus wrappers; M2
  run_one INFRA in 1 ms.
- `python3 /tmp/y14b-gate-dry.py`, 1.6 s wall, exit 0, 4 PASS
  lines, FAILURES: 0. Log: /tmp/y14b-c2-gate.log. A quiet slot
  passes; B bare-relative dummy refuses (flock wrapper, sh
  wrapper and python dummy all listed); C mention-only passes;
  D missing LIVE_SLOT_OK refuses. Same caveat as the
  predecessor: the dry run fakes zen/marionette/ports, so the
  real laptop zen/2828 path is not re-proven here; that code is
  unchanged from the pre-existing gate.

My own extra probe /tmp/y14b-c2-extra.py, exit 0, 25/25 PASS,
FAILURES: 0 (13 -c import cases, 7 -m cases, 2 -c regression
cases, 3 codex cases). Two v1 "FAIL"s in this probe were my
expectation errors, corrected in v2 and recorded here for
honesty: (a) I expected "python3 -m run-nested-pill" False, but
it returns True via the INHERITED flag branch, because
_script_basename_is_runner treats any run-nested* token as a
runner with no .py requirement; a hyphenated name is not a valid
module, so this can never be a real -m launch, harmless.
(b) I applied the runner predicate to a codex cmdline and
expected True; the runner predicate correctly returns False
there, and _is_codex_executor returns True, which is the right
predicate. My plain-codex warning check v1 was likewise vacuous
(the dummy died before the check; sleep rejected "exec" as an
interval); v2 used a valid interval and verified the cmdline
from /proc before asserting (section 3).

## 6. Stale comment fix (Council 2 Fix 2): PASS

Line 2456 now reads "another port would also trip the /proc
tokenizer scan below, but the port check fails closed
directly". The old "pgrep sweep below" wording is gone from
that comment. grep over run_batch3.py finds no remaining
"pgrep sweep" and no "pgrep -f" use (only "pgrep -x" for
zen-bin and geckodriver, as before).

## 7. Residual limitations honesty (check 6): PASS with two precision notes

The docstring (run_batch3.py:2251-2285) lists double-nested -c,
runpy.run_path in -c, extensionless script tokens, direct .pyc,
renamed copies, shebang renamed copies, and spoofed argv[0]. I
verified each misses as claimed: double-nested
`flock -c "bash -c 'python3 run_foo.py'"` False (inner token
comes out "'python3", and "run_foo.py'" fails the .py suffix
check); runpy in -c False; "python3 run_batch3" False;
"python3 run_batch3.pyc" False; renamed copy False; shebang
renamed copy False; spoofed argv[0] "innocuous run_foo.py"
False (probe). None is a launch form in use: grep over the repo
finds no `python3 -m run_` launcher, no `-c "import run_`
launcher, and the runpy uses in the repo (scripts/visuals.py,
scripts/refresh-visuals-manifest.py, tests) execute non-runner
scripts only (build-cursor.py, activate_glass), never a run_*
module. The adjudication's threat model (accidental collision,
not adversarial) still holds.

Two precision notes, both docstring wording, both in the
Required fix:

(a) The sentence "extensionless script tokens ("python3
run_batch3"), direct .pyc execution, ... all miss" overstates
universality. It holds for run_* and hand_drive_e1, but NOT for
run-nested*: `python3 run-nested-pill` returns True (verified
live in my probe), because _script_basename_is_runner has no
.py requirement for the run-nested prefix. Same for a
run-nested*.pyc token. The cited example (run_batch3) is
accurate; the "all miss" reading is not. This is inherited
Y13f helper behavior, not introduced by the fix, but the fix
diff authored this residual sentence, so its precision is in
scope here.

(b) The multi-import second-name miss from section 2 is a new
residual of the -c import branch itself and is not recorded
anywhere yet.

## 8. Sibling copies: FLAG, still need the fix (do not edit)

At HEAD ebe5853 (Y13f landed as 431b2a9):

- tests/realistic/run_codex_y5.py, _is_runner_cmdline at line
  3604: still the OLD form (`if not _script_basename_is_runner:
  continue`, no -m branch, no -c import branch). It still misses
  "python3 -m run_codex_y5" and "python3 -c 'import
  run_codex_y5'". Its codex check at line 3776 still uses the
  substring predicate (`"codex" in _cmd.lower()`), so the M3
  false-positive still lives there. It has no _is_codex_executor
  and no _plain_codex_processes.
- tests/realistic/launch_y13.py, _is_runner_cmdline at line 125:
  same old form, same two missing branches. Its codex scan at
  lines 248-257 still uses the substring predicate, with
  warning-only for plain codex. No _is_codex_executor, no
  _plain_codex_processes.

FLAGGED to Muse/Y13f, per the adjudication (which already
recorded this and said Y14b does not edit Y13f's files). I did
not edit either file. Consequence inside MY scope: the
run_batch3.py docstring line "Keep in sync with launch_y13.py
and run_codex_y5.py (identical logic)" is now FALSE. At re-stage
it was true; this fix moved only run_batch3.py, so the copies
have diverged. The sibling run_codex_y5.py docstring is stale
in the other direction (it still says Y14 "must apply this same
fix when it re-stages", which Y14 has now done); that file is
Y13f-owned, flagged, not edited here.

## 9. Evidence hygiene

- ebe5853 record verified: run_batch3.py at HEAD is git blob
  ed4de81d914f3a75df31554c0b2369110f7e27b0, md5
  65818867865ad4772e78cc2bcac015d6, exactly as the log records;
  fix commit 8bee5249f6e86fce2763bc807cc9b2b1e40d9de1 matches
  the log's ls-remote claim; origin/todolist-push at review time
  is ebe585365d6635bb79dd4f74f544cdcb96dcdda4 (HEAD).
- Fix diff for run_batch3.py (f732d6a..8bee524): 0 em/en dash
  characters, 0 ydotool mentions, no personal info (code and
  comments only).
- py_compile OK at HEAD; import OK, 10 tests (b3-t01..b3-t10).
- Pre-existing untracked files in improvements/ (y6e papers and
  two idea files) were already there before this review; this
  paper is the only file added and the only file committed.

## Required fix (AMEND, docstring only)

One required fix, in tests/realistic/run_batch3.py, function
_is_runner_cmdline docstring (def at line 2251). No behavior
change. Three small edits, all in the same docstring:

1. Sync claim: replace "Keep in sync with launch_y13.py and
   run_codex_y5.py (identical logic)." with a divergence note,
   e.g. "NOTE 2026-11-21: this copy has the -m / -c-import /
   codex-anchor fix; launch_y13.py and run_codex_y5.py do NOT
   yet (flagged to Y13f), so the copies have diverged and the
   old identical-logic claim no longer holds."
2. Residuals: add "comma-list -c import with the runner not
   first (import os, run_foo) misses; only the name immediately
   after import/from is checked."
3. Qualify the extensionless/.pyc sentence: the misses are for
   run_* / hand_drive_e1 names; run-nested* tokens match without
   .py by the helper's prefix rule (including extensionless and
   .pyc forms).

Verification after the fix: grep the three wordings into the
file, re-run `python3 /tmp/y14b-h2-probe.py` (expect 45/45,
exit 0) and `python3 /tmp/y14b-gate-dry.py` (expect 4/4, exit
0). No new council round is needed for a docstring-only change
of this shape, but the fix pass should record the new commit
hash in the re-stage log the same way ebe5853 did for 8bee524.

## Dissent and uncertainty, stated plainly

- I considered GO with the docstring notes as follow-ups, and
  chose AMEND instead, for consistency with the predecessor's
  bar: Council 2 made a stale comment an AMEND-required fix
  (Fix 2), and this paper's item 1 is the same class (a
  now-false claim in the same file), plus two unrecorded
  residuals in a docstring whose stated purpose is to record
  them "not hidden". The fix is minutes of docstring editing;
  holding ship for it costs little and keeps the next reviewer
  from re-discovering the divergence as a surprise.
- The sibling fix itself is NOT required of Y14b and does not
  block this ship: the siblings are Y13f-owned, the
  adjudication already flagged them, and the run_batch3.py gate
  is verified correct on its own. If Y13f lands the sibling fix
  first, item 1 above should instead restore the identical-logic
  claim.
- The -c import branch treats importing a runner module as
  executing it. A hypothetical `python3 -c "import run_batch3"`
  inspection harness (import only, no main call) would be
  refused. No such harness exists in the repo, and importing
  this module executes module-level code, so treating it as a
  runner launch is the fail-closed reading. Recorded, not a
  finding.

## Timed work log (Asia/Ho_Chi_Minh, VM clock UTC+7)

- 21:33:09 task received; fetch + checkout todolist-push, HEAD
  ebe5853, confirmed clean tree apart from pre-existing
  untracked files.
- 21:33:41 H2 probe re-run, 1.3 s, 45/45 PASS, exit 0.
- 21:33:47 gate dry run, 1.6 s, 4/4 PASS, exit 0.
- 21:34 extra probe v1 (25 cases): 2 FAILs, both my expectation
  errors (section 5); v2 corrected, 25/25 PASS, exit 0.
- 21:35 double-nested / runpy / multi-import direct checks;
  sibling grep; hash + dash + compile checks.
- 21:35:56 plain-codex warning check v1 vacuous (dummy died);
  v2 live-verified (helper finds dummy, executor False, scan
  excludes it).
- 21:37-21:44 paper written; committed and pushed after.
