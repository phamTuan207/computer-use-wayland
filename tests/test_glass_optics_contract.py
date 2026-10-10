"""C39 contract tests for the capsule rim optics (numeric model, NOT a GPU render claim).

edge_thickness / refraction_strength are parsed from the real preset so the tests
cannot go stale; the displacement bound is the analytical
    depth * strength * sqrt(IOR^2 - 1)
(with depth = edge_thickness * min(pill) and IOR = 1.45, the shader constant),
plus a tiny relative tolerance. Also checks finite, mirror symmetry, exact zero in
the flat centre, exact zero more than one rim depth inside (including near the left
and right ends), and small-step continuity. The patch-applicability test skips
unless CU_HYPRGLASS_SOURCE is set.
"""
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / 'native/hyprglass-capsule.patch'
PRESET = ROOT / 'native/hyprglass-indicator.lua'
PILL = (288.0, 38.0)
IOR = 1.45
PIN = '84c1a5ab217101a317d4edaab7fba2efcc1bf346'


def read_preset():
    text = PRESET.read_text()
    edge = re.search(r'edge_thickness\s*=\s*([0-9.]+)', text)
    strength = re.search(r'refraction_strength\s*=\s*([0-9.]+)', text)
    if not edge or not strength:
        raise RuntimeError('preset is missing edge_thickness / refraction_strength')
    return float(edge.group(1)), float(strength.group(1))


def depth_px(edge):
    return edge * min(PILL)


def analytic_bound(edge, strength):
    return depth_px(edge) * strength * math.sqrt(IOR * IOR - 1.0)


def edge_distance(lx, ly):
    r = min(PILL[1] * 0.5, min(PILL) * 0.5)
    cx = min(max(lx, r), max(r, PILL[0] - r))
    cy = min(max(ly, r), max(r, PILL[1] - r))
    return max(0.0, r - math.hypot(lx - cx, ly - cy))


def surface(lx, ly, edge, strength):
    """Mirror of Shaders.hpp capsuleNormal + thin-rim branch."""
    r = min(PILL[1] * 0.5, min(PILL) * 0.5)
    depth = depth_px(edge)
    band = min(max(1.0 - edge_distance(lx, ly) / max(1e-5, depth), 0.0), 1.0)
    rim = band * band * (3.0 - 2.0 * band)
    if rim <= 0.0:
        return 0.0, 0.0
    cx = min(max(lx, r), max(r, PILL[0] - r))
    cy = min(max(ly, r), max(r, PILL[1] - r))
    dx, dy = lx - cx, ly - cy
    dist = math.hypot(dx, dy)
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
    return (scale * n2[0] * s) * slab * strength * rim, (scale * n2[1] * s) * slab * strength * rim


class CapsuleRefraction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not PRESET.is_file():
            raise unittest.SkipTest('preset unavailable')
        cls.edge, cls.strength = read_preset()
        cls.depth = depth_px(cls.edge)
        cls.bound = analytic_bound(cls.edge, cls.strength)

    def test_preset_values_are_parsed_and_reproducible(self):
        self.assertGreater(self.edge, 0.0)
        self.assertGreater(self.strength, 0.0)
        self.assertEqual((self.edge, self.strength), read_preset())  # parsed, not hardcoded

    def test_flat_centre_is_exactly_zero(self):
        points = [(60.0, 19.0), (144.0, 19.0), (220.0, 19.0)]
        values = [surface(x, y, self.edge, self.strength) for x, y in points]
        self.assertEqual(len(values), 3)
        for point, value in zip(points, values):
            with self.subTest(point=point):
                self.assertEqual(value, (0.0, 0.0))

    def test_zero_more_than_one_rim_depth_inside_including_ends(self):
        for x in (20.0, 24.0, 40.0, 144.0, 250.0, 268.0):
            with self.subTest(x=x):
                self.assertGreater(edge_distance(x, 19.0), self.depth)
                self.assertEqual(surface(x, 19.0, self.edge, self.strength), (0.0, 0.0))
        for x in (19.0 + self.depth + 0.5, 269.0 - self.depth - 0.5):
            with self.subTest(x=x):
                self.assertEqual(surface(x, 19.0, self.edge, self.strength), (0.0, 0.0))

    def test_finite_and_within_analytic_bound(self):
        for i in range(0, 289, 2):
            for j in range(0, 39):
                ox, oy = surface(float(i), float(j), self.edge, self.strength)
                with self.subTest(i=i, j=j):
                    self.assertTrue(math.isfinite(ox) and math.isfinite(oy))
                    self.assertLessEqual(math.hypot(ox, oy), self.bound * (1.0 + 1e-9))

    def test_top_bottom_and_left_right_mirror_symmetry(self):
        for lx in (60.0, 144.0, 220.0):
            for d in (0.5, 1.5, 3.0):
                top = surface(lx, d, self.edge, self.strength)
                bottom = surface(lx, PILL[1] - d, self.edge, self.strength)
                with self.subTest(lx=lx, d=d):
                    self.assertAlmostEqual(top[1], -bottom[1], places=6)
                    self.assertAlmostEqual(top[0], bottom[0], places=6)
        for ly in (10.0, 19.0, 28.0):
            left = surface(1.0, ly, self.edge, self.strength)
            right = surface(PILL[0] - 1.0, ly, self.edge, self.strength)
            with self.subTest(ly=ly):
                self.assertAlmostEqual(left[0], -right[0], places=6)
                self.assertAlmostEqual(left[1], right[1], places=6)

    def test_continuity_converges_as_the_step_halves(self):
        # Honest check: the max neighbour difference is a discretisation error in the
        # step, so halving the step must shrink it toward zero. No slope assumption
        # on the refract/normal derivatives (the old bound/depth*1.5 was wrong).
        def max_delta(step):
            xs = [i * step for i in range(int(PILL[0] / step) + 1)]
            worst = 0.0
            for y in (1.0, 5.0, 19.0, 33.0, 37.0):
                prev = surface(xs[0], y, self.edge, self.strength)
                for x in xs[1:]:
                    cur = surface(x, y, self.edge, self.strength)
                    worst = max(worst, math.hypot(cur[0] - prev[0], cur[1] - prev[1]))
                    prev = cur
            return worst
        deltas = [max_delta(s) for s in (2.0, 1.0, 0.5, 0.25)]
        for a, b in zip(deltas, deltas[1:]):
            self.assertLess(b, a)                       # each halving reduces the error
        self.assertLessEqual(deltas[-1], deltas[0] * 0.5)   # tends to zero


class CapsulePatchApplicability(unittest.TestCase):
    def test_patch_applies_to_fresh_pinned_upstream(self):
        source = os.environ.get('CU_HYPRGLASS_SOURCE')
        if not (PATCH.is_file() and source and Path(source).is_dir() and shutil.which('git')):
            self.skipTest('set CU_HYPRGLASS_SOURCE to a pinned hyprglass git repo to run this')
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            subprocess.run(['git', 'init', '-q'], cwd=folder, check=True)
            files = ['src/Shaders.hpp', 'src/GlassLayerSurface.cpp', 'src/GlassRenderer.cpp',
                     'src/GlassRenderer.hpp', 'src/ShaderManager.cpp', 'src/ShaderManager.hpp',
                     'src/Diagnostics.cpp']
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


if __name__ == '__main__':
    unittest.main()
