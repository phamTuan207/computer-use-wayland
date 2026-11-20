import importlib.util
import os
import pathlib
import re
import tempfile
import threading
import time
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'code_exec', ROOT / 'scripts' / 'code_exec.py')
code_exec = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(code_exec)


class FakeBackend:
    """Stand-in for the cu.py brokered primitives; records calls."""

    def __init__(self):
        self.calls = []
        self.meta = {
            'id': 'abcdef012345', 'image': '/tmp/x.png',
            'observation': '/tmp/x.json', 'window': '0xabc',
            'window_bounds': [0, 0, 800, 600], 'image_size': [800, 600],
            'region': [0, 0, 800, 600], 'monitor': 'eDP-2',
            'created': time.time(),
        }

    def windows(self):
        self.calls.append(('windows',))
        return [{'address': '0xabc', 'class': 'kitty', 'title': 'speed-pick1-term',
                 'at': [0, 0], 'size': [800, 600], 'workspace': {'id': 1}}]

    def observe_window(self, address, crop, max_width):
        self.calls.append(('observe_window', address, crop, max_width))
        return dict(self.meta)

    def observe_screen(self, monitor, crop, max_width):
        self.calls.append(('observe_screen', monitor, crop, max_width))
        return dict(self.meta)

    def act(self, meta, actions, observation_path):
        self.calls.append(('act', meta['id'], actions, observation_path))
        return {'ok': True, 'completed': len(actions)}


class FakeDomBackend(FakeBackend):
    """Desktop and DOM stand-ins; never starts Chromium or a broker."""

    def __init__(self, heavy_lines=0, dom_assert_ok=True, dom_act_ok=True):
        super().__init__()
        self.dom_calls = []
        self.snapshot_count = 0
        self.heavy_lines = heavy_lines
        self.dom_assert_ok = dom_assert_ok
        self.dom_act_ok = dom_act_ok

    def dom_start(self):
        self.dom_calls.append(('start',))
        return {'ok': True, 'endpoint': 'http://127.0.0.1:9222',
                'reused': True}

    def windows(self):
        self.calls.append(('windows',))
        return super().windows() + [
            {'address': '0xdef', 'class': 'chromium', 'title': 'about:blank',
             'at': [0, 0], 'size': [800, 600], 'workspace': {'id': 1}}]

    def dom_tabs(self):
        self.dom_calls.append(('tabs',))
        return [{'id': 'tab-1', 'title': 'fixture', 'url': 'file:///fixture'}]

    def _snapshot(self, target):
        self.snapshot_count += 1
        number = self.snapshot_count
        return {
            'snapshot': 'dom-snapshot-%d' % number,
            'title': 'fixture', 'url': 'file:///fixture',
            'elements': [{
                'ref': 'dom-ref-%d' % number,
                'role': 'button', 'name': 'Show result',
            }],
            'truncated': False, 'iframes': 0,
        }

    def dom_observe(self, target, scope, max_elements):
        self.dom_calls.append(('observe', target, scope, max_elements))
        total = 0
        for number in range(self.heavy_lines):
            total += number
        if self.heavy_lines:
            assert total >= 0
        return self._snapshot(target)

    def dom_act(self, target, snapshot, actions, after_scope=None, no_after=False):
        self.dom_calls.append(
            ('act', target, snapshot, actions, after_scope, no_after))
        if not self.dom_act_ok:
            return {'ok': False, 'completed': 0, 'error': 'DOM action refused'}
        if any(action.get('type') == 'assert' for action in actions):
            if not self.dom_assert_ok:
                return {'ok': False, 'completed': 0, 'error': 'DOM assertion mismatch'}
        result = {'ok': True, 'completed': len(actions)}
        if no_after:
            result['after_skipped'] = True
        else:
            result['after'] = self._snapshot(target)
        return result


class FakeSlowDomBackend(FakeDomBackend):
    """Chromium window appears only after N windows() polls (startup race)."""

    def __init__(self, chromium_after_calls=3, **kwargs):
        super().__init__(**kwargs)
        self.chromium_after_calls = chromium_after_calls
        self.windows_calls = 0

    def windows(self):
        self.windows_calls += 1
        if self.windows_calls < self.chromium_after_calls:
            self.calls.append(('windows',))
            return [{'address': '0xabc', 'class': 'kitty',
                     'title': 'speed-pick1-term', 'at': [0, 0],
                     'size': [800, 600], 'workspace': {'id': 1}}]
        return super().windows()


def run(source, backend=None, **kwargs):
    backend = backend if backend is not None else FakeBackend()
    return code_exec.run_program(source, backend, **kwargs)


