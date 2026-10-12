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
            self.assertEqual(saved.format, 'PNG')
            self.assertEqual(saved.mode, 'RGB')
            self.assertEqual(saved.size, expected.size)
            self.assertEqual(saved.tobytes(), expected.tobytes())
            self.assertEqual(saved.info, {})
        self.assertEqual(result['image_size'], list(expected.size))
        self.assertEqual(result['pixel_sha256'], hashlib.sha256(expected.tobytes()).hexdigest())
        self.assertEqual(json.loads(record.read_text()), result)
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(record.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.state.stat().st_mode & 0o777, 0o700)
        self.assertEqual(path.parent, self.state)
        self.assertEqual(record.parent, self.state)

    def test_plain_png_preserves_bytes_pixels_hash_and_private_metadata(self):
        image = Image.new('RGB', (16, 8), (19, 87, 203))
        raw = encode(image, compress_level=9)
        result = cu.save_observation(None, {'backend': 'browser', 'target': 'fixture'},
                                     320, encoded_png=raw)
        self.assertEqual(Path(result['image']).read_bytes(), raw)
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
        self.assertEqual(Path(result['image']).read_bytes(), raw)

    def test_rgba_palette_and_other_format_fall_back_to_rgb_png(self):
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

    def test_plain_png_predicate_rejects_invalid_structure(self):
        raw = encode(Image.new('RGB', (16, 8)))
        signature, header, end = raw[:8], raw[8:33], raw[-12:]
        data = raw[33:-12]
        self.assertTrue(cu.plain_rgb_png(raw))
        self.assertTrue(cu.plain_rgb_png(signature + header + data + data + end))
        invalid = [b'', raw[:41], raw[:-1], raw + b'extra',
                   signature + data + header + end,
                   signature + header + header + data + end,
                   signature + header + end,
                   raw[:8] + (14).to_bytes(4, 'big') + raw[12:],
                   raw[:24] + b'\x10' + raw[25:],
                   raw[:25] + b'\x06' + raw[26:],
                   raw[:-12] + b'\x00\x00\x00\x01IENDx' + b'\x00' * 4]
        for encoded in invalid:
            with self.subTest(encoded=encoded):
                self.assertFalse(cu.plain_rgb_png(encoded))

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
                self.assertEqual(meta, {'backend': 'browser', 'image_size': list(expected.size),
                                        'max_width': 320})
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
        self.assertEqual(Path(result['image']).read_bytes(), raw)
        record = json.loads(Path(result['image']).with_suffix('.json').read_text())
        self.assertEqual(record['backend'], 'browser')
        self.assertEqual(record['target'], 'fixture')
        self.assert_saved(record, image)


if __name__ == '__main__':
    unittest.main()
