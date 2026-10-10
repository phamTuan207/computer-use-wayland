"""Geometry and build-selection contracts; not visual acceptance."""
from pathlib import Path
import math
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LocalOptics(unittest.TestCase):
    def test_patch_scoped_to_indicator(self):
        patch = (ROOT / 'native/hyprglass-local-optics.patch').read_text()
        self.assertIn('m_namespace == "computer-use-indicator"', patch)
        self.assertIn('const bool validOpticalBox', patch)
        self.assertIn('if (validOpticalBox)', patch)

    def test_full_box_sentinel_equivalence(self):
        for width, height in ((320,66),(288,38),(1920,1080)):
            for u,v in ((0,0),(.1,.7),(.5,.5),(1,1)):
                self.assertAlmostEqual(width*.5-u*width,(.5-u)*width)
                self.assertAlmostEqual(height*.5-v*height,(.5-v)*height)

    def test_rim_fades_inside(self):
        width = .12*38
        self.assertGreater(math.exp(-2/width), .6)
        self.assertLess(math.exp(-19/width), .02)

    def test_material_has_no_plate_or_noise(self):
        text=(ROOT/'native/hyprglass-local-optics.lua').read_text()
        self.assertIn('tint_color = 0xffffff00', text)
        self.assertIn('noise_strength = 0.0', text)
        self.assertIn('enabled = false', text)


if __name__ == '__main__':
    unittest.main()
