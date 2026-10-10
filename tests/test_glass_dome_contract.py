"""Numeric dome contract for the inspected pinned 4edf shader, not GPU proof.

Models Shaders.hpp:410-425 and GlassRenderer.cpp:490 in the handoff backend.
On the straight capsule centreline, edgeProximity = exp(-19 / rim_depth).
Displacements are in pixels, after cancelling invFullSize from domeUV.
The public capsule patch does not contain this dome implementation: these
tests do not assert shader-string coverage, loaded binary identity, actual
rendered pixels, blur, or a visual improvement over an earlier preset.
Comparing with the analytic rim maximum is not a comparison with every rim
point (some rim displacements are zero).
"""
import math
from pathlib import Path
import re
import unittest


PRESET = Path(__file__).resolve().parents[1] / 'native/hyprglass-indicator.lua'
PILL = (288.0, 38.0)
POINTS = (72.0, 144.0, 216.0)
IOR = 1.45


def read_preset():
    """Read actual Lua assignments; ignore commented-out settings."""
    text = re.sub(r'--[^\n]*', '', PRESET.read_text())
    values = {}
    for name in ('edge_thickness', 'refraction_strength', 'lens_distortion'):
        match = re.search(r'\b' + name + r'\s*=\s*([0-9.]+)', text)
        if match is None:
            raise RuntimeError(f'preset is missing {name}')
        values[name] = float(match.group(1))
    return values


def dome_shift(x, edge, lens):
    """Pixel shift at y=19, restricted to the straight capsule centreline."""
    if not PILL[1] / 2 <= x <= PILL[0] - PILL[1] / 2:
        raise ValueError('point must lie on the straight capsule centreline')
    if lens <= 0.001:
        return 0.0, 0.0
    cx = (x - PILL[0] * 0.5) / (PILL[0] * 0.5)
    cy = 0.0
    gradient = (-4.0 * cx * (1.0 - cy * cy),
                -4.0 * cy * (1.0 - cx * cx))
    lens_max_px = lens * min(PILL) * 0.006
    edge_proximity = math.exp(-19.0 / (edge * min(PILL)))
    return tuple(v * lens_max_px * (1.0 - edge_proximity) for v in gradient)


def rim_bound(edge, strength):
    """Same analytic pixel bound as test_glass_optics_contract.analytic_bound."""
    return edge * min(PILL) * strength * math.sqrt(IOR * IOR - 1.0)


class GlassDomeContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.params = read_preset()

    def shift(self, x):
        return dome_shift(x, self.params['edge_thickness'],
                          self.params['lens_distortion'])

    def test_actual_preset_parameters_are_finite_and_positive(self):
        self.assertEqual(self.params, read_preset())
        for name, value in self.params.items():
            with self.subTest(name=name):
                self.assertTrue(math.isfinite(value))
                self.assertGreater(value, 0.0)
        self.assertGreater(self.params['lens_distortion'], 0.001)

    def test_off_axis_shifts_are_finite_nonzero_and_point_inward(self):
        for x in (POINTS[0], POINTS[2]):
            with self.subTest(x=x):
                dx, dy = self.shift(x)
                self.assertTrue(math.isfinite(dx) and math.isfinite(dy))
                self.assertGreater(abs(dx), 0.0)
                self.assertEqual(dy, 0.0)
                self.assertLess(dx * (x - PILL[0] / 2), 0.0)

    def test_exact_symmetry_axis_has_zero_shift(self):
        self.assertEqual(self.shift(POINTS[1]), (0.0, 0.0))

    def test_mirrored_displacements(self):
        left, right = self.shift(POINTS[0]), self.shift(POINTS[2])
        self.assertEqual(left[0], -right[0])
        self.assertEqual(left[1], right[1])

    def test_central_model_shifts_are_weaker_than_analytic_rim_bound(self):
        bound = rim_bound(self.params['edge_thickness'],
                          self.params['refraction_strength'])
        self.assertTrue(math.isfinite(bound))
        self.assertGreater(bound, 0.0)
        for x in POINTS:
            with self.subTest(x=x):
                self.assertLess(math.hypot(*self.shift(x)), bound)


if __name__ == '__main__':
    unittest.main()
