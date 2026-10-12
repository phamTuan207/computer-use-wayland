import ctypes
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

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
