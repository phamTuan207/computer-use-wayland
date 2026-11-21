# Council Voice 2: Y14b re-stage review, H2 fix + launch gate / preflight only

- Scope: commit f732d6a on todolist-push (Y14b: re-stage batch3 runner from
  suite HEAD 1d23532 + H2 tokenizer fix). Reviewed ONLY the H2 fix and the
  launch-gate / preflight integration in tests/realistic/run_batch3.py.
  The run_b3_t10 rewrite and all other re-stage changes are out of scope
  for this paper.
- Verdict: AMEND. The core is correct and verified live (see evidence),
  but there is one real, reproducible hole in the tokenizer (Fix 1) plus
  one stale comment (Fix 2). Apply both, re-run the probes, then GO.
  No BLOCK: nothing found breaks the gate for any launch form in current use.
- Reviewer: Council Voice 2 (independent review, no subagents spawned).
- Timing (Asia/Ho_Chi_Minh): start 21:13:27. AST identity diff 21:13.
  Y14b H2 probe re-run 21:14, exit 0. Y14b gate dry run 21:14, exit 0.
  Council-2 probe v1 21:15, exit 0 (later found vacuous on B1/B2, see
  method note). Council-2 probe v2 (fixed) 21:16, exit 0. Paper written
  21:17-21:19, committed same evening.

## 1. Identity vs Y13f (check 1): PASS, with one record-keeping caveat

Method: AST-level comparison (ast.get_source_segment per function) of
run_batch3.py at f732d6a (= HEAD for this file; a46d503 touched only the
log) against the working-tree tests/realistic/run_codex_y5.py (Y13f).

- _script_basename_is_runner: identical to Y13f.
- _is_python_token: identical to Y13f.
- _argv_tokens: identical to Y13f.
- _ppid_of: identical to Y13f.
- CODEX_REFUSE_MARKERS: identical to Y13f.
- _is_runner_cmdline: LOGIC identical to Y13f. The only diff is the
  docstring tail: Y13f says "Keep in sync with launch_y13.py (identical
  logic) and with the note in the plan: Y14's run_batch3.py carries the
  same old pattern and must apply this same fix when it re-stages";
  Y14b says "Keep in sync with launch_y13.py and run_codex_y5.py
  (identical logic). This copy IS the Y14 application of the fix (Y14b
  re-stage from suite HEAD 1d23532)". No behavioral difference.
- Cross-check vs launch_y13.py: _argv_tokens logic identical
  (docstring-only diff); _ppid_of logic equivalent (bytes read vs text
  read, same rfind(")") + 2 parse); CODEX_REFUSE_MARKERS and
  _is_python_token identical. The "identical logic" claim holds across
  all three copies.

Caveat (recorded, not a finding against Y14b): Y13f's code is UNCOMMITTED
working-tree code at review time (git status shows
M tests/realistic/run_codex_y5.py, 412 insertions vs HEAD). This identity
claim is therefore against the working tree as it stood 21:13-21:17 on
21/11, not against a commit. If Y13f lands with different helper code,
re-diff before treating the copies as in sync.

## 2. Tokenizer coverage (check 2): PASS for all in-use forms, one hole

Y14b's probe /tmp/y14b-h2-probe.py re-run by me, exit 0, 21/21 as
claimed (14 unit + 7 live): bare-relative, absolute path, flock -c,
shell -c, md5sum/cat mere mentions, -c code path arg, python -u,
run-nested bare-relative, run-nested .sh after bash, pytest file mention,
shebang argv[0], plain sleep, plain codex. Live: bare-relative, flock -c
and shell -c dummies caught; mention-only process not caught; hit set
exactly the dummies plus their wrappers; old pgrep -f false-positived
on the mention process (confirming the old defect).

My own probe /tmp/y14b-c2-probe.py (v2), exit 0, all asserted cases pass.
Additional unit cases verified True: bash -c "exec python3 ...",
env python3, python3.11, /usr/bin/python3.11, sh -c python3,
/usr/bin/env python3, ./run_batch3.py, absolute argv0 shebang,
flock exec form without -c, python3 -m run_batch3.py (flag branch).
Verified False (correct): python3 -m pytest run_batch3.py, vim
run_batch3.py, grep -rn run_batch3.py, plain codex with no marker.
Verified True (correct) for the codex rule predicate: codex + marionette,
codex + .config/zen path, codex + geckodriver.

Recorded misses (all inherited from Y13f, same code, not Y14b-introduced):

