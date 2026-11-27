#!/usr/bin/env python3
"""F11 terminal-death flag tests for rdp_client.py (stdlib unittest,
fake transport, no browser needed).

F11 (improvements/p3-event-feed-measurements-20261128.md, decision
2026-11-28): when a demux-skipped packet is descriptor-destroyed for
the pinned descriptor, the client records a terminal flag;
wait_for/wait_load check it each poll iteration and fail fast with a
tab-destroyed classification instead of burning their budget (M8
shape: evaluate on the dead tab's console returns falsy, never
errors). evaluate(replay=True) must not replay past the flag.

Covers: pinned-tab destroyed sets the flag and fails waits fast;
other-tab destroyed is ignored; storm-shaped interleave keeps
request/evaluate pairing; navigation packets never set the flag;
the flag does not survive reconnect and is cleared by a successful
attach; the replay guard; the error classifier; malformed packets
never raise in the observation.

Run: python3 -m unittest test_f11_terminal -v
No browser needed. ydotool is banned (not used).
"""
import time
import unittest

from rdp_client import RDPClient, RDPError, _classify_error
from test_scope_unittest import FakeRDPTransport, TAB_A, TAB_B, TAB_C


class F11Transport(FakeRDPTransport):
    """FakeRDPTransport plus unsolicited-packet injection: packets in
    inject_next are emitted before the reply to the next handled
    request, mimicking events arriving inside a demux wait."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inject_next = []
        self.eval_count = 0

    def _handle(self, req):
        if req.get("type") == "evaluateJSAsync":
            self.eval_count += 1
        for packet in self.inject_next:
            self._reply(packet)
        self.inject_next = []
        super()._handle(req)

    @staticmethod
    def _eval(expr):
        if "neverAppears" in expr:
            return {"type": "boolean", "value": False}
        if "readyState" in expr:
            return {"type": "string",
                    "value": "loading|http://localhost/page-a.html"}
        return FakeRDPTransport._eval(expr)


def destroyed(actor):
    return {"from": actor, "type": "descriptor-destroyed"}


def make_client():
    transport = F11Transport()
    client = RDPClient(0, transport=transport, unscoped_test=True,
                       warn_unscoped=False)
    client.attach()
    assert client.desc_actor == TAB_A
    return client, transport


class TestF11TerminalFlag(unittest.TestCase):
    def test_pinned_destroyed_fails_wait_for_fast(self):
        c, t = make_client()
        t.inject_next = [destroyed(TAB_A)]
        start = time.monotonic()
        with self.assertRaises(RDPError) as cm:
            c.wait_for("neverAppears", timeout=8)
        elapsed = time.monotonic() - start
        self.assertIn("tab destroyed", str(cm.exception))
        self.assertLess(elapsed, 1.5)
        self.assertIsNotNone(c._terminal_destroyed)
        c.close()

    def test_pinned_destroyed_fails_wait_load_fast(self):
        c, t = make_client()
        t.inject_next = [destroyed(TAB_A)]
        start = time.monotonic()
        with self.assertRaises(RDPError) as cm:
            c.wait_load("page-a", timeout=8)
        elapsed = time.monotonic() - start
        self.assertIn("tab destroyed", str(cm.exception))
        self.assertLess(elapsed, 1.5)
        c.close()

    def test_flag_set_before_wait_fails_without_evaluating(self):
        c, t = make_client()
        c._observe_skipped(destroyed(TAB_A))
        with self.assertRaises(RDPError) as cm:
            c.wait_for("neverAppears", timeout=8)
        self.assertIn("tab destroyed", str(cm.exception))
        self.assertEqual(t.eval_count, 0)
        c.close()

    def test_other_tab_destroyed_ignored(self):
        c, t = make_client()
        t.inject_next = [destroyed(TAB_B), destroyed(TAB_C)]
        with self.assertRaises(RDPError) as cm:
            c.wait_for("neverAppears", timeout=0.3)
        self.assertIn("wait_for timeout", str(cm.exception))
        self.assertIsNone(c._terminal_destroyed)
        c.close()

    def test_navigation_packets_never_set_flag(self):
        c, t = make_client()
        t.inject_next = [
            {"from": TAB_A, "type": "tabNavigated", "state": "start"},
            {"from": "root", "type": "tabListChanged"},
            {"from": TAB_A, "type": "frameUpdate"},
        ]
        with self.assertRaises(RDPError) as cm:
            c.wait_for("neverAppears", timeout=0.3)
        self.assertIn("wait_for timeout", str(cm.exception))
        self.assertIsNone(c._terminal_destroyed)
        c.close()

    def test_storm_interleave_pairing_unchanged(self):
        c, t = make_client()
        storm = []
        for i in range(50):
            storm.append({"from": "root", "type": "tabListChanged"})
            storm.append({"from": TAB_B, "type": "frameUpdate"})
            storm.append(destroyed(TAB_B if i % 2 else TAB_C))
            # resultID acks carry no "type" key (M4 inventory shape).
            storm.append({"from": TAB_A + ".console1", "resultID": i})
        t.inject_next = storm
        # evaluate pairing: the real result still wins.
        self.assertEqual(c.evaluate("1+1"), 2)
        # request pairing: listTabs still returns the tab list.
        t.inject_next = storm
        tabs, _sel = c.list_tabs()
        self.assertEqual(len(tabs), 3)
        # destroyed packets were all for other tabs: no flag.
        self.assertIsNone(c._terminal_destroyed)
        c.close()

    def test_request_skip_path_observes(self):
        c, t = make_client()
        t.inject_next = [destroyed(TAB_A)]
        c.list_tabs()
        self.assertIsNotNone(c._terminal_destroyed)
        self.assertEqual(c._terminal_destroyed["descriptor"], TAB_A)
        c.close()

    def test_replay_guard_never_replays_past_flag(self):
        c, t = make_client()
        t.fail_evals = 1
        t.inject_next = [destroyed(TAB_A)]
        with self.assertRaises(RDPError) as cm:
            c.evaluate("1+1")
        self.assertIn("tab destroyed", str(cm.exception))
        self.assertEqual(c._retries, 0)
        c.close()

    def test_flag_cleared_by_successful_attach(self):
        c, t = make_client()
        c._observe_skipped(destroyed(TAB_A))
        self.assertIsNotNone(c._terminal_destroyed)
        c.get_target(TAB_B)
        self.assertIsNone(c._terminal_destroyed)
        self.assertEqual(c.evaluate("1+1"), 2)
        c.close()

    def test_flag_does_not_survive_reconnect(self):
        c, t = make_client()
        c._observe_skipped(destroyed(TAB_A))
        self.assertIsNotNone(c._terminal_destroyed)
        c.close()
        c2, _t2 = make_client()
        self.assertIsNone(c2._terminal_destroyed)
        c2.close()

    def test_malformed_packets_never_raise(self):
        c, t = make_client()
        for packet in ({}, {"type": "descriptor-destroyed"},
                       {"type": "descriptor-destroyed", "from": None},
                       {"from": TAB_A}, {"type": 42, "from": TAB_A}):
            c._observe_skipped(packet)
        self.assertIsNone(c._terminal_destroyed)
        c.close()

    def test_classifier_tab_destroyed(self):
        code, _delivery, _retry = _classify_error(
            "tab destroyed: descriptor 'x' destroyed during "
            "wait_for (terminal, F11)", "eval")
        self.assertEqual(code, "tab_destroyed")
        code2, _d2, _r2 = _classify_error(
            "wait_for timeout after 8s: 'x' last value None", "eval")
        self.assertEqual(code2, "wait_timeout")


if __name__ == "__main__":
    unittest.main()
