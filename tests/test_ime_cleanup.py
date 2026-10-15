"""literal_keyboard IME cleanup under real signals; fake fcitx5-remote, no GUI.

Runs a child python that enters cu.literal_keyboard and injects SIGTERM/SIGHUP or
an exception, then asserts the IME state file was restored and the original
signal handlers were put back.
"""
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CU = ROOT / 'scripts/cu.py'

FAKE_FCITX = r'''#!/usr/bin/env python3
import os, sys, time
from pathlib import Path
state = Path(os.environ['FCITX_STATE'])
log = Path(os.environ['FCITX_LOG'])
event_log = os.environ.get('FCITX_EVENT_LOG')
def event(line):
    if event_log:
        with open(event_log, 'a') as stream:
            stream.write(line + '\n')
if len(sys.argv) == 1:
    mode = os.environ.get('FCITX_HANG_QUERY')
    try:
        logged = log.read_text().split()
    except OSError:
        logged = []
    if mode == 'all' or (mode == 'after-c' and '-c' in logged) \
            or (mode == 'after-o' and '-o' in logged):
        event('query-hang')
        time.sleep(10)
    current = state.read_text().strip() or '2'
    event('query state=' + current)
    print(current)
    sys.exit(0)
flag = sys.argv[1]
log.write_text(log.read_text() + flag + '\n')
event('flag ' + flag)
if flag == os.environ.get('FCITX_MUTATE_THEN_HANG'):
    state.write_text('1' if flag == '-c' else '2')
    event('mutated-then-hang ' + flag)
    time.sleep(10)
if flag == os.environ.get('FCITX_HANG_FLAG'):
    ready = os.environ.get('FCITX_READY_FILE')
    if ready:
        Path(ready).write_text('hanging')
    time.sleep(10)
if flag == os.environ.get('FCITX_FAIL_FLAG'):
    sys.exit(1)
state.write_text('1' if flag == '-c' else '2')
'''

DRIVER = r'''
import importlib.util, os, signal, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location('cu', sys.argv[1])
cu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cu)
cu.fcitx5_running = lambda: {daemon}
before = signal.getsignal(signal.SIGTERM)
try:
    with cu.literal_keyboard(os.environ.copy(), {enabled}):
        print('handler_installed', signal.getsignal(signal.SIGTERM) is not before)
        {action}
except BaseException as exc:
    print('caught', type(exc).__name__)
    print('caught_msg', str(exc))
print('handler_restored', signal.getsignal(signal.SIGTERM) is before)
'''


