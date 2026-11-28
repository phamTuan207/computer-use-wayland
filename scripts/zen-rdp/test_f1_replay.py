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

from test_scope_unittest import FakeRDPTransport, TAB_A, _packet

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


class SilentTransport(FakeRDPTransport):
    """M1 shape: evaluateJSAsync runs page-side, then the response
    never arrives and recv raises TimeoutError once (stale console
    actor stays silent; the base fake returning empty bytes reads
    as socket-closed, not timeout). bump_gen=True simulates a dead
    actor (re-attach yields a different console actor);
    bump_gen=False simulates slow-but-alive JS (same actor)."""

    def __init__(self, silent_evals=1, bump_gen=True):
        super().__init__()
        self.page_counter = 0
        self.silent_evals = silent_evals
        self.bump_gen = bump_gen
        self._silence_armed = False

    def recv(self, n):
        if self._silence_armed and not self._out:
            self._silence_armed = False
            raise TimeoutError("simulated stale-actor silence")
        return super().recv(n)

    def _handle(self, req):
        if req.get("type") == "evaluateJSAsync":
            self.page_counter += 1  # the script ran page-side
            if self.silent_evals > 0:
                self.silent_evals -= 1
                if self.bump_gen:
                    self.console_gen += 1
                self._silence_armed = True
                return  # no reply: silence
            self._reply({"from": req.get("to"),
                         "type": "evaluationResult",
                         "result": {"type": "number",
                                    "value": self.page_counter}})
            return
        super()._handle(req)


class PartialFrameTransport(FakeRDPTransport):
    """First evaluate response arrives as a partial frame, then
    silence: the client holds bytes in its receive buffer at
    timeout, so the Fix 1 buffer guard must refuse replay."""

    def __init__(self):
        super().__init__()
        self.page_counter = 0
        self._partial_armed = True
        self._silence_armed = False

    def recv(self, n):
        if self._silence_armed and not self._out:
            self._silence_armed = False
            raise TimeoutError("simulated partial-frame silence")
        return super().recv(n)

    def _handle(self, req):
        if req.get("type") == "evaluateJSAsync":
            self.page_counter += 1
            if self._partial_armed:
                self._partial_armed = False
                self.console_gen += 1
                pkt = _packet({"from": req.get("to"),
                               "type": "evaluationResult",
                               "result": {"type": "number", "value": 1}})
                self._out += pkt[:len(pkt) // 2]  # partial frame
                self._silence_armed = True
                return
            self._reply({"from": req.get("to"),
                         "type": "evaluationResult",
                         "result": {"type": "number",
                                    "value": self.page_counter}})
            return
        super()._handle(req)


class LatePacketTransport(FakeRDPTransport):
    """First evaluate response is stashed and delivered during the
    replay (late packet from the dead actor). The sender guard in
    _evaluate_once must skip it so the retry returns the fresh
    result and the next unrelated request stays in sync."""

    def __init__(self):
        super().__init__()
        self.page_counter = 0
        self._stash = None
        self._silence_armed = False
        self._first_eval = True

    def recv(self, n):
        if self._silence_armed and not self._out:
            self._silence_armed = False
            raise TimeoutError("simulated silence before late packet")
        return super().recv(n)

    def _handle(self, req):
        if req.get("type") == "evaluateJSAsync":
            self.page_counter += 1
            if self._first_eval:
                self._first_eval = False
                self.console_gen += 1  # dead actor: replay allowed
                self._stash = {"from": req.get("to"),  # OLD actor
                               "type": "evaluationResult",
                               "result": {"type": "number", "value": 1}}
                self._silence_armed = True
                return
            if self._stash is not None:
                self._reply(self._stash)  # stale packet first
                self._stash = None
            self._reply({"from": req.get("to"),
                         "type": "evaluationResult",
                         "result": {"type": "number",
                                    "value": self.page_counter}})
            return
        super()._handle(req)


class M1TimeoutReplayTests(unittest.TestCase):
    """Fix 1 (M1): TimeoutError replayable for replay=True callers
    only, exactly once, only when re-attach yields a different
    console actor and the receive buffer is clean."""

    def test_silence_replay_false_executes_once(self):
        t = SilentTransport(silent_evals=1, bump_gen=True)
        c = make_client(t)
        c.attach()
        with self.assertRaises(TimeoutError):
            c.evaluate(MARKER, replay=False)
        c.close()
        self.assertEqual(t.page_counter, 1)
        self.assertEqual(c._retries, 0)
        code, delivery, retry = rc._classify_error(
            "simulated stale-actor silence", "eval")
        self.assertEqual((delivery, retry),
                         ("delivery_uncertain", "unsafe"))

    def test_silence_replay_true_recovers_on_dead_actor(self):
        t = SilentTransport(silent_evals=1, bump_gen=True)
        c = make_client(t)
        c.attach()
        value = c.evaluate(MARKER, replay=True)
        c.close()
        self.assertEqual(t.page_counter, 2)
        self.assertEqual(value, 2)
        self.assertEqual(c._retries, 1)

    def test_silence_replay_exactly_once(self):
        # Two silences: the retry also times out; no third attempt.
        t = SilentTransport(silent_evals=2, bump_gen=True)
        c = make_client(t)
        c.attach()
        with self.assertRaises(TimeoutError):
            c.evaluate(MARKER, replay=True)
        c.close()
        self.assertEqual(t.page_counter, 2)
        self.assertEqual(c._retries, 1)

    def test_slow_js_no_replay_same_actor(self):
        # Generation unchanged: re-attach yields the same console
        # actor, so the timeout was slow-but-alive JS. The original
        # TimeoutError propagates and the script never re-runs.
        t = SilentTransport(silent_evals=1, bump_gen=False)
        c = make_client(t)
        c.attach()
        with self.assertRaises(TimeoutError):
            c.evaluate(MARKER, replay=True)
        c.close()
        self.assertEqual(t.page_counter, 1)
        self.assertEqual(c._retries, 0)

    def test_partial_frame_buffer_guard_no_replay(self):
        t = PartialFrameTransport()
        c = make_client(t)
        c.attach()
        with self.assertRaises(TimeoutError):
            c.evaluate(MARKER, replay=True)
        c.close()
        self.assertEqual(t.page_counter, 1)
        self.assertEqual(c._retries, 0)

    def test_late_packet_desync_sender_guard(self):
        t = LatePacketTransport()
        c = make_client(t)
        c.attach()
        value = c.evaluate(MARKER, replay=True)
        # Retry returns the FRESH result (2), not the stale late
        # packet from the dead actor (1).
        self.assertEqual(value, 2)
        # The next unrelated request stays in sync.
        value2 = c.evaluate(MARKER, replay=True)
        c.close()
        self.assertEqual(value2, 3)
        self.assertEqual(t.page_counter, 3)


if __name__ == "__main__":
    unittest.main()
