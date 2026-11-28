# Redteam report: Code Mode snippets registry design (Worker Y1)

Date: 2026-11-21. Author: Redteam (subagent of Worker Y1). Branch: todolist-push.
Repo: ~/workspace/computer-use-wayland.
Scope: attack the snippets registry design, not build it. Read-only on all code;
only this report file was written.

## Method and threat model

Sources read:

- docs/research/2026-11-21-code-mode-integration.md (Worker N, section 4.4 Risks)
- scripts/codemode.py (prototype execute_op)
- scripts/code_exec.py (live runner, merged at commit 453adc4)
- improvements/pick1-program-template.md (P1-P4, the first snippets)
- improvements/worker-y1-council-3.md (the design under attack: snippets as .py
  files under scripts/snippets/ plus manifest.json, run by run_snippet inside
  code_exec.py, same session, same budgets, call-depth cap 1, stale check via
  verified_against git commit hash)

Probes: three rounds of exploit probes run on the VM against the real
scripts/codemode.py and scripts/code_exec.py (probe scripts /tmp/redteam-probes.py,
/tmp/redteam-probes2.py, /tmp/redteam-probes3.py; outputs /tmp/redteam-out.txt,
/tmp/redteam-out2.txt, /tmp/redteam-out3.txt). No laptop touched, no network,
no destructive acts. Every HIGH below is demonstrated, not theorized. Where an
attack failed, that is stated too.

Threat actors assumed:

- A: a prompt-injected model (page content or tool output steering the model)
  writing code or choosing snippet names and params.
- B: a careless or malicious edit to a snippet .py file or to manifest.json
  after promotion (bad merge, mistaken edit, a compromised agent with repo
  write access).
- C: a future maintainer widening the allowlist or adding an op without
  re-checking the sandbox.
- D: ordinary drift (API renamed, desktop behavior changed, /tmp state left
  over from an earlier run).

## What I did NOT find

No full sandbox escape to arbitrary code execution. Direct dunder access
(`x.__class__`), `getattr`, `__import__`, `open`, `eval`, `exec`, `compile`
are all rejected by the AST scan in both files, and I verified the rejections
fire (probe R8: `getattr` gives "banned name: getattr"; probe P12b: dunder
attribute gives "dunder attribute access is banned"). Deep nesting
(`"(" * 3000 + "1" + ")" * 3000`) fails safe on Python 3.12 with
"SyntaxError: too many nested parentheses", enveloped, no crash (probes P7/P8).
`__builtins__` as a name is banned in both files (probe P12).

That is the good news. The bad news is that the scan has one hole that
defeats the dunder ban outright, the budgets do not bind the work they claim
to bind, and the snippet design's two load-bearing guards (stale check via
git commit, trust via CI verification) both fail for exactly the snippets
being promoted first (P1-P4 are live_only, run on the laptop, where there is
no .git and CI never executes them).

---

## Attack 1: str.format defeats the dunder ban (info disclosure, session token)

Severity: HIGH.

### Scenario

`"format"` is in the safe attribute whitelist in both files
(scripts/codemode.py line 49, scripts/code_exec.py line 119). The AST scan
only sees Attribute nodes in source code. `str.format` does attribute access
at runtime, inside the format string, which the scan never sees. So the
dunder ban is bypassed with a one-liner, no import, no getattr, no dunder
in the AST at all:

```python
return "{0.__class__}".format("")
return "{0.__class__.__mro__}".format("")
return "{0.__globals__}".format(repo_list_scripts)
return "{0.__globals__[REPO_ROOT]}".format(repo_list_scripts)
```

Measured (probe round 2, codemode.execute_op):

- `"{0.__class__}".format("")` returns `<class 'str'>`
- `"{0.__class__.__mro__}".format("")` returns
  `(<class 'str'>, <class 'object'>)`
- `"{0.__globals__}".format(repo_list_scripts)` returns the full repr of the
  codemode module globals dict, keys included
- `"{0.__globals__[REPO_ROOT]}".format(repo_list_scripts)` returns
  `~/workspace/computer-use-wayland`

The same hole in the live runner is worse, because code_exec API functions
are bound methods, and a bound method's `__self__` is the whole session:

```python
x = "{0.__self__.__dict__}".format(windows)
```

Measured (probe P9, CodeExecSession with a fake backend): the envelope
returns the full session `__dict__` repr, including the backend object repr,
`check_cancel`, `variables`, `observations`, and `dom_snapshots` (with full
DOM snapshot contents). And the session token itself, one line:

