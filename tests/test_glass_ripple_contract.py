"""Analytic bounds for added capsule rim/ripple, not GPU visual proof."""
import math
from pathlib import Path
import re
import unittest

PATCH = (Path(__file__).resolve().parents[1] / 'native/hyprglass-capsule.patch').read_text()


def constant(name):
    return float(re.search(r'const float ' + name + r' = ([0-9.]+);', PATCH)[1])


class CapsuleRippleContract(unittest.TestCase):
    def test_wider_exponential_rim(self):
        decay = constant('capsuleRimDistance')
        self.assertGreater(decay, 0)
        self.assertLess(decay, 0.8)
        self.assertGreater(math.exp(-5 * decay), math.exp(-5 * 0.8))

    def test_added_displacement_is_bounded(self):
        strength = constant('capsuleRimIntensityPx')
        ripple = constant('capsuleRipplePx')
        decay = constant('capsuleRimDistance')
        bound = math.hypot(strength, ripple)
        for i in range(1901):
            distance = i / 100
            normal = (19 - distance) / 19
            envelope = math.exp(-distance * decay)
            radial = normal * strength * envelope
            tangential = math.sin(distance / 38 * 25) * ripple * envelope * normal
            self.assertTrue(math.isfinite(radial + tangential))
            self.assertLessEqual(math.hypot(radial, tangential), bound + 1e-9)

    def test_axis_fades_without_normalization_jump(self):
        self.assertIn('rimEnvelope * normalLength', PATCH)
        self.assertIn('normalLength > 1e-5', PATCH)
        self.assertIn('baseOffset += (rimOffsetPx + tangent * ripple) * invFullSize;', PATCH)


if __name__ == '__main__':
    unittest.main()
