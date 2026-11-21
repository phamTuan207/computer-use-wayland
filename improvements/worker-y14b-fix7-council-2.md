# Council 2 review: Y14b fix pass 7 (run_batch3.py guard)

Verdict: **AMEND**

Reviewer: Council 2 (voice 2, fix pass 7). Scope: ONLY the fix-pass-7
diff, commit 65d669b (parent d76daba), in tests/realistic/run_batch3.py
plus improvements/worker-y14-batch3-live-plan.md,
improvements/worker-y14b-restage-log.md, and the new
tests/realistic/y14b-fix7-probe.py. I re-verify my own fix-pass-6
findings C6-1..C6-6 first, then the redteam R6-1..R6-4 items, then
probe for new edge cases the fix may have introduced. Every claim
below is my own reproduction with the exact command and output;
nothing is taken from the fix author's log on trust. My probe is
/tmp/y14b-fix7-c2-probe.py, written fresh for this review (118 unit
checks, 5 live checks; the /tmp copy is scratch, the method and the
case list are recorded here and the committed author probes were
also re-run by me, see below).

## Hashes verified (by me, direct git commands, not from the log)

- Commit 65d669b: `65d669b5efd3be927d64e2d516dd8258a310d34c`
  (git rev-parse). Parent d76daba:
  `d76daba8d8a5f4172a46bf0b4a683d10c189e1fe`.
- run_batch3.py at 65d669b: git blob
  `8df578c7013fc096a30470667ae57bf994884280`, md5
  `0d98342e57c44464752cf08715ac3861`. Both match the brief and the
  plan pin.
- run_batch3.py at the parent d76daba: git blob
  `261f09aed1b52c7b80b0b2fc260f13f70fafd142`, md5
  `fac96935988b9c327dcbe9b3cfa1342e`. Both match the brief. This is
  the fix-pass-6 code (commit d552f4d, which I verified carries
  the same blob and md5: `git show d552f4d:tests/realistic/
  run_batch3.py | md5sum` gives fac96935). The log's "Parent
  fix-pass-6 bytes: blob 261f09ae, md5 fac96935, commit d552f4d"
  is therefore consistent: d76daba is a later commit that did not
  touch run_batch3.py.
- Fix-pass-5 bytes for differentials: blob ff4a5358, md5 9e99d9aa,
  commit 46e0909 (verified: `git show 46e0909:tests/realistic/
  run_batch3.py | md5sum` gives 9e99d9aa).
- The diff is 4 files, 668 insertions, 52 deletions
  (`git diff --stat d76daba 65d669b`). The run_batch3.py code diff
  is 221 lines, 6 hunks, all read in full: _quote_states,
  _top_level_sep_index, _runner_basename_head,
  _is_runner_cmdline docstring, the import-branch comment, and
  the _in_shell_c_string docstring. No other code changed.
- py_compile OK on both blobs; import OK.

## My fix-pass-6 findings: closure table

All re-proved with my own probe /tmp/y14b-fix7-c2-probe.py
(unit run plus --live run; unit 118 PASS except the 2 intentional
C7-1 FAILs below; live 5/5 verdicts PASS, 5/5 cleanups PASS).
Differential fix5 / fix6 / fix7 blobs loaded as separate modules
via stubbed sibling imports.

- C6-3 CLOSED as specified, with one residual: see C7-1. b14
  (`python3 run_foo.py(x`) is False in fix7 (was True in fix6);
  b19 (`python3 run_foo.py)`) is False in fix7 (was True in
  fix6); `python3 run_foo.py()` is False in fix7 (was True in
  fix6). b1-b7 stay True: bash -c glued `;echo`, `&&echo`,
  `||echo`, `|cat`, `&echo`, and direct `python3 run_foo.py;echo`
  and `python3 run_foo.py&&echo`. b8-b13 stay False: `md5sum`,
  `echo`, `vim run_foo.py`; `md5sum run_foo.py;echo`;
  `echo run_foo.py&&x`; `vim run_foo.py|cat`. Helper level:
  `_runner_basename_head("run_foo.py(x")` returns the full
  string, `"run_foo.py;echo"` still cuts to `"run_foo.py"`.
  The docstring (run_batch3.py:2532) now lists the grep -r form
  alongside echo/ssh/cat in the _is_runner_cmdline docstring
  (line 2681: "`grep -r bash -c run_batch3.py`"), closing the
  C6-3 note.
