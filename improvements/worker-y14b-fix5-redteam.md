# Fix-pass-5 redteam: AMEND

Scope: ONLY the fix-pass-5 diff, commit
46e0909058af1419c0ef6534394a68019ec8ebd8 (branch todolist-push),
against its parent bf3c939 (fix pass 4). Code changes in
tests/realistic/run_batch3.py; the plan got the F3/F5/H4 doc
fixes and the fix-pass-5 md5 pin; the log got the fix-pass-5
adjudication and verification. Method: re-ran every claimed
verification number against the current tree; wrote an
independent unit probe (/tmp/y14b-fix5-rt-probe.py, 45 checks)
and an independent live probe (/tmp/y14b-fix5-rt-live.py, 16
checks, /proc scans plus sleeping stubs and one real compiled
codex binary); ran a fix4-vs-fix5 differential
(/tmp/y14b-fix5-rt-diff.py) over every attacked case so a
pre-existing issue is never blamed on fix5; prototyped the
deferred C3-2 fix (/tmp/y14b-fix5-rt-c32.py, 14 checks) to
measure whether the deferral is forced or a choice; verified
the live shell/Python semantics of every disputed form with
real runs. No Zen driving, no ydotool, no live browser work.

## Verdict: AMEND

Fix5 lands everything it claims for the forms it probed: the
R2 wrapper cases, the R3/R4 glued-separator cases, the C2-1
trailing-glue cases, the C2-2 bare-& cases, and all the doc
fixes verify. But the fix introduces 12 regressions of its own:
12 cmdlines that returned True in fix4 now return False in
fix5 (8 from the new top-level-separator heuristic, 4 from the
new _owning_command walk-back). That is the exact pattern the
fix-pass-4 redteam called AMEND for in R2 (9 cmdlines
True-to-False, "a fix pass must not erode the previous pass").
Live gate impact is NIL in every case I could build (the leaf
or child process is always caught, except L5, which is an
over-approximation case with a __main__-guard caveat), so this
is AMEND, not BLOCK. Ship after U1 and U2 (both small, both
specified below, with acceptance tests). U3 and U4 are
fix-or-record; U5 is paperwork.

## Hash record (verified by me, not taken from the log)

- Commit 46e0909058af1419c0ef6534394a68019ec8ebd8.
- run_batch3.py at 46e0909: git blob
  ff4a5358ac7f621a1fd649c36cec94da2031399d, md5
  9e99d9aa1bcdbb525407adfb31e0692b.
- Parent bf3c939: git blob
  585fb8016b0618ab02b3e97afa362dbcce7342c9, md5
  2920f1697edb3b33711b83b8a874d88b.
- Working file matches: `git diff 46e0909 HEAD --
  tests/realistic/run_batch3.py` is empty (0 lines), so the tree
  reviewed is the commit reviewed.
- Commit 46e0909 touches exactly 3 files (run_batch3.py, plan,
  log). The bf3c939..46e0909 range diff shows 75 files, but
  that range includes other workers' merged work; the fix5
  commit itself is 3 files only.

## Verification re-runs (all against the current tree)

PASS lines counted only, not the "FAILURES:" summary line.
Every probe exited 0 except my own redteam probes, whose
non-zero exit is the findings themselves.

- Fix5 probe /tmp/y14b-fix5-probe.py: 38/38 PASS.
- Fix4 probe /tmp/y14b-fix4-probe.py: 64/64 PASS.
- Fix3 probe /tmp/y14b-fix3-probe.py: 70/70 PASS.
- Fix2 probe /tmp/y14b-fix2-probe.py: 31/31 PASS.
- H2 probe /tmp/y14b-h2-probe.py: 45/45 PASS.
- Transcription /tmp/y14b-transcribe.py: 82 PASS.
- Gate dry /tmp/y14b-gate-dry.py: 4/4 PASS.
- M1 probe /tmp/y14b-m1-probe.py: 3/3 PASS.
- M1 all-12 /tmp/y14b-fix2-m1-probe.py: 4/4 PASS.
- Council 2 extra probe /tmp/y14b-fix4-c2-probe.py: 36/46
  PASS, the same 10 named failures as the author reports.
  I verified each of the 10 case by case (see below); all 10
  are flips in the intended direction, not regressions.
