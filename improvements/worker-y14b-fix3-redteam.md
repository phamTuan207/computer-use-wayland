# Y14b fix-pass-3 redteam review

## Verdict: AMEND

One MEDIUM regression and seven LOWs. Fix pass 3 closes the headline
items it was given (bundled `-m`/`-c`, the long option, the `-W`/`-X`
false positives, the env codex chain, the semicolon false positive,
the H4 restatement), and every prior probe re-runs clean. But the new
`_python_executes` guard regresses a form fix pass 2 caught:
`python3 -m run_batch3.py` (and its bundled/spaced variants) executes
a runner live and is now missed (R1). Everything else below is a
false positive, a wrapper-level miss with a live leaf backstop, or a
doc/probe-accuracy gap. No BLOCK-grade accidental form: no fleet
launcher uses `-m <runner>.py`, and the bare `-m` and script-path
forms still catch. Ship waits for the U-items below; U1 is the only
one I recommend as a code fix before ship, the rest are small code or
record fixes.

## Scope

Fix-pass-3 diff ONLY: commit `3875215` vs its parent `4b589c7`, plus
`5792a82` (hash record only). I did not re-review the original
re-stage (`f732d6a`), fix pass 1 (`8bee524`) or fix pass 2
(`ad085d9`); those verdicts stand (fix re-review: C1 GO, C2 AMEND,
C3 AMEND, redteam AMEND `04ce6b1`; fix-pass-2 redteam AMEND
`4b589c7`). Branch note: `todolist-push` HEAD is `5792a82`;
`tests/realistic/run_batch3.py` is byte-identical between `3875215`
and HEAD (0-line diff), so all line numbers below are valid at both
commits. The `5792a82` record verifies exactly: `git show
3875215:tests/realistic/run_batch3.py` gives blob
`3a9b7b173c2d2d8e7ca1cc717e22d613bf376727` and md5
`e9e3519af09fb5e1066a2a516dddda05`, matching the log entry, and the
plan's ship-time md5 procedure now quotes those values.

## Method and evidence contract

Independent review, no subagents, no live Zen driving, no ydotool.
Every finding below was reproduced by me with stub processes (a stub
`run_batch3.py` / `run_foo.py` / `run_other.py` / `other.py` that
prints `STUB ... main running` and sleeps 30 s), a compiled C sleeper
binary named `codex`, unit cmdlines, and live `/proc` scans. I did
not trust the fix log's probe claims; I re-ran the prior probes and
wrote my own attack probe. Probe commands and outputs are in the
appendix. Counts below are my predictions confirmed, so a "PASS" on a
predicted-True false-positive case means the false positive exists as
predicted, not that the code is correct; a "FAIL" in my probe log
means the code deviates from correct behavior in the predicted
direction, and each such FAIL maps to a finding below.

Probes: `/tmp/y14b-fix3-rt-probe.py` (my attack probe, final run 100
pass, 9 fail, every fail a finding below), `/tmp/y14b-rt3-live2.py`
(R1 live + long-option live + codex binary leaf),
`/tmp/y14b-rt3-live3.py` (codex binary leaf vs wrapper).
Re-runs of prior probes, all against the current tree: fix3
`/tmp/y14b-fix3-probe.py` 70 pass 0 fail (see F9 for the count
discrepancy), H2 `/tmp/y14b-h2-probe.py` 45/45, fix2
`/tmp/y14b-fix2-probe.py` 31/31, transcription
`/tmp/y14b-transcribe.py` 82 PASS, gate dry `/tmp/y14b-gate-dry.py`
4/4, M1 `/tmp/y14b-m1-probe.py` 3/3, fix2-M1
`/tmp/y14b-fix2-m1-probe.py` 4/4, fix2-rt-M1
`/tmp/y14b-fix2-rt-m1.py` all 12 served-fixture cases PASS
(including TOCTOU step 2 foreign fetch). Two of my own probe
expectations were wrong and corrected with evidence: the H4
continuous margin at N=3.5 @19 ms is exactly 1.835, which rounds
half-up to the plan's 1.84 (Python `round()` gave 1.83 from float
repr; corrected with `Decimal`), and CPython rejects
`--check-hash-based-pycs=always` as "unknown option", so the `=`
form cannot execute (my first live 5c assumed it could; the spaced
form is the real one and is caught live).

