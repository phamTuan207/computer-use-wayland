"""The static Legacy port uses one Snell field and contains no ripple law."""
from pathlib import Path
import unittest

PATCH = (Path(__file__).resolve().parents[1] /
         'native/hyprglass-shayxo-legacy.patch').read_text()
ADDED = '\n'.join(line[1:] for line in PATCH.splitlines()
                  if line.startswith('+') and not line.startswith('+++'))


class ShayxoLegacyNoRippleContract(unittest.TestCase):
    def test_patch_does_not_add_a_ripple_field(self):
        for token in ('capsuleRipple', 'capsuleRim', 'rimOffsetPx', 'tangent * ripple', 'sin('):
            with self.subTest(token=token):
                self.assertNotIn(token, ADDED)

    def test_patch_uses_the_single_snell_displacement(self):
        self.assertIn('float bend = snellShift(slope, SHAYXO_IOR)', ADDED)
        self.assertIn('vec2 push = n * bend * lens;', ADDED)
        self.assertNotIn('baseOffset +=', ADDED)

    def test_old_capsule_ripple_patch_is_not_the_active_contract(self):
        self.assertIn('native/hyprglass-shayxo-legacy.patch', str(
            Path(__file__).resolve().parents[1] / 'native/hyprglass-shayxo-legacy.patch'))
        self.assertNotIn('capsuleRimDistance', ADDED)


if __name__ == '__main__':
    unittest.main()
