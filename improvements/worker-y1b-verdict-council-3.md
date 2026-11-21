# Verdict Council 3: OVERALL Phase A, Worker Y1b fix commit 84b88bb

Date: 2026-11-21. Author: Verdict Council 3 (overall Phase A judge for Worker Y1b).
Scope: all of Phase A, executor hardening items 1-4 from the redteam BLOCK
report (improvements/worker-y1-redteam.md, 7 attacks, 6 HIGH, 12 must-fix
items; Phase A covers the executor half, items 1-4).
Evidence base: Y1b verification run (worktree /tmp/y1b-verify, commit
84b88bb, "fix: harden code execution envelopes"), probe spec
improvements/worker-y1b-verify-council-1.md, probe runner
/tmp/y1b-probes-c1.py, the code diff (git show 84b88bb), and this
council's own independent re-runs of the full probe suite and the unit
tests against the same checkout. This council also adopts the item 1
and item 2 findings of Verdict Council 1
(improvements/worker-y1b-verdict-council-1.md), which it checked against
its own re-run, and judges items 3 and 4 itself.

No em dash or en dash in this file, per standing rule.

## Method and independent confirmation

This council re-ran /tmp/y1b-probes-c1.py twice against /tmp/y1b-verify
and reproduced Y1b's result exactly in kind and in count: 14/20 PASS,
with the same six FAILs (1e, 2a, 2b, 2e, 4a, 4b). Timings vary run to
run (2a elapsed 7.20s here, 5.26s for Y1b, 6.70s for Council 1; 2b
elapsed 6.20s here, 5.31s for Y1b, 9.63s for Council 1), but every run
is above the 4.0s PASS ceiling and the failure modes are identical, so
the variance changes nothing. This council also re-ran Codex's own
tests on the worktree: python3 -m unittest tests.test_codemode
tests.test_code_exec reports Ran 81 tests, OK. The full-suite count on
the worktree is still running and is NOT claimed here; Y1b confirms
that count separately (baseline on the VM was 1,483 tests, 0 failures,
2 errors from VM toolchain gaps; Codex claims 1530 tests, OK, 2 skipped
on the laptop).

## Verdict rule as written: BLOCK

The probe spec's rule: all probes 1a-1f, 2a-2d, 3a-3f, 4a-4c must PASS.
Probe 2e is the single exception (residual risk, recorded not hidden).
Any other FAIL blocks Phase A.

Applied mechanically, the rule gives BLOCK: five non-excepted probes
fail (1e, 2a, 2b, 4a, 4b). But the mechanical count overstates the
real state of the code, because two of the five fails are probe
artifacts, not code gaps. The verdict is still BLOCK, for the right
reasons: three of the fails (1e, 2a, 2b) are real gaps in the code.
The reclassification below matters because it changes what Codex must
fix (three real fixes, not five) and what Y1b must fix (two probe
amendments, not two code fixes). A BLOCK that demands fixing 4a as
written would demand the impossible; see the item 4 reasoning.

## Scoreboard

