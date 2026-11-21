# Council 1 paper: fix pass 6 over fix-pass-5 reviews (GO)

Scope: ONLY the fix-pass-6 diff, commit
d552f4d (parent 0b88ed3, branch todolist-push). The diff touches
3 files: tests/realistic/run_batch3.py (blob ff4a5358 to
261f09ae), improvements/worker-y14-batch3-live-plan.md (F7
sentence + md5 pin), improvements/worker-y14b-restage-log.md
(fix-pass-6 adjudication + verification + C1-2/A1-A14
corrections). Method: my own differential probe
(/tmp/y14b-fix6-c1-probe.py, 97 unit checks + 21 helper
checks, old blob ff4a5358 vs new blob 261f09ae loaded side by
side, plus 6 live cases against /proc); every claimed fix
re-derived from the fix-pass-5 papers (redteam 92fbefd +
addendum, Council 1 239b380, Council 2 505f3e5), not from the
author's probe; the C1-2 correction re-verified by reading the
bf3c939 blobs myself; every doc claim re-checked by grep
against the tree at d552f4d. No Zen driving, no ydotool, no
live browser work, no code edits.

## Verdict: GO

Fix pass 6 closes every fix-pass-5 item it claims to close,
with zero unintended flips across my 97-case differential
probe and 6 live cases, and every doc/record correction
verifies against the tree. The two recorded residuals (R5-8
bare-word FP, the C5-2 known-command flag value) are exactly
as adjudicated: fail-closed, narrow, and stated in the
docstrings with the probe cases pinning them. There is no
finding below that must change before ship. Two INFO notes
follow (a vacuous limitation sentence and a one-line style
nit); neither blocks ship. One review limitation is recorded
honestly: the author's probe files are absent from /tmp in
this session, so the claimed 71/71 and the regression counts
could not be re-run from the author's files; I substituted an
independent 97-case differential probe plus live checks, which
covers every named case and regression family. See "Review
limitation" below.

## Hash record (verified by me)

- Commit d552f4d (parent 0b88ed3).
- run_batch3.py at d552f4d: git blob
  261f09aed1b52c7b80b0b2fc260f13f70fafd142, md5
  fac96935988b9c327dcbe9b3cfa1342e. Parent 0b88ed3: blob
  ff4a5358ac7f621a1fd649c36cec94da2031399d, md5
  9e99d9aa1bcdbb525407adfb31e0692b. Both re-derived by me from
  `git show <commit>:tests/realistic/run_batch3.py | md5sum`
  and `git hash-object --stdin` (see appendix). Working tree
  code is identical to the d552f4d blob
  (`git diff d552f4d -- tests/realistic/run_batch3.py` empty).
  The /tmp copies /tmp/y14b-fix6-run_batch3.py and
  /tmp/y14b-fix5-run_batch3.py (left by a sibling worker) hash
  to the same md5s, fac96935 and 9e99d9aa.
- Hash-record follow-up 6235dab exists and names commit
  d552f4d, blob 261f09ae, md5 fac96935.

## Verification runs (PASS lines counted only)

- My differential probe /tmp/y14b-fix6-c1-probe.py: 97/97
  unit PASS, 21/21 helper PASS, exit 0, 0 OLD-DIFF lines.
  Every case lists old and new results; all 12 fix4-to-fix5
  regressions flip back to the fix4 value, all controls hold.
- My live probe: 6/6 PASS (L1 direct spaced import leaf,
  L2 pipefail wrapper, L3 glue wrapper, L4 echo FP, L4b ssh
  FP, L5 E1 wrapper), all by exact-PID spawn and /proc
  cmdline read; _scan_other_runners hits the three real
  runners and not the E1 wrapper. Zero survivors (see
  appendix for the two orphan notes).
- py_compile OK on the new blob; working-tree import OK.
- Live semantics spot-checked by execution:
  `python3 -c 'import os ; import run_batch3'` prints
  import-ok (from tests/realistic), `bash -o pipefail -c
  'echo hi'` exits 0, so the R5-1/R5-2 forms are real.

## Findings: every claimed fix verified

Line numbers below are in the new blob 261f09ae.

### F1 (R5-1/C5-1/C2-3, REQUIRED): quote-state-aware separator bound, VERIFIED

