"""Contract tests for the Shayxo Legacy liquid-glass port.

Purpose: pin the task-selected Legacy optics and ensure the patch/build path
contains the corresponding math. This is a source and numeric model contract,
not a GPU-render proof.

Spec source: Shayxo commit f5e1fb56, /tmp/pill-copy-shayxo-report.md, and
improvements/pill-shayxo-port-design.md.

Task values: band 14 dp; depth 9 dp; blur 0; IOR 1.5; bevelPower 2;
cornerPower 2; dispersion 0.07; specular 0.55; specularPower 6;
counterLight 0.35; edgeLight 1; bevelPeak 0; innerShadow 0.07; legibility
0.6; Fresnel 0.10; lit bevel 3 dp; light (-0.35, -0.94); transparent white
tint; no pre-blur; no mirror.

Documented deviation from true GlassStyle.Chrome at f5e1fb56:

    Parameter       Task value       True Chrome value
    dispersion      0.07             0.010
    specular        0.55             0.50
    Fresnel         0.10             0.08
    innerShadow     0.07             0.06
    legibility      0.6              0.90
    tint            transparent      white, alpha 0.11
    backdropBlur    0                14 dp
    mirror          0                0.08

Band 14 dp, depth 9 dp, fine blur 0, and lit bevel 3 dp agree. The task set
selects default lighting values with Chrome geometry, so those task values win.

Formula resolution: the normalized Snell ratio still varies across the outer
band; only the inner-fade smoothstep factor is 1 for e <= 0.75. At depths
0/0.5/0.75/1 times the 14 px band, the formula yields 0/0.188/0.086/0.
The 1.5 px checkpoint is 0.508922 (the earlier approximately 0.509 figure);
a 0.0001 px scan puts the actual local maximum near 0.515247 at 1.3983 px.
Tests mirror the full equation, not a bend=1 plateau.
"""
import math
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / 'native/hyprglass-shayxo-legacy.patch'
FALLBACK_PATCH = ROOT / 'native/hyprglass-cylindrical-bottle.patch'
PRESET = ROOT / 'native/hyprglass-local-optics.lua'
BUILD_SCRIPT = ROOT / 'scripts/build-glass.py'


def added_patch():
    if not PATCH.is_file():
        return ''
    return '\n'.join(line[1:] for line in PATCH.read_text().splitlines()
                    if line.startswith('+') and not line.startswith('+++'))


def constant(name):
    if not PATCH.is_file():
        return None
    match = re.search(r'^\+const float ' + re.escape(name) + r' = ([0-9.]+);',
                      PATCH.read_text(), re.MULTILINE)
    return float(match.group(1)) if match is not None else None


def lua_value(name):
    if not PRESET.is_file():
        return None
    source = re.sub(r'--[^\n]*', '', PRESET.read_text())
    match = re.search(r'\b' + re.escape(name) + r'\s*=\s*([0-9.]+)', source)
    return float(match.group(1)) if match is not None else None


def smoothstep(edge0, edge1, value):
    t = min(max((value - edge0) / (edge1 - edge0), 0.0), 1.0)
    return t * t * (3.0 - 2.0 * t)


def bevel_slope(e, power=2.0):
    u = 1.0 - min(max(e, 0.002), 0.998)
    up = u ** power
    return u ** (power - 1.0) / max(1.0 - up, 1e-4) ** (1.0 - 1.0 / power)


def snell_shift(slope, ior=1.5):
    inv = 1.0 / math.sqrt(1.0 + slope * slope)
    si, ci = slope * inv, inv
    st = si / max(ior, 1.0001)
    ct = math.sqrt(max(1.0 - st * st, 0.0))
    return (si * ct - ci * st) / max(ci * ct + si * st, 1e-4)


def legacy_bend(depth):
    e = min(max(depth / 14.0, 0.0), 1.0)
    normalized = snell_shift(bevel_slope(e)) / snell_shift(bevel_slope(0.0))
    return min(max(normalized * (1.0 - smoothstep(0.75, 1.0, e))
                   * smoothstep(0.0, 1.5, depth), 0.0), 1.0)


