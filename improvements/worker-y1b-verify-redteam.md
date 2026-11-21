# Redteam report: Y1b verification probes (Worker Y1b panel)

Date: 2026-11-21. Author: Redteam (subagent of Worker Y1b). Branch: todolist-push.
Repo: ~/workspace/computer-use-wayland.
Scope: attack the verification PROBES, not the code. Read-only on all code;
only this report file was written. No laptop touched, no network, no ydotool.

Sources attacked:
- improvements/worker-y1b-verify-council-1.md (20 probes: items 1-4)
- improvements/worker-y1b-verify-council-2.md (35 probes: items 5-8)
- improvements/worker-y1b-verify-council-3.md (35 probes: items 9-12 plus Phase C)
- improvements/worker-y1-redteam.md (the BLOCK report the probes must cover)
- scripts/code_exec.py, scripts/codemode.py (pre-Codex baseline, for citations)
- tests/test_code_exec.py, tests/test_cursor_session.py (for C1-C5 checks)

Method: for each probe I tried to defeat it three ways: (a) find an attack
variant the probe does not cover, (b) find a setup the probe assumes but the
real code does not guarantee, (c) find a PASS criterion a still-vulnerable
implementation could satisfy, or a correct fix it would fail. Every HIGH
below is proved with a runnable experiment (script /tmp/redteam-y1b-probes.py
on the VM, plus inline runs quoted) or a precise code citation, never a vague
worry. Experiment outputs are quoted in the relevant sections.

## Verdict counts

90 probes attacked. 86 GAP, 4 HOLDS.

- HIGH: 21 gaps. The probe passes while the vulnerability remains, or fails
  a correct fix so the item can never pass.
- MEDIUM: 50 gaps. The probe is weaker than its own PASS text, tests the
  wrong thing, or misses a variant that matters.
- LOW: 15 gaps. Fragile wording, missing boundary, prose-only leg.
- HOLDS: 4 probes (1c, 1d, 4c, 7c). These do what they claim.

Severity rule used: HIGH means the probe either certifies a hole (passes a
vulnerable implementation) or blocks a correct fix (fails it). MEDIUM means
the probe can be satisfied for the wrong reason, or misses a live variant.
LOW means it is fragile or incomplete but its core check is sound.

## Sharpest gap: probe 10b cannot tell a shared deadline from a fresh one

Probe 10b (council 3) is supposed to catch the headline budget
amplification: a nested run_snippet that resets the wall deadline, giving
up to 16 minutes of wall time from one program. Its program is:

```
run_snippet("slow-act")
run_snippet("slow-act")
```

with a 2s outer wall and a snippet that sleeps 0.6s per act, 6 acts.
The probe expects the second call to add ~0 backend acts.

It cannot work. A code_exec program ABORTS on the first error: the first
snippet hits the 2s wall (shared or fresh, the timing is identical, about
1.8s to the 4th act pre-check) and raises, so the outer program never
reaches the second line. Proven on the VM against current code_exec.py:

```
env = session.run('assert_state(False, "boom")\nx = 1')
# ok False, error 'assert failed: boom', x never set
```

With a SHARED deadline the first snippet fails at ~2s and the outer run
aborts. With a FRESH deadline per snippet the first snippet ALSO fails
at ~2s (its own fresh 2s budget against 3.6s of sleeps) and the outer
run aborts. Identical observable behavior: elapsed ~2s, ok False, second
call never executes, backend act count the same. The probe PASSES the
vulnerable implementation. It certifies the exact amplification it was
written to catch.

Stronger probe 10b: make the snippet complete inside a fresh budget but
exceed the outer remaining budget, for example outer program sleeps 1.5s
of API work first, then the snippet does 1.0s of acts with wall_seconds=2.
Shared deadline refuses (1.5 + 1.0 > 2). Fresh deadline runs it. Or wrap
the first call in try/except so the second call actually executes, and
assert the second call fails immediately on the expired outer deadline
with ~0 new backend acts. Either shape distinguishes the two. The same
structural flaw hits probe 10f (see below).

## Per-probe verdicts

### Council 1: items 1-4 (20 probes)

| Probe | Verdict | One line |
| 1a | GAP MEDIUM | Vacuous pass under module-level execution; fragile "class" substring |
| 1b | GAP LOW | Same vacuous pass (uses return); otherwise sound |
| 1c | HOLDS | Token leak probe is sound as written |
| 1d | HOLDS | Session dict dump probe is sound as written |
| 1e | GAP HIGH | Broken: fails a correct fix, codemode leg passes only while Attack 4 is live |
| 1f | GAP LOW | Static set check only; does not pin format_map/__format__ out |
| 2a | GAP HIGH | "wall-clock" error text rejects valid child-process timeouts; one C shape only; cancel untested |
| 2b | GAP HIGH | Same error-text and single-shape gaps as 2a |
| 2c | GAP MEDIUM | Silent truncation accepted as PASS; return value only |
| 2d | GAP HIGH | Aggregate envelope blowup proven: two 40KB vars pass a per-value cap |
| 2e | GAP MEDIUM | 100MB alloc finishes in 0.27s, wall can never fire; measures neither time nor memory |
| 3a | GAP HIGH | Demands "dunder" in error; delete-from-namespace and random-suffix fixes give NameError |
| 3b | GAP HIGH | Same NameError gap as 3a |
| 3c | GAP HIGH | Same NameError gap; vacuous pass under module-level execution |
| 3d | GAP MEDIUM | Tests yield only; yield from is live and untested |
| 3e | GAP LOW | No YieldFrom leg in code_exec either |
| 3f | GAP LOW | Defense-in-depth only; uses return, vacuous under module-level execution |
| 4a | GAP HIGH | False premise: op function globals are module globals, pin cannot change them |
| 4b | GAP MEDIUM | Exact-string match rejects three identical spellings |
| 4c | HOLDS | Static pin guard for code_exec is sound as written |

