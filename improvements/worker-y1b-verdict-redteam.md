# Verdict Redteam: Worker Y1b Phase A draft verdict (Worker Y1b panel)

Date: 2026-11-21. Author: Verdict Redteam (subagent of Worker Y1b).
Scope: attack the DRAFT Phase A verdict from both directions, not the code
alone and not the probes alone. Read-only static audit in this turn, see
the method note below. No laptop touched, no network, no ydotool.

## Method note, and what was NOT done in this turn

This turn did not run the probe runner and did not run git. A shell
result in this session tripped an execution-risk check, and the runtime
notice that followed forbids running, testing, importing, or loading
the checked-out content, and forbids git commands inside it, until
approval to proceed is given. So every claim below is a static code
citation (file, function, quoted code) plus a runnable snippet that
Y1b or the parent can run after that approval. Nothing below is
presented as a live run result from this turn. Y1b's own probe
numbers (14/20 PASS, fails 1e, 2a, 2b, 2e, 4a, 4b) are taken from
the task handoff, not re-measured here.

Sources read in this turn, by plain file viewing only:
- improvements/worker-y1b-verify-council-1.md (20 probes, items 1-4)
- improvements/worker-y1-redteam.md (original BLOCK, Attacks 1-9)
- improvements/worker-y1b-verify-redteam.md (probe redteam, 90 probes)
- improvements/pick1-program-template.md (P1-P4)
- /tmp/y1b-probes-c1.py (Y1b probe runner, 245 lines)
- /tmp/y1b-verify/scripts/code_exec.py (fixed code, commit 84b88bb)
- /tmp/y1b-verify/scripts/codemode.py (fixed code, commit 84b88bb)
- /tmp/y1b-verify/tests/test_codemode.py and tests/test_code_exec.py
- /tmp/y1b-verify/improvements/worker-y1-codex-impl-log.md (Phase A log)

Draft verdict under attack: Phase A BLOCKS. Reasons given: 2a/2b (no
wall preemption), 1e (codemode regression from the pin), 4a (op fn
globals unpinned, residual live-object hop). 4b is a probe string
artifact. 2e rides as documented residual risk.

## Overall call

BLOCK stands, but on narrower grounds than the draft: only 2a/2b are
real blockers. 1e and 4a are probe artifacts, not real gaps, and 4b
is a probe string artifact as the draft says. Direction B finds two
new non-RCE holes the 20 probes miss (error-path mutable persistence,
and unbounded state-file growth), which widen the fix list but do
not change the BLOCK outcome, which 2a/2b already force.

Sharpest hole found: in-place mutation of a persistent mutable
variable persists across a FAILED code_exec run, because run() builds
the namespace as a shallow copy and only restores previous_variables
on the oversize path, never on AssertionError, CodeExecError, or
generic Exception paths. See B1 below.

---

## Direction A. Attack the BLOCK, try to prove Phase A should PASS

Verdict for direction A: PARTIAL SUCCESS. The attack kills two of the
three blocking reasons (1e and 4a), but it does not kill 2a/2b, and
2a/2b alone sustain the BLOCK under the council-1 spec as written.
A PASS is defensible only on the original redteam must-fix scope,
where preemption was should-fix 13, not must-fix. That scope
argument is stated honestly in A4, with its limit.

### A1. Probe 1e (chr): probe artifact, not a regression, not a blocker

Claim: the 1e FAIL does not prove Codex introduced a codemode
regression, and chr is not needed by any real snippet.

Evidence, static:
- chr is not in SAFE_BUILTINS in either file, before or after the
  fix. The Y1b probe redteam already proved this on the VM:
  "chr in codemode.SAFE_BUILTINS: False" and "chr in
  code_exec.SAFE_BUILTINS: False", and the code_exec leg of 1e
  FAILED on unfixed code too, with "name 'chr' is not defined".
  A probe that fails on unfixed code cannot be a regression test
  for the fix.