## What the fix does correctly (verified, not trusted)

- V1, bundles: `-umrun_batch3`, `-bmrun_batch3`, `-smrun_batch3`,
  `-Emrun_batch3`, `-vmrun_batch3`, `-sumrun_batch3`, `-um
  run_batch3`, `-umfoo.run_batch3`, `-uc` / `-bc` import forms,
  `-ucimport` inline, `-uWignore`, `-sWignore`, `-Xdev`, `-Wu` all
  execute the stub live (where applicable) and are caught
  (`-uWignore` and `-sumrun_batch3` confirmed live + scan-hit).
  `-Wmrun_batch3` and `-Xmrun_batch3` still correctly do not flag
  as `-m` (the value option eats the `m`). `-zmrun_batch3`
  correctly misses (unknown letter kills the bundle). Bundles after
  a `-c` string (`bash -c "python3 -umrun_batch3"`, `bash -c "env
  python3 -umrun_batch3"`) are caught.
- V2, long option: `python3 --check-hash-based-pycs always
  run_batch3.py` executes the stub live and is caught (scan hit);
  `pytest` / `echo` / `python3 other.py` variants of the two-back
  rule all return False.
- V3, guard on flag + two-back: `pytest -W ignore run_batch3.py`,
  `echo -W ignore run_batch3.py`, `python3 other.py -W ignore
  run_batch3.py`, `python3 other.py -u run_batch3.py`,
  `python3 other.py -c run_batch3.py` all return False, while
  `python3 -W ignore run_batch3.py`, `python3 -X dev
  run_batch3.py`, `python3 -Wignore run_batch3.py`, `flock -c
  "python3 -W ignore run_batch3.py"`, `bash -c "python3 -W ignore
  run_batch3.py"` all return True. Double-nested `-W` leaf is
  caught live (pid 183217), double-nested `-c import` leaf is
  caught live (pid 183220).
- V4, codex env chain: `env -i`, `env FOO=bar`, `env -u FOO`,
  `env -uFOO`, `env --unset=FOO`, `env --`, `env -i -u FOO BAR=1`,
  `/usr/bin/env`, and `bash -c "env -i codex ..."` all caught;
  `echo env codex marionette`, `bash -c "echo env codex
  marionette"`, `grep -rn marionette codex`, `cat codex
  marionette-notes.txt`, `bash -c "echo codex marionette"` all
  False. `env FOO codex` correctly False (FOO is the command).
- V5, codex semicolon, direct forms: `codex -c 'import time;
  time.sleep(60) # marionette'` (the H2 live case) True, marker
  before `;` also True, `bash -c "codex --help; echo marionette"`
  False, `bash -c "echo hi; codex exec marionette"` True,
  `bash -c "echo marionette; codex exec ..."` False.
- V6, H4 arithmetic: independently recomputed from the model
  ticks = floor/ceil((850 + N*RTT)/100), bound 2..11. At N=3.5:
  (8,9) @2 ms, (9,10) @19 ms, (10,11) @50 ms; continuous margin
  2.43 @2 ms and exactly 1.835 @19 ms (half-up 1.84); discrete
  margin 1-3 (1 adverse @19 ms, 2-3 good phase); first possible
  fail RTT > 71.4 ms, sure fail >= 100.0 ms; N=3 gives 83.3 /
  116.7 ms. The plan's "reads 8-10", "margin 1-3 discrete,
  1.84-2.43 continuous at N=3.5", "10-11 at 50 ms (margin 0-1)",
  "first fails roughly 70-85 ms", "fails surely at ~100-117 ms"
  are all arithmetically correct. See F10 for the one wording
  remainder.
- V7, hygiene: `py_compile` passes on the file at `3875215`. The
  fix diff `4b589c7..3875215` has 0 em dash, 0 en dash, 0 personal
  info; the single `ydotool` grep hit is the log line "no
  ydotool" (a negative mention). No live Zen driving was done for
  this review; all live stub processes were killed and verified
  gone (`ps` shows 0 remaining).

## R1 (MEDIUM, REGRESSION): `-m <runner>.py` executes and is now missed