```python
x = "{0.__self__.session_token}".format(windows)
```

Measured (probe R5b, token `0123456789abcdef` x 2): the envelope returns
`0123456789abcdef0123456789abcdef` verbatim. In production that token names
the mode 0600 state file `code-exec-<token>.json` under the agent state dir
(scripts/code_exec.py lines 402-408, scripts/cu.py line 30). The token is
not a root password, but it is a live session identifier, and the same
one-liner dumps every observation and DOM snapshot the session holds.

Format output is always a string, so this is not RCE by itself. But it is a
complete bypass of the dunder ban for reads: any attribute chain on any
reachable object, returned as a string in the envelope. Reachable objects
include every op function (codemode), every bound API method and the whole
session (code_exec), and any dict they point at, including dicts holding
secret strings, which format extracts with `{0[key]}`.

The injection variant: if any snippet ever passes untrusted text as a
FORMAT STRING (a model-supplied param, or text read from a page through
dom_observe), page content such as `{0.__self__.__dict__}` becomes the
format string and the snippet's own objects become the arguments. P1-P4 do
not do this today, but the whitelist invites it, and a future snippet that
builds a message with `param.format(...)` hands the attacker the hole.

### Fix

- Remove `"format"` from SAFE_ATTRIBUTE_NAMES in both files
  (scripts/codemode.py line 49, scripts/code_exec.py line 119). Nothing in
  P1-P4 or in the template needs it; f-strings are safe here because
  f-string expressions ARE AST nodes and go through the scan, and `%`
  formatting does no attribute access. If a safe formatter is ever needed,
  use `string.Formatter().vformat` with a subclass that rejects attribute
  and index access, never `str.format`.
- Add regression tests that run the R1/P9/R5b one-liners and assert they
  fail the scan (or return no dunder data), in tests/test_codemode.py and
  tests/test_code_exec.py.
- Audit every reachable object's `__format__` and `__str__` for side
  effects before widening the whitelist again; the hole only stays
  read-only while no reachable object has a dangerous `__format__`.

---

## Attack 2: the wall-clock and trace budgets do not bind C-level work

Severity: HIGH (availability, and the cancel latch goes deaf with it).

### Scenario

Both budgets are enforced only by the line tracer. The tracer fires on
Python line events. A single expression that does its work in C fires no
line events until it returns, so the wall clock is never consulted while
it runs. The check is post-hoc, not preemptive.

Measured, codemode.execute_op with wall_seconds=2:

- `x = sum(range(10**8))` took 3.17s, error raised only after the loop
  finished ("wall-clock budget exceeded", probe P4)
- `x = sum(range(3 * 10**8))` took 7.40s with a 2s wall, same late error
  (probe R3). Overrun scales linearly with the expression: a
  `sum(range(10**10))` would burn roughly 300s before the tracer ever fires.

Measured, code_exec.py with wall_seconds=2, worse: the overrun is not even
reported, because `_trace` (scripts/code_exec.py lines 466-484) checks
budgets only every 200 trace events and only on `line` events, and a
one-line program's final line event fires BEFORE the C call, so no check
ever runs after it:

- `x = sum(range(10**8))` took 2.38s, envelope `ok=True`, no error (probe R6)
- `x = sum(range(3 * 10**8))` took 9.06s with a 2s wall, envelope `ok=True`,
  no error (probe R6b)

So in the live runner a snippet can exceed its wall budget by 4.5x and
report success. The same single-expression shape also defeats the trace
step budget (20000 lines, scripts/code_exec.py line 96): `sum(range(...))`
executes one line.

Memory is unbounded the same way. Measured (codemode):

- `x = "A" * (10**8)` allocates a 100MB string in 0.44s, status completed
  (probe P5). No memory cap exists anywhere in either file.
- `return "A" * (5 * 10**7)` returns a 50MB string in the result envelope
  in 0.12s, status completed (probe R4). There is no cap on result size,
  so a snippet can hand the supervisor a gigabyte string and blow up its
  context, or OOM the agent process outright.

The cancel latch is deaf during all of this: `check_cancel` runs in the
tracer (scripts/code_exec.py lines 459-464, every 200 events) and in `_api`
before/after API calls. A C-level loop makes no API calls and fires no
trace events, so a user pressing cancel during a runaway snippet waits
until the C work finishes. On the laptop that is a hung agent session.

### Fix

- Do not claim the wall budget preempts anything. Until preemption exists,
  document it as a post-hoc check.
