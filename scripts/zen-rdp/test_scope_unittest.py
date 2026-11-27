#!/usr/bin/env python3
"""RT-20 scope tests for rdp_client.py (stdlib unittest, fake transport).

Covers: in-scope evaluate ok, out-of-scope refused (id + URL pattern),
AND scope semantics, denylist refused (incl. lazy empty-URL tabs),
denylist+approval ok and logged (id- and URL-pattern-keyed), unscoped
refused without explicit opt-in, drive-report diff (id-keyed and
url/title-keyed), CLI approval-pair validation, fail-closed profile
marker, tab-pinned noSuchActor retry with URL verification (RT-06),
raw request() packet guard, parent-evaluate gate + audit, longString
fetching, single-drive lock, and bench refusal without --unscoped-test.

Run: python3 -m unittest test_scope_unittest -v
No browser needed. ydotool is banned (not used).
Example URLs use the generic localhost host (no machine-specific port).
"""
import io
import json
import subprocess
import sys
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from rdp_client import (DEFAULT_CREDENTIAL_DENYLIST, LAZY_TAB_PATTERN,
                        RDPClient, RDPError, Scope, _build_scope, bench)

# Resolve the client next to this file so the CLI tests work from any cwd.
RDP_CLIENT = str(Path(__file__).resolve().parent / "rdp_client.py")

TAB_A = "server1.conn0.tabDescriptor1"   # http://localhost/page-a.html
TAB_B = "server1.conn0.tabDescriptor2"   # http://localhost/page-b.html
TAB_C = "server1.conn0.tabDescriptor3"   # http://localhost/login.html


def _packet(obj):
    data = json.dumps(obj).encode()
    return f"{len(data)}:".encode() + data


class FakeRDPTransport:
    """Minimal in-memory RDP server: greeting, listTabs, getTarget,
    evaluateJSAsync, navigateTo. Socket-like: sendall/recv/settimeout/close."""

    def __init__(self, tabs=None):
        self.tabs = tabs if tabs is not None else [
            {"actor": TAB_A, "url": "http://localhost/page-a.html",
             "title": "Page A", "selected": True},
            {"actor": TAB_B, "url": "http://localhost/page-b.html",
             "title": "Page B", "selected": False},
            {"actor": TAB_C, "url": "http://localhost/login.html",
             "title": "Login", "selected": False},
        ]
        self._in = b""
        self._out = _packet({"from": "root", "applicationType": "browser",
                             "traits": {}})
        self.closed = False
        # Target-swap simulation (RT-06): the next N evaluates/navigates
        # fail with noSuchActor and bump the console generation, so the
        # following getTarget hands out a fresh consoleActor.
        self.console_gen = 1
        self.fail_evals = 0
        self.fail_navigates = 0

    # socket-like interface
    def settimeout(self, _t):
        pass

    def close(self):
        self.closed = True

    def recv(self, n):
        chunk, self._out = self._out[:n], self._out[n:]
        return chunk

    def sendall(self, data):
        self._in += data
        while b":" in self._in:
            head, rest = self._in.split(b":", 1)
            length = int(head)
            if len(rest) < length:
                break
            raw, self._in = rest[:length], rest[length:]
            self._handle(json.loads(raw.decode()))

    # fake server logic
    def _reply(self, obj):
        self._out += _packet(obj)

    def _handle(self, req):
        t = req.get("type")
        to = req.get("to")
        if t == "listTabs":
            self._reply({"from": "root", "tabs": self.tabs, "selected": 0})
        elif t == "listProcesses":
            self._reply({"from": "root", "processes": [
                {"actor": "server1.conn0.processDescriptor1",
                 "isParent": True}]})
        elif t == "substring":
            n = int(req.get("end", 0)) - int(req.get("start", 0))
            self._reply({"from": to, "substring": "x" * max(n, 0)})
        elif t == "getTarget":
            self._reply({"from": to, "frame": {
                "actor": to + ".target",
                "consoleActor": to + f".console{self.console_gen}"}})
        elif t == "navigateTo":
            if self.fail_navigates > 0:
                self.fail_navigates -= 1
                self.console_gen += 1
                self._reply({"from": to, "error": "noSuchActor"})
                return
            for tab in self.tabs:
                if tab["actor"] == to or to.startswith(tab["actor"]):
                    tab["url"] = req["url"]
            self._reply({"from": to})
        elif t == "evaluateJSAsync":
            if self.fail_evals > 0:
                self.fail_evals -= 1
                self.console_gen += 1
                self._reply({"from": to, "error": "noSuchActor"})
                return
            self._reply({"from": to, "type": "evaluationResult",
                         "result": self._eval(req.get("text", ""))})
        elif t == "attach":
            self._reply({"from": to,
                         "consoleActor": to + f".console{self.console_gen}"})
        else:
            self._reply({"from": to, "error": "unknownType"})

    @staticmethod
    def _eval(expr):
        if expr == "1+1":
            return {"type": "number", "value": 2}
        if "repeat" in expr:
            return {"type": "longString",
                    "actor": "server1.conn0.longString1",
                    "length": 20000, "initial": ""}
        if expr.startswith("typeof ") and "navigator" not in expr:
            return {"type": "string", "value": "object"}
        if expr == "navigator.webdriver":
            return {"type": "boolean", "value": False}
        if expr == "typeof navigator.webdriver":
            return {"type": "string", "value": "boolean"}
        if "getOwnPropertyDescriptor" in expr:
            return {"type": "string",
                    "value": "function webdriver() { [native code] }"}
        if "getAttribute('webdriver')" in expr:
            return {"type": "string", "value": "null"}
        if "navigator.plugins" in expr:
            return {"type": "number", "value": 1}
        if "cdc_" in expr:
            return {"type": "string", "value": ""}
        if "querySelectorAll" in expr:
            return {"type": "number", "value": 7}
        return {"type": "string", "value": "ok"}


