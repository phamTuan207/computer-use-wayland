# Council 3 review: Worker Y14b fix pass 7 (commit 65d669b)

- Reviewer: Council 3 (voice 3), independent. This council found
  U-C3-1 / U-C3-2 in fix pass 6; both are re-verified closed here.
- Scope: ONLY the fix-pass-7 diff, commit
  65d669b5efd3be927d64e2d516dd8258a310d34c (parent d76daba).
  4 files: tests/realistic/run_batch3.py,
  improvements/worker-y14-batch3-live-plan.md,
  improvements/worker-y14b-restage-log.md,
  tests/realistic/y14b-fix7-probe.py (new).
- Review window: 2026-11-22 00:16 to 00:24 +07 (Asia/Ho_Chi_Minh).
  Elapsed about 8 minutes.
- Base note: HEAD at review time is d3e0a76 (hash-record commit on
  top of 65d669b). Verified `git diff 65d669b HEAD --
  tests/realistic/run_batch3.py` is 0 lines, so every check below
  against the working tree tests the fix7 blob.

## Verdict: GO

All seven fix-pass-7 scope items are verified closed with
independent evidence. No BLOCK, no AMEND item. Two INFO notes
at the end; neither requires a fix pass.

## 1. Hashes, verified by direct git commands (not from the log)

- `git ls-tree 65d669b tests/realistic/run_batch3.py`:
  blob 8df578c7013fc096a30470667ae57bf994884280.
- `git ls-tree d76daba tests/realistic/run_batch3.py`:
  blob 261f09aed1b52c7b80b0b2fc260f13f70fafd142.
- `git show 65d669b:... | md5sum`: 0d98342e57c44464752cf08715ac3861.
- `git show d76daba:... | md5sum`: fac96935988b9c327dcbe9b3cfa1342e.
- All four match the claimed values (blob 8df578c7 / md5 0d98342e
  at 65d669b; blob 261f09ae / md5 fac96935 at the parent).
- `git show 65d669b:tests/realistic/y14b-fix7-probe.py` exists,
  blob 899b1135b51c627c439b6295b99d67f38fb99a5b, 379 lines.
- Diff shape: `git diff d76daba 65d669b --stat` is exactly the 4
  files above (668 insertions, 52 deletions). run_batch3.py has
  7 hunks, all inside the scanner helpers and their docstrings
  (_quote_states, _top_level_sep_index, _runner_basename_head,
  _is_runner_cmdline docstring + import-branch comment,
  _in_shell_c_string docstring). Zero t10 hunks: the only "t10"
  strings in the diff are 2 pre-existing context lines in the
  plan file. The plan diff is a single hunk (the md5 line), so
  the H4 note and H4 numbers are byte-identical apart from a
  1-line shift; nothing to re-derive, H4 unchanged. Scanner-only
  diff confirmed.

## 2. U-C3-1 (my fix-pass-6 doc finding): CLOSED

- The _is_runner_cmdline docstring at 65d669b (run_batch3.py
  lines 2689-2696) now reads: "a python -c in a later
  top-level command after a shell -c is treated as nested (fix
  pass 6, import-branch heuristic, synthetic-only, recorded not
  fixed: a single /proc cmdline cannot hold two top-level
  commands from a real shell launch, so no live runner is
  missed) (fix pass 7, Council 3 U-C3-1 / Council 1 INFO-1:
  the old "(fail-closed)" label was the wrong direction; a real
  runner missed would be fail-open, and the combined argv cannot
  occur from a real launch)".
- The import-branch comment (lines 2799-2806) carries the same
  replacement: "that form is synthetic-only (a single /proc
  cmdline cannot hold two top-level commands from a real shell
  launch, so no live runner is missed) (fix pass 7, Council 3
  U-C3-1 / Council 1 INFO-1: the old "(fail-closed)" label was
  the wrong direction)".
- Both required elements are present in both places: the
  synthetic-only wording AND the single-cmdline reasoning.
- Literal-grep note (INFO-1, not a finding): the character
  string "(fail-closed)" still occurs at lines 2694 and 2804,
  but only inside the clause "the old "(fail-closed)" label was
  the wrong direction". No remaining occurrence presents the
  residual AS fail-closed. The string survives as the audit
  trail of the correction, which is correct documentation, not
  a mislabel. The other "(fail-closed)" / "fail-closed"
  occurrences in the file (lines 2447, 2642, 2671, 2683, 2958,
  3004, 3270) attach to different residuals (apostrophe caveat,
  R5-8, R6-4 bound, R5-7) and are not this sentence.

## 3. U-C3-2 (my fix-pass-6 process finding): CLOSED

- The fix7 probe is committed under tests/realistic/ in
  65d669b: tests/realistic/y14b-fix7-probe.py, 379 lines.
- Re-ran it myself from the repo root: exit 0, 86 PASS lines,
  0 lines starting "FAIL " (the single grep hit for "FAIL" is
  the summary line "FAILURES: 0 []").
- Fix6 probe regression re-run by me: 71 PASS lines, 0 FAIL
  lines, exit 0. No fix6 case moved.