#### 1a (GAP MEDIUM): vacuous pass under module-level execution

Probe 1a uses `return "{0.__class__}".format("")`. The redteam fix list
allows executing model code at module level (the way code_exec does).
Under module-level execution, `return` at top level is a SyntaxError
("'return' outside function"), so the program never runs, the error
contains no "class", and probe 1a PASSES without ever testing whether
format was removed. The same vacuous pass hits 1b, 3a, 3b, 3c, 3f, all of
which use `return`. Stronger probe: use assignment form, no return:

```python
env = codemode.execute_op('x = "{0.__class__}".format("")')
# PASS only if status error naming format AND x was never assigned
# (assert no completed status and no "<class 'str'>" anywhere)
```

Second gap: PASS requires `"class" not in str(env)`. Any fix whose error
message mentions the word "class" (for example "dunder attribute access
on class object") fails the probe spuriously. Check the error for the
format rejection specifically, not for a substring of the whole envelope.

#### 1e (GAP HIGH): broken negative control, inverted by the item 4 fix

Probe 1e asserts legitimate formatting still works:

```python
env = codemode.execute_op('x = f"{len(chr(65))}"; return x')
```

`chr` is NOT in SAFE_BUILTINS in either file. Proven on the VM:

```
chr in codemode.SAFE_BUILTINS: False
chr in code_exec.SAFE_BUILTINS: False
codemode f-string probe: {'status': 'completed', 'result': '1'}
code_exec f-string probe: {'ok': False, 'error': "name 'chr' is not defined", 'error_type': 'NameError'}
```

The code_exec half FAILS on unfixed code and on fixed code alike, because
code_exec pins builtins (line 816) and chr is not in the pinned dict.
Nothing in the must-fix list adds chr to SAFE_BUILTINS, so probe 1e
FAILs a correct fix.

Worse, the codemode half passes ONLY because of the Attack 4 hole:
codemode does not pin __builtins__, so CPython inserts the real builtins
and `chr` resolves through them. Fixing item 4 (pinning) makes the
codemode half FAIL too. Probe 1e punishes the item 4 fix it is supposed
to coexist with. Stronger probe, using only builtins that ARE allowlisted:

```python
env = codemode.execute_op('x = f"{len(\"ab\")}"; return x')   # expect '2'
env2 = codemode.execute_op('x = "%s-%d" % ("ok", 1); return x')  # expect 'ok-1'
```

#### 2a / 2b (GAP HIGH): error-text narrowness plus one C shape only

Both probes require "wall-clock" in the error (or an upfront refusal
naming the refused construct). A correct child-process implementation
that kills the run and reports "timed out after 2s" or "killed" FAILS
both probes, even though it is the redteam's own recommended fix
(signal timer OR child process with kill). The PASS text names only one
of the two sanctioned implementations. Stronger PASS: accept any error
naming timeout, wall-clock, killed, or deadline, or an upfront refusal.

Second gap: only one C-level shape is tested, `sum(range(3 * 10**8))`.
A fix that refuses or interrupts that shape (for example a static scan
rejecting `sum(range(...))` with a large literal) passes while other
C-level work sails through. Untested shapes, all of which also fire no
line events until they return:

```python
x = list(range(10**8))        # C-level list build
x = sorted(range(10**7))      # C-level sort
x = "A" * (10**8)             # C-level repeat, 0.27s for 100MB (see 2e)
x = "ab".join(["cd"] * 10**7) # C-level join
x = 2 ** 1000000              # C-level big-int pow
```

Stronger probe: run at least three shapes (sum/range, list/range,
str-repeat) with wall_seconds=2 and require each to stop near 2s or be
refused up front.

Third gap, whole panel: NO probe anywhere tests cancellation during
C-level work. Attack 2 states the cancel latch goes deaf during a C
loop (check_cancel runs in the tracer and in _api, neither fires mid-C).
A signal-timer fix interrupts on wall time but need not interrupt on
cancel; a child-process fix need not kill on cancel. Grep for 'cancel'
across all three council files finds only the word inside
"check_cancel" in probe 1d and the Phase C patch list. Stronger probe:
set a check_cancel that raises after 0.5s, run `sum(range(3 * 10**8))`,
require the run to stop near 0.5s with a cancel error, not run to
completion.

#### 2c (GAP MEDIUM): silent truncation accepted as PASS

Probe 2c passes if the run completes with `len(env["result"]) <= 65536`.
A fix that silently truncates a 50MB result to 64KB passes, handing the
supervisor cut data as if it were complete. A program that then asserts
on the truncated content can pass or fail wrongly, and nothing in the
envelope says data was cut. Stronger probe: require either an error
naming result size, or a completed envelope carrying an explicit
truncation marker (for example a `truncated: true` field or a stated
limit), never a silent cut. Also test the print/log path, not only the
return value.

#### 2d (GAP HIGH): aggregate envelope blowup

Probe 2d tests one 50MB variable. A per-value 64KB cap passes it while
the envelope still blows up through many sub-cap values. Proven on the
VM against current code_exec.py:

```python
env = session.run('x = "A" * 40000\ny = "B" * 40000')
# ok True, len(x) 40000, len(y) 40000, len(json.dumps(env)) 80108
```

Two 40KB variables, each under a 64KB per-value cap, produce an 80,108
byte envelope. Ten such variables produce ~400KB; fifty produce ~2MB
handed to the supervisor. The cap must bind the serialized envelope,
not each value. Stronger probe:

```python
prog = '\n'.join('v%d = "A" * 40000' % i for i in range(5))
env = session.run(prog)
blob = json.dumps(env)
# PASS only if ok False naming size, or len(blob) <= 70000
```

Also require truncation to be signalled (see 2c), and test the log path:
`print("A" * 40000)` five times fills log_lines the same way, and probe
2d's blob check would catch it only if the print path is exercised.

#### 2e (GAP MEDIUM): fast allocation, no memory measurement

Probe 2e runs `x = "A" * (10**8)` with wall_seconds=2 and expects an
error. Measured on the VM: status completed, elapsed 0.27s. The 100MB
allocation finishes long before any 2s wall timer can fire, so the probe
does not test the wall at all, and it measures no memory (no RSS or
tracemalloc check anywhere). Its own text admits it may FAIL on a
signal-only fix and be recorded as residual risk, which means the probe
conflates two properties (time and memory) and resolves the conflict by
waving it through. Stronger probe: measure RSS before and after (or run
under a tracemalloc budget), and add a post-check that a trivial program
still runs afterwards (proving the process stayed alive). Or use a slow
allocation that actually crosses the wall.

#### 3a / 3b / 3c (GAP HIGH): NameError has no "dunder" in it

All three probes demand "dunder" in the error (3a: `"dunder" in
env["error"]`, 3b/3c: same dunder rejection). But the redteam fix list
allows three ways to make the wrapper unreachable: reject dunder names
in the scan, delete the wrapper from the namespace after exec, or name
it with a random unguessable suffix per execution. The second and third
produce a NameError, not a dunder error. Proven on the VM:

```python
codemode.execute_op('return __nonexistent__')
# {'status': 'error', 'error': "NameError: name '__nonexistent__' is not defined"}
```

No "dunder" appears. So probes 3a/3b/3c FAIL two of the three sanctioned
fixes. Stronger PASS for 3a/3b/3c: accept any error (scan rejection OR
NameError) provided no function object leaks anywhere in the envelope
and the body never executes (prove the last part with a side-effect
marker: a program that would set a variable or print if it ran, and
assert the marker is absent). Do not tie PASS to one error string.

#### 3d (GAP MEDIUM): yield from untested

Probe 3d tests `yield 2` only. `yield from` is the same hole and is not
tested. Proven on the VM, both produce a completed envelope with a
generator and a body that never ran:

```python
codemode.execute_op('x = 1\nyield 2\nreturn x')
# {'status': 'completed', 'result': <generator object __codemode_main__ ...>}
codemode.execute_op('x = 1\nyield from []\nreturn x')
# {'status': 'completed', 'result': <generator object __codemode_main__ ...>}
```

A fix that rejects Yield but forgets YieldFrom passes 3d while the hole
stays open. Stronger probe: add the `yield from []` variant, and require
the error to name yield in both.

#### 4a (GAP HIGH): false premise about whose globals these are

Probe 4a returns an op function and inspects
`fn.__globals__["__builtins__"]`, expecting the pinned dict. That is the
wrong globals dict. `repo_list_scripts` is `_op_list_scripts`, defined
at codemode module top level, so its `__globals__` is the codemode
MODULE globals, which CPython fills with the real builtins on import.
The execute_op namespace pin cannot change module globals. Proven:

```python
env = codemode.execute_op('return repo_list_scripts')
fn = env['result']
type(fn.__globals__.get('__builtins__'))  # <class 'dict'>
[n for n in ('eval', 'open', '__import__', 'compile')
 if n in fn.__globals__['__builtins__']]  # ['eval', 'open', '__import__', 'compile']
```

Probe 4a FAILS on fixed code exactly as it fails on unfixed code: the
pin line can never change what this probe measures. Item 4 would be
unverifiable forever under this probe. The correct behavioral probe uses
a MODEL-DEFINED function, whose globals ARE the exec namespace. Proven
on unfixed code, the shape works:

```python
env = codemode.execute_op('def f():\n    pass\nreturn f')
fn = env['result']
type(fn.__globals__.get('__builtins__'))  # <class 'dict'>
'eval' in fn.__globals__['__builtins__']  # True on unfixed code
```

Stronger probe 4a: return a model-defined function, assert its
`__globals__["__builtins__"]` is a dict equal to (or a subset of)
SAFE_BUILTINS with no eval, open, __import__, compile, getattr, input,
globals, locals. On fixed code the pin makes that dict the pinned one.

#### 4b (GAP MEDIUM): exact-string match rejects identical spellings

Probe 4b asserts `"'__builtins__': dict(SAFE_BUILTINS)" in src`. Three
semantically identical spellings all fail that check (verified by string
comparison on the VM):

```python
'"__builtins__": dict(SAFE_BUILTINS)'                       # double quotes
"namespace['__builtins__'] = dict(SAFE_BUILTINS)"           # item assignment
"namespace.update(__builtins__=dict(SAFE_BUILTINS))"        # update call
```

Stronger probe: use the fixed behavioral 4a above as the real check, and
a regex for the pin (`__builtins__.*dict\(SAFE_BUILTINS\)`) as the static
check, never an exact string.

### Council 2: items 5-8 (35 probes)

| Probe | Verdict | One line |
| 5a | GAP MEDIUM | Verdict ignores backend.act_calls; error need not name snippet/hash |
| 5a2 | GAP MEDIUM | Manifest cached at import makes the hashless entry invisible (spurious pass); hash field name assumed |
| 5a3 | GAP HIGH | Counting window covers run_snippet only; load-hash plus exec-read passes |
| 5b1 | GAP MEDIUM | Cached manifest makes collisions invisible; repo.list_scripts omitted from the loop; search untested |
| 5b2 | GAP HIGH | Runtime crash counted as load rejection; post-call windows() check is vacuous |
| 5c | GAP MEDIUM | Any refusal passes, not just approval; return-out and two-snippet exfil untested |
| 5c-laptop | GAP LOW | Prose only, no runnable steps |
| 5d | GAP MEDIUM | validate_program second leg is prose, not code; missing-param refusal passes vacuously |
| 6a1 | GAP LOW | entries[0] approval risk; .git removal is a no-op in temp_tree |
| 6a2 | GAP MEDIUM | Hardcodes pre-Codex api_windows source shape; crashes instead of verdicting if Codex refactored it |
| 6a3 | GAP LOW | Grep leg for rev-parse/git/subprocess is prose, not code |
| 6b1 | GAP HIGH | Remove-first fix cannot pass against a FakeBackend that models no filesystem effects; regex may find nothing |
| 6b2 | GAP MEDIUM | Uses entries[0], not a window-picking snippet; zero-match variant is prose only |
| 6c1 | GAP MEDIUM | Search exclusion explicitly optional, contradicting its own PASS text; loads mod before editing manifest |
| 6c2 | GAP HIGH | Future date and stale API confounded; future-date bypass never tested alone |
| 6c3 | GAP LOW | Inherits 6c1 gaps; marked foldable into 6c1 |
| 6d-VM | GAP HIGH | Replace branch likely makes a syntax break, not a behavior break; breaks entries[0] regardless of live_only; no crash-safe restore |
| 6d-laptop | GAP LOW | Prose only |
| 7a1 | GAP MEDIUM | second_ok computed but never used; recorded-result check looks for 'r', snippet sets 'result' |
| 7a2 | GAP MEDIUM | Ledger key need not include code hash; state-file persistence across sessions untested |
| 7a3 | GAP MEDIUM | Existence check, not coverage; marked entry called with no params |
| 7a-live | GAP LOW | Prose only |
| 7b | GAP MEDIUM | No no-navigation control; blanket refusal on all dom_act would pass |
| 7b-live | GAP LOW | Prose only |
| 7c | HOLDS | Validated against unfixed code, flips on fix, counts backend acts |
| 7c2 | GAP MEDIUM | Prose only, no runnable code at all |
| 8a1 | GAP MEDIUM | Hardcoded name 'p1-terminal-df'; any ok=False passes, not just manifest errors |
| 8a2 | GAP MEDIUM | Logged warning and search exclusion unchecked; only params-as-string tested |
| 8b | GAP MEDIUM | Dict-form duplicate never created (dict assignment overwrites); CI grep leg is prose |
| 8c1 | GAP MEDIUM | Code defaults to 1048576, contradicting its own "FAIL if no cap constant"; 'manifest' substring too broad |
| 8c2 | GAP MEDIUM | Verdict is bare ok=False; error need not name the size cap |
| 8d | GAP HIGH | One inner call per snippet cannot prove inner calls are charged; wall leg is prose and self-contradictory |
| 8e | GAP MEDIUM | Grep runs on the temp tree, which has no tests/ and one script; pattern misses spec_from_file_location |
| 8f | GAP HIGH | Hash not updated for traversal targets; read counter misses os.open and relative paths; flags legitimate reads |
| 8g | GAP MEDIUM | Leg2 allows a default-valued param leak; explicit-param leg is prose, not code |

Systematic gap across council 2: the harness loads the module BEFORE
the probe edits the manifest (5a2, 5b1, 6c1, 8a1, 8a2, 8b, 8c1 and
others all do `mod = H.load_code_exec(tree)` then `H.write_manifest`).
If the loader reads the manifest once at import and caches it, every
fixture edit is invisible: added entries are "unknown" (ok=False, which
most verdicts accept as a pass) and edited dates/hashes are never seen
(which makes 6c1 fail spuriously). The harness never verifies the loader
re-reads the manifest per call. Stronger harness: after every manifest
edit, reload the module in a fresh import (or assert a re-read by
changing a description and observing it), and record which loading mode
the implementation uses.

#### 5a3 (GAP HIGH): the counting window misses the real TOCTOU

Probe 5a3 monkeypatches Path.read_bytes and counts reads of the snippet
file DURING one run_snippet call, expecting at most 1. But the TOCTOU
hole is hash-at-load plus read-again-at-execution: the load-time read
happens OUTSIDE the counting window. Simulated loader, run on the VM:

```python
# loader hashes at load (outside the window), reads again at exec (inside)
reads_during_run = 1   # probe 5a3 verdict: PASS, at most 1
total reads overall = 2  # hash at load plus read at exec, edit between them runs unverified
```

A loader that hashes at manifest load and re-reads the file at execution
passes 5a3 while the hole stays open. Also 0 reads passes (a loader that
refuses everything, or serves from a stale cache, reads nothing), because
the probe has no positive control. And the probe itself admits it
undercounts when the loader uses open() rather than Path.read_bytes.
Stronger probe: count reads from manifest load through execution (start
counting before the loader first touches the file), require the envelope
to be ok True on the untampered control, and assert the executed bytes
equal the hashed bytes by editing the file between load and execution
and requiring refusal.

#### 5b2 (GAP HIGH): two vacuous legs

First, the probe conflates load rejection with a runtime crash. The
verdict is `refused = (not env['ok']) and len(act_calls) == 0`. If the
loader ACCEPTS the colliding param and the snippet runs, its own
`windows()` call hits the string 'pwned' and raises TypeError inside
the snippet: ok False, zero acts. The probe then verdicts True with the
message "param named windows rejected at load", which is false. It never
was rejected at load; it crashed at runtime. The probe cannot tell the
two apart because it never inspects the error for a load/collision
reason and never inspects what the snippet did internally.

Second, the defense-in-depth leg is vacuous. The probe runs a later
program calling `windows()` and expects it to still resolve to the API.
It always will. code_exec.py run() builds the namespace as
`namespace = dict(self.variables)` and then `namespace.update({...,
'windows': self.api_windows, ...})` (code_exec.py run(), lines 814-831
in the baseline).
API names overwrite any persistent variable of the same name on every
run. Proven on the VM:

```python
session.variables['windows'] = 'pwned'
session.run('w = windows()\nassert_state(len(w) == 1, "windows shadowed")')
# ok True, w is the real FakeBackend window list
```

A poisoned persistent variable can never shadow the API in the next
program, so this leg can never fail. The real shadowing symptom lives
INSIDE the snippet (its own windows() call hitting the param), and the
probe never observes it. Stronger probe: give the shadowing snippet a
body that records which windows() it called (for example set
`out = str(type(windows))` or call windows() and store the result), and
assert on the snippet's own envelope variables, not on a later program.
Drop the post-call leg entirely. The same two flaws hit council 3 probe
11b.

#### 6b1 (GAP HIGH): the remove-first fix cannot pass this probe

Probe 6b1 pre-creates the P3/P4 assert targets, then runs the snippet
with a FakeBackend whose act() returns ok True but creates nothing on
disk, and expects ok False. The redteam fix allows two shapes: remove
the target first, or use a fresh unique path per run. Only the second
can pass here. A snippet that correctly removes the target first does so
through act() (typing `rm -rf ...` into the terminal), and the
FakeBackend does not model shell effects, so the pre-created dirs are
still there at assert time and the asserts pass: ok True, probe FAILS a
correct fix. The harness HAS a RefusingBackend, but 6b1 does not use a
modeling backend at all. Stronger probe: use a backend that models the
shell (execute mkdir/rm/printf effects on /tmp, as
tests/test_code_exec.py FakeShellBackend does), or split the probe in
two: one for the fresh-path shape (current probe, valid for that shape
only) and one for the remove-first shape (assert the snippet's act calls
contain a removal of the exact target before the assert). Also the probe
never checks its regex found anything: if the snippet uses single quotes,
variables, or different spacing for its assert paths, zero paths are
pre-created and the asserts fail for the wrong reason, so ok False
passes vacuously. Assert at least one path was pre-created before
running.

#### 6c2 (GAP HIGH): confounded variables, future-date bypass untested

Probe 6c2 sets last_verified to today plus 365 days AND mutates the
runtime API (6a2 shape), then expects refusal. A loader that accepts
future dates as fresh (negative age, never expired) still refuses here,
because the API is stale. The probe PASSES a future-date bypass. The
bypass is never tested alone anywhere in the panel (council 3 probes
12a/12b also never use a future date). Anyone hand-editing the manifest
can set last_verified to 2099 and re-authorize a stale snippet, as long
as the runtime hash matches, and no probe catches it. Stronger probe:
future last_verified plus FRESH runtime hash, expect refusal (date in
the future is invalid, fail closed) or at least a recorded finding.
Second flaw: the API mutation is conditional (`if old_def in text...`)
with no else. If Codex refactored api_windows, the mutation is silently
skipped, the API is fresh, the future date is accepted, the snippet runs,
and the probe FAILs for a reason that has nothing to do with the fix.
Make the mutation unconditional (fail the probe setup loudly if the
source shape changed) instead of silently skipping it.

#### 6d-VM (GAP HIGH): syntax break, wrong target, unsafe restore

Three flaws. First, the break is likely a SYNTAX break, not a behavior
break. The replace turns `assert_state(result["ok"]` into
`assert_state(result["ok"] and False, "y1b-break` plus the remainder of
the original line, opening a string quote that the remainder closes
unpredictably. If the result does not parse, tests/test_snippets.py
fails at the py_compile leg, not at execution, and the probe cannot
tell the difference: its PASS criterion is only exit non-zero, and the
tail -5 is printed but never asserted. It does not prove CI executes
live_only snippets. Use only the fallback shape (append
`assert_state(False, "y1b-break")` at the end), which is a pure behavior
break, and assert the failure mentions the snippet name or the
expected_result check.

Second, it breaks entries[0] regardless of live_only. If entries[0] is
VM-verifiable, the suite failing proves nothing about live_only
execution, which is the whole point of the probe. Select a live_only
entry explicitly.

Third, it mutates the REAL worktree (snippet file plus manifest) with no
trap and no verification of the restore. If the unittest run hangs or
the script is killed, the tree stays broken and re-hashed. Add
`trap restore EXIT`, and verify the restore by comparing sha256 before
and after instead of printing git status.

#### 7a1 (GAP MEDIUM): second_ok is dead code, wrong variable name

The probe computes `second_ok` (second run returns the recorded result
or an already-applied refusal) and then never uses it: the verdict is
only `first['ok'] and acts_after_second == acts_after_first`. A second
run that errors for an unrelated reason (NameError, budget) with zero
new acts PASSES, even though it returned neither the recorded result
nor an already-applied refusal. And the recorded-result check itself is
broken: it looks for `second['variables']['r']`, but the fixture snippet
never sets `r`; it sets `result` (the act result dict). So the
recorded-result leg could never be true. Stronger probe: assert
`second['variables']['result'] == first['variables']['result']` OR
'already applied' in the second error, and use that in the verdict.

#### 8d (GAP HIGH): one inner call cannot prove inner calls are charged

Probe 8d loops 40 run_snippet calls, each doing exactly one windows()
call, with the default 32-call budget. If run_snippet itself costs 1 API
call, the 40 iterations exhaust the budget on run_snippet calls alone
(about 16 iterations in, 16 run_snippet plus 16 windows), and the probe
PASSES even if inner calls are never charged (a reset-plus-restore
implementation that gives each snippet a fresh budget). The probe cannot
distinguish "inner calls charged" from "only run_snippet calls charged".
Council 3 probe 10a is stronger (2 inner calls per snippet, cap 6), but
neither probe states whether run_snippet itself costs budget, so the
accounting contract is ambiguous and two different accountings both
pass. Stronger probe: use a snippet doing 2 inner calls with
max_api_calls=6 (as in 10a) AND check the outer counter is preserved
after the snippet returns (outer does N calls, snippet does M, outer
does more; the total charged must be N plus M plus the rest). Also the
wall-clock second leg is prose only, and its sentence contradicts
itself: "If the fixed code only documents the wall budget as post-hoc,
Y1b records that and this leg passes only if the call is refused up
front or interrupted near the deadline." A post-hoc-only implementation
does neither, so the leg fails; "records that" does not rescue it.
Write the wall leg as runnable code or drop it.

#### 8f (GAP HIGH): hash, counter, and path handling all defeat it

Four flaws. First, the evil entries keep the FIRST entry's sha256 while
pointing code_path at a traversal target, so a hash-check-first loader
refuses for hash mismatch and the probe PASSES without ever testing
containment. Set the sha256 to the traversal target's hash so only
containment can refuse.

Second, the outside-read counter patches builtins.open,
Path.read_bytes and Path.read_text, but not os.open, io.open,
Path.open, or a cached open reference. A loader reading via os.open
bypasses the counter entirely.

Third, `_is_outside` returns False for any non-absolute path, so a
loader that opens '../code_exec.py' relative to the working directory
is never counted, even though the resolved file is outside snippets/.

Fourth, the counter flags LEGITIMATE reads: a loader that reads
scripts/code_exec.py to compute the runtime API hash performs an
"outside snippets/" read on every call and would FAIL this probe
spuriously. The counter should watch only the traversal targets, not
any outside file.

Fifth, most traversal targets do not exist (from top-level snippets/,
'../code_exec.py' resolves to a nonexistent repo-root file), so refusal
is for a missing file, not containment. Only the symlink case points at
a real file. Make every traversal target exist with distinctive
marker content, and assert the marker was never read or executed.

#### 8b (GAP MEDIUM): dict-form duplicate is never created

The list-form leg is sound, but the dict-form leg is not implemented.
The code does `entries[first['name']] = evil` on a Python dict, which
OVERWRITES the original entry. A Python dict cannot hold duplicate
keys, so by the time the manifest is written there is no duplicate at
all: the probe tests replacement, not duplication. Testing JSON
duplicate keys requires writing RAW JSON text with the same key twice
(string manipulation of the manifest file), which the probe never does.
Also the verdict does not check the refusal names the duplicate (any
ok=False passes), and the CI leg (grep tests/test_snippets.py for a
uniqueness test) is prose, not in the code block.

### Council 3: items 9-12 plus Phase C (35 probes)

| Probe | Verdict | One line |
| 9a | GAP MEDIUM | Cap hardcoded 1048576 vs "cap from 0.2"; loader call is a placeholder; hash-first refusal passes vacuously |
| 9b | GAP MEDIUM | Contradicts 9c on whole-registry vs per-entry rejection; no runnable code; no log location |
| 9c | GAP MEDIUM | No listing entry point defined; load-skip vs run-refuse ambiguous; caching assumption |
| 9d | GAP MEDIUM | Caching makes malformed fixture invisible (vacuous pass) or breaks import (order unspecified) |
| 9e | GAP HIGH | Load-time vs execute-time rejection is unobservable; most traversal targets do not exist |
| 9f | GAP MEDIUM | sys.modules check runs in a fresh process that never ran a snippet; grep misses spec_from_file_location |
| 9g | GAP LOW | No boundary test; chars vs bytes unspecified |
| 9h | GAP MEDIUM | TOCTOU check is manual source inspection, not a probe; no case-sensitivity test |
| 10a | GAP MEDIUM | Prose only; envelope-vs-backend cross-check not in code; accounting ambiguous |
| 10b | GAP HIGH | Broken by construction: outer program aborts, second call never executes in either implementation |
| 10c | GAP MEDIUM | Mutual recursion A-B-A untested; exception-path depth counter leak untested; load-vs-run timing |
| 10d | GAP MEDIUM | Grep catches literal spellings only; no tripwire on CodeExecSession.__init__ |
| 10e | GAP HIGH | Contradicts 11d/8g: demands inward visibility and outward isolation without stating the mechanism |
| 10f | GAP HIGH | Snippet alone exceeds the budget, so shared and reset counters both trip; cannot distinguish them |
| 11a | GAP MEDIUM | Name collisions tested for windows/act only; builtin-param collisions untested; prose only |
| 11b | GAP MEDIUM | Post-call windows() check vacuous (same as 5b2); control inconsistent with 11e |
| 11c | GAP MEDIUM | Required/unknown/type param cases untested; outer-program namespace after the call untested |
| 11d | GAP MEDIUM | Declared-output mechanism optional, so PASS is conditional; exception-path restore untested |
| 11e | GAP MEDIUM | Outer bindings not checked for restore after snippet exit; guessed observation id untested |
| 11f | GAP MEDIUM | Bare snippet body unspecified (undefined name gives vacuous pass); dom_calls filtering unspecified |
| 11g | GAP MEDIUM | Restore after exit untested; duplicates 11e with two snippets |
| 11h | GAP MEDIUM | String params only; no valid-expression payload; keyword/collision param names untested |
| 12a | GAP MEDIUM | 1-day margin fragile across timezones; search half untestable if no search exists; fresh control has no side-effect check |
| 12b | GAP LOW | Inherits 12a gaps |
| 12c | GAP LOW | Pure-Python partial execution before the age check is invisible to the backend counter |
| 12d | GAP HIGH | Assumes allow_stale is a run_snippet parameter; logging location unspecified |
| 12e | GAP MEDIUM | Compares manifest bytes, not the last_verified value; grep cannot tell reads from writes |
| 12f | GAP MEDIUM | Search entry point ambiguous; "stale, not runnable" section is a judgment call |
| 12g | GAP MEDIUM | Bootstrap paradox untested; load-skip gives "unknown" error, not stale; non-string dates untested |
| 12h | GAP MEDIUM | Only two string shapes; non-string and datetime-with-time untested; load-skip ambiguity |
| C1 | GAP LOW | py_compile redundant with import; no env-dependency check |
| C2 | GAP MEDIUM | grep -c counts lines, not tests; no timeout; assumes at most one legitimate skip |
| C3 | GAP MEDIUM | Manual review, not a probe; assert count via grep -c counts lines, not statements |
| C4 | GAP MEDIUM | Depth function omits while/class and counts across function boundaries; compares file max, not the target function |
| C5 | GAP HIGH | Compares a 2-module run against the full-suite baseline; g++ error attributed to the wrong module; scope too narrow |

#### 9e (GAP HIGH): the load-time requirement is unobservable

Probe 9e requires traversal entries to be "rejected at load (never
executed...)", and states that "a rejection that happens only at
execution time after the file was already read as code counts as FAIL
if the file content was loaded into the process". But the probe only
checks the `pwned` variable. A loader that reads the file, then refuses
at execution without executing it, leaves pwned unset and PASSES, even
though the probe text says that is FAIL. There is no read counter (unlike
council 2 probe 8f, which at least attempts one, and it is flawed). The
load-time requirement cannot be tested by this probe as written. Add the
8f-style read counter (fixed per the 8f findings) or drop the load-time
claim. Second flaw: most traversal targets do not exist. The probe puts
a marker file at /tmp/y1b-fixtures/9e/evil.py, but the traversal entries
point at '../outside.py' and 'subdir/../../outside.py', which do not
exist, so refusal is for a missing file, not containment. Only the
symlink case points at a real evil file. Make every traversal target
exist with marker content. Third: absolute-path-inside-registry is
untested (redteam says reject absolute paths; the probe only tests
absolute-outside).