`tests/realistic/run_batch3.py:2312-2332` (`_python_executes`) treats
any `-m`/`-c` token between the python token and the script token as
a barrier, but here the script token IS the `-m` flag's own value.
And `2437-2455` (`_is_runner_module`) rejects the `.py` suffix
(`"run_batch3.py"` splits to last component `"py"`, not in
`_RUNNER_MODULES`), so the `-m` branch cannot save it either.

Reproduced live with the stub (all execute, all scan-miss) and by
loading both blobs side by side:

- `python3 -m run_batch3.py`: old (`ad085d9`) True, new
  (`3875215`) False. Live: stub alive, scan hit False (pid run in
  `/tmp/y14b-rt3-live2.py`, R1a).
- `python3 -u -m run_batch3.py`: old True, new False. Live: stub
  alive, scan hit False (R1b).
- `python3 -um run_batch3.py`: old True, new False (my probe 1f;
  tokens after expansion are `['python3', '-u', '-m',
  'run_batch3.py']`, identical shape to the spaced form).
- `python3 -mrun_batch3.py` (joined): False at BOTH commits (the
  old joined `-m` branch also required `_is_runner_module`, which
  rejects the suffix); only the spaced form regressed.

CPython accepts the `.py` suffix for `-m` (verified live: the stub
prints and sleeps; the fix-pass-2 redteam paper documented this
form as caught in its F8). The fix author's probe never tested a
`.py`-suffixed `-m` form (its regression list is "spaced -m
run_batch3", "joined -m run_batch3", "spaced -m foo.run_batch3",
no `.py`), which is how the regression slipped through. No fleet
launcher uses `-m <runner>.py`, so this is AMEND not BLOCK, but it
is a false negative on an executing form one token away from a
documented form, and it reverses a previously verified catch.

Fix (either half alone fixes the spaced form; both together also
fix the joined form): in `_is_runner_module`, strip a trailing
`.py` before matching (CPython semantics); and/or in
`_python_executes`, do not treat a `-m`/`-c` token immediately
before `i` as a barrier (it owns the token at `i`). Re-prove live:
`python3 -m run_batch3.py`, `python3 -um run_batch3.py`,
`python3 -mrun_batch3.py` must then be caught, while `python3
other.py -m run_batch3` stays caught only via the `-m` branch
(that FP is F3, separate) and `pytest -m run_batch3` is unchanged.
See U1.

## F1 (LOW, new FP from expansion): `python3 -crun_batch3.py`

`2244-2268` (`_expand_bundle`) turns `-crun_batch3.py` into `["-c",
"run_batch3.py"]`, then `2289-2310` (`_argv_tokens`) splits the `-c`
value as if it were a `-c` argument's words, and the `-c`
first-word rule in `_is_runner_cmdline` flags it. Live:
`python3 -crun_batch3.py` runs the STRING `"run_batch3.py"` as code
(`NameError: name 'run_batch3' is not defined`, my probe 5b), it
does NOT run the file. Unit returns True. Before pass 3 the single
token never matched, so this false positive is introduced by this
diff. Mechanism: expansion plus the `-c` split conflate python's
`-c` (value is code) with shell `-c` (value is a command line).
Fail-closed and transient; the spelling `-c<runner>.py` is one no
launcher uses. Fix: apply the `-c` first-word rule only when the
`-c` is owned by bash/sh/flock (reuse the `_in_shell_c_string`
ownership check, `2512-2533`); python's own `-c` value is code,
never a file to execute. Note the same change would also correct
`python3 -c "run_batch3.py"` (currently True via the same rule,
pre-existing over-approximation, my probe 2j), while `bash -c
"run_batch3.py"` and `flock -c "run_batch3.py"` stay True. See U2.

## F2 (LOW, codex semicolon scope, wrapper-level): codex `-c` snippet inside a shell `-c` string

`2535-2558` (`_same_command_tokens`) truncates at the `;` inside a
codex `-c` snippet when the codex token itself sits inside a shell
`-c` string, because `2512-2533` (`_in_shell_c_string`) returns
True for the outer shell `-c` and the truncation then treats every
`;` as a shell separator. Reproduced at unit level, all False
although the marker is inside codex's own `-c` snippet:

- `bash -c "codex -c 'import time; x # marionette'"` (my probe 4v)
- `sh -c "codex -c 'import time; x # marionette'"` (4w)
- `flock -c "codex -c 'import time; x # marionette'"` (4x)

