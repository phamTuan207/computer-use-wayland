"""Cursor-guard backend build: pinned headers first, mocked compiler, no real build."""
import hashlib
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
_spec = importlib.util.spec_from_file_location('build_cursor_guard', ROOT / 'scripts/build-cursor-guard.py')
module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(module)
import setup as real_setup


def pkg_ok(argv, **kwargs):
    if argv[:2] == ['pkg-config', '--modversion']:
        return subprocess.CompletedProcess(argv, 0, '0.56.2\n', '')
    if argv[:2] == ['pkg-config', '--cflags']:
        return subprocess.CompletedProcess(argv, 0, '-I/usr/include/hyprland\n', '')
    if argv and argv[0] == 'g++':
        # A real compiler drops one fresh ELF at the -o target; mirror that.
        target = argv[argv.index('-o') + 1]
        Path(target).write_bytes(b'\x7fELFfake-guard')
        return subprocess.CompletedProcess(argv, 0, '', '')
    return subprocess.CompletedProcess(argv, 0, '', '')


class BuildTests(unittest.TestCase):
    def _patched(self, output):
        run = mock.Mock(side_effect=pkg_ok)
        stack = mock.patch.object(module.subprocess, 'run', new=run)
        stack.start()
        self.addCleanup(stack.stop)
        abi = mock.patch.object(real_setup, 'header_abi',
                                return_value='efb50993780079460b0cbed1363e2166a2de1d9f_aq_0.15_hu_0.14_hg_0.5_hc_0.1_hlg_0.6')
        abi.start()
        self.addCleanup(abi.stop)
        out = mock.patch.object(module, 'OUTPUT', output)
        out.start()
        self.addCleanup(out.stop)
        return run

    def test_build_checks_version_abi_then_compiles(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'cursor-guard.so'
            run = self._patched(output)
            result = module.build({})
            self.assertEqual(result, output)
            self.assertEqual(output.read_bytes(), b'\x7fELFfake-guard')
            argv = [call.args[0] for call in run.call_args_list]
            self.assertEqual(argv[0][:3], ['pkg-config', '--modversion', 'hyprland'])
            compile_argv = argv[-1]
            self.assertEqual(compile_argv[:7], ['g++', '-std=c++26', '-shared', '-fPIC', '-O2', '-Wall', '-Wextra'])
            self.assertIn('-I/usr/include/hyprland', compile_argv)
            self.assertIn('-o', compile_argv)
            self.assertIn(str(module.SOURCE), compile_argv)
            self.assertEqual(compile_argv[-1], '-lXcursor')

    def test_wrong_hyprland_version_refuses_before_compiler(self):
        def pkg(argv, **kwargs):
            if argv[:2] == ['pkg-config', '--modversion']:
                return subprocess.CompletedProcess(argv, 0, '0.57.0\n', '')
            return pkg_ok(argv, **kwargs)
        run = mock.Mock(side_effect=pkg)
        with mock.patch.object(module.subprocess, 'run', new=run), \
             mock.patch.object(real_setup, 'header_abi') as abi, \
             tempfile.TemporaryDirectory() as tmp, \
             mock.patch.object(module, 'OUTPUT', Path(tmp) / 'cursor-guard.so'):
            with self.assertRaises(SystemExit):
                module.build({})
            abi.assert_not_called()
        invoked = [c.args[0][0] for c in run.call_args_list]
        self.assertNotIn('g++', invoked)

    def test_unpinned_headers_refuse_before_compiler(self):
        run = mock.Mock(side_effect=pkg_ok)
        with mock.patch.object(module.subprocess, 'run', new=run), \
             mock.patch.object(real_setup, 'header_abi', return_value='deadbeef_aq_0.15'), \
             tempfile.TemporaryDirectory() as tmp, \
             mock.patch.object(module, 'OUTPUT', Path(tmp) / 'cursor-guard.so'):
            with self.assertRaises(SystemExit):
                module.build({})
        invoked = [c.args[0][0] for c in run.call_args_list]
        self.assertNotIn('g++', invoked)

    def test_failed_compile_preserves_existing_output(self):
        def pkg(argv, **kwargs):
            if argv and argv[0] == 'g++':
                return subprocess.CompletedProcess(argv, 1, '', 'error: bad')
            return pkg_ok(argv, **kwargs)
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'cursor-guard.so'
            output.write_bytes(b'\x7fELFprevious')
            with mock.patch.object(module.subprocess, 'run', new=mock.Mock(side_effect=pkg)), \
                 mock.patch.object(real_setup, 'header_abi',
                                   return_value='efb50993780079460b0cbed1363e2166a2de1d9f_x'), \
                 mock.patch.object(module, 'OUTPUT', output):
                with self.assertRaises(SystemExit):
                    module.build({})
            self.assertEqual(output.read_bytes(), b'\x7fELFprevious')
            self.assertFalse(list(Path(tmp).glob('.cursor-build-*')))

    def test_symlink_or_nonregular_output_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            real = Path(tmp) / 'real.so'
            real.write_bytes(b'\x7fELFreal')
            link = Path(tmp) / 'cursor-guard.so'
            link.symlink_to(real)
            with mock.patch.object(module.subprocess, 'run', new=mock.Mock(side_effect=pkg_ok)) as run, \
                 mock.patch.object(real_setup, 'header_abi',
                                   return_value='efb50993780079460b0cbed1363e2166a2de1d9f_x'), \
                 mock.patch.object(module, 'OUTPUT', link):
                with self.assertRaises(SystemExit):
                    module.build({})
            self.assertEqual([c.args[0][0] for c in run.call_args_list][:2],
                             ['pkg-config', 'pkg-config'])
            self.assertEqual(real.read_bytes(), b'\x7fELFreal')

    def test_main_invokes_build(self):
        with mock.patch.object(module, 'build', return_value=Path('/tmp/g.so')) as build:
            self.assertEqual(module.main([]), 0)
            build.assert_called_once_with()


class ImmutableGuardInstall(unittest.TestCase):
    def test_new_version_never_changes_existing_module(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            old = root / 'cursor-guard.so'
            old.write_bytes(b'old loaded module')
            source = root / 'built.so'
            source.write_bytes(b'\x7fELFtest version one')
            first = module.install(source, root)
            inode = first.stat().st_ino
            self.assertEqual(first.name[:13], 'cursor-guard-')
            self.assertEqual(module.install(source, root), first)
            self.assertEqual(first.stat().st_ino, inode)
            source.write_bytes(b'\x7fELFtest version two')
            second = module.install(source, root)
            self.assertNotEqual(first, second)
            self.assertEqual(old.read_bytes(), b'old loaded module')
            self.assertEqual(first.read_bytes(), b'\x7fELFtest version one')
            self.assertFalse(list(root.glob('.guard-*')))

    def test_mismatched_existing_hash_path_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            data = b'\x7fELFtest'
            source = root / 'built.so'
            source.write_bytes(data)
            target = root / ('cursor-guard-' + hashlib.sha256(data).hexdigest() + '.so')
            target.write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError, 'refusing overwrite'):
                module.install(source, root)
            self.assertEqual(target.read_bytes(), b'corrupt')

    def test_symlink_or_nonregular_target_is_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'built.so'
            source.write_bytes(b'\x7fELFtest')
            link = root / ('cursor-guard-' + hashlib.sha256(b'\x7fELFtest').hexdigest() + '.so')
            link.symlink_to(source)
            with self.assertRaisesRegex(ValueError, 'refusing overwrite'):
                module.install(source, root)

    def test_rejects_non_library(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'bad'
            source.write_bytes(b'not ELF')
            with self.assertRaisesRegex(ValueError, 'not an ELF'):
                module.install(source, folder)


if __name__ == '__main__':
    unittest.main()
