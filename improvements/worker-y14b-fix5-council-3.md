# Y14b fix-pass-5 Council 3 review (plan and documentation)

## Verdict: AMEND

Eight of my nine fix-pass-4 findings are closed with independent
reproduction. The code fixes (R2, R3, R4, C2-1, C2-2) all verify
against my own probe cases, the fix5 probe re-runs 38/38, and the
full regression set re-runs green. The one open item is C3-5, and
only half of it: the true fix4 probe breakdown is now recorded in
the fix-pass-5 adjudication, but the original wrong line is still
in place in the fix-pass-4 verification section (log line 667
still reads F3 x8, regressions x17, summing to 66 for a 64-case
probe). That is the same class of ship-document error as C3-1 and
C3-6, which were required fixes in fix pass 4. One line edit
closes it. No code change is required for ship.

## Scope

Fix-pass-5 diff ONLY: commit 46e0909
(46e0909058af1419c0ef6534394a68019ec8ebd8) against its parent
fix-pass-4 state bf3c939
(bf3c939741f86c6c639c730882f8a4f721265a74), scoped to
tests/realistic/run_batch3.py,
improvements/worker-y14-batch3-live-plan.md, and
improvements/worker-y14b-restage-log.md. The unscoped
bf3c939..46e0909 diff touches 75 files (other workers' work on
the shared branch); I did not review those. I did not re-review
the whole runner. The four prior papers under review are my
fix-pass-4 paper 3c6b6c2
(improvements/worker-y14b-fix4-council-3.md), the fix-pass-4
redteam paper eae5a99
(improvements/worker-y14b-fix4-redteam.md), Council 1 in commit
26366a9 (improvements/worker-y14b-fix4-council-1.md), and
Council 2 paper 505f3e5
(improvements/worker-y14b-fix4-council-2.md). Branch
todolist-push.

## Method and evidence contract

Independent review, no subagents, no live Zen driving, no
ydotool. Every claim below was reproduced by me: I re-ran the
fix5 probe and the full regression set myself, ran 26 of my own
unit cases against `_is_runner_cmdline` and `_is_codex_executor`
loaded from the working-tree file (byte-identical to the fix5
blob, md5 9e99d9aa1bcdbb525407adfb31e0692b, confirmed before
testing), recomputed the md5 and git blob of run_batch3.py at
46e0909, recomputed the H4 numbers with Decimal, counted the
fix4 probe breakdown from its source with AST, and checked the
environment state directly. Counts below are PASS lines only,
never the "FAILURES:" summary line. All stub processes from the
probes were verified gone (ps shows no run_foo, run_selfscan,
selfscan, or sleep stubs).

## (1) Hash records: VERIFIED EXACT

Commands and outputs:

```
$ git rev-parse 46e0909
46e0909058af1419c0ef6534394a68019ec8ebd8
$ git hash-object tests/realistic/run_batch3.py
ff4a5358ac7f621a1fd649c36cec94da2031399d
$ md5sum tests/realistic/run_batch3.py
9e99d9aa1bcdbb525407adfb31e0692b
$ git show 46e0909:tests/realistic/run_batch3.py | git hash-object --stdin
ff4a5358ac7f621a1fd649c36cec94da2031399d
$ git show 46e0909:tests/realistic/run_batch3.py | md5sum
9e99d9aa1bcdbb525407adfb31e0692b
$ git ls-remote origin todolist-push
21520c600a9697a4edb3f5d47698fcfd42ec8a8e  refs/heads/todolist-push
```

Blob ff4a5358, md5 9e99d9aa, commit 46e0909 all match the task
brief and the author's hash-record commit 8ab5dd0. The plan's
md5 procedure now pins the fix-pass-5 values (plan lines
614-616: md5 9e99d9aa, blob ff4a5358, commit 46e0909) and
names the fix-pass-4 values as superseded (md5 2920f169, blob
585fb801, commit bf3c939). The parent blob 585fb801 / md5
2920f169 still verify as the fix-pass-4 state.

## (2) Per-finding verdicts for C3-1 through C3-9

