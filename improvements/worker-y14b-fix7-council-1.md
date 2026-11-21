# Council 1 review: Y14b fix pass 7 (voice 1)

- Verdict: **GO**
- Scope: ONLY the fix-pass-7 diff, commit `65d669b` (parent `d76daba`),
  4 files, 668 insertions, 52 deletions.
- Reviewer: independent council, voice 1. Owner is asleep; review
  run autonomously, no questions asked.
- Started 00:16 +07, 2026-11-22. Paper finished 00:37 +07.
  Elapsed about 21 minutes.
- Method: my own differential probe (fix5 blob `ff4a5358`,
  fix6 blob `261f09ae`, fix7 blob `8df578c7` loaded side by side
  from git objects, never the working tree), plus live `/proc`
  checks with the `/tmp/y14b-dummies` stubs (`PATH` prefixed),
  plus direct git hash checks. Every stub killed by exact PID
  (children first, then wrapper); orphan sweep after the run: 0.
  No live Zen driving, no browser work, no `git fetch`.

## Evidence base

- Author probe rerun (not trusted, re-derived): `python3
  tests/realistic/y14b-fix7-probe.py` gives 86 PASS lines,
  0 FAIL, exit 0. `python3 tests/realistic/y14b-fix6-probe.py`
  on the fix7 tree gives 71 PASS, 0 FAIL, exit 0 (no
  regression in the fix6 set).
- My probe `/tmp/y14b-c1-diffprobe2.py` (v2): **53/53 PASS**,
  0 failures, covering unit, helper, live `/proc`, and shell
  semantics. v1 failed 19/52; all 19 were MY probe bugs (see
  "My own v1 errors" below), not code bugs. v2 corrects my
  probe; the code under review is unchanged between v1 and v2.
- Diff saved at `/tmp/y14b-c1-fix7.diff` (843 lines).

## Claim 1: R6-1 backslash escapes (REQUIRED) - VERIFIED

Code: `tests/realistic/run_batch3.py`, `_quote_states`
(lines 2434-2464 in fix7) and `_top_level_sep_index`
(lines 2476-2522) now skip the char after a backslash when
outside single quotes. The rule matches the shell rule for
quote toggling: outside quotes a backslash escapes any char;
inside double quotes `\"` is an escape; inside single quotes
the backslash is literal.

All three proven forms, unit and live, fix6 False to fix7 True:

| Form | Unit fix6 | Unit fix7 | Live fix6 | Live fix7 |
|---|---|---|---|---|
| (a) codex prompt `a \"b; marionette` | False | True | False | True |
| (b) python -c `x=\"a\\\"b\"; import run_batch3` | False | True | False | True |
| (c) apostrophe idiom `don'\''t stop; marionette` | False | True | False | True |

Live (b) is my own addition: the author probe has live (a)
and (c) only. My live (b) puts a sleep inside the python -c
code so bash stays the wrapper while I read `/proc`
(`python3 -c "x=\"a\\\"b\"; __import__(\"time\").sleep(60);
import run_batch3"; sleep 60`, wrapper cmdline read intact,
fix6 False, fix7 True).

No regression in the existing quote cases (all match fix6):
R5-1 B1/B12/d4, C5-1 B5/B6/B7, C2-3 (spaced `&`, glued `;`,
spaced `&&`, spaced `;`), F2, R3/R4 controls, R5-4 fixed
case, R5-3 C1-C5, R5-8. The bare-`don't` form returns True
at unit level in fix5, fix6, and fix7, and bash exits 2
(`unexpected EOF while looking for matching '''`), so it
never reaches a live scan; the author's probe correction
(first run 85/86, expectation fixed to True) is correct,
and the log records it honestly.

Helper level: `_top_level_sep_index("a=1;", False, False)`
is 3 in both blobs (C6-2, unchanged); escaped-quote
`a\"b;c` is 4 in fix7, -1 in fix6 (the fix); escaped `\;`
is -1 in fix7, 2 in fix6 (literal semicolon, correct shell
semantics); double backslash `a\\;b` is 3 in both (the `;`
is a real separator, both agree).

