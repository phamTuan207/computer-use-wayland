# Council 3 review: Y14b fix pass 8 (C7-1 + C7-3)

Verdict: GO

Scope: the fix diff only, commit 6f72fe3 on todolist-push, diff
range 0857d19..6f72fe3. Parent 0857d19 is a concurrent worker
commit; run_batch3.py at 0857d19 is blob 8df578c7, so the
run_batch3.py diff is exactly the fix-pass-8 change. Fix pass 7
was 3 GO + 1 AMEND (Council 2 75274f6); the AMEND had one
required code item, C7-1, plus INFO items C7-2 (no author action)
and C7-3 (process patch). This review re-proves every author
claim with its own probes and its own blob loads. It does not
re-review the whole runner.

Reviewer method: own probe /tmp/y14b-c3-fix8-probe.py, own
4-way differential across fix5/fix6/fix7/fix8 blobs extracted by
git cat-file (md5 verified first), own live checks on own stub
files in /tmp/y14b-c3-dummies with real /proc cmdlines, kills by
exact PID only. No live Zen driving. The uncommitted
fix-pass-6 redteam paper was not touched (md5 6756f7bc unchanged
before and after this review).

## 1. C7-1 code fix: CLOSED, independently proven

Claim: _script_basename_is_runner now returns False when the
name contains "(" or ")", since no real runner name contains
parens. Only call site is via _runner_basename_head.

Verified in the fix8 tree, tests/realistic/run_batch3.py:

- _script_basename_is_runner at line 2217; the paren guard is
  lines 2227-2228:
  `if "(" in name or ")" in name: return False`
  placed before the hand_drive_e1.py, run-nested, and run_
  checks, so it cannot leak past them.
- Its only call site is line 2735, inside _is_runner_cmdline,
  `if _script_basename_is_runner(_runner_basename_head(base)):`.
  (See C8-3 below: the log's "line 2724" is the fix7 line
  number; in the fix8 tree the site moved to 2735. The code
  itself is right; only the cited number is stale.)

Own 4-way unit differential (20 cases, _is_runner_cmdline,
NUL-joined argv, blobs loaded side by side):

- run_foo(a).py: fix5 True, fix6 False, fix7 True, fix8 False.
  want False. PASS. This reproduces C7-1 exactly.
- run_(foo).py: fix5 True, fix6 False, fix7 True, fix8 False.
  want False. PASS. Same.
- run_foo.py(x, run_foo.py)x, run_foo.py(), (run_foo.py):
  False in fix7 and fix8. PASS, all four paren shapes now False.
- run_foo.py;echo, run_foo.py&&echo, run_foo.py|cat,
  run_foo.py&echo: True in fix6, fix7, fix8. PASS, separators
  untouched by the paren guard.
- run_foo.py, hand_drive_e1.py, run-nested-pill.py,
  run-nested-wayland.sh: True in all four blobs. PASS, no true
  case lost.
- run-nested(a)-pill.py (own extra edge, not in the author
  probe): fix5 True, fix6 True, fix7 True, fix8 False.
  want False. PASS. The guard fixes a third mid-name paren
  form the author did not list.

Fix7 to fix8 moves in my 20 cases: 3, all FIXED direction
(the two C7-1 forms plus run-nested(a)-pill.py).
Wrong-direction moves fix7 to fix8: 0.

Helper level, _script_basename_is_runner directly:
run_foo(a).py True in fix7, False in fix8; run_(foo).py True
in fix7, False in fix8; run_foo.py, hand_drive_e1.py,
run-nested-pill.py True in fix8; foo.py False in fix8. All PASS.

_top_level_sep_index("a=1;", False, False) is 3 in fix6, fix7
and fix8 (C6-2, unchanged). Note: fix5 takes only one argument
and returns -1 for the same token; the 3-argument form starts
in fix6. My probe first failed on this signature difference,
which is a probe bug, not a code difference; the corrected
probe passes all four blobs.

Own live checks (own stubs, real /proc cmdlines, fix8 module):

- live run_foo(a).py: False, want False. PASS.
  cmdline was the literal paren path under /tmp/y14b-c3-dummies.
- live run_(foo).py: False, want False. PASS.
- live run_foo.py control: True, want True. PASS.
- Orphan sweep after my live checks: 0 stub processes remain.
  My stubs were killed children-first then wrapper by exact PID
  inside my own probe.

## 2. Doc fixes: CLOSED, verified verbatim

- _script_basename_is_runner docstring, run_batch3.py lines
  2221-2226: states no real runner name contains "(" or ")",
  names the fix7 paren drop re-exposing the fix5 false positive
  for mid-name parens, and states the rejection here closes
  them without touching the separator cut. Present as claimed.
