#!/usr/bin/env python3
"""RT-20 scope tests for rdp_client.py (stdlib unittest, fake transport).

Covers: in-scope evaluate ok, out-of-scope refused (id + URL pattern),
denylist refused, denylist+approval ok and logged, unscoped warning,
drive-report diff correctness, CLI approval-pair validation, fail-closed
profile marker, and tab-pinned noSuchActor retry (RT-06: DevTools close
swaps the tab target and kills the held consoleActor once).

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

from rdp_client import (DEFAULT_CREDENTIAL_DENYLIST, RDPClient, RDPError,
                        Scope)

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
        err = io.StringIO()
        with redirect_stderr(err):
            c = make_client()
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
        # Mutate the world: B navigates, C closes, D opens.
        fake.tabs[1]["url"] = "http://localhost/page-b2.html"
        del fake.tabs[2]
        fake.tabs.append({"actor": "server1.conn0.tabDescriptor4",
                          "url": "http://localhost/page-d.html",
                          "title": "Page D", "selected": False})
        report = c.drive_report()
        diff = report["tab_diff"]
        self.assertEqual([t["actor"] for t in diff["added"]],
                         ["server1.conn0.tabDescriptor4"])
        self.assertEqual([t["actor"] for t in diff["removed"]], [TAB_C])
        self.assertEqual(len(diff["navigated"]), 1)
        self.assertEqual(diff["navigated"][0]["tab_id"], "tabDescriptor2")
        self.assertEqual(report["probe"]["verdict"], "CLEAN")
        self.assertTrue(report["scope"]["scoped"])
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
            [sys.executable, "rdp_client.py", "--port", "1",
             "--allow-credential-tab", "x", "probe"],
            capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 2)
        self.assertIn("must be passed together", r.stderr)

    def test_cli_unscoped_warning_and_error_exit(self):
        r = subprocess.run(
            [sys.executable, "rdp_client.py", "--port", "1", "probe"],
            capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 2)
        self.assertIn("UNSCOPED", r.stderr)
        self.assertIn("ERROR:", r.stderr)

    def test_cli_marker_fail_closed(self):
        # No marker and no test escape: refused before any connection.
        r = subprocess.run(
            [sys.executable, "rdp_client.py", "--port", "1", "probe"],
            capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 2)
        self.assertIn("profile marker is required (fail-closed)",
                      r.stderr)
        # Test-only escape: warns loudly, then fails on the dead port.
        r = subprocess.run(
            [sys.executable, "rdp_client.py", "--port", "1",
             "--allow-unmarked-test-attach", "probe"],
            capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 2)
        self.assertIn("TEST-ONLY unmarked attach", r.stderr)
        self.assertIn("ERROR:", r.stderr)


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


if __name__ == "__main__":
    unittest.main(verbosity=2)