- py_compile OK; import OK.

## Council 2 extra probe: the 10 "failures" are all fixes

Each FAIL line is a fix-pass-4 expectation that fix5
deliberately reverses, with the got value in the fixed
direction:

1. `sep single & alone`: got True, want False (C2-2: "&" is
   now a separator, per Council 2's own fix sketch).
2. `c env bash -c MISS`: got True (R2).
3. `c nice bash -c MISS`: got True (R2).
4. `c sudo bash -c MISS`: got True (R2).
5. `glued; python3 run_foo.py; echo MISS`: got True (C2-1).
6. `glued; bare run_foo.py; echo MISS`: got True (C2-1).
7. `codex -c marker in LATER shell cmd`: got False (R3).
8. `codex single & --help & echo FP`: got False (C2-2).
9. `live glued ; wrapper missed`: got True (C2-1, live).
10. `live double-nested wrapper missed`: got True. Mechanism
    verified by me, not assumed: the outer bash exec-replaces
    itself with the inner bash (a single simple command), so
    the live cmdline of that pid is the single-level `bash -c
    '<stub>; sleep 60'`, which fix5 catches via C2-1. I
    reproduced it directly: live cmdline
    `bash -c /tmp/y14b-c2-dummies/run_shebang.py; sleep 60`,
    tokens `['bash', '-c', '.../run_shebang.py;', 'sleep',
    '60']`, returns True.

The author's claim on all 10 is correct.

## Fix-pass-4 item disposition

- R2/U1 PARTIALLY FIXED. The redteam's A1-A9 all pass, dash
  is added, flock/env/sudo/timeout/nice wrappers pass, the
  fix5 probe's 16 R2 cases are green. But the same walk-back
  now fails a new set of 4 cmdlines (R5-2 below).
- R4/C3-3/C1-R1 FIXED for the forms probed (glued ";"
  after a closing quote, and the direct forms). The spaced
  forms regress (R5-1 below).
- R3/C1-R4 FIXED for the documented form (marker after the
  snippet's closing quote). The spaced forms inside the
  snippet regress (R5-1 below).
- C2-1 HALF FIXED. Trailing glue is fixed (spaced forms:
  `run_foo.py;`, `run_foo.py&&`, `run_foo.py||` all match).
  Mid-token glue still misses (R5-3 below). Council 2's
  stated examples included the no-space forms, so the fix
  does not close the finding as written.
- C2-2 FIXED. Bare "&" is a separator in _is_cmd_separator
  (line 2312) and in _same_command_tokens (line 2741); a "&"
  inside a token is left alone, and my D1/D2 controls confirm
  a URL token does not split and a marker after a URL still
  counts.
- C1-1/C3-1 FIXED. Plan line 738 and log lines 601-602 now
  say `python3 run_other -W ignore run_batch3.py` is False,
  and the code returns False. The fix4 probe label now reads
  "now False (was True in fix3)".
- C3-2 RECORDED. The residual is in the _python_executes
  docstring (lines 2416-2426) with the exact form named
  (`python3 other -W ignore run_batch3.py` returns True) and
  the deferral stated. See R5-6 for the prototype result.
- C3-3 FIXED (same as R4).
- C3-4 FIXED. Plan line 733 and log line 590 now attribute
  the -m example to other.py. (The plan's remaining
  "run_other.py" mentions at lines 698-701 are the -W example,
  which did use run_other.py, so they are correct as written.)
- C3-5 FIXED. Counted from the probe source: `cases` has 39
  entries, `codex_cases` 21, live checks 4, total 64. Per
  section: R1 6, F1 5, F3 9, F4 3, F5 2, regressions 14,
  codex 21, live 4.
- C3-6 FIXED. Log line 688 now says the "72" was a plain
  miscount (70+1=71, not 72).
- C3-7 FIXED. Log line 527 labels F3's unblock U4.
- C3-8 FIXED. Env note updated with the solved root cause
  (log lines 649-653, 737-739, 1053). Verified independently:
  /usr/lib/python3.12/re/__init__.py exists, 16,315 B,
  `import re` OK.
- C3-9 FIXED. U11 parenthetical added to the plan's H4 note
  (plan lines 758-762).
- C1-2 REFUTATION VERIFIED. The plan pins the fix-pass-5
  values at lines 614-615 (md5 9e99d9aa, blob ff4a5358,
  commit 46e0909) and lists the fix-pass-4 values as
  superseded; grep for e9e3519a/3a9b7b17 in the plan returns
  nothing. The log's fix-pass-5 entry records the same blob
  and md5 (lines 1149-1150, 1198-1199, 1208). The fix-pass-3
  values appear in the log only in the historical fix-pass-3
  section (lines 496-497, 550), which is not the live pin.
  Council 1 read a stale file or the historical section.
- C1-R3 RECORDED. The glued `;codex` miss is in the
  known-limitations docstring. My B13 case confirms the
  adjacent _top_level_sep_index limitation is real (R5-5).
- C1-R4 FIXED as R3.

## New findings

### R5-1 LOW, regression vs fix4: a standalone separator inside a -c string truncates the scan

File: tests/realistic/run_batch3.py, _top_level_sep_index
lines 2368-2391, used at line 2599 (import guard) and line
2755 (_same_command_tokens -c branch). _argv_tokens (lines
2289-2310) splits a -c string on whitespace with no quote
awareness, so a SPACED separator inside the string becomes a
standalone separator token, and _top_level_sep_index returns 0
for any standalone separator token. The fix5 heuristic only
saves GLUED separators ("time;"), where the ";" sits inside a
token with no quotes. A separator that is a token of its own
inside the -c value is indistinguishable from a real shell
separator to this helper, so the scan stops there.

Reproduced live (unit probe /tmp/y14b-fix5-rt-probe.py; every
case was True in fix4, verified by loading the fix4 blob
585fb801, and is False in fix5):

- B1 `python3 -c 'import os ; import run_batch3'` False.
  The import is real Python code (verified live: `timeout 5
  python3 -c 'import os ; import run_batch3'` exits 0).
- B2 `python3 -c 'x = 1 ; import run_batch3'` False.
- B3 `bash -c "codex -c 'run tests && restart marionette'"`
  False (codex side). A prompt with a spaced && and a marker
  after it is ordinary prompt language.
- B4 `bash -c "codex -c 'run tests ; restart marionette'"`
  False.
- B5 `bash -c "codex -c 'run tests | grep marionette'"` False.
- B6 `bash -c "codex -c 'run tests & check marionette'"` False.
- B7 `bash -c "codex -c 'run tests || restart marionette'"`
  False.
- B8 `python3 -c 'x = 1 & 2 ; import run_batch3'` False.

Live proof: L1 spawns `bash -c "codex -c 'run tests &&
restart marionette'; sleep 60"` with the real codex binary on
PATH; the wrapper cmdline flags False while the codex child
(cmdline `codex -c 'run tests && restart marionette'`) flags
True, so the gate still refuses. L5 spawns `python3 -c
'import os ; import run_foo'` (cwd /tmp/y14b-dummies); the
process executes the module's top level (it sleeps) while the
gate misses its cmdline; the glued control (`import os;
import run_foo`) flags True. Caveat on L5: run_batch3 itself
has a `__main__` guard (line 3128), so a bare import of it
starts nothing; the import branch is a fail-closed
over-approximation, and the spaced form escapes that rule.
That is why this is LOW, not a live runner escape.

Severity LOW: wrapper-level for codex (the child is caught
live; the direct child form B14 returns True), and an
over-approximation case for the import branch. But it is a
regression in the exact pattern R2 set as AMEND, and the fix
is well specified (see U1). Controls that still pass: the F2
glued case B9 True, the glued python -c case B10 True, the
R3 later-command case B11 False, the R4 case B12 False.

Fix sketch for U1: track quote state while scanning forward
from the -c token (in_single / in_double); a separator is
top-level only when it appears outside quotes. That subsumes
the current heuristic: in `'hello';`, the ";" follows the
closing quote, so it is top-level; in `'import time; x #
marionette'`, the ";" sits inside the quotes, so it is code;
in `'run tests && restart marionette'`, the "&&" sits inside
the quotes, so it is prompt text. Caveat: an apostrophe in a
prompt ("don't") unbalances the tracker, so everything after
it reads as inside quotes; that errs fail-closed (a later real
separator would be missed and the marker scope would extend
too far), which is the safe direction and the same class of
over-approximation the guard already carries.

### R5-2 LOW, regression vs fix4: _owning_command returns a shell's own separate-value flag as the owner

File: tests/realistic/run_batch3.py, _owning_command lines
2340-2365. The walk-back skips flags (start with "-"),
VAR=value assignments, and unknown paths, and returns the
first remaining bare word. A flag OF THE SHELL ITSELF that
takes a separate value sits between the shell and its -c, so
the VALUE is returned as the owner, not the shell.

Reproduced live (unit probe; every case was True in fix4,
False in fix5):

- A1 `bash -o pipefail -c run_batch3.py` False. `bash -o
  pipefail -c 'echo hi'` executes live (exit 0), so this is
  a real shell form.
- A2 `sh -o pipefail -c run_batch3.py` False.
- A3 `bash -O nullglob -c run_batch3.py` False.
- A4 `bash -o pipefail -c codex exec marionette` False
  (codex side).

Live proof: L2 spawns `bash -o pipefail -c
'/tmp/y14b-rt-dummies/run_foo.py; sleep 60'` (shebang stub);
the wrapper cmdline flags False while the leaf python3
process flags True, so the gate still refuses. NIL live
impact.

Boundary, verified by controls A5-A12: a wrapper's
separate-value flag BEFORE the shell is harmless (the
walk-back never reaches it, because the shell is nearer):
`env -u FOO bash -c`, `sudo -u root bash -c`, `timeout -s
KILL bash -c`, `nice -n 5 bash -c` all True. Joined values
(`--signal=KILL`) and path values (`--init-file /dev/null`)
also work. Only a value-taking flag of the shell itself,
between the shell and its -c, breaks the walk-back. (My first
draft of this probe wrongly expected the wrapper-flag forms
to fail; they pass, which pins the boundary exactly.)

Fix sketch for U2: in the walk-back, before returning a bare
word, check whether the token before it is a known
value-taking flag of the shell (-o, -O) and skip both. About
3 lines. Acceptance: A1-A4 True, fix4 probe still 64/64.

### R5-3 LOW, pre-existing, C2-1 half fixed: mid-token glue on the runner token still misses

File: tests/realistic/run_batch3.py, line 2539. The fix5
rstrip (`base.rstrip(";,()&|")`) only strips a separator at
the END of the token (followed by a space). With no space the
separator is mid-token and the token never matches, although
the shell splits it (`python3 run_foo.py&&echo done` is valid
shell; the && is a metacharacter, no spaces needed).

Reproduced live (unit probe; fix4 also False for all five,
so this is an incomplete fix, not a fix5 regression):

- C1 `bash -c "python3 run_foo.py&&echo done"` False.
- C2 `bash -c "python3 run_foo.py;echo done"` False.
- C3 `bash -c "python3 run_foo.py||echo done"` False.
- C4 `bash -c "python3 run_foo.py|cat"` False.
- C5 `bash -c "run_foo.py;echo done"` False.

Live proof: L3 spawns `bash -c "python3
/tmp/y14b-dummies/run_foo.py&&sleep 60"`; the wrapper flags
False while the leaf python3 process flags True. NIL live
impact. Controls: the spaced forms C6/C7 True, and a path
mention C8 (`md5sum run_foo.py;echo`) stays False.

Fix sketch for U3: check the head before the first
separator in the token (mirror _same_command_tokens' glued
handling at lines 2762-2768), or record the exact no-space
forms as a known residual in the docstring.

### R5-4 LOW, pre-existing false positive: _in_shell_c_string nearest -c crosses a separator

File: tests/realistic/run_batch3.py, _in_shell_c_string
lines 2703-2719. Its nearest--c search has no separator
stop, unlike the import branch fix in this same pass. A
python -c in an EARLIER command makes codex in a LATER
command look non-shell, so _is_codex_executor takes the
all-tokens path and a marker from yet another later command
counts.

Reproduced live (unit probe E1; fix4 also True, so
pre-existing, but fix5 fixed this exact blindness in the
import branch and not here):

- E1 `bash -c "python3 -c 'x'; codex exec foo; echo
  marionette"` True, want False. The marker is echo's
  argument in a later command; codex drives nothing.

Live proof: L6 spawns that form with the real codex binary
on PATH (python sleeps 2s first so the codex child exists by
scan time); the wrapper flags True while the codex child
itself (`codex exec foo`, no marker) flags False. The gate
would refuse a launch over an echo. Fail-closed direction,
contrived shape (needs a python -c before the codex in the
same -c string), LOW.

Fix sketch for U4: stop the nearest--c search at a shell
separator, the same stop the import branch now has, or
record the exact form.

### R5-5 INFO, disclosed: separator before the last quote in one token

File: tests/realistic/run_batch3.py, _top_level_sep_index
lines 2368-2391. The docstring discloses this limitation
("a token with a top-level separator BEFORE its last quote
(e.g. \"'a';'b;c'\") is missed"). My B13 case confirms it is
real: `bash -c "codex -c 'a';'b;marionette'"` returns True
(a false positive; the marker names a bogus second command,
not a codex argument). No action; the U1 quote-state sketch
would also close this form, since the ";" after `'a'` sits
outside quotes.

### R5-6 INFO, observation: the C3-2 code fix is small; the deferral is a choice

Prototype /tmp/y14b-fix5-rt-c32.py implements the
script-position barrier the author deferred (skip -W/-X/-c/-m
values to find the script position; the first token in
script position before i blocks). It passes 14/14, including
the traps: `python3 -W ignore run_batch3.py` stays True (the
-W value is skipped, not mistaken for the script), `python3
-m other run_batch3.py` goes False (the -m value IS the
script), `python3 -W ignore -m run_batch3` stays True, and
`python3 other -W ignore run_batch3.py` goes False. The
value-flag set is closed (CPython: -c, -m, -W, -X,
--check-hash-based-pycs; the code already has _PY_VALUE_OPTS
= "cmWX" for bundles). So the deferral is justified only as
a scope choice, not by implementation difficulty. Council 3
explicitly chose record-over-fix, and the record is accurate
and complete, so this is not an unblock. Recommended as a
follow-up, not a ship condition.

### R5-7 minor, doc: the synthetic-& reasoning is imprecise

The log says the direct form `codex --help & echo
marionette` "cannot occur in /proc (the shell splits & before
exec, so a codex process never has & in its argv)". My L4
proves otherwise with a real binary: direct exec of
`/tmp/y14b-rt-bindir/codex --help & echo marionette` puts a
literal "&" token in /proc (verified by reading
/proc/<pid>/cmdline), and a quoted "&" does the same. What
cannot occur is an UNQUOTED shell & surviving into a
process's argv. Consequence nil: the direct form returns True
(fail-closed), verified live and at unit level. Correct the
log sentence to say that (see U5).

## What verified clean

- The R2 A1-A9 cases, dash, flock, and all wrapper forms in
  the fix5 probe (16 cases), plus my A5-A12 boundary
  controls. Wrapper chains before the shell (nohup, time,
  env -u, sudo -u) are harmless; my first draft wrongly
  expected two of them to fail, and the code proved me
  wrong, which pins the _owning_command boundary exactly.
- The R3/R4 glued forms, the F2 case, and the R3/R4
  later-command controls (B9-B12).
- The C2-2 bare-& fix, including URL safety (D1/D2).
- The C2-1 trailing-glue fix (spaced forms).
- All doc fixes listed in the disposition above, including
  the C1-2 refutation and the fix4 probe breakdown recount.
- The differential over my 19 attacked cases shows no
  verdict change other than the 12 regressions (R5-1, R5-2)
  and the 7 pre-existing same-wrong cases (R5-3, R5-4, R5-5);
  the full regression suites are green on top of that.

## Unblock conditions

- U1 REQUIRED (R5-1): bound the import-guard scan and the
  _same_command_tokens -c scan by quote state, so a
  standalone separator inside a -c value does not truncate
  them. B1-B8 must return True again; the R3/R4 controls
  (B11, B12) must still return False; the fix4 probe must
  still be 64/64 and the fix5 probe 38/38.
- U2 REQUIRED (R5-2): skip separate values of known
  value-taking shell flags in _owning_command. A1-A4 must
  return True; the fix4 probe must still be 64/64.
- U3 FIX OR RECORD (R5-3): mid-token glue on the runner
  token (C1-C5). Fix by checking the head before the first
  separator, or record the exact no-space forms as a known
  residual in the docstring.
- U4 FIX OR RECORD (R5-4): stop the _in_shell_c_string
  nearest--c search at a shell separator (E1), or record the
  exact form.
- U5 PAPERWORK (R5-7): correct the synthetic-& sentence in
  the log to say an unquoted shell & never survives into
  argv, while a literal & arg can occur via direct exec or
  quoting, where True is fail-closed.
- U6 PAPERWORK: none. Hashes verify exactly, docs verify,
  hygiene is clean.

## Hygiene

- 0 em dash and 0 en dash in the fix diff (counted with
  Python on the diff text) and 0 in this paper (checked the
  same way before commit).
- "ydotool" in the fix diff appears only inside "no ydotool"
  prose lines (no use). No ydotool in this review.
- No personal info in the fix diff (no real names, emails,
  addresses, or phone numbers in the diff content).
- No live Zen driving by the fix author (code-only pass; the
  log records no driving) and none by me. No browser work.
- `import re` OK; /usr/lib/python3.12/re/__init__.py exists,
  16,315 B.
- Stub processes: every process I spawned was killed by
  explicit PID, and the final check shows none of mine
  survive. Two foreign leftovers were observed during my runs
  (a `sleep 60`, pid 212305, from another worker; a
  `/bin/sh .../codex -c x=1; marionette`, pid 215193) and
  left alone; both were gone by the final sweep. Process
  notes: (a) my first live L5 run returned a transient True
  that a standalone re-run with an aliveness guard corrected
  to False (shared-VM interference, the same class as
  Council 2 INFO-4); (b) one `pkill -f` matched my own exec
  shell's cmdline and killed it (SIGTERM); the target binary
  was also killed and verified gone. Never pkill -f with a
  pattern that appears in my own cmdline; kill by explicit
  PID (my live probe does).

## Probes used

- /tmp/y14b-fix5-rt-probe.py: 45 unit checks. 19 FAIL, all
  findings in this paper (A1-A4, B1-B8, B13, C1-C5, E1); 26
  PASS, including the boundary controls.
- /tmp/y14b-fix5-rt-diff.py: fix4 blob vs fix5 blob over the
  same 19 cases. 12 REGRESSION (fix4 True to fix5 False),
  7 SAME-WRONG pre-existing, 0 other changes.
- /tmp/y14b-fix5-rt-live.py: 16 live checks. 5 FAIL, all
  findings reproduced live (L1 wrapper, L2 wrapper, L3
  wrapper, L5, L6 wrapper); 11 PASS, including every leaf /
  child still-caught check and the L4 direct-& proof;
  survivors none.
- /tmp/y14b-fix5-rt-c32.py: C3-2 prototype, 14/14 PASS.
- /tmp/y14b-rb3-fix4.py: the fix4 blob (md5 2920f169,
  verified on extraction).
- /tmp/y14b-rt-bindir/codex: real compiled binary, argv[0]
  basename "codex", sleeps 60, ignores args. (A script stub
  always runs under /bin/sh, so its argv[0] is "sh", not
  "codex"; the binary was needed for meaningful direct-form
  live checks.)
- /tmp/y14b-rt-dummies/run_foo.py: shebang stub, sleeps 60.
  (The shared /tmp/y14b-dummies/run_foo.py has no shebang,
  so direct exec of it fails instantly; my L2 needed a
  shebang stub as the first word of the -c string.)

## Timed work log (Asia/Ho_Chi_Minh, 21/11)

- 23:04 +07: task received. Hashes verified (commit 46e0909,
  blob ff4a5358, md5 9e99d9aa; parent bf3c939, blob 585fb801,
  md5 2920f169). Working tree matches the commit.
- 23:05 +07: read the fix5 diff and the four prior papers
  (redteam eae5a99, Council 1 26366a9, Council 2 505f3e5,
  Council 3 3c6b6c2) and the fix5 adjudication and
  verification sections of the log.
- 23:07 +07: re-ran the author's probes. Fix5 38/38, fix4
  64/64, fix3 70/70, fix2 31/31, H2 45/45, transcription 82,
  gate dry 4/4, M1 3/3, M1 all-12 4/4, Council 2 extra 36/46
  with the same 10 named failures.
- 23:10 +07: verified the 10 Council 2 failures case by case;
  all flips in the intended direction. Double-nested live
  flip explained: the outer bash exec-replaces itself, so the
  live cmdline is single-level and caught via C2-1.
- 23:11 +07: wrote my own unit probe (45 checks). First run:
  19 FAIL, all findings. Corrected two of my own wrong
  expectations on the spot (nohup/time wrappers pass).
- 23:12 +07: differential fix4 vs fix5: 12 regressions, 7
  pre-existing same-wrong, 0 other changes. Verified live
  semantics: `bash -o pipefail -c` executes, spaced-;
  python -c import executes.
- 23:13 +07: live probe v1: 8 FAIL, including 3 probe bugs of
  mine (stale /bin/sh stub identity, a wrong L2 form, a
  spaced-needle match bug). Fixed the probe, not the
  expectations: real codex binary, shebang stub, NUL
  normalization in the child search.
- 23:15 +07: one `pkill -f` killed my own exec shell (see
  Hygiene). Target binary verified gone; switched to
  explicit-PID kills only.
- 23:16 +07: live probe v2 stable: 5 FAIL (the findings,
  live), 11 PASS, survivors none. Standalone re-run of L5
  with an aliveness guard corrected the transient True to
  False.
- 23:18 +07: C3-2 prototype 14/14 PASS. Doc fixes all
  verified (plan F3/F5/H4, log F3/F5/72/U-label/env, fix4
  probe breakdown recount 39+21+4=64, C1-2 refutation by
  direct grep).
- 23:19 +07: paper written. Dash check, commit, and push to
  follow; hashes to be filled below on landing.