| Finding | Status | Evidence |
|---------|--------|----------|
| C3-1 F5 outcome to False | CLOSED | Plan F5 sentence now False; log line 603 now False; direct test False, and False is correct |
| C3-2 generic extensionless residual | CLOSED | Recorded in `_python_executes` docstring and in the limitations list; `python3 other -W ignore run_batch3.py` still True by direct test; deferral justified, see below |
| C3-3 import guard separator stop | CLOSED | Import after `;` now False in both token forms; legitimate `1;` inside a python -c string still True |
| C3-4 F3 attribution to other.py | CLOSED | Plan and log both say other.py; redteam paper bd3c6c9 F3 section confirms other.py (probes 2c/2d/2e) |
| C3-5 fix4 probe breakdown | PARTIALLY CLOSED | True breakdown (F3 9, regressions 14) is correct by AST count and is recorded in the fix5 adjudication, but log line 667 still has the wrong numbers in place (F3 x8, regressions x17) |
| C3-6 "72" off by one | CLOSED | Log now says plain miscount (70+1=71, not 72); no remaining text says 72 came from the summary line |
| C3-7 U3/U4 label | CLOSED | Log line 527 now reads "U4 left open"; no remaining U3 label on F3's unblock |
| C3-8 env incident note stale | CLOSED | Note updated with solved root cause (shim A6e, VMFIX c16dd4e); re/__init__.py present, 16315 bytes, dpkg -V clean, .pyc gone |
| C3-9 U11 parenthetical | CLOSED | Plan H4 note now carries the leg-precise 3.0 figure with 4 overcounting by 1; arithmetically honest on the N=3.5 model, see below |

### C3-1 (CLOSED)

The plan F5 sentence (now around line 743) reads
"`python3 run_other -W ignore run_batch3.py` is now False, the
extensionless run_* script barrier correctly blocks the -W/-X
two-back rule; the earlier claim that it was True was
backwards, the fix-pass-3 True was the false positive". The log
F5 adjudication (line 603) reads the same way. Direct test by
me against the fix5 code:

```
False  python3 run_other -W ignore run_batch3.py
True   python3 run_other.py -W ignore run_batch3.py
```

