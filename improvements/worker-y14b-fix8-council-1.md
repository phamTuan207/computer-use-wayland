# Council 1 review: Worker Y14b fix pass 8 (Council 2 C7-1 + C7-3)

Verdict: **GO**

Scope: the fix diff only, commit 6f72fe3 on todolist-push
(diff range 0857d19..6f72fe3). Parent 0857d19 is a concurrent
worker commit; run_batch3.py at 0857d19 is blob 8df578c7, so the
run_batch3.py diff is exactly the fix-pass-8 change. I did not
run git fetch. I did not touch
improvements/worker-y14b-fix6-redteam.md. I staged only this
paper file. No live Zen driving, no pkill -f anywhere; every
stub I spawned was killed by exact PID (children first, then
wrapper) and the final orphan sweep is clean.

## Hashes, verified by direct git commands

- Fix8 run_batch3.py: git blob
  eec33fd589a6da5803fd0488745020c579ecd9db, md5
  0527b55e48ec3a406ca1b100c2c1cd04. Matches the task values.
- Fix7 run_batch3.py: git blob
  8df578c7013fc096a30470667ae57bf994884280, md5
  0d98342e57c44464752cf08715ac3861, commit 65d669b. Matches.
- Working tree tests/realistic/run_batch3.py md5 is
  0527b55e48ec3a406ca1b100c2c1cd04, so the tree is the fix8 blob.
- The plan md5 line pins the fix8 values in this fix commit
  (improvements/worker-y14-batch3-live-plan.md, diff hunk at
  line 611: md5 0527b55e, blob eec33fd5, superseding the fix7
  values md5 0d98342e, blob 8df578c7, commit 65d669b).

## Claim 1: C7-1 code fix, VERIFIED

tests/realistic/run_batch3.py, _script_basename_is_runner
(line 2217), now starts with:

    if "(" in name or ")" in name:
        return False

with the docstring stating no real runner name contains parens
and that the fix7 paren drop re-exposed the fix5 false positive
for mid-name parens, which the fix6 cut was accidentally
suppressing. The run_batch3.py diff is exactly 2 hunks in the
basename matcher (this guard plus the _runner_basename_head
docstring rewording). Single call site confirmed by grep in
both blobs: line 2735 in fix8, line 2724 in fix7 (the docstring
grew 11 lines, so the author's cited line 2724 is the fix7
number; see the INFO nit below). The change is contained.

## Claim 2: _runner_basename_head docstring, VERIFIED verbatim

tests/realistic/run_batch3.py lines 2540-2562 (working tree):
the sentence "dropping it is the same correction, not a new
regression" is gone, replaced by: "The paren drop re-exposed
the fix5 false positive for MID-NAME parens (`run_foo(a).py`,
`run_(foo).py`, fix pass 8, Council 2 C7-1); those are now
rejected in _script_basename_is_runner, so the drop plus
that rejection together close all four paren shapes."

## Claim 3: log "zero wrong-direction moves" corrected at both sites, VERIFIED verbatim

- Fix-pass-7 verification section
  (improvements/worker-y14b-restage-log.md, diff hunk at
  log line 2274): "Zero wrong-direction moves ACROSS THE
  REDTEAM'S 98 CASES. CORRECTION (fix pass 8, Council 2
  C7-1): the unqualified "zero wrong-direction moves" claim
  is refuted. The 98 cases did not include mid-name paren
  forms, and `run_foo(a).py` / `run_(foo).py` are fix5 True,
  fix6 False, fix7 True, a wrong-direction move (fix6 False
  to fix7 True) that the differential could not see. The claim
  holds only as scoped to the 98 cases; the C7-1 regression is
  fixed in fix pass 8."
- Council 3 verdict summary (diff hunk at log line 2422):
  "NOTE (fix pass 8, Council 2 C7-1): Council 3's "zero
  wrong-direction moves" is scoped to its own differential,
  which did not include mid-name paren forms; `run_foo(a).py`
  / `run_(foo).py` (fix5 True, fix6 False, fix7 True) are a
  wrong-direction move outside that scope, fixed in fix pass
  8."

