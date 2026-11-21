# Verdict: Phase A items 3-4 (Council Member 2, Worker Y1b)

Date: 2026-11-21. Author: Council Member 2 (verification panel for Worker Y1b).
Scope: items 3 and 4 ONLY, from the Council 1 probe spec
(improvements/worker-y1b-verify-council-1.md). Items 1-2 are not judged here.
Code under test: commit 84b88bb, "fix: harden code execution envelopes",
worktree /tmp/y1b-verify. Probe runner: /tmp/y1b-probes-c1.py.
Independent checks: /tmp/c2-checks.py (run by this council member, not by Y1b).

## Verdicts

- Item 3 (codemode wrapper reachable): FIXED.
- Item 4 (codemode does not pin __builtins__): FIXED, with probe amendments
  required (4a and 4b as written are defective, see below). No code change
  is required for the verdict. One non-blocking hardening is recommended
  in the follow-up section.

## Independent rerun (this council member, same worktree and runner)

Full run reproduces Y1b exactly: 14/20 PASS. Items 3a-3f all PASS.
Item 4: 4a FAIL, 4b FAIL, 4c PASS. The other four FAILs (1e, 2a, 2b, 2e)
are outside this council's scope and are not judged here.

Evidence lines from the rerun:

- 3a: PASS, status=error error=dunder access is banned
- 3b: PASS, status=error error=dunder access is banned
- 3c: PASS, status=error result=None error=dunder access is banned
- 3d: PASS, status=error error=lambda/async/yield/global are banned
- 3e: PASS, ok=False error_type=sandbox error=yield is not allowed in a code-exec program
- 3f: PASS, status=error error=lambda/async/yield/global are banned
- 4a: FAIL, status=error leaked=['__builtins__ is a module, not a pinned dict: None']
- 4b: FAIL, pin line present (string match only, see below)
- 4c: PASS, pin line present

Codex's own tests re-run by this council member: python3 -m unittest
tests.test_codemode tests.test_code_exec = 81 tests, OK.

## Item 3: FIXED

Evidence: all six probes 3a-3f PASS on the independent rerun (lines above).
The wrapper no longer exists: grep for codemode_main in scripts/codemode.py
returns nothing, and _module_code lowers a final top-level Return to a
plain `result = ...` assignment, so there is no function object for model
code to reference, call, or re-enter.

Hole checks run by this council member (all against 84b88bb):

- T1 non-final return in if (`if True: return 1`): error, SyntaxError
  'return' outside function, never executes. A non-final return is a
  compile error, not a hole.
- T2 non-final return in try/finally: same SyntaxError, never executes.
  A finally clause cannot run after a lowered return because the return
  itself never compiles at module level.
- T3 nested def with return, called: completed, result 7. Ordinary code,
  no wrapper involved.
- T4 nested def referencing __codemode_main__: scan error, dunder access
  is banned. The scan walks the whole tree, including nested defs.
- T5 nested def with `global result` overwrite: scan error, Global is
  banned. The `result` variable cannot be rebound from inside a function.
- T6 bare `result = 5` with no return: completed, result 5. Noted as a
  semantic change, not a hole: pre-fix a no-return program returned None,
  now a bare assignment to the name `result` becomes the envelope result.
  The model could already return any value via `return`, and the value
  is still capped by the 64KB envelope check, so this grants no new
  capability. Recommended nit, not blocking: only read namespace["result"]
  when the original tree ends in a Return, else report None.
- T7 `result = 99` then `return 1`: completed, result 1. The lowered
  final return is the last statement, so it always wins.
- T8 nested func mutating a `result` list: completed [1]. Ordinary
  computation, no escape.
- T9 return only inside a nested def: completed, result None.
- T10a class with __enter__/__exit__: error, NameError __build_class__
  not found. Class definitions are dead under the pinned builtins (see
  item 4 notes). This doubly closes dunder-method routes.
- T10b __exit__ reading tb.tb_frame: scan error, tb_frame not allowlisted,
  even inside a dunder method body. Dunder method names are strings, not
  Name nodes, so the def itself is not scan-banned, but every attribute
  spelling inside the body still is.
- T11 __getattr__ laundering of `C().__globals__`: scan error, dunder
  attribute access is banned. A __getattr__ hook cannot launder a banned
  spelling because the spelling itself is rejected at parse time.
- T12 yield inside a nested def: scan error, Yield banned anywhere.
- T13 lambda: scan error, Lambda banned.

No remaining wrapper-reachability path was found. Double execution would
require calling exec/eval (banned names) or the wrapper (deleted). A
model-defined function re-running its own body is just the model running
its own code twice, not a wrapper hole, and each execute_op call gets a
fresh namespace, so nothing persists across calls.