New helpers `_quote_states` (line 2431) and the rewritten
`_top_level_sep_index(tok, in_single, in_double)` (line
2458), applied in `_same_command_tokens` (line 2927) and in
the restructured import branch (lines 2731-2790, direct vs
nested). All 8 R5-1 cases flip False to True (B1, B2, B8
direct single-element python -c; B3-B7 codex prompt spaced
&&, ;, |, &, ||), B9 (F2 glued) and B10 (glued python -c)
stay True, B11 (R3 later command) and B12 (R4) stay False.
C5-1 B5/B6/B7 (opening-quote glue) flip False to True; d4
(wrapper `'a=1;`) flips False to True while the direct leaf
d5 stays True; B13 (`'a';'b;marionette'`) flips True to
False, which is the fix the redteam expected (the marker
after the first top-level separator in the same token is
correctly missed). C2-3 c7/c7b/c7c/d1 (nested codex spaced
and glued separators) flip False to True; d3 stays False, d2
(F2) stays True, direct c6 stays True. Helper level:
`_top_level_sep_index("'x=1;")` is -1 (was 4 in fix5),
`"'hello';"` is 7, `"os';"` is 3 with quote-entry state and
-1 without (the entry state is what the callers pass from
`_quote_states`; the bare-helper value without state is not
the call-site value), `"time;"` is 4 outside quotes and -1
inside, standalone `";"` is 0 outside and -1 inside,
`"'a';'b;c'"` is 3 (the first top-level separator). Token
lists match the log exactly: direct B12 tokens are
`['python3', '-c', 'import', "os';", 'echo', 'import',
'run_batch3']` and E1 tokens are `['bash', '-c', 'python3',
'-c', "'x';", 'codex', 'exec', 'foo;', 'echo', 'marionette']`
(verified by direct `_argv_tokens` print).

### F2 (C5-2/R5-2, REQUIRED): flag-value skip, VERIFIED

`_owning_command` (line 2370) skips a bare word after a flag
unless its basename is a known command, placed before the
path-argument skip, exactly per Council 1's sketch. A1-A4
flip False to True (`bash -o pipefail -c`, `sh -o pipefail
-c`, `bash -O nullglob -c`, `bash -o pipefail -c codex
exec`); controls A5-A12 all stay True (`env -i bash -c`
proves the known-command guard, `env -u`, `sudo -u`,
`timeout -s`, `nice -n`, `bash --rcfile`, `flock -w`, and
`python3 -X dev -c` stays False). Helper level:
`_owning_command(["bash", "-o", "pipefail", "-c"], 3)` is
`bash`, `["env", "-i", "bash", "-c"]` is `bash`. The recorded
residual (a flag value whose basename is exactly a known
command) is in the docstring and is contrived as stated.

### F3 (C2-4/R5-3, U3 FIX): basename truncate, VERIFIED

New helper `_runner_basename_head` (line 2506) truncates at
the first of `;`, `&`, `|`, `(`, `)` and replaces the
`rstrip` in the basename block. C1-C5 plus the two bare
forms (`run_foo.py;echo`, `run_foo.py&&echo`,
`python3 run_foo.py&echo`) flip False to True; spaced
controls stay True and over-strip controls stay False
(`md5sum run_foo.py;echo`, `echo run_foo.py&&x`, `vim
run_foo.py|cat`, `md5sum run_foo.py;`). Helper level: head
of `run_foo.py&&echo`, `run_foo.py;echo`, `run_foo.py|cat`
is `run_foo.py` in each case.

### F4 (B12, found during verification): direct -c argv boundary, VERIFIED

New helper `_c_arg_flat_end` (line 2289) re-simulates
`_argv_tokens` (line 2319) exactly: same parts expansion,
same per-`-c` argument consumption, so the flat index
aligns by construction. Direct B12 (`python3 -c "import
os';" echo import run_batch3`) stays False, and the import
inside the argument stays True. Helper level:
`_c_arg_flat_end` is 4 for the B12 cmdline (import token at
flat 6, past the end) and 7 for single-element B1 (import
token at flat 6, inside). The nested B12 form (`bash -c
"python3 -c 'import os'; echo import run_batch3"`) stays
False via the separator stop. The fix5 probe's 2 unquoted
artifact cases are correctly False in fix6: with the exact
fix5-probe constructions (`python3 -c import run_batch3`
and `python3 -c x=1; import run_batch3`, code as separate
NUL elements) my probe shows fix5 True to fix6 False, and
False is correct because the -c code is just `import` /
`x=1;` and `run_batch3` is a separate argv element, never
imported. The R4-2 tokenization case (`bash -c python3 -c
import x; echo import run_batch3`, missing leading quote)
is fix5 True to fix6 False, and False is correct: the
constructed argv makes `python3` bash's -c argument and
`import run_batch3` a positional parameter, so nothing
imports the runner. The redteam's correct R4 tokenization
passes False in my probe.

### F5 (R5-4, was "fix or record", now FIXED): non-shell -c skip, VERIFIED

