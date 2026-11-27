#!/usr/bin/env python3
"""Unit tests for P2a ambiguity-refusing act in rdp_client.py.

Covers: descriptor/action usage validation, the single-eval script
contract (exhaustive count, scan cap, JSON verdict), act() verdict
handling (success returns, refusal raises ActRefusal with the true
count / candidatesTruncated passthrough), refusal envelope shape
(retry=unsafe, result carries the verdict), success disposition,
and CLI pre-connect validation. No browser needed: evaluate() is
stubbed with canned verdicts, the same pattern as WaitForTests.
The live proof (true count 100 on the 300-control fixture) is the
dedicated-session test recorded in the P2a report.
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


def make_client(verdict):
    """Client with evaluate() stubbed to return the canned verdict
    JSON string, capturing the script it was asked to run."""
    client = rc.RDPClient.__new__(rc.RDPClient)
    client._actions = {"evaluate": 0, "navigate": 0, "get_target": 0,
                       "parent_evaluate": 0, "act": 0}
    client._act_refusals = []
    client.scripts = []

    def fake_evaluate(expr, timeout=20):
        client.scripts.append(expr)
        client._actions["evaluate"] += 1
        return verdict if isinstance(verdict, str) else json.dumps(verdict)

    client.evaluate = fake_evaluate
    return client


class UsageValidationTests(unittest.TestCase):
    def test_no_target_is_usage_error(self):
        err = rc._act_usage_error({}, "click", None)
        self.assertEqual(err[0], "act_target_required")

    def test_blank_target_is_usage_error(self):
        err = rc._act_usage_error({"text": "  "}, "click", None)
        self.assertEqual(err[0], "act_target_required")

    def test_type_requires_value(self):
        err = rc._act_usage_error({"label": "Name"}, "type", None)
        self.assertEqual(err[0], "act_value_required")

    def test_type_accepts_empty_value(self):
        self.assertIsNone(rc._act_usage_error({"label": "Name"}, "type", ""))

    def test_click_rejects_value(self):
        err = rc._act_usage_error({"text": "Go"}, "click", "x")
        self.assertEqual(err[0], "act_value_unexpected")

    def test_bad_action(self):
        err = rc._act_usage_error({"text": "Go"}, "hover", None)
        self.assertEqual(err[0], "act_action_invalid")

    def test_valid_click_and_type(self):
        self.assertIsNone(rc._act_usage_error({"text": "Go"}, "click", None))
        self.assertIsNone(
            rc._act_usage_error({"role": "button", "name": "Go"},
                                "click", None))

    def test_act_raises_on_invalid_request(self):
        client = make_client({"acted": True})
        with self.assertRaises(rc.RDPError):
            client.act({}, "click")
        self.assertEqual(client.scripts, [])  # nothing was evaluated


class ScriptContractTests(unittest.TestCase):
    def test_script_embeds_spec_and_counts_exhaustively(self):
        script = rc._act_script({"text": "Action"}, "click")
        self.assertIn('"text": "Action"', script)
        self.assertIn('"action": "click"', script)
        # Exhaustive count + honest truncation, never a capped count.
        self.assertIn("candidatesTruncated", script)
        self.assertIn("SCAN_CAP", script)
        self.assertIn("count !== 1", script)
        self.assertIn("JSON.stringify", script)

    def test_script_never_takes_first_match(self):
        # The only .click() in the script is guarded by count === 1
        # (the refusal branch returns before it), and the candidate
        # pool is built with querySelectorAll (exhaustive), never a
        # singular first-match lookup for the target. (The one
        # querySelector( in labelText is a label-association lookup,
        # not target resolution.)
        script = rc._act_script({"text": "Action"}, "click")
        self.assertLess(script.index("count !== 1"),
                        script.index(".click()"))
        self.assertIn("document.querySelectorAll(spec.selector)", script)

    def test_script_escapes_descriptor_text(self):
        script = rc._act_script({"text": 'a"b\\c'}, "click")
        self.assertIn(json.dumps({"role": None, "name": None,
                                  "text": 'a"b\\c', "selector": None,
                                  "label": None, "action": "click",
                                  "value": None}), script)


class ActVerdictTests(unittest.TestCase):
    def test_unique_target_acts_and_returns_verdict(self):
        client = make_client({"acted": True, "action": "click", "count": 1,
                              "candidatesTruncated": False,
                              "target": {"tag": "button", "role": "button",
                                         "name": "Submit", "text": "Submit"}})
        verdict = client.act({"role": "button", "name": "Submit"}, "click")
        self.assertTrue(verdict["acted"])
        self.assertEqual(verdict["descriptor"]["name"], "Submit")
        self.assertEqual(client._actions["act"], 1)
        self.assertEqual(client._act_refusals, [])

    def test_ambiguous_refusal_carries_true_count(self):
        client = make_client({"acted": False, "reason": "ambiguous",
                              "count": 100, "candidatesTruncated": False,
                              "candidates": [{"tag": "button"}] * 10})
        with self.assertRaises(rc.ActRefusal) as ctx:
            client.act({"text": "Action"}, "click")
        refusal = ctx.exception
        self.assertEqual(refusal.code, "target_ambiguous")
        self.assertEqual(refusal.refusal["count"], 100)
        self.assertFalse(refusal.refusal["candidatesTruncated"])
        self.assertEqual(client._actions["act"], 0)
        self.assertEqual(len(client._act_refusals), 1)
        self.assertEqual(client._act_refusals[0]["count"], 100)

    def test_truncated_flag_passes_through(self):
        client = make_client({"acted": False, "reason": "ambiguous",
                              "count": 4321, "candidatesTruncated": True,
                              "candidates": []})
        with self.assertRaises(rc.ActRefusal) as ctx:
            client.act({"selector": "button"}, "click")
        self.assertTrue(ctx.exception.refusal["candidatesTruncated"])
        self.assertEqual(ctx.exception.refusal["count"], 4321)

    def test_not_found_and_not_editable_codes(self):
        for reason, code in (("not_found", "target_not_found"),
                             ("not_editable", "target_not_editable"),
                             ("bad_selector", "bad_selector")):
            client = make_client({"acted": False, "reason": reason,
                                  "count": 0, "candidatesTruncated": False,
                                  "candidates": []})
            with self.assertRaises(rc.ActRefusal) as ctx:
                client.act({"text": "Nope"}, "click")
            self.assertEqual(ctx.exception.code, code)

    def test_non_string_verdict_is_contract_error(self):
        client = make_client({"acted": True})
        client.evaluate = lambda expr, timeout=20: {"type": "object"}
        with self.assertRaisesRegex(rc.RDPError, "not a string"):
            client.act({"text": "Go"}, "click")

    def test_invalid_json_verdict_is_contract_error(self):
        client = make_client("not json")
        with self.assertRaisesRegex(rc.RDPError, "not valid JSON"):
            client.act({"text": "Go"}, "click")


class EnvelopeTests(unittest.TestCase):
    def test_act_success_disposition(self):
        d = rc._success_disposition("act")
        self.assertEqual(d, {"delivery": "delivered_unverified",
                             "retry": "not_applicable"})

    def test_refusal_envelope_shape_retry_unsafe(self):
        refusal = {"acted": False, "reason": "ambiguous", "count": 100,
                   "candidatesTruncated": False, "candidates": [],
                   "descriptor": {"text": "Action"}, "action": "click"}
        exc = rc.ActRefusal(refusal)
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc._fail("act", exc.code, str(exc), "delivered_verified",
                     "unsafe", 1, False, result=exc.refusal)
        env = json.loads(out.getvalue())
        self.assertFalse(env["ok"])
        self.assertEqual(env["command"], "act")
        self.assertEqual(env["error"]["code"], "target_ambiguous")
        self.assertEqual(env["disposition"]["retry"], "unsafe")
        self.assertEqual(env["disposition"]["delivery"],
                         "delivered_verified")
        self.assertEqual(env["result"]["count"], 100)
        self.assertFalse(env["result"]["candidatesTruncated"])
        self.assertIn("ERROR:", err.getvalue())

    def test_cli_act_without_target_exit_2(self):
        proc = run_cli("--port", "1", "act", "click")
        self.assertEqual(proc.returncode, 2)
        env = json.loads(proc.stdout)
        self.assertEqual(env["error"]["code"], "act_target_required")
        self.assertEqual(env["disposition"]["delivery"], "not_delivered")
        self.assertEqual(env["disposition"]["retry"], "safe")

    def test_cli_act_type_without_value_exit_2(self):
        proc = run_cli("--port", "1", "act", "--label", "Name", "type")
        self.assertEqual(proc.returncode, 2)
        env = json.loads(proc.stdout)
        self.assertEqual(env["error"]["code"], "act_value_required")

    def test_cli_act_click_with_value_exit_2(self):
        proc = run_cli("--port", "1", "act", "--text", "Go", "click", "x")
        self.assertEqual(proc.returncode, 2)
        env = json.loads(proc.stdout)
        self.assertEqual(env["error"]["code"], "act_value_unexpected")


if __name__ == "__main__":
    unittest.main()