- _runner_basename_head docstring, run_batch3.py lines
  2551-2558: the old sentence "dropping it is the same
  correction, not a new regression" is gone. The new text states
  the paren drop re-exposed the fix5 false positive for
  MID-NAME parens (run_foo(a).py, run_(foo).py, fix pass 8,
  Council 2 C7-1), that those are now rejected in
  _script_basename_is_runner, and that the drop plus that
  rejection together close all four paren shapes. Present
  verbatim as claimed. My section 1 proves the "all four"
  claim: (x, )x, (), and mid-name are all False in fix8.

Log claim correction, both sites, in the committed log at
6f72fe3 (checked with git show, not just the working tree):

- Site 1, improvements/worker-y14b-restage-log.md line 2277:
  "Zero wrong-direction moves ACROSS THE REDTEAM'S 98 CASES.
  CORRECTION (fix pass 8, Council 2 C7-1): the unqualified
  'zero wrong-direction moves' claim is refuted. The 98 cases
  did not include mid-name paren forms, and run_foo(a).py /
  run_(foo).py are fix5 True, fix6 False, fix7 True, a
  wrong-direction move (fix6 False to fix7 True) that the
  differential could not see. The claim holds only as scoped
  to the 98 cases; the C7-1 regression is fixed in fix pass 8."
- Site 2, same file line 2425, in the Council 3 verdict
  summary: "NOTE (fix pass 8, Council 2 C7-1): Council 3's
  'zero wrong-direction moves' is scoped to its own
  differential, which did not include mid-name paren forms;
  run_foo(a).py / run_(foo).py (fix5 True, fix6 False,
  fix7 True) are a wrong-direction move outside that scope,
  fixed in fix pass 8."

Both notes name C7-1 as the wrong-direction move outside the
scope, and both match my own measured 4-way values. The
correction is accepted. My section 1 differential is the
independent confirmation that the scoping was the gap: the
redteam 98-case set has no mid-name paren form, so it could
not see the move.

## 3. C7-3 probe helper patch: CLOSED

The committed fix6 probe tests/realistic/y14b-fix6-probe.py,
live() at lines 54-95 in the fix8 tree, now scans /proc for
children of the wrapper PID, SIGKILLs each child by exact PID,
then kills the wrapper and waits. That is the same
children-first order as the fix7 probe's live helper
(tests/realistic/y14b-fix7-probe.py lines 79-101). The old
wrapper-only kill is gone.

Regression run on the fix8 tree: fix6 probe 71/71 PASS,
0 FAIL lines, exit 0. My own runs left no orphan stubs; a
concurrent sibling reviewer's live probe was observed mid-run
during one sweep and was left alone, so its processes are not
counted here either way.

## 4. Probe counts and regressions, re-derived from PASS lines

Committed fix8 probe, run by me on the fix8 tree:
103 PASS lines, 0 FAIL lines (a grep for "^FAIL " returns 0;
the one "^FAIL" hit is the summary line "FAILURES: 0 []"),
exit 0. Counted from the probe file: 14 unit C7-1 cases plus
3 live C7-1 cases = 17 new, and 17 C7-1 PASS lines appear in
the output. 86 + 17 = 103, consistent.

Regressions, all run by me on the fix8 tree, counted from
PASS lines:

- fix7 probe: 86/86 PASS, 0 FAIL, exit 0.
- fix6 probe: 71/71 PASS, 0 FAIL, exit 0 (after the C7-3 patch).
- Author redteam 98-case differential script
  (/tmp/y14b-fix8-diff.py, fix7 blob vs fix8 tree): 98 same,
  0 diff, exit 0. Its fix7 input /tmp/y14b-fix7-run_batch3.py
  md5 is 0d98342e, the true fix7 bytes, so the differential is
  valid. Helper lines from that run: paren True in fix7,
  False in fix8; sep index 3 in both.
- Council 2 fix7 probe re-run (/tmp/y14b-fix7-c2-probe.py,
  loads its own fix5/fix6/fix7 blob copies, md5 verified
  9e99d9aa / fac96935 / 0d98342e): 118 PASS + 2 FAIL, the 2
  FAILs being exactly the C7-1 cases against the fix7 blob.
  This reproduces the original C7-1 finding and proves the
  fix7 behaviour that fix8 corrects.

C7-2 substance, checked independently with my loaded blobs:
B12 no-separator direct form (python3 -c "import os" echo
import run_batch3) is True in fix5, False in fix6, False in
fix7, False in fix8. The measured values stand; no author
action, as Council 2 said.

## 5. Hashes, verified by direct git commands

- git show 65d669b:tests/realistic/run_batch3.py md5
  0d98342e57c44464752cf08715ac3861, blob 8df578c7. Matches.
- git show 6f72fe3:tests/realistic/run_batch3.py md5
  0527b55e48ec3a406ca1b100c2c1cd04, blob eec33fd5. Matches.
- Blobs extracted by git cat-file and md5 checked: fix5
  ff4a5358 / 9e99d9aa, fix6 261f09ae / fac96935, fix7 8df578c7 /
  0d98342e, fix8 eec33fd5 / 0527b55e. All four match the
  plan/log records.
