"""Tests for scripts/task_chain.py (Phase 2.5: 2.5.1, 2.5.3, 2.5.6, 2.5.7, I29, I30)."""
import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from task_chain import (AgentRegistry, PendingReport, TaskChainMonitor,
                        Track2Gate, kill_stuck_agent, launch_detached,
                        pause_all)


class FakeReporter:
    def __init__(self):
        self.reports = []

    def report(self, kind, message, **detail):
        self.reports.append({"kind": kind, "message": message, **detail})


class TaskChainTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.procs = []

    def tearDown(self):
        for proc in self.procs:
            if proc.poll() is None:
                proc.kill()
                proc.wait()
        self.tmp.cleanup()

    def _sleep(self, seconds="60"):
        proc = subprocess.Popen(["sleep", seconds])
        self.procs.append(proc)
        return proc

    def test_launch_detached_runs_without_blocking(self):
        result = launch_detached(["sleep", "30"], self.dir / "job.log")
        self.procs.append(result["proc"])
        self.assertTrue(result["alive"])
        self.assertIsNone(result["proc"].poll())
        self.assertTrue((self.dir / "job.log").exists())

    def test_kill_stuck_agent_kills_and_reports(self):
        proc = self._sleep()
        registry = AgentRegistry(self.dir / "agents.json")
        registry.register("stuck-1", pid=proc.pid, command="sleep 60")
        # Fake 20 idle minutes: no progress since registration.
        registry.agents["stuck-1"]["last_progress_mono"] = \
            time.monotonic() - 1200
        registry._save()
        reporter = FakeReporter()
        outcome = kill_stuck_agent(registry, "stuck-1", reporter=reporter)
        self.assertTrue(outcome["ok"])
        self.assertIsNotNone(proc.poll())  # actually dead
        self.assertEqual(reporter.reports[0]["kind"], "KILL-STUCK")
        self.assertEqual(registry.agents["stuck-1"]["status"], "killed")

    def test_kill_stuck_agent_refuses_when_not_stuck(self):
        proc = self._sleep()
        registry = AgentRegistry(self.dir / "agents.json")
        registry.register("busy-1", pid=proc.pid, command="sleep 60")
        outcome = kill_stuck_agent(registry, "busy-1")
        self.assertFalse(outcome["ok"])
        self.assertIsNone(proc.poll())  # still alive, correctly spared

    def test_pause_all_stops_dispatched_agents(self):
        procs = [self._sleep() for _ in range(2)]
        registry = AgentRegistry(self.dir / "agents.json")
        for i, proc in enumerate(procs):
            registry.register(f"a{i}", pid=proc.pid, command="sleep 60")
        outcomes = pause_all(registry)
        self.assertTrue(all(o["stopped"] for o in outcomes))
        self.assertTrue(all(p.poll() is not None for p in procs))

    def test_chain_starts_next_task_when_dependency_done(self):
        reporter = FakeReporter()
        monitor = TaskChainMonitor(self.dir / "chain.json",
                                   reporter=reporter)
        monitor.add("problem-2-fix", depends_on=None)
        monitor.add("problem-3", depends_on="problem-2-fix")
        monitor.set_status("problem-2-fix", "running")
        statuses = {"problem-2-fix": "running"}
        started = []

        def status_fn(task):
            return statuses[task]

        self.assertEqual(monitor.check(status_fn, started.append), [])
        statuses["problem-2-fix"] = "done"
        self.assertEqual(monitor.check(status_fn, started.append),
                         ["problem-3"])
        self.assertEqual(started, ["problem-3"])
        self.assertEqual(reporter.reports[0]["kind"], "CHAIN-START")

    def test_pending_report_queue_survives_and_delivers(self):
        queue = PendingReport(self.dir / "pending.json")
        queue.queue("overnight results", "3 tasks done, 1 blocked")
        self.assertEqual(len(queue.pending()), 1)
        delivered = queue.deliver()
        self.assertEqual(delivered[0]["title"], "overnight results")
        self.assertEqual(queue.pending(), [])  # cleared after delivery

    def test_track2_gate_defaults_paused_and_needs_unanimous_go(self):
        gate = Track2Gate(self.dir / "gate.json")
        self.assertFalse(gate.may_run())  # no gate file: PAUSED
        gate.record_go(council_date="2026-11-21", redteam_date="2026-11-21")
        self.assertTrue(gate.may_run())
        gate.record_pause("council has not met")
        self.assertFalse(gate.may_run())
        # GO without unanimity is still PAUSED.
        (self.dir / "gate.json").write_text(json.dumps(
            {"status": "GO", "council_unanimous": True,
             "redteam_unanimous": False}), encoding="utf-8")
        self.assertFalse(gate.may_run())


if __name__ == "__main__":
    unittest.main()
