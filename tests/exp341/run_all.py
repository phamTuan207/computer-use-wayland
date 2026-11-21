#!/usr/bin/env python3
"""Run experiment 3.4.1 E1: arm A vs arm B, 6 tasks, N runs each.

Usage: run_all.py [runs]   (default 3)
Writes results.json next to this file and prints a summary table
with medians per task and arm.
"""

import json
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent
PY = str(Path.home() / "workspace/tools/venv/bin/python")
TASKS = ["task1", "task2", "task3", "task4", "task5", "task6"]


def run_one(cmd):
    t0 = time.perf_counter()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    runner_elapsed = round(time.perf_counter() - t0, 4)
    for line in proc.stdout.splitlines():
        if line.startswith("RESULT "):
            return json.loads(line[len("RESULT "):])
    # The arm crashed or exited without reporting. Record the failure
    # honestly: counts the runner cannot know are None (JSON null),
    # never 0, so a crashed run can never silently drag a median
    # toward zero. The one number the runner does know is how long
    # the subprocess ran, so elapsed_s carries that measurement.
    return {"ok": False, "crashed": True, "returncode": proc.returncode,
            "detail": "no RESULT line (arm crashed or exited early)",
            "stdout": proc.stdout[-500:], "stderr": proc.stderr[-500:],
            "elapsed_s": runner_elapsed, "steps_only_s": None,
            "browser_start_s": None, "observations": None,
            "actions": None, "retries": None}


def median(rows, key):
    vals = [r[key] for r in rows if r.get(key) is not None]
    if not vals:
        return None
    return round(statistics.median(vals), 4)


def main():
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    raw = []
    summary = []
    for task in TASKS:
        for arm, cmd in (
            ("A", [PY, str(ROOT / "arm_a" / f"{task}_a.py")]),
            ("B", [PY, str(ROOT / "arm_b" / "executor.py"), task]),
        ):
            rows = []
            for i in range(runs):
                r = run_one(cmd)
                r["arm"] = arm
                r["run"] = i + 1
                rows.append(r)
                raw.append(r)
                print(f"{task} arm {arm} run {i + 1}: ok={r['ok']} "
                      f"elapsed={r.get('elapsed_s')} obs={r.get('observations')} "
                      f"actions={r.get('actions')} retries={r.get('retries')}",
                      flush=True)
            summary.append({
                "task": task, "arm": arm,
                "runs": runs,
                "successes": sum(1 for r in rows if r["ok"]),
                "crashed_runs": sum(1 for r in rows if r.get("crashed")),
                "median_elapsed_s": median(rows, "elapsed_s"),
                "median_steps_only_s": median(rows, "steps_only_s"),
                "median_observations": median(rows, "observations"),
                "median_actions": median(rows, "actions"),
                "total_retries": sum(r["retries"] for r in rows
                                     if r.get("retries") is not None),
            })
    (ROOT / "results.json").write_text(
        json.dumps({"raw": raw, "summary": summary}, indent=2), encoding="utf-8")
    print("\n=== SUMMARY (medians) ===")
    for row in summary:
        print(row)
    return 0


if __name__ == "__main__":
    sys.exit(main())