- (a) python3 -m run_batch3 returns False. The token "run_batch3" has
  no .py suffix, so _script_basename_is_runner rejects it. Same for
  python3 -u -m run_batch3. This is Fix 1 below. Note the -m handling
  that DOES work: python3 -m run_batch3.py returns True via the flag
  branch, but that is not valid Python (module names have no .py);
  the real module form is the one that misses.
- (b) Double-nested quoting: flock -c "bash -c 'python3 run_foo.py'"
  returns False. _argv_tokens splits only one -c level, and the inner
  token comes out as "'python3" (quote-prefixed), which fails
  _is_python_token. No plan or log uses double nesting; recorded as a
  known residual limitation, not a required fix.
- (c) runpy.run_path('run_batch3.py') inside python3 -c returns False.
  Exotic, not a launch form; recorded only.

## 3. Ancestry exclusion (check 3): PASS, proven live (and one self-correction)

Y14b's probe check "live ancestry (parent shell) NOT flagged" is vacuous:
it checks os.getppid() of the probe, whose cmdline never names a runner.
I first made the same mistake in my v1 probe (self-scanning script named
selfscan.py; its basename is not a runner token, so the ancestors could
not have matched anyway; I proved this: _is_runner_cmdline on the v1
bash -c ancestor cmdline returns False).

V2 fixed it: the self-scanning script is named run_selfscan.py, a runner
name. Non-vacuity proven mechanically first: _is_runner_cmdline returns
True for the real bash -c, flock, and /bin/sh ancestor cmdlines naming
run_selfscan.py. Then live, from INSIDE the runner:

- B1, bash -c "python3 run_selfscan.py": ancestry chain
  [self, bash, probe, probe-parent, 742, 0], HITS [] on all 8 scans.
- B2, flock lock -c "python3 run_selfscan.py": chain
  [self, sh, flock, probe, probe-parent, 742, 0], HITS [] on all 12 scans.
- C, sibling control: with an unrelated "python3 run_foo.py" dummy live,
  the same self-scanner reports exactly [(sibling-pid,
  'python3 run_foo.py')] on every scan. The exclusion does not
  over-exclude.

_ppid_of walk reviewed: loop "while pid > 1", breaks on ppid None or
ppid already in own (cycle guard). The rfind(")") parse handles comm
fields with spaces (C3 F7). One observation, harmless: the chain ends
in 0 (_ppid_of(742) returned 0). Pid 0 never appears as a /proc entry,
so no process can be wrongly excluded by it, and no live test showed
over-exclusion. I did not determine whether 742 genuinely has ppid 0
(pid-namespace root) or this is a parse edge; it does not affect the
verdict.

## 4. Codex-refuse rule (check 4): PASS

CODEX_REFUSE_MARKERS is AST-identical to Y13f's tuple. The scan
predicate ("codex" in cmd.lower() and any marker in cmd.lower()) matches
Y13f's preflight inline block exactly, including the plain-codex
warning-only behavior (plain codex returns no hit). Difference in form
only: Y13f raises RuntimeError on the first hit inside preflight, Y14b
collects hits and launch_gate() prints all of them and returns False,
while run_preflight() raises on the first hit. Same fail-closed outcome.
Minor polish (optional, not required): launch_gate() prints codex hits
under the same "runner process live" line, so the message does not say
which rule fired; the pid and full cmdline are printed, so it stays
diagnosable.

## 5. launch_gate order and preflight re-check (check 5): PASS

launch_gate() (run_batch3.py:2319) order, read from the f732d6a source
and exercised by the dry run:

1. LIVE_SLOT_OK=1, else refuse. 2. pgrep -x zen-bin, refuse on exception
   or empty output. 3. Marionette 2828 TCP connect, refuse on failure.
4. Ports 8771/4452 bind-free, refuse on failure. 5. Predecessor ports
   8767-8770/4448-4451 bind-free, refuse on failure. 6. LIVE_SERVER_ROOT
   holds clone1-batch3/t01-terminal/fixture.html, refuse otherwise.
7. pgrep -x geckodriver, refuse if any. 8. _scan_other_runners(), refuse
   on any hit. Every step returns False on failure; no step falls
   through.

Order note that matters: the geckodriver check swallows a pgrep exception
into "" (fail-open in isolation), but the zen-bin check before it returns
False on any pgrep exception, so a broken pgrep refuses at step 2
before the geckodriver check is reached. Correct as written.