Each site is scoped to its own differential and names C7-1
as the wrong-direction move outside that scope, as required.

## Claim 4: C7-3 fix6 probe orphan fix, VERIFIED

tests/realistic/y14b-fix6-probe.py live() (lines 54-100)
now scans /proc for children by ppid, kills each child with
SIGKILL, then kills the wrapper by exact PID and waits. That
is the same structure as the fix7 probe's live() helper
(tests/realistic/y14b-fix7-probe.py), which already did
children-first. The fix6 probe still passes 71/71 after the
patch (see below), so the patch does not break it. I also
re-ran the fix6 probe and confirmed no orphans remained
afterward (ps sweep, 0 run_foo.py processes).

## Claim 5: probes and regressions, ALL REPRODUCED INDEPENDENTLY

### My own differential probe (not the author's files)

I wrote /tmp/c1-fix8-review/probe.py. It loads the fix7 blob
and the fix8 blob side by side from git objects (git show of
65d669b and 6f72fe3, md5 re-checked inside the probe:
0d98342e and 0527b55e) plus the working tree, and checks
_is_runner_cmdline with NUL-joined argv plus
_script_basename_is_runner directly, unit AND live on real
/proc cmdlines from real stub copies in
/tmp/c1-fix8-review/dummies. Exit 0, 0 failures. Results:

- `python3 run_foo(a).py` and `python3 run_(foo).py`, direct
  and bash -c: fix7 True, fix8 False, tree False, want False.
  C7-1 reproduced in fix7 and closed in fix8, unit and live.
- Paren forms `run_foo.py(x`, `run_foo.py)`, `run_foo.py()`:
  False in fix7, fix8, and tree. All four paren shapes now
  False.
- Separator forms `run_foo.py;echo`, `run_foo.py&&echo`,
  `run_foo.py|cat`, `run_foo.py&echo`, `run_foo.py||echo`
  (bash -c, no space): True in fix7, fix8, and tree.
- Plain `run_foo.py`, `hand_drive_e1.py`,
  `run-nested-pill.py`, `run_batch3.py`: True in all three.
  Control `md5sum run_foo.py`: False in all three.
- Helper: _script_basename_is_runner("run_foo(a).py") True
  in fix7, False in fix8; same for run_(foo).py. Helper True
  in both for run_foo.py, hand_drive_e1.py,
  run-nested-pill.py.
- _top_level_sep_index("a=1;", False, False) is 3 in fix7,
  fix8, and tree (C6-2, unchanged).
- Differential fix7 vs fix8 over my 18 unit cases: exactly
  5 diffs, all True to False on mid-name paren forms
  (including `run_foo(a).py;echo`), all correct-direction
  (false positives removed). No other case moves.
- Live: all 3 stubs killed by exact PID, children list empty
  (direct python3 spawn has no wrapper child), orphan sweep 0.

### My own 98-case differential (not the author's script)

I wrote /tmp/c1-fix8-review/diff98.py. It takes only the
CASES list (98 cases) from the fix6 redteam probe
(/tmp/y14b-fix6-rt-probe.py, confirmed 98 entries) as input
data and evaluates the fix7 blob vs the fix8 blob loaded
fresh from git objects. Result: cases=98 same=98 diff=0.
The author's "98 same, 0 diff" claim is independently
reproduced.

### Committed and reviewer probes, re-run by me

- Fix8 probe tests/realistic/y14b-fix8-probe.py: 103 PASS
  lines, 0 FAIL lines, exit 0. Count re-derived from PASS
  lines, not the summary. The probe is the fix7 probe with
  header updated and exactly 17 new C7-1 cases appended
  (14 unit + 3 live, lines 402-436 of the 440-line file);
  diff of the fix7 vs fix8 probe files shows zero changes to
  the carried-forward 86 cases. 86 + 17 = 103.
