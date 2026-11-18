import importlib.util
import os
import pathlib
import tempfile
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
        return [{'address': '0xabc', 'class': 'kitty', 'title': 'term',
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


def run(source, backend=None, **kwargs):
    backend = backend if backend is not None else FakeBackend()
    return code_exec.run_program(source, backend, **kwargs)


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


if __name__ == '__main__':
    unittest.main()
