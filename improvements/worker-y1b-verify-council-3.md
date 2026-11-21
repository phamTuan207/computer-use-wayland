# Worker Y1b verification probes: Council Member 3 (must-fix 9-12 plus Phase C)

Role: Council Member 3 of Worker Y1b's verification panel. Date: 2026-11-21.
Branch: todolist-push. Repo: ~/workspace/computer-use-wayland.
Scope: PROBE SPECS ONLY. No implementation, no verdicts. Y1b runs these
probes against Codex's Phase A/B/C work (branch y1-snippets, merged to the
VM for verification) and judges pass/fail from the criteria below. Never
trust Codex's own test report; every probe below re-proves the fix
independently on the VM.

Sources grounding these probes (read before running):
- improvements/worker-y1-redteam.md (BLOCK report: 7 attacks, 6 HIGH,
  12-item must-fix checklist; Attacks 5, 6, 7, 8, 9 and checklist items
  9-12 are the basis for items 9-12 below)
- improvements/worker-y1-codex-log.md (Y1 log, council synthesis section,
  amended rules: registry at top-level snippets/, sha256 required, stale
  check keyed on a runtime-computed hash never on a git commit, expiry
  30 days live_only / 90 days VM-verifiable, inline run_snippet with
  shared counters, params as frame locals with snapshot/restore, per-run
  observation/DOM scoping, manifest size cap plus duplicate rejection
  plus per-entry fail-closed loading plus code_path containment plus
  text-only loading plus no __init__.py)
- improvements/worker-y1-council-3.md (original design: run_snippet as a
  code_exec API function, depth cap 1, params bound as values never by
  string interpolation)
- scripts/code_exec.py (pre-Codex baseline on the VM: MAX_PROGRAM_CHARS
  8192 line 92, MAX_WALL_SECONDS 60 line 93, DEFAULT_WALL_SECONDS 30
  line 94, MAX_API_CALLS 32 line 95, MAX_TRACE_STEPS 20000 line 96,
  MAX_READ_BYTES 65536 line 98, OBSERVATION_MAX_AGE 120 line 99,
  run() resets api_calls line 802, _deadline line 806, _trace_steps /
  _trace_events lines 803-804, session.variables persistence lines
  838-845, _bound_observation lines 530-551, api_act(actions,
  observation=None) line 553, api_observe(window/screen) line 515)
- tests/test_code_exec.py (FakeBackend, FakeDomBackend, run() helper:
  reuse them in every probe; do not build a second fake backend)
- tests/test_cursor_session.py (33 tests; Phase C target, SyntaxError
  "too many statically nested blocks" line 566 on VM Python 3.12.3,
  parses fine on laptop Python 3.14.10)

## 0. How to run these probes (read first)

0.1 Environment. All probes run on the VM, from the repo root, with
Python 3.12.3, CU_CODE_EXEC=1 in the environment, on the todolist-push
branch with Codex's y1-snippets work merged in. Commands:

```
cd ~/workspace/computer-use-wayland
git branch --show-current        # must print todolist-push
export CU_CODE_EXEC=1
python3 --version                # must print Python 3.12.3
```

0.2 Surface discovery (do this before any probe, record the answers in
the verification log). Codex may have named things differently from the
design docs. Find the real names first, then run the probes against
them. A naming deviation is recorded as a finding, not an automatic
FAIL, but a probe that cannot find its target at all is a FAIL for
that item (missing surface, not missing probe).

```
grep -rn "def run_snippet\|def _load_manifest\|def load_manifest\|MANIFEST\|SNIPPETS_DIR\|MAX_MANIFEST\|MAX_SNIPPET" scripts/code_exec.py scripts/cu.py
ls snippets/                     # expected top-level registry per amended synthesis
cat snippets/manifest.json       # expected manifest location
grep -rn "run_snippet" scripts/code_exec.py | head -20
grep -rn "allow_stale\|last_verified\|live_only" scripts/code_exec.py | head -30
```

Record: (a) registry directory path, (b) manifest path, (c) loader
function name and its manifest-path override mechanism, if any,
(d) run_snippet signature, (e) cap constant names and values,
(f) expiry constants (30 / 90 days) and their names, (g) the manifest
field name for declared snippet outputs, if any.

0.3 Fixture pattern (used by probes 9a-9h, 11a-11b, 12a-12h). Probes
must not corrupt the real registry. Preferred order:

1. If the loader accepts a manifest path argument or an env var
   override, use it and point it at a fixture manifest under
   /tmp/y1b-fixtures/<probe>/manifest.json with fixture snippet files
   beside it.
2. Else, if the loader reads a module-level constant path, monkeypatch
   that constant in the probe process to the fixture path.
3. Else, back up the real manifest (cp snippets/manifest.json
   /tmp/y1b-fixtures/real-manifest.json.bak), install the fixture
   manifest, run the probe, restore the backup byte-for-byte, and
   verify the restore with sha256sum before and after.

Every probe that touches the real manifest must restore it and prove
the restore. Fixture snippet files live under /tmp/y1b-fixtures/ and
are deleted after the run. No probe writes outside /tmp and the repo
except through this backup/restore pattern.

0.4 Loading code_exec in probes. Mirror tests/test_code_exec.py: load
scripts/code_exec.py by file path with importlib.util, reuse its
FakeBackend / FakeDomBackend by importing tests.test_code_exec. Run
probe scripts as `python3 /tmp/y1b-probes/probe_9a.py` from the repo
root. Each probe script prints one line starting with PROBE <id> PASS
or PROBE <id> FAIL plus the evidence (counts, error strings, paths).