- Add real preemption: a `signal.setitimer` / SIGALRM wall guard around
  execution (SIGXCPU is not a substitute), or run snippet execution in a
  child process with a hard timeout and kill. A child process also bounds
  the memory damage.
- Add a memory cap: `resource.setrlimit(RLIMIT_AS, ...)` in the child, or
  `tracemalloc` accounting with a hard abort. At minimum, cap result
  serialization (see Attack 5c): reject or truncate envelopes over 64KB,
  the same order as MAX_READ_BYTES.
- Add regression tests: `sum(range(3 * 10**8))` with a 2s wall must either
  be interrupted near 2s or be refused up front; a program returning a
  50MB string must not reach the envelope intact.

---

## Attack 3: codemode wrapper function is reachable, callable, and re-runs the program

Severity: HIGH.

### Scenario

scripts/codemode.py wraps model code as the body of a function named
`__codemode_main__` (lines 262-269) and calls it (line 275). The name is
reachable from model code because `_scan` (lines 200-221) only rejects
names in BANNED_NAMES; unlike code_exec's `_Validator.visit_Name`
(scripts/code_exec.py lines 310-316), it does NOT reject dunder names
generally. Measured:

- `return __codemode_main__` gives
  `<function __codemode_main__ at 0x...>` (probe R2a). The model holds a
  live reference to its own wrapper.
- `__codemode_main__()` unconditionally gives
  `RecursionError: maximum recursion depth exceeded` (probe R2b). It is
  callable.
- Conditional self-call double-executes the body. Measured (probe R2c):
  a program that counts executions on an attribute of the function object
  (`__codemode_main__.count`, where `count` IS allowlisted) and calls
  itself once returns 2. The body ran twice.

In a snippet that calls act(), double execution means double desktop
actions: the same text typed twice, the same button clicked twice, the
same form submitted twice. The count attribute trick also shows a second
gap: allowlisted attribute names can be SET on live objects, not just
read, so model code can stash state on the wrapper function, on op
functions, or on any reachable object.

Also in this family: `yield` is not rejected by codemode's `_scan`
(code_exec rejects it at scripts/code_exec.py lines 300-305). Measured
(probe P3): a program containing `yield 2` returns
`{'status': 'completed', 'result': <generator object __codemode_main__ ...>,
'steps': 3}`. The body never executed, and the runner reports success.
A snippet containing a stray `yield` silently does nothing and claims it
worked. The generator object is also not JSON-serializable, so it will
break whatever consumes the envelope downstream.

### Fix

- In codemode `_scan`, reject any Name starting with `__` (copy
  code_exec.py lines 313-314) and reject Yield/YieldFrom (copy lines
  300-305). Reject AsyncFor/AsyncWith too, for parity with code_exec
  lines 288-297.
- Do not leave the wrapper function in the namespace: delete
  `namespace["__codemode_main__"]` after exec, or name it with a
  random unguessable suffix per execution. Better, execute model code at
  module level the way code_exec does, so there is no self-reference
  to reach.
- Add regression tests: `__codemode_main__` must be rejected by the scan;
  a program containing `yield` must be rejected, never "completed".

---

## Attack 4: codemode does not pin __builtins__ (latent full escape)

Severity: MEDIUM (latent; no live path demonstrated, but one gap away
from full RCE).

### Scenario

scripts/code_exec.py run() pins `'__builtins__': dict(SAFE_BUILTINS)` in
the execution namespace (line 816). scripts/codemode.py execute_op does
not: it builds `namespace = dict(SAFE_BUILTINS)` plus `print` and the ops
(lines 240-246) and calls `exec(compiled, namespace)` (line 271). CPython
then inserts the REAL builtins module into the namespace dict as
`__builtins__`. Model code cannot name `__builtins__` (it is banned,
probe P12), but the full builtins, including `eval`, `open`,
`__import__`, and `compile`, sit one attribute hop away inside every
function object's `__globals__`. Today the only way to reach them is the
format hole (Attack 1), which returns strings, not live objects. But any
future gap that yields a globals dict as a live object, or any object
with a `__globals__` reachable by a live reference, immediately hands
over full builtins. The pin in code_exec exists precisely to close that
second hop; codemode lacks it.

### Fix

- Pin `'__builtins__': dict(SAFE_BUILTINS)` in codemode's namespace,
  exactly as code_exec.py line 816 does. One line.
- Add a test asserting that `namespace` after execute_op contains no
  real builtins module.

---

## Attack 5: snippet trust, edit after promotion, name collision, exfiltration