| Probe | Result | Evidence |
| 1a codemode class leak | PASS | status error, no class string in envelope |
| 1b codemode globals leak | PASS | status error, repo root path absent |
| 1c code_exec session-token leak | PASS | ok False, error_type sandbox, token absent from envelope JSON |
| 1d code_exec session dict dump | PASS | ok False, error_type sandbox, no session_token, dom_snapshots, or check_cancel in envelope |
| 1e negative controls | FAIL, real gap | codemode f-string `f"{len(chr(65))}"` errors `NameError: name 'chr' is not defined`; code_exec f-string fails the same way; both `%` halves pass (`ok-1`) |
| 1f static guard | PASS | `format` absent from SAFE_ATTRIBUTE_NAMES in both files |
| 2a codemode wall preemption | FAIL, real gap | elapsed 7.20s (Y1b 5.26s, Council 1 6.70s), status error "wall-clock budget exceeded" raised only AFTER the C loop finished; probe needs elapsed at most 4.0s |
| 2b code_exec wall preemption | FAIL, real gap | elapsed 6.20s (Y1b 5.31s, Council 1 9.63s), ok=True with NO error, silent success; probe needs elapsed at most 4.0s and ok False |
| 2c codemode 50MB result cap | PASS | status error, result_too_large, envelope 189 bytes |
| 2d code_exec 50MB result cap | PASS | ok False, result_too_large, envelope within cap |
| 2e memory, 100MB allocation | FAIL, allowed exception | elapsed 0.06s, status completed; recorded as residual risk per the verdict rule, not a blocker on its own |
| 3a wrapper reference | PASS | status error, dunder access is banned |
| 3b wrapper self-call | PASS | status error, dunder access is banned, no RecursionError |
| 3c wrapper double-exec | PASS | status error from the scan, body never runs |
| 3d yield, codemode | PASS | status error, yield in error text |
| 3e yield, code_exec parity | PASS | ok False, error_type sandbox, yield in error |
| 3f async parity | PASS | status error (rejection via AsyncFunctionDef/AsyncFor path) |
| 4a builtins pin, behavioral | FAIL, probe artifact | status error, leaked list reads `__builtins__ is a module, not a pinned dict: None`; see item 4 reasoning |
| 4b builtins pin, codemode static | FAIL, probe artifact | pin line present at scripts/codemode.py line 278, but in assignment form with double quotes; probe string wants dict-literal single quotes; see item 4 reasoning |
| 4c builtins pin, code_exec static | PASS | pin line present in code_exec.py run() |

Total: 14/20 PASS. Real blocking fails: 3 (1e, 2a, 2b). Probe artifacts: 2 (4a, 4b). Allowed exception: 1 (2e).

## Item 1: str.format defeats the dunder ban. PARTIAL

Adopted from Verdict Council 1, confirmed by this council's re-run.
The attack is dead: all four leak paths (1a-1d) are rejected at scan
time and the whitelist entry is gone in both executors (1f). The 1e
failure is real and is a regression, not an artifact. Commit 84b88bb
pins `namespace["__builtins__"] = dict(SAFE_BUILTINS)` in codemode
(the item 4 fix), and `chr` is in neither SAFE_BUILTINS list, so the
pin removed `chr` from codemode scope where it previously resolved
through the real builtins module CPython inserted. The code_exec half
is pre-existing (chr was never in code_exec SAFE_BUILTINS), but probe
1e requires all four halves to pass. `chr` is safe to add: it is a
pure function, int to one-character string, no attribute access, no
I/O, no evaluation, and it cannot reach any dunder. P1-P4 use no
builtin outside SAFE_BUILTINS and are unaffected by the pin. Follow-up
is a one-line addition per file, not a rework. PARTIAL, not FIXED,
because the gate rule requires 1a-1f all PASS.

## Item 2: wall-clock and result budgets do not bind C-level work. BLOCKED

Adopted from Verdict Council 1, confirmed by this council's re-run.
The result-cap half is genuinely fixed (2c, 2d). The wall-preemption
half is entirely absent: no signal.setitimer, no SIGALRM handler, no
child process, no timeout kill anywhere in commit 84b88bb; grep for
setitimer, SIGALRM, RLIMIT, subprocess, and multiprocessing in both
executors finds no preemption mechanism. The probe spec closes every
candidate reading in advance: a late error is still FAIL (2a), silent
success is worse than a late error (2b, ok=True after 6.20s with the
correct sum and no error), and documenting the budget as post-hoc only
is explicitly ruled out. This is a hard BLOCK, not a partial: the
mechanism does not exist. Probe 2e stays the allowed exception: a
100MB allocation completes in 0.06s because the envelope cap bounds
only what leaves the executor, not intermediate allocations. It is
recorded here as residual risk, not hidden, and it is closed
automatically if the preemption fix uses a child process with an
RLIMIT_AS cap; it stays open as documented residual risk if the fix
uses a signal timer only.

## Item 3: codemode wrapper function is reachable, callable, and re-runs the program. FIXED