False is the correct outcome (run_batch3.py is only an argument
to run_other), and the .py contrast case is still True via
run_other.py itself, so the correction does not overclaim. The
fix4 probe label is also corrected (probe line 83: "python3
run_other -W ignore now False (was True in fix3)").

### C3-2 (CLOSED, deferral justified)

The `_python_executes` docstring now records the residual
verbatim: "a non-run_* extensionless script still
false-positives (`python3 other -W ignore run_batch3.py`
returns True, fix pass 5, Council 3 C3-2 / Council 1 C1-R2)",
with the reason that extending the barrier "would need
flag-value tracking (skip -W/-X/-c/-m values to find the script
position) and is a future improvement". The
`_is_runner_cmdline` limitations list records the same case.
Direct test by me confirms the residual is stated accurately:

```
True  python3 other -W ignore run_batch3.py
```

The deferral is justified, not a dodge. I checked the
difficulty claim myself: a naive extension (treat any
non-flag token as a script barrier) would break the legitimate
two-back rule, because flag values are non-flag tokens. In
`python3 -W ignore run_batch3.py`, the token `ignore` is the
-W value; treating it as a script would return False for a
form the guard must return True for. Telling a script token
apart from a flag value while scanning backwards requires a
forward parse that skips known flag values, which is a real
change with its own probe surface, not a one-line fix. The
residual is a fail-closed false positive in a contrived form
(an extensionless non-run script plus a runner-named argument),
and the fix-pass-3 redteam itself recommended record over fix
for U6. Recording it in two places (docstring plus
limitations list) closes U6 as specified.

### C3-3 (CLOSED)

The import-branch nearest-`-c` scan now breaks at a token
whose `_top_level_sep_index` is >= 0. Direct tests by me
against the fix5 code, all PASS:

```
False  python3 -c 'import os'; echo import run_batch3
False  python3 -c import os ; echo import run_batch3 (bare tokens)
False  bash -c "python3 -c 'import x'; echo import run_batch3"
True   python3 -c "import run_batch3; run_batch3.main()"
True   python3 -c "import run_batch3; x=1; run_batch3.main()"
```

The last two are the quote-aware subtlety: a `;` with no
quotes in its token (the `1;` inside the -c string) is Python
code, not a shell separator, so it does not stop the search and
the legitimate import still returns True. The fix handles both
the quoted form (`'import os';`, where the `;` follows the
closing quote) and the bare-token form (standalone `;`), which
covers the two shapes the finding named. The disclosed
limitation in the `_top_level_sep_index` docstring (a token
with a top-level separator BEFORE its last quote, e.g.
`'a';'b;c'`, is missed) is contrived and not in the fleet's
launchers; disclosing it is the right call.

### C3-4 (CLOSED)

Both the plan F3 bullet and the log F3 adjudication now say
the redteam's -m example was `python3 other.py -m
run_batch3`, NOT run_other.py. I checked the citation myself
against the redteam paper bd3c6c9 (not the fix4 redteam
paper): the F3 section states "`python3 other.py -m
run_batch3` (my probe 2c/2d/2e; the `-m` branch ... has no
`_python_executes` call)". The author's citation "bd3c6c9
lines 222-243" points at that F3 section. The log also
correctly keeps the run_other.py note for the -W case, which
comes from the fix-pass-2 redteam, not the -m case. The
substance was already right; the attribution now is too.

### C3-5 (PARTIALLY CLOSED, the one open item)

My own AST count of /tmp/y14b-fix4-probe.py confirms the true
breakdown:

```
cases per section: R1 6, F1 5, F3 9, F4 3, F5 2, regressions 14 (total 39)
codex_cases: 21, live checks: 4
39 + 21 + 4 = 64
```

The fix-pass-5 adjudication (log lines 1039-1042) states
exactly this: "R1 6, F1 5, F3 9, F4 3, F5 2, regressions 14,
codex 21, live 4 = 64" and "The log said F3 x8 and regressions
x17 (summing to 66); F3 is 9 and regressions is 14." That
part is correct. But the fix-pass-4 verification section
itself was NOT corrected in place. Log lines 666-668 still
read:

```
- Fix4 probe /tmp/y14b-fix4-probe.py: 64/64 PASS, exit 0 (R1
  -m.py x6, F1 x5, F3 x8, F4 x3, F5 x2, regressions x17, codex
  F6/F7/F8 x21, live x4).
```

F3 x8 and regressions x17 still sum to 66 for a 64-case
probe. The author's claim "fix4 probe breakdown corrected"
is therefore half true: the correction exists as adjudication
text, but the wrong numbers remain where a reader of the
verification section will actually read them. This is the
same class of error as C3-1 and C3-6 (a wrong number in the
ship document), and it needs the same treatment: correct
line 667 in place. Required fix U-C3-5b below. No other place
carries the wrong breakdown (grep for "x8"/"x17" in the plan
returns nothing).

### C3-6 (CLOSED)

The log verification section now reads: "The earlier "65"
(fix4) claim counted the summary line (64+1=65); the earlier
"72" (fix3) was a plain miscount (70+1=71, not 72), not from
the summary line; the redteam's 70 for fix3 was right." The
arithmetic is right (70+1=71), and grep finds no remaining
text saying 72 came from counting the summary line. The only
other "72" mentions are the historical quotes of my finding
in the adjudication, which correctly describe the error.

### C3-7 (CLOSED)

The fix-pass-3 verdict section (log line 527) now reads "U4
left open". Grep for "U3 left open" returns nothing. The
remaining "U3" hits in the log are the quoted finding text
in the adjudication (correctly describing the old error) and
the redteam unblock line "U2/U3 FIX OR RECORD" (line 752),
which refers to the fix-pass-4 redteam's U2/U3, a different
numbering, and is correct as written.

### C3-8 (CLOSED)

The env incident note now carries two updates: the 22:41
proper-repair verification and the 22:57 solved root cause.
It states the Y13r2 redteam's shim (A6e) accidentally deleted
the file (globals().update overwrote __file__ before
os.remove), NOT a stray process, and that VMFIX restored it
durably (c16dd4e). I verified the current state myself:

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

The source file is back at 16315 bytes, dpkg -V is clean,
import re resolves to the .py file, and the .pyc stopgap is
gone. I also cross-checked the root-cause claim: MEMORY.md
records the same A6e shim cause and the VMFIX c16dd4e restore,
and commit c16dd4e exists ("VMFIX: VM Python re breakage
verified + durable"). The note no longer reads as an open
"should be repaired properly" flag.

### C3-9 (CLOSED)

The plan H4 note now carries the parenthetical: "(U11,
closed: the literal clause the redteam asked for, leg-precise
3.0 with 4 overcounting by 1, is not stated because on the
N=3.5 model both 3 and 4 are half a round trip off; stating
either as exact would be wrong, so the plan states the
half/half position instead.)" The leg-precise 3.0 figure and
the "4 overcounts by 1" figure are now both in the plan, with
the reason they are not the operative wording. I re-derived
the N=3.5 arithmetic with Decimal to check the honesty of
the half/half claim:

```
N=3.5 @2 ms:  (850 + 3.5*2)/100  = 8.57, ticks (8,9)
N=3.5 @19 ms: (850 + 3.5*19)/100 = 9.165, ticks (9,10)
N=3.5 @50 ms: (850 + 3.5*50)/100 = 10.25, ticks (10,11)
1.835 half-up to 1.84; 1 round trip at 19 ms = 0.19 ticks
first fail N=3.5: (1100-850)/3.5 = 71.4 ms
sure fail N=3.5:  (1200-850)/3.5 = 100.0 ms
```

These match the plan's "reads 8-10", "margin 1-3 discrete,
1.84-2.43 continuous", "first fails roughly 70-85 ms",
"fails surely at ~100-117 ms" (the fail ranges span N=3 to
N=3.5). On the N=3.5 model, 3 undercounts by half a round
trip and 4 overcounts by half, so stating "4 overcounts by 1"
as the operative figure would contradict the plan's own
verified margins, and the parenthetical says so. U11 is
closed. Optional polish only: the parenthetical says the
literal clause "is not stated" while stating its figures
inside the parenthetical itself; a reader could trip on
that. Rewording to "the operative H4 sentence states the
half/half position instead of the literal leg-precise clause"
would remove the wrinkle. Not required for ship.

## (3) Code fixes verified with my own probe cases (26/26 PASS)

Loaded run_batch3.py from the working tree (md5-verified
against the fix5 blob) and ran these directly against
`_is_runner_cmdline` and `_is_codex_executor`:

- R2/U1, wrapper-prefixed shell -c (8 cases, all PASS):
  `env bash -c codex marionette` True, `sudo bash -c` True,
  `dash -c` True, `timeout 10 bash -c` True, `FOO=1 bash -c`
  True, `flock /tmp/lock bash -c` True, `nice bash -c` True,
  and the negative control `env python3 -c codex marionette`
  False. The `_owning_command` walk-back correctly skips
  flags, VAR=value assignments, and path arguments (flock's
  lockfile), and returns the owning command's basename.
- R4/C3-3, import guard boundary: see C3-3 above (5 cases).
- C2-1, glued separator on the runner token (4 cases, all
  PASS): `bash -c "python3 run_foo.py; echo done"` True,
  `run_foo.py&&` True, `run_foo.py||` True, bare
  `run_foo.py; echo done` True. The rstrip set is now
  ";,()&|", which is what the && / || variants need; the
  author's first-run failure on those two variants and the
  fix are consistent with the code as committed.
- C2-2, bare `&` separator (3 cases, all PASS):
  `bash -c "python3 --version & pytest -W ignore
  run_batch3.py"` False, `bash -c "codex --help & echo
  marionette"` False, and the negative control `bash -c
  "codex exec --url http://x/?a=1&b=2 marionette"` True,
  confirming `&` inside a token (a URL) is not split, as the
  fix claims.
- R3, quote-aware codex -c bound (3 cases, all PASS): the F2
  case `bash -c "codex -c 'import time; x # marionette'"`
  still True, `bash -c "codex -c 'hello'; echo marionette"`
  now False, and `codex -c 'import time; sleep 1 #
  marionette'` still True (the `time;` token has no quotes,
  so its `;` is code, not a separator).