def make_client(**kw):
    kw.setdefault("transport", FakeRDPTransport())
    return RDPClient(0, **kw)


class TestScope(unittest.TestCase):
    def test_in_scope_evaluate_ok(self):
        c = make_client(scope=Scope(tab_ids=[TAB_A]))
        c.attach()
        self.assertEqual(c.evaluate("1+1"), 2)
        c.close()

    def test_out_of_scope_tab_id_refused(self):
        c = make_client(scope=Scope(tab_ids=[TAB_A]))
        with self.assertRaises(RDPError) as cm:
            c.attach(TAB_B)
        self.assertIn("SCOPE REFUSED", str(cm.exception))
        self.assertEqual(len(c._scope_refusals), 1)
        c.close()

    def test_out_of_scope_url_pattern_refused(self):
        c = make_client(scope=Scope(url_patterns=["*page-a*"]))
        c.attach(TAB_A)
        self.assertEqual(c.evaluate("1+1"), 2)
        with self.assertRaises(RDPError) as cm:
            c.get_target(TAB_B)
        self.assertIn("SCOPE REFUSED", str(cm.exception))
        c.close()

    def test_denylist_refused_even_in_scope(self):
        c = make_client(scope=Scope(tab_ids=[TAB_C]),
                        denylist_patterns=list(DEFAULT_CREDENTIAL_DENYLIST))
        with self.assertRaises(RDPError) as cm:
            c.attach(TAB_C)
        self.assertIn("CREDENTIAL TAB REFUSED", str(cm.exception))
        self.assertEqual(len(c._denylist_hits), 1)
        c.close()

    def test_denylist_approval_ok_and_logged(self):
        c = make_client(
            scope=Scope(tab_ids=[TAB_C]),
            denylist_patterns=list(DEFAULT_CREDENTIAL_DENYLIST),
            credential_approvals={TAB_C: "unit test approval"})
        c.attach(TAB_C)
        self.assertEqual(c.evaluate("1+1"), 2)
        report = c.drive_report()
        self.assertTrue(report["approvals_used"],
                        "approval use must be logged in drive report")
        self.assertEqual(report["approvals_used"][0]["note"],
                         "unit test approval")
        c.close()

    def test_navigate_into_denylisted_url_refused(self):
        c = make_client(scope=Scope(tab_ids=[TAB_A]),
                        denylist_patterns=list(DEFAULT_CREDENTIAL_DENYLIST))
        c.attach(TAB_A)
        with self.assertRaises(RDPError) as cm:
            c.navigate("http://localhost/checkout.html")
        self.assertIn("CREDENTIAL TAB REFUSED", str(cm.exception))
        c.close()

    def test_unscoped_warning(self):
        # No scope and no opt-in: refused at construction.
        with self.assertRaises(RDPError) as cm:
            make_client()
        self.assertIn("UNSCOPED REFUSED", str(cm.exception))
        # Explicit opt-in: warns loudly and proceeds.
        err = io.StringIO()
        with redirect_stderr(err):
            c = make_client(unscoped_test=True)
        self.assertIn("UNSCOPED", err.getvalue())
        c.close()
        err = io.StringIO()
        with redirect_stderr(err):
            c = make_client(scope=Scope(tab_ids=[TAB_A]))
        self.assertNotIn("UNSCOPED", err.getvalue())
        c.close()

    def test_drive_report_diff(self):
        fake = FakeRDPTransport()
        c = RDPClient(0, transport=fake, scope=Scope(tab_ids=[TAB_A]))
        c.attach(TAB_A)
        # Mutate the world: B navigates, C closes, D opens. Id sets
        # differ, so the diff keys by (url, title): B's navigation
        # shows as removed old pair + added new pair.
        fake.tabs[1]["url"] = "http://localhost/page-b2.html"
        del fake.tabs[2]
        fake.tabs.append({"actor": "server1.conn0.tabDescriptor4",
                          "url": "http://localhost/page-d.html",
                          "title": "Page D", "selected": False})
        report = c.drive_report()
        diff = report["tab_diff"]
        self.assertEqual(diff["key_mode"], "url_title")
        self.assertEqual(sorted(t["actor"] for t in diff["added"]),
                         [TAB_B, "server1.conn0.tabDescriptor4"])
        self.assertEqual(sorted(t["actor"] for t in diff["removed"]),
                         [TAB_B, TAB_C])
        self.assertEqual(diff["navigated"], [])
        self.assertEqual(report["probe"]["verdict"], "CLEAN")
        self.assertTrue(report["scope"]["scoped"])
        c.close()

    def test_drive_report_diff_id_keyed_when_ids_identical(self):
        fake = FakeRDPTransport()
        c = RDPClient(0, transport=fake, scope=Scope(tab_ids=[TAB_A]))
        c.attach(TAB_A)
        fake.tabs[1]["url"] = "http://localhost/page-b2.html"
        report = c.drive_report()
        diff = report["tab_diff"]
        self.assertEqual(diff["key_mode"], "tab_id")
        self.assertEqual(diff["added"], [])
        self.assertEqual(diff["removed"], [])
        self.assertEqual(len(diff["navigated"]), 1)
        self.assertEqual(diff["navigated"][0]["tab_id"], "tabDescriptor2")
        c.close()

    def test_canon_tab_id_across_connections(self):
        # Scope recorded on conn9 must match the same tab seen on conn0
        # (descriptor actors are per-connection; canonical id strips conn).
        c = make_client(scope=Scope(
            tab_ids=["server1.conn9.tabDescriptor1"]))
        c.attach("tabDescriptor1")
        self.assertEqual(c.evaluate("1+1"), 2)
        c.close()

    def test_attach_by_url(self):
        c = make_client(scope=Scope(url_patterns=["*page-b*"]))
        c.attach(tab_url="page-b")
        self.assertEqual(c.evaluate("1+1"), 2)
        c.close()

    def test_cli_approval_pair_validation(self):
        r = subprocess.run(
            [sys.executable, RDP_CLIENT, "--port", "1",
             "--allow-credential-tab", "x", "probe"],
            capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 2)
        self.assertIn("must be passed together", r.stderr)

    def test_cli_unscoped_warning_and_error_exit(self):
        # No scope, no --unscoped-test: refused before any connection.
        r = subprocess.run(
            [sys.executable, RDP_CLIENT, "--port", "1", "probe"],
            capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 2)
        self.assertIn("UNSCOPED REFUSED", r.stderr)
        self.assertIn("ERROR:", r.stderr)
        # With --unscoped-test: warns loudly, then fails on dead port.
        # I1: runtime errors exit 1 (was 2 for everything).
        r = subprocess.run(
            [sys.executable, RDP_CLIENT, "--port", "1",
             "--unscoped-test", "--allow-unmarked-test-attach", "probe"],
            capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 1)
        self.assertIn("UNSCOPED", r.stderr)
        self.assertIn("ERROR:", r.stderr)

    def test_cli_marker_fail_closed(self):
        # No marker and no test escape: refused before any connection.
        # (--unscoped-test passed so the marker check is what fires.)
        r = subprocess.run(
            [sys.executable, RDP_CLIENT, "--port", "1",
             "--unscoped-test", "probe"],
            capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 2)
        self.assertIn("profile marker is required (fail-closed)",
                      r.stderr)
        # Test-only escape: warns loudly, then fails on the dead port.
        # I1: runtime errors exit 1 (was 2 for everything).
        r = subprocess.run(
            [sys.executable, RDP_CLIENT, "--port", "1",
             "--unscoped-test",
             "--allow-unmarked-test-attach", "probe"],
            capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 1)
        self.assertIn("TEST-ONLY unmarked attach", r.stderr)
        self.assertIn("ERROR:", r.stderr)

    def test_cli_bench_refused_without_unscoped_test(self):
        r = subprocess.run(
            [sys.executable, RDP_CLIENT, "--port", "1",
             "--allow-unmarked-test-attach", "bench",
             "--local-url", "http://localhost/slice.html"],
            capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 2)
        self.assertIn("ERROR:", r.stderr)

    def test_build_scope_denylist_default_on(self):
        import types
        args = types.SimpleNamespace(
            scope_config=None, scope_tab_id=[], scope_url_pattern=[],
            use_default_denylist=False, no_denylist=False,
            allow_credential_tab=[], approval_note=None)
        _scope, deny, _appr = _build_scope(args)
        self.assertEqual(deny, DEFAULT_CREDENTIAL_DENYLIST)
        args.no_denylist = True
        _scope, deny, _appr = _build_scope(args)
        self.assertEqual(deny, [])
        args.use_default_denylist = True
        with self.assertRaises(RDPError):
            _build_scope(args)


