# Council Voice 2: Y14b fix-pass-4 review (gate and process check)

- Scope: the FIX DIFF ONLY, commit bf3c939 (todolist-push,
  bf3c939741f86c6c639c730882f8a4f721265a74), file
  tests/realistic/run_batch3.py, plus the plan H4 wording fix and the
  log fix-pass-4 record. The whole runner was NOT re-reviewed.
- Verdict: **AMEND**. Every claimed fix reproduces, the full regression
  set re-passes under my own runs, and the two new findings are LOW,
  wrapper-level, with the leaf process always caught live. No fleet
  launcher uses the affected forms, so nothing here BLOCKs, but both
  findings are small, concrete, and in the same classes fix pass 4
  already worked (F4/F7), so one more small fix pass should take them.
- Reviewer: Council 2 (gate and process check). No live Zen driving.
  No ydotool. Probes run on the VM only, against dummy stubs.
- Reviewed tree: run_batch3.py blob 585fb8016b0618ab02b3e97afa362dbcce7342c9,
  md5 2920f1697edb3b33711b83b8a874d88b, identical to the claimed values
  (git hash-object + md5sum, re-checked 22:50 +07 21/11).

## 1. Regression set, re-run independently (all counts are PASS lines only)

Each probe was re-run by me, in this order, against the current tree
(bf3c939 is an ancestor of HEAD; run_batch3.py is unchanged since it,
git diff HEAD shows nothing for the file):

| Probe | Command | Result |
| --- | --- | --- |
| fix4 | python3 /tmp/y14b-fix4-probe.py | 64 PASS lines, exit 0, FAILURES: 0 |
| H2 | python3 /tmp/y14b-h2-probe.py | 45 PASS lines, exit 0, FAILURES: 0 |
| fix2 | python3 /tmp/y14b-fix2-probe.py | 31 PASS lines, exit 0, FAILURES: 0 |
| fix3 | python3 /tmp/y14b-fix3-probe.py | 70 PASS lines, exit 0, FAILURES: 0 |
| transcription | python3 /tmp/y14b-transcribe.py | 82 PASS lines, exit 0, FAILURES: 0 |
| gate dry | python3 /tmp/y14b-gate-dry.py | 4 PASS lines, exit 0, FAILURES: 0 (clean re-run, see note below) |
| M1 | python3 /tmp/y14b-m1-probe.py | 3 PASS lines, exit 0, FAILURES: 0 |
| M1 all-12 | python3 /tmp/y14b-fix2-m1-probe.py | 4 PASS lines, exit 0, FAILURES: 0 |

All eight claimed counts CONFIRMED. (The grep -c '^FAIL' count is 1
for a passing probe because the "FAILURES: 0" summary line itself
starts with FAIL, as the brief warned. I counted ^PASS lines only.)

Gate-dry process note (INFO-4, see section 4): my first two gate-dry
runs did NOT pass, and neither failure was a fix-pass-4 defect. Run 1
(in the sequential loop, right after the fix3 probe) gave 3/4, gate C
failed, with "runner process live" hits for pids 192812
(python3 -m run_foo.py), 192813 (python3 -um run_foo.py) and 192815
(bash -c codex exec marionette;echo done). Run 2 (alone, minutes
later) gave 2/4, gates A and C failed, with hits including pid 193404,
a concurrent Council 3 worker re-running the h2/fix2/fix3 probes
(its bash cmdline contains python3 -m py_compile
tests/realistic/run_batch3.py plus python3 -c "import run_batch3",
which self-flags through the documented import over-approximation),
plus its live dummies (python3 run_foo.py, flock, python3 -m run_foo,
codex -c ... marionette). After that worker finished (its
/tmp/c3-*.log files timestamped 15:43, ps quiet), the clean re-run
gave 4/4, exit 0, no stray processes. Lesson: gate-dry scans the real
/proc, so it is only meaningful with no sibling live probe running on
the shared VM. The claimed 4/4 stands, but the number is
order-sensitive, and any future re-run must check ps first.

## 2. Live proofs, re-verified by me (dummy dir /tmp/y14b-dummies)

Run from /tmp/y14b-dummies, stub run_foo.py sleeps 60:

- timeout 2 python3 -m run_foo.py -> exit 124 (executes). CONFIRMED.
- timeout 2 python3 -mrun_foo.py -> exit 124. CONFIRMED.
- timeout 2 python3 -um run_foo.py -> exit 124. CONFIRMED.
- timeout 2 python3 -crun_foo.py -> exit 1, stderr "NameError: name
  'run_foo' is not defined" (file never runs). CONFIRMED.
- python3 --check-hash-based-pycs always --version -> "Python 3.12.3",
  exit 0. CONFIRMED.
- python3 --check-hash-based-pycs=always --version -> "unknown option
  --check-hash-based-pycs=always", exit 2. CONFIRMED (the = form is
  correctly recorded as a fail-closed over-approximation, not an
  execution).

## 3. My own extra probe: 46/46 PASS

File: /tmp/y14b-fix4-c2-probe.py (34 unit cases + 12 live checks, none
in the fix4 probe). Result: 46 PASS lines, exit 0, FAILURES: 0, no
stray processes left (ps checked after). Live checks use a new shebang
stub /tmp/y14b-c2-dummies/run_shebang.py (sleep 60) plus the shared
codex stub. Cases that assert CURRENT behavior on a miss or false
positive are labelled MISS / FP in the probe; passing means the
behavior is reproduced, not that it is correct. The findings below
come from those cases.

Unit cases (all via _is_runner_cmdline / _is_codex_executor /
_is_cmd_separator on synthetic NUL-joined argv, unless noted):

- Separator edges: "a|b" False (lone | in a token left alone, per
  docstring); "|" True; "&&" True; "a;b" True; "a||b" True; "a&&b"
  True; "&" False (single & is not a separator, see C2-2).
- _c_is_shell wrappers: nested bash -c (quoted and unquoted) False
  (documented F8 non-residual, leaf caught live, see INFO-3);
  env bash -c False, nice bash -c False, sudo bash -c False
  (synthetic argv only, see INFO-2); flock -c True.
- Moved -m branch: pytest -m run_batch3 False; echo -m run_batch3
  False; node -m run_batch3 False; python3 -m run_tests True
  (prefix rule control); python3 -m foo.run_tests False.
- Guarded import branch: python3 -c "import run_batch3" True;
  python3 -c "from run_batch3 import main" True; echo import
  run_batch3 False; ruby -c "import run_batch3" False; bash -c
  "python3 -c 'run_foo.py'" False.
- Extensionless barrier: python3 run_tests -W ignore run_batch3.py
  False; python3 run_tests.py -W ignore run_batch3.py True (via
  run_tests.py itself); python3 myrun_script -W ignore run_batch3.py
  True; vim run_batch3.py False (mention only).
- Glued separator on the runner token: bash -c "python3 run_foo.py;
  echo done" False; bash -c "run_foo.py; echo done" False (C2-1);
  bash -c "python3 -m run_batch3; echo done" True (asymmetry).
- Codex -c include-everything: bash -c "codex -c 'import time; x #
  foo'; echo marionette" True (documented fail-closed, marker in a
  LATER shell command counts); bash -c "codex -c 'import time; x #
  marionette'" True (F2 fix holds); bash -c "codex --help&&echo
  marionette" False (F7 holds); bash -c "codex --help & echo
  marionette" True (C2-2).

Live checks (all passed): env bash -c caught (True, env exec-replaces
itself, the surviving process IS bash -c) with its leaf python3 stub
caught; flock -c wrapper caught; python3 -c 'run_foo.py' NameError
exit 1; single & echo runs while codex still sleeps (stdout contains
marionette, timeout exit 124); glued ; wrapper missed (False) with its
leaf caught; double-nested bash -c wrapper missed (False) with its
leaf caught.

## 4. Findings

### C2-1 (LOW, miss, wrapper-level): a glued separator on the runner token misses