def template_program(label):
    doc = (ROOT / 'improvements' / 'pick1-program-template.md').read_text()
    marker = '## %s program\n\n%s\n' % (label, chr(96) * 3 + 'python')
    return doc.split(marker, 1)[1].split('\n' + chr(96) * 3, 1)[0] + '\n'


EXPECTED_P4_LINES = (
    'Ý tưởng 1: app nhắc uống nước.',
    'Ý tưởng 2: bot tóm tắt bài giảng.',
    'Ý tưởng 3: web bán đồ secondhand.',
)
EXPECTED_P4_RUNTIME = (
    "printf 'Ý tưởng 1: app nhắc uống nước.\\n"
    "Ý tưởng 2: bot tóm tắt bài giảng.\\n"
    "Ý tưởng 3: web bán đồ secondhand.\\n"
    "' > /tmp/y-tuong.txt && cat /tmp/y-tuong.txt\n"
)


class FakeShellBackend(FakeBackend):
    """Simulate delayed shell command completion for the P3 race."""

    def __init__(self):
        super().__init__()
        self.threads = []

    def observe_window(self, address, crop, max_width):
        time.sleep(0.15)
        return super().observe_window(address, crop, max_width)

    def act(self, meta, actions, observation_path):
        result = super().act(meta, actions, observation_path)
        command = actions[0]['text']
        thread = threading.Thread(target=self._create_directories,
                                  args=(command,))
        self.threads.append(thread)
        thread.start()
        return result

    def _create_directories(self, command):
        time.sleep(0.3)
        paths = command.split('mkdir -p ', 1)[1].split(' && ', 1)[0].split()
        for path in paths:
            pathlib.Path(path).mkdir(parents=True, exist_ok=True)

    def join_shell(self):
        for thread in self.threads:
            thread.join()


class FakeTerminalBackend(FakeBackend):
    """Small shell simulator for the fixed P3 and P4 terminal programs."""

    def __init__(self):
        super().__init__()
        self.actions = []
        self.terminal_output = []
        self.shell_errors = []
        self.observe_count = 0

    def observe_window(self, address, crop, max_width):
        time.sleep(0.15)
        self.observe_count += 1
        meta = super().observe_window(address, crop, max_width)
        meta['id'] = 'fake-observe-%d' % self.observe_count
        meta['created'] = time.time()
        return meta

    def act(self, meta, actions, observation_path):
        result = super().act(meta, actions, observation_path)
        self.actions.extend(actions)
        for action in actions:
            if action.get('type') == 'type':
                self._run_typed_text(action['text'])
        return result

    def _run_typed_text(self, text):
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith('mkdir -p ') and ' && find ' in line:
                mkdir_part, find_part = line.split(' && find ', 1)
                paths = mkdir_part[len('mkdir -p '):].split()
                for path in paths:
                    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
                root = pathlib.Path(find_part.rsplit(' -type d', 1)[0])
                self.terminal_output.extend(
                    str(path) for path in [root] + sorted(root.rglob('*'))
                    if path.is_dir())
                continue
            match = re.fullmatch(r"printf '(.*)' > (\S+) && cat (\S+)", line)
            if match:
                content = match.group(1).replace(r'\n', '\n')
                target = pathlib.Path(match.group(2))
                target.write_bytes(content.encode('utf-8'))
                self.terminal_output.append(
                    pathlib.Path(match.group(3)).read_text(encoding='utf-8'))
                continue
            redirect = re.fullmatch(r'>\s*(\S+)\s*&&\s*cat\s+(\S+)', line)
            if redirect:
                pathlib.Path(redirect.group(1)).write_bytes(b'')
                self.terminal_output.append('')
                continue
            self.shell_errors.append('bash: command not found: ' + line[:80])


class DelayedFileBackend(FakeBackend):
    def __init__(self, path, contents, delay=0.5):
        super().__init__()
        self.path = pathlib.Path(path)
        self.contents = contents
        self.delay = delay
        self.thread = None

    def act(self, meta, actions, observation_path):
        result = super().act(meta, actions, observation_path)
        self.thread = threading.Thread(target=self._write_later)
        self.thread.start()
        return result

    def _write_later(self):
        time.sleep(self.delay)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(self.contents, encoding='utf-8')

    def join_writer(self):
        if self.thread is not None:
            self.thread.join()


class FlagTests(unittest.TestCase):
    def test_flag_defaults_off(self):
        with mock.patch.dict('os.environ', {}, clear=True):
            self.assertFalse(code_exec.is_enabled())

    def test_flag_on_values(self):
        for value in ('1', 'true', 'yes', 'TRUE'):
            with self.subTest(value=value), \
                    mock.patch.dict('os.environ', {'CU_CODE_EXEC': value}):
                self.assertTrue(code_exec.is_enabled())