- The codemode leg of 1e passed pre-fix only because of the Attack 4
  hole itself: codemode did not pin __builtins__, so CPython
  inserted the real builtins module and chr resolved through it.
  Fixing item 4 (pinning) necessarily makes that leg fail. Probe 1e
  as written punishes the item 4 fix it is supposed to coexist
  with. That is a probe bug, not a code regression.
- P1-P4 need no chr. The template programs use only windows(),
  observe(), act(), assert_state(), assert_file_exists(),
  assert_file_contains(), list comprehensions, string literals, and
  dict indexing. No chr, no ord, no character-code work anywhere
  in improvements/pick1-program-template.md. The council-1 spec
  itself says "Nothing in P1-P4 needs it" for format, and the same
  holds for chr.
- The pin did change behavior for code that relied on full builtins,
  but that reliance was reliance on a bug (Attack 4), not on a
  documented capability. SAFE_BUILTINS is the documented allowlist,
  and chr was never in it.

Runnable proof, for Y1b to run after approval (static claim, not
run here):
```python
import importlib.util, pathlib
root = pathlib.Path("/tmp/y1b-verify")
def load(name):
    spec = importlib.util.spec_from_file_location(name, root / "scripts" / (name + ".py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
codemode = load("codemode"); code_exec = load("code_exec")
assert "chr" not in codemode.SAFE_BUILTINS
assert "chr" not in code_exec.SAFE_BUILTINS
# fixed probe 1e, using only allowlisted builtins:
e1 = codemode.execute_op('x = f"{len("ab")}"; return x')
assert e1.get("status") == "completed" and e1.get("result") == "2", e1
e2 = codemode.execute_op('x = "%s-%d" % ("ok", 1); return x')
assert e2.get("status") == "completed" and e2.get("result") == "ok-1", e2
```

Follow-up, not a blocker: add chr (and ord, both harmless, no
dunder, no I/O, no attribute access) to SAFE_BUILTINS in both
files, and fix probe 1e to use len("ab") instead of chr(65).
Do not block Phase A on 1e.

### A2. Probes 2a/2b (wall preemption): real, BLOCK survives this attack

Claim attacked: 5.26s vs the 4.0s threshold is an arbitrary line,
and the fix improved on the original 7.40s/9.06s, so the difference
is not a meaningful security difference.

This attack FAILS on technical grounds. The numbers:
- Original vulnerable code, redteam report: codemode 7.40s,
  code_exec 9.06s, for sum(range(3 * 10**8)) with a 2s wall.
- Fixed code, Y1b handoff: codemode 2a 5.26s with a late wall
  error, code_exec 2b 5.31s with silent ok=True.
- 5.26s is not preemption. It is the C compute time for that one
  input on that run, plus a post-hoc error raised only after the
  C loop returns. The tracer in codemode checks the deadline on
  line events only (codemode.py, execute_op tracer: the deadline
  check sits after the step count, and sys.settrace fires no
  events during a C call). The tracer in code_exec checks budgets
  only every 200 trace events and only on line events
  (code_exec.py, CodeExecSession._trace), and a one-line program's
  final line event fires before the C call, so no check ever runs
  after it. That is exactly the redteam Attack 2 mechanism, still
  present, unchanged by Codex's change.
- The 7.40s to 5.26s difference is machine variance and C loop
  speed for one fixed input, not a fix. The overrun scales
  linearly with the expression: sum(range(10**10)) would burn
  roughly 175s before any check fires, and code_exec would still
  report ok=True. A threshold of 4.0s vs 2.0s vs 7.40s is
  arbitrary, but the underlying property is not: the spec
  requires stopping near the 2s wall or refusing up front, and
  neither executor does either. Cancel is deaf for the same
  reason: check_cancel runs in the tracer and in _api, neither
  fires mid-C-loop.
- So 2a/2b are real gaps, and they are the core of Attack 2.
  No live exploit beyond Y1b's probes is needed here, because
  the probes themselves demonstrate the property: elapsed far
  over wall, and in code_exec silent success.

The only PASS argument for 2a/2b is scope, not technique, see A4.

