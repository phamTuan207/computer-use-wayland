"""Tests for the verified-snippet registry and run_snippet (Phase B).

Fresh tests for the fork-architecture port in scripts/code_exec.py. The
fixture manifests are built at runtime in temp dirs; every api_sha256 is
computed from the current code_exec.py bytes (never a git commit), and
every last_verified defaults to today so fixtures never go stale on age.
"""
import hashlib
import importlib.util
import json
import pathlib
import re
import tempfile
import time
import unittest
from datetime import date, timedelta

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'code_exec', ROOT / 'scripts' / 'code_exec.py')
code_exec = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(code_exec)

import sys
sys.path.insert(0, str(ROOT / 'tests'))
from test_code_exec import FakeBackend, FakeDomBackend  # noqa: E402


def _days_ago(n):
    return (date.today() - timedelta(days=n)).isoformat()


def _param(name, type_name='string', required=False, default=None,
           description='Fixture param'):
    return {'name': name, 'type': type_name, 'required': required,
            'default': default, 'description': description}


def _make_root(entries):
    """Build a temp snippet root from entry dicts.

    Each entry: name, source (snippet code), plus optional params,
    requires_approval, live_only, output, last_verified, sha256,
    api_sha256, file, description, expected_result, tags. Hashes are
    computed from the actual bytes unless overridden.
    """
    root = pathlib.Path(tempfile.mkdtemp())
    manifest_entries = []
    for entry in entries:
        name = entry['name']
        source = entry['source']
        filename = entry.get('file', name + '.py')
        (root / filename).write_text(source, encoding='utf-8')
        item = {
            'name': name, 'file': filename,
            'sha256': entry.get('sha256') or hashlib.sha256(
                source.encode('utf-8')).hexdigest(),
            'description': entry.get('description', 'Fixture snippet ' + name),
            'params': entry.get('params', []),
            'source': entry.get('source_note', 'tests/test_snippets.py fixture'),
            'last_verified': entry.get('last_verified', date.today().isoformat()),
            'api_sha256': entry.get('api_sha256') or code_exec._api_surface_sha256(),
            'expected_result': entry.get('expected_result', 'ok is true'),
            'tags': entry.get('tags', ['fixture']),
        }
        for key in ('requires_approval', 'live_only', 'output'):
            if key in entry:
                item[key] = entry[key]
        manifest_entries.append(item)
    (root / 'manifest.json').write_text(
        json.dumps({'snippets': manifest_entries}), encoding='utf-8')
    return root


def _session(backend=None, root=None, **kwargs):
    backend = backend if backend is not None else FakeBackend()
    return code_exec.CodeExecSession(
        backend, state_dir=tempfile.mkdtemp(),
        session_token='0123456789abcdef' * 2,
        snippet_root=root, **kwargs)


class DistinctIdBackend(FakeBackend):
    """FakeBackend returning a fresh observation id per observe call."""

    def __init__(self):
        super().__init__()
        self._n = 0

    def observe_window(self, address, crop, max_width):
        result = super().observe_window(address, crop, max_width)
        self._n += 1
        result['id'] = 'obs-%04d' % self._n
        result['created'] = time.time() + self._n * 0.001
        return result


TWO_WINDOWS = 'wins = windows()\nwins = windows()\n'
CALLS_A = 'wins = windows()\n'
CALLS_B = 'run_snippet("calls-a")\n'
CALLS_SELF = 'run_snippet("calls-self")\n'
WITH_PARAM = (
    'wins = windows()\n'
    'matches = [w for w in wins if w["title"] == terminal_title]\n'
    'obs = observe(window=matches[0]["address"])\n')
POISONER = 'shared = "poison"\nfresh = 1\n'
WITH_OUTPUT = 'result = 42\nshared = "poison"\n'
USES_TITLE = WITH_PARAM
BARE_ACT = 'act([{"type": "wait", "ms": 0}])\n'
OBSERVE_THEN_ACT = (
    'obs = observe(window="0xabc")\n'
    'result = act([{"type": "wait", "ms": 0, "scope": obs["scope"], '
    '"observation_id": obs["id"]}], obs)\n')
