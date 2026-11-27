#!/usr/bin/env python3
"""M14 adversarial probe gate (bottleneck study 2026-11-27).

Before executor changes land, the frozen Y1b probe suite must
pass and be recorded in probes/ledger.jsonl. This gate checks:

1. The probe file matches the frozen sha256 for this gate
   version. A changed probe file fails the gate: probe changes
   go through full council plus redteam and a gate version bump
   (update GATE_VERSION and FROZEN_SHA256 together).
2. probes/ledger.jsonl validates (delegates to
   probes/validate-ledger.py: rows parse, required fields,
   cited paths exist).
3. The ledger carries a row for the frozen probe suite with
   every required field filled in.

With --run it also executes the probe suite, fails if the
suite fails, and prints a FLAG (not a pass comfort) when the
pass is suspiciously fast: the suite sleeps through real
wall-clock budget probes, so a pass far under the proven
15.478 s means probes were skipped or short-circuited.

This is not a merge-base A/B performance gate and keeps no
baseline store; that half of I8 stays rejected (item 8 record
in improvements/integration-phase-20261127.md). The gate is
adversarial correctness evidence plus a ledger record.

Usage:
  python3 probes/probe-gate.py [--run] [--ledger PATH]
      [--probe PATH] [--expected-sha256 HEX] [--fast-flag-s N]
Exit 0 = gate pass, 1 = gate fail.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
GATE_VERSION = 1
FROZEN_PROBE = "tests/y1b_probes_rewritten.py"
FROZEN_SHA256 = (
    "4d9d71031d23f57fbb3d9b54386709c5487ee4b331214364e2238a34ee22c80d"
)
REQUIRED = ("date", "probe", "question", "result", "output", "verdict")
FAST_FLAG_S = 8.0


def fail(msg):
    print("FAIL: " + msg)
    return 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="M14 probe gate")
    ap.add_argument("--run", action="store_true",
                    help="also execute the probe suite")
    ap.add_argument("--ledger", default=str(HERE / "ledger.jsonl"))
    ap.add_argument("--probe", default=str(ROOT / FROZEN_PROBE))
    ap.add_argument("--expected-sha256", default=FROZEN_SHA256)
    ap.add_argument("--fast-flag-s", type=float, default=FAST_FLAG_S)
    args = ap.parse_args(argv)
    problems = 0

    probe_path = Path(args.probe)
    if not probe_path.exists():
        problems += fail("probe file not found: %s" % probe_path)
    else:
        digest = hashlib.sha256(probe_path.read_bytes()).hexdigest()
        if digest != args.expected_sha256:
            problems += fail(
                "probe file changed (sha256 %s, frozen %s for gate "
                "v%d): probe changes need council plus redteam and "
                "a gate version bump" % (digest, args.expected_sha256,
                                         GATE_VERSION))

    validator = HERE / "validate-ledger.py"
    proc = subprocess.run(
        [sys.executable, str(validator), args.ledger],
        capture_output=True, text=True)
    sys.stdout.write(proc.stdout)
    if proc.returncode != 0:
        problems += fail("ledger validation failed (see above)")

    ledger_path = Path(args.ledger)
    found = False
    if ledger_path.exists():
        for line in ledger_path.read_text().splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if FROZEN_PROBE in str(row.get("probe", "")):
                found = True
                missing = [f for f in REQUIRED if not row.get(f)]
                if missing:
                    problems += fail(
                        "ledger row for %s is missing field(s): %s"
                        % (FROZEN_PROBE, ", ".join(missing)))
    if not found:
        problems += fail(
            "no ledger row for %s: run the probe suite and record "
            "it in probes/ledger.jsonl before executor changes land"
            % FROZEN_PROBE)

    if args.run and probe_path.exists():
        start = time.monotonic()
        proc = subprocess.run([sys.executable, str(probe_path)],
                              capture_output=True, text=True)
        elapsed = time.monotonic() - start
        sys.stdout.write(proc.stdout)
        if proc.returncode != 0:
            problems += fail("probe suite failed (exit %d, %.1fs)"
                             % (proc.returncode, elapsed))
        elif elapsed < args.fast_flag_s:
            print("FLAG: probe suite passed in %.1fs, far under the "
                  "proven 15.478s: treat as suspicious, not as "
                  "comfort; check the probes actually ran" % elapsed)
        else:
            print("probe suite passed in %.1fs" % elapsed)

    if problems:
        print("PROBE GATE FAIL (gate v%d): %d problem(s)"
              % (GATE_VERSION, problems))
        return 1
    print("PROBE GATE PASS (gate v%d)" % GATE_VERSION)
    return 0


if __name__ == "__main__":
    sys.exit(main())