class TestNoSuchActorRetry(unittest.TestCase):
    """RT-06: target swap kills the held consoleActor once; the client
    must re-attach pinned to the same tab (never selected-pick) and
    retry once."""

    def test_evaluate_retries_pinned_not_selected(self):
        fake = FakeRDPTransport()
        c = RDPClient(0, transport=fake, scope=Scope(tab_ids=[TAB_B]))
        c.attach(TAB_B)  # background tab; TAB_A is the selected one
        self.assertEqual(c.desc_actor, TAB_B)
        fake.fail_evals = 1  # next evaluate hits the dead actor
        self.assertEqual(c.evaluate("1+1"), 2)
        self.assertEqual(c.desc_actor, TAB_B,
                         "retry must stay on the pinned tab, not selected")
        self.assertEqual(c._retries, 1)
        self.assertTrue(c.console_actor.endswith(".console2"))
        c.close()

    def test_evaluate_second_failure_raises(self):
        fake = FakeRDPTransport()
        c = RDPClient(0, transport=fake, scope=Scope(tab_ids=[TAB_A]))
        c.attach(TAB_A)
        fake.fail_evals = 2  # retry also fails: only one retry allowed
        with self.assertRaises(RDPError) as cm:
            c.evaluate("1+1")
        self.assertIn("noSuchActor", str(cm.exception))
        self.assertEqual(c._retries, 1)
        c.close()

    def test_navigate_retries_pinned(self):
        fake = FakeRDPTransport()
        c = RDPClient(0, transport=fake, scope=Scope(tab_ids=[TAB_B]))
        c.attach(TAB_B)
        # Both actors (target, then descriptor fallback) report the dead
        # actor, so navigate must re-attach pinned and retry once.
        fake.fail_navigates = 2
        c.navigate("http://localhost/page-b2.html")
        self.assertEqual(c.desc_actor, TAB_B)
        self.assertEqual(c._retries, 1)
        tab_b = next(t for t in fake.tabs if t["actor"] == TAB_B)
        self.assertEqual(tab_b["url"], "http://localhost/page-b2.html")
        c.close()

    def test_reattach_missing_pinned_tab_refuses_selected_fallback(self):
        fake = FakeRDPTransport()
        c = RDPClient(0, transport=fake, scope=Scope(tab_ids=[TAB_B]))
        c.attach(TAB_B)
        # Pinned tab closes; selected TAB_A remains. Must refuse, not
        # silently land on the selected tab.
        fake.tabs = [t for t in fake.tabs if t["actor"] != TAB_B]
        fake.fail_evals = 1
        with self.assertRaises(RDPError) as cm:
            c.evaluate("1+1")
        self.assertIn("refusing selected-tab fallback", str(cm.exception))
        c.close()


