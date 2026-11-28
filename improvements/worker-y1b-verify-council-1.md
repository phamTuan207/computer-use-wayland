# Verification probes: Phase A executor hardening (Council Member 1, Worker Y1b)

Date: 2026-11-21. Author: Council Member 1 (verification panel for Worker Y1b).
Scope: must-fix executor items 1-4 from the redteam BLOCK report
(improvements/worker-y1-redteam.md). These probes are the standard Phase A
is judged against. Never trust Codex's own test report; run these probes
against the fixed code on the VM and record PASS or FAIL per probe.

Mapping to the redteam report: item 1 is Attack 1 (checklist 1); item 2 is
Attack 2 (checklist 4 for the result cap, checklist 13 for preemption; this
panel treats both halves as must-fix, see probe 2a note); item 3 is Attack 3
(checklist 3); item 4 is Attack 4 (checklist 2).

## How to run

- Run from the repo root: ~/workspace/computer-use-wayland, branch
  todolist-push, after the y1-snippets work is merged to the VM.
- Python on the VM is 3.12.3. All probes are plain Python, no laptop, no
  network, no live desktop. Nothing below is marked laptop-only: every
  probe runs on the VM against the fake backends.
- Import pattern (same as tests/test_code_exec.py): load
  scripts/code_exec.py and scripts/codemode.py with importlib from their
  file paths. For code_exec probes, reuse FakeBackend from
  tests/test_code_exec.py, or use the minimal inline fake in probe 1c.
- Sentinel token: use the literal token "0123456789abcdef" repeated twice
  (32 hex chars, the exact token shape code_exec accepts). It is a fake
  test token, never a real session token. The leak check asserts this
  exact string never appears in any envelope.
- Timing margin: wall probes use wall_seconds=2. Vulnerable code took
  7.40s (codemode) and 9.06s (code_exec) on sum(range(3 * 10**8)). PASS
  needs elapsed at most 4s. A full probe run takes about 30s when the code
  is fixed (each wall probe stops near 2s) and about 60s when vulnerable.
- A probe PASSES only when its stated PASS condition holds exactly. A
  partial fix (for example, rejecting the literal redteam one-liner but
  leaving another path open) FAILS the probe that exercises the other path.
- No em dash or en dash in this file, per standing rule.

## Item 1: str.format defeats the dunder ban

Fix under test: "format" removed from SAFE_ATTRIBUTE_NAMES in both
scripts/codemode.py and scripts/code_exec.py. Nothing in P1-P4 needs it;
f-strings and % formatting stay allowed because f-string expressions are
AST nodes and go through the scan, and % formatting does no attribute
access.

### Probe 1a (codemode, class leak)

```python
import importlib.util, pathlib
ROOT = pathlib.Path("scripts/codemode.py").resolve().parent.parent
spec = importlib.util.spec_from_file_location("codemode", ROOT / "scripts" / "codemode.py")
codemode = importlib.util.module_from_spec(spec)
spec.loader.exec_module(codemode)
env = codemode.execute_op('return "{0.__class__}".format("")')
```

- PASS: env["status"] == "error" and "class" not in str(env) and
  "<class 'str'>" not in str(env). The scan rejects the program before
  execution (expected error mentions "format" not allowlisted, or dunder).
- FAIL: env["status"] == "completed" and env["result"] == "<class 'str'>".
  That is the redteam R1 result on unfixed code.

### Probe 1b (codemode, module globals leak)

```python
env = codemode.execute_op('return "{0.__globals__[REPO_ROOT]}".format(repo_list_scripts)')
```

- PASS: env["status"] == "error", and the repo path (the value of
  codemode.REPO_ROOT, e.g. ~/workspace/computer-use-wayland)
  does not appear anywhere in str(env).
- FAIL: env["status"] == "completed" and env["result"] is the repo root
  path. On unfixed code this returns the path verbatim.

### Probe 1c (code_exec, live session-token leak; the critical probe)

```python
import importlib.util, pathlib, json, time
ROOT = pathlib.Path("scripts/code_exec.py").resolve().parent.parent
spec = importlib.util.spec_from_file_location("code_exec", ROOT / "scripts" / "code_exec.py")
code_exec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(code_exec)

class FakeBackend:
    def windows(self):
        return [{"address": "0xabc", "class": "kitty", "title": "t",
                 "at": [0, 0], "size": [800, 600], "workspace": {"id": 1}}]

TOKEN = "0123456789abcdef" * 2
session = code_exec.CodeExecSession(FakeBackend(), session_token=TOKEN)
env = session.run('x = "{0.__self__.session_token}".format(windows)')
assert TOKEN not in json.dumps(env), "TOKEN LEAKED"
```

