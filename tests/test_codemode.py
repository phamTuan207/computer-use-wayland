"""Tests for the Code Mode prototype (scripts/codemode.py).

Run: python3 -m pytest tests/test_codemode.py -q
Or:  python3 tests/test_codemode.py (stdlib runner at the bottom).
VM only. No laptop, no Zen, no network.
"""

import json
import os
import sys
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import codemode  # noqa: E402


class TestSearch(unittest.TestCase):
    def test_search_returns_paths_not_schemas(self):
        out = codemode.search_ops("dom locate")
        self.assertEqual(out["results"][0]["path"], "zen.locate")
        self.assertNotIn("params", out["results"][0])
        self.assertNotIn("returns", out["results"][0])

    def test_search_empty_query_lists_all(self):
        out = codemode.search_ops("")
        self.assertEqual(out["total"], len(codemode.OPS))

    def test_search_no_match(self):
        out = codemode.search_ops("qqqzzz-no-such-thing")
        self.assertEqual(out["total"], 0)

    def test_describe_known_op(self):
        out = codemode.describe_op("repo.list_scripts")
        self.assertEqual(out["path"], "repo.list_scripts")
        self.assertIn("pattern", out["params"])
        self.assertFalse(out["laptop_only"])

    def test_describe_unknown_op(self):
        with self.assertRaises(codemode.CodemodeError):
            codemode.describe_op("nope.missing")


class TestExecute(unittest.TestCase):
    def test_list_scripts_end_to_end(self):
        code = "return repo_list_scripts('dom')"
        out = codemode.execute_op(code)
        self.assertEqual(out["status"], "completed")
        names = [s["name"] for s in out["result"]["scripts"]]
        self.assertIn("zen_dom.py", names)
        self.assertGreater(out["elapsed_ms"], 0)

    def test_chained_ops_in_one_program(self):
        code = (
            "info = repo_script_info('zen_dom.py')\n"
            "compiled = repo_py_compile('zen_dom.py')\n"
            "return {'bytes': info['bytes'], 'ok': compiled['ok'],"
            " 'ms': compiled['elapsed_ms']}"
        )
        out = codemode.execute_op(code)
        self.assertEqual(out["status"], "completed")
        self.assertTrue(out["result"]["ok"])
        self.assertGreater(out["result"]["bytes"], 0)

    def test_loop_and_filter(self):
        code = (
            "all_scripts = repo_list_scripts('')\n"
            "big = [s for s in all_scripts['scripts'] if s['bytes'] > 20000]\n"
            "return {'total': all_scripts['count'], 'big': len(big)}"
        )
        out = codemode.execute_op(code)
        self.assertEqual(out["status"], "completed")
        self.assertGreater(out["result"]["total"], 40)
        self.assertGreater(out["result"]["big"], 0)

    def test_read_file_vm_safe(self):
        code = "return repo_read_file('scripts/codemode.py', 200)"
        out = codemode.execute_op(code)
        self.assertEqual(out["status"], "completed")
        self.assertIn("Code Mode", out["result"]["text"])

    def test_read_file_outside_root_rejected(self):
        code = "return repo_read_file('/etc/passwd')"
        out = codemode.execute_op(code)
        self.assertEqual(out["status"], "error")

    def test_laptop_only_op_returns_requires_laptop(self):
        code = "return zen_locate('#count-btn')"
        out = codemode.execute_op(code)
        self.assertEqual(out["status"], "requires_laptop")

    def test_import_rejected(self):
        out = codemode.execute_op("import os\nreturn 1")
        self.assertEqual(out["status"], "error")
        self.assertIn("import", out["error"])

    def test_open_rejected(self):
        out = codemode.execute_op("return open('/etc/passwd').read()")
        self.assertEqual(out["status"], "error")

    def test_eval_rejected(self):
        out = codemode.execute_op("return eval('1+1')")
        self.assertEqual(out["status"], "error")

    def test_dunder_rejected(self):
        out = codemode.execute_op("return (1).__class__")
        self.assertEqual(out["status"], "error")

    def test_syntax_error_envelope(self):
        out = codemode.execute_op("return 1 +")
        self.assertEqual(out["status"], "error")
        self.assertIn("syntax", out["error"])

    def test_unknown_name_envelope(self):
        out = codemode.execute_op("return no_such_op()")
        self.assertEqual(out["status"], "error")
        self.assertIn("NameError", out["error"])

    def test_wall_clock_budget(self):
        out = codemode.execute_op("x = 0\nwhile True:\n    x += 1",
                                  wall_seconds=2)
        self.assertEqual(out["status"], "error")
        self.assertIn("budget", out["error"])
        self.assertLess(out["elapsed_ms"], 10000)

    def test_program_size_cap(self):
        out = codemode.execute_op("x = 1\n" * 3000)
        self.assertEqual(out["status"], "error")
        self.assertIn("8192", out["error"])


class TestTimings(unittest.TestCase):
    def test_search_is_fast(self):
        started = time.monotonic()
        for _ in range(100):
            codemode.search_ops("dom")
        elapsed_ms = (time.monotonic() - started) * 1000
        self.assertLess(elapsed_ms, 500)

    def test_execute_overhead_is_small(self):
        out = codemode.execute_op("return repo_list_scripts('')")
        self.assertEqual(out["status"], "completed")
        self.assertLess(out["elapsed_ms"], 1000)


if __name__ == "__main__":
    unittest.main(verbosity=2)