FIRST_OBSERVER = 'obs = observe(window="0xabc")\n'
SECOND_BARE_ACT = BARE_ACT
BARE_DOM_ACT = (
    'ref = snap["elements"][0]["ref"]\n'
    'result = dom_act(snap, [{"type": "click", "ref": ref, '
    '"scope": "tab-1", "observation_id": snap["snapshot"]}])\n')
DOM_OBSERVE_THEN_ACT = (
    'snap = dom_observe("tab-1")\n'
    'ref = snap["elements"][0]["ref"]\n'
    'result = dom_act(snap, [{"type": "click", "ref": ref, '
    '"scope": "tab-1", "observation_id": snap["snapshot"]}])\n')
# B2-2 cross-run regression fixtures. SCOPED_BARE_ACT stamps scope and
# observation_id so a binding leak is visible as a backend act call,
# not hidden behind the CB-2 missing-scope refusal. OBS_OUT declares
# its observation as output so the outer program can hand it to a
# later snippet in a later run() call.
SCOPED_BARE_ACT = (
    'act([{"type": "wait", "ms": 0, "scope": "window", '
    '"observation_id": "abcdef012345"}])\n')
OBS_OUT = 'obs = observe(window="0xabc")\n'
EXPLICIT_ACT = (
    'result = act([{"type": "wait", "ms": 0, "scope": obs["scope"], '
    '"observation_id": obs["id"]}], obs)\n')
DOM_OBSERVE = 'snap = dom_observe("tab-1")\n'
ECHO_PARAM = 'print(text)\nout = text\n'