- C3-1/C3-2 controls (3 cases): run_other False, run_other.py
  True, other True, see above.

One residual the author records and I confirmed: the direct
form `codex --help & echo marionette` (no bash -c wrapper)
still returns True via `_is_codex_executor`. The author
records it as synthetic-only, and that is correct: a real
shell splits `&` before exec, so a codex process never has
`&` in its argv. I verified the True result directly; it
cannot occur in /proc.

## (4) Regression re-runs by me (PASS lines only)

Working tree run_batch3.py is byte-identical to the fix5 blob
(md5 9e99d9aa1bcdbb525407adfb31e0692b), so re-running the /tmp
probes against the working tree is re-running them against the
fix-pass-5 code. Each probe log has exactly one "^FAIL" line,
the "FAILURES: 0 []" summary line, except the C2 probe (see
(5)).

```
$ python3 /tmp/y14b-fix5-probe.py      exit 0, PASS lines 38, FAIL lines 1 (summary only)
$ python3 /tmp/y14b-fix4-probe.py     exit 0, PASS lines 64, FAIL lines 1 (summary only)
$ python3 /tmp/y14b-h2-probe.py       exit 0, PASS lines 45, FAIL lines 1 (summary only)
$ python3 /tmp/y14b-fix2-probe.py     exit 0, PASS lines 31, FAIL lines 1 (summary only)
$ python3 /tmp/y14b-fix3-probe.py     exit 0, PASS lines 70, FAIL lines 1 (summary only)
$ python3 /tmp/y14b-transcribe.py     exit 0, PASS lines 82, FAIL lines 1 (summary only)
$ python3 /tmp/y14b-gate-dry.py       exit 0, PASS lines 4,  FAIL lines 1 (summary only)
$ python3 /tmp/y14b-m1-probe.py       exit 0, PASS lines 3,  FAIL lines 1 (summary only)
$ python3 /tmp/y14b-fix2-m1-probe.py  exit 0, PASS lines 4,  FAIL lines 1 (summary only)
$ python3 -m py_compile tests/realistic/run_batch3.py  OK
$ python3 -c "import run_batch3" (from tests/realistic)  OK
```