### A3. Probe 4a (op fn globals): probe artifact, no live path found

Claim attacked: op function globals still carry full real builtins
including eval, so there is a residual live-object hop to RCE.

This attack SUCCEEDS in downgrading 4a from a real gap to a
probe artifact, with one honest residual noted at the end.

Why 4a as written can never pass:
- The op functions (repo_list_scripts and friends) are module-level
  functions defined in scripts/codemode.py. Their __globals__ is
  the codemode MODULE globals dict, which CPython fills with the
  real builtins on import. The execute_op namespace pin cannot
  change module globals. The Y1b probe redteam proved this:
  returning repo_list_scripts and inspecting
  fn.__globals__["__builtins__"] shows eval, open, __import__,
  compile on fixed code exactly as on unfixed code. 4a measures
  the wrong globals dict.
- The correct behavioral check is a MODEL-DEFINED function, whose
  __globals__ IS the exec namespace. codemode.py, execute_op:
  namespace is built as dict(SAFE_BUILTINS), then
  namespace["__builtins__"] = dict(SAFE_BUILTINS), then
  exec(compiled, namespace). A def defined inside the program
  therefore gets the pinned dict as its __globals__. The Y1b
  probe redteam gives the stronger probe shape: execute
  "def f():\n    pass\nreturn f" and assert
  fn.__globals__["__builtins__"] is a dict with no eval, open,
  __import__, compile, getattr, input, globals, locals.
- The envelope cap also closes the outward hop: returning an op
  function from execute_op is not JSON-serializable, so
  _serialized_size returns MAX_ENVELOPE_BYTES + 1 and
  _bounded_envelope replaces the envelope with a result_too_large
  error with no result. Y1b's handoff confirms this: 4a failed
  partly because the probe mechanism was blocked by the envelope
  cap. The harness outside the sandbox cannot even receive the
  live function through execute_op any more.

Live-path audit, every route I tried statically (no live run in
this turn, each route is a code citation):
- Direct attribute: repo_list_scripts.__globals__ is an Attribute
  node with attr starting with "_", rejected by codemode _scan
  and by code_exec _Validator.visit_Attribute (private attribute
  access is not allowed). Same for __self__, __class__,
  __dict__, __globals__, __builtins__.
- f-string: f"{repo_list_scripts.__globals__}" is the same AST
  Attribute node inside a FormattedValue, so the scan rejects it.
  f-strings are safe here precisely because their expressions ARE
  AST nodes, per the council-1 spec.
- str.format: "format" was removed from SAFE_ATTRIBUTE_NAMES in
  both files, and the Attribute check rejects it as not
  allowlisted. The Attack 1 hole is closed for this route.
- getattr / vars / globals / locals / eval / open / __import__:
  all are in BANNED_NAMES in both files, and visit_Name rejects
  any name starting with "__" as well.
- Exception traceback: an op that raises (for example
  repo_script_info on a missing file) returns only a string error
  in the codemode envelope, and inside the sandbox a caught
  exception object offers no usable attribute: e.args is not in
  SAFE_ATTRIBUTE_NAMES, e.__traceback__ starts with "_", and
  f"{e}" yields only the message string. No traceback object is
  ever exposed.
- Default arguments and closures: the op functions have only
  string/int defaults (pattern="", max_bytes=65536) and no
  closures (module-level defs). No callable or privileged object
  hides in a default.
- The result variable: _module_code lowers only a final top-level
  return to a result assignment, and execute_op returns
  namespace.get("result") through _bounded_envelope, which drops
  non-serializable values. A live function cannot leave through
  result.
- print: codemode binds print to a lambda that discards its args,
  code_exec binds print to CodeExecSession._print which appends
  str(a) to log_lines. Neither offers an attribute hop.
- In code_exec, the same audit holds for bound API methods
  (windows, observe, act, and friends): windows.__self__ is a
  dunder attribute, rejected; f"{windows.__self__}" is the same
  AST node, rejected; format is removed; getattr is banned.
  Their return values are plain dicts, lists, and strings, never
  live objects. Persistent variables filter out callables
  (code_exec.py, run(): kept excludes callable(v) and requires
  _is_jsonable(v)).