- PASS: env["ok"] is False, env["error_type"] == "sandbox", the error
  mentions the format attribute (or dunder access), and the TOKEN
  assertion holds: the token string appears nowhere in json.dumps(env).
- FAIL: env["ok"] is True and env["variables"]["x"] == TOKEN, or the
  token appears anywhere in the envelope. On unfixed code the envelope
  returns the token verbatim (redteam probe R5b).

### Probe 1d (code_exec, full session dict dump)

```python
env = session.run('x = "{0.__self__.__dict__}".format(windows)')
```

Use a fresh session with the same TOKEN and FakeBackend as probe 1c.

- PASS: env["ok"] is False with error_type "sandbox", and neither
  "session_token" nor "dom_snapshots" nor "check_cancel" appears in
  json.dumps(env).
- FAIL: env["ok"] is True and env["variables"]["x"] contains
  "session_token" or "dom_snapshots". On unfixed code this dumps the
  whole session __dict__ repr, including observations and DOM snapshots.

### Probe 1e (negative controls: legitimate formatting still works)

```python
env = codemode.execute_op('x = f"{len(chr(65))}"; return x')
env2 = codemode.execute_op('x = "%s-%d" % ("ok", 1); return x')
```

And the code_exec equivalents via session.run with the same programs
(reading the result from env["variables"]["x"]).

- PASS: all four return completed / ok True with result "1" and "ok-1".
  f-strings and % formatting are not collateral damage.
- FAIL: any of them errors. That means the fix over-reached (for example
  banning f-strings or %).

### Probe 1f (static guard: format is gone from both whitelists)

```python
assert "format" not in codemode.SAFE_ATTRIBUTE_NAMES
assert "format" not in code_exec.SAFE_ATTRIBUTE_NAMES
```

- PASS: both assertions hold.
- FAIL: either holds "format". A runtime-only patch that leaves the
  whitelist entry in place is not the fix.

## Item 2: wall-clock and trace budgets do not bind C-level work

Fix under test: real preemption of C-level work (signal.setitimer /
SIGALRM wall guard, or snippet execution in a child process with a hard
timeout and kill), plus a cap on serialized envelope results at 64KB
(65536 bytes, the same order as MAX_READ_BYTES).

Note on scope: the redteam checklist lists preemption as should-fix 13
and the result cap as must-fix 4. This panel treats the wall-clock half
as must-fix too, because the task brief names the budget bypass itself
(sum(range(3 * 10**8)) taking 7.40s / 9.06s against a 2s wall) as the
defect. Documenting the budget as post-hoc only, without preemption or
upfront refusal, FAILS probes 2a and 2b. Either interrupt near 2s or
refuse up front; a late error after 7s+ of burning CPU is not a fix.
Preemption via signal.setitimer only works on the main thread: run
probes 2a and 2b on the main thread (plain script or unittest main
thread). A child-process implementation is equally acceptable and has no
thread constraint.

### Probe 2a (codemode, wall preemption)

```python
import time
started = time.monotonic()
env = codemode.execute_op("x = sum(range(3 * 10**8))", wall_seconds=2)
elapsed = time.monotonic() - started
```

- PASS: elapsed <= 4.0 and env["status"] == "error" with "wall-clock" in
  env["error"], OR elapsed <= 4.0 and the program was refused up front
  (error naming the refused construct). The run stops near the 2s wall.
- FAIL: elapsed > 4.0 (unfixed code: 7.40s), or env["status"] ==
  "completed" with the correct sum. A late "wall-clock budget exceeded"
  raised only after the C loop finishes is still FAIL.

### Probe 2b (code_exec, wall preemption; the worse case)

```python
session = code_exec.CodeExecSession(FakeBackend(), session_token=TOKEN,
                                    wall_seconds=2)
started = time.monotonic()
env = session.run("x = sum(range(3 * 10**8))")
elapsed = time.monotonic() - started
```

- PASS: elapsed <= 4.0 and env["ok"] is False with "wall-clock" in
  env["error"] (error_type "sandbox"), OR elapsed <= 4.0 with an upfront
  refusal error.
- FAIL: env["ok"] is True (unfixed code returns ok True after 9.06s), or
  elapsed > 4.0. Note the unfixed code_exec failure mode is silent
  success, not a late error: the trace check runs every 200 events on
  line events only, and a one-line program's final line event fires
  before the C call, so no check ever runs after it.

### Probe 2c (codemode, 50MB result cap)

```python
env = codemode.execute_op('return "A" * (5 * 10**7)')
```

- PASS: env["status"] == "error" with the error naming result size, OR
  env["status"] == "completed" and isinstance(env["result"], str) and
  len(env["result"]) <= 65536 (truncated at the 64KB cap).
- FAIL: env["status"] == "completed" and len(env["result"]) ==
  50000000. Unfixed code returns the 50MB string intact in 0.12s.

