# Y14b fix-pass-4 Council 3 review (plan and documentation)

## Verdict: AMEND

The code fixes R1 and F1-F4, F6-F9 as claimed, and the hash record is
exact. But the plan and the log misstate the F5 outcome in the
opposite direction (they say True, the code returns False, and False
is the correct outcome), F5 is only half fixed (the generic
extensionless case still false-positives and is unrecorded), and the
F3 import guard has a command-boundary hole the record does not
mention. Those are record errors in the ship document itself, plus
four small arithmetic and cross-reference slips in the log. Fix the
record (U-C3-1 to U-C3-5 below); no code change is required for ship
on R1/F1/F2/F4/F6/F7/F8/F9/F10, and the two residual false positives
are fail-closed and contrived, so recording them is enough.

## Scope

Fix-pass-4 diff ONLY: commit bf3c939
(bf3c939741f86c6c639c730882f8a4f721265a74) against its parent, plus
the hash-record follow-up commit 40c4e48
(40c4e488e3ac123ce78d1a50bcfe15dd1c873386). I did not re-review the
whole runner. The redteam paper under review is bd3c6c9
(bd3c6c90b53fec32bb428eb822c36e3964ef4324, AMEND, R1 + F1-F10,
U1-U11). Branch todolist-push.

## Method and evidence contract

Independent review, no subagents, no live Zen driving, no ydotool.
Every claim below was reproduced by me: I re-ran the fix4 probe and
the transcription probe myself, re-ran H2/fix2/fix3/gate-dry/M1/
fix2-M1/fix2-rt-M1, recomputed the md5 and git blob of
run_batch3.py at bf3c939, recomputed the H4 numbers with Decimal,
ran live CPython checks on a sleeping stub, and ran the disputed
cmdlines directly against `_is_runner_cmdline` and
`_is_codex_executor` loaded from the bf3c939 blob (the working tree
file is byte-identical to it: md5 2920f1697edb3b33711b83b8a874d88b,
confirmed before testing). Counts below are PASS lines only, never
the "FAILURES:" summary line. All stub processes were killed and
verified gone.

## (1) F10 H4 wording: FIXED, with one observation (C3-9)

The H4 note (plan lines 639-660 at 40c4e48) now reads: "The runner's
path is 850 ms + about 3.5 effective Marionette round trips
(Council 1 counts 3, which undercounts by half a round trip, and
Council 3 counts 4, which overcounts by half a round trip; the
advancing read's own transit is half a round trip, not zero and not
one; the two counts differ by at most 0.19 ticks)."

- Half/half stated: yes, verbatim.
- "Bracket" phrasing gone from the H4 note: yes. The only remaining
  "bracket" hit in the plan (line 754) is inside the fix-pass-4
  record bullet itself ("the 'bracket' phrasing is removed"), a
  meta-mention, not the H4 sentence.
- Numbers rechecked independently with Decimal (model ticks =
  floor/ceil((850 + N*RTT)/100), bound 2..11):
  - N=3.5 @2 ms: value 8.57, ticks (8,9), continuous margin 2.43.
  - N=3.5 @19 ms: value 9.165, ticks (9,10), continuous margin
    exactly 1.835, half-up to 1.84.
  - N=3.5 @50 ms: value 10.25, ticks (10,11), continuous margin
    0.75.
  - First fail N=3.5: (1100-850)/3.5 = 71.4 ms. Sure fail N=3.5:
    (1200-850)/3.5 = 100.0 ms. N=3 gives 83.3 / 116.7 ms.
  - These match the redteam V6 recomputation exactly (1.835 half-up
    to 1.84, ticks (8,9)/(9,10)/(10,11), first-fail 71.4 ms,
    sure-fail 100.0 ms at N=3.5), and the plan's "reads 8-10",
    "margin 1-3 discrete, 1.84-2.43 continuous at N=3.5",
    "10-11 at 50 ms (margin 0-1)", "first fails roughly 70-85 ms",
    "fails surely at ~100-117 ms" are all consistent with it (the
    fail ranges span N=3..3.5, which is where 83.3 and 116.7 come
    from). The "differ by at most 0.19 ticks" clause also checks
    out: one round trip is 0.19 ticks at the 19 ms adverse rate.
