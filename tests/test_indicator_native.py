"""Offline tests for the native indicator's small state-transition helpers."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class IndicatorState(unittest.TestCase):
    @unittest.skipUnless(shutil.which('cc'), 'C compiler is unavailable')
    def test_idempotent_visibility_and_present_gate(self):
        with tempfile.TemporaryDirectory() as folder:
            binary = Path(folder) / 'indicator-state-test'
            build = subprocess.run(
                ['cc', '-Wall', '-Wextra', '-Werror', '-o', str(binary),
                 str(ROOT / 'tests/indicator_state_test.c')],
                capture_output=True, text=True, timeout=10)
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            result = subprocess.run([str(binary)], capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
