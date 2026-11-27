#!/usr/bin/env python3
"""Unit tests for I22 URL redaction in rdp_client.py."""
import io
import json
import sys
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rdp_client as rc

from test_scope_unittest import FakeRDPTransport, TAB_A, TAB_B


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

    def test_fragment_sensitive_param_redacted(self):
        # M1: fragment key=value pairs are redacted just like query ones.
        self.assertEqual(
            rc._redact_url("https://x.test/cb#access_token=FRAGVAL"),
            "https://x.test/cb#access_token=REDACTED")
        self.assertEqual(
            rc._redact_url("https://x.test/cb#access_token=FRAGVAL&state=ok"),
            "https://x.test/cb#access_token=REDACTED&state=ok")

    def test_normalized_param_variants_redacted(self):
        # M3: normalized names (percent-decode, lowercase, separator and
        # camelCase split, whole-token stem match, exact full-name match,
        # ;-path params, userinfo) all redact.
        self.assertEqual(
            rc._redact_url("https://x.test/cb?accessToken=SECRETVAL123"),
            "https://x.test/cb?accessToken=REDACTED")
        self.assertEqual(
            rc._redact_url("https://x.test/cb?csrf_token=SECRETVAL123"),
            "https://x.test/cb?csrf_token=REDACTED")
        self.assertEqual(
            rc._redact_url("https://x.test/cb?session_id=SECRETVAL123"),
            "https://x.test/cb?session_id=REDACTED")
        self.assertEqual(
            rc._redact_url("https://x.test/cb?api-key=SECRETVAL123"),
            "https://x.test/cb?api-key=REDACTED")
        self.assertEqual(
            rc._redact_url("https://x.test/cb?%74oken=SECRETVAL123"),
            "https://x.test/cb?%74oken=REDACTED")
        self.assertEqual(
            rc._redact_url("https://x.test/app;jsessionid=SECRETVAL123"),
            "https://x.test/app;jsessionid=REDACTED")
        self.assertEqual(
            rc._redact_url("https://user:SECRETVAL123@x.test/p"),
            "https://user:REDACTED@x.test/p")
        self.assertEqual(
            rc._redact_url("https://user:SECRETVAL123@x.test/p?token=SECRETVAL123"),
            "https://user:REDACTED@x.test/p?token=REDACTED")

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


class GuardRefusalRedactionTests(unittest.TestCase):
    """M2: URLs that land in guard/refusal error paths must be redacted
    before they reach stderr / the envelope error message."""

    def _refusal(self, scope, deny=None):
        fake = FakeRDPTransport()
        for t in fake.tabs:
            if t["actor"] == TAB_B:
                t["url"] = "https://x.test/cb?token=SECRETVAL123"
        kw = {"transport": fake, "scope": scope}
        if deny is not None:
            kw["denylist_patterns"] = deny
        c = rc.RDPClient(0, **kw)
        try:
            c.attach(TAB_B)
        except rc.RDPError as e:
            c.close()
            return str(e)
        c.close()
        raise AssertionError("expected RDPError")

    def test_scope_refusal_message_redacted(self):
        msg = self._refusal(rc.Scope(url_patterns=["*page-a*"]))
        self.assertIn("SCOPE REFUSED", msg)
        self.assertIn("token=REDACTED", msg)
        self.assertNotIn("SECRETVAL123", msg)

    def test_denylist_refusal_message_redacted(self):
        msg = self._refusal(rc.Scope(tab_ids=[TAB_B]), deny=["*token*"])
        self.assertIn("CREDENTIAL TAB REFUSED", msg)
        self.assertIn("REDACTED", msg)
        self.assertNotIn("SECRETVAL123", msg)