Honest residual: the op functions' module globals DO still
contain the real builtins module plus os, sys, json, time, and
Path (codemode module imports). That is a latent second hop, not
a live one: it needs a future gap that yields a live op function
or its globals dict as a value inside the sandbox, and no such
gap was found in this audit. The durable fix is to give the op
functions pinned globals (for example, rebuild each op with
types.FunctionType(fn.__code__, pinned_globals)), or to make the
ops return only plain data through a wrapper whose globals are
pinned. That is a follow-up, not a Phase A blocker on its own,
because the hop is currently unreachable. Do not block Phase A
on 4a as written. Replace 4a with the model-defined-function
probe.

Runnable proof, for Y1b to run after approval:
```python
import importlib.util, pathlib
root = pathlib.Path("/tmp/y1b-verify")
def load(name):
    spec = importlib.util.spec_from_file_location(name, root / "scripts" / (name + ".py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
codemode = load("codemode")
# every route below must be scan-rejected, never completed:
for src in (
    'return repo_list_scripts.__globals__',
    'x = f"{repo_list_scripts.__globals__}"',
    'x = "{0.__globals__}".format(repo_list_scripts)',
    'x = getattr(repo_list_scripts, "__globals__")',
    'return repo_list_scripts',
):
    env = codemode.execute_op(src)
    assert env.get("status") == "error", (src, env)
# model-defined function globals ARE pinned:
env = codemode.execute_op('def f():\n    pass\nreturn f')
# note: this return may hit result_too_large because a function is
# not serializable; the pin check below is the Codex unit test shape
# instead (tests/test_codemode.py test_execute_namespace_pins_safe_builtins):
# capture the exec namespace and assert its __builtins__ is a dict
# with no eval. That test passes on the fixed code.
```

### A4. The scope argument for a PASS, and why it does not win here

The strongest PASS argument is scope, not technique:
- The original redteam checklist (improvements/worker-y1-redteam.md)
  lists the result cap as must-fix 4 and real preemption as
  should-fix 13. Codex delivered the cap (2c/2d PASS) and did not
  deliver preemption (2a/2b FAIL). On the original must-fix list,
  Phase A passes.
- Council 1 upgraded the wall half to must-fix, on the grounds
  that the brief names the budget bypass itself as the defect.
  That upgrade is a judgment call by the same panel whose probes
  the Y1b probe redteam then showed to be flawed in material ways
  (1e fails a correct fix, 4a has a false premise, 2a/2b error
  text rejects a valid child-process timeout wording, 3a/3b/3c
  demand "dunder" where a NameError is a valid fix). A panel
  that erred on probe wording may also have erred on scope.
- A conditional PASS could therefore read: Phase A passes its
  original must-fix scope (format removal, wrapper removal,
  yield/async rejection, builtins pin, 64KB cap), with preemption
  and the chr audit as Phase A2 follow-ups, due before any
  snippet promotion that runs untrusted C-level work.

Why this does not win in this redteam's judgment:
- The council-1 spec is explicit, in writing, that documenting
  the budget as post-hoc only, without preemption or upfront
  refusal, FAILS probes 2a and 2b. Y1b's panel is the judge of
  Phase A, and its spec is the standard. Overruling it needs a
  decision by Y1, not a redteam inference.
- Preemption is not a cosmetic property. Without it, a single
  expression can hang the agent session for minutes (linear
  scaling, see A2), and the cancel latch is deaf during it. That
  is an availability hole in the live runner, not a test nicety.
- So direction A verdict: PASS is justified only if Y1
  explicitly re-scopes preemption back to should-fix. Under the
  spec as written, BLOCK stands on 2a/2b alone.

### A5. Probe 2e and 4b, for completeness

