"""Registry and inline execution tests for the promoted Pick 1 snippets."""

import ast
import hashlib
import json
import os
import pathlib
import py_compile
import shutil
import subprocess
import tempfile
import time
import unittest
from contextlib import contextmanager
from datetime import date
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
import importlib.util

SPEC = importlib.util.spec_from_file_location(
    'code_exec_snippets_test', ROOT / 'scripts' / 'code_exec.py')
code_exec = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(code_exec)

from tests.test_code_exec import FakeBackend, FakeShellBackend, FakeTerminalBackend


def _manifest_path(root):
    return pathlib.Path(root) / 'manifest.json'


def _load_manifest(path=None):
    path = pathlib.Path(path or code_exec.SNIPPET_MANIFEST)
    return json.loads(path.read_text(encoding='utf-8'))


def _path_resolver(runtime_root):
    original = code_exec._resolve_read_path
    runtime_root = pathlib.Path(runtime_root)

    def resolve(path):
        value = pathlib.Path(path)
        try:
            relative = value.relative_to('/tmp')
        except ValueError:
            return original(path)
        return runtime_root / relative

    return resolve


def _assert_expected(test, entry, result, backend, runtime_root):
    test.assertTrue(result['ok'], result)
    test.assertTrue(result['snippet']['ok'], result)
    test.assertEqual(result['snippet']['name'], entry['name'])
    test.assertEqual(result['variables']['verify_image'], '/tmp/x.png')
    actions = getattr(backend, 'actions', None)
    if actions is None:
        actions = [call[2][0] for call in backend.calls if call[0] == 'act']
    typed = [action['text'] for action in actions if action.get('type') == 'type']
    if entry['name'] == 'p1-disk-free':
        test.assertEqual(typed, ['df -h /\n'])
    elif entry['name'] == 'p2-percent-calc':
        test.assertEqual(typed, ['python3 -c "print(144/150*100)"\n'])
    elif entry['name'] == 'p3-make-dirs':
        test.assertTrue(typed[0].startswith('rm -rf /tmp/hoc-ky-2 && mkdir -p '))
        root = pathlib.Path(runtime_root) / 'hoc-ky-2'
        for name in ('dsa', 'ktvm', 'oop'):
            test.assertTrue((root / name).is_dir(), str(root / name))
    elif entry['name'] == 'p4-write-ideas':
        test.assertTrue(typed[0].startswith("rm -f /tmp/y-tuong.txt && printf '"))
        expected = (
            'Ý tưởng 1: app nhắc uống nước.\n'
            'Ý tưởng 2: bot tóm tắt bài giảng.\n'
            'Ý tưởng 3: web bán đồ secondhand.\n'
        ).encode('utf-8')
        target = pathlib.Path(runtime_root) / 'y-tuong.txt'
        test.assertEqual(target.read_bytes(), expected)
        test.assertEqual(backend.terminal_output[-1].encode('utf-8'), expected)
    else:
        test.fail('no expected-result check for ' + entry['name'])


def _run_entry(entry, backend, runtime_root):
    with mock.patch.object(code_exec, '_resolve_read_path',
                           _path_resolver(runtime_root)):
        return code_exec.run_snippet_program(
            entry['name'], backend, approved=entry.get('requires_approval', False))


