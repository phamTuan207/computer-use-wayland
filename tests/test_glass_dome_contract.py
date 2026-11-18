"""Legacy dome gate for the 288 x 38 pill; the port's dome weight is zero here."""
from pathlib import Path
import math
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / 'native/hyprglass-shayxo-legacy.patch'
PILL = (288.0, 38.0)
BAND = 14.0


def smoothstep(edge0, edge1, value):
    t = min(max((value - edge0) / (edge1 - edge0), 0.0), 1.0)
    return t * t * (3.0 - 2.0 * t)


def dome_weight(width, height, band):
    aspect = max(width, height) / max(min(width, height), 1e-4)
    inradius = min(width, height) / 2.0
    return (smoothstep(1.5, 3.0, aspect)
            * smoothstep(0.75, 1.0, band / max(inradius, 1e-4)))


class ShayxoLegacyDomeContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.patch = PATCH.read_text()
        cls.added = '\n'.join(line[1:] for line in cls.patch.splitlines()
                              if line.startswith('+') and not line.startswith('+++'))

    def test_actual_pill_band_stops_below_dome_threshold(self):
        self.assertEqual(PILL, (288.0, 38.0))
        self.assertEqual(BAND, 14.0)
        self.assertAlmostEqual(min(PILL) / 2.0, 19.0)
        self.assertLess(BAND / 19.0, 0.75)
        self.assertEqual(dome_weight(*PILL, BAND), 0.0)

    def test_long_pill_aspect_alone_does_not_enable_dome(self):
        aspect = PILL[0] / PILL[1]
        self.assertGreater(aspect, 3.0)
        self.assertEqual(smoothstep(1.5, 3.0, aspect), 1.0)
        self.assertEqual(dome_weight(*PILL, BAND), 0.0)

    def test_wide_epsilon_axis_fade_handles_the_medial_axis(self):
        self.assertIn('float eps = clamp(bandPx * 0.3, 1.0, 16.0);', self.added)
        self.assertIn('float axisFade = smoothstep(0.15, 0.80, gLen / (2.0 * eps));',
                      self.added)
        axis_fade = smoothstep(0.15, 0.80, 0.0)
        rim_fade = smoothstep(0.15, 0.80, 1.0)
        self.assertEqual(axis_fade, 0.0)
        self.assertEqual(rim_fade, 1.0)

    def test_refraction_uses_sdf_depth_and_wide_epsilon_normal(self):
        self.assertIn('float depth = max(-bevelSdf, 0.0);', self.added)
        self.assertIn('float gLen = length(g);', self.added)
        self.assertIn('vec2 n = g / max(gLen, 1e-5);', self.added)
        self.assertIn('vec2 push = n * bend * lens;', self.added)

    def test_upstream_center_dome_is_removed_from_the_new_path(self):
        self.assertNotIn('domeUV', self.added)
        self.assertNotIn('lensMaxPx * lensFade', self.added)
        self.assertNotIn('dGrad * lensMaxPx', self.added)


if __name__ == '__main__':
    unittest.main()
