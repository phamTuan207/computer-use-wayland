#!/usr/bin/env python3
"""Unit tests for test-discover.py helpers and lineage-check.py.

Run: python3 -m unittest discover -s rung3-ci -p "test-*.py"
"""
import importlib.util
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    spec = importlib.util.spec_from_file_location(
        name.replace("-", "_"), os.path.join(HERE, name))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


td = load("test-discover.py")
lc = load("lineage-check.py")


class BalanceTests(unittest.TestCase):
    def test_greedy_balance(self):
        counts = {"a": 10, "b": 8, "c": 6, "d": 4, "e": 2}
        shards = td.balance_shards(counts, 2)
        loads = sorted(sum(counts[m] for m in s) for s in shards)
        self.assertEqual(loads, [14, 16])
        self.assertEqual(sorted(m for s in shards for m in s),
                         ["a", "b", "c", "d", "e"])

    def test_more_shards_than_modules(self):
        shards = td.balance_shards({"a": 3}, 4)
        self.assertEqual(sum(len(s) for s in shards), 1)


class DiffTests(unittest.TestCase):
    def test_stripped_only_failure_is_dependency(self):
        normal = {"t1": "ok", "t2": "ok", "t3": "fail", "t4": "skip"}
        stripped = {"t1": "fail", "t2": "ok", "t3": "error", "t4": "skip"}
        deps, pre, only_s, only_n = td.diff_outcomes(normal, stripped)
        self.assertEqual(deps, ["t1"])
        self.assertEqual(pre, ["t3"])
        self.assertEqual((only_s, only_n), ([], []))

    def test_set_difference_reported(self):
        deps, pre, only_s, only_n = td.diff_outcomes(
            {"t1": "ok"}, {"t2": "ok"})
        self.assertEqual((only_s, only_n), (["t2"], ["t1"]))


class LineageTests(unittest.TestCase):
    def test_manifest_parse_and_check(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            manifest = os.path.join(d, "m.txt")
            with open(manifest, "w") as fh:
                fh.write("# comment\n\nabc123 some/file.py marker text\n")
            entries = lc.load_manifest(manifest)
            self.assertEqual(entries, [("abc123", "some/file.py",
                                        "marker text")])
            self.assertEqual(len(lc.check(entries, root=d)), 1)
            os.makedirs(os.path.join(d, "some"))
            with open(os.path.join(d, "some", "file.py"), "w") as fh:
                fh.write("has marker text inside\n")
            self.assertEqual(lc.check(entries, root=d), [])


if __name__ == "__main__":
    unittest.main()
