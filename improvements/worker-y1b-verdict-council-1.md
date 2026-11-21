# Verdict Council 1: Phase A items 1-2, Worker Y1b fix commit 84b88bb

Date: 2026-11-21. Author: Verdict Council 1 (judging Worker Y1b).
Scope: items 1 and 2 ONLY, from the Phase A executor hardening set.
Evidence base: Y1b verification run (worktree /tmp/y1b-verify, commit
84b88bb, "fix: harden code execution envelopes"), probe spec
improvements/worker-y1b-verify-council-1.md, probe runner
/tmp/y1b-probes-c1.py, and this council's own independent re-run of the
disputed probes (1e, 2a, 2b) against the same checkout, which reproduced
Y1b's results exactly in kind (1e codemode f-string NameError on chr;
2a elapsed 6.70s with a late wall-clock error; 2b elapsed 9.63s with
ok=True silent success).

Verdict rule applied: the probe spec's Phase A rule. All probes 1a-1f
and 2a-2d must PASS. Probe 2e is the single allowed exception (recorded
as residual risk, not a silent pass). Any other FAIL blocks Phase A.

No em dash or en dash in this file, per standing rule.

## Item 1: str.format defeats the dunder ban

### Verdict: PARTIAL (security hole closed, legitimate-functionality regression open)

| Probe | Result | Evidence |
| 1a codemode class leak | PASS | status error, no class string in envelope |
| 1b codemode globals leak | PASS | status error, repo root path absent |
| 1c code_exec session-token leak | PASS | ok False, error_type sandbox, token absent from envelope JSON |
| 1d code_exec session dict dump | PASS | ok False, error_type sandbox, no session_token, dom_snapshots, or check_cancel in envelope |
| 1e negative controls (legit formatting) | FAIL | codemode f-string `f"{len(chr(65))}"` errors `NameError: name 'chr' is not defined`; code_exec f-string fails the same way; both `%` halves pass (`ok-1`) |
| 1f static guard | PASS | `format` absent from SAFE_ATTRIBUTE_NAMES in both files |

### Reasoning

The attack is dead. All four leak paths (1a-1d) are rejected at scan
time, and the whitelist entry is gone in both executors (1f). That is
the whole of the security defect in item 1, and it is fixed.

The 1e failure is real and is a regression, not a probe artifact. On
BASE code (87cd34f) the same codemode f-string probe PASSED with result
"1", because codemode did not pin `__builtins__` and the full builtins
module leaked into the namespace. Commit 84b88bb pins
`namespace['__builtins__'] = dict(SAFE_BUILTINS)` (the item 4 fix), and
`chr` is in neither SAFE_BUILTINS list. Both lists are identical:
False, None, True, abs, bool, dict, enumerate, float, int, isinstance,
len, list, max, min, range, reversed, round, set, sorted, str, sum,
tuple, zip. So the pin, which item 4 requires, removed `chr` from
codemode scope. The code_exec f-string failure is pre-existing (chr was
never in code_exec SAFE_BUILTINS either), but the codemode half is a
regression introduced by this very commit, and probe 1e explicitly
requires all four halves to pass.

This does NOT block Phase A on security grounds, but it DOES keep the
Phase A gate closed, because the verdict rule requires 1a-1f all PASS.
The distinction matters: the fix approach is right, no redesign is
needed, and the remaining work is a one-line addition, not a rework.
Calling it BLOCKED would misstate the state of the hole; calling it
FIXED would bless a commit that breaks legitimate snippets. PARTIAL is
the accurate verdict.

### Is chr safe to add? Yes.

`chr(i)` is a pure function: for an integer 0 to 0x10FFFF it returns a
one-character string, otherwise it raises ValueError. It performs no
attribute access, no object graph traversal, no I/O, and no evaluation.
It cannot reach `__class__`, `__globals__`, or any dunder, and a string
built with chr is inert inside the sandbox because eval, exec, compile,
and `__import__` are all banned names and the scanner rejects dunder
Names and attributes in code. Adding `chr` to SAFE_BUILTINS in both
files reopens no hole the format removal closed.

### What else might the pin have broken?

