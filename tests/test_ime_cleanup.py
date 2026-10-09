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
import os, sys
from pathlib import Path
state = Path(os.environ['FCITX_STATE'])
log = Path(os.environ['FCITX_LOG'])
if len(sys.argv) == 1:
    print(state.read_text().strip() or '2')
    sys.exit(0)
flag = sys.argv[1]
log.write_text(log.read_text() + flag + '\n')
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
before = signal.getsignal(signal.SIGTERM)
try:
    with cu.literal_keyboard(os.environ.copy(), {enabled}):
        print('handler_installed', signal.getsignal(signal.SIGTERM) is not before)
        {action}
except BaseException as exc:
    print('caught', type(exc).__name__)
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

    def run_driver(self, action, enabled='True', **overrides):
        code = DRIVER.format(enabled=enabled, action=action)
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
        result = self.run_driver('pass', PATH=str(empty))
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
        self.assertIn('handler_restored True', result.stdout)
        self.assertEqual(self.state.read_text().strip(), '1')


if __name__ == '__main__':
    unittest.main()