All six probes pass on this council's re-run. The wrapper is gone:
commit 84b88bb executes model code at module level through
`_module_code` (the final `return` is rewritten to an assignment to
`result`), so there is no `__codemode_main__` to reach. The scan now
rejects any Name starting with `__` ("dunder access is banned") and
rejects Yield, YieldFrom, AsyncFor, and AsyncWith. Probes 3a-3c all
fail at scan time before any execution, 3d rejects the yield program,
and 3e/3f confirm code_exec parity and async parity. No follow-up is
needed for item 3 beyond re-running 3a-3f after the item 1, 2, and 4
follow-ups to confirm no regression.

## Item 4: codemode does not pin __builtins__. FIX IS IN, PROBES NEED AMENDMENT

### The pin is present and behaviorally effective

The pin line exists in codemode at scripts/codemode.py line 278:
`namespace["__builtins__"] = dict(SAFE_BUILTINS)`. This council
verified the behavior directly, outside the 4a probe mechanism:
executing `eval("1+1")`, `open("README.md")`, `__import__("os")`,
`compile(...)`, `getattr(1, "x")`, and `globals()` inside codemode
execute_op all return status error with "banned name: ..." in each
case. Executed code cannot reach the real builtins through the pinned
namespace. That is what the redteam fix (checklist item 2, a one-line
pin) was specified to do, and it does it.

### Probe 4b is a probe-string artifact

Probe 4b asserts the exact string `'__builtins__':
dict(SAFE_BUILTINS)` (dict-literal form, single quotes) appears in
scripts/codemode.py. The code has the same semantic pin in assignment
form with double quotes, because codemode builds its namespace
incrementally (`namespace = dict(SAFE_BUILTINS)` then the pin line),
while code_exec builds a dict literal inside run(). Demanding the
dict-literal string in codemode is demanding a formatting choice, not
a security property. The pin is present; the probe string is wrong.
Amend the probe to accept either form (or to check the namespace at
runtime). No code change is needed for 4b.

### Probe 4a is mis-specified in two independent ways

First, its mechanism is defeated by the new envelope cap (the 2c/2d
fix). Probe 4a returns the live op function `repo_list_scripts` from
execute_op and inspects `fn.__globals__` in the harness. A function
object is not JSON-serializable, so `_serialized_size` returns
MAX_ENVELOPE_BYTES + 1 on the TypeError and `_bounded_envelope`
replaces the envelope with a result_too_large error. This council's
re-run shows status error and `env["result"]` is None, so the probe
reports `__builtins__ is a module, not a pinned dict: None`. The probe
can never observe a completed status for a function result on this
commit, whatever the pin does.

Second, its expectation is unachievable by the specified fix even if
the mechanism worked. Op functions are module-level functions defined
in codemode.py, so `fn.__globals__` IS the codemode module dict, which
must carry the real builtins for the module's own code to run. The
one-line namespace pin changes only the globals dict handed to exec
for the model program; it can never change an op function's own
`__globals__`. Making 4a pass literally would require rebinding every
op function with restricted globals (types.FunctionType with a pinned
globals dict), which would break op functions that read module globals
(`repo_list_scripts` reads REPO_ROOT) and is a far bigger change than
the redteam item the probe is meant to verify. A BLOCK that demands
4a as written would demand work the redteam never specified, to test
a property the specified fix cannot produce.

### The residual risk 4a gestures at is real, and is recorded here

Op function `__globals__` still hold the real builtins, including
eval, open, `__import__`, and compile. There is no live path to them
today: dunder Names and dunder attributes are banned (3a-3c pass) and
`format` is gone from both whitelists (1a-1d, 1f pass), so model code
cannot obtain a live function object and then traverse its globals.
But the second hop the pin was meant to close still exists one
abstraction away: any future hole that yields a live function object
plus any dunder-access path hands over full builtins. That is why the
replacement probe below tests the property that matters (executed code
cannot use real builtins), and why every future allowlist or
dunder-adjacent change must be treated as a security change and
re-checked with the format-hole and dunder probes in the redteam
report. This residual is documented, not hidden, and it does not
block Phase A on its own, because no live exploit path exists on this
commit.

