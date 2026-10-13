import ctypes
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('build_cursor',ROOT/'scripts/build-cursor.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class BuildCursor(unittest.TestCase):
    def test_existing_directory_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,'refusing overwrite'):module.build(tmp)

    @unittest.skipUnless(shutil.which('rsvg-convert'),'optional cursor renderer missing')
    def test_real_xcursor_decoder_accepts_each_size(self):
        try:lib=ctypes.CDLL('libXcursor.so.1')
        except OSError:self.skipTest('optional libXcursor missing')
        class CursorImage(ctypes.Structure):
            _fields_=[(k,ctypes.c_uint32) for k in ('version','size','width','height','xhot','yhot','delay')]+[('pixels',ctypes.c_void_p)]
        lib.XcursorFilenameLoadImage.argtypes=[ctypes.c_char_p,ctypes.c_int]
        lib.XcursorFilenameLoadImage.restype=ctypes.POINTER(CursorImage)
        lib.XcursorImageDestroy.argtypes=[ctypes.POINTER(CursorImage)]
        with tempfile.TemporaryDirectory() as tmp:
            directory=module.build(Path(tmp)/'theme')
            self.assertEqual((directory/'cursors/text').read_bytes(),(directory/'cursors/left_ptr').read_bytes())
            for size in (24,32,34,48,64):
                pointer=lib.XcursorFilenameLoadImage(str(directory/'cursors/left_ptr').encode(),size)
                self.assertTrue(pointer)
                try:
                    self.assertEqual(pointer.contents.width,size)
                    self.assertEqual(pointer.contents.xhot,round(size*18/64))
                    self.assertEqual(pointer.contents.yhot,round(size*18/64))
                finally:lib.XcursorImageDestroy(pointer)

    @unittest.skipUnless(shutil.which('rsvg-convert'),'optional cursor renderer missing')
    def test_rendered_silhouette_is_diagonally_symmetric(self):
        import io
        import subprocess
        from PIL import Image,ImageChops,ImageStat
        raw=subprocess.check_output(['rsvg-convert','-w','34','-h','34',str(ROOT/'native/agent-cursor.svg')])
        alpha=Image.open(io.BytesIO(raw)).convert('RGBA').getchannel('A')
        difference=ImageChops.difference(alpha,alpha.transpose(Image.Transpose.TRANSPOSE))
        self.assertLess(ImageStat.Stat(difference).mean[0],.3)


@unittest.skipUnless(shutil.which('rsvg-convert'), 'cursor renderer missing')
class ImmutableInstall(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def test_digest_is_content_addressed_and_ignores_the_host_path(self):
        first = module.build(self.dir / 'a')
        second = module.build(self.dir / 'b')
        self.assertEqual(module.tree_digest(first), module.tree_digest(second))
        self.assertNotIn(str(self.dir).encode(), module.tree_digest(first).encode())
        (second / 'index.theme').write_text('changed')
        self.assertNotEqual(module.tree_digest(first), module.tree_digest(second))

    def test_digest_follows_a_directory_symlink_instead_of_skipping_it(self):
        root = self.dir / 'theme'
        outside = self.dir / 'outside'
        outside.mkdir()
        (outside / 'extra').write_text('extra alias')
        module.build(root)
        before = module.tree_digest(root)
        (root / 'cursors' / 'extra').symlink_to(outside, target_is_directory=True)
        self.assertNotEqual(module.tree_digest(root), before,
                            'a directory symlink is part of the tree')

    def test_install_publishes_immutably_and_is_idempotent(self):
        icons = self.dir / 'icons'
        name, existed = module.install(icons)
        self.assertFalse(existed)
        self.assertEqual(name.name, 'cu-agent-' + module.tree_digest(name))
        again, existed_again = module.install(icons)
        self.assertTrue(existed_again)
        self.assertEqual(again, name)
        self.assertEqual([p.name for p in icons.iterdir()], [name.name],
                         'no staging residue survives the TemporaryDirectory')

    def test_install_refuses_a_different_tree_at_the_hash_path(self):
        icons = self.dir / 'icons'
        name, _ = module.install(icons)
        (name / 'index.theme').write_text('hijacked')
        with self.assertRaisesRegex(ValueError, 'refusing to touch'):
            module.install(icons)

    def test_install_refuses_a_symlink_at_the_target(self):
        icons = self.dir / 'icons'
        icons.mkdir()
        reference = module.build(self.dir / 'reference')
        (icons / ('cu-agent-' + module.tree_digest(reference))).symlink_to(reference)
        with self.assertRaisesRegex(ValueError, 'refusing to touch'):
            module.install(icons)

    def test_publish_rejects_a_symlink_created_at_the_destination(self):
        source = module.build(self.dir / 'source')
        other = module.build(self.dir / 'other')
        destination = self.dir / 'destination'
        destination.symlink_to(other)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            module.publish(source, destination)

    def test_publish_refuses_a_different_tree_at_the_same_path(self):
        source = module.build(self.dir / 'source')
        destination = module.build(self.dir / 'destination')
        (destination / 'index.theme').write_text('not the same tree')
        with self.assertRaisesRegex(ValueError, 'different theme already exists'):
            module.publish(source, destination)

    def test_publish_accepts_an_identical_tree_as_idempotent(self):
        source = module.build(self.dir / 'source')
        destination = module.build(self.dir / 'destination')
        self.assertEqual(module.publish(source, destination), destination)

    def test_missing_renameat2_publishes_nothing_and_fails_closed(self):
        source = module.build(self.dir / 'source')
        destination = self.dir / 'destination'
        with mock.patch.object(module.ctypes, 'CDLL', side_effect=OSError('no libc')):
            with self.assertRaises(OSError):
                module.publish(source, destination)
        with mock.patch.object(module.ctypes, 'CDLL', return_value=object()):
            with self.assertRaises(OSError):module.publish(source, destination)
        self.assertFalse(destination.exists(), 'nothing is created without the syscall')

    @unittest.skipUnless(shutil.which('rsvg-convert'), 'optional cursor renderer missing')
    def test_a_failed_render_publishes_nothing(self):
        icons = self.dir / 'icons'
        with mock.patch.object(module.subprocess, 'check_output',
                               side_effect=OSError('renderer missing')):
            with self.assertRaises(OSError):
                module.install(icons)
        published = icons.exists() and any(p.name.startswith('cu-agent-') for p in icons.iterdir())
        self.assertFalse(published, 'no theme is published when the render fails')


if __name__ == '__main__':
    unittest.main()
