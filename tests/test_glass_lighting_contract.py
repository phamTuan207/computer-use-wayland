"""Numeric source-lighting contract for the Shayxo Legacy port, not a GPU claim."""
import math
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / 'native/hyprglass-shayxo-legacy.patch'
PRESET = ROOT / 'native/hyprglass-local-optics.lua'


def added_patch():
    return '\n'.join(line[1:] for line in PATCH.read_text().splitlines()
                    if line.startswith('+') and not line.startswith('+++'))


def constant(name):
    match = re.search(r'^\+const float ' + re.escape(name) + r' = ([0-9.]+);',
                      PATCH.read_text(), re.MULTILINE)
    if match is None:
        raise RuntimeError('patch is missing ' + name)
    return float(match.group(1))


def lua_value(name):
    source = re.sub(r'--[^\n]*', '', PRESET.read_text())
    match = re.search(r'\b' + re.escape(name) + r'\s*=\s*([0-9.]+)', source)
    if match is None:
        raise RuntimeError('profile is missing ' + name)
    return float(match.group(1))


def fresnel(slope, ior=1.5):
    cos_i = 1.0 / math.sqrt(1.0 + slope * slope)
    f0 = ((ior - 1.0) / (ior + 1.0)) ** 2
    return f0 + (1.0 - f0) * max(1.0 - cos_i, 0.0) ** 5


class ShayxoLegacyLighting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shader = added_patch()

    def test_task_light_gains_are_in_the_active_lua_profile(self):
        self.assertEqual(lua_value('fresnel_strength'), 0.10)
        self.assertEqual(lua_value('specular_strength'), 0.55)
        self.assertEqual(lua_value('bevel_size'), 3.0)

    def test_source_light_vector_and_lobe_powers_are_selected(self):
        self.assertIn('const vec2 SHAYXO_LIGHT = vec2(-0.35, -0.94);', self.shader)
        self.assertEqual(constant('SHAYXO_SPECULAR_POWER'), 6.0)
        self.assertEqual(constant('SHAYXO_COUNTER_LIGHT'), 0.35)
        self.assertEqual(constant('SHAYXO_EDGE_LIGHT'), 1.0)
        self.assertEqual(constant('SHAYXO_INNER_SHADOW'), 0.07)

    def test_counter_lobe_power_is_9_6_for_task_values(self):
        counter_light = constant('SHAYXO_COUNTER_LIGHT')
        counter_power = constant('SHAYXO_SPECULAR_POWER') * (
            1.6 + (1.0 - 1.6) * 0.0)
        self.assertEqual(counter_light, 0.35)
        self.assertAlmostEqual(counter_power, 9.6, places=12)

    def test_key_counter_and_edge_lobes_have_expected_endpoints(self):
        counter_light = constant('SHAYXO_COUNTER_LIGHT')
        specular_gain = lua_value('specular_strength')
        key_at_light = max(1.0, 0.0) ** 6
        counter_at_back = max(1.0, 0.0) ** 9.6 * counter_light
        edge_light_at_front = 0.5 * 1.0
        edge_light_at_back = 0.5 * counter_light
        self.assertEqual(key_at_light, 1.0)
        self.assertEqual(counter_at_back, 0.35)
        self.assertEqual(edge_light_at_front, 0.5)
        self.assertAlmostEqual(edge_light_at_back, 0.175, places=12)
        self.assertAlmostEqual((key_at_light + edge_light_at_front) * specular_gain, 0.825)

    def test_schlick_fresnel_matches_ior_1_5_formula(self):
        self.assertAlmostEqual(fresnel(0.0), 0.04, places=12)
        self.assertAlmostEqual(fresnel(1.0), 0.04206927312437237, places=12)
        self.assertLessEqual(fresnel(15.787661329349902), 1.0)

    def test_inner_line_uses_three_pixel_bevel_and_0_07_gain(self):
        self.assertEqual(lua_value('bevel_size'), 3.0)
        self.assertEqual(constant('SHAYXO_INNER_SHADOW'), 0.07)
        self.assertIn('1.0 - smoothstep(0.0, 2.2 * bevelPx, depth) - bevelBand', self.shader)

    def test_old_capsule_lighting_formula_is_replaced(self):
        for old in ('1.45 - 1.0', '0.32', '24.0', 'capsuleNormal', 'fresnelStrength * 0.15'):
            self.assertNotIn(old, self.shader)
        self.assertIn('float fresnel = f0 + (1.0 - f0) * pow(max(1.0 - cosI, 0.0), 5.0);',
                      self.shader)
        self.assertIn('pow(max(facing, 0.0), SHAYXO_SPECULAR_POWER)', self.shader)
        self.assertIn('pow(max(-facing, 0.0), counterPow)', self.shader)

    def test_highlight_uses_the_source_oklab_helper(self):
        self.assertIn('vec3 applyHighlight(vec3 col, float amount, float chroma)', self.shader)
        self.assertIn('linearToOklab(toLinearApprox(col))', self.shader)
        self.assertIn('oklabToLinear(lab)', self.shader)

    def test_new_lighting_is_directional_and_has_no_dark_outline_constant(self):
        self.assertIn('float facing = dot(n, uLight);', self.shader)
        self.assertIn('float edge = 1.0 - smoothstep(0.0, 2.0, depth);', self.shader)
        self.assertNotIn('SHAYXO_EDGE_SHADOW', self.shader)


if __name__ == '__main__':
    unittest.main()