class SandboxTests(unittest.TestCase):
    def test_import_rejected_with_no_side_effect(self):
        backend = FakeBackend()
        result = run('import os\nos.system("touch /tmp/pwned")', backend)
        self.assertFalse(result['ok'])
        self.assertEqual(result['error_type'], 'sandbox')
        self.assertEqual(backend.calls, [])
        self.assertFalse(pathlib.Path('/tmp/pwned').exists())

    def test_subprocess_and_eval_rejected(self):
        for source in ('subprocess.run(["ls"])', 'eval("1+1")',
                       'open("/etc/passwd").read()',
                       '__import__("os").system("id")',
                       'x = (lambda: 1)()'):
            with self.subTest(source=source):
                result = run(source)
                self.assertFalse(result['ok'], source)
                self.assertEqual(result['error_type'], 'sandbox')

    def test_dunder_attribute_rejected(self):
        result = run('x = "a".__class__')
        self.assertFalse(result['ok'])
        self.assertEqual(result['error_type'], 'sandbox')

    def test_program_size_cap(self):
        result = run('x = 1\n' + '# ' + 'a' * 9000)
        self.assertFalse(result['ok'])

    def test_wall_clock_budget(self):
        result = run('while True:\n    pass', wall_seconds=1)
        self.assertFalse(result['ok'])
        self.assertIn('budget', result['error'])

    def test_api_call_budget(self):
        result = run('for i in range(40):\n    windows()', max_api_calls=5)
        self.assertFalse(result['ok'])
        self.assertIn('budget', result['error'])


class ApiTests(unittest.TestCase):
    def test_happy_path_loops_and_asserts(self):
        source = (
            'wins = windows()\n'
            'assert_state(len(wins) == 1, "one window")\n'
            'obs = observe(window="0xabc")\n'
            'result = act([{"type": "type", "text": "df -h /\\n"}], obs)\n'
            'assert_state(result["ok"], "act failed")\n'
            'text = read_file("/tmp/y-tuong.txt")\n'
            'assert_file_contains("/tmp/y-tuong.txt", "hello")\n'
            'answer = 144 / 150 * 100\n'
        )
        with tempfile.TemporaryDirectory() as folder:
            target = pathlib.Path(folder) / 'y-tuong.txt'
            target.write_text('hello world\n')
            # read_file is restricted to /tmp; point the test file there.
            tmp_target = pathlib.Path('/tmp/code-exec-test-y-tuong.txt')
            tmp_target.write_text('hello world\n')
            try:
                source = source.replace('/tmp/y-tuong.txt',
                                        str(tmp_target))
                backend = FakeBackend()
                result = run(source, backend)
            finally:
                tmp_target.unlink(missing_ok=True)
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['api_calls'], 3)
        self.assertEqual(result['variables']['answer'], 96.0)
        self.assertEqual(backend.calls[1][0], 'observe_window')
        self.assertEqual(backend.calls[2][0], 'act')

    def test_act_without_observe_fails_closed(self):
        result = run('act([{"type": "wait", "ms": 0}])')
        self.assertFalse(result['ok'])

    def test_act_with_forged_observation_fails_closed(self):
        result = run('act([{"type": "wait", "ms": 0}], {"id": "deadbeef0000"})')
        self.assertFalse(result['ok'])
        self.assertIn('not bound', result['error'])

    def test_read_file_restricted_to_tmp(self):
        for path in ('/etc/passwd', 'relative.txt', '/home/james/x.txt',
                     '/tmp/../etc/passwd'):
            with self.subTest(path=path):
                result = run('read_file(%r)' % path)
                self.assertFalse(result['ok'], path)

    def test_read_file_symlink_escape_rejected(self):
        outside = pathlib.Path.home() / 'code-exec-test-secret.txt'
        outside.write_text('secret')
        link = pathlib.Path('/tmp/code-exec-test-link.txt')
        try:
            link.symlink_to(outside)
            result = run('read_file("/tmp/code-exec-test-link.txt")')
        finally:
            link.unlink(missing_ok=True)
            outside.unlink(missing_ok=True)
        self.assertFalse(result['ok'])

    def test_assert_failure_returns_envelope_not_exception(self):
        result = run('assert_state(1 == 2, "one is not two")')
        self.assertFalse(result['ok'])
        self.assertEqual(result['error_type'], 'assert_failed')
        self.assertIn('one is not two', result['error'])

    def test_failed_assert_after_api_calls_keeps_partial_result(self):
        backend = FakeBackend()
        result = run('obs = observe(window="0xabc")\nassert_state(False, "boom")',
                     backend)
        self.assertFalse(result['ok'])
        self.assertEqual(result['api_calls'], 1)
        self.assertEqual(backend.calls[0][0], 'observe_window')

    def test_refusal_dict_returned_not_raised(self):
        class Refusing(FakeBackend):
            def act(self, meta, actions, observation_path):
                return {'ok': False, 'completed': 0, 'error': 'screen changed',
                        'error_code': 'screen_changed'}
        result = run('obs = observe(window="0xabc")\n'
                     'r = act([{"type": "wait", "ms": 0}], obs)\n'
                     'assert_state(r["ok"] is False, "expected refusal")\n'
                     'obs2 = observe(window="0xabc")\n'
                     'assert_state(obs2["id"] == obs["id"], "same id")\n',
                     Refusing())
        self.assertTrue(result['ok'], result)

    def test_state_persists_across_runs(self):
        with tempfile.TemporaryDirectory() as folder:
            backend = FakeBackend()
            first = run('count = 1', backend, state_dir=folder,
                        session_token='a' * 32)
            self.assertTrue(first['ok'], first)
            second = run('count = count + 1\nassert_state(count == 2, "no persist")',
                         backend, state_dir=folder, session_token='a' * 32)
            self.assertTrue(second['ok'], second)
            self.assertEqual(second['variables']['count'], 2)

    def test_cancel_raises_instead_of_envelope(self):
        def cancel():
            raise RuntimeError('cancelled by user')
        with self.assertRaisesRegex(RuntimeError, 'cancelled'):
            run('windows()', check_cancel=cancel)