Severity: HIGH (5a, 5c); MEDIUM (5b, 5d).

### Scenario 5a: edit after promotion, no signature, no hash

The council design (improvements/worker-y1-council-3.md lines 47-54) says
snippets are never trusted once promoted and are scanned on every run.
That covers the AST scan, but nothing else about the file is verified.
The manifest carries `reviewed_by`, `reviewed_on`, `last_verified`, and
`verified_against` (a git commit hash), but no hash of the snippet .py
content itself. A one-line edit to a promoted snippet changes what
run_snippet executes, with zero signal at runtime. The CI test the design
relies on (tests/test_snippets.py) only py_compiles and validates
live_only snippets; it never executes them. P1-P4 are all live_only, so
an edit to any of the first four snippets passes CI (syntax plus AST
scan) and ships, and is never executed by any check before production
use. The "verification" that would catch it is a manual live run on the
laptop, with no schedule and no expiry. Promotion is a review gate with
no seal on the thing reviewed.

Fix: manifest stores sha256 of the snippet file bytes, set only by the
verification run, never by hand. run_snippet reads the file ONCE, hashes
the bytes it read, compares against the manifest, and executes exactly
those bytes. Any mismatch refuses with a stale-snippet envelope naming
the snippet and the expected hash. No hash match, no run.

### Scenario 5b: name collision with a future op, and param shadowing

Snippets are addressed by string name. The design namespaces search
results as `snippet.<name>` (council-3, question 5), which is good, but
nothing reserves names. A snippet named `windows`, `act`, or
`repo.list_scripts` collides with a future op of the same name in search
results, and a human reading a program cannot tell whether
`run_snippet("act")` is a snippet or a typo for the API. Worse, params
are bound as values into the session namespace (council-3 line 41). A
manifest entry with a param named `windows`, `act`, `observe`, or
`read_file` SHADOWS the API function of that name inside the snippet's
execution: the snippet's own `act(...)` call then calls the param value
(a string) and dies with TypeError, or, if the param value were ever a
callable, calls attacker-chosen code. Params are JSON types only, so the
callable case cannot happen today, but the shadowing DoS is real and
silent at manifest load time.

Fix: reserve the API allowlist names; reject at manifest load any snippet
name equal to an op path or API name, and any param name in the allowlist
(scripts/code_exec.py lines 270-276). Bind params as locals of the
snippet execution frame, never into persistent session variables (see
Attack 9).

### Scenario 5c: a snippet reads a file the model should not see and types it out

A promoted snippet runs by name, and nobody reads its code at run time.
That is the point of snippets, and it is the hole. codemode's read_file
reaches the whole repo root plus /tmp (scripts/codemode.py lines 106-124);
code_exec's read_file reaches /tmp (scripts/code_exec.py lines 640-660).
/tmp on the laptop holds screenshots, downloaded files, and task outputs.
The repo root holds coord files, docs, and the .git directory. A snippet
that reads a file and returns it puts the content in the envelope, and a
snippet that reads a file and types it through act() puts it into
whatever window is focused: a terminal where `curl -d @file` exfiltrates
it, a browser address bar, a chat box. The sandbox has no network, but
act() IS the network: keystrokes into a shell that has curl. A snippet
does not even need to be malicious. A snippet written to "type the
contents of /tmp/result.txt into the terminal" does exactly this by
design, and once promoted it does it on every call with no review step.

The model can already do this directly with read_file plus act, so this
is not a NEW capability. The new risk is the hiding: run-by-name removes
the read-the-code step that is the only review a model-written program
gets. A snippet is trusted code that runs without being read.

Fix: per-snippet approval tiers. Mark snippets that read files or type
arbitrary text as `requires_approval` (the codemode OPS table already has
the field, scripts/codemode.py line 130, set False for all six ops; the
snippet manifest has no equivalent). A snippet that types model-supplied
or file-read text into a live window needs an explicit approval on first
use, and its source must be shown with the approval request. Also cap
what one act() call can type per snippet run, and log every snippet run
with its hash, params, and result.

### Scenario 5d: param values as format strings

Covered in Attack 1: if any snippet passes a model-supplied param or
page-derived text as a format string to `.format`, the attacker controls
the format string and the snippet supplies the objects. Ban `.format`
(Attack 1 fix) and add a manifest lint: no snippet source may call
`.format` on a value that is not a string literal.

---

## Attack 6: stale snippet, and why the designed guard does not work where it runs

Severity: HIGH (6a, 6b); MEDIUM (6c).