- Evidence, run_batch3.py lines 2456-2468 (basename block) and
  2312-2320 (_is_cmd_separator):
  `bash -c "python3 run_foo.py; echo done"` returns False;
  `bash -c "python3 run_foo.py&&echo done"` returns False;
  `bash -c "python3 run_foo.py||echo done"` returns False;
  `bash -c "run_foo.py; echo done"` returns False.
  Mechanism: _argv_tokens splits the -c string on whitespace, so the
  script token arrives as "run_foo.py;" (or "run_foo.py&&echo"),
  and _script_basename_is_runner requires endswith(".py"), which the
  glued token fails. Fix pass 4 split glued separators in
  _same_command_tokens (codex side, F7) but not in the runner
  basename block.
- Asymmetry that proves the gap is local: the -m branch tolerates the
  same glue, `bash -c "python3 -m run_batch3; echo done"` returns
  True, because _is_runner_module (lines 2513-2530) only needs
  startswith("run_").
- Impact bounded, hence LOW not MEDIUM: the leaf process is always
  caught live. My live check L5: bash -c "/tmp/y14b-c2-dummies/
  run_shebang.py; sleep 60" wrapper False, leaf python3 process True.
  No fleet launcher runs the runner with a trailing command in the
  same -c string, so this is a wrapper-level gap in the same class as
  F2, not a full miss like R1.
- Fix sketch for pass 5: in the basename block, compare
  base.rstrip(";,()") (mirroring the import branch, lines 2489-2492,
  which already rstrips) instead of raw base, or strip trailing
  separators inside _script_basename_is_runner, which is used only at
  line 2456, so the change is local. Add the four glued forms above to
  the fix probe.

### C2-2 (LOW, false positive, fail-closed): a bare & is not a command separator

- Evidence, run_batch3.py lines 2312-2320:
  _is_cmd_separator("&") is False, and "&" in tok is not checked.
  Two consequences, both reproduced:
  (a) Runner side (F4 analogue): `python3 --version & pytest -W
  ignore run_batch3.py` returns True. _python_executes walks back
  past the & to the python3 of the first command, finds no barrier,
  and the -W two-back rule fires.
  (b) Codex side: `bash -c "codex --help & echo marionette"` returns
  True. _same_command_tokens does not stop at &, so the marker in the
  later foreground command counts. Live check L4 proves the
  semantics: with the codex stub on PATH, `codex --help & echo
  marionette; wait` prints marionette while codex still sleeps
  (timeout exit 124), so marionette is a later command, not a codex
  marker.
- Impact: fail-closed (a refusal that should not happen), LOW. No
  fleet launcher backgrounds a command with & before naming a runner
  or a marker. A spurious refusal is the safe direction for a launch
  gate, but it is a real false positive in the same class fix pass 4
  closed for ; / && / ||.
- Fix sketch for pass 5: add bare "&" to the separator tuple in
  _is_cmd_separator (tok == "&" only, NOT "&" in tok, so a URL token
  such as "?a=1&b=2" is not split and its later part is not dropped,
  which would be fail-open). Re-check the F7/F4 cases after the
  change; _is_cmd_separator is used at lines 2330, 2352, 2575, 2620
  and 2634, all of which want "a bare & starts a new command".

### INFO-1: ; inside a token splits, | inside a token does not

_is_cmd_separator("a;b") is True while _is_cmd_separator("a|b") is
False. The docstring exempts a lone | inside a token because it is
more often a regex literal, but the same argument applies to ; in a
regex, and F7 forces the ; choice (a glued ";" must split). At token
level the two cannot be told apart. No action; recorded so the
asymmetry is a deliberate choice, not an oversight.

### INFO-2: synthetic env / nice / sudo -c argv do not occur live as written

Unit cases say `env bash -c "run_foo.py"`, `nice bash -c "run_foo.py"`
and `sudo bash -c "run_foo.py"` all return False, but live they
behave differently, and I verified each:
- env and nice exec-replace themselves, so /proc never shows an env
  or nice token: `env bash -c "<stub> & sleep 60"` survives as
  `bash -c "<stub> & sleep 60"` (pid 197924) and returns True, as
  does nice (pid 197933). Not a live miss.
- sudo forks and waits, so the sudo parent (pid 197937, cmdline
  `sudo -n bash -c ...`) returns False, but its bash child (pid
  197938) returns True. The child is always present while the runner
  runs, so the parent-only miss has no live effect.
