import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('install_glass', Path(__file__).resolve().parents[1] / 'scripts/install-glass.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ImmutableGlassInstall(unittest.TestCase):
    def test_new_version_never_changes_existing_module(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            old = root / 'hyprglass.so'
            old.write_bytes(b'old loaded module')
            source = root / 'built.so'
            source.write_bytes(b'\x7fELFtest version one')
            first = module.install(source, root)
            inode = first.stat().st_ino
            self.assertEqual(module.install(source, root), first)
            self.assertEqual(first.stat().st_ino, inode)
            source.write_bytes(b'\x7fELFtest version two')
            second = module.install(source, root)
            self.assertNotEqual(first, second)
            self.assertEqual(old.read_bytes(), b'old loaded module')
            self.assertEqual(first.read_bytes(), b'\x7fELFtest version one')
            self.assertFalse(list(root.glob('.glass-*')))

    def test_mismatched_existing_hash_path_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'built.so'
            data = b'\x7fELFtest'
            source.write_bytes(data)
            target = root / ('hyprglass-' + hashlib.sha256(data).hexdigest() + '.so')
            target.write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError, 'refusing overwrite'):
                module.install(source, root)
            self.assertEqual(target.read_bytes(), b'corrupt')

    def test_rejects_non_library(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'bad'
            source.write_bytes(b'not ELF')
            with self.assertRaisesRegex(ValueError, 'not an ELF'):
                module.install(source, folder)