class DomApiTests(unittest.TestCase):
    def test_dom_start_returns_browser_start_dict(self):
        backend = FakeDomBackend()
        session = code_exec.CodeExecSession(backend)
        result = session.api_dom_start()
        self.assertEqual(result['ok'], True)
        self.assertEqual(backend.dom_calls, [('start',)])

    def test_dom_start_waits_for_chromium_window_to_appear(self):
        backend = FakeSlowDomBackend(chromium_after_calls=3)
        session = code_exec.CodeExecSession(backend)
        result = session.api_dom_start()
        self.assertEqual(result['ok'], True)
        self.assertEqual(backend.windows_calls, 3)
        self.assertEqual(session.api_calls, 1)

    def test_dom_start_raises_when_chromium_window_never_appears(self):
        backend = FakeSlowDomBackend(chromium_after_calls=10 ** 9)
        session = code_exec.CodeExecSession(backend)
        with mock.patch.object(
                code_exec, 'DOM_WINDOW_WAIT_SECONDS', 0.4), mock.patch.object(
                code_exec, 'DOM_WINDOW_POLL_INTERVAL', 0.05):
            with self.assertRaisesRegex(code_exec.CodeExecError,
                                        'did not appear'):
                session.api_dom_start()

    def test_d1_program_looks_up_chromium_right_after_dom_start(self):
        source = (
            'started = dom_start()\n'
            'assert_state(started["ok"], "dom start failed")\n'
            'wins = windows()\n'
            'chrome = [w for w in wins if w["class"] == "chromium"][0]\n'
            'obs = observe(window=chrome["address"])\n'
            'result = act([{"type": "key", "keys": ["ctrl", "l"]}, '
            '{"type": "type", "text": "file:///fixture\\n"}], obs)\n'
            'verify = observe(window=chrome["address"])\n'
            'assert_state(result["ok"], "navigate act failed")\n'
            'tabs = dom_tabs()\n'
            'tab = [t for t in tabs if t["url"] == "file:///fixture"][0]\n'
            'snap = dom_observe(tab["id"])\n'
            'btn = [e for e in snap["elements"] if e["name"] == "Show result"][0]\n'
            'clicked = dom_act(snap, [{"type": "click", "ref": btn["ref"]}])\n'
            'assert_state(clicked["ok"], "dom click failed")\n'
            'after = clicked["after"]\n'
            'dom_assert(after, selector="#result", text="pick4-ok")\n'
            'verify_image = verify["image"]\n'
        )
        backend = FakeSlowDomBackend(chromium_after_calls=3)
        result = run(source, backend)
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['api_calls'], 9)
        # 3 wait polls inside dom_start() plus the program's own windows().
        self.assertEqual(backend.windows_calls, 4)

    def test_dom_observe_binds_snapshot_and_returns_elements(self):
        backend = FakeDomBackend()
        session = code_exec.CodeExecSession(backend)
        snapshot = session.api_dom_observe('tab-1')
        self.assertEqual(snapshot['elements'][0]['name'], 'Show result')
        binding = session.dom_snapshots[snapshot['snapshot']]
        self.assertEqual(binding['target'], 'tab-1')
        self.assertIn('dom-ref-1', binding['refs'])

    def test_dom_act_accepts_bound_ref_and_binds_after_snapshot(self):
        backend = FakeDomBackend()
        session = code_exec.CodeExecSession(backend)
        snapshot = session.api_dom_observe('tab-1')
        result = session.api_dom_act(
            snapshot, [{'type': 'click', 'ref': snapshot['elements'][0]['ref']}])
        self.assertEqual(result['ok'], True)
        after_id = result['after']['snapshot']
        self.assertIn(after_id, session.dom_snapshots)
        self.assertEqual(session.dom_snapshots[after_id]['target'], 'tab-1')
        self.assertEqual(backend.dom_calls[-1][2], snapshot['snapshot'])

    def test_dom_confirm_click_requires_exact_confirmation_fields(self):
        action = {'type': 'confirm_click', 'ref': 'dom-ref-1',
                  'expected_role': 'button', 'expected_name': 'Discard',
                  'expected_text': 'Discard'}
        code_exec._validate_dom_actions([action], {'dom-ref-1'})
        for field in ('expected_role', 'expected_name', 'expected_text'):
            incomplete = dict(action)
            incomplete.pop(field)
            with self.subTest(field=field), self.assertRaisesRegex(
                    code_exec.CodeExecError, 'requires expected_role'):
                code_exec._validate_dom_actions([incomplete], {'dom-ref-1'})
        with self.assertRaisesRegex(code_exec.CodeExecError, 'requires expected_role'):
            code_exec._validate_dom_actions(
                [dict(action, expected_text='x' * 257)], {'dom-ref-1'})

        backend = FakeDomBackend()
        session = code_exec.CodeExecSession(backend)
        snapshot = session.api_dom_observe('tab-1')
        action['ref'] = snapshot['elements'][0]['ref']
        self.assertTrue(session.api_dom_act(snapshot, [action])['ok'])
        self.assertEqual(backend.dom_calls[-1][3][0]['type'], 'confirm_click')

    def test_dom_act_returns_refusal_dict_without_raising(self):
        backend = FakeDomBackend(dom_act_ok=False)
        session = code_exec.CodeExecSession(backend)
        snapshot = session.api_dom_observe('tab-1')
        result = session.api_dom_act(
            snapshot, [{'type': 'click', 'ref': snapshot['elements'][0]['ref']}])
        self.assertEqual(result, {
            'ok': False, 'completed': 0, 'error': 'DOM action refused',
        })

    def test_dom_act_rejects_forged_snapshot(self):
        session = code_exec.CodeExecSession(FakeDomBackend())
        forged = {'snapshot': 'not-bound', 'elements': [{'ref': 'dom-ref-1'}]}
        with self.assertRaisesRegex(code_exec.CodeExecError, 'not bound'):
            session.api_dom_act(forged, [{'type': 'click', 'ref': 'dom-ref-1'}])

    def test_dom_act_rejects_ref_from_another_snapshot(self):
        session = code_exec.CodeExecSession(FakeDomBackend())
        first = session.api_dom_observe('tab-1')
        second = session.api_dom_observe('tab-1')
        other_ref = second['elements'][0]['ref']
        with self.assertRaisesRegex(code_exec.CodeExecError, 'bound snapshot'):
            session.api_dom_act(first, [{'type': 'click', 'ref': other_ref}])

    def test_dom_act_rejects_non_string_ref(self):
        session = code_exec.CodeExecSession(FakeDomBackend())
        snapshot = session.api_dom_observe('tab-1')
        with self.assertRaisesRegex(code_exec.CodeExecError, 'ref must be'):
            session.api_dom_act(snapshot, [{'type': 'click', 'ref': 3}])

    def test_dom_act_rejects_modified_copy_of_a_bound_snapshot(self):
        session = code_exec.CodeExecSession(FakeDomBackend())
        snapshot = session.api_dom_observe('tab-1')
        forged = dict(snapshot)
        forged['title'] = 'changed'
        with self.assertRaisesRegex(code_exec.CodeExecError, 'not the bound'):
            session.api_dom_act(forged, [{'type': 'click', 'ref': 'dom-ref-1'}])

    def test_dom_assert_passes_and_raises_on_mismatch(self):
        backend = FakeDomBackend()
        session = code_exec.CodeExecSession(backend)
        snapshot = session.api_dom_observe('tab-1')
        self.assertTrue(session.api_dom_assert(
            snapshot, selector='#result', text='ready'))
        self.assertTrue(backend.dom_calls[-1][-1])
        backend.dom_assert_ok = False
        with self.assertRaisesRegex(AssertionError, 'DOM assertion mismatch'):
            session.api_dom_assert(
                snapshot, selector='#result', text='missing')

    def test_dom_observe_rejects_bad_scope_and_max_elements(self):
        session = code_exec.CodeExecSession(FakeDomBackend())
        with self.assertRaisesRegex(code_exec.CodeExecError, 'scope'):
            session.api_dom_observe('tab-1', scope=42)
        with self.assertRaisesRegex(code_exec.CodeExecError, 'max_elements'):
            session.api_dom_observe('tab-1', max_elements=81)

    def test_dom_snapshot_older_than_120_seconds_is_rejected(self):
        session = code_exec.CodeExecSession(FakeDomBackend())
        snapshot = session.api_dom_observe('tab-1')
        session.dom_snapshots[snapshot['snapshot']]['created'] = time.time() - 121
        with self.assertRaisesRegex(code_exec.CodeExecError, 'older than 120s'):
            session.api_dom_act(
                snapshot, [{'type': 'click', 'ref': snapshot['elements'][0]['ref']}])

    def test_dom_snapshot_at_100_seconds_is_still_valid(self):
        # 2.8.1: the limit is 120s, not 90s; a snapshot aged 91-119s must work.
        session = code_exec.CodeExecSession(FakeDomBackend())
        snapshot = session.api_dom_observe('tab-1')
        session.dom_snapshots[snapshot['snapshot']]['created'] = time.time() - 100
        session.api_dom_act(
            snapshot, [{'type': 'click', 'ref': snapshot['elements'][0]['ref']}])

    def test_dom_snapshot_binding_persists_across_runs(self):
        backend = FakeDomBackend()
        token = 'b' * 32
        with tempfile.TemporaryDirectory() as folder:
            first = run('snap = dom_observe("tab-1")', backend,
                        state_dir=folder, session_token=token)
            self.assertTrue(first['ok'], first)
            second = run(
                'result = dom_act(snap, [{"type": "click", "ref": snap["elements"][0]["ref"]}])\n'
                'assert_state(result["ok"], "DOM act failed")',
                backend, state_dir=folder, session_token=token)
        self.assertTrue(second['ok'], second)

    def test_multi_step_program_mixes_desktop_and_dom_actions(self):
        source = (
            'wins = windows()\n'
            'obs = observe(window=wins[0]["address"])\n'
            'desktop = act([{"type": "wait", "ms": 0}], obs)\n'
            'verify = observe(window=wins[0]["address"])\n'
            'assert_state(desktop["ok"], "desktop act failed")\n'
            'started = dom_start()\n'
            'tabs = dom_tabs()\n'
            'snap = dom_observe(tabs[0]["id"])\n'
            'clicked = dom_act(snap, [{"type": "click", "ref": snap["elements"][0]["ref"]}])\n'
            'assert_state(clicked["ok"], "DOM act failed")\n'
            'dom_assert(clicked["after"], selector="#result", text="ready")\n'
        )
        backend = FakeDomBackend()
        result = run(source, backend)
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['api_calls'], 9)
        kinds = [call[0] for call in backend.calls]
        self.assertEqual(kinds.count('observe_window'), 2)
        # dom_start() waits on windows() after the verify observe.
        self.assertEqual(kinds[-1], 'windows')
        self.assertEqual(backend.dom_calls[-1][0], 'act')


