"""C45 numeric contract for the capsule lighting branch (model, NOT a GPU proof).

Mirrors the patched Shaders.hpp lighting math and links it to the real patch text:
- capsuleNormal from the closest point on the inset rectangle;
- Fresnel = (1 - f0) * (1 - Nz)^5 * fresnelStrength (f0 from IOR 1.45), so the flat
  centre contributes nothing (no constant white plate);
- specular = pow(max(dot(N, normalize(normalize(vec3(lightDir(angle)*0.85, 0.55))
  + vec3(0,0,1))), 0), 24) * (1 - Nz) * specularStrength * 0.32.
Strengths are parsed from the real Lua preset. These checks prove the model and the
patch string contract, not that the shader renders.
"""
import math
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / 'native/hyprglass-capsule.patch'
PRESET = ROOT / 'native/hyprglass-indicator.lua'
PILL = (288.0, 38.0)
IOR = 1.45
ANGLE = 0.0            # lua has no specular_angle; upstream default


def read_preset():
    text = PRESET.read_text()
    fresnel = re.search(r'fresnel_strength\s*=\s*([0-9.]+)', text)
    specular = re.search(r'specular_strength\s*=\s*([0-9.]+)', text)
    if not fresnel or not specular:
        raise RuntimeError('preset is missing fresnel_strength / specular_strength')
    return float(fresnel.group(1)), float(specular.group(1))


def light_dir(angle_deg):
    """Upstream Shaders.hpp:240-243: (sin a, -cos a); 0 = from the top."""
    a = math.radians(angle_deg)
    return math.sin(a), -math.cos(a)


def normal(lx, ly, size=PILL):
    r = min(size[1] * 0.5, min(size) * 0.5)
    cx = min(max(lx, r), max(r, size[0] - r))
    cy = min(max(ly, r), max(r, size[1] - r))
    dx, dy = lx - cx, ly - cy
    dist = math.hypot(dx, dy)
    n2 = (dx / dist, dy / dist) if dist > 1e-5 else (0.0, 0.0)
    s = min(dist / max(1e-5, r), 1.0)
    return n2[0] * s, n2[1] * s, math.sqrt(max(0.0, 1.0 - s * s))


def f0():
    return ((IOR - 1.0) / (IOR + 1.0)) ** 2


def fresnel(nz, strength):
    return (1.0 - f0()) * (1.0 - min(max(nz, 0.0), 1.0)) ** 5 * strength


def specular(n3, strength, angle=ANGLE):
    lx, ly = light_dir(angle)
    llen = math.hypot(lx * 0.85, ly * 0.85, 0.55)
    light = (lx * 0.85 / llen, ly * 0.85 / llen, 0.55 / llen)
    hx, hy, hz = light[0], light[1], light[2] + 1.0
    hlen = math.hypot(hx, hy, hz)
    half = (hx / hlen, hy / hlen, hz / hlen)
    dot = max(n3[0] * half[0] + n3[1] * half[1] + n3[2] * half[2], 0.0)
    return dot ** 24 * (1.0 - n3[2]) * strength * 0.32