def axis_fade(g_len, epsilon):
    return smoothstep(0.15, 0.80, g_len / (2.0 * epsilon))


def dome_weight(width, height, band):
    aspect = max(width, height) / max(min(width, height), 1e-4)
    inradius = min(width, height) / 2.0
    return smoothstep(1.5, 3.0, aspect) * smoothstep(
        0.75, 1.0, band / max(inradius, 1e-4)
    )


def added_shader_lines(patch_text):
    lines = []
    in_block_comment = False
    for line_number, raw in enumerate(patch_text.splitlines(), 1):
        if raw.startswith(('+++', '---')) or not raw or raw[0] not in ' +-':
            continue
        prefix, code = raw[0], raw[1:]
        if prefix == '-':
            continue
        if in_block_comment:
            if '*/' not in code:
                continue
            code = code.split('*/', 1)[1]
            in_block_comment = False
        while '/*' in code:
            before, after = code.split('/*', 1)
            if '*/' not in after:
                code = before
                in_block_comment = True
                break
            code = before + after.split('*/', 1)[1]
        code = code.split('//', 1)[0]
        if prefix == '+':
            if code.lstrip().startswith('*'):
                continue
            lines.append((line_number, code))
    return lines


def numeric_literals(patch_text):
    pattern = re.compile(
        r'(?<![A-Za-z0-9_.])(?:\d+\.\d*|\.\d+|\d+(?:[eE][+-]?\d+)?)'
        r'(?:[fF])?(?![A-Za-z0-9_.])'
    )
    return [(line, match.group(0))
            for line, code in added_shader_lines(patch_text)
            for match in pattern.finditer(code)]


class ShayxoPortContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shader = added_patch()

    def setUp(self):
        self.assertTrue(
            PATCH.is_file(),
            'shayxo port not landed: native/hyprglass-shayxo-legacy.patch missing',
        )
        self.assertTrue(BUILD_SCRIPT.is_file(), 'scripts/build-glass.py missing')
        build = BUILD_SCRIPT.read_text()
        local_entry = "('local-optics', PATCH)"
        shayxo_entry = "('shayxo Legacy', SHAYXO_PATCH)"
        self.assertIn(
            shayxo_entry,
            build,
            'shayxo port not landed: native/hyprglass-shayxo-legacy.patch '
            'missing from scripts/build-glass.py PATCHES',
        )
        self.assertIn(local_entry, build, 'build order lost local-optics patch')
        self.assertLess(build.index(local_entry), build.index(shayxo_entry),
                        'shayxo patch must follow local-optics in scripts/build-glass.py')
        self.assertTrue(PRESET.is_file(),
                        'active Shayxo Lua profile missing: native/hyprglass-local-optics.lua')
        for name in (
            'SHAYXO_REFRACT_BAND_DP', 'SHAYXO_REFRACT_DEPTH_DP', 'SHAYXO_IOR',
            'SHAYXO_BEVEL_POWER', 'SHAYXO_CORNER_POWER', 'SHAYXO_SPECULAR_POWER',
            'SHAYXO_COUNTER_LIGHT', 'SHAYXO_EDGE_LIGHT', 'SHAYXO_BEVEL_PEAK',
            'SHAYXO_INNER_SHADOW', 'SHAYXO_LEGIBILITY',
        ):
            self.assertIsNotNone(constant(name), 'Shayxo patch missing constant ' + name)
        for name in ('blur_strength', 'chromatic_aberration', 'fresnel_strength',
                     'specular_strength', 'bevel_size'):
            self.assertIsNotNone(lua_value(name), 'active Lua profile missing ' + name)

    def test_selected_task_values_are_bound(self):
        self.assertEqual(constant('SHAYXO_REFRACT_BAND_DP'), 14.0)
        self.assertEqual(constant('SHAYXO_REFRACT_DEPTH_DP'), 9.0)
        self.assertEqual(constant('SHAYXO_IOR'), 1.5)
        self.assertEqual(constant('SHAYXO_BEVEL_POWER'), 2.0)
        self.assertEqual(constant('SHAYXO_CORNER_POWER'), 2.0)
        self.assertEqual(constant('SHAYXO_LEGIBILITY'), 0.6)
        self.assertEqual(lua_value('blur_strength'), 0.0)
        self.assertEqual(lua_value('chromatic_aberration'), 0.07)
        self.assertEqual(lua_value('fresnel_strength'), 0.10)
        self.assertEqual(lua_value('specular_strength'), 0.55)
        self.assertEqual(lua_value('bevel_size'), 3.0)

    def test_transparent_tint_no_preblur_and_no_mirror(self):
        source = PRESET.read_text()
        tint = re.search(r'\btint_color\s*=\s*(0[xX][0-9A-Fa-f]+)', source)
        self.assertIsNotNone(tint, 'active profile is missing tint_color')
        self.assertEqual(tint.group(1).lower(), '0xffffff00')
        self.assertEqual(lua_value('blur_strength'), 0.0)
        self.assertNotRegex(source, r'\bbackdrop_blur\s*=')
        self.assertNotRegex(source, r'\bbackdropBlur\s*=')
        self.assertNotRegex(source, r'\bmirror(?:_strength)?\s*=')
        self.assertNotIn('uMirror', self.shader)

    def test_snell_values_match_the_verified_checkpoints(self):
        self.assertAlmostEqual(snell_shift(bevel_slope(0.0)), 0.9884703910325521, places=12)
        self.assertAlmostEqual(snell_shift(bevel_slope(0.5)), 0.18585864213631031, places=12)
        self.assertAlmostEqual(snell_shift(bevel_slope(0.75)), 0.085439167812735, places=12)
        self.assertAlmostEqual(snell_shift(bevel_slope(1.0)), 0.0006666677037062224, places=12)

    def test_bend_formula_checkpoints_and_non_unit_peak(self):
        checkpoints = ((0.0, 0.0), (0.5, 0.1880265143219547),
                       (0.75, 0.08643573807353562), (1.0, 0.0))
        for e, expected in checkpoints:
            with self.subTest(e=e):
                self.assertAlmostEqual(legacy_bend(e * 14.0), expected, places=12)
        self.assertAlmostEqual(legacy_bend(1.5), 0.5089222661459225, places=12)
        self.assertNotAlmostEqual(legacy_bend(7.0), 1.0)

    def test_dispersion_and_blue_sampling_bound(self):
        aberration = lua_value('chromatic_aberration')
        checkpoint_bend = 0.8
        split = aberration * checkpoint_bend
        self.assertAlmostEqual(split, 0.056, places=12)
        self.assertAlmostEqual(1.0 - split, 0.944, places=12)
        self.assertAlmostEqual(1.0 + split, 1.056, places=12)
        lens_px = 9.0 * 0.85
        max_blue_px = lens_px * (1.0 + aberration)
        self.assertAlmostEqual(lens_px, 7.65, places=12)
        self.assertAlmostEqual(max_blue_px, 8.1855, places=12)
        self.assertIn('float split = chromaticAberration * bend;', self.shader)
        self.assertIn('vec2 pushB = push * (1.0 + split);', self.shader)

    def test_lighting_constants_and_powers(self):
        self.assertEqual(constant('SHAYXO_SPECULAR_POWER'), 6.0)
        self.assertEqual(constant('SHAYXO_COUNTER_LIGHT'), 0.35)
        self.assertEqual(constant('SHAYXO_EDGE_LIGHT'), 1.0)
        self.assertEqual(constant('SHAYXO_INNER_SHADOW'), 0.07)
        self.assertEqual(constant('SHAYXO_BEVEL_PEAK'), 0.0)
        self.assertAlmostEqual(6.0 * 1.6, 9.6, places=12)
        self.assertIn('pow(max(facing, 0.0), SHAYXO_SPECULAR_POWER)', self.shader)
        self.assertIn('pow(max(-facing, 0.0), counterPow)', self.shader)
        self.assertIn('pow(max(1.0 - cosI, 0.0), 5.0)', self.shader)
        counter_power = 6.0 * (
            1.6 + (1.0 - 1.6) * smoothstep(0.35, 1.0, 0.35)
        )
        f0 = ((1.5 - 1.0) / (1.5 + 1.0)) ** 2
        self.assertAlmostEqual(counter_power, 9.6, places=12)
        self.assertAlmostEqual(f0, 0.04, places=12)

    def test_blur_zero_uses_sharp_rgb_and_detail_samples(self):
        self.assertEqual(lua_value('blur_strength'), 0.0)
        self.assertIn('vec3 sharp = vec3(sampleSharp(uvR).r, sampleSharp(uvG).g, sampleSharp(uvB).b);',
                      self.shader)
        self.assertIn('vec3 detailCopy = sampleSharp(uvG);', self.shader)
        self.assertIn('vec3 sampleSharp(vec2 wuv)', self.shader)
        self.assertNotIn('sampleBlurred(uvG)', self.shader)

    def test_legacy_pad_is_12_6_pixels(self):
        depth_px = constant('SHAYXO_REFRACT_DEPTH_DP')
        pad_px = depth_px * 1.4 + max(lua_value('blur_strength'), 0.0)
        self.assertAlmostEqual(pad_px, 12.6, places=12)

    def test_patch_translates_glsl_descending_smoothstep_and_omits_wide_copy(self):
        self.assertIn('(1.0 - smoothstep(0.75, 1.0, e))', self.shader)
        self.assertNotIn('smoothstep(1.0, 0.75, e)', self.shader)
        self.assertNotIn('wideTex', self.shader)
        self.assertIn('color = sharp;', self.shader)
        self.assertIn('toneMappedTint(tintColor, luma(color), SHAYXO_TINT_ADAPTIVITY)', self.shader)

    def test_patch_exposes_single_source_snell_law_and_no_capsule_ripple(self):
        self.assertIn('float bevelSlope(float e, float p)', self.shader)
        self.assertIn('float snellShift(float slope, float ior)', self.shader)
        self.assertIn('vec2 push = n * bend * lens;', self.shader)
        for old in ('capsuleRimDistance', 'capsuleRipplePx', 'capsuleNormal'):
            self.assertNotIn(old, self.shader)

    def test_shader_has_the_rim_snell_normalization_and_both_fades(self):
        self.assertRegex(
            self.shader,
            r'snellShift\(slope,\s*SHAYXO_IOR\)\s*/\s*'
            r'max\(snellShift\(bevelSlope\(0\.0,\s*pw\),\s*SHAYXO_IOR\),\s*1e-4\)',
        )
        self.assertRegex(
            self.shader,
            r'1\.0\s*-\s*smoothstep\(0\.75,\s*1\.0,\s*e\)|'
            r'smoothstep\(1\.0,\s*0\.75,\s*e\)',
        )
        self.assertRegex(self.shader, r'smoothstep\(0\.0,\s*1\.5,\s*depth\)')

    def test_wide_epsilon_and_axis_fade_are_in_the_shader(self):
        self.assertRegex(
            self.shader,
            r'float\s+eps\s*=\s*clamp\(bandPx\s*\*\s*0\.3,\s*1\.0,\s*16\.0\)',
        )
        self.assertIn(
            'float axisFade = smoothstep(0.15, 0.80, gLen / (2.0 * eps));',
            self.shader,
        )

    def test_axis_fade_tends_to_zero_without_a_direction_flip_seam(self):
        epsilon = min(max(14.0 * 0.3, 1.0), 16.0)
        self.assertEqual(epsilon, 4.2)
        for g_len in (0.0, 0.1, 1.0, 1.25):
            with self.subTest(g_len=g_len):
                weight = axis_fade(g_len, epsilon)
                self.assertEqual(weight, 0.0)
                self.assertEqual(weight * 1.0, weight * -1.0)
        self.assertGreater(axis_fade(2.0 * epsilon, epsilon), 0.0)

    def test_outer_inner_fade_is_flat_then_c1_fades_without_midband_peak(self):
        for e in (0.0, 0.1, 0.25, 0.5, 0.75):
            with self.subTest(e=e):
                self.assertEqual(1.0 - smoothstep(0.75, 1.0, e), 1.0)
        depths = (1.5, 2.0, 3.5, 7.0, 10.5, 12.0, 14.0)
        bends = [legacy_bend(depth) for depth in depths]
        self.assertTrue(all(a >= b for a, b in zip(bends, bends[1:])), bends)
        self.assertGreater(bends[0], bends[3])
        h = 0.001
        slope_h = (legacy_bend(14.0) - legacy_bend(14.0 * (1.0 - h))) / h
        half = h / 2.0
        slope_half = (
            legacy_bend(14.0) - legacy_bend(14.0 * (1.0 - half))
        ) / half
        self.assertLess(abs(slope_half), abs(slope_h) * 0.6)

    def test_pill_dome_weight_is_zero(self):
        aspect = 288.0 / 38.0
        band_fraction = 14.0 / 19.0
        self.assertAlmostEqual(aspect, 7.578947368421052, places=14)
        self.assertAlmostEqual(band_fraction, 14.0 / 19.0, places=14)
        self.assertLess(band_fraction, 0.75)
        self.assertEqual(dome_weight(288.0, 38.0, 14.0), 0.0)

    def test_zero_blur_profile_rim_sharp_and_after_push_sample_order(self):
        blur = lua_value('blur_strength')
        self.assertEqual(blur, 0.0)
        # Shayxo radius is uBlur * mat * e. The source default 1.5 dp shows
        # that radius grows with e; the task's zero value removes it everywhere.
        sample_radii = [1.5 * 1.0 * e for e in (0.0, 0.25, 0.5, 1.0)]
        self.assertEqual(sample_radii, [0.0, 0.375, 0.75, 1.5])
        self.assertEqual(sorted(sample_radii), sample_radii)
        self.assertEqual([blur * 1.0 * e for e in (0.0, 0.5, 1.0)],
                         [0.0, 0.0, 0.0])
        for e, expected in ((0.0, 1.0), (0.5, 0.25), (1.0, 0.0)):
            with self.subTest(e=e):
                self.assertAlmostEqual((1.0 - e) ** 2, expected, places=12)

        marker = ('vec3 sharp = vec3(sampleSharp(uvR).r, '
                  'sampleSharp(uvG).g, sampleSharp(uvB).b);')
        self.assertIn(marker, self.shader)
        marker_at = self.shader.index(marker)
        branch_start = self.shader.rfind('#else', 0, marker_at)
        branch_end = self.shader.find('float bevelPx =', marker_at)
        self.assertGreaterEqual(branch_start, 0, 'Legacy sharp sample branch is missing')
        self.assertGreater(branch_end, marker_at, 'Legacy sharp sample branch has no end marker')
        branch = self.shader[branch_start:branch_end]
        for forbidden in ('sampleBlurred', 'blurredAt', 'detailAt', 'frostTex'):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, branch)
        self.assertNotRegex(branch, r'\b(?:for|while)\s*\(')
        push_at = self.shader.index('vec2 push = n * bend * lens;')
        offset_at = self.shader.index('vec2 offsetG = push * invFullSize;')
        uv_at = branch.index('vec2 uvG = uv + offsetG;')
        sample_at = branch.index('sampleSharp(uvG).g')
        self.assertLess(push_at, offset_at)
        self.assertLess(offset_at, marker_at)
        self.assertLess(uv_at, sample_at)
        self.assertIn('float split = chromaticAberration * bend;', self.shader)
        self.assertIn('vec2 pushR = push * (1.0 - split);', self.shader)
        self.assertIn('vec2 pushB = push * (1.0 + split);', self.shader)