### Scenario 6a: verified_against is a git commit hash, and the laptop has no .git

The stale rule (council-3 lines 56-66) compares the manifest's
`verified_against` commit with "the current code_exec.py commit" at load
time, and refuses to run on mismatch. But snippets run on the LAPTOP
(P1-P4 are live_only; the installed copy is synced by
scripts/sync-installed.py, which copies files, not the .git directory).
On the laptop there is no commit to compare against. So the implementer
faces a forced choice: fail closed and P1-P4 never run on the laptop
(the only place they can run), or fail open and the stale guard is dead
exactly where snippets actually execute. Either way the guard as
designed does not work on the deployment target. There is no evidence in
the design that anyone checked whether `git rev-parse HEAD` succeeds in
the installed copy.

Fix: do not key staleness on git. Record `verified_against` as the sha256
of the installed scripts/code_exec.py file bytes, or better as a hash of
the API surface the snippet depends on (the allowlisted function names
plus their signatures plus the validator rules), computed at runtime
from the loaded module. If the hash cannot be computed, fail closed.

### Scenario 6b: silent breakage, and the P3/P4 false-positive assert

Three breakage modes, with very different noise levels:

1. Renamed API or changed return shape: loud. NameError or KeyError,
   error envelope. Caught by the VM CI test for non-live snippets.
2. Changed semantics, same shape: silent. `windows()` returning windows
   in a different order makes `[w for w in wins if w["title"] ==
   title][0]` (improvements/pick1-program-template.md, P1-P4) pick a
   different window with no error. Two terminals sharing a title make
   the pick nondeterministic between runs. The snippet then types into
   the wrong window, and nothing in the envelope says so.
3. Stale /tmp state makes asserts pass without the work happening.
   P3 asserts `assert_file_exists("/tmp/hoc-ky-2/dsa")` and P4 asserts
   file contents (pick1-program-template.md lines 33-60). /tmp persists
   across runs. If a rerun's act() is refused, types into the wrong
   window, or the shell never runs the command, the directories and the
   file from the FIRST successful run are still there, and the asserts
   pass. The snippet reports success for work it did not do. This is
   not hypothetical: the template's own root-cause section documents
   that P3 already failed once on timing, and the fix was ordering, not
   freshness. A rerun after a failed act is exactly the case where the
   stale-state false positive bites.

Fix: snippets that assert on persistent paths must first remove the
target (or use a fresh unique path per run, e.g. a run id under /tmp)
and then assert. Add that rule to the template. For window selection,
require an exact single match: if zero or more than one window matches
the title, fail loudly instead of taking [0]. For semantic drift, the
only real guard is the live verification run, which brings us to 6c.

### Scenario 6c: last_verified is hand-editable and never expires

`last_verified` is a date string in the manifest, and the design says
the verification run updates it, not a human. But nothing enforces that:
anyone editing the manifest can set any date. And there is no expiry:
a snippet verified six months ago stays searchable and runnable
forever, even if the desktop behavior it assumes (window titles, button
positions, page text) has changed five times since. The search-exclusion
rule (council-3, question 3 rule 4) only triggers on a FAILING test, and
live_only snippets have no test that runs without a human.

Fix: `last_verified` plus a max age (e.g. 30 days for live_only
snippets). A snippet past its age is excluded from search and refused
at run time until a passing live verification refreshes it. The age
check must be enforced by the runner, not by convention.

---

## Attack 7: replay and divergence, Polygon uploads and Zen tabs

Severity: HIGH (7a, 7c); MEDIUM (7b).

### Scenario 7a: a retried snippet re-executes non-idempotent acts

code_exec.py has no replay. A retried program re-runs from scratch
(research doc section 4.4, "Silent divergence"). P3's `mkdir -p` is
idempotent and P4's `printf ... > file` overwrite is idempotent, so the
first four snippets survive a retry. Nothing else does. Concrete bites
in this repo:

- Polygon upload: a snippet that clicks "Create problem" or "Submit
  package" and then fails at the verify observe (wall clock, stale
  snapshot, compositor move) gets retried by the supervisor. The retry
  creates a SECOND problem or submits a SECOND package. There is no
  idempotency key and no record of what the first attempt applied.
- Zen tabs: a snippet that types a URL plus Enter and then fails its
  assert retries and opens a second tab with the same URL. A snippet
  that types text into a form field and retries types it twice.
- Any snippet that branches on a value it read early and acts late:
  the value can be stale by act time, and the retry reads a NEW value
  and takes a different branch, so the two attempts do different
  things while both report the path they took.