- Fix7 probe: 86 PASS, 0 FAIL, exit 0 (against the fix8 tree).
- Fix6 probe: 71 PASS, 0 FAIL, exit 0 (against the fix8 tree,
  with the C7-3 patched helper).
- Redteam fix7 probe /tmp/y14b-fix7-rt-probe.py (loads the
  /tmp fix7 blob, md5 0d98342e verified): 56 PASS, 0 FAIL,
  exit 0.
- Council 2 fix7 probe /tmp/y14b-fix7-c2-probe.py --live
  (loads /tmp blobs, md5s verified: fix7 0d98342e, fix6
  fac96935, fix5 9e99d9aa): 118 unit PASS + 2 FAIL, the 2
  FAILs being exactly the intentional C7-1 cases (M7 returns
  True, probe expects False), plus all 5 live cases passing
  (10 live PASS lines including the cleanup checks). This
  reproduces Council 2's 118 PASS + 2 FAIL and proves the
  fix7 blob behaviour the fix8 probe corrects.

### No new wrong-direction move

Across my 18-case unit differential, my 98-case redteam
differential, and all five probe re-runs, the only moves vs
fix7 are the intended True to False flips on mid-name paren
forms. No true case is lost, no false case is gained.

## Claim 6: gap stated plainly, VERIFIED AS STATED

The fix8 log section states plainly that the author H2
probe, fix2/fix3/fix4/fix5 probes, transcription script,
gate-dry and M1 probes are still lost (C6-5) and were not
re-run, and that regression evidence is the committed fix6 +
fix7 probes, the reviewers' fix7 probes, and the new fix8
probe. That matches what I could re-run: every committed
and reviewer probe I had access to was re-run above and
passed (or failed only on the intentional C7-1 cases against
fix7). The run_batch3.py code diff has 0 t10 mentions
(grep 0 on the run_batch3.py diff; the 3 "t10" matches in
the full diff are a pre-existing plan context line
mentioning run_b3_t10 and the log's own sentence stating
the 0 count, neither a code touch). The diff touches only
the basename matcher (2 hunks) plus probe docstrings, so
the H2 launch gate, t10 transcription, and served-fixture
paths are untouched by the code change.

## Hygiene

- 0 em dash (U+2014) and 0 en dash (U+2013) in the full
  fix diff (counted in Python over the diff text).
- 0 ydotool in the code diff. The word occurs twice in the
  full diff, both inside log prose sentences stating 0
  ydotool, not as code or a command.
- No personal info in the diff (no names, emails, addresses,
  phone numbers, or credentials found by grep).
- No live Zen driving, no browser use, no git fetch.

## INFO nit (not AMEND, no action required)

The log and the fix8 paper trail cite "only call site line
2724". That is the fix7 line number; in the fix8 tree the
single call site is line 2735 because the docstring above
it grew by 11 lines. The substance (exactly one call site,
via _runner_basename_head) is correct in both blobs. A
future log entry may cite 2735 for fix8.

## Findings list

- No new findings. C7-1 (REQUIRED, code): FIXED and
  differentially proven. C7-1 doc: FIXED, verbatim. Log
  claim: FIXED at both sites, verbatim. C7-3 (INFO,
  process): FIXED, helper matches the fix7 probe's. C7-2
  (INFO): no author action, correctly none taken.

## Verdict rationale

The one required item from Council 2's AMEND is closed by
the exact one-line fix Council 2 specified, proven by my
own differential probe (unit and live, real /proc
cmdlines) and by the 98-case redteam differential (98 same,
0 diff). All regressions reproduce green, the log
corrections are verbatim at both sites, and hygiene is
clean. Nothing in the diff warrants AMEND or BLOCK.

## Note on this paper's landing

A concurrent worker's `git reset --hard` (reflog entry
"reset: moving to HEAD" at 3f62d67) deleted the first copy
of this paper while it was staged but uncommitted. I
rewrote it verbatim from my own review notes and
re-staged only this file. Content is unchanged from the
first write except this note.