## Claim 2: C6-3/R6-2 paren drop (REQUIRED) - VERIFIED

Code: `_runner_basename_head`, fix7 lines 2531-2552. Cut set
is now `";", "&", "|"` only; `"("` and `")"` dropped.

Paren forms now False (fix6 True, fix7 False), unit and live:

- `python3 run_foo.py(x` direct: False (live `/proc` via
  sleeper exec, cmdline `python3\0run_foo.py(x\0`: fix6 True,
  fix7 False).
- `bash -c python3 run_foo.py(x`: False.
- `python3 run_foo.py)`: False (fix5 True, fix6 True).
- `python3 run_foo.py()`: False, direct and bash -c wrapped.

Separator forms still True (fix6 True, fix7 True), unit and
live: `run_foo.py;echo`, `run_foo.py&&echo`,
`run_foo.py|cat`, `run_foo.py&echo`, `run_foo.py||echo`.
Live `;` control via bash -c with the real dummy passes
both blobs. No true case is lost in my 53-case set: the
only fix6-to-fix7 moves are the 3 R6-1 forms (False to
True), the 5 paren forms (True to False), and 1 synthetic
escaped-`;` case (False to True, intended by the escape
rule). Zero wrong-direction moves.

Shell semantics checked independently of the predicates:
`bash -c 'python3 run_foo.py(x'` exits 2 (syntax error
near unexpected token `(`), `bash -c 'python3 run_foo.py()'`
exits 2, confirming the docstring claim that a paren in
argument position is a syntax error, not a runner launch.

## Claim 3: doc fixes - VERIFIED, all 7

- C6-1: log line 1006 area now states the rstrip set
  `";,()&|"` with the fix-pass-7 annotation. Confirmed
  against the fix5 blob: line 2539 of `ff4a5358` is
  `base.rstrip(";,()&|")`. The old `";,()"` was the
  pre-extension set, as the annotation says.
- C6-2: `_top_level_sep_index` docstring, fix7 line 2502,
  states the helper DOES return a top-level index for an
  unquoted `a=1;` (3, not -1). Measured 3 in both blobs.
- C6-4: B12 example is now the no-separator form
  `python3 -c "import os" echo import run_batch3` in the
  import-branch comment (fix7 line 2825) AND in the log
  adjudication item 4 (line 1704). My probe confirms the
  correction: the no-separator form is True in fix5 and
  False in fix6, while the old glued-`;` form is False in
  fix5 AND fix6, so the old form did not demonstrate the gap.
- U-C3-1 / INFO-1: the `(fail-closed)` label is replaced
  with the synthetic-only wording in the `_is_runner_cmdline`
  docstring (fix7 line 2691) and in the import-branch comment
  (line 2800). The old label survives only as history
  ("the old `(fail-closed)` label was the wrong direction",
  lines 2694 and 2804). Remaining `fail-closed` hits in the
  file are other findings (R5-8, R6-4 bound, `_quote_states`
  caveat), not this sentence.
- R6-4 / U3: one bounding sentence in the `_in_shell_c_string`
  docstring (fix7 lines 2958-2964) naming the exact
  no-separator form. Verified live: the wrapper flags True
  although no codex process exists (wrapper cmdline read
  from `/proc`, fix6 True, fix7 True, documented FP).
- C6-3 note: `grep -r bash -c run_batch3.py` added to the
  C2-5 list in the `_is_runner_cmdline` docstring (fix7 line
  2681), and the author probe covers it as a recorded-FP unit
  case (PASS).
- Plan md5: `improvements/worker-y14-batch3-live-plan.md`
  lines 614-615 pin the fix-pass-7 values IN the fix commit
  (md5 `0d98342e57c44464752cf08715ac3861`, blob
  `8df578c7013fc096a30470667ae57bf994884280`).

## Claim 4: hashes - VERIFIED by direct git commands

