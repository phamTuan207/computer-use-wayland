# Fix-pass-4 redteam: AMEND

Scope: ONLY the fix-pass-4 diff, commit
bf3c939741f86c6c639c730882f8a4f721265a74 (branch todolist-push),
against its parent. Code changes in
tests/realistic/run_batch3.py; the plan got an H4 wording fix and
a fix-pass-4 record bullet; the log got the fix-pass-3 redteam
verdict section plus fix-pass-4 adjudication and verification.
Method: re-ran every claimed verification number against the
current tree; wrote an independent unit probe
(/tmp/y14b-fix4-rt-probe.py, 36 checks) and an independent live
probe (/tmp/y14b-fix4-rt-live.py, 5 checks, /proc scans plus
sleeping stubs); checked every new finding against the fix3
parent code (loaded from bf3c939^) so a pre-existing issue is
never blamed on fix4; verified the live CPython semantics of
every disputed form with timeout runs. No Zen driving, no
ydotool, no live browser work.

## Verdict: AMEND

Three new LOW findings, all reproduced live, none with live gate
impact. The gate still refuses every real live collision I could
build, and every prior probe stays green. But finding R2 is a
genuine regression against fix3: nine cmdlines fix3 caught are
now missed at unit level (the leaf process is still caught live,
so the gate outcome survives, but the unit coverage went
backwards). A fix pass must not erode the previous pass. Ship
after U1 (one small fix to _c_is_shell, specified below, plus
re-probe). U2 and U3 are fix-or-record.

## Verification re-runs (all against the current tree)

PASS lines counted only, not the "FAILURES:" summary line, which
starts with FAIL. Every probe exited 0.

- Fix4 probe /tmp/y14b-fix4-probe.py: 64/64 PASS.
- H2 probe /tmp/y14b-h2-probe.py: 45/45 PASS.
- Fix2 probe /tmp/y14b-fix2-probe.py: 31/31 PASS.
- Fix3 probe /tmp/y14b-fix3-probe.py: 70/70 PASS.
- Transcription /tmp/y14b-transcribe.py: 82 PASS.
- Gate dry /tmp/y14b-gate-dry.py: 4/4 PASS.
- M1 probe /tmp/y14b-m1-probe.py: 3/3 PASS.
- M1 all-12 /tmp/y14b-fix2-m1-probe.py: 4/4 PASS.
- py_compile OK; import OK.

## Fix-pass-3 item disposition

- R1 FIXED. Verified live: `cd /tmp/y14b-dummies && timeout 3
  python3 -m run_foo.py` exits 124 (executes the sleeping stub);
  `-mrun_foo.py` and `-um run_foo.py` also exit 124. Dotted
  `.py` also executes: `timeout 3 python3 -m foo.run_foo.py`
  (package dir /tmp/rt4-pkg/foo) exits 124, so the .py strip in
  _is_runner_module (line 2522) matches CPython, including the
  dotted form.
- F1 FIXED. Verified live: `python3 -crun_foo.py` exits 1 with
  `NameError: name 'run_foo' is not defined`.
- F2 FIXED. `bash -c "codex -c 'import time; x # marionette'"`
  is caught (fix4 probe codex case passes).
- F3 PARTIALLY FIXED. The simple forms now miss as claimed
  (`pytest -m run_batch3`, `echo -m run_batch3`,
  `echo import run_batch3` all False). But the import guard is
  separator-blind, see finding R4.
- F4 FIXED. The guard resets at shell separators; fix4 probe
  F4 cases pass.
- F5 FIXED. The extensionless run_* barrier works and I found
  no over-fire: `python3 -W ignore::run_batch3 run_batch3.py`
  still True (a -W value that merely mentions run_ does not trip
  the barrier), `python3 run_tests -W ignore run_batch3.py`
  False (run_tests really is the script there).
- F6 FIXED for the documented forms (`python3 -c "codex
  marionette"` now False). But the _c_is_shell walk-back
  regresses wrapper-prefixed shell -c, see finding R2 (codex
  side, A7/A8).
- F7 FIXED. Glued separators split correctly in both
  directions: `codex --help;echo marionette` False,
  `codex exec foo&&marionette` False,
  `codex exec foo||marionette` False (all verified live in my
  unit probe).
- F8 FIXED. sudo is restored to the recorded codex gaps:
  `grep -n sudo tests/realistic/run_batch3.py` hits line 2567
  ("nice and sudo wrappers ...").
- F9 FIXED. The fix3 probe is 70 checks, not 72 (re-run
  confirms 70/70). The joined `=` form is documented as a
  fail-closed over-approximation. Verified live:
  `python3 --check-hash-based-pycs=always --version` exits 2
  with `unknown option --check-hash-based-pycs=always`.