### Probe 2d (code_exec, 50MB result cap in the envelope)

```python
session = code_exec.CodeExecSession(FakeBackend(), session_token=TOKEN)
env = session.run('x = "A" * (5 * 10**7)')
blob = json.dumps(env)
```

- PASS: env["ok"] is False with an error naming result size, OR
  env["ok"] is True and len(env["variables"].get("x", "")) <= 65536 and
  len(blob) <= 70000 (64KB result plus envelope overhead).
- FAIL: env["ok"] is True and len(env["variables"]["x"]) == 50000000, or
  len(blob) is on the order of 50MB. The envelope must never carry an
  unbounded string to the supervisor.

### Probe 2e (memory: 100MB single allocation)

```python
env = codemode.execute_op('x = "A" * (10**8)', wall_seconds=2)
```

- PASS: env["status"] == "error" (wall preemption, memory cap, or
  MemoryError enveloped) with elapsed <= 4.0, and the agent process
  stays alive and responsive afterwards.
- FAIL: env["status"] == "completed" with a 100MB string, or the process
  is killed by OOM, or elapsed > 4.0. This probe is secondary to 2a-2d:
  if 2a-2d pass via a child process with an RLIMIT_AS cap, 2e passes
  with it; if 2a-2d pass via a signal timer only, 2e may still FAIL and
  that must be recorded as residual risk, not hidden.

## Item 3: codemode wrapper function is reachable, callable, and re-runs the program

Fix under test: in codemode _scan, reject any Name starting with "__"
(copy code_exec.py visit_Name lines 313-314) and reject Yield/YieldFrom
(copy code_exec.py lines 300-305) and AsyncFor/AsyncWith (copy lines
288-297); and make __codemode_main__ unreachable (delete it from the
namespace after exec, name it with a random unguessable suffix per
execution, or execute model code at module level the way code_exec does,
so there is no self-reference to reach).

### Probe 3a (reference to the wrapper is rejected)

```python
env = codemode.execute_op("return __codemode_main__")
```

- PASS: env["status"] == "error" and "dunder" in env["error"] (or
  "banned name"), and "<function __codemode_main__" appears nowhere in
  str(env).
- FAIL: env["status"] == "completed" and env["result"] is a function
  object (repr "<function __codemode_main__ at 0x...>"). On unfixed code
  the model holds a live reference to its own wrapper (redteam R2a).

### Probe 3b (unconditional self-call)

```python
env = codemode.execute_op("__codemode_main__()")
```

- PASS: env["status"] == "error" from the scan, before any execution
  (same dunder rejection as 3a). No RecursionError, no completed status.
- FAIL: env["status"] == "error" with "RecursionError" in env["error"]
  (proves the wrapper was callable, redteam R2b), or completed.

### Probe 3c (conditional self-call double-executes the body)

```python
prog = (
    "try:\n"
    "    __codemode_main__.count = __codemode_main__.count + 1\n"
    "except:\n"
    "    __codemode_main__.count = 1\n"
    "if __codemode_main__.count == 1:\n"
    "    __codemode_main__()\n"
    "return __codemode_main__.count\n"
)
env = codemode.execute_op(prog)
```

How it works: the first run sets count to 1 via the bare except (the
attribute does not exist yet), then calls itself once; the second run
increments count to 2 and returns it. The function attribute persists
across calls because it lives on the function object, while plain
variables are re-initialized on each run. "count" is an allowlisted
attribute name, so only the dunder-name rejection blocks this.

- PASS: env["status"] == "error" from the scan (dunder rejection). The
  body never runs.
- FAIL: env["status"] == "completed" and env["result"] == 2. That is
  proof the body ran twice (redteam R2c). In a snippet that calls act(),
  double execution means double desktop actions: the same text typed
  twice, the same button clicked twice.

### Probe 3d (yield: body never runs, runner reports success)

```python
env = codemode.execute_op("x = 1\nyield 2\nreturn x")
```

- PASS: env["status"] == "error" and "yield" in env["error"]. The
  program is rejected, never "completed".
- FAIL: env["status"] == "completed" and "generator object" in
  str(env.get("result")). On unfixed code the yield turns the wrapper
  into a generator function, the body never executes, and the runner
  reports success with a non-JSON-serializable generator in the envelope
  (redteam P3).

### Probe 3e (code_exec parity guard: yield already rejected there)

```python
session = code_exec.CodeExecSession(FakeBackend(), session_token=TOKEN)
env = session.run("x = 1\nyield 2")
```

- PASS: env["ok"] is False, error_type "sandbox", "yield" in env["error"].
- FAIL: env["ok"] is True. This should already pass on unfixed code
  (code_exec rejects yield at lines 300-305); it guards against a
  regression while codemode is being fixed.

