"""Verified compositor environment discovery using private socket fixtures."""
import json
import os
import pathlib
import socket
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
import cu  # noqa: E402

REAL_PATH = pathlib.Path
HOST_SHELL_MARKER = b'/usr/share/omarchy/shell'


class HostEnvironment(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.fixtures = REAL_PATH(temporary.name)
        self.proc = self.fixtures / 'proc'
        self.proc.mkdir()
        self.runtime = self.fixtures / 'runtime'
        (self.runtime / 'hypr').mkdir(parents=True)
        self.runtime.chmod(0o700)
        self.pids = {}
        self.rows = []
        self.hypr_response = None

    def base(self, **values):
        result = {'HOME': '/home/testuser', 'USER': 'testuser', 'LOGNAME': 'testuser',
                  'PATH': '/usr/bin:/bin', 'XDG_CACHE_HOME': '/tmp/cu-fixture-cache',
                  'PYTHONDONTWRITEBYTECODE': '1'}
        result.update(values)
        return result

    def add_process(self, pid, name, environ=None, cmdline=None):
        folder = self.write_process(pid, environ, cmdline)
        self.pids.setdefault(name, []).append(str(pid))
        return folder

    def write_process(self, pid, environ=None, cmdline=None):
        folder = self.proc / str(pid)
        folder.mkdir()
        if environ is not None:
            raw = '\0'.join(f'{key}={value}' for key, value in environ.items())
            (folder / 'environ').write_bytes(raw.encode('utf-8', 'surrogateescape'))
        if cmdline is not None:
            (folder / 'cmdline').write_bytes('\0'.join(cmdline).encode())
        return folder

    def make_socket(self, path):
        path = REAL_PATH(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.is_socket():
            return path
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        listener.bind(str(path))
        listener.close()
        return path

    def make_instance(self, signature, display='wayland-1', *, runtime=None, pid=None):
        runtime = REAL_PATH(runtime or self.runtime)
        self.make_socket(runtime / display)
        ipc = runtime / 'hypr' / signature / '.socket.sock'
        self.make_socket(ipc)
        self.rows.append({'instance': signature, 'wl_socket': display, 'pid': pid})
        return {'XDG_RUNTIME_DIR': str(runtime), 'WAYLAND_DISPLAY': display,
                'HYPRLAND_INSTANCE_SIGNATURE': signature}

    def session_environ(self, signature='host22222222', display='wayland-1', **changes):
        result = {
            'XDG_RUNTIME_DIR': str(self.runtime),
            'WAYLAND_DISPLAY': display,
            'DISPLAY': ':77',
            'HYPRLAND_INSTANCE_SIGNATURE': signature,
            'DBUS_SESSION_BUS_ADDRESS': 'unix:path=/fixture/bus',
            'XDG_CURRENT_DESKTOP': 'Hyprland',
            'XDG_SESSION_DESKTOP': 'Hyprland',
            'XDG_SESSION_TYPE': 'wayland',
            'XDG_SEAT': 'seat-fixture',
            'XDG_VTNR': '9',
            'USER': 'gui-user',
            'HOME': '/home/testuser',
            'LOGNAME': 'gui-user',
            'PATH': '/donor/bin:/usr/bin',
            'GDK_BACKEND': 'wayland,x11',
            'QT_QPA_PLATFORM': 'wayland;xcb',
            'ELECTRON_OZONE_PLATFORM_HINT': 'wayland',
            'MOZ_ENABLE_WAYLAND': '1',
            'DONOR_SECRET': 'must-not-propagate',
            'CU_SESSION_TOKEN': 'must-not-propagate',
            'XDG_CACHE_HOME': '/donor/cache-must-not-propagate',
        }
        result.update(changes)
        return result

    def install_process_mocks(self):
        def fake_run(argv, env=None, capture_output=None, text=None, timeout=None):
            if argv[:2] == ['pgrep', '-x']:
                pids = self.pids.get(argv[2], [])
                return types.SimpleNamespace(stdout=' '.join(pids), stderr='',
                                             returncode=0 if pids else 1)
            self.assertEqual(argv, ['hyprctl', '-j', 'instances'])
            if isinstance(self.hypr_response, BaseException):
                raise self.hypr_response
            if self.hypr_response is not None:
                return self.hypr_response
            return types.SimpleNamespace(stdout=json.dumps(self.rows), stderr='', returncode=0)

        def fake_path(*parts):
            if parts and parts[0] == '/proc':
                return REAL_PATH(self.proc, *parts[1:])
            return REAL_PATH(*parts)

        return (patch.object(cu, 'Path', fake_path),
                patch.object(cu, '_system_runtime_dir',
                             return_value=self.fixtures / 'no-system-runtime'),
                patch.object(cu.subprocess, 'run', side_effect=fake_run))

    def run_environment(self, base=None, *, refresh=False):
        patches = self.install_process_mocks()
        with patches[0], patches[1], patches[2]:
            return cu.environment(self.base() if base is None else base, refresh=refresh)

    def add_donor(self, pid, name, env, *, cmdline=None):
        if name == 'quickshell' and cmdline is None:
            cmdline = ['quickshell', '-c', HOST_SHELL_MARKER.decode()]
        return self.add_process(pid, name, env, cmdline)

    def assert_selected(self, env, signature, display='wayland-1'):
        self.assertEqual(env['WAYLAND_DISPLAY'], display)
        self.assertEqual(env['HYPRLAND_INSTANCE_SIGNATURE'], signature)
        self.assertEqual(env['DISPLAY'], ':77')
        self.assertNotIn('DONOR_SECRET', env)
        self.assertNotIn('CU_SESSION_TOKEN', env)

    def test_discovery_copies_all_eighteen_allowlisted_values_and_nothing_else(self):
        donor = self.session_environ()
        self.make_instance(donor['HYPRLAND_INSTANCE_SIGNATURE'], donor['WAYLAND_DISPLAY'])
        self.add_donor(101, 'quickshell', donor)
        base = self.base(GTK_IM_MODULE='fcitx', DISPLAY=':old', XDG_SEAT='old-seat')
        original = dict(base)
        found = self.run_environment(base)
        self.assertEqual(cu.SESSION_KEYS, set(donor).intersection(cu.SESSION_KEYS))
        self.assertEqual({key: found[key] for key in cu.SESSION_KEYS},
                         {key: donor[key] for key in cu.SESSION_KEYS})
        self.assertNotIn('GTK_IM_MODULE', found)
        self.assertNotIn('DONOR_SECRET', found)
        self.assertNotIn('CU_SESSION_TOKEN', found)
        self.assertEqual(found['XDG_CACHE_HOME'], original.get('XDG_CACHE_HOME'))
        self.assertEqual(found['PYTHONDONTWRITEBYTECODE'], '1')
        self.assertEqual(base, original)

    def test_copies_donor_path_and_preserves_caller_identity_when_donor_lacks_it(self):
        donor = self.session_environ(PATH='/different/donor/path')
        for key in ('USER', 'HOME', 'LOGNAME'):
            donor.pop(key)
        self.make_instance(donor['HYPRLAND_INSTANCE_SIGNATURE'])
        self.add_donor(110, 'waybar', donor)
        found = self.run_environment()
        self.assertEqual(found['PATH'], '/different/donor/path')
        self.assertEqual((found['USER'], found['HOME'], found['LOGNAME']),
                         ('testuser', '/home/testuser', 'testuser'))

    def test_does_not_invent_missing_display_seat_or_platform_hints(self):
        donor = self.session_environ()
        for key in ('DISPLAY', 'XDG_SEAT', 'XDG_VTNR', 'GDK_BACKEND',
                    'QT_QPA_PLATFORM', 'ELECTRON_OZONE_PLATFORM_HINT',
                    'MOZ_ENABLE_WAYLAND'):
            donor.pop(key)
        self.make_instance(donor['HYPRLAND_INSTANCE_SIGNATURE'])
        self.add_donor(111, 'kitty', donor)
        found = self.run_environment(self.base(DISPLAY=':stale', XDG_SEAT='stale'))
        for key in ('DISPLAY', 'XDG_SEAT', 'XDG_VTNR', 'GDK_BACKEND',
                    'QT_QPA_PLATFORM', 'ELECTRON_OZONE_PLATFORM_HINT',
                    'MOZ_ENABLE_WAYLAND'):
            self.assertNotIn(key, found)

    def test_gtk_from_donor_is_never_transferred(self):
        donor = self.session_environ(GTK_IM_MODULE='fcitx')
        self.make_instance(donor['HYPRLAND_INSTANCE_SIGNATURE'])
        self.add_donor(112, 'waybar', donor)
        found = self.run_environment(self.base())
        self.assertNotIn('GTK_IM_MODULE', found)

    def test_quickshell_wins_and_lower_ranked_same_tuple_only_fills_missing_values(self):
        shell = self.session_environ(DISPLAY=':quickshell', XDG_SESSION_DESKTOP='')
        kitty = self.session_environ(DISPLAY=':kitty', XDG_CURRENT_DESKTOP='Kitty',
                                     XDG_SESSION_DESKTOP='Hyprland-verified')
        self.make_instance(shell['HYPRLAND_INSTANCE_SIGNATURE'])
        self.add_donor(120, 'quickshell', shell)
        self.add_donor(121, 'kitty', kitty)
        found = self.run_environment()
        self.assertEqual(found['DISPLAY'], ':quickshell')
        self.assertEqual(found['XDG_CURRENT_DESKTOP'], 'Hyprland')
        self.assertEqual(found['XDG_SESSION_DESKTOP'], 'Hyprland-verified')

    def test_waybar_then_kitty_are_fallbacks_without_quickshell(self):
        waybar = self.session_environ(DISPLAY=':waybar')
        kitty = self.session_environ(DISPLAY=':kitty')
        self.make_instance(waybar['HYPRLAND_INSTANCE_SIGNATURE'])
        self.add_donor(130, 'waybar', waybar)
        self.add_donor(131, 'kitty', kitty)
        self.assertEqual(self.run_environment()['DISPLAY'], ':waybar')

    def test_nested_quickshell_unreadable_and_exited_donors_are_skipped(self):
        nested = self.session_environ('nested1111')
        self.make_instance(nested['HYPRLAND_INSTANCE_SIGNATURE'])
        self.add_donor(140, 'quickshell', nested,
                       cmdline=['quickshell', '-c', 'custom-shell'])
        (self.proc / '141').mkdir()
        self.pids['waybar'] = ['141', '142']
        good = self.session_environ('host22222222')
        self.make_instance(good['HYPRLAND_INSTANCE_SIGNATURE'])
        self.add_donor(142, 'waybar', good)
        self.assert_selected(self.run_environment(), 'host22222222')

    def test_foreign_uid_donor_is_skipped(self):
        foreign = self.session_environ('foreign1111')
        good = self.session_environ('host22222222')
        self.make_instance(foreign['HYPRLAND_INSTANCE_SIGNATURE'])
        self.make_instance(good['HYPRLAND_INSTANCE_SIGNATURE'])
        self.add_donor(150, 'quickshell', foreign)
        self.add_donor(151, 'waybar', good)
        actual = cu._process_owned
        with patch.object(cu, '_process_owned', side_effect=lambda pid: False if str(pid) == '150' else actual(pid)):
            found = self.run_environment()
        self.assert_selected(found, 'host22222222')

    def test_no_verified_candidate_raises_instead_of_returning_ssh_base(self):
        stale = self.make_instance('supplied-stale')
        self.rows = []
        base = self.base(**stale, DISPLAY=':stale')
        with self.assertRaisesRegex(RuntimeError, 'no verified Hyprland GUI environment found'):
            self.run_environment(base)

    def test_socket_discovery_does_not_require_a_donor_process(self):
        self.make_instance('socket-only-instance', pid=230)
        self.write_process(230)
        found = self.run_environment(self.base(XDG_RUNTIME_DIR=str(self.runtime)))
        self.assertEqual(cu.compositor_identity(found), {
            'runtime_dir': str(self.runtime),
            'wayland_display': 'wayland-1',
            'instance': 'socket-only-instance',
        })

    def test_invalid_donor_socket_json_and_hyprctl_timeout_all_raise(self):
        donor = self.session_environ()
        self.add_donor(160, 'waybar', donor)
        (self.runtime / 'hypr' / donor['HYPRLAND_INSTANCE_SIGNATURE']).mkdir()
        (self.runtime / 'hypr' / donor['HYPRLAND_INSTANCE_SIGNATURE'] / '.socket.sock').write_text('not socket')
        with self.assertRaisesRegex(RuntimeError, 'no verified Hyprland GUI environment found'):
            self.run_environment()
        (self.runtime / 'hypr' / donor['HYPRLAND_INSTANCE_SIGNATURE'] / '.socket.sock').unlink()
        self.make_socket(self.runtime / 'hypr' / donor['HYPRLAND_INSTANCE_SIGNATURE'] / '.socket.sock')
        self.make_socket(self.runtime / donor['WAYLAND_DISPLAY'])
        self.hypr_response = types.SimpleNamespace(stdout='{broken', stderr='', returncode=0)
        with self.assertRaisesRegex(RuntimeError, 'no verified Hyprland GUI environment found'):
            self.run_environment()
        self.hypr_response = __import__('subprocess').TimeoutExpired(['hyprctl'], 3)
        with self.assertRaisesRegex(RuntimeError, 'no verified Hyprland GUI environment found'):
            self.run_environment()

    def test_stale_socket_inode_and_mismatched_instances_row_do_not_win(self):
        stale = self.session_environ('stale-without-ipc')
        self.make_socket(self.runtime / stale['WAYLAND_DISPLAY'])
        (self.runtime / 'hypr' / stale['HYPRLAND_INSTANCE_SIGNATURE']).mkdir()
        self.add_donor(161, 'waybar', stale)
        with self.assertRaisesRegex(RuntimeError, 'no verified Hyprland GUI environment found'):
            self.run_environment()

        donor = self.session_environ('row-mismatch')
        self.make_instance(donor['HYPRLAND_INSTANCE_SIGNATURE'])
        self.rows = [{'instance': 'another-live-instance', 'wl_socket': 'wayland-1', 'pid': 999}]
        self.add_donor(162, 'kitty', donor)
        with self.assertRaisesRegex(RuntimeError, 'no verified Hyprland GUI environment found'):
            self.run_environment()

    def test_mismatched_complete_tuple_discovers_current_instance_and_metadata(self):
        stale = self.session_environ('obsolete-signature')
        current = self.session_environ('current-signature', DISPLAY=':current', PATH='/current/bin')
        self.make_instance('obsolete-signature')
        self.rows = []
        self.make_instance('current-signature', pid=990)
        self.rows[0]['pid'] = 990
        self.add_donor(170, 'waybar', stale)
        self.write_process(990, current)
        supplied = self.base(XDG_RUNTIME_DIR=str(self.runtime), WAYLAND_DISPLAY='wayland-1',
                             HYPRLAND_INSTANCE_SIGNATURE='obsolete-signature')
        found = self.run_environment(supplied)
        self.assertEqual(found['HYPRLAND_INSTANCE_SIGNATURE'], 'current-signature')
        self.assertEqual(found['WAYLAND_DISPLAY'], 'wayland-1')
        self.assertEqual(found['DISPLAY'], ':current')
        self.assertEqual(found['PATH'], '/current/bin')
        self.assertEqual(found['DISPLAY'], ':current')

    def test_stale_recovery_uses_changed_wl_socket_and_rejects_mismatched_donor(self):
        stale = self.session_environ('obsolete-signature', display='wayland-old',
                                     DISPLAY=':wrong', PATH='/wrong/bin')
        current = self.session_environ('current-signature', display='wayland-current',
                                       DISPLAY=':current', PATH='/current/bin')
        self.make_instance('current-signature', 'wayland-current', pid=991)
        self.rows[0]['pid'] = 991
        self.add_donor(171, 'waybar', stale)
        self.write_process(991, current)
        base = self.base(XDG_RUNTIME_DIR=str(self.runtime), WAYLAND_DISPLAY='wayland-old',
                         HYPRLAND_INSTANCE_SIGNATURE='obsolete-signature')
        found = self.run_environment(base, refresh=True)
        self.assertEqual(found['HYPRLAND_INSTANCE_SIGNATURE'], 'current-signature')
        self.assertEqual(found['WAYLAND_DISPLAY'], 'wayland-current')
        self.assertEqual(found['DISPLAY'], ':current')
        self.assertEqual(found['PATH'], '/current/bin')

    def test_stale_donor_metadata_is_not_transplanted_across_display(self):
        stale = self.session_environ('obsolete-signature', display='wayland-other',
                                     DISPLAY=':wrong')
        current = {'XDG_RUNTIME_DIR': str(self.runtime), 'WAYLAND_DISPLAY': 'wayland-current',
                   'HYPRLAND_INSTANCE_SIGNATURE': 'current-signature', 'USER': 'current-user'}
        self.make_instance('current-signature', 'wayland-current', pid=992)
        self.rows[0]['pid'] = 992
        self.add_donor(172, 'waybar', stale)
        self.write_process(992, current)
        found = self.run_environment(self.base(DISPLAY=':old'), refresh=True)
        self.assertEqual(found['HYPRLAND_INSTANCE_SIGNATURE'], 'current-signature')
        self.assertNotIn('DISPLAY', found)
        self.assertEqual(found['USER'], 'current-user')

    def test_multiple_live_instances_refuse_automatic_selection(self):
        one = self.session_environ('instance-one')
        two = self.session_environ('instance-two', display='wayland-2')
        supplied = self.make_instance('supplied-stale')
        self.rows = []
        self.make_instance('instance-one', 'wayland-1')
        self.make_instance('instance-two', 'wayland-2')
        self.add_donor(180, 'waybar', one)
        self.add_donor(181, 'kitty', two)
        with self.assertRaisesRegex(RuntimeError, 'multiple verified compositor instances'):
            self.run_environment(self.base(**supplied))

    def test_leftover_directory_symlink_invalid_name_and_dead_pid_do_not_win(self):
        leftover = self.runtime / 'hypr' / 'leftover999'
        self.make_socket(leftover / '.socket.sock')
        link = self.runtime / 'hypr' / 'linked999'
        link.symlink_to(leftover, target_is_directory=True)
        invalid = self.runtime / 'hypr' / 'invalid@name'
        self.make_socket(invalid / '.socket.sock')
        dead = self.runtime / 'hypr' / 'dead9999'
        self.make_socket(dead / '.socket.sock')
        self.rows = [{'instance': 'leftover999', 'wl_socket': 'wayland-1', 'pid': 9991},
                     {'instance': 'linked999', 'wl_socket': 'wayland-1', 'pid': 9991},
                     {'instance': 'invalid@name', 'wl_socket': 'wayland-1', 'pid': 9991},
                     {'instance': 'dead9999', 'wl_socket': 'wayland-1', 'pid': 9992}]
        with self.assertRaisesRegex(RuntimeError, 'no verified Hyprland GUI environment found'):
            self.run_environment(self.base(XDG_RUNTIME_DIR=str(self.runtime)), refresh=True)

    def test_recovery_requires_matching_instances_row_and_wayland_socket(self):
        self.make_socket(self.runtime / 'hypr' / 'current999' / '.socket.sock')
        self.rows = [{'instance': 'current999', 'wl_socket': 'wayland-missing', 'pid': 993}]
        self.write_process(993, {'XDG_RUNTIME_DIR': str(self.runtime)})
        with self.assertRaisesRegex(RuntimeError, 'no verified Hyprland GUI environment found'):
            self.run_environment(self.base(XDG_RUNTIME_DIR=str(self.runtime)), refresh=True)

    def test_valid_explicit_tuple_enriches_only_same_tuple_and_keeps_platform_override(self):
        tuple_env = self.make_instance('explicit-signature')
        donor = self.session_environ('explicit-signature', DISPLAY=':donor',
                                     QT_QPA_PLATFORM='donor-platform')
        self.add_donor(190, 'kitty', donor)
        base = self.base(**tuple_env, DISPLAY=':explicit', QT_QPA_PLATFORM='caller-platform',
                         GTK_IM_MODULE='fcitx')
        found = self.run_environment(base)
        self.assertEqual(cu._session_tuple(found), tuple_env)
        self.assertEqual(found['DISPLAY'], ':explicit')
        self.assertEqual(found['QT_QPA_PLATFORM'], 'caller-platform')
        self.assertEqual(found['DBUS_SESSION_BUS_ADDRESS'], donor['DBUS_SESSION_BUS_ADDRESS'])
        self.assertNotIn('GTK_IM_MODULE', found)

    def test_valid_explicit_tuple_needs_no_donor_and_refresh_strips_gtk(self):
        tuple_env = self.make_instance('explicit-signature')
        base = self.base(**tuple_env, GTK_IM_MODULE='fcitx')
        found = self.run_environment(base, refresh=True)
        self.assertEqual(cu._session_tuple(found), tuple_env)
        self.assertNotIn('GTK_IM_MODULE', found)

    def test_gtk_is_removed_from_pinned_token_return_without_discovery(self):
        tuple_env = self.make_instance('pinned-signature')
        base = self.base(**tuple_env, CU_SESSION_TOKEN='a' * 32, GTK_IM_MODULE='fcitx')
        def only_validate(argv, **kwargs):
            self.assertEqual(argv, ['hyprctl', '-j', 'instances'])
            return types.SimpleNamespace(stdout=json.dumps([
                {'instance': 'pinned-signature', 'wl_socket': 'wayland-1'}]),
                stderr='', returncode=0)
        with patch.object(cu.subprocess, 'run', side_effect=only_validate):
            found = cu.environment(base, refresh=True)
        self.assertNotIn('GTK_IM_MODULE', found)

    def test_home_change_that_moves_default_state_root_is_refused(self):
        donor = self.session_environ(HOME='/home/demo')
        self.make_instance(donor['HYPRLAND_INSTANCE_SIGNATURE'])
        self.add_donor(200, 'waybar', donor)
        base = {'HOME': str(pathlib.Path.home()), 'USER': 'testuser', 'LOGNAME': 'testuser',
                'PATH': '/usr/bin:/bin'}
        with self.assertRaisesRegex(RuntimeError, 'donated HOME would change the already computed default'):
            self.run_environment(base)


if __name__ == '__main__':
    unittest.main()