No action. The unit cases stay in my probe as helper-behavior
documentation, not as live findings.

### INFO-3: double-nested -c wrapper miss is the documented F8 position, leaf verified

`bash -c "bash -c 'run_foo.py'"` returns False (two mechanisms: the
quoted token "'run_foo.py'" fails the run_ prefix test, and in the
unquoted form the outer -c trips the any(-c) guard in the -c branch,
lines 2465-2471). The file docstring already records double-nested -c
quoting as NOT a residual because the leaf python process is caught
live. I verified the leaf claim live (L6): the double-nested wrapper
is False, its descendant python3 stub process is True. No action.

### INFO-4 (process): gate-dry is concurrency-sensitive on the shared VM

See section 1. Two of my three gate-dry runs failed only because a
concurrent Council 3 worker had live dummy runners in /proc. The
clean 4/4 came after that worker finished. Recommendation: before any
/proc-scan probe (gate-dry, fix probes with live dummies), check ps
for foreign run_foo / codex dummies, and do not run two live-probe
workers at once. This is a process note, not a code finding.

## 5. Items checked and confirmed (no finding)

- R1: -m .py forms execute live (exit 124, three variants) and the
  gate now catches them; _is_runner_module strips trailing .py.
- F1: python3 -crun_foo.py is a NameError, exit 1, and the gate no
  longer flags the -c branch for it (_c_is_shell).
- F2: codex -c snippet marker caught (True), including the ; inside
  the snippet.
- F3: pytest -m, echo -m, echo import all False now; import branch
  requires a python -c.
- F4: _python_executes stops at shell separators (fix3 probe 70/70
  re-passes, including its ; case).
- F5: extensionless run_* is a script barrier (python3 run_tests -W
  ignore run_batch3.py False, with the run_tests.py / myrun_script
  controls True).
- F6: python3 -c "codex marionette" no longer flags (fix4 probe
  re-passes; my ruby -c import control also False).
- F7: glued ; / && / || split in _same_command_tokens (codex
  --help;echo and --help&&echo both False).
- F8: sudo restored to the recorded codex gaps (line 2567: "nice and
  sudo wrappers each need their own argument parser").
- F9: fix3 probe is 70 checks (re-run: 70 PASS lines); the joined
  --check-hash-based-pycs=always form is rejected by CPython, exit 2,
  and is documented as a fail-closed over-approximation.
- F10: plan H4 wording corrected (lines 643-646: Council 1 counts 3,
  under by half a round trip; Council 3 counts 4, over by half). The
  one remaining "bracket" hit in the plan (line 754) is inside the
  fix-pass-4 record bullet saying the phrasing was removed, not in
  the H4 text itself.

## 6. Hygiene

- py_compile: python3 -m py_compile tests/realistic/run_batch3.py
  prints py_compile_OK.
- Em/en dash: git show bf3c939 over all three changed files has 0
  em dash (U+2014) and 0 en dash (U+2013) characters.
- Personal info: no real names, emails, addresses or phone numbers
  in the changed lines (the only @ match in the diff output is the
  git commit author header and the commit message text itself, not
  file content). No ydotool anywhere in the diff.
- No live Zen driving by this reviewer; all live checks used dummy
  stubs under /tmp. Every stub process spawned by my probe was
  killed, and a final ps shows no run_shebang / codex --help
  processes remaining. (Two orphans from my own early cleanup runs,
  pids 196663 and 197939, were found by ps and killed by hand; the
  final probe kills descendants recursively.)

## 7. What fix pass 5 should do (AMEND items only)

1. C2-1: strip trailing separators from the runner basename before
   matching (base.rstrip(";,()") in the basename block, or inside
   _script_basename_is_runner). Regression: the four glued forms in
   section 3 must flip to True, with the leaf and the -m control
   unchanged.
2. C2-2: treat a bare "&" token as a command separator in
   _is_cmd_separator (bare token only). Regression: `python3
   --version & pytest -W ignore run_batch3.py` and `codex --help &
   echo marionette` must flip to False, with the F4/F7 cases and the
   URL-token behavior unchanged.
3. Process: note in the restage log that gate-dry and the live probes
   must not run concurrently with another worker's live probes on
   the shared VM.
