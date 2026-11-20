"""Tests for scripts/timing.py (Phase 2.3: 2.3.1, 2.3.4, 2.3.5)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from timing import (MIN_ACTIONS_PER_CALL, SLOW_THINK_S,
                    SMALL_TASK_BUDGET_S, TimingLogger)


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class TimingTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_jsonl_append_repairs_missing_trailing_newline(self):
        path = self.dir / "run.jsonl"
        path.write_text('{"event": "step", "step": "old"}', encoding="utf-8")
        clock = FakeClock()
        log = TimingLogger(path, "r1", clock=clock)
        with log.think_step("s1"):
            clock.advance(1.0)
        rows = [json.loads(line) for line in
                path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(rows[0]["step"], "old")
        self.assertEqual(rows[1]["event"], "step")
        self.assertEqual(rows[1]["step"], "s1")

    def test_think_act_split_is_measured(self):
        clock = FakeClock()
        log = TimingLogger(self.dir / "t.jsonl", "r1", clock=clock)
        with log.think_step("find-button") as step:
            clock.advance(45.0)  # deciding
            step.act()
            clock.advance(5.0)   # executing
            log.note_action("click", x=837, y=850)
        row = log.steps[0]
        self.assertEqual(row["think_s"], 45.0)
        self.assertEqual(row["act_s"], 5.0)
        self.assertFalse(row["slow_think"])
        self.assertEqual(row["actions"], 1)

    def test_slow_think_flagged_over_60s(self):
        clock = FakeClock()
        log = TimingLogger(self.dir / "t.jsonl", "r1", clock=clock)
        with log.think_step("delete-dialog"):
            clock.advance(SLOW_THINK_S + 10)
        self.assertTrue(log.steps[0]["slow_think"])
        self.assertEqual(log.pace()["slow_steps"], 1)

    def test_pace_flags_few_clicks_many_calls(self):
        # I16: 6 model calls, almost no clicks. That pattern must flag.
        clock = FakeClock()
        log = TimingLogger(self.dir / "t.jsonl", "r1", clock=clock)
        for _ in range(6):
            log.note_model_call()
        log.note_action("click", x=1, y=2)
        pace = log.pace()
        self.assertEqual(pace["actions_per_call"], round(1 / 6, 3))
        self.assertLess(pace["actions_per_call"], MIN_ACTIONS_PER_CALL)
        self.assertTrue(pace["slow_think"])

    def test_summary_flags_small_task_over_5_min(self):
        clock = FakeClock()
        log = TimingLogger(self.dir / "t.jsonl", "r1", clock=clock)
        with log.think_step("only-step"):
            clock.advance(SMALL_TASK_BUDGET_S + 60)
        summary = log.summary()
        self.assertTrue(summary["over_small_task_budget"])
        self.assertEqual(summary["steps"], 1)
        self.assertEqual(summary["think_max_s"], SMALL_TASK_BUDGET_S + 60)


if __name__ == "__main__":
    unittest.main()