- The author's "first run 85/86" story checks out: the bare
  "don't" control returns True at unit level (the unbalanced
  apostrophe makes the tracker read everything after it as
  inside quotes, fail-closed, as the _quote_states docstring
  records) and is unreachable live (bash exits 2, syntax
  error, verified by me in section 5). Correcting the probe
  expectation to True was the right call, not a code fix.

## 4. R6-1 (redteam U1): backslash escapes: CLOSED

My own probe (/tmp/c3-fix7-probe.py, written from scratch for
this review, not a copy of the author's probe) tested all three
proven forms at unit level AND live, plus a fix6-blob
differential over the same battery. Results:

- (a) codex prompt `a \"b; marionette`: unit wrapper
  `bash -c 'codex -c "a \"b; marionette"; sleep 60'` True
  (fix6 False); leaf `codex -c 'a "b; marionette'` True;
  LIVE /proc wrapper True (dummy codex on PATH).
- (b) python -c `x=\"a\\\"b\"; import run_batch3`: unit wrapper
  True (fix6 False); leaf True; LIVE /proc wrapper True
  (fix6 False) with the corrected construction in section 5.
- (c) shell apostrophe idiom `don'\''t stop; marionette`: unit
  wrapper True (fix6 False); leaf `codex -c "don't stop;
  marionette"` True; LIVE /proc wrapper True.
- Controls unmoved (all identical in fix6 and fix7): R5-1
  `codex -c 'a b; marionette'` True; R3 `codex -c 'hello';
  echo marionette` False; C5-1 python `-c 'x=1; import
  run_batch3'` True and codex `-c 'x=1; marionette'` True;
  C2-3 `codex -c 'a; b marionette'` and `'a;b marionette'`
  True; F2 direct `python3 -c 'import os; import run_batch3'`
  True; double-quoted `codex -c "a;b marionette"` True;
  `codex -c 'a\b'; echo marionette` False (backslash before a
  non-quote does not hide a real separator).
- Differential over my battery: exactly 7 fix6-to-fix7 moves,
  all in the fixed direction (3 R6-1 False to True, 4 paren
  True to False, section 5). Zero wrong-direction moves.
- The escape rule is correctly scoped: a backslash is skipped
  only outside single quotes. Proof: `codex -c 'a \'b;
  marionette'` returns False in BOTH blobs, and real bash
  rejects that form outright (exit 2, "unexpected EOF while
  looking for matching `''"), so it is unreachable live. The
  backslash is literal inside single quotes, exactly as the
  shell rule requires.

## 5. C6-3 / R6-2: parens dropped from the basename cut set: CLOSED

- `_runner_basename_head("run_foo.py(x")` returns "run_foo.py(x"
  (uncut); `"run_foo.py)x"` returns "run_foo.py)x" (uncut).
  Both were True (cut to "run_foo.py") in fix6.
- Unit: direct `python3 run_foo.py(x` False, direct
  `python3 run_foo.py)x` False, wrapped `bash -c "python3
  run_foo.py(x"` False, wrapped `bash -c "python3
  run_foo.py)x"` False. All four were True in fix6.
- Separator forms still cut and still True: `run_foo.py;echo`,
  `run_foo.py&&echo`, `run_foo.py|cat`, `run_foo.py&echo`
  (wrapped and direct), plus plain `run_foo.py`.
- LIVE: `exec -a python3 sleeper "run_foo.py(x"` reads False
  from real /proc; `exec -a python3 sleeper "run_foo.py"`
  reads True. Real bash confirms the paren form never
  executes: `bash -c 'python3 run_foo.py(x'` exits 2.
- No true case is lost: the fix6-to-fix7 differential over my
  battery shows the ONLY moves are the 3 R6-1 fixes and the 4
  paren flips. The author's differential over the redteam's 98
  cases (92 same, 6 diff, all fixed direction) is consistent
  with mine; my battery adds the direct `run_foo.py)x` case,
  which is the 7th diff and also fixed direction.

## 6. Doc items C6-1 / C6-2 / C6-4, R6-4 / U3, plan md5: CLOSED

- C6-1: log line 1006 at 65d669b now states
  ``base.rstrip(";,()&|")`` with the fix-pass-7 annotation
  (the bullet originally stated the pre-extension set
  `";,()"`; the shipped fix-pass-5 code was `";,()&|"`;
  the rstrip is superseded by the fix-pass-6 head check and
  the fix-pass-7 paren drop). Verified in the 65d669b blob,
  not just the working tree.
- C6-2: measured `_top_level_sep_index("a=1;", False, False)`
  myself: returns 3 in fix7 AND in fix6 (unchanged helper).
  The docstring now states the helper DOES return a top-level
  index for it (3, not -1) and that the direct case is safe
  only because its caller applies no separator stop there.
- C6-4: the B12 no-separator example `python3 -c "import os"
  echo import run_batch3` (True in fix5, False in fix6) is
  present in BOTH the import-branch code comment
  (run_batch3.py lines 2822-2833, with the note that the
  earlier glued-";" form returned False in both fix5 and fix6
  and did not demonstrate the gap) AND the log's fix-pass-6
  adjudication item 4 (lines 1701-1712). My own unit checks:
  no-separator later argv False, glued-";" variant False.
- R6-4 / U3: the _in_shell_c_string docstring now carries the
  bounding sentence, naming the exact no-separator form
  (`bash -c "python3 -c 'x=1;__import__(\"time\").sleep(60)'
  codex --help; echo marionette"`), marked pre-existing,
  fail-closed, narrow, recorded not fixed. My unit check
  confirms the behaviour is unchanged (returns True, the
  recorded false positive).
- C6-3 doc note: `grep -r bash -c run_batch3.py` added to the
  _is_runner_cmdline docstring C2-5 list (line 2682-2683).
- Plan md5: the plan file AT 65d669b lines 614-615 pins
  md5 0d98342e57c44464752cf08715ac3861 and blob
  8df578c7013fc096a30470667ae57bf994884280, i.e. the fix-pass-7
  values IN the fix commit (per C5-4). The fix-pass-7 commit
  hash itself goes in the log's hash-record follow-up, which
  is d3e0a76, as expected since it cannot be known before
  committing.

## 7. Hygiene: CLEAN

- 0 em dashes and 0 en dashes in the full fix diff (counted
  with Python over `git diff d76daba 65d669b`).
- No ydotool use: the only "ydotool" line in the diff is the
  log's own sentence "no ydotool lines in the fix diff
  (grep 0)".
- No personal info in the diff (scanned for gmail, names,
  addresses, phone patterns: none).
- No live Zen driving: all live checks used sleeping stubs
  (/tmp/y14b-dummies codex sleeper, sleeper binary,
  python3 -c sleeps) and read /proc only. Every stub I spawned
  was killed by exact PID (children first); final sweep shows
  no stub of mine remaining.

## 8. My probe's three initial FAILs: all probe errors, re-derived

For the record, my independent probe first reported 3 FAILs
out of 43 checks. Each was re-derived, not trusted:

- FAIL 1: `bash -c "echo hi; python3 -c 'import run_batch3'"`
  expected True, got False. Fix6 returns False too: pre-existing
  behaviour, unchanged by fix7 (see INFO-2). My expectation
  was wrong, not the code.
- FAIL 2: `codex -c 'a \'b; marionette'` expected True, got
  False. Fix6 also False, and real bash exits 2 on the form
  (unreachable live). The escape rule is correctly scoped;
  my expectation was wrong.
- FAIL 3: live R6-1 (b) got False. Root cause is my live
  construction, not the code: the python3 -c exits at once,
  so bash execs the trailing `sleep 60` and its own /proc
  cmdline becomes `sleep 60` (proved by dumping the cmdline:
  `b'sleep\x0060\x00'`). Corrected construction (the python
  -c itself sleeps 60, so bash stays in the -c phase) reads
  True in fix7 and False in fix6. Durable lesson for future
  live probes: the leaf command must outlive the read, or bash
  replaces its own cmdline. This is also why the author's
  probe live-tests only R6-1 (a) and (c), where the dummy codex
  sleeps.

## INFO notes (no action required)

- INFO-1: see section 2. The literal "(fail-closed)" string
  survives at run_batch3.py:2694 and :2804 inside the clause
  explaining the old label was wrong. That is the correction's
  audit trail, not a mislabel. No change requested.
- INFO-2: pre-existing miss, identical in fix6 and fix7, out
  of fix7 scope: `bash -c "echo hi; python3 -c 'import
  run_batch3'"` returns False in both blobs, although a real
  shell would execute the runner as the second command. It sits
  next to the recorded import-branch residual (a python -c in a
  later top-level command treated as nested) but the recorded
  form requires an earlier shell -c, while here the earlier
  command is plain `echo hi`. Worth one accurate record sentence
  in a future pass; not a fix-pass-7 item, since fix7 neither
  caused it nor touched that path.
- INFO-3: two run_foo.py processes (PIDs 18546, 18554) were
  observed transiently during the review window and had exited
  on their own (60 s sleep) before exact-PID cleanup was
  attempted; three further run_foo.py processes visible at
  00:19 +07 belong to a concurrent agent's probe loop, not this
  review. Nothing of mine remains running.

## Evidence base

- Author probe: tests/realistic/y14b-fix7-probe.py, 86/86 PASS,
  exit 0, re-run by me. Fix6 probe: 71/71 PASS, exit 0, re-run
  by me.
- Council probe: /tmp/c3-fix7-probe.py (43 checks: 40 PASS as
  written; 3 initial FAILs re-derived as probe errors in
  section 8; corrected live (b) True fix7 / False fix6).
  Fix6-blob differential over the same battery: exactly 7
  moves, all fixed direction, zero wrong-direction moves.
- Direct git evidence: blob/md5 values in section 1, diff
  hunks in section 1, line numbers cited throughout are from
  the 65d669b blobs unless stated otherwise.
