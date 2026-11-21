"""Tests for the Code Mode prototype (scripts/codemode.py).

Run: python3 -m pytest tests/test_codemode.py -q
Or:  python3 tests/test_codemode.py (stdlib runner at the bottom).
VM only. No laptop, no Zen, no network.
"""

import builtins
import json
import os
import sys
import time
import types
import unittest
from unittest import mock

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
        self.assertEqual(sum(item["kind"] == "op"
                             for item in out["results"]), len(codemode.OPS))
        self.assertEqual(sum(item["kind"] == "snippet"
                             for item in out["results"]), 4)
        self.assertEqual(out["total"], len(codemode.OPS) + 4)

    def test_snippets_rank_below_ops_and_search_tags_only(self):
        out = codemode.search_ops("repo terminal")
        kinds = [item["kind"] for item in out["results"]]
        self.assertIn("op", kinds)
        self.assertIn("snippet", kinds)
        self.assertEqual(kinds, sorted(kinds, key=lambda kind: kind != "op"))
        snippet = next(item for item in out["results"]
                       if item["kind"] == "snippet")
        self.assertIn("params_summary", snippet)
        self.assertIn("last_verified", snippet)
        self.assertIn("stale", snippet)
        self.assertNotIn("file", snippet)

    def test_describe_snippet_returns_metadata_only(self):
        out = codemode.describe_snippet("p1-disk-free")
        self.assertEqual(out["name"], "p1-disk-free")
        self.assertIn("sha256", out)
        self.assertIn("expected_result", out)
        self.assertNotIn("code", out)
        self.assertNotIn("source_code", out)

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

    def test_format_cannot_reach_dunder_data(self):
        probes = (
            'return "{0.__class__}".format("")',
            'return "{0.__globals__}".format(repo_list_scripts)',
            'return "{0.__self__.session_token}".format(repo_list_scripts)',
        )
        for source in probes:
            with self.subTest(source=source):
                out = codemode.execute_op(source)
                self.assertEqual(out["status"], "error")
                self.assertIn("format", out["error"])

    def test_dunder_name_rejected(self):
        with self.assertRaisesRegex(codemode.CodemodeError, "dunder"):
            codemode._scan("__codemode_main__")

    def test_yield_and_async_rejected(self):
        for source in (
                "yield 2",
                "yield from ()",
                "async for item in items:\n    pass",
                "async with manager:\n    pass"):
            with self.subTest(source=source):
                out = codemode.execute_op(source)
                self.assertEqual(out["status"], "error")

    def test_execute_namespace_pins_safe_builtins(self):
        captured = []
        original_exec = builtins.exec

        def capture_exec(code, namespace, *args):
            captured.append(namespace)
            return original_exec(code, namespace, *args)

        with mock.patch("builtins.exec", new=capture_exec):
            out = codemode.execute_op("result = 7")
        self.assertEqual(out["status"], "completed")
        self.assertEqual(len(captured), 1)
        safe = captured[0]["__builtins__"]
        self.assertIsInstance(safe, dict)
        self.assertNotIsInstance(safe, types.ModuleType)
        self.assertNotIn("eval", safe)

    def test_50mb_result_is_not_returned(self):
        out = codemode.execute_op('return "A" * (5 * 10**7)')
        self.assertEqual(out["status"], "error")
        self.assertEqual(out["error_type"], "result_too_large")
        self.assertNotIn("result", out)

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
