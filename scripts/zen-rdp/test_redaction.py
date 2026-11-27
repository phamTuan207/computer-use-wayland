#!/usr/bin/env python3
"""Unit tests for I22 URL redaction in rdp_client.py."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rdp_client as rc


class RedactUrlTests(unittest.TestCase):
    def test_sensitive_params_redacted(self):
        self.assertEqual(
            rc._redact_url("https://x.test/cb?code=abc&next=/home"),
            "https://x.test/cb?code=REDACTED&next=/home")
        self.assertEqual(
            rc._redact_url("https://x.test/?token=t&api_key=k&q=hi"),
            "https://x.test/?token=REDACTED&api_key=REDACTED&q=hi")

    def test_no_query_unchanged(self):
        self.assertEqual(rc._redact_url("https://x.test/path"),
                         "https://x.test/path")
        self.assertEqual(rc._redact_url(""), "")

    def test_fragment_preserved(self):
        self.assertEqual(
            rc._redact_url("https://x.test/?sid=1#frag"),
            "https://x.test/?sid=REDACTED#frag")

    def test_tab_snapshot_redacts(self):
        snap = rc._tab_snapshot([{"actor": "tabDescriptor1",
                                  "url": "https://x.test/?password=p",
                                  "title": "t", "selected": True}])
        self.assertEqual(snap[0]["url"],
                         "https://x.test/?password=REDACTED")

    def test_report_walk_redacts_nested_urls(self):
        report = {"tabs_after": [{"url": "https://x.test/?token=1"}],
                  "denylist_hits": [{"url": "https://y.test/?code=2"}],
                  "probe": {"verdict": "CLEAN"}}
        rc._redact_report_urls(report)
        self.assertEqual(report["tabs_after"][0]["url"],
                         "https://x.test/?token=REDACTED")
        self.assertEqual(report["denylist_hits"][0]["url"],
                         "https://y.test/?code=REDACTED")
        self.assertEqual(report["probe"]["verdict"], "CLEAN")


if __name__ == "__main__":
    unittest.main()
