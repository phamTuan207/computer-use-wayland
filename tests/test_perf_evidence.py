"""Focused E3+R6 checks: checker CLI validates under normal and -O."""
import hashlib
import json
import math
import shutil
import statistics
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
A11Y = ROOT / "docs/benchmarks/r5_a11y_aggregate.json"
PAINT = ROOT / "docs/benchmarks/r5_paint_aggregate.json"


def require(condition, detail=None):
    if not condition:
        raise ValueError(detail if detail is not None else "check failed")


def canonical_samples_hash(samples):
    return hashlib.sha256(json.dumps(
        samples, sort_keys=True, separators=(",", ":"),
        ensure_ascii=False, allow_nan=False).encode("utf-8")).hexdigest()


def refresh_block_hash(block):
    block["samples_sha256"] = canonical_samples_hash(block["samples"])


def run_checker(optimized, *args):
    cmd = [sys.executable] + (["-O"] if optimized else []) + [str(CHECKER)] + [str(a) for a in args]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=300)


def check_valid(optimized):
    proc = run_checker(optimized, MUSE2, MUSE1, DOC, R4)
    require(proc.returncode == 0, proc.stderr[-2000:])
    require("OK: public evidence recomputed" in proc.stdout, proc.stdout[-2000:])
    require("870 measured" in proc.stdout, proc.stdout[-2000:])
    require("1440 measured" in proc.stdout, proc.stdout[-2000:])
    require("960 measured" in proc.stdout, proc.stdout[-2000:])
    require("r5 a11y:" in proc.stdout, proc.stdout[-2000:])
    require("r5 paint:" in proc.stdout, proc.stdout[-2000:])


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


def reject(optimized, *args):
    proc = run_checker(optimized, *args)
    require(proc.returncode != 0, proc.stdout[-2000:])
    require("ValueError" in proc.stderr, proc.stderr[-2000:])
    require("OK: public evidence recomputed" not in proc.stdout, proc.stdout[-2000:])
    return proc


def p95_rank(values):
    ordered = sorted(values)
    return statistics.median(ordered), ordered[math.ceil(0.95 * len(ordered)) - 1]


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
                        block = data["comparisons"][0]["blocks"][0]
                        block["samples"][0]["calls"] = 1
                        refresh_block_hash(block)
                    bad = Path(tmp) / "r5.json"
                    bad.write_text(json.dumps(data))
                    proc = run_checker(optimized, MUSE2, MUSE1, DOC, R4, bad)
                    self.assertNotEqual(proc.returncode, 0, proc.stdout[-2000:])
                    self.assertIn("ValueError", proc.stderr[-2000:])
                    self.assertNotIn("OK: public evidence recomputed", proc.stdout)

    def test_muse2_stale_hash_equal_stats(self):
        # Rank 58/60 bump: median (ranks 30/31) and p95 (rank 57) provably
        # unchanged, so only the co-located hash can reject.
        for optimized in (False, True):
            with self.subTest(optimized=optimized), tempfile.TemporaryDirectory(prefix="perf-r6-muse2-") as tmp:
                data = json.loads(MUSE2.read_text())
                block = data["blocks"][0]
                before = [s["whole_task_ms"] for s in block["samples"]]
                require(len(before) == 60)
                med0, p95_0 = p95_rank(before)
                target = sorted(block["samples"], key=lambda s: s["whole_task_ms"])[57]
                target["whole_task_ms"] += 1000
                after = [s["whole_task_ms"] for s in block["samples"]]
                require(p95_rank(after) == (med0, p95_0), "stats must stay equal")
                bad = Path(tmp) / "muse2.json"
                bad.write_text(json.dumps(data))
                proc = reject(optimized, bad, MUSE1, DOC, R4)
                require("samples_sha256 mismatch" in proc.stderr, proc.stderr[-2000:])

    def test_r5_cdp_reorder_rejected(self):
        # Pure reorder: every pooled stat is order-invariant, hash is not.
        for optimized in (False, True):
            with self.subTest(optimized=optimized), tempfile.TemporaryDirectory(prefix="perf-r6-order-") as tmp:
                data = json.loads(R5.read_text())
                block = data["comparisons"][0]["blocks"][0]
                block["samples"] = list(reversed(block["samples"]))
                bad = Path(tmp) / "r5.json"
                bad.write_text(json.dumps(data))
                reject(optimized, MUSE2, MUSE1, DOC, R4, bad)

    def test_a11y_corruptions(self):
        cases = ("invalid_sample", "row_count", "summary_median",
                 "summary_bytes", "summary_p95", "failed_attempt")
        for optimized in (False, True):
            for corruption in cases:
                with self.subTest(optimized=optimized, corruption=corruption), tempfile.TemporaryDirectory(prefix="perf-r6-a11y-") as tmp:
                    data = json.loads(A11Y.read_text())
                    if corruption == "invalid_sample":
                        block = next(b for b in data["blocks"] if b["route"] == "semantic")
                        block["samples"][0]["png_bytes"] = 1
                        refresh_block_hash(block)
                    elif corruption == "row_count":
                        block = data["blocks"][0]
                        block["samples"].pop()
                        refresh_block_hash(block)
                    elif corruption == "summary_median":
                        data["blocks"][0]["whole_median_ms"] += 1.0
                    elif corruption == "summary_bytes":
                        data["blocks"][0]["png_bytes_total"] += 1
                    elif corruption == "summary_p95":
                        data["blocks"][0]["whole_p95_ms"] += 1.0
                    else:
                        data["failed_attempt01"]["sample0"]["png_count"] = 1
                    bad = Path(tmp) / "a11y.json"
                    bad.write_text(json.dumps(data))
                    reject(optimized, MUSE2, MUSE1, DOC, R4, R5, bad)

    def test_paint_corruptions(self):
        cases = ("invalid_sample", "row_count", "summary_median",
                 "summary_bytes", "summary_p95", "failure_string",
                 "failure_image_rgb")
        for optimized in (False, True):
            for corruption in cases:
                with self.subTest(optimized=optimized, corruption=corruption), tempfile.TemporaryDirectory(prefix="perf-r6-paint-") as tmp:
                    data = json.loads(PAINT.read_text())
                    if corruption == "invalid_sample":
                        block = next(b for b in data["blocks"] if b["n_measured"] == 8)
                        block["samples"][0]["after_rgb"] = [251, 0, 0]
                        refresh_block_hash(block)
                    elif corruption == "row_count":
                        block = next(b for b in data["blocks"] if b["n_measured"] == 8)
                        block["samples"].pop()
                        refresh_block_hash(block)
                    elif corruption == "summary_median":
                        data["summary"][0]["whole_task_ms"]["median"] += 1.0
                    elif corruption == "summary_bytes":
                        data["summary"][0]["core_png_bytes"]["total"] += 1
                    elif corruption == "summary_p95":
                        data["summary"][0]["whole_task_ms"]["p95"] += 1.0
                    elif corruption == "failure_image_rgb":
                        data["failure_images"]["after"]["rgb"] = [0, 251, 0]
                    else:
                        block = next(b for b in data["blocks"] if b["n_measured"] == 1)
                        block["samples"][0]["failure"] = "tampered"
                        refresh_block_hash(block)
                    bad = Path(tmp) / "paint.json"
                    bad.write_text(json.dumps(data))
                    proc = reject(optimized, MUSE2, MUSE1, DOC, R4, R5, A11Y, bad)
                    if corruption == "failure_string":
                        require("R5 paint failure retained" in proc.stderr, proc.stderr[-2000:])


if __name__ == "__main__":
    unittest.main()
