"""The lock-holding wrapper: one owner lock across glass + guard activation."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import cursor_session


def _load_wrapper():
    spec = importlib.util.spec_from_file_location(
        'activate_session_backend', ROOT / 'scripts' / 'activate-session-backend.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


wrapper = _load_wrapper()


class WrapperTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.folder = Path(self.tmp.name)
        self.state = self.folder / 'state'
        self.manifest = self.folder / 'visuals.json'
        self.manifest.write_text(json.dumps({
            'library': '/tree/plugins/hyprglass-aaaa.so',
            'cursor_guard_library': '/tree/plugins/cursor-guard-bbbb.so',
            'abi': '11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_aq_0.16',
            'profile_sha256': '9' * 64,
        }))
        self.env = {'PATH': '/usr/bin:/bin'}
        self.calls = []

    def tearDown(self):
        self.tmp.cleanup()

    def _fake(self, name):
        def run(*args):
            locked = False
            try:
                cursor_session.owner_lock()
            except RuntimeError as error:
                locked = 'plugin activation is active' in str(error)
            self.calls.append((name, args, locked))
        return run

    def test_lock_held_across_glass_then_guard_in_order(self):
        with patch.object(cursor_session, 'STATE', self.state), \
                patch.object(wrapper, 'glass_activate', self._fake('glass')), \
                patch.object(wrapper, 'guard_activate', self._fake('guard')), \
                patch.object(wrapper, 'verify', return_value=['a', 'b']):
            names = wrapper.activate(self.manifest, self.env)
        self.assertEqual(names, ['a', 'b'])
        self.assertEqual([call[0] for call in self.calls], ['glass', 'guard'])
        glass_args = self.calls[0][1]
        self.assertEqual(glass_args[0], '/tree/plugins/hyprglass-aaaa.so')
        self.assertEqual(glass_args[1], '11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_aq_0.16')
        self.assertEqual(glass_args[2], '9' * 64)
        guard_args = self.calls[1][1]
        self.assertEqual(guard_args[0], '/tree/plugins/cursor-guard-bbbb.so')
        self.assertEqual(guard_args[1], '11cbc6c577b84ffb1edf4df3fc5b6128c3ae6947_aq_0.16')
        # Both activations ran while the wrapper held the lock.
        self.assertTrue(all(call[2] for call in self.calls),
                        'an activation ran without the owner lock held')

    def test_lock_released_after_activation(self):
        state = patch.object(cursor_session, 'STATE', self.state)
        state.start()
        self.addCleanup(state.stop)
        with patch.object(wrapper, 'glass_activate', self._fake('glass')), \
                patch.object(wrapper, 'guard_activate', self._fake('guard')), \
                patch.object(wrapper, 'verify', return_value=['a']):
            wrapper.activate(self.manifest, self.env)
        lock = cursor_session.owner_lock()
        lock.close()

    def test_glass_failure_skips_guard(self):
        def fail(*args):
            raise RuntimeError('glass refused')
        with patch.object(cursor_session, 'STATE', self.state), \
                patch.object(wrapper, 'glass_activate', fail), \
                patch.object(wrapper, 'guard_activate', self._fake('guard')), \
                patch.object(wrapper, 'verify', return_value=['a']):
            with self.assertRaisesRegex(RuntimeError, 'glass refused'):
                wrapper.activate(self.manifest, self.env)
        self.assertEqual(self.calls, [])


if __name__ == '__main__':
    unittest.main()
