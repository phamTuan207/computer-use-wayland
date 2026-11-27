#!/usr/bin/env python3
"""F1 fault-injection tests: a lost response after execution must
never re-fire a non-idempotent evaluate (pain-point meeting
2026-11-28 BUILD NOW item 2; defines "F1 closure" for the P2b
gate).

The fake transport executes the script page-side (a counter the
test reads back) and then loses the response as noSuchActor with
a console-generation bump, exactly the RT-06 shape that makes
evaluate(replay=True) re-attach and run the script a second
time. Non-idempotent callers (act, CLI eval) run replay=False:
the counter must stay 1 and the error must classify
delivery_uncertain/unsafe. The replay=True control proves the
harness can catch a double execution (counter 2).
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rdp_client as rc
from rdp_client import RDPClient, RDPError, Scope

from test_scope_unittest import FakeRDPTransport, TAB_A

MARKER = "window.__f1 = (window.__f1 || 0) + 1"


class ExecuteThenDieTransport(FakeRDPTransport):
    """evaluateJSAsync runs page-side (page_counter += 1), then the
    response is lost: noSuchActor + console generation bump, so a
    replaying client re-attaches to a fresh console actor."""

    def __init__(self, die_times=1):
        super().__init__()
        self.page_counter = 0
        self.die_times = die_times

    def _handle(self, req):
        if req.get("type") == "evaluateJSAsync":
            self.page_counter += 1  # the script ran page-side
            if self.die_times > 0:
                self.die_times -= 1
                self.console_gen += 1
                self._reply({"from": req.get("to"),
                             "error": "noSuchActor"})
                return
            self._reply({"from": req.get("to"),
                         "type": "evaluationResult",
                         "result": {"type": "number",
                                    "value": self.page_counter}})
            return
        super()._handle(req)


def make_client(transport):
    return RDPClient(0, transport=transport,
                     scope=Scope(tab_ids=[TAB_A]),
                     denylist_patterns=[])


class F1ReplayTests(unittest.TestCase):
    def test_replay_false_executes_exactly_once(self):
        t = ExecuteThenDieTransport(die_times=1)
        c = make_client(t)
        c.attach()
        with self.assertRaises(RDPError):
            c.evaluate(MARKER, replay=False)
        c.close()
        self.assertEqual(t.page_counter, 1,
                         "non-idempotent evaluate re-fired after a "
                         "lost response (F1 double execution)")

    def test_replay_true_control_double_executes(self):
        # Control: the same fault with replay=True (read paths) DOES
        # run the script twice. If this ever stops being true the
        # harness above proves nothing.
        t = ExecuteThenDieTransport(die_times=1)
        c = make_client(t)
        c.attach()
        value = c.evaluate(MARKER, replay=True)
        c.close()
        self.assertEqual(t.page_counter, 2)
        self.assertEqual(value, 2)

    def test_lost_response_classifies_unsafe(self):
        t = ExecuteThenDieTransport(die_times=1)
        c = make_client(t)
        c.attach()
        with self.assertRaises(RDPError) as cm:
            c.evaluate(MARKER, replay=False)
        c.close()
        code, delivery, retry = rc._classify_error(str(cm.exception),
                                                   "eval")
        self.assertEqual((delivery, retry),
                         ("delivery_uncertain", "unsafe"))

    def test_act_never_replays(self):
        # act() already runs replay=False (P2a); pin it under the
        # same fault: the act script executes once, transport error
        # propagates, no second execution.
        t = ExecuteThenDieTransport(die_times=1)
        c = make_client(t)
        c.attach()
        with self.assertRaises(RDPError):
            c.act({"text": "Go"}, "click")
        c.close()
        self.assertEqual(t.page_counter, 1)

    def test_cli_eval_passes_replay_false(self):
        # Source contract: the CLI eval branch is the arbitrary-JS
        # caller and must pin replay=False (F1 audit 2026-11-28).
        src = Path(rc.__file__).read_text()
        branch = src.split('elif args.cmd == "eval":', 1)[1]
        branch = branch.split("elif args.cmd ==", 1)[0]
        self.assertIn("replay=False", branch)


if __name__ == "__main__":
    unittest.main()