#### 10f (GAP HIGH): same structural flaw as 10b

Probe 10f runs a snippet that loops 25000 times against a 20000-step
budget and expects failure. A reset-per-snippet counter also trips,
because the snippet ALONE exceeds the budget. Simulated on the VM:

```python
# shared counter: 'trace step budget exceeded at step 20001'
# reset-per-snippet counter: 'trace step budget exceeded at step 20001'
```

Identical. The probe cannot distinguish shared from reset trace budgets.
It also specifies no instrumentation to observe the step count
(session._trace_steps after the run is never mentioned). Stronger probe:
outer program does 15000 steps, snippet does 10000, each alone under the
20000 cap, total 25000 over it. Shared counter refuses; reset counter
runs both to completion. Assert on session._trace_steps and on the
envelope.

#### 10e (GAP HIGH): contradicts 11d and 8g without stating the mechanism

Probe 10e demands the snippet SEE outer variables (terminal_title set by
the outer program). Probes 11d and 8g demand the snippet's writes NOT
leak out (snapshot and restore). Both can hold only under one specific
mechanism: execute inline in a shared namespace, snapshot on entry,
restore on exit. Neither council 3 nor council 2 ever states that
mechanism as the contract. A Codex implementation that isolates both
directions (fresh namespace seeded with params only) fails 10e. One that
shares both directions (no snapshot/restore) fails 11d and 8g. The panel
demands a mechanism it never specifies, so Y1b has no principled way to
judge an implementation that picks either coherent side. State the
mechanism in the contract (shared-read plus snapshot/restore on exit,
including on the exception path), and add the missing probe: a snippet
that WRITES a variable the outer program then reads mid-run must not
affect the outer program's read or its branch. 11d only checks
session.variables after the outer run ends, not a mid-run read.

