#!/usr/bin/env python3
"""Tests for pre-freeze-gate.py (M11d wrapper).

The happy path runs the gate against the repo's real frozen
list and keys (the list doc is the fixture; verify-list.py
already proves its own checks). The failure paths use
synthetic temp files: a frozen-heads file with a wrong hash,
and triage records missing required sections.
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATE = HERE / "pre-freeze-gate.py"

GOOD_RECORD = """# Pre-freeze triage record (test)

## Mandatory bar
A text change is MANDATORY only when the task as written
cannot be passed, cannot be scored, or can be scored only
by violating the spec.

## Classification
| Task | Class | Disposition |
|---|---|---|
| R3-000 | (c) No action | test row |

## Freeze decision
Gate PASS. Freeze commit recorded separately.

## Catch rate
Filled after the run.
"""


def run_gate(extra=()):
    return subprocess.run([sys.executable, str(GATE)] + list(extra),
                          capture_output=True, text=True)


class PreFreezeGateTests(unittest.TestCase):
    def test_real_repo_state_passes(self):
        proc = run_gate()
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("PRE-FREEZE GATE: PASS", proc.stdout)
        self.assertIn("RESULT: 62 pass, 0 pending, 0 fail",
                      proc.stdout)

    def test_wrong_frozen_hash_fails_at_verify_step(self):
        with tempfile.TemporaryDirectory() as d:
            frozen = Path(d) / "frozen-heads.txt"
            frozen.write_text("list_sha256 " + "0" * 64 + "\n")
            proc = run_gate(["--frozen", str(frozen)])
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("PRE-FREEZE GATE FAIL: verify-list",
                          proc.stdout)
            self.assertIn("list sha256 matches frozen-heads.txt",
                          proc.stdout)

    def test_good_triage_record_passes(self):
        with tempfile.TemporaryDirectory() as d:
            record = Path(d) / "record.md"
            record.write_text(GOOD_RECORD)
            proc = run_gate(["--triage-record", str(record)])
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertIn("PRE-FREEZE GATE: PASS", proc.stdout)

    def test_record_missing_bar_fails(self):
        with tempfile.TemporaryDirectory() as d:
            record = Path(d) / "record.md"
            record.write_text("## Classification\nnone\n"
                              "## Freeze decision\nnone\n")
            proc = run_gate(["--triage-record", str(record)])
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("PRE-FREEZE GATE FAIL: triage-record",
                          proc.stdout)
            self.assertIn("## Mandatory bar", proc.stdout)

    def test_missing_record_file_fails(self):
        proc = run_gate(["--triage-record", "/nonexistent/x.md"])
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("triage record missing", proc.stdout)


if __name__ == "__main__":
    unittest.main()