0.5 Verdict rule. Each numbered item (9, 10, 11, 12, Phase C) is PASS
only if every sub-probe under it is PASS. One FAIL sub-probe fails the
whole item. A sub-probe that cannot run because its target surface
does not exist is FAIL (missing fix), not SKIP. The only allowed SKIP
is the documented lua-missing skip in Phase C probe C2. Laptop-only
probes are listed in section 6 and never block a VM verdict.

0.6 Style rules for probes. Never ydotool. No probe touches the live
desktop, the real terminal, Zen, Chromium, or the network. FakeBackend
only on the VM. No personal info in probe output, fixtures, or commits.

## 1. Item 9: manifest loading

Contract under test (amended synthesis + redteam Attacks 5a, 8a-8e, 9a):
manifest.json has a size cap; duplicate names are rejected loudly;
each bad entry fails closed on its own without taking down the good
entries; code_path is contained under the registry directory; the
loader reads text only and never imports snippet files; snippets/ has
no __init__.py; snippet files have a size cap; the manifest sha256 is
verified against the bytes actually executed (read once, hash the
bytes read, execute those bytes).

Expected caps (redteam): manifest 1 MB, snippet 8192 chars (same as
MAX_PROGRAM_CHARS). If Codex chose different cap values, record them;
enforcement at the documented cap is what PASS requires, and any cap
larger than the redteam values without a written justification in the
merge notes is recorded as a finding.

### Probe 9a: manifest size cap

Setup: fixture manifest larger than the cap. Build it by repeating a
valid entry (or padding a description field) until the file exceeds
the cap constant found in 0.2 by at least 1 byte. Keep the JSON valid.

Probe (runnable):

```
python3 - <<'PY'
import json, pathlib
# cap = <cap constant read from code_exec.py in step 0.2, expected 1048576>
cap = 1048576
entry = {"name": "p1-disk-free", "code_path": "p1_disk_free.py",
         "sha256": "0"*64, "description": "x", "params": [],
         "last_verified": "2026-11-21", "live_only": False}
entry["description"] = "x" * (cap + 1024)
pathlib.Path("/tmp/y1b-fixtures/9a/manifest.json").write_text(json.dumps([entry]))
PY
# then, with the fixture manifest installed per 0.3, run:
python3 -c "import <loader>; print(<loader>.load_manifest('/tmp/y1b-fixtures/9a/manifest.json'))"
```

PASS: the loader refuses the oversized manifest (error envelope or
raised loader error caught inside run_snippet, never served), no
snippet from it runs, and a subsequent call with the real manifest
still works (the runner is not wedged). FAIL: the oversized manifest
parses and serves snippets, or the refusal raises out of run_snippet
as an uncaught exception, or the runner breaks for later calls.

### Probe 9b: duplicate-name rejection

Setup: fixture manifest as a list with two entries sharing one name
but different code_path values, both otherwise valid and both files
present with distinct content. Second variant: a manifest written as
a JSON object (dict keyed by name) whose raw text contains the same
name key twice.

Probe: load the fixture manifest through the loader, then call
run_snippet() for the duplicated name (if the loader served it).

PASS: the loader rejects the duplicate loudly at load (error naming
the duplicated name, registry not served until fixed, or the duplicate
entry refused with a logged error), and run_snippet() for that name
refuses instead of running either file. The dict-key variant is also
rejected (raw-text scan or object_pairs_hook), not silently last-wins.
FAIL: either file runs silently (first-wins or last-wins), or the
duplicate is served with no error anywhere.

### Probe 9c: per-entry fail-closed loading

Setup: fixture manifest with three entries: one good entry (valid
fields, file present, sha256 correct, verifiable against
FakeBackend), one entry missing a required field (e.g. no code_path),
one entry whose code_path points at a missing file. All in one
manifest file.

Probe: load the manifest, list the offered snippets (search/listing
entry point), then run_snippet() the good entry.

PASS: the two bad entries are skipped with a logged warning each,
never offered in search and never runnable (run_snippet() for each
refuses with an entry error), and the good entry still lists and
runs normally. FAIL: the whole registry fails to load, or a bad entry
is offered or runs, or the good entry stops working.

### Probe 9d: malformed manifest JSON

Setup: fixture manifest file containing truncated JSON (e.g. cut off
mid-entry) and, as a second variant, valid JSON of the wrong shape
(e.g. a bare string instead of a list/dict).

Probe: load each variant, then call run_snippet() for a known good
name, then call an unrelated code_exec API (windows() via a trivial
program) to prove the runner still works.

PASS: each variant yields an error envelope for that call only (or a
loader error caught inside run_snippet), the runner import is
unaffected, and later calls with the real manifest work. FAIL: an
uncaught exception escapes run_snippet, or the import of code_exec
breaks, or later calls fail.

### Probe 9e: code_path containment

Setup: fixture manifest entries (one per case, each with its own
fixture manifest or one manifest with several bad entries plus one
good control): code_path "../outside.py", "/tmp/evil.py",
"subdir/../../outside.py", "good.py" where good.py is a symlink
inside the registry pointing at /tmp/evil.py, and code_path
"./good.py" as the control that must load. Put a marker file at
/tmp/y1b-fixtures/9e/evil.py containing a program that would set a
variable named pwned if executed.