class TraceBudgetTests(unittest.TestCase):
    def test_heavy_dom_backend_lines_do_not_blow_trace_budget(self):
        result = run('snap = dom_observe("tab-1")',
                     FakeDomBackend(heavy_lines=100000))
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['api_calls'], 1)

    def test_runaway_loop_calling_dom_ops_is_still_caught(self):
        result = run('while True:\n    dom_tabs()',
                     FakeDomBackend(), max_api_calls=5)
        self.assertFalse(result['ok'])
        self.assertEqual(result['error_type'], 'sandbox')
        self.assertIn('API call budget exceeded', result['error'])

    def test_api_implementation_lines_do_not_count(self):
        # One real observe() executes ~190000 lines on a cold interpreter
        # (PIL first import) and ~7000-10000 warm; counting those lines
        # blew the 20000 budget before act() ever ran (Pick 1 round 1).
        # Only the program's own lines may count now.
        class HeavyBackend(FakeBackend):
            def observe_window(self, address, crop, max_width):
                total = 0
                for i in range(50000):
                    total += i * i
                assert total > 0
                return super().observe_window(address, crop, max_width)
        source = (
            'wins = windows()\n'
            'obs = observe(window="0xabc")\n'
            'result = act([{"type": "wait", "ms": 0}], obs)\n'
            'obs2 = observe(window="0xabc")\n'
            'assert_state(result["ok"], "act failed")\n'
        )
        result = run(source, HeavyBackend())
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['api_calls'], 4)

    def test_trace_budget_still_catches_runaway_loop(self):
        result = run('while True:\n    x = 1')
        self.assertFalse(result['ok'])
        self.assertEqual(result['error_type'], 'sandbox')
        self.assertIn('trace step budget exceeded', result['error'])

    def test_trace_budget_counts_program_function_lines(self):
        source = ('def spin():\n'
                  '    n = 0\n'
                  '    while True:\n'
                  '        n += 1\n'
                  'spin()\n')
        result = run(source)
        self.assertFalse(result['ok'])
        self.assertIn('trace step budget exceeded', result['error'])

    def test_large_finite_program_loop_passes_under_budget(self):
        result = run('total = 0\nfor i in range(5000):\n    total += i')
        self.assertTrue(result['ok'], result)
        self.assertEqual(result['variables']['total'], 12497500)