- Observation C3-9 (not a required fix): U11's literal clause, the
  leg-precise count is 3.0 and 4 overcounts by 1, is stated nowhere
  in the plan. The fix instead states half/half on the effective
  N=3.5 model, which is arithmetically the correct reading of the
  plan's own numbers (at N=3.5, 4 overcounts by half, not by one;
  stating "by 1" would contradict the verified 1.84-2.43 margins),
  and the log's F10 adjudication gives that reasoning ("the
  advancing read's own transit is half a round trip, not zero and
  not one"). I accept the deviation as reasoned, not silent. To
  close U11 fully, one parenthetical could add the leg-precise 3.0
  figure, but it is optional and does not block ship.

## (2) Fix-pass-4 record bullet in the plan: mostly accurate, two errors

Checked line by line against the bf3c939 code diff
(run_batch3.py lines cited at bf3c939):

- R1: accurate. The -m branch runs before the runner-basename
  block (`_is_runner_cmdline`, lines 2446-2453), and
  `_is_runner_module` strips a trailing .py (lines 2513-2520).
  Live check by me: `python3 -m run_foo.py`, `-mrun_foo.py`,
  `-um run_foo.py` all print the stub line and exit 124 under
  `timeout 2`.
- F1: accurate. The -c first-word rule now requires `_c_is_shell`
  (line 2473). Live check by me: `python3 -crun_foo.py` is a
  NameError, exit 1, the file never runs.
- F2: accurate. `_same_command_tokens` (lines 2625-2662) includes
  everything after a codex -c flag. Direct test by me:
  `bash -c "codex -c 'import time; x # marionette'"` returns True
  via `_is_codex_executor`.
- F3: accurate except for the attribution clause (C3-4) and the
  boundary hole (C3-3). The -m branch is guarded by
  `_python_executes(tokens, i - 1)` and the import branch by
  `_python_executes(tokens, c_idx)`; `pytest -m run_batch3`,
  `echo -m run_batch3`, `echo import run_batch3` all return False
  (direct test by me). `python3 other.py -m run_batch3` returns
  False and `python3 run_other.py -m run_batch3` returns True via
  the basename block (direct test by me), so the substance of the
  bullet's run_other.py note is right even though its attribution
  to "the redteam's example" is wrong (C3-4).
- F4: accurate. `_python_executes` (lines 2335-2367) stops its
  backward scan at a shell separator or -c. Direct test by me:
  `bash -c "python3 --version; pytest -W ignore run_batch3.py"`
  returns False, `bash -c "python3 -W ignore run_batch3.py"`
  still returns True.