- C6-1 CLOSED. Log line 1006 at 65d669b now reads
  `` `base.rstrip(";,()&|")` (mirroring the import branch), so ``
  with the annotation "(Fix pass 7, Council 2 C6-1: this bullet
  originally stated the pre-extension set `";,()"`; the shipped
  fix-pass-5 code was `";,()&|"`. The rstrip is itself
  superseded by the fix-pass-6 head-before-first-separator
  check, and the fix-pass-7 paren drop.)" Verified by reading
  the log at 65d669b, line 1006 exactly.
- C6-2 CLOSED. The _top_level_sep_index docstring
  (run_batch3.py:2474) now states: "The direct leaf form
  (\"a=1;\") has no quotes; this helper DOES return a top-level
  index for it (3, not -1), and the direct case is safe only
  because its caller applies no separator stop there (the
  separator is Python code by the direct-vs-nested rule, not by
  this helper) (fix pass 7, Council 2 C6-2)." I measured it
  myself: `_top_level_sep_index("a=1;", False, False)` returns
  3 in both blobs (fix6 and fix7, unchanged, as the log says).
- C6-4 CLOSED at both sites, with a correction to the brief (see
  C7-2). The import-branch comment (run_batch3.py, lines
  2822-2832) now cites `python3 -c "import os" echo import
  run_batch3` as the B12 form, with the note
  that the earlier cited glued-";" form "returns False in both
  fix5 and fix6 and does not demonstrate the gap". The log's
  fix-pass-6 adjudication item 4 (log lines 1700-1715) carries
  the same correction. Differentially proved by me:
  no-separator form True in fix5, False in fix6, False in fix7;
  glued-";" form False in fix5, fix6, and fix7; genuine
  single-element forms stay True.
- C6-5 CLOSED going forward. Both probes are committed at
  65d669b: tests/realistic/y14b-fix6-probe.py (blob cdac7ff)
  and tests/realistic/y14b-fix7-probe.py (blob 899b113). I
  re-ran both from the repo: fix7 probe 86 PASS, 0 FAIL;
  fix6 probe 71 PASS, 0 FAIL (counts by PASS lines, not the
  summary; the "FAILURES: 0 []" line is the only line starting
  with FAIL and is the summary, not a failure). The fix7
  probe's arithmetic checks out: 71 fix6 cases + 15 new
  (R6-1 3 + 2 controls + R6-2/C6-3 4 paren + 4 separator
  controls + 2 live) = 86.
- C6-6 (my own disclosure, no code impact) NOT REPEATED. No
  pkill -f used in this review; every stub killed by exact PID
  (children first, then wrapper). Final orphan sweep: no stubs
  remain. One note: the committed fix6 probe still orphans
  children on every run (see C7-3).

## Redteam R6 items: verification

- R6-1 (U1, REQUIRED) FIXED in code, all three forms, unit and
  live. Differential fix6 False to fix7 True for each:
  (a) codex prompt `a \"b; marionette` (unit, codex predicate);
  (b) python -c code `x=\"a\\\"b\"; import run_batch3` (unit,
  runner predicate); (c) shell apostrophe idiom `don'\''t stop;
  marionette` (unit, codex predicate). Live, on real /proc
  cmdlines with the dummy codex in PATH: (a) True, (c) True,
  and (b) True (my own live case; the author's probe live-tests
  only (a) and (c)). For (b) live I append `; sleep 5; echo
  done`, not just `; sleep 5`: with a bare trailing sleep, bash
  execs the sleep and the wrapper's /proc cmdline reads `sleep
  5`, so the probe would test nothing (my first live run caught
  exactly this: cmdline `sleep 5`, verdict False; the
  construction was fixed, not the code). The escape rule does
  NOT break the existing quote cases: B3-B7, B11, B13, d4,
  C5-1 B5-B7, C2-3 cases, F2, R3, and the fix6 apostrophe edges
  (f3/f4/f5: bare don't True, don't in double quotes True,
  `'don't; echo marionette'` False) all agree between fix6 and
  fix7. New edges I invented also hold in both blobs: an
  escaped backslash before a closing quote closes the quote, so
  the `;` after it is a real separator (False); a backslash
  inside single quotes is literal, so the `;` stays inside
  (True); an escaped `\;` inside double quotes is not a
  separator (True). Helper level: `_quote_states` on the
  escaped-quote tokens gives the inside-single-quotes state
  before `marionette'` as claimed, and
  `_top_level_sep_index('\\"b;', False, True)` returns -1.
- R6-2 CLOSED for the three named forms (same evidence as C6-3
  b14/b19/`run_foo.py()`), with the C7-1 residual below.
- R6-3 NO ACTION, as adjudicated. Not re-probed (already
  recorded accurately); nothing in this diff touches it.
- R6-4 (U3, PAPERWORK) CLOSED. The _in_shell_c_string docstring
  (run_batch3.py:2937) now carries the bounding sentence naming
  the exact no-separator form: "Bound (fix pass 7, redteam
  R6-4, pre-existing, fail-closed, narrow, recorded not
  fixed): the R5-4 skip only fires when a top-level separator
  lies between the non-shell -c and the token. With no
  separator before codex (`bash -c \"python3 -c
  'x=1;__import__(\\\"time\\\").sleep(60)' codex --help; echo
  marionette\"`), the wrapper flags True although no codex
  process exists at all (live-proven)." I verified the
  behaviour too: that form returns True in both blobs
  (pre-existing FP, unchanged), while the R5-4 with-separator
  control still returns False.