class TestP3TemplateRace(unittest.TestCase):
    def test_old_direct_assert_fails_and_template_observe_passes(self):
        template = template_program('P3')
        old_source = template.replace(
            'verify = observe(window=term["address"])\n', '', 1)
        old_source = old_source.replace(
            'verify_image = verify["image"]\n', '', 1)
        with tempfile.TemporaryDirectory(prefix='code-exec-test-p3-race-') as folder:
            old_root = pathlib.Path(folder) / 'old' / 'hoc-ky-2'
            new_root = pathlib.Path(folder) / 'new' / 'hoc-ky-2'
            old_source = old_source.replace('/tmp/hoc-ky-2', str(old_root))
            new_source = template.replace('/tmp/hoc-ky-2', str(new_root))
            old_backend = FakeShellBackend()
            new_backend = FakeShellBackend()

            def immediate_assert_file_exists(session, path):
                resolved = code_exec._resolve_read_path(path)
                if not resolved.exists():
                    raise AssertionError('file does not exist: ' + path)
                return True

            # Isolate the old template race from the separate new poll guard.
            with mock.patch.object(code_exec.CodeExecSession,
                                   'api_assert_file_exists',
                                   immediate_assert_file_exists):
                old_result = run(old_source, old_backend)
            old_backend.join_shell()
            self.assertFalse(old_result['ok'], old_result)
            self.assertEqual(old_result['error_type'], 'assert_failed')
            self.assertIn('file does not exist:', old_result['error'])

            new_result = run(new_source, new_backend)
            new_backend.join_shell()
            self.assertTrue(new_result['ok'], new_result)
            self.assertEqual(new_result['api_calls'], 4)
            self.assertEqual(new_result['variables']['verify_image'], '/tmp/x.png')
            for name in ('dsa', 'ktvm', 'oop'):
                self.assertTrue((new_root / name).is_dir())


