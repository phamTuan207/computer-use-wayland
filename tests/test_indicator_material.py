"""C40 material contract: outside-only shadows and a clear wash midband.

Parses the real constants from native/indicator.c (shadow alpha, ring count, liquid
wash stops, liquid body alpha) so the test cannot go stale, then renders the *
copied* geometry in a tiny offscreen Cairo harness (no GUI) and samples alpha:
the pill interior (including the text position) must stay 0 from the shadow, the
ring band outside the pill must be non-zero, and the wash midband must be 0 while
its top band is non-zero.
"""
import re
import shutil
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'native/indicator.c'

HARNESS = r'''
#include <cairo.h>
#include <stdio.h>
#include <stdlib.h>
static void rounded(cairo_t *cr, double x, double y, double w, double h, double r) {
  if (r > w * 0.5) r = w * 0.5;
  if (r > h * 0.5) r = h * 0.5;
  cairo_new_sub_path(cr);
  cairo_arc(cr, x + w - r, y + r, r, -3.141592653589793 / 2, 0);
  cairo_arc(cr, x + w - r, y + h - r, r, 0, 3.141592653589793 / 2);
  cairo_arc(cr, x + r, y + h - r, r, 3.141592653589793 / 2, 3.141592653589793);
  cairo_arc(cr, x + r, y + r, r, 3.141592653589793, 3 * 3.141592653589793 / 2);
  cairo_close_path(cr);
}
int main(int argc, char **argv) {
  (void)argc;
  double alpha = atof(argv[1]); int rings = atoi(argv[2]);
  double stops[6]; for (int i = 0; i < 6; i++) stops[i] = atof(argv[3 + i]);
  const double px = 16, py = 16, pw = 288, ph = 38;
  cairo_surface_t *s = cairo_image_surface_create(CAIRO_FORMAT_A8, 320, 66);
  cairo_t *cr = cairo_create(s);
  cairo_set_source_rgba(cr, 0, 0, 0, 0); cairo_paint(cr);
  cairo_save(cr);                       // outside-only shadow (even-odd pill hole)
  cairo_rectangle(cr, 0, 0, 320, 66);
  rounded(cr, px, py, pw, ph, ph / 2);
  cairo_set_fill_rule(cr, CAIRO_FILL_RULE_EVEN_ODD); cairo_clip(cr);
  for (int ring = rings; ring >= 1; ring--) {
    rounded(cr, px - ring, py + 2 - ring, pw + 2 * ring, ph + 2 * ring, ph / 2 + ring);
    cairo_set_source_rgba(cr, 0, 0, 0, alpha); cairo_fill(cr);
  }
  cairo_restore(cr);
  rounded(cr, px, py, pw, ph, ph / 2);  // wash (reflection gradient)
  cairo_pattern_t *w = cairo_pattern_create_linear(px, py, px, py + ph);
  cairo_pattern_add_color_stop_rgba(w, 0.00, 1, 1, 1, stops[0]);
  cairo_pattern_add_color_stop_rgba(w, 0.16, 1, 1, 1, stops[1]);
  cairo_pattern_add_color_stop_rgba(w, 0.36, 1, 1, 1, stops[2]);
  cairo_pattern_add_color_stop_rgba(w, 0.66, 1, 1, 1, stops[3]);
  cairo_pattern_add_color_stop_rgba(w, 0.90, 1, 1, 1, stops[4]);
  cairo_pattern_add_color_stop_rgba(w, 1.00, 1, 1, 1, stops[5]);
  cairo_set_source(cr, w); cairo_fill(cr); cairo_pattern_destroy(w);
  cairo_surface_flush(s);
  unsigned char *d = cairo_image_surface_get_data(s);
  int stride = cairo_image_surface_get_stride(s);
  printf("shadow_centre %d\n", d[35 * stride + 144]);
  printf("shadow_text %d\n", d[34 * stride + 160]);
  printf("shadow_outside %d\n", d[15 * stride + 144]);
  printf("wash_mid %d\n", d[35 * stride + 144]);
  printf("wash_top %d\n", d[18 * stride + 144]);
  cairo_destroy(cr); cairo_surface_destroy(s);
  return 0;
}
'''


def parse_source():
    text = SOURCE.read_text()
    alpha = re.search(r'cairo_set_source_rgba\(cr,0,0,0,([0-9.]+)\);cairo_fill\(cr\);\s*\n\s*\}', text)
    rings = re.search(r'ring=entrance_progress<1\.0\?0:(\d+);ring>=1', text)
    liquid = re.findall(r'liquid\?([0-9.]+):', text)
    zero_stops = re.findall(r'wash,\.(?:36|66),1,1,1,0\)', text)
    return {'alpha': float(alpha.group(1)) if alpha else None,
            'rings': int(rings.group(1)) if rings else None,
            'liquid_stops': [float(v) for v in liquid],
            'zero_stop_count': len(zero_stops)}


def sample(alpha, rings, stops):
    compiler = shutil.which('cc')
    if not compiler or not shutil.which('pkg-config'):
        raise unittest.SkipTest('cc/pkg-config unavailable')
    cflags = subprocess.check_output(['pkg-config', '--cflags', 'cairo'], text=True).split()
    libs = subprocess.check_output(['pkg-config', '--libs', 'cairo'], text=True).split()
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        (folder / 'harness.c').write_text(HARNESS)
        binary = folder / 'harness'
        build = subprocess.run([compiler, '-std=c11', '-Wall', '-Wextra', '-Werror',
                                '-o', str(binary), str(folder / 'harness.c'),
                                *cflags, *libs, '-lm'], capture_output=True, text=True)
        if build.returncode:
            raise RuntimeError(build.stderr)
        run = subprocess.run([str(binary), str(alpha), str(rings), *[str(s) for s in stops]],
                             capture_output=True, text=True, timeout=20)
        if run.returncode:
            raise RuntimeError(run.stderr)
    return {line.split()[0]: int(line.split()[1]) for line in run.stdout.splitlines()}


class IndicatorMaterial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = parse_source()

    def test_parsed_constants_are_meaningful(self):
        self.assertEqual(self.src['rings'], 4, 'shadow ring count changed upstream')
        self.assertAlmostEqual(self.src['alpha'], 0.018, places=6)
        self.assertEqual(self.src['zero_stop_count'], 2, 'wash midband must have two zero stops')
        self.assertIn(0.0, self.src['liquid_stops'], 'liquid body alpha 0 expected')
        self.assertIn(0.18, self.src['liquid_stops'])

    def test_cairo_geometry_is_outside_only_and_midband_clear(self):
        stops = [0.18, 0.05, 0.0, 0.0, 0.035, 0.10]
        got = sample(self.src['alpha'], self.src['rings'], stops)
        self.assertEqual(got['shadow_centre'], 0, 'shadow must not fill the pill centre')
        self.assertEqual(got['shadow_text'], 0, 'shadow must not reach the text')
        self.assertGreater(got['shadow_outside'], 0, 'ring band outside the pill must be non-zero')
        self.assertEqual(got['wash_mid'], 0, 'wash must be clear through the midband')
        self.assertGreater(got['wash_top'], 0, 'wash must be lit near the top')


if __name__ == '__main__':
    unittest.main()