Probe: load the manifest and attempt run_snippet() for every entry,
then check whether pwned was ever set (session.variables and the
envelope variables).

PASS: every traversal, absolute-path, and symlink-escape entry is
rejected at load (never executed, pwned never set), and the "./good.py"
control loads and runs. FAIL: any escaping entry loads or executes,
or pwned is set, or the rejection happens only at execution time
after the file was already read as code (load-time rejection is
required; an execute-time refusal after read still counts as FAIL if
the file content was loaded into the process).

### Probe 9f: text-only loading, no import, no __init__.py

Setup: none (repo inspection plus runtime check).

Probe (runnable):

```
ls snippets/__init__.py scripts/snippets/__init__.py 2>&1   # both must not exist
grep -rn "import snippets\|from snippets\|importlib.*snippets\|__import__.*snippet" scripts/ tests/ --include="*.py"
grep -rn "snippets" scripts/code_exec.py | grep -i "import"
python3 - <<'PY'
import sys
# load code_exec, run a snippet via run_snippet, then check sys.modules
print([m for m in sys.modules if "snippet" in m])
PY
```

Plus a runtime trap: a fixture snippet file whose top level contains
`import os` (which validate_program must reject) is offered in the
manifest; run_snippet() for it must refuse via the AST scan, and no
import side effect may occur.

PASS: no __init__.py under either registry path, no grep hit for any
import of snippet files anywhere in scripts/ or tests/, sys.modules
gains no snippet module after a run_snippet call, and the
`import os` snippet is refused by the scan. FAIL: __init__.py
exists, any import hit is found, a snippet module appears in
sys.modules, or the `import os` snippet executes.

### Probe 9g: snippet file size cap

Setup: fixture snippet file larger than the snippet cap (8192 chars
expected; use the cap constant from 0.2 plus 1 char), otherwise valid
code (e.g. a long comment plus a trivial valid body), with correct
sha256 in the fixture manifest.

Probe: run_snippet() for that entry.

PASS: refused with a size error naming the snippet and the cap, never
executed (backend call count unchanged). FAIL: executes, or refuses
with a different error that does not name the size cap (record the
actual error; a refusal for the wrong reason is FAIL because the cap
is unenforced).

### Probe 9h: sha256 verified against the bytes executed

Setup: fixture manifest with a good entry whose sha256 matches its
file, plus two tampered variants: (a) same manifest entry but the
snippet file edited by one byte after the manifest was written
(hash mismatch), (b) manifest sha256 field edited by one hex digit
with the file untouched.

Probe: run_snippet() for each variant. For the positive control, run
the matching entry and confirm it executes.

PASS: the matching entry runs; both mismatched variants refuse with
a stale/hash-mismatch envelope naming the snippet and the expected
hash; no mismatched bytes execute (backend call count unchanged).
FAIL: either mismatched variant runs, or the refusal does not name
the snippet and the hash, or the implementation hashes the file at
load and reads it again at execution (time-of-check vs time-of-use:
inspect the loader source; read-once plus hash-the-bytes-read plus
execute-those-bytes is required; a load-time hash followed by a
second read at execution is FAIL).

## 2. Item 10: run_snippet inline execution, shared budgets, depth cap 1

Contract under test (redteam Attacks 7, 8d, 9e; amended synthesis):
run_snippet executes the snippet INLINE in the current run, sharing
the live api_calls counter, the live deadline, and the live trace
counter. It never calls run() recursively and never builds a nested
session. Depth cap is 1: a snippet may not call run_snippet. The
natural broken implementation (nested run()) resets every budget and
gives 32 outer calls times 32 inner calls = 1024 API calls and up to
16 minutes of wall time from one program; these probes must catch
exactly that amplification.

Setup for all item 10 probes: CU_CODE_EXEC=1; load code_exec by file
path; use FakeBackend / FakeDomBackend from tests.test_code_exec;
construct CodeExecSession directly so wall_seconds and max_api_calls
can be set small (constructor allows max_api_calls 1..32,
wall_seconds 1..60). Fixture snippets live under /tmp/y1b-fixtures/10/
with a fixture manifest per 0.3. Fixture snippet "two-windows":

```
wins = windows()
wins = windows()
```

Fixture snippet "slow-act" (for 10b) uses a backend whose act()
sleeps; see probe. Fixture snippet "calls-b" (for 10c) is a snippet
named "calls-b" whose body is `run_snippet("calls-a")`. Fixture
snippet "calls-a" is a trivial snippet that calls windows() once.

### Probe 10a: API-call budget is shared (loop amplification)

Setup: session = CodeExecSession(FakeBackend(), wall_seconds=30,
max_api_calls=6). Backend call counter: len(backend.calls).

Probe: one outer program calling run_snippet("two-windows") 5 times
in a loop. Each inner call does 2 windows() calls, so the naive
amplified total would be 10 backend windows() calls (plus the 5
run_snippet calls themselves if those also cost budget).

```
source = (
  "for i in range(5):\n"
  "    run_snippet(\"two-windows\")\n"
)
env = session.run(source)
```

