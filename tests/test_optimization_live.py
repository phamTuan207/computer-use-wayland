"""Verifier self-checks; no GUI or Wayland connection."""
import unittest
from optimization_live import button_crop, local_point, summary, verified


class CropTests(unittest.TestCase):
    LAYOUT = {'button': (100, 50, 120, 40), 'canvas': (10, 10, 50, 50)}

    def test_crop_is_padded_eight_and_inside_the_window(self):
        self.assertEqual(button_crop(self.LAYOUT, [800, 600]), [92, 42, 136, 56])
        # Clamped at both edges, and never empty.
        self.assertEqual(button_crop({'button': (0, 0, 20, 20)}, [800, 600]), [0, 0, 28, 28])
        self.assertEqual(button_crop({'button': (790, 590, 20, 20)}, [800, 600]), [782, 582, 18, 18])
        self.assertEqual(button_crop({'button': (0, 0, 800, 600)}, [800, 600]), [0, 0, 800, 600])

    def meta(self, origin, crop):
        return {'window_bounds': [origin[0], origin[1], 800, 600],
                'region': [origin[0] + crop[0], origin[1] + crop[1], crop[2], crop[3]],
                'image_size': [crop[2] * 2, crop[3] * 2]}

    def test_uncropped_keeps_the_old_mapping_at_a_nonzero_window_origin(self):
        meta = self.meta((1280, 720), (0, 0, 800, 600))
        bx, by, bw, bh = self.LAYOUT['button']
        for x, y in ((bx + bw/2, by + bh/2), (10, 10), (799, 599)):
            self.assertEqual(local_point(meta, x, y), [x*2, y*2], 'region origin cancels the window origin')

    def test_cropped_region_maps_relative_to_the_crop_at_any_origin(self):
        crop = button_crop(self.LAYOUT, [800, 600])
        meta = self.meta((1280, 720), crop)
        rx, ry, rw, rh = meta['region']
        # Crop top-left is image (0,0); the button centre is the middle of the crop.
        self.assertEqual(local_point(meta, crop[0], crop[1]), [0, 0])
        self.assertEqual(local_point(meta, crop[0] + rw/2, crop[1] + rh/2), [rw, rh])
        # The same layout point maps to the same image pixels whatever the window origin.
        self.assertEqual(local_point(meta, 100, 50), local_point(self.meta((0, 0), crop), 100, 50), 'the window origin cancels out')
        self.assertEqual(local_point(meta, 100, 50), [16, 16])


class VerifierTests(unittest.TestCase):
    def test_exact_text_not_prefix_or_normalized(self):
        self.assertTrue(verified('type32', {'text': 'Việt'}, 'Việt'))
        self.assertFalse(verified('type32', {'text': 'ViệtX'}, 'Việt'))
        self.assertFalse(verified('type32', {'text': 'Việt'}, 'Vie\u0323\u0302t'))

    def test_task_effects_required(self):
        for case in ['click', 'scroll', 'drag']:
            self.assertFalse(verified(case, {}, None))
        self.assertTrue(verified('click', {'clicks': 1}, None))
        self.assertFalse(verified('click', {'clicks': 2}, None))
        self.assertFalse(verified('scroll', {'scroll': 0}, None))
        self.assertTrue(verified('scroll', {'scroll': 20}, None))
        self.assertTrue(verified('drag', {'drag': [140, 60]}, None))
        self.assertFalse(verified('drag', {'drag': [100, 40]}, None))

    def test_percentile_nearest_rank(self):
        self.assertEqual(summary(list(range(1, 21)))['p95_ms'], 19)
        self.assertEqual(summary(list(range(1, 31)))['p95_ms'], 29)