- F10 FIXED in substance. The H4 note (plan lines 639 to 646)
  now states Council 1's 3 undercounts by half a round
  trip and Council 3's 4 overcounts by half a round trip, and
  the word "bracket" no longer appears in the H4 note itself
  (remaining "bracket" mentions in the plan are in the
  fix-pass-4 record bullet quoting the removal, and in the
  log's historical sections). Note on the literal F10 demand
  ("overcounts by 1"): the new wording is arithmetically the
  correct one. The true value is about 3.5 round trips, so 4
  overcounts by half, not by one; "by 1" is only true as 4
  minus Council 1's 3. The plan now states the half-round-trip
  error on each side, which is the precise claim, so F10 is
  met.

## New findings

### R2 LOW, regression vs fix3: _c_is_shell walks to argv[0], so wrapper-prefixed shell -c is misclassified

File: tests/realistic/run_batch3.py, _c_is_shell lines 2322
to 2332. The walk-back stops only at a previous -c or a
separator, so it lands on argv[0] and tests argv[0] against
(bash, sh, flock). Any wrapper word before the shell makes it
return False, even though the -c IS a shell -c and the runner
IS executed. The same walk-back shape is duplicated in
_in_shell_c_string (lines 2603 to 2622), which does not call
_c_is_shell.

Reproduced live (unit probe /tmp/y14b-fix4-rt-probe.py, each
got False, want True; fix3 parent code returns True for every
one, verified by loading bf3c939^):

- A1 `env bash -c run_batch3.py`
- A2 `sudo bash -c run_batch3.py`
- A3 `timeout 60 bash -c run_batch3.py`
- A4 `nice bash -c run_batch3.py`
- A5 `env -i bash -c run_batch3.py`
- A6 `/usr/bin/env bash -c run_batch3.py`
- A7 `env bash -c codex exec marionette` (_is_codex_executor,
  via _codex_at_command lines 2557 to 2586, whose F6 check
  calls _c_is_shell)
- A8 `sudo bash -c codex exec marionette` (same path)
- A9 `dash -c run_batch3.py` (dash is a real POSIX shell and
  executes the -c string; it is not in the (bash, sh, flock)
  allowlist at all)

Controls that still pass: `bash -c run_batch3.py` True,
`sh -c run_batch3.py` True, `/bin/bash -c run_batch3.py`
True, `flock /tmp/l bash -c run_batch3.py` True (the
walk-back lands on flock, which saves it), `bash -c codex
exec marionette` True.

Live gate impact: NIL, proved live. I spawned
`env bash -c /tmp/run_foo_rt4.py` (executable stub with a
python3 shebang, sleeps 60). bash execs the script, so the
live process is `python3 /tmp/run_foo_rt4.py`, and
_scan_other_runners lists it (live probe L1: hits mentioning
the stub `['python3 /tmp/run_foo_rt4.py']`). In every wrapper
form the wrapper either execs (its cmdline becomes the
leaf's) or forks (the leaf exists beside it), so a process
with a clean catchable cmdline always exists. The regression
is therefore unit-level coverage loss, not a live hole. It
still blocks ship because a fix pass must not move nine
cmdlines from True to False, and the fix is small (see U1).

Exact live commands:

```
$ printf '#!/usr/bin/env python3\nimport time\ntime.sleep(60)\n' > /tmp/run_foo_rt4.py && chmod +x /tmp/run_foo_rt4.py
$ python3 /tmp/y14b-fix4-rt-live.py
L1 hits mentioning stub: ['python3 /tmp/run_foo_rt4.py']
PASS L1 env-wrapped runner leaf caught live: got True want True
PASS L1 unit env bash -c is False: got False want False
```

### R3 LOW, new false-positive class: codex -c include-everything swallows a marker in a LATER shell command

File: tests/realistic/run_batch3.py, _same_command_tokens
lines 2625 to 2663, the `parts.extend(tokens[j:])` at line
2649. Once a codex -c flag is seen, everything after it is
included, including a `;` and whatever follows it. So a marker
that belongs to a later shell command counts against codex.

Reproduced live (unit probe B1/B2 got True, want False;
fix3 parent code returns False for both):

- B1 `bash -c "codex -c 'hello'; echo marionette"` True.
  `codex -c 'hello'` drives nothing; marionette is echo's
  argument.
- B2 `bash -c "codex -c 'hello'; echo geckodriver"` True.
  Same shape with a different marker.

Live proof: I spawned `bash -c "codex -c 'hello'; echo
marionette"` with the dummy codex stub (sleeps 60) first on
PATH, and _scan_other_runners flagged the wrapper bash
(live probe L2 PASS: `codex -c 'hello'; echo marionette`
in hits). That is a spurious refusal: the gate would refuse
a launch over a codex invocation that drives no browser.

Severity is LOW because the direction is fail-closed (a
refusal, not a missed collision), the form is contrived (a
codex -c snippet followed in the same -c string by a later
command naming a marker), and the code already discloses it
in the comment at lines 2650 to 2653 ("a marker in a LATER
shell command would too, but that form is contrived and the
gate is fail-closed"). The disclosure does not make the
false positive go away, so it is a finding, not just a note.
Controls: `bash -c "codex -c 'hello'; echo done"` False,
`bash -c "codex -c 'import time; x # marionette'"` True
(the F2 fix still holds).

### R4 LOW, guard incompleteness: the import branch guard is separator-blind

File: tests/realistic/run_batch3.py, import branch lines
about 2490 to 2510. The guard finds the NEAREST -c anywhere
before the import token and asks _python_executes about it,
without requiring the import to sit in the same shell command
as that -c. A -c from an earlier command therefore satisfies
the guard for an import in a later command that executes
nothing.

Reproduced live (unit probe C1/C2 got True, want False;
fix3 parent code also returns True, so this is a residual
gap in the new guard, not a fix4 regression, but the guard
was the F3 fix and it does not close this form):

- C1 `bash -c "python3 -c 'import x'; echo import
  run_batch3"` True. The import is echo's argument in the
  second command.
- C2 direct argv `python3 -c "import x"; echo import
  run_batch3` True (same shape without the bash -c wrapper).

Live proof: I spawned `bash -c "python3 -c 'import time;
time.sleep(60)'; echo import run_batch3"`. The wrapper bash
cmdline flags True (live probe L3:
`bash -c python3 -c 'import time; time.sleep(60)'; echo
import run_batch3`), while the leaf `python3 -c import time;
time.sleep(60)` correctly flags False. The gate would refuse
a launch over an echo that never runs.

Severity LOW: fail-closed direction, contrived form, and the
simple F3 forms the guard was built for are genuinely fixed.
Controls: `echo import run_batch3` False,
`python3 -c "import run_batch3"` True,
`python3 script.py -c "import run_batch3"` False,
`env python3 -c "import run_batch3"` True.

## INFO, pre-existing, not fix4 (verified against bf3c939^)

- I1: `python3 -m ./run_batch3` and `python3 -m
  /abs/run_batch3` both return True, but CPython rejects
  both (verified live: `./run_foo.py` exits 1, "Relative
  module names not supported"; the absolute path exits 1,
  ModuleNotFoundError). Fix3 also returns True for both, via
  the same basename strip, so this is a pre-existing
  fail-closed false positive, not a fix4 change. The fix4
  .py strip itself is correct (dotted `.py` executes, exit
  124, see R1).
- I2: a glued ";" on a .py token misses:
  `bash -c "python3 run_batch3.py; echo done"` returns False
  (the token is `run_batch3.py;`, which fails the .py suffix
  test). Fix3 also False. Wrapper-level only; the leaf
  python3 process is caught live.
- I3: nested quotes miss the import branch:
  `bash -c "codex -c 'x'; python3 -c 'import run_batch3'"`
  returns False (the -c re-split leaves quote characters on
  `'import`). Fix3 also False. Wrapper-level only; the leaf
  python3 -c process is caught live.
- I4: direct argv `codex -c hello ; echo marionette` returns
  True via the non-shell-c all-tokens path in
  _is_codex_executor. Fix3 also True. Same shape as R3
  outside bash -c, pre-existing.
- I5: a lone "|" inside a token is deliberately not a
  separator (_is_cmd_separator docstring, lines 2312 to
  2320), so `bash -c "codex --help|echo marionette"` returns
  True (the marker is echo's argument). Fix3 also True.
  Documented design choice; the glued && and || cases ARE
  split correctly (both False, verified live in my probe).

## What verified clean

- The moved -m branch does not over-fire on non-python -m:
  `pytest -m run_batch3`, `echo -m run_batch3`,
  `git -m run_batch3` (via _python_executes) all False;
  `python3 -m run_batch3` True; `env python3 -m run_batch3`
  True; a -m in an earlier command does not leak across `;`.
- _c_is_shell does not misclassify the plain forms: bash,
  sh, /bin/bash, flock all True; python3 and codex -c both
  False.
- The extensionless run_* barrier does not over-fire on a
  flag value (E1 above) and does catch a real extensionless
  script as the barrier (E2 above).
- The import guard does not accept non-python imports
  (`echo import`, `codex -c import` both False) and does not
  miss a python -c import through env, python3.12, or plain
  python (all True).
- The F7 glued-separator split is correct in both
  directions, including `codex exec foo&&marionette` and
  `codex exec foo||marionette` (False, correct: the marker
  there names a second command, not a codex argument) and
  `codex exec marionette | cat` (True, correct: the marker
  is codex's argument).

## Unblock conditions

- U1 REQUIRED (R2): fix _c_is_shell (lines 2322 to 2332) so
  the walk-back stops at the command owning the -c instead
  of argv[0]. Check the token immediately before the -c
  first: bash/sh/flock there means shell; a bare command
  word there (python, python3, codex, dash) means not
  shell. Walk further back ONLY past argument-like tokens:
  flags, VAR=value assignments, and path arguments such as
  flock's lockfile (basename not a known command). Apply
  the same logic in _in_shell_c_string (lines 2603 to
  2622), which currently duplicates the walk-back instead
  of calling _c_is_shell. Re-probe must show A1 to A14 all
  PASS (A1-A9 True, A10-A14 True), the fix4 probe still
  64/64, and all other regression probes green.
- U2 FIX OR RECORD (R4): bound the import guard to the same
  shell command as the -c (stop the nearest--c search at a
  separator, and require the import to follow the -c within
  that command). C1 and C2 must then miss. If declined,
  record the exact forms in the _is_runner_cmdline
  docstring as a known residual, the way the -c
  include-everything rule is recorded today.
- U3 FIX OR RECORD (R3): bound the codex -c
  include-everything rule so a marker after a top-level
  shell separator following the snippet does not count. B1
  and B2 must then miss. If declined, extend the existing
  code comment (lines 2650 to 2653) to name the exact form
  (`codex -c 'hello'; echo marionette`) instead of calling
  it contrived in general terms.
- U4 PAPERWORK: none. Hashes verify exactly (below), F9 and
  F10 verify, hygiene is clean.

## Hash record

- Commit bf3c939741f86c6c639c730882f8a4f721265a74.
- run_batch3.py at bf3c939: git blob
  585fb8016b0618ab02b3e97afa362dbcce7342c9, md5
  2920f1697edb3b33711b83b8a874d88b. Working file md5 is the
  same value, and `git diff bf3c939 HEAD --
  tests/realistic/run_batch3.py` is empty (0 lines), so the
  tree reviewed is the commit reviewed.
- The plan's md5 line (lines 614 to 615) and the log's
  fix-pass-4 entry (lines 686 to 687) record the same blob
  and md5.

## Hygiene

- py_compile OK; import OK.
- 0 em dash and 0 en dash in the fix diff (`git show
  bf3c939 | grep -cP` for both characters returns 0) and 0
  in this paper (checked the same way before commit).
- 0 personal info in the fix diff (no real names, emails,
  addresses, or phone numbers in the diff content).
- No live Zen driving, no browser work, no ydotool.
- Stub processes: my live probe spawned three stub trees
  (env bash stub, dummy codex stub, python3 -c sleep). Two
  orphaned `sleep 60` grandchildren survived my first
  kill pass (my kill order listed children after killing
  the parent, so the orphan was missed); both were killed
  by exact PID and verified gone. Final check: `pgrep -a
  sleep` returns nothing, `pgrep -af run_foo_rt4` returns
  nothing. (One `pkill -f` during cleanup matched my own
  exec shell's cmdline and killed that shell only; no repo
  or review state was affected.)

## Probes used

- /tmp/y14b-fix4-rt-probe.py: 36 unit checks. 13 FAIL,
  all fix4-new (A1-A9, B1-B2, C1-C2); 23 PASS, including
  the pre-existing residuals documented as INFO.
- /tmp/y14b-fix4-rt-live.py: 5 live checks, 0 FAIL after
  correcting one bad expectation in the first run (my L1
  check looked for the string `bash -c /tmp/run_foo_rt4.py`
  in the scan hits, but bash execs the script, so the live
  process is `python3 /tmp/run_foo_rt4.py`; the corrected
  check passes).
- /tmp/rt4-rb3-fix3.py: the fix3 parent file, loaded for
  the fix3-vs-fix4 comparison of every finding.
- /tmp/run_foo_rt4.py: executable sleeping stub for the
  live wrapper tests. /tmp/rt4-pkg/foo/run_foo.py: package
  stub for the dotted -m live test.
