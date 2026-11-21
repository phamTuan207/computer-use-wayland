# Council 2 review: Y14b fix pass 8 (C7-1 + C7-3)

Verdict: GO

Scope: the fix diff only, commit 6f72fe3 on todolist-push,
diff range 0857d19..6f72fe3. Parent 0857d19 is a concurrent
worker commit; run_batch3.py at 0857d19 is blob 8df578c7, so the
run_batch3.py diff is exactly the fix-pass-8 change. This paper
reviews the fix for my own fix-pass-7 AMEND (75274f6), so it was
verified hardest: every author claim was re-proved with my own
fresh probe, not the author's probe files.

## Hashes, verified by direct git commands

- Fix8 run_batch3.py: git blob
  eec33fd589a6da5803fd0488745020c579ecd9db, md5
  0527b55e48ec3a406ca1b100c2c1cd04. Matches the claim.
  The working tree file still has this md5.
- Parent fix-pass-7 bytes: blob
  8df578c7013fc096a30470667ae57bf994884280, md5
  0d98342e57c44464752cf08715ac3861, at both 65d669b and
  0857d19 (verified with git show plus md5sum). Matches.
- The plan md5 line pins the fix-pass-8 values in this fix
  commit (plan lines 614-616). The fix-pass-8 commit hash
  itself is recorded in the log's hash-record follow-up
  718729a. See INFO C8-1 for one wrong pointer sentence in
  the plan.
- My probe inputs were verified before use:
  /tmp/y14b-fix8-c2/run_batch3_fix7.py md5 0d98342e,
  /tmp/y14b-fix8-c2/run_batch3_fix8.py md5 0527b55e;
  fix5 blob md5 9e99d9aa, fix6 blob md5 fac96935.

## C7-1 (REQUIRED, code): CLOSED

The fix is the one line I specified: _script_basename_is_runner
now returns False when the name contains "(" or ")", at
run_batch3.py lines 2228-2229 in the fix8 blob. Single call
site confirmed by grep: only the def at 2217, a docstring
mention at 2557, and the call at 2735 inside
_is_runner_cmdline via _runner_basename_head. (The log says
line 2724, which was the fix7 line; in fix8 it is 2735. See
INFO C8-2. Substance, one call site, is true.)

My own probe /tmp/y14b-fix8-c2-probe.py (fresh cases, loads
fix5, fix6, fix7, fix8 side by side) proves it, unit AND live:

- `python3 run_foo(a).py`: fix5 True, fix6 False, fix7 True,
  fix8 False. `python3 run_(foo).py`: same four values.
  Same for both forms under `bash -c`.
- Live, real stub files /tmp/y14b-c2-dummies/run_foo(a).py
  and run_(foo).py, real /proc cmdlines: fix7 True, fix8
  False for both; control run_foo.py True in both.
- Helper level: _script_basename_is_runner("run_foo(a).py")
  True in fix7, False in fix8; same for run_(foo).py.
- All four paren shapes False in fix8: run_foo.py(x,
  run_foo.py), run_foo.py(), run_foo.py(a), plus the two
  mid-name forms above.
- No true case lost: separator forms run_foo.py;echo,
  run_foo.py&&echo, run_foo.py|cat, run_foo.py&echo stay True
  in both blobs, direct and under bash -c; plain run_foo.py,
  hand_drive_e1.py, run-nested-pill.py stay True in both.
- Non-runner controls stay False in both: md5sum, echo, vim
  with run_foo.py, run_foo.py.bak, python3 -c run_foo.py.
- C7-2 confirmed with fix8 added: the B12 no-separator form
  is True in fix5, False in fix6, False in fix7, False in
  fix8. No author action was needed, and none was taken.
- R6-1 escape forms unchanged True in both blobs, so the
  fix touches nothing outside the basename matcher.

## C7-1 docstring: CLOSED, verbatim

_runner_basename_head docstring in the fix8 blob now reads:
"The paren drop re-exposed the fix5 false positive for
MID-NAME parens (`run_foo(a).py`, `run_(foo).py`, fix pass 8,
Council 2 C7-1); those are now rejected in
_script_basename_is_runner, so the drop plus that rejection
together close all four paren shapes." The old sentence
"dropping it is the same correction, not a new regression"
is gone. The _script_basename_is_runner docstring states the
rejection and its reason. Both verified in the 6f72fe3 blob.

## Log claim "zero wrong-direction moves": CLOSED at both sites, verbatim

Site 1, fix-pass-7 verification section (log lines 2277-2285
at 6f72fe3): "Zero wrong-direction moves ACROSS THE
REDTEAM'S 98 CASES. CORRECTION (fix pass 8, Council 2
C7-1): the unqualified "zero wrong-direction moves" claim
is refuted. The 98 cases did not include mid-name paren
forms, and `run_foo(a).py` / `run_(foo).py` are fix5 True,
fix6 False, fix7 True, a wrong-direction move (fix6 False
to fix7 True) that the differential could not see. The
claim holds only as scoped to the 98 cases; the C7-1
regression is fixed in fix pass 8."

