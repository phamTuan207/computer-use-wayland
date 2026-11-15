"""Glass activation policy; every compositor RPC is mocked."""
import hashlib
import importlib.util
import json
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

BAR = {'name': 'hyprbars', 'author': 'Vaxry', 'handle': '55ae075ca090',
       'version': '1.0', 'description': 'Window title bars'}
GLASS = {'name': 'hyprglass', 'author': 'hyprnux', 'handle': 'aabbccddeeff',
         'version': '1.1.1-cu.1', 'description': 'Liquid glass'}
UNKNOWN = {'name': 'other', 'author': 'Other', 'handle': '1234',
           'version': '1', 'description': 'Unknown'}


class Activation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        data = b'fixture library'
        self.library = Path(self.tmp.name) / ('hyprglass-' + hashlib.sha256(data).hexdigest() + '.so')
        self.library.write_bytes(data)
        self.profile = ROOT / 'native/hyprglass-local-optics.lua'
        self.profile_sha256 = hashlib.sha256(self.profile.read_bytes()).hexdigest()
        self.inventory = []
        self.calls = []
        self.version = {'abiHash': 'expected'}
        self.load_answer = 'ok'
        self.reload_answer = 'ok'
        self.config_errors = ''

    def query(self, argv, **kwargs):
        self.calls.append(argv)
        command = argv[1:]
        if command == ['-j', 'version']:
            return json.dumps(self.version)
        if command == ['-j', 'plugin', 'list']:
            return json.dumps(self.inventory)
        if command[:2] == ['plugin', 'load']:
            if self.load_answer == 'ok':
                self.inventory = [*self.inventory, dict(GLASS)]
            return self.load_answer + '\n'
        if command == ['reload']:
            return self.reload_answer + '\n'
        if command == ['configerrors']:
            return self.config_errors
        raise AssertionError('unexpected mocked RPC: ' + repr(argv))

    def activate(self, *, before_load=None, after_reload=None, profile_sha256=None):
        with patch.object(module.subprocess, 'check_output', side_effect=self.query), \
             patch.object(module.activation_checks.indicator, 'liquid_available', return_value=True):
            return module.activate(self.library, 'expected',
                                   profile_sha256 or self.profile_sha256, {},
                                   before_load=before_load, after_reload=after_reload)

    def test_bad_filename_never_queries_compositor(self):
        bad = self.library.with_name('hyprglass.so')
        bad.write_bytes(self.library.read_bytes())
        with patch.object(module.subprocess, 'check_output') as query:
            with self.assertRaisesRegex(RuntimeError, 'immutable SHA256'):
                module.activate(bad, 'expected', self.profile_sha256, {})
            query.assert_not_called()

    def test_wrong_profile_hash_never_queries_or_loads(self):
        with patch.object(module.subprocess, 'check_output') as query:
            with self.assertRaisesRegex(RuntimeError, 'provenance'):
                module.activate(self.library, 'expected', '0' * 64, {})
            query.assert_not_called()

    def test_changed_abi_never_loads(self):
        self.version = {'abiHash': 'different'}
        with patch.object(module.subprocess, 'check_output', side_effect=self.query):
            with self.assertRaisesRegex(RuntimeError, 'ABI changed'):
                module.activate(self.library, 'expected', self.profile_sha256, {})
        self.assertFalse(any(call[1:3] == ['plugin', 'load'] for call in self.calls))

    def test_empty_inventory_and_verified_hyprbars_are_allowed(self):
        for inventory in ([], [dict(BAR)]):
            with self.subTest(inventory=inventory):
                self.inventory = [dict(plugin) for plugin in inventory]
                self.calls.clear()
                self.activate()
                self.assertEqual(sum(call[1:3] == ['plugin', 'load'] for call in self.calls), 1)
                self.assertIn(['hyprctl', 'reload'], self.calls)
                self.assertFalse(any(call[1] == 'eval' for call in self.calls))
                self.assertFalse(any('unload' in call for call in self.calls))

    def test_unknown_duplicate_and_malformed_inventories_refuse(self):
        malformed = {**BAR}
        malformed.pop('description')
        for inventory in ([dict(UNKNOWN)], [dict(BAR), dict(BAR)], [malformed],
                          [{**BAR, 'author': 'someone else'}],
                          [{**BAR, 'version': '2'}], 'not-json-list'):
            with self.subTest(inventory=str(inventory)[:80]):
                self.inventory = inventory
                with patch.object(module.subprocess, 'check_output', side_effect=self.query):
                    with self.assertRaises(RuntimeError):
                        module.activate(self.library, 'expected', self.profile_sha256, {})
                self.assertFalse(any(call[1:3] == ['plugin', 'load'] for call in self.calls))

    def test_inventory_drift_after_login_gate_refuses_first_load(self):
        self.inventory = [dict(BAR)]

        def drift():
            self.inventory[0]['handle'] = 'deadbeef'

        with patch.object(module.subprocess, 'check_output', side_effect=self.query):
            with self.assertRaisesRegex(RuntimeError, 'ownership changed'):
                module.activate(self.library, 'expected', self.profile_sha256, {},
                                 before_load=drift)
        self.assertFalse(any(call[1:3] == ['plugin', 'load'] for call in self.calls))

    def test_fresh_login_gate_is_the_last_check_before_loading(self):
        gate_calls = []

        def gate():
            gate_calls.append(True)
            raise RuntimeError('login is too old')

        with patch.object(module.subprocess, 'check_output', side_effect=self.query):
            with self.assertRaisesRegex(RuntimeError, 'too old'):
                module.activate(self.library, 'expected', self.profile_sha256, {}, before_load=gate)
        self.assertEqual(len(gate_calls), 1)
        self.assertEqual(len(self.calls), 2, 'only ABI and inventory are read before the gate')
        self.assertFalse(any(call[1:3] == ['plugin', 'load'] for call in self.calls))

    def test_refused_load_never_reloads_or_applies_profile(self):
        self.load_answer = 'error'
        with patch.object(module.subprocess, 'check_output', side_effect=self.query):
            with self.assertRaisesRegex(RuntimeError, 'plugin load refused'):
                module.activate(self.library, 'expected', self.profile_sha256, {})
        self.assertFalse(any(call[1:] == ['reload'] for call in self.calls))

    def test_normal_reload_and_ready_status_follow_first_load(self):
        self.inventory = [dict(BAR)]
        self.activate()
        load_at = next(i for i, call in enumerate(self.calls) if call[1:3] == ['plugin', 'load'])
        reload_at = next(i for i, call in enumerate(self.calls) if call[1:] == ['reload'])
        errors_at = next(i for i, call in enumerate(self.calls) if call[1:] == ['configerrors'])
        self.assertLess(load_at, reload_at)
        self.assertLess(reload_at, errors_at)

    def test_after_reload_callback_runs_before_ready_wait(self):
        order = []
        with patch.object(module.activation_checks, 'wait_for_profile',
                          side_effect=lambda env: order.append('ready')):
            self.activate(after_reload=lambda: order.append('overlay'))
        self.assertEqual(order, ['overlay', 'ready'])

    def test_reload_failure_keeps_loaded_plugin_and_never_retries_or_unloads(self):
        self.reload_answer = 'failed'
        with self.assertRaisesRegex(RuntimeError, 'normal config reload refused'):
            self.activate()
        loads = [call for call in self.calls if call[1:3] == ['plugin', 'load']]
        self.assertEqual(len(loads), 1)
        self.assertFalse(any('unload' in call for call in self.calls))
        self.assertEqual(sum(call[1:] == ['reload'] for call in self.calls), 1)

    def test_config_errors_time_out_without_a_second_load(self):
        self.config_errors = 'fixture parse error'
        with patch.object(module.activation_checks.time, 'monotonic', side_effect=[0, 9]), \
             patch.object(module.activation_checks.time, 'sleep'), \
             self.assertRaisesRegex(RuntimeError, 'config reload did not reach'):
            self.activate()
        self.assertEqual(sum(call[1:3] == ['plugin', 'load'] for call in self.calls), 1)
        self.assertFalse(any('unload' in call for call in self.calls))


if __name__ == '__main__':
    unittest.main()
