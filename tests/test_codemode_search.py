#!/usr/bin/env python3
"""Tests for scripts/codemode_search.py: search, describe, snippets.

Token numbers here are estimates (characters divided by 4), labeled as
estimates. Timings are measured wall-clock on this machine.
"""

import json
import sys
import time
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import codemode_search as cs
from code_exec import validate_program


class SearchTest(unittest.TestCase):
    def test_registry_covers_all_scripts(self):
        on_disk = sorted(
            p.name for p in (REPO_ROOT / "scripts").iterdir()
            if p.is_file() and p.suffix in cs.SCRIPT_SUFFIXES)
        names = sorted(op["file"] for op in cs.REGISTRY)
        self.assertEqual(names, on_disk)
        self.assertEqual(len(cs.REGISTRY), len(on_disk))

    def test_search_dom_locate(self):
        result = cs.search_ops("dom locate")
        self.assertGreater(result["total"], 0)
        top = [item["name"] for item in result["results"]]
        self.assertIn("zen_dom", top)

    def test_search_session(self):
        result = cs.search_ops("session")
        names = [item["name"] for item in result["results"]]
        self.assertIn("session_manager", names)

    def test_search_no_match(self):
        result = cs.search_ops("zzzzqqq")
        self.assertEqual(result["total"], 0)
        self.assertEqual(result["results"], [])

    def test_search_empty_returns_all(self):
        result = cs.search_ops("", limit=1000)
        self.assertEqual(result["total"], len(cs.REGISTRY))

    def test_search_results_are_short(self):
        result = cs.search_ops("zen", limit=10)
        for item in result["results"]:
            self.assertLessEqual(len(item["description"]), 200)
            self.assertIn("name", item)
            self.assertNotIn("head", item)

    def test_search_ranking(self):
        result = cs.search_ops("polygon")
        self.assertEqual(result["results"][0]["name"], "polygon_checks")


class DescribeTest(unittest.TestCase):
    def test_describe_zen_dom(self):
        info = cs.describe_op("zen_dom")
        self.assertEqual(info["file"], "zen_dom.py")
        self.assertIn("Zen", info["description"])
        self.assertTrue(info["entry_points"])
        text = json.dumps(info, ensure_ascii=False)
        self.assertLess(len(text), 2000)

    def test_describe_never_returns_whole_file(self):
        info = cs.describe_op("code_exec")
        full = (REPO_ROOT / "scripts" / "code_exec.py").read_text()
        text = json.dumps(info, ensure_ascii=False)
        self.assertLess(len(text), 2000)
        self.assertLess(len(text), len(full) // 10)

    def test_describe_mjs(self):
        info = cs.describe_op("cdp")
        self.assertEqual(info["file"], "cdp.mjs")
        self.assertIn("CDP", info["description"])

    def test_describe_unknown(self):
        with self.assertRaises(cs.CodemodeSearchError):
            cs.describe_op("no_such_script")


class SnippetTest(unittest.TestCase):
    def test_registry_has_four(self):
        items = cs.list_snippets()
        self.assertEqual(len(items), 4)
        names = [item["name"] for item in items]
        self.assertEqual(names, ["p1-terminal-df", "p2-terminal-calc",
                                 "p3-terminal-mkdir",
                                 "p4-terminal-write-file"])

    def test_snippet_fields(self):
        for item in cs.list_snippets():
            full = cs.get_snippet(item["name"])
            for key in ("description", "program", "input", "sample_output"):
                self.assertIn(key, full)
            self.assertTrue(full["sample_output"])
            self.assertTrue(full["program"].strip())

    def test_snippet_programs_pass_code_exec_validation(self):
        for item in cs.list_snippets():
            full = cs.get_snippet(item["name"])
            validate_program(full["program"])

    def test_snippet_files_match_registry(self):
        for item in cs.list_snippets():
            full = cs.get_snippet(item["name"])
            on_disk = (REPO_ROOT / "snippets" / full["file"]).read_text(
                encoding="utf-8")
            self.assertEqual(full["program"], on_disk)

    def test_snippet_sample_outputs_are_real(self):
        p2 = cs.get_snippet("p2-terminal-calc")
        self.assertEqual(p2["sample_output"], "96.0\n")
        p4 = cs.get_snippet("p4-terminal-write-file")
        self.assertIn("Ý tưởng 1", p4["sample_output"])

    def test_snippet_unknown(self):
        with self.assertRaises(cs.CodemodeSearchError):
            cs.get_snippet("no_such_snippet")


class TokenTest(unittest.TestCase):
    def test_search_saves_tokens_vs_full_catalog(self):
        measured = cs.measure_tokens("dom locate", limit=5)
        self.assertLess(measured["after_tokens_estimate"],
                        measured["before_tokens_estimate"])
        self.assertGreater(measured["saved_tokens_estimate"], 0)
        print("measured tokens for 'dom locate': before %.1f, after %.1f, "
              "saved %.1f (estimates, chars/4)"
              % (measured["before_tokens_estimate"],
                 measured["after_tokens_estimate"],
                 measured["saved_tokens_estimate"]))

    def test_before_catalog_matches_worker_n_proxy(self):
        before = cs.catalog_before_text()
        estimate = cs.estimate_tokens(before)
        print("full catalog first-3-lines: %d chars, %.1f tokens estimate"
              % (len(before), estimate))
        self.assertGreater(estimate, 1000)


if __name__ == "__main__":
    started = time.monotonic()
    unittest.main(verbosity=2)
    print("wall clock: %.3fs" % (time.monotonic() - started))
