#!/usr/bin/env python3
"""Tests for probes/probe-gate.py (M14). Run:
python3 probes/test-probe-gate.py
Covers both directions: compliant passes; missing ledger row,
missing field, changed probe file, and invalid ledger fail."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATE = HERE / "probe-gate.py"
PROBE_REL = "tests/y1b_probes_rewritten.py"
GOOD_ROW = {
    "date": "2026-11-27",
    "probe": PROBE_REL,
    "question": "Do the rewritten Y1b probes discriminate?",
    "result": "4/4 PASS",
    "output": "improvements/worker-click5-y1b-probe-log.md",
    "verdict": "M14 gate v1 frozen suite",
}


def run_gate(ledger, probe, sha):
    return subprocess.run(
        [sys.executable, str(GATE), "--ledger", str(ledger),
         "--probe", str(probe), "--expected-sha256", sha],
        capture_output=True, text=True)


class ProbeGateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.probe = d / "probe.py"
        self.probe.write_text("# frozen probe stand-in\n")
        self.sha = hashlib.sha256(self.probe.read_bytes()).hexdigest()
        self.ledger = d / "ledger.jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def write_ledger(self, rows):
        self.ledger.write_text(
            "".join(json.dumps(r) + "\n" for r in rows))

    def test_compliant_passes(self):
        self.write_ledger([GOOD_ROW])
        proc = run_gate(self.ledger, self.probe, self.sha)
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("PROBE GATE PASS", proc.stdout)

    def test_missing_row_fails(self):
        self.write_ledger([])
        proc = run_gate(self.ledger, self.probe, self.sha)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("no ledger row", proc.stdout)

    def test_missing_field_fails(self):
        row = dict(GOOD_ROW)
        del row["verdict"]
        self.write_ledger([row])
        proc = run_gate(self.ledger, self.probe, self.sha)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("missing field", proc.stdout)

    def test_changed_probe_fails(self):
        self.write_ledger([GOOD_ROW])
        self.probe.write_text("# tampered\n")
        proc = run_gate(self.ledger, self.probe, self.sha)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("probe file changed", proc.stdout)

    def test_invalid_ledger_fails(self):
        self.ledger.write_text("{not json\n")
        proc = run_gate(self.ledger, self.probe, self.sha)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("LEDGER INVALID", proc.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
