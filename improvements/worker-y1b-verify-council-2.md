# Verification probes: Council Member 2 (Worker Y1b panel)

Date: 2026-11-21. Author: Council Member 2 of the Worker Y1b verification panel.
Parent: Y1b (Worker Y1b). Scope: must-fix items 5-8 only (the snippet-design fixes).
Branch: todolist-push (this file). Code under test: Codex branch y1-snippets.
Repo: ~/workspace/computer-use-wayland.

## Status note (read first)

As of 2026-11-21 about 18:05 +07, origin/y1-snippets is at 87cd34f
("docs: record Y1 implementation setup") and contains NO snippet code yet:
no snippets/ directory, no run_snippet in scripts/code_exec.py. Codex is
still implementing Phase A + Phase B on the laptop. These probes are
therefore written against the FIXED CONTRACT from the council synthesis
(Y1 log, 17:58 section) and the redteam report, not against Codex's
unseen internal names. Y1b must fetch the latest y1-snippets before
running anything: `git fetch origin y1-snippets` then check out that
branch in a worktree (never on todolist-push). If a probe's entry point
does not exist in the fetched code, that probe FAILS with reason
"interface missing", it is never skipped and never adapted silently.

Contract the probes assume (all from the council synthesis + redteam fix
list; if Codex implemented a different contract, the probe FAILS and Y1b
reports the contract mismatch to Y1, it does not rewrite the probe):

- Registry location is top-level snippets/ (council majority; redteam
  scripts/snippets/ paths map to it). Manifest is snippets/manifest.json.
  A probe resolves SNIPPETS_DIR as snippets/ if it exists, else
  scripts/snippets/ if that exists, else FAILS. It records which one it used.
- run_snippet(name, **params) is an allowlisted code_exec API name, callable
  inside a program, executing INLINE in the current session with shared
  api_calls, deadline, and trace counter. Never a nested run() or session.
- Manifest entries carry sha256 of the snippet file bytes, a runtime API
  hash for staleness (never a git commit), last_verified, requires_approval,
  params, code_path contained under the snippets directory.
- Params are JSON types only, bound as frame locals, never interpolated
  into source. Persistent session variables are snapshotted and restored
  around a snippet run except for one declared output.
- Observation and DOM bindings are scoped per snippet run. A snippet that
  calls act() or dom_act() without its own fresh observe fails loudly.
- Manifest loading is fail-closed per entry. Duplicate names are rejected.
  Size caps are enforced in run_snippet, not only in CI.
- The loader reads snippet files as text only, never imports them.

## How to run

1. Fetch and check out y1-snippets in a worktree. Set REPO to that worktree
   path in every probe (default in the harness is the todolist-push checkout;
   pass the worktree path as argv[1] or edit REPO).
2. Save the harness block below as /tmp/y1b-probes/harness.py.
3. Save each probe block as the /tmp/y1b-probes/pXX_*.py file named in its
   first comment line. Or extract them all at once with the extractor in
   the Setup section below.
4. Run each probe with python3. Each probe prints exactly one line
   starting with PASS or FAIL plus a reason, and exits 0 on PASS, 1 on FAIL.
5. A probe that cannot find its entry point prints FAIL "interface missing:
   <what>" and exits 1. A probe that needs the laptop prints LAPTOP-ONLY
   and exits 2 (not counted as PASS, not counted as FAIL; Y1b runs it on
   the laptop lane separately).
6. Probes that mutate a manifest or a snippet file ALWAYS work on a temp
   copy of the tree (harness.temp_tree()), never on the real registry.
   The only probes that touch the real tree are read-only checks (grep,
   manifest schema read). No probe writes to the real snippets/ directory.
7. CU_CODE_EXEC=1 is not needed for these probes: they call
   CodeExecSession.run() directly, and the flag only gates scripts/cu.py.
   No probe touches the laptop, Zen, Chromium, or the network, except the
   probes explicitly marked LAPTOP-ONLY.

## Setup: extractor

Save this spec file's fenced python blocks to /tmp/y1b-probes/ with:

```bash
mkdir -p /tmp/y1b-probes
python3 - <<'EOF'
import pathlib, re
text = pathlib.Path('improvements/worker-y1b-verify-council-2.md').read_text()
out = pathlib.Path('/tmp/y1b-probes')
for m in re.finditer(r'```python\n# probe (\S+)\n(.*?)```', text, re.S):
    name, body = m.group(1), m.group(2)
    (out / name).write_text('# probe ' + name + '\n' + body)
    print('wrote', name)
(out / 'harness.py').write_text(
    re.search(r'```python\n# harness\n(.*?)```', text, re.S).group(1))