class ManifestTests(unittest.TestCase):
    def test_shipped_registry_loads_and_smoke_runs(self):
        entries = code_exec.load_snippet_manifest()
        self.assertEqual([e['name'] for e in entries], ['two-windows'])
        env = code_exec.run_snippet_program(
            'two-windows', FakeBackend(),
            state_dir=tempfile.mkdtemp(),
            session_token='0123456789abcdef' * 2)
        self.assertTrue(env['ok'], env)
        self.assertEqual(env['api_calls'], 3)

    def test_duplicate_names_fail_the_whole_load(self):
        root = _make_root([
            {'name': 'dup', 'source': TWO_WINDOWS},
            {'name': 'dup', 'source': TWO_WINDOWS},
        ])
        with self.assertRaises(code_exec.SnippetRegistryError) as ctx:
            code_exec.load_snippet_manifest(root=root)
        self.assertIn('duplicate snippet names', str(ctx.exception))

    def test_entry_count_cap_is_enforced(self):
        root = _make_root([
            {'name': 's-%03d' % i, 'source': TWO_WINDOWS}
            for i in range(129)])
        with self.assertRaises(code_exec.SnippetRegistryError) as ctx:
            code_exec.load_snippet_manifest(root=root)
        self.assertIn('exceeds 128 entries', str(ctx.exception))

    def test_manifest_size_cap_is_enforced(self):
        root = pathlib.Path(tempfile.mkdtemp())
        (root / 'manifest.json').write_text(
            '{"snippets": [], "pad": "' + ('x' * (1024 * 1024 + 10)) + '"}',
            encoding='utf-8')
        with self.assertRaises(code_exec.SnippetRegistryError) as ctx:
            code_exec.load_snippet_manifest(root=root)
        self.assertIn('exceeds 1MB size cap', str(ctx.exception))

    def test_malformed_manifest_json_is_an_error(self):
        root = pathlib.Path(tempfile.mkdtemp())
        (root / 'manifest.json').write_text('{not json', encoding='utf-8')
        with self.assertRaises(code_exec.SnippetRegistryError):
            code_exec.load_snippet_manifest(root=root)

    def test_missing_manifest_is_an_error(self):
        root = pathlib.Path(tempfile.mkdtemp())
        with self.assertRaises(code_exec.SnippetRegistryError):
            code_exec.load_snippet_manifest(root=root)

    def test_invalid_entry_is_skipped_and_valid_entry_loads(self):
        root = _make_root([
            {'name': 'good', 'source': TWO_WINDOWS},
            {'name': 'bad-sha', 'source': TWO_WINDOWS,
             'sha256': '0' * 64, 'api_sha256': 'not-hex'},
        ])
        # The bad entry has a malformed api_sha256, so the loader skips it.
        entries = code_exec.load_snippet_manifest(root=root)
        self.assertEqual([e['name'] for e in entries], ['good'])

    def test_unknown_manifest_field_skips_the_entry(self):
        # Per-entry budget caps are not supported in the fork port; an
        # entry declaring wall_seconds is rejected at load, fail-closed.
        root = _make_root([{'name': 'good', 'source': TWO_WINDOWS}])
        raw = json.loads((root / 'manifest.json').read_text())
        raw['snippets'][0]['wall_seconds'] = 5
        (root / 'manifest.json').write_text(json.dumps(raw))
        entries = code_exec.load_snippet_manifest(root=root)
        self.assertEqual(entries, [])

    def test_path_traversal_and_absolute_paths_are_rejected(self):
        for bad_file in ('../evil.py', '/tmp/evil.py', 'sub/../../evil.py'):
            root = _make_root([{'name': 'good', 'source': TWO_WINDOWS}])
            raw = json.loads((root / 'manifest.json').read_text())
            raw['snippets'][0]['file'] = bad_file
            (root / 'manifest.json').write_text(json.dumps(raw))
            entries = code_exec.load_snippet_manifest(root=root)
            self.assertEqual(entries, [], bad_file)

    def test_duplicate_json_keys_are_rejected(self):
        root = pathlib.Path(tempfile.mkdtemp())
        (root / 'manifest.json').write_text(
            '{"snippets": [], "snippets": []}', encoding='utf-8')
        with self.assertRaises(code_exec.SnippetRegistryError) as ctx:
            code_exec.load_snippet_manifest(root=root)
        self.assertIn('duplicate manifest JSON key', str(ctx.exception))