`_in_shell_c_string` (line 2887) now skips a non-shell -c
across a top-level separator and continues backward to the
shell -c. E1 (`bash -c "python3 -c 'x'; codex exec foo;
echo marionette"`) flips True to False, live (L5 wrapper
pid, /proc cmdline read, new False old True) and unit.
`_in_shell_c_string` on the E1 tokens returns True (the
bash -c contains the codex), so `_same_command_tokens`
bounds the scope to `exec foo` and the echo marker does not
count. Controls hold: codex-first and plain-codex forms
stay True; my extra check X1 (codex in a later command
with the marker as its own argument) stays True, so the
skip does not over-narrow. X4 (codex -c, then python -c
with the marker inside the python -c) stays False in both
blobs.

### F6 (R5-8/C2-5): RECORDED only, record VERIFIED accurate

The bare-word FP is recorded in the `_owning_command`
docstring and in the `_is_runner_cmdline` known
limitations, with the exact forms named (`echo bash -c
run_batch3.py`, `ssh host bash -c run_batch3.py`, `cat bash
-c run_batch3.py`, `grep -r bash -c run_batch3.py`). All
five return True in both blobs (fix4 False to fix5 True,
unchanged by fix6), which is the documented fail-closed
behaviour. Live: echo and ssh forms confirmed True against
real /proc cmdlines via a compiled sleeper binary (argv[0]
`echo` / `ssh`, pid-read, both blobs True, both hit by
`_scan_other_runners`). The `python3 script.py bash -c`
mitigation still holds False. Recording was the adjudicated
option (U7 "fix or record"); the record is complete and
the behaviour is unchanged, so this is closed as recorded.

### F7 (C1-2 correction): VERIFIED independently, not on trust

I read the bf3c939 blobs myself:
- Plan at bf3c939, lines 614-615: pins the fix-pass-3
  values (md5 e9e3519a, blob 3a9b7b17, commit 3875215), NOT
  the fix-pass-4 values. Grep for 2920f169/585fb801 in the
  bf3c939 plan returns 0 matches; grep for e9e3519a/3a9b7b17
  returns 2.
- Log at bf3c939: grep for 2920f169/585fb801 returns 0
  matches. The fix-pass-4 entry (line 675) reads "- Fix
  commit: (hash filled below after commit)." (unfilled).
- 40c4e48 ("Y14b: record fix-pass-4 commit bf3c939 hashes")
  pins the fix-pass-4 values in the plan (md5 2920f169,
  blob 585fb801, commit bf3c939).
So Council 1's C1-2 was VALID at the time and was fixed by
40c4e48, not refuted. The log's two CORRECTION notes (lines
954 and 1087 at d552f4d) state exactly this, with the
bf3c939 evidence cited. The correction is accurate.

### F8 (plan md5 pin IN this commit, C5-4): VERIFIED

Plan at d552f4d, lines 614-617: pins the fix-pass-6 values
(md5 fac96935988b9c327dcbe9b3cfa1342e, blob
261f09aed1b52c7b80b0b2fc260f13f70fafd142), with the
fix-pass-5 values (md5 9e99d9aa, blob ff4a5358, commit
46e0909) and fix-pass-4 values labeled superseded, and the
note that the fix-pass-6 commit hash is in the log's
fix-pass-6 entry. The log at d552f4d has the fix-pass-6
entry with the matching hashes (blob 261f09ae, md5
fac96935, parent ff4a5358 / 9e99d9aa / 46e0909). The pin
arrived in the fix commit itself, per C5-4.

### F9 (plan F7 sentence, C2-7/R5-9): VERIFIED

Plan lines 748-755 at d552f4d now read "a codex -c flag now
includes everything after it UP TO a top-level separator,
the bound being quote-state aware (fix pass 6, redteam R5-1
/ Council 1 C5-1 / Council 2 C2-3), so `bash -c \"codex -c
'import time; x # marionette'\"` is caught while `bash -c
\"codex -c 'hello'; echo marionette\"` is not". Both example
claims check out against my probe (F2 True, B11 False).

### F10 ("A1-A14" to "A1-A9 plus 7 further wrapper cases", C5-5): VERIFIED

All 3 live uses corrected (log lines 993-994, 1103, 1107 at
d552f4d read "A1-A9 plus 7 further wrapper cases").
"A1-A14" remains only where the adjudication says it stays:
the C5-5 finding text itself (line 1382) and the fix-pass-6
scope items quoting the label (lines 1425, 1612, 1733,
1943). No live use still carries the phantom label.

### F11 (R5-7/C2-9/C2-10 "cannot occur in /proc", C5-7): VERIFIED