Fix: record applied snippet calls per session (name plus param hash plus
result) in the session state, and on a retry of the same snippet with
the same params, return the recorded result or refuse with an explicit
"already applied" envelope instead of blindly re-executing. This is the
small version of Cloudflare's recorded-results replay, and it is the
minimum for any snippet whose acts are not idempotent. In addition,
mark non-idempotent snippets `requires_approval`, and require snippets
to check state before acting (observe, then act only if the state says
the work is not done) rather than acting blindly.

### Scenario 7b: DOM snapshot refs after navigation, and branching on read values

dom_act validates refs against the bound snapshot
(scripts/code_exec.py lines 590-610), not against the live page. If the
page navigates without a reload (SPA navigation), the same refs can
resolve to different elements, and the click lands on the wrong thing
with no error. A snippet that observes, branches on text, then acts
late is exposed to this for the whole 120s binding life
(OBSERVATION_MAX_AGE, line 99). The binding expiry is a loud failure
after 120s, which is good, but inside the window the snapshot is
trusted while the page may have moved.

Fix: re-observe immediately before any destructive dom_act, and assert
a page-identity predicate (URL or a stable heading) in the same snapshot
as the act. Do not let a snippet hold a snapshot across a navigation.

### Scenario 7c: act() without a fresh observe acts on another snippet's observation

`act()` with no observation argument defaults to the most recent
observation in the session (scripts/code_exec.py lines 530-551), up to
120s old, whoever took it. The council design runs every snippet in the
SAME session with shared bindings. So a snippet that calls act() without
observing first acts on whatever the previous snippet (or the model
program) observed, possibly a different window. P1-P4 all observe first,
so this needs a future snippet that forgets, or one designed to "type
into the current terminal". Either way the shared-session design makes
the failure possible by construction, and the failure mode is typing
into the wrong window.

Fix: scope observation bindings per snippet run. run_snippet clears the
session's observation and DOM bindings on entry, and a snippet that
calls act() or dom_act() without an observe inside its own execution
fails loudly. Add a test: two snippets run in sequence, the second with
no observe, must fail, not act on the first's observation.

---

## Attack 8: registry poisoning, malformed, huge, or looping snippets

Severity: HIGH (8d); MEDIUM (8a, 8b, 8c, 8e).

### Scenario 8a: malformed manifest

The design has manifest.json as the single lookup table. If it is
malformed JSON, the loader behavior decides the blast radius. If the
loader parses it once at import or session start and raises, ALL snippet
runs break, and if the parse happens inside code_exec import, the whole
runner breaks. If the loader parses it per run_snippet call and raises
outside the envelope, the host process sees an uncaught exception.
There is no stated rule for either case.

Fix: load the manifest lazily per call, validate its schema, and fail
closed PER ENTRY: one bad entry is skipped with a logged warning and
never offered in search; a malformed file yields an error envelope for
that call and nothing else. Never let manifest parsing raise out of
run_snippet.

### Scenario 8b: duplicate names, silent shadowing

If the manifest is a list, two entries with the same name resolve by
lookup order (first or last wins, silently). A bad merge can add a
duplicate entry pointing at a different code_path, and which snippet
runs depends on an ordering nobody specified. If the manifest is a
dict, JSON duplicate keys resolve last-wins silently in json.load.
Either way the operator cannot tell from the file which entry is live.

Fix: reject duplicate names at manifest load, loudly, and refuse to
serve the registry until fixed. Add a CI test asserting name uniqueness.

### Scenario 8c: huge manifest, huge snippet, no size caps

No size cap is stated for manifest.json or for a snippet .py file. A
10MB manifest parses slowly and eats memory on every run_snippet call
if loaded per call. A megabyte snippet file compiles slowly and, once
executed, can build arbitrarily large results (Attack 2, R4: a 50MB
string in 0.12s). The 8192-char program cap (scripts/code_exec.py line
92) bounds model-written programs but does NOT bound snippet files, so
run-by-name is also a way to smuggle an arbitrarily large program past
the cap: a 100-char model program can invoke a 1MB snippet.

Fix: cap manifest.json at load (e.g. 1MB, and a max entry count) and cap
snippet files (e.g. 8192 chars, the same as programs, unless a snippet
justifies more in review). Enforce the cap in run_snippet, not only in
CI.

### Scenario 8d: infinite loop snippet, and the budget-reset amplification