class RunSnippetTests(unittest.TestCase):
    def test_unknown_snippet_names_closest_match(self):
        root = _make_root([{'name': 'two-windows', 'source': TWO_WINDOWS}])
        env = _session(root=root).run('run_snippet("two-windowz")\n')
        self.assertFalse(env['ok'])
        self.assertIn('unknown snippet: two-windowz', env['error'])
        self.assertIn('two-windows', env['error'])

    def test_hash_mismatch_refuses_before_backend_calls(self):
        backend = FakeBackend()
        root = _make_root([{'name': 'two-windows', 'source': TWO_WINDOWS,
                            'sha256': 'f' * 64}])
        env = _session(backend, root=root).run('run_snippet("two-windows")\n')
        self.assertFalse(env['ok'])
        self.assertIn('sha256 mismatch', env['error'])
        self.assertEqual(backend.calls, [])

    def test_malformed_snippet_file_is_an_error_envelope(self):
        backend = FakeBackend()
        root = _make_root([{'name': 'broken', 'source': 'x = (\n'}])
        env = _session(backend, root=root).run('run_snippet("broken")\n')
        self.assertFalse(env['ok'])
        self.assertEqual(backend.calls, [])

    def test_api_hash_mismatch_is_stale_and_allow_stale_runs(self):
        backend = FakeBackend()
        root = _make_root([{'name': 'two-windows', 'source': TWO_WINDOWS,
                            'api_sha256': 'a' * 64}])
        env = _session(backend, root=root).run('run_snippet("two-windows")\n')
        self.assertFalse(env['ok'])
        self.assertIn('stale', env['error'])
        self.assertIn('two-windows', env['error'])
        self.assertEqual(backend.calls, [])
        env = _session(backend, root=root).run(
            'run_snippet("two-windows", allow_stale=True)\n')
        self.assertTrue(env['ok'], env)
        self.assertTrue(any('stale override' in line for line in env['log']))

    def test_api_surface_hash_matches_the_file_bytes(self):
        digest = hashlib.sha256(
            (ROOT / 'scripts' / 'code_exec.py').read_bytes()).hexdigest()
        self.assertEqual(code_exec._api_surface_sha256(), digest)

    def test_param_names_cannot_shadow_apis(self):
        # A param named after an API function, and a snippet whose NAME
        # collides with an API function, are both rejected at load.
        root = _make_root([
            {'name': 'shadow-windows', 'source': TWO_WINDOWS,
             'params': [_param('windows', 'string', False, 'x')]},
            {'name': 'windows', 'source': TWO_WINDOWS},
            {'name': 'good', 'source': TWO_WINDOWS},
        ])
        entries = code_exec.load_snippet_manifest(root=root)
        self.assertEqual([e['name'] for e in entries], ['good'])

    def test_unknown_and_wrong_type_params_are_rejected(self):
        root = _make_root([{'name': 'with-param', 'source': WITH_PARAM,
                            'params': [_param('terminal_title', 'string',
                                             False, 'speed-pick1-term')]}])
        env = _session(root=root).run(
            'run_snippet("with-param", nope=1)\n')
        self.assertFalse(env['ok'])
        self.assertIn('unknown snippet params', env['error'])
        env = _session(root=root).run(
            'run_snippet("with-param", terminal_title=7)\n')
        self.assertFalse(env['ok'])
        self.assertIn('must have type string', env['error'])

    def test_params_are_frame_locals_and_do_not_persist(self):
        root = _make_root([{'name': 'with-param', 'source': WITH_PARAM,
                            'params': [_param('terminal_title', 'string',
                                             False, 'speed-pick1-term')]}])
        session = _session(root=root)
        env = session.run(
            'run_snippet("with-param", terminal_title="speed-pick1-term")\n')
        self.assertTrue(env['ok'], env)
        self.assertNotIn('terminal_title', session.variables)
        env2 = session.run('x = terminal_title\n')
        self.assertFalse(env2['ok'])
        self.assertEqual(env2['error_type'], 'NameError')

    def test_snippet_variables_do_not_leak_and_output_propagates(self):
        root = _make_root([
            {'name': 'poisoner', 'source': POISONER},
            {'name': 'with-output', 'source': WITH_OUTPUT, 'output': 'result'},
        ])
        session = _session(root=root)
        self.assertTrue(session.run('shared = "before"\n')['ok'])
        env = session.run('run_snippet("poisoner")\n')
        self.assertTrue(env['ok'], env)
        self.assertEqual(session.variables.get('shared'), 'before')
        self.assertNotIn('fresh', session.variables)
        env = session.run('run_snippet("with-output")\n')
        self.assertTrue(env['ok'], env)
        self.assertEqual(session.variables.get('result'), 42)
        self.assertEqual(session.variables.get('shared'), 'before')

    def test_snippet_sees_outer_variables(self):
        backend = FakeBackend()
        root = _make_root([{'name': 'uses-title', 'source': USES_TITLE}])
        session = _session(backend, root=root)
        env = session.run('terminal_title = "speed-pick1-term"\n'
                          'run_snippet("uses-title")\n')
        self.assertTrue(env['ok'], env)
        observes = [c for c in backend.calls if c[0] == 'observe_window']
        self.assertEqual(len(observes), 1)
        self.assertEqual(observes[0][1], '0xabc')

    def test_snippet_in_place_mutation_does_not_leak(self):
        root = _make_root([{'name': 'mutator',
                            'source': 'wins.append("pwned")\n'}])
        session = _session(root=root)
        self.assertTrue(session.run('wins = ["a"]\n')['ok'])
        env = session.run('run_snippet("mutator")\n')
        self.assertTrue(env['ok'], env)
        self.assertEqual(session.variables.get('wins'), ['a'])

    def test_loop_shares_api_budget(self):
        # Probe 10a: 5x two-windows in a loop, max_api_calls=6. Each
        # run_snippet costs 1 fetch plus 2 windows calls; the shared
        # counter trips at 6 with at most 6 backend calls served.
        backend = FakeBackend()
        root = _make_root([{'name': 'two-windows', 'source': TWO_WINDOWS}])
        session = _session(backend, root=root, max_api_calls=6)
        env = session.run('for i in range(5):\n'
                          '    run_snippet("two-windows")\n')
        self.assertFalse(env['ok'])
        self.assertIn('API call budget exceeded', env['error'])
        windows_calls = [c for c in backend.calls if c[0] == 'windows']
        self.assertLessEqual(len(windows_calls), 6)
        self.assertEqual(session.api_calls, 6)

    def test_nested_snippets_are_rejected(self):
        # Probe 10c: nested and self calls refuse naming the depth cap;
        # the inner body never executes; sequential top-level calls work.
        backend = FakeBackend()
        root = _make_root([
            {'name': 'calls-a', 'source': CALLS_A},
            {'name': 'calls-b', 'source': CALLS_B},
            {'name': 'calls-self', 'source': CALLS_SELF},
        ])
        session = _session(backend, root=root)
        env = session.run('run_snippet("calls-b")\n')
        self.assertFalse(env['ok'])
        self.assertIn('nested run_snippet is not allowed', env['error'])
        self.assertEqual(backend.calls, [])
        env = session.run('run_snippet("calls-self")\n')
        self.assertFalse(env['ok'])
        self.assertIn('nested run_snippet is not allowed', env['error'])
        self.assertEqual(backend.calls, [])
        env = session.run('run_snippet("calls-a")\nrun_snippet("calls-a")\n')
        self.assertTrue(env['ok'], env)
        self.assertEqual(len(backend.calls), 2)

    def test_no_nested_run_or_session(self):
        # Probe 10d, runtime tripwire plus static check on the stub.
        backend = FakeBackend()
        root = _make_root([{'name': 'two-windows', 'source': TWO_WINDOWS}])
        session = _session(backend, root=root)
        orig = code_exec.CodeExecSession.run
        calls = []

        def counting(self, *args, **kwargs):
            calls.append(1)
            return orig(self, *args, **kwargs)

        code_exec.CodeExecSession.run = counting
        try:
            env = orig(session, 'run_snippet("two-windows")\n')
        finally:
            code_exec.CodeExecSession.run = orig
        self.assertEqual(calls, [])
        self.assertTrue(env['ok'], env)
        source = (ROOT / 'scripts' / 'code_exec.py').read_text()
        start = source.index('def run_snippet_stub')
        end = source.index("namespace = dict(self.variables)", start)
        stub_source = source[start:end]
        self.assertNotIn('self.run(', stub_source)
        self.assertNotIn('CodeExecSession(', stub_source)
        self.assertNotIn('run_program(', stub_source)

    def test_observation_bindings_scoped_per_snippet(self):
        # Probes 11e/11g: a snippet that acts without its own fresh
        # observe fails; a snippet that observes then acts succeeds; a
        # second snippet cannot act on the first snippet's observation.
        backend = FakeBackend()
        root = _make_root([
            {'name': 'bare-act', 'source': BARE_ACT},
            {'name': 'observe-then-act', 'source': OBSERVE_THEN_ACT},
            {'name': 'first-observer', 'source': FIRST_OBSERVER},
            {'name': 'second-bare-act', 'source': SECOND_BARE_ACT},
        ])
        session = _session(backend, root=root)
        env = session.run('obs = observe(window="0xabc")\n'
                          'run_snippet("bare-act")\n')
        self.assertFalse(env['ok'])
        self.assertIn('not bound to this snippet run', env['error'])
        self.assertEqual([c for c in backend.calls if c[0] == 'act'], [])
        env = session.run('run_snippet("observe-then-act")\n')
        self.assertTrue(env['ok'], env)
        self.assertEqual(len([c for c in backend.calls if c[0] == 'act']), 1)
        env = session.run('run_snippet("first-observer")\n'
                          'run_snippet("second-bare-act")\n')
        self.assertFalse(env['ok'])
        self.assertIn('not bound to this snippet run', env['error'])
        self.assertEqual(len([c for c in backend.calls if c[0] == 'act']), 1)

    def test_dom_bindings_scoped_per_snippet(self):
        # Probe 11f, same shape on the DOM path.
        backend = FakeDomBackend()
        root = _make_root([
            {'name': 'bare-dom-act', 'source': BARE_DOM_ACT},
            {'name': 'dom-observe-then-act', 'source': DOM_OBSERVE_THEN_ACT},
        ])
        session = _session(backend, root=root)
        env = session.run('snap = dom_observe("tab-1")\n'
                          'run_snippet("bare-dom-act")\n')
        self.assertFalse(env['ok'])
        self.assertIn('not bound to this snippet run', env['error'])
        self.assertEqual(
            sum(1 for c in backend.dom_calls if c[0] == 'act'), 0)
        env = session.run('run_snippet("dom-observe-then-act")\n')
        self.assertTrue(env['ok'], env)
        self.assertEqual(
            sum(1 for c in backend.dom_calls if c[0] == 'act'), 1)

    def test_observation_bindings_cross_run(self):
        # B2-2: snippet run ids must not repeat across run() calls of
        # the same session. Before the fix the child-local counter
        # reset to 1 on every run(), so a snippet in run 2 could act
        # on a snippet's observation from run 1.
        backend = FakeBackend()
        root = _make_root([
            {'name': 'first-observer', 'source': FIRST_OBSERVER},
            {'name': 'second-scoped-bare-act', 'source': SCOPED_BARE_ACT},
            {'name': 'obs-out', 'source': OBS_OUT, 'output': 'obs'},
            {'name': 'explicit-act', 'source': EXPLICIT_ACT},
        ])
        session = _session(backend, root=root)
        # None fallback, cross-run, scoped so the leak would act.
        env = session.run('run_snippet("first-observer")\n')
        self.assertTrue(env['ok'], env)
        env = session.run('run_snippet("second-scoped-bare-act")\n')
        self.assertFalse(env['ok'])
        self.assertIn('not bound to this snippet run', env['error'])
        self.assertEqual([c for c in backend.calls if c[0] == 'act'], [])
        # Explicit act, cross-run, via the first snippet's output.
        env = session.run('holder = run_snippet("obs-out")\n')
        self.assertTrue(env['ok'], env)
        env = session.run('obs = holder["output"]\n'
                          'run_snippet("explicit-act")\n')
        self.assertFalse(env['ok'])
        self.assertIn('not bound to this snippet run', env['error'])
        self.assertEqual([c for c in backend.calls if c[0] == 'act'], [])
        # Guard: the outer program (run 0) may still reuse its own
        # observation across run() calls; only snippet ids are fresh.
        env = session.run('obs = observe(window="0xabc")\n')
        self.assertTrue(env['ok'], env)
        env = session.run(
            'result = act([{"type": "wait", "ms": 0, '
            '"scope": obs["scope"], "observation_id": obs["id"]}], obs)\n')
        self.assertTrue(env['ok'], env)
        self.assertEqual(len([c for c in backend.calls if c[0] == 'act']), 1)

    def test_dom_bindings_cross_run(self):
        # B2-2, DOM path: a DOM snapshot from run 1 must not be usable
        # by a snippet in run 2, even though the snapshot id repeats
        # in the fake backend.
        backend = FakeDomBackend()
        root = _make_root([
            {'name': 'dom-observe', 'source': DOM_OBSERVE, 'output': 'snap'},
            {'name': 'bare-dom-act', 'source': BARE_DOM_ACT},
        ])
        session = _session(backend, root=root)
        env = session.run('holder = run_snippet("dom-observe")\n')
        self.assertTrue(env['ok'], env)
        env = session.run('snap = holder["output"]\n'
                          'run_snippet("bare-dom-act")\n')
        self.assertFalse(env['ok'])
        self.assertIn('not bound to this snippet run', env['error'])
        self.assertEqual(
            sum(1 for c in backend.dom_calls if c[0] == 'act'), 0)

    def test_bound_observation_none_rejects_stale(self):
        # B2-2: the None fallback must check age like the explicit
        # branch. Age the observation to 200s, past the 120s window.
        backend = FakeBackend()
        session = _session(backend, root=None)
        session._current_snippet_run = 1
        session.api_observe(window='0xabc')
        session.observations['abcdef012345']['created'] = time.time() - 200
        with self.assertRaises(code_exec.CodeExecError) as ctx:
            session._bound_observation(None)
        self.assertIn('older than 120s', str(ctx.exception))
        with self.assertRaises(code_exec.CodeExecError) as ctx:
            session._bound_observation({'id': 'abcdef012345'})
        self.assertIn('older than 120s', str(ctx.exception))
        # A fresh observation from the same run still passes None.
        session.api_observe(window='0xabc')
        meta = session._bound_observation(None)
        self.assertEqual(meta['id'], 'abcdef012345')

    def test_param_injection_stays_data(self):
        # Probe 11h: code-shaped param values arrive as plain strings.
        root = _make_root([{'name': 'echo-param', 'source': ECHO_PARAM,
                            'params': [_param('text', 'string', True, None)],
                            'output': 'out'}])
        session = _session(root=root)
        for payload in ('x"); import os; (', '{0.__class__}'):
            env = session.run(
                'result = run_snippet("echo-param", text=%s)\n'
                % json.dumps(payload))
            self.assertTrue(env['ok'], env)
            self.assertEqual(env['variables']['result']['output'], payload)

    def test_requires_approval_and_ledger_prevent_a_retry(self):
        root = _make_root([
            {'name': 'needs-ok', 'source': TWO_WINDOWS,
             'requires_approval': True},
            {'name': 'fails-first', 'source': 'assert_state(False, "boom")\n',
             'requires_approval': True},
        ])
        session = _session(root=root)
        env = session.run('run_snippet("needs-ok")\n')
        self.assertFalse(env['ok'])
        self.assertIn('requires approval', env['error'])
        env = session.run_snippet_program('needs-ok', approved=True)
        self.assertTrue(env['ok'], env)
        env = session.run_snippet_program('needs-ok', approved=True)
        self.assertFalse(env['ok'])
        self.assertIn('already applied', env['error'])
        # A failed application is NOT recorded, so a retry is allowed
        # and fails the same way instead of hitting the ledger.
        env = session.run_snippet_program('fails-first', approved=True)
        self.assertFalse(env['ok'])
        self.assertIn('boom', env['error'])
        env = session.run_snippet_program('fails-first', approved=True)
        self.assertFalse(env['ok'])
        self.assertIn('boom', env['error'])
        self.assertNotIn('already applied', env['error'])

    def test_stale_boundaries_live_only_30_days(self):
        # Probe 12a: 29 days runs, 31 days refuses and leaves search.
        root = _make_root([
            {'name': 'live-fresh', 'source': TWO_WINDOWS,
             'live_only': True, 'last_verified': _days_ago(29)},
            {'name': 'live-stale', 'source': TWO_WINDOWS,
             'live_only': True, 'last_verified': _days_ago(31)},
        ])
        session = _session(root=root)
        env = session.run('run_snippet("live-fresh")\n')
        self.assertTrue(env['ok'], env)
        env = session.run('run_snippet("live-stale")\n')
        self.assertFalse(env['ok'])
        self.assertIn('live-stale', env['error'])
        self.assertIn('31 days', env['error'])
        self.assertIn('stale', env['error'])
        names = [item['name'] for item in code_exec.search_snippets(root=root)]
        self.assertIn('live-fresh', names)
        self.assertNotIn('live-stale', names)

    def test_stale_boundaries_vm_90_days(self):
        # Probe 12b: 89 days runs, 91 days refuses.
        root = _make_root([
            {'name': 'vm-fresh', 'source': TWO_WINDOWS,
             'last_verified': _days_ago(89)},
            {'name': 'vm-stale', 'source': TWO_WINDOWS,
             'last_verified': _days_ago(91)},
        ])
        session = _session(root=root)
        env = session.run('run_snippet("vm-fresh")\n')
        self.assertTrue(env['ok'], env)
        env = session.run('run_snippet("vm-stale")\n')
        self.assertFalse(env['ok'])
        self.assertIn('91 days', env['error'])

    def test_search_hides_hash_mismatched_entry(self):
        root = _make_root([
            {'name': 'good', 'source': TWO_WINDOWS},
            {'name': 'bad-hash', 'source': TWO_WINDOWS,
             'sha256': 'e' * 64},
        ])
        names = [item['name'] for item in code_exec.search_snippets(root=root)]
        self.assertEqual(names, ['good'])

    def test_describe_returns_metadata_without_code(self):
        root = _make_root([{'name': 'two-windows', 'source': TWO_WINDOWS}])
        entry = code_exec.describe_snippet('two-windows', root=root)
        self.assertEqual(entry['name'], 'two-windows')
        self.assertIn('sha256', entry)
        with self.assertRaises(code_exec.SnippetRegistryError) as ctx:
            code_exec.describe_snippet('two-windowz', root=root)
        self.assertIn('two-windows', str(ctx.exception))

    def test_run_snippet_program_top_level(self):
        root = _make_root([{'name': 'two-windows', 'source': TWO_WINDOWS}])
        session = _session(root=root)
        env = session.run_snippet_program('two-windows')
        self.assertTrue(env['ok'], env)
        self.assertEqual(env['api_calls'], 3)