# Exact shader literal -> source citation. Removed diff lines and comments are
# excluded; the scanner checks every added GLSL numeric literal. The active Lua
# optical bindings are checked separately by name, so old 0.25 blur / 0.04
# chroma / 0.50 specular values cannot hide behind another use of that number.
SHADER_LITERAL_CITATIONS = {
    '14.0': 'task value list: band 14 dp',
    '9.0': 'task value list: depth 9 dp',
    '1.5': 'task value list: IOR 1.5; report §3.1 bevel floor and rim guard',
    '2.0': 'task value list: bevel/corner power 2; report §3.6 axis denominator',
    '6.0': 'task value list: specularPower 6',
    '0.35': 'task value list/report §3.9: counterLight 0.35 and light x component',
    '1.0': 'task values and report §3.1-§3.9: identity factors and bounds',
    '0.07': 'task value list: dispersion / innerShadow 0.07',
    '0.0': 'task values/report §3.2-§3.9: zero scale, guards, bevelPeak',
    '0.6': 'task value list: legibility 0.6',
    '0.7': 'report §4: inherited highlight chroma 0.7',
    '0.34': 'report §4: inherited detail share 0.34',
    '0.90': 'design §2: source-Chrome adaptivity; design §3g: highlight coefficient',
    '0.94': 'task value list: light y component -0.94',
    '0.001': 'design §3f: normalized sample-coordinate clamp',
    '0.999': 'design §3f: normalized sample-coordinate clamp',
    '0.002': 'report §3.1: bevel slope endpoint clamp',
    '0.998': 'report §3.1: bevel slope endpoint clamp',
    '1e-4': 'report §3.1: Snell/bevel denominator floors',
    '1.0001': 'report §3.1: IOR denominator floor',
    '0.2126': 'design §3h: luma coefficients',
    '0.7152': 'design §3h: luma coefficients',
    '0.0722': 'design §3h: luma coefficients',
    '0.4122214708': 'design §3g: Oklab linear-to-L coefficient',
    '0.5363325363': 'design §3g: Oklab linear-to-L coefficient',
    '0.0514459929': 'design §3g: Oklab linear-to-L coefficient',
    '0.2119034982': 'design §3g: Oklab linear-to-M coefficient',
    '0.6806995451': 'design §3g: Oklab linear-to-M coefficient',
    '0.1073969566': 'design §3g: Oklab linear-to-M coefficient',
    '0.0883024619': 'design §3g: Oklab linear-to-S coefficient',
    '0.2817188376': 'design §3g: Oklab linear-to-S coefficient',
    '0.6299787005': 'design §3g: Oklab linear-to-S coefficient',
    '0.3333333333': 'design §3g: Oklab cube-root exponent',
    '0.2104542553': 'design §3g: Oklab L output coefficient',
    '0.7936177850': 'design §3g: Oklab L output coefficient',
    '0.0040720468': 'design §3g: Oklab L output coefficient',
    '1.9779984951': 'design §3g: Oklab a output coefficient',
    '2.4285922050': 'design §3g: Oklab a output coefficient',
    '0.4505937099': 'design §3g: Oklab a output coefficient',
    '0.0259040371': 'design §3g: Oklab b output coefficient',
    '0.7827717662': 'design §3g: Oklab b output coefficient',
    '0.8086757660': 'design §3g: Oklab b output coefficient',
    '0.3963377774': 'design §3g: Oklab inverse L coefficient',
    '0.2158037573': 'design §3g: Oklab inverse L coefficient',
    '0.1055613458': 'design §3g: Oklab inverse M coefficient',
    '0.0638541728': 'design §3g: Oklab inverse M coefficient',
    '0.0894841775': 'design §3g: Oklab inverse S coefficient',
    '1.2914855480': 'design §3g: Oklab inverse S coefficient',
    '4.0767416621': 'design §3g: Oklab linear RGB output coefficient',
    '3.3077115913': 'design §3g: Oklab linear RGB output coefficient',
    '0.2309699292': 'design §3g: Oklab linear RGB output coefficient',
    '1.2684380046': 'design §3g: Oklab linear RGB output coefficient',
    '2.6097574011': 'design §3g: Oklab linear RGB output coefficient',
    '0.3413193965': 'design §3g: Oklab linear RGB output coefficient',
    '0.0041960863': 'design §3g: Oklab linear RGB output coefficient',
    '0.7034186147': 'design §3g: Oklab linear RGB output coefficient',
    '1.7076147010': 'design §3g: Oklab linear RGB output coefficient',
    '1.20': 'design §3g: Oklab highlight chroma scale',
    '1.10': 'design §3h: toneMappedTint value',
    '0.88': 'design §3h: toneMappedTint value',
    '1.06': 'design §3h: toneMappedTint saturation value',
    '3.0': 'design §3h: source mean tint dot(tint, vec3(1/3)); task bevel width',
    '0.3': 'report §3.6: wide epsilon is 30% of band',
    '16.0': 'report §3.6: wide epsilon upper clamp',
    '1e-5': 'report §3.6: normal denominator floor',
    '0.15': 'report §3.6: axisFade lower edge',
    '0.80': 'report §3.6: axisFade upper edge',
    '0.75': 'report §3.2: inner fade; report §3.6: dome threshold',
    '0.85': 'report §3.2: element-size lens scale lower endpoint',
    '1.25': 'report §3.2: element-size lens scale upper endpoint; design §3h',
    '0.02': 'design §3h: detailWeight lower edge',
    '0.10': 'design §3h: detailWeight upper edge',
    '4.0': 'report §3.10/design §3h: local contrast multiplier',
    '0.9': 'report §3.10/design §3h: source tint strength factor',
    '0.25': 'report §3.10/design §3h: additive legibility coefficient',
    '0.95': 'report §3.10: strength clamp upper bound',
    '1e-3': 'design §3b: optical-depth band denominator floor',
    '2.2': 'report §3.9: innerLine width multiplier',
    '1.15': 'design §3g: inner-shadow material mix endpoint',
    '5.0': 'report §3.9: Schlick fifth power',
    '1.6': 'report §3.9: counter-lobe power multiplier',
    '0.5': 'report §3.9: directional edge-line half factor',
}