The fix log's invariant ("a codex/python `-c` snippet's `;` does
not truncate") holds for the direct/leaf cmdline but not for the
wrapper cmdline. Live impact is bounded: with a real codex binary
(argv[0] is the binary), the leaf process itself IS caught
(`/tmp/y14b-rt3-live3.py`: direct leaf hit pid 183753, wrapped
leaf hit pid 183770, wrapper missed). Same class as the documented
double-nested residual: the wrapper cmdline misses, the leaf
catches it. (My probe's 5i FAIL is the wrapper-level miss; the
shell-script stub's own process is `/bin/sh`, which is a test
artifact, not a second miss.) Fix: in `_same_command_tokens`,
do not treat `;` as a separator when it falls inside a
codex/python `-c` argument (track `-c` argument spans), or record
the wrapper-level miss as a residual with the leaf-backstop
reasoning. See U3.

## F3 (LOW, carryover): the `-m` and import branches still have no python-executes guard

U3 of the fix-pass-2 verdict said to guard the `-W`/`-X` two-back
rule "and consider the same for the `-m` branches". Pass 3 guarded
only the flag branch and the two-back rule. Reproduced at unit
level, all return True although nothing executes the runner:

- `pytest -m run_batch3`, `echo -m run_batch3`, `python3
  other.py -m run_batch3` (my probe 2c/2d/2e; the `-m` branch,
  `2437` area, has no `_python_executes` call)
- `echo import run_batch3`, `grep import run_batch3`, `bash -c
  "echo import run_batch3"`, `python3 other.py import run_batch3`,
  `echo from run_batch3 import main` (import branch, also
  unguarded; verified in a follow-up check)

Pre-existing (fix-pass-2 F3 noted the `-m` shape; the import
branch dates to fix pass 1, H1). Fail-closed and transient. Either
guard both branches with `_python_executes` (careful: the `-m`
branch must still accept `python3 -m run_batch3`, where the module
token IS the `-m` value, so the guard needs the same
immediately-before exemption as U1), or record the class in the
docstring. See U4.

## F4 (LOW): `_python_executes` does not reset at shell command boundaries

`2312-2332` scans back to the nearest python token regardless of
`;`/`&&`/`||`/`|` between it and `i`. Reproduced at unit level,
both return True although the runner filename belongs to a
different shell command than the python invocation:

- `bash -c "python3 --version; pytest -W ignore run_batch3.py"`
  (my probe 2k; the bare `python3 --version` carries no script,
  `-m` or `-c`, so it does not trip the barrier, and the later
  pytest `-W` passes the two-back rule)
- `bash -c "python3 --version; echo -u run_batch3.py"` (2l, same
  class via the flag branch)

The guard was pass 3's fix for F3; the fix is incomplete for
multi-command `-c` strings. Fail-closed, transient, needs a `-c`
string combining a bare python invocation with a later pytest/echo
`-W`/`-u` plus a runner filename. Fix: stop the backward scan at
shell separators, so only a python token in the same shell command
as `i` counts. Re-prove: 2k/2l False, `bash -c "python3 -W ignore
run_batch3.py"` still True. See U5.

## F5 (LOW): the guard is blind to extensionless scripts

`2312-2332` only treats `.py` basenames (and `-m`/`-c`) as script
barriers. Reproduced at unit level, both return True although
`run_batch3.py` is an argument to another script:

- `python3 run_other -W ignore run_batch3.py` (my probe 2g)
- `python3 other -W ignore run_batch3.py` (2h)

Fail-closed. The barrier cannot simply be "any non-flag token":
in `python3 -W ignore run_batch3.py` the value `ignore` is a
non-flag token between python and the script, and it must not
block. A value-aware barrier scan (skip one token after a known
value-taking flag `-W`/`-X`/`--check-hash-based-pycs`) is a
possible direction, but it does not by itself identify an
extensionless script token, so I recommend recording this as a
limitation rather than demanding a fix. See U6.

## F6 (LOW): `_codex_at_command` treats ANY `-c` as a command boundary

`2475-2510` returns True for codex immediately after any `-c`
token, including python's `-c`. Reproduced at unit level, both
return True although codex is a word inside a python snippet, not
executed:

- `python3 -c "codex = load('marionette')"` (my probe 4ag)
- `python3 -c "codex marionette"` (4ah, minimal form)

`_in_shell_c_string` (`2512-2533`) already implements the
shell-ownership check for the semicolon scope; the anchor does not
use it. Fail-closed; needs a python snippet whose first word is the
bare word `codex` plus a marker anywhere in the rest, which is
contrived. Fix: in `_codex_at_command`, when the boundary token is
`-c`, require it to be shell-owned (bash/sh/flock), the same check
`_in_shell_c_string` makes. Re-prove: 4ag/4ah False, `bash -c
"codex marionette"` and `flock -c "codex marionette"` still True.
See U7.

## F7 (LOW): glued `;` is not a separator to the matcher

`2289-2310` splits `-c` strings on whitespace only, and
`2535-2558` stops only at exact `;` tokens or tokens ending in
`;`. The shell splits on `;` even when glued to the previous word.
Reproduced at unit level, both return True although the marker is
in the later shell command:

- `bash -c "codex --help;echo marionette"` (my probe 4z)
- `bash -c "codex --help ;echo marionette"` (4aa)

Fail-closed FP; the fix3 probe tested only the spaced form
(`codex --help; echo marionette`). Fix: split `-c` words on `;`
(and `&&`/`||`/`|`) as well as whitespace in `_argv_tokens`, or
make `_same_command_tokens` stop at tokens containing `;`
mid-token. Re-prove: 4z/4aa False, `bash -c "codex --help; echo
marionette"` still False, `bash -c "echo hi; codex exec
marionette"` still True. See U8.

## F8 (INFO, doc): sudo dropped from the recorded codex gaps

The fix-pass-2 docstring recorded sudo as a codex wrapper gap.
The pass-3 docstring (`2559-2571`, "Known gaps: nohup, setsid,
timeout, flock-direct, time and nice wrappers miss") no longer
lists it, and `grep -c sudo tests/realistic/run_batch3.py` is 0,
but `sudo codex marionette` still returns False (my probe 4b).
The fix log's F4 note does not mention sudo either. Re-add sudo to
the gap list. Doc-only fix. See U9.

## F9 (INFO, probe accuracy): the fix author's probe count and one wrong expectation

- The commit message claims "fix3 probe 72/72", but the probe file
  in `/tmp` has 70 checks (36 unit + 28 codex + 6 live), and my
  re-run shows 70 PASS, `FAILURES: 0`. Off by 2; correct the count
  to 70/70 in the log.
- The probe's case ("--check-hash-based-pycs=always (joined)",
  expected True) asserts True for a form CPython rejects. Live:
  `python3 --check-hash-based-pycs=always run_batch3.py` prints
  `unknown option --check-hash-based-pycs=always` and exits; it
  cannot execute. The unit True comes from the pre-existing flag
  branch (any `-...` token before a runner script), not from any
  execution. The probe bakes in a false positive as a pass. Same
  pre-existing shape: `--check-hash-based-pycs run_batch3.py`
  (runner as the option value) returns True at unit level while
  live CPython errors (`--check-hash-based-pycs must be one of
  'default', 'always', or 'never'`, my probe 5d), and
  `-Wrun_batch3.py` returns True at unit level while live it drops
  into interactive mode executing nothing (my probe 5e; the scan
  flags that live interactive process, seen as pid 183208 in my
  5g hits). All pre-existing, fail-closed, low plausibility; note
  them, do not block on them. Correct the probe expectation for the
  `=` form to False or drop the case. See U10.

## F10 (INFO, wording): H4 restatement keeps Council 3's count of 4 as a bracket