### Replacement probes for 4a and 4b (Y1b to implement before the re-verification run)

- 4a prime (behavioral, executed-code builtins denial): for each of
  eval, open, `__import__`, compile, getattr, input, globals, locals,
  run execute_op with a program naming it and require status error
  with "banned name" in the error. This council ran this exact check
  by hand on commit 84b88bb and all six tested names error as banned.
  4a prime PASSES on this commit.
- 4b prime (static, form-agnostic): require that the codemode source
  contains a `__builtins__` pin assigning `dict(SAFE_BUILTINS)`,
  accepting either the dict-literal form or the assignment form, and
  require that the pin sits in execute_op's namespace construction.
  4b prime PASSES on this commit.

## Question 1: rule as written, and the reclassification argument

Under the rule as written, Phase A is BLOCK: five non-excepted probes
fail. The outcome is right but the count is wrong. The honest count
is three real blocking fails (1e, 2a, 2b), two probe artifacts (4a,
4b), and one allowed exception (2e). Reclassifying 4a and 4b does not
change the verdict, because 1e, 2a, and 2b each independently block
Phase A under the rule, and no reading of the probe spec passes them.
It does change the work: Codex fixes three real gaps, and Y1b amends
two probe strings, instead of Codex being sent to chase a 4a that the
specified fix cannot deliver. If 1e, 2a, and 2b were fixed and only 4a
and 4b still failed as written, this council would call that PASS
with probe amendments, not BLOCK, because the code would then satisfy
every security property the redteam specified.

## Question 2: minimal follow-up work to unblock Phase A, in order

Must-fix before merge (each with its acceptance probe):