The design says a snippet runs under the SAME API-call budget (32),
wall-clock budget (30s, max 60s), and bindings as the calling program
(council-3 line 41). That is the intent. The natural implementation
defeats it: `CodeExecSession.run()` resets `self.api_calls = 0`
(scripts/code_exec.py line 802) and resets `self._deadline`
(line 806) at the start of every run. If run_snippet is implemented by
calling run() (or by building a nested session), the snippet gets a
FRESH 32 API calls and a FRESH 30s wall clock, and the outer program's
counters are clobbered. A model program can then call run_snippet in a
loop: each call costs 1 outer API call, and each inner execution gets 32
fresh calls and 30 fresh seconds. 32 outer calls times 32 inner calls
is 1024 API calls from one program, and up to 16 minutes of wall time,
all inside budgets that claim 32 calls and 60s max. Combined with
Attack 2, a looping snippet that does C-level work in each inner run
never trips any budget at all, and the cancel latch cannot interrupt it.

Fix: run_snippet must execute the snippet INLINE in the current run,
sharing the live api_calls counter, the live deadline, and the live
trace counter. Never call run() recursively and never build a nested
session. Add a test that a program calling run_snippet in a loop cannot
exceed 32 API calls or the wall clock, and that a snippet doing
`sum(range(10**8))` is charged against the outer deadline.

### Scenario 8e: .py files are importable code, and import bypasses the scan

Snippets are real .py files under scripts/snippets/. The design loads
them by reading text, validating with validate_program, and executing in
session. But a .py file on disk is also importable: any tooling that
imports it (a test loader using importlib, a future `import snippets.x`,
a namespace-package import) executes its top-level statements with full
process privileges and NO AST scan. A poisoned snippet file with
`import os` at the top fires the moment anything imports it. The
validate_program scan only protects the run_snippet path, not the file.

Fix: the loader must read text only, never import; add a CI test that
greps the repo for any import of scripts/snippets and fails if found;
and keep snippets/ free of `__init__.py` so it is not a package by
accident. Note the residual: any agent with repo write access can edit
code_exec.py itself, so this is about blast radius, not about stopping a
fully compromised writer. A snippet edit must not be a stealth privilege
escalation path for an agent that only has "edit a snippet" scope.

---

## Attack 9: other run-by-name attacks

### 9a: path traversal through name or code_path. Severity: MEDIUM.

If the loader builds a path from the snippet name
(`scripts/snippets/<name>.py`) or trusts manifest `code_path` verbatim,
a name like `../../cu` or an absolute path, or a manifest entry with
`code_path` set to `../../something.py`, loads an arbitrary .py file
from disk and executes it through the snippet path. The manifest
indirection mitigates this only if lookup is by manifest key AND
code_path is contained.

Fix: resolve code_path, require the resolved path to be under
scripts/snippets/, reject absolute paths and any `..` component, and
reject names that are not kebab-case matching the manifest key.

### 9b: search description stuffing. Severity: LOW.