Checked against the actual consumers. P1-P4 (improvements/
pick1-program-template.md) use only op functions (`windows`,
`observe`, `act`, `assert_file_exists`, `assert_file_contains`,
`assert_state`) and plain variables; a name scan of every Python block
in the template finds no builtin outside SAFE_BUILTINS. P1-P4 are
unaffected by the pin. No other live snippet set was found in the repo
that needs a builtin outside the list. The only demonstrated breakage
is `chr` in probe 1e.

Other plausible pure builtins (`ord`, `hex`, `oct`, `bin`, `all`,
`any`, `divmod`, `pow`, `hash`, `iter`, `next`) are equally harmless in
principle, but none is demonstrated as needed by any probe, snippet, or
test, so the follow-up must NOT add them speculatively. `repr` is
deliberately excluded from this recommendation: it invokes `__repr__`
on live objects, which can dump object internals. `format` as a builtin
is also excluded: it is not needed and it sits too close to the hole
just closed. Add only what is proven needed.

### Follow-up fix required for item 1 (precise)

1. Add `"chr": chr` to SAFE_BUILTINS in scripts/codemode.py and
   `'chr': chr` to SAFE_BUILTINS in scripts/code_exec.py. Adding
   `"ord": ord` alongside it is acceptable and recommended (chr's exact
   inverse, equally pure, the obvious next NameError a snippet would
   hit), but it is optional, not required.
2. Re-run probe 1e on the VM against the new commit: all four halves
   must return completed / ok True with results "1" and "ok-1".
3. Re-run probes 1a-1d and 1f to confirm no regression from the
   addition, and re-run `python3 -m unittest tests.test_codemode
   tests.test_code_exec` (81 tests, must stay OK).
4. Do NOT widen SAFE_BUILTINS beyond chr (and optionally ord) without a
   failing probe or a named snippet that needs the addition.

## Item 2: wall-clock and result budgets do not bind C-level work

### Verdict: BLOCKED (hard block, no passing reading exists)

