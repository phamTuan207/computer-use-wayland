# Redteam review: Y14b fix pass 7 (65d669b)

- Scope: ONLY the fix-pass-7 diff, `d76daba..65d669b` (4 files).
  `run_batch3.py` blob `261f09ae` to `8df578c7`, md5 `fac96935` to
  `0d98342e`. Adjudication under review: "Fix pass 7 verification"
  in `improvements/worker-y14b-restage-log.md` (lines 2249-2299).
- Reviewer: independent redteam. Worked 00:16-00:20 +07, 2026-11-22.
- Method: own probes, built from shell/Python semantics, not from
  the author's probe. Unit + live `/proc` cmdlines with sleeping
  stubs (`/tmp/y14b-dummies`, `PATH=/tmp/y14b-dummies:$PATH` for
  codex). Every stub killed by exact PID (children first, then
  wrapper); 0 processes left behind at end of review (verified
  with `ps`). No Zen driving, no browser work.
- Verdict: **GO**

## 1. Hashes (verified by direct git commands, not from the log)

- `git rev-parse 65d669b` = `65d669b5efd3be927d64e2d516dd8258a310d34c`.
- `git ls-tree 65d669b tests/realistic/run_batch3.py`:
  blob `8df578c7013fc096a30470667ae57bf994884280`;
  `git show 65d669b:... | md5sum` = `0d98342e57c44464752cf08715ac3861`.
- Parent: `git ls-tree d76daba ...` blob
  `261f09aed1b52c7b80b0b2fc260f13f70fafd142`;
  md5 `fac96935988b9c327dcbe9b3cfa1342e`.
- Fix-pass-6 commit `d552f4d` exists and carries blob `261f09ae`,
  so the log's "parent fix-pass-6 bytes" line is correct.
- Plan md5 line pins the fix-pass-7 values IN the fix commit
  (`improvements/worker-y14-batch3-live-plan.md`, fix-pass-7
  entry: md5 `0d98342e...`, blob `8df578c7...`). Confirmed in the
  diff, not only in the follow-up hash-record commit.

## 2. R6-1 (REQUIRED): backslash escapes

Code change (`tests/realistic/run_batch3.py`, `_quote_states`
~line 2446, `_top_level_sep_index` ~line 2495): when outside
single quotes, a backslash skips the next character (`i += 2`);
inside single quotes it is literal. That is the shell rule.

My own probe (`/tmp/y14b-fix7-rt-probe.py`, 56 checks, 56/56
PASS, exit 0), derived independently of the author's probe:

- Helper level, `_quote_states`:
  - escaped double quote keeps `in_double`:
    `['"a', '\\"b;', 'marionette"']` gives
    `[(F,F), (F,T), (F,T)]`.
  - escaped backslash then quote still toggles:
    `['a\\\\"b', 'x;']` gives `[(F,F), (F,T)]`.
  - backslash inside single quotes is literal:
    `["'a\\'", 'b;', 'c']` gives all `(F,F)`, so `b;` is
    top-level, as the shell parses it.
  - apostrophe idiom token `'don'\''t` ends `in_single=True`;
    the `;` in the following `stop;` token is correctly
    inside quotes, and the marker token closes the region.
- Helper level, `_top_level_sep_index`:
  `a\"b;` returns 4 (was -1 in fix6: the escaped quote no
  longer swallows the separator); `a\;b` returns -1 (escaped
  separator is literal, correct shell behaviour); trailing
  backslash returns -1 with no crash; `a=1;` unquoted
  returns 3 (C6-2, see section 4).
- Predicate level, all three proven forms, unit AND live:
  - (a) codex prompt `a \"b; marionette`: unit True, live True
    (real `/proc` cmdline of the dummy codex sleeper).
  - (b) python -c `x=\"a\\\"b\"; import run_batch3`: unit True,
    live True (own live form:
    `python3 -c 'x="a\\"b"; import time; time.sleep(60);
    import run_foo'`).
  - (c) shell idiom `don'\''t stop; marionette`: unit True,
    live True.
  - Control: apostrophe in double quotes True.