- At `65d669b`: `git ls-tree` gives blob
  `8df578c7013fc096a30470667ae57bf994884280` for
  `tests/realistic/run_batch3.py`; `git show 65d669b:...`
  piped to md5sum gives
  `0d98342e57c44464752cf08715ac3861`. Both match the claim.
- At parent `d76daba`: blob
  `261f09aed1b52c7b80b0b2fc260f13f70fafd142`, md5
  `fac96935988b9c327dcbe9b3cfa1342e`. Both match the claim.
- Fix-pass-6 commit `d552f4d` carries blob `261f09ae` and
  is an ancestor of `65d669b` (`git merge-base
  --is-ancestor` yes). Fix-pass-5 blob `ff4a5358` md5s to
  `9e99d9aa`, matching the plan's recorded fix-pass-5 value.
- HEAD at review time is `d3e0a76` (hash-record follow-up on
  top of `65d669b`); its `run_batch3.py` is blob `8df578c7`.

## Claim 5: hygiene - VERIFIED

- 0 em dash, 0 en dash in the full fix diff (Python count
  over `/tmp/y14b-c1-fix7.diff`, 843 lines).
- No ydotool use: the only `ydotool` line in the diff is the
  log sentence stating the fix diff greps 0 for it.
- No personal info: grep for the owner's Gmail handle,
  Hanoi address, and phone patterns over the diff returns 0.
- No live Zen driving: the diff touches no browser or Zen
  code; all probes use `/tmp` stubs only.
- t10 untouched: 0 added or removed `t10` lines in the
  `run_batch3.py` diff; the 2 `t10` hits in the whole diff
  are context lines in the plan file (pre-existing
  "t10 translation 69/69" note). All 7 `run_batch3.py`
  hunks sit in lines 2434-2954 (the guard region); no hunk
  near `run_b3_t10`.
- New probe file `tests/realistic/y14b-fix7-probe.py` is 379
  lines, added in this commit.

## My own v1 errors (recorded, not hidden)

My first differential probe failed 19/52. All 19 were my
probe's faults, and I say so plainly because a council
that hides its own miscounts is worth nothing:

- 13 unit cases dropped the enclosing quotes on `-c`
  arguments. A real `/proc` cmdline carries the `-c` code
  as ONE argv element WITH its quotes; the predicates
  flatten on whitespace, so the quote chars must stay
  attached to the tokens. v2 re-derives each case from the
  real `/proc` shape and all 13 pass.
- 4 edge expectations had the shell semantics backwards
  (double backslash before a quote closes the quote, so
  the `;` after it IS top-level; `\\;` is a real separator).
  The code was right in all 4; my expectations were wrong.
- 1 live (b) case let bash exec-replace the wrapper with
  `sleep 60` before my `/proc` read (the python -c exited
  instantly). v2 sleeps inside the python -c code and the
  wrapper cmdline reads intact.
- 1 edge case was a synthetic flat form with no enclosing
  `-c` quotes; reframed as a behaviour-change demo with
  corrected expectations.

## Non-findings

- The fix-pass-6 redteam paper
  (`improvements/worker-y14b-fix6-redteam.md`) is
  uncommitted in this shared checkout; I did not stage,
  commit, or touch it, and I ran no `git fetch`, per the
  brief. Its R6-1/R6-2 findings are the basis of this fix
  pass and are confirmed above from the blobs, not from
  trusting the paper.
- The author's earlier `/tmp` probes are gone (known loss,
  C6-5). The committed probes exist and pass (86/86, 71/71),
  so this is not a new finding.
- The author probe covers live R6-1 (a) and (c) but not
  live (b). I closed that gap myself (live (b) passes);
  no action needed from the author.

## Verdict: GO

Fix pass 7 does exactly what its adjudication claims: the
R6-1 escape rule flips the three proven forms from False
to True (unit and live) with no regression in the existing
quote cases; the C6-3/R6-2 paren drop flips the five paren
forms from True to False with no true case lost; all seven
doc fixes are present at the cited lines with the cited
wording; the hashes verify by direct git commands; hygiene
is clean; t10 is untouched. No AMEND item, no BLOCK item.