- F5: INACCURATE (C3-1). The bullet says the extensionless
  barrier is FIXED and "`python3 run_other -W ignore run_batch3.py`
  is now True via run_other itself" (plan line 738). The code
  returns False for that cmdline (direct test by me), and the
  fix4 probe itself expects False ("python3 run_other -W ignore
  stays False", /tmp/y14b-fix4-probe.py lines 80-82). False is
  also the correct outcome: run_batch3.py is only an argument to
  run_other, so the redteam F5 false positive is fixed, not
  preserved as True. The code's own `_python_executes` docstring
  agrees with me: it says the form "misses".
- F6: accurate. `_codex_at_command` (lines 2557-2601) treats a -c
  as a boundary only when `_c_is_shell`. Direct test by me:
  `python3 -c "codex marionette"` returns False via
  `_is_codex_executor`, `bash -c "codex marionette"` still True.
- F7: accurate. `_same_command_tokens` splits glued separators in
  both directions (forward split, backward stop via
  `_is_cmd_separator`, lines 2312-2320). Direct test by me:
  `bash -c "codex --help;echo marionette"` returns False via
  `_is_codex_executor`, `bash -c "codex exec marionette;echo done"`
  still True.
- F8: accurate. The gaps list in `_codex_at_command` now reads
  "nohup, setsid, timeout, flock-direct, time, nice and sudo".
  `grep -c sudo tests/realistic/run_batch3.py` = 1 (was 0 at
  fix pass 3). `sudo codex exec marionette` still returns False,
  a recorded gap.
- F9: accurate. The fix3 probe is 70 checks (my re-run: 70 PASS
  lines, see below), and the docstring records the
  `--check-hash-based-pycs=always` joined case as a fail-closed
  over-approximation. Live check by me:
  `python3 --check-hash-based-pycs=always --version` prints
  "unknown option --check-hash-based-pycs=always", exit 2, while
  the spaced form prints Python 3.12.3, exit 0; the flag branch
  still returns True for the joined form (direct test by me).
- F10: accurate per (1) above.

## (3) Hash records: VERIFIED EXACT

Commands and outputs:

```
$ git show bf3c939:tests/realistic/run_batch3.py | md5sum
2920f1697edb3b33711b83b8a874d88b  -
$ git show bf3c939:tests/realistic/run_batch3.py | git hash-object --stdin
585fb8016b0618ab02b3e97afa362dbcce7342c9
$ git ls-tree bf3c939 -- tests/realistic/run_batch3.py
100644 blob 585fb8016b0618ab02b3e97afa362dbcce7342c9  tests/realistic/run_batch3.py
```

The plan's md5 line at 40c4e48 (lines 614-615) points at the
fix-pass-4 entry with md5 2920f1697edb3b33711b83b8a874d88b, blob
585fb8016b0618ab02b3e97afa362dbcce7342c9, commit bf3c939. The
log's fix-pass-4 entry (lines 675-678) records the same three
values. All three match the recomputation exactly.

The old fix-pass-3 values (blob 3a9b7b17, md5 e9e3519a, commit
3875215) are correctly superseded: they appear nowhere as live
values in the plan at 40c4e48 (grep for e9e3519a, 3a9b7b17,
3875215 in the plan returns nothing), and in the log only in the
historical fix-pass-3 entry (lines 496-497) and the fix-pass-3
redteam verdict section (line 550), both clearly historical.

## (4) Log: verdict section accurate except one label; adjudication covers all findings except two holes; verification numbers re-run green

### Fix-pass-3 redteam verdict section (log lines 503-556)

Present and accurate against paper bd3c6c9, with one mislabel
(C3-7): it says "F3 ... U3 left open", but in the paper U3 is the
F2 unblock condition and F3's is U4. Everything else I checked
matches the paper: R1 mechanism (guard treats -m as a barrier,
`_is_runner_module` rejects .py, probe never tested a .py-suffixed
-m form, no fleet launcher uses -m <runner>.py, U1), F1 NameError,
F2 wrapper miss with leaf pid 183770, F4/F5/F6/F7 examples, F8
grep -c sudo = 0, F9 70 not 72 with the = form rejected live, F10
Decimal recomputation (1.835 half-up to 1.84, ticks
(8,9)/(9,10)/(10,11), first-fail 71.4 ms, sure-fail 100.0 ms at
N=3.5), the clean re-run list, the 5792a82 hash verification, and
the U1-U11 summary (U1 the only required code fix; U2-U5, U7-U8
small code fixes or recordings; U6, U9-U11 doc/log/wording).

### Fix-pass-4 adjudication (log lines 558-640)

Covers R1 and F1-F10, one per bullet, nothing silently dropped.
What it gets right: R1 (ordering + .py strip), F1 (shell -c
requirement + the related import-branch fix), F2 (codex -c
swallows the rest, including the honest note that the first
fix-pass-4 build missed it and the fix4 probe caught it), F3
(guard + the run_other.py true-positive note), F4 (command-start
aware), F6 (shell -c boundary), F7 (glued split + codex -c
inclusion), F8 (sudo restored), F9 (70 not 72, = form documented
as fail-closed over-approximation, spaced form verified live
exit 0), F10 (half/half reasoning). What is wrong or missing in
it is C3-1 (F5 value inverted), C3-3 (import guard boundary hole
unmentioned), C3-4 (F3 attribution), C3-2 (generic extensionless
case unmentioned).

### Fix-pass-4 verification numbers, re-run by me

Working tree run_batch3.py is byte-identical to the bf3c939 blob
(md5 2920f1697edb3b33711b83b8a874d88b), so re-running the /tmp
probes against the working tree is re-running them against the
fix-pass-4 code. Counts are PASS lines only; each log also has
exactly one "^FAIL" line, which is the "FAILURES: 0 []" summary
line, confirming the log's own counting rule.

```
$ python3 /tmp/y14b-fix4-probe.py      exit 0, PASS lines 64, FAIL lines 1 (summary only)
$ python3 /tmp/y14b-transcribe.py     exit 0, PASS lines 82, FAIL lines 1 (summary only)
$ python3 /tmp/y14b-h2-probe.py       exit 0, PASS lines 45, FAIL lines 1 (summary only)
$ python3 /tmp/y14b-fix2-probe.py     exit 0, PASS lines 31, FAIL lines 1 (summary only)
$ python3 /tmp/y14b-fix3-probe.py     exit 0, PASS lines 70, FAIL lines 1 (summary only)
$ python3 /tmp/y14b-gate-dry.py       exit 0, PASS lines 4,  FAIL lines 1 (summary only)
$ python3 /tmp/y14b-m1-probe.py       exit 0, PASS lines 3,  FAIL lines 1 (summary only)
$ python3 /tmp/y14b-fix2-m1-probe.py  exit 0, PASS lines 4,  FAIL lines 1 (summary only)
$ python3 /tmp/y14b-fix2-rt-m1.py     exit 0, 9 scenario lines ending PASS, 0 ending FAIL
$ python3 -m py_compile tests/realistic/run_batch3.py  OK
$ python3 -c "import run_batch3" (from tests/realistic)  OK
```

All match the log's claimed numbers (fix4 64/64, H2 45/45, fix2
31/31, fix3 70/70, transcription 82, gate dry 4/4, M1 3/3, M1
all-12 4/4). The per-section breakdown of the fix4 probe in the
log is wrong, though (C3-5).

