"""Tests for scripts/step_watchdog.py (2.3.2, 2.3.3, 2.5.2, 2.5.5)."""
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from step_watchdog import (HEARTBEAT_S, STEP_TIMEOUT_S, WORKER_STALL_S,
                           DirectReporter, StepWatchdog, WorkerStall,
                           watch_until_done)


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class FakeReporter:
    def __init__(self):
        self.reports = []

    def report(self, kind, message, **detail):
        row = {"kind": kind, "message": message, **detail}
        self.reports.append(row)
        return row


class StepWatchdogTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_stuck_reported_once_past_3_5_min(self):
        clock = FakeClock()
        dog = StepWatchdog("r1", clock=clock)
        dog.start_step("delete-dialog")
        clock.advance(STEP_TIMEOUT_S + 1)
        due = dog.check()
        self.assertEqual([d["kind"] for d in due], ["STUCK"])
        self.assertIn("delete-dialog", due[0]["message"])
        self.assertEqual(dog.check(), [])  # reported once, not spammed

    def test_progress_resets_stuck_timer(self):
        clock = FakeClock()
        dog = StepWatchdog("r1", clock=clock)
        dog.start_step("picker")
        clock.advance(200)
        dog.progress("clicked browse")
        clock.advance(200)
        kinds = [d["kind"] for d in dog.check()]
        self.assertNotIn("STUCK", kinds)

    def test_heartbeat_after_5_min_silence(self):
        clock = FakeClock()
        dog = StepWatchdog("r1", clock=clock)
        dog.start_step("long-task")
        clock.advance(HEARTBEAT_S + 1)
        due = dog.check()
        self.assertTrue(any(d["kind"] == "HEARTBEAT" for d in due))

    def test_worker_stall_after_15_min(self):
        clock = FakeClock()
        worker = WorkerStall("w1", clock=clock)
        clock.advance(WORKER_STALL_S + 1)
        self.assertTrue(worker.stalled())
        worker.progress()
        self.assertFalse(worker.stalled())

    def test_direct_reporter_writes_file_and_stdout(self):
        reporter = DirectReporter(self.dir / "reports.jsonl")
        out = io.StringIO()
        with redirect_stdout(out):
            reporter.report("STUCK", "picker stuck", run="r1")
        lines = (self.dir / "reports.jsonl").read_text(
            encoding="utf-8").splitlines()
        row = json.loads(lines[0])
        self.assertEqual(row["kind"], "STUCK")
        self.assertEqual(row["run"], "r1")
        self.assertIn("STUCK", out.getvalue())

    def test_watch_until_done_polls_and_reports_at_once(self):
        reporter = FakeReporter()
        calls = {"n": 0}

        def poll():
            calls["n"] += 1
            return None if calls["n"] < 3 else {"ok": True}

        slept = []
        outcome = watch_until_done(poll, interval=300, clock=slept.append,
                                   reporter=reporter, job="gates2")
        self.assertEqual(outcome, {"ok": True})
        self.assertEqual(calls["n"], 3)
        self.assertEqual(slept, [300, 300])  # every 5 min, stop at done
        self.assertEqual(reporter.reports[0]["kind"], "DONE")


if __name__ == "__main__":
    unittest.main()