Site 2, Council 3 verdict summary (log lines 2425-2430 at
6f72fe3): "NOTE (fix pass 8, Council 2 C7-1): Council 3's
"zero wrong-direction moves" is scoped to its own
differential, which did not include mid-name paren forms;
`run_foo(a).py` / `run_(foo).py` (fix5 True, fix6 False,
fix7 True) are a wrong-direction move outside that scope,
fixed in fix pass 8."

Both sites are now correctly scoped, each naming C7-1 as the
move outside its scope.

## C7-3 (INFO, process): CLOSED

The committed fix6 probe's live helper now kills children
first then the wrapper by exact PID (scanning /proc stat
for ppid match, same pattern as the fix7 probe's helper),
with the docstring updated to say so. Verified
behaviorally, not just by reading: I ran the committed
fix6 probe, it passed 71/71, and the orphan sweep after it
found 0 sleep-60 children remaining (fix7 had left 2
orphans per run). The helper text matches the fix7 probe's
helper structure.

## Regressions, all re-run by me

- My fix8 probe /tmp/y14b-fix8-c2-probe.py --live: 94 PASS,
  0 FAIL, exit 0. Differential fix7 to fix8: exactly 6
  moves, all the intended C7-1 True to False (4 unit, 2
  live). No new wrong-direction move anywhere in the set.
- My original fix7 probe re-run unmodified
  (/tmp/y14b-fix7-c2-probe.py): 118 PASS + 2 FAIL, both
  FAILs the intentional C7-1 cases where the fix7 blob
  returns True and the probe expects False. This confirms
  the 2 FAILs are fix7-blob behaviour, and the fix8 tree
  returns False for those forms (proved above).
- Author fix8 probe tests/realistic/y14b-fix8-probe.py,
  re-derived from its PASS lines by running it: 103 PASS,
  0 FAIL, exit 0. Matches the claimed 103/103.
- Committed fix7 probe: 86/86 PASS, 0 FAIL.
- Committed fix6 probe: 71/71 PASS, 0 FAIL, 0 orphans after.
- Redteam fix7 probe /tmp/y14b-fix7-rt-probe.py: 56/56 PASS,
  0 FAIL.
- Differential cross-check over the redteam's 98 cases
  (/tmp/y14b-fix8-diff.py, fix7 blob vs fix8 working tree):
  98 same, 0 diff. Helper _script_basename_is_runner
  True in fix7, False in fix8; _top_level_sep_index("a=1;",
  False, False) is 3 in both.
- The run_batch3.py diff is 2 hunks only, both in the
  basename matcher (rejection plus docstrings). 0 t10
  mentions in that diff.

## Gap, stated plainly

The author H2 probe, fix2/fix3/fix4/fix5 probes,
transcription script, gate-dry and M1 probes are still lost
(C6-5), so they were not re-run; the author states this
plainly in the log. Accepted for this pass: the regression
evidence is the committed fix6 and fix7 probes, the
reviewers' fix7 probes, and the new fix8 probe, and the
diff touches only the basename matcher, so the H2 launch
gate, t10 transcription, and served-fixture paths are
untouched by the diff.

## Hygiene

- Diff 0857d19..6f72fe3: 0 em dash, 0 en dash (grep 0 for
  both). This paper likewise contains none.
- The word ydotool occurs twice in the diff, both prose
  mentions inside log hygiene sentences (the fix7 Council 2
  summary quote and the fix8 "no ydotool lines" sentence).
  Zero ydotool usage in code.
- No personal info in the diff: the PII scan matched only
  long hex hash strings. No emails, addresses, or phone
  numbers.
- No live Zen driving: all probes are unit checks plus local
  sleeping stub spawns. Every stub was killed by exact PID,
  children first, and verified 0 remaining after each run
  (final sweep: 0 run_foo / dummy processes alive).
- No git fetch. The uncommitted file
  improvements/worker-y14b-fix6-redteam.md was not touched
  (still untracked in the working tree, byte-identical to
  before this review started). Only this paper file is
  staged, committed, and pushed by this review.

## INFO notes (no author action required for GO)

- C8-1 (INFO, doc): plan line 620-621 says "The fix-pass-8
  commit hash is in the log's fix-pass-7 entry." Wrong entry
  name: the hash record went into the fix-pass-8 entry
  (follow-up commit 718729a). The hash itself is recorded
  correctly; only the pointer sentence is stale. Fix
  opportunistically in a later log touch.
- C8-2 (INFO, doc): the log's "Only call site is line 2724"
  is the fix7 line number. In fix8 the single call site is
  line 2735, because the longer docstring pushed it down 11
  lines. The substance (exactly one call site, via
  _runner_basename_head) is verified true. Fix the number
  opportunistically.

## Fix-pass-7 tally, closed

3 GO (redteam cdd59a3, Council 3 a9c33ad, Council 1 d122518
+ 6fc7cda) + 1 AMEND (Council 2 75274f6). The AMEND's one
required code item C7-1 is fixed and proved here, its doc
corrections are fixed verbatim at both sites, and its
optional process patch C7-3 is fixed and proved by a clean
orphan sweep. C7-2 needed no action. No new finding from
this review rises above INFO.
