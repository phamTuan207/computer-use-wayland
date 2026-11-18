"""Numeric Legacy Snell contract; this models the formula, not GPU pixels."""
import math
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / 'native/hyprglass-shayxo-legacy.patch'
PIN = '03a57c4451b4abee38feda2ffb725f55ecc0f2fd'
BAND = 14.0
IOR = 1.5


def smoothstep(edge0, edge1, value):
    t = min(max((value - edge0) / (edge1 - edge0), 0.0), 1.0)
    return t * t * (3.0 - 2.0 * t)


def bevel_slope(e, power=2.0):
    u = 1.0 - min(max(e, 0.002), 0.998)
    up = u ** power
    return u ** (power - 1.0) / max(1.0 - up, 1e-4) ** (1.0 - 1.0 / power)


def snell_shift(slope, ior=IOR):
    inv = 1.0 / math.sqrt(1.0 + slope * slope)
    si, ci = slope * inv, inv
    st = si / max(ior, 1.0001)
    ct = math.sqrt(max(1.0 - st * st, 0.0))
    return (si * ct - ci * st) / max(ci * ct + si * st, 1e-4)


def legacy_bend(depth):
    """Formula on a straight edge where axisFade is 1 and the pill dome is off."""
    e = min(max(depth / BAND, 0.0), 1.0)
    norm = snell_shift(bevel_slope(e)) / max(snell_shift(bevel_slope(0.0)), 1e-4)
    value = norm * (1.0 - smoothstep(0.75, 1.0, e)) * smoothstep(0.0, 1.5, depth)
    return min(max(value, 0.0), 1.0)


class ShayxoLegacyOptics(unittest.TestCase):
    def test_snell_slope_and_shift_checkpoints(self):
        expected = (
            (0.0, 15.787661329349902, 0.9884703910325521),
            (0.5, 0.5773502691896258, 0.18585864213631031),
            (0.75, 0.2581988897471611, 0.085439167812735),
            (1.0, 0.002000004000012002, 0.0006666677037062224),
        )
        for e, slope, shift in expected:
            with self.subTest(e=e):
                self.assertAlmostEqual(bevel_slope(e), slope, places=12)
                self.assertAlmostEqual(snell_shift(bevel_slope(e)), shift, places=12)

    def test_formula_bend_at_e_checkpoints(self):
        expected = ((0.0, 0.0), (0.5, 0.1880265143219547),
                    (0.75, 0.08643573807353562), (1.0, 0.0))
        for e, bend in expected:
            with self.subTest(e=e):
                self.assertAlmostEqual(legacy_bend(e * BAND), bend, places=12)

    def test_formula_bend_at_depth_checkpoints(self):
        expected = (
            (0.5, 0.18117986236406433),
            (1.5, 0.5089222661459225),
            (3.0, 0.3721929229811058),
            (7.0, 0.1880265143219547),
            (10.5, 0.08643573807353562),
            (12.0, 0.02944844808214233),
            (13.0, 0.004784817221885405),
            (14.0, 0.0),
        )
        for depth, bend in expected:
            with self.subTest(depth=depth):
                self.assertAlmostEqual(legacy_bend(depth), bend, places=12)

    def test_full_strength_plateau_claim_is_not_the_formula(self):
        # smoothstep's outer factor is 1 here, but the normalized Snell term
        # still shapes bend; its local peak is only about 0.515, never 1.
        samples = [(legacy_bend(i / 10000.0), i / 10000.0)
                   for i in range(140001)]
        peak, depth = max(samples)
        self.assertAlmostEqual(peak, 0.5152467247524806, places=8)
        self.assertAlmostEqual(depth, 1.3983, places=4)
        self.assertAlmostEqual(legacy_bend(1.5), 0.5089222661459225, places=12)

    def test_profile_joins_are_c1(self):
        for join in (0.0, 1.5, 10.5, 14.0):
            h = 1e-4
            if join == 0.0:
                left, right = 0.0, (legacy_bend(h) - legacy_bend(0.0)) / h
            elif join == 14.0:
                left = (legacy_bend(join) - legacy_bend(join - h)) / h
                right = 0.0
            else:
                left = (legacy_bend(join) - legacy_bend(join - h)) / h
                right = (legacy_bend(join + h) - legacy_bend(join)) / h
            with self.subTest(join=join):
                self.assertLess(abs(left - right), 0.001)

    def test_profile_is_finite_bounded_and_fades_to_flat_interior(self):
        values = [legacy_bend(i / 100.0) for i in range(1401)]
        self.assertTrue(all(math.isfinite(value) for value in values))
        self.assertTrue(all(0.0 <= value <= 1.0 for value in values))
        self.assertEqual(legacy_bend(14.0), 0.0)
        self.assertEqual(legacy_bend(15.0), 0.0)

    def test_patch_applies_to_fresh_pinned_upstream_when_source_is_supplied(self):
        source = os.environ.get('CU_HYPRGLASS_SOURCE')
        if not (PATCH.is_file() and source and Path(source).is_dir() and shutil.which('git')):
            self.skipTest('set CU_HYPRGLASS_SOURCE to a pinned hyprglass git repo to run this')
        head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip()
        self.assertEqual(head, PIN)
        shader = subprocess.check_output(
            ['git', 'show', 'HEAD:src/Shaders.hpp'], cwd=source, text=True)
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / 'src').mkdir()
            (folder / 'src/Shaders.hpp').write_text(shader)
            check = subprocess.run(
                ['git', 'apply', '--check', str(PATCH)], cwd=folder,
                capture_output=True, text=True)
            self.assertEqual(check.returncode, 0, check.stderr)


if __name__ == '__main__':
    unittest.main()