### Environment incident note

The note says the VM's system Python lost
/usr/lib/python3.12/re/__init__.py, it was restored sourceless
from its own __pycache__ as __init__.pyc as a stopgap, and the
stdlib should be repaired properly when the fleet is quiet. That
was accurate when written. It is now outdated (C3-8): the proper
repair has since happened. Current state, checked by me:

```
$ ls -la /usr/lib/python3.12/re/__init__.py
-rw-r--r-- 1 root root 16315 Nov 21 15:31 __init__.py
$ ls /usr/lib/python3.12/re/__init__.pyc
No such file or directory
$ dpkg -V python3.12
(exit 0, no output)
$ python3 -c "import re; print(re.__file__)"
re ok /usr/lib/python3.12/re/__init__.py
```

The source file is back (16315 bytes), dpkg -V is clean, `import
re` works, and the .pyc stopgap no longer exists. So the task's
literal check ("__init__.pyc exists") fails, but for the good
reason that the stopgap was superseded by the proper restore, not
because the incident note was wrong.

## (5) Docstring claims touched by fix pass 4: accurate, with one gap

- Sync note: "this copy has the fix-pass-1, -2, -3 and -4
  additions; the sibling copies in launch_y13.py and
  run_codex_y5.py do NOT yet have them". Verified: grep for
  `_c_is_shell` and `_is_cmd_separator` in both sibling files
  returns 0 hits, and neither file mentions fix pass 4.
- `_python_executes` docstring: "Callers pass the index of the
  flag introducing the runner token (the -m index, or the -c index
  for an import), so the introducing flag itself is never counted
  as a barrier." True for the -m caller
  (`_python_executes(tokens, i - 1)`) and the import caller
  (`_python_executes(tokens, c_idx)`). The flag/two-back callers
  pass the runner token index instead, which the sentence does
  not mention, but that is incomplete phrasing, not a false claim,
  since -W/-X are not barrier tokens.
- Residual list: "extensionless script tokens and direct .pyc
  execution miss for run_*/hand_drive_e1 names only
  ('python3 run-nested-pill' returns True via the run-nested
  prefix rule)". Verified by direct test: `python3 run-nested-pill`
  returns True, `python3 run_other` returns False.