def refresh_manifest_after_verification():
    """Run every snippet on isolated fakes, then update verified metadata."""
    manifest_path = ROOT / 'snippets' / 'manifest.json'
    raw_manifest = _load_manifest(manifest_path)
    commit = subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    verified_date = date.today().isoformat()
    with tempfile.TemporaryDirectory(prefix='y1-snippet-verify-') as folder:
        temporary_root = pathlib.Path(folder)
        temporary_snippets = temporary_root / 'snippets'
        temporary_snippets.mkdir()
        runtime_root = temporary_root / 'runtime'
        runtime_root.mkdir()
        entries = raw_manifest['snippets']
        for entry in entries:
            source_path = ROOT / 'snippets' / entry['file']
            raw = source_path.read_bytes()
            entry['sha256'] = hashlib.sha256(raw).hexdigest()
            entry['last_verified'] = verified_date
            entry['verified_against'] = commit
            (temporary_snippets / entry['file']).write_bytes(raw)
        (_manifest_path(temporary_snippets)).write_text(
            json.dumps(raw_manifest, ensure_ascii=False, indent=2) + '\n',
            encoding='utf-8')
        with mock.patch.object(code_exec, 'SNIPPET_ROOT', temporary_snippets), \
                mock.patch.object(code_exec, 'SNIPPET_MANIFEST',
                                  _manifest_path(temporary_snippets)):
            for entry in entries:
                source_path = temporary_snippets / entry['file']
                source = source_path.read_text(encoding='utf-8')
                tree = code_exec.validate_program(source)
                code_exec._check_snippet_api_names(
                    tree, {param['name'] for param in entry['params']})
                py_compile.compile(
                    str(source_path), doraise=True,
                    cfile=str(temporary_root / (entry['name'] + '.pyc')))
                if entry['name'] in ('p1-disk-free', 'p2-percent-calc'):
                    backend = FakeBackend()
                elif entry['name'] == 'p3-make-dirs':
                    backend = FakeShellBackend(path_root=runtime_root)
                else:
                    backend = FakeTerminalBackend(path_root=runtime_root)
                result = _run_entry(entry, backend, runtime_root)
                if hasattr(backend, 'join_shell'):
                    backend.join_shell()
                helper = unittest.TestCase()
                _assert_expected(helper, entry, result, backend, runtime_root)
                print('verified fake snippet: ' + entry['name'])

    manifest_path.write_text(
        json.dumps(raw_manifest, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8')
    print('updated verified metadata for %d snippets' % len(raw_manifest['snippets']))
    return raw_manifest


@contextmanager
def _temporary_registry(snippets):
    """Install a small, hash-correct manifest for a focused runner test."""
    with tempfile.TemporaryDirectory(prefix='y1-snippet-registry-') as folder:
        root = pathlib.Path(folder)
        for entry in snippets:
            source = entry.pop('_source')
            path = root / entry['file']
            path.parent.mkdir(parents=True, exist_ok=True)
            raw = source.encode('utf-8')
            path.write_bytes(raw)
            entry['sha256'] = hashlib.sha256(raw).hexdigest()
            entry.setdefault('last_verified', date.today().isoformat())
            entry.setdefault('verified_against', 'audit-only')
        manifest_path = _manifest_path(root)
        manifest_path.write_text(
            json.dumps({'snippets': snippets}, ensure_ascii=False),
            encoding='utf-8')
        with mock.patch.object(code_exec, 'SNIPPET_ROOT', root), \
                mock.patch.object(code_exec, 'SNIPPET_MANIFEST', manifest_path):
            yield root, manifest_path


def _entry(name, file, source, params=None, **fields):
    entry = {
        'name': name, 'file': file,
        'sha256': '0' * 64,
        'description': 'Temporary snippet used by a registry regression test.',
        'params': params or [], 'source': 'tests/test_snippets.py',
        'last_verified': date.today().isoformat(),
        'verified_against': 'audit-only',
        'expected_result': 'The temporary snippet result is returned.',
        'tags': ['test'], '_source': source,
    }
    entry.update(fields)
    return entry


class SnippetRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest_path = ROOT / 'snippets' / 'manifest.json'
        cls.manifest = _load_manifest(cls.manifest_path)
        cls.entries = cls.manifest['snippets']

    def test_manifest_is_bounded_and_entries_are_unique(self):
        self.assertLessEqual(self.manifest_path.stat().st_size,
                             code_exec.MAX_SNIPPET_MANIFEST_BYTES)
        names = [entry['name'] for entry in self.entries]
        self.assertEqual(len(names), len(set(names)))
        self.assertLessEqual(len(names), code_exec.MAX_SNIPPET_ENTRIES)

    def test_files_hashes_syntax_and_ast_are_valid(self):
        for entry in self.entries:
            with self.subTest(name=entry['name']):
                path = code_exec._resolve_snippet_path(entry)
                self.assertTrue(path.is_file())
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                                 entry['sha256'])
                source = path.read_text(encoding='utf-8')
                tree = code_exec.validate_program(source)
                code_exec._check_snippet_api_names(
                    tree, {param['name'] for param in entry['params']})
                with tempfile.TemporaryDirectory() as folder:
                    py_compile.compile(
                        str(path), doraise=True,
                        cfile=str(pathlib.Path(folder) / 'snippet.pyc'))

    def test_manifest_has_required_metadata_and_contained_paths(self):
        loaded = code_exec.load_snippet_manifest()
        self.assertEqual([entry['name'] for entry in loaded],
                         [entry['name'] for entry in self.entries])
        for entry in loaded:
            with self.subTest(name=entry['name']):
                self.assertTrue(code_exec.SNIPPET_REQUIRED_FIELDS <= set(entry))
                self.assertIn(entry['source'], (
                    'improvements/pick1-program-template.md P1',
                    'improvements/pick1-program-template.md P2',
                    'improvements/pick1-program-template.md P3',
                    'improvements/pick1-program-template.md P4'))
                path = code_exec._resolve_snippet_path(entry)
                self.assertIn(code_exec.SNIPPET_ROOT.resolve(), path.parents)
                self.assertNotIn('..', pathlib.Path(entry['file']).parts)
                self.assertEqual(entry['params'][0]['name'], 'terminal_title')
                self.assertEqual(entry['params'][0]['default'], 'speed-pick1-term')

    def test_snippets_are_not_a_package_or_imported(self):
        snippets = ROOT / 'snippets'
        self.assertFalse((snippets / '__init__.py').exists())
        for folder in ('scripts', 'tests'):
            for path in (ROOT / folder).glob('*.py'):
                tree = ast.parse(path.read_text(encoding='utf-8'))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        self.assertFalse(any(alias.name == 'snippets'
                                             or alias.name.startswith('snippets.')
                                             for alias in node.names), str(path))
                    elif isinstance(node, ast.ImportFrom):
                        self.assertFalse(node.module == 'snippets'
                                         or (node.module or '').startswith('snippets.'),
                                         str(path))

    def test_every_snippet_runs_on_its_fake_and_expected_result_holds(self):
        with tempfile.TemporaryDirectory(prefix='y1-snippet-output-') as folder:
            runtime_root = pathlib.Path(folder)
            for entry in self.entries:
                with self.subTest(name=entry['name']):
                    if entry['name'] in ('p1-disk-free', 'p2-percent-calc'):
                        backend = FakeBackend()
                    elif entry['name'] == 'p3-make-dirs':
                        backend = FakeShellBackend(path_root=runtime_root)
                    else:
                        backend = FakeTerminalBackend(path_root=runtime_root)
                    result = _run_entry(entry, backend, runtime_root)
                    if hasattr(backend, 'join_shell'):
                        backend.join_shell()
                    _assert_expected(self, entry, result, backend, runtime_root)

    def test_unknown_name_has_closest_match(self):
        result = code_exec.run_program(
            'run_snippet("p1-disk-fre")', FakeBackend())
        self.assertFalse(result['ok'])
        self.assertIn('closest matches: p1-disk-free', result['error'])

    def test_bad_manifest_entry_is_skipped_and_duplicate_names_fail(self):
        good = _entry('test-good', 'test-good.py', 'value = 1')
        bad = _entry('test-bad', '../outside.py', 'value = 2')
        with _temporary_registry([good, bad]) as (root, manifest_path):
            with self.assertLogs(code_exec.__name__, level='WARNING'):
                self.assertEqual([entry['name'] for entry in
                                  code_exec.load_snippet_manifest()], ['test-good'])
            duplicate = _entry('test-same', 'same-a.py', 'value = 1')
            duplicate2 = _entry('test-same', 'same-b.py', 'value = 2')
            manifest_path.write_text(json.dumps(
                {'snippets': [duplicate, duplicate2]}), encoding='utf-8')
            with self.assertRaisesRegex(code_exec.SnippetRegistryError,
                                        'duplicate snippet names'):
                code_exec.load_snippet_manifest()

    def test_manifest_size_cap_is_enforced(self):
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            manifest_path = _manifest_path(root)
            manifest_path.write_bytes(
                b' ' * (code_exec.MAX_SNIPPET_MANIFEST_BYTES + 1))
            with mock.patch.object(code_exec, 'SNIPPET_ROOT', root), \
                    mock.patch.object(code_exec, 'SNIPPET_MANIFEST', manifest_path):
                with self.assertRaisesRegex(code_exec.SnippetRegistryError,
                                             'exceeds 1MB'):
                    code_exec.load_snippet_manifest()

    def test_malformed_manifest_is_returned_as_an_error_envelope(self):
        with tempfile.TemporaryDirectory() as folder:
            root = pathlib.Path(folder)
            manifest_path = _manifest_path(root)
            manifest_path.write_text('{not json', encoding='utf-8')
            with mock.patch.object(code_exec, 'SNIPPET_ROOT', root), \
                    mock.patch.object(code_exec, 'SNIPPET_MANIFEST', manifest_path):
                backend = FakeBackend()
                result = code_exec.run_program(
                    'run_snippet("p1-disk-free")', backend)
        self.assertFalse(result['ok'])
        self.assertEqual(result['error_type'], 'sandbox')
        self.assertIn('manifest is malformed JSON', result['error'])
        self.assertEqual(backend.calls, [])

    def test_hash_mismatch_and_unknown_api_name_fail_before_backend_calls(self):
        entry = _entry('hash-test', 'hash-test.py', 'windows()')
        with _temporary_registry([entry]) as (root, manifest_path):
            (root / entry['file']).write_text('act([])', encoding='utf-8')
            backend = FakeBackend()
            result = code_exec.run_program(
                'run_snippet("hash-test")', backend)
            self.assertFalse(result['ok'])
            self.assertIn('sha256 mismatch', result['error'])
            self.assertEqual(backend.calls, [])

        unknown = _entry('unknown-api', 'unknown-api.py', 'mystery_api()')
        with _temporary_registry([unknown]):
            backend = FakeBackend()
            result = code_exec.run_program(
                'run_snippet("unknown-api")', backend)
        self.assertFalse(result['ok'])
        self.assertIn('unknown API name: mystery_api', result['error'])
        self.assertEqual(backend.calls, [])

    def test_malformed_snippet_file_is_an_error_envelope(self):
        entry = _entry('malformed-test', 'malformed.py', 'value = 1')
        with _temporary_registry([entry]) as (root, manifest_path):
            raw = b'\xff\xfe'
            (root / entry['file']).write_bytes(raw)
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            manifest['snippets'][0]['sha256'] = hashlib.sha256(raw).hexdigest()
            manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
            backend = FakeBackend()
            result = code_exec.run_program(
                'run_snippet("malformed-test")', backend)
        self.assertFalse(result['ok'])
        self.assertEqual(result['error_type'], 'sandbox')
        self.assertIn('valid UTF-8', result['error'])
        self.assertEqual(backend.calls, [])

    def test_search_hides_a_hash_mismatched_entry(self):
        entry = _entry('search-mismatch', 'search-mismatch.py', 'value = 1')
        with _temporary_registry([entry]) as (root, _):
            (root / entry['file']).write_text('value = 2', encoding='utf-8')
            with self.assertLogs(code_exec.__name__, level='WARNING'):
                self.assertEqual(code_exec.search_snippets(), [])

    def test_param_names_cannot_shadow_apis_and_stale_override_is_logged(self):
        invalid_param = [{
            'name': 'windows', 'type': 'string', 'required': False,
            'default': 'x', 'description': 'Bad API shadow.',
        }]
        bad = _entry('shadow-test', 'shadow-test.py', 'value = 1',
                     params=invalid_param)
        with _temporary_registry([bad]):
            with self.assertLogs(code_exec.__name__, level='WARNING'):
                self.assertEqual(code_exec.load_snippet_manifest(), [])

        stale = _entry('stale-test', 'stale-test.py', 'wins = windows()',
                       last_verified='2026-01-01')
        stale['verified_against'] = 'audit-commit-does-not-gate-runtime'
        with _temporary_registry([stale]) as (root, _):
            stale['last_verified'] = '2026-01-01'
            manifest_path = _manifest_path(root)
            manifest_path.write_text(json.dumps({'snippets': [stale]}),
                                     encoding='utf-8')
            backend = FakeBackend()
            refused = code_exec.run_program(
                'run_snippet("stale-test")', backend)
            self.assertFalse(refused['ok'])
            self.assertIn('snippet is stale', refused['error'])
            passed = code_exec.run_program(
                'run_snippet("stale-test", allow_stale=True)', backend)
        self.assertTrue(passed['ok'], passed)
        self.assertTrue(any('stale override' in line for line in passed['log']))

    def test_requires_approval_and_applied_ledger_prevent_a_retry(self):
        source = (
            'wins = windows()\n'
            'obs = observe(window="0xabc")\n'
            'result = act([{"type": "wait", "ms": 0}], obs)\n'
        )
        entry = _entry('approved-test', 'approved-test.py', source,
                       requires_approval=True)
        with _temporary_registry([entry]):
            backend = FakeBackend()
            session = code_exec.CodeExecSession(backend)
            refused = session.run('run_snippet("approved-test")')
            self.assertFalse(refused['ok'])
            self.assertIn('requires approval', refused['error'])
            first = session.run('run_snippet("approved-test")')
            self.assertFalse(first['ok'])
            session.approved_snippets.add('approved-test')
            first = session.run('run_snippet("approved-test")')
            self.assertTrue(first['ok'], first)
            calls_after_first = len(backend.calls)
            retry = session.run('run_snippet("approved-test")')
        self.assertFalse(retry['ok'])
        self.assertIn('already applied', retry['error'])
        self.assertEqual(len(backend.calls), calls_after_first)

    def test_nested_snippets_are_rejected(self):
        parent = _entry('parent-test', 'parent.py',
                        'run_snippet("child-test")')
        child = _entry('child-test', 'child.py', 'wins = windows()')
        with _temporary_registry([parent, child]):
            backend = FakeBackend()
            result = code_exec.run_program(
                'run_snippet("parent-test")', backend)
        self.assertFalse(result['ok'])
        self.assertIn('nested run_snippet is not allowed', result['error'])
        self.assertEqual(backend.calls, [])

    def test_loop_shares_api_and_wall_budgets(self):
        params = [{
            'name': 'iteration', 'type': 'integer', 'required': False,
            'default': 0, 'description': 'Unique iteration key.',
        }]
        entry = _entry('budget-probe', 'budget-probe.py', 'wins = windows()',
                       params=params)
        with _temporary_registry([entry]):
            class SlowBackend(FakeBackend):
                def windows(self):
                    time.sleep(0.2)
                    return super().windows()

            backend = FakeBackend()
            api_result = code_exec.run_program(
                'for index in range(40):\n    run_snippet("budget-probe", iteration=index)',
                backend)
            self.assertFalse(api_result['ok'])
            self.assertIn('API call budget exceeded', api_result['error'])
            self.assertLessEqual(api_result['api_calls'], code_exec.MAX_API_CALLS)

            slow_result = code_exec.run_program(
                'for index in range(40):\n    run_snippet("budget-probe", iteration=index)',
                SlowBackend(), wall_seconds=1)
        self.assertFalse(slow_result['ok'])
        self.assertIn('wall-clock budget exceeded', slow_result['error'])
        self.assertLessEqual(slow_result['api_calls'], code_exec.MAX_API_CALLS)
        self.assertLess(slow_result['elapsed_ms'], 2000)

    def test_observation_bindings_are_scoped_per_snippet(self):
        first = _entry('first-observe', 'first.py',
                       'obs = observe(window="0xabc")')
        second = _entry('second-act', 'second.py',
                        'act([{"type": "wait", "ms": 0}])')
        with _temporary_registry([first, second]):
            backend = FakeBackend()
            result = code_exec.run_program(
                'run_snippet("first-observe")\n'
                'run_snippet("second-act")', backend)
        self.assertFalse(result['ok'])
        self.assertIn('snippet act needs its own fresh observe()', result['error'])
        self.assertFalse(any(call[0] == 'act' for call in backend.calls))


if __name__ == '__main__' and '--refresh-metadata' in os.sys.argv:
    refresh_manifest_after_verification()