The `_same_command_tokens` docstring now says a bare "&"
CAN occur in /proc via direct exec (redteam L4), the
behaviour is fail-closed, and the direct-form codex "&"
case is recorded there (C5-7 one line). My probe confirms
the behaviour: direct `codex --help & echo marionette`
returns True in both blobs (fail-closed as recorded), bash
-c form returns False in both.

### F12 (t10 untouched): VERIFIED

The code diff has 11 hunks, all in lines 2286-3032 (the
scanner helpers, the `_is_runner_cmdline` docstring and
import branch, `_in_shell_c_string`,
`_same_command_tokens`). Zero t10 / run_b3_t10 / threshold
mentions in the code diff; the only new function
definitions are `_c_arg_flat_end`, `_quote_states`,
`_runner_basename_head` and the `_top_level_sep_index`
rewrite. The t10 checker, preflight, H2 helpers and
launch_gate are untouched by construction, and the
working-tree import succeeds.

### F13 (hygiene): VERIFIED

0 em dash (U+2014) and 0 en dash (U+2013) in the full fix
diff (counted in Python, not grep). "ydotool" appears only
inside "no ydotool" prose lines, no use. No personal info
in the diff (grep for gmail/outlook/phone/+84/real name
returns nothing; the only email anywhere is the noreply
GitHub author address in commit metadata, not diff
content). No live Zen driving, no browser work.

## INFO findings (no action required for ship)

### INFO-1 (doc, minor): the import-branch "later top-level command" limitation is vacuous

The `_is_runner_cmdline` docstring records as a limitation
that "a python -c in a later top-level command after a
shell -c (e.g. `bash -c \"echo hi\"; python3 -c 'import os;
import run_batch3'`) is wrongly treated as nested
(fail-closed)". The example cannot occur as a single /proc
cmdline: the `;` sits outside the bash -c string, so the
shell runs two separate processes and no one process has
both halves in its argv. The genuinely reachable form (the
`;` inside one bash -c string, `bash -c "echo hi; python3
-c 'import os; import run_batch3'"`) returns True in both
blobs (my probe case X2), and True is CORRECT there because
the inner python really imports the runner. So the recorded
limitation never fires on a real cmdline; it is an
over-disclosure, not a bug. A future pass may reword it to
say the form cannot occur in /proc, or drop it. Not a ship
condition.

### INFO-2 (style, trivial): `_quote_states` is computed inside the -c branch

In `_same_command_tokens` the `states = _quote_states(tokens)`
line sits inside the codex -c branch, after `j += 1`. It
runs at most once per call (the `break` after the inner
while exits the outer loop), so this is a single O(n) scan,
not a performance issue. Hoisting it to the top of the
function would read cleaner. No action.

## Review limitation (recorded honestly)

The author's probe files (/tmp/y14b-fix6-probe.py,
/tmp/y14b-h2-probe.py, /tmp/y14b-fix2-probe.py,
/tmp/y14b-fix3-probe.py, /tmp/y14b-fix4-probe.py,
/tmp/y14b-transcribe.py, /tmp/y14b-gate-dry.py,
/tmp/y14b-m1-probe.py, /tmp/y14b-fix2-m1-probe.py) are
absent from /tmp in this session, so the claimed 71/71 and
the regression counts (H2 45/45, fix2 31/31, fix3 70/70,
fix4 64/64, transcription 82, gate dry 4/4, M1 3/3, M1
all-12 4/4, fix5 35/38) could NOT be re-run from the
author's files. I substituted an independent differential
probe (97 unit + 21 helper, all named cases and all named
regression families from the fix-pass-5 papers, including
the fix5 probe's 3 artifact constructions with their exact
shapes) plus 6 live cases, which is stronger evidence about
the code than re-running the author's files would be, but
it is not a line-for-line re-run of their suites. Two
probe-file-only claims are therefore verified by behaviour
rather than from the file: the fix6 probe's real-URL case
(the behaviour, B15 `python3 run_batch3.py
http://x/?a=1&b=2`, returns True in both blobs) and the
fix5-probe docstring note in the fix6 probe header (the
file is absent; the underlying fact, that the fix5 probe
has no live cases, is confirmed by Council 2 C2-10). If
the parent wants the author's exact counts re-run, the
probe files need to be recovered from the author's session
first; nothing in this diff depends on that.

## What verified clean (with my own probe counts)

- R2/A1-A9 wrapper forms all True in the new blob, plus
  env/sudo/timeout/nice/env -i//usr/bin/env/dash/flock
  forms; `python3 -c` still False.
- R4/C3-3/C1-R1 import guard: direct and nested later-
  command forms False, real imports True.
