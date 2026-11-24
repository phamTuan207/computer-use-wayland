#!/usr/bin/env python3
"""R3-L3 audit scan (Decision E, coordinator audit before ledger).

Checks one scorer's verdict file and its read list against the
forbidden-read list. A scorer must never read the run ledger, the
other pair's grades, the other scorer's verdict file, the trial or
preflight reports, or runner logs. The coordinator runs this scan
before a grade enters the ledger. If the scan fails, the grade is
held and the coordinator escalates.

Forbidden reads (any file whose path contains one of these):
  - R3-L2-grades.jsonl, R3-L3-grades.jsonl (run ledgers)
  - rung3-preflight-trial.md, rung3-preflight-REPORT.md (trial)
  - rung3-scorer1-, rung3-scorer2-, rung3-scorer3- grade files of
    another scorer (a scorer reads only its own verdict file)
  - rung3-verdicts/ files belonging to another scorer
  - runner logs (rung3-runner, runner-brief, run-log files other
    than the snapshot manifest and the frozen key)

Usage:
  python3 rung3-ci/audit-scan.py --verdict <verdict.json>
      [--scorer <A1|A2|B1|B2|TB>] [--extra-forbidden <path> ...]

The verdict JSON must have: scorer, task, files_read (array of paths).
Output: PASS or FAIL plus the forbidden reads found, exit 0/1.
Honest limitation: for subagent scorers the coordinator reviews the
verdict file and its read list (this scan). For Mochi (a Chromium
session on the laptop) the audit is manual: the coordinator reviews
her messages and the files she reports reading in the browser session.
This script does not audit Mochi; the coordinator records her audit
by hand in the audit record.
No personal info in this file.
"""
import argparse
import json
import sys

FORBIDDEN_SUBSTRINGS = [
    "R3-L2-grades.jsonl",
    "R3-L3-grades.jsonl",
    "rung3-preflight-trial.md",
    "rung3-preflight-REPORT.md",
    "rung3-preflight",
    "trial",
    "runner-brief",
    "runner-log",
    "run-log/R3-L",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verdict", required=True)
    ap.add_argument("--scorer", default=None)
    ap.add_argument("--extra-forbidden", nargs="*", default=[])
    args = ap.parse_args()
    try:
        with open(args.verdict, encoding="utf-8") as f:
            verdict = json.load(f)
    except (ValueError, OSError) as e:
        print("FAIL: verdict unreadable: %s" % e)
        return 1
    files_read = verdict.get("files_read", [])
    if not isinstance(files_read, list):
        print("FAIL: files_read is not a list")
        return 1
    forbidden = list(FORBIDDEN_SUBSTRINGS) + list(args.extra_forbidden)
    found = []
    for path in files_read:
        for bad in forbidden:
            if bad in path:
                found.append((path, bad))
                break
    if args.scorer:
        others = {"A1": "A2", "A2": "A1", "B1": "B2", "B2": "B1"}
        other = others.get(args.scorer)
        if other:
            for path in files_read:
                if ("-{}-".format(other) in path
                        or path.endswith("-{}.json".format(other))):
                    found.append((path, "other scorer verdict"))
    if found:
        print("FAIL: %d forbidden read(s):" % len(found))
        for path, bad in found:
            print("  %s (matched %s)" % (path, bad))
        return 1
    print("PASS: %s task %s, %d files read, no forbidden reads"
          % (verdict.get("scorer", "?"), verdict.get("task", "?"),
             len(files_read)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
