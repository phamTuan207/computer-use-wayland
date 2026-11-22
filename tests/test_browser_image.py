"""Browser image persistence regressions; memory fixtures, no browser or GUI."""
import base64
from contextlib import ExitStack
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zlib
from unittest.mock import patch

from PIL import Image, PngImagePlugin, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('cu_browser_image', ROOT / 'scripts/cu.py')
cu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cu)


def encode(image, format='PNG', **options):
    stream = io.BytesIO()
    image.save(stream, format=format, **options)
    return stream.getvalue()


class BrowserImage(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        directory = self.stack.enter_context(tempfile.TemporaryDirectory())
        self.state = Path(directory) / 'state'
        self.stack.enter_context(patch.object(cu, 'STATE', self.state))

    def assert_saved(self, result, expected):
        path = Path(result['image'])
        record = Path(result['observation'])
        with Image.open(path) as saved:
            saved.load()
            self.assertEqual(saved.format, 'JPEG')
            self.assertEqual(saved.mode, 'RGB')
            self.assertEqual(saved.size, expected.size)
            # JPEG is lossy: solid-color fixtures round-trip within a few levels.
            diffs = [abs(a - b) for a, b in zip(saved.tobytes(), expected.tobytes())]
            self.assertLessEqual(max(diffs), 5)
            self.assertLessEqual(sum(diffs) / len(diffs), 2)
            # Only the JFIF container keys Pillow writes; no private metadata.
            self.assertEqual(set(saved.info),
                             {'jfif', 'jfif_version', 'jfif_unit', 'jfif_density'})
        self.assertEqual(result['image_size'], list(expected.size))
        # Pinned codec parameters (S0 J37): the stored JPEG is encoded at
        # CAPTURE_JPEG_QUALITY = 90, CAPTURE_JPEG_SUBSAMPLING = 0
        # (scripts/cu.py:71-72, encode at cu.py:885, recorded at
        # cu.py:908-911), so the persisted record must carry them.
        # Literals pin the values; changing the constants must update
        # this test consciously.
        self.assertEqual(result['jpeg_quality'], 90)
        self.assertEqual(result['jpeg_subsampling'], 0)
        # pixel_sha256 hashes the STORED (JPEG-decoded) pixels, not the source.
        self.assertEqual(result['pixel_sha256'],
                         hashlib.sha256(Image.open(path).convert('RGB').tobytes()).hexdigest())
        self.assertEqual(json.loads(record.read_text()), result)
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(record.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.state.stat().st_mode & 0o777, 0o700)
        self.assertEqual(path.parent, self.state)
        self.assertEqual(record.parent, self.state)

    def test_plain_png_is_reencoded_as_jpeg_with_same_pixels(self):
        image = Image.new('RGB', (16, 8), (19, 87, 203))
        raw = encode(image, compress_level=9)
        result = cu.save_observation(None, {'backend': 'browser', 'target': 'fixture'},
                                     320, encoded_png=raw)
        self.assertEqual(result['image_format'], 'JPEG')
        self.assertEqual(Path(result['image']).suffix, '.jpg')
        self.assertNotEqual(Path(result['image']).read_bytes(), raw)
        self.assert_saved(result, image)
        self.assertEqual(result['backend'], 'browser')
        self.assertEqual(result['target'], 'fixture')
        self.assertEqual(result['max_width'], 320)
        self.assertIsInstance(result['created'], (int, float))
        self.assertEqual(Path(result['image']).stem, result['id'])
        self.assertEqual(set(self.state.iterdir()), {Path(result['image']), Path(result['observation'])})

    def test_encoded_image_is_authoritative(self):
        image = Image.new('RGB', (17, 9), 'blue')
        raw = encode(image)
        unrelated = Image.new('RGB', (2, 3), 'red')
        result = cu.save_observation(unrelated, {}, 320, encoded_png=raw)
        self.assert_saved(result, image)
        self.assertNotEqual(Path(result['image']).read_bytes(), raw)

    def test_rgba_palette_and_other_format_fall_back_to_rgb_jpeg(self):
        palette = Image.new('P', (16, 8), 1)
        palette.putpalette([0, 0, 0, 10, 20, 30] + [0] * 762)
        cases = [(Image.new('RGBA', (16, 8), (10, 20, 30, 40)), 'PNG'),
                 (palette, 'PNG'), (Image.new('RGB', (16, 8), 'green'), 'BMP')]
        for image, format in cases:
            with self.subTest(mode=image.mode, format=format):
                raw = encode(image, format)
                result = cu.save_observation(None, {}, 320, encoded_png=raw)
                self.assertNotEqual(Path(result['image']).read_bytes(), raw)
                self.assert_saved(result, image.convert('RGB'))

    def test_png_metadata_is_stripped_on_fallback(self):
        image = Image.new('RGB', (16, 8), (10, 20, 30))
        text = PngImagePlugin.PngInfo()
        text.add_text('Description', 'private fixture metadata')
        exif = Image.Exif()
        exif[270] = 'private fixture metadata'
        for options in ({'pnginfo': text}, {'exif': exif}, {'transparency': (10, 20, 30)}):
            with self.subTest(metadata=next(iter(options))):
                raw = encode(image, **options)
                result = cu.save_observation(None, {}, 320, encoded_png=raw)
                self.assertNotEqual(Path(result['image']).read_bytes(), raw)
                self.assert_saved(result, image)

    def test_private_chunk_and_trailing_bytes_are_stripped(self):
        image = Image.new('RGB', (16, 8), (10, 20, 30))
        raw = encode(image)
        marker = b'FAKE_PRIVATE_METADATA'
        kind = b'raNd'
        chunk = len(marker).to_bytes(4, 'big') + kind + marker + (zlib.crc32(kind + marker) & 0xffffffff).to_bytes(4, 'big')
        for encoded in (raw[:-12] + chunk + raw[-12:], raw + marker):
            with self.subTest(trailing=encoded.endswith(marker)):
                with Image.open(io.BytesIO(encoded)) as decoded:
                    decoded.load()
                    self.assertEqual(decoded.info, {})
                result = cu.save_observation(None, {}, 320, encoded_png=encoded)
                saved = Path(result['image']).read_bytes()
                self.assertNotEqual(saved, encoded)
                self.assertNotIn(marker, saved)
                self.assert_saved(result, image)

    def test_resize_falls_back_with_final_pixel_hash(self):
        image = Image.new('RGB', (640, 16))
        image.paste((40, 80, 120), (0, 0, 320, 16))
        raw = encode(image)
        expected = image.resize((320, 8), Image.Resampling.LANCZOS)
        result = cu.save_observation(None, {}, 320, encoded_png=raw)
        self.assertNotEqual(Path(result['image']).read_bytes(), raw)
        self.assert_saved(result, expected)

    def test_corrupt_bytes_rejected_before_creating_output(self):
        raw = encode(Image.new('RGB', (16, 8)))
        for corrupt in (b'not an image', raw[:41]):
            with self.subTest(length=len(corrupt)):
                with self.assertRaises((UnidentifiedImageError, OSError, SyntaxError, ValueError)):
                    cu.save_observation(None, {}, 320, encoded_png=corrupt)
                self.assertFalse(self.state.exists())

    def test_persist_false_returns_rgb_without_state(self):
        for mode, width in (('RGB', 16), ('RGBA', 640)):
            with self.subTest(mode=mode):
                image = Image.new(mode, (width, 16))
                expected = image.convert('RGB')
                if width > 320:
                    expected = expected.resize((320, 8), Image.Resampling.LANCZOS)
                result, meta = cu.save_observation(None, {'backend': 'browser'}, 320,
                                                   persist=False, encoded_png=encode(image))
                self.assertEqual(result.mode, 'RGB')
                self.assertEqual(result.size, expected.size)
                self.assertEqual(result.tobytes(), expected.tobytes())
                # S0 J37 codec separation (commit 18f2304): save_observation
                # records the pinned codec parameters in the meta on both
                # paths (scripts/cu.py:876-879 persist=False, 908-911
                # persist=True), from CAPTURE_JPEG_QUALITY = 90 and
                # CAPTURE_JPEG_SUBSAMPLING = 0 (cu.py:71-72). The values
                # below are literals on purpose: they pin the pinned
                # parameters, so changing the constants must update this
                # test consciously instead of passing silently.
                self.assertEqual(meta, {'backend': 'browser', 'image_size': list(expected.size),
                                        'max_width': 320, 'image_format': 'JPEG',
                                        'image_bytes': None, 'image_sha256': None,
                                        'encode_ms': 0, 'jpeg_quality': 90,
                                        'jpeg_subsampling': 0})
                self.assertFalse(self.state.exists())

    def test_browser_cli_image_maps_flag_target_and_raw_bytes(self):
        image = Image.new('RGB', (16, 8), 'blue')
        raw = encode(image)
        stdout = io.StringIO()
        with patch.object(cu.sys, 'argv', ['cu', 'browser', 'observe', '--target', 'fixture', '--image']), \
             patch.object(cu.sys, 'stdout', stdout), patch.object(cu, 'check_cancel'), \
             patch.object(cu, 'locked'), patch.object(cu, 'environment') as environment, \
             patch.object(cu, 'browser', return_value={'snapshot': 'test',
                 'image_base64': base64.b64encode(raw).decode()}) as browser:
            self.assertEqual(cu.main(), 0)
        request = browser.call_args.args[0]
        self.assertEqual(request['operation'], 'observe')
        self.assertEqual(request['target'], 'fixture')
        self.assertIs(request['image'], True)
        environment.assert_not_called()
        result = json.loads(stdout.getvalue())
        self.assertNotIn('image_base64', result)
        self.assertEqual(result['snapshot'], 'test')
        self.assertNotEqual(Path(result['image']).read_bytes(), raw)
        record = json.loads(Path(result['image']).with_suffix('.json').read_text())
        self.assertEqual(record['backend'], 'browser')
        self.assertEqual(record['target'], 'fixture')
        self.assert_saved(record, image)


if __name__ == '__main__':
    unittest.main()