- F9 = form note in the `_is_runner_cmdline` docstring: accurate
  (live exit 2, unit True, see (2) F9).
- Gap (C3-2): the `_python_executes` docstring documents the
  extensionless run_* barrier but does not record that a generic
  extensionless script is still not a barrier, which is what U6
  asked to be noted.

## Findings

### C3-1 (REQUIRED, plan + log): F5 outcome stated backwards

Plan line 738 and log lines 601-602 both say `python3 run_other
-W ignore run_batch3.py` "is now True via run_other itself".
Direct test by me against the bf3c939 code:

```
False F5 extless run_other -W
```

The fix4 probe agrees (expects False, "stays False"). The code's
own docstring agrees ("misses"). And False is the correct
outcome: nothing executes run_batch3.py there, it is an argument
to run_other, so the redteam F5 false positive is fixed. The
author most likely confused this with the .py case
(`python3 run_other.py -W ignore run_batch3.py`, which IS True
via run_other.py, direct test by me) or with the old fix-pass-3
value (True, the false positive itself). Fix: change both
sentences to say the form now returns False, the false positive
fixed by the barrier.

### C3-2 (REQUIRED, code/doc): F5 only half fixed, generic extensionless case unrecorded

Redteam F5 had two examples: 2g `python3 run_other -W ignore
run_batch3.py` and 2h `python3 other -W ignore run_batch3.py`.
Fix pass 4 fixes 2g (now False, correct) but 2h still returns
True (direct test by me), because the new barrier only covers
run_* tokens. U6 asked to note the extensionless-script blind
spot in the `_python_executes` docstring; the docstring notes the
run_* barrier but never states the remaining generic blind spot.
Fix: record `python3 other -W ignore run_batch3.py` (still True)
as a residual in the docstring, which closes U6 as the redteam
itself recommended (record over fix, since a value-aware scan
cannot identify an extensionless script in general). Extending
the barrier to any non-flag token is NOT the fix: it would break
the `-W ignore` value handling the guard exists to allow.

### C3-3 (REQUIRED, code/doc): import-branch guard crosses shell separators

The F3 import guard finds the nearest -c by scanning back with
no separator stop, unlike `_python_executes` itself. Direct test
by me against the bf3c939 code:

```
True  import after ; in later echo cmd: python3 -c 'import os'; echo import run_batch3
True  bare tokens: python3 -c import os ; echo import run_batch3
False -m after ; in later cmd: bash -c "python3 --version; pytest -m run_batch3"
```

The import in the later echo command is not a python import, yet
it returns True, because the scan finds the earlier python -c.
The -m branch does not have this hole (its guard endpoint scan
stops at separators, so the pytest -m case is correctly False).
Fail-closed false positive, contrived shape (needs an earlier
python -c in the same cmdline plus a later `import run_batch3`
as a shell word), same class as the previously accepted
residuals. Fix: stop the nearest--c scan at shell separators, or
record the case as a residual in the docstring.

### C3-4 (minor, plan + log): F3 attribution is wrong

The plan bullet and the log F3 adjudication both say "the
redteam's example used run_other.py". The redteam's -m example
was `python3 other.py -m run_batch3` (paper F3, probes 2c/2d/2e);
run_other.py appears in the redteam's -W examples (probe 2a
`python3 run_other.py -W ignore run_batch3.py`, True via
run_other.py itself, documented; and 2g extensionless). The
substance is correct (run_other.py -m is True via the basename
block, the guard is verified with other.py returning False), so
this is a one-clause attribution fix, not a behavior dispute.

### C3-5 (minor, log): fix4 probe breakdown sums to 66, probe has 64

Log lines 660-661: "(R1 -m.py x6, F1 x5, F3 x8, F4 x3, F5 x2,
regressions x17, codex F6/F7/F8 x21, live x4)". That sums to 66.
AST count of /tmp/y14b-fix4-probe.py: `cases` 39 + `codex_cases`
21 + live 4 = 64, matching the 64 PASS lines. Per section: R1 6,
F1 5, F3 9 (not 8), F4 3, F5 2, regressions 14 (not 17), codex 21,
live 4. The total 64 is right; the F3 and regressions counts are
wrong.