- Plan md5 line pins the fix-pass-8 values IN the fix commit:
  improvements/worker-y14-batch3-live-plan.md lines 614-615
  at 6f72fe3 give md5 0527b55e48ec3a406ca1b100c2c1cd04 and blob
  eec33fd589a6da5803fd0488745020c579ecd9db, superseding the
  fix-pass-7 values. Verified with git show 6f72fe3.

## 6. Diff shape and hygiene

- git diff 0857d19..6f72fe3: 5 files, run_batch3.py 2 hunks
  (the paren guard plus the two docstring rewordings),
  fix6 probe 1 hunk (live helper), new fix8 probe (440
  lines), plan 1 hunk, log 1 hunk. No other code file moves.
- Code diff (run_batch3.py hunks only): 0 em/en dash, 0 lines
  naming the banned automation tool, 0 t10 mentions.
  Whole-diff counts, measured by python over the full diff
  text: em dash 0, en dash 0. See C8-1 for the two
  over-claimed hygiene sentences in the log prose.
- No personal info in the diff (no names, addresses, emails,
  phone numbers, account identifiers). No live Zen driving
  anywhere in this review; all live checks are local stub
  processes on /proc.
- Gap, as the author stated: the author H2 probe,
  fix2/fix3/fix4/fix5 probes, transcription script, gate-dry
  and M1 probes are still lost (C6-5) and were not re-run.
  Regression evidence is the committed fix6 + fix7 probes,
  the reviewers' fix7 probes, and the new fix8 probe, all of
  which I re-ran above. The fix8 code diff touches only the
  basename matcher, so the untested paths are untouched by
  this diff. The gap is real but unchanged from fix7 and
  does not block this fix.

## 7. New findings (INFO, no author action required)

C8-1 (INFO, log wording): two hygiene sentences in the
fix-pass-8 log entry over-claim their grep scope. "0 t10
mentions in the diff" is false for the whole diff: 3 lines
contain t10 (one plan hunk-header context line naming
run_b3_t10, plus the two added log lines that themselves
mention t10 while asserting the count is 0). The log sentence
claiming zero banned-tool lines in the fix diff (grep 0) is
likewise false for the whole diff: 2 lines contain the
banned-tool word (one added log line quoting the Council 2
hygiene sentence, one removed line). The substance is true when scoped to the code diff:
run_batch3.py hunks have 0 t10 mentions and 0 banned-tool
lines, and the H2 launch gate and t10 paths are untouched.
Fix: reword to "in the run_batch3.py code diff" in a later
log touch. Not a code defect, not a landing blocker.

C8-2 (INFO, plan wording): the plan at 6f72fe3 line 620 still
says "The fix-pass-8 commit hash is in the log's fix-pass-7
entry." That is the carried-over fix7 sentence with the
number changed; the fix-pass-8 hash record is in the
follow-up hash-record commit and the fix-pass-8 log section,
not the fix-pass-7 entry. One stale sentence; the md5/blob
pins above it are correct. Fix in a later plan touch.

C8-3 (INFO, log wording): the fix-pass-8 adjudication at log
line 2596 says the only call site is "line 2724 (via
_runner_basename_head)". That was the fix7 line number. In
the fix8 tree the call site is line 2735 (the fix8 docstring
added lines above it). The other occurrence, log line 2558,
quotes Council 2's paper, where 2724 was correct for fix7,
so only the adjudication line is stale. The code is right;
only the cited number moved.

## 8. Verdict rationale

C7-1 is closed by the exact one-line fix Council 2 asked
for, and I proved it independently at unit level, helper
level, and live /proc level, across all four blobs, with
0 wrong-direction moves and no true case lost, including one
extra fixed form the author did not list. The doc fixes are
present verbatim at both cited sites plus both log CORRECTION
notes. C7-3 is closed by the children-first helper patch and
the fix6 probe runs clean. All probe counts re-derive from
PASS lines, all hashes verify by direct git commands, and the
C6-5 gap is stated plainly and unchanged. The three new
findings are INFO-level prose nits of the same class as C7-2,
which Council 2 itself filed as INFO with no author action;
none of them changes behaviour, and none warrants another
fix pass. GO.

## 9. Evidence index

- Own probe: /tmp/y14b-c3-fix8-probe.py, exit 0,
  20 unit + 6 helper + 4 sep-index + 4 head + 3 live checks,
  0 failures, 0 orphans from my stubs.
- Own blob dir: /tmp/y14b-c3-fix8/{fix5,fix6,fix7,fix8}/
  run_batch3.py, md5s in section 5.
- Committed probe outputs (this review):
  /tmp/y14b-c3-fix8-out.txt (103 PASS, 0 FAIL),
  /tmp/y14b-c3-fix7-out.txt (86 PASS, 0 FAIL),
  /tmp/y14b-c3-fix6-out.txt (71 PASS, 0 FAIL).
- Diff range: 0857d19..6f72fe3, branch todolist-push.
- This paper: improvements/worker-y14b-fix8-council-3.md,
  staged alone, no other file touched.