- 2e (100MB alloc completes in 0.06s): rides as documented
  residual risk, per the council-1 spec itself. A 2s wall timer
  can never fire on a 0.06s allocation. Only a memory cap or a
  child process with RLIMIT_AS catches it. Not a blocker alone.
- 4b (static pin line): probe string artifact, as the draft says.
  The pin exists in codemode as
  namespace["__builtins__"] = dict(SAFE_BUILTINS)
  (double-quote item assignment form), not as the single-quote
  dict-literal form the probe string-matches. The code_exec pin
  is the dict-literal form and passes 4c. Fix the probe to a
  regex, not the code.

---

## Direction B. Attack the FIX, try to prove the BLOCK is too weak

Verdict for direction B: PARTIAL SUCCESS. Two new holes were found
that the 20 probes miss. Neither is a full sandbox escape to RCE.
Both are real, both are in Phase A scope (executor hardening), and
both should join the fix list. They widen the BLOCK, they do not
upgrade it to a new severity class.

### B1. SHARPEST HOLE: in-place mutation of persistent mutable variables persists on FAILED runs

Severity: MEDIUM-HIGH (integrity, fail-closed violation, cross-run
poisoning). No RCE.

Code, scripts/code_exec.py, CodeExecSession.run():
- previous_variables = _jsonable_copy(self.variables) at run start.
  _jsonable_copy is a deep copy for dicts and lists, so previous
  is a clean snapshot.
- namespace = dict(self.variables). This is a SHALLOW copy. A
  mutable value (a dict or a list) in namespace is the SAME object
  as in self.variables.
- exec(code, namespace) runs the program. A program can mutate a
  persistent mutable in place, using only allowlisted operations:
  x.append(...), x.extend(...), x.pop(), x.remove(), or item
  assignment x["key"] = value (a Subscript store, not an Attribute
  node, so the scan allows it). All of append, extend, pop, remove
  are in SAFE_ATTRIBUTE_NAMES.
- On the oversize path only, the code restores:
  self.variables = previous_variables. That proves the author
  intended rollback on failure.
- On AssertionError, CodeExecError, and generic Exception paths,
  there is NO restore. The except blocks set envelope error and
  error_type only. self.variables is never reassigned, because
  the author assumed namespace mutations cannot reach
  self.variables. That assumption is false for in-place mutation
  of a mutable.
- finally: self._save_state() persists self.variables to disk,
  including the in-place mutation, even though the run failed.
  After the try block, envelope variables are filled from
  _jsonable_copy(self.variables), so the failed run's envelope
  can even report the mutated value.

Consequences:
- A failed run can poison the next run. Example shape: run 1 sets
  x = [] (ok). Run 2 does x.append("pwned"); assert_state(False).
  Run 2 fails, but x is now ["pwned"] in self.variables and on
  disk. Run 3 reads x and gets ["pwned"]. This is the cross-run
  variable poisoning family (redteam 9c), but inside one executor,
  without any snippet involved.
