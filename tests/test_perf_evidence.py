"""Focused E3 checks: checker CLI validates under normal and -O."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check-perf-evidence.py"
MUSE2 = ROOT / "docs/benchmarks/muse2_assertion_poll_aggregate.json"
MUSE1 = ROOT / "docs/benchmarks/muse1_historical_aggregate.json"
DOC = ROOT / "docs/optimization-experiments.md"
R4 = ROOT / "docs/benchmarks/r4_isolation_aggregate.json"
R5 = ROOT / "docs/benchmarks/r5_cdp_aggregate.json"


def require(condition, detail=None):
    if not condition:
        raise ValueError(detail if detail is not None else "check failed")


def run_checker(optimized, *args):
    cmd = [sys.executable] + (["-O"] if optimized else []) + [str(CHECKER)] + [str(a) for a in args]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=300)


def check_valid(optimized):
    proc = run_checker(optimized, MUSE2, MUSE1, DOC, R4)
    require(proc.returncode == 0, proc.stderr[-2000:])
    require("OK: public evidence recomputed" in proc.stdout, proc.stdout[-2000:])
    require("870 measured" in proc.stdout, proc.stdout[-2000:])
    require("1440 measured" in proc.stdout, proc.stdout[-2000:])


def check_corrupt(optimized):
    with tempfile.TemporaryDirectory(prefix="perf-evidence-e3-") as tmp:
        bad = Path(tmp) / "muse2.json"
        shutil.copy(MUSE2, bad)
        data = json.loads(bad.read_text())
        data["blocks"][0]["samples"][0]["whole_task_ms"] += 1000
        bad.write_text(json.dumps(data))
        proc = run_checker(optimized, bad, MUSE1, DOC, R4)
        require(proc.returncode != 0, proc.stdout[-2000:])
        require("ValueError" in proc.stderr, proc.stderr[-2000:])
        require("OK: public evidence recomputed" not in proc.stdout, proc.stdout[-2000:])


class EvidenceChecks(unittest.TestCase):
    def test_valid_normal(self):
        check_valid(False)

    def test_valid_optimized(self):
        check_valid(True)

    def test_corrupt_normal(self):
        check_corrupt(False)

    def test_corrupt_optimized(self):
        check_corrupt(True)

    def test_r5_corruption_normal_and_optimized(self):
        for optimized in (False, True):
            for corruption in ("source_hash", "source_commit", "block_hash", "summary", "round_bytes", "calls"):
                with self.subTest(optimized=optimized, corruption=corruption), tempfile.TemporaryDirectory(prefix="perf-r5-") as tmp:
                    data = json.loads(R5.read_text())
                    if corruption == "source_hash":
                        data["sources"]["final-r5"]["runtime_sha256"]["cdp.mjs"] = "0" * 64
                    elif corruption == "source_commit":
                        data["sources"]["final-r5"]["source_git_commit"] = "0" * 40
                    elif corruption == "block_hash":
                        data["comparisons"][0]["blocks"][0]["runtime_sha256"]["cdp.mjs"] = "0" * 64
                    elif corruption == "summary":
                        data["comparisons"][0]["summary"][0]["gain_ms"] += 100
                    elif corruption == "round_bytes":
                        data["comparisons"][0]["summary"][0]["rounds"][0]["bytes"]["A"]["json_total"] += 1
                    else:
                        data["comparisons"][0]["blocks"][0]["samples"][0]["calls"] = 1
                    bad = Path(tmp) / "r5.json"
                    bad.write_text(json.dumps(data))
                    proc = run_checker(optimized, MUSE2, MUSE1, DOC, R4, bad)
                    self.assertNotEqual(proc.returncode, 0, proc.stdout[-2000:])
                    self.assertIn("ValueError", proc.stderr[-2000:])
                    self.assertNotIn("OK: public evidence recomputed", proc.stdout)



if __name__ == "__main__":
    unittest.main()
