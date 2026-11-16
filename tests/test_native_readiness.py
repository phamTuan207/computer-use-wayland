"""Broker readiness must accept the published glass identity and keep its gates."""
import json
import socket
import subprocess
import sys
import tempfile
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
    def check(self, plugins, *, version=None, status=None, guard_error=None,
              env={'PATH': '/usr/bin'}):
        def query(_env, *args):
            if args == ('-j', 'version'):
                return VERSION if version is None else version
            if args == ('-j', 'plugin', 'list'):
                return plugins
            raise AssertionError(args)

        guard = patch.object(cursor_theme, 'check_guard', side_effect=guard_error)
        with patch.object(session_remote.cu, '_validate_session_tuple', return_value={}), \
                patch.object(session_remote, '_compositor_identity', return_value=IDENTITY), \
                patch.object(session_remote, '_hypr_json', side_effect=query), \
                patch.object(indicator, '_status', return_value=status), guard:
            return session_remote.native_readiness(env)

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

    def test_missing_env_uses_shared_resolver_and_explicit_env_does_not(self):
        with patch.object(session_remote.cu, 'environment',
                           return_value={'PATH': '/resolved'}) as resolve:
            result = self.check([GLASS, GUARD], status=glass_status(), env=None)
        resolve.assert_called_once_with(refresh=True)
        self.assertEqual(result['instance'], IDENTITY['instance'])

        with patch.object(session_remote.cu, 'environment') as resolve, \
                patch.object(session_remote.cu, '_validate_session_tuple',
                             side_effect=RuntimeError('invalid supplied tuple')):
            with self.assertRaises(session_remote.BrokerError) as caught:
                session_remote.native_readiness({'PATH': '/supplied'})
        resolve.assert_not_called()
        self.assertEqual(caught.exception.stage, 'compositor')
        self.assertEqual(caught.exception.diagnostic, 'gui_environment_unavailable')

    def test_shared_discovery_error_is_bounded_at_compositor_stage(self):
        with patch.object(session_remote.cu, 'environment',
                           side_effect=RuntimeError('private path and environment detail')) as resolve:
            with self.assertRaises(session_remote.BrokerError) as caught:
                session_remote.native_readiness()
        resolve.assert_called_once_with(refresh=True)
        self.assertEqual(caught.exception.stage, 'compositor')
        self.assertEqual(caught.exception.diagnostic, 'gui_environment_unavailable')
        self.assertNotIn('private path', str(caught.exception))

    def test_real_tuple_sockets_and_fake_compositor_responses_pass_readiness(self):
        with tempfile.TemporaryDirectory(prefix='native-readiness-env-') as temporary:
            runtime = Path(temporary) / 'runtime'
            instance_dir = runtime / 'hypr' / 'fixture-instance'
            instance_dir.mkdir(parents=True)
            runtime.chmod(0o700)
            sockets = []
            for path in (runtime / 'wayland-fixture', instance_dir / '.socket.sock',
                         Path(temporary) / 'bus.sock'):
                connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                connection.bind(str(path))
                sockets.append(connection)
            env = {'XDG_RUNTIME_DIR': str(runtime), 'WAYLAND_DISPLAY': 'wayland-fixture',
                   'HYPRLAND_INSTANCE_SIGNATURE': 'fixture-instance',
                   'DBUS_SESSION_BUS_ADDRESS': 'unix:path=' + str(Path(temporary) / 'bus.sock'),
                   'PATH': '/usr/bin:/bin'}
            rows = [{'instance': 'fixture-instance', 'wl_socket': 'wayland-fixture'}]

            def fake_run(argv, **kwargs):
                if argv == ['hyprctl', '-j', 'instances']:
                    value = rows
                elif argv == ['hyprctl', '-j', 'version']:
                    value = VERSION
                elif argv == ['hyprctl', '-j', 'plugin', 'list']:
                    value = [GLASS, GUARD]
                else:
                    raise AssertionError(argv)
                return subprocess.CompletedProcess(argv, 0, json.dumps(value).encode(), b'')

            try:
                with patch.object(session_remote.subprocess, 'run', side_effect=fake_run), \
                        patch.object(indicator, '_status', return_value=glass_status()), \
                        patch.object(cursor_theme, 'check_guard') as guard:
                    result = session_remote.native_readiness(env)
                self.assertEqual(result['instance'], 'fixture-instance')
                self.assertEqual(result['wl_socket'], 'wayland-fixture')
                guard.assert_called_once_with(env)

                rows[0]['wl_socket'] = 'wayland-other'
                with patch.object(session_remote.cu, 'environment') as resolver, \
                        patch.object(session_remote.subprocess, 'run', side_effect=fake_run):
                    with self.assertRaises(session_remote.BrokerError) as caught:
                        session_remote.native_readiness(env)
                resolver.assert_not_called()
                self.assertEqual(caught.exception.stage, 'compositor')
                self.assertEqual(caught.exception.diagnostic, 'gui_environment_unavailable')

                rows[0]['wl_socket'] = 'wayland-fixture'
                runtime.chmod(0o755)
                with patch.object(session_remote.subprocess, 'run', side_effect=fake_run):
                    with self.assertRaises(session_remote.BrokerError) as caught:
                        session_remote.native_readiness(env)
                self.assertEqual(caught.exception.stage, 'compositor')
                self.assertEqual(caught.exception.diagnostic, 'gui_environment_unavailable')
                runtime.chmod(0o700)

                bad_bus = Path(temporary) / 'not-a-socket'
                bad_bus.write_text('fixture')
                with patch.object(session_remote.subprocess, 'run', side_effect=fake_run):
                    with self.assertRaises(session_remote.BrokerError) as caught:
                        session_remote.native_readiness({
                            **env, 'DBUS_SESSION_BUS_ADDRESS': 'unix:path=' + str(bad_bus)})
                self.assertEqual(caught.exception.stage, 'compositor')
                self.assertEqual(caught.exception.diagnostic, 'gui_environment_unavailable')
            finally:
                for connection in sockets:
                    connection.close()

    def test_wrong_abi_refuses_before_plugin_or_guard_probes(self):
        with self.assertRaises(session_remote.BrokerError) as caught:
            self.check([GLASS, GUARD], version={**VERSION, 'abiHash': 'wrong'},
                       status=glass_status())
        self.assertEqual(caught.exception.stage, 'abi')
        self.assertEqual(caught.exception.diagnostic, 'unsupported_compositor_abi')


if __name__ == '__main__':
    unittest.main()
