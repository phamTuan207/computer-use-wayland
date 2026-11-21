#!/usr/bin/env python3
"""Run the whole clone2 realistic suite, one subprocess per test.

Each test is independent, builds its own fixture in a temp folder,
and prints a RESULT json line. This runner executes every test file
in order, times the whole suite with wall clock and elapsed, prints
a summary table, writes results.json next to itself when --out is
given, and exits 0 only when every test passes.

Usage:
  python3 tests/realistic_clone2/run_all.py
  python3 tests/realistic_clone2/run_all.py --out /tmp/suite-results.json
"""

import argparse
import datetime
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent


def wall_now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser(description="Run realistic suite")
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    test_files = sorted(HERE.glob("test*.py"))
    results = []
    suite_wall_start = wall_now()
    suite_t0 = time.perf_counter()
    for path in test_files:
        print(f"=== {path.name} ===", flush=True)
        proc = subprocess.run([sys.executable, str(path)],
                              capture_output=True, text=True, timeout=300)
        sys.stdout.write(proc.stdout)
        if proc.stderr:
            sys.stdout.write(proc.stderr)
        parsed = None
        for line in proc.stdout.splitlines():
            if line.startswith("RESULT "):
                parsed = json.loads(line[len("RESULT "):])
        if parsed is None:
            parsed = {"id": path.stem, "title": "unparsed", "ok": False,
                      "elapsed_s": None,
                      "error": f"no RESULT line, exit {proc.returncode}"}
        parsed["exit"] = proc.returncode
        results.append(parsed)

    total = round(time.perf_counter() - suite_t0, 4)
    passed = sum(1 for r in results if r["ok"])
    print("\n=== SUITE SUMMARY ===")
    for r in results:
        print(f"{r['id']}: {'PASS' if r['ok'] else 'FAIL'} "
              f"elapsed_s={r.get('elapsed_s')} {r.get('title', '')}")
    print(f"passed {passed}/{len(results)} total_elapsed_s={total} "
          f"wall_start={suite_wall_start} wall_end={wall_now()}")
    summary = {"suite_wall_start": suite_wall_start,
               "suite_wall_end": wall_now(), "total_elapsed_s": total,
               "passed": passed, "total": len(results), "results": results}
    if args.out:
        Path(args.out).write_text(json.dumps(summary, indent=2),
                                  encoding="utf-8")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