class CapsuleLighting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fresnel_strength, cls.specular_strength = read_preset()
        cls.patch = PATCH.read_text()

    def test_strengths_are_parsed_from_lua(self):
        self.assertGreater(self.fresnel_strength, 0.0)
        self.assertGreater(self.specular_strength, 0.0)
        self.assertEqual((self.fresnel_strength, self.specular_strength), read_preset())

    def test_normals_are_unit_and_finite(self):
        for i in range(0, 289, 3):
            for j in range(0, 39, 2):
                with self.subTest(i=i, j=j):
                    n3 = normal(float(i), float(j))
                    self.assertTrue(all(math.isfinite(v) for v in n3))
                    self.assertAlmostEqual(math.hypot(*n3), 1.0, places=9)

    def test_flat_interior_lighting_is_zero(self):
        for x, y in ((60.0, 19.0), (144.0, 19.0), (220.0, 19.0)):
            n3 = normal(x, y)
            with self.subTest(point=(x, y)):
                self.assertAlmostEqual(n3[2], 1.0, places=9)          # flat => normal up
                self.assertEqual(fresnel(n3[2], self.fresnel_strength), 0.0)
                self.assertEqual(specular(n3, self.specular_strength), 0.0)

    def test_grazing_fresnel_is_bounded_and_max_at_the_rim(self):
        bound = (1.0 - f0()) * self.fresnel_strength
        for i in range(0, 289, 2):
            for j in range(0, 39):
                n3 = normal(float(i), float(j))
                with self.subTest(i=i, j=j):
                    self.assertLessEqual(fresnel(n3[2], self.fresnel_strength), bound + 1e-12)
        self.assertAlmostEqual(fresnel(0.0, self.fresnel_strength), bound, places=12)

    def test_lighting_is_continuous_under_step_halving(self):
        def max_delta(step):
            worst = 0.0
            prev = None
            x = 0.0
            while x <= PILL[0]:
                n3 = normal(x, 1.0)
                value = fresnel(n3[2], self.fresnel_strength) + specular(n3, self.specular_strength)
                if prev is not None:
                    worst = max(worst, abs(value - prev))
                prev, x = value, x + step
            return worst
        deltas = [max_delta(s) for s in (2.0, 1.0, 0.5, 0.25)]
        for a, b in zip(deltas, deltas[1:]):
            self.assertLess(b, a)
        self.assertLessEqual(deltas[-1], deltas[0] * 0.5)

    @staticmethod
    def local_from_uv(uv, full, offset):
        """Invert localPx = uv*fullSize - glassBoxOffsetPx (the shader's own mapping)."""
        return uv[0] * full[0] - offset[0], uv[1] * full[1] - offset[1]

    def test_lighting_is_padding_and_offset_invariant(self):
        # Build real UV/fullSize/offset triples and derive localPx, instead of
        # comparing a normal with itself: two different paddings/offsets must map
        # to the SAME box-local point and therefore the SAME lighting.
        local = (144.0, 19.0)
        scenarios = ((1280.0, 720.0, 500.0, 10.0), (1920.0, 1080.0, 700.0, 60.0))
        derived = []
        for full_w, full_h, off_x, off_y in scenarios:
            uv = ((local[0] + off_x) / full_w, (local[1] + off_y) / full_h)
            derived.append(self.local_from_uv(uv, (full_w, full_h), (off_x, off_y)))
        for got in derived:
            self.assertAlmostEqual(got[0], local[0], places=6)
            self.assertAlmostEqual(got[1], local[1], places=6)
        values = []
        for got in derived:
            n3 = normal(*got)
            values.append((fresnel(n3[2], self.fresnel_strength), specular(n3, self.specular_strength)))
        self.assertEqual(values[0], values[1], 'same local point must light identically')
        self.assertEqual(values[0], (fresnel(normal(*local)[2], self.fresnel_strength),
                                     specular(normal(*local), self.specular_strength)))

    def test_patch_contract_indicator_capsule_uniform_scope(self):
        # 1) the shader branch is driven by an explicit uniform, not a size heuristic
        self.assertIn('uniform int indicatorCapsule;', self.patch)
        self.assertIn('bool capsuleMaterial = indicatorCapsule == 1;', self.patch)
        self.assertIn('glUniform1i(uniforms.indicatorCapsule, mask && mask->indicatorCapsule ? 1 : 0)', self.patch)
        self.assertNotIn('glassBoxSizePx.x < fullSize', self.patch)   # heuristic removed
        # 2) the uniform source is bound to maskInfo.indicatorCapsule only
        self.assertIn('maskInfo.indicatorCapsule = true;', self.patch)
        source = self.patch[self.patch.index('maskInfo.indicatorCapsule = true;') - 600:
                            self.patch.index('maskInfo.indicatorCapsule = true;')]
        self.assertIn('namespace == "computer-use-indicator"', source)   # valid namespace
        self.assertIn('region.empty()', source)                          # valid region only
        self.assertIn('extents.w > 0.0 && extents.h > 0.0', source)      # finite/positive
        # 3) the default (non-capsule) path is intact
        self.assertIn('if (!capsuleMaterial)', self.patch)

    def test_directional_highlight_is_not_symmetric_up_down(self):
        for x in (60.0, 144.0, 220.0):
            top = normal(x, 1.0)
            bottom = normal(x, PILL[1] - 1.0)
            with self.subTest(x=x):
                self.assertGreater(specular(top, self.specular_strength),
                                   specular(bottom, self.specular_strength))
                self.assertAlmostEqual(top[1], -bottom[1], places=9)   # mirrored normals
                self.assertAlmostEqual(fresnel(top[2], self.fresnel_strength),
                                       fresnel(bottom[2], self.fresnel_strength), places=12)

    def test_patch_string_contract_links_model_to_shader(self):
        for needle in ('capsuleNormal',
                       'float f0 = pow((1.45 - 1.0) / (1.45 + 1.0), 2.0)',
                       'fresnel = (1.0 - f0) * pow(grazing, 5.0) * fresnelStrength',
                       'pow(max(dot(materialNormal, halfVector), 0.0), 24.0)',
                       'float curvature = 1.0 - materialNormal.z',
                       '* specularStrength * 0.32',
                       'lightDir(specularAngle)'):
            with self.subTest(needle=needle):
                self.assertIn(needle, self.patch)


if __name__ == '__main__':
    unittest.main()