| Probe | Result | Evidence |
| 2a codemode wall preemption | FAIL | elapsed 5.26s (Y1b) / 6.70s (this council's re-run), status error "wall-clock budget exceeded" raised only AFTER the C loop finished; probe needs elapsed at most 4.0s |
| 2b code_exec wall preemption | FAIL | elapsed 5.31s (Y1b) / 9.63s (this council's re-run), ok=True with NO error, silent success; probe needs elapsed at most 4.0s and ok False |
| 2c codemode 50MB result cap | PASS | status error, result_too_large, envelope 189 bytes |
| 2d code_exec 50MB result cap | PASS | ok False, result_too_large, envelope within cap |
| 2e memory, 100MB allocation | FAIL | allowed exception per the verdict rule; recorded here as residual risk, not as a Phase A blocker on its own |

### Reasoning

The result-cap half is genuinely fixed: both executors refuse a 50MB
result with result_too_large and a 189-byte envelope (2c, 2d). The
wall-preemption half is entirely absent. There is no preemption
mechanism in commit 84b88bb: no signal.setitimer, no SIGALRM handler,
no child process, no timeout kill. The diff adds only the envelope cap.

Is there ANY reading under which 2a or 2b pass? No, and the probe spec
closes each candidate reading in advance:

- Late error is not preemption. Probe 2a's spec states in terms: "A
  late 'wall-clock budget exceeded' raised only after the C loop
  finishes is still FAIL." The 2a error fires after 5 to 7 seconds of
  burning CPU, against a 2s wall. The budget did not bind anything.
- Silent success is worse than a late error. Probe 2b returns ok=True
  after 5 to 10 seconds with the correct sum and no error at all. A
  supervisor reading that envelope treats the run as valid. The trace
  check never fires because a one-line program's final line event fires
  before the C call, so no check ever runs after it. Nothing in the
  commit changes that path.
- Documenting the budget as post-hoc only is explicitly ruled out by
  the probe spec: "Documenting the budget as post-hoc only, without
  preemption or upfront refusal, FAILS probes 2a and 2b." The commit
  documents the budget (the error string exists) and enforces it only
  after the fact.
- Elapsed time alone fails both probes independent of the error text:
  5.26s and 5.31s (Y1b), 6.70s and 9.63s (this council), all above the
  4.0s PASS ceiling, against a 2s wall.

Because the wall half is a named must-fix half of item 2 (the task
brief names the budget bypass itself, sum(range(3 * 10**8)) taking
7.40s / 9.06s against a 2s wall, as the defect), and because both
probes fail on both executors with no mechanism present, this is a hard
BLOCK, not a partial. A partial verdict would imply the fix is
incomplete but present; here the preemption mechanism does not exist.

### Minimal acceptable preemption

One of the following, implemented in BOTH executors (codemode
execute_op and code_exec CodeExecSession.run), since 2a and 2b fail
independently:

- Option A (minimal): signal.setitimer(ITIMER_REAL, wall_seconds)
  armed immediately before exec, with a SIGALRM handler that raises
  inside the snippet, disarmed in a finally block. This works only on
  the main thread, which is acceptable because the probes run on the
  main thread, but the code must fail closed off the main thread: if
  the timer cannot be armed (not the main thread), the run must either
  refuse up front or fall back to Option B, never run unbounded and
  silent the way 2b does today. A bare `signal` import that silently
  no-ops off-thread would reproduce the 2b failure mode and is not
  acceptable.
- Option B (robust, preferred): execute the snippet in a child process
  with a hard timeout and kill on expiry, returning a wall-clock error
  envelope to the caller. This also closes probe 2e (a child with an
  RLIMIT_AS cap turns the 100MB allocation into an enveloped error
  instead of a completed run), which Option A cannot do, since
  `"A" * (10**8)` allocates in one fast C call that a timer never
  interrupts.

Upfront static refusal (rejecting a program before running it) counts
only as a complement, not as the preemption mechanism itself: the probe
spec allows an upfront refusal naming the refused construct, but a
refusal that keys only on the literal `range(3 * 10**8)` in these two
probes would game the probe while leaving `sum(range(n))` with a
computed n, a large list build, or an unbounded loop unbound. Any
static refusal must generalize (a bound the static check cannot prove
small is refused or timed), which in practice means the timer or the
child process anyway. A literal-only refusal will be judged as a probe
bypass, not a fix.

### Proof this council will accept

1. Re-run probes 2a and 2b on the VM against the new commit: elapsed
   at most 4.0s each, with a wall-clock error (or a general upfront
   refusal naming the construct), in both executors. A single run each
   is enough if both pass; two consecutive passing runs are better
   given the timing variance seen (5.26s vs 6.70s for the same probe).
2. Re-run probes 2c and 2d to confirm the cap still holds, and re-run
   probe 2e and record its result: if it still FAILS under Option A,
   record the exact failure as residual risk (memory exhaustion via
   large intermediate allocations is not bounded by the envelope cap,
   which bounds only what leaves the executor); if Option B is used,
   2e must PASS.
3. Re-run `python3 -m unittest tests.test_codemode
   tests.test_code_exec` (81 tests, must stay OK).
4. State in the implementation log which option was chosen, what
   happens off the main thread (Option A) or how the child is reaped
   and its failure enveloped (Option B), and confirm the agent process
   stays alive and responsive after a timed-out run.

### Residual risk: probe 2e

2e FAILS on commit 84b88bb (100MB single allocation completes; the
envelope cap does not bound intermediate allocations, only the
serialized result). Per the verdict rule this is the single allowed
exception and does not block Phase A on its own. It is recorded here
so it is not hidden: a snippet can still allocate unbounded memory
inside one run and the executor will not stop it. Option B above
closes it; Option A leaves it open as documented residual risk.

## Summary

- Item 1: PARTIAL. The format hole is closed (1a-1d, 1f PASS), but
  probe 1e FAILS on a real codemode regression: `chr` worked before the
  builtins pin and now raises NameError. Follow-up: add `chr` (and
  optionally `ord`) to SAFE_BUILTINS in both files, then re-run 1e plus
  1a-1d, 1f and the 81 unit tests.
- Item 2: BLOCKED. The 64KB result cap works (2c, 2d PASS), but wall
  preemption is entirely absent: 2a errors only after the C loop
  finishes (5.26s / 6.70s vs a 2s wall), and 2b silently succeeds
  (5.31s / 9.63s, ok=True, no error). No reading of the probe spec
  passes either probe. Follow-up: implement real preemption in both
  executors (signal timer failing closed off-thread, or preferably a
  child process with timeout and kill), then re-run 2a-2e and the 81
  unit tests.

Phase A does not pass on commit 84b88bb. Items 3 and 4 are out of scope
for this council and are judged by their own panels.