- C2-1 glued separators: spaced and no-space forms True,
  over-strip controls False.
- C2-2 bare "&": shell forms False, real URL True.
- R3/C1-R4: later-command markers False, F2 True, direct
  codex True.
- C3-2/C1-R2 residual still recorded and true (`python3
  other -W ignore run_batch3.py` True in both blobs).
- C1-R3 recorded and true (glued `;codex` still False).
- F1: `python3 -crun_batch3.py` False in both blobs
  (NameError, never runs); `python3 -c run_batch3.py`
  False in both blobs (the -c code is the name, not an
  import; my first probe draft wrongly expected True and
  the code proved me wrong).
- Known miss I3 (`bash -c "python3 -c 'import
  run_batch3'"`) still False in both blobs, unchanged.
- Council 2 extra probe and Council 1 diff probe
  expectations from fix5 are superseded by the fix6
  behaviour verified here (the fix5 regressions they pin
  are the ones fix6 fixes).

## Unblock conditions

None. GO as written; INFO-1 and INFO-2 are optional
follow-ups, not ship conditions.

## Appendix: timed work log (Asia/Ho_Chi_Minh, 21/11)

- 23:49 +07: task received. Hashes verified (commit d552f4d,
  blob 261f09ae, md5 fac96935; parent 0b88ed3, blob ff4a5358,
  md5 9e99d9aa). Old and new blobs extracted to
  /tmp/y14b-c1/old.py and /tmp/y14b-c1/new.py; py_compile OK
  on the new blob.
- 23:52 +07: diff read (11 code hunks, lines 2286-3032);
  plan and log diffs read; /tmp probe files found absent
  (only /tmp/y14b-fix6-run_batch3.py, /tmp/y14b-fix5-
  run_batch3.py and /tmp/y14b-fix6-diff.txt present, all
  hash-matching); fix-pass-5 papers read for case
  definitions (redteam 92fbefd + addendum, Council 1
  239b380, Council 2 505f3e5).
- 23:55 +07: wrote my differential probe
  /tmp/y14b-fix6-c1-probe.py (91 unit + 20 helper). First
  run 90/91 unit, 17/20 helper: all 4 failures were my own
  probe/expectation errors (F1 `python3 -c run_batch3.py`
  is False in both blobs; R5-8 want_old must be True for
  the fix5 blob; `tls "os';"` needs the quote-entry state
  to return 3; `tls "time;"` outside quotes returns 4, the
  separator index, not 0; `"'a';'b;c'"` returns 3, my
  hand count of 2 was wrong). Corrected the probe, not the
  code; also corrected the artifact constructions to the
  exact fix5-probe shapes (a1/a2) and verified the
  author's artifact claim by the argv semantics.
- 23:57 +07: probe run 3: 93/93 unit, 21/21 helper, exit 0,
  0 OLD-DIFF. Live probe 4/5 at first (L4 failed only
  because /usr/bin/echo exits instantly and its /proc
  cmdline was empty by read time; the unit R5-8 cases
  already passed). Killed two orphan leaf processes of
  mine by exact PID (3511, 3513, children of the L2/L3
  wrappers); foreign orphans (3704, 3705, from
  /tmp/y14b-dummies, another worker) left alone.
- 23:58 +07: L4 redone with a compiled sleeper binary
  (argv[0] echo/ssh, /tmp/y14b-c1-sleeper, gcc): echo and
  ssh forms True in both blobs, hit by
  _scan_other_runners. Live 6/6. (An intermediate
  /bin/sleep attempt failed the same instant-exit way:
  sleep parses argv[1] as a duration, so it cannot carry
  a fake argv[0]; the compiled sleeper was the fix.)
- 00:00 +07: C1-2 re-verified against the bf3c939 blobs
  (plan pins fix3 values, log has 0 fix4 mentions, fix4
  entry unfilled at line 675, 40c4e48 pins fix4 values).
  Plan md5 at d552f4d pins fix6 values in-commit; F7
  sentence, A1-A14 corrections, CORRECTION notes, hashes
  entry all verified by grep. t10/hygiene checks done
  (0 em/en dash in the diff by Python count).
- 00:02 +07: added 4 extra council cases (X1-X4) to the
  probe; final run 97/97 unit, 21/21 helper, exit 0.
  Paper written, dash-checked, committed, pushed.
- Process notes: every stub I spawned was killed by exact
  PID and verified gone by ps; no pkill -f used at any
  point. One foreign live probe ran concurrently during
  part of my runs (orphan run_foo.py pids from
  /tmp/y14b-dummies); I killed none of its processes, and
  my live checks read /proc cmdlines by exact PID, so they
  are pollution-proof.