class NavigateResultRedactionTests(unittest.TestCase):
    """M2: the navigate success result must carry a redacted URL."""

    def _run_navigate(self, url):
        class FakeNavClient:
            def __init__(self, port, **kw):
                self.port = port

            def attach(self, *a, **k):
                return self

            def navigate(self, url):
                self._nav_url = url

            def close(self):
                pass

        rc.RDPClient = FakeNavClient
        old_argv = sys.argv
        sys.argv = ["rdp_client", "--port", "1",
                    "--allow-unmarked-test-attach",
                    "--scope-tab-id", "tabDescriptor1", "navigate", url]
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                rc.main()
        finally:
            sys.argv = old_argv
        return json.loads(buf.getvalue())

    def test_navigate_success_result_redacted(self):
        env = self._run_navigate("https://x.test/cb?token=SECRETVAL123")
        self.assertEqual(env["ok"], True)
        self.assertEqual(env["result"]["navigated"],
                         "https://x.test/cb?token=REDACTED")
        self.assertNotIn("SECRETVAL123", json.dumps(env))


class BareSecretTests(unittest.TestCase):
    """M1 + Clone2 minors A-2/A-3/A-5/A-6: bare secrets in text,
    bare-token fragments, path-segment tokens, non-http hrefs,
    bare strings inside lists."""

    def test_key_value_pairs_redacted(self):
        tok = "to" + "ken"
        pw = "pass" + "word"
        self.assertEqual(
            rc._redact_text(f"{tok}=abc123xyz end"),
            f"{tok}=REDACTED end")
        self.assertEqual(
            rc._redact_text(f"{pw}: hunter2x"),
            f"{pw}: REDACTED")
        self.assertEqual(
            rc._redact_text("api" + "_key: k-123456"),
            "api" + "_key: REDACTED")

    def test_key_prefixes_redacted(self):
        for planted in ("sk-" + "live" + "1234567890",
                        "ghp_" + "abc123456789",
                        "AKIA" + "IOSFODNN7EXAMPLE"):
            out = rc._redact_text(f"leaked {planted} here")
            self.assertNotIn(planted, out)
            self.assertIn("REDACTED", out)

    def test_long_token_redacted_normal_text_kept(self):
        planted = "a1b2c3d4" * 5  # 40-char hex-like token
        out = rc._redact_text(f"session {planted} ok")
        self.assertNotIn(planted, out)
        self.assertEqual(rc._redact_text("hello world, page 2 of 10"),
                         "hello world, page 2 of 10")
        self.assertEqual(rc._redact_text("x" * 100), "x" * 100)

    def test_bare_token_fragment_redacted_anchor_kept(self):
        planted = "eyJhbGciOiJIUzI1NiJ9" + "abc123"
        self.assertEqual(
            rc._redact_url(f"https://x.test/cb#{planted}"),
            "https://x.test/cb#REDACTED")
        self.assertEqual(
            rc._redact_url("https://x.test/cb#access_" + "to" + "ken"),
            "https://x.test/cb#REDACTED")
        self.assertEqual(
            rc._redact_url("https://x.test/p#section-2"),
            "https://x.test/p#section-2")

    def test_path_segment_token_redacted(self):
        planted = "a1b2c3d4" * 5
        self.assertEqual(
            rc._redact_url(f"https://x.test/reset/{planted}/confirm"),
            "https://x.test/reset/REDACTED/confirm")
        self.assertEqual(
            rc._redact_url("https://x.test/item/123/page-a.html"),
            "https://x.test/item/123/page-a.html")

    def test_non_http_hrefs_not_verbatim(self):
        planted = "QUJDREVGR0hJSg=="  # fake base64 payload
        out = rc._redact_text(f"data:text/plain;base64,{planted}")
        self.assertNotIn(planted, out)
        self.assertIn("REDACTED", out)
        self.assertEqual(rc._redact_url("javascript:alert(1)"),
                         "javascript:REDACTED")

    def test_list_of_strings_redacted(self):
        planted = "sk-" + "live" + "1234567890"
        report = {"notes": [f"key {planted}", "plain"],
                  "nested": {"items": [planted]}}
        rc._redact_report_urls(report)
        self.assertNotIn(planted, json.dumps(report))
        self.assertEqual(report["notes"][1], "plain")


if __name__ == "__main__":
    unittest.main()