Preflight re-check (run_batch3.py:1929-1933): the scan loop is the first
statement of run_preflight(), before open_test() at line 1934, and it
raises RuntimeError("PREFLIGHT FAIL: live slot busy, runner process
running: ..."). main() calls launch_gate() before start_server(), runs
preflight in its own WD session, and returns 1 before t01 on any
preflight failure. WD.__enter__ (run_live.py:461) only starts
geckodriver and POSTs a session; it opens no tab, so "before any tab
opens" holds literally: the first tab this runner opens is the preflight
probe tab, after the re-check. A runner starting between the gate and
the preflight is therefore caught before any tab opens.

Gate dry run /tmp/y14b-gate-dry.py re-run by me, exit 0, 4/4 as claimed:
A quiet slot passes; B bare-relative dummy refuses (and the log shows
the flock wrapper, sh wrapper and python dummy all listed as hits);
C mention-only process passes; D missing LIVE_SLOT_OK refuses. The dry
run fakes zen/marionette/ports, so the real laptop zen/2828 checks were
not re-proven here; that code is unchanged from the pre-existing gate
(the diff replaces only the sweep), so this is a low residual risk,
recorded for honesty.

## 6. pgrep -f leftovers (check 6): PASS, one stale comment

grep over run_batch3.py: 4 pgrep occurrences, all "pgrep", "-x"
(zen-bin at 2333, geckodriver at 2389, plus two in comments). No
"pgrep -f" and no "pkill -f" use remains. The old six-pattern pgrep -f
sweep is gone. Fix 2 is the stale comment at line 2364, which still
says "another port would also trip the pgrep sweep below"; the sweep
below is now the /proc tokenizer scan.

## Fixes required (AMEND)

Fix 1 (required, substantive). File tests/realistic/run_batch3.py,
function _is_runner_cmdline (def at line 2220), inside the token loop
after the "prev == -c" branch at lines 2247-2248. Add a module-form
branch:

    if prev == "-m" and (base.startswith("run_")
                         or base == "hand_drive_e1"):
        return True

Rationale: this accepts "python3 -m run_batch3" and
"python3 -u -m run_batch3" (the -u case reaches here because prev is
"-m", not "-u") while still rejecting "python3 -m pytest
run_batch3.py" (prev is "pytest", not "-m") and "python3 -m pytest"
alone (no runner token at all). The same fix should be applied to the
sibling copies in run_codex_y5.py and launch_y13.py, or the docstring
claim "identical logic" becomes false; Y14b owns the run_batch3.py
copy, and should flag the other two copies to their owners.
Verification: add probe cases "python3 -m run_batch3" -> True,
"python3 -u -m run_batch3" -> True, "python3 -m hand_drive_e1" ->
True, keep "python3 -m pytest run_batch3.py" -> False, re-run
/tmp/y14b-h2-probe.py (expect 21/21 plus the new cases) and
/tmp/y14b-gate-dry.py (expect 4/4), plus a live -m dummy through
_scan_other_runners.

Fix 2 (required, cosmetic). File tests/realistic/run_batch3.py, line
2364. Change "another port would also trip the pgrep sweep below, but
the port check fails closed directly" to "another port would also trip
the /proc tokenizer scan below, but the port check fails closed
directly".

## Dissent and uncertainty, stated plainly

- I disagree with Y14b's log claim only in one respect: its probe did
  not actually test the ancestry exclusion (see section 3); the
  exclusion itself is correct, as my v2 probe proves, but the 21/21
  headline should not be read as covering it.
- The -m module-form hole is inherited from Y13f, not introduced by
  Y14b, and no launcher in the repo uses -m today (grep for
  "python3 -m run_" across coord/, improvements/ and tests/realistic/
  returns nothing; the runner usage line is script form). I still call
  it AMEND rather than GO because -m is an idiomatic launch form, the
  brief's check 2 names "-m flags" explicitly, a "python3 -m
  run_batch3" runner would bypass the single-runner guard entirely,
  and the fix is four lines plus probe cases.
- Double-nested -c quoting and runpy -c remain missed after Fix 1.
  I judge them acceptable residual limitations (no launcher uses them;
  fixing nested quoting would mean recursive -c splitting with quote
  handling, disproportionate to the risk). They should be recorded in
  the _is_runner_cmdline docstring so the next reviewer does not
  re-discover them as surprises.
- Out of scope, noted only: Y14b's runner has no flock-holder check
  and no geckodriver PID-file sweep of the kind Y13f's preflight has;
  that is pre-existing Y14 design (the queue is coordinated by Muse),
  not something this re-stage changed, so it does not affect this
  verdict.
- No live laptop run was done by this reviewer (VM only, faked
  zen/marionette/ports in the dry run). The gate order and the
  preflight placement are verified from source and from the dry run;
  the real zen/2828 path is unchanged old code.