- A failed run can grow a variable up to the envelope cap. Each
  failed run can append a sub-cap chunk; the second size check
  after the try block only rolls back when the TOTAL envelope
  exceeds 64KB, so accumulation up to 64KB persists silently
  across failed runs. The docstring promise ("A program that
  tries any banned construct fails closed with no side effect
  beyond API calls already made") is violated: the side effect is
  a persistent variable write, not an API call.
- The oversize path's restore shows the fix shape: restore
  previous_variables on EVERY failure path, or build the
  namespace as a deep copy (namespace = _jsonable_copy(
  self.variables)) so in-place mutation cannot alias
  self.variables at all. Deep copy on entry is the cleaner fix,
  and it also fixes the same aliasing for the success path's
  kept-variables computation.

Runnable proof, for Y1b to run after approval (not run here):
```python
import importlib.util, pathlib
root = pathlib.Path("/tmp/y1b-verify")
spec = importlib.util.spec_from_file_location("code_exec", root / "scripts" / "code_exec.py")
code_exec = importlib.util.module_from_spec(spec); spec.loader.exec_module(code_exec)
class FakeBackend:
    def windows(self):
        return [{"address": "0xabc", "class": "kitty", "title": "t",
                 "at": [0, 0], "size": [800, 600], "workspace": {"id": 1}}]
s = code_exec.CodeExecSession(FakeBackend(), session_token="0123456789abcdef" * 2)
assert s.run("x = []")["ok"] is True
env = s.run('x.append("pwned")\nassert_state(False, "boom")')
assert env["ok"] is False, env
# FAIL if the mutation survived the failed run:
assert s.variables.get("x") == [], s.variables
```

Note on scope: on the SUCCESS path, in-place mutation persisting
is intended behavior (variables persist across runs by design).
The hole is failure-path persistence only.

### B2. Unbounded state-file growth via observations and DOM snapshots, past the 64KB envelope cap

Severity: MEDIUM (availability, disk growth, cap bypass by
persistence rather than by envelope).

Code, scripts/code_exec.py:
- CodeExecSession._save_state() writes a payload of variables,
  observations, and dom_snapshots with json.dumps, and applies
  NO size cap and NO pruning. There is no MAX_STATE_BYTES, no
  count cap, and no expiry prune in _save_state.
- CodeExecSession._load_state() prunes observations and
  dom_snapshots older than OBSERVATION_MAX_AGE (120s), but only
  on load, when a new session object is constructed. A live
  session object never prunes, and _save_state never prunes, so
  expired bindings are written to disk on every run until a new
  session loads.
- Each observe() adds an observation meta dict to
  self.observations, keyed by id, never evicted in-session. Each
  dom_observe() binds a full snapshot dict (up to 80 elements)
  into self.dom_snapshots. The envelope cap does not cover either,
  because the candidate envelope in run() contains variables,
  log, api_calls, and elapsed, but not observations or
  dom_snapshots.
- A program can therefore grow the state file without bound while
  every envelope stays under 64KB: 32 API calls per run, repeated
  across runs in one session, each run adding up to 32 new
  observation/snapshot entries. Worst-case estimate (not
  measured in this turn): a DOM snapshot with 80 elements is on
  the order of several KB, so 32 per run is on the order of
  100KB+ per run, and 100 runs is on the order of 10MB in a
  mode 0600 state file the supervisor never sees. The exact
  numbers need a live measurement; the unboundedness is proved
  by the code (no cap, no prune on save).
- Fix: prune expired observations and dom_snapshots in
  _save_state before writing, cap the count of stored bindings,
  and cap the serialized state payload (for example, refuse or
  drop oldest bindings past a state-file size budget).

### B3. _module_code lowering audit: fail-closed, not exploitable, but probe-relevant

Code, scripts/codemode.py, _module_code():
- Only a final top-level Return is lowered to a result
  assignment. A non-final top-level return (for example
  "return 1\nx = 2") is a SyntaxError at module level
  ("'return' outside function"), returned as an error envelope.
  Fail-closed, not an escape. It is a usability wart, and it is
  why probes 1a, 1b, 3a, 3b, 3c, 3f that use return are vacuous
  under module-level execution (already documented by the Y1b
  probe redteam). No security hole found here.
- A nested def can return an op function (def f():
  return repo_list_scripts; x = f()), giving live op fn access
  INSIDE the sandbox. That is intended (calling ops is the job),
  and the value cannot leave: codemode drops it via
  result_too_large, code_exec drops callables from kept
  variables. Its __globals__ is unreachable by the scan, see A3.
- A nested def can be a generator only if it contains yield, and
  Yield/YieldFrom are banned by _scan. A nested def that calls
  itself recursively is bounded by the trace step budget
  (20000) and by Python recursion depth, both enveloped.
- No hole found in _module_code. Recorded as checked, not as a
  finding.

### B4. Scan audit: every AST node type the scan does NOT handle

Checked, no new escape found. The gaps are dead ends on the
fixed code, listed so Y1b does not have to re-audit them:
- ClassDef is not banned in either file. Dead end: class
  creation needs __build_class__, which is not in
  SAFE_BUILTINS, and the pinned __builtins__ dict is used
  as-is, so a class statement raises NameError at runtime.
  Fail-closed.
- FunctionDef with a dunder name (def __foo(): ...) is not
  banned as a definition, but calling it is a Name node starting
  with "__", banned by both scans. Inert.
- Decorators: a decorator expression goes through the normal
  Name/Attribute checks. Decorating with an op function (for
  example @repo_list_scripts) calls the op with the function
  as its pattern argument and raises a type error, enveloped.
  No privilege gained.
- FormattedValue / JoinedStr: f-string expressions are AST nodes
  and go through the scan. A format spec cannot smuggle an
  attribute hop.
- Percent formatting: "%s" % value calls __str__ only, and a
  mapping key is a plain string, no attribute access.
- Subscript item assignment (x["k"] = v) is allowed by the scan,
  and it is the vector for B1, not for attribute access.
- Exception names: specific exception classes (Exception,
  ValueError) are Name nodes, not banned, but not present in the
  pinned builtins, so "except Exception:" raises NameError at
  runtime. Only bare "except:" works. No exception object can be
  inspected for a traceback, because e.args is not allowlisted
  and e.__traceback__ starts with "_".
- Starred, NamedExpr (walrus), comprehensions, and generator
  expressions are allowed and offer no attribute hop. A generator
  expression inside join/sorted can still build a huge string in
  C with no line events, which is the known 2a/2b/2e family, not
  a new scan hole.
- codemode _scan walks all nodes with ast.walk, so nested
  constructs inside functions, comprehensions, and f-strings are
  all visited. code_exec _Validator uses generic_visit the same
  way. No unvisited subtree was found.

### B5. Session restore logic on every error path: B1 is the gap, the rest holds

Checked against code_exec.py, CodeExecSession.run():
- Success path, oversize candidate: restores previous_variables,
  sets variables to {}, saves state again. Correct.
- Success path, final envelope oversize (log added after the
  candidate check): restores previous_variables and saves state
  again. Correct, subject to the _save_state best-effort caveat
  below.
- AssertionError / CodeExecError / generic Exception: NO
  restore. This is B1. The variables object is not reassigned,
  so in-place mutations persist, and _save_state in finally
  persists them to disk.
- _save_state itself is best-effort: it catches OSError and
  passes, with a comment that a failed save must not fail a
  program that already ran. Consequence: if the second save in
  the oversize path fails (disk full, permission), the disk still
  holds the oversize variables from the finally save, and the
  next _load_state loads them without any size check. Narrow
  window, but it means the oversize rollback is not atomic.
  Fix with B1 (deep copy on entry) plus a size check in
  _load_state, or write state to a temp file and rename.
- _save_state opens with O_TRUNC then writes. A crash mid-write
  leaves a truncated file, and _load_state catches ValueError
  and returns empty. Data loss, not a security hole, but it is
  another reason to write-then-rename.
- API side effects on error paths (observations bound, DOM
  snapshots bound, backend acts already made) are intended and
  documented ("no side effect beyond API calls already made").
  B1 is the only non-API side effect found.

### B6. What B did NOT find

- No live path from sandboxed code to eval, open, __import__,
  or compile was found, in either executor, after the format
  removal. See A3 for the full route list.
- No bypass of the 64KB envelope cap for the envelope itself
  was found. The cap checks the whole serialized envelope in
  codemode (_bounded_envelope) and in code_exec (candidate check
  plus final check), so the aggregate-envelope attack from the
  Y1b probe redteam (two 40KB variables making an 80KB envelope)
  is closed for the envelope. B2 is the persistence analogue,
  not an envelope bypass.
- No hole in the log path was found: log_lines are included in
  the candidate envelope in code_exec, and the final size check
  replaces an oversize envelope with an empty log. Codemode
  discards print output entirely.
- No hole in _module_code was found, see B3.

---

## Revised verdict and fix list

Revised BLOCK, on narrower and wider grounds than the draft:
- BLOCKING, real: 2a/2b, no wall preemption at all. Fix with a
  signal timer or a child process with a hard timeout and kill,
  plus a memory cap or RLIMIT_AS for 2e. Until then, do not claim
  the wall budget preempts anything.
- NOT blocking, probe artifacts, remove from the reasons: 1e
  (chr was never allowlisted, P1-P4 do not need it), 4a (wrong
  globals dict, hop unreachable, replace with the
  model-defined-function probe), 4b (pin exists in a different
  spelling, fix the probe to a regex).
- RIDES as documented residual risk: 2e (100MB alloc in 0.06s,
  only a memory cap catches it).
- NEW, joins the fix list (Phase A scope, non-RCE):
  B1, restore previous_variables on every failure path, or
  deep-copy the namespace on entry, so in-place mutation of a
  persistent mutable cannot survive a failed run.
  B2, prune expired observations and DOM snapshots in
  _save_state, and cap the serialized state payload, so the
  64KB envelope cap cannot be bypassed by persistence.
- FOLLOW-UPS, not blockers: add chr and ord to SAFE_BUILTINS
  in both files; pin op function globals (types.FunctionType
  with pinned globals) or prove every path closed, as the
  draft already says; replace probe 4a with the
  model-defined-function shape; fix probe 1e to len("ab");
  fix probe 4b to a regex.

## What still needs a live run (blocked in this turn)

The following were NOT run in this turn, for the execution-risk
reason in the method note, and need Y1b or the parent to run
them after approval to proceed:
1. The runnable snippets in A1, A3, and B1 above, against
   /tmp/y1b-verify at commit 84b88bb.
2. A live measurement for B2: run many dom_observe/observe calls
   in one session and measure the state file size growth.
3. The full 20-probe run, to confirm the revised reasons do not
   change any other probe result.
4. Commit and push of this file on todolist-push (pull --rebase
   and retry on collision), which is a git operation inside the
   checked-out content and was not done in this turn.

## Files

- This report: improvements/worker-y1b-verdict-redteam.md
  (in ~/workspace/computer-use-wayland, not yet committed or
  pushed, for the reason in the method note).

## Y1b live verification (18:33 +07, run by Y1b after approval)

Y1b ran the blocked steps itself against /tmp/y1b-verify at commit
84b88bb (runner /tmp/y1b-verify-b1b2.py). Results:

- B1 CONFIRMED (live): session run 1 sets x = [] (ok). Run 2 does
  x.append("pwned") then assert_state(False, "boom") and fails
  (ok=False, error_type=assert_failed), but s.variables["x"] is
  ["pwned"] AND the state file on disk holds ["pwned"]. In-place
  mutation survives a failed run and persists to disk.
- B2 CONFIRMED (live): 5 runs x 1 observe() in one session store 5
  observations, state file 1285 bytes, no cap and no prune on save.
  Growth is unbounded by the code (no cap in _save_state, prune
  only in _load_state).
- A1 CONFIRMED (live): fixed probe 1e with len("ab") passes
  (f-string result "2", % result "ok-1"). The 1e failure was the
  chr() choice, not formatting itself.
- A3 CONFIRMED (live): all 5 routes to op-function globals are
  scan-rejected (error). Model-defined function globals ARE pinned
  (dict, no eval/open/__import__/compile/getattr), verified by
  capturing the exec namespace.
- Full 20-probe run: already done by Y1b (14/20 PASS, same six
  fails), no change from the revised reasons.

Y1b final Phase A verdict (synthesis of all 4 verdict panel
members + this redteam + the probe redteam): BLOCK. Blocking
code items: 2a/2b (no wall preemption), B1 (restore on every
failure path or deep-copy namespace on entry), B2 (prune + cap
state on save), 1e follow-up (add chr and ord to SAFE_BUILTINS
in both files and amend the probe to len("ab")). Probe
amendments: 4a (model-defined-function probe), 4b (regex pin
check). Residual risk: 2e. Phase B may proceed in a separate
branch, but nothing merges and no snippet promotes until
Phase A re-verifies green.