class ImeCleanup(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        binary = self.folder / 'bin'
        binary.mkdir()
        remote = binary / 'fcitx5-remote'
        remote.write_text(FAKE_FCITX)
        remote.chmod(0o700)
        self.state = self.folder / 'state'
        self.state.write_text('2')
        self.log = self.folder / 'log'
        self.log.write_text('')
        self.base_path = os.environ['PATH']
        self.env = os.environ.copy()
        self.env.update(PATH=str(binary) + os.pathsep + self.base_path,
                        FCITX_STATE=str(self.state), FCITX_LOG=str(self.log))

    def run_driver(self, action, enabled='True', daemon='False', **overrides):
        code = DRIVER.format(enabled=enabled, action=action, daemon=daemon)
        env = dict(self.env, **{k: str(v) for k, v in overrides.items()})
        return subprocess.run([sys.executable, '-c', code, str(CU)], env=env,
                              capture_output=True, text=True, timeout=8)

    def calls(self):
        return self.log.read_text().split()

    def assert_restored(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('handler_restored True', result.stdout)
        self.assertEqual(self.calls(), ['-c', '-o'])
        self.assertEqual(self.state.read_text().strip(), '2')

    def test_sigterm_and_sighup_restore_ime_and_handlers(self):
        for name in ('SIGTERM', 'SIGHUP'):
            with self.subTest(signal=name):
                self.state.write_text('2')
                self.log.write_text('')
                result = self.run_driver(f'os.kill(os.getpid(), signal.{name})')
                self.assertIn('handler_installed True', result.stdout)
                self.assertIn('caught RuntimeError', result.stdout)
                self.assert_restored(result)

    def test_exception_restores_ime_and_handlers(self):
        result = self.run_driver("raise ValueError('boom')")
        self.assertIn('caught ValueError', result.stdout)
        self.assert_restored(result)

    def test_compose_disabled_makes_no_calls(self):
        result = self.run_driver('pass', enabled='False')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('handler_installed False', result.stdout)
        self.assertIn('handler_restored True', result.stdout)
        self.assertEqual(self.calls(), [])
        self.assertEqual(self.state.read_text().strip(), '2')

    def test_missing_remote_yields_without_calls(self):
        empty = self.folder / 'empty'
        empty.mkdir()
        result = self.run_driver('pass', PATH=str(empty), daemon='False')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('handler_installed False', result.stdout)
        self.assertEqual(self.calls(), [])
        self.assertEqual(self.state.read_text().strip(), '2')

    def test_original_custom_handler_is_restored(self):
        code = ("import importlib.util, os, signal, sys\n"
                "from pathlib import Path\n"
                "spec = importlib.util.spec_from_file_location('cu', sys.argv[1])\n"
                "cu = importlib.util.module_from_spec(spec); spec.loader.exec_module(cu)\n"
                "custom = lambda *a: None\n"
                "signal.signal(signal.SIGTERM, custom)\n"
                "try:\n"
                "    with cu.literal_keyboard(os.environ.copy(), True):\n"
                "        os.kill(os.getpid(), signal.SIGTERM)\n"
                "except RuntimeError:\n"
                "    pass\n"
                "print('custom_restored', signal.getsignal(signal.SIGTERM) is custom)\n")
        env = dict(self.env)
        result = subprocess.run([sys.executable, '-c', code, str(CU)], env=env,
                                capture_output=True, text=True, timeout=8)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('custom_restored True', result.stdout)
        self.assertEqual(self.calls(), ['-c', '-o'])
        self.assertEqual(self.state.read_text().strip(), '2')

    def test_inactive_compose_untouched_but_handlers_restored(self):
        self.state.write_text('1')
        self.log.write_text('')
        result = self.run_driver('os.kill(os.getpid(), signal.SIGTERM)')
        self.assertIn('handler_installed True', result.stdout)
        self.assertIn('handler_restored True', result.stdout)
        self.assertEqual(self.calls(), [])
        self.assertEqual(self.state.read_text().strip(), '1')

    def test_handlers_restored_even_if_ime_restore_fails(self):
        result = self.run_driver('os.kill(os.getpid(), signal.SIGTERM)',
                                 FCITX_FAIL_FLAG='-o')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('caught RuntimeError', result.stdout)
        self.assertIn('keyboard input interrupted by signal', result.stdout)
        self.assertIn('handler_restored True', result.stdout)
        self.assertEqual(self.state.read_text().strip(), '1')
        warning = result.stderr.strip().splitlines()
        self.assertEqual(len(warning), 1, 'exactly one warning line')
        self.assertLessEqual(len(warning[0]), 400)
        self.assertIn('IME restoration failed', warning[0])

    def test_daemon_present_without_remote_refuses_before_input(self):
        empty = self.folder / 'empty'
        empty.mkdir()
        result = self.run_driver('pass', PATH=str(empty), daemon='True')
        self.assertIn('caught RuntimeError', result.stdout)
        self.assertIn('requires fcitx5-remote while fcitx5 is running', result.stdout)
        self.assertEqual(self.calls(), [], 'no controller command was sent')
        self.assertEqual(self.state.read_text().strip(), '2')

    def test_hanging_flag_command_still_restores_on_signal(self):
        import signal as signal_module
        import time as time_module
        self.state.write_text('2')
        self.log.write_text('')
        ready = self.folder / 'hang-ready'
        if ready.exists():
            ready.unlink()
        code = DRIVER.format(enabled='True', daemon='False',
                             action='pass')
        env = dict(self.env, FCITX_HANG_FLAG='-c', FCITX_READY_FILE=str(ready))
        proc = subprocess.Popen([sys.executable, '-c', code, str(CU)], env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            # Explicit handshake: signal only after the fake is really hanging.
            # The 8s communicate bound is safety only, never the trigger.
            deadline = time_module.monotonic() + 5
            while not ready.exists() and time_module.monotonic() < deadline:
                time_module.sleep(0.01)
            self.assertTrue(ready.exists(), 'fake controller never reached the hang')
            proc.send_signal(signal_module.SIGTERM)
            out, err = proc.communicate(timeout=8)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.communicate()
        self.assertIn('caught RuntimeError', out)
        self.assertIn('handler_restored True', out)
        # The hanging -c was interrupted, but restore -o still ran once.
        self.assertEqual(self.calls(), ['-c', '-o'])
        self.assertEqual(self.state.read_text().strip(), '2')


    def test_production_timeout_matrix(self):
        # Real fake-controller hangs; the production .5 budget must fire.
        # No injected exceptions, no signal games in these scenarios.
        scenarios = {
            'hang-initial-query': ({'FCITX_HANG_QUERY': 'all'},
                                   False, [], '2'),
            'hang-deactivate-query': ({'FCITX_HANG_QUERY': 'after-c'},
                                      False, ['-c', '-o'], '2'),
            'hang-restore-flag': ({'FCITX_HANG_FLAG': '-o'},
                                  True, ['-c', '-o'], '1'),
            'hang-restore-query': ({'FCITX_HANG_QUERY': 'after-o'},
                                   True, ['-c', '-o'], '2'),
            'mutate-then-hang-c': ({'FCITX_MUTATE_THEN_HANG': '-c'},
                                   False, ['-c', '-o'], '2'),
        }
        for name, (extra, body, calls, final) in scenarios.items():
            with self.subTest(scenario=name):
                self.state.write_text('2')
                self.log.write_text('')
                event_log = self.folder / ('events-' + name)
                if event_log.exists():
                    event_log.unlink()
                marker = self.folder / ('marker-' + name)
                if marker.exists():
                    marker.unlink()
                env = dict(FCITX_EVENT_LOG=str(event_log),
                           MARKER=str(marker), **extra)
                result = self.run_driver(
                    "Path(os.environ['MARKER']).write_text('entered')", **env)
                self.assertIn('caught TimeoutExpired', result.stdout)
                self.assertEqual(marker.exists(), body,
                                 'body entered iff input was reached')
                self.assertEqual(self.calls(), calls)
                self.assertEqual(self.state.read_text().strip(), final)
                self.assertIn('handler_restored True', result.stdout)
                events = event_log.read_text().split()
                if 'FCITX_HANG_QUERY' in extra:
                    self.assertIn('query-hang', events)
                if name == 'mutate-then-hang-c':
                    self.assertIn('mutated-then-hang', events)
                self.assertEqual(calls.count('-o'), 1 if '-o' in calls else 0)
                restores = [c for c in self.calls() if c == '-o']
                if name == 'hang-initial-query':
                    self.assertEqual(restores, [],
                                     'no restore without original/deactivate intent')
                else:
                    self.assertEqual(restores, ['-o'],
                                     'restore exactly once after original 2')

class Fcitx5RunningHelper(unittest.TestCase):
    """N15 helper reads only the process table; unknown states refuse."""

    def load(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('cu_probe', str(CU))
        cu = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cu)
        return cu

    def test_absent_and_present_and_other_uid(self):
        from unittest.mock import patch
        cu = self.load()
        with patch.object(cu.os, 'listdir', return_value=['1', 'self', '42']), \
             patch.object(cu.os, 'stat', return_value=type('S', (), {'st_uid': 1000})()), \
             patch.object(cu.os, 'geteuid', return_value=1000), \
             patch('builtins.open', create=True) as opener:
            opener.return_value.__enter__.return_value.read.return_value = 'other\n'
            self.assertFalse(cu.fcitx5_running())
        with patch.object(cu.os, 'listdir', return_value=['7']), \
             patch.object(cu.os, 'stat', return_value=type('S', (), {'st_uid': 1000})()), \
             patch.object(cu.os, 'geteuid', return_value=1000):
            with patch('builtins.open', create=True) as opener:
                opener.return_value.__enter__.return_value.read.return_value = 'fcitx5\n'
                self.assertTrue(cu.fcitx5_running())
        with patch.object(cu.os, 'listdir', return_value=['7']), \
             patch.object(cu.os, 'stat', return_value=type('S', (), {'st_uid': 999})()), \
             patch.object(cu.os, 'geteuid', return_value=1000):
            with patch('builtins.open', create=True) as opener:
                opener.return_value.__enter__.return_value.read.return_value = 'fcitx5\n'
                self.assertFalse(cu.fcitx5_running(), 'foreign UID must not block')

    def test_empty_or_malformed_own_uid_comm_is_refused_never_absent(self):
        from unittest.mock import patch
        cu = self.load()
        for comm in ('', '   ', 'fcitx\x005', 'fcitx\n5'):
            with self.subTest(comm=repr(comm)):
                with patch.object(cu.os, 'listdir', return_value=['7']), \
                     patch.object(cu.os, 'stat',
                                  return_value=type('S', (), {'st_uid': 1000})()), \
                     patch.object(cu.os, 'geteuid', return_value=1000):
                    with patch('builtins.open', create=True) as opener:
                        opener.return_value.__enter__.return_value.read.return_value = comm
                        with self.assertRaisesRegex(RuntimeError, 'cannot determine'):
                            cu.fcitx5_running()

    def test_disappearing_pid_is_skipped_unknown_state_refuses(self):
        from unittest.mock import patch
        cu = self.load()
        with patch.object(cu.os, 'listdir', return_value=['7']), \
             patch.object(cu.os, 'stat', side_effect=FileNotFoundError()):
            self.assertFalse(cu.fcitx5_running(), 'exited PID is a normal race')
        for failure in (OSError('denied'), PermissionError('denied')):
            with self.subTest(failure=type(failure).__name__), \
                 patch.object(cu.os, 'listdir', return_value=['7']), \
                 patch.object(cu.os, 'stat', side_effect=failure):
                with self.assertRaisesRegex(RuntimeError, 'cannot determine'):
                    cu.fcitx5_running()
        with patch.object(cu.os, 'listdir', side_effect=OSError('no proc')):
            with self.assertRaisesRegex(RuntimeError, 'cannot determine'):
                cu.fcitx5_running()


if __name__ == '__main__':
    unittest.main()
