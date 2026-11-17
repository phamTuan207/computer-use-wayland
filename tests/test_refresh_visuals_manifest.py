"""Manifest refresh policy; every compositor RPC is mocked, all files are fixtures."""
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
spec = importlib.util.spec_from_file_location(
    'refresh_visuals_manifest', ROOT / 'scripts/refresh-visuals-manifest.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

PROFILE_SHA256 = hashlib.sha256(
    (ROOT / 'native/hyprglass-local-optics.lua').read_bytes()).hexdigest()


def _hash_named(directory, prefix, data):
    path = Path(directory) / (prefix + '-' + hashlib.sha256(data).hexdigest() + '.so')
    path.write_bytes(data)
    return path


class RefreshManifest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.installed = base / 'installed'
        plugins = self.installed / 'plugins'
        plugins.mkdir(parents=True)
        self.library = _hash_named(plugins, 'hyprglass', b'new cylindrical glass')
        self.guard = _hash_named(plugins, 'cursor-guard', b'guard')
        self.cursor_dir = base / 'some-dir'
        self.cursor_dir.mkdir()
        self.profile_path = base / 'agent-cursor.json'
        self.profile_path.write_text(json.dumps(
            {'theme': 'TestTheme', 'size': 34,
             'restore_theme': 'default', 'restore_size': 24}))
        self.manifest_path = base / 'visuals.json'
        self.manifest = {
            'version': 1,
            'abi': 'test-abi',
            'library': str(_hash_named(plugins, 'hyprglass', b'old glass')),
            'cursor_guard_library': str(self.guard),
            'profile_sha256': '0' * 64,
            'setup_instance': 'setup-instance-1',
            'cursor_directory': str(self.cursor_dir),
            'cursor_tree_sha256': 'f' * 64,
        }
        self.manifest_path.write_text(json.dumps(self.manifest, indent=2) + '\n')
        self.env = {'HYPRLAND_INSTANCE_SIGNATURE': 'current-instance-9'}
        self.version = {'abiHash': 'test-abi'}

    def _check_output(self, argv, **kwargs):
        if argv == ['hyprctl', '-j', 'version']:
            return json.dumps(self.version)
        raise AssertionError('unexpected mocked RPC: ' + repr(argv))

    def refresh(self, library=None):
        with patch.object(module.subprocess, 'check_output', side_effect=self._check_output), \
             patch.object(module.cursor_theme, 'PROFILE', self.profile_path):
            return module.refresh(
                self.library if library is None else library,
                self.manifest_path, self.installed, self.env)

    def test_refresh_writes_new_library_and_profile_hash(self):
        result = self.refresh()
        self.assertTrue(result['ok'])
        self.assertTrue(result['changed'])
        self.assertEqual(result['library'], str(self.library))
        self.assertEqual(result['profile_sha256'], PROFILE_SHA256)
        updated = json.loads(self.manifest_path.read_text())
        self.assertEqual(updated['library'], str(self.library))
        self.assertEqual(updated['profile_sha256'], PROFILE_SHA256)
        for key in ('version', 'abi', 'setup_instance', 'cursor_guard_library',
                    'cursor_directory', 'cursor_tree_sha256'):
            self.assertEqual(updated[key], self.manifest[key])

    def test_refresh_is_idempotent(self):
        self.refresh()
        result = self.refresh()
        self.assertTrue(result['ok'])
        self.assertFalse(result['changed'])

    def test_refuses_library_with_wrong_hash_name(self):
        bad = Path(self.tmp.name) / 'installed' / 'plugins' / ('hyprglass-' + 'a' * 64 + '.so')
        bad.write_bytes(b'not what the name says')
        with self.assertRaises(RuntimeError):
            self.refresh(library=bad)

    def test_refuses_library_outside_plugins_dir(self):
        outside = _hash_named(Path(self.tmp.name), 'hyprglass', b'elsewhere')
        with self.assertRaises(RuntimeError):
            self.refresh(library=outside)

    def test_refuses_symlinked_library(self):
        link = Path(self.tmp.name) / 'installed' / 'plugins' / ('hyprglass-' + 'b' * 64 + '.so')
        link.symlink_to(self.library)
        with self.assertRaises(RuntimeError):
            self.refresh(library=link)

    def test_refuses_missing_library(self):
        with self.assertRaises(RuntimeError):
            self.refresh(library=self.installed / 'plugins' / 'hyprglass-missing.so')

    def test_refuses_abi_drift(self):
        self.version = {'abiHash': 'different-abi'}
        with self.assertRaises(RuntimeError):
            self.refresh()

    def test_refuses_same_setup_instance(self):
        self.env = {'HYPRLAND_INSTANCE_SIGNATURE': 'setup-instance-1'}
        with self.assertRaises(RuntimeError):
            self.refresh()

    def test_refuses_inside_automation_session(self):
        self.env = {'HYPRLAND_INSTANCE_SIGNATURE': 'current-instance-9',
                    'CU_SESSION_TOKEN': 'token'}
        with self.assertRaises(RuntimeError):
            self.refresh()

    def test_refuses_bad_guard_library(self):
        self.manifest['cursor_guard_library'] = str(
            _hash_named(Path(self.tmp.name), 'cursor-guard', b'wrong place'))
        self.manifest_path.write_text(json.dumps(self.manifest, indent=2) + '\n')
        with self.assertRaises(RuntimeError):
            self.refresh()

    def test_refuses_non_object_manifest(self):
        self.manifest_path.write_text('[1, 2]\n')
        with self.assertRaises(RuntimeError):
            self.refresh()

    def test_refuses_wrong_manifest_version(self):
        self.manifest['version'] = 2
        self.manifest_path.write_text(json.dumps(self.manifest, indent=2) + '\n')
        with self.assertRaises(RuntimeError):
            self.refresh()

    def test_cursor_tree_branch_validates_digest(self):
        digest = 'e' * 64
        cursor_dir = Path(self.tmp.name) / ('cu-agent-' + digest)
        cursor_dir.mkdir()
        self.profile_path.write_text(json.dumps(
            {'theme': 'cu-agent-' + digest, 'size': 34,
             'restore_theme': 'default', 'restore_size': 24}))
        self.manifest['cursor_directory'] = str(cursor_dir)
        self.manifest['cursor_tree_sha256'] = digest
        self.manifest_path.write_text(json.dumps(self.manifest, indent=2) + '\n')
        with patch.object(module.subprocess, 'check_output', side_effect=self._check_output), \
             patch.object(module.cursor_theme, 'PROFILE', self.profile_path), \
             patch.object(module.cursor_theme, 'search_roots',
                          return_value=[Path(self.tmp.name)]), \
             patch.object(module.runpy, 'run_path',
                          return_value={'tree_digest': lambda directory: digest}):
            result = module.refresh(self.library, self.manifest_path,
                                    self.installed, self.env)
        self.assertTrue(result['changed'])

    def test_cursor_tree_branch_refuses_mismatch(self):
        digest = 'e' * 64
        cursor_dir = Path(self.tmp.name) / ('cu-agent-' + digest)
        cursor_dir.mkdir()
        self.profile_path.write_text(json.dumps(
            {'theme': 'cu-agent-' + digest, 'size': 34,
             'restore_theme': 'default', 'restore_size': 24}))
        self.manifest['cursor_directory'] = str(cursor_dir)
        self.manifest['cursor_tree_sha256'] = digest
        self.manifest_path.write_text(json.dumps(self.manifest, indent=2) + '\n')
        with patch.object(module.subprocess, 'check_output', side_effect=self._check_output), \
             patch.object(module.cursor_theme, 'PROFILE', self.profile_path), \
             patch.object(module.cursor_theme, 'search_roots',
                          return_value=[Path(self.tmp.name)]), \
             patch.object(module.runpy, 'run_path',
                          return_value={'tree_digest': lambda directory: 'd' * 64}):
            with self.assertRaises(RuntimeError):
                module.refresh(self.library, self.manifest_path,
                               self.installed, self.env)


if __name__ == '__main__':
    unittest.main()