- No regression on the existing quote cases (same probe):
  R5-1 B1/B6, C5-1 B5, C2-3 `a;b`, F2, R3 control, R4 control,
  B12, d4 all return their fix6 values.
- Bare-dont unreachable form: unit returns True (as the fix6
  redteam paper already records for fix6); live, bash rejects
  the command with exit 2 (`unexpected EOF while looking for
  matching \`'\``), so it never reaches a scan. The author's
  probe correction (first run 85/86, expectation fixed to
  True with that explanation) is correct, and the committed
  probe carries the corrected expectation with the explanation
  in the case name. Not a code issue.

Differential (redteam's 98 fix6-probe cases, fix6 blob vs
fix7 blob, `/tmp/y14b-fix7-diff.py` re-run by me): 92 same,
6 diff, ALL 6 in the FIXED direction (C15 paren `(` True to
False, C16 paren `)` True to False, backslash import False
to True, C15b paren wrapped True to False, dont shell idiom
False to True, backslash esc dq False to True). Zero
wrong-direction moves.

Full 98-case cross-check by me (same CASES, fix7 blob vs
each case's fix6 expectation): 8 mismatches, but all 8 are
cases where the FIX6 blob already mismatched the same
expectation (pre-existing gaps, unchanged by fix7). True
fix7 regressions (fix6 matched, fix7 broke): **0**.
The 8 inherited gaps are: `two python -c`, `bash -c argv
python`, `-W swallows -c`, `init file named python3`,
`-o value named bash`, `dont stop bare`, `E1c no sep before
codex`, `dont bare word`. Two of them (`dont stop bare`,
`dont bare word`) are the bare-dont form above; `E1c` is the
R6-4 documented false positive, now bounded in the
docstring (see section 4). None is in fix-pass-7 scope;
none is newly introduced.

## 3. R6-2 / C6-3 (REQUIRED): parens dropped from the cut set

`_runner_basename_head` now cuts at `";"`, `"&"`, `"|"` only
(`run_batch3.py` ~line 2555). Verified in my probe, unit
and live:

- False now: `python3 run_foo.py(x`, `python3 run_foo.py()`,
  `python3 run_foo.py)`, `bash -c "python3 run_foo.py(x,
  run_foo.py)"`, `bash -c "python3 run_foo.py(x"`, and live
  `bash -c "python3 .../run_foo.py(x; sleep 60"`.
- Still True: `run_foo.py;echo`, `run_foo.py&&echo`,
  `run_foo.py|cat`, `run_foo.py&echo`, `run_foo.py||echo`
  (unit), and live `bash -c "python3 .../run_foo.py;echo
  done; sleep 60"`.
- Helper level: `run_foo.py(x` / `run_foo.py)` /
  `run_foo.py()` all returned whole; `;` / `&&` / `|` / `&`
  still cut to `run_foo.py`. No true case lost: the 98-case
  cross-check shows 0 regressions, and the separator
  controls above all hold.

The docstring's claim about the `")"` cut being pre-existing
fix5 behaviour is consistent with the fix5 code
(`base.rstrip(";,()&|")`, 46e0909 line 2539).

## 4. Doc fixes (all confirmed in the diff)

- C6-1: log line ~1006 now states the shipped fix-pass-5
  rstrip set was `";,()&|"` (was `";,()"`). Verified against
  the fix5 source itself: `git show 46e0909:...run_batch3.py`
  line 2539 reads `base.rstrip(";,()&|")`. Correct.
- C6-2: `_top_level_sep_index` docstring now states the
  helper DOES return a top-level index for unquoted `a=1;`
  (3, not -1) and that the direct case is safe only because
  its caller applies no separator stop there. Verified:
  helper returns 3 in both fix6 and fix7 (unchanged).
- C6-4: B12 comment now cites the no-separator form
  `python3 -c "import os" echo import run_batch3` with the
  fix5/fix6 history. Verified across blobs: no-separator
  form True in fix5, False in fix6, False in fix7; the
  earlier glued-`;` form False in all three. The history
  claim is exactly right, and the fix5 blob I used has md5
  `9e99d9aa...`, matching the plan's recorded fix5 md5.
- U-C3-1 / INFO-1: the old `"(fail-closed)"` label is gone
  from the `_is_runner_cmdline` docstring (line 2691) and the
  import-branch comment (line 2800); both now say
  "synthetic-only" with the reason (a single `/proc` cmdline
  cannot hold two top-level commands from a real shell
  launch, so no live runner is missed). Correct direction:
  a missed real runner would be fail-open, not fail-closed.
- R6-4 / U3: `_in_shell_c_string` docstring carries one
  bounding sentence naming the exact no-separator form
  (`bash -c "python3 -c 'x=1;__import__(\"time\").sleep(60)'
  codex --help; echo marionette"`), marked pre-existing,
  fail-closed, narrow, recorded not fixed. Live-proven by
  me with the EXACT docstring form (sleep 60, dummy codex
  on PATH): wrapper `/proc` cmdline flags True under
  `_is_codex_executor` although no codex process exists.
  The sentence is accurate, and the fix is correctly left
  out of scope.
- C6-3 note: `grep -r bash -c run_batch3.py` added to the
  C2-5 list in the `_is_runner_cmdline` docstring (line
  2681). Present.
- Plan md5 line: pins fix-pass-7 values in-commit (section 1).

## 5. Author's probe, re-derived (not trusted)

- `tests/realistic/y14b-fix7-probe.py`: 86 PASS lines, 0
  FAIL lines, exit 0, counted by me from its output
  (`grep -c "^PASS"` = 86; the single `^FAIL` hit is the
  `FAILURES: 0 []` summary line). The file is committed in
  65d669b (blob `899b1135...`). Its 15 new cases match the
  claimed composition (R6-1 a/b/c + 2 controls + 4 paren +
  4 separator controls + 2 live); the 71 fix6 cases are
  present.
- Fix6 probe regression: `tests/realistic/y14b-fix6-probe.py`
  run by me against the fix7 tree: 71 PASS, 0 FAIL, exit 0.
- The log's "first run 85/86" note is consistent with the
  evidence (bare-dont expectation, section 2) and the
  committed probe carries the corrected expectation.

## 6. Hygiene

- Em/en dash in the diff: 0 and 0 (`grep -c` on the
  `d76daba..65d669b` diff). The single `ydotool` hit in the
  diff is the log's own sentence "no ydotool lines in the
  fix diff (grep 0)": a mention, not use. No ydotool use.
- No personal info in the diff (grep for name, email,
  address patterns: 0).
- No live Zen driving: the diff touches only the runner
  predicate, its docstrings, the plan, the log, and the
  probe. Live checks read `/proc` cmdlines of local stubs
  only.

## 7. Observations (not findings, no action needed)

- During my own verification I once saw 3 `run_foo.py`
  sleepers alive at a `ps` snapshot; all self-expired
  within their 60s sleep and a direct re-test of the
  live-helper kill logic (children-first by exact PID, both
  the `;` and `&&` forms and the `-o pipefail` exec form)
  leaves 0 behind. The helper works; the snapshot caught
  sleepers mid-window. No orphan remained at end of review.
- The fix6 redteam probe's own expectations already
  mismatch fix6 on 8 of 98 cases (it is an informational
  differential probe, not a green gate). Fix7 fixes 6 of
  the 14 fix6 mismatches and introduces 0 new ones; the 8
  remaining are pre-existing documented gaps outside this
  pass's scope.

## Verdict: GO

Both REQUIRED items (R6-1, R6-2/C6-3) are proven by
independent unit + live probes with zero regressions across
the 98-case fix6 set, all 7 doc fixes check out against
primary sources (fix5 code, fix5/fix6/fix7 blobs, live
bash behaviour), hashes match by direct git commands, and
hygiene is clean. Nothing in the diff needs amendment.
Ship may proceed.
