"""Compile the entrance.h C fixture and assert C35 geometry (no GUI).

Checks: first frame is a small protrusion touching y0 (NOT the final pill),
width A < 288 while B == 288, attachment is continuous (cairo_in_fill true at
several y through the pill), a real gap opens in the detach phase, final progress
is exactly the capsule, and the eased duration endpoints are 0/1000 ms.
"""
import math
import shutil
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / 'native/entrance.h'
FINAL = (16.0, 16.0, 304.0, 54.0)
PROGRESS = (0.0, 0.25, 0.5, 0.7, 0.9, 1.0)

FIXTURE = r'''
#include "entrance.h"
#include <stdio.h>
int main(void) {
  const int modes[] = {0, 1, 2};
  const double ps[] = {0.0, 0.25, 0.5, 0.7, 0.9, 1.0};
  cairo_surface_t *s = cairo_image_surface_create(CAIRO_FORMAT_ARGB32, 320, 66);
  cairo_t *cr = cairo_create(s);
  for (unsigned m = 0; m < 3; m++)
    for (unsigned p = 0; p < 6; p++) {
      cairo_new_path(cr);
      entrance_shape(cr, 16.0, 16.0, 288.0, 38.0, ps[p], modes[m]);
      double x0, y0, x1, y1;
      cairo_path_extents(cr, &x0, &y0, &x1, &y1);
      printf("ext %d %.3f %.4f %.4f %.4f %.4f\n", modes[m], ps[p], x0, y0, x1, y1);
    }
  // continuity: is the vertical centre line inside the path at every y up to the pill?
  const double tap[] = {0.0, 0.25, 0.5, 0.7, 0.9};
  for (unsigned m = 1; m <= 2; m++)
    for (unsigned p = 0; p < 5; p++) {
      double prog = tap[p];
      double bottom = 2.0 + 52.0 * prog;             // pill bottom = py*p + (2+(ph-2)p)
      int total = (int)floor(bottom);
      int inside = 0;
      for (int y = 0; y < total; y++) {
        cairo_new_path(cr);
        entrance_shape(cr, 16.0, 16.0, 288.0, 38.0, prog, m);
        if (cairo_in_fill(cr, 160.0, (double)y + 0.5)) inside++;
      }
      printf("fill %d %.3f %d %d\n", m, prog, inside, total);
    }
  printf("ease 0 %.4f 500 %.4f 1000 %.4f\n", entrance_progress_ms(0.0),
         entrance_progress_ms(500.0), entrance_progress_ms(1000.0));
  cairo_destroy(cr);
  cairo_surface_destroy(s);
  return 0;
}
'''


def run_fixture():
    compiler = shutil.which('cc')
    if not compiler or not shutil.which('pkg-config'):
        raise unittest.SkipTest('cc/pkg-config unavailable')
    cflags = subprocess.check_output(['pkg-config', '--cflags', 'cairo'], text=True).split()
    libs = subprocess.check_output(['pkg-config', '--libs', 'cairo'], text=True).split()
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        shutil.copy(HEADER, folder / 'entrance.h')
        (folder / 'fixture.c').write_text(FIXTURE)
        binary = folder / 'fixture'
        build = subprocess.run([compiler, '-std=c11', '-Wall', '-Wextra', '-Werror', '-I', str(folder),
                                '-o', str(binary), str(folder / 'fixture.c'), *cflags, *libs, '-lm'],
                               capture_output=True, text=True)
        if build.returncode:
            raise RuntimeError(build.stderr)
        run = subprocess.run([str(binary)], capture_output=True, text=True, timeout=30)
        if run.returncode:
            raise RuntimeError(run.stderr)
    ext, fill, ease = {}, {}, {}
    for line in run.stdout.splitlines():
        parts = line.split()
        if parts[0] == 'ext':
            ext[(int(parts[1]), float(parts[2]))] = tuple(float(v) for v in parts[3:7])
        elif parts[0] == 'fill':
            fill[(int(parts[1]), float(parts[2]))] = (int(parts[3]), int(parts[4]))
        elif parts[0] == 'ease':
            ease = {'0': float(parts[2]), '500': float(parts[4]), '1000': float(parts[6])}
    return ext, fill, ease


class EntranceGeometry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ext, cls.fill, cls.ease = run_fixture()

    def test_extents_finite_and_inside_surface(self):
        self.assertEqual(len(self.ext), 3 * len(PROGRESS))
        for (mode, prog), box in self.ext.items():
            with self.subTest(mode=mode, progress=prog):
                x0, y0, x1, y1 = box
                self.assertTrue(all(math.isfinite(v) for v in box))
                self.assertGreaterEqual(x0, 0.0)
                self.assertGreaterEqual(y0, 0.0)
                self.assertLessEqual(x1, 320.0)
                self.assertLessEqual(y1, 66.0)
                self.assertLess(x0, x1)

    def test_first_frame_is_small_protrusion_not_final_pill(self):
        for mode in (1, 2):
            x0, y0, x1, y1 = self.ext[(mode, 0.0)]
            with self.subTest(mode=mode):
                self.assertLessEqual(y0, 0.01)              # touches output top
                self.assertLessEqual(y1, 3.0)              # NOT the final bottom 54
                self.assertLess(y1, 54.0)
                self.assertLess(x0, x1)
                self.assertGreaterEqual(x0, 16.0)
                self.assertLessEqual(x1, 304.0)
        narrow = self.ext[(1, 0.0)]
        self.assertLess(narrow[2] - narrow[0], 288.0)               # A narrower
        self.assertAlmostEqual((narrow[0] + narrow[2]) / 2, 160.0, places=1)  # A centred
        wide = self.ext[(2, 0.0)]
        self.assertAlmostEqual(wide[0], 16.0, places=1)             # B full pill width
        self.assertAlmostEqual(wide[2], 304.0, places=1)

    def test_attachment_is_continuous(self):
        for mode in (1, 2):
            for prog in (0.0, 0.25, 0.5, 0.7):
                inside, total = self.fill[(mode, prog)]
                with self.subTest(mode=mode, progress=prog):
                    self.assertGreater(total, 1)
                    self.assertEqual(inside, total, 'structure must be connected while attached')

    def test_detach_phase_opens_a_gap(self):
        for mode in (1, 2):
            inside, total = self.fill[(mode, 0.9)]
            with self.subTest(mode=mode):
                self.assertLess(inside, total, 'a gap must open before the pill settles')

    def test_final_progress_is_exact_capsule(self):
        for mode in (0, 1, 2):
            self.assertEqual(self.ext[(mode, 1.0)], FINAL, msg=f'mode {mode}')

    def test_static_mode_always_capsule(self):
        for prog in PROGRESS:
            self.assertEqual(self.ext[(0, prog)], FINAL)

    def test_drop_width_is_monotonic(self):
        widths = [self.ext[(1, p)][2] - self.ext[(1, p)][0] for p in PROGRESS[:-1]]
        self.assertEqual(widths, sorted(widths))

    def test_sheet_is_pill_width_until_detach(self):
        for prog in (0.0, 0.25, 0.5, 0.7):
            x0, _, x1, _ = self.ext[(2, prog)]
            self.assertAlmostEqual(x0, 16.0, places=1)
            self.assertAlmostEqual(x1, 304.0, places=1)

    def test_eased_duration_1000ms(self):
        self.assertAlmostEqual(self.ease['0'], 0.0, places=3)
        self.assertAlmostEqual(self.ease['1000'], 1.0, places=3)
        self.assertGreater(self.ease['500'], 0.5)


if __name__ == '__main__':
    unittest.main()
