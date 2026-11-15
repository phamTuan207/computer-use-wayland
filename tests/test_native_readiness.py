"""Broker readiness must accept the published glass identity and keep its gates."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import cursor_theme
import indicator
import session_remote

PIN = session_remote.HYPRLAND_PIN
ABI = PIN + '_aq_0.16_hu_0.14_hg_0.6_hc_0.1_hlg_0.6'
VERSION = {'version': '0.57.2', 'commit': PIN, 'abiHash': ABI}
IDENTITY = {'instance': 'fixture-instance', 'wl_socket': 'wayland-fixture'}
GUARD = {'name': 'computer-use-cursor', 'author': 'computer-use-wayland',
         'handle': '112233445566', 'version': '1.0.0', 'description': 'cursor guard'}
GLASS = {'name': 'hyprglass', 'author': 'Hyprnux', 'handle': 'aabbccddeeff',
         'version': indicator.LIQUID_VERSION, 'description': 'accepted glass'}


def glass_status(shaders='ready'):
    return {'schema': 1, 'version': indicator.LIQUID_VERSION, 'versionCheck': 'match',
            'active': True, 'shaders': shaders,
            'features': {'layers': {'enabled': True, 'active': True, 'reason': None},
                         'windows': {'enabled': False, 'active': False, 'reason': 'disabled'},
                         'subsurfaces': {'enabled': False, 'active': False,
                                         'reason': 'disabled'}}}


class NativeReadinessTests(unittest.TestCase):
    def check(self, plugins, *, version=None, status=None, guard_error=None):
        def query(_env, *args):
            if args == ('-j', 'version'):
                return VERSION if version is None else version
            if args == ('-j', 'plugin', 'list'):
                return plugins
            raise AssertionError(args)

        guard = patch.object(cursor_theme, 'check_guard', side_effect=guard_error)
        with patch.object(session_remote, '_compositor_identity', return_value=IDENTITY), \
                patch.object(session_remote, '_hypr_json', side_effect=query), \
                patch.object(indicator, '_status', return_value=status), guard:
            return session_remote.native_readiness({'PATH': '/usr/bin'})

    def test_published_hyprglass_identity_and_ready_status_are_accepted(self):
        result = self.check([GLASS, GUARD], status=glass_status())
        self.assertEqual(result['instance'], IDENTITY['instance'])
        self.assertEqual(result['commit'], PIN)

    def test_case_mismatched_hyprglass_author_is_diagnosed(self):
        with self.assertRaises(session_remote.BrokerError) as caught:
            self.check([GUARD, {**GLASS, 'author': 'hyprnux'}], status=glass_status())
        self.assertEqual(caught.exception.error, 'native_unavailable')
        self.assertEqual(caught.exception.stage, 'glass')
        self.assertEqual(caught.exception.diagnostic, 'glass_plugin_identity_mismatch')

    def test_missing_or_unready_glass_still_refuses_readiness(self):
        cases = (([GUARD], None, 'glass_plugin_missing'),
                 ([GUARD, GLASS], glass_status('pending'), 'liquid_backend_not_ready'),
                 ([GUARD, GLASS], {'schema': 7}, 'liquid_backend_not_ready'))
        for plugins, status, diagnostic in cases:
            with self.subTest(diagnostic=diagnostic):
                with self.assertRaises(session_remote.BrokerError) as caught:
                    self.check(plugins, status=status)
                self.assertEqual(caught.exception.stage, 'glass')
                self.assertEqual(caught.exception.diagnostic, diagnostic)

    def test_missing_guard_refuses_with_stage_and_diagnostic(self):
        with self.assertRaises(session_remote.BrokerError) as caught:
            self.check([GLASS], status=glass_status())
        self.assertEqual(caught.exception.error, 'native_unavailable')
        self.assertEqual(caught.exception.stage, 'guard')
        self.assertEqual(caught.exception.diagnostic, 'cursor_guard_missing')

    def test_busy_guard_refuses_with_stage(self):
        with self.assertRaises(session_remote.BrokerError) as caught:
            self.check([GLASS, GUARD], status=glass_status(),
                       guard_error=RuntimeError('busy'))
        self.assertEqual(caught.exception.stage, 'guard')
        self.assertEqual(caught.exception.diagnostic, 'cursor_guard_busy_or_unavailable')

    def test_wrong_abi_refuses_before_plugin_or_guard_probes(self):
        with self.assertRaises(session_remote.BrokerError) as caught:
            self.check([GLASS, GUARD], version={**VERSION, 'abiHash': 'wrong'},
                       status=glass_status())
        self.assertEqual(caught.exception.stage, 'abi')
        self.assertEqual(caught.exception.diagnostic, 'unsupported_compositor_abi')


if __name__ == '__main__':
    unittest.main()