PASS: env ok is False with an error naming the API call budget, and
len(backend.calls) <= 6 (the session cap; _api checks before
incrementing, so the backend can never see more than the cap). The
session api_calls counter after the run equals the cap (or the cap
plus the run_snippet calls if those are counted separately; record
the exact accounting). FAIL: env ok is True, or len(backend.calls)
> 6 (amplification proven: e.g. 10 windows calls served from a
max_api_calls=6 session), or the envelope reports api_calls reset
to a small number while the backend saw many more.

### Probe 10b: wall-clock deadline is shared (no fresh deadline)

Setup: a FakeBackend subclass whose act() sleeps 0.6 s per call.
Fixture snippet "slow-act": observe a window, then call act() 6
times with a trivial type action list. Session wall_seconds=2,
max_api_calls=32.

Probe: one outer program calling run_snippet("slow-act") twice in
sequence. Record time.monotonic() around session.run(), the envelope,
and the backend act call count.

```
source = (
  "run_snippet(\"slow-act\")\n"
  "run_snippet(\"slow-act\")\n"
)
```

PASS: the envelope is ok False with a wall-clock error; the second
run_snippet call adds ~0 backend act calls (it fails immediately on
the already-expired outer deadline); total elapsed is consistent
with one slow run plus a fast refusal, not two full slow runs.
White-box check: session._deadline after the first inner call is
unchanged from the outer run start (started + wall_seconds), not
reset to a later value. FAIL: the second call executes fully (fresh
deadline proven: act count grows by a second full set of 6 calls),
or elapsed is ~2x the single-run time with ok True, or _deadline
was reset by the inner call.

### Probe 10c: depth cap 1 (nested and mutual run_snippet rejected)

Setup: fixture snippets "calls-a" (body: `wins = windows()`) and
"calls-b" (body: `run_snippet("calls-a")`), plus a self-calling
snippet "calls-self" (body: `run_snippet("calls-self")`).

Probe: three outer programs, one per case: run_snippet("calls-b"),
run_snippet("calls-self"), and a program that calls run_snippet
twice in sequence at the top level (depth 1 each, legal control
that must succeed). Record backend.calls after each.

PASS: the nested and self cases return ok False with an error naming
the depth cap (or nested run_snippet), and backend.calls shows the
inner snippet body never executed (no windows() call attributable
to "calls-a" inside "calls-b"; zero extra calls for the self case).
The sequential top-level control succeeds. FAIL: any nested or self
call executes the inner body, or the error does not name the depth
rule, or the legal sequential control fails.

### Probe 10d: no nested run() and no nested session (white-box)

Setup: none beyond code_exec import.