### C3-6 (minor, log): the "72" story is off by one

Log lines 670-671: "The earlier '72' (fix3) and '65' (fix4) claims
counted the summary line". For fix4 that works: 64 PASS lines + 1
summary line = 65. For fix3 it does not: 70 + 1 = 71, not 72, so
one of the claimed 72 remains unexplained. The F9 adjudication
("my 71 recount counted the summary line") explains 71, not the
commit message's 72. Correct the sentence or drop the
explanation for 72.

### C3-7 (minor, log): F3 unblock label is U4, not U3

The fix-pass-3 verdict section (log line 530) says "F3 ...
U3 left open". In paper bd3c6c9, U3 is the F2 unblock condition
and U4 is the F3 unblock condition. Relabel to U4.

### C3-8 (minor, log): environment incident note is now stale

See (4): the .pyc stopgap is gone and the proper .py restore is
done (dpkg -V clean). Add one follow-up line to the incident
note recording the proper repair, so a later reader does not act
on the "should be repaired properly" flag as if it were still
open.

### C3-9 (observation, optional): U11 literal clause

See (1). The fix is correct on the plan's N=3.5 model and the
deviation from U11's letter is reasoned. Optional: add the
leg-precise 3.0 figure as a parenthetical in the H4 note to close
U11 fully. Not required for ship.

## Unblock conditions for fix pass 5 (all small, record only except C3-3)

- U-C3-1: correct the F5 sentences in the plan (line 738) and the
  log (lines 601-602) to False (C3-1).
- U-C3-2: record `python3 other -W ignore run_batch3.py` (still
  True) as a residual in the `_python_executes` docstring,
  closing U6 (C3-2).
- U-C3-3: stop the import-branch nearest--c scan at shell
  separators, or record the `python3 -c 'import os'; echo import
  run_batch3` True case as a residual (C3-3).
- U-C3-4: fix the F3 attribution clause in the plan bullet and
  the log (redteam -m example was other.py) (C3-4).
- U-C3-5: fix the fix4 probe breakdown (F3 9, regressions 14),
  the "72" sentence, the U3/U4 label, and add the env-note
  follow-up line (C3-5, C3-6, C3-7, C3-8).
- Optional: add the leg-precise 3.0 parenthetical to the H4 note
  (C3-9).

## Hygiene

- 0 em dash, 0 en dash in `git show bf3c939` and `git show
  40c4e48` (grep count 0 for both code points in both commits).
- 0 personal info in the added lines of either commit (no email
  or name pattern in `git show <commit> | grep '^+'`); the only
  name/address hit in the full `git show` output is the git
  Author header, which is commit metadata, not file content.
- ydotool: the only hits in either commit are the log lines "no
  ydotool" (a negative mention), same as the redteam paper.
- No live Zen driving by me or, as far as the diff and log show,
  by the fix author: all live checks are local sleeping stubs
  and /proc scans. My own stub processes were killed and verified
  gone (`pgrep -f run_foo` shows no stub process).

## Timed work log (Asia/Ho_Chi_Minh, 21/11)

- 22:42: task received. Fetch origin, confirm bf3c939 and 40c4e48
  on todolist-push, read both diffs and paper bd3c6c9.
- 22:43-22:45: hash recomputation (md5 + blob match exactly),
  H4 Decimal recomputation, plan/log grep checks.
- 22:45-22:48: re-ran fix4 probe (64/64), transcription (82),
  H2 (45), fix2 (31), fix3 (70), gate dry (4), M1 (3), fix2-M1
  (4), fix2-rt-M1 (9 scenario PASS).
- 22:48-22:52: direct unit tests of the disputed cmdlines
  (F5 False vs the record's True, 2h still True, import-after-;
  True, F3 attribution check); live CPython checks (-m exit 124,
  -c NameError exit 1, = form exit 2, spaced form exit 0);
  env check (re .py restored, dpkg -V clean, .pyc gone).
- 22:52-22:55: paper written, committed, pushed, verified.
