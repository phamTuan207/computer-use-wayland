"""E3.2: host environment discovery filters nested shells and stale sockets.

environment() must select the GUI host session (host Quickshell, not a nested
one) and only a LIVE Hyprland signature (the signature's own control socket
exists as a socket). Everything is simulated with fixture /proc trees and real
AF_UNIX socket inodes in a temp dir; no compositor is contacted, no focus or
input changes, no settings touched.
"""
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
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.fixtures = REAL_PATH(tmp.name)
        self.proc = self.fixtures / 'proc'
        self.proc.mkdir()
        self.runtime = self.fixtures / 'runtime'
        (self.runtime / 'hypr').mkdir(parents=True)
        self.pids = {}

    def add_process(self, pid, name, environ=None, cmdline=None):
        folder = self.proc / str(pid)
        folder.mkdir()
        if environ is not None:
            (folder / 'environ').write_bytes(
                '\0'.join(f'{k}={v}' for k, v in environ.items()).encode())
        if cmdline is not None:
            (folder / 'cmdline').write_bytes('\0'.join(cmdline).encode())
        self.pids.setdefault(name, []).append(str(pid))

    def make_socket(self, signature, runtime=None):
        folder = REAL_PATH(runtime or self.runtime, 'hypr', signature)
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / '.socket.sock'
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        listener.bind(str(path))
        listener.close()  # the socket inode remains on disk and stays S_ISSOCK
        return path

    def session_environ(self, signature, runtime=None):
        return {'XDG_RUNTIME_DIR': str(runtime or self.runtime),
                'WAYLAND_DISPLAY': 'wayland-1',
                'HYPRLAND_INSTANCE_SIGNATURE': signature,
                'DISPLAY': ':1',
                'DBUS_SESSION_BUS_ADDRESS': 'unix:path=/fixture/bus',
                'XDG_CURRENT_DESKTOP': 'Hyprland',
                'XDG_SESSION_TYPE': 'wayland',
                'PATH': '/candidate/only/path',
                'CANDIDATE_SECRET': 'must-not-propagate'}

    def run_environment(self):
        def fake_run(argv, capture_output=None, text=None, timeout=None):
            # Only the read-only process scan may ever run in this unit.
            self.assertEqual(argv[:2], ['pgrep', '-x'])
            return types.SimpleNamespace(
                stdout=' '.join(self.pids.get(argv[2], [])), stderr='', returncode=1)

        def fake_path(*parts):
            if parts and parts[0] == '/proc':
                return REAL_PATH(self.proc, *parts[1:])
            return REAL_PATH(*parts)

        with patch.object(cu, 'Path', fake_path), \
                patch.object(cu.subprocess, 'run', side_effect=fake_run):
            return cu.environment()

    def assert_selected(self, env, signature):
        self.assertEqual(env['WAYLAND_DISPLAY'], 'wayland-1')
        self.assertEqual(env['HYPRLAND_INSTANCE_SIGNATURE'], signature)
        self.assertEqual(env['DISPLAY'], ':1')
        self.assertNotEqual(env['PATH'], '/candidate/only/path',
                            'the allowlist never copies PATH or secrets')
        self.assertNotIn('CANDIDATE_SECRET', env)

    def test_nested_quickshell_skipped_host_shell_selected(self):
        # A nested shell shares the host PID namespace: even with a fully live
        # session it must never shadow the host Omarchy shell process.
        nested = dict(self.session_environ('nested1111'))
        self.make_socket('nested1111')
        self.add_process(100, 'quickshell', environ=nested,
                         cmdline=['quickshell', '-c', 'custom-shell'])
        self.make_socket('host22222222')
        self.add_process(101, 'quickshell',
                         environ=self.session_environ('host22222222'),
                         cmdline=['quickshell', '-c', HOST_SHELL_MARKER.decode()])
        self.assert_selected(self.run_environment(), 'host22222222')

    def test_quickshell_without_marker_cmdline_is_skipped_entirely(self):
        self.make_socket('host33333333')
        self.add_process(110, 'quickshell',
                         environ=self.session_environ('host33333333'),
                         cmdline=['quickshell'])
        env = self.run_environment()
        self.assertEqual(env['HYPRLAND_INSTANCE_SIGNATURE'],
                         os.environ.get('HYPRLAND_INSTANCE_SIGNATURE'),
                         'no candidate accepted: the inherited environment stands')

    def test_stale_signature_is_skipped(self):
        # The signature's own control socket is missing: the candidate is stale.
        self.add_process(200, 'Hyprland',
                         environ=self.session_environ('stale00000001'))
        env = self.run_environment()
        self.assertNotEqual(env.get('HYPRLAND_INSTANCE_SIGNATURE'), 'stale00000001')

    def test_socket_path_regular_file_is_not_a_live_session(self):
        stale = REAL_PATH(self.runtime, 'hypr', 'stale00000002')
        stale.mkdir(parents=True)
        (stale / '.socket.sock').write_bytes(b'not a socket')
        self.add_process(210, 'Hyprland',
                         environ=self.session_environ('stale00000002'))
        env = self.run_environment()
        self.assertNotEqual(env.get('HYPRLAND_INSTANCE_SIGNATURE'), 'stale00000002')

    def test_stale_signature_falls_through_to_next_candidate(self):
        self.add_process(300, 'Hyprland',
                         environ=self.session_environ('stale00000003'))
        self.make_socket('live00000004')
        self.add_process(301, 'Hyprland',
                         environ=self.session_environ('live00000004'))
        self.assert_selected(self.run_environment(), 'live00000004')

    def test_non_quickshell_processes_need_no_shell_marker(self):
        self.make_socket('live00000005')
        # kitty/waybar/Hyprland candidates are not filtered by cmdline at all.
        self.add_process(400, 'kitty', environ=self.session_environ('live00000005'),
                         cmdline=['kitty'])
        self.assert_selected(self.run_environment(), 'live00000005')

    def test_unreadable_environ_is_skipped_not_fatal(self):
        # pid 500 has a /proc directory but no readable environ file: the scan
        # skips it (OSError) and accepts the next live candidate instead.
        (self.proc / '500').mkdir()
        self.pids['Hyprland'] = ['500', '501']
        self.make_socket('live00000006')
        self.add_process(501, 'Hyprland',
                         environ=self.session_environ('live00000006'))
        self.assert_selected(self.run_environment(), 'live00000006')

    def test_candidate_without_session_variables_is_skipped(self):
        partial = {'WAYLAND_DISPLAY': 'wayland-1'}  # no signature
        self.add_process(600, 'waybar', environ=partial)
        self.make_socket('live00000007')
        self.add_process(601, 'waybar',
                         environ=self.session_environ('live00000007'))
        self.assert_selected(self.run_environment(), 'live00000007')

    def test_runtime_dir_falls_back_to_inherited_environment(self):
        # A candidate may omit XDG_RUNTIME_DIR; the inherited one is used to
        # locate the control socket before the candidate is accepted.
        environ = self.session_environ('live00000008')
        del environ['XDG_RUNTIME_DIR']
        self.make_socket('live00000008')
        self.add_process(700, 'waybar', environ=environ)
        with patch.dict(os.environ, {'XDG_RUNTIME_DIR': str(self.runtime)}):
            self.assert_selected(self.run_environment(), 'live00000008')


if __name__ == '__main__':
    unittest.main()
