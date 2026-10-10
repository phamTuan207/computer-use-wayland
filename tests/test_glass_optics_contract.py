"""C37 contract tests: capsule-rim refraction math + patch applicability (no GUI/build).

Numeric part mirrors the Shaders.hpp math (no GPU): explicit flat-interior points
must be exactly zero, top/bottom and left/right mirror-symmetric, finite,
continuous, and bounded to <= ~1px at the current strength. Patch part applies
native/hyprglass-capsule.patch to a fresh pinned upstream exported with
`git archive` (only the 3 files), using an optional CU_HYPRGLASS_SOURCE env path;
it skips when that path or git is unavailable (no private path baked in).
"""
import math
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / 'native/hyprglass-capsule.patch'
PILL = (288.0, 38.0)
EDGE = 0.08
STRENGTH = 0.15
IOR = 1.45
PIN = '84c1a5ab217101a317d4edaab7fba2efcc1bf346'


def surface(lx, ly):
    """Mirror of Shaders.hpp capsuleNormal + thin-rim branch. Returns (ox, oy)."""
    r = min(PILL[1] * 0.5, min(PILL) * 0.5)
    cx = min(max(lx, r), max(r, PILL[0] - r))
    cy = min(max(ly, r), max(r, PILL[1] - r))
    dx, dy = lx - cx, ly - cy
    dist = math.hypot(dx, dy)
    edge = max(0.0, r - dist)
    depth = EDGE * min(PILL)
    band = min(max(1.0 - edge / max(1e-5, depth), 0.0), 1.0)
    rim = band * band * (3.0 - 2.0 * band)
    if rim <= 0.0:
        return 0.0, 0.0
    n2 = (dx / dist, dy / dist) if dist > 1e-5 else (0.0, 0.0)
    s = min(dist / max(1e-5, r), 1.0)
    nz = math.sqrt(max(0.0, 1.0 - s * s))
    eta = 1.0 / IOR
    k = 1.0 - eta * eta * (1.0 - nz * nz)
    if k < 0.0:
        return 0.0, 0.0
    scale = eta * nz - math.sqrt(k)
    rz = -eta + scale * nz
    slab = depth / max(0.2, abs(rz))
    return (scale * n2[0] * s) * slab * STRENGTH * rim, (scale * n2[1] * s) * slab * STRENGTH * rim


class CapsuleRefractionMath(unittest.TestCase):
    def test_flat_interior_points_are_exactly_zero(self):
        points = [(60.0, 19.0), (144.0, 19.0), (220.0, 19.0)]
        zeros = [surface(x, y) for x, y in points]
        self.assertEqual(len(zeros), 3)
        for point, value in zip(points, zeros):
            with self.subTest(point=point):
                self.assertEqual(value, (0.0, 0.0))

    def test_top_and_bottom_are_mirror_symmetric(self):
        for lx in (60.0, 144.0, 220.0):
            for d in (0.5, 1.5, 3.0):
                top, bottom = surface(lx, d), surface(lx, PILL[1] - d)
                with self.subTest(lx=lx, d=d):
                    self.assertAlmostEqual(top[1], -bottom[1], places=6)
                    self.assertAlmostEqual(top[0], bottom[0], places=6)

    def test_left_and_right_are_mirror_symmetric(self):
        for ly in (10.0, 19.0, 28.0):
            left, right = surface(1.0, ly), surface(PILL[0] - 1.0, ly)
            with self.subTest(ly=ly):
                self.assertAlmostEqual(left[0], -right[0], places=6)
                self.assertAlmostEqual(left[1], right[1], places=6)

    def test_displacement_is_finite_and_bounded_below_one_px(self):
        for i in range(0, 289, 4):
            for j in range(0, 39, 2):
                ox, oy = surface(float(i), float(j))
                with self.subTest(i=i, j=j):
                    self.assertTrue(math.isfinite(ox) and math.isfinite(oy))
                    self.assertLessEqual(math.hypot(ox, oy), 1.0)

    def test_displacement_is_continuous_across_a_rim_row(self):
        prev = surface(0.0, 5.0)
        for i in range(1, 289):
            cur = surface(float(i), 5.0)
            with self.subTest(i=i):
                self.assertLess(math.hypot(cur[0] - prev[0], cur[1] - prev[1]), 0.5)
            prev = cur


class CapsulePatchApplicability(unittest.TestCase):
    def test_patch_applies_to_fresh_pinned_upstream(self):
        source = os.environ.get('CU_HYPRGLASS_SOURCE')
        if not (PATCH.is_file() and source and Path(source).is_dir() and shutil.which('git')):
            self.skipTest('set CU_HYPRGLASS_SOURCE to a pinned hyprglass git repo to run this')
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            subprocess.run(['git', 'init', '-q'], cwd=folder, check=True)
            files = ['src/Shaders.hpp', 'src/GlassLayerSurface.cpp', 'src/GlassRenderer.cpp']
            archive = subprocess.run(['git', 'archive', 'HEAD', *files], cwd=source,
                                     capture_output=True, check=True)
            subprocess.run(['tar', '-x', '-C', str(folder)], input=archive.stdout, check=True)
            head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip()
            self.assertEqual(head, PIN)
            subprocess.run(['git', 'add', '-A'], cwd=folder, check=True)
            subprocess.run(['git', '-c', 'user.email=t@t', '-c', 'user.name=t', 'commit', '-qm', 'pin'],
                           cwd=folder, check=True)
            check = subprocess.run(['git', 'apply', '--check', str(PATCH)], cwd=folder,
                                   capture_output=True, text=True)
            self.assertEqual(check.returncode, 0, check.stderr)
            subprocess.run(['git', 'apply', str(PATCH)], cwd=folder, check=True)
            shader = (folder / 'src/Shaders.hpp').read_text()
            self.assertIn('capsuleNormal', shader)
            self.assertIn('1.0 / 1.45', shader)
            self.assertNotIn('vec2 inset', shader)


if __name__ == '__main__':
    unittest.main()