Probe: two parts. (a) Static: grep the run_snippet implementation
for calls to self.run(, run_program(, and CodeExecSession(.

```
grep -n "self\.run(\|run_program(\|CodeExecSession(" scripts/code_exec.py
```

(b) Runtime tripwire: wrap CodeExecSession.run with a counting
wrapper, then invoke the outer program through the saved original
function so only nested calls trip the counter.

```
orig = code_exec.CodeExecSession.run
calls = []
def counting(self, *a, **k):
    calls.append(1)
    return orig(self, *a, **k)
code_exec.CodeExecSession.run = counting
try:
    env = orig(session, "run_snippet(\"two-windows\")\n")
finally:
    code_exec.CodeExecSession.run = orig
assert calls == [] and env["ok"] is True
```

Also tripwire run_program the same way: monkeypatch
code_exec.run_program to raise, run the outer program via
session.run, and confirm it still succeeds.

PASS: no static hit inside the run_snippet code path, the counting
wrapper records 0 nested run() calls, and the run_program tripwire
is never hit. FAIL: any static hit in the run path, or calls != [],
or the tripwire fires. (A static hit in dead code elsewhere in the
file is not a FAIL; only hits reachable from run_snippet count.
Record the line numbers.)

### Probe 10e: inline namespace (snippet sees outer variables)

Setup: fixture snippet "uses-title" whose body reads a variable
named terminal_title set by the outer program and uses it as the
observe window title lookup key (e.g. picks the window whose title
equals terminal_title from windows(), then observes it).

Probe: outer program sets terminal_title = "speed-pick1-term",
then calls run_snippet("uses-title"). FakeBackend returns a window
with that title.

PASS: the snippet runs and observes the right window (backend
observe_window called with address 0xabc). FAIL: NameError inside
the snippet (fresh namespace proven), or the wrong window observed.
Note: probe 11c/11d separately require that the snippet's own
params and new variables do NOT leak back out; 10e only checks the
inward visibility of outer variables.

### Probe 10f: trace-step budget is shared (snippet lines count)

Setup: fixture snippet "many-lines" whose body loops 25000 times
doing one simple assignment per iteration (e.g. `for i in
range(25000): x = i`). Session defaults (MAX_TRACE_STEPS 20000).

Probe: outer program calls run_snippet("many-lines") once.

PASS: envelope ok False with "trace step budget exceeded", and the
failure happens near 20000 steps, not after all 25000 iterations.
FAIL: envelope ok True (snippet lines not counted toward the outer
trace budget). Implementation note for Y1b: the _trace filter counts
only frames whose filename is PROGRAM_FILENAME; if Codex compiles
snippet code under a different filename (e.g. "<snippet:...>"), the
filter must be extended to count snippet frames too, or this probe
fails by construction. If this probe FAILS, check the compile
filename first and record it.

## 3. Item 11: params, persistent variables, per-run bindings

Contract under test (redteam Attacks 5b, 7c, 9c; amended synthesis):
param names colliding with the API allowlist are rejected; params are
bound as frame locals, never into persistent session variables;
persistent variables are snapshotted on run_snippet entry and
restored on exit except for one explicitly declared output; params
are never interpolated into snippet source; observation and DOM
bindings are scoped per snippet run, so a snippet calling act() or
dom_act() without its own fresh observe fails loudly.

The API allowlist for collision checks is scripts/code_exec.py
lines 270-276 in the pre-Codex baseline (windows, observe, act,
read_file, assert_state, assert_file_contains, assert_file_exists,
dom_start, dom_tabs, dom_observe, dom_act, dom_assert, plus
run_snippet itself and print). Probe 11a must read the allowlist from
the implementation at verification time, not from this file.

### Probe 11a: allowlist collisions rejected (params and names)

Setup: fixture manifest entries, one per colliding name, each with a
param named after an API function (windows, act, observe, read_file,
assert_state, dom_act, run_snippet, print) and one entry whose
snippet NAME collides with an API name (name "windows", and name
"act"). Snippet bodies are trivial and valid.

Probe: load the fixture manifest, list offered snippets, and attempt
run_snippet() for each colliding entry.

PASS: every colliding entry is rejected at manifest load (logged
error, never offered in search, never runnable), and run_snippet()
for each refuses with a collision error. FAIL: any colliding entry
loads and is offered, or runs, or a param shadows the API at runtime
(see 11b for the live shadowing symptom).

### Probe 11b: param shadowing symptom is impossible (live test)

Setup: a fixture snippet that would shadow if 11a failed: manifest
entry with param "windows" default "x" (this entry must already have
been rejected by 11a; this probe is the defense-in-depth check that
a hand-built loader bypass cannot produce shadowing). If the loader
refuses the entry outright, this probe is satisfied by that refusal
plus the control below. Control: a legal snippet with param
"terminal_title" whose body calls windows() and then act().

Probe: attempt the shadowing entry; run the control snippet with
terminal_title="speed-pick1-term".

PASS: the shadowing entry never runs (load refusal), and the control
snippet's windows() call still returns the FakeBackend window list
(the API was not shadowed) and act() executes on the observed
window. FAIL: the shadowing entry runs and its windows() call hits
the param value (TypeError calling a string, or any behavior other
than the real API), or the control snippet's API calls are affected
by the param.

### Probe 11c: params are frame locals, not persistent variables

Setup: fixture snippet "with-param" with one param terminal_title
(default "speed-pick1-term"), body observes the window matching
terminal_title and sets nothing else. Session starts with empty
variables.

Probe: run the snippet with terminal_title="speed-pick1-term", then
inspect session.variables, then run a second program that reads
terminal_title.

```
env = session.run("run_snippet(\"with-param\", terminal_title=\"speed-pick1-term\")\n")
assert "terminal_title" not in session.variables
env2 = session.run("x = terminal_title\n")
assert env2["ok"] is False   # NameError, param did not persist
```

PASS: the snippet runs (param visible inside it), session.variables
has no terminal_title after the run, and the second program fails
with NameError. FAIL: terminal_title appears in session.variables
or is readable by the second program.

### Probe 11d: snapshot and restore of persistent variables

Setup: fixture snippet "poisoner" with no params whose body sets
shared = "poison" and fresh = 1. Second fixture snippet
"with-output" with a declared output (manifest field name per 0.2,
e.g. outputs: ["result"]) whose body sets result = 42 and also sets
shared = "poison". If Codex implements no declared-output mechanism,
the second half of this probe is recorded as a deviation and the
first half still applies.

Probe:

```
env0 = session.run("shared = \"before\"\n")
env = session.run("run_snippet(\"poisoner\")\n")
assert env["ok"] is True
assert session.variables.get("shared") == "before"
assert "fresh" not in session.variables
env = session.run("run_snippet(\"with-output\")\n")
assert session.variables.get("result") == 42
assert session.variables.get("shared") == "before"
```

PASS: after each run, shared is still "before", fresh is absent, and
only the declared output result propagates with value 42. FAIL: shared
is "poison", or fresh persists, or an undeclared variable leaks out,
or the declared output does not propagate (record which half failed).

### Probe 11e: observation bindings scoped per snippet run (act)

Setup: fixture snippet "bare-act" whose body calls act() with a
trivial action list and no observe call of its own. Fixture snippet
"observe-then-act" (positive control) whose body observes window
0xabc and then acts on that observation. Outer program observes first
(FakeBackend window 0xabc), then calls the bare-act snippet.

Probe: record backend act call count before and after each call.

```
# outer program 1: observe, then run_snippet("bare-act")
# outer program 2: run_snippet("observe-then-act")
```

PASS: program 1 returns ok False with an error stating act needs an
observation from inside this snippet run (or equivalent per-run
binding error), and the backend act count does not grow. Program 2
succeeds and the backend act count grows by exactly 1. FAIL: program
1 acts on the outer program's observation (act count grows, envelope
ok True), or program 2 fails (scoping implemented as a blanket ban
rather than per-run scoping).

### Probe 11f: DOM bindings scoped per snippet run (dom_act)

Setup: FakeDomBackend. Fixture snippet "bare-dom-act" whose body
calls dom_act() with a snapshot variable it never observed. Fixture
snippet "dom-observe-then-act" (positive control) whose body calls
dom_observe("tab-1") then dom_act() on the returned snapshot.
Outer program calls dom_observe("tab-1") first, then the bare
snippet.

Probe: same shape as 11e, counting backend dom_calls.

PASS: the bare snippet fails loudly (DOM snapshot not bound to this
run, or equivalent), dom_calls does not grow; the control snippet
succeeds with exactly one dom_act backend call. FAIL: the bare
snippet acts on the outer program's snapshot, or the control fails.

### Probe 11g: snippet-to-snippet binding isolation

Setup: fixture snippets "first-observer" (observes window 0xabc)
and "second-bare-act" (calls act() with no observe). One outer
program calls them in sequence.

Probe: run the sequence; record envelope and backend act count.

PASS: the second snippet fails with a per-run binding error and no
act is performed, even though the first snippet observed
successfully in the same outer program. FAIL: the second snippet
acts on the first snippet's observation.

### Probe 11h: params never interpolated into snippet source

Setup: fixture snippet "echo-param" with param text (string) whose
body does `print(text)` and sets out = text. Call it with a param
value carrying an injection payload, e.g.
text = "x\"); import os; (" (code-shaped string) and a second call
with text = "{0.__class__}".format-style content.

Probe: run both calls; inspect the envelope, session.variables, and
confirm no import, no dunder access, and no code execution occurred
(the scan must have run on the snippet source as written, and the
param must have arrived as a plain string value).

PASS: both calls succeed with out equal to the literal param string,
no CodeExecError about banned names is raised by the payload itself
(the payload is data, not code), and nothing executes. FAIL: any
part of the payload executes (import, attribute access, or a scan
error triggered by the param value proves interpolation into source
before scanning).

## 4. Item 12: expiry (30 days live_only, 90 days VM-verifiable)

Contract under test (redteam Attack 6c; amended synthesis majority
C1+C3): live_only snippets expire after 30 days; VM-verifiable
snippets expire after 90 days; an age-stale snippet is excluded from
search and refused at run time by default; allow_stale=True is a
diagnostic override only, and its use is logged; last_verified is
updated only by a verification run, never by hand or by a snippet
run. Age is computed from last_verified to today (UTC date).

Setup for all item 12 probes: fixture manifests with entries whose
last_verified dates are set relative to today (compute dates in the
probe from datetime.date.today() so the probe never goes stale
itself): 29 and 31 days ago for live_only, 89 and 91 days ago for
VM-verifiable, plus a missing-last_verified entry and an unparseable
date entry. Fixture snippets are trivial FakeBackend snippets.
Search/listing entry point is whatever the implementation exposes
(record it in 0.2); if search lives in codemode search_ops, probe
it there too.

### Probe 12a: live_only 30-day boundary

Setup: entries "live-fresh" (live_only true, last_verified 29 days
ago) and "live-stale" (live_only true, last_verified 31 days ago).

Probe: run_snippet() for each; list search results and check for
each name.

PASS: live-fresh runs (ok True); live-stale refuses with an error
naming the snippet, its last_verified, and its age (or the word
stale/expired), and is absent from search results. FAIL: live-stale
runs, or is listed as usable, or the refusal does not name the
snippet and its age. Boundary note: exactly 30 days is
implementation-defined; record what Codex does at exactly 30 days
(refuse or run) without failing the probe on it, but a 31-day run is
an unconditional FAIL.

### Probe 12b: VM-verifiable 90-day boundary

Setup: entries "vm-fresh" (live_only false or absent, last_verified
89 days ago) and "vm-stale" (live_only false or absent, last_verified
91 days ago).

Probe: same as 12a.

PASS: vm-fresh runs; vm-stale refuses with a named age error and is
absent from search. FAIL: vm-stale runs or is listed. Boundary note:
same as 12a, at exactly 90 days record the behavior without failing
on it; 91 days running is an unconditional FAIL.

### Probe 12c: age-stale refusal is a refusal, not a warning plus run

Setup: the live-stale and vm-stale entries from 12a/12b.

Probe: run_snippet() for each and inspect the full envelope.

PASS: envelope ok is False, error names the snippet and states
stale/expired, and the backend call count does not grow (no snippet
code executed at all, not even partially). FAIL: ok True, or the
envelope carries a warning while the snippet still ran, or any
backend call was made before the refusal.

### Probe 12d: allow_stale=True diagnostic override only, logged

Setup: the live-stale entry (31 days, live_only).

Probe, in order:

```
env1 = session.run("run_snippet(\"live-stale\", allow_stale=True)\n")
# check env1 ok True AND the run is logged (log_lines contain
# "stale" and "live-stale", or a log record/file entry does)
env2 = session.run("run_snippet(\"live-stale\")\n")
# env2 must refuse again (override did not persist)
```

Also check the manifest cannot set the override: a fixture entry
with a manifest field allow_stale true (or equivalent) must be
ignored or rejected at load, and a plain run_snippet() call for it
must still refuse.

PASS: the override call runs once, the stale use is logged with the
snippet name, the next default call refuses again, and a manifest
allow_stale field does not enable running. FAIL: the override does
not exist (no way to run a stale snippet diagnostically), the
override run is not logged anywhere inspectable, the override
persists to the next call, or the manifest field enables it.

### Probe 12e: last_verified is not rewritten by a snippet run

Setup: fixture manifest with a fresh entry; record the manifest
file bytes and sha256 before running.

Probe: run_snippet() for the fresh entry (success path), then
re-read the manifest file and compare bytes. Also grep the
implementation for writes to last_verified outside the designated
verifier (tests/test_snippets.py or the verification script named
in 0.2).

```
grep -rn "last_verified" scripts/ tests/ --include="*.py"
sha256sum snippets/manifest.json   # before and after the run
```

PASS: manifest bytes unchanged after the run, and the only code
that writes last_verified is the verification run itself (test or
designated verifier script), never run_snippet or the loader.
FAIL: the run rewrites the manifest, or run_snippet/loader code
updates last_verified.

### Probe 12f: search excludes age-stale snippets

Setup: fixture manifest mixing fresh and stale entries (live and VM
kinds from 12a/12b).

Probe: call the search/listing entry point (snippet search in
code_exec or codemode search_ops, per 0.2) with a query matching all
of them (e.g. a shared tag), and list the returned names.

PASS: fresh entries appear, stale entries are absent from every
search result. FAIL: any stale entry is listed as usable (a stale
entry listed with a visible stale flag but still runnable is FAIL;
a stale entry listed only in a separate "stale, not runnable"
section is acceptable only if run_snippet still refuses it, and
must be recorded).

### Probe 12g: missing last_verified fails closed

Setup: fixture entry with no last_verified field at all (and no
verified_against either).

Probe: run_snippet() for it; check search listing.

PASS: refuses with a stale/missing-verification error and is absent
from search. FAIL: runs, or is listed as usable.

### Probe 12h: unparseable last_verified fails closed, no crash

Setup: fixture entry with last_verified "yesterday-ish" (not an ISO
date) and a second variant with last_verified "2026-13-45".

Probe: run_snippet() for each; then run a good entry to prove the
registry still works.

PASS: each refuses with an error (stale or invalid date), no
uncaught exception escapes, and the good entry still runs. FAIL:
either runs, or an exception escapes run_snippet, or the registry
breaks for later calls.

## 5. Phase C: test_cursor_session.py nesting fix

Contract under test (Y1 log 17:50 and 17:56): the file is currently
UNIMPORTABLE on the VM (SyntaxError "too many statically nested
blocks" line 566, Python 3.12.3; parses fine on laptop Python
3.14.10), so its 33 tests never run on the VM. The fix must reduce
static nesting while keeping behavior identical. The named defect
is test_cleanup_exceptions_cannot_skip_restore (giant with-chain
plus nested with, lines 561-571). No test may be deleted, renamed,
weakened, or skipped to make the file import.

### Probe C1: the file imports on the VM

Setup: repo at todolist-push with Codex's Phase C fix merged in; VM
Python 3.12.3.

Probe (runnable):

```
cd ~/workspace/computer-use-wayland
python3 -c "import tests.test_cursor_session; print('import ok')"
python3 -m py_compile tests/test_cursor_session.py && echo "py_compile ok"
```

PASS: both commands succeed with no SyntaxError. FAIL: any
SyntaxError, including a differently-worded nesting error at a new
line, or an ImportError introduced by the refactor.

### Probe C2: all 33 tests run and pass on the VM

Setup: same as C1. Note the pre-fix VM baseline: the module never
imported, so there is no passing baseline to regress against; the
laptop baseline is 33 tests (O2's suite count implies the module ran
there). The VM run must collect exactly 33 tests.

Probe (runnable):

```
cd ~/workspace/computer-use-wayland
python3 -m unittest tests.test_cursor_session -v 2>&1 | tee /tmp/y1b-phase-c.log
grep -c "def test" tests/test_cursor_session.py   # must print 33
tail -5 /tmp/y1b-phase-c.log
```

PASS: the run reports Ran 33 tests with OK (0 failures, 0 errors).
Skips are allowed ONLY for the documented environment reason: the
lua test (test_lua_string_literals_roundtrip_utf8_controls_and_digits)
may skip if `lua` is not installed on the VM (skipUnless); any other
skip must name its reason in the log and is recorded as a finding,
and a skipped count above 1 fails the probe. FAIL: fewer than 33
tests collected, any failure or error, more than 1 skip, or a skip
with no stated reason.

### Probe C3: behavior-identical refactoring (diff review)

Setup: the pre-fix file from git (git show HEAD:tests/
test_cursor_session.py or the merge-base version before Codex's
Phase C commit; record the exact commit used).

Probe (runnable):

```
cd ~/workspace/computer-use-wayland
git diff <pre-fix-commit> -- tests/test_cursor_session.py > /tmp/y1b-phase-c.diff
wc -l /tmp/y1b-phase-c.diff
git show <pre-fix-commit>:tests/test_cursor_session.py | grep "def test" | sort > /tmp/y1b-tests-before.txt
grep "def test" tests/test_cursor_session.py | sort > /tmp/y1b-tests-after.txt
diff /tmp/y1b-tests-before.txt /tmp/y1b-tests-after.txt && echo "test names identical"
grep -c "assert" tests/test_cursor_session.py
git show <pre-fix-commit>:tests/test_cursor_session.py | grep -c "assert"
```

Review checklist (manual, line by line over the diff; the reviewer
signs each line in the verification log):
1. Test names identical (the diff above must be empty).
2. No assert removed, weakened (e.g. assertEqual replaced by a
   weaker check), or commented out; assert counts before and after
   must match unless the reviewer records a justification per line.
3. The same objects are patched with the same targets in
   test_cleanup_exceptions_cannot_skip_restore (patch.object on
   session.signal signal, session STATE/SNAPSHOT/CANCEL, owner_lock,
   cancel_hotkey hotkey_on/hotkey_off, request_stop, stop_group,
   drain_input, restore, select, os.read, the failing cleanup
   function, cursor_theme snapshot/check_guard/apply, indicator
   Native/listen), and the same assertions run (guardian returns 1,
   restore called once with the env, snapshot unlinked).
4. No new skip, skipIf, skipUnless, or expectedFailure added.
5. No timeout loosened, no retry count changed, no helper behavior
   changed (helpers shared with other tests must be untouched or
   proven equivalent).
6. The nesting reduction is structural (helper function, loop, or
   flattened with-chain), not achieved by deleting coverage.

PASS: all six checklist lines hold, with the diff reviewed and
signed in the log. FAIL: any test renamed, removed, or weakened;
any assert count change without a recorded justification; any new
skip; any helper behavior change. A pure formatting reflow with
identical semantics is PASS; a semantic change of any kind is FAIL.

### Probe C4: nesting is actually reduced (not just moved)

Setup: same as C1.

Probe (runnable):

```
python3 - <<'PY'
import ast, pathlib
tree = ast.parse(pathlib.Path("tests/test_cursor_session.py").read_text())
def depth(node, d=0):
    best = d
    for child in ast.iter_child_nodes(node):
        best = max(best, depth(child, d + 1 if isinstance(child, (ast.With, ast.Try, ast.For, ast.If, ast.FunctionDef)) else d))
    return best
print("max nesting depth:", depth(tree))
PY
python3 -m py_compile tests/test_cursor_session.py && echo "3.12 compile ok"
```

PASS: py_compile succeeds on VM Python 3.12.3, and the reported max
nesting depth is lower than the pre-fix file's depth (compute the
same number on the pre-fix file from git and record both). FAIL:
py_compile fails, or the depth is unchanged (the fix only shuffled
lines without reducing nesting), or the nesting was reduced by
deleting code (see C3).

### Probe C5: no collateral damage to neighboring tests

Setup: same as C1.

Probe (runnable):

```
cd ~/workspace/computer-use-wayland
python3 -m unittest tests.test_cursor_session tests.test_code_exec 2>&1 | tail -3
```

PASS: test_cursor_session reports 33 tests OK per C2, and
test_code_exec shows no new failures versus the Y1 baseline
(1483 tests, 0 failures, 2 errors, both VM toolchain gaps: g++
C++26 and this module's import; with the import fixed, the
remaining known error is the g++ one only). FAIL: any new failure
or error in either module beyond the known g++ toolchain gap.

## 6. Laptop-only probes (VM cannot run these; reason stated)

L-1. Phase C Python 3.14 parse check. Reason: the VM has only
Python 3.12.3, so it cannot prove the refactored file still parses
on the laptop's Python 3.14.10. Laptop probe: `python3 -m
py_compile tests/test_cursor_session.py` plus `python3 -m unittest
tests.test_cursor_session` on the laptop, expecting the same 33
tests OK. A VM PASS on C1/C2 does not substitute for this; the
laptop run is required before merge.

L-2. Live-desktop confirmation of the live_only 30-day expiry
(probe 12a on real hardware). Reason: the VM expiry probes use
FakeBackend, which proves the runner enforces the date rule but not
that a real live_only snippet on the laptop (real terminal, real
act) is refused when stale. Laptop probe: repeat 12a with a real
live_only snippet in the laptop live-test lane; stale must refuse
before any desktop action happens (no window focused, no keystroke
sent). VM PASS on 12a is sufficient for the item verdict; L-2 is a
supplementary live confirmation.

L-3. Live P1-P4 verification runs. Reason: P1-P4 are live_only and
need a real terminal on the laptop; the VM cannot execute them.
Out of scope for items 9-12 and Phase C, listed here only so the
gap is explicit: no live_only snippet is promotable on VM evidence
alone.

## 7. Probe inventory (for the Y1b log)

| Item | Probes | VM-runnable |
| 9 Manifest loading | 9a size cap, 9b duplicates, 9c per-entry fail-closed, 9d malformed JSON, 9e code_path containment, 9f text-only/no __init__.py, 9g snippet size cap, 9h sha256 | all yes |
| 10 Inline execution | 10a API budget sharing, 10b wall deadline sharing, 10c depth cap 1, 10d no nested run/session, 10e inline namespace, 10f trace sharing | all yes |
| 11 Params and bindings | 11a allowlist collisions, 11b shadowing symptom, 11c frame locals, 11d snapshot/restore, 11e observation scoping, 11f DOM scoping, 11g snippet-to-snippet isolation, 11h no interpolation | all yes |
| 12 Expiry | 12a live_only 30 days, 12b VM 90 days, 12c refusal not warning, 12d allow_stale override logged, 12e last_verified not rewritten, 12f search exclusion, 12g missing date fails closed, 12h bad date fails closed | all yes |
| Phase C | C1 import on VM, C2 all 33 tests pass, C3 behavior-identical diff review, C4 nesting reduced, C5 no collateral damage | C1-C5 yes; L-1 laptop parse check supplementary |

End of probe specs. Y1b verdicts go in improvements/worker-y1b-verify.md
(or the Y1b log), not in this file.