search_ops ranks by naive keyword count (scripts/codemode.py lines
173-186). A snippet description stuffed with keywords ("terminal type
click submit upload polygon zen dom file") matches every query and
ranks above the correct op. The model then runs the wrong snippet.

Fix: rank snippets below ops by default, index only tags (not free-text
description) for snippets, and cap the score contribution of any single
field.

### 9c: cross-snippet variable poisoning. Severity: MEDIUM.

Session variables persist across programs (scripts/code_exec.py lines
137-155, 838-845). Measured (probe R7b/R7c): program 1 sets
`term_title = "speed-pick1-term"`, program 2 sets
`term_title = "attacker-controlled"`, program 3 reads `y = term_title`
and gets `"attacker-controlled"`. With run_snippet in the same session,
snippet A can set a variable that snippet B reads without re-validating,
and a param bound into persistent variables (Attack 5b) outlives the
snippet that set it. A snippet that trusts a variable name instead of
its own param is poisoned by whoever ran before it.

Fix: snapshot the variable dict on run_snippet entry and restore it on
exit, except for an explicit declared output (one named result value).
Params are frame locals, never persistent variables.

### 9d: time-of-check vs time-of-use on the hash. Severity: LOW.

If the hash is checked at load and the file is read again at execution,
an edit between the two runs unverified code. Fix: read once, hash the
bytes read, execute those bytes (Attack 5a fix already covers this if
implemented as stated).

### 9e: nested run_snippet and mutual recursion. Severity: LOW, if the cap is enforced as designed.

The council caps call depth at 1 (a snippet may not call run_snippet).
The cap must be a session-level reentrancy counter, incremented on
entry and decremented on exit, counting the outer call too. A
counter stored in a local or reset by a nested run() would not survive
to block A calling B calling A. Enforce it in run_snippet itself, and
test A calling B and A calling itself.

---

## Verdict: BLOCK

BLOCK the first snippet promotion until the must-fix list below is done.
This is not a rejection of the design: the council-3 shape (one registry,
one executor, full scan on every run, value-bound params, depth cap 1)
is the right shape, and no full sandbox escape was found. It is a block
because the design's own guards do not hold for the first four snippets:

1. The format hole (Attack 1) leaks the live session token TODAY in the
   live runner, through a one-liner any prompt-injected model can write.
   It is a one-line whitelist fix, but it is live now, and snippets
   increase the number of callers that can reach it.
2. The stale guard (Attack 6a) depends on a git commit comparison that
   cannot run on the laptop, where P1-P4 actually execute. As designed,
   the guard is dead on the deployment target.
3. The verification that is supposed to catch a bad edit (Attack 5a)
   never executes live_only snippets, so an edit to any of P1-P4 passes
   CI unchecked. Combined with no content hash, a promoted snippet can
   change behavior with zero signal.
4. The budget-sharing rule (Attack 8d) is stated as intent but the
   natural implementation (nested run()) resets every budget, giving a
   32x amplification. Until the inline-execution rule is implemented
   and tested, the budgets are not a safety property of snippets.

### Unblock checklist (must-fix before the first promotion)

Executor fixes (also fix model-written code, not just snippets):

- 1. Remove `"format"` from SAFE_ATTRIBUTE_NAMES in scripts/codemode.py
  and scripts/code_exec.py; add the R1/P9/R5b regression tests.
- 2. Pin `'__builtins__': dict(SAFE_BUILTINS)` in codemode execute_op.
- 3. codemode `_scan`: reject dunder Names, Yield/YieldFrom,
  AsyncFor/AsyncWith; make `__codemode_main__` unreachable (delete from
  namespace or execute at module level); add the yield regression test.
- 4. Cap serialized envelope results at 64KB; add the R4 regression test.

Snippet design fixes:

- 5. Manifest stores sha256 of snippet bytes; run_snippet reads once,
  verifies, executes those bytes; mismatch refuses.
- 6. Stale check keyed on a runtime-computed hash of the code_exec API
  surface or file bytes, never on a git commit; fail closed when the
  hash cannot be computed.
- 7. run_snippet executes inline with shared api_calls, deadline, and
  trace counter; never a nested run() or nested session; add the
  loop-amplification test.
- 8. Live_only snippets get a real verification path before promotion:
  a FakeBackend smoke run in CI plus a dated live re-verification with
  a 30-day expiry enforced by the runner (past expiry means excluded
  from search and refused at run).
- 9. Params: reject names colliding with the API allowlist; bind as
  frame locals; snapshot and restore persistent variables around the
  snippet; never interpolate params into source.
- 10. Scope observation and DOM bindings per snippet run; a snippet
  that calls act() or dom_act() without its own fresh observe fails.
- 11. code_path containment under scripts/snippets/; manifest size cap
  and duplicate-name rejection; per-entry fail-closed loading; loader
  reads text only, never imports snippet files.
- 12. Non-idempotent snippets marked requires_approval (or guarded by
  observe-then-check-state), plus a per-session applied-snippet ledger
  so a retry does not blindly re-execute.

Should-fix soon (not blocking promotion, but do not defer far):

- 13. Real wall-clock preemption (signal timer or child process with
  kill) and a memory cap, so Attack 2 stops being a hang-the-agent
  primitive.
- 14. Snippet assert hygiene in the template: fresh unique /tmp paths
  per run (or remove-then-assert), and exact-single-match window
  selection instead of [0].
- 15. Search ranking: snippets below ops, tags only, per-field score cap.

### Residual risk, stated plainly

Even after the checklist, the AST scan plus restricted builtins is NOT
a true isolate (Worker N, section 4.4). A future allowlist addition, a
reachable object with a side-effecting `__format__` or `__str__`, or a
new op that returns a live privileged object could reopen a hole the
scan cannot see, because the scan reasons about syntax and the danger
lives in runtime object graphs. The durable fix is a real isolate (a
subprocess with no imports of the agent process, or a V8/Boa-style
sandbox) for snippet execution. Until then, treat every allowlist
change as a security change: review it with the format-hole probes in
this report, and never widen the whitelist to unblock a snippet.
