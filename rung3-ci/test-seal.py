#!/usr/bin/env python3
"""Tests for seal.py (M2 one-pass wrapper) with fake evidence."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEAL = HERE / "seal.py"


def make_case(root, complete=True):
    ev_root = root / "evidence"
    snap_root = root / "snapshots"
    task_dir = ev_root / "T-01"
    task_dir.mkdir(parents=True)
    snap_root.mkdir()
    if complete:
        (task_dir / "bao-cao.txt").write_text("report\n")
        (task_dir / "shot-20261127-120000.png").write_bytes(b"\x89PNG-fake")
    reqs = {"T-01": {"files": ["bao-cao.txt"], "patterns": [],
                     "screenshots_min": 1}}
    req_path = root / "reqs.json"
    req_path.write_text(json.dumps(reqs))
    return ev_root, snap_root, req_path


def run_seal(ev_root, snap_root, req_path, extra=()):
    return subprocess.run(
        [sys.executable, str(SEAL), "T-01",
         "--evidence-root", str(ev_root),
         "--snapshot-root", str(snap_root),
         "--requirements", str(req_path)] + list(extra),
        capture_output=True, text=True)


class SealTests(unittest.TestCase):
    def test_happy_path_seals_and_gate_passes(self):
        with tempfile.TemporaryDirectory() as d:
            ev, snap, req = make_case(Path(d))
            proc = run_seal(ev, snap, req)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertIn("SEALED: ", proc.stdout)
            sealed = [p for p in snap.iterdir() if p.is_dir()]
            self.assertEqual(len(sealed), 1)
            manifest = json.loads((sealed[0] / "manifest.json").read_text())
            names = {f["name"] for f in manifest["files"]}
            self.assertEqual(names, {"bao-cao.txt",
                                     "shot-20261127-120000.png"})

    def test_missing_evidence_stops_at_collect(self):
        with tempfile.TemporaryDirectory() as d:
            ev, snap, req = make_case(Path(d), complete=False)
            proc = run_seal(ev, snap, req)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("SEAL FAIL: collect", proc.stdout)
            self.assertEqual(list(snap.iterdir()), [])

    def test_gate_remains_separately_runnable(self):
        with tempfile.TemporaryDirectory() as d:
            ev, snap, req = make_case(Path(d))
            proc = run_seal(ev, snap, req)
            self.assertEqual(proc.returncode, 0, proc.stdout)
            sealed = next(p for p in snap.iterdir() if p.is_dir())
            gate = subprocess.run(
                [sys.executable, str(HERE / "manifest-gate.py"),
                 "--snapshot", str(sealed), "--task", "T-01",
                 "--requirements", str(req)],
                capture_output=True, text=True)
            self.assertEqual(gate.returncode, 0, gate.stdout)


if __name__ == "__main__":
    unittest.main()
