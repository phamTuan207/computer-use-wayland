"""First-load guard activator. Every compositor query is mocked; no GUI or plugin load."""
import contextlib
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
_spec = importlib.util.spec_from_file_location('activate_cursor_guard',
                                               ROOT / 'scripts/activate-cursor-guard.py')
activate_guard = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(activate_guard)
import indicator as real_indicator
import cursor_session as real_session

PIN = 'efb50993780079460b0cbed1363e2166a2de1d9f'
ABI = PIN + '_aq_0.15_hu_0.14_hg_0.5_hc_0.1_hlg_0.6'
VERSION = {'version': '0.56.2', 'commit': PIN, 'abiHash': ABI}
PLUGINS = [{'name': 'hyprglass', 'version': real_indicator.LIQUID_VERSION}]


def sha(data):
    return hashlib.sha256(data).hexdigest()


class ActivateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.library = self.dir / ('cursor-guard-' + sha(b'guard') + '.so')
        self.library.write_bytes(b'guard')
        self.snapshot = self.dir / 'session.json'
        self.env = {'HYPRLAND_INSTANCE_SIGNATURE': 'fresh-login'}
        self.version = dict(VERSION)
        self.plugins = [dict(PLUGINS[0])]
        self.load_answer = 'ok'
        self.calls = []
        query = mock.Mock(side_effect=self._query)
        patcher = mock.patch.object(activate_guard.subprocess, 'check_output', new=query)
        patcher.start()
        self.addCleanup(patcher.stop)
        for name, target in (('liquid_available', mock.Mock(return_value=True)),):
            patcher = mock.patch.object(activate_guard.indicator, name, new=target)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.check = mock.Mock()
        patcher = mock.patch('cursor_theme.check_guard', new=self.check)
        patcher.start()
        self.addCleanup(patcher.stop)
        patcher = mock.patch.object(real_session, 'SNAPSHOT', self.snapshot)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.before_load = mock.Mock()

    def _query(self, argv, **kwargs):
        self.calls.append(argv)
        if argv[:3] == ['hyprctl', '-j', 'version']:
            return json.dumps(self.version)
        if argv[:4] == ['hyprctl', '-j', 'plugin', 'list']:
            return json.dumps(self.plugins)
        if argv[:2] == ['hyprctl', 'plugin']:
            return self.load_answer
        raise AssertionError('unexpected query: ' + ' '.join(argv))

    def activate(self, **overrides):
        kwargs = dict(library=str(self.library), abi=ABI, env=dict(self.env),
                      before_load=self.before_load)
        kwargs.update(overrides)
        return activate_guard.activate(**kwargs)

    def test_success_loads_once_then_confirms_backend(self):
        self.assertTrue(self.activate())
        loads = [c for c in self.calls if c[:2] == ['hyprctl', 'plugin']]
        self.assertEqual(loads, [['hyprctl', 'plugin', 'load', str(self.library)]])
        self.before_load.assert_called_once_with()
        self.check.assert_called_once_with(self.env)
        self.assertLess(self.calls.index(['hyprctl', '-j', 'version']),
                        len(self.calls))

    def test_before_load_runs_before_first_load(self):
        order = []
        self.before_load.side_effect = lambda: order.append('gate')
        real_run = self._query

        def query(argv, **kwargs):
            if argv[:2] == ['hyprctl', 'plugin']:
                order.append('load')
            return real_run(argv, **kwargs)

        with mock.patch.object(activate_guard.subprocess, 'check_output', new=mock.Mock(side_effect=query)):
            self.activate()
        self.assertEqual(order, ['gate', 'load'])

    def test_session_or_token_refuses_before_any_query(self):
        self.snapshot.write_text('{}')
        with self.assertRaisesRegex(RuntimeError, 'session'):
            self.activate()
        self.snapshot.unlink()
        with mock.patch.dict('os.environ', {'CU_SESSION_TOKEN': 't'}):
            with self.assertRaisesRegex(RuntimeError, 'session'):
                self.activate()
        with self.assertRaisesRegex(RuntimeError, 'session'):
            self.activate(env={**self.env, 'CU_SESSION_TOKEN': 't'})
        self.assertEqual(self.calls, [])

    def test_library_must_be_absolute_regular_hash_named(self):
        real = self.dir / 'real.so'
        self.library.rename(real)
        link = self.dir / self.library.name
        link.symlink_to(real)
        for value in (str(link), 'relative.so', str(self.dir / 'missing.so'),
                      str(real)):
            with self.subTest(value=value):
                with self.assertRaises(RuntimeError):
                    self.activate(library=value)
        self.assertEqual(self.calls, [])

    def test_version_mismatch_refuses(self):
        for version in ({**self.version, 'version': '0.56.1'},
                        {**self.version, 'commit': '0' * 40},
                        {**self.version, 'abiHash': 'other'},
                        '[]', '{"version":"0.56.2"}'):
            with self.subTest(version=str(version)[:40]):
                if isinstance(version, dict):
                    self.version = version
                    abi = version.get('abiHash', ABI)
                    self._query_raw = json.dumps(version)
                else:
                    abi = ABI
                    self._query_raw = version
                with mock.patch.object(activate_guard.subprocess, 'check_output',
                                       new=mock.Mock(side_effect=self._raw_query)):
                    with self.assertRaises(RuntimeError):
                        self.activate(abi=abi)
        self.assertNotIn(['hyprctl', 'plugin', 'load', str(self.library)], self.calls)

    def _raw_query(self, argv, **kwargs):
        self.calls.append(argv)
        if argv[:3] == ['hyprctl', '-j', 'version']:
            return self._query_raw
        return self._query(argv, **kwargs)

    def test_abi_prefix_mismatch_refuses(self):
        with self.assertRaisesRegex(RuntimeError, 'pinned'):
            self.activate(abi='deadbeef_aq_0.15')
        self.assertNotIn(['hyprctl', 'plugin', 'load', str(self.library)], self.calls)

    def test_plugin_inventory_must_be_only_accepted_glass(self):
        inventories = ([], [{**self.plugins[0], 'version': 'x'}],
                       [{'name': 'other', 'version': '1'}],
                       self.plugins + [{'name': 'computer-use-cursor', 'version': '1.0.0'}],
                       'not-a-list')
        for inventory in inventories:
            with self.subTest(inventory=str(inventory)[:60]):
                self.plugins = inventory
                with self.assertRaises(RuntimeError):
                    self.activate()
        self.assertNotIn(['hyprctl', 'plugin', 'load', str(self.library)], self.calls)

    def test_missing_liquid_backend_refuses(self):
        activate_guard.indicator.liquid_available.return_value = False
        with self.assertRaisesRegex(RuntimeError, 'glass backend'):
            self.activate()
        self.assertNotIn(['hyprctl', 'plugin', 'load', str(self.library)], self.calls)

    def test_runtime_drift_after_gate_refuses(self):
        seen = {'n': 0}
        real_run = self._query

        def query(argv, **kwargs):
            if argv[:3] == ['hyprctl', '-j', 'version']:
                seen['n'] += 1
                if seen['n'] > 1:
                    return json.dumps({**self.version, 'abiHash': 'moved'})
            return real_run(argv, **kwargs)

        with mock.patch.object(activate_guard.subprocess, 'check_output', new=mock.Mock(side_effect=query)):
            with self.assertRaisesRegex(RuntimeError, 'ownership changed'):
                self.activate()
        self.assertNotIn(['hyprctl', 'plugin', 'load', str(self.library)], self.calls)

    def test_refused_load_and_missing_backend_ack_fail(self):
        self.load_answer = 'no'
        with self.assertRaisesRegex(RuntimeError, 'first-load refused'):
            self.activate()
        self.load_answer = 'ok'
        self.check.side_effect = RuntimeError('no backend ack')
        with self.assertRaisesRegex(RuntimeError, 'no backend ack'):
            self.activate()

    def test_oversized_response_is_refused(self):
        self.version = {**self.version, 'pad': 'x' * 70000}
        with self.assertRaisesRegex(RuntimeError, 'exceeds bounds'):
            self.activate()


class MainTests(unittest.TestCase):
    def test_main_holds_lock_and_reports(self):
        with mock.patch.object(activate_guard, 'activate', return_value=True) as active, \
             mock.patch.object(real_session, 'owner_lock',
                               return_value=contextlib.nullcontext()), \
             mock.patch.dict('sys.modules', {'cu': mock.Mock(
                 environment=mock.Mock(return_value={}))}):
            self.assertEqual(activate_guard.main(['lib', '--abi', 'abi']), 0)
            active.assert_called_once()
        with mock.patch.object(activate_guard, 'activate', side_effect=RuntimeError('nope')), \
             mock.patch.object(real_session, 'owner_lock',
                               return_value=contextlib.nullcontext()), \
             mock.patch.dict('sys.modules', {'cu': mock.Mock(
                 environment=mock.Mock(return_value={}))}):
            self.assertEqual(activate_guard.main(['lib', '--abi', 'abi']), 1)


if __name__ == '__main__':
    unittest.main()