All match the author's claimed numbers (fix5 38/38, fix4
64/64, H2 45/45, fix2 31/31, fix3 70/70, transcription 82,
gate dry 4/4, M1 3/3, M1 all-12 4/4).

## (5) Council 2 extra probe: the 10 "failures" are the fix, not regressions

`/tmp/y14b-fix4-c2-probe.py` re-run by me: 36 PASS, 10 FAIL,
exit 1. I checked each failing case against the fix-pass-5
code; every one encodes fix-pass-4 behavior that fix pass 5
deliberately changes, and the new outcome is the correct one:

1. `sep single & alone` (got True, want False): `&` is now a
   separator (C2-2, Council 2's own fix sketch).
2. `c env bash -c MISS` (got True, want False): wrapper-prefixed
   shell -c now caught (R2).
3. `c nice bash -c MISS` (got True, want False): same, R2.
4. `c sudo bash -c MISS` (got True, want False): same, R2.
5. `glued; python3 run_foo.py; echo MISS` (got True, want
   False): glued separator on the runner token now matches
   (C2-1).
6. `glued; bare run_foo.py; echo MISS` (got True, want False):
   same, C2-1.
7. `codex -c marker in LATER shell cmd` (got False, want True):
   later-command marker now excluded (R3).
8. `codex single & --help & echo FP` (got False, want True):
   `&` now bounds the marker scope (C2-2).
9. `live glued ; wrapper missed` (got True, want False): C2-1
   working live; the leaf is still found and caught.
10. `live double-nested wrapper missed` (got True, want False):
    R2 working live; the leaf is still found and caught.

The case names match the author's list exactly (10/10), and
the fix5 probe covers all 10 with the corrected expectations
(38/38). The author's claim stands. No stub processes
survive from the C2 probe run (ps check clean).

## (6) t10 assert set untouched, no threshold changed

`git diff bf3c939 46e0909 -- tests/realistic/run_batch3.py`
contains zero hits for t10, assert, or expectText, and zero
hits for the threshold figures (850, 1100, 1200). The diff is
confined to the guard helpers (`_is_cmd_separator`,
`_is_var_assignment`, `_KNOWN_COMMANDS`, `_owning_command`,
`_top_level_sep_index`, `_c_is_shell`, `_python_executes`
docstring, `_is_runner_cmdline` docstring and basename
block, import branch, `_in_shell_c_string`,
`_same_command_tokens`) plus the sync-note line. No t10 hunk,
no threshold change.

## (7) Hygiene

- 0 em dash, 0 en dash in the three-file fix-pass-5 diff
  (grep count 0 for both code points).
- ydotool: the only hits in the diff are the log lines "no
  ydotool" and "no ydotool use" (negative mentions), same as
  the prior papers.
- Personal info: no email, name, address, or phone pattern in
  the added lines of the three-file diff (grep for email/name
  patterns returns nothing; the only name in the full diff is
  the git Author header, which is commit metadata).
- No live Zen driving by me or, as far as the diff and log
  show, by the fix author: all live checks are local sleeping
  stubs and /proc scans. My own stub processes were verified
  gone.

## Findings (fix pass 5)

### C3-5b (REQUIRED, log): fix4 probe breakdown still wrong in place

Log lines 666-668 still read "(R1 -m.py x6, F1 x5, F3 x8, F4
x3, F5 x2, regressions x17, codex F6/F7/F8 x21, live x4)",
summing to 66 for a 64-case probe. The true breakdown (R1 6,
F1 5, F3 9, F4 3, F5 2, regressions 14, codex 21, live 4 =
64) is stated in the fix-pass-5 adjudication but not in the
verification section where the wrong numbers live. Fix: edit
log line 667 in place to "R1 -m.py x6, F1 x5, F3 x9, F4 x3,
F5 x2, regressions x14, codex F6/F7/F8 x21, live x4".

