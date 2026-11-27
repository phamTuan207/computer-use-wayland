#!/usr/bin/env python3
"""Unit tests for the I1 CLI envelope in rdp_client.py.

Covers error classification, disposition rules, the refusal
envelopes (no server needed: they fire before connect), exit
codes, and the --legacy-output compat shim.
"""
import io
import json
import subprocess
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rdp_client as rc

CLI = str(Path(__file__).resolve().parent / "rdp_client.py")


def run_cli(*argv):
    return subprocess.run([sys.executable, CLI] + list(argv),
                          capture_output=True, text=True)


class ClassifyTests(unittest.TestCase):
    def test_refusals_are_not_delivered_safe(self):
        for msg, code in (
                ("UNSCOPED REFUSED: x", "unscoped_refused"),
                ("SCOPE REFUSED: x", "scope_refused"),
                ("CREDENTIAL TAB REFUSED: x", "denylist_refused"),
                ("LOCK REFUSED: x", "lock_held"),
                ("port-owner check failed", "port_owner_mismatch")):
            self.assertEqual(rc._classify_error(msg, "eval"),
                             (code, "not_delivered", "safe"))

    def test_evaluate_failure_is_uncertain_unsafe(self):
        self.assertEqual(
            rc._classify_error("evaluate exception: boom", "eval"),
            ("evaluate_failed", "delivery_uncertain", "unsafe"))

    def test_transport_read_vs_action(self):
        self.assertEqual(
            rc._classify_error("RDP socket closed by server", "tabs"),
            ("transport_error", "not_delivered", "safe"))
        self.assertEqual(
            rc._classify_error("RDP socket closed by server", "navigate"),
            ("transport_error", "delivery_uncertain", "unsafe"))

    def test_success_dispositions(self):
        self.assertEqual(rc._success_disposition("tabs")["delivery"],
                         "delivered_verified")
        self.assertEqual(rc._success_disposition("eval")["delivery"],
                         "delivered_unverified")
        self.assertEqual(rc._success_disposition("navigate")["delivery"],
                         "delivered_verified")


class CliEnvelopeTests(unittest.TestCase):
    def test_unscoped_refusal_envelope_exit_2(self):
        proc = run_cli("--port", "1", "tabs")
        self.assertEqual(proc.returncode, 2)
        env = json.loads(proc.stdout)
        self.assertEqual(env["version"], "1")
        self.assertFalse(env["ok"])
        self.assertEqual(env["error"]["code"], "unscoped_refused")
        self.assertEqual(env["disposition"]["delivery"], "not_delivered")
        self.assertIn("ERROR:", proc.stderr)

    def test_missing_marker_envelope_exit_2(self):
        proc = run_cli("--port", "1", "--scope-tab-id", "tabDescriptor1",
                       "tabs")
        self.assertEqual(proc.returncode, 2)
        env = json.loads(proc.stdout)
        self.assertEqual(env["error"]["code"], "profile_marker_required")

    def test_legacy_output_restores_old_shape(self):
        proc = run_cli("--port", "1", "--legacy-output", "tabs")
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(proc.stdout.strip(), "")
        self.assertIn("ERROR: UNSCOPED REFUSED", proc.stderr)

    def test_emit_success_envelope(self):
        out = io.StringIO()
        with redirect_stdout(out):
            rc._emit("tabs", {"tabs": []}, legacy=False)
        env = json.loads(out.getvalue())
        self.assertTrue(env["ok"])
        self.assertEqual(env["result"], {"tabs": []})
        self.assertEqual(env["disposition"]["delivery"],
                         "delivered_verified")

    def test_emit_legacy_is_bare_payload(self):
        out = io.StringIO()
        with redirect_stdout(out):
            rc._emit("tabs", {"tabs": []}, legacy=True)
        self.assertEqual(json.loads(out.getvalue()), {"tabs": []})


class WaitForTests(unittest.TestCase):
    def make_client(self, values):
        client = rc.RDPClient.__new__(rc.RDPClient)
        seq = iter(values)
        client.evaluate = lambda expr, timeout=5: next(seq)
        return client

    def test_wait_for_returns_first_truthy(self):
        client = self.make_client([False, None, "ready"])
        self.assertEqual(client.wait_for("x", timeout=5,
                                         poll_interval=0.01), "ready")

    def test_wait_for_timeout_carries_last_value(self):
        client = self.make_client([False] * 1000)
        with self.assertRaisesRegex(rc.RDPError, "wait_for timeout"):
            client.wait_for("x", timeout=0.05, poll_interval=0.01)

    def test_wait_for_tolerates_transient_errors(self):
        calls = {"n": 0}

        def flaky(expr, timeout=5):
            calls["n"] += 1
            if calls["n"] < 3:
                raise rc.RDPError("context destroyed")
            return True

        client = rc.RDPClient.__new__(rc.RDPClient)
        client.evaluate = flaky
        self.assertTrue(client.wait_for("x", timeout=5,
                                        poll_interval=0.01))

    def test_cli_wait_for_requires_timeout(self):
        proc = run_cli("--port", "1", "--wait-for", "true", "eval", "1")
        self.assertEqual(proc.returncode, 2)
        env = json.loads(proc.stdout)
        self.assertEqual(env["error"]["code"], "wait_timeout_required")

    def test_cli_wait_for_rejected_on_read_command(self):
        proc = run_cli("--port", "1", "--wait-for", "true",
                       "--wait-timeout", "1", "tabs")
        self.assertEqual(proc.returncode, 2)
        env = json.loads(proc.stdout)
        self.assertEqual(env["error"]["code"], "wait_for_unsupported")

    def test_wait_timeout_classification(self):
        self.assertEqual(
            rc._classify_error("wait_for timeout after 1s: 'x'", "eval"),
            ("wait_timeout", "delivered_unverified", "unsafe"))


if __name__ == "__main__":
    unittest.main()
