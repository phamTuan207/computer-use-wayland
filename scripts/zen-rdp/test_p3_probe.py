#!/usr/bin/env python3
"""Unit tests for the P3 probe fail-closed gate (B3, no browser).

The probe must refuse to run without --profile-marker, and refuse
a marker that is not a launch_dedicated profile directory for the
port. Both refusals fire before any RDP connection.
Run: python3 -m unittest test_p3_probe -v
ydotool is banned (not used). Stdlib only.
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROBE = str(Path(__file__).resolve().parent / "probes"
            / "p3_unsolicited_probe.py")


def run_probe(*argv):
    return subprocess.run([sys.executable, PROBE] + list(argv),
                          capture_output=True, text=True, timeout=30)


class ProbeGateTests(unittest.TestCase):
    def test_marker_required(self):
        proc = run_probe("--port", "1")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("--profile-marker", proc.stderr)

    def test_non_dedicated_marker_refused(self):
        with tempfile.TemporaryDirectory() as td:
            proc = run_probe("--port", "1", "--profile-marker", td)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("REFUSED", proc.stderr)

    def test_missing_marker_dir_refused(self):
        proc = run_probe("--port", "1", "--profile-marker",
                         "/tmp/p3-probe-no-such-dir-xyz")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("REFUSED", proc.stderr)

    def test_no_index_close_all_in_source(self):
        # The storm cleanup must close only probe-tagged tabs.
        source = Path(PROBE).read_text()
        self.assertIn("data-p3-probe", source)
        self.assertNotIn("i>=2", source)


if __name__ == "__main__":
    unittest.main()
