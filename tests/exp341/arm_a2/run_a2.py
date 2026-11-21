#!/usr/bin/env python3
"""Run arm A-prime: 6 tasks, N runs each, same protocol as run_all.

Usage: run_a2.py [runs]   (default 3)
Writes tests/exp341/results_a2.json with raw runs and a median
summary, in the same schema as results.json, arm labelled A2.
"""

import json
import statistics
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
PY = str(Path.home() / "workspace/tools/venv/bin/python")
TASKS = ["task1", "task2", "task3", "task4", "task5", "task6"]


def run_one(cmd):
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    for line in proc.stdout.splitlines():
        if line.startswith("RESULT "):
            return json.loads(line[len("RESULT "):])
    return {"ok": False, "detail": "no RESULT line", "stdout": proc.stdout[-500:],
            "stderr": proc.stderr[-500:], "elapsed_s": 0, "observations": 0,
            "actions": 0, "retries": 0, "steps_only_s": 0}


def median(rows, key):
    return round(statistics.median([r[key] for r in rows]), 4)


def main():
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    raw = []
    summary = []
    for task in TASKS:
        rows = []
        for i in range(runs):
            r = run_one([PY, str(HERE / "driver.py"), task])
            r["arm"] = "A2"
            r["run"] = i + 1
            rows.append(r)
            raw.append(r)
            print(f"{task} arm A2 run {i + 1}: ok={r['ok']} "
                  f"elapsed={r.get('elapsed_s')} obs={r.get('observations')} "
                  f"actions={r.get('actions')} retries={r.get('retries')}",
                  flush=True)
        summary.append({
            "task": task, "arm": "A2",
            "runs": runs,
            "successes": sum(1 for r in rows if r["ok"]),
            "median_elapsed_s": median(rows, "elapsed_s"),
            "median_steps_only_s": median(rows, "steps_only_s"),
            "median_observations": median(rows, "observations"),
            "median_actions": median(rows, "actions"),
            "total_retries": sum(r["retries"] for r in rows),
        })
    (ROOT / "results_a2.json").write_text(
        json.dumps({"raw": raw, "summary": summary}, indent=2), encoding="utf-8")
    print("\n=== SUMMARY (medians) ===")
    for row in summary:
        print(row)
    return 0


if __name__ == "__main__":
    sys.exit(main())
