"""Synthetic image checks for opt-in change-only observation."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import cu
import code_exec


class TileHashTests(unittest.TestCase):
    def test_hashes_are_stable_and_sensitive(self):
        first = Image.new('RGB', (120, 80), 'black')
        same = first.copy()
        changed = first.copy()
        ImageDraw.Draw(changed).rectangle((0, 0, 9, 9), fill='white')
        self.assertEqual(cu.tile_hashes(first, 12, 8),
                         cu.tile_hashes(same, 12, 8))
        self.assertNotEqual(cu.tile_hashes(first, 12, 8)[0],
                            cu.tile_hashes(changed, 12, 8)[0])


class DiffObservationTests(unittest.TestCase):
    def setUp(self):
        self.previous = Image.new('RGB', (120, 80), 'black')
        self.current = self.previous.copy()
        ImageDraw.Draw(self.current).rectangle((48, 32, 57, 41), fill='white')

    def test_identical_frames_return_none(self):
        result = cu.diff_observation(self.previous, self.previous.copy())
        self.assertEqual(result['mode'], 'none')
        self.assertEqual(result['changed_tile_count'], 0)
        self.assertIsNone(result['image'])
        self.assertNotIn('tile_distances', result)

    def test_missing_baseline_returns_full_frame(self):
        result = cu.diff_observation(None, self.current)
        self.assertEqual(result['mode'], 'full')
        self.assertEqual(result['image'].tobytes(), self.current.tobytes())

    def test_small_change_returns_padded_crop_from_current_frame(self):
        result = cu.diff_observation(self.previous, self.current)
        self.assertEqual(result['mode'], 'diff')
        x, y, width, height = result['bbox']
        self.assertLessEqual(x, 48 - cu.DIFF_PADDING_PIXELS)
        self.assertLessEqual(y, 32 - cu.DIFF_PADDING_PIXELS)
        self.assertGreaterEqual(x + width, 58 + cu.DIFF_PADDING_PIXELS)
        self.assertGreaterEqual(y + height, 42 + cu.DIFF_PADDING_PIXELS)
        self.assertEqual(result['image'].tobytes(),
                         self.current.crop((x, y, x + width, y + height)).tobytes())

    def test_full_frame_change_returns_full(self):
        black = Image.new('RGB', (120, 80), 'black')
        white = Image.new('RGB', (120, 80), 'white')
        self.assertEqual(cu.diff_observation(black, white)['mode'], 'full')

    def test_small_low_level_noise_is_not_full(self):
        noisy = self.previous.copy()
        noisy.putpixel((10, 10), (2, 2, 2))
        noisy.putpixel((11, 10), (2, 2, 2))
        result = cu.diff_observation(self.previous, noisy)
        self.assertIn(result['mode'], ('none', 'diff'))
        self.assertLess(result['changed_fraction'], cu.FULL_FRAME_FRACTION)

    def test_size_mismatch_returns_full(self):
        resized = Image.new('RGB', (121, 80), 'black')
        result = cu.diff_observation(self.previous, resized)
        self.assertEqual(result['mode'], 'full')
        self.assertTrue(result['size_mismatch'])

    def test_diff_has_bounded_thumbnail_and_summary(self):
        old = Image.new('RGB', (640, 320), 'black')
        new = old.copy()
        ImageDraw.Draw(new).rectangle((300, 140, 319, 159), fill='white')
        result = cu.diff_observation(old, new)
        self.assertEqual(result['mode'], 'diff')
        self.assertIsNotNone(result['thumbnail'])
        self.assertLessEqual(result['thumbnail'].width, 320)
        self.assertIn('mode=diff', result['summary'])
        self.assertIn(str(result['changed_tile_count']), result['summary'])
        self.assertIn(str(result['bbox']), result['summary'])

    def test_crop_metadata_maps_points_to_full_frame(self):
        result = cu.diff_observation(
            self.previous, self.current, region=[100, 200, 120, 80])
        metadata = result['metadata']
        self.assertEqual(cu.validate_coordinate_metadata(metadata),
                         (*metadata['image_size'], *metadata['region']))
        x, y, _, _ = result['bbox']
        self.assertEqual(cu.image_point(metadata, 0, 0), (100 + x, 200 + y))


class ChangeOnlyApiTests(unittest.TestCase):
    class Backend:
        def __init__(self):
            self.calls = []
            self.meta = {
                'id': 'abcdef012345', 'image': '/tmp/fresh.png',
                'observation': '/tmp/fresh.json', 'window': '0x1',
                'window_bounds': [0, 0, 120, 80], 'image_size': [120, 80],
                'region': [0, 0, 120, 80], 'monitor': 'test',
                'scope': 'window', 'crop': None, 'max_width': 960,
            }

        def observe_window(self, address, crop, max_width):
            self.calls.append(('observe_window', address, crop, max_width))
            return dict(self.meta)

    def test_missing_previous_falls_back_to_full_observe(self):
        backend = self.Backend()
        session = code_exec.CodeExecSession(backend)
        fresh = Image.new('RGB', (120, 80), 'green')
        with patch.object(cu, 'validate_desktop_observation', return_value=fresh):
            result = session.api_observe_change_only(None, window='0x1')
        self.assertEqual(result['mode'], 'full')
        self.assertEqual(result['image'], result['observation']['image'])
        self.assertIsNone(result['thumbnail'])
        self.assertEqual(backend.calls, [('observe_window', '0x1', None, 960)])

    def test_invalid_previous_falls_back_to_full_observe(self):
        backend = self.Backend()
        session = code_exec.CodeExecSession(backend)
        session.observations['stale-id'] = {
            'id': 'stale-id', 'scope': 'window', 'window': '0x1',
            'crop': None, 'max_width': 960,
        }
        fresh = Image.new('RGB', (120, 80), 'green')

        def validate(meta, env, load_image=False):
            if meta['id'] == 'stale-id':
                raise ValueError('stale observation')
            return fresh

        with patch.object(cu, 'validate_desktop_observation', side_effect=validate):
            result = session.api_observe_change_only({'id': 'stale-id'})
        self.assertEqual(result['mode'], 'full')
        self.assertEqual(backend.calls, [('observe_window', '0x1', None, 960)])

    def test_valid_previous_compares_with_a_fresh_capture(self):
        backend = self.Backend()
        session = code_exec.CodeExecSession(backend)
        previous_meta = dict(backend.meta, id='previous-id')
        session.observations['previous-id'] = previous_meta
        previous = Image.new('RGB', (120, 80), 'black')
        fresh = previous.copy()
        ImageDraw.Draw(fresh).rectangle((48, 32, 57, 41), fill='white')

        def load(meta, env, load_image=False):
            return previous if meta['id'] == 'previous-id' else fresh

        with patch.object(cu, 'validate_desktop_observation', side_effect=load):
            result = session.api_observe_change_only({'id': 'previous-id'})
        self.assertEqual(result['mode'], 'diff')
        with Image.open(result['image']) as saved:
            saved.load()
            expected = fresh.crop((result['bbox'][0], result['bbox'][1],
                                   result['bbox'][0] + result['bbox'][2],
                                   result['bbox'][1] + result['bbox'][3]))
            self.assertEqual(saved.tobytes(), expected.tobytes())
        self.assertEqual(backend.calls, [('observe_window', '0x1', None, 960)])

    def test_diff_returns_private_png_crop_and_thumbnail_paths(self):
        with tempfile.TemporaryDirectory() as folder:
            backend = self.Backend()
            backend.meta['image'] = str(Path(folder) / 'fresh.png')
            session = code_exec.CodeExecSession(backend)
            previous_meta = dict(backend.meta, id='previous-id')
            session.observations['previous-id'] = previous_meta
            previous = Image.new('RGB', (120, 80), 'black')
            fresh = previous.copy()
            ImageDraw.Draw(fresh).rectangle((48, 32, 57, 41), fill='white')
            expected = cu.diff_observation(previous, fresh)

            def load(meta, env, load_image=False):
                return previous if meta['id'] == 'previous-id' else fresh

            with patch.object(cu, 'validate_desktop_observation', side_effect=load):
                result = session.api_observe_change_only({'id': 'previous-id'})
                repeated = session.api_observe_change_only({'id': 'previous-id'})

            self.assertEqual(result['mode'], 'diff')
            self.assertEqual(result['image'], result['image_path'])
            self.assertEqual(result['thumbnail'], result['thumbnail_path'])
            self.assertEqual(result['image'], repeated['image'])
            self.assertEqual(result['thumbnail'], repeated['thumbnail'])
            self.assertTrue(Path(result['image']).is_file())
            self.assertTrue(Path(result['thumbnail']).is_file())
            with Image.open(result['image']) as saved_crop:
                saved_crop.load()
                x, y, width, height = result['bbox']
                expected_crop = fresh.crop((x, y, x + width, y + height))
                self.assertEqual(saved_crop.format, 'PNG')
                self.assertEqual(saved_crop.size, expected_crop.size)
                self.assertEqual(saved_crop.tobytes(), expected_crop.tobytes())
            with Image.open(result['thumbnail']) as saved_thumbnail:
                saved_thumbnail.load()
                self.assertEqual(saved_thumbnail.format, 'PNG')
                self.assertEqual(saved_thumbnail.tobytes(),
                                 expected['thumbnail'].tobytes())
                self.assertLessEqual(saved_thumbnail.width,
                                     cu.DIFF_THUMBNAIL_MAX_WIDTH)
            self.assertEqual(Path(result['image']).stat().st_mode & 0o777, 0o600)
            self.assertEqual(Path(result['thumbnail']).stat().st_mode & 0o777,
                             0o600)

    def test_change_only_file_paths_survive_program_envelope(self):
        with tempfile.TemporaryDirectory() as folder:
            backend = self.Backend()
            backend.meta['image'] = str(Path(folder) / 'fresh.png')
            session = code_exec.CodeExecSession(backend, state_dir=folder)
            session.observations['previous-id'] = dict(
                backend.meta, id='previous-id')
            previous = Image.new('RGB', (120, 80), 'black')
            fresh = previous.copy()
            ImageDraw.Draw(fresh).rectangle((48, 32, 57, 41), fill='white')

            def load(meta, env, load_image=False):
                return previous if meta['id'] == 'previous-id' else fresh

            with patch.object(cu, 'validate_desktop_observation', side_effect=load):
                envelope = session.run(
                    "change = observe_change_only({'id': 'previous-id'})")

            self.assertTrue(envelope['ok'], envelope)
            self.assertIn('change', envelope['variables'])
            json.dumps(envelope['variables'])
            change = envelope['variables']['change']
            self.assertEqual(change['mode'], 'diff')
            for key in ('image', 'thumbnail'):
                self.assertIsInstance(change[key], str)
                self.assertTrue(Path(change[key]).is_file())

    def test_identical_frames_return_none_without_image_files(self):
        backend = self.Backend()
        session = code_exec.CodeExecSession(backend)
        session.observations['previous-id'] = dict(
            backend.meta, id='previous-id')
        same = Image.new('RGB', (120, 80), 'black')
        with patch.object(cu, 'validate_desktop_observation', return_value=same):
            result = session.api_observe_change_only({'id': 'previous-id'})
        self.assertEqual(result['mode'], 'none')
        self.assertIsNone(result['image'])
        self.assertIsNone(result['thumbnail'])

    def test_change_only_name_is_allowed_in_programs(self):
        code_exec.validate_program("observe_change_only(None, window='0x1')")


if __name__ == '__main__':
    unittest.main()