- U-C3-1 / INFO-1 CLOSED. The "(fail-closed)" label is replaced
  with the synthetic-only wording in both places: the
  _is_runner_cmdline docstring (line 2691: "synthetic-only,
  recorded not fixed: a single /proc cmdline cannot hold two
  top-level commands from a real shell launch, so no live
  runner is missed") and the import-branch comment (line 2800:
  "that form is synthetic-only (a single /proc cmdline cannot
  hold two top-level commands from a real shell launch, so no
  live runner is missed)"). Remaining "fail-closed" mentions
  in the file (lines 2447, 2642, 2671, 2683, 2694, 2804, 2958,
  3004, 3270) are other findings' own labels, correction-context
  quotes of this same sentence, or an unrelated server-timeout
  use, not this sentence.
- Plan md5 CLOSED. The plan md5 line (plan lines 611-619) pins
  the fix-pass-7 values IN the fix commit: md5
  0d98342e57c44464752cf08715ac3861, blob
  8df578c7013fc096a30470667ae57bf994884280, with the fix-pass-6
  values (md5 fac96935, blob 261f09ae, commit d552f4d) kept as
  superseded. The fix-pass-7 commit hash itself is in the
  follow-up hash-record commit d3e0a76, which is the
  established pattern (the hash cannot be known before
  committing).

## Author's probe claims checked

- Fix7 probe 86/86: re-run by me, 86 PASS lines, 0 FAIL, exit 0.
  Fix6 probe 71/71: re-run by me, 71 PASS lines, 0 FAIL.