#### 12d (GAP HIGH): allow_stale interface assumed, logging location unspecified

Probe 12d calls `run_snippet("live-stale", allow_stale=True)`. That
assumes allow_stale is a named parameter of run_snippet, distinct from
snippet params. If Codex implements run_snippet as
run_snippet(name, **params), then allow_stale=True is passed as a
SNIPPET PARAM named allow_stale: it is either ignored (snippet still
refuses for stale, probe FAILs) or bound as a variable (snippet runs
with an extra param, probe behavior undefined). The probe FAILs an
implementation whose override exists through another path (a session
flag, an env var, a separate verifier call). Specify the override
interface in the contract first, or probe it through the interface Codex
actually exposes (recorded in 0.2 surface discovery) instead of
hardcoding a call shape. Second, the logging check ("log_lines contain
'stale' and 'live-stale', or a log record/file entry does") names no
location: session.log_lines, envelope log, a file, stderr, or a logger
are all different places, and the probe does not say which one to read.
Third, the manifest-field variant assumes the override is call-time
only; if Codex implements per-snippet allow_stale in the manifest as the
override mechanism, the probe's expectation conflicts with the design.

#### C5 (GAP HIGH): wrong baseline, wrong module, too narrow

Probe C5 runs `tests.test_cursor_session tests.test_code_exec` and
expects "test_code_exec shows no new failures versus the Y1 baseline
(1483 tests, 0 failures, 2 errors...)". The 1483-test baseline is the
FULL suite, not these two modules; comparing a 2-module run's counts to
a full-suite baseline is incoherent. Then it says "with the import
fixed, the remaining known error is the g++ one only". The g++ C++26
error is in test_cursor_file, which is NOT among the two modules run,
so there should be ZERO known errors in this run; the probe text
attributes the g++ error to the wrong module. And the scope is too
narrow: only two modules run, so collateral damage to other modules
(for example a shared helper touched by the refactor) is missed. Run the
full suite and compare against the full baseline (1483 tests, 0
failures, 2 errors, of which one disappears when the import is fixed).

#### C4 (GAP MEDIUM): the depth metric does not measure the compiler limit

The depth function counts With, Try, For, If and FunctionDef nodes, but
omits while, class, comprehensions and lambdas, and it counts
FunctionDef across boundaries even though the compiler's nesting limit
is per code object (a nested function's blocks do not add to the outer
frame's nesting). The reported number can move independently of whether
py_compile succeeds. It also compares the FILE max depth, not the target
function's depth: a refactor that splits the with-chain into a helper
can leave the file max unchanged (another test has the same depth) and
FAIL spuriously. Measure the depth of
test_cleanup_exceptions_cannot_skip_restore specifically, and treat
py_compile (already C1) as the real check; the depth number is supporting
evidence only.

## Cross-cutting gaps (affect the whole panel)

X1. Naming-deviation contradiction. Council 2 says an entry point that
does not exist FAILs with "interface missing", never adapted silently.
Council 3 section 0.2 says a naming deviation is "a finding, not an
automatic FAIL". If Codex names the loader differently, the two councils
give opposite verdicts. Y1b must pick one rule before running anything.

X2. CU_CODE_EXEC contradiction. Council 2 says the flag "is not needed
for these probes". Council 3 sections 0.1 and 0.3 require
`export CU_CODE_EXEC=1`. Both call CodeExecSession.run() directly, and
the flag only gates scripts/cu.py, so council 3's requirement is
unnecessary but harmless. Record one rule.

X3. Manifest-caching assumption (council 2, systematic). Probes load the
module and then edit the manifest. If the loader caches at import, edits
are invisible and verdicts go wrong in both directions (spurious pass
for added entries that read as "unknown", spurious fail for edited dates
that are never seen). The harness never verifies a re-read. Fix the
harness before running: reload the module after each manifest edit, or
assert re-read by changing a description and observing it.

X4. Council 3 probes are prose, not runnable code. Council 2 gives a
runnable code block per probe (extractable by its extractor). Council 3
gives runnable commands only for Phase C; probes 9a-12h are prose with a
few fragments and placeholders (`<loader>.load_manifest(...)` in 9a).
Y1b must translate prose to code, and that translation can drift from
the spec. A probe that exists only as prose cannot be re-run by anyone
else. Require runnable code blocks for 9a-12h before the panel runs.

X5. Unprobed redteam surface. No probe anywhere covers: search ranking
and description stuffing (redteam 9b: a snippet description stuffed with
keywords outranks the correct op); manifest max entry count (mentioned
in 8c1 setup, never tested); cancel during C-level work (Attack 2, see
2a); per-act char cap and snippet-run logging (redteam 5c fix); the
future-date bypass in isolation (6c2 is confounded, see above); the
verifier bootstrap path (a new snippet with no last_verified needs a way
to run once to be verified, 12g requires refusal but never tests the
bypass exists).

X6. Error-text narrowness is systematic. Probes require substrings
'wall-clock' (2a/2b), 'dunder' (3a/3b/3c), 'stale'/'hash'/'api' (6a2),
'approv' (7a3), 'size'/'cap'/'manifest' (8c1/9a), 'expired'/'stale'/
'verif' (6c1). A correct fix worded differently fails. Prefer behavioral
checks (no leak, no act, no call, correct result) and accept a defined
set of wordings where text must be checked.

X7. Load-skip vs run-refuse ambiguity is systematic. Many probes expect
a refusal naming a specific reason (duplicate, collision, stale, bad
date). If the loader skips the entry at load, run_snippet returns
"unknown snippet", which names none of those reasons, and the probe
fails spuriously even though the entry never runs. Decide one rule: either
load-skip with "unknown" is an acceptable refusal (and probes must accept
it), or the loader must keep rejected entries visible with their reason
(and probes must assert the reason). The current specs demand the reason
while allowing the skip.

## What must be fixed in the probes before Y1b runs them

1. Replace probe 1e with builtins that are actually allowlisted
   (`len("ab")`, not `chr(65)`), and re-run it against the item 4 fix.
2. Replace probe 4a with the model-defined-function globals check.
3. Rewrite probes 10b and 10f so the shared and reset variants differ
   (outer-plus-snippet sums over the cap; try/except around the first
   call in 10b).
4. Loosen the error-text requirements in 3a/3b/3c (accept NameError with
   no leak and no side effect) and in 2a/2b (accept timeout/killed/
   deadline wordings).
5. Add the aggregate-envelope probe for 2d and the cancel-during-C-work
   probe for Attack 2.
6. Fix probe 6b1 to use a shell-modeling backend, or split it into a
   fresh-path probe and a remove-first probe that asserts on the act
   calls.
7. Fix probe 6d-VM to use a pure behavior break on a live_only entry,
   with a trap-guarded restore verified by sha256.
8. Fix probe 5a3 to count reads from load through execution with a
   positive control, and probe 8f to update sha256 for traversal targets
   and watch only those targets.
9. Resolve X1, X2 and X7 (one rule each) and give council 3 runnable code
   blocks for 9a-12h (X4).
10. Add the missing coverage in X5, or record each item explicitly as
    uncovered instead of letting the panel imply it is covered.

Until those are done, the panel must not certify Phase A, B, or C: probes
1e and 4a fail a correct fix, probes 10b, 10f, 5a3, 5b2 and 8d pass
vulnerable implementations, and probe 6b1 fails a correct fix. A green
run on the current specs would certify holes.
