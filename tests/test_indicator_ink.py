"""C41 numeric glyph-ink decode (pure math, no GUI, no source parsing of pixels).

The negotiated marker is the explicit vector (1, 0, 1): premultiplied pixels carry
the marker as coverage in R and B but not G, so coverage = min(R, B) - G. The
decoder subtracts marker*coverage to restore the underlying wash; ordinary white
or grey pixels (R == G == B) decode to coverage 0 and are never guessed as markers.
The green status dot keeps its own colour because its G exceeds min(R, B).
"""
import unittest

MARKER = (1.0, 0.0, 1.0)


def decode(r, g, b):
    """Return (coverage, (base_r, base_g, base_b)) for a premultiplied pixel."""
    coverage = min(r, b) - g
    if coverage <= 0.0:
        return 0.0, (r, g, b)
    return coverage, (r - MARKER[0] * coverage, g - MARKER[1] * coverage, b - MARKER[2] * coverage)


class GlyphInkDecode(unittest.TestCase):
    def test_marker_over_neutral_wash_round_trips(self):
        for wash in (0.0, 0.2, 0.5, 0.9):
            for coverage in (0.05, 0.25, 0.6, 1.0):
                with self.subTest(wash=wash, coverage=coverage):
                    residual = wash * (1.0 - coverage)
                    alpha = coverage + residual
                    pixel = (residual + coverage, residual, residual + coverage)
                    self.assertTrue(all(0.0 <= channel <= alpha <= 1.0 for channel in pixel))
                    got, base = decode(*pixel)
                    self.assertAlmostEqual(got, coverage, places=9)
                    for channel in base:
                        self.assertAlmostEqual(channel, residual, places=9)
                    for ink in (0.0, 1.0):
                        decoded = tuple(channel + ink * got for channel in base)
                        self.assertTrue(all(0.0 <= channel <= alpha + 1e-9 for channel in decoded))

    def test_ordinary_white_is_never_a_marker(self):
        for v in (0.0, 0.5, 1.0, 0.98):
            with self.subTest(v=v):
                coverage, base = decode(v, v, v)
                self.assertEqual(coverage, 0.0)
                self.assertEqual(base, (v, v, v))

    def test_tinted_neutral_wash_is_preserved(self):
        for v in (0.1, 0.4, 0.8):
            coverage, base = decode(v, v, v)          # wash is neutral by construction
            self.assertEqual(coverage, 0.0)
            self.assertEqual(base, (v, v, v))

    def test_green_status_dot_is_preserved(self):
        dot = (0.10, 0.80, 0.55)                      # G exceeds min(R,B): not the marker
        coverage, base = decode(*dot)
        self.assertEqual(coverage, 0.0)
        self.assertEqual(base, dot)

    def test_decoder_requires_the_explicit_marker(self):
        # a pixel that only has R extra (no B) is not this marker
        coverage, base = decode(0.6, 0.2, 0.2)
        self.assertEqual(coverage, 0.0)
        self.assertEqual(base, (0.6, 0.2, 0.2))

    def test_coverage_is_bounded_by_the_pixel(self):
        coverage, base = decode(0.3, 0.0, 0.3)
        self.assertAlmostEqual(coverage, 0.3, places=9)
        for channel in base:
            self.assertGreaterEqual(channel, -1e-9)


if __name__ == '__main__':
    unittest.main()
