#!/usr/bin/env python3
"""Unit tests for test-discover.py helpers and lineage-check.py.

Run: python3 -m unittest discover -s rung3-ci -p "test-*.py"
"""
import contextlib
import importlib.util
import io
import os
import sys
import tempfile
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


def run_cli(argv):
    """Run td.main in-process, capturing stdout; returns (code, out)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = td.main(argv)
    return code, buf.getvalue()


def write_files(root, files):
    for rel, source in files.items():
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write(source)


class ChildProblemTests(unittest.TestCase):
    def test_nonzero_exit_is_problem(self):
        problem = td.child_problem("normal", {"t": "ok"}, True, 3,
                                   "boom\nlast line")
        self.assertIn("exited 3", problem)
        self.assertIn("last line", problem)

    def test_missing_summary_is_problem(self):
        problem = td.child_problem("stripped", {"t": "ok"}, False, 0, "")
        self.assertIn("no SUMMARY", problem)

    def test_zero_outcomes_is_problem(self):
        problem = td.child_problem("normal", {}, True, 0, "")
        self.assertIn("zero test outcomes", problem)

    def test_clean_run_is_none(self):
        self.assertIsNone(
            td.child_problem("normal", {"t": "ok"}, True, 0, ""))

    def test_parse_results(self):
        outcomes, saw = td.parse_results(
            "@@RESULT@@ mod.T.test_a ok\nSUMMARY total=1 ok=1\n")
        self.assertEqual(outcomes, {"mod.T.test_a": "ok"})
        self.assertTrue(saw)
        outcomes, saw = td.parse_results("@@RESULT@@ mod.T.test_a ok\n")
        self.assertFalse(saw)


class SubTestOutcomeTests(unittest.TestCase):
    """Failures inside subTest must still record a parent outcome."""

    def outcomes_for(self, case):
        suite = unittest.TestLoader().loadTestsFromTestCase(case)
        return td.run_suite(suite)

    def test_subtest_failure_recorded(self):
        class Case(unittest.TestCase):
            def test_a(self):
                with self.subTest(x=1):
                    self.assertEqual(1, 2)
        outcomes = self.outcomes_for(Case)
        self.assertEqual(list(outcomes.values()), ["fail"])

    def test_subtest_error_recorded(self):
        class Case(unittest.TestCase):
            def test_a(self):
                with self.subTest(x=1):
                    raise RuntimeError("boom")
        outcomes = self.outcomes_for(Case)
        self.assertEqual(list(outcomes.values()), ["error"])

    def test_subtest_error_outranks_failure(self):
        class Case(unittest.TestCase):
            def test_a(self):
                with self.subTest(x=1):
                    self.assertEqual(1, 2)
                with self.subTest(x=2):
                    raise RuntimeError("boom")
        outcomes = self.outcomes_for(Case)
        self.assertEqual(list(outcomes.values()), ["error"])

    def test_subtest_pass_recorded_ok(self):
        class Case(unittest.TestCase):
            def test_a(self):
                with self.subTest(x=1):
                    self.assertEqual(1, 1)
        outcomes = self.outcomes_for(Case)
        self.assertEqual(list(outcomes.values()), ["ok"])

    def test_subtest_skip_recorded(self):
        class Case(unittest.TestCase):
            def test_a(self):
                with self.subTest(x=1):
                    self.skipTest("nope")
        outcomes = self.outcomes_for(Case)
        self.assertEqual(list(outcomes.values()), ["skip"])


class SetupFailureOutcomeTests(unittest.TestCase):
    """setUpClass/setUpModule failures expand to per-test errors."""

    def test_setup_class_failure_expands(self):
        class Case(unittest.TestCase):
            @classmethod
            def setUpClass(cls):
                raise RuntimeError("nope")

            def test_a(self):
                pass

            def test_b(self):
                pass

        suite = unittest.TestLoader().loadTestsFromTestCase(Case)
        outcomes = td.run_suite(suite)
        self.assertEqual(sorted(outcomes.values()), ["error", "error"])
        self.assertFalse(any(k.startswith("setUpClass")
                             for k in outcomes))

    def test_setup_module_failure_expands(self):
        import types
        mod = types.ModuleType("fake_mod_td")

        def setUpModule():
            raise RuntimeError("nope")

        class Case(unittest.TestCase):
            def test_a(self):
                pass

        Case.__module__ = "fake_mod_td"
        mod.setUpModule = setUpModule
        mod.Case = Case
        sys.modules["fake_mod_td"] = mod
        try:
            suite = unittest.TestLoader().loadTestsFromModule(mod)
            outcomes = td.run_suite(suite)
        finally:
            del sys.modules["fake_mod_td"]
        self.assertEqual(list(outcomes.values()), ["error"])
        self.assertFalse(any(k.startswith("setUpModule")
                             for k in outcomes))


class FailedTestAttributionTests(unittest.TestCase):
    def test_package_failed_test_full_path(self):
        with tempfile.TemporaryDirectory() as d:
            write_files(d, {
                "sub1/__init__.py": "",
                "sub1/test_dup.py":
                    "import no_such_dep_xyz\n"
                    "import unittest\n\n\n"
                    "class T(unittest.TestCase):\n"
                    "    def test_x(self):\n"
                    "        pass\n",
            })
            counts = td.module_test_counts(d, "test_*.py")
            self.assertEqual(counts, {"sub1.test_dup": 1})
            suite = td.suite_for_modules(["sub1.test_dup"], d)
            self.assertEqual(suite.countTestCases(), 1)
            bare = td.suite_for_modules(["test_dup"], d)
            self.assertEqual(bare.countTestCases(), 0)


class HermeticGateTests(unittest.TestCase):
    def test_nonexistent_start_dir_fails(self):
        code, out = run_cli(
            ["hermetic", "--start-dir", "/tmp/does-not-exist-td"])
        self.assertEqual(code, 1)
        self.assertIn("HERMETIC GATE FAIL", out)

    def test_empty_start_dir_fails(self):
        with tempfile.TemporaryDirectory() as d:
            code, out = run_cli(["hermetic", "--start-dir", d])
            self.assertEqual(code, 1)
            self.assertIn("zero test outcomes", out)

    def test_stripped_crash_fails(self):
        with tempfile.TemporaryDirectory() as d:
            write_files(d, {"test_crash.py":
                            "import os\nimport shutil\nimport unittest\n\n\n"
                            "class T(unittest.TestCase):\n"
                            "    def test_a_ok(self):\n"
                            "        self.assertTrue(True)\n"
                            "    def test_b_exit_when_stripped(self):\n"
                            "        if shutil.which('ls') is None:\n"
                            "            os._exit(3)\n"
                            "    def test_c_after(self):\n"
                            "        self.assertTrue(True)\n"})
            code, out = run_cli(["hermetic", "--start-dir", d])
            self.assertEqual(code, 1)
            self.assertIn("stripped child exited 3", out)

    def test_set_difference_fails(self):
        with tempfile.TemporaryDirectory() as d:
            write_files(d, {"test_cond.py":
                            "import shutil\nimport unittest\n\n\n"
                            "class Always(unittest.TestCase):\n"
                            "    def test_a(self):\n"
                            "        self.assertTrue(True)\n\n\n"
                            "if shutil.which('ls'):\n"
                            "    class OnlyWithTool(unittest.TestCase):\n"
                            "        def test_b(self):\n"
                            "            self.assertTrue(True)\n"})
            code, out = run_cli(["hermetic", "--start-dir", d])
            self.assertEqual(code, 1)
            self.assertIn("test sets differ", out)

    def test_ok_to_skip_not_gated(self):
        with tempfile.TemporaryDirectory() as d:
            write_files(d, {"test_skip.py":
                            "import shutil\nimport unittest\n\n\n"
                            "class T(unittest.TestCase):\n"
                            "    def test_a(self):\n"
                            "        if shutil.which('ls') is None:\n"
                            "            self.skipTest('no ls')\n"})
            code, out = run_cli(["hermetic", "--start-dir", d])
            self.assertEqual(code, 0)
            self.assertIn("HERMETIC GATE PASS", out)
            self.assertIn("skips: normal=0, stripped=1", out)

    def test_clean_suite_passes(self):
        with tempfile.TemporaryDirectory() as d:
            write_files(d, {"test_ok.py":
                            "import unittest\n\n\n"
                            "class T(unittest.TestCase):\n"
                            "    def test_a(self):\n"
                            "        self.assertTrue(True)\n"})
            code, out = run_cli(["hermetic", "--start-dir", d])
            self.assertEqual(code, 0)
            self.assertIn("HERMETIC GATE PASS", out)


class ShardGateTests(unittest.TestCase):
    def test_bogus_modules_fails(self):
        with tempfile.TemporaryDirectory() as d:
            write_files(d, {"test_ok.py":
                            "import unittest\n\n\n"
                            "class T(unittest.TestCase):\n"
                            "    def test_a(self):\n"
                            "        self.assertTrue(True)\n"})
            code, out = run_cli(["shard", "--start-dir", d,
                                 "--modules", "bogus.mod"])
            self.assertEqual(code, 1)
            self.assertIn("unknown module(s): bogus.mod", out)

    def test_crash_suite_fails_without_compare(self):
        with tempfile.TemporaryDirectory() as d:
            write_files(d, {
                "test_boom.py":
                    "import os\nimport unittest\n\n\n"
                    "class Boom(unittest.TestCase):\n"
                    "    def test_a_ok(self):\n"
                    "        self.assertTrue(True)\n"
                    "    def test_b_exit(self):\n"
                    "        os._exit(4)\n"
                    "    def test_c_after(self):\n"
                    "        self.assertTrue(True)\n",
                "test_fine.py":
                    "import unittest\n\n\n"
                    "class Fine(unittest.TestCase):\n"
                    "    def test_ok(self):\n"
                    "        self.assertTrue(True)\n",
            })
            code, out = run_cli(["shard", "--start-dir", d,
                                 "--shards", "2"])
            self.assertEqual(code, 1)
            self.assertIn("shard child exited 4", out)
            self.assertIn("missing: test_boom.Boom.test_c_after", out)

    def test_empty_dir_fails(self):
        with tempfile.TemporaryDirectory() as d:
            code, out = run_cli(["shard", "--start-dir", d])
            self.assertEqual(code, 1)
            self.assertIn("SHARD FAIL", out)

    def test_nonexistent_dir_fails(self):
        code, out = run_cli(
            ["shard", "--start-dir", "/tmp/does-not-exist-td"])
        self.assertEqual(code, 1)
        self.assertIn("cannot discover tests", out)

    def test_clean_suite_passes(self):
        with tempfile.TemporaryDirectory() as d:
            write_files(d, {
                "test_one.py":
                    "import unittest\n\n\n"
                    "class One(unittest.TestCase):\n"
                    "    def test_a(self):\n"
                    "        self.assertTrue(True)\n",
                "test_two.py":
                    "import unittest\n\n\n"
                    "class Two(unittest.TestCase):\n"
                    "    def test_b(self):\n"
                    "        self.assertTrue(True)\n",
            })
            code, out = run_cli(["shard", "--start-dir", d,
                                 "--shards", "2"])
            self.assertEqual(code, 0)
            self.assertIn("sharded: 2 tests", out)

    def test_clean_suite_compare_serial_matches(self):
        # Module names must differ from test_clean_suite_passes:
        # unittest discover in this process rejects a same-named
        # module imported from another temp dir.
        with tempfile.TemporaryDirectory() as d:
            write_files(d, {
                "test_three.py":
                    "import unittest\n\n\n"
                    "class Three(unittest.TestCase):\n"
                    "    def test_c(self):\n"
                    "        self.assertTrue(True)\n",
                "test_four.py":
                    "import unittest\n\n\n"
                    "class Four(unittest.TestCase):\n"
                    "    def test_d(self):\n"
                    "        self.assertTrue(True)\n",
            })
            code, out = run_cli(["shard", "--start-dir", d,
                                 "--shards", "2", "--compare-serial"])
            self.assertEqual(code, 0)
            self.assertIn("SHARD MATCH", out)


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
