"""Hermetic transaction coverage for sync-installed.py."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / 'scripts/sync-installed.py'
SPEC = importlib.util.spec_from_file_location('sync_installed_tested', SCRIPT)
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)


def put(path, content, mode=0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content if isinstance(content, bytes) else content.encode())
    path.chmod(mode)


class SyncInstalledTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='sync-installed-test-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / 'repo'
        self.installed = self.base / 'data/agent-computer-use'
        self.cache = self.base / 'cache'
        self.fake_bin = self.base / 'fake-bin'
        self.home = self.base / 'home'
        self.repo.mkdir()
        self.fake_bin.mkdir()
        self.home.mkdir()
        self._make_tools()
        self._make_repo()
        self._make_installed()
        self.env = {
            'HOME': str(self.home),
            'XDG_CACHE_HOME': str(self.cache),
            'PATH': str(self.fake_bin) + os.pathsep + '/usr/bin:/bin',
            'PYTHONDONTWRITEBYTECODE': '1',
        }

    def _make_tools(self):
        put(self.fake_bin / 'cc', '#!/usr/bin/python3\nprint("test cc 1.0")\n', 0o755)
        put(self.fake_bin / 'pkg-config',
            '#!/usr/bin/python3\nprint("")\n', 0o755)
        put(self.fake_bin / 'wayland-scanner',
            '#!/usr/bin/python3\nraise SystemExit("fake build must not invoke wayland-scanner")\n', 0o755)

        put(self.fake_bin / 'patch',
            '#!/usr/bin/python3\nraise SystemExit("fake build must not invoke patch")\n', 0o755)

    def _make_repo(self):
        files = {
            'README.md': '# Fake package\n',
            'LICENSE': 'fake license\n',
            'scripts/setup.py': (
                'import indicator\nGLASS_PIN = "03a57c4451b4abee38feda2ffb725f55ecc0f2fd"\n'
                'REQUIRED_HYPRLAND = "0.57.2"\nLIQUID_VERSION = indicator.LIQUID_VERSION\n'),
            'scripts/build-glass.py': (
                'REQUIRED_COMMIT = "03a57c4451b4abee38feda2ffb725f55ecc0f2fd"\n'
                'REQUIRED_HYPRLAND = "0.57.2"\nVERSION = "1.1.1-cu.1"\n'),
            'scripts/indicator.py': "LIQUID_VERSION = '1.1.1-cu.1'\n",
            'scripts/activation_checks.py': '# fake\n',
            'scripts/plugin_inventory.py': '# fake\n',
            'scripts/session_remote.py': '# fake\n',
            'scripts/cursor_session.py': (REPO_ROOT / 'scripts/cursor_session.py').read_text(),
            'scripts/cu.py': '# fake cli\n',
            'native/indicator.c': 'int main(void) { return 0; }\n',
            'native/pointer.xml': '<protocol name="pointer"/>\n',
            'native/keyboard.xml': '<protocol name="keyboard"/>\n',
            'native/hyprglass-local-optics.lua': 'return {}\n',
            'scripts/build.py': (
                'from pathlib import Path\n'
                'root = Path(__file__).resolve().parents[1] / "native"\n'
                'for name, data in (("indicator", b"fake-indicator"), '
                '("pointer", b"fake-pointer"), ("modifiers", b"fake-modifiers"), ("wtype", b"fake-wtype")):\n'
                '    path = root / name\n    path.write_bytes(data)\n    path.chmod(0o755)\n'
                'print("fake local build complete")\n'),
            'native/visuals-login.lua': '-- fixed repo hook path\n',
            'native/require-liquid': b'',
            'native/agent-cursor.json': '{"theme":"Adwaita"}\n',
            'skill/SKILL.md': '# skill\n',
            'skill/references/usage.md': '# usage\n',
            'tests/test_placeholder.py': '# placeholder\n',
            'docs/install.md': '# install\n',
        }
        for name, content in files.items():
            mode = 0o755 if name == 'scripts/build.py' else 0o644
            put(self.repo / name, content, mode)
        profile_hash = hashlib.sha256((self.repo / 'native/hyprglass-local-optics.lua').read_bytes()).hexdigest()
        glass_data = b'fake hyprglass plugin'
        guard_data = b'fake cursor guard plugin'
        glass_hash = hashlib.sha256(glass_data).hexdigest()
        guard_hash = hashlib.sha256(guard_data).hexdigest()
        put(self.installed / 'plugins' / f'hyprglass-{glass_hash}.so', glass_data)
        put(self.installed / 'plugins' / f'cursor-guard-{guard_hash}.so', guard_data)
        manifest = {
            'version': 1,
            'library': str(self.installed / 'plugins' / f'hyprglass-{glass_hash}.so'),
            'cursor_guard_library': str(self.installed / 'plugins' / f'cursor-guard-{guard_hash}.so'),
            'profile_sha256': profile_hash,
        }
        put(self.repo / 'native/visuals.json', json.dumps(manifest) + '\n')
        subprocess.run(['git', '-C', str(self.repo), 'init', '-q'], check=True)
        subprocess.run(['git', '-C', str(self.repo), 'config', 'user.email', 'sync-test@example.invalid'], check=True)
        subprocess.run(['git', '-C', str(self.repo), 'config', 'user.name', 'Sync Test'], check=True)
        subprocess.run(['git', '-C', str(self.repo), 'add', '-A'], check=True)
        subprocess.run(['git', '-C', str(self.repo), 'commit', '-qm', 'fake package'], check=True)

    def _make_installed(self):
        for directory in sync.MANAGED_DIRS:
            put(self.installed / directory / 'old-release.txt', f'old {directory}\n')
        for name, content in {
            'tests/latest-results.json': '{"run":"keep"}\n',
            'tests/test_report_regressions.py': '# cold test\n',
            'tests/test_session_takeover.py': '# cold test\n',
            'docs/automation-cursor-design.md': '# preserve docs\n',
            'docs/browser-worker-performance.md': '# preserve docs\n',
            'docs/indicator-validation.md': '# preserve docs\n',
            'docs/local-optics.md': '# preserve docs\n',
            'docs/performance-report.md': '# preserve docs\n',
            'docs/research-performance.md': '# preserve docs\n',
            'docs/session-startup-report.md': '# preserve docs\n',
            'docs/wayland-optimization.md': '# preserve docs\n',
            'skill/references/validation.md': '# preserve skill reference\n',
            'CREW.md': '# preserve top-level history\n',
            'scripts/indicator.py.bak-20261116-pinfix': '# hand patch\n',
            'native/indicator.bak-20261116': b'old binary backup',
            'native/hyprglass.so': b'stale glass',
            'native/hyprglass-0123456789abcdef.so': b'stale glass hash',
            'native/cursor-guard-0123456789abcdef.so': b'stale cursor hash',
            'native/hyprglass-local-optics.lua.~1~': b'editor backup',
        }.items():
            put(self.installed / name, content)
        for directory in ('backups', 'browser-profile', 'plugins', 'vendor/hyprglass'):
            put(self.installed / directory / 'keep.txt', f'{directory} sentinel\n')

    def _broker_status(self, **changes):
        status = {
            'ok': True,
            'broker_generation': 'a' * 32,
            'loaded_code_sha256': sync._sha256(self.repo / sync.BROKER_SOURCE),
            'state': 'idle',
            'driver': 'idle',
            'guardian': 'idle',
            'active_sequence': None,
            'error': None,
            'recovery': 'none',
            'cancelled': False,
        }
        status.update(changes)
        return status

    def _run(self, args, *, relay_status=None):
        output = io.StringIO()
        errors = io.StringIO()
        relay_status = relay_status or self._broker_status()
        with mock.patch.dict(os.environ, self.env, clear=True):
            with mock.patch.object(sync, '_relay_public_status', return_value=relay_status):
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                    code = sync.main(['--repo', str(self.repo), '--installed', str(self.installed), *args])
        return code, output.getvalue(), errors.getvalue()

    def test_successful_publication_and_read_only_check(self):
        code, output, error = self._run([])
        self.assertEqual(code, 0, error)
        self.assertIn('Installed sync published and verified.', output)
        code, output, error = self._run(['--check'])
        self.assertEqual(code, 0, error)
        self.assertIn('Preserved-history exceptions:', output)
        for name in ('scripts/indicator.py', 'native/indicator.c', 'native/indicator', 'native/wtype'):
            self.assertTrue((self.installed / name).is_file(), name)
        self.assertFalse((self.installed / 'tests/test_report_regressions.py').exists())
        self.assertFalse((self.installed / 'tests/test_session_takeover.py').exists())
        self.assertFalse((self.installed / 'native/hyprglass.so').exists())
        self.assertFalse((self.installed / 'scripts/indicator.py.bak-20261116-pinfix').exists())
        self.assertFalse((self.installed / 'native/indicator.bak-20261116').exists())
        self.assertEqual((self.installed / 'CREW.md').read_text(), '# preserve top-level history\n')
        snapshot = next((self.installed / 'backups').glob('sync-*'))
        for name in (*sync.HAND_PATCH_BACKUPS, *sync.COLD_TESTS):
            self.assertTrue((snapshot / 'trees' / name).is_file(), name)

    def test_runtime_and_history_files_are_preserved(self):
        keep = {
            'backups/keep.txt': 'backups sentinel\n',
            'browser-profile/keep.txt': 'browser-profile sentinel\n',
            'plugins/keep.txt': 'plugins sentinel\n',
            'vendor/hyprglass/keep.txt': 'vendor/hyprglass sentinel\n',
            'tests/latest-results.json': '{"run":"keep"}\n',
            'docs/local-optics.md': '# preserve docs\n',
            'skill/references/validation.md': '# preserve skill reference\n',
        }
        code, _output, error = self._run([])
        self.assertEqual(code, 0, error)
        for name, content in keep.items():
            self.assertEqual((self.installed / name).read_text(), content, name)

    def test_session_snapshot_and_shared_lock_refuse_publication(self):
        state = self.cache / 'agent-computer-use'
        state.mkdir(parents=True)
        (state / 'session.json').write_text('{"retained":true}\n')
        code, _output, error = self._run([])
        self.assertNotEqual(code, 0)
        self.assertIn('retained session record exists', error)
        (state / 'session.json').unlink()

        lock_path = state / 'cursor.lock'
        child_code = (
            'import fcntl,sys; f=open(sys.argv[1],"a"); '
            'fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB); print("locked",flush=True); sys.stdin.read()')
        child_env = dict(self.env)
        process = subprocess.Popen([sys.executable, '-c', child_code, str(lock_path)],
                                   env=child_env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   text=True)
        try:
            self.assertEqual(process.stdout.readline().strip(), 'locked')
            code, _output, error = self._run([])
            self.assertNotEqual(code, 0)
            self.assertIn('another automation session is active', error)
        finally:
            process.terminate()
            process.communicate(timeout=5)

    def test_mid_publish_failure_restores_and_explicit_rollback_is_complete(self):
        real_rename = os.rename
        calls = 0

        def fail_once(source, destination):
            nonlocal calls
            calls += 1
            if calls == 3:
                raise OSError('simulated mid-publication failure')
            return real_rename(source, destination)

        output, errors = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, self.env, clear=True):
            with mock.patch.object(sync, '_relay_public_status', return_value=self._broker_status()):
                with mock.patch.object(sync.os, 'rename', side_effect=fail_once):
                    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
                        code = sync.main(['--repo', str(self.repo), '--installed', str(self.installed)])
        self.assertNotEqual(code, 0)
        self.assertIn('previous release was restored', errors.getvalue())
        self.assertEqual((self.installed / 'scripts/old-release.txt').read_text(), 'old scripts\n')
        snapshots = sorted((self.installed / 'backups').glob('sync-*'))
        self.assertEqual(len(snapshots), 1)
        code, _output, error = self._run(['--rollback', str(snapshots[0])])
        self.assertEqual(code, 0, error)
        for directory in sync.MANAGED_DIRS:
            self.assertEqual((self.installed / directory / 'old-release.txt').read_text(),
                             f'old {directory}\n')

    def test_check_detects_managed_file_tampering(self):
        code, _output, error = self._run([])
        self.assertEqual(code, 0, error)
        put(self.installed / 'scripts/cu.py', '# tampered cli\n')
        code, _output, error = self._run(['--check'])
        self.assertNotEqual(code, 0)
        self.assertIn('managed installed file differs', error)

    def test_relay_restart_required_only_when_loaded_hash_is_stale(self):
        current = self._broker_status()
        with mock.patch.object(sync, '_relay_public_status', return_value=current):
            self.assertFalse(sync._relay_restart_needed(self.repo))

        stale = self._broker_status(loaded_code_sha256='0' * 64)
        with mock.patch.object(sync, '_relay_public_status', return_value=stale):
            self.assertTrue(sync._relay_restart_needed(self.repo))

    def test_relay_restarts_when_stale_and_idle_then_verifies_new_identity(self):
        before = self._broker_status(loaded_code_sha256='0' * 64)
        after = self._broker_status(broker_generation='c' * 32)
        with mock.patch.object(sync, '_relay_public_status', side_effect=[before, after]):
            with mock.patch.object(sync.subprocess, 'run',
                                   return_value=subprocess.CompletedProcess([], 0, '', '')) as run:
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertTrue(sync._restart_relay(self.repo))
        run.assert_called_once()
        self.assertEqual(run.call_args.args[0], [
            'systemctl', '--user', 'restart', 'computer-use-relay.service'])

    def test_busy_stale_relay_warns_and_refuses_sync_before_publication(self):
        busy = self._broker_status(loaded_code_sha256='0' * 64, state='running',
                                   driver='ready', guardian='active', active_sequence=1)
        code, _output, error = self._run([], relay_status=busy)
        self.assertNotEqual(code, 0)
        self.assertIn('WARNING: broker code is stale and the relay is busy', error)
        self.assertIn('broker-loaded code changed while the relay is busy', error)
        self.assertEqual(list((self.installed / 'backups').glob('sync-*')), [])


if __name__ == '__main__':
    unittest.main()