### C3-9p (OPTIONAL, plan): U11 parenthetical wording wrinkle

The parenthetical says the literal clause "is not stated"
while stating its figures inside the parenthetical itself.
Rewording to "the operative H4 sentence states the half/half
position instead of the literal leg-precise clause" would
remove the wrinkle. Not required for ship.

## Unblock conditions for ship

- U-C3-5b: correct log line 667 in place (F3 x9,
  regressions x14). One line, no code change, no re-probe
  needed beyond confirming the edited line.
- Optional: apply the C3-9p rewording in the same edit.

## Timed work log (Asia/Ho_Chi_Minh, 21/11)

- 23:05: task received. Fetch origin, confirm 46e0909 and
  bf3c939 on todolist-push, read the scoped code diff and the
  doc diff, read my fix-pass-4 paper 3c6b6c2.
- 23:06: hash recomputation (blob ff4a5358, md5 9e99d9aa,
  commit 46e0909, all match exactly); plan md5 lines checked
  (fix-pass-5 values pinned, fix-pass-4 superseded).
- 23:07-23:09: plan/log grep checks for C3-1, C3-4, C3-5,
  C3-6, C3-7, C3-8, C3-9; found log line 667 still carries
  the wrong breakdown (F3 x8, regressions x17) while the
  fix5 adjudication states the true one.
- 23:10: redteam paper bd3c6c9 F3 section read (other.py,
  probes 2c/2d/2e, lines 222-243) and U11 clause read (lines
  415-425); C3-4 citation and C3-9 figures confirmed.
- 23:11: AST count of the fix4 probe (R1 6, F1 5, F3 9, F4 3,
  F5 2, regressions 14, codex 21, live 4 = 64).
- 23:13: my own 26-case unit probe against the fix5 code,
  all PASS (R2 8, C3-3 5, C2-1 4, C2-2 3, R3 3, C3-1/C3-2
  controls 3).
- 23:14-23:15: full regression re-run (fix5 38/38, fix4
  64/64, H2 45/45, fix2 31/31, fix3 70/70, transcription 82,
  gate dry 4/4, M1 3/3, M1 all-12 4/4); C2 probe 36/46 with
  the 10 failures checked case by case; py_compile and
  import OK; stub ps check clean.
- 23:15-23:16: t10/threshold diff check (0 hits), hygiene
  checks (0 em/en dash, ydotool only negative, no PII),
  env check (re/__init__.py 16315 bytes, dpkg -V clean,
  .pyc gone, import re OK), VMFIX c16dd4e cross-check,
  Decimal H4 re-derivation, synthetic-only direct `&` form
  verified True.
- 23:17: paper written, committed, pushed, verified.