class TestP4VietnameseBytes(unittest.TestCase):
    def test_old_command_fails_and_fixed_template_writes_exact_bytes(self):
        template = template_program('P4')
        old_source = template.replace("printf '", 'printf ', 1)
        old_source = old_source.replace('\\\\n', '\\n')
        old_source = old_source.replace("\\n' > /tmp/y-tuong.txt",
                                        '\\n > /tmp/y-tuong.txt', 1)
        with tempfile.TemporaryDirectory(prefix='code-exec-test-p4-bytes-') as folder:
            target = pathlib.Path(folder) / 'y-tuong.txt'
            old_program = old_source.replace('/tmp/y-tuong.txt', str(target))
            new_program = template.replace('/tmp/y-tuong.txt', str(target))

            old_result = run(old_program, FakeTerminalBackend())
            self.assertFalse(old_result['ok'], old_result)
            self.assertEqual(old_result['error_type'], 'assert_failed')
            self.assertIn('does not contain', old_result['error'])

            backend = FakeTerminalBackend()
            result = run(new_program, backend)
            self.assertTrue(result['ok'], result)
            self.assertEqual(result['api_calls'], 4)
            expected = ('\n'.join(EXPECTED_P4_LINES) + '\n').encode('utf-8')
            self.assertEqual(target.read_bytes(), expected)
            self.assertEqual(backend.terminal_output[-1].encode('utf-8'), expected)

    def test_act_passes_fixed_runtime_text_codepoint_for_codepoint(self):
        class CapturingBackend(FakeBackend):
            def __init__(self):
                super().__init__()
                self.captured = None

            def act(self, meta, actions, observation_path):
                result = super().act(meta, actions, observation_path)
                self.captured = actions[0]['text']
                return result

        source = '\n'.join(template_program('P4').splitlines()[:4]) + '\n'
        backend = CapturingBackend()
        result = run(source, backend)
        self.assertTrue(result['ok'], result)
        self.assertEqual(backend.captured, EXPECTED_P4_RUNTIME)
        self.assertEqual(backend.captured.count(r'\n'), 3)
        self.assertEqual(backend.captured.count('\n'), 1)
        self.assertTrue(backend.captured.endswith('\n'))
        self.assertFalse(backend.captured.endswith('\n\n'))