### Probe 3f (async parity: AsyncFor/AsyncWith rejection)

```python
prog = "async def f():\n    async for x in []:\n        pass\nreturn 1"
env = codemode.execute_op(prog)
```

- PASS: env["status"] == "error" (rejection may come via AsyncFunctionDef
  or via AsyncFor; either is acceptable, the program must never execute).
- FAIL: env["status"] == "completed". Note AsyncFor/AsyncWith can only
  appear inside an async def, which codemode already rejects, so this is
  defense-in-depth parity with code_exec lines 288-297, not a live hole
  on its own. Record which node type produced the rejection.

## Item 4: codemode does not pin __builtins__ (latent full escape)

Fix under test: pin '__builtins__': dict(SAFE_BUILTINS) in codemode's
namespace, exactly as code_exec.py run() does at line 816. One line.

Why this is latent, not live: model code cannot name __builtins__ (it is
banned), and the only demonstrated way to reach it was the format hole
(item 1), which returns strings, not live objects. But the full builtins
(including eval, open, __import__, compile) sit one attribute hop away
inside every function object's __globals__. Any future gap that yields a
globals dict as a live object hands over full builtins. The pin closes
that second hop. Probe 4a is the behavioral test; it works because
returning an op function from execute_op hands the test harness the live
function object, and the harness (outside the sandbox) can inspect its
__globals__.

### Probe 4a (behavioral: op function globals carry only safe builtins)

```python
env = codemode.execute_op("return repo_list_scripts")
assert env["status"] == "completed", env
fn = env["result"]
builtins_value = fn.__globals__.get("__builtins__")
if isinstance(builtins_value, dict):
    leaked = [name for name in ("eval", "open", "__import__", "compile",
                                "getattr", "input", "globals", "locals")
              if name in builtins_value]
else:
    leaked = ["__builtins__ is a module, not a pinned dict: %r" % (builtins_value,)]
assert not leaked, leaked
```

- PASS: env["status"] == "completed", fn is the live op function,
  fn.__globals__["__builtins__"] is a dict, and none of eval, open,
  __import__, compile, getattr, input, globals, locals is in it. The
  pinned dict equals (or is a subset of) codemode.SAFE_BUILTINS.
- FAIL: __builtins__ is the real builtins module (unfixed code: CPython
  inserts the real builtins module into the namespace dict because
  execute_op never pins it), or the dict contains eval, open,
  __import__, or compile. Either FAIL means one live-object hop away
  from full RCE.

### Probe 4b (static guard: the pin line exists in codemode)

```python
import pathlib
src = pathlib.Path("scripts/codemode.py").read_text()
assert "'__builtins__': dict(SAFE_BUILTINS)" in src, "pin line missing"
```

- PASS: the exact pin line is present in execute_op's namespace
  construction (same form as code_exec.py line 816).
- FAIL: the line is absent, or present only in a comment or a dead code
  path. A behavioral pass on 4a with no pin line would be suspicious;
  report both results together.

### Probe 4c (code_exec parity guard: pin already exists there)

```python
import pathlib
src = pathlib.Path("scripts/code_exec.py").read_text()
assert "'__builtins__': dict(SAFE_BUILTINS)" in src, "code_exec pin missing"
```

- PASS: the pin line is present in code_exec.py run().
- FAIL: it is absent. This should already pass on unfixed code; it
  guards against the pin being dropped while the two files are edited
  together.

## Score sheet (for Y1b to fill in)

| Probe | Item | Result (PASS/FAIL) | Evidence (elapsed, error text, or leaked value) |
| 1a | format / codemode class | | |
| 1b | format / codemode globals | | |
| 1c | format / code_exec token | | |
| 1d | format / code_exec dict | | |
| 1e | format / negative controls | | |
| 1f | format / static guard | | |
| 2a | wall / codemode preemption | | |
| 2b | wall / code_exec preemption | | |
| 2c | result cap / codemode 50MB | | |
| 2d | result cap / code_exec 50MB | | |
| 2e | memory / 100MB alloc | | |
| 3a | wrapper / reference | | |
| 3b | wrapper / self-call | | |
| 3c | wrapper / double-exec | | |
| 3d | yield / codemode | | |
| 3e | yield / code_exec parity | | |
| 3f | async / parity | | |
| 4a | builtins pin / behavioral | | |
| 4b | builtins pin / codemode static | | |
| 4c | builtins pin / code_exec static | | |

Phase A verdict rule: all probes 1a-1f, 2a-2d, 3a-3f, 4a-4c must PASS.
Probe 2e is the single exception: if 2a-2d pass via a signal timer only
and 2e FAILS, record it as residual risk with the exact failure (not as
a silent pass), and let the Y1b panel judge whether that blocks Phase A
or rides as a documented limitation. Any other FAIL blocks Phase A.