## Item 4: FIXED (specified fix verified; probes 4a/4b defective)

The specified fix was the one-line pin, exactly as code_exec.py run()
does it. Codex implemented it exactly: codemode.py line 278,
`namespace["__builtins__"] = dict(SAFE_BUILTINS)`. This council member
verified the pin behaviorally in-process (check A11 below), which is the
property the fix governs: the exec namespace.

### The pin works where it governs (check A11)

Capturing the exec namespace via mock.patch on builtins.exec and running
`def f(): return 1; return f()` gives: namespace __builtins__ is a dict;
its keys are exactly the 23 SAFE_BUILTINS names; eval, open, __import__,
compile, getattr, input, globals, locals are all absent; the dict equals
codemode.SAFE_BUILTINS. Codex's own codemode builtins test asserts the
same thing and passes (part of the 81 OK). The pin is real, not a comment
or dead path.

### The residual op-globals fact (confirmed, theoretical, no live path)

Y1b's in-process check is confirmed: _op_list_scripts.__globals__ is the
codemode module dict, and its __builtins__ is the real full builtins dict
containing eval (ob.get("eval") is builtins.eval). The namespace pin does
not and cannot change a pre-existing module-level function's __globals__.
That is a fact about Python semantics, not a defect in the pin.

This council member actively tried to construct a live path from sandboxed
code to that dict, and every attempt failed (all against 84b88bb):

- A1 `repo_list_scripts.__globals__`: scan error, dunder attribute banned.
- A2 `getattr(repo_list_scripts, '__glo' + 'bals__')`: scan error, getattr
  is a banned name. Building the string dynamically does not help because
  the getattr name itself is banned.
- A3 f-string `f"{repo_list_scripts.__globals__}"`: scan error. The
  Attribute node inside the f-string is walked by the scan.
- A4 `"{0.__globals__}".format(repo_list_scripts)`: scan error, format
  not allowlisted (item 1 fix).
- A5 `vars(repo_list_scripts)`: scan error, vars banned.
- A6 exception `e.__traceback__`: scan error, dunder attribute banned.
- A7 exception `e.args`: scan error, args not allowlisted.
- A8 named exception handler (`except Exception as e`): NameError, name
  'Exception' is not defined, because Exception is not in SAFE_BUILTINS.
  Named handlers cannot run at all, and bare `except:` binds no object,
  so exception objects are unreachable, not just unreadable.
- A9 `repo_list_scripts['__globals__']`: TypeError enveloped, functions
  are not subscriptable.
- A12 bare `result = repo_list_scripts`: error, serialized result envelope
  exceeds 65536 bytes, error_type result_too_large. The envelope cap
  (item 2 fix) blocks the live function from leaving the process.
- A13 `__builtins__` as a name: scan error, banned name.
- A15 `__class__` cell inside a method: scan error, dunder name banned.
- A16 `(1).__class__`: scan error, dunder attribute banned.
- A17 model-defined `f.__globals__`: scan error, dunder attribute banned.
- A18 `str(repo_list_scripts)`: completed, repr string only, no live object.
- A20 op-arg smuggling via a class with a custom lower() method: error,
  NameError __build_class__ not found. Class definitions are dead under
  the pinned builtins, so model code cannot smuggle dunder methods into
  op calls at all.
- A10 op return values: repo_list_scripts() returns plain dicts/lists/
  strings/ints, zero callables inside. No op returns a live object.

The single choke point is therefore the AST scan (dunder-attribute ban,
banned names including getattr/vars/globals, allowlisted attributes).
Every route to the op globals needs that choke point to fail first, and
several routes are doubly closed (class defs dead, named except handlers
dead). The risk is theoretical and contingent on a future scan gap, not
live in this code. The redteam itself called item 4 "latent, not live".

### Why 4a FAILs: the probe is over-specified on two independent counts

1. Wrong target. Probe 4a asserts the OP function's __globals__ carries
   the pinned dict. No namespace pin can do that: an op function's
   __globals__ is its defining module's dict by construction. The
   specified one-line fix governs the exec namespace (and therefore the
   globals of functions the model defines), never the op functions'
   globals. The probe demands a property the specified fix was never
   designed to provide, so the probe cannot pass under the specified fix.
2. Unmeasurable channel. Probe 4a requires env["status"] == "completed"
   with the live function as the result, then inspects it from outside.
   The item 2 envelope cap in the same commit makes any live-function
   result return result_too_large instead (check A12). The probe's own
   harness shows this: fn is None, so the leaked list is the artifact
   string '__builtins__ is a module, not a pinned dict: None'. Even if
   the op functions were wrapped with pinned globals, 4a as written
   would still FAIL on the status assertion. The probe must be amended
   regardless of any code change.

