"""Activation safety checks, no compositor or live plugin loads."""
import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('activate_glass', ROOT / 'scripts/activate-glass.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Activation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        data = b'fixture library'
        self.library = Path(self.tmp.name) / ('hyprglass-' + hashlib.sha256(data).hexdigest() + '.so')
        self.library.write_bytes(data)

    def test_bad_filename_never_queries_compositor(self):
        bad = self.library.with_name('hyprglass.so')
        bad.write_bytes(b'fixture library')
        with patch.object(module.subprocess, 'check_output') as query:
            with self.assertRaisesRegex(RuntimeError, 'immutable SHA256'):
                module.activate(bad, 'expected', {})
            query.assert_not_called()

    def test_changed_abi_never_loads(self):
        with patch.object(module.subprocess, 'check_output', return_value='{"abiHash":"different"}') as query:
            with self.assertRaisesRegex(RuntimeError, 'ABI changed'):
                module.activate(self.library, 'expected', {})
            self.assertEqual(query.call_count, 1)

    def test_loaded_plugin_never_hot_swaps(self):
        with patch.object(module.subprocess, 'check_output', side_effect=['{"abiHash":"expected"}', '[{}]']) as query:
            with self.assertRaisesRegex(RuntimeError, 'already loaded'):
                module.activate(self.library, 'expected', {})
            self.assertEqual(query.call_count, 2)

    def test_load_and_profile_then_verify(self):
        with patch.object(module.subprocess, 'check_output', side_effect=['{"abiHash":"expected"}', '[]', 'ok\n', 'ok\n']) as query, \
                patch.object(module.indicator, 'liquid_available', return_value=True) as ready:
            module.activate(self.library, 'expected', {})
            self.assertEqual(query.call_args_list[2].args[0][1:3], ['plugin', 'load'])
            self.assertEqual(query.call_args_list[3].args[0][1], 'eval')
            ready.assert_called_once_with({})

    def test_failed_load_never_applies_profile(self):
        with patch.object(module.subprocess, 'check_output', side_effect=['{"abiHash":"expected"}', '[]', 'error']) as query:
            with self.assertRaisesRegex(RuntimeError, 'load refused'):
                module.activate(self.library, 'expected', {})
            self.assertEqual(query.call_count, 3)


if __name__ == '__main__':
    unittest.main()