The numbers are all correct (V6). U6 asked to "say Council 3's
count of 4 overcounts by 1, or drop it". The plan instead keeps
"Council 3 counts 4" in a bracketing sentence ("Council 1 counts
3, Council 3 counts 4; the advancing read's own transit
contributes about half a round trip, so the two counts bracket the
true value"). The leg-precise count is 3.0 (fix-pass-2 redteam V7),
so 4 overcounts by a full round trip rather than bracketing the
true value from above in any tight sense. No arithmetic impact:
every quoted number is computed at the conservative N=3.5. One
clause stating the leg-precise count is 3.0 and 4 overcounts by 1
closes U6's letter. See U11.

## Unblock conditions

- U1 (R1, code): fix the `-m <runner>.py` regression. In
  `_is_runner_module`, strip a trailing `.py` before matching,
  and/or in `_python_executes`, exempt a `-m`/`-c` token
  immediately before `i` from the barrier. Re-prove live with the
  stub: `python3 -m run_batch3.py`, `python3 -u -m run_batch3.py`,
  `python3 -um run_batch3.py`, `python3 -mrun_batch3.py` must all
  be caught; `python3 -m run_batch3` and `python3 -m
  foo.run_batch3` still caught; `python3 -W ignore run_batch3.py`
  still caught.
- U2 (F1, code or record): apply the `-c` first-word rule only
  when the `-c` is shell-owned (bash/sh/flock). Re-prove:
  `python3 -crun_batch3.py` False (live: NameError, no execution),
  `bash -c "run_batch3.py"` and `flock -c "run_batch3.py"` still
  True.
- U3 (F2, code or record): do not truncate at `;` inside a
  codex/python `-c` argument in `_same_command_tokens`, or record
  the wrapper-level miss with the leaf-backstop reasoning.
  Re-prove: `bash -c "codex -c 'import time; x # marionette'"`
  True at unit level (or the residual is recorded with the live
  leaf catch, pid 183770, as evidence).
- U4 (F3, code or record): guard the `-m` and import branches with
  `_python_executes` (with the U1 immediately-before exemption for
  the `-m` branch), or record the false-positive class in the
  docstring. Re-prove: `pytest -m run_batch3`, `echo -m
  run_batch3`, `echo import run_batch3` False; `python3 -m
  run_batch3` still True.
- U5 (F4, code): stop the `_python_executes` backward scan at
  shell separators (`;`, `&&`, `||`, `|`). Re-prove: `bash -c
  "python3 --version; pytest -W ignore run_batch3.py"` and `bash
  -c "python3 --version; echo -u run_batch3.py"` False; `bash -c
  "python3 -W ignore run_batch3.py"` still True.
- U6 (F5, record only): note the extensionless-script blind spot
  in the `_python_executes` docstring.
- U7 (F6, code): in `_codex_at_command`, require a `-c` boundary
  token to be shell-owned. Re-prove: `python3 -c "codex
  marionette"` False; `bash -c "codex marionette"` still True.
- U8 (F7, code): split `-c` words on `;` (and `&&`/`||`/`|`) in
  `_argv_tokens`, or stop `_same_command_tokens` at mid-token
  `;`. Re-prove: `bash -c "codex --help;echo marionette"` False;
  `bash -c "echo hi; codex exec marionette"` still True.
- U9 (F8, doc): re-add sudo to the `_is_codex_executor` known-gap
  list.
- U10 (F9, log/probe): correct the fix3 probe count to 70/70 in
  the log, and correct or drop the `--check-hash-based-pycs=always`
  (`=`) probe expectation (CPython rejects the form).
- U11 (F10, plan wording): add one clause to the H4 note stating
  the leg-precise count is 3.0 and Council 3's count of 4
  overcounts by 1.

## Hygiene

`py_compile` passes on the file at `3875215`. The fix diff has 0
em dash, 0 en dash, 0 personal info; the single `ydotool` grep hit
is the log line "no ydotool". No live Zen driving was done for this
review. All live stub processes were killed and verified gone.

## Timed work log (Asia/Ho_Chi_Minh, 21/11)

- 22:12: task received. Fetch origin, confirm HEAD `5792a82` on
  `todolist-push`, read the fix-pass-3 diff (3 files, runner file
  +278/-52 vs `4b589c7` for the code file) and the fix-pass-2
  redteam verdict `4b589c7`.
- 22:15: verified `5792a82` blob/md5 (`3a9b7b17...`,
  `e9e3519a...`); read the fix3 probe (70 checks, not 72 as the
  commit message claims).
- 22:15-22:17: re-ran prior probes against the current tree:
  fix3 70/70, H2 45/45, fix2 31/31, transcription 82, gate dry
  4/4, M1 3/3, fix2-M1 4/4, fix2-rt-M1 all-12 PASS.
- 22:17-22:19: wrote my attack probe (100 cases); first run 11
  FAILs. Two of my own expectations corrected with evidence (H4
  rounding via `Decimal`, CPython rejecting the long-option `=`
  form).
- 22:19-22:20: proved R1 is a regression by loading both blobs:
  `python3 -m run_batch3.py` True at `ad085d9`, False at
  `3875215`; confirmed live (stub alive, scan miss). Confirmed
  the codex 4v leaf backstop with a real `codex` binary (leaf pid
  183770 hit, wrapper missed). Confirmed the import branch is
  unguarded (`echo import run_batch3` True).
- 22:20-22:22: final probe re-run after correcting my two
  expectations (100 pass, 9 fail, every fail a finding); hygiene
  checks; paper written, committed, pushed, verified.

## Appendix: key reproduction excerpts

My attack probe, final run (`/tmp/y14b-fix3-rt-probe-final.log`,
100 pass, 9 fail):

```
FAIL 1f -um run_batch3.py (spaced module after bundle): got False want True
FAIL 4v bash -c codex -c snippet, marker after ; (ESCAPE?): got False want True
FAIL 4w sh -c codex -c snippet, marker after ;: got False want True
FAIL 4x flock -c codex -c snippet, marker after ;: got False want True
FAIL 4z bash -c codex --help;echo marionette (glued ;, no space): got True want False
FAIL 4aa bash -c codex --help ;echo marionette (glued ; after space): got True want False
FAIL 4ag python3 -c codex = load(marionette) (codex is a -c word): got True want False
FAIL 4ah python3 -c codex marionette (snippet starting with codex): got True want False
FAIL 5i live bash -c codex -c snippet caught: got False want True
```

Old-vs-new blob comparison (R1):

```
'python3 -m run_batch3.py'        old=True  new=False  <-- REGRESSION
'python3 -u -m run_batch3.py'     old=True  new=False  <-- REGRESSION
'python3 -um run_batch3.py'       old=True  new=False  <-- REGRESSION
'python3 -mrun_batch3.py'         old=False new=False
'python3 --check-hash-based-pycs always run_batch3.py'
                                  old=False new=True   <-- FIXED
'pytest -W ignore run_batch3.py'  old=True  new=False  <-- FIXED (intended)
```

Live excerpts (`/tmp/y14b-rt3-live2.py`, `/tmp/y14b-rt3-live3.py`):

```
R1a live python3 -m run_batch3.py: alive=True scan_hit=False (executes but missed = REGRESSION)
R1b live python3 -u -m run_batch3.py: alive=True scan_hit=False
LONG live spaced long-opt: alive=True scan_hit=True
5b live -crun_batch3.py: alive=False out='Traceback ... NameError: name 'run_batch3' is not defined'
5d live long-opt value=runner: alive=False out='--check-hash-based-pycs must be one of 'default', 'always', or 'never''
5c (first run) live long-opt = form: alive=False out='unknown option --check-hash-based-pycs=always'
direct codex-bin leaf hits: [(183753, '/tmp/y14b-rt3-bin/codex -c import time; x # marionette')]
wrapped leaf hits: [(183753, ...), (183770, '/tmp/y14b-rt3-bin/codex -c import time; x # marionette')]
wrapped bash hits: []
```

H4 recomputation (exact, `Decimal`):

```
N=3.5 @2ms: ticks (8,9), continuous margin 2.43, discrete 2..3
N=3.5 @19ms: ticks (9,10), continuous margin exactly 1.835 (half-up 1.84), discrete 1..2
N=3.5 @50ms: ticks (10,11), continuous margin 0.75, discrete 0..1
N=3.0: first fail > 83.3 ms, sure fail >= 116.7 ms
N=3.5: first fail > 71.4 ms, sure fail >= 100.0 ms
N=4.0: first fail > 62.5 ms, sure fail >= 87.5 ms
```

Prior-probe re-run log lines:

```
fix3: FAILURES: 0 [] (70 PASS)
h2:   FAILURES: 0 [] (45 PASS)
fix2: FAILURES: 0 [] (31 PASS)
transcribe: 82 PASS
gate-dry: FAILURES: 0 [] (4 PASS)
m1:   FAILURES: 0 [] (3 PASS)
fix2-m1: FAILURES: 0 [] (4 PASS)
fix2-rt-m1: probe2 done (all 12 served-fixture cases PASS)
```