print('wrote harness.py')
EOF
python3 -m py_compile /tmp/y1b-probes/*.py && echo COMPILE_OK
```

## Harness (shared by every probe)

```python
# harness
"""Shared harness for Y1b council-2 probes. Imported as: sys.path.insert(0, '/tmp/y1b-probes'); import harness as H."""
import datetime
import hashlib
import importlib.util
import json
import pathlib
import shutil
import sys
import tempfile
import time

REPO = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path('~/workspace/computer-use-wayland')

def load_code_exec(tree=None):
    tree = pathlib.Path(tree) if tree else REPO
    path = tree / 'scripts' / 'code_exec.py'
    if not path.is_file():
        raise FileNotFoundError('no scripts/code_exec.py under ' + str(tree))
    spec = importlib.util.spec_from_file_location('code_exec_under_test', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def snippet_dir(tree=None):
    tree = pathlib.Path(tree) if tree else REPO
    for cand in (tree / 'snippets', tree / 'scripts' / 'snippets'):
        if cand.is_dir():
            return cand
    return None

def manifest_path(tree=None):
    d = snippet_dir(tree)
    return (d / 'manifest.json') if d is not None else None

def read_manifest(tree=None):
    p = manifest_path(tree)
    return json.loads(p.read_text(encoding='utf-8'))

def write_manifest(tree, data):
    p = manifest_path(tree)
    p.write_text(json.dumps(data, indent=2), encoding='utf-8')

def manifest_entries(tree=None):
    data = read_manifest(tree)
    if isinstance(data, dict):
        return data.get('snippets', data)
    return data

def sha256_file(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()

def snippet_file(tree, entry):
    """Resolve an entry code_path: bare filename under the snippets dir, or a path relative to the tree root."""
    d = snippet_dir(tree)
    cp = entry['code_path']
    for cand in (d / cp, pathlib.Path(tree) / cp):
        if cand.is_file():
            return cand
    return d / cp

def clone_entry(tree, name, code_path, params=None, **overrides):
    """Build a new manifest entry by cloning the first real entry's metadata (runtime hash, verified_against,
    last_verified set to today) and overriding only the attacked fields. This keeps the entry valid except
    for the property under test, so a refusal proves the attacked property caused it."""
    entries = manifest_entries(tree)
    first = entries[0] if isinstance(entries, list) else entries[list(entries)[0]]
    evil = dict(first)
    evil.update({'name': name, 'code_path': code_path, 'params': params or [],
                 'last_verified': datetime.date.today().isoformat()})
    evil.update(overrides)
    target = snippet_file(tree, {'code_path': code_path})
    if target.is_file():
        evil['sha256'] = sha256_file(target)
    return evil

def add_entry(tree, entry):
    data = read_manifest(tree)
    entries = data['snippets'] if isinstance(data, dict) and 'snippets' in data else data
    if isinstance(entries, list):
        entries.append(entry)
    else:
        entries[entry['name']] = entry
    write_manifest(tree, data)

def temp_tree():
    """Copy scripts/code_exec.py plus the snippets dir into a temp tree. Returns the temp path."""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix='y1b-tree-'))
    (tmp / 'scripts').mkdir(parents=True)
    shutil.copy2(REPO / 'scripts' / 'code_exec.py', tmp / 'scripts' / 'code_exec.py')
    src = snippet_dir()
    if src is not None:
        shutil.copytree(src, tmp / 'snippets')
    return tmp

def call_snippet(mod, session, name, params=None):
    """Call run_snippet from inside a program. Returns the envelope."""
    params = params or {}
    args = ', '.join('%s=%s' % (k, repr(v)) for k, v in params.items())
    src = 'r = run_snippet(%s%s)' % (json.dumps(name), (', ' + args) if args else '')
    return session.run(src)

def call_snippet_approved(mod, session, name, params=None):
    """Call run_snippet, using the approval channel Codex implemented if the entry needs it.
    Raises InterfaceMissing when requires_approval is set but no approval path exists."""
    params = params or {}
    env = call_snippet(mod, session, name, params)
    if env['ok']:
        return env
    err = (env.get('error') or '').lower()
    if 'approv' not in err:
        return env
    src = pathlib.Path(mod.__file__).read_text(encoding='utf-8')
    if 'approved' in src:
        args = ', '.join('%s=%s' % (k, repr(v)) for k, v in params.items())
        src2 = 'r = run_snippet(%s%s, approved=True)' % (json.dumps(name), (', ' + args) if args else '')
        env2 = session.run(src2)
        if env2['ok'] or 'approv' not in (env2.get('error') or '').lower():
            return env2
    if hasattr(session, 'approved_snippets'):
        session.approved_snippets.add(name)
        return call_snippet(mod, session, name, params)
    raise InterfaceMissing('requires_approval is enforced but no approval path exists in code_exec.py')

class InterfaceMissing(Exception):
    pass

class FakeBackend:
    """Stand-in for the cu.py brokered primitives; records calls. Copied semantics from tests/test_code_exec.py."""
    def __init__(self, windows=None):
        self.calls = []
        self.act_calls = []
        self.meta = {'id': 'abcdef012345', 'image': '/tmp/x.png', 'observation': '/tmp/x.json',
                     'window': '0xabc', 'window_bounds': [0, 0, 800, 600], 'image_size': [800, 600],
                     'region': [0, 0, 800, 600], 'monitor': 'eDP-2', 'created': time.time()}
        self._windows = windows if windows is not None else [
            {'address': '0xabc', 'class': 'kitty', 'title': 'speed-pick1-term',
             'at': [0, 0], 'size': [800, 600], 'workspace': {'id': 1}}]
    def windows(self):
        self.calls.append(('windows',))
        return [dict(w) for w in self._windows]
    def observe_window(self, address, crop, max_width):
        self.calls.append(('observe_window', address, crop, max_width))
        meta = dict(self.meta)
        meta['id'] = 'obs-%d' % len(self.calls)
        meta['created'] = time.time()
        return meta
    def observe_screen(self, monitor, crop, max_width):
        self.calls.append(('observe_screen', monitor, crop, max_width))
        return dict(self.meta)
    def act(self, meta, actions, observation_path):
        self.calls.append(('act', meta['id'], actions, observation_path))
        self.act_calls.append(actions)
        return {'ok': True, 'completed': len(actions)}

class RefusingBackend(FakeBackend):
    """act() always refuses: simulates the shell never running the typed command."""
    def act(self, meta, actions, observation_path):
        self.calls.append(('act', meta['id'], actions, observation_path))
        self.act_calls.append(actions)
        return {'ok': False, 'completed': 0, 'error': 'screen changed', 'error_code': 'screen_changed'}

class FakeDomBackend(FakeBackend):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.dom_calls = []
        self.snapshot_count = 0
        self.current_url = 'file:///fixture'
    def dom_start(self):
        self.dom_calls.append(('start',))
        return {'ok': True, 'endpoint': 'http://127.0.0.1:9222', 'reused': True}
    def dom_tabs(self):
        self.dom_calls.append(('tabs',))
        return [{'id': 'tab-1', 'title': 'fixture', 'url': self.current_url}]
    def _snapshot(self, target):
        self.snapshot_count += 1
        n = self.snapshot_count
        return {'snapshot': 'dom-snapshot-%d' % n, 'title': 'fixture', 'url': self.current_url,
                'elements': [{'ref': 'dom-ref-%d' % n, 'role': 'button', 'name': 'Create'}],
                'truncated': False, 'iframes': 0}
    def dom_observe(self, target, scope, max_elements):
        self.dom_calls.append(('observe', target, scope, max_elements))
        return self._snapshot(target)
    def dom_act(self, target, snapshot, actions, after_scope=None, no_after=False):
        self.dom_calls.append(('act', target, snapshot, actions, after_scope, no_after))
        result = {'ok': True, 'completed': len(actions)}
        if not no_after:
            result['after'] = self._snapshot(target)
        return result

def verdict(ok, reason):
    print(('PASS' if ok else 'FAIL') + ': ' + reason)
    raise SystemExit(0 if ok else 1)

def verdict_laptop(reason):
    print('LAPTOP-ONLY: ' + reason)
    raise SystemExit(2)

def need_run_snippet(mod):
    """Confirm run_snippet is an allowlisted program name. Returns the session class otherwise raises."""
    try:
        mod.validate_program('run_snippet("x")')
    except Exception as exc:
        raise InterfaceMissing('run_snippet is not an allowlisted program name: ' + str(exc))
```

---

## ITEM 5: Snippet trust (redteam Attack 5)

Redteam evidence this must defeat: manifest carries reviewed_by,
reviewed_on, last_verified, verified_against but no hash of the snippet
.py content; a one-line edit changes what run_snippet executes with zero
signal; CI only py_compiles live_only snippets and never executes them.
Param named windows/act shadows the API. A snippet can read a file and
type it out through act(). A param used as a format string hands the
attacker the Attack 1 hole.

Setup for all item 5 probes: y1-snippets worktree checked out; a temp
tree from H.temp_tree() for every probe that edits a snippet or the
manifest; at least one manifest entry must exist (P1-P4 migrated). If
no manifest entry exists, every item 5 probe FAILS "no snippet to test".

### Probe 5a: edited snippet after promotion is refused by hash

Attack: edit one line of a promoted snippet .py file after the manifest
recorded its sha256, then call run_snippet. The redteam version of this
attack succeeds silently because there is no hash at all.

```python
# probe p5a_hash_mismatch.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
entries = H.manifest_entries(tree)
assert entries, 'no manifest entries to test'
name = entries[0]['name'] if isinstance(entries, list) else list(entries)[0]
entry = entries[0] if isinstance(entries, list) else entries[name]
path = H.snippet_file(tree, entry)
if 'sha256' not in entry:
    H.verdict(False, '5a: manifest entry %s has no sha256 field' % name)
if entry['sha256'] != H.sha256_file(path):
    H.verdict(False, '5a: manifest sha256 does not match file bytes for %s even before edit' % name)
text = path.read_text(encoding='utf-8')
path.write_text(text + '\n# tampered after promotion\n', encoding='utf-8')
backend = H.FakeBackend()
session = mod.CodeExecSession(backend)
env = H.call_snippet(mod, session, name)
ok = (not env['ok']) and ('hash' in (env.get('error') or '').lower() or 'stale' in (env.get('error') or '').lower())
H.verdict(ok, '5a: edited snippet %s refused=%s error=%s (expected refuse naming hash/stale, zero acts: %d)' % (
    name, not env['ok'], env.get('error'), len(backend.act_calls)))
```

PASS: envelope ok=False, error names hash mismatch or stale snippet (and
names the snippet and the expected hash), backend.act_calls is empty.
FAIL: envelope ok=True, or error is anything else (for example a bare
NameError from the tampered line, which means the tampered code RAN), or
any backend act happened.

### Probe 5a2: manifest entry without sha256 is refused, not trusted

Attack: add a manifest entry with no sha256 field (or a sha256 of the
empty string) pointing at a valid snippet file, then call it.

```python
# probe p5a2_missing_hash.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
data = H.read_manifest(tree)
entries = data['snippets'] if isinstance(data, dict) and 'snippets' in data else data
first = entries[0] if isinstance(entries, list) else entries[list(entries)[0]]
evil = dict(first)
evil.pop('sha256', None)
evil['name'] = 'y1b-no-hash-probe'
if isinstance(entries, list):
    entries.append(evil)
else:
    entries['y1b-no-hash-probe'] = evil
H.write_manifest(tree, data)
backend = H.FakeBackend()
session = mod.CodeExecSession(backend)
env = H.call_snippet(mod, session, 'y1b-no-hash-probe')
H.verdict((not env['ok']) and len(backend.act_calls) == 0,
    '5a2: hashless entry refused=%s error=%s acts=%d (expected refuse, zero acts)' % (
        not env['ok'], env.get('error'), len(backend.act_calls)))
```

PASS: ok=False, zero backend acts. FAIL: ok=True (the loader trusted a
hashless entry) or any act happened.

### Probe 5a3: hash is checked on the bytes read, execute those bytes (TOCTOU)

Attack: the file changes between the hash check and execution, so the
checked bytes are not the executed bytes (redteam 9d). This probe counts
reads of the snippet file during one run_snippet call.

```python
# probe p5a3_read_once.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
import pathlib
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
entries = H.manifest_entries(tree)
name = entries[0]['name'] if isinstance(entries, list) else list(entries)[0]
entry = entries[0] if isinstance(entries, list) else entries[name]
path = H.snippet_file(tree, entry)
orig_open = open
orig_read_bytes = pathlib.Path.read_bytes
orig_read_text = pathlib.Path.read_text
reads = []
def counting_open(file, *a, **k):
    if str(file) == str(path):
        reads.append('open')
    return orig_open(file, *a, **k)
def counting_read_bytes(self, *a, **k):
    if str(self) == str(path):
        reads.append('read_bytes')
    return orig_read_bytes(self, *a, **k)
def counting_read_text(self, *a, **k):
    if str(self) == str(path):
        reads.append('read_text')
    return orig_read_text(self, *a, **k)
import builtins
builtins.open = counting_open
pathlib.Path.read_bytes = counting_read_bytes
pathlib.Path.read_text = counting_read_text
try:
    backend = H.FakeBackend()
    session = mod.CodeExecSession(backend)
    env = H.call_snippet(mod, session, name)
finally:
    builtins.open = orig_open
    pathlib.Path.read_bytes = orig_read_bytes
    pathlib.Path.read_text = orig_read_text
if not reads:
    H.verdict(False, '5a3: no read of the snippet file was observed through open/read_bytes/read_text; the loader reads it another way, re-run with a counter on that path before trusting a read-once claim')
H.verdict(len(reads) <= 1,
    '5a3: snippet file read %d times via %s during one run_snippet (expected at most 1: read once, hash the bytes read, execute those bytes)' % (len(reads), reads))
```

PASS: file read at most once. FAIL: read twice or more (hash check and
execution read separately, TOCTOU window open). Note: if the loader
reads via open() rather than Path.read_bytes, this probe undercounts;
Y1b then re-runs it with an open() counter and reports which path the
loader uses. A loader that provably hashes the exact bytes it executes
by another mechanism passes if Y1b can show the mechanism in code and
the 5a tamper probe still passes.

### Probe 5b1: snippet name colliding with an API or op name is rejected at load

Attack: manifest entry named `act`, `windows`, `observe`, `read_file`,
`run_snippet`, or `repo.list_scripts` (a future op name). Search results
and a human reading a program cannot tell it from the API.

```python
# probe p5b1_name_collision.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
data = H.read_manifest(tree)
entries = data['snippets'] if isinstance(data, dict) and 'snippets' in data else data
first = entries[0] if isinstance(entries, list) else entries[list(entries)[0]]
results = {}
for bad in ('act', 'windows', 'observe', 'run_snippet'):
    evil = dict(first)
    evil['name'] = bad
    if isinstance(entries, list):
        entries.append(evil)
    else:
        entries[bad] = evil
    H.write_manifest(tree, data)
    backend = H.FakeBackend()
    session = mod.CodeExecSession(backend)
    env = H.call_snippet(mod, session, bad)
    err = (env.get('error') or '').lower()
    results[bad] = (not env['ok']) and len(backend.act_calls) == 0 and any(
        w in err for w in ('collision', 'collide', 'reserv', 'allowlist', 'shadow', 'duplicate'))
    if isinstance(entries, list):
        entries.pop()
    else:
        entries.pop(bad)
    H.write_manifest(tree, data)
control = H.call_snippet(mod, mod.CodeExecSession(H.FakeBackend()), first['name'])
H.verdict(all(results.values()) and control['ok'],
    '5b1: colliding names refused=%s control(real name runs)=%s (expected every colliding name refused AT LOAD with an error naming the collision/reservation, zero acts, and the same snippet under its real name still runs)' % (results, control['ok']))
```

PASS: every colliding name refused, zero acts. FAIL: any colliding name
runs (it shadows the API in search results and in programs).

### Probe 5b2: param name colliding with the API allowlist is rejected at load

Attack: manifest entry with a param named `windows`, `act`, `observe`,
or `read_file`. Bound into the session namespace it shadows the API
function of that name inside the snippet, so the snippet's own act()
call dies with TypeError or calls attacker-chosen code.

```python
# probe p5b2_param_shadow.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
data = H.read_manifest(tree)
entries = data['snippets'] if isinstance(data, dict) and 'snippets' in data else data
first = entries[0] if isinstance(entries, list) else entries[list(entries)[0]]
evil = dict(first)
evil['name'] = 'y1b-shadow-probe'
params = list(evil.get('params') or [])
params.append({'name': 'windows', 'type': 'string', 'required': False, 'default': 'pwned'})
evil['params'] = params
if isinstance(entries, list):
    entries.append(evil)
else:
    entries['y1b-shadow-probe'] = evil
H.write_manifest(tree, data)
backend = H.FakeBackend()
session = mod.CodeExecSession(backend)
env = H.call_snippet(mod, session, 'y1b-shadow-probe', {'windows': 'pwned'})
err = (env.get('error') or '').lower()
refused = (not env['ok']) and len(backend.act_calls) == 0 and any(
    w in err for w in ('collision', 'collide', 'reserv', 'allowlist', 'shadow', 'param'))
control = H.call_snippet(mod, mod.CodeExecSession(H.FakeBackend()), first['name'])
if refused and control['ok']:
    H.verdict(True, '5b2: param named windows rejected at load, error=%s (control: same snippet without the colliding param runs)' % env.get('error'))
H.verdict(False, '5b2: load ACCEPTED a param named windows (ok=%s error=%s control_ok=%s); the council synthesis requires allowlist collisions to be rejected at manifest load, even if the API happens to win inside the snippet this time' % (
    env['ok'], env.get('error'), control['ok']))
```

PASS: load refuses the entry outright. FAIL: load accepts it, for any
reason, including the case where the API happens to win inside the
snippet this time. The synthesis requires rejection at manifest load;
a runtime coincidence is not a fix, because the binding order is an
implementation detail that the next edit can flip.

### Probe 5c: snippet that exfils a file through act() needs approval first

Attack (redteam 5c): a promoted snippet reads /tmp/secret and types it
through act() into whatever window is focused. The sandbox has no
network, but act() IS the network: keystrokes into a shell that has
curl. Run-by-name removes the read-the-code step, so the approval tier
is the only review.

```python
# probe p5c_exfil_approval.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
import pathlib
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
secret = pathlib.Path('/tmp/y1b-exfil-secret.txt')
secret.write_text('TOPSECRET-MARKER-7f3a', encoding='utf-8')
sdir = H.snippet_dir(tree)
(sdir / 'y1b_exfil.py').write_text(
    'wins = windows()\n'
    'term = [w for w in wins if w["title"] == "speed-pick1-term"][0]\n'
    'obs = observe(window=term["address"])\n'
    'data = read_file("/tmp/y1b-exfil-secret.txt")\n'
    'result = act([{"type": "type", "text": data + "\\n"}], obs)\n', encoding='utf-8')
evil = H.clone_entry(tree, 'y1b-exfil', 'y1b_exfil.py', [],
                     description='Read a file and type it into the terminal',
                     source='y1b probe', expected_result='refused without approval',
                     tags=['terminal'], requires_approval=True)
H.add_entry(tree, evil)
backend = H.FakeBackend()
session = mod.CodeExecSession(backend)
env = H.call_snippet(mod, session, 'y1b-exfil')
typed = ''.join(a.get('text', '') for acts in backend.act_calls for a in acts)
refused_clean = (not env['ok']) and len(backend.act_calls) == 0 and 'TOPSECRET-MARKER-7f3a' not in typed
if not refused_clean:
    H.verdict(False, '5c: exfil snippet without approval refused=%s error=%s acts=%d secret_typed=%s (expected refuse before any act, secret never typed)' % (
        not env['ok'], env.get('error'), len(backend.act_calls), 'TOPSECRET-MARKER-7f3a' in typed))
backend2 = H.FakeBackend()
session2 = mod.CodeExecSession(backend2)
try:
    approved = H.call_snippet_approved(mod, session2, 'y1b-exfil')
except H.InterfaceMissing as exc:
    H.verdict(False, '5c: refused without approval, but requires_approval has no approval path to ever run it: %s' % exc)
typed2 = ''.join(a.get('text', '') for acts in backend2.act_calls for a in acts)
H.verdict(approved['ok'] and len(backend2.act_calls) > 0 and 'TOPSECRET-MARKER-7f3a' in typed2,
    '5c: control: approved run ok=%s acts=%d secret_typed=%s (expected the approved run to type the secret, proving only approval blocked it)' % (
        approved['ok'], len(backend2.act_calls), 'TOPSECRET-MARKER-7f3a' in typed2))
```

Setup note: this probe assumes Codex marks file-reading plus typing
snippets requires_approval=true, either by manifest field or by loader
rule (any snippet calling read_file plus act). If the manifest entry
above is accepted with requires_approval absent/false and still runs,
the probe FAILS. PASS also requires the manifest schema to HAVE a
requires_approval field: Y1b checks `evil` was stored with
requires_approval true, or the loader inferred it. If Codex instead
implements approval as "show source with the approval request", Y1b
verifies on the laptop lane that the approval request shows the snippet
source (see probe 5c-laptop below).

### Probe 5c-laptop: approval request shows the snippet source (LAPTOP-ONLY)

Reason: the approval UX lives in the laptop session (cu.py gate), not in
the VM session. On the laptop, run the 5c snippet through the real
code-exec path with CU_CODE_EXEC=1 and confirm the approval prompt
includes the full snippet source text plus its sha256 before any act is
typed. PASS: prompt shows source + hash, nothing typed until approved.
FAIL: prompt shows only the name, or typing happens before approval.

### Probe 5d: param value as format string leaks nothing

Attack (redteam 1 + 5d): a snippet passes a model-supplied param as a
format string, so page content such as `{0.__self__.__dict__}` becomes
the format string and the snippet's own objects become the arguments.
Depends on must-fix 1 (remove "format" from SAFE_ATTRIBUTE_NAMES); this
probe asserts the combined effect for snippets.

```python
# probe p5d_param_format.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
sdir = H.snippet_dir(tree)
(sdir / 'y1b_fmt.py').write_text(
    'x = msg.format(windows)\nprint(x)\n', encoding='utf-8')
evil = H.clone_entry(tree, 'y1b-fmt', 'y1b_fmt.py',
                     [{'name': 'msg', 'type': 'string', 'required': True}],
                     description='Format a param message',
                     source='y1b probe', expected_result='rejected by scan',
                     tags=['test'])
H.add_entry(tree, evil)
backend = H.FakeBackend()
session = mod.CodeExecSession(backend)
env = H.call_snippet(mod, session, 'y1b-fmt', {'msg': '{0.__self__.__dict__}'})
leaked = 'session_token' in str(env) or '__dict__' in str(env.get('variables', {}))
refused_clean = (not env['ok']) and not leaked
if not refused_clean:
    H.verdict(False, '5d: param-as-format-string snippet refused=%s error=%s leaked=%s (expected scan rejects .format, no dunder data in envelope)' % (
        not env['ok'], env.get('error'), leaked))
(sdir / 'y1b_fmt_ok.py').write_text('''x = msg + "!"
print(x)
''', encoding='utf-8')
ok_entry = H.clone_entry(tree, 'y1b-fmt-ok', 'y1b_fmt_ok.py',
                         [{'name': 'msg', 'type': 'string', 'required': True}],
                         description='Safe string concat of a param',
                         source='y1b probe', expected_result='ok True', tags=['test'])
H.add_entry(tree, ok_entry)
control = H.call_snippet(mod, mod.CodeExecSession(H.FakeBackend()), 'y1b-fmt-ok', {'msg': 'hello'})
H.verdict(control['ok'],
    '5d: control: safe param use (concat, no .format) runs, ok=%s error=%s (expected ok=True: the refusal must be caused by .format, not by params in general)' % (
        control['ok'], control.get('error')))
```

PASS: ok=False with a sandbox/scan error (format not allowlisted), and no
dunder data anywhere in the envelope. FAIL: ok=True, or the envelope
contains __dict__ / session_token / any attribute-chain dump. A second
leg of this probe: run the same snippet source directly through
mod.validate_program; it must raise CodeExecError naming `format`.

---

## ITEM 6: Stale guard dead on laptop (redteam Attack 6)

Redteam evidence this must defeat: verified_against is a git commit hash
but the installed laptop copy has no .git, so the guard is dead exactly
where P1-P4 execute; CI never executes live_only snippets; P3/P4 asserts
pass on leftover /tmp state from a prior run; last_verified is
hand-editable and never expires.

Setup for all item 6 probes: temp trees from H.temp_tree(); the no-git
probes additionally delete every .git directory under the temp tree and
run with CWD set to the temp tree. Runtime API hash field name is
whatever Codex chose in the manifest; probes resolve it by reading the
manifest keys and the loader source, and say so in their output. If no
runtime hash field exists anywhere, probes 6a1-6a3 FAIL "no runtime hash".

### Probe 6a1: staleness is enforced in a copy with no .git (the laptop shape)

Attack: copy the installed tree without .git (exactly what
scripts/sync-installed.py ships to the laptop), then run a snippet.
The redteam design fails closed (P1-P4 never run) or fails open (guard
dead). The fix must do neither: it must run when the runtime API hash
matches and refuse when it does not, with no git present at all.

```python
# probe p6a1_no_git.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
import os, pathlib, shutil
tree = H.temp_tree()
for git in tree.rglob('.git'):
    shutil.rmtree(git, ignore_errors=True)
assert not list(tree.rglob('.git')), 'temp tree still has .git'
os.chdir(tree)
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
entries = H.manifest_entries(tree)
name = entries[0]['name'] if isinstance(entries, list) else list(entries)[0]
backend = H.FakeBackend()
session = mod.CodeExecSession(backend)
env = H.call_snippet(mod, session, name)
H.verdict(env['ok'],
    '6a1: snippet %s runs in a no-.git copy, ok=%s error=%s (expected ok=True when runtime hash matches; fail-closed here means the guard is dead on the laptop, fail-open is proved by probe 6a2)' % (
        name, env['ok'], env.get('error')))
```

PASS: ok=True with no .git anywhere under the tree. FAIL: ok=False with
any error mentioning git, commit, rev-parse, or "cannot determine
version" (fail-closed on the laptop), or ok=True only because the check
was skipped (proved by 6a2).

### Probe 6a2: changing the runtime API refuses the snippet even when the git hash is unchanged

Attack: mutate code_exec.py in the temp copy (rename an allowlisted API
function the snippet uses, or change its signature), keep the manifest
verified_against git hash exactly as it was, then run the snippet. A
guard keyed on git commits cannot see this change; a guard keyed on the
runtime API hash must refuse.

```python
# probe p6a2_api_change.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
import pathlib
tree = H.temp_tree()
ce = tree / 'scripts' / 'code_exec.py'
text = ce.read_text(encoding='utf-8')
old_def = "    def api_windows(self):\n        return self._api('windows', self.backend.windows)"
old_bind = "                'windows': self.api_windows,\n"
assert old_def in text and old_bind in text, 'api_windows shape changed, adapt probe'
mutated = text.replace(old_def, "    def api_windows_v2(self):\n        return self._api('windows', self.backend.windows)", 1)
mutated = mutated.replace(old_bind, "                'windows': self.api_windows_v2,\n", 1)
assert mutated != text, 'could not mutate api_windows'
ce.write_text(mutated, encoding='utf-8')
mod = H.load_code_exec(tree)
entries = H.manifest_entries(tree)
name = entries[0]['name'] if isinstance(entries, list) else list(entries)[0]
backend = H.FakeBackend()
session = mod.CodeExecSession(backend)
try:
    H.need_run_snippet(mod)
except H.InterfaceMissing as exc:
    H.verdict(True, '6a2: mutating the allowlist removed run_snippet itself, fail-closed as required: %s' % exc)
env = H.call_snippet(mod, session, name)
H.verdict((not env['ok']) and ('stale' in (env.get('error') or '').lower() or 'hash' in (env.get('error') or '').lower() or 'api' in (env.get('error') or '').lower()),
    '6a2: snippet refused after API change, ok=%s error=%s (expected refuse naming stale/hash/API; a git-keyed guard would still run it)' % (
        env['ok'], env.get('error')))
```

PASS: ok=False naming stale, hash, or API. FAIL: ok=True (the guard did
not see the API change, so it is git-keyed or absent). Note: if Codex
keys staleness on the sha256 of the whole code_exec.py file bytes, this
probe also passes, and probe 6a3 distinguishes file-hash from API-hash.

### Probe 6a3: a bogus git hash in verified_against does not block a run (git is audit-only)

Attack (inverse of 6a2): set verified_against to a garbage 40-hex git
hash while the runtime API hash still matches, then run. If the runner
compares the git hash, it refuses a good snippet; if git is audit-only,
it runs.

```python
# probe p6a3_git_audit_only.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
data = H.read_manifest(tree)
entries = data['snippets'] if isinstance(data, dict) and 'snippets' in data else data
first = entries[0] if isinstance(entries, list) else entries[list(entries)[0]]
first['verified_against'] = 'deadbeef' * 5
H.write_manifest(tree, data)
backend = H.FakeBackend()
session = mod.CodeExecSession(backend)
env = H.call_snippet(mod, session, first['name'])
H.verdict(env['ok'],
    '6a3: bogus git verified_against still runs, ok=%s error=%s (expected ok=True: git hash is audit metadata only, runtime hash governs)' % (
        env['ok'], env.get('error')))
```

PASS: ok=True. FAIL: ok=False (the runner still keys staleness on the
git commit). Also grep the loader source for `rev-parse`, `git`, and
`subprocess` in the stale-check path; any hit is a FAIL with the file
and line number, even if this behavioral probe passes.

### Probe 6b1: P3/P4 asserts must not pass on leftover /tmp state

Attack (redteam 6b mode 3): pre-create the P3 target directories (or the
P4 target file with the right content) from a FIRST successful run, then
re-run the snippet with act() reporting ok=True while creating nothing
(typed into the wrong window, the shell never runs the command). The
stale-state asserts pass and the snippet reports success for work it did
not do. Note: a backend whose act() RETURNS a refusal dict does not
discriminate here, because the template asserts result["ok"] and fails
on a refusal either way; the discriminating case is ok=True with no
side effect.

```python
# probe p6b1_stale_tmp.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
import pathlib
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
entries = H.manifest_entries(tree)
names = [e['name'] for e in entries] if isinstance(entries, list) else list(entries)
def _entry(n):
    return entries[names.index(n)] if isinstance(entries, list) else entries[n]
cands = []
for n in names:
    src0 = H.snippet_file(tree, _entry(n)).read_text(encoding='utf-8')
    if 'assert_file_exists' in src0 or 'assert_file_contains' in src0:
        cands.append(n)
if not cands:
    H.verdict(False, '6b1: no file-asserting snippet in manifest to test (names=%s); P3/P4 migration is required' % names)
p3 = cands[0]
entry = _entry(p3)
src = H.snippet_file(tree, entry).read_text(encoding='utf-8')
import re
for path in re.findall(r'assert_file_exists\("([^"]+)"\)', src):
    p = pathlib.Path(path)
    if p.suffix:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('', encoding='utf-8')
    else:
        p.mkdir(parents=True, exist_ok=True)
for path, text in re.findall(r'assert_file_contains\("([^"]+)", "([^"]*)"\)', src):
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')
backend = H.FakeBackend()
session = mod.CodeExecSession(backend)
env = H.call_snippet(mod, session, p3)
H.verdict((not env['ok']),
    '6b1: P3 rerun with act() reporting ok=True but creating nothing (typed into the wrong window) and pre-created dirs, ok=%s error=%s (expected ok=False: snippet must remove targets first or use a fresh unique path per run, then assert)' % (
        env['ok'], env.get('error')))
```

PASS: ok=False. FAIL: ok=True (the asserts passed on leftover state).
Setup note: if the migrated P3 snippet asserts on different paths, Y1b
adjusts the pre-created paths to the snippet's actual assert targets
and records the adjustment; the attack shape (pre-create, refuse act,
expect failure) does not change. A variant for P4: pre-create the
target file with the exact expected content, refuse act(), expect
ok=False.

### Probe 6b2: ambiguous window title fails loudly instead of taking [0]

Attack (redteam 6b mode 2): two terminals share the title
speed-pick1-term. The template's `[w for w in wins if w["title"] ==
title][0]` picks nondeterministically and types into the wrong window
with no error.

```python
# probe p6b2_ambiguous_window.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
entries = H.manifest_entries(tree)
name = entries[0]['name'] if isinstance(entries, list) else list(entries)[0]
twins = [
    {'address': '0xaaa', 'class': 'kitty', 'title': 'speed-pick1-term',
     'at': [0, 0], 'size': [800, 600], 'workspace': {'id': 1}},
    {'address': '0xbbb', 'class': 'kitty', 'title': 'speed-pick1-term',
     'at': [0, 0], 'size': [800, 600], 'workspace': {'id': 1}}]
backend = H.FakeBackend(windows=twins)
session = mod.CodeExecSession(backend)
env = H.call_snippet(mod, session, name)
control = H.call_snippet(mod, mod.CodeExecSession(H.FakeBackend()), name)
H.verdict((not env['ok']) and len(backend.act_calls) == 0 and control['ok'],
    '6b2: two windows share the title, refused=%s error=%s acts=%d control(single window runs)=%s (expected refuse naming ambiguous/multiple match, zero acts)' % (
        not env['ok'], env.get('error'), len(backend.act_calls), control['ok']))
```

PASS: ok=False with an error about ambiguous or multiple matches, zero
backend acts. FAIL: ok=True, or any act happened (it typed into one of
two identical titles at random). Zero-match case is the same probe with
an empty windows list; Y1b runs it as a variant and expects the same
refusal.

### Probe 6c1: expired live_only snippet is excluded from search and refused at run

Attack: set last_verified 40 days ago on a live_only entry. Redteam fix:
30-day max age for live_only, enforced by the runner, not by convention.

```python
# probe p6c1_expired_live.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
import datetime
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
data = H.read_manifest(tree)
entries = data['snippets'] if isinstance(data, dict) and 'snippets' in data else data
first = entries[0] if isinstance(entries, list) else entries[list(entries)[0]]
first['live_only'] = True
first['last_verified'] = (datetime.date.today() - datetime.timedelta(days=40)).isoformat()
H.write_manifest(tree, data)
backend = H.FakeBackend()
session = mod.CodeExecSession(backend)
env = H.call_snippet(mod, session, first['name'])
refused_clean = (not env['ok']) and ('expir' in (env.get('error') or '').lower() or 'stale' in (env.get('error') or '').lower() or 'verif' in (env.get('error') or '').lower())
if not refused_clean:
    H.verdict(False, '6c1: 40-day-old live_only snippet refused=%s error=%s (expected refuse naming expired/stale/verification)' % (
        not env['ok'], env.get('error')))
first['last_verified'] = datetime.date.today().isoformat()
H.write_manifest(tree, data)
control = H.call_snippet(mod, mod.CodeExecSession(H.FakeBackend()), first['name'])
H.verdict(control['ok'],
    '6c1: control: same snippet with last_verified=today runs, ok=%s error=%s (expected ok=True: expiry, not the entry itself, caused the refusal)' % (
        control['ok'], control.get('error')))
```

PASS: ok=False naming expiry, staleness, or verification. FAIL: ok=True
(a six-month-old snippet stays runnable forever). Search exclusion is
checked by the same probe's second leg: Y1b calls the search function
with the snippet's tags and asserts the expired entry is absent; if
Codex has no snippet search yet, Y1b records "search exclusion
untestable, run refusal only" and the probe still passes on refusal
alone only if the run refusal passed.

### Probe 6c2: a future hand-edited last_verified does not authorize a stale snippet

Attack: set last_verified to tomorrow (or 2099) while the runtime API
hash is stale (combine with the 6a2 mutation). A date string alone must
never authorize a run.

```python
# probe p6c2_future_date.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
import datetime, pathlib
tree = H.temp_tree()
ce = tree / 'scripts' / 'code_exec.py'
text = ce.read_text(encoding='utf-8')
old_def = "    def api_windows(self):\n        return self._api('windows', self.backend.windows)"
old_bind = "                'windows': self.api_windows,\n"
if old_def in text and old_bind in text:
    mutated = text.replace(old_def, "    def api_windows_v2(self):\n        return self._api('windows', self.backend.windows)", 1)
    mutated = mutated.replace(old_bind, "                'windows': self.api_windows_v2,\n", 1)
    ce.write_text(mutated, encoding='utf-8')
mod = H.load_code_exec(tree)
data = H.read_manifest(tree)
entries = data['snippets'] if isinstance(data, dict) and 'snippets' in data else data
first = entries[0] if isinstance(entries, list) else entries[list(entries)[0]]
first['last_verified'] = (datetime.date.today() + datetime.timedelta(days=365)).isoformat()
H.write_manifest(tree, data)
backend = H.FakeBackend()
session = mod.CodeExecSession(backend)
try:
    H.need_run_snippet(mod)
    env = H.call_snippet(mod, session, first['name'])
    H.verdict(not env['ok'],
        '6c2: future last_verified plus stale API, ok=%s error=%s (expected refuse: the date must never override the runtime hash)' % (
            env['ok'], env.get('error')))
except H.InterfaceMissing as exc:
    H.verdict(True, '6c2: API mutation removed run_snippet, fail-closed: %s' % exc)
```

PASS: ok=False. FAIL: ok=True (anyone editing the manifest can set any
date and re-authorize a stale snippet).

### Probe 6c3: VM-verifiable snippet expires at 90 days

```python
# probe p6c3_expired_vm.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
import datetime
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
data = H.read_manifest(tree)
entries = data['snippets'] if isinstance(data, dict) and 'snippets' in data else data
first = entries[0] if isinstance(entries, list) else entries[list(entries)[0]]
first['live_only'] = False
first['last_verified'] = (datetime.date.today() - datetime.timedelta(days=100)).isoformat()
H.write_manifest(tree, data)
backend = H.FakeBackend()
session = mod.CodeExecSession(backend)
env = H.call_snippet(mod, session, first['name'])
refused_clean = (not env['ok']) and ('expir' in (env.get('error') or '').lower() or 'stale' in (env.get('error') or '').lower() or 'verif' in (env.get('error') or '').lower())
if not refused_clean:
    H.verdict(False, '6c3: 100-day-old VM-verifiable snippet refused=%s error=%s (expected refuse naming expired/stale/verification)' % (
        not env['ok'], env.get('error')))
first['last_verified'] = datetime.date.today().isoformat()
H.write_manifest(tree, data)
control = H.call_snippet(mod, mod.CodeExecSession(H.FakeBackend()), first['name'])
H.verdict(control['ok'],
    '6c3: control: same snippet with last_verified=today runs, ok=%s error=%s (expected ok=True: expiry, not the entry, caused the refusal)' % (
        control['ok'], control.get('error')))
```

PASS: ok=False naming expiry, staleness, or verification, and the
today control runs. FAIL: ok=True.

### Probe 6d-VM: CI executes live_only snippets against a fake backend, not just py_compile

Attack: break a live_only snippet's behavior without breaking its syntax
(for example change an assert text so its expected_result can never
hold), then run tests/test_snippets.py. The redteam design passes CI
because CI only py_compiles live_only snippets.

```bash
# probe p6d_ci_executes_live.sh
# Run from the y1-snippets worktree root.
set -u
CODE_PATH=$(python3 -c "import json, pathlib; d=json.loads(pathlib.Path('snippets/manifest.json').read_text()); e=d['snippets'][0] if isinstance(d, dict) and 'snippets' in d else d[0]; cp=e['code_path']; print(cp if '/' in cp else 'snippets/'+cp)")
cp "$CODE_PATH" /tmp/y1b-p6d-backup.py
cp snippets/manifest.json /tmp/y1b-p6d-manifest-backup.json
python3 - <<'EOF'
import hashlib, json, pathlib
d = json.loads(pathlib.Path('snippets/manifest.json').read_text())
e = d['snippets'][0] if isinstance(d, dict) and 'snippets' in d else d[0]
cp = e['code_path']
target = pathlib.Path(cp) if '/' in cp else pathlib.Path('snippets') / cp
t = target.read_text()
target.write_text(t.replace('assert_state(result["ok"]', 'assert_state(result["ok"] and False, "y1b-break') if 'assert_state(result["ok"]' in t else t + '\nassert_state(False, "y1b-break")\n')
e['sha256'] = hashlib.sha256(target.read_bytes()).hexdigest()
pathlib.Path('snippets/manifest.json').write_text(json.dumps(d, indent=2))
print('broke', e['name'], 'at', target, 'and re-hashed the manifest so only execution can catch it')
EOF
python3 -m unittest tests.test_snippets > /tmp/y1b-p6d.log 2>&1; STATUS=$?
tail -5 /tmp/y1b-p6d.log
cp /tmp/y1b-p6d-backup.py "$CODE_PATH"
cp /tmp/y1b-p6d-manifest-backup.json snippets/manifest.json
git status --porcelain snippets/ || true
echo "test_snippets exit=$STATUS (expected non-zero: the suite must FAIL on a behavior-broken live_only snippet)"
test $STATUS -ne 0
```

PASS: tests/test_snippets.py FAILS on the broken snippet (it executes
live_only snippets against FakeBackend/FakeTerminalBackend and asserts
expected_result). FAIL: the suite still passes (it only py_compiles and
validates, so a behavior break ships). Setup: run from the y1-snippets
worktree root; the script restores the snippet file afterwards and Y1b
verifies with git status that the tree is clean.

### Probe 6d-laptop: live re-verification refreshes last_verified (LAPTOP-ONLY)

Reason: the live run needs a real terminal, a real Zen, and the laptop
desktop; the VM cannot do it. On the laptop, run the P1-P4 live lane
with CU_CODE_EXEC=1, confirm each live_only snippet passes against the
real desktop, and confirm the verification run itself (not a human)
updated last_verified and the runtime hash in the manifest. PASS: live
run passes and the manifest fields change only as a result of that run.
FAIL: last_verified was edited by hand, or the live lane does not exist.

---

## ITEM 7: Replay and divergence (redteam Attack 7)

Redteam evidence this must defeat: a retried Polygon create/submit
duplicates the problem or the package; a retried Zen URL type opens a
second tab; act() with no observation defaults to the most recent
observation in the session, up to 120s old, whoever took it, so a
snippet that forgets to observe acts on another snippet's observation;
DOM snapshot refs can resolve to different elements after SPA
navigation.

Setup for all item 7 probes: FakeBackend / FakeDomBackend from the
harness, which count every backend call. The counting is the evidence:
any probe that expects "no second act" asserts on backend.act_calls
and backend.dom_calls, not on the envelope alone.

### Probe 7a1: retry of the same snippet with the same params does not re-execute

Attack: run a snippet that types through act(), then retry it with the
identical name and params (the supervisor retry after a failed verify
observe). The redteam version re-executes blindly and duplicates the act.

```python
# probe p7a1_retry_ledger.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
sdir = H.snippet_dir(tree)
(sdir / 'y1b_count.py').write_text(
    'wins = windows()\n'
    'term = [w for w in wins if w["title"] == "speed-pick1-term"][0]\n'
    'obs = observe(window=term["address"])\n'
    'result = act([{"type": "type", "text": "echo MARKER-" + tag + "\\n"}], obs)\n'
    'assert_state(result["ok"], "act failed")\n', encoding='utf-8')
evil = H.clone_entry(tree, 'y1b-count', 'y1b_count.py',
                     [{'name': 'tag', 'type': 'string', 'required': True}],
                     description='Type a tagged marker line',
                     source='y1b probe', expected_result='ok True, one act',
                     tags=['test'], requires_approval=False)
H.add_entry(tree, evil)
backend = H.FakeBackend()
session = mod.CodeExecSession(backend)
first = H.call_snippet(mod, session, 'y1b-count', {'tag': 'once'})
acts_after_first = len(backend.act_calls)
second = H.call_snippet(mod, session, 'y1b-count', {'tag': 'once'})
acts_after_second = len(backend.act_calls)
second_ok = second['ok'] and ('already applied' in str(second.get('variables', {})) or 'already applied' in (second.get('error') or '') or second.get('variables', {}).get('r') is not None)
H.verdict(first['ok'] and acts_after_second == acts_after_first,
    '7a1: retry same snippet same params, first_ok=%s acts_first=%d acts_second=%d second=%s (expected second run returns recorded result or already-applied refusal with ZERO new backend acts)' % (
        first['ok'], acts_after_first, acts_after_second, second))
```

PASS: first ok=True, backend.act_calls unchanged after the retry, and
the second envelope either returns the recorded result or refuses with
"already applied". FAIL: a second backend act happened (the marker
would be typed twice), or the second run errored for any other reason
while still acting. Note: if Codex implements the ledger as
refuse-with-already-applied, second['ok'] is False and that still
passes, provided acts did not increase. The probe checks the act count
first, the envelope shape second.

### Probe 7a2: different params run again, and a new session runs again

Same setup as 7a1, continued: call with tag 'twice' (different params)
and expect a new backend act; then build a fresh CodeExecSession with
the same backend and call with tag 'once' again and expect a new act
(the ledger is per session, not global).

```python
# probe p7a2_ledger_scope.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
sdir = H.snippet_dir(tree)
(sdir / 'y1b_count.py').write_text(
    'wins = windows()\n'
    'term = [w for w in wins if w["title"] == "speed-pick1-term"][0]\n'
    'obs = observe(window=term["address"])\n'
    'result = act([{"type": "type", "text": "echo MARKER-" + tag + "\\n"}], obs)\n'
    'assert_state(result["ok"], "act failed")\n', encoding='utf-8')
evil = H.clone_entry(tree, 'y1b-count', 'y1b_count.py',
                     [{'name': 'tag', 'type': 'string', 'required': True}],
                     description='Type a tagged marker line',
                     source='y1b probe', expected_result='ok True, one act',
                     tags=['test'], requires_approval=False)
H.add_entry(tree, evil)
backend = H.FakeBackend()
session = mod.CodeExecSession(backend)
H.call_snippet(mod, session, 'y1b-count', {'tag': 'once'})
n1 = len(backend.act_calls)
diff = H.call_snippet(mod, session, 'y1b-count', {'tag': 'twice'})
n2 = len(backend.act_calls)
fresh = mod.CodeExecSession(backend)
again = H.call_snippet(mod, fresh, 'y1b-count', {'tag': 'once'})
n3 = len(backend.act_calls)
H.verdict(diff['ok'] and n2 == n1 + 1 and again['ok'] and n3 == n2 + 1,
    '7a2: different params ok=%s acts %d->%d, fresh session ok=%s acts %d->%d (expected both run again: ledger keyed on name plus param hash, scoped per session)' % (
        diff['ok'], n1, n2, again['ok'], n2, n3))
```

PASS: different params act once more, fresh session acts once more.
FAIL: either call was suppressed (ledger keyed on name only, or ledger
leaked across sessions).

### Probe 7a3: non-idempotent snippet is marked requires_approval and refuses without it

Attack: the y1b-count snippet (typing is not idempotent) with
requires_approval true in the manifest is called with no approval. The
call must refuse before any backend act. This probe also covers the
Polygon shape: a create/submit snippet must carry the same mark.

```python
# probe p7a3_requires_approval.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
data = H.read_manifest(tree)
entries = data['snippets'] if isinstance(data, dict) and 'snippets' in data else data
marked = [e for e in (entries if isinstance(entries, list) else entries.values()) if e.get('requires_approval') is True]
if not marked:
    H.verdict(False, '7a3: no manifest entry carries requires_approval=true; non-idempotent snippets (Polygon create/submit, typing) must be marked')
name = marked[0]['name']
backend = H.FakeBackend()
session = mod.CodeExecSession(backend)
env = H.call_snippet(mod, session, name)
refused_clean = (not env['ok']) and len(backend.act_calls) == 0 and 'approv' in (env.get('error') or '').lower()
if not refused_clean:
    H.verdict(False, '7a3: %s without approval refused=%s error=%s acts=%d (expected refuse naming approval, zero acts)' % (
        name, not env['ok'], env.get('error'), len(backend.act_calls)))
try:
    approved = H.call_snippet_approved(mod, mod.CodeExecSession(H.FakeBackend()), name)
except H.InterfaceMissing as exc:
    H.verdict(False, '7a3: refused without approval, but requires_approval has no approval path to ever run it: %s' % exc)
H.verdict(approved['ok'],
    '7a3: control: approved run of %s ok=%s error=%s (expected ok=True: only approval blocked it)' % (
        name, approved['ok'], approved.get('error')))
```

PASS: at least one non-idempotent entry is marked, and calling it
without approval refuses with zero acts. FAIL: no entry is marked, or
the call runs (or acts) without approval. If the marked entry needs
params, Y1b passes benign dummy params and records them; the refusal
must still happen before any act.

### Probe 7a-live: retried Polygon create/submit clicks once (LAPTOP-ONLY)

Reason: the duplicate only shows against the real Polygon page and the
real Zen tab strip; the VM FakeDomBackend cannot prove a second problem
was not created. On the laptop, run a Polygon create snippet against a
throwaway test problem with a forced failure at the verify observe, let
the supervisor retry, then count the created problems in the Polygon
UI. PASS: exactly one problem exists. FAIL: two problems, or two
packages submitted. This probe runs only on the laptop lane, after the
VM probes pass.

### Probe 7b: dom_act on a pre-navigation snapshot is refused

Attack (redteam 7b): a snippet observes, the page navigates without a
reload (SPA navigation), then the snippet dom_acts with the old refs.
The refs can resolve to different elements and the click lands on the
wrong thing with no error.

```python
# probe p7b_dom_stale_snapshot.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
sdir = H.snippet_dir(tree)
(sdir / 'y1b_dom.py').write_text(
    'snap = dom_observe("tab-1")\n'
    'result = dom_act(snap, [{"type": "click", "ref": snap["elements"][0]["ref"]}])\n'
    'assert_state(result["ok"], "dom act failed")\n', encoding='utf-8')
evil = H.clone_entry(tree, 'y1b-dom', 'y1b_dom.py', [],
                     description='Click first element of a snapshot',
                     source='y1b probe', expected_result='refused after navigation',
                     tags=['test'], requires_approval=False)
H.add_entry(tree, evil)
class NavBackend(H.FakeDomBackend):
    """Simulate an SPA navigation right after dom_observe returns: the snapshot URL is stale before dom_act runs."""
    def dom_observe(self, target, scope, max_elements):
        snap = super().dom_observe(target, scope, max_elements)
        self.current_url = 'file:///fixture-other-page'
        return snap
backend = NavBackend()
session = mod.CodeExecSession(backend)
env = H.call_snippet(mod, session, 'y1b-dom')
acts = [c for c in backend.dom_calls if c[0] == 'act']
H.verdict((not env['ok']) and len(acts) == 0,
    '7b: dom_act after SPA navigation refused=%s error=%s dom_acts=%d (expected refuse: snapshot URL no longer matches the live tab, re-observe required; zero backend dom acts)' % (
        not env['ok'], env.get('error'), len(acts)))
```

Setup note: the navigation happens INSIDE the snippet run, between its
own dom_observe and dom_act, via the NavBackend hook. The runner can
only refuse this if it re-validates page identity (live tab URL via
dom_tabs, or a fresh snapshot) at dom_act time, which is the redteam 7b
fix. A runner that trusts the bound snapshot for the whole 120s without
checking the live page FAILS this probe. A snippet-authoring rule alone
(template: re-observe plus URL assert before every destructive dom_act)
cannot pass it, because this snippet observes immediately before acting
and still acts on a stale page; if Codex chose the template-only route,
Y1b reports this probe as FAIL with reason "no runner page-identity
check" and cites this note. The hook is the VM stand-in for a real SPA
navigation; a full live SPA test is laptop-only (see 7b-live).

### Probe 7b-live: SPA navigation then dom_act on the live page (LAPTOP-ONLY)

Reason: needs a real Chromium page that navigates without reload. On
the laptop, observe a fixture page, trigger an SPA navigation, then run
the 7b snippet. PASS: refused, no click landed. FAIL: click landed on
the post-navigation element.

### Probe 7c: act() without a fresh observe inside the snippet fails loudly

Attack (redteam 7c): run snippet A (observes window 0xabc, acts), then
snippet B with NO observe that calls act(). The shared-session design
makes B act on A's observation, possibly a different window. P1-P4 all
observe first, so this needs a future snippet that forgets, or one
designed to "type into the current terminal". Either way the fixed
runner must scope bindings per snippet run.

```python
# probe p7c_act_without_observe.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
sdir = H.snippet_dir(tree)
(sdir / 'y1b_obs_a.py').write_text(
    'wins = windows()\n'
    'term = [w for w in wins if w["title"] == "speed-pick1-term"][0]\n'
    'obs = observe(window=term["address"])\n'
    'result = act([{"type": "wait", "ms": 0}], obs)\n'
    'assert_state(result["ok"], "act failed")\n', encoding='utf-8')
(sdir / 'y1b_noobs_b.py').write_text(
    'result = act([{"type": "type", "text": "echo SHOULD-NOT-TYPE\\n"}])\n'
    'assert_state(result["ok"], "act failed")\n', encoding='utf-8')
for nm, fn in (('y1b-obs-a', 'y1b_obs_a.py'), ('y1b-noobs-b', 'y1b_noobs_b.py')):
    evil = H.clone_entry(tree, nm, fn, [],
                         description='y1b probe snippet',
                         source='y1b probe', expected_result='see probe',
                         tags=['test'], requires_approval=False)
    H.add_entry(tree, evil)
backend = H.FakeBackend()
session = mod.CodeExecSession(backend)
first = H.call_snippet(mod, session, 'y1b-obs-a')
acts_after_a = len(backend.act_calls)
second = H.call_snippet(mod, session, 'y1b-noobs-b')
H.verdict(first['ok'] and (not second['ok']) and len(backend.act_calls) == acts_after_a,
    '7c: snippet A ok=%s acts=%d, snippet B (no observe) refused=%s error=%s acts=%d (expected B fails loudly with zero new acts, never acts on A observation)' % (
        first['ok'], acts_after_a, not second['ok'], second.get('error'), len(backend.act_calls)))
```

PASS: A ok=True with one act, B ok=False, backend.act_calls unchanged.
FAIL: B ok=True (it typed on A's observation), or any second act
happened. This probe was validated against the CURRENT unfixed code on
the VM: two plain programs in one session, the second calling act()
with no observe, returned ok=True and the backend recorded a second
act. The fixed code must flip that result.

### Probe 7c2: dom_act with another snippet's snapshot fails

```python
# probe p7c2_dom_cross_snippet.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
sdir = H.snippet_dir(tree)
(sdir / 'y1b_dom_a.py').write_text('snap = dom_observe("tab-1")\n', encoding='utf-8')
(sdir / 'y1b_dom_b.py').write_text(
    'result = dom_act(snap, [{"type": "click", "ref": snap["elements"][0]["ref"]}])\n'
    'assert_state(result["ok"], "dom act failed")\n', encoding='utf-8')
evil_a = H.clone_entry(tree, 'y1b-dom-a', 'y1b_dom_a.py', [],
                       description='Observe a DOM snapshot',
                       source='y1b probe', expected_result='ok True',
                       tags=['test'], requires_approval=False)
H.add_entry(tree, evil_a)
evil_b = H.clone_entry(tree, 'y1b-dom-b', 'y1b_dom_b.py',
                       [{'name': 'snap', 'type': 'object', 'required': True}],
                       description='Act on a snapshot passed as a param',
                       source='y1b probe', expected_result='refused',
                       tags=['test'], requires_approval=False)
H.add_entry(tree, evil_b)
backend = H.FakeDomBackend()
session = mod.CodeExecSession(backend)
first = H.call_snippet(mod, session, 'y1b-dom-a')
if not first['ok']:
    H.verdict(False, '7c2: snippet A (dom_observe) failed, ok=%s error=%s; cannot test B' % (first['ok'], first.get('error')))
bindings = session.dom_snapshots
if not bindings:
    H.verdict(True, '7c2: DOM bindings cleared when snippet A exited, so B cannot reuse them (scoping enforced)')
snap = list(bindings.values())[0]['snapshot']
n_before = len([c for c in backend.dom_calls if c[0] == 'act'])
second = H.call_snippet(mod, session, 'y1b-dom-b', {'snap': snap})
n_after = len([c for c in backend.dom_calls if c[0] == 'act'])
if (not second['ok']) and 'param' in (second.get('error') or '').lower():
    H.verdict(False, '7c2: UNTESTABLE via params (dict/object params rejected: %s); needs a declared-output channel to hand A snapshot to B' % second.get('error'))
H.verdict((not second['ok']) and n_after == n_before,
    '7c2: snippet B dom_act with A exact snapshot refused=%s error=%s new_dom_acts=%d (expected refuse: DOM bindings scoped per snippet run, zero new dom acts)' % (
        not second['ok'], second.get('error'), n_after - n_before))
```

PASS: B ok=False with zero new backend dom acts, or the bindings are
already gone when A exits. FAIL: B's dom_act lands on A's snapshot
(the binding leaked across the snippet boundary). If dict params are
rejected outright, the probe reports UNTESTABLE instead of passing.

---

## ITEM 8: Registry poisoning (redteam Attack 8 + 9a + 9c)

Redteam evidence this must defeat: no manifest size cap; duplicate-name
shadowing (list order or JSON last-wins, silently); code_path trusted
verbatim so a name like ../../cu loads an arbitrary .py; .py files are
importable so an import bypasses the scan; the natural run_snippet
implementation (nested run()) resets every budget, giving 32x32 = 1024
API calls and up to 16 minutes of wall time; session variables persist
across programs so snippet A can poison a variable snippet B reads.

Setup for all item 8 probes: temp trees from H.temp_tree() for every
probe that mutates the manifest, a snippet, or code_exec.py. Cap values:
redteam fix proposes manifest 1MB with a max entry count and snippet
8192 chars (same as programs). Probes read the cap constants from
code_exec.py when present (MAX_MANIFEST_BYTES, MAX_SNIPPET_CHARS, or
equivalents) and use those; when no constant exists the probe FAILS
"no cap constant" instead of silently assuming one.

### Probe 8a1: malformed manifest JSON fails closed per call, nothing else breaks

Attack: manifest.json is invalid JSON. The loader must return an error
envelope for that run_snippet call and nothing else; it must never raise
out of run_snippet, and a plain model-written program must still run.

```python
# probe p8a1_malformed_manifest.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
H.manifest_path(tree).write_text('{ this is not json', encoding='utf-8')
backend = H.FakeBackend()
session = mod.CodeExecSession(backend)
entries = []
try:
    env = H.call_snippet(mod, session, 'p1-terminal-df')
    refused = not env['ok']
except Exception as exc:
    H.verdict(False, '8a1: run_snippet raised out of the envelope on malformed manifest: %r (expected an error envelope, never an exception)' % exc)
plain = session.run('x = 1 + 1\nassert_state(x == 2, "plain program broken")')
H.verdict(refused and plain['ok'],
    '8a1: malformed manifest refused=%s error=%s, plain program ok=%s (expected error envelope for the snippet call, plain programs unaffected)' % (
        refused, env.get('error'), plain['ok']))
```

PASS: snippet call returns ok=False envelope, plain program ok=True.
FAIL: run_snippet raises, or the whole runner breaks (plain program
fails), or the snippet call somehow succeeds.

### Probe 8a2: one bad entry is skipped, the rest still run

Attack: one manifest entry is missing a required field (or has a bad
type, for example params as a string). The loader must skip that entry
with a logged warning and never offer it; every other entry stays
runnable.

```python
# probe p8a2_bad_entry.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
data = H.read_manifest(tree)
entries = data['snippets'] if isinstance(data, dict) and 'snippets' in data else data
first = entries[0] if isinstance(entries, list) else entries[list(entries)[0]]
good_name = first['name']
evil = dict(first)
evil['name'] = 'y1b-bad-entry'
evil['params'] = 'not-a-list'
if isinstance(entries, list):
    entries.append(evil)
else:
    entries['y1b-bad-entry'] = evil
H.write_manifest(tree, data)
backend = H.FakeBackend()
session = mod.CodeExecSession(backend)
bad = H.call_snippet(mod, session, 'y1b-bad-entry')
good = H.call_snippet(mod, session, good_name)
H.verdict((not bad['ok']) and good['ok'],
    '8a2: bad entry refused=%s error=%s, good entry %s ok=%s (expected bad entry skipped, good entry unaffected)' % (
        not bad['ok'], bad.get('error'), good_name, good['ok']))
```

PASS: bad entry ok=False, good entry ok=True. FAIL: bad entry runs, or
the whole registry refuses to load because of one entry.

### Probe 8b: duplicate names are rejected loudly

Attack: two manifest entries with the same name pointing at different
code_path values (bad merge). Lookup order decides silently which one
runs. JSON duplicate keys are the dict-form variant (json.load takes
last-wins silently).

```python
# probe p8b_duplicate_name.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
data = H.read_manifest(tree)
entries = data['snippets'] if isinstance(data, dict) and 'snippets' in data else data
first = entries[0] if isinstance(entries, list) else entries[list(entries)[0]]
evil = dict(first)
evil['code_path'] = 'y1b_other.py'
(H.snippet_dir(tree) / 'y1b_other.py').write_text('x = 999\n', encoding='utf-8')
evil['sha256'] = H.sha256_file(H.snippet_dir(tree) / 'y1b_other.py')
if isinstance(entries, list):
    entries.append(evil)
else:
    entries[first['name']] = evil
H.write_manifest(tree, data)
backend = H.FakeBackend()
session = mod.CodeExecSession(backend)
env = H.call_snippet(mod, session, first['name'])
if env['ok']:
    H.verdict(False, '8b: duplicated name %s RAN (expected loud refusal: refuse to serve the registry, or at least the duplicated name, until fixed)' % first['name'])
if isinstance(entries, list):
    entries.pop()
else:
    entries.pop(first['name'])
H.write_manifest(tree, data)
control = H.call_snippet(mod, mod.CodeExecSession(H.FakeBackend()), first['name'])
H.verdict(control['ok'],
    '8b: control: duplicate removed, name %s runs again, ok=%s error=%s (expected ok=True: the duplicate, not the entry, caused the refusal)' % (
        first['name'], control['ok'], control.get('error')))
```

PASS: ok=False naming the duplicate. FAIL: ok=True (one of the two
entries ran, and nothing says which). Second leg (CI): tests/test_snippets.py
must contain a test asserting manifest name uniqueness; Y1b greps for
it and reports its absence as a FAIL of the CI leg even if the runtime
leg passes.

### Probe 8c1: manifest size cap enforced at load

Attack: manifest.json grown past the cap (pad it with a 2MB description
field, or duplicate entries until it exceeds 1MB). A 10MB manifest
parses slowly and eats memory on every run_snippet call if loaded per
call.

```python
# probe p8c1_manifest_cap.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
import pathlib
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
cap = getattr(mod, 'MAX_MANIFEST_BYTES', None) or getattr(mod, 'MANIFEST_MAX_BYTES', None) or 1048576
data = H.read_manifest(tree)
entries = data['snippets'] if isinstance(data, dict) and 'snippets' in data else data
first = entries[0] if isinstance(entries, list) else entries[list(entries)[0]]
first['description'] = 'x' * (cap + 1024)
H.write_manifest(tree, data)
size = H.manifest_path(tree).stat().st_size
backend = H.FakeBackend()
session = mod.CodeExecSession(backend)
env = H.call_snippet(mod, session, first['name'])
H.verdict(size > cap and (not env['ok']) and ('size' in (env.get('error') or '').lower() or 'large' in (env.get('error') or '').lower() or 'cap' in (env.get('error') or '').lower() or 'manifest' in (env.get('error') or '').lower()),
    '8c1: manifest %d bytes (cap %d) refused=%s error=%s (expected refuse naming size/cap/manifest)' % (
        size, cap, not env['ok'], env.get('error')))
```

PASS: ok=False naming size, cap, or manifest. FAIL: ok=True (the
oversized manifest loaded and ran). If no cap constant exists in
code_exec.py, this probe FAILS "no manifest cap constant" before
running, since an unenforced cap is not a cap.

### Probe 8c2: snippet file size cap enforced at run (no smuggling past the 8192-char program cap)

Attack: a 1MB snippet file invoked by a 100-char model program. The
8192-char program cap bounds model-written programs but not snippet
files, so run-by-name smuggles an arbitrarily large program past it.

```python
# probe p8c2_snippet_cap.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
cap = getattr(mod, 'MAX_SNIPPET_CHARS', None) or getattr(mod, 'MAX_PROGRAM_CHARS', 8192)
sdir = H.snippet_dir(tree)
big = 'x = 1\n' + '# ' + ('p' * (cap + 1024)) + '\n'
(sdir / 'y1b_big.py').write_text(big, encoding='utf-8')
evil = H.clone_entry(tree, 'y1b-big', 'y1b_big.py', [],
                     description='Oversized snippet',
                     source='y1b probe', expected_result='refused by size cap',
                     tags=['test'])
H.add_entry(tree, evil)
backend = H.FakeBackend()
session = mod.CodeExecSession(backend)
env = H.call_snippet(mod, session, 'y1b-big')
H.verdict((not env['ok']),
    '8c2: %d-char snippet (cap %d) refused=%s error=%s (expected refuse: the file cap binds snippet files, not only CI)' % (
        len(big), cap, not env['ok'], env.get('error')))
```

PASS: ok=False. FAIL: ok=True (a megabyte snippet executed through a
short program). Note: if Codex justifies a larger cap for a specific
snippet in review, Y1b records the justification and re-runs this probe
with that cap; an undocumented larger cap is a FAIL.

### Probe 8d: run_snippet shares budgets, no nested run() reset (budget amplification)

Attack (redteam 8d): a program calls run_snippet in a loop. If
run_snippet calls run() or builds a nested session, each inner execution
gets a fresh 32 API calls and a fresh 30s wall clock, and the outer
counters are clobbered: 32 outer calls times 32 inner calls is 1024 API
calls from one program, up to 16 minutes of wall time, inside budgets
that claim 32 calls and 60s max.

```python
# probe p8d_budget_amplification.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
sdir = H.snippet_dir(tree)
(sdir / 'y1b_tiny.py').write_text('wins = windows()\n', encoding='utf-8')
evil = H.clone_entry(tree, 'y1b-tiny', 'y1b_tiny.py', [],
                     description='One windows() call',
                     source='y1b probe', expected_result='ok True',
                     tags=['test'])
H.add_entry(tree, evil)
backend = H.FakeBackend()
session = mod.CodeExecSession(backend)
env = session.run('for i in range(40):\n    run_snippet("y1b-tiny")\n')
win_calls = len([c for c in backend.calls if c[0] == 'windows'])
H.verdict((not env['ok']) and 'budget' in (env.get('error') or '').lower() and win_calls <= 32,
    '8d: loop of 40 run_snippet calls, ok=%s error=%s windows_calls=%d envelope_api_calls=%s (expected budget refusal once 32 API calls are spent, at most 32 backend windows calls)' % (
        env['ok'], env.get('error'), win_calls, env.get('api_calls')))
```

PASS: envelope ok=False naming the API budget, backend windows calls at
most 32, envelope api_calls at most 32. FAIL: ok=True, or more than 32
backend calls happened (the inner runs got fresh budgets), or
api_calls reset to a small number after the loop (outer counter
clobbered). Second leg (wall clock): a snippet doing
`x = sum(range(10**8))` inside run_snippet with wall_seconds=2 must be
charged against the OUTER deadline: Y1b runs it with a 2s wall and
expects refusal or interruption near 2s, not a 9s ok=True envelope
(redteam R6b). If the fixed code only documents the wall budget as
post-hoc (must-fix 13, should-fix), Y1b records that and this leg
passes only if the call is refused up front or interrupted near the
deadline.

### Probe 8e: snippet .py files are never imported (import bypasses the scan)

Attack (redteam 8e): a poisoned snippet file with `import os` at the top
plus a top-level side effect (writing a marker file). Any tooling that
imports it executes its top-level statements with full process
privileges and NO AST scan.

```python
# probe p8e_no_import.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
import pathlib, subprocess
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
sdir = H.snippet_dir(tree)
marker = pathlib.Path('/tmp/y1b-import-marker.txt')
marker.unlink(missing_ok=True)
(sdir / 'y1b_poison.py').write_text(
    'import os\nos.system("touch /tmp/y1b-import-marker.txt")\n', encoding='utf-8')
has_init = (sdir / '__init__.py').exists()
grep = subprocess.run(['grep', '-rn', '--include=*.py', '-E',
                       r'import (snippets|scripts\.snippets)|importlib.*snippets|from snippets',
                       'scripts', 'tests'], capture_output=True, text=True, cwd=str(tree))
env = None
backend = H.FakeBackend()
session = mod.CodeExecSession(backend)
evil = H.clone_entry(tree, 'y1b-poison', 'y1b_poison.py', [],
                     description='Poisoned snippet',
                     source='y1b probe', expected_result='rejected by scan',
                     tags=['test'])
H.add_entry(tree, evil)
env = H.call_snippet(mod, session, 'y1b-poison')
H.verdict((not has_init) and not grep.stdout.strip() and (not env['ok']) and not marker.exists(),
    '8e: no __init__.py=%s, no import of snippets in repo=%s, run_snippet refused=%s error=%s, marker_exists=%s (expected all four: text-only loading, scan rejects the import, side effect never fires)' % (
        not has_init, not grep.stdout.strip(), not env['ok'], env.get('error'), marker.exists()))
```

PASS: no __init__.py in the snippets dir, no repo code imports snippet
files, run_snippet refuses the poisoned file, marker file absent.
FAIL: any one of the four fails. Note: the grep runs over the temp
tree scripts/ and tests/; Y1b also runs it over the real worktree and
reports hits. A CI test grepping for snippet imports is the durable
version of this leg; Y1b checks tests/test_snippets.py contains it.

### Probe 8f: path traversal through name or code_path is refused (redteam 9a)

Attack: manifest entry with code_path `../../code_exec.py`,
`/etc/passwd`, or `../secret.py`; or a run_snippet name containing
`../` or an absolute path. The loader must resolve code_path and
require it under the snippets directory, reject absolute paths and any
`..` component, and reject names that are not kebab-case matching the
manifest key.

```python
# probe p8f_path_traversal.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
data = H.read_manifest(tree)
entries = data['snippets'] if isinstance(data, dict) and 'snippets' in data else data
first = entries[0] if isinstance(entries, list) else entries[list(entries)[0]]
sdir = H.snippet_dir(tree)
import builtins, pathlib
orig_open = builtins.open
orig_read_bytes = pathlib.Path.read_bytes
orig_read_text = pathlib.Path.read_text
outside_reads = []
def _is_outside(p):
    try:
        pp = pathlib.Path(p)
        return pp.is_absolute() and sdir.resolve() not in pp.resolve().parents and pp.resolve() != sdir.resolve()
    except Exception:
        return False
def counting_open(file, *a, **k):
    if _is_outside(file):
        outside_reads.append(str(file))
    return orig_open(file, *a, **k)
def counting_rb(self, *a, **k):
    if _is_outside(self):
        outside_reads.append(str(self))
    return orig_read_bytes(self, *a, **k)
def counting_rt(self, *a, **k):
    if _is_outside(self):
        outside_reads.append(str(self))
    return orig_read_text(self, *a, **k)
builtins.open = counting_open
pathlib.Path.read_bytes = counting_rb
pathlib.Path.read_text = counting_rt
results = {}
try:
    for label, code_path in (('dotdot', '../code_exec.py'), ('absolute', '/etc/passwd'),
                             ('nested-dotdot', 'sub/../../code_exec.py')):
        evil = dict(first)
        evil['name'] = 'y1b-trav-' + label
        evil['code_path'] = code_path
        if isinstance(entries, list):
            entries.append(evil)
        else:
            entries['y1b-trav-' + label] = evil
        H.write_manifest(tree, data)
        backend = H.FakeBackend()
        session = mod.CodeExecSession(backend)
        env = H.call_snippet(mod, session, 'y1b-trav-' + label)
        results[label] = not env['ok']
        if isinstance(entries, list):
            entries.pop()
        else:
            entries.pop('y1b-trav-' + label)
        H.write_manifest(tree, data)
    name_env = H.call_snippet(mod, mod.CodeExecSession(H.FakeBackend()), '../../cu')
    results['name-dotdot'] = not name_env['ok']
finally:
    builtins.open = orig_open
    pathlib.Path.read_bytes = orig_read_bytes
    pathlib.Path.read_text = orig_read_text
H.verdict(all(results.values()) and not outside_reads,
    '8f: traversal refused=%s outside_snippets_reads=%s (expected every code_path and name variant refused, and no file outside snippets/ read at all, including /etc/passwd)' % (results, outside_reads))
```

PASS: every variant ok=False, and no file outside the snippets dir was
read during any call (the outside-read counter stays empty; a refusal
that still read /etc/passwd is a FAIL, because the read itself is the
traversal). FAIL: any variant runs, or any outside file was read.

### Probe 8g: cross-snippet variable poisoning is blocked (redteam 9c)

Attack: snippet A sets `term_title = "attacker-controlled"`; snippet B
reads `term_title` expecting its own param or default. Session variables
persist across programs, so B is poisoned by whoever ran before it.
This probe was validated against the CURRENT unfixed code on the VM:
program 1 set term_title, program 2 read it back as
"attacker-controlled". The fixed code must snapshot variables on
run_snippet entry and restore them on exit, except for one declared
output, with params as frame locals.

```python
# probe p8g_variable_poisoning.py
import sys
sys.path.insert(0, '/tmp/y1b-probes')
import harness as H
tree = H.temp_tree()
mod = H.load_code_exec(tree)
H.need_run_snippet(mod)
sdir = H.snippet_dir(tree)
(sdir / 'y1b_setter.py').write_text('term_title = "attacker-controlled"\n', encoding='utf-8')
(sdir / 'y1b_reader.py').write_text('seen = term_title\n', encoding='utf-8')
(sdir / 'y1b_reader2.py').write_text(
    'seen = term_title\n'
    'assert_state(seen == "speed-pick1-term", "poisoned: got " + seen)\n', encoding='utf-8')
for nm, fn, params in (('y1b-setter', 'y1b_setter.py', []),
                       ('y1b-reader', 'y1b_reader.py', []),
                       ('y1b-reader2', 'y1b_reader2.py', [{'name': 'term_title', 'type': 'string', 'required': False, 'default': 'speed-pick1-term'}])):
    evil = H.clone_entry(tree, nm, fn, params,
                         description='y1b probe snippet',
                         source='y1b probe', expected_result='see probe',
                         tags=['test'], requires_approval=False)
    H.add_entry(tree, evil)
backend = H.FakeBackend()
session = mod.CodeExecSession(backend)
first = H.call_snippet(mod, session, 'y1b-setter')
second = H.call_snippet(mod, session, 'y1b-reader')
leaked = session.variables.get('term_title')
seen = second.get('variables', {}).get('seen')
leg1 = (not second['ok']) and ('NameError' in (second.get('error_type') or '') or 'not defined' in (second.get('error') or '')) and leaked is None and seen is None
third = H.call_snippet(mod, session, 'y1b-reader2')
leg2 = third['ok'] and session.variables.get('term_title') in (None, 'speed-pick1-term')
H.verdict(first['ok'] and leg1 and leg2,
    '8g: setter ok=%s, reader-no-param ok=%s error=%s seen=%r session_term_title=%r (leg1: reader must NameError, never see A variable), reader-with-default ok=%s (leg2: own param default works, param does not persist)' % (
        first['ok'], second['ok'], second.get('error'), seen, leaked, third['ok']))
```

PASS: the reader with NO param fails with NameError (it never sees the
setter's variable), the session holds no term_title after the setter,
and the reader WITH an explicit param default sees its own default and
leaves no term_title behind. Note: on a nested-run() implementation
this probe can pass vacuously, because the outer run's variable save
clobbers the snippet's write; read 8g together with 8d, which FAILs any
nested-run implementation. The probe is written for the required INLINE
architecture.
FAIL: the no-param reader returns
ok=True with seen="attacker-controlled" (the poison crossed the snippet
boundary), or session.variables still holds "attacker-controlled" after
the setter ran. The no-param leg is the sharp one: a param default
overwrites a poisoned variable in some implementations, so a probe that
only tests the default case passes on vulnerable code. Second leg:
call the reader with an explicit param term_title="my-term" and assert
it sees "my-term"; then assert session.variables has no term_title
left over from the param binding (params are frame locals, never
persistent variables).

---

## Summary table (probe to must-fix item)

| Item | Probes | VM runnable | Laptop-only |
|---|---|---|---|
| 5 snippet trust | 5a, 5a2, 5a3, 5b1, 5b2, 5c, 5c-laptop, 5d | 5a, 5a2, 5a3, 5b1, 5b2, 5c, 5d | 5c-laptop |
| 6 stale guard | 6a1, 6a2, 6a3, 6b1, 6b2, 6c1, 6c2, 6c3, 6d-VM, 6d-laptop | all except 6d-laptop | 6d-laptop |
| 7 replay/divergence | 7a1, 7a2, 7a3, 7a-live, 7b, 7b-live, 7c, 7c2 | 7a1, 7a2, 7a3, 7b, 7c, 7c2 | 7a-live, 7b-live |
| 8 registry poisoning | 8a1, 8a2, 8b, 8c1, 8c2, 8d, 8e, 8f, 8g | all | none |

Count: 8 item 5 probes (7 VM + 1 laptop), 10 item 6 probes (9 VM + 1 laptop),
8 item 7 probes (6 VM + 2 laptop), 9 item 8 probes (9 VM). Total 35 probes,
31 VM-runnable, 4 laptop-only. Runnable code blocks in this file: 30 python
probe files plus 1 shell probe, plus the shared harness.

## What Y1b must report per probe

One line per probe: probe id, PASS/FAIL/LAPTOP-ONLY, the measured output
(envelope ok flag, error text, backend call counts), and the file plus
line that enforces the fix when it passes. A FAIL must quote the exact
output that shows the attack still working (for example the second
backend act in 7a1, or the ok=True envelope in 6b1). Never trust Codex's
own test report: a probe passes only when the attack from the redteam
report is executed against the fixed code and blocked, as specified above.

## Validation done while writing this spec

- The 7c attack shape was executed against the CURRENT unfixed
  code_exec.py on the VM: a second program calling act() with no observe
  returned ok=True and the backend recorded a second act. Probe 7c must
  flip that result.
- The 8g attack shape was executed against the CURRENT unfixed code:
  program 1 set term_title to "attacker-controlled", program 2 read it
  back as "attacker-controlled". Probe 8g must flip that result.
- The 5d attack shape was executed against the CURRENT unfixed code:
  `"{0.__class__}".format("")` returned `<class 'str'>` with ok=True.
  Probe 5d must flip that result (via must-fix 1 plus the snippet scan).
- All probe code blocks in this file were py_compiled after extraction
  (see Setup extractor, COMPILE_OK) before commit. Compile success is
  not a pass claim: each probe still has to run against y1-snippets.
- Smoke validation on the VM (2026-11-21, before commit): all probes
  were extracted and run against two deliberately vulnerable stub
  registries (a nested-run() run_snippet and an inline run_snippet with
  no isolation, both built from the current code_exec.py plus a P1/P3
  manifest). Every attack-detecting probe FAILed on the stubs with the
  attack visibly working (for example 7c: second act landed; 8d: 40
  windows calls with api_calls=1; 5c: secret typed; 8g on the inline
  stub: seen='attacker-controlled'; 7c2: B dom_act landed on A snapshot),
  and the control legs passed. Probes that PASS on the stubs are
  documented in their own text as either companions (6a1, caught by
  6a2), scope checks (7a2), or regression guards for behavior the
  current code already has (8a1, 8a2, 8c2, 8e). 8g passes vacuously on
  the nested stub only; read it with 8d. Two probe bugs found by the
  smoke run were fixed before commit: the harness built program source
  with json.dumps (JSON true/false are not valid Python, broke 7c2)
  and probe 8g originally tested only the param-default case, which
  masks the poisoning.