1. Add `chr` to SAFE_BUILTINS in both files. scripts/codemode.py
   line 38-46 and scripts/code_exec.py line 108-116: add `"chr": chr`
   and `'chr': chr` respectively. Optionally add `ord` alongside it
   (chr's exact inverse, equally pure), but do not widen SAFE_BUILTINS
   beyond chr (and optionally ord) without a failing probe or a named
   snippet that needs the addition. Do not add `repr` (it invokes
   `__repr__` on live objects) or `format` as a builtin. Acceptance:
   probe 1e passes all four halves (f-string results "1", `%`
   results "ok-1", in both executors), and probes 1a-1d and 1f still
   pass. (Adopted from Verdict Council 1.)
2. Add real wall-clock preemption in BOTH executors
   (codemode execute_op and code_exec CodeExecSession.run). Option A,
   minimal: signal.setitimer(ITIMER_REAL, wall_seconds) armed
   immediately before exec, SIGALRM handler raising inside the
   snippet, disarmed in a finally block; it works only on the main
   thread, so off the main thread the run must refuse up front or fall
   back to Option B, never run unbounded and silent the way 2b does
   today. Option B, robust and preferred: execute the snippet in a
   child process with a hard timeout and kill on expiry, returning a
   wall-clock error envelope; with an RLIMIT_AS cap this also closes
   probe 2e. A literal-only static refusal (rejecting only
   `range(3 * 10**8)`) is a probe bypass, not a fix; any static
   refusal must generalize. Acceptance: probes 2a and 2b pass
   (elapsed at most 4.0s each, wall-clock error or general upfront
   refusal, in both executors), probes 2c and 2d still pass, probe 2e
   is re-run and recorded (must PASS under Option B; under Option A a
   FAIL is recorded as residual risk). Two consecutive passing runs
   are better than one, given the timing variance seen. (Adopted from
   Verdict Council 1.)
3. Amend probe 4b to accept either pin form. In
   /tmp/y1b-probes-c1.py (and the probe spec), accept the assignment
   form `namespace["__builtins__"] = dict(SAFE_BUILTINS)` as well as
   the dict-literal form. Acceptance: amended 4b passes on the new
   commit. This is a probe fix, not a code fix.
4. Replace probe 4a with 4a prime (executed-code builtins denial, as
   specified above) and 4b with 4b prime (form-agnostic static pin
   check). Record the residual risk in the probe file: op function
   `__globals__` still carry real builtins, with no live path while
   dunder and format stay closed. Acceptance: 4a prime and 4b prime
   pass on the new commit. This is a probe fix, not a code fix.
5. Full re-verification on the VM against the new commit. Re-run all
   20 probes (with amended 4a/4b); all must PASS except 2e, which is
   the single allowed exception and must be recorded with its exact
   result. Re-run `python3 -m unittest tests.test_codemode
   tests.test_code_exec` (81 tests, must stay OK). Re-run the full
   suite on the VM and record the count against the 1,483-test
   baseline (0 failures, 2 errors from VM toolchain gaps). Update the
   implementation log with which preemption option was chosen, what
   happens off the main thread (Option A) or how the child is reaped
   and its failure enveloped (Option B).

Documented residual risk, not must-fix before merge:

- Probe 2e (memory): a 100MB single allocation completes in 0.06s
  because no memory cap exists; the envelope cap bounds only
  serialized output. Closed automatically by Option B in item 2
  above; if Option A is chosen, it rides as documented residual risk
  with the exact failure recorded, and the follow-up owner notes it
  for the child-process hardening pass.
- Item 4 second hop: op function `__globals__` carry real builtins;
  no live path on this commit. Future allowlist or dunder-adjacent
  changes must be re-checked with the redteam format-hole and dunder
  probes before they land.

## Question 3: should Codex proceed to Phase B (snippets registry) in parallel?

Parallel design and scaffolding, yes. Parallel merge, no. Phase A
must be fully green before any Phase B code merges, and no snippet
may be promoted until then.

The dependency is direct, not speculative. The registry executes
snippets through this same executor (run_snippet inside
CodeExecSession.run), and the two real blocking gaps strike Phase B's
own guarantees. The wall-clock gap (2a/2b) defeats the Phase B
budget-sharing rule: the council-3 probes for item 10 (10a loop
amplification, 10b shared deadline, 10f shared trace budget) assume
the deadline binds, and on this commit a snippet doing C-level work
burns 6 to 9 seconds per call with no interrupt, so a looping
run_snippet call would multiply that without any budget tripping.
Phase B verification cannot pass meaningfully until 2a/2b are fixed,
so merging Phase B first would mean verifying it against an executor
known not to bind its budgets, then re-verifying everything after the
executor changes underneath it. The chr gap (1e) is smaller but of the
same kind: registry code is written against the same SAFE_BUILTINS,
and a snippet that needs chr would fail at runtime on the fixed
executor.

What Codex may do now, in a separate branch at its own risk: the
manifest schema, the loader, the sha256 and expiry machinery, and the
item 9-12 tests that do not depend on preemption. What it must not do:
merge Phase B, promote any snippet, or treat any Phase B probe as
passed until the Phase A re-verification in item 5 above is green.
Merge order is strictly Phase A first, then Phase B re-verified
against the fixed executor.

## Question 4: overall verdict

### BLOCK

Phase A does not pass on commit 84b88bb. The format hole is genuinely
closed (1a-1d, 1f), the wrapper hole is genuinely closed (3a-3f), the
result cap genuinely works (2c, 2d), the builtins pin is present and
behaviorally effective, and Codex's own 81 tests pass. But the
wall-clock budget still does not bind C-level work in either executor
(2a errors only after 7.20s of burning CPU, 2b silently succeeds after
6.20s with ok=True), and the builtins pin introduced a real regression
in which legitimate `chr` use now raises NameError in both executors
(1e). Those three fails are real, each independently blocks Phase A
under the probe spec's rule, and no reclassification rescues them:
the two reclassified fails (4a, 4b) are probe artifacts whose
amendment is Y1b's work, not Codex's, and 2e is the single allowed
exception. The follow-up is small and well specified (add chr, add
real preemption in both executors, amend two probe strings, re-run
everything), and Phase B design work may proceed in parallel in a
separate branch, but nothing merges and no snippet is promoted until
the re-verification run is green.