class TestHardening(unittest.TestCase):
    """L7 hardening: AND scope, lazy tabs, raw-packet guard, parent
    gate, longString, lock, bench gate."""

    def test_scope_and_semantics(self):
        # Both id and URL given: TAB_A id matches but URL pattern does
        # not -> refused. TAB_B URL matches but id does not -> refused.
        c = make_client(scope=Scope(tab_ids=[TAB_A],
                                    url_patterns=["*page-b*"]))
        with self.assertRaises(RDPError) as cm:
            c.attach(TAB_A)
        self.assertIn("SCOPE REFUSED", str(cm.exception))
        with self.assertRaises(RDPError):
            c.get_target(TAB_B)
        c.close()
        # Both match -> ok.
        c = make_client(scope=Scope(tab_ids=[TAB_A],
                                    url_patterns=["*page-a*"]))
        c.attach(TAB_A)
        self.assertEqual(c.evaluate("1+1"), 2)
        c.close()

    def test_lazy_tab_empty_url_denylisted(self):
        tabs = [{"actor": TAB_A, "url": "", "title": "Lazy",
                 "selected": True}]
        c = make_client(transport=FakeRDPTransport(tabs),
                        scope=Scope(tab_ids=[TAB_A]),
                        denylist_patterns=list(DEFAULT_CREDENTIAL_DENYLIST))
        with self.assertRaises(RDPError) as cm:
            c.attach(TAB_A)
        self.assertIn("CREDENTIAL TAB REFUSED", str(cm.exception))
        self.assertEqual(c._denylist_hits[0]["pattern"], LAZY_TAB_PATTERN)
        c.close()
        # Explicit approval covers the lazy tab.
        c = make_client(transport=FakeRDPTransport(
                            [dict(t) for t in tabs]),
                        scope=Scope(tab_ids=[TAB_A]),
                        denylist_patterns=list(DEFAULT_CREDENTIAL_DENYLIST),
                        credential_approvals={TAB_A: "lazy ok"})
        c.attach(TAB_A)
        self.assertEqual(c.evaluate("1+1"), 2)
        c.close()

    def test_approval_by_url_pattern(self):
        c = make_client(
            scope=Scope(tab_ids=[TAB_C]),
            denylist_patterns=list(DEFAULT_CREDENTIAL_DENYLIST),
            credential_approvals={"*login*": "url-keyed approval"})
        c.attach(TAB_C)
        self.assertEqual(c.evaluate("1+1"), 2)
        self.assertTrue(c._approvals_used)
        c.close()

    def test_raw_request_guarded_types_refused(self):
        c = make_client(scope=Scope(tab_ids=[TAB_A]))
        c.attach(TAB_A)
        with self.assertRaises(RDPError) as cm:
            c.request({"to": c.console_actor, "type": "evaluateJSAsync",
                       "text": "1+1"})
        self.assertIn("RAW PACKET REFUSED", str(cm.exception))
        with self.assertRaises(RDPError):
            c.request({"to": c.desc_actor, "type": "navigateTo",
                       "url": "http://localhost/page-b.html"})
        # Guarded methods still work.
        self.assertEqual(c.evaluate("1+1"), 2)
        c.close()

    def test_parent_evaluate_gate_and_audit(self):
        c = make_client(scope=Scope(tab_ids=[TAB_A]))
        c.attach(TAB_A)
        with self.assertRaises(RDPError) as cm:
            c.parent_evaluate("typeof gBrowser")
        self.assertIn("PARENT EVALUATE REFUSED", str(cm.exception))
        c.close()
        c = make_client(scope=Scope(tab_ids=[TAB_A]), allow_parent=True)
        c.attach(TAB_A)
        self.assertEqual(c.parent_evaluate("typeof gBrowser"), "object")
        report = c.drive_report()
        self.assertEqual(len(report["parent_evaluates"]), 1)
        self.assertEqual(report["parent_evaluates"][0]["expr_prefix"],
                         "typeof gBrowser")
        self.assertEqual(report["actions"]["parent_evaluate"], 1)
        c.close()

    def test_long_string_tab_evaluate(self):
        c = make_client(scope=Scope(tab_ids=[TAB_A]))
        c.attach(TAB_A)
        v = c.evaluate("'x'.repeat(20000)")
        self.assertIsInstance(v, str)
        self.assertEqual(len(v), 20000)
        c.close()

    def test_lock_refuses_second_client(self):
        import tempfile
        import os
        path = os.path.join(tempfile.mkdtemp(), "drive.lock")
        c1 = make_client(scope=Scope(tab_ids=[TAB_A]), lock_file=path)
        with self.assertRaises(RDPError) as cm:
            make_client(scope=Scope(tab_ids=[TAB_A]), lock_file=path)
        self.assertIn("LOCK REFUSED", str(cm.exception))
        report = c1.drive_report()
        self.assertEqual(report["lock"]["file"], path)
        self.assertEqual(report["lock"]["holder_pid"], os.getpid())
        c1.close()
        # After release, a new client can take the lock.
        c2 = make_client(scope=Scope(tab_ids=[TAB_A]), lock_file=path)
        c2.close()

    def test_bench_refused_without_unscoped_test(self):
        with self.assertRaises(RDPError) as cm:
            bench(1, None, "http://localhost/slice.html",
                  "https://example.com/", 1,
                  allow_unmarked_test_attach=True)
        self.assertIn("BENCH REFUSED", str(cm.exception))

    def test_reattach_url_mismatch_refused(self):
        fake = FakeRDPTransport()
        c = RDPClient(0, transport=fake, scope=Scope(tab_ids=[TAB_B]))
        c.attach(TAB_B)
        # Positional shift: TAB_B's id now shows a different URL.
        for t in fake.tabs:
            if t["actor"] == TAB_B:
                t["url"] = "http://localhost/other.html"
        fake.fail_evals = 1
        with self.assertRaises(RDPError) as cm:
            c.evaluate("1+1")
        self.assertIn("refusing", str(cm.exception))
        c.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
