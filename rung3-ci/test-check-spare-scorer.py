#!/usr/bin/env python3
"""Tests for check-spare-scorer.py (M10 reduced spare scorer)."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CHECKER = HERE / "check-spare-scorer.py"
REAL_SIGNOFF = "rung3-run-log/r3-l3-clone2-calibration-signoff-20261126.md"


def valid_record():
    return {
        "run_code": "R3-L9",
        "coordinator_session": "sess-coordinator",
        "runner_sessions": ["sess-runner-1", "sess-runner-2"],
        "seated_scorer_sessions": ["sess-scorer-1a", "sess-scorer-2a",
                                   "sess-scorer-1b", "sess-scorer-2b"],
        "spare_scorers": [
            {
                "name": "spare-1",
                "session": "sess-spare",
                "independence_declaration": True,
                "calibration": {
                    "signoff_file": REAL_SIGNOFF,
                    "agreement": "4/4",
                    "verdict": "APPROVED",
                    "verifier_session": "sess-verifier",
                    "signed_at": "2026-11-28T09:00:00+07:00",
                },
                "standing_warm_seat": False,
                "first_assignment_at": None,
            }
        ],
    }


def run_checker(record):
    with tempfile.NamedTemporaryFile("w", suffix=".json",
                                     delete=False) as fh:
        json.dump(record, fh)
        path = fh.name
    return subprocess.run([sys.executable, str(CHECKER), path],
                          capture_output=True, text=True, cwd=ROOT)


class SpareScorerTests(unittest.TestCase):
    def test_valid_record_passes_on_real_signoff(self):
        # The referenced sign-off is the real R3-L3 clone2 file: it
        # carries 4/4 agreement and an APPROVED verdict.
        proc = run_checker(valid_record())
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("SPARE SCORER OK", proc.stdout)

    def test_assignment_after_signoff_passes(self):
        rec = valid_record()
        rec["spare_scorers"][0]["first_assignment_at"] = \
            "2026-11-29T10:00:00+07:00"
        proc = run_checker(rec)
        self.assertEqual(proc.returncode, 0, proc.stdout)

    def test_two_spares_fail(self):
        rec = valid_record()
        second = copy.deepcopy(rec["spare_scorers"][0])
        second["name"] = "spare-2"
        second["session"] = "sess-spare-2"
        rec["spare_scorers"].append(second)
        proc = run_checker(rec)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("exactly one named spare", proc.stdout)

    def test_spare_session_colliding_with_runner_fails(self):
        rec = valid_record()
        rec["spare_scorers"][0]["session"] = "sess-runner-1"
        proc = run_checker(rec)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("already a runner or seated scorer", proc.stdout)

    def test_under_bar_calibration_fails(self):
        rec = valid_record()
        rec["spare_scorers"][0]["calibration"]["agreement"] = "3/4"
        proc = run_checker(rec)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("must be 4/4", proc.stdout)

    def test_missing_signoff_file_fails(self):
        rec = valid_record()
        rec["spare_scorers"][0]["calibration"]["signoff_file"] = \
            "rung3-run-log/no-such-signoff.md"
        proc = run_checker(rec)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("sign-off file not found", proc.stdout)

    def test_warm_seat_fails(self):
        rec = valid_record()
        rec["spare_scorers"][0]["standing_warm_seat"] = True
        proc = run_checker(rec)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("no standing warm seat", proc.stdout)

    def test_assignment_before_signoff_fails(self):
        rec = valid_record()
        rec["spare_scorers"][0]["first_assignment_at"] = \
            "2026-11-28T08:00:00+07:00"
        proc = run_checker(rec)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("precedes calibration sign-off", proc.stdout)

    def test_cap_hours_claim_fails(self):
        rec = valid_record()
        rec["cap_hours_saved"] = 18
        proc = run_checker(rec)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("claims no cap hours", proc.stdout)

    def test_verifier_equal_to_coordinator_fails(self):
        rec = valid_record()
        rec["spare_scorers"][0]["calibration"]["verifier_session"] = \
            "sess-coordinator"
        proc = run_checker(rec)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("verifier session equals coordinator", proc.stdout)


if __name__ == "__main__":
    unittest.main()