### Why 4b FAILs: probe string artifact, not a code failure

Probe 4b asserts the literal string `'__builtins__': dict(SAFE_BUILTINS)`
(single quotes, dict-literal form) in codemode.py. Codex wrote the
semantically identical assignment form, `namespace["__builtins__"] =
dict(SAFE_BUILTINS)` (double quotes, assignment), at line 278. The pin
exists and is verified behaviorally (A11). Probe 4c passes only because
code_exec.py happens to use the dict-literal form. The probe should accept
both forms.

## Follow-up fixes required

### Required: amend probes 4a and 4b (no code change blocks this verdict)

- 4a amended (behavioral, in-process, since a live function can no longer
  cross the envelope): capture the exec namespace by patching builtins.exec
  around execute_op, run code that defines a function (`def f(): return 1;
  return f()`), then assert the captured namespace["__builtins__"] is a
  dict equal to (or a subset of) codemode.SAFE_BUILTINS with none of eval,
  open, __import__, compile, getattr, input, globals, locals in it, and
  assert the model-defined function's __globals__["__builtins__"] is that
  same pinned dict. Record the op-function globals fact separately as a
  known residual: _op_list_scripts.__globals__["__builtins__"] is the real
  builtins dict, reachable only via a scan bypass, with no live path
  demonstrated. This is check A11 in /tmp/c2-checks.py, which passes.
- 4b amended (static): accept either the dict-literal form
  `'__builtins__': dict(SAFE_BUILTINS)` or the assignment form
  `namespace["__builtins__"] = dict(SAFE_BUILTINS)` (match on
  `__builtins__` and `dict(SAFE_BUILTINS)` in the namespace construction
  of execute_op, not on one exact literal).

### Recommended, non-blocking: wrap op functions with pinned minimal globals

Defense in depth for the theoretical op-globals hop. In codemode.py, after
the OPS table, rebind each op fn with types.FunctionType using a minimal
globals dict, and expose the wrapped functions in the exec namespace
instead of the raw module-level functions. Sketch:

```python
import types
_PINNED_OP_GLOBALS = {
    "__builtins__": dict(SAFE_BUILTINS),
    "REPO_ROOT": REPO_ROOT, "Path": Path, "os": os, "time": time,
    "CodemodeError": CodemodeError, "MAX_READ_BYTES": MAX_READ_BYTES,
}
for _op in OPS:
    _fn = _op["fn"]
    _op["fn"] = types.FunctionType(_fn.__code__, dict(_PINNED_OP_GLOBALS),
                                   _fn.__name__, _fn.__defaults__,
                                   _fn.__closure__)
```

Then fn.__globals__["__builtins__"] is the pinned dict for every op. Two
caveats, which is why this is recommended and not blocking: first, the
wrapper globals must contain every module global each op body references
(the names above cover the current four VM-runnable ops; any future op
that references a new module global breaks at runtime with NameError
unless the wrapper dict is updated, so the dict must be reviewed on every
op edit); second, the wrapper globals still hold live Path/os/time objects
(the op code needs them), which are unusable without eval or a
non-allowlisted attribute spelling, so the wrap removes the scan-escaping
primitive (eval), not every dangerous object. The same latent exposure
exists on the code_exec side (bound session methods whose __globals__ is
the code_exec module dict), which the redteam did not flag and probe 4c
does not test, so demanding the wrap for codemode alone would be
inconsistent with the accepted code_exec shape. File as hardening, not as
a Phase A gate.

### Recommended nit, non-blocking: restore no-return means None (item 3, T6)

In _module_code / execute_op, only report namespace["result"] when the
original tree's last statement was a Return; otherwise report None. This
restores exact pre-fix semantics for programs with no return. Do not add
__build_class__ to SAFE_BUILTINS to "fix" class definitions: class defs
being dead is currently load-bearing defense in depth for the dunder-method
routes, and re-enabling them needs a council review first.

## Out of scope, recorded for the parent

This rerun reproduced Y1b's 14/20 exactly, including FAILs on 1e, 2a, 2b,
2e. Those probes belong to items 1-2 and are not judged by this council.
Noted in passing: 2e completed in 0.06s with a 100MB string because
codemode only envelopes the `result` value, not namespace variables, so a
huge assigned-but-unreturned string never reaches the cap check. That is
an item 2 matter for whoever judges item 2, not a finding of this council.