- The "bare dont" control expectation change (False to True)
  is justified, not a code dodge: I verified independently
  that the form returns True at unit level in both blobs and
  that bash exits 2 on it (`bash -c "codex -c don't stop; echo
  marionette"`, exit 2, "unexpected EOF while looking for
  matching `''"), so it never reaches a live scan. The
  unbalanced-apostrophe fail-closed reading in the
  _quote_states docstring already records this.
- The log's "92 same, 6 diff, ALL 6 in the FIXED direction,
  zero wrong-direction moves" differential claim is REFUTED
  by C7-1 below: my differential finds 2 more shapes moving
  in the wrong direction (False in fix6 to True in fix7) that
  the author's 98-case set did not cover. The author's /tmp
  diff probe is not committed, so I could not re-run it
  verbatim; I re-derived the differential from the committed
  blobs instead (fix5/fix6/fix7 via git).

## Findings

### C7-1 (LOW, code): the paren drop re-exposes the fix5 false positive for mid-name parens

Evidence: `_script_basename_is_runner` (run_batch3.py:2217)
matches `name.startswith("run_") and name.endswith(".py")`.
The fix6 paren cut truncated the head at the first paren, so
a mid-name paren suppressed the match; dropping the cut
restores the fix5 behaviour for these shapes:

- `python3 run_foo(a).py`: fix5 True, fix6 False, fix7 True.
- `python3 run_(foo).py`: fix5 True, fix6 False, fix7 True.
- Same for the bash -c form (`bash -c "python3
  run_foo(a).py"`: fix5 True, fix6 False, fix7 True).

Real execution opens a literal file named `run_foo(a).py`;
run_foo.py never runs. So these are false positives of the
exact class C6-3 named ("a direct argv like run_foo.py(x is
a literal filename"), and the fix7 docstring's own principle
applies to them equally. The shapes that stay False show the
boundary precisely: `run_foo.py(a)` is False (ends with `)`,
not `.py`); extensionless `run_foo(a)` is False in all three
blobs; spaced `run_foo (a).py` is False in all three blobs.
Only parens sitting before the `.py` suffix in a `run_*.py`
name now flag.

Why this is AMEND, not BLOCK: fail-closed, contrived literal
filenames, same severity as C6-3 itself, and fix7 is still
strictly better than fix5 on parens (3 of 4 shapes fixed:
`run_foo.py(x`, `run_foo.py)`, `run_foo.py()` all False now)
and better than fix6 on those 3, worse than fix6 only on
this 1 shape. But it must not ship silently, and the log's
"zero wrong-direction moves" claim must be corrected, for
the same reason C6-3 was AMEND in fix6.

Fix (preferred, one line): reject parens in the runner
basename match, since no real runner name contains them, for
example at the top of `_script_basename_is_runner`: return
False if "(" or ")" is in the name. Its only call site is
line 2724 (via `_runner_basename_head`), so the change is
contained. Then re-prove: `run_foo(a).py` and `run_(foo).py`
False, b14/b19/`run_foo.py()` still False, b1-b7 still True.
Alternative: record the mid-name-paren false positive in the
`_runner_basename_head` docstring and correct the log's
zero-wrong-direction claim. Either closes this finding; the
docstring sentence "dropping it is the same correction, not a
new regression" also needs touching, since the drop does
re-expose a fix5 behaviour the cut was suppressing.

### C7-2 (INFO, record correction, not an author error): the brief's C6-4 parenthetical is wrong

My task brief said to prove the no-separator B12 form as
"True in fix6 blob, False in fix7 blob". Measured: True in
fix5, False in fix6, False in fix7. The code and the log are
right (both state "True in fix5 and False in fix6"); the
brief's parenthetical is the error. My first probe draft
followed the brief and failed on it; the expectation was
corrected to the measured values, and the differential above
is the proof. No author action; recorded here so the next
brief does not repeat it.

### C7-3 (INFO, process): the committed fix6 probe still orphans children on every run

Re-running the committed fix6 probe left 2 orphan
`run_foo.py` children per run (its live helper kills only
the wrapper, not the children; the fix7 log already discloses
this as the C6-6 lesson). I killed the ones my runs left
(18400, 18546, 18554, by exact PID) and verified the final
sweep is clean. The fix7 probe's live helper kills children
first and left no orphans in my runs. Recommendation: patch
the fix6 probe's live helper the same way, so re-running the
committed suite does not litter sleep-60 stubs. Not required
for ship.

## Regressions

- My probe: unit 118 PASS, 2 FAIL (both the intentional C7-1
  FAILs); live run 128 PASS, 2 FAIL (same 2). Two earlier
  FAILs in my probe's first draft were my own probe bugs, not
  the code: the _quote_states expectation listed the state
  AFTER token `"a` instead of before it (the function records
  the state before each token), and the C6-4 fix6 expectation
  followed the brief's wrong parenthetical (see C7-2). Both
  corrected, both now pass.
- One live-construction lesson, recorded for future probes:
  a bare trailing `sleep` in a bash -c string gets exec'd by
  bash, replacing the wrapper, so /proc reads `sleep 5`
  instead of the wrapper cmdline. Append a trailing builtin
  (e.g. `; echo done`) after the sleep. The author's live
  cases avoid this because their first command is a sleep-60
  dummy that is still running at read time.
- No other regression found. The only behaviour change in the
  fix6-to-fix7 differential that moves in the wrong direction
  is C7-1. Everything else that flipped is a fix (R6-1 three
  forms, C6-3 three forms).

## Hygiene

- No em/en dash in the fix diff (python count on the
  d76daba..65d669b diff: U+2014 0, U+2013 0). No em/en dash in
  this paper (verified by grep before commit).
- "ydotool" appears once in the diff, inside the log's hygiene
  sentence "no ydotool lines in the fix diff (grep 0)". No
  ydotool use; 0 ydotool lines in the code diff.
- No personal info in the diff (email regex: 0 hits; no
  addresses, phone numbers, or credentials).
- No live Zen driving, no browser work in this review.

## Required fixes for ship (AMEND, not BLOCK)

1. C7-1: reject parens in the runner basename match (one line
   in `_script_basename_is_runner`, only call site line 2724),
   or record the mid-name-paren false positive in the
   `_runner_basename_head` docstring. Re-prove `run_foo(a).py`
   and `run_(foo).py` False, b14/b19/`run_foo.py()` still False,
   b1-b7 still True. Correct the log's "zero wrong-direction
   moves" claim in the fix-pass-7 verification section.
2. C7-3 (process, may land with the fix): patch the committed
   fix6 probe's live helper to kill children first, as the
   fix7 probe already does.

Everything else in the fix-pass-7 scope is verified closed:
C6-1, C6-2, C6-3 (as specified), C6-4, C6-5, C6-6 (not
repeated), R6-1, R6-2, R6-4, U-C3-1/INFO-1, the C6-3 grep -r
note, and the plan md5 pin in-commit. Nothing here blocks ship
on its own: every miss is leaf-masked live, the one new false
positive is fail-closed and contrived, and the doc errors do
not touch the live ship-time pin (which is correct). But C7-1
is a fix-pass-7-introduced wrong-direction move with a one-line
fix that costs nothing demonstrated, so it must not ship
silently. AMEND.

## Appendix: event log (wall-clock Asia/Ho_Chi_Minh)

- 00:16 +07: review starts. Diff read (d76daba..65d669b, 4 files,
  668 insertions, 52 deletions); fix-pass-6 paper re-read
  (worker-y14b-fix6-council-2.md); hashes verified (blob
  8df578c7, md5 0d98342e; parent blob 261f09ae, md5 fac96935).
- 00:16 +07: pre-existing stubs noted: 4 orphan run_foo.py
  processes (17850, 18068, 18083, 18107), not mine, left
  untouched; they exited on their own within the minute
  (sleep 60). Doc checks done (log line 1006, both C6-4 sites,
  synthetic-only both sites, R6-4 sentence, grep -r, plan md5).
- 00:17 +07: author probes re-run from the repo: fix7 probe
  86/86 PASS, fix6 probe 71/71 PASS. The fix6 probe left
  orphan 18400 (killed by exact PID). Second fix6-probe count
  run left orphans 18546, 18554 (killed by exact PID).
- 00:18 +07: my probe /tmp/y14b-fix7-c2-probe.py written
  (fresh cases). Unit run v1: 3 FAILs (2 probe bugs, 1 real:
  C7-1 run_foo(a).py). Fix5 blob loaded (46e0909, md5 9e99d9aa);
  differential confirms run_foo(a).py True/False/True and
  B12 no-sep True/False/False across fix5/fix6/fix7.
- 00:20 +07: bare-dont bash exit verified: exit 2 (background
  delivery). Probe v2 unit: 115 PASS, 2 intentional C7-1
  FAILs. Live v2: (a) and (c) PASS, (b) FAIL on construction
  (bash exec'd the trailing sleep; cmdline read `sleep 5`);
  cleanup FAILs were a zombie-reaping race (final sweep clean).
- 00:21 +07: probe v3 live: 5/5 verdicts PASS, 5/5 cleanups
  PASS, no stubs remain. Extra shapes measured: run_foo(a)
  extless False in all blobs, spaced `run_foo (a).py` False
  in all blobs.
- 00:22 +07: final counts (my probe unit 118 PASS, live run
  128 PASS, 2 FAIL both C7-1); hygiene checks (0 dashes, 0
  emails, ydotool only in the log sentence, no PII, no Zen
  driving). Paper written.
