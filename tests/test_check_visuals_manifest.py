"""Read-only visuals manifest pin checks and the commit hook."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO


ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / 'scripts/check-visuals-manifest.py'
HOOK = ROOT / 'scripts/git-hooks/pre-commit'
spec = importlib.util.spec_from_file_location('check_visuals_manifest', CHECK)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def _sha256(data):
    return hashlib.sha256(data).hexdigest()


class CheckVisualsManifest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.profile = self.base / 'profile.lua'
        self.profile.write_bytes(b'-- optics profile\n')
        self.manifest = self.base / 'visuals.json'
        self.write_manifest(_sha256(self.profile.read_bytes()))

    def write_manifest(self, pin):
        self.manifest.write_text(json.dumps({
            'library': '/installed/plugins/hyprglass-fixture.so',
            'profile_sha256': pin,
        }))

    def run_check(self):
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            result = module.main(['--manifest', str(self.manifest),
                                  '--profile', str(self.profile)])
        return result, stdout.getvalue() + stderr.getvalue()

    def test_match_returns_zero_and_prints_both_hashes(self):
        digest = _sha256(self.profile.read_bytes())
        result, output = self.run_check()
        self.assertEqual(result, 0)
        self.assertIn(f'Lua SHA256: {digest}', output)
        self.assertIn(f'Pinned profile_sha256: {digest}', output)

    def test_stale_pin_fails_with_remediation(self):
        self.write_manifest('0' * 64)
        result, output = self.run_check()
        self.assertEqual(result, 1)
        self.assertIn('python3 scripts/refresh-visuals-manifest.py /installed/plugins/hyprglass-fixture.so',
                      output)
        self.assertIn('python3 scripts/check-visuals-manifest.py', output)
        self.assertIn('python3 scripts/sync-installed.py --check', output)
        self.assertIn('Only then commit.', output)

    def test_missing_manifest_fails(self):
        self.manifest.unlink()
        result, output = self.run_check()
        self.assertEqual(result, 2)
        self.assertIn('error: manifest not found:', output)

    def test_invalid_json_fails(self):
        self.manifest.write_text('{broken\n')
        result, output = self.run_check()
        self.assertEqual(result, 1)
        self.assertIn('error: invalid JSON in manifest', output)

    def test_missing_profile_hash_fails(self):
        self.manifest.write_text(json.dumps({'library': '/some/library.so'}))
        result, output = self.run_check()
        self.assertEqual(result, 1)
        self.assertIn('missing or has empty profile_sha256', output)

    def test_check_never_changes_profile_or_manifest(self):
        paths = (self.profile, self.manifest)

        def snapshot():
            return {path: (path.stat().st_mtime_ns, _sha256(path.read_bytes()))
                    for path in paths}

        before = snapshot()
        self.assertEqual(self.run_check()[0], 0)
        self.assertEqual(snapshot(), before)
        self.write_manifest('f' * 64)
        before = snapshot()
        self.assertEqual(self.run_check()[0], 1)
        self.assertEqual(snapshot(), before)


class PreCommitHook(unittest.TestCase):
    def _repo(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        (root / 'scripts/git-hooks').mkdir(parents=True)
        (root / 'native').mkdir()
        (root / 'nested').mkdir()
        shutil.copy2(CHECK, root / 'scripts/check-visuals-manifest.py')
        shutil.copy2(HOOK, root / 'scripts/git-hooks/pre-commit')
        profile = root / 'native/hyprglass-local-optics.lua'
        profile.write_bytes(b'-- original optics\n')
        manifest = root / 'native/visuals.json'
        manifest.write_text(json.dumps({
            'library': '/installed/plugins/hyprglass-fixture.so',
            'profile_sha256': _sha256(profile.read_bytes()),
        }))
        (root / 'README.md').write_text('fixture\n')
        subprocess.run(['git', 'init', '-q'], cwd=root, check=True)
        subprocess.run(['git', 'config', 'user.name', 'Scratch Test'], cwd=root, check=True)
        subprocess.run(['git', 'config', 'user.email', 'scratch@example.invalid'],
                       cwd=root, check=True)
        subprocess.run(['git', 'add', '.'], cwd=root, check=True)
        subprocess.run(['git', 'commit', '-qm', 'fixture'], cwd=root, check=True)
        return root, profile, manifest

    def _run_hook(self, root):
        return subprocess.run([str(root / 'scripts/git-hooks/pre-commit')],
                              cwd=root / 'nested', text=True,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def test_staged_lua_with_stale_manifest_blocks_commit(self):
        root, profile, _manifest = self._repo()
        profile.write_bytes(b'-- changed optics\n')
        subprocess.run(['git', 'add', 'native/hyprglass-local-optics.lua'],
                       cwd=root, check=True)
        result = self._run_hook(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Lua SHA256:', result.stdout)
        self.assertIn('python3 scripts/refresh-visuals-manifest.py', result.stdout)

    def test_staged_lua_with_fresh_manifest_passes(self):
        root, profile, manifest = self._repo()
        profile.write_bytes(b'-- changed optics\n')
        data = json.loads(manifest.read_text())
        data['profile_sha256'] = _sha256(profile.read_bytes())
        manifest.write_text(json.dumps(data))
        subprocess.run(['git', 'add', 'native/hyprglass-local-optics.lua'],
                       cwd=root, check=True)
        result = self._run_hook(root)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_staged_lua_without_manifest_warns_and_passes(self):
        root, profile, manifest = self._repo()
        profile.write_bytes(b'-- changed optics\n')
        subprocess.run(['git', 'add', 'native/hyprglass-local-optics.lua'],
                       cwd=root, check=True)
        manifest.unlink()
        result = self._run_hook(root)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('visuals manifest not present (setup has not run); skipping pin check',
                      result.stdout)

    def test_unstaged_lua_with_stale_manifest_does_not_block(self):
        root, _profile, manifest = self._repo()
        data = json.loads(manifest.read_text())
        data['profile_sha256'] = '0' * 64
        manifest.write_text(json.dumps(data))
        (root / 'README.md').write_text('unrelated staged change\n')
        subprocess.run(['git', 'add', 'README.md'], cwd=root, check=True)
        result = self._run_hook(root)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(result.stdout, '')


if __name__ == '__main__':
    unittest.main()
