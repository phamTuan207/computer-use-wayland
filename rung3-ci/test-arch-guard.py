#!/usr/bin/env python3
"""Unit tests for arch-guard.py (I13).

Run: python3 rung3-ci/test-arch-guard.py
"""
import importlib.util
import os
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "arch_guard", os.path.join(HERE, "arch-guard.py"))
ag = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ag)


class ImportMapTests(unittest.TestCase):
    def test_unlisted_import_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "scripts"))
            with open(os.path.join(d, "scripts", "a.py"), "w") as fh:
                fh.write("import b\n")
            with open(os.path.join(d, "scripts", "b.py"), "w") as fh:
                fh.write("X = 1\n")
            map_path = os.path.join(d, "map.txt")
            with open(map_path, "w") as fh:
                fh.write("a: \nb: \n")
            violations = ag.check_imports(root=d, map_path=map_path)
            self.assertEqual(len(violations), 1)
            self.assertIn("imports b", violations[0])
            with open(map_path, "w") as fh:
                fh.write("a: b\nb: \n")
            self.assertEqual(ag.check_imports(root=d, map_path=map_path),
                             [])


class MachineValueTests(unittest.TestCase):
    def test_denylist_hits_and_allowlist(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "scripts"))
            with open(os.path.join(d, "scripts", "x.py"), "w") as fh:
                fh.write('P = "/home/someone/secret"\n')
            os.makedirs(os.path.join(d, "tests", "fixtures"))
            with open(os.path.join(d, "tests", "fixtures", "f.py"),
                      "w") as fh:
                fh.write('P = "/home/someone/fake"\n')
            violations = ag.scan_machine_values(root=d)
            self.assertEqual(len(violations), 1)
            self.assertIn("scripts/x.py", violations[0])


if __name__ == "__main__":
    unittest.main()