class B2Tests(unittest.TestCase):
    def test_observation_cap_on_save(self):
        # B2: 40 observations across two runs; the state file keeps at
        # most MAX_OBSERVATIONS (32), oldest pruned, in memory and disk.
        backend = DistinctIdBackend()
        session = _session(backend, max_api_calls=32)
        program = ''.join('observe(window="0xabc")\n' for _ in range(20))
        self.assertTrue(session.run(program)['ok'])
        self.assertTrue(session.run(program)['ok'])
        self.assertEqual(len(backend.calls), 40)
        self.assertLessEqual(len(session.observations), code_exec.MAX_OBSERVATIONS)
        self.assertEqual(len(session.observations), 32)
        path = session._state_path()
        raw = json.loads(path.read_text(encoding='utf-8'))
        self.assertEqual(len(raw['observations']), 32)
        kept = sorted(raw['observations'])
        self.assertEqual(kept[0], 'obs-0009')
        self.assertEqual(kept[-1], 'obs-0040')

    def test_dom_snapshot_cap_on_save(self):
        backend = FakeDomBackend()
        session = _session(backend, max_api_calls=32)
        for _ in range(40):
            session.dom_snapshots['snap-%02d' % _] = {
                'target': 'tab-1', 'created': float(_), 'refs': [],
                'snapshot': {'snapshot': 'snap-%02d' % _}}
        session._save_state()
        self.assertEqual(len(session.dom_snapshots), 32)
        path = session._state_path()
        raw = json.loads(path.read_text(encoding='utf-8'))
        self.assertEqual(len(raw['dom_snapshots']), 32)


if __name__ == '__main__':
    unittest.main()