class TestAssertPoll(unittest.TestCase):
    def test_exists_retries_until_late_file_appears(self):
        with tempfile.TemporaryDirectory(prefix='code-exec-test-assert-late-') as folder:
            path = pathlib.Path(folder) / 'late.txt'
            backend = DelayedFileBackend(path, 'ready\n')
            source = (
                'obs = observe(window="0xabc")\n'
                'result = act([{"type": "wait", "ms": 0}], obs)\n'
                'assert_file_exists(%r)\n' % str(path)
            )
            result = run(source, backend)
            backend.join_writer()
            self.assertTrue(result['ok'], result)

    def test_contains_retries_missing_file_until_late_content_appears(self):
        with tempfile.TemporaryDirectory(prefix='code-exec-test-assert-text-') as folder:
            path = pathlib.Path(folder) / 'late.txt'
            backend = DelayedFileBackend(path, 'needle is ready\n')
            source = (
                'obs = observe(window="0xabc")\n'
                'result = act([{"type": "wait", "ms": 0}], obs)\n'
                'assert_file_contains(%r, "needle")\n' % str(path)
            )
            result = run(source, backend)
            backend.join_writer()
            self.assertTrue(result['ok'], result)

    def test_missing_file_times_out_promptly_with_original_message(self):
        with tempfile.TemporaryDirectory(prefix='code-exec-test-assert-missing-') as folder:
            path = pathlib.Path(folder) / 'never.txt'
            started = time.monotonic()
            result = run('assert_file_exists(%r)' % str(path))
            elapsed = time.monotonic() - started
            self.assertFalse(result['ok'], result)
            self.assertEqual(result['error_type'], 'assert_failed')
            self.assertEqual(result['error'],
                             'assert failed: file does not exist: ' + str(path))
            self.assertLess(elapsed, 5.0)

    def test_missing_content_times_out_with_original_message(self):
        with tempfile.TemporaryDirectory(prefix='code-exec-test-assert-content-') as folder:
            path = pathlib.Path(folder) / 'wrong.txt'
            path.write_text('not the requested text', encoding='utf-8')
            started = time.monotonic()
            result = run('assert_file_contains(%r, "needle")' % str(path))
            elapsed = time.monotonic() - started
            self.assertFalse(result['ok'], result)
            self.assertEqual(result['error_type'], 'assert_failed')
            self.assertEqual(
                result['error'],
                "assert failed: file %s does not contain 'needle'" % str(path))
            self.assertLess(elapsed, 5.0)

    def test_poll_respects_program_wall_budget(self):
        with tempfile.TemporaryDirectory(prefix='code-exec-test-assert-budget-') as folder:
            path = pathlib.Path(folder) / 'never.txt'
            started = time.monotonic()
            result = run('assert_file_exists(%r)' % str(path), wall_seconds=1)
            elapsed = time.monotonic() - started
            self.assertFalse(result['ok'], result)
            self.assertEqual(result['error_type'], 'sandbox')
            self.assertIn('wall-clock budget exceeded', result['error'])
            self.assertLess(elapsed, 1.5)

    def test_already_present_file_does_not_sleep(self):
        with tempfile.TemporaryDirectory(prefix='code-exec-test-assert-ready-') as folder:
            path = pathlib.Path(folder) / 'ready.txt'
            path.write_text('ready', encoding='utf-8')
            with mock.patch.object(code_exec.time, 'sleep',
                                   side_effect=AssertionError('unexpected poll sleep')):
                result = run('assert_file_exists(%r)' % str(path))
            self.assertTrue(result['ok'], result)


class TestTemplateDryRun(unittest.TestCase):
    def test_fixed_p3_and_p4_programs_run_with_mock_terminal(self):
        with tempfile.TemporaryDirectory(prefix='code-exec-test-dry-run-') as folder:
            p3_root = pathlib.Path(folder) / 'p3' / 'hoc-ky-2'
            p3_source = template_program('P3').replace(
                '/tmp/hoc-ky-2', str(p3_root))
            p3 = run(p3_source, FakeTerminalBackend())
            self.assertTrue(p3['ok'], p3)

            p4_path = pathlib.Path(folder) / 'p4' / 'y-tuong.txt'
            p4_path.parent.mkdir(parents=True)
            p4_source = template_program('P4').replace(
                '/tmp/y-tuong.txt', str(p4_path))
            p4 = run(p4_source, FakeTerminalBackend())
            self.assertTrue(p4['ok'], p4)
            expected = ('\n'.join(EXPECTED_P4_LINES) + '\n').encode('utf-8')
            self.assertEqual(p4_path.read_bytes(), expected)
            self.dry_run_envelopes = [
                {key: p3[key] for key in ('ok', 'api_calls', 'elapsed_ms')},
                {key: p4[key] for key in ('ok', 'api_calls', 'elapsed_ms')},
            ]


if __name__ == '__main__':
    unittest.main()