PROFILE_VALUE_CITATIONS = {
    'blur_strength': (0.0, 'task value list: no fine blur or pre-blur'),
    'chromatic_aberration': (0.07, 'task value list: dispersion 0.07'),
    'specular_strength': (0.55, 'task value list: specular 0.55'),
    'fresnel_strength': (0.10, 'task value list: Fresnel 0.10'),
    'bevel_size': (3.0, 'task value list: lit bevel 3 dp'),
}


class ShayxoNoInventedConstants(unittest.TestCase):
    def test_shader_literals_and_bound_profile_values_are_traced(self):
        patch_path = PATCH if PATCH.is_file() else FALLBACK_PATCH
        self.assertTrue(
            patch_path.is_file(),
            'shayxo port not landed: native/hyprglass-shayxo-legacy.patch missing; '
            'active fallback native/hyprglass-cylindrical-bottle.patch also missing',
        )
        patch_text = patch_path.read_text()
        findings = [
            'line {}: {} has no source citation'.format(line, value)
            for line, value in numeric_literals(patch_text)
            if value not in SHADER_LITERAL_CITATIONS
        ]
        if PRESET.is_file():
            for name, (expected, citation) in PROFILE_VALUE_CITATIONS.items():
                pattern = re.compile(
                    r'\b' + re.escape(name) + r'\s*=\s*([0-9.]+)'
                )
                for line_number, line in enumerate(PRESET.read_text().splitlines(), 1):
                    match = pattern.search(line.split('--', 1)[0])
                    if match and float(match.group(1)) != expected:
                        findings.append(
                            'Lua line {}: {}={} is untraced; task value {} ({})'.format(
                                line_number, name, match.group(1), expected, citation
                            )
                        )
            if patch_path == FALLBACK_PATCH and re.search(
                    r'\brefractionStrength\s*\*\s*50(?:\.0)?', patch_text):
                old_gain = re.search(
                    r'\brefraction_strength\s*=\s*([0-9.]+)',
                    '\n'.join(line.split('--', 1)[0] for line in PRESET.read_text().splitlines()),
                )
                if old_gain:
                    line_number = next(
                        n for n, line in enumerate(PRESET.read_text().splitlines(), 1)
                        if re.search(r'\brefraction_strength\s*=', line.split('--', 1)[0])
                    )
                    findings.append(
                        'Lua line {}: refraction_strength={} is an untraced old gain; '
                        'the active shader still multiplies it by 50 px'.format(
                            line_number, old_gain.group(1)
                        )
                    )
        self.assertEqual(
            findings,
            [],
            'uncited constants or old optical parameter values:\n' + '\n'.join(findings),
        )


if __name__ == '__main__':
    unittest.main()
